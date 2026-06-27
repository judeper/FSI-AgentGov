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
from monitoring_shared import compute_hash  # noqa: E402


def _make_item(title, doc_id, *, abstract="", pub_date="2026-01-01",
               source="Federal Register", agency="SEC", url=None):
    """Construct a RegulatoryItem for tests."""
    return regulatory_monitor.RegulatoryItem(
        source=source,
        agency=agency,
        title=title,
        url=url or f"https://example.test/{doc_id}",
        publication_date=pub_date,
        document_id=doc_id,
        abstract=abstract,
    )


def _item_hash(item):
    """Mirror the hash computed inside check_for_new_items/update_source_state."""
    return compute_hash(f"{item.title}|{item.abstract}|{item.publication_date}")


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


def _run_main(monkeypatch, *, state, fed_items, finra_items):
    """Run regulatory_monitor.main() with network + disk side effects stubbed.

    Returns (exit_code, saved_state, reported_items).
    """
    captured = {'saved_state': None, 'report_items': None}

    monkeypatch.setattr(regulatory_monitor, 'load_state', lambda *a, **k: state)

    def fake_save(saved_state, _path):
        captured['saved_state'] = saved_state

    monkeypatch.setattr(regulatory_monitor, 'save_state_atomic', fake_save)

    def fake_report(items, _path):
        captured['report_items'] = list(items)

    monkeypatch.setattr(regulatory_monitor, 'generate_regulatory_report', fake_report)

    monkeypatch.setattr(
        regulatory_monitor, 'fetch_federal_register_documents',
        lambda *a, **k: fed_items,
    )
    monkeypatch.setattr(
        regulatory_monitor, 'fetch_finra_notices',
        lambda *a, **k: finra_items,
    )

    monkeypatch.setattr(sys, 'argv', ['regulatory_monitor.py'])

    with pytest.raises(SystemExit) as exc:
        regulatory_monitor.main()

    return exc.value.code, captured['saved_state'], captured['report_items']


def test_first_run_establishes_baseline_without_reporting(monkeypatch):
    """First run (no prior state) must persist a baseline and report ZERO items.

    Regression guard for the burst-report defect: without first-run suppression,
    a no-prior-state run flags every fetched item as new and emits a noisy
    ~30-day report with exit 1. The fix records the baseline silently (exit 0).
    """
    fed_items = [
        _make_item("SEC Rule A", "fr-1"),
        _make_item("CFTC Rule B", "fr-2", agency="CFTC"),
    ]
    finra_items = [
        _make_item("FINRA Notice 26-01", "finra-1", source="FINRA", agency="FINRA"),
    ]

    # Empty unified state => no prior state for either source.
    code, saved_state, report_items = _run_main(
        monkeypatch, state={}, fed_items=fed_items, finra_items=finra_items,
    )

    assert code == 0, "first run should exit 0 (no burst report)"
    assert report_items is None, "first run must NOT generate a report"

    # Baseline persisted so subsequent runs are incremental.
    fed_state = saved_state['sources'][regulatory_monitor.SOURCE_KEY_FEDERAL_REGISTER]
    finra_state = saved_state['sources'][regulatory_monitor.SOURCE_KEY_FINRA]
    assert fed_state.get('last_run'), "fed baseline last_run must be recorded"
    assert set(fed_state['entries']) == {'fr-1', 'fr-2'}, "fed baseline entries persisted"
    assert finra_state.get('last_run'), "finra baseline last_run must be recorded"
    assert set(finra_state['entries']) == {'finra-1'}, "finra baseline entries persisted"


def test_subsequent_run_still_detects_new_items(monkeypatch):
    """A run WITH prior state must still detect and report genuinely new items.

    Ensures the baseline suppression only affects the FIRST run, not legitimate
    incremental change detection on later runs.
    """
    known_fed = _make_item("SEC Rule A", "fr-1")
    new_fed = _make_item("SEC Rule C (new)", "fr-3")
    known_finra = _make_item("FINRA Notice 26-01", "finra-1", source="FINRA", agency="FINRA")

    # Prior persisted state: last_run set (not a baseline) with the known items.
    prior_state = {
        "version": 1,
        "sources": {
            regulatory_monitor.SOURCE_KEY_FEDERAL_REGISTER: {
                "last_run": "2026-01-01T00:00:00+00:00",
                "last_checked": "2026-01-01",
                "entries": {"fr-1": _item_hash(known_fed)},
            },
            regulatory_monitor.SOURCE_KEY_FINRA: {
                "last_run": "2026-01-01T00:00:00+00:00",
                "entries": {"finra-1": _item_hash(known_finra)},
            },
        },
    }

    code, saved_state, report_items = _run_main(
        monkeypatch,
        state=prior_state,
        fed_items=[known_fed, new_fed],
        finra_items=[known_finra],
    )

    assert code == 1, "new items should trigger exit 1 (PR in CI)"
    assert report_items is not None, "a report must be generated for new items"
    reported_ids = {item.document_id for item in report_items}
    assert reported_ids == {'fr-3'}, "only the genuinely new item should be reported"
