# PowerShell Setup: Control 1.1 - Restrict Agent Publishing by Authorization

!!! warning "Read the FSI PowerShell baseline first"
    Before running any command in this playbook, read the [**PowerShell Authoring Baseline for FSI Implementations**](../../_shared/powershell-baseline.md). It is the canonical source for module version pinning, sovereign-cloud (GCC / GCC High / DoD) endpoints, mutation safety (`-WhatIf` / `SupportsShouldProcess`), Dataverse compatibility, and SHA-256 evidence emission. Snippets below may show abbreviated patterns; the baseline is authoritative.

**Last Updated:** April 2026
**Modules Required:** `Microsoft.PowerApps.Administration.PowerShell` (pinned), optional `Microsoft.Xrm.Data.PowerShell` for Dataverse role assignment

!!! warning "Critical: Dataverse-backed environments"
    The legacy `*-AdminPowerAppEnvironmentRoleAssignment` cmdlets used in this playbook **only work on environments without a Dataverse database**. Every governed Microsoft Copilot Studio production environment is Dataverse-backed.

    On a Dataverse environment:

    - `Get-AdminPowerAppEnvironmentRoleAssignment` returns an empty array (not an error).
    - `Set-AdminPowerAppEnvironmentRoleAssignment` returns 403 / "Forbidden".

    **An empty `Get-` result is NOT proof the environment is hardened — it may simply mean the cmdlet doesn't apply.** Always check `IsDefault` and the environment's Dataverse provisioning status first; for Dataverse environments, do role assignment via PPAC (Settings > Users + permissions > Security roles) or the Dataverse Web API. The script below detects this and routes accordingly.

!!! warning "Sovereign cloud (GCC / GCC-High / DoD)"
    The default `Add-PowerAppsAccount` authenticates against **commercial** endpoints. In a sovereign tenant, this returns 0 environments and reports a false-clean PASS.

    For sovereign tenants, add `-Endpoint usgov`, `-Endpoint usgovhigh`, or `-Endpoint dod` to **every** Power Apps cmdlet in this playbook (including `Add-PowerAppsAccount`, `Get-AdminPowerAppEnvironment`, `Get-AdminPowerAppEnvironmentRoleAssignment`, `Get-TenantSettings`, `Set-TenantSettings`).

## Prerequisites

```powershell
# Require Windows PowerShell 5.1 - the Power Platform admin module ships as Desktop edition
# and many cmdlets fail silently on PowerShell 7.
if ($PSVersionTable.PSEdition -ne 'Desktop' -or $PSVersionTable.PSVersion.Major -ne 5) {
    throw "This playbook requires Windows PowerShell 5.1 (Desktop edition). Current: $($PSVersionTable.PSEdition) $($PSVersionTable.PSVersion). Open 'Windows PowerShell' (not 'PowerShell 7') and re-run."
}

# Pin the module version. Do NOT install with -Force without a -RequiredVersion in regulated change windows.
# Verify the version your firm has tested and approved before running in production.
$ApprovedModuleVersion = '2.0.198'   # <-- replace with your firm's tested-and-approved version
Install-Module -Name Microsoft.PowerApps.Administration.PowerShell `
    -RequiredVersion $ApprovedModuleVersion `
    -Repository PSGallery `
    -Scope CurrentUser `
    -AcceptLicense `
    -Force

Import-Module Microsoft.PowerApps.Administration.PowerShell -RequiredVersion $ApprovedModuleVersion

# Connect to Power Platform (interactive authentication for COMMERCIAL tenants).
# For sovereign tenants, add -Endpoint usgov | usgovhigh | dod
Add-PowerAppsAccount

# For automated/unattended scenarios, use service principal authentication:
# $appId    = "<Application-Client-ID>"
# $secret   = "<Client-Secret>"  # Pull from Key Vault, do NOT inline
# $tenantId = "<Tenant-ID>"
# Add-PowerAppsAccount -ApplicationId $appId -ClientSecret $secret -TenantID $tenantId
```

---

## Configuration Script

### Detect environment type before running role-assignment cmdlets

```powershell
$EnvironmentName = "your-environment-id"

