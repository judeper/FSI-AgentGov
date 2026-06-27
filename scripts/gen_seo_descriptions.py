"""Generate per-page SEO `description:` front-matter for GEO/SEO.

Adds a concise (<=160 char) `description:` field to the YAML front-matter of
control pages and key landing pages. The MkDocs Material OG/meta template reads
`page.meta.description` to emit `<meta name="description">` and `og:description`
tags, which improves discoverability and citability by search engines and LLMs.

Behaviour:
  * Descriptions are derived from each page's `## Objective` (controls) or first
    prose paragraph (landing pages), then cleaned of Markdown and truncated.
  * Existing `description:` keys are never overwritten (idempotent, safe to
    re-run). Files that already carry a description are skipped.
  * Front-matter is created if absent, or the `description:` key is inserted
    into an existing front-matter block.
  * Overclaim language ("ensures compliance", "guarantees", etc.) is rewritten
    to hedged equivalents so generated text passes the FSI language linter.
  * `docs/index.md` is intentionally NOT touched (owned by the site shell).

Usage:
    python scripts/gen_seo_descriptions.py            # write descriptions
    python scripts/gen_seo_descriptions.py --check    # report-only, no writes
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

DOCS_DIR = Path("docs")
MAX_LEN = 160

# Pages owned by other components — never edit.
EXCLUDED = {
    DOCS_DIR / "index.md",
    # Generator-owned pages: scripts/generate_coverage_matrix.py (--type controls
    # / --type frontier) and scripts/generate_pattern_coverage.py overwrite these
    # whole files with no front-matter. Adding a `description:` here silently
    # drifts the coverage/pattern --check gates. Never SEO-target them.
    DOCS_DIR / "reference" / "assessment-coverage.md",
    DOCS_DIR / "reference" / "frontier-assessment-coverage.md",
    DOCS_DIR / "reference" / "pattern-coverage.md",
}

# Curated descriptions for high-value landing pages where auto-extraction would
# produce weak prose (e.g. pages that open with bold key/value lines).
CURATED: dict[str, str] = {
    "docs/controls/index.md": (
        "Complete catalog of 79 governance controls for Microsoft 365 AI agents "
        "across Security, Management, Reporting, and SharePoint pillars."
    ),
    "docs/assessment/index.md": (
        "Interactive governance readiness assessment for Microsoft 365 AI agents. "
        "Score your controls in the browser — no data leaves your device."
    ),
    "docs/framework/index.md": (
        "Governance principles, zones, regulatory context, and operating model "
        "for Microsoft 365 AI agents in US financial services organizations."
    ),
}

# Overclaim -> hedged rewrites so generated descriptions pass the FSI linter.
OVERCLAIM_FIXES = [
    (re.compile(r"\bensures?\s+compliance\b", re.IGNORECASE), "supports compliance"),
    (re.compile(r"\bguarantees?\b", re.IGNORECASE), "supports"),
    (re.compile(r"\bwill\s+prevent\b", re.IGNORECASE), "helps prevent"),
    (re.compile(r"\beliminates?\s+risk\b", re.IGNORECASE), "reduces risk"),
    (re.compile(r"\beliminates?\s+the\s+need\s+for\b", re.IGNORECASE), "reduces the need for"),
]

FRONT_MATTER_RE = re.compile(r"^---\s*\n(.*?\n)---\s*\n", re.DOTALL)


def landing_targets() -> list[Path]:
    """Key non-control landing pages that benefit from SEO descriptions."""
    targets: list[Path] = [
        DOCS_DIR / "controls" / "index.md",
        DOCS_DIR / "assessment" / "index.md",
    ]
    for sub in ("framework", "reference", "getting-started"):
        targets.extend(sorted((DOCS_DIR / sub).glob("*.md")))
    return [p for p in targets if p.exists()]


def control_targets() -> list[Path]:
    """All control specification pages (pillar folders, excluding index.md)."""
    files: list[Path] = []
    for pillar in sorted((DOCS_DIR / "controls").glob("pillar-*")):
        if not pillar.is_dir():
            continue
        for f in sorted(pillar.glob("*.md")):
            if f.name != "index.md":
                files.append(f)
    return files


def strip_markdown(text: str) -> str:
    """Reduce Markdown to plain prose suitable for a meta description."""
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)            # images
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)        # links -> text
    text = re.sub(r"[*_`]+", "", text)                          # emphasis/code
    text = re.sub(r"<[^>]+>", "", text)                         # html tags
    text = text.replace("&amp;", "&")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def hedge(text: str) -> str:
    for pattern, repl in OVERCLAIM_FIXES:
        text = pattern.sub(repl, text)
    return text


def attr_safe(text: str) -> str:
    """Neutralize characters that corrupt an HTML attribute value.

    MkDocs/Material interpolate ``page.meta.description`` into ``content="..."``
    without autoescaping, so a literal double-quote ends the attribute early and
    truncates the meta / OpenGraph / Twitter description (a real SEO defect, not
    just cosmetic). Convert paired straight quotes to typographic quotes
    (attribute-safe and more readable) and drop any stray unbalanced quote.
    """
    text = re.sub(r'"([^"]*)"', "\u201c\\1\u201d", text)
    return text.replace('"', "")


def truncate(text: str, limit: int = MAX_LEN) -> str:
    """Truncate to <= limit chars on a word boundary, preferring full sentences."""
    text = attr_safe(text.strip())
    if len(text) <= limit:
        return text
    cut = text[: limit - 1]
    if " " in cut:
        cut = cut[: cut.rfind(" ")]
    return cut.rstrip(" ,;:.") + "\u2026"


def body_after_front_matter(content: str) -> str:
    m = FRONT_MATTER_RE.match(content)
    return content[m.end():] if m else content


def extract_objective(body: str) -> str | None:
    """First sentence(s) of a control's `## Objective` section."""
    m = re.search(r"##\s+Objective\s*\n(.*?)(?:\n#{1,6}\s|\n---\s*\n|\Z)", body, re.DOTALL)
    if not m:
        return None
    return clean_paragraph(m.group(1))


