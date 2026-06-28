# Control 3.4 — Troubleshooting: Incident Reporting and Root Cause Analysis

> **Companion playbooks.** [Portal walkthrough](portal-walkthrough.md) · [PowerShell setup](powershell-setup.md) · [Verification & testing](verification-testing.md)
>
> **Sibling pillar references.** [Pillar 3 control 3.4 — Incident Reporting & RCA](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) · [Pillar 1 control 1.7 — Comprehensive audit logging](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) · [Pillar 1 control 1.9 — Data retention & deletion](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md) · [Pillar 1 control 1.11 — Conditional Access & MFA (workload identity)](../../../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md) · [Pillar 2 control 2.16 — RAG source integrity](../../../controls/pillar-2-management/2.16-rag-source-integrity-validation.md)

!!! warning "Non-substitution"
    This playbook describes diagnostic and remediation patterns for the Microsoft 365, Defender XDR, Microsoft Sentinel, and Microsoft Purview portals as observed in tenant UIs current as of April 2026. It is **not** legal, regulatory, or compliance advice. Regulatory clocks (NYDFS Part 500.17(a) 72-hour notice, SEC Regulation S-K Item 1.05 four-business-day disclosure, Reg S-P amended §248.30 30-day customer notification, FINRA Rule 4530, FRB SR 22-4 / OCC Bulletin 2022-3 36-hour banking incident notice, CFTC Part 23 / Part 39 notification, CIRCIA covered-entity reporting, OFAC reporting obligations) are determined by counsel and the firm''s compliance leadership using the firm''s own facts and circumstances. Where this document discusses elapsed-time triggers, it is documenting **how the platform records timestamps** so that those records may support — but never substitute for — the firm''s regulatory determination.


> **Regulatory framing.** The control objective behind 3.4 is that an FSI firm operating Microsoft 365 AI agents (Microsoft Copilot Studio agents, Microsoft 365 Copilot agents, Power Platform AI Builder flows, Azure AI Foundry / Azure OpenAI direct-call applications) can (a) **detect** an agent-related incident, (b) **classify and triage** it within an evidence-preserving framework, (c) **report** it to internal stakeholders and external regulators inside the applicable statutory clock, and (d) produce a **root-cause analysis** that meets examiner expectations for repeatability and corrective-action tracking. Each scenario in this playbook documents a failure mode that has been observed (or that is highly likely given platform behaviour) which would prevent one of those four outcomes, together with the specific portal navigation, KQL, and PowerShell needed to detect, contain, and remediate it. Roles named throughout follow the canonical short forms in [`../../../reference/role-catalog.md`](../../../reference/role-catalog.md).

---
## Table of contents

- §0 Triage tree, severity matrix, and pre-escalation checklist
- §1 Diagnostic data collection — the `Get-Agt34*` helper catalog
- §§2–25 Scenarios 1–24
- §26 Escalation matrix and evidence-collection summary
- §27 Cross-references

---

## §0 Triage tree, severity matrix, and pre-escalation checklist

### 0.1 Symptom → pillar map

The following table is the *first* thing an on-call SOC analyst, the Incident Commander, or the duty CCO should consult. Each row maps a presenting symptom to the scenario in this playbook that owns the runbook, plus the regulatory clock(s) that may be running while triage is occurring. The "Owning role" column uses the canonical short forms from [`../../../reference/role-catalog.md`](../../../reference/role-catalog.md).

| # | Presenting symptom | Scenario | Likely owning role | Regulatory clocks that may be running |
|---|--------------------|----------|--------------------|----------------------------------------|
| 1 | Defender XDR auto-downgraded an incident severity and our 72-hour timer never started | Scenario 1 | Sentinel Admin + Incident Commander | NYDFS Part 500.17(a) 72h |
| 2 | We can''t agree whether the SEC 8-K Item 1.05 four-business-day clock has started | Scenario 2 | Disclosure Committee Chair (CCO) + GC | SEC Reg S-K Item 1.05 |
| 3 | NYDFS portal rejected our 72-hour notice submission | Scenario 3 | CCO / Privacy Officer | NYDFS 500.17(a) |
| 4 | Bank examiner asks why our 36-hour federal notice and 72-hour NYDFS notice tell different stories | Scenario 4 | CISO + GC + CCO | FRB SR 22-4 / OCC Bulletin 2022-3 / FDIC Part 304 36h, NYDFS 72h |
| 5 | We''re inside the Reg S-P 30-day window and the customer-notice template still hasn''t cleared Legal | Scenario 5 | Privacy Officer + GC | Reg S-P §248.30 amended (30 days) |
| 6 | A vendor was breached and our Reg S-P 72-hour service-provider clock already expired | Scenario 6 | CCO + Procurement / TPRM | Reg S-P §248.30(b) 72h |
| 7 | FINRA 4530(d) quarterly file omitted complaints raised in agent chat transcripts | Scenario 7 | CCO + Supervisory Principal | FINRA Rule 4530(d) |
| 8 | We can''t tell which states'' breach-notification statutes apply because the customer-residency map is stale | Scenario 8 | Privacy Officer | 50 state breach-notification statutes |
| 9 | Sentinel automation tried to suspend the agent service principal and got an authorization error | Scenario 9 | Sentinel Admin + Entra Identity Admin | Internal containment SLA |
| 10 | The Sentinel automation rule that should have run on this alert never fired | Scenario 10 | Sentinel Admin | Internal SLA |
| 11 | An IRM case has been pseudonymized in Purview for two days and we can''t unmask the user | Scenario 11 | Purview Compliance Admin + HR + GC | Internal SLA |
| 12 | Legal hold doesn''t appear to have reached every custodian''s mailbox / OneDrive / Teams chat | Scenario 12 | eDiscovery Manager + GC | FRCP Rule 37(e), SEC 17a-4(f) |
| 13 | Microsoft Service Health published a correlated outage *after* we declared root cause | Scenario 13 | Incident Commander + Service Owner | Internal RCA SLA + regulator update obligations |
| 14 | The JSON we exported from a Defender / Sentinel incident is missing fields the examiner asked for | Scenario 14 | Sentinel Admin | Examiner request response window |
| 15 | An incident was closed in the SharePoint IR list without an RCA narrative | Scenario 15 | M365 Admin + Records Officer | Internal RCA SLA |
| 16 | Tabletop exercise revealed our team starts the 72h clock at *discovery* not *determination* | Scenario 16 | CCO + GC | NYDFS 500.17(a), Reg S-P §248.30 |
| 17 | Threat actor demanded crypto payment and we have no documented OFAC screening | Scenario 17 | GC + CFO + CISO | OFAC 50% Rule + IEEPA |
| 18 | We notified the regulator before the cyber-insurance carrier and the policy may exclude coverage | Scenario 18 | Risk Officer + GC | Insurance policy notification window |
| 19 | The agent failure crosses a SOX 404 ICFR material-weakness threshold but the Audit Committee hasn''t been briefed | Scenario 19 | Internal Audit + CFO + Audit Committee Chair | SOX §404, NYSE / Nasdaq listing rules, 10-Q filing window |
| 20 | Examiner asks for Sentinel data older than our 90-day operational tier | Scenario 20 | Sentinel Admin + Records Officer | SEC 17a-4(f), FINRA 4511, CFTC 1.31 |
| 21 | Sentinel custom logs contain raw conversation transcripts with PII / PCI / PHI | Scenario 22 | Sentinel Admin + Privacy Officer + DPO | Reg S-P, GLBA Safeguards Rule, state breach laws |
| 22 | OFAC partial-match alert during a ransom-payment decision and counsel needs a decision package | Scenario 23 | GC + CCO + CFO | OFAC SDN List + 50% Rule |
| 23 | CIRCIA final-rule effective date is mid-quarter and our runbook hasn''t been updated | Scenario 24 | CCO + GC + CISO | CIRCIA covered-cyber-incident reporting |
| 24 | State AG portal rejected our breach notice for per-state format mismatch | Scenario 25 | Privacy Officer + GC | State breach-notification statute clocks |

### 0.2 Severity matrix

The severity matrix below is the bridge between the platform''s automatic severity scoring (Defender XDR / Sentinel) and the firm''s *regulatory* severity, which is what actually drives notification clocks. Platform severity and regulatory severity are not the same and a recurring failure mode (Scenario 1) is allowing the lower of the two to silence the higher.

| Severity | Platform indicator | Regulatory trigger candidates | Default response SLA | Notification path |
|----------|---------------------|--------------------------------|----------------------|--------------------|
| **Sev 1** | Defender XDR `High`, Sentinel `High`, multi-stage incident, business email compromise, ransomware, data exfiltration to external tenant, agent producing material misstatements at scale | NYDFS 72h, banking 36h, SEC 8-K Item 1.05 4-bus-day, Reg S-P 30-day customer notice + 72h SP notice, OFAC reportable transaction, CIRCIA covered cyber incident | Acknowledge ≤15 min, contain ≤1h, IC declared ≤30 min | Page CISO + Incident Commander + duty GC + duty CCO; open Sentinel incident; open SharePoint IR record; start clock log |
| **Sev 2** | Defender XDR `Medium`, Sentinel `Medium`, single-stage incident, agent confidentiality breach affecting <50 users, single-customer Reg S-P trigger, supervisory rule violation candidate | NYDFS materiality determination required, Reg S-P determination required, FINRA 4530 review, state-law analysis required | Acknowledge ≤1h, contain ≤4h | SOC analyst + Sentinel Admin; CCO duty pager; GC notified by next business day unless materiality escalates |
| **Sev 3** | Defender XDR `Low` / `Informational`, Sentinel `Low`, hygiene findings, single-user policy violations, false-positive candidates | None at intake; documentation only | Acknowledge ≤4h, resolve ≤24h | SOC analyst; Sentinel Admin reviews weekly; CCO informed via monthly metrics |

> **Severity escalation rule.** Any Sev 2 or Sev 3 incident in which (a) customer NPI is implicated, (b) an agent produced regulated communications without supervisory pre-clearance, (c) the agent service principal showed evidence of credential abuse, or (d) a US-sanctioned jurisdiction is on either end of the data flow **must** be escalated to Sev 1 by the on-call Incident Commander within 30 minutes of that fact becoming known. Escalation timestamps are themselves examiner-relevant (Scenario 16) and must be captured in the SharePoint IR list with a UTC value.

### 0.3 Pre-escalation checklist

Before paging anyone outside the SOC, the on-call analyst should be able to answer these eight questions. The answers will be required by the Incident Commander, by the duty CCO if a regulatory clock is in scope, and ultimately by the examiner. Each question maps to a column in the SharePoint IR list described in [`portal-walkthrough.md`](portal-walkthrough.md).

1. **What agent or agents are involved?** Capture the Copilot Studio bot ID, the M365 Copilot agent app ID, the Power Platform environment ID, or the Azure AI Foundry deployment name. If multiple agents are implicated, list all of them — this drives the blast-radius analysis later.
2. **What is the agent''s service-principal object ID and tenant?** This is the single most useful pivot for KQL across `AADServicePrincipalSignInLogs`, `CloudAppEvents`, and `AppEvents`. The CCO will be asked by the regulator whether the agent acted under its own identity or under a user-delegated token; you cannot answer that without the SPN object ID.
3. **What data classification is in scope?** Use the Purview sensitivity-label taxonomy (Public / Internal / Confidential / Highly Confidential — Customer NPI / Highly Confidential — Material Non-Public Info). If the answer is "unknown", treat it as Highly Confidential for clock-starting purposes pending classification.
4. **What is the user / customer impact estimate?** Number of unique user principal names that interacted with the affected agent in the last 7 days; number of unique external customer identifiers that appeared in the agent''s grounding sources or output; number of regulated communications generated.
5. **What is the geographic scope?** Which US states'' residents are implicated? Which non-US jurisdictions? This drives the Scenario 8 residency-map decision and the state-AG portal selection in Scenario 25.
6. **When was the issue first observed in telemetry?** This is the *discovery* timestamp. Distinct from the *determination* timestamp (Scenario 16), which is the moment a person with authority concluded that an event meeting the regulatory definition had occurred.
7. **What containment actions have been attempted?** List each, with timestamp, executor, and outcome. If the Sentinel "suspend agent" automation failed, capture the HTTP status (Scenario 9) — that is itself examiner evidence.
8. **What is the current evidence-preservation state?** Confirm legal hold has been considered (Scenario 12), Sentinel retention is being held (Scenario 20), and the Defender XDR / Sentinel incident JSON has been exported with the eight required fields (Scenario 14). If any of these is "not yet", note that and page eDiscovery Manager + Records Officer.

### 0.4 Examiner artifact preservation pattern

Within the first hour of a Sev 1 declaration, the Sentinel Admin (or the duty SOC Lead in their absence) should establish a write-once evidence container, populate it with the artifacts listed below, and record the SHA-256 hash of each artifact in the SharePoint IR list. The container itself should be a SharePoint Online site collection or an Azure Storage immutable blob container with legal hold applied; the choice depends on the firm''s records retention schedule but **must** survive the longest applicable regulatory retention period (typically SEC 17a-4(f) six-year requirement for broker-dealers, CFTC 1.31 five-year requirement, or the firm''s own document-retention policy if longer).

| Artifact | Source | Frequency during incident | Retention basis |
|----------|--------|----------------------------|-----------------|
| Defender XDR incident JSON (full) | `https://security.microsoft.com` → Incidents → *Export* | Snapshot at: declaration, status change, RCA close | SEC 17a-4(f), FINRA 4511 |
| Sentinel incident JSON + bookmarks + investigation graph PNG | `https://portal.azure.com` → Sentinel → Incidents → *Export* | Same cadence as above | Same |
| Raw KQL query results referenced in incident notes | Sentinel Logs blade → *Export to CSV* | At each KQL execution | Same |
| `AADServicePrincipalSignInLogs` for agent SPN, ±48h around incident window | Entra Sign-in logs → filter SPN object ID → *Download* | Once at declaration; once at close | NYDFS 500.06 audit-trail |
| `OfficeActivity` for impacted users / tenants | Sentinel Logs blade KQL export | Once at declaration | SEC 17a-4(f) |
| Service Health incident detail page (PDF) | `https://admin.microsoft.com` → Health → Service health → *Print to PDF* | Once at declaration; once at any Microsoft post-incident report publication | Internal RCA |
| SharePoint IR list item snapshot | List → Item → *Export to PDF* | At every status change | Internal RCA |
| Power Automate run history for IR workflows | `https://make.powerautomate.com` → My flows → *Run history* → *Export* | Once at close | Internal RCA |
| Communication artifacts (regulator submission receipts, customer notice samples, attorney engagement letter) | Various | As produced | Reg-specific (NYDFS, Reg S-P, etc.) |
| Decision log (UTC timeline of who decided what, when, on what facts) | Maintained by Incident Commander; final copy filed in IR list | Continuously | NYDFS 500.16, examiner expectation |

> **Hashing convention.** The Sentinel Admin''s helper module exposes `New-Agt34EvidenceManifest` (described in §1) which computes SHA-256 over each artifact, writes a manifest JSON containing `{ name, path, sha256, capturedUtc, capturedBy }`, and uploads both manifest and artifacts to the immutable container with a single `Set-AzStorageBlobImmutabilityPolicy` call. Capture-time SHA-256 values must be recorded in the SharePoint IR list **at the time of capture**, not retrospectively, because retrospective hashes do not establish chain of custody.

