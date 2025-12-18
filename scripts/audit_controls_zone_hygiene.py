"""Audit control docs for zone consistency and common cleanup targets.

This script is intentionally conservative:
- It does not modify files.
- It produces a machine-readable JSON report and a human-friendly Markdown report.

Primary focus:
- Zone 4 mentions (legacy)
- Ambiguous zone-like tokens (e.g., `Zone4`, `zone4_*`)
- Zone label drift (e.g., "Zone 3 (Production)")
- Zone mentions outside the dedicated "### Zone-Specific Configuration" section
- Evidence heading inconsistencies
- "Expected:" formatting drift

Run:
  python scripts/audit_controls_zone_hygiene.py

Outputs:
- maintainers-local/reports/ZONE-AUDIT-REPORT.md
- maintainers-local/reports/ZONE-AUDIT-REPORT.json
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTROLS_ROOT = REPO_ROOT / "docs" / "reference"
REPORTS_ROOT = REPO_ROOT / "maintainers-local" / "reports"
REPORT_MD = REPORTS_ROOT / "ZONE-AUDIT-REPORT.md"
REPORT_JSON = REPORTS_ROOT / "ZONE-AUDIT-REPORT.json"


ZONE_SECTION_HEADING = "### Zone-Specific Configuration"

# Canonical display names used in Zone-Specific Configuration sections.
CANON_ZONE_LABELS = {
    "zone 1 (personal productivity)",
    "zone 2 (team collaboration)",
    "zone 3 (enterprise managed)",
}

# Patterns
RE_ZONE_ANY = re.compile(r"\bZone\s+[1-4]\b", re.IGNORECASE)
RE_ZONE_PAREN = re.compile(r"\b(Zone\s+[1-3])\s*\(([^)]+)\)", re.IGNORECASE)
RE_ZONE4 = re.compile(r"\bZone\s+4\b", re.IGNORECASE)
RE_ZONE4_NOSPACE = re.compile(r"\bZone4\b", re.IGNORECASE)
RE_ZONE4_KEYSTYLE = re.compile(r"\bzone4[_-][a-z0-9_\-]+\b", re.IGNORECASE)
RE_EXPECTED_COLON = re.compile(r"^\s*[-*]?\s*Expected:\s*", re.IGNORECASE | re.MULTILINE)


@dataclass
class FileFindings:
    path: str
    zone4_mentions: int
    ambiguous_zone_like_tokens: dict[str, int]
    zone_paren_mismatches: list[str]
    zone_mentions_outside_zone_section: int
    evidence_heading: str | None
    expected_colon_lines: int


def iter_control_files() -> list[Path]:
    # Only pillar content (controls) — excludes docs/reference/* index pages.
    # Control files are named like "1.1-...md" or "2.15-...md".
    control_name = re.compile(r"^\d+\.\d+-")
    roots = [
        CONTROLS_ROOT / "pillar-1-security",
        CONTROLS_ROOT / "pillar-2-management",
        CONTROLS_ROOT / "pillar-3-reporting",
        CONTROLS_ROOT / "pillar-4-sharepoint",
    ]
    files: list[Path] = []
    for root in roots:
        if root.exists():
            for p in root.rglob("*.md"):
                if control_name.match(p.name):
                    files.append(p)
    return sorted(files)


def _find_zone_section_span(text: str) -> tuple[int | None, int | None]:
    """Return (start, end) character offsets for the Zone-Specific Configuration section.

    End is either the next heading of level 2/3 (## or ###) after the zone heading,
    or EOF.
    """

    start = text.find(ZONE_SECTION_HEADING)
    if start == -1:
        return None, None

    # Find end: next heading after start.
    after = text[start + len(ZONE_SECTION_HEADING) :]
    # Next heading marker at start of a line.
    match = re.search(r"^#{2,3}\s+", after, flags=re.MULTILINE)
    if not match:
        return start, len(text)

    end = start + len(ZONE_SECTION_HEADING) + match.start()
    return start, end


def _evidence_heading(text: str) -> str | None:
    # We only care about a few known variants.
    if re.search(r"^###\s+Verification Evidence\s*$", text, flags=re.MULTILINE):
        return "Verification Evidence"
    if re.search(r"^###\s+Compliance Evidence Checklist\s*$", text, flags=re.MULTILINE):
        return "Compliance Evidence Checklist"
    return None


def audit_file(path: Path) -> FileFindings:
    text = path.read_text(encoding="utf-8")

    zone4_mentions = len(RE_ZONE4.findall(text))

    # Ambiguous tokens that look like a 4th governance zone but are usually example tag/value collisions.
    # We keep this separate from zone4_mentions (which is strictly the spaced "Zone 4" token).
    ambiguous_counts: dict[str, int] = {}
    zone4_nospace = len(RE_ZONE4_NOSPACE.findall(text))
    if zone4_nospace:
        ambiguous_counts["Zone4"] = zone4_nospace

    zone4_keystyle = RE_ZONE4_KEYSTYLE.findall(text)
    if zone4_keystyle:
        # Group all key-style matches under a single family to avoid a huge per-file dict.
        ambiguous_counts["zone4_* (key-style)"] = len(zone4_keystyle)

    zone_paren_mismatches: list[str] = []
    for m in RE_ZONE_PAREN.finditer(text):
        zone = m.group(1).strip().lower()
        paren = m.group(2).strip().lower()
        label = f"{zone} ({paren})"
        if label not in CANON_ZONE_LABELS:
            zone_paren_mismatches.append(label)

    start, end = _find_zone_section_span(text)
    if start is None:
        outside = text
    else:
        outside = text[:start] + text[end:]
    zone_mentions_outside = len(RE_ZONE_ANY.findall(outside))

    expected_colon_lines = len(RE_EXPECTED_COLON.findall(text))

    return FileFindings(
        path=str(path.relative_to(REPO_ROOT)).replace("\\", "/"),
        zone4_mentions=zone4_mentions,
        ambiguous_zone_like_tokens=ambiguous_counts,
        zone_paren_mismatches=sorted(set(zone_paren_mismatches)),
        zone_mentions_outside_zone_section=zone_mentions_outside,
        evidence_heading=_evidence_heading(text),
        expected_colon_lines=expected_colon_lines,
    )


def main() -> int:
    REPORTS_ROOT.mkdir(parents=True, exist_ok=True)

    files = iter_control_files()
    findings = [audit_file(p) for p in files]

    # Aggregate
    zone4_files = [f for f in findings if f.zone4_mentions]
    ambiguous_zone_like_files = [f for f in findings if f.ambiguous_zone_like_tokens]
    paren_mismatch_files = [f for f in findings if f.zone_paren_mismatches]
    zone_leak_files = [f for f in findings if f.zone_mentions_outside_zone_section]
    expected_files = [f for f in findings if f.expected_colon_lines]

    evidence_counts: dict[str, int] = {}
    for f in findings:
        key = f.evidence_heading or "(none)"
        evidence_counts[key] = evidence_counts.get(key, 0) + 1

    report = {
        "summary": {
            "total_controls": len(findings),
            "files_with_zone4": len(zone4_files),
            "files_with_ambiguous_zone_like_tokens": len(ambiguous_zone_like_files),
            "files_with_zone_paren_mismatch": len(paren_mismatch_files),
            "files_with_zone_mentions_outside_zone_section": len(zone_leak_files),
            "files_with_expected_colon_lines": len(expected_files),
            "evidence_heading_counts": dict(sorted(evidence_counts.items(), key=lambda kv: (-kv[1], kv[0]))),
        },
        "files": [f.__dict__ for f in findings],
    }

    REPORT_JSON.write_text(json.dumps(report, indent=2), encoding="utf-8", newline="\n")

    def top_paths(items: list[FileFindings], n: int = 8) -> list[str]:
        return [i.path for i in sorted(items, key=lambda x: (-x.zone_mentions_outside_zone_section, x.path))[:n]]

    md_lines: list[str] = []
    md_lines.append("# Zone Hygiene Audit (Controls)\n")
    md_lines.append("This report is generated by `scripts/audit_controls_zone_hygiene.py`.\n")

    s = report["summary"]
    md_lines.append("## Summary\n")
    md_lines.append(f"- Total controls: **{s['total_controls']}**\n")
    md_lines.append(f"- Files with legacy `Zone 4` mentions: **{s['files_with_zone4']}**\n")
    md_lines.append(
        f"- Files with ambiguous zone-like tokens (`Zone4`, `zone4_*`): **{s['files_with_ambiguous_zone_like_tokens']}**\n"
    )
    md_lines.append(f"- Files with `Zone X ( ... )` label drift: **{s['files_with_zone_paren_mismatch']}**\n")
    md_lines.append(
        f"- Files with zone mentions outside `{ZONE_SECTION_HEADING}`: **{s['files_with_zone_mentions_outside_zone_section']}**\n"
    )
    md_lines.append(f"- Files with `Expected:` formatting drift: **{s['files_with_expected_colon_lines']}**\n")

    md_lines.append("## Evidence Heading Usage\n")
    for k, v in s["evidence_heading_counts"].items():
        md_lines.append(f"- {k}: {v}\n")

    md_lines.append("\n## Priority Buckets\n")

    md_lines.append("### Legacy `Zone 4` Mentions\n")
    if zone4_files:
        for f in zone4_files:
            md_lines.append(f"- {f.path} ({f.zone4_mentions})\n")
    else:
        md_lines.append("- None\n")

    md_lines.append("\n### Ambiguous Zone-like Tokens (Not Governance Zones)\n")
    md_lines.append("These tokens often appear in examples as tag/value collisions. The governance model is strictly Zones 1-3.\n")
    if ambiguous_zone_like_files:
        for f in sorted(ambiguous_zone_like_files, key=lambda x: (x.path))[:20]:
            details = ", ".join(f"{k}={v}" for k, v in sorted(f.ambiguous_zone_like_tokens.items()))
            md_lines.append(f"- {f.path}: {details}\n")
        if len(ambiguous_zone_like_files) > 20:
            md_lines.append(f"- ...and {len(ambiguous_zone_like_files) - 20} more\n")
    else:
        md_lines.append("- None\n")

    md_lines.append("\n### Zone Label Drift (Zone 1/2/3 with non-canonical parentheses)\n")
    if paren_mismatch_files:
        for f in paren_mismatch_files[:20]:
            md_lines.append(f"- {f.path}: {', '.join(f.zone_paren_mismatches)}\n")
        if len(paren_mismatch_files) > 20:
            md_lines.append(f"- ...and {len(paren_mismatch_files) - 20} more\n")
    else:
        md_lines.append("- None\n")

    md_lines.append(f"\n### Zone Mentions Outside `{ZONE_SECTION_HEADING}`\n")
    if zone_leak_files:
        for f in sorted(zone_leak_files, key=lambda x: (-x.zone_mentions_outside_zone_section, x.path))[:20]:
            md_lines.append(f"- {f.path} ({f.zone_mentions_outside_zone_section})\n")
        if len(zone_leak_files) > 20:
            md_lines.append(f"- ...and {len(zone_leak_files) - 20} more\n")
    else:
        md_lines.append("- None\n")

    md_lines.append("\n### Expected: Formatting Drift\n")
    if expected_files:
        for f in sorted(expected_files, key=lambda x: (-x.expected_colon_lines, x.path))[:20]:
            md_lines.append(f"- {f.path} ({f.expected_colon_lines})\n")
        if len(expected_files) > 20:
            md_lines.append(f"- ...and {len(expected_files) - 20} more\n")
    else:
        md_lines.append("- None\n")

    REPORT_MD.write_text("".join(md_lines), encoding="utf-8", newline="\n")

    print(f"Wrote: {REPORT_MD}")
    print(f"Wrote: {REPORT_JSON}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
