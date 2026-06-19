"""Tests for advancing deferred Learn Monitor pending baselines."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

import autodoc_advance as advance
import autodoc_defer as defer
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent


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


def _write_state(path: Path, terminal_url: str, non_terminal_url: str) -> None:
    path.parent.mkdir(parents=True)
    path.write_text(
        json.dumps(
            {
                "version": 1,
                "sources": {
                    "learn": {
                        "schema_version": 2,
                        "last_run": "2026-06-18T00:00:00+00:00",
                        "urls": {
                            terminal_url: {
                                "content_hash": "sha256:old-terminal",
                                "normalized_content": "old terminal",
                                "last_checked": "2026-06-18T00:00:00+00:00",
                                "last_status": 200,
                                "last_changed": "2026-06-17T00:00:00+00:00",
                                "topic": "Terminal",
                                "section": "Learn",
                            },
                            non_terminal_url: {
                                "content_hash": "sha256:old-non-terminal",
                                "normalized_content": "old non terminal",
                                "last_checked": "2026-06-18T00:00:00+00:00",
                                "last_status": 200,
                                "last_changed": "2026-06-17T00:00:00+00:00",
                                "topic": "Non-terminal",
                                "section": "Learn",
                            },
                        },
                        "statistics": {},
                    }
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def test_advance_source_state_only_applies_terminal_urls() -> None:
    terminal_url = "https://learn.microsoft.com/en-us/terminal"
    non_terminal_url = "https://learn.microsoft.com/en-us/non-terminal"
    source_state = {
        "urls": {
            terminal_url: {"content_hash": "sha256:old", "normalized_content": "old", "last_changed": "old-date"},
            non_terminal_url: {
                "content_hash": "sha256:old2",
                "normalized_content": "old2",
                "last_changed": "old-date2",
            },
        }
    }
    pending_records = [
        {
            "url": terminal_url,
            "content_hash": "sha256:new",
            "normalized_content": "new body",
            "detected_at": "2026-06-19T00:00:00+00:00",
        },
        {
            "url": non_terminal_url,
            "content_hash": "sha256:new2",
            "normalized_content": "new body2",
            "detected_at": "2026-06-19T00:00:00+00:00",
        },
    ]

    updated, advanced_urls, missing_urls = advance.advance_source_state(source_state, pending_records, {terminal_url})

    assert advanced_urls == [terminal_url]
    assert missing_urls == []
    assert updated["urls"][terminal_url]["content_hash"] == "sha256:new"
    assert updated["urls"][terminal_url]["normalized_content"] == "new body"
    assert updated["urls"][terminal_url]["last_changed"] == "2026-06-19T00:00:00+00:00"
    assert updated["urls"][non_terminal_url] == source_state["urls"][non_terminal_url]
    assert source_state["urls"][terminal_url]["content_hash"] == "sha256:old"


def test_advance_pending_baselines_removes_only_terminal_pending_blob(workspace: Path) -> None:
    terminal_url = "https://learn.microsoft.com/en-us/terminal"
    non_terminal_url = "https://learn.microsoft.com/en-us/non-terminal"
    state_path = workspace / "data" / "monitor-state.json"
    pending_dir = workspace / "data" / "monitor-pending" / "learn"
    _write_state(state_path, terminal_url, non_terminal_url)

    terminal_pending = defer.pending_path(terminal_url, workspace)
    non_terminal_pending = defer.pending_path(non_terminal_url, workspace)
    defer.write_pending(
        terminal_pending,
        terminal_url,
        "sha256:new-terminal",
        "new terminal",
        "2026-06-19T00:00:00+00:00",
    )
    defer.write_pending(
        non_terminal_pending,
        non_terminal_url,
        "sha256:new-non-terminal",
        "new non terminal",
        "2026-06-19T01:00:00+00:00",
    )

    result = advance.advance_pending_baselines(state_path, pending_dir, {terminal_url})

    state = json.loads(state_path.read_text(encoding="utf-8"))
    terminal_state = state["sources"]["learn"]["urls"][terminal_url]
    non_terminal_state = state["sources"]["learn"]["urls"][non_terminal_url]
    assert result == {"advanced": [terminal_url], "missing": [], "non_terminal": [non_terminal_url]}
    assert terminal_state["content_hash"] == "sha256:new-terminal"
    assert terminal_state["normalized_content"] == "new terminal"
    assert terminal_state["last_changed"] == "2026-06-19T00:00:00+00:00"
    assert non_terminal_state["content_hash"] == "sha256:old-non-terminal"
    assert terminal_pending.exists() is False
    assert non_terminal_pending.exists() is True


def test_advance_pending_baselines_leaves_non_terminal_pending_intact(workspace: Path) -> None:
    terminal_url = "https://learn.microsoft.com/en-us/terminal"
    non_terminal_url = "https://learn.microsoft.com/en-us/non-terminal"
    state_path = workspace / "data" / "monitor-state.json"
    pending_dir = workspace / "data" / "monitor-pending" / "learn"
    _write_state(state_path, terminal_url, non_terminal_url)

    non_terminal_pending = defer.pending_path(non_terminal_url, workspace)
    defer.write_pending(
        non_terminal_pending,
        non_terminal_url,
        "sha256:new-non-terminal",
        "new non terminal",
        "2026-06-19T01:00:00+00:00",
    )

    result = advance.advance_pending_baselines(state_path, pending_dir, set())

    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert result == {"advanced": [], "missing": [], "non_terminal": [non_terminal_url]}
    assert state["sources"]["learn"]["urls"][non_terminal_url]["content_hash"] == "sha256:old-non-terminal"
    assert non_terminal_pending.exists() is True


def test_advance_pending_baselines_removes_terminal_missing_state_blob(workspace: Path) -> None:
    terminal_url = "https://learn.microsoft.com/en-us/terminal"
    non_terminal_url = "https://learn.microsoft.com/en-us/non-terminal"
    missing_url = "https://learn.microsoft.com/en-us/removed-from-state"
    state_path = workspace / "data" / "monitor-state.json"
    pending_dir = workspace / "data" / "monitor-pending" / "learn"
    _write_state(state_path, terminal_url, non_terminal_url)

    missing_pending = defer.pending_path(missing_url, workspace)
    defer.write_pending(
        missing_pending,
        missing_url,
        "sha256:new-missing",
        "new missing",
        "2026-06-19T02:00:00+00:00",
    )

    result = advance.advance_pending_baselines(state_path, pending_dir, {missing_url})

    assert result == {"advanced": [], "missing": [missing_url], "non_terminal": []}
    assert missing_pending.exists() is False


def test_read_terminal_urls_ignores_blank_lines(workspace: Path) -> None:
    terminal_path = workspace / "terminal-urls.txt"
    terminal_path.write_text("\nhttps://learn.microsoft.com/a\n\n https://learn.microsoft.com/b \n", encoding="utf-8")

    assert advance.read_terminal_urls(terminal_path) == {
        "https://learn.microsoft.com/a",
        "https://learn.microsoft.com/b",
    }
