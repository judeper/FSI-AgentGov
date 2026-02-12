# Phase 1 Research: Agent Authentication Enforcement

## Overview

Research for building `Test-AgentAuthConfiguration.ps1` — a PowerShell script that validates 6 SSPM items for per-agent authentication configuration with zone-based logic and drift detection.

## 1. Existing Script Conventions

All governance scripts in `scripts/governance/` follow consistent patterns:

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

### Error Handling
- `try/catch` per check group
- Failed API calls produce `Status = 'Skip'` results (not terminating errors)
- `Write-Warning` for recoverable errors, `Write-Error` + return for fatal

### Output Object Structure
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

## 2. SSPM-1.1 Items (6 Checks)

From the SSPM alert mapping and Control 1.1 verification criteria:

| SSPM ID | Alert | What It Validates | API Source | Severity |
|---------|-------|-------------------|-----------|----------|
| SSPM-1.1-01 | Agent authentication mode ≠ "No Authentication" | Ref 6: `Agent's Security Authentication Should Not Be 'No Authentication'` | Per-agent bot metadata | High |
| SSPM-1.1-02 | Manual auth requires sign-in | Ref 5: `Agent's Authentication Should Be Set To Authenticate Manually` (with sign-in toggle) | Per-agent bot settings | High |
| SSPM-1.1-03 | Auth enforcement timing = "Always" | Ref 3: `Agent Level Authentication Should Be Set To 'Always'` | Per-agent auth config | High |
| SSPM-1.1-04 | Sharing scope is not "Anyone" | Ref 4: `Agent Should Not Be Shared With Everyone` | Per-agent permissions (same as Invoke-SharingAudit) | High |
| SSPM-1.1-05 | AI feature publishing toggle disabled (Zone 2/3) | Ref 29: `The Option 'Publish Bots With AI Features' Should Be Disabled` | Tenant settings | High |
| SSPM-1.1-06 | Unapproved agent blocking enabled | Ref 34: `Shared agents which are not approved by admin should be blocked` | M365 Admin Center API | High |

### Zone-Based Logic

| SSPM Check | Zone 1 | Zone 2 | Zone 3 |
|-----------|--------|--------|--------|
| SSPM-1.1-01 (No Auth) | Fail (all zones) | Fail | Fail |
| SSPM-1.1-02 (Sign-in) | Warning | Fail | Fail |
| SSPM-1.1-03 (Always) | Warning | Fail | Fail |
| SSPM-1.1-04 (Anyone) | Warning | Fail | Fail |
| SSPM-1.1-05 (AI Pub) | Pass (allowed) | Fail (must be disabled) | Fail (must be disabled) |
| SSPM-1.1-06 (Block) | Warning | Fail | Fail |

## 3. BAP/PPAC API Patterns

### Authentication
```powershell
$token = Get-AzAccessToken -ResourceUrl "https://api.bap.microsoft.com" -ErrorAction Stop
$headers = @{ Authorization = "Bearer $($token.Token)"; 'Content-Type' = 'application/json' }
```

### Environment Enumeration
```
GET https://api.bap.microsoft.com/providers/Microsoft.BusinessAppPlatform/scopes/admin/environments?api-version=2016-11-01
```
Returns `{ value: [ { name: envGuid, properties: { displayName: ... } } ] }`

### Agent (Bot) Enumeration
```
GET https://api.bap.microsoft.com/providers/Microsoft.BusinessAppPlatform/environments/{envId}/bots?api-version=2021-04-01
```
Returns `{ value: [ { name: botGuid, properties: { displayName: ..., ... } } ] }`

### Agent Permissions (Sharing Principals)
```
GET https://api.bap.microsoft.com/providers/Microsoft.BusinessAppPlatform/environments/{envId}/bots/{botId}/permissions?api-version=2021-04-01
```
Returns principal array with `principalType` (Organization/Tenant/Public/Group/User)

### Agent Authentication Configuration
The BAP API exposes bot metadata. The auth properties are expected at:
- `properties.configuration.authenticationMode` — "NoAuthentication", "MicrosoftEntraId", "Manual"
- `properties.configuration.requireUserAuthentication` — boolean
- `properties.configuration.authenticationTiming` — "Always", "AsNeeded"
- or via Copilot Studio bot components REST API

**Risk:** The exact property paths for auth configuration are not fully documented in public Microsoft Learn docs. The script should include a discovery mode that dumps raw bot properties for verification, and handle missing properties gracefully with `Skip` status.

### Tenant Settings (existing pattern)
```powershell
$tenantSettings = Get-TenantSettings
$tenantSettings.powerPlatform.copilotStudio.publishBotsWithAIFeatures  # SSPM-1.1-05
```

## 4. Drift Detection Pattern

No established drift detection exists in the current governance scripts. The approach should follow industry patterns:

### Baseline Storage
- Save scan results as JSON baseline file
- Next scan compares current state against baseline
- Delta report shows changed agents

