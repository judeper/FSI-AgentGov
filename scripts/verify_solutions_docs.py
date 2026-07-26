#!/usr/bin/env python3
"""Verify that framework solution docs consume the pinned solutions lock contract.

Checks:

1. ``docs/reference/solutions-index.md`` inventory rows must match the pinned
   ``assessment/data/solutions-lock.json`` for version and canonical control
   coverage.
2. ``docs/reference/solutions-index.md`` detail blocks must match the pinned
   lock for version, preview status (when applicable), and canonical control
   coverage.
3. ``docs/framework/solutions-integration.md`` is allowed to be illustrative,
   but every solution example must include a repository link to a canonical
   solution ID, must only cite control IDs present in that solution's canonical
   ``controls`` array, and must not publish a separate per-solution status line.
4. A control document under ``docs/controls/`` must not carry the
   "no companion solution" sentinel when the pinned lock maps one or more
   solutions to that control ID. This is a contradiction check only: it does not
   require a control to enumerate every solution mapped to it, and it does not
   forbid a control from cross-referencing a solution that is not mapped to it.

Usage::

    python scripts/verify_solutions_docs.py
    python scripts/verify_solutions_docs.py --check
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[1]
LOCK_FILE = REPO_ROOT / "assessment" / "data" / "solutions-lock.json"
SOLUTIONS_INDEX = REPO_ROOT / "docs" / "reference" / "solutions-index.md"
SOLUTIONS_INTEGRATION = REPO_ROOT / "docs" / "framework" / "solutions-integration.md"
CONTROLS_DIR = REPO_ROOT / "docs" / "controls"

NO_SOLUTION_SENTINEL = "No companion solution for this control"
CONTROL_FILE_RE = re.compile(r"^(\d+\.\d+)-")

CONTROL_ID_RE = re.compile(r"\d+\.\d+")
FOLDER_RE = re.compile(r"\[`([^`]+)`\]")
REPO_LINK_RE = re.compile(
    r"https://github\.com/judeper/FSI-AgentGov-Solutions/tree/main/([^\)]+)"
)


def _iter_solutions(lock: dict) -> Iterable[tuple[str, dict]]:
    solutions = lock.get("solutions") or {}
    if isinstance(solutions, dict):
        yield from solutions.items()
    else:
        for item in solutions:
            if isinstance(item, dict):
                yield item.get("id", ""), item


def load_lock() -> dict[str, dict]:
    lock = json.loads(LOCK_FILE.read_text(encoding="utf-8"))
    return {sid: body for sid, body in _iter_solutions(lock)}


def _parse_controls(cell: str) -> list[str]:
    value = cell.strip()
    if value == "—":
        return []
    return [part.strip() for part in value.split(",") if part.strip()]


def check_solutions_index(path: Path, solutions: dict[str, dict]) -> list[str]:
    if not path.exists():
        return [f"FAIL: {path} not found"]
    failures: list[str] = []
    lines = path.read_text(encoding="utf-8").splitlines()

    for line_no, line in enumerate(lines, start=1):
        if not line.startswith("| ["):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 8:
            failures.append(
                f"FAIL: {path}:{line_no}: malformed inventory row; expected 8 columns."
            )
            continue
        folder_match = FOLDER_RE.search(cells[1])
        if not folder_match:
            failures.append(
                f"FAIL: {path}:{line_no}: inventory row is missing a repository folder cell."
            )
            continue
        sid = folder_match.group(1)
        solution = solutions.get(sid)
        if solution is None:
            failures.append(
                f"FAIL: {path}:{line_no}: inventory row references unknown solution {sid!r}."
            )
            continue
        expected_version = f"v{solution['version']}"
        expected_controls = solution.get("controls", [])
        actual_version = cells[2]
        actual_controls = _parse_controls(cells[3])
        if actual_version != expected_version:
            failures.append(
                f"FAIL: {path}:{line_no}: {sid} inventory row version {actual_version!r} does not match lock {expected_version!r}."
            )
        if actual_controls != expected_controls:
            failures.append(
                f"FAIL: {path}:{line_no}: {sid} inventory row controls {actual_controls!r} do not match lock {expected_controls!r}."
            )

    current_folder: str | None = None
    current_heading: str | None = None
    detail_version: tuple[int, str] | None = None
    detail_status: tuple[int, str] | None = None
    detail_controls: tuple[int, list[str]] | None = None

    def finalize_detail() -> None:
        nonlocal current_folder, current_heading, detail_version, detail_status, detail_controls
        if not current_folder:
            return
        solution = solutions.get(current_folder)
        if solution is None:
            failures.append(
                f"FAIL: {path}: detail block {current_heading!r} references unknown solution {current_folder!r}."
            )
        else:
            expected_version = f"v{solution['version']}"
            if detail_version is None:
                failures.append(
                    f"FAIL: {path}: detail block {current_heading!r} is missing a version line."
                )
            elif detail_version[1] != expected_version:
                failures.append(
                    f"FAIL: {path}:{detail_version[0]}: {current_folder} detail version {detail_version[1]!r} does not match lock {expected_version!r}."
                )

            expected_controls = solution.get("controls", [])
            if detail_controls is None:
                failures.append(
                    f"FAIL: {path}: detail block {current_heading!r} is missing a primary-controls line."
                )
            elif detail_controls[1] != expected_controls:
                failures.append(
                    f"FAIL: {path}:{detail_controls[0]}: {current_folder} detail controls {detail_controls[1]!r} do not match lock {expected_controls!r}."
                )

            expected_status = solution.get("status")
            if expected_status == "preview":
                if detail_status is None:
                    failures.append(
                        f"FAIL: {path}: preview solution {current_folder!r} must include a status line in Solution Details."
                    )
                elif detail_status[1].lower() != "preview":
                    failures.append(
                        f"FAIL: {path}:{detail_status[0]}: {current_folder} detail status {detail_status[1]!r} does not match canonical 'Preview'."
                    )
            elif detail_status is not None and detail_status[1].lower() != expected_status:
                failures.append(
                    f"FAIL: {path}:{detail_status[0]}: live solution {current_folder!r} should omit the status line or use {expected_status!r}."
                )

        current_folder = None
        current_heading = None
        detail_version = None
        detail_status = None
        detail_controls = None

    in_solution_details = False
    for line_no, line in enumerate(lines, start=1):
        if line.startswith("## Solution Details"):
            in_solution_details = True
            continue
        if not in_solution_details:
            continue
        if line.startswith("## "):
            finalize_detail()
            break
        if line.startswith("### "):
            finalize_detail()
            current_heading = line[4:].strip()
            continue
        if line.startswith("- **Repository folder:**"):
            match = FOLDER_RE.search(line)
            current_folder = match.group(1) if match else None
        elif line.startswith("- **Version:**"):
            detail_version = (line_no, line.removeprefix("- **Version:**").strip())
        elif line.startswith("- **Status:**"):
            detail_status = (line_no, line.removeprefix("- **Status:**").strip())
        elif line.startswith("- **Primary controls:**"):
            detail_controls = (
                line_no,
                _parse_controls(line.removeprefix("- **Primary controls:**")),
            )
    finalize_detail()
    return failures


def check_solutions_integration(path: Path, solutions: dict[str, dict]) -> list[str]:
    if not path.exists():
        return [f"FAIL: {path} not found"]
    failures: list[str] = []
    text = path.read_text(encoding="utf-8")
    start = text.find("## Solution-to-Control Mapping")
    end = text.find("## Cross-Solution Integration Layer")
    if start == -1 or end == -1 or end <= start:
        return [
            f"FAIL: {path}: expected solution-mapping section boundaries were not found."
        ]
    section = text[start:end]
    if "**Status:**" in section:
        failures.append(
            f"FAIL: {path}: representative solution sections must not publish per-solution status lines; the canonical status source is solutions-index.md / solutions-lock.json."
        )

    blocks = re.split(r"^### ", section, flags=re.M)[1:]
    for block in blocks:
        lines = block.splitlines()
        heading = lines[0].strip()
        folder: str | None = None
        controls: list[tuple[int, str]] = []
        for offset, line in enumerate(lines[1:], start=2):
            link_match = REPO_LINK_RE.search(line)
            if link_match:
                folder = link_match.group(1)
            for cid in CONTROL_ID_RE.findall(line):
                if line.lstrip().startswith("|"):
                    controls.append((offset, cid))
        if not controls:
            continue
        if not folder:
            failures.append(
                f"FAIL: {path}: solution example {heading!r} is missing a repository link to the canonical companion solution ID."
            )
            continue
        solution = solutions.get(folder)
        if solution is None:
            failures.append(
                f"FAIL: {path}: solution example {heading!r} references unknown solution {folder!r}."
            )
            continue
        allowed = set(solution.get("controls", []))
        for _relative_line_no, cid in controls:
            if cid not in allowed:
                failures.append(
                    f"FAIL: {path}: solution example {heading!r} cites control {cid!r}, but {folder!r} canonical controls are {solution.get('controls', [])!r}."
                )
    return failures


def controls_by_id(solutions: dict[str, dict]) -> dict[str, list[str]]:
    """Reverse the lock into a control-ID -> sorted solution-ID mapping."""
    reverse: dict[str, list[str]] = {}
    for sid, body in solutions.items():
        for cid in body.get("controls", []) or []:
            reverse.setdefault(cid, []).append(sid)
    return {cid: sorted(sids) for cid, sids in reverse.items()}


def check_control_solution_sentinels(
    controls_dir: Path, solutions: dict[str, dict]
) -> list[str]:
    """Fail when a control claims no companion solution but the lock maps one.

    Deliberately narrow. A control doc is free to omit some mapped solutions and
    free to cross-reference solutions that are not mapped to it; only the direct
    contradiction against the pinned lock is treated as drift.
    """
    if not controls_dir.exists():
        return [f"FAIL: {controls_dir} not found"]
    failures: list[str] = []
    reverse = controls_by_id(solutions)

    for path in sorted(controls_dir.rglob("*.md")):
        match = CONTROL_FILE_RE.match(path.name)
        if not match:
            continue
        control_id = match.group(1)
        text = path.read_text(encoding="utf-8")
        if NO_SOLUTION_SENTINEL not in text:
            continue
        mapped = reverse.get(control_id, [])
        if mapped:
            try:
                rel = path.relative_to(REPO_ROOT).as_posix()
            except ValueError:
                rel = path.as_posix()
            failures.append(
                f"FAIL: {rel}: control {control_id} declares no companion solution, "
                f"but the pinned lock maps it to {mapped!r}."
            )
    return failures


def run_all_checks() -> tuple[int, list[str]]:
    if not LOCK_FILE.exists():
        return 1, [f"FAIL: {LOCK_FILE} not found"]
    solutions = load_lock()
    messages: list[str] = []
    messages.extend(check_solutions_index(SOLUTIONS_INDEX, solutions))
    messages.extend(check_solutions_integration(SOLUTIONS_INTEGRATION, solutions))
    messages.extend(check_control_solution_sentinels(CONTROLS_DIR, solutions))
    return len(messages), messages


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--check",
        action="store_true",
        help="CI mode: exit 1 on any failure (default exits 0).",
    )
    args = parser.parse_args(argv)

    n_failures, messages = run_all_checks()

    print("=" * 60)
    print("FSI solutions docs verification")
    print("=" * 60)
    print()

    if n_failures == 0:
        print("PASS: framework solution docs match the pinned solutions lock.")
        return 0

    for msg in messages:
        print(msg)
    print()
    print(f"FAIL: {n_failures} drift issue(s) found.")
    return 1 if args.check else 0


if __name__ == "__main__":
    sys.exit(main())
