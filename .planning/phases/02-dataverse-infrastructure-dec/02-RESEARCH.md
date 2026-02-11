# Phase 2 Research: Dataverse Infrastructure for DEC

**Phase:** 2 — Dataverse Infrastructure
**Researched:** 2026-02-10
**Goal:** Design and implement Dataverse tables for deny event persistence, correlation engine, and zone-based retention — transforming DEC from stateless CSV export to persistent Dataverse-backed solution

## Established Dataverse Patterns (v4-v8)

### Proven 3-Plan Split (5th iteration)

Every Dataverse phase since v4 follows this pattern:

| Plan | Wave | Scope |
|------|------|-------|
| XX-01 | 1 | Python client + requirements + schema (tables, option sets, env vars, conn refs, deploy.py) |
| XX-02 | 2 | Wire PowerShell stubs to Dataverse (implement Connect-* and Write-* functions) |
| XX-03 | 3 | Solution-specific logic (correlation, retention, specialized queries) |

### File Structure Convention

```
{solution}/scripts/
├── {prefix}_client.py               # Dataverse Web API client (MSAL auth, retry, dry-run)
├── create_dataverse_schema.py       # Tables + columns + option set reuse
├── create_environment_variables.py  # fsi_{PREFIX}_* operational params
├── create_connection_references.py  # fsi_cr_{connector}_{solution} refs
├── deploy.py                        # Orchestrator (full/selective/dry-run)
└── requirements.txt                 # msal>=1.30.0, requests>=2.32.0
```

### Naming Conventions

- **Table prefix:** `fsi_` (NOT solution-specific `dec_`; mandated by INF-02)
- **Table names:** PascalCase in schema (`fsi_DenyEvent`), lowercase logical (`fsi_denyevent`)
- **Column names:** `fsi_{snake_case}` logical names; same as OData property keys
- **Entity set names:** Auto-pluralize (`fsi_DenyEvent` → `fsi_denyevents`)
- **Ownership:** ValidationHistory → OrganizationOwned (immutable); operational tables → UserOwned
- **IsAuditEnabled:** True on all tables

### Client Class Pattern

`{PREFIX}Client` — MSAL auth (interactive + SP), `Retry(total=3, backoff_factor=1, status_forcelist=[429,500,502,503,504])`, dry-run flag, idempotent create helpers.

## ACV Shared Option Sets

**`fsi_acv_zone`** — Zone classification (shared across ALL solutions):

| Value | Label |
|-------|-------|
| 0 | Unclassified |
| 1 | Zone 1 |
| 2 | Zone 2 |
| 3 | Zone 3 |

**`fsi_acv_severity`** — Validation severity (shared across ALL solutions):

| Value | Label |
|-------|-------|
| 1 | Passed |
| 2 | Warning |
| 3 | GracePeriod |
| 4 | Failed |
| 5 | Error |

**Reuse pattern:** Check existence via `get_global_optionset()` before creating. If ACV/SSC/AAM/CMM/FUS already deployed, reuse. DEC never creates its own option sets — only reuses these two.

## Phase 2 Stub Functions (from Phase 1 DECClient.psm1)

Phase 1 created 4 stubs with full parameter signatures. These must be implemented in Phase 2:

### Connect-DECDataverse

```powershell
param(
    [Parameter(Mandatory)] [string]$TenantId,
    [Parameter(Mandatory)] [string]$ClientId,
    [Parameter(Mandatory)] [string]$KeyVaultName,
    [string]$EnvironmentUrl,        # Falls back to DEC_DataverseUrl env var
    [string]$SecretName = 'sp-dataverse'
)
```

### Write-DECDenyEvent

```powershell
param(
    [Parameter(Mandatory)] [string]$AgentId,
    [Parameter(Mandatory)] [string]$SessionId,
    [Parameter(Mandatory)] [string]$FilterReason,
    [string]$FilterCategory,
    [string]$FilterSeverity,
    [datetime]$EventTimestamp = (Get-Date),
    [ValidateSet('1','2','3')] [string]$ZoneClassification,
    [hashtable]$AdditionalProperties
)
```

### Write-DECCorrelation

```powershell
param(
    [Parameter(Mandatory)] [string]$DenyEventId,
    [string]$AuditRecordId,
    [string]$DlpPolicyMatchId,
    [Parameter(Mandatory)] [ValidateSet('AuditMatch','DlpMatch','TimeProximity')] [string]$CorrelationType,
    [ValidateRange(0.0,1.0)] [double]$ConfidenceScore = 0.0,
    [hashtable]$CorrelationDetails
)
```

### Write-DECValidationHistory

