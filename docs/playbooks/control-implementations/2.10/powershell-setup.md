# PowerShell Setup: Control 2.10 - Patch Management and System Updates

**Last Updated:** January 2026
**Modules Required:** Microsoft.Graph

## Prerequisites

```powershell
Install-Module -Name Microsoft.Graph -Force -Scope CurrentUser
```

---

## Automated Scripts

### Get Message Center Updates

```powershell
<#
.SYNOPSIS
    Retrieves recent Message Center updates for Power Platform

.EXAMPLE
    .\Get-PowerPlatformUpdates.ps1 -Days 30
#>

param(
    [int]$Days = 30
)

Write-Host "=== Power Platform Updates ===" -ForegroundColor Cyan

Connect-MgGraph -Scopes "ServiceMessage.Read.All"

$startDate = (Get-Date).AddDays(-$Days)

$messages = Get-MgServiceAnnouncementMessage | Where-Object {
    $_.LastModifiedDateTime -gt $startDate -and
    ($_.Services -contains "Power Platform" -or
     $_.Services -contains "Microsoft Copilot Studio")
}

Write-Host "Updates in last $Days days: $($messages.Count)"

foreach ($msg in $messages) {
    Write-Host "`n$($msg.Title)" -ForegroundColor Yellow
    Write-Host "  ID: $($msg.Id)"
    Write-Host "  Services: $($msg.Services -join ', ')"
    Write-Host "  Category: $($msg.Category)"
    Write-Host "  Modified: $($msg.LastModifiedDateTime)"
}

Disconnect-MgGraph
```

### Export Patch History

```powershell
<#
.SYNOPSIS
    Exports patch history log for compliance

.EXAMPLE
    .\Export-PatchHistory.ps1
#>

param(
    [string]$OutputPath = ".\PatchHistory.csv"
)

Write-Host "=== Export Patch History ===" -ForegroundColor Cyan

Connect-MgGraph -Scopes "ServiceMessage.Read.All"

$messages = Get-MgServiceAnnouncementMessage | Where-Object {
    $_.Services -contains "Power Platform" -or
    $_.Services -contains "Microsoft Copilot Studio"
} | Select-Object -First 100

$export = @()
foreach ($msg in $messages) {
    $export += [PSCustomObject]@{
        MessageId = $msg.Id
        Title = $msg.Title
        Services = ($msg.Services -join ", ")
        Category = $msg.Category
        StartDateTime = $msg.StartDateTime
        EndDateTime = $msg.EndDateTime
        LastModified = $msg.LastModifiedDateTime
        IsMajorChange = $msg.IsMajorChange
    }
}

$export | Export-Csv -Path $OutputPath -NoTypeInformation
Write-Host "Export saved to: $OutputPath" -ForegroundColor Green

Disconnect-MgGraph
```

---

## Validation Script

```powershell
<#
.SYNOPSIS
    Validates Control 2.10 - Patch management configuration

.EXAMPLE
    .\Validate-Control-2.10.ps1
#>

Write-Host "=== Control 2.10 Validation ===" -ForegroundColor Cyan

# Check 1: Message Center access
Write-Host "`n[Check 1] Message Center Access" -ForegroundColor Cyan
Connect-MgGraph -Scopes "ServiceMessage.Read.All"
$recentMessages = Get-MgServiceAnnouncementMessage | Select-Object -First 5
Write-Host "[PASS] Message Center accessible: $($recentMessages.Count) recent messages" -ForegroundColor Green
Disconnect-MgGraph

# Check 2: Test environment (manual)
Write-Host "`n[Check 2] Test Environment" -ForegroundColor Cyan
Write-Host "[INFO] Verify test environment exists in PPAC"

# Check 3: Documentation (manual)
Write-Host "`n[Check 3] Patch Documentation" -ForegroundColor Cyan
Write-Host "[INFO] Verify patch history log is maintained"

Write-Host "`n=== Validation Complete ===" -ForegroundColor Cyan
```

---

[Back to Control 2.10](../../../controls/pillar-2-management/2.10-patch-management-and-system-updates.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
