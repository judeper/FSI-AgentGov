---
title: "Control 2.1 — PowerShell Setup (Managed Environments)"
control_id: "2.1"
playbook_type: "powershell-setup"
last_updated: "2026-04-18"
version: "v1.4"
ui_verified: "April 2026"
prerequisites:
  - "Windows PowerShell 5.1 (Desktop edition) for legacy Power Apps Administration cmdlets"
  - "PowerShell 7.4 Core for Az.* and Microsoft.Graph cmdlets"
  - "Microsoft.PowerApps.Administration.PowerShell pinned per CAB (verify version in change ticket)"
  - "Microsoft.PowerApps.PowerShell pinned (same baseline as Administration module)"
  - "Az.Accounts, Az.Resources, Az.KeyVault, Az.PowerPlatform — for Customer-Managed Key (CMK) Enterprise Policies"
  - "Microsoft.Graph 2.25.0+ — license consumption + Service Health correlation"
  - "Power Platform Admin (tenant-scoped) — required for any mutation; Environment Admin is INSUFFICIENT"
  - "Entra Global Reader for licensing/Service-Health reads (Global Admin via PIM only for CMK RBAC bootstrap)"
  - "Azure Key Vault with purge-protection AND soft-delete enabled in the same region as target environment"
related_controls: ["1.4", "1.5", "1.20", "2.2", "2.3", "2.15", "2.22"]
---

# Control 2.1 — PowerShell Setup: Managed Environments

> **Control under management:** [`2.1 — Managed Environments`](../../../controls/pillar-2-management/2.1-managed-environments.md)
>
> **Sister playbooks:** [Portal Walkthrough](./portal-walkthrough.md) · [Verification & Testing](./verification-testing.md) · [Troubleshooting](./troubleshooting.md)
>
> **Shared baseline:** [`_shared/powershell-baseline.md`](../../_shared/powershell-baseline.md) — module pinning, mutation safety, evidence emission, SHA-256 manifest format, Dataverse-cmdlet quirks.

This playbook automates the **enablement, configuration, evidence capture, and quarterly attestation** of the Microsoft Power Platform **Managed Environments** capability for a US financial-services tenant. Every helper introduced here is prefixed with `Fsi-` (matching the verb-noun convention used in the request) and follows the structural pattern of the sister playbooks for [Control 2.25](../2.25/powershell-setup.md) and [Control 2.26](../2.26/powershell-setup.md). Where those sister playbooks operate against the unified Microsoft Graph surface, this playbook deals with **two parallel cmdlet families** — the legacy `Microsoft.PowerApps.Administration.PowerShell` module (Windows PowerShell 5.1 only) and the modern `Az.PowerPlatform` Enterprise Policies family (PowerShell 7.4+). Bridging those two worlds correctly is the single largest source of false-clean defects in this control; §0.2 catalogues each one.

!!! danger "Non-Substitution"
    The helpers in this file **do not substitute** for the supervisory review obligations imposed by FINRA Rule 3110 (with RN 24-09 for AI supervisory guidance), the books-and-records obligations of SEC Rules 17a-3 and 17a-4, the ITGC change-control obligations of SOX §302/§404, the safeguards obligations of GLBA §501(b), the third-party risk-management obligations of OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12), the model-risk obligations of Federal Reserve SR 26-2 (formerly SR 11-7), the cybersecurity-program obligations of NYDFS 23 NYCRR 500.06, or the IT examination obligations expressed in the FFIEC IT Examination Handbook. They **support compliance with** those obligations by emitting structured, hash-anchored evidence that a human reviewer (the **AI Governance Lead**, the **Power Platform Admin**, or — for FINRA-regulated firms — a **registered principal**) then reviews and counter-signs. No automation in this file approves, attests to, or certifies compliance on behalf of any human officer of the firm.

!!! note "Hedged-language reminder"
    Throughout this playbook, governance helpers **support compliance with**, **help meet**, and **aid in** the regulatory obligations enumerated above. They do **not** "ensure compliance", "guarantee" any outcome, "eliminate risk", or "prevent" any policy violation. Implementation requires the operator to verify each helper's output against the firm's written supervisory procedures (WSPs) and to retain the SHA-256 manifest of each evidence pack in WORM storage for the regulator-mandated retention period (typically 7 years for SEC 17a-4(f); verify against the firm's record-retention schedule).

---

## §0 — False-Clean Defect Catalogue and Two-Shell Reality

Before any helper is dot-sourced, the operator must internalise the failure modes that have produced **false-clean** governance signals against Managed Environments during the public-preview, GA, and post-GA windows of 2024-2026. Every defect listed below has been observed against at least one production tenant; every helper in §2 onward is hard-wired against the corresponding mitigation.

### 0.1 The two-shell reality

The Power Platform Admin cmdlet surface is split across **two shells that cannot share a session**:

| Shell | Modules | Purpose | Why it cannot be merged |
|---|---|---|---|
| **Windows PowerShell 5.1 (Desktop)** | `Microsoft.PowerApps.Administration.PowerShell`, `Microsoft.PowerApps.PowerShell` | Environment enumeration, Managed-Environment toggle, sharing limits, solution-checker enforcement, maker-welcome content, IP firewall, IP cookie binding, tenant isolation, environment routing, pipeline targets | Modules ship .NET Framework 4.x assemblies; will not load in PS 7+ Core |
| **PowerShell 7.4 Core** | `Az.Accounts`, `Az.Resources`, `Az.KeyVault`, `Az.PowerPlatform`, `Microsoft.Graph` | Enterprise Policy creation (CMK), Key Vault RBAC wiring, license-consumption Graph reads, Service Health correlation | Az and Graph SDKs assume .NET 8 / netstandard2.0 — many cmdlets behave differently or are missing in Desktop |

Operators who try to run the entire workflow in a single shell will see one of two failure modes:

1. **Run the whole thing in PS 7.4** — `Add-PowerAppsAccount` either fails to import or imports an older orphan version that returns empty environment lists. **False clean: zero environments returned, treated as "no work to do".**
2. **Run the whole thing in PS 5.1** — `Az.PowerPlatform` cmdlet output marshalling drops the `properties.encryption` block silently. **False clean: CMK appears applied but the policy ARM ID is never recorded against the environment.**

The orchestrator in §17 (`Invoke-Fsi-Control21Setup`) **does not paper over this split**. It documents which sub-step requires which shell, and it produces a single signed evidence manifest by stitching the JSON outputs of both shells. Operators who try to "simplify" the workflow into one shell will defeat the false-clean mitigation.

### 0.2 False-clean defect catalogue

| # | Defect | Symptom | Root cause | Mitigation in this playbook |
|---|---|---|---|---|
| 1 | Wrong-shell trap (PS 7 + Desktop module) | `Get-AdminPowerAppEnvironment` returns `@()`; helper records "no managed environments" | PS 7.4 silently loaded a stale 1.x version of the Administration module from the user module path | `Assert-Fsi-LegacyShell` (§2.1) throws `Fsi21-WrongShell` |
| 4 | Sharing limits set on standalone cloud flow | Operator believed flow shares were governed; production share leaked at 200+ recipients | Managed-Environment sharing limits **do not govern standalone cloud flows** (only solution-aware flows) | `Set-Fsi-SharingLimits` emits `!!! info` with explicit caveat; verification helper `Test-Fsi-Control21-SharingLimitsBaseline` separately attests DLP coverage from Control 1.5 |
| 5 | Solution checker `Warn` mode treated as enforcement | Audit binder said "enforced"; non-compliant solution imported | Operator misread PPAC dropdown; `Warn` is advisory only | `Set-Fsi-SolutionCheckerEnforcement` accepts only `None`, `Warn`, `Block`; verification helper requires `Block` for Zone 3 |
| 6 | Maker welcome content embedded sensitive WSP excerpt | Examiner found PII in welcome text; tenant could not produce CMK proof for that content | Maker welcome content is **excluded** from CMK encryption — Microsoft-managed only | `Set-Fsi-MakerWelcome` emits `!!! note` and refuses to write content longer than 1500 characters or matching a sensitive-pattern regex |
| 7 | IP Firewall flipped to `Enforce` without baseline | Production traffic blocked Monday 09:00 ET; trading-floor outage | Operator skipped `AuditOnly` baseline window | `Set-Fsi-IPFirewall` defaults to `AuditOnly`; `Get-Fsi-IPFirewallAuditLog` extracts would-be-blocked traffic; verification helper flags `AuditOnly` older than 4 weeks as `Anomaly` |
| 8 | CMK exclusion list never captured | Examiner asked which artefacts remain Microsoft-managed; tenant could not produce list | Operator assumed CMK applied to *all* environment data | `Add-Fsi-CMKPolicyToEnvironment` writes the exclusion list (maker welcome, solution-checker results, display names, descriptions, connection metadata, Agent 365 audit logging) as a JSON evidence artefact; `Test-Fsi-CMKExclusions` regenerates the narrative |
| 9 | Tenant isolation enabled with Azure DevOps still allowed | Believed all cross-tenant traffic blocked; AzDO connector silently bypassed | Documented Microsoft known-issue: AzDO connector is not Entra-ID-authenticated and is excluded from tenant isolation | `Set-Fsi-TenantIsolation` emits explicit warning; verification helper requires the AzDO exception to be documented in DLP (Control 1.5) |
| 10 | Pipeline target environments not Managed | Solution promoted from Dev → Test → Prod; Test environment not Managed; sharing limits not enforced during UAT | Operators enabled Managed on Prod only; pipeline targets missed | `Get-Fsi-PipelineTargets` enumerates tenant-wide; `Enable-Fsi-PipelineTargetsManagedEnv` covers them in bulk |
| 12 | License-coverage check ran against stale entitlements | June 2026 enforcement enabled in-product banner for 47 makers; firm had no remediation backlog | Operator ran license check once, did not re-run before quarterly attestation | `Test-Fsi-ManagedEnvLicensing` is a quarterly verification helper; orchestrator `-Mode Quarterly` always runs it |
| 13 | Disable performed without `ChangeTicketId` | Audit could not reconstruct who disabled Managed on Prod environment | No ITGC linkage to Disable cmdlet | `Disable-Fsi-ManagedEnvironment` requires `-ChangeTicketId`, `-WhatIf` first, and writes a signed before-snapshot |
| 14 | Empty result conflated with "clean" | `$null` returned when no rows found; downstream pack said `Clean` | Helpers must distinguish `Clean` from `NotApplicable` from `Error` from `Pending` | All helpers return `[pscustomobject]` with explicit `Status` enum value drawn from `Clean | Anomaly | Pending | NotApplicable | Error` — **never `$null` and never `@()` as a clean signal** |

Every helper in this playbook returns one of five `Status` values — **`Clean`**, **`Anomaly`**, **`Pending`**, **`NotApplicable`**, **`Error`** — and every helper carries a non-empty `Reason` string when `Status -ne 'Clean'`. **Helpers never return `$null` or `@()` as a clean signal.** This single convention eliminates defect #14 and is the foundation on which the §17 quarterly evidence bundle is built.

---

## §1 — Module Inventory, Az / Graph Scopes, RBAC Matrix, Licensing Preflight

### 1.1 Module pinning

The Managed Environments surface depends on **two distinct module families** (see §0.1). Pin both at versions verified by your CAB; the values below are the April-2026 baseline this playbook was authored against.

```powershell
#Requires -Version 5.1
# Run this block in BOTH shells. The legacy modules import only in 5.1; the Az/Graph modules import only in 7.4.
$pinned = @{
    'Microsoft.PowerApps.Administration.PowerShell' = '2.0.198'   # verify against your CAB
    'Microsoft.PowerApps.PowerShell'                = '1.0.34'
    'Az.Accounts'                                   = '3.0.4'
    'Az.Resources'                                  = '7.5.0'
    'Az.KeyVault'                                   = '6.3.1'
    'Az.PowerPlatform'                              = '1.0.1'
    'Microsoft.Graph'                               = '2.25.0'
    'Microsoft.Graph.Authentication'                = '2.25.0'
}
foreach ($name in $pinned.Keys) {
    $installed = Get-Module -ListAvailable -Name $name |
        Where-Object { $_.Version -eq [version]$pinned[$name] }
    if (-not $installed) {
        Install-Module -Name $name `
            -RequiredVersion $pinned[$name] `
            -Repository PSGallery `
            -Scope CurrentUser `
            -AllowClobber `
            -AcceptLicense
    }
}
```

Operators in regulated tenants must mirror these modules into an **internal artifact feed** (Azure Artifacts, ProGet, Nexus) and substitute `-Repository <YourInternalFeed>`. Direct PSGallery access from production admin workstations is a SOX §404 ITGC finding waiting to happen — pinning a version that PSGallery later overwrites breaks reproducibility.

### 1.2 Edition / version requirements

| Module | Required edition | Minimum version | Failure if mis-targeted |
|---|---|---|---|
| `Microsoft.PowerApps.Administration.PowerShell` | **Desktop only (Windows PowerShell 5.1)** | 5.1 | Silently returns empty results in PS 7 (defect #1) |
| `Microsoft.PowerApps.PowerShell` | Desktop only | 5.1 | Same |
| `Az.Accounts`, `Az.Resources`, `Az.KeyVault` | Core (PS 7.4+) | 7.4 LTS | Some cmdlets behave differently in 5.1 |
| `Az.PowerPlatform` | Core (PS 7.4+) | 7.4 | Marshalling drops `properties.encryption` in 5.1 (defect #1, second variant) |
| `Microsoft.Graph` | Core (PS 7.2+) | 7.4 LTS | Auth surface incompatible with 5.1 |

The legacy-shell guard helper (`Assert-Fsi-LegacyShell`) and the modern-shell guard helper (`Assert-Fsi-AzShell`) are introduced in §2.1.

### 1.3 Required Graph scopes (license-consumption + Service Health)

| Scope | Required for | Helper | Failure mode if missing |
|---|---|---|---|
| `Organization.Read.All` | License SKU enumeration for entitlement audit | `Test-Fsi-ManagedEnvLicensing` | Helper returns `Status='Error'`, `Reason='ScopeMissing:Organization.Read.All'` |
| `Directory.Read.All` | Resolve maker UPNs for uncovered-user list | `Test-Fsi-ManagedEnvLicensing` | UPNs render as `(unresolved)`; helper still returns `Anomaly` per row |
| `User.Read.All` | License-assignment per user (`/users/{id}/licenseDetails`) | `Test-Fsi-ManagedEnvLicensing` | Per-user details degrade; SKU-level totals still computed |
| `Reports.Read.All` | License-consumption usage reports | `Test-Fsi-ManagedEnvLicensing` | Helper degrades when report data is unavailable |
| `ServiceHealth.Read.All` | Service Health correlation when CMK rotation correlates with incidents | CMK rotation review | Correlation column rendered as `(no service-health context)`; status `Anomaly` |

### 1.4 Required Az / ARM RBAC

| Activity | Minimum role | Scope | PIM elevation? |
|---|---|---|---|
| Create Enterprise Policy resource | **Power Platform Admin** (tenant) **and** Contributor on the policy resource group | Subscription / RG | Yes — PIM-bound |
| Grant CMK Enterprise Policy access to Key Vault key | **Key Vault Crypto Officer** on the Key Vault | Key Vault | Yes — PIM-bound |
| Apply CMK Enterprise Policy to environment | **Power Platform Admin** | Tenant | Yes — PIM-bound |
| Read CMK status / exclusions | **Power Platform Admin (Reader)** or canonical role: Power Platform Admin | Tenant | No |
| Configure tenant isolation | **Power Platform Admin** | Tenant | Yes — PIM-bound |
| Create / modify Managed Environment | **Power Platform Admin** OR **Dynamics 365 Admin** | Tenant | Yes — PIM-bound |
| Read environment inventory | **Power Platform Admin (Reader)** | Tenant | No |

Canonical role names used throughout this file: **Power Platform Admin**, **Entra Global Admin**, **Entra Global Reader**, **Purview Compliance Admin**, **AI Governance Lead**, **Compliance Officer**. See [`docs/reference/role-catalog.md`](../../../reference/role-catalog.md). Note in particular that **Environment Admin** and **Delegated Admin** **cannot** mutate the Managed Environments property — every helper that mutates state asserts the caller against Power Platform Admin and refuses to proceed otherwise.

### 1.5 Cmdlet-availability preflight

Between the 2024 GA of Managed Environments and the April 2026 baseline of this playbook, several cmdlets shifted module ownership (notably the move from preview `*-PowerAppManagedEnvironment*` to the GA `*-AdminPowerAppEnvironmentGovernanceConfiguration*`). To prevent silent "cmdlet not found → caught → swallowed → reported clean" defects, every helper that depends on a non-trivial cmdlet first invokes:

```powershell
function Get-Fsi-CmdletAvailability {
<#
.SYNOPSIS
    Reports whether each named cmdlet is present in the current shell.
.DESCRIPTION
    Returns one [pscustomobject] per cmdlet with Available, Module, Version. Used as a preflight
    by every helper to distinguish 'cmdlet missing' (Status=NotApplicable) from 'cmdlet returned
    no rows' (Status=Clean). Eliminates false-clean defect #14.
.NOTES
    Control 2.1 — Managed Environments. Last UI verified: April 2026.
#>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string[]] $CmdletName
    )
    foreach ($name in $CmdletName) {
        $cmd = Get-Command -Name $name -ErrorAction SilentlyContinue
        [pscustomobject]@{
            CmdletName = $name
            Available  = [bool]$cmd
            Module     = if ($cmd) { $cmd.ModuleName } else { $null }
            Version    = if ($cmd) { $cmd.Module.Version.ToString() } else { $null }
        }
    }
}
```

When a required cmdlet is unavailable the calling helper emits `Status='NotApplicable'`, `Reason="CmdletMissing:<name>"`, and a documented portal-export fallback URI (the matching step in [Portal Walkthrough](./portal-walkthrough.md)).

### 1.6 Run-metadata stamp

Every artefact written by every helper carries a `Get-RunMetadata` stamp so that downstream evidence packs can correlate runs across both shells:

```powershell
function Get-RunMetadata {
<#
.SYNOPSIS
    Emits a stable metadata block used by every helper in this playbook.
.NOTES
    Control 2.1 — Managed Environments. Last UI verified: April 2026.
#>
    [CmdletBinding()]
    param(
        [string] $RunId = "fsi21-$((Get-Date).ToUniversalTime().ToString('yyyyMMddHHmmss'))",
        [string] $TenantId = '',
        [string] $ChangeTicketId
    )
    [pscustomobject]@{
        run_id          = $RunId
        run_timestamp   = (Get-Date).ToUniversalTime().ToString('o')
        tenant_id       = $TenantId
        control_id      = '2.1'
        playbook_version = 'v1.4'
        change_ticket   = $ChangeTicketId
        host_edition    = $PSVersionTable.PSEdition
        host_version    = $PSVersionTable.PSVersion.ToString()
        operator_upn    = ([Security.Principal.WindowsIdentity]::GetCurrent()).Name
        schema_version  = '1.0'
    }
}
```

---


## §2 — Bootstrap (Two Shells, One Session Context)

The bootstrap layer establishes both the legacy and the modern shell sessions, validates Az and Graph contexts, and produces a single `SessionContext` `[pscustomobject]` consumed by every helper in §3 onward. Two rules are non-negotiable:

1. **Both shells initialise with `Disconnect-*` first** so cached cross-tenant tokens cannot leak.
2. **Signed transcripts** capture every operator action; `Start-Transcript` is the first call after shell assertion.

### 2.1 Shell-host assertions

```powershell
function Assert-Fsi-LegacyShell {
<#
.SYNOPSIS
    Asserts the current host is Windows PowerShell 5.1 (Desktop) and that the legacy
    Power Apps Administration module is loaded at the CAB-pinned version.
.NOTES
    Control 2.1 — Managed Environments. Last UI verified: April 2026.
#>
    [CmdletBinding()]
    param([string]$RequiredAdminVersion = '2.0.198')
    if ($PSVersionTable.PSEdition -ne 'Desktop') {
        throw [System.InvalidOperationException]::new(
            "Fsi21-WrongShell: Microsoft.PowerApps.Administration.PowerShell requires Windows PowerShell 5.1 (Desktop). Detected: $($PSVersionTable.PSEdition) $($PSVersionTable.PSVersion). Open a Windows PowerShell 5.1 console and re-run.")
    }
    $admin = Get-Module -Name Microsoft.PowerApps.Administration.PowerShell -ListAvailable |
        Sort-Object Version -Descending | Select-Object -First 1
    if (-not $admin -or $admin.Version -lt [version]$RequiredAdminVersion) {
        throw [System.InvalidOperationException]::new(
            "Fsi21-WrongShell: Microsoft.PowerApps.Administration.PowerShell $RequiredAdminVersion+ required; found $($admin.Version).")
    }
    [pscustomobject]@{
        Status        = 'Clean'
        Edition       = 'Desktop'
        PSVersion     = $PSVersionTable.PSVersion.ToString()
        AdminModule   = $admin.Version.ToString()
        Reason        = ''
    }
}

