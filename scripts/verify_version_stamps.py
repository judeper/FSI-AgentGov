#!/usr/bin/env python3
"""Verify framework version stamps across canonical surface files.

Scope (PR-0, Tier -1 foundation gate):
    Catch drift in *footer / metadata stamps* — NOT body text. Historical
    narrative such as "Earlier in v1.5.0 we shipped..." is intentional and
    must never trip this check.

Canonical version source:
    Repo-root ``VERSION`` file (single line, e.g. ``1.6.2``). The MkDocs
    cache-bust hook (``overrides/hooks/cache_bust.py``) also reads this file
    and embeds the value into ``docs/version.json`` at build time so the
    deployed site exposes the canonical version alongside the build SHA.

What this script enforces:
    Each entry in ``CHECKS`` below is a (path, regex, label) triple. The
    regex MUST match exactly one place in the file (the footer/header stamp)
    and is anchored so body prose is not scanned. The captured group is the
    version literal; if it does not equal the canonical version, the file
    is reported as drifted.

What this script DOES NOT enforce:
    The ``_ACCEPTED_VERSION`` allowlist in ``scripts/verify_controls.py``
    legitimately permits historical narrative across many control bodies.
    That is intentional and out of scope here.

Modes:
    default       Scan and print a report. Exit 0 regardless of drift.
    --check       Same scan; exit 1 if any non-allowlisted file is drifted.

Allowlist:
    ``_KNOWN_DRIFT_ALLOWLIST`` grandfathers files that were already drifted
    when this gate was introduced (PR-0). They are tracked for fix-up in
    PR-A (Tier 0A scorched-earth version-stamp audit). The allowlist must
    shrink to empty as PR-A lands; the script reports any allowlisted file
    that is no longer drifted so stale entries are removed.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
VERSION_FILE = REPO_ROOT / "VERSION"


def read_canonical_version() -> str:
    if not VERSION_FILE.exists():
        sys.stderr.write(
            f"ERROR: canonical VERSION file not found at {VERSION_FILE}\n"
        )
        sys.exit(2)
    raw = VERSION_FILE.read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"\d+\.\d+(\.\d+)?", raw):
        sys.stderr.write(
            f"ERROR: VERSION file content {raw!r} is not a valid semver-ish "
            "literal (expected e.g. 1.6.2)\n"
        )
        sys.exit(2)
    return raw


# Each check is: (relative_path, compiled_regex_with_one_capture_group, human_label)
# Regexes are deliberately anchored so they only match footer/header stamps,
# never body prose.
CHECKS: list[tuple[str, re.Pattern[str], str]] = [
    (
        "README.md",
        re.compile(r"^# FSI Agent Governance Framework v(\d+\.\d+(?:\.\d+)?)\b", re.M),
        "README H1",
    ),
    (
        "DISCLAIMER.md",
        re.compile(
            r"^\*FSI Agent Governance Framework v(\d+\.\d+(?:\.\d+)?)\b.*\*\s*$",
            re.M,
        ),
        "Root DISCLAIMER footer",
    ),
    (
        "docs/disclaimer.md",
        re.compile(
            r"^\*FSI Agent Governance Framework v(\d+\.\d+(?:\.\d+)?)\b.*\*\s*$",
            re.M,
        ),
        "docs/disclaimer footer",
    ),
]

# Glob-based check: every framework doc footer "*Updated: ... | Version: vX.Y.Z ..."
FRAMEWORK_FOOTER_RE = re.compile(
    r"^\*Updated:\s+[^|]+\|\s+Version:\s+v(\d+\.\d+(?:\.\d+)?)\b.*\*\s*$",
    re.M,
)
FRAMEWORK_GLOB = "docs/framework/*.md"


# Files that were drifted at the time this gate was introduced (PR-0).
# All originally allowlisted entries were fixed in PR-A (Tier 0A
# scorched-earth version-stamp audit). Allowlist is intentionally empty —
# any future drift becomes a blocking CI failure. Add a new entry only with
# an inline comment explaining why the drift is permanent.
_KNOWN_DRIFT_ALLOWLIST: set[str] = set()


class Result:
    def __init__(self, path: str, label: str, found: str | None, expected: str):
        self.path = path
        self.label = label
        self.found = found
        self.expected = expected

    @property
    def status(self) -> str:
        if self.found is None:
            return "NO-MATCH"
        return "OK" if self.found == self.expected else "DRIFT"


def scan_file(path: Path, regex: re.Pattern[str]) -> str | None:
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8")
    matches = regex.findall(text)
    if not matches:
        return None
    # Use the first match. All anchored regexes here target a single
    # canonical footer/header line so multiple matches indicate a problem
    # but we still return the first for reporting.
    first = matches[0]
    return first if isinstance(first, str) else first[0]


def collect_results(canonical: str) -> list[Result]:
    results: list[Result] = []
    for rel_path, regex, label in CHECKS:
        path = REPO_ROOT / rel_path
        found = scan_file(path, regex)
        results.append(Result(rel_path, label, found, canonical))

    for path in sorted(REPO_ROOT.glob(FRAMEWORK_GLOB)):
        rel = path.relative_to(REPO_ROOT).as_posix()
        found = scan_file(path, FRAMEWORK_FOOTER_RE)
        if found is None:
            # Not every framework doc has a "*Updated: ... | Version: ..." footer.
            # Skip silently — this scanner only enforces files that *do* stamp
            # a version in the canonical footer format.
            continue
        results.append(Result(rel, "framework footer", found, canonical))
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit 1 on non-allowlisted drift (CI mode). Default reports only.",
    )
    args = parser.parse_args()

    canonical = read_canonical_version()
    results = collect_results(canonical)

    drifted: list[Result] = []
    no_match: list[Result] = []
    ok: list[Result] = []
    for r in results:
        if r.status == "DRIFT":
            drifted.append(r)
        elif r.status == "NO-MATCH":
            no_match.append(r)
        else:
            ok.append(r)

    print(f"Canonical version (from VERSION): {canonical}")
    print(f"Files scanned: {len(results)}")
    print(f"  OK:    {len(ok)}")
    print(f"  DRIFT: {len(drifted)}")
    print(f"  NO-MATCH (footer absent): {len(no_match)}")
    print()

    if drifted:
        print("DRIFT detected (file → found / expected):")
        for r in drifted:
            tag = "  [allowlisted]" if r.path in _KNOWN_DRIFT_ALLOWLIST else "  [BLOCKING] "
            print(f"{tag} {r.path:60s} {r.found} → {r.expected}    ({r.label})")
        print()

    # Stale allowlist entries: file no longer drifted but still allowlisted.
    drifted_paths = {r.path for r in drifted}
    stale_entries = sorted(p for p in _KNOWN_DRIFT_ALLOWLIST if p not in drifted_paths)
    if stale_entries:
        print(
            "STALE allowlist entries (file is no longer drifted; remove from "
            "_KNOWN_DRIFT_ALLOWLIST):"
        )
        for p in stale_entries:
            print(f"  - {p}")
        print()

    blocking = [r for r in drifted if r.path not in _KNOWN_DRIFT_ALLOWLIST]

    if args.check:
        if blocking:
            print(
                f"FAIL: {len(blocking)} file(s) drifted from canonical "
                f"version {canonical} and are not allowlisted."
            )
            return 1
        if stale_entries:
            print(
                f"FAIL: {len(stale_entries)} stale allowlist entr(y/ies) "
                "must be removed from _KNOWN_DRIFT_ALLOWLIST."
            )
            return 1
        print("PASS: no non-allowlisted version-stamp drift detected.")
        return 0

    # Default mode: report only.
    print("(report-only mode; pass --check for CI gating)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
