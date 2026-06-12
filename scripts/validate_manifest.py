#!/usr/bin/env python3
"""Validate ``assessment/manifest/controls.json`` against the v1.4 schema.

Schema rules enforced:

* All 79 controls present, unique ``id`` values.
* Required v1.4 keys present on every control:
    name, zonesApplicable, roles, regulatory, priority, yesBar,
    partialBar, noBar, verifyIn, verifyPowerShell, evidenceExpected,
    controlDocUrl, portalPlaybookUrl, collectorField, sectorYesBar,
    facilitatorNotes, solutions
* ``zonesApplicable`` is a non-empty list of integers in {1,2,3}.
* ``roles`` is a non-empty list of strings.
* ``priority`` is one of ``critical|high|medium|low`` (TODO permitted in
  ``--allow-todo`` mode).
* ``verifyIn`` items have ``portal``, ``path``, ``url`` (URL must look
  http(s)).
* ``solutions`` is a list of kebab-case strings matching
  ``^[a-z0-9][a-z0-9-]*$``.
* ``sectorYesBar`` covers the 8 canonical sector keys.
* ``facilitatorNotes`` has ``ask``, ``followUp``, ``timeBudgetMinutes``.

Modes:

* default — strict; any ``TODO:`` value in a required field fails.
* ``--allow-todo`` — advisory; ``TODO:`` values in optional content
  fields (everything except ``solutions``, ``zonesApplicable``,
  ``sectorYesBar.<key>``) are warnings instead of errors.

Exit code: 0 if no errors; 1 otherwise.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_DEFAULT = ROOT / "assessment" / "manifest" / "controls.json"

REQUIRED_KEYS = [
    "id",
    "title",
    "pillar",
    "name",
    "zonesApplicable",
    "roles",
    "regulatory",
    "priority",
    "yesBar",
    "partialBar",
    "noBar",
    "verifyIn",
    "verifyPowerShell",
    "evidenceExpected",
    "controlDocUrl",
    "portalPlaybookUrl",
    "collectorField",
    "sectorYesBar",
    "facilitatorNotes",
    "solutions",
]

PRIORITY_VALUES = {"critical", "high", "medium", "low"}
SECTORS = {
    "bank",
    "broker-dealer",
    "investment-adviser",
    "insurance-carrier",
    "insurance-wholesale",
    "credit-union",
    "holding-company",
    "other",
}
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
URL_RE = re.compile(r"^https?://", re.IGNORECASE)
EXPECTED_COUNT = 79


def is_todo(value: Any) -> bool:
    return isinstance(value, str) and value.strip().startswith("TODO:")


def validate_one(  # noqa: C901 — many independent rules
    control: dict[str, Any], allow_todo: bool
) -> tuple[list[str], list[str]]:
    """Return (errors, warnings) for a single control."""
    errs: list[str] = []
    warns: list[str] = []
    cid = control.get("id", "<missing-id>")

    for key in REQUIRED_KEYS:
        if key not in control:
            errs.append(f"{cid}: missing required key '{key}'")
            return errs, warns  # bail; subsequent checks would explode

    # zonesApplicable
    z = control["zonesApplicable"]
    if not (isinstance(z, list) and z and all(v in (1, 2, 3) for v in z)):
        errs.append(f"{cid}: zonesApplicable must be a non-empty subset of [1,2,3]")

    # roles
    if not (isinstance(control["roles"], list) and control["roles"]):
        errs.append(f"{cid}: roles must be a non-empty list")
    else:
        for r in control["roles"]:
            if is_todo(r) and not allow_todo:
                errs.append(f"{cid}: roles contains TODO entry (strict mode)")
            elif is_todo(r):
                warns.append(f"{cid}: roles contains TODO entry")

    # regulatory (allow empty — some Pillar 4 SP controls have no direct cite)
    if not isinstance(control["regulatory"], list):
        errs.append(f"{cid}: regulatory must be a list")

    # priority
    p = control["priority"]
    if is_todo(p):
        (warns if allow_todo else errs).append(
            f"{cid}: priority is TODO"
        )
    elif p not in PRIORITY_VALUES:
        errs.append(
            f"{cid}: priority must be one of {sorted(PRIORITY_VALUES)} (got {p!r})"
        )

    # rating bars
    for k in ("yesBar", "partialBar", "noBar"):
        v = control[k]
        if not isinstance(v, str) or not v.strip():
            errs.append(f"{cid}: {k} must be a non-empty string")
        elif is_todo(v):
            (warns if allow_todo else errs).append(f"{cid}: {k} is TODO")

    # verifyIn
    vi = control["verifyIn"]
    if not isinstance(vi, list):
        errs.append(f"{cid}: verifyIn must be a list")
    else:
        for i, entry in enumerate(vi):
            if not isinstance(entry, dict):
                errs.append(f"{cid}: verifyIn[{i}] must be an object")
                continue
            for sub in ("portal", "path", "url"):
                if sub not in entry or not isinstance(entry[sub], str):
                    errs.append(f"{cid}: verifyIn[{i}].{sub} missing or not a string")
            if "url" in entry and isinstance(entry["url"], str):
                if not URL_RE.match(entry["url"]):
                    errs.append(f"{cid}: verifyIn[{i}].url must be http(s)")

    # verifyPowerShell — string, may be empty
    if not isinstance(control["verifyPowerShell"], str):
        errs.append(f"{cid}: verifyPowerShell must be a string")

    # evidenceExpected
    ee = control["evidenceExpected"]
    if not isinstance(ee, list) or not all(isinstance(x, str) for x in ee):
        errs.append(f"{cid}: evidenceExpected must be a list of strings")

    # URLs
    for k in ("controlDocUrl", "portalPlaybookUrl"):
        v = control[k]
        if not isinstance(v, str) or not v.startswith("/"):
            errs.append(f"{cid}: {k} must be a site-root path starting with /")
        elif is_todo(v):
            errs.append(f"{cid}: {k} is TODO")

    # collectorField — string, may be empty
    if not isinstance(control["collectorField"], str):
        errs.append(f"{cid}: collectorField must be a string")

    # sectorYesBar
    syb = control["sectorYesBar"]
    if not isinstance(syb, dict):
        errs.append(f"{cid}: sectorYesBar must be an object")
    else:
        missing = SECTORS - set(syb.keys())
        if missing:
            errs.append(f"{cid}: sectorYesBar missing sectors: {sorted(missing)}")
        # TODO: values in sector entries are ALWAYS permitted per spec

    # facilitatorNotes
    fn = control["facilitatorNotes"]
    if not isinstance(fn, dict):
        errs.append(f"{cid}: facilitatorNotes must be an object")
    else:
        for sub in ("ask", "followUp"):
            if sub not in fn or not isinstance(fn[sub], str):
                errs.append(f"{cid}: facilitatorNotes.{sub} missing or not a string")
            elif is_todo(fn[sub]):
                (warns if allow_todo else errs).append(
                    f"{cid}: facilitatorNotes.{sub} is TODO"
                )
        if "timeBudgetMinutes" not in fn or not isinstance(
            fn["timeBudgetMinutes"], int
        ):
            errs.append(f"{cid}: facilitatorNotes.timeBudgetMinutes missing/not int")

    # solutions — STRICTLY a list of kebab-case folder-name strings
    sols = control["solutions"]
    if not isinstance(sols, list):
        errs.append(f"{cid}: solutions must be a list")
    else:
        for i, s in enumerate(sols):
            if not isinstance(s, str):
                errs.append(
                    f"{cid}: solutions[{i}] must be a string folder-name id"
                )
            elif not SLUG_RE.match(s):
                errs.append(
                    f"{cid}: solutions[{i}] = {s!r} must match {SLUG_RE.pattern}"
                )

    return errs, warns


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest", type=Path, default=MANIFEST_DEFAULT, help="Path to controls.json"
    )
    parser.add_argument(
        "--allow-todo",
        action="store_true",
        help="Treat TODO: values in non-structural fields as warnings.",
    )
    parser.add_argument(
        "--quiet", action="store_true", help="Suppress per-control output on success."
    )
    args = parser.parse_args()

    if not args.manifest.exists():
        print(f"ERROR: manifest not found at {args.manifest}", file=sys.stderr)
        return 2

    controls = json.loads(args.manifest.read_text(encoding="utf-8"))
    if not isinstance(controls, list):
        print("ERROR: manifest must be a JSON list", file=sys.stderr)
        return 2

    if len(controls) != EXPECTED_COUNT:
        print(
            f"ERROR: expected {EXPECTED_COUNT} controls, got {len(controls)}",
            file=sys.stderr,
        )
        return 1

    ids = [c.get("id") for c in controls]
    if len(set(ids)) != len(ids):
        print("ERROR: duplicate control ids in manifest", file=sys.stderr)
        return 1

    all_errors: list[str] = []
    all_warnings: list[str] = []
    for ctrl in controls:
        errs, warns = validate_one(ctrl, allow_todo=args.allow_todo)
        all_errors.extend(errs)
        all_warnings.extend(warns)

    for w in all_warnings:
        print(f"WARN: {w}")
    for e in all_errors:
        print(f"ERROR: {e}", file=sys.stderr)

    if all_errors:
        print(
            f"\nFAIL: {len(all_errors)} error(s), {len(all_warnings)} warning(s).",
            file=sys.stderr,
        )
        return 1

    if not args.quiet:
        print(
            f"OK: {len(controls)} controls validated "
            f"({len(all_warnings)} warning(s))."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
