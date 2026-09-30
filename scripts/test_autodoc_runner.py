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

import autodoc_classifier as ac  # noqa: E402
import autodoc_route as route  # noqa: E402
import autodoc_runner as runner  # noqa: E402


def test_main_passes_timeout_flags_into_config(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    captured: dict[str, Any] = {}

    def fake_run(config: runner.RunnerConfig) -> dict[str, Any]:
        captured["config"] = config
        return {"enabled": False, "outcomes": []}

    monkeypatch.setattr(runner, "run", fake_run)
    runner.main(
        [
            "--repo",
            str(tmp_path),
            "--draft-model",
            "claude-opus-4.8",
            "--review-model",
            "gpt-5.5",
            "--draft-timeout",
            "1500",
            "--review-timeout",
            "400",
        ]
    )
    config = captured["config"]
    assert config.draft_timeout == 1500
    assert config.review_timeout == 400
    assert config.draft_model == "claude-opus-4.8"
    assert config.review_model == "gpt-5.5"


def test_default_timeouts_are_generous() -> None:
    # An Opus draft exploring a large worktree can exceed 600s; defaults must be roomy.
    assert runner.DEFAULT_DRAFT_TIMEOUT >= 1200
    assert runner.DEFAULT_REVIEW_TIMEOUT >= 300


# --- deterministic redirect handling --------------------------------------------


def _redirect_ctx(old_url: str, new_url: str, allowed: tuple[str, ...] = ("docs/reference/microsoft-learn-urls.md",)) -> runner.ChangeContext:
    return runner.ChangeContext(
        fingerprint="sha256:redir01",
        route="autodraft",
        contract={"classification": "REDIRECT", "source_url": old_url, "allowed_files": list(allowed)},
        report_path="reports/monitoring/learn-changes-x.md",
        instructions=f"## Learn change evidence\n```diff\nredirects to {new_url}\n```\n",
        title="URL redirect",
        labels=["autodoc"],
    )


def test_is_redirect() -> None:
    assert runner._is_redirect(_redirect_ctx("https://old/", "https://new/"))
    assert not runner._is_redirect(_ctx())


def test_redirect_diff_is_clean_accepts_url_only_swap() -> None:
    old, new = "https://a/old/", "https://a/new/"
    diff = f"--- a/x\n+++ b/x\n@@ -1 +1 @@\n-| Title | {old} | Mar 2026 |\n+| Title | {new} | Mar 2026 |\n"
    assert runner._redirect_diff_is_clean(["docs/reference/microsoft-learn-urls.md"], ["docs/reference/microsoft-learn-urls.md"], diff, old, new)


def test_redirect_diff_is_clean_rejects_extra_change() -> None:
    old, new = "https://a/old/", "https://a/new/"
    diff = f"-| Title | {old} | Mar 2026 |\n+| Title | {new} | Apr 2026 |\n"  # date also changed
    assert not runner._redirect_diff_is_clean(["docs/reference/microsoft-learn-urls.md"], ["docs/reference/microsoft-learn-urls.md"], diff, old, new)


def test_redirect_diff_is_clean_rejects_wrong_file() -> None:
    old, new = "https://a/old/", "https://a/new/"
    diff = f"-{old}\n+{new}\n"
    assert not runner._redirect_diff_is_clean(["docs/controls/x.md"], ["docs/reference/microsoft-learn-urls.md"], diff, old, new)


def test_redirect_diff_is_clean_rejects_prefix_corrupted_sibling() -> None:
    # Independent of the replacement regex: if a sibling cell (value != old_url) was altered, the
    # structural guard must reject because its URL cell is not exactly old_url.
    old, new = "https://learn.microsoft.com/a/foo", "https://learn.microsoft.com/a/baz"
    diff = (
        f"-| B | {old}{{bar}} | Jan 2026 |\n"  # sibling cell value is old+'{bar}', not old_url
        f"+| B | {new}{{bar}} | Jan 2026 |\n"
    )
    assert not runner._redirect_diff_is_clean(["docs/reference/microsoft-learn-urls.md"], ["docs/reference/microsoft-learn-urls.md"], diff, old, new)


def test_redirect_diff_is_clean_rejects_non_table_line() -> None:
    old, new = "https://a/old/", "https://a/new/"
    diff = f"-See {old} for details\n+See {new} for details\n"  # prose, no pipe-delimited URL cell
    assert not runner._redirect_diff_is_clean(["docs/reference/microsoft-learn-urls.md"], ["docs/reference/microsoft-learn-urls.md"], diff, old, new)


def _redirect_git_mock(diff: str):
    def fake_git(config: Any, *args: str) -> str:
        if "--name-only" in args:
            return "docs/reference/microsoft-learn-urls.md\n"
        if args[:2] == ("diff", "--cached"):
            return diff
        return ""
    return fake_git


def test_process_redirect_clean_swap_opens_pr(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    old, new = "https://learn.microsoft.com/old/", "https://learn.microsoft.com/new/"
    url_file = tmp_path / "docs" / "reference" / "microsoft-learn-urls.md"
    url_file.parent.mkdir(parents=True)
    url_file.write_text(f"| Architecting | {old} | Mar 2026 |\n", encoding="utf-8")
    diff = f"--- a/x\n+++ b/x\n@@ -1 +1 @@\n-| Architecting | {old} | Mar 2026 |\n+| Architecting | {new} | Mar 2026 |\n"
    monkeypatch.setattr(runner, "_git", _redirect_git_mock(diff))
    monkeypatch.setattr(runner, "_untracked_files", lambda config: [])
    monkeypatch.setattr(runner, "_reset_attempt", lambda config, base, baseline: None)
    pr_calls: list[str] = []
    monkeypatch.setattr(runner, "_push_and_create_pr", lambda config, ctx, body: pr_calls.append(body) or "PR#9")
    ledger: list[tuple[str, str]] = []
    monkeypatch.setattr(runner, "_record_ledger", lambda config, ctx, state, detail: ledger.append((state, detail)))

    cfg = runner.RunnerConfig(repo_path=tmp_path, draft_model="a", review_model="b")
    outcome = runner._process_redirect(cfg, _redirect_ctx(old, new))

    assert outcome.status == "pr_opened"
    assert new in url_file.read_text(encoding="utf-8")  # the file was actually swapped
    assert old not in url_file.read_text(encoding="utf-8")
    assert ledger[-1][0] == "pr_open"
    assert old in pr_calls[0] and new in pr_calls[0]
    assert "OceanSquad reviews and SHA-pinned merges" in pr_calls[0]
    assert "human merge required" not in pr_calls[0].lower()


def test_regression_734_tracking_urls_produce_one_clean_canonical_redirect(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    canonical_old = "https://learn.microsoft.com/en-us/old?view=power-platform#limits"
    tracked_old = canonical_old.replace("?", "?msockid=abc&")
    canonical_new = "https://learn.microsoft.com/en-us/new?view=power-platform#limits"
    tracked_new = canonical_new.replace("?", "?utm_source=monitor&ocid=test&")
    url_file = tmp_path / "docs" / "reference" / "microsoft-learn-urls.md"
    url_file.parent.mkdir(parents=True)
    url_file.write_text(f"| Redirect | {tracked_old} | Mar 2026 |\n", encoding="utf-8")
    diff = (
        "--- a/x\n+++ b/x\n@@ -1 +1 @@\n"
        f"-| Redirect | {tracked_old} | Mar 2026 |\n"
        f"+| Redirect | {canonical_new} | Mar 2026 |\n"
    )
    monkeypatch.setattr(runner, "_git", _redirect_git_mock(diff))
    monkeypatch.setattr(runner, "_untracked_files", lambda config: [])
    monkeypatch.setattr(runner, "_reset_attempt", lambda config, base, baseline: None)
    bodies: list[str] = []
    monkeypatch.setattr(runner, "_push_and_create_pr", lambda config, ctx, body: bodies.append(body) or "PR#734")
    monkeypatch.setattr(runner, "_record_ledger", lambda config, ctx, state, detail: None)

    ctx = _redirect_ctx(canonical_old, tracked_new)
    ctx.contract["destination_url"] = tracked_new
    outcome = runner._process_redirect(
        runner.RunnerConfig(repo_path=tmp_path, draft_model="a", review_model="b"),
        ctx,
    )

    assert outcome.status == "pr_opened"
    assert canonical_new in url_file.read_text(encoding="utf-8")
    assert "utm_source" not in url_file.read_text(encoding="utf-8")
    assert canonical_new in bodies[0]
    assert tracked_new not in bodies[0]


def test_process_redirect_uses_route_contract_operational_urls_with_fragments(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    source = "HTTPS://LEARN.MICROSOFT.COM/en-us/old?msockid=tracked&view=power-platform#source-fragment"
    destination = "https://learn.microsoft.com/en-us/new?utm_source=monitor&view=power-platform#destination-fragment"
    operational_source = ac._canonicalize_url(source)  # noqa: SLF001 - this test locks route/runner integration.
    operational_destination = ac._canonicalize_url(destination)  # noqa: SLF001
    url_file = tmp_path / "docs" / "reference" / "microsoft-learn-urls.md"
    url_file.parent.mkdir(parents=True)
    url_file.write_text(f"| Redirect | {operational_source} | Mar 2026 |\n", encoding="utf-8")
    diff = (
        "--- a/x\n+++ b/x\n@@ -1 +1 @@\n"
        f"-| Redirect | {operational_source} | Mar 2026 |\n"
        f"+| Redirect | {operational_destination} | Mar 2026 |\n"
    )
    monkeypatch.setattr(runner, "_git", _redirect_git_mock(diff))
    monkeypatch.setattr(runner, "_untracked_files", lambda config: [])
    monkeypatch.setattr(runner, "_reset_attempt", lambda config, base, baseline: None)
    monkeypatch.setattr(runner, "_push_and_create_pr", lambda config, ctx, body: "PR#1705")
    monkeypatch.setattr(runner, "_record_ledger", lambda config, ctx, state, detail: None)

    change = ac.Change(
        topic=f"URL redirect: {source}",
        url=source,
        classification="REDIRECT",
        reason=f"redirects to {destination}",
        kind="redirect",
        destination_url=destination,
    )
    decision = ac.classify_change(change)
    fingerprint = route.compute_fingerprint(
        "report.md",
        decision.url,
        decision.classification,
        [route.REDIRECT_TARGET_FILE],
        decision.destination_url,
    )
    contract = route.build_contract(
        decision,
        "report.md",
        [route.REDIRECT_TARGET_FILE],
        fingerprint,
        repo_root=tmp_path,
    )
    ctx = runner.ChangeContext(
        fingerprint=fingerprint,
        route="autodraft",
        contract=contract,
        report_path=contract["report_path"],
        instructions=f"## Learn change evidence\n```diff\nredirects to {operational_destination}\n```\n",
        title=f"Autodoc draft: URL redirect: {operational_source}",
        labels=["autodoc"],
    )

    outcome = runner._process_redirect(runner.RunnerConfig(repo_path=tmp_path, draft_model="a", review_model="b"), ctx)

    assert outcome.status == "pr_opened"
    content = url_file.read_text(encoding="utf-8")
    assert operational_source not in content
    assert f"| Redirect | {operational_destination} |" in content


def test_process_redirect_url_not_found_escalates(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    url_file = tmp_path / "docs" / "reference" / "microsoft-learn-urls.md"
    url_file.parent.mkdir(parents=True)
    url_file.write_text("| Something else | https://other/ | Mar 2026 |\n", encoding="utf-8")
    monkeypatch.setattr(runner, "_git", _redirect_git_mock(""))
    monkeypatch.setattr(runner, "_untracked_files", lambda config: [])
    monkeypatch.setattr(runner, "_reset_attempt", lambda config, base, baseline: None)
    escalations: list[str] = []
    monkeypatch.setattr(runner, "_escalate", lambda config, ctx, reason, details: escalations.append(reason) or "ISSUE#1")
    monkeypatch.setattr(runner, "_record_ledger", lambda config, ctx, state, detail: None)

    cfg = runner.RunnerConfig(repo_path=tmp_path, draft_model="a", review_model="b")
    outcome = runner._process_redirect(cfg, _redirect_ctx("https://learn.microsoft.com/missing/", "https://learn.microsoft.com/new/"))

    assert outcome.status == "escalated"
    assert escalations == ["redirect_url_not_found"]


def test_process_redirect_ambiguous_new_url_present_escalates(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    old, new = "https://learn.microsoft.com/old/", "https://learn.microsoft.com/new/"
    url_file = tmp_path / "docs" / "reference" / "microsoft-learn-urls.md"
    url_file.parent.mkdir(parents=True)
    url_file.write_text(f"| A | {old} | Mar 2026 |\n| B | {new} | Mar 2026 |\n", encoding="utf-8")
    monkeypatch.setattr(runner, "_git", _redirect_git_mock(""))
    monkeypatch.setattr(runner, "_untracked_files", lambda config: [])
    monkeypatch.setattr(runner, "_reset_attempt", lambda config, base, baseline: None)
    escalations: list[str] = []
    monkeypatch.setattr(runner, "_escalate", lambda config, ctx, reason, details: escalations.append(reason) or "ISSUE#1")
    monkeypatch.setattr(runner, "_record_ledger", lambda config, ctx, state, detail: None)

    cfg = runner.RunnerConfig(repo_path=tmp_path, draft_model="a", review_model="b")
    outcome = runner._process_redirect(cfg, _redirect_ctx(old, new))

    assert outcome.status == "escalated"
    assert escalations == ["redirect_ambiguous"]


def test_process_redirect_new_url_prefix_of_sibling_not_ambiguous(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    # new_url is a strict prefix of an unrelated sibling URL; the boundary-aware ambiguity check
    # must NOT treat the sibling as "new URL already present" and spuriously escalate.
    old = "https://learn.microsoft.com/en-us/power-platform/admin/old-page"
    new = "https://learn.microsoft.com/en-us/power-platform/admin/environment-groups"
    sibling = new + "-rules"
    url_file = tmp_path / "docs" / "reference" / "microsoft-learn-urls.md"
    url_file.parent.mkdir(parents=True)
    url_file.write_text(f"| A | {old} | Mar 2026 |\n| B | {sibling} | Mar 2026 |\n", encoding="utf-8")
    diff = f"--- a/x\n+++ b/x\n@@ -1 +1 @@\n-| A | {old} | Mar 2026 |\n+| A | {new} | Mar 2026 |\n"
    monkeypatch.setattr(runner, "_git", _redirect_git_mock(diff))
    monkeypatch.setattr(runner, "_untracked_files", lambda config: [])
    monkeypatch.setattr(runner, "_reset_attempt", lambda config, base, baseline: None)
    monkeypatch.setattr(runner, "_push_and_create_pr", lambda config, ctx, body: "PR#9")
    monkeypatch.setattr(runner, "_record_ledger", lambda config, ctx, state, detail: None)

    cfg = runner.RunnerConfig(repo_path=tmp_path, draft_model="a", review_model="b")
    outcome = runner._process_redirect(cfg, _redirect_ctx(old, new))

    assert outcome.status == "pr_opened"
    content = url_file.read_text(encoding="utf-8")
    assert sibling in content  # sibling preserved
    assert f"| A | {new} |" in content  # old swapped to new


def test_process_redirect_parse_failure_escalates(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    escalations: list[str] = []
    monkeypatch.setattr(runner, "_escalate", lambda config, ctx, reason, details: escalations.append(reason) or "ISSUE#1")
    monkeypatch.setattr(runner, "_record_ledger", lambda config, ctx, state, detail: None)
    ctx = _redirect_ctx("https://old/", "https://new/")
    ctx.instructions = "no redirect evidence here"  # no 'redirects to <url>'
    cfg = runner.RunnerConfig(repo_path=tmp_path, draft_model="a", review_model="b")
    outcome = runner._process_redirect(cfg, ctx)
    assert outcome.status == "escalated"
    assert escalations == ["redirect_parse_failed"]


def test_process_redirect_embedded_space_target_escalates(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    # An embedded space in the redirect target must NOT be silently truncated to a valid-but-wrong
    # URL; the whole-line capture keeps it and validation rejects it before any file write.
    escalations: list[str] = []
    monkeypatch.setattr(runner, "_escalate", lambda config, ctx, reason, details: escalations.append(reason) or "ISSUE#1")
    monkeypatch.setattr(runner, "_record_ledger", lambda config, ctx, state, detail: None)
    monkeypatch.setattr(runner, "_git", lambda config, *args: pytest.fail("must escalate before touching git"))
    ctx = _redirect_ctx("https://learn.microsoft.com/a/old", "https://learn.microsoft.com/a/new")
    ctx.instructions = "## evidence\n```diff\nredirects to https://learn.microsoft.com/a/new page\n```\n"
    cfg = runner.RunnerConfig(repo_path=tmp_path, draft_model="a", review_model="b")
    outcome = runner._process_redirect(cfg, ctx)
    assert outcome.status == "escalated"
    assert escalations == ["redirect_malformed_url"]


def test_process_redirect_malformed_new_url_escalates(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    # A new_url containing a table-breaking '|' must be rejected before any file write.
    escalations: list[str] = []
    monkeypatch.setattr(runner, "_escalate", lambda config, ctx, reason, details: escalations.append(reason) or "ISSUE#1")
    monkeypatch.setattr(runner, "_record_ledger", lambda config, ctx, state, detail: None)
    monkeypatch.setattr(runner, "_git", lambda config, *args: pytest.fail("must escalate before touching git"))
    cfg = runner.RunnerConfig(repo_path=tmp_path, draft_model="a", review_model="b")
    outcome = runner._process_redirect(cfg, _redirect_ctx("https://learn.microsoft.com/a/foo", "https://learn.microsoft.com/a/bar|frag"))
    assert outcome.status == "escalated"
    assert escalations == ["redirect_malformed_url"]


@pytest.mark.parametrize(
    "bad_new_url",
    [
        "https://evil.example/x",                       # plainly off-domain
        "https://learn.microsoft.com.evil.com/x",       # subdomain spoof (host is *.evil.com)
        "https://learn.microsoft.com@evil.example/x",   # embedded-credentials host trick (host is evil.example)
        "https://amicrosoft.com/x",                     # no dot boundary before microsoft.com
        "http://127.0.0.1/x",                           # raw IP literal
        "https:///x",                                   # empty/malformed host
        "https://[::1/x",                               # malformed bracketed IPv6 (urlparse ValueError)
    ],
)
def test_process_redirect_off_domain_target_escalates(bad_new_url: str, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    # A redirect whose NEW target host is not a Microsoft domain must fail closed: escalate with
    # `redirect_off_domain` and never touch git / draft the swap. Removing the allowlist check in
    # _process_redirect makes every case here proceed past validation and break this test.
    escalations: list[str] = []
    monkeypatch.setattr(runner, "_escalate", lambda config, ctx, reason, details: escalations.append(reason) or "ISSUE#1")
    monkeypatch.setattr(runner, "_record_ledger", lambda config, ctx, state, detail: None)
    monkeypatch.setattr(runner, "_git", lambda config, *args: pytest.fail("must escalate before touching git"))
    cfg = runner.RunnerConfig(repo_path=tmp_path, draft_model="a", review_model="b")
    outcome = runner._process_redirect(cfg, _redirect_ctx("https://learn.microsoft.com/a/old", bad_new_url))
    assert outcome.status == "escalated"
    assert escalations == ["redirect_off_domain"]


@pytest.mark.parametrize(
    "good_new_url",
    [
        "https://learn.microsoft.com/en-us/agents/architecture/",
        "https://go.microsoft.com/fwlink/?linkid=2222",
        "https://docs.microsoft.com/en-us/azure/",       # ends with .microsoft.com
        "https://microsoft.com/x",                       # apex
    ],
)
def test_process_redirect_microsoft_domain_target_proceeds(good_new_url: str, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    # A legitimate Microsoft-domain redirect target must NOT be blocked by the allowlist: the swap
    # proceeds and a PR is opened.
    old = "https://learn.microsoft.com/old/"
    url_file = tmp_path / "docs" / "reference" / "microsoft-learn-urls.md"
    url_file.parent.mkdir(parents=True)
    url_file.write_text(f"| Architecting | {old} | Mar 2026 |\n", encoding="utf-8")
    diff = f"--- a/x\n+++ b/x\n@@ -1 +1 @@\n-| Architecting | {old} | Mar 2026 |\n+| Architecting | {good_new_url} | Mar 2026 |\n"
    monkeypatch.setattr(runner, "_git", _redirect_git_mock(diff))
    monkeypatch.setattr(runner, "_untracked_files", lambda config: [])
    monkeypatch.setattr(runner, "_reset_attempt", lambda config, base, baseline: None)
    monkeypatch.setattr(runner, "_push_and_create_pr", lambda config, ctx, body: "PR#9")
    monkeypatch.setattr(runner, "_record_ledger", lambda config, ctx, state, detail: None)
    cfg = runner.RunnerConfig(repo_path=tmp_path, draft_model="a", review_model="b")
    outcome = runner._process_redirect(cfg, _redirect_ctx(old, good_new_url))
    assert outcome.status == "pr_opened"
    assert good_new_url in url_file.read_text(encoding="utf-8")


def test_redirect_host_allowed_rule() -> None:
    # Direct unit coverage of the fail-closed allowlist boundary.
    assert runner._redirect_host_allowed("https://learn.microsoft.com/x")
    assert runner._redirect_host_allowed("https://microsoft.com/x")
    assert runner._redirect_host_allowed("https://go.microsoft.com/x")
    assert runner._redirect_host_allowed("https://docs.microsoft.com/x")
    assert not runner._redirect_host_allowed("https://evil.example/x")
    assert not runner._redirect_host_allowed("https://learn.microsoft.com.evil.com/x")
    assert not runner._redirect_host_allowed("https://learn.microsoft.com@evil.example/x")
    assert not runner._redirect_host_allowed("https://amicrosoft.com/x")
    assert not runner._redirect_host_allowed("https:///x")
    assert not runner._redirect_host_allowed("https://[::1/x")


def test_process_change_dispatches_redirect(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    called: list[str] = []
    monkeypatch.setattr(runner, "_process_redirect", lambda config, ctx: called.append(ctx.fingerprint) or runner.Outcome(ctx.fingerprint, "pr_opened", "redir"))
    monkeypatch.setattr(runner, "_run_draft", lambda config, ctx, feedback: pytest.fail("redirects must not hit the LLM draft path"))
    outcome = runner.process_change(_config(tmp_path), _redirect_ctx("https://old/", "https://new/"))
    assert outcome.status == "pr_opened"
    assert called == ["sha256:redir01"]


def test_process_redirect_prefix_sibling_not_corrupted(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    # The real URL list has prefix pairs (e.g. environment-groups vs environment-groups-rules).
    # A redirect of the shorter URL must NOT corrupt the longer sibling.
    base = "https://learn.microsoft.com/en-us/power-platform/admin/environment-groups"
    sibling = base + "-rules"
    new = "https://learn.microsoft.com/en-us/power-platform/admin/environments-overview"
    url_file = tmp_path / "docs" / "reference" / "microsoft-learn-urls.md"
    url_file.parent.mkdir(parents=True)
    url_file.write_text(f"| EG | {base} | Mar 2026 |\n| EGR | {sibling} | Mar 2026 |\n", encoding="utf-8")
    diff = f"--- a/x\n+++ b/x\n@@ -1 +1 @@\n-| EG | {base} | Mar 2026 |\n+| EG | {new} | Mar 2026 |\n"
    monkeypatch.setattr(runner, "_git", _redirect_git_mock(diff))
    monkeypatch.setattr(runner, "_untracked_files", lambda config: [])
    monkeypatch.setattr(runner, "_reset_attempt", lambda config, base_, baseline: None)
    monkeypatch.setattr(runner, "_push_and_create_pr", lambda config, ctx, body: "PR#9")
    monkeypatch.setattr(runner, "_record_ledger", lambda config, ctx, state, detail: None)

    cfg = runner.RunnerConfig(repo_path=tmp_path, draft_model="a", review_model="b")
    outcome = runner._process_redirect(cfg, _redirect_ctx(base, new))

    assert outcome.status == "pr_opened"
    content = url_file.read_text(encoding="utf-8")
    assert sibling in content  # longer sibling URL is NOT corrupted
    assert f"| EG | {new} |" in content  # the exact URL was swapped
    assert f"| EG | {base} |" not in content


def test_read_allowed_files_inlines_small_skips_large_and_missing(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "small.md").write_text("small content", encoding="utf-8")
    (tmp_path / "docs" / "big.md").write_text("x" * (runner.MAX_INLINE_FILE_CHARS + 1), encoding="utf-8")
    ctx = runner.ChangeContext(
        fingerprint="sha256:f",
        route="autodraft",
        contract={"allowed_files": ["docs/small.md", "docs/big.md", "docs/new.md"]},
        report_path="reports/monitoring/learn-changes-x.md",
        instructions="",
        title="t",
        labels=[],
    )
    contents = runner._read_allowed_files(runner.RunnerConfig(repo_path=tmp_path, draft_model="a", review_model="b"), ctx)
    assert contents["docs/small.md"] == "small content"
    assert contents["docs/big.md"] is None  # too large to inline
    assert contents["docs/new.md"] is None  # does not exist yet


def test_build_draft_prompt_inlines_content_and_forbids_exploration() -> None:
    ctx = _ctx()
    ctx.instructions = "EVIDENCE: redirect to https://new"
    prompt = runner._build_draft_prompt(ctx, "", {"docs/x.md": "# Heading\nold url"})
    assert "Current content of `docs/x.md`" in prompt
    assert "old url" in prompt
    assert "Do NOT read, search, list, or open any OTHER files" in prompt
    assert "EVIDENCE: redirect to https://new" in prompt  # the issue body/evidence is included


def test_build_draft_prompt_notes_non_inlined_files() -> None:
    prompt = runner._build_draft_prompt(_ctx(), "", {"docs/huge.md": None})
    assert "Open this file directly" in prompt


def test_build_draft_prompt_includes_feedback_on_retry() -> None:
    prompt = runner._build_draft_prompt(_ctx(), "Unsupported claim: bad date", {"docs/x.md": "content"})
    assert "previous attempt was rejected" in prompt
    assert "Unsupported claim: bad date" in prompt


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
    """Neutralize git/worktree and capture PR/escalate/ledger calls."""

    calls: dict[str, list[Any]] = {"pr": [], "escalate": [], "ledger": [], "git": [], "worktree": []}
    monkeypatch.setattr(runner, "_git", lambda config, *args: calls["git"].append(args) or "")
    monkeypatch.setattr(runner, "_untracked_files", lambda config: [])
    monkeypatch.setattr(runner, "_reset_attempt", lambda config, base, new_untracked: calls["git"].append(("reset_attempt", tuple(new_untracked))))
    monkeypatch.setattr(runner, "_create_worktree", lambda config: calls["worktree"].append("create") or config.repo_path)
    monkeypatch.setattr(runner, "_remove_worktree", lambda config, work_path: calls["worktree"].append("remove"))
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

    # finally-block detaches at base (it runs inside a linked worktree, where checking out the
    # base BRANCH would fail because it is already checked out in the primary worktree).
    assert ("checkout", "--force", "--detach", "main") in patched["git"]


def test_process_change_draft_exception_triggers_cleanup(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, patched: dict[str, list[Any]]) -> None:
    def boom(config: Any, ctx: Any, feedback: str) -> runner.DraftResult:
        raise RuntimeError("drafter timed out mid-write")

    monkeypatch.setattr(runner, "_run_draft", boom)

    with pytest.raises(RuntimeError):
        runner.process_change(_config(tmp_path), _ctx())

    # Even on a draft exception, the finally block cleans the attempt and detaches at base.
    assert any(isinstance(c, tuple) and c and c[0] == "reset_attempt" for c in patched["git"])
    assert ("checkout", "--force", "--detach", "main") in patched["git"]

# --- feedback text ---------------------------------------------------------------


def test_feedback_text_lists_claims() -> None:
    text = runner._feedback_text("pass", {"verdict": "fail", "unsupported_claims": ["Fabricated date"], "overbroad_edits": ["Too broad"], "notes": "n"})
    assert "Fabricated date" in text
    assert "Too broad" in text
    assert "Independent review: fail" in text


def test_content_pr_body_describes_oceansquad_merge_and_final_escalation(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(runner, "_git", lambda config, *args: "")
    captured: list[str] = []
    monkeypatch.setattr(
        runner,
        "_push_and_create_pr",
        lambda config, ctx, body: captured.append(body) or "https://github.com/o/r/pull/1",
    )
    runner._open_pr(_config(tmp_path), _ctx(), _draft(), {"verdict": "pass", "confidence": 0.95})
    assert "OceanSquad reviews and SHA-pinned merges" in captured[0]
    assert "only if automation exhausts" in captured[0]
    assert "human merge required" not in captured[0].lower()


# --- run() guard + routing -------------------------------------------------------


def test_assert_canary_cross_model_hook_is_disabled_by_default(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.delenv("AUTODOC_CANARY_CROSS_MODEL_ENABLED", raising=False)
    monkeypatch.setattr(
        runner.autodoc_canary,
        "make_cross_model_verifier",
        lambda **_kwargs: pytest.fail("must not activate cross-model canary by default"),
    )
    monkeypatch.setattr(
        runner.autodoc_canary,
        "run_canary",
        lambda hook=None: [("safe", True, None)] if hook is None else pytest.fail("unexpected hook"),
    )
    runner._assert_canary(_config(tmp_path))


def test_assert_canary_wires_explicit_cross_model_hook(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setenv("AUTODOC_CANARY_CROSS_MODEL_ENABLED", "true")
    verifier = object()
    monkeypatch.setattr(
        runner.autodoc_canary,
        "make_cross_model_verifier",
        lambda **kwargs: verifier if kwargs["model"] == "model-b" else None,
    )
    monkeypatch.setattr(
        runner.autodoc_canary,
        "run_canary",
        lambda hook=None: [("safe", hook is verifier, None)],
    )
    runner._assert_canary(_config(tmp_path))


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
    monkeypatch.setattr(runner.autodoc_route, "route_report", lambda text, name, ledger, **_kw: [spec])

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
    monkeypatch.setattr(runner.autodoc_route, "route_report", lambda text, name, ledger, **_kw: [spec])
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
    monkeypatch.setattr(runner.autodoc_route, "route_report", lambda text, name, ledger, **_kw: [spec])

    def boom(config: Any, ctx: Any, feedback: str) -> runner.DraftResult:
        raise RuntimeError("git exploded")

    monkeypatch.setattr(runner, "_run_draft", boom)

    result = runner.run(_config(tmp_path))

    assert result["outcomes"][0]["status"] == "error"
    assert "processing_error" in result["outcomes"][0]["detail"]


class _FakeCompleted:
    def __init__(self, returncode: int, stdout: str = "", stderr: str = "") -> None:
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def test_push_and_create_pr_raises_on_gh_failure(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(runner, "_git", lambda config, *args: "")
    monkeypatch.setattr(runner, "_existing_pr_url", lambda config, ctx: None)
    monkeypatch.setattr(runner.subprocess, "run", lambda *a, **k: _FakeCompleted(1, stderr="boom"))
    with pytest.raises(RuntimeError, match="gh pr create failed"):
        runner._push_and_create_pr(_config(tmp_path), _ctx(), "body")


def test_push_and_create_pr_returns_existing_pr_on_conflict(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(runner, "_git", lambda config, *args: "")
    monkeypatch.setattr(runner.subprocess, "run", lambda *a, **k: _FakeCompleted(1, stderr="already exists"))
    monkeypatch.setattr(runner, "_existing_pr_url", lambda config, ctx: "https://github.com/x/y/pull/9")
    # gh pr create failed, but a PR already exists for this head → return it, do not raise.
    assert runner._push_and_create_pr(_config(tmp_path), _ctx(), "body") == "https://github.com/x/y/pull/9"


def test_push_and_create_pr_deletes_orphan_branch_on_failure(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(runner, "_git", lambda config, *args: "")
    monkeypatch.setattr(runner, "_existing_pr_url", lambda config, ctx: None)
    runs: list[tuple[Any, ...]] = []

    def fake_run(args: Any, **kwargs: Any) -> "_FakeCompleted":
        runs.append(tuple(args))
        return _FakeCompleted(1, stderr="boom")

    monkeypatch.setattr(runner.subprocess, "run", fake_run)
    with pytest.raises(RuntimeError, match="gh pr create failed"):
        runner._push_and_create_pr(_config(tmp_path), _ctx(), "body")
    # The orphaned remote branch must be deleted before raising.
    assert any("--delete" in r for r in runs)


def test_escalate_raises_on_gh_failure(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(runner, "_existing_issue_url", lambda config, ctx: None)
    monkeypatch.setattr(runner.subprocess, "run", lambda *a, **k: _FakeCompleted(1, stderr="boom"))
    with pytest.raises(RuntimeError, match="gh issue create failed"):
        runner._escalate(_config(tmp_path), _ctx(), "reason", "details")


def test_escalate_reuses_existing_issue(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(runner, "_existing_issue_url", lambda config, ctx: "https://github.com/x/y/issues/3")

    def explode(*a: Any, **k: Any) -> "_FakeCompleted":
        raise AssertionError("must not create a new issue when one already exists")

    monkeypatch.setattr(runner.subprocess, "run", explode)
    assert runner._escalate(_config(tmp_path), _ctx(), "reason", "details") == "https://github.com/x/y/issues/3"


def test_existing_issue_url_reuses_same_fingerprint_from_open_snapshot(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    fingerprint = "sha256:deadbeefcafe0001"
    payload = [
        {
            "number": 33,
            "url": "https://github.com/x/y/issues/33",
            "state": "OPEN",
            "stateReason": None,
            "body": (
                f"AUTODOC-FINGERPRINT: {fingerprint}\n"
                "Source: https://learn.microsoft.com/en-us/example\n"
                "Content-Hash: sha256:abc\n"
            ),
        }
    ]
    monkeypatch.setattr(runner.subprocess, "run", lambda *a, **k: _FakeCompleted(0, stdout=json.dumps(payload)))
    assert runner._existing_issue_url(_config(tmp_path), _ctx()) == "https://github.com/x/y/issues/33"


def _redirect_escalation_ctx(
    *,
    fingerprint: str = "sha256:redirect-current",
    source: str = "https://learn.microsoft.com/en-us/old",
    destination: str = "https://learn.microsoft.com/en-us/new",
) -> runner.ChangeContext:
    return runner.ChangeContext(
        fingerprint=fingerprint,
        route="autodraft",
        contract={
            "fingerprint": fingerprint,
            "classification": "REDIRECT",
            "source_url": source,
            "destination_url": destination,
            "allowed_files": ["docs/reference/microsoft-learn-urls.md"],
        },
        report_path="reports/monitoring/learn-changes-x.md",
        instructions=f"## Learn change evidence\n```diff\nredirects to {destination}\n```\n",
        title=f"Autodoc draft: URL redirect: {source}",
        labels=["autodoc"],
    )


_IDENTITY_SOURCE = "https://learn.microsoft.com/en-us/old"
_IDENTITY_DESTINATION = "https://learn.microsoft.com/en-us/new"
_IDENTITY_OTHER_DESTINATION = "https://learn.microsoft.com/en-us/other-new"
_IDENTITY_CONTENT_HASH = "sha256:content-for-source"


def _json_contract_body(**overrides: str) -> str:
    contract = {
        "fingerprint": "sha256:older",
        "source_url": _IDENTITY_SOURCE,
        "destination_url": _IDENTITY_DESTINATION,
        "content_hash": _IDENTITY_CONTENT_HASH,
    }
    contract.update(overrides)
    return "```json\n" + json.dumps(contract, sort_keys=True) + "\n```\n"


_CONFLICTING_IDENTITY_BODIES = [
    pytest.param(
        _json_contract_body()
        + _json_contract_body(destination_url=_IDENTITY_OTHER_DESTINATION),
        id="two-json-contracts-conflicting-destinations",
    ),
    pytest.param(
        (
            "AUTODOC-FINGERPRINT: sha256:older\n"
            f"Source: {_IDENTITY_SOURCE}\n"
            f"Destination: {_IDENTITY_DESTINATION}\n"
            f"Content-Hash: {_IDENTITY_CONTENT_HASH}\n"
            + _json_contract_body(destination_url=_IDENTITY_OTHER_DESTINATION)
        ),
        id="plaintext-destination-disagrees-json",
    ),
    pytest.param(
        (
            "AUTODOC-FINGERPRINT: sha256:older\n"
            "AUTODOC-FINGERPRINT: sha256:different\n"
            f"Source: {_IDENTITY_SOURCE}\n"
            f"Destination: {_IDENTITY_DESTINATION}\n"
            f"Content-Hash: {_IDENTITY_CONTENT_HASH}\n"
        ),
        id="conflicting-plaintext-fingerprints",
    ),
    pytest.param(
        _json_contract_body(fingerprint="sha256:older")
        + _json_contract_body(fingerprint="sha256:different"),
        id="conflicting-json-fingerprints",
    ),
    pytest.param(
        (
            "AUTODOC-FINGERPRINT: sha256:content-first\n"
            "AUTODOC-FINGERPRINT: sha256:content-second\n"
            f"Source: {_IDENTITY_SOURCE}\n"
            f"Destination: {_IDENTITY_DESTINATION}\n"
            f"Content-Hash: {_IDENTITY_CONTENT_HASH}\n"
        ),
        id="content-body-conflicting-fingerprints",
    ),
]


@pytest.mark.parametrize("body", _CONFLICTING_IDENTITY_BODIES)
def test_existing_issue_url_rejects_conflicting_identity_representations(
    body: str,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    payload = [
        {
            "number": 48,
            "url": "https://github.com/x/y/issues/48",
            "state": "OPEN",
            "stateReason": None,
            "body": body,
        }
    ]
    monkeypatch.setattr(runner.subprocess, "run", lambda *a, **k: _FakeCompleted(0, stdout=json.dumps(payload)))

    assert (
        runner._existing_issue_url(
            _config(tmp_path),
            _redirect_escalation_ctx(source=_IDENTITY_SOURCE, destination=_IDENTITY_DESTINATION),
        )
        is None
    )


@pytest.mark.parametrize("body", _CONFLICTING_IDENTITY_BODIES)
def test_content_supersession_rejects_conflicting_identity_representations(
    body: str,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    issue = runner.autodoc_issue_identity.parse_issue_record(
        {
            "number": 48,
            "url": "https://github.com/x/y/issues/48",
            "state": "OPEN",
            "stateReason": None,
            "body": body,
        }
    )
    monkeypatch.setattr(runner, "_list_open_autodoc_issues", lambda config: [issue])
    close_calls: list[list[str]] = []

    def fake_run(args: Any, **kwargs: Any) -> "_FakeCompleted":
        close_calls.append(list(args))
        return _FakeCompleted(0, stdout="closed")

    monkeypatch.setattr(runner.subprocess, "run", fake_run)

    runner._close_source_siblings_not_planned(
        config=_config(tmp_path),
        source_url=_IDENTITY_SOURCE,
        fingerprint="sha256:active-content",
        superseding_issue_url="https://github.com/x/y/issues/101",
    )

    assert close_calls == []


def test_existing_issue_url_reuses_stable_no_destination_redirect_identity(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    payload = [
        {
            "number": 49,
            "url": "https://github.com/x/y/issues/49",
            "state": "OPEN",
            "stateReason": None,
            "body": (
                "AUTODOC-FINGERPRINT: sha256:older-none\n"
                f"Source: {_IDENTITY_SOURCE}\n"
                "Destination: autodoc:none\n"
            ),
        }
    ]
    monkeypatch.setattr(runner.subprocess, "run", lambda *a, **k: _FakeCompleted(0, stdout=json.dumps(payload)))

    assert (
        runner._existing_issue_url(
            _config(tmp_path),
            _redirect_escalation_ctx(source=_IDENTITY_SOURCE, destination=""),
        )
        == "https://github.com/x/y/issues/49"
    )


def test_no_destination_redirect_supersession_closes_same_identity_sibling(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    issue = runner.autodoc_issue_identity.parse_issue_record(
        {
            "number": 49,
            "url": "https://github.com/x/y/issues/49",
            "state": "OPEN",
            "stateReason": None,
            "body": (
                "AUTODOC-FINGERPRINT: sha256:older-none\n"
                f"Source: {_IDENTITY_SOURCE}\n"
                "Destination: autodoc:none\n"
            ),
        }
    )
    monkeypatch.setattr(runner, "_list_open_autodoc_issues", lambda config: [issue])
    close_calls: list[list[str]] = []

    def fake_run(args: Any, **kwargs: Any) -> "_FakeCompleted":
        close_calls.append(list(args))
        return _FakeCompleted(0, stdout="closed")

    monkeypatch.setattr(runner.subprocess, "run", fake_run)

    runner._close_source_siblings_not_planned(
        config=_config(tmp_path),
        source_url=_IDENTITY_SOURCE,
        fingerprint="sha256:active-none",
        superseding_issue_url="https://github.com/x/y/issues/101",
        redirect_identity=(_IDENTITY_SOURCE, runner.autodoc_endpoint_identity.NO_DESTINATION),
    )

    close_call = next(command for command in close_calls if command[:3] == ["gh", "issue", "close"])
    assert "49" in close_call


def test_existing_issue_url_reuses_open_redirect_with_same_endpoint_not_fingerprint(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    payload = [
        {
            "number": 44,
            "url": "https://github.com/x/y/issues/44",
            "state": "OPEN",
            "stateReason": None,
            "body": (
                "AUTODOC-FINGERPRINT: sha256:older-run-specific\n"
                "Reason: redirect_ambiguous\n"
                "Source: https://learn.microsoft.com/en-us/old?msockid=tracked\n"
                "Destination: https://learn.microsoft.com/en-us/new?utm_source=monitor\n"
            ),
        }
    ]
    monkeypatch.setattr(runner.subprocess, "run", lambda *a, **k: _FakeCompleted(0, stdout=json.dumps(payload)))

    assert (
        runner._existing_issue_url(_config(tmp_path), _redirect_escalation_ctx())
        == "https://github.com/x/y/issues/44"
    )


def test_existing_issue_url_reuses_redirect_when_only_reason_changed(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    payload = [
        {
            "number": 45,
            "url": "https://github.com/x/y/issues/45",
            "state": "OPEN",
            "stateReason": None,
            "body": (
                "AUTODOC-FINGERPRINT: sha256:redirect-url-not-found-run\n"
                "Reason: redirect_url_not_found\n"
                "Source: https://learn.microsoft.com/en-us/old\n"
                "Destination: https://learn.microsoft.com/en-us/new\n"
            ),
        }
    ]
    monkeypatch.setattr(runner.subprocess, "run", lambda *a, **k: _FakeCompleted(0, stdout=json.dumps(payload)))

    assert (
        runner._existing_issue_url(
            _config(tmp_path),
            _redirect_escalation_ctx(fingerprint="sha256:redirect-ambiguous-later-run"),
        )
        == "https://github.com/x/y/issues/45"
    )


def test_existing_issue_url_does_not_reuse_destinationless_redirect_even_with_same_fingerprint(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    fingerprint = "sha256:redirect-current"
    payload = [
        {
            "number": 46,
            "url": "https://github.com/x/y/issues/46",
            "state": "OPEN",
            "stateReason": None,
            "body": (
                f"AUTODOC-FINGERPRINT: {fingerprint}\n"
                "Reason: redirect_ambiguous\n"
                "Source: https://learn.microsoft.com/en-us/old\n"
            ),
        }
    ]
    monkeypatch.setattr(runner.subprocess, "run", lambda *a, **k: _FakeCompleted(0, stdout=json.dumps(payload)))

    assert runner._existing_issue_url(_config(tmp_path), _redirect_escalation_ctx(fingerprint=fingerprint)) is None


def test_existing_issue_url_keeps_non_redirect_fingerprint_reuse_unchanged(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    fingerprint = "sha256:deadbeefcafe0001"
    payload = [
        {
            "number": 47,
            "url": "https://github.com/x/y/issues/47",
            "state": "OPEN",
            "stateReason": None,
            "body": (
                f"AUTODOC-FINGERPRINT: {fingerprint}\n"
                "Source: https://learn.microsoft.com/en-us/content\n"
                "Content-Hash: sha256:content\n"
            ),
        }
    ]
    monkeypatch.setattr(runner.subprocess, "run", lambda *a, **k: _FakeCompleted(0, stdout=json.dumps(payload)))

    assert runner._existing_issue_url(_config(tmp_path), _ctx()) == "https://github.com/x/y/issues/47"


def test_escalate_destination_change_creates_parseable_redirect_issue_without_superseding_different_endpoint(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    old_payload = [
        {
            "number": 77,
            "url": "https://github.com/x/y/issues/77",
            "state": "OPEN",
            "stateReason": None,
            "body": (
                "AUTODOC-FINGERPRINT: sha256:older-destination\n"
                "Reason: redirect_ambiguous\n"
                "Source: https://learn.microsoft.com/en-us/old\n"
                "Destination: https://learn.microsoft.com/en-us/old-destination\n"
            ),
        }
    ]
    calls: list[list[str]] = []

    def fake_run(args: Any, **kwargs: Any) -> "_FakeCompleted":
        calls.append(list(args))
        if args[:3] == ["gh", "issue", "list"]:
            return _FakeCompleted(0, stdout=json.dumps(old_payload))
        if args[:3] == ["gh", "issue", "create"]:
            return _FakeCompleted(0, stdout="https://github.com/x/y/issues/101")
        if args[:3] == ["gh", "issue", "close"]:
            return _FakeCompleted(0, stdout="closed")
        raise AssertionError(f"unexpected command: {args}")

    monkeypatch.setattr(runner.subprocess, "run", fake_run)

    result = runner._escalate(
        _config(tmp_path),
        _redirect_escalation_ctx(destination="https://learn.microsoft.com/en-us/new-destination"),
        "redirect_ambiguous",
        "canonical destination URL already exists; needs human review",
    )

    assert result == "https://github.com/x/y/issues/101"
    create_call = next(command for command in calls if command[:3] == ["gh", "issue", "create"])
    body = create_call[create_call.index("--body") + 1]
    assert "Destination: https://learn.microsoft.com/en-us/new-destination" in body
    assert not any(command[:3] == ["gh", "issue", "close"] for command in calls)


def test_redirect_escalation_does_not_close_destinationless_legacy_sibling(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    old_payload = [
        {
            "number": 77,
            "url": "https://github.com/x/y/issues/77",
            "state": "OPEN",
            "stateReason": None,
            "body": (
                "AUTODOC-FINGERPRINT: sha256:older-destinationless\n"
                "Reason: redirect_ambiguous\n"
                "Source: https://learn.microsoft.com/en-us/old\n"
            ),
        }
    ]
    calls: list[list[str]] = []

    def fake_run(args: Any, **kwargs: Any) -> "_FakeCompleted":
        calls.append(list(args))
        if args[:3] == ["gh", "issue", "list"]:
            return _FakeCompleted(0, stdout=json.dumps(old_payload))
        if args[:3] == ["gh", "issue", "create"]:
            return _FakeCompleted(0, stdout="https://github.com/x/y/issues/101")
        if args[:3] == ["gh", "issue", "close"]:
            return _FakeCompleted(0, stdout="closed")
        raise AssertionError(f"unexpected command: {args}")

    monkeypatch.setattr(runner.subprocess, "run", fake_run)

    result = runner._escalate(
        _config(tmp_path),
        _redirect_escalation_ctx(destination="https://learn.microsoft.com/en-us/new-destination"),
        "redirect_ambiguous",
        "canonical destination URL already exists; needs human review",
    )

    assert result == "https://github.com/x/y/issues/101"
    assert not any(command[:3] == ["gh", "issue", "close"] for command in calls)


def test_redirect_escalation_without_destination_stamps_stable_none_identity(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(runner, "_list_open_autodoc_issues", lambda config: [])
    calls: list[list[str]] = []

    def fake_run(args: Any, **kwargs: Any) -> "_FakeCompleted":
        calls.append(list(args))
        if args[:3] == ["gh", "issue", "create"]:
            return _FakeCompleted(0, stdout="https://github.com/x/y/issues/101")
        raise AssertionError(f"unexpected command: {args}")

    monkeypatch.setattr(runner.subprocess, "run", fake_run)
    ctx = _redirect_escalation_ctx(destination="")

    result = runner._escalate(_config(tmp_path), ctx, "redirect_parse_failed", "could not resolve a URL swap")

    assert result == "https://github.com/x/y/issues/101"
    create_call = next(command for command in calls if command[:3] == ["gh", "issue", "create"])
    body = create_call[create_call.index("--body") + 1]
    assert "Destination: autodoc:none" in body


def test_escalate_closes_exact_source_sibling_with_audit_comment(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    source = "https://learn.microsoft.com/en-us/power-platform/admin/example"
    created_issue = "https://github.com/x/y/issues/101"
    sibling = runner.autodoc_issue_identity.IssueRecord(
        number=77,
        url="https://github.com/x/y/issues/77",
        state="OPEN",
        state_reason="",
        fingerprint="sha256:older",
        source_url=source,
        content_hash="sha256:older-hash",
        source_kind="source_line",
    )
    monkeypatch.setattr(runner, "_existing_issue_url", lambda config, ctx: None)
    monkeypatch.setattr(runner, "_list_open_autodoc_issues", lambda config: [sibling])

    calls: list[list[str]] = []

    def fake_run(args: Any, **kwargs: Any) -> "_FakeCompleted":
        calls.append(list(args))
        if args[:3] == ["gh", "issue", "create"]:
            return _FakeCompleted(0, stdout=created_issue)
        if args[:3] == ["gh", "issue", "close"]:
            return _FakeCompleted(0, stdout="closed")
        raise AssertionError(f"unexpected command: {args}")

    monkeypatch.setattr(runner.subprocess, "run", fake_run)
    ctx = runner.ChangeContext(
        fingerprint="sha256:newer",
        route="human",
        contract={"fingerprint": "sha256:newer", "source_url": source, "content_hash": "sha256:new-hash"},
        report_path="reports/monitoring/learn-changes-x.md",
        instructions="",
        title="Autodoc human review: Example",
        labels=["autodoc", "escalate"],
    )

    result = runner._escalate(_config(tmp_path), ctx, "route=human", "details")

    assert result == created_issue
    close_call = next(command for command in calls if command[:3] == ["gh", "issue", "close"])
    assert "77" in close_call
    assert "--reason" in close_call and "not planned" in close_call
    comment = close_call[close_call.index("--comment") + 1]
    assert created_issue in comment
    assert source in comment
    assert "sha256:newer" in comment


def test_content_escalation_does_not_close_source_only_legacy_issue(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    source = "https://learn.microsoft.com/en-us/power-platform/admin/example"
    sibling = runner.autodoc_issue_identity.IssueRecord(
        number=77,
        url="https://github.com/x/y/issues/77",
        state="OPEN",
        state_reason="",
        fingerprint="sha256:older",
        source_url=source,
        content_hash=None,
        source_kind="source_line",
    )
    monkeypatch.setattr(runner, "_existing_issue_url", lambda config, ctx: None)
    monkeypatch.setattr(runner, "_list_open_autodoc_issues", lambda config: [sibling])

    calls: list[list[str]] = []

    def fake_run(args: Any, **kwargs: Any) -> "_FakeCompleted":
        calls.append(list(args))
        if args[:3] == ["gh", "issue", "create"]:
            return _FakeCompleted(0, stdout="https://github.com/x/y/issues/101")
        if args[:3] == ["gh", "issue", "close"]:
            return _FakeCompleted(0, stdout="closed")
        raise AssertionError(f"unexpected command: {args}")

    monkeypatch.setattr(runner.subprocess, "run", fake_run)
    ctx = runner.ChangeContext(
        fingerprint="sha256:newer",
        route="human",
        contract={"fingerprint": "sha256:newer", "source_url": source, "content_hash": "sha256:new-hash"},
        report_path="reports/monitoring/learn-changes-x.md",
        instructions="",
        title="Autodoc human review: Example",
        labels=["autodoc", "escalate"],
    )

    assert runner._escalate(_config(tmp_path), ctx, "route=human", "details") == "https://github.com/x/y/issues/101"
    assert not any(command[:3] == ["gh", "issue", "close"] for command in calls)


def test_escalate_lookalike_source_does_not_close(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    source = "https://learn.microsoft.com/en-us/power-platform/admin/example"
    lookalike = f"{source}-archive"
    sibling = runner.autodoc_issue_identity.IssueRecord(
        number=78,
        url="https://github.com/x/y/issues/78",
        state="OPEN",
        state_reason="",
        fingerprint="sha256:older",
        source_url=lookalike,
        content_hash="sha256:older-hash",
        source_kind="source_line",
    )
    monkeypatch.setattr(runner, "_existing_issue_url", lambda config, ctx: None)
    monkeypatch.setattr(runner, "_list_open_autodoc_issues", lambda config: [sibling])

    calls: list[list[str]] = []

    def fake_run(args: Any, **kwargs: Any) -> "_FakeCompleted":
        calls.append(list(args))
        if args[:3] == ["gh", "issue", "create"]:
            return _FakeCompleted(0, stdout="https://github.com/x/y/issues/102")
        if args[:3] == ["gh", "issue", "close"]:
            return _FakeCompleted(0, stdout="closed")
        raise AssertionError(f"unexpected command: {args}")

    monkeypatch.setattr(runner.subprocess, "run", fake_run)
    ctx = runner.ChangeContext(
        fingerprint="sha256:newer",
        route="human",
        contract={"fingerprint": "sha256:newer", "source_url": source, "content_hash": "sha256:new-hash"},
        report_path="reports/monitoring/learn-changes-x.md",
        instructions="",
        title="Autodoc human review: Example",
        labels=["autodoc", "escalate"],
    )
    runner._escalate(_config(tmp_path), ctx, "route=human", "details")

    assert not any(command[:3] == ["gh", "issue", "close"] for command in calls)


def test_escalate_create_succeeds_even_when_sibling_close_fails(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    source = "https://learn.microsoft.com/en-us/power-platform/admin/example"
    sibling = runner.autodoc_issue_identity.IssueRecord(
        number=79,
        url="https://github.com/x/y/issues/79",
        state="OPEN",
        state_reason="",
        fingerprint="sha256:older",
        source_url=source,
        content_hash="sha256:older-hash",
        source_kind="source_line",
    )
    monkeypatch.setattr(runner, "_existing_issue_url", lambda config, ctx: None)
    monkeypatch.setattr(runner, "_list_open_autodoc_issues", lambda config: [sibling])

    def fake_run(args: Any, **kwargs: Any) -> "_FakeCompleted":
        if args[:3] == ["gh", "issue", "create"]:
            return _FakeCompleted(0, stdout="https://github.com/x/y/issues/103")
        if args[:3] == ["gh", "issue", "close"]:
            return _FakeCompleted(1, stderr="close failed")
        raise AssertionError(f"unexpected command: {args}")

    monkeypatch.setattr(runner.subprocess, "run", fake_run)
    ctx = runner.ChangeContext(
        fingerprint="sha256:newer",
        route="human",
        contract={"fingerprint": "sha256:newer", "source_url": source, "content_hash": "sha256:new-hash"},
        report_path="reports/monitoring/learn-changes-x.md",
        instructions="",
        title="Autodoc human review: Example",
        labels=["autodoc", "escalate"],
    )

    assert runner._escalate(_config(tmp_path), ctx, "route=human", "details") == "https://github.com/x/y/issues/103"


def test_escalate_body_includes_source_url(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    # The escalation body must carry the exact Source URL so advance/consolidation can do
    # exact-source matching from structured body fields instead of tokenized substring search.
    monkeypatch.setattr(runner, "_existing_issue_url", lambda config, ctx: None)
    monkeypatch.setattr(runner, "_list_open_autodoc_issues", lambda config: [])
    captured: list[list[str]] = []

    def fake_run(args: Any, **kwargs: Any) -> "_FakeCompleted":
        captured.append(list(args))
        return _FakeCompleted(0, stdout="https://github.com/x/y/issues/7")

    monkeypatch.setattr(runner.subprocess, "run", fake_run)
    url = "https://learn.microsoft.com/en-us/power-platform/admin/business-continuity-disaster-recovery"
    ctx = runner.ChangeContext(
        fingerprint="sha256:deadbeefcafe0002",
        route="human",
        contract={"fingerprint": "sha256:deadbeefcafe0002", "source_url": url, "allowed_files": ["docs/x.md"]},
        report_path="reports/monitoring/learn-changes-x.md",
        instructions="",
        title="Autodoc human review: Business Continuity",
        labels=["autodoc", "escalate"],
    )
    assert runner._escalate(_config(tmp_path), ctx, "route=human", "details") == "https://github.com/x/y/issues/7"
    create_call = next(command for command in captured if command[:3] == ["gh", "issue", "create"])
    body = create_call[create_call.index("--body") + 1]
    assert f"Source: {url}" in body
    assert url in body


def test_escalate_body_includes_content_hash(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    # The escalation body must carry the change's exact Content-Hash so learn-monitor-advance.yml
    # can match a closed COMPLETED issue to its specific pending blob by (Source, Content-Hash)
    # instead of GitHub's tokenized `{url} in:body` search (which can advance the wrong baseline).
    monkeypatch.setattr(runner, "_existing_issue_url", lambda config, ctx: None)
    monkeypatch.setattr(runner, "_list_open_autodoc_issues", lambda config: [])
    captured: list[list[str]] = []

    def fake_run(args: Any, **kwargs: Any) -> "_FakeCompleted":
        captured.append(list(args))
        return _FakeCompleted(0, stdout="https://github.com/x/y/issues/9")

    monkeypatch.setattr(runner.subprocess, "run", fake_run)
    url = "https://learn.microsoft.com/en-us/x"
    content_hash = "sha256:deadbeefcafe"
    ctx = runner.ChangeContext(
        fingerprint="sha256:deadbeefcafe0003",
        route="human",
        contract={
            "fingerprint": "sha256:deadbeefcafe0003",
            "source_url": url,
            "content_hash": content_hash,
            "allowed_files": ["docs/x.md"],
        },
        report_path="reports/monitoring/learn-changes-x.md",
        instructions="",
        title="Autodoc human review",
        labels=["autodoc", "escalate"],
    )
    assert runner._escalate(_config(tmp_path), ctx, "route=human", "details") == "https://github.com/x/y/issues/9"
    create_call = next(command for command in captured if command[:3] == ["gh", "issue", "create"])
    body = create_call[create_call.index("--body") + 1]
    assert f"Source: {url}" in body
    assert f"Content-Hash: {content_hash}" in body


def test_escalate_body_omits_source_line_when_url_absent(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(runner, "_existing_issue_url", lambda config, ctx: None)
    captured: dict[str, Any] = {}

    def fake_run(args: Any, **kwargs: Any) -> "_FakeCompleted":
        captured["args"] = list(args)
        return _FakeCompleted(0, stdout="https://github.com/x/y/issues/8")

    monkeypatch.setattr(runner.subprocess, "run", fake_run)
    # _ctx() builds a contract without a source_url or content_hash; both lines must be omitted.
    runner._escalate(_config(tmp_path), _ctx(), "reason", "details")
    body = captured["args"][captured["args"].index("--body") + 1]
    assert "Source:" not in body
    assert "Content-Hash:" not in body


def test_record_ledger_dry_run_is_noop(tmp_path: Path) -> None:
    config = runner.RunnerConfig(repo_path=tmp_path, draft_model="a", review_model="b", dry_run=True)
    runner._record_ledger(config, _ctx(), "pr_open", "detail")
    assert not (tmp_path / config.ledger_path).exists()


def test_record_ledger_writes_to_ledger_abs(tmp_path: Path) -> None:
    # When drafting in a worktree, the ledger must persist to the main repo (ledger_abs).
    main_ledger = tmp_path / "main" / "data" / "autodoc-ledger.json"
    work = tmp_path / "work"
    work.mkdir()
    config = runner.RunnerConfig(repo_path=work, draft_model="a", review_model="b", ledger_abs=main_ledger)
    runner._record_ledger(config, _ctx(), "pr_open", "detail")
    assert main_ledger.exists()
    assert not (work / config.ledger_path).exists()


def test_run_creates_and_removes_worktree(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, patched: dict[str, list[Any]]) -> None:
    monkeypatch.setenv("AUTODOC_ENABLED", "true")
    report = tmp_path / "report.md"
    report.write_text("x", encoding="utf-8")
    monkeypatch.setattr(runner, "_latest_report", lambda config: report)
    monkeypatch.setattr(runner.autodoc_route, "load_ledger", lambda path: {"schema_version": 1, "changes": {}})
    contract = {"fingerprint": "sha256:a", "report_path": "reports/monitoring/learn-changes-x.md", "allowed_files": ["docs/x.md"]}
    spec = {"fingerprint": "sha256:a", "route": "autodraft", "body": "```json\n" + json.dumps(contract) + "\n```", "title": "draft", "labels": ["autodoc"]}
    monkeypatch.setattr(runner.autodoc_route, "route_report", lambda text, name, ledger, **_kw: [spec])
    monkeypatch.setattr(runner, "_run_draft", lambda config, ctx, feedback: _draft())
    monkeypatch.setattr(runner, "_run_deterministic_verify", lambda config, ctx, draft: "pass")
    monkeypatch.setattr(runner, "_run_cross_model_review", lambda config, ctx, draft: {"verdict": "pass"})

    runner.run(_config(tmp_path))

    # Worktree was created before drafting and removed afterward (even though work was used).
    assert patched["worktree"] == ["create", "remove"]


def test_run_no_specs_skips_worktree(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, patched: dict[str, list[Any]]) -> None:
    monkeypatch.setenv("AUTODOC_ENABLED", "true")
    report = tmp_path / "report.md"
    report.write_text("x", encoding="utf-8")
    monkeypatch.setattr(runner, "_latest_report", lambda config: report)
    monkeypatch.setattr(runner.autodoc_route, "load_ledger", lambda path: {"schema_version": 1, "changes": {}})
    monkeypatch.setattr(runner.autodoc_route, "route_report", lambda text, name, ledger, **_kw: [])

    result = runner.run(_config(tmp_path))

    assert result["outcomes"] == []
    assert patched["worktree"] == []  # no worktree created when there is nothing to do


def _write_redirect_catalog(repo_root: Path) -> None:
    url_file = repo_root / "docs" / "reference" / "microsoft-learn-urls.md"
    url_file.parent.mkdir(parents=True, exist_ok=True)
    url_file.write_text(
        "# Microsoft Learn URLs\n\n"
        "## Microsoft Purview\n\n"
        "| Topic | URL | Last checked |\n"
        "| --- | --- | --- |\n"
        "| Existing | https://learn.microsoft.com/en-us/existing | Sep 2026 |\n",
        encoding="utf-8",
    )


def _write_redirect_report(path: Path, rows: list[tuple[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    table_rows = "\n".join(f"| {source} | {destination} |" for source, destination in rows)
    path.write_text(
        "# Learn Monitor report\n\n"
        "## URL Redirects Detected\n\n"
        "| Original URL | Final URL |\n"
        "| --- | --- |\n"
        f"{table_rows}\n",
        encoding="utf-8",
    )


def _patch_redirect_run_side_effects(monkeypatch: pytest.MonkeyPatch) -> dict[str, int]:
    monkeypatch.setenv("AUTODOC_ENABLED", "true")
    monkeypatch.setattr(runner, "_assert_canary", lambda config: None)
    monkeypatch.setattr(runner, "_reconcile_automerge", lambda config: None)
    monkeypatch.setattr(runner, "_create_worktree", lambda config: config.repo_path)
    monkeypatch.setattr(runner, "_remove_worktree", lambda config, work_path: None)
    monkeypatch.setattr(runner, "_git", lambda config, *args: "")
    monkeypatch.setattr(runner, "_untracked_files", lambda config: [])
    monkeypatch.setattr(runner, "_reset_attempt", lambda config, base, baseline: None)
    calls = {"issue_create": 0}

    def fake_run(args: Any, **kwargs: Any) -> "_FakeCompleted":
        if args[:3] == ["gh", "issue", "list"]:
            return _FakeCompleted(0, stdout="[]")
        if args[:3] == ["gh", "issue", "create"]:
            calls["issue_create"] += 1
            return _FakeCompleted(0, stdout=f"https://github.com/x/y/issues/{100 + calls['issue_create']}")
        if args[:3] == ["gh", "issue", "close"]:
            return _FakeCompleted(0, stdout="closed")
        raise AssertionError(f"unexpected command: {args}")

    monkeypatch.setattr(runner.subprocess, "run", fake_run)
    return calls


def _redirect_entry(pr_number: int = 1352, **overrides: Any) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "state": "pr_open",
        "route": "autodraft",
        "classification": "REDIRECT",
        "detail": f"https://github.com/judeper/FSI-AgentGov/pull/{pr_number} (OceanSquad merge)",
    }
    entry.update(overrides)
    return entry


def _write_autodoc_ledger(path: Path, changes: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"schema_version": 1, "changes": changes}, indent=2), encoding="utf-8")


def test_reconcile_reverted_redirect_reroutes_and_preserves_retry_count(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setenv("AUTODOC_ENABLED", "true")
    monkeypatch.setattr(runner, "_assert_canary", lambda config: None)
    monkeypatch.setattr(runner, "_reconcile_automerge", lambda config: None)
    monkeypatch.setattr(runner, "_create_worktree", lambda config: config.repo_path)
    monkeypatch.setattr(runner, "_remove_worktree", lambda config, work_path: None)
    monkeypatch.setattr(
        runner,
        "_fetch_pr_state",
        lambda config, sample: runner.autodoc_automerge.PrState("merged", merge_sha="abc123"),
    )
    monkeypatch.setattr(runner, "_commit_revert_status", lambda config, sha: True)

    source = "https://learn.microsoft.com/en-us/purview/create-retention-policies"
    destination = "https://learn.microsoft.com/en-us/purview/retention"
    _write_redirect_catalog(tmp_path)
    catalog = tmp_path / "docs" / "reference" / "microsoft-learn-urls.md"
    catalog.write_text(catalog.read_text(encoding="utf-8").replace("https://learn.microsoft.com/en-us/existing", source), encoding="utf-8")
    report = tmp_path / "reports" / "monitoring" / "learn-changes-2026-09-30.md"
    _write_redirect_report(report, [(source, destination)])
    fingerprint = route.compute_fingerprint(report.name, source, "REDIRECT", [route.REDIRECT_TARGET_FILE], destination)
    _write_autodoc_ledger(tmp_path / "data" / "autodoc-ledger.json", {fingerprint: _redirect_entry()})
    monkeypatch.setattr(runner, "_latest_report", lambda config: report)
    diff = f"--- a/x\n+++ b/x\n@@ -1 +1 @@\n-| Existing | {source} | Sep 2026 |\n+| Existing | {destination} | Sep 2026 |\n"
    monkeypatch.setattr(runner, "_git", _redirect_git_mock(diff))
    monkeypatch.setattr(runner, "_untracked_files", lambda config: [])
    monkeypatch.setattr(runner, "_reset_attempt", lambda config, base, baseline: None)
    monkeypatch.setattr(
        runner,
        "_push_and_create_pr",
        lambda config, ctx, body: "https://github.com/judeper/FSI-AgentGov/pull/1400",
    )

    result = runner.run(_config(tmp_path))

    assert result["outcomes"][0]["status"] == "pr_opened"
    ledger = route.load_ledger(tmp_path / "data" / "autodoc-ledger.json")
    entry = ledger["changes"][fingerprint]
    assert entry["state"] == "pr_open"
    assert entry["retries"] == 1
    assert entry["retry_history"][0]["reason"] == "merged_reverted"
    assert entry["detail"].startswith("https://github.com/judeper/FSI-AgentGov/pull/1400")


def test_reconcile_closed_unmerged_retries_once_then_exhausts(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    cfg = _config(tmp_path)
    ledger = {"schema_version": 1, "changes": {"sha256:redir": _redirect_entry()}}
    monkeypatch.setattr(runner, "_fetch_pr_state", lambda config, sample: runner.autodoc_automerge.PrState("closed"))

    first = runner._reconcile_redirect_retries(cfg, ledger)

    entry = ledger["changes"]["sha256:redir"]
    assert first["retry_pending"][0]["reason"] == "closed_unmerged"
    assert entry["state"] == "retry_pending"
    assert entry["retries"] == 1

    entry["state"] = "pr_open"
    entry["detail"] = "https://github.com/judeper/FSI-AgentGov/pull/1401"
    second = runner._reconcile_redirect_retries(cfg, ledger)

    assert second["retry_exhausted"][0]["reason"] == "closed_unmerged_limit"
    assert entry["state"] == "retry_exhausted"
    assert entry["retries"] == 1


def test_reconcile_redirect_retry_cap_blocks_third_attempt(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    cfg = _config(tmp_path)
    ledger = {
        "schema_version": 1,
        "changes": {
            "sha256:redir": _redirect_entry(
                retries=2,
                retry_history=[
                    {"retry": 1, "reason": "merged_reverted"},
                    {"retry": 2, "reason": "merged_reverted"},
                ],
            )
        },
    }
    monkeypatch.setattr(
        runner,
        "_fetch_pr_state",
        lambda config, sample: runner.autodoc_automerge.PrState("merged", merge_sha="abc123"),
    )
    monkeypatch.setattr(runner, "_commit_revert_status", lambda config, sha: True)

    summary = runner._reconcile_redirect_retries(cfg, ledger)

    entry = ledger["changes"]["sha256:redir"]
    assert summary["retry_exhausted"][0]["reason"] == "retry_cap_reached"
    assert entry["state"] == "retry_exhausted"
    assert entry["retries"] == 2


@pytest.mark.parametrize(
    ("entry", "observed", "reverted", "expected_reason"),
    [
        (_redirect_entry(detail="not a github pr"), None, None, "unparseable_or_foreign_pr_url"),
        (
            _redirect_entry(detail="https://github.com/other/Repo/pull/1352"),
            None,
            None,
            "unparseable_or_foreign_pr_url",
        ),
        (_redirect_entry(), runner.autodoc_automerge.PrState("open"), None, "open_or_unknown"),
        (_redirect_entry(), runner.autodoc_automerge.PrState("merged", merge_sha="abc123"), None, "revert_lookup_error"),
    ],
)
def test_reconcile_failures_keep_redirect_suppressed(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    entry: dict[str, Any],
    observed: runner.autodoc_automerge.PrState | None,
    reverted: bool | None,
    expected_reason: str,
) -> None:
    cfg = _config(tmp_path)
    ledger = {"schema_version": 1, "changes": {"sha256:redir": dict(entry)}}
    fetch_calls: list[int] = []

    def fake_fetch(config: Any, sample: dict[str, Any]) -> runner.autodoc_automerge.PrState:
        fetch_calls.append(int(sample["pr_number"]))
        if observed is None:
            raise AssertionError("fetch should not run")
        return observed

    monkeypatch.setattr(runner, "_fetch_pr_state", fake_fetch)
    monkeypatch.setattr(runner, "_commit_revert_status", lambda config, sha: reverted)

    summary = runner._reconcile_redirect_retries(cfg, ledger)

    assert ledger["changes"]["sha256:redir"]["state"] == "pr_open"
    assert summary["skipped"][0]["reason"] == expected_reason
    if observed is None:
        assert fetch_calls == []


def test_reconcile_pr_lookup_exception_keeps_redirect_suppressed(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    ledger = {"schema_version": 1, "changes": {"sha256:redir": _redirect_entry()}}
    monkeypatch.setattr(
        runner,
        "_fetch_pr_state",
        lambda config, sample: (_ for _ in ()).throw(RuntimeError("gh unavailable")),
    )

    summary = runner._reconcile_redirect_retries(_config(tmp_path), ledger)

    assert ledger["changes"]["sha256:redir"]["state"] == "pr_open"
    assert summary["skipped"][0]["reason"].startswith("pr_lookup_error:")


def test_reconcile_content_escalated_human_and_legacy_entries_untouched(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    ledger = {
        "schema_version": 1,
        "changes": {
            "sha256:content": _redirect_entry(classification="MEDIUM"),
            "sha256:escalated": _redirect_entry(state="escalated"),
            "sha256:human": _redirect_entry(state="human_escalated"),
            "sha256:legacy": {
                "state": "pr_open",
                "route": "autodraft",
                "detail": "https://github.com/judeper/FSI-AgentGov/pull/1352",
            },
        },
    }
    before = json.loads(json.dumps(ledger))
    monkeypatch.setattr(runner, "_fetch_pr_state", lambda config, sample: pytest.fail("must not query non-redirect rows"))

    summary = runner._reconcile_redirect_retries(_config(tmp_path), ledger)

    assert ledger == before
    assert summary["checked"] == 0
    assert summary["skipped"] == [{"fingerprint": "sha256:legacy", "reason": "missing_redirect_classification"}]


def test_reconcile_dry_run_does_not_write_ledger(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    path = tmp_path / "data" / "autodoc-ledger.json"
    _write_autodoc_ledger(path, {"sha256:redir": _redirect_entry()})
    before = path.read_text(encoding="utf-8")
    ledger = route.load_ledger(path)
    cfg = runner.RunnerConfig(repo_path=tmp_path, draft_model="a", review_model="b", dry_run=True)
    monkeypatch.setattr(runner, "_fetch_pr_state", lambda config, sample: runner.autodoc_automerge.PrState("closed"))

    runner._reconcile_redirect_retries(cfg, ledger)

    assert path.read_text(encoding="utf-8") == before
    assert ledger["changes"]["sha256:redir"]["state"] == "retry_pending"


def test_record_ledger_preserves_redirect_retry_counters(tmp_path: Path) -> None:
    ledger_path = tmp_path / "data" / "autodoc-ledger.json"
    _write_autodoc_ledger(
        ledger_path,
        {
            "sha256:redir01": _redirect_entry(
                state="retry_pending",
                retries=1,
                retry_history=[{"retry": 1, "reason": "closed_unmerged"}],
            )
        },
    )
    cfg = runner.RunnerConfig(repo_path=tmp_path, draft_model="a", review_model="b")
    ctx = _redirect_ctx("https://old/", "https://new/")

    runner._record_ledger(cfg, ctx, "pr_open", "https://github.com/judeper/FSI-AgentGov/pull/1400")

    entry = route.load_ledger(ledger_path)["changes"]["sha256:redir01"]
    assert entry["state"] == "pr_open"
    assert entry["retries"] == 1
    assert entry["retry_history"] == [{"retry": 1, "reason": "closed_unmerged"}]
    assert entry["classification"] == "REDIRECT"


def test_retry_pending_reroutes_without_incrementing_when_absent_from_report(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setenv("AUTODOC_ENABLED", "true")
    monkeypatch.setattr(runner, "_assert_canary", lambda config: None)
    monkeypatch.setattr(runner, "_reconcile_automerge", lambda config: None)
    monkeypatch.setattr(runner, "_fetch_pr_state", lambda config, sample: pytest.fail("pending entries must not be re-queried"))
    report = tmp_path / "reports" / "monitoring" / "learn-changes-empty.md"
    report.parent.mkdir(parents=True)
    report.write_text("# Learn Monitor report\n\nNo changes.\n", encoding="utf-8")
    monkeypatch.setattr(runner, "_latest_report", lambda config: report)
    _write_autodoc_ledger(
        tmp_path / "data" / "autodoc-ledger.json",
        {
            "sha256:redir": _redirect_entry(
                state="retry_pending",
                retries=1,
                retry_history=[{"retry": 1, "reason": "merged_reverted"}],
            )
        },
    )

    result = runner.run(_config(tmp_path))

    entry = route.load_ledger(tmp_path / "data" / "autodoc-ledger.json")["changes"]["sha256:redir"]
    assert result["outcomes"] == []
    assert entry["state"] == "retry_pending"
    assert entry["retries"] == 1
    assert route.already_processed({"changes": {"sha256:redir": entry}}, "sha256:redir") is False


def test_run_processes_fragment_distinct_redirects_before_seen_dedupe(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    calls = _patch_redirect_run_side_effects(monkeypatch)
    _write_redirect_catalog(tmp_path)
    report = tmp_path / "reports" / "monitoring" / "learn-changes-fragments.md"
    source = "https://learn.microsoft.com/en-us/purview/create-retention-policies"
    destination = "https://learn.microsoft.com/en-us/purview/retention"
    _write_redirect_report(
        report,
        [
            (source, destination),
            (f"{source}#retaining-content-thats-in-sharepoint-sites", destination),
        ],
    )
    monkeypatch.setattr(runner, "_latest_report", lambda config: report)

    result = runner.run(_config(tmp_path))

    statuses = [outcome["status"] for outcome in result["outcomes"]]
    fingerprints = [outcome["fingerprint"] for outcome in result["outcomes"]]
    assert statuses == ["escalated", "escalated"]
    assert len(set(fingerprints)) == 2
    assert calls["issue_create"] == 2


def test_run_twice_on_unchanged_human_input_creates_one_issue_total(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    calls = _patch_redirect_run_side_effects(monkeypatch)
    _write_redirect_catalog(tmp_path)
    source = "https://learn.microsoft.com/en-us/purview/create-retention-policies"
    destination = "https://learn.microsoft.com/en-us/purview/retention"
    first_report = tmp_path / "reports" / "monitoring" / "learn-changes-2026-09-29.md"
    second_report = tmp_path / "reports" / "monitoring" / "learn-changes-2026-09-30.md"
    _write_redirect_report(first_report, [(source, destination)])
    _write_redirect_report(second_report, [(source, destination)])
    reports = iter([first_report, second_report])
    monkeypatch.setattr(runner, "_latest_report", lambda config: next(reports))

    first = runner.run(_config(tmp_path))
    second = runner.run(_config(tmp_path))

    assert first["outcomes"][0]["status"] == "escalated"
    assert second["outcomes"] == []
    assert calls["issue_create"] == 1


def test_open_pr_failure_does_not_record_pr_open(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, patched: dict[str, list[Any]]) -> None:
    monkeypatch.setattr(runner, "_run_draft", lambda config, ctx, feedback: _draft())
    monkeypatch.setattr(runner, "_run_deterministic_verify", lambda config, ctx, draft: "pass")
    monkeypatch.setattr(runner, "_run_cross_model_review", lambda config, ctx, draft: {"verdict": "pass"})

    def failing_pr(config: Any, ctx: Any, draft: Any, verdict: Any) -> str:
        raise RuntimeError("gh pr create failed (exit 1)")

    monkeypatch.setattr(runner, "_open_pr", failing_pr)

    with pytest.raises(RuntimeError):
        runner.process_change(_config(tmp_path), _ctx())

    # The ledger must NOT have been marked pr_open for a PR that never opened.
    assert all(state != "pr_open" for state, _ in patched["ledger"])


def test_reset_attempt_removes_only_leaked_untracked(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    git_calls: list[tuple[str, ...]] = []
    monkeypatch.setattr(runner, "_git", lambda config, *args: git_calls.append(args) or "")
    new_file = tmp_path / "docs" / "new.md"
    new_file.parent.mkdir(parents=True)
    new_file.write_text("drafted", encoding="utf-8")
    preexisting = tmp_path / "user-notes.txt"
    preexisting.write_text("keep me", encoding="utf-8")
    # After the reset the working tree shows both as untracked; baseline contained only the
    # pre-existing one, so only the draft-created file is leaked and removed.
    monkeypatch.setattr(runner, "_untracked_files", lambda config: ["docs/new.md", "user-notes.txt"])

    runner._reset_attempt(_config(tmp_path), "main", ["user-notes.txt"])

    assert ("reset", "--hard", "main") in git_calls
    assert not new_file.exists()  # draft-created file removed
    assert preexisting.exists()  # pre-existing user file untouched


def test_run_dedups_duplicate_fingerprints(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, patched: dict[str, list[Any]]) -> None:
    monkeypatch.setenv("AUTODOC_ENABLED", "true")
    report = tmp_path / "report.md"
    report.write_text("irrelevant", encoding="utf-8")
    monkeypatch.setattr(runner, "_latest_report", lambda config: report)
    monkeypatch.setattr(runner.autodoc_route, "load_ledger", lambda path: {"schema_version": 1, "changes": {}})
    contract = {"fingerprint": "sha256:dup", "report_path": "reports/monitoring/learn-changes-x.md", "allowed_files": ["docs/x.md"]}
    body = "```json\n" + json.dumps(contract) + "\n```"
    spec = {"fingerprint": "sha256:dup", "route": "autodraft", "body": body, "title": "draft", "labels": ["autodoc"]}
    monkeypatch.setattr(runner.autodoc_route, "route_report", lambda text, name, ledger, **_kw: [spec, dict(spec)])
    draft_calls = {"n": 0}

    def draft(config: Any, ctx: Any, feedback: str) -> runner.DraftResult:
        draft_calls["n"] += 1
        return _draft()

    monkeypatch.setattr(runner, "_run_draft", draft)
    monkeypatch.setattr(runner, "_run_deterministic_verify", lambda config, ctx, d: "pass")
    monkeypatch.setattr(runner, "_run_cross_model_review", lambda config, ctx, d: {"verdict": "pass"})

    result = runner.run(_config(tmp_path))

    statuses = [o["status"] for o in result["outcomes"]]
    assert statuses == ["pr_opened", "skipped"]
    assert draft_calls["n"] == 1  # second duplicate spec was not processed

# --- Stage 2 redirect auto-merge integration -------------------------------------


def test_pr_number_from_detail() -> None:
    assert runner._pr_number_from_detail("https://github.com/o/r/pull/504") == 504
    assert runner._pr_number_from_detail("PR#9") is None
    assert runner._pr_number_from_detail("") is None


def test_record_and_maybe_automerge_dry_run_noop(tmp_path: Path) -> None:
    cfg = runner.RunnerConfig(repo_path=tmp_path, draft_model="a", review_model="b", dry_run=True)
    ctx = _redirect_ctx("https://old/", "https://new/")
    assert runner._record_and_maybe_automerge(cfg, ctx, "https://old/", "https://new/", "x") == "x"


def test_record_and_maybe_automerge_remains_observational(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(runner, "_enable_automerge", lambda c, ctx: pytest.fail("target-native auto-merge is disabled"))
    cfg = runner.RunnerConfig(repo_path=tmp_path, draft_model="a", review_model="b")
    ctx = _redirect_ctx("https://old/", "https://new/")
    detail = runner._record_and_maybe_automerge(cfg, ctx, "https://old/", "https://new/", "https://github.com/o/r/pull/7")
    assert "target-native auto-merge disabled" in detail
    led = runner._automerge_ledger_file(cfg)
    assert "sha256:redir01" in runner.autodoc_automerge.load_ledger(led)["samples"]


def test_record_and_maybe_automerge_unlocked_still_does_not_enable(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    calls: list[str] = []
    monkeypatch.setattr(runner, "_enable_automerge", lambda c, ctx: calls.append(ctx.branch))
    monkeypatch.setattr(
        runner.autodoc_automerge,
        "unlock_state",
        lambda p, now=None, config=None: runner.autodoc_automerge.UnlockState(True, "unlocked", 10, 10, 0, 1.0, 5.0),
    )
    cfg = runner.RunnerConfig(repo_path=tmp_path, draft_model="a", review_model="b")
    ctx = _redirect_ctx("https://old/", "https://new/")
    detail = runner._record_and_maybe_automerge(cfg, ctx, "https://old/", "https://new/", "https://github.com/o/r/pull/7")
    assert "target-native auto-merge disabled" in detail
    assert "observed gate: unlocked" in detail
    assert calls == []


def test_record_and_maybe_automerge_no_pr_number_noop(tmp_path: Path) -> None:
    cfg = runner.RunnerConfig(repo_path=tmp_path, draft_model="a", review_model="b")
    ctx = _redirect_ctx("https://old/", "https://new/")
    assert runner._record_and_maybe_automerge(cfg, ctx, "https://old/", "https://new/", "PR#9") == "PR#9"
    assert not runner._automerge_ledger_file(cfg).exists()

def test_commit_is_reverted_detection(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    cfg = runner.RunnerConfig(repo_path=tmp_path, draft_model="a", review_model="b")
    cp = runner.subprocess.CompletedProcess
    monkeypatch.setattr(runner.subprocess, "run", lambda *a, **k: cp(args=[], returncode=0, stdout="deadbeef\n", stderr=""))
    assert runner._commit_is_reverted(cfg, "abc") is True
    monkeypatch.setattr(runner.subprocess, "run", lambda *a, **k: cp(args=[], returncode=0, stdout="", stderr=""))
    assert runner._commit_is_reverted(cfg, "abc") is False
    # fail closed on a git error
    monkeypatch.setattr(runner.subprocess, "run", lambda *a, **k: cp(args=[], returncode=128, stdout="", stderr="boom"))
    assert runner._commit_is_reverted(cfg, "abc") is True


def test_fetch_pr_state_merged_reverted(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    cfg = runner.RunnerConfig(repo_path=tmp_path, draft_model="a", review_model="b")
    cp = runner.subprocess.CompletedProcess
    monkeypatch.setattr(runner.subprocess, "run", lambda *a, **k: cp(args=[], returncode=0, stdout='{"state":"MERGED","mergeCommit":{"oid":"abc"}}', stderr=""))
    monkeypatch.setattr(runner, "_commit_is_reverted", lambda c, sha: True)
    st = runner._fetch_pr_state(cfg, {"pr_number": 5})
    assert st.state == "merged" and st.reverted is True


def test_fetch_pr_state_merged_clean(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    cfg = runner.RunnerConfig(repo_path=tmp_path, draft_model="a", review_model="b")
    cp = runner.subprocess.CompletedProcess
    monkeypatch.setattr(runner.subprocess, "run", lambda *a, **k: cp(args=[], returncode=0, stdout='{"state":"MERGED","mergeCommit":{"oid":"abc"}}', stderr=""))
    monkeypatch.setattr(runner, "_commit_is_reverted", lambda c, sha: False)
    monkeypatch.setattr(runner, "_fetch_commit_diff", lambda c, sha: "DIFF")
    st = runner._fetch_pr_state(cfg, {"pr_number": 5})
    assert st.state == "merged" and st.reverted is False and st.merged_diff == "DIFF"

def test_fetch_pr_state_uses_stored_merge_sha_via_git(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    # When merge_sha is already stored, _fetch_pr_state must re-check revert via git
    # (_commit_is_reverted) and NOT call gh (which can fail open).
    cfg = runner.RunnerConfig(repo_path=tmp_path, draft_model="a", review_model="b")
    monkeypatch.setattr(runner.subprocess, "run", lambda *a, **k: pytest.fail("must not call gh when merge_sha is stored"))
    monkeypatch.setattr(runner, "_commit_is_reverted", lambda c, sha: sha == "reverted-sha")
    assert runner._fetch_pr_state(cfg, {"pr_number": 5, "merge_sha": "reverted-sha"}).reverted is True
    assert runner._fetch_pr_state(cfg, {"pr_number": 5, "merge_sha": "clean-sha"}).reverted is False
