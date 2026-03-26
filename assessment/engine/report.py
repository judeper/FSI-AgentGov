#!/usr/bin/env python3
"""FSI-AgentGov Assessment Report Generator.

Reads scored assessment results and the control manifest, then produces:

1. ``assessment-prefilled.md``  — full compliance report with evidence
2. ``manual-questionnaire.md``  — questions requiring stakeholder interview
3. ``assessment-summary.json``  — machine-readable summary

Usage::

    python report.py --scores <scores.json> --manifest <controls.json> \
                     --customer <name> --zone <1|2|3> --output-dir <path>
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

from jinja2 import Environment

log = logging.getLogger("fsi-agentgov-report")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ZONE_DESCRIPTIONS: dict[int, str] = {
    1: "Personal / Low Risk",
    2: "Team / Medium Risk",
    3: "Enterprise / Production",
}

MATURITY_LABELS: dict[int, str] = {
    0: "Not Implemented",
    1: "Aware",
    2: "Recommended",
    3: "Optimized",
    4: "Fully Governed",
}

# ---------------------------------------------------------------------------
# Jinja2 inline templates
# ---------------------------------------------------------------------------

PREFILLED_TEMPLATE = r"""# FSI-AgentGov Automated Assessment

**Customer:** {{ customer }}
**Assessment Date:** {{ date }}
**Assessed Zone:** Zone {{ zone }} — {{ zone_description }}
**Auto-scored:** {{ auto_scored }}/{{ total_controls }} controls | **Requires manual input:** {{ needs_manual }} controls
**Overall Maturity:** {{ average_maturity }} / 4.0

---
{% for pillar_id, pillar in pillars.items() %}

## Pillar {{ pillar_id }} – {{ pillar.name }} ({{ pillar.controls | length }} controls)
{% for ctrl in pillar.controls %}

### Control {{ ctrl.control_id }} – {{ ctrl.title }}
**Maturity Score:** {{ ctrl.maturity_score }}/4 | **Confidence:** {{ ctrl.confidence | title }} | **Status:** {{ ctrl.status }}

| Check | Result | Evidence |
|-------|--------|----------|
{% for row in ctrl.evidence_rows -%}
| {{ row.description }} | {{ row.icon }} {{ row.result_label }} | {{ row.value }} ({{ row.source_label }}, {{ row.date }}) |
{% endfor %}
{% if ctrl.gap -%}
**Gap:** {{ ctrl.gap }}
{% endif %}
{% if ctrl.needs_manual -%}
**Manual Question:** {{ ctrl.manual_question }}
{% endif %}
---
{% endfor %}
{% endfor %}
"""

QUESTIONNAIRE_TEMPLATE = r"""# FSI-AgentGov Manual Assessment Questions

**Assessor:** _______________
**Date:** _______________
**Customer:** {{ customer }}

Complete these questions via stakeholder interview. Each answer should
include the respondent's name, role, and date.

---
{% for pillar_id, pillar in pillars.items() %}
{% if pillar.manual_controls %}

## Pillar {{ pillar_id }} – {{ pillar.name }}
{% for ctrl in pillar.manual_controls %}

**{{ ctrl.control_id }} – {{ ctrl.title }}**
*Automated checks found: {{ ctrl.auto_summary }}*

> {{ ctrl.manual_question }}

Answer: _______________________________________________
Respondent: _____________________ Role: _____________ Date: ________
Evidence reference (document name or location): _______________________

