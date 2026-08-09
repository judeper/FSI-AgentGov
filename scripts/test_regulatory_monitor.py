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
from copy import deepcopy
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

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


class _FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


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


def test_finra_paginates_to_cutoff_and_refetches_overlap_window(monkeypatch):
    """A 92-page-style listing scans the safe window and details every record in it."""
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
    }
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
    }
    requested = []

    def fake_fetch_page(url, _session, **_kwargs):
        requested.append(url)
        if url == regulatory_monitor.FINRA_NOTICES_URL:
            page = 0
        elif "?page=" in url:
            page = int(url.rsplit("=", 1)[1])
        else:
            path = url.removeprefix("https://www.finra.org")
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
    assert result.pages_fetched == 3
    ids = {item.document_id for item in result}
    assert ids == {
        "FINRA 26-15",
        "FINRA 26-14",
        "FINRA 26-13",
        "https://www.finra.org/rules-guidance/notices/information-notice-20260808",
    }
    assert "https://www.finra.org/rules-guidance/notices?page=2" in requested
    assert "https://www.finra.org/rules-guidance/notices?page=3" not in requested
    edited = next(item for item in result if item.document_id == "FINRA 26-15")
    assert "Edited summary" in edited.abstract


def test_finra_pagination_overlap_fails_closed(monkeypatch):
    """A notice repeated across listing pages is an unverifiable pagination overlap."""
    record = ("/rules-guidance/notices/26-15", "Regulatory Notice 26-15", "2026-07-24")
    pages = {
        regulatory_monitor.FINRA_NOTICES_URL: _finra_listing_page(0, 2, [record]),
        "https://www.finra.org/rules-guidance/notices?page=1": _finra_listing_page(1, 2, [record]),
    }

    def fake_fetch_page(url, _session, **_kwargs):
        return {
            "status_code": 200,
            "content": pages[url],
            "final_url": url,
            "was_redirected": False,
            "error": None,
        }

    monkeypatch.setattr(regulatory_monitor, "fetch_page", fake_fetch_page)
    result = regulatory_monitor.fetch_finra_notices(
        _FakeSession([]), {"regulatory": {}, "keyword_control_map": []}
    )

    assert result.complete is False
    assert "overlap" in result.error


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
        return {
            "status_code": 200,
            "content": pages[url],
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
        content = listing_html if url == regulatory_monitor.FINRA_NOTICES_URL else detail_html
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
    """The continue-on-error monitor step must still fail the job for exit >= 2."""
    workflow = (
        Path(__file__).resolve().parents[1]
        / ".github"
        / "workflows"
        / "regulatory-monitoring.yml"
    ).read_text(encoding="utf-8")

    assert 'if [ "$EXIT_CODE" -ge 2 ]; then' in workflow
    assert 'exit "$EXIT_CODE"' in workflow
    assert "Fail on regulatory monitor error" in workflow
    assert "steps.monitor.outputs.exit_code != '1'" in workflow


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
        if url == regulatory_monitor.FINRA_NOTICES_URL:
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
        return {"status_code": 200, "content": listing if url == regulatory_monitor.FINRA_NOTICES_URL
                else details[url], "final_url": url, "was_redirected": False, "error": None}

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
                "content": pages[url],
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
    """A transient 429 is paced and retried rather than skipping the notice."""
    responses = [
        {"status_code": 429, "content": "", "final_url": "https://example.test/finra",
         "was_redirected": False, "error": "rate limited", "retry_after": 10},
        {"status_code": 200, "content": "ok", "final_url": "https://example.test/finra",
         "was_redirected": False, "error": None},
    ]
    sleeps = []
    calls = []

    def fake_fetch_page(_url, _session, **kwargs):
        calls.append(kwargs)
        return responses.pop(0)

    monkeypatch.setattr(regulatory_monitor, "fetch_page", fake_fetch_page)
    monkeypatch.setattr(regulatory_monitor.time, "sleep", sleeps.append)
    monkeypatch.setattr(regulatory_monitor.time, "monotonic", lambda: 0.0)

    result = regulatory_monitor._fetch_finra_page("https://example.test/finra", _FakeSession([]))

    assert result["status_code"] == 200
    assert responses == []
    assert 1 in sleeps
    assert 10 in sleeps
    assert all(call["max_retries"] == 1 for call in calls)


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
        return responses[url].pop(0)

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
