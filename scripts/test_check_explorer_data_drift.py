"""Tests for the Control Explorer field-value drift guard.

Issue #322 (related weakness): ``check_explorer_data_drift`` compared control
IDs and counts but never field *values*, so stale ``effortLevel`` and
``automation`` entries for controls 1.4, 1.11 and 1.15 survived CI until an
unrelated regeneration exposed them.

These tests pin the value-comparison contract and prove the guard shares the
generator's mapping tables instead of re-declaring them.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import check_explorer_data_drift as guard  # noqa: E402
import gen_explorer_data as generator  # noqa: E402


def _manifest_control(**overrides):
    control = {
        "id": "1.1",
        "name": "Control 1.1: Example",
        "pillar": 1,
        "pillar_name": "Security",
        "controlDocUrl": "/controls/pillar-1-security/1.1-example/",
        "zonesApplicable": [2, 1],
        "roles": ["Power Platform Admin (primary)", "Role", "Entra Global Admin"],
        "automation": "partial",
        "solutions": ["beta-solution", "alpha-solution"],
    }
    control.update(overrides)
    return control


def test_expected_values_match_generator_output():
    """The guard must reproduce exactly what gen_explorer_data.py emits."""
    control = _manifest_control()
    expected = guard.expected_values(control)

    assert expected["title"] == "Control 1.1: Example"
    assert expected["pillar"] == 1
    assert expected["pillarName"] == "Security"
    assert expected["url"] == "controls/pillar-1-security/1.1-example/"
    assert expected["zones"] == [1, 2]
    assert expected["roles"] == ["Entra Global Admin", "Power Platform Admin"]
    assert expected["primaryOwner"] == "Power Platform Admin"
    assert expected["automation"] == "Partial"
    assert expected["effortLevel"] == "Medium effort"
    assert expected["solutions"] == ["alpha-solution", "beta-solution"]


def test_guard_shares_generator_mapping_tables():
    """No re-declared copies -- the tables are imported, not duplicated."""
    assert guard.AUTOMATION_LABELS is generator.AUTOMATION_LABELS
    assert guard.EFFORT_MAP is generator.EFFORT_MAP
    assert guard.ROLE_ARTIFACTS is generator.ROLE_ARTIFACTS


def test_role_artifacts_are_dropped_and_parentheticals_stripped():
    control = _manifest_control(roles=["Reviewer", "Purview Compliance Admin (owner)"])
    expected = guard.expected_values(control)
    assert expected["roles"] == ["Purview Compliance Admin"]


def test_unknown_automation_falls_back_to_unspecified():
    control = _manifest_control(automation=None)
    expected = guard.expected_values(control)
    assert expected["automation"] == "unspecified"
    assert expected["effortLevel"] == ""


def test_check_field_values_flags_stale_effort_level():
    """The exact 1.4 / 1.11 / 1.15 failure mode: right ID, wrong value."""
    control = _manifest_control(automation="full")
    explorer = guard.expected_values(control) | {"id": "1.1"}
    explorer["effortLevel"] = "Higher effort"  # stale, pre-regeneration value

    problems = guard.check_field_values({"1.1": control}, {"1.1": explorer}, ["1.1"])
    assert len(problems) == 1
    assert "effortLevel mismatch for control 1.1" in problems[0]


def test_check_field_values_flags_stale_automation():
    control = _manifest_control(automation="manual")
    explorer = guard.expected_values(control) | {"id": "1.1"}
    explorer["automation"] = "Automatable"

    problems = guard.check_field_values({"1.1": control}, {"1.1": explorer}, ["1.1"])
    assert any("automation mismatch" in p for p in problems)


def test_check_field_values_flags_missing_solution_association():
    """Manifest/explorer solution drift -- the #322 reconciliation surface."""
    control = _manifest_control()
    explorer = guard.expected_values(control) | {"id": "1.1"}
    explorer["solutions"] = ["alpha-solution"]

    problems = guard.check_field_values({"1.1": control}, {"1.1": explorer}, ["1.1"])
    assert any("solutions mismatch" in p for p in problems)


def test_check_field_values_clean_when_aligned():
    control = _manifest_control()
    explorer = guard.expected_values(control) | {"id": "1.1"}
    assert guard.check_field_values({"1.1": control}, {"1.1": explorer}, ["1.1"]) == []


def test_every_value_field_is_actually_compared():
    """Guard against a field being listed in VALUE_FIELDS but never populated."""
    control = _manifest_control()
    expected = guard.expected_values(control)
    assert set(guard.VALUE_FIELDS) <= set(expected)


def test_committed_explorer_data_has_no_value_drift():
    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "check_explorer_data_drift.py"), "--check"],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_committed_explorer_data_matches_manifest_solutions():
    """End-to-end: the reconciled manifest is reflected in the published data."""
    manifest = json.loads(guard.MANIFEST.read_text(encoding="utf-8"))
    explorer = json.loads(guard.EXPLORER_DATA.read_text(encoding="utf-8"))["controls"]
    explorer_by_id = {c["id"]: c for c in explorer}
    for control in manifest:
        assert explorer_by_id[control["id"]]["solutions"] == sorted(
            control.get("solutions") or []
        ), control["id"]
