"""Tests for verify_doc_links.py — the post-build broken-link gate.

Each test materializes a tiny site/ tree under tmp_path and asserts the
verifier flags the right hrefs (and only those). These tests are the
RED-then-GREEN proof that the verifier closes:
- F-CI-GAP-ANCHOR-VALIDATOR-01
- F-BUILD-CROSS-PLAYBOOK-DEPTH-BUG-01
- F-BUILD-EXCLUDE-DOCS-DEAD-LINK-01
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

# Make scripts/ importable regardless of pytest invocation directory.
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import verify_doc_links  # noqa: E402


def _write(site: Path, rel: str, body: str = "") -> Path:
    """Write a file under site/ and create parent dirs as needed."""
    target = site / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(body, encoding="utf-8")
    return target


def _page(href: str) -> str:
    """Minimal HTML body containing exactly one <a href="...">."""
    return f'<!doctype html><html><body><a href="{href}">x</a></body></html>'


# -- Positive cases (must NOT be reported) -----------------------------------

def test_external_https_link_is_skipped(tmp_path: Path) -> None:
    site = tmp_path / "site"
    _write(site, "index.html", _page("https://learn.microsoft.com/foo"))
    assert verify_doc_links.scan(site, None) == []


def test_mailto_and_anchor_only_are_skipped(tmp_path: Path) -> None:
    site = tmp_path / "site"
    _write(site, "index.html",
           '<a href="mailto:x@y.com">m</a><a href="#section">a</a>')
    assert verify_doc_links.scan(site, None) == []


def test_trailing_slash_link_to_directory_with_index_html(tmp_path: Path) -> None:
    """use_directory_urls=True style link: ../foo/ resolves to foo/index.html."""
    site = tmp_path / "site"
    _write(site, "controls/index.html", _page("../reference/"))
    _write(site, "reference/index.html", "<html></html>")
    assert verify_doc_links.scan(site, None) == []


def test_link_with_html_suffix_resolves(tmp_path: Path) -> None:
    site = tmp_path / "site"
    _write(site, "index.html", _page("about.html"))
    _write(site, "about.html", "<html></html>")
    assert verify_doc_links.scan(site, None) == []


def test_link_with_implicit_html_suffix_resolves(tmp_path: Path) -> None:
    """foo.md in source becomes foo/index.html — link to "foo" (no slash) hits the dir."""
    site = tmp_path / "site"
    _write(site, "index.html", _page("about"))
    _write(site, "about/index.html", "<html></html>")
    assert verify_doc_links.scan(site, None) == []


def test_query_string_and_fragment_are_stripped(tmp_path: Path) -> None:
    site = tmp_path / "site"
    _write(site, "index.html", _page("about/?q=1#anchor"))
    _write(site, "about/index.html", "<html></html>")
    assert verify_doc_links.scan(site, None) == []


def test_site_root_link_resolves(tmp_path: Path) -> None:
    site = tmp_path / "site"
    _write(site, "controls/1.1/index.html", _page("/"))
    _write(site, "index.html", "<html></html>")
    assert verify_doc_links.scan(site, None) == []


def test_assets_html_files_are_not_scanned(tmp_path: Path) -> None:
    """site/assets/ is build-tool output — never authored content."""
    site = tmp_path / "site"
    # An asset HTML containing a broken link should NOT be reported.
    _write(site, "assets/javascripts/some-pkg/index.html",
           _page("../../../this-does-not-exist"))
    assert verify_doc_links.scan(site, None) == []


# -- Negative cases (MUST be reported) ---------------------------------------

def test_link_to_missing_file_is_reported(tmp_path: Path) -> None:
    site = tmp_path / "site"
    _write(site, "index.html", _page("missing-page/"))
    broken = verify_doc_links.scan(site, None)
    assert len(broken) == 1
    assert broken[0]["href"] == "missing-page/"
    assert "does not exist" in broken[0]["reason"]


def test_cross_playbook_depth_bug_is_reported(tmp_path: Path) -> None:
    """The F-BUILD-CROSS-PLAYBOOK-DEPTH-BUG-01 pattern.

    Source: docs/playbooks/control-implementations/1.2/foo.md links to ../1.20/
    Built:  site/playbooks/control-implementations/1.2/foo/index.html links to ../1.20/
            -> site/playbooks/control-implementations/1.2/1.20/  (WRONG)
    Real target lives at site/playbooks/control-implementations/1.20/.
    """
    site = tmp_path / "site"
    # Build the page that fires the bad link.
    _write(site,
           "playbooks/control-implementations/1.2/foo/index.html",
           _page("../1.20/"))
    # Real (correct) target dir exists one level higher.
    _write(site,
           "playbooks/control-implementations/1.20/portal-walkthrough/index.html",
           "<html></html>")
    broken = verify_doc_links.scan(site, None)
    assert len(broken) == 1
    assert broken[0]["href"] == "../1.20/"
    assert "1.2/1.20" in broken[0]["reason"]


def test_link_to_excluded_file_is_reported(tmp_path: Path) -> None:
    """F-BUILD-EXCLUDE-DOCS-DEAD-LINK-01 — link to file in mkdocs exclude_docs."""
    site = tmp_path / "site"
    _write(site, "controls/index.html", _page("../templates/exception-template/"))
    # NOTE: templates/ deliberately not created — simulates exclude_docs.
    broken = verify_doc_links.scan(site, None)
    assert len(broken) == 1
    assert "templates/exception-template" in broken[0]["reason"]


def test_link_escaping_site_root_is_reported(tmp_path: Path) -> None:
    site = tmp_path / "site"
    _write(site, "index.html", _page("../../../etc/passwd"))
    broken = verify_doc_links.scan(site, None)
    assert len(broken) == 1
    assert "escapes site root" in broken[0]["reason"]


def test_multiple_broken_links_are_all_reported(tmp_path: Path) -> None:
    site = tmp_path / "site"
    _write(site, "index.html",
           '<a href="missing-a/">a</a>'
           '<a href="missing-b/">b</a>'
           '<a href="missing-c/">c</a>')
    broken = verify_doc_links.scan(site, None)
    assert len(broken) == 3
    assert {b["href"] for b in broken} == {"missing-a/", "missing-b/", "missing-c/"}


# -- Site-URL prefix handling -------------------------------------------------

def test_deploy_prefix_is_stripped_when_present(tmp_path: Path) -> None:
    """Production hrefs include /FSI-AgentGov/ prefix; verifier must strip it."""
    site = tmp_path / "site"
    _write(site, "controls/index.html", _page("/FSI-AgentGov/disclaimer/"))
    _write(site, "disclaimer/index.html", "<html></html>")
    assert verify_doc_links.scan(site, "/FSI-AgentGov/") == []


def test_detect_site_url_prefix_from_sitemap(tmp_path: Path) -> None:
    site = tmp_path / "site"
    _write(site, "index.html", "<html></html>")
    _write(site, "sitemap.xml",
           '<?xml version="1.0"?>'
           '<urlset><url><loc>https://example.com/FSI-AgentGov/</loc></url></urlset>')
    assert verify_doc_links.detect_site_url_prefix(site) == "/FSI-AgentGov/"


def test_detect_site_url_prefix_returns_none_when_root(tmp_path: Path) -> None:
    site = tmp_path / "site"
    _write(site, "sitemap.xml",
           '<?xml version="1.0"?>'
           '<urlset><url><loc>https://example.com/</loc></url></urlset>')
    assert verify_doc_links.detect_site_url_prefix(site) == "/"


# -- main() exit codes -------------------------------------------------------

def test_main_exits_zero_on_clean_site(tmp_path: Path) -> None:
    site = tmp_path / "site"
    _write(site, "index.html", _page("about/"))
    _write(site, "about/index.html", "<html></html>")
    assert verify_doc_links.main([str(site)]) == 0


def test_main_exits_one_on_broken_link(tmp_path: Path, capsys) -> None:
    site = tmp_path / "site"
    _write(site, "index.html", _page("missing/"))
    rc = verify_doc_links.main([str(site)])
    assert rc == 1
    out = capsys.readouterr().out
    assert "FAIL" in out
    assert "missing/" in out


def test_main_exits_two_on_missing_site_dir(tmp_path: Path) -> None:
    assert verify_doc_links.main([str(tmp_path / "nope")]) == 2


def test_json_output_writes_full_report(tmp_path: Path) -> None:
    site = tmp_path / "site"
    _write(site, "index.html",
           '<a href="missing-x/">x</a><a href="missing-y/">y</a>')
    out_path = tmp_path / "report.json"
    verify_doc_links.main([str(site), "--json", str(out_path)])
    data = json.loads(out_path.read_text(encoding="utf-8"))
    assert len(data) == 2
    hrefs = {entry["href"] for entry in data}
    assert hrefs == {"missing-x/", "missing-y/"}


# -- Helper unit tests --------------------------------------------------------

@pytest.mark.parametrize("href, expected", [
    ("https://example.com", True),
    ("http://example.com", True),
    ("mailto:x@y.com", True),
    ("tel:+15551234567", True),
    ("javascript:void(0)", True),
    ("//cdn.example.com/x", True),
    ("#anchor", True),
    ("", True),
    ("   ", True),
    ("about/", False),
    ("/disclaimer/", False),
    ("../foo.md", False),
])
def test_is_external_or_anchor_only(href: str, expected: bool) -> None:
    assert verify_doc_links.is_external_or_anchor_only(href) is expected


def test_strip_query_and_fragment_decodes_percents() -> None:
    result = verify_doc_links.strip_query_and_fragment("foo%20bar/?q=1#x")
    assert result == "foo bar/"