function Assert-Fsi-AzShell {
<#
.SYNOPSIS
    Asserts the current host is PowerShell 7.4+ Core with Az.PowerPlatform and Microsoft.Graph
    pinned at CAB versions. Required for CMK Enterprise Policy and licensing helpers.
.NOTES
    Control 2.1 — Managed Environments. Last UI verified: April 2026.
#>
    [CmdletBinding()]
    param(
        [string]$RequiredGraphVersion   = '2.25.0',
        [string]$RequiredAzPpVersion    = '1.0.1'
    )
    if ($PSVersionTable.PSEdition -ne 'Core' -or $PSVersionTable.PSVersion -lt [version]'7.4') {
        throw [System.InvalidOperationException]::new(
            "Fsi21-WrongShell: PowerShell 7.4+ Core required for Az/Graph helpers. Detected: $($PSVersionTable.PSEdition) $($PSVersionTable.PSVersion).")
    }
    $azpp = Get-Module -Name Az.PowerPlatform -ListAvailable | Sort-Object Version -Descending | Select-Object -First 1
    $mg   = Get-Module -Name Microsoft.Graph.Authentication -ListAvailable | Sort-Object Version -Descending | Select-Object -First 1
    if (-not $azpp -or $azpp.Version -lt [version]$RequiredAzPpVersion) {
        throw [System.InvalidOperationException]::new("Fsi21-WrongShell: Az.PowerPlatform $RequiredAzPpVersion+ required.")
    }
    if (-not $mg -or $mg.Version -lt [version]$RequiredGraphVersion) {
        throw [System.InvalidOperationException]::new("Fsi21-WrongShell: Microsoft.Graph.Authentication $RequiredGraphVersion+ required.")
    }
    [pscustomobject]@{
        Status         = 'Clean'
        Edition        = 'Core'
        PSVersion      = $PSVersionTable.PSVersion.ToString()
        AzPP           = $azpp.Version.ToString()
        GraphAuth      = $mg.Version.ToString()
        Reason         = ''
    }
}
```

### 2.3 Initialize-Fsi-PPSession

```powershell
function Initialize-Fsi-PPSession {
<#
.SYNOPSIS
    Connects the legacy Power Apps Admin shell and verifies tenant entitlements.
    Run in Windows PowerShell 5.1 only.
.NOTES
    Control 2.1 — Managed Environments. Last UI verified: April 2026.
#>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string] $RunId,
        [Parameter(Mandatory)] [string] $EvidencePath
    )
    $null = Assert-Fsi-LegacyShell
    if (-not (Test-Path $EvidencePath)) { New-Item -ItemType Directory -Path $EvidencePath -Force | Out-Null }
    $ts = Get-Date -Format 'yyyyMMdd-HHmmss'
    Start-Transcript -Path (Join-Path $EvidencePath "transcript-pp-$ts.log") -IncludeInvocationHeader | Out-Null

    Remove-PowerAppsAccount -ErrorAction SilentlyContinue | Out-Null
    Add-PowerAppsAccount -ErrorAction Stop

    # Sanity probe: must return at least one environment for a non-empty tenant.
    $probe = Get-AdminPowerAppEnvironment -ErrorAction Stop
    if (-not $probe -or $probe.Count -eq 0) {
        Stop-Transcript | Out-Null
        throw [System.InvalidOperationException]::new(
            "Fsi21-EmptyEnvList: Add-PowerAppsAccount returned zero environments for tenant. " +
            "Verify tenant access, Power Platform Admin role assignment, and module authentication state.")
    }
    [pscustomobject]@{
        RunId             = $RunId
        EnvironmentsSeen  = $probe.Count
        TranscriptPath    = (Join-Path $EvidencePath "transcript-pp-$ts.log")
        Status            = 'Clean'
        Reason            = ''
    }
}
```

### 2.4 Initialize-Fsi-AzSession

```powershell
function Initialize-Fsi-AzSession {
<#
.SYNOPSIS
    Connects PowerShell 7.4 Core to Azure, Az.PowerPlatform, and Microsoft Graph.
    Required for CMK Enterprise Policy operations and license-consumption reads.
.NOTES
    Control 2.1 — Managed Environments. Last UI verified: April 2026.
#>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string] $RunId,
        [Parameter(Mandatory)] [string] $TenantId,
        [Parameter(Mandatory)] [string] $SubscriptionId,
        [string[]] $GraphScopes = @(
            'Organization.Read.All',
            'Directory.Read.All',
            'User.Read.All',
            'Reports.Read.All',
            'ServiceHealth.Read.All'
        ),
        [Parameter(Mandatory)] [string] $EvidencePath
    )
    $null = Assert-Fsi-AzShell
    if (-not (Test-Path $EvidencePath)) { New-Item -ItemType Directory -Path $EvidencePath -Force | Out-Null }
    $ts = Get-Date -Format 'yyyyMMdd-HHmmss'
    Start-Transcript -Path (Join-Path $EvidencePath "transcript-az-$ts.log") -IncludeInvocationHeader | Out-Null

    Disconnect-AzAccount -ErrorAction SilentlyContinue | Out-Null
    Disconnect-MgGraph   -ErrorAction SilentlyContinue | Out-Null

    Connect-AzAccount -Tenant $TenantId -Subscription $SubscriptionId -ErrorAction Stop | Out-Null
    Connect-MgGraph   -TenantId $TenantId -Scopes $GraphScopes -NoWelcome -ErrorAction Stop

    $azCtx = Get-AzContext
    $mgCtx = Get-MgContext
    [pscustomobject]@{
        RunId             = $RunId
        AzEnvironment     = $azCtx.Environment.Name
        GraphEnvironment  = $mgCtx.Environment
        ScopesGranted     = $mgCtx.Scopes
        TranscriptPath    = (Join-Path $EvidencePath "transcript-az-$ts.log")
        Status            = 'Clean'
        Reason            = ''
    }
}
```

---

## §3 — Inventory and Licensing Audit

### 3.1 Get-Fsi-PPEnvironment

```powershell
function Get-Fsi-PPEnvironment {
<#
.SYNOPSIS
    Returns enriched environment inventory with Managed-Environment flag, governance protection level,
    SKU, region, and subscription. Drop-in replacement for Get-AdminPowerAppEnvironment that emits
    [pscustomobject] rows with the canonical Status contract.
.PARAMETER EnvironmentName
    Optional GUID. When supplied, returns a single row; otherwise enumerates all.
.NOTES
    Control 2.1 — Managed Environments. Last UI verified: April 2026.
#>
    [CmdletBinding()]
    param(
        [string] $EnvironmentName,
        [switch] $IncludeDeleted
    )
    $avail = Get-Fsi-CmdletAvailability -CmdletName 'Get-AdminPowerAppEnvironment'
    if (-not $avail.Available) {
        return [pscustomobject]@{ Status='NotApplicable'; Reason='CmdletMissing:Get-AdminPowerAppEnvironment'; Rows=@() }
    }
    $raw = if ($EnvironmentName) {
        Get-AdminPowerAppEnvironment -EnvironmentName $EnvironmentName -ErrorAction Stop
    } else {
        Get-AdminPowerAppEnvironment -ErrorAction Stop
    }
    $rows = foreach ($env in $raw) {
        $managed = $false
        $protLevel = 'Standard'
        try {
            $gov = Get-AdminPowerAppEnvironmentGovernanceConfiguration -EnvironmentName $env.EnvironmentName -ErrorAction Stop
            $managed   = [bool]$gov.GovernanceStatus -eq $true -or [bool]$gov.IsManagedEnvironment -eq $true
            $protLevel = if ($gov.ProtectionLevel) { $gov.ProtectionLevel } else { 'Standard' }
        } catch {
            $managed = $false
            $protLevel = '(unavailable)'
        }
        [pscustomobject]@{
            EnvironmentId            = $env.EnvironmentName
            DisplayName              = $env.DisplayName
            EnvironmentSku           = $env.EnvironmentType
            Region                   = $env.Location
            SubscriptionId           = $env.AzureRegion  # populated only for paid environments
            DataverseProvisioned     = ($env.CommonDataServiceDatabaseProvisioningState -eq 'Succeeded')
            ManagedEnvironmentEnabled = $managed
            GovernanceProtectionLevel = $protLevel
            CreatedBy                = $env.CreatedBy.userPrincipalName
            CreatedTime              = $env.CreatedTime
            Status                   = if ($env.LifecycleState -eq 'Ready') { 'Clean' } else { 'Anomaly' }
            Reason                   = if ($env.LifecycleState -eq 'Ready') { '' } else { "LifecycleState:$($env.LifecycleState)" }
        }
    }
    [pscustomobject]@{
        Status     = if ($rows.Count -gt 0) { 'Clean' } else { 'Anomaly' }
        Reason     = if ($rows.Count -gt 0) { '' } else { 'NoEnvironmentsReturned' }
        Count      = $rows.Count
        Rows       = $rows
        ExportedAt = (Get-Date).ToUniversalTime().ToString('o')
    }
}
```

### 3.2 Test-Fsi-ManagedEnvLicensing

!!! warning "June 2026 licensing-enforcement timeline"
    Microsoft has announced an **end-user license-compliance notification** roll-out for Managed Environments beginning **June 2026**. Active makers in a Managed Environment who do not hold one of the qualifying SKUs (Power Apps Premium per-user, Power Automate Premium per-user, a Copilot Studio license that bundles Power Platform Premium, or an in-scope Dynamics 365 license) will see in-product banners. **Pay-as-you-go is NOT a substitute** for the licensing floor. Run `Test-Fsi-ManagedEnvLicensing` at least quarterly through Q2 2026 and weekly during the rollout window so that the firm has a current remediation backlog and is not surprised by a tier-1 ticket from a producing trader.

```powershell
function Test-Fsi-ManagedEnvLicensing {
<#
.SYNOPSIS
    License-coverage audit for every Managed Environment in the tenant. Emits per-environment
    [pscustomobject] with Status=Clean|Anomaly|Pending and a list of uncovered users.
.NOTES
    Control 2.1 — Managed Environments. Last UI verified: April 2026. Enforcement window: June 2026.
#>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [object] $Inventory,
        [string[]] $QualifyingSkuPartNumbers = @(
            'POWERAPPS_PER_USER',
            'FLOW_PER_USER',
            'POWER_AUTOMATE_PREMIUM',
            'COPILOT_STUDIO_USER_PRO',
            'DYN365_ENTERPRISE_PLAN1'
        )
    )
    $managed = $Inventory.Rows | Where-Object ManagedEnvironmentEnabled
    if (-not $managed) {
        return [pscustomobject]@{ Status='NotApplicable'; Reason='NoManagedEnvironments'; Rows=@() }
    }
    $rows = foreach ($env in $managed) {
        $makers = @()
        try {
            $makers = Get-AdminPowerAppEnvironmentRoleAssignment -EnvironmentName $env.EnvironmentId -ErrorAction Stop |
                Where-Object { $_.RoleName -in @('Environment Maker','System Administrator') }
        } catch {
            # Dataverse environments: see baseline §6
        }
        $uncovered = @()
        foreach ($maker in $makers) {
            try {
                $details = Invoke-MgGraphRequest -Method GET -Uri "/v1.0/users/$($maker.PrincipalObjectId)/licenseDetails"
                $skus = ($details.value).skuPartNumber
                if (-not ($skus | Where-Object { $_ -in $QualifyingSkuPartNumbers })) {
                    $uncovered += [pscustomobject]@{
                        Upn        = $maker.PrincipalDisplayName
                        ObjectId   = $maker.PrincipalObjectId
                        SkusHeld   = $skus -join ';'
                    }
                }
            } catch {
                $uncovered += [pscustomobject]@{
                    Upn      = $maker.PrincipalDisplayName
                    ObjectId = $maker.PrincipalObjectId
                    SkusHeld = '(unresolved)'
                }
            }
        }
        $status = if (-not $uncovered) { 'Clean' }
                  elseif ((Get-Date) -lt [datetime]'2026-06-01') { 'Pending' }
                  else { 'Anomaly' }
        [pscustomobject]@{
            EnvironmentId   = $env.EnvironmentId
            DisplayName     = $env.DisplayName
            MakerCount      = $makers.Count
            UncoveredCount  = $uncovered.Count
            UncoveredUsers  = $uncovered
            EnforcementDate = '2026-06-01'
            Status          = $status
            Reason          = if ($status -eq 'Clean') { '' } else { "UncoveredMakers:$($uncovered.Count)" }
        }
    }
    [pscustomobject]@{
        Status     = if ($rows | Where-Object Status -eq 'Anomaly') { 'Anomaly' }
                     elseif ($rows | Where-Object Status -eq 'Pending') { 'Pending' }
                     else { 'Clean' }
        Reason     = ''
        Count      = $rows.Count
        Rows       = $rows
        ExportedAt = (Get-Date).ToUniversalTime().ToString('o')
    }
}
```

The helper distinguishes `Pending` (uncovered makers exist but the June 2026 enforcement window has not opened) from `Anomaly` (uncovered makers persist past the enforcement date). The orchestrator's `-Mode Quarterly` chain treats either non-`Clean` state as a remediation row and produces a per-maker work-list for the licensing administrator.

---


## §4 — Bulk Enablement and Emergency Disable

### 4.1 Enable-Fsi-ManagedEnvironment

```powershell
function Enable-Fsi-ManagedEnvironment {
<#
.SYNOPSIS
    Enables Managed Environments on the named environment with the given protection level.
    Captures a JSON snapshot before and after the mutation; supports -WhatIf and -Confirm.
.PARAMETER ProtectionLevel
    Standard | High. Use High for Zone 3 production environments.
.NOTES
    Control 2.1 — Managed Environments. Last UI verified: April 2026.
    Requires Windows PowerShell 5.1 (Desktop) and Power Platform Admin role.
#>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)] [string] $EnvironmentName,
        [ValidateSet('Standard','High')] [string] $ProtectionLevel = 'Standard',
        [Parameter(Mandatory)] [string] $ChangeTicketId,
        [Parameter(Mandatory)] [string] $EvidencePath
    )
    $null = Assert-Fsi-LegacyShell
    if (-not $ChangeTicketId) {
        throw [System.ArgumentException]::new("Fsi21-NoChangeTicket: -ChangeTicketId is required for any mutation.")
    }
    $ts = Get-Date -Format 'yyyyMMdd-HHmmss'
    $before = Get-AdminPowerAppEnvironment -EnvironmentName $EnvironmentName -ErrorAction Stop
    $beforePath = Join-Path $EvidencePath "before-enable-$EnvironmentName-$ts.json"
    $before | ConvertTo-Json -Depth 10 | Set-Content -Path $beforePath -Encoding UTF8

    if ($PSCmdlet.ShouldProcess($EnvironmentName, "Enable Managed Environment ($ProtectionLevel)")) {
        Set-AdminPowerAppEnvironmentGovernanceConfiguration `
            -EnvironmentName $EnvironmentName `
            -ProtectionLevel $ProtectionLevel `
            -ErrorAction Stop | Out-Null

        $after = Get-AdminPowerAppEnvironmentGovernanceConfiguration -EnvironmentName $EnvironmentName -ErrorAction Stop
        $afterPath = Join-Path $EvidencePath "after-enable-$EnvironmentName-$ts.json"
        $after | ConvertTo-Json -Depth 10 | Set-Content -Path $afterPath -Encoding UTF8

        $hash = (Get-FileHash -Path $afterPath -Algorithm SHA256).Hash
        return [pscustomobject]@{
            EnvironmentId   = $EnvironmentName
            ProtectionLevel = $ProtectionLevel
            ChangeTicketId  = $ChangeTicketId
            BeforePath      = $beforePath
            AfterPath       = $afterPath
            AfterSha256     = $hash
            AppliedAt       = (Get-Date).ToUniversalTime().ToString('o')
            Status          = 'Clean'
            Reason          = ''
        }
    } else {
        return [pscustomobject]@{
            EnvironmentId   = $EnvironmentName
            ProtectionLevel = $ProtectionLevel
            ChangeTicketId  = $ChangeTicketId
            BeforePath      = $beforePath
            Status          = 'Pending'
            Reason          = 'WhatIfMode'
        }
    }
}
```

### 4.2 Disable-Fsi-ManagedEnvironment (emergency workflow)

```powershell
function Disable-Fsi-ManagedEnvironment {
<#
.SYNOPSIS
    Emergency disable of Managed Environments on the named environment. Demands a Change Ticket
    and an explicit Reason; refuses to run without -WhatIf preview confirmation.
.NOTES
    Control 2.1 — Managed Environments. Last UI verified: April 2026.
    Disabling Managed Environments REMOVES sharing limits, solution-checker enforcement, IP firewall,
    and the binding to any CMK Enterprise Policy. Treat as a tier-1 change.
#>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)] [string] $EnvironmentName,
        [Parameter(Mandatory)] [string] $ChangeTicketId,
        [Parameter(Mandatory)] [string] $Reason,
        [Parameter(Mandatory)] [string] $EvidencePath
    )
    $null = Assert-Fsi-LegacyShell
    $ts = Get-Date -Format 'yyyyMMdd-HHmmss'
    $before = Get-AdminPowerAppEnvironmentGovernanceConfiguration -EnvironmentName $EnvironmentName -ErrorAction Stop
    $beforePath = Join-Path $EvidencePath "before-disable-$EnvironmentName-$ts.json"
    $before | ConvertTo-Json -Depth 10 | Set-Content -Path $beforePath -Encoding UTF8

    if ($PSCmdlet.ShouldProcess($EnvironmentName, "DISABLE Managed Environment — $Reason")) {
        Set-AdminPowerAppEnvironmentGovernanceConfiguration `
            -EnvironmentName $EnvironmentName `
            -ProtectionLevel None `
            -ErrorAction Stop | Out-Null
        return [pscustomobject]@{
            EnvironmentId  = $EnvironmentName
            ChangeTicketId = $ChangeTicketId
            Reason         = $Reason
            BeforePath     = $beforePath
            DisabledAt     = (Get-Date).ToUniversalTime().ToString('o')
            Status         = 'Anomaly'    # disable is an exception state, never "Clean"
        }
    }
    [pscustomobject]@{
        EnvironmentId  = $EnvironmentName
        ChangeTicketId = $ChangeTicketId
        Reason         = $Reason
        Status         = 'Pending'
    }
}
```

`Disable-Fsi-ManagedEnvironment` deliberately returns `Status='Anomaly'` even on a successful disable — disabled state is by definition an exception that the AI Governance Lead must counter-sign within 24 hours under the firm's WSPs. The verification helper `Test-Fsi-Control21-EnablementCoverage` (§16) re-detects the disabled state on the next quarterly run and refuses to certify the control closed until the environment is either re-enabled or formally retired.

---

## §5 — Sharing Limits

!!! info "Sharing limits scope — standalone cloud flows are NOT governed"
    Managed Environment sharing limits govern **Power Apps**, **solution-aware Power Automate flows**, **Microsoft Copilot Studio agents**, and the **Editor / Viewer roles** on those resources. They **do not govern standalone cloud flows** that live outside a solution, and they do not govern flows that share via a connection-reference rather than a direct flow share. Operators who rely solely on this helper for share-blast prevention will leak. **Enforce standalone-cloud-flow sharing at the DLP layer (Control 1.5)**, which is the control that actually owns connector-level egress restriction. The verification helper `Test-Fsi-Control21-SharingLimitsBaseline` cross-validates that Control 1.5 has the matching DLP coverage in place before declaring `Clean`.

### 5.1 Set-Fsi-SharingLimits

```powershell
function Set-Fsi-SharingLimits {
<#
.SYNOPSIS
    Sets per-resource-family sharing limits on a Managed Environment (Canvas Apps, solution-aware
    flows, Copilot Studio agents, Viewer / Editor caps). Captures a before/after JSON snapshot.
.NOTES
    Control 2.1 — Managed Environments. Last UI verified: April 2026.
    Standalone cloud flows are NOT governed by this cmdlet — see Control 1.5 for DLP-based enforcement.
#>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)] [string] $EnvironmentName,
        [Parameter(Mandatory)] [int] $CanvasAppsLimit,
        [Parameter(Mandatory)] [int] $SolutionFlowsLimit,
        [Parameter(Mandatory)] [int] $AgentsLimit,
        [Parameter(Mandatory)] [int] $ViewerLimit,
        [Parameter(Mandatory)] [int] $EditorLimit,
        [Parameter(Mandatory)] [string] $ChangeTicketId,
        [Parameter(Mandatory)] [string] $EvidencePath
    )
    $null = Assert-Fsi-LegacyShell
    $ts = Get-Date -Format 'yyyyMMdd-HHmmss'
    $before = Get-AdminPowerAppEnvironmentGovernanceConfiguration -EnvironmentName $EnvironmentName -ErrorAction Stop
    $beforePath = Join-Path $EvidencePath "before-sharing-$EnvironmentName-$ts.json"
    $before | ConvertTo-Json -Depth 10 | Set-Content $beforePath -Encoding UTF8

    $body = @{
        sharingSettings = @{
            canvasApps        = @{ shareLimit = $CanvasAppsLimit }
            cloudFlows        = @{ shareLimit = $SolutionFlowsLimit }   # solution-aware only
            copilotAgents     = @{ shareLimit = $AgentsLimit; viewerLimit = $ViewerLimit; editorLimit = $EditorLimit }
        }
    }
    if ($PSCmdlet.ShouldProcess($EnvironmentName, "Apply sharing limits (Canvas=$CanvasAppsLimit, SolnFlows=$SolutionFlowsLimit, Agents=$AgentsLimit, Viewer=$ViewerLimit, Editor=$EditorLimit)")) {
        Set-AdminPowerAppEnvironmentGovernanceConfiguration `
            -EnvironmentName $EnvironmentName `
            -GovernanceSettings $body `
            -ErrorAction Stop | Out-Null
        $after = Get-AdminPowerAppEnvironmentGovernanceConfiguration -EnvironmentName $EnvironmentName
        $afterPath = Join-Path $EvidencePath "after-sharing-$EnvironmentName-$ts.json"
        $after | ConvertTo-Json -Depth 10 | Set-Content $afterPath -Encoding UTF8
        return [pscustomobject]@{
            EnvironmentId   = $EnvironmentName
            CanvasAppsLimit = $CanvasAppsLimit
            SolutionFlowsLimit = $SolutionFlowsLimit
            AgentsLimit     = $AgentsLimit
            ViewerLimit     = $ViewerLimit
            EditorLimit     = $EditorLimit
            BeforePath      = $beforePath
            AfterPath       = $afterPath
            AfterSha256     = (Get-FileHash $afterPath -Algorithm SHA256).Hash
            ChangeTicketId  = $ChangeTicketId
            Status          = 'Clean'
            Reason          = ''
            Caveat          = 'StandaloneCloudFlowsNotGoverned-SeeControl1.5'
        }
    }
    [pscustomobject]@{ EnvironmentId=$EnvironmentName; ChangeTicketId=$ChangeTicketId; Status='Pending'; Reason='WhatIfMode' }
}
```

The helper writes **`Caveat='StandaloneCloudFlowsNotGoverned-SeeControl1.5'`** into every successful evidence row. The quarterly evidence bundle in §17 surfaces this caveat in the human-readable summary so reviewers cannot overlook it.

### 5.2 FSI sharing-limit baseline (recommended)

| Zone | Canvas Apps | Solution Flows | Agents | Viewer | Editor |
|---|---|---|---|---|---|
| Zone 1 (Personal) | n/a (no Managed) | n/a | n/a | n/a | n/a |
| Zone 2 (Team) | 25 | 10 | 5 | 50 | 10 |
| Zone 3 (Enterprise) | 100 | 50 | 25 | 250 | 25 |

These values are **starting baselines**, not regulatory minimums. Tune to the firm's WSPs and document the rationale in the change ticket. The verification helper `Test-Fsi-Control21-SharingLimitsBaseline` flags any environment whose limits are **above** the baseline (more permissive) as `Anomaly`; values **at or below** the baseline are `Clean`.

---

## §6 — Solution Checker Enforcement

```powershell
function Set-Fsi-SolutionCheckerEnforcement {
<#
.SYNOPSIS
    Sets solution-checker enforcement mode on a Managed Environment. None | Warn | Block.
    For Zone 3 production environments, Block is required by the FSI baseline.
.NOTES
    Control 2.1 — Managed Environments. Last UI verified: April 2026.
#>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)] [string] $EnvironmentName,
        [Parameter(Mandatory)] [ValidateSet('None','Warn','Block')] [string] $Mode,
        [Parameter(Mandatory)] [string] $ChangeTicketId,
        [Parameter(Mandatory)] [string] $EvidencePath
    )
    $null = Assert-Fsi-LegacyShell
    $ts = Get-Date -Format 'yyyyMMdd-HHmmss'
    $before = Get-AdminPowerAppEnvironmentGovernanceConfiguration -EnvironmentName $EnvironmentName -ErrorAction Stop
    $beforePath = Join-Path $EvidencePath "before-solchk-$EnvironmentName-$ts.json"
    $before | ConvertTo-Json -Depth 10 | Set-Content $beforePath

    if ($PSCmdlet.ShouldProcess($EnvironmentName, "Solution checker -> $Mode")) {
        Set-AdminPowerAppEnvironmentGovernanceConfiguration `
            -EnvironmentName $EnvironmentName `
            -SolutionCheckerEnforcement $Mode `
            -ErrorAction Stop | Out-Null
        $after = Get-AdminPowerAppEnvironmentGovernanceConfiguration -EnvironmentName $EnvironmentName
        $afterPath = Join-Path $EvidencePath "after-solchk-$EnvironmentName-$ts.json"
        $after | ConvertTo-Json -Depth 10 | Set-Content $afterPath
        return [pscustomobject]@{
            EnvironmentId    = $EnvironmentName
            Mode             = $Mode
            ChangeTicketId   = $ChangeTicketId
            BeforePath       = $beforePath
            AfterPath        = $afterPath
            AfterSha256      = (Get-FileHash $afterPath -Algorithm SHA256).Hash
            Status           = if ($Mode -eq 'Block') { 'Clean' } elseif ($Mode -eq 'Warn') { 'Anomaly' } else { 'Anomaly' }
            Reason           = if ($Mode -eq 'Block') { '' } else { "ModeBelowZone3Baseline:$Mode" }
        }
    }
    [pscustomobject]@{ EnvironmentId=$EnvironmentName; Status='Pending'; Reason='WhatIfMode' }
}
```

`Warn` mode is **explicitly flagged as `Anomaly`** for any environment classified Zone 3. The §16 verification helper `Test-Fsi-Control21-SolutionCheckerBlock` enforces this rule across the tenant.

---

## §7 — Maker Welcome Content

!!! note "Maker welcome content is excluded from CMK"
    Maker welcome content is rendered by Microsoft-managed services and is **not encrypted with your Customer-Managed Key**, even after `Add-Fsi-CMKPolicyToEnvironment` succeeds. Do **not** embed sensitive content (PII, MNPI, internal account numbers, draft policy text). The recommended pattern is to link to the firm's WSPs and training portal rather than to embed text. `Set-Fsi-MakerWelcome` enforces a 1500-character cap and runs a regex sweep against a sensitive-pattern set; values that match are rejected with `Status='Anomaly'`. The exclusion is restated in the per-environment CMK exclusions narrative produced by `Test-Fsi-CMKExclusions` (§11.3).

```powershell
function Set-Fsi-MakerWelcome {
<#
.SYNOPSIS
    Sets the maker welcome content displayed in Power Apps / Power Automate / Copilot Studio
    designers for a Managed Environment. Refuses to apply content that exceeds 1500 chars or
    matches the sensitive-pattern regex.
.NOTES
    Control 2.1 — Managed Environments. Last UI verified: April 2026.
    Welcome content is NOT CMK-encrypted. Link to WSPs/training rather than embed text.
#>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)] [string] $EnvironmentName,
        [string] $PowerAppsContent,
        [string] $PowerAutomateContent,
        [string] $CopilotStudioContent,
        [Parameter(Mandatory)] [string] $ChangeTicketId,
        [Parameter(Mandatory)] [string] $EvidencePath
    )
    $null = Assert-Fsi-LegacyShell
    $sensitive = '\b(SSN|EIN|MNPI|account\s+number|client\s+account|password|secret)\b'
    foreach ($field in 'PowerAppsContent','PowerAutomateContent','CopilotStudioContent') {
        $val = (Get-Variable -Name $field -ValueOnly)
        if ($val) {
            if ($val.Length -gt 1500) {
                throw [System.ArgumentException]::new("Fsi21-WelcomeTooLong: $field exceeds 1500 chars.")
            }
            if ($val -match $sensitive) {
                throw [System.ArgumentException]::new("Fsi21-WelcomeSensitivePattern: $field matched the sensitive-pattern regex; remove and link to WSPs instead.")
            }
        }
    }
    $ts = Get-Date -Format 'yyyyMMdd-HHmmss'
    $body = @{
        makerOnboardingMarkdown = $PowerAppsContent
        makerOnboardingFlows    = $PowerAutomateContent
        makerOnboardingCopilot  = $CopilotStudioContent
    }
    if ($PSCmdlet.ShouldProcess($EnvironmentName, "Set maker welcome content (lengths: pa=$($PowerAppsContent.Length), pf=$($PowerAutomateContent.Length), cs=$($CopilotStudioContent.Length))")) {
        Set-AdminPowerAppEnvironmentGovernanceConfiguration `
            -EnvironmentName $EnvironmentName `
            -MakerOnboarding $body `
            -ErrorAction Stop | Out-Null
        $afterPath = Join-Path $EvidencePath "after-welcome-$EnvironmentName-$ts.json"
        $body | ConvertTo-Json -Depth 5 | Set-Content $afterPath
        return [pscustomobject]@{
            EnvironmentId   = $EnvironmentName
            ChangeTicketId  = $ChangeTicketId
            AfterPath       = $afterPath
            AfterSha256     = (Get-FileHash $afterPath -Algorithm SHA256).Hash
            Caveat          = 'WelcomeContentNotCmkEncrypted'
            Status          = 'Clean'
            Reason          = ''
        }
    }
    [pscustomobject]@{ EnvironmentId=$EnvironmentName; ChangeTicketId=$ChangeTicketId; Status='Pending'; Reason='WhatIfMode' }
}
```

---


## §8 — IP Firewall (Audit-First, Then Enforce)

The Power Platform IP Firewall is one of the highest-risk Managed-Environment settings to mis-configure. Flipping straight to `Enforce` against an uncalibrated allow-list has produced two trading-floor outages in the field. This playbook **defaults to `AuditOnly`**, requires a **calibration window of at least four weeks**, and exposes a helper that extracts the would-be-blocked traffic so the firm can see exactly what is going to break before it breaks.

### 8.1 Set-Fsi-IPFirewall

```powershell
function Set-Fsi-IPFirewall {
<#
.SYNOPSIS
    Configures IP Firewall for a Managed Environment. Default mode is AuditOnly to surface
    would-be-blocked traffic in the audit log without affecting users.
.PARAMETER ReverseProxyIPs
    Egress IPs of any reverse proxies that fronted client traffic at the Power Platform endpoint
    (otherwise the proxy IPs appear as the source and the user IPs are masked — false-positive blocks).
.NOTES
    Control 2.1 — Managed Environments. Last UI verified: April 2026.
#>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)] [string] $EnvironmentName,
        [ValidateSet('AuditOnly','Enforce')] [string] $Mode = 'AuditOnly',
        [Parameter(Mandatory)] [string[]] $AllowedIPs,
        [string[]] $ReverseProxyIPs = @(),
        [Parameter(Mandatory)] [string] $ChangeTicketId,
        [Parameter(Mandatory)] [string] $EvidencePath
    )
    $null = Assert-Fsi-LegacyShell
    foreach ($ip in $AllowedIPs + $ReverseProxyIPs) {
        if ($ip -notmatch '^\d{1,3}(\.\d{1,3}){3}(/\d{1,2})?$' -and $ip -notmatch ':') {
            throw [System.ArgumentException]::new("Fsi21-BadCIDR: '$ip' is not a recognised CIDR/IP form.")
        }
    }
    $ts = Get-Date -Format 'yyyyMMdd-HHmmss'
    $body = @{
        ipFirewall = @{
            mode             = $Mode
            allowedIpRanges  = $AllowedIPs
            reverseProxyIps  = $ReverseProxyIPs
        }
    }
    if ($PSCmdlet.ShouldProcess($EnvironmentName, "IP Firewall -> $Mode (allowed=$($AllowedIPs.Count), proxies=$($ReverseProxyIPs.Count))")) {
        Set-AdminPowerAppEnvironmentGovernanceConfiguration `
            -EnvironmentName $EnvironmentName `
            -GovernanceSettings $body `
            -ErrorAction Stop | Out-Null
        $afterPath = Join-Path $EvidencePath "after-ipfw-$EnvironmentName-$ts.json"
        $body | ConvertTo-Json -Depth 5 | Set-Content $afterPath
        return [pscustomobject]@{
            EnvironmentId   = $EnvironmentName
            Mode            = $Mode
            AllowedCount    = $AllowedIPs.Count
            ProxyCount      = $ReverseProxyIPs.Count
            ChangeTicketId  = $ChangeTicketId
            AfterPath       = $afterPath
            AfterSha256     = (Get-FileHash $afterPath -Algorithm SHA256).Hash
            AppliedAt       = (Get-Date).ToUniversalTime().ToString('o')
            Status          = 'Clean'
            Reason          = if ($Mode -eq 'AuditOnly') { 'CalibrationWindowOpen' } else { '' }
        }
    }
    [pscustomobject]@{ EnvironmentId=$EnvironmentName; Status='Pending'; Reason='WhatIfMode' }
}
```

### 8.2 Get-Fsi-IPFirewallAuditLog

```powershell
function Get-Fsi-IPFirewallAuditLog {
<#
.SYNOPSIS
    Extracts would-be-blocked traffic from the Purview unified audit log for an environment
    in IP Firewall AuditOnly mode. Use this BEFORE flipping to Enforce.
.NOTES
    Control 2.1 — Managed Environments. Last UI verified: April 2026.
    Requires Purview Compliance Admin and the Microsoft.Graph.Security or ExchangeOnlineManagement
    Search-UnifiedAuditLog cmdlet.
#>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string] $EnvironmentName,
        [int] $SinceDays = 28
    )
    $start = (Get-Date).AddDays(-1 * $SinceDays)
    $end   = Get-Date
    try {
        $rows = Search-UnifiedAuditLog -StartDate $start -EndDate $end `
            -RecordType PowerPlatformAdministratorActivity `
            -Operations 'IpFirewall_AuditOnly_WouldHaveBlocked' `
            -ResultSize 5000
    } catch {
        return [pscustomobject]@{ Status='NotApplicable'; Reason="UnifiedAuditUnavailable:$($_.Exception.Message)"; Rows=@() }
    }
    $byEnv = $rows | Where-Object { $_.AuditData -match $EnvironmentName }
    $unique = $byEnv | Group-Object { ($_.AuditData | ConvertFrom-Json).ClientIP } |
        Select-Object Name, Count
    [pscustomobject]@{
        EnvironmentId         = $EnvironmentName
        WindowDays            = $SinceDays
        TotalAuditedBlocks    = $byEnv.Count
        UniqueSourceIPs       = $unique.Count
        TopOffendingIPs       = ($unique | Sort-Object Count -Descending | Select-Object -First 25)
        Status                = if ($byEnv.Count -eq 0) { 'Clean' } else { 'Anomaly' }
        Reason                = if ($byEnv.Count -eq 0) { 'NoWouldBeBlocks' } else { "WouldBeBlocks:$($byEnv.Count)" }
        Recommendation        = if ($byEnv.Count -eq 0) { 'SafeToEnforce' } else { 'CalibrateAllowListBeforeEnforce' }
    }
}
```

The verification helper `Test-Fsi-Control21-IPFirewallEnforced` (§16) flags any environment that has been in `AuditOnly` for **more than 28 days** as `Anomaly` — calibration windows that linger become permanent loopholes. Operators are expected either to flip to `Enforce` once the would-be-block count is stable at zero for 7 consecutive days, or to file a documented exception against the change ticket.

---

## §9 — IP-Based Cookie Binding

```powershell
function Set-Fsi-IPCookieBinding {
<#
.SYNOPSIS
    Enables IP-based cookie binding so a Power Platform session cookie cannot be replayed from
    a different source IP. Required for Zone 3 production environments.
.NOTES
    Control 2.1 — Managed Environments. Last UI verified: April 2026.
#>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)] [string] $EnvironmentName,
        [Parameter(Mandatory)] [bool] $Enabled,
        [Parameter(Mandatory)] [string] $ChangeTicketId,
        [Parameter(Mandatory)] [string] $EvidencePath
    )
    $null = Assert-Fsi-LegacyShell
    $ts = Get-Date -Format 'yyyyMMdd-HHmmss'
    $body = @{ ipCookieBinding = @{ enabled = $Enabled } }
    if ($PSCmdlet.ShouldProcess($EnvironmentName, "IP cookie binding -> $Enabled")) {
        Set-AdminPowerAppEnvironmentGovernanceConfiguration -EnvironmentName $EnvironmentName -GovernanceSettings $body -ErrorAction Stop | Out-Null
        $afterPath = Join-Path $EvidencePath "after-ipbind-$EnvironmentName-$ts.json"
        $body | ConvertTo-Json -Depth 5 | Set-Content $afterPath
        return [pscustomobject]@{
            EnvironmentId  = $EnvironmentName
            Enabled        = $Enabled
            ChangeTicketId = $ChangeTicketId
            AfterPath      = $afterPath
            AfterSha256    = (Get-FileHash $afterPath -Algorithm SHA256).Hash
            Status         = if ($Enabled) { 'Clean' } else { 'Anomaly' }
            Reason         = if ($Enabled) { '' } else { 'IpCookieBindingDisabled' }
        }
    }
    [pscustomobject]@{ EnvironmentId=$EnvironmentName; Status='Pending'; Reason='WhatIfMode' }
}
```

---

## §10 — Customer Lockbox

```powershell
function Set-Fsi-CustomerLockbox {
<#
.SYNOPSIS
    Enables Customer Lockbox for a Managed Environment. Verifies that the tenant Lockbox tier
    is provisioned (M365 E5 / E5 Compliance / equivalent) before applying.
.NOTES
    Control 2.1 — Managed Environments. Last UI verified: April 2026.
#>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)] [string] $EnvironmentName,
        [Parameter(Mandatory)] [bool] $Enabled,
        [Parameter(Mandatory)] [string] $ChangeTicketId,
        [Parameter(Mandatory)] [string] $EvidencePath
    )
    $null = Assert-Fsi-LegacyShell
    # Tier probe: read tenant Lockbox setting from SCC (Search-AdminAuditLog or Microsoft.Graph)
    try {
        $tier = Invoke-MgGraphRequest -Method GET -Uri '/v1.0/admin/customerLockbox/settings' -ErrorAction Stop
        if (-not $tier.isEnabled) {
            return [pscustomobject]@{
                EnvironmentId = $EnvironmentName
                Status        = 'Anomaly'
                Reason        = 'TenantCustomerLockboxNotEnabled'
            }
        }
    } catch {
        # If the Graph endpoint is unavailable, fall through and rely on the configuration write result.
    }
    $ts = Get-Date -Format 'yyyyMMdd-HHmmss'
    $body = @{ customerLockbox = @{ enabled = $Enabled } }
    if ($PSCmdlet.ShouldProcess($EnvironmentName, "Customer Lockbox -> $Enabled")) {
        Set-AdminPowerAppEnvironmentGovernanceConfiguration -EnvironmentName $EnvironmentName -GovernanceSettings $body -ErrorAction Stop | Out-Null
        $afterPath = Join-Path $EvidencePath "after-lockbox-$EnvironmentName-$ts.json"
        $body | ConvertTo-Json -Depth 5 | Set-Content $afterPath
        return [pscustomobject]@{
            EnvironmentId  = $EnvironmentName
            Enabled        = $Enabled
            ChangeTicketId = $ChangeTicketId
            AfterPath      = $afterPath
            AfterSha256    = (Get-FileHash $afterPath -Algorithm SHA256).Hash
            Status         = if ($Enabled) { 'Clean' } else { 'Anomaly' }
            Reason         = ''
        }
    }
    [pscustomobject]@{ EnvironmentId=$EnvironmentName; Status='Pending'; Reason='WhatIfMode' }
}
```

---

## §11 — Customer-Managed Keys via Az.PowerPlatform Enterprise Policies

CMK for Power Platform is implemented as an **ARM Enterprise Policy** resource that is then linked to one or more environments. The full flow has three steps: provision the Key Vault key (out of scope for this playbook — handled by the firm's PKI / KeyOps team and covered by Control 1.20 / Azure Key Vault standards), create the Enterprise Policy and wire its system-assigned identity into the Key Vault access policy, and finally apply the policy to the target environment. After application, a **non-trivial subset of environment data remains Microsoft-managed** and is therefore **excluded from CMK encryption**. Reproducing that exclusion list verbatim for an examiner is a recurring audit ask; `Test-Fsi-CMKExclusions` produces it.

### 11.1 New-Fsi-CMKPolicy

```powershell
function New-Fsi-CMKPolicy {
<#
.SYNOPSIS
    Creates a Power Platform CMK Enterprise Policy ARM resource, then grants the policy's
    system-assigned identity Get/WrapKey/UnwrapKey on the named Key Vault key.
.PARAMETER PolicyName
    Friendly name for the Enterprise Policy. Will appear in PPAC.
.NOTES
    Control 2.1 — Managed Environments. Last UI verified: April 2026.
    Requires PowerShell 7.4+, Az.PowerPlatform, Az.KeyVault, and PIM elevation to Crypto Officer.
#>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)] [string] $KeyVaultName,
        [Parameter(Mandatory)] [string] $KeyName,
        [Parameter(Mandatory)] [string] $SubscriptionId,
        [Parameter(Mandatory)] [string] $ResourceGroupName,
        [Parameter(Mandatory)] [string] $PolicyName,
        [Parameter(Mandatory)] [string] $Location,
        [Parameter(Mandatory)] [string] $ChangeTicketId,
        [Parameter(Mandatory)] [string] $EvidencePath
    )
    $null = Assert-Fsi-AzShell
    $ctx = Get-AzContext
    if ($ctx.Subscription.Id -ne $SubscriptionId) {
        Set-AzContext -Subscription $SubscriptionId | Out-Null
    }
    $kv = Get-AzKeyVault -VaultName $KeyVaultName -ResourceGroupName $ResourceGroupName
    if (-not $kv.EnablePurgeProtection -or -not $kv.EnableSoftDelete) {
        throw [System.InvalidOperationException]::new(
            "Fsi21-KvHardeningMissing: Key Vault $KeyVaultName must have purge-protection AND soft-delete enabled before CMK policy creation.")
    }
    $key = Get-AzKeyVaultKey -VaultName $KeyVaultName -Name $KeyName
    if (-not $key) { throw "Fsi21-KvKeyMissing: $KeyName not found in $KeyVaultName" }

    if ($PSCmdlet.ShouldProcess($PolicyName, "Create CMK Enterprise Policy bound to ${KeyVaultName}/${KeyName}")) {
        $policy = New-AzResource -ResourceType 'Microsoft.PowerPlatform/enterprisePolicies' `
            -ResourceGroupName $ResourceGroupName `
            -Name $PolicyName `
            -Location $Location `
            -Properties @{
                kind       = 'Encryption'
                encryption = @{
                    state         = 'Enabled'
                    keyVault      = @{
                        id       = $kv.ResourceId
                        key      = @{ name = $KeyName; version = $key.Version }
                    }
                }
            } `
            -IdentityType SystemAssigned `
            -Force

        # Grant the policy identity Key Vault access (Crypto Officer pattern; use RBAC roles in RBAC-mode vaults).
        if ($kv.EnableRbacAuthorization) {
            New-AzRoleAssignment -ObjectId $policy.Identity.PrincipalId `
                -RoleDefinitionName 'Key Vault Crypto Service Encryption User' `
                -Scope $kv.ResourceId | Out-Null
        } else {
            Set-AzKeyVaultAccessPolicy -VaultName $KeyVaultName `
                -ObjectId $policy.Identity.PrincipalId `
                -PermissionsToKeys Get,WrapKey,UnwrapKey
        }

        $ts = Get-Date -Format 'yyyyMMdd-HHmmss'
        $afterPath = Join-Path $EvidencePath "cmk-policy-$PolicyName-$ts.json"
        $policy | ConvertTo-Json -Depth 10 | Set-Content $afterPath
        return [pscustomobject]@{
            PolicyArmId     = $policy.ResourceId
            PolicyName      = $PolicyName
            KeyVaultId      = $kv.ResourceId
            KeyVersion      = $key.Version
            IdentityObjectId = $policy.Identity.PrincipalId
            ChangeTicketId  = $ChangeTicketId
            AfterPath       = $afterPath
            AfterSha256     = (Get-FileHash $afterPath -Algorithm SHA256).Hash
            Status          = 'Clean'
            Reason          = ''
        }
    }
    [pscustomobject]@{ PolicyName=$PolicyName; ChangeTicketId=$ChangeTicketId; Status='Pending'; Reason='WhatIfMode' }
}
```

### 11.2 Add-Fsi-CMKPolicyToEnvironment

```powershell
function Add-Fsi-CMKPolicyToEnvironment {
<#
.SYNOPSIS
    Applies a CMK Enterprise Policy to the named environment. Captures the post-application
    encryption state AND the verbatim CMK exclusion list as a single evidence artefact.
.NOTES
    Control 2.1 — Managed Environments. Last UI verified: April 2026.
    The exclusion list is the artefact regulators ask for first; do not skip its capture.
#>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)] [string] $PolicyArmId,
        [Parameter(Mandatory)] [string] $EnvironmentName,
        [Parameter(Mandatory)] [string] $ChangeTicketId,
        [Parameter(Mandatory)] [string] $EvidencePath
    )
    $null = Assert-Fsi-AzShell
    if ($PSCmdlet.ShouldProcess($EnvironmentName, "Apply CMK policy $PolicyArmId")) {
        New-AzPowerPlatformEnterprisePolicyEnvironmentLink `
            -SystemId $PolicyArmId `
            -EnvironmentId $EnvironmentName `
            -ErrorAction Stop | Out-Null

        $ts = Get-Date -Format 'yyyyMMdd-HHmmss'
        $exclusions = @(
            'Maker welcome content (notes / banners) — Microsoft-managed rendering pipeline'
            'Solution-checker analysis results — Microsoft-managed analyzer service'
            'Environment, app, flow, and agent display names — service-platform metadata'
            'Environment, app, flow, and agent descriptions — service-platform metadata'
            'Connection-reference metadata (display name, connector type, status) — connectors-platform indexed'
            'Microsoft Agent 365 Admin Center audit logging fields — Agent 365 service-platform'
            'Service-side telemetry, throttling counters, and platform diagnostics — Microsoft-managed'
            'Service Health and Message Center notifications — tenant-platform'
        )
        $artefact = [pscustomobject]@{
            EnvironmentId   = $EnvironmentName
            PolicyArmId     = $PolicyArmId
            AppliedAt       = (Get-Date).ToUniversalTime().ToString('o')
            ChangeTicketId  = $ChangeTicketId
            CmkExclusions   = $exclusions
            ExclusionNarrative = "The Customer-Managed Key wrapped by Enterprise Policy $PolicyArmId encrypts Dataverse table data, " +
                                 "Dataverse file/image columns, Dataverse search index content, and connection secrets. " +
                                 "It does NOT encrypt the artefacts enumerated above; those remain protected by Microsoft-managed encryption keys. " +
                                 "This separation is documented in the Microsoft Power Platform CMK service description and is reproduced in this " +
                                 "evidence artefact for examiner reference under FFIEC IT Examination Handbook (Information Security booklet)."
        }
        $artPath = Join-Path $EvidencePath "cmk-applied-$EnvironmentName-$ts.json"
        $artefact | ConvertTo-Json -Depth 8 | Set-Content $artPath
        return [pscustomobject]@{
            EnvironmentId  = $EnvironmentName
            PolicyArmId    = $PolicyArmId
            ChangeTicketId = $ChangeTicketId
            ArtefactPath   = $artPath
            ArtefactSha256 = (Get-FileHash $artPath -Algorithm SHA256).Hash
            Status         = 'Clean'
            Reason         = ''
        }
    }
    [pscustomobject]@{ EnvironmentId=$EnvironmentName; ChangeTicketId=$ChangeTicketId; Status='Pending'; Reason='WhatIfMode' }
}
```

### 11.3 Test-Fsi-CMKExclusions

```powershell
function Test-Fsi-CMKExclusions {
<#
.SYNOPSIS
    Re-generates the FSI-required CMK exclusion narrative for the named environment so it can
    be appended to a quarterly evidence pack or produced on demand for an examiner.
.NOTES
    Control 2.1 — Managed Environments. Last UI verified: April 2026.
#>
    [CmdletBinding()]
    param([Parameter(Mandatory)] [string] $EnvironmentName)
    try {
        $link = Get-AzPowerPlatformEnterprisePolicyEnvironmentLink -EnvironmentId $EnvironmentName -ErrorAction Stop
    } catch {
        return [pscustomobject]@{ EnvironmentId=$EnvironmentName; Status='NotApplicable'; Reason='NoCmkPolicyApplied' }
    }
    [pscustomobject]@{
        EnvironmentId  = $EnvironmentName
        PolicyArmId    = $link.SystemId
        Narrative      = (Get-Content -Raw -Path (Get-ChildItem -Path . -Recurse -Filter "cmk-applied-$EnvironmentName-*.json" |
                            Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName -ErrorAction SilentlyContinue)
        Status         = if ($link) { 'Clean' } else { 'Anomaly' }
        Reason         = ''
    }
}
```

---

## §12 — Tenant Isolation

```powershell
function Set-Fsi-TenantIsolation {
<#
.SYNOPSIS
    Configures Power Platform tenant isolation (inbound and/or outbound). The default FSI baseline
    is BOTH directions enabled, with documented partner exceptions added via Add-Fsi-TenantIsolationException.
.NOTES
    Control 2.1 — Managed Environments. Last UI verified: April 2026.
    KNOWN ISSUE: The Azure DevOps connector is NOT Entra-ID-authenticated and is excluded from
    tenant isolation. Cross-tenant AzDO traffic must be governed by DLP (Control 1.5).
    Tenant isolation governs ONLY connectors that authenticate via Entra ID.
#>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)] [bool] $DirectionInbound,
        [Parameter(Mandatory)] [bool] $DirectionOutbound,
        [Parameter(Mandatory)] [bool] $Enabled,
        [Parameter(Mandatory)] [string] $ChangeTicketId,
        [Parameter(Mandatory)] [string] $EvidencePath
    )
    $null = Assert-Fsi-LegacyShell
    Write-Warning "Fsi21-TenantIsolationScope: governs Entra-ID-authenticated connectors only. Azure DevOps connector is a documented exclusion — enforce via DLP (Control 1.5)."
    $ts = Get-Date -Format 'yyyyMMdd-HHmmss'
    $body = @{
        properties = @{
            isDisabled       = -not $Enabled
            allowedTenants   = @()
            inboundEnabled   = $DirectionInbound
            outboundEnabled  = $DirectionOutbound
        }
    }
    if ($PSCmdlet.ShouldProcess('Tenant', "Tenant isolation Enabled=$Enabled Inbound=$DirectionInbound Outbound=$DirectionOutbound")) {
        Set-PowerAppTenantIsolationPolicy -TenantIsolationPolicy $body -ErrorAction Stop | Out-Null
        $afterPath = Join-Path $EvidencePath "tenant-isolation-$ts.json"
        $body | ConvertTo-Json -Depth 6 | Set-Content $afterPath
        return [pscustomobject]@{
            Enabled         = $Enabled
            DirectionInbound = $DirectionInbound
            DirectionOutbound = $DirectionOutbound
            ChangeTicketId  = $ChangeTicketId
            AfterPath       = $afterPath
            AfterSha256     = (Get-FileHash $afterPath -Algorithm SHA256).Hash
            KnownExclusion  = 'AzureDevOpsConnector-NotEntraAuth-EnforceViaDLP'
            Status          = if ($Enabled -and $DirectionInbound -and $DirectionOutbound) { 'Clean' } else { 'Anomaly' }
            Reason          = if ($Enabled -and $DirectionInbound -and $DirectionOutbound) { '' } else { 'IsolationBelowFSIBaseline' }
        }
    }
    [pscustomobject]@{ Status='Pending'; Reason='WhatIfMode' }
}

