# PowerShell Setup: Control 1.21 - Adversarial Input Logging

**Last Updated:** January 2026
**Modules Required:** Az.SecurityInsights, ExchangeOnlineManagement

## Prerequisites

```powershell
Install-Module -Name Az.SecurityInsights -Force -Scope CurrentUser
Install-Module -Name ExchangeOnlineManagement -Force -Scope CurrentUser
```

---

## Automated Scripts

### Search Audit Log for Adversarial Patterns

```powershell
<#
.SYNOPSIS
    Searches audit log for potential adversarial inputs

.EXAMPLE
    .\Search-AdversarialInputs.ps1 -StartDate "2026-01-01" -EndDate "2026-01-15"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$StartDate,
    [Parameter(Mandatory=$true)]
    [string]$EndDate
)

Write-Host "=== Adversarial Input Search ===" -ForegroundColor Cyan

Connect-IPPSSession

$adversarialPatterns = @(
    "ignore previous",
    "system prompt",
    "DAN mode",
    "jailbreak",
    "pretend you are"
)

foreach ($pattern in $adversarialPatterns) {
    Write-Host "Searching for: $pattern" -ForegroundColor Yellow

    $results = Search-UnifiedAuditLog -StartDate $StartDate -EndDate $EndDate `
        -FreeText $pattern -RecordType "CopilotInteraction" -ResultSize 100

    if ($results) {
        Write-Host "  Found: $($results.Count) events" -ForegroundColor Red
        $results | Select-Object CreationDate, UserIds, Operations | Format-Table
    } else {
        Write-Host "  No matches found" -ForegroundColor Green
    }
}

Disconnect-ExchangeOnline -Confirm:$false
```

### Create Sentinel Analytics Rule

```powershell
<#
.SYNOPSIS
    Creates Sentinel analytics rule for adversarial detection

.EXAMPLE
    .\New-AdversarialDetectionRule.ps1 -WorkspaceName "sentinel-workspace" -ResourceGroup "rg-security"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$WorkspaceName,
    [Parameter(Mandatory=$true)]
    [string]$ResourceGroup
)

Write-Host "=== Create Sentinel Rule ===" -ForegroundColor Cyan

Connect-AzAccount

$query = @"
AuditLogs
| where ActivityDisplayName contains "Copilot"
| where TargetResources has_any ("ignore previous", "system prompt", "jailbreak", "DAN mode")
| project TimeGenerated, UserPrincipalName, ActivityDisplayName, TargetResources
"@

# Note: Full Sentinel rule creation requires ARM templates or portal
Write-Host "[INFO] Use Azure Portal to create analytics rule with this query:"
Write-Host $query
Write-Host ""
Write-Host "Rule settings:"
Write-Host "  - Severity: High"
Write-Host "  - Run frequency: 5 minutes"
Write-Host "  - Lookup period: 5 minutes"
```

---

## Validation Script

```powershell
<#
.SYNOPSIS
    Validates Control 1.21 - Adversarial input logging configuration

.EXAMPLE
    .\Validate-Control-1.21.ps1
#>

Write-Host "=== Control 1.21 Validation ===" -ForegroundColor Cyan

# Check 1: Audit logging
Write-Host "`n[Check 1] Audit Logging" -ForegroundColor Cyan
Connect-IPPSSession
$auditConfig = Get-AdminAuditLogConfig
Write-Host "Unified Audit Log: $($auditConfig.UnifiedAuditLogIngestionEnabled)"

# Check 2: Sentinel rules (manual)
Write-Host "`n[Check 2] Sentinel Rules" -ForegroundColor Cyan
Write-Host "[INFO] Verify analytics rules exist in Azure Sentinel"

# Check 3: Test detection
Write-Host "`n[Check 3] Test Detection" -ForegroundColor Cyan
Write-Host "[INFO] Submit test adversarial input and verify logging"

Disconnect-ExchangeOnline -Confirm:$false

Write-Host "`n=== Validation Complete ===" -ForegroundColor Cyan
```

---

[Back to Control 1.21](../../../controls/pillar-1-security/1.21-adversarial-input-logging.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
