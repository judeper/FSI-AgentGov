# Phase 2 Research: Dataverse Data Model

## Phase Goal

Create Dataverse table schemas for environment policy, compliance records, and error logging with environment variables and connection references for the Inactivity Timeout Enforcement solution (v19, Control 2.22).

## Requirements Covered

- **DVM-01:** `fsi_environmentpolicy` table schema script
- **DVM-02:** `fsi_inactivitytimeout_compliance` table schema script
- **DVM-03:** `fsi_inactivitytimeout_errorlog` table schema script

---

## 1. Existing Dataverse Schema Script Patterns

### 1.1 Script Inventory

| Script | Solution | Tables | Option Sets | Lines |
|--------|----------|--------|-------------|-------|
| `scripts/create_dataverse_schema.py` | CAA (v4) | 3 tables | 2 shared global (`fsi_acv_zone`, `fsi_acv_severity`) | 528 |
| `scripts/create_uasd_dataverse_schema.py` | UASD (v16) | 5 tables | 6 solution-specific (`fsi_UASD_*`) + shared refs | 844 |

No MIME (v18) Dataverse schema script exists — MIME Type Restrictions uses a JSON config file (`src/MimeConfig.json`) rather than Dataverse tables.

### 1.2 Script Structure (Canonical Pattern)

Both scripts follow an identical structure:

```
1. Module docstring (table list + usage examples)
2. Imports (argparse, logging, sys, typing, CAAClient)
3. Option set definitions (SHARED_OPTIONSETS or SOLUTION_OPTIONSETS dict)
4. Column helper functions (_label, _string_col, _memo_col, _boolean_col, _datetime_col, _integer_col, _picklist_col)
5. Table definition functions (_*_table_definition() → Dict)
6. Column definition functions (_*_columns() → List[Dict])
7. Schema creation functions (create_*_table(), _create_table_with_columns())
8. Seed data functions (optional — UASD has seed_default_policy())
9. Orchestrator function (create_schema())
10. CLI entry point (main() with argparse)
```

### 1.3 Column Helper Functions (Shared Across All Scripts)

Each script redeclares identical helper functions. Representative code from `create_dataverse_schema.py`:

```python
def _label(text: str) -> Dict[str, Any]:
    return {"LocalizedLabels": [{"Label": text, "LanguageCode": 1033}]}

def _string_col(schema_name, display, *, max_length=100, required=False):
    # @odata.type: #Microsoft.Dynamics.CRM.StringAttributeMetadata

def _memo_col(schema_name, display, *, required=False):
    # @odata.type: #Microsoft.Dynamics.CRM.MemoAttributeMetadata
    # MaxLength: 1048576, Format: "TextArea"

def _boolean_col(schema_name, display, *, default=False, required=False):
    # @odata.type: #Microsoft.Dynamics.CRM.BooleanAttributeMetadata
    # TrueOption: Yes(1), FalseOption: No(0)

def _datetime_col(schema_name, display, *, required=False):
    # @odata.type: #Microsoft.Dynamics.CRM.DateTimeAttributeMetadata
    # Format: "DateAndTime", DateTimeBehavior: "UserLocal"

def _integer_col(schema_name, display, *, required=False):
    # @odata.type: #Microsoft.Dynamics.CRM.IntegerAttributeMetadata
    # MinValue: 0, MaxValue: 2147483647

def _picklist_col(schema_name, display, global_optionset_name, *, required=False):
    # @odata.type: #Microsoft.Dynamics.CRM.PicklistAttributeMetadata
    # GlobalOptionSet@odata.bind: /GlobalOptionSetDefinitions(Name='...')
```

**Key observation:** These helpers are copy-pasted, not imported from a shared module. The v19 scripts should continue this pattern for consistency, despite the code duplication.

### 1.4 Table Definition Format

Tables are defined as Python functions returning a dictionary:

```python
def _table_definition() -> Dict[str, Any]:
    return {
        "SchemaName": "fsi_TableName",           # PascalCase
        "DisplayName": _label("Display Name"),
        "DisplayCollectionName": _label("Display Names"),  # Plural
        "Description": _label("Description text"),
        "OwnershipType": "OrganizationOwned",     # or "UserOwned"
        "IsActivity": False,
        "EntitySetName": "fsi_tablenames",         # lowercase, plural
        "HasNotes": False,
        "HasActivities": False,
        "PrimaryNameAttribute": "fsi_primary_name", # Must be String type
        "Attributes": [
            _string_col("fsi_primary_name", "Primary Name", max_length=200, required=True),
        ],
    }
```

