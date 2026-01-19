# FSI-AgentGov Repository - Claude Code Instructions

## Project Overview

**FSI Agent Governance Framework v1.1** - A governance framework for Microsoft 365 AI agents (Copilot Studio, Agent Builder) in US financial services organizations.

### Key Stats
- **60 controls** across 4 pillars (Security, Management, Reporting, SharePoint)
- **3 governance zones** (Personal Productivity, Team Collaboration, Enterprise Managed)
- **3-layer documentation** (Framework → Controls → Playbooks)
- **Target regulations:** FINRA 4511/3110/25-07, SEC 17a-3/4, SOX 302/404, GLBA 501(b), OCC 2011-12, Fed SR 11-7, CFTC 1.31
- **Documentation:** MkDocs Material-based site published to GitHub Pages
- **Audience:** M365 administrators in US financial services

---

## Before Starting Any Task

Read these files for full repository context:
1. **`.github/copilot-instructions.md`** - Full repository structure and design decisions
2. **`AGENTS.md`** - Instructions for autonomous agent tasks (vs. interactive work)
3. **`docs/templates/control-setup-template.md`** - The 10-section control template
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
│   ├── framework/                # NEW in v1.1: Governance principles layer
│   │   ├── executive-summary.md  # Strategic overview for leadership
│   │   ├── zones-and-tiers.md    # Governance zone definitions
│   │   ├── adoption-roadmap.md   # Phased implementation approach
│   │   └── ...                   # Lifecycle, roles, risk framework
│   ├── controls/                 # RENAMED in v1.1 (was: reference/pillar-*)
│   │   ├── pillar-1-security/    # Controls 1.1-1.23 (23 controls)
│   │   ├── pillar-2-management/  # Controls 2.1-2.20 (20 controls)
│   │   ├── pillar-3-reporting/   # Controls 3.1-3.10 (10 controls)
│   │   ├── pillar-4-sharepoint/  # Controls 4.1-4.7 (7 controls)
│   │   └── CONTROL-INDEX.md      # Master control list
│   ├── playbooks/                # NEW in v1.1: Implementation layer
│   │   ├── control-implementations/  # Per-control guides (240 files)
│   │   ├── governance-operations/    # Standing governance procedures
│   │   ├── compliance-and-audit/     # Audit preparation guides
│   │   ├── incident-response/        # Incident handling procedures
│   │   └── lifecycle-operations/     # Agent lifecycle management
│   ├── reference/                # Supporting materials
│   │   ├── role-catalog.md       # Canonical role names
│   │   ├── regulatory-mappings.md # Regulation-to-control mapping
│   │   ├── glossary.md           # Term definitions
│   │   └── ...                   # License requirements, FAQ
│   ├── templates/                # Control authoring template
│   ├── images/                   # Screenshot verification specs (LOCAL ONLY)
│   └── downloads/                # Excel templates for admins
├── scripts/                      # Python validation scripts
├── maintainers-local/            # LOCAL ONLY - gitignored (reports, notes, evidence)
├── releases/                     # Release artifacts by version
├── mkdocs.yml                    # Site navigation and MkDocs config
├── AGENTS.md                     # Agent workflow instructions
├── CONTRIBUTING.md               # Language and style guidelines
├── README.md                     # Repository home page
├── CHANGELOG.md                  # Release history
├── SECURITY.md                   # Security policy
└── [LICENSE, CODE_OF_CONDUCT.md, etc.]
```

---

## Three-Layer Documentation Architecture (v1.1)

The framework uses a three-layer documentation model:

### Layer 1: Framework (`docs/framework/`)
**Purpose:** Governance principles, strategy, and organizational context

| File | Content |
|------|---------|
| `executive-summary.md` | Strategic overview for leadership buy-in |
| `zones-and-tiers.md` | Zone 1/2/3 definitions with governance levels |
| `adoption-roadmap.md` | 30/60/90-day phased implementation |
| `agent-lifecycle.md` | Agent lifecycle management process |
| `operating-model.md` | RACI and accountability model |
| `governance-fundamentals.md` | Core governance principles and concepts |
| `governance-cadence.md` | Recurring governance activities and timelines |
| `regulatory-framework.md` | Financial services regulatory landscape |
| `index.md` | Framework layer overview |

### Layer 2: Control Catalog (`docs/controls/pillar-*`)
**Purpose:** Technical control specifications with 10-section format

- **Pillar 1 - Security:** 23 controls (1.1-1.23) - Data protection, access, audit
- **Pillar 2 - Management:** 20 controls (2.1-2.20) - Lifecycle, risk, operations
- **Pillar 3 - Reporting:** 10 controls (3.1-3.10) - Visibility, metrics, dashboards
- **Pillar 4 - SharePoint:** 7 controls (4.1-4.7) - Content governance, grounding

### Layer 3: Playbooks (`docs/playbooks/`)
**Purpose:** Step-by-step implementation procedures

| Category | Content |
|----------|---------|
| `control-implementations/` | 4 playbooks per control (admin, lifecycle, validation, troubleshooting) |
| `governance-operations/` | Standing procedures (weekly reviews, quarterly assessments) |
| `compliance-and-audit/` | Audit preparation, evidence collection |
| `incident-response/` | Data exposure, compliance violation handling |
| `lifecycle-operations/` | Agent provisioning, retirement, updates |

---

## Common Claude Code Workflows

### 1. Update Existing Control

**Scenario:** You need to modify a control's content (e.g., update instructions for a step, fix a typo, add new regulation reference)

**Steps:**
1. **Read the control** you're updating: `docs/controls/pillar-{1-4}-{name}/{id}-{kebab-case}.md`
2. **Read the template** for structure: `docs/templates/control-setup-template.md`
3. **Make changes** while preserving all 10 sections (never skip or remove a section)
4. **Update footer date:** Change "Updated: Month-Year" to current date
5. **If portal paths changed:** Update `docs/images/{control-id}/EXPECTED.md` with new screenshot requirements
6. **Update related playbooks:** Check `docs/playbooks/control-implementations/` for impacted guides
7. **Validate:** Run `mkdocs build --strict` (must pass with zero errors)

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
2. **Paste into correct pillar folder** with proper naming: `docs/controls/pillar-{n}-{name}/{id}-{kebab-case-name}.md`
   - Example: `docs/controls/pillar-1-security/1.24-new-control-example.md`
3. **Fill ALL 10 sections** (do not skip any):
   - Header metadata (Control ID, Pillar, Regulatory Reference, Last UI Verified, Governance Levels)
   - Section 1: Objective (concise purpose statement)
   - Section 2: Why This Matters for FSI (regulatory bullet points)
   - Section 3: Control Description (detailed technical explanation)
   - Section 4: Key Configuration Points (bulleted configuration items)
   - Section 5: Zone-Specific Requirements (Zone 1/2/3 table)
   - Section 6: Roles & Responsibilities (admin roles table)
   - Section 7: Related Controls (cross-reference table)
   - Section 8: Implementation Guides (links to 4 playbooks)
   - Section 9: Verification Criteria (verification checklist)
   - Section 10: Additional Resources (Microsoft Learn links)
   - Footer metadata (Updated: Month-Year | Version: v1.1 | UI Verification Status)
4. **Update CONTROL-INDEX.md:** Add entry to master control list at `docs/controls/CONTROL-INDEX.md`
5. **Update mkdocs.yml:** Add entry to navigation under correct pillar
6. **Create screenshot spec:** `docs/images/{control-id}/EXPECTED.md` with required screenshots
7. **Create playbooks:** Add 4 playbook files in `docs/playbooks/control-implementations/{control-id}/`
8. **Validate:** Run `mkdocs build --strict` (must pass with zero errors)

### 3. Verify Screenshots

**Scenario:** You need to check if control documentation matches actual portal UI

**Steps:**
1. **Read the control** doc: `docs/controls/pillar-{n}-*/`
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
- Keep three-layer structure: Framework → Controls → Playbooks
- Validate after changes: `mkdocs build --strict`

**Example nav entry:**
```yaml
- Framework:
  - Framework Overview: framework/index.md
  - Executive Summary: framework/executive-summary.md
  # ... other framework docs

