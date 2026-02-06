# Requirements Archive: v3 Observability & Documentation Updates

**Archived:** 2026-02-06
**Status:** SHIPPED

This is the archived requirements specification for v3.
For current requirements, see `.planning/REQUIREMENTS.md` (created for next milestone).

---

## v3 Requirements

Requirements for this milestone. Each maps to roadmap phases.

### Core Telemetry Infrastructure

- [x] **TELE-01**: Application Insights workspace configured with Copilot Studio telemetry integration — delivered via provision.py
- [x] **TELE-02**: Log Analytics workspace with 730-day interactive retention for FSI compliance — delivered via provision.py
- [x] **TELE-03**: ADLS Gen2 export via Diagnostic Settings for SEC 17a-4 long-term retention (6 years) — delivered via provision.py + WORM guidance
- [x] **TELE-04**: RBAC separation between operational monitoring and compliance audit data paths — delivered via config.yaml RBAC section
- [x] **TELE-05**: PII sanitization guidance for conversation text in customDimensions — delivered via pii-handling.md
- [x] **TELE-06**: Sampling and cost management configuration to prevent ingestion cost explosion — delivered via cost-management.md

### KQL Query Library

- [x] **KQL-01**: Agent usage analytics query (sessions, messages, completion rates over time) — delivered: agent-usage-analytics.kql
- [x] **KQL-02**: Error categorization query (connector errors, knowledge source failures, orchestration timeouts) — delivered: error-categorization.kql
- [x] **KQL-03**: Latency distribution query (P50/P95/P99 response times) — delivered: latency-distribution.kql
- [x] **KQL-04**: Generative answers telemetry query (topic, result, feedback extraction) — delivered: generative-answers-telemetry.kql
- [x] **KQL-05**: Flow failure correlation query (Power Automate failures linked to agent conversations) — delivered: flow-failure-correlation.kql
- [x] **KQL-06**: Agent decision audit trail query (FINRA 3110/SR 11-7 compliance) — delivered: agent-decision-audit-trail.kql
- [x] **KQL-07**: RAI content filtering detection query (XPIADetected, JailbreakDetected from Purview) — delivered: rai-content-filtering.kql

### Azure Monitor Workbooks

- [x] **WKBK-01**: Operational health workbook (agent availability, error rates, latency by zone) — delivered: operational-health.json ARM template
- [x] **WKBK-02**: Error diagnostics workbook (failure drill-down, root cause analysis) — delivered: error-diagnostics.json ARM template
- [x] **WKBK-03**: Enterprise usage overview workbook (adoption, engagement, channel distribution) — delivered: usage-overview.json ARM template

### Alert Rules

- [x] **ALRT-01**: High failure rate alert (>5% threshold with zone-specific tuning) — delivered: session-failure-rate alert rule
- [x] **ALRT-02**: Latency regression alert (dynamic threshold based on baseline) — delivered: latency-threshold alert rule
- [x] **ALRT-03**: Abnormal usage pattern alert (session count anomaly detection) — delivered: completeness-gap alert rule
- [x] **ALRT-04**: Action group configuration (Teams notification + email escalation) — delivered: 4 action groups + Logic App

### Power BI Integration

- [x] **PBI-01**: Semantic model documentation (star schema, relationships, RLS by zone) — delivered: 16 TMDL files with dual-grain star schema
- [x] **PBI-02**: DAX measures for sessions, average latency, and error rate — delivered: 19 DAX measures in CoreMetrics.tmdl
- [x] **PBI-03**: Integration guidance for DirectQuery (Premium) and ADX connector (Pro) methods — delivered: connector-decision-matrix.md

### Viva Insights

- [x] **VIVA-01**: Scope and limitations documentation (what Viva Insights does and does NOT cover for Copilot Studio) — delivered: viva-insights-scope.md
- [x] **VIVA-02**: Cross-reference mapping between Viva Insights metrics and Application Insights telemetry — delivered: viva-reconciliation-workflow.md

### Governance & Compliance Mapping

- [x] **GOV-01**: Governance mapping document linking observability to existing 62-control framework — delivered: governance-queries.md (507 lines)
- [x] **GOV-02**: SR 11-7 model risk monitoring KQL patterns and audit evidence guidance — delivered: 3 SR 11-7 KQL queries
- [x] **GOV-03**: SOX 302/404 control evidence documentation for agent observability — delivered: governance-queries.md SOX section

### Deployment & Validation

