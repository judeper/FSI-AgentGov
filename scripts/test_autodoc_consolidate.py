"""Tests for autodoc issue supersession consolidation CLI."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import autodoc_consolidate as consolidate  # noqa: E402


def _issue(
    *,
    number: int,
    state: str,
    fingerprint: str | None,
    source_url: str | None,
    content_hash: str | None,
    state_reason: str | None = None,
) -> dict[str, Any]:
    lines: list[str] = []
    if fingerprint:
        lines.append(f"AUTODOC-FINGERPRINT: {fingerprint}")
    if source_url:
        lines.append(f"Source: {source_url}")
    if content_hash:
        lines.append(f"Content-Hash: {content_hash}")
    return {
        "number": number,
        "url": f"https://github.com/x/y/issues/{number}",
        "state": state,
        "stateReason": state_reason,
        "body": "\n".join(lines) + ("\n" if lines else ""),
    }


def _write_snapshot(path: Path, payload: list[dict[str, Any]]) -> str:
    path.write_text(json.dumps(payload), encoding="utf-8")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_plan_supersession_exact_source_and_lookalike_handling() -> None:
    source = "https://learn.microsoft.com/en-us/power-platform/admin/example"
    lookalike = f"{source}-archive"
    plan = consolidate.plan_supersession(
        [
            _issue(
                number=20,
                state="CLOSED",
                state_reason="COMPLETED",
                fingerprint="sha256:done",
                source_url=source,
                content_hash="sha256:done-hash",
            ),
            _issue(
                number=10,
                state="OPEN",
                state_reason=None,
                fingerprint="sha256:older",
                source_url=source,
                content_hash="sha256:older-hash",
            ),
            _issue(
                number=30,
                state="OPEN",
                state_reason=None,
                fingerprint="sha256:newer",
                source_url=source,
                content_hash="sha256:newer-hash",
            ),
            _issue(
                number=11,
                state="OPEN",
                state_reason=None,
                fingerprint="sha256:lookalike",
                source_url=lookalike,
                content_hash="sha256:lookalike-hash",
            ),
            # old schema/unmappable retention (kept by default)
            _issue(
                number=40,
                state="OPEN",
                state_reason=None,
                fingerprint="sha256:legacy",
                source_url=None,
                content_hash=None,
            ),
            _issue(
                number=41,
                state="OPEN",
                state_reason=None,
                fingerprint=None,
                source_url=None,
                content_hash=None,
            ),
        ]
    )

    assert plan["summary"]["closures_planned"] == 1
    closure = plan["closures"][0]
    assert closure["number"] == 10
    assert closure["source_url"] == source
    assert closure["reason"] == "completed_source_supersession"
    assert closure["superseded_by"]["number"] == 20
    active_numbers = {entry["number"] for entry in plan["retained"]["active_open"]}
    assert 11 in active_numbers  # look-alike URL is not an exact-source sibling
    assert 30 in active_numbers
    assert {entry["number"] for entry in plan["retained"]["old_schema"]} == {40}
    assert {entry["number"] for entry in plan["retained"]["unmappable"]} == {41}


def test_main_dry_run_writes_zero_issue_commands(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    snapshot_path = tmp_path / "issues.json"
    snapshot_path.write_text(
        json.dumps(
            [
                _issue(
                    number=2,
                    state="OPEN",
                    state_reason=None,
                    fingerprint="sha256:older",
                    source_url="https://learn.microsoft.com/en-us/example",
                    content_hash="sha256:older-hash",
                ),
                _issue(
                    number=3,
                    state="OPEN",
                    state_reason=None,
                    fingerprint="sha256:newer",
                    source_url="https://learn.microsoft.com/en-us/example",
                    content_hash="sha256:newer-hash",
                ),
            ]
        ),
        encoding="utf-8",
    )

    def explode(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("dry-run must not call gh issue close")

    monkeypatch.setattr(consolidate.subprocess, "run", explode)
    assert consolidate.main(["--issues-json", str(snapshot_path)]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["mode"] == "dry_run"
    assert payload["writes"]["attempted"] == 0
    assert payload["writes"]["succeeded"] == 0


def test_main_guard_mismatch_aborts_without_writes(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    snapshot_path = tmp_path / "issues.json"
    snapshot_path.write_text(json.dumps([_issue(number=9, state="OPEN", state_reason=None, fingerprint=None, source_url=None, content_hash=None)]), encoding="utf-8")

    def explode(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("guard mismatch must abort before any gh write")

    monkeypatch.setattr(consolidate.subprocess, "run", explode)
    assert consolidate.main(["--issues-json", str(snapshot_path), "--expected-count", "999", "--apply"]) == 2
    payload = json.loads(capsys.readouterr().out)
    assert payload["aborted"] is True
    assert payload["guards"]["ok"] is False
    assert "apply mode requires both --expected-count and --expected-snapshot-sha256" in payload["guards"]["errors"]
    assert payload["writes"]["attempted"] == 0


def test_main_apply_closes_with_not_planned_and_comment(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    source = "https://learn.microsoft.com/en-us/example"
    snapshot_path = tmp_path / "issues.json"
    snapshot_sha256 = _write_snapshot(
        snapshot_path,
        [
            _issue(
                number=20,
                state="CLOSED",
                state_reason="COMPLETED",
                fingerprint="sha256:done",
                source_url=source,
                content_hash="sha256:done-hash",
            ),
            _issue(
                number=10,
                state="OPEN",
                state_reason=None,
                fingerprint="sha256:older",
                source_url=source,
                content_hash="sha256:older-hash",
            ),
        ],
    )

    commands: list[list[str]] = []

    def fake_run(args: Any, **kwargs: Any) -> SimpleNamespace:
        commands.append(list(args))
        return SimpleNamespace(returncode=0, stdout="closed", stderr="")

    monkeypatch.setattr(consolidate.subprocess, "run", fake_run)
    rc = consolidate.main(
        [
            "--issues-json",
            str(snapshot_path),
            "--apply",
            "--expected-count",
            "2",
            "--expected-snapshot-sha256",
            snapshot_sha256,
            "--max-closures",
            "5",
            "--repo",
            "owner/repo",
        ]
    )
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["mode"] == "apply"
    assert payload["writes"]["attempted"] == 1
    assert payload["writes"]["succeeded"] == 1
    assert payload["writes"]["failed"] == []

    close = commands[0]
    assert close[:4] == ["gh", "issue", "close", "10"]
    assert "--repo" in close and close[close.index("--repo") + 1] == "owner/repo"
    assert "--reason" in close and close[close.index("--reason") + 1] == "not planned"
    comment = close[close.index("--comment") + 1]
    assert "Superseded by https://github.com/x/y/issues/20." in comment
    assert "Audit: exact-source sibling supersession" in comment
    assert f"- Exact Source: {source}" in comment


def test_main_apply_partial_failure_reports_and_returns_nonzero(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    snapshot_path = tmp_path / "issues.json"
    snapshot_sha256 = _write_snapshot(
        snapshot_path,
        [
            _issue(
                number=20,
                state="CLOSED",
                state_reason="COMPLETED",
                fingerprint="sha256:done-a",
                source_url="https://learn.microsoft.com/en-us/source-a",
                content_hash="sha256:done-a",
            ),
            _issue(
                number=10,
                state="OPEN",
                state_reason=None,
                fingerprint="sha256:open-a",
                source_url="https://learn.microsoft.com/en-us/source-a",
                content_hash="sha256:open-a",
            ),
            _issue(
                number=21,
                state="CLOSED",
                state_reason="COMPLETED",
                fingerprint="sha256:done-b",
                source_url="https://learn.microsoft.com/en-us/source-b",
                content_hash="sha256:done-b",
            ),
            _issue(
                number=11,
                state="OPEN",
                state_reason=None,
                fingerprint="sha256:open-b",
                source_url="https://learn.microsoft.com/en-us/source-b",
                content_hash="sha256:open-b",
            ),
        ],
    )

    def fake_run(args: Any, **kwargs: Any) -> SimpleNamespace:
        issue_number = args[3]
        if issue_number == "10":
            return SimpleNamespace(returncode=1, stdout="", stderr="close failed for 10")
        return SimpleNamespace(returncode=0, stdout="closed", stderr="")

    monkeypatch.setattr(consolidate.subprocess, "run", fake_run)
    rc = consolidate.main(
        [
            "--issues-json",
            str(snapshot_path),
            "--apply",
            "--expected-count",
            "4",
            "--expected-snapshot-sha256",
            snapshot_sha256,
            "--max-closures",
            "5",
        ]
    )
    assert rc == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["writes"]["attempted"] == 2
    assert payload["writes"]["succeeded"] == 1
    assert payload["writes"]["failed"] == [
        {"number": 10, "reason": "completed_source_supersession", "error": "close failed for 10"}
    ]


def test_main_apply_max_closures_exceeded_aborts_before_writes(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    snapshot_path = tmp_path / "issues.json"
    snapshot_sha256 = _write_snapshot(
        snapshot_path,
        [
            _issue(
                number=20,
                state="CLOSED",
                state_reason="COMPLETED",
                fingerprint="sha256:done-a",
                source_url="https://learn.microsoft.com/en-us/source-a",
                content_hash="sha256:done-a",
            ),
            _issue(
                number=10,
                state="OPEN",
                state_reason=None,
                fingerprint="sha256:open-a",
                source_url="https://learn.microsoft.com/en-us/source-a",
                content_hash="sha256:open-a",
            ),
            _issue(
                number=21,
                state="CLOSED",
                state_reason="COMPLETED",
                fingerprint="sha256:done-b",
                source_url="https://learn.microsoft.com/en-us/source-b",
                content_hash="sha256:done-b",
            ),
            _issue(
                number=11,
                state="OPEN",
                state_reason=None,
                fingerprint="sha256:open-b",
                source_url="https://learn.microsoft.com/en-us/source-b",
                content_hash="sha256:open-b",
            ),
        ],
    )

    def explode(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("max-closures failure must abort before any gh write")

    monkeypatch.setattr(consolidate.subprocess, "run", explode)
    rc = consolidate.main(
        [
            "--issues-json",
            str(snapshot_path),
            "--apply",
            "--expected-count",
            "4",
            "--expected-snapshot-sha256",
            snapshot_sha256,
            "--max-closures",
            "1",
        ]
    )
    assert rc == 2
    payload = json.loads(capsys.readouterr().out)
    assert payload["aborted"] is True
    assert payload["guards"]["ok"] is False
    assert "max_closures exceeded: planned=2 limit=1" in payload["guards"]["errors"]
    assert payload["writes"]["attempted"] == 0
