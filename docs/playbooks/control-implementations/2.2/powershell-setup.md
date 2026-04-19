# PowerShell Setup: Control 2.2 — Environment Groups and Tier Classification

!!! warning "Read the FSI PowerShell baseline first"
    Before running any command in this playbook, read the [**PowerShell Authoring Baseline for FSI Implementations**](../../_shared/powershell-baseline.md). It is the canonical source for module version pinning, sovereign-cloud (GCC / GCC High / DoD) endpoints, mutation safety (`-WhatIf` / `SupportsShouldProcess`), Dataverse compatibility, and SHA-256 evidence emission.

**Last Updated:** April 2026
**Modules required:** `Microsoft.PowerApps.Administration.PowerShell` (≥ 2.0.190); the Power Platform CLI (`pac`) for any rule-publishing automation.

---

## Scope and limitations

| Operation | Supported via PowerShell? | Notes |
|---|---|---|
| List environment groups | ✅ `Get-AdminPowerAppEnvironmentGroup` | GA |
| List environments by group | ✅ `Get-AdminPowerAppEnvironment` filter | GA |
| Add environment to group | ✅ `Set-AdminPowerAppEnvironment -EnvironmentGroupId` | GA |
| Remove environment from group | ✅ same cmdlet with `-EnvironmentGroupId $null` | GA |
| Create environment group | ⚠️ Portal-first | Programmatic creation is currently inconsistent across module versions; standard practice is portal creation, then PowerShell for membership and audit. |
| Read / set group **rules** | ❌ | Rule configuration is not exposed by the admin module. Use the portal walkthrough; verify enforcement via per-environment setting reads. |

---

## Prerequisites

```powershell
# Pin the module version per the FSI baseline
$module = 'Microsoft.PowerApps.Administration.PowerShell'
$min    = '2.0.190'

if (-not (Get-Module -ListAvailable -Name $module |
          Where-Object { $_.Version -ge [version]$min })) {
    Install-Module -Name $module -MinimumVersion $min -Scope CurrentUser -Force -AllowClobber
}
Import-Module $module

# Interactive auth (operator workstation)
Add-PowerAppsAccount

# Service-principal auth (automation runner) — store secret in a vault, never inline
# $appId = $env:FSI_PPSP_APPID
# $secret = $env:FSI_PPSP_SECRET
# $tenantId = $env:FSI_PPSP_TENANT
# Add-PowerAppsAccount -ApplicationId $appId -ClientSecret $secret -TenantID $tenantId
```

> **Sovereign clouds (GCC / GCC High / DoD):** add `-Endpoint usgov`, `-Endpoint usgovhigh`, or `-Endpoint dod` to `Add-PowerAppsAccount`. See the PowerShell baseline for the full table.

---

## Read scripts (read-only — safe to run any time)

### List all environment groups

```powershell
Get-AdminPowerAppEnvironmentGroup |
    Select-Object EnvironmentGroupId, DisplayName, Description, CreatedTime |
    Sort-Object DisplayName |
    Format-Table -AutoSize
```

### List environments in each group (with FSI naming check)

```powershell
$groups = Get-AdminPowerAppEnvironmentGroup
$envs   = Get-AdminPowerAppEnvironment

foreach ($g in $groups) {
    $members = $envs | Where-Object { $_.EnvironmentGroupId -eq $g.EnvironmentGroupId }
    $expectedZone = if ($g.DisplayName -match 'FSI-Z(\d)') { $Matches[1] } else { '?' }

    Write-Host "`nGroup: $($g.DisplayName)  (Zone $expectedZone)" -ForegroundColor Cyan
    Write-Host "  Group ID : $($g.EnvironmentGroupId)"
    Write-Host "  Members  : $($members.Count)"
    $members |
        Select-Object DisplayName,
                      EnvironmentName,
                      EnvironmentType,
                      Location,
                      @{ Name = 'IsManaged'; Expression = {
                          $_.Properties.governanceConfiguration.protectionLevel -ne 'Standard'
                      }} |
        Format-Table -AutoSize
}
```

---

## Mutation scripts (require `-WhatIf` first per FSI baseline)

### Add a Managed Environment to a group

```powershell
function Add-FsiEnvironmentToGroup {
    [CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'High')]
    param(
        [Parameter(Mandatory)] [string] $EnvironmentName,
        [Parameter(Mandatory)] [string] $EnvironmentGroupId
    )

    $env = Get-AdminPowerAppEnvironment -EnvironmentName $EnvironmentName
    if (-not $env) { throw "Environment '$EnvironmentName' not found." }

    $isManaged = $env.Properties.governanceConfiguration.protectionLevel -ne 'Standard'
    if (-not $isManaged) {
        throw "Environment '$($env.DisplayName)' is not a Managed Environment. Enable Managed Environment first (Control 2.1)."
    }

    if ($PSCmdlet.ShouldProcess(
            "Environment '$($env.DisplayName)'",
            "Assign to environment group '$EnvironmentGroupId'")) {

        Set-AdminPowerAppEnvironment `
            -EnvironmentName $EnvironmentName `
            -EnvironmentGroupId $EnvironmentGroupId | Out-Null

        Write-Host "[OK] Assigned $($env.DisplayName) -> $EnvironmentGroupId" -ForegroundColor Green
    }
}

