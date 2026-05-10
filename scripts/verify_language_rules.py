"""FSI Language Rules Linter

Two-tier scanning system for prohibited FSI language phrases:

TIER 1 (Repo-wide): Phrases that violate regulatory-safe language guidelines
- "ensures compliance" / "ensure compliance"
- "guarantees" (standalone or in phrases)
- "will prevent"
- "eliminates risk" / "eliminate risk"
- "eliminates the need for" / "eliminate the need for"

TIER 2 (Examiner-facing docs): Autonomous/self-improving language
- "self-improving", "self-optimising", "self-optimizing"
- "autonomous decision-making", "autonomous decisioning"
- "without human review"
- "agent decides", "agent approves", "agent auto-approves"
- "model self-improves"
- "adaptive autonomous"

Tier 2 applies only to:
  docs/framework/**/*.md
  docs/controls/**/*.md
  docs/reference/cape-*.md
  docs/reference/microsoft-cape-crosswalk.md
  docs/reference/agentic-*.md

Files can opt out of Tier 2 checks with:
  <!-- verify-language-rules: allow-second-tier  reason: "explanation" -->

Exit codes:
  0 — no violations found
  1 — tier 1 violations found
  2 — tier 2 violations found
  3 — both tier 1 and tier 2 violations found
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

# TIER 1: Repo-wide prohibited patterns (case-insensitive)
TIER1_PATTERNS = [
    (re.compile(r"\bensures?\s+compliance\b", re.IGNORECASE), "ensures compliance"),
    (re.compile(r"\bguarantees?\b", re.IGNORECASE), "guarantees"),
    (re.compile(r"\bwill\s+prevent\b", re.IGNORECASE), "will prevent"),
    (re.compile(r"\beliminates?\s+risk\b", re.IGNORECASE), "eliminates risk"),
    (re.compile(r"\beliminates?\s+the\s+need\s+for\b", re.IGNORECASE), "eliminates the need for"),
]

# TIER 2: Examiner-facing banned phrases (case-insensitive)
# Applies only to framework/controls/reference CAPE/agentic docs
TIER2_PATTERNS = [
    (re.compile(r"\bself-improving\b", re.IGNORECASE), "self-improving"),
    (re.compile(r"\bself-optimis(ing|izing)\b", re.IGNORECASE), "self-optimising/self-optimizing"),
    (re.compile(r"\bautonomous\s+decision-making\b", re.IGNORECASE), "autonomous decision-making"),
    (re.compile(r"\bautonomous\s+decisioning\b", re.IGNORECASE), "autonomous decisioning"),
    (re.compile(r"\bwithout\s+human\s+review\b", re.IGNORECASE), "without human review"),
    (re.compile(r"\bagent\s+decides\b", re.IGNORECASE), "agent decides"),
    (re.compile(r"\bagent\s+approves\b", re.IGNORECASE), "agent approves"),
    (re.compile(r"\bagent\s+auto-approves\b", re.IGNORECASE), "agent auto-approves"),
    (re.compile(r"\bmodel\s+self-improves\b", re.IGNORECASE), "model self-improves"),
    (re.compile(r"\badaptive\s+autonomous\b", re.IGNORECASE), "adaptive autonomous"),
]

# Tier 2 scope: glob patterns for examiner-facing documents
# Note: Use separate patterns for root-level and nested files
TIER2_SCOPE_PATTERNS = [
    "docs/framework/*.md",
    "docs/framework/**/*.md",
    "docs/controls/*.md",
    "docs/controls/**/*.md",
    "docs/reference/cape-*.md",
    "docs/reference/microsoft-cape-crosswalk.md",
    "docs/reference/agentic-*.md",
]

# Exception comment pattern for tier 2 opt-out
ALLOW_SECOND_TIER_PATTERN = re.compile(
    r"<!--\s*verify-language-rules:\s*allow-second-tier\s+reason:\s*[\"'](.+?)[\"']\s*-->",
    re.IGNORECASE,
)


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


def is_tier2_scope(file_path: Path) -> bool:
    """Check if a file is in Tier 2 scope (examiner-facing documents)."""
    from pathlib import PurePosixPath

    # Convert to forward-slash path for matching
    posix_path = PurePosixPath(file_path.as_posix())

    for pattern in TIER2_SCOPE_PATTERNS:
        if posix_path.match(pattern):
            return True
    return False


def has_tier2_exception(content: str) -> str | None:
    """Check if file has Tier 2 exception comment.

    Returns the reason string if exception is found, None otherwise.
    """
    match = ALLOW_SECOND_TIER_PATTERN.search(content)
    return match.group(1) if match else None


def scan_file(file_path: Path) -> tuple[list[tuple[int, str, str, int]], str | None]:
    """Scan a single file for prohibited phrases.

    Returns:
        - List of (line_number, matched_phrase, line_text, tier) tuples
        - Tier 2 exception reason (if present), or None
    """
    violations = []
    tier2_exception_reason = None

    try:
        content = file_path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return violations, tier2_exception_reason

    # Check for Tier 2 exception
    tier2_exception_reason = has_tier2_exception(content)
    in_tier2_scope = is_tier2_scope(file_path)

    for line_num, line in enumerate(content.splitlines(), start=1):
        # Always check Tier 1 patterns (repo-wide)
        for pattern, label in TIER1_PATTERNS:
            for m in pattern.finditer(line):
                if _is_excused(line, m.start(), m.end()):
                    continue
                violations.append((line_num, label, line.strip(), 1))
                break  # one violation per pattern per line is enough

        # Check Tier 2 patterns only if in scope and no exception
        if in_tier2_scope and tier2_exception_reason is None:
            for pattern, label in TIER2_PATTERNS:
                for m in pattern.finditer(line):
                    if _is_excused(line, m.start(), m.end()):
                        continue
                    violations.append((line_num, label, line.strip(), 2))
                    break

    return violations, tier2_exception_reason


def main(file_args: list[str] | None = None) -> int:
    """Scan markdown files for prohibited FSI language.

    Args:
        file_args: Optional list of specific file paths to check.
                   If None, scans all docs/**/*.md files.
    """
    if not DOCS_DIR.exists():
        print(f"ERROR: {DOCS_DIR} directory not found")
        return 1

    # Determine which files to scan
    if file_args:
        md_files = [Path(f) for f in file_args if Path(f).suffix == ".md"]
        if not md_files:
            print("ERROR: No markdown files specified")
            return 1
    else:
        md_files = sorted(DOCS_DIR.rglob("*.md"))

    tier1_violations = 0
    tier2_violations = 0
    files_with_violations = 0
    tier2_exceptions = []

    print("=" * 60)
    print("FSI LANGUAGE RULES VALIDATION")
    print("=" * 60)
    print(f"\nScanning {len(md_files)} markdown file(s)...\n")

    for file_path in md_files:
        if not file_args and is_excluded(file_path):
            continue

        violations, tier2_exception_reason = scan_file(file_path)

        if tier2_exception_reason:
            rel_path = file_path.relative_to(Path("."))
            tier2_exceptions.append((rel_path, tier2_exception_reason))

        if violations:
            files_with_violations += 1
            rel_path = file_path.relative_to(Path("."))

            # Group violations by tier for cleaner output
            tier1_viols = [(ln, ph, txt) for ln, ph, txt, t in violations if t == 1]
            tier2_viols = [(ln, ph, txt) for ln, ph, txt, t in violations if t == 2]

            if tier1_viols:
                print(f"❌ {rel_path} [TIER 1]")
                for line_num, phrase, line_text in tier1_viols:
                    print(f"   Line {line_num}: [{phrase}]")
                    print(f"   > {line_text}")
                tier1_violations += len(tier1_viols)

            if tier2_viols:
                print(f"❌ {rel_path} [TIER 2 - Examiner-facing]")
                for line_num, phrase, line_text in tier2_viols:
                    print(f"   Line {line_num}: [{phrase}]")
                    print(f"   > {line_text}")
                    print(
                        "   Reframe using: see docs/reference/microsoft-cape-crosswalk.md "
                        "FSI Maturity Translation Table."
                    )
                    print("   (Or add allow comment if this is a Microsoft-source paraphrase page.)")
                    print()
                tier2_violations += len(tier2_viols)

    # Report Tier 2 exceptions
    if tier2_exceptions:
        print("\n" + "=" * 60)
        print("TIER 2 EXCEPTIONS (for review)")
        print("=" * 60)
        for path, reason in tier2_exceptions:
            print(f"⚠️  {path}")
            print(f"   Reason: {reason}\n")

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    total_violations = tier1_violations + tier2_violations

    if total_violations == 0:
        print("✅ No prohibited language found. All docs pass FSI language rules.")
        return 0

    # Report by tier
    if tier1_violations > 0:
        print(f"❌ TIER 1: {tier1_violations} violation(s)")
        print(
            "   Prohibited: 'ensures compliance', 'guarantees', 'will prevent', "
            "'eliminates risk', 'eliminates the need for'"
        )
        print(
            "   Use instead: 'supports compliance with', 'helps meet', "
            "'recommended to', 'aids in'\n"
        )

    if tier2_violations > 0:
        print(f"❌ TIER 2: {tier2_violations} examiner-facing violation(s)")
        print(
            "   Prohibited: 'self-improving', 'autonomous decision-making', "
            "'without human review', 'agent decides/approves', etc."
        )
        print(
            "   See docs/reference/microsoft-cape-crosswalk.md FSI Maturity "
            "Translation Table for reframing.\n"
        )

    print(f"Total: {total_violations} violation(s) in {files_with_violations} file(s).")

    # Exit code logic
    if tier1_violations > 0 and tier2_violations > 0:
        return 3  # Both tiers
    elif tier1_violations > 0:
        return 1  # Tier 1 only
    elif tier2_violations > 0:
        return 2  # Tier 2 only
    else:
        return 0


if __name__ == "__main__":
    # Parse command-line arguments for specific files
    file_args = sys.argv[1:] if len(sys.argv) > 1 else None
    sys.exit(main(file_args))
