#!/usr/bin/env python3
"""Advance deferred Learn Monitor baselines after autodoc issues close.

A pending Learn change is only "terminal" (safe to advance + delete) when an ``autodoc``
issue that was closed **as COMPLETED** carries the change's EXACT identity. Identity is the
``(source url, content hash)`` pair, matched verbatim against the pending blob's
``(url, content_hash)``.

This deliberately does NOT use GitHub's ``{url} in:body`` search to find the matching issue.
That search is tokenized (it strips the scheme and splits on ``/ - .``), so a short watchlist
URL's tokens can be a subset of an UNRELATED closed issue's body — which previously advanced and
``unlink()``-ed the wrong pending blob, silently losing a still-open URL's real change.
"""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

import autodoc_issue_identity
from autodoc_defer import PENDING_RELATIVE_DIR, load_pending
from monitoring_shared import get_source_state, load_state, save_state_atomic, set_source_state

SOURCE_KEY = "learn"
DEFAULT_STATE_PATH = Path("data") / "monitor-state.json"
DEFAULT_PENDING_DIR = PENDING_RELATIVE_DIR

# An issue is only terminal when it was closed as COMPLETED. A human closing an escalation as
# "not planned"/"duplicate" must NOT advance the baseline (that would dedupe a change whose doc
# edit was never shipped).
COMPLETED_STATE_REASON = "COMPLETED"

# A terminal identity is the exact (url, content_hash) pair that uniquely names one change.
Identity = tuple[str, str]


def parse_issue_identity(body: str | None) -> Identity | None:
    """Return the exact ``(url, content_hash)`` identity embedded in an autodoc issue body.

    Two issue-body shapes carry identity: the escalation body (plaintext ``Source:`` +
    ``Content-Hash:`` lines, emitted by ``_escalate``) and the autodraft tracking-issue body
    (identity only inside the embedded ``json`` contract via ``source_url`` / ``content_hash``).
    Both are recognized; otherwise the issue cannot be matched to a specific pending change and
    ``None`` is returned (the blob is left untouched).
    """
    return autodoc_issue_identity.parse_issue_body_identity(body).identity


def _normalize_state_reason(value: Any) -> str:
    """Normalize gh's ``stateReason`` (e.g. ``COMPLETED``/``completed``/None) to upper-case."""
    return autodoc_issue_identity.normalize_state_reason(value)


def terminal_identities_from_issues(closed_issues: list[dict[str, Any]]) -> set[Identity]:
    """Return the set of exact change identities from issues closed as COMPLETED.

    Each issue is a ``gh issue list --json number,stateReason,body`` record. Only issues whose
    ``stateReason`` is ``COMPLETED`` and that carry both a ``Source:`` and ``Content-Hash:`` line
    contribute an identity. Tokenized URL search is never used.
    """
    identities: set[Identity] = set()
    for issue in closed_issues:
        record = autodoc_issue_identity.parse_issue_record(issue)
        if _normalize_state_reason(record.state_reason) != COMPLETED_STATE_REASON:
            continue
        identity = record.identity
        if identity is not None:
            identities.add(identity)
    return identities


def read_closed_issues(path: str | Path) -> list[dict[str, Any]]:
    """Read a ``gh issue list --json number,stateReason,body`` JSON array from disk."""
    issues_path = Path(path)
    if not issues_path.exists():
        return []
    data = json.loads(issues_path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"Closed-issues file must be a JSON array: {issues_path}")
    return data


def read_terminal_identities(path: str | Path) -> set[Identity]:
    """Read terminal identities from a JSON array of ``{"url", "content_hash"}`` objects."""
    identities_path = Path(path)
    if not identities_path.exists():
        return set()
    data = json.loads(identities_path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"Terminal-identities file must be a JSON array: {identities_path}")
    identities: set[Identity] = set()
    for entry in data:
        if not isinstance(entry, dict):
            raise ValueError(f"Terminal-identity entry must be an object: {entry!r}")
        url = entry.get("url")
        content_hash = entry.get("content_hash")
        if isinstance(url, str) and url and isinstance(content_hash, str) and content_hash:
            identities.add((url, content_hash))
    return identities


def _validated_pending(path: Path) -> dict[str, Any]:
    pending = load_pending(path)
    if pending is None:
        raise ValueError(f"Pending blob disappeared before load: {path}")
    if pending.get("schema_version") != 1 or pending.get("source") != SOURCE_KEY:
        raise ValueError(f"Unsupported pending blob schema: {path}")
    for key in ("url", "content_hash", "normalized_content", "detected_at"):
        if not isinstance(pending.get(key), str) or not pending[key]:
            raise ValueError(f"Pending blob missing string field {key!r}: {path}")
    return pending


