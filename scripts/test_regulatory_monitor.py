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

import json
import sys
from copy import deepcopy
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

import pytest
from bs4 import BeautifulSoup

SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))

import monitoring_shared  # noqa: E402
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


def _alias(old_identity, canonical_identity, source_hash):
    return {
        "old_identity": old_identity,
        "canonical_identity": canonical_identity,
        "source_hash": source_hash,
        "evidence": {
            "source_hash_at_migration": source_hash,
            "canonical_hash_at_migration": source_hash,
            "reason": "legacy duplicate migrated to canonical node identity",
        },
    }


def test_finra_alias_migration_removes_duplicate_entries_and_requires_evidence():
    """Legacy aliases are ledger-only and cannot be inferred from a partial refresh."""
    source_hash = "sha256:legacy"
    migrated = regulatory_monitor._build_finra_alias_ledger(
        {"legacy notice": source_hash},
        {"node-123": source_hash},
        legacy_migration_ledger=[
            {"identity": "legacy notice", "reason": "verified duplicate"},
        ],
    )
    assert migrated[0]["old_identity"] == "legacy notice"
    assert migrated[0]["canonical_identity"] == "node-123"
    assert migrated[0]["source_hash"] == source_hash
    assert migrated[0]["evidence"]["reason"] == "verified duplicate"
    with pytest.raises(ValueError, match="lack explicit migration evidence"):
        regulatory_monitor._build_finra_alias_ledger(
            {"legacy notice": source_hash},
            {"node-123": source_hash},
        )


def test_finra_alias_survives_canonical_content_update_without_stale_entry():
    """A later canonical update changes only the fetched node entry."""
    old_hash = "sha256:old"
    new_hash = "sha256:new"
    ledger = [_alias("legacy notice", "node-123", old_hash)]
    entries = {"node-123": new_hash}
    assert regulatory_monitor._validate_finra_alias_ledger(
        ledger, entries, ["node-123"]
    ) == []
    source_state = {"coverage": {"alias_ledger": ledger}}
    assert regulatory_monitor._resolve_finra_identity(
        source_state, "legacy notice"
    ) == "node-123"
    rebuilt = regulatory_monitor._build_finra_alias_ledger(
        entries,
        entries,
        existing_alias_ledger=ledger,
    )
    assert rebuilt == ledger
    assert "legacy notice" not in entries


@pytest.mark.parametrize(
    "ledger, expected",
    [
        (
            [
                _alias("a", "b", "sha256:x"),
                _alias("b", "c", "sha256:x"),
            ],
            "cycle",
        ),
        (
            [
                _alias("a", "b", "sha256:x"),
                _alias("a", "c", "sha256:x"),
            ],
            "multiple targets",
        ),
        (
            [
                _alias("a", "b", "sha256:x"),
                _alias("c", "b", "sha256:x"),
            ],
            "one-to-one",
        ),
        (
            [
                {
                    **_alias("a", "b", "sha256:x"),
                    "evidence": {
                        "source_hash_at_migration": "sha256:wrong",
                        "canonical_hash_at_migration": "sha256:x",
                        "reason": "unverified",
                    },
                }
            ],
            "source hash evidence",
        ),
    ],
)
def test_finra_alias_ledger_rejects_cycles_conflicts_and_unverified_evidence(
    ledger, expected
):
    errors = regulatory_monitor._validate_finra_alias_ledger(
        ledger,
        {"b": "sha256:x", "c": "sha256:x"},
        ["b", "c"],
    )
    assert any(expected in error for error in errors)


def test_finra_unaccounted_leftover_identity_fails_closed():
    """A persisted identity outside the fetched set cannot hide behind a watermark."""
    state = {
        "version": 1,
        "sources": {
            regulatory_monitor.SOURCE_KEY_FINRA: {
                "entries": {"node-123": "sha256:x", "stale": "sha256:y"},
                "coverage": {
                    "schema_version": 1,
                    "source": regulatory_monitor.SOURCE_KEY_FINRA,
                    "entry_count": 2,
                    "entries_digest": regulatory_monitor._entries_digest(
                        {"node-123": "sha256:x", "stale": "sha256:y"}
                    ),
                    "listing_mode": "complete-unfiltered",
                    "listing_url": regulatory_monitor.FINRA_NOTICES_URL,
                    "listing_record_count": 1,
                    "raw_row_count": 1,
                    "resolved_row_count": 1,
                    "unresolved_row_count": 0,
                    "unique_node_count": 1,
                    "pages_fetched": 1,
                    "declared_pages": 1,
                    "detail_count": 1,
                    "page_numbers": [0],
                    "pass_proofs": [],
                    "duplicate_ledger": [],
                    "conflict_ledger": [],
                    "fetched_entry_identities": ["node-123"],
                    "fetched_entry_identity_digest": regulatory_monitor._identity_digest(
                        ["node-123"]
                    ),
                    "entry_identity_digest": regulatory_monitor._identity_digest(
                        ["node-123", "stale"]
                    ),
                    "alias_ledger": [],
                    "alias_ledger_digest": regulatory_monitor._alias_ledger_digest([]),
                },
            }
        }
    }
    errors = regulatory_monitor._validate_source_coverage(
        regulatory_monitor.SOURCE_KEY_FINRA,
        state["sources"][regulatory_monitor.SOURCE_KEY_FINRA],
    )
    assert any("stale or unaccounted identities" in error for error in errors)


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
    run_state = {
        "version": 1,
        "sources": {
            regulatory_monitor.SOURCE_KEY_FEDERAL_REGISTER: {
                "last_run": "2026-08-01T00:00:00+00:00",
                "last_checked": "2026-08-01",
                "entries": {},
                "coverage": {
                    "schema_version": 1,
                    "source": regulatory_monitor.SOURCE_KEY_FEDERAL_REGISTER,
                    "entry_count": 0,
                    "entries_digest": regulatory_monitor._entries_digest({}),
                    "watermark": {
                        "last_run": "2026-08-01T00:00:00+00:00",
                        "last_checked": "2026-08-01",
                    },
                    "complete": True,
                    "window_start": "2026-08-01",
                    "query": {},
                    "expected_count": 0,
                    "fetched_count": 0,
                    "pages_fetched": 1,
                    "declared_pages": 1,
                    "page_numbers": [1],
                },
            },
            regulatory_monitor.SOURCE_KEY_FINRA: {
                "last_run": "2026-08-01T00:00:00+00:00",
                "entries": {},
                "coverage": {
                    "schema_version": 1,
                    "source": regulatory_monitor.SOURCE_KEY_FINRA,
                    "entry_count": 0,
                    "entries_digest": regulatory_monitor._entries_digest({}),
                    "watermark": {"last_run": "2026-08-01T00:00:00+00:00"},
                    "complete": True,
                    "listing_mode": "complete-unfiltered",
                    "listing_url": regulatory_monitor.FINRA_NOTICES_URL,
                    "listing_record_count": 0,
                    "pages_fetched": 1,
                    "declared_pages": 1,
                    "detail_count": 0,
                    "page_numbers": [0],
                    "page_identities": [
                        {"requested": 0, "final": 0, "active": 0},
                    ],
                    "fetched_entry_identities": [],
                    "fetched_entry_identity_digest": regulatory_monitor._identity_digest([]),
                    "entry_identity_digest": regulatory_monitor._identity_digest([]),
                    "alias_ledger": [],
                    "alias_ledger_digest": regulatory_monitor._alias_ledger_digest([]),
                    "raw_row_count": 0,
                    "resolved_row_count": 0,
                    "unresolved_row_count": 0,
                    "unique_node_count": 0,
                    "pass_proofs": [
                        {
                            "token": "test-pass-1",
                            "declared_pages": 1,
                            "pages_fetched": 1,
                            "page_numbers": [0],
                            "page_identities": [{"requested": 0, "final": 0, "active": 0}],
                            "page_row_counts": [0],
                            "page_row_digests": [compute_hash("[]")],
                            "page_row_payloads": [[]],
                            "raw_row_count": 0,
                            "resolved_row_count": 0,
                            "unresolved_row_count": 0,
                            "unique_node_count": 0,
                        },
                        {
                            "token": "test-pass-2",
                            "declared_pages": 1,
                            "pages_fetched": 1,
                            "page_numbers": [0],
                            "page_identities": [{"requested": 0, "final": 0, "active": 0}],
                            "page_row_counts": [0],
                            "page_row_digests": [compute_hash("[]")],
                            "page_row_payloads": [[]],
                            "raw_row_count": 0,
                            "resolved_row_count": 0,
                            "unresolved_row_count": 0,
                            "unique_node_count": 0,
                        },
                    ],
                    "duplicate_ledger": [],
                    "conflict_ledger": [],
                },
            },
        },
    }
    monkeypatch.setattr(regulatory_monitor, "load_state", lambda *a, **k: run_state)

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


def _run_main(monkeypatch, *, state, fed_items, finra_items, args=None):
    """Run regulatory_monitor.main() with network + disk side effects stubbed.

    Returns (exit_code, saved_state, reported_items).
    """
    for source_key in (
        regulatory_monitor.SOURCE_KEY_FEDERAL_REGISTER,
        regulatory_monitor.SOURCE_KEY_FINRA,
    ):
        source_state = state.get("sources", {}).get(source_key)
        if not isinstance(source_state, dict) or "coverage" in source_state:
            continue
        entries = source_state.get("entries", {})
        if not isinstance(entries, dict):
            continue
        common = {
            "schema_version": 1,
            "source": source_key,
            "entry_count": len(entries),
            "entries_digest": regulatory_monitor._entries_digest(entries),
            "watermark": regulatory_monitor._coverage_watermark(source_state),
            "complete": True,
        }
        if source_key == regulatory_monitor.SOURCE_KEY_FEDERAL_REGISTER:
            common.update({
                "window_start": source_state.get("last_checked", "2026-01-01"),
                "query": {},
                "expected_count": len(entries),
                "fetched_count": len(entries),
                "pages_fetched": 1,
                "declared_pages": 1,
                "page_numbers": [1],
            })
        else:
            common.update({
                "listing_mode": "complete-unfiltered",
                "listing_url": regulatory_monitor.FINRA_NOTICES_URL,
                "listing_record_count": len(entries),
                "pages_fetched": 1,
                "declared_pages": 1,
                "detail_count": len(entries),
                "page_numbers": [0],
                "page_identities": [
                    {"requested": 0, "final": 0, "active": 0},
                ],
                "fetched_entry_identities": sorted(entries),
                "fetched_entry_identity_digest": regulatory_monitor._identity_digest(
                    entries
                ),
                "entry_identity_digest": regulatory_monitor._identity_digest(
                    entries
                ),
                "alias_ledger": [],
                "alias_ledger_digest": regulatory_monitor._alias_ledger_digest([]),
                "raw_row_count": len(entries),
                "resolved_row_count": len(entries),
                "unresolved_row_count": 0,
                "unique_node_count": len(entries),
                "pass_proofs": [
                    {
                        "token": "test-pass-1",
                        "declared_pages": 1,
                        "pages_fetched": 1,
                        "page_numbers": [0],
                        "page_identities": [
                            {"requested": 0, "final": 0, "active": 0},
                        ],
                        "page_row_counts": [len(entries)],
                        "page_row_digests": [regulatory_monitor._entries_digest(entries)],
                        "page_row_payloads": [[]],
                        "raw_row_count": len(entries),
                        "resolved_row_count": len(entries),
                        "unresolved_row_count": 0,
                        "unique_node_count": len(entries),
                    },
                    {
                        "token": "test-pass-2",
                        "declared_pages": 1,
                        "pages_fetched": 1,
                        "page_numbers": [0],
                        "page_identities": [
                            {"requested": 0, "final": 0, "active": 0},
                        ],
                        "page_row_counts": [len(entries)],
                        "page_row_digests": [regulatory_monitor._entries_digest(entries)],
                        "page_row_payloads": [[]],
                        "raw_row_count": len(entries),
                        "resolved_row_count": len(entries),
                        "unresolved_row_count": 0,
                        "unique_node_count": len(entries),
                    },
                ],
                "duplicate_ledger": [],
                "conflict_ledger": [],
            })
        source_state["coverage"] = common
    captured = {'saved_state': None, 'report_items': None}

    monkeypatch.setattr(regulatory_monitor, 'load_state', lambda *a, **k: state)

    def fake_save(saved_state, _path):
        captured['saved_state'] = saved_state

    monkeypatch.setattr(regulatory_monitor, 'save_state_atomic', fake_save)

    def fake_report(items, _path):
        captured['report_items'] = list(items)

    monkeypatch.setattr(regulatory_monitor, 'generate_regulatory_report', fake_report)

    def as_result(items, source_key):
        if isinstance(items, regulatory_monitor.FetchResult):
            return items
        items = list(items)
        if source_key == regulatory_monitor.SOURCE_KEY_FEDERAL_REGISTER:
            coverage = {
                "complete": True,
                "window_start": "2026-01-01",
                "query": {},
                "expected_count": len(items),
                "fetched_count": len(items),
                "pages_fetched": 1,
                "declared_pages": 1,
                "page_numbers": [1],
            }
        else:
            coverage = {
                "complete": True,
                "listing_mode": "complete-unfiltered",
                "listing_url": regulatory_monitor.FINRA_NOTICES_URL,
                "listing_record_count": len(items),
                "pages_fetched": 1,
                "declared_pages": 1,
                "detail_count": len(items),
                "page_numbers": [0],
                "page_identities": [
                    {"requested": 0, "final": 0, "active": 0},
                ],
                "fetched_entry_identities": sorted(
                    item.document_id if item.document_id else item.url
                    for item in items
                ),
                "fetched_entry_identity_digest": regulatory_monitor._identity_digest(
                    item.document_id if item.document_id else item.url
                    for item in items
                ),
                "entry_identity_digest": regulatory_monitor._identity_digest(
                    item.document_id if item.document_id else item.url
                    for item in items
                ),
                "alias_ledger": [],
                "alias_ledger_digest": regulatory_monitor._alias_ledger_digest([]),
                "raw_row_count": len(items),
                "resolved_row_count": len(items),
                "unresolved_row_count": 0,
                "unique_node_count": len(items),
                "pass_proofs": [
                    {
                        "token": "test-pass-1",
                        "declared_pages": 1,
                        "pages_fetched": 1,
                        "page_numbers": [0],
                        "page_identities": [
                            {"requested": 0, "final": 0, "active": 0},
                        ],
                        "page_row_counts": [len(items)],
                        "page_row_digests": [compute_hash(str(items))],
                        "page_row_payloads": [[]],
                        "raw_row_count": len(items),
                        "resolved_row_count": len(items),
                        "unresolved_row_count": 0,
                        "unique_node_count": len(items),
                    },
                    {
                        "token": "test-pass-2",
                        "declared_pages": 1,
                        "pages_fetched": 1,
                        "page_numbers": [0],
                        "page_identities": [
                            {"requested": 0, "final": 0, "active": 0},
                        ],
                        "page_row_counts": [len(items)],
                        "page_row_digests": [compute_hash(str(items))],
                        "page_row_payloads": [[]],
                        "raw_row_count": len(items),
                        "resolved_row_count": len(items),
                        "unresolved_row_count": 0,
                        "unique_node_count": len(items),
                    },
                ],
                "duplicate_ledger": [],
                "conflict_ledger": [],
            }
        return regulatory_monitor.FetchResult(
            items,
            complete=True,
            coverage=coverage,
        )

    monkeypatch.setattr(
        regulatory_monitor, 'fetch_federal_register_documents',
        lambda *a, **k: as_result(fed_items, regulatory_monitor.SOURCE_KEY_FEDERAL_REGISTER),
    )
    monkeypatch.setattr(
        regulatory_monitor, 'fetch_finra_notices',
        lambda *a, **k: as_result(finra_items, regulatory_monitor.SOURCE_KEY_FINRA),
    )

    monkeypatch.setattr(
        sys,
        'argv',
        ['regulatory_monitor.py', *(args or [])],
    )

    with pytest.raises(SystemExit) as exc:
        regulatory_monitor.main()

    return exc.value.code, captured['saved_state'], captured['report_items']


