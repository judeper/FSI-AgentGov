# FSI-AgentGov Repository - Claude Code Instructions

## Project Overview

**FSI Agent Governance Framework v1.6.2** - A governance framework for Microsoft 365 AI agents (Copilot Studio, Agent Builder) in US financial services organizations.

### Key Stats
- **78 controls** across 4 pillars (Security, Management, Reporting, SharePoint)
- **3 governance zones** (Personal Productivity, Team Collaboration, Enterprise Managed)
- **3-layer documentation** (Framework → Controls → Playbooks)
- **6 advanced implementations** (Platform Change Governance, Environment Lifecycle Management, Agent 365 Observability, etc.)
- **Target regulations:** FINRA 4511/3110/25-07, SEC 17a-3/4, SOX 302/404, GLBA 501(b), OCC 2011-12, Fed SR 11-7, CFTC 1.31
- **Documentation:** MkDocs Material-based site published to GitHub Pages
- **Audience:** M365 administrators in US financial services

### Companion Repository

**FSI-AgentGov-Solutions** (`C:/dev/FSI-AgentGov-Solutions`) contains **35 live solution implementations** mapped to the current 78-control framework baseline. Use `docs/reference/solutions-index.md` in this repository as the source of truth for the current catalog, versions, and primary control mappings.

**Documentation:**
- `scripts/README.md` - Shared hooks documentation
- `.claude/README.md` - Claude Code configuration guide
- See `docs/framework/solutions-integration.md` for framework mapping
- See `docs/reference/solutions-index.md` for complete catalog

### Cross-Repository Workflow

When working with both repositories:

**Primary Working Directory:** FSI-AgentGov (this repo)
- Has MkDocs, comprehensive CLAUDE.md, and skills
- Boundary hooks allow access to FSI-AgentGov-Solutions

**Hook Scope:**
- `boundary-check.py` only intercepts Bash commands
- Read/Write/Edit/Glob/Grep tools work cross-repo without restriction

**When to Start From Each Repo:**

| Task | Start From | Reason |
|------|-----------|--------|
| Documentation updates | FSI-AgentGov | MkDocs, skills, comprehensive context |
| Solution script development | FSI-AgentGov-Solutions | Focused context |
| Cross-repo feature work | FSI-AgentGov | Better tooling, access to both |
| Quick solution fix | FSI-AgentGov-Solutions | Faster context loading |

**Git Operations:**

Each repo has separate git history. Git commands must run from within the target repo.

```bash
# Verify which repo you're in before committing
pwd
git rev-parse --show-toplevel

# To commit to FSI-AgentGov-Solutions while working in FSI-AgentGov:
cd C:/dev/FSI-AgentGov-Solutions
git add <specific-files>
git commit -m "message"
cd -  # return to previous directory
```

**Committing Changes That Span Both Repos:**

1. Commit FSI-AgentGov-Solutions changes first (scripts/implementations)
2. Commit FSI-AgentGov changes second (documentation)
3. Use cross-references in commit messages when related

**PostToolUse Hook Limitation:**
The `researcher-package-reminder.py` hook only fires when:
- Working directory is FSI-AgentGov AND
- A pillar control file is edited via Edit or Write tool

When working from FSI-AgentGov-Solutions, the reminder will NOT fire even if you edit framework files.

---

## Before Starting Any Task

Read these files for context:
1. **`.github/copilot-instructions.md`** - Full repository structure and design decisions
2. **`AGENTS.md`** - Instructions for autonomous agent tasks
3. **`docs/templates/control-setup-template.md`** - The 10-section control template
4. **`CONTRIBUTING.md`** - Language guidelines and style rules

---

## Directory Structure

