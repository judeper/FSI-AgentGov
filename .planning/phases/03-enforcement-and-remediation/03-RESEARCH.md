# Phase 3 Research: Enforcement & Remediation

**Phase Goal:** Create the remediation capability to restrict agent sharing and apply approved security groups, with approval workflow for governance control.

**Confidence:** HIGH

## Current State

### Phase 1-2 Artifacts (COMPLETE)

**Dataverse Schema** (`scripts/create_asard_dataverse_schema.py`):
- `fsi_AgentSharingCompliance` table — agent sharing status records with alternate key on (agent_id, environment_id) for upsert
- `fsi_ApprovedSecurityGroupPolicy` table — approved groups per zone (zone, group_id, group_name, purpose, active flag)
- Two option sets: `fsi_ASARD_compliancestatus` (Compliant/NonCompliant/Exception/Error), `fsi_ASARD_violationtype` (Everyone/Public/UnapprovedGroup/ExcessiveIndividual/CrossTenant)
- Tables ready for remediation status updates (remediation_date column exists)

**Zone Rules Module** (`scripts/asard_zone_rules.py`):
- `get_approved_groups_for_zone(zone, client)` — query `fsi_approvedsecuritygrouppolicies` table filtered by zone and active status
  - Returns `List[str]` of Azure AD group object IDs
  - Already implemented and tested (29 unit tests passing)
  - Zone 3 (Enterprise Managed) requires pre-approved groups from this function
  - Zone 2 (Team Collaboration) allows any named security groups (no restriction)
  - Zone 1 (Personal Productivity) prohibits all group sharing
- `ZONE_SHARING_RULES` — zone-based sharing policies with `require_approved_groups` flag
- Used by remediation to determine which groups are valid per zone

**BAP Admin Client** (`scripts/bap_admin_client.py`):
- `BAPAdminClient` class — MSAL-based authentication (service principal or interactive)
- HTTP session with retry strategy (3 retries, exponential backoff, 429/500/502/503/504 handling)
- Core read operations: `list_environments()`, `list_agents()`, `get_agent_permissions()`
- **MISSING:** Methods for modifying agent permissions (PUT/DELETE/PATCH operations)
- Base URL: `https://api.bap.microsoft.com`
- Auth scope: `https://api.bap.microsoft.com/.default`

**Detection Script** (`scripts/detect_agent_sharing_violations.py`):
- Full detection workflow (enumerate environments/agents, evaluate compliance, write to Dataverse)
- Writes compliance records with `compliance_status` field (0=Compliant, 1=NonCompliant, 2=Exception, 3=Error)
- CSV export with agent details, sharing principals JSON, violation type
- 57 tests passing (29 zone rules + 12 BAP client + 16 detection output)
- Remediation will query Dataverse for non-compliant agents (compliance_status=1) or read detection CSV

**Adaptive Card Template** (`src/adaptive-card-asard-alert.json`):
- Teams card for detection alerts with summary statistics
- Template variables: scan_run_id, total_agents, non_compliant_count, violation_list
- Can be adapted for remediation approval card (need agent details, current sharing, proposed groups)

### Existing UASD (v16) Remediation Patterns

**UASD Remediation Flow** (`src/uasd-remediation-apply-sharing-policy.json`):
- Power Automate Cloud Flow (MSI auth for BAP APIs)
- Trigger: Dataverse webhook on `fsi_SharingViolation` create/update (status=Open)
- Workflow:
  1. Extract agent_id, environment_id, violation_type from trigger
  2. Check for active exception (skip remediation if exception granted)
  3. Load approved security groups from Dataverse
  4. **Build principal list:** Transform groups into BAP-compatible format
  5. **Remediation mode decision:** Automatic (PUBLIC_LINK only) vs. Approval (default)
  6. **BAP API PATCH:** Overwrite agent permissions with approved principals
  7. Update violation record (remediation_date, status=Remediated)
  8. Teams notification (success card)

**Key BAP API Pattern (lines 400-450):**
```json
{
  "type": "Http",
  "inputs": {
    "method": "PATCH",
    "uri": "https://api.bap.microsoft.com/providers/Microsoft.BusinessAppPlatform/scopes/admin/environments/{environmentId}/bots/{botId}/permissions?api-version=2021-04-01",
    "headers": {
      "Content-Type": "application/json"
    },
    "body": {
      "put": [
        {
          "properties": {
            "roleName": "CanView",
            "principal": {
              "id": "group-guid",
              "type": "Group",
              "displayName": "Finance Team"
            }
          }
        }
      ]
    },
    "authentication": {
      "type": "ManagedServiceIdentity",
      "audience": "https://api.bap.microsoft.com"
    }
  }
}
```

**Critical Insight:** The `PATCH` request body uses `"put": [...]` property with an array of permission objects. The `put` operation **replaces** all existing permissions with the provided list (not additive).

