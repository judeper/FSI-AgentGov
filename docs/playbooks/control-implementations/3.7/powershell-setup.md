# Control 3.7: PPAC Security Posture Assessment — PowerShell Setup

!!! warning "Read the FSI PowerShell baseline first"
    Before running anything in this playbook, read the [**PowerShell Authoring Baseline for FSI Implementations**](../../_shared/powershell-baseline.md). It is the canonical source for module version pinning, mutation safety (`-WhatIf` / `SupportsShouldProcess`), Dataverse compatibility, and SHA-256 evidence emission. Snippets below assume those patterns and reference them by section number.

> Automation scripts for [Control 3.7](../../../controls/pillar-3-reporting/3.7-ppac-security-posture-assessment.md). All cmdlets in this playbook are **read-only collectors** — they do not change tenant state. Even so, scripts emit SHA-256-hashed evidence so the posture review itself is audit-defensible under SEC 17a-4(f) and FINRA 4511.

---

## Prerequisites

- **Windows PowerShell 5.1 (Desktop edition)** — required for `Microsoft.PowerApps.Administration.PowerShell` (baseline §2). PowerShell 7 will silently fail on Power Apps admin cmdlets and produce **false-clean** evidence.
- **Power Platform Admin** role for the executing identity (or service principal with the equivalent application user in each Dataverse environment).
- **Microsoft Graph** scopes for the optional Defender cross-reference: `SecurityEvents.Read.All`, `Policy.Read.All`.
- Tenant-level analytics enabled (the security score and recommendations are populated only after enablement; allow up to 24 hours).

```powershell
# REQUIRED EDITION GUARD — see baseline §2
if ($PSVersionTable.PSEdition -ne 'Desktop') {
    throw "Microsoft.PowerApps.Administration.PowerShell requires Windows PowerShell 5.1 (Desktop). Detected: $($PSVersionTable.PSEdition) $($PSVersionTable.PSVersion)."
}

# REQUIRED PINNED INSTALL — see baseline §1
# Replace <version> with the version approved by your CAB.
Install-Module -Name Microsoft.PowerApps.Administration.PowerShell `
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
```

---

## Commercial cloud authentication

```powershell
param(
    [string]$Endpoint = 'prod'
)

