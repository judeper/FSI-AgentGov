# FSI-AgentGov Repository - Claude Code Instructions

## Project Overview

**FSI Agent Governance Framework v1.2.27** - A governance framework for Microsoft 365 AI agents (Copilot Studio, Agent Builder) in US financial services organizations.

### Key Stats
- **62 controls** across 4 pillars (Security, Management, Reporting, SharePoint)
- **3 governance zones** (Personal Productivity, Team Collaboration, Enterprise Managed)
- **3-layer documentation** (Framework → Controls → Playbooks)
- **6 advanced implementations** (Platform Change Governance, Environment Lifecycle Management, Agent 365 Observability, etc.)
- **Target regulations:** FINRA 4511/3110/25-07, SEC 17a-3/4, SOX 302/404, GLBA 501(b), OCC 2011-12, Fed SR 11-7, CFTC 1.31
- **Documentation:** MkDocs Material-based site published to GitHub Pages
- **Audience:** M365 administrators in US financial services

### Companion Repository

**FSI-AgentGov-Solutions** (`/Users/admin/dev/FSI-AgentGov-Solutions`) contains deployable solution artifacts:

| Solution | Version | Description |
|----------|---------|-------------|
| `environment-lifecycle-management/` | v1.1.2 | Automated environment provisioning with zone classification |
| `message-center-monitor/` | v2.1.1 | M365 Message Center polling and Teams notifications |
| `pipeline-governance-cleanup/` | v1.0.8 | Personal pipeline discovery and cleanup automation |
| `deny-event-correlation-report/` | v1.0.0 | Unified deny event reporting across Purview/DLP/App Insights |

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
cd /Users/admin/dev/FSI-AgentGov-Solutions
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
│   ├── controls/              # Layer 2: Control catalog (62 controls)
│   │   ├── pillar-1-security/     # 1.1-1.24 (24 controls)
│   │   ├── pillar-2-management/   # 2.1-2.21 (21 controls)
│   │   ├── pillar-3-reporting/    # 3.1-3.10 (10 controls)
│   │   └── pillar-4-sharepoint/   # 4.1-4.7 (7 controls)
│   ├── playbooks/             # Layer 3: Implementation guides (254 files)
│   │   ├── control-implementations/  # 4 playbooks per control (248 files)
│   │   └── advanced-implementations/ # Complex multi-control solutions (6 files)
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
| Pillar 1 - Security | 1.1-1.24 (24) | Data protection, access, audit |
| Pillar 2 - Management | 2.1-2.21 (21) | Lifecycle, risk, operations |
| Pillar 3 - Reporting | 3.1-3.10 (10) | Visibility, metrics, dashboards |
| Pillar 4 - SharePoint | 4.1-4.7 (7) | Content governance, grounding |

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
| `docs/controls/CONTROL-INDEX.md` | Master control list with implementation references |
| `docs/templates/control-setup-template.md` | 10-section control template |
| `docs/reference/role-catalog.md` | Canonical role names |
| `docs/reference/regulatory-mappings.md` | Regulation-to-control mapping |
| `docs/reference/solutions-index.md` | Complete FSI-AgentGov-Solutions catalog |
| `docs/reference/learn-monitor-guide.md` | How the Learn monitor works |
| `docs/framework/agent-identity-architecture.md` | Agent ID vs Blueprint architecture guide |
| `docs/framework/solutions-integration.md` | Solutions-to-framework mapping |
| `docs/framework/adoption-roadmap.md` | Phased implementation with solution references |
| `docs/playbooks/advanced-implementations/platform-change-governance/` | Platform Change Governance playbook |
| `docs/playbooks/advanced-implementations/environment-lifecycle-management/` | Environment Lifecycle Management playbook |
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
- `verify_controls.py` reports all 62 controls valid
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
| Understand Agent ID vs Blueprint | `docs/framework/agent-identity-architecture.md` |
| Learn about the doc monitor | `docs/reference/learn-monitor-guide.md` |
| View all solutions | `docs/reference/solutions-index.md` |
| Understand solutions-to-framework mapping | `docs/framework/solutions-integration.md` |
| Implement Platform Change Governance | `docs/playbooks/advanced-implementations/platform-change-governance/` |
| Implement Environment Lifecycle Management | `docs/playbooks/advanced-implementations/environment-lifecycle-management/` |
| Plan adoption phases | `docs/framework/adoption-roadmap.md` |
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

