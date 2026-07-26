"""Tests for the manifest/solutions-lock sync helper.

``sync_manifest_solutions.py`` is the write-side companion to the read-side CI
gate in ``validate_solutions_lock.py`` (issue #322). It applies lock-declared
associations the manifest is missing, and deliberately does **not** delete
manifest-only associations -- the lock is produced by another repo, so silent
deletion would be an unrecorded contract change.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
SCRIPT = SCRIPT_DIR / "sync_manifest_solutions.py"

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import sync_manifest_solutions as sync  # noqa: E402


def _setup(tmp_path: Path, lock_controls: dict, manifest: list[dict]):
    lock = {
        "schemaVersion": "1.5.0",
        "solutions": {
            sid: {"id": sid, "controls": controls}
            for sid, controls in lock_controls.items()
        },
    }
    lock_path = tmp_path / "solutions-lock.json"
    manifest_path = tmp_path / "controls.json"
    lock_path.write_text(json.dumps(lock), encoding="utf-8")
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    return lock_path, manifest_path


def _run(lock_path: Path, manifest_path: Path, *extra: str):
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--lock",
            str(lock_path),
            "--manifest",
            str(manifest_path),
            *extra,
        ],
        capture_output=True,
        text=True,
        check=False,
    )


def test_check_mode_fails_and_does_not_write(tmp_path):
    lock_path, manifest_path = _setup(
        tmp_path, {"alpha-solution": ["1.1"]}, [{"id": "1.1", "solutions": []}]
    )
    before = manifest_path.read_text(encoding="utf-8")
    result = _run(lock_path, manifest_path)
    assert result.returncode == 1
    assert "MISS 1.1 -> alpha-solution" in result.stdout
    assert manifest_path.read_text(encoding="utf-8") == before


def test_write_mode_adds_missing_associations_sorted(tmp_path):
    lock_path, manifest_path = _setup(
        tmp_path,
        {"beta-solution": ["1.1"], "alpha-solution": ["1.1"]},
        [{"id": "1.1", "solutions": ["zeta-solution"]}],
    )
    result = _run(lock_path, manifest_path, "--write")
    assert result.returncode == 0, result.stderr
    written = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert written[0]["solutions"] == [
        "alpha-solution",
        "beta-solution",
        "zeta-solution",
    ]


def test_write_mode_never_deletes_manifest_only_associations(tmp_path):
    """Manifest-only entries are reported, not silently removed."""
    lock_path, manifest_path = _setup(
        tmp_path,
        {"alpha-solution": ["1.1"]},
        [{"id": "1.1", "solutions": ["alpha-solution", "curated-solution"]}],
    )
    result = _run(lock_path, manifest_path, "--write")
    assert result.returncode == 0, result.stderr
    assert "KEEP 1.1 -> curated-solution" in result.stdout
    written = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert "curated-solution" in written[0]["solutions"]


def test_lock_reference_to_unknown_control_is_reported(tmp_path):
    lock_path, manifest_path = _setup(
        tmp_path,
        {"alpha-solution": ["9.9"]},
        [{"id": "1.1", "solutions": []}],
    )
    result = _run(lock_path, manifest_path)
    assert "lock references unknown control 9.9" in result.stdout


def test_idempotent_when_already_synced(tmp_path):
    lock_path, manifest_path = _setup(
        tmp_path,
        {"alpha-solution": ["1.1"]},
        [{"id": "1.1", "solutions": ["alpha-solution"]}],
    )
    result = _run(lock_path, manifest_path)
    assert result.returncode == 0, result.stderr
    assert "already covers every lock association" in result.stdout


def test_lock_solutions_by_control_handles_list_shape():
    lock = {"solutions": [{"id": "alpha-solution", "controls": ["1.1", "1.2"]}]}
    assert sync.lock_solutions_by_control(lock) == {
        "1.1": {"alpha-solution"},
        "1.2": {"alpha-solution"},
    }


def test_committed_manifest_is_already_synced():
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
