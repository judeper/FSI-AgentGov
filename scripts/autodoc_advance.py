#!/usr/bin/env python3
"""Advance deferred Learn Monitor baselines after autodoc issues close."""

from __future__ import annotations

import argparse
import copy
from pathlib import Path
from typing import Any

from autodoc_defer import PENDING_RELATIVE_DIR, load_pending
from monitoring_shared import get_source_state, load_state, save_state_atomic, set_source_state

SOURCE_KEY = "learn"
DEFAULT_STATE_PATH = Path("data") / "monitor-state.json"
DEFAULT_PENDING_DIR = PENDING_RELATIVE_DIR


def read_terminal_urls(path: str | Path) -> set[str]:
    """Read a newline-delimited terminal URL file."""
    terminal_path = Path(path)
    if not terminal_path.exists():
        return set()
    return {line.strip() for line in terminal_path.read_text(encoding="utf-8").splitlines() if line.strip()}


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


def load_pending_records(pending_dir: str | Path) -> list[tuple[Path, dict[str, Any]]]:
    """Load pending records in deterministic path order."""
    pending_root = Path(pending_dir)
    if not pending_root.exists():
        return []
    return [(path, _validated_pending(path)) for path in sorted(pending_root.glob("*.json"))]


def advance_source_state(
    source_state: dict[str, Any],
    pending_records: list[dict[str, Any]],
    terminal_urls: set[str],
) -> tuple[dict[str, Any], list[str], list[str]]:
    """Return a source state with terminal pending baselines applied."""
    advanced_state = copy.deepcopy(source_state)
    urls = advanced_state.setdefault("urls", {})
    advanced_urls: list[str] = []
    missing_urls: list[str] = []

    for pending in pending_records:
        url = pending["url"]
        if url not in terminal_urls:
            continue
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
    terminal_urls: set[str],
) -> dict[str, list[str]]:
    """Advance monitor-state baselines for terminal pending URLs and remove their blobs."""
    pending_records_with_paths = load_pending_records(pending_dir)
    pending_records = [record for _path, record in pending_records_with_paths]
    state = load_state(state_path)
    source_state = get_source_state(state, SOURCE_KEY)
    advanced_state, advanced_urls, missing_urls = advance_source_state(source_state, pending_records, terminal_urls)

    if advanced_urls:
        set_source_state(state, SOURCE_KEY, advanced_state)
        save_state_atomic(state, state_path)

    consumed_urls = set(advanced_urls) | set(missing_urls)
    if consumed_urls:
        for path, pending in pending_records_with_paths:
            if pending["url"] in consumed_urls:
                path.unlink()

    non_terminal_urls = [record["url"] for record in pending_records if record["url"] not in terminal_urls]
    return {
        "advanced": advanced_urls,
        "missing": missing_urls,
        "non_terminal": non_terminal_urls,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", default=str(DEFAULT_STATE_PATH), help="Path to data/monitor-state.json")
    parser.add_argument("--pending-dir", default=str(DEFAULT_PENDING_DIR), help="Path to data/monitor-pending/learn")
    parser.add_argument("--terminal-urls", required=True, help="Newline-delimited file of closed-issue source URLs")
    args = parser.parse_args(argv)

    terminal_urls = read_terminal_urls(args.terminal_urls)
    result = advance_pending_baselines(args.state, args.pending_dir, terminal_urls)
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