- [x] **DEPL-01**: deploy-workbooks.ps1 script (Azure CLI, idempotent, #Requires, try-catch) — delivered: 533-line script
- [x] **DEPL-02**: deploy-alerts.ps1 script (alert rules + action groups, idempotent) — delivered: 684-line script
- [x] **DEPL-03**: Validation checklist (pre-deployment prerequisites + post-deployment verification) — delivered: 411-line checklist

### Solution Documentation

- [x] **SDOC-01**: README.md with architecture overview, compliance mapping, quick start guide — delivered
- [x] **SDOC-02**: architecture.md with Mermaid data flow diagrams, SoD boundaries, data retention — delivered
- [x] **SDOC-03**: prerequisites.md with Azure AD roles, Power BI licensing, data residency, networking — delivered
- [x] **SDOC-04**: governance-mapping.md linking solution artifacts to framework controls — delivered

### Agent 365 & Identity Documentation

- [x] **A365-01**: Microsoft Entra Agent ID documentation (identity architecture, sponsorship model, Conditional Access) — delivered: agent-identity-architecture.md (1009 lines)
- [x] **A365-02**: Agent 365 unified control plane architecture document (registry, access control, security) — delivered: unified in agent-identity-architecture.md
- [x] **A365-03**: M365 Admin Center Agent Settings documentation (allowed types, sharing, templates) — delivered: unified in agent-identity-architecture.md

### Control Enhancements

- [x] **CTRL-01**: Virtual connectors enumeration and DLP guidance added to Control 1.5 — delivered: 11 connectors, zone-specific HTTP filtering
- [x] **CTRL-02**: Enhanced DSPM AI Observability capabilities added to Control 1.6 — delivered: unified DSPM experience, agent risk tracking
- [x] **CTRL-03**: AI Feature Access Control (user-level restrictions, zone-based enablement) added to Control 3.8 — delivered: granular Copilot settings, Admin Exclusion Groups
- [x] **CTRL-04**: AI Administrator role added to role catalog — delivered: comprehensive role documentation, 6-scenario FSI guidance
- [x] **CTRL-05**: Defender XDR Administrator role added to role catalog — delivered: informal alias clarification, Entra Security Admin mapping
- [x] **CTRL-06**: SharePoint Restricted Search documented in Control 4.6 — delivered: positive governance model, 100-site allowed list

## Future Requirements (Deferred)

### Advanced Observability
- **ADV-01**: Token usage tracking per agent (blocked — Copilot Studio does not expose token data natively)
- **ADV-02**: Multi-agent orchestration tracing (theoretical — requires implementation validation)
- **ADV-03**: Auto-remediation workflows (needs FSI-safe human approval patterns)
- **ADV-04**: Dynamic threshold tuning (requires 2-week production baseline first)
- **ADV-05**: Bias testing visualization (no industry standard benchmarks)

### Tooling
- **TOOL-01**: MCP server for governance framework
- **TOOL-02**: Copilot Studio agent for governance Q&A

### Solution Completion
- **SOLN-01**: Deny Event Correlation Report completion
- **SOLN-02**: Conditional Access Automation completion
- **SOLN-03**: Segregation Detector completion
- **SOLN-04**: RAG Source Validator completion
- **SOLN-05**: COI Testing (new)
- **SOLN-06**: Hallucination Tracker (new)
- **SOLN-07**: DR Testing Framework (new)

## Out of Scope

| Feature | Reason |
|---------|--------|
| Token-level cost tracking | Copilot Studio does not expose per-call token data (validated Feb 2026) |
| Real-time compliance scoring | Compliance is point-in-time assessment, not continuous streaming |
| Real-time streaming dashboards | Batch/scheduled refresh sufficient for FSI use cases |
| Custom ML anomaly detection | Simple thresholds more explainable for regulated environments |
| GDPR Article 22 automated decision tracking | US FSI scope only — no EU regulatory coverage |
| Third-party observability platforms | Microsoft-native stack only (Datadog, Splunk, etc. out of scope) |
| Blockchain audit trails | Azure Immutable Storage sufficient for SEC 17a-4 |
| Mobile dashboards | Power BI web and desktop sufficient |
| Non-US regulations | Framework is US financial sector only |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| TELE-01 | Phase 1 | Complete |
| TELE-02 | Phase 1 | Complete |
| TELE-03 | Phase 1 | Complete |
| TELE-04 | Phase 1 | Complete |
| TELE-05 | Phase 1 | Complete |
| TELE-06 | Phase 1 | Complete |
| SDOC-01 | Phase 1 | Complete |
| SDOC-02 | Phase 1 | Complete |
| SDOC-03 | Phase 1 | Complete |
| SDOC-04 | Phase 1 | Complete |
| KQL-01 | Phase 2 | Complete |
| KQL-02 | Phase 2 | Complete |
| KQL-03 | Phase 2 | Complete |
| KQL-04 | Phase 2 | Complete |
| KQL-05 | Phase 2 | Complete |
| KQL-06 | Phase 2 | Complete |
| KQL-07 | Phase 2 | Complete |
| GOV-01 | Phase 2 | Complete |
| GOV-02 | Phase 2 | Complete |
| GOV-03 | Phase 2 | Complete |
| WKBK-01 | Phase 3 | Complete |
| WKBK-02 | Phase 3 | Complete |
| WKBK-03 | Phase 3 | Complete |
| ALRT-01 | Phase 3 | Complete |
| ALRT-02 | Phase 3 | Complete |
| ALRT-03 | Phase 3 | Complete |
| ALRT-04 | Phase 3 | Complete |
| PBI-01 | Phase 4 | Complete |
| PBI-02 | Phase 4 | Complete |
| PBI-03 | Phase 4 | Complete |
| VIVA-01 | Phase 4 | Complete |
| VIVA-02 | Phase 4 | Complete |
| DEPL-01 | Phase 5 | Complete |
| DEPL-02 | Phase 5 | Complete |
| DEPL-03 | Phase 5 | Complete |
| A365-01 | Phase 6 | Complete |
| A365-02 | Phase 6 | Complete |
| A365-03 | Phase 6 | Complete |
| CTRL-01 | Phase 7 | Complete |
| CTRL-02 | Phase 7 | Complete |
| CTRL-03 | Phase 7 | Complete |
| CTRL-04 | Phase 7 | Complete |
| CTRL-05 | Phase 7 | Complete |
| CTRL-06 | Phase 7 | Complete |

**Coverage:**
- v3 requirements: 44 total
- Shipped: 44/44 (100%)
- Unmapped: 0

---

## Milestone Summary

**Shipped:** 44 of 44 v3 requirements
**Adjusted:** None — all requirements shipped as originally specified
**Dropped:** None

---
*Archived: 2026-02-06 as part of v3 milestone completion*
