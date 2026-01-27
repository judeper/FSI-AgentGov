# Application Insights Workbooks for Agent Observability

> Part of [Agent 365 Observability Implementation Guide](index.md)

---

## Overview

This guide provides Azure Workbook templates for monitoring Agent 365 telemetry. These workbooks support Zone 2 and Zone 3 operational requirements for performance monitoring, compliance tracking, and incident investigation.

---

## Workbook Gallery

| Workbook | Purpose | Zone |
|----------|---------|------|
| Agent Performance Overview | Latency, success rates, throughput | Zone 2+ |
| Interaction Analytics | Usage patterns, topic analysis | Zone 2+ |
| Security & Compliance | RAI filters, DLP blocks, access denials | Zone 3 |
| Sponsor Accountability | Sponsor activity, attestation status | Zone 2+ |
| Incident Investigation | Correlation ID tracing | Zone 3 |

---

## Workbook 1: Agent Performance Overview

### Template

```json
{
  "version": "Notebook/1.0",
  "items": [
    {
      "type": 1,
      "content": {
        "json": "# Agent Performance Overview\n\nMonitor agent response times, success rates, and throughput across zones."
      }
    },
    {
      "type": 9,
      "content": {
        "version": "KqlParameterItem/1.0",
        "parameters": [
          {
            "name": "TimeRange",
            "type": 4,
            "defaultValue": {
              "durationMs": 86400000
            }
          },
          {
            "name": "Zone",
            "type": 2,
            "multiSelect": true,
            "query": "traces | distinct tostring(customDimensions.fsi_zone) | order by Column1 asc",
            "value": ["Zone2", "Zone3"]
          },
          {
            "name": "AgentName",
            "type": 2,
            "multiSelect": true,
            "query": "traces | distinct tostring(customDimensions.service_name) | order by Column1 asc"
          }
        ]
      }
    },
    {
      "type": 3,
      "content": {
        "version": "KqlItem/1.0",
        "query": "// Response Latency Trend\ntraces\n| where timestamp {TimeRange}\n| where customDimensions.fsi_zone in ({Zone})\n| where customDimensions.service_name in ({AgentName}) or '*' in ({AgentName})\n| extend latency = todouble(customDimensions.agent_response_latency_ms)\n| summarize\n    P50 = percentile(latency, 50),\n    P95 = percentile(latency, 95),\n    P99 = percentile(latency, 99)\n    by bin(timestamp, 5m)\n| render timechart",
        "size": 0,
        "title": "Response Latency (P50, P95, P99)"
      }
    },
    {
      "type": 3,
      "content": {
        "version": "KqlItem/1.0",
        "query": "// Success Rate by Agent\ntraces\n| where timestamp {TimeRange}\n| where customDimensions.fsi_zone in ({Zone})\n| extend\n    agentName = tostring(customDimensions.service_name),\n    success = customDimensions.agent_response_success == 'true'\n| summarize\n    Total = count(),\n    Successes = countif(success),\n    SuccessRate = round(100.0 * countif(success) / count(), 2)\n    by agentName\n| order by SuccessRate asc",
        "size": 0,
        "title": "Success Rate by Agent"
      }
    },
    {
      "type": 3,
      "content": {
        "version": "KqlItem/1.0",
        "query": "// Throughput Trend\ntraces\n| where timestamp {TimeRange}\n| where name == 'agent.interaction'\n| summarize Interactions = count() by bin(timestamp, 1h)\n| render areachart",
        "size": 0,
        "title": "Interaction Volume"
      }
    },
    {
      "type": 3,
      "content": {
        "version": "KqlItem/1.0",
        "query": "// Tool Call Performance\ntraces\n| where timestamp {TimeRange}\n| where name == 'tool.invocation'\n| extend\n    toolName = tostring(customDimensions.tool_name),\n    duration = todouble(customDimensions.tool_duration_ms),\n    success = customDimensions.tool_success == 'true'\n| summarize\n    Calls = count(),\n    AvgDuration = round(avg(duration), 1),\n    FailRate = round(100.0 * countif(not(success)) / count(), 2)\n    by toolName\n| order by Calls desc",
        "size": 0,
        "title": "Tool/Connector Performance"
      }
    }
  ]
}
```

### Deployment

