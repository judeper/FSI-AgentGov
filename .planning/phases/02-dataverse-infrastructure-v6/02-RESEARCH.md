# Phase 2: Dataverse Infrastructure (v6) - Research

**Researched:** 2026-02-09
**Milestone:** v6 — Agent Access Governance Monitor
**Domain:** Dataverse schema deployment, Python automation, PowerShell integration
**Confidence:** HIGH

## Summary

Phase 2 creates persistent Dataverse infrastructure to store agent access validation results from Phase 1, enabling historical trending, compliance reporting, and automated drift detection workflows. The research focused on four areas: (1) proven ACV/SSC Dataverse deployment patterns to follow, (2) AAM-specific schema design (three tables for access baselines, validation history, and violations), (3) environment variable design for externalizing zone thresholds and operational parameters, and (4) Phase 1 integration points where existing PowerShell scripts already have Dataverse hooks.

**Key finding:** Phase 1 already built AAMClient.psm1 with Dataverse helper functions (`Connect-AAMDataverse`, `Get-AAMEnvironmentVariable`, `Get-AAMActiveBaseline`, `Write-AAMValidationHistory`, `Write-AAMViolation`) that reference Dataverse table names and the `fsi_AAM_` prefix. Phase 2 must create the Python deployment infrastructure that provisions the tables, option sets, and environment variables these helpers expect. The AAMClient.psm1 represents the "consumer" side — Phase 2 builds the "provider" side.

**Primary recommendation:** Follow the ACV/SSC Python deployment pattern exactly, adapting table definitions to AAM's three-table schema (access baselines, validation history, access violations) while reusing existing `fsi_acv_zone` and `fsi_acv_severity` option sets.

---

## 1. Existing Patterns (ACV/SSC Dataverse Infrastructure)

### File Structure

Both ACV (v4) and SSC (v5) follow an identical pattern deployed to `FSI-AgentGov-Solutions/{solution}/scripts/`:

```
audit-configuration-validator/scripts/     session-security-configurator/scripts/
├── acv_client.py                          ├── ssc_client.py
├── create_dataverse_schema.py             ├── create_dataverse_schema.py
├── create_environment_variables.py        ├── create_environment_variables.py
├── create_connection_references.py        ├── create_connection_references.py
├── deploy.py                              ├── deploy.py
└── requirements.txt                       └── requirements.txt
```

**Source:** [02-infrastructure-environment-validation/02-01-SUMMARY.md](../../.planning/phases/02-infrastructure-environment-validation/02-01-SUMMARY.md) (ACV) and [02-dataverse-infrastructure/02-01-SUMMARY.md](../../.planning/phases/02-dataverse-infrastructure/02-01-SUMMARY.md) (SSC)

### Key Classes and Methods

The `{SOLUTION}Client` class (ACVClient, SSCClient → AAMClient) provides:

| Method | Purpose |
|--------|---------|
| `__init__()` | MSAL auth setup (interactive + SP), retry strategy, dry-run flag |
| `_get_token()` | Token acquisition with silent cache → interactive/SP fallback |
| `_get_headers()` | Authorization bearer, OData headers, Prefer annotations |
| `test_connection()` | GET organizations endpoint |
| `query()` | OData query with select, filter, orderby, top |
| `create_record()` | POST to entity set, extract ID from OData-EntityId header |
| `get_entity_metadata()` / `create_entity()` | Table metadata operations |
| `create_attribute()` / `get_attribute_metadata()` | Column metadata operations |
| `create_global_optionset()` / `get_global_optionset()` | Option set operations |
| `check_table_exists()` / `create_table()` / `create_column()` | Idempotent helpers |

**Standard libraries:** `msal>=1.30.0`, `requests>=2.32.0`. No Azure SDK dependencies needed.

**Retry strategy:** `Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])`

**Environment variable prefix convention:**
- ACV: `ACV_TENANT_ID`, `ACV_ENVIRONMENT_URL`, `ACV_CLIENT_ID`, `ACV_CLIENT_SECRET`
- SSC: `SSC_TENANT_ID`, `SSC_ENVIRONMENT_URL`, etc.
- AAM: `AAM_TENANT_ID`, `AAM_ENVIRONMENT_URL`, etc.

### ACV Dataverse Schema

**Tables:** 2 (organization-owned)
- `fsi_auditvalidationhistory` — 12 columns, immutable append-only
- `fsi_environmentregistry` — 9 columns, admin-managed

