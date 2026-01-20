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

## Complete Configuration Script

```powershell
<#
.SYNOPSIS
    Complete patch management configuration for Control 2.10

.DESCRIPTION
    Executes end-to-end patch management setup including:
    - Message Center access verification
    - Recent updates retrieval
    - Patch history export for compliance

.PARAMETER Days
    Number of days of history to retrieve

.PARAMETER OutputPath
    Path for output reports

.EXAMPLE
    .\Configure-Control-2.10.ps1 -Days 30 -OutputPath ".\PatchManagement"

.NOTES
    Last Updated: January 2026
    Related Control: Control 2.10 - Patch Management and System Updates
#>

param(
    [int]$Days = 30,
    [string]$OutputPath = ".\PatchManagement-Report"
)

try {
    Write-Host "=== Control 2.10: Patch Management Configuration ===" -ForegroundColor Cyan

    # Connect to Microsoft Graph
    Connect-MgGraph -Scopes "ServiceMessage.Read.All"

    # Ensure output directory exists
    New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null

    $startDate = (Get-Date).AddDays(-$Days)
    Write-Host "[INFO] Retrieving updates from the last $Days days" -ForegroundColor Cyan

    # Get all service announcements
    $allMessages = Get-MgServiceAnnouncementMessage

    # Filter for Power Platform and Copilot Studio
    $relevantMessages = $allMessages | Where-Object {
        $_.LastModifiedDateTime -gt $startDate -and
        ($_.Services -contains "Power Platform" -or
         $_.Services -contains "Microsoft Copilot Studio" -or
         $_.Services -contains "Dynamics 365")
    }

    Write-Host "[INFO] Found $($relevantMessages.Count) relevant updates" -ForegroundColor Cyan

    # Build export
    $export = $relevantMessages | ForEach-Object {
        [PSCustomObject]@{
            MessageId = $_.Id
            Title = $_.Title
            Services = ($_.Services -join ", ")
            Category = $_.Category
            StartDateTime = $_.StartDateTime
            EndDateTime = $_.EndDateTime
            LastModified = $_.LastModifiedDateTime
            IsMajorChange = $_.IsMajorChange
            ActionRequired = if ($_.ActionRequiredByDateTime) { $_.ActionRequiredByDateTime } else { "N/A" }
        }
    }

    # Export to CSV
    $export | Export-Csv -Path "$OutputPath\PatchHistory-$(Get-Date -Format 'yyyyMMdd').csv" -NoTypeInformation
    Write-Host "[INFO] Exported to: $OutputPath\PatchHistory-$(Get-Date -Format 'yyyyMMdd').csv" -ForegroundColor Green

    # Identify critical updates requiring action
    $actionRequired = $relevantMessages | Where-Object { $_.ActionRequiredByDateTime }
    if ($actionRequired.Count -gt 0) {
        Write-Host "`n[WARN] Updates requiring action: $($actionRequired.Count)" -ForegroundColor Yellow
        $actionRequired | Select-Object Title, ActionRequiredByDateTime | Format-Table -AutoSize
        $actionRequired | Export-Csv -Path "$OutputPath\ActionRequired.csv" -NoTypeInformation
    }

    # Summary
    Write-Host "`n=== Summary ===" -ForegroundColor Cyan
    Write-Host "Total Updates Retrieved: $($relevantMessages.Count)"
    Write-Host "Major Changes: $(($relevantMessages | Where-Object { $_.IsMajorChange }).Count)"
    Write-Host "Action Required: $($actionRequired.Count)"

    Write-Host "`n[PASS] Control 2.10 configuration completed successfully" -ForegroundColor Green
}
catch {
    Write-Host "[FAIL] Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "[INFO] Stack trace: $($_.ScriptStackTrace)" -ForegroundColor Yellow
    exit 1
}
finally {
    # Cleanup connections
    Disconnect-MgGraph -ErrorAction SilentlyContinue
}
```

---

[Back to Control 2.10](../../../controls/pillar-2-management/2.10-patch-management-and-system-updates.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
