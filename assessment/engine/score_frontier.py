#!/usr/bin/env python3
"""FSI-AgentGov Frontier Readiness Scoring Engine.

Evaluates a facilitator-led Frontier Readiness questionnaire against the
``frontier-readiness.json`` manifest to produce per-driver maturity scores
(100-500 scale), a scale-breaker callout, and pattern readiness for the
six transformation patterns.

Frontier Readiness is a self-diagnostic strategy lens. It is deliberately
independent of governance zone (Zone 1/2/3) and supplements — but does not
replace — the 78-control technical assessment.

Usage::

    python score_frontier.py --manifest <frontier-readiness.json> \
                             --collected <dir-containing-frontier.json> \
                             --output <frontier-summary.json>
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ENGINE_VERSION = "1.0.0"

log = logging.getLogger("fsi-agentgov-score-frontier")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DRIVER_IDS: tuple[str, ...] = (
    "ai_strategy",
    "business_strategy",
    "ai_governance",
    "technology_data",
    "organization_culture",
)

LEVELS: tuple[int, ...] = (100, 200, 300, 400, 500)

LEVEL_LABELS: dict[int, str] = {
    100: "Initial",
    200: "Repeatable",
    300: "Defined",
    400: "Capable",
    500: "Optimized",
}

PATTERN_IDS: tuple[int, ...] = (1, 2, 3, 4, 5, 6)

LEVEL_PASS_THRESHOLD: float = 0.7

# Answer-value mapping for ``yes_no_partial`` questions.
YES_NO_PARTIAL_VALUES: dict[str, float] = {
    "yes": 1.0,
    "partial": 0.5,
    "no": 0.0,
}

# Filename produced by Collect-Frontier.ps1.
FRONTIER_COLLECTED_FILENAME = "frontier.json"

SCALE_BREAKER_RATIONALE = (
    "Lowest driver score in profile — limits scale across all patterns "
    "regardless of strength elsewhere."
)


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------


def load_json(path: Path) -> dict:
    """Load and parse a JSON file."""
    # Use utf-8-sig to defensively tolerate BOM written by Windows PowerShell 5.x
    # collectors. Newer collectors emit BOM-less UTF-8 but legacy installs may
    # still produce BOM-prefixed JSON. F-RUN-ASSESSMENT-ORCH-BOM-01.
    with open(path, "r", encoding="utf-8-sig") as fh:
        return json.load(fh)


def load_manifest(path: str | Path) -> dict:
    """Load the frontier-readiness manifest from disk."""
    p = Path(path)
    log.info("Loading frontier manifest from %s", p)
    return load_json(p)


def load_answers(collected_dir: str | Path) -> dict:
    """Read ``frontier.json`` from the collected directory.

    Returns the parsed object. If the file does not exist, returns an
    empty answers envelope so scoring degrades gracefully (every question
    becomes "unanswered").
    """
    p = Path(collected_dir) / FRONTIER_COLLECTED_FILENAME
    if not p.is_file():
        log.warning("Frontier answers not found at %s — scoring with 0 answers", p)
        return {"_metadata": {}, "answers": {}}
    log.info("Loading frontier answers from %s", p)
    return load_json(p)


# ---------------------------------------------------------------------------
# Answer normalization
# ---------------------------------------------------------------------------


def _normalize_answer(question: dict, answer_obj: dict | None) -> float | None:
    """Return a 0.0-1.0 numeric score for an answer, or ``None`` if unscorable.

    Unscorable cases (excluded from numerator AND denominator):
      - missing answer object
      - missing or null ``value`` field
      - ``text`` answer format (not auto-scorable)
      - unrecognised value for the answer format
    """
    if answer_obj is None:
        return None

    raw = answer_obj.get("value")
    if raw is None:
        return None

    fmt = question.get("answer_format", "yes_no_partial")

    if fmt == "yes_no_partial":
        if isinstance(raw, str):
            return YES_NO_PARTIAL_VALUES.get(raw.strip().lower())
        return None

    if fmt == "scale_1_5":
        try:
            n = float(raw)
        except (TypeError, ValueError):
            return None
        if n < 1 or n > 5:
            return None
        # Normalize so 1 -> 0.0 and 5 -> 1.0.
        return (n - 1.0) / 4.0

    if fmt == "text":
        # Free-text answers are captured as evidence but not auto-scored.
        return None

    log.debug("Unknown answer_format %r on question %s", fmt, question.get("question_id"))
    return None


# ---------------------------------------------------------------------------
# Driver scoring
# ---------------------------------------------------------------------------


def _level_label_for(highest_fully_achieved: int, next_level_ratio: float) -> str:
    """Resolve the human-friendly level label for a driver."""
    if highest_fully_achieved == 0:
        return "Below Initial"
    base = LEVEL_LABELS[highest_fully_achieved]
    if highest_fully_achieved >= 500:
        return base
    if next_level_ratio > 0:
        return f"{base}+"
    return base


def _confidence_for(answered: int, total: int) -> str:
    """Confidence band for a driver based on questions answered.

    Spec: high if all 5 answered; medium if 3-4; low if 0-2.
    Generalises gracefully if a driver has != 5 questions.
    """
    if total > 0 and answered >= total:
        return "high"
    if answered >= 3:
        return "medium"
    return "low"


def score_driver(
    driver_id: str,
    manifest_questions: list[dict],
    answers: dict[str, dict],
    collected_dir: Path | None = None,
) -> dict:
    """Score a single driver across its level-stratified questions.

    Returns a dict with ``score``, ``level_label``, ``questions_answered``,
    ``questions_total``, ``confidence``, and ``level_breakdown`` (per-level
    answered / total / ratio).

    When *collected_dir* is provided, evaluator-derived answers are used as
    fallback for questions where no facilitator answer is present.
    """
    driver_questions = [q for q in manifest_questions if q.get("driver") == driver_id]
    questions_total = len(driver_questions)

    # Compute per-level pass ratios.
    level_breakdown: dict[str, dict] = {}
    questions_answered = 0
    for level in LEVELS:
        level_qs = [q for q in driver_questions if q.get("level") == level]
        weighted_sum = 0.0
        weight_sum = 0.0
        answered_at_level = 0
        for q in level_qs:
            qid = q.get("question_id")
            # Facilitator answer wins.
            answer_obj = answers.get(qid)
            # Evaluator fallback when no facilitator answer.
            if (answer_obj is None or answer_obj.get("value") is None) and collected_dir is not None:
                eval_value, eval_evidence = _lookup_evaluator_answer(q, collected_dir)
                if eval_value is not None:
                    answer_obj = {"value": eval_value, "evidence": eval_evidence, "source": "evaluator"}
            normalized = _normalize_answer(q, answer_obj)
            if normalized is None:
                continue
            weight = float(q.get("scoring_weight", 1.0))
            weighted_sum += normalized * weight
            weight_sum += weight
            answered_at_level += 1
        ratio = (weighted_sum / weight_sum) if weight_sum > 0 else 0.0
        level_breakdown[str(level)] = {
            "answered": answered_at_level,
            "total": len(level_qs),
            "ratio": round(ratio, 3),
        }
        questions_answered += answered_at_level

    # Climb the ladder.
    highest_fully_achieved = 0
    next_level_ratio = 0.0
    for level in LEVELS:
        ratio = level_breakdown[str(level)]["ratio"]
        if ratio >= LEVEL_PASS_THRESHOLD:
            highest_fully_achieved = level
            next_level_ratio = 0.0
            continue
        # First level we did not fully achieve — record its ratio and stop.
        next_level_ratio = ratio
        break

    if highest_fully_achieved == 0:
        # L100 not fully achieved: score is L100 ratio * 100 (0-69 range).
        score = int(round(level_breakdown["100"]["ratio"] * 100))
    elif highest_fully_achieved >= 500:
        score = 500
    else:
        score = int(round(highest_fully_achieved + next_level_ratio * 100))

    score = max(0, min(500, score))

    return {
        "score": score,
        "level_label": _level_label_for(highest_fully_achieved, next_level_ratio),
        "questions_answered": questions_answered,
        "questions_total": questions_total,
        "confidence": _confidence_for(questions_answered, questions_total),
        "level_breakdown": level_breakdown,
    }


# ---------------------------------------------------------------------------
# Scale-breaker
# ---------------------------------------------------------------------------


def detect_scale_breaker(driver_scores: dict[str, dict]) -> dict:
    """Identify the lowest-scoring driver (the scale-breaker).

    Returns ``{"driver", "score", "tied_with", "rationale"}``. Ties are
    listed in ``tied_with`` (excluding the primary). Driver order from
    ``DRIVER_IDS`` is used to pick a deterministic primary on ties.
    """
    if not driver_scores:
        return {
            "driver": None,
            "score": None,
            "tied_with": [],
            "rationale": SCALE_BREAKER_RATIONALE,
        }

    min_score = min(d["score"] for d in driver_scores.values())
    # Preserve canonical driver order on ties.
    tied = [d for d in DRIVER_IDS if d in driver_scores and driver_scores[d]["score"] == min_score]
    primary = tied[0]
    return {
        "driver": primary,
        "score": min_score,
        "tied_with": tied[1:],
        "rationale": SCALE_BREAKER_RATIONALE,
    }


# ---------------------------------------------------------------------------
# Pattern readiness
# ---------------------------------------------------------------------------


def assess_pattern_readiness(
    driver_scores: dict[str, dict],
    pattern_target_profiles: dict,
) -> dict[str, dict]:
    """Compute per-pattern readiness against target driver profiles.

    For each pattern, ``gap_drivers`` lists drivers whose current score is
    below target. ``ready`` is True only when there are no gaps. ``min_gap``
    is the smallest positive gap (i.e., how close to ready), or 0 when
    already ready.
    """
    out: dict[str, dict] = {}
    for pattern_id in PATTERN_IDS:
        key = str(pattern_id)
        targets = pattern_target_profiles.get(key, {})
        gap_drivers: list[dict] = []
        for driver_id in DRIVER_IDS:
            target = targets.get(driver_id)
            if target is None:
                continue
            current = driver_scores.get(driver_id, {}).get("score", 0)
            if current < target:
                gap_drivers.append(
                    {
                        "driver": driver_id,
                        "current": current,
                        "target": target,
                        "gap": target - current,
                    }
                )
        ready = len(gap_drivers) == 0
        min_gap = 0 if ready else min(g["gap"] for g in gap_drivers)
        out[key] = {
            "ready": ready,
            "gap_drivers": gap_drivers,
            "min_gap": min_gap,
        }
    return out


# ---------------------------------------------------------------------------
# Pass-condition evaluators
# ---------------------------------------------------------------------------
# Signature: (collected_dir: Path) -> (answer_value: str | None, evidence: str)
# answer_value ∈ {"yes", "no", "partial", None}. None = inconclusive.
# Frontier evaluators take a Path (not a dict) because they run before
# the collected-data dict assembly that score.py performs.


def _load_collected_json(
    collected_dir: Path, filename: str
) -> tuple[dict | None, str | None]:
    """Load a collector JSON file from the collected directory.

    Returns ``(data, None)`` on success, or ``(None, error_reason)`` on failure.
    """
    path = collected_dir / filename
    if not path.is_file():
        return None, f"{filename} not found"
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh), None
    except (json.JSONDecodeError, OSError) as exc:
        return None, f"failed to read {filename} ({exc})"


def _eval_any_environment_visibility_for_agents(
    collected_dir: Path,
) -> tuple[str | None, str]:
    """Q16 evaluator: check ppac.json for environment visibility."""
    ppac, err = _load_collected_json(collected_dir, "ppac.json")
    if ppac is None:
        return None, f"PPAC data unavailable: {err}"

    # Check for collector errors.
    metadata = ppac.get("_metadata") or {}
    errors = metadata.get("errors") or []
    if errors:
        first_error = errors[0] if isinstance(errors[0], str) else str(errors[0])
        return None, f"PPAC data unavailable: collector reported errors ({first_error})"

    environments = ppac.get("environments")
    if environments is None:
        return None, "PPAC data unavailable: environments field absent"

    if not isinstance(environments, list):
        return None, "PPAC data unavailable: environments field is not a list"

    if len(environments) == 0:
        return "no", "PPAC reported zero environments"

    names = [
        env.get("DisplayName") or env.get("EnvironmentName") or "unnamed"
        for env in environments[:3]
    ]
    suffix = f" (and {len(environments) - 3} more)" if len(environments) > 3 else ""
    return (
        "yes",
        f"PPAC reported {len(environments)} environment(s): {', '.join(names)}{suffix}",
    )


def _eval_tagged_environments_with_basic_telemetry(
    collected_dir: Path,
) -> tuple[str | None, str]:
    """Q17 evaluator: check env tags/groups in ppac.json + Sentinel workspace.

    Returns:
      - ("yes", evidence) — at least one env has tags or group membership AND
        Sentinel workspace present.
      - ("partial", evidence) — only one signal present (tags/groups OR Sentinel).
      - ("no", evidence) — neither signal present.
      - (None, evidence) — ppac.json missing or collector errored.
    """
    ppac, ppac_err = _load_collected_json(collected_dir, "ppac.json")
    if ppac is None:
        return None, f"PPAC data unavailable: {ppac_err}"

    # Check for collector errors on environments.
    metadata = ppac.get("_metadata") or {}
    errors = metadata.get("errors") or []
    if errors:
        first_error = errors[0] if isinstance(errors[0], str) else str(errors[0])
        return None, f"PPAC data unavailable: collector reported errors ({first_error})"

    environments = ppac.get("environments")
    if environments is None or not isinstance(environments, list):
        return None, "PPAC data unavailable: environments field absent or invalid"

    # Count environments with non-empty tags.
    tagged_count = 0
    for env in environments:
        tags = env.get("Tags")
        if isinstance(tags, dict) and len(tags) > 0:
            tagged_count += 1

    # Count environments with group membership.
    grouped_count = 0
    for env in environments:
        gid = env.get("EnvironmentGroupId")
        if gid is not None and gid != "":
            grouped_count += 1

    # Count environment groups from top-level field.
    env_groups = ppac.get("environmentGroups")
    env_group_count = len(env_groups) if isinstance(env_groups, list) else 0

    has_tags_or_groups = tagged_count > 0 or grouped_count > 0

    # Build PPAC evidence fragment.
    total = len(environments)
    parts: list[str] = []
    parts.append(f"{tagged_count}/{total} environments with tags")
    if grouped_count > 0:
        parts.append(f"{grouped_count} with group membership")
    if env_group_count > 0:
        parts.append(f"{env_group_count} environment group(s)")
    ppac_evidence = "PPAC reported " + "; ".join(parts)

    # Sentinel workspace presence.
    sentinel, _ = _load_collected_json(collected_dir, "sentinel.json")
    has_sentinel = False
    sentinel_name = ""
    if sentinel is not None:
        workspace = sentinel.get("workspace")
        if isinstance(workspace, dict) and workspace.get("WorkspaceId"):
            has_sentinel = True
            sentinel_name = workspace.get("WorkspaceName") or workspace.get("WorkspaceId") or "unnamed"

    if has_sentinel:
        sentinel_evidence = f"Sentinel workspace '{sentinel_name}' present"
    else:
        sentinel_evidence = "Sentinel workspace not found"

    evidence = f"{ppac_evidence}; {sentinel_evidence}"

    if has_tags_or_groups and has_sentinel:
        return "yes", evidence
    if has_tags_or_groups or has_sentinel:
        return "partial", evidence
    return "no", evidence


# ---------------------------------------------------------------------------
# Q13 evaluator — zone classification + audit log + model risk (partial-only)
# ---------------------------------------------------------------------------

# Zone tag matching patterns (case-insensitive).
ZONE_TAG_KEY_PATTERN: re.Pattern = re.compile(r"^zone$", re.IGNORECASE)
ZONE_TAG_VALUE_PATTERN: re.Pattern = re.compile(r"^[1-3]$")
ZONE_SUBSTRING_PATTERN: re.Pattern = re.compile(r"zone", re.IGNORECASE)


def _q13_zone_count(ppac: dict) -> int:
    """Count environments meeting zone-classification criteria.

    An environment is zone-classified if:
      - Its ``Tags`` dict contains a key matching ``^zone$`` (case-insensitive)
        with a value matching ``^[1-3]$``, OR any key/value containing "zone"
        as a case-insensitive substring.
      - OR its ``EnvironmentGroupId`` resolves to a group whose
        ``DisplayName`` contains "zone" (case-insensitive).
    """
    environments = ppac.get("environments")
    if not isinstance(environments, list):
        return 0

    # Build group-id → DisplayName lookup for env-group zone matching.
    env_groups = ppac.get("environmentGroups")
    group_names: dict[str, str] = {}
    if isinstance(env_groups, list):
        for grp in env_groups:
            gid = grp.get("Id") or ""
            name = grp.get("DisplayName") or ""
            if gid:
                group_names[gid] = name

    count = 0
    for env in environments:
        # Check Tags dict.
        tags = env.get("Tags")
        if isinstance(tags, dict):
            for key, value in tags.items():
                key_str = str(key)
                val_str = str(value)
                if ZONE_TAG_KEY_PATTERN.match(key_str) and ZONE_TAG_VALUE_PATTERN.match(val_str):
                    count += 1
                    break
                if ZONE_SUBSTRING_PATTERN.search(key_str) or ZONE_SUBSTRING_PATTERN.search(val_str):
                    count += 1
                    break
            else:
                # Tags didn't match — fall through to group check.
                gid = env.get("EnvironmentGroupId")
                if gid and gid in group_names and ZONE_SUBSTRING_PATTERN.search(group_names[gid]):
                    count += 1
        else:
            # No tags — check group membership.
            gid = env.get("EnvironmentGroupId")
            if gid and gid in group_names and ZONE_SUBSTRING_PATTERN.search(group_names[gid]):
                count += 1

    return count


def _q13_audit_enabled(purview: dict) -> bool | None:
    """Check whether unified audit log ingestion is enabled.

    Mirrors the controls-side ``_eval_audit_log_enabled`` read pattern.
    Returns ``True`` if enabled, ``False`` if explicitly disabled, or
    ``None`` if the relevant field is absent.
    """
    config = purview.get("audit_config")
    if config is None:
        return None
    enabled = config.get("UnifiedAuditLogIngestionEnabled")
    if enabled is True:
        return True
    if enabled is False:
        return False
    return None


def _eval_zone_classification_with_audit_supervision_and_model_risk(
    collected_dir: Path,
) -> tuple[str | None, str]:
    """Q13 evaluator: zone classification + audit log + model risk overlay.

    Checks two of three L300 signals from telemetry:
      1. Zone-classified Managed Environments (PPAC env tags/groups)
      2. Comprehensive audit signals (Purview UnifiedAuditLogIngestionEnabled)

    The third signal — model-risk overlay — is structurally non-telemetry-
    verifiable (typically a SharePoint document policy or model-card registry).

    **Auto-cap rule:** This evaluator NEVER returns ``"yes"``. The maximum
    auto-confirmable answer is ``"partial"`` because the third signal (model
    risk) cannot be verified from any of the 5 existing collectors. The
    facilitator can upgrade to ``"yes"`` via their own answer (which always
    wins per framework design).

    Returns:
      - ``("partial", evidence)`` — both zone tags and audit log verified;
        evidence notes that model-risk overlay requires facilitator confirmation.
      - ``("partial", evidence)`` — only one of {zone, audit} present; evidence
        describes which is missing.
      - ``("no", evidence)`` — neither zone tags nor audit log enabled.
      - ``(None, evidence)`` — both ppac.json and purview.json missing or errored.
    """
    model_risk_caveat = "model-risk overlay requires facilitator confirmation"

    # --- Load PPAC data ---
    ppac, ppac_err = _load_collected_json(collected_dir, "ppac.json")
    ppac_available = False
    zone_count = 0
    zone_evidence = ""

    if ppac is not None:
        metadata = ppac.get("_metadata") or {}
        errors = metadata.get("errors") or []
        if errors:
            first_error = errors[0] if isinstance(errors[0], str) else str(errors[0])
            ppac_err = f"collector reported errors ({first_error})"
        else:
            ppac_available = True
            zone_count = _q13_zone_count(ppac)

    if ppac_available:
        # Build a brief summary of matched zone tags for evidence.
        tag_samples: list[str] = []
        environments = ppac.get("environments") or []
        for env in environments:
            tags = env.get("Tags")
            if isinstance(tags, dict):
                for key, value in tags.items():
                    key_str = str(key)
                    val_str = str(value)
                    if ZONE_TAG_KEY_PATTERN.match(key_str) and ZONE_TAG_VALUE_PATTERN.match(val_str):
                        tag_samples.append(f"'{key_str}:{val_str}'")
                        break
                    if ZONE_SUBSTRING_PATTERN.search(key_str) or ZONE_SUBSTRING_PATTERN.search(val_str):
                        tag_samples.append(f"'{key_str}:{val_str}'")
                        break
        if tag_samples:
            zone_evidence = (
                f"PPAC reported {zone_count} zone-classified environment(s) "
                f"(tags: {', '.join(tag_samples[:5])})"
            )
        else:
            zone_evidence = f"PPAC reported {zone_count} zone-classified environment(s)"
    else:
        zone_evidence = f"PPAC data unavailable: {ppac_err}"

    # --- Load Purview data ---
    purview, purview_err = _load_collected_json(collected_dir, "purview.json")
    purview_available = False
    audit_enabled: bool | None = None
    audit_evidence = ""

    if purview is not None:
        metadata = purview.get("_metadata") or {}
        errors = metadata.get("errors") or []
        if errors:
            first_error = errors[0] if isinstance(errors[0], str) else str(errors[0])
            purview_err = f"collector reported errors ({first_error})"
        else:
            purview_available = True
            audit_enabled = _q13_audit_enabled(purview)

    if purview_available and audit_enabled is not None:
        audit_evidence = (
            f"audit log {'enabled' if audit_enabled else 'NOT enabled'} "
            f"(UnifiedAuditLogIngestionEnabled={str(audit_enabled).lower()})"
        )
    elif purview_available:
        audit_evidence = "audit_config field absent in Purview data"
    else:
        audit_evidence = f"Purview data unavailable: {purview_err}"

    # --- Both sources unavailable → inconclusive ---
    if not ppac_available and not purview_available:
        return None, f"PPAC and Purview data both unavailable: {ppac_err}; {purview_err}"

    # --- Determine result ---
    has_zones = zone_count > 0
    has_audit = audit_enabled is True

    evidence = f"{zone_evidence}; {audit_evidence}; {model_risk_caveat}"

    if has_zones and has_audit:
        return "partial", evidence
    if has_zones or has_audit:
        return "partial", evidence
    return "no", evidence


# ---------------------------------------------------------------------------
# Q01 evaluator — AI initiative owner identified
# ---------------------------------------------------------------------------

# Canonical AI-leadership job title keywords (case-insensitive substring match).
# Short tokens ("AI", "CDO", "CIO", "CTO") require word-boundary matching to
# avoid false positives (e.g. "MAID", "ACIDOTIC").
AI_LEADERSHIP_TITLES: tuple[str, ...] = (
    "chief data officer",
    "chief information officer",
    "chief ai officer",
    "chief digital officer",
    "chief analytics officer",
    "chief data and analytics officer",
    "chief technology officer",
    "head of ai",
    "head of data",
    "head of digital",
    "ai governance lead",
    "ai officer",
    "director of ai",
    "vp of ai",
    "vp of data",
    "vp of digital",
)

# Short acronyms that require word-boundary matching.
_AI_LEADERSHIP_ACRONYMS: tuple[str, ...] = ("cdo", "cio", "cto")

_ACRONYM_PATTERN = re.compile(
    r"\b(?:" + "|".join(re.escape(a) for a in _AI_LEADERSHIP_ACRONYMS) + r")\b",
    re.IGNORECASE,
)


def _match_ai_leadership_title(job_title: str) -> str | None:
    """Return the matched keyword phrase if *job_title* matches, else ``None``."""
    lower = job_title.lower()
    for phrase in AI_LEADERSHIP_TITLES:
        if phrase in lower:
            return phrase.title()
    if _ACRONYM_PATTERN.search(lower):
        return _ACRONYM_PATTERN.search(lower).group(0).upper()  # type: ignore[union-attr]
    return None


def _eval_ai_initiative_owner_identified(
    collected_dir: Path,
) -> tuple[str | None, str]:
    """Q01 evaluator: check graph.json for AI-leadership job titles.

    Returns:
      - ("yes", evidence) — at least one user with an AI-leadership title found.
      - ("partial", evidence) — no AI titles but senior admin roles assigned.
      - ("no", evidence) — neither AI titles nor senior admin assignments.
      - (None, evidence) — graph.json missing or both data sections errored.
    """
    graph, err = _load_collected_json(collected_dir, "graph.json")
    if graph is None:
        return None, f"Graph data unavailable: {err}"

    metadata = graph.get("_metadata") or {}

    # --- Primary signal: AI leadership job titles (Section 7) ---
    ai_users = graph.get("aiLeadershipUsers")
    section7_available = ai_users is not None

    matched_users: list[tuple[str, str]] = []  # (displayName, matchedKeyword)
    if isinstance(ai_users, list):
        for user in ai_users:
            display = user.get("DisplayName") or user.get("displayName") or "Unknown"
            keyword = user.get("MatchedKeyword") or user.get("matchedKeyword") or ""
            if keyword:
                matched_users.append((display, keyword))
            else:
                # Re-check title in case MatchedKeyword is absent
                title = user.get("JobTitle") or user.get("jobTitle") or ""
                kw = _match_ai_leadership_title(title)
                if kw:
                    matched_users.append((display, kw))

    if matched_users:
        if len(matched_users) > 5:
            shown = matched_users[:3]
            remainder = len(matched_users) - 3
            listing = ", ".join(f"'{n} ({k})'" for n, k in shown)
            listing += f" and {remainder} more"
        else:
            listing = ", ".join(f"'{n} ({k})'" for n, k in matched_users)
        return (
            "yes",
            f"Found {len(matched_users)} user(s) with AI-leadership titles: {listing}",
        )

    # --- Secondary signal: privileged role assignments (Section 4) ---
    priv_roles = graph.get("privilegedRoleAssignments")
    section4_available = priv_roles is not None

    if not section7_available and not section4_available:
        # Both sections failed or missing — check for errors in metadata.
        errors = metadata.get("errors") or metadata.get("warnings") or []
        if errors:
            first = errors[0] if isinstance(errors[0], str) else str(errors[0])
            return None, f"Graph data unavailable: collector reported errors ({first})"
        return None, "Graph data unavailable: neither aiLeadershipUsers nor privilegedRoleAssignments present"

    if isinstance(priv_roles, list) and len(priv_roles) > 0:
        return (
            "partial",
            f"No AI-specific titles found; {len(priv_roles)} senior platform admin "
            f"assignment(s) present (informal accountability)",
        )

    return "no", "No AI-leadership titles or senior admin assignments found in tenant"


# ---------------------------------------------------------------------------
# Q18 evaluator — Environment Groups with inventory, SIEM, RAG, and lineage
# ---------------------------------------------------------------------------


def _q18_env_groups_present(ppac: dict) -> bool:
    """Check whether tiered environment groups are operational."""
    env_groups = ppac.get("environmentGroups")
    if isinstance(env_groups, list) and len(env_groups) > 0:
        return True
    environments = ppac.get("environments")
    if isinstance(environments, list):
        for env in environments:
            if env.get("EnvironmentGroupId"):
                return True
    return False


def _q18_siem_present(sentinel: dict) -> bool:
    """Check whether SIEM integration (data connectors) is present."""
    dc = sentinel.get("dataConnectors")
    if dc is None:
        return False
    if dc.get("Office365Enabled") is True or dc.get("McasEnabled") is True:
        return True
    total = dc.get("TotalConnectors", 0)
    summary = dc.get("ConnectorSummary") or []
    return total > 0 and len(summary) > 0


def _q18_sp_scan_present(sharepoint: dict) -> bool:
    """Check whether item-level permission scanning ran at deployment."""
    ilp = sharepoint.get("itemLevelPermissions")
    if not isinstance(ilp, list) or len(ilp) == 0:
        return False
    for site in ilp:
        if site.get("SampledItems", 0) > 0:
            return True
    return False


def _eval_env_groups_with_inventory_siem_rag_and_lineage(
    collected_dir: Path,
) -> tuple[str | None, str]:
    """Q18 evaluator: tiered env groups + SIEM + item-level scan + agent inventory + RAG/lineage.

    Checks three of five L300 Tech & Data signals from telemetry:
      1. Tiered Environment Groups operational (PPAC env groups)
      2. SIEM integration (Sentinel data connectors)
      3. Item-level permission scanning (SharePoint scan)

    The remaining signals are structurally non-telemetry-verifiable:
      - Agent inventory is not collected by any existing collector
      - RAG-integrity validation + data lineage documentation are facilitator-only

    **Auto-cap rule:** This evaluator NEVER returns ``"yes"``. The maximum
    auto-confirmable answer is ``"partial"`` because agent inventory is not
    collected, and RAG-integrity + data lineage are facilitator-only signals.

    Returns:
      - ``("partial", evidence)`` — 1-3 of 3 telemetry signals present.
      - ``("no", evidence)`` — 0 of 3 telemetry signals present.
      - ``(None, evidence)`` — all three collector files missing or errored.
    """
    agent_inventory_caveat = "agent inventory not collected (out of scope)"
    rag_lineage_caveat = "RAG-integrity + data lineage require facilitator confirmation"

    # --- Load PPAC data ---
    ppac, ppac_err = _load_collected_json(collected_dir, "ppac.json")
    ppac_available = False
    env_groups_signal = False
    env_groups_evidence = ""

    if ppac is not None:
        metadata = ppac.get("_metadata") or {}
        errors = metadata.get("errors") or []
        if errors:
            first_error = errors[0] if isinstance(errors[0], str) else str(errors[0])
            ppac_err = f"collector reported errors ({first_error})"
        else:
            ppac_available = True
            env_groups_signal = _q18_env_groups_present(ppac)

    if ppac_available:
        if env_groups_signal:
            env_groups_list = ppac.get("environmentGroups") or []
            tiered_count = sum(
                1 for g in env_groups_list
                if any(kw in (g.get("DisplayName") or "").lower() for kw in ["tier", "zone", "prod"])
            )
            env_groups_evidence = (
                f"PPAC env groups present ({len(env_groups_list)} total"
                f"{f', {tiered_count} tiered' if tiered_count > 0 else ''})"
            )
        else:
            env_groups_evidence = "PPAC env groups absent"
    else:
        env_groups_evidence = f"PPAC data unavailable: {ppac_err}"

    # --- Load Sentinel data ---
    sentinel, sentinel_err = _load_collected_json(collected_dir, "sentinel.json")
    sentinel_available = False
    siem_signal = False
    siem_evidence = ""

    if sentinel is not None:
        metadata = sentinel.get("_metadata") or {}
        errors = metadata.get("errors") or []
        if errors:
            first_error = errors[0] if isinstance(errors[0], str) else str(errors[0])
            sentinel_err = f"collector reported errors ({first_error})"
        else:
            sentinel_available = True
            siem_signal = _q18_siem_present(sentinel)

    if sentinel_available:
        if siem_signal:
            dc = sentinel.get("dataConnectors") or {}
            connectors = []
            if dc.get("Office365Enabled"):
                connectors.append("Office365")
            if dc.get("McasEnabled"):
                connectors.append("MCAS")
            connector_desc = ", ".join(connectors) if connectors else f"{dc.get('TotalConnectors', 0)} connectors"
            siem_evidence = f"Sentinel SIEM connector(s) enabled ({connector_desc})"
        else:
            siem_evidence = "no SIEM connectors enabled"
    else:
        siem_evidence = f"Sentinel data unavailable: {sentinel_err}"

    # --- Load SharePoint data ---
    sharepoint, sharepoint_err = _load_collected_json(collected_dir, "sharepoint.json")
    sharepoint_available = False
    sp_scan_signal = False
    sp_scan_evidence = ""

    if sharepoint is not None:
        metadata = sharepoint.get("_metadata") or {}
        errors = metadata.get("errors") or []
        if errors:
            first_error = errors[0] if isinstance(errors[0], str) else str(errors[0])
            sharepoint_err = f"collector reported errors ({first_error})"
        else:
            sharepoint_available = True
            sp_scan_signal = _q18_sp_scan_present(sharepoint)

    if sharepoint_available:
        if sp_scan_signal:
            ilp = sharepoint.get("itemLevelPermissions") or []
            total_sampled = sum(site.get("SampledItems", 0) for site in ilp)
            sp_scan_evidence = f"SharePoint item-level scan ran ({len(ilp)} sites, {total_sampled} sampled items)"
            crossref = sharepoint.get("groundingCrossRef")
            if isinstance(crossref, dict) and crossref.get("ApprovedFound", 0) > 0:
                sp_scan_evidence += f"; grounding cross-reference confirmed {crossref['ApprovedFound']} approved site(s)"
        else:
            sp_scan_evidence = "SharePoint item-level scan absent"
    else:
        sp_scan_evidence = f"SharePoint data unavailable: {sharepoint_err}"

    # --- All sources unavailable → inconclusive ---
    if not ppac_available and not sentinel_available and not sharepoint_available:
        return None, (
            f"All three data sources unavailable: {ppac_err}; {sentinel_err}; {sharepoint_err}"
        )

    # --- Count telemetry signals present ---
    signal_count = sum([env_groups_signal, siem_signal, sp_scan_signal])

    evidence = (
        f"{env_groups_evidence}; {siem_evidence}; {sp_scan_evidence}; "
        f"{agent_inventory_caveat}; {rag_lineage_caveat}"
    )

    if signal_count == 0:
        return "no", evidence
    return "partial", evidence


# ---------------------------------------------------------------------------
# Q03 evaluator — Enterprise AI strategy published with portfolio
# ---------------------------------------------------------------------------

AI_STRATEGY_KEYWORDS = (
    "ai strategy",
    "ai governance",
    "ai council",
    "ai portfolio",
    "agent portfolio",
    "frontier",
    "executive sponsor",
    "governance committee",
)


def _eval_enterprise_ai_strategy_published_with_portfolio(
    collected_dir: Path,
) -> tuple[str | None, str]:
    """Q03 evaluator: enterprise AI strategy published with portfolio-level inventory.

    Checks SharePoint site inventory for strategic AI/portfolio naming patterns.
    This is a weak heuristic but acceptable because the evaluator is capped at
    ``"partial"`` — the presence of matching site names suggests strategy
    publication, but "reviewed by Governance Committee", "with portfolio",
    and "active governance" are facilitator-only judgements.

    **Auto-cap rule:** This evaluator NEVER returns ``"yes"``. The maximum
    auto-confirmable answer is ``"partial"`` because site naming is telemetry-
    verifiable but governance review + portfolio scope are facilitator-only.

    Returns:
      - ``("partial", evidence)`` — 1+ SharePoint site name matches keywords.
      - ``("no", evidence)`` — SharePoint collected but no matching sites.
      - ``(None, evidence)`` — sharepoint.json missing or errored.
    """
    portfolio_governance_caveat = "portfolio scope and active governance require facilitator confirmation"

    sharepoint, err = _load_collected_json(collected_dir, "sharepoint.json")
    if sharepoint is None:
        return None, f"SharePoint data unavailable: {err}"

    metadata = sharepoint.get("_metadata") or {}
    errors = metadata.get("errors") or []
    if errors:
        first_error = errors[0] if isinstance(errors[0], str) else str(errors[0])
        return None, f"SharePoint data unavailable: collector reported errors ({first_error})"

    site_inventory = sharepoint.get("siteInventory")
    if not isinstance(site_inventory, list):
        return None, "SharePoint data unavailable: siteInventory field absent or invalid"

    if len(site_inventory) == 0:
        return "no", "SharePoint collected zero sites"

    # Case-insensitive substring matching against AI strategy keywords
    matched_sites: list[tuple[str, str]] = []  # (DisplayName, matched_keyword)
    for site in site_inventory:
        display = site.get("DisplayName") or ""
        lower_display = display.lower()
        for keyword in AI_STRATEGY_KEYWORDS:
            if keyword in lower_display:
                matched_sites.append((display, keyword))
                break

    if matched_sites:
        if len(matched_sites) > 3:
            shown = matched_sites[:3]
            remainder = len(matched_sites) - 3
            listing = ", ".join(f"'{n}' (matched '{k}')" for n, k in shown)
            listing += f" and {remainder} more"
        else:
            listing = ", ".join(f"'{n}' (matched '{k}')" for n, k in matched_sites)
        return (
            "partial",
            f"SharePoint site(s) suggest strategy publication: {listing}; {portfolio_governance_caveat}",
        )

    return "no", "No SharePoint site name matched AI strategy/portfolio keywords"


# --- Evaluator registry ---------------------------------------------------

EVALUATORS: dict[str, object] = {
    "any_environment_visibility_for_agents": _eval_any_environment_visibility_for_agents,
    "tagged_environments_with_basic_telemetry": _eval_tagged_environments_with_basic_telemetry,
    "zone_classification_with_audit_supervision_and_model_risk": _eval_zone_classification_with_audit_supervision_and_model_risk,
    "ai_initiative_owner_identified": _eval_ai_initiative_owner_identified,
    "env_groups_with_inventory_siem_rag_and_lineage": _eval_env_groups_with_inventory_siem_rag_and_lineage,
    "enterprise_ai_strategy_published_with_portfolio": _eval_enterprise_ai_strategy_published_with_portfolio,
}


def _lookup_evaluator_answer(
    question: dict, collected_dir: Path
) -> tuple[str | None, str | None]:
    """Look up an evaluator result for a frontier question.

    Returns ``(answer_value, evidence)`` if an evaluator is registered and
    produces a non-None result. Returns ``(None, None)`` when no evaluator
    applies or the evaluator is inconclusive.
    """
    if question.get("auto_evaluable") is not True:
        return None, None
    condition = question.get("pass_condition") or ""
    evaluator = EVALUATORS.get(condition)
    if evaluator is None:
        return None, None
    answer_value, evidence = evaluator(collected_dir)  # type: ignore[operator]
    return answer_value, evidence


# ---------------------------------------------------------------------------
# Evaluator coverage
# ---------------------------------------------------------------------------


def compute_evaluator_coverage(manifest_questions: list[dict]) -> dict:
    """Aggregate evaluator-state coverage for the question set.

    A frontier question's state is one of:
      - ``auto_evaluable``: ``auto_evaluable == True`` AND ``pass_condition``
        has a registered evaluator in EVALUATORS
      - ``unimplemented_evaluator``: ``auto_evaluable == True`` but no
        registered evaluator (safety net), OR non-Manual collection method
        declared without auto_evaluable
      - ``manual_only``: ``auto_evaluable == False`` and
        ``collection_methods == ["Manual"]``
    """
    counts = {"auto_evaluable": 0, "manual_only": 0, "unimplemented_evaluator": 0}
    for q in manifest_questions:
        auto = q.get("auto_evaluable") is True
        condition = q.get("pass_condition") or ""
        has_evaluator = condition in EVALUATORS
        methods = q.get("collection_methods") or []

        if auto and has_evaluator:
            counts["auto_evaluable"] += 1
        elif auto and not has_evaluator:
            counts["unimplemented_evaluator"] += 1
        elif not auto and list(methods) == ["Manual"]:
            counts["manual_only"] += 1
        else:
            counts["unimplemented_evaluator"] += 1
    return {
        "questions": counts,
        "total_questions": len(manifest_questions),
    }


# ---------------------------------------------------------------------------
# Driver friendly-name lookup
# ---------------------------------------------------------------------------


def _driver_name_lookup(manifest: dict) -> dict[str, str]:
    """Map driver_id -> display name, falling back to title-cased id."""
    out: dict[str, str] = {}
    for d in manifest.get("drivers", []):
        did = d.get("id")
        if did:
            out[did] = d.get("name", did)
    for did in DRIVER_IDS:
        out.setdefault(did, did.replace("_", " ").title())
    return out


# ---------------------------------------------------------------------------
# Entry points
# ---------------------------------------------------------------------------


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="FSI-AgentGov Frontier Readiness Scoring Engine",
    )
    parser.add_argument(
        "--manifest",
        required=True,
        help="Path to frontier-readiness.json manifest",
    )
    parser.add_argument(
        "--collected",
        required=True,
        help="Path to directory containing frontier.json answers",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to write frontier-summary.json output",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )
    return parser.parse_args(argv)


def run(
    manifest_path: str,
    collected_dir: str,
    output_path: str,
) -> dict:
    """Execute the frontier scoring engine and return the results dict.

    Can be called programmatically (e.g. from tests) or via the CLI.
    Writes ``frontier-summary.json`` to ``output_path``.
    """
    manifest_p = Path(manifest_path)
    collected_p = Path(collected_dir)
    output_p = Path(output_path)

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    manifest = load_manifest(manifest_p)
    questions: list[dict] = manifest.get("questions", [])
    pattern_targets: dict = manifest.get("pattern_target_profiles", {})

    answers_envelope = load_answers(collected_p)
    answers: dict[str, dict] = answers_envelope.get("answers", {}) or {}

    log.info(
        "Scoring %d frontier questions across %d drivers (%d answers provided)",
        len(questions),
        len(DRIVER_IDS),
        len(answers),
    )

    driver_scores: dict[str, dict] = {}
    for driver_id in DRIVER_IDS:
        result = score_driver(driver_id, questions, answers, collected_dir=collected_p)
        driver_scores[driver_id] = result
        log.debug(
            "  %s — score %d (%s), confidence %s",
            driver_id,
            result["score"],
            result["level_label"],
            result["confidence"],
        )

    scale_breaker = detect_scale_breaker(driver_scores)
    pattern_readiness = assess_pattern_readiness(driver_scores, pattern_targets)
    evaluator_coverage = compute_evaluator_coverage(questions)

    # Build per-question evaluator results for transparency.
    evaluator_results: dict[str, dict] = {}
    for q in questions:
        eval_value, eval_evidence = _lookup_evaluator_answer(q, collected_p)
        if eval_value is not None or eval_evidence is not None:
            qid = q["question_id"]
            facilitator_answer = answers.get(qid)
            used = facilitator_answer is None or facilitator_answer.get("value") is None
            evaluator_results[qid] = {
                "answer_value": eval_value,
                "evidence": eval_evidence,
                "used_for_scoring": used,
            }

    output = {
        "_metadata": {
            "engine_version": ENGINE_VERSION,
            "timestamp": timestamp,
            "manifest_version": manifest.get("version", "unknown"),
        },
        "driver_scores": driver_scores,
        "scale_breaker": scale_breaker,
        "pattern_readiness": pattern_readiness,
        "evaluator_coverage": evaluator_coverage,
        "evaluator_results": evaluator_results,
    }

    output_p.parent.mkdir(parents=True, exist_ok=True)
    with open(output_p, "w", encoding="utf-8") as fh:
        json.dump(output, fh, indent=2, ensure_ascii=False)
    log.info("Frontier summary written to %s", output_p)

    return output


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )
    try:
        result = run(args.manifest, args.collected, args.output)
    except Exception as exc:
        log.error("Frontier scoring failed: %s", exc, exc_info=True)
        sys.exit(1)

    # Friendly stdout summary.
    manifest = load_manifest(args.manifest)
    name_lookup = _driver_name_lookup(manifest)
    driver_scores = result["driver_scores"]
    scale_breaker = result["scale_breaker"]
    pattern_readiness = result["pattern_readiness"]

    print("\nFrontier Readiness Assessment Complete")
    print("  Driver scores:")
    for driver_id in DRIVER_IDS:
        d = driver_scores.get(driver_id, {})
        print(
            f"    {name_lookup.get(driver_id, driver_id)}: "
            f"{d.get('score', 0)} ({d.get('level_label', 'n/a')})"
        )

    sb_driver = scale_breaker.get("driver") or "n/a"
    sb_name = name_lookup.get(sb_driver, sb_driver)
    sb_tied = scale_breaker.get("tied_with") or []
    tied_suffix = (
        f" (tied with: {', '.join(name_lookup.get(t, t) for t in sb_tied)})"
        if sb_tied
        else ""
    )
    print(f"  Scale-breaker: {sb_name} ({scale_breaker.get('score', 'n/a')}){tied_suffix}")

    ready_count = sum(1 for p in pattern_readiness.values() if p.get("ready"))
    total_patterns = len(pattern_readiness)
    print(f"  Pattern readiness: {ready_count}/{total_patterns} patterns ready")
    print(f"  Output: {args.output}")


if __name__ == "__main__":
    main()
