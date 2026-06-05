# PowerShell Setup: Control 2.15 — Environment Routing and Auto-Provisioning

!!! warning "Read the FSI PowerShell baseline first"
    Before running any command in this playbook, read the [**PowerShell Authoring Baseline for FSI Implementations**](../../_shared/powershell-baseline.md). It is the canonical source for module version pinning, mutation safety (`-WhatIf` / `SupportsShouldProcess`), Dataverse compatibility, and SHA-256 evidence emission. The snippets below intentionally show abbreviated patterns; the baseline is authoritative.

**Last Updated:** April 2026
**Modules Required:** `Microsoft.PowerApps.Administration.PowerShell` (Desktop edition / Windows PowerShell 5.1 only)

---

## Prerequisites

```powershell
# REQUIRED: pin to a CAB-approved version. Floating versions break SOX 404 / OCC 2023-17 reproducibility.
Install-Module -Name Microsoft.PowerApps.Administration.PowerShell `
    -RequiredVersion '<approved-version>' `
    -Repository PSGallery `
    -Scope CurrentUser `
    -AllowClobber `
    -AcceptLicense

# Edition guard — Power Apps Administration cmdlets are Desktop-only.
# Without this guard, a PS 7 host silently returns empty results and produces FALSE-CLEAN evidence.
if ($PSVersionTable.PSEdition -ne 'Desktop') {
    throw "Microsoft.PowerApps.Administration.PowerShell requires Windows PowerShell 5.1 (Desktop). Detected: $($PSVersionTable.PSEdition) $($PSVersionTable.PSVersion)."
}

param(
    [Parameter(Mandatory)] [string] $TenantId
)
Add-PowerAppsAccount -TenantID $TenantId
```

> **For unattended runs**, supply `-ApplicationId` / `-ClientSecret` to `Add-PowerAppsAccount`. The service principal must hold the Power Platform Admin role assignment.

---

## Read the Current Routing Configuration

This is **read-only** — no `-WhatIf` required. Use it to capture baseline evidence before any change.

```powershell
$tenantSettings = Get-TenantSettings

# The routing flags live under powerPlatform.governance
$routing = [PSCustomObject]@{
    EnableDefaultEnvironmentRouting = $tenantSettings.powerPlatform.governance.enableDefaultEnvironmentRouting
    EnvironmentRoutingAllMakers     = $tenantSettings.powerPlatform.governance.environmentRoutingAllMakers
    TargetEnvironmentGroupId        = $tenantSettings.powerPlatform.governance.environmentRoutingTargetEnvironmentGroupId
    TargetSecurityGroupId           = $tenantSettings.powerPlatform.governance.environmentRoutingTargetSecurityGroupId
    CapturedUtc                     = (Get-Date).ToUniversalTime().ToString('o')
}
$routing | Format-List
```

> **Multi-rule routing** (multiple security-group → environment-group mappings) is configured **only via PPAC** today. The PowerShell properties above represent the legacy single-target shape and are still authoritative for the on/off flag and the *primary* target. Capture the multi-rule order from PPAC export as supplementary evidence.

---

## Enable Environment Routing (Mutating Script)

This script changes tenant state. It follows the FSI baseline: `SupportsShouldProcess`, before-snapshot, transcript, SHA-256 evidence emission.

```powershell
<#
.SYNOPSIS
    Enables Power Platform environment routing per Control 2.15.

.DESCRIPTION
    - Snapshots current tenant settings to disk for rollback.
    - Sets enableDefaultEnvironmentRouting = $true.
    - Optionally sets environmentRoutingAllMakers and the primary target group.
    - Emits SHA-256-hashed evidence + manifest per FSI baseline section 4.

.PARAMETER TargetEnvironmentGroupId
    GUID of the environment group that will hold catch-all routed dev envs.

.PARAMETER AllMakers
    If set, route both new and existing makers. Otherwise, new makers only.

.EXAMPLE
    .\Enable-EnvironmentRouting.ps1 -TenantId <id> -TargetEnvironmentGroupId <guid> -AllMakers -WhatIf
    .\Enable-EnvironmentRouting.ps1 -TenantId <id> -TargetEnvironmentGroupId <guid> -AllMakers -Confirm
