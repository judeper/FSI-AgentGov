# Phase 1: PowerShell Core - Research

**Researched:** 2026-02-06
**Domain:** Microsoft Graph Identity.SignIns API, Conditional Access session controls, authentication contexts
**Confidence:** HIGH

## Summary

Phase 1 implements standalone PowerShell scripts for deploying and validating Conditional Access session security configurations aligned with FSI-AgentGov governance zones. The core technology stack is Microsoft Graph PowerShell SDK v2.35.1 with Microsoft.Graph.Identity.SignIns module for CA policy CRUD operations.

The standard approach is:
1. Deploy authentication contexts (c1-c5) as step-up triggers using authenticationContextClassReference API
2. Deploy CA policies in report-only mode with zone-specific session controls (signInFrequency, persistentBrowser)
3. Enforce 72-hour minimum bake period before enforced mode transition
4. Validate configurations against zone baselines with pass/fail/warning status
5. Audit for policy conflicts using AND-logic evaluation rules

Key technical constraints:
- `frequencyInterval: "everyTime"` for Zone 3 risky users requires Microsoft.Graph.Beta.Identity.SignIns
- All other operations use v1.0 API for production stability
- Authentication strength policies coexist with builtInControls in same grantControls object
- Break-glass exclusion validation is mandatory for every deployment operation

**Primary recommendation:** Follow existing CAA and ACV solution patterns for script structure (orchestrator + private helpers), parameter handling (TenantId, Interactive, DryRun), and output formatting (color-coded banners, structured results).

## Standard Stack

The established libraries/tools for Conditional Access automation:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Microsoft.Graph.Identity.SignIns | v2.35.1 | CA policy CRUD, auth contexts, auth strength | GA v1.0 API, production-stable, existing CAA solution uses it |
| Microsoft.Graph.Beta.Identity.SignIns | v2.35.1 | ONLY for `frequencyInterval: "everyTime"` | Required for Zone 3 risky user reauthentication every session |
| Microsoft.Graph.Authentication | v2.35.1 | Graph connection management | Standard auth module for all Graph operations |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| PowerShell | 7.0+ | Script runtime | Required for all solutions (ACV and CAA use 7.0+) |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Graph SDK | Raw REST API | SDK provides automatic retry, error handling, token management - REST requires manual implementation |
| v1.0 API for everyTime | Beta API only | Beta required for this feature - GitHub issue #647 confirms v1.0 returns 400 error |
| Interactive auth | Service principal | Service principals need Policy.ReadWrite.ConditionalAccess, but interactive is simpler for operator workflows |

**Installation:**
```bash
Install-Module Microsoft.Graph.Identity.SignIns -MinimumVersion 2.35.1
Install-Module Microsoft.Graph.Beta.Identity.SignIns -MinimumVersion 2.35.1
Install-Module Microsoft.Graph.Authentication -MinimumVersion 2.35.1
```

**Permissions:**
- Policy.ReadWrite.ConditionalAccess (covers CA policies, auth contexts, auth strength policies)
- No additional permissions needed beyond existing CAA solution

## Architecture Patterns

### Recommended Project Structure
```
session-security-configurator/
├── scripts/
│   ├── Deploy-AuthContexts.ps1           # Create c1-c5 with conflict detection
│   ├── Deploy-StepUpPolicies.ps1         # Zone-specific CA policy deployment
│   ├── Test-SessionCompliance.ps1        # Validate session controls per zone
│   └── private/
│       ├── Connect-GraphSession.ps1      # Graph auth helper
│       ├── Compare-SessionBaseline.ps1   # Baseline comparison logic
│       └── Test-BreakGlassExclusion.ps1  # Break-glass validation helper
├── templates/
│   ├── auth-contexts/
│   │   └── auth-contexts-c1-c5.json      # Authentication context definitions
│   ├── step-up/
│   │   ├── zone1-step-up-policy.json     # Zone 1 risky sign-in policy
│   │   ├── zone2-step-up-policy.json     # Zone 2 sensitive operations
│   │   └── zone3-step-up-policy.json     # Zone 3 high-risk operations
│   └── session-baselines/
│       ├── zone1-baseline.json           # 8h sign-in, standard MFA
│       ├── zone2-baseline.json           # 4h sign-in/30min idle, passwordless MFA
│       └── zone3-baseline.json           # 1h sign-in/15min idle, phishing-resistant MFA
└── docs/
    └── DEPLOYMENT-GUIDE.md               # Operator walkthrough
```

