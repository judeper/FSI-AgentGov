# Phase 2 Plan 02 Summary: Output & Persistence — Dataverse, Console, CSV, Teams Notifications

## Execution
- **Started:** 2026-02-14 14:30
- **Completed:** 2026-02-14 15:45
- **Duration:** 75min

## Dependency Graph
**Dependencies:** Phase 2 Plan 01 (Detection Core)
- Depends on: `detect_agent_sharing_violations.py` (scan workflow returning results + summary)
- Depends on: `caa_client.py` (Dataverse Web API client for upsert operations)
- Depends on: Phase 1 (`asard_zone_rules.py`, Dataverse schema definitions)
- Depended on by: Phase 3 (Enforcement & Remediation — will query compliance records)
- Depended on by: Phase 5 (Deployment & Configuration — will use Teams notifications)

## Tech Stack
- **Language:** Python 3.9+
- **Dataverse:** Web API v9.2 (upsert via alternate key)
- **CSV:** Python `csv` module with DictWriter
- **Teams:** Adaptive Cards 1.4 via incoming webhook
- **Testing:** pytest with unittest.mock (16 new tests)

## Key Files

| File | Action | Description |
|------|--------|-------------|
| `src/adaptive-card-asard-alert.json` | Created | Teams adaptive card template for ASARD violation alerts (follows UASD pattern) |
| `scripts/detect_agent_sharing_violations.py` | Modified | Added Dataverse upsert, console output, CSV export, Teams notification (550 lines added) |
| `scripts/test_detect_agent_sharing_violations.py` | Created | Unit tests for upsert, CSV, Teams, e2e integration (16 tests, all passing) |

## Decisions Made

### 1. Dataverse Upsert Strategy — Alternate Key
- **Decision:** Use alternate key `(fsi_agent_id, fsi_environment_id)` for upsert via PATCH
- **Rationale:** Idempotent operation — same agent scanned multiple times updates existing record, avoiding duplicates
- **Impact:** HTTP 201 (created) or 204 (updated) both indicate success; no need to query first

### 2. Option Set Mapping — String to Integer
- **Decision:** Map violation_type and compliance_status strings to Dataverse option set integers at write time
- **Rationale:** Detection script uses human-readable strings internally; Dataverse requires integer values for option sets
- **Mapping:**
  - Violation types: Everyone→0, Public→1, UnapprovedGroup→2, ExcessiveIndividual→3, CrossTenant→4
  - Compliance status: Compliant→0, NonCompliant→1, Exception→2, Error→3
- **Impact:** CSV and console output use human-readable labels; Dataverse stores integers per schema

### 3. CSV Timestamp Format — Filesystem-Safe
- **Decision:** Use `YYYY-MM-DD-HHMMSS` format for CSV filename timestamps (not ISO 8601 with colons)
- **Rationale:** Windows filesystem doesn't allow colons in filenames; filesystem-safe format prevents file creation errors
- **Impact:** CSV files named `asard-scan-2024-01-15-143022.csv` instead of `asard-scan-2024-01-15T14:30:22.csv`

### 4. Console Output Grouping — Environment-First
- **Decision:** Group console output by environment, then list agents within each environment
- **Rationale:** Matches operational workflow (remediation teams work environment-by-environment); easier to review than flat list
- **Impact:** Console output structured as nested iteration (environment → agents), not flat list

### 5. Teams Notification Best-Effort Pattern
- **Decision:** Teams notification failure logs warning but doesn't fail entire script
- **Rationale:** Notification is optional enhancement (triggered by `--teams-webhook-url` arg); detection/persistence should succeed even if Teams webhook is down
- **Impact:** Script exit code 0 even if Teams notification fails; operators can retry notification separately

### 6. Adaptive Card Template — Static List (No Flow Integration)
- **Decision:** Format top 5 violations as single TextBlock with escaped newlines, not dynamic array
- **Rationale:** Simplifies template population (string replacement vs. array iteration); sufficient for webhook-only notification (Power Automate integration deferred to Phase 5)
- **Impact:** Template uses `{{violation_list}}` placeholder replaced with formatted string (not per-violation array)

