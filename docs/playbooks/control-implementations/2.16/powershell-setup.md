# PowerShell Setup: Control 2.16 - RAG Source Integrity Validation

**Last Updated:** January 2026
**Modules Required:** PnP.PowerShell, Microsoft.PowerApps.Administration.PowerShell

## Prerequisites

```powershell
# Install required modules
Install-Module -Name PnP.PowerShell -Force -Scope CurrentUser
Install-Module -Name Microsoft.PowerApps.Administration.PowerShell -Force -Scope CurrentUser

# Connect to SharePoint Online
Connect-PnPOnline -Url "https://yourtenant.sharepoint.com" -Interactive

# Connect to Power Platform (interactive authentication)
Add-PowerAppsAccount

# For automated/unattended scenarios, use service principal authentication:
# $appId = "<Application-Client-ID>"
# $secret = "<Client-Secret>"
# $tenantId = "<Tenant-ID>"
# Add-PowerAppsAccount -ApplicationId $appId -ClientSecret $secret -TenantID $tenantId
```

---

## Knowledge Source Inventory Scripts

### Audit SharePoint Document Libraries

```powershell
<#
.SYNOPSIS
    Audits SharePoint document libraries used as knowledge sources

.DESCRIPTION
    Generates a report of documents in a library including:
    - Last modified date (for staleness detection)
    - Version count
    - Approval status

.PARAMETER SiteUrl
    SharePoint site URL

.PARAMETER LibraryName
    Document library name

.EXAMPLE
    .\Audit-KnowledgeSource.ps1 -SiteUrl "https://company.sharepoint.com/sites/research" -LibraryName "Research Library"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$SiteUrl,
    [Parameter(Mandatory=$true)]
    [string]$LibraryName
)

# Connect to SharePoint
Connect-PnPOnline -Url $SiteUrl -Interactive

Write-Host "=== Knowledge Source Audit ===" -ForegroundColor Cyan
Write-Host "Site: $SiteUrl"
Write-Host "Library: $LibraryName"

# Get all documents in the library
$items = Get-PnPListItem -List $LibraryName -PageSize 500

$report = $items | Where-Object { $_.FileSystemObjectType -eq "File" } | ForEach-Object {
    $item = $_
    $modified = [DateTime]$item["Modified"]
    $daysSinceModified = (Get-Date) - $modified

    [PSCustomObject]@{
        FileName = $item["FileLeafRef"]
        FilePath = $item["FileRef"]
        LastModified = $modified
        DaysSinceModified = [int]$daysSinceModified.TotalDays
        ModifiedBy = $item["Editor"].LookupValue
        Version = $item["_UIVersionString"]
        ApprovalStatus = $item["_ModerationStatus"]
        IsStale = $daysSinceModified.TotalDays -gt 365
    }
}

# Display summary
Write-Host "`n=== Summary ===" -ForegroundColor Cyan
Write-Host "Total Documents: $($report.Count)"
$staleCount = ($report | Where-Object { $_.IsStale }).Count
Write-Host "Stale Documents (>365 days): $staleCount" -ForegroundColor $(if ($staleCount -gt 0) { "Yellow" } else { "Green" })

# Show stale documents
if ($staleCount -gt 0) {
    Write-Host "`n=== Stale Documents ===" -ForegroundColor Yellow
    $report | Where-Object { $_.IsStale } | Format-Table FileName, LastModified, DaysSinceModified
}

# Export report
$reportPath = "KnowledgeSource-Audit-$(Get-Date -Format 'yyyyMMdd').csv"
$report | Export-Csv -Path $reportPath -NoTypeInformation
Write-Host "`nReport exported to: $reportPath"
```

### Check Document Versioning Configuration

```powershell
<#
.SYNOPSIS
    Checks versioning configuration for SharePoint document libraries

.PARAMETER SiteUrl
    SharePoint site URL

.EXAMPLE
    .\Check-VersioningConfig.ps1 -SiteUrl "https://company.sharepoint.com/sites/research"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$SiteUrl
)

Connect-PnPOnline -Url $SiteUrl -Interactive

Write-Host "=== Versioning Configuration Audit ===" -ForegroundColor Cyan

# Get all document libraries
$libraries = Get-PnPList | Where-Object { $_.BaseTemplate -eq 101 }

$versioningReport = $libraries | ForEach-Object {
    [PSCustomObject]@{
        LibraryName = $_.Title
        VersioningEnabled = $_.EnableVersioning
        MajorVersions = $_.MajorVersionLimit
        MinorVersionsEnabled = $_.EnableMinorVersions
        ContentApproval = $_.EnableModeration
        DraftVisibility = $_.DraftVersionVisibility
    }
}

