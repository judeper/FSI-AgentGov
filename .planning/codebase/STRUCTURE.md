# Codebase Structure

**Analysis Date:** 2026-02-02
**⚠️ Staleness Note:** This snapshot pre-dates v20.5 (added 9 controls, 62→71, 248→284 playbooks) and v23 (deleted src/, migrated solutions to companion repo). Counts and directory references below may be outdated.

## Directory Layout

```
FSI-AgentGov/
├── .claude/                       # Claude Code configuration
│   ├── CLAUDE.md                 # Comprehensive project instructions and context
│   ├── settings.json             # Team-shared Claude Code settings
│   ├── settings.local.json       # Local overrides (not committed)
│   ├── skills/                   # On-demand workflow guides
│   └── sessions/                 # Claude Code session history
├── .github/                       # GitHub automation
│   ├── workflows/                # GitHub Actions
│   │   ├── learn-monitor.yml    # Daily Microsoft Learn change detection
│   │   ├── link-check.yml       # Weekly external link validation
│   │   └── publish_docs.yml     # Auto-publish to GitHub Pages on main push
│   └── copilot-instructions.md  # Full repository structure documentation
├── .planning/                     # GSD (Generalized Skeleton Documentation) planning
│   └── codebase/                # Codebase mapping documents (output location)
├── docs/                          # MkDocs source documentation
│   ├── framework/                # Layer 1: Governance principles (11 files)
│   │   ├── index.md             # Framework overview
│   │   ├── executive-summary.md
│   │   ├── governance-fundamentals.md
│   │   ├── zones-and-tiers.md
│   │   ├── agent-lifecycle.md
│   │   ├── agent-identity-architecture.md
│   │   ├── regulatory-framework.md
│   │   ├── operating-model.md
│   │   ├── governance-cadence.md
│   │   ├── adoption-roadmap.md
│   │   └── solutions-integration.md
│   ├── controls/                 # Layer 2: Control catalog (71 controls)
│   │   ├── CONTROL-INDEX.md     # Master control list with links
│   │   ├── index.md             # Control overview
│   │   ├── pillar-1-security/   # 28 controls (1.1-1.28)
│   │   ├── pillar-2-management/ # 24 controls (2.1-2.24)
│   │   ├── pillar-3-reporting/  # 12 controls (3.1-3.12)
│   │   └── pillar-4-sharepoint/ # 7 controls (4.1-4.7)
│   ├── playbooks/                # Layer 3: Implementation guides
│   │   ├── control-implementations/  # 71 control dirs with 4 playbooks each (284 files)
│   │   │   ├── 1.1/               # Portal walkthrough, PowerShell, verification, troubleshooting
│   │   │   ├── 1.2/
│   │   │   ├── ... (through 4.7)
│   │   │   └── index.md           # Playbook index
│   │   ├── advanced-implementations/  # Complex multi-control solutions (27 files)
│   │   │   ├── platform-change-governance/     # Message Center governance playbook
│   │   │   ├── environment-lifecycle-management/ # ELM automated provisioning
│   │   │   ├── agent-365-observability/        # Telemetry & alerting
│   │   │   ├── agent-blueprint-promotion-gates/
│   │   │   ├── deny-event-correlation-report/
│   │   │   ├── sharepoint-copilot-preflight/
│   │   │   ├── human-in-the-loop-triggers.md
│   │   │   ├── confidence-and-routing.md
│   │   │   ├── zone1-min-explainability.md
│   │   │   ├── dspm-for-ai-policy-pack.md
│   │   │   ├── microsoft-audit-reporting-tools.md
│   │   │   └── index.md
│   │   ├── getting-started/      # Onboarding playbooks
│   │   ├── governance-operations/
│   │   ├── incident-and-risk/
│   │   ├── monitoring-and-validation/
│   │   ├── validation-testing/
│   │   ├── regulatory-modules/
│   │   ├── compliance-and-audit/
│   │   ├── agent-lifecycle/
│   │   └── index.md              # Playbooks overview
│   ├── reference/                 # Layer 4: Lookup tables & FAQs (20 files)
│   │   ├── index.md
│   │   ├── role-catalog.md       # Canonical role names for M365
│   │   ├── regulatory-mappings.md # 71 controls mapped to regulations
│   │   ├── control-setup-template.md (in templates/)
│   │   ├── solutions-index.md    # Catalog of FSI-AgentGov-Solutions
│   │   ├── solutions-integration.md (in framework/)
│   │   ├── solutions-architecture-guide.md
│   │   ├── solutions-coverage-gaps.md
│   │   ├── license-requirements.md
│   │   ├── nist-ai-rmf-crosswalk.md
│   │   ├── learn-monitor-guide.md
│   │   ├── learn-monitor-ai-enhancement.md
│   │   ├── agent-audit-event-taxonomy.md
│   │   ├── evidence-standards.md
│   │   ├── faq.md
│   │   ├── glossary.md
│   │   ├── agent-essentials-control-mapping.md
│   │   ├── fsi-configuration-examples.md
│   │   ├── portal-paths-quick-reference.md
│   │   ├── raci-matrix.md
│   │   ├── sharepoint-advanced-management-licensing.md
│   │   └── microsoft-learn-urls.md (monitored by Learn Monitor)
│   ├── images/                    # Control screenshots and diagrams
│   │   ├── 1.1/ through 4.7/     # One directory per control
│   │   └── (contains portal screenshots, decision trees, etc.)
│   ├── downloads/                 # Excel templates & checklists
│   ├── getting-started/           # Onboarding documentation
│   ├── stylesheets/               # Custom CSS
│   ├── templates/                 # Markdown templates
│   ├── scripts/                   # Script documentation
│   └── index.md                   # Site home page
├── scripts/                       # Python automation & validation (14 files)
│   ├── verify_controls.py        # Validates all 71 controls conform to template
│   ├── verify_excel_templates.py # Validates Excel checklist templates
│   ├── verify_templates.py
│   ├── learn_monitor.py          # Monitors 209 Microsoft Learn URLs for changes
│   ├── compile_researcher_package.py # Generates researcher research package
│   ├── normalize_controls.py     # Standardizes control formatting
│   ├── audit_control_metadata.py # Audits control metadata
│   ├── update_excel_templates.py # Updates Excel templates from control data
│   ├── validate_docs_anchors.py  # Validates markdown anchors
│   ├── validate_before_push.py   # Pre-commit validation
│   ├── extract_whitepaper_text.py
│   ├── check_temp.py
│   └── hooks/                     # Claude Code hooks
│       ├── boundary-check.py     # Prevents Bash commands outside project
│       └── researcher-package-reminder.py # Reminds to regenerate package after edits
├── data/                          # Runtime state (not committed)
│   ├── learn-monitor-state.json  # Hash state of 209 monitored URLs (updated daily)
│   └── .gitkeep
├── reports/                       # Generated reports (not committed)
│   └── learn-changes/            # Learn Monitor change detection reports
├── site/                          # MkDocs build output (not committed)
│   └── (HTML files generated by mkdocs build)
├── releases/                      # Historical version documentation
├── templates/                     # Markdown templates
├── maintainers-local/            # Local maintainer configurations
├── mkdocs.yml                    # MkDocs configuration & site navigation
├── README.md                      # Repository overview
├── CHANGELOG.md                  # Release history (v1.0 through v1.2.37)
├── CONTRIBUTING.md               # Language guidelines & style rules
├── AGENTS.md                      # Instructions for autonomous agent tasks
├── SECURITY.md                    # Security policy
├── DISCLAIMER.md                  # Legal disclaimer
├── LICENSE                        # MIT license
├── .gitignore
└── .markdown-link-check.json     # Link checker configuration
```