```
FSI-AgentGov/
├── .claude/
│   ├── CLAUDE.md              # This file (core instructions)
│   ├── settings.json          # Team-shared settings (hooks, permissions)
│   ├── settings.local.json    # Local overrides (not committed)
│   └── skills/                # On-demand workflow guides (YAML frontmatter)
├── docs/
│   ├── framework/             # Layer 1: Governance principles (10 docs)
│   ├── controls/              # Layer 2: Control catalog (78 controls)
│   │   ├── pillar-1-security/     # 1.1-1.29 (29 controls)
│   │   ├── pillar-2-management/   # 2.1-2.26 (26 controls)
│   │   ├── pillar-3-reporting/    # 3.1-3.14 (14 controls)
│   │   └── pillar-4-sharepoint/   # 4.1-4.9 (9 controls)
│   ├── playbooks/             # Layer 3: Implementation guides (control, advanced, operations, lifecycle)
│   │   ├── control-implementations/  # 312 standard playbooks + 2 supplemental control guides
│   │   └── advanced-implementations/ # Complex multi-control solutions (31 files)
│   ├── assessment/            # Interactive readiness assessment tool
│   ├── reference/             # Supporting materials (incl. CSA quick-reference & positioning guide)
│   ├── downloads/             # Excel templates
│   └── images/                # Screenshot specs + diagrams/ (PNG/SVG exports)
├── scripts/                   # Python validation scripts
│   ├── learn_monitor.py           # Microsoft Learn documentation monitor
│   ├── verify_controls.py         # Control structure validation
│   ├── extract_assessment_data.py # Assessment data extraction (78 controls → JSON)
│   ├── compile_researcher_package.py  # Research package generator
│   └── hooks/                     # Claude Code hooks
├── assessment/                # Automated assessment engine
│   ├── manifest/controls.json     # Machine-readable 78-control definitions
│   ├── collectors/                # 5 PowerShell collectors (PPAC, Graph, Purview, SharePoint, Sentinel)
│   ├── engine/                    # Python scoring (score.py) and report generator (report.py)
│   ├── tests/                     # pytest tests with fixture data
│   ├── run-assessment.ps1         # Main orchestrator
│   └── output/                    # Run outputs (gitignored — customer data)
├── data/                      # Runtime data (state files)
├── reports/                   # Generated reports
│   └── learn-changes/             # Learn documentation change reports
├── mkdocs.yml                 # Site navigation
└── CHANGELOG.md               # Release history
```

---

## Three-Layer Documentation Architecture

| Layer | Location | Purpose |
|-------|----------|---------|
| **Framework** | `docs/framework/` | Governance principles, zones, lifecycle, operating model |
| **Controls** | `docs/controls/pillar-*/` | Technical specifications (10-section format) |
| **Playbooks** | `docs/playbooks/` | Step-by-step implementation procedures |

### Control Catalog

| Pillar | Controls | Focus |
|--------|----------|-------|
| Pillar 1 - Security | 1.1-1.29 (29) | Data protection, access, audit |
| Pillar 2 - Management | 2.1-2.26 (26) | Lifecycle, risk, operations |
| Pillar 3 - Reporting | 3.1-3.14 (14) | Visibility, metrics, dashboards |
| Pillar 4 - SharePoint | 4.1-4.9 (9) | Content governance, grounding |

### Playbook Structure

**Control Implementations** - Each control has 4 playbooks in `docs/playbooks/control-implementations/{control-id}/`:
- `portal-walkthrough.md` - Step-by-step portal configuration
- `powershell-setup.md` - PowerShell automation
- `verification-testing.md` - Test cases, evidence collection
- `troubleshooting.md` - Common issues, resolutions

**Advanced Implementations** - Complex multi-control solutions in `docs/playbooks/advanced-implementations/`:
- `platform-change-governance/` - Message Center governance with Dataverse (6 docs)
- `environment-lifecycle-management/` - Automated environment provisioning (6 docs)

---

## Skills (On-Demand Workflows)

Use these skills for detailed step-by-step workflows:

| Skill | Use When |
|-------|----------|
| `/update-control` | Modifying existing control content |
| `/add-control` | Adding a new control to a pillar |
| `/update-excel` | Maintaining Excel checklist templates |
| `/verify-ui` | Verifying portal screenshots match documentation |
| `/review-learn-changes` | Reviewing monitoring reports and drafting documentation updates |

Skills are loaded on-demand to reduce context size. Each skill includes YAML frontmatter with:
- `name` - Skill identifier
- `description` - When to use this skill (enables auto-suggestion)
- `allowed-tools` - Tools the skill can access
- `user-invocable: true` - Can be invoked via `/skill-name`

---

## Language Guidelines (CRITICAL)

### Regulatory Language

**NEVER use these phrases (legal risk):**
- "ensures compliance" - implies guarantee
- "guarantees" - legal liability
- "will prevent" - overclaim
- "eliminates risk" - unrealistic

**ALWAYS use these alternatives:**
- "supports compliance with"
- "helps meet"
- "required for"
- "recommended to"
- "aids in"

### Example

```markdown
# WRONG
This control ensures you meet SEC 17a-4 requirements.

# RIGHT
This control helps support SEC 17a-4 requirements. Implementation requires...
```

### Role Naming

Use canonical short names from `docs/reference/role-catalog.md`:

| Use This | NOT This |
|----------|----------|
| Entra Global Admin | Global Administrator |
| Purview Compliance Admin | Compliance Administrator |
| Power Platform Admin | Power Apps Admin |
| Exchange Online Admin | Exchange Administrator |

---

## Validation Commands