---
## §1 Diagnostic data collection — the `Get-Agt34*` helper catalog

The `FsiAgtGov.Agt34` PowerShell module (installed by [`powershell-setup.md`](powershell-setup.md)) exposes a set of `Get-Agt34*` and `New-Agt34*` cmdlets that wrap the Microsoft Graph, Defender XDR, Sentinel, and Purview APIs to produce reproducible diagnostic snapshots. Examiners frequently ask "show me the script you ran and the output it produced" — every cmdlet in this module logs its own invocation, parameters, and output hash to a write-once log so that the answer is always "yes, here it is."

### 1.1 Cmdlet catalog

| Cmdlet | Purpose | Required role | Outputs |
|--------|---------|----------------|---------|
| `Get-Agt34Incident -IncidentId <int>` | Pulls a Defender XDR incident plus all alerts, evidence, and entities; resolves agent SPN object IDs into display names | Sentinel Admin (or Defender XDR Security Reader) | JSON to `out/incidents/<id>.json`; SHA-256 logged |
| `Get-Agt34SentinelIncident -IncidentNumber <int>` | Same for a Sentinel incident; includes investigation graph as a serialised adjacency list | Sentinel Admin (or Microsoft Sentinel Reader) | JSON + GraphML |
| `Get-Agt34AgentSpn -AppDisplayName <string>` | Resolves an agent display name to its SPN object ID, app ID, owners, certificates / secrets, and assigned API permissions | Entra Identity Reader | PSCustomObject |
| `Get-Agt34AgentSignIns -SpnObjectId <guid> -StartUtc <datetime> -EndUtc <datetime>` | Pulls `AADServicePrincipalSignInLogs` over the window (chunked at 1000 rows) | Entra Identity Reader | CSV |
| `Get-Agt34AgentRunHistory -EnvironmentId <guid> -BotId <guid>` | For Copilot Studio agents, pulls conversation transcript metadata (NOT content) | Power Platform Admin | CSV |
| `Get-Agt34PurviewIrmCase -CaseId <string>` | Pulls IRM case in pseudonymised form unless `-Unmask` is specified and approval log is present | Purview Insider Risk Investigator + Insider Risk Analyst (joint) | JSON |
| `Get-Agt34LegalHold -CaseId <string>` | Returns the eDiscovery Premium hold''s custodian list, hold locations, hold status per location, and last-evaluated timestamp | eDiscovery Manager | CSV |
| `Get-Agt34ServiceHealth -StartUtc <datetime> -EndUtc <datetime>` | Pulls Microsoft Service Health incidents and advisories overlapping the window | M365 Service Support Admin | JSON |
| `Get-Agt34IrListItem -ItemId <int>` | Reads the SharePoint IR list item, returns it as PSCustomObject, and snapshots the related Power Automate run history | M365 Admin | JSON |
| `Get-Agt34RetentionStatus -WorkspaceName <string> -TableName <string>` | Returns operational retention, archive retention, and total retention for a Sentinel table | Sentinel Admin | PSCustomObject |
| `New-Agt34EvidenceManifest -ArtifactPath <string> -ContainerUri <string>` | Computes SHA-256 over each artifact, writes manifest, uploads to immutable storage container | Sentinel Admin + Storage Blob Data Contributor | JSON manifest |
| `Test-Agt34OfacScreening -PaymentAddress <string> -Counterparty <hashtable>` | Calls the firm''s OFAC screening service (configured in `agt34.config.json`); records request + response with timestamp and SHA-256; **does not** make a determination | OFAC Screening Officer | JSON |
| `Invoke-Agt34RegulatorClockLog -Trigger <string> -Determination <datetime> -Notes <string>` | Appends a row to the immutable clock log used in Scenario 16 | CCO + Incident Commander (joint signoff) | JSONL |

> **Module installation reminder.** All `Get-Agt34*` cmdlets are thin wrappers around supported Microsoft Graph endpoints, Microsoft Sentinel REST APIs, and Purview Compliance APIs. The module does not call any unsupported or undocumented endpoint. The module''s MSI is signed by the firm''s Code-Signing CA and is loaded via the JustInTime / PIM session pattern documented in [`../../_shared/powershell-baseline.md`](../../_shared/powershell-baseline.md).

### 1.2 KQL primer — the seven tables you will keep returning to

The KQL examples throughout the scenarios below assume the analyst is logged into a Sentinel workspace that has the following data connectors enabled and stable for at least 24 hours:

- **Microsoft Defender XDR** (provides `SecurityIncident`, `SecurityAlert`, `AlertEvidence`, `IdentityLogonEvents`, `CloudAppEvents`)
- **Microsoft Entra ID** (provides `SigninLogs`, `AADServicePrincipalSignInLogs`, `AuditLogs`, `AADManagedIdentitySignInLogs`)
- **Office 365** (provides `OfficeActivity` including ExchangeAdmin, SharePoint, OneDrive, Teams, AzureActiveDirectory record types)
- **Application Insights / Log Analytics** for the agent''s host (provides `AppEvents`, `AppRequests`, `AppDependencies`, `AppExceptions`, `AppTraces`)
- **Microsoft Purview** (provides `PurviewDataSensitivityLogs`, `MCASShadowItReporting` where licensed)
- **Power Platform Connector** (provides `PowerPlatformAdminActivity`)
- **Microsoft Sentinel Health** (provides `SentinelHealth`, `SentinelAuditLogs`)

A typical agent-incident pivot starts from the agent''s service-principal object ID, fans out through `AADServicePrincipalSignInLogs` to identify which conditional-access policies fired (cross-ref [Control 1.11](../../../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md)), then joins to `OfficeActivity` and `CloudAppEvents` to identify what the agent actually did with whatever token it obtained. The `AppEvents` table is the right place to look for prompt / response telemetry **only if** the agent''s host application has been configured to log conversation metadata without conversation content (Scenario 22 explains why content-in-telemetry is a reportable PII spill).

### 1.3 Standard KQL header

Every KQL query in this playbook should be prefixed with the following header, which (a) tags the query with the IR record so that examiner queries can be traced back to the runbook step that produced them, and (b) sets a deterministic time window keyed off the IR list item rather than off `now()`:

```kusto
// IR-Record: <SP-IR-id>  Scenario: <playbook-scenario-#>  Run-By: <upn>
let _irId = "SP-IR-2026-NNNN";
let _windowStart = datetime(2026-04-15T13:00:00Z);  // copy from IR list "FirstObservedUtc"
let _windowEnd   = datetime(2026-04-16T13:00:00Z);  // copy from IR list "ContainmentDeclaredUtc"
let _agentSpn    = "00000000-0000-0000-0000-000000000000";  // copy from IR list "AgentSpnObjectId"
```

Examiner-friendly KQL is deterministic KQL. `now()`-based windows are defensible only if the query is rerun together with its results; pinning the window to fields from the IR record means the same query produces the same answer six months later.

---
## §2 Scenario 1 — Defender XDR severity auto-downgrade silences the NYDFS 72-hour timer
**Symptom.** A Defender XDR incident that was created at `Sev=High` is reclassified to `Sev=Medium` (or `Informational`) within 30–90 minutes by the platform''s built-in severity-tuning logic — typically because the alert correlation engine determined that all participating identities are already remediated, the affected mailboxes have advanced phishing protection enabled, or a confidence score on one constituent alert dropped after additional telemetry arrived. The downgrade silently disqualifies the incident from the firm''s "Sev 1 → start NYDFS 72-hour clock" automation rule, and 24–48 hours later the duty CCO discovers the incident in a weekly review with no clock log started.

**Likely cause.** Defender XDR''s adaptive severity scoring (visible under *Settings → Microsoft Defender XDR → Alert tuning → Severity*) is enabled by default and is intended to reduce alert fatigue. The rule firing on this incident does not distinguish between "the alert is now lower priority" and "the regulatory obligation that flowed from the alert at intake has lapsed." The Sentinel automation rule that should have started the clock was filtered on `Severity == "High"` at the time of evaluation rather than at the time of incident creation.

**Diagnostic steps.**

*Portal:* Navigate to `https://security.microsoft.com` → **Incidents & alerts** → **Incidents** → open the incident → **Activity log** tab. The activity log shows every system-initiated and user-initiated severity change with UTC timestamps, the prior value, the new value, and the actor (system or user). If the `Severity` field on the incident header now reads `Medium` but the activity log shows the incident was created at `High` and downgraded by `System (Severity tuning)`, that confirms the auto-downgrade.

*KQL:* Run the following in Sentinel **Logs**:

```kusto
// IR-Record: <SP-IR-id>  Scenario: 1  Run-By: <upn>
SecurityIncident
| where TimeGenerated between (_windowStart .. _windowEnd)
| where IncidentName contains "<incident-name-fragment>"
| project TimeGenerated, IncidentNumber, Title, Severity, Status, Owner, AdditionalData
| order by TimeGenerated asc
```

The `Severity` and `Status` columns expose every change as a separate row. Expect to see an initial `High` row followed by a `Medium` row with the same `IncidentNumber`. Cross-reference against `SecurityAlert` for each constituent alert — if any alert is still `High` but the rolled-up incident is `Medium`, the rollup logic produced the downgrade.

*PowerShell:* `Get-Agt34Incident -IncidentId <id>` returns the full incident JSON including the `lastUpdateDateTime`, `severity`, and `classification` history. Compare against the SharePoint IR record''s `InitialSeverityUtc` field — if they differ, escalate the incident to Sev 1 manually and start the clock retroactively from the *original* `createdDateTime`.

**Resolution.** (1) The duty Sentinel Admin manually overrides the incident severity back to `High` in the portal (incident header → **Manage incident** → **Severity → High** → save with reason "regulatory clock evaluation"). (2) The Incident Commander declares Sev 1 in the SharePoint IR list and updates `InitialSeverityUtc` to the original `createdDateTime` from Defender XDR. (3) The duty CCO calls `Invoke-Agt34RegulatorClockLog -Trigger "NYDFS-500.17a" -Determination <utc-of-original-createdDateTime> -Notes "Downgraded by adaptive severity at <utc>; restored at <utc> per RCA finding 1"`. (4) The Sentinel Admin updates the automation rule that starts the clock to evaluate `Severity` from the incident''s creation event rather than its current state — see resolution snippet below.

```kusto
// Updated automation rule trigger query
SecurityIncident
| summarize InitialSeverity = arg_min(TimeGenerated, Severity) by IncidentNumber
| where InitialSeverity.Severity == "High"
```

**Prevention.** (1) Disable adaptive severity tuning for incident classes that have a regulatory clock attached, OR keep tuning enabled but route the *intake-time* severity into the SharePoint IR list at incident creation (capture `createdDateTime` and `severity` immediately into the IR record). (2) Configure the Sentinel automation rule to fire on the `IncidentCreated` event, not on the polling-style `IncidentUpdated` event. (3) Add a Logic Apps step that, on every Defender XDR severity-change event for an open Sev 1 incident, posts a Teams message to the on-call CCO channel so the regulatory team is informed of the change *as it happens*. (4) Include this scenario in the quarterly tabletop (Scenario 16).

**Regulatory-evidence implications.** The clock-log entry created in step (3) above must include both the original `createdDateTime` and the date / time at which the firm became aware that the downgrade had silenced the automation. Examiners will ask why the clock was started retroactively; the answer is that the regulatory determination is keyed to discovery of the underlying facts, not to the platform''s internal severity score. The decision log entry should reference the activity log evidence and the updated automation rule. This pattern supports — but does not substitute for — the firm''s NYDFS Part 500.17(a) determination, which is made by the CCO based on facts and circumstances.

---

## §3 Scenario 2 — SEC 8-K Item 1.05 materiality clock confusion
**Symptom.** During a Sev 1 incident affecting a public-company registrant, the Disclosure Committee Chair (typically the CCO) and Outside Counsel produce inconsistent positions on whether the SEC Regulation S-K Item 1.05 four-business-day clock has begun. The CCO believes the clock starts on internal "determination of materiality" (the language of the rule); Outside Counsel argues a more conservative reading that incorporates the firm''s public-disclosure controls and the timing of the Disclosure Committee meeting at which materiality was formally voted. The disagreement creates a 24–48 hour gap during which no decision is recorded in the clock log and the incident's RCA cannot proceed.

**Likely cause.** The firm''s incident-response runbook does not explicitly designate (a) which body is authorized to make the materiality determination, (b) what evidentiary record that body must produce, and (c) how the determination is timestamped into the clock log. Item 1.05 of Reg S-K, as adopted in the SEC''s 2023 cybersecurity-disclosure rule, requires disclosure of a "material cybersecurity incident" within four business days of "the date the registrant determines that the cybersecurity incident is material" — but the rule defers to the registrant on the *process* by which materiality is determined.

**Diagnostic steps.**

*Portal:* The SharePoint IR list item should show a `MaterialityDeterminationStatus` field with one of {`Pending`, `Not material`, `Material — public-co disclosure required`, `Deferred — national security`}. If the field reads `Pending` for more than 24 hours after a Sev 1 declaration on a public-co incident, the runbook gap is real. Open the IR list item → **Versions** to see who set the field, when, and what comments were attached.

*Document review:* Open the Disclosure Committee charter (typically stored under the GC''s SharePoint document library). Confirm whether the charter explicitly delegates incident-materiality determination to the committee or whether it reserves that determination to the full board. If the charter is silent, the runbook gap is the root cause.

*PowerShell:* `Get-Agt34IrListItem -ItemId <id>` returns the full IR record including the version history of `MaterialityDeterminationStatus`. The output also includes the `RelatedDecisionLogEntries` field, which lists every entry the Incident Commander has filed in the immutable decision log. If the decision log shows multiple entries from CCO and Outside Counsel disagreeing on the threshold, the runbook gap is documented.

**Resolution.** (1) Convene an emergency Disclosure Committee meeting (the GC and CCO are jointly authorized to call one) to formally vote on materiality and timestamp the vote into the clock log. (2) The CCO calls `Invoke-Agt34RegulatorClockLog -Trigger "SEC-RegSK-1.05" -Determination <utc-of-vote> -Notes "Disclosure Committee voted material at <utc>; recorded by <upn>; quorum present per charter §X.Y"`. (3) Outside Counsel files a memo (saved to the immutable evidence container) describing the basis for the materiality determination and the Item 1.05 disclosure timeline, including any reasoned conclusion to invoke the limited national-security delay available under Item 1.05(c). (4) The Disclosure Committee Chair confirms that the four-business-day clock will run from the timestamp recorded in step (2).

**Prevention.** (1) Update the Disclosure Committee charter to explicitly designate the committee as the authorized body for cyber-incident materiality determinations and to permit emergency meetings called by the GC + CCO jointly. (2) Add a `MaterialityDeterminationOwner` field to the SharePoint IR list with default value "Disclosure Committee Chair (CCO)". (3) Build a Power Automate flow that, on Sev 1 declaration for a public-co registrant, automatically posts to the Disclosure Committee Teams channel with a meeting-request link and a templated agenda. (4) Run a tabletop exercise at least annually (Scenario 16) that includes a Disclosure Committee mock vote.