**Option sets:** 5 global
- `fsi_acv_severity` — Passed(1), Warning(2), GracePeriod(3), Failed(4), Error(5)
- `fsi_acv_zone` — Unclassified(0), Zone 1(1), Zone 2(2), Zone 3(3)
- `fsi_acv_scope` — Tenant(1), Environment(2)
- `fsi_acv_envstatus` — Active(1), Inactive(2)
- `fsi_acv_environmenttype` — Production(1), Sandbox(2), Developer(3), Trial(4), Default(5)

**Environment variables:** 5 (`fsi_ACV_*` prefix)
- `fsi_ACV_Zone1RetentionDays` (180), `fsi_ACV_Zone2RetentionDays` (365), `fsi_ACV_Zone3RetentionDays` (730)
- `fsi_ACV_GracePeriodHours` (24), `fsi_ACV_CanaryWaitMinutes` (5)

**Connection references:** 2
- `fsi_cr_dataverse_auditvalidation` (shared_commondataserviceforapps)
- `fsi_cr_office365_auditvalidation` (shared_office365)

**Source:** [02-infrastructure-environment-validation/02-01-SUMMARY.md](../../.planning/phases/02-infrastructure-environment-validation/02-01-SUMMARY.md)

### SSC Dataverse Schema

**Tables:** 3 (mixed ownership)
- `fsi_SessionBaseline` — UserOwned (operators manage baselines)
- `fsi_ValidationHistory` — OrganizationOwned (immutable audit log)
- `fsi_DriftViolation` — UserOwned (operators acknowledge violations)

**Option sets:** Reuses `fsi_acv_zone` + `fsi_acv_severity`, adds 1 SSC-specific:
- `fsi_ssc_validationtype` — SessionControls(1), AuthStrength(2), PIMSettings(3), BreakGlass(4), ConflictAudit(5), Orchestrator(6)

**Environment variables:** 6 (`fsi_SSC_*` prefix)
- `fsi_SSC_Zone{1,2,3}SignInFrequencyMinutes` (480, 240, 60)
- `fsi_SSC_Zone{1,2,3}AuthStrength` (standard, passwordless, phishing-resistant)

**Connection references:** 3
- `fsi_cr_dataverse_sessionvalidation`, `fsi_cr_office365_sessionvalidation`, `fsi_cr_teams_sessionvalidation`

**Source:** [02-dataverse-infrastructure/02-01-SUMMARY.md](../../.planning/phases/02-dataverse-infrastructure/02-01-SUMMARY.md) and [02-02-SUMMARY.md](../../.planning/phases/02-dataverse-infrastructure/02-02-SUMMARY.md)

### SSC Phase 2 Plan Structure (Proven 3-Plan Split)

| Plan | Wave | Contents | Duration |
|------|------|----------|----------|
| 02-01 | 1 | Client library + requirements + schema (3 tables + option sets) | ~4 min |
| 02-02 | 2 | Environment variables + connection references + deploy.py orchestrator | ~3 min |
| 02-03 | 3 | Wire Phase 1 PowerShell to read thresholds from Dataverse | ~2 min |

**Total SSC Phase 2 time:** ~9 minutes across 3 plans. AAM should follow this exact split.

**Source:** [02-dataverse-infrastructure/02-03-SUMMARY.md](../../.planning/phases/02-dataverse-infrastructure/02-03-SUMMARY.md)

---

## 2. AAM-Specific Schema Design

### Table 1: fsi_AccessBaseline (UserOwned)

Stores per-environment access setting snapshots. Operators manage baselines (capture, activate, deactivate).

| Column | Type | Required | Description |
|--------|------|----------|-------------|
| `fsi_Name` | String(200) | Yes | Baseline ID (e.g., "contoso-z3-trading-2026-02-09") |
| `fsi_EnvironmentGuid` | String(100) | Yes | Power Platform environment GUID |
| `fsi_EnvironmentName` | String(500) | Yes | Environment display name |
| `fsi_Zone` | Picklist | Yes | GlobalOptionSet@odata.bind → `fsi_acv_zone` |
| `fsi_BotLimitSharingMode` | String(200) | Yes | Captured `bot-limitSharingMode` value |
| `fsi_BotAuthoringSharingDisabled` | Boolean | Yes | Captured `bot-authoringSharingDisabled` |
| `fsi_BotPublishedBotLimitSharingMode` | String(200) | Yes | Captured `bot-publishedBotLimitSharingMode` value |
| `fsi_IsActive` | Boolean | Yes | Whether this is the current active baseline |
| `fsi_CapturedAt` | DateTime | Yes | When baseline was captured |
| `fsi_CapturedBy` | String(200) | No | UPN of operator who captured |
| `fsi_RawJson` | Memo(100000) | No | Full JSON snapshot of all governance settings |

