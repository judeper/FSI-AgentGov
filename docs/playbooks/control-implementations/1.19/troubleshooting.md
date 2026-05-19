# Control 1.19 — eDiscovery for Agent Interactions: Troubleshooting & Incident Response

> **Scope.** This playbook covers operational failures, evidence-preservation incidents, and litigation-hold breakdowns specific to eDiscovery (Premium) for Microsoft 365 Copilot, Microsoft Copilot Studio agent transcripts, and declared agent interactions. It assumes the unified eDiscovery experience at `https://purview.microsoft.com` (classic eDiscovery was retired August 31, 2025 in commercial clouds; only the 21Vianet sovereign cloud retains the classic experience as of this revision).
>
> **Companion documents.**
> - Parent control: [`1.19 — eDiscovery for Agent Interactions`](../../../controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md)
> - Portal walkthrough: [`portal-walkthrough.md`](portal-walkthrough.md)
> - PowerShell setup: [`powershell-setup.md`](powershell-setup.md)
> - Verification & testing: [`verification-testing.md`](verification-testing.md)
>
> **Important hedging.** Nothing in this playbook constitutes legal advice. Spoliation determinations, FRCP 37(e) sanctions exposure, and FINRA Rule 8210 sufficiency are decisions for outside counsel and the firm's Legal & Compliance function. The technical procedures here are designed to **support compliance with** evidentiary preservation duties; they do not **guarantee** admissibility, completeness, or freedom from sanction. Organizations should verify every step against current Microsoft Learn documentation and their own retention/legal-hold policies before relying on it during a live matter.

---

## Section 1 — FSI Incident Handling

eDiscovery incidents in an FSI tenant are not ordinary IT tickets. A failure to preserve, search, or produce a Copilot interaction during a regulatory examination can convert a routine technical defect into a **spoliation event** with FRCP 37(e), FINRA Rule 8210, SEC Rule 17a-4, NYDFS Part 500, and Sarbanes-Oxley §802 implications. This section establishes the severity matrix, reportability decision tree, evidence floor, compensating controls, pre-escalation checklist, communication tree, and one fully worked SEV-1 example for an eDiscovery-on-agent-interactions incident.

### 1.1 Severity matrix

The matrix below is the **default classification** for eDiscovery-on-agents incidents. The on-call eDiscovery Manager may escalate (never de-escalate) one tier based on facts known at triage. Any classification change requires a logged justification in the incident record.

| Severity | Definition (eDiscovery-specific) | Examples | Initial response SLA | Standing escalation |
|---|---|---|---|---|
| **SEV-1** | Confirmed or strongly suspected loss, alteration, or non-preservation of agent-interaction content **that is or may be subject to a legal hold, regulatory request, or active matter**. Includes mass-spoliation events (≥10 custodians) and any miss of a court-ordered or regulator-imposed production deadline. | Custodian mailbox deleted while under hold; SubstrateHolds purge confirmed for matter custodian; production deadline for FINRA 8210 request missed; Copilot Studio Dataverse environment deleted with active hold. | **15 minutes** to acknowledge; **1 hour** to convene war room | Auto-page L4 (Legal, CISO, Chief Compliance Officer); notify outside counsel within 4 hours |
| **SEV-2** | Significant degradation of preservation, search, or export capability for an active matter, **without confirmed data loss**, but with realistic risk of missing a deadline or returning incomplete results. | Hold creation succeeds in UI but propagation appears stalled >24 hours; eDiscovery (Premium) search returns suspiciously low result count for known-active custodian; export job repeatedly fails at >50% completion; reviewer cannot access review set due to RBAC drift. | **1 hour** to acknowledge; **4 hours** to remediate or escalate to SEV-1 | L3 (eDiscovery Manager + Purview Compliance Admin + Records Officer) |
| **SEV-3** | Localized failure affecting a single matter, custodian, or job with available workaround; no immediate deadline pressure. | Single export package hash-chain mismatch on first attempt (re-export succeeds); single custodian's Teams chat preservation lag observed within published Microsoft 12-hour SLA; Copilot activity condition card returns expected zero for a custodian who genuinely had no Copilot use. | **4 business hours** to acknowledge; **2 business days** to close | L2 (eDiscovery Operator + Purview Compliance Admin) |
| **SEV-4** | Cosmetic or informational; no impact on preservation, search completeness, or production. | Portal UI rendering glitch in case dashboard; non-blocking warning banner; documentation discrepancy. | **1 business day** to acknowledge; weekly batch | L1 (Service Desk / eDiscovery Operator) |

> **No-judgment-required automatic escalations.** The following conditions promote an incident to the indicated tier **without** discretionary review:
>
> - **Mass spoliation (≥10 custodians)** → automatic **SEV-1**, automatic **L4** page, automatic Microsoft Trust & Safety escalation.
> - **Missed FINRA Rule 8210 production deadline** → automatic **SEV-1**, automatic **L3 minimum** with L4 notification.
> - **Confirmed SubstrateHolds purge for a custodian under active hold** → automatic **SEV-1**, automatic outside-counsel notification within 4 hours.
> - **Cross-tenant guest custodian whose home-tenant mailbox cannot be preserved by this tenant's hold** → automatic **SEV-2** at minimum (scoping gap), promoted to **SEV-1** if matter is active and counsel has not been notified of the gap.
> - **Production miss for SEC subpoena, DOJ request, or court order** → automatic **SEV-1**, automatic L4, automatic outside-counsel and General Counsel notification within 1 hour.

### 1.2 Reportability decision tree (Q1–Q7)

Use this tree at triage and again at the first war-room checkpoint. Anchor concept: **FRCP 37(e) preservation duty attaches when litigation is reasonably anticipated**, not only when filed. Regulatory preservation duties (FINRA 4511, SEC 17a-4) are **continuous** and do not require a triggering event.

```
Q1. Was electronically stored information (ESI) — including a Copilot prompt,
    response, citation, or agent transcript — lost, altered, deleted,
    overwritten, or rendered inaccessible?
    └── NO  → Not a preservation incident. Classify by operational impact (SEV-3/4).
    └── YES → Q2.

Q2. Was that ESI subject to a legal hold, regulatory preservation duty
    (17a-4, 4511, GLBA 501(b) safeguards), or a reasonably anticipated
    litigation/investigation at the time of loss?
    └── NO  → Document and retain incident record for 7 years per 1.21
              audit-log retention. Notify Records Officer. Not reportable
              externally absent counsel direction.
    └── YES → Q3 (preservation incident confirmed; spoliation analysis begins).

Q3. Can the lost ESI be recovered intact from another authoritative source
    (Substrate replicas, immutable storage tier, Microsoft 14-day SubstrateHolds
    soft-delete window, Purview audit log surrogate, Dataverse long-term
    retention, backup snapshot)?
    └── YES → Document recovery, preserve forensic chain, notify counsel,
              continue at SEV-2. NOT a confirmed spoliation but IS a
              reportable preservation incident under most matter protocols.
    └── NO  → Q4 (potential confirmed spoliation).

Q4. Is the affected matter (a) an active regulatory examination, (b) a
    filed lawsuit, (c) a pending arbitration, (d) a SAR/AML investigation,
    or (e) a pending M&A or restatement matter?
    └── YES → Q5 (external reporting analysis required).
    └── NO  → SEV-1 internal only; preserve all forensic artifacts;
              counsel decision on reportability.

Q5. Does the loss meet any **per se** external-notification trigger?
    Apply ALL that fit:
    
    ── NYDFS Part 500.17(a) Cybersecurity Event ──────────────────────────
       72 hours from DETERMINATION (not from event) for any event with
       a reasonable likelihood of materially harming a material part of
       normal operations OR notice required to any other government,
       SRO, or supervisory body. Spoliation that triggers regulator
       notice = NYDFS reportable.
    
    ── SEC Form 8-K Item 1.05 (Material Cybersecurity Incident) ─────────
       4 BUSINESS DAYS from MATERIALITY DETERMINATION. Loss of
       Copilot-generated work product central to financial reporting
       MAY be material. Counsel + CFO + Disclosure Committee call.
    
    ── Reg S-P §248.30 (Customer Notification) ──────────────────────────
       30 days from determination of unauthorized access to or use of
       customer information (including Copilot interactions referencing
       customer NPI). Applies only if customer NPI was IN the lost
       interactions, not merely if a customer was the subject.
    
    ── FINRA Rule 4530 ──────────────────────────────────────────────────
       30 calendar days for specified events including findings of
       violation of securities/investment-related statutes by an
       associated person, AND quarterly statistical reporting for
       customer complaints.
    
    ── Court order / regulator subpoena production deadline miss ────────
       IMMEDIATE counsel notification; counsel will determine whether
       a Rule 26(g) certification, an FRCP 37(e) motion, or a
       direct regulator notification is required.
    
    └── ANY trigger met → Q6 (notification clock running).
    └── NONE met       → Q7 (internal-only handling, document fully).

Q6. Have the following stakeholders been notified within their respective
    SLAs? Each is a hard deadline, not a goal.
    
    [ ] General Counsel / outside counsel — within 1 hour for SEV-1
    [ ] Chief Compliance Officer — within 1 hour for SEV-1
    [ ] CISO — within 1 hour for SEV-1
    [ ] Records Officer — within 4 hours
    [ ] Disclosure Committee (if 8-K possible) — within 24 hours
    [ ] NYDFS (if covered entity) — within 72 hours of DETERMINATION
    [ ] FINRA / SEC examination staff (if active matter) — per counsel
    [ ] Microsoft Trust & Safety (if mass spoliation suspected) — within 24 hours
    
    └── ALL on track → Q7.
    └── ANY missed   → Auto-promote to L4; document the miss in the
                       incident record; counsel must affirmatively
                       decide whether a curative disclosure is required.

Q7. Has the forensic preservation package been assembled to the
    "Evidence floor" standard in §1.3 below?
    └── YES → Continue remediation per §2 runbooks; PIR within 10 BD of
              closure (§8 template).
    └── NO  → STOP. Do not proceed with remediation steps that may
              overwrite forensic state until §1.3 evidence floor is
              captured. Notify counsel before any destructive action.
```

### 1.3 Evidence floor (minimum 13 artifacts)

For any SEV-1 or SEV-2 eDiscovery-on-agents incident, the following 13 artifacts are the **minimum** preservation package. Counsel may demand more; counsel cannot demand less. Capture each artifact to immutable storage (Purview-managed key + locked retention label, or SEC 17a-4(f) WORM tier) **before** any remediation that could overwrite state. The eDiscovery export package itself is **not** WORM — it relies on the underlying immutable storage tier.