**Principal Object Structure:**
```json
{
  "properties": {
    "roleName": "CanView",  // or "CanEdit" (admin), "CanViewWithShare" (contributor)
    "principal": {
      "id": "azure-ad-object-id",
      "type": "Group",  // or "User"
      "displayName": "Display Name"
    }
  }
}
```

**UASD Approval Workflow** (`src/uasd-exception-approval-workflow.json`):
- Trigger: Dataverse webhook on `fsi_SharingException` create (status=Pending)
- Workflow:
  1. Load exception details from Dataverse
  2. **Start approval action:** Power Automate Approvals connector
     - `ApprovalCreationInput/title`: "UASD Exception Approval — {agent_name}"
     - `ApprovalCreationInput/assignedTo`: Governance lead email (from environment variable or config)
     - `ApprovalCreationInput/details`: Agent details, violation type, business justification, expiration date
     - Approval timeout: 7 days (configurable)
  3. Wait for response (Approve/Reject)
  4. Update exception record (status=Approved/Rejected, approver, approved_date)
  5. If approved: set expiration date (request date + 90 days default)
  6. Teams notification (approval decision card)
  7. If approved: update violation record (status=Exception_Granted)

**Approval Card Pattern:**
- Adaptive card embedded in approval request body
- Sections: Agent summary (name, environment, zone), violation details, current sharing principals, proposed changes, business justification
- Actions: Approve, Reject (handled by Approvals connector, not card actions)

### Contrast with ASARD Scope

| Aspect | UASD (v16) | ASARD (v22) |
|--------|-----------|-------------|
| **Remediation Trigger** | Violation record create/update (reactive) | Script-driven (batch or on-demand) |
| **Approved Groups** | Single `fsi_ApprovedSecurityGroup` table (no zone dimension) | `fsi_ApprovedSecurityGroupPolicy` with **zone** column — different groups per zone |
| **Remediation Mode** | Automatic for PUBLIC_LINK, Approval for all others | **Approval-first** for all zones (ENF-03 requirement), optional `-WhatIf` simulation |
| **BAP API Usage** | PATCH with MSI auth (Cloud Flow) | PATCH with service principal or interactive auth (Python script) |
| **Post-Remediation** | Update violation record only | **Post-remediation validation** — re-scan agent to confirm changes applied |
| **Integration** | Standalone flow (trigger-driven) | Part of detection → remediation workflow (detection writes compliance records, remediation reads them) |

## Technical Approach

### Architecture Decision 1: Remediation Implementation Format

**Options:**
- **A) Python script** (`scripts/remediate_agent_sharing.py`)
  - Pros: Direct integration with `asard_zone_rules.py` (reuse `get_approved_groups_for_zone()`), reuse `bap_admin_client.py` patterns, CLI execution for ad-hoc remediation, `-WhatIf` mode trivial to implement, unit testable, consistent with Phase 1-2 Python pattern
  - Cons: No built-in approval workflow (need external approval gate or Phase 3 Plan B flow integration), manual execution unless wrapped by scheduler
- **B) Power Automate Cloud Flow** (like UASD `uasd-remediation-apply-sharing-policy.json`)
  - Pros: Built-in Approvals connector (ENF-03), MSI auth for BAP APIs, Teams notifications native, trigger-driven execution
  - Cons: Zone rules logic re-implementation in Power Automate expressions, `-WhatIf` harder to implement (no script CLI), no direct reuse of `asard_zone_rules.py`, harder to test
- **C) Hybrid** (Python script + Cloud Flow wrapper)
  - Pros: Python core remediation logic (reuse zone rules), Cloud Flow for approval workflow (Approvals connector), best of both worlds
  - Cons: Two artifacts to maintain, more complex integration

**Recommendation:** **Option A (Python script) for Plan 03-01, Option B (Cloud Flow) for Plan 03-02**
- **Plan 03-01 (Remediation Script):** Python script with `-WhatIf` mode, approved group logic, post-remediation validation, Dataverse writes
  - CLI flags: `--agent-id`, `--environment-id`, `--whatif`, `--auto-approve` (skip approval for testing), `--zone-override`
  - Query Dataverse for non-compliant agents or accept agent ID directly
  - Apply zone-appropriate approved groups via BAP API PATCH
  - Re-scan agent post-remediation to validate changes (call detection logic)
  - Update compliance record (remediation_date, compliance_status=Compliant or Error)
- **Plan 03-02 (Approval Workflow):** Power Automate Cloud Flow with Approvals connector (ENF-03)
  - Trigger: Manual (governance lead initiates) or scheduled check for non-compliant agents
  - Load non-compliant agents from Dataverse (compliance_status=1, no active exception)
  - For each agent: Start approval request with adaptive card (agent details, current sharing, proposed groups, zone context)
  - On approval: Invoke Python remediation script via Azure Automation Runbook or HTTP trigger (or inline HTTP action to BAP API)
  - On rejection: Log decision, no changes
  - Teams notification (approval result)