**Ownership:** UserOwned — operators need CRUD lifecycle management for baselines.
**Audit:** IsAuditEnabled = True

**Key queries:**
- "Get active baseline for environment X" → `$filter=fsi_is_active eq true and fsi_environment_guid eq '{guid}'`
- "List all baselines for Zone 3" → `$filter=fsi_zone eq 3`

### Table 2: fsi_AccessValidationHistory (OrganizationOwned — IMMUTABLE)

Immutable append-only audit log of all validation scan results. CRITICAL for regulatory compliance (FINRA 4511, SEC 17a-3).

| Column | Type | Required | Description |
|--------|------|----------|-------------|
| `fsi_Name` | String(200) | Yes | Validation ID (e.g., "Zone3-2026-02-09T14:30:00Z") |
| `fsi_RunId` | String(36) | Yes | GUID correlating all records in one scan execution |
| `fsi_Zone` | Picklist | Yes | GlobalOptionSet@odata.bind → `fsi_acv_zone` |
| `fsi_Severity` | Picklist | Yes | GlobalOptionSet@odata.bind → `fsi_acv_severity` |
| `fsi_TotalEnvironments` | Integer | No | Number of environments scanned |
| `fsi_CompliantCount` | Integer | No | Environments passing all checks |
| `fsi_ViolationCount` | Integer | No | Environments with violations |
| `fsi_OverallStatus` | String(50) | Yes | Passed / Warning / Review / Failed |
| `fsi_SummaryJson` | Memo(100000) | No | Full JSON validation result |
| `fsi_Timestamp` | DateTime | Yes | When validation ran |

**Ownership:** OrganizationOwned — operators cannot modify or delete audit records. Post-deployment, security roles must remove Write/Delete privileges.
**Audit:** IsAuditEnabled = True

**Design note:** This table aligns with `Write-AAMValidationHistory` in AAMClient.psm1, which writes `fsi_validation_time`, `fsi_total_environments`, `fsi_compliant_count`, `fsi_violation_count`, `fsi_overall_status`, and `fsi_summary_json`. The column names in the schema use PascalCase (`fsi_TotalEnvironments`) while the PowerShell helper uses snake_case (`fsi_total_environments`). These map to the same Dataverse logical name (Dataverse is case-insensitive on column logical names).

### Table 3: fsi_AccessViolation (UserOwned)

Per-environment, per-setting violations detected by Compare-ZoneCompliance.ps1. Operators acknowledge and annotate.

| Column | Type | Required | Description |
|--------|------|----------|-------------|
| `fsi_Name` | String(200) | Yes | Violation ID (e.g., "Z3-bot-limitSharingMode-2026-02-09") |
| `fsi_EnvironmentGuid` | String(100) | Yes | Violating environment GUID |
| `fsi_EnvironmentName` | String(500) | Yes | Environment display name |
| `fsi_Zone` | Picklist | Yes | GlobalOptionSet@odata.bind → `fsi_acv_zone` |
| `fsi_Severity` | Picklist | Yes | GlobalOptionSet@odata.bind → `fsi_acv_severity` |
| `fsi_ViolationType` | String(200) | Yes | Setting key that violated (e.g., `bot-limitSharingMode`) |
| `fsi_ExpectedValue` | String(2000) | Yes | What zone requires |
| `fsi_ActualValue` | String(2000) | Yes | What was found |
| `fsi_RegulatoryContext` | String(2000) | No | FINRA/SOX impact statement |
| `fsi_DetectedAt` | DateTime | Yes | When violation found |
| `fsi_Acknowledged` | Boolean | No | Whether operator has reviewed (default: false) |
| `fsi_AcknowledgedBy` | String(200) | No | UPN of acknowledging operator |
| `fsi_AcknowledgedOn` | DateTime | No | When acknowledged |
| `fsi_ResolvedAt` | DateTime | No | When remediated (nullable) |
| `fsi_Notes` | Memo(2000) | No | Operator notes on violation |

**Ownership:** UserOwned — operators need to acknowledge, annotate, and resolve violations.
**Audit:** IsAuditEnabled = True

