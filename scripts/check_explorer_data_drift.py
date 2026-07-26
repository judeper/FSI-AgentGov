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
import sys
from collections import Counter
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST = REPO_ROOT / "assessment" / "manifest" / "controls.json"
EXPLORER_DATA = REPO_ROOT / "docs" / "javascripts" / "control-explorer-data.json"
EXPECTED_CONTROL_COUNT = 79
CONTROL_ID_RE = re.compile(r"^\d+\.\d+$")

# Share the generator's mapping tables so this guard validates against the
# same source of truth rather than a drifting copy (issue #322).
sys.path.insert(0, str(Path(__file__).resolve().parent))
from gen_explorer_data import (  # noqa: E402
    AUTOMATION_LABELS,
    EFFORT_MAP,
    ROLE_ARTIFACTS,
    clean_role,
)

# Explorer fields derived deterministically from the manifest alone. Fields
# that need the control markdown (objective, workload, governanceLevels) or
# the playbook tree (playbooks, primaryPlaybook) are out of scope here --
# mkdocs-strict and verify_controls.py cover those surfaces.
#
# Before issue #322 this checker compared only control IDs and counts, so a
# stale effortLevel or automation value (controls 1.4, 1.11, 1.15) survived CI.
VALUE_FIELDS = (
    "title",
    "pillar",
    "pillarName",
    "url",
    "zones",
    "roles",
    "automation",
    "effortLevel",
    "solutions",
    "primaryOwner",
)


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


def regulatory_set(control: dict[str, Any], key: str) -> set[str]:
    raw = control.get(key, [])
    if not isinstance(raw, list):
        return set()
    return {str(value).strip() for value in raw if str(value).strip()}


def duplicate_ids(ids: list[str]) -> list[str]:
    counts = Counter(ids)
    return sorted(cid for cid, count in counts.items() if count > 1)


def cleaned_roles(control: dict[str, Any]) -> list[str]:
    """Roles as the generator emits them: parentheticals stripped, artifacts dropped."""
    roles: list[str] = []
    for raw in control.get("roles") or []:
        role = clean_role(str(raw))
        if role and role not in ROLE_ARTIFACTS and role not in roles:
            roles.append(role)
    return roles


def expected_values(control: dict[str, Any]) -> dict[str, Any]:
    """Recompute every manifest-derived Explorer field for one control."""
    automation_raw = control.get("automation")
    roles = cleaned_roles(control)
    return {
        "title": control.get("name") or control.get("title") or str(control.get("id")),
        "pillar": control.get("pillar"),
        "pillarName": control.get("pillar_name") or "",
        "url": (control.get("controlDocUrl") or "").lstrip("/"),
        "zones": sorted(control.get("zonesApplicable") or []),
        "roles": sorted(roles),
        "automation": AUTOMATION_LABELS.get(automation_raw, "unspecified"),
        "effortLevel": EFFORT_MAP.get(automation_raw or "", ""),
        "solutions": sorted(control.get("solutions") or []),
        "primaryOwner": roles[0] if roles else "",
    }


def check_field_values(
    manifest_by_id: dict[str, dict[str, Any]],
    explorer_by_id: dict[str, dict[str, Any]],
    shared_ids: list[str],
) -> list[str]:
    """Compare manifest-derived field values, not just IDs and counts."""
    problems: list[str] = []
    for cid in shared_ids:
        expected = expected_values(manifest_by_id[cid])
        actual = explorer_by_id[cid]
        for field in VALUE_FIELDS:
            if actual.get(field) != expected[field]:
                problems.append(
                    f"DRIFT: {field} mismatch for control {cid}: "
                    f"manifest-derived={expected[field]!r} "
                    f"explorer={actual.get(field)!r}"
                )
    return problems


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
    manifest_controls, _ = load_controls(MANIFEST)
    explorer_controls, _ = load_controls(EXPLORER_DATA)
    manifest_by_id = {str(control.get("id")): control for control in manifest_controls}
    explorer_by_id = {str(control.get("id")): control for control in explorer_controls}
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

    promoted_2507_manifest = sorted(
        cid
        for cid, control in manifest_by_id.items()
        if "FINRA-25-07" in regulatory_set(control, "regulatory")
    )
    if promoted_2507_manifest:
        drift = True
        print(
            "DRIFT: manifest contains FINRA-25-07 in primary regulatory mappings "
            f"(must remain pending/nonbinding only): {promoted_2507_manifest}"
        )

    promoted_2507_explorer = sorted(
        cid
        for cid, control in explorer_by_id.items()
        if "FINRA-25-07" in regulatory_set(control, "regulations")
    )
    if promoted_2507_explorer:
        drift = True
        print(
            "DRIFT: Control Explorer data still publishes FINRA-25-07 as a regulation "
            f"facet for control(s): {promoted_2507_explorer}"
        )

    for cid in sorted(manifest_set & explorer_set):
        manifest_regs = regulatory_set(manifest_by_id[cid], "regulatory")
        if not manifest_regs:
            # Controls with empty authoritative mappings may derive fallback facets
            # from markdown headers. Skip parity checks for those controls.
            continue
        explorer_regs = regulatory_set(explorer_by_id[cid], "regulations")
        if manifest_regs != explorer_regs:
            drift = True
            print(
                f"DRIFT: regulation facet mismatch for control {cid}: "
                f"manifest={sorted(manifest_regs)} explorer={sorted(explorer_regs)}"
            )

    value_problems = check_field_values(
        manifest_by_id, explorer_by_id, sorted(manifest_set & explorer_set)
    )
    if value_problems:
        drift = True
        for problem in value_problems:
            print(problem)

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
