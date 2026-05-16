#!/usr/bin/env python3
"""
verify_doc_links.py — fail CI on broken internal HREFs in the built site.

Closes:
- F-CI-GAP-ANCHOR-VALIDATOR-01: gates the failure modes that escape today.
- F-BUILD-CROSS-PLAYBOOK-DEPTH-BUG-01: catches `../X.Y/` from
  playbooks/control-implementations/N.M/foo.md (resolves wrong after
  page-dir transform).
- F-BUILD-EXCLUDE-DOCS-DEAD-LINK-01: catches links to files in mkdocs.yml
  exclude_docs (e.g., CONTROL-INDEX.md, raci-matrix.md).

Why a custom validator (per AS13 rubber-duck B1):
  mkdocs.yml already sets `validation: links: anchors: warn`, but mkdocs
  logs unresolved relative links + excluded-target links at INFO level
  (1,382 lines on a clean build today, all silent on --strict). The 1,365
  "unrecognized relative link" lines are mostly trailing-slash false
  positives that work in production via use_directory_urls=True. The 17
  "excluded from the built site" lines are real broken links. AND mkdocs
  does not flag the cross-playbook depth bug at all — it sees `../X.Y/`
  from the source tree and resolves to a valid source directory, missing
  that the page-dir transform shifts the actual built location one level
  deeper.

Approach:
  Walk the built site/**/*.html and validate every internal <a href="...">.
  For each href:
    - Strip query string and fragment.
    - Skip absolute URLs (http://, https://, mailto:, tel:, ftp:, data:, #).
    - Resolve relative to the containing page's directory.
    - Confirm the target exists as a file, a directory with index.html,
      or a path with .html appended.
  Exit 1 with a per-link report on any failure.

Usage:
    python scripts/verify_doc_links.py [SITE_DIR]
    python scripts/verify_doc_links.py site --json broken-links.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

HREF_PATTERN = re.compile(r'<a\b[^>]*?\bhref\s*=\s*"([^"]*)"', re.IGNORECASE)

ABSOLUTE_SCHEMES = ("http://", "https://", "mailto:", "tel:", "ftp:", "data:", "javascript:")

# Paths under site/ that are not authored content; never validate links inside.
SKIP_HTML_DIR_PARTS = {
    "assets",
    "javascripts",
    "stylesheets",
    "search",
}


def is_external_or_anchor_only(href: str) -> bool:
    """Classify hrefs we never validate against site/ filesystem."""
    if not href:
        return True
    h = href.strip()
    if not h:
        return True
    if h.startswith(ABSOLUTE_SCHEMES):
        return True
    if h.startswith("//"):
        return True
    if h.startswith("#"):
        return True
    return False


def strip_query_and_fragment(href: str) -> str:
    """Drop ?query and #fragment from an href; return percent-decoded path."""
    parsed = urlparse(href)
    return unquote(parsed.path)


def resolve_target(site_root: Path, page_path: Path, href_path: str) -> str | None:
    """Resolve href to a site-relative POSIX-style path (no resolve() call).

    Uses os.path.normpath on a manually composed posix path — way faster
    than Path.resolve() on Windows (which walks symlinks).

    Returns the POSIX-style site-relative path on success, or None if the
    href escapes the site root.
    """
    if href_path.startswith("/"):
        composed = href_path[1:]
    else:
        page_dir_rel = page_path.parent.relative_to(site_root).as_posix()
        if page_dir_rel == ".":
            composed = href_path
        else:
            composed = f"{page_dir_rel}/{href_path}"

    # Normalize using forward slashes (POSIX style) so the result matches
    # the keys we precompute in build_valid_paths().
    parts: list[str] = []
    for segment in composed.split("/"):
        if segment in ("", "."):
            continue
        if segment == "..":
            if not parts:
                return None  # escapes site root
            parts.pop()
            continue
        parts.append(segment)
    return "/".join(parts)


def target_exists(rel_target: str, valid_paths: set[str], valid_dirs: set[str]) -> bool:
    """Check whether the resolved relative target maps to any served file.

    Three valid resolutions:
      1. Direct file: rel_target is itself in valid_paths.
      2. Directory with index.html: rel_target/index.html in valid_paths.
      3. Implicit .html suffix: rel_target + ".html" in valid_paths.

    Empty rel_target = the site root itself = always valid.
    """
    if rel_target == "":
        return True
    if rel_target in valid_paths:
        return True
    if rel_target in valid_dirs:
        # Directory exists — is there an index.html?
        if f"{rel_target}/index.html" in valid_paths:
            return True
    if f"{rel_target}.html" in valid_paths:
        return True
    return False