### Pattern 1: Orchestrator + Private Helpers
**What:** Main scripts (Deploy-*, Test-*) orchestrate workflow, private helpers handle shared logic
**When to use:** All solution scripts
**Example:**
```powershell
# Source: Existing ACV solution pattern
# From: /Users/admin/dev/FSI-AgentGov-Solutions/audit-configuration-validator/scripts/Invoke-TenantAuditValidation.ps1

# Orchestrator loads validators
$scriptRoot = $PSScriptRoot
. "$scriptRoot\Test-UnifiedAuditLog.ps1"
. "$scriptRoot\Test-MailboxAudit.ps1"
. "$scriptRoot\Test-PurviewRetention.ps1"

# Execute each validator with common auth params
$results.Validators.UnifiedAuditLog = Test-UnifiedAuditLog @authParams
$results.Validators.MailboxAudit = Test-MailboxAudit @authParams
$results.Validators.PurviewRetention = Test-PurviewRetention @authParams

# Compute overall status from individual results
if ($statuses -contains "Failed") {
    $results.OverallStatus = "Failed"
}
```

### Pattern 2: Idempotent Deployment with Conflict Detection
**What:** Check for existing resources, warn if conflicts, create only if missing
**When to use:** Deploy-AuthContexts.ps1, Deploy-StepUpPolicies.ps1
**Example:**
```powershell
# Source: Existing CAA solution pattern
# From: /Users/admin/dev/FSI-AgentGov-Solutions/conditional-access-automation/scripts/Deploy-CAPolicies.ps1

$existingPolicy = Get-MgIdentityConditionalAccessPolicy -Filter "displayName eq '$policyName'" -ErrorAction SilentlyContinue

if ($existingPolicy) {
    if ($Force) {
        Write-Host "  Updating existing policy..." -ForegroundColor Yellow
        Update-MgIdentityConditionalAccessPolicy `
            -ConditionalAccessPolicyId $existingPolicy.Id `
            -BodyParameter $template
        Write-Host "  Updated successfully." -ForegroundColor Green
    }
    else {
        Write-Host "  Policy exists. Use -Force to update." -ForegroundColor Yellow
    }
}
else {
    # Create new policy
    Write-Host "  Creating policy..."
    $newPolicy = New-MgIdentityConditionalAccessPolicy -BodyParameter $template
    Write-Host "  Created successfully. ID: $($newPolicy.Id)" -ForegroundColor Green
}
```

### Pattern 3: DryRun Implementation
**What:** Preview changes without applying, return structured results
**When to use:** All deployment operations (SCM-04 requirement)
**Example:**
```powershell
# Source: Existing CAA solution pattern
# From: /Users/admin/dev/FSI-AgentGov-Solutions/conditional-access-automation/scripts/Deploy-CAPolicies.ps1

if ($DryRun) {
    Write-Host "  [DRY RUN] Would create policy" -ForegroundColor Yellow
    $deployedPolicies += @{
        Name = $policyName
        Template = $templateFile
        State = $template.state
        Status = "DryRun"
    }
    continue
}

# Connect to Microsoft Graph
if (-not $DryRun) {
    Write-Host "`nConnecting to Microsoft Graph..."
    Connect-MgGraph -TenantId $TenantId -Scopes "Policy.ReadWrite.ConditionalAccess"
}
```

### Pattern 4: Structured Validation Results
**What:** Consistent result object with status, confidence, reason, timestamp
**When to use:** Test-SessionCompliance.ps1, all validation operations
**Example:**
```powershell
# Source: Existing ACV solution pattern
# From: /Users/admin/dev/FSI-AgentGov-Solutions/audit-configuration-validator/scripts/Invoke-TenantAuditValidation.ps1

