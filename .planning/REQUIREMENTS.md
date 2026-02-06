# Requirements: FSI-AgentGov v3 — Observability & Documentation Updates

**Defined:** 2026-02-05
**Core Value:** Documentation and solutions that US FSI customers trust.

## v3 Requirements

Requirements for this milestone. Each maps to roadmap phases.

### Core Telemetry Infrastructure

- [x] **TELE-01**: Application Insights workspace configured with Copilot Studio telemetry integration
- [x] **TELE-02**: Log Analytics workspace with 730-day interactive retention for FSI compliance
- [x] **TELE-03**: ADLS Gen2 export via Diagnostic Settings for SEC 17a-4 long-term retention (6 years)
- [x] **TELE-04**: RBAC separation between operational monitoring and compliance audit data paths
- [x] **TELE-05**: PII sanitization guidance for conversation text in customDimensions
- [x] **TELE-06**: Sampling and cost management configuration to prevent ingestion cost explosion

### KQL Query Library

- [x] **KQL-01**: Agent usage analytics query (sessions, messages, completion rates over time)
- [x] **KQL-02**: Error categorization query (connector errors, knowledge source failures, orchestration timeouts)
- [x] **KQL-03**: Latency distribution query (P50/P95/P99 response times)
- [x] **KQL-04**: Generative answers telemetry query (topic, result, feedback extraction)
- [x] **KQL-05**: Flow failure correlation query (Power Automate failures linked to agent conversations)
- [x] **KQL-06**: Agent decision audit trail query (FINRA 3110/SR 11-7 compliance)
- [x] **KQL-07**: RAI content filtering detection query (XPIADetected, JailbreakDetected from Purview)

### Azure Monitor Workbooks

- [x] **WKBK-01**: Operational health workbook (agent availability, error rates, latency by zone)
- [x] **WKBK-02**: Error diagnostics workbook (failure drill-down, root cause analysis)
- [x] **WKBK-03**: Enterprise usage overview workbook (adoption, engagement, channel distribution)

### Alert Rules

- [x] **ALRT-01**: High failure rate alert (>5% threshold with zone-specific tuning)
- [x] **ALRT-02**: Latency regression alert (dynamic threshold based on baseline)
- [x] **ALRT-03**: Abnormal usage pattern alert (session count anomaly detection)
- [x] **ALRT-04**: Action group configuration (Teams notification + email escalation)

### Power BI Integration

- [x] **PBI-01**: Semantic model documentation (star schema, relationships, RLS by zone)
- [x] **PBI-02**: DAX measures for sessions, average latency, and error rate
- [x] **PBI-03**: Integration guidance for DirectQuery (Premium) and ADX connector (Pro) methods

### Viva Insights

- [x] **VIVA-01**: Scope and limitations documentation (what Viva Insights does and does NOT cover for Copilot Studio)
- [x] **VIVA-02**: Cross-reference mapping between Viva Insights metrics and Application Insights telemetry

### Governance & Compliance Mapping

- [x] **GOV-01**: Governance mapping document linking observability to existing 62-control framework
- [x] **GOV-02**: SR 11-7 model risk monitoring KQL patterns and audit evidence guidance
- [x] **GOV-03**: SOX 302/404 control evidence documentation for agent observability

### Deployment & Validation

- [ ] **DEPL-01**: deploy-workbooks.ps1 script (Azure CLI, idempotent, #Requires, try-catch)
- [ ] **DEPL-02**: deploy-alerts.ps1 script (alert rules + action groups, idempotent)
- [ ] **DEPL-03**: Validation checklist (pre-deployment prerequisites + post-deployment verification)

### Solution Documentation

- [x] **SDOC-01**: README.md with architecture overview, compliance mapping, quick start guide
- [x] **SDOC-02**: architecture.md with Mermaid data flow diagrams, SoD boundaries, data retention
- [x] **SDOC-03**: prerequisites.md with Azure AD roles, Power BI licensing, data residency, networking
- [x] **SDOC-04**: governance-mapping.md linking solution artifacts to framework controls

### Agent 365 & Identity Documentation

- [ ] **A365-01**: Microsoft Entra Agent ID documentation (identity architecture, sponsorship model, Conditional Access)
- [ ] **A365-02**: Agent 365 unified control plane architecture document (registry, access control, security)
- [ ] **A365-03**: M365 Admin Center Agent Settings documentation (allowed types, sharing, templates)

### Control Enhancements

- [ ] **CTRL-01**: Virtual connectors enumeration and DLP guidance added to Control 1.5
- [ ] **CTRL-02**: Enhanced DSPM AI Observability capabilities added to Control 1.6
- [ ] **CTRL-03**: AI Feature Access Control (user-level restrictions, zone-based enablement) added to Control 3.8
- [ ] **CTRL-04**: AI Administrator role added to role catalog
- [ ] **CTRL-05**: Defender XDR Administrator role added to role catalog
- [ ] **CTRL-06**: SharePoint Restricted Search documented in Control 4.6 or 4.7 (when released)

## Future Requirements

Deferred to later milestones. Tracked but not in current roadmap.

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

Which phases cover which requirements. Updated after roadmap creation.

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
| DEPL-01 | Phase 5 | Pending |
| DEPL-02 | Phase 5 | Pending |
| DEPL-03 | Phase 5 | Pending |
| A365-01 | Phase 6 | Pending |
| A365-02 | Phase 6 | Pending |
| A365-03 | Phase 6 | Pending |
| CTRL-01 | Phase 7 | Pending |
| CTRL-02 | Phase 7 | Pending |
| CTRL-03 | Phase 7 | Pending |
| CTRL-04 | Phase 7 | Pending |
| CTRL-05 | Phase 7 | Pending |
| CTRL-06 | Phase 7 | Pending |

**Coverage:**
- v3 requirements: 44 total
- Mapped to phases: 44 (100%)
- Unmapped: 0

**Phase breakdown:**
- Phase 1 (Telemetry Infrastructure & Solution Foundation): 10 requirements
- Phase 2 (KQL Query Library & Governance Mapping): 10 requirements
- Phase 3 (Azure Monitor Workbooks & Alert Rules): 7 requirements
- Phase 4 (Power BI Integration & Viva Insights): 5 requirements
- Phase 5 (Deployment Scripts & Validation): 3 requirements
- Phase 6 (Agent 365 & Identity Documentation): 3 requirements
- Phase 7 (Control Enhancements & Role Updates): 6 requirements

---
*Requirements defined: 2026-02-05*
*Last updated: 2026-02-06 (Phase 4 complete: 32/44 requirements satisfied)*