$versioningReport | Format-Table

# Check compliance
$nonCompliant = $versioningReport | Where-Object {
    -not $_.VersioningEnabled -or -not $_.ContentApproval
}

if ($nonCompliant) {
    Write-Host "`n=== Libraries Needing Configuration ===" -ForegroundColor Yellow
    $nonCompliant | Format-Table LibraryName, VersioningEnabled, ContentApproval
}

# Export
$versioningReport | Export-Csv -Path "Versioning-Config-$(Get-Date -Format 'yyyyMMdd').csv" -NoTypeInformation
```

### Monitor Content Staleness

```powershell
<#
.SYNOPSIS
    Generates staleness report for knowledge source content

.DESCRIPTION
    Identifies documents that haven't been updated within threshold

.PARAMETER SiteUrl
    SharePoint site URL

.PARAMETER DaysThreshold
    Number of days to consider content stale (default: 365)

.EXAMPLE
    .\Get-StaleContent.ps1 -SiteUrl "https://company.sharepoint.com/sites/research" -DaysThreshold 180
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$SiteUrl,
    [int]$DaysThreshold = 365
)

Connect-PnPOnline -Url $SiteUrl -Interactive

Write-Host "=== Staleness Report (Threshold: $DaysThreshold days) ===" -ForegroundColor Cyan

# Get all document libraries
$libraries = Get-PnPList | Where-Object { $_.BaseTemplate -eq 101 -and $_.Hidden -eq $false }

$allStaleItems = @()

foreach ($library in $libraries) {
    $items = Get-PnPListItem -List $library.Title -PageSize 500

    $staleItems = $items | Where-Object {
        $_.FileSystemObjectType -eq "File" -and
        ((Get-Date) - [DateTime]$_["Modified"]).TotalDays -gt $DaysThreshold
    } | ForEach-Object {
        [PSCustomObject]@{
            Library = $library.Title
            FileName = $_["FileLeafRef"]
            LastModified = $_["Modified"]
            DaysSinceModified = [int]((Get-Date) - [DateTime]$_["Modified"]).TotalDays
            ModifiedBy = $_["Editor"].LookupValue
        }
    }

    $allStaleItems += $staleItems
}

Write-Host "Total Stale Items: $($allStaleItems.Count)" -ForegroundColor $(if ($allStaleItems.Count -gt 0) { "Yellow" } else { "Green" })

if ($allStaleItems.Count -gt 0) {
    $allStaleItems | Sort-Object DaysSinceModified -Descending | Format-Table Library, FileName, DaysSinceModified, ModifiedBy
    $allStaleItems | Export-Csv -Path "Stale-Content-$(Get-Date -Format 'yyyyMMdd').csv" -NoTypeInformation
}
```

---

## Validation Script

```powershell
<#
.SYNOPSIS
    Validates Control 2.16 - RAG Source Integrity

.DESCRIPTION
    Checks knowledge source configuration and compliance

.EXAMPLE
    .\Validate-Control-2.16.ps1 -SiteUrl "https://company.sharepoint.com/sites/research"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$SiteUrl
)

Write-Host "=== Control 2.16 Validation ===" -ForegroundColor Cyan

Connect-PnPOnline -Url $SiteUrl -Interactive

# Check 1: Versioning enabled
Write-Host "`n[Check 1] Document Versioning" -ForegroundColor Cyan
$libraries = Get-PnPList | Where-Object { $_.BaseTemplate -eq 101 -and $_.Hidden -eq $false }
$versioningEnabled = $libraries | Where-Object { $_.EnableVersioning }
Write-Host "Libraries with versioning: $($versioningEnabled.Count) / $($libraries.Count)"

# Check 2: Content approval enabled
Write-Host "`n[Check 2] Content Approval" -ForegroundColor Cyan
$approvalEnabled = $libraries | Where-Object { $_.EnableModeration }
Write-Host "Libraries with content approval: $($approvalEnabled.Count) / $($libraries.Count)"

# Check 3: Staleness
Write-Host "`n[Check 3] Content Staleness (>365 days)" -ForegroundColor Cyan
# Would run staleness check here

Write-Host "`n=== Validation Complete ===" -ForegroundColor Cyan
```

---

## Complete Configuration Script

```powershell
<#
.SYNOPSIS
    Complete RAG source integrity validation for Control 2.16

.DESCRIPTION
    Executes end-to-end RAG source validation including:
    - Document library audit
    - Versioning configuration check
    - Staleness analysis
    - Compliance report generation

