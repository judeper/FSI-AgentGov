#!/usr/bin/env python3
"""Sync ``controls.json.solutions[]`` from the canonical solutions lock.

``assessment/data/solutions-lock.json`` is the canonical control-to-solution
contract: each solution declares the controls it covers. The assessment
manifest expresses the same relation from the other side, as a ``solutions``
array per control. The two must stay in lockstep.

This is the write-side companion to ``scripts/validate_solutions_lock.py``,
which is the read-side CI gate. After a lock refresh
(``scripts/refresh_solutions_lock.py``) introduces new associations, run::

    python scripts/sync_manifest_solutions.py --write

Manifest-side associations that the lock does not back are **not** removed
automatically. Deleting locally curated associations to match an upstream
file the framework repo does not own would be a silent contract change, so
they are reported instead and must be either dropped by hand or recorded in
``assessment/data/solutions-lock-exceptions.json`` with a reason.

Exit code: 0 when the manifest already matches (or was written with
``--write``); 1 when additions are pending in ``--check`` mode.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LOCK_DEFAULT = ROOT / "assessment" / "data" / "solutions-lock.json"
MANIFEST_DEFAULT = ROOT / "assessment" / "manifest" / "controls.json"


def iter_solutions(lock: dict[str, Any]):
    sols = lock.get("solutions")
    if isinstance(sols, dict):
        yield from sols.items()
    elif isinstance(sols, list):
        for body in sols:
            if isinstance(body, dict):
                yield body.get("id", ""), body


def lock_solutions_by_control(lock: dict[str, Any]) -> dict[str, set[str]]:
    by_control: dict[str, set[str]] = {}
    for sid, body in iter_solutions(lock):
        if not isinstance(body, dict) or not isinstance(sid, str):
            continue
        for control_id in body.get("controls", []) or []:
            if isinstance(control_id, str):
                by_control.setdefault(control_id, set()).add(sid)
    return by_control


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lock", type=Path, default=LOCK_DEFAULT)
    parser.add_argument("--manifest", type=Path, default=MANIFEST_DEFAULT)
    parser.add_argument(
        "--write",
        action="store_true",
        help="Apply lock-only additions to the manifest (default is report-only).",
    )
    args = parser.parse_args(argv)

    lock = json.loads(args.lock.read_text(encoding="utf-8"))
    controls = json.loads(args.manifest.read_text(encoding="utf-8"))
    if not isinstance(controls, list):
        print("ERROR: manifest must be a JSON list", file=sys.stderr)
        return 2

    by_control = lock_solutions_by_control(lock)
    manifest_ids = {c.get("id") for c in controls if isinstance(c, dict)}

    added: list[tuple[str, str]] = []
    manifest_only: list[tuple[str, str]] = []

    for ctrl in controls:
        if not isinstance(ctrl, dict):
            continue
        cid = ctrl.get("id")
        current = [s for s in ctrl.get("solutions", []) or [] if isinstance(s, str)]
        expected = by_control.get(cid, set())

        for sid in sorted(expected - set(current)):
            added.append((cid, sid))
        for sid in sorted(set(current) - expected):
            manifest_only.append((cid, sid))

        merged = sorted(set(current) | expected)
        if merged != current:
            ctrl["solutions"] = merged

    orphans = sorted(
        (cid, sid)
        for cid, sids in by_control.items()
        if cid not in manifest_ids
        for sid in sids
    )

    for cid, sid in added:
        print(f"{'ADD ' if args.write else 'MISS'} {cid} -> {sid}")
    for cid, sid in manifest_only:
        print(f"KEEP {cid} -> {sid} (manifest-only; needs a documented exception)")
    for cid, sid in orphans:
        print(f"WARN lock references unknown control {cid} (solution {sid})")

    if added and args.write:
        args.manifest.write_text(
            json.dumps(controls, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"\nWrote {len(added)} association(s) to {args.manifest}")
        return 0

    if added:
        print(
            f"\nFAIL: {len(added)} lock association(s) missing from the manifest. "
            "Re-run with --write.",
            file=sys.stderr,
        )
        return 1

    print("\nOK: manifest solutions[] already covers every lock association.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