**Design note:** Aligns with `Write-AAMViolation` in AAMClient.psm1, which writes `fsi_environment_guid`, `fsi_environment_name`, `fsi_zone`, `fsi_violation_type`, `fsi_expected_value`, `fsi_actual_value`, `fsi_severity`, `fsi_regulatory_context`, `fsi_detected_at`.

---

## 3. Option Set Reuse

### Shared Option Sets (from ACV)

Two global option sets are defined by ACV and reused across all governance solutions:

**`fsi_acv_zone`** — Zone classification:
| Value | Label |
|-------|-------|
| 0 | Unclassified |
| 1 | Zone 1 |
| 2 | Zone 2 |
| 3 | Zone 3 |

**`fsi_acv_severity`** — Validation severity:
| Value | Label |
|-------|-------|
| 1 | Passed |
| 2 | Warning |
| 3 | GracePeriod |
| 4 | Failed |
| 5 | Error |

### Reuse Pattern

AAM follows the SSC precedent:

```python
# In create_dataverse_schema.py
SHARED_OPTIONSETS = {
    "fsi_acv_zone": { ... full definition ... },
    "fsi_acv_severity": { ... full definition ... },
}

def create_optionsets(client, dry_run=False):
    # Shared option sets: create ONLY if not already present
    for name, definition in SHARED_OPTIONSETS.items():
        existing = client.get_global_optionset(name)
        if existing:
            print(f"  {name}: already exists (from ACV or other solution), reusing")
            continue
        # Create if ACV/SSC not deployed
        if dry_run:
            print(f"  {name}: would create")
        else:
            client.create_global_optionset(definition)
```

**Key rule:** AAM never creates its own zone or severity option sets. It checks for existing global option sets and reuses them. If ACV/SSC haven't been deployed (e.g., fresh environment), AAM creates them using the same canonical definitions.

### AAM-Specific Option Sets

AAM's agent access domain is simpler than SSC's session security domain. The violation types map directly to the three `bot-*` settings, which are already captured as string values in `fsi_ViolationType`. Unlike SSC (which needed `fsi_ssc_validationtype` with 6 different validator types), AAM violations are straightforward setting-level comparisons.

**Decision: No AAM-specific option sets needed.** The `fsi_ViolationType` column stores the setting key as text (`bot-limitSharingMode`, `bot-authoringSharingDisabled`, `bot-publishedBotLimitSharingMode`), which is sufficient. This reduces deployment complexity and avoids unnecessary option set proliferation.

**Source:** [ARCHITECTURE.md](../../.planning/research/ARCHITECTURE.md) lines 279-285 (option set reuse strategy), [02-dataverse-infrastructure/02-01-SUMMARY.md](../../.planning/phases/02-dataverse-infrastructure/02-01-SUMMARY.md) (SSC implementation)

---

## 4. Environment Variables

### fsi_AAM_* Variable Design

AAM's zone requirements are binary (expected value matches or doesn't), unlike SSC's numeric thresholds (sign-in frequency in minutes). The zone-specific expected settings are already defined in `zone-settings-baseline.json`. Environment variables should externalize **operational parameters** that operators may want to tune at runtime:

| Variable | Display Name | Type | Default | Description |
|----------|-------------|------|---------|-------------|
| `fsi_AAM_GracePeriodHours` | AAM - Grace Period (Hours) | Decimal | 48 | Hours to exclude newly provisioned environments from violation reporting |
| `fsi_AAM_ScanFrequencyHours` | AAM - Scan Frequency (Hours) | Decimal | 24 | How often automated scans should run |
| `fsi_AAM_IncludeSandbox` | AAM - Include Sandbox Environments | String | false | Whether to include sandbox environments in validation |
| `fsi_AAM_BaselineMaxAgeDays` | AAM - Maximum Baseline Age (Days) | Decimal | 30 | Alert if active baseline is older than this many days |
| `fsi_AAM_TeamsGroupId` | AAM - Teams Alert Group ID | String | (blank) | Teams group GUID for violation alerts |
| `fsi_AAM_TeamsChannelId` | AAM - Teams Alert Channel ID | String | (blank) | Teams channel GUID for violation alerts |

**Type mapping:**
- Decimal (100000001) — for numeric values (hours, days)
- String (100000000) — for text values (boolean strings, GUIDs)

