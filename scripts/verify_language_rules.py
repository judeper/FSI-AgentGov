"""FSI Language Rules Linter

Scans docs/**/*.md for prohibited FSI language phrases that violate
regulatory-safe language guidelines.

Prohibited phrases:
- "ensures compliance" / "ensure compliance"
- "guarantees" (standalone or in phrases)
- "will prevent"
- "eliminates risk" / "eliminate risk"
- "eliminates the need for" / "eliminate the need for"

Exit codes:
  0 — no violations found
  1 — one or more violations found
"""

import re
import sys
from pathlib import Path

# Fix Unicode encoding issues on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

DOCS_DIR = Path("docs")

# Directories/files to exclude from scanning
EXCLUDED_DIRS = {
    DOCS_DIR / "templates",
}

EXCLUDED_FILES = {
    DOCS_DIR / "disclaimer.md",
}

# Compiled patterns for prohibited phrases (case-insensitive)
PROHIBITED_PATTERNS = [
    (re.compile(r"\bensures?\s+compliance\b", re.IGNORECASE), "ensures compliance"),
    (re.compile(r"\bguarantees?\b", re.IGNORECASE), "guarantees"),
    (re.compile(r"\bwill\s+prevent\b", re.IGNORECASE), "will prevent"),
    (re.compile(r"\beliminates?\s+risk\b", re.IGNORECASE), "eliminates risk"),
    (re.compile(r"\beliminates?\s+the\s+need\s+for\b", re.IGNORECASE), "eliminates the need for"),
]


def is_excluded(file_path: Path) -> bool:
    """Check if a file is in an excluded directory or is an excluded file."""
    if file_path in EXCLUDED_FILES:
        return True
    for excluded in EXCLUDED_DIRS:
        try:
            file_path.relative_to(excluded)
            return True
        except ValueError:
            continue
    return False


def scan_file(file_path: Path) -> list[tuple[int, str, str]]:
    """Scan a single file for prohibited phrases.

    Returns list of (line_number, matched_phrase, line_text) tuples.
    """
    violations = []
    try:
        content = file_path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return violations

    for line_num, line in enumerate(content.splitlines(), start=1):
        for pattern, label in PROHIBITED_PATTERNS:
            if pattern.search(line):
                violations.append((line_num, label, line.strip()))
    return violations


def main() -> int:
    """Scan all docs/**/*.md files for prohibited FSI language."""
    if not DOCS_DIR.exists():
        print(f"ERROR: {DOCS_DIR} directory not found")
        return 1

    md_files = sorted(DOCS_DIR.rglob("*.md"))
    total_violations = 0
    files_with_violations = 0

    print("=" * 60)
    print("FSI LANGUAGE RULES VALIDATION")
    print("=" * 60)
    print(f"\nScanning {len(md_files)} markdown files in {DOCS_DIR}/\n")

    for file_path in md_files:
        if is_excluded(file_path):
            continue

        violations = scan_file(file_path)
        if violations:
            files_with_violations += 1
            rel_path = file_path.relative_to(Path("."))
            print(f"❌ {rel_path}")
            for line_num, phrase, line_text in violations:
                print(f"   Line {line_num}: [{phrase}] {line_text}")
            total_violations += len(violations)

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    if total_violations == 0:
        print("✅ No prohibited language found. All docs pass FSI language rules.")
        return 0
    else:
        print(
            f"❌ {total_violations} violation(s) in {files_with_violations} file(s)."
        )
        print(
            "\nProhibited phrases: 'ensures compliance', 'guarantees', "
            "'will prevent', 'eliminates risk', 'eliminates the need for'"
        )
        print(
            "Use instead: 'supports compliance with', 'helps meet', "
            "'recommended to', 'aids in'"
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