**Regulatory-evidence implications.** The clock-log entry, the Disclosure Committee minutes, and the Outside Counsel memo together form the record that the firm relies on to demonstrate to the SEC Division of Corporation Finance — and to investors in any subsequent shareholder action — when materiality was determined and on what facts. The platform''s timestamps (Defender XDR `createdDateTime`, Sentinel `firstActivity`) provide *contemporaneous evidence* of the underlying facts but do not themselves constitute the determination. The four-business-day clock is calculated from the Disclosure Committee vote timestamp recorded in the immutable clock log, not from the platform timestamps.

---

## §4 Scenario 3 — NYDFS portal submission rejected
**Symptom.** Within hours of the firm''s NYDFS Part 500.17(a) 72-hour notice submission, the NYDFS Cybersecurity Portal (`myportal.dfs.ny.gov`) returns one of three rejection patterns: (a) "Incident type does not match a recognised taxonomy value"; (b) "Reporting entity covered-entity number invalid for affiliate scoping"; or (c) "Required field `RansomwareMaterialityFlag` is missing for events involving extortion." The firm now must resubmit before the 72-hour clock expires, with the original submission timestamp preserved as evidence of good-faith effort.

**Likely cause.** (a) NYDFS updated the incident taxonomy in late 2024 (post-amendment to Part 500) and the firm''s submission template still uses the prior values. (b) The covered-entity number on the submission belongs to the parent holding company, but the affected entity is a New York-licensed insurer subsidiary with its own number — Part 500 attaches at the licensee level. (c) NYDFS''s 2023 amendment added a new ransomware-materiality field that is now mandatory whenever the event involves extortion, even if no payment is being considered.

**Diagnostic steps.**

*Portal:* Open `https://myportal.dfs.ny.gov` → **Cybersecurity Event Reporting** → the rejected submission. The portal displays the rejection reason in red at the top of the form, with a field-level highlight indicating which fields failed validation. Take a screenshot — it is contemporaneous evidence of the rejection.

*Document review:* Open the firm''s NYDFS submission template (typically a Word document maintained by the CCO''s office) and compare its taxonomy values against the current portal dropdown. Open the firm''s NYDFS covered-entity inventory to confirm which entity number is correct for the affected business unit.

*PowerShell:* The firm''s NYDFS portal does not expose a public API; submissions are by web form. There is no PowerShell diagnostic — instead, the duty CCO should `Get-Agt34IrListItem -ItemId <id>` to confirm that the IR record''s `RegulatorSubmission` sub-collection has captured the rejection screenshot, the original submission JSON (rendered from the template), and the planned re-submission timestamp.

**Resolution.** (1) The CCO and the duty privacy counsel jointly review the rejection reason and produce a corrected submission within the time remaining on the 72-hour clock. The corrected submission must reference the original submission''s timestamp in its narrative ("Initial submission attempted at `<utc>`; rejected for `<reason>`; resubmitted at `<utc>`."). (2) Update the SharePoint IR list `RegulatorSubmission` sub-collection with both submissions and the rejection screenshot. (3) Append an entry to the immutable clock log: `Invoke-Agt34RegulatorClockLog -Trigger "NYDFS-500.17a-resubmission" -Determination <utc-of-resubmit> -Notes "Original submitted at <utc>, rejected for <reason>, corrected and resubmitted at <utc>"`. (4) If the re-submission also fails or the 72-hour clock expires before submission is accepted, the CCO should call the NYDFS Cybersecurity Division duty officer (number listed in the portal) to record the firm''s attempted compliance and to obtain an out-of-band acknowledgment.

**Prevention.** (1) Subscribe the CCO''s office to NYDFS regulatory bulletins and add a quarterly review of the submission template against the live portal taxonomy to the CCO calendar. (2) Maintain a covered-entity inventory mapping each affected business unit / agent to the correct NYDFS covered-entity number; review at least annually. (3) Build a pre-submission validation script (`Test-Agt34NydfsSubmission` — see [`powershell-setup.md`](powershell-setup.md)) that compares the draft submission JSON against a versioned schema file before the human submitter opens the portal. (4) Conduct a NYDFS-specific tabletop annually (Scenario 16) that exercises the portal submission UI, not just the legal analysis.

**Regulatory-evidence implications.** NYDFS examiners are particularly interested in the firm''s good-faith effort to comply within 72 hours, even when the first submission is rejected on technical grounds. Preserving (a) the original submission timestamp, (b) the rejection screenshot, (c) the corrected submission, and (d) the clock-log entries showing both events demonstrates that the firm attempted timely compliance and acted promptly to correct the rejection. The decision log should reference all four artifacts. None of this substitutes for the firm''s underlying materiality determination, which is governed by Part 500.17(a) and the firm''s Cybersecurity Program documentation.

---
## §5 Scenario 4 — Banking 36h vs NYDFS 72h coordinated submission
**Symptom.** A bank-holding-company subsidiary that is *both* a national bank (regulated by the OCC) and a NYDFS Part 500 covered entity experiences an agent incident that meets the federal "computer-security incident" threshold under FRB SR 22-4 / OCC Bulletin 2022-3 / FDIC Part 304 (notification within 36 hours of determination) and the NYDFS Part 500.17(a) threshold (notification within 72 hours of determination). The firm submits the 36-hour federal notice on day 1 with a brief "still under investigation" narrative, and the 72-hour NYDFS notice on day 3 with a substantially more detailed narrative. Two months later, an OCC examiner asks why the two notices tell materially different stories.

**Likely cause.** The 36-hour clock typically expires before the firm has completed enough investigation to produce a detailed narrative, while the 72-hour clock leaves room for additional fact-finding. If the firm''s incident-response runbook does not enforce *narrative consistency* between the two submissions — explicitly noting in the 72-hour NYDFS notice that the 36-hour federal notice was filed earlier with the information then available — the submissions can read like contradictory accounts of the same incident.

**Diagnostic steps.**

*Portal:* Open the SharePoint IR list item → **RegulatorSubmission** sub-collection → compare the 36-hour and 72-hour submission narratives side-by-side. Look for (a) factual claims in the 72-hour narrative that contradict the 36-hour narrative without an explicit "based on continuing investigation" framing; (b) impact estimates that differ by more than an order of magnitude without explanation; (c) different root-cause hypotheses without a "RCA in progress" caveat in the earlier filing.

*KQL:* Run a Sentinel KQL to compare the incident state at the two timestamps and confirm what was actually known when each submission was filed:

```kusto
// IR-Record: <SP-IR-id>  Scenario: 4  Run-By: <upn>
SecurityIncident
| where IncidentNumber == <id>
| where TimeGenerated <= datetime(<36h-submission-utc>)
| summarize Snapshot36h = arg_max(TimeGenerated, *)
| union (
    SecurityIncident
    | where IncidentNumber == <id>
    | where TimeGenerated <= datetime(<72h-submission-utc>)
    | summarize Snapshot72h = arg_max(TimeGenerated, *)
)
```

The output shows the platform-recorded incident state at each submission moment and supports a "this is what we knew when" narrative.

*PowerShell:* `Get-Agt34IrListItem -ItemId <id>` returns the version history of the IR record, which captures every field change with timestamp and author. Cross-reference against the two submission narratives to confirm which facts had been added to the IR record by the 36-hour submission moment.

**Resolution.** (1) The CCO and GC jointly draft a supplemental NYDFS update that explicitly cross-references the 36-hour federal notice and reconciles any narrative differences ("On `<utc>` the firm filed the federal 36-hour notice with the information available at that time. Continuing investigation through `<utc>` produced the additional facts described in this 72-hour notice; specifically, `<reconciled facts>`."). (2) File the supplemental update through the NYDFS portal with cross-reference to the original NYDFS submission. (3) Update the SharePoint IR list with both the federal and NYDFS submissions, the supplemental update, and an internal memo describing the reconciliation. (4) Append a clock-log entry recording the supplemental submission and its purpose.

**Prevention.** (1) Build a coordinated-submission template that the CCO''s office maintains for any incident triggering both a 36-hour federal notice and a 72-hour NYDFS notice; the template enforces a "what we knew at this timestamp" framing for the earlier submission and a "additional facts learned since" framing for the later submission. (2) Designate the same primary author (typically the duty CCO) for both submissions to enforce narrative consistency. (3) Conduct an annual coordinated-submission tabletop (Scenario 16) that exercises both filings under time pressure. (4) Build a Power Automate flow that, on Sev 1 declaration for a federally-regulated banking subsidiary that is also a NYDFS covered entity, automatically creates draft submissions for both regulators with the coordinated template and routes them to the duty CCO.

**Regulatory-evidence implications.** Examiners from both the federal banking agency and NYDFS will compare the two submissions. The reconciliation memo and the supplemental NYDFS update support the firm''s ability to demonstrate consistent good-faith compliance. The SharePoint IR list version history and the immutable clock log provide contemporaneous evidence of when each fact became known. This pattern supports — but does not substitute for — the firm''s separate determinations under each regulatory regime, which are made by the CCO based on the facts and circumstances and the regulatory thresholds applicable to each.

---

## §6 Scenario 5 — Reg S-P 30-day customer notice template not approved in time
**Symptom.** A confirmed unauthorized access to customer NPI triggers the SEC Regulation S-P amended §248.30 30-day individual customer notification requirement. With ten days remaining on the 30-day clock, the Privacy Officer discovers that the customer-notice template has not yet been approved by the GC, the firm''s outside privacy counsel has open redlines, and the printer-mailer vendor requires five business days' notice for production. The firm now faces a credible risk of missing the 30-day deadline.

**Likely cause.** The runbook treats the 30-day customer notice as a "Day 25" workstream, leaving insufficient float for legal review, vendor coordination, state-AG cross-references (Scenario 25), and edge-case translation requirements (Spanish, Mandarin, Korean, etc.) where the firm''s customer base requires them.

**Diagnostic steps.**

*Portal:* Open the SharePoint IR list item → **CustomerNoticeWorkstream** sub-list. Each row tracks a milestone (template draft, internal legal review, outside counsel review, vendor production order, mail drop). Identify the milestones that are past their planned date with the current `Status = Open` and the rows where the dependency chain has stalled.

*Document review:* Open the customer-notice template in the firm''s Privacy library and check (a) the version history for the most recent edit, (b) the comment thread for unresolved redlines, (c) whether translations are attached as separate sub-documents. Open the printer-mailer master service agreement and confirm the production lead time and the SLA for rush jobs.

*PowerShell:* `Get-Agt34IrListItem -ItemId <id>` returns the workstream sub-list along with the version history of each milestone. The output supports a "where in the dependency chain are we stalled" diagnostic.

**Resolution.** (1) The Privacy Officer convenes an emergency review with the GC, outside privacy counsel, and the vendor account manager — within 24 hours of identifying the slip. (2) Outside counsel triages open redlines into "blocking" (must resolve before mail drop) and "non-blocking" (will record in next cycle); the GC accepts the blocking redlines and signs the template. (3) The vendor is engaged on a rush SLA with explicit overtime authorization. (4) The Privacy Officer files an entry in the immutable clock log: `Invoke-Agt34RegulatorClockLog -Trigger "RegSP-248.30-individual-notice" -Determination <utc-of-mail-drop> -Notes "Mail drop completed at <utc>; 30-day clock from <determination-utc> per CCO finding"`. (5) For any state where the per-state breach-notification statute imposes a shorter deadline than Reg S-P''s 30 days (Scenario 8 / 25), the firm files those notices on the per-state schedule and references the Reg S-P notice in the per-state filing.

**Prevention.** (1) Re-baseline the customer-notice runbook to a "Day 10" planning horizon (template approved, vendor engaged, translations queued) so that subsequent slips have 20 days of float. (2) Maintain a *pre-approved* customer-notice template that the GC and outside counsel review at least annually, with placeholders for incident-specific facts; the runbook then becomes "fill in placeholders and confirm GC signs the populated version" rather than "draft and review from scratch." (3) Negotiate a standing rush-production SLA with the printer-mailer vendor as part of the master agreement. (4) Maintain pre-translated versions of the template for the firm''s top language requirements; the runbook then validates translation rather than producing it from scratch. (5) Run a customer-notice tabletop (Scenario 16) at least annually with realistic vendor and translation dependencies.

**Regulatory-evidence implications.** The SEC''s May 2024 amendment to Regulation S-P added the 30-day individual notification requirement and explicitly contemplates that firms have established processes for timely notification. Maintaining a pre-approved template, a standing vendor SLA, and pre-translated versions supports the firm''s ability to demonstrate the existence of those processes. The clock-log entries, the SharePoint IR list workstream sub-collection, and the printer-mailer''s mail-drop confirmation together form the contemporaneous record of compliance. This pattern supports — but does not substitute for — the firm''s underlying Reg S-P determination, which is made by the CCO and Privacy Officer.

---

## §7 Scenario 6 — Reg S-P 72h service-provider notice missed
**Symptom.** A third-party service provider that hosts (or has access to) the firm''s customer NPI experiences a security incident. The vendor''s incident-response team notifies the firm''s Procurement / Third-Party Risk Management (TPRM) office five business days after detecting the incident. By the time TPRM escalates to the firm''s CCO, the Reg S-P §248.30(b) 72-hour service-provider notification window — which runs from the *vendor''s* awareness, not from the firm''s — has already expired.

**Likely cause.** The vendor master services agreement (MSA) does not contain an explicit notification clause requiring the vendor to notify the firm within a defined window (e.g., 24 or 48 hours) of *the vendor''s* awareness of an incident affecting the firm''s NPI. Without such a clause, the vendor''s internal escalation timeline drives the firm''s ability to comply with Reg S-P''s 72-hour SP-notification requirement.

**Diagnostic steps.**

*Portal:* Open the firm''s TPRM platform (Archer, ProcessUnity, OneTrust, or equivalent) → the vendor record → the contracts tab. Locate the executed MSA, data-processing addendum, and any cybersecurity rider. Search for keywords "notify", "notification", "incident", "breach". Capture the operative clause language.

*Document review:* Compare the operative MSA notification clause (if any) against the firm''s standard cybersecurity rider template. Identify the gap.

*PowerShell:* The TPRM platform may have a Power BI dashboard or a custom export capability. The firm''s `Get-Agt34TprmVendor -VendorId <id>` (companion cmdlet to the 3.4 module, optional) can pull the vendor''s contract, the cybersecurity rider, and the firm''s most recent vendor-risk assessment for examiner-facing review.

**Resolution.** (1) The CCO immediately files the Reg S-P §248.30(b) SP-notification with NYDFS or the relevant regulator (depending on the customer-segment overlap), with an explicit narrative noting the date the vendor became aware vs. the date the firm became aware, and the delay attributable to the vendor''s notification process. (2) The GC and Procurement open a contract amendment with the vendor to add a 24-hour vendor-to-firm notification clause and a corresponding indemnification provision. (3) The CCO reviews other vendors with similar gaps and issues a Procurement standing instruction to add the notification clause to all in-flight renewals and new MSAs. (4) The Privacy Officer evaluates whether the vendor incident also triggers individual-customer notification under Reg S-P §248.30 (Scenario 5) and proceeds accordingly.

