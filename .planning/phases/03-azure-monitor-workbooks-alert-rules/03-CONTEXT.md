# Phase 3: Azure Monitor Workbooks & Alert Rules - Context

**Gathered:** 2026-02-05
**Status:** Ready for planning

<domain>
## Phase Boundary

Create Azure Monitor Workbooks for real-time dashboards and Alert Rules for proactive monitoring of Copilot Studio and Agent 365 SDK agents. Operations teams can visualize agent health and receive notifications when issues occur. Workbooks consume KQL queries from Phase 2. Power BI executive dashboards are Phase 4.

</domain>

<decisions>
## Implementation Decisions

### Workbook layout & navigation
- **Separate workbooks** — 3 workbooks (Operational Health, Error Diagnostics, Usage Overview) for cleaner RBAC and faster load
- **Full drill-down** — Click metric to navigate: summary → agent → session → event level
- **24-hour default** — Time range picker defaults to last 24 hours for daily ops monitoring
- **Zone parameter at top** — Global zone dropdown (Zone 1/2/3) filters all visualizations to match framework governance zones

### Alert thresholds & tuning
- **Dynamic thresholds** — Azure Monitor learns normal patterns, alerts on deviations to reduce false positives
- **Per-zone thresholds** — Zone 3 (Enterprise) stricter than Zone 1 (Personal) to match risk profile
- **3 severity levels** — Critical (immediate action), Warning (investigate soon), Info (awareness)
- **Runbook links in alerts** — Alert payload includes link to troubleshooting playbook for faster MTTR

### Notification routing
- **Teams and email** — Teams for real-time collaboration, email for audit trail (both channels)
- **Zone-based routing** — Zone 3 alerts → enterprise-ops channel, Zone 1 → general channel to match ownership
- **PagerDuty/ServiceNow docs** — Document webhook integration for enterprise ITSM escalation (customer configures)
- **Templates and docs** — ARM templates with placeholder URLs plus documentation for understanding

### Deployment approach
- **ARM templates** — JSON ARM templates for widest compatibility (Azure native)
- **Modular deployment** — Separate templates per workbook/alert so customers deploy what they need
- **Parameter files per environment** — dev.parameters.json, prod.parameters.json pattern
- **Fully idempotent** — Re-running updates existing resources, safe for CI/CD pipelines

### Claude's Discretion
- Exact workbook tab structure within each workbook
- KQL query optimization for workbook performance
- Alert rule naming conventions
- Parameter file schema design

</decisions>

<specifics>
## Specific Ideas

- Workbooks should leverage the KQL queries already created in Phase 2 (14 production queries)
- Zone filtering should use the same zone definitions as the governance framework (Personal Productivity, Team Collaboration, Enterprise Managed)
- Alert runbook links should point to troubleshooting.md playbooks in the FSI-AgentGov documentation
- Dynamic thresholds require ~14 days of baseline data before becoming effective (document this)

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 03-azure-monitor-workbooks-alert-rules*
*Context gathered: 2026-02-05*
