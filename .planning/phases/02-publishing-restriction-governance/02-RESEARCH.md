# Phase 2 Research: Publishing Restriction Governance

## Overview

Research for building `restrict-agent-publishing.ps1` — a PowerShell governance script that validates 6 publishing restriction criteria with SHA-256 evidence export, and integrating those checks into the existing hardening baseline.

## 1. Existing Script Conventions

All governance scripts in `scripts/governance/` follow consistent patterns established in Phase 1 research. The same conventions apply here:

### Parameter Pattern
```powershell
#Requires -Version 7.0
#Requires -Modules @{ ModuleName = 'Microsoft.PowerApps.Administration.PowerShell'; ModuleVersion = '2.0.0' }

[CmdletBinding(SupportsShouldProcess)]
param(
    [ValidateSet('Table', 'JSON', 'Object')]
    [string]$OutputFormat = 'Table',
    [string]$OutputPath,
    [string[]]$EnvironmentFilter,
    [hashtable]$ZoneMapping,
    [switch]$IncludeEvidence
)
```

### Structure Pattern
1. Banner (Write-Host with box drawing)
2. WhatIf preview (ShouldProcess)
3. Helper functions (result builders, API wrappers)
4. Initialize results (Generic List collections)
5. Check groups (numbered steps)
6. Results aggregation (PSCustomObject with Metadata/Summary/Checks/Gaps)
7. SHA-256 evidence hash (optional)
8. Console summary banner
9. Output switch (JSON/Table/Object)

### Output Object Structure
Same as `Invoke-HardeningBaselineCheck.ps1` and `Test-AgentAuthConfiguration.ps1`:
```powershell
[PSCustomObject]@{
    Metadata = [PSCustomObject]@{
        CheckedAt           = $startTime
        ScriptVersion       = '1.0.0'
        EnvironmentsScanned = $envCount
        DurationSeconds     = [math]::Round($duration, 2)
        IntegrityHash       = $null
    }
    Summary = [PSCustomObject]@{
        TotalChecks   = $totalChecks
        Passed        = $passCount
        Failed        = $failCount
        Skipped       = $skipCount
        OverallStatus = 'Passed' | 'GapsFound'
    }
    Checks = $allChecks.ToArray()
    Gaps   = $gaps.ToArray()
}
```

## 2. The 6 Publishing Restriction Criteria

From the todo source and Control 1.1 documentation:

| # | Criterion | What It Validates | API Source | Check Scope |
|---|-----------|-------------------|-----------|-------------|
| 1 | Environment Maker role removal | "All Users" group removed from Environment Maker role per environment | `Get-AdminPowerAppEnvironmentRoleAssignment` | Per-environment |
| 2 | Authorized security groups | `FSI-Agent-Makers-*` security groups assigned to correct environments | `Get-AdminPowerAppEnvironment` properties | Per-environment |
| 3 | Share with Everyone disabled | Tenant setting disabled to prevent agents from being shared with everyone | `Get-TenantSettings` → sharing toggle | Tenant-level |
| 4 | DLP connector blocking | DLP policy blocks agent publishing connector in default environment | `Get-AdminDlpPolicy` | Tenant/environment |
| 5 | Managed Environment sharing limits | Managed Environment sharing limits configured per zone thresholds | Environment governance settings | Per-environment |
| 6 | Approval workflow active (Zone 2/3) | Agent publishing approval workflow exists and is active for Zone 2/3 environments | Power Automate flow check or manual | Per-environment (Zone 2/3) |

### Zone-Based Logic

| Criterion | Zone 1 | Zone 2 | Zone 3 |
|-----------|--------|--------|--------|
| 1 (Env Maker removal) | Warning (recommended) | Fail (required) | Fail (required) |
| 2 (Security groups) | Pass (optional) | Fail (required) | Fail (required) |
| 3 (Share with Everyone) | Warning | Fail | Fail |
| 4 (DLP blocking) | Pass (not required) | Fail (required) | Fail (required) |
| 5 (Sharing limits) | Warning (recommended) | Fail (required) | Fail (must be most restrictive) |
| 6 (Approval workflow) | Pass (not required) | Fail (required) | Fail (required) |

## 3. API Patterns for Each Criterion

### Criterion 1: Environment Maker Role Removal

```powershell
# Get role assignments for an environment
$roleAssignments = Get-AdminPowerAppEnvironmentRoleAssignment -EnvironmentName $envId

# Check if "All Users" has Environment Maker role
# The "00000000-0000-0000-0000-000000000000" principal represents the org-wide group
$allUsersEnvMaker = $roleAssignments | Where-Object {
    $_.PrincipalObjectId -eq '00000000-0000-0000-0000-000000000000' -and
    $_.RoleDefinition.RoleName -eq 'Environment Maker'
}
```

**Risk:** The principal ID for "All Users" may vary. The script should also look for display name patterns ("All Users", "Everyone", tenant-wide group).

### Criterion 2: Authorized Security Groups