**Prevention.** (1) The firm''s standard cybersecurity rider must include a 24-hour vendor-to-firm notification clause for any incident affecting NPI; Procurement should not approve a vendor onboarding without that clause. (2) Annual TPRM audits include a contract-clause check for the notification provision; gaps trigger remediation. (3) The TPRM platform should track every vendor''s notification-clause status as a structured field, supporting bulk reporting and risk-rating. (4) Quarterly TPRM-and-CCO joint reviews flag any vendor without the clause for prioritised renegotiation or termination.

**Regulatory-evidence implications.** Examiners will ask why the firm missed the 72-hour SP-notification clock. The contract-amendment record, the standing Procurement instruction, and the bulk-remediation roadmap support the firm''s ability to demonstrate that the gap has been identified and is being closed. The Reg S-P submission narrative — explicitly distinguishing vendor-awareness from firm-awareness timing — supports the firm''s good-faith compliance posture. This pattern supports — but does not substitute for — the firm''s underlying determination under Reg S-P, which is made by the CCO.

---
## §8 Scenario 7 — FINRA 4530(d) quarterly file missed AI-agent complaints
**Symptom.** During the firm''s quarterly FINRA Rule 4530(d) statistical-complaint filing review, the Supervisory Principal discovers that complaints raised in customer interactions with AI agents (Copilot Studio bot for retail brokerage support, M365 Copilot for financial-advisor productivity) are not in the file. The firm''s WORM-archived `OfficeActivity` records and the agent''s `AppEvents` telemetry contain at least a dozen plausible complaint patterns ("you gave me wrong information about my account", "I want to speak to a human about this advice you gave", "this recommendation is not suitable for my situation") that should have been routed to the complaint-management workflow.

**Likely cause.** The complaint-management workflow ingests escalations from the firm''s contact-center recording vendor and from a SharePoint complaint-intake form, but does not subscribe to the agent''s `AppEvents` telemetry. The agent itself has no automated classifier that detects complaint language and routes to the complaint-management workflow.

**Diagnostic steps.**

*KQL:* Search the agent host''s `AppEvents` for complaint patterns:

```kusto
// IR-Record: <SP-IR-id>  Scenario: 7  Run-By: <upn>
AppEvents
| where TimeGenerated between (_windowStart .. _windowEnd)
| where Name == "ConversationTurn"
| extend role = tostring(Properties.role), text = tostring(Properties.text_metadata_only)
| where role == "user"
| where text matches regex @"(?i)wrong|incorrect|complain|complaint|suitabl|advis|speak to (?:a )?human|escalat|representative|misled|unauthori[sz]ed"
| project TimeGenerated, ConversationId, UserUpn = tostring(Properties.user_upn), text
| order by TimeGenerated asc
```

(Note: `text_metadata_only` is a sanitised field — see Scenario 22 — that does not contain raw conversation content. The complaint-detection pattern is run on a metadata classifier output, not on raw transcripts.)

*Portal:* Open the firm''s complaint-management workflow (typically in Salesforce Financial Services Cloud or a dedicated CRM) → search for any complaint records with `Source = AIAgent` between the relevant dates. If the count is zero or implausibly low, the workflow is not subscribing to the agent telemetry.

*PowerShell:* `Get-Agt34AgentRunHistory -EnvironmentId <env-id> -BotId <bot-id>` returns the conversation metadata (not content) for the relevant period. Cross-reference against the complaint-management workflow records to confirm the gap.

**Resolution.** (1) The Supervisory Principal and the duty CCO file an updated FINRA 4530(d) statistical-complaint amendment that includes the previously-missed AI-agent complaints, with an explicit narrative describing the workflow gap and the remediation plan. (2) The Sentinel Admin and the Power Platform Admin jointly build a Logic Apps flow that subscribes to the agent''s `AppEvents` table, runs the complaint-detection regex (or a more sophisticated classifier), and creates a complaint-management workflow record for any matching event. (3) Each generated complaint record is reviewed by the Supervisory Principal within one business day for routing to the appropriate desk and inclusion in the next 4530(d) filing. (4) The CCO updates the SharePoint IR list with the workflow gap, the remediation, and the back-filing of the 4530(d) amendment.

**Prevention.** (1) Enumerate every customer-interaction surface (contact center, web chat, email, AI agents, Copilot extensions) and confirm each one is subscribed to the complaint-management workflow. (2) Build a quarterly Supervisory Principal control that compares the count of customer interactions per channel against the count of complaints generated; statistically-implausible mismatches (e.g., zero complaints in a high-volume channel) trigger investigation. (3) The complaint-detection classifier should be tuned at least quarterly using a sample of human-reviewed conversations to maintain precision and recall. (4) Cross-reference [Control 2.16 — RAG source integrity](../../../controls/pillar-2-management/2.16-rag-source-integrity-validation.md) for the related concern that the agent may be giving incorrect answers because the grounding sources are stale or wrong; complaints are an early-warning telemetry signal for that scenario.

**Regulatory-evidence implications.** FINRA Rule 4530(d) requires firms to report statistical information about written customer complaints quarterly. The amended filing, the immutable record of the workflow gap and remediation, and the new automated classifier together support the firm''s ability to demonstrate that the gap has been identified and closed. The 4530(d) amendment is the operative regulatory artifact; the platform telemetry is the contemporaneous evidence supporting it. This pattern supports — but does not substitute for — the firm''s separate determinations under FINRA Rule 4530(a)–(c) (event-driven reporting), which are made by the CCO and Supervisory Principal.

---

## §9 Scenario 8 — State breach-notification triage failed (stale residency map)
**Symptom.** Following a confirmed unauthorized access to customer NPI, the Privacy Officer attempts to determine which US state breach-notification statutes apply. The firm''s "customer-residency map" — a Power BI dashboard that aggregates customer-state from the master CRM — shows zero customers in three states that the firm in fact services. The Privacy Officer''s triage produces an under-inclusive list of state-AG submissions, which would be discovered later by a state AG cross-checking with the CRM directly.

**Likely cause.** The customer-residency map''s underlying dataflow has been failing for several refresh cycles. The dashboard displays a "last refreshed" timestamp that is two weeks old, but the privacy team did not have a SLA monitor on the dataflow and did not notice. Separately, the firm acquired a small affiliate eight months ago whose customer base has not been integrated into the master CRM and is therefore absent from the map entirely.

**Diagnostic steps.**

*Portal:* Open `https://app.powerbi.com` → the customer-residency dashboard → **Refresh history** in the dataset settings. Confirm the last successful refresh timestamp and the failure reason for any subsequent attempt. Open the master CRM → run an ad-hoc state-distribution query to compare against the dashboard.

*PowerShell:* The firm''s Privacy team typically runs `Get-Agt34IrListItem -ItemId <id>` to confirm the IR record''s `CustomerStateScope` field, then cross-references against an out-of-band CRM query to validate the field. If the IR record was populated from the stale dashboard, the field is wrong.

**Resolution.** (1) The Privacy Officer immediately runs a fresh ad-hoc state-distribution query directly against the master CRM (and against the affiliate''s separate CRM, if not yet integrated) and updates the IR record''s `CustomerStateScope` field. (2) Per-state breach-notification submissions are triaged based on the corrected scope, with explicit attention to the state statutes that have shorter clocks than Reg S-P''s 30 days (see Scenario 25 for state-AG portal mechanics). (3) The Privacy Officer files a clock-log entry recording the corrected scope and the rationale: `Invoke-Agt34RegulatorClockLog -Trigger "state-residency-corrected" -Determination <utc> -Notes "Original scope based on stale BI dashboard (refresh failed <utc>); corrected via direct CRM query at <utc>"`. (4) The CISO and the BI team open a remediation ticket to fix the dataflow, add SLA monitoring, and integrate the affiliate''s CRM into the master.

**Prevention.** (1) Add an automated SLA monitor on the customer-residency dataflow with paging to the BI on-call team if a refresh fails twice in succession. (2) Annual privacy-program audit includes a "ground-truth" comparison of the dashboard against direct CRM queries; any discrepancy of >0.5% triggers investigation. (3) Acquired-entity integration runbook explicitly includes "integrate customer base into master CRM and into customer-residency dashboard" as a Day-30 milestone; until then, the privacy team treats the acquired entity''s customers as a separate scope. (4) Run a state-residency tabletop (Scenario 16) at least annually that exercises both the BI dashboard and the direct CRM query path.

**Regulatory-evidence implications.** State AGs frequently cross-check breach-notification submissions against publicly-available signals (the firm''s state-presence disclosures in 10-K, ALM-securities filings, branch-locator data, ad spend by state). An under-inclusive state-AG submission set is detectable and creates regulatory risk. The corrected-scope clock-log entry, the remediation ticket, and the affiliate-integration milestone together support the firm''s ability to demonstrate that the gap has been identified and closed. This pattern supports — but does not substitute for — the firm''s determinations under each state breach-notification statute, which are made by the Privacy Officer and the GC.

---

## §10 Scenario 9 — Sentinel Logic Apps "suspend agent" RBAC failure
**Symptom.** During a Sev 1 incident, the Sentinel automation rule "Suspend agent service principal on credential-abuse alert" fires as designed and triggers the associated Logic App. The Logic App''s Microsoft Graph action that calls `PATCH /servicePrincipals/<id>` with `accountEnabled: false` returns an HTTP `403 Forbidden`. The agent service principal remains enabled and continues to be usable by the threat actor for several minutes until a human Entra Identity Admin manually disables it.

**Likely cause.** The managed identity backing the Logic App has the `Microsoft Sentinel Responder` role on the workspace (correct for incident manipulation) but does not have any Entra ID-side role that permits modifying the `accountEnabled` property of an arbitrary service principal. Modifying that property requires either Entra Application Administrator or Cloud Application Administrator (with the additional limitation that the SP being modified is owned by the principal making the call), or a more powerful role like Global Administrator. Cross-reference [Control 1.11 — Conditional Access (workload identity policy)](../../../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md) — workload-identity Conditional Access can also block the operation if the Logic App''s sign-in does not satisfy the workload-identity policy.

**Diagnostic steps.**

*Portal:* Open the Logic App in `https://portal.azure.com` → **Run history** → the failing run → click the failed action. The action''s output displays the HTTP `403` status and the Microsoft Graph error body. Capture a screenshot.

*KQL:* Search Entra audit logs for the failed sign-in or for the absence of a successful API call:

```kusto
// IR-Record: <SP-IR-id>  Scenario: 9  Run-By: <upn>
AADServicePrincipalSignInLogs
| where TimeGenerated between (_windowStart .. _windowEnd)
| where ServicePrincipalId == "<logic-app-mi-object-id>"
| project TimeGenerated, ResultType, ResultDescription, ResourceDisplayName, ConditionalAccessStatus, AppliedConditionalAccessPolicies
| order by TimeGenerated desc
```

If `ResultType != 0`, the sign-in itself failed (Conditional Access). If sign-in succeeded but the Graph call returned `403`, the role assignment is the cause.

```kusto
AuditLogs
| where TimeGenerated between (_windowStart .. _windowEnd)
| where OperationName == "Update service principal"
| where InitiatedBy.app.servicePrincipalId == "<logic-app-mi-object-id>"
| project TimeGenerated, OperationName, Result, ResultReason, TargetResources
```

*PowerShell:* `Get-MgServicePrincipal -ServicePrincipalId <logic-app-mi> -Property AppRoleAssignments` followed by `Get-MgServicePrincipalAppRoleAssignment` enumerates the API permissions held by the managed identity. Compare against the documented requirement (`Application.ReadWrite.OwnedBy` at minimum, or `Application.ReadWrite.All` for cross-tenant agent inventories).

**Resolution.** (1) The Entra Identity Admin manually disables the agent service principal in the portal: `https://entra.microsoft.com` → **Applications → Enterprise applications** → the agent SP → **Properties** → toggle **Enabled for users to sign in** off. (2) The Sentinel Admin opens a change request to grant the Logic App''s managed identity the appropriate permission. The recommended pattern is: assign the managed identity the `Application.ReadWrite.OwnedBy` Microsoft Graph application permission, register the Logic App''s MI as an owner of every agent SP that the firm wants to be able to suspend automatically, and update the Conditional Access workload-identity policy to allow the MI to sign in from the Logic App service tag. (3) Verify the resolution by re-running the suspension flow against a test agent SP in a non-production environment. (4) Update the SharePoint IR record to capture (a) the human-disable timestamp, (b) the duration the agent remained enabled after the alert, (c) the RBAC root-cause finding, and (d) the planned remediation.

**Prevention.** (1) Test every Sentinel automation rule end-to-end at least quarterly against a representative test agent in a non-production environment; a containment automation that has never actually executed in production is a containment automation that may not work when needed. (2) The Sentinel Admin maintains an inventory of every Logic App used in incident response, with each app''s managed-identity object ID, assigned roles, and the date of the last end-to-end test. (3) Conditional Access workload-identity policies for incident-response Logic Apps should be reviewed against the policy''s impact on each automation rule before deployment; the workload-identity team and the Sentinel team should jointly own this review. (4) The change-management runbook for incident-response automation requires a `Test-Agt34AutomationE2E` dry-run script as a gate.

**Regulatory-evidence implications.** Examiners will ask about the duration between alert generation and effective containment. The IR record entries documenting (a) the automation failure, (b) the human containment, and (c) the post-incident remediation support the firm''s ability to demonstrate that containment SLAs are tracked and that gaps are identified and closed. Cross-reference [Control 1.7 — Comprehensive audit logging](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) — the audit-log evidence of the failed call and the subsequent successful manual disable is what supports the timeline reconstruction. This pattern supports — but does not substitute for — the firm''s containment SLA determinations.

---
## §11 Scenario 10 — Sentinel automation rule didn''t fire on a relevant alert
**Symptom.** A Sentinel analytics rule fires and produces an alert that should have been auto-routed to a SharePoint IR record by an automation rule, but the SharePoint IR list shows no new record. The alert is sitting in the Sentinel **Incidents** queue uncorrelated with any IR record, and the on-call SOC analyst notices it only during the next shift change.

**Likely cause.** Several common patterns: (a) the automation rule''s trigger condition (typically a tag or a tactic match) doesn''t match the alert''s actual properties; (b) the automation rule is attached to a specific analytics rule and the alert was produced by a different analytics rule; (c) the automation rule is in a disabled state because it failed during an earlier run and was manually disabled by a Sentinel Admin; (d) the Logic App associated with the automation rule has a syntax error in the SharePoint connector and is throwing exceptions before the SharePoint create operation; (e) the automation rule was created in the wrong Sentinel workspace (a common mistake when the firm operates multiple workspaces for production / non-production / different business units).

**Diagnostic steps.**

*Portal:* Open `https://portal.azure.com` → Microsoft Sentinel → the workspace → **Configuration** → **Automation**. Locate the rule and check its **Status** (Enabled / Disabled), **Order**, and **Trigger** properties. Open the rule and review the **Conditions** tab to confirm that the alert''s properties would match. Open **Run history** to see whether the rule has fired recently and what the outcome was.

