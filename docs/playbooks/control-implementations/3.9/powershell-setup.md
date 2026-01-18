# Control 3.9: Microsoft Sentinel Integration - PowerShell Setup

> This playbook provides PowerShell and KQL scripts for [Control 3.9](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md).

---

## Prerequisites

```powershell
# Install required modules
Install-Module -Name Az.SecurityInsights -Force -AllowClobber
Install-Module -Name Az.OperationalInsights -Force -AllowClobber

# Connect to Azure
Connect-AzAccount
Select-AzSubscription -SubscriptionId "your-subscription-id"
```

---

## KQL Queries for Agent Monitoring

### Unusual Agent Data Access Pattern

```kql
// Detect unusual agent data access patterns
let baseline = materialize(
    OfficeActivity
    | where TimeGenerated > ago(30d) and TimeGenerated < ago(1d)
    | where UserId contains "agent" or ApplicationName contains "Copilot"
    | summarize AvgAccess = count() / 30.0 by UserId
);
OfficeActivity
| where TimeGenerated > ago(1h)
| where UserId contains "agent" or ApplicationName contains "Copilot"
| summarize CurrentAccess = count() by UserId
| join kind=inner baseline on UserId
| where CurrentAccess > AvgAccess * 3
| project
    UserId,
    CurrentAccess,
    Baseline = round(AvgAccess, 0),
    Deviation = round(CurrentAccess / AvgAccess, 1)
```

### Agent DLP Violation Detection

```kql
// Detect DLP violations by AI agents
DlpAll
| where TimeGenerated > ago(1h)
| where Actor contains "agent" or Actor contains "copilot" or Actor contains "bot"
| summarize
    ViolationCount = count(),
    Policies = make_set(PolicyName),
    SensitiveTypes = make_set(SensitiveInfoTypeNames)
    by Actor, Application
| where ViolationCount > 0
| order by ViolationCount desc
```

### After-Hours Agent Activity

```kql
// Detect agent activity outside business hours
let BusinessHoursStart = 7;
let BusinessHoursEnd = 19;
OfficeActivity
| where TimeGenerated > ago(24h)
| where UserId contains "agent" or ApplicationName contains "Copilot"
| extend LocalHour = datetime_part("hour", TimeGenerated)
| where LocalHour < BusinessHoursStart or LocalHour > BusinessHoursEnd
| summarize
    OffHoursEvents = count(),
    Operations = make_set(Operation)
    by UserId, bin(TimeGenerated, 1h)
| where OffHoursEvents > 10
```

### Agent Data Exfiltration Pattern

```kql
// Detect potential data exfiltration by agents
OfficeActivity
| where TimeGenerated > ago(1h)
| where UserId contains "agent" or ApplicationName contains "Copilot"
| where Operation in ("FileDownloaded", "FileSyncDownloadedFull", "FileAccessed")
| summarize
    FileCount = count(),
    TotalSize = sum(tolong(FileSize)),
    UniqueFiles = dcount(OfficeObjectId)
    by UserId, bin(TimeGenerated, 15m)
| where FileCount > 50 or TotalSize > 100000000
```

---

## PowerShell: Create Analytics Rule

```powershell
function New-AgentAnalyticsRule {
    param(
        [Parameter(Mandatory=$true)]
        [string]$WorkspaceName,
        [Parameter(Mandatory=$true)]
        [string]$ResourceGroupName,
        [string]$RuleName = "Unusual Agent Data Access",
        [string]$Severity = "Medium"
    )

    Write-Host "Creating analytics rule: $RuleName" -ForegroundColor Cyan

    $query = @'
let baseline = materialize(
    OfficeActivity
    | where TimeGenerated > ago(30d) and TimeGenerated < ago(1d)
    | where UserId contains "agent" or ApplicationName contains "Copilot"
    | summarize AvgAccess = count() / 30.0 by UserId
);
OfficeActivity
| where TimeGenerated > ago(1h)
| where UserId contains "agent" or ApplicationName contains "Copilot"
| summarize CurrentAccess = count() by UserId
| join kind=inner baseline on UserId
| where CurrentAccess > AvgAccess * 3
'@

    $ruleParams = @{
        ResourceGroupName = $ResourceGroupName
        WorkspaceName = $WorkspaceName
        DisplayName = $RuleName
        Enabled = $true
        Severity = $Severity
        Query = $query
        QueryFrequency = "PT5M"
        QueryPeriod = "PT1H"
        TriggerOperator = "GreaterThan"
        TriggerThreshold = 0
    }

    try {
        New-AzSentinelAlertRule @ruleParams -Kind Scheduled
        Write-Host "Rule created successfully" -ForegroundColor Green
    }
    catch {
        Write-Error "Failed to create rule: $_"
    }
}
```

