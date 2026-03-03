#!/usr/bin/env python3
"""
Extract assessment data from FSI-AgentGov control markdown files.

Generates docs/javascripts/assessment-data.json for the Governance Readiness
Assessment Tool. Parses all 71 controls to extract metadata, verification
criteria, configuration points, zone requirements, and role assignments.

Also parses:
- docs/reference/regulatory-mappings.md   → regulation-to-control matrix
- docs/framework/adoption-roadmap.md      → phase mapping + effort estimates
- docs/downloads/index.md                 → role-to-control assignments

Usage:
    python scripts/extract_assessment_data.py
    python scripts/extract_assessment_data.py --verbose
    python scripts/extract_assessment_data.py --output path/to/output.json
"""

import json
import os
import re
import sys
from pathlib import Path

# Handle Windows encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Paths
SCRIPT_DIR = Path(__file__).parent
BASE_DIR = SCRIPT_DIR.parent
DOCS_DIR = BASE_DIR / "docs"
CONTROLS_DIR = DOCS_DIR / "controls"
OUTPUT_PATH = DOCS_DIR / "javascripts" / "assessment-data.json"

# Reuse PILLARS from compile_researcher_package.py
PILLARS = {
    1: {
        "name": "Security",
        "folder": "pillar-1-security",
        "controls": list(range(1, 29)),  # 1.1 to 1.28 (28 controls)
    },
    2: {
        "name": "Management",
        "folder": "pillar-2-management",
        "controls": list(range(1, 25)),  # 2.1 to 2.24 (24 controls)
    },
    3: {
        "name": "Reporting",
        "folder": "pillar-3-reporting",
        "controls": list(range(1, 13)),  # 3.1 to 3.12 (12 controls)
    },
    4: {
        "name": "SharePoint",
        "folder": "pillar-4-sharepoint",
        "controls": list(range(1, 8)),  # 4.1 to 4.7 (7 controls)
    },
}

# Solution-to-control mappings (from docs/framework/solutions-integration.md)
SOLUTION_CONTROLS = {
    "Environment Lifecycle Management": ["2.1", "2.2", "2.15"],
    "Message Center Monitor": ["2.3", "2.10"],
    "Pipeline Governance Cleanup": ["2.3"],
    "Deny Event Correlation Report": ["1.5", "1.7", "3.4"],
    "FINRA Supervision Workflow": ["2.12", "1.10", "1.7"],
    "Conditional Access Automation": ["1.11", "1.23", "1.18"],
    "Compliance Dashboard": ["3.3", "3.1", "3.2"],
    "Segregation Detector": ["2.8", "2.1", "2.3"],
    "Scope Drift Monitor": ["1.14", "1.4", "1.5"],
    "RAG Source Validator": ["2.16", "1.7", "2.13"],
    "Conflict of Interest Testing": ["2.18", "2.11", "2.5"],
    "Hallucination Tracker": ["3.10", "2.9", "2.12"],
    "DR Testing Framework": ["2.4", "2.1", "1.9"],
    "Session Security Configurator": ["1.23", "1.11"],
    "Audit Compliance Manager": ["1.7"],
    "Agent Access Governance Monitor": ["3.8"],
    "Content Moderation Governance Monitor": ["1.27", "1.8"],
    "File Upload Security Configurator": ["1.14", "1.8", "1.4"],
}

# Adoption phase mappings
PHASE_CONTROLS = {
    "0": {
        "name": "Foundation",
        "duration": "0-60 days",
        "controls": {
            "1.1": "Critical", "1.5": "Critical", "2.1": "Critical",
            "2.3": "High", "3.1": "Critical", "4.1": "High",
        },
    },
    "1": {
        "name": "Production Readiness",
        "duration": "2-6 months",
        "controls": {
            "1.7": "Critical", "1.9": "Critical", "1.11": "High",
            "2.5": "High", "2.8": "Critical", "2.12": "Critical",
            "3.2": "High", "3.3": "High", "3.7": "High", "4.2": "High",
        },
    },
    "2": {
        "name": "Advanced Governance",
        "duration": "6-12 months",
        "controls": {
            "1.6": "High", "1.8": "High", "1.19": "High",
            "1.22": "Medium", "2.6": "Critical", "2.11": "High",
            "2.16": "High", "2.20": "High", "3.9": "High", "3.10": "Medium",
        },
    },
}