**Conventions observed:**
- `OwnershipType`: Mutable config tables use `OrganizationOwned`; immutable audit tables use `OrganizationOwned` (with post-deployment Write/Delete removal)
- `PrimaryNameAttribute`: Always a String-type column included in the `Attributes` array of the table definition
- Additional columns are defined in a separate `_*_columns()` function, added after table creation
- `EntitySetName`: Lowercase, plural form of the table name

### 1.5 Immutable Audit Table Pattern

From CAA's `fsi_CAPolicyValidationHistory`:
- `OwnershipType: "OrganizationOwned"` (not `UserOwned`)
- Security roles strip Write/Delete post-deployment
- One record per scan — never update in place
- Timestamp column for audit trail

This is the exact pattern needed for `fsi_inactivitytimeout_compliance`.

### 1.6 Idempotent Table + Column Creation

From `create_dataverse_schema.py`:

```python
def _create_table_with_columns(client, table_def, columns, dry_run=False):
    logical_name = table_def["SchemaName"].lower()
    created = client.create_table(table_def)  # Checks existence first
    for col in columns:
        added = client.create_column(logical_name, col)  # Checks existence first
```

The `CAAClient` class (`caa_client.py`) provides `create_table()` and `create_column()` with built-in existence checks.

---

## 2. `fsi_acv_zone` Shared Option Set Analysis

### 2.1 Definition (from `create_dataverse_schema.py`)

```python
"fsi_acv_zone": {
    "Name": "fsi_acv_zone",
    "DisplayName": {"LocalizedLabels": [{"Label": "FSI Zone", "LanguageCode": 1033}]},
    "IsGlobal": True,
    "OptionSetType": "Picklist",
    "Options": [
        {"Value": 0, "Label": "Unclassified"},
        {"Value": 1, "Label": "Zone 1"},
        {"Value": 2, "Label": "Zone 2"},
        {"Value": 3, "Label": "Zone 3"},
    ],
}
```

### 2.2 Compatibility Assessment

**Compatible for `fsi_environmentpolicy.fsi_zone`:** YES.

The `fsi_environmentpolicy` table needs Zone 1/2/3 classification. The `fsi_acv_zone` option set includes exactly these values (1, 2, 3) plus Unclassified (0). The requirement says "Zone1/Zone2/Zone3" — Unclassified (0) is acceptable as a fallback value.

**Reuse pattern (from `create_uasd_dataverse_schema.py`):**

```python
# fsi_acv_zone and fsi_acv_severity are created by the CAA schema script
# (create_dataverse_schema.py).  UASD tables bind picklist columns to these
# shared option sets but do not recreate them.
```

UASD references `fsi_acv_zone` via `_picklist_col("fsi_zone", "Zone", "fsi_acv_zone", required=True)` without defining or creating it. The v19 schema script should follow the same pattern — reference but not create.

### 2.3 Existing Usage Across Solutions

| Solution | Table | Column | Required |
|----------|-------|--------|----------|
| CAA | `fsi_CAPolicyBaseline` | `fsi_zone` | Yes |
| CAA | `fsi_CAPolicyViolation` | `fsi_zone` | Yes |
| UASD | `fsi_ApprovedSecurityGroup` | `fsi_zone` | Yes |
| UASD | `fsi_SharingPolicy` | `fsi_governance_zone` | Yes |
| **ITE (new)** | `fsi_environmentpolicy` | `fsi_zone` | Yes |

**Note:** Column name varies between `fsi_zone` and `fsi_governance_zone` — both bind to the same global option set. For v19, `fsi_zone` (the more common convention) is recommended.

---

## 3. Environment Variable Pattern

### 3.1 CAA Pattern (`create_environment_variables.py`)

