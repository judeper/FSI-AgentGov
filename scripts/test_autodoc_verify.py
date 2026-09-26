"""Tests for the deterministic autodoc verifier."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import autodoc_verify  # noqa: E402
import autodoc_verify_gate  # noqa: E402
import autodoc_workflow  # noqa: E402
from autodoc_verify import (  # noqa: E402
    FileChange,
    check_claim_support,
    check_diff_minimality,
    check_language,
    check_path_allowlist,
    check_section_allowlist,
    load_contract,
    parse_unified_diff,
    verify,
)

ALLOWED_PATH = "docs/controls/pillar-2-management/2.4-test.md"
PROJECT_ROOT = SCRIPT_DIR.parent
REDIRECT_PATH = "docs/reference/microsoft-learn-urls.md"
REDIRECT_OLD_URL = "https://learn.microsoft.com/en-us/power-platform/admin/manage-copilot-studio-messages-capacity"
REDIRECT_NEW_URL = "https://learn.microsoft.com/en-us/power-platform/admin/manage-copilot-studio-copilot-credits-capacity"
REDIRECT_FINGERPRINT = "sha256:c3af9af0d43c439f7f51ca530185d7eff9816ba23445ea038e07f18d67a791ed"
REDIRECT_REPORT_PATH = "reports/monitoring/learn-changes-2026-08-20.md"
REDIRECT_BEFORE_FIXTURE = PROJECT_ROOT / "tests" / "fixtures" / "autodoc" / "trusted-redirect-before.md"
REDIRECT_PR_BODY = f"""Automated **deterministic** Learn-URL redirect update.

AUTODOC-FINGERPRINT: {REDIRECT_FINGERPRINT}
Source report: {REDIRECT_REPORT_PATH}

`{REDIRECT_OLD_URL}`
→ `{REDIRECT_NEW_URL}`

No LLM was involved: the runner applied the exact URL swap and verified the staged diff is a clean URL-only change in the Learn URL list.

Merge policy: OceanSquad reviews and SHA-pinned merges after all required checks pass. Owner review is required only if automation escalates the PR.
"""


def _redirect_diff(old_row: str, new_row: str, extra: str = "") -> str:
    return f"""diff --git a/{REDIRECT_PATH} b/{REDIRECT_PATH}
index db8f29dcf9..97f02f633b 100644
--- a/{REDIRECT_PATH}
+++ b/{REDIRECT_PATH}
@@ -50,7 +50,7 @@ Customer-facing reference list of the Microsoft Learn links used throughout the
| **Copilot Hub** | https://learn.microsoft.com/en-us/power-platform/admin/copilot/copilot-hub | Jan 2026 |
| **Maker Onboarding (Welcome Content)** | https://learn.microsoft.com/en-us/power-platform/admin/welcome-content | Jan 2026 |
| **Agent Access Points** | https://learn.microsoft.com/en-us/power-platform/admin/security/identity-access-management#agent-access-points-preview | Jan 2026 |
-{old_row}
+{new_row}
| **Business Continuity** | https://learn.microsoft.com/en-us/power-platform/admin/business-continuity-disaster-recovery | Jan 2026 |
| Backup and Restore | https://learn.microsoft.com/en-us/power-platform/admin/backup-restore-environments | Jan 2026 |
| Regions Overview | https://learn.microsoft.com/en-us/power-platform/admin/regions-overview | Jan 2026 |
{extra}"""


def _trusted_redirect_fixture(
    tmp_path: Path, *, trusted_repo_root: Path = PROJECT_ROOT
) -> tuple[dict, str, str, str, Path]:
    trusted = autodoc_workflow.derive_trusted_contract(REDIRECT_PR_BODY, repo_root=trusted_repo_root)
    report = (trusted_repo_root / REDIRECT_REPORT_PATH).read_text(encoding="utf-8")
    before = REDIRECT_BEFORE_FIXTURE.read_text(encoding="utf-8")
    assert before.count(REDIRECT_OLD_URL) == 1
    assert REDIRECT_NEW_URL not in before
    after = before.replace(REDIRECT_OLD_URL, REDIRECT_NEW_URL, 1)
    assert after != before

    repo = _lint_repo(tmp_path)
    target = repo / Path(*REDIRECT_PATH.split("/"))
    target.parent.mkdir(parents=True)
    target.write_text(after, encoding="utf-8")
    return trusted["contract"], report, before, after, repo


def _contract(**overrides):
    contract = {
        "schema_version": 1,
        "fingerprint": "sha256:test",
        "allowed_files": [ALLOWED_PATH],
        "allowed_headings": ["Additional Resources"],
        "forbidden_paths": [".github/**", "scripts/**", "data/**", "reports/**", "assessment/**", "mkdocs.yml"],
    }
    contract.update(overrides)
    return contract


def _diff(path: str, added_line: str = "Allowed additive note.") -> str:
    return f"""diff --git a/{path} b/{path}
