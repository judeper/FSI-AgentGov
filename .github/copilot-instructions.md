# FSI-AgentGov Repository Instructions

## Project Overview

FSI Agent Governance Framework v1.3.5 - A governance framework for Microsoft 365 AI agents (Copilot Studio, Agent Builder) in US financial services organizations.

- **78 controls** across 4 pillars (Security, Management, Reporting, SharePoint)
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

### Key Reference Materials
- **CSA Quick Reference** (`docs/reference/csa-quick-reference.md`) — partner/CSA engagement summary
- **CSA Positioning Guide** (`docs/reference/csa-positioning-guide.md`) — positioning for CSA conversations
- **Automation indicators** — the current control catalog includes automation feasibility indicators
- **Exportable diagrams** — PNG/SVG architecture diagrams in `docs/images/diagrams/`

### Screenshots
- **LOCAL ONLY** - never push to GitHub
- Used to verify portal instructions stay current with UI changes
- Each control folder has `EXPECTED.md` listing required screenshots (no images are committed)
- Store screenshots and tenant evidence under `maintainers-local/tenant-evidence/` (gitignored)

### Navigation Philosophy (Three-Layer Model)
- **Framework:** Governance principles, strategy, organizational context (`docs/framework/`)
- **Controls:** Technical specifications with 10-section format (`docs/controls/pillar-*/`)
- **Playbooks:** Step-by-step implementation procedures (`docs/playbooks/`) - Standard control implementation playbooks are fully integrated into `mkdocs.yml` navigation (4 per control), with supplemental control-specific guides where needed
- **Reference:** Supporting materials (glossary, RACI, regulatory mappings, license requirements)
- **Assessment:** Interactive governance readiness assessment tool (client-side JavaScript)
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
│   ├── governance-fundamentals.md # Core framework concepts and structure
│   ├── zones-and-tiers.md        # Zone 1/2/3 definitions
│   ├── agent-lifecycle.md        # Agent lifecycle management
│   ├── regulatory-framework.md   # US regulatory requirements and control mappings
│   ├── operating-model.md        # RACI, roles, governance structure
│   ├── governance-cadence.md     # Review schedules and audit readiness
│   ├── adoption-roadmap.md       # 30/60/90-day phased implementation
│   └── index.md
├── controls/                     # RENAMED in v1.1 (was: reference/pillar-*)
│   ├── pillar-1-security/        # 29 security controls (1.1-1.29)
│   ├── pillar-2-management/      # 26 management controls (2.1-2.26)
│   ├── pillar-3-reporting/       # 14 reporting controls (3.1-3.14)
│   ├── pillar-4-sharepoint/      # 9 SharePoint controls (4.1-4.9)
│   └── CONTROL-INDEX.md          # Master control list
├── playbooks/                    # NEW in v1.1: Implementation layer
│   ├── control-implementations/  # Per-control guides (312 standard playbooks + 2 supplemental control guides)
│   ├── governance-operations/    # Standing procedures
│   ├── compliance-and-audit/     # Audit preparation guides
│   ├── incident-and-risk/        # Incident handling procedures
│   └── agent-lifecycle/          # Agent lifecycle management
├── assessment/                   # Interactive readiness assessment tool
├── reference/                    # Supporting materials
│   ├── role-catalog.md
│   ├── regulatory-mappings.md
│   ├── glossary.md
│   └── ...
├── templates/                    # Control authoring template
├── images/                       # Screenshot verification (LOCAL ONLY - gitignored)
└── downloads/                    # Excel templates for admins
scripts/                          # Validation scripts (verify_controls.py, verify_templates.py, extract_assessment_data.py)
assessment/                       # Automated assessment engine (collectors, scoring, reports)
│   ├── manifest/controls.json        # Machine-readable 78-control definitions
│   ├── collectors/                   # 5 PowerShell data collectors (PPAC, Graph, Purview, SharePoint, Sentinel)
│   ├── engine/                       # Python scoring (score.py) and report generator (report.py)
│   ├── tests/                        # pytest tests with fixture data
│   ├── run-assessment.ps1            # Main orchestrator
│   └── output/                       # Run outputs (gitignored — customer data)
releases/                         # Release artifacts by version
mkdocs.yml                        # Site navigation and configuration
.config/wt.toml                   # Worktrunk project hooks (worktree management)

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
8. Implementation Playbooks (links to 4 playbooks)
9. Verification Criteria (verification checklist)
10. Additional Resources (Microsoft Learn links)

**Footer Metadata:**
- *Updated: Month-Year | Version: v1.3 | UI Verification Status: Current*

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
| `docs/controls/CONTROL-INDEX.md` | Master list of all 78 controls |
| `mkdocs.yml` | Site navigation structure |

## Claude Code Skills (On-Demand Workflows)

For Claude Code users, detailed workflows are available as on-demand skills in `.claude/skills/`:

| Skill | Use When |
|-------|----------|
| `/update-control` | Modifying existing control content |
| `/add-control` | Adding a new control to a pillar |
| `/update-excel` | Maintaining Excel checklist templates |
| `/verify-ui` | Verifying portal screenshots match documentation |
| `/review-learn-changes` | Reviewing Learn Monitor change reports and drafting documentation updates |

These skills provide step-by-step instructions and are loaded only when invoked.

## Multi-Agent Configuration

This repository supports three AI tools and uses [Worktrunk](https://worktrunk.dev/) for parallel agent runs via git worktrees:

| Tool | Config | Primary Role |
|------|--------|-------------|
| GitHub Copilot | `.github/agents/`, `.github/prompts/`, `.github/instructions/` | Documentation generation |
| Claude Code | `.claude/CLAUDE.md`, `.claude/skills/` | Verification and QA |
| Codex CLI | `.codex/config.toml` | Documentation generation |
| Worktrunk | `.config/wt.toml` | Worktree management for parallel agent runs |

**Parallel agent runs:** Use `git-wt switch --create branch-name` to create isolated worktrees for each agent session. On Windows, use `git-wt` (winget installs it alongside `wt` to avoid the Windows Terminal conflict). See `AGENTS.md` "Parallel Agent Runs with Worktrunk" for full details.

### Custom Agents (13)
Located in `.github/agents/`: `doc-writer`, `doc-verifier`, plus 11 GSD workflow agents (`gsd-planner`, `gsd-executor`, `gsd-verifier`, `gsd-debugger`, `gsd-codebase-mapper`, `gsd-roadmapper`, `gsd-project-researcher`, `gsd-phase-researcher`, `gsd-research-synthesizer`, `gsd-integration-checker`, `gsd-plan-checker`).

### GSD Prompts (32)
Located in `.github/prompts/`. Use `/gsd-execute-phase`, `/gsd-plan-phase`, etc.

### Instruction Files (12)
Located in `.github/instructions/`. Auto-included by `applyTo` glob patterns.

### VS Code Setup
Add to your `.vscode/settings.json`:
```json
{
  "github.copilot.chat.codeGeneration.useInstructionFiles": true,
  "chat.promptFilesLocations": {
    ".github/prompts": true
  },
  "chat.instructionsFilesLocations": {
    ".github/instructions": true
  }
}
```

### If `/gsd-*` prompts don't show up

If built-in slash commands appear but the workspace prompts under `.github/prompts/` do not, the repo structure is usually fine and the issue is typically one of these:

- **Workspace Trust / Restricted Mode**: prompt files may be skipped when the workspace isn't trusted.
- **Outdated VS Code**: prompt files are a relatively new feature; update VS Code to a current stable release.
- **Load/parse errors**: a specific prompt file can fail to load due to malformed YAML frontmatter.
- **Org policy**: some enterprises restrict chat customization features.

Fastest way to see the exact reason:

1. Open the **Chat** view.
2. **Right-click** in the Chat view and select **Diagnostics**.
3. In the diagnostics report, look for **Prompt files** and confirm your workspace prompts are listed as **Loaded** (or read the error message if they are **Skipped/Failed**).

### Session Ownership
Check `.planning/STATE.md` Active Tool field before writing to shared GSD state files.
See `AGENTS.md` Multi-Agent Coordination section for full protocol.

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

# Run assessment engine tests
cd assessment && pip install -r requirements.txt && pytest tests/ -v
```

## Automated Assessment Engine

The `assessment/` directory contains a programmatic assessment engine that collects Microsoft 365 tenant configuration via APIs, scores all 78 controls against zone thresholds, and generates pre-filled assessment reports.

**Key components:**
- `manifest/controls.json` — machine-readable definitions for all 78 controls with checks, zone thresholds, and manual questions
- `collectors/` — 5 PowerShell collectors (PPAC, Graph, Purview, SharePoint, Sentinel) that write JSON to `output/collected/`
- `engine/score.py` — evaluates checks against collected data, derives maturity scores (0–4)
- `engine/report.py` — generates `assessment-prefilled.md`, `manual-questionnaire.md`, and `assessment-summary.json`
- `run-assessment.ps1` — orchestrator with `-Zone`, `-AuthMode`, `-SkipCollectors` parameters

**Usage:** `.\assessment\run-assessment.ps1 -TenantId <id> -Zone 2 -AuthMode Interactive -CustomerName "Contoso"`

See `assessment/README.md` for full prerequisites and usage documentation.

## Worktree Management (Parallel Agent Runs)

```bash
# Create a new worktree for an agent session (Windows: use git-wt)
git-wt switch --create feature-branch

# List all worktrees with status
git-wt list

# Merge worktree back to main (runs pre-merge hooks)
git-wt merge main

# Remove worktree after merge
git-wt remove
```

Project hooks in `.config/wt.toml` automatically copy dependencies on create and validate docs before merge.

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
