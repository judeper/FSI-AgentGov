# PowerShell Setup: Control 1.18 - Application-Level Authorization and RBAC

!!! warning "Read the FSI PowerShell baseline first"
    Before running any command in this playbook, read the [**PowerShell Authoring Baseline for FSI Implementations**](../../_shared/powershell-baseline.md). It is the canonical source for module version pinning, sovereign-cloud (GCC / GCC High / DoD) endpoints, mutation safety (`-WhatIf` / `SupportsShouldProcess`), Dataverse compatibility, and SHA-256 evidence emission. Snippets below may show abbreviated patterns; the baseline is authoritative.

**Last Updated:** April 2026
**Modules Required:** Microsoft.Graph, Microsoft.PowerApps.Administration.PowerShell

!!! danger "Implementation gap — PowerShell-only configuration cannot complete this control"
    The scripts on this page **bootstrap and inventory** Control 1.18 only — they create the Entra security groups and emit role-assignment evidence. They do **not** create Dataverse custom security roles, assign groups to environment or Dataverse roles, configure PIM-for-Groups, configure column-level security, or schedule access reviews. Those steps require the Power Platform Admin Center (Dataverse Security Roles) and the Entra ID Governance experience — see the [Portal Walkthrough](portal-walkthrough.md) for the full procedure. Running the scripts on this page **alone** does **not** satisfy Control 1.18; the evidence will show the bootstrap is complete but RBAC is not yet enforced.

!!! warning "Dataverse compatibility limitation"
    The cmdlet family `Get/Set/Remove-AdminPowerAppEnvironmentRoleAssignment` per [Microsoft Learn](https://learn.microsoft.com/en-us/powershell/module/microsoft.powerapps.administration.powershell/get-adminpowerappenvironmentroleassignment) only functions on environments **without** a Common Data Service / Dataverse database. Copilot Studio environments are Dataverse-backed by definition, so on those environments `Get-` returns empty (no error) and `Set-/Remove-` returns 403. The scripts below detect Dataverse and refuse to run; for Dataverse environments use the Dataverse Web API or PPAC Dataverse Security Roles (see Portal Walkthrough).

## Prerequisites

```powershell
# Replace <version> with the version approved by your CAB.
# See ../../_shared/powershell-baseline.md for current pinning recommendations.
Install-Module -Name Microsoft.Graph `
    -RequiredVersion '<version>' `
    -Repository PSGallery `
    -Scope CurrentUser `
    -AllowClobber `
    -AcceptLicense

Install-Module -Name Microsoft.PowerApps.Administration.PowerShell `
    -RequiredVersion '<version>' `
    -Repository PSGallery `
    -Scope CurrentUser `
    -AllowClobber `
    -AcceptLicense
```

**Operator role required:** the configuration script requires the **Groups Administrator** Entra role (for `New-MgGroup`); the export and validation scripts only require **Group.Read.All** Graph scope. Use a separation-of-duties pattern: the operator who runs the configuration script must **not** be the operator who attests its output.

**PowerShell edition:** `Microsoft.PowerApps.Administration.PowerShell` is .NET Framework only. **Use Windows PowerShell 5.1 (Desktop edition) — not PowerShell 7+.** The scripts below enforce this.

**Service principal authentication:** for unattended runs, use **certificate-based** auth (`-CertificateThumbprint`) sourced from `CurrentUser\My` or, preferably, from Azure Key Vault via `Get-AzKeyVaultCertificate`. Do **not** embed a client secret in scripts or pipelines — it fails secrets-management scans and creates an FSI examination finding.

```powershell
# Recommended SPN auth pattern (replace placeholders with values from your CAB-approved cert)
# Add-PowerAppsAccount -ApplicationId $appId -CertificateThumbprint $thumbprint -TenantID $tenantId
```

---

## Automated Scripts

### Export Security Role Assignments

```powershell
#Requires -PSEdition Desktop
#Requires -Version 5.1

<#
.SYNOPSIS
    Exports environment role assignments for compliance audit on NON-Dataverse environments.
    Refuses to run on Dataverse-backed environments (use Dataverse Web API instead).

.PARAMETER EnvironmentId
    The GUID of the target Power Platform environment.

.PARAMETER OutputPath
    Folder for evidence output (default: current directory).

.PARAMETER Cloud
    Sovereign cloud for FSI tenants regulated by OCC/Fed in GCC, GCC High, or DoD.

.EXAMPLE
    .\Export-SecurityRoles.ps1 -EnvironmentId "env-guid" -OutputPath ".\evidence" -Cloud Commercial
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)] [string]$EnvironmentId,
    [string]$OutputPath = ".",
    [ValidateSet('Commercial','USGov','USGovHigh','DoD','China')]
    [string]$Cloud = 'Commercial'
)

$ErrorActionPreference = 'Stop'
$ts = Get-Date -Format 'yyyyMMddTHHmmssZ'
New-Item -ItemType Directory -Force -Path $OutputPath | Out-Null
Start-Transcript -Path (Join-Path $OutputPath "transcript-export-$ts.log") -IncludeInvocationHeader

# Module versions for evidence
Get-Module Microsoft.PowerApps.Administration.PowerShell -ListAvailable |
    Select-Object Name, Version | Format-Table | Out-String | Write-Host

$endpointMap = @{ Commercial='prod'; USGov='usgov'; USGovHigh='usgovhigh'; DoD='dod'; China='china' }
Add-PowerAppsAccount -Endpoint $endpointMap[$Cloud]

# Refuse to run on Dataverse — Get-AdminPowerAppEnvironmentRoleAssignment returns empty silently.
$env = Get-AdminPowerAppEnvironment -EnvironmentName $EnvironmentId
if ($env.CommonDataServiceDatabaseType -and $env.CommonDataServiceDatabaseType -ne 'none') {
    Stop-Transcript
    throw "Environment $EnvironmentId is Dataverse-backed. Get-AdminPowerAppEnvironmentRoleAssignment does not return roles for Dataverse environments. Use the Dataverse Web API (/api/data/v9.2/systemusers?`$expand=systemuserroles_association) or PPAC Dataverse Security Roles. See Portal Walkthrough."
}

