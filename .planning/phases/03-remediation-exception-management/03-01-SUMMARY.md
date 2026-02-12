---
phase: 3
plan: 1
status: complete
executed: 2026-02-12
---

# Summary 03-01: Remediation Flow + Exception Approval Flow

## Status: Complete

**Executed:** 2026-02-12
**Duration:** ~25 minutes
**Commit message:** `feat(uasd): add remediation and exception approval flows`

## Deliverables

| File | Lines | Action | Description |
|------|-------|--------|-------------|
| `src/uasd-remediation-apply-sharing-policy.json` | 1054 | CREATE | UASD remediation Power Automate flow definition |
| `src/uasd-exception-approval-workflow.json` | 798 | CREATE | UASD exception approval Power Automate flow definition |

## Requirements Delivered

| ID | Requirement | Status |
|----|-------------|--------|
| REM-01 | Remediation flow with Dataverse trigger, exception check, approval/auto paths, BAP PATCH | Done |
| REM-02 | Exception approval flow with sequential dual approval, 90-day expiration | Done |

## Acceptance Criteria

### Remediation Flow (`uasd-remediation-apply-sharing-policy.json`)

- [x] Valid JSON file parseable by `ConvertFrom-Json` / `json.load()`
- [x] Connection references: `fsi_cr_dataverse_sharingdetector`, `fsi_cr_teams_sharingdetector`, `fsi_cr_approvals_sharingdetector`
- [x] Dataverse webhook trigger on `fsi_sharingviolation` where `fsi_violation_status eq 0` (Open)
- [x] Exception check suppresses remediation for active, non-expired exceptions
- [x] Default mode is Approval for ALL zones (Non-Negotiable Rule #5)
- [x] Auto-remediation only for PUBLIC_INTERNET_LINK (violation_type=1) when `fsi_auto_remediate_public_link = true`
- [x] BAP PATCH overwrites principals with approved security groups per spec §3.3
- [x] Scope_Try/Scope_Catch error handling pattern (Scope_Catch runs on Failed/TimedOut)
- [x] Violation status updated after remediation (Remediated=1, Exception_Granted=2)
- [x] Teams notifications for automatic remediation, approval-based completion, rejection, exception found, and errors

### Exception Approval Flow (`uasd-exception-approval-workflow.json`)

- [x] Valid JSON file parseable by `ConvertFrom-Json` / `json.load()`
- [x] Dataverse trigger on `fsi_sharingexception` creation where `fsi_exception_status eq 0` (Pending)
- [x] Sequential dual approval: Security team → Data Owner
- [x] Exception denied if either approver rejects
- [x] Exception approved only when both approve
- [x] 90-day default expiration via `DefaultExceptionDays` variable
- [x] Violation status updated to Exception_Granted (2) on approval
- [x] Expiration scanner logic documented (runs in detector flow, not this flow)
- [x] Teams notifications for approval, Security denial, Data Owner denial, and errors

## Key Structural Elements

### Remediation Flow

| Element | Implementation |
|---------|---------------|
| **Trigger** | `OpenApiConnectionWebhook` on `fsi_sharingviolation` (message=4: Create+Update, scope=4: Organization) |
| **Variables** | 7 sequential: ViolationId, AgentId, EnvironmentId, ViolationType, RemediationMode ("Approval"), TeamsGroupId, TeamsChannelId |
| **Exception Check** | `ListRecords` on `fsi_sharingexceptions` with agent + violation type + status=Approved + not expired filter |
| **Auto-Remediation Gate** | Condition: ViolationType==1 AND `fsi_auto_remediate_public_link==true` from active sharing policy |
| **Mode Switch** | `Switch` on RemediationMode — "Automatic" case vs default "Approval" case |
| **BAP PATCH** | HTTP PATCH to `api.bap.microsoft.com/.../bots/{AgentId}/permissions` with MSI auth, body `{"put": [...principals]}` |
| **Approval** | `StartAndWaitForAnApproval` via `shared_approvals` connector |
| **Error Handling** | Scope_Catch with adaptive card error notification to Teams |

### Exception Approval Flow

| Element | Implementation |
|---------|---------------|
| **Trigger** | `OpenApiConnectionWebhook` on `fsi_sharingexception` (message=1: Create only, scope=4: Organization) |
| **Variables** | 5 sequential: ExceptionId, DefaultExceptionDays (90), ExpiresAt, TeamsGroupId, TeamsChannelId |
| **Expiration Compute** | `addDays(utcNow(), DefaultExceptionDays)` — stored in ExpiresAt variable |
| **Security Approval** | `StartAndWaitForAnApproval` — first gate, includes agent/violation/justification/classification details |
| **Data Owner Approval** | `StartAndWaitForAnApproval` — second gate, includes Security approval info |
| **Approval Logic** | Nested conditions: Security reject → Denied; Security approve → Data Owner; Data Owner reject → Denied; Both approve → Approved |
| **Status Updates** | Exception: Approved(1)/Denied(2); Violation: Exception_Granted(2) |
| **Expiration Scanner** | Documented in Scope_Try description — runs within detector flow on each scan cycle |
| **Error Handling** | Scope_Catch with adaptive card error notification to Teams |

### Connection References (Both Flows)

| Connector | Logical Name | Purpose |
|-----------|--------------|---------|
| `shared_commondataserviceforapps` | `fsi_cr_dataverse_sharingdetector` | Dataverse CRUD operations |
| `shared_teams` | `fsi_cr_teams_sharingdetector` | Teams channel notifications |
| `shared_approvals` | `fsi_cr_approvals_sharingdetector` | Approval workflow actions |

## Option Set Values Used

| Option Set | Values |
|------------|--------|
| `fsi_UASD_violationstatus` | Open=0, Remediated=1, Exception_Granted=2 |
| `fsi_UASD_exceptionstatus` | Pending=0, Approved=1, Denied=2 |
| `fsi_UASD_violationtype` | ORG_WIDE_SHARING=0, PUBLIC_INTERNET_LINK=1, UNAPPROVED_GROUP=2, EXCESSIVE_INDIVIDUAL=3, CROSS_TENANT_ACCESS=4 |

## Design Decisions

1. **Approvals connector added as third connection reference** — the plan specified "Same 2" connection references, but the `StartAndWaitForAnApproval` action requires a `shared_approvals` connection reference. Added `fsi_cr_approvals_sharingdetector` for functional correctness.

2. **Exception path uses condition nesting** — when an active exception is found, the True branch updates status and notifies; all remediation logic lives in the Else branch to prevent execution after exception grant.

3. **Security rejection terminates via nesting** — the Data Owner approval is inside the Security approval's True branch, so Security rejection naturally stops the flow without a Terminate action.

4. **Expiration scanner in detector flow** — per plan note, expiration scanning logic is documented as a comment in the exception flow's Scope_Try description rather than implemented as a separate scope. The detector flow handles expiration on each scan cycle.
