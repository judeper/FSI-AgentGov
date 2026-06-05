# Troubleshooting — Control 2.26: Entra Agent ID Identity Governance

> **Scope.** This playbook covers operational failure modes for the Entra Agent ID identity-governance program: license / access gating, sponsor assignment and leaver handling, agent-identity access packages, lifecycle workflows for agents, quarterly access reviews of agent identities, orphan detection, SIEM forwarding, and service availability gaps. It is the diagnostic companion to the Control 2.26 specification, the portal walkthrough, the PowerShell setup pack, and the verification-testing pack.
>
> **Post-GA status (May 2026).** Microsoft Agent 365 reached general availability on May 1, 2026 and Microsoft Entra Agent ID is generally available. The pre-GA "Frontier program enrollment" gate is replaced by **Microsoft Agent 365 / Microsoft 365 E7 license assignment**. Pillar names that include "PREVIEW" or "Frontier" — for example **PREVIEW-ACCESS-MISSING** (§2) and **RB-01** (§10) — retain their pre-GA short names and anchor IDs for backward compatibility because the underlying root cause (the calling principal cannot reach the agent identity surface) is the same observable; only the gating mechanism changed. A follow-up issue tracks renaming these pillars / runbooks to license-coverage terms.
>
> **Status hedging.** The core Entra Agent ID surface is GA; some adjacent surfaces (e.g. the Lifecycle Workflows agent-sponsor tasks, the `agentSignIn` log type) remain in Public Preview. Behavior, blade names, Graph endpoints (`/beta/servicePrincipals` filtered by `servicePrincipalType eq 'Agent'`), and Lifecycle Workflow agent task templates may continue to evolve post-GA. Procedures here are written to the May 2026 surface; verify the **Last UI Verified** stamp at the top of `2.26-entra-agent-id-identity-governance.md` before treating any step as authoritative for an examiner artifact.
>
> **Regulatory framing.** Procedures support — they do not determine — compliance with FFIEC IT Handbook (Information Security, Management), OCC Bulletin 2013-29 / 2020-10 third-party risk, FRB Fed SR 26-2 (formerly SR 11-7) model risk management as applied to AI agents, NYDFS 23 NYCRR 500.7 (access privileges), and SEC 17a-4 / FINRA 4511 evidentiary retention. Implementation requires control-owner sign-off; no automated procedure removes the obligation to attest to control effectiveness.

---

## Table of contents

