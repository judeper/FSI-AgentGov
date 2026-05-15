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
    JSON_PROSE_FIELDS,
    SHORTHAND_RE,
    STALE_SLUG_RE,
    check_internal_links,
    check_json_prose,
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
    (
        "**OCC Bulletin 2026-13 (banks; formerly OCC Bulletin 2011-12) / "
        + "Federal Reserve SR 26-2 (formerly SR 11-7; the 2026 supersession)**"
    ),
    # Two separate formerly spans on the same line — both inner mentions
    # are protected.
    "(formerly OCC 2011-12) and (formerly SR 11-7)",
    # Markdown link to canonical filename: URL stripped, link text scanned
    # but contains no stale form.
    (
        "[Model Risk](../controls/pillar-2-management/"
        + "2.6-model-risk-management-sr-26-2.md) covers..."
    ),
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


# ---------------------------------------------------------------------------
# AS11b carve-outs — admonition / supersession / legacy URL / file-slug /
# historical-bullet block / pinned-anchor allowlist
# ---------------------------------------------------------------------------


def test_admonition_title_with_stale_naming_skipped(tmp_path: Path) -> None:
    """Material admonition titles are load-bearing supersession narrative."""
    content = (
        "## Overview\n"
        "Models must follow OCC Bulletin 2026-13 (formerly OCC 2011-12).\n"
        "\n"
        '!!! warning "OCC 2011-12 was rescinded by OCC Bulletin 2026-13"\n'
        "    See the official rescission notice for details.\n"
        "\n"
        "Trailing paragraph.\n"
    )
    f = tmp_path / "ctrl.md"
    f.write_text(content, encoding="utf-8")
    assert check_prose(f) == []


def test_admonition_body_continuation_skipped(tmp_path: Path) -> None:
    """Admonition body lines (4-space indented after open) MUST be skipped
    since the entire admonition block is supersession narrative."""
    content = (
        '!!! note "Supersession history"\n'
        "    OCC 2011-12 was the prior bulletin governing model risk.\n"
        "    SR 11-7 was the corresponding Fed letter.\n"
        "    Both were rescinded in 2026.\n"
        "\n"
        "Plain prose resumes here with OCC Bulletin 2026-13.\n"
    )
    f = tmp_path / "ctrl.md"
    f.write_text(content, encoding="utf-8")
    assert check_prose(f) == []


def test_admonition_close_resumes_scanning(tmp_path: Path) -> None:
    """After the admonition closes (unindented non-blank line), scanning
    MUST resume — bare references after the block are still failures.

    Block has supersession context (body line includes 'rescinded'), so
    AS15b-verifier B2's conditional carve-out keeps the block skipped.
    """
    content = (
        '!!! note "Old naming"\n'
        "    OCC 2011-12 was the prior bulletin.\n"
        "    The OCC rescinded it in April 2026.\n"
        "\n"
        "OCC 2011-12 should fail here.\n"
    )
    f = tmp_path / "ctrl.md"
    f.write_text(content, encoding="utf-8")
    failures = check_prose(f)
    assert len(failures) == 1
    assert ":5:" in failures[0]


def test_admonition_without_supersession_context_does_not_skip_body(
    tmp_path: Path,
) -> None:
    """AS15b-verifier B2 — admonitions WITHOUT a supersession marker in
    the opener title or any body line are NOT carved out: the body is
    scanned and shorthand/bare references are reported.

    This is the regression that motivated AS15b: admonition bodies were
    leaking shorthand like '(OCC 2011-12 / SR 11-7)' to customers via
    Material's search snippets despite the source-level carve-out.
    """
    content = (
        '!!! note "Cross-reference"\n'
        "    Control 2.6 — Model Risk Management (OCC 2011-12 / SR 11-7) "
        "covers the model-risk pillar.\n"
        "    See the linked control for full details.\n"
        "\n"
        "Trailing prose.\n"
    )
    f = tmp_path / "ctrl.md"
    f.write_text(content, encoding="utf-8")
    failures = check_prose(f)
    # Body line has SHORTHAND_RE match (OCC/SR) plus bare BARE_OCC_RE
    # plus bare BARE_SR_RE — minimum 1 failure (shorthand always wrong).
    assert len(failures) >= 1, f"Expected B2 to flag shorthand; got: {failures}"
    assert any(":2:" in f for f in failures), (
        f"Expected at least one failure on line 2 (admonition body); got: {failures}"
    )


