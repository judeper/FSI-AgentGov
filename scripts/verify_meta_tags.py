"""verify_meta_tags.py — post-build OpenGraph + Twitter Card meta gate.

Closes F-DOCS-OG-TWITTER-CARDS-MISSING-01 (AS16). Customer-facing
governance documentation site is shared in customer / partner Slack and
Teams channels in regulated FS organizations. Without OpenGraph and
Twitter Card meta, those links render as bare URLs - poor first
impression.

For each representative page (homepage + a deep playbook + a control
page), this verifier asserts the seven required meta tags render with
non-empty content attributes.

Usage:

  python scripts/verify_meta_tags.py site/

Returns non-zero exit code if any required meta tag is missing or empty
on any sampled page. Wired into CI via python-quality.yml (auto-included
by pytest scripts/).
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Pages we sample. Each is a representative slice of the site corpus:
# - homepage (no page-specific title)
# - a deep playbook (long path, control-specific title)
# - a top-level reference page (medium path, generic title)
SAMPLED_PAGES = (
    "index.html",
    "playbooks/control-implementations/2.26/portal-walkthrough/index.html",
    "reference/microsoft-learn-urls/index.html",
)

# The site-level fallback description (set in mkdocs.yml site_description).
# Playbook pages MUST NOT use this — they need unique per-page descriptions (SEO-02).
GENERIC_SITE_DESCRIPTION = (
    "Governance framework for Microsoft 365 AI agents"
    " (Copilot Studio, Agent Builder) in Financial Services"
)

# Meta tags that MUST be present on every page with non-empty content="".
REQUIRED_META = (
    ('property', 'og:title'),
    ('property', 'og:description'),
    ('property', 'og:url'),
    ('property', 'og:type'),
    ('property', 'og:site_name'),
    ('name', 'twitter:card'),
    ('name', 'twitter:title'),
    ('name', 'twitter:description'),
)


def find_meta_content(html: str, attr: str, value: str) -> str | None:
    """Return the content="..." of a <meta {attr}="{value}" content="..."> tag.

    Returns None if the tag is absent. Returns "" if present-but-empty.
    Tolerates attribute order (content first or second) and arbitrary
    whitespace.
    """
    # Match <meta ... attr="value" ... content="...">
    pattern1 = re.compile(
        rf'<meta\b[^>]*\b{re.escape(attr)}\s*=\s*"{re.escape(value)}"'
        r'[^>]*\bcontent\s*=\s*"([^"]*)"',
        re.IGNORECASE,
    )
    match = pattern1.search(html)
    if match:
        return match.group(1)
    # Match <meta ... content="..." ... attr="value">
    pattern2 = re.compile(
        r'<meta\b[^>]*\bcontent\s*=\s*"([^"]*)"'
        rf'[^>]*\b{re.escape(attr)}\s*=\s*"{re.escape(value)}"',
        re.IGNORECASE,
    )
    match = pattern2.search(html)
    if match:
        return match.group(1)
    return None


def check_page(html: str, is_playbook: bool = False, is_inner: bool = False) -> list[str]:
    """Return a list of human-readable failure messages for one page."""
    failures: list[str] = []
    for attr, value in REQUIRED_META:
        content = find_meta_content(html, attr, value)
        if content is None:
            failures.append(f"missing <meta {attr}=\"{value}\">")
            continue
        if not content.strip():
            failures.append(
                f'<meta {attr}="{value}"> has empty content=""'
            )
    # SEO-02: Playbook pages must have unique descriptions — not the generic site fallback.
    if is_playbook:
        desc = find_meta_content(html, "property", "og:description") or ""
        if desc.strip() == GENERIC_SITE_DESCRIPTION:
            failures.append(
                "og:description is the generic site fallback description — "
                "playbook pages require unique per-page descriptions (SEO-02 regression)"
            )
    # SEO-03: Inner pages must contain BreadcrumbList JSON-LD.
    if is_inner:
        if '"BreadcrumbList"' not in html:
            failures.append(
                'missing BreadcrumbList JSON-LD (SEO-03 regression — '
                '"@type": "BreadcrumbList" not found in page)'
            )
    return failures


def scan(site_root: Path, sampled_pages: tuple[str, ...] = SAMPLED_PAGES) -> dict[str, list[str]]:
    """Return {page_path: [failures]} for every sampled page that fails."""
    broken: dict[str, list[str]] = {}
    for rel in sampled_pages:
        page_path = site_root / rel
        if not page_path.is_file():
            broken[rel] = [f"sampled page not found at {page_path}"]
            continue
        html = page_path.read_text(encoding="utf-8")
        # Classify: homepage, playbook inner page, or generic inner page
        is_homepage = rel == "index.html"
        is_playbook = "playbooks/control-implementations/" in rel
        is_inner = not is_homepage
        failures = check_page(html, is_playbook=is_playbook, is_inner=is_inner)
        if failures:
            broken[rel] = failures
    return broken


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "site_root",
        type=Path,
        help="Path to the built MkDocs site/ directory.",
    )
    args = parser.parse_args()

    if not args.site_root.is_dir():
        print(f"ERROR: site root not found: {args.site_root}", file=sys.stderr)
        return 2

    broken = scan(args.site_root)
    if broken:
        print(
            f"FAIL: OpenGraph/Twitter meta missing on "
            f"{len(broken)} of {len(SAMPLED_PAGES)} sampled pages:",
            file=sys.stderr,
        )
        for page, failures in broken.items():
            print(f"  - {page}:", file=sys.stderr)
            for f in failures:
                print(f"      {f}", file=sys.stderr)
        return 1

    print(
        f"OK: all {len(REQUIRED_META)} required meta tags present on "
        f"{len(SAMPLED_PAGES)} sampled pages."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
