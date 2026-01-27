# PowerShell Setup: Control 1.1 - Restrict Agent Publishing by Authorization

**Last Updated:** January 2026
**Modules Required:** Microsoft.PowerApps.Administration.PowerShell

## Prerequisites

```powershell
# Install Power Platform Admin modules
Install-Module -Name Microsoft.PowerApps.Administration.PowerShell -Scope CurrentUser -Force

# Connect to Power Platform (interactive authentication)
Add-PowerAppsAccount

# For automated/unattended scenarios, use service principal authentication:
# $appId = "<Application-Client-ID>"
# $secret = "<Client-Secret>"
# $tenantId = "<Tenant-ID>"
# Add-PowerAppsAccount -ApplicationId $appId -ClientSecret $secret -TenantID $tenantId
```

---

## Configuration Script

### Get Current Environment Permissions

```powershell
# Get the environment
$EnvironmentName = "your-environment-id"

# Get current environment permissions
$envPermissions = Get-AdminPowerAppEnvironmentRoleAssignment -EnvironmentName $EnvironmentName
$envPermissions | Format-Table PrincipalDisplayName, RoleType, PrincipalType
```

### Remove Environment Maker Role from All Users

```powershell
# Remove Environment Maker role from "All Users" (if assigned)
$allUsersPermission = $envPermissions | Where-Object {
    $_.PrincipalType -eq "Tenant" -and $_.RoleType -eq "EnvironmentMaker"
}

if ($allUsersPermission) {
    Remove-AdminPowerAppEnvironmentRoleAssignment `
        -EnvironmentName $EnvironmentName `
        -RoleId $allUsersPermission.RoleId
    Write-Host "Removed Environment Maker role from All Users" -ForegroundColor Yellow
}
```

### Add Environment Maker Role to Authorized Security Group

```powershell
# Add Environment Maker role to authorized security group
$SecurityGroupId = "your-security-group-id"  # Get from Entra ID

Set-AdminPowerAppEnvironmentRoleAssignment `
    -EnvironmentName $EnvironmentName `
    -PrincipalType Group `
    -PrincipalObjectId $SecurityGroupId `
    -RoleName EnvironmentMaker

Write-Host "Environment Maker role assigned to authorized security group" -ForegroundColor Green
```

### Disable Share with Everyone

```powershell
# Prevent "Share with Everyone" capability
$settings = Get-TenantSettings
$settings.powerPlatform.powerApps.disableShareWithEveryone = $true
Set-TenantSettings -RequestBody $settings

Write-Host "Share with Everyone disabled" -ForegroundColor Green
```

---

## Validation Script

```powershell
# Validation: Check final role assignments
Write-Host "`n=== Environment Maker Role Assignments ===" -ForegroundColor Cyan
Get-AdminPowerAppEnvironmentRoleAssignment -EnvironmentName $EnvironmentName |
    Where-Object { $_.RoleType -eq "EnvironmentMaker" } |
    Format-Table PrincipalDisplayName, PrincipalType

# Verify no "All Users" assignment remains
$remainingAllUsers = Get-AdminPowerAppEnvironmentRoleAssignment -EnvironmentName $EnvironmentName |
    Where-Object { $_.PrincipalType -eq "Tenant" -and $_.RoleType -eq "EnvironmentMaker" }

if ($remainingAllUsers) {
    Write-Host "WARNING: All Users still has Environment Maker role!" -ForegroundColor Red
} else {
    Write-Host "PASS: All Users does not have Environment Maker role" -ForegroundColor Green
}

# Check tenant settings
$settings = Get-TenantSettings
if ($settings.powerPlatform.powerApps.disableShareWithEveryone -eq $true) {
    Write-Host "PASS: Share with Everyone is disabled" -ForegroundColor Green
} else {
    Write-Host "WARNING: Share with Everyone is NOT disabled" -ForegroundColor Yellow
}
```

---

## Complete Configuration Script

```powershell
<#
.SYNOPSIS
    Configures Control 1.1 - Restrict Agent Publishing by Authorization

.DESCRIPTION
    This script restricts agent publishing by:
    1. Removing Environment Maker role from All Users
    2. Assigning Environment Maker role to authorized security groups
    3. Disabling Share with Everyone capability

.PARAMETER EnvironmentName
    The GUID of the target Power Platform environment

.PARAMETER SecurityGroupId
    The GUID of the authorized security group in Entra ID

.EXAMPLE
    .\Configure-Control-1.1.ps1 -EnvironmentName "abc123..." -SecurityGroupId "def456..."

.NOTES
    Last Updated: January 2026
    Related Control: Control 1.1 - Restrict Agent Publishing by Authorization
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$EnvironmentName,

    [Parameter(Mandatory=$true)]
    [string]$SecurityGroupId
)

try {
    # Connect to Power Platform
    Add-PowerAppsAccount

    Write-Host "Configuring Control 1.1 for environment: $EnvironmentName" -ForegroundColor Cyan

    # Step 1: Remove Environment Maker from All Users
    $envPermissions = Get-AdminPowerAppEnvironmentRoleAssignment -EnvironmentName $EnvironmentName
    $allUsersPermission = $envPermissions | Where-Object {
        $_.PrincipalType -eq "Tenant" -and $_.RoleType -eq "EnvironmentMaker"
    }

    if ($allUsersPermission) {
        Remove-AdminPowerAppEnvironmentRoleAssignment `
            -EnvironmentName $EnvironmentName `
            -RoleId $allUsersPermission.RoleId
        Write-Host "  [DONE] Removed Environment Maker from All Users" -ForegroundColor Yellow
    } else {
        Write-Host "  [SKIP] All Users did not have Environment Maker role" -ForegroundColor Gray
    }

    # Step 2: Assign Environment Maker to authorized group
    Set-AdminPowerAppEnvironmentRoleAssignment `
        -EnvironmentName $EnvironmentName `
        -PrincipalType Group `
        -PrincipalObjectId $SecurityGroupId `
        -RoleName EnvironmentMaker
    Write-Host "  [DONE] Assigned Environment Maker to security group" -ForegroundColor Green

    # Step 3: Disable Share with Everyone
    $settings = Get-TenantSettings
    $settings.powerPlatform.powerApps.disableShareWithEveryone = $true
    Set-TenantSettings -RequestBody $settings
    Write-Host "  [DONE] Disabled Share with Everyone" -ForegroundColor Green

    Write-Host "`n[PASS] Control 1.1 configuration completed successfully" -ForegroundColor Green
}
catch {
    Write-Host "[FAIL] Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "[INFO] Stack trace: $($_.ScriptStackTrace)" -ForegroundColor Yellow
    exit 1
}
```

---

[Back to Control 1.1](../../../controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