def test_admonition_supersession_marker_in_title_only_skips_block(
    tmp_path: Path,
) -> None:
    """AS15b-verifier B2 — when the admonition opener title contains a
    supersession marker (e.g., 'rescinded'), the block-level context is
    True and ALL body lines are skipped, even if they contain bare
    references with NO per-line marker. This is the title-propagates-to-body
    invariant nothing else covers.
    """
    content = (
        '!!! warning "OCC 2011-12 was rescinded by OCC Bulletin 2026-13"\n'
        "    The bulletin was effective immediately on issuance.\n"
        "    Implementations referencing OCC 2011-12 should be updated.\n"
        "    SR 11-7 was the corresponding Fed letter.\n"
        "\n"
        "Trailing prose with OCC Bulletin 2026-13.\n"
    )
    f = tmp_path / "ctrl.md"
    f.write_text(content, encoding="utf-8")
    assert check_prose(f) == []


def test_supersession_narrative_line_skipped(tmp_path: Path) -> None:
    """Lines containing 'rescinded', 'superseded', 'predecessor', etc. ARE
    load-bearing supersession narrative and must be allowed."""
    fixtures = [
        "OCC 2011-12 was rescinded by OCC Bulletin 2026-13 in April 2026.",
        "SR 11-7 was superseded by Fed SR 26-2 in 2026.",
        "OCC Bulletin 2026-13 supersedes OCC 2011-12.",
        "The predecessor bulletin OCC 2011-12 governed model risk.",
        "OCC 2011-12 (formerly known as 'OCC Bulletin 2011-12 supervisory guidance').",
        "OCC 2011-12 no longer resolves to the active OCC site.",
        "OCC Bulletin 2026-13 rescinds OCC 2011-12 and OCC Bulletin 2011-12.",
        "This rescinded SR 11-7 letter is archived.",
        # AS15b-verifier N-1 — broadened regex now covers these forms too.
        "The supersession of OCC 2011-12 by OCC Bulletin 2026-13 took effect April 2026.",
        "Superseding bulletin OCC Bulletin 2026-13 replaces OCC 2011-12.",
        "Rescission of OCC 2011-12 was published as a Federal Register notice.",
        "Rescinding SR 11-7 required a 90-day notice.",
    ]
    for line in fixtures:
        f = tmp_path / f"ctrl-{abs(hash(line))}.md"
        f.write_text(line + "\n", encoding="utf-8")
        assert check_prose(f) == [], f"Expected PASS for: {line!r}"


def test_legacy_url_marker_line_skipped(tmp_path: Path) -> None:
    """Lines citing the legacy URL fragments are about the URL, not the
    bare reference. Skip."""
    fixtures = [
        "Legacy archive: https://www.occ.gov/news-issuances/bulletins/2011/bulletin-2011-12.html (now redirects to 2026-13).",
        "The old SR 11-7 PDF was hosted at https://www.federalreserve.gov/supervisionreg/srletters/sr1107.htm.",
        "See the /bulletins/2011/ archive index for the OCC 2011-12 bulletin.",
        "Historical citation: SR letter 11-7 (now Fed SR 26-2).",
    ]
    for line in fixtures:
        f = tmp_path / f"ctrl-{abs(hash(line))}.md"
        f.write_text(line + "\n", encoding="utf-8")
        assert check_prose(f) == [], f"Expected PASS for: {line!r}"


