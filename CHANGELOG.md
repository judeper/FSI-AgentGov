# Changelog

All notable changes to the FSI Agent Governance Framework are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to semantic versioning.

---

## [1.1] — January 2026

### Architecture

- **Three-Layer Documentation Model:**
  - **Layer 1 - Framework** (`docs/framework/`): Governance principles for executives and compliance
  - **Layer 2 - Controls** (`docs/controls/`): Technical specifications (60 controls across 4 pillars)
  - **Layer 3 - Playbooks** (`docs/playbooks/`): Step-by-step implementation procedures
- Renamed `docs/reference/pillar-*/` to `docs/controls/pillar-*/` for clarity
- Reorganized `docs/operational-templates/` content into `docs/playbooks/`
- Added role-based navigation on homepage

### Added

- **Framework Layer (9 documents):**
  - `executive-summary.md` — Board-level overview
  - `zones-and-tiers.md` — Zone 1/2/3 classification guidance
  - `adoption-roadmap.md` — 30/60/90-day phased implementation
  - `lifecycle-governance.md` — Agent lifecycle management
  - `roles-and-responsibilities.md` — RACI and accountability
  - `risk-framework.md` — Risk assessment methodology
  - `regulatory-context.md` — FSI regulatory landscape
  - `training-and-awareness.md` — User education requirements
  - `index.md` — Framework layer overview

- **Control Implementation Playbooks (240 files):**
  - Created 4 playbooks per control (60 controls × 4 = 240 files)
  - Playbook types for each control:
    - `portal-walkthrough.md` — Step-by-step portal configuration
    - `powershell-setup.md` — PowerShell automation scripts
    - `verification-testing.md` — Test cases and evidence collection
    - `troubleshooting.md` — Common issues and resolutions
  - Located at `docs/playbooks/control-implementations/{control-id}/`
  - Each playbook includes: prerequisites, step-by-step instructions, configuration by governance level, FSI example configurations, validation checklists

- **Playbook Categories:**
  - `governance-operations/` — Standing procedures (weekly reviews, quarterly assessments)
  - `compliance-and-audit/` — Audit preparation, evidence collection, examination response
  - `incident-response/` — Data exposure, compliance violation handling
  - `lifecycle-operations/` — Agent provisioning, retirement, updates

- **Scripts Directory Enhancement:**
  - `scripts/README.md` — Usage guide
  - `scripts/requirements.txt` — Python dependencies
  - `scripts/governance/` — Governance automation (placeholder)
  - `scripts/reporting/` — Reporting automation (placeholder)
  - `scripts/hooks/boundary-check.py` — Project boundary protection hook

- **GitHub Issue Templates:**
  - `bug-report.md` — Bug reporting template
  - `feature-request.md` — Feature request template
  - `ui-verification.md` — UI verification checklist

### Changed

- Zone 1 regulatory language softened to conditional phrasing
- Pillar 4 explicitly positions as SharePoint specialization of Pillars 1-3
- HITL patterns explicitly defined (Pre-Approval, Sampled Review, Escalation-on-Threshold)
- Controls 2.12 and 2.19 updated with customer-facing conduct notes
- Updated `.claude/claude.md` with three-layer documentation guidance
- Updated `.github/copilot-instructions.md` with new directory structure
- Updated `scripts/verify_controls.py` to use `docs/controls/` path
- Updated `scripts/compile_researcher_package.py` to use `docs/controls/` path
- Updated `scripts/hooks/researcher-package-reminder.py` to detect both old and new paths

### Fixed

- Fixed 6 broken cross-references between controls:
  - Control 2.16 → 4.1 (wrong filename)
  - Control 2.19 → 1.6 (wrong filename)
  - Control 2.4 → 3.4 (wrong filename)
  - Control 2.6 → 3.3 (wrong filename)
  - Control 3.5 → 2.2 (wrong filename)
  - Control 3.6 → 2.3 (wrong filename)
- Fixed relative path issues in playbooks (1.1, 3.1, 3.2)
- Resolved all link warnings in mkdocs build

---

## [1.0] — January 2026

### Researcher Feedback v2 - Agentic AI and 2025/2026 Compliance (January 17, 2026)

**Status:** New controls and enhancements addressing researcher feedback
**Date:** January 17, 2026
**Scope:** 2 new controls + 6 control enhancements (58 → 60 controls)

#### New Controls Added

- **Control 1.23: Step-up Authentication for Agent Operations** (HIGH priority)
  - Risk-based authentication escalation for sensitive agent actions
  - Multi-factor authentication triggers for financial transactions
  - Zone-specific step-up thresholds
  - Regulatory alignment: FFIEC Authentication Guidance, GLBA 501(b), FINRA 3110