$env = Get-AdminPowerAppEnvironment -EnvironmentName $EnvironmentName
$isDataverseBacked = [bool]$env.CommonDataServiceDatabaseProvisioningState -and `
                     $env.CommonDataServiceDatabaseProvisioningState -eq 'Succeeded'

if ($isDataverseBacked) {
    Write-Warning "Environment '$($env.DisplayName)' is Dataverse-backed."
    Write-Warning "  *-AdminPowerAppEnvironmentRoleAssignment cmdlets will NOT work here."
    Write-Warning "  Assign the 'Environment Maker' Dataverse security role via:"
    Write-Warning "    PPAC > Environments > [env] > Settings > Users + permissions > Security roles"
    Write-Warning "  Or use the Dataverse Web API / Microsoft.Xrm.Data.PowerShell module."
    Write-Warning "Skipping the legacy cmdlet path for this environment."
    return
}
```

### Get Current Environment Permissions (non-Dataverse environments only)

```powershell
$envPermissions = Get-AdminPowerAppEnvironmentRoleAssignment -EnvironmentName $EnvironmentName
$envPermissions | Format-Table PrincipalDisplayName, RoleName, PrincipalType
```

> **Filter property note:** The cmdlet returns `RoleName` (with **spaces**, e.g., `"Environment Maker"`, `"System Administrator"`), **not** `RoleType` and **not** the camel-case `"EnvironmentMaker"`. Filtering on the wrong field/value silently returns `$null` and produces a false-clean PASS.

### Remove Environment Maker Role from "All Users" / Tenant principal

```powershell
$allUsersPermission = $envPermissions | Where-Object {
    $_.PrincipalType -eq "Tenant" -and $_.RoleName -eq "Environment Maker"
}

if ($allUsersPermission) {
    if ($PSCmdlet.ShouldProcess($EnvironmentName, "Remove 'Environment Maker' from Tenant principal")) {
        Remove-AdminPowerAppEnvironmentRoleAssignment `
            -EnvironmentName $EnvironmentName `
            -RoleId $allUsersPermission.RoleId
        Write-Host "Removed Environment Maker role from All Users" -ForegroundColor Yellow
    }
}
```

### Add Environment Maker Role to Authorized Security Group (non-Dataverse only)

```powershell
$SecurityGroupId = "your-security-group-id"  # Get from Entra ID

if ($PSCmdlet.ShouldProcess($EnvironmentName, "Assign 'Environment Maker' to group $SecurityGroupId")) {
    Set-AdminPowerAppEnvironmentRoleAssignment `
        -EnvironmentName $EnvironmentName `
        -PrincipalType Group `
        -PrincipalObjectId $SecurityGroupId `
        -RoleName EnvironmentMaker

    Write-Host "Environment Maker role assigned to authorized security group" -ForegroundColor Green
}
```

> Note the small but important inconsistency: `Set-AdminPowerAppEnvironmentRoleAssignment` accepts `-RoleName EnvironmentMaker` (no space), while `Get-AdminPowerAppEnvironmentRoleAssignment` returns `RoleName = "Environment Maker"` (with space). Both are documented behaviors in current Microsoft Learn pages — verify on your installed module version.

### Tenant Setting: `disableShareWithEveryone` (supplementary canvas-app hygiene)

!!! note "What this setting actually does"
    The `disableShareWithEveryone` tenant setting governs **Power Apps canvas-app sharing**. It does **not** control Copilot Studio agent sharing, Microsoft 365 Copilot agent publishing, or Teams-channel agent distribution — i.e., it does not enforce Control 1.1's primary scope.

    Configure this as **supplementary canvas-app hygiene** for tenants that also use canvas apps. The actual agent-publishing levers are:

    - **Copilot Studio data policies** (per environment / environment group / tenant)
    - **M365 Admin Center** agent block (instance-level — see Portal Walkthrough Step 9)
    - **Managed Environment** agent-sharing limits (see Portal Walkthrough Step 4)
    - **Tenant Copilot Studio authors** setting (see Portal Walkthrough Step 3, Layer A)

