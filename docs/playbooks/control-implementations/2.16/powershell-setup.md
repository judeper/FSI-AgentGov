# Control 2.16: RAG Source Integrity Validation — PowerShell Setup

!!! warning "Read the FSI PowerShell baseline first"
    Before running any command in this playbook, read the [**PowerShell Authoring Baseline for FSI Implementations**](../../_shared/powershell-baseline.md). It is the canonical source for module version pinning, mutation safety (`-WhatIf` / `SupportsShouldProcess`), Dataverse compatibility, and SHA-256 evidence emission. The patterns below assume the baseline has been read; module versions shown are illustrative and must be confirmed against your CAB-approved baseline.

> Automation companion to [Control 2.16: RAG Source Integrity Validation](../../../controls/pillar-2-management/2.16-rag-source-integrity-validation.md).
>
> **Audience:** SharePoint Admins, Power Platform Admins, and AI Administrators executing controls in production tenants subject to FINRA / SEC / GLBA / OCC / Fed SR 26-2 (formerly SR 11-7) / CFTC oversight.
>
> **Scope:** Every script in this playbook is **read-only**. None mutate tenant state. Mutations to SharePoint libraries and Power Automate flows are performed via the [Portal Walkthrough](portal-walkthrough.md) so that change-control evidence is captured by the platform's own audit trail.

---

## Prerequisites

| Requirement | Notes |
|-------------|-------|
| **PowerShell 7.2 LTS or 7.4** | Required for `PnP.PowerShell` v2+ and `Microsoft.Graph` |
| **PnP.PowerShell (pinned, v2+)** | Replace `<version>` below with the version approved by your Change Advisory Board (CAB). v2+ requires Entra app registration with explicit consent — do not silently upgrade from v1 |
| **Microsoft.Graph (pinned)** | Used for citation telemetry reads via Service Communications and Reports APIs |
| **Microsoft.PowerApps.Administration.PowerShell (pinned)** | **Windows PowerShell 5.1 only** — required to enumerate Microsoft Copilot Studio environments |
| **Graph permissions** | `Sites.Read.All`, `Files.Read.All` (delegated or application). Application permissions require Entra Global Admin consent. |
| **PnP app registration** | Entra app registered with `Sites.FullControl.All` *application* or `Sites.Read.All` *delegated*; consent recorded in the change ticket |

### Canonical install pattern

```powershell
# Pin every module to a CAB-approved version. DO NOT use -Force without -RequiredVersion.
Install-Module -Name PnP.PowerShell `
    -RequiredVersion '<version>' `
    -Repository PSGallery `
    -Scope CurrentUser `
    -AllowClobber `
    -AcceptLicense

Install-Module -Name Microsoft.Graph `
    -RequiredVersion '<version>' `
    -Repository PSGallery `
    -Scope CurrentUser `
    -AllowClobber `
    -AcceptLicense

# Desktop edition only — required for Power Apps admin cmdlets
Install-Module -Name Microsoft.PowerApps.Administration.PowerShell `
    -RequiredVersion '<version>' `
    -Repository PSGallery `
    -Scope CurrentUser
```

---

## Authentication Helper

Reused by every script in this playbook. Save as `Connect-FsiTenant.ps1` and dot-source.

```powershell
function Connect-FsiTenant {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string]$SiteUrl,
        [Parameter(Mandatory)] [string]$ClientId,
        [string[]]$GraphScopes = @('Sites.Read.All','Files.Read.All')
    )
    Connect-PnPOnline -Url $SiteUrl `
        -ClientId $ClientId `
        -Interactive `
        -AzureEnvironment 'Production'
    Connect-MgGraph -Environment 'Global' -Scopes $GraphScopes -NoWelcome
    Write-Verbose "Connected: PnP=Production, Graph=Global (commercial)"
}
```

---

## Evidence Emission Helper

Implements the SHA-256 manifest pattern from baseline section 5. Save as `Write-FsiEvidence.ps1` and dot-source in every script below.