# Dry-run first
Add-FsiEnvironmentToGroup -EnvironmentName '<env-id>' -EnvironmentGroupId '<group-id>' -WhatIf
# Then commit
# Add-FsiEnvironmentToGroup -EnvironmentName '<env-id>' -EnvironmentGroupId '<group-id>'
```

---

## Audit-evidence export

Generates the CSV bundle expected by [Verification & Testing](verification-testing.md) and emits a SHA-256 manifest per the FSI baseline.

```powershell
<#
.SYNOPSIS
    Exports Control 2.2 audit evidence: environment groups, members, and a SHA-256 manifest.

.NOTES
    Last Updated   : April 2026
    Related Control: Control 2.2 - Environment Groups and Tier Classification
#>

[CmdletBinding()]
param(
    [string] $OutputRoot = 'C:\FSI-Evidence\Control-2.2'
)

$ErrorActionPreference = 'Stop'
$timestamp   = Get-Date -Format 'yyyyMMdd_HHmm'
$exportPath  = Join-Path $OutputRoot $timestamp
New-Item -ItemType Directory -Path $exportPath -Force | Out-Null

Write-Host "=== Control 2.2 evidence export ===" -ForegroundColor Cyan
Write-Host "Output: $exportPath"

# 1. Environment groups
$groups = Get-AdminPowerAppEnvironmentGroup
$groups |
    Select-Object EnvironmentGroupId, DisplayName, Description, CreatedTime |
    Export-Csv -Path (Join-Path $exportPath 'EnvironmentGroups.csv') -NoTypeInformation -Encoding UTF8

# 2. Environment-to-group mapping
$envs = Get-AdminPowerAppEnvironment
$envs |
    Select-Object DisplayName,
                  EnvironmentName,
                  EnvironmentGroupId,
                  EnvironmentType,
                  Location,
                  @{ Name = 'IsManaged'; Expression = {
                      $_.Properties.governanceConfiguration.protectionLevel -ne 'Standard'
                  }},
                  @{ Name = 'CapturedUtc'; Expression = { (Get-Date).ToUniversalTime().ToString('o') }} |
    Export-Csv -Path (Join-Path $exportPath 'EnvironmentMembership.csv') -NoTypeInformation -Encoding UTF8

# 3. Group summary
$envs |
    Group-Object EnvironmentGroupId |
    ForEach-Object {
        $name = ($groups | Where-Object EnvironmentGroupId -eq $_.Name).DisplayName
        [pscustomobject]@{
            GroupId          = $_.Name
            GroupDisplayName = if ($name) { $name } else { '(Ungrouped)' }
            EnvironmentCount = $_.Count
        }
    } |
    Export-Csv -Path (Join-Path $exportPath 'GroupSummary.csv') -NoTypeInformation -Encoding UTF8

# 4. SHA-256 manifest (FSI baseline requirement)
Get-ChildItem $exportPath -Filter *.csv |
    ForEach-Object {
        [pscustomobject]@{
            File   = $_.Name
            SHA256 = (Get-FileHash -Algorithm SHA256 -Path $_.FullName).Hash
            Bytes  = $_.Length
        }
    } |
    Export-Csv -Path (Join-Path $exportPath 'manifest.sha256.csv') -NoTypeInformation -Encoding UTF8

