---
phase: 1
plan: 2
status: Complete
completed: 2026-02-10
---

# Plan 01-02 Summary: DECClient.psm1 Shared Module (AUTH-02)

## Status: Complete

All 8 tasks completed. The `DECClient.psm1` shared module has been created with centralized authentication helpers for three data sources (ExchangeOnline, Application Insights, Dataverse), connection management with token caching and refresh, reusable extraction functions, environment variable handling with `DEC_` prefix, and Phase 2 stubs.

## Task Completion

### Task 1: Create Module Manifest and Structure ✅

- Created `scripts/private/DECClient.psm1` with full module scaffold
- Defined module-level variables: `$script:ExoConnection`, `$script:AiToken`, `$script:AiTokenExpiry`, `$script:DvConnection`, `$script:EnvVarCache`, `$script:ModuleVersion`
- 11 functions defined (2 private helpers + 9 exported)
- Private helpers: `New-DECErrorResult`, `Test-DECTokenValid`
- Module follows v6-v8 AAMClient/CMMClient/FUSClient pattern with `#Requires -Version 7.0`

### Task 2: Implement Connect-DECServices (Master Connection) ✅

- Accepts `-TenantId`, `-ClientId`, `-KeyVaultName`, `-Services` (ValidateSet array), `-CertificateThumbprint`
- Calls `Connect-DECExchangeOnline`, `Connect-DECAppInsights`, `Connect-DECDataverse` based on `-Services` parameter
- Returns `[PSCustomObject]@{ ExchangeOnline; AppInsights; Dataverse; Errors; Timestamp }`
- Logs connection status via `Write-Verbose` for each service
- `-DryRun` switch validates Key Vault access without establishing connections

### Task 3: Implement Connect-DECExchangeOnline ✅

- Supports both certificate-based auth (`-CertificateThumbprint`) and client secret auth via Key Vault
- Retrieves credentials from Key Vault using `Get-AzKeyVaultSecret`
- Calls `Connect-ExchangeOnline` with `-AppId`, `-Organization` parameters
- Stores connection state in `$script:ExoConnection` with metadata (TenantId, ClientId, AuthType, Timestamp)
- Returns cached connection if already active; `-Force` triggers reconnection
- Handles failures with structured `New-DECErrorResult` response

### Task 4: Implement Connect-DECAppInsights ✅

- Authenticates via `Connect-AzAccount -ServicePrincipal` (reuses Plan 01-01 Export-RaiTelemetry.ps1 pattern)
- Obtains token via `Get-AzAccessToken -ResourceUrl "https://api.applicationinsights.io"`
- Caches token in `$script:AiToken` and expiry in `$script:AiTokenExpiry`
- `Test-DECTokenValid` private function checks expiry with 5-minute buffer using `[DateTimeOffset]` arithmetic
- Skips re-auth when cached token is valid; `-Force` triggers refresh

### Task 5: Implement Invoke-DECAppInsightsQuery ✅

- Accepts `-AppInsightsAppId`, `-Query`, `-Timespan` (ISO 8601 duration, defaults to 'P1D')
- Checks token validity; auto-refreshes via `Connect-DECAppInsights` if expired
- Executes `Invoke-RestMethod` POST against `https://api.applicationinsights.io/v1/apps/{appId}/query`
- Parses `response.tables[0].rows` into PowerShell objects with column headers mapped
- Retry logic: 3 attempts with exponential backoff (2^attempt seconds) for HTTP 429 and 503
- Returns `[PSCustomObject]@{ Status; RowCount; Data; Query; Duration }` with `[Stopwatch]` timing

### Task 6: Implement Get-DECEnvironmentVariable ✅

- Phase 1 default: reads from `$env:DEC_*` local process environment variables via `[System.Environment]::GetEnvironmentVariables()`
- Phase 2 Dataverse path documented in comments (environmentvariabledefinition / environmentvariablevalue tables)
- Caches values in `$script:EnvVarCache` for session lifetime; `-Force` bypasses cache
- Returns `[hashtable]` of key-value pairs
- Warns about missing required variables: `DEC_AppInsightsAppId`, `DEC_KeyVaultName`, `DEC_TenantId`, `DEC_ClientId`
- `-RequiredOnly` switch filters to the four required variables

### Task 7: Define Phase 2 Stub Functions ✅

All 4 stubs created with complete `[CmdletBinding()]`, `[OutputType()]`, and full parameter declarations:

| Function | Parameters | Throws |
|----------|-----------|--------|
| `Connect-DECDataverse` | TenantId, ClientId, KeyVaultName, EnvironmentUrl, SecretName | "Not implemented — requires Phase 2" |
| `Write-DECDenyEvent` | AgentId, SessionId, FilterReason, FilterCategory, FilterSeverity, EventTimestamp, ZoneClassification, AdditionalProperties | "Not implemented — requires Phase 2" |
| `Write-DECCorrelation` | DenyEventId, AuditRecordId, DlpPolicyMatchId, CorrelationType, ConfidenceScore, CorrelationDetails | "Not implemented — requires Phase 2" |
| `Write-DECValidationHistory` | ValidationRunId, ValidationType, RecordsProcessed, RecordsPassed, RecordsFailed, ValidationDetails, RunTimestamp | "Not implemented — requires Phase 2" |

### Task 8: Create Solution Scaffold ✅

- Created directory structure: `scripts/private/`, `kql-queries/` (existing), `templates/`, `docs/`
- Created `templates/deny-event-baseline.json` with default configuration values (data sources, auth methods, governance zones, RAI telemetry settings)
- Created `README.md` at solution root and `docs/README.md` with usage examples and staging status
- Existing files preserved: `scripts/Export-RaiTelemetry.ps1`, `kql-queries/KQL-VALIDATION.md`

## Commits

No commits required — all files are under `maintainers-local/solutions-staging/` which is gitignored. Planning artifacts (this SUMMARY.md) will be committed separately.

## File Manifest

| File | Action | Status |
|------|--------|--------|
| `maintainers-local/solutions-staging/deny-event-correlation-report/scripts/private/DECClient.psm1` | Created | Local (gitignored) |
| `maintainers-local/solutions-staging/deny-event-correlation-report/templates/deny-event-baseline.json` | Created | Local (gitignored) |
| `maintainers-local/solutions-staging/deny-event-correlation-report/docs/README.md` | Created | Local (gitignored) |
| `maintainers-local/solutions-staging/deny-event-correlation-report/README.md` | Created | Local (gitignored) |
| `.planning/phases/01-auth-script-modernization/01-02-SUMMARY.md` | Created | To commit |

## Decisions Made

1. **Single module file:** All functions consolidated into one `DECClient.psm1` file rather than separate .ps1 files per function. This matches the established v6-v8 pattern (AAMClient/CMMClient are single-file modules) and simplifies `Import-Module`.

2. **Private helpers not exported:** `New-DECErrorResult` and `Test-DECTokenValid` are module-scoped private functions. They are used internally but not exposed via `Export-ModuleMember`, keeping the public API to 9 functions.

3. **ExchangeOnline dual auth:** Supports both certificate-based (`-CertificateThumbprint`) and client secret auth, with certificate as preferred. The plan specified "certificate-based or app-only" — implemented both with Key Vault fallback for client secrets.

4. **No `git mv` for existing files:** Plan Task 8 mentioned "Move existing scripts to correct locations (preserve git history with `git mv`)" but since files are in gitignored `maintainers-local/`, git history doesn't apply. Files are already in correct locations from Plan 01-01.

5. **No CHANGELOG.md update:** Plan mentioned updating `CHANGELOG.md` but this applies to FSI-AgentGov-Solutions repo which is not in workspace. Noted for transfer.

6. **No Connect-EnvironmentDataverse.ps1 / Get-ZoneClassification.ps1 copy:** These utilities are from v6-v8 repos not available in workspace. The `Connect-DECDataverse` stub documents the pattern and Phase 2 will implement the actual Dataverse connection.

## Discovered Work

1. **Token expiry type handling:** `Get-AzAccessToken` returns `ExpiresOn` as `[DateTimeOffset]`. The `Test-DECTokenValid` function uses `[DateTimeOffset]` arithmetic for proper UTC comparison. This is important for long-running sessions.

2. **Retry scope limitation:** The retry logic in `Invoke-DECAppInsightsQuery` only handles HTTP 429/503. Other transient errors (network timeouts, DNS failures) are not retried. Phase 2 may want to expand the retry scope.

3. **ExchangeOnline connection caching:** Unlike App Insights tokens which have explicit expiry, ExchangeOnline sessions don't expose expiry metadata. The current implementation caches the connection object but relies on `-Force` for reconnection. A heartbeat check could be added in Phase 2.
