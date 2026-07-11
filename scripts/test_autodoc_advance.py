"""Tests for advancing deferred Learn Monitor pending baselines.

The advance step is the last line of defense against silent data loss: it both rewrites
``data/monitor-state.json`` baselines and ``unlink()``-s pending blobs. These tests pin the
exact-identity matching that prevents the tribunal-confirmed defects:

* (A-CRITICAL) a tokenized ``{url} in:body`` search subsetting an UNRELATED closed issue and
  advancing/deleting the wrong blob;
* (A-HIGH) a "not planned"/"duplicate" close advancing a baseline whose doc edit never shipped;
* (A-HIGH) two changes to one URL collapsing onto one blob and orphaning the other issue.
"""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

import autodoc_advance as advance
import autodoc_defer as defer
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent

TERMINAL_URL = "https://learn.microsoft.com/en-us/terminal"
NON_TERMINAL_URL = "https://learn.microsoft.com/en-us/non-terminal"


@pytest.fixture()
def workspace(request: pytest.FixtureRequest) -> Path:
    name = re.sub(r"[^A-Za-z0-9_.-]+", "-", request.node.name).strip("-")
    path = PROJECT_ROOT / ".pytest-f5-workspaces" / "autodoc-advance" / name
    shutil.rmtree(path, ignore_errors=True)
    path.mkdir(parents=True)
    yield path
    shutil.rmtree(path, ignore_errors=True)
    for parent in (path.parent, PROJECT_ROOT / ".pytest-f5-workspaces"):
        try:
            parent.rmdir()
        except OSError:
            pass


def _state_url_entry(content_hash: str, normalized: str) -> dict:
    return {
        "content_hash": content_hash,
        "normalized_content": normalized,
        "last_checked": "2026-06-18T00:00:00+00:00",
        "last_status": 200,
        "last_changed": "2026-06-17T00:00:00+00:00",
        "topic": "Topic",
        "section": "Learn",
    }


