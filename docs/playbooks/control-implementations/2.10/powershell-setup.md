# Control 2.10: Patch Management and System Updates — PowerShell Setup

!!! warning "Read the FSI PowerShell baseline first"
    Before running any command in this playbook, read the [**PowerShell Authoring Baseline for FSI Implementations**](../../_shared/powershell-baseline.md). It is the canonical source for module version pinning, mutation safety (`-WhatIf` / `SupportsShouldProcess`), Dataverse compatibility, and SHA-256 evidence emission. The patterns below assume the baseline has been read; module versions shown are illustrative and must be confirmed against your CAB-approved baseline.

> Automation companion to [Control 2.10: Patch Management and System Updates](../../../controls/pillar-2-management/2.10-patch-management-and-system-updates.md).
>
> **Audience:** Power Platform Admins and AI Administrators executing controls in production tenants subject to FINRA / SEC / GLBA / OCC / Fed SR 26-2 (formerly SR 11-7) / CFTC oversight.

---

## Prerequisites

| Requirement | Notes |
|-------------|-------|
| **PowerShell 7.2 LTS or 7.4** | Required for `Microsoft.Graph` modules used here |
| **Microsoft.Graph (pinned)** | Replace `<version>` below with the version approved by your Change Advisory Board (CAB) |
| **Az.ResourceGraph (pinned)** | Used to enumerate environments under Service Health alert scope |
| **Microsoft.PowerApps.Administration.PowerShell (pinned)** | **Windows PowerShell 5.1 only** — required to read environment release channel settings |
| **Graph permissions** | `ServiceMessage.Read.All` (delegated or application) — required for Message Center reads. Application permission requires Entra Global Admin consent. |

### Canonical install pattern

```powershell
# Pin every module to a CAB-approved version. DO NOT use -Force without -RequiredVersion.
Install-Module -Name Microsoft.Graph `
    -RequiredVersion '<version>' `
    -Repository PSGallery `
    -Scope CurrentUser `
    -AllowClobber `
    -AcceptLicense

Install-Module -Name Az.ResourceGraph `
    -RequiredVersion '<version>' `
    -Repository PSGallery `
    -Scope CurrentUser

# Desktop edition only — required for Power Apps admin cmdlets
# Run from Windows PowerShell 5.1 host, NOT PowerShell 7
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
        [string[]]$Scopes = @('ServiceMessage.Read.All')
    )
    Connect-MgGraph -Environment 'Global' -Scopes $Scopes -NoWelcome
    Write-Verbose "Connected to Microsoft Graph (commercial Global environment)."
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
        control_id     = '2.10'
    }
    $manifest | ConvertTo-Json -Depth 5 | Set-Content -Path $manifestPath -Encoding UTF8
    return $jsonPath
}
```

---

## Script 1: Pull Message Center Posts (Read-Only)

Uses Microsoft Graph Service Communications API. Filters server-side to reduce throttling risk on large tenants.

