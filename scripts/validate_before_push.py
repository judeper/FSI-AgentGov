#!/usr/bin/env python3
"""
Pre-push validation script for FSI Agent Governance Framework.

Run this script before pushing to ensure all validations pass:
    python scripts/validate_before_push.py

This script runs:
1. Language rules validation (prohibited phrases in docs)
2. Version consistency check (all tracked files show same version)
3. Control file structure validation
4. Assessment data extraction + URL validation
5. MkDocs build --strict (checks for broken internal links)
6. External link check (optional - requires npm markdown-link-check)

Exit codes:
    0 = All checks passed
    1 = One or more checks failed
"""

import re
import subprocess
import sys
from pathlib import Path

# Fix Unicode encoding issues on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Colors for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"
BOLD = "\033[1m"

# Files that must all contain the same framework version number
VERSION_FILES = [
    (".github/copilot-instructions.md", r"Framework v(\d+\.\d+\.\d+)"),
    ("AGENTS.md", r"Framework v(\d+\.\d+\.\d+)"),
    ("docs/index.md", r"\*\*Version:\*\*\s*(\d+\.\d+\.\d+)"),
    ("docs/framework/index.md", r"Framework Version:\*\*\s*(\d+\.\d+\.\d+)"),
]


def run_command(cmd: list[str], description: str, cwd: Path | None = None) -> bool:
    """Run a command and return True if it succeeds."""
    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}Running: {description}{RESET}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")

    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=False,
            text=True,
        )
        if result.returncode == 0:
            print(f"{GREEN}✓ {description} passed{RESET}")
            return True
        else:
            print(f"{RED}✗ {description} failed (exit code: {result.returncode}){RESET}")
            return False
    except FileNotFoundError:
        print(f"{YELLOW}⚠ {description} skipped (command not found){RESET}")
        return True  # Don't fail if tool isn't installed


def check_version_consistency(repo_root: Path) -> bool:
    """Check that all tracked files report the same framework version."""
    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}Running: Version consistency check{RESET}")
    print(f"{'='*60}")

    versions: dict[str, str] = {}
    for rel_path, pattern in VERSION_FILES:
        full_path = repo_root / rel_path
        if not full_path.exists():
            print(f"  {YELLOW}⚠ {rel_path} not found, skipping{RESET}")
            continue
        content = full_path.read_text(encoding="utf-8")
        match = re.search(pattern, content)
        if match:
            versions[rel_path] = match.group(1)
        else:
            print(f"  {YELLOW}⚠ {rel_path}: version pattern not found{RESET}")

    if not versions:
        print(f"  {YELLOW}⚠ No version numbers found, skipping{RESET}")
        return True

    unique = set(versions.values())
    if len(unique) == 1:
        ver = unique.pop()
        print(f"  All {len(versions)} files report v{ver}")
        print(f"{GREEN}✓ Version consistency check passed{RESET}")
        return True
    else:
        print(f"  {RED}Version mismatch detected:{RESET}")
        for path, ver in sorted(versions.items()):
            print(f"    {path}: v{ver}")
        print(f"{RED}✗ Version consistency check failed{RESET}")
        return False


def main():
    """Run all pre-push validations."""
    repo_root = Path(__file__).parent.parent

    print(f"{BOLD}")
    print("=" * 60)
    print("  FSI Agent Governance Framework - Pre-Push Validation")
    print("=" * 60)
    print(f"{RESET}")

    checks = []

    # 1. Language rules (fast — catches prohibited phrases before slow builds)
    checks.append(run_command(
        [sys.executable, "scripts/verify_language_rules.py"],
        "Language rules validation",
        cwd=repo_root
    ))

    # 2. Version consistency (fast — catches forgotten version bumps)
    checks.append(check_version_consistency(repo_root))

    # 3. Control file validation
    checks.append(run_command(
        [sys.executable, "scripts/verify_controls.py"],
        "Control file structure validation",
        cwd=repo_root
    ))

    # 4. Assessment data extraction + URL validation
    checks.append(run_command(
        [sys.executable, "scripts/extract_assessment_data.py"],
        "Assessment data extraction + URL validation",
        cwd=repo_root
    ))

    # 5. MkDocs build (checks internal links and markdown syntax)
    checks.append(run_command(
        ["mkdocs", "build", "--strict"],
        "MkDocs build (internal links + markdown)",
        cwd=repo_root
    ))

    # 6. External link validation (optional - requires npm package)
    # Check a sample of files to avoid timeout (full check runs in CI)
    sample_files = [
        "docs/controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md",
        "docs/controls/pillar-2-management/2.1-managed-environments.md",
        "docs/reference/regulatory-mappings.md",
    ]

    existing_files = [f for f in sample_files if (repo_root / f).exists()]

    if existing_files:
        for file in existing_files[:2]:  # Check first 2 files as sample
            checks.append(run_command(
                ["npx", "markdown-link-check", file, "--config", ".github/workflows/mlc-config.json"],
                f"External link check: {Path(file).name}",
                cwd=repo_root
            ))

    # Summary
    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}SUMMARY{RESET}")
    print(f"{'='*60}")

    passed = sum(checks)
    total = len(checks)

    if passed == total:
        print(f"{GREEN}✓ All {total} checks passed!{RESET}")
        print(f"\n{GREEN}Safe to push.{RESET}")
        return 0
    else:
        print(f"{RED}✗ {total - passed} of {total} checks failed{RESET}")
        print(f"\n{RED}Fix issues before pushing.{RESET}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
