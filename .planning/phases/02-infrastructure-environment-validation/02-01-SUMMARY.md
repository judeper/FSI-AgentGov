---
phase: 02-infrastructure-environment-validation
plan: 01
subsystem: infra
tags: [python, dataverse, msal, power-platform, audit-validation]

# Dependency graph
requires:
  - phase: 01-core-validation-scripts
    provides: PowerShell validators for tenant audit configuration
provides:
  - Dataverse infrastructure for validation history storage
  - API client with MSAL auth and retry logic
  - Environment variables for configurable zone thresholds
  - Connection references for Dataverse and Office 365 connectors
  - Deployment orchestrator with dry-run and selective deployment
affects: [03-power-automate-integration, 04-alerting-reporting]

# Tech tracking
tech-stack:
  added: [msal>=1.30.0, requests>=2.32.0, azure-identity>=1.18.0, azure-keyvault-secrets>=4.7.0]
  patterns: [Tier 2 solution pattern, organization-owned immutable tables, MSAL token caching, idempotent deployment, dry-run preview]

key-files:
  created:
    - audit-configuration-validator/scripts/acv_client.py
    - audit-configuration-validator/scripts/create_dataverse_schema.py
    - audit-configuration-validator/scripts/create_environment_variables.py
    - audit-configuration-validator/scripts/create_connection_references.py
    - audit-configuration-validator/scripts/deploy.py
    - audit-configuration-validator/README.md
    - audit-configuration-validator/CHANGELOG.md
  modified: []

key-decisions:
  - "Organization-owned tables for immutability (security roles must remove Write/Delete post-deployment)"
  - "Zone thresholds stored as Dataverse environment variables (not hardcoded)"
  - "Dry-run mode in ACVClient for safe preview of all API operations"
  - "Retry logic with exponential backoff (3 retries, 429/500/502/503/504 status codes)"
  - "Denormalized zone in validation history (captures zone at time of validation)"
  - "Idempotent deployment with existing schema checks before creation"

patterns-established:
  - "ACVClient pattern: MSAL auth + retry logic + dry-run mode + idempotent helpers"
  - "Deployment orchestrator pattern: selective flags (--tables-only, --vars-only, --refs-only)"
  - "Environment variable pattern: fsi_ACV_* prefix for solution-specific configuration"
  - "Connection reference pattern: fsi_cr_* prefix, definition-only creation"

# Metrics
duration: 7min
completed: 2026-02-06
---

# Phase 2 Plan 1: Solution Structure, Dataverse Schema, and Deploy Orchestrator

**Dataverse infrastructure with organization-owned immutable tables, MSAL-authenticated API client, configurable zone thresholds via environment variables, and idempotent deployment orchestrator**

## Performance

- **Duration:** 7 min
- **Started:** 2026-02-06T21:33:06Z
- **Completed:** 2026-02-06T21:40:14Z
- **Tasks:** 2
- **Files created:** 7 Python files, 2 docs, 2 directories
- **Lines of code:** ~2,157 Python

## Accomplishments

- Complete Dataverse schema: 5 option sets, 2 organization-owned tables (validation history + environment registry)
- ACVClient with MSAL auth (interactive + SP), retry logic, dry-run mode, and idempotent helpers
- 5 environment variables for zone thresholds (180d/365d/730d) and operational parameters (24h grace, 5min canary)
- 2 connection references (Dataverse, Office 365) for Power Automate integration
- deploy.py orchestrator supporting full/selective deployment with dry-run preview
- Solution folder structure following Tier 2 pattern (docs/, src/, scripts/)

## Task Commits

Each task was committed atomically:

1. **Task 1: Create solution folder structure, API client, and Dataverse schema scripts** - `e717db1` (feat)
   - Solution structure (docs/, src/, scripts/)
   - README.md with prerequisites, quick start, zone requirements, data model
   - CHANGELOG.md (v0.1.0 PowerShell, v0.2.0 infrastructure)
   - requirements.txt with Python dependencies
   - acv_client.py: Dataverse Web API client with MSAL auth, retry logic, dry-run mode
   - create_dataverse_schema.py: 5 option sets, 2 tables, all columns

2. **Task 2: Create environment variables, connection references, and deploy orchestrator** - `80f1fe7` (feat)
   - create_environment_variables.py: 5 variables (zone thresholds + operational params)
   - create_connection_references.py: 2 connection references
   - deploy.py: Full orchestration with selective deployment flags

## Files Created/Modified

**Created:**
- `audit-configuration-validator/README.md` - Solution overview, prerequisites, quick start, zone requirements, data model
- `audit-configuration-validator/CHANGELOG.md` - Version history (v0.1.0 PowerShell, v0.2.0 infrastructure)
- `audit-configuration-validator/scripts/requirements.txt` - Python dependencies (msal, requests, azure-identity, azure-keyvault-secrets)
- `audit-configuration-validator/scripts/acv_client.py` - Dataverse Web API client
  - MSAL auth: PublicClientApplication (interactive) + ConfidentialClientApplication (SP)
  - Token caching with acquire_token_silent
  - Retry logic: HTTPAdapter with 3 retries, exponential backoff, 429/500/502/503/504 status codes
  - Dry-run mode: logs API calls without executing
  - Idempotent helpers: create_table(), create_option_set(), check_table_exists(), create_column()