```powershell
# Deploy Performance Overview workbook
$workbookParams = @{
    ResourceGroupName = "rg-agent-governance"
    Name = "agent-performance-overview"
    Location = "eastus"
    DisplayName = "Agent Performance Overview"
    SourceId = "/subscriptions/{sub}/resourceGroups/{rg}/providers/microsoft.insights/components/{appinsights}"
    Category = "workbook"
    SerializedData = (Get-Content -Path "workbook-performance.json" -Raw)
}
New-AzApplicationInsightsWorkbook @workbookParams
```

---

## Workbook 2: Interaction Analytics

### Template

```json
{
  "version": "Notebook/1.0",
  "items": [
    {
      "type": 1,
      "content": {
        "json": "# Agent Interaction Analytics\n\nAnalyze usage patterns, topic engagement, and user behavior."
      }
    },
    {
      "type": 3,
      "content": {
        "version": "KqlItem/1.0",
        "query": "// Top Topics by Engagement\ntraces\n| where timestamp {TimeRange}\n| where name == 'topic.triggered'\n| extend topicName = tostring(customDimensions.topic_name)\n| summarize Triggers = count() by topicName\n| top 10 by Triggers\n| render barchart",
        "size": 0,
        "title": "Top 10 Topics"
      }
    },
    {
      "type": 3,
      "content": {
        "version": "KqlItem/1.0",
        "query": "// Fallback Rate Trend\ntraces\n| where timestamp {TimeRange}\n| extend\n    isFallback = name == 'fallback.triggered',\n    isInteraction = name == 'agent.interaction'\n| summarize\n    Fallbacks = countif(isFallback),\n    Total = countif(isInteraction)\n    by bin(timestamp, 1h)\n| extend FallbackRate = round(100.0 * Fallbacks / Total, 2)\n| project timestamp, FallbackRate\n| render linechart",
        "size": 0,
        "title": "Fallback Rate Trend"
      }
    },
    {
      "type": 3,
      "content": {
        "version": "KqlItem/1.0",
        "query": "// Human Handoff Analysis\ntraces\n| where timestamp {TimeRange}\n| where name == 'agent.handoff'\n| extend\n    reason = tostring(customDimensions.handoff_reason),\n    agentName = tostring(customDimensions.service_name)\n| summarize Handoffs = count() by reason, agentName\n| order by Handoffs desc",
        "size": 0,
        "title": "Human Handoff Reasons"
      }
    },
    {
      "type": 3,
      "content": {
        "version": "KqlItem/1.0",
        "query": "// Usage by Time of Day\ntraces\n| where timestamp {TimeRange}\n| where name == 'agent.interaction'\n| extend hour = datetime_part('hour', timestamp)\n| summarize Interactions = count() by hour\n| order by hour asc\n| render columnchart",
        "size": 0,
        "title": "Usage Distribution by Hour"
      }
    },
    {
      "type": 3,
      "content": {
        "version": "KqlItem/1.0",
        "query": "// Active Users Trend\ntraces\n| where timestamp {TimeRange}\n| where name == 'agent.interaction'\n| extend userId = tostring(customDimensions.user_id)\n| summarize DailyActiveUsers = dcount(userId) by bin(timestamp, 1d)\n| render linechart",
        "size": 0,
        "title": "Daily Active Users"
      }
    }
  ]
}
```

---

## Workbook 3: Security & Compliance

### Template (Zone 3 Required)

