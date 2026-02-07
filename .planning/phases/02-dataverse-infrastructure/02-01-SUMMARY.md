---
phase: 02-dataverse-infrastructure
plan: 01
subsystem: session-security-configurator
tags: [dataverse, python, msal, schema, tier-2]
requires:
  - phase-01-plans: [01-01, 01-02, 01-03]
provides:
  - artifact: ssc_client.py
    capability: "Dataverse Web API client with MSAL authentication"
  - artifact: create_dataverse_schema.py
    capability: "3-table schema deployment (SessionBaseline, ValidationHistory, DriftViolation)"
  - artifact: requirements.txt
    capability: "Python dependencies (msal, requests)"
affects:
  - phase-02-plans: [02-02, 02-03]
  - reason: "All deployment scripts depend on ssc_client.py for Dataverse operations"
tech-stack:
  added: [msal, requests, dataverse-web-api]
  patterns: [client-library, idempotent-deployment, dry-run, shared-option-sets]
key-files:
  created:
    - session-security-configurator/scripts/ssc_client.py
    - session-security-configurator/scripts/requirements.txt
    - session-security-configurator/scripts/create_dataverse_schema.py
  modified: []
decisions:
  - id: SSC-CLIENT-PATTERN
    decision: "Adapt ACVClient pattern for SSC with SSC_ env var prefix"
    rationale: "Proven authentication flow, retry logic, and idempotent helpers from ACV v4"
    alternatives: ["Custom client", "Power Platform CLI Python bindings"]
    trade-offs: "Code duplication across solutions vs proven reliability"
  - id: SHARED-OPTION-SETS
    decision: "Reuse fsi_acv_zone and fsi_acv_severity from ACV with existence check"
    rationale: "Consistency across governance solutions, avoid duplicate definitions"
    alternatives: ["SSC-specific zone/severity option sets"]
    trade-offs: "Cross-solution dependency vs semantic consistency"
  - id: VALIDATION-HISTORY-IMMUTABLE
    decision: "ValidationHistory is OrganizationOwned for immutability"
    rationale: "Audit trail cannot be modified by operators — regulatory requirement"
    alternatives: ["UserOwned with security roles limiting deletion"]
    trade-offs: "Operators cannot delete records vs guaranteed audit integrity"
  - id: THREE-TABLE-DESIGN
    decision: "Separate tables for baselines, history, and violations"
    rationale: "Clear separation of concerns — baseline storage, audit trail, alerting"
    alternatives: ["Single unified table with type column"]
    trade-offs: "More tables to manage vs optimal query patterns per use case"
metrics:
  duration: "4 minutes"
  completed: 2026-02-07
  commits: 2
  files-created: 3
  lines-added: 865
---

# Phase 2 Plan 1: SSC Dataverse Client and Schema Summary

**One-liner:** Python Dataverse client with MSAL auth and 3-table schema (SessionBaseline, ValidationHistory org-owned immutable, DriftViolation) reusing ACV option sets

## What Was Built

Created the Python infrastructure foundation for SSC Dataverse operations:

1. **ssc_client.py** — Dataverse Web API client class
   - MSAL authentication with both interactive and service principal modes
   - Full CRUD operations and metadata management
   - Retry logic for transient failures (3 retries, exponential backoff)
   - Dry-run mode for safe deployment testing
   - Idempotent helpers: check_table_exists, create_table, create_option_set, create_column
   - SSC_ environment variable prefix (SSC_TENANT_ID, SSC_CLIENT_ID, SSC_CLIENT_SECRET, SSC_ENVIRONMENT_URL)

2. **requirements.txt** — Python dependencies
   - msal>=1.30.0 for Entra ID authentication
   - requests>=2.32.0 for HTTP operations
   - No Azure SDK dependencies (keeping it minimal unlike ACV)

3. **create_dataverse_schema.py** — Schema deployment orchestrator
   - **Shared option sets** (reused from ACV):
     - fsi_acv_zone (Unclassified, Zone 1, Zone 2, Zone 3)
     - fsi_acv_severity (Passed, Warning, GracePeriod, Failed, Error)
     - Existence check before creation — no duplication
   - **SSC-specific option set**:
     - fsi_ssc_validationtype (SessionControls, AuthStrength, PIMSettings, BreakGlass, ConflictAudit, Orchestrator)
   - **Table 1: fsi_SessionBaseline (UserOwned)**
     - Purpose: Store zone-specific session security baselines
     - Key columns: Zone, SignInFrequencyMinutes, AuthStrength, RequireCompliantDevice, PIMMaxActivationHours, PIMRequireApproval, PIMRequireAuthContext, IsActive, CapturedOn, RawJson
     - Operators manage baselines (UserOwned for lifecycle operations)
   - **Table 2: fsi_ValidationHistory (OrganizationOwned — IMMUTABLE)**
     - Purpose: Immutable audit log of all validation runs
     - Key columns: RunId (GUID correlation), Zone, Severity, ValidationType, RawValue, Reason, RemediationHint, Timestamp, CheckCount, BaselineId
     - OrganizationOwned ensures operators cannot modify/delete audit records
   - **Table 3: fsi_DriftViolation (UserOwned)**
     - Purpose: Track threshold violations requiring operator attention
     - Key columns: Zone, Severity, DriftType, ExpectedValue, ActualValue, PolicyId, PolicyName, DetectedOn, Acknowledged, AcknowledgedBy, AcknowledgedOn, Notes
     - Operators need to acknowledge and annotate violations (UserOwned)

