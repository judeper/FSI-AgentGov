# Control 2.12 — Supervision and Oversight (FINRA Rule 3110): Troubleshooting Playbook

**Companion to:** [Control 2.12 — Supervision and Oversight (FINRA Rule 3110)](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md)
**Sibling playbooks:** [Portal Walkthrough](./portal-walkthrough.md) · [PowerShell Setup](./powershell-setup.md) · [Verification & Testing](./verification-testing.md)
**Audience:** Designated Principal (Series 24 / 66 / 65), Compliance Officer, AI Governance Lead, AI Administrator, Purview Compliance Admin, Power Platform Admin, Exchange Online Admin, Entra Global Reader, IR on-call.
**Scope:** Diagnose and remediate failures in the human-in-the-loop (HITL) supervisory workflow for Microsoft Copilot Studio, Microsoft Agent Framework (`RequestPort` / `request_info()` / checkpointed pending requests), Power Automate approval actions, the Zone 3 supervisory review queue, Rule 2210 classification and principal pre-use approval, Rule 3120 annual testing, WSP-to-deployed-config reconciliation, designated-principal qualification, sponsorship-derived accountability (cascade from Control 2.26), orphaned-agent supervisory re-entry (cascade from Control 3.6), reviewer-decision evidence retention (FINRA 4511 / SEC 17a-4(b)(4) / (f)).

> **Regulatory framing (non-substitution).** This playbook describes diagnostic and remediation procedures that **support compliance with** FINRA Rule 3110 (Supervision), Rule 3120 (Supervisory Control System), Rule 2210 (Communications with the Public), Rule 4511 (Books and Records), FINRA Regulatory Notice 24-09 (Gen AI / LLM Guidance), SEC Rules 17a-3 / 17a-4, SOX §§ 302 / 404, GLBA Safeguards Rule § 314.4, OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12), Fed SR 26-2 (formerly SR 11-7), CFTC Regulation 1.31, and NYDFS 23 NYCRR 500. The Copilot Studio HITL surface, Agent Framework request/response API, Power Automate approval actions, and Entra Agent ID sponsorship constitute supervisory **tooling**; they do **not** substitute for (a) the firm's written supervisory procedures, (b) the designation of an appropriately registered principal (Series 24 for broker-dealer supervisory scope; Series 66 / 65 for RIA scope), or (c) the registered-principal supervisory review and principal pre-use approval required by FINRA Rule 3110 and Rule 2210 for the business activities involved. Controls 2.25, 2.26, and 3.6 reference Control 2.12 as the authoritative non-substitution anchor. When troubleshooting, a successful remediation that restores tooling does **not** close the supervisory gap for any interaction that occurred while the tooling was broken — that gap remains for Legal / Compliance disposition (see §21 RB-01, RB-03, RB-04).

> **Hedged language reminder.** Throughout this playbook, phrases such as "supports", "helps meet", "aids in demonstrating", and "recommended" are used intentionally. This playbook does not guarantee, ensure, or eliminate any regulatory outcome. Implementation requires firm-specific calibration of WSP language, sampling rates, principal designation, and SLA definitions. Organizations should verify every procedure in a non-production tenant and validate with Legal / Compliance before executing a remediation that mutates production supervisory state.

---

## §0 Overview — How to Use This Playbook

### §0.1 Purpose

This playbook is the first-line reference for on-call supervisory-control operators responding to a symptom or incident that implicates the Control 2.12 HITL surface. It is organized so that the on-call can:

1. Triage the symptom in ≤ 5 minutes (§1);
2. Jump to the correct diagnostic pillar (§2–§12) or situational runbook (§13–§19);
3. Execute the diagnostic, resolution, prevention, and evidence-capture procedures for that pillar;
4. Escalate per the matrix in §20 when tenant-side remediation is exhausted;
5. Deliver the examiner-grade evidence bundle per §21.

The playbook assumes the reader has read [PowerShell Setup](./powershell-setup.md), has loaded the `Agt212` helper module, and has a session authenticated to the PIM-elevated role required for the action in progress.

### §0.2 Audience and Role Boundaries

| Role (canonical — see [Role Catalog](../../../reference/role-catalog.md)) | Primary responsibility in this playbook |
|---|---|
| **Designated Principal / Qualified Supervisor** (Series 24 / 66 / 65) | Final supervisory authority; signs post-incident supervisory determinations; owns principal pre-use approvals under Rule 2210; **cannot** be substituted by any automation. |
| **Compliance Officer** | Owns the WSP addendum; signs Rule 3120 testing evidence; disposition authority for `WSP-DRIFT`, `R2210-MISCLASSIFICATION`, `R3120-TEST-FAIL`. |
| **AI Governance Lead** | Incident commander for Sev1/Sev2 HITL incidents; owns sampling protocol calibration. |
| **AI Administrator** | Microsoft-admin-surface operator for Copilot Studio, Power Automate, Agent Framework configuration; executes remediation commands under AI Governance Lead direction. |
| **Purview Compliance Admin** | Owns retention labels, immutable evidence library, and the audit-log export pipeline feeding WORM / 17a-4(f) storage. |
| **Exchange Online Admin** | Owns retention policy operational verification (`Get-RetentionCompliancePolicy`), mailbox-routed approval actions. |
| **Power Platform Admin** | Owns Power Automate approval flow health, environment-level DLP, and flow ownership. |
| **Entra Global Reader** | Evidence-collection role; read-only access to sign-in logs, audit logs, role assignments; used during triage to avoid mutating state. |
| **IR on-call** | First responder for Sev1; initiates §21 evidence snapshot before any mutation. |

> **SoD (separation-of-duties) reminder.** The AI Administrator who operates Microsoft admin surfaces **must not** be the same natural person as the Designated Principal who signs supervisory decisions. If the same individual is named to both roles in the firm's WSP, the firm is out of line with FINRA 3110(b)(6) SoD expectations; log this as a WSP exception per §6.

### §0.3 Severity Definitions

| Severity | Trigger | Response SLA | Examiner-artifact preservation |
|---|---|---|---|
| **Sev1** | HITL not firing for Zone 3 agents in production, OR a known Rule 2210 retail communication was sent without principal pre-use approval, OR reviewer-decision audit trail is missing for a named customer interaction under examiner inquiry, OR a designated-principal registration has lapsed and no qualified replacement is in place | On-call engaged in 15 min; AI Governance Lead + Compliance Officer in 30 min; Legal notified within 60 min if customer-impacting | **Mandatory before any remediation:** full evidence snapshot per §21 (E-01..E-14) |
| **Sev2** | Review queue SLA breached but not during examiner-active window; a single pillar degraded; Rule 3120 annual-test finding of operating deficiency | 2 business hours; AI Governance Lead within 4 business hours | Snapshot per §21 if Zone 3 affected |
| **Sev3** | Single agent / single template affected; Zone 1 or Zone 2 only; administrative / cosmetic drift; documented compensating-control in place | Next business day | Change-log entry; optional snapshot |

**Examiner-active posture:** If FINRA, SEC, OCC, Fed, CFTC, or NYDFS has an examination in flight or has issued an inquiry within the preceding 60 days, **every** Sev2 is upgraded to Sev1 for purposes of evidence preservation and Legal notification.

### §0.4 Structure of Each Pillar (§3–§13)

Every pillar follows this standardized subsection layout to keep the on-call's cognitive load minimal:

- **.1 Symptom Catalog** — codified P-codes (e.g., `P2-S1`) mapped to severity hints
- **.2 Root Cause Matrix** — codified RC-codes with confirmation signals
- **.3 Diagnostic Steps** — ordered, non-mutating, read-only evidence gathering first
- **.4 Resolution Steps** — per-RC remediation, with `-WhatIf` safety and SoD gating
- **.5 Prevention** — configuration, monitoring, and WSP controls to prevent recurrence
- **.6 Evidence to Capture** — pillar-specific artifacts that append to the §21 bundle
- **.7 Cross-References** — related pillars, runbooks, and controls

### §0.5 What This Playbook Does **Not** Cover

- **Copilot Studio authoring / builder issues** unrelated to HITL — see the Copilot Studio general troubleshooting guidance in Microsoft Learn.
- **Entra directory-level identity issues** — see Control 1.11 (Conditional Access and Phishing-Resistant MFA) and the Entra admin center diagnostics.
- **Power Platform DLP policy authoring** — see Control 2.14.
- **Agent registry / metadata issues** — see [Control 3.1 — Agent Inventory and Metadata Management](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md).
- **Incident reporting mechanics (post-incident lifecycle)** — see [Control 3.4 — Incident Reporting and Root Cause Analysis](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md). This playbook covers the **supervisory-control** incident response; Control 3.4 covers the broader incident reporting and RCA discipline.

---

## §1 Five-Minute Triage

This section is the entry point for every page, ticket, or examiner-driven inquiry touching Control 2.12. Follow it in order. Do **not** skip to a pillar or runbook without completing §1.3 (pre-escalation checklist).

### §1.1 Symptom → Pillar Map

| Observed symptom | First-look pillar | Secondary pillar |
|---|---|---|
| Zone 3 agent returns response to user without visible reviewer intervention when WSP says it should | §3 HITL-NOT-FIRING | §7 WSP-DRIFT |
| Power Automate approval action fired but response never reached the user (timeout) | §4 QUEUE-STUCK | §6 ESCALATION-BROKEN |
| Review queue depth > SLA target for 4+ business hours | §4 QUEUE-STUCK | §5 REVIEWER-UNQUALIFIED |
| Reviewer UPN in audit log does not appear on firm's current designated-principal roster | §5 REVIEWER-UNQUALIFIED | §7 WSP-DRIFT |
| High-risk output escalation routed to the wrong group, or group was empty | §6 ESCALATION-BROKEN | §4 QUEUE-STUCK |
| WSP addendum says "pre-use approval required for retail comms" but deployed agent configuration does not route through approval | §7 WSP-DRIFT | §8 R2210-MISCLASSIFICATION |
| Agent output reached > 25 retail investors within 30 days without pre-use approval | §8 R2210-MISCLASSIFICATION | §7 WSP-DRIFT |
| Zone 3 agent is classified "fully autonomous" in registry but lacks exceptional-controls documentation | §9 AUTONOMY-MISMATCH | §7 WSP-DRIFT |
| Entra Agent ID sponsor UPN is disabled / departed; no replacement sponsor attestation on file | §10 SPONSOR-ATTESTATION-FAIL | §20 RB-07 (cascade via Control 3.6) |
| Reviewer decision captured but rationale field null, or reviewer UPN null, or retention < 6 years | §11 EVIDENCE-GAP | §21 (bundle) |
| Agent Framework workflow resumed but pending request not re-emitted; orphaned request ID with no response | §12 AGF-CHECKPOINT-LOSS | §11 EVIDENCE-GAP |
| Annual Rule 3120 testing found a design or operating deficiency | §13 R3120-TEST-FAIL | (applicable pillar) |
| Examiner inquiry about a named customer interaction cannot produce HITL record | §14 RB-01 (examiner HITL production) | §11 EVIDENCE-GAP |
| Designated principal's Series 24 registration lapsed mid-quarter | §15 RB-02 (principal lapse) | §5 REVIEWER-UNQUALIFIED |
| HITL bypassed due to configuration error (post-incident) | §16 RB-03 (post-incident HITL bypass) | §3 HITL-NOT-FIRING |
| Retail communication sent without pre-use approval (post-incident) | §17 RB-04 (2210 post-incident) | §8 R2210-MISCLASSIFICATION |
| SOX § 302 / § 404 management-cert deadline and supervision evidence incomplete | §18 RB-05 (SOX cert) | §11 EVIDENCE-GAP |
| Surprise Zone 3 audit; reviewer-decision audit trail has gaps | §19 RB-06 (surprise Z3 audit) | §11 EVIDENCE-GAP |
| Sponsor mass-termination; Z3 agents pending reassignment | §20 RB-07 (sponsor cascade) | [Control 3.6](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) |

### §1.2 Severity Fast-Classify

Within the first 5 minutes, the on-call determines severity using:

1. **Customer-impacting?** If any agent response reached a customer (Zone 3) during the fault window → Sev1.
2. **Examiner-active?** If any regulator has an open inquiry → upgrade by one level (Sev3→Sev2, Sev2→Sev1).
3. **Principal qualified?** If the acting reviewer's registration is not current → Sev1 regardless of volume.
4. **Retention intact?** If reviewer-decision records for any interaction in the window cannot be produced in < 2 business hours → Sev1.
5. **WSP deviation?** If deployed config materially differs from the WSP addendum → Sev2 minimum; Sev1 if examiner-active.

### §1.3 Pre-Escalation Checklist (do these before paging)

Before paging the AI Governance Lead or Compliance Officer, the on-call must complete:

1. **Freeze state.** Do **not** re-deploy, re-publish, or re-bind any agent. Mutation before evidence capture destroys examiner-grade artifacts.
2. **Capture initial evidence floor.** Invoke `Invoke-Agt212EvidenceSnapshot -IncidentId <id> -Stage Initial -Destination AgentGov-Evidence-212` (produces E-01 through E-05). See §21.
3. **Identify affected agents.** Run `Get-Agt212Agent -Scope Incident -IncidentId <id>` and capture the list of agent IDs, zones, sponsors, designated principals, autonomy levels.
4. **Identify affected interactions.** Run `Get-Agt212Interaction -AgentId <id> -From <utc> -To <utc>` and determine whether any interaction in the window (a) should have routed to HITL per WSP, (b) actually did, and (c) produced a reviewer decision.
5. **Confirm examiner posture.** Query the firm's examination-tracking system; if an exam is in flight or an inquiry is open, mark incident `ExaminerActive=true` in the ticket.
6. **Confirm principal coverage.** Run `Get-Agt212PrincipalRoster -Current` and verify current designated principals are qualified (CRD extract ≤ 90 days old). If not → §5 REVIEWER-UNQUALIFIED.
7. **Notify Legal / Compliance.** Sev1 customer-impacting incidents require Legal notification within 60 minutes.

### §1.4 When to Skip Straight to a Runbook

Bypass the pillar tree and go directly to the §13–§19 runbook when:

- The incident is **post-incident** (the fault has already occurred; the work now is reconstruction and regulator response) — use RB-01, RB-03, RB-04, or RB-06.
- The incident is **cross-control** (spans 2.12 + 2.26 + 3.6 via sponsor cascade) — use RB-07.
- The incident has a **calendar deadline** (SOX cert, Rule 3120 annual deadline, examiner response due date) — use RB-05 or RB-06.
- The incident involves a **named principal's registration lapse** — use RB-02.

---

## §2 Diagnostic Data Collection (Reference Catalog)

This section enumerates the helper cmdlets, Graph queries, KQL queries, and Dataverse queries referenced throughout §3–§20. All cmdlet examples assume PowerShell 7.4 Core and the helper module loaded per [PowerShell Setup](./powershell-setup.md).