# Effort estimates by phase and role (hours)
EFFORT_ESTIMATES = {
    "0": {
        "Power Platform Admin": "40-60",
        "Compliance": "20-30",
        "Security": "10-20",
        "AI Governance Lead": "60-80",
    },
    "1": {
        "Power Platform Admin": "60-80",
        "Compliance": "40-60",
        "Security": "30-40",
        "AI Governance Lead": "80-100",
    },
    "2": {
        "Power Platform Admin": "40-60",
        "Compliance": "30-40",
        "Security": "60-80",
        "AI Governance Lead": "60-80",
    },
}

# Role-to-control assignments (from docs/downloads/index.md)
ROLE_CONTROLS = {
    "Entra Global Admin": ["1.11", "1.12", "1.18", "3.1"],
    "Power Platform Admin": ["2.1", "2.2", "2.15", "2.16", "2.17", "3.7", "3.8"],
    "Purview Compliance Admin": ["1.5", "1.6", "1.7", "1.9", "1.10", "1.19", "1.22"],
    "SharePoint Admin": ["4.1", "4.2", "4.3", "4.4", "4.5", "4.6", "4.7"],
    "Compliance Officer": [
        "1.7", "1.19", "1.22", "2.6", "2.11", "2.12", "2.13",
        "2.18", "2.19", "2.21", "3.3", "3.10",
    ],
    "AI Governance Lead": [
        "1.1", "1.2", "1.3", "1.4", "1.8", "1.13", "1.14", "1.15",
        "1.16", "1.17", "1.20", "1.21", "1.23", "1.24", "1.25", "1.26",
        "1.27", "1.28", "2.3", "2.4", "2.5", "2.7", "2.8", "2.9", "2.10",
        "2.14", "2.20", "2.22", "2.23", "2.24", "3.2", "3.4", "3.5",
        "3.6", "3.9", "3.11", "3.12",
    ],
}

# Regulatory priority by institution type
INSTITUTION_REGULATORY_PRIORITY = {
    "broker-dealer": {
        "label": "Broker-Dealer (FINRA/SEC)",
        "priority_controls": ["2.12", "1.7", "2.11", "3.3"],
        "regulations": [
            "FINRA Rule 4511", "FINRA Rule 3110",
            "FINRA AI Supervision and Governance",
            "SEC Rule 17a-3/4", "SOX Section 302/404",
        ],
    },
    "bank": {
        "label": "Bank (OCC/Fed)",
        "priority_controls": ["2.6", "2.11", "1.7", "1.5"],
        "regulations": [
            "OCC Bulletin 2011-12 / SR 11-7",
            "GLBA Safeguards Rule (501-505)",
            "SOX Section 302/404",
        ],
    },
    "adviser": {
        "label": "Investment Adviser (SEC)",
        "priority_controls": ["2.12", "2.19", "1.7", "3.1"],
        "regulations": [
            "SEC Rule 17a-3/4", "SOX Section 302/404",
        ],
    },
    "dual-registered": {
        "label": "Dual-Registered (FINRA + SEC)",
        "priority_controls": ["2.12", "1.7", "2.6", "2.11", "3.3"],
        "regulations": [
            "FINRA Rule 4511", "FINRA Rule 3110",
            "FINRA AI Supervision and Governance",
            "SEC Rule 17a-3/4",
            "OCC Bulletin 2011-12 / SR 11-7",
            "GLBA Safeguards Rule (501-505)",
            "SOX Section 302/404",
        ],
    },
    "insurance": {
        "label": "Insurance Company",
        "priority_controls": ["1.5", "1.7", "2.6", "3.3"],
        "regulations": [
            "GLBA Safeguards Rule (501-505)",
            "SOX Section 302/404",
        ],
    },
}

VERBOSE = False


