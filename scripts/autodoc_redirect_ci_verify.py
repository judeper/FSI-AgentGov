#!/usr/bin/env python3
"""Independent CI re-verification of an autodoc *redirect* pull request.

The unattended runner opens redirect PRs (a moved Microsoft Learn URL swapped in
``docs/reference/microsoft-learn-urls.md``) and verifies the swap itself before
opening the PR. For Stage 2 auto-merge, the merge must additionally be gated on an
**independent** check that re-derives the verdict from the *actual* PR diff on
GitHub's side — so a buggy or tampered PR-open path cannot smuggle a non-clean
change past auto-merge.

This module re-implements the clean-swap check from scratch (it does NOT import the
runner) and derives the old/new URLs from the diff itself. A redirect diff is clean
only when:

* the diff touches ONLY the Learn URL list file,
* it is exactly one removed table row + one added table row,
* the two rows differ in exactly one pipe-delimited cell, and
* that cell's old and new values are both well-formed http(s) URLs.

Exit code 0 = clean redirect (safe to auto-merge). Exit code 2 = not a clean
redirect (fail closed; a human must review). Exit code 1 = usage/parse error.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

TARGET_FILE = "docs/reference/microsoft-learn-urls.md"

# A well-formed URL: scheme + only RFC 3986 URL characters. Mirrors the runner's
# guard so the two agree on what a "URL" is, but is duplicated here on purpose so
# the CI check stays independent of the runner module.
_URL_RE = re.compile(r"^https?://[A-Za-z0-9\-._~:/?#\[\]@!$&'()*+,;=%]+$")

# Matches a unified-diff file header: `+++ b/<path>` (or `--- a/<path>`).
_DIFF_FILE_RE = re.compile(r"^[+-]{3} [ab]/(.+)$")


class NotCleanRedirect(Exception):
    """Raised with a human-readable reason when the diff is not a clean swap."""


def _changed_files(diff_text: str) -> list[str]:
    """Repo-relative paths named in the diff's `+++ b/...` / `--- a/...` headers."""

    files: list[str] = []
    for line in diff_text.splitlines():
        if line.startswith(("+++ ", "--- ")):
            match = _DIFF_FILE_RE.match(line)
            if match and match.group(1) != "/dev/null":
                files.append(match.group(1).strip())
    return files


def _diff_body_lines(diff_text: str) -> tuple[list[str], list[str]]:
    """Return (removed, added) content lines, excluding file headers."""

    removed: list[str] = []
    added: list[str] = []
    for line in diff_text.splitlines():
        if line.startswith(("+++", "---")):
            continue
        if line.startswith("+"):
            added.append(line[1:])
        elif line.startswith("-"):
            removed.append(line[1:])
    return removed, added


def _single_cell_swap(removed: str, added: str) -> tuple[str, str]:
    """Return (old_value, new_value) of the one differing table cell, or raise."""

    if not (removed.lstrip().startswith("|") and added.lstrip().startswith("|")):
        raise NotCleanRedirect("changed lines are not markdown table rows")
    rcells = removed.split("|")
    acells = added.split("|")
    if len(rcells) != len(acells):
        raise NotCleanRedirect("removed/added rows have different cell counts")
    diff_positions = [i for i in range(len(rcells)) if rcells[i] != acells[i]]
    if len(diff_positions) != 1:
        raise NotCleanRedirect(f"rows differ in {len(diff_positions)} cells; exactly one URL cell may change")
    index = diff_positions[0]
    return rcells[index].strip(), acells[index].strip()


def verify_redirect_diff(diff_text: str) -> tuple[str, str]:
    """Validate a redirect diff. Return (old_url, new_url) or raise NotCleanRedirect."""

    files = sorted(set(_changed_files(diff_text)))
    if files != [TARGET_FILE]:
        raise NotCleanRedirect(f"diff must touch only {TARGET_FILE}; touched {files or ['nothing']}")

    removed, added = _diff_body_lines(diff_text)
    if len(removed) != 1 or len(added) != 1:
        raise NotCleanRedirect(f"expected exactly 1 removed + 1 added line; got {len(removed)} removed / {len(added)} added")

    old_url, new_url = _single_cell_swap(removed[0], added[0])
    if not _URL_RE.match(old_url):
        raise NotCleanRedirect(f"old cell value is not a well-formed URL: {old_url!r}")
    if not _URL_RE.match(new_url):
        raise NotCleanRedirect(f"new cell value is not a well-formed URL: {new_url!r}")
    if old_url == new_url:
        raise NotCleanRedirect("old and new URLs are identical; nothing changed")
    return old_url, new_url


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Independently verify an autodoc redirect PR diff.")
    parser.add_argument("--diff", required=True, help="Path to the unified diff of the PR (base...head).")
    args = parser.parse_args(argv)

    try:
        diff_text = Path(args.diff).read_text(encoding="utf-8")
    except OSError as exc:
        print(f"redirect-verify: could not read diff: {exc}", file=sys.stderr)
        return 1

    try:
        old_url, new_url = verify_redirect_diff(diff_text)
    except NotCleanRedirect as exc:
        print(f"redirect-verify: NOT a clean redirect — {exc}", file=sys.stderr)
        return 2

    print(f"redirect-verify: clean redirect swap {old_url} -> {new_url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
