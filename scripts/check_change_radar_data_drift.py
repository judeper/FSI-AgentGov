#!/usr/bin/env python3
"""Detect drift in the Change Radar feed data and lint its customer-facing copy.

The Change Radar page consumes ``docs/javascripts/change-radar-data.json``,
which is generated from ``data/change-radar/items.json`` by
``scripts/gen_change_radar_data.py``. This checker enforces three invariants so
the published feed cannot silently diverge from its source or ship unsafe copy:

1. **Regeneration drift** -- regenerating from ``items.json`` must reproduce the
   committed data file exactly (ignoring only the volatile ``generatedAt``
   timestamp). If it does not, the committed file is stale; regenerate it in the
   SAME PR as the ``items.json`` change.
2. **Control-ID subset** -- every referenced control ID must exist in the
   79-control manifest. (Enforced by the generator's ``build()``; surfaced here.)
3. **FSI language** -- the feed's customer-facing strings (``title``,
   ``summary``, ``whatToReview`` and each control ``rationale``) live in JSON,
   which ``verify_language_rules.py`` does NOT scan (it only reads ``docs/**/*.md``).
   This check runs the same TIER 1 overclaim patterns against those JSON strings
   so banned phrases ("ensures compliance", "guarantees", ...) cannot ship via
   the feed data.

Run with ``--check`` in CI to fail on drift.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import gen_change_radar_data as gen  # noqa: E402
from verify_language_rules import TIER1_PATTERNS  # noqa: E402

REPO_ROOT = gen.REPO_ROOT
DATA_FILE = gen.OUTPUT
LINTED_STRING_FIELDS = ("title", "summary", "whatToReview")


def _strip_volatile(doc: dict) -> dict:
    """Return a copy of the feed doc without the volatile generatedAt field."""
    return {k: v for k, v in doc.items() if k != "generatedAt"}


def _lint_strings(doc: dict) -> list[str]:
    """Run TIER 1 overclaim patterns against the feed's customer-facing copy."""
    violations: list[str] = []
    for item in doc.get("items", []):
        item_id = item.get("id", "?")
        strings: list[tuple[str, str]] = [
            (field, str(item.get(field, ""))) for field in LINTED_STRING_FIELDS
        ]
        for ctrl in item.get("controls", []):
            strings.append((f"control {ctrl.get('id', '?')} rationale", str(ctrl.get("rationale", ""))))
        for where, text in strings:
            for pattern, label in TIER1_PATTERNS:
                if pattern.search(text):
                    violations.append(f"item {item_id} ({where}): prohibited phrase {label!r}")
    return violations


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit non-zero on drift (default behavior; flag kept for clarity).",
    )
    parser.parse_args(argv)

    # 1 + 2: regenerate from source and validate control IDs.
    try:
        expected_doc, errors = gen.build()
    except (FileNotFoundError, json.JSONDecodeError, ValueError) as exc:
        print(f"FAIL: {exc}")
        return 1
    if errors:
        print("FAIL: Change Radar items did not validate:")
        for err in errors:
            print(f"  - {err}")
        return 1

    if not DATA_FILE.exists():
        print(
            f"FAIL: {DATA_FILE.relative_to(REPO_ROOT)} does not exist. "
            "Run: python scripts/gen_change_radar_data.py"
        )
        return 1
    try:
        committed_doc = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"FAIL: {DATA_FILE.relative_to(REPO_ROOT)} is not valid JSON: {exc}")
        return 1

    drift = False
    if _strip_volatile(expected_doc) != _strip_volatile(committed_doc):
        drift = True
        print(
            f"DRIFT: {DATA_FILE.relative_to(REPO_ROOT)} is stale. Regenerate it from "
            "data/change-radar/items.json (python scripts/gen_change_radar_data.py) "
            "in the SAME PR as the items.json change."
        )

    # 3: FSI language on the customer-facing JSON copy.
    lint_violations = _lint_strings(committed_doc)
    if lint_violations:
        drift = True
        print("FAIL: prohibited FSI language in Change Radar feed copy:")
        for viol in lint_violations:
            print(f"  - {viol}")

    if drift:
        return 1

    print(
        f"OK: Change Radar data is regenerated, control IDs are in the manifest, "
        f"and feed copy passes FSI language rules ({committed_doc.get('count', 0)} item(s))."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
