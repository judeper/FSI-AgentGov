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
Connect-SPOService -Url "https://tenant-admin.sharepoint.com"
```

---

## Inventory Sites with Copilot Status

```powershell
# Get all non-personal sites with Copilot exclusion status
$sites = Get-SPOSite -Limit All | Where-Object { $_.Template -notlike "*SPSPERS*" }

$siteInventory = $sites | ForEach-Object {
    [PSCustomObject]@{
        Url = $_.Url
        Title = $_.Title
        RestrictedFromCopilot = $_.RestrictContentOrgWideSearchAndCopilot
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
Set-SPOSite -Identity "https://tenant.sharepoint.com/sites/DraftDocuments" `
    -RestrictContentOrgWideSearchAndCopilot $true

# Verify configuration
Get-SPOSite -Identity "https://tenant.sharepoint.com/sites/DraftDocuments" |
    Select-Object Url, RestrictContentOrgWideSearchAndCopilot
```

---

## Bulk Exclude Draft Sites

```powershell
# Exclude all sites with "Draft" in URL
$draftSites = Get-SPOSite -Limit All | Where-Object { $_.Url -like "*draft*" }
foreach ($site in $draftSites) {
    Set-SPOSite -Identity $site.Url -RestrictContentOrgWideSearchAndCopilot $true
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
    Set-SPOSite -Identity $site.Url -RestrictContentOrgWideSearchAndCopilot $true
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
Set-CopilotReadyStatus -SiteUrl "https://tenant.sharepoint.com/sites/ProductKnowledge" `
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
                RestrictedFromCopilot = $site.RestrictContentOrgWideSearchAndCopilot
            }
        } catch {
            Write-Warning "Could not check $($site.Url): $_"
        }
    }

    return $results
}

# Get all sites with CopilotReady status
$copilotStatus = Get-CopilotReadySites -AdminUrl "https://tenant-admin.sharepoint.com"
$copilotStatus | Export-Csv -Path "CopilotReady-Status.csv" -NoTypeInformation
```

---

## Generate Grounding Scope Summary

```powershell
# Create summary report
$allSites = Get-SPOSite -Limit All | Where-Object { $_.Template -notlike "*SPSPERS*" }

$summary = @{
    TotalSites = $allSites.Count
    IndexedSites = ($allSites | Where-Object { -not $_.RestrictContentOrgWideSearchAndCopilot }).Count
    ExcludedSites = ($allSites | Where-Object { $_.RestrictContentOrgWideSearchAndCopilot }).Count
}

Write-Host "`nGrounding Scope Summary:" -ForegroundColor Cyan
Write-Host "  Total Sites: $($summary.TotalSites)"
Write-Host "  Indexed (Copilot can access): $($summary.IndexedSites)" -ForegroundColor Green
Write-Host "  Excluded (Copilot cannot access): $($summary.ExcludedSites)" -ForegroundColor Yellow
```

---

*Updated: January 2026 | Version: v1.1*
