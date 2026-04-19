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


def _is_excused(line: str, match_start: int, match_end: int) -> bool:
    """Return True if the prohibited match should be excused.

    Excuses:
    - Quoted/code-fenced occurrences (single-line `…`, "…", or *…*) — the
      surrounding markup typically signals an explanatory mention, not a
      regulatory claim.
    - Negation context: 'not', 'do not', 'does not', 'cannot', 'rather than',
      'instead of', 'never' appearing within 50 chars before the match.
    - Lines that are teaching about prohibited language (contain 'prohibited',
      'do not use', 'do not say', 'avoid', 'hedged', 'reminder', or list
      multiple banned phrases together).
    """
    matched = line[match_start:match_end]
    before = line[:match_start]

    # Inside backticks/quotes/asterisks (single-line)
    for delim in ("`", '"', "*"):
        # Count delims before match position; if odd → currently open
        if before.count(delim) % 2 == 1:
            return True

    # Negation in the preceding 80 chars (strip markdown emphasis first)
    window = before[-80:].lower()
    window_clean = window.replace("**", "").replace("*", "").replace("__", "").replace("_", " ")
    negations = (" not ", "cannot", "rather than", "instead of",
                 "never ", "without ", "doesn't", "don't", "do not", "does not",
                 "did not", "would not", "will not", "may not", "shall not",
                 "stop", "tempted to", "no by itself", "not by itself",
                 "no longer", "nothing", "constitutes legal", "constitutes a",
                 "constitute a", "produce a legal", "or a guarantee")
    if any(neg in window_clean for neg in negations):
        return True

    # Technical (non-regulatory) senses of 'guarantee(s)': transactional,
    # persistence, durability, hashing, idempotency, atomicity.
    if "guarantee" in matched.lower():
        tech_markers = ("transactional", "persistence", "durability", "hashing",
                        "idempotenc", "atomicity", "delivery guarantee",
                        "ordering guarantee", "consistency guarantee")
        if any(t in line.lower() for t in tech_markers):
            return True

    # Also check the rest-of-line for "not " near the match (within ~30 chars after)
    after = line[match_end:match_end+40].lower()
    after_clean = after.replace("**","").replace("*","")
    if " not " in after_clean[:20] or after_clean.startswith(" not "):
        return True

    # Teaching/reminder lines
    line_lower = line.lower()
    teaching_markers = ("prohibited", "do not use", "do not say", "do not write",
                        "avoid the phrase", "avoid using", "hedged language",
                        "language reminder", "regulatory hedging", "reminder:",
                        "use instead", "in place of", "❌", "implies a legal")
    if any(t in line_lower for t in teaching_markers):
        return True

    # Lines that enumerate multiple banned phrases (clearly a teaching list)
    banned_words = ("ensure", "guarantee", "prevent", "eliminate")
    if sum(1 for w in banned_words if w in line_lower) >= 3:
        return True

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
            for m in pattern.finditer(line):
                if _is_excused(line, m.start(), m.end()):
                    continue
                violations.append((line_num, label, line.strip()))
                break  # one violation per pattern per line is enough
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
