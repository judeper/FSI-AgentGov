# FSI-AgentGov Repository Instructions

## Project Overview

FSI Agent Governance Framework v1.0 Beta - A governance framework for Microsoft 365 AI agents (Copilot Studio, Agent Builder) in US financial services organizations.

- **48 controls** across 4 pillars (Security, Management, Reporting, SharePoint)
- **3 governance zones** (Personal Productivity, Team Collaboration, Enterprise Managed)
- **Target regulations:** FINRA 4511/3110/25-07, SEC 17a-3/4, SOX 302/404, GLBA 501(b), OCC 2011-12, Fed SR 11-7
- **Documentation site:** Built with MkDocs Material, published to GitHub Pages

## Design Decisions

### Audience
- **Primary:** M365 administrators in US financial services
- **Secondary:** Compliance officers, AI governance leads
- **NOT for:** Developers, end users

### GitHub Pages (What to Publish)
- **Publish:** Controls, getting started guides, reference materials, downloads
- **Do NOT publish:** `images/`, `scripts/`, `templates/` folders

### Deliverables (Scope)
- **Ship:** GitHub Pages web docs + Excel templates under `docs/downloads/`
- **Do not ship:** Word/PDF document bundles

### Screenshots
- **LOCAL ONLY** - never push to GitHub
- Used to verify portal instructions stay current with UI changes
- Each control folder has `EXPECTED.md` listing required screenshots (no images are committed)
- Store screenshots and tenant evidence under `maintainers-local/tenant-evidence/` (gitignored)

### Navigation Philosophy
- **Getting Started:** Admin onboarding only (no repo structure info)
- **Pillars 1-4:** Implementation guidance for each control
- **Reference:** Supporting materials (glossary, RACI, regulatory mappings, license requirements)
- **Contributors:** Repo structure and maintenance info for maintainers
- **Downloads:** Role-based Excel checklists for admins

### Language Standards
- Avoid legal overclaims ("ensures compliance", "guarantees")
- Use hedged language ("supports compliance with", "helps meet")
- Always include implementation caveats

---

## Directory Structure

```
docs/
├── getting-started/          # Onboarding guides (overview, quick-start, zones, lifecycle, checklist)
├── reference/
│   ├── pillar-1-security/    # 19 security controls (1.1-1.19)
│   ├── pillar-2-management/  # 15 management controls (2.1-2.15)
│   ├── pillar-3-reporting/   # 9 reporting controls (3.1-3.9)
│   ├── pillar-4-sharepoint/  # 5 SharePoint controls (4.1-4.5)
│   └── CONTROL-INDEX.md          # Master control list
├── templates/                # Control authoring template
├── images/                   # Screenshot verification (LOCAL ONLY - gitignored)
└── downloads/                # Excel templates for admins
scripts/                      # Validation scripts (verify_controls.py, verify_templates.py)
mkdocs.yml                    # Site navigation and configuration

maintainers-local/            # LOCAL ONLY (gitignored)
├── reference-pack/           # Whitepapers and extracted reference content
├── reports/                  # Generated reports / audits
├── tenant-evidence/          # Screenshots, exports, tenant notes
├── notes/                    # Maintainer notes and context
└── tmp/                      # Scratch artifacts
```

## Control Authoring

### Template Location
`docs/templates/control-setup-template.md` - Use this for all new controls.

### Required 12 Sections
1. Overview (ID, Name, Regulatory Reference, Setup Time)
2. Prerequisites (License, Primary Owner Admin Role, Dependencies)
3. Governance Levels (Baseline, Recommended, Regulated)
4. Setup & Configuration (Portal steps + PowerShell alternative)
5. Financial Sector Considerations (Regulatory Alignment table)
6. Zone-Specific Configuration
7. Verification & Testing (numbered steps with EXPECTED result)
8. Troubleshooting & Validation (Common Issues table)
9. Additional Resources (Microsoft Learn links)
10. Related Controls (cross-references)
11. Support & Questions (contact roles)
12. Footer (Updated: Month-Year, Version: v1.0 Beta (Dec 2025), UI Verification Status)

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
| `docs/templates/control-setup-template.md` | Control format (12 sections) |
| `docs/reference/CONTROL-INDEX.md` | Master list of all 48 controls |
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
```

## Common Tasks

### Adding a New Control
1. Copy `docs/templates/control-setup-template.md` to appropriate pillar folder
2. Rename following pattern: `{id}-{kebab-case-name}.md`
3. Fill all 12 sections
4. Update `docs/reference/CONTROL-INDEX.md`
5. Add entry to `mkdocs.yml` navigation
7. Run `mkdocs build --strict` to validate

### Updating a Control
1. Make changes following template structure
2. Update "Updated" in footer (Month-Year)
3. If portal paths changed, update EXPECTED.md in `docs/images/{control-id}/`
4. Run `mkdocs build --strict` to validate

### Verifying Screenshots
1. Ask to "verify screenshots for control X.X"
2. I will read the control doc and compare to EXPECTED.md
3. Report any discrepancies between instructions and screenshots