def log(msg):
    if VERBOSE:
        print(f"  {msg}")


def find_control_file(pillar_num, ctrl_num):
    """Find the markdown file for a specific control."""
    folder = CONTROLS_DIR / PILLARS[pillar_num]["folder"]
    pattern = f"{pillar_num}.{ctrl_num}-*.md"
    matches = list(folder.glob(pattern))
    if not matches:
        return None
    return matches[0]


def extract_section(content, heading, next_heading_pattern=r"^## "):
    """Extract content between a heading and the next same-level heading."""
    pattern = rf"^{re.escape(heading)}\s*$"
    match = re.search(pattern, content, re.MULTILINE)
    if not match:
        return ""
    start = match.end()
    # Find next heading at same level
    next_match = re.search(next_heading_pattern, content[start:], re.MULTILINE)
    if next_match:
        return content[start:start + next_match.start()].strip()
    return content[start:].strip()


def parse_metadata(content):
    """Extract metadata fields from the top of a control file."""
    meta = {}

    # Control title
    title_match = re.search(
        r"^#\s+Control\s+(\d+\.\d+)[:\-]\s+(.+)$", content, re.MULTILINE
    )
    if title_match:
        meta["id"] = title_match.group(1)
        meta["title"] = title_match.group(2).strip()

    # Standard metadata fields
    fields = {
        "pillar": r"\*\*Pillar:\*\*\s*(.+)",
        "regulatoryReference": r"\*\*Regulatory Reference:\*\*\s*(.+)",
        "governanceLevels": r"\*\*Governance Levels:\*\*\s*(.+)",
    }
    for key, pattern in fields.items():
        match = re.search(pattern, content)
        if match:
            meta[key] = match.group(1).strip()

    return meta


def parse_objective(content):
    """Extract the Objective section text."""
    section = extract_section(content, "## Objective")
    # Clean up markdown formatting for display
    section = re.sub(r"\*\*([^*]+)\*\*", r"\1", section)  # Remove bold
    # Take first paragraph only for summary
    paragraphs = section.split("\n\n")
    return paragraphs[0].strip() if paragraphs else section


def parse_zone_requirements(content):
    """Extract zone-specific requirements from the table."""
    section = extract_section(content, "## Zone-Specific Requirements")
    zones = {}

    # Parse markdown table rows
    for match in re.finditer(
        r"\|\s*\*\*Zone\s+(\d)\*\*\s*\([^)]+\)\s*\|\s*([^|]+)\|\s*([^|]+)\|",
        section,
    ):
        zone_num = match.group(1)
        requirement = match.group(2).strip()
        rationale = match.group(3).strip()
        zones[f"zone{zone_num}"] = {
            "requirement": requirement,
            "rationale": rationale,
        }

    return zones


# Keywords indicating a zone requirement is minimal (exclude from zone scoring).
# These patterns match requirements where the ENTIRE control is optional/N/A for a zone.
# Use ZONE_WEIGHT_OVERRIDES below to correct false positives where only a sub-aspect
# matches (e.g., "PIM not required" when the rest of the control is substantive).
ZONE_MINIMAL_PATTERNS = [
    r"\bn/a\b",
    r"\bnot applicable\b",
    r"\boptional\b",
    r"\bnot required\b",
    r"\bawareness only\b",
    r"\bawareness training\b",
    r"\bno recommendation agents\b",
    r"\bno external marketing\b",
    r"\bnon-model classification\b",
    r"\bno delegation allowed\b",
    r"\bnot customer-facing\b",
]

# Manual overrides for controls where keyword matching gives false positives.
# These controls have substantive Zone 1 requirements despite containing
# keywords like "not required" or "optional" in a subordinate clause.
# Key: control ID, Value: dict of zone number -> weight (1=substantive, 0=exclude)
ZONE_WEIGHT_OVERRIDES = {
    "1.18": {"1": 1},  # "Standard roles; self-service; annual review; PIM not required"
    "1.23": {"1": 1},  # "Standard MFA; 8-hour session; step-up not required"
    "2.3":  {"1": 1},  # "Basic change documentation recommended; pipelines optional"
    "2.24": {"1": 1},  # "...default features enabled; preview features allowed for testing; periodic review of feature catalog (quarterly); risk awareness training for agent authors"
    "3.4":  {"1": 1},  # "Standard response (24h); optional RCA for low severity"
}


