"""
Unit tests for the FSI-AgentGov scoring engine (engine/score.py).

Tests 5 representative controls against fixture data to verify maturity
scoring, zone thresholds, confidence levels, and summary calculations.
"""

import json
import os
import sys
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

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
        try:
            import score  # type: ignore[import-untyped]
        except ImportError:
            pytest.skip("score.py not yet implemented in engine/")

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
        try:
            import score  # type: ignore[import-untyped]
        except ImportError:
            pytest.skip("score.py not yet implemented in engine/")

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

        # fsi_security_groups is empty in graph.json, so check 1.1.b fails.
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
        try:
            import score  # type: ignore[import-untyped]
        except ImportError:
            pytest.skip("score.py not yet implemented in engine/")

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
        try:
            import score  # type: ignore[import-untyped]
        except ImportError:
            pytest.skip("score.py not yet implemented in engine/")

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
# Test: missing data → confidence low
# ---------------------------------------------------------------------------

class TestMissingDataLowConfidence:
    """When a collected data source returns null/missing → confidence 'low'."""

    def test_missing_data_low_confidence(self, tmp_path: Path, manifest: dict):
        try:
            import score  # type: ignore[import-untyped]
        except ImportError:
            pytest.skip("score.py not yet implemented in engine/")

        # Create a collected dir with empty/null data files
        collected = tmp_path / "collected"
        collected.mkdir()

        # Write PPAC with null critical fields
        null_ppac = {
            "_metadata": {
                "collector": "PPAC",
                "timestamp": "2026-03-25T21:00:00Z",
                "tenant_id": "test-tenant",
                "warnings": ["Failed to retrieve environments"],
            },
            "environments": None,
            "dlp_policies": None,
            "role_assignments": None,
            "environment_settings": None,
            "security_posture": None,
            "agent_feature_flags": None,
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
        try:
            import score  # type: ignore[import-untyped]
        except ImportError:
            pytest.skip("score.py not yet implemented in engine/")

        # Build collected data where all checks for 1.1 pass (including 1.1.b)
        collected = tmp_path / "collected"
        collected.mkdir()

        # PPAC: no "All Users" assignment, share-with-everyone disabled
        ppac_data = load_fixture("ppac.json")
        write_json(collected / "ppac.json", ppac_data)

        # Graph: include an FSI publisher security group so check 1.1.b passes
        graph_data = load_fixture("graph.json")
        graph_data["fsi_security_groups"] = [
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
# Test: summary calculation matches individual controls
# ---------------------------------------------------------------------------

class TestSummaryCalculation:
    """Verify that summary totals are consistent with individual control scores."""

    def test_summary_calculation(self, tmp_path: Path, manifest: dict, collected_dir: Path):
        try:
            import score  # type: ignore[import-untyped]
        except ImportError:
            pytest.skip("score.py not yet implemented in engine/")

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

        # Auto-scored count
        auto_scored = sum(1 for c in controls if not c.get("needs_manual") or c["automation"] != "manual")
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