def extract_first_paragraph(body: str) -> str | None:
    """First plain-prose paragraph after the H1 of a landing page."""
    # Drop a leading H1.
    body = re.sub(r"^\s*#\s+.*\n", "", body, count=1)
    for block in re.split(r"\n\s*\n", body):
        line = block.strip()
        if not line:
            continue
        first = line.splitlines()[0].strip()
        # Skip non-prose blocks: admonitions, html, lists, tables, headings,
        # bold key/value lines, separators, code fences.
        if first[:1] in {"#", "-", "*", "|", ">", "<"}:
            continue
        if first.startswith(("!!!", "```", "---", "===")):
            continue
        if first.startswith("**"):
            continue
        cleaned = clean_paragraph(block)
        if cleaned and len(cleaned) >= 40:
            return cleaned
    return None


def clean_paragraph(raw: str) -> str:
    text = strip_markdown(raw)
    if not text:
        return ""
    # Prefer the first sentence if it is already a reasonable length.
    sentence_match = re.match(r"(.+?[.!?])(?:\s|$)", text)
    if sentence_match and len(sentence_match.group(1)) >= 60:
        text = sentence_match.group(1)
    return hedge(text).strip()


def yaml_quote(text: str) -> str:
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def build_description(path: Path, body: str) -> str | None:
    key = path.as_posix()
    if key in CURATED:
        return truncate(hedge(CURATED[key]))
    if "controls" in path.parts and re.search(r"\d+\.\d+", path.name):
        raw = extract_objective(body)
        if raw:
            title = title_of(body)
            # Lead with the control title for stronger LLM/search context.
            combined = f"{title}: {raw}" if title and title.lower() not in raw.lower()[:40] else raw
            return truncate(combined)
        return None
    raw = extract_first_paragraph(body)
    return truncate(raw) if raw else None


def title_of(body: str) -> str | None:
    m = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
    if not m:
        return None
    title = strip_markdown(m.group(1))
    # Normalise "Control 1.1: Foo" -> "Foo" for cleaner descriptions.
    title = re.sub(r"^Control\s+\d+\.\d+\s*[:\-]\s*", "", title)
    return title


def has_description(content: str) -> bool:
    m = FRONT_MATTER_RE.match(content)
    if not m:
        return False
    return re.search(r"^description\s*:", m.group(1), re.MULTILINE) is not None


def inject(content: str, description: str) -> str:
    line = f"description: {yaml_quote(description)}\n"
    m = FRONT_MATTER_RE.match(content)
    if m:
        # Insert into existing front-matter block.
        fm_body = m.group(1)
        return content[: m.start()] + "---\n" + fm_body + line + "---\n" + content[m.end():]
    return "---\n" + line + "---\n" + content


def main(check: bool = False) -> int:
    if not DOCS_DIR.exists():
        print("ERROR: docs/ not found (run from repo root)")
        return 1

    targets = control_targets() + landing_targets()
    written = 0
    skipped_existing = 0
    skipped_noextract = 0

    for path in targets:
        if path in EXCLUDED:
            continue
        content = path.read_text(encoding="utf-8")
        if has_description(content):
            skipped_existing += 1
            continue
        body = body_after_front_matter(content)
        description = build_description(path, body)
        if not description:
            skipped_noextract += 1
            print(f"  - no description extracted: {path.as_posix()}")
            continue
        if check:
            print(f"  WOULD ADD [{len(description):>3}] {path.as_posix()}: {description}")
        else:
            path.write_text(inject(content, description), encoding="utf-8")
        written += 1

    action = "would add" if check else "added"
    print(
        f"\nSEO descriptions: {action} {written}; "
        f"skipped {skipped_existing} (already had one); "
        f"{skipped_noextract} had no extractable prose."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(check="--check" in sys.argv[1:]))