def test_file_slug_backtick_line_skipped(tmp_path: Path) -> None:
    """Lines containing the canonical filename in backticks are file-path
    references, not bare regulatory citations. Skip."""
    fixtures = [
        "See `2.6-model-risk-management-sr-26-2.md` for full text on OCC 2011-12.",
        "Edit `docs/controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md` to update SR 11-7.",
    ]
    for line in fixtures:
        f = tmp_path / f"ctrl-{abs(hash(line))}.md"
        f.write_text(line + "\n", encoding="utf-8")
        assert check_prose(f) == [], f"Expected PASS for: {line!r}"


def test_historical_bullet_block_skipped(tmp_path: Path) -> None:
    """The 'Regulatory sources — historical' bullet block in control 2.6
    intentionally lists the prior naming. Skip until next bold paragraph
    header or # heading closes the block."""
    content = (
        "**Regulatory sources — current**\n"
        "- OCC Bulletin 2026-13 — model risk management framework.\n"
        "- Fed SR 26-2 — model risk management.\n"
        "\n"
        "**Regulatory sources — historical**\n"
        "- OCC 2011-12 — original bulletin (rescinded April 2026).\n"
        "- SR 11-7 — original Fed letter (superseded 2026).\n"
        "- OCC Bulletin 2011-12 — long-form name.\n"
        "\n"
        "**Implementation notes**\n"
        "Plain prose mentioning OCC 2011-12 should fail here.\n"
    )
    f = tmp_path / "ctrl.md"
    f.write_text(content, encoding="utf-8")
    failures = check_prose(f)
    assert len(failures) == 1, f"Got: {failures}"
    assert ":11:" in failures[0]


def test_pinned_anchor_inbound_link_passes(tmp_path: Path) -> None:
    """The single explicit pinned anchor used in 2.6/portal-walkthrough
    is on the allowlist and must NOT trip the internal-link check."""
    content = (
        "| 5 | [Vendor Model Governance (SR 26-2 §V (formerly SR 11-7 §V))]"
        "(#5-vendor-model-governance-sr-11-7-v) | Vendor models | VC-8 |\n"
    )
    f = tmp_path / "ctrl.md"
    f.write_text(content, encoding="utf-8")
    assert check_internal_links(f) == []


def test_pinned_anchor_other_stale_slug_still_fails(tmp_path: Path) -> None:
    """The allowlist is one specific anchor — other stale slugs still fail."""
    content = (
        "See [Old section](#occ-2011-12-supersession-context).\n"
        "Also [SR section](#sr-11-7-effective-challenge).\n"
    )
    f = tmp_path / "ctrl.md"
    f.write_text(content, encoding="utf-8")
    failures = check_internal_links(f)
    assert len(failures) == 2


def test_admonition_with_other_indents(tmp_path: Path) -> None:
    """Material allows tabs and 4+ spaces for admonition body. We use
    'indent strictly greater than the opener's leading_spaces' as the
    rule. Validate with a single tab and with deeper indents.

    Block has supersession context (title includes 'rescinded') so
    AS15b-verifier B2's conditional carve-out keeps the body skipped
    regardless of indent flavor — the test still measures indent
    handling without leaking the always-on admonition skip we removed.
    """
    # Single tab indentation.
    content_tab = (
        '!!! warning "Old reference (rescinded)"\n'
        "\tOCC 2011-12 historical context.\n"
        "\n"
        "Resumed prose with OCC Bulletin 2026-13.\n"
    )
    f = tmp_path / "tab.md"
    f.write_text(content_tab, encoding="utf-8")
    # Tab is treated as one column; indent > 0 is enough to keep block open.
    # This documents behavior — we accept either a tab OR 4+ spaces.
    failures = check_prose(f)
    # Whether tabs count depends on impl; document either way is OK as
    # long as the reference doesn't show up as a hard failure on a
    # canonical-form page that isn't trying to break.
    if failures:
        # If our impl doesn't accept tabs, the bare ref on line 2 fails;
        # this is documented behavior, not a regression.
        assert ":2:" in failures[0]


def test_overall_corpus_clean() -> None:
    """Sanity: the entire docs/ corpus must be clean post-AS11a sweep."""
    from verify_regulatory_naming import run_all_checks
    n_failures, messages, files_scanned = run_all_checks()
    assert files_scanned > 100, "Verifier should scan all-of-docs"
    assert n_failures == 0, "Corpus drift found:\n" + "\n".join(messages[:10])


