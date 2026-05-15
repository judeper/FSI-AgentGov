"""Tests for verify_learn_url_health.py — the Learn-URL CI gate.

Closes F-LEARN-URL-DEAD-LINKS-CI-GAP-01.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import verify_learn_url_health  # noqa: E402


def _state(urls: dict[str, dict]) -> dict:
    """Build a schema_version=2 monitor-state dict."""
    return {
        "version": 1,
        "sources": {
            "learn": {
                "schema_version": 2,
                "last_run": "2026-01-01T00:00:00+00:00",
                "statistics": {
                    "total_urls": len(urls),
                    "last_run_checked": len(urls),
                    "last_run_errors": 0,
                    "last_run_redirects": 0,
                    "last_run_critical_changes": 0,
                    "last_run_high_changes": 0,
                    "last_run_medium_changes": 0,
                },
                "urls": urls,
            }
        },
    }


def _legacy_state(urls: dict[str, dict]) -> dict:
    """Schema_version=1 monitor-state (no sources wrapper). Verifier must tolerate."""
    return {"version": 0, "urls": urls}


def _entry(status: int, **extra) -> dict:
    return {
        "last_status": status,
        "last_checked": "2026-01-01T00:00:00+00:00",
        "section": extra.get("section", ""),
        "topic": extra.get("topic", ""),
        "content_hash": extra.get("content_hash", ""),
        "normalized_content": extra.get("normalized_content", ""),
    }


# -- find_dead_urls -----------------------------------------------------------

def test_find_dead_urls_returns_empty_when_all_200() -> None:
    state = _state({
        "https://learn.microsoft.com/a": _entry(200),
        "https://learn.microsoft.com/b": _entry(200),
        "https://learn.microsoft.com/c": _entry(301),
    })
    assert verify_learn_url_health.find_dead_urls(state) == []


def test_find_dead_urls_flags_404() -> None:
    state = _state({
        "https://learn.microsoft.com/a": _entry(200),
        "https://learn.microsoft.com/gone": _entry(404, section="Sec", topic="Tpc"),
    })
    dead = verify_learn_url_health.find_dead_urls(state)
    assert len(dead) == 1
    assert dead[0]["url"] == "https://learn.microsoft.com/gone"
    assert dead[0]["status"] == 404
    assert dead[0]["section"] == "Sec"
    assert dead[0]["topic"] == "Tpc"


def test_find_dead_urls_flags_410_and_451() -> None:
    state = _state({
        "https://learn.microsoft.com/410": _entry(410),
        "https://learn.microsoft.com/451": _entry(451),
        "https://learn.microsoft.com/200": _entry(200),
    })
    dead = verify_learn_url_health.find_dead_urls(state)
    assert {d["status"] for d in dead} == {410, 451}


def test_find_dead_urls_does_not_flag_5xx_or_timeouts() -> None:
    """5xx and transient errors are NOT dead — gate would be flaky."""
    state = _state({
        "https://learn.microsoft.com/500": _entry(500),
        "https://learn.microsoft.com/503": _entry(503),
        "https://learn.microsoft.com/timeout": {"last_status": None},
        "https://learn.microsoft.com/missing": {},  # no last_status field
    })
    assert verify_learn_url_health.find_dead_urls(state) == []


def test_find_dead_urls_sorts_by_status_then_url() -> None:
    state = _state({
        "https://learn.microsoft.com/z-410": _entry(410),
        "https://learn.microsoft.com/a-410": _entry(410),
        "https://learn.microsoft.com/b-404": _entry(404),
    })
    dead = verify_learn_url_health.find_dead_urls(state)
    assert [d["url"] for d in dead] == [
        "https://learn.microsoft.com/b-404",
        "https://learn.microsoft.com/a-410",
        "https://learn.microsoft.com/z-410",
    ]


def test_find_dead_urls_handles_legacy_schema() -> None:
    """schema_version=1 state has urls at the top level (no sources wrapper)."""
    state = _legacy_state({
        "https://learn.microsoft.com/gone": _entry(404),
    })
    dead = verify_learn_url_health.find_dead_urls(state)
    assert len(dead) == 1
    assert dead[0]["status"] == 404


def test_find_dead_urls_handles_empty_state() -> None:
    assert verify_learn_url_health.find_dead_urls({}) == []
    assert verify_learn_url_health.find_dead_urls({"sources": {}}) == []
    assert verify_learn_url_health.find_dead_urls({"sources": {"learn": {}}}) == []


# -- main() exit codes --------------------------------------------------------

def test_main_exits_zero_on_clean_state(tmp_path: Path, capsys) -> None:
    state_path = tmp_path / "monitor-state.json"
    state_path.write_text(json.dumps(_state({
        "https://learn.microsoft.com/a": _entry(200),
        "https://learn.microsoft.com/b": _entry(301),
    })), encoding="utf-8")
    rc = verify_learn_url_health.main(["--state-file", str(state_path)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "OK:" in out
    assert "scanned 2" in out


def test_main_exits_one_on_dead_url(tmp_path: Path, capsys) -> None:
    state_path = tmp_path / "monitor-state.json"
    state_path.write_text(json.dumps(_state({
        "https://learn.microsoft.com/gone": _entry(404),
    })), encoding="utf-8")
    rc = verify_learn_url_health.main(["--state-file", str(state_path)])
    assert rc == 1
    out = capsys.readouterr().out
    assert "FAIL" in out
    assert "[404]" in out
    assert "https://learn.microsoft.com/gone" in out


def test_main_exits_two_on_missing_state_file(tmp_path: Path) -> None:
    rc = verify_learn_url_health.main(
        ["--state-file", str(tmp_path / "nope.json")]
    )
    assert rc == 2


def test_main_exits_two_on_unparseable_state(tmp_path: Path) -> None:
    state_path = tmp_path / "bad.json"
    state_path.write_text("{ not valid json", encoding="utf-8")
    rc = verify_learn_url_health.main(["--state-file", str(state_path)])
    assert rc == 2


def test_main_truncates_long_dead_lists(tmp_path: Path, capsys) -> None:
    state_path = tmp_path / "monitor-state.json"
    urls = {
        f"https://learn.microsoft.com/{i:03d}": _entry(404)
        for i in range(20)
    }
    state_path.write_text(json.dumps(_state(urls)), encoding="utf-8")
    rc = verify_learn_url_health.main(
        ["--state-file", str(state_path), "--max-print", "5"]
    )
    assert rc == 1
    out = capsys.readouterr().out
    assert "... 15 more" in out


# -- Smoke: real state file (best-effort) -------------------------------------

@pytest.mark.skipif(
    not Path("data/monitor-state.json").is_file(),
    reason="real monitor-state.json not present",
)
def test_real_state_file_scans_without_error() -> None:
    """Sanity: verifier processes the real production state file cleanly.

    Does not assert pass/fail — that depends on Learn URL drift.
    """
    state = json.loads(Path("data/monitor-state.json").read_text(encoding="utf-8"))
    dead = verify_learn_url_health.find_dead_urls(state)
    assert isinstance(dead, list)