```powershell
param(
    [Parameter(Mandatory)] [string]$ValidationRunId,
    [Parameter(Mandatory)] [ValidateSet('DenyEventExtraction','CorrelationCheck','ComplianceAudit')] [string]$ValidationType,
    [int]$RecordsProcessed = 0,
    [int]$RecordsPassed = 0,
    [int]$RecordsFailed = 0,
    [hashtable]$ValidationDetails,
    [datetime]$RunTimestamp = (Get-Date)
)
```

## Table Design

### Table Naming Resolution

The ROADMAP references `fsi_denyevent`, `fsi_denycorrelation`, `fsi_denyalert`. The Phase 1 stubs define `Write-DECValidationHistory` (not `Write-DECDenyAlert`). Resolution:

| Table | Schema Name | Purpose | Phase |
|-------|-------------|---------|-------|
| `fsi_DenyEvent` | `fsi_denyevent` | Primary deny event records from 3 sources | Phase 2 (DVS-02) |
| `fsi_DenyCorrelation` | `fsi_denycorrelation` | Daily correlation summaries | Phase 2 (DVS-03) |
| `fsi_DenyAlert` | `fsi_denyalert` | Alert history records | Phase 2 schema, Phase 3 population |
| `fsi_DenyValidationHistory` | `fsi_denyvalidationhistory` | Immutable validation audit log (v4-v8 pattern) | Phase 2 (matches stubs) |

All 4 tables defined in schema. `fsi_DenyAlert` schema created in Phase 2 with `fsi_DenyValidationHistory`; alert population deferred to Phase 3 (ORC-02).

### Column Mapping (from Stub Parameters)

**fsi_DenyEvent:**

| Column | Type | Source | Notes |
|--------|------|--------|-------|
| `fsi_deny_event_id` | Primary Key | Auto-generated | GUID |
| `fsi_agent_id` | String 100 | `$AgentId` | Required |
| `fsi_session_id` | String 100 | `$SessionId` | Required |
| `fsi_filter_reason` | String 500 | `$FilterReason` | Required |
| `fsi_filter_category` | String 200 | `$FilterCategory` | Optional |
| `fsi_filter_severity` | Picklist | `$FilterSeverity` | Reuses `fsi_acv_severity` |
| `fsi_event_timestamp` | DateTimeBehavior.UserLocal | `$EventTimestamp` | Required |
| `fsi_zone` | Picklist | `$ZoneClassification` | Reuses `fsi_acv_zone` |
| `fsi_source_type` | String 50 | NEW — extraction script identifier | `RaiTelemetry`, `PurviewAudit`, `PurviewDlp` |
| `fsi_details_json` | Memo 100000 | `$AdditionalProperties` | JSON serialized |

**fsi_DenyCorrelation:**

| Column | Type | Source | Notes |
|--------|------|--------|-------|
| `fsi_deny_correlation_id` | Primary Key | Auto-generated | GUID |
| `fsi_correlation_date` | DateTimeBehavior.UserLocal | Daily summary date | Required |
| `fsi_agent_id` | String 100 | Grouped by agent | Required |
| `fsi_zone` | Picklist | Grouped by zone | Reuses `fsi_acv_zone` |
| `fsi_event_count` | Integer | Count of deny events | Required |
| `fsi_severity_distribution_json` | Memo 10000 | Severity breakdown | JSON |
| `fsi_trend_7day_json` | Memo 10000 | 7-day trend data | JSON |
| `fsi_time_window_start` | DateTimeBehavior.UserLocal | Window start | Required |
| `fsi_time_window_end` | DateTimeBehavior.UserLocal | Window end | Required |
| `fsi_correlation_details_json` | Memo 100000 | `$CorrelationDetails` | JSON |

**fsi_DenyAlert (Phase 3 population):**

| Column | Type | Notes |
|--------|------|-------|
| `fsi_deny_alert_id` | Primary Key | GUID |
| `fsi_alert_type` | String 50 | VolumeAnomaly, NewAgent, ZoneCritical |
| `fsi_alert_severity` | Picklist | Reuses `fsi_acv_severity` |
| `fsi_agent_id` | String 100 | |
| `fsi_zone` | Picklist | Reuses `fsi_acv_zone` |
| `fsi_alert_timestamp` | DateTimeBehavior.UserLocal | |
| `fsi_alert_message` | Memo 10000 | |
| `fsi_acknowledged` | Boolean | Default false |
| `fsi_details_json` | Memo 100000 | |

**fsi_DenyValidationHistory (OrganizationOwned — immutable):**

