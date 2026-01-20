# Control 4.7: Microsoft 365 Copilot Data Governance - PowerShell Setup

> This playbook provides PowerShell automation guidance for [Control 4.7](../../../controls/pillar-4-sharepoint/4.7-microsoft-365-copilot-data-governance.md).

---

## Prerequisites

```powershell
# Install required modules
Install-Module -Name Microsoft.Graph -Scope CurrentUser
Install-Module -Name Microsoft.Online.SharePoint.PowerShell -Force
```

---

## Connect to Services

```powershell
# Connect to Microsoft Graph
Connect-MgGraph -Scopes "User.Read.All", "Organization.Read.All", "Application.Read.All"

# Connect to SharePoint Online
Connect-SPOService -Url "https://tenant-admin.sharepoint.com"
```

---

## Inventory Copilot Licenses

```powershell
# Get users with Copilot licenses
# Note: SKU ID may vary - verify for your tenant
$licensedUsers = Get-MgUser -Filter "assignedLicenses/any()" -All |
    Where-Object {
        $_.AssignedLicenses | Where-Object {
            $_.SkuId -match "copilot" -or $_.SkuId -match "Copilot"
        }
    }

Write-Host "Found $($licensedUsers.Count) users with potential Copilot licenses"

# Export for documentation
$licensedUsers | Select-Object DisplayName, UserPrincipalName, Id |
    Export-Csv -Path "Copilot-Licensed-Users.csv" -NoTypeInformation
```

---

## Audit Content Exclusions

```powershell
# Get all sites with Copilot exclusion status
$allSites = Get-SPOSite -Limit All | Where-Object { $_.Template -notlike "*SPSPERS*" }

$siteAudit = $allSites | ForEach-Object {
    [PSCustomObject]@{
        Url = $_.Url
        Title = $_.Title
        RestrictedFromCopilot = $_.RestrictContentOrgWideSearchAndCopilot
        SensitivityLabel = $_.SensitivityLabel
        StorageUsedGB = [math]::Round($_.StorageUsageCurrent / 1024, 2)
    }
}

$siteAudit | Export-Csv -Path "Site-Copilot-Status.csv" -NoTypeInformation

# Count summary
$excludedCount = ($siteAudit | Where-Object { $_.RestrictedFromCopilot -eq $true }).Count
$includedCount = ($siteAudit | Where-Object { $_.RestrictedFromCopilot -eq $false }).Count

Write-Host "Sites excluded from Copilot: $excludedCount"
Write-Host "Sites accessible by Copilot: $includedCount"
```

---

## Exclude Sensitive Sites

```powershell
# Exclude sensitive sites from Copilot
$sensitiveSites = @(
    "https://tenant.sharepoint.com/sites/ExecutiveCompensation",
    "https://tenant.sharepoint.com/sites/MergerTarget",
    "https://tenant.sharepoint.com/sites/LegalHold",
    "https://tenant.sharepoint.com/sites/ComplianceInvestigations"
)

foreach ($siteUrl in $sensitiveSites) {
    Set-SPOSite -Identity $siteUrl -RestrictContentOrgWideSearchAndCopilot $true
    Write-Host "Excluded from Copilot: $siteUrl" -ForegroundColor Yellow
}

# Verify exclusions
foreach ($siteUrl in $sensitiveSites) {
    $site = Get-SPOSite -Identity $siteUrl
    Write-Host "$siteUrl - RCD Enabled: $($site.RestrictContentOrgWideSearchAndCopilot)"
}
```

---

## Audit Integrated Apps and Plugins

```powershell
# List integrated apps and plugins
$apps = Get-MgServicePrincipal -All |
    Where-Object { $_.Tags -contains "WindowsAzureActiveDirectoryIntegratedApp" }

$appAudit = $apps | ForEach-Object {
    [PSCustomObject]@{
        DisplayName = $_.DisplayName
        Publisher = $_.PublisherName
        AppId = $_.AppId
        CreatedDate = $_.CreatedDateTime
        SignInAudience = $_.SignInAudience
    }
}

$appAudit | Export-Csv -Path "Integrated-Apps-Inventory.csv" -NoTypeInformation
Write-Host "Found $($appAudit.Count) integrated apps"
```

---

## Generate Governance Recommendations

```powershell
# Identify potentially sensitive sites not excluded
$sensitivePatterns = @("executive", "legal", "hr", "confidential", "board", "merger", "acquisition")

$potentialSensitive = $siteAudit | Where-Object {
    $url = $_.Url.ToLower()
    $title = $_.Title.ToLower()
    ($sensitivePatterns | Where-Object { $url -like "*$_*" -or $title -like "*$_*" }) -and
    $_.RestrictedFromCopilot -ne $true
}

if ($potentialSensitive.Count -gt 0) {
    Write-Host "`nWARNING: $($potentialSensitive.Count) potentially sensitive sites not excluded!" -ForegroundColor Red
    $potentialSensitive | Select-Object Url, Title | Format-Table
} else {
    Write-Host "`nNo sensitive sites found that need exclusion" -ForegroundColor Green
}
```

---

## Graph Connector ACL Validation

```powershell
# Review Graph Connector connections
Connect-MgGraph -Scopes "ExternalConnection.Read.All"

# Get external connections (Graph Connectors)
$connections = Get-MgExternalConnection

