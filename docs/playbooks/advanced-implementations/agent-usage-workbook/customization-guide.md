# Agent Usage & Performance Workbook — Customization Guide

[Playbooks](../../index.md) > Advanced Implementations > [Agent Usage & Performance Workbook](index.md) > Customization Guide

**Status:** February 2026 — FSI-AgentGov v1.2.51
**Related Controls:** 3.1, 3.2, 3.3, 3.7, 3.8

---

## Overview

This guide explains how to extend and customize the Agent Usage & Performance Workbook for organization-specific requirements. It covers threshold tuning, adding custom KQL panels and tabs, and integrating organization-specific KPIs.

**Prerequisites:**

- Workbook deployed per the [Deployment Guide](deployment-guide.md)
- Familiarity with Azure Monitor Workbooks and KQL
- Log Analytics Contributor or higher on the target workspace

!!! warning "Back Up Before Editing"
    Always export the current workbook JSON before making changes. Use the Azure Portal **Advanced Editor** to download the JSON template, and test modifications in a draft (private) workbook before applying to the shared version.

---

## Workbook Structure Reference

### Item Types

| Type | Count | Purpose |
|------|-------|---------|
| Type 1 (Markdown) | 4 | Section headers, estimation caveats, requirement notes |
| Type 3 (KQL Query) | 23 | Data visualizations (Q01–Q23) |
| Type 9 (Parameters) | 1 | Global filter parameters (5 parameters) |
| Type 11 (Tab Links) | 1 | Tab navigation (3 tabs) |
| Type 12 (Groups) | 3 | Tab content containers with `conditionalVisibility` |

### Tab Architecture

| Tab | Label | Queries | Notes |
|-----|-------|---------|-------|
| 1 | Usage & Business Value | Q01–Q08 | Adoption, engagement, ROI |
| 2 | Performance & Errors | Q09–Q16 | Q15 splits into Q15a/Q15b |
| 3 | Operational Health | Q17–Q23 | Q22 splits into Q22a/Q22b |

### Parameter Flow

| Parameter | Type | Behavior |
|-----------|------|----------|
| `TimeRange` | 4 (time picker) | All queries reference via `timeContextFromParameter` |
| `AgentFilter` | 2 (KQL drop-down) | Multi-select, populated from `customDimensions.recipientName` |
| `ChannelFilter` | 2 (KQL drop-down) | Multi-select, populated from `customDimensions.channelId` |
| `MinutesSaved` | 1 (text input) | Numeric — used in Q08 business value calculation |
| `HourlyRate` | 1 (text input) | Numeric — used in Q08 cost avoidance estimation |

---

## Adjusting Zone-Specific Thresholds

Six queries include conditional formatting thresholds. The workbook ships with **Zone 3 (Enterprise Managed)** defaults.

### Current Defaults (Zone 3 — Enterprise Managed)

| Metric | Green | Amber | Red | Query |
|--------|-------|-------|-----|-------|
| Resolution Rate | ≥ 80% | ≥ 60% | < 60% | Q06 |
| Connector Success Rate | ≥ 95% | ≥ 90% | < 90% | Q12 |
| Topic Completion Rate | ≥ 80% | ≥ 60% | < 60% | Q14 |
| GenAI Quality (inverted) | < 15% fallback | < 25% | ≥ 25% | Q20 |
| Dependency Health | ≥ 95% | ≥ 90% | < 90% | Q21 |
| Agent Health Summary | ≥ 80% | ≥ 60% | < 60% | Q23 |

### Recommended Thresholds by Zone

| Metric | Zone 1 (Personal) | Zone 2 (Team) | Zone 3 (Enterprise) |
|--------|-------------------|---------------|---------------------|
| Resolution Rate | ≥ 60% green | ≥ 70% green | ≥ 80% green |
| Connector Success | ≥ 85% green | ≥ 90% green | ≥ 95% green |
| Completion Rate | ≥ 60% green | ≥ 70% green | ≥ 80% green |
| GenAI Fallback | < 30% green | < 20% green | < 15% green |

!!! tip "Zone Selection"
    Match thresholds to the governance zone of the agents being monitored. If you monitor agents across multiple zones in a single workbook, consider creating separate workbook instances per zone to avoid misleading threshold alerts.

### Portal-Based Threshold Editing

1. Open the workbook in **Edit** mode in the Azure Portal.
2. Select the query tile or grid you want to modify (e.g., Q06 Resolution Rate).
3. Click the **Column Settings** button (grid visualizations) or **Tile Settings** (tile visualizations).
4. Navigate to **Custom Formatting** → **Thresholds**.
5. Adjust the operator, value, and representation (color) for each threshold row.
6. Click **Apply** and then **Done Editing** to save.

For tile visualizations (Q06, Q20), thresholds appear under **Tile Settings → Thresholds**. For table/grid visualizations (Q12, Q14, Q21, Q23), thresholds are in **Column Settings → Custom Formatting** for the relevant column.

### JSON-Based Threshold Editing

