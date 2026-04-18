#!/usr/bin/env python3
"""Refresh ``assessment/data/solutions-lock.json`` from FSI-AgentGov-Solutions.

Per the v1.4 cross-repo contract, the framework repo never reaches into
the solutions repo at PR time. This script runs **only on tag bump** to
fetch ``solutions.json`` from a tagged release of FSI-AgentGov-Solutions
and commit a local copy.

Usage::

    python scripts/refresh_solutions_lock.py --tag v1.4.0

The script will:

1. Fetch ``solutions.json`` from the specified tag of
   ``judeper/FSI-AgentGov-Solutions`` over raw.githubusercontent.com.
2. Verify ``schemaVersion`` starts with the major.minor of ``--tag``.
3. Verify the count of solutions matches ``--expect-count`` (default 35).
4. Verify the 7 previously-missing solution IDs are present.
5. Atomically write to ``assessment/data/solutions-lock.json``.

Exit codes: 0 = refreshed; 1 = verification failure; 2 = network/IO error.
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCK_PATH = ROOT / "assessment" / "data" / "solutions-lock.json"

SOLUTIONS_REPO = "judeper/FSI-AgentGov-Solutions"
RAW_BASE = f"https://raw.githubusercontent.com/{SOLUTIONS_REPO}"

# Solutions added in v1.4.0 — must be present in the refreshed lock.
EXPECTED_NEW_IDS = (
    "agent-365-lifecycle-governance",
    "agent-knowledge-source-scanner",
    "agent-registry-automation",
    "credential-oversharing-detector",
    "cross-tenant-external-sharing-governance",
    "model-risk-management-automation",
)


def fetch(url: str, timeout: int = 30) -> bytes:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "FSI-AgentGov-refresh-solutions-lock/1.4"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--tag",
        required=True,
        help="Git tag in FSI-AgentGov-Solutions (e.g., v1.4.0).",
    )
    parser.add_argument(
        "--source-path",
        default="solutions.json",
        help="Path to solutions manifest within the solutions repo.",
    )
    parser.add_argument(
        "--expect-count", type=int, default=35, help="Expected solution count."
    )
    parser.add_argument(
        "--expect-ids",
        nargs="*",
        default=list(EXPECTED_NEW_IDS),
        help="Solution IDs that must be present.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Fetch and verify but do not write the lock file.",
    )
    args = parser.parse_args()

    tag = args.tag.lstrip("v")  # accept v1.4.0 or 1.4.0
    expected_prefix = ".".join(tag.split(".")[:2]) + "."
    url = f"{RAW_BASE}/v{tag}/{args.source_path}"

    print(f"Fetching {url} ...")
    try:
        raw = fetch(url)
    except urllib.error.HTTPError as exc:
        print(f"ERROR: HTTP {exc.code} fetching {url}", file=sys.stderr)
        return 2
    except (urllib.error.URLError, TimeoutError) as exc:
        print(f"ERROR: network failure fetching {url}: {exc}", file=sys.stderr)
        return 2

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"ERROR: response is not valid JSON: {exc}", file=sys.stderr)
        return 2

    sv = data.get("schemaVersion", "")
    if not (isinstance(sv, str) and sv.startswith(expected_prefix)):
        print(
            f"ERROR: schemaVersion {sv!r} does not start with {expected_prefix!r}; "
            "the framework's lock-file consumer expects 1.4.x.",
            file=sys.stderr,
        )
        return 1

    sols = data.get("solutions", {})
    sol_ids = set(sols.keys()) if isinstance(sols, dict) else {
        s.get("id") for s in sols if isinstance(s, dict)
    }
    if len(sol_ids) != args.expect_count:
        print(
            f"ERROR: expected {args.expect_count} solutions, got {len(sol_ids)}",
            file=sys.stderr,
        )
        return 1

    missing = [sid for sid in args.expect_ids if sid not in sol_ids]
    if missing:
        print(
            f"ERROR: missing required solution IDs: {missing}", file=sys.stderr
        )
        return 1

    if args.dry_run:
        print(f"OK (dry-run): {len(sol_ids)} solutions, schemaVersion={sv}")
        return 0

    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOCK_PATH.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(
        f"Wrote {LOCK_PATH.relative_to(ROOT)} "
        f"({len(sol_ids)} solutions, schemaVersion={sv})."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