- **Rationale:** Python script enables ad-hoc remediation and `-WhatIf` testing (critical for Phase 3 validation). Cloud Flow provides enterprise approval workflow (ENF-03 requirement). Separation of concerns: remediation logic (Python) vs. approval orchestration (Cloud Flow).

### Architecture Decision 2: BAP Admin API for Permission Modification

**API Endpoint:**
```
PATCH https://api.bap.microsoft.com/providers/Microsoft.BusinessAppPlatform/scopes/admin/environments/{environmentId}/bots/{botId}/permissions?api-version=2021-04-01
```

**Request Body:**
```json
{
  "put": [
    {
      "properties": {
        "roleName": "CanView",
        "principal": {
          "id": "group-object-id",
          "type": "Group",
          "displayName": "Group Display Name"
        }
      }
    }
  ]
}
```

**Behavior:**
- `"put"` operation **replaces** all existing permissions with the provided array (destructive operation)
- No `"delete"` or `"add"` operations — always full replacement
- Multiple principals supported (array of permission objects)
- Role types: `CanView` (viewer), `CanViewWithShare` (contributor), `CanEdit` (admin/owner)
- ASARD default: `CanView` for approved security groups (least privilege)

**Auth Requirements:**
- Bearer token with `https://api.bap.microsoft.com/.default` scope
- Service principal requires `Power.Admin` API permission (admin consent)
- MSI auth requires Managed Identity with Power Platform Administrator role

**Error Handling:**
- 400 Bad Request: Invalid principal ID, malformed JSON
- 401 Unauthorized: Token expired or invalid scope
- 403 Forbidden: Insufficient permissions (not Power Platform Admin)
- 404 Not Found: Agent or environment doesn't exist
- 429 Too Many Requests: Rate limiting (retry with backoff)
- 500/502/503 Internal Server Error: Transient failure (retry)

**Retry Strategy:**
- Reuse `BAPAdminClient` retry pattern (3 retries, exponential backoff, 429/500/502/503/504)
- Log all PATCH attempts and responses for audit trail

**Implementation in Python:**
```python
def modify_agent_permissions(
    self, 
    environment_id: str, 
    agent_id: str, 
    principals: List[Dict[str, Any]]
) -> bool:
    """Replace agent permissions with approved principals.
    
    Parameters
    ----------
    environment_id : str
        Power Platform environment GUID.
    agent_id : str
        Copilot Studio agent (bot) GUID.
    principals : list[dict]
        List of BAP permission objects with structure:
        [{"properties": {"roleName": "CanView", "principal": {...}}}]
    
    Returns
    -------
    bool
        True if PATCH succeeded, False on error.
    """
    url = (
        f"{self.base_url}/providers/Microsoft.BusinessAppPlatform/"
        f"scopes/admin/environments/{environment_id}/bots/{agent_id}/permissions"
    )
    params = {"api-version": "2021-04-01"}
    body = {"put": principals}
    
    try:
        resp = self._session.patch(
            url, 
            headers=self._get_headers(), 
            params=params, 
            json=body, 
            timeout=60
        )
        resp.raise_for_status()
        logger.info("Successfully modified permissions for agent %s", agent_id)
        return True
    except requests.RequestException as exc:
        logger.error(
            "Failed to modify permissions for agent %s in environment %s: %s",
            agent_id, environment_id, exc
        )
        return False
```

**Add to `BAPAdminClient` class** (extend existing client rather than create new module).

### Architecture Decision 3: Remediation Integration with Detection

**Input Sources:**
1. **Dataverse query** (primary): Query `fsi_agentsharingcompliances` for non-compliant agents
   - Filter: `fsi_compliance_status eq 1` (NonCompliant)
   - Exclude agents with active exceptions (separate table: `fsi_SharingException` from UASD or new `fsi_ASARDException`)
2. **Detection CSV export** (secondary): Read CSV from detection script output
   - Columns: agent_id, environment_id, zone, compliance_status, violation_type, sharing_principals_json
   - Filter: compliance_status="NonCompliant"
3. **Direct agent ID** (ad-hoc): CLI argument `--agent-id` + `--environment-id`
   - Use case: Manual remediation of specific agent, testing, incident response

**Recommended Approach:** Support all three (Dataverse primary, CSV fallback, CLI override)
- Default: Query Dataverse for non-compliant agents (compliance_status=1, last_checked within 24 hours to avoid stale data)
- Flag: `--from-csv <path>` to read detection CSV instead
- Flag: `--agent-id <id> --environment-id <id>` for single-agent remediation

**Workflow:**
```
1. Load non-compliant agents (Dataverse or CSV)
2. For each agent:
   a. Classify environment zone (reuse asard_zone_rules.classify_environment_zone())
   b. Get approved groups for zone (asard_zone_rules.get_approved_groups_for_zone())
   c. Build permission objects (transform group IDs into BAP principal format)
   d. If --whatif: Log proposed changes, skip PATCH
   e. Else: PATCH agent permissions with approved groups
   f. Post-remediation validation: Re-scan agent (call get_agent_permissions(), evaluate compliance)
   g. Update Dataverse compliance record (remediation_date, compliance_status)
   h. Log outcome (success/failure/whatif)
3. Summary report (total agents, remediated, failed, whatif)
```