$users = Get-AdminPowerAppEnvironmentRoleAssignment -EnvironmentName $EnvironmentId

if (-not $users) {
    Write-Warning "No role assignments returned. Verify the operator has Power Platform Admin and the environment is non-Dataverse."
}

# Note: cmdlet exposes RoleName (with spaces) — NOT RoleType.
$export = $users | ForEach-Object {
    [PSCustomObject]@{
        PrincipalDisplayName = $_.PrincipalDisplayName
        PrincipalEmail       = $_.PrincipalEmail
        PrincipalType        = $_.PrincipalType
        RoleName             = $_.RoleName
        RoleId               = $_.RoleId
        EnvironmentName      = $_.EnvironmentName
        ExportUtc            = $ts
    }
}

$csvPath = Join-Path $OutputPath "RoleAssignments-$ts.csv"
$export | Export-Csv -Path $csvPath -NoTypeInformation -Encoding UTF8

# SHA-256 evidence sidecar
$hash = (Get-FileHash -Path $csvPath -Algorithm SHA256).Hash
"$hash *$(Split-Path $csvPath -Leaf)" | Set-Content -Path "$csvPath.sha256"

Write-Host "Export saved: $csvPath" -ForegroundColor Green
Write-Host "SHA-256: $hash" -ForegroundColor Green
Stop-Transcript
```

### Create Security Groups

```powershell
#Requires -PSEdition Desktop
#Requires -Version 5.1

<#
.SYNOPSIS
    Creates the four FSI Copilot Studio security groups for a target environment.

.EXAMPLE
    .\New-FSISecurityGroups.ps1 -Environment "Prod" -WhatIf