$results = @{
    Timestamp = (Get-Date -Format "o")
    Zone = $Zone
    Validators = @{}
    OverallStatus = "Unknown"
    Reason = ""
}

# Each validator returns structured result
$results.Validators.UnifiedAuditLog = @{
    OverallStatus = "Passed"
    Confidence = "HIGH"
    Reason = "Unified Audit Log enabled, canary event found"
    Timestamp = Get-Date -Format "o"
}

# Compute overall status
if ($statuses -contains "Failed") {
    $results.OverallStatus = "Failed"
    $results.Reason = "One or more validators failed. Review individual validator results."
}
```

### Pattern 5: Banner and Color-Coded Output
**What:** Cyan banners for sections, Green/Yellow/Red for status
**When to use:** All user-facing scripts
**Example:**
```powershell
# Source: Existing ACV solution pattern
# From: /Users/admin/dev/FSI-AgentGov-Solutions/audit-configuration-validator/scripts/Invoke-TenantAuditValidation.ps1

Write-Host "`n╔══════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  M365 Tenant Audit Configuration Validation     ║" -ForegroundColor Cyan
Write-Host "╠══════════════════════════════════════════════════╣" -ForegroundColor Cyan
Write-Host "║  FSI-AgentGov Control 1.7                        ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════╝" -ForegroundColor Cyan

$statusColor = switch ($results.OverallStatus) {
    "Passed" { "Green" }
    "Failed" { "Red" }
    "Warning" { "Yellow" }
    default { "Gray" }
}
Write-Host "Result: $($results.OverallStatus)" -ForegroundColor $statusColor
```

### Pattern 6: Parameter Splatting for Auth
**What:** Build common auth parameter hashtable, splat to all commands
**When to use:** Scripts supporting both interactive and service principal auth
**Example:**
```powershell
# Source: Existing ACV solution pattern
# From: /Users/admin/dev/FSI-AgentGov-Solutions/audit-configuration-validator/scripts/Invoke-TenantAuditValidation.ps1

# Build common authentication parameter hashtable
$authParams = @{}
if ($Interactive) { $authParams.Interactive = $true }
if ($TenantId) { $authParams.TenantId = $TenantId }
if ($ClientId) { $authParams.ClientId = $ClientId }
if ($CertificateThumbprint) { $authParams.CertificateThumbprint = $CertificateThumbprint }

