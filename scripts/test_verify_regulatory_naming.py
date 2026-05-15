"""Tests for ``scripts/verify_regulatory_naming.py``.

Covers (1) line/token unit tests for the prose check, (2) integration
tests against temporary files for the file walker (fences, H2 history
skipping, Markdown URL stripping), and (3) internal-link slug tests.

Convention enforced:

* First mention per page: ``OCC Bulletin 2026-13 (formerly OCC 2011-12)``.
* Subsequent mentions: short form ``OCC Bulletin 2026-13`` alone.
* Fed SR pattern: ``Fed SR 26-2 (formerly SR 11-7)``; short ``SR 26-2`` after.
* Shorthand ``OCC/SR`` is always wrong.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from verify_regulatory_naming import (  # noqa: E402
    BARE_OCC_RE,
    BARE_SR_RE,
    HISTORY_SECTION_RE,
    SHORTHAND_RE,
    STALE_SLUG_RE,
    check_internal_links,
    check_prose,
    find_formerly_spans,
    is_external_destination,
    is_inside_any_span,
    iter_lines_skipping_fences,
    strip_link_urls,
)

# ---------------------------------------------------------------------------
# Unit tests — pure regex behavior
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "line, expect_match",
    [
        ("OCC 2011-12", True),
        ("OCC Bulletin 2011-12", True),
        ("OCC  Bulletin   2011-12", True),  # Whitespace tolerance.
        ("occ 2011-12", True),  # Lowercase variant.
        ("OCC 2017-21", False),  # Different bulletin.
        ("OCC Bulletin 2026-13", False),
        ("SR 26-2", False),
    ],
)
def test_bare_occ_regex(line: str, expect_match: bool) -> None:
    assert bool(BARE_OCC_RE.search(line)) is expect_match


@pytest.mark.parametrize(
    "line, expect_match",
    [
        ("SR 11-7", True),
        ("sr 11-7", True),
        ("SR  11-7", True),
        ("SR 26-2", False),
        ("FINRA Rule 3110", False),
    ],
)
def test_bare_sr_regex(line: str, expect_match: bool) -> None:
    assert bool(BARE_SR_RE.search(line)) is expect_match


@pytest.mark.parametrize(
    "line, expect_match",
    [
        ("OCC/SR 11-7", True),
        ("OCC / SR 11-7", True),  # With spaces.
        ("OCC/SR 26-2", True),  # Even canonical 26-2 in shorthand is wrong.
        ("OCC/SR11-7", True),  # No space variant.
        ("OCC Bulletin 2026-13 / Fed SR 26-2", False),  # Explicit form OK.
        ("OCC", False),
    ],
)
def test_shorthand_regex(line: str, expect_match: bool) -> None:
    assert bool(SHORTHAND_RE.search(line)) is expect_match


@pytest.mark.parametrize(
    "line, expected_spans",
    [
        ("OCC Bulletin 2026-13 (formerly OCC 2011-12)", 1),
        ("(formerly SR 11-7)", 1),
        ("(banks; formerly OCC Bulletin 2011-12)", 1),  # Leading qualifier.
        ("(formerly SR 11-7; the 2026 supersession)", 1),  # Trailing.
        ("(formerly OCC 2011-12) and (formerly SR 11-7)", 2),  # Multiple.
        ("OCC 2011-12", 0),  # No formerly anywhere.
        ("(some other parenthetical)", 0),  # No 'formerly' inside.
    ],
)
def test_formerly_spans(line: str, expected_spans: int) -> None:
    assert len(find_formerly_spans(line)) == expected_spans


@pytest.mark.parametrize(
    "h2, expect_match",
    [
        ("Version History", True),
        ("Release History", True),
        ("Changelog", True),
        ("Prior Version Notes", True),
        ("version history", True),  # Case-insensitive.
        ("Overview", False),
        ("Regulatory Mapping", False),
    ],
)
def test_history_section_regex(h2: str, expect_match: bool) -> None:
    assert bool(HISTORY_SECTION_RE.search(h2)) is expect_match


# ---------------------------------------------------------------------------
# Helpers behavior
# ---------------------------------------------------------------------------


def test_is_inside_any_span() -> None:
    spans = [(5, 25), (40, 60)]
    assert is_inside_any_span(10, spans)
    assert is_inside_any_span(50, spans)
    assert not is_inside_any_span(0, spans)
    assert not is_inside_any_span(30, spans)
    assert not is_inside_any_span(60, spans)  # Right boundary exclusive.


def test_strip_link_urls_keeps_text() -> None:
    line = "See [Model Risk](../controls/2.6-model-risk-management-sr-26-2.md)"
    stripped = strip_link_urls(line)
    assert "Model Risk" in stripped
    assert "sr-26-2" not in stripped
    assert "()" in stripped


def test_strip_link_urls_multiple() -> None:
    line = "[A](one) and [B](two) text"
    assert strip_link_urls(line) == "[A]() and [B]() text"


def test_is_external_destination() -> None:
    assert is_external_destination("https://example.com/x")
    assert is_external_destination("http://example.com")
    assert is_external_destination("mailto:foo@bar.com")
    assert not is_external_destination("../relative.md")
    assert not is_external_destination("#anchor")
    assert not is_external_destination("./file.md#anchor")


# ---------------------------------------------------------------------------
# check_prose — line/token PASS cases
# ---------------------------------------------------------------------------


PASS_LINES = [
    "OCC Bulletin 2026-13 (formerly OCC 2011-12)",
    "OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12)",
    "Banks must comply with OCC Bulletin 2026-13 today.",  # Short-form alone.
    "Per SR 26-2, banks must validate models annually.",
    "Fed SR 26-2 (formerly SR 11-7)",
    "Federal Reserve SR 26-2 (formerly SR 11-7)",
    "OCC Bulletin 2026-13 §V (formerly OCC 2011-12 §V)",
    "OCC Bulletin 2026-13 / Fed SR 26-2",
    "OCC Bulletin 2026-13 / Federal Reserve SR 26-2",
    # Mixed formerly with leading/trailing context inside the parenthetical.
    "**OCC Bulletin 2026-13 (banks; formerly OCC Bulletin 2011-12) / "
    "Federal Reserve SR 26-2 (formerly SR 11-7; the 2026 supersession)**",
    # Two separate formerly spans on the same line — both inner mentions
    # are protected.
    "(formerly OCC 2011-12) and (formerly SR 11-7)",
    # Markdown link to canonical filename: URL stripped, link text scanned
    # but contains no stale form.
    "[Model Risk](../controls/pillar-2-management/"
    "2.6-model-risk-management-sr-26-2.md) covers...",
]


@pytest.mark.parametrize("line", PASS_LINES)
def test_pass_lines_via_temp_file(tmp_path: Path, line: str) -> None:
    """A file containing exactly this line must produce zero failures."""
    f = tmp_path / "watched.md"
    f.write_text(line + "\n", encoding="utf-8")
    assert check_prose(f) == [], (
        f"Expected PASS for line: {line!r}"
    )


# ---------------------------------------------------------------------------
# check_prose — line/token FAIL cases
# ---------------------------------------------------------------------------


FAIL_LINES = [
    # Bare standalone, no formerly anywhere.
    "Banks must comply with OCC Bulletin 2011-12 today.",
    "## OCC 2011-12 / SR 26-2",  # Section heading drift.
    "| OCC 2011-12 | Partial |",  # Table cell drift.
    "Per SR 11-7 §V, banks must validate models annually.",
    # Shorthand always wrong.
    "OCC/SR 11-7 mandates model validation.",
    "OCC/SR 26-2 (formerly SR 11-7)",  # Even with formerly suffix.
    "OCC / SR 11-7 mandates...",  # With spaces.
    "OCC/SR11-7 mandates...",  # No space.
    # Formerly somewhere on line is NOT enough — only same-line span
    # containment counts.
    "OCC Bulletin 2026-13 (formerly updated) and OCC 2011-12 lingers",
    # Two parts: inner span passes but second SR 11-7 is bare.
    "OCC Bulletin 2026-13 (formerly SR 11-7) and SR 11-7 remains relevant",
    # Lowercase variants.
    "occ 2011-12 was the prior bulletin.",
    "sr 11-7 was the prior fed letter.",
]


@pytest.mark.parametrize("line", FAIL_LINES)
def test_fail_lines_via_temp_file(tmp_path: Path, line: str) -> None:
    """A file containing this line must produce at least one failure."""
    f = tmp_path / "watched.md"
    f.write_text(line + "\n", encoding="utf-8")
    failures = check_prose(f)
    assert failures, f"Expected FAIL for line: {line!r}"


# ---------------------------------------------------------------------------
# Integration — file walker behavior (fences + H2 skips)
# ---------------------------------------------------------------------------


def test_fenced_code_block_skipped(tmp_path: Path) -> None:
    """Fenced code MUST be skipped even if it contains stale naming."""
    content = (
        "Some intro paragraph.\n"
        "\n"
        "```\n"
        "OCC 2011-12 raw quote\n"
        "SR 11-7 raw quote\n"
        "OCC/SR 11-7 raw quote\n"
        "```\n"
        "\n"
        "Trailing paragraph.\n"
    )
    f = tmp_path / "watched.md"
    f.write_text(content, encoding="utf-8")
    assert check_prose(f) == []


def test_history_h2_section_skipped(tmp_path: Path) -> None:
    """H2 'Version History' / 'Release History' / 'Changelog' / 'Prior
    Version' sections MUST be skipped — they accurately quote prior naming.
    """
    content = (
        "## Overview\n"
        "OCC Bulletin 2026-13 is canonical.\n"
        "\n"
        "## Version History\n"
        "- v1.5: cited OCC 2011-12 directly.\n"
        "- v1.4: cited SR 11-7 in the table.\n"
        "- v1.3: shorthand OCC/SR 11-7 was used.\n"
        "\n"
        "## Trailing\n"
        "OCC Bulletin 2026-13 is canonical.\n"
    )
    f = tmp_path / "watched.md"
    f.write_text(content, encoding="utf-8")
    assert check_prose(f) == []


def test_section_after_history_resumes_scanning(tmp_path: Path) -> None:
    """After exiting a history section, scanning MUST resume."""
    content = (
        "## Version History\n"
        "- v1.5: OCC 2011-12.\n"
        "\n"
        "## Current\n"
        "OCC 2011-12 should fail here.\n"
    )
    f = tmp_path / "watched.md"
    f.write_text(content, encoding="utf-8")
    failures = check_prose(f)
    assert len(failures) == 1
    assert ":5:" in failures[0]


def test_iter_lines_tracks_h2() -> None:
    text = (
        "# Top\nintro\n## SecA\nbody\n## Version History\nold\n"
        "## SecB\nbody\n"
    )
    lines = list(iter_lines_skipping_fences(text))
    h2_by_lineno = {ln: h2 for ln, _, h2 in lines}
    assert h2_by_lineno[2] is None  # Under H1.
    assert h2_by_lineno[4] == "SecA"
    assert h2_by_lineno[6] == "Version History"
    assert h2_by_lineno[8] == "SecB"


def test_multiline_formerly_does_not_protect(tmp_path: Path) -> None:
    """Per design, the formerly-span MUST be on the same rendered line as
    the bare reference. Multi-line parentheticals are NOT supported.
    """
    content = "OCC Bulletin 2026-13\n(formerly OCC 2011-12)\n"
    f = tmp_path / "watched.md"
    f.write_text(content, encoding="utf-8")
    failures = check_prose(f)
    # The bare 'OCC 2011-12' on line 2 sits inside its own same-line
    # parenthetical (line 2 = '(formerly OCC 2011-12)') so it actually
    # PASSES under our same-line rule. This documents the behavior.
    assert failures == []


def test_link_text_with_stale_form_fails(tmp_path: Path) -> None:
    """Stale naming inside link TEXT (not URL) MUST be flagged."""
    content = "[OCC 2011-12 guidance](https://example.com/foo) is here.\n"
    f = tmp_path / "watched.md"
    f.write_text(content, encoding="utf-8")
    failures = check_prose(f)
    assert len(failures) == 1
    assert "2011-12" in failures[0]


def test_link_url_with_stale_slug_does_not_fire_prose(tmp_path: Path) -> None:
    """Stale naming inside link URL MUST NOT fire the prose check (the
    internal-link check handles destinations separately).
    """
    content = "[Model Risk](https://example.com/old/sr-11-7-doc) is here.\n"
    f = tmp_path / "watched.md"
    f.write_text(content, encoding="utf-8")
    failures = check_prose(f)
    assert failures == []


# ---------------------------------------------------------------------------
# check_internal_links — destination slug scanning
# ---------------------------------------------------------------------------


def test_internal_link_with_stale_slug_fails(tmp_path: Path) -> None:
    content = (
        "See [Model Risk](../controls/pillar-2-management/"
        "2.6-model-risk-management-occ-2011-12.md).\n"
    )
    f = tmp_path / "watched.md"
    f.write_text(content, encoding="utf-8")
    failures = check_internal_links(f)
    assert len(failures) == 1
    assert "occ-2011-12" in failures[0].lower()


def test_internal_link_with_canonical_slug_passes(tmp_path: Path) -> None:
    content = (
        "See [Model Risk](../controls/pillar-2-management/"
        "2.6-model-risk-management-sr-26-2.md).\n"
    )
    f = tmp_path / "watched.md"
    f.write_text(content, encoding="utf-8")
    assert check_internal_links(f) == []


def test_internal_link_anchor_with_stale_slug_fails(tmp_path: Path) -> None:
    content = "See [section](#occ-bulletin-2011-12-supersession).\n"
    f = tmp_path / "watched.md"
    f.write_text(content, encoding="utf-8")
    failures = check_internal_links(f)
    assert failures, "Stale anchor must be flagged"


def test_external_link_with_stale_slug_passes(tmp_path: Path) -> None:
    """External URLs are out of scope (third-party content; cannot
    enforce naming on URLs we don't control)."""
    content = "See [OCC archive](https://example.com/sr-11-7-archive).\n"
    f = tmp_path / "watched.md"
    f.write_text(content, encoding="utf-8")
    assert check_internal_links(f) == []


# ---------------------------------------------------------------------------
# Stale slug regex
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "slug, expect_match",
    [
        ("occ-2011-12", True),
        ("occ-bulletin-2011-12", True),
        ("sr-11-7", True),
        ("occ-sr-11-7", True),
        ("occ_2011_12", True),  # Underscore variant.
        ("sr-26-2", False),  # Canonical filename slug.
        ("occ-bulletin-2026-13", False),  # Canonical.
        ("sr-26-2-something", False),  # Canonical embedded.
    ],
)
def test_stale_slug_regex(slug: str, expect_match: bool) -> None:
    assert bool(STALE_SLUG_RE.search(slug)) is expect_match