**Why not zone-specific expected values as env vars?** The zone-settings-baseline.json already defines expected values per zone. These are structural governance decisions (Zone 3 = org-only), not tunable thresholds. Changing them would require policy-level review, not runtime tuning. Operational parameters (grace period, scan frequency) are the right candidates for environment variables.

### AAMClient.psm1 Integration

The existing `Get-AAMEnvironmentVariable` function in AAMClient.psm1 already queries Dataverse for `fsi_AAM_*` environment variables:

```powershell
$schemaName = "fsi_AAM_$Name"
$uri = "$script:DataverseUrl/api/data/v9.2/environmentvariabledefinitions?" +
       "`$filter=schemaname eq '$schemaName'&" +
       "`$expand=environmentvariablevalues"
```

Phase 2 creates the environment variables; AAMClient.psm1 consumes them. No Phase 1 code changes needed for this integration.

**Source:** [AAMClient.psm1](../../FSI-AgentGov-Solutions/agent-access-monitor/scripts/private/AAMClient.psm1) lines 78-120

---

## 5. Connection References

### AAM Connection References

Following the `fsi_cr_{connector}_{solution}` naming convention:

| Logical Name | Display Name | Connector | Purpose |
|-------------|-------------|-----------|---------|
| `fsi_cr_dataverse_accessmonitor` | Dataverse - Agent Access Monitor | `shared_commondataserviceforapps` | Read/write baselines, validation history, violations |
| `fsi_cr_office365_accessmonitor` | Office 365 - Agent Access Monitor | `shared_office365` | Email alerts for critical violations |
| `fsi_cr_teams_accessmonitor` | Teams - Agent Access Monitor | `shared_teams` | Teams adaptive card alerts for violations |

### Naming Convention Catalog

Cross-solution connection reference inventory:

| Solution | Dataverse | Office 365 | Teams |
|----------|-----------|------------|-------|
| ACV (v4) | `fsi_cr_dataverse_auditvalidation` | `fsi_cr_office365_auditvalidation` | — |
| SSC (v5) | `fsi_cr_dataverse_sessionvalidation` | `fsi_cr_office365_sessionvalidation` | `fsi_cr_teams_sessionvalidation` |
| AAM (v6) | `fsi_cr_dataverse_accessmonitor` | `fsi_cr_office365_accessmonitor` | `fsi_cr_teams_accessmonitor` |

**Note:** Connection references are definitions only. Actual connection binding happens during solution import or manual configuration in Power Automate. Deployment script outputs post-deployment binding instructions.

**Source:** [02-infrastructure-environment-validation/02-01-SUMMARY.md](../../.planning/phases/02-infrastructure-environment-validation/02-01-SUMMARY.md) (ACV naming), [02-dataverse-infrastructure/02-02-SUMMARY.md](../../.planning/phases/02-dataverse-infrastructure/02-02-SUMMARY.md) (SSC naming)

---

## 6. Deployment Script Structure

### Files Needed

AAM follows the identical 5-file structure from ACV/SSC:

| File | Responsibility | Key Contents |
|------|---------------|-------------|
| `aam_client.py` | Dataverse Web API client | `class AAMClient`: MSAL auth, retry, dry-run, idempotent helpers |
| `create_dataverse_schema.py` | Table and option set deployment | 3 tables (AccessBaseline, AccessValidationHistory, AccessViolation) + shared option set reuse |
| `create_environment_variables.py` | Env var deployment | 6 variables with `fsi_AAM_*` prefix |
| `create_connection_references.py` | Connection ref deployment | 3 refs (`fsi_cr_*_accessmonitor`) |
| `deploy.py` | Orchestrator | Full/selective deployment (--tables-only, --vars-only, --refs-only), dry-run, post-deployment guidance |
| `requirements.txt` | Python dependencies | `msal>=1.30.0`, `requests>=2.32.0` |

### AAMClient Differences from SSCClient

| Aspect | SSCClient | AAMClient |
|--------|-----------|-----------|
| Class name | `SSCClient` | `AAMClient` |
| Env var prefix | `SSC_` | `AAM_` |
| Docstrings | "Session Security Configurator" | "Agent Access Governance Monitor" |
| API methods | Identical | Identical |
| Auth flow | Identical | Identical |
| Retry logic | Identical | Identical |

Everything else is structurally identical — a direct adaptation with solution-specific naming.

### Idempotent Deployment Pattern

All deployment scripts follow the same pattern:

```python
# Check existence before create
existing = client.get_entity_metadata("fsi_accessbaseline")
if existing:
    print(f"  fsi_accessbaseline: already exists, skipping")
