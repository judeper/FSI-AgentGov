"""Apply targeted, low-risk cleanup transforms to control docs.

Why this exists:
- Keep automation narrow and predictable.
- Avoid semantic rewrites (zones/requirements) while still cleaning obvious drift.

Current transforms:
1) Evidence heading normalization:
   - '### Compliance Evidence Checklist' -> '### Verification Evidence'
2) Expected formatting normalization:
   - '- Expected: ...' -> '- **EXPECTED:** ...'
   - 'Expected: ...' -> '**EXPECTED:** ...'
3) Remove Zone 4 rows from markdown tables:
   - Remove lines that look like table rows containing 'Zone 4'

Run:
  python scripts/fix_controls_targeted_cleanup.py

Notes:
- This is intentionally conservative. Any remaining zone semantic conflicts are
  expected to be handled manually using the audit report.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTROLS_ROOT = REPO_ROOT / "docs" / "reference"

RE_EVIDENCE = re.compile(r"^###\s+Compliance Evidence Checklist\s*$", re.MULTILINE)
RE_EXPECTED_BULLET = re.compile(r"^(\s*[-*]\s*)Expected:\s*", re.IGNORECASE | re.MULTILINE)
RE_EXPECTED_LINE = re.compile(r"^(\s*)Expected:\s*", re.IGNORECASE | re.MULTILINE)

# Standardize near-canonical zone label variants.
RE_ZONE_LABEL_PERSONAL = re.compile(r"\bZone\s+1\s*\(\s*personal\s*\)", re.IGNORECASE)
RE_ZONE_LABEL_TEAM = re.compile(r"\bZone\s+2\s*\(\s*team\s*\)", re.IGNORECASE)
RE_ZONE_LABEL_ENTERPRISE = re.compile(r"\bZone\s+3\s*\(\s*enterprise\s*\)", re.IGNORECASE)
RE_ZONE_LABEL_ENTERPRISE_PROD = re.compile(r"\bZone\s+3\s*\(\s*enterprise\s+production\s*\)", re.IGNORECASE)


@dataclass
class FixCounts:
    evidence_headings: int = 0
    expected_bullets: int = 0
    expected_lines: int = 0
    zone4_table_rows: int = 0
    zone_label_standardizations: int = 0


def iter_control_files() -> list[Path]:
    roots = [
        CONTROLS_ROOT / "pillar-1-security",
        CONTROLS_ROOT / "pillar-2-management",
        CONTROLS_ROOT / "pillar-3-reporting",
        CONTROLS_ROOT / "pillar-4-sharepoint",
    ]
    files: list[Path] = []
    for root in roots:
        if root.exists():
            files.extend(root.rglob("*.md"))
    return sorted(files)


def fix_text(text: str) -> tuple[str, FixCounts]:
    counts = FixCounts()

    # 1) Evidence heading normalization
    text, n = RE_EVIDENCE.subn("### Verification Evidence", text)
    counts.evidence_headings += n

    # 2) Expected formatting
    # Bullet form first, then non-bullet lines.
    text, n = RE_EXPECTED_BULLET.subn(r"\1**EXPECTED:** ", text)
    counts.expected_bullets += n

    def _expected_line_repl(m: re.Match[str]) -> str:
        # Avoid double-fixing bullet lines already handled.
        prefix = m.group(1)
        return f"{prefix}**EXPECTED:** "

    text, n = RE_EXPECTED_LINE.subn(_expected_line_repl, text)
    counts.expected_lines += n

    # 3) Remove Zone 4 rows from markdown tables
    out_lines: list[str] = []
    for line in text.splitlines(keepends=False):
        if line.lstrip().startswith("|") and "zone 4" in line.lower():
            counts.zone4_table_rows += 1
            continue
        out_lines.append(line)

    new_text = "\n".join(out_lines) + ("\n" if text.endswith("\n") else "")

    # 4) Standardize near-canonical zone labels (purely editorial).
    new_text, n = RE_ZONE_LABEL_PERSONAL.subn("Zone 1 (Personal Productivity)", new_text)
    counts.zone_label_standardizations += n
    new_text, n = RE_ZONE_LABEL_TEAM.subn("Zone 2 (Team Collaboration)", new_text)
    counts.zone_label_standardizations += n
    new_text, n = RE_ZONE_LABEL_ENTERPRISE_PROD.subn("Zone 3 (Enterprise Managed)", new_text)
    counts.zone_label_standardizations += n
    new_text, n = RE_ZONE_LABEL_ENTERPRISE.subn("Zone 3 (Enterprise Managed)", new_text)
    counts.zone_label_standardizations += n

    return new_text, counts


def main() -> int:
    totals = FixCounts()
    updated_files = 0

    for path in iter_control_files():
        original = path.read_text(encoding="utf-8")
        updated, counts = fix_text(original)
        if updated != original:
            path.write_text(updated, encoding="utf-8", newline="\n")
            updated_files += 1

        totals.evidence_headings += counts.evidence_headings
        totals.expected_bullets += counts.expected_bullets
        totals.expected_lines += counts.expected_lines
        totals.zone4_table_rows += counts.zone4_table_rows

    print(f"Done. Updated {updated_files} file(s).")
    print(
        "Counts: "
        f"evidence_headings={totals.evidence_headings}, "
        f"expected_bullets={totals.expected_bullets}, "
        f"expected_lines={totals.expected_lines}, "
        f"zone4_table_rows={totals.zone4_table_rows}, "
        f"zone_label_standardizations={totals.zone_label_standardizations}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