### Architecture Decision 4: WhatIf Mode Implementation

**Requirements (ENF-01):**
- `-WhatIf` CLI flag (or `--whatif`, `--dry-run`) simulates remediation without applying changes
- Show proposed changes: Current sharing principals → Approved groups
- No BAP API calls made (read-only operations only)
- Log proposed PATCH body for review

**Implementation Pattern:**
```python
if args.whatif:
    logger.info("[WHATIF] Would replace %d principals with %d approved groups",
                len(current_principals), len(approved_principals))
    logger.info("[WHATIF] Proposed PATCH body: %s", 
                json.dumps({"put": permission_objects}, indent=2))
    # Skip PATCH, no Dataverse write
    continue
else:
    # Execute PATCH
    success = bap_client.modify_agent_permissions(
        environment_id, agent_id, permission_objects
    )
```

**Console Output (WhatIf):**
```
Agent: HR Onboarding Bot (env-123)
  Zone: 3 (Enterprise Managed)
  Current Sharing: 5 principals (2 groups, 3 individuals)
    - Everyone (organization-wide)
    - Group: "All Staff" (unapproved)
    - User: john.doe@contoso.com
    - User: jane.smith@contoso.com
    - User: bob.johnson@contoso.com
  
  [WHATIF] Proposed Changes:
    REMOVE: Everyone, "All Staff", 3 individual users
    ADD: "Finance-Approved-Viewers" (group-guid-1), "HR-Approved-Editors" (group-guid-2)
  
  [WHATIF] Proposed PATCH Body:
    {
      "put": [
        {"properties": {"roleName": "CanView", "principal": {"id": "group-guid-1", "type": "Group", "displayName": "Finance-Approved-Viewers"}}},
        {"properties": {"roleName": "CanView", "principal": {"id": "group-guid-2", "type": "Group", "displayName": "HR-Approved-Editors"}}}
      ]
    }
```

### Architecture Decision 5: Post-Remediation Validation

**Requirements (ENF-01):**
- Validate changes post-remediation (confirm BAP API actually modified permissions)
- Re-scan agent sharing configuration after PATCH
- Compare post-remediation sharing with expected state (approved groups only)
- Update Dataverse compliance record (compliant if validated, error if mismatch)

**Implementation:**
```python
# 1. Apply remediation
success = bap_client.modify_agent_permissions(env_id, agent_id, approved_principals)

if not success:
    logger.error("Remediation PATCH failed for agent %s", agent_id)
    # Update Dataverse: compliance_status=Error, remediation_date=None
    return

# 2. Wait brief delay (API consistency)
time.sleep(2)

# 3. Re-scan agent permissions
current_permissions = bap_client.get_agent_permissions(env_id, agent_id)
current_principals_json = json.dumps(current_permissions)

# 4. Re-evaluate compliance
result = check_agent_compliance(
    agent_id=agent_id,
    environment_id=env_id,
    environment_name=env_name,
    sharing_principals_json=current_principals_json,
    client=dataverse_client,
)

# 5. Validate outcome
if result["compliant"]:
    logger.info("Post-remediation validation PASSED for agent %s", agent_id)
    # Update Dataverse: compliance_status=Compliant, remediation_date=now()
else:
    logger.warning(
        "Post-remediation validation FAILED for agent %s: %s",
        agent_id, result["details"]
    )
    # Update Dataverse: compliance_status=Error, remediation_date=now()
    # Log mismatch for investigation (BAP API eventual consistency issue?)
```

**Validation Failure Scenarios:**
- **BAP API eventual consistency:** PATCH succeeded but GET returns stale data (retry after delay)
- **Partial PATCH application:** Some principals added, others not (BAP API bug — rare)
- **Concurrent modification:** Another admin changed sharing between PATCH and GET (audit log divergence)
- **Zone classification mismatch:** Agent moved to different environment/zone mid-remediation (edge case)

**Mitigation:**
- Retry post-remediation validation up to 3 times with increasing delays (2s, 5s, 10s)
- Log all validation failures with full evidence (pre-PATCH JSON, PATCH body, post-PATCH JSON)
- Dataverse record tracks validation result (compliance_status=Error, evidence_hash for forensics)

### Architecture Decision 6: Approved Security Group Management

**Source:** `fsi_ApprovedSecurityGroupPolicy` table (created in Phase 1)

**Schema:**
- `fsi_zone` (int, option set) — Governance zone (1, 2, 3)
- `fsi_group_id` (string) — Azure AD security group object ID
- `fsi_group_name` (string) — Group display name (for logging/UI)
- `fsi_purpose` (string, optional) — Business justification for approval
- `fsi_is_active` (bool) — Active/inactive flag (deactivate without deleting)

