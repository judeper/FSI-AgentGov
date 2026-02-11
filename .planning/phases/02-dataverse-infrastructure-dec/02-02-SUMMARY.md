---
phase: 02-dataverse-infrastructure-dec
plan: 02
subsystem: deny-event-correlation-report
tags: [dataverse, powershell, ingestion, batch, deny-events, odata]

# Dependency graph
requires: [02-01]
provides:
  - artifact: scripts/private/DECClient.psm1
    capability: "Connect-DECDataverse (Key Vault + SP auth), Write-DECDenyEvent (OData POST with retry), Write-DECDenyEventBatch ($batch endpoint), Test-DECDataverseTokenValid helper"
  - artifact: scripts/Export-CopilotDenyEvents.ps1
    capability: "Dataverse ingestion of CopilotInteraction deny events via -WriteToDataverse switch"
  - artifact: scripts/Export-DlpCopilotEvents.ps1
    capability: "Dataverse ingestion of DLP Copilot events via -WriteToDataverse switch"
  - artifact: scripts/Export-RaiTelemetry.ps1
    capability: "Dataverse ingestion of RAI telemetry events via -WriteToDataverse switch"
  - artifact: scripts/Invoke-DailyDenyReport.ps1
    capability: "Orchestrated Dataverse ingestion across all 3 sources via -WriteToDataverse switch"
affects:
  - phase-02-plans: [02-03]
    reason: "Correlation engine depends on deny events being written to fsi_denyevent table"

# Tech tracking
tech-stack:
  added: [odata-batch, multipart-mixed]
  patterns: [exponential-backoff, auto-reconnect, option-set-mapping, splatting, batch-fallback]

key-files:
  modified:
    - maintainers-local/solutions-staging/deny-event-correlation-report/scripts/private/DECClient.psm1
    - maintainers-local/solutions-staging/deny-event-correlation-report/scripts/Export-CopilotDenyEvents.ps1
    - maintainers-local/solutions-staging/deny-event-correlation-report/scripts/Export-DlpCopilotEvents.ps1
    - maintainers-local/solutions-staging/deny-event-correlation-report/scripts/Export-RaiTelemetry.ps1
    - maintainers-local/solutions-staging/deny-event-correlation-report/scripts/Invoke-DailyDenyReport.ps1
---

# Summary: Plan 02-02 — Deny Event Ingestion — Script Updates to Write to fsi_denyevent (DVS-02)

## Result

Implemented all 8 tasks: Connect-DECDataverse auth, Write-DECDenyEvent with redesigned parameters, Write-DECDenyEventBatch with OData `$batch` endpoint, Dataverse ingestion in all 3 extraction scripts + orchestrator, and Connect-DECServices EnvironmentUrl threading. All 5 files pass PowerShell syntax validation. All changes are backward-compatible (existing CSV/JSON export is unchanged; Dataverse ingestion is opt-in via `-WriteToDataverse`).

## Decisions Made

### 1. Write-DECDenyEvent Parameter Redesign (DENY-EVENT-PARAMS)

**Decision:** Replaced old parameters with schema-aligned set:
- `FilterSeverity` → validated `[ValidateSet('Info', 'Warning', 'High', 'Critical')]` (was untyped string)
- `ZoneClassification` → renamed to `Zone` with `[ValidateSet('1', '2', '3')]`
- `AdditionalProperties` → renamed to `DetailsJson` (hashtable → serialized JSON for `fsi_details_json`)
- Added mandatory `-SourceType` with `[ValidateSet('RaiTelemetry', 'PurviewAudit', 'PurviewDlp')]`
- Removed `ZoneClassification` → `Zone` for brevity and consistency with schema column name

**Rationale:** Parameters now directly match the `fsi_DenyEvent` table schema from Plan 02-01. Option set mapping is cleaner with validated string inputs.

### 2. Auto-Reconnect Pattern (DV-AUTO-RECONNECT)

**Decision:** Store `KeyVaultName` and `SecretName` in `$script:DvConnection` alongside auth tokens. `Write-DECDenyEvent` and `Write-DECDenyEventBatch` auto-reconnect using stored credentials when token expires.

**Rationale:** The App Insights pattern requires callers to re-authenticate manually. For Dataverse writes that may happen in long-running batch jobs, auto-reconnect is more robust. Storing credentials in module-level state (same process, same session) is acceptable for automation runbook scenarios.

### 3. Option Set Integer Mapping (OPTION-SET-MAPPING)

**Decision:** Map strings to integers in PowerShell code:
- Severity: Info=1, Warning=2, High=3, Critical=4 (matching `fsi_acv_severity`)
- Zone: 1=864340000, 2=864340001, 3=864340002 (matching `fsi_acv_zone`)

**Rationale:** Dataverse picklist columns require integer values. Mapping is done client-side to keep the OData payload clean and avoid Dataverse lookup overhead.

### 4. Batch Fallback Strategy (BATCH-FALLBACK)

**Decision:** `Write-DECDenyEventBatch` uses OData `$batch` multipart/mixed endpoint. On batch failure, falls back to individual `Write-DECDenyEvent` calls per event.

**Rationale:** The `$batch` endpoint is more efficient for large volumes but may fail on misconfigured environments. Individual fallback provides resilience at the cost of throughput.

