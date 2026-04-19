# PowerShell Setup: Control 1.23 — Step-Up Authentication for AI Agent Operations

!!! warning "Read the FSI PowerShell baseline first"
    Before running any command in this playbook, read the [**PowerShell Authoring Baseline for FSI Implementations**](../../_shared/powershell-baseline.md). It is the canonical source for module version pinning, sovereign-cloud (GCC / GCC High / DoD) endpoints, mutation safety (`-WhatIf` / `SupportsShouldProcess`), Dataverse compatibility, and SHA-256 evidence emission. Snippets below show abbreviated patterns; the baseline is authoritative.

**Last Updated:** April 2026
**Modules Required:** `Microsoft.Graph.Identity.SignIns`, `Microsoft.Graph.Identity.Governance`, `Microsoft.Graph.Reports`
**Graph API surfaces used:** `/identity/conditionalAccess/authenticationContextClassReferences`, `/identity/conditionalAccess/policies`, `/policies/authenticationStrengthPolicies`, `/auditLogs/signIns`

---

## Prerequisites

```powershell
# Pin module versions per the FSI PowerShell baseline (see _shared/powershell-baseline.md for current pins)
Install-Module Microsoft.Graph.Identity.SignIns      -Scope CurrentUser -Force
Install-Module Microsoft.Graph.Identity.Governance   -Scope CurrentUser -Force
Install-Module Microsoft.Graph.Reports               -Scope CurrentUser -Force
```

> **Sovereign cloud note:** For GCC High and DoD tenants, append `-Environment USGov` or `-Environment USGovDoD` to every `Connect-MgGraph` call.

---

## Script 1 — Create Authentication Contexts (`c1`–`c5`)

Authentication contexts can be created via Microsoft Graph (`POST /identity/conditionalAccess/authenticationContextClassReferences`). The cmdlet is `New-MgIdentityConditionalAccessAuthenticationContextClassReference`.

```powershell
<#
.SYNOPSIS
    Creates the five FSI step-up authentication contexts (c1-c5) in Entra.

.DESCRIPTION
    Idempotent. Re-running updates the display name and description of an
    existing context but never deletes one. Authentication context IDs are
    immutable once created.

.EXAMPLE
    .\New-FsiAuthenticationContexts.ps1 -WhatIf
    .\New-FsiAuthenticationContexts.ps1
#>
[CmdletBinding(SupportsShouldProcess)]
param()

Connect-MgGraph -Scopes "Policy.ReadWrite.ConditionalAccess" -NoWelcome | Out-Null

$contexts = @(
    @{ Id = 'c1'; DisplayName = 'Financial Transaction'; Description = 'Critical - 15 min fresh auth' }
    @{ Id = 'c2'; DisplayName = 'Data Export';           Description = 'High - 30 min fresh auth' }
    @{ Id = 'c3'; DisplayName = 'External API Call';     Description = 'High - 30 min fresh auth' }
    @{ Id = 'c4'; DisplayName = 'Configuration Change';  Description = 'High - 30 min fresh auth' }
    @{ Id = 'c5'; DisplayName = 'Sensitive Query';       Description = 'Medium - 60 min fresh auth' }
)

foreach ($ctx in $contexts) {
    $existing = Get-MgIdentityConditionalAccessAuthenticationContextClassReference `
        -AuthenticationContextClassReferenceId $ctx.Id -ErrorAction SilentlyContinue

    if ($existing) {
        if ($PSCmdlet.ShouldProcess($ctx.Id, 'Update authentication context')) {
            Update-MgIdentityConditionalAccessAuthenticationContextClassReference `
                -AuthenticationContextClassReferenceId $ctx.Id `
                -DisplayName $ctx.DisplayName `
                -Description $ctx.Description `
                -IsAvailable:$true | Out-Null
            Write-Host "[UPDATED] $($ctx.Id) - $($ctx.DisplayName)" -ForegroundColor Yellow
        }
    }
    else {
        if ($PSCmdlet.ShouldProcess($ctx.Id, 'Create authentication context')) {
            New-MgIdentityConditionalAccessAuthenticationContextClassReference `
                -Id $ctx.Id `
                -DisplayName $ctx.DisplayName `
                -Description $ctx.Description `
                -IsAvailable:$true | Out-Null
            Write-Host "[CREATED] $($ctx.Id) - $($ctx.DisplayName)" -ForegroundColor Green
        }
    }
}

