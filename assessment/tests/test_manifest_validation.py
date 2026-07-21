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
GENERATOR = REPO_ROOT / "assessment" / "manifest" / "generate_manifest.py"
VALIDATOR = REPO_ROOT / "scripts" / "validate_manifest.py"
SCORE_ENGINE = REPO_ROOT / "assessment" / "engine" / "score.py"
EXPLORER_DATA = REPO_ROOT / "docs" / "javascripts" / "control-explorer-data.json"
CHANGE_RADAR_DATA = REPO_ROOT / "docs" / "javascripts" / "change-radar-data.json"
CONTROL_EXPLORER_JS = REPO_ROOT / "docs" / "javascripts" / "control-explorer.js"
CONTROL_BLUF_JS = REPO_ROOT / "docs" / "javascripts" / "control-bluf.js"
ASSESSMENT_APP_JS = REPO_ROOT / "docs" / "javascripts" / "assessment-app.js"


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


def _load_generate_manifest_module():
    """Import generate_manifest.py as an isolated module instance.

    Each call returns a fresh module so tests can mutate its in-memory
    CHECKS_DB / CONTROLS source-of-truth (or OUTPUT path) without touching the
    real generator used by other tests or by the subprocess ``--check`` guard.
    """
    spec = importlib.util.spec_from_file_location("generate_manifest", GENERATOR)
    assert spec and spec.loader, "Failed to load generate_manifest module"
    gm = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gm)
    return gm


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


def test_primary_finra_notice_mapping_uses_finra_24_09():
    controls = json.loads(MANIFEST.read_text(encoding="utf-8"))
    with_24_09 = [c["id"] for c in controls if "FINRA-24-09" in c.get("regulatory", [])]
    with_25_07 = [c["id"] for c in controls if "FINRA-25-07" in c.get("regulatory", [])]

    assert with_25_07 == [], (
        "FINRA-25-07 is pending/nonbinding metadata and must not be used as a "
        f"primary manifest mapping: {with_25_07}"
    )
    assert len(with_24_09) == 71, (
        "Expected FINRA-24-09 to carry the corrected primary mapping footprint; "
        f"found {len(with_24_09)} controls"
    )
    assert {"1.1", "2.1", "3.1", "4.1", "2.26"} <= set(with_24_09)


def test_finra_25_07_stays_in_explicit_pending_metadata_surfaces():
    assert "FINRA-25-07" not in MANIFEST.read_text(encoding="utf-8")
    assert "FINRA-25-07" not in EXPLORER_DATA.read_text(encoding="utf-8")
    assert "FINRA-25-07" not in CHANGE_RADAR_DATA.read_text(encoding="utf-8")

    assert '"FINRA-25-07": true' in CONTROL_EXPLORER_JS.read_text(encoding="utf-8")
    assert '"FINRA-25-07": true' in CONTROL_BLUF_JS.read_text(encoding="utf-8")

    assessment_text = ASSESSMENT_APP_JS.read_text(encoding="utf-8")
    assert "FINRA RN 25-07" in assessment_text
    assert "NOT been adopted as binding rulemaking" in assessment_text


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


