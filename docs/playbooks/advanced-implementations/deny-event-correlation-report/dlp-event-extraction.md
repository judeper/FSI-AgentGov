# DLP Event Extraction for Copilot Location

**Parent:** [Deny Event Correlation Report](index.md)

---

## Overview

Microsoft Purview DLP supports a dedicated **Microsoft 365 Copilot and Copilot Chat** policy location. This guide covers extracting DLP events that match this location for correlation with CopilotInteraction deny events.

---

## DLP Policy Location

### Copilot-Specific Policy Location

When creating DLP policies in Microsoft Purview, the "Microsoft 365 Copilot and Copilot Chat" location enables:

- **Sensitivity label-based blocking** - Prevent Copilot from accessing files with specific labels
- **Prompt content inspection** - Detect SITs in user prompts
- **Response blocking** - Block responses containing sensitive data

### Policy Configuration Reference

| Policy Action | When It Triggers | Audit Event |
|---------------|------------------|-------------|
| **Block** | User prompt contains SIT or requests restricted content | `DlpRuleMatch` |
| **Warn** | User warned but can proceed | `DlpRuleMatch` |
| **Override** | User provided justification | `DlpRuleMatch` with override |

---

## DLP Event Schema

### DlpRuleMatch Audit Record

```json
{
  "RecordType": 55,
  "Operation": "DlpRuleMatch",
  "Workload": "MicrosoftCopilot",
  "UserId": "user@contoso.com",
  "PolicyDetails": [{
    "PolicyId": "guid",
    "PolicyName": "Block NPI in Copilot",
    "Rules": [{
      "RuleName": "SSN Detection",
      "Actions": ["BlockAccess"],
      "Severity": "High"
    }]
  }],
  "SensitiveInfoTypeData": [{
    "SensitiveInfoTypeId": "a44669fe-0d48-453d-a9b1-2cc83f2cba77",
    "SensitiveInfoTypeName": "U.S. Social Security Number (SSN)",
    "Count": 1,
    "Confidence": 85
  }],
  "ExceptionInfo": null
}
```

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

---

## PowerShell Extraction Script

### Daily DLP Export with Entra ID Authentication

The modernized script uses the `DECClient.psm1` shared module for secure authentication. Credentials are retrieved from Azure Key Vault — no hardcoded secrets.

```powershell
#Requires -Version 7.0
#Requires -Modules @{ ModuleName="ExchangeOnlineManagement"; ModuleVersion="3.0.0" }

<#
.SYNOPSIS
    Exports DLP events for the Copilot policy location.
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

# Search for DlpRuleMatch events
$startDate = (Get-Date).AddDays(-$DaysBack).Date
$endDate   = (Get-Date).Date
$allDlpEvents = @()
$sessionId = [Guid]::NewGuid().ToString()

do {
    $results = Search-UnifiedAuditLog `
        -RecordType DlpRuleMatch `
        -StartDate $startDate `
        -EndDate $endDate `
        -SessionId $sessionId `
        -SessionCommand ReturnLargeSet `
        -ResultSize 5000

    if ($results) {
        $allDlpEvents += $results
        Write-Verbose "Retrieved $($allDlpEvents.Count) events..."
    }
} while ($results.Count -eq 5000)

Write-Host "Total DLP events: $($allDlpEvents.Count)"

# Filter for Copilot-related events
$copilotDlpEvents = $allDlpEvents | ForEach-Object {
    $auditData = $_.AuditData | ConvertFrom-Json

    $isCopilotRelated = (
        $auditData.Workload -eq "MicrosoftCopilot" -or
        $auditData.Workload -match "Copilot" -or
        ($auditData.PolicyDetails | Where-Object { $_.PolicyName -match "Copilot" })
    )

    if ($isCopilotRelated) {
        $policyNames = ($auditData.PolicyDetails |
            ForEach-Object { $_.PolicyName }) -join "; "
        $ruleNames = ($auditData.PolicyDetails.Rules |
            ForEach-Object { $_.RuleName }) -join "; "
        $actions = ($auditData.PolicyDetails.Rules.Actions |
            Select-Object -Unique) -join "; "
        $sitMatches = ($auditData.SensitiveInfoTypeData | ForEach-Object {
            "$($_.SensitiveInfoTypeName) (Count: $($_.Count), Confidence: $($_.Confidence)%)"
        }) -join "; "

        [PSCustomObject]@{
            Timestamp          = $_.CreationDate
            UserId             = $auditData.UserId
            Workload           = $auditData.Workload
            PolicyNames        = $policyNames
            RuleNames          = $ruleNames
            Actions            = $actions
            SensitiveInfoTypes = $sitMatches
            Severity           = ($auditData.PolicyDetails.Rules |
                Select-Object -ExpandProperty Severity -First 1)
            HasOverride        = ($null -ne $auditData.ExceptionInfo)
            RawAuditData       = $_.AuditData
        }
    }
}

Write-Host "Copilot DLP events found: $($copilotDlpEvents.Count)"

# Export results
if ($OutputFormat -eq 'JSON') {
    $copilotDlpEvents | ConvertTo-Json -Depth 10 |
        Set-Content -Path $OutputPath -Encoding UTF8
} else {
    $copilotDlpEvents | Export-Csv -Path $OutputPath -NoTypeInformation
}
Write-Host "Exported to: $OutputPath"
```