.PARAMETER SiteUrl
    SharePoint site URL containing knowledge sources

.PARAMETER DaysThreshold
    Number of days to consider content stale

.PARAMETER OutputPath
    Path for output reports

.EXAMPLE
    .\Configure-Control-2.16.ps1 -SiteUrl "https://company.sharepoint.com/sites/research" -OutputPath ".\RAGIntegrity"

.NOTES
    Last Updated: January 2026
    Related Control: Control 2.16 - RAG Source Integrity Validation
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$SiteUrl,
    [int]$DaysThreshold = 365,
    [string]$OutputPath = ".\RAGIntegrity-Report"
)

try {
    Write-Host "=== Control 2.16: RAG Source Integrity Configuration ===" -ForegroundColor Cyan

    # Connect to SharePoint
    Connect-PnPOnline -Url $SiteUrl -Interactive

    # Ensure output directory exists
    New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null

    # Get all document libraries
    Write-Host "`n[Step 1] Auditing document libraries..." -ForegroundColor Cyan
    $libraries = Get-PnPList | Where-Object { $_.BaseTemplate -eq 101 -and $_.Hidden -eq $false }
    Write-Host "[INFO] Found $($libraries.Count) document libraries" -ForegroundColor Cyan

    # Check versioning configuration
    $versioningReport = $libraries | ForEach-Object {
        [PSCustomObject]@{
            LibraryName = $_.Title
            VersioningEnabled = $_.EnableVersioning
            MajorVersions = $_.MajorVersionLimit
            MinorVersionsEnabled = $_.EnableMinorVersions
            ContentApproval = $_.EnableModeration
            ItemCount = $_.ItemCount
        }
    }
    $versioningReport | Export-Csv -Path "$OutputPath\VersioningConfig.csv" -NoTypeInformation

    # Check compliance
    $nonCompliant = $versioningReport | Where-Object { -not $_.VersioningEnabled -or -not $_.ContentApproval }
    if ($nonCompliant.Count -gt 0) {
        Write-Host "[WARN] Libraries without versioning or content approval: $($nonCompliant.Count)" -ForegroundColor Yellow
        $nonCompliant | Export-Csv -Path "$OutputPath\NonCompliantLibraries.csv" -NoTypeInformation
    } else {
        Write-Host "[PASS] All libraries have versioning and content approval enabled" -ForegroundColor Green
    }

    # Analyze staleness
    Write-Host "`n[Step 2] Analyzing content staleness (threshold: $DaysThreshold days)..." -ForegroundColor Cyan
    $allStaleItems = @()

    foreach ($library in $libraries) {
        $items = Get-PnPListItem -List $library.Title -PageSize 500 -ErrorAction SilentlyContinue

        $staleItems = $items | Where-Object {
            $_.FileSystemObjectType -eq "File" -and
            ((Get-Date) - [DateTime]$_["Modified"]).TotalDays -gt $DaysThreshold
        } | ForEach-Object {
            [PSCustomObject]@{
                Library = $library.Title
                FileName = $_["FileLeafRef"]
                FilePath = $_["FileRef"]
                LastModified = $_["Modified"]
                DaysSinceModified = [int]((Get-Date) - [DateTime]$_["Modified"]).TotalDays
                ModifiedBy = $_["Editor"].LookupValue
            }
        }

        $allStaleItems += $staleItems
    }

    if ($allStaleItems.Count -gt 0) {
        Write-Host "[WARN] Stale content found: $($allStaleItems.Count) items" -ForegroundColor Yellow
        $allStaleItems | Export-Csv -Path "$OutputPath\StaleContent.csv" -NoTypeInformation
    } else {
        Write-Host "[PASS] No stale content found" -ForegroundColor Green
    }

    # Summary
    Write-Host "`n=== Summary ===" -ForegroundColor Cyan
    Write-Host "Site: $SiteUrl"
    Write-Host "Libraries Audited: $($libraries.Count)"
    Write-Host "Non-Compliant Libraries: $($nonCompliant.Count)"
    Write-Host "Stale Items: $($allStaleItems.Count)"
    Write-Host "Report Path: $OutputPath"

    Write-Host "`n[PASS] Control 2.16 configuration completed successfully" -ForegroundColor Green
}
catch {
    Write-Host "[FAIL] Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "[INFO] Stack trace: $($_.ScriptStackTrace)" -ForegroundColor Yellow
    exit 1
}
finally {
    # Cleanup connections
    Disconnect-PnPOnline -ErrorAction SilentlyContinue
}
```

---

[Back to Control 2.16](../../../controls/pillar-2-management/2.16-rag-source-integrity-validation.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