---
{% endfor %}
{% endif %}
{% endfor %}
"""

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def derive_status(control: dict) -> str:
    """Derive a human-readable status string for a scored control."""
    checks_total = control.get("checks_total", 0)
    checks_passed = control.get("checks_passed", 0)
    checks_failed = control.get("checks_failed", [])
    needs_manual = control.get("needs_manual", False)
    maturity = control.get("maturity_score", 0)

    if checks_total == 0:
        return "Needs Manual Review" if needs_manual else "No Checks Defined"

    if maturity == 0 and checks_passed == 0:
        return "Not Implemented"

    if not checks_failed and checks_passed == checks_total:
        return "Full Compliance"

    if checks_failed:
        return "Partial Gap"

    # All applicable checks are either passed or unknown
    if checks_passed < checks_total:
        return "Partial Gap"

    return "Full Compliance"


def _result_icon(result: str) -> str:
    return {"pass": "✅", "fail": "❌"}.get(result, "⚠️")


def _result_label(result: str) -> str:
    return {"pass": "PASS", "fail": "FAIL"}.get(result, "UNKNOWN")


def generate_gap_description(control: dict) -> str | None:
    """Build a concise, actionable gap description from failed checks."""
    failed_ids = set(control.get("checks_failed", []))
    if not failed_ids:
        return None

    checks = control.get("checks", [])
    parts: list[str] = []
    for chk in checks:
        if chk["check_id"] in failed_ids:
            desc = chk.get("description", "")
            ev = chk.get("evidence", "")
            if desc and ev:
                parts.append(f"{desc} — {ev}")
            elif desc:
                parts.append(desc)
    return "; ".join(parts) if parts else None


def build_auto_summary(control: dict) -> str:
    """One-line summary of automated check results for the questionnaire."""
    total = control.get("checks_total", 0)
    passed = control.get("checks_passed", 0)
    if total == 0:
        return "no automated checks for this control"
    return f"{passed}/{total} automated checks passed"


# ---------------------------------------------------------------------------
# Data preparation
# ---------------------------------------------------------------------------


def prepare_report_data(
    scores: dict,
    manifest: dict,
    customer: str,
    zone: int,
) -> dict:
    """Transform raw scores into template-ready data structures."""
    summary = scores.get("summary", {})
    controls = scores.get("controls", [])
    assessment_ts = summary.get(
        "assessment_timestamp",
        scores.get("_metadata", {}).get("timestamp", ""),
    )
    date_str = assessment_ts[:10] if assessment_ts else datetime.now(
        timezone.utc
    ).strftime("%Y-%m-%d")

    # Build check-description lookup from manifest
    manifest_checks: dict[str, dict] = {}
    for mc in manifest.get("controls", []):
        for chk in mc.get("checks", []):
            manifest_checks[chk["check_id"]] = chk

    # Group controls by pillar
    pillars: dict[str, dict] = {}
    for ctrl in controls:
        pid = str(ctrl["pillar"])
        if pid not in pillars:
            pillars[pid] = {
                "name": ctrl["pillar_name"],
                "controls": [],
                "manual_controls": [],
            }

        status = derive_status(ctrl)

        # Evidence rows for the markdown table
        evidence_rows: list[dict] = []
        evidence_dict = ctrl.get("evidence", {})
        checks_list = ctrl.get("checks", [])
        check_desc_map: dict[str, str] = {
            c["check_id"]: c.get("description", c["check_id"])
            for c in checks_list
        }

        for check_id, ev in evidence_dict.items():
            desc = check_desc_map.get(
                check_id,
                manifest_checks.get(check_id, {}).get(
                    "description", check_id
                ),
            )
            evidence_rows.append(
                {
                    "check_id": check_id,
                    "description": desc,
                    "icon": _result_icon(ev.get("result", "unknown")),
                    "result_label": _result_label(ev.get("result", "unknown")),
                    "value": ev.get("value", ""),
                    "source_label": ev.get("source") or "N/A",
                    "date": (ev.get("timestamp") or "")[:10],
                }
            )

        gap = generate_gap_description(ctrl)

        enriched = {
            "control_id": ctrl.get("control_id", ctrl.get("id", "")),
            "title": ctrl["title"],
            "pillar": ctrl["pillar"],
            "pillar_name": ctrl["pillar_name"],
            "maturity_score": ctrl["maturity_score"],
            "confidence": ctrl.get("confidence", "low"),
            "status": status,
            "checks_total": ctrl.get("checks_total", 0),
            "checks_passed": ctrl.get("checks_passed", 0),
            "checks_failed": ctrl.get("checks_failed", []),
            "evidence_rows": evidence_rows,
            "gap": gap,
            "needs_manual": ctrl.get("needs_manual", False),
            "manual_question": ctrl.get("manual_question"),
            "auto_summary": build_auto_summary(ctrl),
        }

        pillars[pid]["controls"].append(enriched)
        if enriched["needs_manual"] and enriched["manual_question"]:
            pillars[pid]["manual_controls"].append(enriched)

    return {
        "customer": customer,
        "date": date_str,
        "zone": zone,
        "zone_description": ZONE_DESCRIPTIONS.get(zone, "Unknown"),
        "total_controls": summary.get("total_controls", len(controls)),
        "auto_scored": summary.get("auto_scored", 0),
        "needs_manual": summary.get("needs_manual", 0),
        "average_maturity": summary.get("average_maturity", 0.0),
        "pillars": dict(sorted(pillars.items())),
        "summary": summary,
    }


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------


def generate_prefilled_md(data: dict) -> str:
    env = Environment(keep_trailing_newline=True)
    template = env.from_string(PREFILLED_TEMPLATE)
    return template.render(**data)


def generate_questionnaire_md(data: dict) -> str:
    env = Environment(keep_trailing_newline=True)
    template = env.from_string(QUESTIONNAIRE_TEMPLATE)
    return template.render(**data)


def generate_summary_json(
    data: dict,
    output_files: list[str],
) -> dict:
    """Build the machine-readable assessment-summary.json payload."""
    summary = dict(data.get("summary", {}))

    # Identify gaps — controls with maturity below the zone threshold
    gaps: list[str] = []
    critical_gaps: list[str] = []
    for pillar in data.get("pillars", {}).values():
        for ctrl in pillar.get("controls", []):
            if ctrl["status"] in ("Not Implemented", "Partial Gap"):
                cid = ctrl["control_id"]
                gaps.append(cid)
                if ctrl["maturity_score"] == 0:
                    critical_gaps.append(cid)

    summary.update(
        {
            "customer_name": data["customer"],
            "assessment_date": data["date"],
            "zone_assessed": data["zone"],
            "zone_description": data["zone_description"],
            "files_generated": output_files,
            "gaps": sorted(gaps),
            "critical_gaps": sorted(critical_gaps),
        }
    )
    return summary


# ---------------------------------------------------------------------------
# Entry points
# ---------------------------------------------------------------------------


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="FSI-AgentGov Assessment Report Generator",
    )
    parser.add_argument(
        "--scores",
        required=True,
        help="Path to scores.json (output of score.py)",
    )
    parser.add_argument(
        "--manifest",
        required=True,
        help="Path to controls.json manifest",
    )
    parser.add_argument(
        "--customer",
        required=True,
        help="Customer name for the report header",
    )
    parser.add_argument(
        "--zone",
        required=True,
        type=int,
        choices=[1, 2, 3],
        help="Governance zone assessed (1, 2, or 3)",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory to write the three output files",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )
    return parser.parse_args(argv)


def run(
    scores_path: str,
    manifest_path: str,
    customer: str,
    zone: int,
    output_dir: str,
) -> dict:
    """Execute the report generator and return the summary dict.

    Can be called programmatically or via the CLI.
    """
    scores_p = Path(scores_path)
    manifest_p = Path(manifest_path)
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    log.info("Loading scores from %s", scores_p)
    scores = load_json(scores_p)

    log.info("Loading manifest from %s", manifest_p)
    manifest = load_json(manifest_p)

    data = prepare_report_data(scores, manifest, customer, zone)

    # --- 1. assessment-prefilled.md ---
    prefilled_path = out_dir / "assessment-prefilled.md"
    prefilled_md = generate_prefilled_md(data)
    prefilled_path.write_text(prefilled_md, encoding="utf-8")
    log.info("Wrote %s", prefilled_path)

    # --- 2. manual-questionnaire.md ---
    questionnaire_path = out_dir / "manual-questionnaire.md"
    questionnaire_md = generate_questionnaire_md(data)
    questionnaire_path.write_text(questionnaire_md, encoding="utf-8")
    log.info("Wrote %s", questionnaire_path)

    # --- 3. assessment-summary.json ---
    output_files = [
        str(prefilled_path),
        str(questionnaire_path),
    ]
    summary_path = out_dir / "assessment-summary.json"
    output_files.append(str(summary_path))

    summary = generate_summary_json(data, output_files)
    with open(summary_path, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2, ensure_ascii=False)
    log.info("Wrote %s", summary_path)

    return summary


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )
    try:
        summary = run(
            args.scores,
            args.manifest,
            args.customer,
            args.zone,
            args.output_dir,
        )
        print(f"\nReport generation complete")
        print(f"  Customer:    {summary.get('customer_name', '?')}")
        print(f"  Zone:        {summary.get('zone_assessed', '?')}")
        print(f"  Gaps:        {len(summary.get('gaps', []))}")
        print(f"  Critical:    {len(summary.get('critical_gaps', []))}")
        print(f"  Files:       {len(summary.get('files_generated', []))}")
        for fp in summary.get("files_generated", []):
            print(f"    → {fp}")
    except Exception as exc:
        log.error("Report generation failed: %s", exc, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