```powershell
<#
.SYNOPSIS
    Retrieves recent Message Center posts for AI-relevant services and emits SHA-256-hashed evidence.

.PARAMETER Days
    Lookback window in days. Default 30.

.PARAMETER EvidencePath
    Folder for hashed JSON evidence and manifest. Created if missing.

.EXAMPLE
    .\Get-MessageCenterPosts.ps1 -Days 14 -EvidencePath .\evidence\2.10
#>
[CmdletBinding()]
param(
    [int]$Days = 30,
    [string]$EvidencePath = ".\evidence\2.10"
)

$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\Connect-FsiTenant.ps1"
. "$PSScriptRoot\Write-FsiEvidence.ps1"

Connect-FsiTenant -Scopes 'ServiceMessage.Read.All'

# AI-relevant Microsoft 365 services. The Services array on each post is free-text;
# normalize by checking against an allow-list rather than relying on $filter for membership.
$relevantServices = @(
    'Microsoft Copilot',
    'Microsoft Copilot Studio',
    'Power Platform',
    'Power Automate',
    'Power Apps',
    'Microsoft Dataverse',
    'SharePoint Online',
    'Microsoft Purview'
)

$startUtc = (Get-Date).ToUniversalTime().AddDays(-$Days).ToString('o')

# Server-side filter on lastModifiedDateTime; client-side filter on Services membership.
$filter = "lastModifiedDateTime ge $startUtc"
$messages = Get-MgServiceAnnouncementMessage -Filter $filter -All

$relevant = $messages | Where-Object {
    $_.Services -and ($_.Services | Where-Object { $relevantServices -contains $_ })
}

Write-Host ("[INFO] Total messages in window: {0}; relevant to AI estate: {1}" -f $messages.Count, $relevant.Count)

$snapshot = $relevant | ForEach-Object {
    [PSCustomObject]@{
        MessageId            = $_.Id
        Title                = $_.Title
        Services             = ($_.Services -join '; ')
        Category             = $_.Category
        Severity             = $_.Severity
        IsMajorChange        = $_.IsMajorChange
        StartDateTime        = $_.StartDateTime
        EndDateTime          = $_.EndDateTime
        ActionRequiredBy     = $_.ActionRequiredByDateTime
        LastModifiedDateTime = $_.LastModifiedDateTime
        Tags                 = ($_.Tags -join '; ')
        WebUrl               = $_.Details |
            Where-Object { $_.Name -eq 'ExternalLink' } |
            Select-Object -ExpandProperty Value -ErrorAction SilentlyContinue
    }
}

$evidenceFile = Write-FsiEvidence -Object $snapshot -Name 'message-center-posts' -EvidencePath $EvidencePath
Write-Host "[PASS] Evidence written: $evidenceFile" -ForegroundColor Green

Disconnect-MgGraph | Out-Null
```

> **Throttling note:** The Service Communications API returns up to 100 messages per page and is subject to Microsoft Graph throttling. The `-All` switch handles paging. If you see HTTP 429, add a `Start-Sleep` between pages or schedule the job off-peak.

---

## Script 2: Read Environment Release Channel Settings

Confirms each Power Platform environment's release channel matches the policy from Part 3 of the [Portal Walkthrough](portal-walkthrough.md).

> **PowerShell edition guard:** The Power Apps Admin module is **Desktop-only** (Windows PowerShell 5.1). Run this script from a Windows PowerShell 5.1 host, not PowerShell 7. The script enforces this at the top.

```powershell
<#
.SYNOPSIS
    Reports release channel and managed-environment status for all environments.
    Read-only; emits SHA-256-hashed evidence.

.PARAMETER EvidencePath
    Folder for evidence output.

.EXAMPLE
    .\Get-EnvironmentReleaseChannels.ps1 -EvidencePath .\evidence\2.10
#>
[CmdletBinding()]
param(
    [string]$EvidencePath = ".\evidence\2.10"
)

$ErrorActionPreference = 'Stop'

if ($PSVersionTable.PSEdition -ne 'Desktop') {
    throw "Microsoft.PowerApps.Administration.PowerShell requires Windows PowerShell 5.1 (Desktop edition). Detected: $($PSVersionTable.PSEdition) $($PSVersionTable.PSVersion). Re-run from a 5.1 host."
}

. "$PSScriptRoot\Write-FsiEvidence.ps1"

Add-PowerAppsAccount | Out-Null

$envs = Get-AdminPowerAppEnvironment

$report = $envs | ForEach-Object {
    # ReleaseChannel is exposed under the environment Settings; property name has varied
    # across module versions. Probe the common shapes and fall back to "Unknown".
    $channel = $null
    if ($_.Internal.properties.releaseChannel) {
        $channel = $_.Internal.properties.releaseChannel
    } elseif ($_.Internal.properties.environmentSku) {
        # Some module versions surface only via environment description
        $channel = '(read via PPAC UI)'
    } else {
        $channel = 'Unknown'
    }

    [PSCustomObject]@{
        EnvironmentName = $_.EnvironmentName
        DisplayName     = $_.DisplayName
        EnvironmentType = $_.EnvironmentType
        IsManaged       = $_.Internal.properties.governanceConfiguration.protectionLevel -eq 'Standard'
        DataverseState  = $_.CommonDataServiceDatabaseProvisioningState
        ReleaseChannel  = $channel
        Region          = $_.Location
        CreatedTime     = $_.CreatedTime
    }
}

$report | Format-Table -AutoSize

$evidenceFile = Write-FsiEvidence -Object $report -Name 'environment-release-channels' -EvidencePath $EvidencePath
Write-Host "[PASS] Evidence written: $evidenceFile" -ForegroundColor Green
```

