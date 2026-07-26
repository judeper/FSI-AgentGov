#!/usr/bin/env python3
"""Verify prose count claims about solutions and regulatory coverage.

Three targeted checks (per AS9 audit fix-set):

  1. ``docs/reference/regulatory-mappings.md`` ``## Control Coverage Summary
     by Regulation`` section MUST NOT contain fractional control denominators
     (``X/NN`` patterns) outside the ``!!! warning`` admonition that explains
     why those figures were withdrawn pending SME re-validation against the
     v1.6.2 79-control catalog.

  2. ``docs/reference/solutions-index.md`` ``## Companion Inventory`` table
     row count MUST equal ``len(solutions)`` in
     ``assessment/data/solutions-lock.json`` (the canonical source).

  3. Watched prose surfaces (README, AGENTS.md, docs/index.md, etc.) MUST
     reference solution counts that agree with the lock file totals
     (live + preview = total).

Usage::

    python scripts/verify_prose_counts.py            # human-readable scan
    python scripts/verify_prose_counts.py --check    # CI mode (exit 1 on drift)

Design notes:

  * Targeted, not broad. We do NOT lint every digit on every page; we look
    for specific phrasings ("N companion solutions", "N live ... solutions",
    "N preview solutions", "(N live + N preview)", "(N companion solutions
    total)") that constitute count claims.
  * Fenced code blocks and H2 sections whose header matches "Version
    History" / "Release History" / "Changelog" are SKIPPED. Historical
    release-notes prose accurately quotes prior version counts (e.g.,
    "v1.6.0: 35 companion solutions tagged"); flagging that would block CI.
  * Admonition state in Check 1 is tracked explicitly (enter on
    ``^!!! ``; while in admonition, indented continuation lines are
    skipped; first non-indented non-empty line exits).
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

REGULATORY_FILE = REPO_ROOT / "docs" / "reference" / "regulatory-mappings.md"
SOLUTIONS_INDEX = REPO_ROOT / "docs" / "reference" / "solutions-index.md"

WATCHED_PROSE_FILES = [
    REPO_ROOT / "README.md",
    REPO_ROOT / "AGENTS.md",
    REPO_ROOT / "docs" / "index.md",
    REPO_ROOT / "docs" / "reference" / "solutions-index.md",
    REPO_ROOT / "docs" / "controls" / "CONTROL-INDEX.md",
]

# H2 sections whose nearest header matches this pattern are skipped in Check 3
# (release history accurately quotes prior version counts).
HISTORY_SECTION_RE = re.compile(
    r"(?i)(version\s+history|release\s+history|changelog|prior\s+version)"
)

# Per-file H2 skip list. These sections are validated by other means (Check 2
# for the inventory; Solution Details is descriptive prose that may legitimately
# reference patterns like "Tier 2 companion solutions" without making a count
# claim) so Check 3 must not scan them.
PER_FILE_SECTION_SKIPS: dict[Path, tuple[str, ...]] = {
    REPO_ROOT / "docs" / "reference" / "solutions-index.md": (
        "Companion Inventory",
        "Solution Details",
    ),
}

# Check 1: fractional control-count denominators (e.g., 62/72, 75/78).
# Restricted to denominators in the realistic control-catalog range so that
# legitimate regulatory citations in cell text (SOX 302/404, SEC 17a-3/4,
# FINRA 3110/2111) do NOT false-fire.
FRACTION_RE = re.compile(r"\b\d+\s*/\s*(?:7[0-9]|8[0-9])\b")

# Check 3 patterns. Order matters where alternation overlap is possible
# (longer phrasings BEFORE shorter ones so re.finditer claims them first
# and shorter regexes do not double-fire on the same span).
PROSE_PATTERNS: list[tuple[str, re.Pattern[str], str]] = [
    (
        "live_implementations",
        re.compile(
            r"\b(?P<n>\d+)\s+live\s+(?:companion\s+)?solutions?"
            r"\s+implementations?\b",
            re.IGNORECASE,
        ),
        "live",
    ),
    (
        "live_solutions",
        re.compile(
            r"\b(?P<n>\d+)\s+live\s+(?:companion\s+)?solutions?\b",
            re.IGNORECASE,
        ),
        "live",
    ),
    (
        "companion_implementations",
        re.compile(
            r"\b(?P<n>\d+)\s+companion\s+solutions?\s+implementations?\b",
            re.IGNORECASE,
        ),
        "total",
    ),
    (
        "companion_solutions",
        re.compile(
            r"\b(?P<n>\d+)\s+companion\s+solutions?\b",
            re.IGNORECASE,
        ),
        "total",
    ),
    (
        "preview_solutions",
        re.compile(
            r"\b(?P<n>\d+)\s+preview\s+solutions?\b",
            re.IGNORECASE,
        ),
        "preview",
    ),
    (
        "live_plus_preview_paren",
        re.compile(
            r"\(\s*(?P<live>\d+)\s+live\s*\+\s*(?P<preview>\d+)\s+preview\s*\)",
            re.IGNORECASE,
        ),
        "live_plus_preview",
    ),
    (
        "companion_total_paren",
        re.compile(
            r"\(\s*(?P<n>\d+)\s+companion\s+solutions?\s+total\s*\)",
            re.IGNORECASE,
        ),
        "total",
    ),
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def load_lock_counts(lock_path: Path) -> dict[str, int]:
    """Return canonical solution counts from solutions-lock.json.

    The committed lock file must consume the producer's canonical ``counts``
    block directly. We still derive totals from the per-solution ``status``
    fields as a safety check so stale or hand-edited rollups fail loudly.
    """
    data = json.loads(lock_path.read_text(encoding="utf-8"))
    counts = data.get("counts")
    required = ("total", "live", "preview")
    if not isinstance(counts, dict):
        raise ValueError("solutions-lock.json is missing the canonical 'counts' block")
    if any(not isinstance(counts.get(key), int) for key in required):
        raise ValueError(
            "solutions-lock.json counts block must contain integer total/live/preview keys"
        )

    solutions = data.get("solutions") or {}
    if isinstance(solutions, dict):
        items: Iterable[dict] = solutions.values()
    else:
        items = solutions
    derived = {"total": 0, "live": 0, "preview": 0}
    for item in items:
        derived["total"] += 1
        status = item.get("status", "")
        if status in derived:
            derived[status] += 1

    canonical = {key: int(counts[key]) for key in required}
    if canonical != derived:
        raise ValueError(
            "solutions-lock.json counts block does not match per-solution status rollups: "
            f"counts={canonical}, derived={derived}"
        )
    return canonical


def iter_lines_skipping_fences(
    text: str,
) -> Iterable[tuple[int, str, str | None]]:
    """Yield (line_number, line_text, current_h2_heading) skipping fenced
    code blocks. ``line_number`` is 1-based.
    """
    in_fence = False
    current_h2: str | None = None
    for idx, raw in enumerate(text.splitlines(), start=1):
        stripped = raw.lstrip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if raw.startswith("## "):
            current_h2 = raw[3:].strip()
        elif raw.startswith("# "):
            current_h2 = None
        yield idx, raw, current_h2


# ---------------------------------------------------------------------------
# Check 1 — regulatory mappings summary table denominator-clean
# ---------------------------------------------------------------------------


def check_regulatory_table(path: Path) -> list[str]:
    """Return a list of failure messages (empty == PASS)."""
    if not path.exists():
        return [f"FAIL: {path} not found"]
    failures: list[str] = []
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    section_start: int | None = None
    section_end: int | None = None
    for idx, line in enumerate(lines):
        if line.startswith("## Control Coverage Summary by Regulation"):
            section_start = idx + 1
        elif section_start is not None and line.startswith("## "):
            section_end = idx
            break
    if section_start is None:
        return [
            f"FAIL: {path}: section '## Control Coverage Summary by Regulation' "
            "not found",
        ]
    if section_end is None:
        section_end = len(lines)

    in_admonition = False
    for offset, line in enumerate(lines[section_start:section_end]):
        line_no = section_start + offset + 1
        # Admonition state machine.
        if line.startswith("!!! "):
            in_admonition = True
            continue
        if in_admonition:
            # Continuation lines are indented (4+ spaces) or empty.
            if line.strip() == "" or line.startswith("    "):
                continue
            in_admonition = False
        match = FRACTION_RE.search(line)
        if match:
            failures.append(
                f"FAIL: {path}:{line_no}: forbidden fractional control "
                f"denominator {match.group(0)!r} in summary section "
                "(numbers were withdrawn pending SME re-validation; "
                "edit the warning admonition rather than re-introducing "
                "fractions in table cells)"
            )
    return failures


# ---------------------------------------------------------------------------
# Check 2 — solutions inventory table row count == lock file count
# ---------------------------------------------------------------------------


def check_inventory_row_count(
    path: Path, expected_total: int
) -> list[str]:
    """Return a list of failure messages (empty == PASS)."""
    if not path.exists():
        return [f"FAIL: {path} not found"]
    failures: list[str] = []
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    section_start: int | None = None
    section_end: int | None = None
    for idx, line in enumerate(lines):
        if line.startswith("## Companion Inventory"):
            section_start = idx + 1
        elif section_start is not None and line.startswith("## "):
            section_end = idx
            break
    if section_start is None:
        return [
            f"FAIL: {path}: section '## Companion Inventory' not found",
        ]
    if section_end is None:
        section_end = len(lines)
    rows = 0
    for line in lines[section_start:section_end]:
        # Inventory data rows start with "| [" (link to anchor).
        if line.startswith("| ["):
            rows += 1
    if rows != expected_total:
        failures.append(
            f"FAIL: {path}: '## Companion Inventory' table has {rows} data "
            f"rows; assessment/data/solutions-lock.json has "
            f"{expected_total} solutions. Add or remove an inventory row "
            "to match the lock file (the lock file is canonical)."
        )
    return failures


# ---------------------------------------------------------------------------
# Check 3 — prose count claims agree with lock file totals
# ---------------------------------------------------------------------------


def check_prose_counts(
    files: Iterable[Path], counts: dict[str, int]
) -> list[str]:
    """Return a list of failure messages (empty == PASS)."""
    failures: list[str] = []
    canonical_phrase = (
        f"\"{counts['total']} companion solutions "
        f"({counts['live']} live + {counts['preview']} preview)\""
    )
    for path in files:
        if not path.exists():
            failures.append(f"FAIL: watched file {path} not found")
            continue
        text = path.read_text(encoding="utf-8")
        section_skips = PER_FILE_SECTION_SKIPS.get(path, ())
        for line_no, line, h2 in iter_lines_skipping_fences(text):
            if h2 and HISTORY_SECTION_RE.search(h2):
                continue
            if h2 and any(skip in h2 for skip in section_skips):
                continue
            consumed: list[tuple[int, int]] = []
            for _label, regex, kind in PROSE_PATTERNS:
                for match in regex.finditer(line):
                    span = match.span()
                    if any(s <= span[0] < e for s, e in consumed):
                        continue
                    consumed.append(span)
                    if kind == "live_plus_preview":
                        live_n = int(match.group("live"))
                        prev_n = int(match.group("preview"))
                        if live_n != counts["live"]:
                            failures.append(
                                _diag(
                                    path, line_no, line, match.group(0),
                                    f"parenthetical claims {live_n} live "
                                    f"but lock file has {counts['live']}",
                                    canonical_phrase,
                                )
                            )
                        if prev_n != counts["preview"]:
                            failures.append(
                                _diag(
                                    path, line_no, line, match.group(0),
                                    f"parenthetical claims {prev_n} preview "
                                    f"but lock file has {counts['preview']}",
                                    canonical_phrase,
                                )
                            )
                    else:
                        actual = int(match.group("n"))
                        expected = counts[kind]
                        if actual != expected:
                            failures.append(
                                _diag(
                                    path, line_no, line, match.group(0),
                                    f"prose claims {actual} {kind} but lock "
                                    f"file has {expected}",
                                    canonical_phrase,
                                )
                            )
    return failures


def _diag(
    path: Path,
    line_no: int,
    line: str,
    matched: str,
    why: str,
    canonical: str,
) -> str:
    rel = path.relative_to(REPO_ROOT) if path.is_absolute() else path
    snippet = line.strip()
    if len(snippet) > 140:
        snippet = snippet[:137] + "..."
    return (
        f"FAIL: {rel}:{line_no}: {why}.\n"
        f"      matched: {matched!r}\n"
        f"      line:    {snippet}\n"
        f"      suggested canonical phrasing: {canonical}"
    )


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def run_all_checks() -> tuple[int, list[str], dict[str, int]]:
    """Run all three checks. Return (failure_count, messages, lock_counts)."""
    if not LOCK_FILE.exists():
        return 1, [f"FAIL: {LOCK_FILE} not found"], {}
    messages: list[str] = []
    try:
        counts = load_lock_counts(LOCK_FILE)
    except ValueError as exc:
        return 1, [f"FAIL: {exc}"], {}
    messages.extend(check_regulatory_table(REGULATORY_FILE))
    messages.extend(
        check_inventory_row_count(SOLUTIONS_INDEX, counts["total"])
    )
    messages.extend(check_prose_counts(WATCHED_PROSE_FILES, counts))
    return len(messages), messages, counts


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--check",
        action="store_true",
        help="CI mode: exit 1 on any failure (default exits 0).",
    )
    args = parser.parse_args(argv)

    n_failures, messages, counts = run_all_checks()

    print("=" * 60)
    print("FSI prose counts verification")
    print("=" * 60)
    if counts:
        print(
            f"Lock file totals: {counts['total']} companion "
            f"({counts['live']} live + {counts['preview']} preview)"
        )
    print(f"Files scanned (Check 3): {len(WATCHED_PROSE_FILES)}")
    print()

    if n_failures == 0:
        print("PASS: all prose count claims agree with canonical sources.")
        return 0

    for msg in messages:
        print(msg)
    print()
    print(f"FAIL: {n_failures} drift issue(s) found.")
    return 1 if args.check else 0


if __name__ == "__main__":
    sys.exit(main())
