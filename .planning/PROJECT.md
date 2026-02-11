# FSI-AgentGov Comprehensive Audit & Enhancement

## What This Is

A comprehensive audit and enhancement project for the FSI Agent Governance Framework, spanning two repositories: FSI-AgentGov (documentation) and FSI-AgentGov-Solutions (deployable solutions). The goal is to maintain accuracy, resolve tech debt, improve documentation architecture, and complete work-in-progress solutions so US financial sector customers can confidently use this framework.

## Core Value

**Documentation and solutions that US FSI customers trust.** Every control must be accurate, every solution must work, and ongoing maintenance must be sustainable.

## Current Milestone: v10 Conditional Access Automation

**Goal:** Enhance validated CA policy deployment scripts with Tier 2 governance infrastructure — Dataverse persistence, Power Automate automation, drift detection, alerting, SHA-256 evidence export — creating a complete policy lifecycle management solution for Controls 1.11, 1.23, and 1.18.

**Target deliverables:**
- CAAClient PowerShell module with Tier 2 conventions (module structure, error handling, help comments)
- 8 CA policy templates validated against current Graph API schema
- Zone lookup integration with ELM Dataverse for zone-appropriate policy deployment
- Dataverse tables for policy baselines, validation history (immutable), and violations
- Power Automate daily compliance scan and drift detection flows
- Teams adaptive card alerting with zone-based severity classification
- SHA-256 integrity-hashed evidence export for FINRA/SEC examination support
- Control 1.11 framework integration and Compliance Dashboard feed

## Current State (v7 Shipped)

**Framework Version:** 1.2.38 (February 2026)

**Shipped:**
- v1: 62 controls verified, Agent 365 architecture, regulatory validation, solutions audit, unified monitoring
- v2: PowerShell security fixes, documentation architecture (breadcrumbs + playbook discovery), monitoring config externalization, Compliance Dashboard v1.0.0, Scope Drift Monitor v1.1.0
- v3: Agent Observability Foundation solution, Agent 365/Entra Agent ID documentation, Q1 2026 control enhancements (virtual connectors, DSPM, AI Feature Access, SharePoint Restricted Search), role catalog expansion
- v4: Audit Configuration Validator v1.0.0 — automated tenant/environment audit validation with drift detection, multi-channel alerting, and SHA-256 evidence export
- v5: Session Security Configurator — inactivity timeout automation per zone with drift detection and compliance reporting
- v6: Agent Access Governance Monitor — unrestricted agent access detection with zone-based validation and evidence export
- v7: Content Moderation Governance Monitor — per-agent moderation level validation with drift detection and SHA-256 evidence export
- v7.1: Framework Currency Reviews — Dataverse deprecation, Agent 365 GA, evaluation framework, multi-source agent investigation

**Solutions Status:**
- 10 Completed: Environment Lifecycle Management, Message Center Monitor, Pipeline Governance Cleanup, Compliance Dashboard, Scope Drift Monitor, Agent Observability Foundation, Audit Configuration Validator, Session Security Configurator, Agent Access Governance Monitor, Content Moderation Governance Monitor
- 1 Validated: FINRA Supervision Workflow
- 4 Work In Progress: Deny Event Correlation Report, Conditional Access Automation, Segregation Detector, RAG Source Validator
- 3 Planned: COI Testing, Hallucination Tracker, DR Testing Framework

## Requirements

### Validated

Capabilities delivered:

**v1 Milestone:**
- ✓ 62 controls verified against current Microsoft capabilities — v1 Phase 2
- ✓ 248 control playbooks + 27 advanced implementation docs — v1 Phase 2
- ✓ Agent 365 strategic architecture documented — v1 Phase 3
- ✓ Feature enhancements (virtual connectors, DSPM, AI Feature Access, Defender, roles) — v1 Phase 4
- ✓ Regulatory validation (7 federal bodies + 4 state AI laws) — v1 Phase 5
- ✓ 13 solutions audited with status classifications — v1 Phase 6
- ✓ Solutions functionally tested (58/59 artifacts PASS) — v1 Phase 7
- ✓ Unified monitoring system (Learn + Regulatory) — v1 Phase 8
- ✓ GitHub Pages documentation publishing — existing
- ✓ Regulatory mappings (FINRA, SEC, SOX, GLBA, OCC, Fed SR 11-7, CFTC) — existing