!!! warning "Deprecated: Legacy Authentication"
    The v1.x script used interactive `Connect-ExchangeOnline` with user credentials. This approach does not support unattended automation and does not meet FSI security standards. Use the Entra ID service principal pattern shown above.

---

## Correlation with CopilotInteraction

DLP events may precede or coincide with CopilotInteraction events. Use these correlation strategies:

### Timestamp Window Correlation

```powershell
# In Power BI or offline processing
# Join DLP and CopilotInteraction events within ±5 minute window

$correlatedEvents = foreach ($dlp in $copilotDlpEvents) {
    $matchingCopilot = $copilotDenyEvents | Where-Object {
        $_.UserId -eq $dlp.UserId -and
        [Math]::Abs(($_.Timestamp - $dlp.Timestamp).TotalMinutes) -le 5
    }

    if ($matchingCopilot) {
        [PSCustomObject]@{
            CorrelationId = [Guid]::NewGuid()
            DlpTimestamp = $dlp.Timestamp
            CopilotTimestamp = $matchingCopilot.Timestamp
            UserId = $dlp.UserId
            DlpPolicy = $dlp.PolicyNames
            DlpAction = $dlp.Actions
            CopilotDenyReason = $matchingCopilot.DenyReason
            AgentName = $matchingCopilot.AgentName
        }
    }
}
```

### Correlation Categories

| Scenario | DLP Event | CopilotInteraction Event | Meaning |
|----------|-----------|-------------------------|---------|
| **Policy Block** | Present | Status=failure | DLP blocked content access |
| **Prompt Scan** | Present | No deny | DLP scanned but allowed |
| **Agent Guardrail** | Absent | Status=failure | Agent-level block, not DLP |
| **XPIA/Jailbreak** | Absent | XPIA=true | Security event, not data governance |

---

## Output Schema

The exported CSV includes:

| Column | Type | Description |
|--------|------|-------------|
| `Timestamp` | DateTime | Event occurrence time |
| `UserId` | String | User principal name |
| `Workload` | String | Microsoft service (MicrosoftCopilot) |
| `PolicyNames` | String | DLP policies that matched |
| `RuleNames` | String | Specific rules triggered |
| `Actions` | String | Block, Warn, or Override |
| `SensitiveInfoTypes` | String | SITs detected with confidence |
| `Severity` | String | Low, Medium, High |
| `HasOverride` | Boolean | User overrode policy |
| `RawAuditData` | JSON | Full audit record |

---

## Common DLP Patterns for FSI

### Pattern 1: NPI Protection

```
PolicyName: "Block NPI in Microsoft 365 Copilot"
SensitiveInfoTypes: U.S. Social Security Number, U.S. Bank Account Number
Action: Block
```

### Pattern 2: Confidential Label Restriction

```
PolicyName: "Restrict Confidential Content from Copilot"
Condition: Sensitivity Label = "Confidential - NPI"
Action: Block
```

### Pattern 3: Customer Data Warning

```
PolicyName: "Warn on Customer Data in Copilot"
SensitiveInfoTypes: Customer ID, Account Number (Custom SIT)
Action: Warn with justification
```

---

## Next Steps

- [App Insights RAI Telemetry](app-insights-rai-telemetry.md) - Extract RAI content filtering events
- [Power BI Correlation](power-bi-correlation.md) - Build the correlation dashboard

---

*FSI Agent Governance Framework v1.2.43 - February 2026*
