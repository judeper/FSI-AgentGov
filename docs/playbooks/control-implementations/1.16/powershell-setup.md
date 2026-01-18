# PowerShell Setup: Control 1.16 - Information Rights Management (IRM)

**Last Updated:** January 2026
**Modules Required:** AIPService, PnP.PowerShell

## Prerequisites

```powershell
# Install required modules
Install-Module -Name AIPService -Force -Scope CurrentUser
Install-Module -Name PnP.PowerShell -Force -Scope CurrentUser
```

---

## Automated Scripts

### Verify Azure RMS Status

```powershell
<#
.SYNOPSIS
    Verifies Azure Rights Management Service status

.EXAMPLE
    .\Test-AzureRMS.ps1
#>

Write-Host "=== Azure RMS Status Check ===" -ForegroundColor Cyan

# Connect to AIP Service
Connect-AipService

# Get service status
$status = Get-AipService

Write-Host "Azure RMS Status: $status"

if ($status -eq "Enabled") {
    Write-Host "[PASS] Azure RMS is activated" -ForegroundColor Green
} else {
    Write-Host "[FAIL] Azure RMS is not activated" -ForegroundColor Red
    Write-Host "Run: Enable-AipService to activate"
}

# Get configuration
$config = Get-AipServiceConfiguration
Write-Host "`nConfiguration:"
Write-Host "  Licensing URL: $($config.LicensingIntranetDistributionPointUrl)"
Write-Host "  Certification URL: $($config.CertificationIntranetDistributionPointUrl)"

Disconnect-AipService
```

### Enable IRM on SharePoint Library

```powershell
<#
.SYNOPSIS
    Enables IRM on SharePoint document library

.DESCRIPTION
    Configures Information Rights Management settings for a document library

.EXAMPLE
    .\Enable-LibraryIRM.ps1 -SiteUrl "https://tenant.sharepoint.com/sites/HR" -LibraryName "Documents"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$SiteUrl,
    [Parameter(Mandatory=$true)]
    [string]$LibraryName,
    [int]$OfflineDays = 14,
    [switch]$BlockPrint,
    [switch]$BlockCopy
)

Write-Host "=== Enable IRM on Library ===" -ForegroundColor Cyan

# Connect to SharePoint
Connect-PnPOnline -Url $SiteUrl -Interactive

# Get the library
$library = Get-PnPList -Identity $LibraryName

if (-not $library) {
    Write-Host "[FAIL] Library not found: $LibraryName" -ForegroundColor Red
    exit 1
}

# Enable IRM
Set-PnPList -Identity $LibraryName -IrmEnabled $true

# Configure IRM settings
$irmSettings = @{
    "IrmEnabled" = $true
    "IrmExpire" = $true
    "IrmReject" = $true
}

Write-Host "[PASS] IRM enabled on library: $LibraryName" -ForegroundColor Green
Write-Host "  Offline days: $OfflineDays"
Write-Host "  Block print: $BlockPrint"
Write-Host "  Block copy: $BlockCopy"

Disconnect-PnPOnline
```

### Export IRM Configuration Report

```powershell
<#
.SYNOPSIS
    Exports IRM configuration status for all SharePoint sites

.EXAMPLE
    .\Export-IRMReport.ps1 -AdminUrl "https://tenant-admin.sharepoint.com"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$AdminUrl,
    [string]$OutputPath = ".\IRMReport.csv"
)

Write-Host "=== IRM Configuration Report ===" -ForegroundColor Cyan

# Connect to SharePoint Admin
Connect-PnPOnline -Url $AdminUrl -Interactive

# Get all sites
$sites = Get-PnPTenantSite -Detailed

$report = @()

foreach ($site in $sites) {
    Write-Host "Checking: $($site.Url)" -ForegroundColor Yellow

    try {
        Connect-PnPOnline -Url $site.Url -Interactive

        $lists = Get-PnPList | Where-Object { $_.BaseTemplate -eq 101 } # Document libraries

        foreach ($list in $lists) {
            $report += [PSCustomObject]@{
                SiteUrl = $site.Url
                LibraryName = $list.Title
                IRMEnabled = $list.IrmEnabled
                ItemCount = $list.ItemCount
                LastModified = $list.LastItemModifiedDate
            }
        }
    }
    catch {
        Write-Host "  Error accessing site" -ForegroundColor Red
    }
}

$report | Export-Csv -Path $OutputPath -NoTypeInformation
Write-Host "`nReport exported to: $OutputPath" -ForegroundColor Green

# Summary
$irmEnabled = ($report | Where-Object { $_.IRMEnabled -eq $true }).Count
$irmDisabled = ($report | Where-Object { $_.IRMEnabled -eq $false }).Count
Write-Host "`nSummary:"
Write-Host "  IRM Enabled: $irmEnabled libraries"
Write-Host "  IRM Disabled: $irmDisabled libraries"
```

---

## Validation Script

```powershell
<#
.SYNOPSIS
    Validates Control 1.16 - IRM configuration

.EXAMPLE
    .\Validate-Control-1.16.ps1
#>

Write-Host "=== Control 1.16 Validation ===" -ForegroundColor Cyan

# Check 1: Azure RMS Status
Write-Host "`n[Check 1] Azure RMS Status" -ForegroundColor Cyan
Connect-AipService
$status = Get-AipService
if ($status -eq "Enabled") {
    Write-Host "[PASS] Azure RMS is activated" -ForegroundColor Green
} else {
    Write-Host "[FAIL] Azure RMS is not activated" -ForegroundColor Red
}
Disconnect-AipService

# Check 2: Sensitivity Labels
Write-Host "`n[Check 2] Sensitivity Labels with Encryption" -ForegroundColor Cyan
Write-Host "[INFO] Verify in Purview portal that IRM-enabled labels exist"

# Check 3: SharePoint IRM
Write-Host "`n[Check 3] SharePoint Library IRM" -ForegroundColor Cyan
Write-Host "[INFO] Run Export-IRMReport.ps1 to audit library IRM status"

# Check 4: Document Tracking
Write-Host "`n[Check 4] Document Tracking" -ForegroundColor Cyan
Write-Host "[INFO] Verify tracking is enabled in Purview portal"

Write-Host "`n=== Validation Complete ===" -ForegroundColor Cyan
```

---

[Back to Control 1.16](../../../controls/pillar-1-security/1.16-information-rights-management-irm-for-documents.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
