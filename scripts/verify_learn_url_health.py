#!/usr/bin/env python3
"""verify_learn_url_health.py — fail CI on dead Microsoft Learn URLs.

Closes F-LEARN-URL-DEAD-LINKS-CI-GAP-01.

The Learn-URL monitor (`scripts/check_learn_urls.py`) probes every
Microsoft Learn URL referenced by the framework and writes per-URL
status to `data/monitor-state.json`. Today nothing fails CI when one
of those URLs starts returning 404/410/451 — drift sits silently in
the state file until a maintainer notices.

This verifier reads `data/monitor-state.json` and exits 1 if any
URL's `last_status` is in the dead-status set
{404, 410, 451}. 451 (Unavailable for Legal Reasons) is included
because it indicates a hard takedown that breaks the customer
journey just like a 404.

Soft-failures (5xx, timeouts, transient errors) are surfaced via
`statistics.last_run_errors` but do NOT fail this gate — they are
expected during transient Microsoft Learn outages and would produce
flaky CI.

Usage:
    python scripts/verify_learn_url_health.py
    python scripts/verify_learn_url_health.py --state-file data/monitor-state.json
    python scripts/verify_learn_url_health.py --max-print 50
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Ensure non-ASCII output (e.g. the "→" separator below) does not crash on
# consoles using a legacy code page such as Windows cp1252. CI runs on UTF-8
# Linux where this is a no-op, but local maintainer runs on Windows would
# otherwise raise UnicodeEncodeError while reporting a dead URL.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

DEAD_STATUSES: frozenset[int] = frozenset({404, 410, 451})

DEFAULT_STATE_FILE = Path("data/monitor-state.json")


def find_dead_urls(state: dict) -> list[dict]:
    """Return list of {url, status, section, topic, last_checked} for dead URLs.

    Tolerates both schema_version 1 (no `sources` wrapper) and 2 (current).
    """
    sources = state.get("sources")
    if isinstance(sources, dict):
        learn = sources.get("learn", {})
    else:
        # legacy schema: top-level urls
        learn = state
    urls = learn.get("urls", {})
    dead: list[dict] = []
    for url, entry in urls.items():
        if not isinstance(entry, dict):
            continue
        status = entry.get("last_status")
        if isinstance(status, int) and status in DEAD_STATUSES:
            dead.append({
                "url": url,
                "status": status,
                "section": entry.get("section", ""),
                "topic": entry.get("topic", ""),
                "last_checked": entry.get("last_checked", ""),
            })
    dead.sort(key=lambda d: (d["status"], d["url"]))
    return dead


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-file", default=str(DEFAULT_STATE_FILE),
                        help=f"Path to monitor state JSON (default: {DEFAULT_STATE_FILE})")
    parser.add_argument("--max-print", type=int, default=50,
                        help="Maximum number of dead URLs to print (default: 50)")
    args = parser.parse_args(argv)

    state_path = Path(args.state_file)
    if not state_path.is_file():
        print(f"ERROR: state file not found: {state_path}", file=sys.stderr)
        return 2

    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"ERROR: cannot parse {state_path}: {e}", file=sys.stderr)
        return 2

    dead = find_dead_urls(state)
    total = sum(1 for src in (state.get("sources") or {"learn": state}).values()
                if isinstance(src, dict)
                for _ in (src.get("urls") or {}).items())

    if not dead:
        print(f"OK: scanned {total} Microsoft Learn URLs, "
              f"none returning {sorted(DEAD_STATUSES)}.")
        return 0

    print(f"FAIL: {len(dead)} of {total} Microsoft Learn URLs returning a "
          f"dead-status code {sorted(DEAD_STATUSES)}:")
    shown = 0
    for entry in dead:
        if shown >= args.max_print:
            print(f"  ... {len(dead) - shown} more")
            break
        print(f"  [{entry['status']}] {entry['url']}")
        if entry["section"] or entry["topic"]:
            print(f"      ({entry['section']} → {entry['topic']})")
        shown += 1
    print()
    print("Investigate by re-running the Learn URL monitor and updating "
          "any moved/removed canonical references in docs/ accordingly:")
    print("  python scripts/check_learn_urls.py")
    return 1


if __name__ == "__main__":
    sys.exit(main())