else:
    if dry_run:
        print(f"  fsi_accessbaseline: would create")
    else:
        client.create_entity(entity_definition)
        print(f"  fsi_accessbaseline: created")
```

### deploy.py Orchestrator Pattern

```
deploy.py
├── Step 1: Dataverse Schema (create_dataverse_schema.create_schema)
├── Step 2: Environment Variables (create_environment_variables.create_environment_variables)
├── Step 3: Connection References (create_connection_references.create_connection_references)
└── Post-Deployment Guidance
    ├── Security roles: Remove Write/Delete on AccessValidationHistory
    └── Connection binding: Configure in Power Automate
```

**CLI arguments:** `--tenant-id`, `--client-id`, `--client-secret`, `--environment-url`, `--interactive`, `--dry-run`, `--tables-only`, `--vars-only`, `--refs-only`

**Source:** [02-infrastructure-environment-validation/02-01-SUMMARY.md](../../.planning/phases/02-infrastructure-environment-validation/02-01-SUMMARY.md), [02-dataverse-infrastructure/02-02-SUMMARY.md](../../.planning/phases/02-dataverse-infrastructure/02-02-SUMMARY.md)

---

## 7. Phase 1 Integration Points

### AAMClient.psm1 — Already Wired

Phase 1 built AAMClient.psm1 with 6 exported functions that reference Dataverse tables:

| Function | Table Referenced | Phase 2 Table |
|----------|-----------------|---------------|
| `Connect-AAMDataverse` | — (connection setup) | — |
| `Get-AAMConnection` | — (connection status) | — |
| `Get-AAMEnvironmentVariable` | `environmentvariabledefinitions` + `environmentvariablevalues` | `fsi_AAM_*` env vars |
| `Get-AAMActiveBaseline` | `fsi_accessbaselines` | `fsi_AccessBaseline` |
| `Write-AAMValidationHistory` | `fsi_accessvalidationhistory` | `fsi_AccessValidationHistory` |
| `Write-AAMViolation` | `fsi_accessviolations` | `fsi_AccessViolation` |

**Table name alignment issue:** AAMClient.psm1 currently references `fsi_accessbaselines` (plural), `fsi_accessvalidationhistory`, and `fsi_accessviolations` (plural). The Dataverse Web API entity set names (plural) are auto-generated from the table schema name. The schema creates `fsi_AccessBaseline` → entity set becomes `fsi_accessbaselines`. This means the PowerShell code is already using the correct entity set names.

### Test-AgentAccessCompliance.ps1 — Dataverse Placeholder

The orchestrator has a comment placeholder for Dataverse persistence. Phase 2 Plan 3 will wire this to call `Write-AAMValidationHistory` and `Write-AAMViolation` when `-DataverseUrl` is provided. Unlike SSC (which needed a new `Get-DataverseThreshold.ps1` helper), AAM already has `Get-AAMEnvironmentVariable` in AAMClient.psm1 — the wiring is simpler.

### zone-settings-baseline.json — Continues as Fallback

The local JSON baseline file remains the primary reference for expected zone settings. Dataverse environment variables provide operational parameters (grace period, scan frequency), not zone expected values. The JSON file serves as the fallback source and also as the authoritative zone-to-expected-settings mapping for Compare-ZoneCompliance.ps1.

### Integration Flow

```
Phase 2 Python (deploy.py)         Phase 1 PowerShell (AAMClient.psm1)
─────────────────────────         ──────────────────────────────────
deploy.py                         Connect-AAMDataverse
  ├── create_dataverse_schema     Get-AAMActiveBaseline → fsi_accessbaselines
  │   ├── fsi_AccessBaseline      Write-AAMValidationHistory → fsi_accessvalidationhistory
  │   ├── fsi_AccessValidation... Write-AAMViolation → fsi_accessviolations
  │   └── fsi_AccessViolation     Get-AAMEnvironmentVariable → fsi_AAM_*
  ├── create_environment_vars
  │   └── fsi_AAM_* variables
  └── create_connection_refs
      └── fsi_cr_*_accessmonitor
