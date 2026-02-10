---
phase: 2
status: passed
verified_at: 2026-02-09
---

# Phase 2 Verification: Dataverse Infrastructure

## Goal
Access baselines, validation history, and configuration thresholds are stored in Dataverse for persistent, queryable state across automated runs

## Success Criteria Results

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | Dataverse schema deployed with access baseline, validation history (immutable), and violation tables reusing fsi_acv_zone/fsi_acv_severity option sets | ✅ PASS | `create_dataverse_schema.py`: fsi_AccessBaseline (UserOwned, IsAuditEnabled=True), fsi_AccessValidationHistory (OrganizationOwned — confirmed at line 117: `"OwnershipType": "OrganizationOwned"`, IsAuditEnabled=True), fsi_AccessViolation (UserOwned, IsAuditEnabled=True). Both `fsi_acv_zone` and `fsi_acv_severity` defined as shared global option sets with existence check before create (`SHARED_OPTIONSETS` dict, `create_shared_optionsets()` function). Columns: Baseline=10, History=9, Violation=14. |
| 2 | Environment variables (fsi_AAM_* prefix) deployed; Phase 1 scripts read thresholds from them | ✅ PASS | `create_environment_variables.py`: 6 variables — `fsi_AAM_GracePeriodHours` (Decimal, 48), `fsi_AAM_ScanFrequencyHours` (Decimal, 24), `fsi_AAM_IncludeSandbox` (String, false), `fsi_AAM_BaselineMaxAgeDays` (Decimal, 30), `fsi_AAM_TeamsGroupId` (String, empty), `fsi_AAM_TeamsChannelId` (String, empty). `Test-AgentAccessCompliance.ps1` reads via `Get-AAMEnvironmentVariable` in Dataverse Integration region (lines ~120-140): overrides `GracePeriodHours` and `ExcludeSandbox` from Dataverse when `-DataverseUrl` is provided. |
| 3 | Connection references with fsi_cr_* naming convention | ✅ PASS | `create_connection_references.py`: 3 refs — `fsi_cr_dataverse_accessmonitor` (shared_commondataserviceforapps), `fsi_cr_office365_accessmonitor` (shared_office365), `fsi_cr_teams_accessmonitor` (shared_teams). All follow `fsi_cr_{connector}_accessmonitor` naming convention. |
| 4 | Python deployment scripts are idempotent with dry-run mode | ✅ PASS | `deploy.py`: orchestrates schema → env vars → connection refs pipeline. `--dry-run` flag throughout. Selective modes: `--tables-only`, `--vars-only`, `--refs-only` (mutually exclusive). All scripts check existence before creating: schema uses `get_entity_metadata()`/`get_attribute_metadata()`/`get_global_optionset()`, env vars query `environmentvariabledefinitions`, connection refs query `connectionreferences`. `aam_client.py` has `AAMClient.dry_run` property respected in all API calls. |

## Additional Checks

- **AAMClient.psm1 RunId support:** ✅ `Write-AAMValidationHistory` has mandatory `-RunId` parameter; sets `fsi_run_id` field. `Write-AAMViolation` has optional `-RunId` parameter; conditionally adds `fsi_run_id` when RunId provided.
- **Test-AgentAccessCompliance.ps1 -PersistResults:** ✅ New parameters `-DataverseToken` and `-PersistResults`. When both `-DataverseUrl` and `-PersistResults` are set, generates a RunId (`[guid]::NewGuid()`), calls `Write-AAMValidationHistory` for the summary and `Write-AAMViolation` for each violation. All writes gated by `ShouldProcess` (supports `-WhatIf`). Failures caught with `try/catch` and `Write-Warning` (never abort scan).
- **Standalone mode preserved:** ✅ Without `-DataverseUrl`, the Dataverse integration region is entirely skipped. Phase 1 behavior unchanged — no parameter validation depends on Dataverse. The verbose message "Dataverse connected but -PersistResults not specified. Skipping persistence." confirms opt-in persistence.
- **CHANGELOG.md v0.2.0 entry:** ✅ Present with date 2026-02-09. Documents all Phase 2 additions (aam_client.py, schema, env vars, connection refs, deploy.py, persistence parameters) and changes (RunId on Write-AAMValidation* functions).
- **requirements.txt:** ✅ Contains `msal>=1.30.0` and `requests>=2.32.0` — minimal correct dependencies for Dataverse Web API client.
- **aam_client.py:** ✅ Full Dataverse Web API client with MSAL auth (interactive + service principal), retry logic (3 retries, backoff, status 429/5xx), idempotent helper methods (`create_table`, `create_option_set`, `create_column`), dry-run support on all operations.

## Build Validation

- **mkdocs build --strict:** PASSED — built in 28.78 seconds, 4 INFO messages about excluded-file links (pre-existing, not Phase 2 related)
- **verify_controls.py:** 6 pre-existing failures (footer metadata on 1.1, 1.7, 1.8, 1.18, 2.1, 3.8 — missing canonical footer version/date). None related to Phase 2.

## Verdict: PASSED

All 4 success criteria are fully met. The Dataverse infrastructure layer is complete:
- 3-table schema with correct ownership types (OrganizationOwned for immutable audit trail)
- 6 environment variables with fsi_AAM_* prefix read by Phase 1 scripts
- 3 connection references with fsi_cr_* naming convention
- Idempotent Python deployment pipeline with dry-run support
- PowerShell integration with RunId correlation and opt-in persistence
- Standalone mode fully preserved