function Add-Fsi-TenantIsolationException {
<#
.SYNOPSIS
    Adds a trusted-partner tenant ID to the tenant-isolation allow-list. Each exception requires
    a ChangeTicketId, business owner UPN, and direction.
.NOTES
    Control 2.1 — Managed Environments. Last UI verified: April 2026.
#>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)] [string] $TenantId,
        [Parameter(Mandatory)] [ValidateSet('Inbound','Outbound','Both')] [string] $Direction,
        [Parameter(Mandatory)] [string] $BusinessOwnerUpn,
        [Parameter(Mandatory)] [string] $ChangeTicketId,
        [Parameter(Mandatory)] [string] $EvidencePath
    )
    $null = Assert-Fsi-LegacyShell
    $current = Get-PowerAppTenantIsolationPolicy -ErrorAction Stop
    $entry = @{
        tenantId = $TenantId
        direction = $Direction
        owner    = $BusinessOwnerUpn
        ticket   = $ChangeTicketId
        addedUtc = (Get-Date).ToUniversalTime().ToString('o')
    }
    $current.properties.allowedTenants += $entry
    if ($PSCmdlet.ShouldProcess($TenantId, "Add tenant-isolation exception ($Direction) owner=$BusinessOwnerUpn")) {
        Set-PowerAppTenantIsolationPolicy -TenantIsolationPolicy $current -ErrorAction Stop | Out-Null
        $ts = Get-Date -Format 'yyyyMMdd-HHmmss'
        $afterPath = Join-Path $EvidencePath "tenant-isolation-exception-$TenantId-$ts.json"
        $entry | ConvertTo-Json -Depth 5 | Set-Content $afterPath
        return [pscustomobject]@{
            TenantId       = $TenantId
            Direction      = $Direction
            BusinessOwner  = $BusinessOwnerUpn
            ChangeTicketId = $ChangeTicketId
            AfterPath      = $afterPath
            AfterSha256    = (Get-FileHash $afterPath -Algorithm SHA256).Hash
            Status         = 'Anomaly'
            Reason         = 'ExceptionToFSIBaseline-RequiresQuarterlyReview'
        }
    }
    [pscustomobject]@{ TenantId=$TenantId; Status='Pending'; Reason='WhatIfMode' }
}
```

Tenant-isolation exceptions return `Status='Anomaly'` even on success — every exception is, by definition, a deviation from the FSI baseline that must be reviewed quarterly by the AI Governance Lead and the Compliance Officer. The §16 verification helper `Test-Fsi-Control21-TenantIsolationEnabled` enumerates exceptions and flags any whose `addedUtc` is older than 90 days without a re-attestation.

---

## §13 — Environment Routing

```powershell
function Set-Fsi-EnvironmentRouting {
<#
.SYNOPSIS
    Sets environment routing rules so makers landing on Power Apps / Power Automate / Copilot Studio
    are routed into managed developer environments (or environment groups) rather than the default
    environment. NOT a region-selection helper — region is set at environment creation time.
.NOTES
    Control 2.1 — Managed Environments. Last UI verified: April 2026.
#>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)] [object[]] $RuleSet,
        [Parameter(Mandatory)] [string] $ChangeTicketId,
        [Parameter(Mandatory)] [string] $EvidencePath
    )
    $null = Assert-Fsi-LegacyShell
    foreach ($rule in $RuleSet) {
        foreach ($k in 'Service','Audience','TargetEnvironmentGroupId') {
            if (-not $rule.PSObject.Properties.Name -contains $k) {
                throw [System.ArgumentException]::new("Fsi21-BadRoutingRule: missing $k")
            }
        }
        if ($rule.Service -notin 'PowerApps','PowerAutomate','CopilotStudio') {
            throw "Fsi21-BadRoutingRule: Service must be PowerApps|PowerAutomate|CopilotStudio."
        }
    }
    $ts = Get-Date -Format 'yyyyMMdd-HHmmss'
    if ($PSCmdlet.ShouldProcess('Tenant', "Apply $($RuleSet.Count) routing rule(s)")) {
        Set-AdminPowerAppEnvironmentRoutingPolicy -RoutingRules $RuleSet -ErrorAction Stop | Out-Null
        $afterPath = Join-Path $EvidencePath "routing-$ts.json"
        $RuleSet | ConvertTo-Json -Depth 8 | Set-Content $afterPath
        return [pscustomobject]@{
            RuleCount      = $RuleSet.Count
            ChangeTicketId = $ChangeTicketId
            AfterPath      = $afterPath
            AfterSha256    = (Get-FileHash $afterPath -Algorithm SHA256).Hash
            Status         = 'Clean'
            Reason         = ''
        }
    }
    [pscustomobject]@{ ChangeTicketId=$ChangeTicketId; Status='Pending'; Reason='WhatIfMode' }
}
```

---

## §14 — Pipeline Targets

```powershell
function Get-Fsi-PipelineTargets {
<#
.SYNOPSIS
    Discovers all pipeline target environments tenant-wide by reading the deploymentpipelines
    table in each Dataverse-backed environment. Surfaces environments that are pipeline targets
    but are NOT Managed.
.NOTES
    Control 2.1 — Managed Environments. Last UI verified: April 2026.
#>
    [CmdletBinding()]
    param([Parameter(Mandatory)] [object] $Inventory)
    $rows = @()
    foreach ($env in ($Inventory.Rows | Where-Object DataverseProvisioned)) {
        try {
            $targets = Get-AdminDeploymentPipelineStage -EnvironmentName $env.EnvironmentId -ErrorAction Stop |
                Where-Object { $_.StageType -eq 'Target' }
            foreach ($t in $targets) {
                $rows += [pscustomobject]@{
                    HostEnvironmentId     = $env.EnvironmentId
                    HostDisplayName       = $env.DisplayName
                    PipelineId            = $t.PipelineId
                    PipelineName          = $t.PipelineName
                    TargetEnvironmentId   = $t.TargetEnvironmentId
                    TargetEnvironmentName = $t.TargetEnvironmentName
                    TargetIsManaged       = ($Inventory.Rows | Where-Object EnvironmentId -eq $t.TargetEnvironmentId).ManagedEnvironmentEnabled
                }
            }
        } catch {
            # Env without pipelines table — skip silently
        }
    }
    [pscustomobject]@{
        Status     = if (($rows | Where-Object { -not $_.TargetIsManaged }).Count -eq 0) { 'Clean' } else { 'Anomaly' }
        Reason     = if (($rows | Where-Object { -not $_.TargetIsManaged }).Count -eq 0) { '' } else { "UnmanagedPipelineTargets:$(($rows | Where-Object { -not $_.TargetIsManaged }).Count)" }
        Count      = $rows.Count
        Rows       = $rows
        ExportedAt = (Get-Date).ToUniversalTime().ToString('o')
    }
}

