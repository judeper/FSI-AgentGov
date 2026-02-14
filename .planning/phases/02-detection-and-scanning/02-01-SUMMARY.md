# Phase 2 Plan 01 Summary: Detection Core — BAP API Integration & Zone Evaluation

## Execution
- **Started:** 2026-02-13 22:30
- **Completed:** 2026-02-13 23:00
- **Duration:** 30min

## Dependency Graph
**Dependencies:** Phase 1 (Zone Rules & Dataverse Schema)
- Depends on: `asard_zone_rules.py` (check_agent_compliance())
- Depends on: `caa_client.py` (Dataverse Web API client)
- Depended on by: Phase 2 Plan 02 (Output & Persistence)
- Depended on by: Phase 3 (Notification & Reporting)

## Tech Stack
- **Language:** Python 3.9+
- **Authentication:** MSAL (Microsoft Authentication Library)
  - Service principal (ConfidentialClientApplication)
  - Interactive login (PublicClientApplication)
- **APIs:** 
  - BAP Admin API (https://api.bap.microsoft.com)
  - Dataverse Web API (via caa_client.py)
- **Testing:** pytest with unittest.mock
- **Retry Strategy:** urllib3.Retry (exponential backoff)

## Key Files
| File | Action | Description |
|------|--------|-------------|
| `scripts/bap_admin_client.py` | Created | BAP Admin API client with MSAL auth, retry strategy (429/5xx), graceful error handling |
| `scripts/detect_agent_sharing_violations.py` | Created | Detection script — enumerate environments/agents, retrieve permissions, evaluate zone compliance, track scan metadata |
| `scripts/test_bap_admin_client.py` | Created | Unit tests for BAP Admin client (12 tests: init, auth, API methods, error handling) |

## Decisions Made

### 1. BAP API Version Selection
- **Decision:** Use `api-version=2016-11-01` for environments, `2021-04-01` for agents/permissions
- **Rationale:** These are the stable GA versions for BAP Admin API per Microsoft documentation
- **Impact:** Ensures compatibility with current and future Power Platform tenants

### 2. Graceful Degradation Pattern
- **Decision:** API failures return empty lists; errors logged but scan continues
- **Rationale:** Single environment/agent failure shouldn't halt entire tenant scan
- **Impact:** Resilient to transient failures, throttling, or permission issues on specific environments

### 3. Evidence Hash Algorithm
- **Decision:** SHA-256 hash of `sharing_principals_json` for SEC 17a-4 audit trail
- **Rationale:** SHA-256 is NIST-approved, cryptographically strong, widely supported
- **Impact:** Immutable evidence trail for regulatory audit requirements

### 4. Scan Run ID
- **Decision:** UUID v4 for scan run correlation across all compliance results
- **Rationale:** Globally unique, no central coordination required, collision-resistant
- **Impact:** Enable audit queries across scans, track compliance changes over time

### 5. Zone 3 Approved Group Pre-Flight Validation
- **Decision:** Warning-only validation (non-blocking) if Zone 3 policy table is empty
- **Rationale:** Empty policy may be legitimate (no Zone 3 environments yet); shouldn't prevent scan
- **Impact:** Operator awareness of potential false-positives without blocking detection

### 6. Retry Strategy
- **Decision:** 3 retries, exponential backoff (factor=1), status codes 429/500/502/503/504
- **Rationale:** Follows Azure best practices for handling throttling and transient failures
- **Impact:** Resilient to API rate limits and temporary service disruptions

## Commits

| Hash | Message |
|------|---------|
| (pending) | feat(asard): add detection core — BAP API client and agent sharing scanner |

## Self-Check
- [x] All files in manifest exist
  - `scripts/bap_admin_client.py` — 448 lines
  - `scripts/detect_agent_sharing_violations.py` — 547 lines
  - `scripts/test_bap_admin_client.py` — 325 lines
- [x] All commits present (pending git commit)
- [x] Unit tests pass — 12/12 tests passing
  - `test_bap_client_initialization` — ✓
  - `test_bap_client_initialization_missing_tenant` — ✓
  - `test_bap_client_initialization_missing_client_id` — ✓
  - `test_service_principal_auth` — ✓
  - `test_interactive_auth` — ✓
  - `test_list_environments_success` — ✓
  - `test_list_agents_success` — ✓
  - `test_get_agent_permissions_success` — ✓
  - `test_retry_on_throttle_429` — ✓
  - `test_graceful_degradation_on_500` — ✓
  - `test_test_connection_success` — ✓
  - `test_test_connection_failure` — ✓
- [x] Syntax validation — `py_compile` passed for all modules
- [x] Integration points verified
  - Imports `asard_zone_rules.check_agent_compliance()` — ✓
  - Imports `caa_client.CAAClient` — ✓
  - Uses environment variables (BAP_*, CAA_*) — ✓
- [x] CLI arguments implemented
  - `--tenant-id`, `--client-id`, `--client-secret` — ✓
  - `--interactive` — ✓
  - `--environment-filter` — ✓
  - `--dry-run` — ✓
  - `--verbose` — ✓
  - `--log-file` — ✓
- [x] Logging configured
  - Console handler always enabled — ✓
  - File handler optional — ✓
  - DEBUG/INFO levels — ✓
  - Structured format — ✓
- [x] Progress logging
  - Environment enumeration: "Found N environment(s)" — ✓
  - Agent enumeration: "Environment [X/Y]: {name} — Found Z agent(s)" — ✓
  - Compliance evaluation: "✓ Compliant | ✗ Violation: {type}" — ✓
- [x] Scan metadata
  - `scan_run_id` (UUID) — ✓
  - `evidence_hash` (SHA-256) — ✓
  - `last_checked` (ISO 8601 UTC) — ✓
- [x] Summary statistics tracking
  - Counters: total_agents, compliant, non_compliant, exceptions, errors — ✓
  - Returned as tuple: (results, summary) — ✓

## Verification Results

### 1. Syntax Validation
```powershell
python -m py_compile scripts/bap_admin_client.py scripts/detect_agent_sharing_violations.py
```
**Result:** ✓ No syntax errors

### 2. Unit Tests
```powershell
python -m pytest scripts/test_bap_admin_client.py -v
```
**Result:** ✓ 12/12 tests passing (100%)

### 3. Code Pattern Compliance
- [x] BAP Admin API client follows CAAClient pattern (MSAL auth, retry strategy, env vars)
- [x] Detection script imports and uses `asard_zone_rules.check_agent_compliance()`
- [x] Evidence hash uses SHA-256
- [x] Timestamps use ISO 8601 UTC format
- [x] Graceful error handling (log and continue, don't fail entire scan)
- [x] Pre-flight validation logs warning if Zone 3 policy table empty
- [x] Scan run ID logged at start

## Integration Notes

### Phase 1 Integration
- **asard_zone_rules.check_agent_compliance()** — End-to-end compliance check
  - Input: agent_id, environment_id, environment_name, sharing_principals_json, client
  - Output: {agent_id, environment_id, zone, zone_name, compliant, violation_type, details}
- **caa_client.CAAClient** — Dataverse Web API client
  - Used for zone classification (environment policy lookup)
  - Used for approved group queries (Zone 3)

### Phase 2 Plan 02 Handoff
- **Output:** Detection script returns `(compliance_results, summary)`
  - `compliance_results`: List[Dict] — 1 record per agent scanned
  - `summary`: Dict — scan metadata and statistics
- **Next steps:** Plan 02-02 will implement:
  - Dataverse persistence (write to `fsi_AgentSharingViolations` table)
  - Console output formatting (table view, summary stats)
  - CSV export (`--output-csv` flag)

### BAP API Requirements
- **App registration:** 
  - Delegated permission: `Power.Admin` (for interactive)
  - Application permission: `Power.Admin` (for service principal)
- **Entra ID role:** Power Platform Administrator (enforced by API)
- **Endpoints:**
  - `GET /scopes/admin/environments` — List environments
  - `GET /scopes/admin/environments/{envId}/bots` — List agents
  - `GET /scopes/admin/environments/{envId}/bots/{botId}/permissions` — Get permissions

### Dataverse Requirements
- **Tables used:**
  - `fsi_environmentpolicies` — Environment zone classification
  - `fsi_approvedsecuritygrouppolicies` — Zone 3 approved groups
- **Tables written (Plan 02-02):**
  - `fsi_AgentSharingViolations` — Compliance results

## Known Limitations

1. **No Dataverse writes in Plan 02-01** — Deferred to Plan 02-02
2. **No console output formatting** — Deferred to Plan 02-02
3. **No CSV export** — Deferred to Plan 02-02
4. **Interactive auth requires user presence** — Device code flow blocks on user input
5. **Zone 3 false positives if policy table empty** — Pre-flight validation warns but doesn't block

## Next Steps (Plan 02-02)

1. Implement Dataverse persistence
   - Upsert logic (match on agent_id + scan_run_id)
   - Batch writes for large scans
   - Error handling for Dataverse write failures
2. Add console output formatting
   - Table view of violations
   - Summary statistics display
3. Add CSV export
   - `--output-csv` flag
   - Columns: agent_id, agent_name, environment_name, zone, violation_type, compliance_status, last_checked
4. Integration test with live tenant (manual, not automated)

## Phase 2 Progress

**Phase 2: Detection & Scanning (Wave 1)**
- Plan 02-01: Detection Core — **COMPLETE** ✓
- Plan 02-02: Output & Persistence — PENDING