- [§0. Triage tree — symptom → pillar](#0-triage-tree-symptom-pillar)
- [§1. Diagnostic data collection (`Get-Agt226*` helpers, Graph queries, KQL)](#1-diagnostic-data-collection)
- [§2. Pillar PREVIEW-ACCESS-MISSING — Microsoft Agent 365 / M365 E7 license-coverage gating (post-GA semantic equivalent of the pre-GA Frontier / Copilot gate)](#2-pillar-preview-access-missing)
- [§3. Pillar SPONSOR-NULL — agent created without a human sponsor](#3-pillar-sponsor-null)
- [§4. Pillar SPONSOR-DEPARTED — sponsor leaver-event handling](#4-pillar-sponsor-departed)
- [§5. Pillar ACCESSPKG-FAIL — agent-identity access-package assignment failures](#5-pillar-accesspkg-fail)
- [§6. Pillar LIFECYCLE-NOFIRE — Lifecycle Workflow did not trigger](#6-pillar-lifecycle-nofire)
- [§7. Pillar REVIEW-MISSING-AGENTS — quarterly access review excluded agents](#7-pillar-review-missing-agents)
- [§8. Pillar ORPHAN-SCAN-EMPTY — orphan detection returns empty / stale](#8-pillar-orphan-scan-empty)
- [§9. Pillar SIEM-NO-EVENTS — Entra audit events not landing in SIEM](#9-pillar-siem-no-events)
- [§10. Runbook RB-01 — Microsoft Agent 365, M365 E7, or Microsoft 365 Copilot license expiry mid-quarter](#10-runbook-rb-01)
- [§11. Runbook RB-02 — Mass departure of a multi-agent sponsor](#11-runbook-rb-02)
- [§12. Runbook RB-03 — Examiner pulls quarterly review evidence before completion](#12-runbook-rb-03)
- [§13. Runbook RB-04 — Suspended-orphan agent past SLA](#13-runbook-rb-04)
- [§14. Runbook RB-06 — HR connector outage breaks leaver detection](#14-runbook-rb-06)
- [§15. Runbook RB-07 — Bulk re-sponsorship after reorganization](#15-runbook-rb-07)
- [§X. Recovery and post-incident attestation refresh](#x-recovery-and-post-incident-attestation-refresh)

---

## §0. Triage tree — symptom → pillar

Use this table as the first stop for any reported issue. It maps an observed symptom to the most likely pillar (and to a runbook if the symptom is high-severity or examiner-visible). Move to the matching pillar section for diagnostic queries and resolution patterns.

### 0.1 Symptom → pillar map

| # | Symptom (what the reporter said) | Most likely pillar | Severity floor | Runbook? |
|---|----------------------------------|--------------------|----------------|----------|
| S-01 | "I cannot see the **Agent identities (preview)** blade in Entra." | [§2 PREVIEW-ACCESS-MISSING](#2-pillar-preview-access-missing) | SEV-4 | — |
| S-02 | "An admin can see the blade, but **the Agent 365 control plane is empty / Researcher and Workflows agents are missing** (legacy reports phrase this as 'Frontier features greyed out')." | [§2 PREVIEW-ACCESS-MISSING](#2-pillar-preview-access-missing) | SEV-3 | [RB-01](#10-runbook-rb-01) |
| S-03 | "A new agent was registered yesterday and **has no sponsor field populated**." | [§3 SPONSOR-NULL](#3-pillar-sponsor-null) | SEV-3 | — |
| S-04 | "Quarterly orphan scan reports **dozens of agents with null sponsor**." | [§3 SPONSOR-NULL](#3-pillar-sponsor-null) | SEV-2 | — |
| S-05 | "Sponsor left the firm three weeks ago; agents **still show old sponsor**." | [§4 SPONSOR-DEPARTED](#4-pillar-sponsor-departed) | SEV-2 | [RB-02](#11-runbook-rb-02) |
| S-06 | "Sponsor departed; agents were **disabled overnight** breaking production." | [§4 SPONSOR-DEPARTED](#4-pillar-sponsor-departed) (misconfig) | SEV-1 | [RB-02](#11-runbook-rb-02) |
| S-07 | "Access package assignment to an agent **fails on a SharePoint resource**." | [§5 ACCESSPKG-FAIL](#5-pillar-accesspkg-fail) | SEV-3 | — |
| S-08 | "Access package shows **'agent identities not eligible'** error." | [§5 ACCESSPKG-FAIL](#5-pillar-accesspkg-fail) | SEV-3 | — |
| S-09 | "Lifecycle Workflow scheduled run completed but **no agent tasks fired**." | [§6 LIFECYCLE-NOFIRE](#6-pillar-lifecycle-nofire) | SEV-2 | [RB-06](#14-runbook-rb-06) |
| S-10 | "`employeeLeaveDateTime` is set on the user but **agent transfer never queued**." | [§6 LIFECYCLE-NOFIRE](#6-pillar-lifecycle-nofire) | SEV-2 | [RB-02](#11-runbook-rb-02) |
| S-11 | "Quarterly access review completed but **agent identities are not in the review pack**." | [§7 REVIEW-MISSING-AGENTS](#7-pillar-review-missing-agents) | SEV-2 | [RB-03](#12-runbook-rb-03) |
| S-12 | "Reviewer says they **only saw human users**, not agents." | [§7 REVIEW-MISSING-AGENTS](#7-pillar-review-missing-agents) | SEV-2 | [RB-03](#12-runbook-rb-03) |
| S-13 | "`Get-AgentsWithoutSponsors` returns empty but we **know agents exist**." | [§8 ORPHAN-SCAN-EMPTY](#8-pillar-orphan-scan-empty) | SEV-3 | — |
| S-15 | "SIEM dashboard for agent identity events shows **zero events for 24+ hours**." | [§9 SIEM-NO-EVENTS](#9-pillar-siem-no-events) | SEV-2 | — |
| S-16 | "SIEM is receiving `AuditLogs` but **filter on `targetResources.type eq 'Agent'` returns nothing**." | [§9 SIEM-NO-EVENTS](#9-pillar-siem-no-events) | SEV-3 | — |
| S-18 | "Reorg moved 40 agents to a new business line; **need to re-sponsor in bulk**." | [§3 SPONSOR-NULL](#3-pillar-sponsor-null) | SEV-3 | [RB-07](#15-runbook-rb-07) |
| S-19 | "An orphan agent has been suspended for **31 days** and is past the 30-day SLA." | [§4 SPONSOR-DEPARTED](#4-pillar-sponsor-departed) | SEV-2 | [RB-04](#13-runbook-rb-04) |

### 0.2 Severity matrix (Control 2.26 specific)

| Severity | Definition (this control) | Examples | Page first |
|----------|---------------------------|----------|-----------|
| **SEV-1** | Customer-facing or production agents disabled/broken; or examiner request open with no answer | S-06; mass disable from misconfigured leaver workflow; examiner asks "show me your agent inventory" and the inventory cmdlet errors | AI Governance Lead → CISO |
| **SEV-2** | Governance signal lost > 24 h; or > 5 agents in non-compliant state | S-04, S-05, S-09, S-11, S-15, S-19 | AI Governance Lead |
| **SEV-3** | Single-agent issue, control still operating in aggregate | S-02, S-03, S-07, S-08, S-13, S-16, S-18 | Entra Identity Governance Admin |
| **SEV-4** | Cosmetic / single-user UX | S-01 (one admin's view) | Entra Agent ID Admin |

**Aggravating factors that raise severity by one level:**

- The affected agent is in **Zone 3 (Enterprise)** — i.e., it touches production data or customer records.
- The issue surfaces **during an active examiner engagement** (FINRA, SEC, OCC, FRB, NYDFS) or during the 30 days preceding a scheduled exam.
- The issue affects **> 1 sponsor's portfolio** simultaneously (suggests systemic, not isolated, root cause).
- The control has already been cited or self-disclosed in a prior MRA / MRIA.

### 0.3 Pre-escalation checklist (must complete before paging on-call)

Complete all eight items before paging the AI Governance Lead or escalating beyond the owning admin. Capture the answers — examiners will ask whether triage was orderly.

1. [ ] Confirmed the issue against the **Last UI Verified** date in `2.26-entra-agent-id-identity-governance.md`. If the UI changed since, the procedure may be stale.
2. [ ] Captured the exact symptom text from the reporter (screenshot, ticket ID, time stamp in UTC).
3. [ ] Identified the affected agent(s) by `objectId` (not display name — names are not unique in preview).
4. [ ] Checked tenant health: `https://admin.microsoft.com/Adminportal/Home#/servicehealth` for "Microsoft Entra" and "Microsoft 365 Copilot" advisories.
5. [ ] Ran the **§1.2 baseline diagnostic** (`Get-Agt226Health`) and saved the JSON output to the incident folder.
6. [ ] Identified which **zone** (1 / 2 / 3) the agent is in and whether it has external-data access.
7. [ ] Confirmed the tenant context and operating cloud before applying remediation.
8. [ ] Started the **examiner artifact preservation** procedure (see §0.4) if severity is SEV-1 or SEV-2.

### 0.4 Examiner artifact preservation (mandatory for SEV-1 / SEV-2)

Examiners (FINRA, SEC, OCC, FRB, NYDFS, CFTC) routinely request "the state of the control at the time the incident was discovered." Once you start remediation, you destroy that state. Preserve it first.

1. Run `Export-Control226EvidencePackage -IncidentId <ticket> -PreRemediation` (see [`./powershell-setup.md`](./powershell-setup.md)).
2. Snapshot `AuditLogs` for the affected `objectId`s for the prior 30 days into immutable storage (Purview retention label `FSI-Examiner-Hold-7yr` per Control 8.x).
3. Capture the **current** access-package policy JSON for any package that touches the affected agents.
4. Capture Lifecycle Workflow run history (last 90 days) for any workflow with an agent task.
5. Note the operator initiating remediation, in UTC, in the incident ticket.

These five artifacts together satisfy the SEC 17a-4 / FINRA 4511 evidentiary floor for "state at time of detection."

---

## §1. Diagnostic data collection

This section defines the standard diagnostic surface for Control 2.26: a small set of `Get-Agt226*` PowerShell helpers, a Microsoft Graph query catalog, and a KQL query catalog for Entra Audit Logs forwarded to Log Analytics / Sentinel. Every pillar (§2–§10) and runbook (§10–§15) references queries from this section by ID; do not invent ad-hoc queries during an incident — use the catalog so the evidence pack remains comparable across incidents.

### 1.1 Diagnostic helper functions (`Get-Agt226*`)

Add these to your incident-response module (or import the published `FSI.AgentGov.Diagnostics` module). They wrap the cmdlets in [`./powershell-setup.md`](./powershell-setup.md) with consistent JSON output suitable for evidence preservation.

```powershell
# Get-Agt226Health — top-level snapshot. Run first on every incident.
function Get-Agt226Health {
    [CmdletBinding()]
    param(
        [string]$IncidentId,
        [string]$EvidencePath = ".\evidence"
    )
    $snap = [ordered]@{
        IncidentId       = $IncidentId
        TimestampUtc     = (Get-Date).ToUniversalTime().ToString('o')
        Tenant           = (Get-MgContext).TenantId
        Cloud            = (Get-MgContext).Environment
        AgentCount       = (Get-AllAgentIdentities).Count
        OrphanCount      = (Get-AgentsWithoutSponsors).Count
        AccessPkgCount   = (Get-AgentAccessPackageAssignments).Count
        SponsorCoverage  = (Get-AgentGovernanceSummary).SponsorCoveragePct
        FrontierEnabled  = (Get-MgBetaAdminMicrosoft365CopilotSetting -ErrorAction SilentlyContinue).FrontierProgramEnabled
    }
    $out = $snap | ConvertTo-Json -Depth 5
    if ($IncidentId) {
        New-Item -ItemType Directory -Force -Path $EvidencePath | Out-Null
        $out | Out-File "$EvidencePath\$IncidentId-health.json"
    }
    $snap
}
```

```powershell
# Get-Agt226Agent — full posture for one agent (objectId).
function Get-Agt226Agent {
    [CmdletBinding()]
    param([Parameter(Mandatory)][string]$ObjectId)
    $sp = Get-MgBetaServicePrincipal -ServicePrincipalId $ObjectId -ErrorAction Stop
    $sponsor = $sp.AdditionalProperties['sponsor']
    [ordered]@{
        ObjectId          = $sp.Id
        DisplayName       = $sp.DisplayName
        SpnType           = $sp.AdditionalProperties['servicePrincipalType']
        AppId             = $sp.AppId
        SponsorUpn        = $sponsor
        SponsorObjectId   = if ($sponsor) { (Get-MgUser -UserId $sponsor -ErrorAction SilentlyContinue).Id } else { $null }
        SponsorEnabled    = if ($sponsor) { (Get-MgUser -UserId $sponsor -ErrorAction SilentlyContinue).AccountEnabled } else { $null }
        SponsorLeaveDate  = if ($sponsor) { (Get-MgUser -UserId $sponsor -Property employeeLeaveDateTime -ErrorAction SilentlyContinue).EmployeeLeaveDateTime } else { $null }
        AccessPackages    = (Get-AgentAccessPackageAssignments | Where-Object AgentObjectId -eq $ObjectId).PackageName
        CreatedDateTime   = $sp.AdditionalProperties['createdDateTime']
        Suspended         = -not $sp.AccountEnabled
    }
}
```

```powershell
# Get-Agt226SponsorImpact — list every agent owned by one sponsor.
# Use before any sponsor leaver action to size the blast radius.
function Get-Agt226SponsorImpact {
    [CmdletBinding()]
    param([Parameter(Mandatory)][string]$SponsorUpn)
    Get-AllAgentIdentities |
        Where-Object { $_.AdditionalProperties['sponsor'] -eq $SponsorUpn } |
        Select-Object Id, DisplayName, @{n='Zone';e={$_.AdditionalProperties['governanceZone']}}, AccountEnabled
}
```

```powershell
# Get-Agt226LifecycleStatus — last N runs of any agent-tagged Lifecycle Workflow.
function Get-Agt226LifecycleStatus {
    [CmdletBinding()]
    param([int]$Last = 10)
    Get-MgBetaIdentityGovernanceLifecycleWorkflow |
        Where-Object { $_.Category -eq 'leaver' -and $_.DisplayName -match 'agent' } |
        ForEach-Object {
            $wf = $_
            Get-MgBetaIdentityGovernanceLifecycleWorkflowRun -LifecycleWorkflowId $wf.Id -Top $Last |
                Select-Object @{n='Workflow';e={$wf.DisplayName}}, Id, Status, StartedDateTime, CompletedDateTime, FailedTasksCount
        }
}
```

```powershell
# Get-Agt226ReviewCoverage — verify the active quarterly access review includes agents.
function Get-Agt226ReviewCoverage {
    [CmdletBinding()] param()
    Get-MgBetaIdentityGovernanceAccessReviewDefinition |
        Where-Object { $_.DisplayName -match 'agent|quarterly' -and $_.Status -in @('InProgress','NotStarted') } |
        Select-Object Id, DisplayName, Status,
            @{n='ScopePrincipalTypes';e={$_.Scope.PrincipalScopes.Query}},
            @{n='IncludesAgents';e={$_.Scope.PrincipalScopes.Query -match "servicePrincipalType eq 'Agent'" -or
                                    $_.Scope.PrincipalScopes.QueryRoot -match 'servicePrincipals'}}
}
```

> **Note.** The `Get-Agt226*` helpers are diagnostic — they read state. They do not write. Any remediation must be done with the `Set-` / `Update-` cmdlets in `./powershell-setup.md` (under the principle that diagnostic and remediation operators are separable for audit).

### 1.2 Microsoft Graph query catalog

| ID | Purpose | Endpoint | Notes |
|----|---------|----------|-------|
| GQ-01 | List all agent identities | `GET /beta/servicePrincipals?$filter=servicePrincipalType eq 'Agent'&$select=id,displayName,appId,accountEnabled,additionalProperties` | Beta only as of April 2026 |
| GQ-02 | Single agent + sponsor expansion | `GET /beta/servicePrincipals/{id}?$select=id,displayName,additionalProperties` then resolve `additionalProperties.sponsor` (UPN) via `GET /v1.0/users/{upn}` | Sponsor is a UPN string in `additionalProperties`, not a navigation property |
| GQ-03 | Agents created in last 24 h | `GET /beta/servicePrincipals?$filter=servicePrincipalType eq 'Agent' and createdDateTime ge {iso}` | Use to confirm registration of a new agent |
| GQ-04 | Sponsor employeeLeaveDateTime | `GET /v1.0/users/{upn}?$select=id,accountEnabled,employeeLeaveDateTime` | HR connector populates `employeeLeaveDateTime`; absence ≠ active |
| GQ-05 | Lifecycle Workflow runs (leaver) | `GET /beta/identityGovernance/lifecycleWorkflows/workflows/{id}/runs?$top=20&$orderby=startedDateTime desc` | Filter `status` for `failed` |
| GQ-06 | Access package assignments touching agents | `GET /beta/identityGovernance/entitlementManagement/assignments?$filter=target/objectType eq 'servicePrincipal'&$expand=accessPackage` | Returns 0 if access packages were not enabled for agent identities ("All agents (preview)" toggle off) |
| GQ-07 | Active access reviews | `GET /beta/identityGovernance/accessReviews/definitions?$filter=status eq 'InProgress'` | Inspect `scope.principalScopes.query` to see if `Agent` SPN type is included |
| GQ-08 | Audit events for one agent (last 7 d) | `GET /v1.0/auditLogs/directoryAudits?$filter=targetResources/any(t:t/id eq '{objectId}')&$top=200` | `targetResources.type` is `'ServicePrincipal'` (not `'Agent'`) — see [§9](#9-pillar-siem-no-events) |

### 1.3 KQL query catalog (Entra Audit Logs in Sentinel / Log Analytics)

> Diagnostic settings export Entra Audit Logs at the **category** level (`AuditLogs`); Microsoft does not provide per-event filtering at the diagnostic-settings layer. All event-shape filtering happens in your SIEM / Log Analytics workspace **downstream** of the export. If you do not see expected events, see [§9](#9-pillar-siem-no-events) before assuming a gap upstream.

```kusto
// KQL-01 — All agent-identity audit events in last 24 h
AuditLogs
| where TimeGenerated > ago(24h)
| extend tr = parse_json(TargetResources)
| mv-expand tr
| where tostring(tr.type) == "ServicePrincipal"
| extend spType = tostring(parse_json(tostring(tr.modifiedProperties))[0].newValue)
| where spType has "Agent" or OperationName has "agent"
| project TimeGenerated, OperationName, Result, InitiatedBy, tr.id, tr.displayName
```

```kusto
// KQL-02 — Agents created without a sponsor (look-back 30 d)
AuditLogs
| where TimeGenerated > ago(30d)
| where OperationName == "Add service principal"
| extend tr = parse_json(TargetResources)
| mv-expand tr
| where tostring(tr.type) == "ServicePrincipal"
| extend props = tostring(tr.modifiedProperties)
| where props !has "\"sponsor\""
| project TimeGenerated, tr.id, tr.displayName, InitiatedBy
```

```kusto
// KQL-03 — Sponsor reassignment events (manager auto-transfer)
AuditLogs
| where OperationName in ("Update service principal", "Set sponsor")
| extend mp = parse_json(TargetResources)[0].modifiedProperties
| mv-expand mp
| where tostring(mp.displayName) == "sponsor"
| project TimeGenerated, OldSponsor=tostring(mp.oldValue), NewSponsor=tostring(mp.newValue), InitiatedBy
```

```kusto
// KQL-04 — Lifecycle Workflow agent task failures
AuditLogs
| where Category == "WorkflowsLifecycleManagement"
| where Result == "failure"
| where AdditionalDetails has "agent" or TargetResources has "ServicePrincipal"
| project TimeGenerated, OperationName, ResultReason, AdditionalDetails
```

```kusto
// KQL-05 — Access package assignment failures targeting agents
AuditLogs
| where Category == "EntitlementManagement"
| where OperationName has_any ("Fulfill access package assignment request", "create assignment")
| where Result == "failure"
| extend tr = parse_json(TargetResources)
| mv-expand tr
| where tostring(tr.type) == "ServicePrincipal"
| project TimeGenerated, OperationName, ResultReason, tr.id, tr.displayName
```

### 1.4 Evidence-floor for any 2.26 incident (E-01 .. E-09)

| ID | Artifact | Source | Retention label |
|----|----------|--------|-----------------|
| E-01 | `Get-Agt226Health` JSON snapshot at detection | §1.1 | `FSI-Examiner-Hold-7yr` |
| E-02 | `Get-Agt226Agent` for each affected agent | §1.1 | `FSI-Examiner-Hold-7yr` |
| E-03 | KQL-01..05 result CSV exports for the incident window | §1.3 | `FSI-Examiner-Hold-7yr` |
| E-04 | Access-package policy JSON (pre-remediation) | Graph `/beta/identityGovernance/entitlementManagement/accessPackages/{id}` | `FSI-Examiner-Hold-7yr` |
| E-05 | Lifecycle Workflow definition + last 5 runs | §1.1 `Get-Agt226LifecycleStatus` | `FSI-Examiner-Hold-7yr` |
| E-06 | Active access review definition + scope | §1.1 `Get-Agt226ReviewCoverage` | `FSI-Examiner-Hold-7yr` |
| E-07 | Sponsor `employeeLeaveDateTime` value at detection | GQ-04 | `FSI-Examiner-Hold-7yr` |
| E-08 | Tenant cloud + license posture (Copilot + Agent 365 / M365 E7) | `Get-Agt226Health.FrontierEnabled` (field name retained for backward-compat — value reflects Agent ID API surface reachability) + license assignment report | `FSI-Examiner-Hold-7yr` |
| E-09 | Operator identity + UTC timestamp of every remediation step | Incident ticket / change record | `FSI-Examiner-Hold-7yr` |

`Export-Control226EvidencePackage -IncidentId <id>` bundles E-01 through E-08 automatically. E-09 is captured in the incident ticket by the operator.

---

## §2. Pillar PREVIEW-ACCESS-MISSING

<a id="frontier-enrolled-but-blade-403"></a>
<a id="all-agents-preview-missing"></a>

> **Namespace name retained for backward-compatibility.** Pre-GA, this pillar covered Frontier enrollment + Copilot license gaps. Post-GA (May 2026), it covers **Microsoft Agent 365 / Microsoft 365 E7 license-assignment gaps** and **RBAC gaps** that surface as missing-blade or empty-blade symptoms. The pillar name and section anchors are preserved across the GA cutover so existing runbook references continue to resolve.

**One-line:** the **Agent identities** blade is invisible, partially populated, or rejects actions because post-GA prerequisites (license + RBAC) are not met for the tenant or the operator.

### 2.1 Symptom catalog

| Code | Symptom | First responder |
|------|---------|-----------------|
| P2-S1 | Blade not present in left nav under Entra → Identity | Entra Agent ID Admin |
| P2-S2 | Blade present, "feature unavailable" or license banner | AI Administrator |
| P2-S3 | Blade present, no agents listed (empty grid), tenant clearly has agents | Entra Agent ID Admin |
| P2-S4 | Operation "Create access package for agents" greyed out | Entra Identity Governance Admin |
| P2-S5 | Graph `/beta/servicePrincipals?$filter=servicePrincipalType eq 'Agent'` returns 400 / 501 | AI Administrator |

### 2.2 Root cause matrix

| RC | Description | Likelihood | How to confirm |
|----|-------------|-----------|----------------|
| RC-A | Operator missing **Microsoft Agent 365** or **Microsoft 365 E7** license | High (most common post-GA) | M365 admin center → Users → operator → Licenses; Agent 365 or M365 E7 must be assigned (group-based works) |
| RC-B | Tenant has no available Agent 365 / M365 E7 SKUs to assign | Medium | M365 admin center → Billing → Your products; if not listed, contact account team to procure |
| RC-C | Operator missing the **Entra Agent ID Admin** or **AI Administrator** directory role | Medium | `Get-MgRoleManagementDirectoryRoleAssignment -Filter "principalId eq '{id}'"` |
| RC-E | Adjacent surface (e.g., the assignment-policy toggle still labelled "(preview)") rolled back transiently by Microsoft (service advisory) | Low | Service Health → Entra advisories |
| RC-F | Conditional Access policy blocking access to the Agent ID admin endpoint | Low | Sign-in logs → operator → filter app `Microsoft Entra Admin Center` |

> **Important.** RC-A and RC-C are independent gates and **both** must be satisfied. A licensed operator without the Agent ID Admin role will still appear "broken." Confirm both before deeper diagnostics. **If the tenant historically relied on the pre-GA Frontier enrollment pattern,** the GA cutover removed that requirement — a "Frontier disabled" state is no longer a prerequisite gap; the equivalent post-GA gap is missing Agent 365 / M365 E7 license assignment (RC-A / RC-B).

### 2.3 Diagnostic queries

```powershell
# Quick check (post-GA: FrontierEnabled field reflects Agent ID API reachability,
# not the historical Frontier program flag — name retained for backward-compat)
Get-Agt226Health | Select Cloud, FrontierEnabled, AgentCount

# Operator license check (post-GA: prefer Agent 365 / M365 E7; transitional Copilot match retained)
Get-MgUserLicenseDetail -UserId <operator-upn> |
  Where-Object { $_.SkuPartNumber -match 'Microsoft_Agent_365|M365_E7|COPILOT|M365_COPILOT' }

# Operator role check
Get-MgRoleManagementDirectoryRoleAssignment -Filter "principalId eq '<operator-objectId>'" |
  ForEach-Object { Get-MgRoleManagementDirectoryRoleDefinition -UnifiedRoleDefinitionId $_.RoleDefinitionId } |
  Select DisplayName
```

Graph: GQ-01 returning 400/404 → operating principal lacks Microsoft Agent 365 / M365 E7 license coverage (post-GA gating); returning 200 with empty result → license is provisioned but role / RBAC gating on operator only.

### 2.4 Resolution steps

1. Confirm `Cloud` = `Global`.
2. Have an **Entra Global Admin** verify the operating principal has **Microsoft Agent 365** (standalone) or **Microsoft 365 E7** ("Frontier Suite") license assignment active in M365 admin center → Billing → Licenses. Capture the assignment record (date, SKU part number, assigning admin's UPN) for E-08.
3. Assign / verify the affected operator has a Microsoft 365 Copilot license. Group-based assignment is supported; verify license **provisioning status** is `Success`, not `PendingProvisioning`.
4. Assign the **Entra Agent ID Admin** role (preferred; least-privilege) or **AI Administrator** (broader). Avoid Global Admin for routine operation.
5. Operator must sign out and back in (token refresh) before the blade appears. If still missing after 15 minutes, clear browser cache and retry.
6. If Conditional Access is suspected (RC-F), have the Entra Security Admin add the operator to a CA exclusion test group temporarily, retry, then remove the exclusion and adjust policy.

### 2.5 Verification

- `Get-Agt226Health` returns `FrontierEnabled = True` and `AgentCount > 0` (assuming agents exist).
- Pester: `Describe 'Control 2.26 — Preview Gating'` → `It 'has Agent ID API surface reachable in commercial tenants'` and `It 'admins have Agent ID Admin role'` should now pass. See [`./verification-testing.md`](./verification-testing.md).

### 2.6 Cross-links

- Portal: [`./portal-walkthrough.md`](./portal-walkthrough.md) §2 — Microsoft Agent 365 / M365 E7 License Assignment.
- PowerShell: [`./powershell-setup.md`](./powershell-setup.md) §2 — Role assignment helpers.

### 2.7 Examiner artifact preservation

Capture E-01 (`Get-Agt226Health`) and E-08 (Agent 365 / M365 E7 license assignment record) before changing tenant-level license posture. License changes are tenant-wide and affect every Copilot-licensed user; do not remediate without change-record approval.

---

## §3. Pillar SPONSOR-NULL

<a id="sponsor-field-readonly"></a>

**One-line:**an agent identity exists with no value in `additionalProperties.sponsor`, breaking accountability and making the agent invisible to leaver-driven Lifecycle Workflows.

### 3.1 Symptom catalog

| Code | Symptom | First responder |
|------|---------|-----------------|
| P3-S1 | Single new agent reported with empty Sponsor column in portal | Entra Agent ID Admin |
| P3-S2 | Quarterly orphan scan returns ≥ 5 agents | AI Governance Lead |
| P3-S3 | Agent created via API / SDK (CI pipeline) consistently sponsorless | AI Administrator |
| P3-S4 | Reorganization moved 30+ agents; old sponsors disabled, new sponsor not yet set | AI Governance Lead |

### 3.2 Root cause matrix

| RC | Description | Likelihood | Confirm |
|----|-------------|-----------|---------|
| RC-A | Agent registered via Power Platform / Microsoft Copilot Studio before sponsor field was added (legacy) | High in tenants that adopted preview early | Created date < Agent ID GA cutover (May 1, 2026) or pre-GA Frontier enable date for tenants that participated in early access |
| RC-B | Service-principal create script omits the `sponsor` claim | High (CI pipelines) | Inspect the create call payload |
| RC-C | Sponsor specified a **disabled** or **deleted** UPN (silently dropped) | Medium | `Get-MgUser -UserId <upn>` returns 404 or `AccountEnabled=False` |
| RC-D | Bulk reorg invalidated existing sponsor assignments | Situational | Recent `employeeLeaveDateTime` clusters in HR feed |
| RC-E | Custom registration tool not updated for preview schema | Medium | Inspect tool version |

### 3.3 Diagnostic queries

```powershell
# Enumerate orphans
Get-AgentsWithoutSponsors | Format-Table Id, DisplayName, CreatedDateTime

# Cohort by creation date — does the orphan cluster line up with a tool/process change?
Get-AgentsWithoutSponsors |
  Group-Object { ([datetime]$_.AdditionalProperties['createdDateTime']).ToString('yyyy-MM') } |
  Select Name, Count
```

KQL-02 returns historical orphan-create events; correlate with deployment changes.

### 3.4 Resolution steps

1. Run `Get-AgentsWithoutSponsors | Export-Csv .\orphans.csv` and freeze the list as evidence (E-02 per row).
2. For each orphan, identify the **business owner** from the agent registry (Control 1.2 inventory). The agent registry is the source of truth — never invent a sponsor from `createdBy`, which is often a service account.
3. Use `Set-AgentSponsorBulk -CsvPath .\orphans-with-sponsors.csv -WhatIf` to preview, then re-run without `-WhatIf` after AI Governance Lead approval.
4. For RC-B / RC-E (tooling), open a change to update the registration code to require `sponsor` as a non-null parameter; add a Pester test that fails when sponsor is null at creation.
5. For RC-C, escalate to HR / IDM team to clean the registry of disabled UPNs.

### 3.5 Verification

- `Get-AgentsWithoutSponsors` returns zero rows for the remediated cohort.
- Pester: `It 'no agent identities without a sponsor'` passes.
- KQL-03 shows reassignment events with `InitiatedBy` matching the operator who ran `Set-AgentSponsorBulk`.

### 3.6 Cross-links

- Portal: [`./portal-walkthrough.md`](./portal-walkthrough.md) §2 — Sponsor assignment.
- PowerShell: [`./powershell-setup.md`](./powershell-setup.md) §3 — `Set-AgentSponsorBulk`.

## §4. Pillar SPONSOR-DEPARTED

**One-line:** the human sponsor of one or more agents has left (or is leaving) the firm; the question is whether the **manager auto-transfer** built into the Lifecycle Workflow agent leaver task fired correctly, and — critically — whether anyone misconfigured the workflow to **disable** agents on sponsor departure (which is *not* the supported default and creates production-impact incidents like S-06).

> **Critical accuracy point.** The Microsoft-provided default behavior on a sponsor's `employeeLeaveDateTime` is to **automatically transfer agent sponsorship to the sponsor's manager** (resolved via the `manager` user property). Suspension or disablement of the agent only fires when (a) the manager affirmatively declines reassignment via the workflow's manager-task UI, **and** (b) reassignment fails within the configured SLA (default 30 days). If you observe agents being disabled the moment a sponsor is offboarded, the workflow has been customized (or a custom logic-app handler has replaced the default task) and that customization is the bug — not Entra behavior.

### 4.1 Symptom catalog

| Code | Symptom | First responder |
|------|---------|-----------------|
| P4-S1 | Agents still show old (disabled) sponsor weeks after departure | AI Governance Lead |
| P4-S2 | Manager received task notification but no transfer occurred | Entra Identity Governance Admin |
| P4-S3 | **Agents disabled overnight when sponsor offboarded** (production impact) | Entra Agent ID Admin → escalate SEV-1 |
| P4-S4 | Manager declined; agent in suspended-orphan state and approaching 30-day SLA | AI Governance Lead |
| P4-S5 | Sponsor's manager itself is disabled — transfer target invalid | AI Governance Lead |

### 4.2 Root cause matrix

| RC | Description | Likelihood | Confirm |
|----|-------------|-----------|---------|
| RC-A | Lifecycle Workflow leaver template not enabled or scope excludes sponsor | High for P4-S1, P4-S2 | `Get-Agt226LifecycleStatus`; check workflow `executionConditions` |
| RC-B | HR connector did not write `employeeLeaveDateTime` (see §6) | High | GQ-04 |
| RC-C | Workflow customized to **disable** instead of transfer (misconfig) | High for P4-S3 | Inspect workflow tasks for `disableUserAccount` on the agent target |
| RC-D | Sponsor's manager attribute is null or points to a disabled user | Medium | `Get-MgUser -UserId <sponsor-upn> -Property manager -ExpandProperty manager` |
| RC-E | Manager declined transfer in the workflow UI; SLA timer running | Medium | KQL-04 + workflow run details |
| RC-F | Sponsor was a contractor whose departure was never recorded in HR | Low–Medium | HR record absent |

### 4.3 Diagnostic queries

```powershell
# Map the sponsor's blast radius first — never act blind
Get-Agt226SponsorImpact -SponsorUpn <departing-sponsor-upn>

# Verify the manager chain target
Get-MgUser -UserId <sponsor-upn> -Property manager,employeeLeaveDateTime -ExpandProperty manager |
  Select UserPrincipalName, EmployeeLeaveDateTime, @{n='Manager';e={$_.Manager.AdditionalProperties['userPrincipalName']}}

# Workflow runs for this leaver
Get-Agt226LifecycleStatus -Last 5
```

KQL-03 (sponsor reassignment) and KQL-04 (lifecycle task failures) — both for the incident window.

### 4.4 Resolution steps

**For P4-S1 / P4-S2 (no transfer occurred):**

1. Confirm the workflow has fired (`Get-Agt226LifecycleStatus`). If not, jump to [§6 LIFECYCLE-NOFIRE](#6-pillar-lifecycle-nofire).
2. If the workflow ran but produced no agent-task action, inspect `executionConditions` — the scope query must include the agents owned by the leaver. The default Microsoft template scopes by sponsor UPN; custom templates may scope differently.
3. If RC-D (manager null/disabled), have HR populate or correct the manager attribute, then **re-trigger the workflow on demand** for the affected user via Entra → Identity Governance → Lifecycle Workflows → "Run on demand."
4. If RC-F (no HR record), set `employeeLeaveDateTime` manually on the user record (Entra Identity Governance Admin) only with documented HR / People-Ops approval. This is an out-of-band action; preserve the approval record as E-09.

**For P4-S3 (agents disabled — SEV-1):**

1. **Stop the workflow immediately** (pause schedule, do not delete — preserve evidence) to prevent additional agents being disabled.
2. Re-enable the affected agents via `Update-MgBetaServicePrincipal -ServicePrincipalId <id> -AccountEnabled:$true` after AI Governance Lead approval. Document each re-enable in the incident ticket.
3. Notify business owners / sponsors-of-record that their agents are back online; expect downstream effects (queued requests, retried integrations).
4. Open a high-priority remediation ticket to refactor the workflow back to the supported manager-transfer pattern. Add a Pester guard that fails build if any leaver workflow targeting agents includes a `disableUserAccount` task.

**For P4-S4 (manager declined, SLA approaching):**

1. Follow [RB-04](#13-runbook-rb-04).

### 4.5 Verification

- After remediation, `Get-Agt226Agent -ObjectId <id>` shows the new sponsor UPN and `Suspended = False`.
- KQL-03 records a reassignment with `NewSponsor` matching the manager's UPN.
- Pester: `It 'no agents disabled by leaver workflow'` and `It 'all agents have an enabled sponsor'` pass.

### 4.6 Cross-links

- Portal: [`./portal-walkthrough.md`](./portal-walkthrough.md) §5 — Lifecycle Workflow.
- PowerShell: [`./powershell-setup.md`](./powershell-setup.md) §5.
- Runbooks: [RB-02](#11-runbook-rb-02), [RB-04](#13-runbook-rb-04), [RB-06](#14-runbook-rb-06).

### 4.7 Examiner artifact preservation

Capture E-05 (workflow definition + last 5 runs) **before** pausing or modifying the workflow. The workflow definition history, not the current state, is what an examiner will ask for if there is any production-disable incident.

---

## §5. Pillar ACCESSPKG-FAIL

<a id="expired-but-grant-persists"></a>
<a id="auto-apply-stuck"></a>
<a id="provisioning-quarantine"></a>

**One-line:**an Entitlement Management access package fails to provision or assign to an agent identity, blocking the package-based pattern that Control 2.26 specifies for granting agents resource access.

### 5.1 Symptom catalog

| Code | Symptom | First responder |
|------|---------|-----------------|
| P5-S1 | Assignment request errors "agent identities not eligible" | Entra Identity Governance Admin |
| P5-S2 | Assignment succeeds but agent receives no SharePoint access | Entra Identity Governance Admin |
| P5-S3 | Catalog does not show the "Allow agent identities" toggle | Entra Identity Governance Admin |
| P5-S4 | Assignment fulfillment hung in `delivering` state > 1 hour | Entra Identity Governance Admin |
| P5-S5 | Bulk re-assignment after access-package edit drops some agents | AI Governance Lead |

### 5.2 Root cause matrix

| RC | Description | Likelihood | Confirm |
|----|-------------|-----------|---------|
| RC-A | "All agents (preview)" toggle off on the access package policy | High for P5-S1 | Inspect policy; toggle is per-policy, not per-package |
| RC-B | **SharePoint resource added directly to the package** — unsupported for agent identities | High for P5-S2 | Inspect package resources; SharePoint sites cannot be granted to agent SPNs directly |
| RC-C | Catalog is owned by a service account lacking the AI Administrator role | Medium for P5-S3 | Catalog → Roles & administrators |
| RC-D | Resource directory role (e.g., on a group) requires PIM activation that the package does not request | Medium for P5-S4 | Group → Roles |
| RC-E | Operating principal lacks Microsoft Agent 365 / M365 E7 license coverage (overrides) | Low–Medium | §2 |
| RC-F | Bulk edit changed package policy ID, orphaning prior assignments | Low for P5-S5 | Compare policy IDs in audit log |

> **Critical accuracy point — SharePoint resources.** Access packages do not directly support SharePoint site resources for agent identities (preview, April 2026). The supported pattern is: create a security group → grant SharePoint site permission to the group → add the **group** as the resource on the access package. Assigning the package then puts the agent identity into the group, which carries the SharePoint permission transitively. Documentation that suggests adding SharePoint sites directly to packages for agents is wrong for this preview surface.

### 5.3 Diagnostic queries

```powershell
# All agent-touching packages
Get-AgentAccessPackageAssignments | Group-Object PackageName | Select Name, Count

# Inspect a specific package policy
$pkg = Get-MgBetaEntitlementManagementAccessPackage -Filter "displayName eq '<name>'"
Get-MgBetaEntitlementManagementAccessPackageAssignmentPolicy -AccessPackageId $pkg.Id |
  Select Id, DisplayName, @{n='AllowsAgents';e={$_.RequestorSettings.AllowedTargetScope -match 'agent' -or $_.AdditionalProperties['allowAgentIdentities']}}

# Resources on the package
Get-MgBetaEntitlementManagementAccessPackageResource -AccessPackageId $pkg.Id |
  Select OriginSystem, ResourceType, DisplayName
```

KQL-05 enumerates failure events.

### 5.4 Resolution steps

1. Confirm RC-A first — flip the "All agents (preview)" toggle on the policy and resubmit one assignment as a test before bulk retry.
2. For RC-B (SharePoint), refactor the package: remove the SharePoint resource, create or reuse a security group, grant the group the needed SharePoint permission, add the group to the package. Re-issue assignments. Communicate to package owners that this is an indirection — they should document it in the package description.
3. For RC-D, set the package policy to request PIM activation as part of fulfillment, or pre-activate the group's directory role.
4. For RC-F, restore the prior policy from the snapshot in E-04 and reapply edits incrementally.

### 5.5 Verification

- Test agent receives expected resources after assignment (validate SharePoint access via Graph site permission listing).
- Pester: `It 'access packages targeting agents do not include SharePoint resources directly'` passes.

### 5.6 Cross-links

- Portal: [`./portal-walkthrough.md`](./portal-walkthrough.md) §3, §4 — Catalog and access package.
- PowerShell: [`./powershell-setup.md`](./powershell-setup.md) §4.

## §6. Pillar LIFECYCLE-NOFIRE

<a id="lifecycle-workflow-failed-permission"></a>

**One-line:**the Lifecycle Workflow that should drive sponsor leaver/transfer logic for agents did not execute, or executed and skipped its agent-task subtree.

### 6.1 Symptom catalog

| Code | Symptom | First responder |
|------|---------|-----------------|
| P6-S1 | Scheduled run completed; zero agent tasks fired | Entra Identity Governance Admin |
| P6-S2 | `employeeLeaveDateTime` set; no run picked up the user | Entra Identity Governance Admin |
| P6-S3 | Run shows `failed` with cryptic error | Entra Identity Governance Admin |
| P6-S4 | Workflow paused / disabled by mistake | Entra Identity Governance Admin |
| P6-S5 | Run history empty for > 7 days | Entra Identity Governance Admin |

### 6.2 Root cause matrix

| RC | Description | Likelihood | Confirm |
|----|-------------|-----------|---------|
| RC-A | HR connector not writing `employeeLeaveDateTime` (upstream gap) | High for P6-S2 | GQ-04 returns null for known leavers |
| RC-B | Workflow `executionConditions` query excludes the user (e.g., scope by department that doesn't match) | High for P6-S1 | Inspect workflow JSON |
| RC-C | Workflow disabled (`isEnabled = false`) | Medium for P6-S4, P6-S5 | `Get-MgBetaIdentityGovernanceLifecycleWorkflow` |
| RC-D | Schedule misconfigured — daily schedule paused or pointed to a future-only date | Medium | Inspect `executionConditions.scope` and trigger schedule |
| RC-E | Throttling — large tenants may delay runs by hours under load | Low | Service Health |
| RC-F | Permission gap on the workflow's managed identity to read user attributes | Low | Workflow → Identity → role assignments |

### 6.3 Diagnostic queries

```powershell
Get-Agt226LifecycleStatus -Last 20 | Sort StartedDateTime -Descending

# Did the connector write the attribute?
Get-MgUser -UserId <leaver-upn> -Property employeeLeaveDateTime, employeeHireDate
```

KQL-04 lifecycle task failures.

### 6.4 Resolution steps

1. Confirm `employeeLeaveDateTime` is populated (RC-A). If null, escalate to HR / IDM team to fix the connector. Do not work around by manually setting the attribute en masse — that destroys the audit chain showing HR as the source of truth.
2. Confirm the workflow is `isEnabled = true` and the schedule is active.
3. Validate `executionConditions` — run the workflow's scope query manually:

   ```powershell
   $wf = Get-MgBetaIdentityGovernanceLifecycleWorkflow -LifecycleWorkflowId <id>
   # Replicate the rule. Example: scope = "company eq 'Contoso' and employeeLeaveDateTime ge 2026-01-01"
   Get-MgUser -Filter "<rule>" -ConsistencyLevel eventual -CountVariable cnt | Measure-Object
   ```

   If the count returns the expected leavers, the rule is fine and the issue is upstream / engine-side; otherwise, fix the rule.
4. For RC-F, grant the workflow's managed identity `User.Read.All` and the agent-tasks-required scopes per Microsoft Learn.
5. Trigger an on-demand run for the affected user and validate task fired in run history.

### 6.5 Verification

- Run history shows a successful `processed` task for the affected user with an agent-transfer subtask.
- Pester: `It 'lifecycle workflow processed all leavers in last 30 days'` passes.

### 6.6 Cross-links

- Portal: [`./portal-walkthrough.md`](./portal-walkthrough.md) §5.
- PowerShell: [`./powershell-setup.md`](./powershell-setup.md) §5.
- Runbooks: [RB-06](#14-runbook-rb-06).

### 6.7 Examiner artifact preservation

Preserve E-05 (workflow + last 5 runs) and E-07 (`employeeLeaveDateTime`). HR connector outage incidents will be referenced for years if cited in MRA — keep the connector vendor's incident ticket alongside Entra evidence.

---

## §7. Pillar REVIEW-MISSING-AGENTS

**One-line:** a quarterly access review completed without including agent identities in scope, leaving an evidence gap for the period.

### 7.1 Symptom catalog

| Code | Symptom | First responder |
|------|---------|-----------------|
| P7-S1 | Reviewer reports they only saw human users | Compliance Officer |
| P7-S2 | Review pack zero agent rows; tenant has > 50 agents | AI Governance Lead |
| P7-S3 | Review scoped to specific access packages — agent-only packages omitted | Entra Identity Governance Admin |
| P7-S4 | New review series created post-onboarding does not auto-include agents | Entra Identity Governance Admin |

### 7.2 Root cause matrix

| RC | Description | Likelihood | Confirm |
|----|-------------|-----------|---------|
| RC-A | Review scope query filters `userType` and excludes service principals (entitlement vs object scope mismatch) | High | Inspect `scope.principalScopes.query` |
| RC-B | Review template chosen ("guests only," "all users") doesn't include SPNs | High | Template name in definition |
| RC-C | Review created before agent identity preview — never refreshed | Medium | Definition `createdDateTime` |
| RC-D | Reviewer's Entra role lacks `EntitlementManagement.Read.All` for SPN principals | Low–Medium | Reviewer role |

### 7.3 Diagnostic queries

```powershell
Get-Agt226ReviewCoverage | Format-Table DisplayName, Status, IncludesAgents
```

GQ-07 + inspect `scope.principalScopes.query` for `servicePrincipalType eq 'Agent'`.

### 7.4 Resolution steps

1. If a review is **in progress** and excludes agents: do **not** modify the running review (mutating mid-cycle compromises evidence). Instead, create a parallel **supplemental** review explicitly scoped to agents covering the same period, and document the supplement in the review pack.
2. If a review is **completed** and excludes agents: open a finding under Control 2.26 (self-disclosure), launch a remediation review with explicit agent scope, and notify Compliance to flag the period in the next attestation.
3. Edit the review **template** for future cycles to include `or servicePrincipalType eq 'Agent'` in the scope query.
4. Confirm reviewers have correct roles to enumerate SPN-scoped assignments.

### 7.5 Verification

- New / supplemental review definition `IncludesAgents = True`.
- Pester: `It 'every active access review with quarterly cadence includes agents'` passes.

### 7.6 Cross-links

- Portal: [`./portal-walkthrough.md`](./portal-walkthrough.md) §6 — Quarterly reviews.
- Runbook: [RB-03](#12-runbook-rb-03).

### 7.7 Examiner artifact preservation

Preserve E-06 (active review definition). If the firm needs to re-run a supplemental review, the original definition justifies the gap and the supplement closes it — both are needed in the workpaper.

---

## §8. Pillar ORPHAN-SCAN-EMPTY

<a id="diagnostic-no-data"></a>

**One-line:**`Get-AgentsWithoutSponsors` (or the equivalent Graph query) returns empty when agents clearly exist, masking real orphans.

### 8.1 Symptom catalog

| Code | Symptom | First responder |
|------|---------|-----------------|
| P8-S1 | Cmdlet returns empty; portal shows orphan badge on agents | Entra Agent ID Admin |
| P8-S3 | Cmdlet returns inconsistent counts across runs within minutes | Entra Agent ID Admin |
| P8-S4 | Cmdlet errors with `Insufficient privileges` | Entra Agent ID Admin |

### 8.2 Root cause matrix

| RC | Description | Likelihood | Confirm |
|----|-------------|-----------|---------|
| RC-A | Operator's Graph context missing `Application.Read.All` / `Directory.Read.All` | High | `Get-MgContext \| Select Scopes` |
| RC-C | Beta endpoint cache lag (Microsoft cache invalidation up to 15 min) | Medium for P8-S3 | Re-run after 15 min |
| RC-D | Cmdlet definition out of date (filters changed in module update) | Low | Module version |

### 8.3 Diagnostic queries

```powershell
Get-MgContext | Select Environment, Scopes
Get-AllAgentIdentities | Measure-Object  # raw count regardless of sponsor
Get-AgentsWithoutSponsors | Measure-Object
```

If `AllAgentIdentities` count is non-zero but `AgentsWithoutSponsors` returns empty, suspect filter logic or scope.

### 8.4 Resolution steps

1. Re-authenticate with explicit scopes: `Connect-MgGraph -Scopes "Application.Read.All","Directory.Read.All","User.Read.All"`.
3. If cache-lag suspected, wait 15 minutes and re-run before treating as a real defect.
4. Confirm module version: `Get-Module Microsoft.Graph.Beta.Applications -ListAvailable | Select Version` against the version pinned in `./powershell-setup.md`.

### 8.5 Verification

- `Get-AgentsWithoutSponsors` returns expected non-zero count matching portal badges (or zero if remediation has been performed).
- Pester: `It 'orphan scan executes successfully'` passes.

### 8.6 Cross-links

- PowerShell: [`./powershell-setup.md`](./powershell-setup.md) §3.

### 8.7 Examiner artifact preservation

Capture E-01 health snapshot on every orphan-scan execution; the snapshot's `Cloud` field helps distinguish tenant-context issues from missed-control findings.

---

## §9. Pillar SIEM-NO-EVENTS

**One-line:** Entra audit events for agent identities are not visible in the SIEM dashboard, even though events are occurring in Entra.

### 9.1 Symptom catalog

| Code | Symptom | First responder |
|------|---------|-----------------|
| P9-S1 | Dashboard shows zero events for > 24 hours | SIEM Engineer |
| P9-S2 | `AuditLogs` table receives data but agent-filtered queries return nothing | SIEM Engineer |
| P9-S3 | Events arrive but `targetResources.type` is `'ServicePrincipal'`, not `'Agent'` | SIEM Engineer |
| P9-S4 | Events arrive ~24 hours late | SIEM Engineer |

### 9.2 Root cause matrix

| RC | Description | Likelihood | Confirm |
|----|-------------|-----------|---------|
| RC-A | Diagnostic setting category `AuditLogs` not enabled on Entra | High for P9-S1 | Entra → Diagnostic settings |
| RC-B | Diagnostic setting destination misconfigured (workspace deleted, deprecated key) | Medium | Setting health |
| RC-C | SIEM filter assumes `targetResources.type == 'Agent'` (wrong; type is `'ServicePrincipal'`) | High for P9-S2, P9-S3 | Inspect SIEM query |
| RC-D | Diagnostic export latency (Microsoft-documented 5-15 min, occasionally hours) | Low–Medium | Service Health |

> **Critical accuracy point — diagnostic export filtering.** Entra diagnostic settings export the entire `AuditLogs` category; there is no per-event or per-`category` sub-filter at the export layer. All event-shape filtering happens **downstream in your SIEM** (Sentinel / Splunk / Chronicle). If you expected a way to ship "only agent events" out of Entra, that capability does not exist — ship the full category and filter in SIEM.

### 9.3 Diagnostic queries

```kusto
// Are AuditLogs landing at all?
AuditLogs | where TimeGenerated > ago(1h) | summarize count()

// Are agent SPN events present? (Note: filter on ServicePrincipal then inspect modifiedProperties for agent type)
AuditLogs
| where TimeGenerated > ago(24h)
| extend tr = parse_json(TargetResources)
| mv-expand tr
| where tostring(tr.type) == "ServicePrincipal"
| where tostring(tr.modifiedProperties) has "agent" or OperationName has "service principal"
| summarize count() by OperationName
```

### 9.4 Resolution steps

1. Confirm Entra → Diagnostic settings → `AuditLogs` is checked and routes to the expected workspace.
2. Inspect SIEM query for hard-coded `targetResources.type == 'Agent'` and replace with the pattern in KQL-01.
3. If RC-D, wait one hour and re-evaluate. Set a SIEM alert on "no `AuditLogs` ingestion for 4+ hours" so future export outages page automatically.

### 9.5 Verification

- KQL-01 returns events within the incident window.
- Pester: `It 'AuditLogs ingestion latency under 15 minutes for control 2.26 events'` passes.

### 9.6 Cross-links

- Portal: [`./portal-walkthrough.md`](./portal-walkthrough.md) §7 — SIEM forwarding.

### 9.7 Examiner artifact preservation

Preserve E-03 (KQL exports) and a snapshot of the SIEM detection-rule definitions. If the SIEM filter was wrong, the prior-version filter in source control demonstrates when the gap began and ended.

---

## §10. Runbook RB-01

**Title:** Microsoft Agent 365, Microsoft 365 E7, or Microsoft 365 Copilot license expiry mid-quarter
**Severity floor:** SEV-2 (rises to SEV-1 if production agents disabled by the expiry)
**Triggers:** Renewals team reports Copilot subscription not renewed; M365 admin center shows expired SKUs; symptom S-02

### 10.1 Immediate actions (first 30 min)

1. Run `Get-Agt226Health`; capture E-01.
2. Identify scope: how many operators lost the Copilot license? Are any agents themselves in a service-impaired state?
3. Notify AI Governance Lead and Procurement / Renewals.
4. Pause any scheduled `Set-AgentSponsorBulk` or workflow edits — do not change state during a license-driven outage.

### 10.2 Investigation

1. Confirm whether the Microsoft Agent 365 / M365 E7 SKU has lapsed separately from the Microsoft 365 Copilot SKU; an Agent 365 lapse alone removes the Agent ID surface even when the Copilot prerequisite remains active, and vice-versa.
2. Pull sign-in logs for last 24 h to identify which operators were attempting agent admin actions when the lapse hit.
3. Determine whether the renewal is in flight (PO open, awaiting fulfillment) or whether the firm has dropped the SKU intentionally.

### 10.3 Containment

1. If renewal is in flight: open a Microsoft support ticket (severity B) requesting grace-period extension; preserve the case number for E-09.
2. If renewal is not in flight: document the licensing gap, pause new agent-governance changes, and proceed with the renewal or de-scope decision through change control.
3. Communicate to agent owners that admin actions on agent identities are paused; existing agents continue running unless directly impacted.

### 10.4 Eradication / restoration

1. Confirm renewed SKU assigned and provisioned (`Success` not `PendingProvisioning`).
2. Verify Microsoft Agent 365 / M365 E7 license assignment is reattached to operating principals after the renewal posts; it can take up to 24h for the Agent identities surface to reflect the reassignment. If the surface remains empty after 24h, open a Microsoft support ticket per §2.7.
3. Resume paused operations. Run `Get-Agt226Health` and confirm `FrontierEnabled = True`, `AgentCount` matches pre-incident.

### 10.5 Lessons-learned / reportability

- Internal post-mortem within 5 business days.
- Reportability: if no production agent was disabled and no examiner request was open, this is generally **not** a reportable event. Document the gap and renewal-process change in the next quarterly attestation.
- Add a renewal calendar reminder 60 days pre-expiry; add a Sentinel detection on "Copilot SKU lapsed."

### 10.6 Cross-links

- [§2 PREVIEW-ACCESS-MISSING](#2-pillar-preview-access-missing).

---

## §11. Runbook RB-02

**Title:** Mass departure of a multi-agent sponsor
**Severity floor:** SEV-2 (SEV-1 if combined with workflow misconfig that disables agents)
**Triggers:** HR feed shows a single sponsor's `employeeLeaveDateTime` set, owning ≥ 10 agents; symptom S-05 / S-06

### 11.1 Immediate actions (first 60 min)

1. `Get-Agt226SponsorImpact -SponsorUpn <upn>` → freeze list as E-02 entries.
2. `Get-Agt226Health` (E-01) and `Get-Agt226LifecycleStatus` (E-05).
3. Confirm workflow is the supported manager-transfer template (not a custom disable variant). If custom-disable is found, **immediately pause the workflow** to prevent disablement.
4. Notify AI Governance Lead and the manager named in the sponsor's `manager` attribute.

### 11.2 Investigation

1. Verify `employeeLeaveDateTime` is set and accurate (E-07 / GQ-04).
2. Verify the manager attribute resolves to an enabled, in-firm user.
3. Inventory the agents by zone — Zone 3 agents need owner pre-notification before any state change.

### 11.3 Containment

1. If the manager attribute is invalid, pause the workflow and engage HR to correct the attribute before allowing it to fire.
2. Communicate to Zone 3 agent owners that their agent's nominal sponsor is changing; provide the new sponsor's UPN.

### 11.4 Eradication / restoration

1. Allow the supported workflow to run (or trigger on-demand). Confirm `Get-Agt226Agent` for each agent now shows the manager as the new sponsor.
2. If the manager declines: each declined agent enters the suspended-orphan SLA window — track via [RB-04](#13-runbook-rb-04).

### 11.5 Lessons-learned / reportability

- Reportability is driven by impact: if any agent was disabled erroneously, this is a control failure that must surface in the quarterly attestation and may warrant self-disclosure depending on examiner relationship.
- Add a guard test: any single sponsor with > 10 agents triggers a "concentration risk" report quarterly.

### 11.6 Cross-links

- [§4 SPONSOR-DEPARTED](#4-pillar-sponsor-departed), [RB-04](#13-runbook-rb-04), [RB-07](#15-runbook-rb-07).

---

## §12. Runbook RB-03

**Title:** Examiner pulls quarterly review evidence before completion
**Severity floor:** SEV-2
**Triggers:** Compliance receives examiner request for "most recent agent identity access review" and the current cycle is in progress, not completed

### 12.1 Immediate actions

1. **Do not modify the in-flight review.** Capture E-06 immediately.
2. Pull the **prior** completed cycle's review pack and confirm it included agents (per [§7](#7-pillar-review-missing-agents)).
3. Notify Compliance lead; agree on the response narrative.

### 12.2 Investigation

1. Determine whether the prior cycle is acceptable evidence (it is, if it included agents and was completed within the policy cadence).
2. If the prior cycle excluded agents or there is no prior cycle (firm is new to agent governance), the only honest answer is to disclose the gap and offer the in-flight cycle's interim status.

### 12.3 Containment / response

1. Provide the prior completed cycle as the primary artifact, with a covering memo stating the current cycle is in flight and the expected completion date.
2. If asked specifically about the in-flight cycle: provide a snapshot from `Get-Agt226ReviewCoverage` showing scope explicitly includes agents, plus a count of decisions taken so far, without freezing or modifying the review.
3. Do not accelerate the in-flight review's deadline solely to meet the examiner request — accelerated reviews are presumptively lower quality and create new risk.

### 12.4 Eradication / restoration

- Allow the in-flight review to complete on its scheduled cadence.
- After completion, supplement the examiner response with the completed pack.

### 12.5 Lessons-learned / reportability

- This is a process-resilience event, not a control failure (assuming prior cycle was complete). Document examiner question and response in the regulatory engagement log.
- Add automation: surface "current review status" on a Compliance dashboard so future requests are answerable in minutes, not days.

### 12.6 Cross-links

- [§7 REVIEW-MISSING-AGENTS](#7-pillar-review-missing-agents).

---

## §13. Runbook RB-04

**Title:** Suspended-orphan agent past 30-day SLA
**Severity floor:** SEV-2
**Triggers:** Manager declined transfer; reassignment did not complete in 30 days; symptom S-19

### 13.1 Immediate actions

1. `Get-Agt226Agent -ObjectId <id>` → confirm `Suspended = True` and original sponsor leave date > 30 days ago. Capture E-02.
2. Pull the workflow run that suspended the agent (E-05) to identify why reassignment failed.
3. Notify AI Governance Lead and the original sponsor's manager.

### 13.2 Investigation

1. Why did the manager decline? (Manager left also? Manager not the right owner anymore? Reorg?)
2. Has the agent had any execution attempts since suspension? If yes, downstream systems are affected — coordinate with those system owners.
3. Is the agent still required by the business?

### 13.3 Containment

1. If the agent is **not** still required: schedule deletion via the standard offboarding process (Control 2.x decommission). Document in the incident.
2. If the agent **is** still required: identify a new sponsor (business owner or surrogate from agent registry per CC-1), get AI Governance Lead approval, then reassign sponsor and re-enable.

### 13.4 Eradication / restoration

1. `Set-AgentSponsorBulk` (single-row CSV) for the new sponsor.
2. `Update-MgBetaServicePrincipal -ServicePrincipalId <id> -AccountEnabled:$true`.
3. Validate downstream integration recovery with the consuming system owners.

### 13.5 Lessons-learned / reportability

- Track the count of orphans-past-SLA per quarter as a control KRI (Key Risk Indicator). Trend > 0 should trigger root-cause review.
- This is normally not externally reportable unless the agent's suspension caused a customer impact during the SLA window — in which case incident reporting follows the customer-impact rules of the firm's IRT.

### 13.6 Cross-links

- [§4 SPONSOR-DEPARTED](#4-pillar-sponsor-departed).


---

## §14. Runbook RB-06

**Title:** HR connector outage breaks leaver detection
**Severity floor:** SEV-2 (rises if outage > 5 business days)
**Triggers:** `employeeLeaveDateTime` not landing for known leavers; HR / IDM team reports connector failure; symptom S-10

### 14.1 Immediate actions

1. `Get-Agt226LifecycleStatus` — last successful run? Last user with attribute set?
2. Coordinate with HR / IDM on outage scope and ETA.
3. Notify AI Governance Lead.

### 14.2 Investigation

1. List leavers expected during the outage window (HR has the canonical list).
2. Cross-reference with `Get-Agt226SponsorImpact` for each — agents owned by yet-undetected leavers are the at-risk population.

### 14.3 Containment

1. For each at-risk leaver, manually queue a reassignment via change ticket: identify new sponsor, get approval, run `Set-AgentSponsorBulk` (single row), document.
2. Do **not** mass-set `employeeLeaveDateTime` manually — this corrupts HR-as-source-of-truth.
3. Optionally pause the leaver workflow during the outage to prevent partial / inconsistent runs once the connector returns.

### 14.4 Eradication / restoration

1. Connector restored; allow backlog of `employeeLeaveDateTime` writes to land.
2. Resume / on-demand-run the workflow; validate the manually-handled leavers do not double-process (workflow should no-op if sponsor is already correct).

### 14.5 Lessons-learned / reportability

- Track HR connector availability as a Control 2.26 dependency in the dependency map.
- Reportability is rarely triggered unless the outage caused a missed access-removal that resulted in unauthorized data access — in which case it follows the firm's data-incident process.

### 14.6 Cross-links

- [§6 LIFECYCLE-NOFIRE](#6-pillar-lifecycle-nofire).

---

## §15. Runbook RB-07

**Title:** Bulk re-sponsorship after reorganization
**Severity floor:** SEV-3 (SEV-2 if > 100 agents or crosses Zone-3 boundary)
**Triggers:** Reorganization announcement; AI Governance Lead requests sponsor refresh on a cohort; symptom S-18

### 15.1 Immediate actions

1. Obtain the authoritative mapping (old sponsor → new sponsor) from the reorg PMO / HR. Treat the spreadsheet itself as a control artifact.
2. Validate the mapping: every new sponsor exists, is enabled, has manager attribute populated.
3. Create a change ticket; AI Governance Lead approves; capture approval as E-09.

### 15.2 Investigation / preparation

1. `Get-AllAgentIdentities | Export-Csv .\pre-reorg-state.csv` — snapshot pre-state per agent (E-02 in bulk).
2. Build the input CSV for `Set-AgentSponsorBulk` from the mapping.
3. Run with `-WhatIf` first; review the diff.

### 15.3 Execution

1. Run `Set-AgentSponsorBulk -CsvPath .\reassign.csv` outside business hours where practical.
2. Spot-check 5% of rows via `Get-Agt226Agent` to confirm sponsor change.
3. Communicate completion to new sponsors with the list of agents they now own.

### 15.4 Validation

1. `Get-AgentsWithoutSponsors` — should be unchanged (re-sponsoring doesn't create orphans if mapping was complete).
2. KQL-03 — count of reassignment events should match input CSV row count.
3. Pester suite green.

### 15.5 Lessons-learned / reportability

- Not externally reportable. Becomes a positive control evidence point in the next attestation: "the firm operated a planned sponsor refresh covering N agents with full audit trail."

### 15.6 Cross-links

- [§3 SPONSOR-NULL](#3-pillar-sponsor-null) (same cmdlet); [§4 SPONSOR-DEPARTED](#4-pillar-sponsor-departed).

---

## §X. Recovery and post-incident attestation refresh

After any SEV-1 or SEV-2 incident under Control 2.26, run the recovery checklist below within 10 business days. Recovery is not the same as remediation — remediation closes the incident; recovery restores the **control posture** so the next attestation is honest and complete.

### X.1 Recovery checklist

1. [ ] All evidence E-01..E-09 archived to immutable storage with retention label `FSI-Examiner-Hold-7yr`.
2. [ ] Incident ticket closed with operator-by-operator UTC timeline of every action taken.
3. [ ] Pester suite re-run end-to-end; confirm the test that *would have* caught this incident now exists. If it doesn't, file a test-gap remediation.
4. [ ] Cross-reference incident with Control 1.2 agent registry — was the registry accurate at detection? If not, registry remediation is a separate ticket.
5. [ ] Sponsor / owner notifications archived.
6. [ ] Microsoft support case (if any) closed or paused with reference number on the incident record.
7. [ ] Service-health screenshot captured (proves whether tenant was affected by a Microsoft-side issue at the time).
8. [ ] Lessons-learned document drafted; reviewed by AI Governance Lead within 5 business days.

### X.2 Attestation refresh

The next quarterly attestation must explicitly mention the incident, the remediation, the residual risk (if any), and the test added. The attestation language should hedge appropriately — recovery does not prove non-recurrence; it supports non-recurrence by closing the specific gap. Examples:

- ✅ "Following incident INC-2026-04-117, a Pester guard was added to detect customizations of the leaver workflow that disable agents. This test runs in CI on every workflow definition change and supports compliance with the manager-transfer pattern documented in Control 2.26."
- ❌ "The incident has been resolved and will not recur." (Forbidden — overclaim.)

### X.3 Test-gap remediation pattern

For each pillar §2–§9, the verification-testing pack ([`./verification-testing.md`](./verification-testing.md)) should contain at least one `Describe` block. If an incident surfaces a gap not covered by an existing test, add the test before closing recovery. Suggested mapping:

| Pillar | Pester `Describe` | Trigger conditions |
|--------|-------------------|---------------------|
| §2 | `'Preview gating'` | Operating principal lacks Microsoft Agent 365 / M365 E7 license coverage, missing Copilot SKU, or missing Agent ID Admin role |
| §3 | `'Sponsor coverage'` | Any agent with null sponsor |
| §4 | `'Sponsor leaver behavior'` | Workflow customization that disables instead of transfers |
| §5 | `'Access package shape'` | SharePoint resource directly on agent-eligible package |
| §6 | `'Lifecycle workflow health'` | Workflow disabled / no runs in N days |
| §7 | `'Access review scope'` | Active review excludes agents |
| §8 | `'Orphan scan executable'` | Cmdlet errors or returns inconsistent counts |
| §9 | `'SIEM ingestion latency'` | AuditLogs gap > 4 hours |

### X.4 Post-incident communication ladder

| Level | Audience | Trigger | Channel |
|-------|----------|---------|---------|
| L1 | Owning admin team | Any incident | Incident ticket |
| L2 | AI Governance Lead | SEV-2 or above, or any sponsor / examiner-touching incident | Direct ticket assignment + chat |
| L3 | CISO / Compliance Officer | SEV-1, or any examiner-visible incident | Page + executive email |
| L4 | Risk Committee | Any incident self-disclosed in attestation, or recurring SEV-2 of same type | Quarterly committee briefing |
| L5 | Board / Audit Committee | Examiner finding, MRA, MRIA, or SEV-1 with customer impact | Standard board reporting cadence |

---

**Document footer**

| Field | Value |
|-------|-------|
| Control | 2.26 — Entra Agent ID Identity Governance |
| Document type | Troubleshooting playbook |
| Version | 1.0 |
| Last UI verified | See `2.26-entra-agent-id-identity-governance.md` header |
| Cross-references | [`./portal-walkthrough.md`](./portal-walkthrough.md) · [`./powershell-setup.md`](./powershell-setup.md) · [`./verification-testing.md`](./verification-testing.md) · [`../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md`](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md) · [`../../_shared/powershell-baseline.md`](../../_shared/powershell-baseline.md) |
---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*