def compute_zone_weight(requirement_text, control_id=None, zone_num=None):
    """Determine if a zone requirement is substantive (1) or minimal (0).

    Returns 0 for requirements that are optional/awareness-only/N/A,
    and 1 for requirements that are substantive (baseline or above).
    Checks manual overrides first for known false-positive corrections.
    """
    # Check manual overrides first
    if control_id and zone_num and control_id in ZONE_WEIGHT_OVERRIDES:
        override = ZONE_WEIGHT_OVERRIDES[control_id].get(str(zone_num))
        if override is not None:
            return override

    if not requirement_text:
        return 1  # Default to substantive if no text
    text_lower = requirement_text.lower()
    for pattern in ZONE_MINIMAL_PATTERNS:
        if re.search(pattern, text_lower):
            return 0
    return 1


def parse_verification_criteria(content):
    """Extract verification criteria as a list of items."""
    section = extract_section(content, "## Verification Criteria")
    criteria = []

    # Match numbered list items (may span multiple lines)
    items = re.split(r"\n\d+\.\s+", "\n" + section)
    for item in items[1:]:  # Skip empty first split
        # Clean up the text
        text = item.strip()
        text = re.sub(r"\n\s+", " ", text)  # Join wrapped lines
        text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)  # Remove bold
        if text:
            criteria.append(text)

    return criteria


def parse_config_points(content):
    """Extract key configuration points as structured items."""
    section = extract_section(content, "## Key Configuration Points")
    points = []

    def extract_bullets(text):
        """Extract bullet points from a block of text."""
        results = []
        for match in re.finditer(r"^[-*]\s+(.+)$", text, re.MULTILINE):
            item = match.group(1).strip()
            item = re.sub(r"\*\*([^*]+)\*\*", r"\1", item)
            item = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", item)
            if item:
                results.append(item)
        return results

    # Split by subsection headings
    subsections = re.split(r"^###\s+(.+)$", section, flags=re.MULTILINE)

    # subsections[0] contains content before any ### heading (top-level bullets)
    if subsections[0].strip():
        points.extend(extract_bullets(subsections[0]))

    # Process subsection content: [preamble, heading1, content1, heading2, content2, ...]
    for i in range(1, len(subsections), 2):
        body = subsections[i + 1] if i + 1 < len(subsections) else ""
        points.extend(extract_bullets(body))

    return points


def parse_roles(content):
    """Extract roles from the Roles & Responsibilities table."""
    section = extract_section(content, "## Roles & Responsibilities")
    roles = []

    for match in re.finditer(r"\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|", section):
        role = match.group(1).strip()
        responsibility = match.group(2).strip()
        # Skip table header and separator
        if role in ("Role", "---", "----", "------") or role.startswith("-"):
            continue
        if role:
            roles.append({"role": role, "responsibility": responsibility})

    return roles


def get_solutions_for_control(control_id):
    """Return list of solution names that support this control."""
    solutions = []
    for solution_name, ctrl_ids in SOLUTION_CONTROLS.items():
        if control_id in ctrl_ids:
            solutions.append(solution_name)
    return solutions


def get_roles_for_control(control_id):
    """Return list of role names assigned to this control."""
    roles = []
    for role_name, ctrl_ids in ROLE_CONTROLS.items():
        if control_id in ctrl_ids:
            roles.append(role_name)
    return roles


def get_phase_for_control(control_id):
    """Return the adoption phase and priority for this control, or None."""
    for phase_num, phase_data in PHASE_CONTROLS.items():
        if control_id in phase_data["controls"]:
            return {
                "phase": int(phase_num),
                "phaseName": phase_data["name"],
                "priority": phase_data["controls"][control_id],
            }
    return None


def parse_regulations(reg_string):
    """Parse regulatory reference string into list of regulation codes."""
    if not reg_string:
        return []
    # Split on commas, clean up
    regs = [r.strip() for r in reg_string.split(",")]
    return [r for r in regs if r]


