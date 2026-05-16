#!/usr/bin/env python3
"""Verify that the prose URL counts in microsoft-learn-urls.md match reality.

The file ``docs/reference/microsoft-learn-urls.md`` declares its total
``learn.microsoft.com`` URL count in two places:

* **Header** — ``**Total URLs Tracked:** ~N``
* **Footer** — ``*Total URLs Tracked: ~N*``

This script counts the actual occurrences, extracts both prose numbers, and
fails (exit 1) if:

* Either prose number drifts more than 5 from the actual count, OR
* The two prose numbers disagree with each other.

Run with ``--check`` for CI parity with sibling verifier scripts.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
URLS_FILE = REPO_ROOT / "docs" / "reference" / "microsoft-learn-urls.md"

LEARN_URL_PATTERN = re.compile(r"https://learn\.microsoft\.com", re.IGNORECASE)
HEADER_RE = re.compile(r"\*\*Total URLs Tracked:\*\*\s*~(\d+)")
FOOTER_RE = re.compile(r"\*Total URLs Tracked:\s*~(\d+)\*")

TOLERANCE = 5


def count_urls(text: str) -> int:
    return len(LEARN_URL_PATTERN.findall(text))


def parse_header_count(text: str) -> int | None:
    m = HEADER_RE.search(text)
    return int(m.group(1)) if m else None


def parse_footer_count(text: str) -> int | None:
    m = FOOTER_RE.search(text)
    return int(m.group(1)) if m else None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit non-zero on drift (default behavior; flag kept for CI parity).",
    )
    parser.parse_args(argv)

    if not URLS_FILE.exists():
        print(f"FAIL: expected file not found: {URLS_FILE}")
        return 1

    text = URLS_FILE.read_text(encoding="utf-8")
    actual = count_urls(text)
    header_n = parse_header_count(text)
    footer_n = parse_footer_count(text)

    print(f"Actual learn.microsoft.com URL count : {actual}")
    print(f"Header prose count (** … **)         : {header_n}")
    print(f"Footer prose count (* … *)           : {footer_n}")
    print()

    failures: list[str] = []

    if header_n is None:
        failures.append("FAIL: could not find '**Total URLs Tracked:** ~N' in header.")
    if footer_n is None:
        failures.append("FAIL: could not find '*Total URLs Tracked: ~N*' in footer.")

    if header_n is not None and footer_n is not None and header_n != footer_n:
        failures.append(
            f"FAIL: header ({header_n}) and footer ({footer_n}) disagree — "
            "both must show the same number."
        )

    if header_n is not None and abs(header_n - actual) > TOLERANCE:
        failures.append(
            f"FAIL: header count {header_n} drifts {abs(header_n - actual)} "
            f"from actual {actual} (tolerance ±{TOLERANCE})."
        )

    if footer_n is not None and abs(footer_n - actual) > TOLERANCE:
        failures.append(
            f"FAIL: footer count {footer_n} drifts {abs(footer_n - actual)} "
            f"from actual {actual} (tolerance ±{TOLERANCE})."
        )

    if failures:
        for msg in failures:
            print(msg)
        print(
            "\nUpdate the '**Total URLs Tracked:**' line (header) and "
            "'*Total URLs Tracked: ~N*' line (footer) in "
            "docs/reference/microsoft-learn-urls.md to match the actual count."
        )
        return 1

    print(
        f"OK: both prose counts ({header_n}) are within ±{TOLERANCE} "
        f"of actual count ({actual}) and agree with each other."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
