# Phase 4 Plan 1 Summary: Exception Tracking and Review Workflow

## Execution
- **Started:** 2026-02-13 14:30 UTC
- **Completed:** 2026-02-13 15:45 UTC
- **Duration:** 75 minutes

## Dependency Graph

**Dependencies:**
- Phase 1: Dataverse schema and zone rules (complete)
- Phase 2: Detection script (complete)
- Phase 3: Remediation script (complete)

**Dependents:**
- Phase 5: End-to-end deployment and validation (awaiting Phase 4 completion)

## Tech Stack

- **Backend:** Python 3.9+
- **Data Persistence:** Microsoft Dataverse (via Web API)
- **Automation:** Power Automate (scheduled recurrence flow)
- **Notifications:** Microsoft Teams (adaptive cards)
- **Testing:** pytest with unittest.mock
- **Date Parsing:** python-dateutil for ISO 8601 datetime handling

## Key Files

| File | Action | Description |
|------|--------|-------------|
| `scripts/create_asard_dataverse_schema.py` | Modified | Added 5 exception tracking columns to `_agent_sharing_compliance_columns()` function: `fsi_exception_expires_at`, `fsi_exception_justification`, `fsi_exception_approved_by`, `fsi_exception_approved_at`, `fsi_exception_review_date` |
| `scripts/detect_agent_sharing_violations.py` | Modified | Updated `upsert_compliance_record()` to query for existing active exceptions (compliance_status=2, expires_at >= now), preserve exception fields when active, set compliance_status=2 (Exception) instead of NonCompliant. Updated `write_compliance_results_to_dataverse()` to track exception count. |
| `scripts/remediate_agent_sharing.py` | Modified | Added exception check in `remediate_agent()` function at entry point. Queries Dataverse for active exceptions before remediation. Skips agents with active exceptions, logs message with expiration date. Updated main stats tracking to include skipped count in summary output. |
| `src/asard-exception-review-workflow.json` | Created | Power Automate flow with daily scheduled trigger (08:00 UTC). Parallel branches: (1) Query expiring exceptions (within 14 days), send Teams notification. (2) Query expired exceptions, auto-reset to NonCompliant (compliance_status=1), clear exception fields, send Teams notification. |
| `src/adaptive-card-asard-exception-expiring.json` | Created | Adaptive card template for expiring exceptions notification. Warning theme (yellow), displays exception count, expiring agent list (name, environment, days remaining, approver, justification preview), renewal instructions, governance contact info. |
| `src/adaptive-card-asard-exception-expired.json` | Created | Adaptive card template for expired exceptions notification. Critical theme (red), displays exception count, expired agent list (name, environment, expired date, previous justification), auto-remediation notice, re-grant instructions. |
| `docs/playbooks/asard-exception-management.md` | Created | Comprehensive exception management playbook. Sections: Overview, Exception Criteria, Exception Lifecycle (creation, renewal, expiration), Monitoring Expiring Exceptions, Validation, Troubleshooting. Includes manual exception entry procedures, Dataverse query examples, workflow deployment instructions. |
| `scripts/test_detect_agent_sharing_violations.py` | Modified | Added 3 tests for exception handling: `test_upsert_compliance_record_with_active_exception` (verifies preservation of active exceptions), `test_upsert_compliance_record_with_expired_exception` (verifies expired exceptions ignored), `test_upsert_compliance_record_no_existing_exception` (verifies normal operation without exceptions). |
| `scripts/test_remediate_agent_sharing.py` | Modified | Added 3 tests for remediation exception skip logic: `test_remediate_agent_skips_active_exception` (verifies skip with active exception), `test_remediate_agent_proceeds_with_expired_exception` (verifies remediation proceeds when exception expired), `test_remediate_agent_proceeds_with_no_exception` (verifies normal remediation without exception). |

## Decisions Made

### Design Decision 1: Compliance Table Extension vs. Separate Exception Table

**Choice:** Extended `fsi_agentsharingcompliances` table with exception columns rather than creating separate `fsi_asardexceptions` table.

**Rationale:**
- Simpler queries: Agent compliance + exception data in one record (no joins)
- Consistent with existing compliance_status option set (Exception = 2)
- Reduced join complexity in detection/remediation scripts
- UASD pattern uses separate table, but ASARD has simpler exception model (time-bound only, no multi-step approval workflow in v1)

**Trade-offs:**
- Wider table (more nullable columns) vs. normalized schema
- Accepted: Simplicity and query performance outweigh normalization benefits for this use case

### Design Decision 2: Active Exception Check in Detection vs. Remediation

**Choice:** Implemented active exception checks in BOTH detection (upsert) and remediation (pre-remediation check).

