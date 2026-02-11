---
phase: 3
plan: 3
title: "Alert severity classification, DECClient alert functions, and anomaly detection"
status: complete
completed: 2026-02-10
---

# Plan 03-03 Summary: Alert Infrastructure & Evaluation Engine

## Status: Complete

All 6 tasks executed successfully. All files pass PowerShell syntax validation and JSON validation.

## Files Modified

| File | Lines | Change |
|------|-------|--------|
| `scripts/private/DECClient.psm1` | 1769 → 2097 (+328) | Added Write-DECAlert, Read-DECAlerts, Get-DECAlertThresholds; updated ValidateSet for Write-DECValidationHistory; updated export list |
| `scripts/Invoke-DailyDenyReport.ps1` | 490 → 527 (+37) | Added Section 4 alert evaluation step; renumbered Sections 5/6; added alertsGenerated to summary and return object |
| `templates/deny-event-baseline.json` | 84 → 105 (+21) | Added alerting section with threshold defaults, alert types, severity classification, and routing config |

## Files Created

| File | Lines | Purpose |
|------|-------|---------|
| `scripts/Invoke-DECAlertEvaluation.ps1` | 522 | Alert evaluation engine — evaluates correlations for VolumeAnomaly, NewAgent, ZoneCritical, and RoutineDeny alerts |

All paths relative to `maintainers-local/solutions-staging/deny-event-correlation-report/`.

## Functions Added

| Function | Module | Description |
|----------|--------|-------------|
| `Write-DECAlert` | DECClient.psm1 | Persists alert records to fsi_denyalert with AlertType, AlertSeverity, AgentId, Zone, AlertMessage, Details |
| `Read-DECAlerts` | DECClient.psm1 | Queries alert history with date/agent/zone/type OData filters and pagination |
| `Get-DECAlertThresholds` | DECClient.psm1 | Reads AnomalyThresholdSigma, TeamsGroupId, TeamsChannelId from DEC_ environment variables with defaults |

DECClient.psm1 now exports **15 functions** (12 existing + 3 new).

## Task Execution Details

### Task 1: Write-DECAlert ✅
- Follows Write-DECCorrelation pattern: connection validation → auto-reconnect → OData POST → retry loop
- Severity mapping: Critical=4, High=4, Warning=2, Info=1 (per plan specification)
- Zone mapping: reuses 864340000-864340002
- Returns PSCustomObject with Status, AlertId, AlertType, Severity, Timestamp

### Task 2: Read-DECAlerts ✅
- Follows Read-DECCorrelations pattern: build $filter → OData GET → pagination via @odata.nextLink
- Supports StartDate, EndDate, AgentId, Zone, AlertType filters
- Returns Alerts array and AlertCount

### Task 3: Get-DECAlertThresholds ✅
- Reads DEC_AnomalyThresholdSigma (default 2.0), DEC_TeamsGroupId, DEC_TeamsChannelId
- Returns TeamsConfigured boolean and MinHistoryDays (3)

### Task 4: Invoke-DECAlertEvaluation.ps1 ✅
- Full evaluation engine with 4 alert checks per correlation:
  - 4a: ZoneCritical — Zone 3 + Jailbreak/XPIA → Critical
  - 4b: VolumeAnomaly — event_count > avg + (sigma × stddev) → High
  - 4c: NewAgent — no prior correlations → High
  - 4d: RoutineDeny — Zone 1 RAI → Warning, other → Info
- Cold-start protection: skips anomaly detection when < MinHistoryDays (3) of history
- DryRun mode for testing without Dataverse writes
- Writes validation history for audit trail
- Returns structured summary with AlertsByType, AlertsBySeverity, Alerts array

### Task 5: Invoke-DailyDenyReport.ps1 Update ✅
- Section 4 (alert evaluation) inserted after Section 3 (correlation), before blob upload
- Gated on -WriteToDataverse flag
- Error in alert evaluation does not block blob upload or report completion
- Section numbering updated: blob upload → Section 5, cleanup → Section 6
- Summary output includes "Alerts generated" count
- Return object includes AlertResult and AlertsGenerated properties

### Task 6: deny-event-baseline.json Update ✅
- Added "alerting" section with:
  - anomalyThresholdSigma: 2.0, minHistoryDays: 3, coldStartBehavior: "skip"
  - 4 alertTypes with enabled/severity/description
  - severityClassification with optionSetValue, zones, categories/triggers, routing
  - routing config for teams, email, log channels

## Validation Results

```
OK: DECClient.psm1           (PowerShell syntax)
OK: Invoke-DailyDenyReport.ps1  (PowerShell syntax)
OK: Invoke-DECAlertEvaluation.ps1  (PowerShell syntax)
OK: deny-event-baseline.json  (JSON syntax)
Exported functions: 15 (verified)
```

## Deviations from Plan

1. **Get-DECAlertThresholds environment variable names**: Plan showed `Get-DECEnvironmentVariable -Name 'fsi_DEC_AnomalyThresholdSigma'` but the existing function doesn't have a `-Name` parameter. Implemented using hashtable indexing with `DEC_AnomalyThresholdSigma` (local env var name without `fsi_` Dataverse schema prefix).

2. **Parse error fix**: Initial `$zoneStr:` in string interpolation caused PowerShell parse error (colon interpreted as scope modifier). Fixed with `${zoneStr}:` syntax in two alert message strings.

3. **Write-DECValidationHistory ValidateSet**: Added `'AlertEvaluation'` to the ValidateSet to support the new validation type used by Invoke-DECAlertEvaluation.ps1.

## Blockers

None encountered.

## Git Status

Files are under `maintainers-local/` which is gitignored by design (local-only development artifacts). Changes are preserved locally.