### 5. DLP Agent ID Convention (DLP-AGENT-ID)

**Decision:** DLP events lack agent IDs. Use `DLP-{FirstPolicyName}` format, truncated to 100 chars. Falls back to `DLP-Unknown` if no policy name available.

**Rationale:** The `fsi_agent_id` column is mandatory in the schema. Using the policy name as a proxy allows grouping DLP events by policy for correlation analysis.

### 6. Severity Derivation Logic (SEVERITY-DERIVATION)

**Decision:** Each source derives severity differently:
- **PurviewAudit:** `Warning` default; `High` for PolicyBlock; `Critical` for XPIA/Jailbreak
- **PurviewDlp:** Mapped from DLP rule severity (Low→Info, Medium→Warning, High→High); Block action escalates to `High`
- **RaiTelemetry:** Mapped from RAI filterSeverity (Low→Info, Medium→Warning, High→High); default `Warning`

**Rationale:** Each source uses different severity semantics. Normalization at ingestion time supports consistent cross-source analysis.

## Files Modified

| File | Lines Before | Lines After | Change |
|------|-------------|-------------|--------|
| `scripts/private/DECClient.psm1` | 895 | 1296 | +401 (Connect-DECDataverse impl, Write-DECDenyEvent impl, Write-DECDenyEventBatch, Test-DECDataverseTokenValid, Connect-DECServices EnvironmentUrl) |
| `scripts/Export-CopilotDenyEvents.ps1` | 294 | 377 | +83 (WriteToDataverse params, Dataverse ingestion logic) |
| `scripts/Export-DlpCopilotEvents.ps1` | 285 | 374 | +89 (WriteToDataverse params, Dataverse ingestion logic, DLP severity/agent mapping) |
| `scripts/Export-RaiTelemetry.ps1` | 245 | 316 | +71 (WriteToDataverse params, Dataverse ingestion logic, RAI severity mapping) |
| `scripts/Invoke-DailyDenyReport.ps1` | 389 | 429 | +40 (WriteToDataverse orchestration, Dataverse service connection, tracking) |

All files under `maintainers-local/solutions-staging/deny-event-correlation-report/`.

## Commits

Files are in `maintainers-local/` which is gitignored by project convention. No git commits — files exist on disk and pass all validation checks.

## Validation Results

```
DECClient.psm1: OK (syntax check passed, 1296 lines)
Export-CopilotDenyEvents.ps1: OK (syntax check passed, 377 lines)
Export-DlpCopilotEvents.ps1: OK (syntax check passed, 374 lines)
Export-RaiTelemetry.ps1: OK (syntax check passed, 316 lines)
Invoke-DailyDenyReport.ps1: OK (syntax check passed, 429 lines)
```

## Task Completion

| Task | Description | Status |
|------|-------------|--------|
| 1 | Implement Connect-DECDataverse | Done — Key Vault + SP auth, token caching, Force refresh, env var fallback |
| 2 | Implement Write-DECDenyEvent | Done — New params, option set mapping, OData POST, retry logic |
| 3 | Update Export-CopilotDenyEvents.ps1 | Done — WriteToDataverse switch, severity/category derivation |
| 4 | Update Export-DlpCopilotEvents.ps1 | Done — WriteToDataverse switch, DLP-prefixed agent ID |
| 5 | Update Export-RaiTelemetry.ps1 | Done — WriteToDataverse switch, RAI severity mapping |
| 6 | Implement Write-DECDenyEventBatch | Done — OData $batch, multipart/mixed, batch-of-100, fallback |
| 7 | Update Invoke-DailyDenyReport.ps1 | Done — Dataverse service, pass-through, ingestion tracking |
| 8 | Update Connect-DECServices | Done — EnvironmentUrl parameter, splatted Dataverse call |

## Deviations from Plan

1. **No git commit:** `maintainers-local/` is gitignored per project convention. All files validated and present on disk.

2. **Test-DECDataverseTokenValid added as private (not exported):** The plan mentioned adding it as a private helper, which is correct. It's placed alongside `Test-DECTokenValid` in the private helpers section. Not exported in `Export-ModuleMember`.

3. **Connect-DECServices help updated:** Added `.PARAMETER EnvironmentUrl` documentation to Connect-DECServices help block (not explicitly called out in plan but necessary for completeness).

4. **Connect-DECDataverse storing KeyVaultName/SecretName:** Added `KeyVaultName` and `SecretName` to `$script:DvConnection` to enable auto-reconnect in Write-DECDenyEvent and batch functions. This deviates from the App Insights pattern (which doesn't store credentials) but is necessary for long-running batch scenarios.

## Discovered Work for Future Plans

1. **Plan 02-03:** Correlation engine can now query `fsi_denyevent` records written by these scripts. `Write-DECCorrelation` and `Write-DECValidationHistory` stubs remain for Plan 02-03 implementation.

2. **Phase 3+:** Zone classification is currently hardcoded to '1' in all extraction scripts. Future work should implement `Get-ZoneClassification` lookup based on agent registry or Dataverse environment variable configuration.

3. **Batch response parsing:** `Write-DECDenyEventBatch` currently treats HTTP 200 as full success. Future enhancement should parse multipart response to detect partial batch failures within a 200 response.
