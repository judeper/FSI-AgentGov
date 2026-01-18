# PowerShell Setup: Control 1.23 - Step-Up Authentication

**Last Updated:** January 2026
**Modules Required:** Microsoft.Graph

## Prerequisites

```powershell
Install-Module -Name Microsoft.Graph -Force -Scope CurrentUser
```

---

## Automated Scripts

### Create Authentication Contexts

```powershell
<#
.SYNOPSIS
    Creates authentication contexts for step-up authentication

.EXAMPLE
    .\New-AuthenticationContexts.ps1
#>

Write-Host "=== Create Authentication Contexts ===" -ForegroundColor Cyan

Connect-MgGraph -Scopes "Policy.ReadWrite.ConditionalAccess"

$contexts = @(
    @{Id="c1"; DisplayName="Financial Transaction"; Description="Critical - 15 min fresh auth"; IsAvailable=$true},
    @{Id="c2"; DisplayName="Data Export"; Description="High - 30 min fresh auth"; IsAvailable=$true},
    @{Id="c3"; DisplayName="External API Call"; Description="High - 30 min fresh auth"; IsAvailable=$true},
    @{Id="c4"; DisplayName="Configuration Change"; Description="High - 30 min fresh auth"; IsAvailable=$true},
    @{Id="c5"; DisplayName="Sensitive Query"; Description="Medium - 60 min fresh auth"; IsAvailable=$true}
)

foreach ($ctx in $contexts) {
    Write-Host "Creating context: $($ctx.DisplayName)" -ForegroundColor Yellow
    # Note: Authentication context creation requires Graph API
    # Use portal for initial creation
}

Write-Host "[INFO] Create authentication contexts in Entra admin center:"
Write-Host "  Protection > Conditional Access > Authentication context"

Disconnect-MgGraph
```

### Export Step-Up Configuration

```powershell
<#
.SYNOPSIS
    Exports step-up authentication configuration

.EXAMPLE
    .\Export-StepUpConfig.ps1
#>

param(
    [string]$OutputPath = ".\StepUpConfiguration.csv"
)

Write-Host "=== Export Step-Up Configuration ===" -ForegroundColor Cyan

Connect-MgGraph -Scopes "Policy.Read.All"

# Get Conditional Access policies related to step-up
$policies = Get-MgIdentityConditionalAccessPolicy | Where-Object {
    $_.DisplayName -like "*StepUp*" -or $_.DisplayName -like "*Step-Up*"
}

$export = @()
foreach ($policy in $policies) {
    $export += [PSCustomObject]@{
        PolicyName = $policy.DisplayName
        State = $policy.State
        GrantControls = ($policy.GrantControls.BuiltInControls -join ", ")
        SessionControls = $policy.SessionControls.SignInFrequency
        AuthContexts = ($policy.Conditions.Applications.IncludeAuthenticationContextClassReferences -join ", ")
    }
}

$export | Export-Csv -Path $OutputPath -NoTypeInformation
Write-Host "Export saved to: $OutputPath" -ForegroundColor Green

Disconnect-MgGraph
```

---

## Validation Script

```powershell
<#
.SYNOPSIS
    Validates Control 1.23 - Step-up authentication configuration

.EXAMPLE
    .\Validate-Control-1.23.ps1
#>

Write-Host "=== Control 1.23 Validation ===" -ForegroundColor Cyan

Connect-MgGraph -Scopes "Policy.Read.All"

# Check 1: Authentication contexts
Write-Host "`n[Check 1] Authentication Contexts" -ForegroundColor Cyan
Write-Host "[INFO] Verify contexts in Entra admin center"

# Check 2: CA policies
Write-Host "`n[Check 2] Conditional Access Policies" -ForegroundColor Cyan
$stepUpPolicies = Get-MgIdentityConditionalAccessPolicy | Where-Object {
    $_.DisplayName -like "*StepUp*" -or $_.Conditions.Applications.IncludeAuthenticationContextClassReferences
}
Write-Host "Step-up policies found: $($stepUpPolicies.Count)"

# Check 3: Authentication strengths
Write-Host "`n[Check 3] Authentication Strengths" -ForegroundColor Cyan
$strengths = Get-MgPolicyAuthenticationStrengthPolicy
Write-Host "Custom strengths: $($strengths.Count)"

Disconnect-MgGraph

Write-Host "`n=== Validation Complete ===" -ForegroundColor Cyan
```

---

[Back to Control 1.23](../../../controls/pillar-1-security/1.23-step-up-authentication-for-agent-operations.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
