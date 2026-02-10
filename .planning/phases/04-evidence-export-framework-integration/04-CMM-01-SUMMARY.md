# Plan 04-CMM-01 Summary: Evidence Export Scripts

## Plan Identity

| Field | Value |
|-------|-------|
| Plan ID | 04-CMM-01 |
| Title | Evidence export scripts (Export-ContentModerationEvidence, Get-CMMValidationResults, Test-EvidenceIntegrity) |
| Phase | 04-evidence-export-framework-integration |
| Wave | 1 |
| Status | **Complete** |

## Tasks Completed: 3/3

### Task 1: Get-CMMValidationResults.ps1 (private helper)

**File:** `FSI-AgentGov-Solutions/content-moderation-monitor/scripts/private/Get-CMMValidationResults.ps1`

- Queries `fsi_moderationvalidationhistory` with date range and optional RunId filters
- Optionally queries `fsi_moderationviolations` with zone filter
- Violation select includes agent-level columns: `fsi_agent_id`, `fsi_agent_name`, `fsi_expected_level`, `fsi_actual_level`
- Handles OData pagination via `@odata.nextLink`
- Returns `PSCustomObject` with `.Validations` and `.Violations` arrays
- Error handling: specific messages for 401, 404, and generic HTTP errors
- `#Requires -Version 7.0` and complete comment-based help with 3 examples

### Task 2: Export-ContentModerationEvidence.ps1 (main export)

**File:** `FSI-AgentGov-Solutions/content-moderation-monitor/scripts/Export-ContentModerationEvidence.ps1`

- Imports CMMClient.psm1 and dot-sources Get-CMMValidationResults.ps1
- Authentication: MSAL.PS interactive or certificate-based service principal
- Calls `Connect-CMMDataverse` then `Get-CMMValidationResults` with all filters
- Optional baseline inclusion via `Get-ModerationBaseline -ActiveOnly`
- JSON evidence structure with 5 sections: metadata, summary, validations, violations, baselines
- metadata includes: exportedAt, solution, solutionVersion, fromDate, toDate, runId, zoneFilter, exportVersion, recordCount, violationCount, organizationUrl
- summary includes: overallStatus, totalScans, scansCompliant, scansWithViolations, totalAgents, totalViolations, criticalViolations, highViolations, mediumViolations, warningViolations
- Uses `ConvertTo-Json -Depth 10` (prevents nested truncation)
- Writes `cmm-evidence-{zone}-{yyyyMMdd-HHmmss}.json`
- Generates SHA-256 companion `.sha256` file with `{hash}  {filename}` format
- Returns PSCustomObject with EvidenceFile, HashFile, SHA256, RecordCount, ViolationCount, GeneratedAt
- `#Requires -Version 7.0` and complete comment-based help with 3 examples

### Task 3: Test-EvidenceIntegrity.ps1 (verification utility)

**File:** `FSI-AgentGov-Solutions/content-moderation-monitor/scripts/Test-EvidenceIntegrity.ps1`

- Validates evidence file and hash file existence with clear error messages
- Reads expected hash from `.sha256` companion (first field, split on whitespace)
- Computes actual hash via `Get-FileHash -Algorithm SHA256`
- Case-insensitive comparison
- Match: console verification message (unless `-Quiet`), returns `$true`
- Mismatch: `Write-Warning` with expected vs actual, returns `$false`
- `#Requires -Version 5.1` and complete comment-based help with 3 examples

## Files Created

| File | Purpose |
|------|---------|
| `content-moderation-monitor/scripts/private/Get-CMMValidationResults.ps1` | Dataverse query helper for validation history and violations |
| `content-moderation-monitor/scripts/Export-ContentModerationEvidence.ps1` | Main evidence export with JSON + SHA-256 hashing |
| `content-moderation-monitor/scripts/Test-EvidenceIntegrity.ps1` | SHA-256 hash verification utility |

## Key Decisions

1. **Followed AAM pattern exactly** — All three scripts mirror the established `Export-AgentAccessEvidence.ps1`, `Get-AAMValidationResults.ps1`, and `Test-EvidenceIntegrity.ps1` patterns from the agent-access-monitor solution, adapted for CMM's per-agent schema
2. **Agent-level violation columns** — CMM violations include `fsi_agent_id`, `fsi_agent_name`, `fsi_expected_level`, `fsi_actual_level` (vs AAM's environment-level `fsi_violation_type`, `fsi_expected_value`, `fsi_actual_value`)
3. **Agent-level summary metrics** — Added `totalAgents` to summary (sourced from latest scan's `fsi_total_agents`) and `mediumViolations` severity tier alongside critical/high/warning
4. **Baseline mapping uses friendly names** — Baselines from `Get-ModerationBaseline` return mapped property names (e.g., `EnvironmentGuid`, `AgentName`) so the evidence export maps from those friendly names, not raw Dataverse columns
5. **CMM-specific validation history columns** — Added `fsi_environments_scanned` field (tracks how many environments were scanned per run), mapped to `environmentsScanned` in evidence output
6. **File prefix** — Uses `cmm-evidence-` prefix (consistent with solution naming: `aam-evidence-`, `acv-evidence-`, `ssc-evidence-`)
7. **FSI language compliance** — No instances of "ensures compliance", "guarantees", "will prevent", or "eliminates risk"; uses "supports", "aids in", "helps meet"

## Verification Checklist

- [x] Get-CMMValidationResults.ps1 queries both Dataverse tables with filters
- [x] Export-ContentModerationEvidence.ps1 produces JSON with all 5 sections
- [x] ConvertTo-Json -Depth 10 used (prevents truncation)
- [x] SHA-256 companion file uses `{hash}  {filename}` format (two spaces)
- [x] Test-EvidenceIntegrity.ps1 returns boolean and handles all error cases
- [x] All scripts have #Requires and complete comment-based help
- [x] No prohibited FSI language used
- [x] Follows established solution patterns from AAM/ACV/SSC
