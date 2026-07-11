#!/usr/bin/env python3
"""Build deterministic GitHub issue specs for Learn Monitor autodoc routing."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

import autodoc_classifier as classifier
import autodoc_verify

ALLOWED_HEADINGS = [
    "Additional Resources",
    "Implementation Notes",
    "Implementation Playbooks",
    "Verification Criteria",
    "Related Controls",
]
FORBIDDEN_PATHS = [
    ".github/**",
    "scripts/**",
    "data/**",
    "reports/**",
    "assessment/**",
    "mkdocs.yml",
]
# A URL redirect only ever updates the Learn URL list — never a control or playbook file.
REDIRECT_TARGET_FILE = "docs/reference/microsoft-learn-urls.md"

_CHANGE_BLOCK_RE = re.compile(
    r"^### \d+\.\s*(?P<topic>.+?)\n(?P<body>.*?)(?=^### \d+\.\s|^## |\Z)",
    re.DOTALL | re.MULTILINE,
)
_URL_RE = re.compile(r"^\*\*URL:\*\*\s*(\S+)", re.MULTILINE)
_DIFF_RE = re.compile(r"```diff\n.*?```", re.DOTALL)
_CONTROL_FILE_RE = re.compile(r"^\s*-\s*File:\s*`([^`]+\.md)`", re.MULTILINE)
_AFFECTED_PLAYBOOKS_RE = re.compile(
    r"^\*\*Affected Playbooks:\*\*(?P<body>.*?)(?=^\*\*|^---\s*$|^### |\Z)",
    re.DOTALL | re.MULTILINE,
)
_MD_CODE_SPAN_RE = re.compile(r"`([^`]+\.md)`")


def _normalise_repo_path(path: str) -> str:
    normalised = path.strip().replace("\\", "/").lstrip("/")
    if normalised.startswith("./"):
        normalised = normalised[2:]
    if not normalised.startswith("docs/"):
        normalised = f"docs/{normalised}"
    return normalised


def _dedupe_keep_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            out.append(value)
    return out


def compute_fingerprint(
    report_name: str,
    url: str,
    classification: str,
    allowed_files: list[str],
    destination_url: str = "",
) -> str:
    """Return a stable sha256 fingerprint for a routed Learn change."""
    canonical_url = classifier._canonicalize_url(url)  # noqa: SLF001 - shared routing identity rule.
    canonical_destination = classifier._canonicalize_url(  # noqa: SLF001 - shared routing identity rule.
        destination_url
    )
    parts = [report_name, canonical_url, classification, *sorted(allowed_files)]
    if canonical_destination:
        parts.append(f"destination:{canonical_destination}")
    payload = "\n".join(parts)
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def extract_allowed_files(change_block_text: str) -> list[str]:
    """Extract docs-relative control and playbook paths from one report change block."""
    raw_paths = [_normalise_repo_path(path) for path in _CONTROL_FILE_RE.findall(change_block_text)]

    playbooks_match = _AFFECTED_PLAYBOOKS_RE.search(change_block_text)
    if playbooks_match:
        raw_paths.extend(_normalise_repo_path(path) for path in _MD_CODE_SPAN_RE.findall(playbooks_match.group("body")))

    return _dedupe_keep_order(raw_paths)


def build_contract(
    decision: classifier.RoutingDecision,
    report_name: str,
    allowed_files: list[str],
    fingerprint: str,
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    """Build the machine-readable authoring contract embedded in the issue body.

    For redirect changes the allowed file is the URL list (``microsoft-learn-urls.md``), whose
    section headings are topic names (``Copilot Studio`` …) rather than the generic control
    headings. So a redirect contract's ``allowed_headings`` are that file's OWN headings, letting
    a minimal URL edit pass the verifier's section check while the other checks (path-allowlist,
    diff-minimality, claim-support, language) still gate it.
    """
    if getattr(decision, "kind", "content") == "redirect":
        allowed_headings = _redirect_allowed_headings(repo_root, allowed_files)
    else:
        allowed_headings = list(ALLOWED_HEADINGS)
    return {
        "schema_version": 1,
        "fingerprint": fingerprint,
        "report_path": f"reports/monitoring/{Path(report_name).name}",
        "source_url": classifier._canonicalize_url(decision.url),  # noqa: SLF001
        "destination_url": classifier._canonicalize_url(  # noqa: SLF001
            getattr(decision, "destination_url", "")
        ),
        "content_hash": getattr(decision, "content_hash", ""),
        "classification": decision.classification,
        "route": decision.route,
        "automerge_eligible": decision.automerge_eligible,
        "allowed_files": list(allowed_files),
        "allowed_headings": allowed_headings,
        "forbidden_paths": list(FORBIDDEN_PATHS),
        "validation": [
            "python scripts/verify_language_rules.py <files>",
            "mkdocs build --strict",
        ],
    }


def _redirect_allowed_headings(repo_root: str | Path, allowed_files: list[str]) -> list[str]:
    """Return the headings present in the redirect target file(s), using the SAME CommonMark
    parser as the verifier so the contract's headings match what the verifier extracts."""
    headings: set[str] = set()
    for rel in allowed_files:
        path = Path(repo_root) / rel
        try:
            content = path.read_text(encoding="utf-8")
        except OSError:
            continue
        for text in autodoc_verify._heading_lookup(content.splitlines()).values():  # noqa: SLF001 - shared heading oracle.
            if text:
                headings.add(text)
    return sorted(headings)