**Query Pattern (already in `asard_zone_rules.py`):**
```python
approved_groups = get_approved_groups_for_zone(zone=3, client=dataverse_client)
# Returns: ["group-guid-1", "group-guid-2", ...]
```

**Remediation Usage:**
1. Classify agent environment zone → Zone 1, 2, or 3
2. Query approved groups for zone → List of group IDs
3. Transform group IDs into BAP permission objects:
   ```python
   permission_objects = []
   for group_id in approved_groups:
       # Look up group display name (query Entra ID Graph API or use cached value from policy table)
       group_name = get_group_display_name(group_id)  # Optional helper
       permission_objects.append({
           "properties": {
               "roleName": "CanView",
               "principal": {
                   "id": group_id,
                   "type": "Group",
                   "displayName": group_name or group_id  # Fallback to ID if name lookup fails
               }
           }
       })
   ```
4. PATCH agent permissions with `{"put": permission_objects}`

**Zone-Specific Logic:**
- **Zone 1 (Personal Productivity):** No group sharing allowed → remediation removes ALL groups, leaves only individual users (creator/owner)
  - **CRITICAL:** Zone 1 remediation may lock out users if creator is not active — require manual review or approval
  - Approved groups query returns empty list for Zone 1 (by design)
- **Zone 2 (Team Collaboration):** Named groups allowed → remediation removes Everyone/Public, preserves valid named groups
  - Approved groups query returns empty list (Zone 2 doesn't restrict which groups, just prohibits Everyone/Public)
  - Remediation logic: Filter out Everyone/Public/organization principals, keep named groups + individuals
- **Zone 3 (Enterprise Managed):** Pre-approved groups only → remediation replaces ALL principals with approved groups
  - Approved groups query returns policy table groups (e.g., ["Finance-Viewers", "HR-Editors"])
  - Remediation logic: Full replacement with approved groups (destructive — removes all existing principals)

**Zone 1 Remediation Challenge:**
- Removing all groups may leave agent inaccessible (no viewers except creator)
- **Mitigation:** Require approval for Zone 1 remediation (ENF-03), show creator/owner in approval card, governance lead confirms creator is still active

**Zone 2 Remediation Pattern (Preserve Named Groups):**
```python
# Zone 2: Remove Everyone/Public, preserve named groups
current_principals = bap_client.get_agent_permissions(env_id, agent_id)
parsed = parse_sharing_principals(json.dumps(current_principals))

# Filter out prohibited principals
permitted_principals = []
for principal in current_principals:
    p_type = principal.get("type", "").lower()
    if p_type in ("group", "securitygroup"):
        # Keep named groups (not Everyone/Public/organization)
        if principal.get("id") and principal.get("displayName"):
            permitted_principals.append({
                "properties": {
                    "roleName": principal.get("roleName", "CanView"),
                    "principal": principal
                }
            })
    elif p_type == "user":
        # Keep individual users
        permitted_principals.append({
            "properties": {
                "roleName": principal.get("roleName", "CanView"),
                "principal": principal
            }
        })
    # Skip Everyone/Public/organization principals

# PATCH with filtered list
bap_client.modify_agent_permissions(env_id, agent_id, permitted_principals)
```

**Zone 3 Remediation Pattern (Full Replacement):**
```python
# Zone 3: Replace ALL principals with approved groups
approved_groups = get_approved_groups_for_zone(zone=3, client=dataverse_client)

permission_objects = []
for group_id in approved_groups:
    permission_objects.append({
        "properties": {
            "roleName": "CanView",
            "principal": {
                "id": group_id,
                "type": "Group",
                "displayName": get_group_name_from_policy(group_id, dataverse_client)
            }
        }
    })

# PATCH with approved groups only (removes ALL existing principals)
bap_client.modify_agent_permissions(env_id, agent_id, permission_objects)
```

### Architecture Decision 7: Approval Workflow Design (ENF-03)

**Requirements:**
- Power Automate flow triggering approval before changes applied
- Approval card includes agent details, current sharing, proposed groups, zone context
- Approval decision (Approve/Reject) gates remediation execution

**Trigger Options:**
1. **Manual trigger** (governance lead initiates) — Button click, scheduled recurrence
2. **Dataverse trigger** (detection writes compliance record) — Webhook on `fsi_agentsharingcompliances` create/update with compliance_status=1
3. **Detection script trigger** (detection calls flow) — HTTP POST to flow endpoint with agent list JSON

**Recommendation:** **Manual trigger** (scheduled daily or on-demand)
- Query Dataverse for non-compliant agents (compliance_status=1, no active exception)
- Batch approval (multiple agents in single approval request or loop with individual requests)
- Governance lead reviews and approves/rejects each agent

**Approval Card Structure:**
```
🔐 Agent Sharing Remediation Approval

Agent: HR Onboarding Bot
Environment: Production - Finance (env-123)
Governance Zone: Zone 3 (Enterprise Managed)
Violation Type: UnapprovedGroup

Current Sharing (5 principals):
  🔴 Everyone (organization-wide) — REMOVE
  🟡 Group: "All Staff" (unapproved) — REMOVE
  🟡 User: john.doe@contoso.com — REMOVE
  🟡 User: jane.smith@contoso.com — REMOVE
  🟡 User: bob.johnson@contoso.com — REMOVE

Proposed Changes:
  ✅ ADD: "Finance-Approved-Viewers" (group-guid-1) — 150 members
  ✅ ADD: "HR-Approved-Editors" (group-guid-2) — 12 members

Impact:
  - Existing 5 principals will be replaced
  - Agent access restricted to 2 approved security groups (162 total members)
  - Creator/owner preserved: jane.smith@contoso.com (system)

Compliance: Non-Compliant (detected 2026-02-13)
Last Checked: 2026-02-13 18:00 UTC
Scan Run ID: abc-123-def-456

[Approve] [Reject]
```

**Flow Workflow:**
1. Trigger: Scheduled (daily 09:00) or manual button
2. Query Dataverse: Non-compliant agents (compliance_status=1, last_checked within 24h)
3. For each agent (or batch of N agents):
   a. Load agent details (name, environment, zone, current sharing, violation type)
   b. Get approved groups for zone (Dataverse policy table)
   c. Build proposed changes (current → approved)
   d. Compose adaptive card (agent details, current sharing, proposed changes, zone context)
   e. **Start approval:** Approvals connector
      - Title: "ASARD Remediation Approval — {agent_name}"
      - Assigned to: Governance lead (environment variable `fsi_ASARD_ApprovalEmail`)
      - Details: Adaptive card body (JSON string)
      - Timeout: 7 days (configurable)
   f. Wait for response
   g. If **Approved**:
      - Execute remediation (HTTP action to BAP API PATCH or invoke Python script via Runbook/Function)
      - Update Dataverse (remediation_date, compliance_status=Compliant if validated)
      - Teams notification (success)
   h. If **Rejected**:
      - Log rejection reason (approver comments)
      - Update Dataverse (approval_status=Rejected, no remediation)
      - Teams notification (rejection)
4. Summary notification: X agents approved, Y rejected, Z remediated successfully

**Implementation Artifact:** `src/asard-remediation-approval-workflow.json` (Power Automate Cloud Flow export)

**Alternative (Simpler):** Python script with `--approval-required` flag that pauses and prompts for Y/N confirmation before PATCH. Cloud Flow in Phase 5 for enterprise automation.

## Dependencies

### External Dependencies

**Python packages:**
- `msal` — OAuth 2.0 token acquisition (already in requirements.txt)
- `requests` — HTTP client for BAP API (already in requirements.txt)
- No new packages required

**Azure AD permissions (App Registration):**
- **BAP Admin API:** `https://api.bap.microsoft.com/.default` with `Power.Admin` scope (application permission)
  - Required for PATCH operations on agent permissions
  - Admin consent required
  - **NEW:** Phase 2 only needed READ access (GET endpoints); Phase 3 adds WRITE (PATCH)
- **Dataverse:** `user_impersonation` (delegated) or application permission — already configured from Phase 1-2

**Power Platform Admin role:**
- Remediation script requires Power Platform Administrator role (BAP Admin API write operations)
- Service principal must be added to Power Platform Admin role (cannot use Entra ID role alone)

### Phase 1-2 Prerequisites

- ✓ `fsi_agentsharingcompliances` table with compliance_status column
- ✓ `fsi_approvedsecuritygrouppolicies` table populated with approved groups per zone
- ✓ `asard_zone_rules.get_approved_groups_for_zone()` function tested and working
- ✓ `bap_admin_client.py` with GET operations (list_environments, list_agents, get_agent_permissions)
- ✓ Detection script writes non-compliant agents to Dataverse (compliance_status=1)

### Phase 3 Blockers

**None.** All prerequisites complete. BAP Admin API PATCH endpoint is documented (UASD provides working pattern).

## Risks and Pitfalls

| Risk | Severity | Mitigation |
|------|----------|-----------|
| **Zone 1 remediation removes all group sharing → agent inaccessible** | HIGH | Require approval for Zone 1 (ENF-03). Approval card shows creator/owner. Governance lead confirms creator is active. Document Zone 1 risk in troubleshooting guide. |
| **Zone 3 remediation replaces ALL principals → overwrites valid users** | HIGH | `-WhatIf` mode shows full before/after state. Approval workflow required (ENF-03). Post-remediation validation detects mismatch. Log all PATCH bodies for rollback. |
| **BAP API eventual consistency → post-remediation validation fails incorrectly** | MEDIUM | Retry validation up to 3 times with increasing delays (2s, 5s, 10s). Log all validation attempts. Dataverse evidence_hash tracks changes for forensics. |
| **Approved group list empty for zone → remediation removes all access** | HIGH | Pre-flight check: Query approved groups, fail if empty for Zone 3. Log warning if Zone 2 has no approved groups (allowed but suspicious). Zone 1 expects empty list. |
| **Concurrent remediation runs overwrite each other** | MEDIUM | Python script uses exclusive lock file or Dataverse flag (remediation_in_progress). Cloud Flow uses concurrency control (single instance). |
| **BAP API rate limiting during bulk remediation** | MEDIUM | Throttle PATCH requests (configurable delay between agents, e.g., 2s). Batch remediation via `--batch-size` flag (remediate N agents, wait, continue). Retry on 429 with exponential backoff. |
| **PATCH fails but Dataverse record updated → inconsistent state** | MEDIUM | Update Dataverse AFTER post-remediation validation (not after PATCH). If validation fails, compliance_status=Error (not Compliant). |
| **Approval workflow timeout (7 days) → agents remain non-compliant** | LOW | Scheduled re-scan triggers new approval if previous expired. Email reminder to governance lead before expiration (optional enhancement). |
| **Remediation removes creator/owner → agent orphaned** | MEDIUM | BAP API may preserve agent creator implicitly (system principal, not visible in permissions list). Test Zone 3 remediation in lab environment. Document behavior in deployment guide. |
| **Group display name lookup fails (Entra ID Graph API permission missing)** | LOW | Use group ID as fallback display name in PATCH body. BAP API accepts empty displayName (ID is required field). Log warning. |
| **Cross-tenant groups in sharing principals (B2B)** | LOW | Detect cross-tenant principals in detection phase (violation_type=CrossTenant). Remediation skips cross-tenant groups or removes them (configurable behavior). Document in deployment guide. |

## Recommended Plan Structure

**Phase 3 has 2 plans** (from ROADMAP.md):

### Plan 03-01: Remediation Script with WhatIf

**Scope:**
- Extend `BAPAdminClient` with `modify_agent_permissions()` method (BAP API PATCH)
- Remediation script (`scripts/remediate_agent_sharing.py`) with CLI interface
- Query Dataverse for non-compliant agents or accept agent ID directly
- Zone-based approved group logic (reuse `get_approved_groups_for_zone()`)
- Zone 1/2/3 remediation patterns (remove prohibited principals, apply approved groups)
- `-WhatIf` mode (simulate changes, no PATCH, log proposed body)
- Post-remediation validation (re-scan agent, update Dataverse)
- Dataverse writes (remediation_date, compliance_status=Compliant/Error)

**Deliverables:**
- `bap_admin_client.py` extended with `modify_agent_permissions(env_id, agent_id, principals)` method
- `scripts/remediate_agent_sharing.py` with CLI:
  - `--whatif` / `--dry-run` (simulation mode)
  - `--agent-id <id> --environment-id <id>` (single agent)
  - `--from-csv <path>` (read detection CSV)
  - `--from-dataverse` (query non-compliant agents, default)
  - `--zone-override <1|2|3>` (testing)
  - `--auto-approve` (skip approval prompt, for testing)
  - `--verbose` (detailed logging)
- Console output with remediation summary (agents processed, succeeded, failed, whatif)
- Unit tests for `modify_agent_permissions()` (mock BAP API responses)
- Integration test for full remediation workflow (lab environment required)

**Wave assignment:** Wave 1 (core functionality, blocking Plan 03-02)

**Testing:**
- Unit test: `modify_agent_permissions()` with mock HTTP responses (200 OK, 400 Bad Request, 403 Forbidden, 429 Rate Limit)
- Unit test: Zone 1/2/3 remediation logic (principal filtering, approved group transformation)
- Integration test: `-WhatIf` mode (no actual PATCH, log proposed changes)
- Integration test: Single-agent remediation (lab tenant, non-production agent)
- Integration test: Post-remediation validation (verify compliance after PATCH)

**Estimated complexity:** MEDIUM-HIGH (BAP API PATCH new, zone-specific logic complex, post-remediation validation adds steps)

### Plan 03-02: Approval Workflow Specification

**Scope:**
- Remediation approval workflow specification (ENF-03)
- Power Automate flow template (`src/asard-remediation-approval-workflow.json`)
- Adaptive card template for approval request (agent details, current sharing, proposed groups, zone context)
- Flow workflow: Query non-compliant agents → Start approval → On approval, invoke remediation → Update Dataverse → Teams notification

**Deliverables:**
- `src/asard-remediation-approval-workflow.json` — Power Automate Cloud Flow export
  - Trigger: Manual or scheduled (daily 09:00 UTC)
  - Query Dataverse: `fsi_agentsharingcompliances` (compliance_status=1, last_checked within 24h)
  - Approval connector: Start approval per agent (or batched)
  - HTTP action: Invoke remediation (BAP API PATCH or Azure Automation Runbook calling Python script)
  - Dataverse connector: Update compliance record (remediation_date, compliance_status, approval_status)
  - Teams connector: Post notification (approval result card)
- `src/adaptive-card-asard-remediation-approval.json` — Adaptive card template for approval request
  - Sections: Agent summary, zone, violation type, current sharing (list with icons), proposed changes (list with icons), impact summary, compliance metadata
  - Variables: agent_name, environment_name, zone, zone_name, violation_type, current_principals_list, proposed_principals_list, member_count, scan_run_id, last_checked
- Approval workflow documentation (deployment guide section)
  - Prerequisites: Approvals connector, Teams connection reference, environment variables (approval email)
  - Configuration: Approval timeout, approval email, Teams channel for notifications

**Wave assignment:** Wave 1 (depends on Plan 03-01 for remediation logic understanding, but can develop flow in parallel)

**Testing:**
- Manual flow execution (lab tenant, single non-compliant agent)
- Approval card rendering (Teams mobile + desktop)
- Approval decision handling (Approve → remediation invoked, Reject → logged)
- Dataverse update validation (remediation_date, approval_status)
- Teams notification delivery (success + rejection cards)

**Estimated complexity:** MEDIUM (Power Automate flow similar to UASD pattern, approval connector well-documented, adaptive card reuses ASARD alert template)

### Sequencing Rationale

**Parallel-eligible with coordination:**
- Plan 03-01 (remediation script) and Plan 03-02 (approval workflow) can be developed in parallel
- Plan 03-01 establishes remediation API contract (input: agent_id + env_id, output: success/failure)
- Plan 03-02 orchestrates approval and invokes Plan 03-01 remediation
- Integration point: Cloud Flow HTTP action to call Python script (via Azure Automation Runbook or HTTP-triggered Function — Phase 5 deployment concern)

**Sequencing for testing:**
- Plan 03-01 must be testable independently (CLI execution, `-WhatIf`, manual approval prompt)
- Plan 03-02 can reference Plan 03-01 remediation logic without blocking (approval workflow spec can describe integration, implementation deferred to Phase 5)

**Integration with Phase 4 (Exception Management):**
- Phase 4 will create exception tracking (time-bound exceptions, expiration)
- Remediation script (Plan 03-01) should check for active exceptions before applying changes (query `fsi_SharingException` table if exists, skip remediation if exception active)
- Approval workflow (Plan 03-02) should exclude agents with active exceptions from approval list

## Sources

**FSI-AgentGov codebase:**
- `.planning/ROADMAP.md` — Phase 3 requirements and success criteria
- `.planning/REQUIREMENTS.md` — ENF-01, ENF-02, ENF-03 detailed specifications
- `scripts/asard_zone_rules.py` — `get_approved_groups_for_zone()` function (Phase 1)
- `scripts/create_asard_dataverse_schema.py` — Dataverse table definitions (Phase 1)
- `scripts/bap_admin_client.py` — BAP Admin API client with GET operations (Phase 2)
- `scripts/detect_agent_sharing_violations.py` — Detection workflow writes compliance records (Phase 2)
- `src/uasd-remediation-apply-sharing-policy.json` — UASD remediation flow (BAP API PATCH pattern, lines 400-450)
- `src/uasd-exception-approval-workflow.json` — UASD approval workflow (Approvals connector pattern)
- `src/adaptive-card-asard-alert.json` — ASARD detection alert card (template for approval card)

**Microsoft documentation:**
- [Power Platform for Admins connector — Update bot permissions](https://learn.microsoft.com/en-us/connectors/powerplatformforadmins/#update-bot-permissions) — BAP API PATCH endpoint reference
- [Power Automate Approvals connector](https://learn.microsoft.com/en-us/connectors/approvals/) — Start approval action, response handling
- [Adaptive Cards Designer](https://adaptivecards.io/designer/) — Card schema and rendering

**FSI-AgentGov established patterns:**
- Python scripts as primary artifacts (Phase 1-2: schema, zone rules, detection)
- Power Automate flows for enterprise automation (UASD, CAA, timeout enforcement)
- `-WhatIf` / `--dry-run` mode for simulation (Phase 2 detection, Phase 3 remediation)
- Post-operation validation (ALCA v21 pattern: policy apply → validate → update Dataverse)
- Approval-first for destructive operations (UASD exception approval, ALCA policy exceptions)

**BAP Admin API PATCH Pattern (from UASD):**
```http
PATCH https://api.bap.microsoft.com/providers/Microsoft.BusinessAppPlatform/scopes/admin/environments/{envId}/bots/{botId}/permissions?api-version=2021-04-01
Content-Type: application/json

{
  "put": [
    {
      "properties": {
        "roleName": "CanView",
        "principal": {
          "id": "azure-ad-group-guid",
          "type": "Group",
          "displayName": "Finance Approved Viewers"
        }
      }
    }
  ]
}
```

**Key Insight:** The `"put"` property replaces all existing permissions (destructive). No incremental add/remove operations. Always full replacement.

---

*Research completed: 2026-02-13*  
*Researcher: copilot*  
*Confidence: HIGH — UASD provides clear BAP API PATCH pattern, Phase 1-2 artifacts ready for integration, approval workflow follows established Power Automate patterns*