| # | Artifact | Source | Retention | Notes |
|---|---|---|---|---|
| 1 | Incident record (timeline, classification, decisions log) | ServiceNow / ITSM | 7 years (1.21 audit retention) | Include every classification change with timestamp and approver. |
| 2 | Unified Audit Log export for affected custodians, ±30 days from event | `Search-UnifiedAuditLog` or Purview Audit Search; expect **up to 24-hour ingestion lag** for some record types | 7 years (matches SEC 17a-4(b)(4) baseline) | Filter for `RecordType` in: `CopilotInteraction`, `ExchangeItem`, `ExchangeItemAggregated`, `MicrosoftTeams`, `SharePointFileOperation`, `MicrosoftPurviewDataLossPrevention`. Do **not** rely on `CopilotInteraction` for prompt/response **content** — that record contains metadata only; the body lives in the user's mailbox under `SubstrateHolds` and must be retrieved via eDiscovery (Premium) search. |
| 3 | Hold configuration export (XML/JSON) at time of incident | `Get-CaseHoldPolicy`, `Get-CaseHoldRule` | Life of matter + 7 years | Capture both the policy and the rule; the rule contains the KQL filter that scopes the hold. |
| 4 | Hold-distribution status per location | `Get-CaseHoldPolicy -Identity <name> -DistributionDetail` | Life of matter + 7 years | Status values: `Pending`, `Success`, `PartiallySuccess`, `Failed`. Pending status alone is not a defect within the first several hours; propagation can take **hours** (not minutes). |
| 5 | SubstrateHolds folder inventory for affected custodian | eDiscovery (Premium) search scoped to `Custom location` → user mailbox → `Recoverable Items\SubstrateHolds` | Life of matter + 7 years | This is the canonical Copilot-interaction preservation container. Empty when expected non-empty = SEV-1 trigger. |
| 6 | Copilot activity report for affected custodian, ±30 days | Microsoft 365 admin center → Reports → Usage → Microsoft 365 Copilot, **and** Copilot Dashboard if licensed | 7 years | Provides corroborating evidence of whether Copilot activity occurred during the period in question. |
| 7 | eDiscovery (Premium) case audit log | Purview portal → eDiscovery → case → Settings → Audit, or `Search-UnifiedAuditLog -RecordType ComplianceDLPExchange,DiscoveryAdministration` | Life of matter + 7 years | Records every search, every export, every reviewer action, every hold modification. |
| 8 | Search definition + estimate statistics | Purview portal export of search KQL, locations, conditions, and `Get-ComplianceSearch` statistics | Life of matter + 7 years | Capture the **exact** KQL string. Whitespace, quoting, and operator precedence matter for FRCP 26(g) defensibility. |
| 9 | Export package + manifest + hash | eDiscovery (Premium) export → download via Microsoft Edge with eDiscovery export tool | Life of matter + 7 years on WORM | Manifest includes per-item hash. Compare against on-disk hash after download to detect transit corruption. |
| 10 | Purview RBAC snapshot at time of incident | `Get-RoleGroup` and `Get-RoleGroupMember` for `eDiscovery Manager`, `eDiscovery Administrator`, `Reviewer`, `Compliance Administrator` | 7 years | Establishes who had what authority at the moment of the event — critical for FRCP 37(e) intent analysis. |
| 11 | Conditional Access / sign-in logs for actors involved in the event | Entra ID sign-in logs filtered to actor UPNs | 7 years (FSI baseline) | Establishes whether the destructive action was performed by a human, an automation principal, or under MFA. |
| 12 | Microsoft Service Health snapshot | Microsoft 365 admin center → Health → Service health, screenshot + JSON export | Life of matter | Establishes whether a concurrent Microsoft service incident contributed; cite advisory IDs in the incident record. |
| 13 | Chain-of-custody form, signed | Internal template, signed by Records Officer + eDiscovery Manager + Counsel | Life of matter + 7 years | Required for SEC 17a-4(f) audit-trail alternative reliance. Each transfer of the export package between custodians must be logged. |

> **Why 13 and not 12.** The chain-of-custody form (#13) is non-negotiable for FSI matters. The export package (#9) captures the data; the chain of custody captures **who handled it and when**. Without #13, the package's evidentiary weight is materially reduced and FRCP 37(e) "intent" analysis becomes harder to defend.

### 1.4 Compensating controls during incident

When eDiscovery preservation is degraded but not failed, the following compensating controls **help meet** the firm's preservation duty until the primary control is restored. None of these substitutes for a working hold; each is a stopgap.

| Compensating control | When to invoke | Limitations | Owner |
|---|---|---|---|
| **Manual journaling** of affected custodian mailboxes via Exchange transport rule to a journaling mailbox on WORM storage | Hold propagation stalled >24 hours; SubstrateHolds inaccessible | Does **not** capture Copilot interactions that never traverse SMTP (most do not); captures email only. | Exchange Online Admin |
| **Org-wide retention policy** at maximum scope, set to "Retain only" | Active matter, hold cannot be created or modified due to service incident | Over-retains; creates downstream defensible-disposition burden; does not segregate matter scope. | Purview Compliance Admin |
| **Purview Audit (Premium) extended retention** activated for affected custodians | When a matter may extend beyond default 1-year audit retention for non-E5 users | Captures metadata only, not content; does not substitute for SubstrateHolds. | Purview Compliance Admin |
| **Copilot disable for affected custodians** via license removal or sensitivity-label restriction | When preservation cannot be guaranteed and counsel directs interim suspension | Operationally disruptive; document counsel's written direction. | Entra Global Admin + License Admin |
| **Power Platform DLP tightening** to block Copilot Studio agent connectors that produce non-preservable transcripts | Copilot Studio agent transcript preservation gap discovered | May break legitimate business agents; coordinate with agent owners. | Power Platform Admin |
| **Records Officer hold-letter reissuance** to custodians, instructing manual preservation | Always, in any SEV-1/SEV-2; supports FRCP 37(e) "reasonable steps" defense | Relies on custodian compliance; not a technical control. | Records Officer |
| **Tenant-out export** of Substrate data via Microsoft Graph Data Connect to a customer-controlled WORM landing zone | Long-running matter where the firm cannot rely on Microsoft-side retention alone | Heavy engineering effort; not appropriate for short-fuse incidents. | Data Engineering + Records Officer |

### 1.5 Pre-escalation checklist

Before paging L3 or higher, the on-call eDiscovery Operator must confirm — and timestamp in the incident record — every item below. Missing items do not block escalation if SEV-1 thresholds are met, but each missing item must be called out at the war-room kick-off.

- [ ] Incident classified per §1.1 with rationale.
- [ ] Q1–Q7 reportability tree walked, results documented.
- [ ] All 13 evidence-floor artifacts captured **or** explicit reason logged for each gap.
- [ ] Microsoft Service Health checked; advisory IDs cited if any.
- [ ] Hold status confirmed via PowerShell (not portal alone) — `Get-CaseHoldPolicy -Identity <name> -DistributionDetail` and per-location result captured.
- [ ] Affected custodian list finalized and frozen; any addition triggers re-trigger of evidence capture.
- [ ] Counsel notified per §1.2 Q6 SLAs.
- [ ] Records Officer notified.
- [ ] Microsoft Support case opened with Severity A for SEV-1 (or Severity B for SEV-2); case number captured in incident record.
- [ ] Communication tree (§1.6) followed; named recipients confirmed.
- [ ] If incident involves Copilot Studio agents: agent owner identified, Dataverse environment ID captured, environment admin notified.
- [ ] If cross-tenant guest custodians involved: home-tenant contact identified; counsel advised of jurisdictional scoping gap.
- [ ] Sovereign cloud confirmed (commercial / GCC / GCC High / DoD / 21Vianet); cmdlet endpoint used noted.

### 1.6 Communication tree

Communication is **named recipients, not distribution lists**. Distribution lists fail silently. Each recipient below is a role; the on-call rota maps roles to people. Update the rota quarterly.

```
SEV-1 (within 1 hour of classification)
├── General Counsel (named) ──────────────► Outside e-discovery counsel (named)
├── Chief Compliance Officer (named) ─────► CCO deputy + relevant LOB compliance lead
├── CISO (named) ─────────────────────────► CIRT lead + Forensics lead
├── Chief Privacy Officer (named) ────────► (if customer NPI involved)
├── Records Officer (named) ──────────────► Records deputy
├── eDiscovery Manager (named) ───────────► eDiscovery Operator on-call + L3 backup
└── Microsoft TAM (named) ────────────────► Microsoft Support case owner

SEV-1 within 4 hours
├── Disclosure Committee chair ─── (CFO, GC, CEO designee) for 8-K materiality call
├── Audit Committee chair ──────── if matter touches financial reporting
└── External auditor lead partner ─ if matter touches financial reporting

SEV-1 within 24 hours
├── Microsoft Trust & Safety ───── for mass-spoliation events
├── Affected business unit head ── for operational impact awareness
└── HR (named) ─────────────────── if a custodian's actions appear willful

SEV-2 (within 4 hours of classification)
├── eDiscovery Manager (named)
├── Purview Compliance Admin on-call
├── Records Officer (named)
└── General Counsel (named) — notice only, not paged

SEV-3 (within 1 business day)
└── eDiscovery Operator queue
```

### 1.7 Worked example — SEV-1: Custodian mailbox deleted while under hold during pending FINRA Rule 8210 examination

**Background.** Firm receives a FINRA Rule 8210 request on Day 0 covering communications and Copilot interactions of three registered representatives ("RR-A", "RR-B", "RR-C") for a 2-year lookback. Production deadline: Day 30. eDiscovery Manager creates an eDiscovery (Premium) case and a case hold covering the three custodians' Exchange mailboxes, OneDrive, Teams chats, and (via the Copilot interactions location) their SubstrateHolds folders on Day 1. Hold status `Success` for all three on Day 2.

**Day 14: Incident.** A scripted offboarding workflow, triggered by an HR feed indicating RR-B's termination, deletes RR-B's mailbox and removes RR-B's Microsoft 365 license. The deletion succeeds despite the hold because the offboarding script uses an automation principal that holds the **Exchange Recipient Administrator** role and was not constrained by an Adaptive Scope that excluded held mailboxes. The deletion is detected at Day 16 when an eDiscovery Operator runs a routine search and finds zero results for RR-B.

**Triage (Day 16, 09:14 ET).**

- eDiscovery Operator confirms zero results, captures the search KQL, opens incident `INC-2026-04-0117`.
- Classification: **SEV-1** per §1.1 (confirmed loss of ESI subject to active legal hold AND active regulatory matter).
- Reportability tree:
  - Q1: YES (mailbox deleted).
  - Q2: YES (active hold; active 8210 matter).
  - Q3: TO BE DETERMINED — mailbox is within Microsoft 30-day soft-delete window for deleted users; SubstrateHolds may be recoverable.
  - Q4: YES — active FINRA 8210.
  - Q5: Production-deadline risk; counsel notification immediate.
  - Q6: Notification clock starts.
  - Q7: Begin evidence floor capture **before** any restoration attempt.

**War room (Day 16, 10:14 ET).**

- Attendees: GC, CCO, CISO, eDiscovery Manager, Records Officer, Microsoft TAM, outside e-discovery counsel.
- Decisions:
  1. Open Microsoft Severity A case requesting (a) inactive-mailbox conversion of RR-B's deleted mailbox before the 30-day soft-delete window expires, and (b) confirmation of SubstrateHolds preservation status.
  2. Capture all 13 evidence-floor artifacts before any restoration. Records Officer assigned as custodian.
  3. Issue litigation-hold reissuance letter to RR-A and RR-C reminding them of preservation duties; copy to their managers.
  4. CCO drafts FINRA 8210 status update advising of preservation incident and remediation in progress; outside counsel reviews before transmission. Decision: **transmit on Day 17** to preserve candor and reduce sanctions exposure.
  5. Initiate root-cause review of offboarding automation; pause the offboarding script tenant-wide pending RBAC remediation. (Compensating control.)
  6. NYDFS Part 500.17 evaluation: counsel determines event is reportable as a Cybersecurity Event because notice to FINRA is required → 72-hour clock starts at materiality determination (Day 16, 14:00 ET).

**Remediation (Day 16–18).**

- Microsoft Support converts RR-B's deleted mailbox to inactive on Day 16 (within the 30-day window); SubstrateHolds folder confirmed intact.
- eDiscovery (Premium) search reissued targeting the inactive mailbox; results return as expected; export to WORM begins.
- Offboarding script remediated (Day 17): added pre-flight check that calls `Get-CaseHoldPolicy` and aborts if any held policy includes the target mailbox; automation principal demoted from Exchange Recipient Administrator to a custom role lacking `Mailbox Delete` rights, with delete operations gated by a Compliance Manager approval.
- Day 17, 16:00 ET: FINRA 8210 status update transmitted by outside counsel.
- Day 18, 11:30 ET: NYDFS Part 500.17 notification submitted within 72-hour window.

**Closure.** Production met on Day 30 with full RR-B record. PIR (§8) completed Day 40. Permanent control changes: (i) all automation principals with destructive Exchange rights now require Privileged Identity Management just-in-time elevation; (ii) Adaptive Scopes implemented to exclude any mailbox under any active eDiscovery hold from offboarding workflows; (iii) standing weekly reconciliation between HR offboarding feed and eDiscovery hold inventory.

**Lessons embedded in this playbook.** Runbook 2.1 (hold not propagating) and Runbook 2.2 (SubstrateHolds empty) below incorporate the diagnostic queries developed during this incident. Anti-pattern AP-04 (relying on hold to block destructive admin actions) was added to §3 as a direct result.

---

## Section 2 — Failure-Mode Runbooks

Each runbook follows the same six-block structure: **Symptoms → Root cause → Diagnostic queries → Remediation → Validation → Evidence to capture**. Use these in conjunction with §1 incident handling; do **not** run remediation steps until §1.3 evidence floor has been captured.

> **Cmdlet endpoints by sovereign cloud.** All PowerShell below is shown for the commercial cloud. For sovereign clouds, swap the connection endpoint:
>
> - **Commercial / GCC:** `Connect-IPPSSession`
> - **GCC High:** `Connect-IPPSSession -ConnectionUri https://ps.compliance.protection.office365.us/powershell-liveid/ -AzureADAuthorizationEndpointUri https://login.microsoftonline.us/common`
> - **DoD:** `Connect-IPPSSession -ConnectionUri https://l5.ps.compliance.protection.office365.us/powershell-liveid/ -AzureADAuthorizationEndpointUri https://login.microsoftonline.us/common`
> - **21Vianet:** `Connect-IPPSSession -ConnectionUri https://ps.compliance.protection.partner.outlook.cn/powershell-liveid/ -AzureADAuthorizationEndpointUri https://login.partner.microsoftonline.cn/common` — note that 21Vianet **still uses classic eDiscovery** as of this revision; cmdlet names below that begin with `Get-Compliance*` and `Get-CaseHold*` apply, but the **portal experience** in 21Vianet differs from the unified experience and runbook UI screenshots reference the commercial cloud.

### Runbook 2.1 — Hold not propagating (status remains `Pending` or `Failed`)

**Symptoms.**

- `Get-CaseHoldPolicy -Identity <name> -DistributionDetail` returns `Pending` for one or more locations >24 hours after creation.
- Or returns `Failed` for one or more locations.
- eDiscovery (Premium) search returns content from preservation locations that should be held but appears to be deleted, suggesting the hold never actually attached.

**Root cause (in descending order of frequency).**

1. **Propagation latency** — published Microsoft guidance is "up to several hours"; field experience shows up to **24 hours** is within normal range for tenants with large mailbox counts or complex Adaptive Scopes. Pending status alone within the first 24 hours is **not** a defect.
2. **Adaptive Scope query mismatch** — the scope's filter excludes the intended custodian (e.g., scope filters on `Department -eq "Wealth Mgmt"` but custodian's directory attribute is `Wealth Management`).
3. **Mailbox not yet provisioned** — for newly hired custodians, the mailbox may not be fully provisioned when the hold is created; the hold cannot attach to a non-existent mailbox.
4. **Inactive mailbox edge case** — for terminated custodians whose mailbox was inactivated, the hold must target the inactive mailbox by `ExchangeGuid`, not by UPN.
5. **License gap** — Exchange Online Plan 2 (or equivalent) is required for held mailboxes >50 GB; held mailbox approaching size limit may stall.
6. **Service incident** — concurrent Microsoft service incident affecting Substrate or Purview.
7. **Permission bug** — the principal that created the hold lacks `Hold` right on the target location (e.g., a SharePoint site collection where the principal lacks Site Collection Administrator).