```

---

## 8. Risks and Dependencies

### Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Option set name collision (fsi_acv_zone already exists) | High (ACV deployed) | Low | Existence check before create (proven pattern) |
| AAMClient.psm1 table name mismatch | Low | Medium | Verify entity set names match Dataverse auto-pluralization |
| Connection reference binding confusion | Medium | Low | Clear post-deployment documentation |
| Cross-repo code duplication (AAMClient ≈ SSCClient ≈ ACVClient) | Certain | Low (accepted) | Future v9: extract shared `fsi_dataverse_client` library |
| TypeMismatch on env var retrieval | Low | Low | Store numeric as Decimal, cast in PowerShell |

### Cross-Repository Concerns

| Concern | Details |
|---------|---------|
| Python scripts deploy to FSI-AgentGov-Solutions | Commits go to companion repo, planning docs stay in FSI-AgentGov |
| AAMClient.psm1 already exists in FSI-AgentGov-Solutions | Phase 2 must not break existing Phase 1 code |
| Shared option sets span solutions | If ACV later changes fsi_acv_zone values, all solutions need review |
| deploy.py requires Dataverse admin access | Service principal or interactive auth with System Administrator role |

### Dependencies

| Dependency | Status | Risk |
|------------|--------|------|
| Phase 1 PowerShell Core complete | ✅ COMPLETE | None |
| FSI-AgentGov-Solutions repo accessible | ✅ Available | Low |
| ACV option set definitions (fsi_acv_zone, fsi_acv_severity) | Defined in code | None (AAM handles both create and reuse) |
| Python 3.10+ available | Standard | Low |
| msal and requests packages | pip installable | None |

---

## 9. Recommended Plan Structure

### Plan Split (3 Plans, 3 Waves)

Following the proven SSC Phase 2 structure exactly:

#### Plan 02-01: AAM Dataverse Client, Requirements, and Three-Table Schema (Wave 1)

**Files:**
- `agent-access-monitor/scripts/aam_client.py`
- `agent-access-monitor/scripts/requirements.txt`
- `agent-access-monitor/scripts/create_dataverse_schema.py`

**Scope:**
- AAMClient class adapted from SSCClient (AAM_ env var prefix, same API surface)
- requirements.txt with msal>=1.30.0 and requests>=2.32.0
- Three-table schema: AccessBaseline (UserOwned), AccessValidationHistory (OrganizationOwned), AccessViolation (UserOwned)
- Shared option set reuse (fsi_acv_zone, fsi_acv_severity) with existence check
- No AAM-specific option sets needed

**Must-haves:**
- AAMClient authenticates with MSAL (interactive + SP)
- AccessValidationHistory is OrganizationOwned (immutable)
- Shared option sets checked for existence before creation
- All operations idempotent and dry-run capable

**Depends on:** Nothing (first plan in phase)

#### Plan 02-02: Environment Variables, Connection References, and deploy.py (Wave 2)

**Files:**
- `agent-access-monitor/scripts/create_environment_variables.py`
- `agent-access-monitor/scripts/create_connection_references.py`
- `agent-access-monitor/scripts/deploy.py`

**Scope:**
- 6 environment variables (fsi_AAM_*): GracePeriodHours, ScanFrequencyHours, IncludeSandbox, BaselineMaxAgeDays, TeamsGroupId, TeamsChannelId
- 3 connection references: fsi_cr_dataverse_accessmonitor, fsi_cr_office365_accessmonitor, fsi_cr_teams_accessmonitor
- deploy.py orchestrator with full/selective deployment and dry-run

**Must-haves:**
- Environment variables use correct types (Decimal for numeric, String for text)
- Connection references follow fsi_cr_ naming convention
- deploy.py supports --tables-only, --vars-only, --refs-only modes
- Post-deployment guidance for security roles and connection binding

**Depends on:** 02-01 (requires aam_client.py)

#### Plan 02-03: Wire Phase 1 PowerShell Scripts to Dataverse (Wave 3)

**Files:**
- `agent-access-monitor/scripts/Test-AgentAccessCompliance.ps1` (modify)

**Scope:**
- Add `-DataverseUrl` and `-DataverseToken` parameters to Test-AgentAccessCompliance.ps1
- When `-DataverseUrl` provided: import AAMClient.psm1, connect, read operational parameters from Dataverse env vars
- After validation runs: write results via `Write-AAMValidationHistory` and violations via `Write-AAMViolation`
- Graceful fallback: when Dataverse unavailable, continue with local baseline and no persistence

**Must-haves:**
- No regression when -DataverseUrl is omitted (standalone mode unchanged)
- Grace period and scan frequency read from Dataverse when available
- Validation results persisted to fsi_accessvalidationhistory
- Individual violations persisted to fsi_accessviolations
- All Dataverse operations fail gracefully (write warnings, don't abort)

**Depends on:** 02-02 (requires environment variables deployed)

### Estimated Timeline

Based on SSC Phase 2 actuals (9 minutes total):

| Plan | Estimated | SSC Actual |
|------|-----------|------------|
| 02-01 | ~5 min | 4 min |
| 02-02 | ~4 min | 3 min |
| 02-03 | ~3 min | 2 min |
| **Total** | **~12 min** | **9 min** |

AAM may take slightly longer due to the additional PowerShell wiring in Plan 3 (AAMClient.psm1 is more feature-rich than SSC's Get-DataverseThreshold.ps1), but the overall structure is proven and predictable.

---

## Common Pitfalls (From ACV/SSC Experience)

1. **Option set naming collision** — Always check `get_global_optionset()` before `create_global_optionset()`. ACV may already have deployed `fsi_acv_zone`.

2. **Environment variable type mismatch** — Store numeric values as Decimal type (100000001) in Dataverse, cast to `[int]` in PowerShell. The `value` field is always a string.

3. **Organization-owned security misconfiguration** — OrganizationOwned removes per-record ownership but doesn't restrict Write/Delete. Security roles must remove these privileges post-deployment.

4. **Connection reference binding** — `create_connection_references.py` creates definitions only. Actual connections are bound during solution import or manual flow configuration. Always document next steps.

5. **Dry-run mode incomplete** — Pass `dry_run` to the client constructor so all mutating operations are centrally guarded. Don't scatter dry-run checks.

6. **Entity set name mismatch** — Dataverse auto-pluralizes: `fsi_AccessBaseline` → `fsi_accessbaselines`. AAMClient.psm1 already uses the plural form.

---

## Sources

### Primary (HIGH confidence — direct workspace examination)

| Source | What it provides |
|--------|-----------------|
| `02-infrastructure-environment-validation/02-01-SUMMARY.md` | ACV Phase 2 architecture, files, option sets, env vars, connection refs |
| `02-dataverse-infrastructure/02-RESEARCH.md` | SSC Phase 2 research (633 lines): patterns, pitfalls, code examples |
| `02-dataverse-infrastructure/02-01-PLAN.md` | SSC schema plan with table/column definitions |
| `02-dataverse-infrastructure/02-02-PLAN.md` | SSC env vars + connection refs plan |
| `02-dataverse-infrastructure/02-03-PLAN.md` | SSC PowerShell wiring plan |
| `02-dataverse-infrastructure/02-01-SUMMARY.md` | SSC schema execution results |
| `02-dataverse-infrastructure/02-02-SUMMARY.md` | SSC env vars execution results |
| `02-dataverse-infrastructure/02-03-SUMMARY.md` | SSC PowerShell wiring results |
| `research/ARCHITECTURE.md` | Cross-solution option set definitions, connection ref naming |
| `research/v6-agent-access-monitor-research.md` | AAM domain research, zone requirements |
| `ROADMAP.md` | v6 Phase 2 success criteria |
| `REQUIREMENTS.md` | INF-01, INF-02, INF-03, INF-05 definitions |
| AAMClient.psm1 (FSI-AgentGov-Solutions) | Phase 1 Dataverse hooks, table references |
| zone-settings-baseline.json (FSI-AgentGov-Solutions) | Zone expected settings reference data |
| Phase 1 summaries (01-01, 01-02, 01-03) | Phase 1 output files and integration points |

### Secondary (MEDIUM confidence — derived from patterns)

| Source | What it provides |
|--------|-----------------|
| SSC Phase 2 duration metrics | Estimated timeline for AAM Phase 2 |
| ACV → SSC adaptation pattern | How to adapt client class naming without changing structure |

## Metadata

**Confidence:** HIGH — AAM Phase 2 is the third iteration of an identical pattern (ACV → SSC → AAM). All unknowns were resolved in prior milestones.

**Research date:** 2026-02-09
**Valid until:** 2026-03-09 (30 days — Dataverse Web API and MSAL patterns are stable)

**Key assumptions:**
- ACV/SSC pattern is appropriate for AAM (same Tier 2 solution architecture)
- fsi_acv_zone and fsi_acv_severity option sets may or may not exist in target environment (AAM handles both cases)
- AAMClient.psm1 entity set names align with Dataverse auto-pluralization
- Python 3.10+ is available in the deployment environment