- **Control 2.20: Adversarial Testing and Red Team Framework** (HIGH priority)
  - Structured red team exercises for AI agents
  - Prompt injection and jailbreak testing procedures
  - Data exfiltration and boundary testing
  - Regulatory alignment: OCC 2011-12, Fed SR 11-7, NIST AI RMF

#### Control Enhancements

- **Control 1.18 (Application-Level Authorization)** - Enhanced RBAC guidance for agentic scenarios
- **Control 2.3 (Change Management)** - Added AI-specific change categories and risk assessment
- **Control 2.5 (Testing and Validation)** - Expanded test scenarios for agent behaviors
- **Control 2.6 (Model Risk Management)** - Enhanced OCC 2011-12 alignment with agentic AI considerations
- **Control 2.12 (Supervision and Oversight)** - Updated FINRA 3110 guidance for automated supervision
- **Control 4.7 (Copilot Data Governance)** - Enhanced data governance for M365 Copilot grounding

#### Supporting Materials Added

- **Evidence Standards Reference** (`docs/reference/evidence-standards.md`)
- **Governance Operating Calendar** (`docs/operational-templates/templates/governance-operating-calendar.md`)
- **Screenshot Specifications** for controls 1.20, 1.21, 2.16, 4.6
- **Researcher Package Compiler** (`scripts/compile_researcher_package.py`)

#### Framework Statistics Update

- **Total controls:** 58 → 60 (+2)
- **Pillar 1 (Security):** 22 → 23 (+1)
- **Pillar 2 (Management):** 19 → 20 (+1)

---

### Feature Gap Analysis Implementation (January 16, 2026)

**Status:** New controls and enhancements addressing identified feature gaps
**Date:** January 16, 2026
**Scope:** 2 new controls + 1 control enhancement (55 → 57 controls)

#### New Controls Added

- **Control 2.19: Customer AI Disclosure and Transparency** (HIGH priority)
  - Formal processes for disclosing AI agent use to customers
  - Disclosure templates by zone (Basic/Standard/Comprehensive)
  - Human escalation path requirements
  - Regulatory alignment: SEC Reg BI, CFPB UDAAP, FINRA 25-07, GLBA 501(b)
  - Change management workflow for disclosure updates

- **Control 4.7: Microsoft 365 Copilot Data Governance** (MEDIUM-HIGH priority)
  - Governance for embedded M365 Copilot (Word, Excel, Teams, etc.)
  - Knowledge source boundaries via Restricted Content Discovery
  - Plugin and web access governance
  - User behavior guardrails and acceptable use policy
  - Output review processes for customer-facing content
  - Distinction from Copilot Studio agent governance

#### Control Enhancements

- **Control 3.10 (Hallucination Feedback Loop)** - Added 4 new sections:
  - **Proactive Output Quality Monitoring** - Pre-delivery content scanning, quality scoring thresholds, automated flagging
  - **Content Safety Guardrails** - Tone monitoring, financial advice boundaries, harmful content prevention
  - **Sensitive Topic Handling** - Financial hardship, complaints, crisis, regulatory inquiry procedures
  - **Real-Time Quality Scoring** - Confidence-based routing, quality dashboards, degradation alerting

#### Supporting Files Updated

- **CONTROL-INDEX.md** - Added 2.19, 4.7; updated counts (55 → 57)
- **regulatory-mappings.md** - Added new controls to applicable regulations; updated coverage summary
- **mkdocs.yml** - Added navigation entries for 2.19, 4.7

#### Framework Statistics Update

- **Total controls:** 55 → 57 (+2)
- **Pillar 2 (Management):** 18 → 19 (+1)
- **Pillar 4 (SharePoint):** 6 → 7 (+1)

#### Gap Analysis Source

These additions address gaps identified during framework self-review:
1. Customer AI disclosure (partial coverage → dedicated control)
2. Output quality/content safety (reactive → proactive monitoring)
3. M365 Copilot governance (minimal → dedicated control)

---

### Link Validation CI Fix (January 16, 2026)

**Status:** Fixed broken external URLs causing CI failure
**Date:** January 16, 2026
**Scope:** 8 broken external URLs across 5 control files

#### Configuration Update

- **mlc-config.json** - Expanded SEC.gov ignore pattern to handle 403 blocks on regulation pages

#### URL Fixes