**Diagnostic queries.**

```powershell
# 1. Capture full hold definition.
Connect-IPPSSession
$case   = "FINRA-8210-2026-04"
$policy = Get-CaseHoldPolicy -Identity "$case-Hold" -Case $case -DistributionDetail
$policy | Format-List Name, Enabled, Mode, ExchangeLocation, SharePointLocation, `
    PublicFolderLocation, DistributionStatus, LastStatusUpdateTime
$policy.DistributionResults | Format-Table Location, Status, ResultMessage -AutoSize

# 2. Capture rule (KQL).
Get-CaseHoldRule -Policy "$case-Hold" | Format-List Name, ContentMatchQuery, Disabled

# 3. Compare hold's ExchangeLocation against custodian's actual recipient identity.
$custodian = "rr-b@contoso.com"
Get-Recipient -Identity $custodian | Format-List Name, PrimarySmtpAddress, ExchangeGuid, RecipientTypeDetails

# 4. For inactive mailboxes, target by ExchangeGuid.
Get-Mailbox -InactiveMailboxOnly -Identity $custodian | Format-List ExchangeGuid, IsInactiveMailbox

# 5. Check Service Health for concurrent advisories.
# Microsoft 365 admin center → Health → Service health → filter "Exchange Online" + "Microsoft Purview"

# 6. Audit log for hold creation and modification events.
Search-UnifiedAuditLog -StartDate (Get-Date).AddDays(-7) -EndDate (Get-Date) `
    -RecordType ComplianceDLPExchange,DiscoveryAdministration `
    -Operations CaseHoldPolicyCreated,CaseHoldPolicyChanged,CaseHoldRuleCreated,CaseHoldRuleChanged `
    | Format-Table CreationDate, UserIds, Operations, AuditData
```

**Remediation.**

1. **If <24 hours since creation and status is `Pending`:** wait. Do not modify the hold; modifications restart propagation.
2. **If >24 hours `Pending` with no Service Health advisory:** open Microsoft Severity B case with the diagnostic output above. Do not delete and recreate; re-creation does not accelerate propagation and loses the original creation timestamp (which is forensically relevant).
3. **If status is `Failed` with `ResultMessage` indicating scope mismatch:** edit the Adaptive Scope query, validate against `Get-Recipient` output for the intended custodian, save the scope, then **wait** — scope changes also propagate over hours.
4. **If failure is due to inactive mailbox not targeted:** add the mailbox to the hold by `ExchangeGuid` using `Set-CaseHoldPolicy -Identity <name> -AddExchangeLocation <ExchangeGuid>`.
5. **If license gap:** apply correct license, then re-evaluate; do not delete the hold.
6. **In all cases:** while remediation is in flight, invoke compensating controls (§1.4): Records Officer hold-letter reissuance, manual journaling if SEV-1.

**Validation.**

- `DistributionStatus` returns `Success` for all locations.
- Test custodian sends a test Copilot prompt; within 12 hours, the prompt+response appear in an eDiscovery (Premium) search scoped to that custodian's `Copilot interactions location` and `SubstrateHolds`.
- Test deletion: have the custodian (with counsel approval) hard-delete a non-evidentiary test item; within 1 hour, item appears in `SubstrateHolds` (preservation worked).

**Evidence to capture.**

- Hold definition before remediation, after remediation.
- `DistributionResults` per location, before and after.
- Audit-log records for any policy/rule modification.
- Microsoft Support case number and summary disposition.
- Service Health advisory IDs (if any).
- Validation test artifacts (test prompt content, search result screenshots, timestamps).

---

### Runbook 2.2 — `SubstrateHolds` folder empty for a custodian known to have used Copilot

**Symptoms.**

- eDiscovery (Premium) search scoped to a custodian's `Recoverable Items\SubstrateHolds` returns zero items.
- Microsoft 365 Copilot Usage report shows the custodian had Copilot activity in the period.
- The custodian is, or was, under an eDiscovery hold or org-wide retention policy that should have routed Copilot interactions to `SubstrateHolds`.

**Root cause.**