```powershell
# Environment security group is in properties
$env = Get-AdminPowerAppEnvironment -EnvironmentName $envId
$securityGroupId = $env.Internal.properties.securityGroupId

# Verify the group matches expected FSI-Agent-Makers-* pattern
# Requires Graph API call to resolve group name
$token = Get-AzAccessToken -ResourceUrl 'https://graph.microsoft.com'
$group = Invoke-RestMethod -Uri "https://graph.microsoft.com/v1.0/groups/$securityGroupId" `
    -Headers @{ Authorization = "Bearer $($token.Token)" }
$groupName = $group.displayName
# Check against pattern
$isAuthorized = $groupName -match '^FSI-Agent-Makers-'
```

**Risk:** Graph API call required to resolve group name. May need `Group.Read.All` permission. Fallback: report group ID only with recommendation to verify manually.

### Criterion 3: Share with Everyone

```powershell
$tenantSettings = Get-TenantSettings
# The exact property path for "share agents with everyone" toggle
$shareWithEveryoneDisabled = $tenantSettings.powerPlatform.copilotStudio.shareWithEveryoneDisabled
# Or similar property path — may also be:
$shareSettting = $tenantSettings.powerPlatform.powerApps.disableShareWithEveryone
```

**Risk:** Property path may vary by tenant configuration version. Script should check multiple paths.

### Criterion 4: DLP Connector Blocking

```powershell
# Get DLP policies
$dlpPolicies = Get-AdminDlpPolicy

# Check if "HTTP" and/or "Microsoft Copilot Studio" connectors are blocked
# DLP policies have business/non-business/blocked connector groups
foreach ($policy in $dlpPolicies) {
    $blockedConnectors = $policy.connectorGroups | Where-Object { $_.classification -eq 'Blocked' }
    # Check for relevant connectors in blocked group
}
```

**Risk:** DLP policy structure is complex with multiple connector group classifications. The specific connector names for agent publishing may include "Microsoft Copilot Studio", "HTTP", and others. Semi-automated check — validate policy exists and has blocked connectors, but exact connector list may need manual verification.

### Criterion 5: Managed Environment Sharing Limits

```powershell
# Managed Environment settings include sharing limits
$env = Get-AdminPowerAppEnvironment -EnvironmentName $envId
$governanceConfig = $env.Internal.properties.governanceConfiguration

# Check managed environment status and sharing limits
$isManagedEnv = $governanceConfig.protectionLevel -eq 'Standard' # or 'Managed'
$sharingLimit = $governanceConfig.settings.extendedSettings.sharingControlLimit
```

**Zone thresholds:**
- Zone 1: No limit required (recommend managedEnvironment enabled)
- Zone 2: Sharing limit ≤ 20 users
- Zone 3: Sharing limit ≤ 5 users (most restrictive)

**Risk:** Property paths may differ based on Power Platform API version. The `governanceConfiguration` object structure needs runtime validation.

### Criterion 6: Approval Workflow Active

This is the hardest to automate. Two approaches:

**Approach A: Check for Power Automate flow with naming convention**
```powershell
# Look for flows matching approval workflow naming pattern
# Requires Power Automate management API
$flows = Get-AdminFlow -EnvironmentName $envId
$approvalFlows = $flows | Where-Object {
    $_.DisplayName -match 'agent.*publish.*approval|publishing.*approval'
}
```

**Approach B: Semi-automated — report managed environment maker onboarding setting**
- Check if maker onboarding is enabled, which includes approval as part of environment access
- Report status as "Semi-Automated" — admin must verify approval workflow specifics

**Decision:** Use Approach B (semi-automated). Exact approval workflow validation requires knowing the specific flow name/pattern in each tenant. The script checks whether environment maker onboarding is configured (proxy for approval process) and reports that + manual verification guidance.

## 4. Hardening Baseline Integration (Items 1-6)

The current `Invoke-HardeningBaselineCheck.ps1` validates items 7-9, 14-17, 28-32 (12 items). Items 1-6 are currently "Manual Attestation":

| Baseline Item | Publishing Criterion | Current Status | Target Status |
|---------------|---------------------|----------------|---------------|
| 1 | Env Maker role removal | Manual Attestation | Automated |
| 2 | Security groups assigned | Manual Attestation | Semi-Automated (requires Graph for name resolution) |
| 3 | Share with Everyone disabled | Manual Attestation | Automated |
| 4 | DLP connector blocking | Manual Attestation | Semi-Automated (policy exists, connector list needs verification) |
| 5 | Managed Env sharing limits | Manual Attestation | Automated |
| 6 | Approval workflow active | Manual Attestation | Semi-Automated (checks proxy indicators) |

### Integration Approach

Two options for integration:

**Option A: Add items 1-6 directly into `Invoke-HardeningBaselineCheck.ps1`**
- Pro: Single script covers all 32 items
- Con: Makes the script significantly larger; mixes per-environment checks with publishing-specific checks

**Option B: Keep `restrict-agent-publishing.ps1` standalone, add cross-reference in hardening baseline**
- Pro: Modular scripts; each focused on its domain
- Con: Two scripts need to run for full baseline coverage

**Decision:** Option B (standalone + cross-reference). The hardening baseline script gets a new check group that:
1. Updates the item metadata for items 1-6 with new status (Automated/Semi-Automated)
2. Adds references to `restrict-agent-publishing.ps1` in the script's documentation
3. Optionally calls `restrict-agent-publishing.ps1` and incorporates results (if the script is available)

### Modification to `Invoke-HardeningBaselineCheck.ps1`

Add a new check group near the top (before existing Check Group 1):

```powershell
# ═══════════════════════════════════════════════════════════════════════
# Check Group 0: Agent Publishing Restrictions (Items 1-6)
# Cross-reference: restrict-agent-publishing.ps1
# ═══════════════════════════════════════════════════════════════════════

