# Application Insights RAI Telemetry

**Parent:** [Deny Event Correlation Report](index.md)

---

## Overview

Copilot Studio agents can be configured to send telemetry to Azure Application Insights, including Responsible AI (RAI) content filtering events. This guide covers setup and extraction of these events for correlation with Purview audit data.

---

## Why RAI Telemetry Matters

RAI content filtering occurs at the **Azure AI Content Safety** layer, which is separate from Microsoft Purview governance. Key differences:

| Aspect | Purview Audit | Application Insights RAI |
|--------|---------------|-------------------------|
| **What it captures** | Resource access, policy enforcement | Model response filtering |
| **When it triggers** | Data governance violations | Content safety violations |
| **Event type** | CopilotInteraction, DlpRuleMatch | ContentFiltered custom event |
| **Configuration** | Tenant-wide (automatic) | Per-agent (manual setup) |

Organizations need **both sources** for complete deny event visibility.

---

## Application Insights Setup

### Prerequisites

- Azure subscription
- Application Insights resource (or create new)
- Copilot Studio Premium license
- Agent editing permissions

### Step 1: Create or Identify Application Insights Resource

1. Navigate to **Azure Portal** > **Application Insights**
2. Create new resource or use existing
3. Copy the **Connection String** from the Overview blade

!!! note "Resource Per Environment"
    Consider separate Application Insights resources for Dev/Test vs. Production to isolate telemetry.

### Step 2: Configure Each Copilot Studio Agent

1. Open **Copilot Studio** > Select agent
2. Go to **Settings** > **Generative AI**
3. Enable **Advanced settings** toggle
4. Under **Application Insights**, paste connection string
5. Click **Save** and **Publish**

!!! warning "Per-Agent Requirement"
    This configuration must be repeated for each Copilot Studio agent. There is no tenant-wide setting. Include this in Zone 2/3 agent onboarding checklists.

### Step 3: Verify Telemetry Flow

After configuration, test by sending a message to the agent, then verify in Application Insights:

```kql
customEvents
| where timestamp > ago(1h)
| where name == "MicrosoftCopilotStudio"
| take 10
```

---

## RAI Event Schema

### ContentFiltered Event

When Azure AI Content Safety blocks a response, the event includes:

```json
{
  "name": "MicrosoftCopilotStudio",
  "timestamp": "2026-01-26T10:30:00Z",
  "customDimensions": {
    "EventType": "ContentFiltered",
    "BotId": "agent-guid",
    "ConversationId": "session-guid",
    "FilterReason": "Hate/Harassment",
    "FilterCategory": "Hate",
    "FilterSeverity": "Medium",
    "TurnId": "turn-guid"
  }
}
```

### Filter Categories

| Category | Description | FSI Relevance |
|----------|-------------|---------------|
| **Hate** | Hate speech or harassment | Brand protection |
| **Violence** | Violent content | Inappropriate responses |
| **SelfHarm** | Self-harm content | Duty of care |
| **Sexual** | Sexual content | Inappropriate responses |
| **Jailbreak** | Prompt manipulation attempt | Security incident |

---

## KQL Queries

### Daily ContentFiltered Events

```kql
// All content filtering events in last 24 hours
customEvents
| where timestamp > ago(24h)
| where name == "MicrosoftCopilotStudio"
| extend eventType = tostring(customDimensions["EventType"])
| where eventType == "ContentFiltered"
| extend
    agentId = tostring(customDimensions["BotId"]),
    sessionId = tostring(customDimensions["ConversationId"]),
    filterReason = tostring(customDimensions["FilterReason"]),
    filterCategory = tostring(customDimensions["FilterCategory"]),
    filterSeverity = tostring(customDimensions["FilterSeverity"])
| project timestamp, agentId, sessionId, filterReason, filterCategory, filterSeverity
| order by timestamp desc
```

### Summary by Agent and Category

```kql
// Daily summary of filtering by agent and category
customEvents
| where timestamp > ago(24h)
| where name == "MicrosoftCopilotStudio"
| extend eventType = tostring(customDimensions["EventType"])
| where eventType == "ContentFiltered"
| extend
    agentId = tostring(customDimensions["BotId"]),
    filterCategory = tostring(customDimensions["FilterCategory"])
| summarize FilterCount = count() by agentId, filterCategory
| order by FilterCount desc
```

### High-Severity Events Alert Query

```kql
// High-severity events for alerting (last 15 minutes)
customEvents
| where timestamp > ago(15m)
| where name == "MicrosoftCopilotStudio"
| extend eventType = tostring(customDimensions["EventType"])
| where eventType == "ContentFiltered"
| extend filterSeverity = tostring(customDimensions["FilterSeverity"])
| where filterSeverity == "High"
| project timestamp,
    agentId = tostring(customDimensions["BotId"]),
    filterReason = tostring(customDimensions["FilterReason"])
```