def _issue_title(decision: classifier.RoutingDecision) -> str:
    topic = re.sub(r"\s+", " ", decision.topic).strip()
    prefix = "Autodoc draft" if decision.route == "autodraft" else "Autodoc human review"
    return f"{prefix}: {topic}"[:240]


def _diff_excerpt(change: classifier.Change) -> str:
    excerpt = change.diff_text.strip() or change.reason.strip() or "No diff excerpt was included in the report."
    if len(excerpt) > 1500:
        return excerpt[:1500].rstrip() + "\n..."
    return excerpt


def build_issue(
    decision: classifier.RoutingDecision,
    change: classifier.Change,
    contract: dict[str, Any],
    fingerprint: str,
) -> dict[str, Any]:
    """Build a GitHub issue specification for one routing decision."""
    labels = (
        ["autodoc", "squad:copilot"]
        if decision.route == "autodraft"
        else ["autodoc", "escalate", "needs-review"]
    )
    human_note = ""
    if decision.route == "human":
        human_note = (
            "\n> **Human analysis required:** This change routed to `human`; a human must analyze it. "
            "No agent draft should be requested from this issue.\n"
        )

    contract_json = json.dumps(contract, indent=2, sort_keys=True)
    body = f"""AUTODOC-FINGERPRINT: {fingerprint}
AUTODOC-REPORT: {contract["report_path"]}
AUTODOC-ROUTE: {decision.route}
AUTODOC-AUTOMERGE-ELIGIBLE: {json.dumps(decision.automerge_eligible)}
{human_note}
```json
{contract_json}
```

## Task

Make the smallest faithful documentation edit for the Learn change below. Edit only allowed_files; do not reformat unrelated content; preserve admonitions; do NOT edit regulatory obligations/legal interpretation; use FSI-safe language (avoid 'ensures compliance','guarantees','will prevent','eliminates risk'); if the report does not support a specific edit, comment `AUTODOC-NEEDS-HUMAN` and stop.

## Learn change evidence

```diff
{_diff_excerpt(change)}
```

## Required PR body

Include `Closes #<issue>` and `AUTODOC-FINGERPRINT: {fingerprint}` in the PR body.
"""
    return {"title": _issue_title(decision), "body": body, "labels": labels}


def _empty_ledger() -> dict[str, Any]:
    return {"schema_version": 1, "changes": {}}


def load_ledger(path: str | Path) -> dict[str, Any]:
    """Load the autodoc ledger, returning an empty v1 ledger when it does not exist."""
    ledger_path = Path(path)
    if not ledger_path.exists():
        return _empty_ledger()
    try:
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid autodoc ledger JSON: {ledger_path}") from exc

    if not isinstance(ledger, dict) or ledger.get("schema_version") != 1:
        raise ValueError(f"Unsupported autodoc ledger schema: {ledger_path}")
    if not isinstance(ledger.get("changes"), dict):
        raise ValueError(f"Autodoc ledger changes must be an object: {ledger_path}")
    return ledger