**Version:** 1.2.27 (January 2026)
**Status:** All 62 controls complete, 248 control playbooks + 27 advanced implementation docs, build passing, Learn monitor active (196 URLs)

**Recent Additions (v1.2.27):**
- **ELM Technical Accuracy Remediation** - Corrected immutability claims in Environment Lifecycle Management playbook
- **architecture.md** - Changed "Immutable Audit Trail" to "Append-Only Audit Trail" with access control limitations table
- **evidence-and-audit.md** - Added "What These Controls Prevent vs. Allow" table and examiner transparency guidance
- **index.md** - Updated terminology from "immutable" to "append-only" in 4 locations
- **Key Clarification** - ProvisioningLog access controls are defense-in-depth, not true immutability; System Administrators retain full Dataverse access
- **FSI-AgentGov-Solutions** - ELM v1.1.2 with updated Python dependencies (msal>=1.30.0, requests>=2.32.0, azure-identity>=1.18.0) and corrected Environment Groups API claim

**Previous Additions (v1.2.26):**
- **Solutions Architecture Guide** - New `docs/reference/solutions-architecture-guide.md` with enterprise scalability guidance
- **Platform selection guide** - Power Automate vs Logic Apps vs Azure Functions comparison
- **Scalability limits** - Power Platform requests, Graph API throttling, Dataverse capacity, Power BI refresh limits
- **Secret management** - Azure Key Vault integration patterns and rotation best practices
- **Compliance storage** - Azure Immutable Blob Storage for SEC 17a-4/FINRA 4511 validated WORM compliance
- **CoE Starter Kit alignment** - Integration guidance for existing CoE deployments
- **Cross-references** - Updated Solutions Index, Solutions Integration, DEC playbook with architecture links

**Previous Additions (v1.2.25):**
- **February 2026 Pipeline Deadline Documentation** - Added critical compliance deadline for pipeline Managed Environment enforcement
- **Control 2.1 Critical Warning** - Added danger callout documenting automatic Managed Environment enablement for pipeline targets starting February 2026, licensing implications, and required actions
- **Solutions Index Urgency** - Added warning to Pipeline Governance Cleanup section highlighting February 2026 deadline

**Previous Additions (v1.2.24):**
- **Pillar 2 Management Controls Technical Accuracy Clarifications** - Distinguishes built-in platform capabilities from custom implementation requirements
- **Control 2.3** - Clarified approval gates require Power Automate integration (OnApprovalStarted trigger)
- **Control 2.6** - Added info box: Microsoft provides infrastructure, not pre-built MRM solution
- **Control 2.9** - Added RAI telemetry table distinguishing native analytics from custom hallucination tracking
- **Control 2.16** - Added built-in vs custom capabilities table for integrity validation features
- **Control 2.17** - Clarified orchestration limits are design patterns, not platform-enforced constraints
- **Control 2.21** - Reframed as process/policy control; no FINRA/SEC-specific tools exist

**Previous Additions (v1.2.23):**
- **Pillar 4 SharePoint Controls Technical Accuracy Updates** - Research-validated updates to all 7 controls (4.1-4.7)
- **SharePoint Advanced Management Licensing Guide** - New reference documenting SAM features included with Copilot license
- **SharePoint Governance Pre-Flight Checklist** - New playbook for Copilot pre-deployment preparation

**Previous Additions (v1.2.22):**
- **Industry Framework Alignment References** - Added FINOS AI Governance Framework and Sardine Agentic Oversight Framework references
- **FINOS alignment** - Risk mapping table for authorization bypass, privilege escalation, workflow circumvention
- **Sardine alignment** - 5-component oversight model mapped to HITL triggers playbook

