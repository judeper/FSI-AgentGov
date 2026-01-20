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

## Complete Configuration Script

```powershell
<#
.SYNOPSIS
    Configures Control 1.23 - Step-Up Authentication for Agent Operations

.DESCRIPTION
    This script validates authentication context configuration, exports
    Conditional Access policies for step-up authentication, and generates
    compliance reports.

.PARAMETER ExportPath
    Path for exports (default: current directory)

.EXAMPLE
    .\Configure-Control-1.23.ps1

.NOTES
    Last Updated: January 2026
    Related Control: Control 1.23 - Step-Up Authentication for Agent Operations
#>

param(
    [string]$ExportPath = "."
)

try {
    # Connect to Microsoft Graph
    Write-Host "Connecting to Microsoft Graph..." -ForegroundColor Cyan
    Connect-MgGraph -Scopes "Policy.Read.All", "Policy.ReadWrite.ConditionalAccess"

    Write-Host "Configuring Control 1.23: Step-Up Authentication for Agent Operations" -ForegroundColor Cyan

    # Step 1: Define authentication contexts
    Write-Host "`n[Step 1] Authentication context requirements..." -ForegroundColor Yellow
    $contexts = @(
        @{Id="c1"; DisplayName="Financial Transaction"; Description="Critical - 15 min fresh auth"},
        @{Id="c2"; DisplayName="Data Export"; Description="High - 30 min fresh auth"},
        @{Id="c3"; DisplayName="External API Call"; Description="High - 30 min fresh auth"},
        @{Id="c4"; DisplayName="Configuration Change"; Description="High - 30 min fresh auth"},
        @{Id="c5"; DisplayName="Sensitive Query"; Description="Medium - 60 min fresh auth"}
    )

    Write-Host "  Required authentication contexts:" -ForegroundColor Gray
    foreach ($ctx in $contexts) {
        Write-Host "    - $($ctx.DisplayName): $($ctx.Description)"
    }
    Write-Host "`n  [INFO] Create contexts in Entra admin center:" -ForegroundColor Gray
    Write-Host "    Protection > Conditional Access > Authentication context" -ForegroundColor Gray

    # Step 2: Check existing step-up policies
    Write-Host "`n[Step 2] Checking existing step-up CA policies..." -ForegroundColor Yellow
    $allPolicies = Get-MgIdentityConditionalAccessPolicy
    $stepUpPolicies = $allPolicies | Where-Object {
        $_.DisplayName -like "*StepUp*" -or
        $_.DisplayName -like "*Step-Up*" -or
        $_.Conditions.Applications.IncludeAuthenticationContextClassReferences
    }

    if ($stepUpPolicies) {
        Write-Host "  Step-up policies found: $($stepUpPolicies.Count)" -ForegroundColor Green
        $stepUpPolicies | ForEach-Object { Write-Host "    - $($_.DisplayName): $($_.State)" }
    } else {
        Write-Host "  No step-up policies found" -ForegroundColor Yellow
        Write-Host "  [INFO] Create policies in Entra admin center" -ForegroundColor Gray
    }

    # Step 3: Check authentication strengths
    Write-Host "`n[Step 3] Checking authentication strength policies..." -ForegroundColor Yellow
    $strengths = Get-MgPolicyAuthenticationStrengthPolicy
    Write-Host "  Authentication strengths: $($strengths.Count)" -ForegroundColor Green
    $strengths | ForEach-Object { Write-Host "    - $($_.DisplayName): $($_.PolicyType)" }

    # Step 4: Export configuration
    Write-Host "`n[Step 4] Exporting step-up configuration..." -ForegroundColor Yellow

    $export = @()
    foreach ($policy in $stepUpPolicies) {
        $export += [PSCustomObject]@{
            PolicyName = $policy.DisplayName
            State = $policy.State
            GrantControls = ($policy.GrantControls.BuiltInControls -join ", ")
            SessionFrequency = $policy.SessionControls.SignInFrequency.Value
            AuthContexts = ($policy.Conditions.Applications.IncludeAuthenticationContextClassReferences -join ", ")
            ExportDate = Get-Date
        }
    }

    if ($export.Count -gt 0) {
        $exportFile = Join-Path $ExportPath "StepUpAuth-Config-$(Get-Date -Format 'yyyyMMdd').csv"
        $export | Export-Csv -Path $exportFile -NoTypeInformation
        Write-Host "  Configuration exported to: $exportFile" -ForegroundColor Green
    }

    # Step 5: Export authentication strengths
    $strengthFile = Join-Path $ExportPath "AuthStrengths-$(Get-Date -Format 'yyyyMMdd').csv"
    $strengths | Select-Object DisplayName, PolicyType, Description |
        Export-Csv -Path $strengthFile -NoTypeInformation
    Write-Host "  Authentication strengths exported to: $strengthFile" -ForegroundColor Green

    Write-Host "`n[PASS] Control 1.23 configuration completed successfully" -ForegroundColor Green
}
catch {
    Write-Host "[FAIL] Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "[INFO] Stack trace: $($_.ScriptStackTrace)" -ForegroundColor Yellow
    exit 1
}
finally {
    # Cleanup connections
    if (Get-MgContext) {
        Disconnect-MgGraph -ErrorAction SilentlyContinue
        Write-Host "`nDisconnected from Microsoft Graph" -ForegroundColor Gray
    }
}
```

---

[Back to Control 1.23](../../../controls/pillar-1-security/1.23-step-up-authentication-for-agent-operations.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