#>
[CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
param(
    [Parameter(Mandatory=$true)] [string]$Environment,
    [string]$EvidencePath = ".\evidence"
)

$ErrorActionPreference = 'Stop'
$ts = Get-Date -Format 'yyyyMMddTHHmmssZ'
New-Item -ItemType Directory -Force -Path $EvidencePath | Out-Null
Start-Transcript -Path (Join-Path $EvidencePath "transcript-newgroups-$ts.log") -IncludeInvocationHeader

Connect-MgGraph -Scopes "Group.ReadWrite.All" -NoWelcome

$groups = @(
    @{Name="SG-PowerPlatform-Admins-$Environment";   Description="Power Platform Administrators for $Environment"},
    @{Name="SG-CopilotStudio-Makers-$Environment";   Description="Copilot Studio agent creators for $Environment"},
    @{Name="SG-CopilotStudio-Viewers-$Environment";  Description="Copilot Studio read-only users for $Environment"},
    @{Name="SG-CopilotStudio-Testers-$Environment";  Description="Copilot Studio testers for $Environment"}
)

$results = @()
foreach ($group in $groups) {
    # Exact-name match only — startsWith would false-PASS on stale groups (e.g., -Dev-OLD).
    $existing = Get-MgGroup -Filter "displayName eq '$($group.Name)'" -ConsistencyLevel eventual -CountVariable cnt
    if ($cnt -gt 1) {
        throw "Ambiguous: $cnt groups already named $($group.Name). Resolve before continuing."
    }
    if ($existing) {
        Write-Host "[EXISTS] $($group.Name)" -ForegroundColor Yellow
        $results += [PSCustomObject]@{ Name=$group.Name; Action='exists'; Id=$existing.Id }
        continue
    }
    if ($PSCmdlet.ShouldProcess($group.Name, "Create Entra security group")) {
        $nick = ($group.Name -replace '[^A-Za-z0-9]','') + (Get-Random -Maximum 9999)
        $newGroup = New-MgGroup -DisplayName $group.Name `
            -Description $group.Description `
            -MailEnabled:$false `
            -SecurityEnabled:$true `
            -MailNickname $nick
        Write-Host "[CREATED] $($group.Name)" -ForegroundColor Green
        $results += [PSCustomObject]@{ Name=$group.Name; Action='created'; Id=$newGroup.Id }
    }
}

# Evidence emit
$jsonPath = Join-Path $EvidencePath "GroupCreation-$ts.json"
$results | ConvertTo-Json -Depth 5 | Set-Content -Path $jsonPath -Encoding UTF8
$hash = (Get-FileHash -Path $jsonPath -Algorithm SHA256).Hash
"$hash *$(Split-Path $jsonPath -Leaf)" | Set-Content "$jsonPath.sha256"

Disconnect-MgGraph | Out-Null
Stop-Transcript
```

---

## Validation Script

```powershell
#Requires -PSEdition Desktop
#Requires -Version 5.1

<#
.SYNOPSIS
    Validates that Control 1.18 BOOTSTRAP is in place: groups exist with correct
    names, environment is non-Dataverse (or routes operator to Dataverse path),
    and PIM eligibility is queried for the privileged group.

    NOTE: This validation does NOT confirm Dataverse role assignment, group→role
    mapping, column-level security, or access-review configuration. Those require
    portal-based verification and Dataverse Web API queries — see Verification & Testing.

.EXAMPLE
    .\Validate-Control-1.18.ps1 -EnvironmentId "env-guid" -EnvironmentSuffix "Prod"
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)] [string]$EnvironmentId,
    [Parameter(Mandatory=$true)] [string]$EnvironmentSuffix,
    [ValidateSet('Commercial','USGov','USGovHigh','DoD','China')]
    [string]$Cloud = 'Commercial'
)

$ErrorActionPreference = 'Stop'
$endpointMap = @{ Commercial='prod'; USGov='usgov'; USGovHigh='usgovhigh'; DoD='dod'; China='china' }
$mgEnvMap    = @{ Commercial='Global'; USGov='USGov'; USGovHigh='USGovDoD'; DoD='USGovDoD'; China='China' }

