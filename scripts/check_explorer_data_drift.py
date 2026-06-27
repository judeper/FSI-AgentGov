#!/usr/bin/env python3
"""Detect drift between the control manifest and Control Explorer data.

The docs-site Control Explorer reads ``docs/javascripts/control-explorer-data.json``.
That data must stay aligned with the canonical 79-control manifest in
``assessment/manifest/controls.json`` so search facets and recommendations do
not publish stale or missing controls.

Run with ``--check`` in CI to fail on drift.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST = REPO_ROOT / "assessment" / "manifest" / "controls.json"
EXPLORER_DATA = REPO_ROOT / "docs" / "javascripts" / "control-explorer-data.json"
EXPECTED_CONTROL_COUNT = 79
CONTROL_ID_RE = re.compile(r"^\d+\.\d+$")


def rel(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def read_json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"expected file not found: {rel(path)}")
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def load_controls(path: Path) -> tuple[list[dict[str, Any]], int | None]:
    raw = read_json(path)
    declared_count: int | None = None

    if isinstance(raw, list):
        controls = raw
    elif isinstance(raw, dict):
        controls = raw.get("controls", [])
        if isinstance(raw.get("count"), int):
            declared_count = raw["count"]
    else:
        raise ValueError(f"{rel(path)} must be a JSON list or object with a 'controls' list")

    if not isinstance(controls, list):
        raise ValueError(f"{rel(path)} field 'controls' must be a list")
    if not all(isinstance(control, dict) for control in controls):
        raise ValueError(f"{rel(path)} controls must be JSON objects")

    return controls, declared_count


def ids_from_controls(path: Path) -> tuple[list[str], int | None]:
    controls, declared_count = load_controls(path)
    ids: list[str] = []
    for index, control in enumerate(controls, 1):
        cid = control.get("id")
        if cid is None:
            raise ValueError(f"{rel(path)} control #{index} is missing required field 'id'")
        ids.append(str(cid))
    return ids, declared_count


def duplicate_ids(ids: list[str]) -> list[str]:
    counts = Counter(ids)
    return sorted(cid for cid, count in counts.items() if count > 1)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit non-zero on drift (default behavior; flag kept for clarity).",
    )
    parser.parse_args(argv)

    try:
        manifest_ids, manifest_declared_count = ids_from_controls(MANIFEST)
        explorer_ids, explorer_declared_count = ids_from_controls(EXPLORER_DATA)
    except (FileNotFoundError, json.JSONDecodeError, ValueError) as exc:
        print(f"FAIL: {exc}")
        return 1

    manifest_set = set(manifest_ids)
    explorer_set = set(explorer_ids)
    sources = {
        "manifest (controls.json)": manifest_ids,
        "Control Explorer data": explorer_ids,
    }

    print("Source counts:")
    for label, ids in sources.items():
        print(f"  {label}: {len(ids)} control IDs ({len(set(ids))} unique)")
    if manifest_declared_count is not None:
        print(f"  manifest declared count: {manifest_declared_count}")
    if explorer_declared_count is not None:
        print(f"  Control Explorer declared count: {explorer_declared_count}")
    print(f"  expected framework count: {EXPECTED_CONTROL_COUNT}")
    print()

    drift = False

    count_checks = [
        ("manifest actual", len(manifest_ids)),
        ("manifest unique", len(manifest_set)),
        ("Control Explorer actual", len(explorer_ids)),
        ("Control Explorer unique", len(explorer_set)),
    ]
    if manifest_declared_count is not None:
        count_checks.append(("manifest declared", manifest_declared_count))
    if explorer_declared_count is not None:
        count_checks.append(("Control Explorer declared", explorer_declared_count))

    for label, count in count_checks:
        if count != EXPECTED_CONTROL_COUNT:
            drift = True
            print(f"DRIFT: {label} count is {count}; expected {EXPECTED_CONTROL_COUNT}.")

    for label, ids in sources.items():
        duplicates = duplicate_ids(ids)
        if duplicates:
            drift = True
            print(f"DRIFT: {label} contains duplicate control ID(s): {duplicates}")

    missing_from_explorer = manifest_set - explorer_set
    extra_in_explorer = explorer_set - manifest_set
    if missing_from_explorer:
        drift = True
        print(
            f"DRIFT: Control Explorer data is missing {len(missing_from_explorer)} "
            f"manifest control(s): {sorted(missing_from_explorer)}"
        )
    if extra_in_explorer:
        drift = True
        print(
            f"DRIFT: Control Explorer data has {len(extra_in_explorer)} control(s) "
            f"not in manifest: {sorted(extra_in_explorer)}"
        )

    malformed = sorted(cid for cid in manifest_set | explorer_set if not CONTROL_ID_RE.match(cid))
    if malformed:
        drift = True
        print(f"DRIFT: malformed control IDs detected: {malformed}")

    if drift:
        print(
            "\nFAIL: Control Explorer data drifts from assessment/manifest/controls.json. "
            "Regenerate docs/javascripts/control-explorer-data.json from the manifest."
        )
        return 1

    print("OK: Control Explorer data is in sync with the 79-control manifest.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