```powershell
function Write-FsiEvidence {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] $Object,
        [Parameter(Mandatory)] [string]$Name,
        [Parameter(Mandatory)] [string]$EvidencePath,
        [string]$ScriptVersion = '1.0.0'
    )
    if (-not (Test-Path $EvidencePath)) {
        New-Item -ItemType Directory -Force -Path $EvidencePath | Out-Null
    }
    $ts = Get-Date -Format 'yyyyMMddTHHmmssZ'
    $jsonPath = Join-Path $EvidencePath "$Name-$ts.json"
    $Object | ConvertTo-Json -Depth 20 | Set-Content -Path $jsonPath -Encoding UTF8
    $hash = (Get-FileHash -Path $jsonPath -Algorithm SHA256).Hash
    $manifestPath = Join-Path $EvidencePath 'manifest.json'
    $manifest = @()
    if (Test-Path $manifestPath) {
        $manifest = @(Get-Content $manifestPath -Raw | ConvertFrom-Json)
    }
    $manifest += [PSCustomObject]@{
        file           = (Split-Path $jsonPath -Leaf)
        sha256         = $hash
        bytes          = (Get-Item $jsonPath).Length
        generated_utc  = $ts
        script_version = $ScriptVersion
        control_id     = '2.16'
    }
    $manifest | ConvertTo-Json -Depth 5 | Set-Content -Path $manifestPath -Encoding UTF8
    return $jsonPath
}
```

---

## Script 1: Audit SharePoint Library Hardening

Confirms versioning, content approval, and the FSI metadata schema are applied to every knowledge library on a site. Read-only.

```powershell
<#
.SYNOPSIS
    Audits SharePoint document libraries for the controls required by Control 2.16:
    versioning, content approval, and the FSI metadata schema.

.PARAMETER SiteUrl
    SharePoint site URL containing knowledge source libraries.

.PARAMETER ClientId
    Client ID of the registered Entra app used by PnP.PowerShell v2+.

.PARAMETER LibraryNames
    Optional list of library titles. If omitted, all non-hidden document libraries are audited.

.PARAMETER EvidencePath
    Folder for hashed JSON evidence and manifest. Created if missing.

.EXAMPLE
    .\Test-LibraryHardening.ps1 -SiteUrl https://contoso.sharepoint.com/sites/research `
        -ClientId 00000000-0000-0000-0000-000000000000 `
        -EvidencePath .\evidence\2.16
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string]$SiteUrl,
    [Parameter(Mandatory)] [string]$ClientId,
    [string[]]$LibraryNames,
    [string]$EvidencePath = ".\evidence\2.16"
)

$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\Connect-FsiTenant.ps1"
. "$PSScriptRoot\Write-FsiEvidence.ps1"

Connect-FsiTenant -SiteUrl $SiteUrl -ClientId $ClientId

# BaseTemplate 101 = document library
$libraries = Get-PnPList | Where-Object {
    $_.BaseTemplate -eq 101 -and -not $_.Hidden -and
    ($null -eq $LibraryNames -or $LibraryNames -contains $_.Title)
}

$requiredColumns = @('Source Owner','Approval Date','Next Review Date','Classification','Regulatory Scope','Approved For Agents')

$report = foreach ($lib in $libraries) {
    $fields = Get-PnPField -List $lib | Select-Object -ExpandProperty Title
    $missingCols = $requiredColumns | Where-Object { $fields -notcontains $_ }

    $status = 'PASS'
    $reasons = @()
    if (-not $lib.EnableVersioning)        { $status = 'FAIL'; $reasons += 'Versioning disabled' }
    if (-not $lib.EnableMinorVersions)     { $status = 'FAIL'; $reasons += 'Minor versions disabled' }
    if (-not $lib.EnableModeration)        { $status = 'FAIL'; $reasons += 'Content approval disabled' }
    if ($missingCols.Count -gt 0)          { $status = 'FAIL'; $reasons += "Missing FSI columns: $($missingCols -join ', ')" }

    [PSCustomObject]@{
        Site                  = $SiteUrl
        Library               = $lib.Title
        VersioningEnabled     = $lib.EnableVersioning
        MinorVersionsEnabled  = $lib.EnableMinorVersions
        MajorVersionLimit     = $lib.MajorVersionLimit
        ContentApprovalOn     = $lib.EnableModeration
        DraftVisibility       = $lib.DraftVersionVisibility
        MissingFsiColumns     = ($missingCols -join '; ')
        Status                = $status
        Reasons               = ($reasons -join '; ')
    }
}

$report | Format-Table Library, Status, Reasons -AutoSize

$evidenceFile = Write-FsiEvidence -Object $report -Name 'library-hardening' -EvidencePath $EvidencePath
$failures = ($report | Where-Object { $_.Status -eq 'FAIL' }).Count

if ($failures -gt 0) {
    Write-Host "[FAIL] $failures of $($report.Count) libraries are non-compliant. Evidence: $evidenceFile" -ForegroundColor Red
    exit 1
}
Write-Host "[PASS] All $($report.Count) libraries hardened. Evidence: $evidenceFile" -ForegroundColor Green

Disconnect-PnPOnline
Disconnect-MgGraph | Out-Null
```