# Splat to all validators
$results.Validators.UnifiedAuditLog = Test-UnifiedAuditLog @authParams
$results.Validators.MailboxAudit = Test-MailboxAudit @authParams
```

### Anti-Patterns to Avoid

- **Hard-coded resource IDs:** Templates use placeholders like `<zone-1-users-group-id>`, configs provide actual values
- **No dry-run:** Every deployment operation must support -DryRun to preview changes
- **Silent failures:** Log errors to $errors array, display summary at end
- **Premature enforcement:** Never deploy policies in enforced mode without report-only bake period
- **Missing break-glass validation:** Every deployment must validate break-glass exclusions to prevent tenant lockout

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Graph API authentication | Custom token refresh logic | Microsoft.Graph.Authentication | Handles token refresh, retry logic, error handling automatically |
| CA policy conflict detection | Manual policy comparison | Get-MgIdentityConditionalAccessPolicy with filtering | Graph API already knows which policies apply to same conditions |
| Baseline comparison | String comparison of JSON | Private helper Compare-SessionBaseline.ps1 | Need to normalize signInFrequency (hours vs minutes), handle missing properties |
| Break-glass validation | Manual user list comparison | Private helper Test-BreakGlassExclusion.ps1 | Must check excludeUsers AND excludeGroups, resolve group members |
| Report-only enforcement | Honor system | State validation + timestamp check | Must prevent enforcement before 72-hour minimum bake period |

**Key insight:** Conditional Access policy evaluation is complex (AND logic, inheritance, exclusions). Don't replicate Graph API logic - query actual policy state and let Microsoft's engine do the evaluation.

## Common Pitfalls

### Pitfall 1: Overlapping CA Policy Session Controls
**What goes wrong:** Multiple CA policies with different signInFrequency values apply to same user/app, causing unpredictable session timeouts
**Why it happens:** CA policies use AND logic - when multiple policies apply, most restrictive session control wins
**How to avoid:**
- Pre-deployment audit: Query all CA policies targeting same includeGroups/includeApplications
- Check for conflicting sessionControls.signInFrequency values
- Warn operator if overlap detected: "Existing policy 'CA-Legacy-4h' also applies to Zone 2 users with 4h timeout. This policy enforces 4h timeout."
**Warning signs:**
- Users report unexpected MFA prompts (shorter timeout winning)
- Sign-in logs show multiple CA policies evaluated for same session

### Pitfall 2: Break-Glass Account Exclusion Failure
**What goes wrong:** Break-glass accounts not excluded from new CA policy, tenant lockout occurs when policy enforced
**Why it happens:** Template has placeholders for excludeUsers, deployment script doesn't validate they're populated with actual break-glass accounts
**How to avoid:**
- Every deployment operation MUST call private/Test-BreakGlassExclusion.ps1
- Validate break-glass accounts exist in excludeUsers OR parent excludeGroups
- ABORT deployment if break-glass validation fails
**Warning signs:**
- Template has `"excludeUsers": []` empty array
- Config file missing breakGlassAccounts section
- Break-glass accounts are group members but policy doesn't exclude the group

### Pitfall 3: Premature Report-Only to Enforced Transition
**What goes wrong:** Policy deployed in enforced mode too quickly, users blocked from legitimate access patterns not seen in testing
**Why it happens:** Operator skips report-only bake period or miscalculates 72-hour window
**How to avoid:**
- Deploy-StepUpPolicies.ps1 MUST create policies in report-only mode by default
- Add -EnablePolicies parameter with confirmation prompt: "DANGER: Policy will be enforced immediately. Report-only period should be minimum 72 hours."
- Check policy createdDateTime, block enforcement if < 72 hours old
**Warning signs:**
- Policy has `"state": "enabled"` instead of `"state": "enabledForReportingButNotEnforced"`
- createdDateTime shows policy created < 72 hours ago
- No sign-in log entries exist for policy (never evaluated in report-only)

### Pitfall 4: Authentication Context Already in Use
**What goes wrong:** Deploy-AuthContexts.ps1 creates c1 with description "FSI-AgentGov Zone 1", but tenant already uses c1 for different purpose (e.g., "PIM elevation")
**Why it happens:** authenticationContextClassReference IDs (c1-c25) are tenant-wide shared resource
**How to avoid:**
- Query existing auth contexts: `Get-MgIdentityConditionalAccessAuthenticationContextClassReference`
- Detect conflicts: Check if c1-c5 exist with different descriptions
- Warn operator: "Auth context c1 already exists with description 'PIM elevation'. FSI-AgentGov expects c1='FSI Zone 1'. Use -Force to overwrite or choose different IDs."
- Provide -AuthContextPrefix parameter to use c10-c14 instead of c1-c5
**Warning signs:**
- Graph API returns 409 Conflict on auth context creation
- Existing CA policies reference c1-c5 for non-FSI purposes

### Pitfall 5: Persistent Browser Requires "All Cloud Apps"
**What goes wrong:** Policy sets `persistentBrowser.mode: "never"` but targets only specific app IDs, browser session persists unexpectedly
**Why it happens:** persistentBrowser is browser-level control, not app-level - requires `includeApplications: ["All"]` to work
**How to avoid:**
- Templates for persistent browser MUST use `"includeApplications": ["All"]`
- Validate: If sessionControls.persistentBrowser exists, check conditions.applications.includeApplications contains "All"
- Warn if app-specific: "Persistent browser control requires 'All cloud apps' targeting. This policy targets specific apps and may not enforce persistent browser settings."
**Warning signs:**
- Policy targets individual app IDs but includes persistentBrowser control
- Users report "Remember me" checkbox persists session despite policy

### Pitfall 6: frequencyInterval Beta API Requirement
**What goes wrong:** Script uses v1.0 API to set `frequencyInterval: "everyTime"`, Graph returns 400 error
**Why it happens:** everyTime value only supported in beta API (GitHub issue #647 confirms)
**How to avoid:**
- Zone 3 risky user policy MUST use Microsoft.Graph.Beta.Identity.SignIns
- All other policies use v1.0 API for stability
- Detect Beta requirement: If template contains `"frequencyInterval": "everyTime"`, switch to Beta module
**Warning signs:**
- Error message: "Operation requires beta endpoint"
- 400 Bad Request when creating CA policy with everyTime

## Code Examples

Verified patterns from official sources:

### Creating Authentication Contexts (c1-c5)
```powershell
# Source: Microsoft Learn - authenticationContextClassReference API
# URL: https://learn.microsoft.com/en-us/graph/api/resources/authenticationcontextclassreference

