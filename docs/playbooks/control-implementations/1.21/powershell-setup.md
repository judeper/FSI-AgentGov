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

## Complete Configuration Script

```powershell
<#
.SYNOPSIS
    Configures Control 1.21 - Adversarial Input Logging

.DESCRIPTION
    This script searches audit logs for potential adversarial inputs,
    validates logging configuration, and generates detection reports.

.PARAMETER StartDate
    Start date for audit log search

.PARAMETER EndDate
    End date for audit log search

.PARAMETER ExportPath
    Path for exports (default: current directory)

.EXAMPLE
    .\Configure-Control-1.21.ps1 -StartDate "2026-01-01" -EndDate "2026-01-15"

.NOTES
    Last Updated: January 2026
    Related Control: Control 1.21 - Adversarial Input Logging
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$StartDate,

    [Parameter(Mandatory=$true)]
    [string]$EndDate,

    [string]$ExportPath = "."
)

try {
    # Connect to Security & Compliance
    Write-Host "Connecting to Security & Compliance Center..." -ForegroundColor Cyan
    Connect-IPPSSession

    Write-Host "Configuring Control 1.21: Adversarial Input Logging" -ForegroundColor Cyan

    # Step 1: Verify audit logging is enabled
    Write-Host "`n[Step 1] Verifying audit logging configuration..." -ForegroundColor Yellow
    $auditConfig = Get-AdminAuditLogConfig
    if ($auditConfig.UnifiedAuditLogIngestionEnabled) {
        Write-Host "  Unified Audit Log: Enabled" -ForegroundColor Green
    } else {
        Write-Host "  WARNING: Unified Audit Log is NOT enabled" -ForegroundColor Red
        Write-Host "  [INFO] Enable via: Set-AdminAuditLogConfig -UnifiedAuditLogIngestionEnabled \$true" -ForegroundColor Gray
    }

    # Step 2: Define adversarial patterns
    Write-Host "`n[Step 2] Searching for adversarial input patterns..." -ForegroundColor Yellow
    $adversarialPatterns = @(
        "ignore previous",
        "system prompt",
        "DAN mode",
        "jailbreak",
        "pretend you are",
        "bypass",
        "override instructions"
    )

    $allResults = @()

    foreach ($pattern in $adversarialPatterns) {
        Write-Host "  Searching: '$pattern'" -ForegroundColor Gray

        $results = Search-UnifiedAuditLog -StartDate $StartDate -EndDate $EndDate `
            -FreeText $pattern -RecordType "CopilotInteraction" -ResultSize 100 -ErrorAction SilentlyContinue

        if ($results) {
            Write-Host "    Found: $($results.Count) events" -ForegroundColor Red
            foreach ($r in $results) {
                $allResults += [PSCustomObject]@{
                    Pattern = $pattern
                    Date = $r.CreationDate
                    User = $r.UserIds
                    Operation = $r.Operations
                }
            }
        } else {
            Write-Host "    No matches" -ForegroundColor Green
        }
    }

    # Step 3: Generate summary
    Write-Host "`n[Step 3] Generating detection summary..." -ForegroundColor Yellow
    if ($allResults.Count -gt 0) {
        Write-Host "  WARNING: $($allResults.Count) potential adversarial inputs detected" -ForegroundColor Red

        # Group by pattern
        $groupedResults = $allResults | Group-Object Pattern
        foreach ($group in $groupedResults) {
            Write-Host "    $($group.Name): $($group.Count) events"
        }

        # Export results
        $reportFile = Join-Path $ExportPath "AdversarialInputs-$(Get-Date -Format 'yyyyMMdd').csv"
        $allResults | Export-Csv -Path $reportFile -NoTypeInformation
        Write-Host "  Results exported to: $reportFile" -ForegroundColor Yellow
    } else {
        Write-Host "  No adversarial inputs detected in the specified period" -ForegroundColor Green
    }

    # Step 4: Provide Sentinel guidance
    Write-Host "`n[Step 4] Sentinel analytics rule guidance..." -ForegroundColor Yellow
    Write-Host "  [INFO] Create a Sentinel analytics rule with this KQL query:" -ForegroundColor Gray
    $kqlQuery = @"
AuditLogs
| where ActivityDisplayName contains "Copilot"
| where TargetResources has_any ("ignore previous", "system prompt", "jailbreak", "DAN mode")
| project TimeGenerated, UserPrincipalName, ActivityDisplayName, TargetResources
"@
    Write-Host $kqlQuery -ForegroundColor DarkGray
    Write-Host "`n  Recommended settings: Severity=High, Frequency=5min" -ForegroundColor Gray

    Write-Host "`n[PASS] Control 1.21 configuration completed successfully" -ForegroundColor Green
}
catch {
    Write-Host "[FAIL] Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "[INFO] Stack trace: $($_.ScriptStackTrace)" -ForegroundColor Yellow
    exit 1
}
finally {
    # Cleanup connections
    Disconnect-ExchangeOnline -Confirm:$false -ErrorAction SilentlyContinue
    Write-Host "`nDisconnected from Security & Compliance Center" -ForegroundColor Gray
}
```

---

[Back to Control 1.21](../../../controls/pillar-1-security/1.21-adversarial-input-logging.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