---

## Script 2: Detect Stale Knowledge Source Content

Reports documents in approved knowledge libraries that exceed the zone's staleness threshold. Read-only.

```powershell
<#
.SYNOPSIS
    Identifies documents in knowledge libraries whose Modified date exceeds the zone
    staleness threshold. Cross-references the FSI 'Next Review Date' column when present.

.PARAMETER SiteUrl
    SharePoint site URL.

.PARAMETER ClientId
    Client ID of the registered PnP Entra app.

.PARAMETER DaysThreshold
    Staleness threshold in days. Defaults to 90 (Zone 3). Use 180 for Zone 2, 365 for Zone 1.

.PARAMETER EvidencePath
    Folder for evidence output.

.EXAMPLE
    .\Get-StaleKnowledgeContent.ps1 -SiteUrl https://contoso.sharepoint.com/sites/research `
        -ClientId 00000000-0000-0000-0000-000000000000 -DaysThreshold 90 `
        -EvidencePath .\evidence\2.16
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string]$SiteUrl,
    [Parameter(Mandatory)] [string]$ClientId,
    [int]$DaysThreshold = 90,
    [string]$EvidencePath = ".\evidence\2.16"
)

$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\Connect-FsiTenant.ps1"
. "$PSScriptRoot\Write-FsiEvidence.ps1"

Connect-FsiTenant -SiteUrl $SiteUrl -ClientId $ClientId

$cutoff = (Get-Date).AddDays(-$DaysThreshold)
$libraries = Get-PnPList | Where-Object { $_.BaseTemplate -eq 101 -and -not $_.Hidden }

$findings = foreach ($lib in $libraries) {
    # Use $top batching via -PageSize to avoid throttling on large libraries
    $items = Get-PnPListItem -List $lib -PageSize 500 -Fields 'FileLeafRef','FileRef','Modified','Editor','_ModerationStatus','Next_x0020_Review_x0020_Date','Source_x0020_Owner'
    foreach ($item in $items) {
        if ($item.FileSystemObjectType -ne 'File') { continue }
        $modified = [DateTime]$item['Modified']
        $nextReview = $item['Next_x0020_Review_x0020_Date']
        $isStaleByModified = $modified -lt $cutoff
        $isOverdueReview = $nextReview -and ([DateTime]$nextReview -lt (Get-Date))

        if ($isStaleByModified -or $isOverdueReview) {
            [PSCustomObject]@{
                Library            = $lib.Title
                FileName           = $item['FileLeafRef']
                FilePath           = $item['FileRef']
                LastModified       = $modified
                DaysSinceModified  = [int]((Get-Date) - $modified).TotalDays
                NextReviewDate     = $nextReview
                ReviewOverdue      = $isOverdueReview
                ApprovalStatus     = $item['_ModerationStatus']
                SourceOwner        = $item['Source_x0020_Owner'].Email
                ModifiedBy         = $item['Editor'].Email
            }
        }
    }
}

$evidenceFile = Write-FsiEvidence -Object $findings -Name 'stale-content' -EvidencePath $EvidencePath
Write-Host ("[INFO] Stale items: {0}. Threshold: {1} days. Evidence: {2}" -f $findings.Count, $DaysThreshold, $evidenceFile)

if ($findings.Count -gt 0) {
    $findings | Sort-Object DaysSinceModified -Descending | Format-Table Library, FileName, DaysSinceModified, ReviewOverdue, SourceOwner -AutoSize
    Write-Host "[WARN] Stale content present. Notify Source Owners and AI Governance Lead." -ForegroundColor Yellow
} else {
    Write-Host "[PASS] No stale content detected." -ForegroundColor Green
}

Disconnect-PnPOnline
Disconnect-MgGraph | Out-Null
```

