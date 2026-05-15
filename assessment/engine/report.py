#!/usr/bin/env python3
"""FSI-AgentGov Assessment Report Generator.

Reads scored assessment results and the control manifest, then produces:

1. ``assessment-prefilled.md``  — full compliance report with evidence
2. ``manual-questionnaire.md``  — questions requiring stakeholder interview
3. ``assessment-summary.json``  — machine-readable summary

Frontier mode (``--type frontier``) reads a frontier-summary.json and
frontier-readiness.json manifest to produce:

4. ``frontier-prefilled.md``   — Frontier Readiness assessment report

Combined mode (``--type both``) produces all of the above plus:

5. ``capability-driver-rollup.json`` — control maturity rolled up by driver

Usage::

    python report.py --scores <scores.json> --manifest <controls.json> \\
                     --customer <name> --zone <1|2|3> --output-dir <path>

    python report.py --type frontier \\
                     --frontier-summary <frontier-summary.json> \\
                     --frontier-manifest <frontier-readiness.json> \\
                     --customer <name> --output-dir <path>

    python report.py --type both \\
                     --scores <scores.json> --manifest <controls.json> \\
                     --frontier-summary <frontier-summary.json> \\
                     --frontier-manifest <frontier-readiness.json> \\
                     --customer <name> --zone <1|2|3> --output-dir <path>
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

from jinja2 import Environment, select_autoescape

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

PATTERN_NAMES: dict[int, str] = {
    1: "Employee AI Enablement",
    2: "Business Expert Empowerment",
    3: "Workplace & IT Services",
    4: "Core Business Process Transformation",
    5: "External Engagement",
    6: "AI-First Capabilities",
}

FRONTIER_DRIVER_IDS: tuple[str, ...] = (
    "ai_strategy",
    "business_strategy",
    "ai_governance",
    "technology_data",
    "organization_culture",
)

FRONTIER_LEVEL_LABELS: dict[int, str] = {
    100: "Initial",
    200: "Repeatable",
    300: "Defined",
    400: "Capable",
    500: "Optimized",
}

CONFIDENCE_WEIGHTS: dict[str, float] = {
    "high": 1.0,
    "medium": 0.5,
    "low": 0.25,
}

ENGINE_VERSION = "1.0.0"


def _read_framework_version() -> str:
    """Read FSI-AgentGov framework version from repo-root VERSION file.

    Single source of truth for the framework release the engine was built
    against (e.g., "1.6.2"). Returns "unknown" if VERSION is missing.
    """
    version_file = Path(__file__).resolve().parents[2] / "VERSION"
    if version_file.exists():
        return version_file.read_text(encoding="utf-8").strip()
    return "unknown"


FRAMEWORK_VERSION = _read_framework_version()


def normalize_manifest_controls(raw: object) -> list[dict]:
    """Return the controls list regardless of manifest top-level shape.

    The on-disk ``assessment/manifest/controls.json`` is a bare JSON list
    of 78 control objects. Earlier engine code assumed a dict-wrapped
    form ``{"controls": [...]}`` and crashed against the real file with
    ``AttributeError: 'list' object has no attribute 'get'``. This helper
    accepts either shape so the engine runs end-to-end against the
    production manifest. Closes F-MANIFEST-FORMAT-MISMATCH-01.
    """
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict):
        return raw.get("controls", [])
    raise TypeError(
        f"Manifest must be list or dict; got {type(raw).__name__}"
    )


# ---------------------------------------------------------------------------
# Jinja2 inline templates
# ---------------------------------------------------------------------------

PREFILLED_TEMPLATE = r"""# FSI-AgentGov Automated Assessment

**Customer:** {{ customer }}
**Framework Version:** v{{ framework_version }}
**Assessment Date:** {{ date }}
**Assessed Zone:** Zone {{ zone }} — {{ zone_description }}
**Auto-scored:** {{ auto_scored }}/{{ total_controls }} controls | **Requires manual input:** {{ needs_manual }} controls
**Overall Maturity:** {{ average_maturity }} / 4.0

---
{% for pillar_id, pillar in pillars.items() %}

## Pillar {{ pillar_id }} – {{ pillar.name }} ({{ pillar.controls | length }} controls)
{% for ctrl in pillar.controls %}

### Control {{ ctrl.control_id }} – {{ ctrl.title }}
**Maturity Score:** {{ ctrl.maturity_score }}/4 | **Confidence:** {{ ctrl.confidence | title }} | **Status:** {{ ctrl.status }} | **Evaluator:** {{ ctrl.evaluator_state }}

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
**Framework Version:** v{{ framework_version }}

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

