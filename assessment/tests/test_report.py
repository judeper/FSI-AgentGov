"""
Smoke tests for the FSI-AgentGov report generator (engine/report.py).

Verifies that report.py produces the expected output files with correct
structure when given valid scores.json input.
"""

import json
import sys
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Path setup
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


def run_report(tmp_path: Path) -> Path:
    """Set up inputs and run report.py, returning the output directory."""
    try:
        import report  # type: ignore[import-untyped]
    except ImportError:
        pytest.skip("report.py not yet implemented in engine/")

    scores_data = load_fixture("expected_scores.json")
    manifest_data = load_fixture("controls_subset.json")

    scores_path = tmp_path / "scores.json"
    manifest_path = tmp_path / "controls.json"
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    write_json(scores_path, scores_data)
    write_json(manifest_path, manifest_data)

    report.run(
        scores_path=str(scores_path),
        manifest_path=str(manifest_path),
        customer="Test Customer",
        zone=2,
        output_dir=str(output_dir),
    )

    return output_dir


# ---------------------------------------------------------------------------
# Test: all output files are generated
# ---------------------------------------------------------------------------

class TestGeneratesAllOutputFiles:
    """Given valid scores.json input, all 3 output files should be created."""

    def test_generates_all_output_files(self, tmp_path: Path):
        output_dir = run_report(tmp_path)

        expected_files = [
            "assessment-prefilled.md",
            "manual-questionnaire.md",
            "assessment-summary.json",
        ]
        for filename in expected_files:
            filepath = output_dir / filename
            assert filepath.exists(), f"Expected output file not found: {filename}"
            assert filepath.stat().st_size > 0, f"Output file is empty: {filename}"


# ---------------------------------------------------------------------------
# Test: pre-filled report structure
# ---------------------------------------------------------------------------

class TestPrefilledReportStructure:
    """Verify assessment-prefilled.md has expected Markdown heading structure."""

    def test_prefilled_report_structure(self, tmp_path: Path):
        output_dir = run_report(tmp_path)
        report_path = output_dir / "assessment-prefilled.md"
        content = report_path.read_text(encoding="utf-8")

        # Must have an H1 title
        assert content.startswith("# "), "Report should start with an H1 heading"

        # Must have H2 headings for each pillar in the fixture data
        expected_pillars = ["Security", "Management", "Reporting", "SharePoint Grounding"]
        for pillar in expected_pillars:
            assert "## " in content and pillar in content, (
                f"Report should contain H2 section for pillar: {pillar}"
            )

        # Must have H3 headings for each control
        expected_controls = [
            "1.1",
            "1.3",
            "2.1",
            "3.1",
            "4.4",
        ]
        for ctrl_id in expected_controls:
            assert ctrl_id in content, (
                f"Report should contain section for control: {ctrl_id}"
            )


# ---------------------------------------------------------------------------
# Test: manual questionnaire only includes manual controls
# ---------------------------------------------------------------------------

class TestManualQuestionnaireOnlyManualControls:
    """Verify manual-questionnaire.md only includes controls with needs_manual=true."""

    def test_manual_questionnaire_only_manual_controls(self, tmp_path: Path):
        output_dir = run_report(tmp_path)
        questionnaire_path = output_dir / "manual-questionnaire.md"
        content = questionnaire_path.read_text(encoding="utf-8")

        scores_data = load_fixture("expected_scores.json")
        manual_controls = [
            c for c in scores_data["controls"] if c.get("needs_manual")
        ]
        non_manual_controls = [
            c for c in scores_data["controls"] if not c.get("needs_manual")
        ]

        # All manual controls should appear
        for ctrl in manual_controls:
            assert ctrl["id"] in content, (
                f"Manual control {ctrl['id']} should appear in questionnaire"
            )

        # Non-manual controls should NOT appear as questionnaire items
        # (they may appear in a summary table, so we check for the specific
        # questionnaire question pattern rather than just the ID)
        for ctrl in non_manual_controls:
            # The manual_question field should not appear for non-manual controls
            if ctrl.get("manual_question"):
                # This shouldn't happen in our fixture but guard anyway
                continue
            # The control should not have a question block
            assert f"**Question for {ctrl['id']}**" not in content


# ---------------------------------------------------------------------------
# Test: summary JSON schema
# ---------------------------------------------------------------------------

class TestSummaryJsonSchema:
    """Verify assessment-summary.json has all required top-level keys."""

    def test_summary_json_schema(self, tmp_path: Path):
        output_dir = run_report(tmp_path)
        summary_path = output_dir / "assessment-summary.json"
        summary = json.loads(summary_path.read_text(encoding="utf-8"))

        required_keys = [
            "customer_name",
            "zone_assessed",
            "assessment_date",
            "total_controls",
            "auto_scored",
            "needs_manual",
            "average_maturity",
            "by_pillar",
            "by_maturity",
            "confidence_distribution",
        ]
        for key in required_keys:
            assert key in summary, f"Missing required key in summary: {key}"

        # Type checks
        assert isinstance(summary["customer_name"], str)
        assert isinstance(summary["zone_assessed"], int)
        assert isinstance(summary["total_controls"], int)
        assert isinstance(summary["average_maturity"], (int, float))
        assert isinstance(summary["by_pillar"], dict)
        assert isinstance(summary["by_maturity"], dict)
        assert isinstance(summary["confidence_distribution"], dict)


