# Control 4.6: Grounding Scope Governance - PowerShell Setup

> This playbook provides PowerShell automation guidance for [Control 4.6](../../../controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md).

---

## Prerequisites

```powershell
# Install required modules
Install-Module -Name Microsoft.Online.SharePoint.PowerShell -Force
Install-Module -Name PnP.PowerShell -Scope CurrentUser
```

---

## Connect to SharePoint

```powershell
Connect-SPOService -Url "https://contoso-admin.sharepoint.com"
```

---

!!! note "Parameter Status"
    `RestrictContentOrgWideSearch` is the current GA parameter for site-level search/Copilot
    restrictions. Copilot-specific parameters are in preview and subject to change.

## Inventory Sites with Copilot Status

```powershell
# Get all non-personal sites with Copilot exclusion status
$sites = Get-SPOSite -Limit All | Where-Object { $_.Template -notlike "*SPSPERS*" }

$siteInventory = $sites | ForEach-Object {
    [PSCustomObject]@{
        Url = $_.Url
        Title = $_.Title
        RestrictedFromCopilot = $_.RestrictContentOrgWideSearch
        SensitivityLabel = $_.SensitivityLabel
        LastModified = $_.LastContentModifiedDate
        StorageUsedGB = [math]::Round($_.StorageUsageCurrent / 1024, 2)
        ContentCategory = switch -Wildcard ($_.Url) {
            "*draft*" { "Draft" }
            "*archive*" { "Archive" }
            "*personal*" { "Personal" }
            "*test*" { "Test" }
            default { "Production" }
        }
    }
}

$siteInventory | Export-Csv -Path "Site-Copilot-Inventory.csv" -NoTypeInformation
```

---

## Exclude Sites from Semantic Index

```powershell
# Exclude specific site from Copilot/Semantic Index
Set-SPOSite -Identity "https://contoso.sharepoint.com/sites/DraftDocuments" `
    -RestrictContentOrgWideSearch $true

# Verify configuration
Get-SPOSite -Identity "https://contoso.sharepoint.com/sites/DraftDocuments" |
    Select-Object Url, RestrictContentOrgWideSearch
```

---

## Bulk Exclude Draft Sites

```powershell
# Exclude all sites with "Draft" in URL
$draftSites = Get-SPOSite -Limit All | Where-Object { $_.Url -like "*draft*" }
foreach ($site in $draftSites) {
    Set-SPOSite -Identity $site.Url -RestrictContentOrgWideSearch $true
    Write-Host "Excluded: $($site.Url)" -ForegroundColor Yellow
}
```

---

## Bulk Exclude Archive Sites

```powershell
# Exclude archive sites
$archiveSites = Get-SPOSite -Limit All | Where-Object {
    $_.Url -like "*archive*" -or $_.Title -like "*Archive*"
}
foreach ($site in $archiveSites) {
    Set-SPOSite -Identity $site.Url -RestrictContentOrgWideSearch $true
    Write-Host "Excluded archive: $($site.Url)" -ForegroundColor Yellow
}
```

---

## Set CopilotReady Metadata

```powershell
# Using PnP PowerShell to set site property bag
function Set-CopilotReadyStatus {
    param(
        [string]$SiteUrl,
        [bool]$IsReady,
        [string]$ApprovedBy,
        [datetime]$ApprovedDate
    )

    Connect-PnPOnline -Url $SiteUrl -Interactive

    # Set site property bag values
    Set-PnPPropertyBagValue -Key "CopilotReady" -Value $IsReady.ToString()
    Set-PnPPropertyBagValue -Key "CopilotReadyApprovedBy" -Value $ApprovedBy
    Set-PnPPropertyBagValue -Key "CopilotReadyApprovedDate" -Value $ApprovedDate.ToString("yyyy-MM-dd")

    Write-Host "Site $SiteUrl marked as CopilotReady: $IsReady" -ForegroundColor Green
}

# Mark site as approved for Copilot
Set-CopilotReadyStatus -SiteUrl "https://contoso.sharepoint.com/sites/ProductKnowledge" `
    -IsReady $true -ApprovedBy "compliance@contoso.com" -ApprovedDate (Get-Date)
```

---

## Query CopilotReady Sites

```powershell
function Get-CopilotReadySites {
    param([string]$AdminUrl)

    Connect-SPOService -Url $AdminUrl
    $sites = Get-SPOSite -Limit All | Where-Object { $_.Template -notlike "*SPSPERS*" }

    $results = @()
    foreach ($site in $sites) {
        try {
            Connect-PnPOnline -Url $site.Url -Interactive
            $copilotReady = Get-PnPPropertyBag -Key "CopilotReady"

            $results += [PSCustomObject]@{
                SiteUrl = $site.Url
                Title = $site.Title
                CopilotReady = if ($copilotReady) { $copilotReady } else { "Not Set" }
                RestrictedFromCopilot = $site.RestrictContentOrgWideSearch
            }
        } catch {
            Write-Warning "Could not check $($site.Url): $_"
        }
    }

    return $results
}

# Get all sites with CopilotReady status
$copilotStatus = Get-CopilotReadySites -AdminUrl "https://contoso-admin.sharepoint.com"
$copilotStatus | Export-Csv -Path "CopilotReady-Status.csv" -NoTypeInformation
```