| File | Issue | Fix |
|------|-------|-----|
| 1.21 (Adversarial Input Logging) | Dead link to Defender for Cloud Apps AI protection | Updated to AI Agent Inventory URL |
| 2.16 (RAG Source Integrity) | Dead links + placeholder URL parsed as link | Fixed Copilot Studio knowledge URL, SharePoint management URL, escaped placeholder |
| 2.17 (Multi-Agent Orchestration) | Dead link to Power Automate error handling | Updated to coding guidelines error handling URL |
| 4.6 (Grounding Scope Governance) | Dead links to SharePoint restricted content | Updated to restricted-content-discovery and data-access-governance-reports URLs |

#### Verification

- All 5 affected files pass `markdown-link-check` validation
- `mkdocs build --strict` passes with zero errors

---

### Link Consistency and Regulatory Mappings Update (January 16, 2026)

**Status:** Self-review implementation - cross-reference and link improvements
**Date:** January 16, 2026
**Scope:** Link standardization, regulatory mappings update, navigation improvements

#### Link Standardization

- **Standardized Related Controls format** across all controls to Style A pattern: `| [X.Y - Control Name](path.md) | Description |`
- **Fixed Control 1.5** - Changed from Style B (`[Control 1.6: DSPM for AI]`) to Style A
- **Fixed Control 4.2** - Removed unique Priority column, standardized link format
- **Fixed Control 2.18** - Added missing reciprocal link to 2.12 (Supervision)

#### Dependencies Converted to Clickable Links

Converted plain text dependencies to markdown links in 7 Pillar 2 controls:
- Control 2.8 (Access Control and Segregation of Duties)
- Control 2.9 (Agent Performance Monitoring)
- Control 2.10 (Patch Management)
- Control 2.11 (Bias Testing)
- Control 2.12 (Supervision and Oversight)
- Control 2.13 (Documentation and Record Keeping)
- Control 2.14 (Training and Awareness)

#### Regulatory Mappings Update

- **Added 7 missing controls** to `regulatory-mappings.md`: 1.20, 1.21, 2.16, 2.17, 2.18, 3.10, 4.6
- **Updated Control Coverage Summary** from 48/48 to 55/55 controls
- **Recalculated percentages** for all 15 regulations

#### Cross-Pillar Navigation

- Added Control 4.1 (SharePoint IAG) reference to Control 1.4 (Advanced Connector Policies)
- Verified existing cross-pillar links (2.1→1.20, 3.8→3.1/3.2, 1.14→1.3)

#### Verification

- Confirmed mkdocs.yml includes all 55 controls in correct numerical order
- `mkdocs build --strict` passes with zero errors

---

### Gap Analysis Response Update (January 16, 2026)

**Status:** Implementation of AI Governance Research Unit gap analysis recommendations
**Date:** January 16, 2026
**Scope:** 6 new controls + 4 control enhancements + 3 supporting documents (49 → 55 controls)

#### New Controls Added

- **Control 1.21: Adversarial Input Logging** (Critical)
  - Detection patterns for prompt injection, jailbreaking, encoding attacks
  - KQL queries for Sentinel integration
  - Zone-specific configuration (Zone 1: monitoring only, Zone 2-3: blocking)
  - Regulatory alignment: FFIEC CAT 2025, GLBA 501(b)

- **Control 2.16: RAG Source Integrity Validation** (Critical)
  - Knowledge source approval workflows
  - Content versioning and staleness detection
  - Citation logging requirements
  - Regulatory alignment: Fed SR 11-7, FDIC FIL-15-2025

- **Control 2.17: Multi-Agent Orchestration Limits** (High)
  - Delegation depth limits by zone (Zone 1: 0, Zone 2: 2, Zone 3: 3)
  - Circuit breaker configuration for cascade failure prevention
  - HITL checkpoint integration
  - Regulatory alignment: FINRA 2026 Priorities

- **Control 2.18: Automated Conflict of Interest Testing** (Critical)
  - Test scenarios for proprietary bias, commission bias, cross-selling
  - SEC Reg BI compliance testing procedures
  - Automated test execution scripts
  - Regulatory alignment: SEC Reg BI, SEC 10b-5

- **Control 3.10: Hallucination Feedback Loop** (Medium)
  - User feedback collection mechanisms
  - Hallucination categorization taxonomy
  - Remediation tracking workflow
  - Regulatory alignment: CFPB UDAAP, SOX 302

- **Control 4.6: Grounding Scope Governance** (Critical)
  - Semantic Index site scoping configuration
  - Exclusion rules for Draft, Archived, Personal content
  - PowerShell for auditing indexed content scope
  - Regulatory alignment: SEC 17a-3/4, GLBA

