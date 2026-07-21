"""Tests for ``scripts/validate_manifest.py`` and the harvested manifest.

These tests guard the v1.4 manifest contract:

* All 79 controls present and enriched with the v1.4 fields.
* Validator passes in ``--allow-todo`` mode against the committed manifest.
* Validator catches structural problems (bad slug, missing key, bad URL,
  unknown priority) when applied to mutated copies.
"""
from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST = REPO_ROOT / "assessment" / "manifest" / "controls.json"
VALIDATOR = REPO_ROOT / "scripts" / "validate_manifest.py"
SCORE_ENGINE = REPO_ROOT / "assessment" / "engine" / "score.py"


def _run(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def _load_score_module():
    spec = importlib.util.spec_from_file_location("score", SCORE_ENGINE)
    assert spec and spec.loader, "Failed to load assessment engine module"
    score = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(score)
    return score


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


def test_control_1_12_requires_manual_portal_review():
    controls = json.loads(MANIFEST.read_text(encoding="utf-8"))
    ctrl = next(c for c in controls if c["id"] == "1.12")

    assert ctrl["automation"] == "manual"
    assert ctrl["collection_methods"] == []
    assert ctrl["checks"] == []
    assert "Purview portal evidence" in ctrl["manual_question"]


def test_control_1_11_marks_non_evaluable_subchecks_manual():
    controls = json.loads(MANIFEST.read_text(encoding="utf-8"))
    ctrl = next(c for c in controls if c["id"] == "1.11")
    checks = {chk["check_id"]: chk for chk in ctrl["checks"]}

    assert ctrl["automation"] == "partial"
    assert isinstance(ctrl["manual_question"], str) and ctrl["manual_question"].strip()

    assert checks["1.11.a"]["pass_condition"] == "ca_policy_requires_mfa"
    assert checks["1.11.b"]["pass_condition"] == ""
    assert checks["1.11.c"]["pass_condition"] == ""
    assert checks["1.11.b"].get("collection_methods") == ["Manual"]
    assert checks["1.11.c"].get("collection_methods") == ["Manual"]


def test_control_1_13_corrects_sit_api_call_and_manual_gate():
    controls = json.loads(MANIFEST.read_text(encoding="utf-8"))
    ctrl = next(c for c in controls if c["id"] == "1.13")
    checks = {chk["check_id"]: chk for chk in ctrl["checks"]}

    assert ctrl["automation"] == "partial"
    assert checks["1.13.a"]["api_call"] == "Get-DlpSensitiveInformationType"
    assert checks["1.13.a"]["pass_condition"] == ""
    assert checks["1.13.a"].get("collection_methods") == ["Manual"]
    assert checks["1.13.b"]["pass_condition"] == "dlp_references_sits"
    assert checks["1.13.b"]["api_call"] == "Get-DlpCompliancePolicy"


def test_control_1_15_downgraded_to_manual_until_collectible():
    controls = json.loads(MANIFEST.read_text(encoding="utf-8"))
    ctrl = next(c for c in controls if c["id"] == "1.15")

    assert ctrl["automation"] == "manual"
    assert ctrl["collection_methods"] == []
    assert ctrl["checks"] == []
    assert isinstance(ctrl["manual_question"], str) and ctrl["manual_question"].strip()


def test_manifest_excludes_unsupported_insider_risk_cmdlet_surface():
    controls = json.loads(MANIFEST.read_text(encoding="utf-8"))
    banned = {
        "Get-InsiderRiskPolicy",
        "New-InsiderRiskPolicy",
        "Set-InsiderRiskPolicy",
        "Get-InsiderRiskPolicyTemplate",
        "Get-InsiderRiskTenantSettings",
    }
    offenders: list[str] = []
    for ctrl in controls:
        for check in ctrl.get("checks", []):
            api = check.get("api_call")
            if api in banned:
                offenders.append(f"{ctrl['id']}:{check.get('check_id')}")

    assert offenders == [], (
        "Unsupported Insider Risk automation surface must not appear in manifest checks: "
        + ", ".join(offenders)
    )


def test_manifest_non_manual_checks_resolve_to_source_or_explicit_state():
    """Manifest-wide lint: no silent source-map drift on non-manual checks."""
    score = _load_score_module()
    controls = json.loads(MANIFEST.read_text(encoding="utf-8"))
    issues = score.lint_manifest_source_resolution(controls)
    assert issues == [], (
        "Non-manual checks must resolve to a source or be explicitly "
        f"manual/unimplemented. Found: {issues}"
    )


def test_source_resolution_lint_flags_non_manual_unknown_method_token():
    """Adversarial guard: unknown automatable method token must fail lint."""
    score = _load_score_module()
    controls = json.loads(MANIFEST.read_text(encoding="utf-8"))
    mutated = copy.deepcopy(controls)
    target = next(c for c in mutated if c["id"] == "4.4")
    target["collection_methods"] = ["SharePoint_Graph_BROKEN"]
    for check in target.get("checks", []):
        check["api_call"] = f"{check.get('api_call')}_BROKEN"

    issues = score.lint_manifest_source_resolution([target])
    assert issues, "Expected source-resolution lint to catch broken method token"
    assert any("4.4:4.4.a" in issue for issue in issues), issues


def test_source_resolution_separates_azure_network_from_sentinel():
    """Azure network checks must not borrow Sentinel source availability."""
    score = _load_score_module()

    assert score._resolve_source_key(  # noqa: SLF001
        "Get-AzOperationalInsightsWorkspace", ["Sentinel"]
    ) == "sentinel"
    assert score._resolve_source_key(  # noqa: SLF001
        "Get-AzPrivateEndpointConnection", ["Azure_API"]
    ) == "azure/network"
    assert "azure/network" in score.UNCOLLECTED_SOURCE_KEYS
    assert "azure/network" not in score.SOURCE_FILENAMES


def test_manifest_control_1_20_resolves_to_uncollected_azure_network_source():
    """Control 1.20 source mapping should stay truthful until collector exists."""
    score = _load_score_module()
    controls = json.loads(MANIFEST.read_text(encoding="utf-8"))
    control = next(c for c in controls if c["id"] == "1.20")
    for check in control.get("checks", []):
        source = score._resolve_source_key(  # noqa: SLF001
            str(check.get("api_call", "")),
            check.get("collection_methods") or control.get("collection_methods"),
        )
        assert source == "azure/network"


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