- Controls:
  - Control Index: controls/CONTROL-INDEX.md
  - Pillar 1 - Security:
    - Pillar 1 Overview: controls/pillar-1-security/index.md
    - 1.1 - Control Name: controls/pillar-1-security/1.1-control-name.md
    # ... maintain numerical order

- Playbooks:
  - Implementation Guides: playbooks/control-implementations/index.md
  # ... playbook categories
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
| `.github/copilot-instructions.md` | Copilot context | Update when structure changes |
| `AGENTS.md` | Autonomous agent workflows | Reference only |
| `docs/templates/control-setup-template.md` | Control authoring template | Reference only |
| `CONTRIBUTING.md` | Language and style rules | Update if rules change |
| `mkdocs.yml` | Site navigation and config | Update for nav changes |
| `docs/controls/CONTROL-INDEX.md` | Master control list | Update when controls added/removed |
| `docs/framework/*.md` | Governance principles | Update for strategic changes |
| `docs/playbooks/**/*.md` | Implementation guides | Update when procedures change |
| `LICENSE` | Legal file | Never modify without permission |
| `SECURITY.md` | Security policy | Never modify without permission |
| `CODE_OF_CONDUCT.md` | Community standards | Never modify without permission |
| Individual control files `docs/controls/pillar-*/` | Control documentation | Update following template |

