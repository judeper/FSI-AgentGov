# Control 1.7 — Troubleshooting: Comprehensive Audit Logging and Compliance

**Control:** 1.7 — Comprehensive Audit Logging and Compliance
**Pillar:** Pillar 1 — Security
**Last Verified:** 2026-10-16
**Verification basis:** Live Microsoft Learn documentation; no tenant UI, licensing assignment, or end-to-end capture was tested.
**Audience:** Purview Audit Admin, Purview Compliance Admin, Exchange Online Admin (Organization Configuration role), SOC Analyst, Entra Security Admin, Power Platform Admin, Azure Storage Account Owner, AI Governance Lead, FSI Compliance Officer, General Counsel
**Companion playbooks:**
[Portal walkthrough](./portal-walkthrough.md) ·
[PowerShell setup](./powershell-setup.md) ·
[Verification & testing](./verification-testing.md)

> **Scope.** This troubleshooting playbook covers operational, evidentiary, and regulatory failure modes for the [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) audit-logging surface — Microsoft 365 Audit (Standard / Premium / 10-Year add-on), the `CopilotInteraction` / `ConnectedAIAppInteraction` / `AIAppInteraction` / `PowerPlatformAdministratorActivity` record types, the PAYG opt-in for non-Microsoft AI events, Dataverse environment-level and per-table audit, Entra agent sign-ins and the separately configured Microsoft service-principal stream, supported PowerShell and Graph Audit Search, Sentinel connector-specific ingestion, and the downstream WORM / 17a-4(f) preservation tier.
>
> Every scenario is organized as **Symptom → Likely Cause → Diagnostic → Resolution → What good looks like**. Read [§1 FSI Incident Handling](#1-fsi-incident-handling-read-first) before remediating any production issue — for record-keeping controls the order of operations is *preserve evidence first, remediate second*.

> **Hedging note.** This playbook helps meet, and is recommended to support compliance with, the regulations cited below. It does not by itself satisfy any reporting or recordkeeping obligation. Implementation requires legal review and organizations should verify each obligation against current rule text and the firm's written supervisory procedures (WSPs) before relying on the timing or scope guidance here.

---

## Table of Contents

- [§1. FSI Incident Handling — Read First](#1-fsi-incident-handling-read-first)
- [§2. Capture vs Preservation vs Content — The Three Layers](#2-capture-vs-preservation-vs-content-the-three-layers)
- [§3. Critical FSI Failure Scenarios](#3-critical-fsi-failure-scenarios)
  - [Scenario 1 — Auditor wants prompt and response text; we only have audit metadata](#scenario-1-auditor-wants-prompt-and-response-text-we-only-have-audit-metadata)
  - [Scenario 2 — We assumed the 10-Year Audit Retention add-on satisfied SEC 17a-4(f)](#scenario-2-we-assumed-the-10-year-audit-retention-add-on-satisfied-sec-17a-4f)
  - [Scenario 3 — `AIAppInteraction` events missing](#scenario-3-aiappinteraction-events-missing)
  - [Scenario 4 — `ConnectedAIAppInteraction` sometimes free, sometimes billable](#scenario-4-connectedaiappinteraction-sometimes-free-sometimes-billable)
  - [Scenario 5 — Entra sign-in log doesn't show the "Is Agent" filter](#scenario-5-entra-sign-in-log-doesnt-show-the-is-agent-filter)
  - [Scenario 6 — `Search-UnifiedAuditLog` returns empty for `CopilotInteraction`](#scenario-6-search-unifiedauditlog-returns-empty-for-copilotinteraction)
  - [Scenario 7 — Audit search timeout / 5,000-row cap hit](#scenario-7-audit-search-timeout-5000-row-cap-hit)
  - [Scenario 8 — Sentinel not ingesting `CopilotInteraction`](#scenario-8-sentinel-not-ingesting-copilotinteraction)
  - [Scenario 9 — Per-table Dataverse audit not enabled on Copilot Studio entities](#scenario-9-per-table-dataverse-audit-not-enabled-on-copilot-studio-entities)
  - [Scenario 10 — Audit retention dropped from Premium to Standard mid-year](#scenario-10-audit-retention-dropped-from-premium-to-standard-mid-year)
  - [Scenario 11 — NYDFS 500.06 / 500.16 / 500.17 — single-artifact 12-month AI audit evidence](#scenario-11-nydfs-50006-50016-50017-single-artifact-12-month-ai-audit-evidence)
  - [Scenario 12 — Audit shows event but content is gone (mailbox deleted)](#scenario-12-audit-shows-event-but-content-is-gone-mailbox-deleted)
  - [Scenario 13 — FFIEC IT Examination wants tamper-evident audit](#scenario-13-ffiec-it-examination-wants-tamper-evident-audit)
- [§4. Anti-Patterns](#4-anti-patterns)
- [§5. Cross-References](#5-cross-references)

---

## 1. FSI Incident Handling — Read First

When an audit-logging issue is detected, the order of operations for an FSI tenant is:

1. **Triage severity** (§1.1)
2. **Determine reportability** (§1.2)
3. **Preserve evidence BEFORE remediation** (§1.3)
4. **Stand up compensating controls** (§1.4)
5. **Remediate**, then verify with the [Verification & Testing](verification-testing.md) suite

Skipping evidence preservation can convert a recoverable operational issue into a regulatory record-integrity finding.

### 1.1 Severity matrix

| Severity | Examples | Response window |
|---|---|---|
| **SEV-1 — record-keeping integrity at risk** | Audit ingestion silently disabled in production tenant; immutable storage policy unlocked or deleted; default retention silently applied to Copilot record types in Zone 3 (license shortfall); per-environment Dataverse audit off; preservation tier (immutable blob or 17a-4(f) archive) unavailable | Immediate (page on-call); preserve evidence within 1 hour |
| **SEV-2 — audit gap with bounded blast radius** | One Zone 2 environment Dataverse audit off; Sentinel connector down >24h; PAYG `AIAppInteraction` not enabled with non-Microsoft AI in use; `agentSignIn` forwarding to SIEM disabled in Zone 3 | Within business day |
| **SEV-3 — operational only** | `Search-UnifiedAuditLog` throttling; SIEM connector latency above empirical ceiling but within documented variance; transient `Get-AdminAuditLogConfig` connection failures | Routine queue |

### 1.2 Reportability decision tree

For SEV-1 and confirmed SEV-2, walk this tree before remediating. Do **not** rely on this list for legal advice — escalate to General Counsel / CCO immediately.

| Trigger | Likely reportable to | Notice clock |
|---|---|---|
| Confirmed loss of NPI audit trail | GLBA 501(b); state regulators per Reg S-P amendments (effective phased through 2026) | "As soon as practicable" — verify against current Reg S-P final rule |
| Cybersecurity incident affecting customer NPI in NY DFS-regulated entity | NY DFS Part 500.17(a) | **72 hours** from determination |
| Material cybersecurity incident at SEC registrant | SEC 8-K Item 1.05 (issuers); Form ADV-C (advisers) | "Material" thresholds — escalate to GC/CCO |
| FINRA member firm — significant event | FINRA Rule 4530 | Rule-defined window per event category |
| Broker-dealer record preservation failure | SEC 17a-4(f) third-party access undertaking implications | Escalate to CCO immediately |
| Bank model risk event (validation evidence loss) | OCC Bulletin 2026-13 (formerly OCC 2011-12) / Federal Reserve SR 26-2 (formerly SR 11-7) examiner notification | Per supervisory guidance |
| FCM / swap dealer / CPO record loss | CFTC 1.31 | Per CFTC guidance |

### 1.3 Evidence preservation BEFORE remediation

For every SEV-1 (and SEV-2 where reportability is plausible):

1. **Capture the failure state in place.** Run `Get-AdminAuditLogConfig | Format-List UnifiedAuditLogIngestionEnabled` from Exchange Online PowerShell, `Get-UnifiedAuditLogRetentionPolicy` from Security & Compliance PowerShell, and `Get-AzRmStorageContainerImmutabilityPolicy` for Azure storage, and save with SHA-256 sidecar **before** changing anything. The defective configuration is the evidence.
2. **Capture the operational artifacts** — Sentinel logs, error messages, transcript files. Hash on capture.
3. **Open a chain-of-custody record** — file, captured-by, captured-at-UTC, hash, hand-off log.
4. **Preserve any in-flight search jobs** — search jobs persist 30 days; export to immutable storage before they expire.
5. Only then proceed to remediation. The remediation step itself is also evidenced (transcript + post-state capture).

### 1.4 Compensating controls during the gap

If audit ingestion is impaired or a record type is uncovered:

- Tighten Zone 3 agent change windows; require dual-control approval for any agent activation
- Increase Communication Compliance ([Control 1.10](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md)) sampling on the affected agents
- Increase DSPM for AI ([Control 1.6](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md)) review cadence on the affected workspaces
- Notify the user community: "audit telemetry temporarily impaired — high-risk activity will be surveilled by alternate means until audit ingestion is verified"
- Document the gap window with start/end UTC for the audit binder

### 1.5 Pre-escalation checklist

Before paging a Microsoft Support escalation, verify:

1. Active session is Exchange Online PowerShell (not Security & Compliance PowerShell) — `(Get-ConnectionInformation).ConnectionUri`
2. RecordType used is in the live `AuditLogRecordType` enumeration
3. Search used `-SessionCommand ReturnLargeSet -SessionId` pagination, or migrated to the Graph audit search API
4. Date window is within retention horizon for that record type / user license
5. User account running the search holds `Audit Logs` or `View-Only Audit Logs`
6. Tenant audit ingestion is `True` (`(Get-AdminAuditLogConfig).UnifiedAuditLogIngestionEnabled` from Exchange Online)
7. Custom retention policy covers the record type, either explicitly or through an all-record-types policy (default policy excludes Copilot)
8. License entitlement gap report is empty for the user/event in question
9. PAYG enablement state captured if `AIAppInteraction` involved
10. Module versions captured and within the CAB-pinned range
11. End-to-end latency measured and outside empirical ceiling (not a fabricated SLA)

---

## 2. Capture vs Preservation vs Content — The Three Layers

Most of the failure modes documented below collapse to one of three layer confusions. Internalize this picture before triaging:

| Layer | What it is | Microsoft 365 product | What it cannot do alone |
|---|---|---|---|
| **Capture (Audit)** | Operational telemetry — *who did what, when, against which agent/resource* | Microsoft 365 Audit (Standard / Premium / 10-Year add-on) | Does **not** preserve verbatim prompt/response text; is **not** a SEC 17a-4(f) electronic recordkeeping system on its own |
| **Content (Substrate)** | The verbatim prompt and response text for Microsoft 365 Copilot interactions | Microsoft 365 Substrate (per-user Copilot interactions mailbox), surfaced via DSPM for AI ([Control 1.6](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md)), eDiscovery (Premium) ([Control 1.19](../../../controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md)), and Communication Compliance ([Control 1.10](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md)) | Does **not** by itself produce a regulator-ready chain-of-custody artifact |
| **Preservation (17a-4(f) tier)** | Long-horizon, regulator-attested books-and-records vault | Azure immutable blob storage (Cohasset-attested) **or** a third-party SEC 17a-4-attested archive (Smarsh, Global Relay, Proofpoint, Mimecast, Bloomberg Vault, Veritas EV.cloud) **or** the October 2022 audit-trail alternative (DEO/DTP undertaking + independent assessment) | Does **not** generate the activity timeline; consumes exports from the Capture and Content layers |

A complete FSI program for AI agent communications **chains all three**: Audit produces the activity record and the message-ID join keys → Substrate (via DSPM/eDiscovery/Comm Compliance) yields the verbatim content → the preservation tier locks both into a 17a-4(f)-attested vault. When an examiner says *"show me the prompt that produced this output and prove it has not been altered since June 2024"*, you are answering across all three layers, not one.

---

## 3. Critical FSI Failure Scenarios

### Scenario 1 — Auditor wants prompt and response text; we only have audit metadata

**Symptom.** Examiner (FINRA, SEC, OCC, or internal audit) requests the verbatim prompt and the verbatim response for a `CopilotInteraction` event surfaced from `Search-UnifiedAuditLog`. The compliance team exports the audit JSON, opens it, and finds `Messages[].ID`, `Messages[].IsPrompt`, `AgentId`, `ModelTransparencyDetails.ModelProviderName`, `JailbreakDetected`, `XPIADetected` — but no prompt or response body.

**Likely cause.** *Capture-vs-content layer confusion.* The team designed evidence collection assuming `Search-UnifiedAuditLog` would return the chat text. Per [Microsoft Learn — Audit logs for Copilot and AI applications](https://learn.microsoft.com/en-us/purview/audit-copilot), the `CopilotInteraction` audit record carries interaction **metadata and message IDs only**. Conversation copies are stored in hidden folders in the user's Exchange mailbox and are searchable with eDiscovery; supported DSPM for AI and Communication Compliance scenarios provide content review. These surfaces have separate permissions, collection, and licensing prerequisites; a metadata hit does not establish that content was captured or remains available.

**Diagnostic.**

```powershell
# 1. Confirm the audit record carries metadata only
$rec = Search-UnifiedAuditLog `
  -StartDate (Get-Date).AddDays(-7) -EndDate (Get-Date) `
  -RecordType CopilotInteraction -ResultSize 1 -SessionCommand ReturnLargeSet
if (-not $rec) { throw 'No audit record returned; content coverage is unverified.' }
$audit = $rec.AuditData | ConvertFrom-Json
if (-not $audit.CopilotEventData.Messages) {
  throw 'Expected CopilotEventData.Messages missing; inspect the returned schema.'
}
$audit | Select-Object AgentId, AgentName, `
  @{n='MessageIDs';e={$_.CopilotEventData.Messages.Id}}, `
  @{n='HasPromptText';e={[bool]($_.CopilotEventData.Messages | Where-Object { $_.PSObject.Properties.Name -contains 'Body' })}}

# Expected: message IDs populated; HasPromptText = False.
```

The [published raw audit schema](https://learn.microsoft.com/en-us/office/office-365-management-api/copilot-schema) nests `Messages`, `AccessedResources`, and `ModelTransparencyDetails` under `CopilotEventData`. Do not interpret a missing top-level field as proof that the underlying data is absent.

Confirm Substrate-tier retrieval is configured: DSPM for AI is enabled (Control 1.6), Copilot interactions are in scope of an eDiscovery (Premium) hold (Control 1.19), and Communication Compliance has a policy targeting AI-generated communications (Control 1.10).

**Resolution.**

1. Document the capture/content distinction in your Written Supervisory Procedures (WSPs) so this does not recur.
2. Retrieve the verbatim content via the Substrate path appropriate to the request:
   - **Investigation / supervisory review** → Communication Compliance ([Control 1.10](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md)) — open the policy match, read transcript in place.
   - **Regulator / litigation pull** → eDiscovery (Premium) ([Control 1.19](../../../controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md)) — place the user(s) on hold, build a search using the message IDs from the audit record as the join key, export the review set.
   - **Compliance manager spot-read** → DSPM for AI ([Control 1.6](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md)) — view chat transcript directly from the DSPM for AI experience.
3. Hand the auditor the **paired artifact**: audit record (timeline, who/what/when, message IDs) + content artifact (verbatim text exported via the chosen Substrate path). Both go into the evidence binder with SHA-256 sidecars.
4. If the request relates to a books-and-records record set, also export the content artifact to the firm's 17a-4(f) preservation tier (see Scenario 2).

**What good looks like.** WSP §"AI Agent Communications Recordkeeping" explicitly names (a) Audit as the activity tier, (b) Substrate via DSPM/eDiscovery/Comm Compliance as the content tier, and (c) the 17a-4(f) preservation tier. Compliance team can produce a paired artifact (metadata + verbatim text) for any `CopilotInteraction` event within the firm's documented response window.

---

### Scenario 2 — We assumed the 10-Year Audit Retention add-on satisfied SEC 17a-4(f)

**Symptom.** Mock examination or independent assessment finds that the firm's broker-dealer books-and-records preservation strategy for AI agent communications relies solely on the per-user **10-Year Audit Log Retention** add-on. No WORM-format vault, no Cohasset-attested storage, no DEO/DTP undertaking, no third-party 17a-4 archive. The firm's response to "show me your 17a-4(f) attestation" is to point at the audit retention SKU.

**Likely cause.** *Capture-vs-preservation conflation.* The 10-Year add-on extends Microsoft 365 Audit retention to ten years for covered record types, but Microsoft 365 Audit (Standard, Premium, and the 10-Year add-on inclusive) is **operational telemetry** — it is not a SEC 17a-4(f)-compliant electronic recordkeeping system on its own. The "Capture vs Preservation" warning at the top of the [Control 1.7 doc](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md#control-description) calls this out explicitly.

**Diagnostic.** Walk this checklist with Compliance and General Counsel:

- [ ] Does the firm have a **Cohasset-attested** WORM tier holding the books-and-records record set? (Azure immutable blob storage with a time-based retention policy in the **locked** state qualifies — Cohasset has attested it for SEC 17a-4(f), CFTC 1.31, and FINRA 4511.)
- [ ] Or, is the firm relying on the **October 2022 audit-trail alternative** (compliance date 3 May 2023)? If yes, are the DEO representation or DTP undertaking *and* the independent records-management assessment on file?
- [ ] Or, does the firm journal/capture the AI content tier into a **third-party SEC 17a-4-attested archive** (Smarsh Enterprise Archive, Global Relay Archive, Proofpoint Enterprise Archive, Mimecast Cloud Archive, Bloomberg Vault, Veritas Enterprise Vault.cloud)?
- [ ] Is the DTP undertaking, where applicable, on file with FINRA?

If all three boxes are unchecked, the firm has a **preservation gap**, regardless of how long the audit log is retained.

**Resolution.** Choose one of the three preservation paths and stand it up:

1. **Azure immutable blob storage path.** Create a storage account, container, and a time-based retention policy in the **locked** state. Periodically export Substrate content (Copilot interactions) plus the paired audit records to that container. The documented [`Get-AzRmStorageContainerImmutabilityPolicy`](https://learn.microsoft.com/en-us/powershell/module/az.storage/get-azrmstoragecontainerimmutabilitypolicy) cmdlet should report `State = Locked`. Validate export completeness separately from policy state.
2. **Third-party 17a-4-attested archive.** Configure journaling/capture from the M365 Substrate into the chosen vendor (Smarsh / Global Relay / Proofpoint / Mimecast / Bloomberg Vault / Veritas EV.cloud). The vendor maintains its own 17a-4(f) attestation; obtain and file the current attestation letter.
3. **Audit-trail alternative path.** Document that the system preserves original records and a complete time-stamped audit trail of all modifications and deletions; obtain a Designated Executive Officer (DEO) representation **or** a Designated Third Party (DTP) undertaking; commission and file the independent records-management assessment.

In all three cases, the 10-Year audit retention add-on remains useful as the **activity-trail layer**, but it is no longer being asked to play the preservation role.

**What good looks like.** Audit binder contains: (a) Cohasset attestation letter (or equivalent vendor attestation, or DEO/DTP undertaking + independent assessment), (b) evidence the preservation policy is **locked** (immutable storage policy in `Locked` state, or vendor attestation), (c) the export pipeline runbook from Substrate → preservation tier with SHA-256 manifests, and (d) a WSP section that explicitly disclaims reliance on the 10-Year audit add-on as the 17a-4(f) layer.

---

### Scenario 3 — `AIAppInteraction` events missing

**Symptom.** Compliance team is monitoring use of non-Microsoft AI assistants (ChatGPT, Claude, Gemini, etc.) via the unified audit log. `Search-UnifiedAuditLog -RecordType AIAppInteraction` returns zero rows, even though endpoint telemetry confirms users are interacting with these services from managed devices.

**Likely cause.** `AIAppInteraction` is a **PAYG-only** record type (per the [Control 1.7 control description](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md#control-description)) and requires explicit enablement, plus an upstream capture mechanism. Common gaps:

1. Audit pay-as-you-go (PAYG) billing is not opted-in for the tenant.
2. Network/browser DLP is not configured to capture non-Microsoft AI traffic — Edge for Business unmanaged-AI policy ([Control 1.5](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md)) is the upstream feeder for the `AIApp` workload.
3. Affected users lack the appropriate license (Audit Premium tier prerequisites).
4. Date window is older than the **180-day** retention horizon for PAYG-captured records.

**Diagnostic.**

```powershell
# 1. Confirm tenant audit ingestion
Connect-ExchangeOnline
(Get-AdminAuditLogConfig).UnifiedAuditLogIngestionEnabled  # must be True

# 2. Confirm PAYG association via the Microsoft Purview portal
#    Settings > Account details; verify the billed subscription and resource group.
#    (No first-party PowerShell cmdlet exposes this state at the time of writing —
#     screenshot the portal state and hash for the evidence binder.)

# 3. Confirm the AIApp DLP feeder
Get-DlpCompliancePolicy | Where-Object { $_.Workload -match 'AIApp|Endpoint|Browser' } |
  Select-Object Name, Enabled, Mode, Workload

# 4. Confirm the audit window does not exceed 180 days for PAYG records
$start = (Get-Date).AddDays(-30)
Search-UnifiedAuditLog -StartDate $start -EndDate (Get-Date) `
  -RecordType AIAppInteraction -ResultSize 10 -SessionCommand ReturnLargeSet
```

Verify the Azure subscription association at **Settings > Account details**, as documented in [Enable Microsoft Purview pay-as-you-go features](https://learn.microsoft.com/en-us/purview/purview-payg-subscription-based-enablement). Initial enablement requires Entra Global Admin and an active Azure subscription/resource group in the same tenant. Verify the applicable collection policy separately; do not assume a per-record-type toggle exists under Audit settings.

**Resolution.**

1. Enable PAYG for `AIAppInteraction` in the Microsoft Purview portal. Capture the change with a screenshot and hash it for the audit binder.
2. Configure or extend the Edge for Business unmanaged-AI policy and the network DLP rules per [Control 1.5](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) so non-Microsoft AI traffic is being captured upstream.
3. Validate license entitlements for the affected user population.
4. Re-run the audit search after the documented propagation window (allow up to 24 hours for first events to surface).
5. Add a recurring verification job (see [Verification & Testing](verification-testing.md)) that alerts on any 24-hour window of zero `AIAppInteraction` events when DLP telemetry confirms upstream activity.

**What good looks like.** PAYG opt-in screenshot on file; DLP/Edge-for-Business policy state evidenced; `Search-UnifiedAuditLog -RecordType AIAppInteraction` returns events within the empirical latency ceiling for the tenant; daily verification job is green; 180-day horizon documented in WSPs and longer retention sourced from the Substrate / preservation tier rather than from PAYG audit alone.

---

### Scenario 4 — `ConnectedAIAppInteraction` sometimes free, sometimes billable

**Symptom.** Finance / IT operations sees inconsistent billing line items for `ConnectedAIAppInteraction` events. Some workloads are included in Audit (Standard) at no incremental cost; others land on the PAYG meter. Admins are unable to predict the cost of enabling a new agent.

**Likely cause.** This is **expected behavior**, not a defect. Per [Microsoft Learn — Audit logs for Copilot and AI applications](https://learn.microsoft.com/en-us/purview/audit-copilot):

- Microsoft applications, including **custom applications built using Microsoft Copilot Studio and Microsoft Foundry**, are **included in Audit (Standard)**. A custom-built app is not automatically PAYG-billable.
- **Some** scenarios under the same `ConnectedAIAppInteraction` RecordType — specifically, interactions with **non-Microsoft AI apps** surfaced via Connected AI App — fall under **Audit pay-as-you-go (PAYG) billing** and require explicit PAYG opt-in.

The single RecordType name spans both regimes; establish the application's platform and collection scenario, not only its developer or record type.

**Diagnostic.** Build a per-app inventory and tag provenance:

```powershell
# Pull a 30-day sample and aggregate by ApplicationId / app name
$start = (Get-Date).AddDays(-30); $end = Get-Date
$rows = Search-UnifiedAuditLog -StartDate $start -EndDate $end `
  -RecordType ConnectedAIAppInteraction -ResultSize 5000 -SessionCommand ReturnLargeSet
$rows | ForEach-Object {
  $a = $_.AuditData | ConvertFrom-Json
  [pscustomobject]@{
    AppId    = $a.AppIdentity
    AppName  = $a.AgentName
    Provider = $a.CopilotEventData.ModelTransparencyDetails.ModelProviderName
  }
} | Group-Object AppId, AppName, Provider | Sort-Object Count -Descending |
  Select-Object Count, Name
```

Then, for each AppId, consult the live [Microsoft Purview billing models](https://learn.microsoft.com/en-us/purview/purview-billing-models) page for the current free-vs-PAYG split. **Do not hardcode the split into a runbook** — Microsoft has revised the boundary more than once and is expected to continue to do so.

**Resolution.**

1. Treat the Microsoft Learn billing page as the source of truth; link to it from the runbook rather than restating its contents.
2. Maintain an internal app register recording the platform, collection scenario, and applicable Audit Standard or PAYG treatment. Include custom Copilot Studio and Foundry apps in the documented Microsoft-application exclusion from PAYG.
3. Before enabling a new Connected AI App, verify its billing classification and update the register.
4. Reconcile finance billing exports against the register monthly; surface drift as a SEV-3.

**What good looks like.** App-provenance register exists and is reviewed monthly; finance billing matches expectations within tolerance; runbooks point to the live Microsoft Learn billing page rather than asserting a fixed split; new Connected AI App enablement passes through a billing-classification check.

---

### Scenario 5 — Entra sign-in log doesn't show the "Is Agent" filter

**Symptom.** Operator follows an older runbook that says "in Entra > Sign-in logs, apply the *Is Agent = Yes* filter chip." The filter is not present in the current UI. Operator cannot confirm whether agent sign-ins are being captured.

**Likely cause.** The operator may be using a different sign-in experience or lack access to the required logs. [Microsoft Entra Agent ID logs](https://learn.microsoft.com/en-us/entra/agent-id/sign-in-audit-logs-agents) explicitly documents **Is Agent = Yes** and **Agent type** filters at **Entra ID > Monitoring & health > Sign-in logs**. Agent sign-ins can appear across all four sign-in types; a separate Agent activity navigation entry is not the documented procedure on that page.

**Diagnostic.**

1. Sign in as at least Reports Reader. Open **Entra ID > Monitoring & health > Sign-in logs** and apply **Is Agent = Yes** or an appropriate **Agent type** value.
2. Inspect the relevant interactive, non-interactive, service-principal, and managed-identity sign-in views. Record the tenant's available filters and a known test sign-in.
3. To check forwarding, enumerate the configured diagnostic categories:

```powershell
# Confirm diagnostic settings for the tenant include sign-in log streams
Get-AzDiagnosticSetting -ResourceId "/providers/Microsoft.aadiam" |
  Select-Object Name, @{n='Logs';e={ $_.Log | Where-Object Enabled | Select-Object -ExpandProperty Category }}
# Look for SignInLogs, NonInteractiveUserSignInLogs, ServicePrincipalSignInLogs,
# ManagedIdentitySignInLogs, MicrosoftServicePrincipalSignInLogs.
# agentSignIn is an event type, not a documented diagnostic-setting category.
```

**Resolution.**

1. Document the **live** filter affordance names from your tenant in the runbook — verbatim, dated, with a screenshot in the audit binder.
2. If the documented filters are absent, capture the tenant discrepancy and investigate access and availability rather than declaring that Microsoft removed the filters.
3. For API verification, use the documented **beta** `/auditLogs/signIns` query, not an invented `/agentSignIn` endpoint:

   ```http
   GET https://graph.microsoft.com/beta/auditLogs/signIns?$filter=signInEventTypes/any(t: t eq 'servicePrincipal') and agent/agentType eq 'AgentIdentity'
   ```

   Forward the relevant supported sign-in diagnostic categories and verify agent fields in the destination. Do not create a diagnostic setting named `agentSignIn` without a published category.
4. Cross-reference [Control 1.7 §"Agent Sign-In and Activity Audit Logs"](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md#agent-sign-in-and-activity-audit-logs-preview) for the canonical preview-feature scope.

**What good looks like.** Runbook records the documented filters, actual tenant availability, a known agent sign-in, and the forwarding categories/destination. UI or beta Graph evidence demonstrates agent activity; a configured diagnostic setting alone is not proof of capture.

---

### Scenario 6 — `Search-UnifiedAuditLog` returns empty for `CopilotInteraction`

**Symptom.** `Search-UnifiedAuditLog -RecordType CopilotInteraction -StartDate (Get-Date).AddDays(-7) -EndDate (Get-Date)` returns zero rows in a tenant with active Copilot users.

**Likely cause.** Multiple non-exclusive causes, ordered by frequency:

1. **Unified audit ingestion not enabled** — `(Get-AdminAuditLogConfig).UnifiedAuditLogIngestionEnabled` is `False`.
2. **Entitlement or collection gap** — verify the specific Copilot product and Audit entitlement. Do not assume every `CopilotInteraction` producer requires the paid Microsoft 365 Copilot add-on.
3. **Data-availability latency** — Copilot record types can take longer than core workloads to surface (empirical typical latency is 60–90 minutes for core; Copilot, Power Platform, and Dataverse can take longer; allow up to 24 hours for first events).
4. **Time zone confusion** — `-StartDate`/`-EndDate` parameters are interpreted as UTC; a "yesterday" expressed in a non-UTC zone may bracket an empty window.
5. **Permission scope mismatch** — service principal (app-only) connections do not always carry the same audit-search rights as a delegated user with the `Audit Logs` role.
6. **Audit Premium retention boundary** — under the default Audit Premium retention policy, Copilot record types are **not covered**; retention falls back to 180 days, and queries beyond that window return empty.
7. **Session is Security & Compliance PowerShell**, not Exchange Online — `Get-AdminAuditLogConfig` from S&C PowerShell always returns `False` for `UnifiedAuditLogIngestionEnabled` regardless of true tenant state.

**Diagnostic.**

```powershell
# 1. Confirm session is EXO, not S&C PowerShell
(Get-ConnectionInformation).ConnectionUri  # should be the EXO endpoint

# 2. Confirm tenant ingestion
Connect-ExchangeOnline
(Get-AdminAuditLogConfig).UnifiedAuditLogIngestionEnabled

# 3. Inspect effective audit-search role assignments for the operator.
# Audit Logs is a role, not necessarily a role-group name.
Get-ManagementRoleAssignment -RoleAssignee 'audit.admin@contoso.com' -GetEffectiveUsers |
  Where-Object { $_.Role -in @('Audit Logs','View-Only Audit Logs') }

# 4. Confirm at least one user has a Copilot license
Get-MgUserLicenseDetail -UserId user@contoso.com |
  Where-Object { $_.SkuPartNumber -match 'Copilot' }

# 5. Inspect the installed cmdlet's accepted RecordType values.
Get-Help Search-UnifiedAuditLog -Parameter RecordType

# 6. Re-issue the search with explicit UTC and pagination
$start = [DateTime]::UtcNow.AddDays(-7)
$end   = [DateTime]::UtcNow
Search-UnifiedAuditLog -StartDate $start -EndDate $end `
  -RecordType CopilotInteraction `
  -SessionCommand ReturnLargeSet -SessionId "diag-$(Get-Random)" -ResultSize 5000

# 7. Inspect candidate retention policies, including all-record-types policies
Get-UnifiedAuditLogRetentionPolicy |
  Sort-Object Priority |
  Select-Object Name, Priority, RecordTypes, RetentionDuration
```

**Resolution.**

1. Reconnect to Exchange Online if the session was S&C PowerShell.
2. Enable unified audit ingestion if needed; allow up to 60 minutes for configuration propagation and longer for ingestion to begin.
3. Reconcile licenses and re-run after the propagation window.
4. Re-issue the query with explicit UTC and paginated `ReturnLargeSet` semantics.
5. If the date window exceeds 180 days, confirm a custom retention policy covers `CopilotInteraction` and the user has Audit Premium. The 10-Year Audit Log Retention add-on is needed for durations **beyond one year**, including the 3-, 5-, and 7-year options, not for a one-year policy. See [audit retention policies](https://learn.microsoft.com/en-us/purview/audit-log-retention-policies).
6. If the search will be repeated programmatically, migrate to the Graph audit search API (see Scenario 7).

**What good looks like.** A known controlled `CopilotInteraction` is returned within the tenant's measured latency window; `(Get-AdminAuditLogConfig).UnifiedAuditLogIngestionEnabled` is True from Exchange Online; the operator role and license entitlements are evidenced. Applicable retention coverage is confirmed by user/operation scope, priority, and record types (explicit or all types), not merely policy-name presence.

---

### Scenario 7 — Audit search timeout / 5,000-row cap hit

**Symptom.** `Search-UnifiedAuditLog` either times out, throws `TooManyRequests` (HTTP 429), or returns at most 5,000 rows per call (or stops at the 50,000 session ceiling) when the operator knows the underlying event volume is much higher.

**Likely cause.** The [supported cmdlet](https://learn.microsoft.com/en-us/powershell/module/exchangepowershell/search-unifiedauditlog) has documented per-call and per-session caps. Microsoft recommends the Office 365 Management Activity API for programmatic downloads; the Graph Audit Search API is also available at `v1.0`. Do not infer a maintenance-only or deprecated status for `Search-UnifiedAuditLog` from the retirement of a different cmdlet.

**Resolution.**

1. **Use a supported programmatic extraction path.** For Graph, [create an auditLogQuery](https://learn.microsoft.com/en-us/graph/api/security-auditcoreroot-post-auditlogqueries?view=graph-rest-1.0), poll for a terminal status, reject failed/cancelled jobs, then page `/queries/{id}/records` using `@odata.nextLink`. Consent the applicable query permissions (for this cross-workload example, `AuditLogsQuery.Read.All`), not Entra's `AuditLog.Read.All` alone.

   A `succeeded` query can still be truncated. Inspect `isRecordCountLimitExceeded` before accepting completeness; if true, split the window and re-run. If completeness metadata is absent, reconcile counts and document the uncertainty. Honor `Retry-After` on HTTP 429. See [query properties](https://learn.microsoft.com/en-us/graph/api/resources/security-auditlogquery?view=graph-rest-1.0) and [service limits](https://learn.microsoft.com/en-us/graph/throttling-limits#security-audit-log-query-service-limits).

   ```powershell
   # Sketch — Graph audit log queries
   $body = @{
     '@odata.type'        = '#microsoft.graph.security.auditLogQuery'
     displayName          = 'CopilotInteraction-Q1-2026'
     filterStartDateTime  = '2026-01-01T00:00:00Z'
     filterEndDateTime    = '2026-03-31T23:59:59Z'
     operationFilters     = @('CopilotInteraction')
   } | ConvertTo-Json
   $q = Invoke-MgGraphRequest -Method POST `
     -Uri 'https://graph.microsoft.com/v1.0/security/auditLog/queries' -Body $body
   # Poll $q.id to terminal status; reject failed/cancelled or truncated results.
   # Follow every @odata.nextLink; split/retry any count-limited window.
   ```

2. **Use server-side filtering.** Push `RecordType`, `UserIds`, `Operations`, and time windows into the API call rather than filtering client-side after a wide pull.
3. **Chunk by `RecordType` × time window.** A 90-day pull across all Copilot record types is more reliable as 90 daily windows × N record types, executed serially with a small delay, than as a single wide call.
4. **Serialize, do not parallelize.** Aggressive parallel pagination across multiple sessions trips the per-tenant rate limit.
5. For ad-hoc UI use, use **Audit > Search** in the Microsoft Purview portal. Its documented maximum search window is 180 days; export supports up to 50,000 rows for Audit Standard and 1,000,000 for Audit Premium. These are not the PowerShell session limits.

**What good looks like.** Scheduled extraction uses an approved supported API with bounded windows, explicit completeness evidence, pagination, and monitored throttling/retry behavior. `Search-UnifiedAuditLog` remains supported; its documented session cap is not proof of deprecation.

---

### Scenario 8 — Sentinel not ingesting `CopilotInteraction`

**Symptom.** Purview has a known Copilot audit event, but a Sentinel query against `OfficeActivity` returns no matching interaction.

**Likely cause.** Common gaps:

1. Wrong connector or table. The [Microsoft Copilot connector](https://learn.microsoft.com/en-us/azure/sentinel/data-connectors-reference#microsoft-copilot) uses the Office Management API and writes to [`CopilotActivity`](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/copilotactivity). The Microsoft 365 connector's `OfficeActivity` table is not a universal destination for every Purview record type.
2. Tenant license tier does not surface the record type to the connector.
3. Sentinel workspace tier or daily-cap settings are dropping events.
4. Analytics rule conditions prevent alerts after ingestion. A rule filter does not remove source rows from the destination table.
5. Connector polling latency is within Microsoft's empirical envelope but exceeds the operator's expectation.

**Diagnostic.**

1. In Sentinel **Data connectors**, inspect **Microsoft Copilot** and its configured workspace. Separately inspect Microsoft 365, Dataverse, and any custom connectors used for the other record types.
2. KQL — confirm Copilot ingestion:

   ```kusto
   CopilotActivity
   | where TimeGenerated > ago(24h)
   | summarize Count=count() by RecordType, bin(TimeGenerated, 1h)
   | order by TimeGenerated desc
   ```

3. KQL — confirm Copilot record types specifically:

   ```kusto
   CopilotActivity
   | where RecordType in ("CopilotInteraction","ConnectedAIAppInteraction",
                          "AIAppInteraction","PowerPlatformAdministratorActivity")
   | summarize Count=count() by RecordType, bin(TimeGenerated, 1h)
   ```

4. Confirm the workspace daily cap is not being hit (workspace settings > Usage and estimated costs).
5. Confirm the analytics rule scope and `where` clauses are not pre-filtering events away.

**Resolution.**

1. Enable or repair the Microsoft Copilot connector for its documented scope. Inventory the actual destination/schema for each other record type; a connector that covers Microsoft 365 and Security Copilot is not proof that all connected/third-party AI or Power Platform admin events flow through it.
2. Validate license entitlement and PAYG opt-in (Scenario 3) for the affected record types.
3. Raise the workspace daily cap if events are being dropped; this is a tenant-cost decision that should go through CAB.
4. Refer to [Control 3.9 — Microsoft Sentinel Integration](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md) for the canonical Sentinel ingestion architecture for AI audit events.
5. Document the empirical end-to-end latency (audit emit → Sentinel destination table) for the tenant and alert on deviations from that measured ceiling, not on a fabricated SLA.

**What good looks like.** A known audit record is correlated by ID into `CopilotActivity`; each other in-scope record type has its own tested connector/table mapping or an explicitly recorded coverage gap. Analytics rules fire on test events, and the ingestion budget and empirical latency are documented.

---

### Scenario 9 — Per-table Dataverse audit not enabled on Copilot Studio entities

**Symptom.** Dataverse auditing is enabled, but the expected table-change record or Copilot Studio authoring audit event cannot be found.

**Likely cause.** Two audit pipelines have been conflated. [Dataverse auditing](https://learn.microsoft.com/en-us/power-platform/admin/manage-dataverse-auditing) requires environment, table, and relevant column settings for data-change history. [Copilot Studio administrative activity collection](https://learn.microsoft.com/en-us/microsoft-copilot-studio/admin-logging-copilot-studio) is enabled by default on all tenants; it is not unlocked by a mandatory six-table Dataverse switch. Search authoring operations such as `BotCreate` and `BotUpdateOperation-BotPublish` under `PowerPlatformAdministratorActivity`, not interaction records under `ConnectedAIAppInteraction`.

**Diagnostic.**

```powershell
# Using Microsoft.PowerApps.Administration.PowerShell + Dataverse Web API
$envUrl = 'https://contoso.crm.dynamics.com'
# Framework-selected starting set, not a Microsoft-mandated authoring-audit prerequisite.
# Confirm installed tables, audit support, and required columns per environment.
$tables = @('bot','botcomponent','botcomponentcollection',
            'conversationtranscript','aiplugin','aipluginauth')

foreach ($t in $tables) {
  $meta = Invoke-RestMethod -Uri "$envUrl/api/data/v9.2/EntityDefinitions(LogicalName='$t')?`$select=LogicalName,IsAuditEnabled" `
    -Headers @{ Authorization = "Bearer $token" }
  [pscustomobject]@{ Table = $t; AuditEnabled = $meta.IsAuditEnabled.Value }
}
# Expected: each in-scope supported table has AuditEnabled = True.
```

**Resolution.**

1. **Portal path.** Power Apps Maker portal > select the environment > Tables > select the table (e.g., `bot`) > Properties > **Advanced options** > under "Rows in this table" check **Audit changes to its data** > Save. Repeat for the approved, supported table scope and verify column-level auditing. Record unsupported or absent tables explicitly.
2. **PowerShell / Web API path.** Patch each `EntityDefinition`:

   ```powershell
   foreach ($t in $tables) {
     $body = @{ IsAuditEnabled = @{ Value = $true } } | ConvertTo-Json
     Invoke-RestMethod -Method PATCH `
       -Uri "$envUrl/api/data/v9.2/EntityDefinitions(LogicalName='$t')" `
       -Headers @{ Authorization = "Bearer $token"; 'Content-Type' = 'application/json' } `
       -Body $body
   }
   ```

3. Test the two pipelines separately: change an audited Dataverse column and retrieve its data-change history; publish a sandbox agent and search `PowerPlatformAdministratorActivity` for `BotUpdateOperation-BotPublish`. Neither result substitutes for the other.
4. The [May 2026 Dataverse change](https://learn.microsoft.com/en-us/power-platform/important-changes-coming#removal-of-before-and-after-field-change-values-in-audit-events-sent-to-microsoft-purview) removes before/after values from events sent to Purview, not from Dataverse audit history. Retrieve details using [`audits(<id>)/Microsoft.Dynamics.CRM.RetrieveAuditDetails`](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/auditing/retrieve-audit-data#retrieve-audit-change-history), or evaluate the separately configured Synapse Link audit export.

**What good looks like.** The approved Dataverse table/column inventory is audited where supported; authoring operations are independently visible in Purview; a field-level change can be retrieved from Dataverse despite its omission from the Purview export.

---

### Scenario 10 — Audit retention dropped from Premium to Standard mid-year

**Symptom.** Quarterly evidence review discovers that a subset of users had their audit retention silently downgraded from Premium (one year, or up to ten years with the add-on) to Standard (180 days) at some point during the year. Events emitted before the downgrade are still within the Premium horizon, but the system can no longer guarantee Premium-tier coverage going forward, and there is a possible **gap** between the downgrade date and the discovery date.

**Likely cause.** Audit retention is a **per-user license attribute** evaluated at event-ingestion time. A license SKU change — Premium → Standard, or removal of the 10-Year add-on — silently re-tiers retention for that user from that point forward. Common triggers: cost-optimization sweep; reorg moving users to a different department's license pool; license SKU expiration without renewal; M&A integration license harmonization.

**Resolution.**

1. **Never downgrade audit licenses for users in scope of regulated workloads** (broker-dealer associated persons, FCM swap-dealer-registered persons, OCC-supervised model owners, NY DFS Covered Entities). Add a hard constraint to the license-management workflow that prohibits the downgrade for users in regulated populations, with an exception path that requires Compliance and CCO sign-off.
2. **If a downgrade has already occurred:**
   - Identify the affected user population and the downgrade date(s) precisely (from license-change audit log).
   - Reconstruct the missing-coverage period from alternative sources: the Substrate (still holds Copilot interactions per its own retention), DSPM for AI, eDiscovery, Communication Compliance, the Sentinel workspace (if Copilot events were ingested), and the 17a-4(f) preservation tier (if exports were running).
   - Document the gap window precisely (start UTC, end UTC, affected users, affected record types) in the audit binder.
   - Document the reconstruction methodology and the residual gap (the part you could not reconstruct).
   - Re-license the affected users back to Premium / 10-Year add-on; verify with `Get-MgUserLicenseDetail`.
3. **Assess regulatory disclosure obligation.** Walk the [§1.2 reportability tree](#12-reportability-decision-tree) with General Counsel and CCO. For broker-dealers, books-and-records preservation gaps may have notification implications under SEC 17a-4(f) DTP undertakings. For NY DFS Covered Entities, NYDFS Part 500 may apply if NPI was implicated.
4. **Update WSPs** to require dual-control on any license SKU change for users in regulated populations.

**What good looks like.** Regulated-population license guard is in place and tested; license-change audit alerts on any downgrade for users in scope; if a historical downgrade is found, the gap is reconstructed as far as the alternative sources allow, the residual is documented, and the WSPs prohibit recurrence.

---

### Scenario 11 — NYDFS 500.06 / 500.16 / 500.17 — single-artifact 12-month AI audit evidence

**Symptom.** NY DFS examiner under Part 500 (specifically 23 NYCRR 500.06 audit trail, 500.16 incident response, and 500.17 notice of cybersecurity event) requests a **single artifact** showing all AI-related audit events for the past 12 months, joined across record types, with the preservation-tier export evidence demonstrating the artifact is anchored to the 17a-4(f) vault.

**Likely cause.** Not a defect — a normal NYDFS examiner request. Most firms have not pre-built the joined query and scramble to assemble it under a regulator clock.

**Resolution.** Pre-build the artifact as a **named saved query** so it can be re-run on demand. The following paths have different coverage and must be reconciled, not assumed equivalent:

**Path A — Microsoft Graph audit search API**, scheduled monthly, output to immutable blob:

```powershell
# Sketch: run bounded UTC windows across the required 12-month period.
# Query all record types, then select the four required types from auditData.
# A retained 12-month history must already exist; this cannot recover expired data.
$body = @{
  '@odata.type'       = '#microsoft.graph.security.auditLogQuery'
  displayName         = "NYDFS-500-AI-Audit-$(Get-Date -Format 'yyyyMMdd')"
  filterStartDateTime = [DateTime]::UtcNow.AddDays(-30).ToString('o')
  filterEndDateTime   = [DateTime]::UtcNow.ToString('o')
} | ConvertTo-Json
$q = Invoke-MgGraphRequest -Method POST `
  -Uri 'https://graph.microsoft.com/v1.0/security/auditLog/queries' -Body $body
# Poll $q.id; reject failed/cancelled or isRecordCountLimitExceeded results.
# Page every @odata.nextLink, reconcile each required type, write NDJSON,
# SHA-256 hash, push to Cohasset-attested immutable blob container.
```

**Path B — Sentinel workbook** (preferred when Sentinel is the SIEM of record):

```kusto
// Copilot metadata slice, not a complete cross-source AI audit export
let lookback = 365d;
CopilotActivity
| where TimeGenerated > ago(lookback)
| where RecordType == "CopilotInteraction"
| extend EventDate = bin(TimeGenerated, 1d)
| summarize EventCount = count(),
            DistinctUsers = dcount(ActorUserId),
            DistinctAgents = dcount(AgentId)
            by RecordType, EventDate
| order by EventDate asc, RecordType asc
```

The workbook is a daily aggregate, not a row-level export of all events. Add the independently verified destinations for connected/third-party AI and Power Platform admin activity, and preserve row-level query results separately. Pin the workbook, schedule the monthly export, and persist exports to the 17a-4(f) preservation tier with SHA-256 sidecars. The deliverable handed to the examiner is **three artifacts together**: the joined query result, the chain-of-custody manifest, and the preservation-tier confirmation (immutable-blob policy state, or vendor archive attestation).

**What good looks like.** Saved query / workbook exists, has been run monthly for at least 12 months with outputs in the preservation tier, and can be produced for the examiner within the firm's documented response window. WSPs name the artifact and the responsible role.

---

### Scenario 12 — Audit shows event but content is gone (mailbox deleted)

**Symptom.** `Search-UnifiedAuditLog -RecordType CopilotInteraction` shows events for a former employee, but eDiscovery / DSPM for AI / Communication Compliance retrieval comes back empty for the verbatim prompt and response. Investigation shows the user's mailbox was deleted as part of the leaver process, and the Substrate Copilot interactions mailbox was deleted with it.

**Likely cause.** No legal hold or records-management retention policy was in place on the affected user's Copilot interactions mailbox, and the standard leaver workflow purged it. The audit log (operational telemetry) survived because it is tenant-scoped, but the content store (per-user Substrate mailbox) did not.

**Resolution.**

1. **Enable Records Management retention** ([Control 1.9 — Data Retention and Deletion Policies](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md)) covering the Copilot interactions location, with a retention duration aligned to the applicable regulatory horizon (3 years for SEC 17a-4(b)(4) communications; 5 years for CFTC 1.31; longer per firm policy).
2. **Apply In-Place Hold / Litigation Hold** to mailboxes of users in scope of regulatory recordkeeping at the moment of separation, **before** the leaver workflow runs the mailbox-delete step. Make this a hard gate in the leaver runbook.
3. **Sequence the leaver workflow** so retention/hold is verified present before any delete or disable action.
4. For the immediate incident, do not assume deletion means permanent loss. [Copilot retention documentation](https://learn.microsoft.com/en-us/purview/retention-policies-copilot#when-a-user-leaves-the-organization) states that retained messages remain searchable in an inactive mailbox when retention was applied before deletion. Have the Exchange/eDiscovery team assess inactive-mailbox and soft-deleted-mailbox recovery before concluding content is unavailable. If permanently deleted and not preserved elsewhere, reconstruct what is available from the preservation tier (if exports were running), document the residual gap, and walk the [§1.2 reportability tree](#12-reportability-decision-tree) with General Counsel.

**What good looks like.** Retention policy covering Copilot interactions is in place and verified for all in-scope users; leaver runbook gates mailbox-delete on hold-present check; periodic verification job confirms holds are intact for the regulated population; no `CopilotInteraction` audit row exists for which the content store cannot be retrieved.

---

### Scenario 13 — FFIEC IT Examination wants tamper-evident audit

**Symptom.** FFIEC IT Examination Handbook–driven examiner asks the firm to demonstrate that the AI audit trail is **tamper-evident** — that is, that no insider (including the highest-privileged tenant admin) can alter or delete historical audit records without detection.

**Likely cause.** Not a defect — a normal control attestation question. The firm needs to articulate the layered tamper-evidence model.

**Resolution.** Walk the examiner through the layered tamper-evidence story:

1. **Service-layer evidence (Microsoft 365 Audit).** Document supported search/export surfaces, retention, and administrative configuration from the [Audit overview](https://learn.microsoft.com/en-us/purview/audit-solutions-overview). Do not infer cryptographic integrity or immutable-archive attestation merely from read/search access to historical records; validate preservation and access separation independently.
2. **Disablement-detection layer.** While history cannot be edited, audit ingestion *itself* can in principle be disabled by a tenant admin. Mitigate with an alerting rule that fires if `UnifiedAuditLogIngestionEnabled` flips to `False` (this is itself an auditable configuration change). Wire the alert into the SOC pager.
3. **Cryptographic / WORM evidence layer.** For regulator-requested cryptographic evidence, supplement with: (a) verified Sentinel ingestion ([Control 3.9](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md)) — a separate copy only after successful delivery, with independent access/retention controls rather than an assumption that suppression requires collusion; (b) immutable-blob export with a **locked** time-based retention policy (Cohasset-attested for SEC 17a-4(f), CFTC 1.31, FINRA 4511); (c) WORM seal on the export with SHA-256 manifests anchored to a separate identity boundary (different subscription, different RBAC, different break-glass).
4. **Independent validation layer.** Periodic independent control testing per [Control 3.4 — Audit and Compliance Reporting](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md), and (for broker-dealers) the independent records-management assessment under the SEC 17a-4(f) audit-trail alternative.

```powershell
# Verify the Azure immutable blob policy is locked
Get-AzRmStorageContainerImmutabilityPolicy `
  -ResourceGroupName 'rg-fsi-audit-vault' `
  -StorageAccountName 'fsiauditvault' -ContainerName 'm365-audit-export' |
  Select-Object State, ImmutabilityPeriodSinceCreationInDays
# Expected: State = Locked
```

**What good looks like.** The firm can present a **four-layer tamper-evidence narrative** (service, disablement-detection, WORM/Sentinel, independent assessment); the immutable storage policy is in `Locked` state with hash sidecars; the disablement-detection alert exists and has been tested; control testing per Control 3.4 is current.

---

## 4. Anti-Patterns

| Anti-pattern | Why it's harmful |
|---|---|
| Equating "10-Year Audit Retention" with SEC 17a-4(f) compliance | Capture is not preservation. The add-on extends operational telemetry retention; it does not constitute a 17a-4(f) electronic recordkeeping system. (Scenario 2.) |
| Asking the audit log alone for prompt and response text | The `CopilotInteraction` record holds metadata and message IDs only. Verbatim text lives in the Substrate, retrieved via DSPM for AI / eDiscovery / Communication Compliance. (Scenario 1.) |
| Declaring the "Is Agent = Yes" filter unsupported | Microsoft documents Is Agent and Agent type at Entra ID > Monitoring & health > Sign-in logs. Record tenant discrepancies rather than inventing a replacement path. (Scenario 5.) |
| Hardcoding the free-vs-PAYG split for `ConnectedAIAppInteraction` | Microsoft has revised the boundary more than once. Link to the live Microsoft Learn billing page; do not restate the split in a static runbook. (Scenario 4.) |
| `-ErrorAction SilentlyContinue` in audit verification scripts | Hides exactly the failures you're verifying. Always `Stop` or `Continue` with logging. |
| Assuming the default Audit Premium retention policy covers Copilot record types | The one-year default covers only the four named workloads. Verify applicable custom policy coverage, including all-record-types policies, user/operation scope, priority, and licensing. (Scenario 6.) |
| Reading `Get-AdminAuditLogConfig` from Security & Compliance PowerShell | Always returns `False` for `UnifiedAuditLogIngestionEnabled` regardless of true tenant state. Use Exchange Online PowerShell. (Scenario 6.) |
| Single-shot `Search-UnifiedAuditLog -ResultSize 5000` for high-volume pulls | Caps at 5,000 per call and 50,000 per session. Migrate to the Graph audit search API. (Scenario 7.) |
| Treating a successful Graph query as proof of completeness | A query may succeed after reaching its record-count limit. Inspect `isRecordCountLimitExceeded`, split capped windows, and exhaust pagination. (Scenario 7.) |
| Citing fabricated "15-minute SIEM SLA" or "24-hour audit SLA" | Microsoft does not publish a hard SLA. Examiners will challenge specific numerical claims. Document the empirical ceiling instead. (Scenario 8.) |
| Downgrading audit licenses on users in regulated populations to optimize cost | Silent retention re-tiering creates evidence gaps and possible disclosure obligations. Hard-gate the downgrade. (Scenario 10.) |
| Running the leaver workflow before applying retention/hold to the user's Copilot mailbox | Audit row survives, content does not — a worst-case examiner scenario. Sequence hold-before-delete. (Scenario 12.) |
| Treating `agentSignIn` as a separate diagnostic category | It is an event type; verify supported sign-in streams and beta Graph agent filters against Microsoft Learn and the tenant. |
| Stamping `[PASS]` immediately after `Set-AdminAuditLogConfig` | Configuration takes up to 60 minutes to propagate; ingestion takes longer. Re-verify after the propagation window. |

---

## 5. Cross-References

- [Control 1.5 — Microsoft Purview Data Loss Prevention](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) … endpoint and browser DLP (Edge for Business unmanaged-AI policy) is the upstream feeder for the `AIApp` workload that surfaces `AIAppInteraction` events. Without DLP capture, PAYG opt-in alone produces no events. (Scenario 3.)
- [Control 1.6 — Microsoft Purview DSPM for AI](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md) … one of three Substrate-tier paths for retrieving the verbatim prompt and response text that the audit record references by message ID. (Scenarios 1, 10, 12.)
- [Control 1.10 — Communication Compliance for AI Interactions](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md) … Substrate-tier path for policy-driven supervisory review of AI-generated communications; FINRA Rule 3110 alignment. (Scenarios 1, 10, 12.)
- [Control 1.19 — eDiscovery for Agent Interactions](../../../controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md) … Substrate-tier path for legal hold, collection, and review of Copilot interactions; the canonical regulator/litigation export channel. (Scenarios 1, 10, 12.)
- [Control 1.9 — Data Retention and Deletion Policies](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md) … Records Management retention design covering the Copilot interactions location; gates the leaver-workflow content-loss scenario. (Scenario 12.)
- [Control 2.12 — Agent Lifecycle Management](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) … leaver / mover sequencing for agent owners and users; ensures hold-before-delete and license-tier guard for regulated populations.
- [Control 3.4 — Audit and Compliance Reporting](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) … independent control testing layer in the tamper-evidence narrative; periodic attestation of the audit-logging stack. (Scenario 13.)
- [Control 3.9 — Microsoft Sentinel Integration](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md) … canonical Sentinel ingestion architecture for AI audit events; second-plane tamper-evidence and the workbook channel for the NYDFS 12-month artifact. (Scenarios 8, 11, 13.)

---

## Documentation Re-Verification Sources

The 2026-10-16 review checked product behavior, API/cmdlet names, permissions, billing prerequisites, retention options, and destination schemas against live Microsoft Learn. It did not verify a tenant, screenshots, licenses assigned to particular users, or regulatory conclusions. Expected test outcomes and framework-selected scopes are implementation criteria, not Microsoft service guarantees.

| Claim family | Primary sources |
|---|---|
| Audit record types, message metadata versus content, product/billing scope | [Copilot and AI audit](https://learn.microsoft.com/en-us/purview/audit-copilot), [raw Copilot schema](https://learn.microsoft.com/en-us/office/office-365-management-api/copilot-schema), [Copilot message retention](https://learn.microsoft.com/en-us/purview/retention-policies-copilot) |
| Enablement, search roles, latency caveats, export limits | [Enable auditing](https://learn.microsoft.com/en-us/purview/audit-log-enable-disable), [Audit search](https://learn.microsoft.com/en-us/purview/audit-search), [supported PowerShell search](https://learn.microsoft.com/en-us/powershell/module/exchangepowershell/search-unifiedauditlog) |
| Audit retention, user licensing, non-user exception | [Audit retention policies](https://learn.microsoft.com/en-us/purview/audit-log-retention-policies), [Audit overview](https://learn.microsoft.com/en-us/purview/audit-solutions-overview) |
| PAYG association and billing | [Enable PAYG](https://learn.microsoft.com/en-us/purview/purview-payg-subscription-based-enablement), [billing models](https://learn.microsoft.com/en-us/purview/purview-billing-models) |
| Graph query permissions, v1.0, pagination and truncation | [Create query](https://learn.microsoft.com/en-us/graph/api/security-auditcoreroot-post-auditlogqueries?view=graph-rest-1.0), [query resource](https://learn.microsoft.com/en-us/graph/api/resources/security-auditlogquery?view=graph-rest-1.0), [service limits](https://learn.microsoft.com/en-us/graph/throttling-limits#security-audit-log-query-service-limits) |
| Agent filters, beta sign-in query, first-party service stream | [Entra Agent ID logs](https://learn.microsoft.com/en-us/entra/agent-id/sign-in-audit-logs-agents), [Microsoft service-principal logs](https://learn.microsoft.com/en-us/entra/identity/monitoring-health/reference-service-principal-table) |
| Default-on authoring versus Dataverse change history | [Copilot Studio auditing](https://learn.microsoft.com/en-us/microsoft-copilot-studio/admin-logging-copilot-studio), [Dataverse audit settings](https://learn.microsoft.com/en-us/power-platform/admin/manage-dataverse-auditing), [May 2026 field-value change](https://learn.microsoft.com/en-us/power-platform/important-changes-coming#removal-of-before-and-after-field-change-values-in-audit-events-sent-to-microsoft-purview), [retrieve details](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/auditing/retrieve-audit-data#retrieve-audit-change-history) |
| Sentinel connector and normalized schema | [Microsoft Copilot connector](https://learn.microsoft.com/en-us/azure/sentinel/data-connectors-reference#microsoft-copilot), [CopilotActivity columns](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/copilotactivity) |
| Immutable-storage verification | [Immutable storage](https://learn.microsoft.com/en-us/azure/storage/blobs/immutable-storage-overview), [read policy cmdlet](https://learn.microsoft.com/en-us/powershell/module/az.storage/get-azrmstoragecontainerimmutabilitypolicy), [lock policy cmdlet](https://learn.microsoft.com/en-us/powershell/module/az.storage/lock-azrmstoragecontainerimmutabilitypolicy) |

[Back to Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification & Testing](verification-testing.md)

---

*Updated: October 2026 | Version: v1.6.2 | UI Verification Status: Needs Review (documentation re-verified; tenant UI not tested)*
