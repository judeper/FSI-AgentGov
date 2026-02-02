# FSI-AgentGov Repository - Claude Code Instructions

## Project Overview

**FSI Agent Governance Framework v1.2.36** - A governance framework for Microsoft 365 AI agents (Copilot Studio, Agent Builder) in US financial services organizations.

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
| `deny-event-correlation-report/` | v1.1.0 | Unified deny event reporting across Purview/DLP/App Insights |
| `finra-supervision-workflow/` | v1.0.0 | FINRA 3110 supervision queue for AI agent outputs |
| `conditional-access-automation/` | v1.0.0 | CA policy deployment and compliance monitoring for AI workloads |
| `compliance-dashboard/` | v1.0.0-beta | Aggregated compliance reporting across 62 controls |
| `segregation-detector/` | v1.0.0 | Role conflict detection for Maker/Checker enforcement |
| `scope-drift-monitor/` | v1.0.0 | Detect agent data access beyond declared scope |
| `rag-source-validator/` | v1.0.0 | Integrity validation for RAG knowledge sources |
| `coi-testing/` | v1.0.0 | Conflict of interest testing for agent recommendations |
| `hallucination-tracker/` | v1.0.0 | Feedback aggregation for hallucination pattern analysis |
| `dr-testing-framework/` | v1.0.0 | Automated disaster recovery testing for AI agents |

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

**Version:** 1.2.36 (February 2026)
**Status:** All 62 controls complete, 248 control playbooks + 27 advanced implementation docs, build passing, Learn monitor active (196 URLs)

**Recent Additions (v1.2.36):**
- **7 New FSI-AgentGov-Solutions Released** - Complete solution development backlog delivered ahead of schedule
- **Compliance Dashboard v1.0.0-beta** - Aggregated compliance reporting across 62 controls with zone-based filtering, Dataverse schema, Power Automate flows, DAX measures (Control 3.3)
- **Segregation of Duties Detector v1.0.0** - Role conflict detection with 10 predefined rules across Maker/Checker, Segregation, Privileged Access categories (Control 2.8)
- **Scope Drift Monitor v1.0.0** - Automated detection of agent data access beyond declared scope with expansion workflow (Control 1.14)
- **RAG Source Validator v1.0.0** - SHA-256 hash validation for knowledge sources, schema drift detection, freshness monitoring (Control 2.16)
- **COI Testing Framework v1.0.0** - 10 predefined conflict of interest test scenarios across 4 categories with Python runner (Control 2.18)
- **Hallucination Tracker v1.0.0** - Multi-source feedback collection, pattern detection, agent accuracy scoring (Control 3.10)
- **DR Testing Framework v1.0.0** - 4 DR test scenarios with RTO/RPO measurement and gap tracking (Control 2.4)
- **Coverage Improvements** - Solutions coverage increased from 16.1% to 27.4% (10 → 17 controls); Pillar 1: 12.5% → 16.7%, Pillar 2: 28.6% → 47.6%, Pillar 3: 10.0% → 30.0%
- **Solutions Index Updated** - 13 solutions now cataloged with full documentation
- **Coverage Gaps Updated** - All P0/P1/P2 backlog items marked as RELEASED

**Previous Additions (v1.2.35):**
- **Phase 4 Technical Review Integration** - Integrated comprehensive technical review deliverables with 97% framework alignment validation
- **Control 1.6 DSPM Rebranding Note** - Added naming history callout: "AI Hub DSPM" → "DSPM for AI" (November 2024)
- **Enhanced Implementation Roadmap** - Added effort estimates, approach classification, and Phase 4 (Q4 2026) to solutions-coverage-gaps.md
- **Solution Development Backlog** - New section with P0/P1/P2 prioritized solution development queue
- **FINRA Supervision Workflow v1.0.0** - New FSI-AgentGov-Solutions component: Dataverse schema, security roles, Power Automate flows, Python scripts, Power BI dashboard for FINRA 3110 compliance (Control 2.12)
- **Conditional Access Automation v1.0.0** - New FSI-AgentGov-Solutions component: 8 CA policy templates, PowerShell deployment scripts, zone-based requirements, drift detection for AI workloads (Controls 1.11, 1.23, 1.18)
- **Coverage Improvements** - Solutions coverage increased from 12.9% to 16.1% (8 → 10 controls); Pillar 1: 8.3% → 12.5%, Pillar 2: 23.8% → 28.6%