---

## Excel Download Templates

The framework includes Excel checklists for administrators in `docs/downloads/`. When adding new controls, these templates must be updated.

### Template Files and Their Control Counts

| File | Role | Controls | Notes |
|------|------|----------|-------|
| `governance-maturity-dashboard.xlsx` | AI Governance Lead | 60 (all) | Has "All Controls" + "Summary Dashboard" sheets |
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
1. Check `docs/controls/CONTROL-INDEX.md` to verify control exists
2. Verify file path: `docs/controls/pillar-{n}-{name}/{id}-{kebab-case}.md`
3. Update the reference with correct control ID

### Error: "Control missing section X"
**Cause:** Control file doesn't include all 10 required sections
**Solution:**
1. Read `docs/templates/control-setup-template.md` for the 10 sections
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
1. Use forward slashes in all links: `docs/controls/...` not `docs\controls\...`
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
1. Read all 23 Pillar 1 controls
2. Identify their current Zone 1 guidance
3. Present proposed updates for your review
4. Apply consistent changes across all files

---

## Researcher Package

The framework maintains a compiled "researcher package" for external reviewers to assess regulatory accuracy and identify gaps. This package is stored locally and not committed to the repository.

### Location

`maintainers-local/researcher-package/`

### Contents

| File | Contents |
|------|----------|
| `00-FSI-AgentGov-Summary-and-Review-Guide.md` | Framework overview, reviewer guidance, control index |
| `01-Pillar-1-Security-Controls.md` | Controls 1.1-1.23 (23 controls) |
| `02-Pillar-2-Management-Controls.md` | Controls 2.1-2.20 (20 controls) |
| `03-Pillar-3-Reporting-Controls.md` | Controls 3.1-3.10 (10 controls) |
| `04-Pillar-4-SharePoint-Controls.md` | Controls 4.1-4.7 (7 controls) |

### Regenerating the Package

When pillar controls are updated, regenerate the package:

```bash
python scripts/compile_researcher_package.py
```

### Automatic Reminder Hook

A Claude Code hook (`PostToolUse`) is configured to remind you to regenerate the researcher package when pillar control files are edited. The hook is defined in `.claude/settings.local.json` and runs `scripts/hooks/researcher-package-reminder.py`.

### Project Boundary Check Hook

A `PreToolUse` hook is configured to prevent Bash commands from accidentally operating outside the project directory. The hook intercepts all Bash tool invocations and blocks commands that might escape `C:\dev\FSI-AgentGov`.

**Blocked patterns include:**
- Absolute paths to other drives or directories (e.g., `C:\Users`, `/c/Windows`)
- Root-level find/ls/dir operations
- Excessive parent directory traversal

**Safe patterns allowed:**
- Commands explicitly targeting the project path
- Git, mkdocs, python, pip commands
- Relative path operations

The hook is defined in `.claude/settings.local.json` and runs `scripts/hooks/boundary-check.py`.

---

## Quick Navigation

**Want to...**
- Add a new control? → Start with `docs/templates/control-setup-template.md`
- Update site menu? → Edit `mkdocs.yml` navigation section
- Check all controls? → Read `docs/controls/CONTROL-INDEX.md`
- Review rules? → Read `CONTRIBUTING.md`
- Understand regulations? → Read `docs/reference/regulatory-mappings.md`
- See role names? → Read `docs/reference/role-catalog.md`
- Understand zones? → Read `docs/framework/zones-and-tiers.md`
- Read framework docs? → Browse `docs/framework/`
- Find playbooks? → Browse `docs/playbooks/`

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

## Recent Work Context (January 2026)

This section provides context for new Claude Code sessions about recent major changes.

### v1.1 Restructuring Complete (January 18, 2026)

The framework underwent a major restructuring from a flat documentation model to a three-layer architecture:

#### What Was Done

1. **Created Framework Layer** (`docs/framework/`)
   - 9 documents covering governance principles, zones, lifecycle, operating model, regulatory context
   - Target audience: executives, compliance officers, governance leads

