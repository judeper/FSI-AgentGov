"""Smoke tests for FSI-AgentGov monitoring scripts.

Verifies that the learn_monitor and regulatory_monitor modules import
cleanly, expose their main entry points, and can run in --dry-run mode
(offline) without mutating state. Asserts that the unified state file
retains its expected shape after each run.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS_DIR.parent
STATE_FILE = REPO_ROOT / "data" / "monitor-state.json"

sys.path.insert(0, str(SCRIPTS_DIR))


def _assert_state_shape() -> dict:
    assert STATE_FILE.exists(), f"State file missing: {STATE_FILE}"
    data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    assert isinstance(data, dict), "State file must be a JSON object"
    assert "version" in data, "State file missing 'version' key"
    assert "sources" in data, "State file missing 'sources' key"
    assert isinstance(data["sources"], dict), "'sources' must be an object"
    return data


def test_state_file_has_expected_shape():
    _assert_state_shape()


def test_learn_monitor_imports():
    import learn_monitor

    assert hasattr(learn_monitor, "main")
    assert callable(learn_monitor.main)


def test_regulatory_monitor_imports():
    import regulatory_monitor

    assert hasattr(regulatory_monitor, "main")
    assert callable(regulatory_monitor.main)


def test_monitoring_shared_imports():
    import monitoring_shared

    assert hasattr(monitoring_shared, "load_state")
    assert hasattr(monitoring_shared, "save_state_atomic")


@pytest.mark.parametrize(
    "script",
    ["learn_monitor.py", "regulatory_monitor.py"],
)
def test_script_dry_run_exits_cleanly(script):
    """Each script must exit with code 0 in --dry-run mode (offline)."""
    before = _assert_state_shape()

    result = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / script), "--dry-run"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=60,
    )

    assert result.returncode == 0, (
        f"{script} --dry-run failed\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )

    # State file shape must remain intact and unchanged by dry-run.
    after = _assert_state_shape()
    assert before == after, f"{script} --dry-run mutated state file"