--- a/{path}
+++ b/{path}
@@ -3,2 +3,3 @@
 ## Additional Resources
 Existing.
+{added_line}
"""


def _lint_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    scripts_dir = repo / "scripts"
    docs_dir = repo / "docs"
    scripts_dir.mkdir(parents=True)
    docs_dir.mkdir()
    (scripts_dir / "verify_language_rules.py").write_text(
        (SCRIPT_DIR / "verify_language_rules.py").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    return repo


REDIRECT_OLD_ROW = f"| **Copilot Studio Message Capacity** | {REDIRECT_OLD_URL} | Jan 2026 |"
REDIRECT_NEW_ROW = f"| **Copilot Studio Message Capacity** | {REDIRECT_NEW_URL} | Jan 2026 |"

# Relative --head-dir exactly as .github/workflows/autodoc-verify.yml passes it.
WORKFLOW_HEAD_DIR_ARG = ".autodoc/head"


def _workflow_runner_workspace(
    root: Path,
    *,
    head_markdown: str,
    diff_text: str,
    pr_body: str = REDIRECT_PR_BODY,
) -> dict[str, str]:
    """Materialize the runner layout that .github/workflows/autodoc-verify.yml builds.

    Mirrors the workflow steps: the trusted base checkout supplies the contract and the
    monitoring report at their real repo-relative paths, the base-code language linter is
    copied into ``.autodoc/head/scripts``, and the allowed PR head Markdown is written into
    ``.autodoc/head`` as LF bytes the way the Contents API serves it. Returned argument
    values are repo-relative, so the gate runs against a relative ``--head-dir``.
    """

    trusted = autodoc_workflow.derive_trusted_contract(pr_body, repo_root=PROJECT_ROOT)
    contract = trusted["contract"]
    report_path = str(trusted["report_path"])

    work = root / ".autodoc"
    work.mkdir(parents=True, exist_ok=True)

    base_report = root / Path(*report_path.split("/"))
    base_report.parent.mkdir(parents=True, exist_ok=True)
    base_report.write_bytes((PROJECT_ROOT / report_path).read_text(encoding="utf-8").encode("utf-8"))

    head_dir = work / "head"
    linter = head_dir / "scripts" / "verify_language_rules.py"
    linter.parent.mkdir(parents=True)
    linter.write_bytes((SCRIPT_DIR / "verify_language_rules.py").read_text(encoding="utf-8").encode("utf-8"))

    head_file = head_dir / Path(*REDIRECT_PATH.split("/"))
    head_file.parent.mkdir(parents=True, exist_ok=True)
    head_file.write_bytes(head_markdown.encode("utf-8"))

    (work / "contract.json").write_bytes((json.dumps(contract, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    (work / "pr.diff").write_bytes(diff_text.encode("utf-8"))
    (work / "pr-body.txt").write_bytes(pr_body.encode("utf-8"))

    return {
        "contract": ".autodoc/contract.json",
        "report": report_path,
        "diff": ".autodoc/pr.diff",
        "head_dir": WORKFLOW_HEAD_DIR_ARG,
        "pr_body": ".autodoc/pr-body.txt",
        "out": ".autodoc/gate.json",
    }


def _run_workflow_gate(
    root: Path, args: dict[str, str], monkeypatch: pytest.MonkeyPatch
) -> tuple[int, dict]:
    """Invoke the gate CLI from the runner workspace root, as the workflow step does."""

    monkeypatch.chdir(root)
    exit_code = autodoc_verify_gate.main(
        [
            "--contract",
            args["contract"],
            "--report",
            args["report"],
            "--diff",
            args["diff"],
            "--head-dir",
            args["head_dir"],
            "--pr-body",
            args["pr_body"],
            "--out",
            args["out"],
        ]
    )
    result = json.loads((root / Path(*args["out"].split("/"))).read_text(encoding="utf-8"))
    return exit_code, result


def _assert_linter_started(result: dict) -> None:
    """Fail if the language linter never launched instead of judging the content."""

    for finding in result.get("deterministic", {}).get("findings", []):
        message = str(finding.get("message", ""))
        assert "No such file or directory" not in message, f"language linter did not start: {message}"
        assert "can't open file" not in message, f"language linter did not start: {message}"
        assert "was not found under repo_root" not in message, f"language linter did not start: {message}"


def _redirect_head_markdown(new_row: str = REDIRECT_NEW_ROW) -> str:
    before = REDIRECT_BEFORE_FIXTURE.read_text(encoding="utf-8")
    return before.replace(REDIRECT_OLD_ROW, new_row, 1)


def test_path_allowlist_blocks_forbidden_paths() -> None:
    contract = _contract(allowed_files=[".github/workflows/x.yml", "scripts/y.py"])
    changes = parse_unified_diff(_diff(".github/workflows/x.yml") + _diff("scripts/y.py"))

    findings = check_path_allowlist(list(changes), contract)

    assert {finding.path for finding in findings} == {".github/workflows/x.yml", "scripts/y.py"}
    assert all(finding.severity == "block" for finding in findings)


def test_path_allowlist_blocks_files_not_in_allowed_files() -> None:
    changes = parse_unified_diff(_diff("docs/controls/pillar-2-management/2.99-other.md"))

    findings = check_path_allowlist(list(changes), _contract())

    assert len(findings) == 1
    assert findings[0].path == "docs/controls/pillar-2-management/2.99-other.md"
    assert "allowed_files" in findings[0].message


def test_path_allowlist_allows_only_allowed_file() -> None:
    changes = parse_unified_diff(_diff(ALLOWED_PATH))

    assert check_path_allowlist(list(changes), _contract()) == []


def test_forbidden_glob_matching_supports_double_star_patterns() -> None:
    path = "docs/a/b/secret.md"
    contract = _contract(allowed_files=[path], forbidden_paths=["docs/**/secret.md"])
    changes = parse_unified_diff(_diff(path))

    findings = check_path_allowlist(list(changes), contract)

    assert len(findings) == 1
    assert findings[0].path == path
    assert "docs/**/secret.md" in findings[0].message


def test_section_allowlist_blocks_added_line_under_unapproved_heading() -> None:
    diff = f"""diff --git a/{ALLOWED_PATH} b/{ALLOWED_PATH}