Add-PowerAppsAccount -Endpoint $Endpoint
Connect-MgGraph -Environment 'Global' -Scopes 'SecurityEvents.Read.All','Policy.Read.All'
```

---

## Evidence emission helper (baseline §4)

The posture collector uses the canonical `Write-FsiEvidence` helper from [powershell-baseline.md §4](../../_shared/powershell-baseline.md#4-evidence-emission-sha-256-integrity). Copy the function from the baseline into your script library or dot-source it.

---

## Collector 1 — Per-environment security configuration

```powershell
function Get-Control37EnvironmentPosture {
    [CmdletBinding()]
    param(
        [string]$EnvironmentName
    )

    $envs = if ($EnvironmentName) {
        @(Get-AdminPowerAppEnvironment -EnvironmentName $EnvironmentName)
    } else {
        Get-AdminPowerAppEnvironment
    }

    $results = foreach ($env in $envs) {
        $detail = Get-AdminPowerAppEnvironment -EnvironmentName $env.EnvironmentName
        $props  = $detail.Internal.properties

        [PSCustomObject]@{
            EnvironmentId            = $env.EnvironmentName
            DisplayName              = $env.DisplayName
            EnvironmentType          = $env.EnvironmentType
            HasDataverse             = $detail.CommonDataServiceDatabaseProvisioningState -eq 'Succeeded'
            IsManagedEnvironment     = [bool]$props.governanceConfiguration.enableManagedEnvironment
            SecurityGroupAssigned    = [bool]$props.linkedEnvironmentMetadata.securityGroupId
            CreatedTimeUtc           = $env.CreatedTime
            CollectedUtc             = (Get-Date).ToUniversalTime().ToString('o')
        }
    }

    return $results
}
```

> The cmdlet does not return Privacy + Security settings (blocked attachments, inactivity timeout, CSP, etc.) — those live in Dataverse `organization` table and require Dataverse Web API or `Get-CrmOrganization` access. Capture them via the per-environment manual review in [portal walkthrough Step 7](portal-walkthrough.md), or extend this collector with Dataverse Web API calls if you have an authorized service principal.

---

## Collector 2 — DLP policy coverage

```powershell
function Get-Control37DlpCoverage {
    [CmdletBinding()] param()

    $envs     = Get-AdminPowerAppEnvironment
    $policies = Get-DlpPolicy

    foreach ($env in $envs) {
        $tenantWide = $policies | Where-Object {
            $_.environmentType -in @('AllEnvironments','OnlyEnvironments') -or
            ($_.environments -and $_.environments.name -contains $env.EnvironmentName)
        }
        [PSCustomObject]@{
            EnvironmentId   = $env.EnvironmentName
            DisplayName     = $env.DisplayName
            PolicyCount     = ($tenantWide | Measure-Object).Count
            PolicyNames     = ($tenantWide.DisplayName -join '; ')
            HasCoverage     = ($tenantWide | Measure-Object).Count -gt 0
            CollectedUtc    = (Get-Date).ToUniversalTime().ToString('o')
        }
    }
}
```

> `Get-DlpPolicy` shape varies between module versions; the snippet handles both the legacy `environments` array and the newer `environmentType` discriminator. Verify against your pinned module version (baseline §1).

---

## Collector 3 — Tenant settings snapshot

```powershell
function Get-Control37TenantSettings {
    [CmdletBinding()] param()

    $tenant = Get-TenantSettings
    [PSCustomObject]@{
        TenantIsolationEnabled = $tenant.powerPlatform.tenantIsolation.isDisabled -eq $false
        DisableDeveloperEnvironmentCreationByNonAdminUsers = $tenant.disableDeveloperEnvironmentCreationByNonAdminUsers
        DisableEnvironmentCreationByNonAdminUsers          = $tenant.disableEnvironmentCreationByNonAdminUsers
        WalkMeOptOut                                       = $tenant.walkMeOptOut
        CollectedUtc                                       = (Get-Date).ToUniversalTime().ToString('o')
    }
}
```

---

## Orchestrator — produce posture report with SHA-256 evidence

```powershell
<#
.SYNOPSIS
    Control 3.7 posture collector and report generator (read-only).

.DESCRIPTION
    Collects per-environment security posture, DLP coverage, and tenant settings.
    Emits JSON evidence with SHA-256 hashes and a manifest, plus a human-readable HTML report.
    DOES NOT mutate tenant state.

.PARAMETER Endpoint
    Power Platform endpoint: prod (default).

.PARAMETER EvidencePath
    Output directory for evidence and report. Defaults to .\evidence-3.7.

.EXAMPLE
    .\New-Control37PostureReport.ps1 -Endpoint prod -EvidencePath .\evidence-3.7
#>
[CmdletBinding()]
param(
    [string]$Endpoint = 'prod',

    [string]$EvidencePath = ".\evidence-3.7"
)

$ErrorActionPreference = 'Stop'

# Edition guard (baseline §2)
if ($PSVersionTable.PSEdition -ne 'Desktop') {
    throw "Run under Windows PowerShell 5.1 (Desktop) — see baseline §2."
}

New-Item -ItemType Directory -Force -Path $EvidencePath | Out-Null
$ts = Get-Date -Format 'yyyyMMdd-HHmmss'
Start-Transcript -Path "$EvidencePath\transcript-$ts.log" -IncludeInvocationHeader

