"""Commercial-Cloud Scope Linter  (COMMON RULE — identical across all four FSI repos)

Purpose
-------
These frameworks/solutions are scoped to **US commercial-cloud Microsoft 365 only**.
Government / sovereign clouds (GCC, GCC High, DoD, Azure Government, and other
sovereign clouds) are intentionally **out of scope** so the team does not carry the
ongoing burden of tracking gov-cloud feature parity and availability.

This linter fails CI if forward-facing content (documentation + published assessment
data) introduces government/sovereign-cloud guidance. It does NOT scan functional code
or inert historical records (changelogs, monitoring reports, fixtures, state files).

The single canonical place that is *allowed* to name these terms is the scope
disclaimer (see commercial-scope.instructions.md), plus any file that carries an
explicit, reasoned opt-out marker:

    <!-- commercial-scope: allow reason: "why this mention is legitimate" -->

Exit codes:
  0 — clean (no government/sovereign-cloud content in forward-facing files)
  1 — violations found

Usage:
  python scripts/verify_commercial_scope.py            # scan repo from CWD
  python scripts/verify_commercial_scope.py --root DIR # scan a specific root
  python scripts/verify_commercial_scope.py FILE...    # scan specific files (CI on changed files)
  python scripts/verify_commercial_scope.py --list     # list scannable files and exit
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path, PurePosixPath

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# --------------------------------------------------------------------------- #
# Banned government / sovereign-cloud patterns (case-insensitive unless noted)
# --------------------------------------------------------------------------- #
BANNED_PATTERNS = [
    (re.compile(r"\bGCC\s*High\b", re.IGNORECASE), "GCC High"),
    (re.compile(r"\bGCC\b", re.IGNORECASE), "GCC"),
    (re.compile(r"\bDoD\b"), "DoD"),  # case-sensitive: avoids matching inside other words
    (re.compile(r"\bsovereign\b", re.IGNORECASE), "sovereign (cloud)"),
    (re.compile(r"\bgovernment\s+cloud(s)?\b", re.IGNORECASE), "government cloud"),
    (re.compile(r"\bGovCloud\b", re.IGNORECASE), "GovCloud"),
    (re.compile(r"\bAzure\s+Government\b", re.IGNORECASE), "Azure Government"),
    (re.compile(r"\bpurview\.microsoft\.us\b", re.IGNORECASE), "purview.microsoft.us (gov endpoint)"),
    (re.compile(r"\b[\w.-]+\.(?:office365|microsoftonline)\.us\b", re.IGNORECASE),
     "US-gov cloud endpoint"),
]

# Only these content types are scanned. Functional code (.ps1/.py/.psm1/.js) is NOT
# scanned — gov-endpoint handling in code is functionality, not tracked guidance.
SCANNED_EXTENSIONS = {".md", ".json"}

# Path segments (any depth) that mark inert/historical/non-published content — skipped.
EXCLUDED_DIR_SEGMENTS = {
    ".git", ".github", "node_modules", "__pycache__", ".squad",
    "site",            # mkdocs build output
    "reports",         # monitoring / learn-change logs (factual history)
    "releases",        # changelog archives
    "templates",       # scaffolding templates may carry placeholder enums
    "tests", "test", "fixtures", "__fixtures__",
    "research",        # internal working notes, not published guidance
    "artifacts-review",
    "orchestration-log",
}

# Filename globs that are inert/historical — skipped.
EXCLUDED_FILE_GLOBS = [
    "CHANGELOG*", "*.migrated", "*.backup",
    "monitor-state*.json", "*-lock.json", "package-lock.json",
    "*.schema.json",   # schema enums legitimately enumerate residency values
]

# Specific files allowed to NAME the banned terms (the canonical disclaimer + this rule).
EXCLUDED_BASENAMES = {
    "commercial-scope.instructions.md",
    "verify_commercial_scope.py",
    "SCOPE.md",
    "disclaimer.md",
}

OPT_OUT = re.compile(
    r"<!--\s*commercial-scope:\s*allow\s+reason:\s*[\"'](.+?)[\"']\s*-->",
    re.IGNORECASE,
)


def _has_excluded_segment(path: PurePosixPath) -> bool:
    return any(seg in EXCLUDED_DIR_SEGMENTS for seg in path.parts)


def _matches_excluded_glob(path: PurePosixPath) -> bool:
    name = path.name
    return any(path.match(g) or PurePosixPath(name).match(g) for g in EXCLUDED_FILE_GLOBS)


def is_scannable(path: Path, root: Path) -> bool:
    if path.suffix.lower() not in SCANNED_EXTENSIONS:
        return False
    if path.name in EXCLUDED_BASENAMES:
        return False
    rel = PurePosixPath(path.relative_to(root).as_posix())
    if _has_excluded_segment(rel):
        return False
    if _matches_excluded_glob(rel):
        return False
    return True


def _git_tracked_files(root: Path) -> list[Path] | None:
    """Return committed (tracked) files, or None if not a git repo / git unavailable.

    Gating tracked files only is the correct CI semantic: we enforce on what is
    committed, and git-ignored build artifacts (e.g. a generated assessment-data.json)
    never cause false positives.
    """
    import subprocess
    try:
        res = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-z"],
            capture_output=True, check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    names = res.stdout.decode("utf-8", "replace").split("\0")
    return [root / n for n in names if n]


def iter_files(root: Path, file_args: list[str] | None) -> list[Path]:
    if file_args:
        out = []
        for f in file_args:
            p = Path(f)
            if p.suffix.lower() in SCANNED_EXTENSIONS and p.exists():
                out.append(p.resolve())
        return out
    tracked = _git_tracked_files(root)
    if tracked is not None:
        return sorted(p for p in tracked if p.is_file() and is_scannable(p, root))
    return sorted(p for p in root.rglob("*") if p.is_file() and is_scannable(p, root))


def scan_file(path: Path) -> tuple[list[tuple[int, str, str]], str | None]:
    try:
        content = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return [], None
    opt = OPT_OUT.search(content)
    if opt:
        return [], opt.group(1)
    violations: list[tuple[int, str, str]] = []
    for n, line in enumerate(content.splitlines(), start=1):
        for pattern, label in BANNED_PATTERNS:
            if pattern.search(line):
                violations.append((n, label, line.strip()[:160]))
                break
    return violations, None


def main() -> int:
    ap = argparse.ArgumentParser(description="Commercial-cloud scope linter")
    ap.add_argument("--root", default=".", help="repo root to scan (default: CWD)")
    ap.add_argument("--list", action="store_true", help="list scannable files and exit")
    ap.add_argument("files", nargs="*", help="specific files to scan (optional)")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    files = iter_files(root, args.files or None)

    if args.list:
        for f in files:
            print(f.relative_to(root) if f.is_relative_to(root) else f)
        print(f"\n{len(files)} scannable file(s).")
        return 0

    print("=" * 64)
    print("COMMERCIAL-CLOUD SCOPE VALIDATION (no GCC / GCC High / DoD / sovereign)")
    print("=" * 64)
    print(f"\nScanning {len(files)} forward-facing file(s) under {root}...\n")

    total = 0
    files_hit = 0
    opt_outs: list[tuple[Path, str]] = []
    for path in files:
        violations, opt_reason = scan_file(path)
        if opt_reason:
            opt_outs.append((path, opt_reason))
            continue
        if violations:
            files_hit += 1
            rel = path.relative_to(root) if path.is_relative_to(root) else path
            print(f"\u274c {rel}")
            for ln, label, text in violations:
                print(f"   Line {ln}: [{label}]")
                print(f"   > {text}")
            total += len(violations)

    if opt_outs:
        print("\n" + "-" * 64)
        print("OPT-OUTS (allowed mentions, for review)")
        for path, reason in opt_outs:
            rel = path.relative_to(root) if path.is_relative_to(root) else path
            print(f"\u26a0\ufe0f  {rel}  —  {reason}")

    print("\n" + "=" * 64)
    if total == 0:
        print("\u2705 No government/sovereign-cloud content in forward-facing files.")
        return 0
    print(f"\u274c {total} government/sovereign-cloud mention(s) in {files_hit} file(s).")
    print("   Policy: these repos are US commercial-cloud M365 only. Remove the")
    print("   gov-cloud guidance, or (if a mention is genuinely required) add:")
    print('   <!-- commercial-scope: allow reason: "..." -->')
    return 1


if __name__ == "__main__":
    sys.exit(main())
