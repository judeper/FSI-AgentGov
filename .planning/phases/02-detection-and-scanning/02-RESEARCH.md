# Phase 2 Research: Detection & Scanning

**Phase Goal:** Create the detection engine that scans all Copilot Studio agents for sharing violations and evaluates compliance against zone-specific rules.

**Confidence:** HIGH

## Current State

### Phase 1 Artifacts (COMPLETE)

**Dataverse Schema** (`scripts/create_asard_dataverse_schema.py`):
- `fsi_AgentSharingCompliance` table — agent sharing status records with alternate key on (agent_id, environment_id) for upsert
- `fsi_ApprovedSecurityGroupPolicy` table — approved groups per zone
- Two option sets: `fsi_ASARD_compliancestatus` (Compliant/NonCompliant/Exception/Error), `fsi_ASARD_violationtype` (Everyone/Public/UnapprovedGroup/ExcessiveIndividual/CrossTenant)
- Schema creation validated in Phase 1, tables use OrganizationOwned ownership

**Zone Rules Module** (`scripts/asard_zone_rules.py`):
- `ZONE_SHARING_RULES` — zone-based sharing policies (Zone 1: individual only, Zone 2: named groups, Zone 3: pre-approved groups)
- `classify_environment_zone()` — determine zone from policy table, naming convention, or fallback (default Zone 0)
- `parse_sharing_principals()` — parse BAP API principals JSON into structured dict (individuals, security_groups, has_everyone, has_public, has_organization)
- `evaluate_zone_compliance()` — evaluate parsed principals against zone rules, return compliant/violation_type/details
- `get_approved_groups_for_zone()` — query Dataverse policy table for approved groups (Zone 3)
- `check_agent_compliance()` — end-to-end orchestrator (classify zone → parse principals → get approved groups → evaluate compliance)
- 29 unit tests passing (`scripts/test_asard_zone_rules.py`)

**Existing Dataverse Client** (`scripts/caa_client.py`):
- `CAAClient` class — MSAL-based authentication (client credentials or interactive)
- HTTP session with retry strategy (3 retries, exponential backoff, 429/500/502/503/504 handling)
- Core operations: `query()`, `create_record()`, `update_record()`, `test_connection()`
- Dry-run mode for testing
- Environment variable configuration: `CAA_TENANT_ID`, `CAA_ENVIRONMENT_URL`, `CAA_CLIENT_ID`, `CAA_CLIENT_SECRET`

### Existing UASD (v16) Detection Patterns

**UASD Detection Flow** (`src/uasd-detector-scan-agents.json`):
- Power Automate Cloud Flow (not Python script)
- Recurrence trigger: daily at 06:00 UTC
- Managed Service Identity authentication for BAP APIs
- BAP Admin API endpoints:
  - List environments: `GET https://api.bap.microsoft.com/providers/Microsoft.BusinessAppPlatform/scopes/admin/environments?api-version=2016-11-01`
  - List agents per environment: `GET https://api.bap.microsoft.com/providers/Microsoft.BusinessAppPlatform/scopes/admin/environments/{environmentId}/bots?api-version=2021-04-01`
  - Get agent permissions: `GET https://api.bap.microsoft.com/providers/Microsoft.BusinessAppPlatform/scopes/admin/environments/{environmentId}/bots/{botId}/permissions?api-version=2021-04-01`
- Nested foreach loops: environments → agents → evaluate sharing
- Dataverse upserts via Dataverse connector (OpenApiConnection action)
- Teams adaptive card notifications via Teams connector
- Environment variables for config: `fsi_UASD_DataverseUrl`, `fsi_UASD_HomeTenantId`, `fsi_UASD_TeamsGroupId`, `fsi_UASD_TeamsChannelId`
- Violation counters and scan run ID tracking
- Scope/Try/Catch error handling pattern

