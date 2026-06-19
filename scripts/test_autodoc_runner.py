"""Tests for the unattended autodoc runner orchestration (side effects mocked)."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import autodoc_runner as runner  # noqa: E402


def _config(tmp_path: Path) -> runner.RunnerConfig:
    return runner.RunnerConfig(repo_path=tmp_path, draft_model="model-a", review_model="model-b", max_fix_cycles=2)


def _ctx(route: str = "autodraft") -> runner.ChangeContext:
    return runner.ChangeContext(
        fingerprint="sha256:deadbeefcafe0001",
        route=route,
        contract={"fingerprint": "sha256:deadbeefcafe0001", "report_path": "reports/monitoring/learn-changes-x.md", "allowed_files": ["docs/x.md"]},
        report_path="reports/monitoring/learn-changes-x.md",
        instructions="DO THE EDIT",
        title="Autodoc draft: x",
        labels=["autodoc", "squad:copilot"],
    )


def _draft(needs_human: bool = False, files: list[str] | None = None) -> runner.DraftResult:
    return runner.DraftResult(
        needs_human=needs_human,
        diff_text="+added line",
        changed_files=files if files is not None else ["docs/x.md"],
        notes="",
    )


@pytest.fixture()
def patched(monkeypatch: pytest.MonkeyPatch) -> dict[str, list[Any]]:
    """Neutralize git and capture PR/escalate/ledger calls."""

    calls: dict[str, list[Any]] = {"pr": [], "escalate": [], "ledger": [], "git": []}
    monkeypatch.setattr(runner, "_git", lambda config, *args: calls["git"].append(args) or "")
    monkeypatch.setattr(runner, "_open_pr", lambda config, ctx, draft, verdict: calls["pr"].append(ctx.fingerprint) or "PR#1")
    monkeypatch.setattr(runner, "_escalate", lambda config, ctx, reason, details: calls["escalate"].append(reason) or "ISSUE#1")
    monkeypatch.setattr(runner, "_record_ledger", lambda config, ctx, state, detail: calls["ledger"].append((state, detail)))
    return calls


# --- _combine_conclusion ---------------------------------------------------------


@pytest.mark.parametrize(
    ("deterministic", "verdict", "expected"),
    [
        ("pass", {"verdict": "pass"}, "pass"),
        ("pass", {"verdict": "fail"}, "fail"),
        ("pass", {"verdict": "needs_human"}, "needs_human"),
        ("pass", None, "fail"),
        ("fail", None, "fail"),
        ("needs_human", None, "needs_human"),
        ("anything-else", None, "fail"),
    ],
)
def test_combine_conclusion(deterministic: str, verdict: dict[str, Any] | None, expected: str) -> None:
    assert runner._combine_conclusion(deterministic, verdict) == expected


def test_conclusion_from_exit() -> None:
    assert runner._conclusion_from_exit(0) == "pass"
    assert runner._conclusion_from_exit(1) == "fail"
    assert runner._conclusion_from_exit(2) == "needs_human"
    assert runner._conclusion_from_exit(99) == "needs_human"


# --- contract extraction ---------------------------------------------------------


def test_extract_contract_matches_fingerprint() -> None:
    contract = {"fingerprint": "sha256:abc", "report_path": "reports/monitoring/learn-changes-x.md"}
    body = "AUTODOC-FINGERPRINT: sha256:abc\n```json\n" + json.dumps(contract) + "\n```\n"
    assert runner._extract_contract(body, "sha256:abc") == contract


def test_extract_contract_wrong_fingerprint_raises() -> None:
    body = "```json\n" + json.dumps({"fingerprint": "sha256:other"}) + "\n```"
    with pytest.raises(ValueError):
        runner._extract_contract(body, "sha256:abc")


def test_build_context_rejects_bad_report_path() -> None:
    contract = {"fingerprint": "sha256:abc", "report_path": "scripts/evil.md"}
    spec = {"fingerprint": "sha256:abc", "route": "autodraft", "body": "```json\n" + json.dumps(contract) + "\n```", "title": "t", "labels": []}
    with pytest.raises(ValueError):
        runner._build_context(spec)


# --- process_change paths --------------------------------------------------------


def test_process_change_both_pass_opens_pr(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, patched: dict[str, list[Any]]) -> None:
    monkeypatch.setattr(runner, "_run_draft", lambda config, ctx, feedback: _draft())
    monkeypatch.setattr(runner, "_run_deterministic_verify", lambda config, ctx, draft: "pass")
    monkeypatch.setattr(runner, "_run_cross_model_review", lambda config, ctx, draft: {"verdict": "pass", "confidence": 0.9})

    outcome = runner.process_change(_config(tmp_path), _ctx())

    assert outcome.status == "pr_opened"
    assert patched["pr"] == ["sha256:deadbeefcafe0001"]
    assert patched["escalate"] == []
    assert patched["ledger"][-1][0] == "pr_open"


def test_process_change_draft_needs_human_escalates(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, patched: dict[str, list[Any]]) -> None:
    monkeypatch.setattr(runner, "_run_draft", lambda config, ctx, feedback: _draft(needs_human=True))
    monkeypatch.setattr(runner, "_run_deterministic_verify", lambda config, ctx, draft: pytest.fail("verify must not run"))

    outcome = runner.process_change(_config(tmp_path), _ctx())

    assert outcome.status == "escalated"
    assert patched["pr"] == []
    assert patched["escalate"] == ["draft_needs_human"]


def test_process_change_empty_diff_escalates(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, patched: dict[str, list[Any]]) -> None:
    monkeypatch.setattr(runner, "_run_draft", lambda config, ctx, feedback: _draft(files=[]))

    outcome = runner.process_change(_config(tmp_path), _ctx())

    assert outcome.status == "escalated"
    assert patched["escalate"] == ["draft_needs_human"]


def test_process_change_deterministic_needs_human_escalates(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, patched: dict[str, list[Any]]) -> None:
    monkeypatch.setattr(runner, "_run_draft", lambda config, ctx, feedback: _draft())
    monkeypatch.setattr(runner, "_run_deterministic_verify", lambda config, ctx, draft: "needs_human")
    monkeypatch.setattr(runner, "_run_cross_model_review", lambda config, ctx, draft: pytest.fail("review must not run when deterministic needs_human"))

    outcome = runner.process_change(_config(tmp_path), _ctx())

    assert outcome.status == "escalated"
    assert patched["pr"] == []


def test_process_change_retries_then_succeeds(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, patched: dict[str, list[Any]]) -> None:
    drafts = iter([_draft(), _draft()])
    verifies = iter(["fail", "pass"])
    monkeypatch.setattr(runner, "_run_draft", lambda config, ctx, feedback: next(drafts))
    monkeypatch.setattr(runner, "_run_deterministic_verify", lambda config, ctx, draft: next(verifies))
    monkeypatch.setattr(runner, "_run_cross_model_review", lambda config, ctx, draft: {"verdict": "pass"})

    outcome = runner.process_change(_config(tmp_path), _ctx())

    assert outcome.status == "pr_opened"
    assert patched["pr"] == ["sha256:deadbeefcafe0001"]


def test_process_change_exceeds_fix_cycles_escalates(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, patched: dict[str, list[Any]]) -> None:
    draft_calls = {"n": 0}

    def draft(config: Any, ctx: Any, feedback: str) -> runner.DraftResult:
        draft_calls["n"] += 1
        return _draft()

    monkeypatch.setattr(runner, "_run_draft", draft)
    monkeypatch.setattr(runner, "_run_deterministic_verify", lambda config, ctx, d: "fail")  # always fails
    monkeypatch.setattr(runner, "_run_cross_model_review", lambda config, ctx, d: {"verdict": "pass"})

    outcome = runner.process_change(_config(tmp_path), _ctx())

    assert outcome.status == "escalated"
    assert patched["pr"] == []
    # initial attempt + max_fix_cycles (2) retries = 3 draft calls
    assert draft_calls["n"] == 3


def test_process_change_review_fail_then_escalates(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, patched: dict[str, list[Any]]) -> None:
    monkeypatch.setattr(runner, "_run_draft", lambda config, ctx, feedback: _draft())
    monkeypatch.setattr(runner, "_run_deterministic_verify", lambda config, ctx, draft: "pass")
    monkeypatch.setattr(runner, "_run_cross_model_review", lambda config, ctx, draft: {"verdict": "fail", "unsupported_claims": ["bad date"]})

    outcome = runner.process_change(_config(tmp_path), _ctx())

    assert outcome.status == "escalated"
    assert patched["pr"] == []


def test_process_change_always_returns_to_base_branch(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, patched: dict[str, list[Any]]) -> None:
    monkeypatch.setattr(runner, "_run_draft", lambda config, ctx, feedback: _draft())
    monkeypatch.setattr(runner, "_run_deterministic_verify", lambda config, ctx, draft: "pass")
    monkeypatch.setattr(runner, "_run_cross_model_review", lambda config, ctx, draft: {"verdict": "pass"})

    runner.process_change(_config(tmp_path), _ctx())

    # finally-block force-restores the base branch, discarding any failed draft edits
    assert ("checkout", "--force", "main") in patched["git"]


# --- feedback text ---------------------------------------------------------------


def test_feedback_text_lists_claims() -> None:
    text = runner._feedback_text("pass", {"verdict": "fail", "unsupported_claims": ["Fabricated date"], "overbroad_edits": ["Too broad"], "notes": "n"})
    assert "Fabricated date" in text
    assert "Too broad" in text
    assert "Independent review: fail" in text


# --- run() guard + routing -------------------------------------------------------


def test_run_disabled_is_noop(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.delenv("AUTODOC_ENABLED", raising=False)
    result = runner.run(_config(tmp_path))
    assert result == {"enabled": False, "outcomes": []}


def test_run_enabled_no_report(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("AUTODOC_ENABLED", "true")
    monkeypatch.setattr(runner, "_latest_report", lambda config: None)
    result = runner.run(_config(tmp_path))
    assert result["enabled"] is True
    assert result["outcomes"] == []


def test_run_routes_human_change_to_escalation(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, patched: dict[str, list[Any]]) -> None:
    monkeypatch.setenv("AUTODOC_ENABLED", "true")
    report = tmp_path / "report.md"
    report.write_text("irrelevant", encoding="utf-8")
    monkeypatch.setattr(runner, "_latest_report", lambda config: report)
    monkeypatch.setattr(runner.autodoc_route, "load_ledger", lambda path: {"schema_version": 1, "changes": {}})
    contract = {"fingerprint": "sha256:h", "report_path": "reports/monitoring/learn-changes-x.md"}
    spec = {"fingerprint": "sha256:h", "route": "human", "body": "```json\n" + json.dumps(contract) + "\n```", "title": "human", "labels": ["autodoc", "escalate"]}
    monkeypatch.setattr(runner.autodoc_route, "route_report", lambda text, name, ledger: [spec])

    result = runner.run(_config(tmp_path))

    assert result["outcomes"][0]["status"] == "escalated"
    assert patched["escalate"] == ["route=human"]
    assert patched["pr"] == []


def test_run_autodraft_change_opens_pr(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, patched: dict[str, list[Any]]) -> None:
    monkeypatch.setenv("AUTODOC_ENABLED", "true")
    report = tmp_path / "report.md"
    report.write_text("irrelevant", encoding="utf-8")
    monkeypatch.setattr(runner, "_latest_report", lambda config: report)
    monkeypatch.setattr(runner.autodoc_route, "load_ledger", lambda path: {"schema_version": 1, "changes": {}})
    contract = {"fingerprint": "sha256:a", "report_path": "reports/monitoring/learn-changes-x.md", "allowed_files": ["docs/x.md"]}
    spec = {"fingerprint": "sha256:a", "route": "autodraft", "body": "```json\n" + json.dumps(contract) + "\n```", "title": "draft", "labels": ["autodoc"]}
    monkeypatch.setattr(runner.autodoc_route, "route_report", lambda text, name, ledger: [spec])
    monkeypatch.setattr(runner, "_run_draft", lambda config, ctx, feedback: _draft())
    monkeypatch.setattr(runner, "_run_deterministic_verify", lambda config, ctx, draft: "pass")
    monkeypatch.setattr(runner, "_run_cross_model_review", lambda config, ctx, draft: {"verdict": "pass"})

    result = runner.run(_config(tmp_path))

    assert result["outcomes"][0]["status"] == "pr_opened"
    assert patched["pr"] == ["sha256:a"]


def test_run_isolates_per_change_failure(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, patched: dict[str, list[Any]]) -> None:
    monkeypatch.setenv("AUTODOC_ENABLED", "true")
    report = tmp_path / "report.md"
    report.write_text("irrelevant", encoding="utf-8")
    monkeypatch.setattr(runner, "_latest_report", lambda config: report)
    monkeypatch.setattr(runner.autodoc_route, "load_ledger", lambda path: {"schema_version": 1, "changes": {}})
    contract = {"fingerprint": "sha256:a", "report_path": "reports/monitoring/learn-changes-x.md", "allowed_files": ["docs/x.md"]}
    spec = {"fingerprint": "sha256:a", "route": "autodraft", "body": "```json\n" + json.dumps(contract) + "\n```", "title": "draft", "labels": ["autodoc"]}
    monkeypatch.setattr(runner.autodoc_route, "route_report", lambda text, name, ledger: [spec])

    def boom(config: Any, ctx: Any, feedback: str) -> runner.DraftResult:
        raise RuntimeError("git exploded")

    monkeypatch.setattr(runner, "_run_draft", boom)

    result = runner.run(_config(tmp_path))

    assert result["outcomes"][0]["status"] == "error"
    assert "processing_error" in result["outcomes"][0]["detail"]
