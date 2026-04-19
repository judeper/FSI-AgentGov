# PowerShell Setup: Control 2.21 — AI Marketing Claims and Substantiation

!!! warning "Read the FSI PowerShell baseline first"
    Before running any command in this playbook, read the [**PowerShell Authoring Baseline for FSI Implementations**](../../_shared/powershell-baseline.md). It is the canonical source for module version pinning, sovereign-cloud (GCC / GCC High / DoD) endpoints, mutation safety (`-WhatIf` / `SupportsShouldProcess`), Dataverse compatibility, and SHA-256 evidence emission. Snippets below use the baseline patterns; if a snippet appears to deviate, the baseline wins.

**Last Updated:** April 2026
**Module Requirements:** `PnP.PowerShell` v2+ (PowerShell 7.2+)
**Estimated Time:** 30–45 minutes (idempotent; safe to re-run)
**Audience:** SharePoint Admin executing in a CAB-approved change window

---

## Prerequisites

| Item | Details |
|---|---|
| Roles | **SharePoint Admin** or **Site Collection Admin** on the target site |
| PowerShell edition | **PowerShell 7.2 or later** (PnP.PowerShell v2 does not support Windows PowerShell 5.1) |
| Module | `PnP.PowerShell` pinned to a CAB-approved version |
| App registration | PnP.PowerShell v2 requires an Entra app registration with delegated SharePoint permissions; do **not** silently upgrade from v1 in production |
| Sovereign cloud | Identify your tenant cloud (Commercial, GCC, GCC High, DoD) before connecting |
| Change ticket | Open and reference in `-WhatIf` dry runs and final apply runs |

---

## Module Installation (CAB-pinned)

```powershell
# Replace <version> with the version approved by your Change Advisory Board.
Install-Module -Name PnP.PowerShell `
    -RequiredVersion '<version>' `
    -Repository PSGallery `
    -Scope CurrentUser `
    -AllowClobber `
    -AcceptLicense

Import-Module PnP.PowerShell -RequiredVersion '<version>'
```

If your tenant uses GCC High or DoD, append `-AzureEnvironment USGovernmentHigh` (or `USGovernmentDoD`) on `Connect-PnPOnline`. See the baseline for the full sovereign-cloud matrix.

---

## Script 1 — Provision the AI Marketing Claims inventory list (idempotent)

```powershell
<#
.SYNOPSIS
    Provisions the AI Marketing Claims Inventory list for Control 2.21.

.DESCRIPTION
    Idempotent setup of the SharePoint list used as the system of record for
    AI marketing claim submissions, reviews, and approvals. Supports -WhatIf
    via SupportsShouldProcess and emits a SHA-256 evidence record describing
    each created or skipped artifact.

.PARAMETER SiteUrl
    Full URL of the governance SharePoint site, e.g. https://contoso.sharepoint.com/sites/AIGovernance

.PARAMETER AzureEnvironment
    Sovereign-cloud target. One of: Production, USGovernment, USGovernmentHigh,
    USGovernmentDoD, China, Germany. Defaults to Production.

.PARAMETER EvidencePath
    Folder where the JSON evidence record is written.

.EXAMPLE
    .\New-AIClaimsInventory.ps1 -SiteUrl 'https://contoso.sharepoint.com/sites/AIGovernance' -WhatIf

.NOTES
    Control: 2.21 — AI Marketing Claims and Substantiation
    Last Updated: April 2026
#>
[CmdletBinding(SupportsShouldProcess, ConfirmImpact = 'High')]
param(
    [Parameter(Mandatory)] [string] $SiteUrl,
    [ValidateSet('Production','USGovernment','USGovernmentHigh','USGovernmentDoD','China','Germany')]
    [string] $AzureEnvironment = 'Production',
    [string] $EvidencePath = '.\evidence\2.21'
)

$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Path $EvidencePath -Force | Out-Null

Write-Host "[2.21] Connecting to $SiteUrl ($AzureEnvironment)..." -ForegroundColor Cyan
Connect-PnPOnline -Url $SiteUrl -Interactive -AzureEnvironment $AzureEnvironment

$listName = 'AI Marketing Claims Inventory'
$evidence = [ordered]@{
    control       = '2.21'
    siteUrl       = $SiteUrl
    listName      = $listName
    timestampUtc  = (Get-Date).ToUniversalTime().ToString('o')
    operations    = @()
}

