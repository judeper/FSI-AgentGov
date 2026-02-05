# ROADMAP: FSI-AgentGov v3 — Observability & Documentation Updates

**Milestone:** v3
**Phases:** 7
**Requirements:** 44 total
**Depth:** Comprehensive
**Created:** 2026-02-05

## Overview

This milestone delivers two strategic capabilities: **Agent Observability Foundation** (FSI-AgentGov-Solutions) and **Documentation Gap Closure** (FSI-AgentGov). The observability solution provides FSI-compliant monitoring for Copilot Studio and Agent 365 SDK agents using Azure-native telemetry. Documentation updates align the framework with Microsoft's 2025-2026 governance releases (Agent 365, Entra Agent ID, enhanced Defender capabilities).

**Key outcomes:**
- Production-ready observability solution with KQL queries, workbooks, alerts, Power BI integration
- Governance mapping linking observability artifacts to 62-control framework
- Agent 365 architecture documentation for unified control plane migration
- Control enhancements for virtual connectors, DSPM, AI feature access

## Phases

### Phase 1: Telemetry Infrastructure & Solution Foundation

**Goal:** Telemetry pipeline is operational with FSI-compliant data retention and solution documentation is complete.

**Primary Repository:** FSI-AgentGov-Solutions

**Dependencies:** None (foundation phase)

**Requirements:**
- TELE-01: Application Insights workspace with Copilot Studio integration
- TELE-02: Log Analytics workspace with 730-day retention
- TELE-03: ADLS Gen2 export via Diagnostic Settings (SEC 17a-4 compliance)
- TELE-04: RBAC separation (operational vs compliance data paths)
- TELE-05: PII sanitization guidance
- TELE-06: Sampling and cost management configuration
- SDOC-01: README.md with architecture overview and quick start
- SDOC-02: architecture.md with Mermaid diagrams and SoD boundaries
- SDOC-03: prerequisites.md with Azure AD roles and licensing
- SDOC-04: governance-mapping.md linking solution to framework controls

**Success Criteria:**
1. User can deploy Application Insights with 730-day retention via prerequisites checklist
2. User can verify telemetry flowing from Copilot Studio agent to customEvents table
3. User can access ADLS Gen2 compliance export for SEC 17a-4 long-term retention
4. User can read solution README and understand architecture without external research
5. User can identify which framework controls require observability evidence

**Plans:** 4 plans

Plans:
- [x] 01-01-PLAN.md — Config scaffolding and provision.py (Azure resource provisioning) [79c57db, 7fd0058]
- [ ] 01-02-PLAN.md — README, architecture, and prerequisites documentation
- [ ] 01-03-PLAN.md — Teardown and verification scripts (teardown, telemetry, WORM)
- [ ] 01-04-PLAN.md — Governance mapping and compliance guides (PII, cost, WORM docs)

---

### Phase 2: KQL Query Library & Governance Mapping

**Goal:** Reusable KQL queries enable consistent metrics across all visualization layers with governance compliance patterns.

**Primary Repository:** FSI-AgentGov-Solutions

**Dependencies:** Phase 1 (requires telemetry infrastructure)

**Requirements:**
- KQL-01: Agent usage analytics query (sessions, messages, completion rates)
- KQL-02: Error categorization query (connector errors, knowledge source failures)
- KQL-03: Latency distribution query (P50/P95/P99 response times)
- KQL-04: Generative answers telemetry query (topic, result, feedback)
- KQL-05: Flow failure correlation query (Power Automate failures)
- KQL-06: Agent decision audit trail query (FINRA 3110/SR 11-7 compliance)
- KQL-07: RAI content filtering detection query (XPIADetected from Purview)
- GOV-01: Governance mapping document linking observability to 62 controls
- GOV-02: SR 11-7 model risk monitoring KQL patterns and audit evidence
- GOV-03: SOX 302/404 control evidence documentation

**Success Criteria:**
1. User can run agent usage analytics query and see 30-day trend of sessions
2. User can categorize errors into connector/knowledge/orchestration buckets
3. User can generate FINRA 3110 audit trail showing agent decisions with timestamps
4. User can identify which KQL queries provide evidence for specific framework controls
5. User can generate SR 11-7 model risk monitoring report using documented patterns