Disconnect-MgGraph | Out-Null
```

---

## Script 2 — Deploy Step-Up Conditional Access Policies (Report-Only)

```powershell
<#
.SYNOPSIS
    Creates the five FSI-StepUp-* CA policies in REPORT-ONLY state.

.DESCRIPTION
    Use -BreakGlassGroupId to exclude the break-glass exclusion group.
    Re-run is idempotent: existing policies with the same name are updated,
    not duplicated. Policies are created in 'enabledForReportingButNotEnforced'
    state per the FSI 72-hour bake requirement.

.PARAMETER BreakGlassGroupId
    Object ID of the Entra group containing break-glass accounts.

.PARAMETER PhishingResistantStrengthId
    Object ID of the Authentication Strength to require. Defaults to the
    built-in 'Phishing-resistant MFA' strength.

.EXAMPLE
    .\New-FsiStepUpPolicies.ps1 -BreakGlassGroupId '<guid>' -WhatIf
#>
[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(Mandatory)] [string] $BreakGlassGroupId,
    [string] $PhishingResistantStrengthId = '00000000-0000-0000-0000-000000000004'
)

Connect-MgGraph -Scopes "Policy.ReadWrite.ConditionalAccess","Policy.Read.All" -NoWelcome | Out-Null

$matrix = @(
    @{ Name='FSI-StepUp-c1-FinancialTxn';   Ctx='c1'; Freq=15 }
    @{ Name='FSI-StepUp-c2-DataExport';     Ctx='c2'; Freq=30 }
    @{ Name='FSI-StepUp-c3-ExternalAPI';    Ctx='c3'; Freq=30 }
    @{ Name='FSI-StepUp-c4-ConfigChange';   Ctx='c4'; Freq=30 }
    @{ Name='FSI-StepUp-c5-SensitiveQuery'; Ctx='c5'; Freq=60 }
)

foreach ($row in $matrix) {
    $body = @{
        displayName = $row.Name
        state       = 'enabledForReportingButNotEnforced'   # Report-only
        conditions  = @{
            users        = @{
                includeUsers  = @('All')
                excludeGroups = @($BreakGlassGroupId)
            }
            applications = @{
                includeAuthenticationContextClassReferences = @($row.Ctx)
            }
            clientAppTypes = @('all')
        }
        grantControls = @{
            operator                    = 'AND'
            authenticationStrength      = @{ id = $PhishingResistantStrengthId }
        }
        sessionControls = @{
            signInFrequency = @{
                value             = $row.Freq
                type              = 'minutes'
                authenticationType= 'primaryAndSecondaryAuthentication'
                frequencyInterval = 'timeBased'
                isEnabled         = $true
            }
            persistentBrowser = @{ mode = 'never'; isEnabled = $true }
        }
    }

    $existing = Get-MgIdentityConditionalAccessPolicy -Filter "displayName eq '$($row.Name)'" -ErrorAction SilentlyContinue

    if ($existing) {
        if ($PSCmdlet.ShouldProcess($row.Name, 'Update step-up CA policy')) {
            Update-MgIdentityConditionalAccessPolicy -ConditionalAccessPolicyId $existing.Id -BodyParameter $body | Out-Null
            Write-Host "[UPDATED] $($row.Name)" -ForegroundColor Yellow
        }
    }
    else {
        if ($PSCmdlet.ShouldProcess($row.Name, 'Create step-up CA policy')) {
            New-MgIdentityConditionalAccessPolicy -BodyParameter $body | Out-Null
            Write-Host "[CREATED] $($row.Name) (report-only)" -ForegroundColor Green
        }
    }
}