---

## PowerShell: Get Agent-Related Incidents

```powershell
function Get-AgentSecurityIncidents {
    param(
        [Parameter(Mandatory=$true)]
        [string]$WorkspaceName,
        [Parameter(Mandatory=$true)]
        [string]$ResourceGroupName,
        [int]$DaysBack = 7
    )

    Write-Host "Retrieving agent-related incidents..." -ForegroundColor Cyan

    $incidents = Get-AzSentinelIncident -ResourceGroupName $ResourceGroupName -WorkspaceName $WorkspaceName

    $agentIncidents = $incidents | Where-Object {
        $_.Title -like "*agent*" -or
        $_.Title -like "*copilot*" -or
        $_.Title -like "*bot*"
    }

    Write-Host "Found $($agentIncidents.Count) agent-related incidents" -ForegroundColor Green

    $agentIncidents | Select-Object Title, Severity, Status, CreatedTimeUtc | Format-Table

    return $agentIncidents
}
```

---

## PowerShell: Export Sentinel Report

```powershell
function Export-SentinelAgentReport {
    param(
        [Parameter(Mandatory=$true)]
        [string]$WorkspaceId,
        [int]$DaysBack = 30,
        [string]$OutputPath = ".\SentinelAgentReport-$(Get-Date -Format 'yyyyMMdd').html"
    )

    Write-Host "Generating Sentinel agent report..." -ForegroundColor Cyan

    # Query Log Analytics
    $query = @"
OfficeActivity
| where TimeGenerated > ago($($DaysBack)d)
| where UserId contains "agent" or ApplicationName contains "Copilot"
| summarize
    TotalEvents = count(),
    UniqueAgents = dcount(UserId),
    UniqueOperations = dcount(Operation)
| project TotalEvents, UniqueAgents, UniqueOperations
"@

    $result = Invoke-AzOperationalInsightsQuery -WorkspaceId $WorkspaceId -Query $query

    $html = @"
<!DOCTYPE html>
<html>
<head>
    <title>Sentinel Agent Activity Report</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; margin: 40px; }
        h1 { color: #0078d4; }
        .metric { display: inline-block; padding: 20px; background: #f0f0f0; border-radius: 8px; margin: 10px; }
    </style>
</head>
<body>
    <h1>Microsoft Sentinel - Agent Activity Report</h1>
    <p>Period: Last $DaysBack days | Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm')</p>

    <div class="metric">
        <h3>Total Events</h3>
        <p style="font-size: 28px;">$($result.Results[0].TotalEvents)</p>
    </div>
    <div class="metric">
        <h3>Unique Agents</h3>
        <p style="font-size: 28px;">$($result.Results[0].UniqueAgents)</p>
    </div>
</body>
</html>
"@

    $html | Out-File $OutputPath -Encoding UTF8
    Write-Host "Report generated: $OutputPath" -ForegroundColor Green
}
```

---

## Usage Examples

```powershell
# Create analytics rule
New-AgentAnalyticsRule -WorkspaceName "sentinel-workspace" -ResourceGroupName "rg-security"

# Get agent incidents
Get-AgentSecurityIncidents -WorkspaceName "sentinel-workspace" -ResourceGroupName "rg-security"

# Export report
Export-SentinelAgentReport -WorkspaceId "workspace-guid"
```

---

## Next Steps

- [Portal Walkthrough](./portal-walkthrough.md) - Manual configuration
- [Verification & Testing](./verification-testing.md) - Test procedures
- [Troubleshooting](./troubleshooting.md) - Common issues

---

*Updated: January 2026 | Version: v1.1*