---

### Phase 3: Azure Monitor Workbooks & Alert Rules

**Goal:** Operations team has real-time dashboards and proactive alerts for agent health monitoring.

**Primary Repository:** FSI-AgentGov-Solutions

**Dependencies:** Phase 2 (requires KQL query library)

**Requirements:**
- WKBK-01: Operational health workbook (availability, error rates, latency by zone)
- WKBK-02: Error diagnostics workbook (failure drill-down, root cause analysis)
- WKBK-03: Enterprise usage overview workbook (adoption, engagement, channels)
- ALRT-01: High failure rate alert (>5% threshold with zone tuning)
- ALRT-02: Latency regression alert (dynamic threshold based on baseline)
- ALRT-03: Abnormal usage pattern alert (session count anomaly detection)
- ALRT-04: Action group configuration (Teams notification + email escalation)

**Success Criteria:**
1. User can open operational health workbook and see agent success rates by zone
2. User can drill down into error diagnostics workbook to identify root cause of failure
3. User receives Teams notification within 5 minutes when failure rate exceeds threshold
4. User can tune alert thresholds independently for Zone 1/2/3 environments
5. User can deploy workbooks to new environment via ARM templates

---

### Phase 4: Power BI Integration & Viva Insights

**Goal:** Executives can access compliance dashboards and adoption metrics without KQL knowledge.

**Primary Repository:** FSI-AgentGov-Solutions

**Dependencies:** Phase 2 (requires KQL query library)

**Requirements:**
- PBI-01: Semantic model documentation (star schema, relationships, RLS by zone)
- PBI-02: DAX measures for sessions, average latency, and error rate
- PBI-03: Integration guidance for DirectQuery (Premium) and ADX connector (Pro)
- VIVA-01: Scope and limitations documentation (what Viva Insights covers)
- VIVA-02: Cross-reference mapping between Viva Insights and Application Insights

**Success Criteria:**
1. User can deploy Power BI semantic model with zone-based RLS
2. User can view executive dashboard showing cost, usage, and compliance posture
3. User can connect Power BI Pro using ADX connector without Premium license
4. User understands Viva Insights only covers Copilot Studio agents (not Agent Builder)
5. User can reconcile Viva Insights adoption metrics with Application Insights telemetry

---

### Phase 5: Deployment Scripts & Validation

**Goal:** Any administrator can deploy the observability solution following documented procedures with validation.

**Primary Repository:** FSI-AgentGov-Solutions

**Dependencies:** Phase 3 (requires workbooks and alerts artifacts)

