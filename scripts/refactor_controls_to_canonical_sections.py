"""LEGACY SCRIPT - Refactor control markdown files to canonical section structure.

WARNING: This script is OUTDATED as of v1.1 restructuring (January 2026).
- It references old paths (docs/reference/pillar-*) instead of docs/controls/pillar-*
- It references old section names that don't match the current 10-section template
- The current control structure uses 10 sections (see docs/templates/control-setup-template.md)

DO NOT USE this script without updating it first.

Original Goal (Option B):
- Make every control use the canonical H2 headings in the canonical order.
- Keep content intact, but re-home non-canonical H2 headings as H3 subheadings
  under the appropriate canonical section.
- Ensure `### Zone-Specific Configuration` exists under Financial Sector Considerations.
- Preserve existing intra-site heading anchors where possible by inserting an
  extra HTML anchor when an H2 heading name is changed.

Run from repo root:
  python scripts/refactor_controls_to_canonical_sections.py

Notes:
- This script intentionally does NOT touch the canonical footer fields; run
  scripts/normalize_controls.py afterwards to re-assert the footer.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


DOCS_DIR = Path("docs")
PILLAR_DIRS = [
    DOCS_DIR / "reference" / "pillar-1-security",
    DOCS_DIR / "reference" / "pillar-2-management",
    DOCS_DIR / "reference" / "pillar-3-reporting",
    DOCS_DIR / "reference" / "pillar-4-sharepoint",
]

CANONICAL_H2 = [
    "Overview",
    "Prerequisites",
    "Governance Levels",
    "Setup & Configuration",
    "Financial Sector Considerations",
    "Verification & Testing",
    "Troubleshooting & Validation",
    "Additional Resources",
    "Related Controls",
    "Support & Questions",
]

# H2 variants that should become canonical H2 headings.
H2_VARIANTS_TO_CANON = {
    "Troubleshooting": "Troubleshooting & Validation",
    "Microsoft Learn References": "Additional Resources",
    "Resources": "Additional Resources",
    "Implementation Guidance": "Setup & Configuration",
    "Configuration Steps": "Setup & Configuration",
    "Setup Steps": "Setup & Configuration",
    "Setup": "Setup & Configuration",
}

# H2 headings that should generally become H3s under Overview.
OVERVIEW_SUBHEADINGS = {
    "Purpose",
    "Description",
    "Key Capabilities",
}

# H2 headings that should generally become H3s under Setup & Configuration.
SETUP_SUBHEADINGS = {
    "PowerShell Configuration",
    "PowerShell/CLI Configuration",
    "Portal Configuration",
    "Portal-Based Configuration",
    "Entra Id Navigation",
    "Entra ID Navigation",
    "PPAC Security Section",
    "SharePoint Admin Center",
}


@dataclass
class Section:
    title: str
    body_lines: list[str]


def _slugify(text: str) -> str:
    # Approximate MkDocs/Markdown TOC slug behavior.
    text = text.strip().lower()
    text = re.sub(r"\{#.+?\}$", "", text).strip()
    text = re.sub(r"[^a-z0-9\s\-]", "", text)
    text = re.sub(r"\s+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text


def _strip_footer(text: str) -> tuple[str, str]:
    """Return (content_without_footer, footer_block_or_empty)."""
    # Canonical footer introduced by normalize_controls.py
    m = re.search(
        r"\n---\n\n\*\*Updated:\*\*\s+.+\n\*\*Version:\*\*\s+.+\n\*\*UI Verification Status:\*\*\s+.+\n?\s*$",
        text,
        flags=re.IGNORECASE,
    )
    if not m:
        return text, ""
    return text[: m.start()].rstrip() + "\n", text[m.start() :].lstrip("\n")


def _iter_h2_sections(lines: list[str]) -> tuple[list[str], list[tuple[str, list[str]]]]:
    """Split file into preamble lines + list of (h2_title, section_lines_including_heading)."""
    in_fence = False
    h2_indices: list[int] = []

    for i, line in enumerate(lines):
        if line.strip().startswith("```"):
            in_fence = not in_fence
        if in_fence:
            continue
        if line.startswith("## "):
            h2_indices.append(i)

    if not h2_indices:
        return lines, []

    preamble = lines[: h2_indices[0]]
    sections: list[tuple[str, list[str]]] = []

    for idx, start in enumerate(h2_indices):
        end = h2_indices[idx + 1] if idx + 1 < len(h2_indices) else len(lines)
        heading_line = lines[start].rstrip("\n")
        title = heading_line[3:].strip()
        # Strip attr_list if present
        title = re.sub(r"\s*\{#.+?\}\s*$", "", title).strip()
        sections.append((title, [l.rstrip("\n") for l in lines[start:end]]))

    return [l.rstrip("\n") for l in preamble], sections


def _guess_bucket(
    title: str,
    current_bucket: str,
) -> str:
    if title in CANONICAL_H2:
        return title

    mapped = H2_VARIANTS_TO_CANON.get(title)
    if mapped:
        return mapped

    if title in OVERVIEW_SUBHEADINGS:
        return "Overview"

    if title in SETUP_SUBHEADINGS:
        return "Setup & Configuration"

    # Keyword heuristics for setup-like headings.
    setup_keywords = [
        "navigation",
        "policy",
        "policies",
        "admin",
        "center",
        "portal",
        "configuration",
        "settings",
        "ppac",
        "sharepoint",
        "entra",
        "purview",
        "power platform",
        "powershell",
        "cli",
    ]
    if any(k in title.lower() for k in setup_keywords):
        return "Setup & Configuration"

    if "regulator" in title.lower() or "regulatory" in title.lower():
        return "Financial Sector Considerations"

    # Default: keep within current canonical bucket.
    return current_bucket


def _ensure_zone_specific(financial_body: list[str]) -> list[str]:
    in_fence = False
    for line in financial_body:
        if line.strip().startswith("```"):
            in_fence = not in_fence
        if in_fence:
            continue
        if line.strip() == "### Zone-Specific Configuration":
            return financial_body

    # Append minimal guidance stub.
    stub = [
        "",
        "### Zone-Specific Configuration",
        "",
        "**Zone 1 (Personal Productivity):**",
        "- Not required by default; document any exceptions.",
        "",
        "**Zone 2 (Team Collaboration):**",
        "- Apply recommended configuration and validate with a pilot group.",
        "",
        "**Zone 3 (Enterprise Managed):**",
        "- Apply the strictest configuration and require change control evidence.",
        "",
    ]
    return financial_body + stub


def _extract_learn_links(text: str) -> list[str]:
    urls = re.findall(r"https?://learn\.microsoft\.com/[^\s\)\]]+", text, flags=re.IGNORECASE)
    deduped: list[str] = []
    seen = set()
    for u in urls:
        u = u.rstrip(".)]")
        if u.lower() in seen:
            continue
        seen.add(u.lower())
        deduped.append(u)
    return deduped


def _minimal_section_body(title: str, learn_links: list[str]) -> list[str]:
    if title == "Setup & Configuration":
        return [
            "",
            "Add portal-based configuration steps and (if applicable) PowerShell/CLI alternatives.",
            "",
        ]
    if title == "Troubleshooting & Validation":
        return [
            "",
            "Add common issues, root causes, and validation steps.",
            "",
        ]
    if title == "Additional Resources":
        if learn_links:
            return ["", *[f"- {u}" for u in learn_links], ""]
        return [
            "",
            "- Microsoft Learn: https://learn.microsoft.com/en-us/",
            "",
        ]
    if title == "Support & Questions":
        return [
            "",
            "For implementation support or questions about this control, contact:",
            "- **AI Governance Lead** (governance direction)",
            "- **Compliance Officer** (regulatory requirements)",
            "- **Technical Implementation Team** (platform setup)",
            "",
        ]
    return ["", "(No additional content yet.)", ""]


def refactor_control(path: Path) -> bool:
    raw = path.read_text(encoding="utf-8")
    content, footer = _strip_footer(raw)

    learn_links = _extract_learn_links(content)

    lines = content.splitlines()
    preamble, h2_sections = _iter_h2_sections(lines)

    # If no H2 sections, bail (unexpected for controls).
    if not h2_sections:
        return False

    # Build canonical buckets.
    buckets: dict[str, list[str]] = {t: [] for t in CANONICAL_H2}

    current_bucket = "Overview"
    seen_main_heading: set[str] = set()

    for original_title, section_lines in h2_sections:
        # section_lines includes the original heading line as first element.
        body = section_lines[1:]

        bucket = _guess_bucket(original_title, current_bucket)

        # If this section is a canonical bucket section (or variant that maps to it),
        # treat it as the main H2 for that bucket.
        mapped = H2_VARIANTS_TO_CANON.get(original_title)
        is_main = original_title in CANONICAL_H2 or mapped in CANONICAL_H2

        if is_main:
            canon_title = original_title if original_title in CANONICAL_H2 else mapped
            if canon_title:
                # Preserve old anchor by inserting an extra anchor when the heading text changed.
                if original_title != canon_title:
                    old_id = _slugify(original_title)
                    if old_id:
                        buckets[canon_title].append(f"<a id=\"{old_id}\"></a>")

                # Append this section body to the canonical bucket.
                if buckets[canon_title] and buckets[canon_title][-1].strip() != "":
                    buckets[canon_title].append("")
                buckets[canon_title].extend(body)
                seen_main_heading.add(canon_title)
                current_bucket = canon_title
                continue

        # Otherwise, demote the original H2 heading to an H3 inside its target bucket.
        if bucket not in buckets:
            bucket = current_bucket

        if buckets[bucket] and buckets[bucket][-1].strip() != "":
            buckets[bucket].append("")
        buckets[bucket].append(f"### {original_title}")
        buckets[bucket].append("")
        buckets[bucket].extend(body)
        current_bucket = bucket

    # Ensure Zone-Specific Configuration exists.
    buckets["Financial Sector Considerations"] = _ensure_zone_specific(
        buckets["Financial Sector Considerations"]
    )

    # Fill any missing canonical sections with minimal bodies.
    for title in CANONICAL_H2:
        if not buckets[title] or all(l.strip() == "" for l in buckets[title]):
            buckets[title] = _minimal_section_body(title, learn_links)

    # Reassemble.
    out_lines: list[str] = []
    out_lines.extend([l.rstrip() for l in preamble])
    # Ensure title exists and a blank line before first H2.
    while out_lines and out_lines[-1].strip() == "":
        out_lines.pop()
    out_lines.append("")

    for title in CANONICAL_H2:
        out_lines.append(f"## {title}")
        # Normalize bucket body whitespace.
        body = [l.rstrip() for l in buckets[title]]
        # Trim leading/trailing blank lines in body.
        while body and body[0].strip() == "":
            body.pop(0)
        while body and body[-1].strip() == "":
            body.pop()
        if body:
            out_lines.append("")
            out_lines.extend(body)
        out_lines.append("")

    # Re-attach footer (if present) or leave for normalize_controls.py.
    if footer:
        out_lines.append(footer.rstrip())
        out_lines.append("")

    updated = "\n".join(out_lines).rstrip() + "\n"

    if updated != raw:
        path.write_text(updated, encoding="utf-8", newline="\n")
        return True
    return False


def iter_control_files() -> list[Path]:
    files: list[Path] = []
    for pillar_dir in PILLAR_DIRS:
        if not pillar_dir.exists():
            continue
        for path in pillar_dir.glob("*.md"):
            if path.name.lower() == "index.md":
                continue
            files.append(path)
    return sorted(files)


def main() -> int:
    files = iter_control_files()
    if not files:
        print("No control files found.")
        return 1

    changed = 0
    for path in files:
        if refactor_control(path):
            changed += 1
            print(f"UPDATED: {path.as_posix()}")

    print(f"\nDone. Updated {changed}/{len(files)} control files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
