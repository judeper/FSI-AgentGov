# PowerShell Setup: Control 2.21 - AI Marketing Claims and Substantiation

**Last Updated:** January 2026
**Module Requirements:** PnP.PowerShell, Microsoft.Graph
**Estimated Time:** 30-45 minutes

## Prerequisites

- [ ] PnP.PowerShell module installed: `Install-Module PnP.PowerShell -Scope CurrentUser`
- [ ] Microsoft.Graph module installed: `Install-Module Microsoft.Graph -Scope CurrentUser`
- [ ] SharePoint Admin or Site Collection Admin permissions
- [ ] Governance SharePoint site URL identified

---

## Module Installation

```powershell
# Install required modules
Install-Module PnP.PowerShell -Scope CurrentUser -Force
Install-Module Microsoft.Graph -Scope CurrentUser -Force

# Import modules
Import-Module PnP.PowerShell
Import-Module Microsoft.Graph
```

---

## Script 1: Create AI Claims Inventory List

```powershell
<#
.SYNOPSIS
    Creates the AI Marketing Claims Inventory list in SharePoint.

.DESCRIPTION
    Sets up the claims inventory list with all required columns
    for tracking AI marketing claims per Control 2.21.

.PARAMETER SiteUrl
    The URL of the governance SharePoint site.

.EXAMPLE
    .\New-AIClaimsInventory.ps1 -SiteUrl "https://contoso.sharepoint.com/sites/AIGovernance"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$SiteUrl
)

# Connect to SharePoint
Connect-PnPOnline -Url $SiteUrl -Interactive

# Create the list
$listName = "AI Marketing Claims Inventory"
$list = New-PnPList -Title $listName -Template GenericList

# Add columns
Add-PnPField -List $listName -DisplayName "Claim Text" -InternalName "ClaimText" -Type Note
Add-PnPField -List $listName -DisplayName "Claim Category" -InternalName "ClaimCategory" -Type Choice `
    -Choices "Performance","Capability","Comparative","Predictive","Efficiency"
Add-PnPField -List $listName -DisplayName "Agent/Product" -InternalName "AgentProduct" -Type Text
Add-PnPField -List $listName -DisplayName "Target Channel" -InternalName "TargetChannel" -Type Choice `
    -Choices "Website","Email","Social Media","Sales Collateral","Press Release","Multiple"
Add-PnPField -List $listName -DisplayName "Governance Zone" -InternalName "GovernanceZone" -Type Choice `
    -Choices "Zone 1 - Personal","Zone 2 - Team","Zone 3 - Enterprise"
Add-PnPField -List $listName -DisplayName "Substantiation File" -InternalName "SubstantiationFile" -Type URL
Add-PnPField -List $listName -DisplayName "Status" -InternalName "ClaimStatus" -Type Choice `
    -Choices "Draft","Under Review","Approved","Rejected","Retired"
Add-PnPField -List $listName -DisplayName "Submitted By" -InternalName "SubmittedBy" -Type User
Add-PnPField -List $listName -DisplayName "Submission Date" -InternalName "SubmissionDate" -Type DateTime
Add-PnPField -List $listName -DisplayName "Compliance Reviewer" -InternalName "ComplianceReviewer" -Type User
Add-PnPField -List $listName -DisplayName "Review Date" -InternalName "ReviewDate" -Type DateTime
Add-PnPField -List $listName -DisplayName "Approval Date" -InternalName "ApprovalDate" -Type DateTime
Add-PnPField -List $listName -DisplayName "Next Review Date" -InternalName "NextReviewDate" -Type DateTime
Add-PnPField -List $listName -DisplayName "Review Comments" -InternalName "ReviewComments" -Type Note

Write-Host "AI Marketing Claims Inventory list created successfully." -ForegroundColor Green

# Disconnect
Disconnect-PnPOnline
```

---

## Script 2: Create Substantiation Evidence Library

```powershell
<#
.SYNOPSIS
    Creates the substantiation evidence document library.

.PARAMETER SiteUrl
    The URL of the governance SharePoint site.

.EXAMPLE
    .\New-SubstantiationLibrary.ps1 -SiteUrl "https://contoso.sharepoint.com/sites/AIGovernance"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$SiteUrl
)

# Connect to SharePoint
Connect-PnPOnline -Url $SiteUrl -Interactive

# Create document library
$libraryName = "AI Claims Substantiation"
New-PnPList -Title $libraryName -Template DocumentLibrary

# Enable versioning
Set-PnPList -Identity $libraryName -EnableVersioning $true -MajorVersions 50 -EnableMinorVersions $false

# Create folder structure
$categories = @(
    "Performance Claims",
    "Capability Claims",
    "Comparative Claims",
    "Predictive Claims",
    "Efficiency Claims"
)

foreach ($category in $categories) {
    Add-PnPFolder -Name $category -Folder $libraryName
    Write-Host "Created folder: $category" -ForegroundColor Cyan
}

Write-Host "Substantiation library created successfully." -ForegroundColor Green

# Disconnect
Disconnect-PnPOnline
```

---

## Script 3: Export Claims Inventory Report

