"""Apply Primary Owner Admin Role blocks to all control documents.

Adds a small metadata block immediately under the `## Prerequisites` heading:

  **Primary Owner Admin Role:** <canonical role>
  **Supporting Roles:** <optional>

Canonical role names come from docs/reference/role-catalog.md.

Run from repo root:
  python scripts/apply_primary_owner_roles.py
"""

from __future__ import annotations

import re
from pathlib import Path


DOCS_DIR = Path("docs")
PILLAR_DIRS = [
    DOCS_DIR / "reference" / "pillar-1-security",
    DOCS_DIR / "reference" / "pillar-2-management",
    DOCS_DIR / "reference" / "pillar-3-reporting",
    DOCS_DIR / "reference" / "pillar-4-sharepoint",
]


ROLE_MAP: dict[str, tuple[str, list[str]]] = {
    # Pillar 1 - Security
    "1.1": ("Power Platform Admin", ["Dataverse System Admin", "Entra Global Admin"]),
    "1.2": ("Power Platform Admin", ["Dataverse System Admin", "Entra App Admin", "SharePoint Site Owner"]),
    "1.3": ("SharePoint Admin", ["SharePoint Site Collection Admin"]),
    "1.4": ("Power Platform Admin", ["Environment Admin"]),
    "1.5": ("Purview Compliance Admin", ["Purview Info Protection Admin"]),
    "1.6": ("Purview Compliance Admin", []),
    "1.7": ("Purview Audit Admin", []),
    "1.8": ("Entra Security Admin", []),
    "1.9": ("Purview Records Manager", []),
    "1.10": ("Purview Communication Compliance Roles", []),
    "1.11": ("Entra Security Admin", []),
    "1.12": ("Purview Insider Risk Roles", []),
    "1.13": ("Purview Info Protection Admin", ["Purview Compliance Admin"]),
    "1.14": ("Power Platform Admin", ["SharePoint Admin", "Purview Compliance Admin"]),
    "1.15": ("Entra Security Admin", ["SharePoint Admin"]),
    "1.16": ("Purview Info Protection Admin", ["SharePoint Admin"]),
    "1.17": ("Purview Compliance Admin", ["Entra Security Admin"]),
    "1.18": ("Power Platform Admin", ["Dataverse System Admin"]),
    "1.19": ("Purview eDiscovery Roles", []),

    # Pillar 2 - Management
    "2.1": ("Power Platform Admin", ["Environment Admin"]),
    "2.2": ("Power Platform Admin", ["Environment Admin"]),
    "2.3": ("Power Platform Admin", ["Pipeline Admin", "Environment Admin"]),
    "2.4": ("Power Platform Admin", ["Environment Admin"]),
    "2.5": ("AI Governance Lead", ["Power Platform Admin", "Compliance Officer"]),
    "2.6": ("AI Governance Lead", ["Compliance Officer", "Power Platform Admin"]),
    "2.7": ("AI Governance Lead", ["Compliance Officer"]),
    "2.8": ("Power Platform Admin", ["Dataverse System Admin", "Entra Privileged Role Admin"]),
    "2.9": ("Power Platform Admin", []),
    "2.10": ("Power Platform Admin", []),
    "2.11": ("AI Governance Lead", ["Compliance Officer"]),
    "2.12": ("Compliance Officer", ["AI Governance Lead"]),
    "2.13": ("Compliance Officer", ["SharePoint Admin", "Purview Records Manager"]),
    "2.14": ("AI Governance Lead", ["Compliance Officer"]),
    "2.15": ("Power Platform Admin", ["Environment Admin"]),

    # Pillar 3 - Reporting
    "3.1": ("Power Platform Admin", ["Entra Global Reader"]),
    "3.2": ("Power Platform Admin", []),
    "3.3": ("Compliance Officer", ["Power Platform Admin", "SharePoint Site Owner"]),
    "3.4": ("Entra Security Admin", ["Compliance Officer"]),
    "3.5": ("Power Platform Admin", []),
    "3.6": ("Power Platform Admin", ["Dataverse System Admin"]),
    "3.7": ("Power Platform Admin", []),
    "3.8": ("Power Platform Admin", []),
    "3.9": ("Entra Security Admin", []),

    # Pillar 4 - SharePoint
    "4.1": ("SharePoint Admin", ["SharePoint Site Collection Admin"]),
    "4.2": ("SharePoint Admin", ["Entra Identity Governance Admin", "SharePoint Site Collection Admin"]),
    "4.3": ("SharePoint Admin", ["Purview Records Manager", "Purview Compliance Admin"]),
    "4.4": ("SharePoint Admin", ["SharePoint Site Collection Admin"]),
    "4.5": ("SharePoint Admin", []),
}


CONTROL_ID_RE = re.compile(r"\*\*Control ID:\*\*\s*(\d+\.\d+)")


def iter_control_files() -> list[Path]:
    files: list[Path] = []
    for pillar_dir in PILLAR_DIRS:
        if not pillar_dir.exists():
            continue
        for path in pillar_dir.glob("*.md"):
            if path.name.lower() == "index.md":
                continue
            files.append(path)
    return sorted(files)


def get_control_id(text: str) -> str | None:
    m = CONTROL_ID_RE.search(text)
    if m:
        return m.group(1).strip()
    # Fallback: header like "# Control 2.4: ..."
    m2 = re.search(r"^#\s*Control\s+(\d+\.\d+)\b", text, flags=re.MULTILINE)
    if m2:
        return m2.group(1).strip()
    return None


def has_primary_owner_block(text: str) -> bool:
    return "**Primary Owner Admin Role:**" in text


def insert_primary_owner_block(text: str, primary: str, supporting: list[str]) -> str:
    lines = text.splitlines(keepends=True)

    for i, line in enumerate(lines):
        if line.strip() == "## Prerequisites":
            # Insert after this heading and any immediate blank line(s)
            j = i + 1
            if j < len(lines) and lines[j].strip() == "":
                j += 1

            supporting_str = ", ".join(supporting) if supporting else "None"
            block = (
                f"**Primary Owner Admin Role:** {primary}  \n"
                f"**Supporting Roles:** {supporting_str}\n\n"
            )
            lines.insert(j, block)
            return "".join(lines)

    return text


def main() -> int:
    files = iter_control_files()
    changed = 0
    skipped = 0

    for path in files:
        text = path.read_text(encoding="utf-8")
        if has_primary_owner_block(text):
            skipped += 1
            continue

        cid = get_control_id(text)
        if not cid or cid not in ROLE_MAP:
            # If we cannot identify it, leave it unchanged.
            skipped += 1
            continue

        primary, supporting = ROLE_MAP[cid]
        updated = insert_primary_owner_block(text, primary, supporting)
        if updated != text:
            path.write_text(updated, encoding="utf-8", newline="\n")
            changed += 1
            print(f"UPDATED: {path.as_posix()} -> {cid}")
        else:
            skipped += 1

    print(f"\nDone. Updated {changed} files. Skipped {skipped}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