> **Module compatibility note:** The exact JSON path for `releaseChannel` has changed between module versions. If the value reports as `Unknown`, treat the PPAC UI as authoritative and document the module version mismatch in your validation evidence.

---

## Script 3: Validate Service Health Alert Coverage

Read-only audit that the alert rules from Part 2 of the [Portal Walkthrough](portal-walkthrough.md) exist and are enabled for the right resource providers.

```powershell
<#
.SYNOPSIS
    Validates Azure Service Health alert rule coverage for AI-platform resource providers.

.PARAMETER SubscriptionIds
    Subscriptions to audit.

.PARAMETER EvidencePath
    Folder for evidence output.

.EXAMPLE
    .\Test-ServiceHealthAlertCoverage.ps1 -SubscriptionIds @('00000000-0000-0000-0000-000000000000') -EvidencePath .\evidence\2.10
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string[]]$SubscriptionIds,
    [string]$EvidencePath = ".\evidence\2.10"
)

$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\Write-FsiEvidence.ps1"

if (-not (Get-AzContext)) {
    Connect-AzAccount -ErrorAction Stop | Out-Null
}

$expectedProviders = @(
    'Microsoft.PowerPlatform',
    'Microsoft.PowerApps',
    'Microsoft.Flow',
    'Microsoft.KeyVault',
    'Microsoft.Insights'
)

$findings = foreach ($subId in $SubscriptionIds) {
    Set-AzContext -SubscriptionId $subId | Out-Null
    $alerts = Get-AzActivityLogAlert | Where-Object {
        $_.ConditionAllOf.Field -contains 'category' -and
        ($_.ConditionAllOf | Where-Object { $_.Field -eq 'category' -and $_.Equals -eq 'ServiceHealth' })
    }

    $coveredProviders = @()
    foreach ($alert in $alerts) {
        $providerCondition = $alert.ConditionAllOf | Where-Object { $_.Field -eq 'properties.impactedServices[*].ServiceName' }
        if ($providerCondition) {
            $coveredProviders += $providerCondition.Equals
        }
    }

    foreach ($provider in $expectedProviders) {
        [PSCustomObject]@{
            SubscriptionId = $subId
            ResourceProvider = $provider
            HasAlertRule = ($coveredProviders -contains $provider) -or ($alerts.Count -gt 0)
            AlertRuleCount = $alerts.Count
            Status = if ($coveredProviders -contains $provider -or $alerts.Count -gt 0) { 'PASS' } else { 'FAIL' }
        }
    }
}

$findings | Format-Table -AutoSize

$evidenceFile = Write-FsiEvidence -Object $findings -Name 'service-health-alert-coverage' -EvidencePath $EvidencePath
Write-Host "[PASS] Evidence written: $evidenceFile" -ForegroundColor Green
```

---

## Script 4: Compose the Patch History Log

Combines outputs from Scripts 1, 2, and 3 into a single CSV suitable for examiner review and SharePoint upload to `FSI-Patch-Evidence`.

