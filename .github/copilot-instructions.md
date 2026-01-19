# FSI-AgentGov Repository Instructions

## Project Overview

FSI Agent Governance Framework v1.1 - A governance framework for Microsoft 365 AI agents (Copilot Studio, Agent Builder) in US financial services organizations.

- **60 controls** across 4 pillars (Security, Management, Reporting, SharePoint)
- **3 governance zones** (Personal Productivity, Team Collaboration, Enterprise Managed)
- **3-layer documentation** (Framework → Controls → Playbooks)
- **Target regulations:** FINRA 4511/3110/25-07, SEC 17a-3/4, SOX 302/404, GLBA 501(b), OCC 2011-12, Fed SR 11-7, CFTC 1.31
- **Documentation site:** Built with MkDocs Material, published to GitHub Pages

## Design Decisions

### Audience
- **Primary:** M365 administrators in US financial services
- **Secondary:** Compliance officers, AI governance leads
- **NOT for:** Developers, end users

### GitHub Pages (What to Publish)
- **Publish:** Framework docs, controls, playbooks, getting started guides, reference materials, downloads
- **Do NOT publish:** `images/`, `scripts/`, `templates/` folders

### Deliverables (Scope)
- **Ship:** GitHub Pages web docs + Excel templates under `docs/downloads/`
- **Do not ship:** Word/PDF document bundles

### Screenshots
- **LOCAL ONLY** - never push to GitHub
- Used to verify portal instructions stay current with UI changes
- Each control folder has `EXPECTED.md` listing required screenshots (no images are committed)
- Store screenshots and tenant evidence under `maintainers-local/tenant-evidence/` (gitignored)

### Navigation Philosophy (Three-Layer Model)
- **Framework:** Governance principles, strategy, organizational context (`docs/framework/`)
- **Controls:** Technical specifications with 10-section format (`docs/controls/pillar-*/`)
- **Playbooks:** Step-by-step implementation procedures (`docs/playbooks/`)
- **Reference:** Supporting materials (glossary, RACI, regulatory mappings, license requirements)
- **Getting Started:** Admin onboarding only (no repo structure info)
- **Downloads:** Role-based Excel checklists for admins

### Language Standards
- Avoid legal overclaims ("ensures compliance", "guarantees")
- Use hedged language ("supports compliance with", "helps meet")
- Always include implementation caveats

---

## Directory Structure

```
docs/
├── getting-started/              # Onboarding guides (overview, quick-start, zones, lifecycle, checklist)
├── framework/                    # NEW in v1.1: Governance principles layer
│   ├── executive-summary.md      # Strategic overview for leadership
│   ├── zones-and-tiers.md        # Zone 1/2/3 definitions
│   ├── adoption-roadmap.md       # 30/60/90-day phased implementation
│   ├── lifecycle-governance.md   # Agent lifecycle management
│   ├── roles-and-responsibilities.md
│   ├── risk-framework.md
│   ├── regulatory-context.md
│   ├── training-and-awareness.md
│   └── index.md
├── controls/                     # RENAMED in v1.1 (was: reference/pillar-*)
│   ├── pillar-1-security/        # 23 security controls (1.1-1.23)
│   ├── pillar-2-management/      # 20 management controls (2.1-2.20)
│   ├── pillar-3-reporting/       # 10 reporting controls (3.1-3.10)
│   ├── pillar-4-sharepoint/      # 7 SharePoint controls (4.1-4.7)
│   └── CONTROL-INDEX.md          # Master control list
├── playbooks/                    # NEW in v1.1: Implementation layer
│   ├── control-implementations/  # Per-control guides (240 files, 4 per control)
│   ├── governance-operations/    # Standing procedures
│   ├── compliance-and-audit/     # Audit preparation guides
│   ├── incident-response/        # Incident handling procedures
│   └── lifecycle-operations/     # Agent lifecycle management
├── reference/                    # Supporting materials
│   ├── role-catalog.md
│   ├── regulatory-mappings.md
│   ├── glossary.md
│   └── ...
├── templates/                    # Control authoring template
├── images/                       # Screenshot verification (LOCAL ONLY - gitignored)
└── downloads/                    # Excel templates for admins
scripts/                          # Validation scripts (verify_controls.py, verify_templates.py)
releases/                         # Release artifacts by version
mkdocs.yml                        # Site navigation and configuration

maintainers-local/                # LOCAL ONLY (gitignored)
├── reference-pack/               # Whitepapers and extracted reference content
├── researcher-package/           # Compiled controls for external review
├── reports/                      # Generated reports / audits
├── tenant-evidence/              # Screenshots, exports, tenant notes
├── notes/                        # Maintainer notes and context
└── tmp/                          # Scratch artifacts
```