**UASD Dataverse Schema** (`scripts/create_uasd_dataverse_schema.py`):
- 5 tables: fsi_AgentSharingSetting, fsi_SharingViolation, fsi_SharingException, fsi_ApprovedSecurityGroup, fsi_SharingPolicy
- 6 solution-specific option sets: fsi_UASD_sharingscope, fsi_UASD_violationtype, fsi_UASD_violationstatus, fsi_UASD_exceptionstatus, fsi_UASD_remediationstatus, fsi_UASD_approvalstatus
- References shared option sets: fsi_acv_zone, fsi_acv_severity

### Contrast with ASARD Scope

| Aspect | UASD (v16) | ASARD (v22) |
|--------|-----------|-------------|
| **Focus** | Detect unrestricted sharing broadly (Everyone, Public, cross-tenant, excessive individual, unapproved groups) | Enforce least-privilege via **approved** Azure AD security groups |
| **Sharing Rules** | Threshold-based (max individual shares), Everyone/Public detection, approved group validation | **Zone-based** sharing rules (Zone 1: individual only, Zone 2: named groups, Zone 3: pre-approved groups) |
| **Dataverse Schema** | 5 tables (separation of concerns: settings, violations, exceptions, approved groups, policy) | 2 tables (compliance state + approved group policy) — simpler, zone-centric |
| **Approved Groups** | Single `fsi_ApprovedSecurityGroup` table (no zone dimension) | `fsi_ApprovedSecurityGroupPolicy` with **zone** column (different approved groups per zone) |
| **Zone Logic** | Not zone-aware (references fsi_acv_zone but doesn't use for validation) | **Zone-based compliance** — rules vary by governance zone |
| **Implementation** | Power Automate Cloud Flow (MSI auth) | TBD — Python script vs. Cloud Flow |
| **Relationship** | UASD = broad sharing detection | ASARD = approved-group enforcement (complements UASD) |

## Technical Approach

### Architecture Decision 1: Implementation Format

**Options:**
- **A) Python script** (like `create_asard_dataverse_schema.py`, `asard_zone_rules.py`)
  - Pros: Direct integration with `asard_zone_rules.py` module (no re-implementation), easier testing/debugging, `caa_client.py` reuse, can run ad-hoc from command line
  - Cons: Requires BAP Admin API token acquisition (not trivial for Python), no built-in scheduling (need external scheduler), less native Power Platform integration
- **B) Power Automate Cloud Flow** (like UASD `uasd-detector-scan-agents.json`)
  - Pros: Built-in scheduling (recurrence trigger), Managed Service Identity auth for BAP APIs (zero credential management), Dataverse connector native, Teams notifications native, consistent with UASD pattern
  - Cons: Zone rules logic must be re-implemented in Power Automate expressions, harder to test/debug, no direct reuse of `asard_zone_rules.py`

**Recommendation:** **Hybrid approach** (Python + Cloud Flow)
- **Python script** (`scripts/detect_agent_sharing_violations.py`) — core detection logic using `asard_zone_rules.py`, called by Cloud Flow via HTTP trigger or on-demand
- **Cloud Flow** (`src/asard-detector-scan-agents.json`) — scheduling, BAP API enumeration, per-agent delegation to Python logic, Dataverse writes, notifications
- **Rationale:** Maximizes code reuse (zone rules already implemented in Python with 29 tests), keeps BAP API auth simple (Cloud Flow MSI), enables ad-hoc CLI execution for testing/troubleshooting, follows FSI-AgentGov pattern (scripts/ for logic, src/ for flows)

**REVISED Recommendation:** **Python-only script** (simpler, more testable)
- **Python script** (`scripts/detect_agent_sharing_violations.py`) — full detection workflow (enumerate environments/agents, call zone rules, write Dataverse, export CSV)
- **Cloud Flow** (optional, deferred to Phase 3/5) — scheduled wrapper for Python script via Azure Automation Runbook or HTTP-triggered function
- **Rationale:** Phase 1 established Python pattern with `asard_zone_rules.py` (29 tests passing). Python script enables:
  - Direct `check_agent_compliance()` reuse (no re-implementation)
  - Unit testing of detection workflow
  - CLI execution for ad-hoc scans (troubleshooting, audit response)
  - CSV export via Python (simpler than Cloud Flow variable manipulation)
  - BAP API auth via interactive MSAL (lab-grade) or service principal (enterprise-grade)
