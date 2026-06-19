"""Tests for the deterministic autodoc verifier."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import autodoc_verify  # noqa: E402
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
