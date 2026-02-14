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

#### Azure Resources

- Azure subscription with an Application Insights resource (or permissions to create one)
- Copilot Studio Premium license
- Agent editing permissions in Copilot Studio

#### Entra ID Authentication (Required)

The following resources are required for automated telemetry extraction. API key (`x-api-key`) authentication is deprecated and will stop working on **March 31, 2026**.

| Prerequisite | Purpose |
|-------------|---------|
| **Entra ID App Registration** | Service principal for unattended authentication |
| **Monitoring Reader role** | Assigned to the App Registration on the Application Insights resource |
| **Azure Key Vault** | Stores the service principal client secret securely |
| **Az.Accounts 3.0+** | PowerShell module for `Connect-AzAccount` / `Get-AzAccessToken` |
| **Az.KeyVault 5.0+** | PowerShell module for `Get-AzKeyVaultSecret` |
| **PowerShell 7.0+** | Required runtime version |

??? note "Setting Up the App Registration"
    1. In **Entra ID** > **App registrations**, create a new registration (e.g., `sp-appinsights-rai`)
    2. Create a **Client secret** and store it in Azure Key Vault
    3. In the **Application Insights** resource, assign the **Monitoring Reader** role to the App Registration
    4. Record the **Tenant ID**, **Client ID**, **Key Vault name**, and **Secret name** for script parameters

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

### Entra ID Authentication (Current)

The `Export-RaiTelemetry.ps1` script authenticates using an Entra ID service principal with a bearer token. This is the supported method for automated Application Insights queries.

**Authentication flow:**

1. Retrieve client secret from Azure Key Vault
2. Authenticate service principal via `Connect-AzAccount`
3. Acquire bearer token via `Get-AzAccessToken`
4. Call Application Insights REST API with `Authorization: Bearer` header

### Export-RaiTelemetry.ps1

```powershell
#Requires -Version 7.0
#Requires -Modules @{ ModuleName="Az.Accounts"; ModuleVersion="3.0.0" }, @{ ModuleName="Az.KeyVault"; ModuleVersion="5.0.0" }

<#
.SYNOPSIS
    Exports RAI telemetry from Application Insights using Entra ID authentication.
.PARAMETER AppInsightsAppId
    Application Insights Application ID
.PARAMETER TenantId
    Entra ID tenant ID for service principal authentication
.PARAMETER ClientId
    App Registration (client) ID with Monitoring Reader role
.PARAMETER KeyVaultName
    Azure Key Vault containing the client secret
.PARAMETER SecretName
    Name of the Key Vault secret for the service principal
.PARAMETER DaysBack
    Number of days of telemetry to retrieve (default: 1)
.PARAMETER OutputPath
    Path for CSV export
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidateNotNullOrEmpty()]
    [string]$AppInsightsAppId,

    [Parameter(Mandatory)]
    [ValidateNotNullOrEmpty()]
    [string]$TenantId,

    [Parameter(Mandatory)]
    [ValidateNotNullOrEmpty()]
    [string]$ClientId,

    [Parameter(Mandatory)]
    [ValidateNotNullOrEmpty()]
    [string]$KeyVaultName,

    [Parameter(Mandatory)]
    [ValidateNotNullOrEmpty()]
    [string]$SecretName,

    [ValidateRange(1, 90)]
    [int]$DaysBack = 1,

    [ValidateNotNullOrEmpty()]
    [string]$OutputPath = ".\RaiTelemetry-$(Get-Date -Format 'yyyy-MM-dd').csv"
)

# --- Authenticate via Entra ID ---
try {
    Write-Verbose "Retrieving client secret from Key Vault '$KeyVaultName'..."
    $secret = Get-AzKeyVaultSecret -VaultName $KeyVaultName -Name $SecretName -ErrorAction Stop

    Write-Verbose "Authenticating service principal '$ClientId'..."
    $credential = [PSCredential]::new($ClientId, $secret.SecretValue)
    Connect-AzAccount -ServicePrincipal -TenantId $TenantId -Credential $credential -ErrorAction Stop | Out-Null

    Write-Verbose "Acquiring bearer token..."
    $token = (Get-AzAccessToken -ResourceUrl "https://api.applicationinsights.io" -ErrorAction Stop).Token
    $headers = @{ "Authorization" = "Bearer $token" }
}
catch {
    Write-Error "Authentication failed: $_"
    return [PSCustomObject]@{
        Status = 'Error'; ErrorType = 'AuthenticationFailure'
        Message = "$_"; Timestamp = (Get-Date -Format 'o')
    }
}

# --- Build and execute KQL query ---
$startDate = (Get-Date).AddDays(-$DaysBack).ToString("yyyy-MM-dd")
$endDate   = (Get-Date).ToString("yyyy-MM-dd")

$query = @"
customEvents
| where timestamp between(datetime('$startDate') .. datetime('$endDate'))
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

$apiUrl = "https://api.applicationinsights.io/v1/apps/$AppInsightsAppId/query"
$body   = @{ query = $query } | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri $apiUrl -Headers $headers `
        -Method Post -Body $body -ContentType "application/json" -ErrorAction Stop

    $columns = $response.tables[0].columns.name
    $rows    = $response.tables[0].rows

    $results = foreach ($row in $rows) {
        $obj = [ordered]@{}
        for ($i = 0; $i -lt $columns.Count; $i++) {
            $obj[$columns[$i]] = $row[$i]
        }
        [PSCustomObject]$obj
    }

    Write-Host "RAI events found: $($results.Count)"
    if ($results.Count -gt 0) {
        $results | Export-Csv -Path $OutputPath -NoTypeInformation
        Write-Host "Exported to: $OutputPath"
    }
}
catch {
    Write-Error "Query failed: $_"
}
```

!!! tip "Full Script"
    The complete script with structured error handling, token refresh, and verbose logging is available in [FSI-AgentGov-Solutions](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/deny-event-correlation-report/scripts).

### Migration from x-api-key (v1.x)

If you are upgrading from the v1.x script that used `x-api-key` authentication:

| Step | Action |
|------|--------|
| 1 | Create an Entra ID App Registration (see Prerequisites above) |
| 2 | Assign **Monitoring Reader** role on the Application Insights resource |
| 3 | Store the client secret in Azure Key Vault |
| 4 | Replace script parameters: remove `-ApiKey`, add `-TenantId`, `-ClientId`, `-KeyVaultName`, `-SecretName` |
| 5 | Install required modules: `Install-Module Az.Accounts, Az.KeyVault` |
| 6 | Update any scheduled task or automation runbook invocations |

!!! warning "Legacy x-api-key Script (Deprecated)"
    The previous version of this script used `x-api-key` header authentication. This method is **deprecated as of March 31, 2026** and will stop working after that date. The legacy script is preserved below for reference only.

??? note "Legacy Script (x-api-key — DO NOT USE in production)"
    ```powershell
    # DEPRECATED — x-api-key authentication stops working March 31, 2026
    param(
        [Parameter(Mandatory)]
        [string]$AppInsightsAppId,

        [Parameter(Mandatory)]
        [string]$ApiKey,  # DEPRECATED

        [DateTime]$StartDate = (Get-Date).AddDays(-1),
        [DateTime]$EndDate = (Get-Date),
        [string]$OutputPath = ".\RaiTelemetry-$(Get-Date -Format 'yyyy-MM-dd').csv"
    )

    $headers = @{ "x-api-key" = $ApiKey }
    # ... remainder of legacy script omitted for brevity
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

*FSI Agent Governance Framework v1.2.41 - February 2026*
