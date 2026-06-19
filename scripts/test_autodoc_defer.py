"""Tests for deferred Learn Monitor baseline advancement helpers."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from types import SimpleNamespace

import autodoc_defer as defer
import learn_monitor
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture()
def workspace(request: pytest.FixtureRequest) -> Path:
    name = re.sub(r"[^A-Za-z0-9_.-]+", "-", request.node.name).strip("-")
    path = PROJECT_ROOT / ".pytest-f5-workspaces" / "autodoc-defer" / name
    shutil.rmtree(path, ignore_errors=True)
    path.mkdir(parents=True)
    yield path
    shutil.rmtree(path, ignore_errors=True)
    for parent in (path.parent, PROJECT_ROOT / ".pytest-f5-workspaces"):
        try:
            parent.rmdir()
        except OSError:
            pass


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("true", True),
        (" TRUE ", True),
        ("TrUe", True),
        ("", False),
        ("false", False),
        ("1", False),
        ("yes", False),
        ("true-ish", False),
    ],
)
def test_defer_enabled_matrix(value: str, expected: bool) -> None:
    assert defer.defer_enabled({"AUTODOC_ENABLED": value}) is expected


def test_defer_enabled_uses_environment_when_env_omitted(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AUTODOC_ENABLED", "true")
    assert defer.defer_enabled() is True
    monkeypatch.setenv("AUTODOC_ENABLED", "false")
    assert defer.defer_enabled() is False


def test_pending_path_uses_safe_deterministic_filename(workspace: Path) -> None:
    url = "https://learn.microsoft.com/en-us/../../Power Platform/Admin?q=1&x=/bad"

    first = defer.pending_path(url, workspace)
    second = defer.pending_path(url, workspace)

    assert first == second
    assert first.parent == workspace / "data" / "monitor-pending" / "learn"
    assert first.suffix == ".json"
    assert re.fullmatch(r"[A-Za-z0-9._-]+\.json", first.name)
    assert ".." not in first.name
    assert "/" not in first.name
    assert "\\" not in first.name


def test_pending_round_trip_and_dedupe(workspace: Path) -> None:
    url = "https://learn.microsoft.com/en-us/power-platform/admin/example"
    pending = defer.pending_path(url, workspace)

    assert defer.load_pending(pending) is None
    assert defer.is_already_pending(url, "sha256:new", workspace) is False

    defer.write_pending(pending, url, "sha256:new", "normalized body", "2026-06-19T00:00:00+00:00")

    loaded = defer.load_pending(pending)
    assert loaded == {
        "schema_version": 1,
        "source": "learn",
        "url": url,
        "content_hash": "sha256:new",
        "normalized_content": "normalized body",
        "detected_at": "2026-06-19T00:00:00+00:00",
    }
    assert defer.is_already_pending(url, "sha256:new", workspace) is True
    assert defer.is_already_pending(url, "sha256:other", workspace) is False
    assert defer.is_already_pending(url + "-other", "sha256:new", workspace) is False


def _write_monitor_fixture(workspace: Path, url: str, old_hash: str) -> tuple[Path, Path]:
    docs_dir = workspace / "docs"
    watchlist_path = docs_dir / "reference" / "microsoft-learn-urls.md"
    state_path = workspace / "data" / "monitor-state.json"
    reports_dir = workspace / "reports" / "monitoring"

    watchlist_path.parent.mkdir(parents=True)
    watchlist_path.write_text(
        "\n".join(
            [
                "# URLs",
                "",
                "## Power Platform Administration",
                "",
                "| Topic | URL |",
                "|-------|-----|",
                f"| Example Topic | {url} |",
                "",
            ]
        ),
        encoding="utf-8",
    )
    state_path.parent.mkdir(parents=True)
    state_path.write_text(
        json.dumps(
            {
                "version": 1,
                "sources": {
                    "learn": {
                        "schema_version": 2,
                        "last_run": "2026-06-18T00:00:00+00:00",
                        "urls": {
                            url: {
                                "content_hash": old_hash,
                                "normalized_content": "old normalized",
                                "last_checked": "2026-06-18T00:00:00+00:00",
                                "last_status": 200,
                                "last_changed": "2026-06-17T00:00:00+00:00",
                                "topic": "Example Topic",
                                "section": "Power Platform Administration",
                            }
                        },
                        "statistics": {},
                    }
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    reports_dir.mkdir(parents=True)
    return watchlist_path, state_path


def _run_changed_monitor(
    monkeypatch: pytest.MonkeyPatch,
    workspace: Path,
    *,
    autodoc_enabled: str | None,
    already_pending: bool = False,
) -> dict:
    url = "https://learn.microsoft.com/en-us/power-platform/admin/example"
    old_hash = learn_monitor.compute_hash("old normalized")
    new_hash = learn_monitor.compute_hash("new normalized")
    watchlist_path, state_path = _write_monitor_fixture(workspace, url, old_hash)

    monkeypatch.setattr(learn_monitor, "PROJECT_ROOT", workspace)
    monkeypatch.setattr(learn_monitor, "DOCS_DIR", workspace / "docs")
    monkeypatch.setattr(learn_monitor, "WATCHLIST_PATH", watchlist_path)
    monkeypatch.setattr(learn_monitor, "STATE_FILE_PATH", state_path)
    monkeypatch.setattr(learn_monitor, "REPORTS_DIR", workspace / "reports" / "monitoring")
    monkeypatch.setattr(learn_monitor.time, "sleep", lambda _seconds: None)
    monkeypatch.setattr(
        learn_monitor,
        "fetch_page",
        lambda url, session: {
            "url": url,
            "status_code": 200,
            "content": "new html",
            "final_url": url,
            "was_redirected": False,
            "error": None,
        },
    )
    monkeypatch.setattr(learn_monitor, "normalize_content", lambda _html: "new normalized")
    monkeypatch.setattr(
        learn_monitor,
        "classify_change",
        lambda old, new, url, config=None: ("MEDIUM", "test change", "--- old\n+++ new\n"),
    )
    monkeypatch.setattr(learn_monitor, "find_affected_controls", lambda url, docs_dir: {"controls": [], "playbooks": []})

    if autodoc_enabled is None:
        monkeypatch.delenv("AUTODOC_ENABLED", raising=False)
    else:
        monkeypatch.setenv("AUTODOC_ENABLED", autodoc_enabled)

    if already_pending:
        defer.write_pending(
            defer.pending_path(url, workspace),
            url,
            new_hash,
            "new normalized",
            "2026-06-18T12:00:00+00:00",
        )

    args = SimpleNamespace(dry_run=False, limit=None, url=None)
    with pytest.raises(SystemExit) as exc_info:
        learn_monitor._run_monitor(args, {"operational": {"request_delay": 0}})
    assert exc_info.value.code == 0

    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["_test_url"] = url
    state["_test_new_hash"] = new_hash
    return state


def test_learn_monitor_disabled_path_still_advances_accepted_state(
    workspace: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    state = _run_changed_monitor(monkeypatch, workspace, autodoc_enabled=None)
    url = state["_test_url"]
    new_hash = state["_test_new_hash"]
    source = state["sources"]["learn"]
    url_state = source["urls"][url]

    assert url_state["content_hash"] == new_hash
    assert url_state["normalized_content"] == "new normalized"
    assert url_state["last_checked"] == source["last_run"]
    assert url_state["last_changed"] == source["last_run"]
    assert url_state["last_status"] == 200
    assert source["statistics"]["last_run_medium_changes"] == 1
    assert not (workspace / "data" / "monitor-pending" / "learn").exists()


def test_learn_monitor_enabled_path_defers_accepted_state(
    workspace: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    state = _run_changed_monitor(monkeypatch, workspace, autodoc_enabled="true")
    url = state["_test_url"]
    new_hash = state["_test_new_hash"]
    source = state["sources"]["learn"]
    url_state = source["urls"][url]
    pending = defer.load_pending(defer.pending_path(url, workspace))

    assert url_state["content_hash"] == learn_monitor.compute_hash("old normalized")
    assert url_state["normalized_content"] == "old normalized"
    assert url_state["last_checked"] == source["last_run"]
    assert url_state["last_changed"] == "2026-06-17T00:00:00+00:00"
    assert source["statistics"]["last_run_medium_changes"] == 1
    assert pending is not None
    assert pending["content_hash"] == new_hash
    assert pending["normalized_content"] == "new normalized"
    assert pending["detected_at"] == source["last_run"]


def test_learn_monitor_enabled_pending_dedupe_does_not_re_report(
    workspace: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    state = _run_changed_monitor(monkeypatch, workspace, autodoc_enabled="true", already_pending=True)
    url = state["_test_url"]
    source = state["sources"]["learn"]
    url_state = source["urls"][url]
    pending = defer.load_pending(defer.pending_path(url, workspace))

    assert url_state["content_hash"] == learn_monitor.compute_hash("old normalized")
    assert url_state["normalized_content"] == "old normalized"
    assert url_state["last_checked"] == source["last_run"]
    assert url_state["last_changed"] == "2026-06-17T00:00:00+00:00"
    assert source["statistics"]["last_run_medium_changes"] == 0
    assert pending is not None
    assert pending["detected_at"] == "2026-06-18T12:00:00+00:00"