Disconnect-MgGraph | Out-Null
```

> **Reminder:** Promote each policy to `enabled` only after a 72-hour bake window with zero unintended *Failure* outcomes in **Sign-in logs → Conditional Access → Report-only**.

---

## Script 3 — Validate Control 1.23 Configuration

```powershell
<#
.SYNOPSIS
    Validates Control 1.23 - returns a structured object with PASS/FAIL per check.

.OUTPUTS
    PSCustomObject with: AuthContexts, StepUpPolicies, RiskPolicies, AuthStrengths,
    BreakGlassExclusions, OverallStatus.
#>
[CmdletBinding()]
param(
    [string[]] $RequiredContexts = @('c1','c2','c3','c4','c5'),
    [string[]] $RequiredPolicies = @(
        'FSI-StepUp-c1-FinancialTxn','FSI-StepUp-c2-DataExport',
        'FSI-StepUp-c3-ExternalAPI','FSI-StepUp-c4-ConfigChange',
        'FSI-StepUp-c5-SensitiveQuery'),
    [Parameter(Mandatory)] [string] $BreakGlassGroupId
)

Connect-MgGraph -Scopes "Policy.Read.All" -NoWelcome | Out-Null

# Check 1: Authentication contexts exist and are published
$ctxResults = foreach ($id in $RequiredContexts) {
    $c = Get-MgIdentityConditionalAccessAuthenticationContextClassReference `
        -AuthenticationContextClassReferenceId $id -ErrorAction SilentlyContinue
    [PSCustomObject]@{
        Context   = $id
        Exists    = [bool]$c
        Published = $c.IsAvailable -eq $true
        Status    = if ($c -and $c.IsAvailable) { 'PASS' } else { 'FAIL' }
    }
}

# Check 2: Step-up policies exist, are 'enabled', target the right context
$polResults = foreach ($name in $RequiredPolicies) {
    $p = Get-MgIdentityConditionalAccessPolicy -Filter "displayName eq '$name'" -ErrorAction SilentlyContinue
    $excludesBG = $p.Conditions.Users.ExcludeGroups -contains $BreakGlassGroupId
    [PSCustomObject]@{
        Policy           = $name
        Exists           = [bool]$p
        State            = $p.State
        ExcludesBreakGlass = $excludesBG
        Status           = if ($p -and $p.State -eq 'enabled' -and $excludesBG) { 'PASS' } else { 'FAIL' }
    }
}

# Check 3: Risk-based policies are present
$riskPolicies = Get-MgIdentityConditionalAccessPolicy | Where-Object {
    $_.Conditions.SignInRiskLevels.Count -gt 0 -or $_.Conditions.UserRiskLevels.Count -gt 0
}

# Check 4: Phishing-resistant strength is in use somewhere
$strengths = Get-MgPolicyAuthenticationStrengthPolicy

$result = [PSCustomObject]@{
    AuthContexts          = $ctxResults
    StepUpPolicies        = $polResults
    RiskPoliciesCount     = $riskPolicies.Count
    AuthStrengthsCount    = $strengths.Count
    OverallStatus         = if (
        ($ctxResults.Status -notcontains 'FAIL') -and
        ($polResults.Status -notcontains 'FAIL') -and
        ($riskPolicies.Count -ge 1)
    ) { 'PASS' } else { 'FAIL' }
}

Disconnect-MgGraph | Out-Null
$result
```

---

## Script 4 — Export Step-Up Evidence (SHA-256 Hashed)

```powershell
<#
.SYNOPSIS
    Exports CA policy snapshots and recent step-up sign-in events for FSI examination
    evidence. Writes a manifest with SHA-256 hashes per the FSI baseline.

.PARAMETER OutputPath
    Output directory. Defaults to .\evidence\1.23\<UTC-timestamp>\.

.PARAMETER LookbackDays
    Sign-in log lookback window. Defaults to 7. Maximum 30 days for the Graph API.
#>
[CmdletBinding()]
param(
    [string] $OutputPath = ".\evidence\1.23\$(Get-Date -Format 'yyyyMMddTHHmmssZ' -AsUTC)",
    [int]    $LookbackDays = 7
)

New-Item -ItemType Directory -Force -Path $OutputPath | Out-Null
Connect-MgGraph -Scopes "Policy.Read.All","AuditLog.Read.All" -NoWelcome | Out-Null

# Snapshot all step-up CA policies
$polFile = Join-Path $OutputPath 'ca-policies-stepup.json'
Get-MgIdentityConditionalAccessPolicy |
    Where-Object {
        $_.DisplayName -like 'FSI-StepUp-*' -or
        $_.Conditions.Applications.IncludeAuthenticationContextClassReferences.Count -gt 0
    } |
    ConvertTo-Json -Depth 10 | Set-Content -Path $polFile -Encoding UTF8

# Snapshot authentication contexts
$ctxFile = Join-Path $OutputPath 'authentication-contexts.json'
Get-MgIdentityConditionalAccessAuthenticationContextClassReference |
    ConvertTo-Json -Depth 5 | Set-Content -Path $ctxFile -Encoding UTF8

# Snapshot authentication strengths
$strFile = Join-Path $OutputPath 'authentication-strengths.json'
Get-MgPolicyAuthenticationStrengthPolicy |
    ConvertTo-Json -Depth 10 | Set-Content -Path $strFile -Encoding UTF8

# Sign-in events that requested an authentication context
$since = (Get-Date).AddDays(-$LookbackDays).ToString('yyyy-MM-ddTHH:mm:ssZ')
$signInFile = Join-Path $OutputPath 'signins-with-authcontext.json'
$signIns = Get-MgAuditLogSignIn -Filter "createdDateTime ge $since" -All |
    Where-Object { $_.AuthenticationContextClassReferences.Count -gt 0 }
$signIns | ConvertTo-Json -Depth 10 | Set-Content -Path $signInFile -Encoding UTF8

# Manifest with SHA-256 per FSI baseline
$manifest = Get-ChildItem $OutputPath -File | ForEach-Object {
    [PSCustomObject]@{
        File     = $_.Name
        SizeBytes= $_.Length
        SHA256   = (Get-FileHash -Algorithm SHA256 -Path $_.FullName).Hash
    }
}
$manifest | ConvertTo-Json -Depth 3 |
    Set-Content -Path (Join-Path $OutputPath 'manifest.json') -Encoding UTF8

Disconnect-MgGraph | Out-Null
Write-Host "Evidence written to $OutputPath" -ForegroundColor Green
```

---

## Sentinel / Defender XDR KQL — Step-Up Failure Detection

Save as analytics rules per [Step 7 of the portal walkthrough](portal-walkthrough.md#step-7-configure-monitoring-and-alerts).

```kusto
// Step-up failure spike: >5 failures in 10 minutes for the same user
SigninLogs
| where TimeGenerated > ago(15m)
| where AuthenticationContextClassReferences contains "c"
| where ResultType != 0
| summarize FailureCount = count() by UserPrincipalName, bin(TimeGenerated, 10m)
| where FailureCount > 5
```

```kusto
// Conditional Access policy state change on FSI-StepUp-* policies
AuditLogs
| where ActivityDisplayName in ("Update conditional access policy","Delete conditional access policy")
| where TargetResources has "FSI-StepUp-"
| project TimeGenerated, InitiatedBy, ActivityDisplayName, Result, TargetResources
```

```kusto
// PIM activation where required authentication context was not satisfied
AuditLogs
| where Category == "RoleManagement"
| where ActivityDisplayName == "Add member to role completed (PIM activation)"
| extend ContextRequested = tostring(parse_json(AdditionalDetails)[0].value)
| where isnotempty(ContextRequested)
| join kind=leftouter (
    SigninLogs
    | where AuthenticationContextClassReferences contains "c"
    | project UserId, SigninAuthContext = AuthenticationContextClassReferences, SignInTime = TimeGenerated
) on $left.InitiatedBy.user.id == $right.UserId
| where SigninAuthContext !contains ContextRequested or isnull(SigninAuthContext)
```

---

[Back to Control 1.23](../../../controls/pillar-1-security/1.23-step-up-authentication-for-agent-operations.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