Write-Host "[OK] Evidence pack ready: $exportPath" -ForegroundColor Green
```

---

## Validation script — `Validate-Control-2.2.ps1`

Read-only. Fails fast on the conditions documented in the [Verification & Testing](verification-testing.md) playbook.

```powershell
<#
.SYNOPSIS
    Validates Control 2.2 — Environment Groups and Tier Classification.

.PARAMETER FailOnWarning
    Treat warnings as failures (recommended for CI).

.OUTPUTS
    Exit code 0 = pass, 1 = fail.
#>

[CmdletBinding()]
param(
    [switch] $FailOnWarning
)

$ErrorActionPreference = 'Stop'
$failures = @()
$warnings = @()

Write-Host "=== Control 2.2 validation ===" -ForegroundColor Cyan

$groups = Get-AdminPowerAppEnvironmentGroup
$envs   = Get-AdminPowerAppEnvironment

# Check 1 — at least one FSI-Z{n} group exists per zone
foreach ($zone in 1..3) {
    $zoneGroups = $groups | Where-Object { $_.DisplayName -match "FSI-Z$zone(-|$)" }
    if (-not $zoneGroups) {
        $failures += "No environment group named FSI-Z$zone-* found."
    } else {
        Write-Host "[PASS] Zone $zone groups: $(@($zoneGroups).Count)" -ForegroundColor Green
    }
}

# Check 2 — every production environment is in a group
$prodEnvs       = $envs | Where-Object EnvironmentType -eq 'Production'
$ungroupedProd  = $prodEnvs | Where-Object { -not $_.EnvironmentGroupId }
if ($ungroupedProd) {
    $failures += "Ungrouped production environments: $(($ungroupedProd.DisplayName) -join ', ')"
} else {
    Write-Host "[PASS] All production environments are grouped." -ForegroundColor Green
}

# Check 3 — every grouped environment is Managed
$groupedEnvs    = $envs | Where-Object { $_.EnvironmentGroupId }
$unmanagedInGrp = $groupedEnvs | Where-Object {
    $_.Properties.governanceConfiguration.protectionLevel -eq 'Standard'
}
if ($unmanagedInGrp) {
    $failures += "Unmanaged environments inside groups: $(($unmanagedInGrp.DisplayName) -join ', ')"
} else {
    Write-Host "[PASS] All grouped environments are Managed Environments." -ForegroundColor Green
}

# Check 4 — group descriptions reference governance zone
$noZoneInDesc = $groups | Where-Object {
    [string]::IsNullOrWhiteSpace($_.Description) -or
    $_.Description -notmatch 'Zone\s*[123]'
}
if ($noZoneInDesc) {
    $warnings += "Groups missing 'Zone {1|2|3}' in description: $(($noZoneInDesc.DisplayName) -join ', ')"
}

# Summary
Write-Host "`n=== Summary ===" -ForegroundColor Cyan
Write-Host "Groups        : $(@($groups).Count)"
Write-Host "Environments  : $(@($envs).Count)"
Write-Host "Grouped       : $(@($groupedEnvs).Count)"
Write-Host "Failures      : $(@($failures).Count)" -ForegroundColor (if ($failures) { 'Red' } else { 'Green' })
Write-Host "Warnings      : $(@($warnings).Count)" -ForegroundColor (if ($warnings) { 'Yellow' } else { 'Green' })

$failures | ForEach-Object { Write-Host "[FAIL] $_" -ForegroundColor Red }
$warnings | ForEach-Object { Write-Host "[WARN] $_" -ForegroundColor Yellow }

if ($failures -or ($FailOnWarning -and $warnings)) { exit 1 }
exit 0
```

---

## Notes

- Group **creation** and **rule configuration** remain portal-first per the [portal walkthrough](portal-walkthrough.md).
- For automated environment provisioning that auto-assigns to the correct zone group, see the [Environment Lifecycle Management](../../advanced-implementations/environment-lifecycle-management/index.md) advanced implementation.

---

*Updated: April 2026 | Version: v1.4.0*

[Back to Control 2.2](../../../controls/pillar-2-management/2.2-environment-groups-and-tier-classification.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification & Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
