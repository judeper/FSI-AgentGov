#!/usr/bin/env python3
"""Guard the FAQ schema.org JSON-LD against drift from the visible FAQ page.

`overrides/partials/faq-jsonld.html` ships a static ``FAQPage`` JSON-LD block
that is injected (head-only) on ``docs/reference/faq.md`` for Google
rich-result eligibility. Google requires the structured data to mirror the
visible page content; a stale JSON-LD block is a policy violation and an SEO
liability.

Because the two artifacts are maintained by hand, they will silently desync
the next time someone edits the FAQ. This check fails CI when the set of
questions in the JSON-LD no longer matches the ``### Q: ...`` headings on the
page.

Scope: we assert **question** parity (ordered list of question strings). We
intentionally do NOT assert byte-for-byte answer parity — the JSON-LD answers
are a markdown-flattened rendering of the page answers (lists/links removed),
so an exact comparison would be brittle and flaky in CI. Question parity
catches the high-value drift (a question added, removed, reordered, or
reworded) without false positives.

Usage:
    python scripts/check_faq_jsonld_drift.py --check
    python scripts/check_faq_jsonld_drift.py            # same as --check
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FAQ_MD = ROOT / "docs" / "reference" / "faq.md"
PARTIAL = ROOT / "overrides" / "partials" / "faq-jsonld.html"

LDJSON_RE = re.compile(
    r'<script type="application/ld\+json">(.*?)</script>', re.DOTALL
)
# Question headings on the page look like: "### Q: How long does ... take?"
HEADING_RE = re.compile(r"^###\s+(?:Q[:.]?\s*)?(.+?)\s*$")


def normalize(text: str) -> str:
    """Collapse whitespace and fold smart quotes/dashes so cosmetic typography
    differences between the page and the JSON-LD don't trip the check."""
    text = unicodedata.normalize("NFKC", text)
    text = (
        text.replace("\u2019", "'")
        .replace("\u2018", "'")
        .replace("\u201c", '"')
        .replace("\u201d", '"')
        .replace("\u2013", "-")
        .replace("\u2014", "-")
    )
    return re.sub(r"\s+", " ", text).strip()


def page_questions(md_path: Path) -> list[str]:
    questions: list[str] = []
    for line in md_path.read_text(encoding="utf-8").splitlines():
        m = HEADING_RE.match(line)
        if m:
            questions.append(normalize(m.group(1)))
    return questions


def jsonld_questions(partial_path: Path) -> list[str]:
    html = partial_path.read_text(encoding="utf-8")
    m = LDJSON_RE.search(html)
    if not m:
        raise SystemExit(
            f"ERROR: no <script type=\"application/ld+json\"> block in {partial_path}"
        )
    data = json.loads(m.group(1))
    if data.get("@type") != "FAQPage":
        raise SystemExit(
            f"ERROR: JSON-LD @type is {data.get('@type')!r}, expected 'FAQPage'"
        )
    questions: list[str] = []
    for entry in data.get("mainEntity", []):
        if entry.get("@type") != "Question" or "name" not in entry:
            raise SystemExit("ERROR: malformed mainEntity Question entry")
        questions.append(normalize(str(entry["name"])))
    return questions


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail (exit 1) if the JSON-LD questions drift from faq.md.",
    )
    parser.parse_args()

    if not FAQ_MD.exists():
        print(f"ERROR: missing {FAQ_MD}", file=sys.stderr)
        return 2
    if not PARTIAL.exists():
        print(f"ERROR: missing {PARTIAL}", file=sys.stderr)
        return 2

    page = page_questions(FAQ_MD)
    ld = jsonld_questions(PARTIAL)

    if page == ld:
        print(f"OK: FAQ JSON-LD in sync with faq.md ({len(page)} questions).")
        return 0

    print("FAIL: FAQ JSON-LD has drifted from docs/reference/faq.md", file=sys.stderr)
    print(f"  page questions:   {len(page)}", file=sys.stderr)
    print(f"  json-ld questions: {len(ld)}", file=sys.stderr)
    page_set, ld_set = set(page), set(ld)
    only_page = [q for q in page if q not in ld_set]
    only_ld = [q for q in ld if q not in page_set]
    if only_page:
        print("  on page but MISSING from JSON-LD:", file=sys.stderr)
        for q in only_page:
            print(f"    - {q}", file=sys.stderr)
    if only_ld:
        print("  in JSON-LD but NOT on page (stale):", file=sys.stderr)
        for q in only_ld:
            print(f"    - {q}", file=sys.stderr)
    if not only_page and not only_ld:
        print("  same questions but DIFFERENT ORDER.", file=sys.stderr)
    print(
        "\nUpdate overrides/partials/faq-jsonld.html to mirror the visible "
        "FAQ before merging.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
