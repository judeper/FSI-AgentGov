#!/usr/bin/env python3
"""Generate the 78-control × 6-pattern CAPE coverage matrix.

Reads ``assessment/manifest/controls.json`` and writes a Markdown matrix
to ``docs/reference/pattern-coverage.md`` showing which controls apply to
which Microsoft CAPE Frontier Transformation Patterns and which are
pattern-critical.

Run::

    python scripts/generate_pattern_coverage.py

CI may also call this with ``--check`` to fail when the doc is stale.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = REPO_ROOT / "assessment" / "manifest" / "controls.json"
OUTPUT_PATH = REPO_ROOT / "docs" / "reference" / "pattern-coverage.md"

PATTERNS: dict[int, tuple[str, str]] = {
    1: ("Employee AI Enablement", "Z1 (Personal)"),
    2: ("Business Expert Empowerment", "Z2 (Team)"),
    3: ("Workplace & IT Services", "Z2 (Team)"),
    4: ("Core Business Process Transformation", "Z3 (Enterprise)"),
    5: ("External Engagement", "Z3 (Enterprise)"),
    6: ("AI-First Capabilities", "Z3 (Enterprise) — D3 guardrail applies"),
}

PILLAR_CONTROL_COUNTS = {1: 29, 2: 26, 3: 14, 4: 9}

PILLAR_NAMES = {
    1: "Security",
    2: "Management",
    3: "Reporting",
    4: "SharePoint",
}


def load_controls() -> list[dict]:
    raw = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return raw if isinstance(raw, list) else raw.get("controls", [])


def applicable_patterns(ctrl: dict) -> list[int]:
    return ctrl.get("applicable_patterns") or list(PATTERNS.keys())


def pattern_critical(ctrl: dict) -> list[int]:
    return ctrl.get("pattern_critical") or []


def render(controls: list[dict]) -> str:  # noqa: PLR0912
    total_controls = len(controls)

    # Pre-compute per-pattern counts
    ap_counts: Counter = Counter()
    pc_counts: Counter = Counter()
    for ctrl in controls:
        for pid in applicable_patterns(ctrl):
            ap_counts[pid] += 1
        for pid in pattern_critical(ctrl):
            pc_counts[pid] += 1

    # Group controls by pillar
    pillars: dict[int, list[dict]] = {}
    for ctrl in controls:
        pillars.setdefault(int(ctrl["pillar"]), []).append(ctrl)

    lines: list[str] = []

    # --- Header ---
    lines.append("# CAPE Pattern Coverage Matrix")
    lines.append("")
    lines.append(
        "This page is **generated** by `scripts/generate_pattern_coverage.py` "
        "from `assessment/manifest/controls.json`. Do not edit by hand."
    )
    lines.append("")
    lines.append(
        f"It maps the {total_controls} FSI-AgentGov controls to the "
        f"{len(PATTERNS)} Microsoft CAPE Frontier Transformation Patterns. "
        "For each control:"
    )
    lines.append("")
    lines.append(
        "- The **Patterns** column lists patterns where the control applies "
        "(`applicable_patterns`)."
    )
    lines.append(
        "- The **Critical For** column lists patterns where the control is "
        "mission-critical (`pattern_critical`)."
    )
    lines.append(
        "- A pattern-critical control means failure in that control would "
        "block the named pattern's deployment. Use this lens during "
        "pattern-specific risk reviews."
    )
    lines.append("")

    # --- Pattern legend ---
    lines.append("## Pattern legend")
    lines.append("")
    lines.append("| ID | Pattern | Default zones |")
    lines.append("|---|---|---|")
    for pid, (name, zones) in PATTERNS.items():
        lines.append(f"| {pid} | {name} | {zones} |")
    lines.append("")

    # --- Coverage summary ---
    lines.append("## Coverage summary")
    lines.append("")
    lines.append("| Pattern | Total controls applicable | Pattern-critical controls |")
    lines.append("|---|---|---|")
    for pid, (name, _) in PATTERNS.items():
        lines.append(
            f"| {pid} \u2014 {name} | {ap_counts[pid]} | {pc_counts[pid]} |"
        )
    lines.append("")

    # --- Pattern-critical controls section ---
    lines.append("## Pattern-critical controls")
    lines.append("")
    lines.append(
        "The following controls are flagged as mission-critical for one or more "
        "patterns. Failure in any of these blocks the named pattern's safe "
        "deployment."
    )
    lines.append("")

    for pid, (name, _) in PATTERNS.items():
        critical_for_pattern = [
            ctrl for ctrl in controls if pid in pattern_critical(ctrl)
        ]
        if not critical_for_pattern:
            continue
        lines.append(f"### Pattern {pid} \u2014 {name}")
        lines.append("")
        for ctrl in sorted(critical_for_pattern, key=lambda c: c["id"]):
            title = ctrl["title"].replace("|", "\\|")
            lines.append(f"- **{ctrl['id']}** {title}")
        lines.append("")

    # --- Per-pillar matrix ---
    lines.append("## Per-pillar control \u00d7 pattern matrix")
    lines.append("")

    for pillar_id in sorted(pillars):
        pname = PILLAR_NAMES.get(pillar_id, f"Pillar {pillar_id}")
        ctrl_count = len(pillars[pillar_id])
        lines.append(f"### Pillar {pillar_id} \u2014 {pname} ({ctrl_count} controls)")
        lines.append("")
        # Table header
        pat_headers = " | ".join(f"P{p}" for p in sorted(PATTERNS))
        lines.append(f"| Control | Title | {pat_headers} | Critical For |")
        sep_cols = " | ".join("----" for _ in PATTERNS)
        lines.append(f"|---------|-------|{sep_cols}|--------------|")

        for ctrl in sorted(pillars[pillar_id], key=lambda c: c["id"]):
            title = ctrl["title"].replace("|", "\\|")
            ap = set(applicable_patterns(ctrl))
            pc = set(pattern_critical(ctrl))

            cells: list[str] = []
            for pid in sorted(PATTERNS):
                if pid in pc:
                    cells.append("\U0001f3af")  # 🎯
                elif pid in ap:
                    cells.append("\u2705")  # ✅
                else:
                    cells.append("\u2014")  # —

            critical_label = (
                ", ".join(f"P{p}" for p in sorted(pc)) if pc else "\u2014"
            )
            row = " | ".join(cells)
            lines.append(f"| {ctrl['id']} | {title} | {row} | {critical_label} |")

        lines.append("")

    lines.append(
        "<!-- This page is generated by scripts/generate_pattern_coverage.py. "
        "Do not edit by hand. -->"
    )
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit non-zero if the generated content differs from disk.",
    )
    parser.add_argument(
        "--output",
        default=str(OUTPUT_PATH),
        help="Override output path (default: docs/reference/pattern-coverage.md)",
    )
    args = parser.parse_args(argv)

    controls = load_controls()
    rendered = render(controls)
    target = Path(args.output)

    if args.check:
        if not target.exists():
            print(
                f"ERROR: {target} does not exist. Run "
                "`python scripts/generate_pattern_coverage.py` to create it.",
                file=sys.stderr,
            )
            return 1
        existing = target.read_text(encoding="utf-8")
        if existing != rendered:
            print(
                f"ERROR: {target} is out of date. Run "
                "`python scripts/generate_pattern_coverage.py` and commit.",
                file=sys.stderr,
            )
            return 1
        print(f"OK: {target} is current.")
        return 0

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(rendered, encoding="utf-8")
    print(f"Wrote {target} ({len(controls)} controls).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