```powershell
<#
.SYNOPSIS
    Exports the AI claims inventory to CSV for compliance reporting.

.PARAMETER SiteUrl
    The URL of the governance SharePoint site.

.PARAMETER OutputPath
    Path for the output CSV file.

.EXAMPLE
    .\Export-AIClaimsReport.ps1 -SiteUrl "https://contoso.sharepoint.com/sites/AIGovernance" -OutputPath "C:\Reports\AIClaimsReport.csv"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$SiteUrl,

    [Parameter(Mandatory=$true)]
    [string]$OutputPath
)

# Connect to SharePoint
Connect-PnPOnline -Url $SiteUrl -Interactive

# Get all claims
$listName = "AI Marketing Claims Inventory"
$claims = Get-PnPListItem -List $listName -PageSize 500

# Build report data
$reportData = @()
foreach ($claim in $claims) {
    $reportData += [PSCustomObject]@{
        ClaimID = $claim.Id
        ClaimText = $claim.FieldValues.ClaimText
        Category = $claim.FieldValues.ClaimCategory
        AgentProduct = $claim.FieldValues.AgentProduct
        Channel = $claim.FieldValues.TargetChannel
        Zone = $claim.FieldValues.GovernanceZone
        Status = $claim.FieldValues.ClaimStatus
        SubmissionDate = $claim.FieldValues.SubmissionDate
        ApprovalDate = $claim.FieldValues.ApprovalDate
        NextReviewDate = $claim.FieldValues.NextReviewDate
        HasSubstantiation = if ($claim.FieldValues.SubstantiationFile) { "Yes" } else { "No" }
    }
}

# Export to CSV
$reportData | Export-Csv -Path $OutputPath -NoTypeInformation

Write-Host "Claims report exported to: $OutputPath" -ForegroundColor Green
Write-Host "Total claims: $($reportData.Count)" -ForegroundColor Cyan

# Summary statistics
$summary = $reportData | Group-Object -Property Status | Select-Object Name, Count
Write-Host "`nClaims by Status:" -ForegroundColor Yellow
$summary | Format-Table -AutoSize

# Disconnect
Disconnect-PnPOnline
```

---

## Script 4: Identify Claims Due for Review

```powershell
<#
.SYNOPSIS
    Identifies AI claims due for quarterly review.

.PARAMETER SiteUrl
    The URL of the governance SharePoint site.

.PARAMETER DaysAhead
    Number of days to look ahead for upcoming reviews. Default: 14

.EXAMPLE
    .\Get-ClaimsDueForReview.ps1 -SiteUrl "https://contoso.sharepoint.com/sites/AIGovernance"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$SiteUrl,

    [int]$DaysAhead = 14
)

# Connect to SharePoint
Connect-PnPOnline -Url $SiteUrl -Interactive

$listName = "AI Marketing Claims Inventory"
$cutoffDate = (Get-Date).AddDays($DaysAhead)

# Build CAML query for approved claims with upcoming review dates
$camlQuery = @"
<View>
    <Query>
        <Where>
            <And>
                <Eq>
                    <FieldRef Name='ClaimStatus'/>
                    <Value Type='Choice'>Approved</Value>
                </Eq>
                <Leq>
                    <FieldRef Name='NextReviewDate'/>
                    <Value Type='DateTime'>$($cutoffDate.ToString("yyyy-MM-dd"))</Value>
                </Leq>
            </And>
        </Where>
    </Query>
</View>
"@

$claimsDue = Get-PnPListItem -List $listName -Query $camlQuery

if ($claimsDue.Count -eq 0) {
    Write-Host "No claims due for review in the next $DaysAhead days." -ForegroundColor Green
} else {
    Write-Host "Claims due for review:" -ForegroundColor Yellow
    foreach ($claim in $claimsDue) {
        Write-Host "  - ID: $($claim.Id) | $($claim.FieldValues.ClaimText.Substring(0, [Math]::Min(50, $claim.FieldValues.ClaimText.Length)))..." -ForegroundColor Cyan
        Write-Host "    Review Due: $($claim.FieldValues.NextReviewDate)" -ForegroundColor Gray
    }
}

# Disconnect
Disconnect-PnPOnline
```

---

## Validation Script

```powershell
<#
.SYNOPSIS
    Validates Control 2.21 configuration.

.PARAMETER SiteUrl
    The URL of the governance SharePoint site.
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$SiteUrl
)

Connect-PnPOnline -Url $SiteUrl -Interactive

$results = @()

# Check 1: Claims Inventory List exists
$claimsList = Get-PnPList -Identity "AI Marketing Claims Inventory" -ErrorAction SilentlyContinue
$results += [PSCustomObject]@{
    Check = "Claims Inventory List exists"
    Status = if ($claimsList) { "PASS" } else { "FAIL" }
}

# Check 2: Substantiation Library exists
$substLib = Get-PnPList -Identity "AI Claims Substantiation" -ErrorAction SilentlyContinue
$results += [PSCustomObject]@{
    Check = "Substantiation Library exists"
    Status = if ($substLib) { "PASS" } else { "FAIL" }
}

# Check 3: Required columns exist
$requiredColumns = @("ClaimText", "ClaimCategory", "ClaimStatus", "SubstantiationFile", "NextReviewDate")
$listFields = Get-PnPField -List "AI Marketing Claims Inventory"
$missingColumns = $requiredColumns | Where-Object { $_ -notin $listFields.InternalName }
$results += [PSCustomObject]@{
    Check = "Required columns configured"
    Status = if ($missingColumns.Count -eq 0) { "PASS" } else { "FAIL - Missing: $($missingColumns -join ', ')" }
}

# Display results
Write-Host "`nControl 2.21 Validation Results:" -ForegroundColor Yellow
$results | Format-Table -AutoSize

Disconnect-PnPOnline
```

---

[Back to Control 2.21](../../../controls/pillar-2-management/2.21-ai-marketing-claims-and-substantiation.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