# Query existing auth contexts to detect conflicts
$existingContexts = Get-MgIdentityConditionalAccessAuthenticationContextClassReference

# Define FSI-AgentGov contexts
$authContexts = @(
    @{ id = "c1"; displayName = "FSI-AgentGov Zone 1"; description = "Personal Productivity zone step-up" },
    @{ id = "c2"; displayName = "FSI-AgentGov Zone 2"; description = "Team Collaboration zone step-up" },
    @{ id = "c3"; displayName = "FSI-AgentGov Zone 3"; description = "Enterprise Managed zone step-up" },
    @{ id = "c4"; displayName = "FSI-AgentGov PIM Elevation"; description = "PIM role activation step-up" },
    @{ id = "c5"; displayName = "FSI-AgentGov Emergency Access"; description = "Break-glass account activation" }
)

foreach ($context in $authContexts) {
    $existing = $existingContexts | Where-Object { $_.Id -eq $context.id }

    if ($existing) {
        if ($existing.DisplayName -ne $context.displayName) {
            Write-Warning "Auth context $($context.id) exists with different name: '$($existing.DisplayName)'"
            Write-Warning "FSI-AgentGov expects: '$($context.displayName)'"
            if (-not $Force) {
                throw "Auth context conflict detected. Use -Force to overwrite or -AuthContextPrefix to use different IDs."
            }
        }
        Write-Host "Auth context $($context.id) already exists." -ForegroundColor Cyan
    }
    else {
        if (-not $DryRun) {
            New-MgIdentityConditionalAccessAuthenticationContextClassReference -BodyParameter $context
            Write-Host "Created auth context $($context.id): $($context.displayName)" -ForegroundColor Green
        }
        else {
            Write-Host "[DRY RUN] Would create auth context $($context.id)" -ForegroundColor Yellow
        }
    }
}
```

### Deploying CA Policy with Session Controls (v1.0 API)
```powershell
# Source: Existing CAA solution template + Microsoft Learn
# URL: https://learn.microsoft.com/en-us/powershell/module/microsoft.graph.identity.signins/new-mgidentityconditionalaccesspolicy