```bash
# Build documentation (must pass with zero errors)
mkdocs build --strict

# Preview locally
mkdocs serve

# Validate control structure
python scripts/verify_controls.py

# Validate Excel templates
python scripts/verify_excel_templates.py

# Check Microsoft Learn URLs for changes (manual run)
python scripts/learn_monitor.py --dry-run --limit 5

# Regenerate researcher package after control changes
python scripts/compile_researcher_package.py

# Run assessment engine tests
cd assessment && pip install -r requirements.txt && pytest tests/ -v

# Lint Python (root pyproject.toml — F, B, I)
ruff check assessment scripts

# Cross-source consistency (manifest, CONTROL-INDEX.md, mkdocs nav)
python scripts/check_manifest_doc_drift.py --check

# Honest assessment-engine coverage matrix
python scripts/generate_coverage_matrix.py --check

# FSI-banned-phrase linter
python scripts/verify_language_rules.py
```

### What "Pass" Means
- `mkdocs build --strict` produces zero errors/warnings
- `verify_controls.py` reports all 78 controls valid
- `check_manifest_doc_drift.py --check` returns 0
- `generate_coverage_matrix.py --check` returns 0 (matrix is current)
- `verify_language_rules.py` returns 0 (no banned phrases)
- `ruff check assessment scripts` returns 0
- No broken internal links

---

## Automation

### Microsoft Learn Documentation Monitor

Monitors Microsoft Learn URLs for content changes that may require framework updates.

**Script:** `scripts/learn_monitor.py`
**Workflow:** `.github/workflows/learn-monitor.yml`
**Schedule:** Daily at 6:00 AM UTC

**Usage:**
```bash
# Test with limited URLs
python scripts/learn_monitor.py --limit 5 --dry-run

# Debug a single URL
python scripts/learn_monitor.py --url "https://learn.microsoft.com/..."

# Full run with verbose output
python scripts/learn_monitor.py --verbose
```

**Output:**
- `data/learn-monitor-state.json` - Content hashes for all monitored URLs
- `reports/learn-changes/learn-changes-YYYY-MM-DD.md` - Change reports with diffs

**Change Classification:**
| Classification | Trigger | Action |
|---------------|---------|--------|
| CRITICAL | Playbook portal-walkthrough.md affected | Immediate update required |
| HIGH | UI steps, policy language, deprecations | Review and update |
| MEDIUM | Minor content changes | Review optional |
| NOISE | Metadata/formatting only | Ignore |

**AI-Assisted Review (v1.2.37+):**

When a Learn Monitor PR is created with changes detected:

```bash
# 1. Checkout the PR branch
gh pr checkout {PR_NUMBER}

# 2. Run the AI-assisted review skill
/review-learn-changes

# 3. Claude will analyze changes and propose documentation updates
# 4. Commit and push, then merge the PR
```

See `docs/reference/learn-monitor-ai-enhancement.md` for the full design.

### GitHub Actions Workflows

| Workflow | Schedule | Purpose |
|----------|----------|---------|
| `link-check.yml` | Weekly (Sundays) | Validate markdown links |
| `publish_docs.yml` | On push to main | Deploy to GitHub Pages |
| `learn-monitor.yml` | Daily (6 AM UTC) | Monitor Learn documentation changes |

---

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| "Broken reference to control X.X" | Wrong path/filename | Check `CONTROL-INDEX.md`, verify path |
| "Control missing section X" | Incomplete template | Read `control-setup-template.md`, add section |
| "mkdocs build failed" | Markdown syntax or nav issue | Check bracket matching, verify nav entry |

---

## Quick Reference

| Want to... | Go to... |
|------------|----------|
| Add a control | `/add-control` skill or `docs/templates/control-setup-template.md` |
| Update a control | `/update-control` skill |
| Check all controls | `docs/controls/CONTROL-INDEX.md` |
| See role names | `docs/reference/role-catalog.md` |
| Check regulatory mappings | `docs/reference/regulatory-mappings.md` |
| Understand zones | `docs/framework/zones-and-tiers.md` |
| Understand Agent ID vs Blueprint | `docs/framework/agent-identity-architecture.md` |
| Learn about the doc monitor | `docs/reference/learn-monitor-guide.md` |
| Understand AI-assisted Learn Monitor | `docs/reference/learn-monitor-ai-enhancement.md` |
| Use AI-assisted Learn Monitor review | `/review-learn-changes` skill |
| CSA Quick Reference | `docs/reference/csa-quick-reference.md` |
| CSA Positioning Guide | `docs/reference/csa-positioning-guide.md` |
| View exportable diagrams | `docs/images/diagrams/` (PNG/SVG) |
| View all solutions | `docs/reference/solutions-index.md` |
| Understand solutions-to-framework mapping | `docs/framework/solutions-integration.md` |
| Implement Platform Change Governance | `docs/playbooks/advanced-implementations/platform-change-governance/` |
| Implement Environment Lifecycle Management | `docs/playbooks/advanced-implementations/environment-lifecycle-management/` |
| Plan adoption phases | `docs/framework/adoption-roadmap.md` |
| Assess governance readiness | `docs/assessment/index.md` |
| Review language rules | `CONTRIBUTING.md` |
| Edit site navigation | `mkdocs.yml` |
| View release history | `CHANGELOG.md` |