def test_first_run_establishes_baseline_without_reporting(monkeypatch):
    """Explicitly approved baseline mode persists a baseline without reporting.

    Regression guard for the burst-report defect: without first-run suppression,
    a no-prior-state run flags every fetched item as new and emits a noisy
    ~30-day report with exit 1. Only the explicitly approved manual mode records
    the baseline silently (exit 0).
    """
    # CI sets GITHUB_ACTIONS globally; this test explicitly models the
    # operator-approved local-only baseline path.
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    fed_items = [
        _make_item("SEC Rule A", "fr-1"),
        _make_item("CFTC Rule B", "fr-2", agency="CFTC"),
    ]
    finra_items = [
        _make_item("FINRA Notice 26-01", "finra-1", source="FINRA", agency="FINRA"),
    ]

    # Empty unified state => no prior state for either source.
    monkeypatch.setenv("REGULATORY_MONITOR_BASELINE_APPROVED", "I_UNDERSTAND")
    code, saved_state, report_items = _run_main(
        monkeypatch,
        state={},
        fed_items=fed_items,
        finra_items=finra_items,
        args=["--initialize-baseline"],
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


def test_missing_regulatory_state_fails_before_fetch_or_write(monkeypatch):
    """A scheduled run must not baseline an absent regulatory section silently."""
    state = {
        "version": 1,
        "sources": {
            "learn": {"last_run": "2026-08-01T00:00:00+00:00"},
        },
    }
    fetch_calls = []
    save_calls = []

    monkeypatch.setattr(regulatory_monitor, "load_state", lambda *a, **k: state)
    monkeypatch.setattr(
        regulatory_monitor,
        "fetch_federal_register_documents",
        lambda *a, **k: fetch_calls.append("federal") or [],
    )
    monkeypatch.setattr(
        regulatory_monitor,
        "fetch_finra_notices",
        lambda *a, **k: fetch_calls.append("finra") or [],
    )
    monkeypatch.setattr(
        regulatory_monitor,
        "save_state_atomic",
        lambda *a, **k: save_calls.append(a),
    )
    monkeypatch.setattr(sys, "argv", ["regulatory_monitor.py"])

    with pytest.raises(SystemExit) as exc:
        regulatory_monitor.main()

    assert exc.value.code == 2
    assert fetch_calls == []
    assert save_calls == []


def test_corrupt_regulatory_state_fails_before_baseline_suppression(monkeypatch):
    """Malformed entries/last_run cannot trigger implicit first-run baseline mode."""
    state = {
        "version": 1,
        "sources": {
            regulatory_monitor.SOURCE_KEY_FEDERAL_REGISTER: {
                "last_run": "not-a-timestamp",
                "entries": [],
            },
            regulatory_monitor.SOURCE_KEY_FINRA: {
                "last_run": "2026-08-01T00:00:00+00:00",
                "entries": {},
            },
        },
    }
    monkeypatch.setattr(regulatory_monitor, "load_state", lambda *a, **k: state)
    monkeypatch.setattr(
        regulatory_monitor,
        "fetch_federal_register_documents",
        lambda *a, **k: pytest.fail("corrupt state must stop before fetching"),
    )
    monkeypatch.setattr(sys, "argv", ["regulatory_monitor.py"])

    with pytest.raises(SystemExit) as exc:
        regulatory_monitor.main()

    assert exc.value.code == 2


def test_known_incident_state_rejects_watermarks_without_coverage_proof(monkeypatch):
    """The e802babd 332/2 state cannot advance Aug-9 watermarks."""
    corrupt_state = {
        "version": 1,
        "sources": {
            regulatory_monitor.SOURCE_KEY_FEDERAL_REGISTER: {
                "last_run": "2026-08-09T08:21:38+00:00",
                "last_checked": "2026-08-09",
                "entries": {
                    f"2026-{number:05d}": "sha256:corrupt"
                    for number in range(332)
                },
            },
            regulatory_monitor.SOURCE_KEY_FINRA: {
                "last_run": "2026-08-09T08:21:38+00:00",
                "entries": {
                    f"FINRA 26-{number:02d}": "sha256:corrupt"
                    for number in range(1, 3)
                },
            },
        },
    }
    fetch_calls = []
    monkeypatch.setattr(regulatory_monitor, "load_state", lambda *a, **k: corrupt_state)
    monkeypatch.setattr(
        regulatory_monitor,
        "fetch_federal_register_documents",
        lambda *a, **k: fetch_calls.append("federal") or [],
    )
    monkeypatch.setattr(
        regulatory_monitor,
        "fetch_finra_notices",
        lambda *a, **k: fetch_calls.append("finra") or [],
    )
    monkeypatch.setattr(sys, "argv", ["regulatory_monitor.py"])

    with pytest.raises(SystemExit) as exc:
        regulatory_monitor.main()

    assert exc.value.code == 2
    assert fetch_calls == []


def test_coverage_proof_rejects_entry_count_or_digest_drift():
    """A proof cannot be reused after entries change under the watermark."""
    source_state = {
        "last_run": "2026-08-09T08:21:38+00:00",
        "last_checked": "2026-08-09",
        "entries": {"2026-00001": "sha256:one"},
        "coverage": {
            "schema_version": 1,
            "source": regulatory_monitor.SOURCE_KEY_FEDERAL_REGISTER,
            "entry_count": 1,
            "entries_digest": regulatory_monitor._entries_digest(
                {"2026-00001": "sha256:old"}
            ),
            "watermark": {
                "last_run": "2026-08-09T08:21:38+00:00",
                "last_checked": "2026-08-09",
            },
            "complete": True,
            "window_start": "2026-08-09",
            "query": {},
            "expected_count": 1,
            "fetched_count": 1,
            "pages_fetched": 1,
            "declared_pages": 1,
            "page_numbers": [1],
        },
    }

    errors = regulatory_monitor._validate_source_coverage(
        regulatory_monitor.SOURCE_KEY_FEDERAL_REGISTER,
        source_state,
    )

    assert any("entries_digest" in error for error in errors)


def test_finra_zero_result_coverage_proof_is_valid():
    """The explicit zero-result response is a complete, verifiable shape."""
    source_state = {
        "last_run": "2026-08-09T08:21:38+00:00",
        "entries": {},
        "coverage": {
            "schema_version": 1,
            "source": regulatory_monitor.SOURCE_KEY_FINRA,
            "entry_count": 0,
            "entries_digest": regulatory_monitor._entries_digest({}),
            "watermark": {"last_run": "2026-08-09T08:21:38+00:00"},
            "complete": True,
            "listing_mode": "complete-unfiltered",
            "listing_url": regulatory_monitor.FINRA_NOTICES_URL,
            "listing_record_count": 0,
            "pages_fetched": 1,
            "declared_pages": 0,
            "detail_count": 0,
            "page_numbers": [0],
            "page_identities": [
                {"requested": 0, "final": 0, "active": 0},
            ],
            "fetched_entry_identities": [],
            "fetched_entry_identity_digest": regulatory_monitor._identity_digest([]),
            "entry_identity_digest": regulatory_monitor._identity_digest([]),
            "alias_ledger": [],
            "alias_ledger_digest": regulatory_monitor._alias_ledger_digest([]),
            "raw_row_count": 0,
            "resolved_row_count": 0,
            "unresolved_row_count": 0,
            "unique_node_count": 0,
            "pass_proofs": [
                {
                    "token": "zero-pass-1",
                    "declared_pages": 0,
                    "pages_fetched": 1,
                    "page_numbers": [0],
                    "page_identities": [
                        {"requested": 0, "final": 0, "active": 0},
                    ],
                    "page_row_counts": [0],
                    "page_row_digests": [compute_hash("[]")],
                    "page_row_payloads": [[]],
                    "raw_row_count": 0,
                    "resolved_row_count": 0,
                    "unresolved_row_count": 0,
                    "unique_node_count": 0,
                },
                {
                    "token": "zero-pass-2",
                    "declared_pages": 0,
                    "pages_fetched": 1,
                    "page_numbers": [0],
                    "page_identities": [
                        {"requested": 0, "final": 0, "active": 0},
                    ],
                    "page_row_counts": [0],
                    "page_row_digests": [compute_hash("[]")],
                    "page_row_payloads": [[]],
                    "raw_row_count": 0,
                    "resolved_row_count": 0,
                    "unresolved_row_count": 0,
                    "unique_node_count": 0,
                },
            ],
            "duplicate_ledger": [],
            "conflict_ledger": [],
        },
    }

    assert regulatory_monitor._validate_source_coverage(
        regulatory_monitor.SOURCE_KEY_FINRA,
        source_state,
    ) == []


def test_finra_coverage_rejects_stale_unseen_entry():
    """A watermark cannot advance with an entry absent from fetched identities."""
    state_path = Path(__file__).resolve().parents[1] / "data" / "monitor-state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    source_state = deepcopy(
        state["sources"][regulatory_monitor.SOURCE_KEY_FINRA]
    )
    source_state["entries"]["FINRA stale-unseen"] = "sha256:stale"
    source_state["coverage"]["entry_count"] = len(source_state["entries"])
    source_state["coverage"]["entries_digest"] = regulatory_monitor._entries_digest(
        source_state["entries"]
    )
    source_state["coverage"]["entry_identity_digest"] = (
        regulatory_monitor._identity_digest(source_state["entries"])
    )

    errors = regulatory_monitor._validate_source_coverage(
        regulatory_monitor.SOURCE_KEY_FINRA,
        source_state,
    )

    assert any("stale or unaccounted identities" in error for error in errors)