# Check if restrict-agent-publishing.ps1 exists and can provide results
$publishingScriptPath = Join-Path $PSScriptRoot 'restrict-agent-publishing.ps1'
if (Test-Path $publishingScriptPath) {
    # Script exists — items 1-6 are now Automated/Semi-Automated
    # Add informational results referencing the dedicated script
    1..6 | ForEach-Object {
        $status = switch ($_) {
            { $_ -in 1, 3, 5 } { 'Automated' }
            { $_ -in 2, 4, 6 } { 'Semi-Automated' }
        }
        $allChecks.Add((New-CheckResult -ItemNumber $_ -Setting "Agent publishing restriction $_" `
            -CheckGroup 'AgentPublishing' -Status 'Pass' `
            -Message "Validated by restrict-agent-publishing.ps1 ($status)"))
    }
} else {
    # Script doesn't exist — still manual attestation
    1..6 | ForEach-Object {
        $allChecks.Add((New-CheckResult -ItemNumber $_ -Setting "Agent publishing restriction $_" `
            -CheckGroup 'AgentPublishing' -Status 'Skip' `
            -Message 'Manual attestation required — restrict-agent-publishing.ps1 not found'))
    }
}
```

## 5. Evidence Export Pattern

Same SHA-256 pattern established in Phase 1 and existing scripts:

```powershell
if ($IncludeEvidence) {
    $resultsJson = $results | ConvertTo-Json -Depth 10 -Compress
    $hashBytes = [System.Security.Cryptography.SHA256]::Create().ComputeHash(
        [System.Text.Encoding]::UTF8.GetBytes($resultsJson)
    )
    $results.Metadata.IntegrityHash = [BitConverter]::ToString($hashBytes) -replace '-'
}
```

Per-check evidence hashing follows the same pattern as `Test-AgentAuthConfiguration.ps1`:
- Serialize the raw API response for each check to JSON
- Compute SHA-256 over that JSON
- Store as `EvidenceHash` property on each check result

## 6. Risks and Dependencies

| Risk | Impact | Mitigation |
|------|--------|------------|
| DLP policy structure complexity | May not correctly identify blocked connectors | Semi-automated: validate policy exists, manual connector verification |
| Graph API permission for group name resolution | Cannot verify FSI-Agent-Makers-* pattern | Fallback to reporting group ID; recommend manual verification |
| Approval workflow detection | No standard naming pattern for flows | Semi-automated: check proxy indicators (maker onboarding config) |
| Managed Environment property path variations | governanceConfiguration may not exist on all environments | Graceful Skip with informational message |
| Hardening baseline script changes | Integration could break existing checks | Minimal changes: add cross-reference group, don't modify existing check groups |

### Dependencies
- `Az.Accounts` module for token acquisition
- `Microsoft.PowerApps.Administration.PowerShell` 2.0.0+ for environment/DLP queries
- Optional: `Microsoft.Graph` module for group name resolution (Criterion 2)

## 7. Recommended Approach

### Script Structure for `restrict-agent-publishing.ps1`
1. **Parameters**: Same convention (`OutputFormat`, `OutputPath`, `EnvironmentFilter`, `ZoneMapping`, `IncludeEvidence`)
2. **Helper functions**: `Get-EnvironmentZone` (reuse pattern), `New-PublishingCheckResult` builder
3. **Check groups**:
   - Group 1: Tenant-level checks (Criterion 3: Share with Everyone) — single call
   - Group 2: Per-environment checks (Criteria 1, 2, 5: env maker role, security groups, sharing limits)
   - Group 3: DLP policy checks (Criterion 4) — may span multiple policies
   - Group 4: Approval workflow checks (Criterion 6) — Zone 2/3 only, semi-automated
4. **Evidence**: Per-check evidence hash + overall integrity hash
5. **Output**: Standard Metadata/Summary/Checks/Gaps structure

### Hardening Baseline Modification
- Add Check Group 0 for items 1-6 cross-reference
- Update script description in comment-based help to mention "18 items" (was 12)
- Keep existing check groups untouched

### File Plan
- **Created**: `scripts/governance/restrict-agent-publishing.ps1`
- **Modified**: `scripts/governance/Invoke-HardeningBaselineCheck.ps1` (items 1-6 cross-reference)

---
*Research completed: 2026-02-12*
*Researcher: Copilot*
