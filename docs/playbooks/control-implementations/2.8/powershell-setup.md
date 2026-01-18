# PowerShell Setup: Control 2.8 - Access Control and Segregation of Duties

**Last Updated:** January 2026
**Modules Required:** Microsoft.Graph, Microsoft.PowerApps.Administration.PowerShell

## Prerequisites

```powershell
Install-Module -Name Microsoft.Graph -Force -Scope CurrentUser
Install-Module -Name Microsoft.PowerApps.Administration.PowerShell -Force -Scope CurrentUser
```

---

## Automated Scripts

### Create Security Groups

```powershell
<#
.SYNOPSIS
    Creates security groups for agent governance roles

.EXAMPLE
    .\New-AgentGovernanceGroups.ps1
#>

Write-Host "=== Create Agent Governance Security Groups ===" -ForegroundColor Cyan

Connect-MgGraph -Scopes "Group.ReadWrite.All", "Directory.ReadWrite.All"

$groups = @(
    @{DisplayName="SG-Agent-Developers"; Description="Can create and edit agents"; MailNickname="sg-agent-developers"},
    @{DisplayName="SG-Agent-Reviewers"; Description="Can review agent submissions"; MailNickname="sg-agent-reviewers"},
    @{DisplayName="SG-Agent-Approvers"; Description="Can approve agent deployments"; MailNickname="sg-agent-approvers"},
    @{DisplayName="SG-Agent-ReleaseManagers"; Description="Can deploy agents to production"; MailNickname="sg-agent-releasemgrs"},
    @{DisplayName="SG-Agent-PlatformAdmins"; Description="Can configure platform settings"; MailNickname="sg-agent-platformadmins"}
)

foreach ($group in $groups) {
    $existing = Get-MgGroup -Filter "displayName eq '$($group.DisplayName)'"
    if (-not $existing) {
        $newGroup = New-MgGroup -DisplayName $group.DisplayName `
                                -Description $group.Description `
                                -MailNickname $group.MailNickname `
                                -MailEnabled:$false `
                                -SecurityEnabled:$true
        Write-Host "[CREATED] $($group.DisplayName)" -ForegroundColor Green
    } else {
        Write-Host "[EXISTS] $($group.DisplayName)" -ForegroundColor Yellow
    }
}

Disconnect-MgGraph
```

### Export Role Membership Report

```powershell
<#
.SYNOPSIS
    Exports membership of agent governance groups

.EXAMPLE
    .\Export-AgentGovernanceRoles.ps1
#>

Write-Host "=== Agent Governance Role Membership Report ===" -ForegroundColor Cyan

Connect-MgGraph -Scopes "Group.Read.All", "User.Read.All"

$groupPrefixes = @("SG-Agent-Developers", "SG-Agent-Reviewers", "SG-Agent-Approvers", "SG-Agent-ReleaseManagers", "SG-Agent-PlatformAdmins")
$report = @()

foreach ($prefix in $groupPrefixes) {
    $group = Get-MgGroup -Filter "displayName eq '$prefix'"
    if ($group) {
        $members = Get-MgGroupMember -GroupId $group.Id
        foreach ($member in $members) {
            $user = Get-MgUser -UserId $member.Id
            $report += [PSCustomObject]@{
                Group = $prefix
                UserPrincipalName = $user.UserPrincipalName
                DisplayName = $user.DisplayName
                JobTitle = $user.JobTitle
            }
        }
        Write-Host "$prefix : $($members.Count) members" -ForegroundColor Green
    }
}

$report | Export-Csv -Path ".\AgentGovernanceRoles_$(Get-Date -Format 'yyyyMMdd').csv" -NoTypeInformation
Write-Host "`nExported to AgentGovernanceRoles_$(Get-Date -Format 'yyyyMMdd').csv" -ForegroundColor Cyan

Disconnect-MgGraph
```

### Segregation of Duties Validation

```powershell
<#
.SYNOPSIS
    Validates no SoD violations exist (user in conflicting roles)

.EXAMPLE
    .\Test-SoDCompliance.ps1
#>

Write-Host "=== Segregation of Duties Validation ===" -ForegroundColor Cyan

Connect-MgGraph -Scopes "Group.Read.All", "User.Read.All"

# Define conflicting role pairs
$conflictingPairs = @(
    @{Role1="SG-Agent-Developers"; Role2="SG-Agent-Approvers"; Reason="Creator cannot approve own work"},
    @{Role1="SG-Agent-Approvers"; Role2="SG-Agent-ReleaseManagers"; Reason="Approver cannot deploy"},
    @{Role1="SG-Agent-Developers"; Role2="SG-Agent-ReleaseManagers"; Reason="Creator cannot deploy"}
)