def test_baseline_mode_requires_manual_approval_and_rejects_ci(monkeypatch):
    """Baseline initialization cannot be reached from an unattended workflow."""
    monkeypatch.delenv("REGULATORY_MONITOR_BASELINE_APPROVED", raising=False)
    monkeypatch.setattr(sys, "argv", ["regulatory_monitor.py", "--initialize-baseline"])
    with pytest.raises(SystemExit) as exc:
        regulatory_monitor.main()
    assert exc.value.code == 2

    monkeypatch.setenv("REGULATORY_MONITOR_BASELINE_APPROVED", "I_UNDERSTAND")
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    with pytest.raises(SystemExit) as exc:
        regulatory_monitor.main()
    assert exc.value.code == 2


def test_recovery_findings_do_not_suppress_post_watermark_high_items():
    """Trusted July-20 history must leave FINRA 26-15 and later items reportable."""
    pre_watermark = _make_item(
        "Historical notice",
        "FINRA 26-01",
        pub_date="2026-07-20",
        source="FINRA",
        agency="FINRA",
    )
    post_watermark = _make_item(
        "FINRA Requests Comment on Modernizing Best Execution Guidance",
        "FINRA 26-15",
        pub_date="2026-07-24",
        source="FINRA",
        agency="FINRA",
    )
    post_watermark.classification = regulatory_monitor.CLASSIFICATION_HIGH
    changed_known = _make_item(
        "Edited historical notice",
        "FINRA 26-01",
        abstract="Edited after the trusted watermark.",
        pub_date="2026-07-20",
        source="FINRA",
        agency="FINRA",
    )
    trusted = {
        "last_run": "2026-07-20T09:56:38.066467+00:00",
        "entries": {
            "FINRA 26-01": _item_hash(pre_watermark),
        },
    }

    findings = regulatory_monitor.check_for_recovery_items(
        regulatory_monitor.SOURCE_KEY_FINRA,
        [pre_watermark, post_watermark, changed_known],
        trusted,
    )

    assert {item.document_id for item in findings} == {
        "FINRA 26-15",
        "FINRA 26-01",
    }
    assert post_watermark.classification == regulatory_monitor.CLASSIFICATION_HIGH


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
    saved_fed = saved_state['sources'][regulatory_monitor.SOURCE_KEY_FEDERAL_REGISTER]
    assert saved_fed['entries']['fr-3'] == _item_hash(new_fed)


def test_successful_no_findings_runs_advance_cursor_across_committed_state(monkeypatch):
    """Exit-0 refresh progress must persist and continue from the next batch."""
    known_items = [
        _make_item(
            f"FINRA Notice 26-{number:02d}",
            f"FINRA 26-{number:02d}",
            source="FINRA",
            agency="FINRA",
            url=f"https://www.finra.org/rules-guidance/notices/26-{number:02d}",
        )
        for number in range(1, 41)
    ]
    entries = {
        item.document_id: _item_hash(item)
        for item in known_items
    }
    state = {
        "version": 1,
        "sources": {
            regulatory_monitor.SOURCE_KEY_FINRA: {
                "last_run": "2026-08-01T00:00:00+00:00",
                "entries": entries,
                "refresh_cursor": 0,
            },
        },
    }

    first_code, first_state, first_report = _run_main(
        monkeypatch,
        state=deepcopy(state),
        fed_items=[],
        finra_items=known_items,
        args=["--source", "finra"],
    )
    second_code, second_state, second_report = _run_main(
        monkeypatch,
        state=deepcopy(first_state),
        fed_items=[],
        finra_items=known_items,
        args=["--source", "finra"],
    )

    assert first_code == second_code == 0
    assert first_report is None and second_report is None
    first_finra = first_state["sources"][regulatory_monitor.SOURCE_KEY_FINRA]
    second_finra = second_state["sources"][regulatory_monitor.SOURCE_KEY_FINRA]
    assert first_finra["refresh_cursor"] == 25
    assert second_finra["refresh_cursor"] == 10
    assert second_finra["last_run"] != "2026-08-01T00:00:00+00:00"


class _FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


class _FakeHttpResponse:
    def __init__(self, status_code, *, retry_after=None, url="https://example.test"):
        self.status_code = status_code
        self.headers = {"Retry-After": str(retry_after)} if retry_after is not None else {}
        self.url = url
        self.text = "ok" if status_code == 200 else ""


def test_shared_fetch_page_honors_valid_retry_after(monkeypatch):
    """Shared monitor callers must wait the server-advertised 60 seconds."""
    responses = [
        _FakeHttpResponse(429, retry_after=60),
        _FakeHttpResponse(200),
    ]
    sleeps = []

    class Session:
        def get(self, *_args, **_kwargs):
            return responses.pop(0)

    monkeypatch.setattr(monitoring_shared.time, "sleep", sleeps.append)
    result = monitoring_shared.fetch_page("https://example.test", Session(), max_retries=2)

    assert result["status_code"] == 200
    assert sleeps == [60]


class _FakeSession:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return _FakeResponse(self.responses.pop(0))


def _federal_doc(document_id):
    return {
        "document_number": document_id,
        "title": f"Document {document_id}",
        "abstract": "",
        "publication_date": "2026-08-01",
        "type": "NOTICE",
        "html_url": f"https://www.federalregister.gov/{document_id}",
        "agencies": [{"slug": "securities-and-exchange-commission", "name": "SEC"}],
    }


def test_federal_register_fetches_and_validates_all_pages():
    """All API pages must be consumed and reconciled with the declared count."""
    session = _FakeSession([
        {
            "count": 3,
            "total_pages": 2,
            "results": [_federal_doc("fr-1"), _federal_doc("fr-2")],
            "next_page_url": "https://www.federalregister.gov/api/v1/documents?page=2",
        },
        {
            "count": 3,
            "total_pages": 2,
            "results": [_federal_doc("fr-3")],
            "next_page_url": None,
        },
    ])
    config = {
        "federal_register": {
            "agencies": [{"slug": "securities-and-exchange-commission", "short_name": "SEC"}],
            "document_types": ["NOTICE"],
        },
        "regulatory": {},
        "keyword_control_map": [],
    }

    result = regulatory_monitor.fetch_federal_register_documents(session, "2026-08-01", config)

    assert result.complete is True
    assert result.expected_count == 3
    assert result.pages_fetched == 2
    assert [item.document_id for item in result] == ["fr-1", "fr-2", "fr-3"]
    assert len(session.calls) == 2


def test_federal_register_zero_results_are_verified():
    """A valid zero-result response is complete; malformed emptiness is not."""
    session = _FakeSession([{"count": 0, "total_pages": None, "results": None, "next_page_url": None}])
    config = {"federal_register": {}, "regulatory": {}, "keyword_control_map": []}

    result = regulatory_monitor.fetch_federal_register_documents(session, "2999-01-01", config)

    assert result.complete is True
    assert result.expected_count == 0
    assert result == []


def test_federal_register_missing_page_link_fails_closed():
    """Declared pages must reconcile even when next_page_url disappears."""
    session = _FakeSession([{
        "count": 3,
        "total_pages": 2,
        "results": [_federal_doc("fr-1"), _federal_doc("fr-2"), _federal_doc("fr-3")],
        "next_page_url": None,
    }])
    config = {"federal_register": {}, "regulatory": {}, "keyword_control_map": []}

    result = regulatory_monitor.fetch_federal_register_documents(session, "2026-08-01", config)

    assert result.complete is False
    assert "declared 2 page(s), fetched 1" in result.error


def test_federal_register_contradictory_zero_metadata_fails_closed():
    """count=0 with a declared page is contradictory, not a valid empty result."""
    session = _FakeSession([{
        "count": 0,
        "total_pages": 1,
        "results": None,
        "next_page_url": None,
    }])
    config = {"federal_register": {}, "regulatory": {}, "keyword_control_map": []}

    result = regulatory_monitor.fetch_federal_register_documents(session, "2999-01-01", config)

    assert result.complete is False
    assert "zero-result" in result.error


def test_federal_register_overlap_fails_closed():
    """Overlapping pages must not silently overwrite or advance the watermark."""
    session = _FakeSession([
        {
            "count": 3,
            "total_pages": 2,
            "results": [_federal_doc("fr-1"), _federal_doc("fr-2")],
            "next_page_url": "https://www.federalregister.gov/api/v1/documents?page=2",
        },
        {
            "count": 3,
            "total_pages": 2,
            "results": [_federal_doc("fr-2")],
            "next_page_url": None,
        },
    ])
    config = {
        "federal_register": {
            "agencies": [{"slug": "securities-and-exchange-commission", "short_name": "SEC"}],
            "document_types": ["NOTICE"],
        },
        "regulatory": {},
        "keyword_control_map": [],
    }

    result = regulatory_monitor.fetch_federal_register_documents(session, "2026-08-01", config)

    assert result.complete is False
    assert "overlap" in result.error


def test_main_does_not_advance_state_on_incomplete_source(monkeypatch):
    """A partial source fetch must fail without saving state or generating a report."""
    state = {
        "version": 1,
        "sources": {
            regulatory_monitor.SOURCE_KEY_FEDERAL_REGISTER: {
                "last_run": "2026-08-01T00:00:00+00:00",
                "last_checked": "2026-08-01",
                "entries": {"fr-1": "sha256:old"},
            },
            regulatory_monitor.SOURCE_KEY_FINRA: {
                "last_run": "2026-08-01T00:00:00+00:00",
                "entries": {},
            },
        },
    }
    original_state = repr(state)
    save_calls = []
    report_calls = []

    monkeypatch.setattr(regulatory_monitor, "load_state", lambda *a, **k: state)
    monkeypatch.setattr(
        regulatory_monitor,
        "fetch_federal_register_documents",
        lambda *a, **k: regulatory_monitor.FetchResult(
            [_make_item("Partial", "fr-2")],
            complete=False,
            error="declared count mismatch",
        ),
    )
    monkeypatch.setattr(regulatory_monitor, "fetch_finra_notices", lambda *a, **k: [])
    monkeypatch.setattr(regulatory_monitor, "save_state_atomic", lambda *a, **k: save_calls.append(a))
    monkeypatch.setattr(regulatory_monitor, "generate_regulatory_report", lambda *a, **k: report_calls.append(a))
    monkeypatch.setattr(sys, "argv", ["regulatory_monitor.py"])

    with pytest.raises(SystemExit) as exc:
        regulatory_monitor.main()

    assert exc.value.code == 2
    assert save_calls == []
    assert report_calls == []
    assert repr(state) == original_state


def test_main_preserves_unrelated_learn_state(monkeypatch):
    """Regulatory updates must not roll back the unrelated Learn source."""
    learn_state = {
        "schema_version": 2,
        "last_run": "2026-08-08T06:54:59.825001+00:00",
        "urls": {"https://learn.example/item": {
            "last_checked": "2026-08-08T06:54:59.825001+00:00",
            "content_hash": "sha256:learn",
        }},
        "statistics": {
            "total_urls": 1,
            "last_run_critical_changes": 4,
            "last_run_high_changes": 3,
            "last_run_medium_changes": 2,
            "last_run_noise_changes": 1,
            "last_run_redirects": 0,
            "last_run_errors": 0,
        },
    }
    state = {
        "version": 1,
        "sources": {
            "learn": deepcopy(learn_state),
            regulatory_monitor.SOURCE_KEY_FEDERAL_REGISTER: {
                "last_run": "2026-08-07T00:00:00+00:00",
                "last_checked": "2026-08-07",
                "entries": {},
            },
            regulatory_monitor.SOURCE_KEY_FINRA: {
                "last_run": "2026-08-07T00:00:00+00:00",
                "entries": {},
            },
        },
    }
    code, saved_state, _ = _run_main(
        monkeypatch,
        state=state,
        fed_items=[],
        finra_items=[],
    )

    assert code == 0
    assert saved_state["sources"]["learn"] == learn_state


def _finra_listing_page(page, total_pages, records):
    rows = "\n".join(
        f'<tr><td><time datetime="{date}T12:00:00Z"></time>'
        f'<a href="{href}">{title}</a></td></tr>'
        for href, title, date in records
    )
    pager = (
        '<nav class="pagination">'
        f'<li class="page-item active"><span class="page-link">{page + 1}</span></li>'
        f'<a href="?page={total_pages - 1}">Last >> Last page</a>'
        '</nav>'
    )
    return f"<html><body>{rows}{pager}</body></html>"


