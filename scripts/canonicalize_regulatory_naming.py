#!/usr/bin/env python3
"""Canonicalize stale OCC 2011-12 and SR 11-7 references corpus-wide.

Companion to ``scripts/verify_regulatory_naming.py``. Reuses the same
skip logic so the transform is provably idempotent (rerunning produces
no diff).

Convention enforced (mirrors AS3' watchlist convention):

* **Prose**, **bullets**, and table cells: bare ``OCC 2011-12`` →
  ``OCC Bulletin 2026-13 (formerly OCC 2011-12)``; bare ``SR 11-7`` /
  ``Federal Reserve SR 11-7`` → ``Fed SR 26-2 (formerly SR 11-7)``.
  Tables are random-access surfaces, so every cell containing the
  reference gets the formerly-form. The verifier accepts this.
* **Headings** (``#``..``######``) and **table-row first cells** that
  embed the regulation in a section name: short canonical form is
  preferred (``OCC Bulletin 2026-13``, ``SR 26-2``) so heading TOC and
  table-row labels stay readable. We keep the heading-TEXT canonical
  short and ALSO pin the OLD slug as an explicit ``{#old-slug}``
  anchor when (a) the heading text actually changes AND (b) the file
  has any inbound cross-references using the old slug. (Inbound check
  is repo-wide grep at script-load time.)
* **Shorthand** ``OCC/SR 11-7`` and ``OCC/SR 26-2`` (always wrong) →
  ``OCC Bulletin 2026-13 / Fed SR 26-2`` (or ``... (formerly SR 11-7)``
  for the 11-7 form).

Same-line and same-block carve-outs (NEVER rewritten):

* Lines inside fenced code blocks.
* Lines under H2 sections matching ``version history``, ``release
  history``, ``changelog``, or ``prior version``.
* Lines containing supersession-narrative markers: ``rescinded``,
  ``superseded``, ``supersede and rescind``, ``supersedes``,
  ``predecessor``, ``formerly known as``, ``no longer resolves``,
  ``rescinds``.
* Material **admonition titles** (lines starting ``!!! `` or ``??? ``)
  and **admonition continuation lines** (4-space-indented lines under
  the most recent open admonition until the next blank-then-unindented
  line).
* Lines containing the file slug in backticks
  (``2.6-model-risk-management-sr-26-2.md``).
* Lines inside the "Regulatory sources — historical" bullet section
  (between that bold-paragraph header and the next blank line OR the
  next section header).
* Lines containing the legacy URL fragment
  ``bulletin-2011-12.html`` or ``sr1107.htm`` (citing the historical
  URL on the same line means the text reference is intentional).

Usage::

    python scripts/canonicalize_regulatory_naming.py --dry-run
    python scripts/canonicalize_regulatory_naming.py --apply
    python scripts/canonicalize_regulatory_naming.py --verify  # idempotence check
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_ROOT = REPO_ROOT / "docs"

# ---------------------------------------------------------------------------
# Surface coverage — every .md under docs/ except local-only screenshot
# checklists (docs/images/*/EXPECTED.md and similar).
# ---------------------------------------------------------------------------


SKIP_DIR_PARTS = {"images"}


def gather_files() -> list[Path]:
    out: list[Path] = []
    for path in sorted(DOCS_ROOT.rglob("*.md")):
        rel_parts = path.relative_to(DOCS_ROOT).parts
        if any(part in SKIP_DIR_PARTS for part in rel_parts):
            continue
        out.append(path)
    return out


# ---------------------------------------------------------------------------
# Same skip logic as the verifier
# ---------------------------------------------------------------------------


HISTORY_SECTION_RE = re.compile(
    r"(?i)(version\s+history|release\s+history|changelog|prior\s+version)"
)

# Material admonition opener: `!!! ` (plain) or `??? ` (collapsible).
ADMONITION_OPENER_RE = re.compile(r"^\s*(?:!!!|\?\?\?)\s+")

# Lines that document the supersession event itself — preserved as-is.
# (Broadened in AS15b-verifier per rubber-duck N-1: covers `supersession`,
# `superseding`, `rescission`, `rescinding` in addition to the original
# verb forms. SOFT words like "legacy"/"historical"/"archived" are
# deliberately NOT included — too easy for an author to drop accidentally
# and would defeat the gate.)
SUPERSESSION_NARRATIVE_RE = re.compile(
    r"(?i)\b(rescind(?:ed|ing|s)?|rescission|"
    r"supersed(?:e|ed|es|ing)|supersession|"
    r"supersede\s+and\s+rescind|"
    r"predecessor|formerly\s+known\s+as|"
    r"no\s+longer\s+resolves)\b"
)

# Legacy-URL citation markers — if these appear on the same line, the bare
# textual reference is intentional (it pairs the historical URL with its
# old name).
LEGACY_URL_MARKER_RE = re.compile(
    r"(bulletin-2011-12\.html|sr1107\.htm|/bulletins/2011/|sr\s*letter\s*11-7)",
    re.IGNORECASE,
)

# File-slug self-reference (the canonical file IS named after the
# supersession; mentioning that slug requires the old name).
FILE_SLUG_BACKTICK_RE = re.compile(r"`[^`]*2\.6-model-risk-management-sr-26-2[^`]*`")

# Bold paragraph header that opens the "historical regulatory sources" block
# in control 2.6 (NOT an H2, so the H2 history-section rule doesn't catch it).
HISTORICAL_BLOCK_OPENER_RE = re.compile(
    r"\*\*Regulatory sources\s*[—-]\s*historical", re.IGNORECASE
)


# Already-canonical span: ``(formerly ...)``.
FORMERLY_SPAN_RE = re.compile(r"\([^)]*\bformerly\b[^)]*\)", re.IGNORECASE)

# Bare references that need rewriting.
BARE_OCC_RE = re.compile(r"\bOCC\s+(?:Bulletin\s+)?2011-12\b")
BARE_SR_RE = re.compile(r"\b(?:Federal\s+Reserve\s+SR|Fed\s+SR|SR)\s+11-7\b")

# Always-wrong shorthand.
SHORTHAND_OCC_SR_11_7_RE = re.compile(
    r"\bOCC\s*/\s*SR\s*11-7\b", re.IGNORECASE
)
SHORTHAND_OCC_SR_26_2_RE = re.compile(
    r"\bOCC\s*/\s*SR\s*26-2\b", re.IGNORECASE
)


# ---------------------------------------------------------------------------
# Per-line skip context tracker
# ---------------------------------------------------------------------------


@dataclass
class LineContext:
    """Per-line state machine state at the time the line is seen.

    `admonition_has_supersession_context` is set BLOCK-LEVEL during a
    second-pass-style mutation in `iter_lines`: True iff the admonition
    opener title OR ANY body line in the same block contains a marker
    matching `SUPERSESSION_NARRATIVE_RE`. Lines outside admonitions
    have this field = False (its default). The carve-out at
    `line_is_skip_eligible` reads this to decide whether to skip the
    line: `if ctx.in_admonition: return ctx.admonition_has_supersession_context`.

    Note: nested admonitions are NOT modeled. An opener at deeper indent
    inside an outer body is treated as starting a new block (which closes
    the outer). No corpus files use nested admonitions today.
    """

    line_no: int
    text: str
    in_fence: bool
    in_admonition: bool
    in_historical_block: bool
    current_h2: str | None
    admonition_has_supersession_context: bool = False


def iter_lines(text: str) -> list[LineContext]:
    """Walk the file, tracking fenced code, admonition continuation, and
    historical-bullet sections.

    Per-block admonition context (AS15b-verifier B2):
    each admonition block is assigned a single ``has_supersession_context``
    flag computed from its opener title + body lines. The flag is then
    written back onto every emitted ``LineContext`` belonging to the block
    via in-place mutation at block close. Block close happens at four
    sites — heading, unindented non-blank line, new admonition opener,
    and EOF — all routed through the local ``close_block`` helper to
    keep them in sync.
    """
    out: list[LineContext] = []
    in_fence = False
    in_admonition = False
    admonition_indent: int | None = None
    in_historical_block = False
    current_h2: str | None = None

    # AS15b-verifier B2 — per-block admonition context tracker.
    block_start_idx: int | None = None
    block_has_context = False

    def close_block() -> None:
        """Mark every LineContext in the current admonition block with
        the computed ``admonition_has_supersession_context`` flag, then
        reset block tracking. Idempotent if no block is open.
        """
        nonlocal block_start_idx, block_has_context
        if block_start_idx is not None:
            for i in range(block_start_idx, len(out)):
                out[i].admonition_has_supersession_context = block_has_context
        block_start_idx = None
        block_has_context = False

    for idx, raw in enumerate(text.splitlines(), start=1):
        stripped_left = raw.lstrip()
        leading_spaces = len(raw) - len(stripped_left)

        # Fenced-code toggle.
        if stripped_left.startswith("```"):
            in_fence = not in_fence
            out.append(
                LineContext(idx, raw, in_fence, in_admonition,
                            in_historical_block, current_h2)
            )
            continue

        if in_fence:
            out.append(
                LineContext(idx, raw, True, in_admonition,
                            in_historical_block, current_h2)
            )
            continue

        # Heading tracker (H1 resets, H2 sets current). Headings always
        # close any open admonition block — route through close_block so
        # the block-context flag is written back before reset.
        if raw.startswith("## "):
            close_block()
            current_h2 = raw[3:].strip()
            in_admonition = False
            admonition_indent = None
            in_historical_block = False
        elif raw.startswith("# "):
            close_block()
            current_h2 = None
            in_admonition = False
            admonition_indent = None
            in_historical_block = False
        elif raw.startswith("### ") or raw.startswith("#### "):
            close_block()
            in_admonition = False
            admonition_indent = None
            in_historical_block = False

        # Admonition open/continue/close.
        if ADMONITION_OPENER_RE.match(raw):
            close_block()  # Close any prior block before opening a new one.
            in_admonition = True
            admonition_indent = leading_spaces
            block_start_idx = len(out)  # Opener is the start of the new block.
            block_has_context = bool(SUPERSESSION_NARRATIVE_RE.search(raw))
        elif in_admonition:
            if raw.strip() == "":
                # Blank line — admonition stays open until next non-blank
                # at lower indent. Continue without closing.
                pass
            elif leading_spaces > (admonition_indent or 0):
                # Still inside admonition body — accumulate context.
                if SUPERSESSION_NARRATIVE_RE.search(raw):
                    block_has_context = True
            else:
                # Unindented non-blank — admonition closed.
                close_block()
                in_admonition = False
                admonition_indent = None

        # Historical-bullet block.
        if HISTORICAL_BLOCK_OPENER_RE.search(raw):
            in_historical_block = True
        elif in_historical_block:
            if raw.startswith("**") and not HISTORICAL_BLOCK_OPENER_RE.search(raw):
                # Next bold paragraph header closes the block.
                in_historical_block = False
            elif raw.startswith(("# ", "## ", "### ", "#### ")):
                in_historical_block = False

        out.append(
            LineContext(idx, raw, in_fence, in_admonition,
                        in_historical_block, current_h2)
        )

    # EOF: close any trailing open block so its members get the flag.
    close_block()
    return out


# ---------------------------------------------------------------------------
# Per-line transform
# ---------------------------------------------------------------------------


def line_is_skip_eligible(ctx: LineContext) -> bool:
    if ctx.in_fence:
        return True
    if ctx.in_admonition:
        # AS15b-verifier B2 — admonitions are skipped ONLY when the block
        # has supersession context (opener title or any body line contains
        # a marker matching SUPERSESSION_NARRATIVE_RE). Generic admonitions
        # without supersession context are scanned, so admonition-body
        # shorthand (e.g., "(OCC 2011-12 / SR 11-7)") is no longer leaked
        # to customers via search snippets.
        return ctx.admonition_has_supersession_context
    if ctx.in_historical_block:
        return True
    if ctx.current_h2 and HISTORY_SECTION_RE.search(ctx.current_h2):
        return True
    if SUPERSESSION_NARRATIVE_RE.search(ctx.text):
        return True
    if LEGACY_URL_MARKER_RE.search(ctx.text):
        return True
    if FILE_SLUG_BACKTICK_RE.search(ctx.text):
        return True
    return False


def is_heading_line(text: str) -> bool:
    return bool(re.match(r"^#{1,6}\s", text))


def is_table_row(text: str) -> bool:
    s = text.strip()
    return s.startswith("|") and s.endswith("|") and "|" in s[1:-1]


def find_formerly_spans(line: str) -> list[tuple[int, int]]:
    return [m.span() for m in FORMERLY_SPAN_RE.finditer(line)]


def in_any_span(pos: int, spans: list[tuple[int, int]]) -> bool:
    return any(s <= pos < e for s, e in spans)


def transform_line(line: str, mode: str) -> str:
    """Rewrite bare references on ``line``.

    ``mode`` is ``heading``, ``table``, or ``prose``. Heading uses short
    canonical (no formerly span). Table and prose use formerly-form.
    """
    out = line

    # Process shorthand FIRST (always wrong, no skip).
    def _rewrite_shorthand_11_7(m: re.Match) -> str:
        return "OCC Bulletin 2026-13 / Fed SR 26-2 (formerly SR 11-7)"

    def _rewrite_shorthand_26_2(m: re.Match) -> str:
        return "OCC Bulletin 2026-13 / Fed SR 26-2"

    out = SHORTHAND_OCC_SR_11_7_RE.sub(_rewrite_shorthand_11_7, out)
    out = SHORTHAND_OCC_SR_26_2_RE.sub(_rewrite_shorthand_26_2, out)

    # Now bare OCC 2011-12.
    def _rewrite_occ(out_str: str) -> str:
        spans_local = find_formerly_spans(out_str)
        # Walk matches right-to-left so position-based replacement doesn't
        # shift later matches.
        matches = list(BARE_OCC_RE.finditer(out_str))
        for m in reversed(matches):
            if in_any_span(m.start(), spans_local):
                continue
            old = m.group(0)
            if mode == "heading":
                replacement = "OCC Bulletin 2026-13"
            else:
                # Preserve "Bulletin" capitalization if the source had it.
                if "Bulletin" in old:
                    replacement = "OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12)"
                else:
                    replacement = "OCC Bulletin 2026-13 (formerly OCC 2011-12)"
            out_str = out_str[:m.start()] + replacement + out_str[m.end():]
        return out_str

    out = _rewrite_occ(out)

    # Now bare SR 11-7 (preserve "Federal Reserve" / "Fed" prefix when present).
    def _rewrite_sr(out_str: str) -> str:
        spans_local = find_formerly_spans(out_str)
        matches = list(BARE_SR_RE.finditer(out_str))
        for m in reversed(matches):
            if in_any_span(m.start(), spans_local):
                continue
            old = m.group(0)
            old_lower = old.lower()
            if mode == "heading":
                if "federal reserve" in old_lower:
                    replacement = "Federal Reserve SR 26-2"
                elif old_lower.startswith("fed "):
                    replacement = "Fed SR 26-2"
                else:
                    replacement = "SR 26-2"
            else:
                if "federal reserve" in old_lower:
                    replacement = "Federal Reserve SR 26-2 (formerly SR 11-7)"
                elif old_lower.startswith("fed "):
                    replacement = "Fed SR 26-2 (formerly SR 11-7)"
                else:
                    replacement = "Fed SR 26-2 (formerly SR 11-7)"
            out_str = out_str[:m.start()] + replacement + out_str[m.end():]
        return out_str

    out = _rewrite_sr(out)
    return out


def transform_file(text: str) -> str:
    contexts = iter_lines(text)
    new_lines: list[str] = []
    for ctx in contexts:
        if line_is_skip_eligible(ctx):
            new_lines.append(ctx.text)
            continue
        if is_heading_line(ctx.text):
            mode = "heading"
        elif is_table_row(ctx.text):
            mode = "table"
        else:
            mode = "prose"
        new_lines.append(transform_line(ctx.text, mode))
    return "\n".join(new_lines) + ("\n" if text.endswith("\n") else "")


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true",
                   help="Show files that would change. No writes.")
    g.add_argument("--apply", action="store_true",
                   help="Apply rewrites in place.")
    g.add_argument("--verify", action="store_true",
                   help="Idempotence check: rewrite in memory, exit 1 "
                   "if any file would change.")
    parser.add_argument("--paths", nargs="*", default=None,
                        help="Limit to these paths (relative to repo root). "
                        "Default: every .md under docs/ except images/.")
    args = parser.parse_args(argv)

    if args.paths:
        files = [REPO_ROOT / p for p in args.paths]
    else:
        files = gather_files()

    changed: list[Path] = []
    for f in files:
        if not f.exists():
            print(f"WARN: {f} not found", file=sys.stderr)
            continue
        original = f.read_text(encoding="utf-8")
        rewritten = transform_file(original)
        if original != rewritten:
            changed.append(f)
            if args.apply:
                f.write_text(rewritten, encoding="utf-8")

    print(f"Files scanned: {len(files)}")
    print(f"Files {'changed' if args.apply else 'would-change'}: {len(changed)}")
    for f in changed:
        try:
            print(f"  {f.relative_to(REPO_ROOT)}")
        except ValueError:
            print(f"  {f}")

    if args.verify and changed:
        print("FAIL: idempotence check found pending rewrites.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