## Control Authoring

### Template Location
`docs/templates/control-setup-template.md` - Use this for all new controls.

### Required 10 Sections

Controls follow a standardized format with header metadata, 10 sections, and footer metadata:

**Header Metadata:**
- Control ID, Pillar, Regulatory Reference, Last UI Verified, Governance Levels

**Sections:**
1. Objective (concise purpose statement)
2. Why This Matters for FSI (regulatory bullet points)
3. Control Description (detailed technical explanation)
4. Key Configuration Points (bulleted configuration items)
5. Zone-Specific Requirements (Zone 1/2/3 table)
6. Roles & Responsibilities (admin roles table)
7. Related Controls (cross-reference table)
8. Implementation Guides (links to 4 playbooks)
9. Verification Criteria (verification checklist)
10. Additional Resources (Microsoft Learn links)

**Footer Metadata:**
- *Updated: Month-Year | Version: v1.1 | UI Verification Status: Current*

### Administrator Role Naming (Canonical)

- Use the framework's canonical short role names (e.g., "Entra Global Admin", "Purview Compliance Admin", "Power Platform Admin").
- Avoid synonyms like "Global Administrator" vs "Global Admin" inside controls; pick one canonical name.
- Refer to the role catalog for canonical names and accepted aliases: `docs/reference/role-catalog.md`.

### Language Rules
- **Never say:** "ensures compliance", "guarantees"
- **Instead use:** "supports compliance with", "helps meet", "required for"
- Include implementation caveats where appropriate

## Screenshot Verification (Local Only)

Screenshots are stored locally for verifying portal instructions stay current.

- **Location:** `docs/images/{control-id}/` (e.g., `docs/images/1.1/`)
- **Workflow:** Use `docs/images/{control-id}/EXPECTED.md` as the checklist
- **Storage:** Put screenshots and evidence in `maintainers-local/tenant-evidence/`
- **Files stay local** - all binaries are gitignored

## Key Files to Read First

| File | Purpose |
|------|---------|
| `CONTRIBUTING.md` | Style guidelines and language rules |
| `docs/templates/control-setup-template.md` | Control format (10 sections) |
| `docs/controls/CONTROL-INDEX.md` | Master list of all 60 controls |
| `mkdocs.yml` | Site navigation structure |

## Build and Validate

```bash
# Validate site builds without errors
mkdocs build --strict

# Preview locally
mkdocs serve
# Opens at http://localhost:8000

# Validate controls match expected structure
python scripts/verify_controls.py

# Validate templates are valid
python scripts/verify_templates.py

# Validate Excel templates (control counts, version references)
python scripts/verify_excel_templates.py
```

## Common Tasks

### Adding a New Control
1. Copy `docs/templates/control-setup-template.md` to appropriate pillar folder
2. Rename following pattern: `{id}-{kebab-case-name}.md`
3. Fill all 10 sections (plus header and footer metadata)
4. Update `docs/controls/CONTROL-INDEX.md`
5. Add entry to `mkdocs.yml` navigation
6. Create playbooks in `docs/playbooks/control-implementations/{control-id}/`
7. Run `mkdocs build --strict` to validate

### Updating a Control
1. Make changes following template structure
2. Update "Updated" in footer (Month-Year)
3. If portal paths changed, update EXPECTED.md in `docs/images/{control-id}/`
4. Update related playbooks in `docs/playbooks/control-implementations/`
5. Run `mkdocs build --strict` to validate

### Verifying Screenshots
1. Ask to "verify screenshots for control X.X"
2. I will read the control doc and compare to EXPECTED.md
3. Report any discrepancies between instructions and screenshots