def _pending_identity(pending: dict[str, Any]) -> Identity:
    return (pending["url"], pending["content_hash"])


def load_pending_records(pending_dir: str | Path) -> list[tuple[Path, dict[str, Any]]]:
    """Load pending records in deterministic path order."""
    pending_root = Path(pending_dir)
    if not pending_root.exists():
        return []
    return [(path, _validated_pending(path)) for path in sorted(pending_root.glob("*.json"))]


def advance_source_state(
    source_state: dict[str, Any],
    pending_records: list[dict[str, Any]],
    terminal_identities: set[Identity],
) -> tuple[dict[str, Any], list[str], list[str]]:
    """Return a source state with terminal pending baselines applied.

    Only pending records whose EXACT ``(url, content_hash)`` identity is terminal advance their
    baseline. Two changes to the same URL are independent: closing one does not advance the other.
    """
    advanced_state = copy.deepcopy(source_state)
    urls = advanced_state.setdefault("urls", {})
    advanced_urls: list[str] = []
    missing_urls: list[str] = []

    # Apply in detected_at order (ISO-8601, lexicographically chronological) so that when two
    # terminal changes to the SAME url advance in one run, the NEWEST content wins the baseline
    # (last write); path/hash order would non-deterministically land on the older content.
    for pending in sorted(pending_records, key=lambda p: p["detected_at"]):
        if _pending_identity(pending) not in terminal_identities:
            continue
        url = pending["url"]
        if url not in urls:
            missing_urls.append(url)
            continue
        urls[url]["content_hash"] = pending["content_hash"]
        urls[url]["normalized_content"] = pending["normalized_content"]
        urls[url]["last_changed"] = pending["detected_at"]
        advanced_urls.append(url)

    return advanced_state, advanced_urls, missing_urls


def advance_pending_baselines(
    state_path: str | Path,
    pending_dir: str | Path,
    terminal_identities: set[Identity],
) -> dict[str, list[str]]:
    """Advance monitor-state baselines for terminal pending changes and remove their blobs."""
    pending_records_with_paths = load_pending_records(pending_dir)
    pending_records = [record for _path, record in pending_records_with_paths]
    state = load_state(state_path)
    source_state = get_source_state(state, SOURCE_KEY)
    advanced_state, advanced_urls, missing_urls = advance_source_state(
        source_state, pending_records, terminal_identities
    )

    if advanced_urls:
        set_source_state(state, SOURCE_KEY, advanced_state)
        save_state_atomic(state, state_path)

    # Delete ONLY the blobs whose exact identity is terminal (advanced, or terminal-but-missing
    # from state). A non-terminal blob for the same URL must survive.
    for path, pending in pending_records_with_paths:
        if _pending_identity(pending) in terminal_identities:
            path.unlink()

    non_terminal_urls = [
        record["url"] for record in pending_records if _pending_identity(record) not in terminal_identities
    ]
    return {
        "advanced": advanced_urls,
        "missing": missing_urls,
        "non_terminal": non_terminal_urls,
    }


def _load_terminal_identities(args: argparse.Namespace) -> set[Identity]:
    if args.closed_issues:
        closed_issues = read_closed_issues(args.closed_issues)
        return terminal_identities_from_issues(closed_issues)
    return read_terminal_identities(args.terminal_identities)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", default=str(DEFAULT_STATE_PATH), help="Path to data/monitor-state.json")
    parser.add_argument("--pending-dir", default=str(DEFAULT_PENDING_DIR), help="Path to data/monitor-pending/learn")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument(
        "--closed-issues",
        help="Path to a `gh issue list --json number,stateReason,body` JSON array of closed autodoc issues",
    )
    source.add_argument(
        "--terminal-identities",
        help="Path to a JSON array of {url, content_hash} objects naming terminal pending changes",
    )
    args = parser.parse_args(argv)

    terminal_identities = _load_terminal_identities(args)
    result = advance_pending_baselines(args.state, args.pending_dir, terminal_identities)
    print(
        "Autodoc advance summary: "
        f"advanced={len(result['advanced'])} "
        f"non_terminal={len(result['non_terminal'])} "
        f"missing={len(result['missing'])}"
    )
    for url in result["advanced"]:
        print(f"Advanced baseline: {url}")
    for url in result["missing"]:
        print(f"Skipped missing state URL: {url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