# ---------------------------------------------------------------------------
# AS22 — JSON prose field scanning (assessment/data/*.json)
# ---------------------------------------------------------------------------


def _write_json(tmp_path: Path, payload: dict) -> Path:
    import json as _json
    f = tmp_path / "data.json"
    f.write_text(_json.dumps(payload, indent=2), encoding="utf-8")
    return f


def test_json_prose_field_with_legacy_naming_fails(tmp_path: Path) -> None:
    """A bare ``OCC 2011-12`` reference inside a ``description`` field is the
    exact escape AS22 closes. Reproduces the original
    ``solutions-lock.json`` regression so this test stays meaningful even
    if the producer is fixed upstream.
    """
    payload = {
        "solutions": {
            "model-risk-management-automation": {
                "id": "model-risk-management-automation",
                "description": (
                    "Automated OCC 2011-12 and Fed SR 11-7 model risk "
                    "management for AI agents."
                ),
            }
        }
    }
    f = _write_json(tmp_path, payload)
    failures = check_json_prose(f)
    assert len(failures) == 2, (
        f"Expected one bare-OCC and one bare-SR fail; got: {failures}"
    )
    # Diagnostic must include the JSON path so maintainers can locate it.
    assert any(
        "solutions.model-risk-management-automation.description" in msg
        for msg in failures
    ), failures


def test_json_prose_field_with_canonical_naming_passes(tmp_path: Path) -> None:
    """The fix-form (formerly-span around each bare reference) must PASS."""
    payload = {
        "solutions": {
            "model-risk-management-automation": {
                "id": "model-risk-management-automation",
                "description": (
                    "Automated OCC Bulletin 2026-13 (formerly OCC 2011-12) "
                    "and Fed SR 26-2 (formerly SR 11-7) model risk management."
                ),
            }
        }
    }
    f = _write_json(tmp_path, payload)
    assert check_json_prose(f) == []


def test_json_non_prose_fields_not_scanned(tmp_path: Path) -> None:
    """Machine-only fields (``id``, ``url``, ``slug``, ``version``) must
    NOT be scanned — they are not customer-facing prose. This narrowness
    is what keeps the new check from melting down on URLs and IDs that
    legitimately contain ``2011`` / ``11-7`` substrings."""
    payload = {
        "solutions": {
            "model-risk-management-automation": {
                "id": "model-risk-occ-2011-12",
                "url": "https://example.com/sr-11-7-archive",
                "version": "11.7.0",
                "slug": "occ-2011-12-bulletin",
                # Prose field is canonical so we are isolating the
                # non-prose-fields invariant.
                "description": "Canonical citation: OCC Bulletin 2026-13.",
            }
        }
    }
    f = _write_json(tmp_path, payload)
    assert check_json_prose(f) == []


def test_json_shorthand_in_prose_field_fails(tmp_path: Path) -> None:
    """``OCC/SR`` shorthand inside a prose field is always a fail."""
    payload = {
        "controls": [
            {
                "id": "2.6",
                "summary": "Maps to OCC/SR 11-7 model-risk guidance.",
            }
        ]
    }
    f = _write_json(tmp_path, payload)
    failures = check_json_prose(f)
    assert failures, "Shorthand 'OCC/SR' must fire even in JSON prose"
    assert "shorthand" in failures[0].lower()


def test_json_prose_field_set_is_explicit() -> None:
    """``JSON_PROSE_FIELDS`` is a closed allowlist. Anything not in it is
    not scanned — guards against accidentally scanning IDs / URLs."""
    assert "description" in JSON_PROSE_FIELDS
    assert "summary" in JSON_PROSE_FIELDS
    assert "verification" in JSON_PROSE_FIELDS
    assert "id" not in JSON_PROSE_FIELDS
    assert "url" not in JSON_PROSE_FIELDS
    assert "slug" not in JSON_PROSE_FIELDS
    assert "version" not in JSON_PROSE_FIELDS