```json
{
  "version": "Notebook/1.0",
  "items": [
    {
      "type": 1,
      "content": {
        "json": "# Security & Compliance Dashboard\n\n⚠️ **Zone 3 Only** - Contains sensitive security event data"
      }
    },
    {
      "type": 3,
      "content": {
        "version": "KqlItem/1.0",
        "query": "// RAI Filter Activations\ntraces\n| where timestamp {TimeRange}\n| where name == 'rai.filter'\n| extend\n    filterType = tostring(customDimensions.rai_filter_type),\n    action = tostring(customDimensions.rai_filter_action),\n    agentName = tostring(customDimensions.service_name)\n| summarize\n    Triggered = count(),\n    Blocked = countif(action == 'Block')\n    by filterType, agentName\n| order by Blocked desc",
        "size": 0,
        "title": "RAI Filter Summary"
      }
    },
    {
      "type": 3,
      "content": {
        "version": "KqlItem/1.0",
        "query": "// RAI Filter Trend\ntraces\n| where timestamp {TimeRange}\n| where name == 'rai.filter'\n| extend filterType = tostring(customDimensions.rai_filter_type)\n| summarize Count = count() by bin(timestamp, 1h), filterType\n| render timechart",
        "size": 0,
        "title": "RAI Filter Activity Trend"
      }
    },
    {
      "type": 3,
      "content": {
        "version": "KqlItem/1.0",
        "query": "// DLP Policy Blocks\ntraces\n| where timestamp {TimeRange}\n| where name == 'dlp.block'\n| extend\n    policyName = tostring(customDimensions.dlp_policy_name),\n    dataType = tostring(customDimensions.dlp_data_type),\n    agentName = tostring(customDimensions.service_name)\n| summarize Blocks = count() by policyName, dataType, agentName\n| order by Blocks desc",
        "size": 0,
        "title": "DLP Blocks by Policy"
      }
    },
    {
      "type": 3,
      "content": {
        "version": "KqlItem/1.0",
        "query": "// Access Denial Events\ntraces\n| where timestamp {TimeRange}\n| where name == 'access.denied'\n| extend\n    reason = tostring(customDimensions.denial_reason),\n    resource = tostring(customDimensions.target_resource),\n    userId = tostring(customDimensions.user_id)\n| summarize Denials = count() by reason, resource\n| order by Denials desc",
        "size": 0,
        "title": "Access Denials"
      }
    },
    {
      "type": 3,
      "content": {
        "version": "KqlItem/1.0",
        "query": "// Authentication Failures\ntraces\n| where timestamp {TimeRange}\n| where name == 'auth.failure'\n| extend\n    failureReason = tostring(customDimensions.failure_reason),\n    ipAddress = tostring(customDimensions.client_ip),\n    agentId = tostring(customDimensions.agent_id)\n| summarize Failures = count() by failureReason, agentId\n| order by Failures desc",
        "size": 0,
        "title": "Authentication Failures"
      }
    },
    {
      "type": 3,
      "content": {
        "version": "KqlItem/1.0",
        "query": "// Compliance Event Timeline\ntraces\n| where timestamp {TimeRange}\n| where name in ('rai.filter', 'dlp.block', 'access.denied', 'auth.failure')\n| project timestamp, EventType = name, Details = tostring(customDimensions)\n| order by timestamp desc\n| take 100",
        "size": 0,
        "title": "Recent Compliance Events"
      }
    }
  ]
}
```

---

## Workbook 4: Sponsor Accountability

### Template

```json
{
  "version": "Notebook/1.0",
  "items": [
    {
      "type": 1,
      "content": {
        "json": "# Sponsor Accountability Dashboard\n\nTrack sponsor activity and attestation compliance."
      }
    },
    {
      "type": 3,
      "content": {
        "version": "KqlItem/1.0",
        "query": "// Agents by Sponsor\ntraces\n| where timestamp > ago(1d)\n| where name == 'agent.interaction'\n| extend\n    sponsorId = tostring(customDimensions.sponsor_id),\n    agentName = tostring(customDimensions.service_name),\n    zone = tostring(customDimensions.fsi_zone)\n| summarize\n    Agents = dcount(agentName),\n    Interactions = count()\n    by sponsorId, zone\n| order by Agents desc",
        "size": 0,
        "title": "Agent Distribution by Sponsor"
      }
    },
    {
      "type": 3,
      "content": {
        "version": "KqlItem/1.0",
        "query": "// Attestation Status (requires custom dimension)\ntraces\n| where timestamp > ago(90d)\n| where name == 'sponsor.attestation'\n| extend\n    sponsorId = tostring(customDimensions.sponsor_id),\n    agentId = tostring(customDimensions.agent_id),\n    status = tostring(customDimensions.attestation_status),\n    attestationDate = todatetime(customDimensions.attestation_date)\n| summarize LastAttestation = max(attestationDate), Status = any(status) by sponsorId, agentId\n| extend DaysSince = datetime_diff('day', now(), LastAttestation)\n| order by DaysSince desc",
        "size": 0,
        "title": "Attestation Compliance"
      }
    },
    {
      "type": 3,
      "content": {
        "version": "KqlItem/1.0",
        "query": "// Sponsor Activity Summary\ntraces\n| where timestamp {TimeRange}\n| extend sponsorId = tostring(customDimensions.sponsor_id)\n| where isnotempty(sponsorId)\n| summarize\n    TotalInteractions = count(),\n    UniqueAgents = dcount(customDimensions.service_name),\n    UniqueUsers = dcount(customDimensions.user_id)\n    by sponsorId\n| order by TotalInteractions desc",
        "size": 0,
        "title": "Sponsor Activity Overview"
      }
    }
  ]
}
```

