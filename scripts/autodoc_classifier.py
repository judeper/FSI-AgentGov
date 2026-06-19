#!/usr/bin/env python3
"""
Deterministic, fail-closed routing classifier for the autonomous Learn Monitor
documentation pipeline (Stage 1).

Given a Learn Monitor change report (``reports/monitoring/learn-changes-*.md``),
this decides, for each detected change, whether it is:

  * ``route = "autodraft"`` -> mechanically safe for an agent to DRAFT a
                               documentation edit (a human still merges at Stage 1).
  * ``route = "human"``     -> must be analyzed by a human; no agent draft.

and, separately, whether the change is ``automerge_eligible`` -- a redirect-only
Stage 2 gate for now. Content changes are never auto-merge-eligible until a
future scoped Stage 2 mechanism is added.

DESIGN PRINCIPLES (from the June 2026 autodoc council review)
-------------------------------------------------------------
* **Deterministic.** No LLM. The monitor's own CRITICAL/HIGH/MEDIUM tier is noisy
  (it has mislabelled content rewrites as "Deprecation notice"), so this classifier
  applies its OWN safety gates to the actual diff content rather than trusting the
  tier.
* **Fail-closed.** The default is ``route="human"`` / ``automerge_eligible=False``.
  Only narrow, mechanically-verifiable changes are promoted to ``autodraft``.
* **Escalation tripwires mirror CONTRIBUTING.md.** Regulatory/compliance/policy
  language, dates/durations/SKUs, deprecations, overclaim language, and any edit to
  *existing* control prose are never auto-eligible -- they always route to a human.

The module is pure-stdlib and offline; it is unit-tested against the real report
fixtures in ``reports/monitoring/``.

Usage
-----
    python scripts/autodoc_classifier.py [REPORT.md] [--json OUT.json] [--quiet]

If REPORT is omitted, the most recent ``reports/monitoring/learn-changes-*.md`` is
used. A machine-readable routing artifact is written to
``reports/monitoring/autodoc-routing-<date>.json`` (or ``--json`` path) for the
Stage 1 routing workflow to consume.

Exit code is always 0 (this tool is advisory). The structured output -- not an exit
code -- is the contract.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
REPORTS_DIR = PROJECT_ROOT / "reports" / "monitoring"

# Handle Windows console encoding for the report's emoji/box-drawing characters.
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):  # pragma: no cover - older interpreters
        pass


# ---------------------------------------------------------------------------
# Sensitive-token pattern groups
#
# Any match of a HARD-HUMAN group in the *added* text of a change forces
# ``route="human"``. These mirror the framework's "never auto-edit regulatory /
# compliance content" rule (CONTRIBUTING.md) and the council's never-auto-merge
# token rule (numbers, dates, durations, SKUs, citations, hedge words).
# ---------------------------------------------------------------------------
_MONTH_PATTERN = (
    r"\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
    r"Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|"
    r"Dec(?:ember)?)(?:\.)?(?:\s+\d{1,2},?\s+\d{4}|\s+\d{4})?\b"
)
_NUMBER_WORD_PATTERN = (
    r"(?:zero|one|two|three|four|five|six|seven|eight|nine|ten|eleven|"
    r"twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|"
    r"nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|"
    r"hundred|thousand)"
)
_NUMBER_WORD_SEQUENCE = rf"{_NUMBER_WORD_PATTERN}(?:[\s-]+{_NUMBER_WORD_PATTERN})*"
_TIME_UNIT_PATTERN = r"(?:day|week|month|quarter|year|hour|minute)s?"
_FREQUENCY_PATTERN = (
    r"(?:annually|biannually|semi-?annually|quarterly|monthly|weekly|daily)"
)
_RETENTION_STEM_PATTERN = (
    r"(?:retain(?:ed|ing|s)?|retention|archiv\w*|preserv\w*|disposition)"
)

HARD_HUMAN_PATTERNS: dict[str, str] = {
    "regulatory_citation": (
        r"\b(?:FINRA|SEC|SOX|GLBA|OCC|CFTC|FedRAMP|HIPAA|CCPA|GDPR)\b"
        r"|\bPCI[\s-]?DSS\b|\bNIST(?:[\s-]?SP)?[\s-]?\d[\d-]*\b"
        r"|\bSOC[\s-]?2\b|\bISO(?:\s*/\s*IEC|[\s-]IEC)?[\s-]?27001\b"
        r"|\b17a-\d|\bSR\s*\d{2}-\d|\bBulletin\s+\d{4}-\d"
        r"|\bRule\s+\d|\bReg(?:ulation)?[\s-]+[A-Z]{1,3}(?:-[A-Z]{1,3})?\b"
        r"|\b\d+\s*CFR\b|\bFederal\s+Reserve\b"
    ),
    "date_or_deadline": (
        _MONTH_PATTERN
        + r"|\b\d{4}-\d{2}-\d{2}\b"      # ISO date
        r"|\b\d{1,2}/\d{1,2}/\d{2,4}\b"  # numeric date
        r"|\bQ[1-4]\s*\d{4}\b"           # quarter
        r"|\b(?:deadline|effective\s+date|sunset|end\s+of\s+(?:life|support))\b"
    ),
    "duration_or_retention": (
        rf"\b\d+\s*{_TIME_UNIT_PATTERN}\b"
        rf"|\b\d+\s*[ymwd]\b"
        rf"|\b{_NUMBER_WORD_SEQUENCE}(?:\s*\(\s*\d+\s*\))?[\s-]+{_TIME_UNIT_PATTERN}\b"
        rf"|\ba\s+{_TIME_UNIT_PATTERN}\b"
        rf"|\bhalf\s+a\s+{_TIME_UNIT_PATTERN}\b"
        rf"|\b{_FREQUENCY_PATTERN}\b"
        rf"|\b{_RETENTION_STEM_PATTERN}\b|\blegal\s+hold\b"
    ),
    "license_sku": (
        r"\b[AEFGP][1-5]\b|\bSKU\b|\blicens(?:e|ing)\b|\badd-?on\b"
        r"|\bpremium\s+capacit"
    ),
    "deprecation": (
        r"\bdeprecat|\bretir(?:e|ed|ing|ement)\b|\bno\s+longer\b|\bremoved\b"
        r"|\bbreaking\s+change\b|\bmigration\s+required\b"
    ),
    "policy_language": (
        r"\bmust\b|\brequired\b|\bprohibited\b|\bshall\b|\bmandatory\b"
        r"|\bcompliance\b|\baudit\b|\beDiscovery\b|\bconsent\b|\bprivacy\b"
    ),
    "compliance_surface": (
        r"\bDLP\b|\bdata\s+loss\s+prevention\b|\beDiscovery\b|\bretention\b"
        r"|\bsensitivity\s+labels?\b|\binformation\s+barriers?\b|\blegal\s+hold\b"
        r"|\bencryption\b|\baudit\s+logs?\b|\bprivacy\b|\bPII\b|\bsupervision\b"
        r"|\binsider\s+risk\b"
    ),
    "overclaim": (
        r"\bguarantee|\bensures?\s+compliance\b|\beliminat|\bwill\s+prevent\b"
        r"|\b100\s*%|\bfully\s+compliant\b"
    ),
}

KNOWN_TIERS = {"CRITICAL", "HIGH", "MEDIUM", "NOISE"}

_COMPILED_HARD = {k: re.compile(v, re.IGNORECASE) for k, v in HARD_HUMAN_PATTERNS.items()}


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------
@dataclass
class Change:
    topic: str
    url: str
    section: str = ""
    classification: str = ""
    reason: str = ""
    affected_controls: list = field(default_factory=list)  # list[str] of control IDs
    affected_playbooks: list = field(default_factory=list)  # list[str] of file paths
    diff_text: str = ""
    kind: str = "content"  # "content" or "redirect"


@dataclass
class RoutingDecision:
    topic: str
    url: str
    classification: str
    kind: str
    route: str                     # "autodraft" | "human"
    automerge_eligible: bool
    additive_only: bool
    affects_control: bool
    affected_controls: list
    sensitive_categories: list     # which HARD_HUMAN groups matched
    reasons: list                  # human-readable explanation of the decision


# ---------------------------------------------------------------------------
# Diff helpers
# ---------------------------------------------------------------------------
def added_lines(diff_text: str) -> list[str]:
    """Return the content of added (``+``) diff lines, excluding the ``+++`` header."""
    out = []
    for line in diff_text.splitlines():
        if line.startswith("+") and not line.startswith("+++"):
            out.append(line[1:])
    return out


def removed_lines(diff_text: str) -> list[str]:
    """Return removed (``-``) diff lines with content, excluding the ``---`` header."""
    out = []
    for line in diff_text.splitlines():
        if line.startswith("-") and not line.startswith("---"):
            content = line[1:].strip()
            if content:
                out.append(content)
    return out


def is_additive_only(diff_text: str) -> bool:
    """True when the diff only adds content (no existing prose is removed/edited)."""
    if not diff_text.strip():
        return False
    return len(removed_lines(diff_text)) == 0 and len(added_lines(diff_text)) > 0


def match_sensitive(text: str) -> dict[str, list]:
    """Return {category: [matched snippets]} for every HARD_HUMAN group that hits."""
    hits: dict[str, list] = {}
    for category, pattern in _COMPILED_HARD.items():
        found = pattern.findall(text)
        if found:
            # findall may return tuples when the regex has groups; normalise to str.
            flat = []
            for f in found:
                if isinstance(f, tuple):
                    f = next((p for p in f if p), "")
                if f:
                    flat.append(f)
            hits[category] = sorted(set(flat))[:5]
    return hits


# ---------------------------------------------------------------------------
# Classification (the core, fail-closed decision)
# ---------------------------------------------------------------------------
def classify_change(change: Change) -> RoutingDecision:
    reasons: list[str] = []
    added = "\n".join(added_lines(change.diff_text))
    additive = is_additive_only(change.diff_text)
    affects_control = bool(change.affected_controls)
    has_diff = bool(change.diff_text.strip())
    tier = change.classification.strip().upper()

    # URL redirects are a pure URL-table update with no prose. They remain an
    # explicitly allowlisted unattended-merge special case.
    if change.kind == "redirect":
        return RoutingDecision(
            topic=change.topic, url=change.url, classification="REDIRECT",
            kind="redirect", route="autodraft", automerge_eligible=True,
            additive_only=True, affects_control=False, affected_controls=[],
            sensitive_categories=[],
            reasons=["URL redirect: update microsoft-learn-urls.md (no prose change)"],
        )

    sensitive = match_sensitive(added)

    # --- Routing gates (fail-closed: promote only when every allowlist gate passes) ---
    route = "human"
    if not has_diff:
        reasons.append("missing diff block; summary-only or unparsable change")
    if not additive:
        reasons.append("not additive-only")
    if affects_control:
        reasons.append("affects a control/compliance file")
    if tier not in KNOWN_TIERS:
        reasons.append("missing or unknown classification tier")
    elif tier == "CRITICAL":
        reasons.append("monitor classified the change CRITICAL")
    if sensitive:
        reasons.append(
            "sensitive content in additions: " + ", ".join(sorted(sensitive))
        )
    if (
        has_diff
        and additive
        and not affects_control
        and tier in KNOWN_TIERS
        and tier != "CRITICAL"
        and not sensitive
    ):
        route = "autodraft"
        reasons.append("allowlisted additive non-control change with known non-CRITICAL tier")

    automerge = False
    reasons.append(
        "automerge is redirect-only; content changes are never auto-merge-eligible "
        "(Stage 2 will add scoped categories)"
    )

    return RoutingDecision(
        topic=change.topic, url=change.url, classification=tier or change.classification,
        kind=change.kind, route=route, automerge_eligible=automerge,
        additive_only=additive, affects_control=affects_control,
        affected_controls=list(change.affected_controls),
        sensitive_categories=sorted(sensitive.keys()), reasons=reasons,
    )


# ---------------------------------------------------------------------------
# Report parsing
# ---------------------------------------------------------------------------
_SECTION_RE = re.compile(
    r"^### \d+\.\s*(?P<topic>.+?)\n(?P<body>.*?)(?=^### \d+\.\s|^## |\Z)",
    re.DOTALL | re.MULTILINE,
)
_URL_RE = re.compile(r"^\*\*URL:\*\*\s*(\S+)", re.MULTILINE)
_SECTION_FIELD_RE = re.compile(r"^\*\*Section:\*\*\s*(.+)$", re.MULTILINE)
_CLASS_TIER_RE = re.compile(r"^\*\*Classification:\*\*\s*([A-Za-z]+)", re.MULTILINE)
_CLASS_REASON_RE = re.compile(
    r"^\*\*Classification:\*\*\s*[A-Za-z]+\s*(?:\((.*?)\))?",
    re.MULTILINE,
)
_CONTROL_RE = re.compile(r"^- Control (\d+\.\d+):", re.MULTILINE)
_PLAYBOOK_RE = re.compile(r"`([^`]+\.md)`")
_DIFF_RE = re.compile(r"```diff\n(.*?)```", re.DOTALL)
_REDIRECT_ROW_RE = re.compile(
    r"^\|\s*(https?://\S+)\s*\|\s*(https?://\S+)\s*\|", re.MULTILINE
)


def _dedupe_changes_by_url(changes: list[Change]) -> list[Change]:
    """Deduplicate content changes by URL, preferring the record with a diff block."""
    deduped: dict[str, Change] = {}
    for change in changes:
        existing = deduped.get(change.url)
        if existing is None:
            deduped[change.url] = change
            continue
        if change.diff_text.strip() and not existing.diff_text.strip():
            deduped[change.url] = change
    return list(deduped.values())


def parse_report(text: str) -> list[Change]:
    """Parse a Learn Monitor markdown report into Change records."""
    changes: list[Change] = []

    for m in _SECTION_RE.finditer(text):
        topic = m.group("topic").strip()
        body = m.group("body")
        url_m = _URL_RE.search(body)
        if not url_m:
            continue  # not a change block
        class_tier_m = _CLASS_TIER_RE.search(body)
        class_reason_m = _CLASS_REASON_RE.search(body)
        section_m = _SECTION_FIELD_RE.search(body)
        diff_m = _DIFF_RE.search(body)

        # Playbooks come from a dedicated section; controls from "- Control X.Y".
        playbooks = []
        pb_split = body.split("**Affected Playbooks:**")
        if len(pb_split) > 1:
            playbooks = _PLAYBOOK_RE.findall(pb_split[1].split("**What Changed:**")[0])

        changes.append(Change(
            topic=topic,
            url=url_m.group(1).strip(),
            section=section_m.group(1).strip() if section_m else "",
            classification=class_tier_m.group(1).strip().upper() if class_tier_m else "",
            reason=(
                class_reason_m.group(1).strip()
                if class_reason_m and class_reason_m.group(1)
                else ""
            ),
            affected_controls=_CONTROL_RE.findall(body),
            affected_playbooks=playbooks,
            diff_text=diff_m.group(1) if diff_m else "",
            kind="content",
        ))

    changes = _dedupe_changes_by_url(changes)

    # URL redirects (a separate table section).
    redirect_block = ""
    if "## URL Redirects Detected" in text:
        redirect_block = text.split("## URL Redirects Detected", 1)[1].split("\n## ", 1)[0]
    for orig, final in _REDIRECT_ROW_RE.findall(redirect_block):
        changes.append(Change(
            topic=f"URL redirect: {orig}", url=orig, classification="REDIRECT",
            reason=f"redirects to {final}", kind="redirect",
        ))

    return changes


def classify_report(text: str) -> list[RoutingDecision]:
    return [classify_change(c) for c in parse_report(text)]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def _latest_report() -> Path | None:
    candidates = sorted(REPORTS_DIR.glob("learn-changes-*.md"))
    return candidates[-1] if candidates else None


def summarize(decisions: list[RoutingDecision]) -> dict:
    return {
        "total": len(decisions),
        "autodraft": sum(1 for d in decisions if d.route == "autodraft"),
        "human": sum(1 for d in decisions if d.route == "human"),
        "automerge_eligible": sum(1 for d in decisions if d.automerge_eligible),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", nargs="?", help="Path to a learn-changes-*.md report")
    parser.add_argument("--json", dest="json_out", help="Where to write routing JSON")
    parser.add_argument("--quiet", action="store_true", help="Suppress table output")
    args = parser.parse_args(argv)

    report_path = Path(args.report) if args.report else _latest_report()
    if not report_path or not report_path.exists():
        print("No Learn Monitor report found.", file=sys.stderr)
        return 0

    text = report_path.read_text(encoding="utf-8")
    decisions = classify_report(text)
    summary = summarize(decisions)

    if not args.quiet:
        print(f"Report: {report_path.name}")
        print(f"  changes={summary['total']}  autodraft={summary['autodraft']}  "
              f"human={summary['human']}  automerge_eligible={summary['automerge_eligible']}")
        for d in decisions:
            flag = "AUTO" if d.route == "autodraft" else "HUMAN"
            am = " [automerge]" if d.automerge_eligible else ""
            print(f"  [{flag}{am}] {d.classification:<8} {d.topic[:60]}")
            print(f"           {('; '.join(d.reasons))[:110]}")

    out_path = (Path(args.json_out) if args.json_out
                else REPORTS_DIR / f"autodoc-routing-{report_path.stem.split('-', 2)[-1]}.json")
    payload = {
        "report": report_path.name,
        "summary": summary,
        "decisions": [asdict(d) for d in decisions],
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    if not args.quiet:
        print(f"Routing artifact written to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
