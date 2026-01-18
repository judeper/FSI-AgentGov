# PowerShell Setup: Control 2.12 - Supervision and Oversight

**Last Updated:** January 2026
**Modules Required:** PnP.PowerShell, ImportExcel

## Prerequisites

```powershell
Install-Module -Name PnP.PowerShell -Force -Scope CurrentUser
Install-Module -Name ImportExcel -Force -Scope CurrentUser
```

---

## Automated Scripts

### Export Supervision Log

```powershell
<#
.SYNOPSIS
    Exports supervision review log for compliance audit

.EXAMPLE
    .\Export-SupervisionLog.ps1 -SiteUrl "https://tenant.sharepoint.com/sites/AIGovernance"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$SiteUrl,
    [string]$ListName = "AgentSupervisionLog",
    [string]$OutputPath = ".\SupervisionLog.csv"
)

Write-Host "=== Export Supervision Log ===" -ForegroundColor Cyan

Connect-PnPOnline -Url $SiteUrl -Interactive

$items = Get-PnPListItem -List $ListName -PageSize 1000

$export = @()
foreach ($item in $items) {
    $export += [PSCustomObject]@{
        AgentName = $item["AgentName"]
        ConversationId = $item["ConversationId"]
        ReviewDate = $item["ReviewDate"]
        Reviewer = $item["Reviewer"]
        Decision = $item["Decision"]
        Comments = $item["Comments"]
        RiskLevel = $item["RiskLevel"]
    }
}

$export | Export-Csv -Path $OutputPath -NoTypeInformation
Write-Host "Export saved to: $OutputPath" -ForegroundColor Green
Write-Host "Total records: $($export.Count)"

Disconnect-PnPOnline
```

### Generate Supervision Report

```powershell
<#
.SYNOPSIS
    Generates supervision statistics report

.EXAMPLE
    .\New-SupervisionReport.ps1 -LogPath ".\SupervisionLog.csv"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$LogPath,
    [string]$OutputPath = ".\SupervisionReport.xlsx"
)

Write-Host "=== Generate Supervision Report ===" -ForegroundColor Cyan

$log = Import-Csv $LogPath

# Summary statistics
$total = $log.Count
$approved = ($log | Where-Object { $_.Decision -eq "Approved" }).Count
$rejected = ($log | Where-Object { $_.Decision -eq "Rejected" }).Count
$pending = ($log | Where-Object { $_.Decision -eq "Pending" }).Count

$summary = [PSCustomObject]@{
    TotalReviews = $total
    Approved = $approved
    Rejected = $rejected
    Pending = $pending
    ApprovalRate = [math]::Round($approved / $total * 100, 1)
}

# By risk level
$byRisk = $log | Group-Object RiskLevel | ForEach-Object {
    [PSCustomObject]@{
        RiskLevel = $_.Name
        Count = $_.Count
        Percentage = [math]::Round($_.Count / $total * 100, 1)
    }
}

# Export to Excel
$summary | Export-Excel -Path $OutputPath -WorksheetName "Summary" -AutoSize
$byRisk | Export-Excel -Path $OutputPath -WorksheetName "ByRiskLevel" -AutoSize -Append

Write-Host "Report saved to: $OutputPath" -ForegroundColor Green
```

---

## Validation Script

```powershell
<#
.SYNOPSIS
    Validates Control 2.12 - Supervision configuration

.EXAMPLE
    .\Validate-Control-2.12.ps1
#>

Write-Host "=== Control 2.12 Validation ===" -ForegroundColor Cyan

# Check 1: WSP documentation
Write-Host "`n[Check 1] WSP Addendum" -ForegroundColor Cyan
Write-Host "[INFO] Verify WSP addendum for AI agents is documented and approved"

# Check 2: HITL configuration
Write-Host "`n[Check 2] HITL Configuration" -ForegroundColor Cyan
Write-Host "[INFO] Verify HITL is enabled in Copilot Studio for Zone 3 agents"

# Check 3: Supervision log
Write-Host "`n[Check 3] Supervision Log" -ForegroundColor Cyan
Write-Host "[INFO] Verify supervision reviews are being logged"

# Check 4: Designated principals
Write-Host "`n[Check 4] Designated Principals" -ForegroundColor Cyan
Write-Host "[INFO] Verify principals with appropriate registrations are assigned"

Write-Host "`n=== Validation Complete ===" -ForegroundColor Cyan
```

---

[Back to Control 2.12](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