--- a/{ALLOWED_PATH}
+++ b/{ALLOWED_PATH}
@@ -1,3 +1,4 @@
 # Control
 ## Objective
 Existing.
+New implementation note.
"""
    changes = parse_unified_diff(diff)
    contents = {ALLOWED_PATH: "# Control\n## Objective\nExisting.\nNew implementation note.\n"}

    findings = check_section_allowlist(contents, changes, _contract())

    assert len(findings) == 1
    assert findings[0].check == "section_allowlist"
    assert "Objective" in findings[0].message


def test_section_allowlist_allows_added_line_under_allowed_heading() -> None:
    changes = parse_unified_diff(_diff(ALLOWED_PATH))
    contents = {ALLOWED_PATH: "# Control\n\n## Additional Resources\nExisting.\nAllowed additive note.\n"}

    assert check_section_allowlist(contents, changes, _contract()) == []


def test_section_allowlist_ignores_spoofed_heading_inside_fence() -> None:
    diff = f"""diff --git a/{ALLOWED_PATH} b/{ALLOWED_PATH}
--- a/{ALLOWED_PATH}
+++ b/{ALLOWED_PATH}
@@ -1,5 +1,6 @@
 # Control
 
 ```text
 ## Additional Resources
 ```
+New implementation note.
"""
    changes = parse_unified_diff(diff)
    contents = {ALLOWED_PATH: "# Control\n\n```text\n## Additional Resources\n```\nNew implementation note.\n"}

    findings = check_section_allowlist(contents, changes, _contract())

    assert len(findings) == 1
    assert findings[0].check == "section_allowlist"
    assert "Additional Resources" not in findings[0].message


def test_section_allowlist_ignores_spoofed_heading_inside_tilde_fence() -> None:
    diff = f"""diff --git a/{ALLOWED_PATH} b/{ALLOWED_PATH}
--- a/{ALLOWED_PATH}
+++ b/{ALLOWED_PATH}
@@ -1,5 +1,6 @@
 # Control
 
 ~~~text
 ## Additional Resources
 ~~~
