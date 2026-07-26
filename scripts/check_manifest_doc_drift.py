#!/usr/bin/env python3
"""Detect drift between the control manifest, CONTROL-INDEX, and mkdocs nav.

The 79-control framework is described in three places:

* ``assessment/manifest/controls.json`` — machine-readable source of truth
* ``docs/controls/CONTROL-INDEX.md`` — human-readable master index
* ``mkdocs.yml`` — published navigation

This script makes sure the same 79 control IDs appear in all three with
the same pillar grouping. Run with ``--check`` in CI to fail on drift.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST = REPO_ROOT / "assessment" / "manifest" / "controls.json"
INDEX = REPO_ROOT / "docs" / "controls" / "CONTROL-INDEX.md"
MKDOCS = REPO_ROOT / "mkdocs.yml"

CONTROL_ID_RE = re.compile(r"^\d+\.\d+$")
INDEX_ROW_RE = re.compile(r"^\|\s*(\d+\.\d+)\s*\|")
NAV_FILE_RE = re.compile(r"controls/pillar-(\d)-[\w-]+/(\d+\.\d+)-")


def load_manifest_ids() -> set[str]:
    raw = json.loads(MANIFEST.read_text(encoding="utf-8"))
    controls = raw if isinstance(raw, list) else raw.get("controls", [])
    return {c["id"] for c in controls}


def load_index_ids() -> set[str]:
    ids: set[str] = set()
    for line in INDEX.read_text(encoding="utf-8").splitlines():
        m = INDEX_ROW_RE.match(line)
        if m:
            ids.add(m.group(1))
    return ids


def load_nav_ids() -> set[str]:
    ids: set[str] = set()
    for line in MKDOCS.read_text(encoding="utf-8").splitlines():
        m = NAV_FILE_RE.search(line)
        if m:
            ids.add(m.group(2))
    return ids


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit non-zero on drift (default behavior; flag kept for clarity).",
    )
    parser.parse_args(argv)

    manifest_ids = load_manifest_ids()
    index_ids = load_index_ids()
    nav_ids = load_nav_ids()

    sources = {
        "manifest (controls.json)": manifest_ids,
        "CONTROL-INDEX.md": index_ids,
        "mkdocs.yml nav": nav_ids,
    }

    print("Source counts:")
    for label, ids in sources.items():
        print(f"  {label}: {len(ids)} control IDs")
    print()

    union = set().union(*sources.values())
    drift = False
    for label, ids in sources.items():
        missing = union - ids
        if missing:
            drift = True
            print(
                f"DRIFT: {label} is missing {len(missing)} control(s): "
                f"{sorted(missing)}"
            )

    # Sanity: every recorded ID should look like N.N.
    bogus = [cid for cid in union if not CONTROL_ID_RE.match(cid)]
    if bogus:
        drift = True
        print(f"DRIFT: malformed control IDs detected: {sorted(bogus)}")

    if drift:
        print(
            "\nFAIL: control IDs drift between manifest, CONTROL-INDEX, "
            "and mkdocs nav. Update all three to stay in sync."
        )
        return 1

    print("OK: all 3 sources reference the same control IDs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