# Ensure list exists
$list = Get-PnPList -Identity $listName -ErrorAction SilentlyContinue
if (-not $list) {
    if ($PSCmdlet.ShouldProcess($listName, 'Create SharePoint list')) {
        $list = New-PnPList -Title $listName -Template GenericList -OnQuickLaunch
        $evidence.operations += @{ action = 'create-list'; target = $listName; result = 'created' }
        Write-Host "[2.21] Created list: $listName" -ForegroundColor Green
    }
} else {
    $evidence.operations += @{ action = 'create-list'; target = $listName; result = 'already-exists' }
    Write-Host "[2.21] List already exists: $listName" -ForegroundColor Yellow
}

# Field schema (display name, internal name, type, choices)
$fields = @(
    @{ Display = 'Claim Text';                  Internal = 'ClaimText';          Type = 'Note';     Choices = $null },
    @{ Display = 'Claim Category';              Internal = 'ClaimCategory';      Type = 'Choice';   Choices = @('Performance','Capability','Comparative','Predictive','Efficiency') },
    @{ Display = 'Agent/Product';               Internal = 'AgentProduct';       Type = 'Text';     Choices = $null },
    @{ Display = 'Target Channel';              Internal = 'TargetChannel';      Type = 'Choice';   Choices = @('Website','Email','Social Media','Sales Collateral','Press Release','Conference Material','Multiple') },
    @{ Display = 'Governance Zone';             Internal = 'GovernanceZone';     Type = 'Choice';   Choices = @('Zone 1 - Personal','Zone 2 - Team','Zone 3 - Enterprise') },
    @{ Display = 'FINRA 2210 Communication';    Internal = 'FinraCommType';      Type = 'Choice';   Choices = @('Correspondence','Retail Communication','Institutional Communication','N/A') },
    @{ Display = 'Substantiation File';         Internal = 'SubstantiationFile'; Type = 'URL';      Choices = $null },
    @{ Display = 'Status';                      Internal = 'ClaimStatus';        Type = 'Choice';   Choices = @('Draft','Under Review','Approved','Rejected','Withdrawn','Retired') },
    @{ Display = 'Submitted By';                Internal = 'SubmittedByUser';    Type = 'User';     Choices = $null },
    @{ Display = 'Submission Date';             Internal = 'SubmissionDate';     Type = 'DateTime'; Choices = $null },
    @{ Display = 'Compliance Reviewer';         Internal = 'ComplianceReviewer'; Type = 'User';     Choices = $null },
    @{ Display = 'Review Date';                 Internal = 'ReviewDate';         Type = 'DateTime'; Choices = $null },
    @{ Display = 'Approval Date';               Internal = 'ApprovalDate';       Type = 'DateTime'; Choices = $null },
    @{ Display = 'Next Review Date';            Internal = 'NextReviewDate';     Type = 'DateTime'; Choices = $null },
    @{ Display = 'Review Comments';             Internal = 'ReviewComments';     Type = 'Note';     Choices = $null }
)

$existingFields = (Get-PnPField -List $listName | Select-Object -ExpandProperty InternalName)

foreach ($f in $fields) {
    if ($existingFields -contains $f.Internal) {
        $evidence.operations += @{ action = 'add-field'; target = $f.Internal; result = 'already-exists' }
        Write-Host "  [skip] $($f.Internal)" -ForegroundColor DarkGray
        continue
    }
    if ($PSCmdlet.ShouldProcess("$listName : $($f.Internal)", "Add field ($($f.Type))")) {
        if ($f.Type -eq 'Choice' -and $f.Choices) {
            Add-PnPField -List $listName -DisplayName $f.Display -InternalName $f.Internal -Type Choice -Choices $f.Choices | Out-Null
        } else {
            Add-PnPField -List $listName -DisplayName $f.Display -InternalName $f.Internal -Type $f.Type | Out-Null
        }
        $evidence.operations += @{ action = 'add-field'; target = $f.Internal; result = 'created' }
        Write-Host "  [+]  $($f.Internal)" -ForegroundColor Green
    }
}

# Versioning
if ($PSCmdlet.ShouldProcess($listName, 'Enable versioning (50 major)')) {
    Set-PnPList -Identity $listName -EnableVersioning $true -MajorVersions 50 | Out-Null
    $evidence.operations += @{ action = 'enable-versioning'; target = $listName; result = 'set'; majorVersions = 50 }
}

# Persist evidence record + SHA-256 hash
$evidenceJson = $evidence | ConvertTo-Json -Depth 6
$evidenceFile = Join-Path $EvidencePath ("2.21-inventory-{0}.json" -f (Get-Date -Format 'yyyyMMdd-HHmmss'))
$evidenceJson | Out-File -FilePath $evidenceFile -Encoding utf8
$hash = Get-FileHash -Path $evidenceFile -Algorithm SHA256
"$($hash.Hash)  $($hash.Path)" | Out-File -FilePath ($evidenceFile + '.sha256') -Encoding ascii

