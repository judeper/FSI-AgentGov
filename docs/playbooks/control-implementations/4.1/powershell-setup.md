# PowerShell Setup: Control 4.1 - SharePoint Information Access Governance (IAG)

**Last Updated:** January 2026
**Modules Required:** Microsoft.Online.SharePoint.PowerShell

## Prerequisites

```powershell
# Install SharePoint Online Management Shell if not already installed
Install-Module -Name Microsoft.Online.SharePoint.PowerShell -Scope CurrentUser -Force

# Import the module
Import-Module Microsoft.Online.SharePoint.PowerShell
```

---

## Connect to SharePoint Online

```powershell
# Connect to SharePoint Online Admin Center
$AdminUrl = "https://yourtenant-admin.sharepoint.com"
Connect-SPOService -Url $AdminUrl

# Verify connection
Get-SPOTenant | Select-Object StorageQuota, ResourceQuota
```

---

## Configuration Scripts

### Get Sites with Copilot Content Restrictions

```powershell
# Get all sites and their Copilot restriction status
$AllSites = Get-SPOSite -Limit All

# Filter sites with Copilot restrictions enabled
$RestrictedSites = $AllSites | Where-Object { $_.RestrictContentOrgWideSearch -eq $true }

# Display restricted sites
$RestrictedSites | Select-Object Url, Title, RestrictContentOrgWideSearch | Format-Table -AutoSize

# Count restricted vs unrestricted
Write-Host "Total Sites: $($AllSites.Count)" -ForegroundColor Cyan
Write-Host "Restricted Sites: $($RestrictedSites.Count)" -ForegroundColor Yellow
Write-Host "Unrestricted Sites: $($AllSites.Count - $RestrictedSites.Count)" -ForegroundColor Green
```

### Set Copilot Content Restrictions for a Site

```powershell
# Enable Copilot content restriction for a specific site
$SiteUrl = "https://yourtenant.sharepoint.com/sites/FinanceConfidential"

# Restrict content from Microsoft 365 Copilot
Set-SPOSite -Identity $SiteUrl -RestrictContentOrgWideSearch $true

# Verify the setting
Get-SPOSite -Identity $SiteUrl | Select-Object Url, RestrictContentOrgWideSearch

# To disable restriction (use with caution)
# Set-SPOSite -Identity $SiteUrl -RestrictContentOrgWideSearch $false
```

### Configure Restricted SharePoint Search (RSS) - Allow-List

```powershell
# Enable Restricted SharePoint Search
Set-SPOTenant -RestrictedSearchEnabled $true

# Add sites to the allow-list
Add-SPOSearchSiteConfiguration -Sites @(
    "https://yourtenant.sharepoint.com/sites/ApprovedSite1",
    "https://yourtenant.sharepoint.com/sites/ApprovedSite2"
)

# Get current RSS configuration
Get-SPOTenant | Select-Object RestrictedSearchEnabled
Get-SPOSearchSiteConfiguration
```

### Configure Restricted Access Control (RAC)

```powershell
# Configure restricted site access (limits access to specific security groups)
$SiteUrl = "https://yourtenant.sharepoint.com/sites/MandA-ProjectAlpha"
$SecurityGroupId = "00000000-0000-0000-0000-000000000000"  # Replace with actual Entra ID group ID

# Enable restricted access
Set-SPOSite -Identity $SiteUrl -RestrictedAccessControl $true

# Add authorized security group (up to 10 groups allowed)
Set-SPOSite -Identity $SiteUrl -RestrictedAccessControlGroups $SecurityGroupId

# Add multiple groups
$GroupIds = @("group-id-1", "group-id-2", "group-id-3")
Set-SPOSite -Identity $SiteUrl -RestrictedAccessControlGroups $GroupIds

# Verify configuration
Get-SPOSite -Identity $SiteUrl | Select-Object Url, RestrictedAccessControl, RestrictedAccessControlGroups
```

### Bulk Configure Sites by Zone

