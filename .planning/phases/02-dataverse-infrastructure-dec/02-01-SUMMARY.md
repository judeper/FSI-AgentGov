---
phase: 02-dataverse-infrastructure-dec
plan: 01
subsystem: deny-event-correlation-report
tags: [dataverse, python, msal, schema, retention, bulk-delete, option-sets]

# Dependency graph
requires: []
provides:
  - artifact: scripts/dec_client.py
    capability: "Dataverse Web API client with MSAL authentication (DECClient class)"
  - artifact: scripts/create_dataverse_schema.py
    capability: "4-table schema deployment with shared option set reuse"
  - artifact: scripts/create_environment_variables.py
    capability: "7 environment variables for retention, scan frequency, alerting"
  - artifact: scripts/create_connection_references.py
    capability: "3 connection references (Dataverse, Office 365, Teams)"
  - artifact: scripts/deploy.py
    capability: "Deployment orchestrator with dry-run, selective deployment, bulk delete retention"
  - artifact: docs/SCHEMA.md
    capability: "Complete schema documentation with ERD, retention rules, deployment instructions"
  - artifact: scripts/requirements.txt
    capability: "Python dependencies (msal, requests)"
affects:
  - phase-02-plans: [02-02, 02-03]
    reason: "All DEC Dataverse operations depend on dec_client.py and schema"

# Tech tracking
tech-stack:
  added: [msal>=1.30.0, requests>=2.32.0]
  patterns: [client-library, idempotent-deployment, dry-run, shared-option-sets, bulk-delete-retention]

key-files:
  created:
    - maintainers-local/solutions-staging/deny-event-correlation-report/scripts/dec_client.py
    - maintainers-local/solutions-staging/deny-event-correlation-report/scripts/requirements.txt
    - maintainers-local/solutions-staging/deny-event-correlation-report/scripts/create_dataverse_schema.py
    - maintainers-local/solutions-staging/deny-event-correlation-report/scripts/create_environment_variables.py
    - maintainers-local/solutions-staging/deny-event-correlation-report/scripts/create_connection_references.py
    - maintainers-local/solutions-staging/deny-event-correlation-report/scripts/deploy.py
    - maintainers-local/solutions-staging/deny-event-correlation-report/docs/SCHEMA.md
  modified:
    - maintainers-local/solutions-staging/deny-event-correlation-report/templates/deny-event-baseline.json
---

# Summary: Plan 02-01 — Dataverse Schema Design and Table Definitions (DVS-01)

## Result

Created the complete Dataverse infrastructure foundation for DEC deny event persistence. Eight deliverables across 8 tasks: Python client library (DECClient), requirements, 4-table schema deployment, environment variables, connection references, deployment orchestrator with bulk delete retention, schema documentation, and updated baseline template. All Python files pass syntax validation. All files follow idempotent check-before-create patterns and support `--dry-run` mode.

## Decisions Made

### 1. DECClient Pattern (DEC-CLIENT-PATTERN)

**Decision:** Adapt the proven v4-v8 client pattern for DEC with `DEC_` environment variable prefix.

**Rationale:** The v4-v8 client pattern (ACVClient → SSCClient → AAMClient → CMMClient → FUSClient) has been validated across 5 solutions. Reusing the identical MSAL auth flow, retry strategy, and idempotent helpers reduces risk.

**Key differences from prior clients:**
- Class name: `DECClient`
- Env var prefix: `DEC_` (DEC_TENANT_ID, DEC_ENVIRONMENT_URL, DEC_CLIENT_ID, DEC_CLIENT_SECRET)
- Added `create_environment_variable()` and `create_connection_reference()` convenience methods directly on the client class (prior solutions had these inline in their respective scripts)

### 2. Shared Option Set Reuse (OPTION-SET-REUSE)

**Decision:** Reuse `fsi_acv_zone` and `fsi_acv_severity` via existence check. Create only if fresh environment.

**Rationale:** All governance solutions share the same zone and severity definitions. DEC never creates its own option sets — consistency across solutions is mandatory per research INF-02.

