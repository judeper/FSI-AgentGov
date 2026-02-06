# Milestone v3: Observability & Documentation Updates

**Status:** SHIPPED 2026-02-06
**Phases:** 1-7
**Total Plans:** 27

## Overview

This milestone delivered two strategic capabilities: **Agent Observability Foundation** (FSI-AgentGov-Solutions) and **Documentation Gap Closure** (FSI-AgentGov). The observability solution provides FSI-compliant monitoring for Copilot Studio and Agent 365 SDK agents using Azure-native telemetry. Documentation updates align the framework with Microsoft's 2025-2026 governance releases (Agent 365, Entra Agent ID, enhanced Defender capabilities).

**Key outcomes:**
- Production-ready observability solution with KQL queries, workbooks, alerts, Power BI integration
- Governance mapping linking observability artifacts to 62-control framework
- Agent 365 architecture documentation for unified control plane migration
- Control enhancements for virtual connectors, DSPM, AI feature access
- Role catalog expansion with AI Administrator and Defender XDR Admin

## Phases

### Phase 1: Telemetry Infrastructure & Solution Foundation

**Goal:** Telemetry pipeline is operational with FSI-compliant data retention and solution documentation is complete.
**Primary Repository:** FSI-AgentGov-Solutions
**Depends on:** None (foundation phase)
**Plans:** 4 plans

Plans:
- [x] 01-01: Config scaffolding and provision.py (Azure resource provisioning)
- [x] 01-02: README, architecture, and prerequisites documentation
- [x] 01-03: Teardown and verification scripts (teardown, telemetry, WORM)
- [x] 01-04: Governance mapping and compliance guides (PII, cost, WORM docs)

**Details:**
- Application Insights workspace with Copilot Studio telemetry integration
- Log Analytics workspace with 730-day interactive retention
- ADLS Gen2 export via Diagnostic Settings for SEC 17a-4 compliance (6 years)
- RBAC separation between operational and compliance data paths
- PII sanitization guidance for conversation text
- Sampling and cost management configuration
- Complete solution documentation (README, architecture, prerequisites, governance mapping)

**Completed:** 2026-02-05

---

### Phase 2: KQL Query Library & Governance Mapping

**Goal:** Reusable KQL queries enable consistent metrics across all visualization layers with governance compliance patterns.
**Primary Repository:** FSI-AgentGov-Solutions
**Depends on:** Phase 1 (requires telemetry infrastructure)
**Plans:** 3 plans

Plans:
- [x] 02-01: Query library foundation (README, usage-analytics, performance, error queries)
- [x] 02-02: Compliance queries (audit trail, RAI detection, generative answers, flow failures)
- [x] 02-03: SR 11-7 queries and governance-queries.md mapping document

**Details:**
- 14 KQL queries across 6 functional categories
- Agent decision audit trail for FINRA 3110/SR 11-7 compliance
- RAI content filtering detection (XPIADetected, JailbreakDetected)
- Governance mapping document linking queries to 62-control framework
- SR 11-7 model risk monitoring patterns with drift detection

**Completed:** 2026-02-05

---

### Phase 3: Azure Monitor Workbooks & Alert Rules

**Goal:** Operations team has real-time dashboards and proactive alerts for agent health monitoring.
**Primary Repository:** FSI-AgentGov-Solutions
**Depends on:** Phase 2 (requires KQL query library)
**Plans:** 5 plans

Plans:
- [x] 03-01: Operational Health workbook ARM template with zone/time parameters and drill-down
- [x] 03-02: Action groups (zone-based routing) and Logic App Teams notification
- [x] 03-03: Error Diagnostics and Usage Overview workbook ARM templates
- [x] 03-04: Alert rules (failure rate, latency regression, abnormal usage) with dynamic thresholds
- [x] 03-05: Phase documentation (workbooks README, alerts README, tuning guide, solution README update)

**Details:**
- 3 workbooks: Operational Health, Error Diagnostics, Usage Overview
- 4 alert rules with zone-specific thresholds
- 4 action groups (operations, compliance, security, cost management)
- Logic App for Teams channel notifications
- ARM templates for idempotent deployment

**Completed:** 2026-02-05

---

### Phase 4: Power BI Integration & Viva Insights

**Goal:** Executives can access compliance dashboards and adoption metrics without KQL knowledge.
**Primary Repository:** FSI-AgentGov-Solutions
**Depends on:** Phase 2 (requires KQL query library)
**Plans:** 4 plans

Plans:
- [x] 04-01: TMDL semantic model (dual-grain star schema, dimensions, relationships, zone-based RLS)
- [x] 04-02: DAX measures (CoreMetrics.tmdl) and Power BI integration guide
- [x] 04-03: KQL pre-aggregation functions, connector decision matrix, and solution README
- [x] 04-04: Viva Insights scope/limitations documentation and reconciliation workflow

**Details:**
- 16 TMDL files (database, model, 11 tables, relationships, RLS role, measures)
- 19 DAX measures across 6 categories (Session Metrics, Latency, Error Rates, Compliance, Trends, Event Detail)
- 4 KQL pre-aggregation functions for Power BI data layer
- Dual connector support: DirectQuery (Premium) and ADX Import (Pro)
- Viva Insights scope documentation and Application Insights reconciliation workflow

**Completed:** 2026-02-06

---

### Phase 5: Deployment Scripts & Validation

