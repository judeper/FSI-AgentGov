"""Autodoc fix-retry and escalation decision helpers.

This module is intentionally pure-stdlib and offline. GitHub API calls live in the
workflow; this file only makes deterministic, fail-closed decisions and builds the
comments the workflow posts.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

_RETRY_MARKER_RE = re.compile(r"^\s*AUTODOC-RETRY:\s*(\d+)\s*/\s*(\d+)\s*$", re.IGNORECASE | re.MULTILINE)
_DEFAULT_FINDINGS_SUMMARY = "No verifier findings summary was available."


def count_attempts(pr_comments: list[str]) -> int:
    """Count prior autodoc retry markers in PR comment bodies."""

    attempts = 0
    for body in pr_comments:
        if not isinstance(body, str):
            continue
        attempts += sum(1 for _match in _RETRY_MARKER_RE.finditer(body))
    return attempts


def decide(attempts: int, max_cycles: int, verifier_conclusion: str) -> dict[str, int | str]:
    """Return a fail-closed retry/escalation decision for an Autodoc Verify result."""

    next_attempt = attempts + 1
    conclusion = (verifier_conclusion or "").strip()
    if conclusion == "needs_human":
        return {
            "action": "escalate",
            "next_attempt": next_attempt,
            "reason": "verifier_conclusion=needs_human requires human judgment",
        }
    if conclusion != "fail":
        normalized = conclusion if conclusion else "unknown"
        return {
            "action": "escalate",
            "next_attempt": next_attempt,
            "reason": f"verifier_conclusion={normalized} is not auto-retryable",
        }
    if attempts >= max_cycles:
        return {
            "action": "escalate",
            "next_attempt": next_attempt,
            "reason": f"retry limit reached ({attempts}/{max_cycles})",
        }
    return {
        "action": "retry",
        "next_attempt": next_attempt,
        "reason": f"verifier_conclusion=fail and retry limit not reached ({attempts}/{max_cycles})",
    }


def build_retry_comment(next_attempt: int, max_cycles: int, findings_summary: str) -> str:
    """Build the PR comment that re-tasks the Copilot coding agent."""

    summary = _normalize_summary(findings_summary)
    return "\n".join(
        [
            "### Autodoc fix retry requested",
            "",
            f"AUTODOC-RETRY: {next_attempt}/{max_cycles}",
            "",
            "Autodoc Verify failed on checks that may be fixable by a bounded retry.",
            "",
            "**Failing checks summary:**",
            summary,
            "",
            "@copilot please revise this autodoc PR to address the failing checks.",
            "",
            "Hard constraints:",
            "- Preserve the same `AUTODOC-FINGERPRINT` value; do not replace or remove it.",
            "- Stay within the autodoc contract's `allowed_files`; do not edit any other files.",
            "- Keep the change scoped to the source monitoring report and the linked contract.",
            "- Do not advance any baseline, merge this PR, or broaden the documented claim.",
        ]
    ) + "\n"


def build_escalation_comment(attempts: int, reason: str) -> str:
    """Build the PR comment explaining why a human must review the autodoc draft."""

    normalized_reason = (reason or "unspecified fail-closed reason").strip()
    return "\n".join(
        [
            "### Autodoc escalated to human review",
            "",
            "Autodoc fix-retry stopped instead of asking the agent for another change.",
            "",
            f"- Prior retry attempts: {attempts}",
            f"- Reason: {normalized_reason}",
            "",
            "A human reviewer should inspect the PR, the linked contract, and the verifier findings.",
            "No baseline was advanced and no merge action was taken.",
        ]
    ) + "\n"


def main(argv: list[str] | None = None) -> int:
    """CLI entry point used by the GitHub Actions workflow."""

    parser = argparse.ArgumentParser(description="Decide whether autodoc should retry or escalate.")
    parser.add_argument("--comments-json", required=True, help="Issue comments JSON from the GitHub API.")
    parser.add_argument("--conclusion", required=True, help="Verifier conclusion: fail, needs_human, or unknown.")
    parser.add_argument("--max-cycles", required=True, type=int, help="Maximum retry cycles allowed.")
    parser.add_argument("--summary", default="", help="Verifier findings summary text.")
    parser.add_argument("--summary-file", help="Path to verifier findings summary text.")
    parser.add_argument("--decision-out", required=True, help="Path to write decision JSON.")
    parser.add_argument("--comment-out", required=True, help="Path to write the retry/escalation comment body.")
    args = parser.parse_args(argv)

    comments = _load_comment_bodies(Path(args.comments_json))
    attempts = count_attempts(comments)
    decision = decide(attempts, args.max_cycles, args.conclusion)
    summary = _read_summary(args.summary, args.summary_file)

    if decision["action"] == "retry":
        comment = build_retry_comment(int(decision["next_attempt"]), args.max_cycles, summary)
    else:
        comment = build_escalation_comment(attempts, str(decision["reason"]))

    payload = {
        "attempts": attempts,
        "max_cycles": args.max_cycles,
        "verifier_conclusion": args.conclusion,
        **decision,
    }
    _write_text(Path(args.comment_out), comment)
    _write_text(Path(args.decision_out), json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(f"autodoc-retry decision: {payload['action']} ({payload['reason']})")
    return 0


def _load_comment_bodies(path: Path) -> list[str]:
    data: Any = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise SystemExit("comments JSON must be a list")
    bodies: list[str] = []
    for item in data:
        if isinstance(item, str):
            bodies.append(item)
        elif isinstance(item, dict):
            body = item.get("body")
            bodies.append(body if isinstance(body, str) else "")
        else:
            bodies.append("")
    return bodies


def _read_summary(summary: str, summary_file: str | None) -> str:
    if summary_file:
        return Path(summary_file).read_text(encoding="utf-8")
    return summary


def _normalize_summary(summary: str) -> str:
    stripped = (summary or "").strip()
    return stripped if stripped else _DEFAULT_FINDINGS_SUMMARY


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