---

## PowerShell Extraction via REST API

### Export-RaiTelemetry.ps1

```powershell
<#
.SYNOPSIS
    Exports RAI telemetry from Application Insights
.PARAMETER AppInsightsAppId
    Application Insights Application ID
.PARAMETER ApiKey
    Application Insights API key (read access)
.PARAMETER StartDate
    Start of time window
.PARAMETER OutputPath
    Path for CSV export
#>
param(
    [Parameter(Mandatory)]
    [string]$AppInsightsAppId,

    [Parameter(Mandatory)]
    [string]$ApiKey,

    [DateTime]$StartDate = (Get-Date).AddDays(-1),
    [DateTime]$EndDate = (Get-Date),
    [string]$OutputPath = ".\RaiTelemetry-$(Get-Date -Format 'yyyy-MM-dd').csv"
)

$headers = @{
    "x-api-key" = $ApiKey
}

# KQL query (URL encoded)
$query = @"
customEvents
| where timestamp between(datetime('$($StartDate.ToString("yyyy-MM-dd"))') .. datetime('$($EndDate.ToString("yyyy-MM-dd"))'))
| where name == "MicrosoftCopilotStudio"
| extend eventType = tostring(customDimensions["EventType"])
| where eventType == "ContentFiltered"
| extend
    agentId = tostring(customDimensions["BotId"]),
    sessionId = tostring(customDimensions["ConversationId"]),
    filterReason = tostring(customDimensions["FilterReason"]),
    filterCategory = tostring(customDimensions["FilterCategory"]),
    filterSeverity = tostring(customDimensions["FilterSeverity"])
| project timestamp, agentId, sessionId, filterReason, filterCategory, filterSeverity
"@

$encodedQuery = [System.Web.HttpUtility]::UrlEncode($query)
$uri = "https://api.applicationinsights.io/v1/apps/$AppInsightsAppId/query?query=$encodedQuery"

Write-Host "Querying Application Insights..."

try {
    $response = Invoke-RestMethod -Uri $uri -Headers $headers -Method Get

    # Convert response to objects
    $columns = $response.tables[0].columns.name
    $rows = $response.tables[0].rows

    $results = foreach ($row in $rows) {
        $obj = @{}
        for ($i = 0; $i -lt $columns.Count; $i++) {
            $obj[$columns[$i]] = $row[$i]
        }
        [PSCustomObject]$obj
    }

    Write-Host "RAI events found: $($results.Count)"

    $results | Export-Csv -Path $OutputPath -NoTypeInformation
    Write-Host "Exported to: $OutputPath"
}
catch {
    Write-Error "Failed to query Application Insights: $_"
}
```

---

## Correlation with Purview Events

RAI telemetry does not include `UserId` by default. Correlation requires:

### Option 1: Session-Based Correlation

If your agent passes user identity to conversation context:

```kql
customEvents
| where name == "MicrosoftCopilotStudio"
| extend
    eventType = tostring(customDimensions["EventType"]),
    userId = tostring(customDimensions["UserId"]) // If configured
| where isnotempty(userId)
```

### Option 2: Timestamp + Agent Correlation

Correlate by `AgentId` and timestamp window when direct user correlation isn't available:

1. Match `agentId` from RAI telemetry to `AgentId` from CopilotInteraction
2. Use ±2 minute timestamp window
3. Flag as "probable correlation" (not definitive)

---

## Zone Requirements

| Zone | RAI Telemetry Requirement | Alert Threshold |
|------|---------------------------|-----------------|
| **Zone 1** | Optional | N/A |
| **Zone 2** | Required | Daily report |
| **Zone 3** | Required | Real-time (15-min SLA) |

---

## Output Schema

The exported CSV includes:

| Column | Type | Description |
|--------|------|-------------|
| `timestamp` | DateTime | Event occurrence time (UTC) |
| `agentId` | String | Copilot Studio agent GUID |
| `sessionId` | String | Conversation session ID |
| `filterReason` | String | Why content was filtered |
| `filterCategory` | String | Hate, Violence, SelfHarm, Sexual, Jailbreak |
| `filterSeverity` | String | Low, Medium, High |

---

## Next Steps

- [Power BI Correlation](power-bi-correlation.md) - Build the correlation dashboard
- [Deployment Guide](deployment-guide.md) - End-to-end deployment

---

*FSI Agent Governance Framework v1.2 - January 2026*
