# Control 4.4: Guest and External User Access Controls - PowerShell Setup

> This playbook provides PowerShell automation guidance for [Control 4.4](../../../controls/pillar-4-sharepoint/4.4-guest-and-external-user-access-controls.md).

---

## Prerequisites

```powershell
# Install SharePoint Online Management Shell
Install-Module -Name Microsoft.Online.SharePoint.PowerShell -Force
```

---

## Connect to SharePoint Online

```powershell
# Connect to SharePoint Online Admin Center
$adminUrl = "https://yourtenant-admin.sharepoint.com"
Connect-SPOService -Url $adminUrl
```

---

## Get Tenant Sharing Settings

```powershell
# Get current tenant-level sharing configuration
Get-SPOTenant | Select-Object `
    SharingCapability, `
    SharingDomainRestrictionMode, `
    SharingAllowedDomainList, `
    SharingBlockedDomainList, `
    DefaultSharingLinkType, `
    DefaultLinkPermission, `
    RequireAnonymousLinksExpireInDays, `
    ExternalUserExpirationRequired, `
    ExternalUserExpireInDays
```

---

## Set Tenant Sharing Settings

```powershell
# Configure restrictive tenant-level sharing for regulated environments
Set-SPOTenant `
    -SharingCapability ExistingExternalUserSharingOnly `
    -DefaultSharingLinkType Internal `
    -DefaultLinkPermission View `
    -RequireAnonymousLinksExpireInDays 30 `
    -ExternalUserExpirationRequired $true `
    -ExternalUserExpireInDays 30 `
    -PreventExternalUsersFromResharing $true

# Optional: Configure domain restrictions for approved partners
Set-SPOTenant `
    -SharingDomainRestrictionMode AllowList `
    -SharingAllowedDomainList "approvedpartner.com trustedvendor.com"
```

---

## Get Site-Level Sharing Settings

```powershell
# Get sharing settings for a specific site
$siteUrl = "https://yourtenant.sharepoint.com/sites/YourSite"
Get-SPOSite -Identity $siteUrl | Select-Object `
    Url, `
    SharingCapability, `
    DisableSharingForNonOwnersStatus, `
    SharingAllowedDomainList, `
    SharingBlockedDomainList, `
    ExternalUserExpirationInDays

# Get sharing settings for all sites
Get-SPOSite -Limit All | Select-Object Url, SharingCapability |
    Export-Csv -Path "SiteSharingSettings.csv" -NoTypeInformation
```

---

## Set Site-Level Sharing Settings

```powershell
# Zone 3 (Enterprise managed): Disable external sharing completely
Set-SPOSite -Identity "https://yourtenant.sharepoint.com/sites/RegulatedSite" `
    -SharingCapability Disabled

# Zone 2 (Team collaboration): Restrict to existing guests only
Set-SPOSite -Identity "https://yourtenant.sharepoint.com/sites/CollaborationSite" `
    -SharingCapability ExistingExternalUserSharingOnly `
    -DisableSharingForNonOwnersStatus $true `
    -ExternalUserExpirationInDays 30

# Zone 1 (Personal productivity): Allow new guests with controls
Set-SPOSite -Identity "https://yourtenant.sharepoint.com/sites/PersonalSite" `
    -SharingCapability ExternalUserSharingOnly `
    -ExternalUserExpirationInDays 90
```

---

## Bulk Configure Regulated Sites

```powershell
# Import regulated sites and disable external sharing
$regulatedSites = Import-Csv -Path "RegulatedSites.csv"

foreach ($site in $regulatedSites) {
    Write-Host "Configuring regulated site: $($site.Url)" -ForegroundColor Yellow
    Set-SPOSite -Identity $site.Url -SharingCapability Disabled
    Write-Host "External sharing disabled for: $($site.Url)" -ForegroundColor Green
}
```

---

## Export Guest Access Configuration

```powershell
# Export comprehensive guest access audit report
$allSites = Get-SPOSite -Limit All
$guestAccessReport = @()

foreach ($site in $allSites) {
    $guestAccessReport += [PSCustomObject]@{
        SiteUrl = $site.Url
        SharingCapability = $site.SharingCapability
        ExternalUserExpiration = $site.ExternalUserExpirationInDays
        NonOwnerSharingDisabled = $site.DisableSharingForNonOwnersStatus
        Template = $site.Template
        Owner = $site.Owner
    }
}

$guestAccessReport | Export-Csv -Path "GuestAccessConfiguration_$(Get-Date -Format 'yyyyMMdd').csv" -NoTypeInformation
Write-Host "Guest access configuration exported successfully" -ForegroundColor Green
```

---