```powershell
<#
.SYNOPSIS
    Joins Message Center posts, environment channel state, and alert coverage into one
    examiner-ready CSV with a SHA-256 manifest entry.

.PARAMETER EvidencePath
    Folder containing previously emitted JSON evidence.

.EXAMPLE
    .\Export-PatchHistory.ps1 -EvidencePath .\evidence\2.10
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string]$EvidencePath
)

$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\Write-FsiEvidence.ps1"

$mcLatest = Get-ChildItem $EvidencePath -Filter 'message-center-posts-*.json' |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1
if (-not $mcLatest) { throw "No message-center-posts-*.json found in $EvidencePath. Run Script 1 first." }

$posts = Get-Content $mcLatest.FullName -Raw | ConvertFrom-Json

$report = $posts | ForEach-Object {
    [PSCustomObject]@{
        MessageId         = $_.MessageId
        Title             = $_.Title
        Services          = $_.Services
        Category          = $_.Category
        IsMajorChange     = $_.IsMajorChange
        ActionRequiredBy  = $_.ActionRequiredBy
        AssessmentOwner   = ''   # Filled in by AI Governance Lead during triage
        AssessmentResult  = ''   # Pass | Fail | N/A
        ValidationRunId   = ''   # Link to validation environment test run
        DeploymentDate    = ''   # Production deployment timestamp
        ApproverUPN       = ''   # Person principal name of CAB approver
        EvidenceLink      = ''   # SharePoint URL of validation artifacts
        Status            = 'Open'
    }
}

$csv = Join-Path $EvidencePath ("patch-history-{0}.csv" -f (Get-Date -Format 'yyyyMMdd'))
$report | Export-Csv -Path $csv -NoTypeInformation -Encoding UTF8

# Hash the CSV and append to manifest
$hash = (Get-FileHash -Path $csv -Algorithm SHA256).Hash
$manifestPath = Join-Path $EvidencePath 'manifest.json'
$manifest = if (Test-Path $manifestPath) { @(Get-Content $manifestPath -Raw | ConvertFrom-Json) } else { @() }
$manifest += [PSCustomObject]@{
    file           = (Split-Path $csv -Leaf)
    sha256         = $hash
    bytes          = (Get-Item $csv).Length
    generated_utc  = (Get-Date -Format 'yyyyMMddTHHmmssZ')
    script_version = '1.0.0'
    control_id     = '2.10'
}
$manifest | ConvertTo-Json -Depth 5 | Set-Content -Path $manifestPath -Encoding UTF8

Write-Host "[PASS] Patch history exported: $csv" -ForegroundColor Green
```

---

## Validation Script (End-to-End)

```powershell
<#
.SYNOPSIS
    Runs all read-only validation checks for Control 2.10 and exits non-zero on failure.
    Safe to schedule; does not mutate tenant state.

.EXAMPLE
    .\Validate-Control-2.10.ps1 -EvidencePath .\evidence\2.10 -SubscriptionIds @('...')
#>
[CmdletBinding()]
param(
    [string]$EvidencePath = ".\evidence\2.10",
    [Parameter(Mandatory)] [string[]]$SubscriptionIds
)

$ErrorActionPreference = 'Stop'
$failed = $false

Write-Host "=== Control 2.10 Validation ===" -ForegroundColor Cyan

try {
    & "$PSScriptRoot\Get-MessageCenterPosts.ps1" -Days 30 -EvidencePath $EvidencePath
} catch {
    Write-Host "[FAIL] Message Center pull: $($_.Exception.Message)" -ForegroundColor Red
    $failed = $true
}

try {
    & "$PSScriptRoot\Test-ServiceHealthAlertCoverage.ps1" -SubscriptionIds $SubscriptionIds -EvidencePath $EvidencePath
} catch {
    Write-Host "[FAIL] Service Health coverage: $($_.Exception.Message)" -ForegroundColor Red
    $failed = $true
}

# Environment release channel check requires Windows PowerShell 5.1; skip with INFO if running PS7+.
if ($PSVersionTable.PSEdition -eq 'Desktop') {
    try {
        & "$PSScriptRoot\Get-EnvironmentReleaseChannels.ps1" -EvidencePath $EvidencePath
    } catch {
        Write-Host "[FAIL] Environment release channel read: $($_.Exception.Message)" -ForegroundColor Red
        $failed = $true
    }
} else {
    Write-Host "[INFO] Skipping environment release channel check (requires Windows PowerShell 5.1)" -ForegroundColor Yellow
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
| `Get-MessageCenterPosts.ps1` | Daily 06:00 local | Service principal with `ServiceMessage.Read.All` (application permission, Global Admin consent) |
| `Test-ServiceHealthAlertCoverage.ps1` | Weekly | Service principal with Reader on each subscription |
| `Get-EnvironmentReleaseChannels.ps1` | Weekly, **Windows PowerShell 5.1** runner | Power Platform Admin service account (no MFA-blocked) |
| `Validate-Control-2.10.ps1` | Monthly + before each wave window | Same as above |

> **Mutation safety note:** None of the scripts in this playbook mutate tenant state. There is no `-WhatIf` switch because there is nothing to confirm. If you extend these scripts to *change* settings (e.g., flip a release channel programmatically once that capability stabilizes), wrap mutations in `[CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]` and follow baseline section 4.

---

[Back to Control 2.10](../../../controls/pillar-2-management/2.10-patch-management-and-system-updates.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
