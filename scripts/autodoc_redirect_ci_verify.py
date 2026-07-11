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
import urllib.parse
from pathlib import Path

TARGET_FILE = "docs/reference/microsoft-learn-urls.md"

# A well-formed URL: scheme + only RFC 3986 URL characters. Mirrors the runner's
# guard so the two agree on what a "URL" is, but is duplicated here on purpose so
# the CI check stays independent of the runner module.
_URL_RE = re.compile(r"^https?://[A-Za-z0-9\-._~:/?#\[\]@!$&'()*+,;=%]+$")
_TRACKING_QUERY_KEYS = {"msockid", "wt.mc_id", "ocid"}


def _canonicalize_url(url: str) -> str:
    """Independent tracking-parameter canonicalization for the CI trust boundary."""

    value = url.strip()
    try:
        parsed = urllib.parse.urlsplit(value)
    except ValueError:
        return value
    filtered = [
        (key, item)
        for key, item in urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
        if key.lower() not in _TRACKING_QUERY_KEYS and not key.lower().startswith("utm_")
    ]
    return urllib.parse.urlunsplit(
        (parsed.scheme, parsed.netloc, parsed.path, urllib.parse.urlencode(filtered, doseq=True), parsed.fragment)
    )


def _host_allowed(url: str) -> bool:
    """Fail-closed Microsoft-domain allowlist for the NEW redirect target URL.

    Independent re-implementation of the runner's allowlist (deliberately NOT imported from
    ``autodoc_runner``, mirroring the duplicated URL-charset guard above). A redirect's new URL
    host must be ``learn.microsoft.com``, ``microsoft.com``, or a subdomain ending in
    ``.microsoft.com``. The host comes from ``urlparse(...).hostname`` (lower-cased) so credential
    tricks (``https://learn.microsoft.com@evil.example/``) resolve to the real authority host and
    subdomain spoofs (``learn.microsoft.com.evil.com``) are rejected. Empty host, IPs, malformed
    authority, or any parse error fail closed.
    """

    try:
        host = (urllib.parse.urlparse(url).hostname or "").lower()
    except ValueError:
        return False
    return host in ("learn.microsoft.com", "microsoft.com") or host.endswith(".microsoft.com")

# Matches a unified git-diff file header: `diff --git a/<path> b/<path>`.
# Files are taken from this authoritative header (not the +++/--- lines), which
# never carries a +/-/space prefix and so cannot be spoofed by hunk content.
_GIT_FILE_RE = re.compile(r"^diff --git a/.+ b/(.+)$")


class NotCleanRedirect(Exception):
    """Raised with a human-readable reason when the diff is not a clean swap."""


def _parse_diff(diff_text: str) -> tuple[list[str], list[str], list[str]]:
    """Hunk-aware parse of a unified git diff.

    Returns ``(files, removed, added)``. File paths are taken only from the
    authoritative ``diff --git a/... b/<path>`` headers, and ``+``/``-`` content
    lines are collected ONLY inside ``@@`` hunks. This is deliberately not a naive
    "skip lines starting with +++/---" parser: a removed content line whose text is
    ``---`` appears as ``----`` and an added line whose text starts with ``++``
    appears as ``+++...``; a naive parser would silently drop those, letting a
    non-clean change masquerade as clean. Header/metadata lines (``index``, mode,
    ``--- a/``, ``+++ b/``) appear only outside a hunk and are ignored here; only
    real ``diff --git`` and ``@@`` lines (which never carry a +/-/space prefix)
    change the parse state, so content lines cannot spoof them.
    """

    files: list[str] = []
    removed: list[str] = []
    added: list[str] = []
    in_hunk = False
    for line in diff_text.splitlines():
        if line.startswith("diff --git "):
            in_hunk = False
            match = _GIT_FILE_RE.match(line)
            if match and match.group(1) != "/dev/null":
                files.append(match.group(1).strip())
            continue
        if line.startswith("@@"):
            in_hunk = True
            continue
        if not in_hunk:
            continue
        if line.startswith("\\"):  # "\ No newline at end of file"
            continue
        if line.startswith("+"):
            added.append(line[1:])
        elif line.startswith("-"):
            removed.append(line[1:])
    return files, removed, added


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

    file_list, removed, added = _parse_diff(diff_text)
    files = sorted(set(file_list))
    if files != [TARGET_FILE]:
        raise NotCleanRedirect(f"diff must touch only {TARGET_FILE}; touched {files or ['nothing']}")

    if len(removed) != 1 or len(added) != 1:
        raise NotCleanRedirect(f"expected exactly 1 removed + 1 added line; got {len(removed)} removed / {len(added)} added")

    old_url, new_url = _single_cell_swap(removed[0], added[0])
    if not _URL_RE.match(old_url):
        raise NotCleanRedirect(f"old cell value is not a well-formed URL: {old_url!r}")
    if not _URL_RE.match(new_url):
        raise NotCleanRedirect(f"new cell value is not a well-formed URL: {new_url!r}")
    canonical_old = _canonicalize_url(old_url)
    canonical_new = _canonicalize_url(new_url)
    if new_url != canonical_new:
        raise NotCleanRedirect("new URL still contains known tracking parameters")
    if not _host_allowed(new_url):
        raise NotCleanRedirect(f"new URL host is not a Microsoft domain (off-domain redirect target): {new_url!r}")
    if canonical_old == canonical_new:
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
