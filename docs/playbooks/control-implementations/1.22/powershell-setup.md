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

## Complete Configuration Script

```powershell
<#
.SYNOPSIS
    Configures Control 1.22 - Information Barriers

.DESCRIPTION
    This script creates organization segments and Information Barrier policies
    for FSI Chinese wall requirements.

.PARAMETER Segments
    Hashtable array of segments to create with Name and Filter properties

.PARAMETER Barriers
    Hashtable array of barrier policies to create

.PARAMETER ExportPath
    Path for exports (default: current directory)

.EXAMPLE
    .\Configure-Control-1.22.ps1

.NOTES
    Last Updated: January 2026
    Related Control: Control 1.22 - Information Barriers
#>

param(
    [string]$ExportPath = "."
)

try {
    # Connect to Security & Compliance
    Write-Host "Connecting to Security & Compliance Center..." -ForegroundColor Cyan
    Connect-IPPSSession

    Write-Host "Configuring Control 1.22: Information Barriers" -ForegroundColor Cyan

    # Step 1: Create organization segments
    Write-Host "`n[Step 1] Creating organization segments..." -ForegroundColor Yellow
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
            Write-Host "  [EXISTS] $($segment.Name)" -ForegroundColor Yellow
        } else {
            New-OrganizationSegment -Name $segment.Name -UserGroupFilter $segment.Filter
            Write-Host "  [CREATED] $($segment.Name)" -ForegroundColor Green
        }
    }

    # Step 2: Create barrier policies
    Write-Host "`n[Step 2] Creating Information Barrier policies..." -ForegroundColor Yellow
    $barriers = @(
        @{Name="Research-Trading-Barrier"; Assigned="IB-Research"; Blocked="IB-Trading"},
        @{Name="IB-Sales-Barrier"; Assigned="IB-InvestmentBanking"; Blocked="IB-Sales"}
    )

    foreach ($barrier in $barriers) {
        $existing = Get-InformationBarrierPolicy -Identity $barrier.Name -ErrorAction SilentlyContinue
        if ($existing) {
            Write-Host "  [EXISTS] $($barrier.Name)" -ForegroundColor Yellow
        } else {
            New-InformationBarrierPolicy -Name $barrier.Name `
                -AssignedSegment $barrier.Assigned `
                -SegmentsBlocked $barrier.Blocked `
                -State Active
            Write-Host "  [CREATED] $($barrier.Name)" -ForegroundColor Green
        }
    }

    # Step 3: Apply policies
    Write-Host "`n[Step 3] Applying Information Barrier policies..." -ForegroundColor Yellow
    Start-InformationBarrierPoliciesApplication
    Write-Host "  Policy application started" -ForegroundColor Green

    # Step 4: Check application status
    Write-Host "`n[Step 4] Checking application status..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5  # Brief wait for status update
    $status = Get-InformationBarrierPoliciesApplicationStatus
    Write-Host "  Status: $($status.Status)" -ForegroundColor Green

    # Step 5: Export configuration
    Write-Host "`n[Step 5] Exporting configuration for compliance evidence..." -ForegroundColor Yellow

    $allSegments = Get-OrganizationSegment
    $segmentFile = Join-Path $ExportPath "IB-Segments-$(Get-Date -Format 'yyyyMMdd').csv"
    $allSegments | Select-Object Name, UserGroupFilter, CreatedDateTime |
        Export-Csv -Path $segmentFile -NoTypeInformation
    Write-Host "  Segments exported to: $segmentFile" -ForegroundColor Green

    $allPolicies = Get-InformationBarrierPolicy
    $policyFile = Join-Path $ExportPath "IB-Policies-$(Get-Date -Format 'yyyyMMdd').csv"
    $allPolicies | Select-Object Name, AssignedSegment, SegmentsBlocked, State |
        Export-Csv -Path $policyFile -NoTypeInformation
    Write-Host "  Policies exported to: $policyFile" -ForegroundColor Green

    Write-Host "`n[PASS] Control 1.22 configuration completed successfully" -ForegroundColor Green
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

[Back to Control 1.22](../../../controls/pillar-1-security/1.22-information-barriers.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
