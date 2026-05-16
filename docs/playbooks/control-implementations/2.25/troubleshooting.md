# Control 2.25 — Microsoft Agent 365 Admin Center Governance Console: Troubleshooting Playbook

**Companion to:** [Control 2.25 — Agent 365 Admin Center Governance Console](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md)
**Sibling playbooks:** [Portal Walkthrough](./portal-walkthrough.md) · [PowerShell Setup](./powershell-setup.md) · [Verification & Testing](./verification-testing.md)
**Audience:** AI Administrator, Entra Global Reader, AI Governance Lead, Purview Compliance Admin, Power Platform Admin, IR on-call.
**Scope:** Diagnose and remediate failures in the Microsoft Agent 365 Admin Center (GA May 1, 2026), Default and Custom Governance Templates, admin-gated approval workflows, agent publish/deploy actions, inventory export, Researcher with Computer Use configuration, and sovereign-cloud parity gaps. Aligns with FINRA Rule 3110 supervisory tooling expectations, SEC Rule 17a-4 evidence preservation, SOX ITGC change-control proof, GLBA Safeguards Rule §314.4(c)(1) access enforcement, OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12) / Fed SR 26-2 (formerly SR 11-7) model risk oversight, and CFTC Reg 1.31 retention.

> **Regulatory framing.** This playbook describes diagnostic and remediation procedures that **support compliance with** the cited regulations. The Agent 365 Admin Center provides supervisory tooling; it does **not** substitute for the registered-principal supervisory obligations under FINRA Rule 3110. Organizations should verify each procedure in a non-production tenant before production execution, and engage Legal / Compliance before altering any governance template or approval workflow that has produced examiner-reviewable evidence.