**Previous Additions (v1.2.34):**
- **Solutions Coverage Gap Analysis** - New reference document (`docs/reference/solutions-coverage-gaps.md`) analyzing FSI-AgentGov-Solutions coverage against 62-control framework
- **Coverage Metrics** - 8 controls with deployable solutions (12.9% coverage); Pillar 1: 8.3%, Pillar 2: 23.8%, Pillar 3: 10.0%, Pillar 4: 0.0%
- **Gap Classification** - Three categories: Native Microsoft Features (portal configuration), Custom Solution Recommended, Process/Documentation Controls
- **High-Risk Gaps** - 32 Zone 3 controls identified with regulatory impact assessment
- **Critical Regulatory Gaps** - FINRA 3110 supervision and OCC 2011-12 model risk management mitigation guidance
- **Implementation Roadmap** - Q1-Q3 2026 prioritization for addressing solution gaps

**Previous Additions (v1.2.33):**
- **Phase 2 Technical Accuracy Remediation** - Four updates from Phase 2 technical accuracy research report verification
- **Control 1.5 DLP for Copilot Prompts** - Added new Public Preview capability (November 2025) for blocking sensitive data in M365 Copilot prompts; available to all Copilot users at no additional license cost
- **Control 3.8 Security Pivot and Readiness Page** - Added January 2026 Copilot Hub enhancements (MC1187780): Security pivot on overview page, Readiness page with three categories, success metrics (Chat Active Users, Assisted Hours, Satisfaction Rate)
- **Microsoft 365 Copilot Business License** - Added SMB SKU ($21/user/month, up to 300 users, GA December 2025) to license requirements with FSI applicability guidance
- **DEC Playbook x-api-key Deprecation Warning** - Added critical deprecation callout for March 31, 2026 App Insights API key retirement; migration guidance to Entra ID authentication

**Previous Additions (v1.2.32):**
- **Research Report Remediation Phase 1-6** - Regulatory citations, technical architecture, licensing, implementation, industry framework, and documentation enhancements from 76 research reports
- **NIST AI RMF Treasury Position Fix** - Corrected "Treasury recommended" to "stakeholders expressed support for voluntary adoption; Treasury committed to clarifying applicability"
- **ISO 42001 Positioning Fix** - Changed from "alternative" to "complementary" framework; ISO provides certifiable governance, NIST provides flexible risk assessment
- **Exchange Basic Auth Date Fix** - Corrected from December 2026 to March 1 – April 30, 2026; clarified applies to SMTP AUTH only
- **CopilotInteraction Schema Clarification** - Added warning that audit schema captures metadata only; full content requires eDiscovery/DSPM
- **UPIA/XPIA Detection Locations** - Corrected to show detection flags are in BOTH Purview CopilotInteraction AND Defender CloudAppEvents
- **Sentinel MCP Server Integration** - Added GA November 2025 MCP Server as primary Sentinel integration path for Copilot Studio
- **SEC 17a-4 Audit Trail Alternative** - Documented post-May 2023 option: WORM storage OR audit trail with modification history
- **PAYG Licensing Limitation** - Added critical warning to Control 2.1: Pay-as-you-go does NOT satisfy Managed Environment licensing for active users
- **E5 License Distinction** - Added table distinguishing E5 vs E5 Compliance vs E5 Security with capability matrix
- **Premium Connector Clarification** - Clarified Copilot Studio includes ALL premium connectors; Power Apps/Automate require separate licensing
- **Azure Key Vault API Retirement** - Added February 27, 2027 retirement warning for pre-2026-02-01 APIs; RBAC migration guidance
- **Approval Gates Architecture Distinction** - Added native Copilot Studio approvals vs. ALM pipeline approvals distinction to Control 2.3
- **Service Principal Security Group Bypass** - Added critical warning to ELM architecture: SPs bypass environment Security Groups; added quarterly audit requirement
- **Information Barriers Channel Agent Scope** - Clarified: Copilot Studio agents in Teams DO support IB; Channel Agents do NOT
- **DLP Enforcement Phased Timeline** - Added MC973179 three-phase rollout (Jan-Mar 2025) and 11 virtual governance connectors
- **FINOS AIGF v2.0 Update** - Updated to November 2025 release with 46 agentic AI-specific risks across 5 categories
- **SR 11-7 Vendor Model Governance** - Added Section V requirements: vendor models validated with equal rigor; cross-reference to SR 13-19
- **SOX AI Governance** - Added ICFR applicability note; PCAOB AI audit standards research (July 2024); documentation requirements
- **GLBA Safeguards Rule 10 Elements** - Added FTC 2021/2023 amendments; mapped 10 required elements to FSI-AgentGov controls
- **GLBA 30-Day Breach Notification** - Added FTC requirement for incidents affecting 500+ customers
- **Sardine AOF Interpretation Layer** - Clarified FSI-AgentGov mapping is framework interpretation, not direct Sardine guidance
- **Defender AI-SPM Updates** - Added GCP Vertex AI GA (November 2025), January 2026 agent-specific recommendations, attack path expansion
- **Sentinel Three Data Pathways** - Documented Power Platform Admin Activity, Purview UAL, Defender CloudAppEvents ingestion pathways
- **Custom Power BI Analytics** - Added infrastructure documentation (Dataverse → Synapse Link → Data Lake → Power BI) with decision matrix
- **SharePoint Admin Agent vs. Content Governance Agent** - Clarified distinction: Admin Agent (GA Nov 2025) for queries, Content Governance (Preview) for lifecycle

