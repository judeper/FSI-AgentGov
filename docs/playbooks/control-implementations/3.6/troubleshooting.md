# Control 3.6 — Troubleshooting: Orphaned Agent Detection and Remediation

> **Scope.** This playbook is the diagnostic companion to [Control 3.6 — Orphaned Agent Detection and Remediation](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md). It covers detection drift, sponsor/HR signal breaks, reassignment failures, bulk remediation partial success, terminal-delete blocks (Purview hold / retention label), multi-source reconciliation instability, sovereign-cloud parity gaps (GCC / GCC High / DoD), false-positive owner classifications, and SIEM ingestion gaps.
>
> **Regulatory framing.** Accurate, timely orphan detection and remediation *supports compliance with* FINRA Rule 4511 (records), SEC Rule 17a-4(f) (WORM retention of the orphan register and remediation evidence), SOX §404 (ITGC — access provisioning/de-provisioning around financially significant systems), GLBA Safeguards Rule (access controls over nonpublic personal information), and OCC Bulletin 2013-29 / Fed SR 11-7 (third-party and model risk for AI agents that persist after sponsor separation). Controls described here *support — they do not replace* registered-principal supervisory review under FINRA Rule 3110 or firm-specific model-risk governance.
>
> **Audience.** AI Administrator, Power Platform Admin, Entra Agent ID Admin, Entra Identity Governance Admin, Entra Global Reader, AI Governance Lead, Purview Compliance Admin, and SOC analysts supporting examiner/audit response.
>
> **Sibling playbooks.** [portal-walkthrough.md](portal-walkthrough.md) · [powershell-setup.md](powershell-setup.md) · [verification-testing.md](verification-testing.md)

---

## Table of Contents