## Task Commits

| Task | Commit | Description |
|------|--------|-------------|
| 1 | 0965175 | Create ssc_client.py and requirements.txt |
| 2 | e4e8d0d | Create create_dataverse_schema.py with 3-table design |

**Files created:**
- session-security-configurator/scripts/ssc_client.py (297 lines)
- session-security-configurator/scripts/requirements.txt (7 lines)
- session-security-configurator/scripts/create_dataverse_schema.py (568 lines)

**Total additions:** 865 lines Python (client + schema definitions)

## Decisions Made

### 1. SSC Client Pattern (SSC-CLIENT-PATTERN)

**Decision:** Adapt the proven ACVClient pattern for SSC with SSC_ environment variable prefix.

**Rationale:** The ACV client (v4 milestone) demonstrated reliable MSAL authentication flow, retry logic for Dataverse transient failures, and idempotent deployment helpers. Rather than reinventing, adapt the working pattern.

**Key differences from ACV:**
- Class name: SSCClient (not ACVClient)
- Env var prefix: SSC_ (not ACV_)
- Docstrings reference "Session Security Configurator"
- No Azure Key Vault or Managed Identity support yet (future enhancement)

**What stayed identical:**
- MSAL auth flow (interactive vs SP)
- Retry strategy (3 retries, backoff on 429/5xx)
- Web API operations (query, create_record, metadata methods)
- Idempotent helpers (check before create pattern)

**Alternatives considered:**
- Custom client from scratch (rejected: unnecessary risk, more time)
- Power Platform CLI Python bindings (rejected: not stable enough, limited documentation)

**Trade-offs:**
- Code duplication across solutions (ACVClient, SSCClient will share 95% code)
- Future: Consider extracting to shared fsi_dataverse_client library

### 2. Shared Option Set Reuse (SHARED-OPTION-SETS)

**Decision:** Reuse fsi_acv_zone and fsi_acv_severity from ACV with existence check before creation.

**Rationale:**
- Semantic consistency across all FSI-AgentGov solutions
- Zone definitions are framework-level (not solution-specific)
- Severity levels (Passed, Warning, GracePeriod, Failed, Error) apply uniformly to all validators
- Avoids duplicate definitions that could diverge over time

**Implementation:**
- SHARED_OPTIONSETS dict with full definitions (needed if ACV not deployed first)
- create_optionsets() checks get_global_optionset() before creating
- Print "Already exists (reusing)" when found, "Creating" when missing

**Alternatives considered:**
- SSC-specific zone/severity option sets (rejected: breaks cross-solution reporting)
- Require ACV to be deployed first (rejected: creates unnecessary dependency order)

**Trade-offs:**
- Cross-solution dependency on shared option set names
- If ACV changes zone definitions, SSC must be updated (acceptable: zones are stable)

### 3. ValidationHistory Immutability (VALIDATION-HISTORY-IMMUTABLE)

**Decision:** fsi_ValidationHistory is OrganizationOwned to enforce immutability.

**Rationale:**
- Regulatory requirement: Audit trails cannot be modified or deleted by operators
- FINRA 4511, SEC 17a-4 require tamper-proof logs of compliance checks
- OrganizationOwned = no user can delete records (only system administrators with delete org-owned data privileges)
- SessionBaseline and DriftViolation are UserOwned (operators need lifecycle management)

**Impact:**
- Operators cannot delete ValidationHistory records even if no longer relevant
- Data retention must be managed via automated archival processes
- Power Automate flows write-only to ValidationHistory (no update/delete flows)

**Alternatives considered:**
- UserOwned with security roles limiting deletion (rejected: still allows privileged users to modify)
- Custom API with immutability checks (rejected: OrganizationOwned is built-in enforcement)

**Trade-offs:**
- Table growth unbounded without archival automation
- Cannot correct erroneous validation records (by design — audit integrity)

### 4. Three-Table Design (THREE-TABLE-DESIGN)

