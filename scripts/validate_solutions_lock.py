#!/usr/bin/env python3
"""Validate ``assessment/data/solutions-lock.json``.

Per the v1.4+ cross-repo contract, this lock file is fetched from the
``FSI-AgentGov-Solutions`` repo at a pinned release tag and committed
locally so framework builds are reproducible.

Rules enforced:

* ``schemaVersion`` must start with ``"1.4."`` or ``"1.5."`` (both
  accepted; 1.5.0 made the producer-side ``zones`` field required, but
  the consumer treats either version as structurally valid).
* ``solutions`` is an object keyed by kebab-case folder-name ID (or a
  list of objects with the same fields — both shapes accepted).
* Each solution has: ``id``, ``name``, ``version``, ``domain``,
  ``tier`` ∈ {"1","2","3"}, ``description``, ``url``, ``prerequisites``
  (object), ``verification`` (string).

Cross-check (warning only — graceful degradation per spec):
* Every solution id referenced in ``controls.json.solutions[]`` should
  exist in the lock; missing IDs emit a warning but do **not** fail.

Exit code: 0 if lock is structurally valid; 1 otherwise.
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

SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
TIER_VALUES = {"1", "2", "3"}
ACCEPTED_SCHEMA_PREFIXES = ("1.4.", "1.5.")
REQUIRED_FIELDS = (
    "id",
    "name",
    "version",
    "domain",
    "tier",
    "description",
    "url",
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

    if "prerequisites" in body and not isinstance(body["prerequisites"], (dict, list)):
        errs.append(f"solutions[{sid}].prerequisites must be an object or list")

    if "url" in body and not (
        isinstance(body["url"], str) and body["url"].startswith(("http://", "https://"))
    ):
        errs.append(f"solutions[{sid}].url must be http(s)")

    return errs


def cross_check(lock: dict[str, Any], manifest_path: Path) -> list[str]:
    """Emit warnings for solutions referenced from controls.json but missing in lock."""
    if not manifest_path.exists():
        return []
    controls = json.loads(manifest_path.read_text(encoding="utf-8"))
    lock_ids = {sid for sid, _ in iter_solutions(lock)}
    missing: dict[str, list[str]] = {}
    for ctrl in controls:
        for sid in ctrl.get("solutions", []):
            if isinstance(sid, str) and sid not in lock_ids:
                missing.setdefault(sid, []).append(ctrl.get("id", "?"))
    return [
        f"solution {sid!r} referenced by controls {sorted(set(ctrls))} is not in the lock"
        for sid, ctrls in sorted(missing.items())
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lock", type=Path, default=LOCK_DEFAULT)
    parser.add_argument("--manifest", type=Path, default=MANIFEST_DEFAULT)
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

    sol_count = 0
    for sid, body in iter_solutions(lock):
        sol_count += 1
        errs.extend(validate_solution(sid, body))

    warns = cross_check(lock, args.manifest)

    for w in warns:
        print(f"WARN: {w}")
    for e in errs:
        print(f"ERROR: {e}", file=sys.stderr)

    if errs:
        print(f"\nFAIL: {len(errs)} error(s), {len(warns)} warning(s).", file=sys.stderr)
        return 1

    print(f"OK: solutions-lock.json valid ({sol_count} solutions, {len(warns)} warning(s)).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