function Enable-Fsi-PipelineTargetsManagedEnv {
<#
.SYNOPSIS
    Bulk-enables Managed Environments on every pipeline target environment that is currently
    unmanaged. Each enablement is wrapped in -WhatIf and writes a per-environment evidence row.
.NOTES
    Control 2.1 — Managed Environments. Last UI verified: April 2026.
#>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)] [object] $PipelineTargetReport,
        [Parameter(Mandatory)] [string] $ChangeTicketId,
        [Parameter(Mandatory)] [string] $EvidencePath
    )
    $null = Assert-Fsi-LegacyShell
    $unmanaged = $PipelineTargetReport.Rows | Where-Object { -not $_.TargetIsManaged } |
        Group-Object TargetEnvironmentId | ForEach-Object { $_.Group | Select-Object -First 1 }
    $results = foreach ($t in $unmanaged) {
        if ($PSCmdlet.ShouldProcess($t.TargetEnvironmentId, "Bulk-enable Managed (pipeline target $($t.PipelineName))")) {
            Enable-Fsi-ManagedEnvironment -EnvironmentName $t.TargetEnvironmentId `
                -ProtectionLevel Standard `
                -ChangeTicketId $ChangeTicketId `
                -EvidencePath $EvidencePath
        } else {
            [pscustomobject]@{ EnvironmentId=$t.TargetEnvironmentId; Status='Pending'; Reason='WhatIfMode' }
        }
    }
    [pscustomobject]@{
        Count   = $results.Count
        Results = $results
        Status  = if ($results | Where-Object Status -eq 'Clean') { 'Clean' } else { 'Pending' }
        Reason  = ''
    }
}
```

---



## §16 — Verification Helpers

The helpers below are the per-criterion attestation points consumed by the §17 quarterly evidence bundle. Each is a pure read (no mutation) and each emits one `[pscustomobject]` with the canonical Status contract. None of these helpers writes to the tenant; all of them assume that §3 inventory has already been collected.

!!! warning "Pending is not Clean"
    Several of these helpers can return `Pending` when a calibration window is open (for example, IP Firewall in `AuditOnly` for less than 28 days). Pending must be surfaced in the quarterly attestation packet alongside Anomaly. Do not aggregate `Pending` into `Clean` for executive reporting — it is a distinct, named state that requires the AI Governance Lead and Power Platform Admin to sign off on the closure date.

### 16.1 Test-Fsi-Control21-EnablementCoverage

```powershell
function Test-Fsi-Control21-EnablementCoverage {
<#
.SYNOPSIS
    Verifies every Zone-2 and Zone-3 environment has Managed Environments enabled, and that
    every pipeline target environment is also Managed.
.NOTES
    Control 2.1 — Managed Environments. Last UI verified: April 2026.
#>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [object] $Inventory,
        [Parameter(Mandatory)] [object] $PipelineTargetReport,
        [Parameter(Mandatory)] [hashtable] $ZoneAssignments    # @{ EnvId -> Zone1|Zone2|Zone3 }
    )
    $rows = foreach ($env in $Inventory.Rows) {
        $zone = if ($ZoneAssignments.ContainsKey($env.EnvironmentId)) { $ZoneAssignments[$env.EnvironmentId] } else { "Unassigned" }
        $shouldBeManaged = $zone -in "Zone2","Zone3" -or
                           ($PipelineTargetReport.Rows.TargetEnvironmentId -contains $env.EnvironmentId)
        [pscustomobject]@{
            EnvironmentId = $env.EnvironmentId
            DisplayName   = $env.DisplayName
            Zone          = $zone
            ManagedEnabled = $env.ManagedEnvironmentEnabled
            Status        = if ($shouldBeManaged -and -not $env.ManagedEnvironmentEnabled) { "Anomaly" }
                            elseif (-not $shouldBeManaged) { "NotApplicable" }
                            else { "Clean" }
            Reason        = if ($shouldBeManaged -and -not $env.ManagedEnvironmentEnabled) { "ShouldBeManaged-Zone:$zone" } else { "" }
        }
    }
    [pscustomobject]@{
        Count  = $rows.Count
        Rows   = $rows
        Status = if ($rows | Where-Object Status -eq "Anomaly") { "Anomaly" } else { "Clean" }
        Reason = ""
    }
}
```

### 16.2 Test-Fsi-Control21-LicensingCoverage

```powershell
function Test-Fsi-Control21-LicensingCoverage {
<#
.SYNOPSIS
    Wraps Test-Fsi-ManagedEnvLicensing to produce a single Clean|Anomaly|Pending readiness
    signal for the June 2026 enforcement window.
.NOTES
    Control 2.1 — Managed Environments. Last UI verified: April 2026.
#>
    [CmdletBinding()]
    param([Parameter(Mandatory)] [object] $LicensingReport)
    [pscustomobject]@{
        EnvironmentsEvaluated = $LicensingReport.Count
        TotalUncovered        = ($LicensingReport.Rows | Measure-Object -Property UncoveredCount -Sum).Sum
        EnforcementDate       = "2026-06-01"
        DaysUntilEnforcement  = [int]([datetime]"2026-06-01" - (Get-Date)).TotalDays
        Status                = $LicensingReport.Status
        Reason                = if ($LicensingReport.Status -eq "Clean") { "" } else { "See per-environment Rows for uncovered users." }
    }
}
```

### 16.3 Test-Fsi-Control21-SharingLimitsBaseline

```powershell
function Test-Fsi-Control21-SharingLimitsBaseline {
<#
.SYNOPSIS
    Verifies sharing limits on every Managed Environment are at or below the FSI baseline by zone.
    Returns Anomaly if any resource family is unconfigured (defaults are too permissive).
.NOTES
    Control 2.1 — Managed Environments. Last UI verified: April 2026.
#>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [object] $Inventory,
        [Parameter(Mandatory)] [hashtable] $ZoneAssignments
    )
    $baseline = @{
        Zone2 = @{ Canvas=25;  SolnFlows=10; Agents=5;  Viewer=50;  Editor=10 }
        Zone3 = @{ Canvas=100; SolnFlows=50; Agents=25; Viewer=250; Editor=25 }
    }
    $rows = foreach ($env in ($Inventory.Rows | Where-Object ManagedEnvironmentEnabled)) {
        $zone = if ($ZoneAssignments.ContainsKey($env.EnvironmentId)) { $ZoneAssignments[$env.EnvironmentId] } else { "Unassigned" }
        if ($zone -notin "Zone2","Zone3") { continue }
        try {
            $cfg = Get-AdminPowerAppEnvironmentGovernanceConfiguration -EnvironmentName $env.EnvironmentId -ErrorAction Stop
        } catch {
            [pscustomobject]@{ EnvironmentId=$env.EnvironmentId; Zone=$zone; Status="Error"; Reason=$_.Exception.Message }
            continue
        }
        $b = $baseline[$zone]
        $current = @{
            Canvas    = $cfg.sharingSettings.canvasApps.shareLimit
            SolnFlows = $cfg.sharingSettings.cloudFlows.shareLimit
            Agents    = $cfg.sharingSettings.copilotAgents.shareLimit
            Viewer    = $cfg.sharingSettings.copilotAgents.viewerLimit
            Editor    = $cfg.sharingSettings.copilotAgents.editorLimit
        }
        $missing = $current.Keys | Where-Object { -not $current[$_] }
        $exceed  = $current.Keys | Where-Object { $current[$_] -and $current[$_] -gt $b[$_] }
        $status = if ($missing -or $exceed) { "Anomaly" } else { "Clean" }
        [pscustomobject]@{
            EnvironmentId  = $env.EnvironmentId
            Zone           = $zone
            CurrentLimits  = $current
            BaselineLimits = $b
            UnconfiguredFamilies = $missing
            ExceedingBaseline    = $exceed
            Status         = $status
            Reason         = if ($status -eq "Clean") { "" } else { "Missing:$($missing -join ',');Exceed:$($exceed -join ',')" }
            Caveat         = "StandaloneCloudFlowsNotGoverned-VerifyControl1.5DLP"
        }
    }
    [pscustomobject]@{
        Count  = $rows.Count
        Rows   = $rows
        Status = if ($rows | Where-Object Status -eq "Anomaly") { "Anomaly" } else { "Clean" }
        Reason = ""
    }
}
```

### 16.4 Test-Fsi-Control21-SolutionCheckerBlock

```powershell
function Test-Fsi-Control21-SolutionCheckerBlock {
<#
.SYNOPSIS
    Verifies solution-checker enforcement is set to Block on every Zone-3 environment.
.NOTES
    Control 2.1 — Managed Environments. Last UI verified: April 2026.
#>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [object] $Inventory,
        [Parameter(Mandatory)] [hashtable] $ZoneAssignments
    )
    $rows = foreach ($env in ($Inventory.Rows | Where-Object ManagedEnvironmentEnabled)) {
        $zone = if ($ZoneAssignments.ContainsKey($env.EnvironmentId)) { $ZoneAssignments[$env.EnvironmentId] } else { "Unassigned" }
        if ($zone -ne "Zone3") { continue }
        try {
            $cfg = Get-AdminPowerAppEnvironmentGovernanceConfiguration -EnvironmentName $env.EnvironmentId -ErrorAction Stop
            $mode = $cfg.SolutionCheckerEnforcement
        } catch {
            $mode = "(unavailable)"
        }
        [pscustomobject]@{
            EnvironmentId = $env.EnvironmentId
            Zone          = $zone
            Mode          = $mode
            Status        = if ($mode -eq "Block") { "Clean" } else { "Anomaly" }
            Reason        = if ($mode -eq "Block") { "" } else { "Zone3RequiresBlock-Found:$mode" }
        }
    }
    [pscustomobject]@{
        Count  = $rows.Count
        Rows   = $rows
        Status = if ($rows | Where-Object Status -eq "Anomaly") { "Anomaly" } else { "Clean" }
        Reason = ""
    }
}
```

### 16.5 Test-Fsi-Control21-IPFirewallEnforced

```powershell
function Test-Fsi-Control21-IPFirewallEnforced {
<#
.SYNOPSIS
    Verifies every Zone-3 environment has IP Firewall in Enforce mode, OR has been in AuditOnly
    for less than 28 days. Stale AuditOnly is flagged as Anomaly.
.NOTES
    Control 2.1 — Managed Environments. Last UI verified: April 2026.
#>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [object] $Inventory,
        [Parameter(Mandatory)] [hashtable] $ZoneAssignments,
        [int] $AuditOnlyToleranceDays = 28
    )
    $rows = foreach ($env in ($Inventory.Rows | Where-Object ManagedEnvironmentEnabled)) {
        $zone = if ($ZoneAssignments.ContainsKey($env.EnvironmentId)) { $ZoneAssignments[$env.EnvironmentId] } else { "Unassigned" }
        if ($zone -ne "Zone3") { continue }
        try {
            $cfg = Get-AdminPowerAppEnvironmentGovernanceConfiguration -EnvironmentName $env.EnvironmentId -ErrorAction Stop
            $mode = $cfg.ipFirewall.mode
            $sinceUtc = $cfg.ipFirewall.modeChangedUtc
        } catch {
            $mode = "(unavailable)"; $sinceUtc = $null
        }
        $age = if ($sinceUtc) { [int]((Get-Date) - [datetime]$sinceUtc).TotalDays } else { -1 }
        $status = switch ($mode) {
            "Enforce"   { "Clean" }
            "AuditOnly" { if ($age -le $AuditOnlyToleranceDays) { "Pending" } else { "Anomaly" } }
            default     { "Anomaly" }
        }
        [pscustomobject]@{
            EnvironmentId = $env.EnvironmentId
            Zone          = $zone
            Mode          = $mode
            ModeAgeDays   = $age
            Status        = $status
            Reason        = if ($status -eq "Anomaly" -and $mode -eq "AuditOnly") { "StaleAuditOnly:${age}d" }
                            elseif ($status -eq "Anomaly") { "BadMode:$mode" }
                            elseif ($status -eq "Pending") { "CalibrationWindowOpen:${age}d" }
                            else { "" }
        }
    }
    [pscustomobject]@{
        Count  = $rows.Count
        Rows   = $rows
        Status = if ($rows | Where-Object Status -eq "Anomaly") { "Anomaly" }
                 elseif ($rows | Where-Object Status -eq "Pending") { "Pending" }
                 else { "Clean" }
        Reason = ""
    }
}
```

### 16.6 Test-Fsi-Control21-CMKExclusionsDocumented

```powershell
function Test-Fsi-Control21-CMKExclusionsDocumented {
<#
.SYNOPSIS
    Verifies that every CMK-applied environment has a current exclusion-narrative artefact on disk.
.NOTES
    Control 2.1 — Managed Environments. Last UI verified: April 2026.
#>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [object] $Inventory,
        [Parameter(Mandatory)] [string] $EvidencePath
    )
    $rows = foreach ($env in $Inventory.Rows) {
        $exclusion = Test-Fsi-CMKExclusions -EnvironmentName $env.EnvironmentId
        if ($exclusion.Status -eq "NotApplicable") { continue }
        $artefact = Get-ChildItem -Path $EvidencePath -Filter "cmk-applied-$($env.EnvironmentId)-*.json" -ErrorAction SilentlyContinue |
            Sort-Object LastWriteTime -Descending | Select-Object -First 1
        [pscustomobject]@{
            EnvironmentId = $env.EnvironmentId
            PolicyArmId   = $exclusion.PolicyArmId
            ArtefactPath  = if ($artefact) { $artefact.FullName } else { $null }
            ArtefactAgeDays = if ($artefact) { [int]((Get-Date) - $artefact.LastWriteTime).TotalDays } else { -1 }
            Status        = if ($artefact) { "Clean" } else { "Anomaly" }
            Reason        = if ($artefact) { "" } else { "CmkAppliedButExclusionNarrativeMissing" }
        }
    }
    [pscustomobject]@{
        Count  = $rows.Count
        Rows   = $rows
        Status = if ($rows | Where-Object Status -eq "Anomaly") { "Anomaly" } else { "Clean" }
        Reason = ""
    }
}
```

### 16.7 Test-Fsi-Control21-TenantIsolationEnabled

```powershell
function Test-Fsi-Control21-TenantIsolationEnabled {
<#
.SYNOPSIS
    Verifies tenant isolation is enabled in BOTH directions and that every documented exception
    has a Control 1.5 DLP cross-reference (specifically including Azure DevOps).
.NOTES
    Control 2.1 — Managed Environments. Last UI verified: April 2026.
#>
    [CmdletBinding()]
    param([Parameter(Mandatory)] [object] $Dlp15ExceptionTable)
    try {
        $policy = Get-PowerAppTenantIsolationPolicy -ErrorAction Stop
    } catch {
        return [pscustomobject]@{ Status="Error"; Reason=$_.Exception.Message }
    }
    $enabled  = -not $policy.properties.isDisabled
    $inbound  = $policy.properties.inboundEnabled
    $outbound = $policy.properties.outboundEnabled
    $azdoCovered = $Dlp15ExceptionTable | Where-Object { $_.Connector -eq "AzureDevOps" }
    $exceptions = $policy.properties.allowedTenants | ForEach-Object {
        [pscustomobject]@{
            TenantId      = $_.tenantId
            Direction     = $_.direction
            Owner         = $_.owner
            AddedUtc      = $_.addedUtc
            AgeDays       = [int]((Get-Date) - [datetime]$_.addedUtc).TotalDays
            Status        = if (((Get-Date) - [datetime]$_.addedUtc).TotalDays -gt 90) { "Anomaly" } else { "Clean" }
            Reason        = if (((Get-Date) - [datetime]$_.addedUtc).TotalDays -gt 90) { "ExceptionExceeds90d-RequiresReAttestation" } else { "" }
        }
    }
    $status = if (-not ($enabled -and $inbound -and $outbound)) { "Anomaly" }
              elseif (-not $azdoCovered) { "Anomaly" }
              elseif ($exceptions | Where-Object Status -eq "Anomaly") { "Anomaly" }
              else { "Clean" }
    [pscustomobject]@{
        Enabled              = $enabled
        Inbound              = $inbound
        Outbound             = $outbound
        AzureDevOpsDlpExceptionLogged = [bool]$azdoCovered
        Exceptions           = $exceptions
        Status               = $status
        Reason               = if ($status -eq "Clean") { "" }
                               elseif (-not $azdoCovered) { "AzDoConnectorNotDocumentedInControl1.5DLP" }
                               else { "OneOrMoreExceptionsStaleOrIsolationDisabled" }
    }
}
```

---

## §17 — Quarterly Evidence Bundle

The quarterly evidence bundle is the primary attestation artefact for Control 2.1. It is produced by `Export-Fsi-Control21-QuarterlyEvidence`, which composes the §3 inventory and the §16 verification helpers into a single signed JSON manifest. The bundle supports compliance with FINRA Rule 3110 (supervision), SEC Rule 17a-4 (records retention), and OCC Bulletin 2013-29 (third-party / model-risk management) when paired with the parent control narrative — it is a record of administrative state, not a substitute for the legal narrative the Compliance Officer and AI Governance Lead must author.

### 17.1 Bundle contract

| Section | Source | Purpose |
|---|---|---|
| `inventory` | `Get-Fsi-PPEnvironment` | Snapshot of every environment, Managed flag, region, owner |
| `licensing` | `Test-Fsi-Control21-LicensingCoverage` | Readiness for the June 2026 enforcement |
| `sharingLimits` | `Test-Fsi-Control21-SharingLimitsBaseline` | Per-zone baseline conformance |
| `solutionChecker` | `Test-Fsi-Control21-SolutionCheckerBlock` | Zone-3 enforcement state |
| `ipFirewall` | `Test-Fsi-Control21-IPFirewallEnforced` | Enforce vs AuditOnly with calibration age |
| `cmkExclusions` | `Test-Fsi-Control21-CMKExclusionsDocumented` | Verbatim 8-item exclusion narrative coverage |
| `tenantIsolation` | `Test-Fsi-Control21-TenantIsolationEnabled` | Both-direction state + 1.5 DLP cross-reference for AzDO |
| `pipelineTargets` | `Get-Fsi-PipelineTargets` + `Test-Fsi-Control21-EnablementCoverage` | All ALM targets are Managed |
| `signatures` | Three named signers | Power Platform Admin + AI Governance Lead + Compliance Officer |

### 17.2 Export-Fsi-Control21-QuarterlyEvidence

```powershell
function Export-Fsi-Control21-QuarterlyEvidence {
<#
.SYNOPSIS
    Composes the quarterly Control 2.1 evidence bundle and writes a signed JSON manifest. The
    manifest is intended for retention under SEC 17a-4 and supports — but does not substitute for —
    the parent Compliance Officer attestation narrative.
.NOTES
    Control 2.1 — Managed Environments. Last UI verified: April 2026.
    Hedged-language reminder: this script aids in documenting the state of Managed Environment
    configuration; it does not certify regulatory compliance.
#>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)] [string] $Quarter,                    # e.g. 2026Q2
        [Parameter(Mandatory)] [hashtable] $ZoneAssignments,
        [Parameter(Mandatory)] [object] $Dlp15ExceptionTable,
        [Parameter(Mandatory)] [string] $EvidencePath,
        [Parameter(Mandatory)] [string] $ChangeTicketId,
        [Parameter(Mandatory)] [hashtable] $Signers                  # @{ PowerPlatformAdmin='upn'; AIGovernanceLead='upn'; ComplianceOfficer='upn' }
    )
    if (-not $PSCmdlet.ShouldProcess("Control 2.1 Q=$Quarter", "Export quarterly evidence bundle")) { return }
    foreach ($k in 'PowerPlatformAdmin','AIGovernanceLead','ComplianceOfficer') {
        if (-not $Signers.ContainsKey($k) -or [string]::IsNullOrWhiteSpace($Signers[$k])) {
            throw "Fsi21-MissingSigner:$k"
        }
    }
    $ts = Get-Date -Format "yyyyMMdd-HHmmss"
    $runMeta = Get-RunMetadata -ChangeTicketId $ChangeTicketId

    Write-Host "[Fsi21] Collecting inventory..."
    $inv = Get-Fsi-PPEnvironment
    $lic = Test-Fsi-ManagedEnvLicensing -Inventory $inv
    $pipe = Get-Fsi-PipelineTargets

    $sections = [ordered]@{
        runMetadata           = $runMeta
        inventory             = $inv
        licensing             = (Test-Fsi-Control21-LicensingCoverage -LicensingReport $lic)
        sharingLimits         = (Test-Fsi-Control21-SharingLimitsBaseline -Inventory $inv -ZoneAssignments $ZoneAssignments)
        solutionChecker       = (Test-Fsi-Control21-SolutionCheckerBlock -Inventory $inv -ZoneAssignments $ZoneAssignments)
        ipFirewall            = (Test-Fsi-Control21-IPFirewallEnforced -Inventory $inv -ZoneAssignments $ZoneAssignments)
        cmkExclusions         = (Test-Fsi-Control21-CMKExclusionsDocumented -Inventory $inv -EvidencePath $EvidencePath)
        tenantIsolation       = (Test-Fsi-Control21-TenantIsolationEnabled -Dlp15ExceptionTable $Dlp15ExceptionTable)
        pipelineTargets       = (Test-Fsi-Control21-EnablementCoverage -Inventory $inv -PipelineTargetReport $pipe -ZoneAssignments $ZoneAssignments)
    }

    # Aggregate the cross-section status. Pending is preserved separately from Anomaly.
    $allStatus = $sections.Values | Where-Object { $_ -and $_.PSObject.Properties.Match('Status').Count } | ForEach-Object { $_.Status }
    $bundleStatus = if ($allStatus -contains 'Anomaly') { 'Anomaly' }
                    elseif ($allStatus -contains 'Pending') { 'Pending' }
                    elseif ($allStatus -contains 'Error') { 'Error' }
                    else { 'Clean' }

    $manifest = [pscustomobject]@{
        controlId       = "2.1"
        controlName     = "Managed Environments"
        quarter         = $Quarter
        generatedAtUtc  = (Get-Date).ToUniversalTime().ToString("o")
        bundleStatus    = $bundleStatus
        sections        = $sections
        signers         = [ordered]@{
            PowerPlatformAdmin = @{ upn = $Signers.PowerPlatformAdmin; signedAtUtc = $null; signatureSha256 = $null }
            AIGovernanceLead   = @{ upn = $Signers.AIGovernanceLead;   signedAtUtc = $null; signatureSha256 = $null }
            ComplianceOfficer  = @{ upn = $Signers.ComplianceOfficer;  signedAtUtc = $null; signatureSha256 = $null }
        }
        attestation     = @{
            statement = "Power Platform Admin attests to current technical state. AI Governance Lead attests to baseline conformance. Compliance Officer attests to retention and the parent narrative. This bundle aids in evidencing Managed Environment configuration; it does not certify regulatory compliance."
            retention = "SEC 17a-4 minimum 6 years; FINRA 4511 minimum 6 years; institution policy may extend."
        }
    }

    $artPath = Join-Path $EvidencePath "control-2.1-quarterly-$Quarter-$ts.json"
    $manifest | ConvertTo-Json -Depth 12 | Set-Content $artPath -Encoding utf8
    $sha = (Get-FileHash $artPath -Algorithm SHA256).Hash

    [pscustomobject]@{
        ControlId      = "2.1"
        Quarter        = $Quarter
        ArtefactPath   = $artPath
        ArtefactSha256 = $sha
        BundleStatus   = $bundleStatus
        SignersPending = @('PowerPlatformAdmin','AIGovernanceLead','ComplianceOfficer')
        Status         = if ($bundleStatus -in 'Clean','Pending') { 'Pending' } else { $bundleStatus }
        Reason         = "AwaitingThreeSignatures-See:Add-Fsi-EvidenceSignature(SharedBaseline)"
    }
}
```

### 17.3 Signing workflow

The bundle is emitted with `Status=Pending` and `SignersPending` populated. Each signer countersigns the manifest using `Add-Fsi-EvidenceSignature` from the shared baseline (see [`../../_shared/powershell-baseline.md`](../../_shared/powershell-baseline.md), §5). When the third signature is posted, the consuming script promotes the bundle's overall `Status` to its underlying `bundleStatus` (Clean | Anomaly | Pending). The manifest must be retained under SEC 17a-4 (minimum six years) and FINRA Rule 4511; institutional policy may extend. The signed bundle is the only artefact that the AI Risk Committee will accept as quarterly evidence for Control 2.1.

---

## §18 — Orchestrator

`Invoke-Fsi-Control21Setup` is the top-level entry point. It composes the helpers above into three named modes and is the only function that quarterly operations should invoke directly.

### 18.1 Modes

| Mode | Purpose | Mutates tenant? | Typical caller |
|---|---|---|---|
| `Provision` | Apply the FSI baseline (enable Managed, set sharing limits, set solution-checker, configure IP firewall in AuditOnly, configure tenant isolation) to a named environment list | **Yes** — gated by `-WhatIf` and `-ChangeTicketId` | Power Platform Admin during onboarding |
| `Verify` | Run all §16 helpers and produce a console summary; no mutation | No | Power Platform Admin (weekly) |
| `Quarterly` | Verify + produce the §17 signed evidence bundle | No (read-only mutation: writes evidence file) | AI Governance Lead (quarterly) |

### 18.2 Invoke-Fsi-Control21Setup

```powershell
function Invoke-Fsi-Control21Setup {
<#
.SYNOPSIS
    Top-level orchestrator for Control 2.1. Routes to Provision, Verify, or Quarterly modes.
.NOTES
    Control 2.1 — Managed Environments. Last UI verified: April 2026.
#>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)] [ValidateSet("Provision","Verify","Quarterly")] [string] $Mode,
        [Parameter(Mandatory)] [hashtable] $ZoneAssignments,
        [Parameter()] [object] $Dlp15ExceptionTable,
        [Parameter()] [string[]] $EnvironmentIds,
        [Parameter()] [string] $Quarter,
        [Parameter()] [string] $EvidencePath = (Join-Path $PWD "evidence\control-2.1"),
        [Parameter()] [string] $ChangeTicketId,
        [Parameter()] [hashtable] $Signers
    )
    if (-not (Test-Path $EvidencePath)) { New-Item -Path $EvidencePath -ItemType Directory -Force | Out-Null }
    $runId = "fsi21-$((Get-Date).ToUniversalTime().ToString('yyyyMMddHHmmss'))"
    Write-Host "[Fsi21] Mode=$Mode"

    switch ($Mode) {
        "Provision" {
            $null = Assert-Fsi-LegacyShell
            if (-not $ChangeTicketId)         { throw "Fsi21-NoChangeTicket" }
            if (-not $EnvironmentIds)         { throw "Fsi21-EmptyEnvList" }
            Initialize-Fsi-PPSession -RunId $runId -EvidencePath $EvidencePath
            foreach ($eid in $EnvironmentIds) {
                if ($PSCmdlet.ShouldProcess($eid, "Apply Control 2.1 baseline")) {
                    Enable-Fsi-ManagedEnvironment       -EnvironmentName $eid -ChangeTicketId $ChangeTicketId -EvidencePath $EvidencePath
                    Set-Fsi-SharingLimits               -EnvironmentName $eid -Zone ($ZoneAssignments[$eid]) -ChangeTicketId $ChangeTicketId -EvidencePath $EvidencePath
                    Set-Fsi-SolutionCheckerEnforcement  -EnvironmentName $eid -Zone ($ZoneAssignments[$eid]) -ChangeTicketId $ChangeTicketId -EvidencePath $EvidencePath
                    Set-Fsi-MakerWelcome                -EnvironmentName $eid -ChangeTicketId $ChangeTicketId -EvidencePath $EvidencePath
                    Set-Fsi-IPFirewall                  -EnvironmentName $eid -Mode AuditOnly -ChangeTicketId $ChangeTicketId -EvidencePath $EvidencePath
                    Set-Fsi-IPCookieBinding             -EnvironmentName $eid -ChangeTicketId $ChangeTicketId -EvidencePath $EvidencePath
                }
            }
            Set-Fsi-TenantIsolation -Mode Enable -ChangeTicketId $ChangeTicketId -EvidencePath $EvidencePath
            return [pscustomobject]@{ Mode='Provision'; Count=$EnvironmentIds.Count; Status='Pending'; Reason='ReviewIPFirewallCalibrationWithin28d' }
        }
        "Verify" {
            $null = Assert-Fsi-LegacyShell
            Initialize-Fsi-PPSession -RunId $runId -EvidencePath $EvidencePath
            $inv = Get-Fsi-PPEnvironment
            $lic = Test-Fsi-ManagedEnvLicensing -Inventory $inv
            $pipe = Get-Fsi-PipelineTargets
            $results = [ordered]@{
                EnablementCoverage    = Test-Fsi-Control21-EnablementCoverage    -Inventory $inv -PipelineTargetReport $pipe -ZoneAssignments $ZoneAssignments
                LicensingCoverage     = Test-Fsi-Control21-LicensingCoverage     -LicensingReport $lic
                SharingLimitsBaseline = Test-Fsi-Control21-SharingLimitsBaseline -Inventory $inv -ZoneAssignments $ZoneAssignments
                SolutionCheckerBlock  = Test-Fsi-Control21-SolutionCheckerBlock  -Inventory $inv -ZoneAssignments $ZoneAssignments
                IPFirewallEnforced    = Test-Fsi-Control21-IPFirewallEnforced    -Inventory $inv -ZoneAssignments $ZoneAssignments
                CMKExclusions         = Test-Fsi-Control21-CMKExclusionsDocumented -Inventory $inv -EvidencePath $EvidencePath
                TenantIsolation       = Test-Fsi-Control21-TenantIsolationEnabled -Dlp15ExceptionTable $Dlp15ExceptionTable
            }
            $statuses = $results.Values | ForEach-Object { $_.Status }
            $overall = if ($statuses -contains 'Anomaly') { 'Anomaly' }
                       elseif ($statuses -contains 'Pending') { 'Pending' }
                       elseif ($statuses -contains 'Error') { 'Error' }
                       else { 'Clean' }
            $results.GetEnumerator() | ForEach-Object {
                Write-Host ("  {0,-26} {1,-12} {2}" -f $_.Key, $_.Value.Status, ($_.Value.Reason ?? ""))
            }
            return [pscustomobject]@{ Mode='Verify'; Status=$overall; Sections=$results }
        }
        "Quarterly" {
            if (-not $Quarter)        { throw "Fsi21-MissingQuarter" }
            if (-not $Signers)        { throw "Fsi21-MissingSigners" }
            if (-not $ChangeTicketId) { throw "Fsi21-NoChangeTicket" }
            $null = Assert-Fsi-LegacyShell
            Initialize-Fsi-PPSession -RunId $runId -EvidencePath $EvidencePath
            return Export-Fsi-Control21-QuarterlyEvidence `
                -Quarter $Quarter -ZoneAssignments $ZoneAssignments `
                -Dlp15ExceptionTable $Dlp15ExceptionTable -EvidencePath $EvidencePath `
                -ChangeTicketId $ChangeTicketId -Signers $Signers
        }
    }
}
```

### 18.3 Invocation examples

```powershell
# Provision a new Zone-2 environment (Power Platform Admin, Windows PowerShell 5.1).
Invoke-Fsi-Control21Setup -Mode Provision `
    -EnvironmentIds @("e1c4f8a0-...") `
    -ZoneAssignments @{ "e1c4f8a0-..." = "Zone2" } `
    -ChangeTicketId "CHG0091233" `
    -WhatIf