- [§0 Triage Tree](#0-triage-tree)
- [§1 Diagnostic Data Collection](#1-diagnostic-data-collection)
- [§2 Pillar — DETECT-NO-RESULTS](#2-pillar-detect-no-results)
- [§3 Pillar — DETECT-DATA-DRIFT](#3-pillar-detect-data-drift)
- [§4 Pillar — HR-SIGNAL-MISSING](#4-pillar-hr-signal-missing)
- [§5 Pillar — SPONSOR-TRANSFER-FAIL](#5-pillar-sponsor-transfer-fail)
- [§6 Pillar — REASSIGN-FAIL](#6-pillar-reassign-fail)
- [§7 Pillar — BULK-PARTIAL-FAIL](#7-pillar-bulk-partial-fail)
- [§8 Pillar — TERMINAL-DELETE-BLOCKED](#8-pillar-terminal-delete-blocked)
- [§9 Pillar — RECONCILE-DRIFT](#9-pillar-reconcile-drift)
- [§10 Pillar — SOV-PARITY-GAP (GCC / GCC High / DoD)](#10-pillar-sov-parity-gap-gcc-gcc-high-dod)
- [§11 Pillar — FALSE-POSITIVE-DL-OWNER](#11-pillar-false-positive-dl-owner)
- [§12 Pillar — SIEM-NO-EVENTS](#12-pillar-siem-no-events)
- [§13 Runbook RB-01 — M&A / RIF Mass Departure](#13-runbook-rb-01-ma-rif-mass-departure)
- [§14 Runbook RB-02 — Examiner Pulls Register with SIEM Gaps](#14-runbook-rb-02-examiner-pulls-register-with-siem-gaps)
- [§15 Runbook RB-03 — Sponsor Termination Cascade](#15-runbook-rb-03-sponsor-termination-cascade)
- [§16 Runbook RB-04 — Bulk Reassign Over-Applied](#16-runbook-rb-04-bulk-reassign-over-applied)
- [§17 Runbook RB-05 — Sovereign Manual Reconciliation Drift](#17-runbook-rb-05-sovereign-manual-reconciliation-drift)
- [§18 Runbook RB-06 — SOX Zero-Orphan Attestation Failure](#18-runbook-rb-06-sox-zero-orphan-attestation-failure)
- [§19 Runbook RB-07 — Litigation-Hold Deletion Blocked](#19-runbook-rb-07-litigation-hold-deletion-blocked)
- [§20 Escalation Matrix](#20-escalation-matrix)
- [§21 Evidence Collection During Incident](#21-evidence-collection-during-incident)
- [§22 Cross-References](#22-cross-references)

---

## §0 Triage Tree

### 0.1 Symptom → Pillar Map

| # | Presenting Symptom | Most Likely Pillar | First Diagnostic |
|---|---|---|---|
| 1 | `Find-OrphanedAgents` returns 0 rows but known terminated sponsors exist | [§2 DETECT-NO-RESULTS](#2-pillar-detect-no-results) | `Get-Agt36Health -Surface Detection` |
| 2 | Agent 365 **Ownerless Agents** card shows N, script shows N±Δ | [§3 DETECT-DATA-DRIFT](#3-pillar-detect-data-drift) | GQ-01 vs. card export diff |
| 3 | Terminated user's `employeeLeaveDateTime` is null in Graph | [§4 HR-SIGNAL-MISSING](#4-pillar-hr-signal-missing) | GQ-03 HR attribute audit |
| 4 | Entra Lifecycle Workflow "Manager Transfer" didn't fire on leaver | [§5 SPONSOR-TRANSFER-FAIL](#5-pillar-sponsor-transfer-fail) | LCW run history + GQ-04 |
| 5 | `Set-AgentOwner` throws "principal not licensed for environment" | [§6 REASSIGN-FAIL](#6-pillar-reassign-fail) | `Get-Agt36OwnerEligibility` |
| 6 | Bulk remediation reports 47 of 52 succeeded, no per-agent detail | [§7 BULK-PARTIAL-FAIL](#7-pillar-bulk-partial-fail) | Correlation-ID replay |
| 7 | `Remove-OrphanedAgent` returns "PolicyHold" / "LabelRetained" | [§8 TERMINAL-DELETE-BLOCKED](#8-pillar-terminal-delete-blocked) | Purview label + hold check |
| 8 | Orphan register count changes ±15% run-to-run with no known events | [§9 RECONCILE-DRIFT](#9-pillar-reconcile-drift) | 3-source reconciliation diff |
| 9 | GCC High tenant — Ownerless Agents card not visible | [§10 SOV-PARITY-GAP](#10-pillar-sov-parity-gap-gcc-gcc-high-dod) | Sovereign surface inventory |
| 10 | Agent owned by a Distribution List flagged as "orphan" | [§11 FALSE-POSITIVE-DL-OWNER](#11-pillar-false-positive-dl-owner) | Owner principalType inspect |
| 11 | Sentinel shows no `AgentOrphanDetectionRun` events for >24h | [§12 SIEM-NO-EVENTS](#12-pillar-siem-no-events) | KQL-01 + connector health |
| 12 | Examiner asks for orphan register as-of prior quarter, cannot produce | [§14 RB-02](#14-runbook-rb-02-examiner-pulls-register-with-siem-gaps) | WORM snapshot retrieval |
| 13 | RIF event produced 600 leavers, LCW throttled | [§13 RB-01](#13-runbook-rb-01-ma-rif-mass-departure) | Throttle metrics + batch plan |
| 14 | SOX attestation shows 3 orphaned Zone 3 agents past SLA | [§18 RB-06](#18-runbook-rb-06-sox-zero-orphan-attestation-failure) | SLA clock audit |
| 15 | Litigation hold owner refuses delete despite terminal SLA breach | [§19 RB-07](#19-runbook-rb-07-litigation-hold-deletion-blocked) | Custodian coordination |

### 0.2 Severity Matrix

| Severity | Criteria | Response Target | Notifications |
|---|---|---|---|
| **SEV-1** | Detection pipeline is silent >24h **and** HR leaver events exist in the window; or examiner/regulator is on-the-clock | Triage within 1h; mitigation within 4h | AI Governance Lead, CISO delegate, Legal (if examiner) |
| **SEV-2** | Zone 3 (Enterprise) orphan past 7-day remediation SLA with no owner candidate; bulk remediation <90% success | Triage within 4h; mitigation within 24h | AI Governance Lead, Control Owner |
| **SEV-3** | Zone 2 orphan past SLA; reconciliation drift 5-15%; single reassign failure | Triage within 1 business day | Control Owner, sponsor line manager |
| **SEV-4** | Zone 1 orphan past SLA; cosmetic/reporting defect; single false positive | Triage within 5 business days | Control Owner only |

### 0.3 Pre-Escalation Checklist

Before escalating any incident above SEV-3, the on-call administrator must confirm and record:

1. **Evidence preservation initiated** — before any remediation action, capture E-01 (orphan register snapshot at time of detection) and E-02 (raw detection-run log) per [§1.5](#15-evidence-floor).
2. **Scope quantified** — exact count of affected agents, by Zone, with tenant and environment IDs.
3. **Sovereign cloud status** — whether the affected tenant is Commercial, GCC, GCC High, or DoD, and which [§10 SOV-PARITY-GAP](#10-pillar-sov-parity-gap-gcc-gcc-high-dod) compensating controls are in force.
4. **Examiner/litigation flag** — confirmation from Legal / Compliance whether any affected agent is subject to an active examination, subpoena, or litigation hold (determines whether [§8 TERMINAL-DELETE-BLOCKED](#8-pillar-terminal-delete-blocked) logic must be honored before any delete).
5. **Control dependencies verified** — status of upstream controls [1.2 Agent Registry](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md), [2.25 Agent 365 Console](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md), [2.26 Entra Agent ID](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md), [3.1 Agent Inventory](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md).

### 0.4 Examiner Artifact Preservation (Do-This-First)

If the incident could be pulled into an examination, subpoena, or internal investigation:

1. **Do not delete** any orphan entries, detection logs, or reassignment audit rows until the Legal Hold Coordinator confirms preservation.
2. Snapshot the current orphan register to an **immutable storage location** (Blob with legal hold, or Purview retention label `FSI-Examiner-Preserve-Indefinite`).
3. Record the snapshot hash (SHA-256), timestamp (UTC), operator UPN, and ticket ID in the incident record.
4. Do not run `Remove-OrphanedAgent` or `Set-AgentOwner -Force` against any preserved agent without written Legal approval.
5. Preserve raw Graph and Power Platform activity logs for the affected agents for 7 years (FINRA 4511 floor) or longer if Legal specifies.

---

## §1 Diagnostic Data Collection

All diagnostic helpers are thin, read-only wrappers that call the underlying Graph, Power Platform, and Log Analytics APIs and standardize output for evidence capture. They **never** mutate state. Names follow the `Get-Agt36*` convention.

### 1.1 Helper Inventory

| Helper | Purpose | Inputs | Output |
|---|---|---|---|
| `Get-Agt36Health` | One-shot health snapshot across detection, HR connector, LCW, Purview hold services, Agent 365 card, SIEM connector | `-Surface <Detection\|HR\|LCW\|Purview\|Card\|SIEM\|All>` | PSCustomObject with per-surface status, lastSuccess, lagMinutes |
| `Get-Agt36Orphan` | Pulls current orphan register with full metadata; supports as-of queries against WORM snapshots | `-AsOf <datetime>`, `-Zone <1\|2\|3>`, `-IncludeShadow` | Array of orphan records with category, detection source, SLA clock |
| `Get-Agt36SponsorImpact` | Given a leaver UPN, lists all agents owned, co-owned, or uniquely operated by that principal | `-LeaverUpn <string>`, `-Lookback <days>` | Impact report grouped by Zone |
| `Get-Agt36ReconcileState` | Runs a live 3-source reconciliation: Power Platform DLP inventory, Graph `applications`/`servicePrincipals`, Agent 365 export | `-Tenant <guid>` | Reconciliation delta report with hashes |
| `Get-Agt36OwnerEligibility` | Tests whether a candidate owner meets licensing, environment membership, and SoD requirements before reassignment | `-CandidateUpn <string>`, `-AgentId <guid>` | Eligibility verdict with blocking reasons |
| `Get-Agt36RetentionBindings` | For an agent, lists Purview retention labels, litigation holds, and eDiscovery case memberships | `-AgentId <guid>` | Binding list with hold IDs and custodians |

All helpers return objects compatible with `Export-Clixml`, `ConvertTo-Json -Depth 8`, and `ConvertTo-Csv` for evidence archival. Helpers respect the sovereign-cloud endpoint selection from [`_shared/powershell-baseline.md` §3](../../_shared/powershell-baseline.md#3-sovereign-cloud-endpoints-gcc-gcc-high-dod).

### 1.2 Graph Query Catalog

| ID | Purpose | Endpoint | Required Permission |
|---|---|---|---|
| **GQ-01** | Enumerate servicePrincipals with `tags` containing `AgentId` | `GET /servicePrincipals?$filter=tags/any(t:t eq 'AgentId')&$select=id,appId,displayName,owners,tags,signInActivity` | `Application.Read.All` |
| **GQ-02** | Identify ownerless agent app registrations | `GET /applications?$expand=owners&$filter=owners/$count eq 0` | `Application.Read.All` |
| **GQ-03** | Audit HR attribute presence on separated users | `GET /users?$filter=accountEnabled eq false&$select=id,userPrincipalName,employeeLeaveDateTime,employeeOrgData,manager` | `User.Read.All` |
| **GQ-04** | Lifecycle Workflow run history for a workflow | `GET /identityGovernance/lifecycleWorkflows/workflows/{id}/runs?$top=200` | `LifecycleWorkflows.Read.All` |
| **GQ-05** | Agent owners with expanded principalType (user / group / servicePrincipal) | `GET /applications/{id}/owners?$select=id,userPrincipalName,displayName,@odata.type` | `Application.Read.All` |
| **GQ-06** | Agent sign-in activity for staleness scoring | `GET /auditLogs/signIns?$filter=appId eq '{appId}' and createdDateTime ge {iso}` | `AuditLog.Read.All` |
| **GQ-07** | Directory role assignments to detect admin-owned agents | `GET /directoryRoles?$expand=members` | `RoleManagement.Read.Directory` |
| **GQ-08** | Guest/external owner enumeration (high risk) | `GET /applications?$expand=owners&$filter=owners/any(o:o/userType eq 'Guest')` | `Application.Read.All` |

Permissions must be granted to the detection pipeline's managed identity or app registration; see [2.26 Entra Agent ID](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md) for the SoD-aware permission set.

### 1.3 KQL Query Catalog (Log Analytics / Sentinel)

```kusto
// KQL-01 — Detection run cadence and success over last 14 days
AgentGovernance_CL
| where TimeGenerated > ago(14d)
| where EventType_s == "AgentOrphanDetectionRun"
| summarize Runs = count(), Successes = countif(Status_s == "Success"),
            LastSuccess = maxif(TimeGenerated, Status_s == "Success")
  by Tenant_s, bin(TimeGenerated, 1d)
| extend LagHours = datetime_diff('hour', now(), LastSuccess)
| where LagHours > 24 or Successes < Runs
```

```kusto
// KQL-02 — Reassignment actions, grouped by operator and outcome
AgentGovernance_CL
| where TimeGenerated > ago(30d)
| where EventType_s in ("AgentOwnerReassigned", "AgentOwnerReassignFailed")
| summarize count() by OperatorUpn_s, EventType_s, FailureReason_s
| order by OperatorUpn_s asc
```

```kusto
// KQL-03 — Purview hold / label block events blocking terminal delete
AgentGovernance_CL
| where EventType_s == "AgentTerminalDeleteBlocked"
| project TimeGenerated, AgentId_g, BlockReason_s, HoldId_s, CustodianUpn_s, Zone_s
| order by TimeGenerated desc
```

```kusto
// KQL-04 — HR attribute propagation lag
AgentGovernance_CL
| where EventType_s == "HrAttributeObserved"
| extend LagMinutes = datetime_diff('minute', TimeGenerated, HrSystemTimestamp_t)
| summarize p50 = percentile(LagMinutes, 50), p95 = percentile(LagMinutes, 95),
            p99 = percentile(LagMinutes, 99) by bin(TimeGenerated, 1d)
```

```kusto
// KQL-05 — Reconciliation drift alarms
AgentGovernance_CL
| where EventType_s == "AgentInventoryReconciliation"
| extend DriftPct = todouble(DriftCount_d) / todouble(TotalCount_d) * 100.0
| where DriftPct > 5.0
| project TimeGenerated, Tenant_s, DriftPct, SourceA_s, SourceB_s, DeltaHash_s
```

```kusto
// KQL-06 — SIEM connector health (self-test ping)
AgentGovernance_CL
| where EventType_s == "ConnectorSelfTest"
| summarize LastPing = max(TimeGenerated) by ConnectorName_s
| extend SilenceMinutes = datetime_diff('minute', now(), LastPing)
| where SilenceMinutes > 30
```

### 1.4 Power Platform / Agent 365 Exports

| Export | Surface | Format | Cadence |
|---|---|---|---|
| Ownerless Agents card CSV | Agent 365 Admin Center | CSV | On-demand |
| DLP policy inventory | Power Platform Admin Center | JSON (`Get-AdminDlpPolicy`) | Daily |
| Environment admin audit | Power Platform Admin Center | CSV | On-demand |
| Copilot Studio publisher audit | Copilot Studio Admin | CSV | On-demand |

### 1.5 Evidence Floor

Every Control 3.6 incident ticket must carry the following evidence artifacts, stored in immutable storage with `FSI-Records-6yr-WORM` or stricter retention:

| ID | Artifact | Source | Retention |
|---|---|---|---|
| **E-01** | Orphan register snapshot at time of detection (CSV + SHA-256) | `Get-Agt36Orphan \| Export-Csv` | 7 years (SEC 17a-4(f) floor) |
| **E-02** | Raw detection-run log (JSONL) | Log Analytics export | 7 years |
| **E-03** | Graph query responses (GQ-01..GQ-08 as relevant) | Graph API | 7 years |
| **E-04** | Lifecycle Workflow run record (if SPONSOR-TRANSFER-FAIL) | `GET /lifecycleWorkflows/.../runs/{id}` | 7 years |
| **E-05** | Reassignment audit rows (before/after owner, operator, justification) | `AgentGovernance_CL` | 7 years |
| **E-06** | Bulk job correlation-ID result set (BULK-PARTIAL-FAIL) | Job orchestrator | 7 years |
| **E-07** | Purview label / hold binding report (TERMINAL-DELETE-BLOCKED) | `Get-Agt36RetentionBindings` | 7 years |
| **E-08** | Sovereign manual reconciliation worksheet (dual-signed PDF) | Offline workbook | 7 years |
| **E-09** | Incident timeline with UTC timestamps, operator UPNs, ticket IDs | Ticketing system | 7 years |
| **E-10** | Post-incident root-cause memo and control change log | Incident review | 7 years |

Hashes (SHA-256) of E-01 through E-08 must be recorded in the incident ticket and cross-filed with the Legal Hold Coordinator if any affected agent is subject to active examination or litigation hold.

---

## §2 Pillar — DETECT-NO-RESULTS

**Symptom.** `Find-OrphanedAgents` (see [powershell-setup.md](powershell-setup.md)) returns zero records even though terminated sponsors with known agent ownership exist in the tenant.

### 2.1 Symptom Catalog

| Variant | Observable |
|---|---|
| Empty array | `Find-OrphanedAgents` returns `@()` with exit code 0 |
| Silent failure | Cmdlet returns nothing; no log line emitted to `AgentGovernance_CL` |
| Filter collapse | Results returned but every row has same `detectedSource`, missing categories 2-10 |
| Auth fail masquerading as empty | Cmdlet swallows 401/403 and returns empty set |

### 2.2 Root Cause Matrix

| Cause | Likelihood | Verification |
|---|---|---|
| Graph permission missing (`Application.Read.All`, `User.Read.All`, `AuditLog.Read.All`) | High | `Get-MgContext \| Select-Object -ExpandProperty Scopes` |
| Managed identity lost role assignment | Medium | GQ-07 directory role check; Entra audit log `Remove member from role` events |
| Detection filter too narrow (only category 1 "ownerless") | High | Inspect cmdlet source; confirm all 10 categories enumerated |
| HR connector silent — `employeeLeaveDateTime` is null everywhere | Medium | GQ-03 distribution: percentage of disabled accounts with non-null leave date |
| Token cache stale after tenant change | Low | `Disconnect-MgGraph; Connect-MgGraph` and retry |
| Tenant throttling returning empty pages | Low | Inspect Graph response headers `Retry-After`, `x-ms-throttle-*` |

### 2.3 Diagnostic Procedure

1. Run `Get-Agt36Health -Surface Detection`. If `lastSuccess` is more than 24h old or `permissionSet` shows missing scopes, treat as SEV-1 and proceed to [§12 SIEM-NO-EVENTS](#12-pillar-siem-no-events) in parallel to confirm the detection job is even executing.
2. Execute GQ-01 directly against Graph with the pipeline's credentials. If GQ-01 returns results but `Find-OrphanedAgents` does not, the cmdlet's filter logic is at fault — not the upstream data.
3. Execute GQ-02 (ownerless apps) and GQ-03 (HR attribute audit). Confirm you have non-empty result sets for **both**. If GQ-03 is empty across all disabled users, escalate to [§4 HR-SIGNAL-MISSING](#4-pillar-hr-signal-missing).
4. Inspect `AgentGovernance_CL` for `AgentOrphanDetectionRun` events in the last 24h (KQL-01). If absent, the detection job itself did not execute — investigate scheduler (Azure Automation, Logic App, or Power Automate flow owning the run).

### 2.4 Resolution Steps

- **Permission gap.** Re-consent the managed identity or app registration with the minimum scopes listed in [§1.2](#12-graph-query-catalog). Record the before/after permission set as E-03.
- **Narrow filter.** File a change request per [Control 2.3 Change Management](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md) to widen detection logic to all 10 signal categories. Do not patch in production without CAB approval.
- **Throttling.** Add exponential backoff + `Retry-After` respect to the detection helper; increase page size ceiling only after measuring 429 rates.
- **Token/context.** `Disconnect-MgGraph; Connect-MgGraph -Identity` (for managed identity) or `-Scopes` (for interactive re-consent). Verify with `Get-MgContext`.

### 2.5 Verification

1. `Find-OrphanedAgents` returns ≥ expected count (compare to manual Graph enumeration in step 2 above).
2. KQL-01 shows a successful `AgentOrphanDetectionRun` in the last hour with status `Success` and non-zero `AgentsScanned_d`.
3. Evidence E-01 and E-02 captured and hashed.
4. All 10 detection categories represented in the output (spot-check each category has at least one test case or documented zero-finding rationale).

### 2.6 Cross-References

- [Control 3.6 §Detection Signal Categories](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md)
- [Control 2.26 Entra Agent ID — permission model](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md)
- [Control 3.1 Agent Inventory](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md)

### 2.7 Examiner Artifact Preservation

Before any configuration change, export the current detection cmdlet source, scheduler definition, and permission grants to E-03. If the incident is examiner-adjacent, record the full permission-set delta (before/after) signed by the AI Administrator and AI Governance Lead.

---

## §3 Pillar — DETECT-DATA-DRIFT

**Symptom.** The Agent 365 **Ownerless Agents** governance card and `Find-OrphanedAgents` disagree on the orphan count by more than the 5% reconciliation tolerance.

### 3.1 Symptom Catalog

| Variant | Observable |
|---|---|
| Card > script | Card reports 42 ownerless; script reports 31 |
| Script > card | Script reports 58; card reports 47 |
| Category disagreement | Both agree on total, disagree on which agents are in category 1 vs. 4 |
| Transient drift | Drift resolves after 60-90 minutes (propagation lag) |

### 3.2 Root Cause Matrix

| Cause | Likelihood | Verification |
|---|---|---|
| Agent 365 card covers only category 1 (ownerless); script covers all 10 | **Very High** (by design) | Control 3.6 §Ownerless Agents card scope note |
| Card refresh lag (up to 24h) | High | Card footer "Last refreshed" timestamp |
| Script running against stale cache | Medium | Clear helper's local cache and rerun |
| Group-owned agents counted differently (expand vs. not expand) | Medium | GQ-05 principalType analysis |
| Guest/external owner exclusions differ | Medium | GQ-08 + card filter settings |
| Soft-deleted vs. hard-deleted agents in 30-day window | Low | Graph `directory/deletedItems` comparison |

### 3.3 Diagnostic Procedure

1. Export the Ownerless Agents card to CSV; capture timestamp and row count.
2. Run `Get-Agt36Orphan -Zone 3,2,1 -IncludeShadow` at the same wall-clock time.
3. Compute a **set diff** (not just a count diff) on `agentId`: rows only in card, rows only in script, rows in both.
4. For rows only in card: inspect ownership in Graph (GQ-05). They should be category 1 (truly ownerless). If they are not in script output, the script's category-1 filter has a gap.
5. For rows only in script: map each to its category (2-10). These are expected — the card does not cover categories 2-10.
6. Record the diff as E-03 with both source hashes.

### 3.4 Resolution Steps

- **Expected architectural drift (card scope).** Not an incident. Document the reconciliation narrative in the monthly governance review; the script is the system of record per Control 3.6.
- **Card refresh lag.** Wait up to 24h and re-compare. If drift persists beyond 24h after a known change event, open a Microsoft support case referencing the card refresh cadence.
- **Script cache staleness.** Clear helper cache: `Get-Agt36Orphan -ClearCache`. Rerun and re-diff.
- **Principal-type inconsistency.** Align script's principalType handling with the card's (user + group + servicePrincipal) and document in the detection cmdlet's header comment.

### 3.5 Verification

1. Set diff resolves to zero for category 1 rows.
2. Non-category-1 rows are present only in the script output, which is expected.
3. E-01 (orphan register) hash matches E-03 (card export) for the category-1 subset.
4. Monthly reconciliation narrative updated in the Control 3.6 governance log.

### 3.6 Cross-References

- [Control 2.25 Agent 365 Admin Console](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md)
- [Control 3.13 Agent 365 Admin Center Analytics](../../../controls/pillar-3-reporting/3.13-agent-365-admin-center-analytics.md)

### 3.7 Examiner Artifact Preservation

Archive both the card CSV and the script output side-by-side with the reconciliation narrative. Examiners frequently ask "why do these two numbers differ" and the prepared narrative must be retrievable within the examination response SLA.

---

## §4 Pillar — HR-SIGNAL-MISSING

**Symptom.** `employeeLeaveDateTime`, `employeeHireDate`, or `manager` is not populated on Entra user objects for known HR events, breaking every downstream lifecycle signal.

### 4.1 Symptom Catalog

| Variant | Observable |
|---|---|
| Global null | GQ-03 shows 0% populated across all disabled users |
| Partial propagation | Some populations (FTE) populated; contractors not |
| Time zone truncation | Leave date set to midnight UTC regardless of local termination time |
| Stale update | Leave date populated but does not match HRIS of record |

### 4.2 Root Cause Matrix

| Cause | Likelihood | Verification |
|---|---|---|
| HR connector (Workday, SuccessFactors, Entra Cloud Sync with HR source) not running | High | Connector run history |
| Attribute mapping missing for `employeeLeaveDateTime` | High | Provisioning attribute mapping JSON |
| Non-FTE populations excluded from HR sync scope | High | Sync scope rules |
| Source HRIS does not publish leave date | Medium | HRIS data team confirmation |
| Provisioning throttled / quarantined | Low | Provisioning logs |

### 4.3 Diagnostic Procedure

1. Run GQ-03 and compute coverage: (non-null `employeeLeaveDateTime` / accountEnabled=false) × 100.
2. Pull Entra provisioning logs for the HR connector: filter on action=Update, last 7 days.
3. Compare a known-terminated user's Entra record to the HRIS source-of-truth record. Record deltas.
4. Verify attribute mapping in the provisioning configuration (portal: Entra ID → Users → Provisioning → Attribute mappings).

### 4.4 Resolution Steps

- **Connector down.** Restart connector; if quarantined, clear quarantine after diagnosing root cause (typically >10% mismatch rate during pilot).
- **Mapping gap.** File change request (Control 2.3) to add `employeeLeaveDateTime` mapping; coordinate with HR systems team on the source-attribute name.
- **Scope exclusion.** If contractor population is excluded by policy, document the compensating control (manual monthly HR export → orphan register reconciliation).
- **Time zone.** Document the UTC midnight convention in the Control 3.6 data dictionary; downstream cmdlets must not assume local-time precision.

### 4.5 Verification

1. GQ-03 coverage ≥ 95% on disabled users terminated in the last 30 days.
2. Representative sample of 10 recent terminations — Entra record matches HRIS within ±1 business day.
3. Entra provisioning logs show connector healthy with <5% failure rate.
4. Orphan detection rerun shows HR-signal-driven categories (2, 3, 5) returning expected volumes.

### 4.6 Cross-References

- [Control 2.26 Entra Agent ID — HR signal dependencies](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md)
- [Control 2.8 Access Control & Segregation of Duties](../../../controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md)

### 4.7 Examiner Artifact Preservation

Preserve the HR connector run history and attribute mapping configuration as E-03. For FSI examinations focused on JML (Joiner-Mover-Leaver) controls, examiners will request evidence that HR events flow into identity governance within a documented SLA.

---

## §5 Pillar — SPONSOR-TRANSFER-FAIL

**Symptom.** Entra Identity Governance Lifecycle Workflow "Manager Transfer on Leaver" did not fire, or fired but did not transfer agent ownership to the leaver's manager.

### 5.1 Symptom Catalog

| Variant | Observable |
|---|---|
| Workflow did not fire | `GET /lifecycleWorkflows/workflows/{id}/runs` has no run for the leaver |
| Workflow fired but no-op | Run record exists; action log shows 0 objects transferred |
| Partial transfer | Some agents transferred; some skipped with `TargetNotEligible` |
| Manager missing | Leaver has no `manager` attribute; workflow has no transfer target |

### 5.2 Root Cause Matrix

| Cause | Likelihood | Verification |
|---|---|---|
| Workflow trigger condition does not match leaver's attributes | High | Trigger JSON vs. leaver attribute dump |
| `manager` attribute null on leaver | High | GQ-03 extended with `manager` expansion |
| Workflow scope excludes leaver's department/OU | Medium | Workflow scope rules |
| Workflow disabled or in draft state | Medium | Workflow `isEnabled` property |
| Custom task script failed (returned non-zero) | Medium | Task run result |
| Licensing — Entra ID Governance P2 not assigned to workflow identity | Low | Tenant license audit |

### 5.3 Diagnostic Procedure

1. Identify the specific workflow by name; record its `id`.
2. GQ-04: pull last 50 runs; filter to leaver's UPN.
3. If no run: confirm the leaver matches the workflow's scope and trigger (employeeLeaveDateTime in last N days + scope attribute match).
4. If run exists but no-op: inspect each task's `status` and `processingResult`. "Task completed, 0 objects" typically means the identity had no owned apps at run time — which may be correct if a prior run already transferred them.
5. For partial transfer: inspect the skipped agents' owner eligibility with `Get-Agt36OwnerEligibility -CandidateUpn <manager>`.

### 5.4 Resolution Steps

- **Trigger mismatch.** Adjust trigger expression (portal or Graph PATCH), requires Entra Identity Governance Admin. File Control 2.3 change request.
- **Missing manager.** Escalate to HR to populate; until populated, workflow cannot transfer. Interim: manual reassignment per [§6 REASSIGN-FAIL](#6-pillar-reassign-fail) procedures with AI Governance Lead approval.
- **Eligibility block.** Transfer target (manager) lacks required license or environment membership. Either license them or pick an alternate owner (line-of-business agent steward).
- **Disabled workflow.** Re-enable after root-cause of disabling is documented (often: emergency disable during incident).

### 5.5 Verification

1. GQ-04 shows a successful run for each recent leaver within the workflow's SLA (typically 2h post employeeLeaveDateTime).
2. Post-transfer, GQ-05 on each affected agent shows the new manager as owner.
3. E-04 (LCW run record) captured.
4. Entra audit log shows `Update application owners` events matching the workflow run correlation ID.

### 5.6 Cross-References

- [Control 2.26 Entra Agent ID — Lifecycle Workflows](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md)
- [Control 2.8 SoD — manager-transfer justification](../../../controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md)

### 5.7 Examiner Artifact Preservation

Preserve the workflow definition JSON, run record, and resulting Entra audit events as an E-04 bundle. Manager-transfer is a critical JML control; examiners will expect end-to-end traceability from HR event → LCW run → ownership change → Entra audit.

---

## §6 Pillar — REASSIGN-FAIL

**Symptom.** `Set-AgentOwner` or `Set-AdminPowerAppOwner` fails with errors such as "principal not licensed for environment", "not a member of environment", "SoD violation", or "insufficient privileges on target".

### 6.1 Symptom Catalog

| Variant | Observable |
|---|---|
| License block | Error `UserLicenseNotFound` or `NotLicensedForEnvironment` |
| Environment membership block | Error `UserNotEnvironmentMember` |
| SoD block | Error `SegregationOfDutiesViolation` (operator and candidate overlap on incompatible roles) |
| Privilege block | Error `InsufficientPrivileges` on operator |
| Silent success-then-revert | Reassignment appears to succeed, then reverts within minutes (policy overrider) |

### 6.2 Root Cause Matrix

| Cause | Likelihood | Verification |
|---|---|---|
| Candidate owner lacks Power Apps per-user or per-app license | High | `Get-MgUserLicenseDetail -UserId <upn>` |
| Candidate not in the target environment's access list | High | Power Platform Admin Center → Environment → Access |
| SoD policy blocks cross-role reassignment (e.g., assigning ownership to a user with incompatible Entra role) | Medium | Control 2.8 SoD matrix |
| Operator is Global Reader — read-only | Medium | `Get-MgContext` scope enumeration |
| Conditional Access blocks the candidate (device compliance, MFA) | Low | Sign-in logs for candidate |
| Managed environment policy (in Managed Environments) enforces stricter owner rules | Low | Managed Environments settings |

### 6.3 Diagnostic Procedure

1. `Get-Agt36OwnerEligibility -CandidateUpn <upn> -AgentId <guid>`. Read the verdict block — it enumerates every blocker.
2. If license block: confirm with `Get-MgUserLicenseDetail`. Provision license (requires License Admin) or pick a different candidate.
3. If environment block: add candidate to target environment with correct role.
4. If SoD block: consult Control 2.8 SoD matrix. Either change the candidate or route through an approved break-glass procedure.
5. If silent revert: inspect environment's Managed Environments policy for owner-enforcement rules; disable enforcement temporarily with change-request approval.

### 6.4 Resolution Steps

- **Licensing.** Coordinate with License Admin to provision Power Apps license. Do not proxy the license through a service principal — ownership must resolve to a human or approved group.
- **Environment membership.** Add candidate via Power Platform Admin Center → Environment → Access. Record the add event as E-03.
- **SoD.** Select an alternate candidate in line with Control 2.8. If none exists, escalate to AI Governance Lead for documented exception with compensating control.
- **Privileges.** Operator must hold Power Platform Admin or equivalent; re-authenticate with the correct principal.

### 6.5 Verification

1. `Set-AgentOwner` succeeds; exit code 0 with new ownerId in response.
2. GQ-05 on the agent shows the new owner.
3. Audit event `AgentOwnerReassigned` present in `AgentGovernance_CL` (KQL-02) with operator, justification, old/new owner.
4. E-05 captured.

### 6.6 Cross-References

- [Control 2.8 Access Control & SoD](../../../controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md)
- [Control 1.2 Agent Registry](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md)

### 6.7 Examiner Artifact Preservation

For each reassignment, preserve the full E-05 audit row including justification free-text. Examiners will sample reassignments and ask for the business rationale; the justification field is the primary evidence.

---

## §7 Pillar — BULK-PARTIAL-FAIL

**Symptom.** A bulk reassignment or bulk terminal-delete job reports "47 of 52 succeeded" with no per-agent detail, or hangs partway through.

### 7.1 Symptom Catalog

| Variant | Observable |
|---|---|
| Aggregate counter only | Log says "5 failed" with no agentId list |
| Hang | Job status `Running` for >4h with no progress events |
| Inconsistent retry | Some failures retried, others not — no deterministic policy |
| Correlation missing | No correlation ID tying bulk job to individual agent actions |

### 7.2 Root Cause Matrix

| Cause | Likelihood | Verification |
|---|---|---|
| Per-item error logging not emitted by job orchestrator | High | Inspect orchestrator source / logs |
| Throttling mid-batch (429) with silent drop | High | Response-header telemetry |
| Mixed-cause failures (some license, some SoD, some hold) hidden behind single counter | Medium | Per-agent replay |
| Orchestrator process restart mid-run | Low | Process uptime telemetry |

### 7.3 Diagnostic Procedure

1. Pull the bulk job's correlation ID.
2. Query `AgentGovernance_CL` for all events with that correlation ID (KQL-02 variant).
3. For each agent in the input set missing a success event, replay the single-agent reassignment using `Get-Agt36OwnerEligibility` first, then `Set-AgentOwner` with the same parameters.
4. Record per-agent outcome into E-06.

### 7.4 Resolution Steps

- **Instrumentation.** File Control 2.3 change request to add per-item logging (agentId, status, errorCode, errorMessage, durationMs) to the orchestrator. Until patched, manual replay per step 3 above is required.
- **Throttling.** Implement batch sizing (e.g., 25 at a time) with backoff; respect `Retry-After` headers.
- **Mixed-cause surfacing.** Aggregate log must include a failure-reason histogram, not just a count.

### 7.5 Verification

1. Every agent in the input set has exactly one terminal event (success or classified failure) in `AgentGovernance_CL`.
2. E-06 shows per-agent outcome with correlation ID traceable end-to-end.
3. Re-run of the same input set converges to steady state within 2 attempts.

### 7.6 Cross-References

- [§6 REASSIGN-FAIL](#6-pillar-reassign-fail)
- [§8 TERMINAL-DELETE-BLOCKED](#8-pillar-terminal-delete-blocked)
- [Control 2.3 Change Management](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md)

### 7.7 Examiner Artifact Preservation

A bulk job is examination-sensitive because it represents a population-level control action. Preserve the input manifest (list of agent IDs), the per-item outcome ledger (E-06), and the aggregate summary. Examiners will reconcile input vs. outcome counts line-by-line.

---

## §8 Pillar — TERMINAL-DELETE-BLOCKED

**Symptom.** `Remove-OrphanedAgent` returns `PolicyHold`, `LabelRetained`, `LitigationHoldActive`, or `eDiscoveryCaseMember` and refuses to delete.

### 8.1 Symptom Catalog

| Variant | Observable |
|---|---|
| Purview retention label binding | Label with retention rule + record designation prevents delete |
| Litigation hold on owner mailbox | Owner's mailbox on hold; associated artifacts preserved |
| eDiscovery case custodian | Agent listed as custodian-adjacent in active case |
| Managed Environments data-loss policy | Environment-level policy requires manual dual approval |

### 8.2 Root Cause Matrix

This is **by design** — terminal delete must never silently override a legal preservation obligation. The troubleshooting task is to confirm the block is valid, route to the correct preservation workflow, and advance the remediation clock correctly.

| Cause | Likelihood | Action |
|---|---|---|
| Purview retention label (record) | High | Confirm label; route to Records Management workflow |
| Litigation hold | High | Coordinate with Legal Hold Coordinator |
| eDiscovery custodian | Medium | Coordinate with Case Manager |
| Stale hold not released after matter close | Medium | Request hold release from Legal |
| Label misapplied (false positive) | Low | File label-correction request with Purview Compliance Admin |

### 8.3 Diagnostic Procedure

1. `Get-Agt36RetentionBindings -AgentId <guid>`. Enumerate every label and hold binding with custodian UPNs.
2. For each binding, open the corresponding case/hold in Purview Compliance and confirm status.
3. If any binding is active, the agent **must not be deleted**. It may be (a) retained in place with ownership reassigned to a records steward, or (b) soft-deleted with the retention binding preserved — whichever the Records Management policy specifies.

### 8.4 Resolution Steps

- **Active hold, valid.** Reassign ownership to records steward or designated custodian. Document the decision and file in the orphan register with status `Retained-Under-Hold`. The remediation SLA clock stops at the point of hold confirmation per Control 3.6 §Evidence & Retention.
- **Stale hold.** Request hold release from Legal Hold Coordinator; attach evidence that the matter is closed. Re-run terminal delete after release is confirmed in Purview.
- **Misapplied label.** Purview Compliance Admin corrects label assignment; retain full audit trail of the correction.

### 8.5 Verification

1. For each agent blocked, there is a documented decision: `Retained-Under-Hold`, `Released-Then-Deleted`, or `Label-Corrected-Then-Deleted`.
2. E-07 (retention binding report) captured with timestamp and operator.
3. No terminal delete occurred against an agent with an active legal preservation obligation.

### 8.6 Cross-References

- [Control 3.6 §Evidence & Retention](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md)
- [§19 Runbook RB-07](#19-runbook-rb-07-litigation-hold-deletion-blocked)

### 8.7 Examiner Artifact Preservation

This pillar is itself an evidence-preservation pillar. Every blocked delete produces an artifact (E-07) that becomes part of the agent's lifecycle record. Examiners view intact preservation as a positive control signal.

---

## §9 Pillar — RECONCILE-DRIFT

**Symptom.** The 3-source reconciliation (Power Platform inventory + Graph + Agent 365) shows >5% drift run-to-run with no corresponding change events, indicating reconciliation logic instability rather than real change.

### 9.1 Symptom Catalog

| Variant | Observable |
|---|---|
| High-frequency oscillation | Drift bounces between +5% and -5% every run |
| One-sided drift | One source systematically higher than the others |
| Hash mismatch with zero row-level diff | Hashes differ but row-level comparison shows identical content |

### 9.2 Root Cause Matrix

| Cause | Likelihood | Verification |
|---|---|---|
| Eventual-consistency window (Graph and Power Platform propagate at different rates) | High | Stagger run timestamps 15 min apart; drift should converge |
| Soft-deleted agents counted differently | High | Include/exclude soft-deleted uniformly |
| Key normalization differs (appId vs. objectId vs. agentId) | Medium | Inspect join keys in reconciliation code |
| Sort order differences break hash even when content identical | Medium | Canonicalize order before hashing |

### 9.3 Diagnostic Procedure

1. Run `Get-Agt36ReconcileState -Tenant <guid>`. Capture the delta report.
2. For each row in the delta: confirm whether it is present in all 3 sources, or absent from one.
3. Compute an **order-independent hash** on each source and compare.
4. Stagger a second run 30 minutes later and compare — persistent drift is structural; transient drift is propagation lag.

### 9.4 Resolution Steps

- **Propagation lag.** Document the eventual-consistency window; raise the drift-alarm threshold or debounce with a 60-minute moving average.
- **Normalization.** Align join keys; canonicalize to `agentId` (the governance identifier). File Control 2.3 change request.
- **Sort-independence.** Replace sequence-dependent hash with sorted-merge hash.

### 9.5 Verification

1. KQL-05 shows drift < 5% for 3 consecutive runs.
2. Hash computation is order-independent (test: shuffle input, re-hash, compare).
3. Reconciliation narrative in E-09 explains any residual expected drift.

### 9.6 Cross-References

- [Control 3.1 Agent Inventory](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md)
- [Control 2.25 Agent 365 Console](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md)

### 9.7 Examiner Artifact Preservation

Preserve both the raw source exports and the reconciliation delta. Examiners may request "show me that your three inventory sources agree" and the prepared reconciliation artifact is the direct response.

---

## §10 Pillar — SOV-PARITY-GAP (GCC / GCC High / DoD)

**Symptom.** In sovereign clouds (GCC, GCC High, DoD), the Agent 365 Ownerless Agents card and Entra Lifecycle Workflows are **not available or are feature-delayed**, preventing the commercial-cloud automation path.

### 10.1 Symptom Catalog

| Variant | Observable |
|---|---|
| Card absent | Agent 365 Admin Center has no Ownerless Agents tile in GCC High |
| LCW feature-delayed | Manager-transfer workflow template unavailable in DoD |
| Endpoint mismatch | Commercial Graph endpoint used against sovereign tenant — 404s |
| Permission scope parity gap | Scope exists in commercial but not yet in sovereign |

### 10.2 Compensating Controls (Sovereign)

Per Control 3.6, sovereign tenants **must** implement:

1. **Quarterly manual reconciliation** with a dual-signed PDF worksheet (operator + AI Governance Lead), using `Get-Agt36Orphan` against the sovereign Graph endpoint.
2. **HR-event-triggered manual review** for every leaver with Zone 3 agent ownership — documented in a ticketed workflow with 7-day SLA.
3. **Terminal deletion dual control** — Power Platform Admin + AI Administrator both required.

### 10.3 Diagnostic Procedure

1. Confirm the correct sovereign endpoint is in use. Reference [`_shared/powershell-baseline.md §3 Sovereign Cloud Endpoints (GCC / GCC High / DoD)`](../../_shared/powershell-baseline.md#3-sovereign-cloud-endpoints-gcc-gcc-high-dod).
2. Run `Get-Agt36Health -Surface All`. Sovereign-expected surfaces will report `NotAvailable`; this is not a failure.
3. Confirm the quarterly manual reconciliation worksheet (E-08) has been executed on schedule.
4. Confirm dual-control signatures on the last terminal-delete action.

### 10.4 Resolution Steps

- **Wrong endpoint.** Re-authenticate with the sovereign-cloud environment parameter (`-Environment USGov`, `USGovHigh`, `USGovDoD` as applicable).
- **Missing quarterly reconciliation.** Execute immediately; file an off-cycle worksheet documenting the gap and remediation; reset the quarterly clock.
- **Feature-delay.** Track the Microsoft 365 Roadmap; document the compensating control in the Control 3.6 sovereign addendum until parity is achieved.

### 10.5 Verification

1. Sovereign endpoint confirmed in helper output and log breadcrumbs.
2. E-08 (dual-signed manual reconciliation worksheet) present for the current quarter.
3. Audit log shows dual approvers for every terminal-delete action in the quarter.

### 10.6 Cross-References

- [Control 3.6 §Sovereign Cloud Compensating Controls](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md)
- [`_shared/powershell-baseline.md` §3 Sovereign Cloud Endpoints](../../_shared/powershell-baseline.md#3-sovereign-cloud-endpoints-gcc-gcc-high-dod)
- [§17 Runbook RB-05 Sovereign Manual Reconciliation Drift](#17-runbook-rb-05-sovereign-manual-reconciliation-drift)

### 10.7 Examiner Artifact Preservation

Sovereign examinations (typically DoD / federal FSI subsidiaries) scrutinize compensating-control evidence heavily. Preserve E-08 worksheets with full signature blocks (signer UPN, timestamp, certificate thumbprint if digitally signed).

---

## §11 Pillar — FALSE-POSITIVE-DL-OWNER

**Symptom.** An agent owned by a Distribution List, Microsoft 365 Group, or Security Group is flagged as "orphan" because the detection cmdlet resolved ownership to "no user principal".

### 11.1 Symptom Catalog

| Variant | Observable |
|---|---|
| DL owner | Owner is a mail-enabled distribution list |
| Security group owner | Owner is a security group with members |
| Dynamic group | Owner is a dynamic M365 group, membership resolves at runtime |
| Nested group | Owner is a group whose only member is another group |

### 11.2 Root Cause Matrix

| Cause | Likelihood | Verification |
|---|---|---|
| Detection cmdlet does not expand group membership to check for human members | High | Inspect cmdlet source |
| Group membership resolves to zero users (empty DL) — genuine orphan-equivalent | Medium | Expand membership at detection time |
| Nested group depth exceeds cmdlet's expansion limit | Low | Increase expansion depth (cap at 3 levels per governance policy) |

### 11.3 Diagnostic Procedure

1. For each flagged agent, run GQ-05 and inspect owner `@odata.type`.
2. If type is `#microsoft.graph.group`: expand membership with `GET /groups/{id}/transitiveMembers`.
3. If expanded membership contains ≥1 active user, this is a **false positive** — the agent is owned by a group with valid human members.
4. If expanded membership is empty or contains only disabled users, this is a **genuine orphan-equivalent** and should remain in the register with a category-specific flag.

### 11.4 Resolution Steps

- **False positive.** File Control 2.3 change request to enhance the detection cmdlet to expand group membership (up to 3 levels) and classify as orphan only if transitive membership has zero active users.
- **Empty DL.** Retain in orphan register under new category "ownerless-group-resolved". Apply same remediation workflow as a direct ownerless agent.
- **Temporary workaround.** Maintain a curated allowlist of group owners known to be valid (e.g., `agent-stewards@org`), with quarterly recertification.

### 11.5 Verification

1. Flagged DL/group-owned agents with valid transitive human members no longer appear in the orphan register.
2. Empty DL/group-owned agents appear with the correct category flag.
3. Allowlist recertified in the last quarter (if used as interim).

### 11.6 Cross-References

- [Control 1.2 Agent Registry](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md)
- [Control 2.8 SoD](../../../controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md)

### 11.7 Examiner Artifact Preservation

Document the false-positive analysis as part of the monthly governance review. Examiners appreciate explicit false-positive handling because it demonstrates control calibration maturity.

---

## §12 Pillar — SIEM-NO-EVENTS

**Symptom.** Sentinel (or other SIEM) shows no `AgentOrphanDetectionRun`, `AgentOwnerReassigned`, or `AgentTerminalDelete` events for more than 24 hours, despite operational activity.

### 12.1 Symptom Catalog

| Variant | Observable |
|---|---|
| Total silence | KQL-01, KQL-02, KQL-03 all empty for 24h+ |
| Partial silence | Detection events arrive; reassignment events do not |
| Connector unhealthy | Data Connector status in Sentinel shows "Degraded" or "Disconnected" |
| Table schema drift | Events arrive but in a different table or with renamed columns |

### 12.2 Root Cause Matrix

| Cause | Likelihood | Verification |
|---|---|---|
| Data Collection Rule (DCR) misconfigured or disabled | High | Azure Monitor → DCR inventory |
| Log Analytics workspace key rotated without updating sender | High | Sender configuration vs. current workspace key |
| Sender identity lost `Log Analytics Contributor` role | Medium | RBAC audit |
| Network egress blocked (private endpoint / NSG change) | Medium | Connectivity test from sender |
| Ingestion cap hit (daily cap reached) | Medium | Log Analytics workspace usage |
| Table name change (Custom Logs v2 migration) | Low | Schema audit |

### 12.3 Diagnostic Procedure

1. KQL-06 (Connector self-test ping). If self-test is silent, the sender pipeline is down.
2. Azure Portal → Log Analytics workspace → Usage and estimated costs → check daily cap and ingestion.
3. From the sender host, test connectivity to the ingestion endpoint (public or private).
4. Verify sender identity's role assignments against the workspace.

### 12.4 Resolution Steps

- **DCR disabled.** Re-enable; verify with KQL-06 self-test within 15 minutes.
- **Key rotated.** Update sender; restart sender service; confirm with KQL-06.
- **RBAC lost.** Re-assign `Log Analytics Contributor` or `Monitoring Metrics Publisher` to sender identity.
- **Network.** Diagnose NSG/private endpoint; file network change request.
- **Ingestion cap.** Coordinate with platform team on cap increase or workload rebalancing.

### 12.5 Verification

1. KQL-06 returns a ping within the last 10 minutes.
2. KQL-01, KQL-02 return events consistent with current operational tempo.
3. Sentinel Data Connector status is Healthy.
4. E-02 recoverable for the silent window (from sender-side local buffer if available, or post-incident manual replay).

### 12.6 Cross-References

- [§14 Runbook RB-02 — Examiner Pulls Register with SIEM Gaps](#14-runbook-rb-02-examiner-pulls-register-with-siem-gaps)
- [Control 3.1 Agent Inventory](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md)

### 12.7 Examiner Artifact Preservation

During SIEM silence, the sender host's local buffer (if implemented) is often the only record. Preserve the local buffer until events are confirmed ingested. Document the silent window with start/end UTC timestamps in E-09 for examiner transparency.

---

## §13 Runbook RB-01 — M&A / RIF Mass Departure

**Trigger.** M&A divestiture, reduction in force, or mass reorganization generates >100 leaver events in a <72-hour window, potentially orphaning hundreds of agents.

### 13.1 Pre-Conditions

- HR has confirmed the population cutoff list (final leaver UPNs).
- Legal has confirmed whether any leaver is subject to litigation hold.
- AI Governance Lead has briefed Control Owners on the event window.
- Baseline orphan register (E-01) captured immediately pre-event.

### 13.2 Procedure

1. **T-24h**: Snapshot current orphan register and agent inventory (E-01, E-03). Hash and file.
2. **T-0**: HR event propagates. Monitor GQ-03 coverage; expected populated `employeeLeaveDateTime` within 4h.
3. **T+4h**: Run `Get-Agt36SponsorImpact` across the full leaver list. Produce an impact report grouped by Zone with total affected agent count.
4. **T+8h**: Entra Lifecycle Workflows should have fired. Verify via GQ-04 batch query. Throttling is likely — if <80% processed at T+8h, escalate to parallel-batch manual reassignment.
5. **T+24h**: For agents still orphaned post-LCW, initiate batched `Set-AgentOwner` in groups of 25 with 5-minute pauses. Capture per-agent outcomes (E-05, E-06).
6. **T+72h**: Run full reconciliation (`Get-Agt36ReconcileState`). Zero Zone 3 agents should remain orphaned.
7. **T+7d**: Produce RIF remediation summary memo (E-10).

### 13.3 Evidence Bundle

E-01 (T-24h baseline), E-03 (Graph queries at multiple checkpoints), E-04 (LCW runs), E-05 (reassignments), E-06 (bulk job outcomes), E-09 (incident timeline), E-10 (summary memo).

### 13.4 Post-Incident Actions

- Tune LCW throttle configuration based on observed throughput.
- Document any novel orphan patterns as new detection categories or false-positive rules.
- Conduct lessons-learned with AI Governance Lead; update this runbook.

### 13.5 Cross-References

- [§5 SPONSOR-TRANSFER-FAIL](#5-pillar-sponsor-transfer-fail)
- [§7 BULK-PARTIAL-FAIL](#7-pillar-bulk-partial-fail)
- [Control 2.26 Entra Agent ID](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md)

---

## §14 Runbook RB-02 — Examiner Pulls Register with SIEM Gaps

**Trigger.** Examiner or internal audit requests the orphan register "as of" a prior date, but SIEM ingestion had silent windows during that period.

### 14.1 Pre-Conditions

- Examiner request scope documented (as-of date, agent population, detail level).
- Legal Hold Coordinator engaged if the examination is formal.
- WORM storage access available (read-only with audit) to the AI Governance Lead.

### 14.2 Procedure

1. **T+0**: Acknowledge request; confirm scope in writing with examiner and AI Governance Lead.
2. **T+1h**: Retrieve WORM-stored orphan register snapshot (E-01) closest to the examiner's as-of date. Verify hash.
3. **T+2h**: Cross-check against detection-run logs (E-02). Identify any silent windows from [§12 SIEM-NO-EVENTS](#12-pillar-siem-no-events) post-incident records.
4. **T+4h**: For each silent window, retrieve sender-side local buffer or re-run `Get-Agt36Orphan -AsOf <datetime>` against Graph / Power Platform historical data where available. Document explicitly which sources were usable for which time ranges.
5. **T+24h**: Package register, supporting evidence, and silent-window narrative for examiner. Include explicit statement of known gaps — **do not** paper over gaps; examiners view candor favorably.
6. **T+48h**: AI Governance Lead review and dual-signature on the examiner deliverable.

### 14.3 Evidence Bundle

E-01, E-02, E-03 (historical Graph query replays), E-09, E-10 (examiner response memo with silent-window narrative).

### 14.4 Post-Incident Actions

- Remediate any SIEM gaps identified during the silent-window narrative.
- Implement sender-side durable buffering if not already in place.
- Update the retention policy on WORM storage if the examiner-relevant window is older than the current retention.

### 14.5 Cross-References

- [§12 SIEM-NO-EVENTS](#12-pillar-siem-no-events)
- [Control 3.5 Cost Allocation & Budget Tracking](../../../controls/pillar-3-reporting/3.5-cost-allocation-and-budget-tracking.md) *(for examiner cost-impact questions)*

---

## §15 Runbook RB-03 — Sponsor Termination Cascade

**Trigger.** A single high-privilege sponsor's termination triggers orphaning of 10+ Zone 3 agents, including cross-business-unit agents.

### 15.1 Pre-Conditions

- HR confirmed termination with effective date.
- Sponsor's `manager` attribute is populated in Entra.
- Business-unit agent stewards identified for each affected Zone 3 agent.

### 15.2 Procedure

1. **T-24h** (if planned): Run `Get-Agt36SponsorImpact -LeaverUpn <sponsor>`. Distribute to business-unit stewards for reassignment pre-planning.
2. **T-0**: Termination effective. `employeeLeaveDateTime` populated.
3. **T+2h**: LCW fires. Verify GQ-04. Manager-transfer default covers agents where business-unit steward agrees.
4. **T+4h**: For agents requiring alternate owner (not manager), execute `Set-AgentOwner` with documented business-steward approval (E-05).
5. **T+24h**: Zero orphans in sponsor's impact set. Final reconciliation and evidence bundle.

### 15.3 Evidence Bundle

E-03 impact report, E-04 LCW runs, E-05 per-agent reassignments with business-unit approvals, E-09 timeline.

### 15.4 Post-Incident Actions

- Review whether the sponsor held single-owner status on any agent (SoD risk pattern); add co-owner policy for Zone 3 agents with privileged sponsors.

### 15.5 Cross-References

- [§5 SPONSOR-TRANSFER-FAIL](#5-pillar-sponsor-transfer-fail)
- [Control 2.8 SoD](../../../controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md)

---

## §16 Runbook RB-04 — Bulk Reassign Over-Applied

**Trigger.** A bulk reassignment job transferred ownership of agents that were **not** intended to be in scope, due to an over-broad input filter.

### 16.1 Pre-Conditions

- The over-application has been detected (typically: unexpected ownership-change events in KQL-02).
- Input manifest preserved.
- Legal notified if any over-applied agent is examination-adjacent.

### 16.2 Procedure

1. **T+0**: Freeze further bulk jobs. Snapshot current state (E-03, E-05).
2. **T+1h**: Reconstruct the intended input set vs. the actual processed set. Identify the over-applied subset.
3. **T+2h**: For each over-applied agent, retrieve the pre-change owner from E-05 audit rows. Re-run `Set-AgentOwner` to restore the original owner with justification "Reversal of RB-04 incident <id>".
4. **T+8h**: Full reconciliation. Confirm all over-applied agents are restored.
5. **T+24h**: Root cause of filter over-broadness documented. Input-validation enhancement filed under Control 2.3.

### 16.3 Evidence Bundle

E-05 (both original and reversal rows), E-06 (original bulk job), E-09, E-10.

### 16.4 Post-Incident Actions

- Add pre-flight dry-run with diff preview to the bulk orchestrator.
- Require dual approval on any bulk job exceeding 50 agents.

### 16.5 Cross-References

- [§7 BULK-PARTIAL-FAIL](#7-pillar-bulk-partial-fail)
- [Control 2.3 Change Management](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md)

---

## §17 Runbook RB-05 — Sovereign Manual Reconciliation Drift

**Trigger.** Quarterly sovereign manual reconciliation (GCC High or DoD) shows >10% delta between manual worksheet and automated helper output.

### 17.1 Pre-Conditions

- Prior quarter's dual-signed worksheet (E-08) retrievable.
- Sovereign endpoint configuration verified per [`_shared/powershell-baseline.md §3`](../../_shared/powershell-baseline.md#3-sovereign-cloud-endpoints-gcc-gcc-high-dod).

### 17.2 Procedure

1. Recompute both the manual and automated numbers at the same wall-clock time.
2. Diff at agent-ID level, not just count.
3. Classify each delta: missed-by-manual, missed-by-automated, or eventual-consistency.
4. File a sovereign-addendum narrative in E-08 for the current quarter, signed by the operator and AI Governance Lead.
5. Escalate any missed-by-manual findings to the sovereign operations team for training.

### 17.3 Evidence Bundle

E-08 (current + prior quarter), E-03 (Graph queries against sovereign endpoint), E-09.

### 17.4 Post-Incident Actions

- Consider automating the reconciliation in the sovereign tenant once Microsoft roadmap parity enables it.
- Update the sovereign operations runbook with any newly discovered reconciliation nuances.

### 17.5 Cross-References

- [§10 SOV-PARITY-GAP](#10-pillar-sov-parity-gap-gcc-gcc-high-dod)

---

## §18 Runbook RB-06 — SOX Zero-Orphan Attestation Failure

**Trigger.** Quarterly SOX attestation for financially significant systems (Zone 3, tagged `SOX-ICFR-Relevant`) shows >0 orphaned agents past remediation SLA.

### 18.1 Pre-Conditions

- SOX attestation window is active (typically last 2 weeks of quarter).
- Control Owner and SOX Control Tester identified.
- Audit committee reporting timeline known.

### 18.2 Procedure

1. **T+0**: SOX Tester flags orphan count > 0. AI Governance Lead acknowledges.
2. **T+1h**: For each orphan, produce SLA clock audit — start time (detection), current time, breach magnitude.
3. **T+2h**: Classify each breach: genuine remediation miss, TERMINAL-DELETE-BLOCKED (valid preservation), or data-quality artifact.
4. **T+24h**: Remediate the genuine misses. For hold-blocked items, ensure the register correctly reflects `Retained-Under-Hold` status per [§8.4](#84-resolution-steps).
5. **T+3d**: Control Owner and AI Governance Lead sign a deficiency memo if any genuine miss exceeded materiality thresholds; route through Internal Audit per SOX §404 process.
6. **T+7d**: Remediation evidence (E-05, E-07 as applicable, E-10) bundled for Internal Audit.

### 18.3 Evidence Bundle

E-01 at start of window, E-01 at attestation time, E-05 remediations, E-07 hold records, E-09 timeline, E-10 deficiency memo (if applicable).

### 18.4 Post-Incident Actions

- Tune detection SLA tiering if a recurring category is slipping.
- Review whether Zone 3 SOX-tagged agents require stricter owner policy (e.g., mandatory co-owner).

### 18.5 Cross-References

- [Control 3.6 §Evidence & Retention](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md)
- [Control 2.8 SoD](../../../controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md)

---

## §19 Runbook RB-07 — Litigation-Hold Deletion Blocked

**Trigger.** An agent is past terminal-deletion SLA but `Remove-OrphanedAgent` is blocked by an active litigation hold or eDiscovery case binding.

### 19.1 Pre-Conditions

- Legal Hold Coordinator identified.
- eDiscovery Case Manager identified (if applicable).
- `Get-Agt36RetentionBindings` output available (E-07).

### 19.2 Procedure

1. **T+0**: Confirm the block is valid via Purview Compliance. This is not an error to work around — it is a legal obligation.
2. **T+1h**: Route the agent to `Retained-Under-Hold` status in the orphan register. Reassign ownership (not deletion) to the designated records steward. The remediation SLA clock stops at this point per Control 3.6 §Evidence & Retention.
3. **T+24h**: Document in the register the hold ID, custodian, and expected matter-close date.
4. **On hold release** (date varies): Legal Hold Coordinator notifies AI Governance Lead. Re-run `Remove-OrphanedAgent`. Capture E-05, E-07, and the Legal release notice as E-10.

### 19.3 Evidence Bundle

E-07 (binding at start, release at end), E-05 (final deletion), Legal release notice, E-09 end-to-end timeline (often spanning months or years).

### 19.4 Post-Incident Actions

- Review the agent's lifecycle record for completeness; the full retained-through-hold narrative is examination-grade.
- If a recurring pattern emerges (same custodian, multiple holds), coordinate with Legal on whether a more structured custodian-of-record role is appropriate.

### 19.5 Cross-References

- [§8 TERMINAL-DELETE-BLOCKED](#8-pillar-terminal-delete-blocked)
- [Control 3.6 §Evidence & Retention](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md)

---

## §20 Escalation Matrix

| Severity | Primary Responder | Escalation L1 | Escalation L2 | External |
|---|---|---|---|---|
| SEV-1 | AI Administrator on-call | AI Governance Lead | CISO delegate | Legal, examiner liaison |
| SEV-2 | AI Administrator | Control Owner | AI Governance Lead | — |
| SEV-3 | AI Administrator | Control Owner | — | — |
| SEV-4 | AI Administrator | — | — | — |

**Cross-functional contacts** (always reachable via established on-call rotation):

- **Entra Identity Governance Admin** — Lifecycle Workflows, HR attribute provisioning (§4, §5).
- **Power Platform Admin** — environment membership, DLP policy, bulk job orchestration (§6, §7).
- **Purview Compliance Admin** — retention labels, holds, eDiscovery (§8, RB-07).
- **Legal Hold Coordinator** — litigation holds, examiner artifact preservation, RB-02, RB-07.
- **AI Governance Lead** — policy interpretation, dual-signature on SEV-1/2 evidence bundles.

Notifications are dispatched via the firm's ticketing system with SLA clocks per the severity matrix. The AI Governance Lead carries authority to waive non-regulatory SLAs in the case of a compensating incident; such waivers are recorded in E-10.

---

## §21 Evidence Collection During Incident

Evidence collection is **continuous and non-destructive**. The following conventions apply to every Control 3.6 incident:

1. **Capture before you act.** E-01 and E-02 must be captured prior to any remediation step. Hashes recorded in the incident ticket.
2. **Hash every artifact.** SHA-256 at minimum; include filename, size, and UTC capture time.
3. **Chain of custody.** Every handoff of evidence (operator → analyst → Legal) records UPN and UTC timestamp.
4. **Immutable storage.** All evidence artifacts ultimately land in WORM storage with `FSI-Records-6yr-WORM` retention or stricter. Examination-flagged artifacts escalate to `FSI-Examiner-Preserve-Indefinite`.
5. **Never edit a primary artifact.** Derivations (e.g., filtered views for examiner response) are separate files that reference the primary.
6. **Cross-file with Legal** whenever examiner, subpoena, or litigation hold touches the incident.
7. **Complete the evidence bundle** before closing the ticket. E-09 (timeline) and E-10 (root-cause memo) are mandatory for SEV-1 and SEV-2.

### 21.1 Standard Evidence Capture Skeleton

```powershell
# Capture orphan register snapshot (E-01)
$ts    = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
$stem  = "INC-$($TicketId)-$ts"
$regP  = "$EvidenceRoot\$stem-E01-orphan-register.csv"

Get-Agt36Orphan -Zone 3,2,1 -IncludeShadow |
    Export-Csv -Path $regP -NoTypeInformation -Encoding UTF8

$hash  = (Get-FileHash -Path $regP -Algorithm SHA256).Hash
Write-EvidenceManifest -TicketId $TicketId -ArtifactId E-01 `
    -Path $regP -Sha256 $hash -CapturedBy (whoami) -CapturedAtUtc $ts
```

The `Write-EvidenceManifest` helper writes a signed JSON manifest to the same WORM storage location, keyed by ticket ID. See [powershell-setup.md](powershell-setup.md) for the full helper definition.

---

## §22 Cross-References

### 22.1 Control Cross-References

- [Control 3.6 — Orphaned Agent Detection and Remediation](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) — source-of-truth control specification.
- [Control 1.2 — Agent Registry and Integrated Apps Management](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md) — upstream inventory.
- [Control 2.25 — Agent 365 Admin Center Governance Console](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md) — Ownerless Agents card.
- [Control 2.26 — Entra Agent ID Identity Governance](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md) — Lifecycle Workflows, HR signal.
- [Control 2.3 — Change Management and Release Planning](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md) — for all detection/orchestrator changes.
- [Control 2.8 — Access Control and Segregation of Duties](../../../controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md) — reassignment SoD rules.
- [Control 3.1 — Agent Inventory and Metadata Management](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md) — inventory reconciliation.
- [Control 3.5 — Cost Allocation and Budget Tracking](../../../controls/pillar-3-reporting/3.5-cost-allocation-and-budget-tracking.md) — orphan cost reporting.
- [Control 3.13 — Agent 365 Admin Center Analytics](../../../controls/pillar-3-reporting/3.13-agent-365-admin-center-analytics.md) — analytics surface.

### 22.2 Sibling Playbook Cross-References

- [3.6 portal-walkthrough.md](portal-walkthrough.md)
- [3.6 powershell-setup.md](powershell-setup.md)
- [3.6 verification-testing.md](verification-testing.md)
- [`_shared/powershell-baseline.md` §3 Sovereign Cloud Endpoints (GCC / GCC High / DoD)](../../_shared/powershell-baseline.md#3-sovereign-cloud-endpoints-gcc-gcc-high-dod)

### 22.3 Regulatory Cross-References

- **FINRA Rule 4511** — books and records preservation; register is system-of-record artifact.
- **FINRA Rule 3110** — supervisory review; this playbook *supports — does not replace* registered-principal supervisory review.
- **SEC Rule 17a-4(f)** — WORM retention for broker-dealer records; 6-year floor applied to E-01 through E-10.
- **SOX §404** — ITGC for access provisioning/de-provisioning; see RB-06.
- **GLBA Safeguards Rule** — access controls over NPI; orphan agents are access-control risks.
- **OCC Bulletin 2013-29 / Fed SR 11-7** — third-party and model risk; AI agents that persist past sponsor separation are in-scope risk events.

---

*Updated: April 2026 | Version: v1.4.0 | UI Verification Status: Current*
