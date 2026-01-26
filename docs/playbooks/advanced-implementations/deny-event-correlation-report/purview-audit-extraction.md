# Purview Audit Extraction for Deny Events

**Parent:** [Deny Event Correlation Report](index.md)

---

## Overview

This guide covers extracting CopilotInteraction deny events from Microsoft Purview Unified Audit Log using PowerShell.

---

## CopilotInteraction Deny Event Schema

When a Copilot or Copilot Studio agent encounters a policy block, the audit record includes specific indicators:

### AccessedResources Array

```json
{
  "AccessedResources": [
    {
      "ID": "resource-id-guid",
      "Name": "Confidential Document.docx",
      "Type": "File",
      "SiteUrl": "https://contoso.sharepoint.com/sites/hr",
      "Action": "Read",
      "Status": "failure",
      "SensitivityLabelId": "a1b2c3d4-...",
      "PolicyDetails": {
        "PolicyId": "policy-guid",
        "PolicyName": "Block Confidential from Copilot",
        "Action": "deny"
      },
      "XPIADetected": false
    }
  ]
}
```

### Key Deny Indicators

| Field | Deny Condition | Description |
|-------|----------------|-------------|
| `Status` | `"failure"` | Resource access was blocked |
| `PolicyDetails` | Present | DLP or sensitivity policy triggered |
| `XPIADetected` | `true` | Cross-prompt injection attempt detected |
| `Messages[].JailbreakDetected` | `true` | Jailbreak attempt detected |

---

## PowerShell Extraction Script

### Basic Daily Export

```powershell
<#
.SYNOPSIS
    Exports CopilotInteraction deny events from Purview Audit Log
.DESCRIPTION
    Extracts events where Status=failure, PolicyDetails present,
    or XPIA/Jailbreak detected
.PARAMETER StartDate
    Start of time window (default: yesterday)
.PARAMETER EndDate
    End of time window (default: today)
.PARAMETER OutputPath
    Path for CSV export
#>
param(
    [DateTime]$StartDate = (Get-Date).AddDays(-1),
    [DateTime]$EndDate = (Get-Date),
    [string]$OutputPath = ".\CopilotDenyEvents-$(Get-Date -Format 'yyyy-MM-dd').csv"
)

# Connect to Exchange Online (required for Search-UnifiedAuditLog)
if (-not (Get-Command Search-UnifiedAuditLog -ErrorAction SilentlyContinue)) {
    Connect-ExchangeOnline -ShowBanner:$false
}

Write-Host "Searching for CopilotInteraction events from $StartDate to $EndDate..."

# Search with pagination (50K limit per query)
$allEvents = @()
$sessionId = [Guid]::NewGuid().ToString()
$resultIndex = 0

do {
    $results = Search-UnifiedAuditLog `
        -RecordType CopilotInteraction `
        -StartDate $StartDate `
        -EndDate $EndDate `
        -SessionId $sessionId `
        -SessionCommand ReturnLargeSet `
        -ResultSize 5000

    if ($results) {
        $allEvents += $results
        $resultIndex = $results[-1].ResultIndex
        Write-Host "Retrieved $($allEvents.Count) events..."
    }
} while ($results.Count -eq 5000)

Write-Host "Total events retrieved: $($allEvents.Count)"

# Filter for deny events
$denyEvents = $allEvents | ForEach-Object {
    $auditData = $_.AuditData | ConvertFrom-Json

    $isDeny = $false
    $denyReason = @()

    # Check AccessedResources for failures
    foreach ($resource in $auditData.AccessedResources) {
        if ($resource.Status -eq "failure") {
            $isDeny = $true
            $denyReason += "ResourceFailure"
        }
        if ($resource.PolicyDetails) {
            $isDeny = $true
            $denyReason += "PolicyBlock:$($resource.PolicyDetails.PolicyName)"
        }
        if ($resource.XPIADetected -eq $true) {
            $isDeny = $true
            $denyReason += "XPIA"
        }
    }

    # Check Messages for jailbreak
    foreach ($message in $auditData.Messages) {
        if ($message.JailbreakDetected -eq $true) {
            $isDeny = $true
            $denyReason += "Jailbreak"
        }
    }

    if ($isDeny) {
        [PSCustomObject]@{
            Timestamp = $_.CreationDate
            UserId = $auditData.UserId
            Operation = $auditData.Operation
            AgentId = $auditData.AgentId
            AgentName = $auditData.AgentName
            AppHost = $auditData.AppHost
            DenyReason = ($denyReason -join "; ")
            ResourceCount = ($auditData.AccessedResources | Measure-Object).Count
            RawAuditData = $_.AuditData
        }
    }
}

Write-Host "Deny events found: $($denyEvents.Count)"

# Export to CSV
$denyEvents | Export-Csv -Path $OutputPath -NoTypeInformation
Write-Host "Exported to: $OutputPath"
```

---

## Event Categories

The script categorizes deny events by reason:

| Category | Description | Regulatory Impact |
|----------|-------------|-------------------|
| **ResourceFailure** | Agent couldn't access a resource | Access control evidence |
| **PolicyBlock** | DLP or sensitivity policy triggered | Data governance evidence |
| **XPIA** | Cross-prompt injection detected | Security incident |
| **Jailbreak** | Guardrail bypass attempt detected | Adversarial input evidence |

---

## Scheduling Daily Extraction

### Option 1: Windows Task Scheduler

```powershell
# Create scheduled task for daily 6 AM extraction
$action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-File C:\Scripts\Export-CopilotDenyEvents.ps1"

$trigger = New-ScheduledTaskTrigger -Daily -At "6:00 AM"

Register-ScheduledTask `
    -TaskName "Daily Copilot Deny Export" `
    -Action $action `
    -Trigger $trigger `
    -RunLevel Highest
```

### Option 2: Azure Automation

Deploy the script as an Azure Automation Runbook with a daily schedule. See [Deployment Guide](deployment-guide.md) for details.

---

## Output Schema

The exported CSV includes:

| Column | Type | Description |
|--------|------|-------------|
| `Timestamp` | DateTime | Event occurrence time |
| `UserId` | String | User principal name |
| `Operation` | String | Always "CopilotInteraction" |
| `AgentId` | String | Copilot Studio agent GUID |
| `AgentName` | String | Agent display name |
| `AppHost` | String | Hosting application (Teams, Web, etc.) |
| `DenyReason` | String | Categorized deny reason(s) |
| `ResourceCount` | Int | Number of resources in request |
| `RawAuditData` | JSON | Full audit record for analysis |

---

## Correlation Fields

Use these fields for correlation with DLP and RAI telemetry:

| Field | Correlation Use |
|-------|-----------------|
| `Timestamp` | ±5 minute window for event matching |
| `UserId` | Primary correlation key |
| `AgentId` | Filter to specific agents |
| `AppHost` | Channel-specific analysis |

---

## Next Steps

- [DLP Event Extraction](dlp-event-extraction.md) - Extract DLP rule matches for Copilot location
- [Power BI Correlation](power-bi-correlation.md) - Build the correlation dashboard

---

*FSI Agent Governance Framework v1.2 - January 2026*