foreach ($conn in $connections) {
    Write-Host "`nConnection: $($conn.Name)" -ForegroundColor Cyan

    # Get connection operations/status
    $status = Get-MgExternalConnectionOperation -ExternalConnectionId $conn.Id -All |
        Sort-Object -Property StartedDateTime -Descending |
        Select-Object -First 5

    foreach ($op in $status) {
        $statusColor = switch ($op.Status) {
            "completed" { "Green" }
            "inProgress" { "Yellow" }
            "failed" { "Red" }
            default { "White" }
        }
        Write-Host "  $($op.StartedDateTime): $($op.Status) - $($op.Type)" -ForegroundColor $statusColor
    }
}
```

---

## Complete Configuration Script

```powershell
<#
.SYNOPSIS
    Configures Control 4.7 - Microsoft 365 Copilot Data Governance

.DESCRIPTION
    This script configures Copilot data governance:
    1. Inventories Copilot licenses
    2. Audits content exclusions
    3. Excludes sensitive sites from Copilot
    4. Generates governance recommendations

.PARAMETER AdminUrl
    SharePoint Admin Center URL

.PARAMETER SensitiveSites
    Array of site URLs to exclude from Copilot

.EXAMPLE
    .\Configure-Control-4.7.ps1 -AdminUrl "https://contoso-admin.sharepoint.com"

.NOTES
    Last Updated: January 2026
    Related Control: Control 4.7 - Microsoft 365 Copilot Data Governance
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$AdminUrl,

    [Parameter(Mandatory=$false)]
    [string[]]$SensitiveSites = @()
)

try {
    # Connect to Microsoft Graph
    Write-Host "Connecting to Microsoft Graph..." -ForegroundColor Cyan
    Connect-MgGraph -Scopes "User.Read.All", "Organization.Read.All", "Application.Read.All"

    # Connect to SharePoint Online
    Write-Host "Connecting to SharePoint Online..." -ForegroundColor Cyan
    Connect-SPOService -Url $AdminUrl

    Write-Host "Configuring Control 4.7 Copilot Data Governance" -ForegroundColor Cyan

    # Audit content exclusions
    Write-Host "`nAuditing Copilot content exclusions..." -ForegroundColor Yellow
    $allSites = Get-SPOSite -Limit All | Where-Object { $_.Template -notlike "*SPSPERS*" }

    $siteAudit = $allSites | ForEach-Object {
        [PSCustomObject]@{
            Url = $_.Url
            Title = $_.Title
            RestrictedFromCopilot = $_.RestrictContentOrgWideSearchAndCopilot
            SensitivityLabel = $_.SensitivityLabel
        }
    }

    $siteAudit | Export-Csv -Path "Site-Copilot-Status.csv" -NoTypeInformation

    $excludedCount = ($siteAudit | Where-Object { $_.RestrictedFromCopilot -eq $true }).Count
    $includedCount = ($siteAudit | Where-Object { $_.RestrictedFromCopilot -eq $false }).Count

    Write-Host "  Sites excluded from Copilot: $excludedCount" -ForegroundColor Green
    Write-Host "  Sites accessible by Copilot: $includedCount" -ForegroundColor Yellow

    # Exclude specified sensitive sites
    if ($SensitiveSites.Count -gt 0) {
        Write-Host "`nExcluding sensitive sites from Copilot..." -ForegroundColor Yellow
        foreach ($siteUrl in $SensitiveSites) {
            try {
                Set-SPOSite -Identity $siteUrl -RestrictContentOrgWideSearchAndCopilot $true
                Write-Host "  [DONE] Excluded: $siteUrl" -ForegroundColor Green
            }
            catch {
                Write-Host "  [FAIL] $siteUrl: $($_.Exception.Message)" -ForegroundColor Red
            }
        }
    }

    # Check for potentially sensitive sites not excluded
    Write-Host "`nGenerating governance recommendations..." -ForegroundColor Yellow
    $sensitivePatterns = @("executive", "legal", "hr", "confidential", "board", "merger", "acquisition")

    $potentialSensitive = $siteAudit | Where-Object {
        $url = $_.Url.ToLower()
        $title = $_.Title.ToLower()
        ($sensitivePatterns | Where-Object { $url -like "*$_*" -or $title -like "*$_*" }) -and
        $_.RestrictedFromCopilot -ne $true
    }

    if ($potentialSensitive.Count -gt 0) {
        Write-Host "  [WARN] $($potentialSensitive.Count) potentially sensitive sites not excluded" -ForegroundColor Yellow
        $potentialSensitive | Select-Object Url, Title | Format-Table
    } else {
        Write-Host "  [PASS] No sensitive sites need exclusion" -ForegroundColor Green
    }

    Write-Host "`nCopilot Governance Summary:" -ForegroundColor Cyan
    Write-Host "  Total sites: $($allSites.Count)" -ForegroundColor Green
    Write-Host "  Excluded from Copilot: $excludedCount" -ForegroundColor Green
    Write-Host "  Recommendations: $($potentialSensitive.Count)" -ForegroundColor $(if ($potentialSensitive.Count -gt 0) { "Yellow" } else { "Green" })

    Write-Host "`n[PASS] Control 4.7 configuration completed successfully" -ForegroundColor Green
}
catch {
    Write-Host "[FAIL] Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "[INFO] Stack trace: $($_.ScriptStackTrace)" -ForegroundColor Yellow
    exit 1
}
finally {
    # Cleanup connections
    Disconnect-MgGraph -ErrorAction SilentlyContinue
    if (Get-SPOSite -Limit 1 -ErrorAction SilentlyContinue) {
        Disconnect-SPOService -ErrorAction SilentlyContinue
    }
}
```

---

*Updated: January 2026 | Version: v1.1*
