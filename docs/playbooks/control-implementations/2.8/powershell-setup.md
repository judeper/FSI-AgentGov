# PowerShell Setup: Control 2.8 — Access Control and Segregation of Duties

!!! warning "Read the FSI PowerShell baseline first"
    Before running any command in this playbook, read the [**PowerShell Authoring Baseline for FSI Implementations**](../../_shared/powershell-baseline.md). It is the canonical source for module version pinning, sovereign-cloud (GCC / GCC High / DoD) endpoints, mutation safety (`-WhatIf` / `SupportsShouldProcess`), Dataverse compatibility, and SHA-256 evidence emission. Snippets below show abbreviated patterns; the baseline is authoritative.

**Last Updated:** April 2026
**Modules Required:** `Microsoft.Graph` (v2.x, pinned), `Microsoft.PowerApps.Administration.PowerShell` (Windows PowerShell 5.1 only)
**Audience:** M365 administrators in US financial services
**Mutation safety:** All scripts below support `-WhatIf` via `SupportsShouldProcess`; run with `-WhatIf` first in regulated tenants.

---

## Prerequisites

```powershell
# Pin to the version approved by your CAB (replace <version>):
Install-Module -Name Microsoft.Graph `
    -RequiredVersion '<version>' -Repository PSGallery `
    -Scope CurrentUser -AllowClobber -AcceptLicense

# Power Apps Administration is Windows PowerShell 5.1 (Desktop) only:
if ($PSVersionTable.PSEdition -ne 'Desktop') {
    Write-Warning "Run Power Apps Administration cmdlets from Windows PowerShell 5.1."
}
Install-Module -Name Microsoft.PowerApps.Administration.PowerShell `
    -RequiredVersion '<version>' -Scope CurrentUser -AllowClobber
```

**Required Graph scopes (delegated):**

| Script | Scopes |
|---|---|
| Group creation | `Group.ReadWrite.All`, `Directory.ReadWrite.All`, `RoleManagement.ReadWrite.Directory` |
| Membership / SoD audit | `Group.Read.All`, `User.Read.All`, `RoleManagement.Read.Directory` |
| PIM eligibility audit | `RoleManagementPolicy.Read.Directory`, `PrivilegedAccess.Read.AzureADGroup` |

> **Sovereign cloud note:** GCC / GCC High / DoD tenants must pass `-Environment USGov` / `USGovHigh` / `USGovDoD` to `Connect-MgGraph` and the equivalent endpoint to `Add-PowerAppsAccount`. See the baseline.

---

## Script 1 — Create role-assignable security groups

```powershell
<#
.SYNOPSIS
    Creates the five SG-Agent-* security groups for Control 2.8.
    Marks Approvers / Release Managers / Platform Admins as role-assignable.
.NOTES
    Run with -WhatIf first. Idempotent: skips groups that already exist.
#>
[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'High')]
param(
    [string]$EvidencePath = ".\evidence\2.8"
)

Connect-MgGraph -Scopes "Group.ReadWrite.All","Directory.ReadWrite.All","RoleManagement.ReadWrite.Directory" -NoWelcome

$null = New-Item -ItemType Directory -Path $EvidencePath -Force

$groups = @(
    @{ DisplayName = "SG-Agent-Developers";      MailNickname = "sg-agent-developers";      RoleAssignable = $false; Description = "Copilot Studio authoring identities (makers)" }
    @{ DisplayName = "SG-Agent-Reviewers";       MailNickname = "sg-agent-reviewers";       RoleAssignable = $false; Description = "Independent reviewers of agent submissions" }
    @{ DisplayName = "SG-Agent-Approvers";       MailNickname = "sg-agent-approvers";       RoleAssignable = $true;  Description = "PIM-gated approvers for production publish" }
    @{ DisplayName = "SG-Agent-ReleaseManagers"; MailNickname = "sg-agent-releasemgrs";     RoleAssignable = $true;  Description = "PIM-gated release managers (Zone 3 deploy)" }
    @{ DisplayName = "SG-Agent-PlatformAdmins";  MailNickname = "sg-agent-platformadmins";  RoleAssignable = $true;  Description = "PIM-eligible Power Platform / Environment admins" }
)