**v2 Milestone:**
- ✓ PowerShell security vulnerabilities eliminated (ConvertTo-SecureString pattern) — v2 Phase 1
- ✓ Comprehensive error handling in production scripts — v2 Phase 1
- ✓ #Requires statements on all 14 PowerShell scripts — v2 Phase 1
- ✓ Breadcrumb navigation enabled site-wide — v2 Phase 2
- ✓ INFO admonition boxes on all 62 control pages for playbook discovery — v2 Phase 2
- ✓ Monitoring classification patterns externalized to YAML (391 lines) — v2 Phase 3
- ✓ Compliance Dashboard v1.0.0 production-ready — v2 Phase 4
- ✓ Scope Drift Monitor v1.1.0 production-ready — v2 Phase 5

**v3 Milestone:**
- ✓ Agent Observability Foundation solution (14 KQL queries, 3 workbooks, 4 alerts, Power BI, deployment scripts) — v3 Phases 1-5
- ✓ Agent 365 & Entra Agent ID unified governance document (1009 lines, 17-control impact analysis) — v3 Phase 6
- ✓ Virtual connectors enumeration and DLP guidance (11 connectors, zone-specific) — v3 Phase 7
- ✓ Enhanced DSPM AI Observability with unified DSPM experience — v3 Phase 7
- ✓ AI Feature Access Control with zone-based enablement and Admin Exclusion Groups — v3 Phase 7
- ✓ SharePoint Restricted Search with positive governance model (100-site allowed list) — v3 Phase 7
- ✓ AI Administrator and Defender XDR Admin role catalog expansion with FSI guidance — v3 Phase 7

**v4 Milestone:**
- ✓ Audit Configuration Validator v1.0.0 with dual validation strategy (cmdlet + canary event) — v4 Phase 1
- ✓ Dataverse infrastructure with immutable validation history and zone-specific retention rules — v4 Phase 2
- ✓ Automated daily validation with drift detection and multi-channel alerting (Teams + email) — v4 Phase 3
- ✓ SHA-256 integrity-hashed compliance evidence export for SEC 17a-4(f) support — v4 Phase 4
- ✓ Control 1.7 framework integration and solutions-index.md catalog entry — v4 Phase 4

### Active

**v5-v9 Milestone Series: Customer-Requested Automation Solutions**

4 remaining automation solutions addressing customer-identified gaps, plus integration milestone:
- v5: Session Security Configurator — inactivity timeout automation per zone
- v6: Agent Access Governance Monitor — unrestricted agent access detection
- v7: Content Moderation Governance Monitor — AI content moderation policy enforcement
- v8: File Upload Security Configurator — MIME type restriction enforcement
- v9: Integration — ELM hooks, Compliance Dashboard feeds, cross-solution wiring

**Current milestone: v10 — Conditional Access Automation (IN PROGRESS)**

### Out of Scope

- Non-US regulations — this framework is specifically for US financial sector
- Real-time monitoring — batch/scheduled monitoring is sufficient
- Mobile or alternative interfaces — GitHub Pages is the delivery mechanism
- Token-level cost tracking — Copilot Studio does not expose per-call token data
- GDPR Article 22 — US FSI scope only, no EU regulatory coverage
- Third-party observability platforms — Microsoft-native stack only

### Deferred to v10+

- MCP server for governance framework
- Copilot Studio agent for governance Q&A
- Complete remaining WIP solutions (Deny Event, Conditional Access, Segregation Detector, RAG Validator)
- Complete Planned solutions (COI Testing, Hallucination Tracker, DR Testing)
- Navigation auto-generation with Awesome Pages plugin (risk of breaking pedagogical structure)
- .pbit Power BI template file (TMDL import path is functional workaround)
- Dynamic threshold tuning (requires 2-week production baseline)
- Multi-agent orchestration tracing

## Context

**Repository Structure:**
- **FSI-AgentGov** (this repo): MkDocs-based documentation site with 62 controls, playbooks, and framework guidance
- **FSI-AgentGov-Solutions** (`C:/dev/FSI-AgentGov-Solutions`): Companion repo with deployable solutions (PowerShell, Power Automate, Dataverse schemas)

**Target audience:**
- US financial sector Microsoft 365 administrators
- Compliance auditors
- Power Platform administrators