FRONTIER_PREFILLED_TEMPLATE = r"""# Frontier Readiness Assessment

**Customer:** {{ customer }}
**Framework Version:** v{{ framework_version }}
**Assessment Date:** {{ date }}
**Facilitator:** {{ facilitator }}
**Drivers Assessed:** {{ drivers_assessed }}

---

## Executive Summary

{{ overall_posture }}

!!! warning "Scale-Breaker: {{ scale_breaker_name }}"
    **{{ scale_breaker_name }}** (score: {{ scale_breaker_score }}) is the lowest-scoring driver and caps transformation scale regardless of strength in other areas.{{ " Tied with: " + tied_with_names + "." if tied_with_names else "" }}

### Pattern Readiness Summary

| Pattern | Ready? |
|---------|--------|
{% for p in patterns -%}
| {{ p.id }}. {{ p.name }} | {{ p.ready_icon }} {{ p.ready_label }} |
{% endfor %}
---

## Driver Scores

| Driver | Score | Level | FSI Translation | Recommended Next Action |
|--------|-------|-------|-----------------|-------------------------|
{% for d in drivers_table -%}
| {{ d.name }} | {{ d.score }} | {{ d.level_label }} | {{ d.fsi_translation }} | {{ d.next_action }} |
{% endfor %}
---

## Scale-Breaker Analysis

**Scale-breaker driver:** {{ scale_breaker_name }} (score: {{ scale_breaker_score }})

{{ scale_breaker_rationale }}
{% if tied_with_names %}
**Tied with:** {{ tied_with_names }}
{% endif %}
### Recommended Remediation

{{ remediation_bullets }}

{{ controls_anchor }}

---

## Pattern Readiness

| Pattern | Ready? | Min Gap | Gap Drivers | FSI Notes |
|---------|--------|---------|-------------|-----------|
{% for p in patterns -%}
| {{ p.id }}. {{ p.name }} | {{ p.ready_icon }} {{ p.ready_label }} | {{ p.min_gap_display }} | {{ p.gap_drivers_str }} | {{ p.fsi_notes }} |
{% endfor %}
---

## Question-Level Detail
{% for driver_section in question_detail %}

### {{ driver_section.name }}
{% for q in driver_section.questions %}

**{{ q.question_id }}** *{{ q.driver_name }} — {{ q.level_label }} (L{{ q.level }})*: {{ q.question_text }}

- **Answer:** {{ q.answer_icon }} {{ q.answer_display }}
- **Evidence:** {{ q.evidence_note if q.evidence_note else "—" }}
- **Respondent:** {{ q.respondent if q.respondent else "—" }}
{% endfor %}
{% endfor %}

---

## Methodology and Limitations

This Frontier Readiness assessment is a facilitator-led, self-attested diagnostic across 5 capability drivers. It supplements but does not replace the FSI-AgentGov 78-control technical assessment. Driver scores reflect organizational maturity claims at the time of assessment; they are not auditor-grade evidence and do not substitute for examiner-defensible control evidence collected through the controls assessment engine.
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
# Frontier helpers
# ---------------------------------------------------------------------------


def _render_frontier_answer_icon(value: str | int | float | None) -> str:
    """Return an emoji icon for a frontier answer value."""
    if value is None:
        return "—"
    if isinstance(value, str):
        sv = value.strip().lower()
        return {"yes": "✅", "partial": "⚠️", "no": "❌"}.get(sv, "—")
    if isinstance(value, (int, float)):
        if value >= 4:
            return "✅"
        if value >= 2:
            return "⚠️"
        return "❌"
    return "—"


def _load_frontier_collected(output_dir: Path) -> dict[str, dict]:
    """Load frontier.json answers from the collected sub-directory if present."""
    collected_path = output_dir / "collected" / "frontier.json"
    if not collected_path.is_file():
        return {}
    try:
        with open(collected_path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        return data.get("answers", {}) or {}
    except Exception:
        log.warning("Could not load frontier collected answers from %s", collected_path)
        return {}


def _next_level_action(score: int) -> str:
    """One-sentence recommendation for advancing to the next maturity level."""
    if score >= 500:
        return "Maintain at L500 through a documented continuous-improvement cadence."
    if score >= 400:
        return "Address L500 (Optimized) requirements to reach full frontier maturity."
    if score >= 300:
        return "Address L400 (Capable) requirements to advance beyond the Defined stage."
    if score >= 200:
        return "Address L300 (Defined) requirements to move beyond repeatable practices."
    if score >= 100:
        return "Address L200 (Repeatable) requirements to establish consistent practices."
    return "Address L100 (Initial) requirements to establish baseline accountability."


def _scale_breaker_remediation(driver_name: str) -> str:
    """Markdown bullet list of remediation steps for the scale-breaker driver."""
    lines = [
        (
            f"Identify the level-stratified questions for **{driver_name}** that received"
            " 'no' or 'partial' answers and assign a named owner to each."
        ),
        (
            "Set target dates for each remediation action and track progress"
            " in the governance cadence review."
        ),
        (
            "Schedule a follow-up facilitated Frontier Readiness session within 90 days"
            " to re-assess this driver."
        ),
        (
            "Prioritize remediations that unblock the highest-priority"
            " Frontier Transformation Pattern for the organization."
        ),
        (
            "Review related FSI-AgentGov technical controls mapped to this driver"
            " to identify complementary technical gaps."
        ),
    ]
    return "\n".join(f"- {line}" for line in lines)


def _overall_posture_summary(driver_scores: dict) -> str:
    """One-line overall posture statement for the Executive Summary."""
    if not driver_scores:
        return "Frontier Readiness assessment is pending — no driver scores available."
    all_scores = [d.get("score", 0) for d in driver_scores.values()]
    avg = sum(all_scores) / len(all_scores)
    min_score = min(all_scores)
    if avg >= 400:
        posture = "Strong"
    elif avg >= 300:
        posture = "Advancing"
    elif avg >= 200:
        posture = "Developing"
    else:
        posture = "Early-stage"
    return (
        f"{posture} Frontier Readiness posture "
        f"(average driver score {avg:.0f}/500; scale-breaker at {min_score})."
    )


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
    for mc in normalize_manifest_controls(manifest):
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
            "evaluator_state": ctrl.get("evaluator_state", "manual_only"),
            "evaluator_state_breakdown": ctrl.get(
                "evaluator_state_breakdown", {}
            ),
        }

        pillars[pid]["controls"].append(enriched)
        if enriched["needs_manual"] and enriched["manual_question"]:
            pillars[pid]["manual_controls"].append(enriched)

    return {
        "customer": customer,
        "date": date_str,
        "framework_version": FRAMEWORK_VERSION,
        "zone": zone,
        "zone_description": ZONE_DESCRIPTIONS.get(zone, "Unknown"),
        "total_controls": summary.get("total_controls", len(controls)),
        "auto_scored": summary.get("auto_scored", 0),
        "needs_manual": summary.get("needs_manual", 0),
        "average_maturity": summary.get("average_maturity", 0.0),
        "pillars": dict(sorted(pillars.items())),
        "summary": summary,
    }


def prepare_frontier_data(
    frontier_summary: dict,
    frontier_manifest: dict,
    customer: str,
    output_dir: Path,
    zone: int | None = None,
    controls_manifest: dict | None = None,
) -> dict:
    """Transform frontier-summary.json and manifest into template-ready data."""
    metadata = frontier_summary.get("_metadata", {})
    driver_scores = frontier_summary.get("driver_scores", {})
    scale_breaker = frontier_summary.get("scale_breaker", {})
    pattern_readiness = frontier_summary.get("pattern_readiness", {})
    questions_list: list[dict] = frontier_manifest.get("questions", [])
    drivers_list: list[dict] = frontier_manifest.get("drivers", [])

    # Load answers from collected frontier.json when available
    answers = _load_frontier_collected(output_dir)

    # Build driver lookup: id -> manifest driver dict
    driver_lookup: dict[str, dict] = {d["id"]: d for d in drivers_list if "id" in d}
    for did in FRONTIER_DRIVER_IDS:
        if did not in driver_lookup:
            driver_lookup[did] = {
                "id": did,
                "name": did.replace("_", " ").title(),
                "fsi_translation": "",
            }

    # Date
    ts = metadata.get("timestamp", "")
    date_str = ts[:10] if ts else datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Scale-breaker info
    sb_driver_id = scale_breaker.get("driver") or ""
    sb_driver_name = driver_lookup.get(sb_driver_id, {}).get("name", sb_driver_id)
    sb_score = scale_breaker.get("score") or 0
    sb_tied_with: list[str] = scale_breaker.get("tied_with") or []
    tied_with_names = ", ".join(
        driver_lookup.get(t, {}).get("name", t) for t in sb_tied_with
    )
    sb_rationale = scale_breaker.get("rationale", "")

    # Patterns
    patterns = []
    for pid in range(1, 7):
        key = str(pid)
        pr = pattern_readiness.get(key, {})
        ready = pr.get("ready", False)
        min_gap = pr.get("min_gap", 0)
        gap_drivers_raw: list[dict] = pr.get("gap_drivers", []) or []
        gap_drivers_str = (
            ", ".join(
                driver_lookup.get(g["driver"], {}).get("name", g["driver"])
                for g in gap_drivers_raw
            )
            if gap_drivers_raw
            else "—"
        )
        fsi_notes = (
            "⚠ Zone 3 deployments require documented regulator pre-approval (D3 guardrail)."
            if pid == 6
            else "—"
        )
        patterns.append(
            {
                "id": pid,
                "name": PATTERN_NAMES.get(pid, f"Pattern {pid}"),
                "ready": ready,
                "ready_icon": "✅" if ready else "❌",
                "ready_label": "Ready" if ready else "Not Ready",
                "min_gap": min_gap,
                "min_gap_display": str(min_gap) if min_gap > 0 else "—",
                "gap_drivers_str": gap_drivers_str,
                "fsi_notes": fsi_notes,
            }
        )

    # Driver scores table
    drivers_table = []
    for did in FRONTIER_DRIVER_IDS:
        ds = driver_scores.get(did, {})
        score = ds.get("score", 0)
        level_label = ds.get("level_label", "—")
        fsi_translation = driver_lookup.get(did, {}).get("fsi_translation", "—")
        drivers_table.append(
            {
                "name": driver_lookup.get(did, {}).get("name", did),
                "score": score,
                "level_label": level_label,
                "fsi_translation": fsi_translation,
                "next_action": _next_level_action(score),
            }
        )

    # Controls anchor for scale-breaker section
    if controls_manifest is not None and sb_driver_id:
        related_ids = sorted(
            c.get("id", "")
            for c in normalize_manifest_controls(controls_manifest)
            if sb_driver_id in (c.get("applicable_drivers") or [])
        )
        if related_ids:
            ids_str = ", ".join(related_ids)
            controls_anchor = (
                f"**See related FSI controls:** The following controls are mapped to the"
                f" **{sb_driver_name}** driver: {ids_str}."
            )
        else:
            controls_anchor = (
                f"**See related FSI controls:** No controls in the current manifest are"
                f" tagged to the **{sb_driver_name}** driver."
            )
    else:
        controls_anchor = (
            "**See related FSI controls:** Run the controls assessment to surface"
            " specific control gaps linked to the scale-breaker driver."
        )

    # Question-level detail grouped by driver
    question_detail = []
    for did in FRONTIER_DRIVER_IDS:
        driver_qs = sorted(
            [q for q in questions_list if q.get("driver") == did],
            key=lambda q: q.get("level", 0),
        )
        qs_rendered = []
        for q in driver_qs:
            qid = q.get("question_id", "")
            answer_obj = answers.get(qid)
            level = q.get("level", 0)
            level_label = FRONTIER_LEVEL_LABELS.get(level, str(level))
            if answer_obj is not None:
                raw_val = answer_obj.get("value")
                answer_icon = _render_frontier_answer_icon(raw_val)
                answer_display = (
                    "skipped" if raw_val is None else (raw_val if isinstance(raw_val, str) else str(raw_val))
                )
                evidence_note = answer_obj.get("evidence_note")
                respondent = answer_obj.get("respondent")
            else:
                answer_icon = "—"
                answer_display = "Not yet answered"
                evidence_note = None
                respondent = None
            qs_rendered.append(
                {
                    "question_id": qid,
                    "driver_name": driver_lookup.get(did, {}).get("name", did),
                    "level": level,
                    "level_label": level_label,
                    "question_text": q.get("question_text", ""),
                    "answer_icon": answer_icon,
                    "answer_display": answer_display,
                    "evidence_note": evidence_note,
                    "respondent": respondent,
                }
            )
        question_detail.append(
            {
                "name": driver_lookup.get(did, {}).get("name", did),
                "questions": qs_rendered,
            }
        )

    return {
        "customer": customer,
        "date": date_str,
        "framework_version": FRAMEWORK_VERSION,
        "facilitator": metadata.get("facilitator", "Facilitator-led self-diagnostic"),
        "drivers_assessed": 5,
        "overall_posture": _overall_posture_summary(driver_scores),
        "scale_breaker_name": sb_driver_name,
        "scale_breaker_score": sb_score,
        "scale_breaker_rationale": sb_rationale,
        "tied_with_names": tied_with_names,
        "patterns": patterns,
        "drivers_table": drivers_table,
        "remediation_bullets": _scale_breaker_remediation(sb_driver_name),
        "controls_anchor": controls_anchor,
        "question_detail": question_detail,
    }


def compute_driver_rollup(scores: dict, manifest: dict, zone: int) -> dict:
    """Compute capability-driver-rollup.json: control maturity indexed by Frontier driver."""
    controls = scores.get("controls", [])

    # Build manifest lookup: control_id -> applicable_drivers (None = field absent)
    manifest_applicable: dict[str, list[str] | None] = {
        mc.get("id", ""): mc.get("applicable_drivers")
        for mc in normalize_manifest_controls(manifest)
    }

    rollup: dict[str, dict] = {}
    for driver_id in FRONTIER_DRIVER_IDS:
        matched = [
            ctrl
            for ctrl in controls
            if (
                (applicable := manifest_applicable.get(ctrl.get("control_id", ctrl.get("id", ""))))
                is not None
                and driver_id in applicable
            )
        ]

        if not matched:
            rollup[driver_id] = {
                "control_count": 0,
                "average_maturity": 0.0,
                "weighted_average_maturity": 0.0,
                "confidence_distribution": {"high": 0, "medium": 0, "low": 0},
                "controls": [],
            }
            continue

        maturity_sum = 0.0
        weighted_sum = 0.0
        weight_total = 0.0
        conf_dist: dict[str, int] = {"high": 0, "medium": 0, "low": 0}
        ctrl_list: list[dict] = []

        for ctrl in matched:
            m = ctrl.get("maturity_score", 0)
            c = ctrl.get("confidence", "low")
            w = CONFIDENCE_WEIGHTS.get(c, 0.25)
            maturity_sum += m
            weighted_sum += m * w
            weight_total += w
            conf_dist[c] = conf_dist.get(c, 0) + 1
            ctrl_list.append(
                {
                    "id": ctrl.get("control_id", ctrl.get("id", "")),
                    "maturity": m,
                    "confidence": c,
                }
            )

        count = len(matched)
        avg = round(maturity_sum / count, 2)
        w_avg = round(weighted_sum / weight_total, 2) if weight_total > 0 else 0.0
        ctrl_list.sort(key=lambda x: x["id"])

        rollup[driver_id] = {
            "control_count": count,
            "average_maturity": avg,
            "weighted_average_maturity": w_avg,
            "confidence_distribution": conf_dist,
            "controls": ctrl_list,
        }

    return {
        "_metadata": {
            "engine_version": ENGINE_VERSION,
            "framework_version": FRAMEWORK_VERSION,
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "zone": zone,
        },
        "driver_rollups": rollup,
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
            "framework_version": data.get("framework_version", FRAMEWORK_VERSION),
            "assessment_date": data["date"],
            "zone_assessed": data["zone"],
            "zone_description": data["zone_description"],
            "files_generated": output_files,
            "gaps": sorted(gaps),
            "critical_gaps": sorted(critical_gaps),
        }
    )
    return summary


def generate_frontier_prefilled_md(data: dict) -> str:
    # Markdown output (not HTML); select_autoescape with no enabled
    # extensions is explicit and satisfies CodeQL py/jinja2-autoescape-false.
    env = Environment(
        keep_trailing_newline=True,
        autoescape=select_autoescape(enabled_extensions=(), default_for_string=False),
    )
    template = env.from_string(FRONTIER_PREFILLED_TEMPLATE)
    return template.render(**data)


def generate_frontier_report(
    frontier_summary_path: str,
    frontier_manifest_path: str,
    customer: str,
    output_dir: str,
    zone: int | None = None,
    controls_manifest: dict | None = None,
) -> Path:
    """Generate frontier-prefilled.md and return the output path."""
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    frontier_summary = load_json(Path(frontier_summary_path))
    frontier_manifest = load_json(Path(frontier_manifest_path))

    data = prepare_frontier_data(
        frontier_summary,
        frontier_manifest,
        customer,
        out_dir,
        zone=zone,
        controls_manifest=controls_manifest,
    )

    output_path = out_dir / "frontier-prefilled.md"
    output_path.write_text(generate_frontier_prefilled_md(data), encoding="utf-8")
    log.info("Wrote %s", output_path)
    return output_path


def generate_capability_driver_rollup(
    scores_path: str,
    manifest_path: str,
    zone: int,
    output_dir: str,
) -> Path:
    """Compute and write capability-driver-rollup.json."""
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    scores = load_json(Path(scores_path))
    manifest = load_json(Path(manifest_path))

    rollup = compute_driver_rollup(scores, manifest, zone)

    output_path = out_dir / "capability-driver-rollup.json"
    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump(rollup, fh, indent=2, ensure_ascii=False)
    log.info("Wrote %s", output_path)
    return output_path


# ---------------------------------------------------------------------------
# Entry points
# ---------------------------------------------------------------------------


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="FSI-AgentGov Assessment Report Generator",
    )
    parser.add_argument(
        "--type",
        default="controls",
        choices=["controls", "frontier", "both"],
        help="Report type: controls (default), frontier, or both",
    )
    parser.add_argument(
        "--scores",
        default=None,
        help="Path to scores.json; required for --type controls|both",
    )
    parser.add_argument(
        "--manifest",
        default=None,
        help="Path to controls.json manifest; required for --type controls|both",
    )
    parser.add_argument(
        "--frontier-summary",
        default=None,
        dest="frontier_summary",
        help="Path to frontier-summary.json; required for --type frontier|both",
    )
    parser.add_argument(
        "--frontier-manifest",
        default=None,
        dest="frontier_manifest",
        help="Path to frontier-readiness.json; required for --type frontier|both",
    )
    parser.add_argument(
        "--customer",
        required=True,
        help="Customer name for the report header",
    )
    parser.add_argument(
        "--zone",
        default=None,
        type=int,
        choices=[1, 2, 3],
        help="Governance zone assessed (1, 2, or 3); required for --type controls|both",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory to write output files",
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

    report_type = args.type

    # Validate required args per report type
    missing: list[str] = []
    if report_type in ("controls", "both"):
        for arg_name, val in [
            ("--scores", args.scores),
            ("--manifest", args.manifest),
            ("--zone", args.zone),
        ]:
            if val is None:
                missing.append(f"{arg_name} (required for --type {report_type})")
    if report_type in ("frontier", "both"):
        for arg_name, val in [
            ("--frontier-summary", args.frontier_summary),
            ("--frontier-manifest", args.frontier_manifest),
        ]:
            if val is None:
                missing.append(f"{arg_name} (required for --type {report_type})")
    if missing:
        for m in missing:
            log.error("Missing required argument: %s", m)
        sys.exit(1)

    try:
        generated: list[str] = []
        controls_summary: dict = {}

        if report_type in ("controls", "both"):
            controls_summary = run(
                args.scores,
                args.manifest,
                args.customer,
                args.zone,
                args.output_dir,
            )
            generated.extend(controls_summary.get("files_generated", []))

        controls_manifest: dict | None = None
        if report_type == "both":
            controls_manifest = load_json(Path(args.manifest))

        if report_type in ("frontier", "both"):
            fp = generate_frontier_report(
                args.frontier_summary,
                args.frontier_manifest,
                args.customer,
                args.output_dir,
                zone=args.zone,
                controls_manifest=controls_manifest,
            )
            generated.append(str(fp))

        if report_type == "both":
            rp = generate_capability_driver_rollup(
                args.scores,
                args.manifest,
                args.zone,
                args.output_dir,
            )
            generated.append(str(rp))

            # files_generated atomicity: run() wrote assessment-summary.json
            # before frontier + rollup paths existed, so its files_generated
            # listed only 3/5 outputs. Rewrite it now with the complete list
            # so customer-facing summary accurately reflects all artifacts.
            summary_path = Path(args.output_dir) / "assessment-summary.json"
            if summary_path.exists():
                with open(summary_path, encoding="utf-8") as fh:
                    summary_doc = json.load(fh)
                summary_doc["files_generated"] = sorted(generated)
                with open(summary_path, "w", encoding="utf-8") as fh:
                    json.dump(summary_doc, fh, indent=2, ensure_ascii=False)

        print("\nReport generation complete")
        if controls_summary:
            print(f"  Customer:    {controls_summary.get('customer_name', '?')}")
            print(f"  Zone:        {controls_summary.get('zone_assessed', '?')}")
            print(f"  Gaps:        {len(controls_summary.get('gaps', []))}")
            print(f"  Critical:    {len(controls_summary.get('critical_gaps', []))}")
        print(f"  Files:       {len(generated)}")
        for fp_str in generated:
            print(f"    → {fp_str}")
    except Exception as exc:
        log.error("Report generation failed: %s", exc, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
