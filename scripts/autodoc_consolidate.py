#!/usr/bin/env python3
"""Consolidate autodoc issue supersession using exact-source identity."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Any

import autodoc_issue_identity

DEFAULT_MAX_CLOSURES = 10


def _repo_slug() -> str:
    return os.environ.get("AUTODOC_REPO", "judeper/FSI-AgentGov")


def load_issue_snapshot(path: str | Path) -> tuple[list[dict[str, Any]], str]:
    snapshot_path = Path(path)
    raw = snapshot_path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    payload = json.loads(raw.decode("utf-8"))
    if not isinstance(payload, list):
        raise ValueError(f"Issue snapshot must be a JSON array: {snapshot_path}")
    issues: list[dict[str, Any]] = []
    for item in payload:
        if isinstance(item, dict):
            issues.append(item)
    return issues, digest


def _issue_summary(issue: autodoc_issue_identity.IssueRecord) -> dict[str, Any]:
    return {
        "number": issue.number,
        "url": issue.url,
        "state": issue.state,
        "state_reason": issue.state_reason,
        "fingerprint": issue.fingerprint,
        "source_url": issue.source_url,
        "content_hash": issue.content_hash,
        "source_kind": issue.source_kind,
    }


def plan_supersession(issues: list[dict[str, Any]]) -> dict[str, Any]:
    records = autodoc_issue_identity.parse_issue_records(issues)
    closures: list[dict[str, Any]] = []
    active_open: list[dict[str, Any]] = []
    retained_unmappable: list[dict[str, Any]] = []
    retained_old_schema: list[dict[str, Any]] = []

    by_source: dict[str, list[autodoc_issue_identity.IssueRecord]] = {}
    for record in records:
        if record.source_url and record.fingerprint and record.number is not None:
            by_source.setdefault(record.source_url, []).append(record)
        elif record.fingerprint and not record.source_url:
            retained_old_schema.append(_issue_summary(record))
        else:
            retained_unmappable.append(_issue_summary(record))

    for source_url, grouped in sorted(by_source.items()):
        open_issues = [record for record in grouped if record.state == "OPEN"]
        completed_issues = [
            record
            for record in grouped
            if record.state == "CLOSED"
            and record.state_reason == "COMPLETED"
            and record.number is not None
        ]
        newest_open = max(open_issues, key=lambda item: item.number or -1) if open_issues else None
        newest_completed = (
            max(completed_issues, key=lambda item: item.number or -1)
            if completed_issues
            else None
        )

        for issue in sorted(open_issues, key=lambda item: item.number or -1):
            anchor: autodoc_issue_identity.IssueRecord | None = None
            reason = ""
            if (
                newest_completed is not None
                and issue.number is not None
                and newest_completed.number is not None
                and issue.number < newest_completed.number
                and issue.fingerprint != newest_completed.fingerprint
            ):
                anchor = newest_completed
                reason = "completed_source_supersession"
            elif (
                newest_open is not None
                and newest_open.number is not None
                and issue.number != newest_open.number
                and issue.fingerprint != newest_open.fingerprint
            ):
                anchor = newest_open
                reason = "newer_open_source_supersession"

            if anchor is None:
                active_open.append(_issue_summary(issue))
                continue

            closures.append(
                {
                    "number": issue.number,
                    "url": issue.url,
                    "fingerprint": issue.fingerprint,
                    "source_url": source_url,
                    "reason": reason,
                    "superseded_by": {
                        "number": anchor.number,
                        "url": anchor.url,
                        "fingerprint": anchor.fingerprint,
                        "state": anchor.state,
                        "state_reason": anchor.state_reason,
                    },
                }
            )

    return {
        "summary": {
            "issues_total": len(records),
            "closures_planned": len(closures),
            "active_open": len(active_open),
            "retained_old_schema": len(retained_old_schema),
            "retained_unmappable": len(retained_unmappable),
        },
        "closures": sorted(closures, key=lambda item: item["number"] or -1),
        "retained": {
            "active_open": sorted(active_open, key=lambda item: item.get("number") or -1),
            "old_schema": sorted(retained_old_schema, key=lambda item: item.get("number") or -1),
            "unmappable": sorted(retained_unmappable, key=lambda item: item.get("number") or -1),
        },
    }


def _close_issue_not_planned(repo: str, closure: dict[str, Any]) -> tuple[bool, str]:
    number = closure.get("number")
    superseded = closure.get("superseded_by", {})
    source = closure.get("source_url", "")
    comment = (
        f"Superseded by {superseded.get('url')}.\n\n"
        "Audit: exact-source sibling supersession\n"
        f"- Exact Source: {source}\n"
        f"- This fingerprint: {closure.get('fingerprint')}\n"
        f"- Active fingerprint: {superseded.get('fingerprint')}\n"
        f"- Consolidation reason: {closure.get('reason')}\n"
    )
    completed = subprocess.run(
        [
            "gh",
            "issue",
            "close",
            str(number),
            "--repo",
            repo,
            "--reason",
            "not planned",
            "--comment",
            comment,
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        return False, (completed.stderr or "").strip()
    return True, (completed.stdout or "").strip()


def _build_guard_errors(
    *,
    apply_mode: bool,
    expected_count: int | None,
    expected_snapshot_sha256: str | None,
    actual_count: int,
    actual_snapshot_sha256: str,
) -> list[str]:
    errors: list[str] = []
    if apply_mode and (expected_count is None or expected_snapshot_sha256 is None):
        errors.append("apply mode requires both --expected-count and --expected-snapshot-sha256")
    if expected_count is not None and expected_count != actual_count:
        errors.append(f"expected_count mismatch: expected={expected_count} actual={actual_count}")
    if (
        expected_snapshot_sha256 is not None
        and expected_snapshot_sha256.lower() != actual_snapshot_sha256.lower()
    ):
        errors.append(
            "expected_snapshot_sha256 mismatch: "
            f"expected={expected_snapshot_sha256} actual={actual_snapshot_sha256}"
        )
    return errors


def _non_negative_int(value: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("must be >= 0")
    return parsed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--issues-json", required=True, help="Path to `gh issue list --json ...` snapshot.")
    parser.add_argument("--repo", default=_repo_slug(), help="GitHub repo slug for apply mode.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true", help="Apply NOT_PLANNED closures.")
    mode.add_argument("--dry-run", action="store_true", help="Plan only (default).")
    parser.add_argument("--expected-count", type=int, help="Abort if snapshot issue count differs.")
    parser.add_argument(
        "--expected-snapshot-sha256",
        help="Abort if snapshot SHA-256 differs from this value.",
    )
    parser.add_argument(
        "--max-closures",
        type=_non_negative_int,
        default=DEFAULT_MAX_CLOSURES,
        help=f"Abort apply before writes if planned closures exceed this ceiling (default: {DEFAULT_MAX_CLOSURES}).",
    )
    args = parser.parse_args(argv)

    dry_run = not args.apply
    issues, snapshot_sha256 = load_issue_snapshot(args.issues_json)
    guard_errors = _build_guard_errors(
        apply_mode=args.apply,
        expected_count=args.expected_count,
        expected_snapshot_sha256=args.expected_snapshot_sha256,
        actual_count=len(issues),
        actual_snapshot_sha256=snapshot_sha256,
    )
    result: dict[str, Any] = {
        "mode": "dry_run" if dry_run else "apply",
        "snapshot": {
            "path": str(Path(args.issues_json)),
            "count": len(issues),
            "sha256": snapshot_sha256,
        },
        "guards": {
            "expected_count": args.expected_count,
            "expected_snapshot_sha256": args.expected_snapshot_sha256,
            "max_closures": args.max_closures if args.apply else None,
            "ok": not guard_errors,
            "errors": guard_errors,
        },
        "writes": {"attempted": 0, "succeeded": 0, "failed": []},
    }
    if guard_errors:
        result["aborted"] = True
        print(json.dumps(result, indent=2, sort_keys=True))
        return 2

    plan = plan_supersession(issues)
    result.update(plan)
    if args.apply and plan["summary"]["closures_planned"] > args.max_closures:
        result["guards"]["ok"] = False
        result["guards"]["errors"].append(
            "max_closures exceeded: "
            f"planned={plan['summary']['closures_planned']} limit={args.max_closures}"
        )
        result["aborted"] = True
        print(json.dumps(result, indent=2, sort_keys=True))
        return 2

    if dry_run:
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0

    failures: list[dict[str, Any]] = []
    succeeded = 0
    for closure in plan["closures"]:
        ok, output = _close_issue_not_planned(args.repo, closure)
        result["writes"]["attempted"] += 1
        if ok:
            succeeded += 1
        else:
            failures.append(
                {
                    "number": closure.get("number"),
                    "reason": closure.get("reason"),
                    "error": output,
                }
            )
    result["writes"]["succeeded"] = succeeded
    result["writes"]["failed"] = failures
    print(json.dumps(result, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