def _write_state(path: Path, urls: dict[str, dict]) -> None:
    path.parent.mkdir(parents=True)
    path.write_text(
        json.dumps(
            {
                "version": 1,
                "sources": {
                    "learn": {
                        "schema_version": 2,
                        "last_run": "2026-06-18T00:00:00+00:00",
                        "urls": urls,
                        "statistics": {},
                    }
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def _issue_body(url: str, content_hash: str) -> str:
    return (
        "Autodoc escalation — human review required.\n\n"
        "AUTODOC-FINGERPRINT: sha256:deadbeef\n"
        "Reason: route=human\n"
        f"Source: {url}\n"
        f"Content-Hash: {content_hash}\n"
        "\nThis change must be analyzed by a human.\n"
    )


# ---------------------------------------------------------------------------
# Identity parsing (the core of the exact-match fix)
# ---------------------------------------------------------------------------
def test_parse_issue_identity_requires_both_lines() -> None:
    assert advance.parse_issue_identity(_issue_body(TERMINAL_URL, "sha256:h")) == (TERMINAL_URL, "sha256:h")
    assert advance.parse_issue_identity(f"Source: {TERMINAL_URL}\n") is None  # missing Content-Hash
    assert advance.parse_issue_identity("Content-Hash: sha256:h\n") is None  # missing Source
    assert advance.parse_issue_identity(None) is None


def test_terminal_identities_from_issues_filters_state_reason() -> None:
    closed_issues = [
        {"number": 1, "stateReason": "COMPLETED", "body": _issue_body(TERMINAL_URL, "sha256:done")},
        {"number": 2, "stateReason": "NOT_PLANNED", "body": _issue_body(NON_TERMINAL_URL, "sha256:dropped")},
        {"number": 3, "stateReason": None, "body": _issue_body(NON_TERMINAL_URL, "sha256:null")},
    ]
    assert advance.terminal_identities_from_issues(closed_issues) == {(TERMINAL_URL, "sha256:done")}


def test_terminal_identities_from_issues_accepts_lowercase_completed() -> None:
    closed_issues = [{"number": 1, "stateReason": "completed", "body": _issue_body(TERMINAL_URL, "sha256:done")}]
    assert advance.terminal_identities_from_issues(closed_issues) == {(TERMINAL_URL, "sha256:done")}


def _tracking_issue_body(url: str, content_hash: str) -> str:
    """Mirror route.build_issue: identity lives ONLY in the embedded ```json``` contract."""
    contract = {
        "schema_version": 1,
        "fingerprint": "sha256:deadbeef",
        "source_url": url,
        "content_hash": content_hash,
        "classification": "TECHNICAL",
    }
    return (
        "Autodoc tracking issue.\n\n"
        "AUTODOC-FINGERPRINT: sha256:deadbeef\n"
        "AUTODOC-AUTOMERGE-ELIGIBLE: false\n\n"
        "```json\n" + json.dumps(contract, indent=2, sort_keys=True) + "\n```\n"
    )


def test_parse_issue_identity_from_json_contract() -> None:
    # Autodraft tracking issues (the common path) carry identity ONLY in the JSON contract, with
    # no plaintext Source:/Content-Hash: lines. The parser must still recover the exact identity,
    # else autodrafted changes' baselines never advance and their blobs accumulate forever.
    body = _tracking_issue_body(TERMINAL_URL, "sha256:tracked")
    assert "Source:" not in body
    assert advance.parse_issue_identity(body) == (TERMINAL_URL, "sha256:tracked")


def test_parse_issue_identity_json_contract_requires_both_fields() -> None:
    no_hash = '```json\n{"source_url": "' + TERMINAL_URL + '"}\n```\n'
    assert advance.parse_issue_identity(no_hash) is None
    no_url = '```json\n{"content_hash": "sha256:h"}\n```\n'
    assert advance.parse_issue_identity(no_url) is None


def test_parse_issue_identity_prefers_complete_plaintext_pair_over_contract() -> None:
    body = (
        f"Source: {TERMINAL_URL}\n"
        "Content-Hash: sha256:plain\n"
        + '```json\n{"source_url": "https://learn.microsoft.com/en-us/contract", "content_hash": "sha256:contract"}\n```\n'
    )
    assert advance.parse_issue_identity(body) == (TERMINAL_URL, "sha256:plain")


def test_parse_issue_identity_uses_complete_contract_when_plaintext_is_partial() -> None:
    body = (
        f"Source: {TERMINAL_URL}\n"
        + '```json\n{"source_url": "https://learn.microsoft.com/en-us/contract", "content_hash": "sha256:contract"}\n```\n'
    )
    assert advance.parse_issue_identity(body) == ("https://learn.microsoft.com/en-us/contract", "sha256:contract")


def test_parse_issue_identity_rejects_mixed_partial_pairs() -> None:
    source_plus_contract_hash_only = (
        f"Source: {TERMINAL_URL}\n" + '```json\n{"content_hash": "sha256:contract"}\n```\n'
    )
    hash_plus_contract_source_only = (
        "Content-Hash: sha256:line\n"
        + '```json\n{"source_url": "https://learn.microsoft.com/en-us/contract"}\n```\n'
    )
    assert advance.parse_issue_identity(source_plus_contract_hash_only) is None
    assert advance.parse_issue_identity(hash_plus_contract_source_only) is None


# ---------------------------------------------------------------------------
# advance_source_state — identity matching
# ---------------------------------------------------------------------------
def test_advance_source_state_only_applies_terminal_identities() -> None:
    source_state = {
        "urls": {
            TERMINAL_URL: {"content_hash": "sha256:old", "normalized_content": "old", "last_changed": "old-date"},
            NON_TERMINAL_URL: {
                "content_hash": "sha256:old2",
                "normalized_content": "old2",
                "last_changed": "old-date2",
            },
        }
    }
    pending_records = [
        {
            "url": TERMINAL_URL,
            "content_hash": "sha256:new",
            "normalized_content": "new body",
            "detected_at": "2026-06-19T00:00:00+00:00",
        },
        {
            "url": NON_TERMINAL_URL,
            "content_hash": "sha256:new2",
            "normalized_content": "new body2",
            "detected_at": "2026-06-19T00:00:00+00:00",
        },
    ]

    updated, advanced_urls, missing_urls = advance.advance_source_state(
        source_state, pending_records, {(TERMINAL_URL, "sha256:new")}
    )

    assert advanced_urls == [TERMINAL_URL]
    assert missing_urls == []
    assert updated["urls"][TERMINAL_URL]["content_hash"] == "sha256:new"
    assert updated["urls"][TERMINAL_URL]["normalized_content"] == "new body"
    assert updated["urls"][TERMINAL_URL]["last_changed"] == "2026-06-19T00:00:00+00:00"
    assert updated["urls"][NON_TERMINAL_URL] == source_state["urls"][NON_TERMINAL_URL]
    assert source_state["urls"][TERMINAL_URL]["content_hash"] == "sha256:old"


def test_advance_applies_newest_change_by_detected_at() -> None:
    # Two terminal changes to the SAME url advancing in one run: the NEWEST (by detected_at) must
    # win the baseline. Pass them newest-first in the list to prove ordering is by detected_at,
    # not list/path order (without the sort, the older change would land last and win).
    source_state = {
        "urls": {TERMINAL_URL: {"content_hash": "sha256:old", "normalized_content": "old", "last_changed": "old"}}
    }
    older = {
        "url": TERMINAL_URL,
        "content_hash": "sha256:h1",
        "normalized_content": "older body",
        "detected_at": "2026-06-18T00:00:00+00:00",
    }
    newer = {
        "url": TERMINAL_URL,
        "content_hash": "sha256:h2",
        "normalized_content": "newer body",
        "detected_at": "2026-06-20T00:00:00+00:00",
    }
    updated, advanced_urls, _missing = advance.advance_source_state(
        source_state, [newer, older], {(TERMINAL_URL, "sha256:h1"), (TERMINAL_URL, "sha256:h2")}
    )

    assert updated["urls"][TERMINAL_URL]["content_hash"] == "sha256:h2"
    assert updated["urls"][TERMINAL_URL]["normalized_content"] == "newer body"
    assert updated["urls"][TERMINAL_URL]["last_changed"] == "2026-06-20T00:00:00+00:00"


def test_advance_pending_baselines_removes_only_terminal_pending_blob(workspace: Path) -> None:
    state_path = workspace / "data" / "monitor-state.json"
    pending_dir = workspace / "data" / "monitor-pending" / "learn"
    _write_state(
        state_path,
        {
            TERMINAL_URL: _state_url_entry("sha256:old-terminal", "old terminal"),
            NON_TERMINAL_URL: _state_url_entry("sha256:old-non-terminal", "old non terminal"),
        },
    )

    terminal_pending = defer.pending_path(TERMINAL_URL, "sha256:new-terminal", workspace)
    non_terminal_pending = defer.pending_path(NON_TERMINAL_URL, "sha256:new-non-terminal", workspace)
    defer.write_pending(terminal_pending, TERMINAL_URL, "sha256:new-terminal", "new terminal", "2026-06-19T00:00:00+00:00")
    defer.write_pending(
        non_terminal_pending, NON_TERMINAL_URL, "sha256:new-non-terminal", "new non terminal", "2026-06-19T01:00:00+00:00"
    )

    result = advance.advance_pending_baselines(state_path, pending_dir, {(TERMINAL_URL, "sha256:new-terminal")})

    state = json.loads(state_path.read_text(encoding="utf-8"))
    terminal_state = state["sources"]["learn"]["urls"][TERMINAL_URL]
    non_terminal_state = state["sources"]["learn"]["urls"][NON_TERMINAL_URL]
    assert result == {"advanced": [TERMINAL_URL], "missing": [], "non_terminal": [NON_TERMINAL_URL]}
    assert terminal_state["content_hash"] == "sha256:new-terminal"
    assert terminal_state["normalized_content"] == "new terminal"
    assert terminal_state["last_changed"] == "2026-06-19T00:00:00+00:00"
    assert non_terminal_state["content_hash"] == "sha256:old-non-terminal"
    assert terminal_pending.exists() is False
    assert non_terminal_pending.exists() is True


def test_advance_pending_baselines_leaves_non_terminal_pending_intact(workspace: Path) -> None:
    state_path = workspace / "data" / "monitor-state.json"
    pending_dir = workspace / "data" / "monitor-pending" / "learn"
    _write_state(
        state_path,
        {
            TERMINAL_URL: _state_url_entry("sha256:old-terminal", "old terminal"),
            NON_TERMINAL_URL: _state_url_entry("sha256:old-non-terminal", "old non terminal"),
        },
    )

    non_terminal_pending = defer.pending_path(NON_TERMINAL_URL, "sha256:new-non-terminal", workspace)
    defer.write_pending(
        non_terminal_pending, NON_TERMINAL_URL, "sha256:new-non-terminal", "new non terminal", "2026-06-19T01:00:00+00:00"
    )

    result = advance.advance_pending_baselines(state_path, pending_dir, set())

    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert result == {"advanced": [], "missing": [], "non_terminal": [NON_TERMINAL_URL]}
    assert state["sources"]["learn"]["urls"][NON_TERMINAL_URL]["content_hash"] == "sha256:old-non-terminal"
    assert non_terminal_pending.exists() is True


def test_advance_pending_baselines_removes_terminal_missing_state_blob(workspace: Path) -> None:
    missing_url = "https://learn.microsoft.com/en-us/removed-from-state"
    state_path = workspace / "data" / "monitor-state.json"
    pending_dir = workspace / "data" / "monitor-pending" / "learn"
    _write_state(state_path, {TERMINAL_URL: _state_url_entry("sha256:old-terminal", "old terminal")})

    missing_pending = defer.pending_path(missing_url, "sha256:new-missing", workspace)
    defer.write_pending(missing_pending, missing_url, "sha256:new-missing", "new missing", "2026-06-19T02:00:00+00:00")

    result = advance.advance_pending_baselines(state_path, pending_dir, {(missing_url, "sha256:new-missing")})

    assert result == {"advanced": [], "missing": [missing_url], "non_terminal": []}
    assert missing_pending.exists() is False


# ---------------------------------------------------------------------------
# Regression tests for the three tribunal-confirmed defects
# ---------------------------------------------------------------------------
def test_tokenized_false_positive_does_not_advance_or_delete(workspace: Path) -> None:
    """(A-CRITICAL) An unrelated closed issue whose body merely token-contains X's URL must NOT
    make X terminal. Exact ``(Source, Content-Hash)`` matching ignores it; X's still-open change
    is preserved.
    """
    url_x = "https://learn.microsoft.com/x"  # short URL whose tokens subset the unrelated body
    state_path = workspace / "data" / "monitor-state.json"
    pending_dir = workspace / "data" / "monitor-pending" / "learn"
    _write_state(state_path, {url_x: _state_url_entry("sha256:old-x", "old x")})

    pending_x = defer.pending_path(url_x, "sha256:new-x", workspace)
    defer.write_pending(pending_x, url_x, "sha256:new-x", "new x", "2026-06-19T00:00:00+00:00")

    # X's own escalation issue is still OPEN, so it is absent from the closed-issue list.
    # An UNRELATED closed issue's prose happens to contain the tokens "learn microsoft com x".
    unrelated_closed = [
        {
            "number": 99,
            "stateReason": "COMPLETED",
            "body": (
                "AUTODOC-FINGERPRINT: sha256:unrelated\n"
                "Reason: route=human\n"
                "Source: https://learn.microsoft.com/x-completely-different-page\n"
                "Content-Hash: sha256:unrelated-hash\n"
                "\nThe learn.microsoft.com/x docs were reorganized in this unrelated work.\n"
            ),
        }
    ]
    terminal_identities = advance.terminal_identities_from_issues(unrelated_closed)
    assert (url_x, "sha256:new-x") not in terminal_identities

    result = advance.advance_pending_baselines(state_path, pending_dir, terminal_identities)

    assert result["advanced"] == []
    assert pending_x.exists() is True  # blob NOT deleted — no silent data loss
    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state["sources"]["learn"]["urls"][url_x]["content_hash"] == "sha256:old-x"


def test_not_planned_close_does_not_advance(workspace: Path) -> None:
    """(A-HIGH) A change whose escalation a human closed as "not planned"/"duplicate" must NOT
    advance its baseline — otherwise the change is deduped though no doc edit ever shipped.
    """
    url_y = "https://learn.microsoft.com/en-us/y"
    state_path = workspace / "data" / "monitor-state.json"
    pending_dir = workspace / "data" / "monitor-pending" / "learn"
    _write_state(state_path, {url_y: _state_url_entry("sha256:old-y", "old y")})

    pending_y = defer.pending_path(url_y, "sha256:new-y", workspace)
    defer.write_pending(pending_y, url_y, "sha256:new-y", "new y", "2026-06-19T00:00:00+00:00")

    closed_not_planned = [{"number": 7, "stateReason": "NOT_PLANNED", "body": _issue_body(url_y, "sha256:new-y")}]
    terminal_identities = advance.terminal_identities_from_issues(closed_not_planned)
    assert terminal_identities == set()

    result = advance.advance_pending_baselines(state_path, pending_dir, terminal_identities)

    assert result["advanced"] == []
    assert pending_y.exists() is True
    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state["sources"]["learn"]["urls"][url_y]["content_hash"] == "sha256:old-y"


def test_multi_change_per_url_advances_only_its_own_blob(workspace: Path) -> None:
    """(A-HIGH) Two changes to one URL produce two blobs. Closing the first change's issue must
    advance/delete ONLY that change's blob, leaving the second change's blob (and open issue)
    intact instead of orphaning it.
    """
    url_z = "https://learn.microsoft.com/en-us/z"
    state_path = workspace / "data" / "monitor-state.json"
    pending_dir = workspace / "data" / "monitor-pending" / "learn"
    _write_state(state_path, {url_z: _state_url_entry("sha256:old-z", "old z")})

    blob_1 = defer.pending_path(url_z, "sha256:z1", workspace)
    blob_2 = defer.pending_path(url_z, "sha256:z2", workspace)
    assert blob_1 != blob_2  # distinct identities -> distinct blobs
    defer.write_pending(blob_1, url_z, "sha256:z1", "z change one", "2026-06-19T00:00:00+00:00")
    defer.write_pending(blob_2, url_z, "sha256:z2", "z change two", "2026-06-20T00:00:00+00:00")

    # Only issue-1 (change z1) is closed as COMPLETED; issue-2 (z2) is still open.
    closed = [{"number": 11, "stateReason": "COMPLETED", "body": _issue_body(url_z, "sha256:z1")}]
    terminal_identities = advance.terminal_identities_from_issues(closed)

    result = advance.advance_pending_baselines(state_path, pending_dir, terminal_identities)

    assert result["advanced"] == [url_z]
    assert blob_1.exists() is False  # change-1 blob consumed
    assert blob_2.exists() is True  # change-2 blob preserved (issue still open)
    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state["sources"]["learn"]["urls"][url_z]["content_hash"] == "sha256:z1"
    assert state["sources"]["learn"]["urls"][url_z]["normalized_content"] == "z change one"


def test_happy_path_completed_close_advances_and_cleans(workspace: Path) -> None:
    """A COMPLETED close whose body exactly names the pending change advances + cleans its blob."""
    url = "https://learn.microsoft.com/en-us/power-platform/admin/example"
    state_path = workspace / "data" / "monitor-state.json"
    pending_dir = workspace / "data" / "monitor-pending" / "learn"
    _write_state(state_path, {url: _state_url_entry("sha256:old", "old body")})

    blob = defer.pending_path(url, "sha256:fixed", workspace)
    defer.write_pending(blob, url, "sha256:fixed", "fixed body", "2026-06-19T00:00:00+00:00")

    closed = [{"number": 21, "stateReason": "COMPLETED", "body": _issue_body(url, "sha256:fixed")}]
    terminal_identities = advance.terminal_identities_from_issues(closed)

    result = advance.advance_pending_baselines(state_path, pending_dir, terminal_identities)

    assert result == {"advanced": [url], "missing": [], "non_terminal": []}
    assert blob.exists() is False
    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state["sources"]["learn"]["urls"][url]["content_hash"] == "sha256:fixed"
    assert state["sources"]["learn"]["urls"][url]["normalized_content"] == "fixed body"


# ---------------------------------------------------------------------------
# File-format readers
# ---------------------------------------------------------------------------
def test_read_closed_issues_round_trips(workspace: Path) -> None:
    issues_path = workspace / "closed.json"
    issues = [{"number": 1, "stateReason": "COMPLETED", "body": _issue_body(TERMINAL_URL, "sha256:done")}]
    issues_path.write_text(json.dumps(issues), encoding="utf-8")
    assert advance.read_closed_issues(issues_path) == issues
    assert advance.read_closed_issues(workspace / "missing.json") == []


def test_read_terminal_identities_parses_objects(workspace: Path) -> None:
    identities_path = workspace / "identities.json"
    identities_path.write_text(
        json.dumps(
            [
                {"url": TERMINAL_URL, "content_hash": "sha256:a"},
                {"url": "", "content_hash": "sha256:skip"},  # ignored: blank url
                {"url": NON_TERMINAL_URL},  # ignored: missing content_hash
            ]
        ),
        encoding="utf-8",
    )
    assert advance.read_terminal_identities(identities_path) == {(TERMINAL_URL, "sha256:a")}