#### Control Enhancements

- **Control 1.7 (Audit Logging)** - Added Adversarial Input Pattern Detection section with encoding attack detection (Base64, Unicode obfuscation, prompt chaining)
- **Control 2.6 (Model Risk Management)** - Added Step 6a: Prompt Engineering Change Review with checklist for system prompt, topic, fallback, and grounding instruction changes
- **Control 3.4 (Incident Reporting)** - Added Step 5a: RAG Citation Logging for Incident Investigation with KQL queries
- **Control 4.2 (Site Access Reviews)** - Added AI Agent Service Account Access Reviews section with least privilege checklist for service principals

#### New Operational Templates

- **AI Incident Response Playbook** (`specs/ai-incident-response-playbook.md`)
  - Incident categories: Hallucination, Prompt Injection, Data Leakage, Bias
  - Response procedures with timelines (T+0 through T+48 hours)
  - Regulatory notification requirements (GLBA, FINRA 4530, SEC)
  - Post-incident review checklist

- **Human-in-the-Loop Trigger Definitions** (`specs/human-in-the-loop-triggers.md`)
  - Mandatory HITL triggers (financial thresholds, suitability determinations)
  - Configurable triggers (confidence scores, complexity indicators)
  - Zone-specific HITL configurations
  - SLA definitions and breach handling

- **Semantic Index Governance Queries** (`templates/semantic-index-governance-queries.md`)
  - PowerShell: Get-CopilotRestrictionAudit, Get-HighRiskIndexedContent
  - KQL queries for Sentinel monitoring
  - Weekly audit automation script

#### Framework Statistics Update

- **Total controls:** 49 → 55 (+6)
- **Pillar 1 (Security):** 20 → 21 (+1)
- **Pillar 2 (Management):** 15 → 18 (+3)
- **Pillar 3 (Reporting):** 9 → 10 (+1)
- **Pillar 4 (SharePoint):** 5 → 6 (+1)
- **Operational templates:** 9 → 10 (+1)
- **Operational specifications:** 5 → 7 (+2)

---

### Operational Templates & Comprehensive Framework Validation

**Status:** Operational templates released + comprehensive validation against Microsoft Learn documentation
**Date:** January 10, 2026
**Scope:** Enhancements to existing 48 controls; no breaking changes

#### Added

- **Operational Templates Section** - 14 new production-ready templates and specifications
  - 9 implementation templates (matrices, schemas, registries)
  - 5 technical specifications (dashboards, detection, routing)
  - Optional Colorado AI Act readiness module (conditional for CO operations)
- **Infrastructure & Documentation**
  - `.claude/claude.md` - Claude Code agent instructions (mirrors GitHub Copilot guidance)
  - Comprehensive validation report with regulatory and technical feasibility assessment
  - Cross-reference links from existing controls (1.7, 2.7, 2.12, 3.8) to related templates
- **Review & Validation Materials**
  - `review/validation-findings.md` - Comprehensive review against Microsoft Learn (697 lines)
  - `review/validation-review-response.md` - Validation results (12 findings validated, 4 rejected as outdated)
  - `review/Copilot Studio Governance Review.docx` - External review documentation

#### Enhanced

- **73 control and documentation files** updated based on Microsoft Learn validation (Jan 2026)
  - **Control 1.1** - Added agent creation limitation warning and sterile containment strategy
  - **Control 1.5** - Added 6 Copilot Studio channel connectors documentation; noted DLP enforcement now enabled by default
  - **Control 1.7** - Added automatic security scan pre-publish feature; links to Decision Log Schema, Zone 1 Explainability, Evidence Pack Assembly
  - **Control 2.1** - Expanded Managed Environment features to full 24-capability list
  - **Control 2.2** - Updated environment group rules count to 21 with source citations
  - **Control 2.7** - Links to Supply Chain Risk Register Entry template
  - **Control 2.12** - Links to Escalation Matrix and Action Authorization Matrix
  - **Control 2.15** - Added environment routing fallback warning (users route to default environment if no rule matches)
  - **Control 3.1** - Clarified two agent inventories (M365 Admin Center vs Power Platform Admin Center)
  - **Control 3.8** - Renamed from "Copilot Command Center" to "Copilot Hub and Governance Dashboard" (official Microsoft terminology); links to Real-time Compliance Dashboard and Evidence Pack Assembly
  - **Control 4.1** - Added Restricted SharePoint Search (RSS) allow-list guidance and Restricted Access Control (RAC) for ethical walls
  - Multiple list formatting, cross-linking, and Microsoft Learn citation improvements across all pillars