### Implementation Pattern
```powershell
param(
    [string]$BaselinePath  # Path to previous scan JSON
)

# Load previous baseline
$previousBaseline = if (Test-Path $BaselinePath) {
    Get-Content $BaselinePath -Raw | ConvertFrom-Json
} else { $null }

# After current scan, compare
$drifts = Compare-AgentAuthBaseline -Current $currentChecks -Previous $previousBaseline
```

### Drift Types
- `NewAgent` — agent exists in current scan but not baseline
- `RemovedAgent` — agent in baseline but not current scan
- `SettingChanged` — auth setting changed from baseline value
- `StatusChanged` — check result changed (Pass→Fail, Fail→Pass)

## 5. Evidence Export Pattern (SHA-256)

Established pattern from both HardeningBaseline and SharingAudit:

```powershell
if ($IncludeEvidence) {
    $resultsJson = $results | ConvertTo-Json -Depth 10 -Compress
    $hashBytes = [System.Security.Cryptography.SHA256]::Create().ComputeHash(
        [System.Text.Encoding]::UTF8.GetBytes($resultsJson)
    )
    $results.Metadata.IntegrityHash = [BitConverter]::ToString($hashBytes) -replace '-'
}
```

## 6. Hardening Baseline Items 1-6

The current `Invoke-HardeningBaselineCheck.ps1` covers items 7-9, 14-17, 28-32 (12 items). Items 1-6 are NOT automated — they map to the 6 SSPM-1.1 checks:

| Baseline Item | SSPM Check | Current Status |
|---------------|-----------|----------------|
| 1 | SSPM-1.1-01 (No auth mode) | Manual Attestation |
| 2 | SSPM-1.1-02 (Sign-in required) | Manual Attestation |
| 3 | SSPM-1.1-03 (Auth timing Always) | Manual Attestation |
| 4 | SSPM-1.1-04 (Sharing not Anyone) | Manual Attestation |
| 5 | SSPM-1.1-05 (AI pub disabled) | Manual Attestation |
| 6 | SSPM-1.1-06 (Unapproved blocking) | Manual Attestation |

After Phase 1, items 1-4 become "Automated" (per-agent BAP API). Items 5-6 are tenant-level checks — item 5 automated, item 6 semi-automated (requires M365 Admin Center API which may have limited programmatic access).

## 7. Risks and Dependencies

| Risk | Impact | Mitigation |
|------|--------|------------|
| BAP API bot auth properties undocumented | May not return expected fields | Include property discovery mode; graceful Skip for missing fields |
| M365 Admin Center agent blocking API | SSPM-1.1-06 may not be programmatically queryable | Mark as Semi-Automated; provide manual check guidance |
| Rate limiting on BAP API | Large tenants with many agents could hit throttling | Implement retry with exponential backoff |
| Auth config property path variations | Different bot types may store auth differently | Flexible property extraction with fallbacks |
| Module dependency | Requires Microsoft.PowerApps.Administration.PowerShell 2.0.0+ | Already established; same as HardeningBaseline |

### Dependencies
- `Az.Accounts` module for BAP API token acquisition (established pattern)
- `Microsoft.PowerApps.Administration.PowerShell` 2.0.0+ for environment enumeration
- Existing `Get-BapApiToken` and `Invoke-BapApi` patterns from `Invoke-SharingAudit.ps1`

## 8. Recommended Approach

### Script Structure
1. **Parameters**: Follow established convention (`OutputFormat`, `OutputPath`, `EnvironmentFilter`, `ZoneMapping`, `IncludeEvidence`) plus new `BaselinePath` for drift detection
2. **Helper functions**: Reuse `Get-BapApiToken`, `Invoke-BapApi` patterns from SharingAudit; add `New-AuthCheckResult` builder
3. **Check groups**:
   - Group 1: Tenant-level checks (SSPM-1.1-05, SSPM-1.1-06) — single API call
   - Group 2: Per-agent checks (SSPM-1.1-01 through SSPM-1.1-04) — iterate environments → agents
4. **Drift detection**: Load baseline, compare per-agent, output delta
5. **Evidence**: SHA-256 hash on final results JSON
6. **Output**: Standard Metadata/Summary/Checks/Gaps/Drifts structure

### File Plan
- **Created**: `scripts/governance/Test-AgentAuthConfiguration.ps1`
- **Not modified**: No existing files changed in Phase 1 (hardening baseline integration is Phase 2/4)

## 9. API Property Research Notes

### Bot Properties via BAP API
The `/bots` endpoint returns bot objects with `properties` containing:
- `displayName` — agent display name
- `botId` — unique identifier
- `schemaName` — internal schema reference
- `state` — published/draft status

The auth-related properties are exposed through the bot's component model, potentially at:
- `properties.configuration.authentication` — authentication settings object
- `properties.authenticationTrigger` — auth timing setting

The script should first dump raw bot properties on a test agent to discover the exact paths, then hardcode them with fallback chains.

---
*Research completed: 2026-02-12*
*Researcher: Copilot*
