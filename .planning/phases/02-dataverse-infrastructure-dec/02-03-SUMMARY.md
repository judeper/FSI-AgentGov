---
phase: 2
plan: 3
wave: 3
status: complete
completed: 2026-02-10
---

# Plan 02-03 Summary: Correlation Engine and Zone-Based Retention Rules

## Objective

Implemented the deny event correlation engine that produces daily summaries grouping events by agent, zone, and time window with severity distribution and 7-day trend indicators. Implemented zone-based retention rules via Dataverse bulk delete jobs. Completed remaining DECClient.psm1 stubs.

## Decisions Made

1. **Write-DECCorrelation redesign**: Completely replaced the Phase 1 stub parameters (`DenyEventId`, `AuditRecordId`, `DlpPolicyMatchId`, `CorrelationType`, `ConfidenceScore`) with daily aggregate summary parameters matching the `fsi_DenyCorrelation` table schema (`CorrelationDate`, `AgentId`, `Zone`, `EventCount`, `SeverityDistribution`, `Trend7Day`, `TimeWindowStart`, `TimeWindowEnd`, `CorrelationDetails`).

2. **Trend direction calculation**: Used a first-half vs. second-half comparison of the 7-day window with ±15% threshold to classify trends as Increasing, Decreasing, or Stable.

3. **Retention scope**: Created bulk delete jobs for BOTH `fsi_denyevent` and `fsi_denycorrelation` tables (6 total jobs: 3 zones × 2 tables).

4. **deploy.py retention integration**: Added `--retention-ps` flag as a new mutually exclusive option that invokes `Set-DECRetentionRules.ps1` via subprocess. Kept existing Python-based `--retention-only` path intact for environments that prefer direct API calls without PowerShell.

5. **Invoke-DailyDenyReport.ps1 correlation step**: Added as Section 3 (after extractions, before blob upload), gated on `-WriteToDataverse`. Also added overall validation history write at the end.

## Files Modified

| File | Action | Lines |
|------|--------|-------|
| `maintainers-local/.../private/DECClient.psm1` | Modified | 1768 (was 1297; +471) |
| `maintainers-local/.../Invoke-DailyDenyReport.ps1` | Modified | 489 (was 430; +59) |
| `maintainers-local/.../deploy.py` | Modified | 361 (was 280; +81) |

## Files Created

| File | Lines | Purpose |
|------|-------|---------|
| `maintainers-local/.../Invoke-DenyEventCorrelation.ps1` | 401 | Daily correlation engine |
| `maintainers-local/.../Set-DECRetentionRules.ps1` | 317 | Zone-based retention bulk delete jobs |

## Task Completion

| Task | Description | Status |
|------|-------------|--------|
| 1 | Redesign and implement Write-DECCorrelation | ✅ Complete |
| 2 | Implement Write-DECValidationHistory | ✅ Complete |
| 3 | Add Read-DECDenyEvents helper | ✅ Complete |
| 4 | Add Read-DECCorrelations helper | ✅ Complete |
| 5 | Create Invoke-DenyEventCorrelation.ps1 | ✅ Complete |
| 6 | Create Set-DECRetentionRules.ps1 | ✅ Complete |
| 7 | Update deploy.py retention integration | ✅ Complete |
| 8 | Update Invoke-DailyDenyReport.ps1 for correlation step | ✅ Complete |

## New Exported Functions (DECClient.psm1)

| Function | Type | Purpose |
|----------|------|---------|
| `Write-DECCorrelation` | Write | Daily aggregate correlation summary to `fsi_denycorrelations` |
| `Write-DECValidationHistory` | Write | Validation audit trail to `fsi_denyvalidationhistory` |
| `Read-DECDenyEvents` | Read | OData query with filter/pagination for `fsi_denyevents` |
| `Read-DECCorrelations` | Read | OData query with filter/pagination for `fsi_denycorrelations` |

## Validation Results

- ✅ PowerShell syntax: All 4 PS files parse without errors
- ✅ Python syntax: deploy.py compiles without errors
- ✅ Module exports: All 12 functions exported (5 required verified)

## Deviations from Plan

1. **No git commit**: All modified/created files are under `maintainers-local/` which is gitignored per repository design. Changes are saved locally but cannot be committed to git. The summary and planning files can be committed separately.

## Key Patterns Followed

- All new Dataverse functions follow `Write-DECDenyEvent` pattern: connection validation → auto-reconnect → OData payload → retry loop with exponential backoff (429/503)
- All new scripts follow framework standards: `#Requires`, `[CmdletBinding()]`, full comment-based help, `$ErrorActionPreference = 'Stop'`, `[System.Diagnostics.Stopwatch]` duration tracking, `-Verbose` progress logging
- Zone option set mapping consistent: `864340000` (Zone 1), `864340001` (Zone 2), `864340002` (Zone 3)
- Severity option set mapping consistent: `1` (Info), `2` (Warning), `3` (High), `4` (Critical)
