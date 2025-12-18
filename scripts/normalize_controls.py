"""Normalize control document metadata across all 48 controls.

This script enforces the beta requirements:
- Footer must include the exact string: "v1.0 Beta (Dec 2025)"
- Footer must include: "Updated: Dec 2025" (month-year)

It also removes legacy/conflicting metadata in control overviews/footers
(e.g., "Version: 2.0", "Last Updated: January 2025") and collapses
duplicate footer blocks into one canonical footer.

Design goals:
- Conservative edits: only touch obvious metadata lines and footer blocks.
- Preserve any existing UI verification status if present.

Run from repo root:
  python scripts/normalize_controls.py
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

CANON_UPDATED = "Dec 2025"
CANON_VERSION = "v1.0 Beta (Dec 2025)"


@dataclass
class UpdateResult:
    path: Path
    changed: bool
    reason: str


_UI_STATUS_PATTERNS = [
    re.compile(r"^\*\*UI Verification Status:\*\*\s*(.+?)\s*$", re.IGNORECASE),
    re.compile(r"^\*\*Last Updated:\*\*\s*(.+?)\s*$", re.IGNORECASE),
]


def _detect_ui_status(lines: list[str]) -> str | None:
    for line in reversed(lines[-80:]):
        m = re.search(r"\*\*UI Verification Status:\*\*\s*(.+?)\s*$", line, flags=re.IGNORECASE)
        if m:
            return m.group(1).strip()
    # Heuristic: if a footer line says "(Portal UI verified)", treat as Current.
    for line in reversed(lines[-80:]):
        if "portal ui verified" in line.lower():
            return "✅ Current"
    return None


def _strip_legacy_overview_metadata(text: str) -> str:
    """Remove legacy overview metadata lines that conflict with the beta footer.

    We only remove *bold* field lines for Version/Last Updated in the Overview block.
    """
    # Remove lines like "**Version:** 2.0" and "**Last Updated:** January 2025"
    text = re.sub(r"^\*\*Version:\*\*\s*.+?\s*$\n?", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\*\*Last Updated:\*\*\s*.+?\s*$\n?", "", text, flags=re.MULTILINE)
    # Some files used non-bold metadata lines (e.g., "Last Updated: January 2025").
    # Strip these conservatively anywhere they appear as standalone lines.
    text = re.sub(r"^Last Updated:\s*.+?\s*$\n?", "", text, flags=re.MULTILINE | re.IGNORECASE)
    text = re.sub(r"^Version:\s*.+?\s*$\n?", "", text, flags=re.MULTILINE | re.IGNORECASE)
    # A few legacy markers were accidentally authored as headings.
    text = re.sub(r"^#+\s*Last Updated:\s*.+?\s*$\n?", "", text, flags=re.MULTILINE | re.IGNORECASE)
    text = re.sub(r"^#+\s*Version:\s*.+?\s*$\n?", "", text, flags=re.MULTILINE | re.IGNORECASE)

    # Strip legacy review metadata blocks that conflict with the canonical footer.
    text = re.sub(r"^\*\*Control Owner:\*\*\s*.+?\s*$\n?", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\*\*Last Review:\*\*\s*.+?\s*$\n?", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\*\*Next Review:\*\*\s*.+?\s*$\n?", "", text, flags=re.MULTILINE)
    text = re.sub(r"^Control Owner:\s*.+?\s*$\n?", "", text, flags=re.MULTILINE | re.IGNORECASE)
    text = re.sub(r"^Last Review:\s*.+?\s*$\n?", "", text, flags=re.MULTILINE | re.IGNORECASE)
    text = re.sub(r"^Next Review:\s*.+?\s*$\n?", "", text, flags=re.MULTILINE | re.IGNORECASE)
    return text


def _strip_existing_footer_blocks(text: str) -> tuple[str, str | None]:
    """Remove known footer metadata patterns at end of file.

    Returns (stripped_text, detected_ui_status)
    """
    lines = text.rstrip().splitlines()
    ui_status = _detect_ui_status(lines)

    # Remove trailing blank lines
    while lines and lines[-1].strip() == "":
        lines.pop()

    # Remove trailing legacy/beta footer metadata lines.
    footer_line_patterns = [
        re.compile(r"^\*\*Updated:\*\*\s*.+$", re.IGNORECASE),
        re.compile(r"^\*\*Last Updated:\*\*\s*.+$", re.IGNORECASE),
        re.compile(r"^\*Last Updated:\s*.+\*$", re.IGNORECASE),
        re.compile(r"^\*\*Version:\*\*\s*.+$", re.IGNORECASE),
        re.compile(r"^\*Version:\s*.+\*$", re.IGNORECASE),
        re.compile(r"^\*FSI Agent Governance Framework.*\*$", re.IGNORECASE),
        re.compile(r"^\*\*UI Verification Status:\*\*\s*.+$", re.IGNORECASE),
    ]

    def is_footer_meta(line: str) -> bool:
        return any(p.match(line.strip()) for p in footer_line_patterns)

    # Pop footer meta lines at bottom (possibly multiple blocks)
    removed_any = False
    while lines and (is_footer_meta(lines[-1]) or lines[-1].strip() == "---"):
        if is_footer_meta(lines[-1]) or lines[-1].strip() == "---":
            removed_any = True
        lines.pop()
        while lines and lines[-1].strip() == "":
            lines.pop()

    stripped = "\n".join(lines).rstrip() + "\n"
    return stripped, ui_status


def _append_canonical_footer(text: str, ui_status: str | None) -> str:
    status = ui_status or "❌ Needs verification"
    footer = (
        "\n---\n\n"
        f"**Updated:** {CANON_UPDATED}  \n"
        f"**Version:** {CANON_VERSION}  \n"
        f"**UI Verification Status:** {status}\n"
    )
    return text.rstrip() + footer


def normalize_file(path: Path) -> UpdateResult:
    raw = path.read_text(encoding="utf-8")
    before = raw

    raw = _strip_legacy_overview_metadata(raw)
    stripped, ui_status = _strip_existing_footer_blocks(raw)
    after = _append_canonical_footer(stripped, ui_status)

    changed = after != before
    if changed:
        path.write_text(after, encoding="utf-8", newline="\n")
        return UpdateResult(path=path, changed=True, reason="normalized footer/version metadata")
    return UpdateResult(path=path, changed=False, reason="already normalized")


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
        result = normalize_file(path)
        if result.changed:
            changed += 1
            print(f"UPDATED: {path.as_posix()}")

    print(f"\nDone. Updated {changed}/{len(files)} control files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