2. **Reorganized Controls** (`docs/controls/`)
   - Moved from `docs/reference/pillar-*/` to `docs/controls/pillar-*/`
   - 60 controls across 4 pillars remain unchanged in content
   - Updated all cross-references and navigation

3. **Created 240 Playbooks** (`docs/playbooks/control-implementations/`)
   - 4 playbooks per control (60 × 4 = 240 files)
   - Each control has: portal-walkthrough, powershell-setup, verification-testing, troubleshooting
   - Playbooks contain step-by-step implementation details

4. **Fixed Build Issues**
   - Fixed 6 broken cross-references between controls
   - Fixed relative path issues in playbooks (1.1, 3.1, 3.2)
   - Build now passes with no link errors

#### Current State

| Component | Status | Location |
|-----------|--------|----------|
| Framework docs | Complete | `docs/framework/` (9 files) |
| Control catalog | Complete | `docs/controls/pillar-*/` (60 files) |
| Playbooks | Complete | `docs/playbooks/control-implementations/` (240 files) |
| Navigation | Complete | `mkdocs.yml` updated |
| Cross-references | Fixed | All links working |
| Build validation | Passing | `mkdocs build` succeeds |

#### Files Modified in v1.1

| File | Changes |
|------|---------|
| `.claude/claude.md` | Updated for three-layer architecture |
| `.github/copilot-instructions.md` | Updated directory structure, counts |
| `mkdocs.yml` | Three-layer navigation structure |
| `CHANGELOG.md` | Detailed v1.1 release notes |
| `scripts/verify_controls.py` | Path updated to `docs/controls/` |
| `scripts/compile_researcher_package.py` | Path updated to `docs/controls/` |
| `scripts/hooks/researcher-package-reminder.py` | Supports both old and new paths |

#### Known Issues / Future Work

| Item | Priority | Notes |
|------|----------|-------|
| PowerShell scripts in `scripts/governance/` | Medium | Placeholder directories; implement actual scripts |
| PowerShell scripts in `scripts/reporting/` | Medium | Placeholder directories; implement actual scripts |

#### v1.1 Legacy Cleanup (January 18, 2026)

Removed legacy/duplicate files to streamline the repository:
- Deleted `docs/reference/pillar-*/` (64 files) - superseded by `docs/controls/pillar-*/`
- Deleted `docs/operational-templates/` (21 files) - migrated to `docs/playbooks/`
- Deleted 4 excluded getting-started files (duplicates of framework layer)
- Updated `mkdocs.yml` exclude_docs section
- Fixed `docs/downloads/index.md` (58→60 controls, v1.0→v1.1)

#### v1.1 Documentation Cleanup (January 18, 2026)

Fixed stale documentation after v1.1 restructuring:

| File | Issue | Fix |
|------|-------|-----|
| `docs/reference/regulatory-mappings.md` | Broken hyperlink to deleted `../operational-templates/...` | Updated to `../playbooks/regulatory-modules/...` |
| `docs/getting-started/checklist.md` | Control counts (48→60), version (v1.0→v1.1) | Updated all pillar counts and version footer |
| `docs/reference/faq.md` | Control counts (48→60) | Updated all pillar counts |
| `docs/images/README.md` | Old paths `docs/reference/pillar-*` | Updated to `docs/controls/pillar-*` |
| `docs/images/VERIFY.md` | Old path pattern | Updated to `docs/controls/...` |
| `docs/templates/README.md` | Non-existent JSON files, old count (48) | Removed JSON references, updated to 60 controls |
| `mkdocs.yml` | 240 playbook "not in nav" warnings | Added `playbooks/control-implementations/*/` to exclude_docs |

#### v1.1 Deep Verification (January 18, 2026)

Comprehensive verification of all documentation after v1.1 restructuring:

**Verified Clean:**
- All 60 controls present with correct 10-section structure
- All 240 playbooks present with complete content
- All internal cross-references working
- No placeholder/TODO content in controls
- Build passes with `mkdocs build --strict`

**Fixed Issues:**

| File | Issue | Fix |
|------|-------|-----|
| `scripts/refactor_controls_to_canonical_sections.py` | Legacy script with old paths | Deleted (marked LEGACY, unusable) |
| `scripts/normalize_controls.py:4` | Comment said "v1.0" | Updated to "v1.1" |
| `docs/reference/license-requirements.md:3` | Said "48 FSI Agent" | Updated to "60 FSI Agent" |
| `docs/images/README.md` | Said "48 possible folders" with old ranges | Updated to "60 possible folders" with correct ranges |
| `scripts/hooks/researcher-package-reminder.py` | Legacy path support in regex | Removed legacy `reference` path |
| `.github/workflows/publish_docs.yml:24` | Error message incomplete | Updated to mention both paths |
| `.github/workflows/link-check.yml:49` | Error message incomplete | Updated to mention both paths |

