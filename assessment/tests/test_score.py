"""
Unit tests for the FSI-AgentGov scoring engine (engine/score.py).

Tests 5 representative controls against fixture data to verify maturity
scoring, zone thresholds, confidence levels, and summary calculations.
"""

import json
import sys
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Path setup — allow importing score.py from the engine directory
# ---------------------------------------------------------------------------

ASSESSMENT_ROOT = Path(__file__).resolve().parent.parent
ENGINE_DIR = ASSESSMENT_ROOT / "engine"
FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"

sys.path.insert(0, str(ENGINE_DIR))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_fixture(name: str) -> dict:
    """Load a JSON fixture file by name."""
    path = FIXTURES_DIR / name
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: dict) -> None:
    """Write data as JSON to *path*."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# ---------------------------------------------------------------------------
# DLP-for-Copilot scope evidence (control 1.13.b)
#   The evaluator credits a policy only when it binds the Microsoft 365 Copilot
#   scope via the three documented structural signals — Workload=Applications, a
#   Locations entry carrying the Copilot location GUID, and the
#   CopilotExperiences enforcement plane (Microsoft Learn New-DlpCompliancePolicy
#   Example 4 / "DLP for Microsoft 365 Copilot location"; control 1.13
#   powershell-setup.md §9). These helpers build valid-scope fixtures so the
#   SIT-parsing tests exercise "direct/grouped/AdvancedRule rules under valid
#   scope" and the scope tests can drop each signal in isolation.
# ---------------------------------------------------------------------------
COPILOT_LOCATION_GUID = "470f2276-e011-4e9d-a6ec-20768be3a4b0"


def copilot_scope_fields() -> dict:
    """The three structural Copilot-scope signals a qualifying policy carries."""
    return {
        "Workload": "Applications",
        "EnforcementPlanes": ["CopilotExperiences"],
        "Locations": [
            {
                "Workload": "Applications",
                "Location": COPILOT_LOCATION_GUID,
                "Inclusions": [{"Type": "Tenant", "Identity": "All"}],
            }
        ],
    }


def scoped_policy(**overrides) -> dict:
    """A Mode=Enable, Copilot-scoped DLP policy with overridable fields.

    Enabled is intentionally *absent* unless overridden so a bare
    ``scoped_policy(...)`` exercises the "Mode governs, Enabled absent" P2 path.
    """
    policy = {"Name": "Copilot MNPI DLP", "Mode": "Enable"}
    policy.update(copilot_scope_fields())
    policy.update(overrides)
    return policy


def direct_sit_rule(*sit_names: str) -> dict:
    """An active rule with a direct ContentContainsSensitiveInformation match."""
    return {
        "Disabled": False,
        "ContentContainsSensitiveInformation": [{"Name": n} for n in sit_names],
    }


def setup_collected_dir(tmp_path: Path) -> Path:
    """Copy all collector fixture files into a temporary collected/ directory."""
    collected = tmp_path / "collected"
    collected.mkdir()
    for name in ("ppac", "graph", "purview", "sharepoint", "sentinel"):
        src = FIXTURES_DIR / f"{name}.json"
        if src.exists():
            data = load_fixture(f"{name}.json")
            write_json(collected / f"{name}.json", data)
    return collected


def build_manifest_with_controls(controls: list[dict]) -> dict:
    """Wrap a list of control dicts into a valid manifest envelope."""
    return {
        "version": "1.0.0",
        "generated": "2026-03-25T20:00:00Z",
        "controls": controls,
    }


def build_frontier_manifest_with_questions(questions: list[dict]) -> dict:
    """Wrap frontier question dicts into a minimal manifest envelope."""
    return {
        "version": "1.0.0",
        "drivers": [
            {"id": "ai_strategy", "name": "AI Strategy"},
            {"id": "business_strategy", "name": "Business Strategy"},
            {"id": "ai_governance", "name": "AI Governance"},
            {"id": "technology_data", "name": "Technology & Data"},
            {"id": "organization_culture", "name": "Organization & Culture"},
        ],
        "questions": questions,
        "pattern_target_profiles": {},
    }


# ---------------------------------------------------------------------------
# Fixtures (pytest)
# ---------------------------------------------------------------------------

@pytest.fixture()
def manifest() -> dict:
    """The 5-control test manifest."""
    return load_fixture("controls_subset.json")


@pytest.fixture()
def collected_dir(tmp_path: Path) -> Path:
    """Temporary collected/ directory pre-populated with fixture data."""
    return setup_collected_dir(tmp_path)


@pytest.fixture()
def expected_scores() -> dict:
    """Expected scoring output for zone 2."""
    return load_fixture("expected_scores.json")


# ---------------------------------------------------------------------------
# Test: full pass — all applicable checks pass (zone 1)
# ---------------------------------------------------------------------------

class TestFullPassControl:
    """Control 1.1 with all zone-1 checks passing → maturity 1, confidence high."""

    def test_full_pass_control(self, tmp_path: Path, manifest: dict, collected_dir: Path):
        # For zone 1, only check 1.1.a is applicable and it should pass.
        score = pytest.importorskip("score")  # type: ignore[import-untyped]

        manifest_path = tmp_path / "controls.json"
        output_path = tmp_path / "scores.json"
        write_json(manifest_path, manifest)

        score.run(
            manifest_path=str(manifest_path),
            collected_dir=str(collected_dir),
            zone=1,
            output_path=str(output_path),
        )

        result = json.loads(output_path.read_text(encoding="utf-8"))
        ctrl = next(c for c in result["controls"] if c["id"] == "1.1")

        assert ctrl["maturity_score"] >= 1, "Zone-1 threshold should be met"
        assert ctrl["confidence"] == "high"


# ---------------------------------------------------------------------------
# Test: partial fail — check 1.1.b fails for zone 2
# ---------------------------------------------------------------------------

class TestPartialFailControl:
    """Control 1.1 for zone 2 with check 1.1.b failing → maturity 0 (below threshold)."""

    def test_partial_fail_control(self, tmp_path: Path, manifest: dict, collected_dir: Path):
        score = pytest.importorskip("score")  # type: ignore[import-untyped]

        manifest_path = tmp_path / "controls.json"
        output_path = tmp_path / "scores.json"
        write_json(manifest_path, manifest)

        score.run(
            manifest_path=str(manifest_path),
            collected_dir=str(collected_dir),
            zone=2,
            output_path=str(output_path),
        )

        result = json.loads(output_path.read_text(encoding="utf-8"))
        ctrl = next(c for c in result["controls"] if c["id"] == "1.1")

        # fsiSecurityGroups is empty in graph.json, so check 1.1.b fails.
        # Zone 2 requires min 2 checks passed → below threshold → maturity 0.
        assert ctrl["checks_passed"] < ctrl["min_checks_required"]
        assert ctrl["maturity_score"] == 0
        assert ctrl["confidence"] == "high"


# ---------------------------------------------------------------------------
# Test: manual-only control
# ---------------------------------------------------------------------------

class TestManualOnlyControl:
    """A control with automation='manual' should get needs_manual=true, maturity 0."""

    def test_manual_only_control(self, tmp_path: Path, collected_dir: Path):
        score = pytest.importorskip("score")  # type: ignore[import-untyped]

        manual_control = {
            "id": "99.1",
            "title": "Manual-Only Control for Testing",
            "pillar": 99,
            "pillar_name": "Test",
            "source_file": "docs/controls/test/99.1-manual-only.md",
            "automation": "manual",
            "collection_methods": [],
            "checks": [],
            "zone_thresholds": {
                "zone1": {"min_checks_passed": 0, "maturity_score": 0},
                "zone2": {"min_checks_passed": 0, "maturity_score": 0},
                "zone3": {"min_checks_passed": 0, "maturity_score": 0},
            },
            "manual_question": "Describe the organization's agent deployment approval workflow.",
        }

        manifest_data = build_manifest_with_controls([manual_control])
        manifest_path = tmp_path / "controls.json"
        output_path = tmp_path / "scores.json"
        write_json(manifest_path, manifest_data)

        score.run(
            manifest_path=str(manifest_path),
            collected_dir=str(collected_dir),
            zone=2,
            output_path=str(output_path),
        )

        result = json.loads(output_path.read_text(encoding="utf-8"))
        ctrl = next(c for c in result["controls"] if c["id"] == "99.1")

        assert ctrl["needs_manual"] is True
        assert ctrl["maturity_score"] == 0


# ---------------------------------------------------------------------------
# Test: partial automation — auto checks scored, but needs_manual=true
# ---------------------------------------------------------------------------

class TestPartialAutomationControl:
    """Control 1.3 (partial automation) scores auto checks but sets needs_manual=true."""

    def test_partial_automation_control(self, tmp_path: Path, manifest: dict, collected_dir: Path):
        score = pytest.importorskip("score")  # type: ignore[import-untyped]

        manifest_path = tmp_path / "controls.json"
        output_path = tmp_path / "scores.json"
        write_json(manifest_path, manifest)

        score.run(
            manifest_path=str(manifest_path),
            collected_dir=str(collected_dir),
            zone=2,
            output_path=str(output_path),
        )

        result = json.loads(output_path.read_text(encoding="utf-8"))
        ctrl = next(c for c in result["controls"] if c["id"] == "1.3")

        # Automated checks should be evaluated
        assert ctrl["checks_applicable"] >= 1
        # But the control also has a manual question
        assert ctrl["needs_manual"] is True
        assert ctrl["manual_question"] is not None


# ---------------------------------------------------------------------------
# Test: Control 1.12 must remain manual/fail-closed
# ---------------------------------------------------------------------------

class TestControl112ManualGate:
    """Control 1.12 cannot pass via unsupported automation surfaces."""

    def test_control_1_12_is_manual_only_in_real_manifest(
        self, tmp_path: Path, collected_dir: Path
    ):
        score = pytest.importorskip("score")  # type: ignore[import-untyped]
        real_manifest = ASSESSMENT_ROOT / "manifest" / "controls.json"
        controls = json.loads(real_manifest.read_text(encoding="utf-8"))
        manifest_data = build_manifest_with_controls(controls)

        manifest_path = tmp_path / "controls.json"
        output_path = tmp_path / "scores.json"
        write_json(manifest_path, manifest_data)

        score.run(
            manifest_path=str(manifest_path),
            collected_dir=str(collected_dir),
            zone=2,
            output_path=str(output_path),
        )

        result = json.loads(output_path.read_text(encoding="utf-8"))
        ctrl = next(c for c in result["controls"] if c["id"] == "1.12")

        assert ctrl["needs_manual"] is True
        assert ctrl["checks"] == []
        assert ctrl["checks_applicable"] == 0
        assert ctrl["maturity_score"] == 0
        assert ctrl["evaluator_state"] == "manual_only"


class TestControl115ManualGate:
    """Control 1.15 cannot claim unsupported tenant-level TLS/at-rest automation."""

    def test_control_1_15_is_manual_only_in_real_manifest(
        self, tmp_path: Path, collected_dir: Path
    ):
        score = pytest.importorskip("score")  # type: ignore[import-untyped]
        real_manifest = ASSESSMENT_ROOT / "manifest" / "controls.json"
        controls = json.loads(real_manifest.read_text(encoding="utf-8"))
        manifest_data = build_manifest_with_controls(controls)

        manifest_path = tmp_path / "controls.json"
        output_path = tmp_path / "scores.json"
        write_json(manifest_path, manifest_data)

        score.run(
            manifest_path=str(manifest_path),
            collected_dir=str(collected_dir),
            zone=2,
            output_path=str(output_path),
        )

        result = json.loads(output_path.read_text(encoding="utf-8"))
        ctrl = next(c for c in result["controls"] if c["id"] == "1.15")

        assert ctrl["needs_manual"] is True
        assert ctrl["checks"] == []
        assert ctrl["checks_applicable"] == 0
        assert ctrl["maturity_score"] == 0
        assert ctrl["evaluator_state"] == "manual_only"


# ---------------------------------------------------------------------------
# Test: per-check Manual collection_methods override parent control methods
# ---------------------------------------------------------------------------

class TestPerCheckManualMethods:
    """Checks that declare ``collection_methods: ["Manual"]`` must be scored as
    manual-only even when their parent control is automatable and their
    ``api_call`` maps to an automated source.

    Regression for PR #1021: 1.11.b / 1.11.c / 1.13.a were emitted in zone 2/3
    as 'unknown' automated checks carrying graph.json / purview.json evidence
    instead of manual-only evidence, because evaluate_check resolved the source
    from the parent control's methods (and the check's api_call) rather than
    honoring the check-level Manual override. Their automated siblings
    (1.11.a, 1.13.b) must keep their real collected source.
    """

    @staticmethod
    def _real_control(control_id: str) -> dict:
        real_manifest = ASSESSMENT_ROOT / "manifest" / "controls.json"
        controls = json.loads(real_manifest.read_text(encoding="utf-8"))
        return next(c for c in controls if c["id"] == control_id)

    @classmethod
    def _eval_real_check(cls, control_id: str, check_id: str, zone: int) -> dict:
        score = pytest.importorskip("score")  # type: ignore[import-untyped]
        control = cls._real_control(control_id)
        check = next(c for c in control["checks"] if c["check_id"] == check_id)
        # Non-empty collected sources so the automated path *would* resolve —
        # this is exactly the condition under which the bug surfaced.
        collected = {
            "graph": {"conditional_access_policies": []},
            "purview": {"dlpCompliancePolicies": []},
        }
        return score.evaluate_check(
            check,
            collected,
            zone,
            control.get("collection_methods", []),
            "2026-01-01T00:00:00Z",
            control.get("automation", "full"),
        )

    @pytest.mark.parametrize(
        "control_id,check_id,zone",
        [
            ("1.11", "1.11.b", 2),
            ("1.11", "1.11.b", 3),
            ("1.11", "1.11.c", 3),
            ("1.13", "1.13.a", 2),
            ("1.13", "1.13.a", 3),
        ],
    )
    def test_manual_check_is_manual_only_with_no_automated_source(
        self, control_id: str, check_id: str, zone: int
    ):
        res = self._eval_real_check(control_id, check_id, zone)

        assert res["applicable"] is True
        assert res["evaluator_state"] == "manual_only"
        # The api_call would otherwise resolve to graph.json / purview.json.
        assert res["source"] is None
        # No automated pass/fail — scoring/thresholds must be unaffected.
        assert res["passed"] is None
        assert res["data_available"] is False
        assert "manual" in res["evidence"].lower()

    @pytest.mark.parametrize(
        "control_id,check_id,zone,expected_source",
        [
            ("1.11", "1.11.a", 2, "graph.json"),
            ("1.11", "1.11.a", 3, "graph.json"),
            ("1.13", "1.13.b", 2, "purview.json"),
            ("1.13", "1.13.b", 3, "purview.json"),
        ],
    )
    def test_automated_sibling_checks_remain_automated(
        self, control_id: str, check_id: str, zone: int, expected_source: str
    ):
        res = self._eval_real_check(control_id, check_id, zone)

        assert res["applicable"] is True
        assert res["evaluator_state"] == "auto_evaluable"
        assert res["source"] == expected_source

    @pytest.mark.parametrize("zone", [2, 3])
    def test_manual_checks_carry_no_automated_evidence_end_to_end(
        self, tmp_path: Path, collected_dir: Path, zone: int
    ):
        score = pytest.importorskip("score")  # type: ignore[import-untyped]
        real_manifest = ASSESSMENT_ROOT / "manifest" / "controls.json"
        controls = json.loads(real_manifest.read_text(encoding="utf-8"))
        manifest_data = build_manifest_with_controls(controls)

        manifest_path = tmp_path / "controls.json"
        output_path = tmp_path / "scores.json"
        write_json(manifest_path, manifest_data)

        score.run(
            manifest_path=str(manifest_path),
            collected_dir=str(collected_dir),
            zone=zone,
            output_path=str(output_path),
        )

        result = json.loads(output_path.read_text(encoding="utf-8"))
        controls_by_id = {c["id"]: c for c in result["controls"]}

        # Manual checks applicable in this zone must present no automated source.
        manual_expect = {"1.11": ["1.11.b"], "1.13": ["1.13.a"]}
        if zone == 3:
            manual_expect["1.11"].append("1.11.c")

        for control_id, check_ids in manual_expect.items():
            ctrl = controls_by_id[control_id]
            evidence = ctrl["evidence"]
            check_states = {c["check_id"]: c for c in ctrl["checks"]}
            for check_id in check_ids:
                assert evidence[check_id]["source"] is None
                assert check_states[check_id]["evaluator_state"] == "manual_only"
                assert check_states[check_id]["passed"] is None

        # Automated siblings keep their real collected source in the same report.
        ctrl_111 = controls_by_id["1.11"]
        ctrl_113 = controls_by_id["1.13"]
        assert ctrl_111["evidence"]["1.11.a"]["source"] == "graph.json"
        assert ctrl_113["evidence"]["1.13.b"]["source"] == "purview.json"
        sibling_111a = next(
            c for c in ctrl_111["checks"] if c["check_id"] == "1.11.a"
        )
        assert sibling_111a["evaluator_state"] == "auto_evaluable"


# ---------------------------------------------------------------------------
# Test: missing data → confidence low
# ---------------------------------------------------------------------------

class TestMissingDataLowConfidence:
    """When a collected data source returns null/missing → confidence 'low'."""

    def test_missing_data_low_confidence(self, tmp_path: Path, manifest: dict):
        score = pytest.importorskip("score")  # type: ignore[import-untyped]

        # Create a collected dir with empty/null data files
        collected = tmp_path / "collected"
        collected.mkdir()

        # Write PPAC with null critical fields
        null_ppac = {
            "_metadata": {
                "collector": "Collect-PPAC",
                "timestamp": "2026-03-25T21:00:00Z",
                "tenant_id": "test-tenant",
                "warnings": ["Failed to retrieve environments"],
            },
            "environments": None,
            "dlpPolicies": None,
            "roleAssignments": None,
            "routingRules": None,
            "inactivityTimeout": None,
            "securityPosture": None,
            "agentFeatureFlags": None,
            "environmentGroups": None,
        }
        write_json(collected / "ppac.json", null_ppac)

        # Write minimal stubs for other collectors so the engine doesn't crash
        for name in ("graph", "purview", "sharepoint", "sentinel"):
            stub = {
                "_metadata": {
                    "collector": name.capitalize(),
                    "timestamp": "2026-03-25T21:00:00Z",
                    "tenant_id": "test-tenant",
                    "warnings": [f"{name} data unavailable"],
                },
            }
            write_json(collected / f"{name}.json", stub)

        manifest_path = tmp_path / "controls.json"
        output_path = tmp_path / "scores.json"
        write_json(manifest_path, manifest)

        score.run(
            manifest_path=str(manifest_path),
            collected_dir=str(collected),
            zone=2,
            output_path=str(output_path),
        )

        result = json.loads(output_path.read_text(encoding="utf-8"))

        # Controls that depend on PPAC data should have low confidence
        ctrl_11 = next(c for c in result["controls"] if c["id"] == "1.1")
        assert ctrl_11["confidence"] == "low"


# ---------------------------------------------------------------------------
# Test: zone 3 threshold boundary — all checks pass → maturity 4
# ---------------------------------------------------------------------------

class TestZoneThresholdBoundary:
    """Zone 3 requires all checks passed for control 1.1; all passing → maturity 4."""

    def test_zone_threshold_boundary(self, tmp_path: Path, manifest: dict):
        score = pytest.importorskip("score")  # type: ignore[import-untyped]

        # Build collected data where all checks for 1.1 pass (including 1.1.b)
        collected = tmp_path / "collected"
        collected.mkdir()

        # PPAC: no "All Users" assignment, share-with-everyone disabled
        ppac_data = load_fixture("ppac.json")
        write_json(collected / "ppac.json", ppac_data)

        # Graph: include an FSI publisher security group so check 1.1.b passes
        graph_data = load_fixture("graph.json")
        graph_data["fsiSecurityGroups"] = [
            {
                "displayName": "FSI Agent Publishers",
                "id": "sg-publishers-001",
                "securityEnabled": True,
            }
        ]
        write_json(collected / "graph.json", graph_data)

        # Copy remaining fixtures
        for name in ("purview", "sharepoint", "sentinel"):
            write_json(collected / f"{name}.json", load_fixture(f"{name}.json"))

        manifest_path = tmp_path / "controls.json"
        output_path = tmp_path / "scores.json"
        write_json(manifest_path, manifest)

        score.run(
            manifest_path=str(manifest_path),
            collected_dir=str(collected),
            zone=3,
            output_path=str(output_path),
        )

        result = json.loads(output_path.read_text(encoding="utf-8"))
        ctrl = next(c for c in result["controls"] if c["id"] == "1.1")

        assert ctrl["checks_passed"] == 3
        assert ctrl["maturity_score"] == 4
        assert ctrl["confidence"] == "high"


# ---------------------------------------------------------------------------
# Test: zero-threshold maturity safety guard (fail closed)
# ---------------------------------------------------------------------------


class TestZeroThresholdMaturitySafety:
    """min_checks_passed=0 must not auto-award nonzero maturity without attestation."""

    def test_zero_threshold_nonzero_target_fails_closed_without_attestation(self):
        score = pytest.importorskip("score")  # type: ignore[import-untyped]

        maturity_score, maturity_label, min_required = score.compute_maturity(
            checks_passed=999,
            zone=2,
            zone_thresholds={
                "zone2": {"min_checks_passed": 0, "maturity_score": 3}
            },
        )

        assert min_required == 0
        assert maturity_score == 0
        assert maturity_label == "Not Implemented"

    def test_zero_threshold_nonzero_target_requires_supported_attestation(self):
        score = pytest.importorskip("score")  # type: ignore[import-untyped]

        maturity_score, maturity_label, min_required = score.compute_maturity(
            checks_passed=0,
            zone=3,
            zone_thresholds={
                "zone3": {
                    "min_checks_passed": 0,
                    "maturity_score": 4,
                    "supported_attestation": True,
                }
            },
        )

        assert min_required == 0
        assert maturity_score == 4
        assert maturity_label == "Fully Governed"

    def test_zero_threshold_target_zero_remains_valid_for_manual_controls(self):
        score = pytest.importorskip("score")  # type: ignore[import-untyped]

        maturity_score, maturity_label, min_required = score.compute_maturity(
            checks_passed=0,
            zone=1,
            zone_thresholds={
                "zone1": {"min_checks_passed": 0, "maturity_score": 0}
            },
        )

        assert min_required == 0
        assert maturity_score == 0
        assert maturity_label == "Not Implemented"


# ---------------------------------------------------------------------------
# Test: manual-attestation maturity ceiling (partial controls 1.11 / 1.13)
# ---------------------------------------------------------------------------


class TestManualGateMaturityCap:
    """A partial control with required in-zone manual-only checks must not
    claim the full zone maturity from a single automated pass while the manual
    gate is unattested.

    Regression for PR #1021 (Codex thread PRRT_kwDOQpaCdc6TAmIt): zone
    thresholds derive ``min_checks_passed`` only from auto-evaluable checks, so
    a lone passing automated check (1.11.a / 1.13.b) previously awarded the full
    zone maturity (zone 2 -> 2, zone 3 -> 4) even though 1.11.b / 1.11.c /
    1.13.a carried no manual evidence. The engine has no per-check manual
    attestation input, so those gates stay ``passed is None`` and the control is
    capped one rung below the full zone target until attestation exists.
    """

    # --- pure compute_maturity unit coverage -------------------------------

    def test_zone2_full_target_capped_when_manual_gate_pending(self):
        score = pytest.importorskip("score")  # type: ignore[import-untyped]
        thresholds = {"zone2": {"min_checks_passed": 1, "maturity_score": 2}}

        capped, label, _ = score.compute_maturity(
            checks_passed=1,
            zone=2,
            zone_thresholds=thresholds,
            unresolved_manual_gates=1,
        )
        assert capped == 1
        assert label == "Aware"

        # Same automated evidence, but with the manual gate resolved, reaches
        # the full zone target — the documented attestation transition.
        full, _, _ = score.compute_maturity(
            checks_passed=1,
            zone=2,
            zone_thresholds=thresholds,
            unresolved_manual_gates=0,
        )
        assert full == 2

    def test_zone3_full_target_capped_when_manual_gates_pending(self):
        score = pytest.importorskip("score")  # type: ignore[import-untyped]
        thresholds = {"zone3": {"min_checks_passed": 1, "maturity_score": 4}}

        capped, label, _ = score.compute_maturity(
            checks_passed=1,
            zone=3,
            zone_thresholds=thresholds,
            unresolved_manual_gates=2,
        )
        assert capped == 3
        assert label == "Optimized"

        full, _, _ = score.compute_maturity(
            checks_passed=1,
            zone=3,
            zone_thresholds=thresholds,
            unresolved_manual_gates=0,
        )
        assert full == 4

    def test_cap_only_lowers_a_would_be_full_award(self):
        """A failing automated threshold stays 0; the cap invents no credit."""
        score = pytest.importorskip("score")  # type: ignore[import-untyped]
        capped, _, _ = score.compute_maturity(
            checks_passed=0,
            zone=3,
            zone_thresholds={"zone3": {"min_checks_passed": 1, "maturity_score": 4}},
            unresolved_manual_gates=2,
        )
        assert capped == 0

    def test_cap_floors_at_zero(self):
        score = pytest.importorskip("score")  # type: ignore[import-untyped]
        capped, label, _ = score.compute_maturity(
            checks_passed=1,
            zone=1,
            zone_thresholds={"zone1": {"min_checks_passed": 1, "maturity_score": 1}},
            unresolved_manual_gates=1,
        )
        assert capped == 0
        assert label == "Not Implemented"

    def test_supported_attestation_overrides_manual_gate_cap(self):
        """An explicit supported_attestation signal is honored, not capped."""
        score = pytest.importorskip("score")  # type: ignore[import-untyped]
        capped, _, _ = score.compute_maturity(
            checks_passed=0,
            zone=3,
            zone_thresholds={
                "zone3": {
                    "min_checks_passed": 0,
                    "maturity_score": 4,
                    "supported_attestation": True,
                }
            },
            unresolved_manual_gates=1,
        )
        assert capped == 4

    def test_auto_only_control_reaches_full_target(self):
        """No manual gates -> full zone target (automated sibling behavior)."""
        score = pytest.importorskip("score")  # type: ignore[import-untyped]
        full, _, _ = score.compute_maturity(
            checks_passed=2,
            zone=3,
            zone_thresholds={"zone3": {"min_checks_passed": 2, "maturity_score": 4}},
            unresolved_manual_gates=0,
        )
        assert full == 4

    # --- end-to-end coverage on the real 1.11 / 1.13 controls --------------

    @staticmethod
    def _real_controls() -> list[dict]:
        real_manifest = ASSESSMENT_ROOT / "manifest" / "controls.json"
        return json.loads(real_manifest.read_text(encoding="utf-8"))

    @staticmethod
    def _run_real(controls: list[dict], collected: Path, tmp_path: Path, zone: int) -> dict:
        score = pytest.importorskip("score")  # type: ignore[import-untyped]
        manifest_path = tmp_path / "controls.json"
        output_path = tmp_path / f"scores{zone}.json"
        write_json(manifest_path, build_manifest_with_controls(controls))
        score.run(
            manifest_path=str(manifest_path),
            collected_dir=str(collected),
            zone=zone,
            output_path=str(output_path),
        )
        result = json.loads(output_path.read_text(encoding="utf-8"))
        return {c["id"]: c for c in result["controls"]}

    @pytest.mark.parametrize("zone,expected,full_target", [(2, 1, 2), (3, 3, 4)])
    def test_control_1_11_cannot_claim_full_maturity_with_manual_gate(
        self,
        tmp_path: Path,
        collected_dir: Path,
        zone: int,
        expected: int,
        full_target: int,
    ):
        # The graph fixture makes 1.11.a (ca_policy_requires_mfa) pass, which
        # alone meets the auto-derived threshold; 1.11.b / 1.11.c carry no
        # attestation, so maturity must be capped below the full zone target.
        by_id = self._run_real(self._real_controls(), collected_dir, tmp_path, zone)
        ctrl = by_id["1.11"]

        assert ctrl["evidence"]["1.11.a"]["result"] == "pass"
        assert ctrl["checks_passed"] == 1
        assert ctrl["maturity_score"] == expected
        assert ctrl["maturity_score"] < full_target
        assert ctrl["needs_manual"] is True

        gates = ["1.11.b"] + (["1.11.c"] if zone == 3 else [])
        chk = {c["check_id"]: c for c in ctrl["checks"]}
        for gate in gates:
            assert chk[gate]["evaluator_state"] == "manual_only"
            assert chk[gate]["passed"] is None
            assert ctrl["evidence"][gate]["source"] is None
        # Automated sibling behavior is preserved.
        assert chk["1.11.a"]["evaluator_state"] == "auto_evaluable"

    @pytest.mark.parametrize("zone,expected,full_target", [(2, 1, 2), (3, 3, 4)])
    def test_control_1_13_cannot_claim_full_maturity_with_manual_gate(
        self,
        tmp_path: Path,
        zone: int,
        expected: int,
        full_target: int,
    ):
        # Build collected data where 1.13.b (dlp_references_sits) passes so the
        # auto threshold is met; 1.13.a is a manual gate with no attestation.
        collected = tmp_path / "collected"
        collected.mkdir()
        for name in ("ppac", "graph", "sharepoint", "sentinel"):
            src = FIXTURES_DIR / f"{name}.json"
            if src.exists():
                write_json(collected / f"{name}.json", load_fixture(f"{name}.json"))
        purview = load_fixture("purview.json")
        purview["dlpCompliancePolicies"] = scoped_policy(
            Name="FSI regulated DLP",
            Enabled=True,
            Rules={
                "Disabled": False,
                "ContentContainsSensitiveInformation": ["CRD Number SIT"],
            },
        )
        write_json(collected / "purview.json", purview)

        by_id = self._run_real(self._real_controls(), collected, tmp_path, zone)
        ctrl = by_id["1.13"]

        assert ctrl["evidence"]["1.13.b"]["result"] == "pass"
        assert ctrl["checks_passed"] == 1
        assert ctrl["maturity_score"] == expected
        assert ctrl["maturity_score"] < full_target
        assert ctrl["needs_manual"] is True

        chk = {c["check_id"]: c for c in ctrl["checks"]}
        assert chk["1.13.a"]["evaluator_state"] == "manual_only"
        assert chk["1.13.a"]["passed"] is None
        assert ctrl["evidence"]["1.13.a"]["source"] is None
        assert chk["1.13.b"]["evaluator_state"] == "auto_evaluable"


# ---------------------------------------------------------------------------
# Test: 1.1.c tenant setting evaluator (fail-closed behavior)
# ---------------------------------------------------------------------------


class TestShareWithEveryoneEvaluator:
    """Control 1.1.c must use tenant disableShareWithEveryone evidence."""

    def test_share_with_everyone_fails_closed_when_tenant_setting_missing(
        self, tmp_path: Path, manifest: dict
    ):
        score = pytest.importorskip("score")  # type: ignore[import-untyped]

        collected = tmp_path / "collected"
        collected.mkdir()

        ppac_data = load_fixture("ppac.json")
        ppac_data.pop("tenantSettings", None)
        write_json(collected / "ppac.json", ppac_data)

        graph_data = load_fixture("graph_collector_contract.json")
        write_json(collected / "graph.json", graph_data)

        for name in ("purview", "sharepoint", "sentinel"):
            write_json(collected / f"{name}.json", load_fixture(f"{name}.json"))

        manifest_path = tmp_path / "controls.json"
        output_path = tmp_path / "scores.json"
        write_json(manifest_path, manifest)

        score.run(
            manifest_path=str(manifest_path),
            collected_dir=str(collected),
            zone=3,
            output_path=str(output_path),
        )

        result = json.loads(output_path.read_text(encoding="utf-8"))
        ctrl = next(c for c in result["controls"] if c["id"] == "1.1")

        assert ctrl["evidence"]["1.1.c"]["result"] == "fail"
        assert "fail closed" in ctrl["evidence"]["1.1.c"]["value"]
        assert ctrl["maturity_score"] == 0


# ---------------------------------------------------------------------------
# Test: 1.7.b audit plan evaluator (Graph subscribed SKU evidence)
# ---------------------------------------------------------------------------


class TestAuditPlanTierEvaluator:
    """Control 1.7.b must fail closed unless per-user entitlement is proven."""

    @staticmethod
    def _audit_control_manifest() -> dict:
        return build_manifest_with_controls(
            [
                {
                    "id": "1.7",
                    "title": "Control 1.7: Comprehensive Audit Logging and Compliance",
                    "pillar": 1,
                    "pillar_name": "Security",
                    "source_file": "docs/controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md",
                    "automation": "full",
                    "collection_methods": ["Purview_PowerShell", "Graph_API"],
                    "checks": [
                        {
                            "check_id": "1.7.a",
                            "description": "Unified audit logging enabled",
                            "api_call": "Get-AdminAuditLogConfig",
                            "pass_condition": "audit_log_enabled",
                            "zone_required": [1, 2, 3],
                        },
                        {
                            "check_id": "1.7.b",
                            "description": "M365 Audit plan tier is E5 or equivalent",
                            "api_call": "Get-MgSubscribedSku",
                            "pass_condition": "audit_plan_tier_adequate",
                            "zone_required": [2, 3],
                        },
                    ],
                    "zone_thresholds": {
                        "zone1": {"min_checks_passed": 1, "maturity_score": 1},
                        "zone2": {"min_checks_passed": 2, "maturity_score": 2},
                        "zone3": {"min_checks_passed": 2, "maturity_score": 4},
                    },
                    "manual_question": None,
                }
            ]
        )

    def test_audit_plan_tier_requires_manual_verification_with_e5_sku(
        self, tmp_path: Path
    ):
        score = pytest.importorskip("score")  # type: ignore[import-untyped]

        collected = tmp_path / "collected"
        collected.mkdir()
        write_json(collected / "ppac.json", load_fixture("ppac.json"))
        write_json(collected / "purview.json", load_fixture("purview.json"))
        write_json(collected / "sharepoint.json", load_fixture("sharepoint.json"))
        write_json(collected / "sentinel.json", load_fixture("sentinel.json"))
        write_json(
            collected / "graph.json",
            load_fixture("graph_collector_contract.json"),
        )

        manifest_path = tmp_path / "controls-1.7.json"
        output_path = tmp_path / "scores.json"
        write_json(manifest_path, self._audit_control_manifest())

        score.run(
            manifest_path=str(manifest_path),
            collected_dir=str(collected),
            zone=2,
            output_path=str(output_path),
        )

        result = json.loads(output_path.read_text(encoding="utf-8"))
        ctrl = next(c for c in result["controls"] if c["id"] == "1.7")

        assert ctrl["evidence"]["1.7.b"]["result"] == "unknown"
        assert "SPE_E5" in ctrl["evidence"]["1.7.b"]["value"]
        assert "Manual per-user verification required" in ctrl["evidence"]["1.7.b"]["value"]
        assert ctrl["maturity_score"] == 0
        assert ctrl["confidence"] == "medium"

    @pytest.mark.parametrize("zone", [2, 3])
    def test_audit_plan_tier_one_e5_many_e3_copilot_still_unknown(
        self, tmp_path: Path, zone: int
    ):
        score = pytest.importorskip("score")  # type: ignore[import-untyped]

        collected = tmp_path / f"collected-zone{zone}"
        collected.mkdir()
        write_json(collected / "ppac.json", load_fixture("ppac.json"))
        write_json(collected / "purview.json", load_fixture("purview.json"))
        write_json(collected / "sharepoint.json", load_fixture("sharepoint.json"))
        write_json(collected / "sentinel.json", load_fixture("sentinel.json"))

        graph_data = load_fixture("graph.json")
        graph_data["subscribedSkus"] = [
            {
                "SkuId": "06ebc4ee-1bb5-47dd-8120-11324bc54e06",
                "SkuPartNumber": "SPE_E5",
                "CapabilityStatus": "Enabled",
                "ConsumedUnits": 1,
                "PrepaidUnits": {"Enabled": 1, "Suspended": 0, "Warning": 0},
            },
            {
                "SkuId": "6fd2c87f-b296-42f0-b197-1e91e994b900",
                "SkuPartNumber": "ENTERPRISEPACK",
                "CapabilityStatus": "Enabled",
                "ConsumedUnits": 800,
                "PrepaidUnits": {"Enabled": 1200, "Suspended": 0, "Warning": 0},
            },
            {
                "SkuId": "a403ebcc-fae0-4ca2-8c8c-7a907fd6c235",
                "SkuPartNumber": "MICROSOFT_COPILOT_STUDIO_VIRAL",
                "CapabilityStatus": "Enabled",
                "ConsumedUnits": 600,
                "PrepaidUnits": {"Enabled": 1000, "Suspended": 0, "Warning": 0},
            },
            {
                "SkuId": "c7df2760-2c81-4ef7-b578-5b5392b571df",
                "SkuPartNumber": "MCOMEETADV",
                "CapabilityStatus": "Enabled",
                "ConsumedUnits": 250,
                "PrepaidUnits": {"Enabled": 500, "Suspended": 0, "Warning": 0},
            },
        ]
        write_json(collected / "graph.json", graph_data)

        manifest_path = tmp_path / f"controls-1.7-zone{zone}.json"
        output_path = tmp_path / f"scores-zone{zone}.json"
        write_json(manifest_path, self._audit_control_manifest())

        score.run(
            manifest_path=str(manifest_path),
            collected_dir=str(collected),
            zone=zone,
            output_path=str(output_path),
        )

        result = json.loads(output_path.read_text(encoding="utf-8"))
        ctrl = next(c for c in result["controls"] if c["id"] == "1.7")

        assert ctrl["evidence"]["1.7.b"]["result"] == "unknown"
        assert "SPE_E5" in ctrl["evidence"]["1.7.b"]["value"]
        assert "Manual per-user verification required" in ctrl["evidence"]["1.7.b"]["value"]
        assert ctrl["checks_passed"] == 1
        assert ctrl["maturity_score"] == 0
        assert ctrl["confidence"] == "medium"

    def test_audit_plan_tier_fails_closed_when_sku_evidence_missing(
        self, tmp_path: Path
    ):
        score = pytest.importorskip("score")  # type: ignore[import-untyped]

        collected = tmp_path / "collected"
        collected.mkdir()
        write_json(collected / "ppac.json", load_fixture("ppac.json"))
        write_json(collected / "purview.json", load_fixture("purview.json"))
        write_json(collected / "sharepoint.json", load_fixture("sharepoint.json"))
        write_json(collected / "sentinel.json", load_fixture("sentinel.json"))

        graph_data = load_fixture("graph.json")
        graph_data.pop("subscribedSkus", None)
        write_json(collected / "graph.json", graph_data)

        manifest_path = tmp_path / "controls-1.7.json"
        output_path = tmp_path / "scores.json"
        write_json(manifest_path, self._audit_control_manifest())

        score.run(
            manifest_path=str(manifest_path),
            collected_dir=str(collected),
            zone=2,
            output_path=str(output_path),
        )

        result = json.loads(output_path.read_text(encoding="utf-8"))
        ctrl = next(c for c in result["controls"] if c["id"] == "1.7")

        assert ctrl["evidence"]["1.7.b"]["result"] == "fail"
        assert "not collected" in ctrl["evidence"]["1.7.b"]["value"]
        assert "fail closed" in ctrl["evidence"]["1.7.b"]["value"]
        assert ctrl["confidence"] == "high"
        assert ctrl["maturity_score"] == 0

    def test_audit_plan_tier_fails_closed_when_sku_evidence_ambiguous(
        self, tmp_path: Path
    ):
        score = pytest.importorskip("score")  # type: ignore[import-untyped]

        collected = tmp_path / "collected"
        collected.mkdir()
        write_json(collected / "ppac.json", load_fixture("ppac.json"))
        write_json(collected / "purview.json", load_fixture("purview.json"))
        write_json(collected / "sharepoint.json", load_fixture("sharepoint.json"))
        write_json(collected / "sentinel.json", load_fixture("sentinel.json"))

        graph_data = load_fixture("graph.json")
        graph_data["subscribedSkus"] = [
            {
                "SkuId": "06ebc4ee-1bb5-47dd-8120-11324bc54e06",
                "SkuPartNumber": "SPE_E5",
                "CapabilityStatus": "Enabled",
                "ConsumedUnits": 1,
                "PrepaidUnits": {"Enabled": None, "Suspended": 0, "Warning": 0},
            }
        ]
        write_json(collected / "graph.json", graph_data)

        manifest_path = tmp_path / "controls-1.7.json"
        output_path = tmp_path / "scores.json"
        write_json(manifest_path, self._audit_control_manifest())

        score.run(
            manifest_path=str(manifest_path),
            collected_dir=str(collected),
            zone=2,
            output_path=str(output_path),
        )

        result = json.loads(output_path.read_text(encoding="utf-8"))
        ctrl = next(c for c in result["controls"] if c["id"] == "1.7")

        assert ctrl["evidence"]["1.7.b"]["result"] == "fail"
        assert "ambiguous/insufficient" in ctrl["evidence"]["1.7.b"]["value"]
        assert "fail closed" in ctrl["evidence"]["1.7.b"]["value"]
        assert ctrl["confidence"] == "high"
        assert ctrl["maturity_score"] == 0


# ---------------------------------------------------------------------------
# Test: 1.13.b DLP SIT reference evaluator
# ---------------------------------------------------------------------------


class TestDlpReferencesSitsEvaluator:
    """Control 1.13.b passes only for enforced, Copilot-scoped policies with
    active SIT rules (Microsoft Learn New-DlpCompliancePolicy Example 4 / control
    1.13 powershell-setup.md §9)."""

    @staticmethod
    def _evaluate(policies):
        score = pytest.importorskip("score")  # type: ignore[import-untyped]
        return score._eval_dlp_references_sits(  # noqa: SLF001
            {"purview": {"dlpCompliancePolicies": policies}},
            None,
        )

    def test_dlp_references_sits_passes_with_enforced_sit_conditions(self):
        purview = load_fixture("purview_collector_contract.json")
        passed, evidence = self._evaluate(purview["dlpCompliancePolicies"])

        assert passed is True
        assert "Copilot-scoped" in evidence
        assert "reference" in evidence.lower()
        assert "sit" in evidence.lower()

    def test_dlp_references_sits_accepts_singleton_policy_and_rule_dicts(self):
        passed, evidence = self._evaluate(
            scoped_policy(
                Name="Singleton policy and rule",
                Enabled=True,
                Rules={
                    "Disabled": False,
                    "ContentContainsSensitiveInformation": ["Test SIT"],
                },
            )
        )

        assert passed is True
        assert "Test SIT" in evidence

    def test_dlp_references_sits_accepts_singleton_policy_with_rule_list(self):
        passed, evidence = self._evaluate(
            scoped_policy(
                Name="Singleton policy",
                Enabled=True,
                Rules=[
                    {
                        "Disabled": False,
                        "ContentContainsSensitiveInformation": ["Test SIT"],
                    }
                ],
            )
        )

        assert passed is True
        assert "Test SIT" in evidence

    def test_dlp_references_sits_accepts_policy_list_with_singleton_rule_dict(self):
        passed, evidence = self._evaluate(
            [
                scoped_policy(
                    Name="Singleton rule",
                    Enabled=True,
                    Rules={
                        "Disabled": False,
                        "ContentContainsSensitiveInformation": ["Test SIT"],
                    },
                )
            ]
        )

        assert passed is True
        assert "Test SIT" in evidence

    def test_dlp_references_sits_accepts_singleton_sit_condition_dict(self):
        # The Purview collector can serialize exactly one
        # ContentContainsSensitiveInformation condition as a bare object
        # (PowerShell singleton-collapse) instead of a one-element array. An
        # enforced one-SIT policy must still pass rather than fail closed.
        passed, evidence = self._evaluate(
            scoped_policy(
                Name="Enforced one-SIT policy",
                Enabled=True,
                Rules=[
                    {
                        "Disabled": False,
                        "ContentContainsSensitiveInformation": {"Name": "Test SIT"},
                    }
                ],
            )
        )

        assert passed is True
        assert "Test SIT" in evidence

    def test_dlp_references_sits_accepts_singleton_sit_condition_dict_all_the_way_down(
        self,
    ):
        # Singleton collapse can occur simultaneously at the policy, rule and
        # SIT-condition levels; all three normalizations must compose.
        passed, evidence = self._evaluate(
            scoped_policy(
                Name="Fully collapsed singleton",
                Enabled=True,
                Rules={
                    "Disabled": False,
                    "ContentContainsSensitiveInformation": {"Name": "Test SIT"},
                },
            )
        )

        assert passed is True
        assert "Test SIT" in evidence

    # -- Copilot-scope gate (P1, PRRT_kwDOQpaCdc6TDHOI) ---------------------

    def test_dlp_references_sits_does_not_infer_scope_from_name_or_workload(self):
        # An Exchange/SharePoint SIT policy — even one named "Copilot ..." — is
        # not Copilot-scoped and must FAIL 1.13.b. Scope is structural, never
        # inferred from the policy name or an unrelated workload string.
        policy = {
            "Name": "Copilot Data Loss Prevention",
            "Mode": "Enable",
            "Enabled": True,
            "Workload": "Exchange,SharePoint",
            "Rules": [
                {
                    "Disabled": False,
                    "ContentContainsSensitiveInformation": ["Test SIT"],
                }
            ],
        }

        passed, evidence = self._evaluate([policy])

        assert passed is False
        assert "copilot-scoped" in evidence.lower()
        assert "Test SIT" not in evidence

    def test_dlp_references_sits_passes_when_fully_copilot_scoped(self):
        passed, evidence = self._evaluate(
            [scoped_policy(Enabled=True, Rules=[direct_sit_rule("CRD Number SIT")])]
        )

        assert passed is True
        assert "CRD Number SIT" in evidence
        assert "Copilot-scoped" in evidence

    @pytest.mark.parametrize("dropped", ["Workload", "EnforcementPlanes", "Locations"])
    def test_dlp_references_sits_fails_when_a_scope_signal_is_missing(self, dropped):
        # Each of the three documented signals is individually required; drop any
        # one and an otherwise-enforced SIT policy must fail closed.
        policy = scoped_policy(Enabled=True, Rules=[direct_sit_rule("Test SIT")])
        del policy[dropped]

        passed, evidence = self._evaluate([policy])

        assert passed is False
        assert "copilot-scoped" in evidence.lower()

    @pytest.mark.parametrize(
        "workload",
        ["Exchange", "Exchange,SharePoint", "SharePoint,OneDriveForBusiness,Teams"],
    )
    def test_dlp_references_sits_fails_for_non_applications_workload(self, workload):
        policy = scoped_policy(Enabled=True, Rules=[direct_sit_rule("Test SIT")])
        policy["Workload"] = workload

        passed, evidence = self._evaluate([policy])

        assert passed is False
        assert "copilot-scoped" in evidence.lower()

    @pytest.mark.parametrize(
        "planes",
        [["Browser"], ["Application"], ["Network"], "Browser", []],
    )
    def test_dlp_references_sits_fails_for_non_copilot_enforcement_plane(self, planes):
        policy = scoped_policy(Enabled=True, Rules=[direct_sit_rule("Test SIT")])
        policy["EnforcementPlanes"] = planes

        passed, evidence = self._evaluate([policy])

        assert passed is False
        assert "copilot-scoped" in evidence.lower()

    def test_dlp_references_sits_fails_when_location_guid_absent(self):
        policy = scoped_policy(Enabled=True, Rules=[direct_sit_rule("Test SIT")])
        policy["Locations"] = [
            {
                "Workload": "Applications",
                "Location": "00000000-0000-0000-0000-000000000000",
            }
        ]

        passed, evidence = self._evaluate([policy])

        assert passed is False
        assert "copilot-scoped" in evidence.lower()

    def test_dlp_references_sits_ignores_copilot_guid_in_inclusion_identity(self):
        # A decoy: the Copilot GUID appears only as an Inclusions *Identity*, not
        # as a Location. Structural matching must not treat that as a Copilot
        # binding (no false positive from Inclusions/Exclusions or nested values).
        policy = scoped_policy(Enabled=True, Rules=[direct_sit_rule("Test SIT")])
        policy["Locations"] = [
            {
                "Workload": "Applications",
                "Location": "11111111-1111-1111-1111-111111111111",
                "Inclusions": [{"Type": "Group", "Identity": COPILOT_LOCATION_GUID}],
            }
        ]

        passed, evidence = self._evaluate([policy])

        assert passed is False
        assert "copilot-scoped" in evidence.lower()

    def test_dlp_references_sits_ignores_copilot_guid_in_unrelated_nested_value(self):
        # The GUID buried in an unrelated rule payload is not a location binding.
        policy = scoped_policy(
            Enabled=True,
            Rules=[
                {
                    "Disabled": False,
                    "ContentContainsSensitiveInformation": ["Test SIT"],
                    "Comment": f"related to location {COPILOT_LOCATION_GUID}",
                }
            ],
        )
        policy["Locations"] = [
            {"Workload": "Applications", "Location": "not-the-copilot-location"}
        ]

        passed, evidence = self._evaluate([policy])

        assert passed is False
        assert "copilot-scoped" in evidence.lower()

    def test_dlp_references_sits_scoped_policy_credited_beside_exchange_policy(self):
        # An unscoped Exchange SIT policy must never contribute; only the
        # genuinely Copilot-scoped policy is credited.
        exchange = {
            "Name": "Exchange DLP",
            "Mode": "Enable",
            "Enabled": True,
            "Workload": "Exchange",
            "Rules": [direct_sit_rule("Exchange Only SIT")],
        }
        copilot = scoped_policy(
            Name="Copilot DLP", Enabled=True, Rules=[direct_sit_rule("Copilot SIT")]
        )

        passed, evidence = self._evaluate([exchange, copilot])

        assert passed is True
        assert "Copilot SIT" in evidence
        assert "Exchange Only SIT" not in evidence
        assert "across 1 policy/policies" in evidence

    # -- Documented singleton / string scope shapes -------------------------

    def test_dlp_references_sits_accepts_singleton_scope_shapes(self):
        # ConvertTo-Json collapses a one-element EnforcementPlanes array to a
        # scalar and a one-element Locations array to a bare object.
        policy = scoped_policy(Enabled=True, Rules=[direct_sit_rule("Test SIT")])
        policy["EnforcementPlanes"] = "CopilotExperiences"
        policy["Locations"] = {
            "Workload": "Applications",
            "Location": COPILOT_LOCATION_GUID,
        }

        passed, evidence = self._evaluate([policy])

        assert passed is True
        assert "Test SIT" in evidence

    def test_dlp_references_sits_accepts_locations_as_json_string(self):
        # The raw -Locations input is a JSON string; accept a captured string too.
        policy = scoped_policy(Enabled=True, Rules=[direct_sit_rule("Test SIT")])
        policy["Locations"] = json.dumps(
            [{"Workload": "Applications", "Location": COPILOT_LOCATION_GUID}]
        )

        passed, evidence = self._evaluate([policy])

        assert passed is True
        assert "Test SIT" in evidence

    # -- SIT-condition and rule handling (under valid scope) ----------------

    @pytest.mark.parametrize(
        "sit_condition",
        ["Test SIT", 1, True, None, {}, {"minCount": 1}],
    )
    def test_dlp_references_sits_rejects_scalar_or_nameless_sit_conditions(
        self, sit_condition
    ):
        # A scalar / null / nameless SIT-condition payload must stay
        # conservative: no SIT is extracted, so an otherwise-enforced (and
        # Copilot-scoped) policy fails closed rather than being credited with a
        # phantom SIT.
        passed, evidence = self._evaluate(
            scoped_policy(
                Name="Enforced with malformed condition",
                Enabled=True,
                Rules=[
                    {
                        "Disabled": False,
                        "ContentContainsSensitiveInformation": sit_condition,
                    }
                ],
            )
        )

        assert passed is False
        assert "fail closed" in evidence.lower()

    @pytest.mark.parametrize(
        "override",
        [
            {"Mode": "TestWithNotifications"},
            {"Enabled": False},
            {"Rules": [{"Disabled": False, "ContentContainsSensitiveInformation": []}]},
        ],
    )
    def test_dlp_references_sits_rejects_nonqualifying_singleton_policies(
        self, override
    ):
        policy = scoped_policy(
            Name="Nonqualifying",
            Enabled=True,
            Rules={
                "Disabled": False,
                "ContentContainsSensitiveInformation": ["Test SIT"],
            },
        )
        policy.update(override)

        passed, evidence = self._evaluate(policy)

        assert passed is False
        assert "fail closed" in evidence.lower()

    @pytest.mark.parametrize("mode", ["TestWithNotifications", "Audit", "Disable", None])
    def test_dlp_references_sits_rejects_non_enforced_or_missing_mode(self, mode):
        policy = scoped_policy(
            Name="Not enforced",
            Enabled=True,
            Rules=[direct_sit_rule("Test SIT")],
        )
        policy.pop("Mode", None)
        if mode is not None:
            policy["Mode"] = mode

        passed, evidence = self._evaluate([policy])

        assert passed is False
        assert "copilot-scoped" in evidence.lower()
        assert "fail closed" in evidence.lower()

    # -- Enabled truth table (P2, PRRT_kwDOQpaCdc6TDHOR) --------------------

    def test_dlp_references_sits_qualifies_when_enabled_absent(self):
        # Get-DlpCompliancePolicy has no reliable Enabled Boolean; a Mode=Enable
        # policy with no Enabled key stays qualifying (Mode governs).
        policy = scoped_policy(Rules=[direct_sit_rule("Test SIT")])
        assert "Enabled" not in policy

        passed, evidence = self._evaluate([policy])

        assert passed is True
        assert "Test SIT" in evidence

    def test_dlp_references_sits_qualifies_when_enabled_null(self):
        passed, evidence = self._evaluate(
            [scoped_policy(Enabled=None, Rules=[direct_sit_rule("Test SIT")])]
        )

        assert passed is True
        assert "Test SIT" in evidence

    def test_dlp_references_sits_qualifies_when_enabled_true(self):
        passed, evidence = self._evaluate(
            [scoped_policy(Enabled=True, Rules=[direct_sit_rule("Test SIT")])]
        )

        assert passed is True
        assert "Test SIT" in evidence

    def test_dlp_references_sits_rejects_explicit_false_enabled(self):
        # An explicit strict boolean False disables the policy: reject it.
        passed, evidence = self._evaluate(
            [scoped_policy(Enabled=False, Rules=[direct_sit_rule("Test SIT")])]
        )

        assert passed is False
        assert "copilot-scoped" in evidence.lower()
        assert "Test SIT" not in evidence

    @pytest.mark.parametrize(
        "enabled",
        ["false", "true", "True", "yes", 0, 1, 3.14, {}, [], {"v": 1}],
    )
    def test_dlp_references_sits_treats_malformed_enabled_conservatively(
        self, enabled
    ):
        # A present but non-boolean Enabled value is uninterpretable: the policy
        # is not credited and the evidence is reported malformed (fail closed),
        # never silently accepted.
        passed, evidence = self._evaluate(
            [scoped_policy(Enabled=enabled, Rules=[direct_sit_rule("Test SIT")])]
        )

        assert passed is False
        assert "malformed" in evidence.lower()
        assert "Test SIT" not in evidence

    def test_dlp_references_sits_missing_enabled_does_not_fail_valid_policy(self):
        # Regression guard for P2: a valid scoped policy must not flip to fail
        # merely because Enabled is absent or null.
        for enabled_state in ("absent", "null"):
            policy = scoped_policy(Rules=[direct_sit_rule("Test SIT")])
            if enabled_state == "null":
                policy["Enabled"] = None
            passed, _ = self._evaluate([policy])
            assert passed is True, enabled_state

    # -- Empty / null and malformed contracts (preserved) -------------------

    def test_dlp_references_sits_fails_closed_when_no_sit_conditions(self):
        policy = scoped_policy(
            Name="Enforced without SIT",
            Enabled=True,
            Rules=[{"Disabled": False, "ContentContainsSensitiveInformation": []}],
        )

        passed, evidence = self._evaluate([policy])

        assert passed is False
        assert "fail closed" in evidence.lower()

    def test_dlp_references_sits_fails_when_rules_list_empty(self):
        # A *successfully collected* empty rule set ([]) on an enforced,
        # Copilot-scoped policy scores fail (absence affirmatively observed), not
        # unknown.
        policy = scoped_policy(
            Name="Enforced, zero collected rules", Enabled=True, Rules=[]
        )

        passed, evidence = self._evaluate([policy])

        assert passed is False
        assert "fail closed" in evidence.lower()

    def test_dlp_references_sits_empty_rules_singleton_policy_fails(self):
        passed, evidence = self._evaluate(
            scoped_policy(
                Name="Singleton enforced, empty rules", Enabled=True, Rules=[]
            )
        )

        assert passed is False
        assert "fail closed" in evidence.lower()

    def test_dlp_references_sits_empty_rules_is_fail_but_null_is_unknown(self):
        # Empty-collected ([] -> fail) and uncollected (null -> unknown) rule sets
        # must resolve to DIFFERENT outcomes on an enforced, Copilot-scoped policy.
        enforced = scoped_policy(Name="Enforced", Enabled=True)

        empty_passed, empty_evidence = self._evaluate([{**enforced, "Rules": []}])
        null_passed, null_evidence = self._evaluate([{**enforced, "Rules": None}])

        assert empty_passed is False
        assert "fail closed" in empty_evidence.lower()
        assert null_passed is None
        assert "not collected" in null_evidence.lower()
        assert empty_passed != null_passed

    def test_dlp_references_sits_empty_policy_list_is_fail_but_null_is_unknown(self):
        # A *successfully collected* empty POLICY set ([]) affirmatively observes
        # "no DLP policies exist" and scores fail; a genuinely uncollected (null)
        # set stays unknown. The two must resolve to DIFFERENT outcomes.
        empty_passed, empty_evidence = self._evaluate([])
        null_passed, null_evidence = self._evaluate(None)

        assert empty_passed is False
        assert "fail closed" in empty_evidence.lower()
        assert (
            "no enforced, copilot-scoped dlp compliance policies"
            in empty_evidence.lower()
        )
        assert null_passed is None
        assert "not collected" in null_evidence.lower()
        assert empty_passed != null_passed

    @pytest.mark.parametrize("policies", ["not-a-policy", 1, True])
    def test_dlp_references_sits_rejects_scalar_policy_values(self, policies):
        passed, evidence = self._evaluate(policies)

        assert passed is False
        assert "malformed" in evidence.lower()

    @pytest.mark.parametrize("rules", ["not-rules", 1, True])
    def test_dlp_references_sits_rejects_scalar_rule_values(self, rules):
        passed, evidence = self._evaluate(
            scoped_policy(Name="Scalar rules", Enabled=True, Rules=rules)
        )

        assert passed is False
        assert "malformed" in evidence.lower()

    def test_dlp_references_sits_fails_closed_on_non_dict_policy(self):
        passed, evidence = self._evaluate(["not-a-policy"])

        assert passed is False
        assert "malformed" in evidence.lower()

    @pytest.mark.parametrize(
        "rules",
        [["not-a-rule"], {"nested": {"Disabled": False}}],
    )
    def test_dlp_references_sits_fails_closed_on_malformed_rule_shapes(self, rules):
        passed, evidence = self._evaluate(
            [scoped_policy(Name="Malformed rule", Enabled=True, Rules=rules)]
        )

        assert passed is False
        assert "malformed" in evidence.lower()

    def test_dlp_references_sits_is_unknown_when_rule_collection_failed(self):
        passed, evidence = self._evaluate(
            scoped_policy(Name="Enforced", Enabled=True, Rules=None)
        )

        assert passed is None
        assert "not collected" in evidence.lower()

    def test_dlp_references_sits_is_unknown_when_policy_collection_missing(self):
        score = pytest.importorskip("score")  # type: ignore[import-untyped]

        passed, evidence = score._eval_dlp_references_sits(  # noqa: SLF001
            {"purview": {"audit_config": {}}},
            None,
        )

        assert passed is None
        assert "not collected" in evidence.lower()

    def test_dlp_references_sits_is_unknown_when_purview_missing(self):
        score = pytest.importorskip("score")  # type: ignore[import-untyped]

        passed, evidence = score._eval_dlp_references_sits(  # noqa: SLF001
            {"purview": None},
            None,
        )

        assert passed is None
        assert "not available" in evidence.lower()

# ---------------------------------------------------------------------------
# Test: 1.13.b grouped SIT condition parsing
#   Purview DLP rules built from an AdvancedRule grouped SIT match serialize as
#   ContentContainsSensitiveInformation.groups[].sensitivetypes[].name — see
#   docs/playbooks/control-implementations/1.13/powershell-setup.md (control
#   4.7's playbook reads the live .groups property). The parser must credit
#   these without breaking direct top-level Name support or failing closed on
#   malformed structures.
# ---------------------------------------------------------------------------


class TestExtractSitReferencesGroupedShapes:
    """_extract_sit_references parses grouped SIT conditions as well as the
    pre-existing direct top-level Name / string shapes."""

    @staticmethod
    def _extract(rule):
        score = pytest.importorskip("score")  # type: ignore[import-untyped]
        return score._extract_sit_references(rule)  # noqa: SLF001

    @staticmethod
    def _rule(condition):
        return {"Disabled": False, "ContentContainsSensitiveInformation": condition}

    def test_grouped_list_shape(self):
        rule = self._rule(
            {
                "groups": [
                    {
                        "name": "FSI-MNPI-Group",
                        "operator": "Or",
                        "sensitivetypes": [
                            {
                                "name": "CRD Number SIT",
                                "confidencelevel": "High",
                                "mincount": 1,
                            },
                            {"Name": "MNPI Keyword SIT"},
                        ],
                    }
                ]
            }
        )
        assert self._extract(rule) == {"CRD Number SIT", "MNPI Keyword SIT"}

    def test_singleton_group_dict(self):
        # ConvertTo-Json collapses a one-element groups array to a bare object.
        rule = self._rule(
            {
                "groups": {
                    "name": "FSI-MNPI-Group",
                    "operator": "Or",
                    "sensitivetypes": [{"name": "CRD Number SIT"}],
                }
            }
        )
        assert self._extract(rule) == {"CRD Number SIT"}

    def test_singleton_sensitivetype_dict(self):
        # ConvertTo-Json collapses a one-element sensitivetypes array too.
        rule = self._rule(
            {
                "groups": [
                    {
                        "name": "FSI-MNPI-Group",
                        "sensitivetypes": {"name": "CRD Number SIT"},
                    }
                ]
            }
        )
        assert self._extract(rule) == {"CRD Number SIT"}

    def test_fully_collapsed_group_and_sensitivetype(self):
        # Singleton collapse can occur at the group and sensitivetype levels
        # simultaneously; both normalizations must compose.
        rule = self._rule(
            {"groups": {"name": "G", "sensitivetypes": {"Name": "CRD Number SIT"}}}
        )
        assert self._extract(rule) == {"CRD Number SIT"}

    def test_mixed_valid_and_malformed_sensitivetypes(self):
        # Only structurally valid named dict entries are extracted; blank names,
        # nameless/empty dicts, nulls and bare scalars contribute nothing.
        rule = self._rule(
            {
                "groups": [
                    {
                        "name": "G",
                        "sensitivetypes": [
                            {"name": "Valid SIT"},
                            {"Name": "   "},
                            {"mincount": 1},
                            {},
                            None,
                            "U.S. SSN",
                            42,
                        ],
                    }
                ]
            }
        )
        assert self._extract(rule) == {"Valid SIT"}

    def test_group_label_name_is_not_extracted(self):
        # The group's own name is a label, not a SIT, and must not be credited.
        rule = self._rule(
            {
                "groups": [
                    {"name": "FSI-MNPI-Group", "sensitivetypes": [{"name": "Real SIT"}]}
                ]
            }
        )
        assert self._extract(rule) == {"Real SIT"}

    @pytest.mark.parametrize(
        "condition",
        [
            {"groups": "not-a-list"},
            {"groups": 1},
            {"groups": True},
            {"groups": None},
            {"groups": []},
            {"groups": [None, 42, "x"]},
            {"groups": [{}]},
            {"groups": [{"operator": "Or"}]},
            {"groups": [{"sensitivetypes": "not-a-list"}]},
            {"groups": [{"sensitivetypes": 1}]},
            {"groups": [{"sensitivetypes": []}]},
            {"groups": [{"sensitivetypes": [None, 1, "x", {}, {"mincount": 1}]}]},
        ],
    )
    def test_fully_malformed_grouped_structures_yield_no_names(self, condition):
        assert self._extract(self._rule(condition)) == set()

    def test_coexistence_direct_top_level_and_grouped_in_one_list(self):
        # A ContentContainsSensitiveInformation list can carry a direct
        # top-level Name entry alongside a grouped-condition object; both
        # surface.
        rule = self._rule(
            [
                {"Name": "Direct SIT"},
                {"groups": [{"name": "G", "sensitivetypes": [{"name": "Grouped SIT"}]}]},
            ]
        )
        assert self._extract(rule) == {"Direct SIT", "Grouped SIT"}

    def test_direct_top_level_shapes_unchanged(self):
        # Regression guard: pre-existing direct shapes keep working untouched.
        assert self._extract(self._rule([{"Name": "Direct SIT"}])) == {"Direct SIT"}
        assert self._extract(self._rule(["String SIT"])) == {"String SIT"}
        assert self._extract(self._rule({"Name": "Singleton SIT"})) == {"Singleton SIT"}
        assert self._extract(self._rule({"minCount": 1})) == set()
        assert self._extract(self._rule("scalar")) == set()


class TestDlpReferencesSitsGroupedEvaluator:
    """End-to-end _eval_dlp_references_sits behavior for grouped SIT rules under
    a valid Copilot scope."""

    @staticmethod
    def _evaluate(policies):
        score = pytest.importorskip("score")  # type: ignore[import-untyped]
        return score._eval_dlp_references_sits(  # noqa: SLF001
            {"purview": {"dlpCompliancePolicies": policies}},
            None,
        )

    @staticmethod
    def _policy(rules):
        return [scoped_policy(Enabled=True, Rules=rules)]

    def test_enforced_grouped_rule_passes(self):
        passed, evidence = self._evaluate(
            self._policy(
                [
                    {
                        "Disabled": False,
                        "ContentContainsSensitiveInformation": {
                            "groups": [
                                {
                                    "name": "FSI-MNPI-Group",
                                    "operator": "Or",
                                    "sensitivetypes": [
                                        {
                                            "name": "CRD Number SIT",
                                            "confidencelevel": "High",
                                            "mincount": 1,
                                        }
                                    ],
                                }
                            ]
                        },
                    }
                ]
            )
        )

        assert passed is True
        assert "CRD Number SIT" in evidence

    def test_enforced_grouped_rule_without_valid_names_fails_closed(self):
        passed, evidence = self._evaluate(
            self._policy(
                [
                    {
                        "Disabled": False,
                        "ContentContainsSensitiveInformation": {
                            "groups": [{"sensitivetypes": [{}]}]
                        },
                    }
                ]
            )
        )

        assert passed is False
        assert "fail closed" in evidence.lower()

    def test_grouped_and_direct_rules_credited_together(self):
        passed, evidence = self._evaluate(
            self._policy(
                [
                    {
                        "Disabled": False,
                        "ContentContainsSensitiveInformation": ["Direct SIT"],
                    },
                    {
                        "Disabled": False,
                        "ContentContainsSensitiveInformation": {
                            "groups": [
                                {
                                    "name": "G",
                                    "sensitivetypes": [{"name": "Grouped SIT"}],
                                }
                            ]
                        },
                    },
                ]
            )
        )

        assert passed is True
        assert "Direct SIT" in evidence
        assert "Grouped SIT" in evidence


# ---------------------------------------------------------------------------
# Test: 1.13.b AdvancedRule-backed SIT condition parsing
#   Control 1.13 binds SITs to the Copilot workload via
#   New-DlpComplianceRule -AdvancedRule (a JSON string), not
#   -ContentContainsSensitiveInformation — see
#   docs/playbooks/control-implementations/1.13/powershell-setup.md §9 and
#   troubleshooting.md, plus control 1.5's AdvancedRule/SubConditions parse. The
#   evaluator must credit these as a fallback, extract SIT names only from
#   ContentContainsSensitiveInformation subconditions (never from a sibling
#   ContentContainsSensitivityLabel, group label, or arbitrary Name), and fail
#   closed on malformed or unrelated payloads.
# ---------------------------------------------------------------------------


def _advanced_rule(*sit_names, condition_name="ContentContainsSensitiveInformation"):
    """Build the grounded AdvancedRule document (dict) for the given SIT names.

    Mirrors New-FsiCopilotDlpPolicy.ps1 §9: a Version-1 Condition whose
    SubConditions carry a grouped ContentContainsSensitiveInformation match.
    """
    return {
        "Version": "1.0",
        "Condition": {
            "Operator": "And",
            "SubConditions": [
                {
                    "ConditionName": condition_name,
                    "Value": {
                        "groups": [
                            {
                                "name": "FSI-MNPI-Group",
                                "operator": "Or",
                                "sensitivetypes": [
                                    {
                                        "name": sit,
                                        "confidencelevel": "High",
                                        "mincount": 1,
                                    }
                                    for sit in sit_names
                                ],
                            }
                        ]
                    },
                }
            ],
        },
    }


class TestExtractAdvancedRuleSits:
    """_extract_advanced_rule_sits parses grounded AdvancedRule SIT bindings and
    fails closed on malformed / unrelated shapes."""

    @staticmethod
    def _extract(advanced):
        score = pytest.importorskip("score")  # type: ignore[import-untyped]
        return score._extract_advanced_rule_sits(  # noqa: SLF001
            {"Disabled": False, "AdvancedRule": advanced}
        )

    def test_valid_advanced_rule_json_string(self):
        # The collector preserves AdvancedRule as the raw JSON *string* the rule
        # was created with; the evaluator must json.loads and walk it.
        advanced = json.dumps(_advanced_rule("CRD Number SIT"))
        assert self._extract(advanced) == {"CRD Number SIT"}

    def test_valid_advanced_rule_multiple_sits(self):
        advanced = json.dumps(_advanced_rule("CRD Number SIT", "MNPI Keyword SIT"))
        assert self._extract(advanced) == {"CRD Number SIT", "MNPI Keyword SIT"}

    def test_already_parsed_dict_payload(self):
        # Defensive: if a collector/fixture ever emits AdvancedRule as a nested
        # object rather than a string, the same walk applies.
        assert self._extract(_advanced_rule("CRD Number SIT")) == {"CRD Number SIT"}

    def test_singleton_subconditions_collapse(self):
        # ConvertTo-Json can collapse a one-element SubConditions array to a
        # bare object; normalize it like grouped conditions.
        advanced = {
            "Condition": {
                "SubConditions": {
                    "ConditionName": "ContentContainsSensitiveInformation",
                    "Value": {"groups": [{"sensitivetypes": [{"name": "Solo SIT"}]}]},
                }
            }
        }
        assert self._extract(advanced) == {"Solo SIT"}

    def test_singleton_group_and_sensitivetype_collapse(self):
        # Collapse can occur at group and sensitivetype levels simultaneously.
        advanced = {
            "Condition": {
                "SubConditions": [
                    {
                        "ConditionName": "ContentContainsSensitiveInformation",
                        "Value": {"groups": {"name": "G", "sensitivetypes": {"name": "CRD Number SIT"}}},
                    }
                ]
            }
        }
        assert self._extract(advanced) == {"CRD Number SIT"}

    @pytest.mark.parametrize(
        "condition_name",
        [
            "contentcontainssensitiveinformation",
            "CONTENTCONTAINSSENSITIVEINFORMATION",
            "  ContentContainsSensitiveInformation  ",
        ],
    )
    def test_conditionname_casing_and_whitespace_normalized(self, condition_name):
        advanced = json.dumps(_advanced_rule("CRD Number SIT", condition_name=condition_name))
        assert self._extract(advanced) == {"CRD Number SIT"}

    def test_sensitivity_label_subcondition_is_not_credited(self):
        # Control 1.5: a rule can also carry a ContentContainsSensitivityLabel
        # subcondition. Its names must NEVER be mistaken for SITs.
        advanced = json.dumps(
            _advanced_rule("Should Not Appear", condition_name="ContentContainsSensitivityLabel")
        )
        assert self._extract(advanced) == set()

    def test_mixed_sit_and_label_subconditions_credit_only_sit(self):
        advanced = {
            "Condition": {
                "SubConditions": [
                    {
                        "ConditionName": "ContentContainsSensitivityLabel",
                        "Value": {"groups": [{"sensitivetypes": [{"name": "Label Only"}]}]},
                    },
                    {
                        "ConditionName": "ContentContainsSensitiveInformation",
                        "Value": {"groups": [{"sensitivetypes": [{"name": "Real SIT"}]}]},
                    },
                ]
            }
        }
        assert self._extract(advanced) == {"Real SIT"}

    def test_group_label_name_is_not_credited(self):
        # The group's own name is a label; only sensitivetypes[].name are SITs.
        advanced = {
            "Condition": {
                "SubConditions": [
                    {
                        "ConditionName": "ContentContainsSensitiveInformation",
                        "Value": {"groups": [{"name": "FSI-MNPI-Group", "sensitivetypes": [{"name": "Real SIT"}]}]},
                    }
                ]
            }
        }
        assert self._extract(advanced) == {"Real SIT"}

    def test_malformed_json_string_yields_no_names(self):
        assert self._extract("{ not valid json") == set()

    @pytest.mark.parametrize("advanced", ["", "   ", "\n\t"])
    def test_empty_or_whitespace_string_yields_no_names(self, advanced):
        assert self._extract(advanced) == set()

    @pytest.mark.parametrize("advanced", [None, 42, True, ["x"], 3.14])
    def test_non_string_non_dict_payload_yields_no_names(self, advanced):
        assert self._extract(advanced) == set()

    @pytest.mark.parametrize(
        "advanced",
        [
            {},
            {"Condition": "not-a-dict"},
            {"Condition": {}},
            {"Condition": {"SubConditions": "not-a-list"}},
            {"Condition": {"SubConditions": 1}},
            {"Condition": {"SubConditions": []}},
            {"Condition": {"SubConditions": [None, 42, "x"]}},
            {"Condition": {"SubConditions": [{"Value": {"groups": [{"sensitivetypes": [{"name": "No ConditionName"}]}]}}]}},
            {"Condition": {"SubConditions": [{"ConditionName": "ContentContainsSensitiveInformation"}]}},
            {"Condition": {"SubConditions": [{"ConditionName": "ContentContainsSensitiveInformation", "Value": "not-a-dict"}]}},
            {"Condition": {"SubConditions": [{"ConditionName": "ContentContainsSensitiveInformation", "Value": {"groups": [{"sensitivetypes": [{}]}]}}]}},
        ],
    )
    def test_malformed_structures_yield_no_names(self, advanced):
        assert self._extract(advanced) == set()


class TestDlpReferencesSitsAdvancedRuleEvaluator:
    """End-to-end _eval_dlp_references_sits behavior for AdvancedRule-backed
    rules and the direct/advanced fallback contract."""

    @staticmethod
    def _evaluate(policies):
        score = pytest.importorskip("score")  # type: ignore[import-untyped]
        return score._eval_dlp_references_sits(  # noqa: SLF001
            {"purview": {"dlpCompliancePolicies": policies}},
            None,
        )

    @staticmethod
    def _policy(rules):
        # AdvancedRule-backed rules exercised under a valid Copilot scope.
        return [scoped_policy(Name="Copilot MNPI DLP", Enabled=True, Rules=rules)]

    def test_enforced_advanced_rule_backed_policy_passes(self):
        # An AdvancedRule-backed rule has no direct ContentContainsSensitive
        # Information; the SIT must be recovered from AdvancedRule.
        passed, evidence = self._evaluate(
            self._policy(
                [{"Disabled": False, "AdvancedRule": json.dumps(_advanced_rule("CRD Number SIT"))}]
            )
        )
        assert passed is True
        assert "CRD Number SIT" in evidence

    def test_malformed_advanced_rule_without_other_evidence_fails_closed(self):
        passed, evidence = self._evaluate(
            self._policy([{"Disabled": False, "AdvancedRule": "{ broken json"}])
        )
        assert passed is False
        assert "fail closed" in evidence.lower()

    def test_label_only_advanced_rule_fails_closed(self):
        # A rule whose AdvancedRule only carries a sensitivity-label subcondition
        # references no SITs and must not manufacture a phantom pass.
        passed, evidence = self._evaluate(
            self._policy(
                [
                    {
                        "Disabled": False,
                        "AdvancedRule": json.dumps(
                            _advanced_rule("Label Only", condition_name="ContentContainsSensitivityLabel")
                        ),
                    }
                ]
            )
        )
        assert passed is False
        assert "fail closed" in evidence.lower()

    def test_advanced_rule_fallback_when_direct_condition_absent(self):
        # Direct condition present-but-null (AdvancedRule-backed rules) must still
        # fall through to the AdvancedRule evidence rather than short-circuiting.
        passed, evidence = self._evaluate(
            self._policy(
                [
                    {
                        "Disabled": False,
                        "ContentContainsSensitiveInformation": None,
                        "AdvancedRule": json.dumps(_advanced_rule("CRD Number SIT")),
                    }
                ]
            )
        )
        assert passed is True
        assert "CRD Number SIT" in evidence

    def test_direct_and_advanced_rules_credited_together(self):
        passed, evidence = self._evaluate(
            self._policy(
                [
                    {"Disabled": False, "ContentContainsSensitiveInformation": ["Direct SIT"]},
                    {"Disabled": False, "AdvancedRule": json.dumps(_advanced_rule("Advanced SIT"))},
                ]
            )
        )
        assert passed is True
        assert "Direct SIT" in evidence
        assert "Advanced SIT" in evidence

    def test_direct_evidence_survives_malformed_advanced_rule_on_same_rule(self):
        # A single rule carrying valid direct evidence AND a malformed
        # AdvancedRule must still pass on the direct evidence (fallback never
        # discards good evidence).
        passed, evidence = self._evaluate(
            self._policy(
                [
                    {
                        "Disabled": False,
                        "ContentContainsSensitiveInformation": ["Direct SIT"],
                        "AdvancedRule": "{ broken",
                    }
                ]
            )
        )
        assert passed is True
        assert "Direct SIT" in evidence


# ---------------------------------------------------------------------------
# Test: 1.11.a CA MFA evaluator (All-app + exclusion/report-only safety)
# ---------------------------------------------------------------------------


class TestConditionalAccessMfaEvaluator:
    """Adversarial tests for ca_policy_requires_mfa fail-closed behavior."""

    @staticmethod
    def _policy(
        *,
        name: str,
        state: str,
        include_apps: list[str],
        exclude_apps: list[str] | None = None,
        controls: list[str] | str | None = None,
        operator: object | None = None,
        authentication_strength: object | None = None,
    ) -> dict:
        grant_controls: dict[str, object] = {
            "builtInControls": controls if controls is not None else []
        }
        if operator is not None:
            grant_controls["operator"] = operator
        if authentication_strength is not None:
            grant_controls["authenticationStrength"] = authentication_strength
        return {
            "displayName": name,
            "state": state,
            "conditions": {
                "applications": {
                    "includeApplications": include_apps,
                    "excludeApplications": exclude_apps or [],
                }
            },
            "grantControls": grant_controls,
        }

    def test_ca_mfa_accepts_all_cloud_apps_when_mfa_is_sole_control(self):
        score = pytest.importorskip("score")  # type: ignore[import-untyped]

        policies = [
            self._policy(
                name="Require MFA for all cloud apps",
                state="enabled",
                include_apps=["All"],
                controls=["mfa"],
            )
        ]
        passed, evidence = score._eval_ca_policy_requires_mfa(  # noqa: SLF001
            {"graph": {"conditional_access_policies": policies}},
            None,
        )

        assert passed is True
        assert "targets Copilot Studio" in evidence

    def test_ca_mfa_accepts_multi_control_only_when_operator_is_and(self):
        score = pytest.importorskip("score")  # type: ignore[import-untyped]

        policies = [
            self._policy(
                name="All apps MFA and compliant device",
                state="enabled",
                include_apps=["All"],
                controls=["mfa", "compliantDevice"],
                operator="AND",
            )
        ]
        passed, evidence = score._eval_ca_policy_requires_mfa(  # noqa: SLF001
            {"graph": {"conditional_access_policies": policies}},
            None,
        )

        assert passed is True
        assert "operator='AND'" in evidence

    def test_ca_mfa_fails_closed_when_operator_is_or_with_non_mfa_alternatives(self):
        score = pytest.importorskip("score")  # type: ignore[import-untyped]

        policies = [
            self._policy(
                name="All apps MFA or compliant device",
                state="enabled",
                include_apps=["All"],
                controls=["mfa", "compliantDevice"],
                operator="OR",
            )
        ]
        passed, evidence = score._eval_ca_policy_requires_mfa(  # noqa: SLF001
            {"graph": {"conditional_access_policies": policies}},
            None,
        )

        assert passed is False
        assert "operator='OR'" in evidence
        assert "fail closed" in evidence.lower()

    def test_ca_mfa_accepts_authentication_strength_when_it_is_sole_requirement(self):
        score = pytest.importorskip("score")  # type: ignore[import-untyped]

        policies = [
            self._policy(
                name="All apps auth strength MFA only",
                state="enabled",
                include_apps=["All"],
                controls=[],
                authentication_strength={"requirementsSatisfied": "mfa"},
            )
        ]
        passed, evidence = score._eval_ca_policy_requires_mfa(  # noqa: SLF001
            {"graph": {"conditional_access_policies": policies}},
            None,
        )

        assert passed is True
        assert "authenticationStrength" in evidence

    def test_ca_mfa_accepts_authentication_strength_with_non_mfa_controls_only_when_operator_is_and(
        self,
    ):
        score = pytest.importorskip("score")  # type: ignore[import-untyped]

        policies = [
            self._policy(
                name="All apps auth strength MFA and compliant device",
                state="enabled",
                include_apps=["All"],
                controls=["compliantDevice"],
                operator="AND",
                authentication_strength={"requirementsSatisfied": "mfa"},
            )
        ]
        passed, evidence = score._eval_ca_policy_requires_mfa(  # noqa: SLF001
            {"graph": {"conditional_access_policies": policies}},
            None,
        )

        assert passed is True
        assert "operator='AND'" in evidence
        assert "authenticationStrength" in evidence

    def test_ca_mfa_fails_closed_when_authentication_strength_coexists_with_non_mfa_and_operator_is_or(
        self,
    ):
        score = pytest.importorskip("score")  # type: ignore[import-untyped]

        policies = [
            self._policy(
                name="All apps auth strength MFA or compliant device",
                state="enabled",
                include_apps=["All"],
                controls=["compliantDevice"],
                operator="OR",
                authentication_strength={"requirementsSatisfied": "mfa"},
            )
        ]
        passed, evidence = score._eval_ca_policy_requires_mfa(  # noqa: SLF001
            {"graph": {"conditional_access_policies": policies}},
            None,
        )

        assert passed is False
        assert "operator='OR'" in evidence
        assert "fail closed" in evidence.lower()

    def test_ca_mfa_fails_closed_when_authentication_strength_has_multiple_non_mfa_alternatives_with_or(
        self,
    ):
        score = pytest.importorskip("score")  # type: ignore[import-untyped]

        policies = [
            self._policy(
                name="All apps auth strength MFA or multiple alternatives",
                state="enabled",
                include_apps=["All"],
                controls=["compliantDevice", "domainJoinedDevice"],
                operator="OR",
                authentication_strength={"requirementsSatisfied": "mfa"},
            )
        ]
        passed, evidence = score._eval_ca_policy_requires_mfa(  # noqa: SLF001
            {"graph": {"conditional_access_policies": policies}},
            None,
        )

        assert passed is False
        assert "operator='OR'" in evidence
        assert "fail closed" in evidence.lower()

    def test_ca_mfa_fails_when_all_cloud_apps_policy_excludes_copilot(self):
        score = pytest.importorskip("score")  # type: ignore[import-untyped]

        policies = [
            self._policy(
                name="All apps except Copilot Studio",
                state="enabled",
                include_apps=["All"],
                exclude_apps=[score.COPILOT_STUDIO_APP_ID],  # noqa: SLF001
                controls=["mfa"],
            )
        ]
        passed, evidence = score._eval_ca_policy_requires_mfa(  # noqa: SLF001
            {"graph": {"conditional_access_policies": policies}},
            None,
        )

        assert passed is False
        assert "excluded" in evidence.lower()

    def test_ca_mfa_ignores_report_only_and_disabled_policies_for_enforcement(self):
        score = pytest.importorskip("score")  # type: ignore[import-untyped]

        policies = [
            self._policy(
                name="Report-only all apps MFA",
                state="enabledforreportingbutnotenforced",
                include_apps=["All"],
                controls=["mfa"],
            ),
            self._policy(
                name="Disabled direct-app MFA",
                state="disabled",
                include_apps=[score.COPILOT_STUDIO_APP_ID],  # noqa: SLF001
                controls=["mfa"],
            ),
            self._policy(
                name="Enabled policy without MFA",
                state="enabled",
                include_apps=[score.COPILOT_STUDIO_APP_ID],  # noqa: SLF001
                controls=["compliantDevice"],
            ),
        ]
        passed, evidence = score._eval_ca_policy_requires_mfa(  # noqa: SLF001
            {"graph": {"conditional_access_policies": policies}},
            None,
        )

        assert passed is False
        assert "no mfa requirement" in evidence.lower()

    def test_ca_mfa_fails_closed_when_operator_missing_for_multi_controls(self):
        score = pytest.importorskip("score")  # type: ignore[import-untyped]

        policies = [
            self._policy(
                name="Missing operator with multiple controls",
                state="enabled",
                include_apps=["All"],
                controls=["mfa", "compliantDevice"],
            )
        ]
        passed, evidence = score._eval_ca_policy_requires_mfa(  # noqa: SLF001
            {"graph": {"conditional_access_policies": policies}},
            None,
        )

        assert passed is False
        assert "operator missing" in evidence.lower()
        assert "fail closed" in evidence.lower()

    def test_ca_mfa_fails_closed_when_operator_shape_is_invalid(self):
        score = pytest.importorskip("score")  # type: ignore[import-untyped]

        policies = [
            self._policy(
                name="Malformed operator",
                state="enabled",
                include_apps=["All"],
                controls=["mfa", "compliantDevice"],
                operator=["AND"],
            )
        ]
        passed, evidence = score._eval_ca_policy_requires_mfa(  # noqa: SLF001
            {"graph": {"conditional_access_policies": policies}},
            None,
        )

        assert passed is False
        assert "operator missing/invalid" in evidence.lower()
        assert "fail closed" in evidence.lower()

    def test_ca_mfa_fails_closed_when_authentication_strength_coexists_with_non_mfa_and_operator_missing(
        self,
    ):
        score = pytest.importorskip("score")  # type: ignore[import-untyped]

        policies = [
            self._policy(
                name="Missing operator with auth strength and non-MFA control",
                state="enabled",
                include_apps=["All"],
                controls=["compliantDevice"],
                authentication_strength={"requirementsSatisfied": "mfa"},
            )
        ]
        passed, evidence = score._eval_ca_policy_requires_mfa(  # noqa: SLF001
            {"graph": {"conditional_access_policies": policies}},
            None,
        )

        assert passed is False
        assert "operator missing for authenticationstrength" in evidence.lower()
        assert "fail closed" in evidence.lower()

    def test_ca_mfa_fails_closed_when_authentication_strength_coexists_with_non_mfa_and_operator_malformed(
        self,
    ):
        score = pytest.importorskip("score")  # type: ignore[import-untyped]

        policies = [
            self._policy(
                name="Malformed operator with auth strength and non-MFA control",
                state="enabled",
                include_apps=["All"],
                controls=["compliantDevice"],
                operator=["AND"],
                authentication_strength={"requirementsSatisfied": "mfa"},
            )
        ]
        passed, evidence = score._eval_ca_policy_requires_mfa(  # noqa: SLF001
            {"graph": {"conditional_access_policies": policies}},
            None,
        )

        assert passed is False
        assert "operator missing/invalid" in evidence.lower()
        assert "fail closed" in evidence.lower()

    def test_ca_mfa_fails_closed_when_built_in_controls_shape_is_invalid(self):
        score = pytest.importorskip("score")  # type: ignore[import-untyped]

        policies = [
            self._policy(
                name="Malformed controls",
                state="enabled",
                include_apps=[score.COPILOT_STUDIO_APP_ID],  # noqa: SLF001
                controls="mfa",
            )
        ]
        passed, evidence = score._eval_ca_policy_requires_mfa(  # noqa: SLF001
            {"graph": {"conditional_access_policies": policies}},
            None,
        )

        assert passed is False
        assert "fail closed" in evidence.lower()

    def test_ca_mfa_fails_closed_when_include_applications_shape_is_invalid(self):
        score = pytest.importorskip("score")  # type: ignore[import-untyped]

        policies = [
            {
                "displayName": "Malformed app targets",
                "state": "enabled",
                "conditions": {
                    "applications": {
                        "includeApplications": "All",  # invalid shape
                        "excludeApplications": [],
                    }
                },
                "grantControls": {"builtInControls": ["mfa"]},
            }
        ]
        passed, evidence = score._eval_ca_policy_requires_mfa(  # noqa: SLF001
            {"graph": {"conditional_access_policies": policies}},
            None,
        )

        assert passed is False
        assert "fail closed" in evidence.lower()


class TestConditionalAccessMfaEndToEnd:
    """Collector → normalizer → evaluator path for CA MFA enforcement."""

    @staticmethod
    def _manifest() -> dict:
        return build_manifest_with_controls(
            [
                {
                    "id": "1.11",
                    "title": "Control 1.11: Conditional Access and MFA",
                    "pillar": 1,
                    "pillar_name": "Security",
                    "source_file": "docs/controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md",
                    "automation": "full",
                    "collection_methods": ["Graph_API"],
                    "checks": [
                        {
                            "check_id": "1.11.b",
                            "description": "Conditional Access policy enforces MFA for Copilot Studio",
                            "api_call": "Get-MgIdentityConditionalAccessPolicy",
                            "pass_condition": "ca_policy_requires_mfa",
                            "zone_required": [2, 3],
                        }
                    ],
                    "zone_thresholds": {
                        "zone1": {"min_checks_passed": 1, "maturity_score": 1},
                        "zone2": {"min_checks_passed": 1, "maturity_score": 2},
                        "zone3": {"min_checks_passed": 1, "maturity_score": 4},
                    },
                    "manual_question": None,
                }
            ]
        )

    @staticmethod
    def _collector_policy(
        *,
        name: str,
        include_apps: list[str],
        controls: list[str] | str | None,
        state: str = "enabled",
        exclude_apps: list[str] | None = None,
        operator: object = "OR",
        include_operator: bool = True,
        authentication_strength: dict | None = None,
    ) -> dict:
        policy = {
            "Id": f"policy-{name.lower().replace(' ', '-')}",
            "DisplayName": name,
            "State": state,
            "IncludeApplications": include_apps,
            "ExcludeApplications": exclude_apps or [],
            "IncludeUsers": ["All"],
            "ExcludeUsers": [],
            "IncludeGroups": [],
            "ExcludeGroups": [],
            "BuiltInControls": controls if controls is not None else [],
        }
        if include_operator:
            policy["Operator"] = operator
        if authentication_strength is not None:
            policy["AuthenticationStrength"] = authentication_strength
        return policy

    def _run(self, tmp_path: Path, policies: list[dict]) -> dict:
        score = pytest.importorskip("score")  # type: ignore[import-untyped]

        collected = tmp_path / "collected"
        collected.mkdir()

        graph_data = load_fixture("graph_collector_contract.json")
        graph_data["conditionalAccessPolicies"] = policies
        write_json(collected / "graph.json", graph_data)
        for name in ("ppac", "purview", "sharepoint", "sentinel"):
            write_json(collected / f"{name}.json", load_fixture(f"{name}.json"))

        manifest_path = tmp_path / "controls-1.11.json"
        output_path = tmp_path / "scores.json"
        write_json(manifest_path, self._manifest())
        score.run(
            manifest_path=str(manifest_path),
            collected_dir=str(collected),
            zone=2,
            output_path=str(output_path),
        )

        result = json.loads(output_path.read_text(encoding="utf-8"))
        ctrl = next(c for c in result["controls"] if c["id"] == "1.11")
        return ctrl["evidence"]["1.11.b"]

    def test_graph_normalizer_traces_operator_and_authentication_strength_shape(self):
        score = pytest.importorskip("score")  # type: ignore[import-untyped]

        policy = self._collector_policy(
            name="Shape trace",
            include_apps=["All"],
            controls=["mfa", "compliantDevice"],
            operator="AND",
            authentication_strength={
                "Id": "auth-strength-001",
                "DisplayName": "Phishing-resistant MFA",
                "RequirementsSatisfied": "mfa",
                "PolicyType": "builtIn",
                "AllowedCombinations": ["fido2"],
            },
        )
        normalized = score._normalize_graph_data(  # noqa: SLF001
            {"conditionalAccessPolicies": [policy]}
        )
        out_policy = normalized["conditional_access_policies"][0]

        assert out_policy["grantControls"]["operator"] == "AND"
        assert out_policy["grantControls"]["authenticationStrength"] == {
            "id": "auth-strength-001",
            "displayName": "Phishing-resistant MFA",
            "policyType": "builtIn",
            "requirementsSatisfied": "mfa",
            "allowedCombinations": ["fido2"],
        }

    @pytest.mark.parametrize(
        ("policy", "expected_result", "expected_text"),
        [
            (
                lambda self: self._collector_policy(
                    name="All apps OR",
                    include_apps=["All"],
                    controls=["mfa", "compliantDevice"],
                    operator="OR",
                ),
                "fail",
                "operator='OR'",
            ),
            (
                lambda self: self._collector_policy(
                    name="All apps AND",
                    include_apps=["All"],
                    controls=["mfa", "compliantDevice"],
                    operator="AND",
                ),
                "pass",
                "operator='AND'",
            ),
            (
                lambda self: self._collector_policy(
                    name="MFA only",
                    include_apps=["All"],
                    controls=["mfa"],
                ),
                "pass",
                "sole builtInControl",
            ),
            (
                lambda self: self._collector_policy(
                    name="Auth strength MFA",
                    include_apps=["All"],
                    controls=["compliantDevice"],
                    operator="AND",
                    authentication_strength={
                        "Id": "auth-strength-001",
                        "DisplayName": "Phishing-resistant MFA",
                        "RequirementsSatisfied": "mfa",
                        "PolicyType": "builtIn",
                    },
                ),
                "pass",
                "operator='AND' with authenticationStrength",
            ),
            (
                lambda self: self._collector_policy(
                    name="Auth strength MFA only",
                    include_apps=["All"],
                    controls=[],
                    include_operator=False,
                    authentication_strength={
                        "Id": "auth-strength-001",
                        "DisplayName": "Phishing-resistant MFA",
                        "RequirementsSatisfied": "mfa",
                        "PolicyType": "builtIn",
                    },
                ),
                "pass",
                "authenticationStrength",
            ),
            (
                lambda self: self._collector_policy(
                    name="Auth strength MFA OR compliant device",
                    include_apps=["All"],
                    controls=["compliantDevice"],
                    operator="OR",
                    authentication_strength={
                        "Id": "auth-strength-001",
                        "DisplayName": "Phishing-resistant MFA",
                        "RequirementsSatisfied": "mfa",
                        "PolicyType": "builtIn",
                    },
                ),
                "fail",
                "operator='OR'",
            ),
            (
                lambda self: self._collector_policy(
                    name="Auth strength MFA OR multiple non-MFA alternatives",
                    include_apps=["All"],
                    controls=["compliantDevice", "domainJoinedDevice"],
                    operator="OR",
                    authentication_strength={
                        "Id": "auth-strength-001",
                        "DisplayName": "Phishing-resistant MFA",
                        "RequirementsSatisfied": "mfa",
                        "PolicyType": "builtIn",
                    },
                ),
                "fail",
                "operator='OR'",
            ),
            (
                lambda self: self._collector_policy(
                    name="Auth strength missing operator",
                    include_apps=["All"],
                    controls=["compliantDevice"],
                    include_operator=False,
                    authentication_strength={
                        "Id": "auth-strength-001",
                        "DisplayName": "Phishing-resistant MFA",
                        "RequirementsSatisfied": "mfa",
                        "PolicyType": "builtIn",
                    },
                ),
                "fail",
                "operator missing for authenticationStrength",
            ),
            (
                lambda self: self._collector_policy(
                    name="Auth strength malformed operator",
                    include_apps=["All"],
                    controls=["compliantDevice"],
                    operator=["AND"],
                    authentication_strength={
                        "Id": "auth-strength-001",
                        "DisplayName": "Phishing-resistant MFA",
                        "RequirementsSatisfied": "mfa",
                        "PolicyType": "builtIn",
                    },
                ),
                "fail",
                "operator missing/invalid",
            ),
            (
                lambda self: self._collector_policy(
                    name="Excluded app",
                    include_apps=["All"],
                    exclude_apps=["96ff4394-9197-43aa-b393-6a41652e21f8"],
                    controls=["mfa"],
                ),
                "fail",
                "excluded",
            ),
            (
                lambda self: self._collector_policy(
                    name="Missing operator",
                    include_apps=["All"],
                    controls=["mfa", "compliantDevice"],
                    include_operator=False,
                ),
                "fail",
                "operator missing",
            ),
            (
                lambda self: self._collector_policy(
                    name="Malformed operator",
                    include_apps=["All"],
                    controls=["mfa", "compliantDevice"],
                    operator=["AND"],
                ),
                "fail",
                "operator missing/invalid",
            ),
            (
                lambda self: self._collector_policy(
                    name="Report-only auth strength policy",
                    include_apps=["All"],
                    controls=[],
                    state="enabledForReportingButNotEnforced",
                    include_operator=False,
                    authentication_strength={
                        "Id": "auth-strength-001",
                        "DisplayName": "Phishing-resistant MFA",
                        "RequirementsSatisfied": "mfa",
                        "PolicyType": "builtIn",
                    },
                ),
                "fail",
                "No enabled CA policy targets Copilot Studio app ID",
            ),
        ],
    )
    def test_ca_mfa_end_to_end(self, tmp_path: Path, policy, expected_result: str, expected_text: str):
        evidence = self._run(tmp_path, [policy(self)])
        assert evidence["result"] == expected_result
        assert expected_text.lower() in evidence["value"].lower()


# ---------------------------------------------------------------------------
# Test: Azure network source separation (no Sentinel inflation)
# ---------------------------------------------------------------------------


class TestAzureNetworkSourceSeparation:
    """Get-AzPrivateEndpointConnection must not borrow Sentinel availability."""

    def test_private_endpoint_check_remains_unknown_without_azure_network_collector(self):
        score = pytest.importorskip("score")  # type: ignore[import-untyped]

        check = {
            "check_id": "1.20.a",
            "description": "Private endpoint configured",
            "api_call": "Get-AzPrivateEndpointConnection",
            "pass_condition": "private_endpoint_exists",
            "zone_required": [3],
        }
        result = score.evaluate_check(  # noqa: SLF001
            check=check,
            collected={"sentinel": load_fixture("sentinel.json")},
            zone=3,
            collection_methods=["Azure_API"],
            timestamp="2026-07-17T00:00:00Z",
            control_automation="full",
        )

        assert result["source"] is None
        assert result["data_available"] is False
        assert result["result"] == "unknown"
        assert "azure/network" in result["value"]


# ---------------------------------------------------------------------------
# Test: collector-real payloads keep engine contracts stable
# ---------------------------------------------------------------------------

class TestCollectorContractNormalization:
    """Representative collector payloads should score without contract drift."""

    def test_ppac_collector_shape_supports_control_2_1(
        self, tmp_path: Path, manifest: dict
    ):
        score = pytest.importorskip("score")  # type: ignore[import-untyped]

        collected = tmp_path / "collected"
        collected.mkdir()

        write_json(
            collected / "ppac.json",
            load_fixture("ppac_collector_contract.json"),
        )
        for name in ("graph", "purview", "sharepoint", "sentinel"):
            write_json(collected / f"{name}.json", load_fixture(f"{name}.json"))

        manifest_path = tmp_path / "controls.json"
        output_path = tmp_path / "scores.json"
        write_json(manifest_path, manifest)

        score.run(
            manifest_path=str(manifest_path),
            collected_dir=str(collected),
            zone=2,
            output_path=str(output_path),
        )

        result = json.loads(output_path.read_text(encoding="utf-8"))
        ctrl = next(c for c in result["controls"] if c["id"] == "2.1")

        assert ctrl["checks_passed"] == 2
        assert ctrl["maturity_score"] == 2
        assert ctrl["evidence"]["2.1.a"]["result"] == "pass"
        assert "securityGroupId" in ctrl["evidence"]["2.1.a"]["value"]
        assert ctrl["evidence"]["2.1.b"]["result"] == "pass"

    def test_graph_collector_shape_supports_controls_1_1_and_1_3(
        self, tmp_path: Path, manifest: dict
    ):
        score = pytest.importorskip("score")  # type: ignore[import-untyped]

        collected = tmp_path / "collected"
        collected.mkdir()

        write_json(
            collected / "graph.json",
            load_fixture("graph_collector_contract.json"),
        )
        for name in ("ppac", "purview", "sharepoint", "sentinel"):
            write_json(collected / f"{name}.json", load_fixture(f"{name}.json"))

        manifest_path = tmp_path / "controls.json"
        output_path = tmp_path / "scores.json"
        write_json(manifest_path, manifest)

        score.run(
            manifest_path=str(manifest_path),
            collected_dir=str(collected),
            zone=2,
            output_path=str(output_path),
        )

        result = json.loads(output_path.read_text(encoding="utf-8"))
        ctrl_11 = next(c for c in result["controls"] if c["id"] == "1.1")
        ctrl_13 = next(c for c in result["controls"] if c["id"] == "1.3")

        assert ctrl_11["evidence"]["1.1.b"]["result"] == "pass"
        assert ctrl_13["checks_passed"] == 2
        assert ctrl_13["maturity_score"] == 2
        assert ctrl_13["evidence"]["1.3.a"]["result"] == "pass"
        assert "app ID" in ctrl_13["evidence"]["1.3.a"]["value"]
        assert ctrl_13["evidence"]["1.3.b"]["result"] == "pass"

    def test_purview_collector_shape_supports_control_3_1(
        self, tmp_path: Path, manifest: dict
    ):
        score = pytest.importorskip("score")  # type: ignore[import-untyped]

        collected = tmp_path / "collected"
        collected.mkdir()

        write_json(
            collected / "purview.json",
            load_fixture("purview_collector_contract.json"),
        )
        for name in ("ppac", "graph", "sharepoint", "sentinel"):
            write_json(collected / f"{name}.json", load_fixture(f"{name}.json"))

        manifest_path = tmp_path / "controls.json"
        output_path = tmp_path / "scores.json"
        write_json(manifest_path, manifest)

        score.run(
            manifest_path=str(manifest_path),
            collected_dir=str(collected),
            zone=2,
            output_path=str(output_path),
        )

        result = json.loads(output_path.read_text(encoding="utf-8"))
        ctrl = next(c for c in result["controls"] if c["id"] == "3.1")

        assert ctrl["checks_passed"] == 2
        assert ctrl["maturity_score"] == 2
        assert ctrl["evidence"]["3.1.a"]["result"] == "pass"
        assert "UnifiedAuditLogIngestionEnabled is true" in ctrl["evidence"]["3.1.a"]["value"]
        assert ctrl["evidence"]["3.1.b"]["result"] == "pass"
        assert "Copilot Interaction Retention" in ctrl["evidence"]["3.1.b"]["value"]

    def test_sharepoint_collector_shape_supports_control_4_4(
        self, tmp_path: Path, manifest: dict
    ):
        score = pytest.importorskip("score")  # type: ignore[import-untyped]

        collected = tmp_path / "collected"
        collected.mkdir()

        write_json(
            collected / "sharepoint.json",
            load_fixture("sharepoint_collector_contract.json"),
        )
        for name in ("ppac", "graph", "purview", "sentinel"):
            write_json(collected / f"{name}.json", load_fixture(f"{name}.json"))

        manifest_path = tmp_path / "controls.json"
        output_path = tmp_path / "scores.json"
        write_json(manifest_path, manifest)

        score.run(
            manifest_path=str(manifest_path),
            collected_dir=str(collected),
            zone=2,
            output_path=str(output_path),
        )

        result = json.loads(output_path.read_text(encoding="utf-8"))
        ctrl = next(c for c in result["controls"] if c["id"] == "4.4")

        assert ctrl["checks_passed"] == 2
        assert ctrl["maturity_score"] == 2
        assert ctrl["evidence"]["4.4.a"]["result"] == "pass"
        assert ctrl["evidence"]["4.4.b"]["result"] == "pass"
        assert "Disabled" in ctrl["evidence"]["4.4.b"]["value"]

    def test_sentinel_collector_shape_supports_frontier_q17(
        self, tmp_path: Path
    ):
        score_frontier = pytest.importorskip("score_frontier")  # type: ignore[import-untyped]

        collected = tmp_path / "collected"
        collected.mkdir()

        write_json(collected / "ppac.json", load_fixture("ppac.json"))
        write_json(
            collected / "sentinel.json",
            load_fixture("sentinel_collector_contract.json"),
        )

        manifest_data = build_frontier_manifest_with_questions(
            [
                {
                    "question_id": "Q17",
                    "driver": "technology_data",
                    "level": 100,
                    "question_text": "Are environments tagged and is telemetry available?",
                    "fsi_context": "Contract test",
                    "scoring_weight": 1.0,
                    "answer_format": "yes_no_partial",
                    "auto_evaluable": True,
                    "pass_condition": "tagged_environments_with_basic_telemetry",
                    "collection_methods": ["PPAC_PowerShell", "Sentinel"],
                }
            ]
        )
        manifest_path = tmp_path / "frontier-manifest.json"
        output_path = tmp_path / "frontier-summary.json"
        write_json(manifest_path, manifest_data)

        result = score_frontier.run(
            manifest_path=str(manifest_path),
            collected_dir=str(collected),
            output_path=str(output_path),
        )

        q17 = result["evaluator_results"]["Q17"]
        driver = result["driver_scores"]["technology_data"]

        assert q17["answer_value"] == "partial"
        assert "Sentinel workspace" in q17["evidence"]
        assert driver["score"] == 50

    def test_frontier_collector_shape_supports_frontier_run(
        self, tmp_path: Path
    ):
        score_frontier = pytest.importorskip("score_frontier")  # type: ignore[import-untyped]

        collected = tmp_path / "collected"
        collected.mkdir()

        write_json(
            collected / "frontier.json",
            load_fixture("frontier_collector_contract.json"),
        )

        manifest_data = build_frontier_manifest_with_questions(
            [
                {
                    "question_id": "Q01",
                    "driver": "ai_strategy",
                    "level": 100,
                    "question_text": "Is an AI initiative owner identified?",
                    "fsi_context": "Contract test",
                    "scoring_weight": 1.0,
                    "answer_format": "yes_no_partial",
                    "auto_evaluable": False,
                    "collection_methods": ["Manual"],
                },
                {
                    "question_id": "Q02",
                    "driver": "ai_strategy",
                    "level": 200,
                    "question_text": "How repeatable is the AI initiative review process?",
                    "fsi_context": "Contract test",
                    "scoring_weight": 1.0,
                    "answer_format": "scale_1_5",
                    "auto_evaluable": False,
                    "collection_methods": ["Manual"],
                },
                {
                    "question_id": "Q03",
                    "driver": "ai_strategy",
                    "level": 300,
                    "question_text": "Describe where the AI strategy narrative is stored.",
                    "fsi_context": "Contract test",
                    "scoring_weight": 1.0,
                    "answer_format": "text",
                    "auto_evaluable": False,
                    "collection_methods": ["Manual"],
                },
            ]
        )
        manifest_path = tmp_path / "frontier-manifest.json"
        output_path = tmp_path / "frontier-summary.json"
        write_json(manifest_path, manifest_data)

        result = score_frontier.run(
            manifest_path=str(manifest_path),
            collected_dir=str(collected),
            output_path=str(output_path),
        )

        driver = result["driver_scores"]["ai_strategy"]

        assert driver["questions_answered"] == 2
        assert driver["questions_total"] == 3
        assert driver["level_breakdown"]["200"]["ratio"] == 0.75
        assert driver["score"] == 200
        assert result["evaluator_coverage"]["questions"]["manual_only"] == 3


# ---------------------------------------------------------------------------
# Test: summary calculation matches individual controls
# ---------------------------------------------------------------------------

class TestSummaryCalculation:
    """Verify that summary totals are consistent with individual control scores."""

    def test_summary_calculation(self, tmp_path: Path, manifest: dict, collected_dir: Path):
        score = pytest.importorskip("score")  # type: ignore[import-untyped]

        manifest_path = tmp_path / "controls.json"
        output_path = tmp_path / "scores.json"
        write_json(manifest_path, manifest)

        score.run(
            manifest_path=str(manifest_path),
            collected_dir=str(collected_dir),
            zone=2,
            output_path=str(output_path),
        )

        result = json.loads(output_path.read_text(encoding="utf-8"))
        controls = result["controls"]
        summary = result["summary"]

        # Total controls matches
        assert summary["total_controls"] == len(controls)

        manual_count = sum(1 for c in controls if c.get("needs_manual"))
        assert summary["needs_manual"] == manual_count

        # Average maturity should be the mean of all control maturity scores
        scores_list = [c["maturity_score"] for c in controls]
        expected_avg = sum(scores_list) / len(scores_list) if scores_list else 0
        assert abs(summary["average_maturity"] - expected_avg) < 0.01

        # Confidence distribution should sum to total controls
        conf_dist = summary["confidence_distribution"]
        assert sum(conf_dist.values()) == len(controls)

        # Maturity distribution should sum to total controls
        mat_dist = summary["by_maturity"]
        assert sum(mat_dist.values()) == len(controls)

        # Per-pillar control counts should sum to total
        pillar_total = sum(p["controls"] for p in summary["by_pillar"].values())
        assert pillar_total == len(controls)


# ---------------------------------------------------------------------------
# Test: evaluator_state classification and rollup (transparency)
# ---------------------------------------------------------------------------

class TestEvaluatorStateTransparency:
    """Verify that every check and control carries an honest evaluator_state.

    The three states distinguish "manual by design" from "evaluator not
    yet implemented" so the assessment output cannot silently overstate
    automation coverage.
    """

    def test_classify_check_states(self):
        score = pytest.importorskip("score")  # type: ignore[import-untyped]

        # auto_evaluable: condition is in EVALUATORS
        auto_check = {
            "check_id": "x.a",
            "pass_condition": "no_everyone_assignment",
            "collection_methods": ["PPAC_PowerShell"],
        }
        assert (
            score.classify_check_evaluator_state(
                auto_check, "full", ["PPAC_PowerShell"]
            )
            == "auto_evaluable"
        )

        # manual_only: control automation is "manual"
        manual_ctrl_check = {
            "check_id": "x.b",
            "pass_condition": "some_condition",
            "collection_methods": ["Manual"],
        }
        assert (
            score.classify_check_evaluator_state(
                manual_ctrl_check, "manual", ["Manual"]
            )
            == "manual_only"
        )

        # manual_only: no automatable collection method
        manual_method_check = {
            "check_id": "x.c",
            "pass_condition": "some_condition",
            "collection_methods": ["Manual"],
        }
        assert (
            score.classify_check_evaluator_state(
                manual_method_check, "partial", ["Manual"]
            )
            == "manual_only"
        )

        # unimplemented_evaluator: condition specified but no bespoke fn
        unimpl_check = {
            "check_id": "x.d",
            "pass_condition": "some_unwired_condition",
            "collection_methods": ["PPAC_PowerShell"],
        }
        assert (
            score.classify_check_evaluator_state(
                unimpl_check, "full", ["PPAC_PowerShell"]
            )
            == "unimplemented_evaluator"
        )

    def test_rollup_precedence(self):
        score = pytest.importorskip("score")  # type: ignore[import-untyped]

        # auto wins over unimpl wins over manual
        assert (
            score.rollup_control_evaluator_state(
                "full", ["unimplemented_evaluator", "auto_evaluable", "manual_only"]
            )
            == "auto_evaluable"
        )
        assert (
            score.rollup_control_evaluator_state(
                "full", ["unimplemented_evaluator", "manual_only"]
            )
            == "unimplemented_evaluator"
        )
        assert (
            score.rollup_control_evaluator_state("manual", ["manual_only"])
            == "manual_only"
        )

    def test_state_surfaces_in_output(
        self, tmp_path: Path, manifest: dict, collected_dir: Path
    ):
        score = pytest.importorskip("score")  # type: ignore[import-untyped]

        manifest_path = tmp_path / "controls.json"
        output_path = tmp_path / "scores.json"
        write_json(manifest_path, manifest)

        score.run(
            manifest_path=str(manifest_path),
            collected_dir=str(collected_dir),
            zone=2,
            output_path=str(output_path),
        )

        result = json.loads(output_path.read_text(encoding="utf-8"))

        # Every control has an evaluator_state and a breakdown that sums
        # to the number of checks defined.
        for ctrl in result["controls"]:
            assert ctrl["evaluator_state"] in score.EVALUATOR_STATES
            breakdown = ctrl["evaluator_state_breakdown"]
            assert set(breakdown.keys()) >= set(score.EVALUATOR_STATES)
            assert sum(breakdown.values()) == len(ctrl["checks"])
            for chk in ctrl["checks"]:
                assert chk["evaluator_state"] in score.EVALUATOR_STATES

        # Summary surfaces evaluator_coverage rollups
        coverage = result["summary"]["evaluator_coverage"]
        assert set(coverage["controls"].keys()) == set(score.EVALUATOR_STATES)
        assert set(coverage["checks"].keys()) == set(score.EVALUATOR_STATES)
        assert coverage["total_controls"] == len(result["controls"])
        assert coverage["total_checks"] == sum(
            len(c["checks"]) for c in result["controls"]
        )

    def test_full_manifest_coverage_honest(self, tmp_path: Path, collected_dir: Path):
        """Score the real 79-control manifest and assert that the rollup
        reflects today's actual evaluator coverage rather than overstating it.
        """
        score = pytest.importorskip("score")  # type: ignore[import-untyped]

        real_manifest = ASSESSMENT_ROOT / "manifest" / "controls.json"
        if not real_manifest.exists():
            pytest.skip("real controls.json manifest not available")

        # The real manifest is a list of controls; wrap it for the engine
        # if needed.
        raw = json.loads(real_manifest.read_text(encoding="utf-8"))
        controls = raw if isinstance(raw, list) else raw.get("controls", [])
        manifest_data = build_manifest_with_controls(controls)

        manifest_path = tmp_path / "controls.json"
        output_path = tmp_path / "scores.json"
        write_json(manifest_path, manifest_data)

        score.run(
            manifest_path=str(manifest_path),
            collected_dir=str(collected_dir),
            zone=2,
            output_path=str(output_path),
        )

        result = json.loads(output_path.read_text(encoding="utf-8"))
        coverage = result["summary"]["evaluator_coverage"]

        # We must not silently classify every check as auto-evaluable.
        # If this assertion ever fires, either real evaluators were added
        # (great — relax the cap) or the classifier regressed.
        assert coverage["checks"]["auto_evaluable"] < coverage["total_checks"]
        assert coverage["total_controls"] == 79


# ---------------------------------------------------------------------------
# Test: collector failure modes (AS15c)
# ---------------------------------------------------------------------------
# F-ENGINE-API-FAILURE-MODE-UNTESTED-01: assessment engine collectors are
# only happy-path tested; collector failure modes (API timeouts, permission
# denials, malformed responses) never propagate to customer-facing reports.
#
# Each test below exercises one failure mode end-to-end through score.run()
# and asserts (a) the engine does not crash and (b) the failure surfaces in
# the output _metadata.collector_warnings rollup so the customer sees it.

class TestCollectorFailureModes:
    """Engine resilience to malformed / missing / partial collector data.

    Closes F-ENGINE-API-FAILURE-MODE-UNTESTED-01.
    """

    def _run(
        self, tmp_path: Path, manifest: dict, collected: Path, zone: int = 2
    ) -> dict:
        """Run score.run() and return the parsed output JSON."""
        score = pytest.importorskip("score")  # type: ignore[import-untyped]
        manifest_path = tmp_path / "controls.json"
        output_path = tmp_path / "scores.json"
        write_json(manifest_path, manifest)
        score.run(
            manifest_path=str(manifest_path),
            collected_dir=str(collected),
            zone=zone,
            output_path=str(output_path),
        )
        return json.loads(output_path.read_text(encoding="utf-8"))

    def _empty_collected_dir(self, tmp_path: Path) -> Path:
        """Return a fresh empty collected/ directory (no source files)."""
        collected = tmp_path / "collected"
        collected.mkdir()
        return collected

    def test_missing_source_file_no_crash(
        self, tmp_path: Path, manifest: dict
    ):
        """Missing collector files do not crash; warnings surface for each."""
        collected = self._empty_collected_dir(tmp_path)
        result = self._run(tmp_path, manifest, collected)

        warnings = result["_metadata"]["collector_warnings"]
        for src in ("ppac", "graph", "purview", "sharepoint", "sentinel"):
            assert src in warnings, (
                f"Expected warning for missing {src}; got keys {list(warnings)}"
            )
            assert any("not found" in w for w in warnings[src]), (
                f"Expected 'not found' diagnostic in {src} warnings; "
                f"got {warnings[src]}"
            )

    def test_malformed_json_no_crash(
        self, tmp_path: Path, manifest: dict
    ):
        """Malformed JSON does not crash; warning surfaces with parse error."""
        collected = self._empty_collected_dir(tmp_path)
        # Truncated JSON (closing brace missing) - JSONDecodeError path.
        (collected / "ppac.json").write_text(
            '{"_metadata": {"collector": "PPAC"',
            encoding="utf-8",
        )
        # Stub the rest so we isolate the malformed-ppac path.
        for name in ("graph", "purview", "sharepoint", "sentinel"):
            write_json(
                collected / f"{name}.json",
                {"_metadata": {"collector": name.capitalize(), "warnings": []}},
            )
        result = self._run(tmp_path, manifest, collected)

        warnings = result["_metadata"]["collector_warnings"]
        assert "ppac" in warnings, (
            f"Expected ppac warning for malformed JSON; got {list(warnings)}"
        )
        assert any("failed to parse" in w for w in warnings["ppac"]), (
            f"Expected 'failed to parse' diagnostic; got {warnings['ppac']}"
        )
        # Sources that loaded cleanly contribute no warnings.
        for clean in ("graph", "purview", "sharepoint", "sentinel"):
            assert clean not in warnings, (
                f"Unexpected warning for clean source {clean}: {warnings.get(clean)}"
            )

    def test_empty_json_synthesizes_warning(
        self, tmp_path: Path, manifest: dict
    ):
        """Empty `{}` payload triggers a 'collector produced no data' warning.

        Per AS15c rubber-duck S-3: empty payload is the strongest possible
        partial-data signal; the customer must see it.
        """
        collected = self._empty_collected_dir(tmp_path)
        (collected / "ppac.json").write_text("{}", encoding="utf-8")
        for name in ("graph", "purview", "sharepoint", "sentinel"):
            write_json(
                collected / f"{name}.json",
                {"_metadata": {"collector": name.capitalize(), "warnings": []}},
            )
        result = self._run(tmp_path, manifest, collected)

        warnings = result["_metadata"]["collector_warnings"]
        assert "ppac" in warnings
        assert any(
            "empty" in w and "no data" in w for w in warnings["ppac"]
        ), f"Expected empty-payload diagnostic; got {warnings['ppac']}"

    def test_non_dict_root_no_crash(
        self, tmp_path: Path, manifest: dict
    ):
        """Non-dict JSON root (list, null) normalizes to None + warning.

        B-1 from AS15c rubber-duck: PowerShell's ConvertTo-Json collapses
        single-element arrays to bare scalars, so a collector may emit a
        bare list or null at the root. Without a guard, every evaluator
        crashes with `AttributeError: 'list' object has no attribute 'get'`.
        """
        collected = self._empty_collected_dir(tmp_path)
        (collected / "ppac.json").write_text(
            '[{"environments": []}]',  # bare list root
            encoding="utf-8",
        )
        (collected / "graph.json").write_text("null", encoding="utf-8")
        for name in ("purview", "sharepoint", "sentinel"):
            write_json(
                collected / f"{name}.json",
                {"_metadata": {"collector": name.capitalize(), "warnings": []}},
            )
        result = self._run(tmp_path, manifest, collected)

        warnings = result["_metadata"]["collector_warnings"]
        assert "ppac" in warnings
        assert any(
            "expected JSON object" in w for w in warnings["ppac"]
        ), f"Expected non-dict-root diagnostic for ppac; got {warnings['ppac']}"
        assert "graph" in warnings
        assert any(
            "expected JSON object" in w for w in warnings["graph"]
        ), f"Expected non-dict-root diagnostic for graph; got {warnings['graph']}"

    def test_partial_with_warnings_surfaces_per_collector(
        self, tmp_path: Path, manifest: dict
    ):
        """Existing `*_with_errors` fixtures roll up to collector_warnings.

        S-4 from AS15c rubber-duck: parametrize across all collectors with
        existing _with_errors fixtures so we validate warning extraction
        works for every collector schema, not just one.
        """
        collected = tmp_path / "collected"
        collected.mkdir()
        # Use the existing _with_errors fixtures for each collector.
        # Each fixture's _metadata.warnings should appear verbatim in the
        # rollup, in insertion order (no alphabetical sort).
        fixture_map = {
            "ppac": "ppac_with_errors.json",
            "graph": "graph_with_section7_errored.json",
            "purview": "purview_with_errors.json",
            "sharepoint": "sharepoint_errored.json",
            "sentinel": "sentinel.json",  # clean fixture for control
        }
        for source, fixture_name in fixture_map.items():
            write_json(
                collected / f"{source}.json", load_fixture(fixture_name)
            )
        result = self._run(tmp_path, manifest, collected)

        warnings = result["_metadata"]["collector_warnings"]
        # Verify warnings rolled up for the four errored collectors.
        for source in ("ppac", "graph", "purview", "sharepoint"):
            fixture_data = load_fixture(fixture_map[source])
            expected = (
                fixture_data.get("_metadata", {}).get("warnings", [])
            )
            assert source in warnings, (
                f"Expected {source} in collector_warnings; got {list(warnings)}"
            )
            for exp_w in expected:
                assert exp_w in warnings[source], (
                    f"Expected fixture warning '{exp_w}' in rollup for "
                    f"{source}; got {warnings[source]}"
                )
            # Errors (when present) should appear with [error] prefix.
            errors = fixture_data.get("_metadata", {}).get("errors", [])
            for exp_e in errors:
                assert any(
                    f"[error] {exp_e}" == w for w in warnings[source]
                ), (
                    f"Expected fixture error '[error] {exp_e}' for {source}; "
                    f"got {warnings[source]}"
                )
        # Sentinel had no warnings/errors -> excluded from rollup.
        assert "sentinel" not in warnings

    def test_insider_risk_warning_classification_not_mislabeled_as_licensing(
        self, tmp_path: Path, manifest: dict
    ):
        """Insider Risk inventory warnings must surface as unsupported, not E5/licensing."""
        collected = self._empty_collected_dir(tmp_path)
        write_json(collected / "purview.json", load_fixture("purview_with_errors.json"))
        for name in ("ppac", "graph", "sharepoint", "sentinel"):
            write_json(collected / f"{name}.json", load_fixture(f"{name}.json"))

        result = self._run(tmp_path, manifest, collected)
        warnings = result["_metadata"]["collector_warnings"]
        assert "purview" in warnings
        assert any("unsupported_surface" in w for w in warnings["purview"]), warnings["purview"]
        assert not any(
            "licens" in w.lower() for w in warnings["purview"]
        ), warnings["purview"]

    def test_collector_warnings_schema_shape(
        self, tmp_path: Path, manifest: dict, collected_dir: Path
    ):
        """collector_warnings shape: dict[source, list[str]] with valid keys.

        S-2 from AS15c rubber-duck: lock the field's shape via test so a
        future contributor can't accidentally change it (e.g., to a flat
        list or nested object).
        """
        result = self._run(tmp_path, manifest, collected_dir)

        meta = result["_metadata"]
        assert "collector_warnings" in meta
        cw = meta["collector_warnings"]
        assert isinstance(cw, dict)
        valid_sources = {"ppac", "graph", "purview", "sharepoint", "sentinel"}
        for k, v in cw.items():
            assert k in valid_sources, (
                f"Unexpected collector key '{k}' (allowed: {valid_sources})"
            )
            assert isinstance(v, list), (
                f"collector_warnings[{k}] must be list; got {type(v).__name__}"
            )
            assert all(isinstance(s, str) for s in v), (
                f"collector_warnings[{k}] must contain strings; got "
                f"{[type(s).__name__ for s in v]}"
            )

    def test_clean_collected_data_yields_empty_warnings(
        self, tmp_path: Path, manifest: dict, collected_dir: Path
    ):
        """Happy path: all fixtures clean -> collector_warnings == {}."""
        result = self._run(tmp_path, manifest, collected_dir)
        assert result["_metadata"]["collector_warnings"] == {}

    def test_warnings_field_coerces_string_to_list(
        self, tmp_path: Path, manifest: dict
    ):
        """N-4: PowerShell emits string when single-element warnings list.

        ConvertTo-Json collapses single-element arrays to scalars - the
        engine must coerce a bare string back to a single-element list
        rather than treating it as no data.
        """
        collected = self._empty_collected_dir(tmp_path)
        # PPAC fixture with _metadata.warnings as a string (PS footgun).
        write_json(
            collected / "ppac.json",
            {
                "_metadata": {
                    "collector": "PPAC",
                    "warnings": "Lone warning that PowerShell unwrapped",
                },
                "environments": [],
            },
        )
        for name in ("graph", "purview", "sharepoint", "sentinel"):
            write_json(
                collected / f"{name}.json",
                {"_metadata": {"collector": name.capitalize(), "warnings": []}},
            )
        result = self._run(tmp_path, manifest, collected)

        warnings = result["_metadata"]["collector_warnings"]
        assert "ppac" in warnings
        assert "Lone warning that PowerShell unwrapped" in warnings["ppac"]
