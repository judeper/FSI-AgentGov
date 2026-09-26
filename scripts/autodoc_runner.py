#!/usr/bin/env python3
"""Local, unattended orchestrator for the autonomous Learn Monitor doc pipeline.

This is the engine of the local-CLI pivot. Run on a schedule (see
``scripts/Register-AutodocTask.ps1``) it: reads the latest Learn Monitor report, routes
each change (``autodoc_route``), and for every *autodraft* change drafts a minimal doc
edit with the GitHub Copilot CLI, gates it through the deterministic verifier
(``autodoc_verify_gate``) **and** an independent cross-model review
(``autodoc_cli_review``, a different Copilot model family), and — only when both pass —
opens a pull request for OceanSquad review and merge. Failures retry a bounded number of times
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
import urllib.parse
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import autodoc_automerge
import autodoc_canary
import autodoc_classifier
import autodoc_issue_identity
import autodoc_retry
import autodoc_route

COPILOT_BIN = "copilot"
DEFAULT_MAX_FIX_CYCLES = 2
DEFAULT_DRAFT_TIMEOUT = 1200
DEFAULT_REVIEW_TIMEOUT = 300
NEEDS_HUMAN_MARKER = "AUTODOC-NEEDS-HUMAN"
MAX_INLINE_FILE_CHARS = 60000
_CONTRACT_RE = re.compile(r"```json\s*(?P<json>\{.*?\})\s*```", re.DOTALL)
# Capture the entire remainder of the evidence line (the classifier emits "redirects to <final>"
# with nothing after the URL). Capturing to end-of-line — rather than \S+ — means an embedded
# space or other junk is kept and then rejected by _URL_WELL_FORMED_RE, instead of being silently
# truncated into a valid-but-wrong URL.
_REDIRECT_TO_RE = re.compile(r"redirects to (\S[^\n]*)")
# A well-formed redirect URL: scheme + only RFC 3986 URL characters. Excludes anything that would
# break the markdown table or isn't URL-legal (|, quotes, <>, backtick, braces, control chars).
_URL_WELL_FORMED_RE = re.compile(r"^https?://[A-Za-z0-9\-._~:/?#\[\]@!$&'()*+,;=%]+$")
_ISSUE_URL_NUMBER_RE = re.compile(r"/issues/(\d+)(?:/)?$")


def _redirect_host_allowed(url: str) -> bool:
    """Fail-closed Microsoft-domain allowlist for a redirect's NEW target URL.

    A poisoned upstream redirect could otherwise smuggle an attacker-controlled URL into the
    canonical Learn-URL list once Stage-2 auto-merge is enabled. Only a host that is
    ``learn.microsoft.com``, ``microsoft.com``, or a subdomain ending in ``.microsoft.com`` is
    accepted. The host is taken from ``urlparse(...).hostname`` (lower-cased), so userinfo/credential
    tricks (``https://learn.microsoft.com@evil.example/``) resolve to the real authority host and
    subdomain spoofs (``learn.microsoft.com.evil.com``) are rejected. Empty host, IPs, malformed
    authority, or any parse error all fail closed.

    This rule is duplicated — on purpose — in ``autodoc_redirect_ci_verify`` so the CI gate stays
    independent of this runner. Do NOT factor the two copies into a shared helper.
    """

    try:
        host = (urllib.parse.urlparse(url).hostname or "").lower()
    except ValueError:
        return False
    return host in ("learn.microsoft.com", "microsoft.com") or host.endswith(".microsoft.com")


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
    automerge_ledger_path: str = "data/autodoc-automerge-ledger.json"
    # Absolute auto-merge agreement-ledger path (main repo), like ledger_abs: the runner
    # drafts in a disposable worktree but the agreement ledger must persist in the main repo.
    automerge_ledger_abs: Path | None = None


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

    _assert_canary(config)

    # Update the auto-merge agreement ledger with how past redirect PRs were resolved by
    # OceanSquad/the owner (merged-as-is / edited / closed). This remains observational:
    # target-native auto-merge activation is deliberately disabled.
    _reconcile_automerge(config)

    report_path = _latest_report(config)
    if report_path is None:
        return {"enabled": True, "outcomes": [], "note": "no monitoring report found"}

    report_text = report_path.read_text(encoding="utf-8")
    main_ledger_path = config.repo_path / config.ledger_path
    main_automerge_ledger = config.repo_path / config.automerge_ledger_path
    ledger = autodoc_route.load_ledger(main_ledger_path)
    specs = autodoc_route.route_report(report_text, report_path.name, ledger, repo_root=config.repo_path)
    if not specs:
        return {"enabled": True, "report": report_path.name, "outcomes": []}

    work_path = _create_worktree(config)
    work_config = replace(config, repo_path=work_path, ledger_abs=main_ledger_path, automerge_ledger_abs=main_automerge_ledger)
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
    """Draft → deterministic verify → cross-model review → PR, with bounded fix-retry.

    Redirect changes are handled deterministically (no LLM) — see ``_process_redirect``.
    """

    if _is_redirect(ctx):
        return _process_redirect(config, ctx)

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


# --------------------------------------------------------------------------------------
# Deterministic redirect handling (no LLM)
# --------------------------------------------------------------------------------------


def _is_redirect(ctx: ChangeContext) -> bool:
    return ctx.contract.get("classification") == "REDIRECT"


def _process_redirect(config: RunnerConfig, ctx: ChangeContext) -> Outcome:
    """Apply a URL redirect deterministically: swap the old Learn URL for the new one in the
    URL list, verify the diff is a clean URL-only change, and open an OceanSquad-reviewed PR.
    No LLM and no prose verifier are used — a redirect is a mechanical string replacement.
    """

    old_url = autodoc_classifier._canonicalize_url(  # noqa: SLF001 - shared routing identity rule.
        str(ctx.contract.get("source_url", ""))
    )
    contract_destination = str(ctx.contract.get("destination_url", ""))
    match = _REDIRECT_TO_RE.search(ctx.instructions)
    evidence_destination = match.group(1).strip() if match else ""
    new_url = autodoc_classifier._canonicalize_url(  # noqa: SLF001 - shared routing identity rule.
        contract_destination or evidence_destination
    )
    if not (old_url.startswith("http") and new_url.startswith("http")) or old_url == new_url:
        return _do_escalate(config, ctx, "redirect_parse_failed", f"could not resolve a URL swap (old={old_url!r} new={new_url!r})")
    # Reject URLs containing table-breaking or non-URL-legal characters before any file write, so a
    # malformed redirect target can never corrupt the markdown table and slip past the diff guard.
    if not (_URL_WELL_FORMED_RE.match(old_url) and _URL_WELL_FORMED_RE.match(new_url)):
        return _do_escalate(config, ctx, "redirect_malformed_url", f"URL contains characters that are not URL-legal (old={old_url!r} new={new_url!r})")
    # Fail closed if the redirect target host is not a Microsoft domain. A poisoned upstream redirect
    # must never be drafted into the canonical Learn-URL list (defence in depth with the independent
    # CI gate in autodoc_redirect_ci_verify).
    if not _redirect_host_allowed(new_url):
        return _do_escalate(config, ctx, "redirect_off_domain", f"redirect target host is not a Microsoft domain; refusing off-domain swap (new={new_url!r})")

    base = config.base_branch
    _git(config, "checkout", "-B", ctx.branch, base)
    baseline_untracked = _untracked_files(config)
    committed = False
    try:
        outcome = _apply_and_open_redirect(config, ctx, old_url, new_url)
        committed = outcome.status == "pr_opened"
        return outcome
    finally:
        if not committed:
            _reset_attempt(config, base, baseline_untracked)
        _git(config, "checkout", "--force", "--detach", base)


def _apply_and_open_redirect(config: RunnerConfig, ctx: ChangeContext, old_url: str, new_url: str) -> Outcome:
    allowed = [rel for rel in ctx.contract.get("allowed_files", [])]
    matches: list[tuple[Path, str, str]] = []
    new_url_present = False
    for rel in allowed:
        path = config.repo_path / rel
        try:
            before = path.read_text(encoding="utf-8")
        except OSError:
            continue
        lines = before.splitlines(keepends=True)
        for line_index, line in enumerate(lines):
            cells = line.split("|")
            for cell_index, cell in enumerate(cells):
                candidate = cell.strip()
                if not _URL_WELL_FORMED_RE.fullmatch(candidate):
                    continue
                canonical = autodoc_classifier._canonicalize_url(candidate)  # noqa: SLF001
                if canonical == new_url:
                    new_url_present = True
                if canonical != old_url:
                    continue
                updated_cells = list(cells)
                updated_cells[cell_index] = cell.replace(candidate, new_url, 1)
                updated_lines = list(lines)
                updated_lines[line_index] = "|".join(updated_cells)
                matches.append((path, before, "".join(updated_lines)))

    if new_url_present:
        return _do_escalate(config, ctx, "redirect_ambiguous", "canonical destination URL already exists; needs human review")
    if not matches:
        return _do_escalate(config, ctx, "redirect_url_not_found", f"{old_url} not found as a complete URL in allowed file(s); nothing to update")
    if len(matches) != 1:
        return _do_escalate(
            config,
            ctx,
            "redirect_ambiguous",
            f"canonical source URL matched {len(matches)} rows; refusing a multi-row edit",
        )

    path, _before, after = matches[0]
    path.write_text(after, encoding="utf-8")

    _git(config, "add", "-A")
    diff_text = _git(config, "diff", "--cached", "--unified=3")
    changed_files = [line for line in _git(config, "diff", "--cached", "--name-only").splitlines() if line.strip()]
    if not _redirect_diff_is_clean(changed_files, allowed, diff_text, old_url, new_url):
        return _do_escalate(config, ctx, "redirect_unclean_diff", "the staged change was not a clean URL-only swap")

    detail = _open_pr_redirect(config, ctx, old_url, new_url)
    detail = _record_and_maybe_automerge(config, ctx, old_url, new_url, detail)
    _record_ledger(config, ctx, "pr_open", detail)
    return Outcome(ctx.fingerprint, "pr_opened", detail)


def _swap_url_cell(line: str, old_url: str, new_url: str) -> str | None:
    """Replace a markdown table cell whose trimmed value is exactly ``old_url`` with ``new_url``.

    Returns the rewritten line, or ``None`` if the line does not have exactly one pipe-delimited
    cell equal to ``old_url``. This is intentionally independent of the replacement regex: it matches
    a *complete* table cell, so a sibling URL that merely has ``old_url`` as a prefix (a different,
    longer cell value) is never mistaken for the target. ``old_url`` is always a full Learn URL drawn
    from the URL column (``source_url`` is parsed from that column), so the matched cell is the URL
    cell in practice; a non-URL column could only collide if a Title/Date cell were literally a full
    URL, which the catalog does not contain.
    """

    cells = line.split("|")
    hits = [
        i
        for i, cell in enumerate(cells)
        if autodoc_classifier._canonicalize_url(cell.strip())  # noqa: SLF001
        == autodoc_classifier._canonicalize_url(old_url)  # noqa: SLF001
    ]
    if len(hits) != 1:
        return None
    index = hits[0]
    actual_url = cells[index].strip()
    cells[index] = cells[index].replace(actual_url, new_url, 1)
    return "|".join(cells)


def _redirect_diff_is_clean(changed_files: list[str], allowed: list[str], diff_text: str, old_url: str, new_url: str) -> bool:
    """True only if the staged diff is exactly an old_url→new_url swap confined to allowed files.

    The check is structural (table-cell based), not a string ``replace``: every removed line must be a
    table row whose URL cell is *exactly* ``old_url`` and whose only difference from the matching added
    line is that cell becoming ``new_url``. A prefix-corrupted sibling URL (cell value != ``old_url``)
    therefore fails this guard even if the replacement regex had let it through.
    """

    if not changed_files or any(rel not in allowed for rel in changed_files):
        return False
    added: list[str] = []
    removed: list[str] = []
    for line in diff_text.splitlines():
        if line.startswith(("+++", "---")):
            continue
        if line.startswith("+"):
            added.append(line[1:])
        elif line.startswith("-"):
            removed.append(line[1:])
    if not added or len(added) != len(removed):
        return False
    transformed: list[str] = []
    for line in removed:
        swapped = _swap_url_cell(line, old_url, new_url)
        if swapped is None or new_url not in swapped:
            return False
        transformed.append(swapped)
    return sorted(transformed) == sorted(added)


def _open_pr_redirect(config: RunnerConfig, ctx: ChangeContext, old_url: str, new_url: str) -> str:
    """Commit the verified URL swap and open an OceanSquad-reviewed PR."""

    if config.dry_run:
        return f"dry-run: would open redirect PR for {ctx.branch} ({old_url} -> {new_url})"
    commit_message = f"docs(autodoc): update redirected Learn URL\n\nAUTODOC-FINGERPRINT: {ctx.fingerprint}"
    _git(config, "commit", "-m", commit_message)
    pr_body = (
        "Automated **deterministic** Learn-URL redirect update.\n\n"
        f"AUTODOC-FINGERPRINT: {ctx.fingerprint}\n"
        f"Source report: {ctx.report_path}\n\n"
        f"`{old_url}`\n→ `{new_url}`\n\n"
        "No LLM was involved: the runner applied the exact URL swap and verified the staged diff "
        "is a clean URL-only change in the Learn URL list.\n\n"
        "Merge policy: OceanSquad reviews and SHA-pinned merges after all required checks pass. "
        "Owner review is required only if automation escalates the PR."
    )
    return _push_and_create_pr(config, ctx, pr_body)


# --------------------------------------------------------------------------------------
# Redirect agreement telemetry (observational; native auto-merge disabled)
# --------------------------------------------------------------------------------------


def _automerge_ledger_file(config: RunnerConfig) -> Path:
    return config.automerge_ledger_abs or (config.repo_path / config.automerge_ledger_path)


def _pr_number_from_detail(detail: str) -> int | None:
    match = re.search(r"/pull/(\d+)", detail or "")
    return int(match.group(1)) if match else None


def _record_and_maybe_automerge(config: RunnerConfig, ctx: ChangeContext, old_url: str, new_url: str, detail: str) -> str:
    """Record the redirect outcome for agreement telemetry without enabling native auto-merge.

    OceanSquad is the sole merge owner. The historical unlock calculation remains available
    as observational metadata, but this target never calls ``gh pr merge --auto``.
    """

    if config.dry_run:
        return detail
    pr_number = _pr_number_from_detail(detail)
    if pr_number is None:
        return detail
    ledger = _automerge_ledger_file(config)
    autodoc_automerge.record_drafted(
        ledger,
        fingerprint=ctx.fingerprint,
        pr_number=pr_number,
        pr_url=detail,
        old_url=old_url,
        new_url=new_url,
    )
    state = autodoc_automerge.unlock_state(ledger)
    return f"{detail} (OceanSquad merge; target-native auto-merge disabled; observed gate: {state.reason})"


def _enable_automerge(config: RunnerConfig, ctx: ChangeContext) -> None:
    """Fail closed: OceanSquad, not GitHub native auto-merge, owns final merges."""

    raise RuntimeError("target-native autodoc auto-merge is disabled")


def _reconcile_automerge(config: RunnerConfig) -> None:
    """Update the agreement ledger with the observed outcomes of past redirect sample PRs.

    Side-effecting (gh queries) and isolated so tests can monkeypatch it. Best-effort: a
    failed lookup leaves a sample ``open`` so it never counts as agreement (fail-closed).
    """

    ledger = _automerge_ledger_file(config)
    if not ledger.exists():
        return
    try:
        autodoc_automerge.reconcile(ledger, lambda sample: _fetch_pr_state(config, sample))
    except Exception:  # noqa: BLE001 - reconcile is best-effort and must not abort a run.
        return


def _fetch_pr_state(config: RunnerConfig, sample: dict[str, Any]) -> autodoc_automerge.PrState:
    # Once a sample is known merged, the only thing that can still change is whether its
    # merge commit was reverted. Re-check that with git against the stored merge sha — git
    # on the hard-synced checkout is reliable and _commit_is_reverted fails CLOSED — instead
    # of gh, which can fail open (a gh outage must never let a reverted sample keep counting).
    stored_sha = sample.get("merge_sha")
    if stored_sha:
        return autodoc_automerge.PrState(
            "merged", merge_sha=stored_sha, reverted=_commit_is_reverted(config, stored_sha)
        )

    pr_number = sample.get("pr_number")
    completed = subprocess.run(
        ["gh", "pr", "view", str(pr_number), "--repo", _repo_slug(config), "--json", "state,mergeCommit"],
        check=False,
        capture_output=True,
        text=True,
        cwd=str(config.repo_path),
    )
    if completed.returncode != 0:
        return autodoc_automerge.PrState("open")
    info = json.loads(completed.stdout or "{}")
    gh_state = str(info.get("state") or "").upper()
    if gh_state == "MERGED":
        merge_sha = (info.get("mergeCommit") or {}).get("oid")
        if not merge_sha:
            return autodoc_automerge.PrState("open")  # merged but sha unknown -> retry next run
        if _commit_is_reverted(config, merge_sha):
            return autodoc_automerge.PrState("merged", merge_sha=merge_sha, reverted=True)
        diff = _fetch_commit_diff(config, merge_sha)
        return autodoc_automerge.PrState("merged", merged_diff=diff, merge_sha=merge_sha)
    if gh_state == "CLOSED":
        return autodoc_automerge.PrState("closed")
    return autodoc_automerge.PrState("open")


def _commit_is_reverted(config: RunnerConfig, sha: str) -> bool:
    """True if ``base_branch`` contains a commit reverting ``sha``.

    Detects both a human revert and the automated auto-revert PR, since ``git revert``
    writes the canonical ``This reverts commit <full-sha>`` trailer. This is what makes the
    gate's "zero post-merge reverts" condition real: a merged sample later reverted flips to
    ``reverted`` and re-locks the gate. The dedicated checkout is hard-synced to
    ``origin/<base>`` each run, so the log query sees the current main. **Fails closed**: if
    the query cannot be run (non-zero exit), the sample is treated as reverted so an
    indeterminate revert status never silently counts as agreement.
    """

    completed = subprocess.run(
        ["git", "-C", str(config.repo_path), "log", "--format=%H", "--grep", f"This reverts commit {sha}", config.base_branch],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        return True
    return bool((completed.stdout or "").strip())


def _fetch_commit_diff(config: RunnerConfig, sha: str) -> str | None:
    completed = subprocess.run(
        ["gh", "api", "-H", "Accept: application/vnd.github.v3.diff", f"repos/{_repo_slug(config)}/commits/{sha}"],
        check=False,
        capture_output=True,
        text=True,
        cwd=str(config.repo_path),
    )
    return completed.stdout if completed.returncode == 0 else None


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


def _assert_canary(config: RunnerConfig) -> None:
    """Halt routing if deterministic or explicitly enabled cross-model poison checks leak."""

    verifier_hook = None
    if os.environ.get("AUTODOC_CANARY_CROSS_MODEL_ENABLED", "").strip().lower() == "true":
        verifier_hook = autodoc_canary.make_cross_model_verifier(
            model=config.review_model,
            timeout=config.review_timeout,
        )
    failures = [name for name, rejected, _decision in autodoc_canary.run_canary(verifier_hook) if not rejected]
    if failures:
        raise RuntimeError(f"autodoc canary failed closed: {', '.join(failures)}")


def _latest_report(config: RunnerConfig) -> Path | None:
    reports = sorted((config.repo_path).glob(config.reports_glob))
    return reports[-1] if reports else None


def _run_draft(config: RunnerConfig, ctx: ChangeContext, feedback: str) -> DraftResult:
    """Drive the Copilot CLI to edit the allowed files in the working tree.

    To keep drafts fast and deterministic, the current content of the allowed file(s) is
    read and inlined into the prompt so the model can make a targeted edit WITHOUT exploring
    the (large) worktree. Everything the draft touches (including new untracked files) is then
    staged with ``git add -A`` so the deterministic verifier and the review see the full change
    set — the path allowlist flags anything off-contract. Cleanup of any files the draft
    creates is handled by ``_reset_attempt`` against the branch-start baseline.
    """

    file_contents = _read_allowed_files(config, ctx)
    prompt = _build_draft_prompt(ctx, feedback, file_contents)
    # Pass the prompt via STDIN, not as a `-p` argument: inlined file content can exceed the
    # Windows command-line length limit (~32 KB → WinError 206). Copilot CLI runs the piped
    # prompt non-interactively and exits.
    completed = subprocess.run(
        [
            COPILOT_BIN,
            "--model",
            config.draft_model,
            "-s",
            "--no-ask-user",
            "--no-remote",
            "--allow-all-tools",
            "-C",
            str(config.repo_path),
        ],
        input=prompt,
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


def _read_allowed_files(config: RunnerConfig, ctx: ChangeContext) -> dict[str, str | None]:
    """Return current content for each allowed file (None when too large to inline or new)."""

    contents: dict[str, str | None] = {}
    for rel in ctx.contract.get("allowed_files", []):
        path = config.repo_path / rel
        try:
            if path.is_file():
                text = path.read_text(encoding="utf-8", errors="replace")
                contents[rel] = text if len(text) <= MAX_INLINE_FILE_CHARS else None
            else:
                contents[rel] = None
        except OSError:
            contents[rel] = None
    return contents


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


def _build_draft_prompt(ctx: ChangeContext, feedback: str, file_contents: dict[str, str | None]) -> str:
    feedback_block = ""
    if feedback:
        feedback_block = (
            "\n\nA previous attempt was rejected by the verifiers. Correct exactly these problems "
            f"and make no other changes:\n{feedback}\n"
        )

    files_block_parts: list[str] = []
    for rel, content in file_contents.items():
        if content is None:
            files_block_parts.append(
                f"\n### `{rel}`\nOpen this file directly in the working tree (it is too large to inline, "
                "or it does not exist yet and must be created).\n"
            )
        else:
            files_block_parts.append(f"\n### Current content of `{rel}`\n```markdown\n{content}\n```\n")
    files_block = "".join(files_block_parts) or "\n(no allowed files resolved; do not edit anything)\n"

    return (
        "You are drafting a minimal, faithful documentation edit for a US financial-services "
        "compliance framework. Follow the authoring contract and task below EXACTLY. Edit only the "
        "files listed in allowed_files, touch only the allowed_headings, and ground every change "
        "solely in the Learn change evidence — invent nothing. Use FSI-safe language (never "
        "'ensures compliance', 'guarantees', 'will prevent', 'eliminates risk'). If the evidence "
        f"does not support a concrete edit, print {NEEDS_HUMAN_MARKER} and make no file changes.\n\n"
        "IMPORTANT — work only from what is in this prompt. The current content of the file(s) you "
        "may edit is provided below. Do NOT read, search, list, or open any OTHER files in the "
        "repository; make a single targeted edit to the allowed file(s).\n\n"
        f"{ctx.instructions}{feedback_block}\n\n"
        f"## Files you may edit (current content)\n{files_block}\n"
        "Apply the minimal edit to the allowed file(s) now."
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
    """Commit the verified draft, push as the owner, and open an OceanSquad-reviewed PR."""

    if config.dry_run:
        return f"dry-run: would open PR for {ctx.branch}"
    commit_message = f"docs(autodoc): {ctx.title}\n\nAUTODOC-FINGERPRINT: {ctx.fingerprint}"
    # The verified change set is already staged by _run_draft (git add -A) and the
    # deterministic verifier confirmed only allowed_files changed, so commit the staged set.
    _git(config, "commit", "-m", commit_message)
    pr_body = (
        f"Automated documentation draft.\n\n"
        f"AUTODOC-FINGERPRINT: {ctx.fingerprint}\n"
        f"Source report: {ctx.report_path}\n\n"
        f"Independent cross-model review verdict: {review_verdict.get('verdict', 'n/a')} "
        f"(confidence {review_verdict.get('confidence', 'n/a')}).\n\n"
        "Merge policy: OceanSquad reviews and SHA-pinned merges after all required checks pass. "
        "Owner review is required only if automation exhausts its review/fix path and escalates."
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
    # Include the source URL AND content hash so the deferred-baseline advance workflow
    # (learn-monitor-advance.yml) can match this issue to its EXACT pending change once it
    # is closed. The advance step compares these two lines verbatim against the pending blob's
    # (url, content_hash) — it never relies on GitHub's tokenized `in:body` search, which can
    # subset an unrelated issue's body and advance the wrong baseline (silent data loss).
    source_url = ctx.contract.get("source_url", "") if isinstance(ctx.contract, dict) else ""
    content_hash = ctx.contract.get("content_hash", "") if isinstance(ctx.contract, dict) else ""
    source_line = f"Source: {source_url}\n" if source_url else ""
    content_hash_line = f"Content-Hash: {content_hash}\n" if content_hash else ""
    body = (
        f"Autodoc escalation — human review required.\n\n"
        f"AUTODOC-FINGERPRINT: {ctx.fingerprint}\n"
        f"Reason: {reason}\n"
        f"{source_line}"
        f"{content_hash_line}"
        f"\n{details}\n"
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
    created_issue_url = (completed.stdout or "").strip()

    # Best-effort sibling supersession: once the new issue exists, close any OLDER open
    # issue that tracks the same exact Source but a different fingerprint. This cleanup
    # must never suppress creation success.
    source_url = ctx.contract.get("source_url", "") if isinstance(ctx.contract, dict) else ""
    if isinstance(source_url, str) and source_url.strip():
        try:
            _close_source_siblings_not_planned(
                config=config,
                source_url=source_url.strip(),
                fingerprint=ctx.fingerprint,
                superseding_issue_url=created_issue_url,
            )
        except Exception as exc:  # noqa: BLE001 - creation already succeeded; cleanup is best-effort.
            print(
                "warning: escalation issue was created but sibling supersession cleanup failed: "
                f"{exc}",
                file=sys.stderr,
            )
    return created_issue_url


def _existing_issue_url(config: RunnerConfig, ctx: ChangeContext) -> str | None:
    """Return the URL of an open escalation issue already carrying this fingerprint."""

    for issue in _list_open_autodoc_issues(config):
        if issue.fingerprint == ctx.fingerprint and issue.url:
            return issue.url
    return None


def _list_open_autodoc_issues(config: RunnerConfig) -> list[autodoc_issue_identity.IssueRecord]:
    """Return parsed open autodoc issues for exact local matching."""

    completed = subprocess.run(
        [
            "gh",
            "issue",
            "list",
            "--repo",
            _repo_slug(config),
            "--state",
            "open",
            "--label",
            "autodoc",
            "--json",
            "number,url,state,stateReason,body",
            "--limit",
            "500",
        ],
        check=False,
        capture_output=True,
        text=True,
        cwd=str(config.repo_path),
    )
    if completed.returncode != 0:
        return []
    try:
        payload = json.loads(completed.stdout or "[]")
    except ValueError:
        return []
    if not isinstance(payload, list):
        return []
    records: list[autodoc_issue_identity.IssueRecord] = []
    for item in payload:
        if isinstance(item, dict):
            records.append(autodoc_issue_identity.parse_issue_record(item))
    return [record for record in records if record.state == "OPEN"]


def _close_source_siblings_not_planned(
    *,
    config: RunnerConfig,
    source_url: str,
    fingerprint: str,
    superseding_issue_url: str,
) -> None:
    """Close older open same-source/different-fingerprint siblings as NOT_PLANNED."""

    superseding_number = _issue_number_from_url(superseding_issue_url)
    if superseding_number is None:
        return

    for issue in _list_open_autodoc_issues(config):
        if issue.source_url != source_url:
            continue
        if issue.fingerprint == fingerprint:
            continue
        if issue.number is None:
            continue
        if issue.number >= superseding_number:
            continue
        comment = (
            f"Superseded by {superseding_issue_url}.\n\n"
            "Audit: exact-source sibling supersession\n"
            f"- Exact Source: {source_url}\n"
            f"- Superseded fingerprint: {issue.fingerprint or 'unknown'}\n"
            f"- Active fingerprint: {fingerprint}\n"
        )
        completed = subprocess.run(
            [
                "gh",
                "issue",
                "close",
                str(issue.number),
                "--repo",
                _repo_slug(config),
                "--reason",
                "not planned",
                "--comment",
                comment,
            ],
            check=False,
            capture_output=True,
            text=True,
            cwd=str(config.repo_path),
        )
        if completed.returncode != 0:
            raise RuntimeError(
                "gh issue close failed "
                f"(#{issue.number}, exit {completed.returncode}): {(completed.stderr or '').strip()}"
            )


def _issue_number_from_url(url: str) -> int | None:
    match = _ISSUE_URL_NUMBER_RE.search(url.strip())
    if not match:
        return None
    return int(match.group(1))


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
    parser.add_argument("--draft-timeout", type=int, default=DEFAULT_DRAFT_TIMEOUT, help="Seconds before a draft is abandoned (an Opus draft exploring a large repo can be slow).")
    parser.add_argument("--review-timeout", type=int, default=DEFAULT_REVIEW_TIMEOUT, help="Seconds before the independent review is abandoned.")
    parser.add_argument("--dry-run", action="store_true", help="Do everything except push/PR/escalate.")
    args = parser.parse_args(argv)

    config = RunnerConfig(
        repo_path=Path(args.repo).resolve(),
        draft_model=args.draft_model,
        review_model=args.review_model,
        max_fix_cycles=args.max_fix_cycles,
        draft_timeout=args.draft_timeout,
        review_timeout=args.review_timeout,
        dry_run=args.dry_run,
    )
    summary = run(config)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