def _finra_detail_page(title, date, summary):
    return f"""
    <html><body>
      <h1>{title}</h1>
      <div class="field--name-field-core-official-dt">
        <time datetime="{date}T12:00:00Z">{date}</time>
      </div>
      <div class="field--name-body"><h2>Summary</h2><p>{summary}</p>
        <h2>Action Required</h2><p>Comments are requested.</p>
      </div>
    </body></html>
    """


def _finra_request_base(url):
    """Remove only the pass cache token from a test request URL."""
    parsed = urlparse(url)
    query = parse_qs(parsed.query, keep_blank_values=True)
    query.pop(regulatory_monitor.FINRA_CACHE_BUST_PARAM, None)
    base = parsed._replace(query=urlencode(query, doseq=True))
    return urlunparse(base)


def _synthetic_finra_listing(rows):
    """Build a complete listing result for detail/duplicate unit tests."""
    proof = {
        "token": "test-pass-1",
        "declared_pages": 1,
        "pages_fetched": 1,
        "page_numbers": [0],
        "page_identities": [{"requested": 0, "final": 0, "active": 0}],
        "page_row_counts": [len(rows)],
        "page_row_digests": [compute_hash(json.dumps(
            [row["raw_payload"] for row in rows],
            sort_keys=True,
            separators=(",", ":"),
        ))],
        "raw_row_count": len(rows),
        "resolved_row_count": len(rows),
        "unresolved_row_count": 0,
        "unique_node_count": len({row["node_identity"] for row in rows}),
    }
    proof2 = dict(proof, token="test-pass-2")
    return {
        "complete": True,
        "rows": rows,
        "pass_proof": proof,
        "pages_fetched": 1,
        "declared_pages": 1,
        "cutoff_page": None,
        "coverage": {
            "complete": True,
            "listing_mode": "complete-unfiltered",
            "listing_url": regulatory_monitor.FINRA_NOTICES_URL,
            "listing_record_count": len(rows),
            "raw_row_count": len(rows),
            "resolved_row_count": len(rows),
            "unresolved_row_count": 0,
            "unique_node_count": len({row["node_identity"] for row in rows}),
            "pages_fetched": 1,
            "declared_pages": 1,
            "page_numbers": [0],
            "pass_proofs": [proof, proof2],
            "duplicate_ledger": [],
            "conflict_ledger": [],
        },
    }


def _synthetic_finra_row(url, node_identity, title="Notice 26-14"):
    payload = {"text": title, "links": [{"href": url, "text": title}]}
    return {
        "row_index": 0,
        "page": 0,
        "raw_payload": payload,
        "raw_row_digest": compute_hash(json.dumps(
            payload, sort_keys=True, separators=(",", ":")
        )),
        "detail_url": url,
        "node_identity": node_identity,
        "title": title,
        "listing_date": "2026-07-09",
        "unresolved": False,
    }


def test_finra_normalizes_index_php_and_numeric_node_links():
    """Legacy and node links resolve to stable same-origin identities."""
    assert regulatory_monitor._finra_normalize_detail_link(
        "/index.php/rules-guidance/notices/26-14"
    ) == (
        "https://www.finra.org/rules-guidance/notices/26-14",
        "url:/rules-guidance/notices/26-14",
    )
    assert regulatory_monitor._finra_normalize_detail_link(
        "/node/382806"
    ) == ("https://www.finra.org/node/382806", "node:382806")
    assert regulatory_monitor._finra_normalize_detail_link(
        "https://evil.example/notice"
    ) == (None, None)


def test_finra_listing_rows_preserve_legacy_targets_and_unresolved_rows():
    """Scoped Drupal rows retain supported aliases and fail closed on bad links."""
    soup = BeautifulSoup(
        """
        <div class="view-content">
          <div class="views-row">
            <a href="/index.php/rules-guidance/notices/26-14">Legacy notice</a>
          </div>
          <div class="views-row">
            <a href="/node/382806">Numeric node</a>
          </div>
          <div class="views-row">
            <a href="https://evil.example/notices/26-15">Unsupported notice</a>
          </div>
        </div>
        """,
        "html.parser",
    )

    rows, unresolved = regulatory_monitor._extract_finra_listing_rows(soup)

    assert len(rows) == 3
    assert unresolved == 1
    assert rows[0]["node_identity"] == "url:/rules-guidance/notices/26-14"
    assert rows[1]["node_identity"] == "node:382806"
    assert rows[2]["detail_url"] is None


def test_finra_active_last_page_is_included_in_declared_total():
    """An active zero-based page 91 proves a 92-page listing."""
    soup = BeautifulSoup(
        """
        <nav aria-labelledby="pagination-heading"><ul class="pagination">
          <li class="page-item active"><span class="page-link">92</span></li>
          <li><a href="?page=90">Last</a></li>
        </ul></nav>
        """,
        "html.parser",
    )
    assert regulatory_monitor._extract_finra_declared_pages(soup) == 92


def test_finra_same_numeric_node_duplicate_coalesces_after_detail_proof(monkeypatch):
    """Repeated numeric-node rows coalesce after identical authoritative details."""
    rows = [
        _synthetic_finra_row(
            "https://www.finra.org/node/382806",
            "node:382806",
            title="Legacy duplicate listing",
        ),
        _synthetic_finra_row(
            "https://www.finra.org/node/382806",
            "node:382806",
        ),
    ]
    listing = _synthetic_finra_listing(rows)
    detail = _finra_detail_page("Notice 26-14", "2026-07-09", "Stable content.")
    detail = detail.replace(
        "</body>", '<link rel="shortlink" href="/node/382806"></body>'
    )

    monkeypatch.setattr(
        regulatory_monitor, "_fetch_finra_listing_records",
        lambda *_args: listing,
    )
    monkeypatch.setattr(
        regulatory_monitor, "fetch_page",
        lambda url, _session, **_kwargs: {
            "status_code": 200,
            "content": detail,
            "final_url": url,
            "was_redirected": False,
            "error": None,
        },
    )
    result = regulatory_monitor.fetch_finra_notices(
        _FakeSession([]), {"regulatory": {}, "keyword_control_map": []}
    )
    assert result.complete is True
    assert len(result) == 1
    assert result.coverage["unique_node_count"] == 1
    assert len(result.coverage["duplicate_ledger"]) == 1
    assert result.coverage["duplicate_ledger"][0]["raw_row_conflicts_with_first"] is True


def test_finra_same_numeric_node_conflicting_detail_fails_closed(monkeypatch):
    """A duplicate node whose authoritative content changes is unverifiable."""
    rows = [
        _synthetic_finra_row(
            "https://www.finra.org/rules-guidance/notices/26-14",
            "url:/rules-guidance/notices/26-14",
        ),
        _synthetic_finra_row(
            "https://www.finra.org/node/382806",
            "node:382806",
        ),
    ]
    listing = _synthetic_finra_listing(rows)
    details = {
        "https://www.finra.org/rules-guidance/notices/26-14":
            _finra_detail_page("Notice 26-14", "2026-07-09", "Version one."),
        "https://www.finra.org/node/382806":
            _finra_detail_page("Notice 26-14", "2026-07-09", "Version two."),
    }
    for key in details:
        details[key] = details[key].replace(
            "</body>", '<link rel="shortlink" href="/node/382806"></body>'
        )
    monkeypatch.setattr(
        regulatory_monitor, "_fetch_finra_listing_records",
        lambda *_args: listing,
    )
    monkeypatch.setattr(
        regulatory_monitor, "fetch_page",
        lambda url, _session, **_kwargs: {
            "status_code": 200,
            "content": details[url],
            "final_url": url,
            "was_redirected": False,
            "error": None,
        },
    )
    result = regulatory_monitor.fetch_finra_notices(
        _FakeSession([]), {"regulatory": {}, "keyword_control_map": []}
    )
    assert result.complete is False
    assert "duplicate detail conflict" in result.error


def test_finra_authoritative_node_resolves_duplicate_listing_date_conflict(monkeypatch):
    """A stale duplicate row is safe only when another URL resolves its node/detail."""
    rows = [
        _synthetic_finra_row(
            "https://www.finra.org/rules-guidance/notices/fyi-10-2002",
            "url:/rules-guidance/notices/fyi-10-2002",
            title="FYI 10-2002",
        ),
        _synthetic_finra_row(
            "https://www.finra.org/node/126166",
            "node:126166",
            title="FYI 10-2002 (legacy)",
        ),
    ]
    rows[0]["listing_date"] = "2002-10-01"
    rows[1]["listing_date"] = "2002-10-02"
    listing = _synthetic_finra_listing(rows)
    detail = _finra_detail_page("FYI 10-2002", "2002-10-02", "Stable content.")
    detail = detail.replace(
        "</body>", '<link rel="shortlink" href="/node/126166"></body>'
    )
    monkeypatch.setattr(
        regulatory_monitor, "_fetch_finra_listing_records",
        lambda *_args: listing,
    )
    monkeypatch.setattr(
        regulatory_monitor, "fetch_page",
        lambda url, _session, **_kwargs: {
            "status_code": 200,
            "content": detail,
            "final_url": url,
            "was_redirected": False,
            "error": None,
        },
    )

    result = regulatory_monitor.fetch_finra_notices(
        _FakeSession([]), {"regulatory": {}, "keyword_control_map": []}
    )

    assert result.complete is True
    assert len(result) == 1
    duplicate = result.coverage["duplicate_ledger"][0]
    assert duplicate["resolves_listing_date_conflict"] is True


def test_finra_unresolved_listing_row_fails_closed(monkeypatch):
    """A scoped row without a supported detail target cannot complete."""
    listing = """
    <nav aria-labelledby="pagination-heading"><ul class="pagination">
      <li class="page-item active"><span class="page-link">1</span></li>
    </ul></nav>
    <table><tbody><tr><td><a href="https://evil.example/notices/26-14">
      Notice 26-14</a></td></tr></tbody></table>
    """
    monkeypatch.setattr(
        regulatory_monitor,
        "fetch_page",
        lambda url, _session, **_kwargs: {
            "status_code": 200,
            "content": listing,
            "final_url": url,
            "url": url,
            "was_redirected": False,
            "error": None,
        },
    )
    result = regulatory_monitor._fetch_finra_listing_pass(
        _FakeSession([]), None, "test-token"
    )
    assert result["complete"] is False
    assert "unresolved" in result["error"]


def test_finra_two_pass_shifted_rows_fail_closed(monkeypatch):
    """A [A,B]/[C] -> [X,A]/[B,C] shift fails after both passes complete."""
    def pass_result(pages, token):
        rows = []
        page_digests = []
        page_payloads = []
        for page, page_urls in enumerate(pages):
            page_rows = []
            for row_index, slug in enumerate(page_urls):
                row = _synthetic_finra_row(
                    f"https://www.finra.org/rules-guidance/notices/{slug}",
                    f"url:/rules-guidance/notices/{slug}",
                    title=slug,
                )
                row["page"] = page
                row["row_index"] = row_index
                page_rows.append(row)
            rows.extend(page_rows)
            payloads = [row["raw_payload"] for row in page_rows]
            page_payloads.append(payloads)
            page_digests.append(compute_hash(json.dumps(
                payloads,
                sort_keys=True,
                separators=(",", ":"),
            )))
        proof = {
            "token": token,
            "declared_pages": len(pages),
            "pages_fetched": len(pages),
            "page_numbers": list(range(len(pages))),
            "page_identities": [
                {"requested": page, "final": page, "active": page}
                for page in range(len(pages))
            ],
            "page_row_counts": [len(page) for page in pages],
            "page_row_digests": page_digests,
            "page_row_payloads": page_payloads,
            "raw_row_count": len(rows),
            "resolved_row_count": len(rows),
            "unresolved_row_count": 0,
            "unique_node_count": len({row["node_identity"] for row in rows}),
        }
        return {
            "complete": True,
            "rows": rows,
            "records": [
                (row["detail_url"], row["title"], row["listing_date"])
                for row in rows
            ],
            "pages_fetched": len(pages),
            "declared_pages": len(pages),
            "cutoff_page": None,
            "pass_proof": proof,
        }

    results = iter([
        pass_result([["A", "B"], ["C"]], "pass-1"),
        pass_result([["X", "A"], ["B", "C"]], "pass-2"),
    ])
    monkeypatch.setattr(
        regulatory_monitor,
        "_fetch_finra_listing_pass",
        lambda *_args: next(results),
    )
    result = regulatory_monitor._fetch_finra_listing_records(
        _FakeSession([]), None
    )
    assert result["complete"] is False
    assert "independent-pass mismatch" in result["error"]