try {
    # Commercial cloud sign-in
    Add-PowerAppsAccount -Endpoint $Endpoint | Out-Null
    Connect-MgGraph -Environment 'Global' -Scopes 'SecurityEvents.Read.All','Policy.Read.All' -NoWelcome | Out-Null

    Write-Host "Collecting environment posture..." -ForegroundColor Cyan
    $envPosture = Get-Control37EnvironmentPosture

    Write-Host "Collecting DLP coverage..." -ForegroundColor Cyan
    $dlpCoverage = Get-Control37DlpCoverage

    Write-Host "Collecting tenant settings..." -ForegroundColor Cyan
    $tenantSettings = Get-Control37TenantSettings

    # Compose summary (FSI-defensible: report inputs, not just headline numbers)
    $managedCount = ($envPosture | Where-Object IsManagedEnvironment).Count
    $sgCount      = ($envPosture | Where-Object SecurityGroupAssigned).Count
    $dlpCovered   = ($dlpCoverage | Where-Object HasCoverage).Count

    $summary = [PSCustomObject]@{
        ControlId                    = '3.7'
        FrameworkVersion             = 'v1.3.3'
        Endpoint                     = $Endpoint
        GeneratedUtc                 = (Get-Date).ToUniversalTime().ToString('o')
        EnvironmentCount             = $envPosture.Count
        ManagedEnvironmentCount      = $managedCount
        SecurityGroupCoverageCount   = $sgCount
        DlpCoverageCount             = $dlpCovered
        TenantIsolationEnabled       = $tenantSettings.TenantIsolationEnabled
        Notes                        = 'Security score (Preview) NOT collected via PowerShell — capture from PPAC Security > Overview manually and archive screenshot.'
    }

    # Emit SHA-256-hashed evidence (baseline §4)
    Write-FsiEvidence -Object $envPosture     -Name 'environment-posture'    -EvidencePath $EvidencePath | Out-Null
    Write-FsiEvidence -Object $dlpCoverage    -Name 'dlp-coverage'           -EvidencePath $EvidencePath | Out-Null
    Write-FsiEvidence -Object $tenantSettings -Name 'tenant-settings'        -EvidencePath $EvidencePath | Out-Null
    Write-FsiEvidence -Object $summary        -Name 'control-3.7-summary'    -EvidencePath $EvidencePath | Out-Null

    Write-Host "[PASS] Control 3.7 posture collected. Evidence at $EvidencePath" -ForegroundColor Green
}
catch {
    Write-Host "[FAIL] $($_.Exception.Message)" -ForegroundColor Red
    Write-Host $_.ScriptStackTrace -ForegroundColor Yellow
    exit 1
}
finally {
    Stop-Transcript | Out-Null
}
```

---

## What this script does NOT cover

The collector is intentionally bounded. The following items must be evidenced via other means:

| Item | How to evidence |
|------|----------------|
| Security score (Preview) | Manual screenshot of `PPAC > Security > Overview` — not exposed via supported PowerShell or Graph API |
| Recommendations list, severity, refresh date | Manual review of `PPAC > Actions` page or use the Power Platform for Admin v2 connector in a Power Automate flow |
| Dismissed / snoozed recommendations | Manual export from `PPAC > Actions > Dismissed recommendations` and `Snoozed recommendations` |
| Per-environment Privacy + Security (blocked attachments, MIME, timeout, CSP) | Dataverse Web API against `organization` entity, or manual review per environment |
| Defender for Cloud Apps AI agent inventory | Microsoft Defender portal; Graph Security API where available |

> Document each manual evidence item in the same evidence package and add its file to the SHA-256 manifest using `Write-FsiEvidence`.

---

## Scheduling

For Zone 3 environments run weekly via a service principal in Azure Automation or a hardened build agent. Pin module versions (baseline §1), enable verbose logging, and write evidence to a WORM-protected store (Purview Data Lifecycle retention lock or Azure Storage immutability policy) per SEC 17a-4(f).

---

[Back to Control 3.7](../../../controls/pillar-3-reporting/3.7-ppac-security-posture-assessment.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification & Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