> **Modified-date caveat:** SharePoint updates `Modified` whenever metadata is touched, not only when content changes. For higher-fidelity drift detection, use the [RAG Source Validator](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/rag-source-validator) solution, which computes per-file SHA-256 hashes and detects schema drift independent of metadata churn.

---

## Script 3: Snapshot Copilot Studio Knowledge Source Bindings

Captures the **declared** knowledge sources for every agent in an environment so that drift from the approved-sources register is detectable. Read-only.

```powershell
<#
.SYNOPSIS
    Enumerates Copilot Studio agents and their declared knowledge source bindings via
    the Power Apps admin cmdlets and Dataverse. Produces a snapshot suitable for
    diffing against the approved-sources register.

.PARAMETER EnvironmentId
    Power Platform environment ID hosting the agents.

.PARAMETER EvidencePath
    Folder for evidence output.

.EXAMPLE
    .\Get-AgentKnowledgeBindings.ps1 -EnvironmentId 00000000-0000-0000-0000-000000000000 `
        -EvidencePath .\evidence\2.16

.NOTES
    Requires Windows PowerShell 5.1 (Desktop edition).
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string]$EnvironmentId,
    [string]$EvidencePath = ".\evidence\2.16"
)

$ErrorActionPreference = 'Stop'

if ($PSVersionTable.PSEdition -ne 'Desktop') {
    throw "Microsoft.PowerApps.Administration.PowerShell requires Windows PowerShell 5.1 (Desktop edition). Detected: $($PSVersionTable.PSEdition) $($PSVersionTable.PSVersion). Re-run from a 5.1 host."
}

. "$PSScriptRoot\Write-FsiEvidence.ps1"

Add-PowerAppsAccount | Out-Null

$env = Get-AdminPowerAppEnvironment -EnvironmentName $EnvironmentId
if (-not $env) { throw "Environment $EnvironmentId not found." }

if ($env.CommonDataServiceDatabaseProvisioningState -ne 'Succeeded') {
    Write-Warning "Environment $EnvironmentId has no Dataverse database. Copilot Studio agent bindings cannot be enumerated; this script requires Dataverse."
    return
}

# Bot table holds Copilot Studio agents; bot_botcomponent rows of type "Knowledge"
# represent declared knowledge sources. Use the Dataverse Web API via the OData endpoint
# exposed by the environment.
$baseUrl = "$($env.Internal.properties.linkedEnvironmentMetadata.instanceApiUrl)/api/data/v9.2"
$token = (Get-PowerAppsAccessToken -Audience $env.Internal.properties.linkedEnvironmentMetadata.instanceUrl).AccessToken
$headers = @{ Authorization = "Bearer $token"; Accept = 'application/json' }

$bots = Invoke-RestMethod -Uri "$baseUrl/bots?`$select=botid,name,statecode,owninguser" -Headers $headers
$bindings = foreach ($bot in $bots.value) {
    $components = Invoke-RestMethod -Uri "$baseUrl/bot_botcomponents?`$filter=_parentbotid_value eq $($bot.botid) and componenttype eq 9&`$select=name,componenttype,data" -Headers $headers
    foreach ($comp in $components.value) {
        [PSCustomObject]@{
            EnvironmentId  = $EnvironmentId
            AgentId        = $bot.botid
            AgentName      = $bot.name
            ComponentName  = $comp.name
            ComponentType  = 'Knowledge'
            BindingData    = $comp.data
        }
    }
}