**Previous Additions (v1.2.21):**
- **Pillar 3 Reporting Controls Technical Accuracy Updates** - Research-validated updates to Controls 3.1, 3.2, 3.3, 3.6, 3.7, 3.8, 3.9, 3.10
- **Control 3.9 Clarification** - No dedicated Copilot Studio connector exists for Sentinel; use Power Platform Admin Activity connector
- **Control 3.10 Clarification** - No automated hallucination detection exists; all detection relies on manual feedback

**Previous Additions (v1.2.20):**
- **Colorado SB24-205 Date Fix** - Effective date changed from February 1, 2026 to June 30, 2026 (extended via SB 25B-004)
- **OWASP LLM Top 10 Update** - Updated from 2023 to 2025 version in Controls 2.7 and 2.20
- **Treasury NIST AI RMF Correction** - Changed "endorsed by" to "recommended by" in crosswalk
- **MITRE ATLAS Context** - Added technique count (15 tactics, 66 techniques) to Control 2.20
- **State AI Law Monitoring** - Added table of other 2026 state AI laws (Texas TRAIGA, Illinois HB 3773, California TFAIA)

**Recent Additions (v1.2.19):**
- **SEC Rule 17a-4 Citation Correction** - Fixed retention period from "6 years + 3 years accessible" to "6 years, first 2 years readily accessible" per 17 CFR § 240.17a-4
- **5 files corrected** - regulatory-framework.md (4), zones-and-tiers.md (1), agent-decommissioning.md (1), faq.md (1), PCG architecture.md (1)
- **Validated SEC citations** - Marketing Rule 206(4)-1, Reg S-P, Reg BI, Reg S-ID, Rule 10b-5, 2026 Examination Priorities confirmed accurate

**Previous Additions (v1.2.18):**
- **Banking Regulator Citation Remediation** - Corrected erroneous FDIC FIL-15-2025 citation, fixed OCC 2021-18 AI guidance claim
- **Control 2.16 fix** - Replaced incorrect FDIC FIL-15-2025 with Interagency Third-Party Guidance (2023)
- **Control 2.6 fix** - Replaced incorrect OCC 2021-18 with Interagency RFI on AI (2021), added SR 11-7 joint issuance note
- **Validated citations** - OCC 2011-12, Fed SR 11-7, SOX 302/404/802, GLBA 501(b), OCC Heightened Standards confirmed accurate

**Recent Additions (v1.2.17):**
- **FINRA Citation Remediation** - Corrected FINRA Rule 4511 retention period errors (5 files), fixed Notice 25-07 link text
- **FINRA Regulatory Notice 24-09** - Added official Gen AI/LLM guidance references to regulatory-framework.md, regulatory-mappings.md, Control 2.12
- **FINRA Rule 3120** - Added supervisory control system cross-reference in Control 2.12
- **FINRA FAQ D.8** - Added firm responsibility citation for AI-generated communications

**Recent Additions (v1.2.16):**
- **Cross-Repository Documentation Parity** - Bidirectional cross-references between FSI-AgentGov and FSI-AgentGov-Solutions
- **Control tip boxes** - Added deployable solution links to Controls 2.1, 2.10, and 1.7
- **Playbook solution links** - Added Deployable Solution sections to 2.1 and 1.7 PowerShell playbooks
- **Playbooks index callout** - Added info box linking to Solutions Index
- **FSI-AgentGov-Solutions updates:**
  - Fixed broken URL in deny-event-correlation-report README
  - Added Related Controls sections to message-center-monitor and deny-event READMEs
  - Added Controls column to root README solutions table
  - Added Control Implementations table to CLAUDE.md

