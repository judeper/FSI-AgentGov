# Requirements: Agent Usage & Performance Workbook (v15)

## Overview

Deployable Azure Monitor Workbook template for Copilot Studio agent usage, performance, and error visibility — solving the ALM separation-of-duties gap for FSI organizations where production Analytics tab access is restricted.

**Source:** Deferred v13 todo ([Agent Usage & Performance Workbook for Enterprise ALM](todos/pending/2026-02-11-agent-usage-workbook-for-enterprise-alm.md))

## Requirement Categories

| Code | Category | Count |
|------|----------|-------|
| TEL | Telemetry Foundation | 2 |
| WBK | Workbook Template | 4 |
| DEP | Deployment & Access | 2 |
| FRM | Framework Integration | 3 |
| VAL | Validation | 1 |
| **Total** | | **12** |

## TEL - Telemetry Foundation

- [ ] **TEL-01:** Confirm Application Insights telemetry schema from Copilot Studio — document customEvents schema, customDimensions properties, channel identifiers (SharePoint vs Teams); identify available vs. custom telemetry fields
- [ ] **TEL-02:** Design KQL query library for workbook panels — KQL queries for all 3-tab panels (Usage/Business Value, Performance/Errors, Operational Health); parameterized by time range and agent ID

## WBK - Workbook Template

- [ ] **WBK-01:** Usage & Business Value tab — session counts, unique users (DAU/MAU), conversation volume trends, channel breakdown (SharePoint vs Teams), resolution/escalation rates, average session duration, "Assisted Hours" equivalent, business value estimation metrics
- [ ] **WBK-02:** Performance & Errors tab — response latency (p50, p95, p99), error rates by type (topic failure, API call failure, knowledge source timeout), agent action/connector call success rates, RAI content filtering trigger rates
- [ ] **WBK-03:** Operational Health tab — anomaly detection indicators, availability/uptime trends, hallucination/grounding indicators (custom telemetry), DLP policy match events
- [ ] **WBK-04:** Deployable workbook JSON template — single JSON file importable via Azure portal or ARM template; parameterized Application Insights resource ID; zone-aware thresholds

## DEP - Deployment & Access

- [ ] **DEP-01:** RBAC configuration for read-only access — document Application Insights Reader role assignment for workbook consumers; RBAC-scoped access solving the ALM/separation-of-duties gap
- [ ] **DEP-02:** Deployment playbook — ARM template or manual import instructions; prerequisites list; validation checklist

## FRM - Framework Integration

- [ ] **FRM-01:** Update Controls 3.2, 3.9, 2.9 to reference workbook — tip admonitions linking to workbook solution; ALM scenario cross-reference in relevant playbooks
- [ ] **FRM-02:** Add workbook to solutions-index.md — catalog entry with status, control mappings, and component list
- [ ] **FRM-03:** Customization guide — document how to extend workbook with custom telemetry, add panels, adjust thresholds per zone

## VAL - Validation

- [ ] **VAL-01:** Build and language validation — `mkdocs build --strict` passes, `verify_controls.py` 62/62, `verify_language_rules.py` 0 violations after all framework changes

## Out of Scope

| Item | Reason |
|------|--------|
| Power BI dashboard alternative | Workbook is the deliverable; Power BI pipeline documented in Control 3.2 already |
| Real-time streaming telemetry | Batch/daily Application Insights queries sufficient for governance reporting |
| Token-level cost tracking | Copilot Studio does not expose per-call token data |
| Custom telemetry SDK implementation | Workbook consumes existing Application Insights data; custom instrumentation is org-specific |
| Third-party observability platforms | Microsoft-native stack only per framework constraints |

## Traceability

| Requirement | Milestone Goal |
|-------------|---------------|
| TEL-01, TEL-02 | Understand available telemetry to build accurate workbook |
| WBK-01, WBK-02, WBK-03, WBK-04 | Deployable workbook template with 3 tabs |
| DEP-01, DEP-02 | Enterprise deployment with RBAC solving ALM gap |
| FRM-01, FRM-02, FRM-03 | Framework integration keeping controls and catalog current |
| VAL-01 | Quality gate ensuring no regressions |

---
*Requirements defined: 2026-02-11*
*Source: Deferred v13 todo — Agent Usage & Performance Workbook for Enterprise ALM*
