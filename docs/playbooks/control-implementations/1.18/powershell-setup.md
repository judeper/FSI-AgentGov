# PowerShell Setup: Control 1.18 - Application-Level Authorization and RBAC

**Last Updated:** January 2026
**Modules Required:** Microsoft.Graph, Microsoft.PowerApps.Administration.PowerShell

## Prerequisites

```powershell
Install-Module -Name Microsoft.Graph -Force -Scope CurrentUser
Install-Module -Name Microsoft.PowerApps.Administration.PowerShell -Force -Scope CurrentUser
```

---

## Automated Scripts

### Export Security Role Assignments

```powershell
<#
.SYNOPSIS
    Exports security role assignments for compliance audit

.EXAMPLE
    .\Export-SecurityRoles.ps1 -EnvironmentId "env-guid"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$EnvironmentId,
    [string]$OutputPath = ".\SecurityRoleExport.csv"
)

Write-Host "=== Security Role Export ===" -ForegroundColor Cyan

Add-PowerAppsAccount

# Get environment users and roles
$users = Get-AdminPowerAppEnvironmentRoleAssignment -EnvironmentName $EnvironmentId

$export = @()
foreach ($user in $users) {
    $export += [PSCustomObject]@{
        PrincipalDisplayName = $user.PrincipalDisplayName
        PrincipalEmail = $user.PrincipalEmail
        PrincipalType = $user.PrincipalType
        RoleType = $user.RoleType
        EnvironmentName = $user.EnvironmentName
        ExportDate = Get-Date
    }
}

$export | Export-Csv -Path $OutputPath -NoTypeInformation
Write-Host "Export saved to: $OutputPath" -ForegroundColor Green
```

### Create Security Groups

```powershell
<#
.SYNOPSIS
    Creates FSI security groups for Copilot Studio access

.EXAMPLE
    .\New-FSISecurityGroups.ps1 -Environment "Prod"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$Environment
)

Write-Host "=== Create FSI Security Groups ===" -ForegroundColor Cyan

Connect-MgGraph -Scopes "Group.ReadWrite.All"

$groups = @(
    @{Name="SG-PowerPlatform-Admins-$Environment"; Description="Power Platform Administrators for $Environment"},
    @{Name="SG-CopilotStudio-Makers-$Environment"; Description="Copilot Studio agent creators for $Environment"},
    @{Name="SG-CopilotStudio-Viewers-$Environment"; Description="Copilot Studio read-only users for $Environment"},
    @{Name="SG-CopilotStudio-Testers-$Environment"; Description="Copilot Studio testers for $Environment"}
)

foreach ($group in $groups) {
    $existing = Get-MgGroup -Filter "displayName eq '$($group.Name)'"
    if ($existing) {
        Write-Host "Group already exists: $($group.Name)" -ForegroundColor Yellow
    } else {
        $newGroup = New-MgGroup -DisplayName $group.Name `
            -Description $group.Description `
            -MailEnabled:$false `
            -SecurityEnabled:$true `
            -MailNickname $group.Name.Replace("-","")

        Write-Host "Created: $($group.Name)" -ForegroundColor Green
    }
}

Disconnect-MgGraph
```

---

## Validation Script

```powershell
<#
.SYNOPSIS
    Validates Control 1.18 - RBAC configuration

.EXAMPLE
    .\Validate-Control-1.18.ps1 -EnvironmentId "env-guid"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$EnvironmentId
)

Write-Host "=== Control 1.18 Validation ===" -ForegroundColor Cyan

Add-PowerAppsAccount
Connect-MgGraph -Scopes "Group.Read.All"

# Check 1: Security groups exist
Write-Host "`n[Check 1] Security Groups" -ForegroundColor Cyan
$requiredGroups = @("SG-PowerPlatform-Admins", "SG-CopilotStudio-Makers", "SG-CopilotStudio-Viewers")
foreach ($groupName in $requiredGroups) {
    $group = Get-MgGroup -Filter "startsWith(displayName,'$groupName')"
    if ($group) {
        Write-Host "[PASS] Found: $($group.DisplayName)" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] Missing: $groupName" -ForegroundColor Red
    }
}

# Check 2: Role assignments
Write-Host "`n[Check 2] Environment Role Assignments" -ForegroundColor Cyan
$roles = Get-AdminPowerAppEnvironmentRoleAssignment -EnvironmentName $EnvironmentId
Write-Host "Total assignments: $($roles.Count)"

# Check 3: PIM (manual)
Write-Host "`n[Check 3] PIM Configuration" -ForegroundColor Cyan
Write-Host "[INFO] Verify PIM is configured in Entra admin center"

Disconnect-MgGraph

Write-Host "`n=== Validation Complete ===" -ForegroundColor Cyan
```

---

[Back to Control 1.18](../../../controls/pillar-1-security/1.18-application-level-authorization-and-role-based-access-control-rbac.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