*KQL:* Confirm whether the automation rule fired at all:

```kusto
// IR-Record: <SP-IR-id>  Scenario: 10  Run-By: <upn>
SentinelHealth
| where TimeGenerated between (_windowStart .. _windowEnd)
| where OperationName == "Automation rule run"
| where Description contains "<rule-name-fragment>"
| project TimeGenerated, OperationName, Status, Description, Reason, ExtendedProperties
| order by TimeGenerated desc
```

If `Status == "Failed"`, the `Reason` and `ExtendedProperties` columns explain why. If no rows are returned, the rule never evaluated against this alert — meaning either the rule''s conditions excluded the alert, the rule is disabled, or the rule is in a different workspace.

*PowerShell:* `Get-AzSentinelAutomationRule -ResourceGroupName <rg> -WorkspaceName <ws>` enumerates every automation rule in the workspace and returns its conditions, actions, and enable state. Cross-reference the conditions against the alert''s properties to identify the mismatch.

**Resolution.** (1) The on-call SOC analyst manually creates the SharePoint IR record and links the alert. (2) The Sentinel Admin diagnoses the mismatch — using the diagnostics above — and fixes the automation rule. Common fixes: (a) broaden the rule''s tactic-match condition; (b) attach the rule to all relevant analytics rules rather than to a specific one; (c) re-enable a rule that was manually disabled, after addressing the underlying Logic App error; (d) fix the Logic App syntax; (e) move the rule to the correct workspace. (3) The Sentinel Admin re-runs the automation rule manually against the alert (Sentinel **Automation** → the rule → **Run** → select the alert) to confirm the fix works end-to-end. (4) Update the SharePoint IR list with the gap, the diagnostic findings, and the remediation.

**Prevention.** (1) Maintain an inventory of every Sentinel analytics rule mapped to its expected automation rule, owned by the Sentinel Admin. Quarterly review the inventory against the live workspace configuration to catch drift. (2) Build a `Test-Agt34AutomationCoverage` script that, given a list of analytics rules, identifies which have no associated automation rule or have automation rules that have not run in the last 30 days; route the report to the Sentinel Admin weekly. (3) Build a `SentinelHealth` watchlist analytics rule that pages the Sentinel on-call when an automation rule fails twice in succession or when an analytics rule fires but no automation rule runs within 5 minutes. (4) Disable rules through code-managed deployment (Bicep, Terraform) rather than through the portal so that the configuration is auditable and any manual portal change is detectable.

**Regulatory-evidence implications.** The IR record documenting the gap, the SentinelHealth evidence of the failure mode, and the remediation steps support the firm''s ability to demonstrate that the SOC processes are subject to continuous monitoring and that gaps are identified and closed. Cross-reference [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) for the underlying audit-logging requirements that the SentinelHealth table satisfies.

---

## §12 Scenario 11 — Purview Insider Risk Management case stuck pseudonymized
**Symptom.** A Purview Insider Risk Management policy fires on an agent-related signal (an employee''s frequent use of an AI agent to summarise sensitive deal documents in patterns inconsistent with their role). The IRM case is created in pseudonymised form (the user''s identity is replaced with an anonymous identifier per Purview''s default configuration). For two days, the IRM Investigator is unable to unmask the user because the unmask workflow requires HR + Legal joint sign-off and the routing has stalled in the IRM Analyst''s inbox.

**Likely cause.** The unmask workflow (a Power Automate flow triggered by an IRM Investigator''s "request unmask" action) routes to a single named HR partner who is on vacation. There is no backup approver and no escalation timer.

**Diagnostic steps.**

*Portal:* Open `https://purview.microsoft.com` → **Insider risk management** → **Cases** → the pseudonymised case. The case header shows the case ID, the policy that triggered it, the case priority, and the days-open count. Click **Activity log** to see whether an unmask request has been filed and what its status is.

Open `https://make.powerautomate.com` → **My flows** → the unmask-approval flow → **Run history** → the relevant run. The run history shows where the approval has stalled (typically in an "Approve or Reject — Wait for an approval" step).

*PowerShell:* `Get-Agt34PurviewIrmCase -CaseId <id>` returns the case in pseudonymised form along with the unmask-request status and the routing chain. The output supports a "where is the approval stuck" diagnostic.

**Resolution.** (1) The IRM Analyst contacts the HR partner''s backup (typically the HR partner for the same business unit, if one exists, or the head of HR). The backup reviews the unmask request, considers the case context, and approves or rejects per the same standards the original approver would apply. (2) The IRM Investigator proceeds with the unmasked case and follows the IRM playbook for confirmed insider-risk events (HR consultation, manager notification if appropriate, supervisory file annotation, employee meeting if appropriate). (3) The IRM Analyst updates the unmask-approval flow to add an escalation timer (e.g., re-route to backup approver after 24 hours of inactivity) and a backup-approver designation per HR partner.

**Prevention.** (1) Every named approver in incident-response and IRM workflows should have a designated backup; the Power Automate approval action supports `Approver` lists with `Approve from any` semantics. (2) An escalation timer (typically 24 hours) on every approval action ensures stalled approvals are flagged before they become a regulatory issue. (3) IRM workflow runbook includes a quarterly "approver inventory" review against the firm''s active HR partner list; departures and role changes are reflected within 30 days. (4) IRM tabletop exercises (Scenario 16) include a stalled-approver scenario.

**Regulatory-evidence implications.** While IRM cases themselves do not typically have a regulatory clock attached, the pseudonymisation-and-unmask design pattern supports the firm''s GLBA Safeguards Rule and Reg S-P obligations to limit access to NPI to those with a need to know. Maintaining the dual-control unmask workflow, with appropriate backups and escalation, supports the firm''s ability to demonstrate that the access-control framework is operating. The Power Automate run history is the contemporaneous record. Cross-reference [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) and [Control 1.9 — Data retention](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md).

---

## §13 Scenario 12 — eDiscovery Premium legal hold not propagating
**Symptom.** Following an incident, the GC''s office issues a legal-hold notification through eDiscovery Premium covering the relevant custodians (the on-call SOC analysts, the Incident Commander, the agent service principal''s mailbox, the SharePoint sites associated with the affected agent, and several Teams channels). 24 hours later, the eDiscovery Manager runs a hold-status report and finds that the hold did not propagate to two custodians'' OneDrive accounts and one Teams chat.

**Likely cause.** Several common patterns: (a) the custodian was added to the case but their OneDrive location was not added as a hold location; (b) the OneDrive site URL changed (the user changed display name) and the cached URL in the hold is now invalid; (c) the Teams chat is a 1:1 chat that is not hold-eligible without explicit configuration; (d) a transient Microsoft Graph throttling error caused the hold-application step to fail silently for some custodians; (e) the eDiscovery Manager''s account does not have sufficient permissions on the destination location and the hold cannot be applied.

**Diagnostic steps.**

*Portal:* Open `https://purview.microsoft.com` → **eDiscovery → Premium** → the case → the **Holds** tab → the hold → **Statistics**. The statistics tab shows, per custodian, the count of items held and the per-location status (Active / Failed / Pending). Failed locations show a per-location error message.

*PowerShell:* `Get-Agt34LegalHold -CaseId <id>` returns the per-custodian, per-location status with the last-evaluated timestamp. The output supports a "which custodians and which locations are in failed state" diagnostic. Cross-reference against `Get-CaseHoldPolicy` and `Get-CaseHoldRule` from the Security & Compliance PowerShell module for additional detail.

**Resolution.** (1) The eDiscovery Manager addresses each failed location: re-add the custodian if missing, refresh the cached URL, explicitly configure 1:1 Teams chat retention if the policy permits, retry the hold-application step for any throttling-induced failure, escalate to the M365 Admin for permission grants where required. (2) Re-run the hold-status report and confirm all locations show Active. (3) Notify the GC of the gap and the remediation; the GC determines whether the gap window (between hold issuance and effective application) requires any additional action under FRCP 37(e) or applicable spoliation doctrine. (4) Update the SharePoint IR record with the hold-status report (initial and post-remediation) and the GC''s notification.

**Prevention.** (1) The eDiscovery Manager runs `Get-Agt34LegalHold -CaseId <id>` at 1 hour, 4 hours, and 24 hours after every hold issuance and posts the result to the case Teams channel; gaps are identified and remediated within hours rather than days. (2) Maintain a "hold-eligible locations checklist" per typical-custodian template (SOC analyst, incident commander, agent SPN mailbox, SharePoint site, Teams channel, Teams 1:1 chat, OneDrive, mailbox archive); the GC and eDiscovery Manager confirm the checklist is fully populated when a hold is issued. (3) Enable Microsoft Graph telemetry export to Sentinel and build an analytics rule that fires when a hold-application step throws an error; route to the eDiscovery on-call. (4) Quarterly eDiscovery review confirms hold-status stability across all open cases.

**Regulatory-evidence implications.** SEC Rule 17a-4(f) requires broker-dealers to preserve electronic records in a non-rewritable, non-erasable format for the prescribed retention period; FINRA Rule 4511 incorporates the requirement. The legal hold is an additional, examiner-facing assurance that documents will be preserved for litigation or regulatory examination. The hold-status reports, the gap-remediation log, and the GC notification together support the firm''s ability to demonstrate that the preservation framework is operating. Cross-reference [Control 1.9 — Data retention](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md).

---
## §14 Scenario 13 — Service Health correlated outage after RCA
**Symptom.** The firm closes the RCA on an agent incident with a stated root cause of "service-principal credential exposure due to misconfigured Logic App connection." Three days later, Microsoft publishes a Service Health post-incident report describing a global Microsoft Sentinel connector outage that overlapped the incident window and produced symptoms similar to those the firm observed. The Incident Commander now must determine whether to reopen the RCA, amend prior regulator submissions, and update the customer-notice narrative.

**Likely cause.** The Microsoft 365 Service Health timeline is the authoritative source for platform-side incidents, but its post-incident reports are typically published days after the underlying event. A firm RCA closed before Microsoft publishes its report is closed on incomplete information.

**Diagnostic steps.**

*Portal:* Open `https://admin.microsoft.com` → **Health → Service health** → **History**. Filter by date range covering the incident window. Open any incident with overlap and read the Microsoft post-incident report (PIR). Capture the PIR as a PDF and store in the immutable evidence container.

*PowerShell:* `Get-Agt34ServiceHealth -StartUtc <window-start> -EndUtc <window-end>` returns every Service Health incident, advisory, and PIR in the window with the affected services, the Microsoft incident ID, the start / end times, and the PIR URL. Run this cmdlet (a) at incident close, (b) at RCA close, and (c) on a 30-day post-close cadence to catch late PIR publications.

**Resolution.** (1) The Incident Commander reopens the RCA in the SharePoint IR list with status `Reopened — Microsoft PIR published`. (2) The Incident Commander, the Sentinel Admin, and the Service Owner jointly assess whether the Microsoft PIR materially changes the firm''s root-cause finding. Possible outcomes: (a) the firm''s root cause is correct and the Microsoft PIR is unrelated; (b) the firm''s root cause is partially correct but the Microsoft outage was a contributing factor; (c) the firm''s root cause is incorrect and the Microsoft outage is the primary cause. (3) For outcomes (b) or (c), the CCO and GC determine whether prior regulator submissions require an amendment under the relevant rule''s "ongoing duty to update" provisions (e.g., NYDFS Part 500.17(a)(2) supplemental information requirement; SEC Reg S-K Item 1.05 amended 8-K). (4) Customer-notice narratives may also need amendment if previously-published narratives are now misleading. (5) The reopened RCA is closed only after the assessment is complete and any required amendments are filed.

**Prevention.** (1) Build a 30-day-post-close watchlist of every closed RCA''s `Get-Agt34ServiceHealth` query, automatically re-run by an Azure Automation runbook; route any new overlapping PIR to the relevant Incident Commander. (2) The RCA-close template in the SharePoint IR list includes a checklist item "Microsoft Service Health checked at close — no overlapping PIR found" with timestamp; this becomes the baseline for the 30-day re-check. (3) The Incident Commander handoff to "incident closed" includes a 30-day reopen-evaluation milestone that auto-creates a Planner task. (4) Annual tabletop exercises (Scenario 16) include a late-PIR scenario.

**Regulatory-evidence implications.** Most regulatory regimes have an "ongoing duty to update" obligation when material information changes after a notification has been filed. NYDFS Part 500.17(a)(2) is explicit; SEC Reg S-K Item 1.05 contemplates 8-K amendments. The 30-day reopen-evaluation milestone, the Microsoft PIR record, and any amended submissions together support the firm''s ability to demonstrate good-faith compliance with the ongoing duty. The decision log entries for the reopen evaluation are examiner-relevant and must reference the Microsoft PIR.

---

## §15 Scenario 14 — Defender XDR / Sentinel incident JSON export missing fields
**Symptom.** A regulator (NYDFS, SEC, OCC, FINRA, or CFTC) requests the firm''s incident-investigation file. The firm''s prepared package includes a Defender XDR / Sentinel incident JSON export, but the export is missing fields the examiner specifically requested: the per-alert evidence linkage, the entity graph adjacency, the activity log with system-vs-user attribution, the raw KQL queries with results, the assigned analyst''s investigation comments, and the Logic App run history for any automation rule that fired on the incident.

**Likely cause.** The portal''s default **Export to JSON** action exports the incident header plus a summary of constituent alerts but does not include (a) the full alert evidence per the `AlertEvidence` table, (b) the investigation graph as a serialised structure, (c) the activity log, (d) the raw KQL with results, (e) analyst comments, or (f) Logic App run history. The complete examiner-facing package requires multiple distinct export operations.

**Diagnostic steps.**

*Portal:* Open `https://security.microsoft.com` → **Incidents** → the incident → click **Export**. Compare the exported JSON against the required field list. The portal-only export will be missing several required fields.

*PowerShell:* `Get-Agt34Incident -IncidentId <id>` and `Get-Agt34SentinelIncident -IncidentNumber <id>` together produce the complete examiner-facing package, including all fields listed above. The cmdlets call the supported Microsoft Graph Security API and Microsoft Sentinel REST API endpoints to assemble the package.

**Resolution.** (1) Re-run the examiner-facing package using the cmdlets above; verify the package contains every required field. (2) Run a SHA-256 over the package and record in the SharePoint IR record. (3) Provide the package to the regulator with a cover letter from the GC describing the contents, the timestamps of the underlying source data, and the firm''s chain-of-custody attestations. (4) Update the SharePoint IR record with the examiner request, the package, the cover letter, and the SHA-256.

**Prevention.** (1) Treat the cmdlet-based examiner-facing package as the *default* export, not the portal-based JSON. The Sentinel Admin runs the cmdlet at every Sev 1 incident close and stores the package in the immutable evidence container. (2) The package format is versioned; changes are backward-compatible whenever feasible so that older incidents'' packages remain comparable to newer ones. (3) Quarterly examiner-readiness review compares a sample of stored packages against the most current required-field list; gaps are remediated by re-running the cmdlet against the source incident. (4) Maintain a "examiner-package field requirements" matrix per regulator (NYDFS, SEC, OCC, FRB, FDIC, FINRA, CFTC, state AGs) and update at least annually.

