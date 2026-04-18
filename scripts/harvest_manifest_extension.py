#!/usr/bin/env python3
"""Harvest additive metadata into ``assessment/manifest/controls.json``.

Reads each control doc referenced by ``source_file`` and derives the new
v1.4 manifest fields where the value can be obtained deterministically.
Anything that requires authoring judgment (e.g., ``yesBar``) is filled
with the literal string ``"TODO: <hint>"``.

The harvest is **additive**: existing fields are never removed and never
overwritten unless the existing value is missing.

Run from the repo root::

    python scripts/harvest_manifest_extension.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "assessment" / "manifest" / "controls.json"

# Regulatory tokens we look for in the "Regulatory Reference" line.
REG_TOKENS = [
    ("FINRA 4511", "FINRA-4511"),
    ("FINRA 3110", "FINRA-3110"),
    ("FINRA 4530", "FINRA-4530"),
    ("FINRA 25-07", "FINRA-25-07"),
    ("Notice 25-07", "FINRA-25-07"),
    ("17a-4", "SEC-17a-4"),
    ("17a-3", "SEC-17a-3"),
    ("Reg S-P", "Reg-S-P"),
    ("Regulation S-P", "Reg-S-P"),
    ("SOX", "SOX-404"),
    ("GLBA", "GLBA"),
    ("OCC 2011-12", "OCC-2011-12"),
    ("OCC 2023-17", "OCC-2023-17"),
    ("OCC Bulletin 2011-12", "OCC-2011-12"),
    ("OCC Bulletin 2023-17", "OCC-2023-17"),
    ("SR 11-7", "Fed-SR-11-7"),
    ("SR 16-11", "Fed-SR-16-11"),
    ("Federal Reserve SR 11-7", "Fed-SR-11-7"),
    ("CFTC 1.31", "CFTC-1.31"),
    ("NIST AI RMF", "NIST-AI-RMF"),
    ("NYDFS", "NYDFS-500"),
    ("HIPAA", "HIPAA"),
    ("PCI", "PCI-DSS"),
    ("NCUA", "NCUA"),
]

# Canonical role-name aliasing for the role-catalog short names.
ROLE_NORMALIZE = {
    "global administrator": "Entra Global Admin",
    "global admin": "Entra Global Admin",
    "entra global admin": "Entra Global Admin",
    "purview compliance admin": "Purview Compliance Admin",
    "compliance administrator": "Purview Compliance Admin",
    "compliance admin": "Purview Compliance Admin",
    "purview admin": "Purview Compliance Admin",
    "power platform admin": "Power Platform Admin",
    "power platform administrator": "Power Platform Admin",
    "power apps admin": "Power Platform Admin",
    "exchange online admin": "Exchange Online Admin",
    "exchange administrator": "Exchange Online Admin",
    "sharepoint admin": "SharePoint Admin",
    "sharepoint administrator": "SharePoint Admin",
    "security administrator": "Security Admin",
    "security admin": "Security Admin",
    "security operations": "Security Operations",
    "soc": "Security Operations",
    "compliance officer": "Compliance Officer",
    "governance lead": "Governance Lead",
    "ai governance lead": "Governance Lead",
    "model risk management": "Model Risk Management",
    "mrm": "Model Risk Management",
}


def slug_from_source_file(source_file: str) -> str | None:
    """Extract the control slug from ``docs/controls/.../<slug>.md``."""
    if not source_file:
        return None
    name = Path(source_file).stem  # strip .md
    return name


def control_doc_url(source_file: str) -> str:
    slug = slug_from_source_file(source_file) or ""
    return f"/controls/{slug}/" if slug else "TODO: control doc URL"


def playbook_url(control_id: str, kind: str) -> str:
    return f"/playbooks/control-implementations/{control_id}/{kind}/"


def derive_zones(checks: list[dict]) -> list[int]:
    zones: set[int] = set()
    for c in checks or []:
        for z in c.get("zone_required", []) or []:
            if isinstance(z, int):
                zones.add(z)
    return sorted(zones) if zones else [1, 2, 3]


def parse_regulatory(doc_text: str) -> list[str]:
    m = re.search(
        r"^\*\*Regulatory Reference:\*\*\s*(.+?)$", doc_text, re.MULTILINE
    )
    if not m:
        return []
    line = m.group(1)
    found: list[str] = []
    for token, tag in REG_TOKENS:
        if token.lower() in line.lower() and tag not in found:
            found.append(tag)
    return found


def parse_roles(doc_text: str) -> list[str]:
    """Pull role names from the Roles & Responsibilities section."""
    sec = re.search(
        r"^##\s+Roles\s*&\s*Responsibilities(.+?)(?=^## |\Z)",
        doc_text,
        re.MULTILINE | re.DOTALL,
    )
    if not sec:
        return []
    body = sec.group(1)
    roles: set[str] = set()
    # Match leading column of any markdown table row, ignoring header/sep rows.
    for line in body.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if not cells:
            continue
        first = cells[0]
        if not first or set(first) <= set("-: "):
            continue
        if first.lower() in ("role", "roles", "admin role", "responsible"):
            continue
        # Sometimes the cell is bolded.
        first_clean = re.sub(r"\*+", "", first).strip()
        canonical = ROLE_NORMALIZE.get(first_clean.lower(), first_clean)
        if canonical and len(canonical) <= 60:
            roles.add(canonical)
    return sorted(roles)


def name_from_title(title: str, control_id: str) -> str:
    # Strip "Control X.Y: " prefix
    m = re.match(rf"^Control\s+{re.escape(control_id)}\s*:\s*(.+)$", title)
    return m.group(1).strip() if m else title


def harvest_one(control: dict[str, Any]) -> dict[str, Any]:
    cid = control["id"]
    src = control.get("source_file", "")
    doc_path = ROOT / src if src else None
    doc_text = ""
    if doc_path and doc_path.exists():
        try:
            doc_text = doc_path.read_text(encoding="utf-8")
        except OSError:
            doc_text = ""

    extension: dict[str, Any] = {}

    # name (deterministic)
    if "name" not in control:
        extension["name"] = name_from_title(control.get("title", ""), cid)

    # zonesApplicable (deterministic from checks)
    if "zonesApplicable" not in control:
        extension["zonesApplicable"] = derive_zones(control.get("checks", []))

    # roles (parsed; falls back to TODO list)
    if "roles" not in control:
        roles = parse_roles(doc_text)
        extension["roles"] = roles or ["TODO: populate from control doc"]

    # regulatory (parsed; empty list permitted)
    if "regulatory" not in control:
        extension["regulatory"] = parse_regulatory(doc_text)

    # priority (author judgment)
    if "priority" not in control:
        extension["priority"] = "TODO: critical|high|medium|low"

    # rating bars (author judgment)
    for key, hint in (
        ("yesBar", "concise pass criteria"),
        ("partialBar", "partial coverage criteria"),
        ("noBar", "fail criteria"),
    ):
        if key not in control:
            extension[key] = f"TODO: {hint}"

    # verifyIn (portal links — author per control)
    if "verifyIn" not in control:
        extension["verifyIn"] = []  # empty, drawer falls back to controlDocUrl

    # verifyPowerShell (author per control; empty string if none)
    if "verifyPowerShell" not in control:
        extension["verifyPowerShell"] = ""

    # evidenceExpected
    if "evidenceExpected" not in control:
        extension["evidenceExpected"] = []

    # controlDocUrl + portalPlaybookUrl (deterministic)
    if "controlDocUrl" not in control:
        extension["controlDocUrl"] = control_doc_url(src)
    if "portalPlaybookUrl" not in control:
        extension["portalPlaybookUrl"] = playbook_url(cid, "portal-walkthrough")

    # collectorField (engine-aware authoring)
    if "collectorField" not in control:
        extension["collectorField"] = ""

    # sectorYesBar — TODO entries permitted per spec
    if "sectorYesBar" not in control:
        extension["sectorYesBar"] = {
            sector: "TODO: sector-specific yes-bar"
            for sector in (
                "bank",
                "broker-dealer",
                "investment-adviser",
                "insurance-carrier",
                "insurance-wholesale",
                "credit-union",
                "holding-company",
                "other",
            )
        }

    # facilitatorNotes
    if "facilitatorNotes" not in control:
        extension["facilitatorNotes"] = {
            "ask": "TODO: facilitator question",
            "followUp": "TODO: follow-up hint",
            "timeBudgetMinutes": 5,
        }

    # solutions (folder-name kebab-case strings, per v1.4 cross-repo contract)
    if "solutions" not in control:
        extension["solutions"] = []

    return extension


def main() -> int:
    if not MANIFEST.exists():
        print(f"ERROR: manifest not found at {MANIFEST}", file=sys.stderr)
        return 2
    controls = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if not isinstance(controls, list):
        print("ERROR: manifest is not a JSON list", file=sys.stderr)
        return 2

    enriched_count = 0
    for ctrl in controls:
        before_keys = set(ctrl.keys())
        ext = harvest_one(ctrl)
        added = {k: v for k, v in ext.items() if k not in before_keys}
        if added:
            ctrl.update(added)
            enriched_count += 1

    MANIFEST.write_text(
        json.dumps(controls, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Enriched {enriched_count} of {len(controls)} controls.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