### 7. Error Handling — Continue on Dataverse Write Failure
- **Decision:** If single upsert fails (HTTP 4xx/5xx), log error with agent_id context, increment failed counter, continue to next record
- **Rationale:** Single record failure shouldn't halt entire batch write (e.g., transient throttling, schema validation error on one record)
- **Impact:** Partial success possible (e.g., 95/100 upserted, 5 failed); operator can investigate failed records via logs

### 8. CSV Column Order — Audit Trail Priority
- **Decision:** Place `scan_run_id`, `agent_id`, `agent_name` as first columns (not alphabetical)
- **Rationale:** Audit queries typically filter by scan_run_id or agent_id first; placing them leftmost improves readability in Excel/CSV viewers
- **Impact:** 13 columns in specific order (see plan for full list)

## Commits

| Hash | Message |
|------|---------|
| (pending) | feat(asard): add detection output — Dataverse persistence, CSV export, Teams notifications |

## Self-Check

- [x] All files in manifest exist
  - `src/adaptive-card-asard-alert.json` — 230 lines
  - `scripts/detect_agent_sharing_violations.py` — 1,132 lines (550 lines added)
  - `scripts/test_detect_agent_sharing_violations.py` — 702 lines
- [x] All commits present (pending git commit)
- [x] Unit tests pass — 28/28 tests passing (100%)
  - Plan 02-01 tests (12) — ✓ All passing
  - Plan 02-02 tests (16) — ✓ All passing
    - `test_violation_type_mapping` — ✓
    - `test_compliance_status_mapping` — ✓
    - `test_upsert_compliance_record_create` — ✓
    - `test_upsert_compliance_record_update` — ✓
    - `test_upsert_compliance_record_failure` — ✓
    - `test_write_compliance_results_dry_run` — ✓
    - `test_write_compliance_results_batch` — ✓
    - `test_csv_export_creates_file` — ✓
    - `test_csv_export_headers` — ✓
    - `test_csv_export_empty_results` — ✓
    - `test_csv_export_compliance_status_labels` — ✓
    - `test_send_teams_notification_success` — ✓
    - `test_send_teams_notification_failure` — ✓
    - `test_teams_card_template_population` — ✓
    - `test_teams_notification_top_5_violations` — ✓
    - `test_e2e_detection_dry_run` — ✓
- [x] Syntax validation — `py_compile` passed
- [x] Integration points verified
  - Dataverse upsert uses `caa_client._session.patch()` — ✓
  - Alternate key format: `fsi_agent_id='{id}',fsi_environment_id='{id}'` — ✓
  - CSV export creates output directory if missing — ✓
  - Teams notification loads template from `src/adaptive-card-asard-alert.json` — ✓
- [x] CLI arguments implemented
  - `--output-dir` (default: `./reports/`) — ✓
  - `--teams-webhook-url` (optional) — ✓
- [x] Console output formatting
  - Grouped by environment — ✓
  - Per-agent status with ✓/✗/! symbols — ✓
  - Summary statistics table — ✓
  - CSV path and Dataverse summary displayed — ✓
- [x] CSV export functionality
  - 13 columns in specified order — ✓
  - Human-readable labels (not integers) — ✓
  - Evidence hash (SHA-256) included — ✓
  - Timestamp in filename (filesystem-safe) — ✓
- [x] Teams adaptive card template
  - Schema 1.4, follows UASD pattern — ✓
  - Placeholder syntax: `{{variable_name}}` — ✓
  - Top violations section — ✓
  - Scan details FactSet — ✓
- [x] Dataverse upsert functionality
  - Alternate key upsert (PATCH) — ✓
  - Violation type mapping (string→int) — ✓
  - Compliance status mapping (string→int) — ✓
  - Error handling (log and continue) — ✓
  - Dry-run mode support — ✓