**Rationale:**
- Detection script preserves exceptions during Dataverse upsert: Prevents exception data loss during routine scans
- Remediation script checks exceptions before PATCH: Prevents remediation of legitimately excepted agents
- Dual check provides defense-in-depth: Even if detection fails to preserve exception, remediation respects it

**Implementation:**
- Detection: Query existing record → check if active exception → preserve fields + set compliance_status=2
- Remediation: Query existing record → check if active exception → skip with informative log message

### Design Decision 3: Manual Exception Entry (No Canvas App in v1)

**Choice:** ASARD v1 uses direct Dataverse record updates for exception management (no Canvas app UI).

**Rationale:**
- Phase 4 scope: Core exception lifecycle automation (expiration tracking, notifications)
- UASD exception manager app pattern exists (`uasd-exception-manager-app.json`) but full Canvas app development out of scope for v22
- Manual entry sufficient for v1 governance workflows (low exception volume expected)
- Future enhancement: Phase 6+ can add exception manager app based on UASD pattern

**Documentation:**
- Playbook includes detailed manual exception entry procedures
- Dataverse query examples for exception creation, renewal, monitoring

### Design Decision 4: Exception Expiration Auto-Reset

**Choice:** Expired exceptions automatically reset to NonCompliant status (compliance_status=1) with all exception fields cleared.

**Rationale:**
- Ensures time-bound exceptions don't persist indefinitely
- Triggers re-scan during next detection run (agent re-evaluated against zone rules)
- Governance leads notified via Teams when exceptions expire
- Re-granting exception requires explicit approval action (prevents silent extension)

**Implementation:**
- Exception review workflow queries for expired exceptions (expires_at < now)
- Updates Dataverse record: Set compliance_status=1, clear all `fsi_exception_*` fields
- Sends Teams notification with expired agent list

## Commits

| Hash | Message |
|------|---------|
| TBD | feat(asard): add exception management — time-bound tracking, review workflow, expiration notifications |

## Self-Check

- [x] All files in manifest exist
  - Schema extension: `create_asard_dataverse_schema.py` (exception columns)
  - Detection updates: `detect_agent_sharing_violations.py` (active exception preservation)
  - Remediation updates: `remediate_agent_sharing.py` (exception skip logic)
  - Workflow: `asard-exception-review-workflow.json`
  - Adaptive cards: `adaptive-card-asard-exception-expiring.json`, `adaptive-card-asard-exception-expired.json`
  - Playbook: `docs/playbooks/asard-exception-management.md`
  - Tests: `test_detect_agent_sharing_violations.py` (3 new tests), `test_remediate_agent_sharing.py` (3 new tests)

- [x] All tests pass
  - **91 tests passing** (6 new exception tests added)
  - Detection tests: 19 tests (includes 3 exception handling tests)
  - Remediation tests: 23 tests (includes 3 exception skip tests)
  - Zone rules tests: 29 tests (unchanged, all pass)
  - BAP client tests: 20 tests (unchanged, all pass)

- [x] Code follows existing patterns
  - Schema columns use existing helper functions (`_datetime_col()`, `_memo_col()`, `_string_col()`)
  - Detection exception check follows same GET → parse → conditional logic pattern
  - Remediation exception check at function entry follows fail-fast pattern
  - Test structure matches existing test files (mocked clients, mock.patch decorators)

- [x] Language rules enforced
  - Playbook uses "supports compliance", "helps monitor", "required for"
  - No guarantees ("ensures", "prevents all", "eliminates")
  - Objective descriptions of features, no marketing language

## Integration Points

### Dataverse Schema

**New columns on `fsi_agentsharingcompliances` table:**

```python
_datetime_col("fsi_exception_expires_at", "Exception Expires At"),
_memo_col("fsi_exception_justification", "Exception Justification"),
_string_col("fsi_exception_approved_by", "Exception Approved By", max_length=256),
_datetime_col("fsi_exception_approved_at", "Exception Approved At"),
_datetime_col("fsi_exception_review_date", "Exception Review Date"),
```

All columns optional (required=False). Schema script is idempotent (creates columns only if missing).

### Detection Script Integration

**Active exception logic in `upsert_compliance_record()`:**

1. Query Dataverse for existing record using alternate key
2. If record exists and has `fsi_compliance_status = 2` AND `fsi_exception_expires_at >= now()`:
   - Set compliance_status = 2 (Exception) in payload
   - Preserve all exception fields from existing record
3. Otherwise: Evaluate normally per zone rules

**Impact:**
- Agents with active exceptions marked as "Exception" (not "NonCompliant")
- Exception count incremented in summary statistics
- CSV export unchanged (exception fields not included in scan output)

### Remediation Script Integration

**Exception check in `remediate_agent()` function:**