---

## Configuration

### Settings Files

| File | Purpose | Committed |
|------|---------|-----------|
| `.claude/settings.json` | Team-shared settings (hooks, base permissions, deny rules) | Yes |
| `.claude/settings.local.json` | Local overrides (WebFetch domains, personal preferences) | No |

Settings are merged at runtime: `settings.json` provides the base, `settings.local.json` adds local overrides.

### Hooks

**PreToolUse: Project Boundary Check**
- Script: `scripts/hooks/boundary-check.py`
- Blocks Bash commands that might operate outside the project directory
- Returns JSON: `{"decision": "allow"}` or `{"decision": "block", "reason": "..."}`

**PostToolUse: Researcher Package Reminder**
- Script: `scripts/hooks/researcher-package-reminder.py`
- Triggers when pillar control files are edited
- Reminds to run: `python scripts/compile_researcher_package.py`

### Permissions

**Team-shared (settings.json):**
- Allow: git, mkdocs, python, pip commands
- Deny: `rm -rf /`, `.env` file access

**Local overrides (settings.local.json):**
- WebFetch domains (microsoft.com, learn.microsoft.com, github.com)
- GitHub CLI commands

---

## Current State

**Version:** 1.3.0 (March 2026)
**Status:** 78 controls published, 314 control-implementation markdown docs (312 standard playbooks + 2 supplemental guides), 41 advanced implementation docs, build passing, Learn monitor active (207 URLs), interactive assessment tool live, CSA reference guides published, exportable diagrams available

**Key capabilities in recent releases:**

- v1.4.0 unification — assessment manifest unification (single source of truth across Python engine + browser SPA), Solutions Bridge (cross-repo integration with FSI-AgentGov-Solutions v1.4.1, 35 solutions indexed, 26 controls wired), sector-specific calibration (8 institution types), facilitator mode, role-based homework pages, How to verify drawer, collector evidence import (April 2026)
- v1.3.0 expansion — six new controls, 24 new playbooks, five existing-control patches, and catalog growth to 78 controls (March 2026)
- CSA Quick Reference and Positioning Guide — partner/CSA engagement materials in `docs/reference/`
- Automation indicators across the control catalog — each control identifies automation feasibility
- Exportable architecture diagrams — PNG/SVG exports available in `docs/images/diagrams/`
- Interactive Governance Readiness Assessment tool — client-side wizard assessing the full control catalog with smart scoping, two-phase drill-down, visual dashboard, remediation roadmap, and Excel/JSON/CSV/PDF export. JSON exports include a `_metadata` + `_computedScores` envelope (framework version, schema version, pre-computed pillar/overall scores, derived `assessmentStatus`) for downstream reporting agent consumption — see `assessment/data/README.md` "Portal Export Schema" for the contract.
- 48-batch automated documentation review — SSPM mapping, Control 2.22 zone thresholds, stale footers, terminology fixes (v1.2.52)
- UASD review remediation — 6 critical script fixes, 6 new troubleshooting scenarios (v1.2.51)
- Five-solution deep dive — 18 UASD bugs, 16 MIME bugs, ITE round 2 fixes (v1.2.49)
- Comprehensive repository review — 12 GitHub issues resolved across both repos (v1.2.48)
- Solution consolidation — ACV + ALCA merged into Audit Compliance Manager (v1.2.47)
- Live solutions index tracks 35 live companion solution implementations with mapped control coverage
- Native Microsoft Defender integration for AI agents (v1.2.37)
- AI-assisted Learn Monitor review with `/review-learn-changes` skill (v1.2.37)
- State AI law monitoring — Colorado, Texas, Illinois, California, NYC (v1.2.20–v1.2.31)

For detailed release history, see `CHANGELOG.md`.

---

## Version Info
- **Framework Version:** 1.6.2
- **Last Updated:** May 2026
- **Repository:** https://github.com/judeper/FSI-AgentGov
- **Solutions Repository:** https://github.com/judeper/FSI-AgentGov-Solutions