$evidenceFile = Write-FsiEvidence -Object $bindings -Name 'agent-knowledge-bindings' -EvidencePath $EvidencePath
Write-Host "[INFO] Captured $($bindings.Count) knowledge bindings across $($bots.value.Count) agents. Evidence: $evidenceFile"
```

> **Dataverse compatibility note:** Per baseline section 6, this script returns immediately on non-Dataverse environments rather than producing false-clean evidence. Copilot Studio agents always require Dataverse, so a non-Dataverse environment in scope is itself a finding to surface to the AI Governance Lead.

---

## Validation Script (End-to-End)

```powershell
<#
.SYNOPSIS
    Runs all read-only validation checks for Control 2.16 and exits non-zero on failure.
    Safe to schedule; does not mutate tenant state.

.EXAMPLE
    .\Validate-Control-2.16.ps1 -SiteUrl https://contoso.sharepoint.com/sites/research `
        -ClientId <guid> -EnvironmentId <guid> -DaysThreshold 90 `
        -EvidencePath .\evidence\2.16
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string]$SiteUrl,
    [Parameter(Mandatory)] [string]$ClientId,
    [Parameter(Mandatory)] [string]$EnvironmentId,
    [int]$DaysThreshold = 90,
    [string]$EvidencePath = ".\evidence\2.16"
)

$ErrorActionPreference = 'Stop'
$failed = $false

Write-Host "=== Control 2.16 Validation ===" -ForegroundColor Cyan

try {
    & "$PSScriptRoot\Test-LibraryHardening.ps1" -SiteUrl $SiteUrl -ClientId $ClientId -EvidencePath $EvidencePath
} catch {
    Write-Host "[FAIL] Library hardening: $($_.Exception.Message)" -ForegroundColor Red
    $failed = $true
}

try {
    & "$PSScriptRoot\Get-StaleKnowledgeContent.ps1" -SiteUrl $SiteUrl -ClientId $ClientId -DaysThreshold $DaysThreshold -EvidencePath $EvidencePath
} catch {
    Write-Host "[FAIL] Stale content scan: $($_.Exception.Message)" -ForegroundColor Red
    $failed = $true
}

# Knowledge bindings snapshot requires Windows PowerShell 5.1; skip with INFO if running PS7+.
if ($PSVersionTable.PSEdition -eq 'Desktop') {
    try {
        & "$PSScriptRoot\Get-AgentKnowledgeBindings.ps1" -EnvironmentId $EnvironmentId -EvidencePath $EvidencePath
    } catch {
        Write-Host "[FAIL] Knowledge bindings snapshot: $($_.Exception.Message)" -ForegroundColor Red
        $failed = $true
    }
} else {
    Write-Host "[INFO] Skipping knowledge bindings snapshot (requires Windows PowerShell 5.1)" -ForegroundColor Yellow
}

if ($failed) {
    Write-Host "=== Validation FAILED ===" -ForegroundColor Red
    exit 1
}

Write-Host "=== Validation PASS ===" -ForegroundColor Green
```

---

## Scheduled-Run Recommendations

| Script | Schedule | Run as |
|--------|----------|--------|
| `Test-LibraryHardening.ps1` | Weekly + on each library configuration change | Service principal with `Sites.Read.All` (application) |
| `Get-StaleKnowledgeContent.ps1` | Daily for Zone 3; weekly for Zone 2; monthly for Zone 1 | Service principal with `Sites.Read.All` |
| `Get-AgentKnowledgeBindings.ps1` | Weekly, **Windows PowerShell 5.1** runner | Power Platform Admin service account (no MFA-blocked); Dataverse access required |
| `Validate-Control-2.16.ps1` | Monthly + before each examiner request | Same as above |

> **Mutation safety note:** None of the scripts in this playbook mutate tenant state. There is no `-WhatIf` switch because there is nothing to confirm. If you extend these scripts to *change* settings (e.g., set `EnableModeration` programmatically), wrap mutations in `[CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]`, capture a before-snapshot, and follow baseline section 4.

---

[Back to Control 2.16](../../../controls/pillar-2-management/2.16-rag-source-integrity-validation.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification & Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