For tile visualizations (e.g., Q06 Resolution Rate), locate the `tileSettings.thresholds` array:

```json
"tileSettings": {
  "thresholds": [
    { "operator": ">=", "value": 80, "representation": "green" },
    { "operator": ">=", "value": 60, "representation": "yellow" },
    { "operator": "Default", "representation": "red" }
  ]
}
```

For grid/table visualizations (e.g., Q12 Connector Success Rate), locate the `gridSettings.formatters[].formatOptions.thresholdsGrid` array:

```json
"gridSettings": {
  "formatters": [
    {
      "columnMatch": "SuccessRate",
      "formatter": 18,
      "formatOptions": {
        "thresholdsOptions": "icons",
        "thresholdsGrid": [
          { "operator": ">=", "thresholdValue": "95", "representation": "success", "text": "{0}{1}" },
          { "operator": ">=", "thresholdValue": "90", "representation": "warning", "text": "{0}{1}" },
          { "operator": "Default", "representation": "critical", "text": "{0}{1}" }
        ]
      }
    }
  ]
}
```

Adjust `value` / `thresholdValue` fields to match your target zone thresholds. The `representation` values map to: `green`/`success`, `yellow`/`warning`, `red`/`critical`.

---

## Adding Custom KQL Panels

### Query Template

Use the following JSON structure when adding new KQL query items. Continue numbering from Q24 onward.

```json
{
  "type": 3,
  "content": {
    "version": "KqlItem/1.0",
    "query": "// FINRA 4511: <regulatory justification>\n// <additional regulation>: <justification>\ncustomEvents\n| where timestamp {TimeRange}\n| where customDimensions.designMode == \"False\"\n| where customDimensions.recipientName in ({AgentFilter}) or '*' in ({AgentFilter})\n| where customDimensions.channelId in ({ChannelFilter}) or '*' in ({ChannelFilter})\n| <your query logic here>",
    "size": 0,
    "title": "<Panel Title>",
    "timeContext": {
      "durationMs": 86400000
    },
    "timeContextFromParameter": "TimeRange",
    "queryType": 0,
    "resourceType": "microsoft.insights/components",
    "visualization": "<timechart|barchart|tiles|table|piechart>"
  },
  "name": "query-Q24-<kebab-case-description>"
}
```

### Conventions

| Convention | Requirement |
|------------|-------------|
| **Query naming** | `query-QNN-kebab-case-description` — continue from Q24+ |
| **Time context** | Always set `timeContextFromParameter: "TimeRange"` |
| **Design mode filter** | Include `customDimensions.designMode == "False"` in all production queries |
| **Agent filter** | Include `where customDimensions.recipientName in ({AgentFilter}) or '*' in ({AgentFilter})` |
| **Channel filter** | Include when the query involves channel-specific data |
| **Regulatory comments** | Prefix each query with `// <REGULATION>: <justification>` comments |

!!! note "Filter Pattern"
    The `or '*' in ({AgentFilter})` pattern handles the "All" selection from the parameter drop-down. Omitting it causes queries to return no results when users select the default "All" option.

### Visualization Types

| Type | Use When | Example Queries |
|------|----------|-----------------|
| `timechart` | Trends over time | Q01, Q02, Q09 |
| `barchart` | Categorical comparisons | Q05, Q11 |
| `tiles` | Single KPI values | Q03, Q06, Q08 |
| `table` | Detailed row-level data | Q12, Q14, Q21 |
| `piechart` | Distribution breakdowns | Q04 |
| `areachart` | Volume trends with fill | Q01, Q16 |

---

## Adding New Tabs

### Step 1 — Add Tab Link

In the type 11 (tab-selector) item, add a new entry to the `links` array:

```json
{
  "id": "<new-guid>",
  "cellValue": "4",
  "linkTarget": "parameter",
  "linkLabel": "Custom Tab Name",
  "subTarget": "selectedTab",
  "style": "link"
}
```

Use the next sequential `cellValue` (the existing tabs use `"1"`, `"2"`, `"3"`).

### Step 2 — Add Group Container

Create a new type 12 group with `conditionalVisibility` matching the tab's `cellValue`:

```json
{
  "type": 12,
  "content": {
    "version": "NotebookGroup/1.0",
    "groupType": 0,
    "items": [
      // Insert your type 3 query items here
    ]
  },
  "conditionalVisibility": {
    "parameterName": "selectedTab",
    "comparison": "isEqualTo",
    "value": "4"
  },
  "name": "tab-custom-name"
}
```

### Step 3 — Insert in Items Array

Place the new group object in the top-level `items` array after the last tab group (`tab-operational-health`) and before `fallbackResourceIds`.

!!! warning "Item Order Matters"
    Workbook items render in array order. Placing a group outside the correct position may cause rendering issues or break the tab visibility logic.

---

## Integrating Organization-Specific KPIs

### CSAT Scores

If your agents log customer satisfaction via a custom event, surface the data using:

```kql
// SOX 302: Customer outcome measurement
// FINRA 4511: Agent effectiveness — satisfaction tracking
customEvents
| where timestamp {TimeRange}
| where customDimensions.designMode == "False"
| where customDimensions.recipientName in ({AgentFilter}) or '*' in ({AgentFilter})
| where name == "CustomerSatisfaction"
| summarize
    AvgScore = round(avg(toreal(customDimensions.score)), 2),
    Responses = count()
    by bin(timestamp, 1d)
| render timechart
```

!!! note "Custom Telemetry Required"
    CSAT tracking requires your agent topics to emit a custom event named `CustomerSatisfaction` with a `score` property in `customDimensions`. This is not part of default Copilot Studio telemetry.

### SLA Compliance Tracking

Extend the Q09 latency query with SLA threshold lines by adding a parameter-driven target:

```kql
// OCC 2011-12: SLA compliance monitoring
let SLATargetMs = 5000;  // Adjust to your SLA target
customEvents
| where timestamp {TimeRange}
| where customDimensions.designMode == "False"
| where name in ("BotMessageReceived", "BotMessageSend")
| extend sessionId = tostring(customDimensions.session_Id)
| order by sessionId, timestamp asc
| serialize
| extend prevEvent = prev(name), prevTimestamp = prev(timestamp),
    prevSession = prev(tostring(customDimensions.session_Id))
| where name == "BotMessageSend" and prevEvent == "BotMessageReceived"
    and sessionId == prevSession
| extend latencyMs = datetime_diff('millisecond', timestamp, prevTimestamp)
| where latencyMs > 0 and latencyMs < 120000
| summarize P95 = percentile(latencyMs, 95), SLATarget = SLATargetMs
    by bin(timestamp, 5m)
| render timechart
```

### Cost Per Conversation

Add a parameter-driven cost calculation tile, similar to Q08's approach:

```kql
// SOX 302: Cost efficiency reporting
let CostPerSession = 0.12;  // Estimated cost per agent session
customEvents
| where timestamp {TimeRange}
| where customDimensions.designMode == "False"
| where customDimensions.recipientName in ({AgentFilter}) or '*' in ({AgentFilter})
| extend sessionId = tostring(customDimensions.session_Id)
| summarize TotalSessions = dcount(sessionId)
| extend EstimatedCost = round(TotalSessions * CostPerSession, 2)
```

Consider adding `CostPerSession` as a workbook parameter (type 1) for runtime flexibility, following the pattern of `MinutesSaved` and `HourlyRate`.

### Regulatory Escalation Tracking

Track escalation patterns by filtering for escalation-related topic names:

```kql
// FINRA 3110: Supervisory escalation tracking
// SOX 404: Control effectiveness — escalation pattern analysis
customEvents
| where timestamp {TimeRange}
| where customDimensions.designMode == "False"
| where customDimensions.recipientName in ({AgentFilter}) or '*' in ({AgentFilter})
| where name == "TopicStart"
| extend topicName = tostring(customDimensions.TopicName)
| where topicName has_any ("Escalate", "Transfer", "Handoff", "Compliance", "Regulatory")
| summarize EscalationCount = count() by topicName, bin(timestamp, 1d)
| render barchart
```

!!! tip "Topic Naming Taxonomy"
    Establish a consistent naming convention for escalation-related topics across all agents (e.g., prefix with `Escalate-` or `Compliance-`). This simplifies KQL filtering and supports consistent reporting.

---

## JSON Editing Best Practices

1. **Use the Advanced Editor** in the Azure Portal for syntax validation — avoid editing the raw `.json` file directly unless importing a fresh template.
2. **Export a backup** of the current workbook JSON before making changes.
3. **Test in a draft workbook** — save changes as a private workbook first, validate, then promote to shared.
4. **Validate JSON syntax** after each edit — a misplaced comma or bracket breaks the entire workbook.
5. **Maintain regulatory comments** (`// FINRA 4511: ...`) in all KQL queries to support audit traceability.
6. **Keep the `designMode` filter** (`customDimensions.designMode == "False"`) in all production queries to exclude test/design-time data.
7. **Preserve `timeContextFromParameter`** — removing it decouples the query from the global time picker.

!!! warning "Avoid Direct File Edits for Production"
    The `agent-observability-foundation/src/agent-usage-workbook.json` template in the [FSI-AgentGov-Solutions](https://github.com/judeper/FSI-AgentGov-Solutions) repository is the deployment baseline. For production customizations, use the Azure Portal workbook editor or import the template into a new workbook instance. Direct file edits should be limited to version-controlled template updates.

---

## Additional Resources

- [Azure Monitor Workbooks documentation](https://learn.microsoft.com/azure/azure-monitor/visualize/workbooks-overview)
- [KQL reference](https://learn.microsoft.com/en-us/kusto/query/?view=azure-data-explorer&preserve-view=true)
- [Telemetry Schema Reference](telemetry-schema.md)
- [Deployment Guide](deployment-guide.md)
- [Control 3.1 — Agent Inventory and Metadata Management](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md)
- [Control 3.2 — Usage Analytics and Activity Monitoring](../../../controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md)

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