- `audit-configuration-validator/scripts/create_dataverse_schema.py` - Tables and option sets
  - 5 global option sets: fsi_acv_severity (Passed/Warning/GracePeriod/Failed/Error), fsi_acv_scope (Tenant/Environment), fsi_acv_zone (Unclassified/Zone1/Zone2/Zone3), fsi_acv_envstatus (Active/Inactive), fsi_acv_environmenttype (Production/Sandbox/Developer/Trial/Default)
  - fsi_auditvalidationhistory table: organization-owned, 12 columns, immutable append-only
  - fsi_environmentregistry table: organization-owned, 9 columns, admin-managed
  - Idempotent deployment with existing schema checks
- `audit-configuration-validator/scripts/create_environment_variables.py` - Configurable zone thresholds
  - fsi_ACV_Zone1RetentionDays (default: 180)
  - fsi_ACV_Zone2RetentionDays (default: 365)
  - fsi_ACV_Zone3RetentionDays (default: 730)
  - fsi_ACV_GracePeriodHours (default: 24)
  - fsi_ACV_CanaryWaitMinutes (default: 5)
- `audit-configuration-validator/scripts/create_connection_references.py` - Solution connectors
  - fsi_cr_dataverse_auditvalidation (Dataverse connector)
  - fsi_cr_office365_auditvalidation (Office 365 connector)
  - Definition-only creation (connections bind at runtime)
- `audit-configuration-validator/scripts/deploy.py` - Deployment orchestrator
  - Full deployment: schema + env vars + connection refs
  - Selective flags: --tables-only, --vars-only, --refs-only
  - Dry-run preview: --dry-run
  - Interactive and Service Principal auth
  - Step-by-step execution with clear output
- `audit-configuration-validator/docs/.gitkeep` - Placeholder for future documentation
- `audit-configuration-validator/src/.gitkeep` - Placeholder for future Power Automate flows

## Decisions Made

1. **Organization-owned tables for immutability** - Both fsi_auditvalidationhistory and fsi_environmentregistry use OwnershipType "OrganizationOwned" to prevent modification/deletion. Security roles must remove Write/Delete privileges post-deployment (documented in deploy.py output and README security section).

2. **Zone thresholds as environment variables** - Zone retention thresholds stored as Dataverse environment variables (fsi_ACV_Zone1RetentionDays, etc.) instead of hardcoded values. Enables runtime configuration without code changes.

3. **Dry-run mode in ACVClient** - Added dry_run parameter to ACVClient constructor and all API methods. Logs intended API calls without executing, enabling safe preview of deployment.

4. **Retry logic with exponential backoff** - Implemented HTTPAdapter with Retry strategy (3 retries, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504]) to handle transient API failures.

5. **Denormalized zone in validation history** - fsi_zone column in fsi_auditvalidationhistory denormalizes environment zone at time of validation. Captures historical zone classification even if environment is later reclassified.

6. **Idempotent deployment** - All create_* scripts check for existing schema before attempting creation. Enables safe re-runs and incremental deployment.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None - all scripts created successfully, imports verified, naming conventions honored (fsi_ prefix for schema, fsi_ACV_* for env vars, fsi_cr_* for connection refs).

## User Setup Required

None at this stage - Dataverse infrastructure deployment is automated via deploy.py.

**Manual steps deferred to Phase 3:**
- Power Automate flow creation (scheduled tenant/environment validation)
- Connection binding for Dataverse and Office 365 connectors

**Post-deployment security configuration required:**
- Security roles must remove Write/Delete privileges on fsi_auditvalidationhistory
- Only Create (append-only) privilege for automation accounts
- See README.md security section for details

## Next Phase Readiness

**Ready for Phase 3 (Power Automate Integration):**
- Dataverse schema complete (tables, option sets, columns)
- Environment variables configured (zone thresholds, operational params)
- Connection references defined (Dataverse, Office 365)
- deploy.py enables rapid lab testing per user requirement

**Dependencies satisfied:**
- INFR-01: Solution structure (docs/, src/, scripts/) ✓
- INFR-02: Dataverse schema (tables, option sets) ✓
- INFR-03: Connection references (fsi_cr_*) ✓
- INFR-04: Environment variables (fsi_ACV_*) ✓
- EVID-03: Organization-owned validation history table ✓

**Blockers:** None

**Concerns:** None - all infrastructure ready for Phase 3 flow development

---
*Phase: 02-infrastructure-environment-validation*
*Completed: 2026-02-06*

## Self-Check: PASSED

All files created successfully:
- FOUND: /Users/admin/dev/FSI-AgentGov-Solutions/audit-configuration-validator/scripts/acv_client.py
- FOUND: /Users/admin/dev/FSI-AgentGov-Solutions/audit-configuration-validator/scripts/create_dataverse_schema.py
- FOUND: /Users/admin/dev/FSI-AgentGov-Solutions/audit-configuration-validator/scripts/create_environment_variables.py
- FOUND: /Users/admin/dev/FSI-AgentGov-Solutions/audit-configuration-validator/scripts/create_connection_references.py
- FOUND: /Users/admin/dev/FSI-AgentGov-Solutions/audit-configuration-validator/scripts/deploy.py
- FOUND: /Users/admin/dev/FSI-AgentGov-Solutions/audit-configuration-validator/README.md
- FOUND: /Users/admin/dev/FSI-AgentGov-Solutions/audit-configuration-validator/CHANGELOG.md

All commits verified:
- FOUND: e717db1
- FOUND: 80f1fe7
