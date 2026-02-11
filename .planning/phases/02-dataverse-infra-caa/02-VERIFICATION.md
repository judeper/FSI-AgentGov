---
phase: 2
status: passed
verified: 2026-02-10
---

# Verification: Phase 2 — Dataverse Infrastructure

## Phase Goal

CA policy baselines, validation history, and violation records are stored in Dataverse for persistent, queryable state across automated runs.

## Success Criteria Assessment

### SC-1: Dataverse schema deployed with CA policy baseline, validation history (immutable), and violation tables reusing existing `fsi_acv_zone` and `fsi_acv_severity` option sets
**Status: PASSED**
- `create_dataverse_schema.py` defines all 3 tables with correct column types
- `fsi_CAPolicyBaseline` (UserOwned, 13 columns) — per-policy configuration snapshots
- `fsi_CAPolicyValidationHistory` (OrganizationOwned, 11 columns) — immutable audit trail
- `fsi_CAPolicyViolation` (UserOwned, 13 columns) — individual violation records
- Shared option sets (`fsi_acv_zone`, `fsi_acv_severity`) use existence-check reuse pattern
- `EntitySetName` explicitly set on all tables (especially history to avoid pluralization)
- All columns use `fsi_` prefix

### SC-2: Environment variables for zone-specific CA policy thresholds (`fsi_CAA_*` prefix) deployed and consumed by Phase 1 scripts
**Status: PASSED**
- `create_environment_variables.py` defines 7 variables with correct types (3 Decimal, 4 String)
- `CAAClient.psm1` `Get-CAAEnvironmentVariable` reads variables via Dataverse API
- `Test-PolicyCompliance.ps1` reads 4 operational parameters (GracePeriodHours, BaselineMaxAgeDays, DriftSeverityEscalation, IncludeReportOnlyPolicies) when connected

### SC-3: Connection references for Dataverse, Office 365, Teams, and Microsoft Graph deployed with `fsi_cr_*` naming convention
**Status: PASSED**
- `create_connection_references.py` defines 4 connection references:
  - `fsi_cr_dataverse_conditionalaccessautomation` (shared_commondataserviceforapps)
  - `fsi_cr_office365_conditionalaccessautomation` (shared_office365)
  - `fsi_cr_teams_conditionalaccessautomation` (shared_teams)
  - `fsi_cr_graph_conditionalaccessautomation` (shared_microsoftgraphconnector)
- Error handling for invalid connector IDs (catches 400/404)

### SC-4: Python deployment scripts are idempotent (safe to re-run) and support dry-run mode, following ACV/SSC/AAM pattern
**Status: PASSED**
- `deploy.py` orchestrates schema → vars → refs with selective modes (`--tables-only`, `--vars-only`, `--refs-only`)
- All create operations use existence-check pattern (query before create, skip if exists)
- `--dry-run` propagated to all sub-modules
- Connection test blocks deployment on failure
- Post-deployment guidance printed on completion

## Build Validation

| Check | Result |
|-------|--------|
| `mkdocs build --strict` | PASSED (INFO only) |
| `python scripts/verify_controls.py` | PASSED (exit 0) |
| Python syntax (5 files) | PASSED |
| CAAClient.psm1 stubs | 0 remaining (all 8 implemented) |
| Module manifest | v1.1.0, NestedModules correct |

## File Manifest

### Python (5 files)
| File | Lines | Purpose |
|------|-------|---------|
| `scripts/caa_client.py` | ~460 | CAAClient Dataverse Web API client (MSAL auth, retry, dry-run) |
| `scripts/create_dataverse_schema.py` | ~600 | Three-table schema deployment with shared option sets |
| `scripts/create_environment_variables.py` | ~226 | 7 fsi_CAA_* environment variable deployment |
| `scripts/create_connection_references.py` | ~244 | 4 fsi_cr_* connection reference deployment |
| `scripts/deploy.py` | ~186 | Deployment orchestrator with selective execution |

### PowerShell (3 files modified)
| File | Change | Purpose |
|------|--------|---------|
| `scripts/private/CAAClient.psm1` | 8 stubs → implementations | Dataverse CRUD via Invoke-RestMethod |
| `scripts/Test-PolicyCompliance.ps1` | +3 params, +persistence | Opt-in Dataverse result/violation persistence |
| `scripts/conditional-access-automation.psd1` | v1.0.0 → v1.1.0 | Version bump for Dataverse integration |

### Dependencies
| File | Change |
|------|--------|
| `scripts/requirements.txt` | +msal>=1.30.0, +requests>=2.32.0 |

## Conclusion

Phase 2 goal achieved. All 4 success criteria passed. The Dataverse infrastructure layer is complete — CA policy baselines, validation history, and violations can be persisted and queried through both Python deployment scripts and PowerShell operational scripts.