$report = foreach ($g in $groups) {
    $existing = Get-MgGroup -Filter "displayName eq '$($g.DisplayName)'" -ErrorAction SilentlyContinue
    if ($existing) {
        [PSCustomObject]@{ Group = $g.DisplayName; Action = "Exists"; Id = $existing.Id; RoleAssignable = $existing.IsAssignableToRole }
    }
    elseif ($PSCmdlet.ShouldProcess($g.DisplayName, "Create security group (RoleAssignable=$($g.RoleAssignable))")) {
        $params = @{
            DisplayName        = $g.DisplayName
            Description        = $g.Description
            MailNickname       = $g.MailNickname
            MailEnabled        = $false
            SecurityEnabled    = $true
            IsAssignableToRole = $g.RoleAssignable
        }
        $new = New-MgGroup @params
        [PSCustomObject]@{ Group = $g.DisplayName; Action = "Created"; Id = $new.Id; RoleAssignable = $new.IsAssignableToRole }
    }
}

$reportPath = Join-Path $EvidencePath "groups-$(Get-Date -Format 'yyyyMMdd-HHmm').csv"
$report | Export-Csv -Path $reportPath -NoTypeInformation

# SHA-256 evidence hash (per baseline)
$hash = (Get-FileHash -Path $reportPath -Algorithm SHA256).Hash
"$reportPath,$hash" | Out-File (Join-Path $EvidencePath "evidence-hashes.txt") -Append

Disconnect-MgGraph
```

---

## Script 2 — Segregation-of-Duties detector

Detects identities that hold conflicting role pairs. Output is the canonical evidence artefact for examiners.

```powershell
<#
.SYNOPSIS
    Detects SoD violations across the five agent governance groups
    AND across PIM-eligible / Active assignments to high-privileged roles.
.OUTPUTS
    CSV: SoD-Violations-yyyyMMdd-HHmm.csv with one row per (User, ConflictPair).
.EXAMPLE
    .\Test-Control28-SoD.ps1 -EvidencePath .\evidence\2.8
#>
[CmdletBinding()]
param(
    [string]$EvidencePath = ".\evidence\2.8",
    [switch]$IncludePIMEligible
)

Connect-MgGraph -Scopes "Group.Read.All","User.Read.All","RoleManagement.Read.Directory" -NoWelcome
$null = New-Item -ItemType Directory -Path $EvidencePath -Force

# Conflict matrix — anchored to NIST AC-5 / SOX 404 SoD principles
$conflictPairs = @(
    @{ A = "SG-Agent-Developers";  B = "SG-Agent-Approvers";       Rule = "Maker cannot approve own work (FINRA 3110, SOX 404)" }
    @{ A = "SG-Agent-Developers";  B = "SG-Agent-ReleaseManagers"; Rule = "Maker cannot deploy to production (SOX 404)" }
    @{ A = "SG-Agent-Approvers";   B = "SG-Agent-ReleaseManagers"; Rule = "Approver cannot self-deploy (NIST AC-5)" }
    @{ A = "SG-Agent-Reviewers";   B = "SG-Agent-Approvers";       Rule = "Reviewer should not also approve (independent review)" }
    @{ A = "SG-Agent-Developers";  B = "SG-Agent-PlatformAdmins";  Rule = "Maker cannot hold platform admin (Copilot Studio author/admin separation)" }
)

function Get-GroupMemberSet {
    param([string]$Name)
    $g = Get-MgGroup -Filter "displayName eq '$Name'" -ErrorAction SilentlyContinue
    if (-not $g) { return @{} }
    $members = Get-MgGroupTransitiveMember -GroupId $g.Id -All -ErrorAction SilentlyContinue
    $set = @{}
    foreach ($m in $members) {
        if ($m.AdditionalProperties['@odata.type'] -eq '#microsoft.graph.user') {
            $set[$m.Id] = $m.AdditionalProperties.userPrincipalName
        }
    }
    return $set
}

$violations = New-Object System.Collections.Generic.List[object]

foreach ($p in $conflictPairs) {
    $setA = Get-GroupMemberSet $p.A
    $setB = Get-GroupMemberSet $p.B
    $overlap = $setA.Keys | Where-Object { $setB.ContainsKey($_) }
    foreach ($id in $overlap) {
        $violations.Add([PSCustomObject]@{
            UserId            = $id
            UserPrincipalName = $setA[$id]
            GroupA            = $p.A
            GroupB            = $p.B
            Rule              = $p.Rule
            DetectedAtUtc     = (Get-Date).ToUniversalTime().ToString("o")
        })
    }
}