# ---------------------------------------------------------------------------
# Test: collector_warnings flow through to customer-facing artifacts (AS15c)
# ---------------------------------------------------------------------------
# B-2 from AS15c rubber-duck: warnings must appear in BOTH the markdown
# admonition and the assessment-summary.json so downstream dashboards see
# the same data-quality signal as the customer reading the report.
# B-3 from AS15c rubber-duck: verify the admonition actually renders when
# warnings are present and is absent when none are.

def _write_scores_with_warnings(
    tmp_path: Path, collector_warnings: dict
) -> tuple[Path, Path]:
    """Build a minimal scores.json with given collector_warnings + manifest."""
    scores = load_fixture("expected_scores.json")
    scores.setdefault("_metadata", {})["collector_warnings"] = collector_warnings
    scores_path = tmp_path / "scores.json"
    manifest_path = tmp_path / "controls.json"
    write_json(scores_path, scores)
    write_json(manifest_path, load_fixture("controls_subset.json"))
    return scores_path, manifest_path


def _run_report_with_scores(
    tmp_path: Path, scores_path: Path, manifest_path: Path
) -> Path:
    """Run report.run() against caller-provided scores + return output dir."""
    try:
        import report  # type: ignore[import-untyped]
    except ImportError:
        pytest.skip("report.py not yet implemented in engine/")
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    report.run(
        scores_path=str(scores_path),
        manifest_path=str(manifest_path),
        customer="Test Customer",
        zone=2,
        output_dir=str(output_dir),
    )
    return output_dir


class TestCollectorWarningsSurface:
    """collector_warnings flow into prefilled.md admonition + summary.json."""

    def test_admonition_renders_when_warnings_present(self, tmp_path: Path):
        """Non-empty collector_warnings -> warning admonition in prefilled.md."""
        cw = {
            "ppac": [
                "ppac data file failed to parse: Expecting value: line 1 column 1",
                "[error] Permission denied (HTTP 403)",
            ],
            "graph": ["Section 7 (AI Leadership Job Titles) failed: timeout"],
        }
        scores_p, manifest_p = _write_scores_with_warnings(tmp_path, cw)
        output_dir = _run_report_with_scores(tmp_path, scores_p, manifest_p)
        prefilled = (output_dir / "assessment-prefilled.md").read_text(
            encoding="utf-8"
        )

        # Admonition header present.
        assert '!!! warning "Data quality notice' in prefilled, (
            "Expected data-quality warning admonition to render"
        )
        # Each warning string appears verbatim.
        for items in cw.values():
            for w in items:
                assert w in prefilled, (
                    f"Expected warning text '{w}' to render in prefilled.md"
                )
        # Source labels appear (one per source with warnings).
        assert "**ppac:**" in prefilled
        assert "**graph:**" in prefilled

    def test_admonition_absent_when_no_warnings(self, tmp_path: Path):
        """Empty collector_warnings -> no admonition, no spurious header."""
        scores_p, manifest_p = _write_scores_with_warnings(tmp_path, {})
        output_dir = _run_report_with_scores(tmp_path, scores_p, manifest_p)
        prefilled = (output_dir / "assessment-prefilled.md").read_text(
            encoding="utf-8"
        )

        assert '!!! warning "Data quality notice' not in prefilled, (
            "Expected NO data-quality admonition when collector_warnings empty"
        )

    def test_summary_json_carries_collector_warnings(self, tmp_path: Path):
        """assessment-summary.json includes collector_warnings field (B-2).

        Downstream dashboards / CI consumers must see the same data-quality
        signal as the customer reading the markdown report.
        """
        cw = {"sharepoint": ["Section 1 (Site Inventory) failed: Graph API error"]}
        scores_p, manifest_p = _write_scores_with_warnings(tmp_path, cw)
        output_dir = _run_report_with_scores(tmp_path, scores_p, manifest_p)
        summary = json.loads(
            (output_dir / "assessment-summary.json").read_text(encoding="utf-8")
        )

        assert "collector_warnings" in summary, (
            "assessment-summary.json must carry collector_warnings field"
        )
        assert summary["collector_warnings"] == cw

    def test_summary_json_collector_warnings_default_empty(self, tmp_path: Path):
        """Missing _metadata.collector_warnings on input -> {} in summary."""
        # Build scores without the field at all (simulates an old scores.json).
        scores = load_fixture("expected_scores.json")
        scores.setdefault("_metadata", {}).pop("collector_warnings", None)
        scores_path = tmp_path / "scores.json"
        manifest_path = tmp_path / "controls.json"
        write_json(scores_path, scores)
        write_json(manifest_path, load_fixture("controls_subset.json"))
        output_dir = _run_report_with_scores(tmp_path, scores_path, manifest_path)
        summary = json.loads(
            (output_dir / "assessment-summary.json").read_text(encoding="utf-8")
        )

        assert summary.get("collector_warnings") == {}, (
            "Missing collector_warnings on input should default to empty dict"
        )

