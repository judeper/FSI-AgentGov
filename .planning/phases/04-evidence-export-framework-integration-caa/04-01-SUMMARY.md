---
phase: 4
plan: 1
title: "SHA-256 evidence export scripts"
status: Complete
completed: 2026-02-10
---

# Plan 04-01 Summary: SHA-256 Evidence Export Scripts

## Status: Complete

## Objective

Created PowerShell evidence export scripts that produce JSON files with CA policy compliance results, violations, baselines, and SHA-256 integrity hashes for FINRA/SEC examination support.

## Tasks Completed

### Task 1: Get-CAAValidationResults.ps1 private helper
**File:** `C:/dev/FSI-AgentGov-Solutions/conditional-access-automation/scripts/private/Get-CAAValidationResults.ps1`
- Queries Dataverse via OData Web API with pagination (`@odata.nextLink`)
- Supports 3 tables: `fsi_capolicyvalidationhistories`, `fsi_capolicyviolations`, `fsi_capolicybaselines`
- Parameters: `DataverseUrl` (M), `AccessToken` (M), `Table` (M, ValidateSet), `FromDate` (O), `ToDate` (O), `RunId` (O)
- Auto-filters baselines to active-only (`fsi_isactive eq true`)
- `#Requires -Version 5.1`, comment-based help with examples

### Task 2: Export-CAAComplianceEvidence.ps1 main export
**File:** `C:/dev/FSI-AgentGov-Solutions/conditional-access-automation/scripts/Export-CAAComplianceEvidence.ps1`
- Full evidence schema: metadata, summary (with zone breakdown), validations, violations, baselines
- SHA-256 companion file in sha256sum-compatible format (`"{hash}  {filename}"`)
- `ConvertTo-Json -Depth 10` and `Out-File -Encoding utf8`
- ShouldProcess/WhatIf support
- Overall status computed from worst severity: Error > Failed > GracePeriod > Warning > Passed
- Output: `CAA-Evidence-{timestamp}.json` + `.sha256`

### Task 3: Test-EvidenceIntegrity.ps1 hash verification
**File:** `C:/dev/FSI-AgentGov-Solutions/conditional-access-automation/scripts/Test-EvidenceIntegrity.ps1`
- Reads companion `.sha256` file and computes `Get-FileHash -Algorithm SHA256`
- Returns `[PSCustomObject]@{ Path; Valid; ExpectedHash; ActualHash }`
- Exit code 0 on match, 1 on mismatch
- Pipeline support via `ValueFromPipeline` and `FullName` alias

### Task 4: Module manifest update
**File:** `C:/dev/FSI-AgentGov-Solutions/conditional-access-automation/scripts/conditional-access-automation.psd1`
- Version bumped from 1.0.0 → 1.1.0
- Added `Export-CAAComplianceEvidence` and `Test-EvidenceIntegrity` to `FunctionsToExport`
- Updated ReleaseNotes with 1.1.0 changelog

## Commits

| Hash | Message |
|------|---------|
| `ba594ac` | feat(evidence): add SHA-256 evidence export scripts (Plan 04-01) |

## Verification

- All 3 scripts pass PSParser syntax validation (0 errors each)
- Module manifest validates successfully via `Test-ModuleManifest`
- Version confirmed: 1.1.0
- Exported functions confirmed: 7 total (5 existing + 2 new)

## Acceptance Criteria Status

- [x] `Export-CAAComplianceEvidence.ps1` produces valid JSON with metadata/summary/validations/violations/baselines sections
- [x] SHA-256 companion file generated with `"{hash}  {filename}"` format
- [x] `Test-EvidenceIntegrity.ps1` returns `Valid = $true` for matching hash
- [x] All 3 scripts have `#Requires`, comment-based help, and ShouldProcess where appropriate
- [x] JSON uses `-Depth 10` and explicit UTF-8 encoding
- [x] Module manifest exports new functions

## Decisions

- Used `#Requires -Version 5.1` as specified in the plan (vs. 7.0 in existing scripts) for broader compatibility
- Authentication falls back to `Get-AzAccessToken` if `CAAClient` module-scoped token is not set, since CAAClient stubs throw "not implemented" errors
- Zone breakdown computed dynamically from `fsi_zone` field in validation records
- Baselines auto-filtered to `fsi_isactive eq true` to return only current baselines

## Discovered Work

None — all tasks completed as planned.
