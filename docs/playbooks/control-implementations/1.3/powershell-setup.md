# PowerShell Setup: Control 1.3 - SharePoint Content Governance and Permissions

**Last Updated:** January 2026
**Modules Required:** Microsoft.Online.SharePoint.PowerShell, Microsoft.Graph

## Prerequisites

```powershell
# Install required modules
Install-Module -Name Microsoft.Online.SharePoint.PowerShell -Force
Install-Module -Name Microsoft.Graph -Force

# Connect to SharePoint Online
$AdminUrl = "https://contoso-admin.sharepoint.com"
Connect-SPOService -Url $AdminUrl
```

---

## Site Inventory and Audit

### Get All Sites and Their Sharing Settings

```powershell
# Get all sites and their sharing settings
$Sites = Get-SPOSite -Limit All
$SiteReport = $Sites | Select-Object Url, Title, Owner, SharingCapability,
    ConditionalAccessPolicy, SensitivityLabel, LockState |
    Export-Csv "C:\Governance\SharePoint-Sites-$(Get-Date -Format 'yyyyMMdd').csv" -NoTypeInformation

Write-Host "Exported $($Sites.Count) sites to report" -ForegroundColor Green
```

---

## Configure Agent Knowledge Sites

### Restrict Sharing for Enterprise-Managed Sites

```powershell
# Configure a site for an enterprise-managed agent knowledge source
$AgentKnowledgeSite = "https://contoso.sharepoint.com/sites/Agent-CustomerService"

Set-SPOSite -Identity $AgentKnowledgeSite `
    -SharingCapability Disabled `
    -DisableSharingForNonOwners $true `
    -DefaultLinkPermission View `
    -ConditionalAccessPolicy AllowLimitedAccess `
    -LimitedAccessFileType OfficeOnlineFilesOnly

Write-Host "Configured $AgentKnowledgeSite for enterprise-managed access" -ForegroundColor Green
```

---

## Remove Overly Permissive Groups

### Remove "Everyone" Groups from Agent Sites

```powershell
# Define agent knowledge source sites
$AgentSites = @(
    "https://contoso.sharepoint.com/sites/Agent-CustomerService",
    "https://contoso.sharepoint.com/sites/Agent-Trading",
    "https://contoso.sharepoint.com/sites/Agent-Compliance"
)

foreach ($SiteUrl in $AgentSites) {
    # Get site details
    $Site = Get-SPOSite -Identity $SiteUrl -Detailed

    # Remove Everyone group if present
    try {
        Remove-SPOUser -Site $SiteUrl -LoginName "c:0(.s|true"  # Everyone
        Write-Host "Removed 'Everyone' from $SiteUrl" -ForegroundColor Yellow
    } catch {
        Write-Host "'Everyone' not found on $SiteUrl" -ForegroundColor Gray
    }

    # Remove Everyone except external users if present
    try {
        Remove-SPOUser -Site $SiteUrl -LoginName "c:0-.f|rolemanager|spo-grid-all-users/$($Site.Id)"
        Write-Host "Removed 'Everyone except external users' from $SiteUrl" -ForegroundColor Yellow
    } catch {
        Write-Host "'Everyone except external' not found on $SiteUrl" -ForegroundColor Gray
    }
}
```

---

## Permission Audit

### Generate Permission Report for Agent Sites

```powershell
# Generate permission report for agent knowledge sites
$PermissionReport = @()

foreach ($SiteUrl in $AgentSites) {
    $SiteUsers = Get-SPOUser -Site $SiteUrl -Limit All

    foreach ($User in $SiteUsers) {
        $PermissionReport += [PSCustomObject]@{
            Site = $SiteUrl
            LoginName = $User.LoginName
            DisplayName = $User.DisplayName
            IsSiteAdmin = $User.IsSiteAdmin
            Groups = ($User.Groups -join "; ")
        }
    }
}

$PermissionReport | Export-Csv "C:\Governance\AgentSites-Permissions-$(Get-Date -Format 'yyyyMMdd').csv" -NoTypeInformation
Write-Host "Permission report exported with $($PermissionReport.Count) entries" -ForegroundColor Green
```

---

## Bulk Site Configuration

### Configure Multiple Sites for FSI Compliance

```powershell
# Bulk configure sharing settings for agent sites
$SitesToConfigure = @(
    @{ Url = "https://contoso.sharepoint.com/sites/Agent-CustomerService"; Zone = "Enterprise" },
    @{ Url = "https://contoso.sharepoint.com/sites/Agent-Trading"; Zone = "Enterprise" },
    @{ Url = "https://contoso.sharepoint.com/sites/Team-Research"; Zone = "Team" }
)