```powershell
#Requires -Version 7.4
#Requires -Modules Microsoft.Graph.Authentication, Microsoft.PowerApps.Administration.PowerShell, PnP.PowerShell, Microsoft.Graph.Identity.Governance
```

### §2.1 `Get-Agt212*` / `Invoke-Agt212*` Helper Catalog

| Cmdlet | Purpose | Mutates? |
|---|---|---|
| `Get-Agt212Health` | End-to-end probe of Copilot Studio handoff endpoint, Power Automate approval endpoint, Agent Framework checkpoint service, Purview evidence-library write path, and WSP-reconciliation service | No |
| `Get-Agt212Agent` | Returns a single agent's configuration including zone, autonomy level, sponsor UPN, designated principal UPN, HITL pattern, 2210 classification, and WSP addendum reference | No |
| `Get-Agt212Interaction` | Returns interaction records (conversation ID, user UPN, timestamp, HITL routing decision, reviewer decision) for a time window | No |
| `Get-Agt212HitlStatus` | Returns HITL configuration state per agent: pattern (handoff / approval / guardrails), trigger criteria, reviewer group binding | No |
| `Get-Agt212ReviewQueue` | Returns pending review items with age, assignee, agent ID, conversation ID | No |
| `Get-Agt212PrincipalRoster -Current` | Returns the active list of designated principals with CRD registration state, series held, and attestation timestamp | No |
| `Get-Agt212WspReconciliation` | Compares the deployed HITL / 2210 config against the WSP addendum and returns drift records | No |
| `Get-Agt212R2210Classification` | Returns Rule 2210 classification (Correspondence / Retail / Institutional) for agent output templates | No |
| `Get-Agt212AutonomyDeclaration` | Returns agent's declared autonomy level (Recommend-Only / Semi-Autonomous / Fully-Autonomous) and exceptional-controls documentation reference | No |
| `Get-Agt212SponsorState` | Returns sponsor UPN, employment status, attestation date, backup sponsor UPN | No |
| `Get-Agt212AgfCheckpoint` | Returns Agent Framework checkpoint records for pending `request_info()` invocations, including checkpoint ID, request ID, agent ID, timestamp | No |
| `Get-Agt212Evidence` | Returns a reviewer-decision evidence record by conversation ID, including reviewer UPN, timestamp, decision, rationale, retention label | No |
| `Get-Agt212R3120Status` | Returns the most recent Rule 3120 annual testing record with pass/fail per test area | No |
| `Get-Agt212AuditEvents` | Wrapper over Purview Audit unified log filtered to the AgentGov supervisory workloads | No |
| `Invoke-Agt212EvidenceSnapshot` | Produces the E-01..E-14 evidence bundle to the Purview immutable evidence library | Yes (write-only to WORM) |
| `Invoke-Agt212HitlRebind` | Rebinds a Copilot Studio HITL pattern or Agent Framework handler binding; `-WhatIf` supported | Yes |
| `Invoke-Agt212QueueReassign` | Reassigns pending review items from an unavailable reviewer to a backup principal; `-WhatIf` supported | Yes |
| `Invoke-Agt212WspReconcile` | Re-applies WSP-sourced config to deployed agent; `-WhatIf` supported; requires Compliance Officer co-sign | Yes |

All mutating cmdlets honor `-WhatIf` and emit a SHA-256 evidence hash per the [PowerShell Authoring Baseline](../../_shared/powershell-baseline.md).

### §2.2 Graph Query Catalog (GQ-01..GQ-10)

Replace `{tenantId}`, `{agentId}`, `{conversationId}` as appropriate.

**GQ-01 — Agent Framework checkpoint service probe**
```http
GET https://graph.microsoft.com/beta/admin/agentFramework/serviceStatus
```
Expected `200 OK` with `state: "operational"`.

**GQ-02 — Pending HITL requests (Agent Framework)**
```http
GET https://graph.microsoft.com/beta/admin/agentFramework/pendingRequests?$filter=state eq 'awaitingResponse'&$top=999
```

**GQ-03 — Agent Framework checkpoint for a request**
```http
GET https://graph.microsoft.com/beta/admin/agentFramework/checkpoints/{checkpointId}?$expand=pendingRequests
```

**GQ-04 — Copilot Studio HITL configuration for an agent**
```http
GET https://graph.microsoft.com/beta/copilotStudio/agents/{agentId}/hitlConfiguration
```

**GQ-05 — Power Automate approval flow state**
```http
GET https://graph.microsoft.com/beta/admin/powerAutomate/flows/{flowId}?$expand=runs($top=50)
```

**GQ-06 — Entra directory role assignment for a reviewer UPN**
```http
GET https://graph.microsoft.com/v1.0/users/{upn}/memberOf
```

**GQ-07 — Entra Agent ID sponsor binding**
```http
GET https://graph.microsoft.com/beta/identity/agenticUsers/{agentId}?$expand=sponsors,owners,managers
```

**GQ-08 — Supervisory-review audit events (last 24h)**
```http
GET https://graph.microsoft.com/beta/security/auditLog/directoryAudits?$filter=category eq 'AgentSupervision' and activityDateTime ge {iso8601-24h-ago}
```

**GQ-09 — Retention label for supervisory evidence library**
```http
GET https://graph.microsoft.com/beta/security/labels/retentionLabels?$filter=displayName eq 'AgentGov-Evidence-212'
```

**GQ-10 — Rule 3120 testing evidence record**
```http
GET https://graph.microsoft.com/beta/admin/agentGov/supervisionTesting?$filter=year eq {yyyy}
```

### §2.3 KQL Catalog (KQL-01..KQL-08)

Run in Microsoft Sentinel or the Purview Audit advanced-search experience.

**KQL-01 — HITL trigger rate vs WSP expectation**
```kusto
AgentGovActivity
| where TimeGenerated > ago(7d)
| where Workload in ("CopilotStudio","AgentFramework","PowerAutomateApproval")
| where OperationName in ("HitlTriggered","HitlNotTriggered","HitlBypassed")
| summarize Triggered=countif(OperationName=="HitlTriggered"),
            NotTriggered=countif(OperationName=="HitlNotTriggered"),
            Bypassed=countif(OperationName=="HitlBypassed")
            by AgentId, Zone=tostring(AdditionalProperties.Zone), bin(TimeGenerated, 1d)
| extend TriggerRatePct = round(100.0 * Triggered / (Triggered+NotTriggered+Bypassed), 2)
| order by TimeGenerated desc, Zone asc
```

**KQL-02 — Review queue age distribution**
```kusto
AgentGovActivity
| where TimeGenerated > ago(7d)
| where OperationName == "ReviewQueue.ItemSnapshot"
| extend AgeMin = todouble(AdditionalProperties.AgeMinutes)
| summarize p50=percentile(AgeMin,50), p95=percentile(AgeMin,95), p99=percentile(AgeMin,99), MaxDepth=max(toint(AdditionalProperties.QueueDepth))
            by Zone=tostring(AdditionalProperties.Zone), bin(TimeGenerated, 1h)
| order by TimeGenerated desc
```
p95 > SLA target sustained > 2h → §4 QUEUE-STUCK.

**KQL-03 — Reviewer-UPN-to-principal-roster reconciliation gaps**
```kusto
let Roster = AgentGovActivity
    | where OperationName == "PrincipalRoster.Snapshot"
    | where TimeGenerated > ago(1d)
    | project ActiveUPNs=todynamic(AdditionalProperties.ActiveUPNs);
AgentGovActivity
| where TimeGenerated > ago(7d)
| where OperationName == "HitlReviewerDecision"
| extend ReviewerUPN = tostring(AdditionalProperties.ReviewerUPN)
| join kind=leftouter (Roster | mv-expand upn=ActiveUPNs | project RosterUPN=tostring(upn)) on $left.ReviewerUPN==$right.RosterUPN
| where isempty(RosterUPN)
| project TimeGenerated, ReviewerUPN, AgentId, ConversationId, CorrelationId
```

**KQL-04 — HITL bypass events**
```kusto
AgentGovActivity
| where OperationName == "HitlBypassed"
| project TimeGenerated, ActorUPN, AgentId, ConversationId, BypassReason=AdditionalProperties.BypassReason, CorrelationId
| order by TimeGenerated desc
```
Any Zone 3 bypass is Sev1.

**KQL-05 — WSP-to-deployed drift signals**
```kusto
AgentGovActivity
| where OperationName == "WspReconciliation.Drift"
| project TimeGenerated, AgentId, DriftField=AdditionalProperties.Field, WspValue=AdditionalProperties.WspValue, DeployedValue=AdditionalProperties.DeployedValue, CorrelationId
| order by TimeGenerated desc
```

**KQL-06 — 2210 classification misalignment**
```kusto
AgentGovActivity
| where OperationName == "R2210.ClassificationApplied"
| where AdditionalProperties.RetailAudienceCount > 25 and AdditionalProperties.ClassificationApplied == "Correspondence"
| project TimeGenerated, AgentId, TemplateId, RetailAudienceCount=toint(AdditionalProperties.RetailAudienceCount), ClassificationApplied, CorrelationId
```

**KQL-07 — Agent Framework checkpoint loss signals**
```kusto
AgentGovActivity
| where OperationName in ("Agf.RequestInfoRaised","Agf.ResponseHandled","Agf.CheckpointRestoredMissingRequest")
| summarize Raised=countif(OperationName=="Agf.RequestInfoRaised"),
            Handled=countif(OperationName=="Agf.ResponseHandled"),
            MissingOnRestore=countif(OperationName=="Agf.CheckpointRestoredMissingRequest")
            by AgentId, bin(TimeGenerated, 1h)
| extend OrphanRate = round(100.0 * MissingOnRestore / Raised, 2)
| where MissingOnRestore > 0
```

**KQL-08 — Evidence-retention label coverage**
```kusto
AgentGovActivity
| where OperationName == "HitlReviewerDecision"
| extend Label = tostring(AdditionalProperties.RetentionLabel)
| summarize Total=count(), Labeled=countif(isnotempty(Label) and Label=="AgentGov-Evidence-212")
            by bin(TimeGenerated, 1d)
| extend CoveragePct = round(100.0 * Labeled / Total, 2)
| where CoveragePct < 100
```

### §2.4 Dataverse / SharePoint Queries

The firm's supervision register may be backed by a Dataverse table (recommended for Zone 3) or a SharePoint list (legacy). The following helper queries assume the Dataverse table `cr_agentsupervisionlog` or the SharePoint list `AgentSupervisionLog`.

```powershell
# Dataverse — pending reviews older than SLA
Get-Agt212ReviewQueue -Backend Dataverse -OlderThanMinutes 240

# SharePoint — full export for 3120 testing
Get-Agt212ReviewQueue -Backend SharePoint -SiteUrl https://contoso.sharepoint.com/sites/AIGovernance -ListName AgentSupervisionLog -ExportPath .\sup-log.csv
```

## §3 Pillar: HITL-NOT-FIRING

The Copilot Studio human-agent handoff, Power Automate approval action, or Agent Framework `request_info()` invocation does not fire when the firm's WSP says it should. This is the most consequential supervisory failure: an agent output reaches a customer **as if approved** when no principal has approved it.

### §3.1 Symptom Catalog

| Code | Symptom | Severity hint |
|---|---|---|
| **P3-S1** | Zone 3 agent returns investment recommendation to a customer; no review queue item was created; no principal attestation on the transcript | Sev1 |
| **P3-S2** | Agent Framework workflow completes without entering `awaitingResponse` state, despite the WSP pattern saying a `request_info()` should fire for the detected pattern | Sev1 |
| **P3-S3** | Copilot Studio topic with "Require human handoff" flag set returns directly to user without handoff | Sev1 |
| **P3-S4** | Power Automate approval flow triggers but agent does not wait — response is sent to user in parallel | Sev1 |
| **P3-S5** | HITL fires only for some trigger phrases listed in the WSP, not others | Sev2 |
| **P3-S6** | HITL fires correctly in the test environment but not production | Sev1 |
| **P3-S7** | KQL-01 shows `TriggerRatePct` dropped materially below the 30-day baseline without a WSP change | Sev2 |

### §3.2 Root Cause Matrix

| Code | Root cause | Confirmation signal |
|---|---|---|
| **RC-A** | **Trigger criteria mismatch.** The deployed agent's intent / topic / pattern does not reference the WSP trigger vocabulary (e.g., WSP says "route on 'investment advice'" but topic only matches "investing advice"). | `Get-Agt212HitlStatus -AgentId <id>` returns `TriggerCriteria` whose tokens do not match `Get-Agt212WspReconciliation -AgentId <id>`. |
| **RC-B** | **HITL pattern not wired.** The agent has no HITL configuration at all (Copilot Studio "Require handoff" is off; no Agent Framework `RequestPort` wired; no Power Automate approval action bound). | GQ-04 returns `hitlPattern: "none"` for an agent whose registry record says Zone 3. |
| **RC-C** | **Configuration drift post-republish.** The agent was republished and the HITL binding was lost (common when the author did not include the handoff topic in the solution import). | KQL-05 shows `WspReconciliation.Drift` for field `hitlPattern` after a recent publish event. |
| **RC-D** | **Power Automate flow disabled or in error.** The approval flow backing the agent is disabled, suspended, or has exceeded its run quota. | GQ-05 returns `state: "Suspended"` or `runs[].status: "Failed"` with quota-exceeded error. |
| **RC-E** | **Agent Framework handler wired but `request_info()` not called.** The workflow executor checks a condition that evaluates false for production traffic (e.g., compares against a feature-flag that is off in prod). | KQL-07 shows `Raised` zero while `Handled` zero and interaction volume non-zero; code review confirms gated call. |
| **RC-F** | **Wrong autonomy level.** Agent is declared `Recommend-Only` (no HITL needed) but in fact executes material actions; WSP misclassified the agent at onboarding. | `Get-Agt212AutonomyDeclaration -AgentId <id>` returns `Recommend-Only` but `Get-Agt212Agent` shows it has connectors that perform trades, moves money, or sends customer communications. |
| **RC-G** | **Generative-answers path bypass.** The HITL pattern is wired to the scripted-topic path, but the agent fell through to the generative-answers path on an unmatched intent, which has no handoff. | KQL-04 `BypassReason: "FellThroughToGenerativeAnswers"`. |
| **RC-H** | **Trigger suppression override.** A recent tenant-level "expedite" or "low-friction customer experience" toggle in Copilot Studio has overridden HITL. | Copilot Studio environment-level flag `SuppressHandoffForLowConfidence` set to `true`. |

### §3.3 Diagnostic Steps

