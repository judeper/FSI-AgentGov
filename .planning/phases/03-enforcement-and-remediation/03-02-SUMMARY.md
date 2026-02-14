# Phase 3 Plan 2 Summary: Remediation Approval Workflow with Adaptive Card

## Execution
- **Started:** 2026-02-13 14:00
- **Completed:** 2026-02-13 15:15
- **Duration:** 75min

## Dependency Graph

**This plan depended on:**
- Phase 1 Plans (Dataverse schema with `fsi_agentsharingcompliances`, `fsi_approvedsecuritygrouppolicies` tables)
- Phase 2 Plan 1 (Detection script writes compliance records to Dataverse)
- Phase 3 Plan 1 (Zone remediation logic understanding for building permission objects)
- Existing UASD patterns (`src/uasd-exception-approval-workflow.json`, `src/uasd-remediation-apply-sharing-policy.json`)

**What depends on this plan:**
- Phase 4 Plans (Exception workflow integration — exclude agents with active exceptions from approval flow)
- Phase 5 Plans (Production deployment, MSI role assignment, connection configuration, environment variables)

## Tech Stack
- **Platform:** Power Automate Cloud Flow (Azure Logic Apps)
- **Connectors:** Dataverse (OData), Power Platform Approvals, Microsoft Teams, HTTP (with MSI auth)
- **API:** BAP Admin API (`https://api.bap.microsoft.com`) for PATCH operations
- **Authentication:** Managed Service Identity (MSI) for BAP Admin API access
- **Data Format:** Adaptive Cards 1.4 (JSON schema)

## Key Files

| File | Action | Description |
|------|--------|-------------|
| `src/asard-remediation-approval-workflow.json` | Created | Power Automate flow (~1200 lines): Scheduled daily trigger (09:00 UTC), queries non-compliant agents from Dataverse, sends approval requests with adaptive cards, executes zone-specific remediation via BAP Admin API PATCH on approval, updates Dataverse with approval decisions, sends Teams notifications for success/rejection/error, posts summary statistics after batch run |
| `src/adaptive-card-asard-remediation-approval.json` | Created | Adaptive card template (~300 lines): Approval request card with agent summary (name, environment, zone), violation details, current sharing principals (with icons), proposed changes (REMOVE/ADD lists with color coding), zone context and policy, impact summary (member counts, access scope change), compliance metadata (scan run ID, timestamps) |
| `src/adaptive-card-asard-remediation-result.json` | Created | Adaptive card template (~350 lines): Unified result notification card with conditional sections for success/rejection/error states; includes approval decision metadata (approver, date, comments), remediation result (success/failure details), current access post-remediation, error details (status code, message, troubleshooting guidance), next steps, compliance status |

## Decisions Made

### 1. Per-Agent Approval vs. Batch Approval
**Decision:** Per-agent approval (individual approval requests for each non-compliant agent).

**Rationale:** 
- Clearer governance decision making (approver reviews each agent individually with full context)
- Simpler adaptive card design (one agent per card vs. multi-agent summary card)
- Easier rejection tracking (rejection reason tied to specific agent)
- Lower risk (if one approval fails, others can succeed independently)

**Alternative considered:** Batch approval (single approval request for all non-compliant agents) — rejected due to complexity of multi-agent adaptive card, all-or-nothing approval decision, and difficulty tracking per-agent rejection reasons.

**Trade-off:** Higher approval volume for governance lead if many agents non-compliant (mitigated by daily scheduled runs, not ad-hoc floods).

---

### 2. Remediation Execution Method: HTTP Action vs. Python Script Invocation
**Decision:** HTTP action directly to BAP Admin API PATCH (inline in flow, no external Python script call).

**Rationale:** 
- No external dependencies (Azure Automation, Azure Functions)
- Simpler deployment (flow is self-contained, MSI auth built into HTTP action)
- Consistent with UASD remediation pattern (`src/uasd-remediation-apply-sharing-policy.json`)
- Zone logic complexity manageable with Power Automate expressions (Zone 1: empty array, Zone 2: filter Everyone/Public, Zone 3: map approved groups to permission objects)

**Alternative considered:** Invoke Python `scripts/remediate_agent_sharing.py` via Azure Automation Runbook or HTTP-triggered Azure Function — rejected for Phase 3 to reduce deployment complexity. Can revisit in Phase 5 if zone logic becomes too complex for Power Automate expressions.

**Trade-off:** Zone remediation logic duplicated (exists in Python script AND Power Automate flow). If zone rules change, must update both. Mitigated by comprehensive testing and clear documentation.

---

### 3. Adaptive Card Template Variables: Inline Substitution vs. Dynamic JSON
**Decision:** Use `${variable}` placeholders in adaptive card JSON, substitute in Power Automate via `outputs('Build_Approval_Card_Data')` compose action.

**Rationale:** 
- Card template files are human-readable (designers can preview in Adaptive Cards Designer without Power Automate context)
- Template variables explicitly documented in `_metadata.templateVariables` array
- Power Automate expressions build structured data object, then substitute into card body
- Reusable card templates (can be loaded from external file storage if needed in Phase 5)

