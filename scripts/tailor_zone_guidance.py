"""Replace boilerplate Zone-Specific Configuration stubs with tailored guidance.

This is a controlled editorial automation:
- Only replaces the exact boilerplate stub inserted by the refactor script.
- Generates short, control-specific Zone 1/2/3 guidance + rationale.
- Leaves existing, hand-authored Zone guidance untouched.

Run from repo root:
  python scripts/tailor_zone_guidance.py
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


DOCS_DIR = Path("docs")
PILLAR_DIRS = [
    DOCS_DIR / "reference" / "pillar-1-security",
    DOCS_DIR / "reference" / "pillar-2-management",
    DOCS_DIR / "reference" / "pillar-3-reporting",
    DOCS_DIR / "reference" / "pillar-4-sharepoint",
]

ZONE_H3 = "### Zone-Specific Configuration"

BOILERPLATE_BLOCK = (
    "**Zone 1 (Personal Productivity):**\n"
    "- Not required by default; document any exceptions.\n\n"
    "**Zone 2 (Team Collaboration):**\n"
    "- Apply recommended configuration and validate with a pilot group.\n\n"
    "**Zone 3 (Enterprise Managed):**\n"
    "- Apply the strictest configuration and require change control evidence.\n"
)

_BOILERPLATE_NONEMPTY_LINES = [
    "**Zone 1 (Personal Productivity):**",
    "- Not required by default; document any exceptions.",
    "**Zone 2 (Team Collaboration):**",
    "- Apply recommended configuration and validate with a pilot group.",
    "**Zone 3 (Enterprise Managed):**",
    "- Apply the strictest configuration and require change control evidence.",
]


@dataclass
class ControlInfo:
    control_id: str
    title: str


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


def parse_control_info(text: str) -> ControlInfo:
    m = re.search(r"^#\s+Control\s+(\d+\.\d+):\s+(.+?)\s*$", text, flags=re.MULTILINE)
    if not m:
        return ControlInfo(control_id="?", title="Control")
    return ControlInfo(control_id=m.group(1).strip(), title=m.group(2).strip())


def _topic_phrases(title: str) -> dict[str, str]:
    t = title.lower()

    def has(*words: str) -> bool:
        return all(w in t for w in words)

    # Default phrases
    action = f"{title} controls"
    primary = "apply the control"
    evidence = "retain evidence (screenshots/exports/logs)"

    if "data loss prevention" in t or "dlp" in t:
        action = "DLP policies and sensitivity labels"
        primary = "apply DLP to AI locations (Copilot/M365, Copilot Studio) and label-conditioned rules"
        evidence = "retain policy export + test prompts/results"
    elif "conditional access" in t or "mfa" in t:
        action = "Conditional Access and phishing-resistant MFA"
        primary = "enforce strong auth and risk-aware access for admin/maker roles"
        evidence = "retain policy JSON/export + sign-in log samples"
    elif "retention" in t:
        action = "retention policies/labels for SharePoint content"
        primary = "ensure agent knowledge sources follow retention and disposition rules"
        evidence = "retain policy configs + evidence of label/policy assignment"
    elif "access review" in t or "certification" in t or "attestation" in t:
        action = "SharePoint access reviews and certification"
        primary = "run periodic access reviews/attestations for agent knowledge sites"
        evidence = "retain review exports/attestation records"
    elif "environment group" in t or "tier classification" in t:
        action = "environment groups and tier classification"
        primary = "apply zone-aligned rules consistently across environments"
        evidence = "retain rule snapshots + group membership exports"
    elif "business continuity" in t or "disaster recovery" in t:
        action = "business continuity and disaster recovery"
        primary = "define RTO/RPO for critical agents and validate restore procedures"
        evidence = "retain test results + recovery runbooks"
    elif "sensitive information" in t or "sits" in t or "pattern recognition" in t:
        action = "Sensitive Information Types (SITs)"
        primary = "maintain SIT definitions and test detection quality"
        evidence = "retain SIT definitions + test corpus results"
    elif "audit" in t and "logging" in t:
        action = "audit logging"
        primary = "ensure key agent/admin activities are logged and reviewable"
        evidence = "retain audit configuration + sample queries"
    elif "ediscovery" in t:
        action = "eDiscovery"
        primary = "ensure agent interactions/content are discoverable and hold-capable"
        evidence = "retain case settings + sample holds/searches"
    elif "managed environment" in t:
        action = "managed environments"
        primary = "enable managed environment governance controls for shared/production"
        evidence = "retain environment settings exports"
    elif "sentinel" in t:
        action = "SIEM integration (Microsoft Sentinel)"
        primary = "forward and correlate agent/security events for monitoring"
        evidence = "retain connector config + sample alerts"

    return {"action": action, "primary": primary, "evidence": evidence}


def build_zone_block(info: ControlInfo) -> str:
    p = _topic_phrases(info.title)

    primary_phrase = p["primary"].strip()
    if primary_phrase.lower().startswith("apply "):
        primary_phrase = primary_phrase[6:]

    # Safe default posture requested by user: baseline minimum + document exceptions,
    # and keep zones separate from governance levels.
    return (
        f"**Zone 1 (Personal Productivity):**\n"
        f"- Apply a baseline minimum of {p['action']} that impacts tenant-wide safety (where applicable), and document any exceptions for personal agents.\n"
        f"- Avoid expanding scope beyond the user’s own data unless explicitly justified.\n"
        f"- Rationale: reduces risk from personal use while keeping friction low; legal/compliance can tighten later.\n\n"
        f"**Zone 2 (Team Collaboration):**\n"
        f"- Apply {primary_phrase} for shared agents and shared data sources; require an identified owner and an approval trail.\n"
        f"- Validate configuration in a pilot environment before broader rollout; {p['evidence']}.\n"
        f"- Rationale: shared agents increase blast radius; controls must be consistently applied and provable.\n\n"
        f"**Zone 3 (Enterprise Managed):**\n"
        f"- Require the strictest configuration for {p['action']} and enforce it via policy where possible (not manual-only).\n"
        f"- Treat changes as controlled (change ticket + documented testing); {p['evidence']}.\n"
        f"- Rationale: enterprise agents handle the most sensitive content and are the highest audit/regulatory risk.\n"
    )


def replace_zone_stub(text: str, info: ControlInfo) -> tuple[str, bool]:
    # Find the Zone-Specific Configuration section content up to next H2.
    m = re.search(
        r"^###\s+Zone-Specific Configuration\s*$",
        text,
        flags=re.MULTILINE,
    )
    if not m:
        return text, False

    start = m.end()
    after = text[start:]

    next_h2 = re.search(r"^##\s+", after, flags=re.MULTILINE)
    end = start + (next_h2.start() if next_h2 else len(after))

    section_body = text[start:end]

    # Detect the boilerplate even if formatting/blank lines were changed.
    nonempty = [ln.strip() for ln in section_body.splitlines() if ln.strip()]
    if nonempty != _BOILERPLATE_NONEMPTY_LINES:
        return text, False

    new_body = "\n\n" + build_zone_block(info) + "\n"
    updated = text[:start] + new_body + text[end:]
    return updated, True


def main() -> int:
    files = iter_control_files()
    if not files:
        print("No control files found.")
        return 1

    changed = 0
    for path in files:
        raw = path.read_text(encoding="utf-8")
        info = parse_control_info(raw)
        updated, did = replace_zone_stub(raw, info)
        if did and updated != raw:
            path.write_text(updated, encoding="utf-8", newline="\n")
            changed += 1
            print(f"UPDATED: {path.as_posix()}")

    print(f"\nDone. Updated {changed}/{len(files)} control files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