def test_finra_passes_create_independent_sessions_sequentially(monkeypatch):
    """Pass two starts only after pass one has fully closed."""
    events = []

    class _PassSession:
        def close(self):
            events.append("close")

    proof = {
        "token": "pass",
        "declared_pages": 1,
        "pages_fetched": 1,
        "page_numbers": [0],
        "page_identities": [{"requested": 0, "final": 0, "active": 0}],
        "page_row_counts": [0],
        "page_row_digests": [compute_hash("[]")],
        "page_row_payloads": [[]],
        "raw_row_count": 0,
        "resolved_row_count": 0,
        "unresolved_row_count": 0,
        "unique_node_count": 0,
    }

    monkeypatch.setattr(
        regulatory_monitor,
        "_new_finra_pass_session",
        lambda _template: (events.append("new") or _PassSession()),
    )
    monkeypatch.setattr(
        regulatory_monitor,
        "_fetch_finra_listing_pass",
        lambda *_args: (
            events.append("fetch")
            or {
                "complete": True,
                "rows": [],
                "records": [],
                "pages_fetched": 1,
                "declared_pages": 1,
                "cutoff_page": None,
                "pass_proof": proof,
            }
        ),
    )

    result = regulatory_monitor._fetch_finra_listing_records(
        _FakeSession([]), None
    )

    assert result["complete"] is True
    assert events == ["new", "fetch", "close", "new", "fetch", "close"]


def test_finra_complete_unfiltered_listing_catches_taxonomy_omissions(monkeypatch):
    """Selected-year taxonomy omissions cannot make the unfiltered crawl incomplete."""
    monkeypatch.setattr(regulatory_monitor, "FINRA_REQUEST_INTERVAL_SECONDS", 0)
    page_records = {
        0: [
            ("/rules-guidance/notices/26-15", "Regulatory Notice 26-15", "2026-07-24"),
        ],
        1: [
            ("/rules-guidance/notices/26-05", "Regulatory Notice 26-05", "2026-02-27"),
        ],
    }
    details = {
        "/rules-guidance/notices/26-15": _finra_detail_page(
            "Notice 26-15", "2026-07-24", "Current notice content."
        ),
        "/rules-guidance/notices/26-05": _finra_detail_page(
            "Notice 26-05", "2026-02-27", "Omitted by selected-year taxonomy."
        ),
    }
    requested = []

    def fake_fetch_page(url, _session, **_kwargs):
        requested.append(url)
        base_url = _finra_request_base(url)
        if base_url == regulatory_monitor.FINRA_NOTICES_URL:
            page = 0
        elif "?page=" in base_url:
            page = int(base_url.rsplit("=", 1)[1])
        else:
            path = base_url.removeprefix("https://www.finra.org")
            return {
                "status_code": 200,
                "content": details[path],
                "final_url": url,
                "url": url,
                "was_redirected": False,
                "error": None,
            }
        content = _finra_listing_page(page, 2, page_records[page])
        return {
            "status_code": 200,
            "content": content,
            "final_url": url,
            "url": url,
            "was_redirected": False,
            "error": None,
        }

    monkeypatch.setattr(regulatory_monitor, "fetch_page", fake_fetch_page)
    result = regulatory_monitor.fetch_finra_notices(
        _FakeSession([]),
        {"regulatory": {}, "keyword_control_map": []},
        since_date="2026-08-08",
    )

    assert result.complete is True
    assert {item.document_id for item in result} == {"FINRA 26-15", "FINRA 26-05"}
    assert not any("combine_1" in url for url in requested)


def test_finra_paginates_to_cutoff_and_refetches_overlap_window(monkeypatch):
    """A 92-page listing is fully traversed despite an old-page cutoff."""
    monkeypatch.setattr(regulatory_monitor, "FINRA_REQUEST_INTERVAL_SECONDS", 0)
    total_pages = 92
    page_records = {
        0: [
            ("/rules-guidance/notices/26-15", "Regulatory Notice 26-15", "2026-07-24"),
            ("/rules-guidance/notices/information-notice-20260808",
             "Information Notice 8/8/26", "2026-08-08"),
        ],
        1: [("/rules-guidance/notices/26-14", "Regulatory Notice 26-14", "2026-07-10")],
        2: [("/rules-guidance/notices/26-13", "Regulatory Notice 26-13", "2026-08-01")],
        3: [("/rules-guidance/notices/26-12", "Regulatory Notice 26-12", "2026-07-01")],
        91: [("/rules-guidance/notices/26-99", "Regulatory Notice 26-99", "2026-06-15")],
    }
    for page in range(4, 91):
        page_records[page] = [(
            f"/rules-guidance/notices/information-notice-2026{page:04d}",
            f"Information Notice page {page}",
            "2026-06-01",
        )]
    details = {
        "/rules-guidance/notices/26-15": _finra_detail_page(
            "FINRA Requests Comment on Modernizing FINRA's Best Execution Guidance",
            "2026-07-24",
            "Edited summary for FINRA Rule 5310.",
        ),
        "/rules-guidance/notices/information-notice-20260808": _finra_detail_page(
            "Information Notice", "2026-08-08", "Current notice content."
        ),
        "/rules-guidance/notices/26-14": _finra_detail_page(
            "Older notice", "2026-07-10", "Older content."
        ),
        "/rules-guidance/notices/26-13": _finra_detail_page(
            "Backdated notice", "2026-08-01", "Backdated content."
        ),
        "/rules-guidance/notices/26-12": _finra_detail_page(
            "Overlap-window notice", "2026-07-01", "Overlap content."
        ),
        "/rules-guidance/notices/26-99": _finra_detail_page(
            "Backdated page 92 notice", "2026-06-15", "Page 92 content."
        ),
    }
    for page, records in page_records.items():
        for path, title, date in records:
            details.setdefault(
                path,
                _finra_detail_page(title, date, f"Content from listing page {page}."),
            )
    requested = []

    def fake_fetch_page(url, _session, **_kwargs):
        requested.append(url)
        base_url = _finra_request_base(url)
        if base_url == regulatory_monitor.FINRA_NOTICES_URL:
            page = 0
        elif "?page=" in base_url:
            page = int(base_url.rsplit("=", 1)[1])
        else:
            path = base_url.removeprefix("https://www.finra.org")
            content = details[path]
            return {
                "status_code": 200,
                "content": content,
                "final_url": url,
                "was_redirected": False,
                "error": None,
            }
        content = _finra_listing_page(page, total_pages, page_records[page])
        return {
            "status_code": 200,
            "content": content,
            "final_url": url,
            "was_redirected": False,
            "error": None,
        }

    monkeypatch.setattr(regulatory_monitor, "fetch_page", fake_fetch_page)
    result = regulatory_monitor.fetch_finra_notices(
        _FakeSession([]),
        {"regulatory": {}, "keyword_control_map": []},
        since_date="2026-08-08",
    )

    assert result.complete is True
    assert result.declared_pages == total_pages
    assert result.cutoff_page == 1
    assert result.pages_fetched == total_pages
    ids = {item.document_id for item in result}
    assert "FINRA 26-12" in ids
    assert "FINRA 26-99" in ids
    assert len(ids) == sum(len(records) for records in page_records.values())
    requested_bases = {_finra_request_base(url) for url in requested}
    assert "https://www.finra.org/rules-guidance/notices?page=2" in requested_bases
    assert "https://www.finra.org/rules-guidance/notices?page=3" in requested_bases
    assert "https://www.finra.org/rules-guidance/notices?page=91" in requested_bases
    edited = next(item for item in result if item.document_id == "FINRA 26-15")
    assert "Edited summary" in edited.abstract


def test_finra_pagination_overlap_detail_date_conflict_fails_closed(monkeypatch):
    """An unpaired listing/detail date conflict fails closed."""
    record = ("/rules-guidance/notices/26-15", "Regulatory Notice 26-15", "2026-07-24")
    pages = {
        regulatory_monitor.FINRA_NOTICES_URL: _finra_listing_page(0, 1, [record]),
        "https://www.finra.org/rules-guidance/notices/26-15": _finra_detail_page(
            "Notice 26-15", "2026-07-23", "Stable authoritative content."
        ),
    }

    def fake_fetch_page(url, _session, **_kwargs):
        lookup_url = _finra_request_base(url)
        return {
            "status_code": 200,
            "content": pages[lookup_url],
            "final_url": url,
            "was_redirected": False,
            "error": None,
        }

    monkeypatch.setattr(regulatory_monitor, "fetch_page", fake_fetch_page)
    result = regulatory_monitor.fetch_finra_notices(
        _FakeSession([]), {"regulatory": {}, "keyword_control_map": []}
    )

    assert result.complete is False
    assert "date conflict" in result.error


def test_finra_identical_listing_overlap_is_coalesced(monkeypatch):
    """Stable cross-page duplicate rows coalesce after detail verification."""
    record = ("/rules-guidance/notices/26-15", "Regulatory Notice 26-15", "2026-07-24")
    listing = {
        regulatory_monitor.FINRA_NOTICES_URL: _finra_listing_page(0, 2, [record]),
        "https://www.finra.org/rules-guidance/notices?page=1": _finra_listing_page(
            1, 2, [record]
        ),
        "https://www.finra.org/rules-guidance/notices/26-15": _finra_detail_page(
            "Notice", "2026-07-24", "Stable content."
        ),
    }

    monkeypatch.setattr(regulatory_monitor, "FINRA_REQUEST_INTERVAL_SECONDS", 0)
    monkeypatch.setattr(
        regulatory_monitor,
        "fetch_page",
        lambda url, _session, **_kwargs: {
            "status_code": 200,
            "content": listing[_finra_request_base(url)],
            "final_url": url,
            "was_redirected": False,
            "error": None,
        },
    )
    result = regulatory_monitor.fetch_finra_notices(
        _FakeSession([]), {"regulatory": {}, "keyword_control_map": []}
    )

    assert result.complete is True
    assert len(result) == 1
    assert len(result.coverage["duplicate_ledger"]) == 1


def test_finra_repeated_page_identity_fails_closed(monkeypatch):
    """A response claiming the previous page cannot advance coverage."""
    record = ("/rules-guidance/notices/26-15", "Regulatory Notice 26-15", "2026-07-24")
    listing = {
        regulatory_monitor.FINRA_NOTICES_URL: _finra_listing_page(0, 2, [record]),
        "https://www.finra.org/rules-guidance/notices?page=1": _finra_listing_page(
            0, 2, [record]
        ),
    }

    monkeypatch.setattr(regulatory_monitor, "FINRA_REQUEST_INTERVAL_SECONDS", 0)
    monkeypatch.setattr(
        regulatory_monitor,
        "fetch_page",
        lambda url, _session, **_kwargs: {
            "status_code": 200,
            "content": listing[_finra_request_base(url)],
            "final_url": url,
            "url": url,
            "was_redirected": False,
            "error": None,
        },
    )
    result = regulatory_monitor.fetch_finra_notices(
        _FakeSession([]), {"regulatory": {}, "keyword_control_map": []}
    )

    assert result.complete is False
    assert "identity mismatch" in result.error


def test_finra_active_pager_ignores_global_navigation_current_page():
    """Global aria-current navigation must not mask the listing pager."""
    soup = BeautifulSoup(
        """
        <a aria-current="page" class="nav-link active">Notices</a>
        <nav aria-labelledby="pagination-heading">
          <ul class="pagination">
            <li class="page-item active"><span class="page-link">1</span></li>
            <li class="page-item"><a class="page-link" href="?page=1">2</a></li>
          </ul>
        </nav>
        """,
        "html.parser",
    )

    assert regulatory_monitor._extract_finra_active_page(soup) == 0


def test_finra_listing_collects_all_notice_slug_types():
    """Election/trade notices are not silently omitted from full coverage."""
    soup = BeautifulSoup(
        """
        <table><tbody>
          <tr><td><a href="/rules-guidance/notices/election-notice-091809">
            Election Notice - 9/18/09</a></td></tr>
          <tr><td><a href="/rules-guidance/notices/trade-reporting-notice-022409">
            Trade Reporting Notice</a></td></tr>
          <tr><td><a href="/rules-guidance/notices/09-29">
            Regulatory Notice 09-29</a></td></tr>
        </tbody></table>
        """,
        "html.parser",
    )

    records = regulatory_monitor._extract_finra_notice_links(soup)

    assert [record[0].rsplit("/", 1)[-1] for record in records] == [
        "election-notice-091809",
        "trade-reporting-notice-022409",
        "09-29",
    ]


