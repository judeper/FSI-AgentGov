"""Regression tests for scripts/regulatory_monitor.py.

The critical guard here is test_save_state_atomic_arg_order: regulatory_monitor
must call save_state_atomic(state, STATE_FILE) — dict first, path second — to
match the signature in monitoring_shared.save_state_atomic(state, state_path).
A prior bug swapped these arguments, raising TypeError that was swallowed by the
workflow's continue-on-error, so the monitor never persisted state.

This test exercises the REAL save path (NOT --dry-run, which short-circuits
before any save) by stubbing out the network fetches and capturing the args
passed to save_state_atomic.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))

import regulatory_monitor  # noqa: E402


def test_save_state_atomic_arg_order(monkeypatch):
    """Real (non-dry-run) save path must pass (dict, path), not (path, dict)."""
    captured = {}

    def fake_save(*args, **kwargs):
        captured['args'] = args
        captured['kwargs'] = kwargs

    # Capture the save call instead of writing to disk.
    monkeypatch.setattr(regulatory_monitor, 'save_state_atomic', fake_save)

    # Stub network fetches so no items are "new" -> no-changes branch, which
    # still performs a real save_state_atomic call.
    monkeypatch.setattr(
        regulatory_monitor, 'fetch_federal_register_documents',
        lambda *a, **k: [],
    )
    monkeypatch.setattr(
        regulatory_monitor, 'fetch_finra_notices',
        lambda *a, **k: [],
    )

    # Run the real (non --dry-run) code path.
    monkeypatch.setattr(sys, 'argv', ['regulatory_monitor.py'])

    with pytest.raises(SystemExit) as exc:
        regulatory_monitor.main()

    assert exc.value.code == 0, "no-changes run should exit 0"
    assert 'args' in captured, "save_state_atomic was never called on the real save path"

    args = captured['args']
    assert len(args) >= 2, f"expected (state, path) positional args, got {args!r}"

    # First positional arg MUST be the state dict.
    assert isinstance(args[0], dict), (
        f"save_state_atomic first arg must be the state dict, got {type(args[0]).__name__}. "
        "Arguments are likely swapped (path, dict) instead of (dict, path)."
    )

    # Second positional arg MUST be the state file path.
    assert args[1] == regulatory_monitor.STATE_FILE, (
        f"save_state_atomic second arg must be STATE_FILE, got {args[1]!r}"
    )
