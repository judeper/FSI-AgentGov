"""Tests for the independent autodoc redirect CI verifier."""

from __future__ import annotations

import autodoc_redirect_ci_verify as v
import pytest

TARGET = "docs/reference/microsoft-learn-urls.md"
OLD = "https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/architecture/"
NEW = "https://learn.microsoft.com/en-us/agents/architecture/"


def _diff(removed: str, added: str, file: str = TARGET) -> str:
    return (
        f"diff --git a/{file} b/{file}\n"
        "index 1111111..2222222 100644\n"
        f"--- a/{file}\n"
        f"+++ b/{file}\n"
        "@@ -97 +97 @@\n"
        f"-{removed}\n"
        f"+{added}\n"
    )


def _row(url: str, title: str = "Architecting Agent Solutions", date: str = "Mar 2026") -> str:
    return f"| {title} | {url} | {date} |"


def test_clean_swap_returns_urls() -> None:
    old, new = v.verify_redirect_diff(_diff(_row(OLD), _row(NEW)))
    assert (old, new) == (OLD, NEW)


def test_rejects_wrong_file() -> None:
    diff = _diff(_row(OLD), _row(NEW), file="docs/controls/pillar-1-security/1.6-x.md")
    with pytest.raises(v.NotCleanRedirect, match="touch only"):
        v.verify_redirect_diff(diff)


def test_rejects_multiple_files() -> None:
    diff = _diff(_row(OLD), _row(NEW)) + _diff(_row(OLD), _row(NEW), file="docs/other.md")
    with pytest.raises(v.NotCleanRedirect, match="touch only"):
        v.verify_redirect_diff(diff)


def test_rejects_two_removed_lines() -> None:
    diff = (
        f"diff --git a/{TARGET} b/{TARGET}\n--- a/{TARGET}\n+++ b/{TARGET}\n@@ -97,2 +97,2 @@\n"
        f"-{_row(OLD)}\n-{_row(OLD, title='Other')}\n+{_row(NEW)}\n+{_row(NEW, title='Other')}\n"
    )
    with pytest.raises(v.NotCleanRedirect, match="exactly 1 removed"):
        v.verify_redirect_diff(diff)


def test_rejects_hidden_removed_dashes_line() -> None:
    # A removed content line whose text is "---" appears as "----"; a naive parser
    # that skips lines starting with "---" would drop it, hiding an extra deletion.
    diff = (
        f"diff --git a/{TARGET} b/{TARGET}\n--- a/{TARGET}\n+++ b/{TARGET}\n"
        "@@ -10 +9,0 @@\n----\n"
        f"@@ -42 +42 @@\n-{_row(OLD)}\n+{_row(NEW)}\n"
    )
    with pytest.raises(v.NotCleanRedirect, match="exactly 1 removed"):
        v.verify_redirect_diff(diff)


def test_rejects_hidden_added_pluses_line() -> None:
    # An added content line whose text starts with "++" appears as "+++..."; a naive
    # parser that skips lines starting with "+++" would drop it, hiding an addition.
    diff = (
        f"diff --git a/{TARGET} b/{TARGET}\n--- a/{TARGET}\n+++ b/{TARGET}\n"
        "@@ -10,0 +10 @@\n+++ injected table junk\n"
        f"@@ -42 +42 @@\n-{_row(OLD)}\n+{_row(NEW)}\n"
    )
    with pytest.raises(v.NotCleanRedirect, match="exactly 1 removed|1 added"):
        v.verify_redirect_diff(diff)


def test_rejects_hidden_second_file_after_hunk() -> None:
    # A second file's changes appended after the first file's hunk must be detected
    # via its own `diff --git` header, not absorbed as hunk content.
    diff = _diff(_row(OLD), _row(NEW)) + (
        "diff --git a/docs/controls/pillar-1-security/1.6-x.md b/docs/controls/pillar-1-security/1.6-x.md\n"
        "--- a/docs/controls/pillar-1-security/1.6-x.md\n+++ b/docs/controls/pillar-1-security/1.6-x.md\n"
        "@@ -1 +1 @@\n-old line\n+new line\n"
    )
    with pytest.raises(v.NotCleanRedirect, match="touch only"):
        v.verify_redirect_diff(diff)


def test_rejects_extra_cell_change() -> None:
    # URL changed AND date changed -> two differing cells -> reject.
    with pytest.raises(v.NotCleanRedirect, match="exactly one URL cell"):
        v.verify_redirect_diff(_diff(_row(OLD, date="Mar 2026"), _row(NEW, date="Apr 2026")))


def test_rejects_non_table_line() -> None:
    with pytest.raises(v.NotCleanRedirect, match="table rows"):
        v.verify_redirect_diff(_diff(f"See {OLD} for details", f"See {NEW} for details"))


def test_rejects_non_url_cell() -> None:
    # The differing cell is the Title, whose value is not a URL.
    removed = _row(OLD).replace("Architecting Agent Solutions", "Architecting")
    with pytest.raises(v.NotCleanRedirect, match="not a well-formed URL"):
        v.verify_redirect_diff(_diff(removed, _row(OLD)))


def test_rejects_url_cell_with_trailing_junk() -> None:
    # A pipe-broken / junk URL cell (table-breaking char) is not well-formed.
    bad_new = NEW + " (preview)"
    with pytest.raises(v.NotCleanRedirect, match="not a well-formed URL"):
        v.verify_redirect_diff(_diff(_row(OLD), _row(bad_new)))


def test_rejects_identical_urls() -> None:
    with pytest.raises(v.NotCleanRedirect, match="exactly one URL cell|identical"):
        v.verify_redirect_diff(_diff(_row(OLD), _row(OLD)))


def test_rejects_cell_count_mismatch() -> None:
    removed = _row(OLD)
    added = _row(NEW) + " extra |"
    with pytest.raises(v.NotCleanRedirect, match="cell counts"):
        v.verify_redirect_diff(_diff(removed, added))


def test_main_clean(tmp_path, capsys) -> None:
    p = tmp_path / "pr.diff"
    p.write_text(_diff(_row(OLD), _row(NEW)), encoding="utf-8")
    assert v.main(["--diff", str(p)]) == 0
    assert "clean redirect swap" in capsys.readouterr().out


def test_main_not_clean(tmp_path) -> None:
    p = tmp_path / "pr.diff"
    p.write_text(_diff(_row(OLD, date="Mar 2026"), _row(NEW, date="Apr 2026")), encoding="utf-8")
    assert v.main(["--diff", str(p)]) == 2


def test_main_missing_diff(tmp_path) -> None:
    assert v.main(["--diff", str(tmp_path / "nope.diff")]) == 1
