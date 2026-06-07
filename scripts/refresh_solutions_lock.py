#!/usr/bin/env python3
"""Refresh ``assessment/data/solutions-lock.json`` from FSI-AgentGov-Solutions.

Per the v1.4+ cross-repo contract, the framework repo never reaches
into the solutions repo at PR time. This script runs **only on tag
bump** to fetch ``solutions.json`` from a tagged release of
FSI-AgentGov-Solutions and commit a local copy.

Usage::

    python scripts/refresh_solutions_lock.py --tag v1.4.0
    python scripts/refresh_solutions_lock.py --tag v1.5.0

The script will:

1. Fetch ``solutions.json`` from the specified tag of
   ``judeper/FSI-AgentGov-Solutions`` over raw.githubusercontent.com.
2. Verify ``schemaVersion`` starts with the major.minor of ``--tag``.
3. Verify the canonical ``counts`` block exists and matches the per-solution
   ``status`` rollup.
4. Verify the total count matches ``--expect-count`` (default 36).
5. Verify key solution IDs are present.
6. Atomically write to ``assessment/data/solutions-lock.json``.

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

# Key v1.4+ solution IDs — must be present in the refreshed lock.
EXPECTED_NEW_IDS = (
    "agent-365-lifecycle-governance",
    "agent-knowledge-source-scanner",
    "agent-registry-automation",
    "credential-oversharing-detector",
    "cross-tenant-external-sharing-governance",
    "model-risk-management-automation",
)


def fetch(url: str, timeout: int = 30) -> bytes:
    if not url.lower().startswith("https://"):
        raise ValueError(f"refusing to fetch non-HTTPS URL: {url!r}")
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "FSI-AgentGov-refresh-solutions-lock/1.4"},
    )
    # https scheme is enforced by the guard above; urlopen is safe here.
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # nosec B310
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
        "--expect-count", type=int, default=36, help="Expected solution count."
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
    parser.add_argument(
        "--accept-schema",
        action="append",
        default=None,
        help=(
            "Schema-version prefix the lock-file consumer accepts (e.g., '1.5.'). "
            "May be repeated. When set, overrides the default check that the "
            "manifest's schemaVersion matches the major.minor of --tag. Use this "
            "when a release tag (e.g. a feature wave) does not bump the manifest "
            "schemaVersion. The framework's lock-file consumer currently accepts "
            "1.4.x and 1.5.x."
        ),
    )
    args = parser.parse_args()

    tag = args.tag.lstrip("v")  # accept v1.4.0 or 1.4.0
    if args.accept_schema:
        accepted_prefixes = tuple(args.accept_schema)
    else:
        accepted_prefixes = (".".join(tag.split(".")[:2]) + ".",)
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
    if not (isinstance(sv, str) and any(sv.startswith(p) for p in accepted_prefixes)):
        joined = " or ".join(repr(p) for p in accepted_prefixes)
        print(
            f"ERROR: schemaVersion {sv!r} does not start with {joined}; "
            "the framework's lock-file consumer expects 1.4.x or 1.5.x. "
            "If this tag intentionally ships an unchanged schemaVersion, "
            "re-run with --accept-schema '<prefix>.' (may be repeated).",
            file=sys.stderr,
        )
        return 1

    counts = data.get("counts")
    if not isinstance(counts, dict) or any(
        not isinstance(counts.get(key), int) for key in ("total", "live", "preview")
    ):
        print(
            "ERROR: solutions.json is missing the canonical counts block "
            "(integer total/live/preview keys required)",
            file=sys.stderr,
        )
        return 1

    sols = data.get("solutions", {})
    if isinstance(sols, dict):
        sol_ids = set(sols.keys())
        items = [body for body in sols.values() if isinstance(body, dict)]
    else:
        items = [s for s in sols if isinstance(s, dict)]
        sol_ids = {s.get("id") for s in items if s.get("id")}

    derived_counts = {"total": len(sol_ids), "live": 0, "preview": 0}
    for item in items:
        status = item.get("status")
        if status in ("live", "preview"):
            derived_counts[status] += 1

    if counts != derived_counts:
        print(
            f"ERROR: counts block {counts} does not match derived status rollup {derived_counts}",
            file=sys.stderr,
        )
        return 1

    if counts["total"] != args.expect_count:
        print(
            f"ERROR: expected counts.total={args.expect_count}, got {counts['total']}",
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
        print(
            "OK (dry-run): "
            f"schemaVersion={sv}, counts={counts}, totalSolutions={len(sol_ids)}"
        )
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