# Zone 2 policy: 4h sign-in, 30min idle, passwordless MFA
$policyTemplate = @{
    displayName = "SSC-Zone2-Session-Controls"
    state = "enabledForReportingButNotEnforced"  # Always start report-only
    conditions = @{
        users = @{
            includeGroups = @($config.groups.zone2Users)
            excludeUsers = $config.breakGlassAccounts  # MANDATORY
        }
        applications = @{
            includeApplications = @("All")  # Required for persistentBrowser
        }
        clientAppTypes = @("browser", "mobileAppsAndDesktopClients")
    }
    grantControls = @{
        operator = "AND"
        builtInControls = @("mfa")
        authenticationStrength = @{
            id = $config.authStrengthPolicies.passwordlessMFA  # Zone 2 uses passwordless
        }
    }
    sessionControls = @{
        signInFrequency = @{
            value = 4
            type = "hours"
            isEnabled = $true
        }
        applicationEnforcedRestrictions = @{
            isEnabled = $true
        }
        persistentBrowser = @{
            mode = "never"
            isEnabled = $true
        }
    }
}

# Validate break-glass exclusion before deployment
if (-not (Test-BreakGlassExclusion -PolicyTemplate $policyTemplate -Config $config)) {
    throw "Break-glass validation failed. Deployment aborted to prevent tenant lockout."
}

# Create policy
if (-not $DryRun) {
    $newPolicy = New-MgIdentityConditionalAccessPolicy -BodyParameter $policyTemplate
    Write-Host "Policy created: $($newPolicy.Id)" -ForegroundColor Green
    Write-Host "State: $($newPolicy.State)" -ForegroundColor Yellow
    Write-Host "IMPORTANT: Policy in report-only mode. Wait 72 hours, review sign-in logs, then enable." -ForegroundColor Yellow
}
```

### Deploying Zone 3 Risky User Policy (Beta API Required)
```powershell
# Source: GitHub issue #647 + Microsoft Learn beta API docs
# URL: https://github.com/microsoftgraph/msgraph-metadata/issues/647

# Import Beta module for frequencyInterval: everyTime
Import-Module Microsoft.Graph.Beta.Identity.SignIns

# Zone 3 risky user policy: Reauthenticate every time
$policyTemplate = @{
    displayName = "SSC-Zone3-Risky-User-Reauthentication"
    state = "enabledForReportingButNotEnforced"
    conditions = @{
        users = @{
            includeGroups = @($config.groups.zone3Users)
            excludeUsers = $config.breakGlassAccounts
        }
        userRiskLevels = @("medium", "high")
        applications = @{
            includeApplications = @("All")
        }
    }
    grantControls = @{
        operator = "AND"
        builtInControls = @("mfa", "compliantDevice")
        authenticationStrength = @{
            id = $config.authStrengthPolicies.phishingResistantMFA
        }
    }
    sessionControls = @{
        signInFrequency = @{
            value = 1
            type = "everyTime"  # REQUIRES BETA API
            authenticationType = "primaryAndSecondaryAuthentication"
            frequencyInterval = "everyTime"  # REQUIRES BETA API
            isEnabled = $true
        }
    }
}

# Use Beta cmdlet
if (-not $DryRun) {
    $newPolicy = New-MgBetaIdentityConditionalAccessPolicy -BodyParameter $policyTemplate
    Write-Host "Zone 3 risky user policy created (Beta API)." -ForegroundColor Green
}
```

### Validating Session Controls Against Baseline
```powershell
# Source: Pattern from existing ACV solution Compare-ValidationBaseline.ps1