1. **No retention or hold policy was in effect at the time of the Copilot activity.** Without a hold or a retention policy that covers Teams chats / Copilot interactions, deleted Copilot interactions are purged on the standard Substrate cycle (default 30 days `Recoverable Items` → permanent deletion). `SubstrateHolds` is populated **only** when preservation is required.
2. **Custodian deleted Copilot interactions before any hold attached.** Pre-hold deletions are not recoverable from `SubstrateHolds` past the 30-day soft-delete window.
3. **Search location misconfigured.** Search was scoped to mailbox custom location only and not to the dedicated `Copilot interactions` location card — Microsoft has progressively split Copilot evidence collection across both surfaces; matter teams should select **both**.
4. **Copilot Studio agent transcripts** — these may persist to **Dataverse**, not the user's mailbox. There is **no** SubstrateHolds equivalent for a Dataverse-only agent transcript; preservation must be configured on the Dataverse environment (long-term retention, Dataverse audit, environment hold), not via Purview Exchange-side mechanisms.
5. **License downgrade after Copilot use.** If the custodian was downgraded from Microsoft 365 Copilot to a SKU without Copilot, historical interactions remain but newer surfaces (e.g., Copilot Pages) may have moved.
6. **Tenant-level Copilot retention setting "Do not retain" or short retention** that purged before the hold attached.

**Diagnostic queries.**

```powershell
# 1. Confirm custodian had Copilot activity.
# Microsoft 365 admin center → Reports → Usage → Microsoft 365 Copilot
# Or via Microsoft Graph reports API:
# GET /reports/getMicrosoft365CopilotUsageUserDetail(period='D30')

# 2. Confirm a retention policy / hold covered the period.
Get-RetentionCompliancePolicy | Where-Object { $_.Workload -match "Teams" -or $_.Workload -match "Exchange" } |
    Format-Table Name, Enabled, ExchangeLocation, ModernGroupLocation, TeamsChatLocation

Get-CaseHoldPolicy -Case <case> -DistributionDetail | Format-List Name, ExchangeLocation, CreatedTime

# 3. Search via Copilot interactions location card (Purview portal → eDiscovery → Search → Locations →
#    "Copilot interactions" toggle ON; add custodian; save and run estimate).

# 4. Audit-log: did Copilot interactions exist for the period?
Search-UnifiedAuditLog -StartDate <start> -EndDate <end> `
    -UserIds rr-b@contoso.com -RecordType CopilotInteraction `
    | Format-Table CreationDate, Operations, AuditData
# NOTE: CopilotInteraction record contains METADATA only. Absence of records here
# is meaningful (custodian had no Copilot use, OR audit ingestion lag of up to 24h);
# presence does NOT give you the prompt/response body — that requires eDiscovery search
# of the mailbox-side store.

# 5. Copilot Studio agents — Dataverse side.
# Power Platform admin center → Environments → <env> → Auditing → Audit history
# Verify long-term retention is configured if agent transcripts are evidentiary.
```

**Remediation.**

1. **If pre-hold deletion confirmed:** counsel notification immediately. The data is gone; the question is whether the deletion was within the custodian's reasonable expectation of routine retention or constituted spoliation. This is a Q3-NO branch in §1.2.
2. **If search misconfigured:** rerun with both Custom locations + Copilot interactions location selected.
3. **If Copilot Studio Dataverse gap:** engage Power Platform Admin and agent owner; capture Dataverse audit logs; counsel evaluates whether the gap requires disclosure to opposing counsel/regulator.
4. **If tenant retention setting is the cause:** do not change it during an active matter without counsel approval (changing it may destroy more evidence). Document the setting; counsel decides next steps.
5. **Going forward:** add a tenant-wide retention policy that covers Teams chats and Copilot interactions at minimum 7 years (matches SEC 17a-4(b)(4)); see Control 1.13 for retention pattern.

**Validation.**

- Search returns expected non-zero results when locations are correctly scoped.
- Or: confirmed and documented that absence is correct (no hold + no retention = no preservation expected).

**Evidence to capture.**

- Copilot Usage report PDF + JSON.
- Retention policy inventory at time of incident.
- Hold inventory at time of incident.
- UAL `CopilotInteraction` records for period.
- Search definition (with both location surfaces selected) and results.
- Counsel determination memo on whether the gap is reportable.

---

### Runbook 2.3 — eDiscovery (Premium) search returns zero or implausibly low results for active custodian

**Symptoms.**

- Estimated statistics show 0 items, or a count that is implausibly low given the custodian's known activity.
- Same KQL run against a different custodian returns expected results.
- Or: same KQL run yesterday returned N items, today returns substantially fewer.

**Root cause.**

1. **KQL syntax error** that yields a false-zero — most commonly mis-quoted phrases, missing parentheses, or wildcard that resolves to nothing (`*` is not allowed as a leading wildcard in many fields).
2. **Anti-pattern AP-01: searching for `from:"Copilot"` or `participants:"copilot"` to find Copilot interactions.** Copilot interactions are **not** stored as messages from a `Copilot` sender. They are stored in `SubstrateHolds` as a distinct item class. Use the **Copilot activity condition card** in the search builder, **or** scope to the `Copilot interactions` location, **not** keyword search for "Copilot".
3. **Locations selected do not include where the data lives.** For Copilot evidence, you typically need: the user's mailbox (Custom location), the Copilot interactions location card, and OneDrive (citations).
4. **Date filter is in wrong time zone.** Purview eDiscovery date filters are in **UTC**. A search for "April 1" in ET will miss items created in the first 4–5 hours of April 1 ET.
5. **Indexing lag.** Newly created items can take up to 1 hour to be indexed for search. For very recent activity, run estimate again after 1–2 hours.
6. **Partially indexed items** — an item may exist but not appear in keyword results if it failed indexing. Use `IncludeUnindexedItems` on the search and, in eDiscovery (Premium), enable "Include partially indexed items" in the search settings.
7. **Permission scope** — the searching principal's Compliance Boundary or Adaptive Scope assignment may exclude the custodian.
8. **Hold-only KQL on the search** — confusing the hold's `ContentMatchQuery` with the search's KQL; a hold scoped to a narrow KQL preserves only matching items, but **the search does not need to match the hold KQL** to find unheld items.

**Diagnostic queries.**

```powershell
# 1. Capture the search definition exactly.
Get-ComplianceSearch -Identity "<search-name>" |
    Format-List Name, ContentMatchQuery, ExchangeLocation, SharePointLocation, `
        PublicFolderLocation, AllowNotFoundExchangeLocationsEnabled

# 2. Capture statistics with partially-indexed items separated.
Get-ComplianceSearch -Identity "<search-name>" |
    Format-List Status, Items, Size, UnindexedItems, UnindexedSize, ErrorTag

# 3. Run a no-KQL counter-test scoped only to the custodian's mailbox for the matter date range
#    to establish a baseline of "what is there at all".
New-ComplianceSearch -Name "DIAG-<custodian>-<date>" `
    -ExchangeLocation rr-b@contoso.com `
    -ContentMatchQuery "received>=2026-03-01 AND received<=2026-04-30"
Start-ComplianceSearch -Identity "DIAG-<custodian>-<date>"
Get-ComplianceSearch -Identity "DIAG-<custodian>-<date>" | Format-List Items, Size, UnindexedItems

# 4. Confirm Copilot activity location is selected (portal-only check; PowerShell does not
#    yet expose the location card toggle as a single property).
```

**Remediation.**

1. **Strip the KQL to nothing**, run estimate again. If you now get expected items, the KQL was the problem. Rebuild the KQL incrementally.
2. **Replace `from:"Copilot"` and similar with the Copilot activity condition card** in the search builder. (Anti-pattern AP-01.)
3. **Add the Copilot interactions location card** if Copilot evidence is in scope.
4. **Re-express the date filter in UTC** explicitly (`received>=2026-04-01T00:00:00Z`).
5. **Wait 1–2 hours** for indexing of recent items, then re-estimate.
6. **Enable partially-indexed items** in the search and review the unindexed bucket as a separate review set.
7. **Verify Compliance Boundary assignment** for the searching principal; if the principal is scoped to a different boundary, request boundary expansion or transfer the search to a properly scoped principal.

**Validation.**

- A counter-test search with no KQL returns plausible item counts.
- The original search, after remediation, returns counts consistent with the counter-test minus expected KQL filtering.
- A test prompt sent by the custodian appears in the search after the indexing lag.

**Evidence to capture.**

- Original search definition, all subsequent revisions.
- Statistics outputs at each iteration.
- Counter-test search definition and statistics.
- KQL change log with rationale per change.

---

### Runbook 2.4 — Copilot activity condition card returns unexpected zero

**Symptoms.**

- Search uses the Copilot activity condition card with a custodian who is known to have used Copilot in the period.
- Card returns zero matching activities.
- Other Copilot evidence (e.g., Usage report) confirms activity.

**Root cause.**

1. The card filters on **first-party Microsoft 365 Copilot** activity only. Copilot Studio agent activity, Copilot for Sales, Copilot for Service, and third-party agents declared in the Microsoft 365 admin center may not be enumerated by this card.
2. Date filter inside the card is in UTC and does not match the date filter outside the card.
3. The custodian's interactions occurred in a **canceled/abandoned** state and were not persisted as an `interaction` record.
4. The activity occurred in a workload (e.g., Loop) that is not yet covered by the Copilot activity card.

**Diagnostic queries.**

```powershell
# 1. UAL CopilotInteraction enumeration as a cross-check.
Search-UnifiedAuditLog -StartDate <start> -EndDate <end> -UserIds <upn> `
    -RecordType CopilotInteraction -ResultSize 5000 |
    Group-Object { ($_.AuditData | ConvertFrom-Json).AppHost } |
    Format-Table Count, Name -AutoSize
# AppHost values include Word, Excel, PowerPoint, Teams, Outlook, BizChat, M365App, etc.

# 2. Copilot Studio agent enumeration via Power Platform.
# Power Platform admin center → Environments → <env> → Resources → Copilot Studio agents.
# Capture environment ID; pull Dataverse audit for agent runs separately.
```

**Remediation.**

1. **Augment the search with mailbox + Copilot interactions location card** (do not rely solely on the activity condition card).
2. **For Copilot Studio gaps:** open a separate Dataverse-side preservation workstream; capture audit history; counsel decides reportability.
3. **Document the card's coverage limits** in the search rationale memo so the search defensibility record is complete.

**Validation.**

- Combined search (location card + activity card) returns counts consistent with UAL CopilotInteraction enumeration.

**Evidence to capture.**

- UAL enumeration grouped by AppHost.
- Card filter definition.
- Counter-test results with combined locations.

---

### Runbook 2.5 — Export job stalls or fails repeatedly

**Symptoms.**

- Export job in eDiscovery (Premium) reports `In progress` for >24 hours with no progress percentage change.
- Or fails with `Failed` and a generic error.
- Or download via Microsoft Edge eDiscovery export tool stalls partway.

**Root cause.**

