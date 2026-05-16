"""Tests for verify_meta_tags.py — the post-build OpenGraph + Twitter
Card meta gate.

Closes F-DOCS-OG-TWITTER-CARDS-MISSING-01 (AS16). Each test materializes
a tiny site/ tree under tmp_path with a single sampled HTML file and
asserts the verifier flags (or accepts) the page correctly.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Make scripts/ importable regardless of pytest invocation directory.
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import verify_meta_tags  # noqa: E402


def _full_meta_block(title: str = "Test Page", desc: str = "Test desc",
                     url: str = "https://example.com/p/") -> str:
    """Return a complete OG + Twitter meta block — passes verifier."""
    return f"""
<!doctype html><html><head>
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Site">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
</head><body></body></html>
"""


def _materialize(site: Path, files: dict[str, str]) -> None:
    """Write each {rel: html} under site/, creating parent dirs."""
    for rel, body in files.items():
        target = site / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body, encoding="utf-8")


# -- Positive cases (must NOT be reported) -----------------------------------

def test_full_meta_block_passes(tmp_path: Path):
    """All required meta present on all sampled pages -> empty result."""
    files = {rel: _full_meta_block() for rel in verify_meta_tags.SAMPLED_PAGES}
    _materialize(tmp_path, files)
    result = verify_meta_tags.scan(tmp_path)
    assert result == {}, f"Expected no failures, got: {result}"


def test_meta_with_attribute_order_reversed_passes(tmp_path: Path):
    """content="..." before property/name attribute also accepted."""
    page = """<!doctype html><html><head>
<meta content="Test" property="og:title">
<meta content="Desc" property="og:description">
<meta content="https://x.test/" property="og:url">
<meta content="website" property="og:type">
<meta content="Site" property="og:site_name">
<meta content="summary" name="twitter:card">
<meta content="Test" name="twitter:title">
<meta content="Desc" name="twitter:description">
</head><body></body></html>"""
    files = {rel: page for rel in verify_meta_tags.SAMPLED_PAGES}
    _materialize(tmp_path, files)
    result = verify_meta_tags.scan(tmp_path)
    assert result == {}, f"Expected no failures, got: {result}"


def test_meta_with_extra_attributes_passes(tmp_path: Path):
    """Unrelated meta tags + classes/ids on the meta element are OK."""
    page = _full_meta_block().replace(
        '<meta property="og:title"',
        '<meta data-instrument="x" property="og:title"',
    )
    files = {rel: page for rel in verify_meta_tags.SAMPLED_PAGES}
    _materialize(tmp_path, files)
    result = verify_meta_tags.scan(tmp_path)
    assert result == {}


# -- Negative cases (must be reported) ---------------------------------------

def test_missing_og_title_reported(tmp_path: Path):
    """Removing og:title produces a failure on the affected page."""
    page = _full_meta_block().replace(
        '<meta property="og:title" content="Test Page">', "",
    )
    files = {rel: page for rel in verify_meta_tags.SAMPLED_PAGES}
    _materialize(tmp_path, files)
    result = verify_meta_tags.scan(tmp_path)
    assert len(result) == len(verify_meta_tags.SAMPLED_PAGES), (
        f"Expected all sampled pages to fail; got {result}"
    )
    for failures in result.values():
        assert any("og:title" in f for f in failures)


def test_empty_content_attribute_reported(tmp_path: Path):
    """og:description with content="" must fail (empty != absent)."""
    page = _full_meta_block().replace(
        '<meta property="og:description" content="Test desc">',
        '<meta property="og:description" content="">',
    )
    files = {rel: page for rel in verify_meta_tags.SAMPLED_PAGES}
    _materialize(tmp_path, files)
    result = verify_meta_tags.scan(tmp_path)
    for failures in result.values():
        assert any(
            "og:description" in f and "empty" in f for f in failures
        ), f"Expected empty-content message; got {failures}"


def test_missing_sampled_page_reported(tmp_path: Path):
    """If a sampled page doesn't exist on disk, the verifier reports it."""
    # Materialize only the homepage; the deep playbook + reference page
    # are missing.
    _materialize(tmp_path, {verify_meta_tags.SAMPLED_PAGES[0]: _full_meta_block()})
    result = verify_meta_tags.scan(tmp_path)
    assert len(result) == 2, (
        f"Expected 2 missing-page failures; got {result}"
    )
    for failures in result.values():
        assert any("not found" in f for f in failures)


def test_missing_twitter_card_reported(tmp_path: Path):
    """twitter:card is required - removing it fails."""
    page = _full_meta_block().replace(
        '<meta name="twitter:card" content="summary">', "",
    )
    files = {rel: page for rel in verify_meta_tags.SAMPLED_PAGES}
    _materialize(tmp_path, files)
    result = verify_meta_tags.scan(tmp_path)
    for failures in result.values():
        assert any("twitter:card" in f for f in failures)


def test_whitespace_only_content_treated_as_empty(tmp_path: Path):
    """content="   " is treated as empty (string-strip is empty)."""
    page = _full_meta_block().replace(
        '<meta property="og:url" content="https://example.com/p/">',
        '<meta property="og:url" content="   ">',
    )
    files = {rel: page for rel in verify_meta_tags.SAMPLED_PAGES}
    _materialize(tmp_path, files)
    result = verify_meta_tags.scan(tmp_path)
    for failures in result.values():
        assert any("og:url" in f and "empty" in f for f in failures)


# -- Schema sanity -----------------------------------------------------------

def test_required_meta_schema_locked():
    """Lock the REQUIRED_META schema so a contributor can't accidentally
    drop or rename a tag without the test catching it."""
    expected = {
        ("property", "og:title"),
        ("property", "og:description"),
        ("property", "og:url"),
        ("property", "og:type"),
        ("property", "og:site_name"),
        ("name", "twitter:card"),
        ("name", "twitter:title"),
        ("name", "twitter:description"),
    }
    assert set(verify_meta_tags.REQUIRED_META) == expected


def test_sampled_pages_cover_three_distinct_paths():
    """Sampled pages must cover homepage + a deep page + a reference page."""
    assert len(verify_meta_tags.SAMPLED_PAGES) == 3
    pages = list(verify_meta_tags.SAMPLED_PAGES)
    assert pages[0] == "index.html"  # homepage
    # All three should be distinct
    assert len(set(pages)) == 3


# -- Built-site integration -------------------------------------------------

def test_built_site_passes_when_present():
    """If a built site/ directory is present, verify it passes the gate.

    Skipped when running before mkdocs build (e.g., on a fresh clone).
    Acts as a real-world integration check when mkdocs build has run.
    """
    repo_root = Path(__file__).resolve().parents[1]
    built_site = repo_root / "site"
    if not built_site.is_dir():
        pytest.skip(
            "site/ not built - run 'mkdocs build' before this test for "
            "real-world integration coverage"
        )
    # All sampled pages must exist (otherwise tests above already cover
    # the missing case).
    for rel in verify_meta_tags.SAMPLED_PAGES:
        if not (built_site / rel).is_file():
            pytest.skip(f"sampled page not in built site: {rel}")
    result = verify_meta_tags.scan(built_site)
    assert result == {}, (
        f"Built site failed meta-tag gate: {result}. "
        "Re-run mkdocs build after fixing overrides/main.html."
    )