def test_finra_uses_authoritative_detail_fields_and_classifies_26_15(monkeypatch):
    """FINRA 26-15 must use its published date/summary, not URL heuristics."""
    listing_html = """
    <html><body>
      <nav aria-labelledby="pagination-heading">
        <ul class="pagination"><li class="page-item active"><span class="page-link">1</span></li></ul>
      </nav>
      <a href="/rules-guidance/notices/26-15">Regulatory Notice 26-15</a>
      <a href="/rules-guidance/notices/26-14">Regulatory Notice 26-14</a>
    </body></html>
    """
    detail_26_15 = """
    <html><body>
      <h1>FINRA Requests Comment on Modernizing FINRA's Best Execution Guidance</h1>
      <div class="field--name-field-core-official-dt">
        <time datetime="2026-07-24T12:00:00Z">July 24, 2026</time>
      </div>
      <div class="field--name-body"><h2>Summary</h2>
        <p>A broker-dealer duty under FINRA Rule 5310 requires best execution.</p>
        <h2>Action Required</h2><p>Comments are requested.</p>
      </div>
    </body></html>
    """
    detail_26_14 = """
    <html><body>
      <h1>Older notice</h1>
      <div class="field--name-field-core-official-dt">
        <time datetime="2026-07-18T12:00:00Z">July 18, 2026</time>
      </div>
      <div class="field--name-body"><h2>Summary</h2><p>Older content.</p></div>
    </body></html>
    """

    def fake_fetch_page(url, _session, **_kwargs):
        pages = {
            regulatory_monitor.FINRA_NOTICES_URL: listing_html,
            "https://www.finra.org/rules-guidance/notices/26-15": detail_26_15,
            "https://www.finra.org/rules-guidance/notices/26-14": detail_26_14,
        }
        lookup_url = _finra_request_base(url)
        return {
            "status_code": 200,
            "content": pages[lookup_url],
            "final_url": url,
            "was_redirected": False,
            "error": None,
        }

    monkeypatch.setattr(regulatory_monitor, "fetch_page", fake_fetch_page)
    config = {
        "regulatory": {
            "medium_patterns": [
                {"pattern": r"\bbroker-dealer", "reason": "Broker-dealer regulation"}
            ]
        },
        "keyword_control_map": [],
    }

    result = regulatory_monitor.fetch_finra_notices(
        _FakeSession([]), config, since_date="2026-07-20"
    )

    assert result.complete is True
    assert {item.document_id for item in result} == {"FINRA 26-15", "FINRA 26-14"}
    item = next(item for item in result if item.document_id == "FINRA 26-15")
    assert item.title == "FINRA Requests Comment on Modernizing FINRA's Best Execution Guidance"
    assert item.publication_date == "2026-07-24"
    assert "broker-dealer" in item.abstract
    assert "Action Required" in item.substantive_content
    assert item.classification == regulatory_monitor.CLASSIFICATION_MEDIUM
    assert item.classification_reason == "Broker-dealer regulation"
    assert regulatory_monitor._item_content_hash(item) == compute_hash(item.substantive_content)


def test_finra_missing_date_remains_unknown(monkeypatch):
    """Missing FINRA publication metadata must remain empty, never January 1/current date."""
    listing_html = """
    <nav aria-labelledby="pagination-heading">
      <ul class="pagination"><li class="page-item active"><span class="page-link">1</span></li></ul>
    </nav>
    <a href="/rules-guidance/notices/26-15">Regulatory Notice 26-15</a>
    """
    detail_html = """
    <html><body><h1>Notice title</h1>
      <div class="field--name-body"><h2>Summary</h2><p>Broker-dealer content.</p></div>
    </body></html>
    """

    def fake_fetch_page(url, _session, **_kwargs):
        content = (
            listing_html
            if _finra_request_base(url) == regulatory_monitor.FINRA_NOTICES_URL
            else detail_html
        )
        return {"status_code": 200, "content": content, "final_url": url,
                "was_redirected": False, "error": None}

    monkeypatch.setattr(regulatory_monitor, "fetch_page", fake_fetch_page)
    result = regulatory_monitor.fetch_finra_notices(
        _FakeSession([]),
        {"regulatory": {}, "keyword_control_map": []},
    )

    assert result.complete is True
    assert result[0].publication_date == ""
    assert "2026-01-01" not in result[0].publication_date


def test_workflow_fails_closed_for_monitor_exit_two_or_more():
    """Preflight and undocumented monitor statuses fail the mutation job."""
    workflow = (
        Path(__file__).resolve().parents[1]
        / ".github"
        / "workflows"
        / "regulatory-monitoring.yml"
    ).read_text(encoding="utf-8")

    assert 'exit "$EXIT_CODE"' in workflow
    assert '0|1)' in workflow
    assert "undocumented exit code" in workflow
    assert "- name: Validate monitor outcome and outputs" in workflow
    assert 'if: always()' in workflow
    assert 'steps.monitor.outcome' in workflow
    assert "exit_code output is missing or undocumented" in workflow
    assert "continue-on-error:" not in workflow


def test_workflow_persists_exit0_dirty_state_without_clean_run_pr_noise():
    """Exit-0 state progress gets a maintenance PR; a clean run stays silent."""
    workflow = (
        Path(__file__).resolve().parents[1]
        / ".github"
        / "workflows"
        / "regulatory-monitoring.yml"
    ).read_text(encoding="utf-8")

    assert "- name: Detect persisted monitor changes" in workflow
    assert "git status --porcelain=v1 --untracked-files=all" in workflow
    assert 'echo "changed=true"' in workflow
    assert 'echo "changed=false"' in workflow
    assert (
        'if [ "$EXIT_CODE" = "1" ] || { [ "$EXIT_CODE" = "0" ] && '
        '[ "$STATE_CHANGED" = "true" ]; }; then'
    ) in workflow
    assert "steps.should_create_pr.outputs.create_pr == 'true'" in workflow
    assert "successful state maintenance" in workflow
    assert 'echo "automerge_eligible=true" >> $GITHUB_OUTPUT' in workflow


def test_workflow_exit_semantics_keep_findings_and_fail_closed_runs_distinct():
    """Exit 1 stages findings; exit >=2 cannot reach state PR creation."""
    workflow = (
        Path(__file__).resolve().parents[1]
        / ".github"
        / "workflows"
        / "regulatory-monitoring.yml"
    ).read_text(encoding="utf-8")

    assert "reports/monitoring/*.md" in workflow
    assert "data/monitor-state.json.backup" in workflow
    assert "echo \"run_kind=findings\"" in workflow
    assert "steps.monitor.outputs.exit_code == '0' ||" in workflow
    assert "steps.monitor.outputs.exit_code == '1'" in workflow
    assert 'if [ "$EXIT_CODE" -eq 1 ]; then' in workflow
    assert "if: steps.create_pr.outputs.pull-request-number && steps.monitor.outputs.exit_code == '1'" in workflow
    assert "steps.should_create_pr.outputs.create_pr == 'true'" in workflow
    assert "steps.monitor.outputs.exit_code == '0' ||" in workflow


def test_workflow_mutation_is_default_branch_only_and_cas_checked():
    """Feature refs are read-only; mutation has isolated write permissions and CAS."""
    workflow = (
        Path(__file__).resolve().parents[1]
        / ".github"
        / "workflows"
        / "regulatory-monitoring.yml"
    ).read_text(encoding="utf-8")

    assert "validate-read-only:" in workflow
    assert "monitor-regulatory:" in workflow
    assert "contents: read" in workflow
    assert "contents: write" in workflow
    assert "pull-requests: read" in workflow
    assert "pull-requests: write" in workflow
    assert "python scripts/regulatory_monitor.py --dry-run" in workflow
    assert "persist-credentials: false" in workflow
    assert "Checkout trusted default branch" in workflow
    assert "Verify trusted default-branch checkout" in workflow
    assert "Generate GitHub App token" in workflow
    assert "STATE_SHA_BEFORE=$(sha256sum data/monitor-state.json" in workflow
    assert "- name: Validate default-branch monitor CAS" in workflow
    assert 'git fetch --no-tags origin "$DEFAULT_BRANCH"' in workflow
    assert 'BASE_STATE=$(git show "$EXPECTED_BASE:data/monitor-state.json"' in workflow
    assert "steps.cas.outputs.valid == 'true'" in workflow
    assert "baseRefName,baseRefOid" in workflow
    assert "Maintenance PR base CAS mismatch" in workflow

    state_changes_block = workflow.split(
        "- name: Detect persisted monitor changes", 1
    )[1].split("- name:", 1)[0]
    cas_block = workflow.split(
        "- name: Validate default-branch monitor CAS", 1
    )[1].split("- name:", 1)[0]
    for block in (state_changes_block, cas_block):
        assert "steps.monitor.outcome == 'success'" in block
        assert "github.event_name != 'pull_request'" in block
        assert (
            "github.ref_name == github.event.repository.default_branch"
            in block
        )

    read_only_block = workflow.split("validate-read-only:", 1)[1].split(
        "monitor-regulatory:", 1
    )[0]
    assert "contents: write" not in read_only_block
    assert "pull-requests: write" not in read_only_block
    assert "private-key:" not in read_only_block


def test_baseline_initialization_requires_manual_approval_and_is_not_in_workflow():
    """The exceptional baseline path cannot be invoked by Actions automation."""
    workflow = (
        Path(__file__).resolve().parents[1]
        / ".github"
        / "workflows"
        / "regulatory-monitoring.yml"
    ).read_text(encoding="utf-8")

    assert "--initialize-baseline" not in workflow
    assert "REGULATORY_MONITOR_BASELINE_APPROVED=I_UNDERSTAND" not in workflow


def test_recovery_state_restores_complete_regulatory_baseline_without_watermark_only_corruption():
    """Recovery state must retain all sources and keep primary/backup identical."""
    primary_path = Path(__file__).resolve().parents[1] / "data" / "monitor-state.json"
    backup_path = primary_path.with_name("monitor-state.json.backup")
    primary = json.loads(primary_path.read_text(encoding="utf-8"))
    backup = json.loads(backup_path.read_text(encoding="utf-8"))

    assert primary == backup
    assert primary["sources"]["learn"] == backup["sources"]["learn"]
    assert len(primary["sources"][regulatory_monitor.SOURCE_KEY_FEDERAL_REGISTER]["entries"]) == 506
    assert len(primary["sources"][regulatory_monitor.SOURCE_KEY_FINRA]["entries"]) == 3616
    assert len(primary["sources"][regulatory_monitor.SOURCE_KEY_FINRA]["entries"]) >= 57
    assert primary["sources"][regulatory_monitor.SOURCE_KEY_FEDERAL_REGISTER]["last_checked"] >= "2026-08-09"
    assert primary["sources"][regulatory_monitor.SOURCE_KEY_FINRA]["last_run"] >= "2026-08-09"
    finra_coverage = primary["sources"][regulatory_monitor.SOURCE_KEY_FINRA]["coverage"]
    assert finra_coverage["raw_row_count"] == 3671
    assert finra_coverage["detail_count"] == 3616
    assert finra_coverage["unique_node_count"] == 3616
    assert len(finra_coverage["duplicate_ledger"]) == 55
    assert len(finra_coverage["alias_ledger"]) == 622
    assert finra_coverage["alias_ledger_digest"] == regulatory_monitor._alias_ledger_digest(
        finra_coverage["alias_ledger"]
    )
    assert not (
        {
            item["old_identity"] for item in finra_coverage["alias_ledger"]
        }
        & set(primary["sources"][regulatory_monitor.SOURCE_KEY_FINRA]["entries"])
    )
    assert finra_coverage["pages_fetched"] == 92
    assert finra_coverage["declared_pages"] == 92
    assert len(finra_coverage["fetched_entry_identities"]) == finra_coverage["detail_count"]
    assert finra_coverage["entry_identity_digest"] == regulatory_monitor._identity_digest(
        sorted(primary["sources"][regulatory_monitor.SOURCE_KEY_FINRA]["entries"])
    )