**Previous Additions (v1.2.31):**
- **State AI Laws Research Remediation** - Corrected Texas TRAIGA scope, NYC LL 144 effective date, NYDFS Part 500 2024 updates
- **Texas TRAIGA Scope Correction** - Clarified enacted law (HB 149) is narrower than presented; substantive requirements apply to state agencies only, private sector has intent-based prohibitions only
- **NYC Local Law 144** - Added effective date (January 1, 2023; enforcement July 5, 2023)
- **NYDFS Part 500 Updates** - Added dual-signature certification (April 2024), October 2024 AI cybersecurity guidance, 24-hour extortion reporting
- **Illinois HB 3773 Clarification** - Noted law requires notice but not bias audits (unlike Colorado/NYC)
- **Colorado SB24-205 Note** - Added that proposed small business exemptions (HB 25B-1009) were not enacted

**Previous Additions (v1.2.30):**
- **FINRA Research Report Remediation** - Communications retention corrected to 3 years (SEC 17a-4(b)(4)), Notice 25-07 RFI clarification, Rule 3120 testing requirements, 2026 Report integration
- **Retention Period Corrections** - Agent conversation logs are communications (3-year retention), not financial records (6-year); added retention matrix to framework docs
- **FINRA 2026 Annual Regulatory Oversight Report** - Added comprehensive references to December 2025 report with AI agent supervision guidance
- **Rule 3120 Annual Testing** - Added testing checklist and attestation template to Control 2.12 and verification playbook
- **Rule 2210 Communication Classifications** - Added correspondence vs. retail communication supervision requirements
- **AI Agent Autonomy Levels** - Added autonomy definitions (Assisted, Augmented, Automated, Autonomous) with HITL mapping
- **Notice 15-09 Testing Precedent** - Added algorithmic trading testing principles to Control 2.5
- **Storage Tier Guidance** - Added "readily accessible" compliance tiers to Control 1.9

**Previous Additions (v1.2.29):**
- **SEC Rules Research Report Remediation** - Corrected CFTC WORM misattribution and enhanced CFPB regulatory clarity
- **CFTC Rule 1.31 Fix** - Removed incorrect WORM references; CFTC uses principles-based "authenticity and reliability" standard (WORM eliminated May 2017)
- **Dual-Registrant Guidance** - Added warning clarifying SEC maintains WORM while CFTC uses principles-based approach
- **CFPB ECOA/UDAAP Distinction** - Added table clarifying ECOA is primary for credit decisions, UDAAP for all consumer products
- **Control 2.19 Update** - Clarified CFPB Chatbots report is research, not binding regulation
- **SOX AI Coverage Note** - Added clarification that SOX governs AI implicitly through ICFR; PCAOB researching new standards

**Previous Additions (v1.2.28):**
- **Research Report Remediation** - Addressed outstanding items from 15 research reports across 5 categories
- **DEC Solution Critical Updates** - Added x-api-key deprecation warnings (March 31, 2026), corrected schema documentation (XPIADetected/JailbreakDetected fields), added CloudAppEvents integration guidance
- **Control 1.8 Correction** - Clarified UPIA/XPIA detections are in Defender CloudAppEvents, not Purview CopilotInteraction audit schema
- **Control 1.22 Scope Limitation** - Added warning that Information Barriers are NOT supported for Channel Agent in Teams
- **API Deprecation Timeline** - New FAQ section documenting March 2026 (App Insights x-api-key, O365 Connectors), April 2026 (Reporting Webservice), Exchange Basic Auth SMTP (March–April 2026) deprecations
- **ISO/IEC 42001 Reference** - Added alternative AI management system standard reference to NIST AI RMF crosswalk
- **FSI-AgentGov-Solutions** - DEC v1.1.0 with deprecation warnings, MCM deprecation context note

**Previous Additions (v1.2.27):**
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
- **Framework Version:** 1.2.36
- **Last Updated:** February 2026
- **Repository:** https://github.com/judeper/FSI-AgentGov
- **Solutions Repository:** https://github.com/judeper/FSI-AgentGov-Solutions
