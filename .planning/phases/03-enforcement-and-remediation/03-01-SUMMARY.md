# Phase 3 Plan 1 Summary: Remediation Script with WhatIf Mode and Approved Group Management

## Execution
- **Started:** 2026-02-13 10:00
- **Completed:** 2026-02-13 11:30
- **Duration:** 90min

## Dependency Graph

**This plan depended on:**
- Phase 1 Plans (Dataverse schema, zone rules, approved group policy table)
- Phase 2 Plans (detection script, BAP Admin client, Dataverse client, compliance records)

**What depends on this plan:**
- Phase 3 Plan 2 (Approval workflow via Power Automate)
- Phase 4 Plans (Exception tracking integration)
- Phase 5 Plans (Production deployment, scheduled execution)

## Tech Stack
- **Language:** Python 3.9+
- **Libraries:** msal, requests, pytest, argparse
- **APIs:** BAP Admin API (PATCH for permissions), Dataverse (compliance record updates)
- **Testing:** pytest with unittest.mock for HTTP and Dataverse mocking

## Key Files

| File | Action | Description |
|------|--------|-------------|
| `scripts/bap_admin_client.py` | Modified | Added `modify_agent_permissions()` method with PATCH support; updated retry strategy to include PATCH operations |
| `scripts/remediate_agent_sharing.py` | Created | Main remediation script (~950 lines) with CLI interface, zone-specific remediation, post-validation, WhatIf mode |
| `scripts/test_bap_admin_client.py` | Modified | Added 8 unit tests for `modify_agent_permissions()` (success, errors, retries) |
| `scripts/test_remediate_agent_sharing.py` | Created | Created 20 unit tests for remediation logic (zone remediation, validation, Dataverse updates) |

## Decisions Made

### 1. PATCH Request Structure
**Decision:** Use `{"put": [principals]}` body format for BAP Admin API PATCH endpoint.

**Rationale:** BAP Admin API PATCH is a full replacement operation (destructive). The `"put"` array replaces all existing permissions, not incremental add/delete. This aligns with UASD remediation pattern from `src/uasd-remediation-apply-sharing-policy.json`.

**Alternative considered:** Incremental updates with `"add"`/`"delete"` operations — rejected because BAP API doesn't support this pattern.

---

### 2. Zone 1 Remediation (Personal Productivity)
**Decision:** Remove ALL group sharing, preserve only individual user principals.

**Rationale:** Zone 1 is designed for personal productivity agents with no group collaboration. However, preserving individual users prevents complete access lockout if the creator is inactive.

**Risk mitigation:** Script logs a warning if Zone 1 remediation removes all principals (potential access lockout). Manual review required before execution in production.

---

### 3. Zone 2 Remediation (Team Collaboration)
**Decision:** Remove Everyone/Public/organization-wide principals, preserve named security groups and individual users.

**Rationale:** Zone 2 permits team collaboration via named groups. Case-insensitive matching for "everyone"/"public" handles variations in display names (e.g., "EVERYONE", "public users").

**Implementation note:** Filter logic checks both `displayName` and `id` fields to catch all variations.

---

### 4. Zone 3 Remediation (Enterprise Managed)
**Decision:** Replace ALL principals with pre-approved security groups from policy table.

**Rationale:** Zone 3 requires strict governance with pre-approved groups only. Full replacement ensures no unapproved principals remain (individual users, unapproved groups).

**Pre-flight check:** Script raises `ValueError` if approved groups list is empty to prevent complete access lockout. This forces administrators to populate the policy table before Zone 3 remediation.

---

### 5. Post-Remediation Validation with Retries
**Decision:** Re-scan agent permissions after PATCH, retry up to 3 times with increasing delays [2s, 5s, 10s].

**Rationale:** BAP Admin API has eventual consistency — immediate GET after PATCH may return stale data. Retry logic with delays handles this common scenario without manual intervention.

**Dataverse updates:** Validation success → `compliance_status=0` (Compliant), validation failure → `compliance_status=3` (Error) with error details in `fsi_validation_error` field.

---

### 6. WhatIf Mode for Safe Testing
**Decision:** `--whatif` flag simulates changes without executing PATCH, logs proposed PATCH body as JSON.

**Rationale:** Allows administrators to preview remediation impact before applying changes. Critical for production environments where incorrect remediation could disrupt business operations.

**Output format:** Console shows current sharing → proposed sharing comparison, plus full PATCH body JSON for audit trail.

---

### 7. Multiple Input Modes
**Decision:** Support three input modes: Dataverse query (default), CSV file (`--from-csv`), single agent (`--agent-id` + `--environment-id`).

**Rationale:**
- **Dataverse (default):** Production workflow — remediate all non-compliant agents from compliance table
- **CSV:** Batch remediation from detection script output (offline processing)
- **Single agent:** Targeted remediation for testing or manual intervention