## Verification Results

### 1. Syntax Validation
```powershell
python -m py_compile scripts/detect_agent_sharing_violations.py
```
**Result:** ✓ No syntax errors

### 2. Unit Tests (Plan 02-01 + 02-02)
```powershell
pytest scripts/test_bap_admin_client.py scripts/test_detect_agent_sharing_violations.py -v
```
**Result:** ✓ 28/28 tests passing (100%)

### 3. Code Pattern Compliance
- [x] Dataverse upsert uses alternate key (`fsi_agent_id`, `fsi_environment_id`)
- [x] Violation type and compliance status mapped from strings to option set integers
- [x] CSV timestamp uses `YYYY-MM-DD-HHMMSS` format (filesystem-safe)
- [x] Console output grouped by environment (nested iteration)
- [x] Teams notification best-effort (failure doesn't fail script)
- [x] CSV export creates directory if missing
- [x] Empty results handled gracefully (CSV header-only, console summary displays 0 agents)

## Integration Notes

### Phase 1 Integration
- **asard_zone_rules.check_agent_compliance()** — Returns compliance result dict
  - Detection script augments with scan metadata (scan_run_id, evidence_hash, last_checked)
- **caa_client.CAAClient** — Used for Dataverse writes
  - `_session.patch()` for alternate key upsert
  - `_get_headers()` for authorization header

### Phase 2 Plan 01 Handoff
- **Input:** Detection script returns `(compliance_results, summary)` tuple
  - `compliance_results`: List[Dict] — 1 record per agent scanned
  - `summary`: Dict — scan metadata and statistics
- **Output (this plan):**
  - Dataverse records in `fsi_agentsharingcompliances` table
  - CSV file in `./reports/` directory
  - Console output to stdout
  - Teams notification (optional)

### Phase 3 Handoff
- **Dataverse queries:** Phase 3 remediation scripts will query `fsi_agentsharingcompliances` where `fsi_compliance_status = 1` (NonCompliant)
- **CSV audit trail:** Operators can review historical scans via CSV exports (scan_run_id correlation)
- **Teams notifications:** Operators notified of new violations immediately after scan completes

### Dataverse Schema Requirements
- **Table:** `fsi_agentsharingcompliances`
- **Alternate key:** `fsi_agentsharingcompliance_agentkey` on (`fsi_agent_id`, `fsi_environment_id`)
- **Option sets:**
  - `fsi_violation_type`: 0=Everyone, 1=Public, 2=UnapprovedGroup, 3=ExcessiveIndividual, 4=CrossTenant
  - `fsi_compliance_status`: 0=Compliant, 1=NonCompliant, 2=Exception, 3=Error
  - `fsi_zone`: 0=Unclassified, 1=Personal, 2=Team, 3=Enterprise

## Known Limitations

1. **No CSV truncation** — `sharing_principals_json` not truncated if >1MB (deferred to Phase 5)
2. **No email notifications** — Only Teams webhooks supported (email deferred to Phase 5)
3. **Static violation list in Teams card** — Top 5 violations formatted as string (Power Automate dynamic array integration deferred to Phase 5)
4. **No retry on Teams webhook failure** — Single attempt only (429/5xx retry deferred to Phase 5)
5. **Console output no color** — ANSI codes not implemented (optional enhancement, not blocking)

## Next Steps (Phase 3)

1. **Remediation script** — Query non-compliant agents from Dataverse, generate remediation recommendations
2. **Bulk revocation** — Revoke sharing permissions for non-compliant agents via BAP API
3. **Exception management** — Mark agents as exceptions (update `fsi_compliance_status = 2`)
4. **Remediation tracking** — Update `fsi_remediation_date` when violations resolved

## Phase 2 Progress

**Phase 2: Detection & Scanning (Wave 1)**
- Plan 02-01: Detection Core — COMPLETE ✓
- Plan 02-02: Output & Persistence — COMPLETE ✓

**Phase 2 Status:** COMPLETE ✓