+New implementation note.
"""
    changes = parse_unified_diff(diff)
    contents = {ALLOWED_PATH: "# Control\n\n~~~text\n## Additional Resources\n~~~\nNew implementation note.\n"}

    findings = check_section_allowlist(contents, changes, _contract())

    assert len(findings) == 1
    assert findings[0].check == "section_allowlist"
    assert "Additional Resources" not in findings[0].message


def test_heading_lookup_ignores_premature_close_with_trailing_text() -> None:
    # CommonMark: a fence line with trailing text does NOT close the block, so a
    # heading after it is still code, not a real heading.
    lines = ["~~~", "example output:", "~~~ delimiter", "## Spoofed Heading", "payload", "~~~"]
    assert "Spoofed Heading" not in autodoc_verify._heading_lookup(lines).values()


def test_heading_lookup_requires_close_fence_at_least_opener_length() -> None:
    # CommonMark: a closing fence must be at least as long as the opener, so a
    # 3-backtick line does not close a 4-backtick fence.
    lines = ["````", "example", "```", "## Spoofed Heading", "still code", "````"]
    assert "Spoofed Heading" not in autodoc_verify._heading_lookup(lines).values()


def test_heading_lookup_indented_close_fence_does_not_close() -> None:
    # CommonMark: a fence delimiter indented >=4 spaces is code, not a close.
    lines = ["```text", "example", "     ```", "## Spoofed Heading", "payload", "```"]
    assert "Spoofed Heading" not in autodoc_verify._heading_lookup(lines).values()


def test_heading_lookup_ignores_heading_inside_list_item_fence() -> None:
    # A code fence opened inside a list item is still a code block per CommonMark,
    # so an ATX heading inside it must NOT be treated as a real heading.
    lines = ["# Control", "", "## Objective", "", "- ```", "  ## Additional Resources", "  ```", "payload"]
    assert "Additional Resources" not in autodoc_verify._heading_lookup(lines).values()


def test_diff_minimality_blocks_huge_diff() -> None:
    change = FileChange(path=ALLOWED_PATH, added_lines=["line"] * 121)

    findings = check_diff_minimality({ALLOWED_PATH: change}, _contract(), max_total_lines=120)

    assert len(findings) == 1
    assert findings[0].check == "diff_minimality"
    assert "121" in findings[0].message


def test_claim_support_blocks_unsupported_factual_date() -> None:
    findings = check_claim_support(["+Available starting March 2027."], "The report mentions April 2027 only.")

    assert len(findings) == 1
    assert findings[0].check == "claim_support"
    assert "March 2027" in findings[0].message


def test_claim_support_allows_supported_factual_date() -> None:
    findings = check_claim_support(
        ["+Available starting March 2027."],
        "The Microsoft Learn source report explicitly mentions March 2027.",
    )

    assert findings == []


def test_claim_support_blocks_hallucinated_numeric_context() -> None:
    findings = check_claim_support(
        ["+The data retention period is 90 days."],
        "The source report says the data retention period is 30 days.",
    )

    assert len(findings) == 1
    assert findings[0].check == "claim_support"
    assert "90 days" in findings[0].message


def test_claim_support_allows_supported_numeric_context() -> None:
    findings = check_claim_support(
        ["+The data retention period is 90 days."],
        "The source report says the data retention period is 90 days.",
    )

    assert findings == []


def test_verify_keeps_claim_support_for_non_redirect_autodrafts(tmp_path: Path) -> None:
    repo = _lint_repo(tmp_path)
    target = repo / Path(*ALLOWED_PATH.split("/"))
    target.parent.mkdir(parents=True)
    content = "# Control\n\n## Additional Resources\nAvailable starting March 2027.\n"
    target.write_text(content, encoding="utf-8")
    contract = _contract(classification="MEDIUM", route="autodraft")

    verdict = verify(
        contract,
        _diff(ALLOWED_PATH, "Available starting March 2027."),
        {ALLOWED_PATH: content},
        "The source report mentions April 2027 only.",
        pr_body="AUTODOC-FINGERPRINT: sha256:test\n",
        repo_root=repo,
    )

    assert verdict["pass"] is False
    assert any(finding["check"] == "claim_support" for finding in verdict["findings"])


def test_trusted_1228_redirect_passes_without_treating_unchanged_date_as_claim(tmp_path: Path) -> None:
    contract, report, _before, after, repo = _trusted_redirect_fixture(tmp_path)
    old_row = f"| **Copilot Studio Message Capacity** | {REDIRECT_OLD_URL} | Jan 2026 |"
    new_row = f"| **Copilot Studio Message Capacity** | {REDIRECT_NEW_URL} | Jan 2026 |"
    diff = _redirect_diff(old_row, new_row)

    # This is the parent behavior: every `+` row was passed to claim-support, so the
    # unchanged `Jan 2026` table cell was mistaken for a newly authored claim.
    parent_findings = check_claim_support(parse_unified_diff(diff)[REDIRECT_PATH].added_lines, report)
    assert any(finding.check == "claim_support" for finding in parent_findings)

    verdict = verify(
        contract,
        diff,
        {REDIRECT_PATH: after},
        report,
        pr_body=REDIRECT_PR_BODY,
        repo_root=repo,
    )

    assert contract["fingerprint"] == REDIRECT_FINGERPRINT
    assert contract["report_path"] == REDIRECT_REPORT_PATH
    assert contract["classification"] == "REDIRECT"
    assert contract["source_url"] == REDIRECT_OLD_URL
    assert contract["destination_url"] == REDIRECT_NEW_URL
    assert contract["allowed_files"] == [REDIRECT_PATH]
    assert verdict["pass"] is True
    assert verdict["findings"] == []

    gate = autodoc_verify_gate.run_gate(
        contract,
        report,
        diff,
        {REDIRECT_PATH: after},
        pr_body=REDIRECT_PR_BODY,
        repo_root=repo,
    )
    assert gate["conclusion"] == "pass"


@pytest.mark.parametrize(
    "checkout_url",
    [REDIRECT_OLD_URL, REDIRECT_NEW_URL],
    ids=["checkout-before-redirect", "checkout-after-redirect"],
)
def test_trusted_redirect_fixture_is_independent_of_checkout_url_state(
    tmp_path: Path, checkout_url: str
) -> None:
    fixture_before = REDIRECT_BEFORE_FIXTURE.read_text(encoding="utf-8")
    checkout_content = fixture_before.replace(REDIRECT_OLD_URL, checkout_url, 1)
    trusted_repo_root = tmp_path / "trusted-base"
    checkout_path = trusted_repo_root / Path(*REDIRECT_PATH.split("/"))
    report_path = trusted_repo_root / Path(*REDIRECT_REPORT_PATH.split("/"))
    checkout_path.parent.mkdir(parents=True)
    report_path.parent.mkdir(parents=True)
    checkout_path.write_text(checkout_content, encoding="utf-8")
    report_path.write_text((PROJECT_ROOT / REDIRECT_REPORT_PATH).read_text(encoding="utf-8"), encoding="utf-8")

    contract, report, before, after, repo = _trusted_redirect_fixture(
        tmp_path / "verification",
        trusted_repo_root=trusted_repo_root,
    )
    old_row = f"| **Copilot Studio Message Capacity** | {REDIRECT_OLD_URL} | Jan 2026 |"
    new_row = f"| **Copilot Studio Message Capacity** | {REDIRECT_NEW_URL} | Jan 2026 |"
    verdict = verify(
        contract,
        _redirect_diff(old_row, new_row),
        {REDIRECT_PATH: after},
        report,
        pr_body=REDIRECT_PR_BODY,
        repo_root=repo,
    )

    checkout_text = checkout_path.read_text(encoding="utf-8")
    assert (REDIRECT_OLD_URL in checkout_text) is (checkout_url == REDIRECT_OLD_URL)
    assert (REDIRECT_NEW_URL in checkout_text) is (checkout_url == REDIRECT_NEW_URL)
    assert before == fixture_before
    assert REDIRECT_OLD_URL in before
    assert REDIRECT_NEW_URL in after
    assert verdict["pass"] is True


def test_trusted_redirect_rejects_changed_date_cell(tmp_path: Path) -> None:
    contract, report, _before, after, repo = _trusted_redirect_fixture(tmp_path)
    old_row = f"| **Copilot Studio Message Capacity** | {REDIRECT_OLD_URL} | Jan 2026 |"
    new_row = f"| **Copilot Studio Message Capacity** | {REDIRECT_NEW_URL} | Feb 2026 |"
    altered = after.replace(
        f"| **Copilot Studio Message Capacity** | {REDIRECT_NEW_URL} | Jan 2026 |",
        new_row,
        1,
    )

    verdict = verify(
        contract,
        _redirect_diff(old_row, new_row),
        {REDIRECT_PATH: altered},
        report,
        pr_body=REDIRECT_PR_BODY,
        repo_root=repo,
    )

    assert verdict["pass"] is False
    assert any(finding["check"] == "redirect_contract" for finding in verdict["findings"])


def test_trusted_redirect_rejects_changed_title_cell(tmp_path: Path) -> None:
    contract, report, _before, after, repo = _trusted_redirect_fixture(tmp_path)
    old_row = f"| **Copilot Studio Message Capacity** | {REDIRECT_OLD_URL} | Jan 2026 |"
    new_row = f"| **Unexpected Title** | {REDIRECT_NEW_URL} | Jan 2026 |"
    altered = after.replace(
        "| **Copilot Studio Message Capacity** |",
        "| **Unexpected Title** |",
        1,
    )

    verdict = verify(
        contract,
        _redirect_diff(old_row, new_row),
        {REDIRECT_PATH: altered},
        report,
        pr_body=REDIRECT_PR_BODY,
        repo_root=repo,
    )

    assert verdict["pass"] is False
    assert any(finding["check"] == "redirect_contract" for finding in verdict["findings"])


def test_trusted_redirect_rejects_added_prose(tmp_path: Path) -> None:
    contract, report, _before, after, repo = _trusted_redirect_fixture(tmp_path)
    old_row = f"| **Copilot Studio Message Capacity** | {REDIRECT_OLD_URL} | Jan 2026 |"
    new_row = f"| **Copilot Studio Message Capacity** | {REDIRECT_NEW_URL} | Jan 2026 |"
    altered = after + "\nNew unrelated prose.\n"

    verdict = verify(
        contract,
        _redirect_diff(old_row, new_row, "+New unrelated prose.\n"),
        {REDIRECT_PATH: altered},
        report,
        pr_body=REDIRECT_PR_BODY,
        repo_root=repo,
    )

    assert verdict["pass"] is False
    assert any(finding["check"] == "redirect_contract" for finding in verdict["findings"])


def test_trusted_redirect_rejects_unrelated_file(tmp_path: Path) -> None:
    contract, report, _before, after, repo = _trusted_redirect_fixture(tmp_path)
    old_row = f"| **Copilot Studio Message Capacity** | {REDIRECT_OLD_URL} | Jan 2026 |"
    new_row = f"| **Copilot Studio Message Capacity** | {REDIRECT_NEW_URL} | Jan 2026 |"
    unrelated_path = "docs/reference/unrelated.md"
    unrelated_diff = f"""diff --git a/{unrelated_path} b/{unrelated_path}