---

## Generate Grounding Scope Summary

```powershell
# Create summary report
$allSites = Get-SPOSite -Limit All | Where-Object { $_.Template -notlike "*SPSPERS*" }

$summary = @{
    TotalSites = $allSites.Count
    IndexedSites = ($allSites | Where-Object { -not $_.RestrictContentOrgWideSearch }).Count
    ExcludedSites = ($allSites | Where-Object { $_.RestrictContentOrgWideSearch }).Count
}

Write-Host "`nGrounding Scope Summary:" -ForegroundColor Cyan
Write-Host "  Total Sites: $($summary.TotalSites)"
Write-Host "  Indexed (Copilot can access): $($summary.IndexedSites)" -ForegroundColor Green
Write-Host "  Excluded (Copilot cannot access): $($summary.ExcludedSites)" -ForegroundColor Yellow
```

---

## Configure SharePoint Restricted Search

!!! info "GA Feature"
    SharePoint Restricted Search is generally available. These cmdlets are current as of January 2026. Verify cmdlet names with `Get-Command *RestrictedSearch*` if errors occur.

### Enable Restricted Search

```powershell
# Enable Restricted Search for tenant
Set-SPOTenant -EnableRestrictedSearchAllList $true

# Verify status
Get-SPOTenant | Select-Object EnableRestrictedSearchAllList
```

### Add Sites to Allowed List

```powershell
# Add single site to allowed list
Add-SPOTenantRestrictedSearchAllowedList -SiteUrl "https://contoso.sharepoint.com/sites/ApprovedContent"

# Verify addition
Get-SPOTenantRestrictedSearchAllowedList | Where-Object { $_ -like "*ApprovedContent*" }
```

### Bulk Add Sites from CSV

```powershell
# CSV format: SiteUrl, BusinessJustification, ApprovedBy, ApprovedDate
$approvedSites = Import-Csv -Path "ApprovedSites.csv"

foreach ($site in $approvedSites) {
    try {
        Add-SPOTenantRestrictedSearchAllowedList -SiteUrl $site.SiteUrl
        Write-Host "Added to allowed list: $($site.SiteUrl)" -ForegroundColor Green
    } catch {
        Write-Host "Failed to add $($site.SiteUrl): $_" -ForegroundColor Red
    }
}
```

### Export Current Allowed List for Compliance Evidence

```powershell
# Export allowed list with metadata
$allowedSites = Get-SPOTenantRestrictedSearchAllowedList

$allowedListReport = $allowedSites | ForEach-Object {
    $siteUrl = $_
    $siteDetails = Get-SPOSite -Identity $siteUrl -ErrorAction SilentlyContinue

    [PSCustomObject]@{
        SiteUrl = $siteUrl
        Title = if ($siteDetails) { $siteDetails.Title } else { "N/A" }
        Owner = if ($siteDetails) { $siteDetails.Owner } else { "N/A" }
        LastModified = if ($siteDetails) { $siteDetails.LastContentModifiedDate } else { "N/A" }
        ExportDate = Get-Date -Format "yyyy-MM-dd"
    }
}

$allowedListReport | Export-Csv -Path "RestrictedSearch-AllowedList-$(Get-Date -Format 'yyyy-MM-dd').csv" -NoTypeInformation
```

### Remove Site from Allowed List

```powershell
# Remove site from allowed list (after governance approval)
Remove-SPOTenantRestrictedSearchAllowedList -SiteUrl "https://contoso.sharepoint.com/sites/OldContent"

# Verify removal
Get-SPOTenantRestrictedSearchAllowedList | Where-Object { $_ -like "*OldContent*" }
```

### Audit Allowed List Count (100-Site Limit)

```powershell
# Check current count against 100-site limit
$allowedCount = (Get-SPOTenantRestrictedSearchAllowedList).Count

Write-Host "`nRestricted Search Allowed List Status:" -ForegroundColor Cyan
Write-Host "  Current sites: $allowedCount / 100" -ForegroundColor $(if ($allowedCount -ge 90) { "Yellow" } else { "Green" })
Write-Host "  Remaining capacity: $(100 - $allowedCount) sites" -ForegroundColor $(if ($allowedCount -ge 90) { "Yellow" } else { "Green" })

if ($allowedCount -ge 90) {
    Write-Host "`nWARNING: Approaching 100-site limit. Review and prioritize sites." -ForegroundColor Red
}
```

### Disable Restricted Search

```powershell
# Disable Restricted Search (returns to RCD-only governance)
Set-SPOTenant -EnableRestrictedSearchAllList $false

# Note: This does NOT clear the allowed list - sites remain configured
# Users: Verify this is the intended behavior before disabling
```

---

[Back to Control 4.6](../../../controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: April 2026 | Version: v1.3*