foreach ($SiteConfig in $SitesToConfigure) {
    $SiteUrl = $SiteConfig.Url
    $Zone = $SiteConfig.Zone

    Write-Host "Configuring $SiteUrl (Zone: $Zone)" -ForegroundColor Cyan

    switch ($Zone) {
        "Enterprise" {
            Set-SPOSite -Identity $SiteUrl `
                -SharingCapability Disabled `
                -DisableSharingForNonOwners $true `
                -DefaultLinkPermission View
            Write-Host "  [DONE] Applied Enterprise settings" -ForegroundColor Green
        }
        "Team" {
            Set-SPOSite -Identity $SiteUrl `
                -SharingCapability ExistingExternalUserSharingOnly `
                -DisableSharingForNonOwners $false `
                -DefaultLinkPermission View
            Write-Host "  [DONE] Applied Team settings" -ForegroundColor Green
        }
        "Personal" {
            # Use tenant defaults
            Write-Host "  [SKIP] Using tenant defaults for Personal zone" -ForegroundColor Gray
        }
    }
}
```

---

## Complete Configuration Script

```powershell
<#
.SYNOPSIS
    Configures Control 1.3 - SharePoint Content Governance and Permissions

.DESCRIPTION
    This script:
    1. Audits existing SharePoint sites
    2. Configures sharing settings for agent knowledge sources
    3. Removes overly permissive groups
    4. Generates permission reports

.PARAMETER AdminUrl
    SharePoint admin center URL

.PARAMETER AgentSites
    Array of agent knowledge source site URLs

.EXAMPLE
    .\Configure-Control-1.3.ps1 -AdminUrl "https://contoso-admin.sharepoint.com"

.NOTES
    Last Updated: January 2026
    Related Control: Control 1.3 - SharePoint Content Governance
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$AdminUrl,

    [Parameter(Mandatory=$false)]
    [string[]]$AgentSites = @()
)

# Connect to SharePoint Online
Connect-SPOService -Url $AdminUrl

Write-Host "=== Control 1.3: SharePoint Content Governance ===" -ForegroundColor Cyan

# Step 1: Audit all sites
Write-Host "`nStep 1: Auditing SharePoint sites..." -ForegroundColor Cyan
$Sites = Get-SPOSite -Limit All
Write-Host "  [DONE] Found $($Sites.Count) sites" -ForegroundColor Green

# Step 2: Export site report
$ReportPath = "C:\Governance\SharePoint-Sites-$(Get-Date -Format 'yyyyMMdd').csv"
$Sites | Select-Object Url, Title, Owner, SharingCapability, SensitivityLabel |
    Export-Csv -Path $ReportPath -NoTypeInformation
Write-Host "  [DONE] Exported to $ReportPath" -ForegroundColor Green

# Step 3: Configure agent sites (if provided)
if ($AgentSites.Count -gt 0) {
    Write-Host "`nStep 2: Configuring agent knowledge sites..." -ForegroundColor Cyan
    foreach ($SiteUrl in $AgentSites) {
        Set-SPOSite -Identity $SiteUrl `
            -SharingCapability Disabled `
            -DisableSharingForNonOwners $true
        Write-Host "  [DONE] Configured $SiteUrl" -ForegroundColor Green
    }
}

# Step 4: Identify sites with "Everyone" permissions
Write-Host "`nStep 3: Checking for overly permissive sites..." -ForegroundColor Cyan
$OverlyPermissive = @()
foreach ($Site in $Sites) {
    try {
        $Users = Get-SPOUser -Site $Site.Url -Limit All -ErrorAction SilentlyContinue
        $HasEveryone = $Users | Where-Object { $_.LoginName -match "everyone|spo-grid-all-users" }
        if ($HasEveryone) {
            $OverlyPermissive += $Site.Url
        }
    } catch {
        # Skip sites we can't access
    }
}

if ($OverlyPermissive.Count -gt 0) {
    Write-Host "  [WARN] Found $($OverlyPermissive.Count) sites with broad permissions:" -ForegroundColor Yellow
    $OverlyPermissive | ForEach-Object { Write-Host "    - $_" -ForegroundColor Yellow }
} else {
    Write-Host "  [PASS] No sites with 'Everyone' permissions found" -ForegroundColor Green
}

Write-Host "`nControl 1.3 configuration complete!" -ForegroundColor Cyan
```

---

[Back to Control 1.3](../../../controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
