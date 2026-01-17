# FSI-AgentGov Repository - Claude Code Instructions

## Project Overview

**FSI Agent Governance Framework v1.0** - A governance framework for Microsoft 365 AI agents (Copilot Studio, Agent Builder) in US financial services organizations.

### Key Stats
- **58 controls** across 4 pillars (Security, Management, Reporting, SharePoint)
- **3 governance zones** (Personal Productivity, Team Collaboration, Enterprise Managed)
- **Target regulations:** FINRA 4511/3110/25-07, SEC 17a-3/4, SOX 302/404, GLBA 501(b), OCC 2011-12, Fed SR 11-7, CFTC 1.31
- **Documentation:** MkDocs Material-based site published to GitHub Pages
- **Audience:** M365 administrators in US financial services

---

## Before Starting Any Task

Read these files for full repository context:
1. **`.github/copilot-instructions.md`** - Full repository structure and design decisions
2. **`AGENTS.md`** - Instructions for autonomous agent tasks (vs. interactive work)
3. **`docs/templates/control-setup-template.md`** - The 12-section control template
4. **`CONTRIBUTING.md`** - Language guidelines and style rules
5. **`.claude/claude.md`** - This file (you're reading it!)

---

## Directory Structure (Quick Reference)

```
C:\dev\FSI-AgentGov\
├── .git/                         # Git repository
├── .venv/                        # Python virtual environment
├── .github/                      # GitHub-specific files
├── .claude/                      # Claude Code configuration
├── docs/
│   ├── getting-started/          # Onboarding guides for admins
│   ├── reference/
│   │   ├── pillar-1-security/   # Controls 1.1-1.22 (22 controls)
│   │   ├── pillar-2-management/ # Controls 2.1-2.19 (19 controls)
│   │   ├── pillar-3-reporting/  # Controls 3.1-3.10 (10 controls)
│   │   ├── pillar-4-sharepoint/ # Controls 4.1-4.7 (7 controls)
│   │   ├── CONTROL-INDEX.md     # Master control list
│   │   └── [other reference materials]
│   ├── templates/               # Control authoring template
│   ├── images/                  # Screenshot verification specs (LOCAL ONLY)
│   └── downloads/               # Excel templates for admins
├── scripts/                      # Python validation scripts
├── maintainers-local/           # LOCAL ONLY - gitignored (reports, notes, evidence)
├── review/                      # Review materials and proposals
├── mkdocs.yml                   # Site navigation and MkDocs config
├── AGENTS.md                    # Agent workflow instructions
├── CONTRIBUTING.md              # Language and style guidelines
├── README.md                    # Repository home page
├── CHANGELOG.md                 # Release history
├── SECURITY.md                  # Security policy
└── [LICENSE, CODE_OF_CONDUCT.md, etc.]
```

---

## Common Claude Code Workflows

### 1. Update Existing Control

**Scenario:** You need to modify a control's content (e.g., update instructions for a step, fix a typo, add new regulation reference)

**Steps:**
1. **Read the control** you're updating: `docs/reference/pillar-{1-4}-{name}/{id}-{kebab-case}.md`
2. **Read the template** for structure: `docs/templates/control-setup-template.md`
3. **Make changes** while preserving all 12 sections (never skip or remove a section)
4. **Update footer date:** Change "Updated: Month-Year" to current date
5. **If portal paths changed:** Update `docs/images/{control-id}/EXPECTED.md` with new screenshot requirements
6. **Validate:** Run `mkdocs build --strict` (must pass with zero errors)

**Critical Language Rules (NEVER violate):**
- ❌ Avoid: "ensures compliance", "guarantees", "will prevent"
- ✅ Use: "supports compliance with", "helps meet", "required for"
- Always include implementation caveats

**Example Change:**
```markdown
❌ WRONG: "This control ensures you meet SEC 17a-4 requirements"
✅ RIGHT: "This control helps support SEC 17a-4 requirements. Implementation requires..."
```

### 2. Add a New Control

**Scenario:** You're adding a brand new control to one of the four pillars

**Steps:**
1. **Copy template:** `docs/templates/control-setup-template.md`
2. **Paste into correct pillar folder** with proper naming: `docs/reference/pillar-{n}-{name}/{id}-{kebab-case-name}.md`
   - Example: `docs/reference/pillar-1-security/1.20-new-control-example.md`
3. **Fill ALL 12 sections** (do not skip any):
   - Section 1: Overview (ID, Name, Regulatory Reference, Setup Time)
   - Section 2: Prerequisites (License, Primary Owner Admin Role, Dependencies)
   - Section 3: Governance Levels (Baseline/Recommended/Regulated configs)
   - Section 4: Setup & Configuration (Portal steps + PowerShell alternative)
   - Section 5: Financial Sector Considerations (Regulatory Alignment table)
   - Section 6: Zone-Specific Configuration (Zone 1/2/3 variations)
   - Section 7: Verification & Testing (numbered steps with EXPECTED result)
   - Section 8: Troubleshooting & Validation (Common Issues table)
   - Section 9: Additional Resources (Microsoft Learn links)
   - Section 10: Related Controls (cross-references)
   - Section 11: Support & Questions (contact roles)
   - Section 12: Footer (Updated: Month-Year, Version: v1.0 (Jan 2026), UI Verification Status)
4. **Update CONTROL-INDEX.md:** Add entry to master control list
5. **Update mkdocs.yml:** Add entry to navigation under correct pillar
6. **Create screenshot spec:** `docs/images/{control-id}/EXPECTED.md` with required screenshots
7. **Validate:** Run `mkdocs build --strict` (must pass with zero errors)

### 3. Verify Screenshots

**Scenario:** You need to check if control documentation matches actual portal UI

**Steps:**
1. **Read the control** doc: `docs/reference/pillar-{n}-*/`
2. **Read expected screenshots:** `docs/images/{control-id}/EXPECTED.md`
3. **Review workflow in `docs/images/VERIFY.md`** for detailed instructions
4. **Compare:** Portal instructions against screenshot requirements
5. **Report:**
   - ✅ "Matches" - instructions align with screenshots
   - ⚠️ "Discrepancies found" - instructions don't match current UI
   - ❌ "Outdated" - UI has changed since screenshots were taken

### 4. Update Site Navigation

**Scenario:** You need to reorganize controls in the site menu, add a section, or fix nav order

**File to edit:** `mkdocs.yml` (the `nav:` section)

**Rules:**
- Maintain alphabetical/numerical order within each pillar
- Keep pillar sections organized: Pillar 1, Pillar 2, Pillar 3, Pillar 4
- Validate after changes: `mkdocs build --strict`

**Example nav entry:**
```yaml
- Pillar 1 - Security:
  - Pillar 1 Overview: reference/pillar-1-security/index.md
  - 1.1 - Control Name: reference/pillar-1-security/1.1-control-name.md
  - 1.2 - Control Name: reference/pillar-1-security/1.2-control-name.md
  # ... maintain numerical order
```

---

## Language & Terminology Guidelines

### Role Naming (Canonical Short Names)
Use consistent, short role names. Refer to `docs/reference/role-catalog.md` for approved names:

**Approved Examples:**
- "Entra Global Admin" (NOT "Global Administrator")
- "Purview Compliance Admin" (NOT "Compliance Administrator")
- "Power Platform Admin" (NOT "Power Apps Admin")
- "Exchange Online Admin" (NOT "Exchange Administrator")

### Regulatory Language
**CRITICAL:** This framework operates in highly regulated industries. Language matters.

**NEVER use these phrases:**
- "ensures compliance" → implies guarantee
- "guarantees" → legal risk
- "will prevent" → overclaim
- "eliminates risk" → unrealistic

**ALWAYS use these alternatives:**
- "supports compliance with" → accurate and hedged
- "helps meet" → appropriate scope
- "required for" → clear without overclaiming
- "recommended to" → proportional to impact
- "aids in" → realistic framing

**Example control language:**
```markdown
# Correct (hedged, implementation-aware)
This control supports compliance with FINRA 4511(j) by providing tools for
supervisory oversight of AI agent outputs. Implementation requires establishing
review procedures tailored to your specific use cases and risk profile.

# Incorrect (overclaimful)
This control ensures FINRA 4511(j) compliance and guarantees proper agent oversight.
```

---

## Key Files & Their Purposes

| File | Purpose | Modification Policy |
|------|---------|-------------------|
| `.github/copilot-instructions.md` | Copilot context | Never modify without permission |
| `AGENTS.md` | Autonomous agent workflows | Reference only |
| `docs/templates/control-setup-template.md` | Control authoring template | Reference only |
| `CONTRIBUTING.md` | Language and style rules | Update if rules change |
| `mkdocs.yml` | Site navigation and config | Update for nav changes |
| `docs/reference/CONTROL-INDEX.md` | Master control list | Update when controls added/removed |
| `LICENSE` | Legal file | Never modify without permission |
| `SECURITY.md` | Security policy | Never modify without permission |
| `CODE_OF_CONDUCT.md` | Community standards | Never modify without permission |
| Individual control files `docs/reference/pillar-*/` | Control documentation | Update following template |

---

## Excel Download Templates

The framework includes Excel checklists for administrators in `docs/downloads/`. When adding new controls, these templates must be updated.

### Template Files and Their Control Counts

| File | Role | Controls | Notes |
|------|------|----------|-------|
| `governance-maturity-dashboard.xlsx` | AI Governance Lead | 58 (all) | Has "All Controls" + "Summary Dashboard" sheets |
| `purview-administrator-checklist.xlsx` | Purview Compliance Admin | 7 | DLP, DSPM, Audit, eDiscovery, Information Barriers |
| `sharepoint-administrator-checklist.xlsx` | SharePoint Admin | 7 | IAG, Access Reviews, Retention, External Access, Grounding |
| `power-platform-administrator-checklist.xlsx` | Power Platform Admin | 7 | Environments, Groups, Routing, RAG, Orchestration |
| `compliance-officer-checklist.xlsx` | Compliance Officer | 11 | Regulatory controls across pillars |
| `entra-administrator-checklist.xlsx` | Entra Global Admin | 4 | Conditional Access, Insider Risk, RBAC |

### Updating Excel Templates

When adding new controls, update the relevant Excel files using Python with openpyxl:

```bash
pip install openpyxl
```

**Key considerations:**
- `governance-maturity-dashboard.xlsx` has merged cells for pillar headers - unmerge before editing, re-merge after
- Update the "Summary Dashboard" sheet control counts when adding controls
- Insert new controls in numerical order within their pillar section
- All checklists use the same column format: Control ID | Control Name | Status | Notes | Due Date

**Control-to-checklist mapping:**
- Pillar 1 Security controls → `purview-administrator-checklist.xlsx` (for Purview-managed controls)
- Pillar 2 Management controls → `power-platform-administrator-checklist.xlsx` (for PPAC-managed controls)
- Pillar 3 Reporting controls → Various based on reporting owner
- Pillar 4 SharePoint controls → `sharepoint-administrator-checklist.xlsx`
- Regulatory/compliance controls → `compliance-officer-checklist.xlsx`
- ALL controls → `governance-maturity-dashboard.xlsx`

See `docs/downloads/index.md` for the full control-to-role mapping.

---

## Validation & Testing

### Before Committing Any Changes

Always run these commands and verify they pass:

```bash
# Validate the entire site builds without errors
mkdocs build --strict

# Preview locally (opens at http://localhost:8000)
mkdocs serve

# Validate all controls follow required structure
python scripts/verify_controls.py

# Validate templates are properly formatted
python scripts/verify_templates.py
```

### What "Pass" Means
- ✅ **`mkdocs build --strict`** produces **zero errors** or **zero warnings**
- ✅ **`verify_controls.py`** reports **all controls valid**
- ✅ No broken internal links in site navigation
- ✅ All cross-references to controls exist and work

### If Build Fails
1. Read the error message carefully (usually points to specific file and issue)
2. Check the file mentioned for:
   - Markdown syntax errors (missing brackets, malformed links)
   - Broken cross-references (links to non-existent controls)
   - Missing required sections in controls
3. Fix the issue and re-run validation
4. Repeat until validation passes

---

## Administrator Role Reference

The framework uses **canonical short role names** consistently throughout controls. When you write or edit controls, use these names:

**Microsoft Entra (Azure AD)**
- Entra Global Admin
- Entra Privileged Role Admin
- Entra Security Administrator

**Microsoft Purview & Compliance**
- Purview Compliance Admin
- Purview Compliance Data Administrator
- Purview eDiscovery Manager
- Purview Information Protection Admin

**Microsoft 365 / Microsoft Defender**
- Teams Administrator
- Exchange Online Admin
- SharePoint Admin
- Microsoft 365 Admin
- Defender for Cloud Apps Admin
- Security Administrator

**Microsoft Power Platform**
- Power Platform Admin
- Power Platform Service Admin
- Dynamics 365 Administrator

**See:** `docs/reference/role-catalog.md` for complete list and accepted aliases

---

## Common Errors & Solutions

### Error: "Broken reference to control X.X"
**Cause:** Control doesn't exist or file name is wrong
**Solution:**
1. Check `docs/reference/CONTROL-INDEX.md` to verify control exists
2. Verify file path: `docs/reference/pillar-{n}-{name}/{id}-{kebab-case}.md`
3. Update the reference with correct control ID

### Error: "Control missing section X"
**Cause:** Control file doesn't include all 12 required sections
**Solution:**
1. Read `docs/templates/control-setup-template.md` for the 12 sections
2. Add missing section(s) to the control file
3. Ensure all sections are present, even if one is brief

### Error: "mkdocs build failed with warnings"
**Cause:** Markdown syntax error or missing navigation entry
**Solution:**
1. Check mkdocs output for line number with error
2. Verify bracket matching: `[text](url)` format
3. Check `mkdocs.yml` nav section for the file path
4. Ensure internal links point to existing files

### Error: Build passes locally but fails on GitHub Pages
**Cause:** Path differences between Windows and Linux
**Solution:**
1. Use forward slashes in all links: `docs/reference/...` not `docs\reference\...`
2. Use lowercase file names and folder names
3. Test with `mkdocs build --strict` before committing

---

## Claude Code-Specific Tips

Claude Code excels at:
- **Multi-file editing:** Update multiple controls simultaneously with consistent changes
- **Refactoring:** Rename controls or reorganize sections across the framework
- **Cross-file analysis:** Find references to a control and update all related content
- **Template application:** Copy template structure to new controls efficiently
- **Validation integration:** Run scripts and parse output for issues

### Example: Bulk Control Update
Instead of editing each control individually, provide context about what needs changing:
> "Update all Pillar 1 controls' 'Zone-Specific Configuration' section to clarify that Zone 1 agents should use minimal data access. Show me the changes before I approve them."

Claude can then:
1. Read all 19 Pillar 1 controls
2. Identify their current Zone 1 guidance
3. Present proposed updates for your review
4. Apply consistent changes across all files

---

## Quick Navigation

**Want to...**
- Add a new control? → Start with `docs/templates/control-setup-template.md`
- Update site menu? → Edit `mkdocs.yml` navigation section
- Check all controls? → Read `docs/reference/CONTROL-INDEX.md`
- Review rules? → Read `CONTRIBUTING.md`
- Understand regulations? → Read `docs/reference/regulatory-mappings.md`
- See role names? → Read `docs/reference/role-catalog.md`
- Understand zones? → Read `docs/getting-started/zones.md`

---

## Support & Questions

**For questions about:**
- **Documentation structure:** See `.github/copilot-instructions.md`
- **Autonomous workflows:** See `AGENTS.md`
- **Language rules:** See `CONTRIBUTING.md`
- **This Claude Code guide:** You're reading it!

**Need to contact maintainers?**
See individual control files' Section 11 (Support & Questions) for role-based contacts.

---

## Version Info
- **Framework Version:** 1.0 (January 2026)
- **Last Updated:** January 2026
- **Repository:** https://github.com/judeper/FSI-AgentGov