**Validation Results:**
- `mkdocs build --strict`: ✅ Pass
- `python scripts/verify_controls.py`: ✅ 60/60 controls valid
- `python scripts/verify_templates.py`: ✅ All templates valid
- Zero stale "48 controls" references in docs
- Zero active `docs/reference/pillar-*` paths (only in CHANGELOG)

#### v1.1 Comprehensive Repository Verification (January 18, 2026)

Exhaustive verification of ALL repository content including scripts, Excel files, and issue templates.

**Phase 1: Parallel Documentation Sweep (6 agents)**
- Framework layer (`docs/framework/`): ✅ Clean
- Reference directory (`docs/reference/`): 2 date fixes needed
- Control & playbook indexes: ✅ Clean
- Legacy scripts audit: 6 scripts identified for deletion
- GitHub & root files: ✅ Clean
- Getting-started & templates: ✅ Clean

**Phase 2: Excel Template Verification**
- Created `scripts/verify_excel_templates.py` for automated Excel validation
- Found: 6 files with "v1.0 Beta" references, dashboard missing 2 controls

**Phase 3: Remediation**

*Files Deleted (6 legacy scripts with stale `docs/reference/pillar-*` paths):*
- `scripts/apply_primary_owner_roles.py`
- `scripts/fix_zone_guidance_grammar.py`
- `scripts/tailor_zone_guidance.py`
- `scripts/fix_controls_targeted_cleanup.py`
- `scripts/audit_controls_zone_hygiene.py`
- `scripts/generate_zone_cleanup_plan.py`

*Documentation Fixed:*
| File | Issue | Fix |
|------|-------|-----|
| `docs/reference/microsoft-learn-urls.md:140` | "December 2025" | Updated to "January 2026" |
| `docs/reference/faq.md:455` | "Dec 2025" | Updated to "Jan 2026" |

*Excel Templates Updated (all 6 files):*
| File | Changes |
|------|---------|
| `governance-maturity-dashboard.xlsx` | v1.0 Beta → v1.1, added controls 1.23 & 2.20 (58→60) |
| `compliance-officer-checklist.xlsx` | v1.0 Beta → v1.1 |
| `entra-administrator-checklist.xlsx` | v1.0 Beta → v1.1 |
| `power-platform-administrator-checklist.xlsx` | v1.0 Beta → v1.1 |
| `purview-administrator-checklist.xlsx` | v1.0 Beta → v1.1 |
| `sharepoint-administrator-checklist.xlsx` | v1.0 Beta → v1.1 |

*New Scripts Created:*
- `scripts/verify_excel_templates.py` - Validates Excel template content and counts
- `scripts/update_excel_templates.py` - Updates Excel templates (version refs, missing controls)

**Phase 4: Final Validation**
- `mkdocs build --strict`: ✅ Pass
- `python scripts/verify_controls.py`: ✅ 60/60 controls valid
- `python scripts/verify_templates.py`: ✅ All templates valid
- `python scripts/verify_excel_templates.py`: ✅ All 6 files pass
- Zero stale "48 control" references
- Zero stale `docs/reference/pillar-*` paths in active code
- Zero stale "v1.0" references (except CHANGELOG)

#### Playbook Structure Reference

Each control's playbooks follow this structure:

```
docs/playbooks/control-implementations/{control-id}/
├── portal-walkthrough.md    # Step-by-step portal configuration
├── powershell-setup.md      # PowerShell automation scripts
├── verification-testing.md  # Test cases, evidence collection, attestation
└── troubleshooting.md       # Common issues, resolutions, escalation
```

Each playbook contains:
- **Portal Walkthrough:** Prerequisites, numbered steps, screenshots locations, validation checklist
- **PowerShell Setup:** Module requirements, automated scripts, validation script
- **Verification Testing:** Manual test steps, test cases table, evidence checklist, attestation template
- **Troubleshooting:** Common issues table, detailed resolution steps, escalation path, known limitations

---

## Version Info
- **Framework Version:** 1.1 (January 2026)
- **Last Updated:** January 18, 2026
- **Repository:** https://github.com/judeper/FSI-AgentGov