def test_legacy_finra_proof_requires_explicit_recovery_migration():
    """Legacy FINRA coverage is admitted only by the approved recovery path."""
    state_path = Path(__file__).resolve().parents[1] / "data" / "monitor-state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    legacy_state = deepcopy(state)
    coverage = legacy_state["sources"][regulatory_monitor.SOURCE_KEY_FINRA]["coverage"]
    prior_alias_ledger = coverage.get("alias_ledger", [])
    prior_migration_ledger = coverage.get("migration_ledger", [])
    for key in (
        "alias_ledger",
        "alias_ledger_digest",
    ):
        coverage.pop(key, None)
    coverage["migration_ledger"] = prior_migration_ledger or [
        {
            "identity": item["old_identity"],
            "reason": item["evidence"]["reason"],
        }
        for item in prior_alias_ledger
    ]
    for item in prior_alias_ledger:
        legacy_state["sources"][regulatory_monitor.SOURCE_KEY_FINRA]["entries"][
            item["old_identity"]
        ] = legacy_state["sources"][regulatory_monitor.SOURCE_KEY_FINRA][
            "entries"
        ][item["canonical_identity"]]
    legacy_entries = legacy_state["sources"][regulatory_monitor.SOURCE_KEY_FINRA][
        "entries"
    ]
    coverage["entry_count"] = len(legacy_entries)
    coverage["entries_digest"] = regulatory_monitor._entries_digest(legacy_entries)

    normal_errors = regulatory_monitor._validate_regulatory_state(
        legacy_state,
        [
            regulatory_monitor.SOURCE_KEY_FEDERAL_REGISTER,
            regulatory_monitor.SOURCE_KEY_FINRA,
        ],
    )
    assert any("alias_ledger" in error for error in normal_errors)

    recovery_errors = regulatory_monitor._validate_regulatory_state(
        legacy_state,
        [
            regulatory_monitor.SOURCE_KEY_FEDERAL_REGISTER,
            regulatory_monitor.SOURCE_KEY_FINRA,
        ],
        allow_legacy_finra_identity_proof=True,
    )
    assert recovery_errors == []


def test_known_corrupt_incident_state_fails_coverage_validation():
    """The 332/2 state cannot hide behind Aug-9 watermarks."""
    state_path = Path(__file__).resolve().parents[1] / "data" / "monitor-state.json"
    incident = json.loads(state_path.read_text(encoding="utf-8"))
    incident["sources"][regulatory_monitor.SOURCE_KEY_FEDERAL_REGISTER]["entries"] = dict(
        list(
            incident["sources"][
                regulatory_monitor.SOURCE_KEY_FEDERAL_REGISTER
            ]["entries"].items()
        )[:332]
    )
    incident["sources"][regulatory_monitor.SOURCE_KEY_FINRA]["entries"] = dict(
        list(
            incident["sources"][regulatory_monitor.SOURCE_KEY_FINRA]["entries"].items()
        )[:2]
    )
    for source_key in (
        regulatory_monitor.SOURCE_KEY_FEDERAL_REGISTER,
        regulatory_monitor.SOURCE_KEY_FINRA,
    ):
        source_state = incident["sources"][source_key]
        source_state["last_run"] = "2026-08-09T20:39:20+00:00"
        coverage = source_state["coverage"]
        coverage["entry_count"] = len(source_state["entries"])
        coverage["entries_digest"] = regulatory_monitor._entries_digest(
            source_state["entries"]
        )
        coverage["watermark"]["last_run"] = source_state["last_run"]
    fr_coverage = incident["sources"][
        regulatory_monitor.SOURCE_KEY_FEDERAL_REGISTER
    ]["coverage"]
    fr_coverage["expected_count"] = 332
    fr_coverage["fetched_count"] = 332
    errors = regulatory_monitor._validate_regulatory_state(
        incident,
        [
            regulatory_monitor.SOURCE_KEY_FEDERAL_REGISTER,
            regulatory_monitor.SOURCE_KEY_FINRA,
        ],
    )
    assert any(
        "identity digest" in error or "unaccounted identities" in error
        for error in errors
    )


def test_dry_run_does_not_fetch_or_persist_watermarks(monkeypatch):
    """Feature/PR validation must not call sources or write monitor state."""
    def fail_fetch(*_args, **_kwargs):
        raise AssertionError("dry-run must not fetch source data")

    def fail_save(*_args, **_kwargs):
        raise AssertionError("dry-run must not persist state")

    monkeypatch.setattr(regulatory_monitor, "fetch_federal_register_documents", fail_fetch)
    monkeypatch.setattr(regulatory_monitor, "fetch_finra_notices", fail_fetch)
    monkeypatch.setattr(regulatory_monitor, "save_state_atomic", fail_save)
    monkeypatch.setattr(regulatory_monitor, "load_state", lambda *a, **k: {})
    monkeypatch.setattr(sys, "argv", ["regulatory_monitor.py", "--dry-run"])

    with pytest.raises(SystemExit) as exc:
        regulatory_monitor.main()

    assert exc.value.code == 0


def test_finra_missing_pager_fails_closed(monkeypatch):
    """Notice links without authoritative pager metadata must not imply one page."""
    listing_html = '<a href="/rules-guidance/notices/26-15">Regulatory Notice 26-15</a>'

    monkeypatch.setattr(
        regulatory_monitor,
        "fetch_page",
        lambda _url, _session, **_kwargs: {
            "status_code": 200,
            "content": listing_html,
            "final_url": regulatory_monitor.FINRA_NOTICES_URL,
            "was_redirected": False,
            "error": None,
        },
    )
    result = regulatory_monitor.fetch_finra_notices(
        _FakeSession([]),
        {"regulatory": {}, "keyword_control_map": []},
    )

    assert result.complete is False
    assert "pagination metadata" in result.error


def test_finra_malformed_pager_fails_closed(monkeypatch):
    """A pager with an unparseable page value is not silently treated as page one."""
    listing_html = """
    <nav aria-labelledby="pagination-heading">
      <ul class="pagination"><li><a href="?page=not-a-number">Next</a></li></ul>
    </nav>
    <a href="/rules-guidance/notices/26-15">Regulatory Notice 26-15</a>
    """

    monkeypatch.setattr(
        regulatory_monitor,
        "fetch_page",
        lambda _url, _session, **_kwargs: {
            "status_code": 200,
            "content": listing_html,
            "final_url": regulatory_monitor.FINRA_NOTICES_URL,
            "was_redirected": False,
            "error": None,
        },
    )
    result = regulatory_monitor.fetch_finra_notices(
        _FakeSession([]),
        {"regulatory": {}, "keyword_control_map": []},
    )

    assert result.complete is False
    assert "pagination metadata" in result.error


def test_finra_authoritative_single_page_and_zero_result_shapes(monkeypatch):
    """Only explicit one-page or zero-result markup may complete without page links."""
    detail = _finra_detail_page("Notice title", "2026-07-24", "Summary text.")
    requested = []

    def fake_single_page(url, _session, **_kwargs):
        requested.append(url)
        if _finra_request_base(url) == regulatory_monitor.FINRA_NOTICES_URL:
            content = """
            <nav aria-labelledby="pagination-heading">
              <ul class="pagination">
                <li class="page-item active"><span class="page-link">1</span></li>
              </ul>
            </nav>
            <a href="/rules-guidance/notices/26-15">Regulatory Notice 26-15</a>
            """
        else:
            content = detail
        return {"status_code": 200, "content": content, "final_url": url,
                "was_redirected": False, "error": None}

    monkeypatch.setattr(regulatory_monitor, "fetch_page", fake_single_page)
    one_page = regulatory_monitor.fetch_finra_notices(
        _FakeSession([]), {"regulatory": {}, "keyword_control_map": []}
    )
    assert one_page.complete is True
    assert one_page.declared_pages == 1

    monkeypatch.setattr(
        regulatory_monitor,
        "fetch_page",
        lambda url, _session, **_kwargs: {
            "status_code": 200,
            "content": '<div class="view-empty">No results found.</div>',
            "final_url": url,
            "was_redirected": False,
            "error": None,
        },
    )
    zero = regulatory_monitor.fetch_finra_notices(
        _FakeSession([]), {"regulatory": {}, "keyword_control_map": []}
    )
    assert zero.complete is True
    assert zero == []
    assert zero.declared_pages == 0


def test_finra_refreshes_known_notice_outside_listing_window(monkeypatch):
    """Known old notices are detailed every run even when cutoff pagination omits them."""
    listing = _finra_listing_page(
        0, 1, [("/rules-guidance/notices/26-15", "Regulatory Notice 26-15", "2026-07-24")]
    )
    details = {
        "https://www.finra.org/rules-guidance/notices/26-15": _finra_detail_page(
            "Current notice", "2026-07-24", "Current summary."
        ),
        "https://www.finra.org/rules-guidance/notices/26-14": _finra_detail_page(
            "Edited old notice", "2026-07-09", "Edited background."
        ),
    }
    requested = []

    def fake_fetch_page(url, _session, **_kwargs):
        requested.append(url)
        base_url = _finra_request_base(url)
        return {
            "status_code": 200,
            "content": listing if base_url == regulatory_monitor.FINRA_NOTICES_URL
            else details[base_url],
            "final_url": url,
            "was_redirected": False,
            "error": None,
        }

    monkeypatch.setattr(regulatory_monitor, "fetch_page", fake_fetch_page)
    result = regulatory_monitor.fetch_finra_notices(
        _FakeSession([]),
        {"regulatory": {}, "keyword_control_map": []},
        since_date="2026-07-24",
        known_urls=["https://www.finra.org/rules-guidance/notices/26-14"],
    )

    assert result.complete is True
    assert {item.document_id for item in result} == {"FINRA 26-15", "FINRA 26-14"}
    assert "https://www.finra.org/rules-guidance/notices/26-14" in requested


def test_finra_known_refresh_is_bounded_and_resumable():
    """Known historical URLs advance through a deterministic round-robin batch."""
    source_state = {
        "entries": {
            f"FINRA 26-{number:02d}": "sha256:old"
            for number in range(1, 41)
        },
        "refresh_cursor": 39,
    }

    batch = regulatory_monitor._finra_refresh_batch(source_state)

    assert len(batch) == regulatory_monitor.FINRA_REFRESH_BATCH_SIZE
    assert batch[0].endswith("/26-40")
    assert batch[1].endswith("/26-01")
    assert len(set(batch)) == len(batch)


def test_finra_hashes_and_classifies_non_summary_edits(monkeypatch):
    """Changes in Action Required/Background content affect provenance and tier."""
    listing = _finra_listing_page(
        0, 1, [("/rules-guidance/notices/26-14", "Regulatory Notice 26-14", "2026-07-09")]
    )
    base_detail = """
    <main><h1>Notice</h1>
      <div class="field--name-field-core-official-dt"><time datetime="2026-07-09T00:00:00Z"></time></div>
      <div class="field--name-body"><h2>Summary</h2><p>Stable summary.</p>
      <h2>Action Required</h2><p>Stable action.</p>
      <h2>Background &amp; Discussion</h2><p>Stable background.</p>
      <h2>Endnotes</h2><p>Stable note.</p></div>
    </main>
    """
    edited_detail = base_detail.replace("Stable background.", "urgent marker in the background.")
    pages = {regulatory_monitor.FINRA_NOTICES_URL: listing}

    def run(detail):
        pages["https://www.finra.org/rules-guidance/notices/26-14"] = detail
        monkeypatch.setattr(
            regulatory_monitor,
            "fetch_page",
            lambda url, _session, **_kwargs: {
                "status_code": 200,
                "content": pages[_finra_request_base(url)],
                "final_url": url,
                "was_redirected": False,
                "error": None,
            },
        )
        return regulatory_monitor.fetch_finra_notices(
            _FakeSession([]),
            {
                "regulatory": {
                    "critical_patterns": [
                        {"pattern": r"urgent marker", "reason": "Urgent notice content"}
                    ]
                },
                "keyword_control_map": [],
            },
        )[0]

    first = run(base_detail)
    second = run(edited_detail)
    assert "Background & Discussion" in first.substantive_content
    assert "Endnotes" in first.substantive_content
    assert regulatory_monitor._item_content_hash(first) != regulatory_monitor._item_content_hash(second)
    assert second.classification == regulatory_monitor.CLASSIFICATION_CRITICAL


def _finra_canonicalization_fixture(
    *,
    comments: str = "No comments.",
    attachment_href: str = "/sites/default/files/attachment-v1.pdf",
    deadline: str = "09/11/2026",
    contact_href: str = "",
    formatted: bool = False,
) -> str:
    """Build a notice with separate mutable comments and authoritative content."""
    action = (
        "<p>Action <strong>required</strong>.</p>"
        if formatted
        else "<p>Action required.</p>"
    )
    contact = (
        f'<p>Contact <a href="{contact_href}">FINRA staff</a>.</p>'
        if contact_href
        else ""
    )
    return f"""
    <html><body>
      <h1>Regulatory Notice 26-14</h1>
      <div class="field--name-field-core-official-dt">
        <time datetime="2026-07-09T00:00:00Z"></time>
      </div>
      <div class="field--name-field-notice-subtitle-tx">
        Comment Period Expires: {deadline}
      </div>
      <div id="notice" class="tab-pane">
        <h2>Summary</h2><p>Stable authoritative summary.</p>
        <h2>Action Required</h2>{action}
        {contact}
        <h2>Endnotes</h2>
        <p><a href="#_ednref1">1</a> Authoritative endnote.</p>
      </div>
      <div id="block-noticeattachment">
        <a href="{attachment_href}?utm_source=tracking">Attachment A</a>
      </div>
      <div id="comments" class="tab-pane">
        <h2>Comments (1)</h2><p>{comments}</p>
      </div>
    </body></html>
    """