1. **Capture evidence floor first** (`Invoke-Agt212EvidenceSnapshot -Stage Initial`). Do **not** remediate before evidence.
2. Run `Get-Agt212HitlStatus -AgentId <id> -Verbose`. Compare `TriggerCriteria`, `HitlPattern`, `ReviewerGroup` against the firm's WSP addendum for the agent's zone / business activity.
3. Run `Get-Agt212WspReconciliation -AgentId <id>`. Any `Drift` record → RC-C.
4. Inspect GQ-04 for Copilot Studio agents. If `hitlPattern: "none"` or trigger list empty → RC-A / RC-B.
5. Inspect GQ-05 for backing Power Automate flows. `Suspended` or quota-exceeded → RC-D.
6. Run KQL-04 for the affected agent; any non-empty `BypassReason` illuminates RC-G or RC-H.
7. Run KQL-01 for 30-day trend; sustained drop → RC-C / RC-H.
8. Review `Get-Agt212AutonomyDeclaration` and cross-reference against the agent's connectors and actions. Mismatch → RC-F.
9. If Agent Framework is involved, inspect the workflow code for the `request_info()` call and any gating conditions; run KQL-07.
10. **Determine blast radius.** Run `Get-Agt212Interaction -AgentId <id> -From <fault-start> -To <now> -Where 'ShouldHaveRouted=true AND ActuallyRouted=false'`. Every matching interaction is a **supervisory gap** for Legal disposition — do not treat remediation of the config as closure of the gap.

### §3.4 Resolution Steps

| Root cause | Resolution |
|---|---|
| RC-A | Edit topic / intent to include the complete WSP trigger vocabulary. Re-publish. Re-run `Get-Agt212WspReconciliation`; confirm zero drift. Document change in Change Advisory Board (CAB) record. |
| RC-B | Wire the HITL pattern per `Portal Walkthrough §2`. Use `Invoke-Agt212HitlRebind -AgentId <id> -Pattern <handoff|approval|guardrails> -ReviewerGroup <groupId> -WhatIf` first; execute after Compliance Officer co-sign. |
| RC-C | Re-apply WSP-sourced config via `Invoke-Agt212WspReconcile -AgentId <id> -WhatIf`. Confirm publish includes the handoff topic in the solution. Update deployment pipeline to include a post-publish HITL verification step. |
| RC-D | Re-enable or re-authorize the Power Automate flow. If quota-exceeded, escalate to Power Platform Admin for quota uplift; document temporary compensating control. |
| RC-E | Code change: remove gating condition on `request_info()` or make the gating condition explicit and test-covered. Require an Agent Framework test suite that asserts `request_info()` is called for every WSP-defined trigger. |
| RC-F | Re-classify agent autonomy per [Control 2.12 Autonomy Classification](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md). If `Fully-Autonomous` is being claimed, recall that this pattern is **out of scope at Agent 365 GA** — the agent should be retired or reduced to `Semi-Autonomous` with HITL. |
| RC-G | Add a generative-answers fallback that routes unmatched intents to handoff instead of free-form response, or restrict the agent's intent surface so unmatched intents are impossible. |
| RC-H | Revert the tenant-level suppression toggle; document the decision in the Risk Register if the toggle must remain for a subset of agents. **Do not** apply suppression to Zone 3. |

All resolutions require a post-remediation verification test (§3.5) before re-opening the agent to customer traffic. For any Sev1 HITL-NOT-FIRING incident on a customer-facing Zone 3 agent, **pause the agent** (disable publish) until remediation is verified. Document the pause as a change-control artifact.

### §3.5 Prevention

1. **WSP reconciliation gate in CI/CD.** Every agent publish must pass `Invoke-Agt212WspReconcile -WhatIf` in the pipeline; non-zero drift blocks publish.
2. **HITL unit test.** Every agent carries an automated test that submits each WSP trigger phrase and asserts that a review-queue item is created. Publish is blocked on test failure.
3. **30-day trigger-rate monitoring.** Alert on KQL-01 deviation > 20% from 30-day baseline.
4. **Autonomy-classification quarterly attestation.** Compliance Officer re-confirms each agent's autonomy declaration; mismatched connectors trigger reclassification.
5. **Bypass-event alert.** Any Zone 3 `HitlBypassed` event pages AI Governance Lead within 5 minutes.

### §3.6 Evidence to Capture

Append to the §21 bundle:

- **E-HITL-01** — `Get-Agt212HitlStatus` output at fault time and at recovery close.
- **E-HITL-02** — `Get-Agt212WspReconciliation` output at fault time.
- **E-HITL-03** — List of affected interactions (conversation IDs, user UPNs, timestamps) from `Get-Agt212Interaction` — this is the **supervisory-gap set** for Legal disposition.
- **E-HITL-04** — Post-remediation verification test transcript.
- **E-HITL-05** — CAB record for the configuration change.
- **E-HITL-06** — Compliance Officer co-sign attestation on remediation.

### §3.7 Cross-References

- §4 QUEUE-STUCK — if HITL fires but review never completes.
- §7 WSP-DRIFT — structural drift that underlies RC-A / RC-C.
- §8 R2210-MISCLASSIFICATION — if the missed HITL was a retail-communication pre-use approval.
- §16 RB-03 — post-incident HITL bypass runbook.
- [Control 1.5 — Data Loss Prevention and Sensitivity Labels](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) — if DLP is blocking the approval connector.
- [Control 3.4 — Incident Reporting and Root Cause Analysis](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) — upstream incident discipline.

---

## §4 Pillar: QUEUE-STUCK

The HITL fires correctly and review items land in the queue, but the queue backs up. Items age past SLA. The customer waits; the interaction may time out; reviewers are absent, misrouted, or the routing logic is looping.

### §4.1 Symptom Catalog

| Code | Symptom | Severity hint |
|---|---|---|
| **P4-S1** | Queue depth ≥ WSP threshold with oldest item > 2× SLA | Sev1 if examiner-active, Sev2 otherwise |
| **P4-S2** | Specific zone's queue is stalled while other zones process normally | Sev2 |
| **P4-S3** | Items appear in queue and immediately disappear without a reviewer decision | Sev1 (silent drop) |
| **P4-S4** | Reviewer opens item but approval-action submission returns 500 | Sev2 |
| **P4-S5** | Same item cycles through queue multiple times (routing loop) | Sev2 |
| **P4-S6** | Queue reports p95 age within SLA but KQL-02 shows p99 age orders-of-magnitude higher | Sev3 |
| **P4-S7** | Customer-facing agent has timed out waiting for reviewer response; customer sees error or truncated reply | Sev1 |

### §4.2 Root Cause Matrix

| Code | Root cause | Confirmation signal |
|---|---|---|
| **RC-A** | **Reviewer unavailability.** The assigned reviewer group is empty, has only absent members, or all PIM-eligible reviewers have expired activation. | `Get-Agt212PrincipalRoster -Current` intersected with GQ-06 for reviewer group returns no active member. |
| **RC-B** | **SLA clock misconfigured.** Approval-flow timeout is longer than the agent's response-wait window; reviewer answers after agent has already given up. | Power Automate flow definition shows `WaitForApproval` timeout > agent orchestration timeout. |
| **RC-C** | **Routing loop.** Reviewer's "Escalate" action routes back to the same group that originated the item (misconfigured escalation target). | KQL-02 shows oscillating queue depth with cycle count > 1 per item. |
| **RC-D** | **Queue backend full.** Dataverse or SharePoint list hit capacity; new items error on insert but existing items appear. | `Get-Agt212ReviewQueue -IncludeBackendDiagnostics` returns `storageQuotaExceeded: true`. |
| **RC-E** | **Power Automate flow throttled.** Too many concurrent runs; throttling errors in flow history. | GQ-05 `runs[].status: "Failed"` with `errorCode: "FlowRunQuotaExceeded"`. |
| **RC-F** | **Mailbox-routed approval broken.** Approval email never reaches reviewer (transport rule, spam filter, mailbox quota). | Message trace in Exchange admin center shows bounce / spam disposition. |
| **RC-G** | **Teams approval surface rendering bug.** Reviewer sees approval card in Teams but action buttons do not render or return error. | Teams admin center service incident advisory or reproducible repro on multiple clients. |
| **RC-H** | **Silent drop on insert.** Approval flow writes to a logging sink that errors silently; item appears transiently then is lost. | Flow run shows success, but Dataverse record not present; KQL-08 coverage gap. |

### §4.3 Diagnostic Steps

1. Evidence floor first.
2. Snapshot the queue: `Get-Agt212ReviewQueue -IncludeAge -ExportPath .\queue-snapshot.csv`.
3. Run KQL-02 for the past 24h. Determine whether p95 age is sustained above SLA or spiking.
4. Run `Get-Agt212PrincipalRoster -Current | Where-Object { $_.ReviewerGroupId -eq '<id>' }` for the queue's reviewer group. If empty → RC-A.
5. Inspect the Power Automate flow for the agent: GQ-05. Look at `runs[].status` distribution for the past 24h. Failures with throttling → RC-E.
6. Check Exchange message trace if the flow uses mailbox-routed approvals: `Get-MessageTrace -SenderAddress <flow-sender> -StartDate <t-1h>`.
7. For Teams-surfaced approvals, ask the affected reviewer to reproduce on a known-good client; if multi-client failure → RC-G, engage Microsoft Support.
8. Compare KQL-08 coverage against expected decision volume; divergence → RC-H.
9. If routing loops are suspected, run KQL-02 with `dcount(ItemId)` per item and look for items with > 1 appearance → RC-C.

### §4.4 Resolution Steps

| Root cause | Resolution |
|---|---|
| RC-A | `Invoke-Agt212QueueReassign -FromGroup <id> -ToGroup <backupGroupId> -WhatIf`. Activate backup reviewer PIM. Document the reviewer availability exception; update WSP if the backup group was not previously documented as a qualified pool. |
| RC-B | Align Power Automate flow timeout with agent orchestration timeout; SLA for Zone 3 should be ≤ agent response budget minus safety margin. Re-publish flow. |
| RC-C | Correct escalation target in Power Automate flow. Add a test case that simulates escalation and asserts no cycle. |
| RC-D | Archive / purge expired queue items per retention label; increase backend capacity; re-route new items. **Do not** delete items that are under examiner inquiry without Legal approval. |
| RC-E | Request quota uplift from Power Platform Admin; until uplift, throttle agent traffic or temporarily route via an alternate environment. |
| RC-F | Work with Exchange Online Admin to whitelist flow sender address; verify reviewer mailbox not over quota; test with secondary mail path. |
| RC-G | Engage Microsoft Support with repro data; until resolved, instruct reviewers to use Power Automate web approvals surface instead of Teams. |
| RC-H | Repair the logging sink error handling; audit the run history to identify dropped items; reconstruct lost interactions for Legal disposition. |

### §4.5 Prevention

1. **Backup reviewer groups.** Every reviewer group has a documented backup group; tested monthly via `Invoke-Agt212QueueReassign -WhatIf`.
2. **SLA alerting.** KQL-02 p95 > SLA alert fires within 15 minutes; page on-call.
3. **Throttling headroom.** Power Automate quota for the supervisory environment maintained at ≥ 3× peak observed.
4. **Silent-drop invariant.** Flow writes to Dataverse with transactional guarantees; write failures retry with dead-letter.
5. **Principal PIM continuity.** Designated principals maintain always-on (non-PIM-gated) access to the approval surface, or PIM eligibility with extended activation window; this is acceptable for a narrow "supervisory action" role scoped only to the review queue, subject to Entra Global Admin approval.

### §4.6 Evidence to Capture

- **E-Q-01** — Queue snapshot at fault time and at recovery close.
- **E-Q-02** — KQL-02 output for the fault window with p50/p95/p99.
- **E-Q-03** — Reviewer roster cross-reference showing coverage gap if RC-A.
- **E-Q-04** — Flow run history export if RC-D/E/H.
- **E-Q-05** — Post-remediation test transcript (reviewer assignment, decision, round-trip time).
- **E-Q-06** — Reconstructed list of dropped / delayed interactions for Legal.

### §4.7 Cross-References

- §3 HITL-NOT-FIRING — if the queue is empty because HITL never fired.
- §5 REVIEWER-UNQUALIFIED — if RC-A is resolved by reassignment to someone who is in fact not qualified.
- §6 ESCALATION-BROKEN — if the loop or misroute manifests in the escalation path.
- [Control 1.5 — Data Loss Prevention and Sensitivity Labels](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) — DLP blocking approval connector.

---

## §5 Pillar: REVIEWER-UNQUALIFIED

The reviewer who acted on a queue item lacks the current, valid qualification required by the WSP for the business activity reviewed. This includes expired Series 24 / 66 / 65 registrations, scope mismatches (BD reviewer approving RIA scope or vice versa), and reviewer-UPN reconciliation gaps where the acting UPN is not on the firm's current designated-principal roster.

### §5.1 Symptom Catalog

| Code | Symptom | Severity hint |
|---|---|---|
| **P5-S1** | KQL-03 returns reviewer UPNs not on the current principal roster | Sev1 |
| **P5-S2** | CRD extract shows a designated principal's Series 24 or 66 is in "Lapsed" or "Inactive" status | Sev1 |
| **P5-S3** | Reviewer approved a retail communication but is registered only for institutional scope | Sev1 |
| **P5-S4** | Reviewer UPN on record is a shared mailbox / service account rather than a natural person | Sev1 (cannot be reconciled to a registered human) |
| **P5-S5** | Reviewer's PIM role activation logs show an assumed identity (admin acting on behalf) | Sev1 (attribution gap) |
| **P5-S6** | WSP names reviewer by role title; CRD link cannot be established from role title alone | Sev2 |
| **P5-S7** | Reviewer is qualified but the attestation timestamp is > 90 days stale | Sev3 |

### §5.2 Root Cause Matrix

| Code | Root cause | Confirmation signal |
|---|---|---|
| **RC-A** | **Registration lapsed.** Continuing-education or annual compliance registration not completed. | FINRA CRD or WebCRD extract shows `status: "Inactive"` or `"Lapsed"`. |
| **RC-B** | **Scope mismatch.** Reviewer holds Series 24 only but is approving RIA-scope (Series 66 / 65) content, or vice versa. | WSP mapping says Series 66 required for this activity; reviewer holds Series 24 only. |
| **RC-C** | **Roster not updated.** New reviewer added to Entra group without being added to WSP roster and CRD-verified. | `Get-Agt212PrincipalRoster -Current` does not contain the reviewer UPN, but the Entra reviewer group does. |
| **RC-D** | **Shared mailbox used for approval.** Approval email routed to a shared mailbox; anyone with access to the mailbox could click Approve. | Mailbox type is `SharedMailbox`; no sign-in logs for the UPN. |
| **RC-E** | **Admin acting on behalf.** An AI Administrator clicked Approve "to unblock the customer"; Administrator is not a registered principal. | Entra sign-in log shows approver is in AI Administrator role but not in Designated Principal group. |
| **RC-F** | **Attestation expired.** Principal was qualified 6 months ago; attestation refresh missed. | `Get-Agt212PrincipalRoster -Current` `LastAttestation` > 90 days. |
| **RC-G** | **Principal deceased / departed / suspended.** UPN still active in directory due to HR lag. | HR system `TerminationDate` set; directory not yet de-provisioned. |

