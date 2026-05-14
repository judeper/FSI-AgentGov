"""
Phase 0G — Full-pipeline orchestrator tests.

Validates that score.py → report.py produces ALL expected output files for
controls mode (3 files), frontier mode (1 file), and combined "both" mode
(5 files).  Also checks report determinism.

Invocation::

    cd assessment && pytest tests/test_engine_orchestrator.py -v

Design notes:
- All engine calls go through subprocess.run(sys.executable, ...) so the
  test is environment-agnostic (no sys.path manipulation required).
- Collected fixtures are copied into a tmp_path/collected/ directory that
  matches the directory layout expected by score.py's --collected argument.
- Manifest normalization: assessment/manifest/controls.json is currently a
  bare JSON array (list). score.py expects {"controls": [...]} dict form.
  This mismatch is documented as P0 bug MANIFEST-FORMAT-MISMATCH below.
  The tests use a normalized wrapper written to tmp_path so the pipeline
  logic can still be exercised end-to-end.
- Frontier fixtures:
    * frontier-summary input  → assessment/tests/fixtures/expected_frontier_scores.json
      (this is the stored output of score_frontier.py; it's the correct
       frontier-summary.json format consumed by report.py --type frontier)
    * frontier-manifest        → assessment/manifest/frontier-readiness.json
  If either is missing the relevant tests are skipped with a loud finding.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Paths — all resolved relative to this file so tests run from any cwd
# ---------------------------------------------------------------------------

TESTS_DIR = Path(__file__).resolve().parent
FIXTURES_DIR = TESTS_DIR / "fixtures"
ASSESSMENT_ROOT = TESTS_DIR.parent
ENGINE_DIR = ASSESSMENT_ROOT / "engine"

SCORE_PY = ENGINE_DIR / "score.py"
REPORT_PY = ENGINE_DIR / "report.py"

CONTROLS_MANIFEST = ASSESSMENT_ROOT / "manifest" / "controls.json"
FRONTIER_MANIFEST = ASSESSMENT_ROOT / "manifest" / "frontier-readiness.json"

# The stored output of score_frontier.py serves as the frontier-summary.json
# consumed by report.py --type frontier|both.
FRONTIER_SUMMARY_FIXTURE = FIXTURES_DIR / "expected_frontier_scores.json"

# Collected collector output files to stage in tmp_path/collected/
COLLECTED_FIXTURES: dict[str, str] = {
    "ppac.json": "ppac.json",
    "graph.json": "graph.json",
    "purview.json": "purview.json",
    "sharepoint.json": "sharepoint.json",
    "sentinel.json": "sentinel.json",
}

# Files expected from controls mode
CONTROLS_FILES = [
    "assessment-prefilled.md",
    "manual-questionnaire.md",
    "assessment-summary.json",
]

# Additional files expected from frontier / both modes
FRONTIER_FILE = "frontier-prefilled.md"
ROLLUP_FILE = "capability-driver-rollup.json"


# ---------------------------------------------------------------------------
# Manifest normalization
# ---------------------------------------------------------------------------
# P0 Bug MANIFEST-FORMAT-MISMATCH:
#   assessment/manifest/controls.json is a bare JSON array (list), but
#   score.py calls manifest.get("controls", []) which requires a dict with
#   a "controls" key. Running score.py against the real file causes:
#       AttributeError: 'list' object has no attribute 'get'
#
# Expected fix: either (a) score.py should handle both bare-list and wrapped
# forms, or (b) controls.json should be updated to the wrapped dict form.
# Until fixed, tests write a normalized copy to tmp_path and use that path.


def normalize_manifest(tmp_path: Path) -> Path:
    """Load controls.json, wrap in dict if needed, write normalized copy.

    Returns the path to the normalized manifest in tmp_path.
    Logs a clear P0 finding if the real manifest is a bare list.
    """
    raw = json.loads(CONTROLS_MANIFEST.read_text(encoding="utf-8"))
    if isinstance(raw, list):
        print(
            "\n[P0 BUG MANIFEST-FORMAT-MISMATCH] assessment/manifest/controls.json "
            "is a bare JSON list. score.py expects {'controls': [...]} dict form. "
            "score.py will crash with AttributeError: 'list' object has no attribute 'get' "
            "when run against the production manifest. "
            "Fix required: wrap controls.json in a dict OR update score.py to handle both forms."
        )
        normalized = {"version": "unknown", "controls": raw}
    else:
        normalized = raw

    dest = tmp_path / "controls_normalized.json"
    dest.write_text(json.dumps(normalized, indent=2, ensure_ascii=False), encoding="utf-8")
    return dest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def stage_collected(tmp_path: Path) -> Path:
    """Copy the standard collected fixtures into <tmp_path>/collected/."""
    collected = tmp_path / "collected"
    collected.mkdir(parents=True, exist_ok=True)
    for fixture_name, dest_name in COLLECTED_FIXTURES.items():
        src = FIXTURES_DIR / fixture_name
        if not src.exists():
            pytest.skip(f"Required collected fixture missing: {src}")
        shutil.copy2(src, collected / dest_name)
    return collected


def _subprocess_env() -> dict:
    """Return os.environ with UTF-8 IO encoding forced.

    On Windows, the default console code page (cp1252) cannot encode
    characters like → (U+2192) that report.py prints to stdout.
    Setting PYTHONIOENCODING=utf-8 prevents UnicodeEncodeError in the
    subprocess and surfaces the real exit code.
    """
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    return env


def run_score(collected: Path, scores_out: Path, manifest: Path) -> subprocess.CompletedProcess:
    """Invoke score.py; raise CalledProcessError on failure."""
    return subprocess.run(
        [
            sys.executable,
            str(SCORE_PY),
            "--manifest", str(manifest),
            "--collected", str(collected),
            "--zone", "2",
            "--output", str(scores_out),
        ],
        capture_output=True,
        text=True,
        check=True,
        env=_subprocess_env(),
    )


def run_report_controls(scores: Path, output_dir: Path, manifest: Path) -> subprocess.CompletedProcess:
    """Invoke report.py in controls mode."""
    return subprocess.run(
        [
            sys.executable,
            str(REPORT_PY),
            "--type", "controls",
            "--scores", str(scores),
            "--manifest", str(manifest),
            "--customer", "Test Customer",
            "--zone", "2",
            "--output-dir", str(output_dir),
        ],
        capture_output=True,
        text=True,
        check=True,
        env=_subprocess_env(),
    )


def run_report_frontier(output_dir: Path) -> subprocess.CompletedProcess:
    """Invoke report.py in frontier mode."""
    _require_frontier_fixtures()
    return subprocess.run(
        [
            sys.executable,
            str(REPORT_PY),
            "--type", "frontier",
            "--frontier-summary", str(FRONTIER_SUMMARY_FIXTURE),
            "--frontier-manifest", str(FRONTIER_MANIFEST),
            "--customer", "Test Customer",
            "--output-dir", str(output_dir),
        ],
        capture_output=True,
        text=True,
        check=True,
        env=_subprocess_env(),
    )


def run_report_both(scores: Path, output_dir: Path, manifest: Path) -> subprocess.CompletedProcess:
    """Invoke report.py in both mode."""
    _require_frontier_fixtures()
    return subprocess.run(
        [
            sys.executable,
            str(REPORT_PY),
            "--type", "both",
            "--scores", str(scores),
            "--manifest", str(manifest),
            "--frontier-summary", str(FRONTIER_SUMMARY_FIXTURE),
            "--frontier-manifest", str(FRONTIER_MANIFEST),
            "--customer", "Test Customer",
            "--zone", "2",
            "--output-dir", str(output_dir),
        ],
        capture_output=True,
        text=True,
        check=True,
        env=_subprocess_env(),
    )


def _require_frontier_fixtures() -> None:
    """Skip the test loudly if frontier fixtures are absent."""
    missing = []
    if not FRONTIER_MANIFEST.exists():
        missing.append(str(FRONTIER_MANIFEST))
    if not FRONTIER_SUMMARY_FIXTURE.exists():
        missing.append(str(FRONTIER_SUMMARY_FIXTURE))
    if missing:
        finding = (
            "Phase 1 finding F-FRONTIER-FIXTURE-MISSING: frontier fixtures not present.\n"
            f"  Expected frontier manifest : {FRONTIER_MANIFEST}\n"
            f"  Expected frontier summary  : {FRONTIER_SUMMARY_FIXTURE}\n"
            "  Per codebase conventions, frontier-readiness.json lives in assessment/manifest/\n"
            "  and the frontier-summary fixture should live in assessment/tests/fixtures/."
        )
        print(f"\n[FINDING] {finding}")
        pytest.skip(finding)


def assert_files_exist(output_dir: Path, filenames: list[str], min_bytes: int = 100) -> None:
    """Assert each file exists and is at least min_bytes large."""
    for name in filenames:
        p = output_dir / name
        assert p.exists(), f"Expected output file not found: {name}"
        size = p.stat().st_size
        assert size >= min_bytes, (
            f"Output file is suspiciously small ({size} bytes < {min_bytes}): {name}"
        )


def strip_volatile_fields(obj: object) -> object:
    """Recursively remove fields that legitimately differ between identical runs.

    Volatile fields:
    - Timestamps: assessment_date, assessment_timestamp, timestamp, run_timestamp
    - Output paths: files_generated (contains absolute tmp_path-based paths)
    """
    VOLATILE_KEYS = frozenset(
        {
            "assessment_date",
            "assessment_timestamp",
            "timestamp",
            "run_timestamp",
            "files_generated",  # absolute paths; differ by output dir, not logic
        }
    )
    if isinstance(obj, dict):
        return {k: strip_volatile_fields(v) for k, v in obj.items() if k not in VOLATILE_KEYS}
    if isinstance(obj, list):
        return [strip_volatile_fields(i) for i in obj]
    return obj


# Keep the old name as an alias so it's clear what's being stripped
strip_timestamps = strip_volatile_fields


# ---------------------------------------------------------------------------
# Test 0: P0 Bug — production manifest format mismatch
# ---------------------------------------------------------------------------


class TestManifestFormatP0Bug:
    """Document the P0 format mismatch between controls.json and score.py expectations."""

    def test_production_manifest_format(self) -> None:
        """
        P0 Bug MANIFEST-FORMAT-MISMATCH: controls.json is a bare list.
        score.py expects a dict with a 'controls' key.
        This test explicitly asserts the expected shape and FAILS if the bug
        is still present, surfacing it as a Red test per Phase 0G discipline.
        """
        raw = json.loads(CONTROLS_MANIFEST.read_text(encoding="utf-8"))
        is_dict = isinstance(raw, dict) and "controls" in raw
        if not is_dict:
            print(
                "\n[P0 BUG MANIFEST-FORMAT-MISMATCH] "
                f"controls.json top-level type: {type(raw).__name__}. "
                "score.py expects a dict with a 'controls' key but gets a bare list. "
                "score.py line: `controls = manifest.get('controls', [])` will raise "
                "AttributeError: 'list' object has no attribute 'get'. "
                "Required fix: add a top-level dict wrapper to controls.json or update score.py."
            )
        assert is_dict, (
            "P0 BUG: assessment/manifest/controls.json is a bare JSON list, "
            "not a dict with a 'controls' key. score.py crashes on the real manifest. "
            "See MANIFEST-FORMAT-MISMATCH finding above."
        )


# ---------------------------------------------------------------------------
# Test 1: Controls mode produces 3 files
# ---------------------------------------------------------------------------


class TestControlsMode:
    """score.py + report.py (controls) produce the 3 expected files."""

    def test_score_and_report_controls(self, tmp_path: Path) -> None:
        collected = stage_collected(tmp_path)
        manifest = normalize_manifest(tmp_path)
        scores = tmp_path / "scores.json"
        output_dir = tmp_path / "reports"
        output_dir.mkdir()

        # Step 1: score
        try:
            run_score(collected, scores, manifest)
        except subprocess.CalledProcessError as exc:
            pytest.fail(
                f"score.py failed (exit {exc.returncode}):\n"
                f"STDOUT: {exc.stdout[:2000]}\nSTDERR: {exc.stderr[:2000]}"
            )

        assert scores.exists(), "score.py did not create scores.json"

        # Step 2: report (controls mode)
        try:
            run_report_controls(scores, output_dir, manifest)
        except subprocess.CalledProcessError as exc:
            pytest.fail(
                f"report.py (controls) failed (exit {exc.returncode}):\n"
                f"STDOUT: {exc.stdout[:2000]}\nSTDERR: {exc.stderr[:2000]}"
            )

        assert_files_exist(output_dir, CONTROLS_FILES)

    def test_summary_json_top_level_keys(self, tmp_path: Path) -> None:
        collected = stage_collected(tmp_path)
        manifest = normalize_manifest(tmp_path)
        scores = tmp_path / "scores.json"
        output_dir = tmp_path / "reports"
        output_dir.mkdir()
        run_score(collected, scores, manifest)
        run_report_controls(scores, output_dir, manifest)

        summary_path = output_dir / "assessment-summary.json"
        summary = json.loads(summary_path.read_text(encoding="utf-8"))

        # Discovered top-level keys (from test_report.py's schema test)
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
        missing = [k for k in required_keys if k not in summary]
        assert not missing, (
            f"assessment-summary.json missing expected keys: {missing}\n"
            f"Actual top-level keys: {sorted(summary.keys())}"
        )

        print(f"\n[INFO] assessment-summary.json top-level keys: {sorted(summary.keys())}")

        assert isinstance(summary["customer_name"], str)
        assert isinstance(summary["zone_assessed"], int)
        assert isinstance(summary["total_controls"], int)
        assert isinstance(summary["average_maturity"], (int, float))
        assert isinstance(summary["by_pillar"], dict)
        assert isinstance(summary["by_maturity"], dict)
        assert isinstance(summary["confidence_distribution"], dict)


# ---------------------------------------------------------------------------
# Test 2: Frontier mode produces frontier-prefilled.md
# ---------------------------------------------------------------------------


class TestFrontierMode:
    """report.py --type frontier produces frontier-prefilled.md."""

    def test_frontier_report(self, tmp_path: Path) -> None:
        output_dir = tmp_path / "reports"
        output_dir.mkdir()

        try:
            run_report_frontier(output_dir)
        except subprocess.CalledProcessError as exc:
            pytest.fail(
                f"report.py (frontier) failed (exit {exc.returncode}):\n"
                f"STDOUT: {exc.stdout[:2000]}\nSTDERR: {exc.stderr[:2000]}"
            )

        assert_files_exist(output_dir, [FRONTIER_FILE])


# ---------------------------------------------------------------------------
# Test 3: Both mode produces all 5 files
# ---------------------------------------------------------------------------


class TestBothMode:
    """report.py --type both produces all 5 expected output files."""

    def test_both_produces_all_five_files(self, tmp_path: Path) -> None:
        collected = stage_collected(tmp_path)
        manifest = normalize_manifest(tmp_path)
        scores = tmp_path / "scores.json"
        output_dir = tmp_path / "reports"
        output_dir.mkdir()

        run_score(collected, scores, manifest)

        try:
            run_report_both(scores, output_dir, manifest)
        except subprocess.CalledProcessError as exc:
            pytest.fail(
                f"report.py (both) failed (exit {exc.returncode}):\n"
                f"STDOUT: {exc.stdout[:2000]}\nSTDERR: {exc.stderr[:2000]}"
            )

        all_five = CONTROLS_FILES + [FRONTIER_FILE, ROLLUP_FILE]
        assert_files_exist(output_dir, all_five)

    def test_rollup_json_valid_and_non_empty(self, tmp_path: Path) -> None:
        collected = stage_collected(tmp_path)
        manifest = normalize_manifest(tmp_path)
        scores = tmp_path / "scores.json"
        output_dir = tmp_path / "reports"
        output_dir.mkdir()

        run_score(collected, scores, manifest)
        run_report_both(scores, output_dir, manifest)

        rollup_path = output_dir / ROLLUP_FILE
        rollup = json.loads(rollup_path.read_text(encoding="utf-8"))
        assert isinstance(rollup, dict), "capability-driver-rollup.json should be a dict"
        assert rollup, "capability-driver-rollup.json should not be empty"
        assert "driver_rollups" in rollup, (
            f"Expected 'driver_rollups' key; got: {list(rollup.keys())}"
        )
        print(f"\n[INFO] capability-driver-rollup.json top-level keys: {sorted(rollup.keys())}")


# ---------------------------------------------------------------------------
# Test 4: Determinism — two identical runs produce byte-identical JSON
# ---------------------------------------------------------------------------


class TestDeterminism:
    """Running the full pipeline twice should produce identical JSON outputs."""

    def _run_pipeline(self, tmp_path: Path, run_id: str, manifest: Path) -> Path:
        """Run score + report(both) into a labelled subdirectory; return output_dir."""
        collected = stage_collected(tmp_path)
        scores = tmp_path / f"scores_{run_id}.json"
        output_dir = tmp_path / f"reports_{run_id}"
        output_dir.mkdir()

        run_score(collected, scores, manifest)
        run_report_both(scores, output_dir, manifest)
        return output_dir

    def test_json_outputs_are_deterministic(self, tmp_path: Path) -> None:
        manifest = normalize_manifest(tmp_path)
        out_a = self._run_pipeline(tmp_path, "a", manifest)
        out_b = self._run_pipeline(tmp_path, "b", manifest)

        json_files_to_compare = [
            "assessment-summary.json",
            "capability-driver-rollup.json",
        ]

        discovered_stripped_keys: list[str] = []

        for fname in json_files_to_compare:
            data_a = json.loads((out_a / fname).read_text(encoding="utf-8"))
            data_b = json.loads((out_b / fname).read_text(encoding="utf-8"))

            # Find timestamp fields that differ between runs so we can document them
            def _find_timestamp_fields(d1: object, d2: object, path: str = "") -> list[str]:
                found = []
                if isinstance(d1, dict) and isinstance(d2, dict):
                    for k in d1:
                        if k in d2 and d1[k] != d2[k]:
                            key_path = f"{path}.{k}" if path else k
                            if isinstance(d1[k], str):
                                found.append(key_path)
                            else:
                                found.extend(_find_timestamp_fields(d1[k], d2[k], key_path))
                return found

            ts_fields = _find_timestamp_fields(data_a, data_b)
            if ts_fields:
                discovered_stripped_keys.extend(
                    f"{fname}:{f}" for f in ts_fields
                )

            stripped_a = strip_timestamps(data_a)
            stripped_b = strip_timestamps(data_b)

            assert stripped_a == stripped_b, (
                f"Non-determinism detected in {fname} after stripping timestamp fields.\n"
                f"Timestamp fields stripped: {ts_fields}\n"
                "This means the report differs between identical runs — P0 bug."
            )

        if discovered_stripped_keys:
            print(
                f"\n[INFO] Timestamp fields stripped for determinism check:\n"
                + "\n".join(f"  {f}" for f in sorted(set(discovered_stripped_keys)))
            )
        else:
            print("\n[INFO] No timestamp fields detected as differing between runs.")