def test_finra_comments_do_not_change_authoritative_hash_or_classification():
    """Mutable public comments must be excluded from FINRA provenance."""
    base = BeautifulSoup(
        _finra_canonicalization_fixture(comments="Alice Example"),
        "html.parser",
    )
    changed = BeautifulSoup(
        _finra_canonicalization_fixture(
            comments="Bob Example: urgent marker; 999 additional comments"
        ),
        "html.parser",
    )

    base_content = regulatory_monitor._extract_finra_substantive_content(base)
    changed_content = regulatory_monitor._extract_finra_substantive_content(changed)
    assert "Alice Example" not in base_content
    assert "Bob Example" not in changed_content
    assert regulatory_monitor.compute_hash(base_content) == (
        regulatory_monitor.compute_hash(changed_content)
    )

    config = {
        "regulatory": {
            "critical_patterns": [
                {"pattern": r"urgent marker", "reason": "Comment-only signal"}
            ]
        }
    }
    assert regulatory_monitor.classify_regulatory_relevance(
        "Regulatory Notice 26-14", base_content, config
    ) == regulatory_monitor.classify_regulatory_relevance(
        "Regulatory Notice 26-14", changed_content, config
    )


def test_finra_canonicalization_preserves_attachment_targets_and_dates():
    """Attachment revisions and substantive deadline revisions change hashes."""
    attachment_v1 = regulatory_monitor._extract_finra_substantive_content(
        BeautifulSoup(
            _finra_canonicalization_fixture(
                attachment_href="/sites/default/files/attachment-v1.pdf"
            ),
            "html.parser",
        ),
        "https://www.finra.org/rules-guidance/notices/26-14",
    )
    attachment_v2 = regulatory_monitor._extract_finra_substantive_content(
        BeautifulSoup(
            _finra_canonicalization_fixture(
                attachment_href="/sites/default/files/attachment-v2.pdf"
            ),
            "html.parser",
        )
    )
    deadline_v1 = regulatory_monitor._extract_finra_substantive_content(
        BeautifulSoup(
            _finra_canonicalization_fixture(deadline="09/11/2026"),
            "html.parser",
        )
    )
    deadline_v2 = regulatory_monitor._extract_finra_substantive_content(
        BeautifulSoup(
            _finra_canonicalization_fixture(deadline="09/25/2026"),
            "html.parser",
        )
    )

    assert "attachment-v1.pdf" in attachment_v1
    assert "notices/26-14#_ednref1" in attachment_v1
    assert "2026-09-11" in deadline_v1
    assert regulatory_monitor.compute_hash(attachment_v1) != (
        regulatory_monitor.compute_hash(attachment_v2)
    )
    assert regulatory_monitor.compute_hash(deadline_v1) != (
        regulatory_monitor.compute_hash(deadline_v2)
    )


def test_finra_canonicalization_ignores_formatting_and_tracking_noise():
    """Markup-only and tracking-query changes must not create provenance churn."""
    plain = regulatory_monitor._extract_finra_substantive_content(
        BeautifulSoup(
            _finra_canonicalization_fixture(
                attachment_href="/sites/default/files/attachment-v1.pdf"
            ),
            "html.parser",
        )
    )
    formatted = regulatory_monitor._extract_finra_substantive_content(
        BeautifulSoup(
            _finra_canonicalization_fixture(
                attachment_href="/sites/default/files/attachment-v1.pdf",
                formatted=True,
            ),
            "html.parser",
        )
    )

    assert regulatory_monitor.compute_hash(plain) == (
        regulatory_monitor.compute_hash(formatted)
    )


def _cloudflare_email_href(email: str, key: int) -> str:
    """Encode a fixture email using Cloudflare's XOR email-protection format."""
    encoded = bytes(ord(character) ^ key for character in email)
    return (
        "https://www.finra.org/cdn-cgi/l/email-protection#"
        f"{key:02x}{encoded.hex()}"
    )


def test_finra_cloudflare_email_tokens_are_canonicalized_before_hashing():
    """Randomized Cloudflare tokens for one email must not churn provenance."""
    token_v1 = _cloudflare_email_href("notices@example.test", 0x12)
    token_v2 = _cloudflare_email_href("notices@example.test", 0xA7)
    different_email = _cloudflare_email_href("changed@example.test", 0x12)

    def content(token):
        return regulatory_monitor._extract_finra_substantive_content(
            BeautifulSoup(
                _finra_canonicalization_fixture(contact_href=token),
                "html.parser",
            ),
            "https://www.finra.org/rules-guidance/notices/26-14",
        )

    content_v1 = content(token_v1)
    content_v2 = content(token_v2)
    content_different = content(different_email)

    assert "mailto:notices@example.test" in content_v1
    assert regulatory_monitor.compute_hash(content_v1) == (
        regulatory_monitor.compute_hash(content_v2)
    )
    assert regulatory_monitor.compute_hash(content_v1) != (
        regulatory_monitor.compute_hash(content_different)
    )


def test_finra_rate_limit_retry_resumes_same_url(monkeypatch):
    """A transient 429 honors Retry-After and retries the exact URL."""
    responses = [
        {"status_code": 429, "content": "", "final_url": "https://example.test/finra",
         "was_redirected": False, "error": "rate limited", "retry_after": 60},
        {"status_code": 200, "content": "ok", "final_url": "https://example.test/finra",
         "was_redirected": False, "error": None},
    ]
    sleeps = []
    calls = []

    def fake_fetch_page(url, _session, **kwargs):
        calls.append(url)
        calls.append(kwargs)
        return responses.pop(0)

    monkeypatch.setattr(regulatory_monitor, "fetch_page", fake_fetch_page)
    monkeypatch.setattr(regulatory_monitor.time, "sleep", sleeps.append)
    monkeypatch.setattr(regulatory_monitor.time, "monotonic", lambda: 0.0)

    result = regulatory_monitor._fetch_finra_page("https://example.test/finra", _FakeSession([]))

    assert result["status_code"] == 200
    assert responses == []
    assert 1 in sleeps
    assert 60 in sleeps
    assert calls[0] == "https://example.test/finra"
    assert calls[1]["max_retries"] == 1
    assert calls[2] == "https://example.test/finra"
    assert calls[3]["max_retries"] == 1


def test_finra_rate_limit_preserves_listing_page_url(monkeypatch):
    """A 429 on page 1 must retry page 1, never page 0 or a slash variant."""
    responses = [
        {
            "status_code": 429,
            "content": "",
            "final_url": "https://example.test/finra?page=1",
            "was_redirected": False,
            "error": "rate limited",
            "retry_after": 0,
        },
        {
            "status_code": 200,
            "content": "notice",
            "final_url": "https://example.test/finra?page=1",
            "was_redirected": False,
            "error": None,
        },
    ]
    requested = []

    def fake_fetch_page(url, _session, **_kwargs):
        requested.append(url)
        return responses.pop(0)

    monkeypatch.setattr(regulatory_monitor, "fetch_page", fake_fetch_page)
    monkeypatch.setattr(regulatory_monitor.time, "sleep", lambda _seconds: None)
    monkeypatch.setattr(regulatory_monitor.time, "monotonic", lambda: 0.0)

    result = regulatory_monitor._fetch_finra_page(
        "https://example.test/finra?page=1", _FakeSession([])
    )

    assert result["status_code"] == 200
    assert requested == [
        "https://example.test/finra?page=1",
        "https://example.test/finra?page=1",
    ]


def test_finra_rate_limit_uses_persisted_authoritative_node_fallback(monkeypatch):
    """A learned FINRA node shortlink can recover a canonical-page 429."""
    canonical = "https://www.finra.org/rules-guidance/notices/26-14"
    node_url = "https://www.finra.org/node/382806"
    listing = _finra_listing_page(
        0, 1, [("/rules-guidance/notices/26-14", "Regulatory Notice 26-14", "2026-07-09")]
    )
    detail = _finra_detail_page("Regulatory Notice 26-14", "2026-07-09", "Stable content.")
    requested = []

    def fake_fetch_page(url, _session, **_kwargs):
        requested.append(url)
        base_url = _finra_request_base(url)
        if base_url == regulatory_monitor.FINRA_NOTICES_URL:
            content = listing
            status = 200
        elif base_url == node_url:
            content = detail
            status = 200
        else:
            content = ""
            status = 429
        return {
            "status_code": status,
            "content": content,
            "final_url": url,
            "was_redirected": False,
            "error": "rate limited" if status == 429 else None,
            "retry_after": 0,
        }

    monkeypatch.setattr(regulatory_monitor, "fetch_page", fake_fetch_page)
    monkeypatch.setattr(regulatory_monitor.time, "sleep", lambda _seconds: None)
    result = regulatory_monitor.fetch_finra_notices(
        _FakeSession([]),
        {"regulatory": {}, "keyword_control_map": []},
        fallback_urls={canonical: node_url},
    )

    assert result.complete is True
    assert result[0].url == canonical
    assert node_url in requested
    assert requested.count(canonical) == 1
    assert result.fallback_urls[canonical] == node_url
    state = {"sources": {regulatory_monitor.SOURCE_KEY_FINRA: {"entries": {}}}}
    regulatory_monitor.update_source_state(
        regulatory_monitor.SOURCE_KEY_FINRA,
        list(result),
        state,
        fallback_urls=result.fallback_urls,
    )
    assert state["sources"][regulatory_monitor.SOURCE_KEY_FINRA]["fallback_urls"] == {
        canonical: node_url
    }


def test_finra_rate_limit_cooldown_is_shared_across_urls(monkeypatch):
    """A 429 cooldown applies to the next FINRA request, not just one URL."""
    clock = [0.0]
    sleeps = []
    responses = {
        "https://example.test/first": [
            {
                "status_code": 429,
                "content": "",
                "final_url": "https://example.test/first",
                "was_redirected": False,
                "error": "rate limited",
                "retry_after": 10,
            },
            {
                "status_code": 200,
                "content": "first",
                "final_url": "https://example.test/first",
                "was_redirected": False,
                "error": None,
            },
        ],
        "https://example.test/second": [
            {
                "status_code": 200,
                "content": "second",
                "final_url": "https://example.test/second",
                "was_redirected": False,
                "error": None,
            },
        ],
    }

    def fake_sleep(seconds):
        sleeps.append(seconds)
        clock[0] += seconds

    def fake_fetch_page(url, _session, **_kwargs):
        key = url.split("?", 1)[0].rstrip("/")
        return responses[key].pop(0)

    monkeypatch.setattr(regulatory_monitor, "fetch_page", fake_fetch_page)
    monkeypatch.setattr(regulatory_monitor.time, "sleep", fake_sleep)
    monkeypatch.setattr(regulatory_monitor.time, "monotonic", lambda: clock[0])
    session = _FakeSession([])

    assert regulatory_monitor._fetch_finra_page(
        "https://example.test/first", session
    )["status_code"] == 200
    assert regulatory_monitor._fetch_finra_page(
        "https://example.test/second", session
    )["status_code"] == 200
    assert 10 in sleeps
    assert sleeps.count(10) == 1


def test_main_does_not_advance_finra_on_detail_failure(monkeypatch):
    """A failed refresh leaves the entire persisted state untouched."""
    state = {
        "version": 1,
        "sources": {
            regulatory_monitor.SOURCE_KEY_FINRA: {
                "last_run": "2026-08-08T00:00:00+00:00",
                "entries": {"FINRA 26-14": "sha256:old"},
            }
        },
    }
    original_state = repr(state)
    incomplete = regulatory_monitor.FetchResult(
        [], complete=False, error="FINRA notice detail page returned status 429"
    )
    save_calls = []
    monkeypatch.setattr(regulatory_monitor, "load_state", lambda *a, **k: state)
    monkeypatch.setattr(regulatory_monitor, "save_state_atomic", lambda *a, **k: save_calls.append(a))
    monkeypatch.setattr(regulatory_monitor, "fetch_finra_notices", lambda *a, **k: incomplete)
    monkeypatch.setattr(sys, "argv", ["regulatory_monitor.py", "--source", "finra"])

    with pytest.raises(SystemExit) as exc:
        regulatory_monitor.main()

    assert exc.value.code == 2
    assert save_calls == []
    assert repr(state) == original_state
