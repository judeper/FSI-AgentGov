---
created: 2026-02-05T10:30
title: Create agent-observability-foundation solution
area: tooling
files:
  - agent-observability-foundation/README.md
  - agent-observability-foundation/architecture.md
  - agent-observability-foundation/prerequisites.md
  - agent-observability-foundation/governance-mapping.md
  - agent-observability-foundation/validation-checklist.md
  - docs/framework/solutions-integration.md
  - docs/reference/solutions-index.md
---

## Problem

The FSI-AgentGov framework lacks a comprehensive observability solution for Microsoft 365 Copilot Studio agents. Financial services organizations need production-ready monitoring, alerting, and compliance audit capabilities that integrate with Azure Application Insights, Power BI, and Viva Insights while meeting regulatory requirements (SR 11-7, GDPR Art 22, SOX).

Currently the framework has 13 solutions in FSI-AgentGov-Solutions but no unified observability foundation covering:
- Agent usage analytics and adoption metrics
- Error tracking and failure correlation with Power Automate
- Latency distribution and SLA monitoring
- Deep reasoning / AI token cost tracking
- Regulatory audit trails for agent decisions
- Executive reporting via Power BI and Viva Insights

## Solution

Create `agent-observability-foundation/` solution with 7 phases:

**Phase 1 — Foundation Structure:**
- Directory tree: `application-insights/{kql,workbooks,alerts}`, `power-bi/dax`, `viva-insights/`, `compliance-audit/regulatory-mapping/`, `deployment/`
- Core docs: README.md, architecture.md, prerequisites.md, governance-mapping.md

**Phase 2 — Core Documentation:**
- README with architecture overview, compliance mapping table, quick start
- Architecture with Mermaid data flow diagrams, SoD boundaries, data retention, PII handling
- Prerequisites with Azure AD roles, Power BI licensing, data residency, private link

**Phase 3 — Application Insights (KQL, Workbooks, Alerts):**
- 6 KQL queries: agent-usage, agent-errors, latency-distribution, deep-reasoning-usage, flow-failure-correlation, agent-decision-audit
- 3 Workbook JSON templates: operational-health, enterprise-usage-overview, error-diagnostics
- 3 Alert templates: high-failure-rate (>5%), abnormal-token-usage, latency-regression

**Phase 4 — Power BI:**
- Semantic model documentation (star schema, RLS, relationships)
- 3 DAX measure files: sessions, avg-latency, error-rate
- Sample dashboard placeholder

**Phase 5 — Viva Insights:**
- Scope and limitations documentation
- Mapping to agent metrics cross-reference
- Executive reporting guidance

**Phase 6 — Governance & Compliance:**
- Governance mapping to existing 62-control framework
- SR 11-7 model risk KQL queries
- GDPR Article 22 automated decision tracking KQL
- SOX controls tracking documentation

**Phase 7 — Deployment & Validation:**
- deploy-workbooks.ps1 (Azure CLI, idempotent)
- deploy-alerts.ps1 (alert rules + action groups)
- validation-checklist.md (pre/post deployment)

### Requirements:
- FSI-compliant: SoD, audit trails, data residency
- Production-ready with proper error handling
- Data classification headers on all files
- Cross-references between artifacts (workbooks → KQL queries)
- Consistent with existing FSI-AgentGov patterns (#Requires, try-catch, etc.)

### Location decision:
- TBD: Could live in FSI-AgentGov-Solutions (alongside other solutions) or as a new advanced implementation in FSI-AgentGov docs. Recommend FSI-AgentGov-Solutions for consistency with existing 13 solutions.