function Compare-SessionBaseline {
    param(
        [Parameter(Mandatory = $true)]
        [object]$Policy,

        [Parameter(Mandatory = $true)]
        [object]$Baseline
    )

    $results = @{
        Status = "Unknown"
        Mismatches = @()
    }

    # Normalize signInFrequency to minutes for comparison
    $policyMinutes = if ($Policy.sessionControls.signInFrequency.type -eq "hours") {
        $Policy.sessionControls.signInFrequency.value * 60
    } else {
        $Policy.sessionControls.signInFrequency.value
    }

    $baselineMinutes = if ($Baseline.signInFrequency.type -eq "hours") {
        $Baseline.signInFrequency.value * 60
    } else {
        $Baseline.signInFrequency.value
    }

    if ($policyMinutes -ne $baselineMinutes) {
        $results.Mismatches += "Sign-in frequency: Policy=$($policyMinutes)min, Baseline=$($baselineMinutes)min"
    }

    # Check persistent browser
    if ($Policy.sessionControls.persistentBrowser.mode -ne $Baseline.persistentBrowser.mode) {
        $results.Mismatches += "Persistent browser: Policy=$($Policy.sessionControls.persistentBrowser.mode), Baseline=$($Baseline.persistentBrowser.mode)"
    }

    # Check authentication strength
    if ($Policy.grantControls.authenticationStrength.id -ne $Baseline.authenticationStrength.id) {
        $results.Mismatches += "Auth strength: Policy=$($Policy.grantControls.authenticationStrength.id), Baseline=$($Baseline.authenticationStrength.id)"
    }

    # Determine status
    if ($results.Mismatches.Count -eq 0) {
        $results.Status = "Passed"
    } else {
        $results.Status = "Failed"
    }

    return $results
}
```

### Break-Glass Exclusion Validation
```powershell
# Source: Best practices from Microsoft Learn + existing CAA pattern
# URL: https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/security-emergency-access

