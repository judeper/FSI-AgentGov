"""Fix small systemic grammar defects in control docs.

Currently targets a known repeated-verb defect introduced by automation:
- "- Apply apply ..." -> "- Apply ..."

This script is intentionally narrow to avoid unintended content edits.
"""

from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTROLS_ROOT = REPO_ROOT / "docs" / "reference"


def iter_control_files() -> list[Path]:
    return sorted(CONTROLS_ROOT.rglob("*.md"))


def fix_apply_apply(text: str) -> tuple[str, int]:
    # Only rewrite the specific bullet prefix to be safe.
    pattern = re.compile(r"^(\s*-\s+Apply)\s+apply\b", re.IGNORECASE | re.MULTILINE)
    new_text, count = pattern.subn(r"\1", text)
    return new_text, count


def main() -> int:
    updated_files = 0
    total_fixes = 0

    for path in iter_control_files():
        original = path.read_text(encoding="utf-8")
        updated, count = fix_apply_apply(original)
        if count:
            path.write_text(updated, encoding="utf-8", newline="\n")
            updated_files += 1
            total_fixes += count

    print(f"Done. Updated {updated_files} file(s); fixed {total_fixes} occurrence(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