```python
ENVIRONMENT_VARIABLES: List[Dict[str, Any]] = [
    {
        "schema_name": "fsi_CAA_GracePeriodHours",        # Prefix: fsi_{SOLUTION}_
        "display_name": "CAA - Grace Period (Hours)",      # Display: {SOLUTION} - {Name}
        "type": 100000001,  # Decimal                      # Types: 100000000=String, 100000001=Decimal
        "default_value": "48",                             # Always string representation
        "description": "Hours before newly deployed policies are included in validation",
    },
    # ...
]
```

### 3.2 UASD Pattern (`create_uasd_environment_variables.py`)

Identical structure with `fsi_UASD_*` prefix. 4 variables defined.

### 3.3 Naming Convention

| Convention | Pattern | Example |
|-----------|---------|---------|
| Schema name | `fsi_{SOLUTION}_{VariableName}` | `fsi_ITE_ConcurrencyLimit` |
| Display name | `{SOLUTION} - {Human Name}` | `ITE - Concurrency Limit` |
| Type codes | `100000000` = String, `100000001` = Decimal | |
| Default value | Always a string | `"5"`, `""`, `"true"` |

### 3.4 Required Environment Variables for v19

Per ROADMAP.md success criteria 4:

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `fsi_ITE_ConcurrencyLimit` | Decimal | `"5"` | Max parallel environment evaluations |
| `fsi_ITE_NotificationRecipients` | String | `""` | Email addresses for compliance alerts |
| `fsi_ITE_ScanFrequencyHours` | Decimal | `"24"` | Scan interval (matches CAA/UASD pattern) |

### 3.5 Script Structure

The script structure is identical to the schema scripts: module docstring → imports → variable list → `create_environment_variable()` → `create_environment_variables()` → CLI main(). The `CAAClient` is used with the same args pattern.

---

## 4. Connection Reference Pattern

### 4.1 CAA Pattern (`create_connection_references.py`)

```python
CONNECTION_REFERENCES: List[Dict[str, Any]] = [
    {
        "logical_name": "fsi_cr_dataverse_conditionalaccessautomation",  # fsi_cr_{connector}_{solution}
        "display_name": "Dataverse - Conditional Access Automation",      # {Connector} - {Solution}
        "connector_id": "shared_commondataserviceforapps",                # Power Platform connector ID
        "description": "Table CRUD for baselines, history, violations",
    },
    # ...
]
```

### 4.2 UASD Pattern (`create_uasd_connection_references.py`)

2 connection references: Dataverse + Teams.

### 4.3 Required Connection References for v19

Per ROADMAP.md success criteria 4:

| Logical Name | Connector | Purpose |
|-------------|-----------|---------|
| `fsi_cr_dataverse_inactivitytimeout` | `shared_commondataserviceforapps` | Policy/compliance/errorlog table CRUD |
| `fsi_cr_powerplatformforadmins_inactivitytimeout` | `shared_powerplatformforadmins` | BAP Admin API environment enumeration |

**Note:** The BAP Admin API for privacy settings (`api.bap.microsoft.com`) uses service principal auth with scope `https://api.bap.microsoft.com/.default`, which is called via HTTP action in the flow. The `shared_powerplatformforadmins` connector is used for environment enumeration (Power Platform for Admins V2 connector). A Teams connector is NOT required — the flow sends email only for non-compliant results.

---

## 5. `CAAClient` Shared Utility

### 5.1 Overview (`caa_client.py`)

The `CAAClient` class (463 lines) provides:
- MSAL authentication (service principal or interactive)
- Retry strategy (3 retries, exponential backoff on 429/5xx)
- CRUD operations: `create_record()`, `update_record()`, `query()`
- Metadata operations: `create_table()`, `create_column()`, `create_global_optionset()`, `get_global_optionset()`
- Idempotent helpers: `check_table_exists()`, `create_table()` (checks first), `create_column()` (checks first)
- Dry-run support baked into all mutating operations
- Environment variables: `CAA_TENANT_ID`, `CAA_ENVIRONMENT_URL`, `CAA_CLIENT_ID`, `CAA_CLIENT_SECRET`

### 5.2 Usage

All schema/env-var/conn-ref scripts import from `caa_client`:

```python
from caa_client import CAAClient
```

Despite being named "CAA Client," it's used by UASD scripts too — it's effectively a generic Dataverse Web API client. The v19 scripts should continue using `CAAClient` directly.

---

## 6. Solution-Specific Option Set Analysis

### 6.1 v19 Requires Two Solution-Specific Option Sets