Write-Host "`n[2.21] Evidence: $evidenceFile (SHA-256 $($hash.Hash))" -ForegroundColor Cyan
Disconnect-PnPOnline
```

---

## Script 2 — Provision the substantiation library

```powershell
<#
.SYNOPSIS
    Creates the AI Claims Substantiation document library and category folders.
.NOTES
    Idempotent. Apply your firm's retention label via Purview policy targeting
    this library; this script does not set retention labels (use Purview).
#>
[CmdletBinding(SupportsShouldProcess, ConfirmImpact = 'High')]
param(
    [Parameter(Mandatory)] [string] $SiteUrl,
    [ValidateSet('Production','USGovernment','USGovernmentHigh','USGovernmentDoD','China','Germany')]
    [string] $AzureEnvironment = 'Production'
)

$ErrorActionPreference = 'Stop'
Connect-PnPOnline -Url $SiteUrl -Interactive -AzureEnvironment $AzureEnvironment

$libName = 'AI Claims Substantiation'
$lib = Get-PnPList -Identity $libName -ErrorAction SilentlyContinue
if (-not $lib -and $PSCmdlet.ShouldProcess($libName, 'Create document library')) {
    New-PnPList -Title $libName -Template DocumentLibrary -OnQuickLaunch | Out-Null
    Set-PnPList -Identity $libName -EnableVersioning $true -MajorVersions 50 -ForceCheckout $true | Out-Null
    Write-Host "[2.21] Created library: $libName" -ForegroundColor Green
} else {
    Write-Host "[2.21] Library already exists: $libName" -ForegroundColor Yellow
}

$folders = @('Performance Claims','Capability Claims','Comparative Claims','Predictive Claims','Efficiency Claims')
foreach ($folder in $folders) {
    $exists = Get-PnPFolder -Url "$libName/$folder" -ErrorAction SilentlyContinue
    if (-not $exists -and $PSCmdlet.ShouldProcess("$libName/$folder", 'Create folder')) {
        Add-PnPFolder -Name $folder -Folder $libName | Out-Null
        Write-Host "  [+] $folder" -ForegroundColor Green
    }
}

Disconnect-PnPOnline
```

---

## Script 3 — Export claims inventory for compliance reporting

```powershell
<#
.SYNOPSIS
    Read-only export of the AI Marketing Claims inventory to CSV with SHA-256 evidence.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string] $SiteUrl,
    [ValidateSet('Production','USGovernment','USGovernmentHigh','USGovernmentDoD','China','Germany')]
    [string] $AzureEnvironment = 'Production',
    [string] $OutputPath = '.\evidence\2.21'
)

$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null

Connect-PnPOnline -Url $SiteUrl -Interactive -AzureEnvironment $AzureEnvironment
$items = Get-PnPListItem -List 'AI Marketing Claims Inventory' -PageSize 500

$rows = foreach ($i in $items) {
    [PSCustomObject]@{
        ClaimID           = $i.Id
        ClaimText         = $i.FieldValues.ClaimText
        Category          = $i.FieldValues.ClaimCategory
        AgentProduct      = $i.FieldValues.AgentProduct
        Channel           = $i.FieldValues.TargetChannel
        Zone              = $i.FieldValues.GovernanceZone
        FinraCommType     = $i.FieldValues.FinraCommType
        Status            = $i.FieldValues.ClaimStatus
        SubmissionDate    = $i.FieldValues.SubmissionDate
        ApprovalDate      = $i.FieldValues.ApprovalDate
        NextReviewDate    = $i.FieldValues.NextReviewDate
        HasSubstantiation = [bool]$i.FieldValues.SubstantiationFile
    }
}

$csv = Join-Path $OutputPath ("2.21-claims-{0}.csv" -f (Get-Date -Format 'yyyyMMdd-HHmmss'))
$rows | Export-Csv -Path $csv -NoTypeInformation -Encoding UTF8
$hash = Get-FileHash -Path $csv -Algorithm SHA256
"$($hash.Hash)  $($hash.Path)" | Out-File -FilePath ($csv + '.sha256') -Encoding ascii

Write-Host "[2.21] Exported $($rows.Count) claims to $csv (SHA-256 $($hash.Hash))" -ForegroundColor Green
$rows | Group-Object Status | Select-Object Name, Count | Format-Table -AutoSize
Disconnect-PnPOnline
```

---

## Script 4 — Identify claims due for quarterly review

```powershell
<#
.SYNOPSIS
    Read-only query for approved claims with NextReviewDate within the lookahead window.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string] $SiteUrl,
    [ValidateSet('Production','USGovernment','USGovernmentHigh','USGovernmentDoD','China','Germany')]
    [string] $AzureEnvironment = 'Production',
    [int] $DaysAhead = 14
)

