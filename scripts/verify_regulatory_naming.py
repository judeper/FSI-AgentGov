"""Verify canonical OCC/SR regulatory naming across the docs/ corpus.

Two checks (per AS3' + AS11 audit fix-sets):

  1. **Rendered prose** — every reference to OCC Bulletin 2011-12 or SR 11-7
     in scanned files MUST be inside a ``(... formerly ...)`` parenthetical
     span on the same line, OR the line/section qualifies for a carve-out
     (fenced code blocks, version-history H2 sections, Material admonition
     titles + bodies, supersession-narrative lines, legacy-URL citation
     lines, file-slug self-reference lines, historical-bullet blocks).

     Shorthand ``OCC/SR 11-7``, ``OCC/SR 26-2``, ``OCC / SR 11-7`` is ALWAYS
     a fail (explicit naming required).

  2. **Internal link destinations** — Markdown links whose destination is
     internal (``#anchor`` or relative ``../`` path, not ``http://``/``https://``)
     MUST NOT contain stale slugs: ``occ-2011-12``, ``occ-bulletin-2011-12``,
     ``sr-11-7``, ``occ-sr-11-7``. The canonical filename slug
     ``2.6-model-risk-management-sr-26-2.md`` is allowed, and the explicit
     pinned anchor ``{#5-vendor-model-governance-sr-11-7-v}`` is allowed.

  3. **Customer-facing JSON prose** (AS22) — string fields under
     ``assessment/data/*.json`` that render verbatim into customer-facing
     SPA exports (e.g. ``description``, ``summary``, ``verification``,
     ``narrative``) are scanned with the same Check-1 prose rules (no
     formerly-span = fail; ``OCC/SR`` shorthand always fails). Markdown
     carve-outs (admonitions, history sections, fenced code) do not apply
     because JSON values render as plain bullet text in the agenda
     Markdown export at ``docs/javascripts/assessment-app.js`` lines
     4485-4495.

Usage::

    python scripts/verify_regulatory_naming.py            # human-readable scan
    python scripts/verify_regulatory_naming.py --check    # CI mode (exit 1)

Design notes:

  * **Line/token** — not proximity. We scan one line at a time. A bare
    ``OCC 2011-12`` mention is allowed only if its character span sits
    inside a ``(... formerly ...)`` parenthetical on the same line OR the
    enclosing line/section qualifies for a carve-out.
  * **URL-aware** — the ``(URL)`` portion of a Markdown ``[text](URL)``
    link is stripped before the prose scan (URLs are not customer-facing
    rendered text). Link **text** is scanned. Internal link destinations
    are scanned by Check 2 instead.
  * **Carve-outs** for supersession-narrative content (control 2.6 etc.):
      - Material admonition titles (``!!! ``/``??? ``) and indented body
      - Lines containing supersession markers (rescinded, superseded,
        supersedes, supersede and rescind, predecessor, formerly known
        as, no longer resolves, rescinds)
      - Lines containing legacy URL fragments (``bulletin-2011-12.html``,
        ``sr1107.htm``, ``/bulletins/2011/``, ``SR letter 11-7``)
      - Lines containing the file-slug in backticks
      - Bullets inside the ``Regulatory sources — historical`` block
  * **Skipped directories** — ``docs/images/*`` (local-only screenshot
    checklists, not customer-facing rendered content).

The convention this gate enforces:

  * First mention per page: ``OCC Bulletin 2026-13 (formerly OCC 2011-12)``.
  * Subsequent mentions: short form ``OCC Bulletin 2026-13`` alone.
  * Fed SR pattern: ``Fed SR 26-2 (formerly SR 11-7)``; short ``SR 26-2`` after.
  * Headings: short canonical form ``OCC Bulletin 2026-13`` / ``SR 26-2``
    is preferred (avoids TOC bloat) and accepted without formerly-span.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_ROOT = REPO_ROOT / "docs"
ASSESSMENT_DATA_ROOT = REPO_ROOT / "assessment" / "data"

# AS22 — JSON string fields under assessment/data/*.json that render as
# customer-facing prose in SPA exports (agenda Markdown bullets, JSON
# envelope summaries) and therefore must follow OCC/SR canonical naming.
# Keep this list narrow to avoid scanning machine-only fields like ``id``,
# ``url``, ``slug``, etc.
JSON_PROSE_FIELDS = frozenset({
    "description",
    "summary",
    "narrative",
    "verification",
    "rationale",
    "remediation",
    "guidance",
    "details",
    "notes",
    # solutions-lock-exceptions.json: maintainer-authored justification for an
    # accepted manifest/lock discrepancy. Free prose, so scan it (issue #322).
    "reason",
})

# AS22 hardening (post-audit follow-up): the companion to JSON_PROSE_FIELDS.
# Every string-valued key that appears in assessment/data/*.json must be
# classified as either prose (above) or machine-only (here). The drift-guard
# unit test in test_verify_regulatory_naming.py asserts the union covers
# every string-valued key actually present; a new key in neither bucket fails
# the test loudly so the maintainer must explicitly classify it. Without this
# guard, a future schema growth (e.g. a new ``commentary`` field on
# solutions-lock.json) would be silently skipped from the OCC/SR canonical-
# naming sweep, allowing customer-facing prose drift to ship undetected.
#
# Membership rule: list a key here only if its values are NEVER customer-
# facing prose (IDs, URLs, names of admin roles, schema versions, status
# enums, etc.). When in doubt, add the key to JSON_PROSE_FIELDS instead --
# false positives in prose scanning are recoverable; false negatives are not.
MACHINE_ONLY_JSON_FIELDS = frozenset({
    # Identifiers / slugs / versioning
    "id",
    "url",
    "name",
    "version",
    "schemaVersion",
    "tier",
    "domain",
    "status",
    "dataClassification",
    "retention",
    "generatedBy",
    # solutions-lock-exceptions.json: a control ID ("1.23"), a kebab-case
    # solution slug, and a fixed direction enum. Never narrative (issue #322).
    "control",
    "solution",
    "direction",
    # Admin role tokens (kebab-case enum values, never narrative)
    "azure-admin",
    "compliance-admin",
    "global-reader",
    "log-analytics-reader",
    "m365-admin",
    "power-platform-admin",
    "records-management-admin",
    "security-admin",
    "sharepoint-admin",
    "teams-admin",
})

# ---------------------------------------------------------------------------
# Reuse the rich line-context tracker + skip predicate from the companion
# canonicalize script. Single source of truth for the carve-out logic.
# ---------------------------------------------------------------------------

sys.path.insert(0, str(Path(__file__).resolve().parent))
from canonicalize_regulatory_naming import (  # noqa: E402, I001
    SKIP_DIR_PARTS,
    iter_lines as iter_line_contexts,
    line_is_skip_eligible,
)


def gather_watched_paths() -> list[Path]:
    """Return every .md under docs/ except local-only screenshot checklists."""
    out: list[Path] = []
    for path in sorted(DOCS_ROOT.rglob("*.md")):
        rel_parts = path.relative_to(DOCS_ROOT).parts
        if any(part in SKIP_DIR_PARTS for part in rel_parts):
            continue
        out.append(path)
    return out


def gather_watched_json_paths() -> list[Path]:
    """Return every .json under assessment/data/ (AS22 — customer-facing
    SPA prose lives here and is rendered verbatim into agenda exports)."""
    if not ASSESSMENT_DATA_ROOT.is_dir():
        return []
    return sorted(ASSESSMENT_DATA_ROOT.rglob("*.json"))


# ---------------------------------------------------------------------------
# Regex library (unchanged from AS3'b — these are the validation predicates)
# ---------------------------------------------------------------------------

# H2 sections whose nearest header matches this pattern are skipped (covered
# by the canonicalize tracker too — keep here for unit-test parametrization).
HISTORY_SECTION_RE = re.compile(
    r"(?i)(version\s+history|release\s+history|changelog|prior\s+version)"
)

# Strip any ``[text](URL)`` Markdown URL destination. The TEXT is scanned by
# the prose check; the URL is scanned by the internal-link check.
MD_LINK_URL_STRIP_RE = re.compile(r"\]\([^)]*\)")

# Markdown link / image destinations to scan for stale slugs.
MD_LINK_DEST_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")

# ``(... formerly ... )`` parenthetical span. Case-insensitive.
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
# ``sr-26-2`` slugs (filenames) are explicitly allowed; the explicit
# pinned anchor ``5-vendor-model-governance-sr-11-7-v`` is also allowed.
STALE_SLUG_RE = re.compile(
    r"(?i)\b(occ[-_]?bulletin[-_]?2011[-_]?12|occ[-_]?2011[-_]?12|"
    r"sr[-_]11[-_]7|occ[-_]sr[-_]11[-_]7)\b"
)
PINNED_ANCHOR_ALLOWLIST = {
    "5-vendor-model-governance-sr-11-7-v",
}


# ---------------------------------------------------------------------------
# Compatibility helpers (preserved for the existing test suite + idiomatic
# usage in any future caller).
# ---------------------------------------------------------------------------


def iter_lines_skipping_fences(text: str):
    """Compatibility shim — yields ``(line_no, line_text, current_h2)``."""
    for ctx in iter_line_contexts(text):
        if ctx.in_fence:
            continue
        yield ctx.line_no, ctx.text, ctx.current_h2


def find_formerly_spans(line: str) -> list[tuple[int, int]]:
    return [m.span() for m in FORMERLY_SPAN_RE.finditer(line)]


def is_inside_any_span(pos: int, spans: list[tuple[int, int]]) -> bool:
    return any(start <= pos < end for start, end in spans)


def strip_link_urls(line: str) -> str:
    return MD_LINK_URL_STRIP_RE.sub("]()", line)


# ---------------------------------------------------------------------------
# Check 1 — rendered prose
# ---------------------------------------------------------------------------


def check_prose(path: Path) -> list[str]:
    """Return failure messages (empty == PASS) for one file."""
    failures: list[str] = []
    text = path.read_text(encoding="utf-8")
    for ctx in iter_line_contexts(text):
        if line_is_skip_eligible(ctx):
            continue
        line = ctx.text
        scan_line = strip_link_urls(line)
        # Always-wrong shorthand.
        for m in SHORTHAND_RE.finditer(scan_line):
            failures.append(
                _diag(
                    path, ctx.line_no, line, m.group(0),
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
                    path, ctx.line_no, line, m.group(0),
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
                    path, ctx.line_no, line, m.group(0),
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


def _stale_slug_is_allowlisted(dest: str, matched: str) -> bool:
    """Return True if the stale-looking slug is on the explicit allowlist."""
    # Pinned anchor: anything ending in #<allowlisted-fragment> is allowed.
    if "#" in dest:
        anchor = dest.split("#", 1)[1]
        if anchor in PINNED_ANCHOR_ALLOWLIST:
            return True
    return False


def check_internal_links(path: Path) -> list[str]:
    """Return failure messages (empty == PASS) for one file."""
    failures: list[str] = []
    text = path.read_text(encoding="utf-8")
    for ctx in iter_line_contexts(text):
        if ctx.in_fence:
            continue
        if ctx.current_h2 and HISTORY_SECTION_RE.search(ctx.current_h2):
            continue
        line = ctx.text
        for m in MD_LINK_DEST_RE.finditer(line):
            dest = m.group(1)
            if is_external_destination(dest):
                continue
            stale = STALE_SLUG_RE.search(dest)
            if stale and not _stale_slug_is_allowlisted(dest, stale.group(0)):
                failures.append(
                    _diag(
                        path, ctx.line_no, line, stale.group(0),
                        f"internal link destination contains stale slug "
                        f"{stale.group(0)!r} (target appears to reference "
                        "a stale-named file or anchor)",
                        "Update the target to the canonical sr-26-2 / "
                        "bulletin-2026-13 form",
                    )
                )
    return failures


# ---------------------------------------------------------------------------
# Check 3 — customer-facing JSON prose fields (AS22)
# ---------------------------------------------------------------------------


def _iter_json_prose_strings(node, path_trail: tuple[str, ...] = ()):
    """Recursively yield ``(json_path, value)`` for every string at a key in
    ``JSON_PROSE_FIELDS``. ``json_path`` is a dotted path for diagnostics
    (``solutions.model-risk-management-automation.description`` etc.)."""
    if isinstance(node, dict):
        for key, value in node.items():
            new_trail = path_trail + (str(key),)
            if isinstance(value, str) and key in JSON_PROSE_FIELDS:
                yield ".".join(new_trail), value
            else:
                yield from _iter_json_prose_strings(value, new_trail)
    elif isinstance(node, list):
        for idx, item in enumerate(node):
            yield from _iter_json_prose_strings(item, path_trail + (f"[{idx}]",))


def check_json_prose(path: Path) -> list[str]:
    """Return failure messages (empty == PASS) for one JSON file.

    Only string values keyed under ``JSON_PROSE_FIELDS`` are scanned.
    Each value is treated as a single rendered line: same regex predicates
    as ``check_prose`` (bare 2011-12 / SR 11-7 outside a formerly-span,
    or any ``OCC/SR`` shorthand). Markdown carve-outs do NOT apply because
    JSON values render as plain text in customer-facing exports.
    """
    failures: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return [f"FAIL: {path}: cannot parse JSON ({exc})"]

    for json_path, value in _iter_json_prose_strings(data):
        scan_line = strip_link_urls(value)
        # Always-wrong shorthand.
        for m in SHORTHAND_RE.finditer(scan_line):
            failures.append(
                _diag_json(
                    path, json_path, value, m.group(0),
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
                _diag_json(
                    path, json_path, value, m.group(0),
                    "bare OCC 2011-12 reference outside a "
                    "'(... formerly ...)' parenthetical",
                    "OCC Bulletin 2026-13 (formerly OCC 2011-12)",
                )
            )
        for m in BARE_SR_RE.finditer(scan_line):
            if is_inside_any_span(m.start(), spans):
                continue
            failures.append(
                _diag_json(
                    path, json_path, value, m.group(0),
                    "bare SR 11-7 reference outside a "
                    "'(... formerly ...)' parenthetical",
                    "Fed SR 26-2 (formerly SR 11-7)",
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


def _diag_json(
    path: Path, json_path: str, value: str, matched: str, why: str, canonical: str,
) -> str:
    """Diagnostic for a JSON prose field (AS22).

    ``json_path`` is a dotted path inside the JSON document
    (``solutions.model-risk-management-automation.description`` etc.) that
    helps maintainers locate the exact key without grepping.
    """
    if path.is_absolute():
        try:
            rel: Path = path.relative_to(REPO_ROOT)
        except ValueError:
            rel = path
    else:
        rel = path
    snippet = value.strip()
    if len(snippet) > 160:
        snippet = snippet[:157] + "..."
    return (
        f"FAIL: {rel} (json: {json_path}): {why}.\n"
        f"      matched: {matched!r}\n"
        f"      value:   {snippet}\n"
        f"      suggested canonical phrasing: {canonical}"
    )


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def run_all_checks() -> tuple[int, list[str], int]:
    """Return ``(failure_count, messages, files_scanned)``."""
    paths = gather_watched_paths()
    json_paths = gather_watched_json_paths()
    messages: list[str] = []
    for path in paths:
        if not path.exists():
            messages.append(f"FAIL: watched file {path} not found")
            continue
        messages.extend(check_prose(path))
        messages.extend(check_internal_links(path))
    for path in json_paths:
        messages.extend(check_json_prose(path))
    return len(messages), messages, len(paths) + len(json_paths)


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
        print("PASS: all OCC/SR references use canonical naming.")
        return 0

    for msg in messages:
        print(msg)
    print()
    print(f"FAIL: {n_failures} drift issue(s) found.")
    return 1 if args.check else 0


if __name__ == "__main__":
    sys.exit(main())
