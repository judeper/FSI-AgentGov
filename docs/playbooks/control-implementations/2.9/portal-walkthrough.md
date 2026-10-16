# Portal Walkthrough: Control 2.9 - Agent Performance Monitoring and Optimization

**Last Updated:** October 2026 (navigation documentation review; tenant UI not tested)
**Portals:** Power Platform Admin Center (PPAC), Microsoft Copilot Studio, Azure Portal (Application Insights / Log Analytics), Power BI
**Estimated Time:** 4–6 hours for a full Zone 3 setup; ~90 min for Zone 1 baseline
**Audience:** M365 administrators in US financial services

---

## Prerequisites

- [ ] **Power Platform Admin** role (tenant analytics, environment selection, data export)
- [ ] **AI Administrator** role (per-agent analytics and Application Insights linkage in Copilot Studio)
- [ ] **Owner** or **Contributor** on the target Azure subscription (to create Application Insights / Log Analytics workspace)
- [ ] **Power BI Pro or PPU** license for any user authoring dashboards (Premium capacity recommended for Zone 3 datasets)
- [ ] KPI thresholds documented per zone and approved by AI Governance Lead and (for Zone 3) Model Risk Manager

---

## Step 1 — Review operational metrics (Power Platform Admin Center)

1. Open **[Power Platform Admin Center](https://admin.powerplatform.microsoft.com)**.
2. Navigate to **Monitor** → **Products** → **Copilot Studio**.
3. Confirm the metrics page renders for the intended environments. [Microsoft's procedure](https://learn.microsoft.com/en-us/power-platform/admin/monitoring/monitor-copilot-studio) requires tenant-level analytics; opening this page does not enable collection.
4. The documented preview metrics are **Agent session success rate** and **Recent agent sessions**. Do not treat this page as the per-agent CSAT or resolution dashboard.

**Evidence to capture:** the actual Monitor → Products → Copilot Studio metrics and environment context, including any empty-data or prerequisite message. Store the screenshot under `maintainers-local/tenant-evidence/2.9/` (gitignored).

---

## Step 2 — Review per-agent analytics in Copilot Studio

1. Open **[Microsoft Copilot Studio](https://copilotstudio.microsoft.com)**.
2. Select a standard-harness agent → **Monitor** on the top menu bar.
3. Review **Overview**, **Summary**, and **Savings**, then **Effectiveness** for conversation outcomes, reactions, and customer satisfaction. Use **Use** for themes, generated answer quality, tools, and knowledge sources.
4. For autonomous agents, follow the applicable health-monitoring procedure linked from the [Monitor overview](https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-overview), rather than assume a universal **Autonomous** pane.
5. For connected/child agents, review the documented **Agents** call-volume, success-rate, and status metrics where available; do not assume a **Hybrid analytics** enable switch. See [Monitor conversational agents](https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-improve-agent-effectiveness).

**FSI note:** Native CSAT only fires when the agent prompts for it. Confirm a satisfaction survey topic is published and routed at end-of-conversation, otherwise CSAT remains empty and supervisory reviews lack required evidence.

---

## Step 3 — Link Azure Application Insights to each Zone 2/3 agent

Application Insights provides enterprise-grade telemetry (full session traces, KQL-queryable events, alert rules, retention configurable to satisfy SEC 17a-4) that the built-in dashboards do not.

1. In the [Azure Portal](https://portal.azure.com), create or identify an **Application Insights** resource:
    - Region: same geography as your tenant data residency
    - Workspace-based (links to a Log Analytics workspace — required for KQL and alerts)
    - Retention: set to **at least 365 days** for Zone 2; **2 years archived to immutable storage** for Zone 3 to help meet SEC 17a-4(f)
2. Copy the **Connection string** (preferred) or **Instrumentation key**.
3. In Copilot Studio → agent → **Settings** → **Advanced** → **Application Insights**, paste the connection string and save.
4. Confirm telemetry begins flowing (allow 5–15 minutes; Application Insights has ingestion latency).
5. Repeat for every Zone 2 and Zone 3 agent. Maintain a mapping of `AgentName → ApplicationInsightsResourceId` in your governance inventory (linked to Control 3.1).

!!! note "WORM retention"
    Application Insights and Log Analytics retention alone is not WORM. For SEC 17a-4(f) compliance, configure a **continuous export** (Diagnostic Settings → Archive to storage account with **immutability policy** in **time-based retention** mode, locked) or use **Microsoft Purview Data Lifecycle Management** retention locks on the storage container.

---

## Step 4 — Configure Power Platform analytics export (Zone 2/3)

For dashboarding, longitudinal trend analysis, and cross-environment views.

1. PPAC → **Data integration** → **Self-service analytics**.
2. **+ New export**:
    - **Name:** `FSI-Agent-Analytics-Export`
    - **Destination:** Azure Data Lake Storage Gen2 (must be in the same region as your tenant)
    - **Tables:** select Copilot Studio analytics tables
    - **Frequency:** daily incremental
3. Save. The first export typically lands within 24 hours.
4. In Power BI, create workspace **`Agent-Performance-Analytics`** and connect to the ADLS Gen2 export via a Dataflow Gen2 or direct Azure Data Lake Storage Gen2 connector.

---

## Step 5 — Build the Power BI performance dashboard

Create one report per zone with these visuals (minimum):

| Visual | Source | Purpose |
|---|---|---|
| KPI cards: sessions / 24h, error rate, p95 response time, CSAT | Application Insights or ADLS export | Operational glance |
| Latency percentiles (p50 / p95 / p99) over 30 days | Application Insights `requests` / `customMetrics` | Fed SR 26-2 (formerly SR 11-7) performance trend |
| Error rate by agent (stacked) | Application Insights `exceptions` | Hotspot identification |
| Topic resolution & escalation funnel | ADLS export — topic table | Completion quality |
| CSAT distribution + trend | ADLS export — satisfaction table | Customer-impact signal |
| Generative answer source coverage | Copilot Studio Generative AI pane export | Grounding evidence |

Set workspace access to **AI Governance Lead**, **Operations Team**, **Agent Owners**, and (read-only) **Internal Audit**.

The pre-built [Agent Usage & Performance Workbook](../../advanced-implementations/agent-usage-workbook/index.md) contains a Power BI template you can import.

---

## Step 6 — Configure threshold alerting

### Built-in (Power Automate, all zones)

1. [Power Automate](https://make.powerautomate.com) → **My flows** → **Cloud flows** tab → **Create from blank** → **Add a trigger** → search for and select **Recurrence**. If your tenant still exposes **+ Create** → **Scheduled cloud flow**, verify that shortcut in your tenant before using it.
2. Name `FSI-Agent-Performance-Alert`, recurrence hourly (Zone 3) / daily (Zones 1–2).
3. Action: query the Power BI dataset or ADLS export for threshold breaches.
4. Conditions per zone:

| Zone | Error rate | p95 response time | CSAT floor |
|---|---|---|---|
| Zone 1 | > 5% | > 30 s | n/a |
| Zone 2 | > 2% | > 15 s | < 3.5 / 5 |
| Zone 3 | > 1% | > 5 s | < 4.0 / 5 |

5. Send Teams + email to the AI Governance distribution list. For Zone 3, escalate to Model Risk Manager and on-call CISO if breach persists > 30 minutes.

### Application Insights alert rules (Zone 2/3)

1. Azure Portal → Application Insights → **Alerts** → **Create** → **Alert rule**.
2. Signal: `requests/failed` count, `requests/duration` p95, custom metric `hallucinationRate` (if implemented).
3. Action group: include Teams webhook, ITSM connector (ServiceNow/Jira), and on-call paging (PagerDuty/Splunk OnCall).
4. **Smart Detection** (Azure Monitor) — enable for Zone 3 to catch anomalies the static thresholds miss.

---

## Step 7 — Establish review cadence and document it

| Review | Frequency | Attendees | Required evidence |
|---|---|---|---|
| Operational | Weekly (Zone 2/3); monthly (Zone 1) | Ops, Agent Owners | Alert log, top error topics, CSAT delta |
| Business | Monthly | AI Governance Lead, Stakeholders | KPI trend, ROI workbook, optimization backlog |
| Model risk | Quarterly (Zone 3) | Model Risk Manager, AI Governance Lead | Fed SR 26-2 (formerly SR 11-7) monitoring memo, hallucination/grounding metrics, drift analysis |
| Executive | Quarterly | Leadership, Compliance, Internal Audit | Cross-zone scorecard, regulatory posture, incidents |

Document the schedule in your supervisory procedures (FINRA Rule 3110) and store meeting minutes on WORM-capable SharePoint or Purview-retained storage.

---

## Configuration by Governance Level

| Setting | Baseline (Zone 1) | Recommended (Zone 2) | Regulated (Zone 3) |
|---|---|---|---|
| Native analytics | Enabled | Enabled + per-agent review | Enabled + Hybrid + Autonomous panes |
| Application Insights | Optional | Required | Required + custom RAI events |
| Analytics export | Optional | ADLS export daily | ADLS export + WORM archive |
| Dashboard | Summary | Per-agent detail | Real-time + drill-down + MRM tab |
| Alerting | Error rate only | Error + latency + CSAT | All metrics + Smart Detection + paging |
| Review cadence | Monthly | Weekly + monthly + quarterly | Daily + weekly + monthly + quarterly MRM |
| Telemetry retention | 30 days | 365 days | 2 years on WORM storage |

---

## Validation checklist

- [ ] PPAC → Monitor → Products → Copilot Studio renders the documented preview metrics
- [ ] Each Zone 2/3 agent shows a configured Application Insights resource ID
- [ ] ADLS export shows recent files
- [ ] Power BI workspace `Agent-Performance-Analytics` exists with at least one published report and a recent refresh
- [ ] At least one alert rule fires successfully against a temporarily lowered threshold
- [ ] Review cadence is documented in supervisory procedures with named attendees
- [ ] Evidence artifacts staged under `maintainers-local/tenant-evidence/2.9/` for the next examination

---

[Back to Control 2.9](../../../controls/pillar-2-management/2.9-agent-performance-monitoring-and-optimization.md) | [PowerShell Setup](powershell-setup.md) | [Verification & Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