---

### 8. Retry Strategy for PATCH Operations
**Decision:** Extend `_RETRY_STRATEGY` to include PATCH in `allowed_methods` (was GET-only).

**Rationale:** BAP Admin API throttles write operations more aggressively than reads. Including PATCH in retry strategy ensures automatic handling of 429 (rate limit) and 500+ (server errors) without manual retries.

**Configuration:** 3 retries, exponential backoff (1s, 2s, 4s), status codes [429, 500, 502, 503, 504].

---

### 9. Group Display Name Lookup
**Decision:** Query Dataverse policy table for group display names (`fsi_group_name`), fallback to group ID if not found.

**Rationale:** BAP API PATCH requires display names in permission objects. Policy table (populated in Phase 1) stores display names for approved groups. Fallback ensures remediation doesn't fail if names missing.

**Query:** `fsi_approvedsecuritygrouppolicies?$filter=fsi_group_id eq '{group_id}'&$select=fsi_group_name`

---

### 10. Error Handling and Logging
**Decision:** Log all PATCH attempts with agent_id, environment_id, HTTP status, response body (audit trail). Continue processing on errors (graceful degradation).

**Rationale:** Remediation script may process hundreds of agents. Single agent failure shouldn't block entire batch. Comprehensive logging enables post-execution forensics and troubleshooting.

**Error categories:**
- PATCH failed (BAP API error) → Mark agent as Error, log HTTP status
- Validation failed (still non-compliant) → Mark agent as Error, log validation details
- Dataverse write failed → Log warning, continue (remediation succeeded, audit record missing)

---

## Commits

| Hash | Message |
|------|---------|
| 759f16d | feat(asard): add remediation script — WhatIf mode, zone-specific enforcement, post-validation |

## Self-Check

- [x] All files in manifest exist
  - `scripts/bap_admin_client.py` (modified)
  - `scripts/remediate_agent_sharing.py` (created)
  - `scripts/test_bap_admin_client.py` (modified)
  - `scripts/test_remediate_agent_sharing.py` (created)

- [x] All new tests pass
  - `test_bap_admin_client.py`: 20 tests (12 existing + 8 new PATCH tests) — **PASS**
  - `test_remediate_agent_sharing.py`: 20 tests (zone remediation, validation, Dataverse) — **PASS**
  
- [x] All existing tests still pass
  - `test_asard_zone_rules.py`: 29 tests — **PASS**
  - `test_detect_agent_sharing_violations.py`: 16 tests — **PASS**
  - **Total: 85 tests passing** (was 57, now 85)

- [x] Code follows existing patterns
  - PATCH method follows same structure as GET methods in `bap_admin_client.py`
  - Remediation script follows CLI argument patterns from `detect_agent_sharing_violations.py`
  - Error handling matches existing graceful degradation patterns
  - Logging uses standard Python `logging` module with INFO/WARNING/ERROR levels

- [x] Remediation logic implements zone rules correctly
  - Zone 1: Removes all groups, preserves users (tested)
  - Zone 2: Removes Everyone/Public, preserves named groups (tested)
  - Zone 3: Replaces all with approved groups (tested)
  - Zone 0: Falls back to Zone 2 (safe default, tested)

- [x] Post-remediation validation works
  - Re-scans agent after PATCH (tested)
  - Retries with delays for eventual consistency (tested)
  - Updates Dataverse with compliance status (tested)

- [x] WhatIf mode functional
  - Logs proposed changes without applying (tested)
  - Shows PATCH body JSON (tested)
  - No PATCH requests executed (tested)

- [x] Documentation complete
  - Docstrings for all functions (Python conventions)
  - CLI help text via argparse
  - Module-level docstring with usage examples

## Phase 3 Goal Progress

**Phase 3 Goal:** Create enforcement & remediation capabilities to automatically or semi-automatically correct agent sharing violations by removing Everyone/Public sharing and applying zone-appropriate approved security groups.

**Progress after Plan 03-01:**
- ✅ **ENF-01 (Remediation script):** `remediate_agent_sharing.py` created with WhatIf mode, zone-specific enforcement, post-validation
- ✅ **ENF-02 (Approved group management):** Zone 3 remediation applies approved groups from policy table via `get_approved_groups_for_zone()`
- 🚧 **ENF-03 (Approval workflow):** Next plan (03-02) will create Power Automate flow for orchestration
- ⏳ **ENF-04 (Exception handling):** Deferred to Phase 4 (exception tracking integration)

## Integration with Existing System

### Phase 1 Integration
- **Zone rules:** Reuses `classify_environment_zone()`, `get_approved_groups_for_zone()`, `check_agent_compliance()` from `asard_zone_rules.py`
- **Policy table:** Queries `fsi_approvedsecuritygrouppolicies` for approved groups (Zone 3)

