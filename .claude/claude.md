# FSI-AgentGov Repository - Claude Code Instructions

## Project Overview

**FSI Agent Governance Framework v1.1** - A governance framework for Microsoft 365 AI agents (Copilot Studio, Agent Builder) in US financial services organizations.

### Key Stats
- **61 controls** across 4 pillars (Security, Management, Reporting, SharePoint)
- **3 governance zones** (Personal Productivity, Team Collaboration, Enterprise Managed)
- **3-layer documentation** (Framework → Controls → Playbooks)
- **Target regulations:** FINRA 4511/3110/25-07, SEC 17a-3/4, SOX 302/404, GLBA 501(b), OCC 2011-12, Fed SR 11-7, CFTC 1.31
- **Documentation:** MkDocs Material-based site published to GitHub Pages
- **Audience:** M365 administrators in US financial services

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
│   ├── framework/             # Layer 1: Governance principles (9 docs)
│   ├── controls/              # Layer 2: Control catalog (61 controls)
│   │   ├── pillar-1-security/     # 1.1-1.23 (23 controls)
│   │   ├── pillar-2-management/   # 2.1-2.21 (21 controls)
│   │   ├── pillar-3-reporting/    # 3.1-3.10 (10 controls)
│   │   └── pillar-4-sharepoint/   # 4.1-4.7 (7 controls)
│   ├── playbooks/             # Layer 3: Implementation guides (244 files)
│   │   └── control-implementations/  # 4 playbooks per control
│   ├── reference/             # Supporting materials
│   ├── downloads/             # Excel templates
│   └── images/                # Screenshot specs
├── scripts/                   # Python validation scripts
│   ├── learn_monitor.py           # Microsoft Learn documentation monitor
│   ├── verify_controls.py         # Control structure validation
│   ├── compile_researcher_package.py  # Research package generator
│   └── hooks/                     # Claude Code hooks
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
| Pillar 1 - Security | 1.1-1.23 (23) | Data protection, access, audit |
| Pillar 2 - Management | 2.1-2.21 (21) | Lifecycle, risk, operations |
| Pillar 3 - Reporting | 3.1-3.10 (10) | Visibility, metrics, dashboards |
| Pillar 4 - SharePoint | 4.1-4.7 (7) | Content governance, grounding |

### Playbook Structure

Each control has 4 playbooks in `docs/playbooks/control-implementations/{control-id}/`:
- `portal-walkthrough.md` - Step-by-step portal configuration
- `powershell-setup.md` - PowerShell automation
- `verification-testing.md` - Test cases, evidence collection
- `troubleshooting.md` - Common issues, resolutions

---

## Skills (On-Demand Workflows)

Use these skills for detailed step-by-step workflows:

| Skill | Use When |
|-------|----------|
| `/update-control` | Modifying existing control content |
| `/add-control` | Adding a new control to a pillar |
| `/update-excel` | Maintaining Excel checklist templates |
| `/verify-ui` | Verifying portal screenshots match documentation |

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

## Key Files

| File | Purpose |
|------|---------|
| `docs/controls/CONTROL-INDEX.md` | Master control list |
| `docs/templates/control-setup-template.md` | 10-section control template |
| `docs/reference/role-catalog.md` | Canonical role names |
| `docs/reference/regulatory-mappings.md` | Regulation-to-control mapping |
| `mkdocs.yml` | Site navigation |
| `CHANGELOG.md` | Release history |

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
```

### What "Pass" Means
- `mkdocs build --strict` produces zero errors/warnings
- `verify_controls.py` reports all 61 controls valid
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

## Quick Navigation

| Want to... | Go to... |
|------------|----------|
| Add a control | `/add-control` skill or `docs/templates/control-setup-template.md` |
| Update a control | `/update-control` skill |
| Check all controls | `docs/controls/CONTROL-INDEX.md` |
| See role names | `docs/reference/role-catalog.md` |
| Understand zones | `docs/framework/zones-and-tiers.md` |
| Review language rules | `CONTRIBUTING.md` |
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

**Version:** 1.1.6 (January 2026)
**Status:** All 61 controls complete, all 244 playbooks complete, build passing, Learn monitor active

For detailed release history, see `CHANGELOG.md`.

---

## Version Info
- **Framework Version:** 1.1.6
- **Last Updated:** January 2026
- **Repository:** https://github.com/judeper/FSI-AgentGov