Add-PowerAppsAccount -Endpoint $endpointMap[$Cloud]
Connect-MgGraph -Scopes @("Group.Read.All","RoleManagement.Read.Directory","PrivilegedAccess.Read.AzureADGroup") `
    -Environment $mgEnvMap[$Cloud] -NoWelcome

$pass = $true

# Check 1: Exact-name security group existence
Write-Host "`n[Check 1] Security Groups (exact match)" -ForegroundColor Cyan
$required = @(
    "SG-PowerPlatform-Admins-$EnvironmentSuffix",
    "SG-CopilotStudio-Makers-$EnvironmentSuffix",
    "SG-CopilotStudio-Viewers-$EnvironmentSuffix",
    "SG-CopilotStudio-Testers-$EnvironmentSuffix"
)
foreach ($name in $required) {
    $g = Get-MgGroup -Filter "displayName eq '$name'" -ConsistencyLevel eventual -CountVariable c
    if ($c -eq 1) {
        Write-Host "  [PASS] $name ($($g.Id))" -ForegroundColor Green
    } else {
        Write-Host "  [FAIL] $name (matched $c groups)" -ForegroundColor Red
        $pass = $false
    }
}

# Check 2: Environment Dataverse status — if Dataverse, environment-role check is N/A
Write-Host "`n[Check 2] Environment / Role Assignments" -ForegroundColor Cyan
$env = Get-AdminPowerAppEnvironment -EnvironmentName $EnvironmentId
if ($env.CommonDataServiceDatabaseType -and $env.CommonDataServiceDatabaseType -ne 'none') {
    Write-Host "  [INFO] Dataverse environment — environment-role cmdlet N/A. Verify Dataverse Security Role assignments via Portal Walkthrough." -ForegroundColor Yellow
} else {
    $roles = Get-AdminPowerAppEnvironmentRoleAssignment -EnvironmentName $EnvironmentId
    Write-Host "  Total assignments: $($roles.Count)"
    $roles | Group-Object RoleName | ForEach-Object {
        Write-Host "    $($_.Name): $($_.Count)"
    }
}

