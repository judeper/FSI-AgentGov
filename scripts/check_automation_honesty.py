#!/usr/bin/env python3
"""Fail-closed guard against dishonest ``automation`` claims in the manifest.

Every control in ``assessment/manifest/controls.json`` publishes an
``automation`` claim — ``full``, ``partial`` or ``manual``. That claim is a
promise about how much of the control the assessment engine can actually score
from collected telemetry. It drifts from reality whenever a check declares a
``pass_condition`` that has no registered evaluator in the ``EVALUATORS``
registry in ``assessment/engine/score.py``.

This guard catches **overclaims** only. Understating automation is always
allowed, because an understated claim is the fail-closed direction: the
reviewer is asked for manual evidence that the engine could in principle have
gathered, which is safe. The rules are:

* ``full``    — every check must be ``auto_evaluable`` (and there must be at
  least one check). Claiming full automation with an unwired check tells a
  reviewer the engine covered ground it never touched.
* ``partial`` — at least one check must be ``auto_evaluable``. A ``partial``
  claim with zero working evaluators automates nothing.
* ``manual``  — never an overclaim; it is the floor.

Correcting a control means either wiring the missing evaluator or downgrading
the claim (see controls 1.11, 1.13 and 1.15 for the established shape of an
explicit manual gate).

Pre-existing drift is recorded in ``assessment/manifest/automation-honesty-baseline.json``
and the baseline is a **one-way ratchet**: ``--write`` refuses to add control
IDs that are not already listed, so newly introduced overclaims can never be
regenerated away. Fixing a control and rerunning ``--write`` removes it.

Usage::

    python scripts/check_automation_honesty.py            # check (default)
    python scripts/check_automation_honesty.py --check
    python scripts/check_automation_honesty.py --write    # shrink baseline
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST = REPO_ROOT / "assessment" / "manifest" / "controls.json"
BASELINE = REPO_ROOT / "assessment" / "manifest" / "automation-honesty-baseline.json"

sys.path.insert(0, str(REPO_ROOT / "assessment"))

from engine import score  # noqa: E402

VALID_AUTOMATION = ("full", "partial", "manual")


def load_manifest(path: Path = MANIFEST) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate_control(control: dict) -> dict:
    """Return the honesty facts for one control.

    Keys: ``automation``, ``auto_evaluable``, ``checks``, ``violation``
    (``None`` when the claim is honest, otherwise a human-readable reason).
    """
    automation = str(control.get("automation", "full"))
    methods = control.get("collection_methods", [])
    states = [
        score.classify_check_evaluator_state(check, automation, methods)
        for check in control.get("checks", [])
    ]
    auto_evaluable = states.count("auto_evaluable")
    total = len(states)

    violation: str | None = None
    if automation not in VALID_AUTOMATION:
        violation = (
            f"unknown automation value {automation!r} "
            f"(expected one of {', '.join(VALID_AUTOMATION)})"
        )
    elif automation == "full" and (total == 0 or auto_evaluable != total):
        violation = (
            f"claims full automation but only {auto_evaluable} of {total} "
            "checks have a registered evaluator"
        )
    elif automation == "partial" and auto_evaluable == 0:
        violation = (
            f"claims partial automation but none of its {total} checks "
            "have a registered evaluator"
        )

    return {
        "automation": automation,
        "auto_evaluable": auto_evaluable,
        "checks": total,
        "violation": violation,
    }


def collect_violations(controls: list[dict]) -> dict[str, dict]:
    """Map control id -> recorded facts for every control that overclaims."""
    violations: dict[str, dict] = {}
    for control in controls:
        facts = evaluate_control(control)
        if facts["violation"] is None:
            continue
        violations[str(control.get("id"))] = {
            "automation": facts["automation"],
            "auto_evaluable": facts["auto_evaluable"],
            "checks": facts["checks"],
            "reason": facts["violation"],
        }
    return violations


def load_baseline(path: Path = BASELINE) -> dict[str, dict]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("controls", {})


def render_baseline(violations: dict[str, dict]) -> str:
    payload = {
        "_comment": (
            "Pre-existing automation overclaims accepted as known debt. "
            "Managed by scripts/check_automation_honesty.py. This list is a "
            "one-way ratchet: --write refuses to add new control IDs, so it "
            "can only shrink as evaluators are wired or claims are corrected."
        ),
        "controls": {
            cid: violations[cid]
            for cid in sorted(violations, key=lambda c: [int(p) for p in c.split(".")])
        },
    }
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def check(controls: list[dict], baseline: dict[str, dict]) -> list[str]:
    """Return a list of failure messages (empty when the manifest is honest)."""
    violations = collect_violations(controls)
    failures: list[str] = []

    for cid in sorted(set(violations) - set(baseline)):
        failures.append(
            f"NEW OVERCLAIM {cid}: {violations[cid]['reason']}. "
            "Wire the evaluator or downgrade the automation claim; the "
            "baseline cannot absorb new entries."
        )

    for cid in sorted(set(baseline) - set(violations)):
        failures.append(
            f"STALE BASELINE {cid}: no longer overclaims. "
            "Run: python scripts/check_automation_honesty.py --write"
        )

    for cid in sorted(set(baseline) & set(violations)):
        if baseline[cid] != violations[cid]:
            failures.append(
                f"BASELINE DRIFT {cid}: recorded {baseline[cid]} but observed "
                f"{violations[cid]}. Run: "
                "python scripts/check_automation_honesty.py --write"
            )

    return failures


def write(controls: list[dict], baseline: dict[str, dict], path: Path = BASELINE) -> int:
    violations = collect_violations(controls)
    added = sorted(set(violations) - set(baseline))
    if added and baseline:
        print(
            "ERROR: refusing to add new control IDs to the baseline: "
            + ", ".join(added),
            file=sys.stderr,
        )
        for cid in added:
            print(f"  {cid}: {violations[cid]['reason']}", file=sys.stderr)
        print(
            "The baseline is a one-way ratchet. Fix the control instead.",
            file=sys.stderr,
        )
        return 1

    path.write_text(render_baseline(violations), encoding="utf-8")
    removed = sorted(set(baseline) - set(violations))
    try:
        label = path.relative_to(REPO_ROOT)
    except ValueError:
        label = path
    print(f"Wrote {label} ({len(violations)} known overclaims)")
    if removed:
        print("Cleared: " + ", ".join(removed))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit non-zero when the manifest overclaims automation (default).",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Regenerate the baseline. Refuses to add new control IDs.",
    )
    args = parser.parse_args(argv)

    controls = load_manifest()
    baseline = load_baseline()

    if args.write:
        return write(controls, baseline)

    failures = check(controls, baseline)
    if failures:
        print("Automation honesty check FAILED:\n", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1

    print(
        f"OK: automation claims are honest "
        f"({len(baseline)} known overclaims held at baseline)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
