# Purview Audit Extraction for Deny Events

**Parent:** [Deny Event Correlation Report](index.md)

---

## Overview

This guide covers extracting CopilotInteraction deny events from Microsoft Purview Unified Audit Log using PowerShell.

---

## CopilotInteraction Deny Event Schema

When a Copilot or Microsoft Copilot Studio agent encounters a policy block, the audit record includes specific indicators:

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

## Prerequisites

### Entra ID App Registration

Before running the extraction script, configure an Entra ID App Registration with Exchange Online access:

| Requirement | Value |
|-------------|-------|
| **App Registration** | Create in Entra ID > App registrations |
| **API Permission** | Office 365 Exchange Online > Application > `Exchange.ManageAsApp` |
| **Admin Consent** | Required (tenant admin) |
| **Entra Role** | Purview Audit Reader or Purview Compliance Admin |
| **Key Vault** | Store client secret in Azure Key Vault |

!!! tip "Certificate-Based Authentication (Recommended)"
    For production deployments, use certificate-based authentication instead of client secrets. Pass the `-CertificateThumbprint` parameter to skip Key Vault secret retrieval.

---

## PowerShell Extraction Script

### Daily Export with Entra ID Authentication

The modernized script uses the `DECClient.psm1` shared module for secure authentication. Credentials are retrieved from Azure Key Vault — no hardcoded secrets.

```powershell
#Requires -Version 7.0
#Requires -Modules @{ ModuleName="ExchangeOnlineManagement"; ModuleVersion="3.0.0" }

<#
.SYNOPSIS
    Exports CopilotInteraction deny events from Purview Audit Log.
.DESCRIPTION
    Uses Entra ID service principal authentication via DECClient module.
    Retrieves credentials from Azure Key Vault — no hardcoded secrets.
.PARAMETER TenantId
    Entra ID tenant ID for service principal authentication.
.PARAMETER ClientId
    App Registration client ID with Exchange.ManageAsApp permission.
.PARAMETER KeyVaultName
    Azure Key Vault containing the service principal credentials.
.PARAMETER DaysBack
    Days of data to retrieve (default: 1, max: 90).
.PARAMETER OutputPath
    Path for exported file.
.PARAMETER OutputFormat
    Export format: CSV or JSON (default: CSV).
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidateNotNullOrEmpty()][string]$TenantId,
    [Parameter(Mandatory)][ValidateNotNullOrEmpty()][string]$ClientId,
    [Parameter(Mandatory)][ValidateNotNullOrEmpty()][string]$KeyVaultName,
    [ValidateNotNullOrEmpty()][string]$CertificateThumbprint,
    [ValidateRange(1, 90)][int]$DaysBack = 1,
    [ValidateScript({ Test-Path (Split-Path $_) })][string]$OutputPath,
    [ValidateSet('CSV','JSON')][string]$OutputFormat = 'CSV'
)

$ErrorActionPreference = 'Stop'

# Import shared authentication module
Import-Module "$PSScriptRoot/private/DECClient.psm1" -Force

# Connect to Exchange Online via Entra ID service principal
$connectParams = @{
    TenantId     = $TenantId
    ClientId     = $ClientId
    KeyVaultName = $KeyVaultName
}
if ($CertificateThumbprint) {
    $connectParams['CertificateThumbprint'] = $CertificateThumbprint
}
$connectResult = Connect-DECExchangeOnline @connectParams
if ($connectResult.Status -ne 'Success') {
    Write-Error "Connection failed: $($connectResult.Message)"
    return
}

# Search with pagination (50K limit per query)
$startDate = (Get-Date).AddDays(-$DaysBack).Date
$endDate   = (Get-Date).Date
$allEvents = @()
$sessionId = [Guid]::NewGuid().ToString()

do {
    $results = Search-UnifiedAuditLog `
        -RecordType CopilotInteraction `
        -StartDate $startDate `
        -EndDate $endDate `
        -SessionId $sessionId `
        -SessionCommand ReturnLargeSet `
        -ResultSize 5000

    if ($results) {
        $allEvents += $results
        Write-Verbose "Retrieved $($allEvents.Count) events..."
    }
} while ($results.Count -eq 5000)

Write-Host "Total events retrieved: $($allEvents.Count)"

# Filter for deny events
$denyEvents = $allEvents | ForEach-Object {
    $auditData = $_.AuditData | ConvertFrom-Json

    $isDeny = $false
    $denyReason = @()

    foreach ($resource in $auditData.AccessedResources) {
        if ($resource.Status -eq "failure") {
            $isDeny = $true; $denyReason += "ResourceFailure"
        }
        if ($resource.PolicyDetails) {
            $isDeny = $true
            $denyReason += "PolicyBlock:$($resource.PolicyDetails.PolicyName)"
        }
        if ($resource.XPIADetected -eq $true) {
            $isDeny = $true; $denyReason += "XPIA"
        }
    }

    foreach ($message in $auditData.Messages) {
        if ($message.JailbreakDetected -eq $true) {
            $isDeny = $true; $denyReason += "Jailbreak"
        }
    }

    if ($isDeny) {
        [PSCustomObject]@{
            Timestamp     = $_.CreationDate
            UserId        = $auditData.UserId
            Operation     = $auditData.Operation
            AgentId       = $auditData.AgentId
            AgentName     = $auditData.AgentName
            AppHost       = $auditData.AppHost
            DenyReason    = ($denyReason -join "; ")
            ResourceCount = ($auditData.AccessedResources | Measure-Object).Count
            RawAuditData  = $_.AuditData
        }
    }
}

Write-Host "Deny events found: $($denyEvents.Count)"

# Export results
if ($OutputFormat -eq 'JSON') {
    $denyEvents | ConvertTo-Json -Depth 10 | Set-Content -Path $OutputPath -Encoding UTF8
} else {
    $denyEvents | Export-Csv -Path $OutputPath -NoTypeInformation
}
Write-Host "Exported to: $OutputPath"
```

!!! warning "Deprecated: Legacy Authentication"
    The v1.x script used interactive `Connect-ExchangeOnline` with user credentials. This approach does not support unattended automation and does not meet FSI security standards. Use the Entra ID service principal pattern shown above.

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

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