#>
[CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
param(
    [Parameter(Mandatory)] [string] $TenantId,
    [Parameter(Mandatory)] [string] $TargetEnvironmentGroupId,
    [string] $TargetSecurityGroupId,
    [switch] $AllMakers,
    [string] $EvidencePath = ".\evidence\2.15"
)

$ErrorActionPreference = 'Stop'

if ($PSVersionTable.PSEdition -ne 'Desktop') {
    throw "Run in Windows PowerShell 5.1 (Desktop). Detected: $($PSVersionTable.PSEdition) $($PSVersionTable.PSVersion)."
}

New-Item -ItemType Directory -Force -Path $EvidencePath | Out-Null
$ts = Get-Date -Format 'yyyyMMddTHHmmssZ'
Start-Transcript -Path "$EvidencePath\transcript-$ts.log" -IncludeInvocationHeader

try {
    Add-PowerAppsAccount -TenantID $TenantId

    # 1. BEFORE snapshot (required for rollback evidence)
    $before = Get-TenantSettings
    $beforePath = "$EvidencePath\tenant-settings-before-$ts.json"
    $before | ConvertTo-Json -Depth 50 | Set-Content -Path $beforePath -Encoding UTF8

    # 2. Build mutated copy
    $after = $before
    $after.powerPlatform.governance.enableDefaultEnvironmentRouting = $true
    $after.powerPlatform.governance | Add-Member -NotePropertyName 'environmentRoutingAllMakers' `
        -NotePropertyValue ([bool]$AllMakers) -Force
    $after.powerPlatform.governance | Add-Member -NotePropertyName 'environmentRoutingTargetEnvironmentGroupId' `
        -NotePropertyValue $TargetEnvironmentGroupId -Force
    if ($TargetSecurityGroupId) {
        $after.powerPlatform.governance | Add-Member -NotePropertyName 'environmentRoutingTargetSecurityGroupId' `
            -NotePropertyValue $TargetSecurityGroupId -Force
    }

    # 3. ShouldProcess gate
    if ($PSCmdlet.ShouldProcess("Tenant $TenantId", "Enable environment routing -> group $TargetEnvironmentGroupId (AllMakers=$AllMakers)")) {
        Set-TenantSettings -RequestBody $after
        Write-Host "[OK] Environment routing enabled." -ForegroundColor Green
    }

    # 4. AFTER snapshot + SHA-256 manifest
    $afterActual = Get-TenantSettings
    $afterPath = "$EvidencePath\tenant-settings-after-$ts.json"
    $afterActual | ConvertTo-Json -Depth 50 | Set-Content -Path $afterPath -Encoding UTF8

    $manifest = @($beforePath, $afterPath, "$EvidencePath\transcript-$ts.log") | ForEach-Object {
        [PSCustomObject]@{
            file          = (Split-Path $_ -Leaf)
            sha256        = (Get-FileHash -Path $_ -Algorithm SHA256).Hash
            bytes         = (Get-Item $_).Length
            generated_utc = $ts
            control       = '2.15'
        }
    }
    $manifest | ConvertTo-Json -Depth 5 | Set-Content -Path "$EvidencePath\manifest-$ts.json" -Encoding UTF8
    Write-Host "[OK] Evidence written to $EvidencePath" -ForegroundColor Green
}
finally {
    Stop-Transcript | Out-Null
}
```

> **Always invoke first with `-WhatIf`.** This is the difference between an undo-able config change and a tenant-wide maker provisioning incident.

---

## Disable Environment Routing (Rollback)

```powershell
[CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
param(
    [Parameter(Mandatory)] [string] $TenantId,
    [string] $EvidencePath = ".\evidence\2.15"
)
$ErrorActionPreference = 'Stop'
Add-PowerAppsAccount -TenantID $TenantId

$before = Get-TenantSettings
$ts = Get-Date -Format 'yyyyMMddTHHmmssZ'
$before | ConvertTo-Json -Depth 50 | Set-Content "$EvidencePath\rollback-before-$ts.json" -Encoding UTF8

$after = $before
$after.powerPlatform.governance.enableDefaultEnvironmentRouting = $false

if ($PSCmdlet.ShouldProcess("Tenant $TenantId", "Disable environment routing")) {
    Set-TenantSettings -RequestBody $after
    Write-Host "[OK] Environment routing disabled." -ForegroundColor Yellow
}
```

> Disabling routing **does not** delete already-provisioned personal dev environments. Decommission those separately via Control 2.16 (environment lifecycle) procedures.

---

## Inventory: Routed Personal Dev Environments

Use this read-only inventory after routing has been live for one supervisory cycle. It identifies developer environments likely created by routing and flags ones outside the target groups (a misconfiguration signal).

```powershell
param(
    [string] $ExpectedGroupNamePattern = 'FSI-Personal-Dev-*',
    [string] $OutDir = ".\evidence\2.15"
)
$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$envs = Get-AdminPowerAppEnvironment
$rows = foreach ($e in $envs | Where-Object EnvironmentType -eq 'Developer') {
    [PSCustomObject]@{
        DisplayName   = $e.DisplayName
        EnvironmentId = $e.EnvironmentName
        Region        = $e.Location
        Created       = $e.Properties.createdTime
        CreatedBy     = $e.Properties.createdBy.displayName
        IsManaged     = ($e.Properties.protectionLevel -ne 'Standard')
        EnvGroup      = $e.Properties.parentEnvironmentGroup.displayName
    }
}

$rows | Export-Csv "$OutDir\dev-env-inventory-$(Get-Date -Format 'yyyyMMdd').csv" -NoTypeInformation

# Anomaly: dev env that is NOT in the expected group pattern
$anomalies = $rows | Where-Object { $_.EnvGroup -notlike $ExpectedGroupNamePattern -or -not $_.IsManaged }
if ($anomalies) {
    Write-Warning "Found $($anomalies.Count) developer environments outside the routing target groups."
    $anomalies | Format-Table DisplayName, CreatedBy, EnvGroup, IsManaged
}
```

---

## Evidence Storage

All artifacts produced by this playbook (`tenant-settings-before-*.json`, `tenant-settings-after-*.json`, `transcript-*.log`, `manifest-*.json`, `dev-env-inventory-*.csv`) must be transferred to a WORM-locked store (Microsoft Purview retention lock or Azure Storage immutability policy) per SEC 17a-4(f) and FINRA 4511 expectations. The local `evidence\2.15` directory is a staging area only.

---

[Back to Control 2.15](../../../controls/pillar-2-management/2.15-environment-routing.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