**Decision:** Separate tables for SessionBaseline, ValidationHistory, and DriftViolation.

**Rationale:**
- **SessionBaseline**: Configuration storage — operators CRUD active baselines per zone
- **ValidationHistory**: Append-only audit log — high write volume, time-series queries
- **DriftViolation**: Alert management — operators acknowledge, annotate, resolve violations

**Query pattern optimization:**
- Baseline queries: "Get active baseline for Zone 2" (simple filter on IsActive + Zone)
- History queries: "Show all validations for RunId X" (correlation across 5 validators)
- Violation queries: "Show unacknowledged drift in Zone 3" (operator to-do list)

**Alternatives considered:**
- Single unified table with fsi_RecordType column (rejected: mixed query patterns, ownership conflicts)
- Two tables: Baseline + combined History/Violation (rejected: immutability requirement for history only)

**Trade-offs:**
- More tables to manage (3 vs 1)
- Clearer separation of concerns and optimal access patterns per use case
- Future reporting can join across tables via Zone + timestamp

## Verification Results

All verification checks passed:

1. ✅ Python syntax validation (ast.parse) for all 3 files
2. ✅ SSCClient class exists with all required methods (10 methods)
3. ✅ SSC_ environment variable prefix used (6 occurrences)
4. ✅ requirements.txt has msal and requests dependencies
5. ✅ Three tables defined with correct ownership types:
   - SessionBaseline: UserOwned ✅
   - ValidationHistory: OrganizationOwned ✅
   - DriftViolation: UserOwned ✅
6. ✅ Shared option sets (fsi_acv_zone, fsi_acv_severity) referenced via GlobalOptionSet@odata.bind (5 references)
7. ✅ SSC-specific option set (fsi_ssc_validationtype) defined with 6 values
8. ✅ Existence checks in create_optionsets() for both shared and SSC option sets
9. ✅ Idempotent deployment pattern throughout (check before create)
10. ✅ Dry-run support in all deployment operations

## Integration Points

### Upstream Dependencies (Phase 1)
- **01-01**: PowerShell templates define zone session controls that become baseline values
- **01-02**: Deploy-AuthContexts.ps1 and Deploy-StepUpPolicies.ps1 create policies referenced in drift detection
- **01-03**: Test-SessionCompliance.ps1 will write validation results to ValidationHistory table

### Downstream Dependencies (This Phase)
- **02-02**: Environment variables and connection references will use ssc_client.py authentication pattern
- **02-03**: Dataverse deployment scripts (write baselines, validation history, drift violations) import SSCClient

### Cross-Solution Dependencies
- **ACV (v4)**: Shares fsi_acv_zone and fsi_acv_severity option sets
- **Future solutions**: Any validator can write to shared option set-based tables for unified reporting

## Next Phase Readiness

**Phase 2 Plan 2 can proceed** — Environment variables, connection references, and Power Platform configuration scripts are next.

**Readiness checklist:**
- ✅ Python client library exists (ssc_client.py)
- ✅ Schema definitions complete (create_dataverse_schema.py)
- ✅ Dependencies documented (requirements.txt)
- ✅ Idempotent deployment pattern established
- ✅ Dry-run capability for safe testing

**Blockers:** None

**Concerns:** None

**Recommendations for next plan:**
1. Create SSC_ environment variables matching ACVClient pattern (SSC_TENANT_ID, SSC_CLIENT_ID, etc.)
2. Connection references for Dataverse and Microsoft Graph
3. Deployment orchestrator to run schema creation before first use

## Deviations from Plan

None — plan executed exactly as written.

## Performance Notes

**Execution time:** 4 minutes (2 tasks)

**Commit breakdown:**
- Task 1 (ssc_client.py + requirements.txt): 297 lines added
- Task 2 (create_dataverse_schema.py): 568 lines added

**Code reuse:**
- SSCClient is 95% identical to ACVClient (proven pattern)
- Shared option set definitions copied from ACV for consistency

**Deployment characteristics:**
- Schema creation is fully idempotent (safe to run multiple times)
- Dry-run mode allows validation without Dataverse credentials
- Three tables will be created in order: option sets → tables → columns

## Repository Context

**Solution repository:** FSI-AgentGov-Solutions
**Commits:** 0965175, e4e8d0d (committed to FSI-AgentGov-Solutions)
**Documentation repository:** FSI-AgentGov
**Planning docs:** .planning/phases/02-dataverse-infrastructure/

## Self-Check: PASSED

All verification checks passed:
- ✅ ssc_client.py exists on disk
- ✅ requirements.txt exists on disk
- ✅ Commit 0965175 exists in git log
- ✅ Commit e4e8d0d exists in git log