def save_ledger(path: str | Path, ledger: dict[str, Any]) -> None:
    """Persist an autodoc ledger as stable JSON."""
    if not isinstance(ledger, dict) or ledger.get("schema_version") != 1:
        raise ValueError("Refusing to save unsupported autodoc ledger schema")
    if not isinstance(ledger.get("changes"), dict):
        raise ValueError("Refusing to save autodoc ledger without a changes object")

    ledger_path = Path(path)
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    ledger_path.write_text(json.dumps(ledger, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def already_processed(ledger: dict[str, Any], fingerprint: str) -> bool:
    return fingerprint in ledger.get("changes", {})


def _change_blocks_by_url(report_text: str) -> dict[str, str]:
    blocks: dict[str, str] = {}
    for match in _CHANGE_BLOCK_RE.finditer(report_text):
        block = match.group(0)
        url_match = _URL_RE.search(block)
        if not url_match:
            continue
        url = classifier._canonicalize_url(url_match.group(1))  # noqa: SLF001
        existing = blocks.get(url)
        if existing is None or (_DIFF_RE.search(block) and not _DIFF_RE.search(existing)):
            blocks[url] = block
    return blocks


def _allowed_files_for_change(change: classifier.Change, block_text: str) -> list[str]:
    if change.kind == "redirect":
        # A URL redirect must ONLY ever edit the Learn URL list — never a control/playbook file.
        # The same URL can appear in both a detailed change block (with a `- File:` control) and
        # the redirect table; without this guard the redirect would inherit that control file in
        # allowed_files and could edit control prose (and is auto-merge-eligible). Always pin it.
        return [REDIRECT_TARGET_FILE]
    return extract_allowed_files(block_text)


def route_report(report_text: str, report_name: str, ledger: dict[str, Any], repo_root: str | Path = ".") -> list[dict[str, Any]]:
    """Classify a Learn report and return issue specs for changes not present in the ledger."""
    changes = classifier.parse_report(report_text)
    decisions = classifier.classify_report(report_text)
    blocks_by_url = _change_blocks_by_url(report_text)
    issue_specs: list[dict[str, Any]] = []

    for change, decision in zip(changes, decisions, strict=True):
        allowed_files = _allowed_files_for_change(change, blocks_by_url.get(change.url, ""))
        fingerprint = compute_fingerprint(
            report_name,
            decision.url,
            decision.classification,
            allowed_files,
            getattr(decision, "destination_url", ""),
        )
        if already_processed(ledger, fingerprint):
            continue

        contract = build_contract(decision, report_name, allowed_files, fingerprint, repo_root)
        issue = build_issue(decision, change, contract, fingerprint)
        issue_specs.append(
            {
                "fingerprint": fingerprint,
                "route": decision.route,
                "automerge_eligible": decision.automerge_eligible,
                "title": issue["title"],
                "body": issue["body"],
                "labels": issue["labels"],
            }
        )

    return issue_specs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", required=True, help="Path to a reports/monitoring/learn-changes-*.md report")
    parser.add_argument("--ledger", required=True, help="Path to data/autodoc-ledger.json")
    parser.add_argument("--out", help="Path where issue-spec JSON should be written")
    parser.add_argument("--repo-root", default=".", help="Repo root for resolving allowed_files (redirect heading extraction)")
    args = parser.parse_args(argv)

    report_path = Path(args.report)
    report_text = report_path.read_text(encoding="utf-8")
    ledger = load_ledger(args.ledger)
    issue_specs = route_report(report_text, report_path.name, ledger, repo_root=args.repo_root)

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(issue_specs, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"Wrote {len(issue_specs)} issue spec(s) to {out_path}")
    else:
        print(json.dumps(issue_specs, indent=2, sort_keys=True))

    autodraft = sum(1 for spec in issue_specs if spec["route"] == "autodraft")
    human = sum(1 for spec in issue_specs if spec["route"] == "human")
    print(f"Autodoc route summary: total={len(issue_specs)} autodraft={autodraft} human={human}")
    return 0


if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):  # pragma: no cover
        pass


if __name__ == "__main__":
    raise SystemExit(main())
