#!/usr/bin/env python3
"""Generate the Control Explorer data file for the FSI-AgentGov docs site.

This standalone generator reads the authoritative assessment manifest plus the
per-control markdown headers and emits a clean, faceted JSON document consumed
by ``docs/javascripts/control-explorer.js``.

Data sources (in priority order):
  1. ``assessment/manifest/controls.json`` -- authoritative for id, title,
     pillar, zone applicability, normalized regulatory codes, roles, automation,
     solutions, and the published control-page URL (``controlDocUrl``).
  2. The per-control markdown files referenced by each manifest entry's
     ``source_file`` -- used to learn the header-metadata format and to
     back-fill regulation facets for any control missing them in the manifest
     (parsed from the ``**Regulatory Reference:**`` header line). The
     ``**Governance Levels:**`` header is read as a cross-check only.
  3. ``docs/controls/CONTROL-INDEX.md`` -- read to confirm the control count and
     titles line up with the manifest (cross-check only; no data invented).

Nothing is fabricated: when a facet cannot be reliably derived for a control it
is recorded as ``unspecified`` (automation) or an empty list (regulations,
roles, solutions), and the run summary reports every such case.

Output: ``docs/javascripts/control-explorer-data.json`` with the shape::

    { "generatedAt": "<ISO-8601 UTC>", "count": 79, "controls": [ ... ] }

The script is idempotent and prints a summary on each run.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST = REPO_ROOT / "assessment" / "manifest" / "controls.json"
CONTROL_INDEX = REPO_ROOT / "docs" / "controls" / "CONTROL-INDEX.md"
OUTPUT = REPO_ROOT / "docs" / "javascripts" / "control-explorer-data.json"
PLAYBOOKS_ROOT = REPO_ROOT / "docs" / "playbooks" / "control-implementations"

EXPECTED_COUNT = 79

# Map manifest automation values -> human-facing facet labels.
AUTOMATION_LABELS = {
    "full": "Automatable",
    "partial": "Partial",
    "manual": "Manual",
}

# Pure table-parse artifacts that are not real administrator roles.
ROLE_ARTIFACTS = {"Role", "Role group", "Reviewer"}

# Ordered regex rules to normalize a free-text "Regulatory Reference" header
# into facet codes, used ONLY as a fallback when the manifest has no
# regulatory codes for a control. Patterns are intentionally conservative.
REG_FALLBACK_RULES: list[tuple[str, str]] = [
    (r"FINRA\s+(?:Regulatory Notice|RN)\s*(\d{2}-\d{2})", r"FINRA-\1"),
    (r"FINRA\s+Rule\s+(\d{4})", r"FINRA-\1"),
    (r"SEC\s+Marketing\s+Rule", "SEC-Marketing-Rule"),
    (r"Rule\s+17a-3", "SEC-17a-3"),
    (r"Rule\s+17a-4", "SEC-17a-4"),
    (r"FTC\s+Act\s+Section\s+5", "FTC-Act-5"),
    (r"State\s+Unfair\s+Trade\s+Practices", "State-UTP"),
    (r"SOX", "SOX-404"),
    (r"GLBA", "GLBA"),
    (r"Reg(?:ulation)?\s+S-?P", "Reg-S-P"),
    (r"NYDFS", "NYDFS-500"),
    (r"CFTC", "CFTC-1.31"),
    (r"NIST", "NIST-AI-RMF"),
]

PAREN_RE = re.compile(r"\s*\(.*?\)\s*")
REG_HEADER_RE = re.compile(r"\*\*Regulatory Reference:\*\*\s*(.+)")
GOV_HEADER_RE = re.compile(r"\*\*Governance Levels:\*\*\s*(.+)")
OBJECTIVE_SECTION_RE = re.compile(
    r"^##\s+Objective\s*$\n(?P<body>.*?)(?=^##\s+|\Z)",
    flags=re.MULTILINE | re.DOTALL,
)
H1_RE = re.compile(r"^#\s+(.+?)\s*$", flags=re.MULTILINE)

WORKLOAD_SIGNAL_RULES: list[tuple[str, re.Pattern[str]]] = [
    ("Purview", re.compile(r"\b(?:Microsoft\s+)?Purview\b", flags=re.IGNORECASE)),
    ("Copilot Studio", re.compile(r"\b(?:Microsoft\s+)?Copilot Studio\b", flags=re.IGNORECASE)),
    ("Power Platform", re.compile(r"\bPower Platform\b", flags=re.IGNORECASE)),
    (
        "Microsoft 365 Copilot",
        re.compile(
            r"\b(?:Microsoft\s*365|M365)\s+Copilot\b|\bCopilot for Microsoft 365\b",
            flags=re.IGNORECASE,
        ),
    ),
]

PLAYBOOK_NAME_BY_STEM = {
    "portal-walkthrough": "Portal Walkthrough",
    "powershell-setup": "PowerShell Setup",
    "verification-testing": "Verification & Testing",
    "troubleshooting": "Troubleshooting",
}

PLAYBOOK_ORDER = {
    "portal-walkthrough": 0,
    "powershell-setup": 1,
    "verification-testing": 2,
    "troubleshooting": 3,
}


def clean_role(role: str) -> str:
    """Strip parenthetical annotations from a role name."""
    return PAREN_RE.sub(" ", role).strip()


def parse_reg_header(text: str) -> str | None:
    m = REG_HEADER_RE.search(text)
    return m.group(1).strip().rstrip("<br>").strip() if m else None


def parse_gov_header(text: str) -> str | None:
    m = GOV_HEADER_RE.search(text)
    return m.group(1).strip().rstrip("<br>").strip() if m else None


def governance_levels_from_header(header: str) -> list[str]:
    levels: list[str] = []
    for part in re.split(r"/|,", header):
        level = part.strip()
        if level and level not in levels:
            levels.append(level)
    return levels


def regs_from_header(header: str) -> list[str]:
    """Derive normalized regulation facet codes from a header string."""
    found: list[str] = []
    for pattern, repl in REG_FALLBACK_RULES:
        for m in re.finditer(pattern, header, flags=re.IGNORECASE):
            code = m.expand(repl)
            if code not in found:
                found.append(code)
    return found


def objective_from_markdown(text: str) -> str:
    m = OBJECTIVE_SECTION_RE.search(text)
    if not m:
        return ""
    body = m.group("body")
    lines: list[str] = []
    for raw in body.splitlines():
        line = raw.strip()
        if not line or line == "---":
            continue
        if line.startswith("!!! "):
            continue
        lines.append(line)
    return " ".join(lines)


def workloads_for_control(pillar: int | str | None, title: str, objective: str) -> list[str]:
    workloads: list[str] = []
    if str(pillar) == "4":
        workloads.append("SharePoint")
    haystack = f"{title}\n{objective}"
    for label, pattern in WORKLOAD_SIGNAL_RULES:
        if pattern.search(haystack) and label not in workloads:
            workloads.append(label)
    if not workloads:
        workloads.append("unspecified")
    return workloads


def heading_from_markdown(text: str) -> str | None:
    m = H1_RE.search(text)
    return m.group(1).strip() if m else None


def title_from_stem(stem: str) -> str:
    return stem.replace("-", " ").title().replace("Powershell", "PowerShell")


def playbook_name(path: Path) -> str:
    mapped = PLAYBOOK_NAME_BY_STEM.get(path.stem)
    if mapped:
        return mapped
    heading = heading_from_markdown(path.read_text(encoding="utf-8"))
    if heading:
        heading = re.sub(r"^Control\s+\d+\.\d+:\s*", "", heading).strip()
        heading = re.sub(r":\s*Control\s+\d+\.\d+.*$", "", heading).strip()
        if heading:
            return heading
    return title_from_stem(path.stem)


def control_playbooks(control_id: str) -> list[dict[str, str]]:
    root = PLAYBOOKS_ROOT / control_id
    if not root.exists() or not root.is_dir():
        return []
    md_files = sorted(
        [p for p in root.glob("*.md") if p.name.lower() != "index.md"],
        key=lambda p: (PLAYBOOK_ORDER.get(p.stem, 99), p.stem),
    )
    return [
        {
            "name": playbook_name(p),
            "url": f"playbooks/control-implementations/{control_id}/{p.stem}/",
        }
        for p in md_files
    ]


def load_manifest() -> list[dict]:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise SystemExit(f"Unexpected manifest shape: {type(data)!r}")
    return data


def index_ids() -> set[str]:
    """Extract control IDs from CONTROL-INDEX.md table rows for cross-check."""
    if not CONTROL_INDEX.exists():
        return set()
    ids: set[str] = set()
    for line in CONTROL_INDEX.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\|\s*(\d+\.\d+)\s*\|", line)
        if m:
            ids.add(m.group(1))
    return ids


def build() -> tuple[dict, dict]:
    manifest = load_manifest()
    idx_ids = index_ids()

    controls: list[dict] = []
    notes = {
        "reg_fallback": [],   # controls whose regs came from markdown header
        "no_regs": [],        # controls with no regulations at all
        "automation_unspecified": [],
        "missing_source_file": [],
        "index_mismatch": [],
        "missing_gov_levels": [],
        "workload_unspecified": [],
    }

    for c in manifest:
        cid = c["id"]
        name = c.get("name") or c.get("title") or cid
        pillar = c.get("pillar")
        pillar_name = c.get("pillar_name") or ""

        # URL: manifest controlDocUrl is a root-relative path; store it without
        # the leading slash so the JS can prefix the deployed site base path.
        url = (c.get("controlDocUrl") or "").lstrip("/")

        zones = sorted(c.get("zonesApplicable") or [])

        # Regulations: manifest codes are authoritative; fall back to the
        # markdown header only when the manifest has none.
        regulations = list(c.get("regulatory") or [])
        src = c.get("source_file")
        src_path = REPO_ROOT / src if src else None
        src_text = ""
        if src_path and src_path.exists():
            src_text = src_path.read_text(encoding="utf-8")
        if not regulations and src_text:
            header = parse_reg_header(src_text)
            if header:
                regulations = regs_from_header(header)
                if regulations:
                    notes["reg_fallback"].append(cid)
        if not regulations:
            notes["no_regs"].append(cid)
        if src and not (src_path and src_path.exists()):
            notes["missing_source_file"].append(cid)

        gov_header = parse_gov_header(src_text) if src_text else None
        governance_levels = (
            governance_levels_from_header(gov_header) if gov_header else []
        )
        if not governance_levels:
            notes["missing_gov_levels"].append(cid)

        objective = objective_from_markdown(src_text) if src_text else ""
        workload = workloads_for_control(pillar, name, objective)
        if workload == ["unspecified"]:
            notes["workload_unspecified"].append(cid)

        roles = []
        for r in c.get("roles") or []:
            cr = clean_role(r)
            if cr and cr not in ROLE_ARTIFACTS and cr not in roles:
                roles.append(cr)

        auto_raw = c.get("automation")
        automation = AUTOMATION_LABELS.get(auto_raw, "unspecified")
        if automation == "unspecified":
            notes["automation_unspecified"].append(cid)

        solutions = list(c.get("solutions") or [])
        playbooks = control_playbooks(cid)

        if idx_ids and cid not in idx_ids:
            notes["index_mismatch"].append(cid)

        # Primary owner: first non-artifact role from manifest roles list (pre-cleanup).
        primary_owner = ""
        for r in (c.get("roles") or []):
            cr = clean_role(r)
            if cr and cr not in ROLE_ARTIFACTS:
                primary_owner = cr
                break

        # Effort estimate derived from automation classification.
        EFFORT_MAP = {
            "full": "Low effort",
            "partial": "Medium effort",
            "manual": "Higher effort",
        }
        effort_level = EFFORT_MAP.get(auto_raw or "", "")

        # Primary playbook URL: the portal-walkthrough (first in ordered list).
        primary_playbook = playbooks[0] if playbooks else None

        controls.append({
            "id": cid,
            "title": name,
            "pillar": pillar,
            "pillarName": pillar_name,
            "url": url,
            "objective": objective,
            "primaryOwner": primary_owner,
            "effortLevel": effort_level,
            "primaryPlaybook": primary_playbook,
            "workload": workload,
            "governanceLevels": governance_levels,
            "zones": zones,
            "regulations": sorted(regulations),
            "roles": sorted(roles),
            "automation": automation,
            "solutions": sorted(solutions),
            "playbooks": playbooks,
        })

    # Stable sort by numeric (pillar, control) order.
    controls.sort(key=lambda x: tuple(int(p) for p in x["id"].split(".")))

    doc = {
        "generatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "count": len(controls),
        "controls": controls,
    }
    return doc, notes


def main() -> int:
    doc, notes = build()
    count = doc["count"]

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n",
                      encoding="utf-8")

    # ----- summary -----
    print("Control Explorer data generator")
    print(f"  manifest : {MANIFEST.relative_to(REPO_ROOT)}")
    print(f"  output   : {OUTPUT.relative_to(REPO_ROOT)}")
    print(f"  controls : {count} (expected {EXPECTED_COUNT})")

    all_regs = sorted({r for c in doc["controls"] for r in c["regulations"]})
    all_roles = sorted({r for c in doc["controls"] for r in c["roles"]})
    all_sol = sorted({s for c in doc["controls"] for s in c["solutions"]})
    all_workloads = sorted({w for c in doc["controls"] for w in c["workload"]})
    all_gov_levels = sorted(
        {g for c in doc["controls"] for g in c["governanceLevels"]}
    )
    all_playbooks = sum(len(c["playbooks"]) for c in doc["controls"])
    autos = {}
    for c in doc["controls"]:
        autos[c["automation"]] = autos.get(c["automation"], 0) + 1
    print(f"  facets   : regulations={len(all_regs)} roles={len(all_roles)} "
          f"solutions={len(all_sol)} automation={autos} "
          f"workloads={len(all_workloads)} governance_levels={len(all_gov_levels)} "
          f"playbooks={all_playbooks}")

    if notes["reg_fallback"]:
        print(f"  reg fallback (parsed from markdown header): "
              f"{notes['reg_fallback']}")
    if notes["no_regs"]:
        print(f"  WARN no regulations: {notes['no_regs']}")
    if notes["automation_unspecified"]:
        print(f"  automation unspecified: {notes['automation_unspecified']}")
    if notes["missing_source_file"]:
        print(f"  WARN missing source_file: {notes['missing_source_file']}")
    if notes["index_mismatch"]:
        print(f"  WARN not in CONTROL-INDEX: {notes['index_mismatch']}")
    if notes["missing_gov_levels"]:
        print(f"  WARN missing governance levels: {notes['missing_gov_levels']}")
    if notes["workload_unspecified"]:
        print(f"  workload unspecified: {notes['workload_unspecified']}")

    if count != EXPECTED_COUNT:
        print(f"ERROR: expected {EXPECTED_COUNT} controls, got {count}",
              file=sys.stderr)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