## Directory Purposes

**`.claude/` - Claude Code Configuration:**
- Purpose: Configure Claude Code behavior, skills, and automation
- Contains: CLAUDE.md (14KB, core instructions), settings.json (team-shared), settings.local.json (local overrides)
- Key files: CLAUDE.md documents all 71 controls, regulatory framework, FSI-AgentGov-Solutions companion repo, hooks

**`docs/framework/` - Governance Framework Layer:**
- Purpose: Define governance principles, zones, operating models, regulatory context
- Contains: 11 strategic documents (governance fundamentals, zones, agent lifecycle, regulatory framework)
- Key files:
  - `zones-and-tiers.md` - Zone 1/2/3 classification system
  - `regulatory-framework.md` - FINRA, SEC, SOX, GLBA, OCC, Fed, CFTC mapping
  - `adoption-roadmap.md` - Phased implementation with solution references
  - `solutions-integration.md` - Maps solutions to framework controls

**`docs/controls/` - Control Catalog Layer:**
- Purpose: Technical specifications for 71 granular governance controls
- Contains: Master index + 4 pillar directories with 71 control documents
- Organization: `pillar-{1-4}-{name}/` with controls numbered by pillar (1.1-1.24, 2.1-2.21, 3.1-3.10, 4.1-4.7)
- Key files:
  - `CONTROL-INDEX.md` - Master list with links to all controls and playbooks
  - Each control file: 10-section template (Objective, Description, Key Config, Zone Requirements, Roles, etc.)