# Optional: cross-check directory-role overlaps (Maker vs Power Platform Admin via PIM)
if ($IncludePIMEligible) {
    $ppaRole = Get-MgRoleManagementDirectoryRoleDefinition -Filter "displayName eq 'Power Platform Administrator'"
    if ($ppaRole) {
        $eligible = Get-MgRoleManagementDirectoryRoleEligibilityScheduleInstance -Filter "roleDefinitionId eq '$($ppaRole.Id)'" -All
        $devSet = Get-GroupMemberSet "SG-Agent-Developers"
        foreach ($e in $eligible) {
            if ($devSet.ContainsKey($e.PrincipalId)) {
                $violations.Add([PSCustomObject]@{
                    UserId            = $e.PrincipalId
                    UserPrincipalName = $devSet[$e.PrincipalId]
                    GroupA            = "SG-Agent-Developers"
                    GroupB            = "Power Platform Administrator (PIM-eligible)"
                    Rule              = "Maker cannot be eligible for Power Platform Admin (Zone 3)"
                    DetectedAtUtc     = (Get-Date).ToUniversalTime().ToString("o")
                })
            }
        }
    }
}

$ts = Get-Date -Format 'yyyyMMdd-HHmm'
$out = Join-Path $EvidencePath "SoD-Violations-$ts.csv"
$violations | Export-Csv -Path $out -NoTypeInformation

if ($violations.Count -eq 0) {
    Write-Host "[PASS] No SoD violations detected." -ForegroundColor Green
} else {
    Write-Host "[FAIL] $($violations.Count) SoD violation(s) detected. See $out" -ForegroundColor Red
}

# Evidence hash
$hash = (Get-FileHash -Path $out -Algorithm SHA256).Hash
"$out,$hash" | Out-File (Join-Path $EvidencePath "evidence-hashes.txt") -Append

Disconnect-MgGraph
exit ([int]($violations.Count -gt 0))
```

> The exit code is non-zero when violations exist — wire this script into your monthly governance pipeline (Azure DevOps, GitHub Actions, or Power Automate Desktop) and treat a failed run as a Sev-2 control incident.

---

## Script 3 — Membership and PIM eligibility export

```powershell
<#
.SYNOPSIS
    Exports (a) members of each SG-Agent-* group and (b) PIM-eligible
    members of high-privileged directory roles. Used as quarterly
    access-review evidence.
#>
[CmdletBinding()]
param([string]$EvidencePath = ".\evidence\2.8")

Connect-MgGraph -Scopes "Group.Read.All","User.Read.All","RoleManagement.Read.Directory" -NoWelcome
$null = New-Item -ItemType Directory -Path $EvidencePath -Force
$ts = Get-Date -Format 'yyyyMMdd-HHmm'

# (a) Group memberships
$groupNames = "SG-Agent-Developers","SG-Agent-Reviewers","SG-Agent-Approvers","SG-Agent-ReleaseManagers","SG-Agent-PlatformAdmins"
$rows = foreach ($name in $groupNames) {
    $g = Get-MgGroup -Filter "displayName eq '$name'" -ErrorAction SilentlyContinue
    if (-not $g) { continue }
    Get-MgGroupTransitiveMember -GroupId $g.Id -All | ForEach-Object {
        [PSCustomObject]@{
            Group             = $name
            UserPrincipalName = $_.AdditionalProperties.userPrincipalName
            DisplayName       = $_.AdditionalProperties.displayName
            JobTitle          = $_.AdditionalProperties.jobTitle
            AccountEnabled    = $_.AdditionalProperties.accountEnabled
        }
    }
}
$rows | Export-Csv (Join-Path $EvidencePath "Membership-$ts.csv") -NoTypeInformation