**`fsi_ITE_compliancestatus`** — for `fsi_inactivitytimeout_compliance.fsi_compliancestatus`:

| Value | Label |
|-------|-------|
| 0 | Compliant |
| 1 | Non-Compliant |
| 2 | Unknown |

**`fsi_ITE_environmenttype`** — for `fsi_inactivitytimeout_compliance.fsi_environmenttype`:

| Value | Label |
|-------|-------|
| 0 | Default |
| 1 | Sandbox |
| 2 | Production |
| 3 | Developer |
| 4 | Trial |

These values reflect common Power Platform environment types returned by the BAP Admin API.

### 6.2 Option Set Naming Convention

| Solution | Prefix | Examples |
|----------|--------|---------|
| CAA | `fsi_acv_` (shared) | `fsi_acv_zone`, `fsi_acv_severity` |
| UASD | `fsi_UASD_` | `fsi_UASD_sharingscope`, `fsi_UASD_violationtype` |
| **ITE** | `fsi_ITE_` | `fsi_ITE_compliancestatus`, `fsi_ITE_environmenttype` |

### 6.3 fsi_errortype for Error Log

The `fsi_errortype` column in REQUIREMENTS.md is specified as Text type (401/403/404/429/MissingPolicy/ParseError). This is correct — using a free-text field rather than a choice allows for unanticipated error types without schema changes. No option set needed.

---

## 7. Table Schema Designs

### 7.1 `fsi_environmentpolicy` (DVM-01)

**Purpose:** Admin-managed environment policy configuration — zone classification and required maximum inactivity timeout per environment.

| Column | Type | Helper | Required | Notes |
|--------|------|--------|----------|-------|
| `fsi_environmentid` | String 100 | `_string_col` | Yes | PrimaryNameAttribute — EnvironmentName (canonical identifier) |
| `fsi_environmentdisplayname` | String 200 | `_string_col` | No | Human-readable name |
| `fsi_zone` | Picklist (fsi_acv_zone) | `_picklist_col` | Yes | Reuses shared global option set |
| `fsi_requiredmaxduration` | Integer | `_integer_col` | Yes | Maximum timeout in minutes |
| `fsi_notes` | Memo | `_memo_col` | No | Admin notes |

**Ownership:** `OrganizationOwned` (admin-managed configuration)
**EntitySetName:** `fsi_environmentpolicies`
**Immutability:** Mutable (admin updates zone/duration as needed)

### 7.2 `fsi_inactivitytimeout_compliance` (DVM-02)

**Purpose:** Immutable compliance scan records — one per environment per scan, never update in place.

| Column | Type | Helper | Required | Notes |
|--------|------|--------|----------|-------|
| `fsi_name` | String 200 | `_string_col` | Yes | PrimaryNameAttribute — `{EnvironmentName}-{timestamp}` |
| `fsi_environmentid` | String 100 | `_string_col` | Yes | EnvironmentName |
| `fsi_environmentname` | String 200 | `_string_col` | No | Display name from BAP API |
| `fsi_environmenttype` | Picklist (fsi_ITE_environmenttype) | `_picklist_col` | No | Default/Sandbox/Production/Developer/Trial |
| `fsi_inactivitytimeoutenabled` | Boolean | `_boolean_col` | Yes | Whether timeout is enabled |
| `fsi_timeoutduration` | Integer | `_integer_col` | No | Actual duration in minutes (null if disabled) |
| `fsi_requiredmaxduration` | Integer | `_integer_col` | No | Required maximum from policy (null if no policy) |
| `fsi_compliancestatus` | Picklist (fsi_ITE_compliancestatus) | `_picklist_col` | Yes | Compliant/Non-Compliant/Unknown |
| `fsi_lastscandate` | DateTime | `_datetime_col` | Yes | When this scan ran |
| `fsi_notes` | Memo | `_memo_col` | No | Evaluation notes (e.g., "No policy found") |

**Ownership:** `OrganizationOwned` (immutable — remove Write/Delete post-deployment)
**EntitySetName:** `fsi_inactivitytimeoutcompliances`
**Index:** Composite on `(fsi_environmentid, fsi_lastscandate)` — noted in script comment but Dataverse Web API does not support programmatic index creation; document as a post-deployment manual step.