| Column | Type | Source | Notes |
|--------|------|--------|-------|
| `fsi_deny_validation_id` | Primary Key | Auto-generated | GUID |
| `fsi_validation_run_id` | String 100 | `$ValidationRunId` | Required |
| `fsi_validation_type` | String 50 | `$ValidationType` | Required |
| `fsi_records_processed` | Integer | `$RecordsProcessed` | |
| `fsi_records_passed` | Integer | `$RecordsPassed` | |
| `fsi_records_failed` | Integer | `$RecordsFailed` | |
| `fsi_validation_details_json` | Memo 100000 | `$ValidationDetails` | JSON |
| `fsi_run_timestamp` | DateTimeBehavior.UserLocal | `$RunTimestamp` | Required |

## Retention Implementation (NEW capability)

**Critical finding:** No prior milestone has implemented Dataverse record-level retention. v4-v8 retention env vars (`fsi_ACV_Zone*RetentionDays`) validate external system settings, not Dataverse records.

### Approach: Dataverse Bulk Delete Jobs

Create 3 recurring bulk delete jobs (one per zone) during deployment:

| Job Name | Zone | Retention | FetchXML Filter |
|----------|------|-----------|-----------------|
| `DEC Zone 1 Retention` | 1 | 90 days | `fsi_zone = 1 AND fsi_event_timestamp < (UtcNow - 90d)` |
| `DEC Zone 2 Retention` | 2 | 365 days | `fsi_zone = 2 AND fsi_event_timestamp < (UtcNow - 365d)` |
| `DEC Zone 3 Retention` | 3 | 730 days | `fsi_zone = 3 AND fsi_event_timestamp < (UtcNow - 730d)` |

**Implementation:** Python `deploy.py` creates bulk delete jobs via `BulkDeleteRequest` Web API action, or provide PowerShell `Set-DECRetentionRules.ps1` for manual setup. Both paths supported.

Retention days configurable via environment variables (`fsi_DEC_Zone1RetentionDays`, etc.).

## Environment Variables (Projected)

| Schema Name | Type | Default | Purpose |
|------------|------|---------|---------|
| `fsi_DEC_Zone1RetentionDays` | Decimal | 90 | Deny event retention for Zone 1 |
| `fsi_DEC_Zone2RetentionDays` | Decimal | 365 | Deny event retention for Zone 2 |
| `fsi_DEC_Zone3RetentionDays` | Decimal | 730 | Deny event retention for Zone 3 |
| `fsi_DEC_ScanFrequencyHours` | Decimal | 24 | How often correlation runs |
| `fsi_DEC_AnomalyThresholdSigma` | Decimal | 2.0 | Standard deviations for volume anomaly |
| `fsi_DEC_TeamsGroupId` | String | (blank) | Teams group for deny alerts (Phase 3) |
| `fsi_DEC_TeamsChannelId` | String | (blank) | Teams channel for deny alerts (Phase 3) |

## Connection References

| Logical Name | Connector | Purpose |
|-------------|-----------|---------|
| `fsi_cr_dataverse_denyeventcorrelation` | `shared_commondataserviceforapps` | Read/write deny events, correlations, validation history |
| `fsi_cr_office365_denyeventcorrelation` | `shared_office365` | Email alerts (Phase 3) |
| `fsi_cr_teams_denyeventcorrelation` | `shared_teams` | Teams alerts (Phase 3) |

## DEC-Specific Design Considerations

### Multi-Source Architecture

DEC is unique among solutions — it correlates events from 3 data sources:
- App Insights RAI telemetry (`RaiTelemetry`)
- Purview Audit CopilotInteraction (`PurviewAudit`)
- Purview DLP Copilot events (`PurviewDlp`)

Requires a `fsi_source_type` discriminator column on `fsi_DenyEvent` — no prior solution has this.

### Correlation Logic

The `fsi_DenyCorrelation` table is novel — prior solutions have baselines/violations/history, never cross-source correlation. The correlation engine:

1. Queries `fsi_DenyEvent` for events in the target time window
2. Groups by `fsi_agent_id` + `fsi_zone` + time window
3. Calculates: event count, severity distribution, source mix
4. Computes 7-day trend (query prior 7 correlation records for the same agent/zone)
5. Writes summary to `fsi_DenyCorrelation`

### Volume Considerations

Large tenants may generate 100s-1000s of deny events daily. `Write-DECDenyEvent` should support batch ingestion via Dataverse Web API `$batch` endpoint for performance.

## Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Retention is new capability (no v4-v8 precedent) | Certain | Medium | Research BulkDeleteRequest API; include as deploy.py step |
| EntitySetName pluralization on `fsi_DenyValidationHistory` | High | Low | Set explicit EntitySetName |
| High event volume in large tenants | Medium | Medium | Batch ingestion in Write-DECDenyEvent |
| Zone lookup: extraction scripts may not know agent zone | High | Medium | Zone mapping in correlation engine or orchestrator |
| Cross-repo staging (FSI-AgentGov-Solutions) | Certain | Low | Follow established cross-repo pattern |

---
*Research completed: 2026-02-10*