1. **Export package size** — multi-TB exports are slow and may time out segments. Microsoft recommends splitting exports >1 TB.
2. **Network throughput** between the reviewer workstation and Azure Blob storage backing the export.
3. **Export tool authentication expiry** — the export key issued for the package has a finite life; re-issue if the tool repeatedly authenticates.
4. **Browser version** — the export tool requires Microsoft Edge; older Chromium versions may not function.
5. **Partially indexed items in scope without "Include partially indexed items" enabled** — these may stall the export.
6. **Service-side throttling** during peak times.
7. **PST format vs. individual messages format** — PST format is slower and has a 50 GB per-PST cap.

**Diagnostic queries.**

```powershell
# 1. Capture export job definition and status.
Get-ComplianceSearchAction -Identity "<search-name>_Export" |
    Format-List Name, Action, Status, JobStartTime, JobEndTime, Errors, Results

# 2. Count items in the underlying review set / search.
Get-ComplianceSearch -Identity "<search-name>" | Format-List Items, Size

# 3. Network test from reviewer workstation.
# Test-NetConnection blob.core.windows.net -Port 443
```

**Remediation.**

1. **For >1 TB exports: split** by date range or by custodian; relaunch as multiple smaller jobs.
2. **Switch export format** from PST to individual messages if PST is the bottleneck.
3. **Re-issue export key** in the portal; restart download from the same byte offset (the export tool supports resume).
4. **Update Microsoft Edge** to current channel.
5. **Move reviewer workstation** to a higher-bandwidth network segment, or use an Azure VM in the same region as the export storage as a staging host.
6. **Open Microsoft Severity B case** if export fails with cryptic error after the above steps.
7. **Never** consider an aborted export as a "completed" record. Aborted exports must be deleted and re-issued; partial packages have indeterminate completeness and are not defensible.

**Validation.**

- Export `Status` = `Completed`, `Results` includes a non-zero `Total estimated items`, `Total exported items` matches.
- Manifest hash verification (Runbook 2.6) succeeds.
- Reviewer can open the package locally, item counts match.

**Evidence to capture.**

- Export action definition, full status output.
- Manifest file.
- Per-item hash file.
- Reviewer workstation performance counters during download (optional but recommended).
- Microsoft Support case number if opened.

---

### Runbook 2.6 — Export package hash-chain mismatch

**Symptoms.**

- After download, the local computed hash for one or more items does not match the hash recorded in the export manifest.
- Or the manifest itself fails its integrity signature.

**Root cause.**

1. **Transit corruption** during download (most common; re-download usually resolves).
2. **Storage tier corruption** on the reviewer workstation (failing disk).
3. **Antivirus modification** of files post-download (some AV products inject metadata).
4. **Export tool bug** — rare but possible, especially on outdated Edge versions.
5. **Tampering** — only conclude this after exhausting 1–4.

**Diagnostic queries.**

```powershell
# 1. Recompute hashes locally and compare to manifest.
$manifest = Import-Csv "C:\Exports\<case>\manifest.csv"
$mismatches = foreach ($row in $manifest) {
    $localHash = (Get-FileHash -Algorithm SHA256 -Path $row.Path).Hash
    if ($localHash -ne $row.Hash) {
        [pscustomobject]@{ Path = $row.Path; ManifestHash = $row.Hash; LocalHash = $localHash }
    }
}
$mismatches | Format-Table -AutoSize
$mismatches | Export-Csv "C:\Exports\<case>\hash-mismatches.csv" -NoTypeInformation
```

**Remediation.**

1. **Re-download** the affected item(s) using export-tool resume.
2. **If still mismatched after second download:** open Severity B Microsoft case attaching the manifest and hash-mismatches CSV.
3. **Disable AV scanning** on the export landing folder during download (with security team approval and time-boxed exception).
4. **Move download to a different workstation** to rule out local disk corruption.
5. **Never alter** the manifest to "fix" a mismatch. Hash mismatches are forensic events; document, do not edit.
6. **If tampering is suspected:** stop, preserve the artifact, escalate to L4 and CIRT immediately.

**Validation.**

- Re-downloaded package: 100% hash match against manifest.
- Manifest signature verification (where supported) passes.

**Evidence to capture.**

- Original mismatch report.
- Re-download log and second hash report.
- Microsoft Support case if escalated.
- AV exclusion request and approval (if invoked).

---

### Runbook 2.7 — Reviewer cannot access review set / export misassigned

**Symptoms.**

- Reviewer with `Reviewer` role assignment cannot see the case or review set.
- Or: the export was downloaded by a person not on the named reviewer roster, suggesting RBAC over-grant.

**Root cause.**

1. **Role assignment scoped to wrong case** — the eDiscovery RBAC model assigns reviewers per case, not tenant-wide.
2. **Compliance Boundary** restricts the reviewer's principal from the custodian's geography/business unit.
3. **PIM (Privileged Identity Management) eligibility** not yet activated — the reviewer is eligible but has not activated for the current session.
4. **Group membership replication delay** when the reviewer is added via a security group rather than directly.
5. **Over-broad role assignment** — the `eDiscovery Administrator` role grants visibility into all cases tenant-wide; if a non-named principal holds it, that is a compliance defect (separation-of-duties violation; see Control 1.5).

**Diagnostic queries.**

```powershell
# 1. Inventory eDiscovery roles tenant-wide.
$roleGroups = "eDiscovery Manager", "eDiscovery Administrator", "Reviewer", "Compliance Administrator", "Compliance Data Administrator"
foreach ($rg in $roleGroups) {
    "=== $rg ==="
    Get-RoleGroupMember -Identity $rg | Format-Table Name, RecipientType -AutoSize
}

# 2. Per-case membership.
Get-ComplianceCase -Identity "<case>" | Format-List Name, CaseType, Status, Members
Get-ComplianceCaseMember -Case "<case>" | Format-Table Name, Role -AutoSize

# 3. Compliance Boundary assignment.
Get-RoleGroup | Where-Object { $_.RoleAssignmentPolicy -ne $null } |
    Format-List Name, AssignedRoles, Members
```

**Remediation.**

1. **For missing access:** add the reviewer's principal to the case's reviewer roster (not tenant role group). Record the change in the case audit log.
2. **For over-broad assignment:** remove the principal from the tenant role group; reassign per case only. If the principal had access in violation of separation of duties, treat as a compliance event (see Control 1.5).
3. **For PIM eligibility:** instruct reviewer to activate; verify activation in Entra audit log.
4. **For Compliance Boundary mismatch:** evaluate whether the case requires a cross-boundary reviewer; if so, document the boundary exception and counsel approval.

**Validation.**

- Reviewer can access only the case(s) and review set(s) they are named on.
- Case audit log shows their access events.
- No principal holds `eDiscovery Administrator` outside the named eDiscovery Manager rota.

**Evidence to capture.**

- Role-group inventory before and after.
- Case-member list before and after.
- PIM activation logs (Entra audit).
- Counsel approval memo for any boundary exception.

---

### Runbook 2.8 — Retired Standard / classic eDiscovery cmdlet errors after August 31, 2025

**Symptoms.**

- Scripts that worked prior to August 31, 2025 fail with errors such as `The term '<cmdlet>' is not recognized` or `The case is not accessible from this experience`.
- Portal redirects from classic eDiscovery URLs to the unified experience at `purview.microsoft.com`.

**Root cause.**

- Microsoft retired classic eDiscovery in commercial, GCC, GCC High, and DoD clouds on **August 31, 2025**. Cases were migrated to the unified eDiscovery experience. Some classic-only cmdlets and parameters were removed; others retained the same name but changed behavior.
- The **21Vianet** sovereign cloud retains classic eDiscovery as of this revision; scripts targeting 21Vianet should not be migrated to the unified-only patterns until Microsoft announces 21Vianet retirement.

**Diagnostic queries.**

```powershell
# Confirm cloud target.
Get-ConnectionInformation | Format-List ConnectionUri, AzureADAuthorizationEndpointUri, TenantId

# Confirm cmdlet availability.
Get-Command Get-ComplianceCase | Format-List Name, Module, ParameterSets
```

**Remediation.**

1. **Inventory all eDiscovery scripts** firm-wide; tag each by cloud (commercial vs. 21Vianet).
2. **For commercial/GCC/GCC High/DoD scripts:** migrate to unified-experience cmdlets. Notably:
   - `Get-ComplianceCase`, `New-ComplianceCase`, `Get-CaseHoldPolicy`, `New-CaseHoldPolicy`, `Get-ComplianceSearch`, `New-ComplianceSearch`, `Start-ComplianceSearch`, `Get-ComplianceSearchAction`, `New-ComplianceSearchAction` remain valid.
   - Standard-eDiscovery-only parameters or the Standard eDiscovery case type are no longer available; all cases are Premium-equivalent in the unified experience.
3. **For 21Vianet scripts:** retain classic patterns; add explicit endpoint variable; do not co-mingle with commercial scripts.
4. **Retest all scripts in non-production tenant** before relying on them in a live matter.
5. **Update internal documentation, runbooks, and onboarding materials** to reference the unified portal URL `https://purview.microsoft.com` and not legacy `compliance.microsoft.com` or `protection.office.com` URLs.

**Validation.**

- All scripts run cleanly in target cloud.
- Test case can be created, hold applied, search run, export completed end-to-end via scripts.

**Evidence to capture.**

- Script inventory with migration status.
- Test-tenant validation logs.
- Microsoft Learn references for each migrated cmdlet.

---

### Runbook 2.9 — Cross-tenant guest custodian: this tenant's hold does not preserve home-tenant data

**Symptoms.**

- A custodian is a B2B guest in the firm's tenant.
- The firm creates an eDiscovery hold on the guest's principal.
- An eDiscovery search of the guest's mailbox returns zero results.
- The guest's actual mailbox is in their home tenant; this tenant has no preservation authority over it.

**Root cause.**