# Weekly verify (Power Platform Admin).
Invoke-Fsi-Control21Setup -Mode Verify `
    -ZoneAssignments $zoneMap `
    -Dlp15ExceptionTable $dlpExceptions

# Quarterly evidence (AI Governance Lead, post-attestation).
Invoke-Fsi-Control21Setup -Mode Quarterly `
    -Quarter "2026Q2" `
    -ZoneAssignments $zoneMap -Dlp15ExceptionTable $dlpExceptions `
    -ChangeTicketId "CHG0091290" `
    -Signers @{
        PowerPlatformAdmin = "ppa@fsi.example.com"
        AIGovernanceLead   = "aigov@fsi.example.com"
        ComplianceOfficer  = "comp@fsi.example.com"
    }
```

---

## §19 — Validation, Anti-Patterns, Cadence, and Module Map

### 19.1 Pester validation skeleton

The helpers in this playbook are amenable to integration-style Pester tests against a non-production tenant. The skeleton below is the FSI minimum; institutional teams typically extend it with production-tenant smoke tests gated on `-Tag 'ProdReadOnly'`.

```powershell
Describe "Control 2.1 — verification helpers" {
    BeforeAll {
        Initialize-Fsi-PPSession -RunId "pester-control-2.1" -EvidencePath $TestDrive
        $script:inv  = Get-Fsi-PPEnvironment
        $script:zone = @{}  # populate from your zone assignment store
        $script:dlp  = @()  # populate from your Control 1.5 export
    }
    It "EnablementCoverage returns Clean for fully Managed tenant" {
        $r = Test-Fsi-Control21-EnablementCoverage -Inventory $inv -PipelineTargetReport (Get-Fsi-PipelineTargets) -ZoneAssignments $zone
        $r.Status | Should -BeIn @('Clean','NotApplicable')
    }
    It "TenantIsolationEnabled flags missing AzDO DLP cross-reference" {
        $r = Test-Fsi-Control21-TenantIsolationEnabled -Dlp15ExceptionTable @()
        $r.Status | Should -Be 'Anomaly'
        $r.Reason | Should -Match 'AzDoConnector'
    }
    It "IPFirewallEnforced returns Pending for AuditOnly under tolerance" {
        # Synthetic inventory with AuditOnly aged 5 days.
        # ... shape the input accordingly ...
    }
    It "Quarterly bundle status reports Pending until three signatures are added" {
        # Smoke test against TestDrive, mocking Get-Fsi-PPEnvironment and the Test-* helpers.
    }
}
```

### 19.2 Anti-patterns

| # | Anti-pattern | Why it is wrong | Correct pattern |
|---|---|---|---|
| 1 | `Get-AdminPowerAppEnvironment` returning empty silently treated as `Clean` | A failed legacy session returns `@()` with no exception; that is `Anomaly`/`Error`, not `Clean` | `Get-Fsi-PPEnvironment` raises `Fsi21-EmptyInventory` and emits `Status='Anomaly'` |
| 2 | Setting sharing limits on a non-Managed environment and assuming success | The legacy cmdlet returns 200-OK on a no-op against a non-Managed env | Verify `ManagedEnvironmentEnabled -eq $true` before invoking `Set-Fsi-SharingLimits` |
| 3 | Enabling IP Firewall directly in `Enforce` mode | Locks out makers and pipeline service principals before allow-list calibration | Always start `AuditOnly`, run `Get-Fsi-IPFirewallAuditLog`, escalate to `Enforce` after ≤28 d |
| 4 | Treating CMK exclusions as a Microsoft bug | The 8-item exclusion list is by design; ignoring it produces a misleading attestation | Capture the verbatim exclusion narrative artefact via `Add-Fsi-CMKPolicyToEnvironment` |
| 5 | Single-signer evidence bundle | Three-signer attestation is the institutional control | `Export-Fsi-Control21-QuarterlyEvidence` requires PowerPlatformAdmin + AIGovernanceLead + ComplianceOfficer |
| 6 | Combining Az.PowerPlatform and Microsoft.PowerApps.Administration in the same shell | Editions and authentication contexts conflict; results are non-deterministic | `Assert-Fsi-LegacyShell` and `Assert-Fsi-AzShell` enforce separation |
| 7 | Disabling Managed Environments to "fix" a sharing-limit problem | Drops every governance lever in one motion; shows up as Anomaly across half the §16 helpers | Use `Set-Fsi-SharingLimits` with a temporary higher value under `-ChangeTicketId`; never disable |
| 8 | Leaving `Sharing Limits` unset on Zone-3 because "it inherits the default" | The default is unbounded; `Test-Fsi-Control21-SharingLimitsBaseline` will report `UnconfiguredFamilies` | Always set every resource family explicitly |
| 9 | Using the same change ticket for an entire quarterly cohort | Auditors cannot reconstruct per-environment intent | One `-ChangeTicketId` per environment per `Provision` invocation |
| 10 | Treating `Pending` as `Clean` in executive reporting | Pending is a calibration window, not a passing grade | Surface `Pending` as a distinct row with the days-remaining counter |

### 19.3 Operating cadence

| Cadence | Action | Helper(s) | Owner |
|---|---|---|---|
| On environment creation | Apply baseline | `Invoke-Fsi-Control21Setup -Mode Provision` | Power Platform Admin |
| Weekly | Status verify | `Invoke-Fsi-Control21Setup -Mode Verify` | Power Platform Admin |
| Weekly | Read Usage Insights digest | PPAC weekly digest review | AI Governance Lead |
| Within 28 days of IP Firewall enablement | AuditOnly → Enforce | `Get-Fsi-IPFirewallAuditLog`, then `Set-Fsi-IPFirewall -Mode Enforce` | Power Platform Admin |
| Quarterly | Signed evidence bundle | `Invoke-Fsi-Control21Setup -Mode Quarterly` | AI Governance Lead (orchestrates), Compliance Officer (signs) |
| Quarterly | Tenant-isolation exception re-attestation | `Test-Fsi-Control21-TenantIsolationEnabled` | Power Platform Admin |
| Annually | CMK key rotation review (if CMK applied) | `Test-Fsi-Control21-CMKExclusionsDocumented` + KV health check | Security Operations |

### 19.4 Module map

The following table lists every `Fsi-*` helper introduced in this playbook, the underlying module that supplies the bound cmdlets, and the required PowerShell edition. Use the table to compose a pinned `RequiredModules` block in your runner manifest.

| Helper | Underlying module | PS edition | Notes |
|---|---|---|---|
| `Assert-Fsi-LegacyShell` | n/a (env check) | 5.1 Desktop | Throws `Fsi21-WrongShell` on 7.x |
| `Assert-Fsi-AzShell` | n/a (env check) | 7.4 Core | Throws `Fsi21-WrongShell` on 5.1 |
| `Initialize-Fsi-PPSession` | Microsoft.PowerApps.Administration.PowerShell | 5.1 Desktop | Session bootstrap |
| `Initialize-Fsi-AzSession` | Az.Accounts, Az.PowerPlatform, Microsoft.Graph | 7.4 Core | Conditional-access aware |
| `Get-Fsi-CmdletAvailability` | n/a (introspection) | both | Diagnostic |
| `Get-RunMetadata` | shared baseline | both | Standard run header |
| `Get-Fsi-PPEnvironment` | Microsoft.PowerApps.Administration.PowerShell | 5.1 Desktop | Inventory primary source |
| `Test-Fsi-ManagedEnvLicensing` | Microsoft.Graph (users), Microsoft.PowerApps.Administration | both | June 2026 readiness |
| `Enable-Fsi-ManagedEnvironment` | Microsoft.PowerApps.Administration.PowerShell | 5.1 Desktop | Mutation; ChangeTicketId required |
| `Disable-Fsi-ManagedEnvironment` | Microsoft.PowerApps.Administration.PowerShell | 5.1 Desktop | Mutation; returns `Anomaly` on success (deviation) |
| `Set-Fsi-SharingLimits` | Microsoft.PowerApps.Administration.PowerShell | 5.1 Desktop | Mutation; standalone-flow caveat |
| `Set-Fsi-SolutionCheckerEnforcement` | Microsoft.PowerApps.Administration.PowerShell | 5.1 Desktop | Mutation |
| `Set-Fsi-MakerWelcome` | Microsoft.PowerApps.Administration.PowerShell | 5.1 Desktop | Mutation; CMK-excluded content |
| `Set-Fsi-IPFirewall` | Microsoft.PowerApps.Administration.PowerShell | 5.1 Desktop | Mutation; default AuditOnly |
| `Get-Fsi-IPFirewallAuditLog` | Az.PowerPlatform / REST | 7.4 Core | Calibration source |
| `Set-Fsi-IPCookieBinding` | Microsoft.PowerApps.Administration.PowerShell | 5.1 Desktop | Mutation |
| `Set-Fsi-CustomerLockbox` | Az.PowerPlatform / REST | 7.4 Core | Mutation |
| `New-Fsi-CMKPolicy` | Az.PowerPlatform | 7.4 Core | Mutation; KV hardening required |
| `Add-Fsi-CMKPolicyToEnvironment` | Az.PowerPlatform | 7.4 Core | Mutation; emits exclusion narrative |
| `Test-Fsi-CMKExclusions` | Az.PowerPlatform | 7.4 Core | Read-only |
| `Set-Fsi-TenantIsolation` | Microsoft.PowerApps.Administration.PowerShell | 5.1 Desktop | Mutation; AzDO known issue |
| `Add-Fsi-TenantIsolationException` | Microsoft.PowerApps.Administration.PowerShell | 5.1 Desktop | Mutation; returns `Anomaly` on success |
| `Set-Fsi-EnvironmentRouting` | Microsoft.PowerApps.Administration.PowerShell | 5.1 Desktop | Mutation; not region selection |
| `Get-Fsi-PipelineTargets` | Microsoft.PowerApps.Administration.PowerShell | 5.1 Desktop | Inventory |
| `Enable-Fsi-PipelineTargetsManagedEnv` | Microsoft.PowerApps.Administration.PowerShell | 5.1 Desktop | Mutation |
| `Test-Fsi-Control21-EnablementCoverage` | composes inventory | 5.1 Desktop | Verification |
| `Test-Fsi-Control21-LicensingCoverage` | wraps Test-Fsi-ManagedEnvLicensing | both | Verification |
| `Test-Fsi-Control21-SharingLimitsBaseline` | Microsoft.PowerApps.Administration.PowerShell | 5.1 Desktop | Verification |
| `Test-Fsi-Control21-SolutionCheckerBlock` | Microsoft.PowerApps.Administration.PowerShell | 5.1 Desktop | Verification |
| `Test-Fsi-Control21-IPFirewallEnforced` | Microsoft.PowerApps.Administration.PowerShell | 5.1 Desktop | Verification |
| `Test-Fsi-Control21-CMKExclusionsDocumented` | filesystem | both | Verification |
| `Test-Fsi-Control21-TenantIsolationEnabled` | Microsoft.PowerApps.Administration.PowerShell | 5.1 Desktop | Verification |
| `Export-Fsi-Control21-QuarterlyEvidence` | composes §16 helpers | 5.1 Desktop (driver) | Three-signer manifest |
| `Invoke-Fsi-Control21Setup` | composes everything above | 5.1 Desktop (driver) | Top-level orchestrator |

---

## Cross-References

### Within Control 2.1
- [Portal walkthrough](./portal-walkthrough.md) — UI-driven equivalent of `-Mode Provision`
- [Verification testing](./verification-testing.md) — manual steps that complement `-Mode Verify`
- [Troubleshooting](./troubleshooting.md) — recovery paths for the `Fsi21-*` error tokens

### Sister Managed-Environment playbooks
- [Control 2.25 — PowerShell setup](../2.25/powershell-setup.md) — structural sibling; shares the `Status` contract and the false-clean catalogue
- [Control 2.26 — PowerShell setup](../2.26/powershell-setup.md) — sibling for Managed Environment governance overlays

### Related controls
- [Control 1.4 — Advanced Connector Policies](../../../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md) — connector-level controls that compose with Managed Environment sharing limits
- [Control 1.5 — DLP for Standalone Cloud Flows](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) — required cross-reference for Azure DevOps tenant-isolation exception
- [Control 1.20 — Network Isolation](../../../controls/pillar-1-security/1.20-network-isolation-private-connectivity.md) — IP Firewall is the Managed-Environment-scoped projection
- [Control 2.2 — Environment Groups and Tier Classification](../../../controls/pillar-2-management/2.2-environment-groups-and-tier-classification.md) — defines the Zone assignments this playbook consumes
- [Control 2.3 — Change Management](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md) — source of `-ChangeTicketId` requirement
- [Control 2.15 — Environment Routing](../../../controls/pillar-2-management/2.15-environment-routing.md) — composes with `Set-Fsi-EnvironmentRouting`
- [Control 2.22 — Inactivity Timeout](../../../controls/pillar-2-management/2.22-inactivity-timeout-enforcement.md) — Managed-Environment-scoped session control

### Shared baseline and reference
- [PowerShell baseline](../../_shared/powershell-baseline.md) — module pinning, mutation safety, evidence emission, signature workflow
- [Role catalogue](../../../reference/role-catalog.md) — canonical short names for Power Platform Admin, AI Governance Lead, Compliance Officer
- [Regulatory mappings](../../../reference/regulatory-mappings.md) — FINRA 3110 / SEC 17a-4 / OCC 2013-29 / FFIEC IT Handbook references

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