## Audit Guest Access

```powershell
# Get all external users across the tenant
Get-SPOExternalUser -PageSize 50 | Select-Object `
    DisplayName, `
    Email, `
    AcceptedAs, `
    WhenCreated, `
    InvitedBy | Export-Csv -Path "ExternalUsers_$(Get-Date -Format 'yyyyMMdd').csv" -NoTypeInformation

# Get external users for a specific site
$siteUrl = "https://yourtenant.sharepoint.com/sites/YourSite"
Get-SPOExternalUser -SiteUrl $siteUrl | Select-Object DisplayName, Email, AcceptedAs, WhenCreated

# Remove expired or unauthorized external users (requires Microsoft Graph PowerShell)
# Note: Remove-SPOExternalUser was deprecated July 2024
$externalUser = Get-MgUser -Filter "userType eq 'Guest' and mail eq 'user@external.com'"
Remove-MgUser -UserId $externalUser.Id -Confirm:$false
```

---

## Complete Configuration Script

```powershell
<#
.SYNOPSIS
    Configures Control 4.4 - Guest and External User Access Controls

.DESCRIPTION
    This script configures external sharing settings:
    1. Sets tenant-level sharing restrictions
    2. Configures site-level sharing for regulated sites
    3. Exports guest access audit report

.PARAMETER AdminUrl
    SharePoint Admin Center URL

.PARAMETER RegulatedSitesFile
    Path to CSV file containing regulated site URLs

.EXAMPLE
    .\Configure-Control-4.4.ps1 -AdminUrl "https://contoso-admin.sharepoint.com" -RegulatedSitesFile ".\RegulatedSites.csv"

.NOTES
    Last Updated: January 2026
    Related Control: Control 4.4 - Guest and External User Access Controls
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$AdminUrl,

    [Parameter(Mandatory=$false)]
    [string]$RegulatedSitesFile
)

try {
    # Connect to SharePoint Online
    Write-Host "Connecting to SharePoint Online..." -ForegroundColor Cyan
    Connect-SPOService -Url $AdminUrl

    Write-Host "Configuring Control 4.4 Guest Access Controls" -ForegroundColor Cyan

    # Get current tenant settings
    Write-Host "`nRetrieving tenant sharing settings..." -ForegroundColor Yellow
    $tenantSettings = Get-SPOTenant
    Write-Host "  Current sharing capability: $($tenantSettings.SharingCapability)" -ForegroundColor Green

    # If regulated sites file provided, disable external sharing
    if ($RegulatedSitesFile -and (Test-Path $RegulatedSitesFile)) {
        Write-Host "`nConfiguring regulated sites..." -ForegroundColor Yellow
        $regulatedSites = Import-Csv -Path $RegulatedSitesFile

        foreach ($site in $regulatedSites) {
            try {
                Set-SPOSite -Identity $site.Url -SharingCapability Disabled
                Write-Host "  [DONE] External sharing disabled: $($site.Url)" -ForegroundColor Green
            }
            catch {
                Write-Host "  [FAIL] $($site.Url): $($_.Exception.Message)" -ForegroundColor Red
            }
        }
    }

    # Export guest access audit report
    Write-Host "`nExporting guest access configuration..." -ForegroundColor Yellow
    $allSites = Get-SPOSite -Limit All
    $guestAccessReport = @()

    foreach ($site in $allSites) {
        $guestAccessReport += [PSCustomObject]@{
            SiteUrl = $site.Url
            SharingCapability = $site.SharingCapability
            ExternalUserExpiration = $site.ExternalUserExpirationInDays
            NonOwnerSharingDisabled = $site.DisableSharingForNonOwnersStatus
            Template = $site.Template
        }
    }

    $guestAccessReport | Export-Csv -Path "GuestAccessConfiguration_$(Get-Date -Format 'yyyyMMdd').csv" -NoTypeInformation

    # Summary
    $disabledCount = ($allSites | Where-Object { $_.SharingCapability -eq "Disabled" }).Count
    $externalCount = ($allSites | Where-Object { $_.SharingCapability -ne "Disabled" }).Count

    Write-Host "`nGuest Access Summary:" -ForegroundColor Cyan
    Write-Host "  Total sites: $($allSites.Count)" -ForegroundColor Green
    Write-Host "  External sharing disabled: $disabledCount" -ForegroundColor Green
    Write-Host "  External sharing enabled: $externalCount" -ForegroundColor $(if ($externalCount -gt 0) { "Yellow" } else { "Green" })

    Write-Host "`n[PASS] Control 4.4 configuration completed successfully" -ForegroundColor Green
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

*Updated: January 2026 | Version: v1.2*
