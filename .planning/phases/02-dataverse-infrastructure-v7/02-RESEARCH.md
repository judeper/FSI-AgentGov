# Phase 2: Dataverse Infrastructure (v7) — Research

**Researched:** 2026-02-10
**Milestone:** v7 — Content Moderation Governance Monitor
**Domain:** Dataverse schema deployment, Python automation, PowerShell integration
**Confidence:** HIGH

## Summary

Phase 2 creates persistent Dataverse infrastructure for the Content Moderation Governance Monitor — three tables for moderation baselines, immutable validation history, and per-agent violations, plus environment variables for operational thresholds and connection references for Power Automate integration. The Python deployment scripts follow the proven ACV/SSC/AAM pattern (fourth iteration) and are fully idempotent with dry-run support.

**Key finding:** Phase 1 built CMMClient.psm1 (523 lines, 10 exported functions) with Dataverse consumer functions that reference specific table names, column keys, and the `fsi_CMM_` prefix. Phase 2 must create the Python deployment infrastructure that provisions the exact tables, option sets, and environment variables these helpers expect. CMMClient.psm1 is the "consumer" side — Phase 2 builds the "provider" side.

**Critical difference from AAM (v6):** CMM stores **per-agent** moderation baselines, not per-environment access settings. Each baseline and violation record references an individual Copilot Studio agent within an environment. This means:
- `fsi_ModerationBaseline` includes `fsi_agent_id` and `fsi_agent_name` columns (AAM's `fsi_AccessBaseline` only has environment-level granularity)
- `fsi_ModerationViolation` includes `fsi_agent_id`, `fsi_agent_name`, `fsi_expected_level`, and `fsi_actual_level` (not generic `fsi_expected_value`/`fsi_actual_value`)
- `fsi_ModerationValidationHistory` includes `fsi_total_agents` and `fsi_environments_scanned` (not just `fsi_total_environments`)

**Primary recommendation:** Follow the ACV/SSC/AAM Python deployment pattern exactly, adapting table definitions to CMM's three-table schema while reusing existing `fsi_acv_zone` and `fsi_acv_severity` option sets. The column names must match CMMClient.psm1's property keys precisely.

---

## 1. Existing Patterns (ACV/SSC/AAM Dataverse Infrastructure)

### File Structure (Proven Across 3 Solutions)

ACV (v4), SSC (v5), and AAM (v6) all follow an identical 6-file pattern deployed to `FSI-AgentGov-Solutions/{solution}/scripts/`:

```
audit-configuration-validator/scripts/     agent-access-monitor/scripts/
├── acv_client.py                          ├── aam_client.py
├── create_dataverse_schema.py             ├── create_dataverse_schema.py
├── create_environment_variables.py        ├── create_environment_variables.py
├── create_connection_references.py        ├── create_connection_references.py
├── deploy.py                              ├── deploy.py
└── requirements.txt                       └── requirements.txt
```

**Source:** Phase 2 summaries from v4 (ACV), v5 (SSC), v6 (AAM)

### Key Classes and Methods

The `{SOLUTION}Client` class (ACVClient, SSCClient, AAMClient → CMMClient) provides:

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

**Standard libraries:** `msal>=1.30.0`, `requests>=2.32.0`. No Azure SDK dependencies.

**Retry strategy:** `Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])`

**Environment variable prefix convention:**
- ACV: `ACV_TENANT_ID`, `ACV_ENVIRONMENT_URL`, `ACV_CLIENT_ID`, `ACV_CLIENT_SECRET`
- SSC: `SSC_TENANT_ID`, `SSC_ENVIRONMENT_URL`, etc.
- AAM: `AAM_TENANT_ID`, `AAM_ENVIRONMENT_URL`, etc.
- **CMM: `CMM_TENANT_ID`, `CMM_ENVIRONMENT_URL`, `CMM_CLIENT_ID`, `CMM_CLIENT_SECRET`**

### ACV Dataverse Schema (Original Pattern)

**Tables:** 2 (organization-owned)
- `fsi_auditvalidationhistory` — 12 columns, immutable append-only
- `fsi_environmentregistry` — 9 columns, admin-managed

**Option sets:** 5 global (2 shared across all solutions)
- `fsi_acv_zone` — Unclassified(0), Zone 1(1), Zone 2(2), Zone 3(3)
- `fsi_acv_severity` — Passed(1), Warning(2), GracePeriod(3), Failed(4), Error(5)

**Source:** 02-infrastructure-environment-validation/02-01-SUMMARY.md

### AAM Dataverse Schema (Immediate Predecessor)

**Tables:** 3 (mixed ownership)
- `fsi_AccessBaseline` — UserOwned (operators manage baselines)
- `fsi_AccessValidationHistory` — OrganizationOwned (immutable audit log)
- `fsi_AccessViolation` — UserOwned (operators acknowledge violations)

**Option sets:** Reuses `fsi_acv_zone` + `fsi_acv_severity`, no AAM-specific option sets.

**Environment variables:** 6 (`fsi_AAM_*` prefix)
- `fsi_AAM_GracePeriodHours` (48), `fsi_AAM_ScanFrequencyHours` (24), `fsi_AAM_IncludeSandbox` (false)
- `fsi_AAM_BaselineMaxAgeDays` (30), `fsi_AAM_TeamsGroupId` (""), `fsi_AAM_TeamsChannelId` ("")

**Connection references:** 3
- `fsi_cr_dataverse_accessmonitor`, `fsi_cr_office365_accessmonitor`, `fsi_cr_teams_accessmonitor`

**Source:** 02-dataverse-infrastructure-v6 (02-01-SUMMARY.md, 02-02-SUMMARY.md, 02-VERIFICATION.md)

### Proven 3-Plan Split (AAM Phase 2 Actuals)

| Plan | Wave | Contents | AAM Duration |
|------|------|----------|--------------|
| 02-01 | 1 | Client library + requirements + schema (3 tables + option sets) | 12 min |
| 02-02 | 2 | Environment variables + connection references + deploy.py orchestrator | 8 min |
| 02-03 | 3 | Wire Phase 1 PowerShell to read thresholds from Dataverse | 8 min |

**Total AAM Phase 2 time:** ~28 minutes across 3 plans. CMM should follow this exact split.

---

## 2. CMM-Specific Schema Design

### Key Difference: Per-Agent Granularity

AAM stores per-environment access setting baselines. CMM stores **per-agent moderation level baselines**. This fundamental difference affects all three tables:

| Aspect | AAM (v6) | CMM (v7) |
|--------|----------|----------|
| Baseline granularity | One baseline per environment | One baseline per agent per environment |
| Baseline columns | `fsi_bot_limit_sharing_mode`, `fsi_bot_authoring_sharing_disabled`, etc. | `fsi_moderation_level`, `fsi_agent_id`, `fsi_agent_name` |
| Violation granularity | Per-environment, per-setting | Per-agent |
| Violation columns | `fsi_violation_type`, `fsi_expected_value`, `fsi_actual_value` | `fsi_expected_level`, `fsi_actual_level`, `fsi_agent_id`, `fsi_agent_name` |
| History columns | `fsi_total_environments` | `fsi_total_agents`, `fsi_environments_scanned` |
| Table logical names | `fsi_accessbaseline` | `fsi_moderationbaseline` |

### CMMClient.psm1 Consumer Function Analysis

The following CMMClient.psm1 functions define the **exact column keys** that Phase 2 must deploy. These are the authoritative interface:

#### `Get-ModerationBaseline` (queries `fsi_moderationbaselines`)
```
$filter=statecode eq 0 [and fsi_environment_guid eq '{guid}']
$select=fsi_name,fsi_environment_guid,fsi_environment_name,fsi_zone,fsi_agent_id,
        fsi_agent_name,fsi_moderation_level,fsi_is_active,fsi_captured_at,
        fsi_captured_by,fsi_raw_json
```

#### `Write-ModerationValidationHistory` (POSTs to `fsi_moderationvalidationhistory`)
```json
{
  "fsi_name": "...",
  "fsi_run_id": "...",
  "fsi_validation_time": "...",
  "fsi_total_agents": 0,
  "fsi_compliant_count": 0,
  "fsi_violation_count": 0,
  "fsi_overall_status": "...",
  "fsi_environments_scanned": "...",
  "fsi_summary_json": "..."
}
```

#### `Write-ModerationViolation` (POSTs to `fsi_moderationviolations`)
```json
{
  "fsi_name": "...",
  "fsi_environment_guid": "...",
  "fsi_environment_name": "...",
  "fsi_agent_id": "...",
  "fsi_agent_name": "...",
  "fsi_zone": 0,
  "fsi_expected_level": "...",
  "fsi_actual_level": "...",
  "fsi_severity": 0,
  "fsi_regulatory_context": "...",
  "fsi_detected_at": "...",
  "fsi_run_id": "..."
}
```

#### `Save-CMMBaseline` (POSTs to `fsi_moderationbaselines`)
```json
{
  "fsi_name": "...",
  "fsi_environment_guid": "...",
  "fsi_environment_name": "...",
  "fsi_zone": 0,
  "fsi_agent_id": "...",
  "fsi_agent_name": "...",
  "fsi_moderation_level": "...",
  "fsi_captured_by": "...",
  "fsi_captured_at": "...",
  "fsi_is_active": true,
  "fsi_raw_json": "..."
}
```

#### `Get-CMMLastValidation` (queries `fsi_moderationvalidationhistory`)
```
$orderby=fsi_validation_time desc
$top=1
$select=fsi_name,fsi_run_id,fsi_validation_time,fsi_total_agents,
        fsi_compliant_count,fsi_violation_count,fsi_overall_status,
        fsi_environments_scanned,fsi_summary_json
```

#### `Get-CMMEnvironmentVariable` (queries `environmentvariabledefinitions`)
```
$filter=schemaname eq 'fsi_CMM_{Name}'
$expand=environmentvariablevalues
```

### Table 1: fsi_ModerationBaseline (UserOwned)

Stores per-agent content moderation level snapshots. Operators capture, activate, and deactivate baselines. Each record represents a single agent's moderation configuration at a point in time.

| SchemaName | Type | Required | Description | CMMClient Key |
|------------|------|----------|-------------|---------------|
| `fsi_name` | String(200) | Yes | Baseline ID (e.g., "contoso-trading-z3-agent1-2026-02-10") | `fsi_name` (primary name) |
| `fsi_environment_guid` | String(100) | Yes | Power Platform environment GUID | `fsi_environment_guid` |
| `fsi_environment_name` | String(500) | Yes | Environment display name | `fsi_environment_name` |
| `fsi_zone` | Picklist (fsi_acv_zone) | Yes | Zone classification | `fsi_zone` |
| `fsi_agent_id` | String(100) | Yes | Copilot Studio bot GUID (botid) | `fsi_agent_id` |
| `fsi_agent_name` | String(500) | Yes | Agent display name | `fsi_agent_name` |
| `fsi_moderation_level` | String(50) | Yes | Captured moderation level (Low/Medium/High) | `fsi_moderation_level` |
| `fsi_is_active` | Boolean | Yes | Whether this is the current active baseline | `fsi_is_active` |
| `fsi_captured_at` | DateTime | Yes | When baseline was captured | `fsi_captured_at` |
| `fsi_captured_by` | String(200) | No | UPN of operator who captured | `fsi_captured_by` |
| `fsi_raw_json` | Memo(100000) | No | Full JSON snapshot of agent configuration | `fsi_raw_json` |

**Column count:** 11 (including system fsi_name)

**Ownership:** UserOwned — operators need CRUD lifecycle management for baselines (capture new, deactivate old).

**Audit:** IsAuditEnabled = True

**Key difference from AAM:** Includes `fsi_agent_id` and `fsi_agent_name` (AAM had no agent concept). Uses `fsi_moderation_level` (a single string) instead of AAM's three `fsi_bot_*` settings columns. This is simpler because moderation is a single tri-state value (Low/Medium/High) rather than multiple access settings.

**Key queries (CMMClient.psm1):**
- "Get active baselines for environment X" → `$filter=statecode eq 0 and fsi_environment_guid eq '{guid}'`
- "Get all active baselines" → `$filter=statecode eq 0`
- "Save baseline" → POST with all fields populated

### Table 2: fsi_ModerationValidationHistory (OrganizationOwned — IMMUTABLE)

Immutable append-only audit log of all moderation validation scan results. CRITICAL for regulatory compliance (FINRA 4511, SEC 17a-3). Each record summarizes one scan execution.

| SchemaName | Type | Required | Description | CMMClient Key |
|------------|------|----------|-------------|---------------|
| `fsi_name` | String(200) | Yes | Validation ID (e.g., "Passed-2026-02-10T14:30:00Z") | `fsi_name` (primary name) |
| `fsi_run_id` | String(36) | Yes | GUID correlating all records in one scan execution | `fsi_run_id` |
| `fsi_validation_time` | DateTime | Yes | When validation ran | `fsi_validation_time` |
| `fsi_total_agents` | Integer | Yes | Total agents scanned across all environments | `fsi_total_agents` |
| `fsi_compliant_count` | Integer | Yes | Agents passing all checks | `fsi_compliant_count` |
| `fsi_violation_count` | Integer | Yes | Agents with violations | `fsi_violation_count` |
| `fsi_overall_status` | String(50) | Yes | Critical / Failed / Review / Passed | `fsi_overall_status` |
| `fsi_environments_scanned` | String(2000) | No | Comma-separated list or JSON of scanned environment names | `fsi_environments_scanned` |
| `fsi_summary_json` | Memo(100000) | No | Full JSON validation result | `fsi_summary_json` |

**Column count:** 9 (including system fsi_name)

**Ownership:** OrganizationOwned — operators cannot modify or delete audit records. Post-deployment, security roles must remove Write/Delete privileges.

**Audit:** IsAuditEnabled = True

**Key difference from AAM:** Uses `fsi_total_agents` instead of `fsi_total_environments` (CMM validates at agent granularity). Adds `fsi_environments_scanned` to record which environments were covered. Does NOT have `fsi_zone` or `fsi_severity` picklists on the history table — the CMMClient.psm1 consumer functions write summary-level records, with per-agent detail in the violations table and in `fsi_summary_json`.

**Design note:** The `Write-ModerationValidationHistory` function in CMMClient.psm1 generates `fsi_name` as `"$($OverallStatus)-$(Get-Date -Format 'yyyy-MM-ddTHH:mm:ssZ')"`. The `fsi_validation_time` column matches the CMMClient.psm1 property name exactly.

### Table 3: fsi_ModerationViolation (UserOwned)

Per-agent violations detected by Compare-ModerationCompliance.ps1. Each record represents one agent whose content moderation level does not meet its zone's requirement.

| SchemaName | Type | Required | Description | CMMClient Key |
|------------|------|----------|-------------|---------------|
| `fsi_name` | String(200) | Yes | Violation ID (e.g., "Zone3-AgentX-Medium-2026-02-10") | `fsi_name` (primary name) |
| `fsi_environment_guid` | String(100) | Yes | Environment GUID containing the agent | `fsi_environment_guid` |
| `fsi_environment_name` | String(500) | Yes | Environment display name | `fsi_environment_name` |
| `fsi_agent_id` | String(100) | Yes | Violating agent's bot GUID | `fsi_agent_id` |
| `fsi_agent_name` | String(500) | Yes | Agent display name | `fsi_agent_name` |
| `fsi_zone` | Picklist (fsi_acv_zone) | Yes | Zone classification of hosting environment | `fsi_zone` |
| `fsi_expected_level` | String(50) | Yes | Zone-required moderation level (Medium/High) | `fsi_expected_level` |
| `fsi_actual_level` | String(50) | Yes | Agent's current moderation level (Low/Medium) | `fsi_actual_level` |
| `fsi_severity` | Picklist (fsi_acv_severity) | Yes | Violation severity (Failed/Warning/Error) | `fsi_severity` |
| `fsi_regulatory_context` | String(2000) | No | FINRA/SOX/GLBA impact statement | `fsi_regulatory_context` |
| `fsi_detected_at` | DateTime | Yes | When violation was detected | `fsi_detected_at` |
| `fsi_run_id` | String(36) | No | Correlating scan execution GUID | `fsi_run_id` |

**Column count:** 12 (including system fsi_name)

**Ownership:** UserOwned — operators may need to acknowledge, annotate, or manage violation lifecycle in Phase 3.

**Audit:** IsAuditEnabled = True

**Key difference from AAM:** CMM violations reference individual agents (`fsi_agent_id`, `fsi_agent_name`) rather than just environments. Uses `fsi_expected_level` / `fsi_actual_level` (simple strings) instead of AAM's generic `fsi_expected_value` / `fsi_actual_value` — this is cleaner because moderation is always a level comparison. No `fsi_acknowledged`/`fsi_acknowledged_by`/`fsi_resolved_at`/`fsi_notes` columns in initial deployment — these acknowledgement workflow columns are deferred to Phase 3 if needed (keeping the violation table aligned with what CMMClient.psm1 actually writes today).

**Design note:** The `Write-ModerationViolation` function writes `fsi_zone` and `fsi_severity` as integer values (picklist option values). The schema must bind these columns to the `fsi_acv_zone` and `fsi_acv_severity` global option sets respectively.

### Entity Set Name Alignment

Dataverse auto-pluralizes entity set names from table schema names:

| Table Schema Name | Entity Set Name | CMMClient.psm1 Reference |
|-------------------|-----------------|--------------------------|
| `fsi_ModerationBaseline` | `fsi_moderationbaselines` | ✅ `fsi_moderationbaselines` |
| `fsi_ModerationValidationHistory` | `fsi_moderationvalidationhistorys` | ⚠️ CMMClient uses `fsi_moderationvalidationhistory` |
| `fsi_ModerationViolation` | `fsi_moderationviolations` | ✅ `fsi_moderationviolations` |

**CRITICAL ISSUE — Pluralization mismatch on ValidationHistory:**

Dataverse auto-pluralization appends 's' to the logical name, producing `fsi_moderationvalidationhistorys` — which is grammatically awkward and may not match what CMMClient.psm1 uses. The CMMClient.psm1 likely references `fsi_moderationvalidationhistory` (without plural 's').

**Resolution:** Set the `EntitySetName` explicitly in the table definition to `fsi_moderationvalidationhistory` (matching the CMMClient.psm1 reference). This overrides auto-pluralization. The AAM precedent used `fsi_accessvalidationhistory` (no trailing 's') for the same reason.

```python
# In create_dataverse_schema.py
"EntitySetName": "fsi_moderationvalidationhistory",
```

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

### Reuse Pattern (Proven in SSC, AAM)

```python
# In create_dataverse_schema.py
SHARED_OPTIONSETS = {
    "fsi_acv_zone": { ... full definition ... },
    "fsi_acv_severity": { ... full definition ... },
}

def create_shared_optionsets(client, dry_run=False):
    for name, definition in SHARED_OPTIONSETS.items():
        existing = client.get_global_optionset(name)
        if existing:
            print(f"  {name}: already exists (from ACV or other solution), reusing")
            continue
        if dry_run:
            print(f"  {name}: would create")
        else:
            client.create_global_optionset(definition)
```

**Key rule:** CMM never creates its own zone or severity option sets. It checks for existing global option sets and reuses them. If ACV/SSC/AAM haven't been deployed, CMM creates them using the same canonical definitions.

### CMM-Specific Option Sets

**Decision: No CMM-specific option sets needed.** Content moderation is a simple tri-state (Low/Medium/High) captured as a string column (`fsi_moderation_level`, `fsi_expected_level`, `fsi_actual_level`). Unlike SSC (which needed `fsi_ssc_validationtype` with 6 validator types), CMM violations are straightforward level comparisons. This reduces deployment complexity.

**Source:** AAM research (02-dataverse-infrastructure-v6/02-RESEARCH.md) — same decision made for AAM.

---

## 4. Environment Variables

### fsi_CMM_* Variable Design

CMM's moderation thresholds are structural governance decisions defined in `moderation-baseline.json` (Zone 1: Medium minimum, Zone 2: High, Zone 3: High). These are not tunable runtime parameters — changing them requires policy review. Environment variables should externalize **operational parameters** that operators tune without code changes:

| Schema Name | Display Name | Type | Default | Description |
|-------------|-------------|------|---------|-------------|
| `fsi_CMM_GracePeriodHours` | CMM - Grace Period (Hours) | Decimal (100000001) | 48 | Hours to exclude newly created agents from violation reporting |
| `fsi_CMM_ScanFrequencyHours` | CMM - Scan Frequency (Hours) | Decimal (100000001) | 24 | How often automated scans run |
| `fsi_CMM_IncludeSandbox` | CMM - Include Sandbox Environments | String (100000000) | false | Whether to include sandbox environments in validation |
| `fsi_CMM_IncludeDrafts` | CMM - Include Draft Agents | String (100000000) | false | Whether to include draft/unpublished agents in validation |
| `fsi_CMM_BaselineMaxAgeDays` | CMM - Maximum Baseline Age (Days) | Decimal (100000001) | 30 | Alert threshold for stale agent baselines |
| `fsi_CMM_TeamsGroupId` | CMM - Teams Alert Group ID | String (100000000) | (blank) | Teams group GUID for violation alerts |
| `fsi_CMM_TeamsChannelId` | CMM - Teams Alert Channel ID | String (100000000) | (blank) | Teams channel GUID for violation alerts |

**Count:** 7 variables (AAM had 6 — CMM adds `IncludeDrafts` because per-agent filtering is a CMM-specific concern)

**Type mapping:**
- Decimal (100000001) — for numeric values (hours, days)
- String (100000000) — for text values (boolean strings, GUIDs)

**Why `fsi_CMM_IncludeDrafts` is new:** AAM had no concept of draft vs. published entities. CMM's per-agent granularity means operators need to control whether draft agents are validated (CMV-05 success criterion). Default `false` means only published agents are validated.

### CMMClient.psm1 Integration

The existing `Get-CMMEnvironmentVariable` function in CMMClient.psm1 already queries Dataverse for `fsi_CMM_*` environment variables:

```powershell
$schemaName = "fsi_CMM_$Name"
$uri = "$script:DataverseUrl/api/data/v9.2/environmentvariabledefinitions?" +
       "`$filter=schemaname eq '$schemaName'&" +
       "`$expand=environmentvariablevalues"
```

Phase 2 creates the environment variables; CMMClient.psm1 consumes them. Phase 1 scripts already accept `-GracePeriodHours`, `-IncludeDrafts`, etc. as parameters. Phase 2 Plan 3 wires these to read from Dataverse when `-DataverseUrl` is provided, with parameter values falling back to local defaults.

---

## 5. Connection References

### CMM Connection References

Following the `fsi_cr_{connector}_{solution}` naming convention:

| Logical Name | Display Name | Connector ID | Purpose |
|-------------|-------------|-------------|---------|
| `fsi_cr_dataverse_moderationmonitor` | Dataverse - Content Moderation Monitor | `shared_commondataserviceforapps` | Read/write baselines, validation history, violations |
| `fsi_cr_office365_moderationmonitor` | Office 365 - Content Moderation Monitor | `shared_office365` | Email alerts for critical moderation violations |
| `fsi_cr_teams_moderationmonitor` | Teams - Content Moderation Monitor | `shared_teams` | Teams adaptive card alerts for moderation violations |

### Cross-Solution Connection Reference Inventory

| Solution | Dataverse | Office 365 | Teams |
|----------|-----------|------------|-------|
| ACV (v4) | `fsi_cr_dataverse_auditvalidation` | `fsi_cr_office365_auditvalidation` | — |
| SSC (v5) | `fsi_cr_dataverse_sessionvalidation` | `fsi_cr_office365_sessionvalidation` | `fsi_cr_teams_sessionvalidation` |
| AAM (v6) | `fsi_cr_dataverse_accessmonitor` | `fsi_cr_office365_accessmonitor` | `fsi_cr_teams_accessmonitor` |
| **CMM (v7)** | `fsi_cr_dataverse_moderationmonitor` | `fsi_cr_office365_moderationmonitor` | `fsi_cr_teams_moderationmonitor` |

**Note:** Connection references are definitions only. Actual connection binding happens during solution import or manual configuration in Power Automate. Deployment script outputs post-deployment binding instructions.

---

## 6. Deployment Script Architecture

### Files Needed

CMM follows the identical 6-file structure from ACV/SSC/AAM:

| File | Responsibility | Key Contents |
|------|---------------|-------------|
| `cmm_client.py` | Dataverse Web API client | `class CMMClient`: MSAL auth, retry, dry-run, idempotent helpers |
| `create_dataverse_schema.py` | Table and option set deployment | 3 tables (ModerationBaseline, ModerationValidationHistory, ModerationViolation) + shared option set reuse |
| `create_environment_variables.py` | Env var deployment | 7 variables with `fsi_CMM_*` prefix |
| `create_connection_references.py` | Connection ref deployment | 3 refs (`fsi_cr_*_moderationmonitor`) |
| `deploy.py` | Orchestrator | Full/selective deployment (--tables-only, --vars-only, --refs-only), dry-run, post-deployment guidance |
| `requirements.txt` | Python dependencies | `msal>=1.30.0`, `requests>=2.32.0` |

**Deployment path:** `content-moderation-monitor/scripts/`

### CMMClient Differences from AAMClient

| Aspect | AAMClient | CMMClient |
|--------|-----------|-----------|
| Class name | `AAMClient` | `CMMClient` |
| Env var prefix | `AAM_` | `CMM_` |
| Docstrings | "Agent Access Governance Monitor" | "Content Moderation Governance Monitor" |
| API methods | Identical | Identical |
| Auth flow | Identical | Identical |
| Retry logic | Identical | Identical |

Everything else is structurally identical — a direct adaptation with solution-specific naming.

### deploy.py Orchestrator Pattern

```
deploy.py
├── Step 1: Test Connection
├── Step 2: Dataverse Schema (create_dataverse_schema.create_schema)
│   ├── Shared option sets (fsi_acv_zone, fsi_acv_severity)
│   ├── fsi_ModerationBaseline (UserOwned)
│   ├── fsi_ModerationValidationHistory (OrganizationOwned)
│   └── fsi_ModerationViolation (UserOwned)
├── Step 3: Environment Variables (create_environment_variables.create_environment_variables)
│   └── 7 fsi_CMM_* variables
├── Step 4: Connection References (create_connection_references.create_connection_references)
│   └── 3 fsi_cr_*_moderationmonitor references
└── Post-Deployment Guidance
    ├── Security: Remove Write/Delete on fsi_ModerationValidationHistory
    ├── Connections: Bind connection references in Power Automate
    └── Verification: Run deploy.py --dry-run to confirm
```

**CLI arguments:** `--tenant-id`, `--client-id`, `--client-secret`, `--environment-url`, `--interactive`, `--dry-run`, `--tables-only`, `--vars-only`, `--refs-only`, `--verbose`

### Idempotent Deployment Pattern

All deployment scripts follow the same check-before-create pattern:

```python
# Check existence before create
existing = client.get_entity_metadata("fsi_moderationbaseline")
if existing:
    print(f"  fsi_moderationbaseline: already exists, skipping")
else:
    if dry_run:
        print(f"  fsi_moderationbaseline: would create")
    else:
        client.create_entity(entity_definition)
        print(f"  fsi_moderationbaseline: created")
```

---

## 7. Phase 1 Integration Points

### CMMClient.psm1 — Already Wired (10 Functions)

Phase 1 built CMMClient.psm1 with 10 exported functions. Six reference Dataverse tables that Phase 2 provisions:

| Function | Table/Entity Referenced | Phase 2 Provisions |
|----------|------------------------|-------------------|
| `Connect-CMMDataverse` | — (connection setup) | — |
| `Get-CMMConnection` | — (connection status) | — |
| `Get-CMMEnvironmentVariable` | `environmentvariabledefinitions` + `environmentvariablevalues` | `fsi_CMM_*` env vars |
| `Get-ModerationBaseline` | `fsi_moderationbaselines` | `fsi_ModerationBaseline` table |
| `Write-ModerationValidationHistory` | `fsi_moderationvalidationhistory` | `fsi_ModerationValidationHistory` table |
| `Write-ModerationViolation` | `fsi_moderationviolations` | `fsi_ModerationViolation` table |
| `Save-CMMBaseline` | `fsi_moderationbaselines` | `fsi_ModerationBaseline` table |
| `Get-CMMLastValidation` | `fsi_moderationvalidationhistory` | `fsi_ModerationValidationHistory` table |
| `Get-AgentBots` | `bots` (per-environment) | — (built-in Dataverse table) |
| `Get-BotModerationLevel` | — (in-memory processing) | — |

**Entity set name alignment:** CMMClient.psm1 uses entity set names (plural forms) in its Web API calls. Phase 2 must ensure the deployed table definitions produce matching entity set names:
- `fsi_moderationbaselines` ✅ (auto-plural of `fsi_moderationbaseline`)
- `fsi_moderationvalidationhistory` ⚠️ (set `EntitySetName` explicitly to avoid `fsi_moderationvalidationhistorys`)
- `fsi_moderationviolations` ✅ (auto-plural of `fsi_moderationviolation`)

### Test-ContentModerationCompliance.ps1 — Dataverse Wiring Points

The orchestrator needs Phase 2 wiring to:

1. **Read operational parameters from Dataverse env vars** when `-DataverseUrl` is provided:
   - `GracePeriodHours` → `fsi_CMM_GracePeriodHours`
   - `IncludeDrafts` → `fsi_CMM_IncludeDrafts`
   - `IncludeSandbox` → `fsi_CMM_IncludeSandbox`

2. **Persist validation results** when `-PersistResults` is provided:
   - Summary → `Write-ModerationValidationHistory` with RunId correlation
   - Each violation → `Write-ModerationViolation` with RunId correlation

3. **Graceful fallback** when Dataverse is unavailable — log warning, continue with local baseline/defaults

### New Parameters for Test-ContentModerationCompliance.ps1

```powershell
[Parameter(Mandatory = $false)]
[string]$DataverseToken,       # Pre-obtained Dataverse token (for automation)

[Parameter(Mandatory = $false)]
[switch]$PersistResults        # Opt-in persistence to Dataverse
```

**Behavior matrix:**

| Parameters | Behavior |
|-----------|----------|
| No Dataverse params | Standalone mode (unchanged from Phase 1) |
| `-DataverseUrl` only | Read env vars from Dataverse, no persistence |
| `-DataverseUrl -PersistResults` | Full integration: read env vars + persist results |
| `-DataverseUrl -PersistResults -WhatIf` | Preview what would be persisted without writing |

### moderation-baseline.json — Continues as Fallback

The local JSON baseline file remains the primary reference for expected zone moderation levels. Dataverse environment variables provide operational parameters (grace period, scan frequency, include drafts), not zone-level moderation requirements. The JSON serves as:
1. Authoritative zone-to-expected-moderation-level mapping
2. Severity matrix source
3. Regulatory context strings

### Integration Flow Diagram

```
Phase 2 Python (deploy.py)              Phase 1 PowerShell (CMMClient.psm1)
─────────────────────────               ──────────────────────────────────
deploy.py                               Connect-CMMDataverse
  ├── create_dataverse_schema            Get-ModerationBaseline → fsi_moderationbaselines
  │   ├── fsi_ModerationBaseline         Save-CMMBaseline → fsi_moderationbaselines
  │   ├── fsi_ModerationValidation...    Write-ModerationValidationHistory → fsi_moderationvalidationhistory
  │   └── fsi_ModerationViolation        Write-ModerationViolation → fsi_moderationviolations
  ├── create_environment_vars            Get-CMMEnvironmentVariable → fsi_CMM_*
  │   └── fsi_CMM_* variables            Get-CMMLastValidation → fsi_moderationvalidationhistory
  └── create_connection_refs
      └── fsi_cr_*_moderationmonitor
```

### Write-ModerationValidationHistory Updates Needed

The existing function needs `-RunId` parameter support:

```powershell
function Write-ModerationValidationHistory {
    param(
        [Parameter(Mandatory)]
        [hashtable]$ValidationResult,

        [Parameter(Mandatory)]
        [string]$RunId
    )
    $record = @{
        fsi_name                = "$($ValidationResult.OverallStatus)-$(Get-Date -Format 'yyyy-MM-ddTHH:mm:ssZ')"
        fsi_run_id              = $RunId
        fsi_validation_time     = (Get-Date).ToUniversalTime().ToString('o')
        fsi_total_agents        = $ValidationResult.TotalAgents
        fsi_compliant_count     = $ValidationResult.CompliantCount
        fsi_violation_count     = $ValidationResult.ViolationCount
        fsi_overall_status      = $ValidationResult.OverallStatus
        fsi_environments_scanned = $ValidationResult.EnvironmentsScanned
        fsi_summary_json        = $ValidationResult | ConvertTo-Json -Depth 10 -Compress
    }
    # POST to fsi_moderationvalidationhistory
}
```

### Write-ModerationViolation Updates Needed

```powershell
function Write-ModerationViolation {
    param(
        [Parameter(Mandatory)]
        [hashtable]$Violation,

        [Parameter()]
        [string]$RunId
    )
    $record = @{
        fsi_name               = "$($Violation.AgentName)-$($Violation.Zone)-$(Get-Date -Format 'yyyy-MM-dd')"
        fsi_environment_guid   = $Violation.EnvironmentGuid
        fsi_environment_name   = $Violation.EnvironmentName
        fsi_agent_id           = $Violation.AgentId
        fsi_agent_name         = $Violation.AgentName
        fsi_zone               = $Violation.Zone           # Integer picklist value
        fsi_expected_level     = $Violation.ExpectedLevel
        fsi_actual_level       = $Violation.ActualLevel
        fsi_severity           = $Violation.Severity       # Integer picklist value
        fsi_regulatory_context = $Violation.RegulatoryContext
        fsi_detected_at        = (Get-Date).ToUniversalTime().ToString('o')
    }
    if ($RunId) { $record['fsi_run_id'] = $RunId }
    # POST to fsi_moderationviolations
}
```

---

## 8. Risks and Dependencies

### Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Option set name collision (fsi_acv_zone already exists) | High (ACV deployed) | Low | Existence check before create (proven pattern from AAM/SSC) |
| Entity set name pluralization mismatch (fsi_moderationvalidationhistorys) | High | Medium | Set `EntitySetName` explicitly in table definition |
| CMMClient.psm1 property key mismatch | Low | High | Cross-reference every column against CMMClient.psm1 functions (done in Section 2) |
| Connection reference binding confusion | Medium | Low | Clear post-deployment documentation (same as AAM) |
| Cross-repo code duplication (CMMClient ≈ AAMClient ≈ SSCClient) | Certain | Low (accepted) | Future v9: extract shared `fsi_dataverse_client` library |
| TypeMismatch on env var retrieval | Low | Low | Store numeric as Decimal type, cast in PowerShell |
| fsi_zone/fsi_severity integer values differ from CMMClient expectations | Low | Medium | Verify picklist option binding in schema script; CMMClient.psm1 writes integer values that match option set definitions |

### Cross-Repository Concerns

| Concern | Details |
|---------|---------|
| Python scripts deploy to FSI-AgentGov-Solutions | Commits go to companion repo, planning docs stay in FSI-AgentGov |
| CMMClient.psm1 already exists in FSI-AgentGov-Solutions | Phase 2 Plan 3 modifies it — must not break Phase 1 behavior |
| Shared option sets span solutions | If ACV later changes fsi_acv_zone values, all solutions need review |
| deploy.py requires Dataverse admin access | Service principal or interactive auth with System Administrator role |

### Dependencies

| Dependency | Status | Risk |
|------------|--------|------|
| Phase 1 PowerShell Core complete | ✅ COMPLETE (3/3 plans, verified 2026-02-10) | None |
| FSI-AgentGov-Solutions repo accessible | ✅ Available | Low |
| ACV option set definitions (fsi_acv_zone, fsi_acv_severity) | Defined in code (shared across solutions) | None (CMM handles both create and reuse) |
| Python 3.10+ available | Standard | Low |
| msal and requests packages | pip installable | None |
| CMMClient.psm1 exported function signatures | Stable from Phase 1 | None (interface is frozen) |

### Validation History Column Comparison (AAM → CMM)

This cross-check ensures no columns are missed:

| AAM Column | CMM Column | Change |
|------------|------------|--------|
| `fsi_name` | `fsi_name` | Same |
| `fsi_run_id` | `fsi_run_id` | Same |
| `fsi_zone` | — | **Removed** (CMM validation history is aggregate, not per-zone) |
| `fsi_severity` | — | **Removed** (same reason) |
| `fsi_total_environments` | `fsi_total_agents` | **Renamed** (per-agent granularity) |
| `fsi_compliant_count` | `fsi_compliant_count` | Same |
| `fsi_violation_count` | `fsi_violation_count` | Same |
| `fsi_overall_status` | `fsi_overall_status` | Same |
| `fsi_summary_json` | `fsi_summary_json` | Same |
| `fsi_validation_time` | `fsi_validation_time` | Same |
| — | `fsi_environments_scanned` | **Added** (multi-environment tracking) |

---

## 9. Recommended Plan Structure

### Plan Split (3 Plans, 3 Waves)

Following the proven AAM Phase 2 structure:

#### Plan 02-01: CMM Dataverse Client, Requirements, and Three-Table Schema (Wave 1)

**Files:**
- `content-moderation-monitor/scripts/cmm_client.py` (CREATE)
- `content-moderation-monitor/scripts/requirements.txt` (CREATE)
- `content-moderation-monitor/scripts/create_dataverse_schema.py` (CREATE)

**Scope:**
- CMMClient class adapted from AAMClient (CMM_ env var prefix, same API surface)
- requirements.txt with msal>=1.30.0 and requests>=2.32.0
- Three-table schema: ModerationBaseline (UserOwned), ModerationValidationHistory (OrganizationOwned), ModerationViolation (UserOwned)
- Shared option set reuse (fsi_acv_zone, fsi_acv_severity) with existence check
- No CMM-specific option sets needed
- Explicit EntitySetName on ValidationHistory to avoid pluralization mismatch

**Must-haves:**
- CMMClient authenticates with MSAL (interactive + SP)
- ModerationValidationHistory is OrganizationOwned (immutable)
- Shared option sets checked for existence before creation
- All operations idempotent and dry-run capable
- Column SchemaNames match CMMClient.psm1 property keys exactly
- EntitySetName set explicitly to `fsi_moderationvalidationhistory`

**Acceptance criteria:**
1. `python -c "from cmm_client import CMMClient; print('Import OK')"` → passes
2. `python create_dataverse_schema.py --dry-run --interactive` → previews 3 tables + 2 option sets
3. Table ownership: Baseline=UserOwned, History=OrganizationOwned, Violation=UserOwned
4. Schema re-run produces no side effects (idempotent)

**Depends on:** Nothing (first plan in phase)

#### Plan 02-02: Environment Variables, Connection References, and deploy.py (Wave 2)

**Files:**
- `content-moderation-monitor/scripts/create_environment_variables.py` (CREATE)
- `content-moderation-monitor/scripts/create_connection_references.py` (CREATE)
- `content-moderation-monitor/scripts/deploy.py` (CREATE)

**Scope:**
- 7 environment variables (fsi_CMM_*): GracePeriodHours, ScanFrequencyHours, IncludeSandbox, IncludeDrafts, BaselineMaxAgeDays, TeamsGroupId, TeamsChannelId
- 3 connection references: fsi_cr_dataverse_moderationmonitor, fsi_cr_office365_moderationmonitor, fsi_cr_teams_moderationmonitor
- deploy.py orchestrator with full/selective deployment and dry-run

**Must-haves:**
- Environment variables use correct Dataverse types (Decimal for numeric, String for text)
- Connection references follow fsi_cr_{connector}_{solution} naming
- deploy.py supports --tables-only, --vars-only, --refs-only modes (mutually exclusive)
- Post-deployment guidance for security roles and connection binding
- All operations idempotent and dry-run capable

**Acceptance criteria:**
1. `python create_environment_variables.py --dry-run` → shows 7 variables
2. `python create_connection_references.py --dry-run` → shows 3 references
3. `python deploy.py --dry-run` → full pipeline preview
4. `python deploy.py --vars-only --dry-run` → selective mode works
5. Post-deployment output includes ModerationValidationHistory security guidance

**Depends on:** 02-01 (requires cmm_client.py)

#### Plan 02-03: Wire Phase 1 PowerShell Scripts to Dataverse (Wave 3)

**Files:**
- `content-moderation-monitor/scripts/Test-ContentModerationCompliance.ps1` (MODIFY)
- `content-moderation-monitor/scripts/private/CMMClient.psm1` (MODIFY)
- `content-moderation-monitor/CHANGELOG.md` (MODIFY)

**Scope:**
- Add `-DataverseToken` and `-PersistResults` parameters to Test-ContentModerationCompliance.ps1
- When `-DataverseUrl` provided: import CMMClient.psm1, connect, read operational parameters from Dataverse env vars (GracePeriodHours, IncludeDrafts, IncludeSandbox)
- When `-PersistResults` provided: write results via `Write-ModerationValidationHistory` and violations via `Write-ModerationViolation` with RunId correlation
- Update `Write-ModerationValidationHistory` to accept mandatory `-RunId`, set `fsi_name` and `fsi_run_id`
- Update `Write-ModerationViolation` to accept optional `-RunId`, set `fsi_name`
- Graceful fallback: when Dataverse unavailable, continue with local defaults
- Add v0.2.0 CHANGELOG.md entry

**Must-haves:**
- No regression when -DataverseUrl is omitted (standalone mode unchanged)
- Operational parameters read from Dataverse when available, fall back to defaults
- Validation results persisted to fsi_moderationvalidationhistory with RunId
- Individual violations persisted to fsi_moderationviolations with RunId
- All Dataverse operations fail gracefully (Write-Warning, don't abort)
- ShouldProcess/-WhatIf gates all write operations

**Acceptance criteria:**
1. `Test-ContentModerationCompliance` without -DataverseUrl → Phase 1 behavior unchanged
2. `Test-ContentModerationCompliance -DataverseUrl $url -WhatIf` → shows Dataverse operations
3. `Test-ContentModerationCompliance -DataverseUrl $url -PersistResults` → writes to Dataverse
4. Invalid DataverseUrl → graceful fallback with warnings
5. CHANGELOG.md has v0.2.0 entry

**Depends on:** 02-02 (requires environment variables deployed)

### Estimated Timeline

Based on AAM Phase 2 actuals (28 minutes total):

| Plan | Estimated | AAM Actual |
|------|-----------|------------|
| 02-01 | ~12 min | 12 min |
| 02-02 | ~8 min | 8 min |
| 02-03 | ~8 min | 8 min |
| **Total** | **~28 min** | **28 min** |

CMM is structurally identical to AAM Phase 2 with column-level differences. The predictability is very high — this is the fourth iteration of an identical deployment pattern.

---

## 10. Common Pitfalls (From ACV/SSC/AAM Experience)

1. **Option set naming collision** — Always check `get_global_optionset()` before `create_global_optionset()`. ACV may already have deployed `fsi_acv_zone`.

2. **Environment variable type mismatch** — Store numeric values as Decimal type (100000001) in Dataverse, cast to `[int]` or `[decimal]` in PowerShell. The `value` field is always returned as a string.

3. **Organization-owned security misconfiguration** — OrganizationOwned removes per-record ownership but doesn't restrict Write/Delete. Security roles must remove these privileges post-deployment for the immutable audit trail.

4. **Connection reference binding** — `create_connection_references.py` creates definitions only. Actual connections are bound during solution import or manual flow configuration. Always document next steps.

5. **Dry-run mode incomplete** — Pass `dry_run` to the client constructor so all mutating operations are centrally guarded. Don't scatter dry-run checks.

6. **Entity set name mismatch** — Dataverse auto-pluralizes by appending 's'. Tables with names ending in "y" get "ys" (not "ies"). Set `EntitySetName` explicitly when the auto-plural would mismatch CMMClient.psm1 usage.

7. **Column key casing** — CMMClient.psm1 uses snake_case keys (e.g., `fsi_agent_id`). The Dataverse Web API is case-insensitive on logical names, but the schema creation should use matching snake_case for consistency and clarity.

8. **Picklist column binding** — Zone and severity columns must use `GlobalOptionSet@odata.bind` syntax in the column definition to reference the shared option sets. Omitting this creates a local option set instead of binding to the global one.

---

## Sources

### Primary (HIGH confidence — direct workspace examination)

| Source | What It Provides |
|--------|-----------------|
| `01-powershell-core-v7/01-VERIFICATION.md` | CMM Phase 1 verified output, file manifest, CMMClient.psm1 summary |
| `01-powershell-core-v7/01-01-SUMMARY.md` | CMMClient.psm1 function details (10 exports, CMM-specific bot queries) |
| `01-powershell-core-v7/01-RESEARCH.md` | Per-agent architecture analysis, moderation level values, severity matrix |
| `02-dataverse-infrastructure-v6/02-RESEARCH.md` | AAM Dataverse research (601 lines): patterns, schema, env vars, connection refs |
| `02-dataverse-infrastructure-v6/02-01-PLAN.md` | AAM schema plan with table/column definitions |
| `02-dataverse-infrastructure-v6/02-02-PLAN.md` | AAM env vars + connection refs plan |
| `02-dataverse-infrastructure-v6/02-03-PLAN.md` | AAM PowerShell wiring plan |
| `02-dataverse-infrastructure-v6/02-01-SUMMARY.md` | AAM schema execution results (12 min) |
| `02-dataverse-infrastructure-v6/02-02-SUMMARY.md` | AAM env vars + deploy.py results (8 min) |
| `02-dataverse-infrastructure-v6/02-03-SUMMARY.md` | AAM PowerShell wiring results (8 min) |
| `02-dataverse-infrastructure-v6/02-VERIFICATION.md` | AAM Phase 2 full verification — all criteria passed |
| `research/ARCHITECTURE.md` | Cross-solution option set definitions, connection ref naming, table patterns |
| `ROADMAP.md` | v7 Phase 2 success criteria and requirement mappings |
| `REQUIREMENTS.md` | INF-01, INF-02, INF-03, INF-05 definitions |

### Inferred (MEDIUM confidence — derived from proven patterns)

| Source | What It Provides |
|--------|-----------------|
| CMMClient.psm1 function signatures (from Phase 1 summaries) | Exact column keys and entity set names for schema alignment |
| AAM Phase 2 duration metrics | Estimated timeline for CMM Phase 2 |
| ACV → SSC → AAM adaptation pattern | How to adapt client class naming without changing structure |

## Metadata

**Confidence:** HIGH — CMM Phase 2 is the fourth iteration of an identical pattern (ACV → SSC → AAM → CMM). All unknowns were resolved in prior milestones. The only CMM-specific complexity is the per-agent column additions, which are straightforward.

**Research date:** 2026-02-10
**Valid until:** 2026-03-10 (30 days — Dataverse Web API and MSAL patterns are stable)

**Key assumptions:**
- ACV/SSC/AAM pattern is appropriate for CMM (same Tier 2 solution architecture)
- fsi_acv_zone and fsi_acv_severity option sets may or may not exist in target environment (CMM handles both cases)
- CMMClient.psm1 entity set names use the forms documented in Phase 1 summaries
- Python 3.10+ is available in the deployment environment
- CMMClient.psm1 function signatures from Phase 1 are frozen and will not change

**Requirement coverage:**

| Requirement | Covered By |
|-------------|-----------|
| INF-01 | Section 2 (schema design) + Plan 02-01 |
| INF-02 | Section 4 (env vars) + Plan 02-02 |
| INF-03 | Section 5 (connection refs) + Plan 02-02 |
| INF-05 | Section 6 (deployment scripts) + Plans 02-01, 02-02 |