```powershell
# Snapshot tenant settings BEFORE mutation - required for change-control evidence and rollback
$snapshotPath = ".\tenant-settings-snapshot-$(Get-Date -Format 'yyyyMMdd-HHmmss').json"
$settings = Get-TenantSettings
$settings | ConvertTo-Json -Depth 20 | Out-File -FilePath $snapshotPath -Encoding UTF8
$snapshotHash = (Get-FileHash -Path $snapshotPath -Algorithm SHA256).Hash
Write-Host "Tenant settings snapshot: $snapshotPath" -ForegroundColor Cyan
Write-Host "  SHA-256: $snapshotHash" -ForegroundColor Cyan

# CORRECT property path is at the ROOT of the settings object.
# Earlier versions of this playbook used $settings.powerPlatform.powerApps.disableShareWithEveryone
# which does NOT exist in the API response - the Where-Object always evaluated $null and emitted false WARN.
if ($settings.disableShareWithEveryone -ne $true) {
    if ($PSCmdlet.ShouldProcess("Tenant", "Set disableShareWithEveryone = true")) {
        $settings.disableShareWithEveryone = $true
        Set-TenantSettings -RequestBody $settings
        Write-Host "Share with Everyone disabled (canvas apps)" -ForegroundColor Green
        Write-Host "Rollback: Re-import $snapshotPath via Set-TenantSettings if revert needed." -ForegroundColor Yellow
    }
} else {
    Write-Host "Already disabled - no change" -ForegroundColor Gray
}
```

---

## Validation Script

```powershell
# Validation: Check final role assignments (non-Dataverse environments only)
Write-Host "`n=== Environment Maker Role Assignments ===" -ForegroundColor Cyan

$env = Get-AdminPowerAppEnvironment -EnvironmentName $EnvironmentName
if ($env.CommonDataServiceDatabaseProvisioningState -eq 'Succeeded') {
    Write-Host "[INFO] Dataverse-backed environment - validate via PPAC Security Roles, not this script" -ForegroundColor Yellow
    return
}

$envPermissions = Get-AdminPowerAppEnvironmentRoleAssignment -EnvironmentName $EnvironmentName
$envPermissions |
    Where-Object { $_.RoleName -eq "Environment Maker" } |
    Format-Table PrincipalDisplayName, PrincipalType

# Verify no "All Users" / Tenant assignment remains
$remainingAllUsers = $envPermissions |
    Where-Object { $_.PrincipalType -eq "Tenant" -and $_.RoleName -eq "Environment Maker" }

if ($remainingAllUsers) {
    Write-Host "FAIL: Tenant principal still has Environment Maker role" -ForegroundColor Red
    exit 2
} else {
    Write-Host "PASS: Tenant principal does not have Environment Maker role" -ForegroundColor Green
}

# Check tenant setting (CORRECT path - root level, not powerPlatform.powerApps)
$settings = Get-TenantSettings
if ($settings.disableShareWithEveryone -eq $true) {
    Write-Host "PASS: Share with Everyone (canvas apps) is disabled" -ForegroundColor Green
} else {
    Write-Host "WARN: Share with Everyone (canvas apps) is NOT disabled" -ForegroundColor Yellow
}
```

---

## Complete Configuration Script

```powershell
<#
.SYNOPSIS
    Configures Control 1.1 - Restrict Agent Publishing by Authorization (non-Dataverse environments + tenant)

.DESCRIPTION
    Automates baseline checks for Control 1.1:
    1. Detects Dataverse-backed environments and routes them to PPAC (script does NOT mutate them)
    2. For non-Dataverse environments: removes Environment Maker from Tenant principal, assigns to authorized group
    3. Tenant: disables canvas-app "Share with Everyone" (supplementary hygiene; NOT the primary 1.1 control)

    Manual follow-up REQUIRED:
    - Dataverse-backed environments: assign Environment Maker / Copilot Author via PPAC > Settings > Users + permissions > Security roles
    - Managed Environment agent-sharing limits (Portal Walkthrough Step 4)
    - Copilot Studio per-agent authentication (Portal Walkthrough Step 6)
    - M365 Admin Center instance-level Block actions (Portal Walkthrough Step 9)
    - Tenant Copilot Studio authors setting (Portal Walkthrough Step 3, Layer A)
    - Approval workflow / release gates (Portal Walkthrough Step 5)

