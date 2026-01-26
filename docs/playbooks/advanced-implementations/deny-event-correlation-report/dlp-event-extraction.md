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

## PowerShell Extraction Script

### Daily DLP Export for Copilot

```powershell
<#
.SYNOPSIS
    Exports DLP events for Copilot policy location
.DESCRIPTION
    Extracts DlpRuleMatch events where Workload is Copilot-related
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
    [string]$OutputPath = ".\DlpCopilotEvents-$(Get-Date -Format 'yyyy-MM-dd').csv"
)

# Connect to Exchange Online
if (-not (Get-Command Search-UnifiedAuditLog -ErrorAction SilentlyContinue)) {
    Connect-ExchangeOnline -ShowBanner:$false
}

Write-Host "Searching for DLP events from $StartDate to $EndDate..."

# Search for DlpRuleMatch events
$allDlpEvents = @()
$sessionId = [Guid]::NewGuid().ToString()

do {
    $results = Search-UnifiedAuditLog `
        -RecordType DlpRuleMatch `
        -StartDate $StartDate `
        -EndDate $EndDate `
        -SessionId $sessionId `
        -SessionCommand ReturnLargeSet `
        -ResultSize 5000

    if ($results) {
        $allDlpEvents += $results
        Write-Host "Retrieved $($allDlpEvents.Count) events..."
    }
} while ($results.Count -eq 5000)

Write-Host "Total DLP events: $($allDlpEvents.Count)"

# Filter for Copilot-related events
$copilotDlpEvents = $allDlpEvents | ForEach-Object {
    $auditData = $_.AuditData | ConvertFrom-Json

    # Check if Copilot workload or Copilot-named policy
    $isCopilotRelated = (
        $auditData.Workload -eq "MicrosoftCopilot" -or
        $auditData.Workload -match "Copilot" -or
        ($auditData.PolicyDetails | Where-Object { $_.PolicyName -match "Copilot" })
    )

    if ($isCopilotRelated) {
        # Extract policy and rule details
        $policyNames = ($auditData.PolicyDetails | ForEach-Object { $_.PolicyName }) -join "; "
        $ruleNames = ($auditData.PolicyDetails.Rules | ForEach-Object { $_.RuleName }) -join "; "
        $actions = ($auditData.PolicyDetails.Rules.Actions | Select-Object -Unique) -join "; "

        # Extract SIT matches
        $sitMatches = ($auditData.SensitiveInfoTypeData | ForEach-Object {
            "$($_.SensitiveInfoTypeName) (Count: $($_.Count), Confidence: $($_.Confidence)%)"
        }) -join "; "

        [PSCustomObject]@{
            Timestamp = $_.CreationDate
            UserId = $auditData.UserId
            Workload = $auditData.Workload
            PolicyNames = $policyNames
            RuleNames = $ruleNames
            Actions = $actions
            SensitiveInfoTypes = $sitMatches
            Severity = ($auditData.PolicyDetails.Rules | Select-Object -ExpandProperty Severity -First 1)
            HasOverride = ($auditData.ExceptionInfo -ne $null)
            RawAuditData = $_.AuditData
        }
    }
}

Write-Host "Copilot DLP events found: $($copilotDlpEvents.Count)"

# Export to CSV
$copilotDlpEvents | Export-Csv -Path $OutputPath -NoTypeInformation
Write-Host "Exported to: $OutputPath"
```

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

*FSI Agent Governance Framework v1.2 - January 2026*