> **Sovereign-cloud caveat.** Microsoft Agent 365 Admin Center, Default Governance Template, Custom Governance Templates, and admin-gated approval workflows are **not at parity** in GCC, GCC High, or DoD as of April 2026. Sovereign-tenant operators must use the compensating-control runbook in §10 (`PILLAR-SOV-PARITY-GAP`) and document the parity gap in the tenant Risk Register before relying on any procedure in this playbook. See [PowerShell baseline · §3 Sovereign Cloud Endpoints](../../_shared/powershell-baseline.md#3-sovereign-cloud-endpoints-gcc-gcc-high-dod).

---

## §0 Triage Tree

Use this section as the entry point for every Sev1/Sev2/Sev3 incident touching Control 2.25. The triage tree maps observed symptoms to one of nine diagnostic pillars (§2–§10) or one of seven situational runbooks (§11–§17). Severity is determined by the matrix below and drives examiner-artifact preservation requirements.

### §0.1 Symptom → Pillar Map

| Observed symptom | First-look pillar | Secondary pillar |
|---|---|---|
| Admin Center landing page fails to render, blank tile, "We can''t load this view" | §2 CONSOLE-NOT-LOADING | §5 TEMPLATE-APPLY-FAIL |
| Pending-approval queue static for >4 business hours, new requests not appearing | §3 APPROVAL-QUEUE-STALE | §2 CONSOLE-NOT-LOADING |
| Console shows orphaned/ownerless agents, but Agent Registry (Control 1.2) does not | §4 OWNERLESS-AGENTS-MISMATCH | §3 APPROVAL-QUEUE-STALE |

| Default or Custom Governance Template "Apply" returns error or partial success | §5 TEMPLATE-APPLY-FAIL | §6 PUBLISH-WIZARD-FAIL |
| Agent Publish wizard cannot save draft, validation errors on required fields | §6 PUBLISH-WIZARD-FAIL | §5 TEMPLATE-APPLY-FAIL |
| Deploy / Reassign / Disable bulk action fails for one or more agents | §7 DEPLOY-ACTION-FAIL | §4 OWNERLESS-AGENTS-MISMATCH |
| Inventory export (CSV / JSON / Graph) returns truncated rows or missing columns | §8 INVENTORY-EXPORT-INCOMPLETE | §4 OWNERLESS-AGENTS-MISMATCH |
| Researcher with Computer Use suddenly available to users not in approved group | §9 RESEARCHER-CONFIG-DRIFT | §5 TEMPLATE-APPLY-FAIL |
| Sovereign tenant (GCC / GCC High / DoD) cannot access Admin Center features | §10 SOV-PARITY-GAP | (compensating-control activation) |
| Multiple symptoms above, post-acquisition or post-reorg | §11 RB-01 (mass re-onboarding) | applicable pillar |
| Examiner request received and queue is stale | §12 RB-02 (examiner pull) | §3 APPROVAL-QUEUE-STALE |

### §0.2 Severity Matrix

| Severity | Trigger | Response SLA | Examiner-artifact preservation |
|---|---|---|---|
| **Sev1** | Console fully unavailable, OR approval queue stale during examiner-active window, OR Researcher Computer Use enabled for non-approved population | Engage on-call within 15 min; AI Governance Lead within 30 min | **Mandatory before remediation:** snapshot per §1.5 (E-01..E-09) |
| **Sev2** | Single pillar degraded; partial functionality; affects Zone 3 agents | 2 business hours | Snapshot per §1.5 if Zone 3 affected |
| **Sev3** | Single agent / single template affected; Zone 1 or Zone 2; no examiner exposure | Next business day | Optional; document in change log |

### §0.3 Pre-Escalation Checklist

Before paging the AI Governance Lead or Entra Global Admin (PIM-elevated), the on-call AI Administrator must complete:

1. Confirm GA status: tenant is on Microsoft Agent 365 Admin Center GA build (≥ May 1, 2026). Pre-GA preview tenants follow a different support path; see §2.4.
2. Confirm reporter''s license posture: M365 E7 "Frontier Suite" OR standalone Agent 365 + Copilot prerequisite (`Get-Agt225LicenseAssignment -UserPrincipalName <upn>`).
3. Confirm reporter''s role: AI Administrator, Entra Global Reader, AI Governance Lead, or other role per [Role Catalog](../../../reference/role-catalog.md). PIM activation timestamp captured.
4. Capture initial evidence floor (E-01 console screenshot, E-02 Graph activity log, E-03 PowerShell session transcript). See §1.5.
5. Identify affected zone(s): Zone 1 Personal, Zone 2 Team, Zone 3 Enterprise. Zone 3 escalations require Compliance Officer notification within 1 hour.
6. Determine examiner-active status (FINRA / SEC / OCC / Fed exam in flight). If yes, escalate immediately and **do not** mutate state until Legal acknowledges.

### §0.4 Examiner-Artifact Preservation (SEC 17a-4 / CFTC 1.31)

Any remediation that mutates console state (template re-apply, approval queue replay, owner reassignment, license change) must be preceded by an evidence snapshot meeting SEC Rule 17a-4(f) WORM-equivalent retention and CFTC Regulation 1.31 record-keeping. The snapshot bundle is enumerated in §1.5 (E-01 through E-09) and is delivered to the Purview-configured immutable evidence library (`AgentGov-Evidence-225`).

> **Hedged language reminder.** Snapshots **support** the regulated firm''s ability to reconstruct the supervisory state at a point in time; they do not by themselves satisfy retention obligations. The retention SLA depends on the firm''s configured Purview retention label and immutability policy. Verify with the Purview Compliance Admin before relying on the snapshot for examiner production.

---
## §1 Diagnostic Data Collection

This section catalogs the helper cmdlets, Graph queries, and KQL queries used throughout §2–§17. All examples assume PowerShell 7.4 Core and the helper module loaded per [PowerShell Setup §2](./powershell-setup.md).

```powershell
#Requires -Version 7.4
#Requires -Modules Microsoft.Graph.Authentication, Microsoft.Graph.Users, Microsoft.Graph.Identity.Governance
```

### §1.1 `Get-Agt225*` Helper Catalog

| Cmdlet | Purpose | Source |
|---|---|---|
| `Get-Agt225Health` | End-to-end health probe of console + Graph + template service endpoints | [PowerShell Setup §4.1](./powershell-setup.md) |
| `Get-Agt225Agent` | Returns single agent record from console-backing store, including ownership chain and template binding | [PowerShell Setup §4.2](./powershell-setup.md) |
| `Get-Agt225PendingRequests` | Returns approval-queue snapshot with age, requester, governance-template id | [PowerShell Setup §4.3](./powershell-setup.md) |
| `Get-Agt225TemplateStatus` | Returns Default / Custom Governance Template apply state per agent or per scope | [PowerShell Setup §4.4](./powershell-setup.md) |
| `Get-Agt225InventoryExport` | Streams console inventory in CSV / JSON; pagination-safe fallback for failed UI export | [PowerShell Setup §3](./powershell-setup.md) |
| `Get-Agt225ResearcherConfig` | Returns Researcher with Computer Use enablement scope, group bindings, and license check | [PowerShell Setup §4.5](./powershell-setup.md) |
| `Get-Agt225LicenseAssignment` | Returns Frontier Suite / Agent 365 / Copilot license posture for a user or group | [PowerShell Setup §4.6](./powershell-setup.md) |
| `Get-Agt225AuditEvents` | Wrapper over Purview Audit unified log filtered to Agent365AdminCenter workload | [PowerShell Setup §4.7](./powershell-setup.md) |
| `Invoke-Agt225EvidenceSnapshot` | Produces the E-01..E-09 evidence bundle to the Purview immutable library | [PowerShell Setup §5](./powershell-setup.md) |

### §1.2 Graph Query Catalog (GQ-01..GQ-08)

All Graph queries target the `/beta/admin/agent365` namespace as published in the Microsoft Graph documentation for the Agent 365 GA release. Replace `{tenantId}` and `{agentId}` placeholders.

**GQ-01 — Console health probe**
```http
GET https://graph.microsoft.com/beta/admin/agent365/serviceStatus
```
Expected `200 OK` with `state: "operational"`. Anything else → §2.

**GQ-02 — Pending approval requests (queue snapshot)**
```http
GET https://graph.microsoft.com/beta/admin/agent365/governance/pendingRequests?$filter=status eq ''pending''&$top=999
```

**GQ-03 — Single agent record**
```http
GET https://graph.microsoft.com/beta/admin/agent365/agents/{agentId}?$expand=owners,governanceTemplate,licenseBinding
```

**GQ-04 — Default Governance Template state for tenant**
```http
GET https://graph.microsoft.com/beta/admin/agent365/governance/templates/default
```

**GQ-05 — Custom Governance Template enumeration**
```http
GET https://graph.microsoft.com/beta/admin/agent365/governance/templates?$filter=type eq ''custom''
```

**GQ-06 — Researcher with Computer Use scope**
```http
GET https://graph.microsoft.com/beta/admin/agent365/features/researcherComputerUse
```
Returns `enabledFor` (`all` | `group` | `none`) and bound group ids. Default-on for Copilot tenants per the October 2025 GA — FSI tenants must scope to a group or set `none` and document the affirmative restrictive decision in the Risk Register.

**GQ-07 — Bulk action audit (last 24h)**
```http
GET https://graph.microsoft.com/beta/admin/agent365/auditEvents?$filter=createdDateTime ge {iso8601-24h-ago} and category eq ''bulkAction''
```

**GQ-08 — Inventory export job status**
```http
GET https://graph.microsoft.com/beta/admin/agent365/exportJobs/{jobId}
```

### §1.3 KQL Catalog (KQL-01..KQL-05)

Run in Microsoft Sentinel or the Purview Audit advanced-search experience, depending on the firm''s SIEM landing.

**KQL-01 — Console availability over 24h**
```kusto
AgentGovActivity
| where TimeGenerated > ago(24h)
| where Workload == "Agent365AdminCenter"
| where OperationName in ("Console.Load", "Console.LoadFailed")
| summarize Loads=countif(OperationName=="Console.Load"),
            Failures=countif(OperationName=="Console.LoadFailed"),
            FailureRate = round(100.0 * countif(OperationName=="Console.LoadFailed") / count(), 2)
            by bin(TimeGenerated, 1h)
| order by TimeGenerated desc
```

**KQL-02 — Approval queue ingestion lag**
```kusto
AgentGovActivity
| where TimeGenerated > ago(7d)
| where OperationName == "ApprovalRequest.Created"
| extend QueueIngestionLagSec = datetime_diff(''second'', QueueAppearedAt, RequestCreatedAt)
| summarize p50=percentile(QueueIngestionLagSec,50),
            p95=percentile(QueueIngestionLagSec,95),
            p99=percentile(QueueIngestionLagSec,99)
            by bin(TimeGenerated, 1d)
```
Sustained p95 > 600 s indicates §3 APPROVAL-QUEUE-STALE.

**KQL-03 — Template apply failures**
```kusto
AgentGovActivity
| where Workload == "Agent365AdminCenter"
| where OperationName == "GovernanceTemplate.Apply"
| where ResultStatus != "Success"
| project TimeGenerated, ActorUPN, AgentId, TemplateId, TemplateType, FailureReason, CorrelationId
| order by TimeGenerated desc
```

**KQL-04 — Researcher Computer Use scope changes**
```kusto
AgentGovActivity
| where OperationName == "Feature.ResearcherComputerUse.ScopeChanged"
| project TimeGenerated, ActorUPN, OldScope, NewScope, BoundGroupIds, JustificationText, CorrelationId
| order by TimeGenerated desc
```

**KQL-05 — Bulk-action failure rate by action type**
```kusto
AgentGovActivity
| where TimeGenerated > ago(7d)
| where OperationName startswith "BulkAction."
| summarize Total=count(), Failed=countif(ResultStatus!="Success")
            by ActionType=tostring(split(OperationName,".")[1])
| extend FailureRatePct = round(100.0 * Failed / Total, 2)
| order by FailureRatePct desc
```

### §1.4 Sovereign-Cloud Endpoint Substitution

For GCC, GCC High, and DoD tenants, replace `graph.microsoft.com` with the appropriate sovereign endpoint per [PowerShell baseline · §3](../../_shared/powershell-baseline.md#3-sovereign-cloud-endpoints-gcc-gcc-high-dod). **Note:** the `/beta/admin/agent365` namespace is not at parity in sovereign clouds as of April 2026; queries will return `404 Not Found` or `403 Forbidden`. Use the compensating-control runbook in §10.

### §1.5 Evidence Floor (E-01..E-09)

Every Sev1 and every Zone-3 Sev2 incident must produce the following bundle via `Invoke-Agt225EvidenceSnapshot -IncidentId <id> -Destination AgentGov-Evidence-225`:

| Artifact | Description | Source | Retention target |
|---|---|---|---|
| **E-01** | Console screenshot at incident time (full viewport, timestamp visible) | Browser / on-call | 7 yr (SEC 17a-4) |
| **E-02** | Graph activity log for last 24h scoped to incident agent / template | GQ-07 | 7 yr |
| **E-03** | PowerShell session transcript (Start-Transcript) | On-call workstation | 7 yr |
| **E-04** | Approval queue snapshot at incident time | GQ-02 | 7 yr |
| **E-05** | Affected agent record(s) | GQ-03 per agent | 7 yr |
| **E-06** | Template state snapshot | GQ-04 / GQ-05 | 7 yr |
| **E-07** | License-posture snapshot of affected actors | `Get-Agt225LicenseAssignment` | 7 yr |
| **E-08** | Purview Audit unified-log export for the incident window | `Get-Agt225AuditEvents` | 7 yr (CFTC 1.31) |
| **E-09** | Incident commander attestation (signed by AI Governance Lead at recovery close) | §X recovery | 7 yr |

The snapshot is written with a Purview retention label that **supports** SEC Rule 17a-4(f) WORM-equivalent immutability when the Purview Compliance Admin has correctly configured the immutability policy. Verify policy state via `Get-RetentionCompliancePolicy -Identity "AgentGov-Evidence-225"` (Exchange Online Admin or Purview Compliance Admin role required).

---
## §2 Pillar: CONSOLE-NOT-LOADING

The Microsoft Agent 365 Admin Center landing page fails to render, returns "We can''t load this view," or hangs at the loading skeleton. This pillar covers license/role gaps, GA-vs-pre-GA build mismatches, browser-side cache poisoning, and downstream Graph service degradation.

### §2.1 Symptom Catalog

| Code | Symptom | Severity hint |
|---|---|---|
| **P2-S1** | Landing tile shows error banner "We can''t load this view. Please try again." | Sev2 |
| **P2-S2** | Page renders skeleton indefinitely; no error banner; network tab shows 401 / 403 from `/admin/agent365/serviceStatus` | Sev2 |
| **P2-S3** | Page renders but all sub-blades (Approvals, Templates, Inventory, Researcher) are empty with "Loading…" spinner | Sev2 |
| **P2-S4** | Page renders for some admins but not others, despite identical role assignments | Sev3 |
| **P2-S5** | Page redirects back to admin.microsoft.com root with no error | Sev3 |
| **P2-S6** | Console returns HTTP 503 from the fabric edge | Sev1 (Microsoft service incident likely) |

### §2.2 Root Cause Matrix

| Code | Root cause | Confirmation signal |
|---|---|---|
| **RC-A** | Admin lacks AI Administrator or AI Governance Lead role; PIM activation lapsed | GQ-01 returns 401 / 403; Entra sign-in log shows missing role token claim |
| **RC-B** | Tenant on pre-GA preview build; flighting flag dropped after GA cut-over | GQ-01 returns 200 but `state: "preview-deprecated"`; banner present in admin.microsoft.com |
| **RC-C** | Frontier Suite or Agent 365 SKU not assigned to tenant; license expired | `Get-Agt225LicenseAssignment -TenantScope` returns `licenseState: "expired"` or `"none"` |
| **RC-D** | Browser-side cache holds stale pre-GA bundle; service worker not refreshed | Hard reload (Ctrl-F5) restores function; problem returns next session |
| **RC-E** | Conditional Access policy blocks the admin.microsoft.com → graph.microsoft.com token exchange (e.g., new device-compliance grant control) | Entra sign-in log shows `Failure reason: 53003 - Blocked by Conditional Access` |
| **RC-F** | Microsoft service incident affecting the Agent 365 Admin Center fabric | Service Health Dashboard shows active advisory; KQL-01 shows tenant-wide failure spike |

### §2.3 Diagnostic Steps

1. Run `Get-Agt225Health -Verbose`. Inspect `ServiceStatus`, `GraphReachability`, `LicensePosture`, `RolePosture` blocks.
2. Issue **GQ-01**. Capture HTTP status and response body. 401/403 → RC-A or RC-E. 503 → RC-F. 200 with `state != "operational"` → RC-B.
3. Run `Get-Agt225LicenseAssignment -TenantScope` and confirm Frontier Suite or Agent 365 SKU is in `enabled` state with seats available.
4. Confirm reporter''s role bindings: `Get-MgUserMemberOf -UserId <upn>` and cross-check against [Role Catalog](../../../reference/role-catalog.md). For PIM-eligible roles, confirm activation timestamp via `Get-MgPrivilegedAccessRoleAssignmentScheduleInstance`.
5. Inspect Entra sign-in log for the affected admin in the past 1 hour: `Get-MgAuditLogSignIn -Filter "userPrincipalName eq ''<upn>''" -Top 25`. Look for `errorCode 53003`, `500011`, or `50105`.
6. If RC-D suspected, ask reporter to (a) hard-reload, (b) clear site data for `admin.microsoft.com` and `*.cloud.microsoft`, (c) re-test in InPrivate / new profile.
7. Review Service Health Dashboard for advisories tagged `Agent365` or `Copilot Admin`. RC-F is non-actionable from the tenant — escalate to Microsoft Support and document.

### §2.4 Pre-GA vs GA Build Detection

Tenants enrolled in the pre-GA preview (Sept 2025 – April 2026) used a flighting flag (`Agt365.Console.PreviewBuild`) that was deprecated on the May 1, 2026 GA cutover. Symptoms include phantom blades that no longer exist in GA and missing Custom Governance Template editor.

```powershell
$buildInfo = Get-Agt225Health -Verbose | Select-Object -ExpandProperty ConsoleBuildInfo
if ($buildInfo.Channel -ne ''GA'') {
    Write-Output "Tenant on non-GA channel: $($buildInfo.Channel). Engage Microsoft FastTrack to graduate the tenant."
}
```

If the tenant is stuck on `preview-deprecated`, open a Microsoft 365 service request citing the GA cutover; do **not** attempt to roll back the Entra application service principals (this will break the GA console).

### §2.5 Resolution Steps

| Root cause | Resolution |
|---|---|
| RC-A | Re-activate PIM role; if eligible-only without active assignment, request activation justification per Privileged Access Workflow. Document in change log. |
| RC-B | File Microsoft service request to graduate tenant to GA channel. **Do not** attempt local workarounds. |
| RC-C | Coordinate with Procurement to remediate license; until remediated, sovereign-style compensating controls (§10) apply. |
| RC-D | Instruct reporter to clear site data; if recurring, file an internal IT ticket to investigate browser policy preventing cache refresh. |
| RC-E | Coordinate with Identity team to evaluate the blocking Conditional Access policy. Common cause is a new device-compliance grant control rolled out without admin-workstation exemption. |
| RC-F | Wait on Microsoft mitigation; activate §10 compensating-control posture if examiner-active or Sev1. |

### §2.6 Verification

After remediation, confirm:

1. `Get-Agt225Health -Verbose` returns `Overall: Healthy` for all four blocks.
2. Reporter can load the Admin Center landing page and all four sub-blades within 60 s.
3. Pester test `TRG-225-01` (Console Load Smoke) passes (`Invoke-Pester -Path ./tests/trg-225-01.tests.ps1`). See [Verification & Testing §2](./verification-testing.md).
4. Evidence snapshot E-01..E-08 captured to `AgentGov-Evidence-225` if Sev1 or Zone-3 Sev2.

### §2.7 Cross-References

- [Portal Walkthrough §1 — First-time console activation](./portal-walkthrough.md)
- [Verification & Testing §2 — Console availability tests](./verification-testing.md)
- [Control 1.2 — Agent Registry](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md) (registry serves as fallback inventory when console unavailable)

---

## §3 Pillar: APPROVAL-QUEUE-STALE

The admin-gated approval queue (Default Governance Template "Approve Before Publish" gate, or Custom Template equivalents) shows no new arrivals for >4 business hours, or queue depth grows without admin action. This is a Sev1 if examiner-active, Sev2 otherwise — a stale queue means agent publish requests are blocked, which surfaces as user-reported "I can''t publish my agent" tickets to the help desk.

### §3.1 Symptom Catalog

| Code | Symptom | Severity hint |
|---|---|---|
| **P3-S1** | Queue depth ≥ 50 with oldest item > 8 business hours; no recent approvals | Sev1 if examiner-active, else Sev2 |
| **P3-S2** | New publish requests submitted by users do not appear in queue within 10 min | Sev2 |
| **P3-S3** | Approval action ("Approve" / "Reject") returns success in UI but agent publish state does not change | Sev2 |
| **P3-S4** | Queue shows duplicate entries for the same publish request | Sev3 |
| **P3-S5** | Queue filter by "Zone 3" returns empty when Zone 3 publish requests are known to exist | Sev2 |
| **P3-S6** | Approval-action audit event is missing from Purview unified log | Sev1 (audit gap) |

### §3.2 Root Cause Matrix

| Code | Root cause | Confirmation signal |
|---|---|---|
| **RC-A** | Approval-queue ingestion service degraded (Microsoft-side) | KQL-02 shows tenant-wide p95 lag spike; Service Health advisory present |
| **RC-B** | AI Governance Lead or designated approver lacks the `Agent365.Approval.Process` permission (regression after a recent role change) | GQ-02 succeeds for Global Reader but UI shows queue empty for approver |
| **RC-C** | Governance template prerequisite missing — e.g., the Default Template''s required Purview AI Compliance Assessment policy was deleted or disabled | GQ-04 returns `prerequisiteState: "incomplete"`; KQL-03 shows correlated `GovernanceTemplate.Apply` failures |
| **RC-D** | Custom Governance Template references an Entra Access Package that has been retired; new requests stall at the access-package gate | GQ-05 shows `accessPackageBindingState: "broken"` for the affected template |
| **RC-E** | Approval-action token-exchange failure due to Conditional Access (CA evaluates the approver''s session during the action and blocks) | Entra sign-in log shows interrupt during approval action |
| **RC-F** | Audit-pipeline outage (Purview side); queue functions, but examiner-grade evidence is not being recorded → P3-S6 | Purview Service Health advisory; `Get-Agt225AuditEvents` returns empty for known approvals |

### §3.3 Diagnostic Steps

1. Capture queue snapshot: `$snap = Get-Agt225PendingRequests -IncludeAge`. Compute p95 age and queue depth.
2. Run KQL-02 for last 7 days. Compare today''s p95 ingestion lag to baseline. Sustained > 600 s → RC-A or RC-D.
3. For each affected approver, run `Get-MgUserMemberOf -UserId <upn>` and confirm the `AI Governance Lead` directory role and any custom approval-permission group bindings are present.
4. Issue **GQ-04** and inspect `prerequisiteState`. If `incomplete`, the Default Template''s downstream policies need re-validation — see §5 PILLAR-TEMPLATE-APPLY-FAIL for re-apply procedure.
5. Issue **GQ-05** for each Custom Template in use. Inspect `accessPackageBindingState`. `broken` → RC-D, see resolution table.
6. For RC-F suspicion: pick three approvals known to have completed in the past 24h, confirm they are queryable via `Get-Agt225AuditEvents -StartTime (Get-Date).AddDays(-1) -OperationName "ApprovalRequest.Approved"`. Missing → escalate to Purview Compliance Admin, freeze any examiner-facing evidence claims until pipeline restored.
7. Inspect Entra sign-in log for affected approver during the failed action window.

### §3.4 FINRA 3110 Caveat (Critical)

The Agent 365 approval queue **supports** FINRA Rule 3110 supervisory review by surfacing publish events for review and recording the approver''s decision. It does **not** substitute for the registered-principal''s independent supervisory judgment. A stale queue does not relieve the registered principal of the supervisory obligation — manual review and out-of-band approval (documented in the change log) must continue during the outage. Coordinate immediately with the Compliance Officer and document the manual-review fallback in the incident record.

### §3.5 Resolution Steps

| Root cause | Resolution |
|---|---|
| RC-A | Wait on Microsoft mitigation; activate manual-review fallback per §3.4. Snapshot E-04 every 30 min until resolved. |
| RC-B | Reinstate approver permission via PIM; for permanent regression, file Identity-team ticket to investigate role-assignment drift. |
| RC-C | Re-establish missing prerequisite policy in Purview (`New-ProtectionAlert` / `Set-AIComplianceAssessment`), then re-apply Default Template per §5.5. |
| RC-D | Rebuild the Entra Access Package or rebind the Custom Template to the replacement package. Pending requests will not auto-replay — they must be re-submitted by users; communicate via published change record. |
| RC-E | Coordinate with Identity team to add an approver-action exemption to the blocking CA policy (or use admin-workstation grant). Document in change log. |
| RC-F | Engage Purview Compliance Admin and Microsoft Support; freeze examiner production until audit pipeline confirmed healthy and back-fill complete. |

### §3.6 Verification

1. `Get-Agt225PendingRequests -IncludeAge` returns p95 age < 4 business hours and depth < pre-incident baseline.
2. KQL-02 returns p95 ingestion lag < 120 s for the most recent 1 h bin.
3. Three test publish requests submitted by a test user appear in the queue within 60 s and can be approved with audit-log confirmation.
4. Pester `TRG-225-02` (Approval Queue Round-Trip) passes.
5. Evidence E-04, E-08 captured for the incident window.

### §3.7 Cross-References

- [Portal Walkthrough §3 — Approval queue operations](./portal-walkthrough.md)
- [Verification & Testing §3 — Approval round-trip tests](./verification-testing.md)
- [Control 1.2 — Agent Registry](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md)

---
## §4 Pillar: OWNERLESS-AGENTS-MISMATCH

The Agent 365 Admin Center shows a different ownerless / orphaned-agent count than the Agent Registry (Control 1.2) or the Orphaned Agent Detection control (Control 3.6). Mismatches have direct examiner-evidence consequences: the firm cannot present a single authoritative ownerless inventory, which weakens any FINRA 3110 or SOX ITGC narrative.

### §4.1 Symptom Catalog

| Code | Symptom | Severity hint |
|---|---|---|
| **P4-S1** | Console "Ownerless Agents" tile shows N; Agent Registry export shows M; N ≠ M | Sev2 |
| **P4-S2** | Console shows agent as "Ownerless" but Registry shows valid owner | Sev2 |
| **P4-S3** | Registry shows agent as ownerless but Console shows valid owner | Sev2 |
| **P4-S4** | Console ownerless count grows steadily over multiple days without reorg activity | Sev2 |
| **P4-S5** | Console identifies the AI Administrator service principal as "owner" of agents whose human owner has been offboarded | Sev3 |
| **P4-S6** | Console "Reassign Owner" bulk action succeeds but ownership reverts within 24h | Sev1 (state-mutation loop) |

### §4.2 Root Cause Matrix

| Code | Root cause | Confirmation signal |
|---|---|---|
| **RC-A** | Reconciliation cadence mismatch: Console reads from Graph at near-real-time; Registry reconciles on a 6-hour cadence | Mismatch resolves on next Registry reconcile cycle; KQL-05 shows no anomalies |
| **RC-B** | Offboarded user''s Entra account in soft-deleted state; Console resolves owner ID to a tombstone, Registry resolves to the soft-deleted user record | `Get-MgDirectoryDeletedItem -DirectoryObjectId <ownerId>` returns object |
| **RC-C** | Agent created via API/SDK with `owner` field unset; Console infers ownership from creator service principal, Registry leaves null | GQ-03 returns `owners: [{type:"servicePrincipal", id:"..."}]` while Registry shows `owners: []` |
| **RC-D** | Group-based ownership: Console expands group, Registry stores group reference | GQ-03 shows expanded user list; Registry export shows single group entry |
| **RC-E** | Reassignment loop: a downstream automation (e.g., Power Automate flow tied to a leaver event) is reverting owner assignments | KQL audit on `Agent.OwnerChanged` shows oscillating actor identities |
| **RC-F** | Console-backing store stale due to Microsoft-side cache invalidation lag | Mismatch persists > 24h with no reconcile correction; Service Health advisory present |

### §4.3 Diagnostic Steps

1. Capture both inventories at a single timestamp:
   - `$console = Get-Agt225InventoryExport -Format Json -Filter "ownership eq ''ownerless''"`
   - `$registry = Get-AgtRegistry -Filter "ownership eq ''ownerless''"` (Control 1.2 helper, see [Control 1.2 portal walkthrough](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md))
2. Compute set differences: agents in Console-only, in Registry-only, and in both. Persist to evidence library as E-05 enrichment.
3. For each Console-only-ownerless agent, issue **GQ-03** and inspect the `owners` collection. Empty array or tombstoned owner → confirms ownerless. Service principal owner → RC-C.
4. For each Registry-only-ownerless agent, query Registry-side reconciliation log for the most recent ownership-resolution attempt.
5. For RC-E suspicion, run `Get-Agt225AuditEvents -OperationName "Agent.OwnerChanged" -StartTime (Get-Date).AddDays(-7)` and group by `AgentId`. Any agent with > 4 owner changes in a week is in a reassignment loop.
6. For RC-B, enumerate soft-deleted directory objects referenced by Console: `Get-MgDirectoryDeletedItem -DirectoryObjectId <ownerId>` per affected agent.

### §4.4 Reassignment Loop Containment

If RC-E confirmed, **stop the reassignment loop before any further owner changes** to avoid producing audit-log noise that obscures the examiner narrative. Disable the offending automation:

```powershell
# Identify candidate automations
Get-MgIdentityGovernanceLifecycleWorkflow | Where-Object { $_.Category -eq ''leaver'' -and $_.Enabled }
# Pause the suspect workflow (requires AI Governance Lead + Identity Governance Admin)
Update-MgIdentityGovernanceLifecycleWorkflow -LifecycleWorkflowId <id> -Enabled $false
```

Document the pause in the change log. Resume only after the Power Automate / Logic App / lifecycle workflow logic has been corrected to honor the Console as the authoritative owner field.

### §4.5 Resolution Steps

| Root cause | Resolution |
|---|---|
| RC-A | Wait one reconcile cycle (≤ 6h); if mismatch persists, escalate to RC-F path. |
| RC-B | Restore or hard-delete the soft-deleted directory object via Identity team; re-run reconciliation. |
| RC-C | Use the Console "Reassign Owner" bulk action to set a human owner on each affected agent; update SDK / IaC to require owner field on creation. |
| RC-D | Update Registry mapping rules to expand group ownership for export parity, OR document the intentional divergence in the Registry README and the Risk Register. |
| RC-E | See §4.4. |
| RC-F | File Microsoft service request; fall back to Registry as the authoritative inventory until Console resolves; document fallback decision. |

### §4.6 Verification

1. Re-run §4.3 step 1 at T+1h after remediation. Set differences < 1% of total agents.
2. Pester `TRG-225-04` (Console-Registry Parity) passes.
3. Evidence E-05 (per-agent records) and E-08 (audit log) captured.
4. Cross-control verification: Control 3.6 orphaned-agent dashboard re-runs and produces matching count (within reconcile tolerance).

### §4.7 Cross-References

- [Control 1.2 — Agent Registry](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md)
- [Control 3.6 — Orphaned Agent Detection and Remediation](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md)
- [Portal Walkthrough §4 — Ownership operations](./portal-walkthrough.md)
- [Verification & Testing §4 — Inventory parity tests](./verification-testing.md)

---

## §5 Pillar: TEMPLATE-APPLY-FAIL

Applying the Default Governance Template (bundled at GA: Entra Identity Protection, Lifecycle Management, SharePoint access, Purview Audit / AI Compliance Assessment, automatic Agent 365 license assignment) or a Custom Governance Template (extends with Entra Access Packages, Global Secure Access, Purview Know Your Data, SharePoint Content Permissions Insights) returns an error or partial-success state. Zone 3 agents are required to bind to a Custom Template that includes an Entra Access Package — failures here block Zone 3 publish.

### §5.1 Symptom Catalog

| Code | Symptom | Severity hint |
|---|---|---|
| **P5-S1** | "Apply" button on Default Template returns "Prerequisite checks failed" | Sev2 |
| **P5-S2** | Custom Template apply succeeds but `prerequisiteState` reports `incomplete` for the access-package binding | Sev2 |
| **P5-S3** | Apply succeeds for some agents in scope, fails for others | Sev2 |
| **P5-S4** | Auto-license assignment fails: agents apply, but downstream license assignment to agent owner stalls | Sev2 |
| **P5-S5** | Custom Template apply fails with "GSA prerequisite missing" for Zone 3 agents | Sev1 (Zone 3 publish blocked) |
| **P5-S6** | Apply succeeds, but next-day reconcile shows the template state has reverted | Sev2 (configuration drift) |

### §5.2 Root Cause Matrix

| Code | Root cause | Confirmation signal |
|---|---|---|
| **RC-A** | Entra Identity Protection policy required by Default Template missing or disabled | GQ-04 returns `prerequisites: [{name:"IdentityProtection", state:"missing"}]` |
| **RC-B** | Purview AI Compliance Assessment policy missing or scope mismatch | GQ-04 prerequisite state `policyScopeMismatch` |
| **RC-C** | License drift: tenant has Frontier Suite assigned but seat count exhausted; auto-assignment cannot complete | `Get-Agt225LicenseAssignment -TenantScope` returns `seatsAvailable: 0` |
| **RC-D** | Custom Template bound to an Entra Access Package whose policy expired or lacks reviewer | GQ-05 returns `accessPackageBindingState: "policyExpired"` |
| **RC-E** | Global Secure Access (GSA) prerequisite required by Custom Template''s SharePoint Content Permissions Insights component is not deployed in tenant | GQ-05 prerequisite `gsa: "notDeployed"` |
| **RC-F** | Background reconciliation job conflict — concurrent template re-apply from a Power Automate scheduled flow | KQL-03 shows two template-apply events from different actors within seconds |

### §5.3 Diagnostic Steps

1. Issue **GQ-04** for Default Template; inspect `prerequisites` collection. Any element with `state != "satisfied"` indicates a missing dependency.
2. Issue **GQ-05** for the affected Custom Template. Inspect `prerequisites`, `accessPackageBindingState`, `componentStates`.
3. Run KQL-03 for last 24h. Group failures by `FailureReason`. Multi-mode failure (multiple distinct reasons) often indicates RC-F (concurrent apply).
4. Run `Get-Agt225TemplateStatus -TemplateId <id> -Detailed` to retrieve per-agent apply state. For P5-S3, the per-agent failure reason is the most precise diagnostic.
5. For RC-C, run `Get-Agt225LicenseAssignment -TenantScope -IncludeSeatAccounting`. If `seatsAvailable == 0`, coordinate with Procurement immediately.
6. For RC-E, validate GSA tenant posture: `Get-MgNetworkAccessTenantStatus`. If `provisioningState != "complete"`, the Custom Template''s SCPI component will fail.
7. For RC-D, retrieve access-package state: `Get-MgEntitlementManagementAccessPackage -AccessPackageId <id> -ExpandProperty AssignmentPolicies`.

### §5.4 Default Template Prerequisites (Reference)

The Default Governance Template at GA bundles five managed components. **Each must be in `satisfied` state** before apply will succeed:

| Component | Underlying control | Owner |
|---|---|---|
| Entra Identity Protection (sign-in & user risk policies for agent-OBO scenarios) | Identity team | Entra Global Admin |
| Lifecycle Management (joiner/leaver propagation to agent ownership) | Identity Governance | Identity Governance Admin |
| SharePoint access (default site-collection access boundaries for SharePoint-grounded agents) | M365 Apps | SharePoint Admin |
| Purview Audit + AI Compliance Assessment (audit pipeline + AI-specific risk evaluation) | Compliance | Purview Compliance Admin |
| Automatic Agent 365 license assignment (group-based) | Licensing | AI Administrator |

A change to any underlying control (e.g., a Purview policy retirement) can break the Default Template''s prerequisite check. The AI Administrator should subscribe to change-management notifications from each underlying-control owner.

### §5.5 Custom Template Re-apply (Recovery Procedure)

After remediating a prerequisite, re-apply the template:

```powershell
# Validate prerequisites first
$status = Get-Agt225TemplateStatus -TemplateId $templateId -Detailed
if ($status.PrerequisiteState -ne ''Satisfied'') {
    throw "Prerequisites not satisfied: $($status.PrerequisiteFailures -join ''; '')"
}
# Apply (idempotent)
Invoke-Agt225TemplateApply -TemplateId $templateId -Scope $scopeFilter -WhatIf
# Then drop -WhatIf and re-run after review
```

Capture the apply event in evidence (E-06).

### §5.6 Resolution Steps

| Root cause | Resolution |
|---|---|
| RC-A | Coordinate with Identity team to restore Identity Protection policy; re-apply per §5.5. |
| RC-B | Coordinate with Purview Compliance Admin to restore AI Compliance Assessment policy; re-apply. |
| RC-C | Procurement provisions additional Frontier Suite / Agent 365 seats; auto-assignment will complete on next reconcile (≤ 1h). |
| RC-D | Renew the Access Package assignment policy; assign reviewers; re-apply Custom Template. |
| RC-E | Coordinate with Identity / Network team to deploy GSA; until deployed, Zone 3 agents that depend on SCPI cannot publish. |
| RC-F | Disable conflicting Power Automate flow; consolidate template-apply automation under a single AI Administrator service principal. |

### §5.7 Verification

1. `Get-Agt225TemplateStatus -TemplateId <id>` returns `PrerequisiteState: Satisfied` and `ApplyState: Success` for all in-scope agents.
2. KQL-03 returns no failures in the past 1 h.
3. Pester `TRG-225-05` (Template Apply Idempotency) passes.
4. Evidence E-06 (template state snapshot) captured pre- and post-apply.

### §5.8 Cross-References

- [Portal Walkthrough §5 — Template management](./portal-walkthrough.md)
- [Verification & Testing §5 — Template apply tests](./verification-testing.md)
- [Control 2.26 — Entra Agent ID Identity Governance](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md) (template apply propagates identity-governance state)

---
## §6 Pillar: PUBLISH-WIZARD-FAIL

The Agent Publish wizard (used by Agent Owners to submit a new agent for approval, and by AI Administrators to publish on behalf) fails to save the draft, returns validation errors on required fields, or rejects a previously valid template binding due to template-version mismatch.

### §6.1 Symptom Catalog

| Code | Symptom | Severity hint |
|---|---|---|
| **P6-S1** | Publish wizard "Save draft" returns generic "Something went wrong" with no field-level error | Sev3 |
| **P6-S2** | Field-level validation errors on required fields the user has populated (false positives) | Sev3 |
| **P6-S3** | Template selector shows version `v3` but submit returns "Template version mismatch — expected v2" | Sev2 |
| **P6-S4** | Wizard accepts submission, but the request never appears in the approval queue | Sev2 (cross-link to §3) |
| **P6-S5** | "Required field gap" surfaced for an Agent Owner field that the firm has marked optional in its Custom Template | Sev2 |
| **P6-S6** | Publish wizard returns 403 "Insufficient privilege" for an Agent Owner who has the `Agent365.Publish.Submit` permission | Sev2 |

### §6.2 Root Cause Matrix

| Code | Root cause | Confirmation signal |
|---|---|---|
| **RC-A** | Custom Template was edited mid-flight; user''s draft was created against the prior version | Browser dev-tools shows submitted `templateVersion` ≠ Console current |
| **RC-B** | Required-field metadata cached on the client; backend now demands additional fields after a Custom Template update | KQL audit shows `Template.SchemaUpdated` event in the last 24h |
| **RC-C** | License posture for the submitter changed mid-session (Frontier Suite seat reclaimed) | `Get-Agt225LicenseAssignment -UserPrincipalName <upn>` returns `enabled: false` |
| **RC-D** | Approval-queue ingestion broken (cross-link §3 RC-A) | Wizard succeeds; queue does not show entry |
| **RC-E** | Custom Template''s `requiredFields` schema includes a field that no longer exists in the Console UI (schema drift) | `Get-Agt225TemplateStatus -TemplateId <id> -Detailed` shows `schemaWarnings` |
| **RC-F** | Submitter''s permission was assigned via a group whose membership eval is delayed | Sign-in log shows token issued before group-membership refresh |

### §6.3 Diagnostic Steps

1. Reproduce in InPrivate session with a known-good Agent Owner identity. Capture HAR file for E-03 enrichment.
2. Inspect submitted JSON payload in browser dev-tools network panel. Note `templateVersion`, `requiredFields` set, and HTTP response body.
3. Issue **GQ-05** for the affected Custom Template; compare `version` and `requiredFields` to the submitted payload.
4. Run `Get-Agt225TemplateStatus -TemplateId <id> -Detailed` and inspect `schemaWarnings` and `lastSchemaUpdate`.
5. For P6-S6, run `Get-MgUserMemberOf -UserId <upn>` and verify the publish-permission group membership is present *and* token reflects it (`Get-MgAuditLogSignIn -Filter "userPrincipalName eq ''<upn>''"`).
6. For P6-S4, immediately switch to §3 diagnostic flow.

### §6.4 Schema-Drift Containment

When a Custom Template is edited, in-flight drafts created against the prior schema will fail submission. The Console does **not** auto-migrate drafts. Containment requires:

1. AI Administrator publishes a change-management notice ≥ 24h before a Custom Template schema update.
2. Drafts older than the schema update are listed via `Get-Agt225PendingRequests -Status draft -OlderThan (Get-Date).AddDays(-1)`.
3. Affected Agent Owners are notified to re-create the draft against the new schema.
4. Old drafts are auto-purged at T+30 days per the Default Template lifecycle policy.

### §6.5 Resolution Steps

| Root cause | Resolution |
|---|---|
| RC-A | User re-creates draft against current template version; AI Administrator confirms no other in-flight drafts via §6.4. |
| RC-B | Force client refresh (hard reload) so client picks up the new schema. If recurring, file Microsoft service request — schema cache TTL may need tuning. |
| RC-C | Coordinate with Procurement / Identity to restore submitter''s license; user re-attempts submission. |
| RC-D | Switch to §3. |
| RC-E | AI Administrator removes orphaned `requiredFields` entry from Custom Template; re-apply per §5.5. |
| RC-F | Wait ≤ 1 h for token-refresh cycle; user re-attempts. If persistent, file Identity-team ticket. |

### §6.6 Verification

1. Test agent submission via test Agent Owner identity completes within 60 s.
2. Submitted entry appears in approval queue within 2 min.
3. Pester `TRG-225-06` (Publish Wizard Round-Trip) passes.
4. Evidence E-04 captured if Sev2.

### §6.7 Cross-References

- [Portal Walkthrough §6 — Publish wizard](./portal-walkthrough.md)
- [Verification & Testing §6 — Publish round-trip](./verification-testing.md)

---

## §7 Pillar: DEPLOY-ACTION-FAIL

Deploy / Reassign / Disable bulk actions from the Console fail for one or more target agents. Bulk actions are critical for SOX ITGC change-control narratives because they are the auditable surface through which the AI Administrator effects post-approval state changes at scale.

### §7.1 Symptom Catalog

| Code | Symptom | Severity hint |
|---|---|---|
| **P7-S1** | Bulk Deploy returns "Partial success: N of M agents failed" | Sev2 |
| **P7-S2** | Single-agent Deploy returns "Target group could not be resolved" | Sev3 |
| **P7-S3** | Deploy succeeds in UI but downstream license check shows target users do not have required license | Sev2 |
| **P7-S4** | Deploy blocked by Conditional Access on the actor session mid-action | Sev2 |
| **P7-S5** | Reassign Owner action returns "Dependent agents must be reassigned first" | Sev3 |
| **P7-S6** | Bulk Disable succeeds in UI but Purview audit log shows no `Agent.Disabled` events | Sev1 (audit gap) |

### §7.2 Root Cause Matrix

| Code | Root cause | Confirmation signal |
|---|---|---|
| **RC-A** | Target group unresolvable: dynamic Entra group rule errored; group soft-deleted; group too large for Console expansion | KQL audit shows `BulkAction.GroupResolutionFailed` |
| **RC-B** | License-coverage gap on target population (cross-link RB-04) | `Get-Agt225LicenseAssignment -GroupId <targetGroup>` returns coverage < 100% |
| **RC-C** | Conditional Access interrupt (cross-link §2 RC-E) | Sign-in log shows interrupt during action |
| **RC-D** | Dependency chain: agents reference one another via multi-agent orchestration (Control 2.17); reassign parent first | GQ-03 returns `dependencies: [...]` |
| **RC-E** | Bulk action exceeded the Console''s 500-agent batch limit; the Console truncated silently in pre-GA, errors loudly post-GA | Action JSON payload count > 500 |
| **RC-F** | Audit pipeline outage (cross-link §3 RC-F) | `Get-Agt225AuditEvents` returns empty for known successful actions |

### §7.3 Diagnostic Steps

1. Capture the bulk-action correlation ID from the Console UI ("View action details" link) and persist as evidence.
2. Run KQL-05 for the past 24h. Group failures by `ActionType` and `FailureReason`. Cross-reference to RC table.
3. For P7-S2, run `Get-MgGroup -GroupId <targetGroup> -Property *` and validate `groupTypes`, `membershipRule`, `membershipRuleProcessingState`. Errored dynamic-rule processing → RC-A.
4. For P7-S3, run `Get-Agt225LicenseAssignment -GroupId <targetGroup> -IncludeMissingMembers` to enumerate users lacking required license.
5. For P7-S5, run `Get-Agt225Agent -Id <agentId>` and inspect `dependencies` collection. Plan reassignment in dependency-topological order.
6. For P7-S6, immediately escalate to Purview Compliance Admin per §3 RC-F path; do **not** re-run the bulk action until audit pipeline confirmed healthy.

### §7.4 Batch-Size Discipline

Bulk actions in the Agent 365 Admin Center are bounded at **500 agents per submission** post-GA. For tenants with > 500 agents in scope, partition the action via PowerShell:

```powershell
$targets = Get-Agt225InventoryExport -Format Json -Filter "<scope>"
$batches = [System.Collections.ArrayList]::new()
for ($i = 0; $i -lt $targets.Count; $i += 500) {
    $end = [Math]::Min($i + 499, $targets.Count - 1)
    $null = $batches.Add($targets[$i..$end])
}
foreach ($batch in $batches) {
    Invoke-Agt225BulkAction -ActionType Deploy -AgentIds $batch.Id -CorrelationIdPrefix "deploy-$(Get-Date -Format yyyyMMdd)"
    Start-Sleep -Seconds 30  # respect throttle
}
```

Each batch produces a distinct correlation ID, which simplifies the SOX ITGC change-record narrative.

### §7.5 Resolution Steps

| Root cause | Resolution |
|---|---|
| RC-A | Repair dynamic group rule via Identity team; OR target a static group; re-run failed batch only. |
| RC-B | Coordinate license remediation per RB-04 (§14); re-run after coverage restored. |
| RC-C | Coordinate Conditional Access exemption per §2 RC-E. |
| RC-D | Re-order action in topological order per §7.4 helper; reassign roots first, dependents second. |
| RC-E | Re-partition action per §7.4. |
| RC-F | Freeze actions; restore audit pipeline; back-fill audit events with Microsoft Support before resuming. |

### §7.6 Verification

1. KQL-05 returns 0% failure rate for the most recent action.
2. Target population state matches expected post-action state (sample 10 agents via `Get-Agt225Agent`).
3. Pester `TRG-225-07` (Bulk Action Round-Trip) passes.
4. Evidence E-08 captured for the action window; correlation IDs catalogued.

### §7.7 Cross-References

- [Control 2.17 — Multi-Agent Orchestration Limits](../../../controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md)
- [Portal Walkthrough §7 — Bulk operations](./portal-walkthrough.md)
- [Verification & Testing §7 — Bulk action tests](./verification-testing.md)

---

## §8 Pillar: INVENTORY-EXPORT-INCOMPLETE

The Agent 365 Admin Center inventory export (CSV / JSON via UI, or Graph job per GQ-08) returns truncated rows, missing columns, or fails outright. Examiner production frequently depends on inventory-export deliverables — this pillar is high-priority during exam windows.

### §8.1 Symptom Catalog

| Code | Symptom | Severity hint |
|---|---|---|
| **P8-S1** | UI export returns CSV with row count < known agent count | Sev2 (Sev1 if examiner-active) |
| **P8-S2** | Graph export job (`exportJobs/{jobId}`) stays in `running` indefinitely (> 30 min) | Sev2 |
| **P8-S3** | Export missing columns the Console UI displays (e.g., `governanceTemplateId`, `lastApprovedBy`) | Sev2 |
| **P8-S4** | Export succeeds but row encoding garbles non-ASCII characters in agent names / descriptions | Sev3 |
| **P8-S5** | Two consecutive exports return different row counts (non-deterministic) | Sev2 |
| **P8-S6** | Export job returns 403 "Insufficient privilege" for an admin who can view inventory in UI | Sev3 |

### §8.2 Root Cause Matrix

| Code | Root cause | Confirmation signal |
|---|---|---|
| **RC-A** | Export pagination bug — UI export silently truncates at 10,000 rows | Row count exactly 10,000 |
| **RC-B** | Permission propagation lag: AI Administrator role assigned via group, token has not refreshed | Sign-in log timestamp > role-assignment timestamp by < 1h |
| **RC-C** | Export format gaps — CSV format omits columns that JSON includes | Compare CSV vs JSON exports of same scope |
| **RC-D** | Source-data ownership reconciliation in flight (cross-link §4 RC-A) | Two consecutive exports differ; KQL shows reconciliation event between |
| **RC-E** | Encoding configuration: CSV exported as Windows-1252 instead of UTF-8 | Garbled non-ASCII characters in CSV |
| **RC-F** | Microsoft-side export-job worker outage | Service Health advisory; multiple jobs stuck `running` |

### §8.3 Diagnostic Steps

1. Compare expected vs actual: `$expected = (Get-Agt225Agent -All).Count`; `$actual = (Import-Csv $exportPath).Count`. Delta indicates RC-A or RC-D.
2. For P8-S2, issue **GQ-08** with the job ID. Inspect `state`, `progress`, `error`. `running` > 30 min → cancel and re-submit; persistent → RC-F.
3. For P8-S3, request both CSV and JSON exports of the same scope; diff column lists. Confirm the missing column is present in JSON; if so, RC-C — use JSON for examiner production.
4. For P8-S5, compute row-count delta and run KQL audit for `Agent.OwnerChanged` events between the two exports. Reconciliation activity → RC-D.
5. For P8-S6, validate role-membership token freshness as in §6 RC-F.

### §8.4 PowerShell Fallback (Authoritative for Examiner Production)

When the UI export is unreliable, fall back to the helper cmdlet documented in [PowerShell Setup §3](./powershell-setup.md) — `Get-Agt225InventoryExport`. The helper:

- Streams pagination beyond the 10,000-row UI ceiling
- Emits all columns regardless of CSV/JSON choice
- Uses UTF-8 encoding by default
- Computes a SHA-256 hash of the output and writes it alongside the file for integrity attestation

```powershell
$exportPath = "./evidence/agent-inventory-$(Get-Date -Format yyyyMMddHHmmss).json"
Get-Agt225InventoryExport -Format Json -OutputPath $exportPath -ComputeIntegrityHash
# Writes $exportPath and $exportPath.sha256
```

For SEC 17a-4 examiner production, the hash file is co-archived to the immutable evidence library and referenced in the production-package README.

### §8.5 Resolution Steps

| Root cause | Resolution |
|---|---|
| RC-A | Use PowerShell fallback (§8.4); file Microsoft service request for UI pagination fix. |
| RC-B | Wait ≤ 1 h for token refresh; if persistent, force token refresh via re-auth. |
| RC-C | Use JSON format for examiner production; document column-set difference in production README. |
| RC-D | Wait for reconciliation cycle to complete (≤ 6h); then re-export. Document the timing in production README. |
| RC-E | Use PowerShell fallback (§8.4) which forces UTF-8; OR open CSV in Excel with explicit UTF-8 import. |
| RC-F | Wait on Microsoft mitigation; use PowerShell fallback as primary. |

### §8.6 Verification

1. Row count matches `(Get-Agt225Agent -All).Count` ± reconciliation tolerance (< 1%).
2. JSON export contains all columns documented in [Portal Walkthrough §8](./portal-walkthrough.md).
3. SHA-256 hash file present alongside export.
4. Pester `TRG-225-08` (Inventory Export Integrity) passes.
5. Evidence E-05 captured.

### §8.7 Cross-References

- [PowerShell Setup §3 — Inventory export helper](./powershell-setup.md)
- [Control 3.1 — Agent Inventory and Metadata Management](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md)
- [Control 3.11 — Centralized Agent Inventory Enforcement](../../../controls/pillar-3-reporting/3.11-centralized-agent-inventory-enforcement.md)

---
## §9 Pillar: RESEARCHER-CONFIG-DRIFT

Researcher with Computer Use (GA October 2025) is **default-on for Copilot-licensed tenants**. FSI tenants must make an affirmative restrictive decision: scope to a specific Entra group, OR set scope to `none`. This pillar covers detection and remediation when the configured scope drifts — typically due to a license-eligibility change, a group-membership change, or a tenant-wide policy push from Microsoft.

> **FSI affirmative-restriction expectation.** A Copilot-licensed Researcher with Computer Use enables agents to operate browser-based actions on behalf of the user. In an FSI context, this surface must be explicitly scoped, not implicitly enabled. Document the scoping decision and reviewing approver in the Risk Register.

### §9.1 Symptom Catalog

| Code | Symptom | Severity hint |
|---|---|---|
| **P9-S1** | `Get-Agt225ResearcherConfig` returns `enabledFor: "all"` when the firm policy is group-scoped | Sev1 |
| **P9-S2** | Bound group exists but membership has expanded to include users not in the originally approved population | Sev2 |
| **P9-S3** | Scope was `none`, but a recent Microsoft tenant-policy push reverted to default-on | Sev1 |
| **P9-S4** | Scope unchanged but feature is unavailable to approved users (regression) | Sev3 |
| **P9-S5** | License expiry mid-period: user retained group membership but lost Copilot license; feature no longer available — change is silent | Sev3 |
| **P9-S6** | Audit event `Feature.ResearcherComputerUse.ScopeChanged` recorded but no change-management ticket exists | Sev1 (unsanctioned change) |

### §9.2 Root Cause Matrix

| Code | Root cause | Confirmation signal |
|---|---|---|
| **RC-A** | Microsoft tenant-policy push (e.g., new Wave release toggles default-on); customer override not preserved | KQL-04 shows `ActorUPN: System` change event |
| **RC-B** | Identity team modified group membership without notifying AI Governance | Group-membership audit shows additions; no change ticket |
| **RC-C** | License-driven eligibility change: user lost Copilot license; Researcher silently unavailable for that user | `Get-Agt225LicenseAssignment -UserPrincipalName <upn>` shows `copilot: false` |
| **RC-D** | An admin used the Console "Reset to Microsoft default" action in error | KQL-04 shows admin actor + `NewScope: "all"` |
| **RC-E** | Custom Governance Template removed the Researcher scoping component during a template edit | GQ-05 diff shows component removal |
| **RC-F** | Conditional Access change blocks Researcher for in-scope users (false-positive availability gap) | Sign-in log shows blocking CA evaluation |

### §9.3 Diagnostic Steps

1. Capture current state: `$rc = Get-Agt225ResearcherConfig -Detailed`. Persist as evidence E-06 enrichment.
2. Compare `$rc` to the approved baseline stored in the tenant Risk Register. Any divergence → RC-A through RC-E.
3. Run KQL-04 for the past 90 days. Inspect every scope change. Match each to a change-management ticket.
4. For P9-S2, run `Get-MgGroupMember -GroupId <boundGroup>` and compare to the approved-population source-of-truth (often an HR system export). Membership expansion → RC-B.
5. For P9-S5, run `Get-Agt225LicenseAssignment -GroupId <boundGroup> -IncludeMissingMembers` to enumerate license-eligibility gaps in the bound group.

### §9.4 Affirmative-Restriction Reset Procedure

Re-applying the firm''s scoping decision after detected drift:

```powershell
# Apply group-scoped restriction (preferred)
Set-Agt225ResearcherConfig -Scope Group -BoundGroupId $approvedGroupId `
    -JustificationText "Reset to firm baseline per RR-225-009; ticket CHG-2026-0421" `
    -Confirm

# OR apply firm-wide disable (most restrictive)
Set-Agt225ResearcherConfig -Scope None `
    -JustificationText "Disable per firm policy; pending zone-3 risk review" `
    -Confirm
```

The cmdlet writes a `Feature.ResearcherComputerUse.ScopeChanged` audit event with the supplied justification. Capture E-08 immediately after.

### §9.5 Resolution Steps

| Root cause | Resolution |
|---|---|
| RC-A | Apply §9.4 immediately; file Microsoft service request to flag the override-loss; subscribe to Wave-release change notices to anticipate future pushes. |
| RC-B | Apply §9.4; coordinate with Identity team to add change-management gating on the bound group; consider converting to PIM-eligible group. |
| RC-C | Coordinate Procurement to restore licensing OR remove user from bound group with documented rationale. |
| RC-D | Apply §9.4; review admin role assignments and consider PIM-elevation for the scope-change permission. |
| RC-E | Restore Custom Template scoping component; re-apply per §5.5; review template-edit change-control. |
| RC-F | Coordinate with Identity team to add Researcher-scope exemption to the blocking CA policy. |

### §9.6 Verification

1. `Get-Agt225ResearcherConfig` returns scope matching firm baseline.
2. KQL-04 shows the reset event with admin justification.
3. Bound-group membership matches HR-system source-of-truth.
4. Pester `TRG-225-09` (Researcher Scope Drift Detection) passes.
5. Evidence E-06 and E-08 captured pre- and post-reset.

### §9.7 Cross-References

- [Control 2.24 — Agent Feature Enablement and Restriction Governance](../../../controls/pillar-2-management/2.24-agent-feature-enablement-and-restriction-governance.md)
- [Portal Walkthrough §9 — Researcher scope management](./portal-walkthrough.md)
- [Verification & Testing §9 — Researcher scope tests](./verification-testing.md)

---

## §10 Pillar: SOV-PARITY-GAP — Sovereign Cloud Compensating Controls

Microsoft Agent 365 Admin Center, Default and Custom Governance Templates, admin-gated approval workflows, and Researcher with Computer Use are **not at parity** in GCC, GCC High, or DoD as of April 2026. Sovereign-tenant operators cannot use the procedures in §2–§9 directly. This pillar documents the compensating-control posture that **supports** equivalent governance outcomes pending Microsoft sovereign-cloud parity.

> **Hedged framing.** Compensating controls **support** the firm''s objective of equivalent governance posture. They do **not** guarantee functional equivalence with the commercial-cloud Admin Center. Document the gap, the compensating controls in effect, and the residual risk in the tenant Risk Register, reviewed quarterly by the AI Governance Lead and the Information Security Officer.

### §10.1 Parity Status (April 2026)

| Capability | Commercial | GCC | GCC High | DoD |
|---|---|---|---|---|
| Agent 365 Admin Center | GA | Not available | Not available | Not available |
| Default Governance Template | GA | Not available | Not available | Not available |
| Custom Governance Templates | GA | Not available | Not available | Not available |
| Admin-gated approval workflows | GA | Not available | Not available | Not available |
| Researcher with Computer Use | GA (Oct 2025) | Not available | Not available | Not available |
| `/beta/admin/agent365` Graph namespace | Available | Not available | Not available | Not available |
| Purview Audit (`Agent365AdminCenter` workload) | Available | Audit available, workload tag not yet emitted | Audit available, workload tag not yet emitted | Audit available, workload tag not yet emitted |

Sovereign-cloud operators should subscribe to the Microsoft Cloud Sovereignty roadmap and revalidate this table quarterly.

### §10.2 Compensating Control Posture

For each Admin Center capability not available in sovereign clouds, the following compensating controls apply:

| Capability gap | Compensating control | Owner | Evidence pattern |
|---|---|---|---|
| Console inventory & ownership view | Agent Registry export (Control 1.2 PowerShell) | AI Administrator | Registry CSV/JSON to immutable evidence library, daily |
| Default Template auto-bundle | Manual binding of each underlying control via per-control PowerShell scripts | AI Administrator + per-control owners | Per-control verification logs |
| Custom Template extension | Manual binding of Entra Access Packages, GSA, Purview KYD, SCPI via per-control scripts | AI Administrator | Per-control verification logs |
| Admin-gated approval workflow | Manual approval workflow via ServiceNow / Jira ticket + Power Automate flow against the Agent Registry | AI Governance Lead | Ticket archive + Registry change log |
| Researcher with Computer Use scoping | Feature unavailable in sovereign clouds; document non-applicability | AI Governance Lead | Risk Register entry |
| Inventory export | `Get-AgtRegistry -Export` (Control 1.2) | AI Administrator | UTF-8 + SHA-256 to immutable evidence library |

### §10.3 Sovereign Cloud Activation Runbook

When a sovereign-tenant on-call engineer is paged for a Control 2.25 incident, the response is **always** to activate compensating controls and **never** to attempt commercial-cloud procedures (which will fail with 404 / 403).

1. **Acknowledge the parity gap** in the incident record (template text in `runbooks/sov-225-ack.md`).
2. **Identify the requested operation** (inventory pull, approval, ownership change, template apply equivalent).
3. **Map to the compensating control** per §10.2 and execute via Control 1.2 / Control 3.6 / per-control PowerShell.
4. **Capture evidence** to the sovereign-tenant immutable evidence library (`AgentGov-Evidence-225-Sov`).
5. **File a quarterly Risk Register update** noting the incident as evidence of the residual risk.

### §10.4 Sovereign Endpoint Reference

All sovereign-cloud diagnostic queries must use the appropriate endpoint. See [PowerShell Baseline §3](../../_shared/powershell-baseline.md#3-sovereign-cloud-endpoints-gcc-gcc-high-dod) for the canonical endpoint list. The `Get-Agt225*` helpers detect cloud environment via `Get-MgEnvironment` and substitute endpoints automatically; manual Graph queries must substitute by hand.

### §10.5 Verification

1. Sovereign tenant Risk Register entry exists, updated within last 90 days.
2. Compensating-control evidence is being produced on the documented cadence (e.g., daily Registry export).
3. Pester `TRG-225-10` (Sovereign Compensating Control Activation) passes — the test verifies that `Get-Agt225Health` correctly reports `SovereignCompensatingMode: true` on a sovereign tenant.
4. Quarterly review attestation signed by AI Governance Lead + Information Security Officer.

### §10.6 Cross-References

- [PowerShell Baseline §3 — Sovereign Endpoints](../../_shared/powershell-baseline.md#3-sovereign-cloud-endpoints-gcc-gcc-high-dod)
- [Control 1.2 — Agent Registry](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md)
- [Control 3.6 — Orphaned Agent Detection and Remediation](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md)

---
## §11 Runbook RB-01 — Mass Agent Re-onboarding After Acquisition

**Trigger.** The firm has acquired another organization and 10+ agents from the acquired tenant must be onboarded into the Frontier-Suite tenant''s Console with template binding, ownership assignment, and approval. Sev2 unless examiner-active or > 200 agents (Sev1).

### §11.1 Pre-Conditions

- Acquired-tenant inventory exported as CSV/JSON with at minimum: agent display name, owner UPN (mapped to acquirer-tenant UPN), zone classification, current template binding, license requirement.
- Frontier Suite seats provisioned for inbound owners (verified via `Get-Agt225LicenseAssignment -TenantScope -IncludeSeatAccounting`).
- Default Governance Template and any required Custom Templates are in `prerequisiteState: Satisfied`.
- Change-management ticket open with rollback plan.

### §11.2 Procedure

1. **Stage inventory**: import the acquired CSV; validate UPN mapping; flag rows without acquirer-tenant UPN (these block the run).
2. **Partition by zone**: Zone 3 agents must bind to a Custom Template with Entra Access Package; do these in a separate batch.
3. **Submit publish drafts via PowerShell** (Console wizard does not scale to 10+):
   ```powershell
   $stage = Import-Csv ./acquisition-stage.csv
   foreach ($row in $stage) {
       New-Agt225PublishDraft -DisplayName $row.DisplayName -OwnerUpn $row.OwnerUpn `
           -Zone $row.Zone -GovernanceTemplateId $row.TemplateId `
           -CorrelationIdPrefix "rb01-$(Get-Date -Format yyyyMMdd)"
   }
   ```
4. **Approve in batches** of ≤ 50 via the Console approval queue. AI Governance Lead reviews; FINRA-3110 manual supervisory review per §3.4 must accompany.
5. **Apply template** per §5.5 procedure.
6. **Verify** via `Get-Agt225Agent` sample of 10% (or all if N < 100).

### §11.3 Evidence Bundle

- E-04 approval queue snapshot at start, mid-point, end
- E-05 per-agent records post-onboarding
- E-06 template state pre/post
- E-08 Purview audit window
- Acquisition CSV + UPN mapping spreadsheet
- Change-management ticket with sign-off chain

### §11.4 Rollback

If onboarding produces unexpected failures (> 5% per batch), pause via `Suspend-Agt225BulkOperation -CorrelationIdPrefix "rb01-..."`. Disable agents created in the failing batch via `Invoke-Agt225BulkAction -ActionType Disable`. Document and re-plan.

### §11.5 Cross-References

- [Verification & Testing §11 — Mass onboarding tests](./verification-testing.md)
- [Control 2.3 — Change Management and Release Planning](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md)

---

## §12 Runbook RB-02 — Examiner Pulls Quarterly Governance Evidence with Stale Approval Queue

**Trigger.** A FINRA / SEC / OCC / Fed examiner has issued a request for quarterly governance evidence (typically: ownerless inventory, approval audit, template-state snapshot, Researcher scope evidence) and the approval queue is stale per §3. Sev1 by default.

### §12.1 Pre-Conditions

- Examiner request acknowledged in Compliance ticketing system with response SLA documented.
- Legal has reviewed the request scope.
- Incident commander assigned (AI Governance Lead).

### §12.2 Procedure

1. **Freeze the queue state immediately**: capture E-04 (queue snapshot), E-08 (audit log) for the examiner-requested window. **Do not** mutate state until evidence is preserved.
2. **Diagnose the staleness** per §3 in parallel with the examiner-evidence collection. Engage Microsoft Support if RC-A or RC-F suspected.
3. **Activate FINRA 3110 manual-review fallback** per §3.4. The registered principal''s independent supervisory judgment continues; the queue tooling is unavailable.
4. **Produce examiner deliverables** from the **frozen** evidence (not from live queries that may reflect the staleness):
   - Queue snapshot: E-04 with timestamp, depth, p95 age, FINRA-3110 manual-review log
   - Approval audit: KQL `AgentGovActivity | where OperationName startswith "ApprovalRequest." | where TimeGenerated between (start..end)`
   - Ownership inventory: Registry export (Control 1.2), with delta-vs-Console reconciliation note per §4
   - Template state: `Get-Agt225TemplateStatus -All` snapshot
   - Researcher scope: `Get-Agt225ResearcherConfig -Detailed` snapshot
5. **Document the staleness** in the production package README. Disclose: "The Agent 365 Admin Center approval queue experienced a Sev1 staleness incident from {start} to {end}; manual supervisory review continued throughout per FINRA Rule 3110 § (b); evidence of the manual review is in Section X of this package."

### §12.3 Examiner-Production Package Structure

```
examiner-prod-2026Q1/
├── README.md
├── 01-ownership-inventory.json (Registry export, SHA-256)
├── 02-approval-audit.csv (KQL export, SHA-256)
├── 03-template-state.json
├── 04-researcher-scope.json
├── 05-queue-staleness-incident-record.md
├── 06-manual-review-evidence/ (FINRA 3110 supervisory log)
└── attestation.pdf (signed by AI Governance Lead + Compliance Officer)
```

### §12.4 Cross-References

- [Control 2.12 — Supervision and Oversight (FINRA Rule 3110)](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md)
- [Control 3.3 — Compliance and Regulatory Reporting](../../../controls/pillar-3-reporting/3.3-compliance-and-regulatory-reporting.md)

---

## §13 Runbook RB-03 — Bulk Owner Reassignment After Team Reorganization

**Trigger.** A business-unit reorganization has changed reporting lines for 25+ agent owners; the Console "Owner" field must be updated to reflect new ownership without breaking template bindings or approval workflows. Sev2.

### §13.1 Pre-Conditions

- HR-system export of leaver-joiner mapping (old UPN → new UPN) validated by HR data steward.
- New owners have Frontier Suite / Agent 365 license assignment.
- New owners hold an Agent Owner role binding (or a group containing them does).

### §13.2 Procedure

1. **Stage mapping**: import HR CSV; validate every old UPN appears exactly once.
2. **Capture pre-state**: `Get-Agt225InventoryExport -Format Json` to evidence.
3. **Apply reassignment**:
   ```powershell
   $map = Import-Csv ./reorg-owner-map.csv  # columns: OldOwnerUpn, NewOwnerUpn
   $agents = Get-Agt225Agent -All | Where-Object { $map.OldOwnerUpn -contains $_.OwnerUpn }
   foreach ($a in $agents) {
       $newUpn = ($map | Where-Object OldOwnerUpn -eq $a.OwnerUpn).NewOwnerUpn
       Invoke-Agt225BulkAction -ActionType ReassignOwner -AgentIds @($a.Id) `
           -NewOwnerUpn $newUpn -CorrelationIdPrefix "rb03-$(Get-Date -Format yyyyMMdd)"
   }
   ```
4. **Verify**: post-state export; diff to pre-state should match the mapping table exactly.
5. **Confirm no reassignment loop** per §4.4 (no automation should be reverting these changes).

### §13.3 Evidence Bundle

- HR mapping CSV
- Pre/post inventory exports
- E-08 audit log for the reassignment window
- Confirmation of zero-loop check (KQL `Agent.OwnerChanged` showing each agent changed exactly once)

### §13.4 Cross-References

- [Verification & Testing §13 — Reassignment tests](./verification-testing.md)
- [Control 1.2 — Agent Registry](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md)

---

## §14 Runbook RB-04 — License Coverage Gap (Agent Acting OBO Unlicensed User)

**Trigger.** Audit reveals one or more agents performing OBO (on-behalf-of) operations for users whose Frontier Suite / Agent 365 / Copilot license has lapsed. Sev1 because the firm is consuming a service that the user is not licensed for, with potential contractual and audit consequences.

### §14.1 Pre-Conditions

- License-coverage gap identified, typically via `Get-Agt225LicenseAssignment -GroupId <agentTargetGroup> -IncludeMissingMembers`.
- Procurement engaged for emergency license review.

### §14.2 Procedure

1. **Identify scope**: enumerate agents, target users, and time window of OBO activity for unlicensed users.
2. **Immediate containment**: disable the affected agents via `Invoke-Agt225BulkAction -ActionType Disable -AgentIds @(...)` to stop further unlicensed OBO activity.
3. **Capture evidence**: E-08 audit window covering all unlicensed OBO calls (for SOX ITGC and contractual records).
4. **Decision branch**:
   - If users should be licensed: Procurement provisions licenses; re-enable agents; post-mortem.
   - If users should not be licensed: remove users from the target group; re-enable agents with corrected scope; document rationale.
5. **Notify Compliance Officer** for assessment of contractual exposure.

### §14.3 Evidence Bundle

- License-gap analysis output
- Disable bulk-action correlation IDs
- E-08 audit window
- Procurement decision record OR target-group correction record
- Compliance Officer acknowledgement

### §14.4 Cross-References

- [Control 2.7 — Vendor and Third-Party Risk Management](../../../controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md)
- [Verification & Testing §14 — License coverage tests](./verification-testing.md)

---

## §15 Runbook RB-05 — Agent Suggestions Feature Lighting Up Unexpectedly

**Trigger.** Agent Suggestions (Microsoft-planned for 2026 Wave 1, **not yet GA** as of April 2026) appears in the Admin Center or in user surfaces unexpectedly — either via a Microsoft preview rollout or via a misconfigured tenant flighting flag. Sev2 because the feature has no FSI risk-acceptance documentation yet.

### §15.1 Pre-Conditions

- Detection: Console UI shows a "Suggestions" blade not previously present, OR users report receiving "suggested agents" notifications.
- AI Governance Lead has not yet approved Agent Suggestions for this tenant.

### §15.2 Procedure

1. **Capture evidence** of the unexpected feature appearance: E-01 console screenshot; any user notification screenshots; release-notes search for "Agent Suggestions" GA status.
2. **Disable at tenant scope** if a feature toggle is exposed:
   ```powershell
   # Toggle path subject to change once GA; check release notes
   Set-Agt225FeaturePolicy -FeatureName AgentSuggestions -State Disabled `
       -JustificationText "Feature not yet risk-accepted; awaiting GA + AI Governance Lead review"
   ```
3. **If no toggle is exposed** (common during silent flighting): file a Microsoft service request requesting opt-out; in parallel, communicate to users via the change-management channel that the feature is not yet sanctioned.
4. **Open Risk Register entry** noting the unsanctioned feature appearance, dates, and remediation.
5. **Schedule risk review** when GA is announced; do **not** rely on the silently-flighted feature for any production workflow.

### §15.3 Evidence Bundle

- Screenshots of unexpected feature appearance
- Microsoft service request reference
- Risk Register entry
- AI Governance Lead acknowledgement

### §15.4 Cross-References

- [Control 2.24 — Agent Feature Enablement and Restriction Governance](../../../controls/pillar-2-management/2.24-agent-feature-enablement-and-restriction-governance.md)
- [Control 2.3 — Change Management and Release Planning](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md)

---

## §16 Runbook RB-06 — Frontier-Suite → Agent 365 GA Migration Day Issues (May 1, 2026 Transition)

**Trigger.** On the May 1, 2026 GA cutover, tenants enrolled in pre-GA preview migrate to GA. Symptoms during the cutover window can include: console blade reshuffling, deprecated flighting flags, transient template-prerequisite check failures, audit-pipeline correlation-ID format changes. Sev2 by default; Sev1 if examiner-active during the cutover.

### §16.1 Pre-Conditions

- Pre-GA preview tenants identified; AI Administrator subscribed to Microsoft cutover communications.
- Cutover window (Microsoft-published) captured in the change-management calendar.
- Examiner-active windows checked against cutover; Compliance notified if conflict.

### §16.2 Procedure

1. **T-7d**: Validate `Get-Agt225Health -Verbose` returns `Channel: PreviewLatest`; capture baseline E-01..E-09.
2. **T-1d**: Capture full evidence baseline (E-04, E-05, E-06, E-08).
3. **T+0** (cutover window): Suspend non-essential bulk operations; monitor `Get-Agt225Health` every 15 min.
4. **T+0 → T+24h**: After cutover banner clears, validate `Channel: GA`. Re-run §2.6, §3.6, §5.7 verification suites.
5. **T+24h → T+7d**: Monitor KQL-01 / KQL-02 / KQL-03 daily for elevated failure rates. Microsoft typically issues post-cutover hotfixes during this window.
6. **T+7d**: Capture post-migration evidence baseline; archive comparison artifacts.

### §16.3 Cutover Failure Modes

| Mode | Symptom | Action |
|---|---|---|
| Flighting flag stuck | `Channel: preview-deprecated` after cutover | §2.4 procedure |
| Template prerequisite false-fail | `prerequisiteState: incomplete` despite no underlying change | Re-apply per §5.5; if persistent, file Microsoft service request |
| Audit correlation-ID format change | KQL queries that parse correlation IDs may break | Update KQL parsers per Microsoft cutover release notes |
| Researcher scope drift to default-on | Cross-link §9 RC-A | Apply §9.4 immediately |

### §16.4 Cross-References

- [Verification & Testing §16 — Cutover validation suite](./verification-testing.md)
- [Control 2.3 — Change Management and Release Planning](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md)
- [Control 2.4 — Business Continuity and Disaster Recovery](../../../controls/pillar-2-management/2.4-business-continuity-and-disaster-recovery.md)

---

## §17 Runbook RB-07 — SOX Audit Cycle: Prove Approval Chain for Every Zone 3 Agent

**Trigger.** SOX ITGC audit cycle (typically annual + interim) requires evidence that every Zone 3 (Enterprise) agent in production was approved through the admin-gated workflow with a documented approver, justification, and template binding. Sev2 (audit-driven, scheduled).

### §17.1 Pre-Conditions

- SOX audit scope includes Agent 365 Admin Center governance (confirmed with internal audit).
- Audit window dates captured.
- Auditor evidence-format preference captured (typically: per-agent record + approval audit log + template state snapshot).

### §17.2 Procedure

1. **Enumerate Zone 3 production agents**:
   ```powershell
   $z3 = Get-Agt225InventoryExport -Format Json -Filter "zone eq ''Enterprise'' and lifecycleState eq ''Published''"
   ```
2. **For each agent, compile the approval-chain record**:
   - Agent metadata: `Get-Agt225Agent -Id <id> -ExpandApprovalHistory`
   - Approval audit: KQL filtered to `ApprovalRequest.Approved` for the agent ID
   - Template binding: `Get-Agt225TemplateStatus -AgentId <id>`
   - Custom Template Access Package binding: `Get-MgEntitlementManagementAccessPackage -AccessPackageId <id>`
3. **Identify gaps**: agents without an `ApprovalRequest.Approved` audit event are SOX exceptions and must be:
   - Documented in the SOX exception log
   - Either re-approved retroactively (with disclosed justification) or remediated (decommissioned / re-published)
4. **Produce the auditor package** in the auditor''s preferred format; include attestation by AI Governance Lead.
5. **Schedule remediation** for any exceptions before the audit close date.

### §17.3 SOX Exception Categories

| Category | Cause | Remediation |
|---|---|---|
| Migrated agent (pre-GA) | Agent existed before admin-gated workflow GA | Disclose; document migration approval date; no further action if pre-dates control effective date |
| Emergency publish (out-of-band) | Sev1 incident required immediate publish bypassing the queue | Disclose; provide IR ticket + retroactive approval record |
| Approver impersonation | Service principal used to approve (anti-pattern) | Remediate; replace with named approver; potential SOD finding |

### §17.4 Evidence Bundle

- Per-agent approval-chain records
- KQL approval audit (full scope)
- Template state snapshot
- Access Package state snapshot
- SOX exception log with remediation status
- AI Governance Lead attestation

### §17.5 Cross-References

- [Control 2.8 — Access Control and Segregation of Duties](../../../controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md)
- [Control 2.13 — Documentation and Record Keeping](../../../controls/pillar-2-management/2.13-documentation-and-record-keeping.md)
- [Control 3.3 — Compliance and Regulatory Reporting](../../../controls/pillar-3-reporting/3.3-compliance-and-regulatory-reporting.md)

---

## §X Recovery and Post-Incident Attestation

After any Sev1 or Zone-3 Sev2 incident under Control 2.25, the incident commander runs the following recovery and attestation procedure before closing the incident.

### §X.1 Recovery Verification Checklist

1. The triggering symptom is no longer reproducible (validated by re-running the relevant pillar §N.6 verification block).
2. All evidence E-01..E-08 captured to `AgentGov-Evidence-225` (or `-Sov` for sovereign tenants).
3. Pester suite for the affected pillar passes (`Invoke-Pester -Path ./tests/trg-225-NN.tests.ps1`).
4. KQL-01 (console availability) and KQL-02 (queue ingestion) return baseline metrics for the most recent 1 h bin.
5. No outstanding Microsoft service request blocking — OR open service request documented with target ETA in the incident record.
6. FINRA 3110 manual-review fallback (if activated per §3.4) is formally stood down with the registered principal''s sign-off.
7. Affected zone(s) re-validated: 10% sample of agents in the affected zone returns expected state via `Get-Agt225Agent`.

### §X.2 Post-Incident Attestation (E-09)

The incident commander (AI Governance Lead) signs the E-09 attestation:

```text
Incident: <id>
Pillar(s): <pillar codes>
Severity: <Sev1|Sev2|Sev3>
Window: <start ISO8601> to <end ISO8601>
Root cause: <RC code(s) from §N.2>
Evidence bundle: AgentGov-Evidence-225/<incident-id>/ (E-01..E-08 verified present)
Verification: §X.1 checklist all items pass; pester TRG-225-NN green
FINRA 3110 fallback: <Activated|Not activated>; if activated, stood down with registered principal sign-off on <date>
Compensating controls (if sovereign): <list>
Residual risk: <description>
Risk Register update: <Y|N>; ticket <ref>
Signed: AI Governance Lead, <name>, <date>
Counter-signed: Information Security Officer, <name>, <date>
```

The attestation is written to the immutable evidence library with a 7-year Purview retention label, **supporting** the firm''s SEC Rule 17a-4(f) and CFTC Regulation 1.31 retention obligations.

### §X.3 Attestation Refresh Cadence

- **Per-incident**: attestation written at incident close (above).
- **Quarterly**: aggregate attestation across all Sev1/Sev2 incidents in the quarter, signed by AI Governance Lead + Information Security Officer + Compliance Officer.
- **Annual**: included in the SOX ITGC audit package (RB-07).

### §X.4 Lessons-Learned Loop

Within 5 business days of incident close, the incident commander updates this troubleshooting playbook with any new symptom, root cause, or diagnostic step uncovered. The playbook''s `Updated:` and `Version:` footer fields are bumped on every such edit.

### §X.5 Cross-References

- [Control 3.4 — Incident Reporting and Root Cause Analysis](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md)
- [Verification & Testing §X — Recovery validation tests](./verification-testing.md)
- [PowerShell Setup §5 — `Invoke-Agt225EvidenceSnapshot`](./powershell-setup.md)

---

*Updated: April 2026 | Version: v1.6.2 | UI Verification Status: Current (April 2026, post-GA)*