**Requirements:**
- DEPL-01: deploy-workbooks.ps1 script (Azure CLI, idempotent, #Requires, try-catch)
- DEPL-02: deploy-alerts.ps1 script (alert rules + action groups, idempotent)
- DEPL-03: Validation checklist (pre-deployment prerequisites + post-deployment verification)

**Success Criteria:**
1. User can run deploy-workbooks.ps1 and see all workbooks deployed to target resource group
2. User can run deploy-alerts.ps1 and receive test alert in Teams channel
3. User can follow validation checklist and confirm all components operational
4. User can re-run deployment scripts without errors (idempotent behavior)
5. User receives clear error messages if prerequisites are missing

---

### Phase 6: Agent 365 & Identity Documentation

**Goal:** Framework reflects Microsoft's unified Agent 365 control plane and Entra Agent ID architecture.

**Primary Repository:** FSI-AgentGov

**Dependencies:** None (documentation track independent)

**Requirements:**
- A365-01: Microsoft Entra Agent ID documentation (identity architecture, sponsorship, CA)
- A365-02: Agent 365 unified control plane architecture document (registry, access control)
- A365-03: M365 Admin Center Agent Settings documentation (allowed types, sharing)

**Success Criteria:**
1. User understands how Entra Agent ID differs from traditional service principals
2. User can architect agent identity with sponsorship model for FINRA 3110 alignment
3. User understands Agent 365 unified governance vs. per-platform governance
4. User can configure M365 Admin Center Agent Settings when feature reaches GA
5. User can plan migration roadmap from current governance to Agent 365 architecture

---

### Phase 7: Control Enhancements & Role Updates

**Goal:** Framework controls reflect Q1 2026 Microsoft governance capabilities.

**Primary Repository:** FSI-AgentGov

**Dependencies:** None (documentation track independent)

**Requirements:**
- CTRL-01: Virtual connectors enumeration and DLP guidance added to Control 1.5
- CTRL-02: Enhanced DSPM AI Observability capabilities added to Control 1.6
- CTRL-03: AI Feature Access Control (user-level restrictions) added to Control 3.8
- CTRL-04: AI Administrator role added to role catalog
- CTRL-05: Defender XDR Administrator role added to role catalog
- CTRL-06: SharePoint Restricted Search documented in Control 4.6 or 4.7 (when released)

**Success Criteria:**
1. User can configure virtual connectors in Control 1.5 using updated DLP guidance
2. User understands enhanced DSPM AI Observability weekly risk assessments in Control 1.6
3. User can implement user-level AI feature restrictions in Control 3.8
4. User can assign AI Administrator role per updated role catalog guidance
5. User can implement SharePoint Restricted Search when feature reaches GA

---

## Progress

| Phase | Status | Plans | Requirements | Success Criteria |
|-------|--------|-------|--------------|------------------|
| 1 - Telemetry Infrastructure & Solution Foundation | In Progress | 1/4 | 10 | 5 |
| 2 - KQL Query Library & Governance Mapping | Pending | 0/0 | 10 | 5 |
| 3 - Azure Monitor Workbooks & Alert Rules | Pending | 0/0 | 7 | 5 |
| 4 - Power BI Integration & Viva Insights | Pending | 0/0 | 5 | 5 |
| 5 - Deployment Scripts & Validation | Pending | 0/0 | 3 | 5 |
| 6 - Agent 365 & Identity Documentation | Pending | 0/0 | 3 | 5 |
| 7 - Control Enhancements & Role Updates | Pending | 0/0 | 6 | 5 |

**Total:** 1/4 plans complete in Phase 1, 5/44 requirements partially satisfied (TELE-01,02,03,04,06)

---

## Cross-Repository Work

This milestone operates across two repositories:

| Phase | Primary Repo | Creates/Modifies |
|-------|--------------|------------------|
| 1 - Telemetry Infrastructure | FSI-AgentGov-Solutions | /agent-observability-foundation/* |
| 2 - KQL Query Library | FSI-AgentGov-Solutions | /agent-observability-foundation/queries/* |
| 3 - Azure Monitor Artifacts | FSI-AgentGov-Solutions | /agent-observability-foundation/workbooks/*, /alerts/* |
| 4 - Power BI Integration | FSI-AgentGov-Solutions | /agent-observability-foundation/power-bi/* |
| 5 - Deployment Scripts | FSI-AgentGov-Solutions | /agent-observability-foundation/scripts/* |
| 6 - Agent 365 Documentation | FSI-AgentGov | /docs/framework/agent-365-architecture.md, controls/pillar-1-security/* |
| 7 - Control Enhancements | FSI-AgentGov | /docs/controls/pillar-*/* |

**Git operations:** Each repo has separate git history. Git commands must run from within the target repo.

---

## Research Flags

Phases with research needs identified:

- **Phase 1:** Standard Azure deployment patterns (LOW research need)
- **Phase 2:** GDPR Article 22 applicability to US FSI firms may need legal review (MEDIUM research need)
- **Phase 3:** Standard workbook and alert patterns (LOW research need)
- **Phase 4:** Power BI semantic model design patterns (LOW research need)
- **Phase 5:** Standard PowerShell deployment patterns (LOW research need)
- **Phase 6:** Agent 365 preview feature architecture (HIGH research need - incomplete documentation)
- **Phase 7:** Standard control enhancement patterns (LOW research need)

Phases 1-5 use well-documented Azure patterns. Phase 6 may require deeper research due to preview feature status.

---

*Roadmap created: 2026-02-05*
*Last updated: 2026-02-05 (01-01-PLAN.md complete)*