### 3. Organization-Owned Validation History (VALIDATION-IMMUTABLE)

**Decision:** `fsi_DenyValidationHistory` is OrganizationOwned; other 3 tables are UserOwned.

**Rationale:** Follows v4-v8 pattern — validation history is an immutable audit log. Organization-owned prevents per-record ownership cascade deletes and supports regulatory immutability requirements.

### 4. Bulk Delete Retention (RETENTION-APPROACH)

**Decision:** Implement zone-based retention via Dataverse `BulkDeleteRequest` API with 3 recurring daily jobs at 02:00 UTC.

**Rationale:** This is a new capability — no prior v4-v8 solution has implemented Dataverse record-level retention. Bulk delete is the supported Dataverse pattern for automated record cleanup. Retention days are configurable via environment variables.

### 5. Template Prefix Fix (TEMPLATE-PREFIX)

**Decision:** Updated `deny-event-baseline.json` from `dec_*` to `fsi_*` table prefixes throughout. Added all 4 tables, entity set names, shared option sets, environment variables, and connection references.

**Rationale:** The `fsi_` prefix is mandated by INF-02 naming convention. Prior template had placeholder `dec_*` names from Phase 1 stub work.

## Files Created/Modified

| File | Action | Lines |
|------|--------|-------|
| `scripts/dec_client.py` | CREATE | 323 |
| `scripts/requirements.txt` | CREATE | 2 |
| `scripts/create_dataverse_schema.py` | CREATE | 308 |
| `scripts/create_environment_variables.py` | CREATE | 121 |
| `scripts/create_connection_references.py` | CREATE | 99 |
| `scripts/deploy.py` | CREATE | 226 |
| `docs/SCHEMA.md` | CREATE | 297 |
| `templates/deny-event-baseline.json` | MODIFY | 70 |

All files under `maintainers-local/solutions-staging/deny-event-correlation-report/`.

## Commits

Files are in `maintainers-local/` which is gitignored by project convention (local-only staging artifacts). No git commits were made — files exist on disk and pass all validation checks.

## Validation Results

```
dec_client.py: OK (syntax check passed)
create_dataverse_schema.py: OK (syntax check passed)
create_environment_variables.py: OK (syntax check passed)
create_connection_references.py: OK (syntax check passed)
deploy.py: OK (syntax check passed)
SCHEMA.md: exists
deny-event-baseline.json: valid JSON, all fsi_ prefixes confirmed, no dec_ prefixes remaining
```

## Deviations from Plan

1. **Client convenience methods:** Added `create_environment_variable()` and `create_connection_reference()` methods directly on `DECClient` class rather than as standalone functions. This reduces boilerplate in the env vars and connection refs scripts while maintaining the same external API.

2. **No git commit:** `maintainers-local/` is gitignored per project convention. All files validated and present on disk. Future phases that move solution artifacts to FSI-AgentGov-Solutions repo will track them there.

## Discovered Work for Future Plans

1. **Plan 02-02:** Wire PowerShell stubs (`Connect-DECDataverse`, `Write-DECDenyEvent`, `Write-DECCorrelation`, `Write-DECValidationHistory`) in `DECClient.psm1` to use Dataverse Web API via the schema deployed here.

2. **Plan 02-03:** Implement correlation engine logic — query `fsi_DenyEvent`, group by agent/zone, compute trends, write to `fsi_DenyCorrelation`.

3. **Phase 3:** Populate `fsi_DenyAlert` table and configure Teams alerting via `fsi_DEC_TeamsGroupId`/`fsi_DEC_TeamsChannelId` environment variables.

4. **Security role configuration:** Post-deployment step to remove Write/Delete privileges on `fsi_DenyValidationHistory` — documented in SCHEMA.md but requires manual action or a dedicated script.

5. **Batch ingestion:** Large tenants may need `$batch` endpoint support for `Write-DECDenyEvent` — deferred to Plan 02-02 or 02-03 based on volume testing.