**Goal:** Any administrator can deploy the observability solution following documented procedures with validation.
**Primary Repository:** FSI-AgentGov-Solutions
**Depends on:** Phase 3 (requires workbooks and alerts artifacts)
**Plans:** 3 plans

Plans:
- [x] 05-01: deploy-workbooks.ps1 (533 lines, idempotent 3-workbook deployment with DryRun)
- [x] 05-02: deploy-alerts.ps1 (684 lines, 3-phase Logic App -> Action Groups -> Alert Rules)
- [x] 05-03: Validation checklist (411 lines) and README deployment section update

**Details:**
- Idempotent PowerShell deployment scripts with #Requires statements
- 3-phase alert deployment: Logic App -> Action Groups -> Alert Rules
- DryRun mode for deployment preview
- Confirmation prompts for production safety
- Comprehensive validation checklist (pre-deployment + post-deployment)

**Completed:** 2026-02-06

---

### Phase 6: Agent 365 & Identity Documentation

**Goal:** Framework reflects Microsoft's unified Agent 365 control plane and Entra Agent ID architecture.
**Primary Repository:** FSI-AgentGov
**Depends on:** None (documentation track independent)
**Plans:** 3 plans

Plans:
- [x] 06-01: Unified Agent 365 & Entra Agent ID governance document (1009 lines, 3 Mermaid diagrams, 17-control impact analysis)
- [x] 06-02: Agent 365 forward-reference notes for HIGH/MEDIUM-impact control files (10 controls)
- [x] 06-03: Agent 365 forward-reference notes for LOW-impact control files (7 controls) and Learn Monitor URL updates (12 new URLs)

**Details:**
- Unified governance document covering Entra Agent ID, Agent 365 control plane, M365 Admin Center settings
- 3 Mermaid diagrams (sponsorship flow, control plane architecture, admin settings hierarchy)
- 17-control impact analysis (HIGH: 4, MEDIUM: 6, LOW: 7)
- Migration roadmap with "prepare now, migrate later" tone
- Learn Monitor URLs expanded from 174 to 186

**Completed:** 2026-02-06

---

### Phase 7: Control Enhancements & Role Updates

**Goal:** Framework controls reflect Q1 2026 Microsoft governance capabilities.
**Primary Repository:** FSI-AgentGov
**Depends on:** None (documentation track independent)
**Plans:** 5 plans

Plans:
- [x] 07-01: Control 1.5 virtual connector expansion with zone-specific DLP guidance and 4 playbook updates
- [x] 07-02: Control 1.6 enhanced DSPM AI Observability with unified DSPM experience and 4 playbook updates
- [x] 07-03: Control 3.8 AI Feature Access Control with zone-based enablement and 4 playbook updates
- [x] 07-04: Control 4.6 SharePoint Restricted Search with AI grounding focus and 4 playbook updates
- [x] 07-05: Role catalog expansion (AI Admin, Defender XDR Admin) with role selection guidance and control cross-references

**Details:**
- 4 controls enhanced with Q1 2026 capabilities
- 16 playbooks updated (4 per control)
- Virtual connectors: 11 connectors enumerated with zone-specific DLP guidance
- DSPM AI Observability: Unified DSPM experience (preview, June 2026 GA)
- AI Feature Access Control: Granular Copilot settings with Admin Exclusion Groups
- SharePoint Restricted Search: Positive governance model with 100-site allowed list
- Role catalog: AI Administrator and Defender XDR Admin with 6-scenario FSI guidance

**Completed:** 2026-02-06

---

## Milestone Summary

**Key Decisions:**
- Consolidated 13 proposed phases to 7 for coherence
- Combined related Azure Monitor artifacts (telemetry + docs, queries + mapping, workbooks + alerts, Power BI + Viva)
- WORM policy excluded from automation (irreversible — too risky for accidental lockdown)
- 730-day default retention for SEC 17a-4(b)(4) compliance
- Function-based KQL query organization (not regulation-based) for reusability
- Dual-grain star schema for Power BI (session-grain + event-grain)
- Unified Agent 365 document combines 3 requirements into single comprehensive source
- SharePoint Restricted Search documented at GA status
- AI Administrator expanded beyond basic Copilot management to comprehensive governance role

**Issues Resolved:**
- SEC 17a-4 retention compliance via 730-day Log Analytics + ADLS Gen2 export
- FINRA 3110 audit trail gaps via agent-decision-audit-trail.kql with CompletenessPercent
- SR 11-7 model drift detection via 20% threshold with InvestigationRequired flag
- PII exposure risk via sanitization guidance and IncludePII toggle (default false)
- Cost explosion risk via adaptive sampling and 50%/75%/90% budget alerts
- Agent 365 migration uncertainty via "prepare now, migrate later" documentation approach

**Issues Deferred:**
- GDPR Article 22 applicability (US FSI scope only — no EU regulatory coverage)
- Viva Insights GA timeline confirmation (March 2026)
- M365 Admin Center Agent Settings GA date
- Multi-agent orchestration tracing pattern

**Technical Debt Incurred:**
- Missing .pbit Power BI template file (workaround via TMDL import path exists, medium impact)
- REQUIREMENTS.md traceability table partially out of sync (Phase 6-7 requirements show "Pending" despite completion)

---

_For current project status, see .planning/ROADMAP.md_

---

*Archived: 2026-02-06 as part of v3 milestone completion*