**Regulations covered:**
- FINRA 4511/3110/25-07
- SEC 17a-3/4
- SOX 302/404
- GLBA 501(b)
- OCC 2011-12
- Fed SR 11-7
- CFTC 1.31

## Constraints

- **Scope**: US financial sector only — no international regulations
- **Platform**: Microsoft 365 / Power Platform / Copilot Studio agents
- **Format**: Must maintain existing 10-section control template structure
- **Cross-repo**: Git operations must run from within target repo
- **Language**: Must use regulatory-safe language ("supports compliance" not "ensures compliance")
- **Solutions**: Each solution completed as standalone phase (one at a time)

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Audit both repos in one project | Documentation and solutions are interrelated; changes often span both | ✓ Good |
| Review solutions one at a time | Ensures thorough validation without overwhelming scope | ✓ Good |
| Simplify monitoring systems | User wants straightforward implementations, not over-engineered | ✓ Good |
| Tech debt before architecture | Fix security/quality issues before adding new features | ✓ Good |
| Architecture before solutions | Documentation improvements benefit all future work | ✓ Good |
| Defer MCP server and Copilot agent to v3 | Keep v2 focused on debt, architecture, and 2 solutions | ✓ Good |
| Only complete 2 WIP solutions in v2 | Compliance Dashboard and Scope Drift Monitor are closest to done | ✓ Good |
| Defer ARCH-04 (awesome-pages) to v3 | Risk of breaking pedagogical nav structure per research | ✓ Good |
| Defer ARCH-05 (SQLite) indefinitely | JSON sufficient for 209 URLs | ✓ Good |
| Human verification gate for solutions | Automated + human checkpoint ensures production quality | ✓ Good |
| Unpacked solution format | Enables version control and pac CLI packaging | ✓ Good |
| Consolidate 13 phases to 7 | Research suggested 10+3 phases; consolidation improves coherence | ✓ Good |
| 730-day default retention | SEC 17a-4(b)(4) requires 2-year retention for broker-dealer communications | ✓ Good |
| WORM policy excluded from automation | Irreversible — too risky for accidental lockdown | ✓ Good |
| Dual-grain star schema for Power BI | Session-grain for trends, event-grain for drill-down investigation | ✓ Good |
| Unified Agent 365 document | Single comprehensive source consolidates 3 requirements | ✓ Good |
| Function-based KQL query organization | Reusability over regulation-based organization | ✓ Good |
| SharePoint Restricted Search at GA | Research confirmed GA status from Microsoft Learn documentation | ✓ Good |
| AI Administrator expanded scope | Comprehensive governance role beyond basic Copilot management | ✓ Good |
| 5 separate milestones for 5 solutions | Each solution is self-contained milestone; cleaner scope, faster cycles | ✓ Good |
| Enhance existing controls (not new ones) | Keep 62-control structure; add automation sections to existing controls | ✓ Good |
| Separate integration milestone (v9) | Build all 5 solutions first, then wire ELM + Dashboard in v9 | ✓ Good |
| Dual validation strategy (cmdlet + canary) | Prevents false positives from audit lag; canary verifies actual audit pipeline | ✓ Good |
| Organization-owned Dataverse tables | Immutable audit history; security roles remove Write/Delete post-deployment | ✓ Good |
| Auto-remediation deferred to v4.1+ | Too risky without approval workflow; validation-only meets SEC 17a-4(f) | ✓ Good |

| v7.1 maintenance milestone | Interstitial docs review before v8; todos have time-sensitive items | ✓ Good |
| v8 binary validation model | File upload is enabled/disabled per agent, not multi-level; solution validates on/off status per zone | ✓ Good |
| v8 Control 1.14 as primary | Data minimization — file uploads expand data intake beyond declared scope | ✓ Good |
| v8 content moderation cross-check | Agents with file uploads enabled must meet minimum moderation level by zone | ✓ Good |
| v9 canonical zone values 1/2/3 | Match ELM/CD convention; ACV's 100000001 series is internal-only | — Pending |
| v9 daily batch feeds | Batch/daily sufficient for governance monitoring; no real-time webhooks | — Pending |
| v9 ELM → ACV auto-registration | Only ACV auto-registers on provisioning; other solutions register on first scan | — Pending |
| v9 cross-solution-integration dir | Integration code lives in dedicated solution directory in FSI-AgentGov-Solutions | — Pending |

---
*Last updated: 2026-02-10 after v9 milestone start*