### §5.3 Diagnostic Steps

1. Evidence floor first.
2. Run KQL-03 for the fault window and the past 30 days. Enumerate every reviewer UPN present in decisions but absent from roster.
3. For each unknown UPN: `Get-MgUser -UserId <upn>` to determine if the UPN is a natural person, shared mailbox, or service account.
4. For each natural-person UPN: cross-reference against the firm's CRD / WebCRD extract. Determine registration status, series held, and effective dates.
5. For each approved interaction by an unqualified reviewer: flag the conversation ID as a **supervisory gap** for Legal disposition (same discipline as §3 HITL-NOT-FIRING — remediation of the roster does not retroactively qualify a past decision).
6. Run `Get-Agt212PrincipalRoster -Current` and compare `LastAttestation` timestamps; any > 90 days → RC-F.
7. If RC-E suspected, compare the acting UPN's role bindings via GQ-06 against the Designated Principal group.
8. If RC-D suspected, review mailbox permissions and sign-in history for the shared mailbox to identify the natural person who actually clicked Approve — this may not be possible (shared mailboxes often cannot be attributed), which is itself the finding.

### §5.4 Resolution Steps

| Root cause | Resolution |
|---|---|
| RC-A | Immediate: remove reviewer from reviewer Entra group via `Remove-MgGroupMember`. Reassign pending items via `Invoke-Agt212QueueReassign`. Notify Compliance Officer; principal completes CE / reinstatement before re-addition. Document the fault window and the decisions made during it for Legal review. |
| RC-B | Same immediate removal; add a qualified principal of correct scope; update WSP to make the scope-to-activity mapping explicit and auto-enforced. |
| RC-C | Back-date the roster addition is **not** acceptable. Enter the reviewer on the current-dated roster only after CRD verification; decisions made prior to that date by that reviewer are supervisory gaps. |
| RC-D | Replace shared-mailbox approval route with named-reviewer routing (Teams or direct-UPN approval). Document every past approval that routed through the shared mailbox as unattributable; Legal disposes. |
| RC-E | Remove admin from reviewer group; update Entra Conditional Access to make the approval action unavailable to AI Administrator role; institute SoD check in CAB for future role assignments. |
| RC-F | Run the attestation refresh; capture signed attestation; update roster. |
| RC-G | De-provision UPN; update roster; reconcile any pending items. |

### §5.5 Prevention

1. **CRD sync.** A quarterly automated feed from WebCRD to the firm's principal-roster system; `Get-Agt212PrincipalRoster -Current` trusts this feed.
2. **Attestation pipeline.** Entra Access Reviews quarterly on the reviewer group, with review due dates aligned to the 90-day roster freshness requirement.
3. **Role gating at the Entra level.** The reviewer Entra group membership is restricted to accounts carrying a firm-issued `finra-principal-series: 24|66|65` attribute, populated by the CRD sync.
4. **Reviewer-UPN-only routing.** Approval actions never route to shared mailboxes, distribution lists, or service accounts. Verified in CAB pre-publish.
5. **Immediate-removal playbook.** When a principal's registration lapses, the removal from the reviewer Entra group must occur within 1 business hour of the lapse event, enforced by automation (`Start-Agt212PrincipalOffboard`).

### §5.6 Evidence to Capture

- **E-PR-01** — CRD / WebCRD extract at fault time.
- **E-PR-02** — Roster snapshot at fault time and at recovery close.
- **E-PR-03** — List of decisions made by unqualified reviewers during the fault window (supervisory-gap set for Legal).
- **E-PR-04** — Entra group membership diff at fault time and at recovery close.
- **E-PR-05** — Replacement principal attestation.
- **E-PR-06** — SoD CAB record if RC-E.

### §5.7 Cross-References

- §15 RB-02 — principal lapse mid-quarter runbook.
- §4 QUEUE-STUCK — RC-A coverage gap relates to queue availability.
- §10 SPONSOR-ATTESTATION-FAIL — sponsor qualification has a separate discipline from principal qualification; both apply.
- [Control 1.7 — Comprehensive Audit Logging and Compliance](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) — enforces audit-trail capture for principal decisions.

---

## §6 Pillar: ESCALATION-BROKEN

Reviewer chooses Escalate (Reject with elevation) on a queue item but the escalation does not reach the correct higher-qualified principal or group. Routing is misconfigured, the escalation group is empty, or the escalation path is missing altogether.

### §6.1 Symptom Catalog

| Code | Symptom | Severity hint |
|---|---|---|
| **P6-S1** | Reviewer escalates; no item appears in escalation queue | Sev1 |
| **P6-S2** | Escalation lands in a group whose members are at same qualification level as the original reviewer | Sev1 |
| **P6-S3** | Escalation SLA (typically 1 business hour for Zone 3) is breached repeatedly | Sev1 |
| **P6-S4** | Escalation routes to a disabled Teams channel | Sev2 |
| **P6-S5** | No escalation action available on the reviewer's surface (UI button missing) | Sev1 |
| **P6-S6** | Escalation bounces back to originating queue (loop) | Sev2 |
| **P6-S7** | Escalation reaches Compliance but no Legal cc for customer-impacting Zone 3 flags | Sev2 |

### §6.2 Root Cause Matrix

| Code | Root cause | Confirmation signal |
|---|---|---|
| **RC-A** | **Escalation target group empty.** Group was decommissioned or membership drained. | `Get-MgGroupMember -GroupId <escalationGroupId>` returns empty. |
| **RC-B** | **Escalation group unqualified.** Group members are at same level as original reviewer. | Cross-reference group members against principal roster. |
| **RC-C** | **Routing expression wrong.** Power Automate `Switch` on zone / risk value does not cover the actual value produced. | Flow run shows default branch hit when a specific zone / risk branch was expected. |
| **RC-D** | **Escalation action disabled in UI.** Copilot Studio or Teams approval card definition is missing the Escalate button. | GQ-04 `hitlActions` array does not include `"escalate"`. |
| **RC-E** | **Escalation notification channel broken.** Email / Teams channel for escalations is deleted or filtered. | Power Automate flow run log: notification step fails. |
| **RC-F** | **No Legal cc configured.** Firm WSP requires Legal notification for Zone 3 customer-impacting escalations; not wired. | GQ-05 flow definition has no Legal recipient. |
| **RC-G** | **Cascade loop.** Escalation target group is itself a member of the originating group. | Entra nested group analysis. |

### §6.3 Diagnostic Steps