- **Gap Analysis Enhancements (January 2026)**
  - **Control 2.1** - Added cross-tenant inbound/outbound restrictions (capability #19); updated to 24 total Managed Environment capabilities
  - **Control 1.7** - Added granular Copilot Studio audit operations tables (25+ operation names for targeted audit searches)
  - **Control 1.4** - Added Copilot Studio DLP examples (4 scenarios: social media blocking, HTTP restrictions, knowledge sources, channel restrictions)

#### Fixed

- Repository folder structure - Eliminated nested duplication (was `FSI-AgentGov/FSI-AgentGov/`, now `FSI-AgentGov/`)
- 615 markdown list formatting issues resolved
- Broken Microsoft Learn URLs corrected across all documentation
- Control navigation and cross-reference accuracy

#### Validation & Compliance

- **Regulatory citations verified:** FINRA 2026 Report, SEC 2026 Exam Priorities, Colorado SB24-205
- **Technical feasibility assessed:** Purview audit capabilities with documented workarounds
- **Microsoft Learn validation:** All 48 controls validated against current Microsoft documentation (Jan 2026)
  - 12 corrections validated and incorporated
  - 4 outdated claims rejected
  - 12 missing governance controls identified for future consideration
- **Alignment confirmed:** All 10 operational template gaps enhance existing 48 controls with zero conflicts

#### Documentation

- CONTRIBUTING.md - Added reference to `.claude/claude.md` for Claude Code users
- Multiple control files - Enhanced with comprehensive FSI guidance and regulatory alignment
- 2,597 total insertions, 426 deletions across 73 files

---

## [Beta] — December 2025

### Initial Beta Release

**Status:** First public beta  
**Date:** December 2025  
**Validation:** Awaiting customer feedback and testing; will advance to Final Release after at least one FSI customer validation and confirmation that no major control gaps exist.

#### Added

- **48 Governance Controls** across 4 pillars (Security, Management, Reporting, SharePoint)
- **Markdown documentation** (single source of truth) with structured organization
  - Getting Started: 4 guides (overview, scope, quick-start, governance zones)
  - Reference: 48 control files + RACI, regulatory mappings, glossary, FAQ
- **Role-based Excel templates** (6 downloads)
  - Role-specific checklists (Entra, Power Platform, Purview, SharePoint, Compliance)
  - Governance maturity dashboard for tracking all 48 controls
- **Release Notes** (`CHANGELOG.md`)
- **Regulatory Mappings**
  - FINRA 4511/3110: 100% coverage (6-year retention)
  - SEC 17a-3/17a-4: 88% coverage (6-year retention)
  - SOX 302/404: 81% coverage (7-year retention)
  - GLBA 501b: 93% coverage (5-7 year retention)
  - OCC 2011-12 & Fed SR 11-7: 58% coverage (per-model retention)
- **Governance Zone Model** (Personal, Team, Enterprise)
  - Graduated controls based on agent risk and scope
  - Zone-specific implementation guidance
- **Operational Procedures**
  - Daily, weekly, monthly, quarterly operations checklist
  - 37 documented runbooks with step-by-step navigation
- **RACI Matrix**
  - Clear role definitions (AI Administrator, Power Platform Admin, Compliance Admin, Security Admin, SharePoint Admin)
  - Escalation and reporting lines
- **Exam Preparation Guides**
  - FINRA, SEC, SOX, GLBA, OCC, and Federal Reserve exam focus areas
  - Control-to-regulation mapping for auditor Q&A

#### Documentation Features

### Known Limitations (Beta)

- **Microsoft Graph Connectors**: Deep auditing for custom connector actions is still in preview by Microsoft.
- **Model Risk Management**: "Bias Testing" control relies on emerging tooling (Azure AI Content Safety) which may require custom implementation.
- **Cost Allocation**: Granular token-level cost tracking per user/department is currently an estimation based on capacity units, not exact consumption.

### Planned for Final Release

- **Automated Policy Scripts**: PowerShell scripts to apply baseline DLP policies automatically.
- **PowerBI Dashboard Template**: A `.pbix` file to visualize the inventory and compliance status.
- **Terraform/Bicep Modules**: Infrastructure-as-Code for deploying the management zones.

### Feedback

**Beta users:** Please report issues, gaps, or clarification requests via GitHub Issues. Include:
- Control ID (if applicable)
- Scenario description
- Suggested improvement

All feedback will be evaluated for inclusion in the Final Release.



---

**Note:** This framework is maintained as a living document. See README.md for review triggers and update frequency.
