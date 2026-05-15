#!/usr/bin/env python3
"""Verify canonical OCC/SR regulatory naming on customer-facing summary surfaces.

Two checks (per AS3' audit fix-set):

  1. **Rendered prose** — every reference to OCC Bulletin 2011-12 or SR 11-7
     in the watched 20-file allowlist MUST be inside a ``(... formerly ...)``
     parenthetical span on the same line, OR the file/section is on the
     skip list (fenced code blocks, version-history H2 sections).

     Shorthand ``OCC/SR 11-7``, ``OCC/SR 26-2``, ``OCC / SR 11-7`` is ALWAYS
     a fail (explicit naming required).

  2. **Internal link destinations** — Markdown links whose destination is
     internal (``#anchor`` or relative ``../`` path, not ``http://``/``https://``)
     MUST NOT contain stale slugs: ``occ-2011-12``, ``occ-bulletin-2011-12``,
     ``sr-11-7``, ``occ-sr-11-7``. The canonical filename slug
     ``2.6-model-risk-management-sr-26-2.md`` is allowed.

Usage::

    python scripts/verify_regulatory_naming.py            # human-readable scan
    python scripts/verify_regulatory_naming.py --check    # CI mode (exit 1)

Design notes:

  * **Line/token** — not proximity. We scan one line at a time. A bare
    ``OCC 2011-12`` mention is allowed only if its character span sits
    inside a ``(... formerly ...)`` parenthetical on the same line.
  * **URL-aware** — the ``(URL)`` portion of a Markdown ``[text](URL)``
    link is stripped before the prose scan (URLs are not customer-facing
    rendered text). Link **text** is scanned. Internal link destinations
    are scanned by Check 2 instead.
  * **History sections** — H2 sections matching ``version history``,
    ``release history``, ``changelog``, or ``prior version`` are skipped
    on the assumption that historical text accurately quotes prior naming.
  * **Allowlist** — narrow to 20 customer-facing summary surfaces. Pillar
    control bodies, playbooks, and historical reports are out of scope.

The convention this gate enforces:

  * First mention per page: ``OCC Bulletin 2026-13 (formerly OCC 2011-12)``
    or ``OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12)``.
  * Subsequent mentions: short form ``OCC Bulletin 2026-13`` alone.
  * Fed SR pattern: ``Fed SR 26-2 (formerly SR 11-7)`` or
    ``Federal Reserve SR 26-2 (formerly SR 11-7)`` first; ``SR 26-2``
    alone thereafter.
  * Section V references: ``OCC Bulletin 2026-13 §V (formerly OCC 2011-12 §V)``.
  * Compact regulatory anchors:
    ``OCC Bulletin 2026-13 / Fed SR 26-2`` or
    ``OCC Bulletin 2026-13 / Federal Reserve SR 26-2``.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_ROOT = REPO_ROOT / "docs"

# ---------------------------------------------------------------------------
# Watched 20-file summary-surface allowlist
# ---------------------------------------------------------------------------
#
# We narrow to customer-facing summary surfaces only. Pillar control bodies
# (78 files) and per-control playbooks (~312 files) are deferred to a
# separate per-pillar sweep with its own design pass.

WATCHED_FILES: list[Path] = [
    DOCS_ROOT / "index.md",
    DOCS_ROOT / "controls" / "CONTROL-INDEX.md",
    DOCS_ROOT / "reference" / "regulatory-mappings.md",
    DOCS_ROOT / "reference" / "glossary.md",
    DOCS_ROOT / "reference" / "agent-365-capabilities-summary.md",
    DOCS_ROOT / "reference" / "cco-quick-reference.md",
    DOCS_ROOT / "reference" / "csa-quick-reference.md",
    DOCS_ROOT / "reference" / "csa-positioning-guide.md",
    DOCS_ROOT / "reference" / "assessment-coverage.md",
    DOCS_ROOT / "reference" / "faq.md",
]
# Plus every Markdown file under getting-started/ and framework/.
WATCHED_DIRS: list[Path] = [
    DOCS_ROOT / "getting-started",
    DOCS_ROOT / "framework",
]


def gather_watched_paths() -> list[Path]:
    """Return the full deterministic watched-file list."""
    paths: list[Path] = list(WATCHED_FILES)
    for directory in WATCHED_DIRS:
        if directory.exists():
            paths.extend(sorted(directory.glob("*.md")))
    # De-duplicate while preserving order.
    seen: set[Path] = set()
    out: list[Path] = []
    for p in paths:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out


# ---------------------------------------------------------------------------
# Regex library
# ---------------------------------------------------------------------------

# H2 sections whose nearest header matches this pattern are skipped. Release
# history and changelog text accurately quotes prior naming and must not be
# flagged.
HISTORY_SECTION_RE = re.compile(
    r"(?i)(version\s+history|release\s+history|changelog|prior\s+version)"
)

# Strip any ``[text](URL)`` Markdown URL destination. The TEXT is scanned by
# the prose check; the URL is scanned by the internal-link check.
MD_LINK_URL_STRIP_RE = re.compile(r"\]\([^)]*\)")

# Markdown link / image destinations to scan for stale slugs.
MD_LINK_DEST_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")

# ``(... formerly ... )`` parenthetical span. Case-insensitive. The
# parenthetical must contain ``formerly`` somewhere inside its body, not
# only at the start (e.g. ``(banks; formerly OCC Bulletin 2011-12)`` and
# ``(formerly SR 11-7; the 2026 supersession)`` both qualify).
FORMERLY_SPAN_RE = re.compile(r"\([^)]*\bformerly\b[^)]*\)", re.IGNORECASE)

# Bare references that MUST sit inside a formerly-span on the same line.
BARE_OCC_RE = re.compile(r"\bOCC\s*(?:Bulletin\s+)?2011-12\b", re.IGNORECASE)
BARE_SR_RE = re.compile(r"\bSR\s*11-7\b", re.IGNORECASE)

# Always-wrong shorthand. The OCC and Fed are different authorities.
SHORTHAND_RE = re.compile(
    r"\bOCC\s*/\s*SR\s*(?:11-7|26-2)\b|\bOCC/SR(?:11-7|26-2)\b",
    re.IGNORECASE,
)

# Stale slugs in internal Markdown link destinations. Canonical
# ``sr-26-2`` slugs (filenames) are explicitly allowed.
STALE_SLUG_RE = re.compile(
    r"(?i)\b(occ[-_]?bulletin[-_]?2011[-_]?12|occ[-_]?2011[-_]?12|"
    r"sr[-_]11[-_]7|occ[-_]sr[-_]11[-_]7)\b"
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def iter_lines_skipping_fences(
    text: str,
) -> Iterable[tuple[int, str, str | None]]:
    """Yield ``(line_number, line_text, current_h2)`` for every line that is
    NOT inside a fenced code block. ``line_number`` is 1-based.
    """
    in_fence = False
    current_h2: str | None = None
    for idx, raw in enumerate(text.splitlines(), start=1):
        stripped = raw.lstrip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if raw.startswith("## "):
            current_h2 = raw[3:].strip()
        elif raw.startswith("# "):
            current_h2 = None
        yield idx, raw, current_h2


def find_formerly_spans(line: str) -> list[tuple[int, int]]:
    """Return inclusive char ranges that mark ``(... formerly ...)`` spans."""
    return [m.span() for m in FORMERLY_SPAN_RE.finditer(line)]


def is_inside_any_span(pos: int, spans: list[tuple[int, int]]) -> bool:
    return any(start <= pos < end for start, end in spans)


def strip_link_urls(line: str) -> str:
    """Replace ``](URL)`` destinations with empty destinations to keep
    column positions stable for the prose scan. Link TEXT is preserved
    so naming inside link text is still scanned.
    """
    return MD_LINK_URL_STRIP_RE.sub("]()", line)


# ---------------------------------------------------------------------------
# Check 1 — rendered prose
# ---------------------------------------------------------------------------


def check_prose(path: Path) -> list[str]:
    """Return failure messages (empty == PASS) for one watched file."""
    failures: list[str] = []
    text = path.read_text(encoding="utf-8")
    for line_no, line, h2 in iter_lines_skipping_fences(text):
        if h2 and HISTORY_SECTION_RE.search(h2):
            continue
        scan_line = strip_link_urls(line)
        # Always-wrong shorthand.
        for m in SHORTHAND_RE.finditer(scan_line):
            failures.append(
                _diag(
                    path, line_no, line, m.group(0),
                    "shorthand 'OCC/SR' is always wrong (OCC and the Fed "
                    "are different authorities; explicit naming required)",
                    "OCC Bulletin 2026-13 / Fed SR 26-2",
                )
            )
        # Bare 2011-12 / SR 11-7 references must be inside a formerly-span.
        spans = find_formerly_spans(scan_line)
        for m in BARE_OCC_RE.finditer(scan_line):
            if is_inside_any_span(m.start(), spans):
                continue
            failures.append(
                _diag(
                    path, line_no, line, m.group(0),
                    "bare OCC 2011-12 reference outside a "
                    "'(... formerly ...)' parenthetical",
                    "OCC Bulletin 2026-13 (formerly OCC 2011-12)",
                )
            )
        for m in BARE_SR_RE.finditer(scan_line):
            if is_inside_any_span(m.start(), spans):
                continue
            failures.append(
                _diag(
                    path, line_no, line, m.group(0),
                    "bare SR 11-7 reference outside a "
                    "'(... formerly ...)' parenthetical",
                    "Fed SR 26-2 (formerly SR 11-7)",
                )
            )
    return failures


# ---------------------------------------------------------------------------
# Check 2 — internal link destinations
# ---------------------------------------------------------------------------


def is_external_destination(dest: str) -> bool:
    dest = dest.strip().split()[0] if dest.strip() else dest
    return dest.startswith(("http://", "https://", "mailto:", "tel:"))


def check_internal_links(path: Path) -> list[str]:
    """Return failure messages (empty == PASS) for one watched file."""
    failures: list[str] = []
    text = path.read_text(encoding="utf-8")
    for line_no, line, h2 in iter_lines_skipping_fences(text):
        if h2 and HISTORY_SECTION_RE.search(h2):
            continue
        for m in MD_LINK_DEST_RE.finditer(line):
            dest = m.group(1)
            if is_external_destination(dest):
                continue
            stale = STALE_SLUG_RE.search(dest)
            if stale:
                failures.append(
                    _diag(
                        path, line_no, line, stale.group(0),
                        f"internal link destination contains stale slug "
                        f"{stale.group(0)!r} (target appears to reference "
                        "a stale-named file or anchor)",
                        "Update the target to the canonical sr-26-2 / "
                        "bulletin-2026-13 form",
                    )
                )
    return failures


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def _diag(
    path: Path, line_no: int, line: str, matched: str, why: str, canonical: str,
) -> str:
    if path.is_absolute():
        try:
            rel: Path = path.relative_to(REPO_ROOT)
        except ValueError:
            rel = path
    else:
        rel = path
    snippet = line.strip()
    if len(snippet) > 160:
        snippet = snippet[:157] + "..."
    return (
        f"FAIL: {rel}:{line_no}: {why}.\n"
        f"      matched: {matched!r}\n"
        f"      line:    {snippet}\n"
        f"      suggested canonical phrasing: {canonical}"
    )


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def run_all_checks() -> tuple[int, list[str], int]:
    """Return ``(failure_count, messages, files_scanned)``."""
    paths = gather_watched_paths()
    messages: list[str] = []
    for path in paths:
        if not path.exists():
            messages.append(f"FAIL: watched file {path} not found")
            continue
        messages.extend(check_prose(path))
        messages.extend(check_internal_links(path))
    return len(messages), messages, len(paths)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--check",
        action="store_true",
        help="CI mode: exit 1 on any failure (default exits 0).",
    )
    args = parser.parse_args(argv)

    n_failures, messages, files_scanned = run_all_checks()

    print("=" * 60)
    print("FSI regulatory naming verification")
    print("=" * 60)
    print(f"Files scanned: {files_scanned}")
    print()

    if n_failures == 0:
        print("PASS: all OCC/SR references on watched surfaces use canonical "
              "naming.")
        return 0

    for msg in messages:
        print(msg)
    print()
    print(f"FAIL: {n_failures} drift issue(s) found.")
    return 1 if args.check else 0


if __name__ == "__main__":
    sys.exit(main())
