#!/usr/bin/env python3
"""Validate ``assessment/data/solutions-lock.json``.

Per the v1.4+ cross-repo contract, this lock file is fetched from the
``FSI-AgentGov-Solutions`` repo at a pinned release tag and committed
locally so framework builds are reproducible.

Rules enforced:

* ``schemaVersion`` must start with ``"1.4."`` or ``"1.5."``.
* Top-level ``counts`` must exist with integer ``total``, ``live``, and
  ``preview`` keys, and must match the per-solution ``status`` rollup.
* ``solutions`` is an object keyed by kebab-case folder-name ID (or a
  list of objects with the same fields — both shapes accepted).
* Each solution has: ``id``, ``name``, ``version``, ``status``, ``domain``,
  ``tier`` ∈ {"1","2","3"}, ``description``, ``url``, ``controls``
  (list), ``prerequisites`` (object), and ``verification`` (string).

Bidirectional cross-check against ``assessment/manifest/controls.json``
(**errors** — CI-blocking):

The lock is the canonical contract and carries a ``controls`` array per
solution. The manifest carries a ``solutions`` array per control. Those
two express the *same* control-to-solution association set, so they must
agree in **both** directions:

* ``manifest-only`` — a ``(control, solution)`` pair present in the
  manifest with no backing in the lock.
* ``lock-only`` — a pair present in the lock that the manifest never
  records. Before issue #322 this direction was never checked, so 76
  associations went missing from the manifest without failing CI.

A pair may be exempted only by an explicit, reasoned entry in
``assessment/data/solutions-lock-exceptions.json``. Exceptions are
themselves validated: an exception that no longer matches live drift is
**stale** and fails, so the file cannot accumulate silent debt.

Exit code: 0 if lock is structurally valid and cross-checks clean;
1 otherwise.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
LOCK_DEFAULT = ROOT / "assessment" / "data" / "solutions-lock.json"
MANIFEST_DEFAULT = ROOT / "assessment" / "manifest" / "controls.json"
EXCEPTIONS_DEFAULT = ROOT / "assessment" / "data" / "solutions-lock-exceptions.json"

MANIFEST_ONLY = "manifest-only"
LOCK_ONLY = "lock-only"
EXCEPTION_DIRECTIONS = (MANIFEST_ONLY, LOCK_ONLY)

SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
CONTROL_ID_RE = re.compile(r"^\d+\.\d+$")
TIER_VALUES = {"1", "2", "3"}
STATUS_VALUES = {"live", "preview"}
COUNT_KEYS = ("total", "live", "preview")
ACCEPTED_SCHEMA_PREFIXES = ("1.4.", "1.5.")
REQUIRED_FIELDS = (
    "id",
    "name",
    "version",
    "status",
    "domain",
    "tier",
    "description",
    "url",
    "controls",
    "prerequisites",
    "verification",
)


def iter_solutions(lock: dict[str, Any]) -> Iterable[tuple[str, dict[str, Any]]]:
    sols = lock.get("solutions")
    if isinstance(sols, dict):
        for sid, body in sols.items():
            yield sid, body
    elif isinstance(sols, list):
        for body in sols:
            yield body.get("id", ""), body


def validate_solution(sid: str, body: dict[str, Any]) -> list[str]:
    errs: list[str] = []
    if not isinstance(body, dict):
        return [f"solutions[{sid}] must be an object"]

    for f in REQUIRED_FIELDS:
        if f not in body:
            errs.append(f"solutions[{sid}] missing field '{f}'")

    if "id" in body and body["id"] != sid:
        errs.append(f"solutions[{sid}].id ({body['id']!r}) does not match key {sid!r}")
    if not SLUG_RE.match(sid):
        errs.append(f"solutions[{sid}] id is not kebab-case (regex {SLUG_RE.pattern})")

    if "tier" in body and str(body["tier"]) not in TIER_VALUES:
        errs.append(
            f"solutions[{sid}].tier must be in {sorted(TIER_VALUES)} (got {body['tier']!r})"
        )

    if "status" in body and body["status"] not in STATUS_VALUES:
        errs.append(
            f"solutions[{sid}].status must be in {sorted(STATUS_VALUES)} (got {body['status']!r})"
        )

    if "controls" in body:
        if not isinstance(body["controls"], list):
            errs.append(f"solutions[{sid}].controls must be a list")
        else:
            for control_id in body["controls"]:
                if not isinstance(control_id, str) or not CONTROL_ID_RE.match(control_id):
                    errs.append(
                        f"solutions[{sid}].controls contains invalid control ID {control_id!r}"
                    )

    if "prerequisites" in body and not isinstance(body["prerequisites"], (dict, list)):
        errs.append(f"solutions[{sid}].prerequisites must be an object or list")

    if "url" in body and not (
        isinstance(body["url"], str) and body["url"].startswith(("http://", "https://"))
    ):
        errs.append(f"solutions[{sid}].url must be http(s)")

    return errs


def validate_counts(lock: dict[str, Any]) -> list[str]:
    errs: list[str] = []
    counts = lock.get("counts")
    if not isinstance(counts, dict):
        return ["counts block must be present at the top level of solutions-lock.json"]
    for key in COUNT_KEYS:
        if not isinstance(counts.get(key), int):
            errs.append(f"counts.{key} must be an integer")

    if errs:
        return errs

    derived = {"total": 0, "live": 0, "preview": 0}
    for _sid, body in iter_solutions(lock):
        derived["total"] += 1
        status = body.get("status") if isinstance(body, dict) else None
        if status in ("live", "preview"):
            derived[status] += 1

    for key in COUNT_KEYS:
        if counts[key] != derived[key]:
            errs.append(
                f"counts.{key} ({counts[key]!r}) does not match derived value {derived[key]!r}"
            )
    return errs


def load_manifest_controls(manifest_path: Path) -> list[dict[str, Any]]:
    """Return the manifest control list, tolerating both accepted shapes."""
    raw = json.loads(manifest_path.read_text(encoding="utf-8"))
    if isinstance(raw, list):
        return [c for c in raw if isinstance(c, dict)]
    if isinstance(raw, dict):
        controls = raw.get("controls", [])
        if isinstance(controls, list):
            return [c for c in controls if isinstance(c, dict)]
    return []


def lock_pairs(lock: dict[str, Any]) -> set[tuple[str, str]]:
    """Every ``(control_id, solution_id)`` association declared by the lock."""
    pairs: set[tuple[str, str]] = set()
    for sid, body in iter_solutions(lock):
        if not isinstance(body, dict):
            continue
        for control_id in body.get("controls", []) or []:
            if isinstance(control_id, str):
                pairs.add((control_id, sid))
    return pairs


def manifest_pairs(controls: list[dict[str, Any]]) -> set[tuple[str, str]]:
    """Every ``(control_id, solution_id)`` association declared by the manifest."""
    pairs: set[tuple[str, str]] = set()
    for ctrl in controls:
        cid = ctrl.get("id")
        if not isinstance(cid, str):
            continue
        for sid in ctrl.get("solutions", []) or []:
            if isinstance(sid, str):
                pairs.add((cid, sid))
    return pairs


def load_exceptions(path: Path) -> tuple[dict[tuple[str, str, str], str], list[str]]:
    """Load documented cross-check exemptions.

    Returns ``(exceptions, errors)`` where ``exceptions`` maps
    ``(control, solution, direction)`` to the recorded reason.
    """
    if not path.exists():
        return {}, []

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {}, [f"exceptions file is not valid JSON: {exc}"]

    entries = raw.get("exceptions") if isinstance(raw, dict) else raw
    if not isinstance(entries, list):
        return {}, ["exceptions file must contain an 'exceptions' list"]

    exceptions: dict[tuple[str, str, str], str] = {}
    errors: list[str] = []
    for i, entry in enumerate(entries):
        if not isinstance(entry, dict):
            errors.append(f"exceptions[{i}] must be an object")
            continue
        control = entry.get("control")
        solution = entry.get("solution")
        direction = entry.get("direction")
        reason = entry.get("reason")
        if not (isinstance(control, str) and CONTROL_ID_RE.match(control)):
            errors.append(f"exceptions[{i}].control must be a control ID like '1.1'")
            continue
        if not (isinstance(solution, str) and SLUG_RE.match(solution)):
            errors.append(f"exceptions[{i}].solution must be a kebab-case solution id")
            continue
        if direction not in EXCEPTION_DIRECTIONS:
            errors.append(
                f"exceptions[{i}].direction must be one of "
                f"{list(EXCEPTION_DIRECTIONS)} (got {direction!r})"
            )
            continue
        if not (isinstance(reason, str) and reason.strip()):
            errors.append(
                f"exceptions[{i}] ({control}/{solution}) must carry a non-empty "
                "'reason' explaining why the drift is accepted"
            )
            continue
        key = (control, solution, direction)
        if key in exceptions:
            errors.append(f"exceptions[{i}] duplicates {control}/{solution}/{direction}")
            continue
        exceptions[key] = reason.strip()
    return exceptions, errors


def cross_check(
    lock: dict[str, Any],
    manifest_path: Path,
    exceptions_path: Path,
) -> tuple[list[str], list[str]]:
    """Bidirectionally compare lock and manifest associations.

    Returns ``(errors, infos)``. Every unexempted association present on
    only one side is an error, in either direction.
    """
    if not manifest_path.exists():
        return ([f"manifest not found at {manifest_path}; cannot cross-check"], [])

    try:
        controls = load_manifest_controls(manifest_path)
    except json.JSONDecodeError as exc:
        return ([f"manifest is not valid JSON: {exc}"], [])

    exceptions, errors = load_exceptions(exceptions_path)
    infos: list[str] = []

    lock_ids = {sid for sid, _ in iter_solutions(lock)}
    manifest_ids = {c["id"] for c in controls if isinstance(c.get("id"), str)}

    in_lock = lock_pairs(lock)
    in_manifest = manifest_pairs(controls)

    only_manifest = in_manifest - in_lock
    only_lock = in_lock - in_manifest

    used: set[tuple[str, str, str]] = set()

    def exempt(control: str, solution: str, direction: str) -> bool:
        key = (control, solution, direction)
        if key in exceptions:
            used.add(key)
            infos.append(
                f"documented exception ({direction}) {control} -> {solution}: "
                f"{exceptions[key]}"
            )
            return True
        return False

    # Direction 1: manifest asserts an association the lock does not back.
    unknown_slugs: dict[str, list[str]] = {}
    for control, solution in sorted(only_manifest):
        if exempt(control, solution, MANIFEST_ONLY):
            continue
        if solution not in lock_ids:
            unknown_slugs.setdefault(solution, []).append(control)
            continue
        errors.append(
            f"manifest-only association: control {control} lists solution "
            f"{solution!r}, but the lock's solutions[{solution}].controls does not "
            "include that control"
        )
    for solution, ctrls in sorted(unknown_slugs.items()):
        errors.append(
            f"manifest-only association: solution {solution!r} referenced by "
            f"controls {sorted(set(ctrls))} is not in the lock at all"
        )

    # Direction 2: the lock declares an association the manifest never records.
    # This direction was unchecked before issue #322.
    for control, solution in sorted(only_lock):
        if exempt(control, solution, LOCK_ONLY):
            continue
        if control not in manifest_ids:
            errors.append(
                f"lock-only association: solutions[{solution}].controls references "
                f"control {control!r}, which is not in the manifest"
            )
            continue
        errors.append(
            f"lock-only association: solutions[{solution}].controls includes control "
            f"{control}, but the manifest's controls[{control}].solutions omits "
            f"{solution!r}"
        )

    # Stale exceptions are debt in disguise — fail so they get removed.
    for control, solution, direction in sorted(set(exceptions) - used):
        errors.append(
            f"stale exception: {control} -> {solution} ({direction}) no longer "
            "drifts; remove it from solutions-lock-exceptions.json"
        )

    return errors, infos


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lock", type=Path, default=LOCK_DEFAULT)
    parser.add_argument("--manifest", type=Path, default=MANIFEST_DEFAULT)
    parser.add_argument(
        "--exceptions",
        type=Path,
        default=EXCEPTIONS_DEFAULT,
        help="Documented cross-check exemptions (missing file = no exemptions).",
    )
    parser.add_argument(
        "--allow-missing",
        action="store_true",
        help="Treat a missing lock file as a warning (graceful degradation).",
    )
    args = parser.parse_args()

    if not args.lock.exists():
        msg = f"solutions-lock.json not found at {args.lock}"
        if args.allow_missing:
            print(f"WARN: {msg} — E1/E7 will render without solution chips.")
            return 0
        print(f"ERROR: {msg}", file=sys.stderr)
        return 1

    try:
        lock = json.loads(args.lock.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"ERROR: lock is not valid JSON: {exc}", file=sys.stderr)
        return 1

    errs: list[str] = []
    sv = lock.get("schemaVersion", "")
    if not (isinstance(sv, str) and sv.startswith(ACCEPTED_SCHEMA_PREFIXES)):
        accepted = ", ".join(repr(p) for p in ACCEPTED_SCHEMA_PREFIXES)
        errs.append(
            f"schemaVersion must start with one of {accepted} (got {sv!r}); "
            "refresh the lock against a supported FSI-AgentGov-Solutions release tag."
        )

    errs.extend(validate_counts(lock))

    sol_count = 0
    for sid, body in iter_solutions(lock):
        sol_count += 1
        errs.extend(validate_solution(sid, body))

    warns: list[str] = []
    cross_errs, infos = cross_check(lock, args.manifest, args.exceptions)
    errs.extend(cross_errs)

    for i in infos:
        print(f"INFO: {i}")
    for w in warns:
        print(f"WARN: {w}")
    for e in errs:
        print(f"ERROR: {e}", file=sys.stderr)

    if errs:
        print(f"\nFAIL: {len(errs)} error(s), {len(warns)} warning(s).", file=sys.stderr)
        return 1

    print(
        f"OK: solutions-lock.json valid ({sol_count} solutions, "
        f"manifest cross-check clean in both directions, "
        f"{len(infos)} documented exception(s))."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