**Regulatory-evidence implications.** A complete and reproducible examiner-facing package is the principal artifact the firm relies on to demonstrate the contents and the integrity of its incident response. The cmdlet-based package and the SHA-256 chain-of-custody record support the firm''s ability to demonstrate that the package contents are authentic and contemporaneous. Cross-reference [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) for the underlying audit-log requirements.

---

## §16 Scenario 15 — SharePoint IR list field validation broken
**Symptom.** During a routine RCA-completeness audit, the Records Officer discovers that several IR records in the past quarter were closed (status set to `Closed — RCA complete`) without a value in the `RcaNarrative` field. The SharePoint list''s field-validation rule (which should require a non-empty `RcaNarrative` for `Status == "Closed — RCA complete"`) does not appear to be enforcing.

**Likely cause.** The list-level validation rule was inadvertently disabled when a M365 Admin migrated the list schema to add new columns. The Power Automate workflow that should also enforce the requirement (by failing the close action if the narrative is empty) was modified to remove the check during a previous troubleshooting session and was never restored.

**Diagnostic steps.**

*Portal:* Open the SharePoint IR list → **Settings → List settings → Validation settings**. Confirm the validation formula and that the rule is enabled. The expected formula references `RcaNarrative` and `Status`. If the formula field is empty or the rule is disabled, the gap is confirmed.

Open `https://make.powerautomate.com` → **My flows** → the IR-close approval flow → the action that validates the close request. Confirm the validation step exists; if missing, restore from the version history.

*PowerShell:* `Get-Agt34IrListItem -ItemId <id>` returns the list item plus the list''s schema and validation settings. Compare against the source-of-truth schema documented in [`portal-walkthrough.md`](portal-walkthrough.md). Cross-reference against the OOTB SharePoint list-settings export (`Get-PnPList | Get-PnPProperty Validation`).

**Resolution.** (1) The M365 Admin restores the list-level validation rule from the documented schema. (2) The Power Platform Admin restores the Power Automate validation step from version history. (3) The Records Officer audits every IR record closed since the gap was introduced (use the IR list view filter `Status == "Closed — RCA complete" AND RcaNarrative IS BLANK`) and routes each to the original Incident Commander for narrative back-fill within 5 business days. (4) The completed records are re-closed; the re-close action records the back-fill timestamp and the original closer''s attestation that the narrative reflects the contemporaneous understanding. (5) The Records Officer files a memo in the SharePoint IR list describing the gap, the remediation, and the back-fill outcome.

**Prevention.** (1) The IR list schema is defined in source control (PnP Provisioning Engine template or SPFx site script) and applied via deploy pipeline; manual schema changes are detected by a daily drift-check script. (2) Power Automate flows used in incident response are exported and stored in source control; changes go through PR review with the Records Officer and the M365 Admin as required reviewers. (3) Quarterly RCA-completeness audit by the Records Officer re-validates the schema and the Power Automate flows. (4) Add a Sentinel analytics rule (low-severity) that fires when a SharePoint IR list close event occurs without a populated `RcaNarrative`; route to the Records Officer queue.

**Regulatory-evidence implications.** RCA narratives are the firm-facing evidence that the incident has been investigated to root cause, that corrective actions have been identified, and that the firm has the institutional learning to prevent recurrence. Examiners will sample RCA narratives during examinations and will look for evidence of consistent quality. The schema-restoration record, the back-fill memo, and the source-control history of the IR list and the Power Automate flow together support the firm''s ability to demonstrate that the RCA process is operating as designed. Cross-reference [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md).

---
## §17 Scenario 16 — Tabletop reveals 72h discovery vs determination
**Symptom.** During the firm''s annual incident-response tabletop exercise, the moderator presents a scenario in which the SOC observes anomalous agent behaviour at `T0`, the Sentinel Admin escalates to Incident Commander at `T0+30min`, the Incident Commander declares Sev 1 at `T0+1h`, and the duty CCO determines that the event meets the NYDFS Part 500.17(a) threshold at `T0+8h`. When asked to identify the start of the 72-hour clock, the participating CCO and Sentinel Admin name `T0` (the discovery timestamp); the participating GC and Outside Counsel name `T0+8h` (the determination timestamp). The disagreement is unresolved at the end of the exercise.

**Likely cause.** The runbook does not contain a clearly-articulated, plain-English statement of which timestamp starts the regulatory clock for each applicable rule. NYDFS Part 500.17(a), as amended in November 2023, runs the 72-hour clock from "after a determination has been made that a Cybersecurity Event has occurred" — a determination, not a discovery. The team has been operating on the more conservative discovery timestamp because it produces an earlier deadline and was mistakenly assumed to satisfy the rule''s text.

**Diagnostic steps.**

*Document review:* Open the firm''s incident-response runbook → the regulatory-clock section. Identify whether each applicable rule (NYDFS 500.17(a), SEC Reg S-K Item 1.05, banking 36-hour rule, Reg S-P §248.30, FINRA 4530, OFAC, CIRCIA) has a plain-English statement of (a) the trigger event and (b) which timestamp starts the clock. Many runbooks conflate "discovery" and "determination."

*Tabletop transcript:* Read the moderator''s after-action report. Identify each disagreement among participants and trace each disagreement to a runbook ambiguity.

*PowerShell:* `Invoke-Agt34RegulatorClockLog -List` returns the full clock-log history with the trigger and determination timestamps. If past entries show a discovery-style timestamp where a determination-style timestamp would have been more accurate, the runbook ambiguity has affected operational practice.

**Resolution.** (1) The CCO, the GC, Outside Counsel, and the Sentinel Admin jointly draft a "regulatory clock primer" appendix to the runbook, with one row per applicable rule, listing the trigger event, the operative phrase from the rule''s text, the timestamp source, the responsible decision-maker, and the canonical clock-log `Trigger` value. (2) The CCO updates the `Invoke-Agt34RegulatorClockLog` reference documentation to map every authorised `Trigger` value to a primer row. (3) The Sentinel Admin updates the SharePoint IR list to add a `DeterminationUtc` field (distinct from the existing `FirstObservedUtc`) and updates the Power Automate flows accordingly. (4) The next quarterly tabletop re-tests the discovery-vs-determination scenario; participants are expected to identify the determination timestamp.

**Prevention.** (1) The regulatory clock primer is reviewed annually by the CCO, GC, and Outside Counsel jointly and updated whenever a relevant rule is amended (e.g., NYDFS 500 amendments in 2023, SEC Reg S-K Item 1.05 in 2023, Reg S-P amendment in 2024, CIRCIA rulemaking in 2025–2026). (2) Every IR record at Sev 1 declaration auto-creates a clock-log preview for each potentially-applicable trigger, prompting the CCO to either confirm the trigger or document why it doesn''t apply. (3) Tabletop exercises (run at least quarterly for sub-scenarios, annually for full incident response) include a scenario specifically testing discovery-vs-determination distinctions. (4) New CCO / SOC analyst onboarding includes a 1-hour module on the regulatory clock primer.

**Regulatory-evidence implications.** The regulatory clock primer is itself an examiner-facing artifact that supports the firm''s ability to demonstrate that the incident-response program has institutional knowledge of the operative regulatory clocks. The clock-log entries with explicit `Trigger` values, the SharePoint IR list `DeterminationUtc` field, and the tabletop after-action reports together support the firm''s ability to demonstrate that the program operates per the primer. This pattern supports — but does not substitute for — the firm''s rule-by-rule determinations, which are made by the CCO, GC, and where relevant Outside Counsel based on facts and circumstances.

---

## §18 Scenario 17 — OFAC sanctions screening missed in an extortion-payment scenario
!!! danger "OFAC sanctions screening"
    The decision whether to make a payment to a threat actor in response to extortion or ransomware demand is governed by the Office of Foreign Assets Control (OFAC) sanctions regime, including (a) the Specially Designated Nationals and Blocked Persons List (SDN List), (b) the OFAC 50% Rule (entities owned 50% or more, in the aggregate, by sanctioned persons are themselves blocked), and (c) the broader prohibitions of the International Emergency Economic Powers Act (IEEPA). OFAC''s 2020 and 2021 advisories on ransomware payments make clear that payments to sanctioned actors — even payments made under coercion or for the purpose of recovering business operations — may constitute sanctions violations and may be subject to civil or criminal enforcement. **A payment to a sanctioned actor is not made compliant by post-payment screening.** OFAC screening must be completed *before* any payment instruction is issued, and the screening evidence must be preserved in the firm''s records. This playbook describes the screening *workflow* the firm uses; it does not constitute legal advice on whether a particular payment is permitted, which determination is made by the GC and Outside Counsel in consultation with the CFO and the firm''s OFAC Screening Officer.

**Symptom.** A threat actor demands a cryptocurrency payment to release encrypted firm data. The CFO, under pressure from business leadership, begins to coordinate the payment with the firm''s incident-response retainer, but the GC discovers — three hours into the payment workflow — that no documented OFAC screening of the payment address or of the threat-actor identifiers (TOR onion URL, email handle, ransom-note signature) has been performed.

**Likely cause.** The firm''s incident-response runbook contemplates ransom payments as a low-likelihood scenario and does not include a hard gate requiring OFAC screening before any payment-coordination step. The OFAC Screening Officer (a Compliance role) is not on the on-call rotation for cyber incidents.

**Diagnostic steps.**

*Document review:* Open the incident-response runbook and the firm''s extortion-response playbook (if separate). Confirm whether (a) OFAC screening is a documented gate, (b) the OFAC Screening Officer is on the on-call rotation or otherwise contactable within hours, (c) the firm has a documented OFAC screening procedure including which lists are checked, who performs the screening, and how the result is recorded.

*PowerShell:* `Test-Agt34OfacScreening -PaymentAddress <btc-address> -Counterparty @{ TorUrl = "<url>"; Email = "<handle>"; NotePattern = "<sha256>" }` performs the screening using the firm''s configured OFAC service (typically Refinitiv World-Check, Dow Jones Risk & Compliance, or a US Treasury-licensed equivalent) and returns the result with timestamp, screening service, list version, and SHA-256 of the result. The cmdlet records the screening to an immutable JSON log irrespective of result. **The cmdlet does not make a determination** — it provides the screening evidence that the GC and OFAC Screening Officer rely on.

**Resolution.** (1) The GC immediately halts the payment-coordination workflow. (2) The OFAC Screening Officer is paged and runs `Test-Agt34OfacScreening` against the payment address and every threat-actor identifier captured in the incident; the result is reviewed jointly by the OFAC Screening Officer, the GC, and Outside Counsel. (3) If the screening produces a hit, a partial match, or any ambiguity (Scenario 23), the payment workflow remains halted pending counsel determination. (4) If the screening is clean, the GC confirms in writing — with reference to the screening evidence — whether the payment may proceed; the determination is recorded in the immutable decision log with the GC''s electronic signature. (5) Regardless of payment outcome, the SharePoint IR record captures every screening result, the determination memo, and the contemporaneous timestamps. (6) The CFO files any required reporting (FinCEN SAR for any cryptocurrency transaction over the reporting threshold; OFAC voluntary self-disclosure if applicable).

**Prevention.** (1) Update the incident-response runbook and the extortion-response playbook to add OFAC screening as a hard gate before any payment-coordination step; the gate is enforced by a Power Automate approval action requiring the OFAC Screening Officer''s electronic signature. (2) Add the OFAC Screening Officer to the cyber on-call rotation with a documented escalation path. (3) Maintain the OFAC screening service configuration in `agt34.config.json` with the service URL, the API key reference (Azure Key Vault), and the list-coverage attestation. (4) Annual extortion-response tabletop exercises include the OFAC screening gate.

**Regulatory-evidence implications.** OFAC enforcement actions for inadequate screening can include civil penalties (with maxima per violation that vary by sanctions program) and, in egregious cases, criminal referral. The screening evidence — the cmdlet log, the OFAC Screening Officer''s attestation, the GC''s determination memo, the immutable decision log entries — is the firm''s primary defence against an OFAC enforcement action arising from a ransom payment. This playbook describes the workflow; the underlying determination of whether a payment is permitted is made by the GC and Outside Counsel and is not a function of platform configuration. Cross-reference [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) for the underlying audit-log requirements.

---

## §19 Scenario 18 — Cyber-insurance carrier not notified within policy window
**Symptom.** The firm''s Risk Officer discovers, during a post-incident insurance review, that the firm''s cyber-insurance carrier was notified of a Sev 1 incident on day 4, but the policy''s notification clause requires notice within 48 hours of the firm''s awareness. The carrier reserves the right to deny coverage for incidents not noticed within the policy window. The firm''s out-of-pocket exposure may now include the legal, forensic, regulatory, and customer-notification costs that the policy was intended to cover.

**Likely cause.** The incident-response runbook does not include a hard gate requiring cyber-insurance notification within the policy window, and the Risk Officer is not on the cyber on-call rotation. The CCO and GC focused on regulatory clocks (NYDFS, banking 36h, SEC) and did not cross-reference the insurance policy.

**Diagnostic steps.**

*Document review:* Open the firm''s cyber-insurance policy declarations page and the policy''s notification clause. Identify the operative window (typically 24–72 hours), the notification method (typically a dedicated carrier email + phone hotline), and any specific information the notification must contain.

*PowerShell:* `Get-Agt34IrListItem -ItemId <id>` returns the IR record''s `InsuranceNotification` sub-collection. If the sub-collection is empty or the timestamp postdates the policy window, the gap is confirmed.

**Resolution.** (1) The Risk Officer immediately notifies the carrier in writing with a full description of the firm''s timeline, including the discovery, determination, regulatory submission, and notification timestamps; the notice acknowledges the late notification and requests the carrier''s reservation-of-rights position. (2) The GC engages outside insurance coverage counsel to negotiate with the carrier on the late-notice issue; potential arguments include (a) the policy''s notification clause is a condition rather than a covenant; (b) the carrier suffered no prejudice from the late notification; (c) the carrier had constructive notice through industry information-sharing or media coverage. (3) The Risk Officer updates the SharePoint IR record with the carrier notification, the carrier''s response, and the coverage-counsel engagement. (4) The CFO updates financial-reporting accruals to reflect the contingent uninsured exposure.

**Prevention.** (1) Add cyber-insurance notification as a hard gate in the incident-response runbook with a SLA of 24 hours from Sev 1 declaration (well within typical policy windows). (2) Add the Risk Officer (or a designated alternate) to the cyber on-call rotation. (3) Maintain a "regulatory-and-contractual notification matrix" per incident severity that lists every required notification (regulators, insurance carriers, key customers per master agreement, contracted vendors per their security riders) with the operative window and the responsible role. (4) Annual incident-response tabletop exercises include a cyber-insurance notification step. (5) Annual insurance-program review by the Risk Officer and the CFO includes a runbook-vs-policy reconciliation.

**Regulatory-evidence implications.** While cyber-insurance notification is not a regulatory requirement per se, the insurance-coverage outcome materially affects the firm''s financial position and may itself be disclosable under SEC Reg S-K Item 1.05 (impact analysis) and under SOX 404 ICFR (Scenario 19) if the uninsured exposure is material. The reservation-of-rights letter and the coverage-counsel engagement record should be preserved in the immutable evidence container.

