#!/usr/bin/env python3
"""Local, unattended orchestrator for the autonomous Learn Monitor doc pipeline.

This is the engine of the local-CLI pivot. Run on a schedule (see
``scripts/Register-AutodocTask.ps1``) it: reads the latest Learn Monitor report, routes
each change (``autodoc_route``), and for every *autodraft* change drafts a minimal doc
edit with the GitHub Copilot CLI, gates it through the deterministic verifier
(``autodoc_verify_gate``) **and** an independent cross-model review
(``autodoc_cli_review``, a different Copilot model family), and — only when both pass —
opens a pull request for a **human** to merge. Failures retry a bounded number of times
(``autodoc_retry.decide``) and then escalate to a human. *human*-routed changes are never
drafted; they get an escalation issue.

Account model: the Copilot CLI reasons on the EMU license; all git/PR writes use the
``judeper`` token (independent auths). The pipeline is **off by default**: ``run`` is a
no-op unless ``AUTODOC_ENABLED=true``.

All side-effecting steps (drafting, verification, review, git, PR, escalation) are module
functions so the orchestration is unit-testable by monkeypatching them; the live default
implementations shell out to ``copilot``/``git``/``gh``.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import autodoc_retry
import autodoc_route

COPILOT_BIN = "copilot"
DEFAULT_MAX_FIX_CYCLES = 2
DEFAULT_DRAFT_TIMEOUT = 600
DEFAULT_REVIEW_TIMEOUT = 240
NEEDS_HUMAN_MARKER = "AUTODOC-NEEDS-HUMAN"
_CONTRACT_RE = re.compile(r"```json\s*(?P<json>\{.*?\})\s*```", re.DOTALL)


@dataclass
class RunnerConfig:
    """Static configuration for one runner invocation."""

    repo_path: Path
    draft_model: str
    review_model: str
    base_branch: str = "main"
    branch_prefix: str = "autodoc"
    max_fix_cycles: int = DEFAULT_MAX_FIX_CYCLES
    draft_timeout: int = DEFAULT_DRAFT_TIMEOUT
    review_timeout: int = DEFAULT_REVIEW_TIMEOUT
    ledger_path: str = "data/autodoc-ledger.json"
    reports_glob: str = "reports/monitoring/learn-changes-*.md"
    dry_run: bool = False
    # Absolute ledger path override. When the runner drafts inside a disposable worktree,
    # process_change runs against the worktree but the ledger must persist in the main repo;
    # this points at the main repo's ledger so idempotency survives across runs.
    ledger_abs: Path | None = None


@dataclass
class ChangeContext:
    """Everything the runner needs to draft and gate one routed change."""

    fingerprint: str
    route: str
    contract: dict[str, Any]
    report_path: str
    instructions: str
    title: str
    labels: list[str]

    @property
    def short_fingerprint(self) -> str:
        digest = self.fingerprint.split(":", 1)[-1]
        return digest[:12]

    @property
    def branch(self) -> str:
        return f"autodoc/{self.short_fingerprint}"


@dataclass
class DraftResult:
    needs_human: bool
    diff_text: str
    changed_files: list[str] = field(default_factory=list)
    notes: str = ""


@dataclass
class Outcome:
    fingerprint: str
    status: str  # pr_opened | escalated | skipped | error
    detail: str = ""


# --------------------------------------------------------------------------------------
# Orchestration (pure; depends only on the module functions below, which tests monkeypatch)
# --------------------------------------------------------------------------------------


def run(config: RunnerConfig) -> dict[str, Any]:
    """Top-level entry point. No-op unless AUTODOC_ENABLED=true.

    Reads the report + ledger from the main repo, then drafts each change inside a
    **disposable git worktree** (a fresh checkout of base with none of the user's ignored
    or local files), so an autonomous draft can never touch the main checkout. The ledger
    is still written to the main repo so idempotency persists across runs.
    """

    if not _autodoc_enabled():
        return {"enabled": False, "outcomes": []}

    report_path = _latest_report(config)
    if report_path is None:
        return {"enabled": True, "outcomes": [], "note": "no monitoring report found"}

    report_text = report_path.read_text(encoding="utf-8")
    main_ledger_path = config.repo_path / config.ledger_path
    ledger = autodoc_route.load_ledger(main_ledger_path)
    specs = autodoc_route.route_report(report_text, report_path.name, ledger)
    if not specs:
        return {"enabled": True, "report": report_path.name, "outcomes": []}

    work_path = _create_worktree(config)
    work_config = replace(config, repo_path=work_path, ledger_abs=main_ledger_path)
    outcomes: list[Outcome] = []
    seen: set[str] = set()
    try:
        for spec in specs:
            try:
                ctx = _build_context(spec)
            except Exception as exc:  # noqa: BLE001 - a malformed spec must not crash the run.
                outcomes.append(Outcome(spec.get("fingerprint", "unknown"), "error", f"context_error: {exc}"))
                continue
            if ctx.fingerprint in seen:
                # Defensive de-duplication: the same fingerprint must be processed at most
                # once per run, even if routing emitted duplicate rows for the same change.
                outcomes.append(Outcome(ctx.fingerprint, "skipped", "duplicate fingerprint in this run"))
                continue
            seen.add(ctx.fingerprint)
            try:
                if ctx.route != "autodraft":
                    outcomes.append(_handle_human_change(work_config, ctx))
                else:
                    outcomes.append(process_change(work_config, ctx))
            except Exception as exc:  # noqa: BLE001 - one change's failure must not abort the batch.
                outcomes.append(Outcome(ctx.fingerprint, "error", f"processing_error: {exc}"))
    finally:
        _remove_worktree(config, work_path)

    return {"enabled": True, "report": report_path.name, "outcomes": [vars(o) for o in outcomes]}


def process_change(config: RunnerConfig, ctx: ChangeContext) -> Outcome:
    """Draft → deterministic verify → cross-model review → PR, with bounded fix-retry."""

    base = config.base_branch
    _git(config, "checkout", "-B", ctx.branch, base)
    # Snapshot untracked files at branch start. Cleanup removes only files that appear
    # AFTER this (the draft's), never pre-existing user files — and this baseline approach
    # also cleans files left behind if a draft raises/times out mid-write.
    baseline_untracked = _untracked_files(config)
    attempts = 0
    feedback = ""
    committed = False
    try:
        while True:
            draft = _run_draft(config, ctx, feedback)
            if draft.needs_human or not draft.changed_files:
                return _do_escalate(config, ctx, "draft_needs_human", draft.notes or "Drafter produced no usable edit.")

            deterministic = _run_deterministic_verify(config, ctx, draft)
            review_verdict: dict[str, Any] | None = None
            if deterministic == "pass":
                review_verdict = _run_cross_model_review(config, ctx, draft)

            conclusion = _combine_conclusion(deterministic, review_verdict)
            if conclusion == "pass":
                detail = _open_pr(config, ctx, draft, review_verdict or {})
                committed = True
                _record_ledger(config, ctx, "pr_open", detail)
                return Outcome(ctx.fingerprint, "pr_opened", detail)

            decision = autodoc_retry.decide(attempts, config.max_fix_cycles, conclusion)
            if decision["action"] != "retry":
                return _do_escalate(
                    config, ctx, str(decision["reason"]), _feedback_text(deterministic, review_verdict)
                )

            attempts += 1
            feedback = _feedback_text(deterministic, review_verdict)
            _reset_attempt(config, base, baseline_untracked)
    finally:
        # Discard any uncommitted attempt and any untracked files the draft(s) created
        # (relative to the branch-start baseline), then leave the worktree on a DETACHED base
        # HEAD. We must detach rather than `checkout main`: this runs inside a linked worktree
        # and git forbids checking out a branch (main) that is already checked out in the
        # primary worktree (`fatal: 'main' is already used by worktree ...`).
        if not committed:
            _reset_attempt(config, base, baseline_untracked)
        _git(config, "checkout", "--force", "--detach", base)


def _handle_human_change(config: RunnerConfig, ctx: ChangeContext) -> Outcome:
    """A human-routed change is never drafted; open an escalation issue once."""

    detail = _escalate(config, ctx, "route=human", "This change must be analyzed by a human; no draft was attempted.")
    _record_ledger(config, ctx, "human_escalated", detail)
    return Outcome(ctx.fingerprint, "escalated", detail)


def _do_escalate(config: RunnerConfig, ctx: ChangeContext, reason: str, details: str) -> Outcome:
    """Open the escalation issue and record it; the working tree is cleaned in the finally block."""

    detail = _escalate(config, ctx, reason, details)
    _record_ledger(config, ctx, "escalated", detail)
    return Outcome(ctx.fingerprint, "escalated", f"{reason}: {detail}")


def _combine_conclusion(deterministic: str, review_verdict: dict[str, Any] | None) -> str:
    """Reduce the deterministic conclusion and the review verdict to one fail-closed result."""

    if deterministic == "needs_human":
        return "needs_human"
    if deterministic != "pass":
        return "fail"
    # Deterministic passed; the review verdict decides.
    verdict = (review_verdict or {}).get("verdict")
    if verdict == "pass":
        return "pass"
    if verdict == "needs_human":
        return "needs_human"
    return "fail"


def _feedback_text(deterministic: str, review_verdict: dict[str, Any] | None) -> str:
    lines = [f"Deterministic verifier: {deterministic}."]
    if review_verdict:
        verdict = review_verdict.get("verdict", "unknown")
        lines.append(f"Independent review: {verdict}.")
        for claim in review_verdict.get("unsupported_claims", []) or []:
            lines.append(f"- Unsupported claim: {claim}")
        for edit in review_verdict.get("overbroad_edits", []) or []:
            lines.append(f"- Overbroad edit: {edit}")
        if review_verdict.get("notes"):
            lines.append(f"Reviewer notes: {review_verdict['notes']}")
    return "\n".join(lines)


def _build_context(spec: dict[str, Any]) -> ChangeContext:
    """Parse a route issue spec into a ChangeContext, extracting the embedded contract."""

    body = spec.get("body") or ""
    fingerprint = spec.get("fingerprint") or ""
    contract = _extract_contract(body, fingerprint)
    report_path = str(contract.get("report_path", ""))
    if not report_path.startswith("reports/monitoring/"):
        raise ValueError(f"contract report_path must be under reports/monitoring/: {report_path!r}")
    return ChangeContext(
        fingerprint=fingerprint,
        route=spec.get("route", ""),
        contract=contract,
        report_path=report_path,
        instructions=body,
        title=spec.get("title", ""),
        labels=list(spec.get("labels", [])),
    )


def _extract_contract(body: str, fingerprint: str) -> dict[str, Any]:
    for match in _CONTRACT_RE.finditer(body):
        try:
            candidate = json.loads(match.group("json"))
        except json.JSONDecodeError:
            continue
        if isinstance(candidate, dict) and candidate.get("fingerprint") == fingerprint:
            return candidate
    raise ValueError("issue body did not contain a JSON contract matching the fingerprint")


# --------------------------------------------------------------------------------------
# Side effects (monkeypatched in tests; live implementations shell out)
# --------------------------------------------------------------------------------------


def _autodoc_enabled() -> bool:
    return os.environ.get("AUTODOC_ENABLED", "").strip().lower() == "true"


def _latest_report(config: RunnerConfig) -> Path | None:
    reports = sorted((config.repo_path).glob(config.reports_glob))
    return reports[-1] if reports else None


def _run_draft(config: RunnerConfig, ctx: ChangeContext, feedback: str) -> DraftResult:
    """Drive the Copilot CLI to edit the allowed files in the working tree.

    Everything the draft touches (including new untracked files) is staged with
    ``git add -A`` so the deterministic verifier and the review see the full change set —
    the path allowlist then flags anything off-contract. Cleanup of any files the draft
    creates is handled by ``_reset_attempt`` against the branch-start baseline.
    """

    prompt = _build_draft_prompt(ctx, feedback)
    completed = subprocess.run(
        [
            COPILOT_BIN,
            "-p",
            prompt,
            "--model",
            config.draft_model,
            "-s",
            "--no-ask-user",
            "--no-remote",
            "--allow-all-tools",
            "-C",
            str(config.repo_path),
        ],
        check=False,
        capture_output=True,
        text=True,
        timeout=config.draft_timeout,
    )
    stdout = completed.stdout or ""
    _git(config, "add", "-A")
    diff_text = _git(config, "diff", "--cached", "--unified=3")
    changed = [line for line in _git(config, "diff", "--cached", "--name-only").splitlines() if line.strip()]
    needs_human = NEEDS_HUMAN_MARKER in stdout or not changed
    return DraftResult(needs_human=needs_human, diff_text=diff_text, changed_files=changed, notes=stdout[-2000:])


def _untracked_files(config: RunnerConfig) -> list[str]:
    """Return repo-relative paths of untracked files (NUL-delimited, unicode-safe)."""

    output = _git(config, "status", "--porcelain", "-z", "--untracked-files=all")
    paths: list[str] = []
    for entry in output.split("\x00"):
        if entry.startswith("?? "):
            paths.append(entry[3:])
    return paths


def _reset_attempt(config: RunnerConfig, base: str, baseline_untracked: list[str]) -> None:
    """Discard an uncommitted draft attempt: hard-reset tracked changes, then remove only the
    untracked files that appeared since ``baseline_untracked`` (never pre-existing user files).

    ``git reset --hard`` un-stages and reverts tracked edits but leaves draft-created files on
    disk as untracked; computing the delta AFTER the reset also catches files a draft left
    behind when it raised or timed out before staging.
    """

    _git(config, "reset", "--hard", base)
    leaked = sorted(set(_untracked_files(config)) - set(baseline_untracked))
    for rel_path in leaked:
        target = config.repo_path / rel_path
        try:
            if target.is_file():
                target.unlink()
        except OSError:
            pass


def _build_draft_prompt(ctx: ChangeContext, feedback: str) -> str:
    feedback_block = ""
    if feedback:
        feedback_block = (
            "\n\nA previous attempt was rejected by the verifiers. Correct exactly these problems "
            f"and make no other changes:\n{feedback}\n"
        )
    return (
        "You are drafting a minimal, faithful documentation edit for a US financial-services "
        "compliance framework. Follow the authoring contract and task below EXACTLY. Edit only the "
        "files listed in allowed_files, touch only the allowed_headings, and ground every change "
        "solely in the Learn change evidence — invent nothing. Use FSI-safe language (never "
        "'ensures compliance', 'guarantees', 'will prevent', 'eliminates risk'). If the evidence "
        f"does not support a concrete edit, print {NEEDS_HUMAN_MARKER} and make no file changes.\n\n"
        f"{ctx.instructions}{feedback_block}\n\nMake the edits to the working tree now."
    )


def _run_deterministic_verify(config: RunnerConfig, ctx: ChangeContext, draft: DraftResult) -> str:
    """Run the deterministic verify gate; return its conclusion (pass/fail/needs_human)."""

    with tempfile.TemporaryDirectory() as tmp:
        diff_path = Path(tmp) / "pr.diff"
        body_path = Path(tmp) / "pr-body.txt"
        out_path = Path(tmp) / "gate.json"
        diff_path.write_text(draft.diff_text, encoding="utf-8")
        body_path.write_text(f"AUTODOC-FINGERPRINT: {ctx.fingerprint}\n", encoding="utf-8")
        contract_path = Path(tmp) / "contract.json"
        contract_path.write_text(json.dumps(ctx.contract), encoding="utf-8")
        proc = subprocess.run(
            [
                sys.executable,
                str(SCRIPT_DIR / "autodoc_verify_gate.py"),
                "--contract",
                str(contract_path),
                "--report",
                str(config.repo_path / ctx.report_path),
                "--diff",
                str(diff_path),
                "--head-dir",
                str(config.repo_path),
                "--pr-body",
                str(body_path),
                "--out",
                str(out_path),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        return _conclusion_from_exit(proc.returncode)


def _run_cross_model_review(config: RunnerConfig, ctx: ChangeContext, draft: DraftResult) -> dict[str, Any]:
    """Run the independent cross-model review; return the verdict dict."""

    with tempfile.TemporaryDirectory() as tmp:
        diff_path = Path(tmp) / "pr.diff"
        contract_path = Path(tmp) / "contract.json"
        out_path = Path(tmp) / "verdict.json"
        diff_path.write_text(draft.diff_text, encoding="utf-8")
        contract_path.write_text(json.dumps(ctx.contract), encoding="utf-8")
        subprocess.run(
            [
                sys.executable,
                str(SCRIPT_DIR / "autodoc_cli_review.py"),
                "--contract",
                str(contract_path),
                "--report",
                str(config.repo_path / ctx.report_path),
                "--diff",
                str(diff_path),
                "--model",
                config.review_model,
                "--out",
                str(out_path),
                "--timeout",
                str(config.review_timeout),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        try:
            return json.loads(out_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {"verdict": "needs_human", "notes": "review output unreadable"}


def _conclusion_from_exit(code: int) -> str:
    return {0: "pass", 1: "fail", 2: "needs_human"}.get(code, "needs_human")


def _git(config: RunnerConfig, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(config.repo_path), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout


def _open_pr(config: RunnerConfig, ctx: ChangeContext, draft: DraftResult, review_verdict: dict[str, Any]) -> str:
    """Commit the verified draft, push as the owner, and open a human-merge PR."""

    if config.dry_run:
        return f"dry-run: would open PR for {ctx.branch}"
    commit_message = f"docs(autodoc): {ctx.title}\n\nAUTODOC-FINGERPRINT: {ctx.fingerprint}"
    # The verified change set is already staged by _run_draft (git add -A) and the
    # deterministic verifier confirmed only allowed_files changed, so commit the staged set.
    _git(config, "commit", "-m", commit_message)
    pr_body = (
        f"Automated documentation draft (human merge required).\n\n"
        f"AUTODOC-FINGERPRINT: {ctx.fingerprint}\n"
        f"Source report: {ctx.report_path}\n\n"
        f"Independent cross-model review verdict: {review_verdict.get('verdict', 'n/a')} "
        f"(confidence {review_verdict.get('confidence', 'n/a')}).\n"
    )
    return _push_and_create_pr(config, ctx, pr_body)


def _push_and_create_pr(config: RunnerConfig, ctx: ChangeContext, pr_body: str) -> str:
    """Live PR creation via gh; isolated so tests can monkeypatch it. Raises on failure.

    The runner exclusively owns ``autodoc/<fingerprint>`` branches (the fingerprint is unique
    per change and never human-touched), so a force push is safe and keeps re-pushes
    idempotent after a discarded local attempt. If ``gh pr create`` fails but a PR already
    exists for this head (a prior partial run), that existing PR is returned. Otherwise the
    just-pushed orphan branch is removed so the next run starts clean, and the call raises.
    """

    _git(config, "push", "--force", "--set-upstream", "origin", ctx.branch)
    completed = subprocess.run(
        [
            "gh",
            "pr",
            "create",
            "--repo",
            _repo_slug(config),
            "--head",
            ctx.branch,
            "--base",
            config.base_branch,
            "--title",
            f"docs(autodoc): {ctx.title}",
            "--body",
            pr_body,
            "--label",
            "autodoc",
        ],
        check=False,
        capture_output=True,
        text=True,
        cwd=str(config.repo_path),
    )
    if completed.returncode == 0:
        return (completed.stdout or "").strip()

    existing = _existing_pr_url(config, ctx)
    if existing:
        return existing

    # No PR exists; drop the orphaned remote branch (best effort) and fail loudly so the
    # ledger is NOT marked pr_open and the change is retried cleanly next run.
    subprocess.run(
        ["git", "-C", str(config.repo_path), "push", "origin", "--delete", ctx.branch],
        check=False,
        capture_output=True,
        text=True,
    )
    raise RuntimeError(f"gh pr create failed (exit {completed.returncode}): {(completed.stderr or '').strip()}")


def _existing_pr_url(config: RunnerConfig, ctx: ChangeContext) -> str | None:
    """Return the URL of an open PR for this branch head, or None."""

    completed = subprocess.run(
        ["gh", "pr", "view", ctx.branch, "--repo", _repo_slug(config), "--json", "url", "-q", ".url"],
        check=False,
        capture_output=True,
        text=True,
        cwd=str(config.repo_path),
    )
    url = (completed.stdout or "").strip()
    return url if completed.returncode == 0 and url else None


def _escalate(config: RunnerConfig, ctx: ChangeContext, reason: str, details: str) -> str:
    """Open (or reuse) a human-review issue for a change the runner will not auto-draft.

    Idempotent across runs: if an open escalation issue already carries this fingerprint, it
    is reused instead of opening a duplicate.
    """

    if config.dry_run:
        return f"dry-run: would escalate {ctx.fingerprint} ({reason})"
    existing = _existing_issue_url(config, ctx)
    if existing:
        return existing
    body = (
        f"Autodoc escalation — human review required.\n\n"
        f"AUTODOC-FINGERPRINT: {ctx.fingerprint}\n"
        f"Reason: {reason}\n\n{details}\n"
    )
    completed = subprocess.run(
        [
            "gh",
            "issue",
            "create",
            "--repo",
            _repo_slug(config),
            "--title",
            ctx.title or f"Autodoc escalation {ctx.short_fingerprint}",
            "--body",
            body,
            "--label",
            "autodoc",
            "--label",
            "escalate",
        ],
        check=False,
        capture_output=True,
        text=True,
        cwd=str(config.repo_path),
    )
    if completed.returncode != 0:
        # Must raise so the ledger is NOT marked escalated for an issue that was never created.
        raise RuntimeError(f"gh issue create failed (exit {completed.returncode}): {(completed.stderr or '').strip()}")
    return (completed.stdout or "").strip()


def _existing_issue_url(config: RunnerConfig, ctx: ChangeContext) -> str | None:
    """Return the URL of an open escalation issue already carrying this fingerprint, or None."""

    completed = subprocess.run(
        [
            "gh",
            "issue",
            "list",
            "--repo",
            _repo_slug(config),
            "--state",
            "open",
            "--search",
            f"AUTODOC-FINGERPRINT: {ctx.fingerprint} in:body",
            "--json",
            "url",
            "-q",
            ".[0].url",
        ],
        check=False,
        capture_output=True,
        text=True,
        cwd=str(config.repo_path),
    )
    url = (completed.stdout or "").strip()
    return url if completed.returncode == 0 and url else None


def _create_worktree(config: RunnerConfig) -> Path:
    """Create a disposable git worktree (detached at base) for isolated drafting.

    The worktree is a fresh checkout of the base ref containing only tracked files — none of
    the user's ignored or local files — so an autonomous draft cannot touch the main checkout.
    """

    work_path = config.repo_path.parent / f".autodoc-worktree-{os.getpid()}"
    _remove_worktree(config, work_path)  # clear any stale worktree at this path
    _git(config, "worktree", "add", "--force", "--detach", str(work_path), config.base_branch)
    return work_path


def _remove_worktree(config: RunnerConfig, work_path: Path) -> None:
    """Remove a disposable worktree and everything in it (best effort)."""

    subprocess.run(
        ["git", "-C", str(config.repo_path), "worktree", "remove", "--force", str(work_path)],
        check=False,
        capture_output=True,
        text=True,
    )


def _record_ledger(config: RunnerConfig, ctx: ChangeContext, state: str, detail: str) -> None:
    """Record a terminal-ish outcome in the ledger so the change is not reprocessed."""

    if config.dry_run:
        # Dry-run must not persist terminal states, or routing would skip these forever.
        return
    ledger_path = config.ledger_abs or (config.repo_path / config.ledger_path)
    ledger = autodoc_route.load_ledger(ledger_path)
    ledger.setdefault("changes", {})[ctx.fingerprint] = {
        "state": state,
        "route": ctx.route,
        "detail": detail,
    }
    autodoc_route.save_ledger(ledger_path, ledger)


def _repo_slug(config: RunnerConfig) -> str:
    return os.environ.get("AUTODOC_REPO", "judeper/FSI-AgentGov")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the unattended autodoc drafter.")
    parser.add_argument("--repo", default=".", help="Path to the repository working tree.")
    parser.add_argument("--draft-model", required=True, help="Copilot model for drafting.")
    parser.add_argument("--review-model", required=True, help="Copilot model for the independent review (different family).")
    parser.add_argument("--max-fix-cycles", type=int, default=DEFAULT_MAX_FIX_CYCLES)
    parser.add_argument("--dry-run", action="store_true", help="Do everything except push/PR/escalate.")
    args = parser.parse_args(argv)

    config = RunnerConfig(
        repo_path=Path(args.repo).resolve(),
        draft_model=args.draft_model,
        review_model=args.review_model,
        max_fix_cycles=args.max_fix_cycles,
        dry_run=args.dry_run,
    )
    summary = run(config)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
