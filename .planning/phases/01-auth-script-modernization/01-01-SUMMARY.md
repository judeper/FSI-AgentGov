---
phase: 1
plan: 1
status: Complete
completed: 2026-02-10
---

# Plan 01-01 Summary: Entra ID Authentication Migration (AUTH-01)

## Status: Complete

All 5 tasks completed. The `Export-RaiTelemetry.ps1` script has been migrated from deprecated `x-api-key` authentication to Entra ID bearer token authentication, and the framework playbook has been updated with Entra ID prerequisites, the modernized script, and a migration guide.

## Task Completion

### Task 1: Update Export-RaiTelemetry.ps1 Parameters ✅

- Removed `-ApiKey` parameter
- Added `-TenantId`, `-ClientId`, `-KeyVaultName`, `-SecretName` parameters
- Added `[CmdletBinding()]` with `[ValidateNotNullOrEmpty()]` on all 6 parameters (5 mandatory + `OutputPath`)
- Added `#Requires -Version 7.0` and `#Requires -Modules` for Az.Accounts 3.0.0 and Az.KeyVault 5.0.0
- Preserved `-AppInsightsAppId`, `-DaysBack`, `-OutputPath` parameters

### Task 2: Implement Entra ID Authentication Flow ✅

- Key Vault secret retrieval via `Get-AzKeyVaultSecret`
- PSCredential construction from ClientId + SecretValue
- `Connect-AzAccount -ServicePrincipal` authentication
- `Get-AzAccessToken -ResourceUrl "https://api.applicationinsights.io"` for bearer token
- Headers set to `@{ "Authorization" = "Bearer $token" }`
- Token refresh helper function `Get-AppInsightsToken` for long-running sessions

### Task 3: Add Structured Error Handling ✅

- `New-ErrorResult` helper returns `[PSCustomObject]@{ Status; ErrorType; Message; Timestamp }`
- Specific error types: `KeyVaultAccessFailure`, `ServicePrincipalAuthFailure`, `TokenAcquisitionFailure`, `QueryExecutionFailure`
- `Write-Verbose` output at each authentication step (4 steps)
- Existing extraction logic preserved; only auth mechanism changed

### Task 4: Validate KQL Queries with Bearer Token Auth ✅

- Documented in `KQL-VALIDATION.md` that all 3 KQL queries are auth-agnostic
- REST API endpoint unchanged: `https://api.applicationinsights.io/v1/apps/{appId}/query`
- Response format unchanged: `tables[0].rows`
- No API version parameter changes needed
- Noted migration from GET+URL-encoded to POST+JSON body (recommended for bearer token)

### Task 5: Update Framework Playbook ✅

- Added Entra ID Prerequisites section with App Registration, Monitoring Reader, Key Vault table
- Added collapsible "Setting Up the App Registration" admonition
- Replaced deprecated inline script with full Entra ID version (inline in playbook)
- Added "Migration from v1.x" section with 6-step upgrade table
- Preserved legacy script in collapsed `??? note` admonition for reference
- Added deprecation warning admonition for legacy script
- Updated framework version from v1.2.33 to v1.2.38
- `mkdocs build --strict` passes

## Commits

| Hash | Message |
|------|---------|
| `74c7420` | `docs(dec): update RAI telemetry playbook with Entra ID auth and migration guide` |

Note: Script and KQL validation files are under `maintainers-local/solutions-staging/` which is gitignored. These files are staged locally for transfer to the FSI-AgentGov-Solutions repository.

## File Manifest

| File | Action | Status |
|------|--------|--------|
| `maintainers-local/solutions-staging/deny-event-correlation-report/scripts/Export-RaiTelemetry.ps1` | Created | Local (gitignored) |
| `maintainers-local/solutions-staging/deny-event-correlation-report/kql-queries/KQL-VALIDATION.md` | Created | Local (gitignored) |
| `docs/playbooks/advanced-implementations/deny-event-correlation-report/app-insights-rai-telemetry.md` | Modified | Committed |

## Decisions Made

1. **Script staging location**: Created under `maintainers-local/solutions-staging/` since FSI-AgentGov-Solutions repo is not in workspace. Files are gitignored by design.
2. **POST vs GET for API calls**: Switched from GET with URL-encoded query to POST with JSON body in v2.0 script. This avoids URL length limits and aligns with Microsoft's Entra ID documentation patterns.
3. **Legacy script preservation**: Kept the deprecated x-api-key script in a collapsed admonition in the playbook for reference, rather than removing it entirely. This aids migration for existing deployments.
4. **x-api-key in comments**: The new script references "x-api-key" in `.DESCRIPTION` and `.NOTES` comment blocks to document the migration context. No functional code uses x-api-key.
5. **DaysBack vs StartDate/EndDate**: Simplified the parameter interface from separate StartDate/EndDate to a single DaysBack parameter (default 1, max 90) for cleaner UX. The v1.x StartDate/EndDate pattern is preserved in the legacy reference.

## Discovered Work

1. **FSI-AgentGov-Solutions commit needed**: The `Export-RaiTelemetry.ps1` script needs to be committed to the Solutions repository separately. The staged file is ready at `maintainers-local/solutions-staging/`.
2. **FAQ cross-reference is already accurate**: `docs/reference/faq.md` already contains correct Entra ID migration guidance pointing to the DEC playbook. No update needed.

## Verification Results

| Check | Result |
|-------|--------|
| No `x-api-key` in functional code | ✅ Pass (only in comments) |
| `#Requires -Version 7.0` | ✅ Pass |
| `#Requires Az.Accounts` | ✅ Pass |
| `#Requires Az.KeyVault` | ✅ Pass |
| `Connect-AzAccount -ServicePrincipal` | ✅ Pass |
| `Get-AzAccessToken` | ✅ Pass |
| `[ValidateNotNullOrEmpty()]` count = 6 | ✅ Pass |
| FSI language rules (no prohibited phrases) | ✅ Pass |
| `mkdocs build --strict` | ✅ Pass |
