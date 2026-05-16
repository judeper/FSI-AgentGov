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
- Manifest format: assessment/manifest/controls.json is a bare JSON list
  on disk. Both score.py and report.py accept either bare-list OR
  dict-wrapped form via normalize_manifest_controls() (closes
  F-MANIFEST-FORMAT-MISMATCH-01 in Phase 3 AS6). Tests now invoke the
  engine against the production manifest path directly — no normalization
  workaround is needed.
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
# Test 0: Production manifest loads cleanly through the engine
# ---------------------------------------------------------------------------


class TestProductionManifestLoads:
    """Engine accepts the on-disk production manifest without crashing.

    Closes F-MANIFEST-FORMAT-MISMATCH-01: prior to Phase 3 AS6, both
    score.py and report.py called ``manifest.get("controls", [])`` which
    raised AttributeError against the bare-list manifest on disk. The
    fix added ``normalize_manifest_controls()`` to both modules so they
    accept either shape.

    These assertions exercise the engine end-to-end against the REAL
    ``assessment/manifest/controls.json`` and verify:
      * score.py exits 0
      * scores.json contains 78 controls
      * _metadata.framework_version is read from VERSION (1.6.2)
    """

    def test_score_py_loads_production_manifest(self, tmp_path: Path) -> None:
        collected = stage_collected(tmp_path)
        scores_out = tmp_path / "scores.json"

        try:
            run_score(collected, scores_out, CONTROLS_MANIFEST)
        except subprocess.CalledProcessError as exc:
            pytest.fail(
                "score.py crashed against the production manifest "
                "(F-MANIFEST-FORMAT-MISMATCH-01 regression):\n"
                f"  exit {exc.returncode}\n"
                f"  STDOUT: {exc.stdout[:2000]}\n"
                f"  STDERR: {exc.stderr[:2000]}"
            )

        assert scores_out.exists(), "score.py did not write scores.json"

        scores = json.loads(scores_out.read_text(encoding="utf-8"))
        assert len(scores["controls"]) == 78, (
            f"Expected 78 controls; got {len(scores['controls'])}"
        )

        meta = scores.get("_metadata", {})
        assert meta.get("total_controls") == 78
        assert meta.get("framework_version") == "1.6.2", (
            "framework_version must be read from VERSION file (1.6.2); "
            f"got {meta.get('framework_version')!r}"
        )


# ---------------------------------------------------------------------------
# Test 1: Controls mode produces 3 files
# ---------------------------------------------------------------------------


class TestControlsMode:
    """score.py + report.py (controls) produce the 3 expected files."""

    def test_score_and_report_controls(self, tmp_path: Path) -> None:
        collected = stage_collected(tmp_path)
        manifest = CONTROLS_MANIFEST
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
        manifest = CONTROLS_MANIFEST
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
        manifest = CONTROLS_MANIFEST
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
        manifest = CONTROLS_MANIFEST
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
        manifest = CONTROLS_MANIFEST
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
                "\n[INFO] Timestamp fields stripped for determinism check:\n"
                + "\n".join(f"  {f}" for f in sorted(set(discovered_stripped_keys)))
            )
        else:
            print("\n[INFO] No timestamp fields detected as differing between runs.")


# ---------------------------------------------------------------------------
# Test 5: framework_version is surfaced in every customer-facing artifact
# ---------------------------------------------------------------------------


def _read_framework_version() -> str:
    """Mirror engine helper — read repo-root VERSION as ground truth."""
    return (ASSESSMENT_ROOT.parent / "VERSION").read_text(encoding="utf-8").strip()


class TestFrameworkVersionInReports:
    """Closes F-ENGINE-PREFILLED-NO-FRAMEWORK-VERSION-01.

    Every one of the 5 customer-facing report artifacts must carry the
    framework version it was assessed against, so an auditor opening a
    years-old artifact can establish provenance without out-of-band
    context. Asserts the literal version string from VERSION appears in
    each output.
    """

    def test_all_five_reports_contain_framework_version(
        self, tmp_path: Path
    ) -> None:
        expected_version = _read_framework_version()
        assert expected_version, "VERSION file is empty or missing"

        collected = stage_collected(tmp_path)
        manifest = CONTROLS_MANIFEST
        scores = tmp_path / "scores.json"
        output_dir = tmp_path / "reports"
        output_dir.mkdir()

        run_score(collected, scores, manifest)
        run_report_both(scores, output_dir, manifest)

        # 1-2: Markdown reports — version appears verbatim in header
        for md_name in (
            "assessment-prefilled.md",
            "manual-questionnaire.md",
            "frontier-prefilled.md",
        ):
            text = (output_dir / md_name).read_text(encoding="utf-8")
            assert expected_version in text, (
                f"{md_name} does not contain framework version "
                f"{expected_version!r}. Header rendering may be broken. "
                "F-ENGINE-PREFILLED-NO-FRAMEWORK-VERSION-01 regression."
            )

        # 3: assessment-summary.json — top-level framework_version key
        summary = json.loads(
            (output_dir / "assessment-summary.json").read_text(encoding="utf-8")
        )
        assert summary.get("framework_version") == expected_version, (
            "assessment-summary.json top-level framework_version must "
            f"equal {expected_version!r}; got {summary.get('framework_version')!r}"
        )

        # 4: capability-driver-rollup.json — _metadata.framework_version
        rollup = json.loads(
            (output_dir / "capability-driver-rollup.json").read_text(
                encoding="utf-8"
            )
        )
        assert rollup.get("_metadata", {}).get("framework_version") == expected_version, (
            "capability-driver-rollup.json _metadata.framework_version "
            f"must equal {expected_version!r}; got "
            f"{rollup.get('_metadata', {}).get('framework_version')!r}"
        )

        # 5: scores.json (intermediate but customer-archived) —
        # _metadata.framework_version
        scores_doc = json.loads(scores.read_text(encoding="utf-8"))
        assert scores_doc.get("_metadata", {}).get("framework_version") == expected_version, (
            "scores.json _metadata.framework_version must equal "
            f"{expected_version!r}; got "
            f"{scores_doc.get('_metadata', {}).get('framework_version')!r}"
        )

    def test_files_generated_lists_all_five_in_both_mode(
        self, tmp_path: Path
    ) -> None:
        """Closes the rubber-duck-flagged ordering bug.

        In ``--type both``, ``assessment-summary.json`` is written by
        ``run()`` BEFORE frontier + rollup are generated, so its original
        ``files_generated`` listed only 3 of 5 outputs. AS6 step 4
        rewrites the summary at end of main() with the complete list.
        """
        collected = stage_collected(tmp_path)
        manifest = CONTROLS_MANIFEST
        scores = tmp_path / "scores.json"
        output_dir = tmp_path / "reports"
        output_dir.mkdir()

        run_score(collected, scores, manifest)
        run_report_both(scores, output_dir, manifest)

        summary = json.loads(
            (output_dir / "assessment-summary.json").read_text(encoding="utf-8")
        )
        files = summary.get("files_generated", [])
        basenames = {Path(p).name for p in files}

        expected = {
            "assessment-prefilled.md",
            "manual-questionnaire.md",
            "assessment-summary.json",
            "frontier-prefilled.md",
            "capability-driver-rollup.json",
        }
        missing = expected - basenames
        assert not missing, (
            f"assessment-summary.json files_generated missing: {missing}\n"
            f"Got basenames: {sorted(basenames)}\n"
            "Rewrite at end of main() (--type both) must include all 5 outputs."
        )