**`docs/playbooks/control-implementations/` - Playbook Layer (Control-Specific):**
- Purpose: Step-by-step implementation guides for each control
- Contains: 71 control directories, each with 4 playbooks (284 files total)
- Structure: `{control-id}/portal-walkthrough.md`, `powershell-setup.md`, `verification-testing.md`, `troubleshooting.md`
- Pattern: Each control ID has identical 4-document structure

**`docs/playbooks/advanced-implementations/` - Playbook Layer (Multi-Control):**
- Purpose: Complex governance solutions spanning multiple controls
- Contains: 11 solution playbooks (6+ documents each)
- Key examples:
  - `platform-change-governance/` - Message Center monitoring with Dataverse (6 docs)
  - `environment-lifecycle-management/` - Automated environment provisioning (6 docs)
  - `agent-365-observability/` - Telemetry & alerting setup (6 docs)

**`docs/reference/` - Reference Layer:**
- Purpose: Lookup tables, FAQs, mapping documents, evidence standards
- Contains: 20 reference documents
- Key files:
  - `role-catalog.md` - Canonical M365 role names
  - `regulatory-mappings.md` - 71 controls mapped to regulations
  - `solutions-index.md` - Catalog of FSI-AgentGov-Solutions
  - `license-requirements.md` - SKU and licensing matrix
  - `evidence-standards.md` - What to collect for regulatory audits

**`docs/images/` - Control Screenshots & Diagrams:**
- Purpose: Visual reference materials for portal configurations
- Contains: One directory per control (1.1/ through 4.7/)
- Usage: Referenced in portal-walkthrough.md playbooks

**`scripts/` - Automation & Validation:**
- Purpose: Python utilities for validation, monitoring, and documentation generation
- Key scripts:
  - `verify_controls.py` - Validates all 71 controls conform to 10-section template
  - `learn_monitor.py` - Monitors 209 Microsoft Learn URLs; detects breaking changes
  - `compile_researcher_package.py` - Generates research package from control data
  - `hooks/boundary-check.py` - Claude Code hook preventing commands outside project
  - `hooks/researcher-package-reminder.py` - Reminds to regenerate package after edits

**`data/` - Runtime State:**
- Purpose: Persisted state files (not committed to git)
- Contents:
  - `learn-monitor-state.json` - Hash state of 209 monitored Microsoft Learn URLs (updated daily by Learn Monitor workflow)

**`reports/` - Generated Reports:**
- Purpose: Audit and compliance reports (not committed)
- Contents:
  - `learn-changes/` - Learn Monitor change detection reports (one per day)

**`site/` - MkDocs Build Output:**
- Purpose: Compiled HTML documentation (not committed)
- Generated by: `mkdocs build` command
- Deployed to: GitHub Pages via GitHub Actions

## Key File Locations

**Entry Points:**

- `docs/index.md` - Site home page; compiled to GitHub Pages
- `docs/getting-started/quick-start.md` - Quick start guide for new users
- `docs/controls/CONTROL-INDEX.md` - Master control list with all 71 controls

**Configuration:**

- `mkdocs.yml` - MkDocs site navigation and configuration (42KB)
- `.claude/CLAUDE.md` - Comprehensive Claude Code instructions
- `.claude/settings.json` - Team-shared Claude Code settings
- `.github/workflows/` - GitHub Actions automation (learn-monitor, link-check, publish_docs)

**Core Logic:**

- `docs/templates/control-setup-template.md` - 10-section control template (enforced by validation)
- `docs/controls/pillar-*/` - 71 control specifications
- `docs/playbooks/control-implementations/*/` - 248 control implementation playbooks
- `docs/playbooks/advanced-implementations/*/` - 27 complex multi-control solution documents

**Testing & Validation:**

- `scripts/verify_controls.py` - Control structure validation
- `scripts/verify_excel_templates.py` - Excel template validation
- `scripts/learn_monitor.py` - Microsoft Learn URL monitoring
- `.github/workflows/link-check.yml` - External link validation (weekly)
- `.github/workflows/publish_docs.yml` - Build & deploy validation

**Regulatory & Reference:**