- A B2B guest principal in tenant A does **not** have a mailbox in tenant A. Their mailbox is in their home tenant B. Tenant A's eDiscovery holds cannot preserve content in tenant B's mailbox.
- The guest's activity in the firm's tenant (Teams chats, SharePoint file actions, Copilot interactions on the firm's resources) **is** in scope of the firm's preservation tools, but routes to different stores than the guest's mailbox.

**Diagnostic queries.**

```powershell
# 1. Confirm principal type.
Get-User -Identity "guest@external.com" | Format-List UserPrincipalName, RecipientType, ExternalDirectoryObjectId
Get-Recipient -Identity "guest@external.com" | Format-List RecipientType, RecipientTypeDetails

# 2. Identify Teams / SharePoint footprint of the guest in this tenant.
Search-UnifiedAuditLog -StartDate <start> -EndDate <end> -UserIds "guest@external.com" |
    Group-Object RecordType | Format-Table Count, Name
```

**Remediation.**

1. **Document the scoping gap** in the matter file and counsel-notify immediately.
2. **Preserve in this tenant** what is preservable: Teams chat content (1:1 and channel) where the guest participated, SharePoint files the guest touched, audit-log records of guest activity.
3. **Counsel decides** whether to seek production from the guest's home-tenant organization via subpoena or cooperation request.
4. **Do not represent** to opposing counsel or regulator that the guest's home-tenant data has been preserved by the firm; that is outside the firm's control.
5. **Going forward:** review B2B guest policies; consider whether sensitive matters should restrict guest participation or use a cross-tenant access policy that limits Copilot exposure.

**Validation.**

- Tenant-side preservation confirmed (Teams chats, SharePoint, audit log) for guest activity.
- Counsel-approved scoping memo on file.

**Evidence to capture.**

- Recipient/User cmdlet output proving guest principal type.
- UAL inventory of guest activity in tenant.
- Counsel scoping memo.
- Any subpoena/cooperation correspondence with home-tenant organization (counsel-controlled).

---

## Section 3 — Anti-Patterns

The patterns below are observed failure modes in FSI eDiscovery operations. Each is paired with the recommended pattern. The presence of any of these in the firm's procedures, scripts, or training materials is itself a finding for internal audit.

| # | Anti-pattern | Why it fails | Recommended pattern |
|---|---|---|---|
| **AP-01** | Searching for Copilot interactions using `from:"Copilot"`, `participants:"Copilot"`, or keyword `"Copilot"` in the body. | Copilot interactions are not stored as messages from a Copilot sender; they live in `SubstrateHolds` as a distinct item class. Keyword search misses the canonical store. | Use the **Copilot interactions location** card and/or the **Copilot activity condition** card in the search builder. |
| **AP-02** | Treating the eDiscovery export package itself as WORM-compliant for SEC 17a-4(f) audit-trail alternative reliance. | The export package is a ZIP/PST/folder; it is not inherently immutable. WORM compliance depends on the **storage tier** the package lands on (immutable Azure Blob, Purview-managed key with locked retention, or a third-party WORM appliance). | Land exports in a configured WORM tier; capture the immutability proof (storage policy, retention lock) as part of the evidence floor. |
| **AP-03** | Asserting that the `CopilotInteraction` Unified Audit Log record contains the prompt and response body. | The `CopilotInteraction` UAL record contains **metadata only** (timestamp, user, app host, action). The prompt/response body lives in the user's mailbox-side `SubstrateHolds`. Relying on UAL alone yields incomplete production. | Always pair UAL enumeration (for activity discovery) with eDiscovery (Premium) search of the mailbox-side store (for content). |
| **AP-04** | Relying on a hold to block destructive admin actions (e.g., assuming `Remove-Mailbox` will fail if a hold is in effect). | Holds preserve content via the soft-delete pipeline; they do not gate administrative APIs. A privileged principal can still delete a mailbox; the deleted mailbox is recoverable as **inactive** within the soft-delete window only. | Layer **RBAC least privilege**, **PIM just-in-time elevation**, **Adaptive Scopes excluding held objects from destructive workflows**, and **change-control approval gates** on top of holds. (See Control 1.5.) |
| **AP-05** | Citing "15–30 minutes" as the hold propagation expectation. | Microsoft documents propagation as "up to several hours"; field experience extends to **24 hours** for large or scoped tenants. Internal SLAs based on 15–30 minutes generate false alarms and erode confidence. | Document the propagation expectation as **"up to 24 hours; pending status within that window is not a defect"**. Counsel-defensible SLAs use this floor. |
| **AP-06** | Deleting and recreating a hold to "fix" a stalled propagation. | Re-creation does not accelerate propagation, **does** lose the original creation timestamp (forensically relevant), and risks a coverage gap during the moments between deletion and re-creation. | Wait the published window; open a Microsoft Severity B case if exceeded; never delete-recreate without counsel approval. |
| **AP-07** | Modifying a hold's KQL filter mid-matter without counsel approval. | The hold's `ContentMatchQuery` defines preservation scope. Narrowing it post-creation may purge previously preserved items; broadening it restarts propagation and may create the appearance of a coverage gap. | Treat hold scope as a counsel decision; modifications go through the matter's change-control. Capture before/after diffs in the case audit log. |
| **AP-08** | Using a single shared `eDiscovery Administrator` service account for routine work. | The `eDiscovery Administrator` role grants tenant-wide access to all cases, breaking matter compartmentalization and separation of duties. Shared accounts also defeat actor attribution. | Use named human principals with PIM elevation; reserve `eDiscovery Administrator` for genuine cross-case operations and emergency access. (See Control 1.5.) |
| **AP-09** | Ignoring the partially-indexed items bucket in search results. | Partially indexed items may contain responsive content that the keyword search did not reach. Producing only the indexed bucket and silently dropping the unindexed bucket is a **completeness defect** under FRCP 26(g). | Always include partially indexed items in search and review; document review of the unindexed bucket; produce or withhold with logged reason. |
| **AP-10** | Treating Copilot Studio agent transcripts as captured by Exchange-side preservation. | Copilot Studio agent transcripts may persist only to **Dataverse**. Exchange holds and `SubstrateHolds` do not cover Dataverse-only transcripts. | Configure Dataverse long-term retention and audit; treat Copilot Studio agents as a **separate preservation workstream** with its own controls. |
| **AP-11** | Performing exports to a reviewer's local workstation `Downloads` folder. | Local downloads bypass WORM, lack chain-of-custody enforcement, and are mixed with non-evidentiary content. AV scans may modify files. | Land exports on a designated immutable storage tier accessed via a managed reviewer workstation or Azure VM in the same region. |
| **AP-12** | Communicating sensitive matter details via distribution lists. | DLs fail silently (membership drift, mailbox over-quota), provide weak attribution, and may include unintended recipients. | Communicate via **named recipients** for SEV-1/SEV-2; use a matter-specific Teams channel with a closed membership audited weekly. |
| **AP-13** | Skipping the chain-of-custody form because "the export package has hashes". | Hashes prove integrity of the data at hash time; chain of custody proves **who handled the data and when**. Without chain of custody, FRCP 37(e) intent analysis is harder to defend and SEC 17a-4(f) audit-trail alternative reliance is weaker. | Always sign the chain-of-custody form at every transfer; retain for life of matter + 7 years. |
| **AP-14** | Counting an aborted or partial export as "complete enough" to ship. | Partial exports have indeterminate completeness. Producing one constitutes a representation that the package is the search result, which is not true if items are missing. | Always re-issue and re-validate aborted exports; never ship a partial. |
| **AP-15** | Letting the Microsoft 365 Copilot tenant retention default control matter preservation. | Tenant-wide Copilot retention defaults are operational, not matter-specific. Relying on them for matter preservation conflates routine retention with legal hold and creates ambiguity if the default is changed. | Apply matter-specific case holds for active matters; maintain a separate org-wide retention policy at minimum 7 years for the SEC 17a-4(b)(4) baseline. |

---

## Section 4 — Sovereign Cloud Matrix

Behavior of eDiscovery on Copilot interactions varies by Microsoft sovereign cloud. Confirm cloud-of-record at incident triage; cite cloud in every status update.

| Capability | Commercial | GCC | GCC High | DoD | 21Vianet (China) |
|---|---|---|---|---|---|
| **Unified eDiscovery experience at `purview.microsoft.com`** | Available (post-Aug 31 2025) | Available | Available | Available | **Not available — classic eDiscovery still in use** |
| **Microsoft 365 Copilot availability** | GA | GA | Limited (verify current Microsoft Roadmap; not all surfaces parity) | Limited (verify) | **Not available** in 21Vianet as of this revision |
| **Copilot Studio availability** | GA | GA | Yes (verify connectors) | Yes (verify connectors) | Limited |
| **`SubstrateHolds` preservation container** | Yes | Yes | Yes | Yes | Yes (within the classic eDiscovery experience) |
| **Copilot interactions location card in search builder** | Yes | Yes | Yes | Yes | N/A (classic experience) — use mailbox custom location and `SubstrateHolds` |
| **Copilot activity condition card in search builder** | Yes | Yes | Yes (verify) | Yes (verify) | N/A (classic) |
| **PowerShell connection endpoint** | `https://ps.compliance.protection.outlook.com/powershell-liveid/` | Same as Commercial | `https://ps.compliance.protection.office365.us/powershell-liveid/` | `https://l5.ps.compliance.protection.office365.us/powershell-liveid/` | `https://ps.compliance.protection.partner.outlook.cn/powershell-liveid/` |
| **Authorization endpoint** | `https://login.microsoftonline.com/common` | Same | `https://login.microsoftonline.us/common` | `https://login.microsoftonline.us/common` | `https://login.partner.microsoftonline.cn/common` |
| **Microsoft Graph endpoint for reports** | `graph.microsoft.com` | Same | `graph.microsoft.us` | `dod-graph.microsoft.us` | `microsoftgraph.chinacloudapi.cn` |
| **Microsoft Support severity model** | Standard A/B/C | Standard | Standard (FedRAMP-cleared engineers) | Standard (DoD-cleared engineers) | Operated by 21Vianet; severity model parallel but staffed locally |
| **Trust & Safety escalation pathway** | Microsoft Customer Trust | Same | Same (US-cleared) | Same (US-cleared) | Via 21Vianet operations |
| **FedRAMP boundary considerations** | N/A | FedRAMP Moderate | FedRAMP High + DFARS / ITAR | DoD IL5 | N/A |
| **Cross-cloud guest interactions (Commercial ↔ GCC ↔ GCC High)** | Constrained by cross-cloud B2B policy; not all guest scenarios supported | Constrained | Constrained | Constrained | Effectively isolated |
| **Production deadlines may require local data-protection coordination** | N/A | Per agency | Per agency + ITAR | Per DoD | **PIPL / DSL / CSL coordination required**; cross-border transfers face restrictions |

> **21Vianet caveat.** Because 21Vianet retains classic eDiscovery, runbooks 2.1–2.9 above apply with the following adjustments: (a) the **portal screenshots** in the companion `portal-walkthrough.md` show the unified experience and do not match 21Vianet; (b) **Copilot is not generally available** in 21Vianet as of this revision, so the Copilot-specific runbooks (2.2, 2.4) are largely inapplicable until Microsoft announces 21Vianet Copilot availability; (c) **cross-border data transfers** for export production are subject to PIPL Article 38 and the CAC standard contract or security assessment regime — coordinate with Chinese counsel before any export leaves the China region.

---

## Section 5 — Escalation Ladder (L1 → L4)

Escalation thresholds below are **trigger conditions**, not discretionary judgment calls. If a trigger is met, escalation is automatic. The on-call may also escalate at any time on judgment.

### L1 — Service Desk / eDiscovery Operator

**Scope.** SEV-3 and SEV-4 incidents; routine portal navigation issues; reviewer access provisioning within scope; first-pass diagnosis of search and export failures.

**Authority.** Run estimates and exports against existing searches; provision case-scoped reviewer access; open Microsoft Severity C cases.

**Cannot.** Create or modify holds; modify role-group membership; classify SEV-1/SEV-2 (must escalate to L2 for classification).

**Auto-escalate to L2 if:**
- Any indication of possible data loss.
- Any indication of permission or RBAC defect.
- Any incident touching an active matter (regulatory, litigation, arbitration).
- Microsoft Severity C case unresolved within 2 business days.

### L2 — eDiscovery Operator (senior) + Purview Compliance Admin

**Scope.** SEV-2 incidents; hold creation and modification; search-completeness analysis; export job management; reviewer RBAC reviews.

**Authority.** Create and modify holds with case-team and counsel approval; modify search definitions; manage export jobs; open Microsoft Severity B cases.

**Cannot.** Approve external regulator notification; modify tenant-wide retention defaults; remove principals from `eDiscovery Administrator` (must coordinate with Records Officer / Compliance Manager).

**Auto-escalate to L3 if:**
- Confirmed data loss or strongly suspected spoliation.
- Active matter with deadline within 5 business days.
- Hold propagation stalled >24 hours after Microsoft case opened.
- Search completeness questioned by counsel or opposing counsel.
- Cross-tenant guest scoping gap on active matter.
- Microsoft Severity B case unresolved within 1 business day.

### L3 — eDiscovery Manager + Records Officer

**Scope.** SEV-1 incidents (operational); cross-matter pattern analysis; vendor coordination; counsel liaison.

**Authority.** Convene war room; engage outside counsel; approve compensating controls (§1.4) including org-wide retention policy at maximum scope; approve manual journaling; open Microsoft Severity A cases; engage Microsoft TAM.

**Cannot.** Approve external regulator notification (counsel + CCO); approve 8-K disclosure (Disclosure Committee); approve Microsoft Trust & Safety escalation (CISO + GC).

**Auto-escalate to L4 if:**
- Mass spoliation suspected (≥10 custodians).
- Production miss for SEC subpoena, DOJ request, or court order.
- NYDFS Part 500.17 or 8-K disclosure clock initiated.
- Microsoft Severity A case unresolved within 4 hours of opening.
- Any indication that incident may involve wilful misconduct by a custodian or insider threat.

### L4 — General Counsel + CISO + Chief Compliance Officer (named, joint)

**Scope.** External-disclosure decisions; outside-counsel engagement strategy; Microsoft Trust & Safety escalation; Disclosure Committee convene; board/audit-committee notification.

**Authority.** All firm-level decisions on disclosure, regulator engagement, public statement, and operational suspension of Copilot or eDiscovery features tenant-wide.

**Cannot delegate.** External-disclosure decisions and regulator-notification decisions cannot be delegated below L4.

**Standing escalation companions:**
- Microsoft Trust & Safety — for mass spoliation, suspected platform-side compromise, or any event with cross-tenant exposure.
- Outside e-discovery counsel — engaged for any SEV-1 within 4 hours.
- External auditor lead partner — for any incident touching financial reporting (SOX §404) or material weakness analysis.

### No-judgment-required escalation triggers (consolidated)

| Trigger | Auto-tier | Auto-paged |
|---|---|---|
| Confirmed `SubstrateHolds` purge for custodian under active hold | SEV-1 / L4 | GC, CCO, CISO within 1 hour |
| Mass spoliation ≥10 custodians | SEV-1 / L4 | GC, CCO, CISO + Microsoft Trust & Safety within 24 hours |
| Production deadline miss for FINRA Rule 8210 | SEV-1 / L3 minimum | GC, CCO + L4 notification |
| Production deadline miss for SEC subpoena, DOJ, or court order | SEV-1 / L4 | GC, CCO, CISO + outside counsel within 1 hour |
| Hash-chain mismatch persisting after re-download (suspected tampering) | SEV-1 / L4 | GC, CISO, CIRT within 1 hour |
| Cross-tenant guest custodian on active matter without home-tenant coordination | SEV-2 minimum / L3 | GC + Records Officer |
| NYDFS reportable cyber event | SEV-1 / L4 | GC, CISO + NYDFS within 72 hours of determination |
| 8-K Item 1.05 materiality determination | SEV-1 / L4 | Disclosure Committee + outside counsel + CFO |
| Reg S-P customer NPI in lost interactions | SEV-1 / L4 | GC, CPO + Reg S-P notification within 30 days |

---

## Section 6 — Microsoft Support Pack

When opening a Microsoft Support case for an eDiscovery-on-agents incident, providing the right artifacts up front shortens time-to-engagement materially. Use the package below.

### 6.1 What to include in the initial case

1. **Tenant ID** and **cloud** (commercial / GCC / GCC High / DoD / 21Vianet).
2. **Case impact statement** in three sentences: what failed, what is at stake, what regulatory deadline is in play.
3. **Severity request** with justification (Severity A reserved for SEV-1; Severity B for SEV-2).
4. **Reproduction steps** including the exact PowerShell command(s) and exact portal navigation path.
5. **Diagnostic outputs** from the relevant runbook in §2 (cmdlet results, distribution status, search definition).
6. **Service Health advisory IDs** if any are concurrent.
7. **Affected principals list** (UPNs) — for content cases, Microsoft cannot view the content but needs the principals to inspect platform-side metadata.
8. **Affected case ID(s)** and search/export job IDs.
9. **Time window** in UTC of the failure observation.
10. **Business impact statement** including the regulatory matter (without disclosing privileged content) and any deadline.
11. **Counsel approval** for content-side investigation if Microsoft engineers will need to inspect customer data (rare; usually Microsoft uses platform telemetry only).

### 6.2 What Microsoft Support **can** do

- Diagnose platform-side propagation, indexing, and storage issues.
- Convert a deleted mailbox to an inactive mailbox within the 30-day soft-delete window (subject to standard procedures and authorization).
- Investigate and remediate platform-side bugs in eDiscovery, Purview, Substrate, Copilot indexing.
- Provide engineering-level statements for inclusion in regulator responses (with appropriate scoping; will not characterize legal sufficiency).
- Escalate cross-cloud or cross-region issues to internal Microsoft engineering teams.
- Coordinate with Microsoft Trust & Safety on mass-spoliation or platform-compromise investigations.

### 6.3 What Microsoft Support **cannot** do

- **Make legal determinations.** Microsoft cannot opine on FRCP 37(e) sanctions exposure, FINRA Rule 8210 sufficiency, SEC 17a-4 compliance, or NYDFS reportability. These are firm-and-counsel decisions.
- **Restore content past published soft-delete windows.** A mailbox deleted >30 days ago is generally not recoverable; a mailbox item past `Recoverable Items` retention is generally not recoverable.
- **Bypass tenant-side configuration.** If the firm's hold or retention configuration permitted an outcome, Microsoft will not retroactively reconfigure to undo it.
- **Provide content evidence in lieu of eDiscovery.** Microsoft does not deliver customer mailbox content via Support tickets; the firm must use eDiscovery (Premium) export with the firm's own credentials.
- **Certify chain of custody.** The firm and its counsel certify chain of custody; Microsoft can attest to platform behavior but does not act as a forensic custodian for customer matters.
- **Accelerate beyond published SLAs** for free; Premier / Unified Support contracts have specific accelerated paths but even these do not change platform propagation physics.
- **Provide privileged or work-product protection** for incident communications. Treat Microsoft case content as discoverable; route privileged analysis through outside counsel.

### 6.4 Premier / Unified Support escalation paths

- **Designated Support Engineer (DSE)** — for tenants with Unified Support, request DSE engagement for matter-specific recurring issues.
- **Customer Success Account Manager (CSAM)** — owns relationship escalation; loops in TAM.
- **Cloud Solution Architect (CSA)** — for design-side remediation when the incident reveals an architectural defect.
- **Microsoft Trust & Safety** — for mass spoliation, suspected platform compromise, or insider-threat scenarios with platform implications.
- **Customer Lockbox** approver chain — required if Microsoft engineers need to access customer data for diagnosis; always approve via the named GC + CISO + CPO triad and log the approval.

---

## Section 7 — Cross-References

### 7.1 Related controls

| Control | Why it matters here |
|---|---|
| [`1.5 — DLP and Sensitivity Labels`](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) | Sensitivity labels propagate to Copilot-discovered content; label-based encryption affects how exported items render during review and feeds review-set filtering and redaction posture. |
| [`1.6 — DSPM for AI`](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md) | DSPM for AI surfaces sensitive-data interactions used to scope eDiscovery cases for Copilot agents and prioritize custodian inclusion. |
| [`1.7 — Comprehensive Audit Logging`](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) | The UAL `CopilotInteraction` records are evidence-floor item #2; this control governs ingestion, retention, and search of the audit log that complements eDiscovery content retrieval. |
| [`1.9 — Data Retention and Deletion Policies`](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md) | The org-wide retention floor that prevents AP-15; coordinate label-driven retention with eDiscovery hold posture to avoid premature purge of held content. |
| [`1.10 — Communication Compliance Monitoring`](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md) | Comm Compliance reviewer queues feed escalations into eDiscovery cases for supervisory action under FINRA Rule 3110. |
| [`1.14 — Data Minimization and Agent Scope`](../../../controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md) | Defines the agent ↔ grounding-surface inventory that determines eDiscovery scope per agent. |
| [`1.21 — Adversarial Input Logging`](../../../controls/pillar-1-security/1.21-adversarial-input-logging.md) | Comm Compliance + Defender XDR Copilot incident evidence is preserved under eDiscovery hold for SEC 17a-4(b)(4) production; this control's troubleshooting playbook is the gold-standard companion to this one. |
| [`1.22 — Information Barriers`](../../../controls/pillar-1-security/1.22-information-barriers.md) | Information Barriers may prevent reviewers from accessing content across business-unit boundaries; coordinate Compliance Boundary and IB scoping during reviewer assignment. |
| [`2.13 — Documentation and Record-Keeping`](../../../controls/pillar-2-management/2.13-documentation-and-record-keeping.md) | Record-keeping policy framework that eDiscovery operationalises; records-declared agent outputs follow a different retention pipeline than ordinary preservation. |
| [`4.6 — Grounding Scope Governance`](../../../controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md) | Grounding posture (RCD / RSS / DAG) determines what SharePoint content lands in scope of an eDiscovery hold for a Copilot agent. |
| [`4.7 — Microsoft 365 Copilot Data Governance`](../../../controls/pillar-4-sharepoint/4.7-microsoft-365-copilot-data-governance.md) | Tenant-wide Copilot data governance posture (retention, residency, citation behavior) shapes what eDiscovery can reach and how it must be scoped. |

### 7.2 Microsoft Learn anchors

- Microsoft Purview eDiscovery (overview): `https://learn.microsoft.com/purview/ediscovery`
- eDiscovery (Premium) — case management: `https://learn.microsoft.com/purview/ediscovery-create-case`
- eDiscovery holds — overview and behavior: `https://learn.microsoft.com/purview/ediscovery-create-hold`
- Microsoft 365 Copilot — eDiscovery & retention: `https://learn.microsoft.com/copilot/microsoft-365/microsoft-365-copilot-privacy`
- Search and preserve Copilot interactions: `https://learn.microsoft.com/purview/ediscovery-search-copilot-data` (verify current URL; topic title may change)
- Audit log `CopilotInteraction` record: `https://learn.microsoft.com/purview/audit-copilot`
- Inactive mailboxes and recovery: `https://learn.microsoft.com/exchange/security-and-compliance/inactive-mailboxes`
- Classic eDiscovery retirement notice (Aug 31, 2025): `https://learn.microsoft.com/purview/ediscovery-classic-retirement` (verify current URL)
- 21Vianet operated by 21Vianet — service availability: `https://learn.microsoft.com/microsoft-365/admin/services-in-china`
- PowerShell connection — Security & Compliance Center: `https://learn.microsoft.com/powershell/exchange/connect-to-scc-powershell`
- Sovereign cloud endpoint reference: `https://learn.microsoft.com/microsoft-365/enterprise/microsoft-365-endpoints`

### 7.3 Regulatory anchors

- **SEC Rule 17a-4(b)(4)** — 6-year retention (first 2 years readily accessible) for communications received and sent relating to the broker-dealer's business.
- **SEC Rule 17a-4(f)** — WORM / audit-trail-alternative requirement for electronic record storage; the audit-trail alternative requires a complete audit trail, time-date stamping, and ability to recreate the original.
- **Reg S-P §248.30** — 30-day customer notification for unauthorized access to or use of customer information.
- **FINRA Rule 4511** — Books and records retention and format.
- **FINRA RN 24-09 / Rule 3110** — Generative-AI supervision and communications recordkeeping expectations applied to AI-assisted output.
- **FINRA Rule 8210** — Provision of information and testimony to FINRA; production deadlines and the duty to respond completely.
- **FINRA Rule 4530** — Reporting requirements for member firms.
- **FINRA Rule 3110** — Supervision, including supervision of communications and the use of new technologies.
- **SOX §802** — Criminal penalties for altering, destroying, mutilating, concealing, or falsifying records with intent to obstruct.
- **FRCP 37(e)** — Failure to preserve electronically stored information; sanctions framework including adverse-inference instructions and case-dispositive sanctions for intent to deprive.
- **NYDFS Part 500.17** — Cybersecurity event notification within 72 hours of determination.
- **GLBA §501(b)** — Safeguards Rule; administrative, technical, and physical safeguards for customer information.

### 7.4 Companion repository — `FSI-AgentGov-Solutions`

Where applicable, this playbook references deployable artifacts in the companion solutions repository. Cite the specific solution directory and version in the matter file.

- `solutions/edisc-hold-bootstrap/` — parameterized PowerShell module to create matter case holds with reproducible naming and audit logging. (Verify current version in `docs/reference/solutions-index.md`.)
- `solutions/edisc-evidence-floor-collector/` — runbook automation that captures the 13 evidence-floor artifacts to a designated WORM landing zone. (Verify current version.)
- `solutions/copilot-preservation-validator/` — periodic synthetic test that issues a Copilot prompt, expects soft-delete, and confirms `SubstrateHolds` capture; reports drift to the eDiscovery Manager. (Verify current version.)
- `solutions/sovereign-edisc-endpoint-pack/` — PowerShell profile module that sets the correct Connection URI and Authorization endpoint for each sovereign cloud, eliminating hand-edited endpoint mistakes. (Verify current version.)

---

## Section 8 — Post-Incident Review (PIR) Template

A PIR is required for every SEV-1 within **10 business days** of incident closure, and for every SEV-2 within **20 business days**. The template below is the minimum scope; counsel may direct additional sections.

### 8.1 Cover sheet

- Incident ID
- Severity (initial / final)
- Detection date/time (UTC)
- Closure date/time (UTC)
- Total duration
- Affected matter(s) (case number / counsel of record)
- Affected custodians (count; UPN list redacted-as-needed)
- Affected sovereign cloud(s)
- PIR author + reviewers
- Counsel reviewer (named)
- Distribution (named recipients only)

### 8.2 Executive summary (1 page maximum)

Three paragraphs: **what happened**, **what was the impact**, **what changed as a result**. Written for an audience that includes the Audit Committee.

### 8.3 Timeline

Minute-by-minute for the first 4 hours; 15-minute granularity through the first 24 hours; daily thereafter. Each entry: timestamp (UTC), actor (named), action, source artifact (incident record line, case audit log, ticket).

### 8.4 Root cause analysis

Using **5 Whys** at minimum; **Ishikawa / fishbone** for incidents touching multiple subsystems. Distinguish:

- **Proximate cause** — the immediate technical or procedural failure.
- **Contributing causes** — preconditions that made the proximate cause possible.
- **Systemic causes** — organizational, training, or governance gaps.

### 8.5 Decisions log

Every decision made during the incident, in time order. Each row: time, decision, decider (named), rationale, alternatives considered, outcome.

### 8.6 Evidence floor reconciliation

Confirm each of the 13 evidence-floor artifacts (§1.3) was captured, where it is stored, retention applied, who has access. Flag any gap and counsel's disposition of the gap.

### 8.7 Reportability reconciliation

For each external trigger evaluated under §1.2 Q5: trigger, applicability determination, decision, decider, deadline, actual notification date. Include written counsel opinion for any negative determination ("not reportable, here's why").

### 8.8 Compensating controls invoked

Which §1.4 compensating controls were invoked, when activated, when stood down, residual exposure during use, who approved.

### 8.9 Communication audit

Cross-check §1.6 communication tree: was every named recipient actually notified within the SLA? Document misses and remediation.

### 8.10 Microsoft engagement

Case numbers, severity, time-to-engagement, Microsoft engineering disposition. Capture any platform commitments (e.g., engineering fix in flight) with target date and owner.

### 8.11 Permanent control changes

Tabulate every permanent change to controls, scripts, runbooks, role assignments, training, or vendor configuration that resulted from this incident. Each row: change, owner, target date, verification method, ledger entry in the change-management system.

### 8.12 Lessons learned

A short narrative section that will be circulated to the eDiscovery community of practice and embedded in onboarding training. Anonymized for any insider-attribution sensitivity per HR / counsel direction.

### 8.13 Standing PIR questions (16)

Every PIR must answer the following 16 questions in writing. "N/A" with a justification is acceptable; silence is not.

1. Was the incident detected by automation or by a human? If by a human, what automation should have detected it?
2. Was the initial classification correct? If not, why was the correct classification missed at triage?
3. Was every named SEV-1 / SEV-2 communication-tree recipient actually notified within the SLA?
4. Was the §1.3 evidence floor captured **before** any remediation that could overwrite forensic state? If not, what state was lost?
5. Did the hold propagation behave within the published "up to 24 hours" window? If exceeded, was Microsoft Severity B opened?
6. Did the search-completeness analysis include partially indexed items? Was the unindexed bucket reviewed and dispositioned?
7. Did the export package land on a configured WORM tier? Was the chain-of-custody form signed at every transfer?
8. Was the Q1–Q7 reportability tree walked at triage and again at war-room kickoff? Was every "YES" branch followed to completion?
9. Were any external-notification clocks (NYDFS 72h, 8-K 4 BD, Reg S-P 30d, FINRA 8210 deadline) triggered? If so, was the notification timely?
10. Did any AP (anti-pattern) from §3 appear in the incident handling? Which? What permanent control change addresses it?
11. Was outside counsel engaged within the §1.6 SLA? Was every privileged communication routed through counsel?
12. Was Microsoft Trust & Safety engaged when triggers were met? If not, document the judgment.
13. Were compensating controls (§1.4) stood down with documented approval after the primary control was restored?
14. Did any reviewer or eDiscovery principal hold elevated rights outside their PIM activation window during the incident?
15. Were Copilot Studio / Dataverse-side preservation surfaces evaluated, even if no Studio agent was in initial scope?
16. Does this incident reveal a pattern across recent SEV-1/SEV-2 incidents that warrants a horizontal control review?

### 8.14 Twelve-month trend watch

The eDiscovery Manager maintains a rolling 12-month log of incident classifications, root-cause categories, and compensating-control invocations. Each PIR contributes a row. Quarterly, the Manager presents the trend to the Compliance Committee. Triggers for a horizontal control review:

- **3 or more SEV-1 / SEV-2 incidents in any rolling 90-day window** with the same root-cause category.
- **2 or more incidents** invoking the same compensating control in any rolling 90-day window (suggests primary control is unstable).
- **Any incident** that meets a no-judgment-required external-disclosure trigger.
- **Any incident** that reveals a previously unknown sovereign-cloud behavior delta.

### 8.15 Annual effectiveness statement

Once per calendar year, the eDiscovery Manager + Records Officer + General Counsel jointly sign an Effectiveness Statement covering the prior 12 months. The statement addresses:

- Whether the eDiscovery-on-agents control set, as implemented and operated, **supports compliance with** SEC 17a-4, FINRA 4511 / 8210, NYDFS Part 500, FRCP 37(e), and the firm's own preservation policy.
- Whether the control set, as implemented and operated, has been observed to **fail in a manner that resulted in actual loss of evidence on an active matter** during the period.
- Material changes to scope, sovereign-cloud footprint, license posture, or vendor (Microsoft) capability during the period.
- A forward-looking risk register identifying the next 12 months' top three risks to eDiscovery-on-agents efficacy, with mitigation owners.

The Effectiveness Statement is provided to the Audit Committee and retained as a board-level record. It does **not** constitute a guarantee of compliance; it is a management attestation supported by the evidence in this control's audit trail.

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
