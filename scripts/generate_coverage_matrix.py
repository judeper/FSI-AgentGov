#!/usr/bin/env python3
"""Generate the 78-control evaluator coverage matrix.

Reads ``assessment/manifest/controls.json`` and the ``EVALUATORS`` registry
from ``assessment/engine/score.py`` and writes a Markdown coverage report
to ``docs/reference/assessment-coverage.md``.

The matrix is the canonical answer to the question "what does the
assessment engine actually automate today?" — distinguishing:

* ``auto_evaluable`` — bespoke evaluator wired up
* ``manual_only`` — manual by design (manual control or non-automatable
  collection method)
* ``unimplemented_evaluator`` — pass condition exists but no evaluator
  is registered yet (today's biggest coverage gap)

Run::

    python scripts/generate_coverage_matrix.py

CI may also call this with ``--check`` to fail when the doc is stale.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ENGINE_DIR = REPO_ROOT / "assessment" / "engine"
MANIFEST_PATH = REPO_ROOT / "assessment" / "manifest" / "controls.json"
OUTPUT_PATH = REPO_ROOT / "docs" / "reference" / "assessment-coverage.md"

sys.path.insert(0, str(ENGINE_DIR))

import score  # type: ignore[import-untyped]  # noqa: E402

STATE_LABEL = {
    "auto_evaluable": "Auto",
    "unimplemented_evaluator": "Unimplemented",
    "manual_only": "Manual",
}

STATE_ICON = {
    "auto_evaluable": "✅",
    "unimplemented_evaluator": "⚠️",
    "manual_only": "📝",
}


def load_controls() -> list[dict]:
    raw = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return raw if isinstance(raw, list) else raw.get("controls", [])


def collection_sources(check: dict, control: dict) -> str:
    methods = check.get("collection_methods") or control.get(
        "collection_methods", []
    )
    if not methods:
        return "—"
    return ", ".join(sorted(set(methods)))


def caveat_for_check(check: dict, state: str) -> str:
    cond = (check.get("pass_condition") or "").strip()
    if state == "auto_evaluable":
        return ""
    if state == "manual_only":
        return "Manual review required."
    return (
        f"`pass_condition: {cond}` declared in manifest but no bespoke "
        f"evaluator registered in score.py. Result will be `unknown`."
    )


def render(controls: list[dict]) -> str:
    registered = sorted(score.EVALUATORS.keys())
    total_controls = len(controls)
    control_states: Counter = Counter()
    check_states: Counter = Counter()

    pillars: dict[int, list[dict]] = {}
    for ctrl in controls:
        cm = ctrl.get("collection_methods", [])
        automation = ctrl.get("automation", "full")
        per_check_states = []
        for chk in ctrl.get("checks", []):
            s = score.classify_check_evaluator_state(chk, automation, cm)
            per_check_states.append(s)
            check_states[s] += 1
        rollup = score.rollup_control_evaluator_state(automation, per_check_states)
        control_states[rollup] += 1
        pillars.setdefault(int(ctrl["pillar"]), []).append(
            {
                "control": ctrl,
                "rollup": rollup,
                "check_states": per_check_states,
            }
        )

    lines: list[str] = []
    lines.append("# Assessment Engine Coverage Matrix")
    lines.append("")
    lines.append(
        "This page is **generated** by `scripts/generate_coverage_matrix.py` "
        "from `assessment/manifest/controls.json` and the `EVALUATORS` "
        "registry in `assessment/engine/score.py`. Do not edit by hand."
    )
    lines.append("")
    lines.append(
        "It is the honest answer to *what does the assessment engine "
        "actually automate today?* and is intended to prevent confusion "
        "between **manual by design** and **evaluator not yet implemented**."
    )
    lines.append("")
    lines.append("## Evaluator states")
    lines.append("")
    lines.append("| State | Icon | Meaning |")
    lines.append("|-------|------|---------|")
    lines.append(
        "| `auto_evaluable` | ✅ | A bespoke evaluator is registered for the "
        "check's `pass_condition` and the engine can score it from collected "
        "telemetry. |"
    )
    lines.append(
        "| `unimplemented_evaluator` | ⚠️ | The manifest declares a "
        "`pass_condition`, but no evaluator function is registered yet. "
        "The generic fallback returns `unknown`. |"
    )
    lines.append(
        "| `manual_only` | 📝 | The control is manual by design — either "
        "`automation: manual` in the manifest or all collection methods are "
        "non-automatable. Reviewer must answer the manual question. |"
    )
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("### By control")
    lines.append("")
    lines.append("| State | Count | Share |")
    lines.append("|-------|-------|-------|")
    for s in score.EVALUATOR_STATES:
        n = control_states.get(s, 0)
        pct = (n / total_controls * 100) if total_controls else 0
        lines.append(f"| {STATE_ICON[s]} {STATE_LABEL[s]} | {n} | {pct:.1f}% |")
    lines.append(f"| **Total** | **{total_controls}** | 100% |")
    lines.append("")
    total_checks = sum(check_states.values())
    lines.append("### By check")
    lines.append("")
    lines.append("| State | Count | Share |")
    lines.append("|-------|-------|-------|")
    for s in score.EVALUATOR_STATES:
        n = check_states.get(s, 0)
        pct = (n / total_checks * 100) if total_checks else 0
        lines.append(f"| {STATE_ICON[s]} {STATE_LABEL[s]} | {n} | {pct:.1f}% |")
    lines.append(f"| **Total** | **{total_checks}** | 100% |")
    lines.append("")
    lines.append("### Registered evaluators")
    lines.append("")
    lines.append(
        f"`assessment/engine/score.py` registers **{len(registered)}** "
        "bespoke evaluator functions:"
    )
    lines.append("")
    for name in registered:
        lines.append(f"- `{name}`")
    lines.append("")
    used_conditions = {
        chk.get("pass_condition")
        for ctrl in controls
        for chk in ctrl.get("checks", [])
    }
    unused = sorted(set(registered) - used_conditions)
    if unused:
        lines.append(
            "**Drift warning** — the following evaluators are registered "
            "but no manifest check uses them as a `pass_condition`. This "
            "usually means the manifest condition string drifted from "
            "the evaluator key:"
        )
        lines.append("")
        for name in unused:
            lines.append(f"- `{name}`")
        lines.append("")

    lines.append("## Per-pillar matrix")
    lines.append("")

    for pillar_id in sorted(pillars):
        first = pillars[pillar_id][0]["control"]
        lines.append(f"### Pillar {pillar_id} – {first['pillar_name']}")
        lines.append("")
        lines.append(
            "| Control | Title | State | Auto | Unimpl | Manual | "
            "Collection | Caveats |"
        )
        lines.append(
            "|---------|-------|-------|------|--------|--------|"
            "------------|---------|"
        )
        for entry in sorted(
            pillars[pillar_id], key=lambda e: e["control"]["id"]
        ):
            ctrl = entry["control"]
            states = entry["check_states"]
            counts = Counter(states)
            sources = ", ".join(
                sorted(set(ctrl.get("collection_methods", []) or ["—"]))
            )
            # Caveats: prefer the most specific drift message.
            caveats: list[str] = []
            for chk in ctrl.get("checks", []):
                s = score.classify_check_evaluator_state(
                    chk, ctrl.get("automation", "full"),
                    ctrl.get("collection_methods", []),
                )
                msg = caveat_for_check(chk, s)
                if msg and msg not in caveats:
                    caveats.append(msg)
            caveat_text = " ".join(caveats) if caveats else ""
            # Truncate to keep the table readable.
            if len(caveat_text) > 240:
                caveat_text = caveat_text[:237] + "…"
            # Escape pipes in title and caveat text.
            title = ctrl["title"].replace("|", "\\|")
            caveat_text = caveat_text.replace("|", "\\|")
            lines.append(
                f"| {ctrl['id']} | {title} | "
                f"{STATE_ICON[entry['rollup']]} {STATE_LABEL[entry['rollup']]} "
                f"| {counts.get('auto_evaluable', 0)} "
                f"| {counts.get('unimplemented_evaluator', 0)} "
                f"| {counts.get('manual_only', 0)} "
                f"| {sources} | {caveat_text} |"
            )
        lines.append("")

    lines.append("## How to add a new evaluator")
    lines.append("")
    lines.append(
        "1. Add a `_eval_<name>(collected, source_key)` function to "
        "`assessment/engine/score.py` returning `(passed: bool | None, "
        "evidence: str)`."
    )
    lines.append(
        "2. Register it in the `EVALUATORS` dict using the same string "
        "as the manifest's `pass_condition`."
    )
    lines.append(
        "3. Add a fixture and a unit test in `assessment/tests/`."
    )
    lines.append(
        "4. Re-run `python scripts/generate_coverage_matrix.py` and commit "
        "the regenerated `docs/reference/assessment-coverage.md`."
    )
    lines.append("")
    lines.append(
        "<!-- This page is generated by scripts/generate_coverage_matrix.py. "
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
        help="Override output path (default: docs/reference/assessment-coverage.md)",
    )
    args = parser.parse_args(argv)

    controls = load_controls()
    rendered = render(controls)
    target = Path(args.output)

    if args.check:
        if not target.exists():
            print(
                f"ERROR: {target} does not exist. Run "
                "`python scripts/generate_coverage_matrix.py` to create it.",
                file=sys.stderr,
            )
            return 1
        existing = target.read_text(encoding="utf-8")
        if existing != rendered:
            print(
                f"ERROR: {target} is out of date. Run "
                "`python scripts/generate_coverage_matrix.py` and commit.",
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