---
## §20 Scenario 19 — SOX 404 material weakness Audit Committee not briefed
**Symptom.** An agent failure (an M365 Copilot agent producing materially-misstated draft financial-reporting analyses that were used by a controllership team for two reporting periods) crosses Internal Audit''s threshold for a SOX §404 ICFR material-weakness candidate. The next quarterly 10-Q is six weeks out and the Audit Committee has not yet been briefed. Without a timely briefing, the Audit Committee cannot fulfil its oversight obligations and the CFO and CEO cannot meaningfully sign the §302 / §906 certifications attached to the 10-Q.

**Likely cause.** The incident-response runbook treats agent incidents as IT / Security incidents, not as financial-reporting-control incidents. There is no escalation path from the SOC / Sentinel Admin / CCO to Internal Audit, the CFO, the Audit Committee Chair, and Outside Auditor when an agent failure has potential ICFR implications.

**Diagnostic steps.**

*Document review:* Open the firm''s SOX §404 control inventory and identify whether the affected agent is in scope as a control or as a control-supporting tool. Open the Internal Audit charter and confirm the materiality threshold for material-weakness candidates and the escalation path. Open the Audit Committee charter and confirm the meeting cadence and the emergency-meeting protocol.

*PowerShell:* `Get-Agt34IrListItem -ItemId <id>` returns the IR record''s `IcfrImpactAssessment` sub-collection (if the field is configured). If the sub-collection is empty for an agent that is in SOX scope, the assessment has not been performed.

**Resolution.** (1) The CCO and CFO immediately convene Internal Audit, Outside Auditor, the Audit Committee Chair, and the GC for an emergency briefing on the agent failure, the affected reporting periods, the magnitude of the potential misstatement, and the remediation plan. (2) Internal Audit performs a full ICFR impact assessment using the firm''s standard methodology (SAB 99 / SAB 108 quantitative and qualitative factors). (3) The Audit Committee, advised by Outside Auditor, determines whether the failure constitutes a material weakness, a significant deficiency, or a control deficiency that does not rise to either threshold. (4) The CFO and CEO determine, in consultation with Outside Counsel and the Disclosure Committee, whether the assessment requires disclosure in the next 10-Q (or, if material and timely, in an 8-K Item 4.02 restatement filing). (5) The remediation plan — including agent-design changes, additional manual review controls, and timelines — is documented and tracked.

**Prevention.** (1) The agent inventory (maintained per [Control 2.16 — RAG source integrity](../../../controls/pillar-2-management/2.16-rag-source-integrity-validation.md)) includes a SOX-scope flag per agent. (2) The incident-response runbook includes a hard gate at Sev 1 declaration: "If any agent in SOX scope is implicated, page Internal Audit and the CFO within 1 hour." (3) Internal Audit is added to the cyber on-call rotation as a 24h-callback secondary. (4) Annual ICFR-update review by the CFO and Internal Audit includes a "agent inventory + SOX scope" reconciliation. (5) Annual SOX tabletop exercise (separate from the cyber tabletop, Scenario 16) includes an agent-failure scenario.

**Regulatory-evidence implications.** SOX §302 / §906 certifications by the CEO and CFO are based on the design and operation of the firm''s ICFR. The Audit Committee briefing record, the Internal Audit assessment, the Outside Auditor concurrence, and the disclosure determination together support the certification. NYSE / Nasdaq listing rules require ongoing Audit Committee oversight of material risks, including cyber-incident-driven ICFR risks. Cross-reference [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) and the parent control [3.4](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md).

---

## §21 Scenario 20 — Sentinel retention expired before regulator inquiry
**Symptom.** A regulator (FINRA, SEC, CFTC) asks the firm to produce Sentinel data — specifically, `AADServicePrincipalSignInLogs` for the agent service principal and `OfficeActivity` for the affected user accounts — covering an incident window that occurred 18 months before the inquiry. The Sentinel Admin discovers that the workspace''s operational retention is configured for 90 days; archived retention extends to 2 years for some tables but only 6 months for others. The data is not directly queryable.

**Likely cause.** Sentinel''s retention model has two tiers: operational retention (default 90 days for Log Analytics workspaces, configurable up to 730 days per table) and archive retention (configurable up to 12 years per table). Tables that were not configured for archive retention beyond the requested window are no longer queryable. Even tables configured for archive retention require a "search job" or "data restore" operation to surface in queries — they are not directly hot-queryable.

**Diagnostic steps.**

*Portal:* Open `https://portal.azure.com` → Log Analytics workspace → **Tables**. Each table shows its **Total retention** (operational + archive) and **Archive period**. Identify which of the requested tables are still within total retention and which are not.

*PowerShell:* `Get-Agt34RetentionStatus -WorkspaceName <ws> -TableName <table>` returns the retention configuration and the earliest queryable timestamp per table. Run for each requested table.

**Resolution.** (1) For tables within archive retention but outside operational retention: open Sentinel **Search jobs** in `https://portal.azure.com`, configure a search job over the requested window, and surface the results to a queryable target table. Search jobs typically complete within 24 hours. Alternative: open **Data restore** to restore the archived data to a hot tier for a defined duration. (2) For tables outside total retention: the Sentinel data is not recoverable; the Records Officer must produce alternative evidence from the firm''s WORM-archived `OfficeActivity` (M365 records management) and from the immutable evidence container (which should contain a snapshot of the relevant logs from the original incident close, per §0.4). (3) The Sentinel Admin updates the SharePoint IR record with the search-job results, the data-restore record, or the alternative-evidence sources used to respond to the inquiry. (4) The GC files the response with the regulator, with a cover letter describing the data sources, the recovery method, and the firm''s chain-of-custody attestations.

**Prevention.** (1) The firm''s data-retention schedule (see [Control 1.9](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md)) maps each Sentinel table to a retention class based on the longest applicable regulatory retention period (typically SEC 17a-4(f) 6 years for broker-dealers, FINRA 4511 6 years, CFTC 1.31 5 years). The Sentinel Admin configures table-level archive retention to satisfy the schedule. (2) Tables with regulatory retention requirements are flagged in the Sentinel workspace inventory and reviewed quarterly for configuration drift. (3) The §0.4 evidence-collection pattern includes a snapshot of every regulatory-retention table''s relevant data into the immutable evidence container at incident close — this provides a directly-queryable alternative even if the live workspace retention has expired. (4) Annual records-management audit by the Records Officer includes a Sentinel-retention reconciliation against the data-retention schedule.

**Regulatory-evidence implications.** SEC Rule 17a-4(f) for broker-dealers, FINRA Rule 4511, and CFTC Rule 1.31 each require the preservation of certain electronic records in non-rewritable, non-erasable formats for the prescribed periods. While Sentinel itself is not the firm''s primary records-of-record system for these requirements (M365 records management plays that role), Sentinel data is frequently used in regulatory inquiries. The immutable evidence container, the data-retention schedule, and the search-job / data-restore records together support the firm''s ability to demonstrate that incident-investigation data is recoverable for the longest applicable retention period.

---

## §22 Scenario 21 — PII spill into Sentinel through Application Insights
!!! danger "PII spill — emergency remediation"
    A PII spill into a logging or monitoring system that was not designed for that data class is itself a regulatory event. Customer NPI in Sentinel custom logs may trigger Reg S-P (SEC §248.30), GLBA Safeguards Rule notification, state breach-notification statutes, and (where the data also includes payment-card information) PCI DSS incident-handling requirements. Treat a confirmed spill as a Sev 1 event in its own right with its own SharePoint IR record, its own clock log, and its own evidence-collection workflow per §0.4. Cross-reference [Control 1.7 — Comprehensive audit logging](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md), [Control 1.9 — Data retention](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md), and the parent control [3.4 (Reg S-P TC-7 trigger condition)](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md). **Do not attempt to "delete the data" through portal actions until the GC and Privacy Officer have formally instructed.** Premature deletion may itself constitute spoliation if the spill is the subject of a regulator inquiry; the standard remediation pattern is a controlled purge after evidence preservation, not an immediate delete.

**Symptom.** A Sentinel Admin running a routine cost / volume analysis on the workspace notices that an `AppEvents` table fed by an agent''s Application Insights instance is much larger than expected. Sampling shows that the agent''s host application is logging the full conversation transcript — user prompts and agent responses — to `Properties.text` rather than to a sanitised `Properties.text_metadata_only`. The transcripts contain customer names, account numbers, SSN fragments, and (in some cases) payment-card data.

**Likely cause.** A code change in the agent''s host application accidentally enabled "verbose" logging mode in production, or a developer added a temporary diagnostic logging statement and forgot to remove it. The Sentinel ingestion side accepts whatever the host application sends; there is no automated PII-detection step on ingestion.

**Diagnostic steps.**

*KQL:* Confirm the spill''s scope:

```kusto
// IR-Record: <SP-IR-id>  Scenario: 22  Run-By: <upn>
AppEvents
| where TimeGenerated between (_windowStart .. _windowEnd)
| where isnotempty(tostring(Properties.text)) and tostring(Properties.text) != tostring(Properties.text_metadata_only)
| extend hasPii = tostring(Properties.text) matches regex @"\b\d{3}-\d{2}-\d{4}\b|\b\d{4}[ -]?\d{4}[ -]?\d{4}[ -]?\d{4}\b"
| summarize SpilledRows = count(), AffectedConvos = dcount(ConversationId), FirstSeen = min(TimeGenerated), LastSeen = max(TimeGenerated) by hasPii
```

```kusto
// Identify which deployment / version of the host introduced the spill
AppEvents
| where TimeGenerated between (_windowStart .. _windowEnd)
| where isnotempty(tostring(Properties.text)) and tostring(Properties.text) != tostring(Properties.text_metadata_only)
| summarize FirstSeen = min(TimeGenerated) by AppRoleName, AppVersion, RoleInstance
| order by FirstSeen asc
```

*PowerShell:* `Get-Agt34RetentionStatus -WorkspaceName <ws> -TableName AppEvents` confirms the table''s retention; the spill data may also exist in the table''s archive tier and may need separate handling.

**Resolution.** (1) The Sentinel Admin opens a Sev 1 IR record for the spill itself. (2) The agent host''s development team rolls back the code change that enabled verbose logging or removes the temporary diagnostic statement; the rollback is verified by re-running the diagnostic KQL and confirming no new spilled rows appear after the rollback timestamp. (3) The Privacy Officer and GC determine, with reference to the spill''s scope and the affected data classes, which regulatory notifications are required (Reg S-P §248.30 individual-customer notice; state breach notifications; GLBA notification; PCI DSS notification if PCI data is in scope). (4) The Sentinel Admin, at the GC''s written instruction and *after* the evidence-collection workflow per §0.4 has produced a hash-recorded snapshot of the spilled data, executes a controlled purge of the spilled data using the Log Analytics workspace data-purge mechanism (`Invoke-AzOperationalInsightsPurge -ResourceGroupName <rg> -WorkspaceName <ws> -Table AppEvents -Filter @(...)`) — which Microsoft processes within 30 days — and records the purge request ID in the SharePoint IR record. (5) The CCO files the regulatory submissions per the duty CCO''s determination. (6) The agent''s Application Insights configuration is updated to enforce the metadata-only logging pattern; a Sentinel analytics rule is created to fire on any future row in `AppEvents` where `Properties.text != Properties.text_metadata_only`.

**Prevention.** (1) The agent host''s logging configuration is treated as a security-sensitive setting; changes are routed through the Sentinel Admin and the Privacy Officer for review prior to deployment. (2) A Sentinel analytics rule fires on any row where conversation content (rather than metadata) appears in `AppEvents`; this is a continuous detective control. (3) The agent CI/CD pipeline includes a static-analysis check for verbose-logging statements; the check fails the build if a `Properties.text = <raw transcript>` pattern is added. (4) Annual privacy-program audit by the Privacy Officer includes a sample of `AppEvents` rows to confirm the metadata-only pattern. (5) Cross-reference [Control 2.16](../../../controls/pillar-2-management/2.16-rag-source-integrity-validation.md) — the agent''s grounding-source telemetry should be logged as metadata only.

**Regulatory-evidence implications.** A PII spill — including a spill into the firm''s own logging systems — may be a reportable security event under multiple US regulatory regimes. The Reg S-P §248.30 trigger condition (TC-7 in the parent control 3.4) addresses unauthorized access to NPI; an internal logging system that exposes NPI to anyone with access to the Sentinel workspace, broader than the population permitted by the firm''s NPI access controls, may meet the trigger. The decision is made by the CCO, the Privacy Officer, and the GC. The contemporaneous evidence — the diagnostic KQL output, the rollback record, the data-purge request ID, the regulatory submissions, the post-spill detective control — together support the firm''s ability to demonstrate that the spill was identified, scoped, contained, and remediated.

---

## §23 Scenario 22 — OFAC ransom-payment ambiguous match
!!! danger "OFAC sanctions screening"
    This scenario continues from Scenario 17. An "ambiguous match" — where the OFAC screening service returns a partial-name match, a partial-address-prefix match for a cryptocurrency address, or a hit on a near-match list (such as the Counter-Narcotics Trafficking List or sectoral sanctions identifications) — is *not* a clean clearance. The firm''s decision whether to proceed with a payment in the face of an ambiguous match is governed by OFAC enforcement guidance and the firm''s OFAC compliance program; the determination is made by the GC and Outside Counsel in consultation with the OFAC Screening Officer, not by the platform. **An ambiguous match resolved in favour of payment without a documented decision package is a regulatory finding waiting to happen.** The decision package described below is the firm''s primary defence in any subsequent OFAC enforcement inquiry.

**Symptom.** During the Scenario 17 OFAC screening workflow, the screening service returns a partial-name match between a threat-actor handle observed in incident telemetry and a name on the OFAC SDN list. The match is below the screening service''s "automatic block" confidence threshold but above its "automatic clear" threshold — i.e., it is ambiguous. The CFO is under business pressure to move quickly; the GC needs a documented decision package to support whatever determination is made.

**Likely cause.** OFAC screening services produce matches across a confidence spectrum; ambiguous matches require human review and are fact-intensive. The firm''s runbook does not include a documented "decision package" template for ambiguous OFAC matches, and the OFAC Screening Officer does not have a pre-defined investigatory checklist.

**Diagnostic steps.**

*Document review:* Open the OFAC Compliance Manual maintained by the firm''s OFAC Screening Officer and the firm''s OFAC risk-assessment artifact. Identify whether ambiguous-match handling is documented and whether a decision-package template exists.

*PowerShell:* `Test-Agt34OfacScreening -PaymentAddress <btc-address> -Counterparty @{ ... } -Verbose` returns the screening result with the full per-list score breakdown and the matched-record details. Cross-reference against `Get-Agt34IrListItem -ItemId <id>` to identify which threat-actor identifiers from incident telemetry have been screened.