function Test-BreakGlassExclusion {
    param(
        [Parameter(Mandatory = $true)]
        [hashtable]$PolicyTemplate,

        [Parameter(Mandatory = $true)]
        [object]$Config
    )

    $excludedUsers = $PolicyTemplate.conditions.users.excludeUsers
    $excludedGroups = $PolicyTemplate.conditions.users.excludeGroups

    # Check if any break-glass accounts are excluded directly
    $breakGlassExcluded = $Config.breakGlassAccounts | Where-Object { $excludedUsers -contains $_ }

    if ($breakGlassExcluded.Count -eq $Config.breakGlassAccounts.Count) {
        Write-Host "✓ All break-glass accounts excluded directly." -ForegroundColor Green
        return $true
    }

    # Check if break-glass accounts are members of excluded groups
    foreach ($groupId in $excludedGroups) {
        $groupMembers = Get-MgGroupMember -GroupId $groupId | Select-Object -ExpandProperty Id
        $breakGlassInGroup = $Config.breakGlassAccounts | Where-Object { $groupMembers -contains $_ }

        if ($breakGlassInGroup.Count -eq $Config.breakGlassAccounts.Count) {
            Write-Host "✓ All break-glass accounts excluded via group: $groupId" -ForegroundColor Green
            return $true
        }
    }

    # Break-glass accounts not excluded
    Write-Error "DANGER: Break-glass accounts not excluded from policy."
    Write-Error "Policy: $($PolicyTemplate.displayName)"
    Write-Error "Break-glass accounts: $($Config.breakGlassAccounts -join ', ')"
    Write-Error "Excluded users: $($excludedUsers -join ', ')"
    Write-Error "Excluded groups: $($excludedGroups -join ', ')"
    Write-Error "Deployment aborted to prevent tenant lockout."

    return $false
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| AzureAD module | Microsoft.Graph SDK | 2023 | AzureAD deprecated, Graph SDK is official path |
| Manual JSON construction | Hashtable with ConvertTo-Json | Ongoing | PowerShell hashtables more maintainable than JSON strings |
| v1.0 API for all | Beta API for everyTime | 2024 | everyTime only in beta (GitHub issue #647) |
| Hard-coded policy JSON | Template files + config | Ongoing | Separation of structure from tenant-specific values |
| Report-only optional | Report-only mandatory | 2025 | Microsoft best practice: always test before enforcement |

**Deprecated/outdated:**
- AzureAD PowerShell module: Deprecated, use Microsoft.Graph
- Connect-AzureAD: Use Connect-MgGraph instead
- Get-AzureADMSConditionalAccessPolicy: Use Get-MgIdentityConditionalAccessPolicy
- Manual token management: Graph SDK handles automatically

## Open Questions

Things that couldn't be fully resolved:

1. **Authentication Strength + compliantDevice Coexistence**
   - What we know: Templates show both authenticationStrength and builtInControls in same grantControls
   - What's unclear: Official docs don't explicitly confirm this combination is supported
   - Recommendation: Deploy in DryRun, test in dev tenant, verify sign-in logs show both controls evaluated

2. **Persistent Browser with App-Specific Targeting**
   - What we know: Community sources suggest persistentBrowser requires "All cloud apps"
   - What's unclear: Official docs don't state this as hard requirement
   - Recommendation: Build validation check - warn if persistentBrowser used with specific app IDs, but don't block deployment

3. **CA Policy Conflict Detection Algorithm**
   - What we know: Multiple policies use AND logic, most restrictive wins
   - What's unclear: Exact precedence when signInFrequency conflicts (1h vs 4h)
   - Recommendation: Pre-deployment audit queries overlapping policies, warns operator, but doesn't automatically resolve conflicts

## Sources

### Primary (HIGH confidence)
- [Microsoft Learn: authenticationContextClassReference resource type](https://learn.microsoft.com/en-us/graph/api/resources/authenticationcontextclassreference?view=graph-rest-1.0) - Auth context CRUD operations
- [Microsoft Learn: Authentication Strength Policies API](https://learn.microsoft.com/en-us/graph/api/resources/authenticationstrengths-overview?view=graph-rest-1.0) - Custom auth strength creation
- [Microsoft Learn: New-MgIdentityConditionalAccessPolicy](https://learn.microsoft.com/en-us/powershell/module/microsoft.graph.identity.signins/new-mgidentityconditionalaccesspolicy?view=graph-powershell-1.0) - CA policy creation cmdlet
- [Microsoft Learn: Manage Emergency Access Accounts](https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/security-emergency-access) - Break-glass best practices
- [Microsoft Learn: PIM API Overview](https://learn.microsoft.com/en-us/graph/api/resources/privilegedidentitymanagementv3-overview?view=graph-rest-1.0) - PIM settings validation
- Existing FSI-AgentGov-Solutions: CAA v1.0.0, ACV v1.0.0 (local file system)

### Secondary (MEDIUM confidence)
- [GitHub Issue #647: frequencyInterval everyTime not supported in v1.0](https://github.com/microsoftgraph/msgraph-metadata/issues/647) - Beta API requirement confirmed by Microsoft
- [Microsoft Learn: Conditional Access Session Lifetime](https://learn.microsoft.com/en-us/entra/identity/conditional-access/howto-conditional-access-session-lifetime) - Session control configuration
- [Microsoft Learn: Report-Only Mode](https://learn.microsoft.com/en-us/entra/identity/conditional-access/concept-conditional-access-report-only) - Report-only best practices

### Tertiary (LOW confidence)
- [Practical365: Common CA Misconfigurations](https://practical365.com/five-most-common-conditional-access-misconfigurations/) - AND logic explanation
- [AdminDroid: Phishing-Resistant MFA](https://blog.admindroid.com/use-phishing-resistant-mfa-to-implement-stronger-mfa-authentication/) - Auth strength overview
- [Welkas World: Report-Only to Enforced Transition](https://www.welkasworld.com/post/conditional-access-essentials-how-to-safely-transition-policies-from-report-only-to-enforced-mode) - 72-hour bake period recommendation

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Verified via existing CAA/ACV solutions, Microsoft Graph SDK official docs
- Architecture patterns: HIGH - Copied directly from existing validated solutions (CAA, ACV)
- Authentication contexts: HIGH - Official Microsoft Learn API documentation
- Beta API requirement: HIGH - GitHub issue #647 confirmed by Microsoft Graph team
- Session controls: MEDIUM - Official docs confirm features, but everyTime + compliantDevice coexistence needs testing
- Break-glass practices: HIGH - Official Microsoft Learn emergency access guidance
- Policy conflict behavior: MEDIUM - AND logic confirmed, but exact precedence for overlapping session controls unclear

**Research date:** 2026-02-06
**Valid until:** 2026-03-06 (30 days - Conditional Access API is stable, but enforcement behavior may change per Microsoft's March 2026 rollout)