$ErrorActionPreference = 'Stop'
Connect-PnPOnline -Url $SiteUrl -Interactive -AzureEnvironment $AzureEnvironment
$cutoff = (Get-Date).AddDays($DaysAhead).ToString('yyyy-MM-dd')

$caml = @"
<View>
  <Query>
    <Where>
      <And>
        <Eq><FieldRef Name='ClaimStatus'/><Value Type='Choice'>Approved</Value></Eq>
        <Leq><FieldRef Name='NextReviewDate'/><Value Type='DateTime'>$cutoff</Value></Leq>
      </And>
    </Where>
    <OrderBy><FieldRef Name='NextReviewDate' Ascending='TRUE'/></OrderBy>
  </Query>
</View>
"@

$due = Get-PnPListItem -List 'AI Marketing Claims Inventory' -Query $caml
if (-not $due -or $due.Count -eq 0) {
    Write-Host "[2.21] No claims due for review within $DaysAhead days." -ForegroundColor Green
} else {
    Write-Host "[2.21] $($due.Count) claim(s) due for review:" -ForegroundColor Yellow
    $due | ForEach-Object {
        $text = [string]$_.FieldValues.ClaimText
        $snippet = if ($text.Length -gt 60) { $text.Substring(0,60) + '...' } else { $text }
        Write-Host ("  ID {0,-5}  Due {1:yyyy-MM-dd}  {2}" -f $_.Id, $_.FieldValues.NextReviewDate, $snippet)
    }
}
Disconnect-PnPOnline
```

---

## Validation script

```powershell
<#
.SYNOPSIS
    Read-only verification that Control 2.21 SharePoint artifacts exist.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string] $SiteUrl,
    [ValidateSet('Production','USGovernment','USGovernmentHigh','USGovernmentDoD','China','Germany')]
    [string] $AzureEnvironment = 'Production'
)

$ErrorActionPreference = 'Stop'
Connect-PnPOnline -Url $SiteUrl -Interactive -AzureEnvironment $AzureEnvironment

$results = @()

$inv = Get-PnPList -Identity 'AI Marketing Claims Inventory' -ErrorAction SilentlyContinue
$results += [PSCustomObject]@{ Check = 'Claims inventory list exists'; Status = if ($inv) {'PASS'} else {'FAIL'} }

$lib = Get-PnPList -Identity 'AI Claims Substantiation' -ErrorAction SilentlyContinue
$results += [PSCustomObject]@{ Check = 'Substantiation library exists'; Status = if ($lib) {'PASS'} else {'FAIL'} }

$required = @('ClaimText','ClaimCategory','ClaimStatus','SubstantiationFile','NextReviewDate','GovernanceZone','FinraCommType')
if ($inv) {
    $present = (Get-PnPField -List 'AI Marketing Claims Inventory').InternalName
    $missing = $required | Where-Object { $_ -notin $present }
    $results += [PSCustomObject]@{ Check = 'Required fields configured'; Status = if (-not $missing) {'PASS'} else {"FAIL - missing: $($missing -join ', ')"} }
}

if ($lib) {
    $folders = @('Performance Claims','Capability Claims','Comparative Claims','Predictive Claims','Efficiency Claims')
    $missingF = $folders | Where-Object { -not (Get-PnPFolder -Url "AI Claims Substantiation/$_" -ErrorAction SilentlyContinue) }
    $results += [PSCustomObject]@{ Check = 'Category folders present'; Status = if (-not $missingF) {'PASS'} else {"FAIL - missing: $($missingF -join ', ')"} }
}

Write-Host "`n=== Control 2.21 Validation ===" -ForegroundColor Cyan
$results | Format-Table -AutoSize
Disconnect-PnPOnline
```

!!! note "Workflow validation is a portal task"
    Power Automate flows must be validated in the maker portal (Step 5 of the portal walkthrough). The validation script above intentionally does not modify or test flows; instead, run the test cases in the [Verification & Testing](verification-testing.md) playbook.

---

## Safety Checklist

- [ ] Module pinned to a CAB-approved `RequiredVersion`
- [ ] PowerShell 7.2+ confirmed (`$PSVersionTable.PSVersion`)
- [ ] `-AzureEnvironment` matches the tenant cloud
- [ ] Each mutating script run with `-WhatIf` first; output reviewed against change ticket
- [ ] Evidence JSON / CSV files retained with `.sha256` sidecar
- [ ] `Disconnect-PnPOnline` runs even on failure (consider wrapping calls in `try/finally` for production)

---

[Back to Control 2.21](../../../controls/pillar-2-management/2.21-ai-marketing-claims-and-substantiation.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification & Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
