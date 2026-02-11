# Todo: Agent Usage & Performance Workbook for Enterprise ALM Scenarios

**Created:** 2026-02-11
**Source:** User request — need custom Azure Monitor Workbooks to monitor Copilot Studio agents deployed to SharePoint and Teams, with usage data for business value reporting to leadership, plus performance/error metrics. Production Analytics tab inaccessible due to separation of duties and ALM.
**Priority:** high

## Description

Build a deployable Azure Monitor Workbook (JSON template) that gives enterprise teams read-only visibility into Copilot Studio agent performance, usage, and errors — without requiring access to the Copilot Studio Analytics tab in production. The workbook should be shareable via RBAC-scoped Application Insights access.

### What Already Exists

The framework has strong conceptual coverage but **no pre-built workbook template**:

| Existing Asset | What It Covers | Gap |
|---|---|---|
| **Control 3.2** (Usage Analytics) | PPAC Monitor dashboards, custom Power BI pipeline (Dataverse → Synapse → Power BI), Agent 365 Observability SDK | Assumes portal access; pipeline is "optional scale-up", not framed as ALM solution |
| **Control 3.9** (Sentinel Integration) | Sentinel workbook sections (Overview, Activity Timeline, Anomalies, DLP Events) | Manual creation only — no deployable JSON template |
| **Control 2.9** (Performance Monitoring) | KPIs, anomaly detection, RAI telemetry via custom App Insights events | Requires custom implementation; no out-of-box template |
| **Control 3.8** (Copilot Hub) | Chat Active Users, Assisted Hours, Satisfaction Rate | Native M365 Admin Center — limited customization, requires portal access |
| **Control 3.5** (Cost Allocation) | Budget tracking, cost dashboards | No business value quantification (ROI, time saved) |
| **Deny Event Correlation Report** (Solution) | Power BI for deny events + RAI filtering from App Insights | Scoped to deny/block events only |
| **Compliance Dashboard** (Solution) | 62-control compliance scoring via Power BI | Compliance posture, not usage/performance |
| **Microsoft Audit Reporting Tools** (Playbook) | AI-in-One Dashboard, PAX | Power BI templates, not Azure Monitor Workbooks |

### What Needs to Be Built

An Azure Monitor Workbook template sourced from **Application Insights** (where Copilot Studio can send telemetry) covering:

**Usage / Business Value Tab:**
- Session counts, unique users (DAU/MAU), conversation volume trends
- Channel breakdown (SharePoint vs. Teams vs. other)
- Resolution/escalation rates, average session duration
- "Assisted Hours" equivalent for leadership reporting
- Business value estimation metrics (time saved, interactions handled)

**Performance / Errors Tab:**
- Response latency (p50, p95, p99)
- Error rates by type (topic failure, API call failure, knowledge source timeout)
- Agent action/connector call success rates
- RAI content filtering trigger rates

**Operational Health Tab:**
- Anomaly detection indicators
- Availability / uptime trends
- Hallucination/grounding issue indicators (if custom telemetry enabled)
- DLP policy match events

### Why This Is Needed

In enterprise FSI organizations with ALM (dev → test → prod), **separation of duties** (Control 2.8) means makers/developers do not have access to the production Copilot Studio environment. The built-in Analytics tab is therefore invisible to the people who need it. An Azure Monitor Workbook with RBAC-scoped read access to a shared Application Insights resource solves this cleanly.

## Context

- User needs to report agent business value to senior leadership
- Production environment uses ALM with separation of duties — makers can't access Analytics tab
- Agent is deployed to both SharePoint and Teams channels
- Existing solutions (DEC Report, Compliance Dashboard) use Power BI but don't cover usage/performance
- Application Insights integration is already documented in controls 3.2, 3.9, 2.9 but no deployable template exists
- The companion repo (FSI-AgentGov-Solutions) is the natural home for the workbook template

## Acceptance Criteria

- [ ] Confirm Application Insights telemetry fields available from Copilot Studio (customEvents schema, customDimensions properties including channel info)
- [ ] Design workbook with 3 tabs: Usage/Business Value, Performance/Errors, Operational Health
- [ ] Create deployable Azure Monitor Workbook JSON template
- [ ] Include KQL queries for each visualization panel
- [ ] Document RBAC configuration for read-only access (solving the ALM/separation of duties gap)
- [ ] Add channel-specific breakdowns (SharePoint vs. Teams)
- [ ] Include business value estimation metrics (sessions handled, time saved estimates)
- [ ] Create deployment playbook (ARM template or manual import instructions)
- [ ] Update controls 3.2, 3.9, 2.9 to reference the new workbook solution
- [ ] Add workbook to solutions-index.md in the framework
- [ ] Validate with `mkdocs build --strict` after documentation updates