def parse_control(pillar_num, ctrl_num):
    """Parse a single control file and return structured data."""
    control_id = f"{pillar_num}.{ctrl_num}"
    filepath = find_control_file(pillar_num, ctrl_num)
    if not filepath:
        print(f"  ERROR: No file found for control {control_id}")
        return None

    log(f"Parsing {control_id} from {filepath.name}")
    content = filepath.read_text(encoding="utf-8")

    meta = parse_metadata(content)
    if not meta.get("id"):
        print(f"  ERROR: Could not extract ID from {filepath.name}")
        return None

    objective = parse_objective(content)
    zones = parse_zone_requirements(content)
    verification = parse_verification_criteria(content)
    config_points = parse_config_points(content)
    roles = parse_roles(content)
    regulations = parse_regulations(meta.get("regulatoryReference", ""))
    phase_info = get_phase_for_control(control_id)
    solutions = get_solutions_for_control(control_id)
    assigned_roles = get_roles_for_control(control_id)

    # Determine which zones this control applies to
    applicable_zones = []
    if zones.get("zone1"):
        applicable_zones.append(1)
    if zones.get("zone2"):
        applicable_zones.append(2)
    if zones.get("zone3"):
        applicable_zones.append(3)
    # If no zones parsed from table, default to all zones
    if not applicable_zones:
        applicable_zones = [1, 2, 3]

    # Compute zone weights for scoring differentiation
    zone_weights = {}
    for z in [1, 2, 3]:
        zone_data = zones.get(f"zone{z}", {})
        req_text = zone_data.get("requirement", "")
        zone_weights[str(z)] = compute_zone_weight(req_text, control_id, z)

    # Build playbook paths (no .md extension — MkDocs serves without it)
    playbooks = {
        "portalWalkthrough": f"playbooks/control-implementations/{control_id}/portal-walkthrough/",
        "powershellSetup": f"playbooks/control-implementations/{control_id}/powershell-setup/",
        "verificationTesting": f"playbooks/control-implementations/{control_id}/verification-testing/",
        "troubleshooting": f"playbooks/control-implementations/{control_id}/troubleshooting/",
    }

    return {
        "id": control_id,
        "pillar": pillar_num,
        "pillarName": PILLARS[pillar_num]["name"],
        "title": meta.get("title", f"Control {control_id}"),
        "objective": objective,
        "regulations": regulations,
        "governanceLevels": meta.get("governanceLevels", ""),
        "zones": applicable_zones,
        "zoneWeights": zone_weights,
        "zoneRequirements": zones,
        "verificationCriteria": verification,
        "configPoints": config_points,
        "roles": roles,
        "assignedRoles": assigned_roles,
        "adoptionPhase": phase_info,
        "solutions": solutions,
        "playbooks": playbooks,
    }


def parse_regulatory_mappings():
    """Parse regulatory-mappings.md into regulation-to-control matrix."""
    filepath = DOCS_DIR / "reference" / "regulatory-mappings.md"
    if not filepath.exists():
        print("  WARNING: regulatory-mappings.md not found, skipping")
        return {}

    content = filepath.read_text(encoding="utf-8")
    mappings = {}

    # Find each regulation section and its control tables
    # Regulations are ## headings
    sections = re.split(r"^## (.+)$", content, flags=re.MULTILINE)

    for i in range(1, len(sections), 2):
        heading = sections[i].strip()
        body = sections[i + 1] if i + 1 < len(sections) else ""

        # Extract regulation short code from heading
        # Format: "FINRA Rule 4511 - Books and Records" or "SOX Section 302/404"
        reg_key = heading.split(" - ")[0].strip() if " - " in heading else heading.strip()

        # Find all control references in table rows
        controls = []
        for match in re.finditer(
            r"\[(\d+\.\d+)\]\([^)]+\)", body
        ):
            ctrl_id = match.group(1)
            if ctrl_id not in controls:
                controls.append(ctrl_id)

        if controls:
            mappings[reg_key] = {
                "label": heading,
                "controls": sorted(controls, key=lambda x: [int(p) for p in x.split(".")]),
            }

    return mappings