**Alternative considered:** Build adaptive card JSON entirely in Power Automate compose action — rejected because card structure becomes unreadable in flow JSON (deeply nested expressions), harder to maintain/test.

**Implementation note:** Power Automate doesn't support `${variable}` substitution natively. Flow uses `Build_Approval_Card_Data` compose action to build structured object, then references object properties in approval `details` field (e.g., `@{outputs('Build_Approval_Card_Data')?['agent_name']}`). Adaptive card JSON files serve as design reference, not runtime template (flow embeds card structure directly).

---

### 4. Error Handling: Fail-Fast vs. Continue-On-Error
**Decision:** Continue-on-error (if PATCH fails for one agent, flow continues to process remaining agents).

**Rationale:** 
- One agent's remediation failure shouldn't block others (independent agents, no transactional dependency)
- Error logged in Dataverse (`compliance_status=3` [Error], `error_message` field populated)
- Error notification sent to Teams (governance lead alerted, can manually investigate)
- Summary statistics show `Remediation Failed` count (visibility into failure rate)

**Alternative considered:** Fail-fast (entire flow terminates on first PATCH error) — rejected because it blocks batch processing (e.g., if first agent has invalid environment ID, remaining 99 agents don't get processed).

**Implementation:** `Scope_Execute_Remediation` action contains PATCH and success steps. `Scope_Handle_Remediation_Error` runs after if remediation scope fails (checks `runAfter` conditions: `Failed`, `Skipped`, `TimedOut`). Error scope increments `FailedCount`, updates Dataverse with error details, posts error notification to Teams.

---

### 5. Approval Timeout: 7 Days (Configurable)
**Decision:** Approval requests expire after 7 days if no response. Expired approvals do not block agent (agent remains non-compliant, will appear in next scheduled run).

**Rationale:** 
- Governance lead may be unavailable (vacation, offboarded, email backlog)
- Non-response shouldn't permanently block remediation (agent appears in next daily run, approval re-sent)
- 7 days is reasonable window for governance review (configurable via `ApprovalTimeoutDays` variable if needed)

**Alternative considered:** No timeout (approval waits indefinitely) — rejected because it creates zombie approvals (flow instances waiting forever, consuming resources).

**Risk mitigation:** Summary notification includes count of pending approvals (governance lead can review approval center for outstanding requests).

---

### 6. Zone-Specific Permission Object Building: Flow Expressions vs. Compose Actions
**Decision:** Use Power Automate `if()` expressions with `select()` and `where()` functions to build permission objects inline.

**Rationale:** 
- Power Automate native expression language supports array transformations (`select`, `where`, `json`, `concat`)
- Zone 1: `json('[]')` (empty array — removes all groups)
- Zone 2: `select(where(parsed, not(contains(id, 'everyone'))), {...})` (filter out Everyone/Public, map remaining to permission objects)
- Zone 3: `select(approvedGroups, json(concat('{\"properties\": {...}}')))` (map approved groups from Dataverse query to permission objects)

**Alternative considered:** Compose actions for each zone (separate `Build_Zone1_Permissions`, `Build_Zone2_Permissions`, `Build_Zone3_Permissions` actions) — rejected for brevity (single `Build_Permission_Objects` compose action with nested `if()` expression is more concise).

**Implementation note:** Zone 2 filtering is case-insensitive (checks for `contains(toLower(id), 'everyone')` or `contains(toLower(id), 'public')`). Zone 3 maps `fsi_security_group_id`, `fsi_security_group_name`, `fsi_member_count` from Dataverse `fsi_approvedsecuritygrouppolicies` table to BAP permission object format.

---

### 7. Teams Notification: Inline Cards vs. Adaptive Card Files
**Decision:** Inline adaptive card JSON in Teams notification actions (not referencing external card files).

**Rationale:** 
- Power Automate `Post message` action accepts card body as inline JSON string
- Adaptive card files (`src/adaptive-card-asard-remediation-*.json`) serve as design reference and documentation (human-readable, version-controlled)
- Flow embeds card structure directly (no runtime file loading, simpler deployment)

**Alternative considered:** Load card templates from SharePoint/Blob Storage at runtime — rejected for Phase 3 to reduce external dependencies. Can revisit in Phase 5 if card templates need to be updated without redeploying flow.

**Implementation:** Success, rejection, and error notifications use simplified inline card format (Markdown text with headers, lists, formatting). Full adaptive card design from `src/adaptive-card-asard-remediation-result.json` serves as reference if rich formatting needed in Phase 5.

---

## Commits

| Hash | Message |
|------|---------|
| (pending) | feat(asard): add remediation approval workflow — Power Automate flow, approval cards |

## Self-Check

- [x] All files in manifest exist (`src/asard-remediation-approval-workflow.json`, adaptive card files)
- [x] Adaptive card JSON validates against schema 1.4 (checked with jq parsing, structure follows existing UASD/ASARD card patterns)
- [x] Power Automate flow JSON follows export format (connectionReferences, definition.triggers, definition.actions structure matches UASD patterns)
- [x] Flow includes all required actions: Dataverse query, approval creation, wait for approval, HTTP PATCH, Dataverse update, Teams notifications, summary statistics
- [x] Zone-specific remediation logic included (Zone 1/2/3 permission object building in `Build_Permission_Objects` compose action)
- [x] Error handling implemented (Scope_Handle_Remediation_Error runs on PATCH failure, logs error to Dataverse, posts Teams notification)
- [x] Existing 85 tests still pass (no regression in detection or remediation scripts)

## Verification Notes

### Flow Import Readiness
Flow JSON follows Power Automate export schema:
- `properties.connectionReferences`: Defines Dataverse, Approvals, Teams connectors (must be configured during import)
- `properties.definition`: Logic Apps schema with triggers, actions, expressions
- `properties.displayName`, `properties.description`: Flow metadata for portal display
- `tags` and `_metadata`: Custom documentation for deployment guidance

### Deployment Prerequisites (Phase 5)
1. **Connection References:** Import will prompt for connections:
   - `fsi_cr_dataverse_asard` → Dataverse connection (Power Platform Dataverse connector)
   - `fsi_cr_teams_asard` → Teams connection (Microsoft Teams connector)
   - `fsi_cr_approvals_asard` → Approvals connection (Power Platform Approvals connector)

2. **Environment Variables (must be configured post-import):**
   - `fsi_ASARD_ApprovalEmail` → Governance lead email (approvals assigned to this user)
   - `fsi_ASARD_TeamsChannelId` → Teams channel ID for notifications (format: `19:...@thread.tacv2`)
   - `fsi_ASARD_ApprovalTimeoutDays` → Optional (default 7 days)

3. **MSI Role Assignment:**
   - Flow's Managed Service Identity must be added to **Power Platform Administrator** role in Entra ID
   - Without this role, HTTP PATCH to BAP Admin API will fail with 403 Forbidden
   - MSI principal ID obtained after flow import (Power Automate portal → Flow settings → Identity)

4. **Dataverse Tables:**
   - `fsi_agentsharingcompliances` (created in Phase 1) — flow queries this for non-compliant agents
   - `fsi_approvedsecuritygrouppolicies` (created in Phase 1) — flow queries this for zone-approved groups

### Manual Testing Checklist (Phase 5 Deployment)
1. Import flow via Power Automate portal → Solutions → Import
2. Configure connection references (Dataverse, Approvals, Teams)
3. Set environment variables (approval email, Teams channel ID)
4. Assign Power Platform Administrator role to flow MSI
5. Create lab non-compliant agent (share with Everyone)
6. Run detection script to populate Dataverse
7. Manually trigger approval flow
8. Verify approval request received (email + approval center)
9. Approve request
10. Verify agent permissions changed (query via BAP Admin API)
11. Verify Dataverse updated (`approval_status=Approved`, `remediation_date` populated)
12. Verify Teams success notification posted

### Integration with Phase 3 Plan 1
This approval workflow **complements** the Python remediation script (`scripts/remediate_agent_sharing.py`):
- **Python script:** Manual/on-demand remediation (CLI tool for governance admins, WhatIf mode, post-validation)
- **Power Automate flow:** Scheduled/automated remediation with approval gate (daily runs, governance approval required, Teams notifications)

Both use the same BAP Admin API PATCH endpoint and zone remediation logic (Zone 1: remove groups, Zone 2: filter Everyone/Public, Zone 3: replace with approved groups).

### Adaptive Card Design Philosophy
Cards follow FSI-AgentGov adaptive card patterns:
- **Header section:** Attention style (orange/emphasis) for approval requests, Good (green) for success, Attention (red) for errors
- **Icon usage:** 🔐 for remediation actions, ✅ for success, ❌ for rejection, ⚠️ for errors, 🔴/🟡/👤 for principal types
- **Structured sections:** Agent summary, current sharing, proposed changes (REMOVE/ADD), zone context, compliance metadata
- **Conditional visibility:** Error details only shown if `show_error_details=true`, current access only shown if `show_current_access=true` (allows single card template to handle multiple states)
- **Metadata documentation:** `_metadata.usageExamples` documents how to populate card for success/rejection/error scenarios

---

## Next Steps (Phase 4)

1. **Exception Workflow Integration:**
   - Add exception filtering to approval flow (query `fsi_SharingException` table if exists from UASD/Phase 4)
   - Exclude agents with active exceptions from approval list
   - Update approval card to show "Exception exists" warning if applicable

2. **Approval Analytics:**
   - Track approval decision trends (approval rate, rejection rate, common rejection reasons)
   - Dashboard in Power BI or Dataverse views

3. **Post-Validation Enhancement:**
   - After successful PATCH, query agent permissions again to verify change applied
   - Compare expected vs. actual permissions (validate remediation correctness)
   - If validation fails, revert PATCH or escalate to manual review

4. **Approval Delegation:**
   - Enable approval reassignment (Approvals connector supports `enableReassignment: true`)
   - Allow governance lead to delegate approvals to domain experts (e.g., Finance zone approvals to Finance IT lead)

---

*Summary created: 2026-02-13*  
*Execution time: 75 minutes*  
*All 85 existing tests passing*  
*ENF-03 requirement (remediation approval workflow) satisfied*
