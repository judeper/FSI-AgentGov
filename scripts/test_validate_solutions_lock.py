"""Tests for the bidirectional manifest/solutions-lock cross-check.

Issue #322: ``validate_solutions_lock.cross_check`` only looked for manifest
slugs missing from the lock, and only ever emitted warnings. A control-to-
solution association declared by the lock but absent from the manifest passed
CI silently -- 76 of them had accumulated.

These tests pin the fixed contract:

* drift is detected in **both** directions, and it **fails** (exit 1);
* a documented exception suppresses exactly one pair in one direction;
* an exception that no longer matches live drift is stale and fails, so the
  exceptions file cannot become a place to bury debt;
* malformed or reason-less exceptions fail rather than silently exempting;
* the committed repo data passes.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
SCRIPT = SCRIPT_DIR / "validate_solutions_lock.py"

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import validate_solutions_lock as guard  # noqa: E402


def _lock(solutions: dict[str, list[str]]) -> dict:
    """Build a structurally valid lock whose solutions cover the given controls."""
    entries = {}
    for sid, controls in solutions.items():
        entries[sid] = {
            "id": sid,
            "name": sid.replace("-", " ").title(),
            "version": "1.0.0",
            "status": "live",
            "domain": "security",
            "tier": "1",
            "description": "Test solution.",
            "url": f"https://example.invalid/{sid}/",
            "controls": controls,
            "prerequisites": {},
            "verification": "Test verification.",
        }
    return {
        "schemaVersion": "1.5.0",
        "counts": {"total": len(entries), "live": len(entries), "preview": 0},
        "solutions": entries,
    }


def _manifest(controls: dict[str, list[str]]) -> list[dict]:
    return [{"id": cid, "solutions": sols} for cid, sols in controls.items()]


def _write(tmp_path: Path, lock: dict, manifest: list[dict], exceptions=None):
    lock_path = tmp_path / "solutions-lock.json"
    manifest_path = tmp_path / "controls.json"
    lock_path.write_text(json.dumps(lock), encoding="utf-8")
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    exc_path = tmp_path / "solutions-lock-exceptions.json"
    if exceptions is not None:
        exc_path.write_text(json.dumps({"exceptions": exceptions}), encoding="utf-8")
    return lock_path, manifest_path, exc_path


def _run(lock_path: Path, manifest_path: Path, exc_path: Path):
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--lock",
            str(lock_path),
            "--manifest",
            str(manifest_path),
            "--exceptions",
            str(exc_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )


# --------------------------------------------------------------------------
# Direction 2 -- the gap issue #322 reported.
# --------------------------------------------------------------------------


def test_lock_only_association_fails(tmp_path):
    """A lock association the manifest omits must fail (was silent pre-#322)."""
    paths = _write(
        tmp_path,
        _lock({"alpha-solution": ["1.1"]}),
        _manifest({"1.1": []}),
        exceptions=[],
    )
    result = _run(*paths)
    assert result.returncode == 1
    assert "lock-only association" in result.stderr
    assert "alpha-solution" in result.stderr


def test_lock_referencing_unknown_control_fails(tmp_path):
    paths = _write(
        tmp_path,
        _lock({"alpha-solution": ["9.9"]}),
        _manifest({"1.1": ["alpha-solution"]}),
        exceptions=[],
    )
    result = _run(*paths)
    assert result.returncode == 1
    assert "not in the manifest" in result.stderr


# --------------------------------------------------------------------------
# Direction 1 -- previously a warning, now an error.
# --------------------------------------------------------------------------


def test_manifest_only_association_fails(tmp_path):
    """The manifest claiming an association the lock does not back must fail."""
    paths = _write(
        tmp_path,
        _lock({"alpha-solution": ["1.1"]}),
        _manifest({"1.1": ["alpha-solution"], "1.2": ["alpha-solution"]}),
        exceptions=[],
    )
    result = _run(*paths)
    assert result.returncode == 1
    assert "manifest-only association" in result.stderr
    assert "1.2" in result.stderr


def test_manifest_slug_absent_from_lock_fails(tmp_path):
    paths = _write(
        tmp_path,
        _lock({"alpha-solution": ["1.1"]}),
        _manifest({"1.1": ["alpha-solution", "ghost-solution"]}),
        exceptions=[],
    )
    result = _run(*paths)
    assert result.returncode == 1
    assert "not in the lock at all" in result.stderr


def test_matching_sides_pass(tmp_path):
    paths = _write(
        tmp_path,
        _lock({"alpha-solution": ["1.1", "1.2"]}),
        _manifest({"1.1": ["alpha-solution"], "1.2": ["alpha-solution"]}),
        exceptions=[],
    )
    result = _run(*paths)
    assert result.returncode == 0, result.stderr
    assert "clean in both directions" in result.stdout


# --------------------------------------------------------------------------
# Documented exceptions.
# --------------------------------------------------------------------------


def test_documented_exception_suppresses_drift(tmp_path):
    paths = _write(
        tmp_path,
        _lock({"alpha-solution": ["1.1"]}),
        _manifest({"1.1": ["alpha-solution"], "1.2": ["alpha-solution"]}),
        exceptions=[
            {
                "control": "1.2",
                "solution": "alpha-solution",
                "direction": "manifest-only",
                "reason": "Framework-side secondary mapping; reported upstream.",
            }
        ],
    )
    result = _run(*paths)
    assert result.returncode == 0, result.stderr
    assert "documented exception" in result.stdout


def test_exception_direction_is_not_interchangeable(tmp_path):
    """A lock-only exception must not exempt manifest-only drift."""
    paths = _write(
        tmp_path,
        _lock({"alpha-solution": ["1.1"]}),
        _manifest({"1.1": ["alpha-solution"], "1.2": ["alpha-solution"]}),
        exceptions=[
            {
                "control": "1.2",
                "solution": "alpha-solution",
                "direction": "lock-only",
                "reason": "Wrong direction on purpose.",
            }
        ],
    )
    result = _run(*paths)
    assert result.returncode == 1
    assert "manifest-only association" in result.stderr


def test_stale_exception_fails(tmp_path):
    """An exception with no live drift behind it must fail, not linger."""
    paths = _write(
        tmp_path,
        _lock({"alpha-solution": ["1.1"]}),
        _manifest({"1.1": ["alpha-solution"]}),
        exceptions=[
            {
                "control": "1.2",
                "solution": "alpha-solution",
                "direction": "manifest-only",
                "reason": "Reconciled upstream but never cleaned up.",
            }
        ],
    )
    result = _run(*paths)
    assert result.returncode == 1
    assert "stale exception" in result.stderr


def test_exception_without_reason_fails(tmp_path):
    paths = _write(
        tmp_path,
        _lock({"alpha-solution": ["1.1"]}),
        _manifest({"1.1": ["alpha-solution"], "1.2": ["alpha-solution"]}),
        exceptions=[
            {
                "control": "1.2",
                "solution": "alpha-solution",
                "direction": "manifest-only",
                "reason": "   ",
            }
        ],
    )
    result = _run(*paths)
    assert result.returncode == 1
    assert "reason" in result.stderr


def test_exception_with_bad_direction_fails(tmp_path):
    paths = _write(
        tmp_path,
        _lock({"alpha-solution": ["1.1"]}),
        _manifest({"1.1": ["alpha-solution"], "1.2": ["alpha-solution"]}),
        exceptions=[
            {
                "control": "1.2",
                "solution": "alpha-solution",
                "direction": "whatever",
                "reason": "Bad direction value.",
            }
        ],
    )
    result = _run(*paths)
    assert result.returncode == 1
    assert "direction must be one of" in result.stderr


def test_missing_exceptions_file_means_no_exemptions(tmp_path):
    lock_path, manifest_path, exc_path = _write(
        tmp_path,
        _lock({"alpha-solution": ["1.1"]}),
        _manifest({"1.1": []}),
    )
    assert not exc_path.exists()
    result = _run(lock_path, manifest_path, exc_path)
    assert result.returncode == 1
    assert "lock-only association" in result.stderr


# --------------------------------------------------------------------------
# Committed repo data.
# --------------------------------------------------------------------------


def test_repo_lock_and_manifest_agree_both_directions():
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        check=False,
    )
    assert result.returncode == 0, result.stderr


def test_pair_helpers_are_symmetric():
    lock = _lock({"alpha-solution": ["1.1", "1.2"]})
    controls = _manifest({"1.1": ["alpha-solution"], "1.2": ["alpha-solution"]})
    assert guard.lock_pairs(lock) == guard.manifest_pairs(controls)


def test_committed_exceptions_file_is_well_formed():
    exceptions, errors = guard.load_exceptions(guard.EXCEPTIONS_DEFAULT)
    assert not errors, errors
    for (control, solution, direction), reason in exceptions.items():
        assert direction in guard.EXCEPTION_DIRECTIONS
        assert reason.strip(), f"{control}/{solution} has an empty reason"