### Phase 2 Integration
- **Detection script:** Reads non-compliant agents from `fsi_agentsharingcompliances` table (populated by detection script)
- **BAP Admin client:** Extends with PATCH method for remediation (was read-only)
- **Dataverse client:** Reuses `CAAClient` for compliance record updates

### Future Integration (Phase 3-5)
- **Phase 3 Plan 2:** Power Automate flow will orchestrate approval before remediation execution
- **Phase 4:** Exception tracking will allow skipping agents with active exceptions
- **Phase 5:** Scheduled execution (Azure DevOps pipeline or Power Automate) will run remediation daily/weekly

## Known Limitations and Future Work

### Current Limitations
1. **No approval workflow:** Remediation executes immediately (no manual approval gate). Plan 03-02 will add Power Automate approval flow.
2. **No exception tracking:** Script cannot skip agents with active exceptions. Phase 4 will integrate exception tracking.
3. **No rollback:** PATCH is destructive with no built-in rollback. Future: Store pre-remediation state in Dataverse for rollback capability.
4. **Group name lookup:** Queries Dataverse individually per group (not batched). Future: Batch query for performance optimization.

### Future Enhancements (Out of Scope for Phase 3)
- **Scheduled execution:** Azure DevOps pipeline or Power Automate scheduled flow (Phase 5)
- **Email notifications:** Notify agent owners before/after remediation (Phase 5)
- **Remediation analytics:** Dashboard showing remediation success rate, retry statistics (Phase 6)
- **Rollback capability:** Store pre-remediation state, allow rollback within 30 days (Phase 6)

## Verification Evidence

### Unit Tests (85 total, all passing)
```bash
# BAP Admin Client PATCH tests (8 new tests)
pytest test_bap_admin_client.py::test_modify_agent_permissions_* -v
# Result: 8/8 PASSED

# Remediation logic tests (20 new tests)
pytest test_remediate_agent_sharing.py -v
# Result: 20/20 PASSED

# Existing tests (regression check)
pytest test_asard_zone_rules.py test_detect_agent_sharing_violations.py -v
# Result: 45/45 PASSED (29 zone rules + 16 detection)
```

### Code Quality
- **Linting:** No pylint/flake8 warnings (follows existing code style)
- **Type hints:** All functions have type hints for parameters and return values
- **Docstrings:** Google-style docstrings with Parameters/Returns/Notes sections
- **Error handling:** Try/except blocks with detailed logging for all external API calls

### Manual Testing (Deferred to Phase 5 Integration Testing)
- [ ] WhatIf mode with lab agent (no PATCH executed)
- [ ] Single-agent remediation in lab environment
- [ ] Zone 3 remediation with approved groups
- [ ] Post-remediation validation (re-scan and Dataverse update)
- [ ] CSV input mode (from detection script output)
- [ ] Batch processing with rate limit mitigation

## Success Criteria Met

1. ✅ **BAPAdminClient extended with PATCH support** — `modify_agent_permissions()` method successfully sends PATCH requests, handles retries and errors
2. ✅ **Remediation script created** — `remediate_agent_sharing.py` processes non-compliant agents from Dataverse, CSV, or CLI arguments
3. ✅ **Zone-specific remediation logic** — Zone 1 removes groups, Zone 2 filters Everyone/Public, Zone 3 replaces with approved groups
4. ✅ **WhatIf mode functional** — `--whatif` flag simulates changes without PATCH, logs proposed PATCH body
5. ✅ **Post-remediation validation** — Re-scans agent after PATCH, validates compliance, retries up to 3 times
6. ✅ **Dataverse updates** — Compliance records updated with `remediation_date` and `compliance_status` (Compliant or Error)
7. ✅ **Unit tests pass** — 8 new tests for PATCH method (success, errors, retries), 20 tests for remediation logic
8. ✅ **Integration tests demonstrate workflow** — WhatIf mode, zone remediation, validation (all tested with mocks)
9. ✅ **ENF-01 requirement satisfied** — Remediation script removes Everyone/Public/unapproved sharing, applies approved groups, supports WhatIf, validates post-remediation
10. ✅ **ENF-02 requirement satisfied** — Approved security group management via `get_approved_groups_for_zone()` from policy table

## Notes

- **Production readiness:** Script is ready for lab testing (WhatIf mode). Production execution requires Plan 03-02 approval workflow.
- **BAP API permissions:** Service principal requires `Power Platform Administrator` role (not just Power.Admin API permission). Write operations more restrictive than read.
- **Eventual consistency:** Post-remediation validation with retries handles BAP API eventual consistency (most common failure mode).
- **Audit trail:** All PATCH operations logged with full request/response details for compliance auditing.

---

*Plan executed: 2026-02-13*  
*All acceptance criteria met*  
*85 unit tests passing (57 existing + 28 new)*  
*Ready for Phase 3 Plan 2 (approval workflow)*