--- a/{unrelated_path}
+++ b/{unrelated_path}
@@ -1 +1 @@
-Existing.
+Changed.
"""

    verdict = verify(
        contract,
        _redirect_diff(old_row, new_row) + unrelated_diff,
        {REDIRECT_PATH: after, unrelated_path: "Changed.\n"},
        report,
        pr_body=REDIRECT_PR_BODY,
        repo_root=repo,
    )

    assert verdict["pass"] is False
    checks = {finding["check"] for finding in verdict["findings"]}
    assert {"path_allowlist", "redirect_contract"} <= checks


def test_trusted_redirect_rejects_widened_allowed_file_contract(tmp_path: Path) -> None:
    contract, report, _before, after, repo = _trusted_redirect_fixture(tmp_path)
    contract["allowed_files"].append("docs/reference/unrelated.md")
    old_row = f"| **Copilot Studio Message Capacity** | {REDIRECT_OLD_URL} | Jan 2026 |"
    new_row = f"| **Copilot Studio Message Capacity** | {REDIRECT_NEW_URL} | Jan 2026 |"

    verdict = verify(
        contract,
        _redirect_diff(old_row, new_row),
        {REDIRECT_PATH: after},
        report,
        pr_body=REDIRECT_PR_BODY,
        repo_root=repo,
    )

    assert verdict["pass"] is False
    assert any(
        finding["check"] == "redirect_contract" and "allow only" in finding["message"]
        for finding in verdict["findings"]
    )


def test_trusted_redirect_rejects_wrong_url_pair(tmp_path: Path) -> None:
    contract, report, _before, after, repo = _trusted_redirect_fixture(tmp_path)
    unexpected_url = "https://learn.microsoft.com/en-us/power-platform/admin/unexpected-capacity"
    old_row = f"| **Copilot Studio Message Capacity** | {REDIRECT_OLD_URL} | Jan 2026 |"
    new_row = f"| **Copilot Studio Message Capacity** | {unexpected_url} | Jan 2026 |"
    altered = after.replace(REDIRECT_NEW_URL, unexpected_url, 1)

    verdict = verify(
        contract,
        _redirect_diff(old_row, new_row),
        {REDIRECT_PATH: altered},
        report,
        pr_body=REDIRECT_PR_BODY,
        repo_root=repo,
    )

    assert verdict["pass"] is False
    assert any(
        finding["check"] == "redirect_contract" and "does not match" in finding["message"]
        for finding in verdict["findings"]
    )


def test_trusted_redirect_rejects_mismatched_fingerprint(tmp_path: Path) -> None:
    contract, report, _before, after, repo = _trusted_redirect_fixture(tmp_path)
    old_row = f"| **Copilot Studio Message Capacity** | {REDIRECT_OLD_URL} | Jan 2026 |"
    new_row = f"| **Copilot Studio Message Capacity** | {REDIRECT_NEW_URL} | Jan 2026 |"

    verdict = verify(
        contract,
        _redirect_diff(old_row, new_row),
        {REDIRECT_PATH: after},
        report,
        pr_body=REDIRECT_PR_BODY.replace(REDIRECT_FINGERPRINT, "sha256:wrong"),
        repo_root=repo,
    )

    assert verdict["pass"] is False
    assert any(finding["check"] == "fingerprint" for finding in verdict["findings"])


def test_language_blocks_banned_phrase(tmp_path: Path) -> None:
    repo = _lint_repo(tmp_path)
    target = repo / "docs" / "bad.md"
    target.write_text("# Bad\n\nThis guarantees compliance.\n", encoding="utf-8")

    findings = check_language(["docs/bad.md"], repo)

    assert findings
    assert findings[0].check == "language"
    assert findings[0].severity == "block"
    assert findings[0].path == "docs/bad.md"


def test_language_subprocess_exception_fails_closed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo = _lint_repo(tmp_path)

    def raise_subprocess_error(*_args: object, **_kwargs: object) -> None:
        raise OSError("boom")

    monkeypatch.setattr(autodoc_verify.subprocess, "run", raise_subprocess_error)

    findings = check_language(["docs/bad.md"], repo)

    assert len(findings) == 1
    assert findings[0].check == "language"
    assert findings[0].severity == "block"
    assert "failed closed" in findings[0].message


def test_language_starts_linter_from_relative_repo_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The linter must actually start when repo_root is a relative path.

    The workflow passes ``--head-dir .autodoc/head``. A relative script path handed to a
    child process running with ``cwd=repo_root`` is re-anchored against repo_root a second
    time, so the linter never launched and produced a spurious blocking finding.
    """

    repo = _lint_repo(tmp_path)
    target = repo / "docs" / "clean.md"
    target.write_text(REDIRECT_BEFORE_FIXTURE.read_text(encoding="utf-8"), encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    assert check_language(["docs/clean.md"], Path("repo")) == []


def test_language_reports_real_violations_from_relative_repo_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = _lint_repo(tmp_path)
    (repo / "docs" / "bad.md").write_text("# Bad\n\nThis guarantees compliance.\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    findings = check_language(["docs/bad.md"], Path("repo"))

    assert findings
    assert findings[0].check == "language"
    assert findings[0].severity == "block"
    assert findings[0].path == "docs/bad.md"
    assert "No such file or directory" not in findings[0].message


def test_workflow_gate_passes_trusted_redirect_from_relative_head_dir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Regression for PR #1228: the pull_request_target gate must pass the trusted redirect.

    Reproduces the workflow context end to end - base-code verifier, base-code language
    linter copied into ``.autodoc/head``, PR head Markdown in ``.autodoc/head``, and the
    relative ``--head-dir`` the workflow passes - rather than a pure-function approximation.
    """

    args = _workflow_runner_workspace(
        tmp_path,
        head_markdown=_redirect_head_markdown(),
        diff_text=_redirect_diff(REDIRECT_OLD_ROW, REDIRECT_NEW_ROW),
    )

    exit_code, result = _run_workflow_gate(tmp_path, args, monkeypatch)

    _assert_linter_started(result)
    assert result["deterministic"]["findings"] == []
    assert result["conclusion"] == "pass"
    assert exit_code == 0


@pytest.mark.parametrize(
    ("case", "new_row", "extra"),
    [
        (
            "second-cell-date",
            f"| **Copilot Studio Message Capacity** | {REDIRECT_NEW_URL} | Feb 2027 |",
            "",
        ),
        (
            "malformed-title-cell",
            f"| **Copilot Studio Message Capacity (Renamed)** | {REDIRECT_NEW_URL} | Jan 2026 |",
            "",
        ),
        (
            "extra-prose-line",
            REDIRECT_NEW_ROW,
            "+This update guarantees compliance for every regulated tenant.\n",
        ),
    ],
)
def test_workflow_gate_still_blocks_out_of_contract_edits_from_relative_head_dir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, case: str, new_row: str, extra: str
) -> None:
    """The relative-head-dir fix must not weaken any content constraint."""

    head_markdown = _redirect_head_markdown(new_row)
    if extra:
        head_markdown = f"{head_markdown}{extra[1:]}"

    args = _workflow_runner_workspace(
        tmp_path,
        head_markdown=head_markdown,
        diff_text=_redirect_diff(REDIRECT_OLD_ROW, new_row, extra),
    )

    exit_code, result = _run_workflow_gate(tmp_path, args, monkeypatch)

    _assert_linter_started(result)
    assert result["conclusion"] == "fail", case
    assert exit_code == 1, case
    assert result["deterministic"]["summary"]["block_findings"] >= 1, case


def test_workflow_gate_blocks_forged_fingerprint_from_relative_head_dir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    args = _workflow_runner_workspace(
        tmp_path,
        head_markdown=_redirect_head_markdown(),
        diff_text=_redirect_diff(REDIRECT_OLD_ROW, REDIRECT_NEW_ROW),
    )
    body_path = tmp_path / ".autodoc" / "pr-body.txt"
    body_path.write_bytes(REDIRECT_PR_BODY.replace(REDIRECT_FINGERPRINT, "sha256:forged").encode("utf-8"))

    exit_code, result = _run_workflow_gate(tmp_path, args, monkeypatch)

    _assert_linter_started(result)
    assert result["conclusion"] == "fail"
    assert exit_code == 1
    assert any(finding["check"] == "fingerprint" for finding in result["deterministic"]["findings"])


def test_verify_passes_clean_faithful_additive_edit(tmp_path: Path) -> None:
    repo = _lint_repo(tmp_path)
    target = repo / Path(*ALLOWED_PATH.split("/"))
    target.parent.mkdir(parents=True)
    content = "# Control\n\n## Additional Resources\nExisting.\n- Available starting March 2027.\n"
    target.write_text(content, encoding="utf-8")
    diff = _diff(ALLOWED_PATH, "- Available starting March 2027.")
    report = "The source monitoring report says this update is available starting March 2027."
    pr_body = "Autodoc update\n\nAUTODOC-FINGERPRINT: sha256:test\n"

    verdict = verify(_contract(), diff, {ALLOWED_PATH: content}, report, pr_body=pr_body, repo_root=repo)

    assert verdict["pass"] is True
    assert verdict["findings"] == []


def test_verify_blocks_empty_diff() -> None:
    verdict = verify(_contract(), "", {}, "")

    assert verdict["pass"] is False
    assert any(finding["check"] == "diff_parse" for finding in verdict["findings"])


def test_verify_blocks_combined_diff_touching_forbidden_path() -> None:
    diff = """diff --cc scripts/evil.py
index 0000000,1111111..2222222
--- a/scripts/evil.py
+++ b/scripts/evil.py
@@@ -1,1 -1,1 +1,2 @@@
++print("evil")
"""

    verdict = verify(_contract(), diff, {}, "")

    assert verdict["pass"] is False
    assert any("Combined diffs" in finding["message"] for finding in verdict["findings"])


def test_verify_blocks_non_git_diff_garbage_with_added_lines() -> None:
    diff = """not a unified git diff
+The data retention period is 90 days.
"""

    verdict = verify(_contract(), diff, {}, "The report says 90 days.")

    assert verdict["pass"] is False
    assert any("unparseable or unrecognized" in finding["message"] for finding in verdict["findings"])


def test_load_contract_raises_on_malformed_contract() -> None:
    with pytest.raises(ValueError):
        load_contract(
            {
                "schema_version": 1,
                "allowed_files": [ALLOWED_PATH],
                "allowed_headings": ["Additional Resources"],
                "forbidden_paths": ["scripts/**"],
            }
        )