.PARAMETER EnvironmentName
    The GUID of the target Power Platform environment.

.PARAMETER SecurityGroupId
    The GUID of the authorized security group in Entra ID.

.PARAMETER EvidencePath
    Directory for tenant-settings snapshot, JSON evidence emit, and SHA-256 hash file.

.PARAMETER Endpoint
    'prod' (default), 'usgov', 'usgovhigh', 'dod'. MUST match your tenant's sovereign cloud.

.EXAMPLE
    .\Configure-Control-1.1.ps1 -EnvironmentName "abc..." -SecurityGroupId "def..." -EvidencePath "C:\Evidence\1.1"

.EXAMPLE  # Dry run
    .\Configure-Control-1.1.ps1 -EnvironmentName "abc..." -SecurityGroupId "def..." -EvidencePath "C:\Evidence\1.1" -WhatIf

.NOTES
    Last Updated: April 2026
    Related Control: Control 1.1
    Module pin: see $ApprovedModuleVersion in Prerequisites
#>

[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'High')]
param(
    [Parameter(Mandatory = $true)]
    [string]$EnvironmentName,

    [Parameter(Mandatory = $true)]
    [string]$SecurityGroupId,

    [Parameter(Mandatory = $true)]
    [string]$EvidencePath,

    [ValidateSet('prod','usgov','usgovhigh','dod')]
    [string]$Endpoint = 'prod'
)

if ($PSVersionTable.PSEdition -ne 'Desktop') {
    throw "Run in Windows PowerShell 5.1 (Desktop edition). Current: $($PSVersionTable.PSEdition)."
}

if (-not (Test-Path $EvidencePath)) { New-Item -ItemType Directory -Path $EvidencePath | Out-Null }

$transcriptPath = Join-Path $EvidencePath "transcript-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"
Start-Transcript -Path $transcriptPath -Force | Out-Null

$evidence = [ordered]@{
    Control            = '1.1'
    RunUtc             = (Get-Date).ToUniversalTime().ToString('o')
    Operator           = "$env:USERDOMAIN\$env:USERNAME"
    Endpoint           = $Endpoint
    EnvironmentName    = $EnvironmentName
    SecurityGroupId    = $SecurityGroupId
    Actions            = @()
    Result             = 'UNKNOWN'
}

