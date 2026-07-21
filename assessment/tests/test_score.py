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


# ---------------------------------------------------------------------------
# Test: 1.6 DSPM for AI evaluator (issue #250)
# ---------------------------------------------------------------------------


class TestDspmPolicyEvaluator:
    """Regression tests for dspm_policy_exists evaluator (control 1.6.a).

    Verifies the evaluator, normalizer, and collector contract alignment
    corrected in issue #250: official DLP field shapes, active enforcement,
    relevant blocking-rule evidence, and the collector→normalizer→evaluator path.
    """

    @staticmethod
    def _dspm_control_manifest() -> dict:
        return build_manifest_with_controls(
            [
                {
                    "id": "1.6",
                    "title": "Control 1.6: Microsoft Purview DSPM for AI",
                    "pillar": 1,
                    "pillar_name": "Security",
                    "source_file": "docs/controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md",
                    "automation": "partial",
                    "collection_methods": ["Purview_PowerShell"],
                    "checks": [
                        {
                            "check_id": "1.6.a",
                            "description": (
                                "Actively enforced Microsoft 365 Copilot DLP policy "
                                "matches all documented signals"
                            ),
                            "api_call": "Get-DlpCompliancePolicy",
                            "pass_condition": "dspm_policy_exists",
                            "zone_required": [2, 3],
                        }
                    ],
                    "zone_thresholds": {
                        "zone1": {"min_checks_passed": 1, "maturity_score": 1},
                        "zone2": {"min_checks_passed": 1, "maturity_score": 2},
                        "zone3": {"min_checks_passed": 1, "maturity_score": 4},
                    },
                    "manual_question": "Has a DSPM for AI scan been reviewed with findings actioned in the last 30 days?",
                }
            ]
        )

    # ---- Unit: evaluator function -------------------------------------------

    def test_dspm_evaluator_passes_for_qualifying_active_copilot_dlp(self):
        score = pytest.importorskip("score")  # type: ignore[import-untyped]

        purview = {
            "dspm_for_ai": {
                "CollectionStatus": "collected",
                "Detected": True,
                "PolicyCount": 1,
                "PolicyNames": ["Active Microsoft 365 Copilot DLP"],
                "DiagnosticPolicyCount": 1,
                "PolicyDiagnostics": [{"Qualifies": True}],
                "RetentionCoverage": False,
            }
        }
        passed, evidence = score._eval_dspm_policy_exists(  # noqa: SLF001
            {"purview": purview}, None
        )

        assert passed is True
        assert "1 actively enforced" in evidence
        assert "Workload=Applications" in evidence
        assert "CopilotExperiences" in evidence

    def test_dspm_evaluator_fails_after_successful_negative_collection(self):
        score = pytest.importorskip("score")  # type: ignore[import-untyped]

        purview = {
            "dspm_for_ai": {
                "CollectionStatus": "collected",
                "Detected": False,
                "PolicyCount": 0,
                "PolicyNames": [],
                "DiagnosticPolicyCount": 0,
                "PolicyDiagnostics": [],
                "RetentionCoverage": False,
                "Note": "DLP collection succeeded; no qualifying active Copilot DLP policy.",
            }
        }
        passed, evidence = score._eval_dspm_policy_exists(  # noqa: SLF001
            {"purview": purview}, None
        )

        assert passed is False
        assert "no qualifying active" in evidence

    def test_dspm_evaluator_fails_for_retention_only_evidence(self):
        score = pytest.importorskip("score")  # type: ignore[import-untyped]

        purview = {
            "dspm_for_ai": {
                "CollectionStatus": "collected",
                "Detected": False,
                "PolicyCount": 0,
                "PolicyNames": [],
                "DiagnosticPolicyCount": 0,
                "PolicyDiagnostics": [],
                "RetentionCoverage": True,
                "RetentionPolicyNames": ["Copilot Retention"],
                "Note": (
                    "No qualifying active Copilot DLP policy. Retention coverage "
                    "is informational only and does not satisfy control 1.6."
                ),
            }
        }
        passed, evidence = score._eval_dspm_policy_exists(  # noqa: SLF001
            {"purview": purview}, None
        )

        assert passed is False
        assert "informational only" in evidence

    def test_dspm_evaluator_rejects_inconsistent_detected_with_zero_policies(self):
        score = pytest.importorskip("score")  # type: ignore[import-untyped]

        purview = {
            "dspm_for_ai": {
                "CollectionStatus": "collected",
                "Detected": True,
                "PolicyCount": 0,
                "PolicyNames": [],
                "DiagnosticPolicyCount": 0,
                "PolicyDiagnostics": [],
                "RetentionCoverage": True,
            }
        }
        passed, evidence = score._eval_dspm_policy_exists(  # noqa: SLF001
            {"purview": purview}, None
        )

        assert passed is False
        assert "no qualifying" in evidence.lower()

    def test_dspm_evaluator_returns_unknown_when_dspm_field_is_none(self):
        score = pytest.importorskip("score")  # type: ignore[import-untyped]

        # dspm_for_ai key present but value is None (collector failed for section 7)
        purview = {"dspm_for_ai": None, "audit_config": {"UnifiedAuditLogIngestionEnabled": True}}
        passed, evidence = score._eval_dspm_policy_exists(  # noqa: SLF001
            {"purview": purview}, None
        )

        assert passed is None
        assert "not collected" in evidence

    def test_dspm_evaluator_returns_unknown_when_purview_missing(self):
        score = pytest.importorskip("score")  # type: ignore[import-untyped]

        passed, evidence = score._eval_dspm_policy_exists(  # noqa: SLF001
            {}, None
        )

        assert passed is None
        assert "not available" in evidence

    def test_dspm_evaluator_returns_unknown_when_rule_evidence_failed(self):
        score = pytest.importorskip("score")  # type: ignore[import-untyped]

        purview = {
            "dspm_for_ai": {
                "CollectionStatus": "failed",
                "Detected": None,
                "PolicyCount": 0,
                "Note": (
                    "DLP policy collection succeeded, but rule evidence failed or "
                    "was unavailable for an otherwise matching Copilot policy."
                ),
            }
        }
        passed, evidence = score._eval_dspm_policy_exists(  # noqa: SLF001
            {"purview": purview}, None
        )

        assert passed is None
        assert "rule evidence failed or was unavailable" in evidence

    def test_dspm_evaluator_returns_unknown_for_legacy_positive_summary(self):
        score = pytest.importorskip("score")  # type: ignore[import-untyped]

        purview = {
            "dspm_for_ai": {
                "Detected": True,
                "PolicyCount": 1,
                "PolicyNames": ["Legacy substring match"],
            }
        }
        passed, evidence = score._eval_dspm_policy_exists(  # noqa: SLF001
            {"purview": purview}, None
        )

        assert passed is None
        assert "state is unavailable" in evidence

    @pytest.mark.parametrize("collection_status", [None, "", "partial"])
    def test_dspm_evaluator_returns_unknown_for_noncanonical_collection_status(
        self, collection_status: str | None
    ):
        score = pytest.importorskip("score")  # type: ignore[import-untyped]

        purview = {
            "dspm_for_ai": {
                "CollectionStatus": collection_status,
                "Detected": True,
                "PolicyCount": 1,
                "PolicyNames": ["Untrusted positive"],
                "DiagnosticPolicyCount": 1,
                "PolicyDiagnostics": [{"Qualifies": True}],
            }
        }
        passed, evidence = score._eval_dspm_policy_exists(  # noqa: SLF001
            {"purview": purview}, None
        )

        assert passed is None
        assert "state is unavailable" in evidence

    def test_dspm_evaluator_requires_canonical_diagnostics_for_collected_summary(
        self,
    ):
        score = pytest.importorskip("score")  # type: ignore[import-untyped]

        purview = {
            "dspm_for_ai": {
                "CollectionStatus": "collected",
                "Detected": True,
                "PolicyCount": 1,
                "PolicyNames": ["Summary without diagnostics"],
            }
        }
        passed, evidence = score._eval_dspm_policy_exists(  # noqa: SLF001
            {"purview": purview}, None
        )

        assert passed is None
        assert "canonical policy diagnostics" in evidence

    # ---- Unit: normalizer handles camelCase → snake_case --------------------

    def test_purview_normalizer_maps_dspmForAi_to_dspm_for_ai(self):
        score = pytest.importorskip("score")  # type: ignore[import-untyped]

        payload = {
            "dspmForAi": {
                "CollectionStatus": "collected",
                "Detected": True,
                "PolicyCount": 1,
                "PolicyNames": ["Active Microsoft 365 Copilot DLP"],
                "RetentionCoverage": False,
            }
        }
        normalized = score._normalize_purview_data(payload)  # noqa: SLF001

        assert "dspm_for_ai" in normalized
        assert normalized["dspm_for_ai"]["Detected"] is True
        assert normalized["dspm_for_ai"]["PolicyCount"] == 1

    def test_purview_normalizer_ignores_null_dspmForAi(self):
        score = pytest.importorskip("score")  # type: ignore[import-untyped]

        payload = {"dspmForAi": None}
        normalized = score._normalize_purview_data(payload)  # noqa: SLF001

        # null dspmForAi should not create a dspm_for_ai key (None is not a dict)
        assert normalized.get("dspm_for_ai") is None

    # ---- Integration: collector contract → evaluator path ------------------

    def test_purview_collector_contract_shape_scores_control_1_6(
        self, tmp_path: Path
    ):
        """Collector contract fixture with canonical shape passes 1.6.a via normalizer."""
        score = pytest.importorskip("score")  # type: ignore[import-untyped]

        collected = tmp_path / "collected"
        collected.mkdir()

        fixture = load_fixture("purview_collector_contract.json")
        policy = fixture["dlpCompliancePolicies"][0]
        assert "Workload" not in policy
        assert policy["Mode"] == "Enable"
        assert policy["Enabled"] is None
        assert json.loads(policy["Locations"]) == {
            "Location": "470f2276-e011-4e9d-a6ec-20768be3a4b0",
            "Workload": "Applications",
        }
        assert policy["RuleCollectionSucceeded"] is True
        assert policy["RuleCollectionStatus"] == "collected"
        assert policy["Rules"] == [
            {
                "Name": "Block public sharing of sensitive content",
                "Priority": 0,
                "Disabled": False,
                "BlockAccess": None,
                "RestrictAccess": [
                    {"setting": "ExcludeContentProcessing", "value": "Block"}
                ],
                "EnforcementPlanes": None,
                "ContentContainsSensitiveInformation": None,
                "ContentContainsSensitivityLabel": None,
                "AdvancedRule": (
                    '{"Version":"1.0","Condition":{"Operator":"And","SubConditions":['
                    '{"ConditionName":"ContentContainsSensitiveInformation","Value":'
                    '[{"groups":[{"Operator":"Or","name":"Default","sensitivetypes":'
                    '[{"confidencelevel":"Low","name":"U.S. Social Security Number"}]}]}]}]}}'
                ),
            }
        ]
        write_json(collected / "purview.json", fixture)
        for name in ("ppac", "graph", "sharepoint", "sentinel"):
            write_json(collected / f"{name}.json", load_fixture(f"{name}.json"))

        manifest_path = tmp_path / "controls-1.6.json"
        output_path = tmp_path / "scores.json"
        write_json(manifest_path, self._dspm_control_manifest())

        score.run(
            manifest_path=str(manifest_path),
            collected_dir=str(collected),
            zone=2,
            output_path=str(output_path),
        )

        result = json.loads(output_path.read_text(encoding="utf-8"))
        ctrl = next(c for c in result["controls"] if c["id"] == "1.6")

        assert ctrl["evidence"]["1.6.a"]["result"] == "pass"
        assert "Workload=Applications" in ctrl["evidence"]["1.6.a"]["value"]
        assert ctrl["checks_passed"] == 1
        assert ctrl["maturity_score"] == 2
        assert ctrl["evaluator_state"] == "auto_evaluable"

    def test_purview_base_fixture_fails_1_6_a_no_dspm_detected(
        self, tmp_path: Path
    ):
        """Base purview.json (no DSPM detected) → 1.6.a fails, maturity 0."""
        score = pytest.importorskip("score")  # type: ignore[import-untyped]

        collected = tmp_path / "collected"
        collected.mkdir()

        for name in ("ppac", "graph", "purview", "sharepoint", "sentinel"):
            write_json(collected / f"{name}.json", load_fixture(f"{name}.json"))

        manifest_path = tmp_path / "controls-1.6.json"
        output_path = tmp_path / "scores.json"
        write_json(manifest_path, self._dspm_control_manifest())

        score.run(
            manifest_path=str(manifest_path),
            collected_dir=str(collected),
            zone=2,
            output_path=str(output_path),
        )

        result = json.loads(output_path.read_text(encoding="utf-8"))
        ctrl = next(c for c in result["controls"] if c["id"] == "1.6")

        assert ctrl["evidence"]["1.6.a"]["result"] == "fail"
        assert ctrl["checks_passed"] == 0
        assert ctrl["maturity_score"] == 0
        assert "informational only" in ctrl["evidence"]["1.6.a"]["value"]

    def test_purview_error_fixture_scores_control_1_6_unknown(self, tmp_path: Path):
        """Failed DLP collection must remain unknown rather than a false negative."""
        score = pytest.importorskip("score")  # type: ignore[import-untyped]

        collected = tmp_path / "collected"
        collected.mkdir()
        write_json(
            collected / "purview.json",
            load_fixture("purview_with_errors.json"),
        )
        for name in ("ppac", "graph", "sharepoint", "sentinel"):
            write_json(collected / f"{name}.json", load_fixture(f"{name}.json"))

        manifest_path = tmp_path / "controls-1.6.json"
        output_path = tmp_path / "scores.json"
        write_json(manifest_path, self._dspm_control_manifest())

        score.run(
            manifest_path=str(manifest_path),
            collected_dir=str(collected),
            zone=2,
            output_path=str(output_path),
        )

        result = json.loads(output_path.read_text(encoding="utf-8"))
        ctrl = next(c for c in result["controls"] if c["id"] == "1.6")

        assert ctrl["evidence"]["1.6.a"]["result"] == "unknown"
        assert ctrl["checks_passed"] == 0
        assert ctrl["maturity_score"] == 0

    def test_control_1_6_is_auto_evaluable_in_real_manifest(
        self, tmp_path: Path, collected_dir: Path
    ):
        """Real manifest check 1.6.a must be auto_evaluable after fix (not unimplemented)."""
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
        ctrl = next(c for c in result["controls"] if c["id"] == "1.6")

        # After fix: 1.6.a has a registered evaluator → auto_evaluable
        assert ctrl["evaluator_state"] == "auto_evaluable", (
            f"Expected auto_evaluable after issue-250 fix; got {ctrl['evaluator_state']}. "
            "Check that dspm_policy_exists is registered in EVALUATORS."
        )
        # Checks should be scored, not left as unknown with unimplemented evidence
        chk = ctrl["checks"][0]
        assert chk["evaluator_state"] == "auto_evaluable"