**Note on PrimaryNameAttribute:** The REQUIREMENTS.md specifies `fsi_environmentid` as a key, but Dataverse requires a unique primary name. Using `fsi_name` (composite `{EnvironmentName}-{timestamp}`) follows the CAA `fsi_run_id` pattern for immutable tables.

### 7.3 `fsi_inactivitytimeout_errorlog` (DVM-03)

**Purpose:** Error logging for scan failures — separate from compliance records to avoid polluting the audit trail.

| Column | Type | Helper | Required | Notes |
|--------|------|--------|----------|-------|
| `fsi_name` | String 256 | `_string_col` | Yes | PrimaryNameAttribute — `{EnvironmentName}-{errortype}-{timestamp}` |
| `fsi_environmentid` | String 100 | `_string_col` | Yes | EnvironmentName |
| `fsi_errortype` | String 50 | `_string_col` | Yes | 401/403/404/429/MissingPolicy/ParseError |
| `fsi_errorraw` | Memo | `_memo_col` | No | Raw error response / stack trace |
| `fsi_timestamp` | DateTime | `_datetime_col` | Yes | When error occurred |

**Ownership:** `OrganizationOwned`
**EntitySetName:** `fsi_inactivitytimeouterrorlogs`
**Immutability:** Append-only (error records should not be modified)

---

## 8. Risk Assessment

| # | Risk | Severity | Mitigation |
|---|------|----------|------------|
| 1 | Pattern deviation | Low | All patterns are well-documented across 2 existing scripts; follow them exactly |
| 2 | `fsi_acv_zone` not deployed | Low | UASD already handles this — document as prerequisite (CAA schema must be deployed first) |
| 3 | Column helper duplication | Low | Acceptable — matches existing convention (each script self-contained) |
| 4 | CAAClient naming confusion | Low | Already used by UASD — proven to work cross-solution |
| 5 | Dataverse index creation | Medium | Web API doesn't support programmatic index creation; document as manual post-deployment step |
| 6 | `fsi_environmenttype` values | Medium | Power Platform environment types may evolve; using a Choice allows adding values later |
| 7 | Seed data for `fsi_environmentpolicy` | Medium | Zone-specific rows need tenant-specific EnvironmentNames — seed data should be template-based (instructions, not auto-insert) |

No high risks identified. Phase 2 work is schema-only (no runtime behavior) and follows a pattern with zero ambiguity from 2 existing implementations.

---

## 9. Recommended Approach

### Plan A: Policy + Compliance Tables + Env Vars + Conn Refs (02-01-PLAN.md)

**Files:**
- `scripts/create_timeout_dataverse_schema.py` — Two solution-specific option sets (`fsi_ITE_compliancestatus`, `fsi_ITE_environmenttype`), `fsi_environmentpolicy` table definition + columns, `fsi_inactivitytimeout_compliance` table definition + columns, schema orchestration, CLI entry point
- `scripts/create_timeout_environment_variables.py` — 3 environment variables (`fsi_ITE_ConcurrencyLimit`, `fsi_ITE_NotificationRecipients`, `fsi_ITE_ScanFrequencyHours`), standard deployment functions + CLI
- `scripts/create_timeout_connection_references.py` — 2 connection references (Dataverse + Power Platform for Admins), standard deployment functions + CLI

**Estimated complexity:** ~500 lines (schema) + ~180 lines (env vars) + ~180 lines (conn refs)

### Plan B: Error Log Table + Seed Data Configuration (02-02-PLAN.md)

**Files:**
- `scripts/create_timeout_errorlog_schema.py` — `fsi_inactivitytimeout_errorlog` table definition + columns, no new option sets (error type is free-text), schema orchestration (1 table), CLI entry point

**Additional scope:**
- Seed data documentation — a commented template in the schema script + README text showing how to populate `fsi_environmentpolicy` rows for common zone configurations
- Post-deployment index creation instructions as a comment block

**Estimated complexity:** ~200 lines (error log schema) + ~30 lines (seed data comments)

### Wave Assignment

Both plans are **Wave 1** — they target non-overlapping files and can run in parallel.

---

*Research completed: 2026-02-12*
*Phase: 02 — Dataverse Data Model*
*Milestone: v19 — Inactivity Timeout Enforcement (Policy-Driven Maximum)*