def build_valid_paths(site_root: Path) -> tuple[set[str], set[str]]:
    """Walk site/ once. Return (set of file POSIX paths, set of dir POSIX paths)."""
    valid_files: set[str] = set()
    valid_dirs: set[str] = set()
    for path in site_root.rglob("*"):
        rel = path.relative_to(site_root).as_posix()
        if path.is_file():
            valid_files.add(rel)
        elif path.is_dir():
            valid_dirs.add(rel)
    return valid_files, valid_dirs


def iter_html_files(site_root: Path):
    """Yield every site/**/*.html that holds authored content."""
    for path in site_root.rglob("*.html"):
        rel_parts = set(path.relative_to(site_root).parts[:-1])
        if rel_parts & SKIP_HTML_DIR_PARTS:
            continue
        yield path


def scan(site_root: Path, site_url_prefix: str | None) -> list[dict]:
    """Walk every authored HTML file and collect broken hrefs."""
    broken: list[dict] = []
    valid_files, valid_dirs = build_valid_paths(site_root)
    # Cache per-href lookup results — many pages link to the same files.
    seen: dict[tuple[str, str], bool] = {}
    for html_path in iter_html_files(site_root):
        try:
            text = html_path.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            broken.append({
                "page": str(html_path.relative_to(site_root)).replace("\\", "/"),
                "href": "(unreadable)",
                "reason": f"read error: {e}",
            })
            continue
        page_dir_rel = html_path.parent.relative_to(site_root).as_posix()
        for raw in HREF_PATTERN.findall(text):
            if is_external_or_anchor_only(raw):
                continue
            href_path = strip_query_and_fragment(raw)
            if not href_path:
                continue
            # Strip the deploy site_url prefix if present; preserve the
            # leading slash so resolve_target() treats the result as
            # site-root-absolute (NOT page-relative — that would resolve
            # `/FSI-AgentGov/disclaimer/` against every page's directory
            # and falsely flag 700+ links).
            if site_url_prefix and href_path.startswith(site_url_prefix):
                href_path = "/" + href_path[len(site_url_prefix):].lstrip("/")
            cache_key = (page_dir_rel, href_path)
            if cache_key in seen:
                ok = seen[cache_key]
            else:
                rel_target = resolve_target(site_root, html_path, href_path)
                if rel_target is None:
                    ok = False
                else:
                    ok = target_exists(rel_target, valid_files, valid_dirs)
                seen[cache_key] = ok
            if not ok:
                rel_target = resolve_target(site_root, html_path, href_path)
                if rel_target is None:
                    reason = "escapes site root"
                else:
                    reason = f"resolves to {rel_target} which does not exist"
                broken.append({
                    "page": str(html_path.relative_to(site_root)).replace("\\", "/"),
                    "href": raw,
                    "reason": reason,
                })
    return broken


def detect_site_url_prefix(site_root: Path) -> str | None:
    """Read site/sitemap.xml to learn the deploy prefix (e.g., /FSI-AgentGov/)."""
    sitemap = site_root / "sitemap.xml"
    if not sitemap.is_file():
        return None
    try:
        head = sitemap.read_text(encoding="utf-8", errors="replace")[:4096]
    except OSError:
        return None
    m = re.search(r"<loc>(https?://[^<]+?)</loc>", head)
    if not m:
        return None
    parsed = urlparse(m.group(1))
    prefix = parsed.path
    if not prefix:
        return None
    if not prefix.endswith("/"):
        prefix += "/"
    return prefix


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("site_dir", nargs="?", default="site",
                        help="Path to the built MkDocs site (default: site)")
    parser.add_argument("--json", dest="json_out",
                        help="Optional path to write the broken-link report as JSON")
    parser.add_argument("--max-print", type=int, default=50,
                        help="Maximum number of broken links to print (default: 50)")
    args = parser.parse_args(argv)

    site_root = Path(args.site_dir)
    if not site_root.is_dir():
        print(f"ERROR: site directory not found: {site_root}", file=sys.stderr)
        return 2

    prefix = detect_site_url_prefix(site_root)
    broken = scan(site_root, prefix)

    if args.json_out:
        Path(args.json_out).write_text(
            json.dumps(broken, indent=2), encoding="utf-8"
        )

    if not broken:
        page_count = sum(1 for _ in iter_html_files(site_root))
        print(f"OK: scanned {page_count} pages, no broken internal links.")
        return 0

    print(f"FAIL: {len(broken)} broken internal href(s) detected:")
    by_page: dict[str, list[dict]] = {}
    for b in broken:
        by_page.setdefault(b["page"], []).append(b)
    shown = 0
    for page in sorted(by_page):
        for b in by_page[page]:
            if shown >= args.max_print:
                remaining = len(broken) - shown
                print(f"  ... {remaining} more (use --json to see all)")
                return 1
            print(f"  {page}")
            print(f"    href: {b['href']}")
            print(f"    {b['reason']}")
            shown += 1
    return 1


if __name__ == "__main__":
    sys.exit(main())