- Cloud Flow scheduling can be added later (Phase 3 or 5) as a thin wrapper
- Consistent with v21 ALCA pattern (Python script as primary artifact, Cloud Flow as deployment option)

### Architecture Decision 2: BAP Admin API Integration

**BAP Admin API Requirements:**
- **Authentication:** OAuth 2.0 bearer token with `https://api.bap.microsoft.com/.default` scope
- **Endpoints:**
  1. List environments: `GET /providers/Microsoft.BusinessAppPlatform/scopes/admin/environments?api-version=2016-11-01`
     - Response: `{"value": [{"name": "env-guid", "properties": {"displayName": "..."}}]}`
  2. List agents: `GET /scopes/admin/environments/{envId}/bots?api-version=2021-04-01`
     - Response: `{"value": [{"properties": {"name": "bot-guid", "displayName": "..."}}]}`
  3. Get permissions: `GET /scopes/admin/environments/{envId}/bots/{botId}/permissions?api-version=2021-04-01`
     - Response: `{"value": [{"properties": {"principal": {"id": "...", "displayName": "...", "type": "User/Group/Everyone/Public", "tenantId": "..."}}}]}`

**Integration Pattern:**
- **Python requests library** with MSAL token acquisition
- **Retry strategy** (reuse `caa_client.py` retry pattern: 3 retries, exponential backoff, 429/500/502/503/504)
- **Error handling:** Log API failures, continue to next environment/agent (don't fail entire scan), record Error status in Dataverse

**Token Acquisition Options:**
- **Interactive (lab-grade):** MSAL PublicClientApplication with `acquire_token_interactive()` — same pattern as `caa_client.py`
- **Service Principal (enterprise-grade):** App registration with API permissions (Power Platform Admin → Read) + client credentials flow
- **Managed Identity (future):** Azure Automation Runbook or Function App with system-assigned MI (not required for Phase 2)

**Recommendation:** Support both interactive and service principal auth (reuse `caa_client.py` pattern, extend for BAP audience)

### Architecture Decision 3: Detection Output

**Requirements (DET-03):**
- Console output with per-agent sharing status
- Summary statistics (total agents, compliant, non-compliant, exceptions)
- CSV export
- Optional Teams adaptive card or email notification

**Console Output Pattern:**
```
Agent Sharing Compliance Scan
==============================
Scan Run ID: abc-123-def-456
Started: 2026-02-13 18:00:00 UTC

Environment: Production-Finance (Zone 3: Enterprise Managed)
  [✓] Agent: Customer Support Bot — Compliant (2 approved groups)
  [✗] Agent: Sales Assistant — VIOLATION: UnapprovedGroup (Zone 3 requires pre-approved groups. 1 unapproved group(s) found: group-xyz)
  [✓] Agent: HR Onboarding — Compliant (1 approved group)

Environment: QA-Testing (Zone 2: Team Collaboration)
  [✗] Agent: Test Bot Alpha — VIOLATION: Everyone (Zone 2 prohibits Everyone sharing)
  [✓] Agent: Test Bot Beta — Compliant (2 named groups)

Summary
-------
Total Agents: 5
Compliant: 3 (60%)
Non-Compliant: 2 (40%)
Exceptions: 0
Errors: 0

CSV Export: ./reports/asard-scan-2026-02-13-180000.csv
Dataverse Records: 5 upserted to fsi_agentsharingcompliances
```

**CSV Export Fields:**
- agent_id, agent_name, environment_id, environment_name, zone, zone_name, compliance_status, violation_type, sharing_principals_json, last_checked, scan_run_id, evidence_hash

**Teams Adaptive Card Pattern:**
- Reuse `src/adaptive-card-uasd-alert.json` as template
- Title: "Agent Sharing Compliance Alert — [N] Violations Detected"
- Body: Summary statistics + top 5 violations with agent name, environment, zone, violation type
- Actions: "View Full Report" (link to CSV), "Manage Exceptions" (link to exception management flow/app)

**Email Notification Pattern:**
- HTML email with summary table
- Deferred to Phase 5 (deployment/configuration) — not core detection requirement

### Architecture Decision 4: Dataverse Writes

**Upsert Strategy:**
- Use alternate key `fsi_agentsharingcompliance_agentkey` (agent_id + environment_id) created in Phase 1
- Dataverse Web API upsert: `PATCH /fsi_agentsharingcompliances(fsi_agent_id='agent-123',fsi_environment_id='env-456')`
- `caa_client.py` does NOT have upsert method — need to add or implement inline

**Upsert Implementation:**
```python
def upsert_compliance_record(client: CAAClient, record: dict) -> str:
    """Upsert compliance record using alternate key."""
    agent_id = record["fsi_agent_id"]
    env_id = record["fsi_environment_id"]
    
    # Construct alternate key reference
    key = f"fsi_agent_id='{agent_id}',fsi_environment_id='{env_id}'"
    url = f"{client.api_url}/fsi_agentsharingcompliances({key})"
    
    resp = client._session.patch(
        url, headers=client._get_headers(), json=record, timeout=60
    )
    # 204 No Content = existing record updated
    # 201 Created = new record created via upsert
    resp.raise_for_status()
    return "upserted"
```

**Record Fields:**
- fsi_agent_id (str, required)
- fsi_agent_name (str, required)
- fsi_environment_id (str, required)
- fsi_environment_name (str)
- fsi_sharing_principals_json (str, JSON serialized)
- fsi_violation_type (int, option set value or None)
- fsi_zone (int, option set value)
- fsi_compliance_status (int, option set value: 0=Compliant, 1=NonCompliant, 2=Exception, 3=Error)
- fsi_last_checked (datetime, required)
- fsi_remediation_date (datetime, None if not remediated)
- fsi_scan_run_id (str, GUID for batch correlation)
- fsi_evidence_hash (str, SHA-256 hash of sharing principals JSON for tamper detection)

**Evidence Hash Pattern:**
```python
import hashlib
evidence_hash = hashlib.sha256(sharing_principals_json.encode('utf-8')).hexdigest()
```

### Architecture Decision 5: Error Handling

**Error Scenarios:**
1. **BAP API auth failure** — fail fast with clear error (cannot proceed without auth)
2. **Environment enumeration failure** — log error, skip environments, record None
3. **Agent enumeration failure for environment** — log error, skip environment, continue to next
4. **Permissions retrieval failure for agent** — log error, record compliance_status=Error, continue to next agent
5. **Zone classification failure** — use default zone (Zone 0), log warning
6. **Dataverse write failure** — log error, continue to next agent (don't fail entire scan)
7. **Approved group query failure** — log warning, skip approved group check (Zone 3 agents may false-positive)

**Logging Strategy:**
- Python `logging` module (INFO for normal operations, WARNING for fallbacks, ERROR for failures)
- Console output for user-facing messages
- Log file optional (via `--log-file` CLI argument)

**Retry Strategy:**
- BAP API calls: 3 retries with exponential backoff (reuse `requests.Session` with `urllib3.Retry`)
- Dataverse writes: 3 retries with exponential backoff (via `caa_client.py` session)

## Dependencies

### External Dependencies

**Python packages:**
- `msal` — OAuth 2.0 token acquisition for BAP Admin API and Dataverse
- `requests` — HTTP client for BAP Admin API calls
- `urllib3` — Retry strategy for BAP API
- Already in `scripts/requirements.txt` from Phase 1

**Azure AD permissions (App Registration):**
- **Dataverse:** `user_impersonation` (delegated) or `Dynamics CRM.Write` (application) — already configured for `caa_client.py`
- **BAP Admin API:** `https://api.bap.microsoft.com/Power.Admin` (delegated) or `Power.Admin` (application) — NEW requirement
  - Grants: Read access to environments, agents, and permissions via BAP Admin API
  - Admin consent required

**Power Platform Admin role:**
- Detection script requires Power Platform Administrator or Dynamics 365 Administrator role (BAP Admin API requires admin scope)

### Phase 1 Prerequisites

- ✓ `fsi_agentsharingcompliances` table created with alternate key
- ✓ `fsi_approvedsecuritygrouppolicies` table populated with approved groups (Zone 3 validation)
- ✓ `fsi_ASARD_compliancestatus` option set available
- ✓ `fsi_ASARD_violationtype` option set available
- ✓ `fsi_acv_zone` option set available (shared, created by CAA schema)
- ✓ `asard_zone_rules.py` module with 29 passing tests

### Phase 2 Blockers

**None.** All Phase 1 artifacts complete. BAP Admin API is documented and accessible.

## Risks and Pitfalls

| Risk | Severity | Mitigation |
|------|----------|-----------|
| BAP Admin API rate limiting (429 Too Many Requests) | MEDIUM | Implement retry strategy with exponential backoff (3 retries). Add `--throttle-delay` CLI option for manual rate control. |
| BAP Admin API permissions JSON schema undocumented | HIGH | Use UASD flow as reference (`uasd-detector-scan-agents.json` lines 337-400). Parse principals with error handling (malformed JSON → log warning, skip agent). |
| Large tenants: 1000+ agents across 50+ environments = 10+ minutes scan time | MEDIUM | Add progress indicators (environment N/M, agent X/Y). Support `--environment-filter` for targeted scans. Async execution (Phase 5). |
| Zone classification failure (no policy, no naming match) | LOW | Default to Zone 0 (safe fallback: named groups allowed, no Everyone/Public). Log warning for manual review. |
| Approved group list empty for Zone 3 → all agents false-positive non-compliant | MEDIUM | `asard_zone_rules.py` already logs warning if `approved_groups=None`. Detection script should validate policy table populated before scan (pre-flight check). |
| Dataverse upsert alternate key timing (key may not be active immediately after creation) | LOW | Phase 1 schema script already created keys. If key doesn't exist, fail gracefully with actionable error message. |
| Sharing principals JSON exceeds memo field 1MB limit (extreme case: agent shared with 10,000+ users) | LOW | Truncate JSON with marker if >1MB. Log warning. Store full JSON in Azure Blob (Phase 5 enhancement). |
| Concurrent scan runs overwriting scan_run_id in Dataverse | LOW | Each scan generates unique GUID. Dataverse record tracks last scan only (by design — not immutable audit trail like ACV). |
| CSV export file permissions (CI/CD pipelines, restricted directories) | LOW | Default to `./reports/` directory. Add `--output-dir` CLI option. Create directory if missing. |

## Recommended Plan Structure

**Phase 2 has 2 plans** (from ROADMAP.md):

### Plan 02-01: Detection Core

**Scope:**
- Agent enumeration script (`scripts/detect_agent_sharing_violations.py`)
- BAP Admin API integration (token acquisition, environment/agent enumeration, permissions retrieval)
- Zone rules integration (`check_agent_compliance()` orchestration per agent)
- Approved group query from Dataverse policy table

**Deliverables:**
- Python script with CLI interface (`--dry-run`, `--verbose`, `--environment-filter`)
- BAP Admin API helper module or extend `caa_client.py`
- Environment → Agent → Permissions enumeration with retry/error handling
- Per-agent compliance evaluation via `asard_zone_rules.check_agent_compliance()`
- Zone 3 approved group lookup from `fsi_approvedsecuritygrouppolicies`

**Wave assignment:** Wave 1 (core functionality, blocking Plan 02-02)

**Testing:**
- Unit tests for BAP API helpers (mock responses)
- Integration test with single environment (requires live Power Platform tenant)
- Dry-run mode validation (no Dataverse writes)

**Estimated complexity:** MEDIUM (BAP API integration new, but UASD provides pattern)

### Plan 02-02: Output & Persistence

**Scope:**
- Dataverse upsert (compliance records via alternate key)
- Console output formatting (per-agent status, summary statistics)
- CSV export (agent compliance records with evidence hash)
- Optional Teams adaptive card notification (reuse UASD pattern)

**Deliverables:**
- Dataverse upsert implementation (extend `caa_client.py` or inline)
- Console output with color-coded status (✓/✗), summary table
- CSV writer (headers, per-agent rows, evidence hash, scan_run_id)
- Adaptive card JSON template (`src/adaptive-card-asard-alert.json`)
- Teams notification logic (optional, via CLI flag `--notify-teams`)

**Wave assignment:** Wave 1 (depends on Plan 02-01)

**Testing:**
- Dataverse upsert validation (create/update via alternate key)
- CSV export validation (file format, field accuracy)
- Adaptive card rendering test (Teams webhook or local render)

**Estimated complexity:** LOW (straightforward I/O operations, UASD provides templates)

### Sequencing Rationale

**Sequential execution (Plan 02-01 → 02-02):**
- Plan 02-01 establishes detection workflow (enumerate → evaluate → collect results)
- Plan 02-02 persists and presents results (Dataverse writes, CSV, notifications)
- No parallelization opportunity (02-02 depends on 02-01 output structure)

**Integration with Phase 1:**
- Both plans import and use `asard_zone_rules` module (classify_environment_zone, parse_sharing_principals, check_agent_compliance)
- Plan 02-02 writes to `fsi_agentsharingcompliances` table created in Phase 1

**Integration with Phase 3 (Enforcement):**
- Phase 3 will query `fsi_agentsharingcompliances` for non-compliant agents (compliance_status=1)
- CSV export provides audit trail for remediation planning

## Sources

**FSI-AgentGov codebase:**
- `.planning/ROADMAP.md` — Phase 2 requirements and success criteria
- `.planning/REQUIREMENTS.md` — DET-01, DET-02, DET-03 detailed specifications
- `scripts/asard_zone_rules.py` — Zone classification and compliance evaluation (Phase 1)
- `scripts/create_asard_dataverse_schema.py` — Dataverse table definitions (Phase 1)
- `scripts/caa_client.py` — Dataverse Web API client pattern
- `src/uasd-detector-scan-agents.json` — Existing UASD detection flow (BAP API patterns)
- `scripts/create_uasd_dataverse_schema.py` — UASD schema reference

**Microsoft documentation:**
- [Power Platform for Admins connector reference](https://learn.microsoft.com/en-us/connectors/powerplatformforadmins/) — BAP Admin API operations
- [Dataverse Web API alternate keys](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/retrieve-entity-using-web-api#retrieve-using-an-alternate-key) — Upsert pattern
- [MSAL Python documentation](https://msal-python.readthedocs.io/) — Token acquisition patterns

**FSI-AgentGov established patterns:**
- Python scripts as primary artifacts (Phase 1: schema creation, zone rules)
- `caa_client.py` for Dataverse interaction (all v4-v21 solutions)
- 29 unit tests for `asard_zone_rules.py` (TDD pattern)
- Managed Service Identity deferred to enterprise deployment (v21 ALCA set precedent for lab-grade → enterprise-grade evolution)

---

*Research completed: 2026-02-13*  
*Researcher: copilot*  
*Confidence: HIGH — Phase 1 artifacts complete, UASD provides clear BAP API patterns, zone rules module tested and ready for integration*