def test_generate_manifest_reproduces_committed_manifest():
    result = subprocess.run(
        [sys.executable, str(GENERATOR), "--check"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, (
        f"Generator drifted:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    )


# ---------------------------------------------------------------------------
# Generator reproducibility repository-wide (PR #1021 Codex thread
# PRRT_kwDOQpaCdc6TAmIx): render_manifest must regenerate and compare the
# generated-core fields for *every* generator-defined control while preserving
# authored enrichment. Previously only 1.11 / 1.13 were regenerated, so a
# CHECKS_DB / CONTROLS change to any of the other 77 controls was silently
# dropped and never surfaced by ``--check``.
# ---------------------------------------------------------------------------


def test_build_control_emits_exactly_the_generated_core_fields():
    """Locks the generated-core contract used to split regen vs preservation."""
    gm = _load_generate_manifest_module()
    row = next(r for r in gm.CONTROLS if r[0] == "1.1")
    built = gm.build_control(*row)
    assert set(built.keys()) == set(gm.GENERATED_CORE_FIELDS)


def test_render_regenerates_checks_for_non_authoritative_control(monkeypatch):
    """A CHECKS_DB change to an ordinary control is now written on render."""
    gm = _load_generate_manifest_module()
    existing = json.loads(MANIFEST.read_text(encoding="utf-8"))
    existing_by_id = {c["id"]: c for c in existing}
    target = "1.1"
    assert target not in {"1.11", "1.13"}

    injected = (
        "1.1.zzz",
        "Injected regression check",
        "Get-MgGroup",
        "no_everyone_assignment",
        [3],
    )
    monkeypatch.setitem(
        gm.CHECKS_DB, target, list(gm.CHECKS_DB[target]) + [injected]
    )

    rendered = {c["id"]: c for c in gm.render_manifest(existing)}
    rendered_check_ids = [chk["check_id"] for chk in rendered[target]["checks"]]

    # Old behavior preserved 1.1 wholesale (injected check absent); the fix
    # regenerates generated-core for every known control.
    assert "1.1.zzz" in rendered_check_ids
    assert rendered[target]["checks"] != existing_by_id[target]["checks"]
    # Authored enrichment stays intact.
    assert rendered[target]["regulatory"] == existing_by_id[target]["regulatory"]


def test_render_regenerates_metadata_for_non_authoritative_control(monkeypatch):
    """CONTROLS metadata (automation / methods / manual_question) is regenerated."""
    gm = _load_generate_manifest_module()
    existing = json.loads(MANIFEST.read_text(encoding="utf-8"))
    existing_by_id = {c["id"]: c for c in existing}
    target = "1.5"
    assert target not in {"1.11", "1.13"}

    new_controls = []
    for row in gm.CONTROLS:
        if row[0] == target:
            cid, filename, pillar, _automation, _methods, _manual_q = row
            new_controls.append(
                (
                    cid,
                    filename,
                    pillar,
                    "partial",
                    ["PPAC_PowerShell", "Graph_API"],
                    "Injected regression manual question?",
                )
            )
        else:
            new_controls.append(row)
    monkeypatch.setattr(gm, "CONTROLS", new_controls)

    rendered = {c["id"]: c for c in gm.render_manifest(existing)}

    assert rendered[target]["automation"] == "partial"
    assert rendered[target]["collection_methods"] == ["PPAC_PowerShell", "Graph_API"]
    assert rendered[target]["manual_question"] == "Injected regression manual question?"
    # These generated-core fields differ from the committed manifest, so
    # ``--check`` would now fire.
    assert rendered[target]["automation"] != existing_by_id[target]["automation"]
    # Authored enrichment is preserved.
    assert rendered[target]["regulatory"] == existing_by_id[target]["regulatory"]


def test_check_detects_non_authoritative_core_drift(tmp_path, monkeypatch):
    """``--check`` must fail on stale generated-core for an ordinary control."""
    gm = _load_generate_manifest_module()
    existing = json.loads(MANIFEST.read_text(encoding="utf-8"))
    stale = copy.deepcopy(existing)
    target = next(c for c in stale if c["id"] == "1.1")
    target["checks"][0]["description"] = "STALE DESCRIPTION — generator must overwrite"

    stale_path = tmp_path / "controls.json"
    stale_path.write_text(
        json.dumps(stale, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    monkeypatch.setattr(gm, "OUTPUT", stale_path)

    assert gm.main(["--check"]) == 1


def test_render_preserves_authored_enrichment_for_ordinary_control():
    """Every non-core (authored) field of an ordinary control is preserved."""
    gm = _load_generate_manifest_module()
    existing = json.loads(MANIFEST.read_text(encoding="utf-8"))
    existing_by_id = {c["id"]: c for c in existing}
    rendered = {c["id"]: c for c in gm.render_manifest(existing)}
    target = "1.5"

    enrichment_keys = [
        k for k in existing_by_id[target] if k not in gm.GENERATED_CORE_FIELDS
    ]
    assert "regulatory" in enrichment_keys  # sanity: enrichment is present
    for key in enrichment_keys:
        assert rendered[target][key] == existing_by_id[target][key], key
    assert set(gm.GENERATED_CORE_FIELDS) <= set(rendered[target].keys())


def test_render_preserves_authored_only_control_wholesale():
    """A control with no generator definition (2.27) is preserved verbatim."""
    gm = _load_generate_manifest_module()
    existing = json.loads(MANIFEST.read_text(encoding="utf-8"))
    existing_by_id = {c["id"]: c for c in existing}
    assert "2.27" not in {row[0] for row in gm.CONTROLS}

    rendered = {c["id"]: c for c in gm.render_manifest(existing)}
    assert rendered["2.27"] == existing_by_id["2.27"]


# ---------------------------------------------------------------------------
# Generator completeness for *new* controls (PR #1021 Codex thread
# PRRT_kwDOQpaCdc6TBvvV): render_manifest previously walked existing_controls
# only, so a control added to CONTROLS but absent from the committed
# controls.json was silently dropped on both ``generate`` (walks existing only)
# and ``--check`` (compares the dropped render to the committed file). The
# generator must append missing generated controls in deterministic generator
# order so a brand-new control both enters the manifest and surfaces as drift.
# ---------------------------------------------------------------------------


def _controls_with_appended(gm, *rows):
    """Return CONTROLS with extra generator rows appended (generator order)."""
    return list(gm.CONTROLS) + list(rows)


def test_render_appends_missing_generated_control(monkeypatch):
    """A control added to CONTROLS but absent from controls.json is appended."""
    gm = _load_generate_manifest_module()
    existing = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert "2.90" not in {c["id"] for c in existing}

    monkeypatch.setattr(
        gm,
        "CONTROLS",
        _controls_with_appended(
            gm, ("2.90", "2.90-newly-authored-control.md", 2, "manual", [], "New?")
        ),
    )

    rendered = gm.render_manifest(existing)
    ids = [c["id"] for c in rendered]

    assert "2.90" in ids
    # Appended at the end (generator order); existing controls keep their order.
    assert ids[-1] == "2.90"
    assert ids[: len(existing)] == [c["id"] for c in existing]
    # The appended control carries the full generated-core contract.
    new_control = next(c for c in rendered if c["id"] == "2.90")
    assert set(gm.GENERATED_CORE_FIELDS) <= set(new_control.keys())


def test_render_appends_multiple_missing_controls_in_generator_order(monkeypatch):
    """Multiple new controls are appended in CONTROLS (generator) order."""
    gm = _load_generate_manifest_module()
    existing = json.loads(MANIFEST.read_text(encoding="utf-8"))

    monkeypatch.setattr(
        gm,
        "CONTROLS",
        _controls_with_appended(
            gm,
            ("2.90", "2.90-new-a.md", 2, "manual", [], "A?"),
            ("2.91", "2.91-new-b.md", 2, "full", ["PPAC_PowerShell"], None),
        ),
    )

    ids = [c["id"] for c in gm.render_manifest(existing)]
    assert ids[-2:] == ["2.90", "2.91"]


def test_render_appends_missing_without_duplicates_or_disturbing_authored(monkeypatch):
    """Appending new controls preserves authored-only 2.27 and adds no dups."""
    gm = _load_generate_manifest_module()
    existing = json.loads(MANIFEST.read_text(encoding="utf-8"))
    existing_by_id = {c["id"]: c for c in existing}

    monkeypatch.setattr(
        gm,
        "CONTROLS",
        _controls_with_appended(
            gm, ("2.90", "2.90-new-a.md", 2, "manual", [], "A?")
        ),
    )

    rendered = gm.render_manifest(existing)
    ids = [c["id"] for c in rendered]

    assert len(ids) == len(existing) + 1
    assert len(ids) == len(set(ids)), "no duplicate control ids"
    # Authored-only control is preserved verbatim and not duplicated.
    assert ids.count("2.27") == 1
    rendered_by_id = {c["id"]: c for c in rendered}
    assert rendered_by_id["2.27"] == existing_by_id["2.27"]
    # Authored enrichment on an ordinary control is still preserved.
    assert rendered_by_id["1.5"]["regulatory"] == existing_by_id["1.5"]["regulatory"]


def test_check_detects_missing_generated_control_drift(tmp_path, monkeypatch):
    """``--check`` fails when CONTROLS gains a control absent from controls.json."""
    gm = _load_generate_manifest_module()
    committed = MANIFEST.read_text(encoding="utf-8")

    # OUTPUT points at an unmodified copy of the committed manifest (no new
    # control); CONTROLS gains a new control. render must append it, so the
    # rendered text now differs from the committed file and --check fails.
    output_path = tmp_path / "controls.json"
    output_path.write_text(committed, encoding="utf-8")
    monkeypatch.setattr(gm, "OUTPUT", output_path)
    monkeypatch.setattr(
        gm,
        "CONTROLS",
        _controls_with_appended(
            gm, ("2.90", "2.90-new-a.md", 2, "manual", [], "A?")
        ),
    )

    assert gm.main(["--check"]) == 1


def test_control_1_11_marks_non_evaluable_subchecks_manual():
    controls = json.loads(MANIFEST.read_text(encoding="utf-8"))
    ctrl = next(c for c in controls if c["id"] == "1.11")
    checks = {chk["check_id"]: chk for chk in ctrl["checks"]}

    assert ctrl["automation"] == "partial"
    assert isinstance(ctrl["manual_question"], str) and ctrl["manual_question"].strip()
    assert ctrl["zone_thresholds"]["zone3"]["min_checks_passed"] == 1

    assert checks["1.11.a"]["pass_condition"] == "ca_policy_requires_mfa"
    assert checks["1.11.b"]["pass_condition"] == ""
    assert checks["1.11.c"]["pass_condition"] == ""
    assert checks["1.11.b"].get("collection_methods") == ["Manual"]
    assert checks["1.11.c"].get("collection_methods") == ["Manual"]


def test_control_1_4_separates_classic_dlp_from_required_acp_evidence():
    score = _load_score_module()
    controls = json.loads(MANIFEST.read_text(encoding="utf-8"))
    ctrl = next(c for c in controls if c["id"] == "1.4")
    checks = {chk["check_id"]: chk for chk in ctrl["checks"]}

    assert ctrl["automation"] == "partial"
    assert ctrl["collection_methods"] == ["PPAC_PowerShell"]
    assert ctrl["zone_thresholds"] == {
        "zone1": {"min_checks_passed": 1, "maturity_score": 1},
        "zone2": {"min_checks_passed": 1, "maturity_score": 2},
        "zone3": {"min_checks_passed": 1, "maturity_score": 4},
    }

    question = ctrl["manual_question"].lower()
    for required_term in (
        "policy",
        "assignment",
        "allowlist",
        "environment-group scope",
        "runtime",
        "blocked connector",
        "zone 2",
        "zone 3",
    ):
        assert required_term in question

    assert checks["1.4.a"]["api_call"] == "Get-DlpPolicy"
    assert checks["1.4.a"]["pass_condition"] == "dlp_policy_exists"
    assert checks["1.4.a"]["description"] == (
        "Enabled classic DLP policy has effective scope over collected "
        "Power Platform environments"
    )
    assert "agent" not in checks["1.4.a"]["description"].lower()
    assert score.classify_check_evaluator_state(
        checks["1.4.a"], ctrl["automation"], ctrl["collection_methods"]
    ) == "auto_evaluable"
    assert score._resolve_source_key(  # noqa: SLF001
        checks["1.4.a"]["api_call"], ctrl["collection_methods"]
    ) == "ppac"

    acp_api = (
        "https://api.powerplatform.com/governance/ruleBasedPolicies"
        "?api-version=2024-10-01"
    )
    for check_id in ("1.4.b", "1.4.c"):
        check = checks[check_id]
        assert check["api_call"] == acp_api
        assert check["pass_condition"] == ""
        assert check["collection_methods"] == ["Manual"]
        assert score.classify_check_evaluator_state(
            check, ctrl["automation"], ctrl["collection_methods"]
        ) == "manual_only"
        assert score._resolve_source_key(  # noqa: SLF001
            check["api_call"], check["collection_methods"]
        ) is None

    assert acp_api not in score.API_SOURCE_MAP
    assert all(
        "ruleBasedPolicies" not in key and "ruleBasedPolicies" not in filename
        for key, filename in score.SOURCE_FILENAMES.items()
    )


def test_control_1_13_corrects_sit_api_call_and_manual_gate():
    controls = json.loads(MANIFEST.read_text(encoding="utf-8"))
    ctrl = next(c for c in controls if c["id"] == "1.13")
    checks = {chk["check_id"]: chk for chk in ctrl["checks"]}

    assert ctrl["automation"] == "partial"
    assert ctrl["zone_thresholds"]["zone1"]["min_checks_passed"] == 0
    assert ctrl["zone_thresholds"]["zone3"]["min_checks_passed"] == 1
    assert checks["1.13.a"]["api_call"] == "Get-DlpSensitiveInformationType"
    assert checks["1.13.a"]["pass_condition"] == ""
    assert checks["1.13.a"].get("collection_methods") == ["Manual"]
    assert checks["1.13.b"]["description"] == (
        "Enforced Copilot-scoped DLP policy rules reference SIT conditions"
    )
    assert checks["1.13.b"]["pass_condition"] == "dlp_references_sits"
    assert checks["1.13.b"]["api_call"] == "Get-DlpCompliancePolicy"


def test_control_1_15_remains_manual_without_get_mgorganization_tls_claims():
    controls = json.loads(MANIFEST.read_text(encoding="utf-8"))
    ctrl = next(c for c in controls if c["id"] == "1.15")

    assert ctrl["automation"] == "manual"
    assert ctrl["collection_methods"] == []
    assert ctrl["checks"] == []
    assert ctrl["manual_question"] is not None

    unsupported_conditions = {
        ("Get-MgOrganization", "tls_12_enforced"),
        ("Get-MgOrganization", "at_rest_encryption_verified"),
    }
    offenders = [
        f"{ctrl['id']}:{check.get('check_id')}"
        for check in ctrl.get("checks", [])
        if (check.get("api_call"), check.get("pass_condition"))
        in unsupported_conditions
    ]
    assert offenders == [], (
        "Control 1.15 must not claim Get-MgOrganization proves TLS or "
        f"at-rest encryption settings: {offenders}"
    )


def test_controls_1_15_and_1_16_rubric_fields_are_not_todo():
    """Rubric fields for 1.15 and 1.16 must be authored content, not TODO placeholders."""
    controls = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rubric_fields = ("priority", "yesBar", "partialBar", "noBar")
    for cid in ("1.15", "1.16"):
        ctrl = next(c for c in controls if c["id"] == cid)
        for field in rubric_fields:
            value = ctrl.get(field, "")
            assert not str(value).startswith("TODO"), (
                f"Control {cid}: rubric field '{field}' still contains a TODO placeholder: {value!r}"
            )
        fn = ctrl.get("facilitatorNotes", {})
        for note_key in ("ask", "followUp"):
            value = fn.get(note_key, "")
            assert not str(value).startswith("TODO"), (
                f"Control {cid}: facilitatorNotes.{note_key} still contains a TODO placeholder: {value!r}"
            )


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