# (b) PIM-eligible holders of priority roles
$priorityRoles = "Power Platform Administrator","AI Administrator","Global Administrator","Privileged Role Administrator"
$pim = foreach ($rn in $priorityRoles) {
    $rd = Get-MgRoleManagementDirectoryRoleDefinition -Filter "displayName eq '$rn'" -ErrorAction SilentlyContinue
    if (-not $rd) { continue }
    $assigns = Get-MgRoleManagementDirectoryRoleEligibilityScheduleInstance `
                  -Filter "roleDefinitionId eq '$($rd.Id)'" -All
    foreach ($a in $assigns) {
        $u = Get-MgUser -UserId $a.PrincipalId -ErrorAction SilentlyContinue
        [PSCustomObject]@{
            Role              = $rn
            UserPrincipalName = $u.UserPrincipalName
            AssignmentType    = "Eligible"
            EndDateTime       = $a.EndDateTime
        }
    }
}
$pim | Export-Csv (Join-Path $EvidencePath "PIM-Eligible-$ts.csv") -NoTypeInformation

Disconnect-MgGraph
```

---

## Script 4 — Dataverse System Administrator audit (Zone 3)

Dataverse System Administrator is **outside** the Entra group model, so this check uses the Power Platform Admin module (Windows PowerShell 5.1).

```powershell
<#
.SYNOPSIS
    Lists every identity holding the Dataverse System Administrator
    role across all production-aligned environments.
.NOTES
    Requires Microsoft.PowerApps.Administration.PowerShell on PS 5.1.
#>
if ($PSVersionTable.PSEdition -ne 'Desktop') {
    throw "Run from Windows PowerShell 5.1 (Desktop edition)."
}
Add-PowerAppsAccount   # add -Endpoint usgov / usgovhigh / dod for sovereign clouds

$envs = Get-AdminPowerAppEnvironment | Where-Object { $_.EnvironmentType -in 'Production','Sandbox' }
$rows = foreach ($e in $envs) {
    $roles = Get-AdminPowerAppEnvironmentRoleAssignment -EnvironmentName $e.EnvironmentName -ErrorAction SilentlyContinue
    foreach ($r in $roles | Where-Object { $_.RoleName -eq 'EnvironmentAdmin' -or $_.RoleName -eq 'SystemAdministrator' }) {
        [PSCustomObject]@{
            Environment      = $e.DisplayName
            EnvironmentId    = $e.EnvironmentName
            EnvironmentType  = $e.EnvironmentType
            Role             = $r.RoleName
            PrincipalType    = $r.PrincipalType
            PrincipalEmail   = $r.PrincipalEmail
        }
    }
}
$rows | Export-Csv ".\evidence\2.8\Dataverse-SysAdmins-$(Get-Date -Format 'yyyyMMdd-HHmm').csv" -NoTypeInformation
```

> Any **standing** (non-PIM) System Administrator in a Zone 3 environment must be either (a) an approved break-glass identity in your runbook, or (b) treated as a Sev-2 SoD finding.

---

## Validation Script (Composite)

```powershell
<#
.SYNOPSIS
    Composite validation for Control 2.8. Returns 0 on full pass.
.EXAMPLE
    .\Validate-Control-2.8.ps1 -EvidencePath .\evidence\2.8
#>
param([string]$EvidencePath = ".\evidence\2.8")

$results = @()

# 1. Groups exist with correct role-assignable flag
Connect-MgGraph -Scopes "Group.Read.All" -NoWelcome
$expected = @{
    "SG-Agent-Developers"      = $false
    "SG-Agent-Reviewers"       = $false
    "SG-Agent-Approvers"       = $true
    "SG-Agent-ReleaseManagers" = $true
    "SG-Agent-PlatformAdmins"  = $true
}
foreach ($name in $expected.Keys) {
    $g = Get-MgGroup -Filter "displayName eq '$name'" -ErrorAction SilentlyContinue
    if (-not $g) {
        $results += [PSCustomObject]@{ Check = "Group $name exists"; Result = "FAIL"; Detail = "Not found" }
    } elseif ($g.IsAssignableToRole -ne $expected[$name]) {
        $results += [PSCustomObject]@{ Check = "Group $name role-assignable"; Result = "FAIL"; Detail = "Expected $($expected[$name]), found $($g.IsAssignableToRole)" }
    } else {
        $results += [PSCustomObject]@{ Check = "Group $name OK"; Result = "PASS"; Detail = "" }
    }
}

# 2. Run SoD detector (exit code 0 = pass)
& (Join-Path $PSScriptRoot 'Test-Control28-SoD.ps1') -EvidencePath $EvidencePath -IncludePIMEligible | Out-Null
$results += [PSCustomObject]@{ Check = "SoD detector"; Result = ($(if ($LASTEXITCODE -eq 0){"PASS"}else{"FAIL"})); Detail = "Exit $LASTEXITCODE" }

# 3. Reminder-only checks (manual verification)
$results += [PSCustomObject]@{ Check = "Access Reviews scheduled"; Result = "MANUAL"; Detail = "Verify in Entra Identity Governance portal" }
$results += [PSCustomObject]@{ Check = "PIM for Groups onboarded"; Result = "MANUAL"; Detail = "Verify in PIM → Groups blade" }

$results | Format-Table -AutoSize
$failCount = ($results | Where-Object Result -eq 'FAIL').Count
exit $failCount
```

---

## Scheduling

| Cadence | Script | Owner |
|---|---|---|
| At change window | Script 1 (group create) | Entra Privileged Role Admin |
| Daily | Script 2 (SoD detector, `-IncludePIMEligible`) | AI Governance Lead (automated pipeline) |
| Quarterly | Script 3 (membership + PIM export) | Compliance Officer |
| Quarterly | Script 4 (Dataverse SysAdmin audit) | Power Platform Admin |
| Per release | Validation Script | Release Manager |

All emitted CSVs should be appended to `evidence-hashes.txt` (SHA-256) and stored in your immutable evidence repository per the WORM expectations of FINRA 4511 / SEC 17a-4.

---

[Back to Control 2.8](../../../controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification & Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