1. Evidence floor first.
2. `Get-Agt212HitlStatus -AgentId <id>` — inspect `EscalationGroup` and `EscalationAction` fields.
3. `Get-MgGroupMember -GroupId <escalationGroupId>` — confirm non-empty.
4. Cross-reference members against principal roster (each must hold series strictly higher qualification than originator's).
5. Flow run inspection: pick a recent escalation, open the run, determine which branch fired.
6. Teams channel / mailbox check for notification sink.
7. KQL-04 filtered to `BypassReason: "EscalationPathMissing"` or similar codes.

### §6.4 Resolution Steps

| Root cause | Resolution |
|---|---|
| RC-A | Populate the group with qualified principals per WSP; add monitoring on group membership count. |
| RC-B | Redefine escalation matrix so escalation levels are strictly increasing qualification. Typically: reviewer (Series 24) → senior principal (Series 24 + supervisory tenure) → Compliance Officer → CCO + Legal. |
| RC-C | Fix the flow routing expression; add test cases covering every risk / zone value; publish. |
| RC-D | Add Escalate action in Copilot Studio agent or Teams approval card; re-publish. |
| RC-E | Restore the notification channel; add heartbeat test that posts a test message daily and alerts on failure. |
| RC-F | Wire Legal recipient; document in WSP which events trigger Legal cc. |
| RC-G | Flatten nested groups; enforce no-cycle invariant via Entra group-governance policy. |

### §6.5 Prevention

1. **Escalation test case.** Monthly synthetic escalation test that walks the full escalation path and asserts arrival.
2. **Membership floor.** Escalation groups maintain ≥ 3 qualified members with documented backup.
3. **WSP-to-flow invariant.** A linter compares WSP-declared escalation matrix against Power Automate flow routing; divergence blocks publish.
4. **Legal-cc policy codified.** Firm rule: any customer-impacting Zone 3 reject-or-escalate action ccs Legal. Enforced in flow.

### §6.6 Evidence to Capture

- **E-ESC-01** — Escalation matrix from WSP vs deployed flow config.
- **E-ESC-02** — Group membership snapshot.
- **E-ESC-03** — Flow run history for escalations in fault window.
- **E-ESC-04** — Synthetic test transcript at recovery close.

### §6.7 Cross-References

- §3 HITL-NOT-FIRING, §4 QUEUE-STUCK — upstream of escalation.
- §5 REVIEWER-UNQUALIFIED — if escalation targets are themselves unqualified.
- [Control 3.4 — Incident Reporting and Root Cause Analysis](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md).

---

## §7 Pillar: WSP-DRIFT

The deployed supervisory configuration (Copilot Studio handoff topic, Agent Framework handlers, Power Automate approval flow, reviewer groups, autonomy classification, 2210 classification) differs from what the firm's WSP addendum says it should be. This is both a standalone pillar and the upstream root cause for many §3 / §7 / §8 incidents.

### §7.1 Symptom Catalog

| Code | Symptom | Severity hint |
|---|---|---|
| **P7-S1** | `Get-Agt212WspReconciliation` returns drift records for one or more Zone 3 agents | Sev2 (Sev1 if examiner-active) |
| **P7-S2** | WSP addendum references a trigger phrase, reviewer group, or classification that does not exist in the deployed agent | Sev2 |
| **P7-S3** | Deployed agent has configuration (e.g., a connector, an action, an autonomy level) that is not referenced in the WSP | Sev2 |
| **P7-S4** | Quarterly WSP attestation fails because reconciliation artifact is missing for one or more agents | Sev2 |
| **P7-S5** | Post-publish drift: an agent that was in WSP alignment yesterday is out of alignment today without a WSP change | Sev1 |
| **P7-S6** | WSP has been updated but the deployment has not caught up | Sev2 |
| **P7-S7** | Multiple agents share a WSP addendum but only some have been reconciled after the last WSP revision | Sev2 |

### §7.2 Root Cause Matrix

| Code | Root cause | Confirmation signal |
|---|---|---|
| **RC-A** | **WSP updated, deploy lagged.** Compliance amended the WSP but agent publish pipeline has not yet reconciled. | WSP document version > deployed config version; `Get-Agt212WspReconciliation` `Field: "WspVersion"` drift. |
| **RC-B** | **Deploy updated, WSP lagged.** Engineer added a new connector / trigger without updating WSP. | WSP has no mention of the deployed config element. |
| **RC-C** | **Manual edit in Copilot Studio.** Author edited the agent directly in Copilot Studio bypass the CI/CD pipeline; change was not reflected in WSP. | Copilot Studio audit log shows edit by non-pipeline UPN. |
| **RC-D** | **Republish without solution.** Author republished an older solution that lacks the latest handoff topic. | Publish event correlated with drift appearing. |
| **RC-E** | **Template restored from backup.** Environment restore or solution rollback brought in stale config. | Environment operation log shows restore event. |
| **RC-F** | **Partial rollout.** New WSP version applied to some agents (one zone, one business line) but not others. | Reconciliation passes for subset; fails for others. |
| **RC-G** | **Manual override by AI Administrator.** Admin adjusted a config "temporarily" without WSP change. | Admin-action audit log. |

### §7.3 Diagnostic Steps

1. Evidence floor.
2. `Get-Agt212WspReconciliation -Scope Tenant -ExportPath .\drift-report.csv` — this produces the authoritative drift report across all agents.
3. For each drift record: determine which direction (WSP ahead of deploy vs deploy ahead of WSP) and the field affected.
4. For fields that affect HITL enforcement: upgrade to Sev1 pending customer-facing blast-radius assessment.
5. For agents with drift, freeze publish until remediation.
6. Review the last 30 days of publish events against drift appearance to correlate cause (RC-C / RC-D / RC-E).

### §7.4 Resolution Steps

| Root cause | Resolution |
|---|---|
| RC-A | Invoke `Invoke-Agt212WspReconcile -AgentId <id> -Direction WspToDeploy -WhatIf`, execute after Compliance co-sign, verify drift is zero. |
| RC-B | Either update WSP to reflect the new config (Compliance + Legal + Designated Principal co-sign) or revert the deploy to match WSP. The "right" direction depends on whether the new config is something the firm actually wants (WSP updates) or an unapproved addition (revert). |
| RC-C | Revert via the CI/CD pipeline; disable Copilot Studio direct-edit privilege for the agent; document the finding; require the author to requalify on the change-control process. |
| RC-D | Republish the latest solution via the pipeline; verify drift zero. |
| RC-E | Rebuild from CI/CD; disable environment restore privileges outside the change-control process. |
| RC-F | Complete the rollout; reconcile each laggard agent. |
| RC-G | Revert the override; document; if the override was necessary for a valid reason, formalize it through the CAB and WSP update process. |

### §7.5 Prevention

1. **CI/CD-only publish invariant.** No Copilot Studio direct edits in production; enforced via Power Platform environment role scoping.
2. **WSP-version attribute.** Every agent carries a `wspVersion` metadata tag; pipeline asserts match before publish.
3. **Weekly reconciliation report.** `Get-Agt212WspReconciliation` run weekly; report to AI Governance Lead + Compliance Officer; non-zero drift is a ticket.
4. **WSP-update-to-deploy SLA.** Firm-defined SLA (typically 5 business days for non-emergency, 1 business day for examiner-driven) from WSP approval to deploy reconciliation.

### §7.6 Evidence to Capture

- **E-WSP-01** — Drift report at fault time.
- **E-WSP-02** — WSP version and deployed version for each affected agent.
- **E-WSP-03** — CAB record for the remediation.
- **E-WSP-04** — Compliance co-sign attestation.
- **E-WSP-05** — Post-remediation reconciliation (zero drift).

### §7.7 Cross-References

- §3 HITL-NOT-FIRING — drift manifests as HITL failure.
- §8 R2210-MISCLASSIFICATION — drift in classification field.
- §9 AUTONOMY-MISMATCH — drift in autonomy declaration.
- [Control 2.13 — Documentation and Record-Keeping](../../../controls/pillar-2-management/2.13-documentation-and-record-keeping.md).

---

## §8 Pillar: R2210-MISCLASSIFICATION

An agent output was classified as Correspondence (post-use review acceptable) when it should have been classified as Retail Communication (principal pre-use approval required, subject to Rule 2210(b)(1) enumerated exclusions), or Institutional when it should have been Retail. Misclassification exposes the firm to a Rule 2210 violation independent of any HITL failure.

### §8.1 Symptom Catalog

| Code | Symptom | Severity hint |
|---|---|---|
| **P8-S1** | KQL-06 returns events where `RetailAudienceCount > 25` but `ClassificationApplied == "Correspondence"` | Sev1 |
| **P8-S2** | Agent template marked "Institutional" is in fact deployed to a Zone 3 retail-facing experience | Sev1 |
| **P8-S3** | WSP addendum's classification for a template differs from the deployed classification | Sev2 |
| **P8-S4** | Classification was correct at the template level but the agent's distribution reached > 25 retail investors without re-classification | Sev1 |
| **P8-S5** | Firm's marketing-review system lacks a principal pre-use approval record for an agent output that is a retail communication | Sev1 |
| **P8-S6** | Reliance on a Rule 2210(b)(1) exclusion documented, but the exclusion's conditions are not actually met | Sev1 |
| **P8-S7** | Firm has no audit trail connecting agent output to 2210 classification decision | Sev1 (audit gap) |

### §8.2 Root Cause Matrix

| Code | Root cause | Confirmation signal |
|---|---|---|
| **RC-A** | **Audience threshold crossed without re-classification.** Template was "Correspondence" when audience was small; audience grew past 25 retail investors over a 30-day window; classification did not update. | Audience-tracking system shows threshold crossing; classification record unchanged. |
| **RC-B** | **Template-level classification wrong.** Classification was made by someone lacking authority, or based on incomplete audience understanding. | Classification metadata shows non-principal author; no signature. |
| **RC-C** | **Institutional misapplied.** Agent declared Institutional but distribution channel permits retail access. | Channel metadata (Copilot Studio channel bindings) includes retail-facing surface. |
| **RC-D** | **Exclusion reliance unfounded.** Firm relied on Rule 2210(b)(1) exclusion (e.g., previously approved template) but the output was materially altered by the agent. | Comparison of delivered output vs previously approved template shows material differences. |
| **RC-E** | **Pre-use approval missed.** Classification correct but the pre-use approval workflow did not fire. | HITL queue has no record for this template. |
| **RC-F** | **WSP not aligned to FINRA 2210 current guidance.** Firm WSP has stale classification criteria. | WSP last-updated date predates a relevant FINRA notice. |
| **RC-G** | **Counting window wrong.** Firm counted unique retail recipients per channel rather than aggregate across channels within the 30-day window. | Reconciliation against aggregate recipient logs. |

### §8.3 Diagnostic Steps

1. Evidence floor.
2. KQL-06 for the past 90 days; enumerate every flagged event.
3. `Get-Agt212R2210Classification -TemplateId <id>` — confirm classification metadata.
4. For each flagged event, reconstruct the audience count from distribution logs and validate the 30-day window counting.
5. For exclusion reliance: retrieve the exclusion documentation and compare delivered content to approved template.
6. For missing pre-use approvals: cross-reference queue for the relevant window.
7. Produce the Legal-disposition set: every interaction that was a retail communication delivered without pre-use approval.

### §8.4 Resolution Steps

| Root cause | Resolution |
|---|---|
| RC-A | Implement audience-threshold monitoring that re-classifies templates automatically when 25-retail threshold approaches; pause distribution pending re-classification; principal performs retroactive review. |
| RC-B | Re-classify with principal signature; update template metadata; retrain author. |
| RC-C | Scope agent to Institutional-only channels; remove retail-facing surface bindings; update WSP. |
| RC-D | Withdraw the exclusion reliance; route output through pre-use approval going forward; Legal dispose of past reliance. |
| RC-E | Wire pre-use approval into the template's publish path; test end-to-end. |
| RC-F | Update WSP to current FINRA 2210 guidance; train principals; reconcile all active templates against the new criteria. |
| RC-G | Correct counting logic; build an aggregate recipient view; re-run last 90 days against the new view to surface additional misclassifications. |

### §8.5 Prevention

1. **Automatic audience monitoring.** Distribution logs feed a 30-day rolling counter per template; crossing 25 retail recipients triggers re-classification review automatically.
2. **Classification required at publish.** Copilot Studio or Agent Framework publish blocked unless template has a signed classification.
3. **Exclusion-reliance registry.** Firm maintains a registry of every template relying on Rule 2210(b)(1) exclusion, with the specific exclusion paragraph cited, the approved content hash, and quarterly re-verification by a principal.
4. **WSP-to-FINRA mapping review.** WSP reviewed against the latest FINRA 2210 notices and regulatory-oversight reports at least annually; additional reviews triggered by new FINRA guidance.
5. **KQL-06 alerting.** Continuous monitoring with alerting on the Sev1 condition.

### §8.6 Evidence to Capture

- **E-R22-01** — Classification metadata for each flagged template.
- **E-R22-02** — Audience counts reconstructed from distribution logs.
- **E-R22-03** — Principal pre-use approval records where present; gaps flagged.
- **E-R22-04** — Exclusion-reliance documentation.
- **E-R22-05** — Legal disposition log for retail communications delivered without pre-use approval.
- **E-R22-06** — Updated WSP and classification metadata after remediation.

### §8.7 Cross-References

- §3 HITL-NOT-FIRING — when pre-use approval itself is the failure mode.
- §7 WSP-DRIFT — classification drift as structural cause.
- §17 RB-04 — post-incident 2210 runbook.
- [Control 2.13 — Documentation and Record-Keeping](../../../controls/pillar-2-management/2.13-documentation-and-record-keeping.md).

---

## §9 Pillar: AUTONOMY-MISMATCH

An agent is classified at an autonomy level that does not match its actual behavior, or is classified at a level (notably Fully-Autonomous) that is not supported by the platform's GA configuration. FINRA's 2026 Annual Regulatory Oversight Report emphasizes that supervisory procedures must be tailored to autonomy level — a misclassification undermines the supervisory approach.

### §9.1 Symptom Catalog

| Code | Symptom | Severity hint |
|---|---|---|
| **P9-S1** | Agent declared Recommend-Only but executes transfers, trades, communications without human approval | Sev1 |
| **P9-S2** | Agent declared Fully-Autonomous in Zone 3 production without the exceptional-controls documentation required by Control 2.12 | Sev1 |
| **P9-S3** | Agent in Z3 is Fully-Autonomous at Agent 365 GA (out-of-scope pattern) | Sev1 |
| **P9-S4** | Autonomy declaration is Semi-Autonomous but material-decision threshold is set above anything the agent actually does (no real HITL ever fires) | Sev2 |
| **P9-S5** | Autonomy changed during publish without WSP update | Sev2 |
| **P9-S6** | No autonomy declaration at all | Sev2 |

### §9.2 Root Cause Matrix

| Code | Root cause | Confirmation signal |
|---|---|---|
| **RC-A** | **Onboarding classification error.** Agent classified without review of connectors and actions. | `Get-Agt212AutonomyDeclaration` Recommend-Only; `Get-Agt212Agent` connectors list includes non-read-only connectors. |
| **RC-B** | **Connector added after classification.** New connector pushed agent into higher autonomy without reclassification. | Connector-add event after last autonomy declaration. |
| **RC-C** | **Material-threshold too high.** Threshold set to bypass HITL. | Threshold comparison against observed action value distribution. |
| **RC-D** | **Fully-Autonomous out-of-scope pattern.** Preview-only autonomous-identity pattern deployed in Z3. | Agent identity type = autonomous per Entra Agent ID; zone = Z3. |
| **RC-E** | **Declaration absent.** Agent onboarded before autonomy classification was required. | `Get-Agt212AutonomyDeclaration` returns null. |
| **RC-F** | **Exceptional-controls documentation missing.** Fully-Autonomous declared with documentation that is stale, unsigned, or otherwise non-conformant. | Documentation artifact missing or incomplete. |

### §9.3 Diagnostic Steps

1. Evidence floor.
2. `Get-Agt212AutonomyDeclaration -Scope Tenant -ExportPath .\autonomy.csv` — produces autonomy declarations for all agents.
3. Cross-reference declared autonomy vs agent connectors and actions; build a "declared vs observed" matrix.
4. For Fully-Autonomous in Z3: produce the exceptional-controls documentation set (real-time monitoring, exception alerting, pre-deployment principal approval, 100% post-use review) and validate each.
5. If agent uses Entra Agent ID autonomous-identity pattern, confirm scope: this pattern is Preview at Agent 365 GA and out-of-scope for Z3 production.

### §9.4 Resolution Steps

| Root cause | Resolution |
|---|---|
| RC-A | Re-classify to appropriate level (typically Semi-Autonomous); add HITL for material actions. |
| RC-B | Re-classify; if additional controls are needed, add them before re-opening the agent. |
| RC-C | Lower the threshold to a defensible level; principal attests to the threshold based on observed action-value distribution. |
| RC-D | **Retire the Fully-Autonomous Z3 agent** until Microsoft publishes GA guidance for the autonomous-identity pattern. Reduce to Semi-Autonomous with HITL, or move to Z2. |
| RC-E | Classify now; update registry; apply supervision requirements for the new level. |
| RC-F | Produce the documentation (or retire the agent to a supported autonomy level). Documentation must be signed by Designated Principal and AI Governance Lead. |

### §9.5 Prevention

1. **Autonomy declaration required at onboarding.** Registration (Control 3.1) blocks without a declaration.
2. **Connector-change triggers reclassification.** New connector invokes a CAB step that re-evaluates autonomy.
3. **Fully-Autonomous gate.** Platform-level gate preventing Fully-Autonomous declaration in Z3 until Microsoft publishes GA guidance.
4. **Quarterly attestation.** Compliance Officer re-attests each agent's autonomy declaration quarterly.

### §9.6 Evidence to Capture

- **E-AUT-01** — Autonomy declarations at fault time.
- **E-AUT-02** — Declared vs observed matrix.
- **E-AUT-03** — Exceptional-controls documentation set for Fully-Autonomous agents.
- **E-AUT-04** — Reclassification attestation.
- **E-AUT-05** — Retired-agent record if RC-D.

### §9.7 Cross-References

- [Control 2.12 — AI Agent Autonomy Levels](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md).
- [Control 2.25 — Agent 365 GA Scope](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md).
- §3 HITL-NOT-FIRING — autonomy misclassification manifests as missing HITL.

---

## §10 Pillar: SPONSOR-ATTESTATION-FAIL

The Entra Agent ID sponsor for an agent has departed, been disabled, or has not attested within the firm's quarterly window, leaving the agent without the lifecycle-accountability layer that Control 2.26 provides as a complement to Control 2.12 supervision. FINRA 3110 does not require sponsorship — it requires principal supervision — but the firm's WSP may have wired sponsorship as part of its overall supervisory posture, and a sponsor gap degrades the broader accountability chain.

### §10.1 Symptom Catalog

| Code | Symptom | Severity hint |
|---|---|---|
| **P10-S1** | Sponsor UPN is disabled in Entra but agent remains active | Sev1 if Z3 |
| **P10-S2** | Sponsor attestation > 90 days stale | Sev2 |
| **P10-S3** | Sponsor departed per HR feed; no replacement attestation filed | Sev1 if Z3 |
| **P10-S4** | Agent has no sponsor assigned | Sev2 |
| **P10-S5** | Sponsor is a distribution list / service account / shared mailbox | Sev1 |
| **P10-S6** | Sponsor reassignment was automatic-default to the AI Administrator | Sev1 (SoD violation) |
| **P10-S7** | Multiple sponsors of record; most-recent attestation from a sponsor no longer with the firm | Sev2 |

### §10.2 Root Cause Matrix

| Code | Root cause | Confirmation signal |
|---|---|---|
| **RC-A** | Sponsor departure; no Lifecycle Workflow re-assignment. | HR `TerminationDate`; Entra Lifecycle Workflow ran but took no action (notification-only by default). |
| **RC-B** | Attestation workflow not scheduled. | No Access Review record for the sponsor group. |
| **RC-C** | Agent onboarded without sponsor. | `Get-Agt212SponsorState` returns null. |
| **RC-D** | Sponsor designated as non-human identity. | UPN resolves to non-human account type. |
| **RC-E** | Automatic default reassignment. | Reassignment actor = service principal or AI Administrator. |
| **RC-F** | Sponsor was never qualified. | Sponsor UPN is not on the firm's qualified-sponsor roster. |

### §10.3 Diagnostic Steps

1. Evidence floor.
2. `Get-Agt212SponsorState -Scope Tenant` for all Z3 agents.
3. Cross-reference sponsor UPN against current HR directory (employment status, role).
4. Pull Entra Lifecycle Workflow history for the sponsor group; note notification-only actions.
5. For the affected agents, identify the sponsorship gap duration; this is the window of degraded accountability for Legal / Compliance reference.

### §10.4 Resolution Steps

| Root cause | Resolution |
|---|---|
| RC-A | Assign replacement sponsor with attestation; update registry; document gap duration. If prolonged (> firm SLA), raise as supervisory-control incident. |
| RC-B | Schedule quarterly Access Reviews on the sponsor group. |
| RC-C | Retroactive sponsor assignment; agent onboarding pipeline updated to require sponsor. |
| RC-D | Replace with named human sponsor; do not accept non-human sponsors for Z3. |
| RC-E | Revert to human sponsor; disable auto-default in workflow; enforce that reassignment must be by human actor. |
| RC-F | Add sponsor to qualified-sponsor roster after verification (role, training, attestation), or replace sponsor. |

### §10.5 Prevention

1. **HR feed integration.** Real-time or daily HR feed into Entra Lifecycle Workflow triggers sponsor re-assignment request within 1 business day of departure.
2. **Backup sponsor required.** Every Z3 agent has primary and backup sponsor.
3. **Quarterly Access Reviews** on sponsor group, aligned with Control 2.26.
4. **No-autonomous-default.** Auto-default to a service account or AI Administrator is prohibited.

### §10.6 Evidence to Capture

- **E-SP-01** — Sponsor state at fault time.
- **E-SP-02** — HR feed record for departure event.
- **E-SP-03** — Replacement sponsor attestation.
- **E-SP-04** — Gap-duration log for Compliance disposition.
- **E-SP-05** — Updated Access Review schedule.

### §10.7 Cross-References

- [Control 2.26 — Entra Agent ID Identity Governance](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md).
- [Control 3.6 — Orphaned Agent Detection and Remediation](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md).
- §20 RB-07 — sponsor cascade runbook.

---

## §11 Pillar: EVIDENCE-GAP

Reviewer decision evidence is missing, incomplete, or below-retention for an interaction that requires a 6-year supervisory record under FINRA 4511 / SEC 17a-4(b)(4). This pillar catches the tail risks that undermine every other pillar: even if HITL fires, queue processes, and reviewer is qualified, a gap in the evidence layer means the firm cannot demonstrate supervision to an examiner.

### §11.1 Symptom Catalog

| Code | Symptom | Severity hint |
|---|---|---|
| **P11-S1** | Reviewer UPN is null for a decision | Sev1 |
| **P11-S2** | Rationale field is null / empty for a decision | Sev1 |
| **P11-S3** | Retention label on supervision record is not `AgentGov-Evidence-212` or equivalent 6yr-WORM label | Sev1 |
| **P11-S4** | Audit export cannot produce decision records for a requested date range | Sev1 |
| **P11-S5** | Timestamp missing timezone; ambiguous | Sev2 |
| **P11-S6** | Decision cannot be traced to originating agent interaction / conversation ID | Sev1 |
| **P11-S7** | Decision cannot be traced to originating Agent Framework request ID + checkpoint | Sev1 (if Agent Framework) |
| **P11-S8** | Retention label applied but Purview retention policy is not in enforced state | Sev1 |

### §11.2 Root Cause Matrix

| Code | Root cause | Confirmation signal |
|---|---|---|
| **RC-A** | Flow writes decision before binding reviewer UPN. | Flow definition places `AddRecord` step before `GetApproverIdentity`. |
| **RC-B** | Rationale not required in UI / flow. | Flow definition shows `Rationale` as optional. |
| **RC-C** | Retention label not applied. | Records created without label; KQL-08 coverage < 100%. |
| **RC-D** | Retention policy is in `TestMode` or `Disabled`. | `Get-RetentionCompliancePolicy` shows non-enforced state. |
| **RC-E** | Records stored in a location not covered by retention policy. | Location mismatch between flow sink and policy scope. |
| **RC-F** | Timestamps recorded in local time without TZ offset. | Schema review. |
| **RC-G** | Agent interaction logs and supervision logs do not share a correlation ID. | Correlation-ID field missing. |
| **RC-H** | Agent Framework request / checkpoint IDs not persisted alongside reviewer decision. | Schema gap. |

### §11.3 Diagnostic Steps

1. Evidence floor.
2. `Get-Agt212Evidence -ConversationId <id>` for a sample set — validate all fields present.
3. KQL-08 for retention-label coverage.
4. `Get-RetentionCompliancePolicy -Identity AgentGov-Evidence-212` (Purview Compliance Admin or Exchange Online Admin role required) — verify enforced.
5. Test evidence production: simulate an examiner request for a named customer interaction — can the firm produce reviewer UPN, timestamp (with TZ), decision, rationale, and link to originating agent interaction within 2 business hours?

### §11.4 Resolution Steps

| Root cause | Resolution |
|---|---|
| RC-A | Fix flow step order; all decision records must include reviewer UPN at creation. Back-fill where reconstructible; log unreconstructible records for Legal. |
| RC-B | Make rationale mandatory in flow and UI; enforce minimum character length. |
| RC-C | Apply retention label via Purview `Set-RetentionComplianceRule` on the sink; back-fill with `Start-RetentionLabelBackfill`. |
| RC-D | Enforce the retention policy via Purview Compliance Admin; document the transition. |
| RC-E | Move records to covered location or expand policy scope. |
| RC-F | Switch all timestamps to ISO 8601 UTC; add TZ offset. |
| RC-G | Add correlation ID to schema; pipeline must populate for every record. |
| RC-H | Add request ID and checkpoint ID to schema; populate from Agent Framework `request_info()` result. |

### §11.5 Prevention

1. **Evidence-schema contract.** Every supervision record conforms to a documented schema with required fields (reviewer UPN, timestamp ISO 8601 UTC, decision, rationale, agent ID, conversation ID, correlation ID, AGF request ID where applicable, retention label). Schema enforcement in flow.
2. **Daily evidence-integrity test.** Synthetic test creates an approval, retrieves the record, validates every field; alert on any gap.
3. **Retention-policy heartbeat.** Daily probe of `Get-RetentionCompliancePolicy` confirms `Enabled: true` and scope covers expected locations.
4. **Examiner-mock drill.** Quarterly: pull a random customer interaction from the prior quarter; attempt to produce the full evidence bundle within 2 business hours; track success rate.

### §11.6 Evidence to Capture

- **E-EV-01** — Schema validation report.
- **E-EV-02** — Retention policy state snapshot.
- **E-EV-03** — KQL-08 coverage report.
- **E-EV-04** — List of records with evidence gaps (back-fill log for unreconstructible records).
- **E-EV-05** — Quarterly mock-drill result.

### §11.7 Cross-References

- [Control 1.7 — Comprehensive Audit Logging and Compliance](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md).
- [Control 2.13 — Documentation and Record-Keeping](../../../controls/pillar-2-management/2.13-documentation-and-record-keeping.md).
- §19 RB-06 — surprise Z3 audit runbook.

---

## §12 Pillar: AGF-CHECKPOINT-LOSS

Microsoft Agent Framework supports human-in-the-loop via `RequestPort` / `request_info()` with pending requests preserved in checkpoints. When a workflow is restored from a checkpoint, pending requests should be re-emitted so supervisory review can resume. This pillar covers the failure mode where checkpoints are not persisted, not restored cleanly, or the request/response pair becomes orphaned — leaving an interaction in a supervisory limbo state.

### §12.1 Symptom Catalog

| Code | Symptom | Severity hint |
|---|---|---|
| **P13-S1** | `request_info()` invoked but no checkpoint written | Sev1 |
| **P13-S2** | Workflow restored; pending requests not re-emitted; items lost | Sev1 |
| **P13-S3** | Response handler received a response for a request ID with no originating checkpoint | Sev1 (orphan response) |
| **P13-S4** | Response payload received but workflow did not resume | Sev1 |
| **P13-S5** | Checkpoint storage backend returns errors | Sev1 |
| **P13-S6** | Request ID collision across workflows | Sev2 |
| **P13-S7** | Checkpoint contains pending requests older than retention | Sev2 |

### §12.2 Root Cause Matrix

| Code | Root cause | Confirmation signal |
|---|---|---|
| **RC-A** | Checkpoint not persisted — code path exits before checkpoint write. | Trace shows `request_info()` return without checkpoint op. |
| **RC-B** | Checkpoint backend (durable storage) misconfigured. | GQ-01 service status degraded; storage errors. |
| **RC-C** | Workflow identity / scope not preserved; restore loads different scope. | Request ID present but belongs to different workflow key. |
| **RC-D** | Response handler not bound to the RequestPort. | Code review: handler registration missing. |
| **RC-E** | Event streaming broker dropped events. | Broker metrics show drop. |
| **RC-F** | Clock skew / ordering issues. | Timestamps out of order. |
| **RC-G** | Retention policy evicts checkpoints before reviewer responds (SLA > retention). | Policy SLA mismatch. |

### §12.3 Diagnostic Steps

1. Evidence floor; capture the checkpoint store state before any repair.
2. KQL-07 — identify orphan rate and affected request IDs.
3. `Get-Agt212AgfCheckpoint -AgentId <id> -IncludeOrphans` — detailed checkpoint diagnostics.
4. For each orphan: determine whether the user-facing interaction completed, errored, or hung.
5. Code review of the `request_info()` code path and response handler bindings.
6. Verify checkpoint retention policy vs SLA: retention must be > SLA + safety margin.

### §12.4 Resolution Steps

| Root cause | Resolution |
|---|---|
| RC-A | Fix code path to always write checkpoint before returning from `request_info()`. Add test. |
| RC-B | Reconfigure backend durability; increase persistence guarantees; monitor. |
| RC-C | Preserve workflow identity / scope in checkpoint metadata; restore with scope validation. |
| RC-D | Bind response handler; add registration test. |
| RC-E | Switch to a durable broker / enable at-least-once delivery. |
| RC-F | NTP sync; authoritative timestamp from service. |
| RC-G | Increase checkpoint retention beyond SLA; surface misconfiguration alert. |

### §12.5 Prevention

1. **Checkpoint-invariant test.** Every `request_info()` call is preceded by a verified checkpoint write; test-covered.
2. **Orphan alarm.** KQL-07 orphan rate > 0 pages AI Administrator within 15 min.
3. **Retention > SLA.** Firm invariant.
4. **Request ID uniqueness.** Enforced via UUIDv4; collision test.

### §12.6 Evidence to Capture

- **E-AGF-01** — Checkpoint store state at fault time.
- **E-AGF-02** — List of orphan request IDs.
- **E-AGF-03** — Reconstruction of affected interactions.
- **E-AGF-04** — Code diff for RC-A / RC-D.

### §12.7 Cross-References

- §3 HITL-NOT-FIRING — related downstream symptom.
- §11 EVIDENCE-GAP — orphan responses generate evidence gaps.
- [Microsoft Agent Framework HITL documentation (March 2026)](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md).

---

## §13 Pillar: R3120-TEST-FAIL

FINRA Rule 3120 requires annual testing and verification of supervisory controls. When the annual test reveals a design or operating deficiency in the Control 2.12 supervisory controls, this pillar covers the response: characterizing the finding, executing remediation, documenting exceptions, and preparing examiner-grade attestation. A failed 3120 test is not merely a compliance artifact — it is an exception record under FINRA 4511 and must be preserved for 6 years under SEC 17a-4(b)(4).

### §13.1 Symptom Catalog

| Code | Symptom | Severity hint |
|---|---|---|
| **P14-S1** | WSP Adherence test: sampled approvals deviate from WSP procedures | Sev2 |
| **P14-S2** | HITL Functionality test: trigger phrase does not produce review queue item | Sev1 |
| **P14-S3** | Escalation Procedures test: escalation not routed correctly | Sev1 |
| **P14-S4** | Review Queue Performance test: < 95% reviews within SLA | Sev2 |
| **P14-S5** | Sampling Protocol test: actual sampling rate deviates materially from target | Sev2 |
| **P14-S6** | Supervisor Qualifications test: a principal's registration lapsed; not caught in-period | Sev1 |
| **P14-S7** | Design Effectiveness: WSP does not address a known AI agent supervision risk | Sev2 |
| **P14-S8** | Test was not performed within the annual window | Sev1 |

### §13.2 Root Cause Matrix

| Code | Root cause | Confirmation signal |
|---|---|---|
| **RC-A** | Design deficiency: WSP lacks coverage. | Gap in WSP vs tested scenarios. |
| **RC-B** | Operating deficiency: control designed correctly, operated incorrectly. | Test showing config drift, missed steps. |
| **RC-C** | Sampling methodology flawed. | Sampling produced non-representative set. |
| **RC-D** | Testing not independent. | Tester also operated the control during the period. |
| **RC-E** | Test evidence incomplete. | Working papers missing signatures, dates, exception resolution. |

### §13.3 Diagnostic Steps

1. Review 3120 working papers for completeness.
2. For each failed test area, trace finding to control (pillars §3–§12) and apply that pillar's diagnostics.
3. Validate sampling methodology against firm SOP.
4. Confirm tester independence.
5. Identify the exception window: when did the deficiency begin, end, and what was the customer-facing blast radius?

### §13.4 Resolution Steps

| Root cause | Resolution |
|---|---|
| RC-A | Amend WSP to cover the gap; CAB + Designated Principal co-sign; reconcile all agents against the new WSP. |
| RC-B | Remediate the underlying pillar; document exception window. |
| RC-C | Revise sampling methodology; re-execute tests with corrected methodology. |
| RC-D | Re-execute test with independent tester. |
| RC-E | Complete working papers; re-sign; preserve. |

### §13.5 Prevention

1. **Continuous-testing posture.** Run 3120 test sub-procedures monthly rather than only annually; surface findings earlier.
2. **Tester-independence rotation.** Tester pool separated from operator pool.
3. **Working-papers template.** Standardized to force complete documentation.
4. **Remediation SLA.** Findings have remediation due dates; tracked to closure.

### §13.6 Evidence to Capture

- **E-3120-01** — 3120 working papers at test close.
- **E-3120-02** — Exception register.
- **E-3120-03** — Remediation plan with due dates and owners.
- **E-3120-04** — Re-test results.
- **E-3120-05** — Principal sign-off on final attestation.

### §13.7 Cross-References

- [Control 2.12 — Rule 3120 Annual Testing Requirements](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md).
- All §3–§12 pillars as potential root-cause sources.

---

## §14 Runbook RB-01: Examiner Finds Missing HITL Review for Named Customer Interaction

**Trigger:** FINRA / SEC / OCC / Fed / NYDFS examiner (or internal audit acting as examiner proxy) submits a written inquiry naming a customer interaction (conversation ID, date, or customer name) and requesting the corresponding HITL supervisory-review record. Initial query of `Get-Agt212Evidence -ConversationId <id>` returns no record, incomplete record, or a record attributable to an unqualified reviewer.

**Severity:** Sev1. Examiner-active posture. Legal notification within 60 minutes.

**Lead roles:** Incident commander = AI Governance Lead. Accountable authority = Designated Principal + Compliance Officer + Legal.

**Time pressure:** Examiners typically grant 10 business days for written production. Within the first 24 hours, the firm must complete reconstruction or formally characterize the gap.

### RB-01 Steps

| # | Step | Owner | Evidence |
|---|---|---|---|
| 1 | **Freeze state.** Do not modify any agent, flow, policy, or retention label until evidence is preserved. | IR on-call | Change-freeze notice |
| 2 | Capture full evidence bundle §21 (E-01..E-14) with `Invoke-Agt212EvidenceSnapshot -IncidentId <id> -Stage Initial -Destination AgentGov-Evidence-212`. | AI Administrator | Snapshot manifest |
| 3 | Notify Legal. Legal owns all outbound communication to the examiner from this point forward. | AI Governance Lead | Legal intake ticket |
| 4 | Retrieve the named interaction: `Get-Agt212Interaction -ConversationId <id> -IncludeAll`. Confirm agent ID, user UPN, timestamp, WSP-mapped trigger criteria, actual routing outcome. | AI Administrator | Interaction record |
| 5 | Determine the expected supervisory path: cross-reference interaction content against WSP addendum. Was HITL required? What reviewer / group? What decision fields? | Compliance Officer | WSP mapping memo |
| 6 | Reconstruct available evidence: Purview audit log, Copilot Studio transcript, Power Automate run history, Agent Framework checkpoint store. Build the fullest possible supervisory record. | AI Administrator | Reconstructed record |
| 7 | If reconstructed record is complete and attributable to a qualified reviewer, produce to Legal for examiner response. Inform Legal of any reconstruction artifacts (vs original-system records). | Designated Principal | Production package |
| 8 | If record is incomplete or absent, characterize the gap precisely: what was missing, why, and for what window. | Compliance Officer + Designated Principal | Gap memo |
| 9 | Identify blast radius: are other interactions in the same window similarly gapped? Run `Get-Agt212Interaction -From <window> -To <window> -Where 'ShouldHaveRouted=true AND ActuallyRouted=false'`. | AI Governance Lead | Blast-radius report |
| 10 | Apply the relevant pillar's resolution (typically §3 HITL-NOT-FIRING or §11 EVIDENCE-GAP). Remediation restores the tooling; it does **not** retroactively create a supervisory record. | AI Administrator under Compliance direction | Pillar resolution evidence |
| 11 | Prepare examiner response. Legal reviews and signs before transmission. The response must be accurate and hedged; it must not claim that remediation has cured a past supervisory gap. | Legal + Designated Principal + Compliance Officer | Examiner response (via Legal) |
| 12 | Open Control 3.4 incident with this incident ID; perform root cause analysis to closure. | AI Governance Lead | RCA record |
| 13 | Add to 3120 exception register for next annual test. | Compliance Officer | Exception register entry |
| 14 | Post-incident: test-and-fix pipeline hardening (§3.5 or §11.5 preventions). | AI Administrator + AI Governance Lead | Prevention artifacts |

### RB-01 Artifacts to Preserve

- Examiner inquiry letter (inbound).
- All evidence snapshots (initial and recovery-close).
- Gap memo and blast-radius report.
- Legal-reviewed examiner response.
- RCA record.
- 3120 exception register entry.

### RB-01 Hedging Note

Language in the examiner response matters. Use "the firm has reconstructed the following artifacts from available source systems" rather than "the supervisory record is." Use "the firm has identified a gap of duration [x]" rather than "the firm failed to supervise." Factual accuracy is paramount; adjectives are Legal's call.

---

## §15 Runbook RB-02: Designated Principal's Series 24 Lapses Mid-Quarter

**Trigger:** CRD / WebCRD extract, HR notification, or attestation process reveals that a currently designated principal's Series 24 (or 66 / 65 for RIA scope) is in `Lapsed` or `Inactive` status.

**Severity:** Sev1 from the moment of lapse to the moment of replacement. All decisions made by that principal after the lapse date are supervisory gaps.

**Lead roles:** Incident commander = Compliance Officer. Accountable authority = Compliance Officer + CCO.

### RB-02 Steps

| # | Step | Owner | Evidence |
|---|---|---|---|
| 1 | Confirm the lapse: pull fresh WebCRD extract; identify lapse date with precision (ISO 8601 UTC). | Compliance Officer | CRD extract |
| 2 | **Immediately** remove the principal from every reviewer Entra group: `Start-Agt212PrincipalOffboard -UPN <upn> -Reason "CRD-lapse" -EffectiveAt <lapseDate>`. This blocks further decisions. | AI Administrator | Offboard log |
| 3 | Reassign pending queue items to a qualified backup principal: `Invoke-Agt212QueueReassign -FromUPN <upn> -ToGroup <backupGroupId>`. | AI Administrator | Reassignment log |
| 4 | Enumerate decisions made by the principal since the lapse date: KQL-03 filtered to the lapsed UPN and time window. | AI Governance Lead | Decision list |
| 5 | For each decision in the window: determine whether the decision approved a customer-facing action. Sev1 if any. | Compliance Officer | Disposition memo per decision |
| 6 | For retail communications approved during the lapse window: engage Legal for disposition under Rule 2210. | Legal | Legal memo |
| 7 | Arrange CRD reinstatement path with the principal (CE completion, attestation). Do not permit re-addition to the reviewer group until reinstatement is confirmed in CRD. | Compliance Officer + HR | Reinstatement record |
| 8 | Update WSP roster: lapse event logged; backup principal named; attestation refreshed. | Compliance Officer | WSP roster update |
| 9 | Update principal-lapse runbook prevention: confirm CRD-sync automation is active and timely; if lapse was not caught by sync, raise that as a sub-incident. | AI Governance Lead | Sync audit |
| 10 | Report to CCO; if customer harm identified, engage Legal for customer-communication decision. | CCO + Legal | CCO memo |
| 11 | Add to 3120 exception register. | Compliance Officer | Exception register entry |

### RB-02 Prevention (Post-Incident)

- Daily CRD sync — confirm operational.
- Attestation cadence tightened: 90 day max staleness.
- Dual-principal attestation for Z3: every decision requires attestation by a secondary principal within 48 hours, so single-principal lapse does not create a silent gap.
- HR termination / status-change feed connected directly to Entra Lifecycle Workflow for principals.

---

## §16 Runbook RB-03: HITL Bypassed Due to Configuration Error (Post-Incident)

**Trigger:** Post-hoc discovery (via KQL-04, user report, or audit) that a Zone 3 agent processed customer interactions during a window with HITL misconfigured — the firm's WSP required HITL but deployed configuration did not enforce it. Fault window is bounded.

**Severity:** Sev1.

**Lead roles:** Incident commander = AI Governance Lead. Accountable = Designated Principal + Compliance Officer.

### RB-03 Steps

| # | Step | Owner | Evidence |
|---|---|---|---|
| 1 | Freeze state. Pause the affected agent (disable publish, or disable the channel routing customer traffic) while evidence is captured. | AI Administrator under AI Governance Lead direction | Pause artifact |
| 2 | Capture full §21 evidence bundle at the fault-state configuration. This preserves what the misconfigured state looked like. | AI Administrator | Snapshot manifest |
| 3 | Characterize the fault window: earliest and latest interactions affected, number of affected customers, business activity category. Use `Get-Agt212Interaction` over the window. | AI Governance Lead | Window memo |
| 4 | Identify the config-error mechanism: apply §3 HITL-NOT-FIRING diagnostic matrix to determine which RC (A-H) applies. | AI Administrator | Pillar diagnostic |
| 5 | Produce the supervisory-gap set: every interaction in the window that should have routed to HITL but did not. | AI Governance Lead | Gap set |
| 6 | Engage Legal. Customer-impact assessment begins. | Legal | Legal intake |
| 7 | Perform retroactive principal review of the gap set — a qualified principal reviews each interaction to identify (a) outputs that would have been rejected or modified, (b) outputs that were acceptable on their merits, (c) outputs requiring customer remediation (e.g., correction, rescission). | Designated Principal | Retroactive review log |
| 8 | Remediate the config per §3.4. Do not re-enable customer traffic until HITL is verified. | AI Administrator | Remediation log |
| 9 | Verify remediation per §3.5. Synthetic tests across the WSP trigger vocabulary. | AI Administrator + Compliance Officer | Test transcript |
| 10 | Customer remediation (if any) executed per Legal direction. | Legal + Compliance Officer | Customer-notice records |
| 11 | Regulatory notification (if required by firm SOP or by the nature of the harm): Legal decision. | Legal | Notification record |
| 12 | Open Control 3.4 incident; complete RCA. | AI Governance Lead | RCA record |
| 13 | 3120 exception register entry. | Compliance Officer | Exception entry |
| 14 | Long-term prevention: WSP reconciliation gate in CI/CD (§3.5.1), HITL unit test (§3.5.2), 30-day trigger-rate monitoring (§3.5.3). | AI Administrator + AI Governance Lead | Prevention artifacts |

### RB-03 Hedging Note

**Remediating the configuration does not cure the supervisory gap.** The gap set is a historical fact; the firm's disposition of it (retroactive review, customer remediation, regulatory notification) is how it responds to the gap. Do not describe remediation as "restoring compliance" for the gap period.

---

## §17 Runbook RB-04: Retail Communication Sent Without Pre-Use Approval (Post-Incident)

**Trigger:** Post-hoc discovery that an AI agent delivered a retail communication (Rule 2210 definition: to > 25 retail investors within any 30 calendar-day period, and not subject to an enumerated Rule 2210(b)(1) exclusion) without the required principal pre-use approval. Trigger may come from KQL-06, audience-monitoring alert, or customer complaint.

**Severity:** Sev1.

**Lead roles:** Incident commander = Compliance Officer. Accountable = Designated Principal + CCO + Legal.

### RB-04 Steps

| # | Step | Owner | Evidence |
|---|---|---|---|
| 1 | Freeze: pause the template / agent distribution channel. | AI Administrator | Pause record |
| 2 | Capture §21 evidence bundle. | AI Administrator | Snapshot |
| 3 | Reconstruct distribution: how many retail investors received the communication, over what window, via what channels? | Marketing Ops + AI Governance Lead | Distribution reconstruction |
| 4 | Confirm classification misapplication: follow §8 diagnostic matrix (RC-A..G). | Compliance Officer | Pillar diagnostic |
| 5 | Engage Legal. Legal owns FINRA notification decisions and customer-communication decisions. | Legal | Legal intake |
| 6 | Conduct retroactive principal review of the communication content: was the content itself compliant, notwithstanding the missed pre-use approval step? | Designated Principal | Retroactive approval memo |
| 7 | If content itself was non-compliant: immediate customer remediation (correction, rescission, re-communication with accurate content) per Legal direction. | Legal + Compliance Officer | Remediation record |
| 8 | If content was compliant but approval step missed: document as a 2210 procedural exception for 3120 register; consult Legal on notification. | Compliance Officer + Legal | Exception record |
| 9 | Remediate classification per §8.4. Wire pre-use approval into template publish path. | AI Administrator | Remediation log |
| 10 | Regulatory notification (firm SOP + Rule 4530 considerations): Legal decision. | Legal | Notification record |
| 11 | Open 3.4 incident; RCA. | AI Governance Lead | RCA record |
| 12 | Update WSP to strengthen classification and counting controls (§8.5). | Compliance Officer | WSP update |
| 13 | 3120 register entry. | Compliance Officer | Exception register |

### RB-04 Distinction: Procedural vs Substantive

A missed pre-use approval is a procedural exception if the content was nonetheless compliant; it is a substantive exception if the content was not compliant. Both are reportable exceptions under 3120, but customer-remediation and regulatory-notification obligations differ. Do not conflate.

---

## §18 Runbook RB-05: SOX Management-Cert Deadline, Supervision Evidence Incomplete

**Trigger:** SOX § 302 or § 404 management certification deadline approaches (typically quarterly 10-Q and annual 10-K). Control self-assessment identifies that Control 2.12 supervision evidence is incomplete for the certification period.

**Severity:** Sev2 initially (calendar deadline drives to Sev1 as deadline approaches).

**Lead roles:** Incident commander = AI Governance Lead. Accountable = CCO + CFO.

### RB-05 Steps

| # | Step | Owner | Evidence |
|---|---|---|---|
| 1 | Identify deadline and lead time. Typical management cert preparation window is 30-45 days before filing. | AI Governance Lead + SOX PMO | Timeline memo |
| 2 | Inventory expected evidence vs actual evidence: for each Control 2.12 verification criterion, was evidence produced at target cadence? | AI Governance Lead | Gap matrix |
| 3 | For each gap, characterize: reconstructible vs non-reconstructible. | AI Governance Lead + Compliance Officer | Gap memo |
| 4 | Reconstruct where possible (audit log, backups, flow history). | AI Administrator | Reconstruction artifacts |
| 5 | For non-reconstructible gaps: document as a control deficiency for SOX purposes. | Internal Audit + SOX PMO | Deficiency memo |
| 6 | Evaluate materiality per SOX methodology: significant deficiency vs material weakness determination. | Internal Audit + External Audit liaison | Materiality assessment |
| 7 | If significant deficiency or material weakness: remediation plan with CFO awareness; disclosure review by Legal + External Counsel. | CFO + Legal | Disclosure memo |
| 8 | Complete management cert with disclosed deficiencies (if any). | CFO + CEO | Filed certification |
| 9 | Post-filing remediation; re-test next quarter. | Internal Audit + AI Governance Lead | Re-test plan |
| 10 | 3120 register entry. | Compliance Officer | Exception register |

### RB-05 Prevention

- Continuous-cadence evidence production (don't wait for quarter-end).
- Automated evidence-integrity probe (§11.5.2) ensures gaps surface within 24 hours.
- SOX-Control 2.12 calendar: evidence maturity check 45, 30, 15 days before each quarter-end.

---

## §19 Runbook RB-06: Surprise Audit of Zone 3 Agent — Reviewer-Decision Audit Trail Has Gaps

**Trigger:** Unannounced internal audit, FINRA cycle exam, or acquirer-driven due diligence requests full reviewer-decision audit trail for one or more Z3 agents. Sampling reveals gaps.

**Severity:** Sev1 (examiner-active posture by default for any external audit trigger).

**Lead roles:** Incident commander = AI Governance Lead. Accountable = Designated Principal + Compliance Officer + Legal.

### RB-06 Steps

| # | Step | Owner | Evidence |
|---|---|---|---|
| 1 | Freeze state. | AI Administrator | Change-freeze notice |
| 2 | Capture §21 evidence bundle. | AI Administrator | Snapshot |
| 3 | Determine the auditor's scope: which agents, which time window, which decision fields? | AI Governance Lead | Scope memo |
| 4 | For the requested scope, produce the evidence bundle: `Get-Agt212Evidence -Scope <scope> -ExportPath .\audit.csv`. | AI Administrator | Evidence export |
| 5 | Apply §11 EVIDENCE-GAP diagnostic matrix to characterize each gap. | Compliance Officer | Gap matrix |
| 6 | Engage Legal early if external examiner. | Legal | Legal intake |
| 7 | For each gap, reconstruct from secondary sources (Purview audit, flow history, mailbox trace). | AI Administrator | Reconstruction |
| 8 | Produce audit response: (a) complete records where reconstructed, (b) characterized gaps where not. | Designated Principal + Legal | Audit response package |
| 9 | Pillar remediation per §11. | AI Administrator | Remediation log |
| 10 | 3.4 incident; RCA; 3120 register entry. | AI Governance Lead + Compliance Officer | RCA + exception |

### RB-06 Prevention

- Quarterly mock drill (§11.5.4) trains the firm to produce evidence on demand.
- Evidence-schema invariant testing (§11.5.1).

---

## §20 Runbook RB-07: Sponsor Terminates; Z3 Agents Pending Reassignment (Cascade with Control 3.6)

**Trigger:** Sponsor (Entra Agent ID sponsor role) termination event for a sponsor covering multiple Z3 agents. This is a cascade event intersecting Control 2.12 (supervision), Control 2.26 (sponsorship), and Control 3.6 (orphaned-agent detection and remediation).

**Severity:** Sev1 if multiple Z3 agents; Sev2 if single Z3.

**Lead roles:** Incident commander = AI Governance Lead. Accountable = Compliance Officer + Designated Principal. Cross-control coordination with Control 3.6 on-call.

### RB-07 Steps

| # | Step | Owner | Evidence |
|---|---|---|---|
| 1 | HR termination feed triggers Entra Lifecycle Workflow. Confirm workflow executed; capture workflow log. | HR + AI Administrator | Workflow log |
| 2 | Enumerate agents with terminated UPN as sponsor: `Get-Agt212SponsorState -SponsorUPN <upn>`. | AI Administrator | Affected-agent list |
| 3 | Capture §21 evidence bundle for affected agents. | AI Administrator | Snapshot |
| 4 | Invoke Control 3.6 orphan-detection procedure on the affected agents — this is the authoritative orphan-response path. See [Control 3.6 — Orphaned Agent Detection and Remediation](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md). | AI Governance Lead | 3.6 procedure output |
| 5 | For each Z3 orphaned agent, apply Control 2.12 interim supervisory posture: until sponsor reassigned, increase principal oversight to 100% review pending assignment. | Designated Principal | Interim oversight log |
| 6 | Assign replacement sponsors (primary + backup) per WSP; document attestation. | Compliance Officer + affected business-line lead | Sponsor attestation |
| 7 | Verify `Get-Agt212SponsorState` shows valid sponsor for every Z3 agent. | AI Administrator | Verification log |
| 8 | Calculate gap duration per agent (from termination to sponsor reassignment). Gap > firm SLA → exception. | AI Governance Lead | Gap duration log |
| 9 | 3.4 incident for any gap > SLA; RCA. | AI Governance Lead | RCA |
| 10 | 3120 register. | Compliance Officer | Exception entry |
| 11 | Prevention: HR-feed-to-Lifecycle-Workflow latency tightened; backup-sponsor-required invariant enforced pre-publish. | AI Governance Lead + HR + AI Administrator | Prevention artifacts |

### RB-07 Cross-Control Coordination

This runbook intentionally **does not** duplicate the Control 3.6 orphaned-agent remediation procedure — Control 3.6 is the authoritative procedure for that step. The Control 2.12 role in this cascade is to ensure that while Control 3.6 remediates the orphan-state (lifecycle), Control 2.12 maintains the supervisory layer (business-activity oversight) through the gap. The interim 100% review posture in Step 5 is the Control 2.12 compensating control for the gap.

---

## §21 Escalation Matrix

Escalation is a governance act, not a technical one. The matrix below names the path for each incident class. Firms should verify against their own escalation SOP.

### §21.1 Microsoft Support Tiers

| Domain | Support Channel | When to Engage | Severity Mapping |
|---|---|---|---|
| Copilot Studio agent behavior, trigger routing, publish failures | Copilot Studio support (via M365 Admin Center → Support) | §3, §4, §8, §12 pillars where root cause is product behavior vs config | Sev1 → Severity A; Sev2 → Severity B |
| Power Automate flow execution, connector failures, premium-connector faults | Power Platform support | §4 QUEUE-STUCK root causes involving flow internals | Sev1 → Severity A |
| Agent Framework (Azure AI Foundry Agents) runtime, thread API failures, checkpoint store | Azure support (Agent Framework SKU, SLA per subscription tier) | §12 AGF-CHECKPOINT-LOSS escalations beyond local recovery | Follow Azure severity classifications |
| Entra ID agent-identity issues, Lifecycle Workflows | Entra support | §10 SPONSOR-ATTESTATION-FAIL escalations; identity / lifecycle product issues | Severity per Entra support matrix |
| Purview eDiscovery, retention label propagation, audit search gaps | Purview support (compliance tier) | §11 EVIDENCE-GAP where audit events are missing at source | Severity per M365 support matrix |
| Teams (if supervisory approvals use Adaptive Cards in Teams) | Teams support | §4 QUEUE-STUCK where approvals fail at Teams channel | Severity per M365 support matrix |

**Engagement expectations:**

- Open a Severity A case only when operational impact warrants; escalation of severity via Microsoft's premium support (Unified / Premier) is the normal route for examiner-active incidents.
- Attach the §21 evidence bundle to every support case where possible.
- Log case IDs in the incident record and in the 3120 exception register entry.

### §21.2 Internal Compliance and Business Escalation

| Trigger | First-Line | Second-Line | Third-Line |
|---|---|---|---|
| Sev3 config drift, single-user impact | AI Administrator | AI Governance Lead | — |
| Sev2 supervisory control degradation | AI Governance Lead | Compliance Officer | CCO on request |
| Sev1 potential supervisory gap, no examiner | Compliance Officer | CCO | General Counsel |
| Sev1 examiner-active | Compliance Officer + AI Governance Lead | CCO + General Counsel | CEO / Board (per firm SOP) |
| Retail comm 2210 incident | Compliance Officer | CCO + General Counsel | CEO / Board (per firm SOP) |
| Principal CRD lapse with customer-facing decisions | Compliance Officer | CCO + General Counsel | CEO / Board (per firm SOP) |
| Sponsor mass-termination cascade | AI Governance Lead | Compliance Officer + HR | CCO |

### §21.3 Legal Notification

| Scenario | Legal Notification SLA |
|---|---|
| Examiner inquiry (any) | Within 60 minutes of inquiry receipt |
| Post-incident finding of supervisory gap (Sev1) | Within 4 hours of Sev1 declaration |
| Post-incident finding of 2210 violation (substantive) | Within 2 hours of substantive classification |
| Customer-impact assessment required | Immediately upon gap characterization |
| Regulatory notification contemplated | Legal owns the notification decision |

### §21.4 Regulatory Notification — Firm SOP Dependent

The following timelines reflect commonly referenced regulatory expectations. **They are not a substitute for firm Legal analysis and firm regulatory-reporting SOP.** Firms should consult rule text and counsel for each case.

| Regulator | Notification Rule (Illustrative) | Typical Cadence |
|---|---|---|
| FINRA | Rule 4530 for specified events (customer-complaint thresholds, regulatory action, certain internal findings) | Within 30 calendar days of triggering event (Rule 4530) |
| SEC | Form 8-K for material events (issuers); Rule 204-2 for RIAs (books-and-records) | 8-K: 4 business days; 204-2: continuing recordkeeping |
| OCC / Fed | Suspicious Activity Reports for specified events; supervisory communications per exam cycle | SAR: 30 days; supervisory: per exam cycle |
| CFTC / NFA | Rule 2-9 (supervision), 3-10 (recordkeeping), applicable CFTC reporting rules | Per rule |
| NYDFS | 23 NYCRR 500 § 500.17 cybersecurity-event notification | 72 hours for qualifying events |
| State regulators | Varies | Per rule |

### §21.5 Severity-to-Escalation Flow

```
Sev3  → AI Administrator resolves; AI Governance Lead informed next business day.
Sev2  → AI Governance Lead directs; Compliance Officer informed within 8 hours.
Sev1  → Compliance Officer on bridge; Legal notified per §21.3; CCO informed immediately.
Sev1 (examiner) → Legal leads external comms; CCO + General Counsel on bridge; IR + RCA activate.
```

---

## §22 Evidence Collection During Incident

Every incident produces evidence. Evidence collection is itself a Control 2.12 deliverable — the firm's ability to reconstruct the incident and demonstrate response discipline is a supervisory artifact.

### §22.1 The E-Bundle

| Code | Artifact | Source | Collector | Retention Target | Regulatory Anchor |
|---|---|---|---|---|---|
| E-01 | Incident declaration record (who, when, severity, trigger) | IR platform | IR on-call | 6 years, WORM | FINRA 4511, SEA 17a-4(f) |
| E-02 | Change-freeze notice and timestamp | Service ops | AI Administrator | 6 years, WORM | SOX § 404 |
| E-03 | Agent-state snapshot (Copilot Studio / Agent Framework configuration export) | Product export API | AI Administrator | 6 years, WORM | FINRA 3110, 17a-4(f) |
| E-04 | Flow / plugin snapshot (Power Automate solution export, connector config) | Power Platform | AI Administrator | 6 years, WORM | FINRA 3110 |
| E-05 | Purview audit log extract for incident window | Purview | AI Administrator | 10 years (firm-adjustable to retention policy), WORM | SEA 17a-4 |
| E-06 | Interaction transcripts for affected window | Copilot Studio transcripts + AGF thread export | AI Administrator | 6 years, WORM | FINRA 3110, 17a-4(f) |
| E-07 | Supervisory-decision records (pre- and post-incident) | `AgentSupervisionLog` SharePoint list + Dataverse `agt_supervisionlog` | AI Administrator | 6 years, WORM | FINRA 3110(a), 3110(b)(4) |
| E-08 | Reviewer-roster snapshot (Entra group membership) at fault window | Entra | AI Administrator | 6 years, WORM | FINRA 3110(e) |
| E-09 | CRD / attestation snapshot for reviewers in scope | HR / CRD feed | Compliance Officer | 6 years, WORM | FINRA 1210, 3110(e) |
| E-10 | Sponsor-state snapshot | Entra agent-identity store | AI Administrator | 6 years, WORM | Internal (2.26) + FINRA 3110 |
| E-11 | WSP version and diff at incident time | Compliance document store | Compliance Officer | 6 years, WORM | FINRA 3110(b) |
| E-12 | RCA record | Incident platform | AI Governance Lead | 6 years, WORM | SOX § 404, FINRA 3120 |
| E-13 | Customer-impact memo and disposition (if any) | Legal / Compliance | Legal | Retain per Legal hold | Rule 4530, state consumer-protection |
| E-14 | Regulatory-notification records (if any) | Legal | Legal | Retain per Legal hold | Rule-specific |

### §22.2 Snapshot Invocation

```powershell
# Initial snapshot at incident declaration:
Invoke-Agt212EvidenceSnapshot `
    -IncidentId <id> `
    -Stage Initial `
    -Destination AgentGov-Evidence-212 `
    -RetentionLabel "AgentGov-Evidence-212-6yr-WORM"

# Mid-incident snapshot at each state change:
Invoke-Agt212EvidenceSnapshot -IncidentId <id> -Stage Mid -Note "<what changed>"

# Recovery-close snapshot:
Invoke-Agt212EvidenceSnapshot -IncidentId <id> -Stage RecoveryClose

# Post-RCA snapshot (for long-tail cases):
Invoke-Agt212EvidenceSnapshot -IncidentId <id> -Stage PostRCA
```

Each invocation produces a manifest (JSON) listing every artifact, SHA-256 hash, source system, and retention label. The manifest is itself E-01 attachment.

### §22.3 Retention and WORM Discipline

Evidence destined for 17a-4(f) style recordkeeping is written to storage configured for Write-Once-Read-Many (WORM) immutability. For the Microsoft 365 stack, this is typically Purview retention labels with "Records" disposition and the label marked as regulatory (legal hold override). Firms should verify that:

1. The retention label `AgentGov-Evidence-212` is configured as **Record** with mutability **Regulatory** (immutable).
2. Storage targets (SharePoint library, Exchange mailbox, Dataverse table) honor the label.
3. Retention policy is **6 years** at minimum (FINRA 4511) or firm-required longer horizon.
4. Disposition review is governed by Compliance; no deletion occurs silently.

### §22.4 Chain of Custody

| Step | Control |
|---|---|
| Collector identity on every artifact | UPN and device ID in manifest |
| Timestamp | ISO 8601 UTC from the source system, not the collector's workstation |
| Hash | SHA-256 computed at collection, re-verified at archive |
| Access log | Audit every read of the evidence bundle; investigator UPN and purpose logged |
| Legal hold | Legal applies hold labels to incident artifacts upon Sev1 declaration |

### §22.5 Evidence Gaps Are Themselves Evidence

If an artifact cannot be collected (e.g., retention policy was not applied in time and the audit log aged out), document the gap explicitly in E-12 RCA with:

- What was expected.
- What is actually available.
- Why the expected artifact is not available.
- What secondary reconstruction is possible (and what its limitations are).

Do not omit. Do not describe reconstructed artifacts as if they were primary. Examiners read RCAs; candor is a supervisory asset.

---

## §23 Cross-References

### §23.1 Sibling Playbooks for Control 2.12

- [Portal Walkthrough](portal-walkthrough.md) — step-by-step portal configuration for HITL routing, reviewer groups, audit retention.
- [PowerShell Setup](powershell-setup.md) — automation scripts (`Export-SupervisionLog.ps1`, SharePoint list `AgentSupervisionLog`, roster sync).
- [Verification and Testing](verification-testing.md) — test cases TC-2.12-01..05 and Rule 3120 annual test plan.

### §23.2 Related Controls

| Control | Why Linked |
|---|---|
| [1.2 — Agent Registry and Integrated Apps Management](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md) | Agent identity is the entity being supervised; reviewer-roster mapping depends on identity |
| [1.7 — Comprehensive Audit Logging and Compliance](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) | Tenant-level audit policy is precondition for 2.12 evidence; source of E-05 |
| [2.13 — Documentation and Record-Keeping](../../../controls/pillar-2-management/2.13-documentation-and-record-keeping.md) | WSP and supervisory documentation discipline |
| [2.25 — Agent 365 Admin Center Governance Console](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md) | Cross-tenant agent visibility supports supervisory inventory |
| [2.26 — Entra Agent ID Identity Governance](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md) | Sponsor attestation cascades into §10 |
| [3.1 — Agent Inventory and Metadata Management](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md) | Inventory feeds the supervisory scope |
| [3.4 — Incident Reporting and Root Cause Analysis](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) | All Sev1/Sev2 runbooks open a 3.4 incident |
| [3.6 — Orphaned Agent Detection and Remediation](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) | RB-07 cascades with 3.6 |

### §23.3 Framework Documents

- [Agent Identity Architecture](../../../framework/agent-identity-architecture.md)
- [Zones and Tiers](../../../framework/zones-and-tiers.md)
- [Agent Lifecycle](../../../framework/agent-lifecycle.md)
- [Operating Model](../../../framework/operating-model.md)

### §23.4 Reference

- [Role Catalog](../../../reference/role-catalog.md) — canonical short names used throughout this playbook.
- [Regulatory Mappings](../../../reference/regulatory-mappings.md) — FINRA 3110, 3120, 2210; SEA 17a-4; SOX § 302/404; Reg SCI.
- [PowerShell Baseline](../../_shared/powershell-baseline.md) — helper module conventions.
- [Solutions Index](../../../reference/solutions-index.md) — deployable artifacts in the `FSI-AgentGov-Solutions` repo.

### §23.5 External References

- FINRA Rule 3110 — Supervision
- FINRA Rule 3120 — Supervisory Control System
- FINRA Rule 2210 — Communications with the Public
- FINRA Rule 4511 — Books and Records
- FINRA Rule 1210 — Registration Requirements
- SEC Rule 17a-3 / 17a-4 under the Exchange Act — Books and records
- Sarbanes-Oxley Act § 302 and § 404
- OCC Bulletin 2021-40 — Model Risk Management Guidance (as applicable)
- Federal Reserve SR 26-2 (formerly SR 11-7) — Guidance on Model Risk Management
- NYDFS 23 NYCRR 500 — Cybersecurity Requirements
- CFTC Rule 23.602 — Supervision; NFA Compliance Rule 2-9

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*