def build_output():
    """Build the complete assessment data JSON."""
    controls = []
    errors = []

    for pillar_num, pillar_data in PILLARS.items():
        for ctrl_num in pillar_data["controls"]:
            control = parse_control(pillar_num, ctrl_num)
            if control:
                controls.append(control)
            else:
                errors.append(f"{pillar_num}.{ctrl_num}")

    # Validate we got all 71 controls
    if len(controls) != 71:
        print(f"\nERROR: Expected 71 controls, got {len(controls)}")
        if errors:
            print(f"  Missing: {', '.join(errors)}")
        return None

    # Validate required fields
    for ctrl in controls:
        missing = []
        for field in ["id", "pillar", "title", "objective", "zones", "verificationCriteria", "configPoints"]:
            val = ctrl.get(field)
            if val is None or val == "" or val == []:
                missing.append(field)
        if missing:
            print(f"  WARNING: Control {ctrl['id']} missing fields: {', '.join(missing)}")

    # Parse regulatory mappings
    reg_mappings = parse_regulatory_mappings()

    output = {
        "version": "1.0.0",
        "generatedAt": None,  # Set at write time
        "frameworkVersion": "1.2.52",
        "totalControls": len(controls),
        "pillars": {
            str(k): {"name": v["name"], "controlCount": len(v["controls"])}
            for k, v in PILLARS.items()
        },
        "controls": controls,
        "regulatoryMappings": reg_mappings,
        "institutionTypes": INSTITUTION_REGULATORY_PRIORITY,
        "adoptionPhases": PHASE_CONTROLS,
        "effortEstimates": EFFORT_ESTIMATES,
        "roleAssignments": ROLE_CONTROLS,
        "solutionMappings": SOLUTION_CONTROLS,
    }

    return output


def main():
    global VERBOSE
    import argparse
    from datetime import datetime, timezone

    parser = argparse.ArgumentParser(
        description="Extract assessment data from FSI-AgentGov controls"
    )
    parser.add_argument("--verbose", action="store_true", help="Show detailed output")
    parser.add_argument("--output", type=str, help="Output file path")
    args = parser.parse_args()

    VERBOSE = args.verbose
    output_path = Path(args.output) if args.output else OUTPUT_PATH

    print("FSI-AgentGov Assessment Data Extraction")
    print("=" * 45)

    data = build_output()
    if data is None:
        print("\nFAILED: Could not build assessment data")
        sys.exit(1)

    data["generatedAt"] = datetime.now(timezone.utc).isoformat()

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\nGenerated {output_path}")
    print(f"  Controls: {data['totalControls']}")
    print(f"  Regulations: {len(data['regulatoryMappings'])}")

    # Summary stats
    with_phase = sum(1 for c in data["controls"] if c["adoptionPhase"])
    with_solutions = sum(1 for c in data["controls"] if c["solutions"])
    avg_criteria = sum(len(c["verificationCriteria"]) for c in data["controls"]) / len(data["controls"])
    avg_config = sum(len(c["configPoints"]) for c in data["controls"]) / len(data["controls"])

    print(f"  Controls with adoption phase: {with_phase}")
    print(f"  Controls with solutions: {with_solutions}")
    print(f"  Avg verification criteria: {avg_criteria:.1f}")
    print(f"  Avg config points: {avg_config:.1f}")

    # Validate generated playbook URLs (must not end in .md — MkDocs uses directory URLs)
    bad_urls = []
    for ctrl in data["controls"]:
        for key, url in ctrl.get("playbooks", {}).items():
            if url.endswith(".md"):
                bad_urls.append(f"  {ctrl['id']}.playbooks.{key}: {url}")
    if bad_urls:
        print(f"\nFAILED: {len(bad_urls)} playbook URLs end in .md (MkDocs uses directory URLs)")
        for b in bad_urls:
            print(b)
        sys.exit(1)

    print("\nSUCCESS")


if __name__ == "__main__":
    main()