try {
    if ($Endpoint -eq 'prod') {
        Add-PowerAppsAccount
    } else {
        Add-PowerAppsAccount -Endpoint $Endpoint
    }

    Write-Host "Configuring Control 1.1 for environment: $EnvironmentName (endpoint: $Endpoint)" -ForegroundColor Cyan

    # Snapshot BEFORE any mutation
    $snapshotFile = Join-Path $EvidencePath "tenant-settings-before-$(Get-Date -Format 'yyyyMMdd-HHmmss').json"
    $beforeSettings = Get-TenantSettings
    $beforeSettings | ConvertTo-Json -Depth 20 | Out-File -FilePath $snapshotFile -Encoding UTF8
    $evidence.Actions += @{ Action = 'Snapshot'; File = $snapshotFile; Hash = (Get-FileHash $snapshotFile -Algorithm SHA256).Hash }

    # Detect Dataverse
    $env_obj = Get-AdminPowerAppEnvironment -EnvironmentName $EnvironmentName
    $isDataverse = $env_obj.CommonDataServiceDatabaseProvisioningState -eq 'Succeeded'
    $evidence.IsDataverseBacked = $isDataverse

    if ($isDataverse) {
        Write-Warning "Dataverse-backed environment - skipping legacy role-assignment cmdlets."
        $evidence.Actions += @{ Action = 'SkipDataverse'; Reason = 'Cmdlets do not apply to Dataverse environments. Use PPAC.' }
    } else {
        # Step 1: Remove Environment Maker from Tenant principal
        $envPermissions = Get-AdminPowerAppEnvironmentRoleAssignment -EnvironmentName $EnvironmentName
        $allUsersPermission = $envPermissions | Where-Object {
            $_.PrincipalType -eq "Tenant" -and $_.RoleName -eq "Environment Maker"
        }

        if ($allUsersPermission) {
            if ($PSCmdlet.ShouldProcess($EnvironmentName, "Remove Environment Maker from Tenant")) {
                Remove-AdminPowerAppEnvironmentRoleAssignment `
                    -EnvironmentName $EnvironmentName `
                    -RoleId $allUsersPermission.RoleId
                $evidence.Actions += @{ Action = 'RemoveTenantEnvMaker'; Result = 'OK' }
                Write-Host "  [DONE] Removed Environment Maker from All Users" -ForegroundColor Yellow
            }
        } else {
            $evidence.Actions += @{ Action = 'RemoveTenantEnvMaker'; Result = 'AlreadyClean' }
            Write-Host "  [SKIP] Tenant principal did not have Environment Maker role" -ForegroundColor Gray
        }

        # Step 2: Assign Environment Maker to authorized group
        if ($PSCmdlet.ShouldProcess($EnvironmentName, "Assign Environment Maker to group $SecurityGroupId")) {
            Set-AdminPowerAppEnvironmentRoleAssignment `
                -EnvironmentName $EnvironmentName `
                -PrincipalType Group `
                -PrincipalObjectId $SecurityGroupId `
                -RoleName EnvironmentMaker
            $evidence.Actions += @{ Action = 'AssignEnvMakerToGroup'; GroupId = $SecurityGroupId; Result = 'OK' }
            Write-Host "  [DONE] Assigned Environment Maker to security group" -ForegroundColor Green
        }
    }

    # Step 3: Tenant canvas-app sharing hygiene (NOT the primary 1.1 control - see note in playbook)
    if ($beforeSettings.disableShareWithEveryone -ne $true) {
        if ($PSCmdlet.ShouldProcess("Tenant", "Set disableShareWithEveryone = true")) {
            $beforeSettings.disableShareWithEveryone = $true
            Set-TenantSettings -RequestBody $beforeSettings
            $evidence.Actions += @{ Action = 'DisableShareWithEveryone'; Result = 'Changed' }
            Write-Host "  [DONE] Disabled Share with Everyone (canvas apps)" -ForegroundColor Green
        }
    } else {
        $evidence.Actions += @{ Action = 'DisableShareWithEveryone'; Result = 'AlreadyDisabled' }
    }

    $evidence.Result = 'PASS'
    Write-Host "`n[PASS] Control 1.1 configuration completed" -ForegroundColor Green
    $exitCode = 0
}
catch {
    $evidence.Result = 'FAIL'
    $evidence.Error  = $_.Exception.Message
    $evidence.Stack  = $_.ScriptStackTrace
    Write-Host "[FAIL] $($_.Exception.Message)" -ForegroundColor Red
    $exitCode = 1
}
finally {
    # Emit tamper-evident evidence
    $evidenceFile = Join-Path $EvidencePath "evidence-1.1-$(Get-Date -Format 'yyyyMMdd-HHmmss').json"
    $evidence | ConvertTo-Json -Depth 10 | Out-File -FilePath $evidenceFile -Encoding UTF8
    $hash = (Get-FileHash -Path $evidenceFile -Algorithm SHA256).Hash
    "$hash  $(Split-Path $evidenceFile -Leaf)" | Out-File -FilePath "$evidenceFile.sha256" -Encoding ASCII
    Write-Host "Evidence: $evidenceFile" -ForegroundColor Cyan
    Write-Host "  SHA-256: $hash" -ForegroundColor Cyan
    Stop-Transcript | Out-Null
    exit $exitCode
}
```

---

[Back to Control 1.1](../../../controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