# Check 3: PIM-for-Groups eligibility for the Admins group (graph query — not a print stub)
Write-Host "`n[Check 3] PIM-for-Groups eligibility" -ForegroundColor Cyan
$adminGroup = Get-MgGroup -Filter "displayName eq 'SG-PowerPlatform-Admins-$EnvironmentSuffix'" -ConsistencyLevel eventual -CountVariable c
if ($c -eq 1) {
    try {
        $eligible = Get-MgIdentityGovernancePrivilegedAccessGroupEligibilityScheduleInstance `
            -Filter "groupId eq '$($adminGroup.Id)'" -ErrorAction Stop
        if ($eligible) {
            Write-Host "  [PASS] PIM-for-Groups eligible assignments: $($eligible.Count)" -ForegroundColor Green
        } else {
            Write-Host "  [WARN] No eligible PIM assignments found. Configure PIM-for-Groups for the Admins group before declaring Control 1.18 in scope for production." -ForegroundColor Yellow
            $pass = $false
        }
    } catch {
        Write-Host "  [WARN] PIM-for-Groups query failed: $($_.Exception.Message). May indicate insufficient license (Entra ID P2) or missing scope." -ForegroundColor Yellow
    }
} else {
    Write-Host "  [SKIP] Admins group not found." -ForegroundColor Gray
}

Disconnect-MgGraph | Out-Null
Write-Host "`n=== Bootstrap Validation $(if ($pass) {'PASSED'} else {'FAILED — see above'}) ===" -ForegroundColor (if ($pass) {'Green'} else {'Red'})
if (-not $pass) { exit 1 }
```

---

## Bootstrap Script (Configuration is **NOT** complete after this script)

```powershell
#Requires -PSEdition Desktop
#Requires -Version 5.1

<#
.SYNOPSIS
    Bootstraps Control 1.18 — creates Entra security groups and exports the
    starting-state role-assignment inventory. Does NOT complete the control.

.DESCRIPTION
    This script:
      1. Creates the four FSI Entra security groups for a target environment.
      2. Exports the starting-state environment role assignment inventory
         (or, on Dataverse, halts and routes the operator to the portal path).
      3. Validates that the four groups now exist.
      4. Emits SHA-256 evidence for both the role inventory and the group manifest.

    This script does NOT:
      - Create the FSI Dataverse custom security roles
        (FSI - Agent Publisher / Viewer / Tester) — use PPAC.
      - Assign environment or Dataverse roles to the new groups — use PPAC.
      - Configure PIM-for-Groups on the Admins group — use Entra ID Governance.
      - Configure Dataverse column-level security on PII columns — use PPAC.
      - Schedule access reviews — use Entra ID Governance.

    See Portal Walkthrough for the remaining steps required to complete Control 1.18.

.EXAMPLE
    .\Bootstrap-Control-1.18.ps1 -EnvironmentId "env-guid" -EnvironmentSuffix "Prod" -WhatIf
#>
[CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
param(
    [Parameter(Mandatory=$true)] [string]$EnvironmentId,
    [Parameter(Mandatory=$true)] [string]$EnvironmentSuffix,
    [string]$EvidencePath = ".\evidence",
    [ValidateSet('Commercial','USGov','USGovHigh','DoD','China')]
    [string]$Cloud = 'Commercial'
)

$ErrorActionPreference = 'Stop'
$ts = Get-Date -Format 'yyyyMMddTHHmmssZ'
New-Item -ItemType Directory -Force -Path $EvidencePath | Out-Null
Start-Transcript -Path (Join-Path $EvidencePath "transcript-bootstrap-$ts.log") -IncludeInvocationHeader

$endpointMap = @{ Commercial='prod'; USGov='usgov'; USGovHigh='usgovhigh'; DoD='dod'; China='china' }
$mgEnvMap    = @{ Commercial='Global'; USGov='USGov'; USGovHigh='USGovDoD'; DoD='USGovDoD'; China='China' }

try {
    Connect-MgGraph -Scopes "Group.ReadWrite.All" -Environment $mgEnvMap[$Cloud] -NoWelcome
    Add-PowerAppsAccount -Endpoint $endpointMap[$Cloud]

    # Step 1: Refuse to mutate Dataverse-backed environments via the legacy cmdlets.
    $env = Get-AdminPowerAppEnvironment -EnvironmentName $EnvironmentId
    $isDataverse = $env.CommonDataServiceDatabaseType -and $env.CommonDataServiceDatabaseType -ne 'none'
    if ($isDataverse) {
        Write-Warning "Environment $EnvironmentId is Dataverse-backed. Group creation will proceed; role assignment must be done via PPAC Dataverse Security Roles. See Portal Walkthrough."
    }

    # Step 2: Create groups (per-group try/catch, idempotent, exact match)
    $groupSpecs = @(
        @{Name="SG-PowerPlatform-Admins-$EnvironmentSuffix";   Description="Power Platform Administrators for $EnvironmentSuffix"},
        @{Name="SG-CopilotStudio-Makers-$EnvironmentSuffix";   Description="Copilot Studio agent creators for $EnvironmentSuffix"},
        @{Name="SG-CopilotStudio-Viewers-$EnvironmentSuffix";  Description="Copilot Studio read-only users for $EnvironmentSuffix"},
        @{Name="SG-CopilotStudio-Testers-$EnvironmentSuffix";  Description="Copilot Studio testers for $EnvironmentSuffix"}
    )
    $manifest = @()
    foreach ($spec in $groupSpecs) {
        try {
            $existing = Get-MgGroup -Filter "displayName eq '$($spec.Name)'" -ConsistencyLevel eventual -CountVariable c
            if ($c -eq 1) {
                $manifest += [PSCustomObject]@{ Name=$spec.Name; Action='exists'; Id=$existing.Id }
                continue
            }
            if ($PSCmdlet.ShouldProcess($spec.Name, "Create Entra security group")) {
                $nick = ($spec.Name -replace '[^A-Za-z0-9]','') + (Get-Random -Maximum 9999)
                $g = New-MgGroup -DisplayName $spec.Name -Description $spec.Description `
                    -MailEnabled:$false -SecurityEnabled:$true -MailNickname $nick
                $manifest += [PSCustomObject]@{ Name=$spec.Name; Action='created'; Id=$g.Id }
            }
        } catch {
            $manifest += [PSCustomObject]@{ Name=$spec.Name; Action='error'; Error=$_.Exception.Message }
        }
    }

    # Step 3: Inventory role assignments (skip on Dataverse with explicit reason)
    if (-not $isDataverse) {
        $users = Get-AdminPowerAppEnvironmentRoleAssignment -EnvironmentName $EnvironmentId
        $roleExport = $users | ForEach-Object {
            [PSCustomObject]@{
                PrincipalDisplayName = $_.PrincipalDisplayName
                PrincipalEmail       = $_.PrincipalEmail
                PrincipalType        = $_.PrincipalType
                RoleName             = $_.RoleName
                RoleId               = $_.RoleId
                EnvironmentName      = $_.EnvironmentName
                ExportUtc            = $ts
            }
        }
        $roleFile = Join-Path $EvidencePath "RoleAssignments-$ts.csv"
        $roleExport | Export-Csv -Path $roleFile -NoTypeInformation -Encoding UTF8
        $hashRoles = (Get-FileHash -Path $roleFile -Algorithm SHA256).Hash
        "$hashRoles *$(Split-Path $roleFile -Leaf)" | Set-Content "$roleFile.sha256"
    } else {
        $roleFile = "(skipped: Dataverse environment — see Portal Walkthrough for Dataverse Security Role inventory)"
    }

    # Step 4: Emit group manifest with SHA-256
    $manifestPath = Join-Path $EvidencePath "GroupManifest-$ts.json"
    $manifest | ConvertTo-Json -Depth 5 | Set-Content -Path $manifestPath -Encoding UTF8
    $hashManifest = (Get-FileHash -Path $manifestPath -Algorithm SHA256).Hash
    "$hashManifest *$(Split-Path $manifestPath -Leaf)" | Set-Content "$manifestPath.sha256"

    Write-Host "`n=== Bootstrap complete ===" -ForegroundColor Cyan
    Write-Host "Group manifest: $manifestPath (SHA-256 $hashManifest)"
    Write-Host "Role inventory: $roleFile"
    if (-not $isDataverse) { Write-Host "Role inventory SHA-256: $hashRoles" }
    Write-Host "`n[ACTION REQUIRED] This script bootstrapped the groups only." -ForegroundColor Yellow
    Write-Host "  - Assign Dataverse Security Roles to the four groups via PPAC." -ForegroundColor Yellow
    Write-Host "  - Configure PIM-for-Groups on the Admins group via Entra ID Governance." -ForegroundColor Yellow
    Write-Host "  - Configure Dataverse column-level security and access reviews." -ForegroundColor Yellow
    Write-Host "  See Portal Walkthrough for the remaining procedure." -ForegroundColor Yellow
}
catch {
    Write-Host "[FAIL] $($_.Exception.Message)" -ForegroundColor Red
    Write-Host $_.ScriptStackTrace
    exit 1
}
finally {
    if (Get-MgContext) { Disconnect-MgGraph -ErrorAction SilentlyContinue | Out-Null }
    if (Get-Command Remove-PowerAppsAccount -ErrorAction SilentlyContinue) {
        Remove-PowerAppsAccount -ErrorAction SilentlyContinue | Out-Null
    }
    Stop-Transcript
}
```

---

[Back to Control 1.18](../../../controls/pillar-1-security/1.18-application-level-authorization-and-role-based-access-control-rbac.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
