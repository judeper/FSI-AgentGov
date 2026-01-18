# PowerShell Setup: Control 1.22 - Information Barriers

**Last Updated:** January 2026
**Modules Required:** ExchangeOnlineManagement

## Prerequisites

```powershell
Install-Module -Name ExchangeOnlineManagement -Force -Scope CurrentUser
```

---

## Automated Scripts

### Create Organization Segments

```powershell
<#
.SYNOPSIS
    Creates organization segments for Information Barriers

.EXAMPLE
    .\New-IBSegments.ps1
#>

Write-Host "=== Create IB Segments ===" -ForegroundColor Cyan

Connect-IPPSSession

$segments = @(
    @{Name="IB-Research"; Filter="Department -eq 'Research'"},
    @{Name="IB-Trading"; Filter="Department -eq 'Trading'"},
    @{Name="IB-InvestmentBanking"; Filter="Department -eq 'Investment Banking'"},
    @{Name="IB-Sales"; Filter="Department -eq 'Sales'"},
    @{Name="IB-Compliance"; Filter="Department -eq 'Compliance'"}
)

foreach ($segment in $segments) {
    $existing = Get-OrganizationSegment -Identity $segment.Name -ErrorAction SilentlyContinue
    if ($existing) {
        Write-Host "Segment exists: $($segment.Name)" -ForegroundColor Yellow
    } else {
        New-OrganizationSegment -Name $segment.Name -UserGroupFilter $segment.Filter
        Write-Host "Created: $($segment.Name)" -ForegroundColor Green
    }
}

Disconnect-ExchangeOnline -Confirm:$false
```

### Create Barrier Policies

```powershell
<#
.SYNOPSIS
    Creates Information Barrier policies

.EXAMPLE
    .\New-IBPolicies.ps1
#>

Write-Host "=== Create IB Policies ===" -ForegroundColor Cyan

Connect-IPPSSession

# Research-Trading barrier
New-InformationBarrierPolicy -Name "Research-Trading-Barrier" `
    -AssignedSegment "IB-Research" `
    -SegmentsBlocked "IB-Trading" `
    -State Active

# IB-Sales barrier
New-InformationBarrierPolicy -Name "IB-Sales-Barrier" `
    -AssignedSegment "IB-InvestmentBanking" `
    -SegmentsBlocked "IB-Sales" `
    -State Active

Write-Host "Policies created. Now applying..." -ForegroundColor Yellow
Start-InformationBarrierPoliciesApplication

Write-Host "Policy application started. Check status with Get-InformationBarrierPoliciesApplicationStatus"

Disconnect-ExchangeOnline -Confirm:$false
```

### Export Barrier Configuration

```powershell
<#
.SYNOPSIS
    Exports Information Barrier configuration for audit

.EXAMPLE
    .\Export-IBConfiguration.ps1
#>

param(
    [string]$OutputPath = ".\IBConfiguration"
)

Write-Host "=== Export IB Configuration ===" -ForegroundColor Cyan

Connect-IPPSSession

# Export segments
$segments = Get-OrganizationSegment
$segments | Export-Csv -Path "$OutputPath-Segments.csv" -NoTypeInformation

# Export policies
$policies = Get-InformationBarrierPolicy
$policies | Export-Csv -Path "$OutputPath-Policies.csv" -NoTypeInformation

# Check application status
$status = Get-InformationBarrierPoliciesApplicationStatus
Write-Host "Application Status: $($status.Status)"

Disconnect-ExchangeOnline -Confirm:$false

Write-Host "Export complete: $OutputPath-*.csv" -ForegroundColor Green
```

---

## Validation Script

```powershell
<#
.SYNOPSIS
    Validates Control 1.22 - Information Barriers configuration

.EXAMPLE
    .\Validate-Control-1.22.ps1
#>

Write-Host "=== Control 1.22 Validation ===" -ForegroundColor Cyan

Connect-IPPSSession

# Check 1: Segments
Write-Host "`n[Check 1] Organization Segments" -ForegroundColor Cyan
$segments = Get-OrganizationSegment
Write-Host "Segments defined: $($segments.Count)"
$segments | ForEach-Object { Write-Host "  - $($_.Name)" }

# Check 2: Policies
Write-Host "`n[Check 2] Barrier Policies" -ForegroundColor Cyan
$policies = Get-InformationBarrierPolicy
$active = $policies | Where-Object { $_.State -eq "Active" }
Write-Host "Active policies: $($active.Count)"

# Check 3: Application status
Write-Host "`n[Check 3] Application Status" -ForegroundColor Cyan
$status = Get-InformationBarrierPoliciesApplicationStatus
Write-Host "Status: $($status.Status)"

Disconnect-ExchangeOnline -Confirm:$false

Write-Host "`n=== Validation Complete ===" -ForegroundColor Cyan
```

---

[Back to Control 1.22](../../../controls/pillar-1-security/1.22-information-barriers.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