- `docs/reference/regulatory-mappings.md` - 71 controls to regulations mapping
- `docs/reference/role-catalog.md` - Canonical role names
- `docs/reference/solutions-index.md` - FSI-AgentGov-Solutions catalog
- `docs/framework/regulatory-framework.md` - Regulatory overview

## Naming Conventions

**Files:**

- Control documents: `{pillar-number}-{control-slug}.md` (e.g., `1.1-restrict-agent-publishing-by-authorization.md`)
- Playbook playbooks: Standard names: `portal-walkthrough.md`, `powershell-setup.md`, `verification-testing.md`, `troubleshooting.md`
- Advanced implementations: `{solution-name}/index.md` + supporting documents
- Reference documents: Descriptive lowercase with hyphens (e.g., `role-catalog.md`, `regulatory-mappings.md`)

**Directories:**

- Pillar directories: `pillar-{number}-{name}` (e.g., `pillar-1-security`)
- Control playbook directories: Control ID only (e.g., `1.1/`, `2.12/`)
- Advanced implementation directories: Solution name with hyphens (e.g., `environment-lifecycle-management/`)
- Image directories: Control ID only (e.g., `docs/images/1.1/`, `docs/images/3.9/`)

**Variables in YAML Front-Matter:**

- Control ID format: `1.1`, `2.12` (number dot number)
- Pillar format: `Security`, `Management`, `Reporting`, `SharePoint`
- Zone format: `Zone 1`, `Zone 2`, `Zone 3`
- Governance Levels: `Baseline / Recommended / Regulated` (slash-separated on single line)

## Where to Add New Code

**New Control:**

- Control specification: `docs/controls/pillar-{1-4}-{name}/{control-id}-{slug}.md` (use 10-section template from `docs/templates/control-setup-template.md`)
- Playbook directory: `docs/playbooks/control-implementations/{control-id}/` with 4 files
- Update: `docs/controls/CONTROL-INDEX.md` to add control row
- Update: `mkdocs.yml` to add control to navigation
- Run: `python scripts/verify_controls.py` to validate

**New Framework Document:**

- Location: `docs/framework/{document-slug}.md`
- Update: `mkdocs.yml` under Framework section
- Reference: From control documents and adoption roadmap

**New Playbook (Advanced/Multi-Control):**

- Location: `docs/playbooks/advanced-implementations/{solution-name}/`
- Create: `index.md` + supporting documentation
- Update: `mkdocs.yml` under Playbooks section
- Document: Control cross-references and architecture diagrams

**New Reference Document:**

- Location: `docs/reference/{document-slug}.md`
- Update: `mkdocs.yml` under Reference section (if navigable) or `mkdocs.yml` exclude_docs (if lookup-only)
- Examples: `regulatory-mappings.md` (excluded, linked internally), `role-catalog.md` (excluded, linked internally)

**New Script or Automation:**

- Location: `scripts/{script-name}.py` or `scripts/hooks/{hook-name}.py`
- Register in: `.claude/settings.json` for hooks; GitHub Actions for workflows
- Example: Learn Monitor registered in `learn-monitor.yml` workflow

**New Image/Screenshot:**

- Location: `docs/images/{control-id}/` (one directory per control)
- Reference: From `portal-walkthrough.md` files with relative paths: `../../../images/{control-id}/{filename}.png`

## Special Directories

**`site/` - MkDocs Build Output:**
- Purpose: Generated HTML documentation
- Generated: By running `mkdocs build`
- Committed: No (in .gitignore)
- Deployment: GitHub Actions publishes to GitHub Pages on push to main

**`data/` - Runtime State:**
- Purpose: Persisted state files for automation
- Generated: By `scripts/learn_monitor.py` (daily scheduled task)
- Committed: Yes (but .gitkeep only; state file is tracked)
- Usage: Learn Monitor tracks hash state of 209 Microsoft Learn URLs

**`reports/` - Generated Reports:**
- Purpose: Audit outputs (Learn Monitor change reports)
- Generated: By `scripts/learn_monitor.py` and GitHub Actions
- Committed: No (in .gitignore)
- Usage: PR body content when breaking Learn changes detected

**`releases/` - Historical Versions:**
- Purpose: Archive of previous framework versions
- Contains: `v1.1/` subdirectory
- Committed: Yes
- Usage: Reference for version history

**`maintainers-local/` - Maintainer Configurations:**
- Purpose: Local development configurations
- Committed: Yes
- Usage: Maintainer-specific setups (not used by standard workflow)

---

*Structure analysis: 2026-02-02*