$violations = @()

foreach ($pair in $conflictingPairs) {
    $group1 = Get-MgGroup -Filter "displayName eq '$($pair.Role1)'"
    $group2 = Get-MgGroup -Filter "displayName eq '$($pair.Role2)'"

    if ($group1 -and $group2) {
        $members1 = (Get-MgGroupMember -GroupId $group1.Id).Id
        $members2 = (Get-MgGroupMember -GroupId $group2.Id).Id

        $overlap = $members1 | Where-Object { $_ -in $members2 }

        foreach ($userId in $overlap) {
            $user = Get-MgUser -UserId $userId
            $violations += [PSCustomObject]@{
                User = $user.UserPrincipalName
                Role1 = $pair.Role1
                Role2 = $pair.Role2
                Violation = $pair.Reason
            }
        }
    }
}

if ($violations.Count -eq 0) {
    Write-Host "[PASS] No SoD violations found" -ForegroundColor Green
} else {
    Write-Host "[FAIL] $($violations.Count) SoD violation(s) found:" -ForegroundColor Red
    $violations | Format-Table -AutoSize
}

Disconnect-MgGraph
```

---

## Validation Script

```powershell
<#
.SYNOPSIS
    Validates Control 2.8 - Access Control and Segregation of Duties

.EXAMPLE
    .\Validate-Control-2.8.ps1
#>

Write-Host "=== Control 2.8 Validation ===" -ForegroundColor Cyan

Connect-MgGraph -Scopes "Group.Read.All", "RoleManagement.Read.All"

# Check 1: Security groups exist
Write-Host "`n[Check 1] Security Groups" -ForegroundColor Cyan
$requiredGroups = @("SG-Agent-Developers", "SG-Agent-Reviewers", "SG-Agent-Approvers", "SG-Agent-ReleaseManagers", "SG-Agent-PlatformAdmins")
$groupsFound = 0

foreach ($groupName in $requiredGroups) {
    $group = Get-MgGroup -Filter "displayName eq '$groupName'"
    if ($group) {
        Write-Host "[PASS] $groupName exists" -ForegroundColor Green
        $groupsFound++
    } else {
        Write-Host "[FAIL] $groupName not found" -ForegroundColor Red
    }
}

# Check 2: PIM configured (check for active assignments)
Write-Host "`n[Check 2] Privileged Identity Management" -ForegroundColor Cyan
Write-Host "[INFO] Verify PIM is configured for admin roles in Entra Admin Center" -ForegroundColor Yellow

# Check 3: Access reviews (manual verification)
Write-Host "`n[Check 3] Access Reviews" -ForegroundColor Cyan
Write-Host "[INFO] Verify quarterly access reviews are scheduled in Identity Governance" -ForegroundColor Yellow

# Check 4: SoD validation
Write-Host "`n[Check 4] Segregation of Duties" -ForegroundColor Cyan
# Run SoD check inline
$conflictingPairs = @(
    @{Role1="SG-Agent-Developers"; Role2="SG-Agent-Approvers"},
    @{Role1="SG-Agent-Approvers"; Role2="SG-Agent-ReleaseManagers"},
    @{Role1="SG-Agent-Developers"; Role2="SG-Agent-ReleaseManagers"}
)

$hasViolations = $false
foreach ($pair in $conflictingPairs) {
    $g1 = Get-MgGroup -Filter "displayName eq '$($pair.Role1)'"
    $g2 = Get-MgGroup -Filter "displayName eq '$($pair.Role2)'"
    if ($g1 -and $g2) {
        $m1 = (Get-MgGroupMember -GroupId $g1.Id -ErrorAction SilentlyContinue).Id
        $m2 = (Get-MgGroupMember -GroupId $g2.Id -ErrorAction SilentlyContinue).Id
        if ($m1 -and $m2) {
            $overlap = $m1 | Where-Object { $_ -in $m2 }
            if ($overlap) { $hasViolations = $true }
        }
    }
}

if (-not $hasViolations) {
    Write-Host "[PASS] No SoD violations detected" -ForegroundColor Green
} else {
    Write-Host "[FAIL] SoD violations detected - run Test-SoDCompliance.ps1 for details" -ForegroundColor Red
}

Write-Host "`n=== Validation Summary ===" -ForegroundColor Cyan
Write-Host "Groups configured: $groupsFound / $($requiredGroups.Count)"

Disconnect-MgGraph
```

---

[Back to Control 2.8](../../../controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