1. At entry: Query Dataverse for compliance record
2. If record exists with `fsi_compliance_status = 2` AND `fsi_exception_expires_at >= now()`:
   - Log skip message with expiration date
   - Return `{"success": True, "skipped": True, "skip_reason": "active_exception"}`
   - Do NOT call `modify_agent_permissions()` (no PATCH to BAP API)
3. Otherwise: Proceed with zone-based remediation

**Impact:**
- Skipped agents tracked in summary: "Skipped (active exceptions): X"
- Console output includes skip messages for visibility
- WhatIf mode respects exceptions (simulated skip, no PATCH)

### Exception Review Workflow

**Power Automate flow schedule:**
- Daily trigger at 08:00 UTC
- Parallel branches: Expiring notifications + Expired auto-reset
- Connection references: Dataverse (`shared_commondataserviceforapps`), Teams (`shared_teams`)

**Deployment:**
- Import flow via Power Automate portal or ALM pipelines
- Configure connection references (service principal or delegated auth)
- Update placeholders: `{{TEAMS_CHANNEL_ID}}`, `{{ADAPTIVE_CARD_TEMPLATE_URL}}`
- Enable flow and test manually via "Run" button

### Teams Notifications

**Expiring exceptions card:**
- Sent when exceptions expire within 14 days
- Displays agent list with days remaining, approver, justification preview
- Action buttons: "View Compliance Dashboard", "Exception Management Playbook"

**Expired exceptions card:**
- Sent after auto-reset to NonCompliant
- Displays expired agent list with previous justification
- Notice about re-scan and potential remediation

## Known Limitations

### v1 Scope Limitations

1. **Manual exception entry:** No Canvas app UI for exception management. Governance leads must update Dataverse records directly via Power Apps maker portal or Web API. Future enhancement (Phase 6+) can add exception manager app based on UASD pattern.

2. **CSV export omits exception fields:** Detection script CSV output does not include exception fields (expires_at, justification, approved_by). Rationale: Detection scan focuses on current compliance state; exception details available via Dataverse queries. Future enhancement: Add optional `--include-exceptions` flag.

3. **Single expiration date:** No multi-stage approval workflow or cascading expiration dates. Exception either active (expires_at >= now) or expired. Future enhancement: Add approval workflow based on UASD exception approval pattern.

4. **Exception renewal requires manual update:** No automated renewal reminders or approval workflow. Governance leads receive expiring notification 14 days before expiration but must manually update expires_at field to renew. Future enhancement: Add "Renew Exception" button in adaptive card that triggers approval workflow.

### Technical Limitations

1. **Exception check performance:** Detection script queries Dataverse for existing record before each upsert (GET request per agent). For large environments (>1000 agents), consider batch exception queries. Future optimization: Pre-load all exception records in memory at scan start, check in-memory dictionary.

2. **Adaptive card template hosting:** Workflow uses HTTP action to load adaptive card templates from external URL. Requires templates hosted in accessible location (GitHub raw content, Azure Blob Storage, etc.). Alternative: Embed card JSON directly in workflow (reduces external dependency but complicates maintenance).

3. **Exception review workflow error handling:** Flow does not retry failed Dataverse updates or Teams notifications. If action fails (network error, throttling), expired exception may not reset until next day's run. Future enhancement: Add retry logic and error notification to governance leads.

## Next Steps

### Phase 5: End-to-End Deployment and Validation

1. Deploy Dataverse schema updates (exception columns) to target environment
2. Deploy exception review workflow to Power Platform environment
3. Host adaptive card templates in accessible location (GitHub Pages, Azure Blob)
4. Configure Teams channel for exception notifications
5. Run end-to-end validation:
   - Create test exception with future expiration date
   - Verify detection script respects exception (marked as Exception, not NonCompliant)
   - Verify remediation script skips agent (console message logged)
   - Set expiration date to past, trigger workflow manually
   - Verify auto-reset to NonCompliant + Teams notification
6. Document deployment procedures in `docs/playbooks/asard-deployment.md`

### Future Enhancements (Phase 6+)

1. **Exception Manager App:** Canvas app for self-service exception requests, approval workflow, renewal management (based on UASD pattern)
2. **Exception Analytics Dashboard:** Power BI report with exception trends, expiration forecasting, approval metrics
3. **Advanced Notifications:** Slack/Email integration for expiring exceptions (in addition to Teams)
4. **Exception Audit Trail:** Log all exception lifecycle events (created, renewed, expired) to separate audit table for compliance reporting

---

**Summary Version:** 1.0.0  
**Phase:** 4 (Exception Management)  
**Plan:** 04-01  
**Requirements:** EXC-01, EXC-02  
**Status:** ✅ Complete