---

## Workbook 5: Incident Investigation

### Template

```json
{
  "version": "Notebook/1.0",
  "items": [
    {
      "type": 1,
      "content": {
        "json": "# Incident Investigation Workbook\n\nTrace complete interaction path using correlation ID."
      }
    },
    {
      "type": 9,
      "content": {
        "version": "KqlParameterItem/1.0",
        "parameters": [
          {
            "name": "CorrelationId",
            "type": 1,
            "description": "Enter correlation ID to trace"
          },
          {
            "name": "TimeRange",
            "type": 4,
            "defaultValue": {
              "durationMs": 86400000
            }
          }
        ]
      }
    },
    {
      "type": 3,
      "content": {
        "version": "KqlItem/1.0",
        "query": "// Complete Trace Path\ntraces\n| where timestamp {TimeRange}\n| where customDimensions.correlation_id == '{CorrelationId}' or operation_Id == '{CorrelationId}'\n| project\n    timestamp,\n    EventType = name,\n    Agent = tostring(customDimensions.service_name),\n    User = tostring(customDimensions.user_id),\n    Details = tostring(customDimensions)\n| order by timestamp asc",
        "size": 0,
        "title": "Event Timeline"
      }
    },
    {
      "type": 3,
      "content": {
        "version": "KqlItem/1.0",
        "query": "// Request Details\nrequests\n| where timestamp {TimeRange}\n| where operation_Id == '{CorrelationId}'\n| project\n    timestamp,\n    name,\n    url,\n    duration,\n    success,\n    resultCode,\n    performanceBucket",
        "size": 0,
        "title": "HTTP Requests"
      }
    },
    {
      "type": 3,
      "content": {
        "version": "KqlItem/1.0",
        "query": "// Dependencies Called\ndependencies\n| where timestamp {TimeRange}\n| where operation_Id == '{CorrelationId}'\n| project\n    timestamp,\n    name,\n    target,\n    type,\n    duration,\n    success,\n    resultCode",
        "size": 0,
        "title": "External Dependencies"
      }
    },
    {
      "type": 3,
      "content": {
        "version": "KqlItem/1.0",
        "query": "// Exceptions\nexceptions\n| where timestamp {TimeRange}\n| where operation_Id == '{CorrelationId}'\n| project\n    timestamp,\n    type,\n    method,\n    message,\n    outerMessage,\n    details",
        "size": 0,
        "title": "Exceptions"
      }
    }
  ]
}
```

---

## Deployment Script

Deploy all workbooks:

```powershell
# Deploy all Agent Observability workbooks
$workbooks = @(
    @{ Name = "agent-performance-overview"; DisplayName = "Agent Performance Overview" },
    @{ Name = "agent-interaction-analytics"; DisplayName = "Agent Interaction Analytics" },
    @{ Name = "agent-security-compliance"; DisplayName = "Agent Security & Compliance" },
    @{ Name = "agent-sponsor-accountability"; DisplayName = "Agent Sponsor Accountability" },
    @{ Name = "agent-incident-investigation"; DisplayName = "Agent Incident Investigation" }
)

$resourceGroup = "rg-agent-governance"
$appInsightsId = "/subscriptions/{sub}/resourceGroups/{rg}/providers/microsoft.insights/components/{ai}"

foreach ($wb in $workbooks) {
    $templatePath = "workbooks/$($wb.Name).json"

    if (Test-Path $templatePath) {
        New-AzApplicationInsightsWorkbook `
            -ResourceGroupName $resourceGroup `
            -Name $wb.Name `
            -Location "eastus" `
            -DisplayName $wb.DisplayName `
            -SourceId $appInsightsId `
            -Category "workbook" `
            -SerializedData (Get-Content -Path $templatePath -Raw)

        Write-Host "Deployed: $($wb.DisplayName)" -ForegroundColor Green
    } else {
        Write-Warning "Template not found: $templatePath"
    }
}
```

---

## Related Resources

- [Overview](index.md) - Observability architecture
- [OpenTelemetry Setup](opentelemetry-setup.md) - Collector configuration
- [Alerting Configuration](alerting-configuration.md) - Alert rules
- [Microsoft Learn: Azure Workbooks](https://learn.microsoft.com/en-us/azure/azure-monitor/visualize/workbooks-overview)

---

*FSI Agent Governance Framework v1.2.6 - January 2026*