```powershell
# Bulk enable Copilot restrictions for enterprise-managed sites
# Define enterprise-managed site URLs (from your governance inventory)
$EnterpriseSites = @(
    "https://yourtenant.sharepoint.com/sites/TradingData",
    "https://yourtenant.sharepoint.com/sites/CustomerPII",
    "https://yourtenant.sharepoint.com/sites/RegulatoryFilings",
    "https://yourtenant.sharepoint.com/sites/MergerAcquisition"
)

# Apply restrictions to all enterprise-managed sites
foreach ($SiteUrl in $EnterpriseSites) {
    try {
        Set-SPOSite -Identity $SiteUrl -RestrictContentOrgWideSearch $true
        Write-Host "Restricted: $SiteUrl" -ForegroundColor Green
    }
    catch {
        Write-Host "Failed to restrict: $SiteUrl - $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Verify all enterprise-managed sites are restricted
Write-Host "`nVerification Report:" -ForegroundColor Cyan
foreach ($SiteUrl in $EnterpriseSites) {
    $Site = Get-SPOSite -Identity $SiteUrl
    $Status = if ($Site.RestrictContentOrgWideSearch) { "RESTRICTED" } else { "UNRESTRICTED" }
    Write-Host "$Status - $SiteUrl" -ForegroundColor $(if ($Status -eq "RESTRICTED") { "Green" } else { "Red" })
}
```

### Export IAG Configuration Report

```powershell
# Export comprehensive IAG configuration report
$ReportDate = Get-Date -Format "yyyy-MM-dd"
$ReportPath = "C:\Reports\IAG-Configuration-$ReportDate.csv"

$AllSites = Get-SPOSite -Limit All | Select-Object `
    Url, `
    Title, `
    RestrictContentOrgWideSearch, `
    SharingCapability, `
    ConditionalAccessPolicy, `
    SensitivityLabel, `
    Owner, `
    LastContentModifiedDate

$AllSites | Export-Csv -Path $ReportPath -NoTypeInformation

Write-Host "IAG Configuration Report exported to: $ReportPath" -ForegroundColor Green
Write-Host "Total sites analyzed: $($AllSites.Count)" -ForegroundColor Cyan
```

---

## Complete Configuration Script

```powershell
<#
.SYNOPSIS
    Configures Control 4.1 - SharePoint Information Access Governance (IAG)

.DESCRIPTION
    This script configures IAG settings including:
    1. Enabling Restricted Content Discovery for sensitive sites
    2. Configuring Restricted Access Control for ethical walls
    3. Generating compliance reports

.PARAMETER AdminUrl
    The SharePoint Admin Center URL

.PARAMETER EnterpriseSitesFile
    Path to CSV file containing enterprise-managed site URLs

.EXAMPLE
    .\Configure-Control-4.1.ps1 -AdminUrl "https://contoso-admin.sharepoint.com" -EnterpriseSitesFile ".\sites.csv"

.NOTES
    Last Updated: January 2026
    Related Control: Control 4.1 - SharePoint IAG / RCD
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$AdminUrl,

    [Parameter(Mandatory=$false)]
    [string]$EnterpriseSitesFile
)

try {
    # Connect to SharePoint
    Connect-SPOService -Url $AdminUrl

    Write-Host "Configuring Control 4.1 for tenant: $AdminUrl" -ForegroundColor Cyan

    # Get current state
    $AllSites = Get-SPOSite -Limit All
    $CurrentRestricted = ($AllSites | Where-Object { $_.RestrictContentOrgWideSearch -eq $true }).Count
    Write-Host "Current restricted sites: $CurrentRestricted / $($AllSites.Count)" -ForegroundColor Yellow

    # If sites file provided, configure those sites
    if ($EnterpriseSitesFile -and (Test-Path $EnterpriseSitesFile)) {
        $SitesToRestrict = Import-Csv -Path $EnterpriseSitesFile

        foreach ($Site in $SitesToRestrict) {
            try {
                Set-SPOSite -Identity $Site.Url -RestrictContentOrgWideSearch $true
                Write-Host "  [DONE] Restricted: $($Site.Url)" -ForegroundColor Green
            }
            catch {
                Write-Host "  [FAIL] $($Site.Url): $($_.Exception.Message)" -ForegroundColor Red
            }
        }
    }

    # Generate summary
    $UpdatedSites = Get-SPOSite -Limit All
    $NewRestricted = ($UpdatedSites | Where-Object { $_.RestrictContentOrgWideSearch -eq $true }).Count

    Write-Host "`nControl 4.1 configuration complete!" -ForegroundColor Cyan
    Write-Host "Restricted sites: $CurrentRestricted -> $NewRestricted" -ForegroundColor Green

    Write-Host "`n[PASS] Control 4.1 configuration completed successfully" -ForegroundColor Green
}
catch {
    Write-Host "[FAIL] Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "[INFO] Stack trace: $($_.ScriptStackTrace)" -ForegroundColor Yellow
    exit 1
}
finally {
    # Cleanup SharePoint connection
    if (Get-SPOSite -Limit 1 -ErrorAction SilentlyContinue) {
        Disconnect-SPOService -ErrorAction SilentlyContinue
    }
}
```

---

[Back to Control 4.1](../../../controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