**Recent Additions (v1.2.15):**
- **Solutions Index** - New `docs/reference/solutions-index.md` cataloging all FSI-AgentGov-Solutions with versions and control mappings
- **Solutions Integration** - New `docs/framework/solutions-integration.md` mapping solutions to pillars and zones with architecture diagrams
- **CONTROL-INDEX.md Enhancement** - Added Implementation Reference column for all 62 controls linking to solutions where applicable
- **Adoption Roadmap Updates** - Added automation tips and solution references to implementation phases
- **Platform Change Governance Cross-Link** - Added explicit message-center-monitor reference to PCG playbook
- **FSI-AgentGov-Solutions Documentation** - Added `scripts/README.md` and `.claude/README.md` for hooks and configuration guidance

**Recent Additions (v1.2.14):**
- **SECURITY.md version fix** - Updated outdated version footer from v1.1 to v1.2.14
- **Control 2.1 licensing prerequisites** - Added explicit Prerequisites section documenting Power Platform Premium capacity requirements

**Recent Additions (v1.2.13):**
- **Control count parity fix** - Updated all documentation files from 61 to 62 controls after v1.2.10 addition of Control 1.24

**Previous Additions (v1.2.12):**
- **ELM Automation Documentation** - Updated ELM playbook with automated deployment quick start using FSI-AgentGov-Solutions v1.1.0 scripts
- **Labs Option A** - Added automated deployment path as alternative to manual Lab 1 setup

**FSI-AgentGov-Solutions Updates:**
- **Pipeline Governance Cleanup v1.0.8** - Documentation accuracy fixes: corrected misleading "deployment configurations preserved" language, added directional-only warning for `-ProbePipelines`, added manual verification requirement for greenfield detection

**Previous Additions (v1.2.11):**
- **Solutions Cross-Reference** - Added cross-references to FSI-AgentGov-Solutions automated export scripts in ELM playbook
- **Hook API Update** - Updated boundary-check.py response format for Claude Code compatibility

**Previous Additions (v1.2.10):**
- **Control 1.24: Defender AI-SPM** - Multi-cloud AI security posture management (Azure, AWS, GCP) with agent discovery, attack path analysis, and AI Bill of Materials
- **Control 1.5 Update** - Mandatory DLP enforcement notice (since early 2025), Copilot Studio DLP connector categories, HTTP endpoint filtering
- **Control 1.6 Update** - Expanded workload coverage (ChatGPT Enterprise, Gemini, Purview SDK apps)
- **Control 1.8 Update** - Enhanced Security Webhooks API section with vendor assessment guidance

**Previous Additions (v1.2.8-v1.2.9):**
- **Environment Lifecycle Management** - Automated environment provisioning playbook with Copilot Studio intake agent
- **Pipeline Governance Cleanup Cross-Reference** - Added cross-references to new FSI-AgentGov-Solutions tool

**Previous Additions (v1.2.7):**
- **Regulatory Accuracy Remediation** - FINRA Notice 25-07 citation corrections (35+ files), GLBA 72-hour claim removal, SEC Reg S-P precision
- **Framework Enhancements** - AML/KYC/OFAC awareness, SEC Reg S-ID reference, AI RIA scoring rubrics, exception criteria

**Previous Additions (v1.2.5-v1.2.6):**
- **Agent 365 Operational Depth** - Conditional Access agent templates, audit event taxonomy, Blueprint promotion gates playbook
- **Agent Essentials Mapping** - Microsoft's 8-category framework mapped to FSI controls
- **Sponsorship Lifecycle** - Workflows for sponsor reviews and departure handling
- **Observability Implementation** - OpenTelemetry setup, Application Insights workbooks, alerting configuration
- **Control 2.21** - AI Marketing Claims and Substantiation (SEC Marketing Rule, FINRA 2210)

For detailed release history, see `CHANGELOG.md`.

---

## Version Info
- **Framework Version:** 1.2.26
- **Last Updated:** January 2026
- **Repository:** https://github.com/judeper/FSI-AgentGov
- **Solutions Repository:** https://github.com/judeper/FSI-AgentGov-Solutions