**Resolution.** (1) The OFAC Screening Officer assembles a decision package containing: (a) the full screening output including all matched records and confidence scores; (b) the firm''s investigation of the matched records (does the SDN-listed person have any plausible nexus to the threat-actor identifiers observed?); (c) the contextual evidence from incident telemetry (origin geographies, language patterns, infrastructure attribution); (d) commercial threat-intelligence reports (if any) addressing the threat-actor cluster; (e) the OFAC Compliance Manual provisions governing ambiguous-match handling; (f) a recommendation. (2) The GC and Outside Counsel review the decision package and make a written determination on whether the payment may proceed; the determination cites the operative OFAC guidance and the firm''s manual. (3) If the determination is "may not proceed," the CFO and Incident Commander pivot to an OFAC-clean recovery path (rebuild from backups, accept business-continuity impact, etc.). (4) If the determination is "may proceed," the determination memo, the decision package, and the OFAC Screening Officer''s contemporaneous attestation are filed in the immutable evidence container. (5) Regardless of outcome, the firm considers an OFAC voluntary self-disclosure if any pre-determination payment activity occurred or if the firm''s OFAC Compliance Manual was not followed.

**Prevention.** (1) The firm''s OFAC Compliance Manual includes a documented ambiguous-match handling procedure with a decision-package template. (2) The OFAC Screening Officer maintains a pre-defined investigatory checklist for ambiguous matches and is trained on it at least annually. (3) The incident-response runbook, the extortion-response playbook, and the OFAC Compliance Manual cross-reference each other so that the operational and compliance workflows are integrated. (4) Annual OFAC tabletop exercise (jointly with the cyber tabletop, Scenario 16) includes an ambiguous-match scenario.

**Regulatory-evidence implications.** OFAC enforcement actions for inadequate handling of ambiguous matches can include civil penalties and, in egregious cases, criminal referral. The decision package, the GC / Outside Counsel determination memo, the OFAC Screening Officer''s attestation, and the contemporaneous timestamps are the firm''s primary defence. This playbook describes the workflow; the underlying determination is made by the GC and Outside Counsel and is not a function of platform configuration.

---

## §24 Scenario 23 — CIRCIA rulemaking effective mid-quarter
**Symptom.** The Cyber Incident Reporting for Critical Infrastructure Act of 2022 (CIRCIA) final rule from CISA becomes effective mid-quarter, several months after the firm''s most recent annual runbook review. The new requirements include reporting "covered cyber incidents" within 72 hours of reasonable belief (and ransom payments within 24 hours), with specific definitional coverage that may include some of the firm''s business lines depending on its sector classification. The firm''s current runbook does not reference CIRCIA.

**Likely cause.** Annual runbook review is well-suited to stable regulatory regimes but lags behind active rulemaking. CIRCIA''s definitional scope (which entities are "covered" depends on whether they fall within one of CISA''s sixteen critical-infrastructure sectors and whether they meet additional size or activity thresholds) requires legal analysis specific to each business line.

**Diagnostic steps.**

*Document review:* Open the firm''s incident-response runbook and search for "CIRCIA". If absent, the runbook gap is confirmed. Open the firm''s sector-classification analysis (typically maintained by the GC''s regulatory-affairs team or by Outside Counsel). Identify which business lines may be covered.

**Resolution.** (1) The CCO, GC, and CISO jointly convene a CIRCIA-readiness working group with Outside Counsel, Internal Audit, and the relevant business-line CCOs. (2) The working group produces a per-business-line CIRCIA scoping memo identifying covered entities, applicable thresholds, and the operative reporting triggers. (3) The runbook is updated to add CIRCIA as an applicable regulatory regime in the regulatory-clock primer (Scenario 16), with a documented `Trigger` value for `Invoke-Agt34RegulatorClockLog` and a documented submission path (CISA''s reporting portal, expected to be a web form similar in style to the NYDFS portal). (4) The Power Automate flows that route Sev 1 incidents to regulatory submissions are updated to include a CIRCIA evaluation step. (5) Tabletop exercises (Scenario 16) are updated to include CIRCIA scenarios. (6) The CCO files an interim communication with the firm''s board or audit committee describing the regulatory change, the firm''s scoping conclusions, and the runbook updates.

**Prevention.** (1) The CCO subscribes to CISA, NYDFS, SEC, OCC, FRB, FDIC, FINRA, and CFTC regulatory-bulletin feeds and triages each new bulletin within five business days for runbook impact. (2) Mid-quarter regulatory updates that materially affect the runbook trigger an emergency runbook review rather than waiting for the annual cycle. (3) The runbook''s regulatory-clock primer (Scenario 16) is versioned and dated; every applicable rule has a "last reviewed" timestamp. (4) The Outside Counsel relationship includes a "regulatory-update advisory" line item in the engagement letter so that material rulemaking is brought to the firm''s attention proactively.

**Regulatory-evidence implications.** CISA enforcement of CIRCIA is expected to focus on serial non-reporting and on bad-faith non-reporting; the firm''s scoping memo, the runbook update, and the tabletop records together support the firm''s ability to demonstrate good-faith engagement with the new rule. The interim board / audit-committee communication supports oversight obligations under NYSE / Nasdaq listing rules and under the firm''s own corporate governance.

---

## §25 Scenario 24 — State AG portal submission rejected for per-state format mismatch
**Symptom.** Following an incident that triggers per-state breach-notification submissions in 14 states, the Privacy Officer''s submissions to two of the state-AG portals are rejected for format mismatch: California requires a specific paginated PDF format with mandatory fields in a specific order; New York requires submission through a specific online portal with character-limited free-text fields; Massachusetts requires fields the firm''s standard template doesn''t include.

**Likely cause.** State breach-notification statutes are highly heterogeneous in both substantive scope and submission-format mechanics. The firm''s template was built around the most common pattern (Reg S-P-style notice content) and does not address the specific format requirements of each state-AG portal.

**Diagnostic steps.**

*Document review:* Open each rejected state-AG portal, capture the rejection reason and the format requirement, and compare against the firm''s submission. Open the firm''s state-AG submission template inventory; identify which states have per-state format-specific templates and which rely on the general template.

**Resolution.** (1) The Privacy Officer corrects each rejected submission using the per-state format requirement and resubmits within the time remaining on the operative state clock. (2) The original submission timestamp, the rejection reason, and the corrected submission timestamp are recorded in the SharePoint IR record per Scenario 3''s pattern. (3) The Privacy Officer files a memo describing the gap and the per-state remediation. (4) For any state where the corrected submission would miss the operative clock, the Privacy Officer contacts the state-AG office directly to record the firm''s good-faith effort and obtain an out-of-band acknowledgment.

**Prevention.** (1) Maintain a per-state submission template inventory with format-specific templates for any state that has a portal-specific format. (2) The state-AG submission templates are reviewed at least annually against the live state-AG portal requirements; gaps are remediated. (3) The IR-response runbook''s state-AG submission step references the per-state template inventory rather than a generic template. (4) Build a `Test-Agt34StateAgSubmission -State <code>` script that pre-validates the draft submission against a versioned per-state schema before the human submitter opens the portal. (5) Annual privacy-program tabletop exercises include a multi-state submission scenario.

**Regulatory-evidence implications.** State AG enforcement actions for breach-notification non-compliance frequently focus on the per-state format and timing requirements. The per-state template inventory, the format-specific templates, the pre-validation script, and the rejection-remediation records together support the firm''s ability to demonstrate good-faith compliance. Cross-reference Scenario 8 (residency map) for the upstream determination of which states are in scope.

---
## §26 Escalation matrix and evidence-collection summary

### 27.1 Escalation matrix

The escalation matrix below is referenced from §0.2 (Severity matrix) and from every scenario that requires an escalation decision. The matrix uses the canonical role names from [`../../../reference/role-catalog.md`](../../../reference/role-catalog.md). Role assignments follow the firm''s on-call rotations; "duty" prefix indicates the named role''s currently-on-call individual.

| Trigger | Primary | Secondary | Tertiary | Notification SLA |
|---------|---------|-----------|----------|-------------------|
| Sev 1 declaration | Incident Commander | CISO | duty CCO + duty GC | 15 min |
| NYDFS 72h clock candidate | duty CCO | GC | Outside Counsel | 30 min |
| Banking 36h clock candidate (FRB / OCC / FDIC) | CISO | duty CCO + GC | Outside Counsel + Bank-Reg Liaison | 15 min |
| SEC 8-K Item 1.05 candidate | Disclosure Committee Chair (CCO) | GC + CFO | Outside Counsel + IR Officer | 30 min |
| Reg S-P §248.30 candidate | Privacy Officer | duty CCO | GC | 1 hour |
| OFAC ambiguous match | OFAC Screening Officer | GC | Outside Counsel + CFO | 30 min |
| SOX 404 ICFR material-weakness candidate | Internal Audit | CFO | Audit Committee Chair + Outside Auditor | 4 hours |
| Cyber-insurance notification | Risk Officer | CFO + GC | Insurance Coverage Counsel | 24 hours from Sev 1 |
| Microsoft Service Health late PIR | Incident Commander | CISO + Service Owner | duty CCO + GC | 1 business day |
| State-AG submission rejection | Privacy Officer | GC | per-state Outside Counsel | 4 hours |
| CIRCIA 72h candidate | duty CCO | GC + CISO | Outside Counsel | 30 min |
| PII spill into Sentinel | Sentinel Admin | Privacy Officer + duty CCO | GC + DPO | 30 min |

### 27.2 Evidence-collection summary

The §0.4 evidence-collection pattern is the canonical reference; this summary is for quick reference during incident response. For every Sev 1 incident, the Sentinel Admin (with the Records Officer as backup) is responsible for:

1. Establishing the immutable evidence container (SharePoint Online site collection or Azure Storage immutable blob) within 1 hour of declaration.
2. Capturing and SHA-256-hashing each artifact listed in §0.4 at the cadence specified.
3. Recording each artifact''s SHA-256 in the SharePoint IR list at the time of capture.
4. Refreshing the Service Health snapshot at 30, 60, and 90 days post-close to detect late PIR publications (Scenario 13).
5. Confirming legal-hold status (Scenario 12) on every relevant custodian within 4 hours of declaration.
6. Confirming Sentinel data-retention status (Scenario 20) for every regulatory-retention table referenced in the IR record.
7. Producing the cmdlet-based examiner package (Scenario 14) at incident close and at any subsequent regulator request.

### 27.3 Diagnostic data summary

Every diagnostic operation in this playbook calls one of the cmdlets in [§1.1](#11-cmdlet-catalog). The output of each cmdlet is logged to the `FsiAgtGov.Agt34` module''s immutable invocation log alongside the parameters, the runtime, the executor, and the SHA-256 of the output. This log is itself an examiner-facing artifact and is preserved per the firm''s data-retention schedule (see [Control 1.9](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md)).

---

## §27 Cross-references

### 28.1 Sibling playbooks (Control 3.4)

- [Portal walkthrough](portal-walkthrough.md) — the SharePoint IR list schema, Power Automate workflow design, Sentinel analytics rule inventory, and incident-classification taxonomy referenced throughout this troubleshooting playbook.
- [PowerShell setup](powershell-setup.md) — the `FsiAgtGov.Agt34` module installation, the `Test-Agt34*` and `Get-Agt34*` cmdlet sources, and the JIT / PIM session pattern.
- [Verification & testing](verification-testing.md) — the test-case catalog, the synthetic-incident generation patterns, and the evidence-pack templates used during quarterly compliance attestations.

### 28.2 Related controls (FSI Agent Governance Framework)

- [Control 1.7 — Comprehensive audit logging and compliance](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) — provides the underlying audit-log infrastructure (`SigninLogs`, `AuditLogs`, `AADServicePrincipalSignInLogs`, `OfficeActivity`) on which most diagnostic KQL in this playbook depends. PII-spill Scenario 22 references the audit-trail integrity expectations from 1.7.
- [Control 1.9 — Data retention and deletion policies](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md) — provides the data-retention schedule used in Scenario 20 (Sentinel retention) and Scenario 22 (PII-spill controlled purge). Cross-referenced by §27.3.
- [Control 1.11 — Conditional Access and phishing-resistant MFA](../../../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md) — Conditional Access workload-identity policy is the access-control surface that Scenario 9 references when diagnosing automation-rule RBAC failures, and that Scenarios 17 and 23 implicitly rely on for the OFAC Screening Officer''s privileged-access path.
- [Control 2.16 — RAG source integrity validation](../../../controls/pillar-2-management/2.16-rag-source-integrity-validation.md) — the agent-grounding integrity controls that Scenario 7 cross-references when investigating why an agent produced complaint-generating responses, and that Scenario 19 cross-references when scoping SOX-relevant agents.
- [Control 3.4 — Incident reporting and root cause analysis](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) — the parent control. The "trigger conditions" sub-section of the parent control enumerates the full set of TC-1 through TC-10 that map to the 24 scenarios in this playbook.

### 28.3 Reference materials

- [Role catalog](../../../reference/role-catalog.md) — canonical short forms for every administrative role referenced in the matrices and runbooks.
- [PowerShell baseline](../../_shared/powershell-baseline.md) — JIT / PIM session pattern, and the module-loading conventions for the `FsiAgtGov.Agt34` module.

### 28.4 Regulatory references mentioned in this playbook

This playbook references the following US financial-services regulatory regimes. The references are illustrative of the platform behaviour that supports compliance with each regime; they are not legal advice on any specific obligation, and they do not constitute regulatory interpretation. The firm''s determinations under each regime are made by the GC, the CCO, the Privacy Officer, and where relevant Outside Counsel based on the firm''s specific facts and circumstances.

- **NYDFS 23 NYCRR Part 500**, including the November 2023 amendments — particularly §500.17(a) (72-hour cybersecurity-event reporting), §500.16 (incident-response-plan documentation), §500.06 (audit-trail requirements).
- **SEC Regulation S-K Item 1.05** (cybersecurity-incident disclosure on Form 8-K) and Item 106 (annual cybersecurity disclosures on Form 10-K).
- **SEC Regulation S-P** as amended in May 2024 — §248.30 (individual-customer notification within 30 days of determination; service-provider notification within 72 hours of vendor''s awareness).
- **SEC Rule 17a-4(f)** and **FINRA Rule 4511** (broker-dealer record-preservation in non-rewritable, non-erasable formats).
- **CFTC Rule 1.31** (commodity-broker record-preservation requirements).
- **FRB SR 22-4 / OCC Bulletin 2022-3 / FDIC 12 CFR Part 304** (federal banking-agency 36-hour cyber-incident notification).
- **GLBA Safeguards Rule** (FTC implementing regulation; sector-specific requirements administered by the FRB, OCC, FDIC, and SEC).
- **FINRA Rule 4530** subsections (a)–(d) (event-driven and quarterly statistical reporting of customer complaints and other reportable events).
- **OFAC** Specially Designated Nationals and Blocked Persons List, the OFAC 50% Rule, the International Emergency Economic Powers Act (IEEPA), and OFAC''s ransomware-payment advisories (2020 and 2021).
- **Cyber Incident Reporting for Critical Infrastructure Act of 2022 (CIRCIA)** and CISA''s implementing rule.
- **SOX §302 / §404 / §906** (officer certifications, ICFR assessment, criminal liability for false certifications).
- **NYSE / Nasdaq listing rules** on Audit Committee oversight of material risks.
- **State breach-notification statutes** (50 states plus DC and US territories; per-state operative timing and content requirements).

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
