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
    with open(path, "r", encoding="utf-8") as fh:
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
) -> dict:
    """Score a single driver across its level-stratified questions.

    Returns a dict with ``score``, ``level_label``, ``questions_answered``,
    ``questions_total``, ``confidence``, and ``level_breakdown`` (per-level
    answered / total / ratio).
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
            normalized = _normalize_answer(q, answers.get(q.get("question_id")))
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
# Evaluator coverage
# ---------------------------------------------------------------------------


def compute_evaluator_coverage(manifest_questions: list[dict]) -> dict:
    """Aggregate evaluator-state coverage for the question set.

    A frontier question's state is one of:
      - ``auto_evaluable``: ``auto_evaluable == True``
      - ``manual_only``: ``collection_methods == ["Manual"]`` and not auto-evaluable
      - ``unimplemented_evaluator``: anything else (a non-Manual collection
        method is declared but no evaluator wired)
    """
    counts = {"auto_evaluable": 0, "manual_only": 0, "unimplemented_evaluator": 0}
    for q in manifest_questions:
        if q.get("auto_evaluable") is True:
            counts["auto_evaluable"] += 1
            continue
        methods = q.get("collection_methods") or []
        if list(methods) == ["Manual"]:
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
        result = score_driver(driver_id, questions, answers)
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
