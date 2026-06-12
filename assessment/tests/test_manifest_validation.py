"""Tests for ``scripts/validate_manifest.py`` and the harvested manifest.

These tests guard the v1.4 manifest contract:

* All 79 controls present and enriched with the v1.4 fields.
* Validator passes in ``--allow-todo`` mode against the committed manifest.
* Validator catches structural problems (bad slug, missing key, bad URL,
  unknown priority) when applied to mutated copies.
"""
from __future__ import annotations

import copy
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST = REPO_ROOT / "assessment" / "manifest" / "controls.json"
VALIDATOR = REPO_ROOT / "scripts" / "validate_manifest.py"


def _run(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def test_manifest_validates_in_allow_todo_mode():
    """The shipped manifest must pass with --allow-todo."""
    result = _run(["--allow-todo", "--quiet"])
    assert result.returncode == 0, (
        f"Validator failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    )


def test_manifest_has_79_controls():
    controls = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert len(controls) == 79
    ids = [c["id"] for c in controls]
    assert len(set(ids)) == 79, "duplicate control ids"


def test_every_control_has_v14_keys():
    controls = json.loads(MANIFEST.read_text(encoding="utf-8"))
    required = {
        "name",
        "zonesApplicable",
        "roles",
        "regulatory",
        "priority",
        "yesBar",
        "partialBar",
        "noBar",
        "verifyIn",
        "verifyPowerShell",
        "evidenceExpected",
        "controlDocUrl",
        "portalPlaybookUrl",
        "collectorField",
        "sectorYesBar",
        "facilitatorNotes",
        "solutions",
    }
    for ctrl in controls:
        missing = required - set(ctrl.keys())
        assert not missing, f"control {ctrl['id']} missing v1.4 keys: {sorted(missing)}"


def test_solutions_is_string_array():
    """Per the v1.4 cross-repo contract, solutions[] holds folder-name IDs."""
    controls = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for ctrl in controls:
        sols = ctrl.get("solutions", [])
        assert isinstance(sols, list), ctrl["id"]
        for s in sols:
            assert isinstance(s, str), f"{ctrl['id']}: solutions entry not a string"


def test_zones_applicable_subset_of_123():
    controls = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for ctrl in controls:
        z = ctrl["zonesApplicable"]
        assert z and all(v in (1, 2, 3) for v in z), ctrl["id"]


def test_control_doc_url_starts_with_slash():
    controls = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for ctrl in controls:
        assert ctrl["controlDocUrl"].startswith("/"), ctrl["id"]
        assert ctrl["portalPlaybookUrl"].startswith("/"), ctrl["id"]


def test_capability_driver_tags_provide_rollup_signal():
    """Driver tags must stay broad enough to produce a useful rollup signal."""
    controls = json.loads(MANIFEST.read_text(encoding="utf-8"))
    counts = Counter(driver for ctrl in controls for driver in ctrl.get("applicable_drivers", []))

    assert counts["ai_governance"] < len(controls), (
        "ai_governance should not blanket every control or the driver rollup "
        "collapses into the overall maturity score"
    )

    for driver in (
        "ai_strategy",
        "business_strategy",
        "technology_data",
        "organization_culture",
    ):
        assert counts[driver] >= 5, (
            f"{driver} should tag enough controls to produce a meaningful rollup"
        )


# ---------------------------------------------------------------------------
# Negative tests — write a mutated manifest and verify the validator catches it
# ---------------------------------------------------------------------------


@pytest.fixture()
def tmp_manifest(tmp_path):
    """Return a (path, controls) tuple — caller mutates ``controls`` then dumps."""
    controls = json.loads(MANIFEST.read_text(encoding="utf-8"))
    target = tmp_path / "controls.json"

    def write(mutated):
        target.write_text(json.dumps(mutated, indent=2), encoding="utf-8")
        return target

    return controls, write


def test_validator_rejects_bad_solution_slug(tmp_manifest):
    controls, write = tmp_manifest
    mutated = copy.deepcopy(controls)
    mutated[0]["solutions"] = ["BadSlug_With_Caps"]
    path = write(mutated)
    result = _run(["--allow-todo", "--manifest", str(path)])
    assert result.returncode == 1
    assert "BadSlug_With_Caps" in result.stderr or "BadSlug_With_Caps" in result.stdout


def test_validator_rejects_bad_priority_in_strict(tmp_manifest):
    controls, write = tmp_manifest
    mutated = copy.deepcopy(controls)
    mutated[0]["priority"] = "extreme"
    path = write(mutated)
    result = _run(["--manifest", str(path)])  # strict mode
    assert result.returncode == 1
    assert "priority" in result.stderr.lower() or "priority" in result.stdout.lower()


def test_validator_rejects_missing_sector(tmp_manifest):
    controls, write = tmp_manifest
    mutated = copy.deepcopy(controls)
    del mutated[0]["sectorYesBar"]["bank"]
    path = write(mutated)
    result = _run(["--allow-todo", "--manifest", str(path)])
    assert result.returncode == 1
    assert "sectorYesBar" in result.stderr or "sectorYesBar" in result.stdout


def test_validator_rejects_non_https_verify_url(tmp_manifest):
    controls, write = tmp_manifest
    mutated = copy.deepcopy(controls)
    mutated[0]["verifyIn"] = [{"portal": "X", "path": "Y", "url": "ftp://bad/"}]
    path = write(mutated)
    result = _run(["--allow-todo", "--manifest", str(path)])
    assert result.returncode == 1
    assert "url" in (result.stdout + result.stderr).lower()


def test_validator_rejects_count_drift(tmp_manifest):
    controls, write = tmp_manifest
    path = write(controls[:-1])  # 78 controls
    result = _run(["--allow-todo", "--manifest", str(path)])
    assert result.returncode == 1
    assert "79" in result.stderr or "78" in result.stderr
