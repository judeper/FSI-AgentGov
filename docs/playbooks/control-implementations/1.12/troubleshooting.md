# Control 1.12 — Troubleshooting: Insider Risk Detection and Response

> **Scope.** This playbook is the symptom-first diagnostic companion to [Control 1.12 — Insider Risk Detection and Response](../../../controls/pillar-1-security/1.12-insider-risk-detection-and-response.md). It covers Microsoft Purview Insider Risk Management (IRM) detection failures across the FSI-relevant surface — Risky Agents, Risky AI usage, Data leaks (priority users), Security policy violations, Adaptive Protection, Forensic Evidence (dual-auth, 120-day clip retention), Triage Agent, HR connector, browser-extension Windows-only constraint, pseudonymization, and the cross-control handoffs to Communication Compliance (1.10), eDiscovery (1.19), Sentinel UEBA (3.9), Incident Reporting (3.4), and Model Risk (2.6).
>
> **Audience.** Insider Risk Management Admin, Insider Risk Management Analyst, Insider Risk Management Investigator, Insider Risk Management Auditor, Insider Risk Management Approver, Purview Compliance Admin, Privacy Officer, General Counsel, HR Privileged, SOC Analyst, AI Governance Lead. Roles named per [`docs/reference/role-catalog.md`](../../../reference/role-catalog.md).
>
> **Sibling playbooks.** [portal-walkthrough.md](portal-walkthrough.md) · [verification-testing.md](verification-testing.md)
>
> **Last UI Verified:** April 2026

!!! warning "Non-Substitution"
    Microsoft Purview Insider Risk Management *supports compliance with* FINRA Rule 3110(b) supervisory expectations, FINRA Rule 4511 / SEC Rule 17a-3 / 17a-4(b)(4) make-and-preserve obligations, FINRA RN 24-09 / Rule 3110 (generative-AI supervision expectations), SEC Regulation S-P §248.30 (post-2024 amendments), GLBA §501(b) Safeguards Rule, NYDFS 23 NYCRR 500 §§500.06 / .16 / .17, FFIEC IT Examination Handbook expectations, OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12), and Fed SR 26-2 (formerly SR 11-7) model risk management — but it **does not replace** those obligations or substitute for the firm's documented supervisory procedures, model risk governance, written information security program, or registered-principal review. Implementation requires written supervisory procedures (WSPs), documented SoD across IRM role groups, signed Compliance + Legal + HR + Privacy review of the policy posture, and continuous regulator-facing evidence preservation. Microsoft does not publish IRM investigation or alert-response SLAs; any response window stated in this playbook is a **firm-defined** supervisory commitment.

---

## Table of Contents

- [§0 Triage and Severity Framework](#0-triage-and-severity-framework)
- [§1 Evidence Preservation Before Remediation](#1-evidence-preservation-before-remediation)
- [§2 Decision Matrix — IRM vs CC vs eDiscovery vs DLP vs Sentinel](#2-decision-matrix-irm-vs-cc-vs-ediscovery-vs-dlp-vs-sentinel)
- [§3 Compensating Controls During an IRM Degradation](#3-compensating-controls-during-an-irm-degradation)
- [§4 Symptom-Driven Diagnostics — 23 Scenarios](#4-symptom-driven-diagnostics-23-scenarios)
  - [Scenario 1 — Unified Audit Log not capturing IRM alerts](#scenario-1-unified-audit-log-not-capturing-irm-alerts)
  - [Scenario 2 — Risky Agents (preview) policy not visible in portal](#scenario-2-risky-agents-preview-policy-not-visible-in-portal)
  - [Scenario 3 — Risky AI usage policy not generating alerts](#scenario-3-risky-ai-usage-policy-not-generating-alerts)
  - [Scenario 4 — Data leaks (priority users) over-alerting](#scenario-4-data-leaks-priority-users-over-alerting)
  - [Scenario 5 — Security policy violations not firing](#scenario-5-security-policy-violations-not-firing)
  - [Scenario 6 — Defender for Cloud Apps anomaly silence post-June-2025 migration](#scenario-6-defender-for-cloud-apps-anomaly-silence-post-june-2025-migration)
  - [Scenario 7 — Entra ID Protection signals not feeding IRM](#scenario-7-entra-id-protection-signals-not-feeding-irm)
  - [Scenario 8 — HR connector health red](#scenario-8-hr-connector-health-red)
  - [Scenario 9 — Forensic Evidence capture stuck "Pending Approval"](#scenario-9-forensic-evidence-capture-stuck-pending-approval)
  - [Scenario 10 — Forensic Evidence policy creation rejected](#scenario-10-forensic-evidence-policy-creation-rejected)
  - [Scenario 11 — Forensic clip approaching 120-day expiry without export](#scenario-11-forensic-clip-approaching-120-day-expiry-without-export)
  - [Scenario 12 — State employee-monitoring law non-compliance discovered post-deployment](#scenario-12-state-employee-monitoring-law-non-compliance-discovered-post-deployment)
  - [Scenario 13 — Triage Agent fails to refresh after 90 days](#scenario-13-triage-agent-fails-to-refresh-after-90-days)
  - [Scenario 15 — Pseudonymization broken (anonymization toggled off)](#scenario-15-pseudonymization-broken-anonymization-toggled-off)
  - [Scenario 16 — Pseudonymization → non-pseudonymized escalation lacks HR + Legal sign-off](#scenario-16-pseudonymization-non-pseudonymized-escalation-lacks-hr-legal-sign-off)
  - [Scenario 17 — Communication Compliance correlation missing](#scenario-17-communication-compliance-correlation-missing)
  - [Scenario 18 — Sentinel UEBA service-principal anomaly not joined with IRM alert](#scenario-18-sentinel-ueba-service-principal-anomaly-not-joined-with-irm-alert)
  - [Scenario 19 — Risky Agents alert volume from one Copilot Studio agent overwhelms queue](#scenario-19-risky-agents-alert-volume-from-one-copilot-studio-agent-overwhelms-queue)
  - [Scenario 20 — IRM alert escalates to incident — handoff to Control 3.4 + legal hold](#scenario-20-irm-alert-escalates-to-incident-legal-hold-regulator-clock)
  - [Scenario 21 — SoD violation found in IRM role groups](#scenario-21-sod-violation-found-in-irm-role-groups)
  - [Scenario 22 — Forensic Evidence exposed PII to non-cleared reviewer](#scenario-22-forensic-evidence-exposed-pii-to-non-cleared-reviewer)
  - [Scenario 23 — AI-driven risk score (Triage Agent / ML scoring) drifts](#scenario-23-ai-driven-risk-score-triage-agent-ml-scoring-drifts)
  - [Scenario 25 — Examiner request for IRM evidence cannot be produced](#scenario-25-examiner-request-for-irm-evidence-cannot-be-produced)
- [§6 Escalation Matrix](#6-escalation-matrix)
- [§7 Cross-References](#7-cross-references)

---

## §0 Triage and Severity Framework

Microsoft Purview Insider Risk Management (IRM) is the **user-behavior risk plane** for the M365 estate and (via browser extensions) selected non-Microsoft AI / SaaS surfaces. For an FSI organization it is a **detective control feeding the supervisory program** under FINRA Rule 3110(b), a **safeguards-monitoring component** under GLBA 501(b), and a **model-driven detection system** subject to model risk governance under OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12) / Fed SR 26-2 (formerly SR 11-7). IRM is **not** a books-and-records system: alerts, cases, and Forensic Evidence clips are working investigative artifacts. **Forensic Evidence clips auto-delete 120 days after capture unless exported.** Treat any change to a policy, role-group membership, priority user/content list, pseudonymization setting, or Forensic Evidence approver list as an **evidence-bearing event**: preserve **before** you remediate.

### 0.1 Severity matrix (Zone-aware, firm-defined response windows)

> Microsoft Learn does **not** publish IRM investigation or alert-response SLAs. The response windows below are **firm-defined supervisory commitments** — align them with the firm's WSP and FINRA 3110 supervisory expectations. Do not represent them to a regulator as Microsoft-stated ceilings.

| Severity | Trigger (IRM-specific) | Response window (firm-defined) | Escalation |
|---|---|---|---|
| **SEV-1** | An IRM policy covering a Zone 3 population (FINRA-supervised registered representatives, RIA staff, trading desk, MNPI-handlers, agent admins) is **off, deleted, mis-scoped, or producing zero alerts** during a window where seed/test activity is known to have occurred; the **Risky Agents** default policy is missing or scoped to zero users; HR connector last-success > 24 h while a known leaver's `LastWorkingDate` is within the policy lookback window; Forensic Evidence captures are running **without** dual-auth or **without** state-law notice; pseudonymization was disabled tenant-wide; Unified Audit Log is **off** (silent-zero-row trap); a Forensic Evidence approver group is empty (zero-approver state); priority user group includes the entire tenant ("everyone is priority" defeats focused review); PII surfaced via Forensic Evidence to a non-cleared reviewer (Scenario 22); examiner cannot be served on time (Scenario 25) | Immediate | CISO + Compliance + Legal + HR + Privacy within 1 h; NYDFS 23 NYCRR 500 §500.17(a) **72-hour cybersecurity-event clock** evaluated by Legal |
| **SEV-2** | Coverage gap on a Zone 2 population (single business unit excluded from a Risky AI usage policy; browser extension missing from an OS class; non-Windows population excluded silently); HR connector field-mapping drift (e.g., `ResignationDate` populated but `LastWorkingDate` blank → departing-user template silently quiet); Adaptive Protection threshold no longer triggering after a baseline shift; classifier / ML model bump invalidated the prior week's alert baseline; Auditor role group empty (no independent assurance trail for unmask events); Investigator role group also assigned as Approver (separation-of-duties violation for Forensic Evidence) | 4 h | IRM Admin → AI Governance Lead / Insider Risk Lead within 4 h; Compliance notified |
| **SEV-3** | Single-user / single-channel coverage gap; Forensic Evidence storage cap approaching; analytics scan stalled past the documented 48 h window; Triage Agent unavailable (capacity / Preview→GA churn); Defender for Cloud Apps connector for a single SaaS source delayed; case-to-eDiscovery escalation failing for a single case | 1 business day | IRM Admin |
| **SEV-4** | Cosmetic UI drift; tooltip / column-order changes; preview-feature regression that does not affect coverage, evidence, or reviewer access | Best effort | Track in known-issues log |

**Zone-aware reading.** Severity is interpreted against the in-scope user population. The same configuration error is SEV-1 against a Zone 3 broker-dealer population and SEV-3 against a Zone 1 administrator pilot. Always classify by the **regulatory exposure of the affected users**, not by the technical defect.

### 0.2 Reportability decision tree

> This is an **escalation aid**, not a legal determination. Reportability is decided by Compliance and Legal. Use the matrix to surface the right question to the right desk **inside the response window** — do not self-decide.

| Trigger | Escalate to | Possible obligation (verify with counsel) |
|---|---|---|
| Loss of insider-risk visibility on Zone 3 FINRA-supervised population (policy off, mis-scoped, or zero-alert with seed activity present) | Compliance | **FINRA Rule 3110(b)** supervisory system — documented procedures must be followed; **FINRA RN 24-09 / Rule 3110** firm reminders on AI/agent supervision (re-states existing 3110/4511 obligations; do not over-cite as standalone authority) |
| Books-and-records gap — IRM artifacts treated as records and lost (cases closed, clips expired at 120 d, alerts deleted) | Compliance + Legal | **FINRA Rule 4511(a)/(b)** make-and-preserve; **SEC Rule 17a-3** required records; **SEC Rule 17a-4(b)(4)** non-rewriteable / non-erasable retention. **IRM is not the retention plane** — the gap is in the records pipeline (Control 1.9), not in IRM itself |
| Customer NPI / PII surfaced via insider exfiltration alert and not contained | Privacy + Legal | **GLBA 501(b)** Safeguards; **SEC Reg S-P §248.30** customer-notification timeline (post-2024 amendments — written incident-response program, individual notice "as soon as practicable" and not later than 30 days); state breach-notification statutes |
| Cybersecurity event determination — reasonable likelihood of material harm to normal operations | CISO + Legal | **NYDFS 23 NYCRR 500 §500.17(a)** — **72-hour** notice to Department after determination; the clock starts at **determination**, not at first alert; cross-reference §500.06 audit-trail and §500.16 incident-response-plan obligations |
| Internal control over financial reporting impacted (insider activity touches financial-disclosure data, treasury, close process) | Compliance + Internal Audit | **SOX §302 / §404** ICFR — insider-risk monitoring is referenced in the firm's control inventory |
| Model-risk event — IRM ML risk scoring or the Triage Agent produced demonstrably wrong prioritization that affected an outcome | Model Risk + Compliance | **OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12)** / **Fed SR 26-2 (formerly SR 11-7)** model risk management; AI Triage Agent and ML risk scoring are model-driven and belong in the model inventory (Control 2.6) |
| Records-related event for a covered swap / trading-related insider activity | Compliance | **CFTC Rule 1.31** recordkeeping (full, complete, original; retention period; production timeline) |
| Insider misconduct surfaced through IRM alert (suspected fraud, theft, market manipulation, harassment) | HR + Legal + Compliance | **FINRA Rule 4530** reporting; firm code-of-conduct procedures; coordinate Forensic Evidence preservation with Legal **before** notifying the subject |
| Forensic Evidence captured for a user resident in / employed in a state with employee-monitoring notice statutes (CT, DE, NY) | Privacy + Legal + HR | State employee-monitoring notice law; coordinate notice posture **before** capture; document in the privacy register |
| Pseudonymized usernames re-identified by an investigator without HR + Legal sign-off | Privacy + Compliance | Privacy-by-design defeat; the unmask must have a logged investigation reason; the IRM Auditor reviews the unmask audit row |

### 0.3 Pre-escalation checklist (≥ 16 items)

1. [ ] **Tenant ID and cloud** confirmed (Commercial)
2. [ ] **IRM SKU verified** — Microsoft 365 E5, E5 Compliance, Insider Risk Management standalone, or Microsoft Purview Suite (per-user); PAYG enabled where required (notably Forensic Evidence)
3. [ ] **Unified Audit Log on** — `Get-AdminAuditLogConfig` from a `Connect-ExchangeOnline` session shows `UnifiedAuditLogIngestionEnabled : True` (UAL off is the **most common silent-failure mode** in IRM)
4. [ ] **HR connector last-success ≤ 24 h**; field mapping for `EmployeeID`, `ResignationDate`, `LastWorkingDate`, `EmploymentStatus` verified against the source HRIS schema
5. [ ] **Audit ingestion confirmed** for IRM admin actions (verify operation names against current Learn `audit-log-activities`)
6. [ ] **Analytics enabled** with **≥ 7-day baseline**; Learn states analytics scans may take **up to 48 h** to complete
7. [ ] **Pseudonymization state captured before any re-identification**
8. [ ] **Forensic Evidence dual-auth approver list** non-empty and **distinct from Investigators**; state-law notice posture (CT / DE / NY) confirmed with Privacy + Legal before any new capture
9. [ ] **Browser extension / Edge config policy state** — Microsoft Insider risk extension (Edge) and Microsoft Purview extension (Chrome) deployed via Intune to the in-scope **Windows** population; non-Windows excluded explicitly with documented gap
10. [ ] **Device onboarding state** — devices onboarded to Microsoft Purview cover the in-scope user population
11. [ ] **Priority user group membership snapshot** captured (membership at incident UTC); group is **role-based**, not "everyone"
12. [ ] **Priority content list snapshot** captured (SharePoint sites / sensitive-info types)
13. [ ] **Administrative units exclusion check** — restricted-AU admins/investigators see only their scoped users
15. [ ] **Compliance + Legal + HR notified** per severity matrix; Privacy notified for any pseudonymization-related, NPI-related, or Forensic-Evidence-related event; **NYDFS 72-hour determination** evaluated by Legal where applicable
16. [ ] **Evidence preserved** per §1; SHA-256 sidecars captured; manifest stored in Control 1.7 evidence bucket
17. [ ] **Companion-control health checked** — DLP (1.5), DSPM (1.6), Audit (1.7), Records (1.9), CC (1.10), Conditional Access (1.11), eDiscovery (1.19), Sentinel (3.9), Incident Reporting (3.4), Model Risk (2.6) — none silently degraded in a way that compounds the IRM symptom

---

## §1 Evidence Preservation Before Remediation

A common audit finding in FSI is *"the policy was modified before the failing-state evidence was captured, and the firm cannot reconstruct what insider-risk coverage was in effect during the relevant period."* Do not be that finding. Capture the following artifacts **before** disabling, editing, re-scoping, replacing approvers, or unmasking pseudonymized identities.

### 1.1 Evidence inventory

| ID | Artifact | Source | Retention |
|---|---|---|---|
| **E-01** | Policy snapshot (template, scope, conditions, indicators, threshold profile, status, last-modified-by/UTC) — **including Risky Agents default policy** | Purview portal — Insider Risk Management > Policies | 7 y (FINRA 4511 / SEC 17a-4(f) floor) |
| **E-02** | Alerts queue snapshot (filter by policy, severity, status); per-alert risk-score breakdown (sequence vs cumulative; weighted indicators) | Purview portal — Alerts | 7 y |
| **E-03** | Cases queue snapshot (status, assignee, last activity); investigation-notes / activity-timeline / data-risk-graph export | Purview portal — Cases | 7 y |
| **E-04** | Forensic Evidence clip inventory (capture UTC, trigger, requesting Investigator, approving Approver, retention countdown to **120-day auto-delete**) | Purview — Forensic Evidence | 7 y (clip itself: must be exported pre-120-d if retention required) |
| **E-05** | Role-group snapshot for `Insider Risk Management`, `Insider Risk Management Admins`, `Insider Risk Management Analysts`, `Insider Risk Management Investigators`, `Insider Risk Management Auditors`, `Insider Risk Management Approvers` (membership, AU restriction, effective permissions) | Purview > Permissions; Microsoft Graph `directoryRoles` | 7 y |
| **E-06** | Priority user group snapshot + priority content list snapshot | Purview — Insider Risk Management > Settings | 7 y |
| **E-07** | Pseudonymization state (toggle state, last-toggled-by identity, active "show usernames" sessions) — **captured before any re-identification action** | Purview — Insider Risk Management > Settings > Privacy | 7 y |
| **E-08** | HR connector last-success UTC, ingestion row count, schema, field mapping for `EmployeeID` / `ResignationDate` / `LastWorkingDate` / `EmploymentStatus` | Purview — Data connectors | 7 y |
| **E-09** | Browser extension / Edge config policy state (Intune coverage report; per-OS coverage; non-Windows gap documented) | Intune (or equivalent MDM); Edge / Chrome management | 7 y |
| **E-10** | Device onboarding state — devices onboarded to Microsoft Purview, cross-referenced against policy user scope | Purview — Settings > Device onboarding | 7 y |
| **E-11** | Audit-search export (`Search-UnifiedAuditLog` filtered for IRM admin actions and unmask events) — paginated, raw-JSON, SHA-256-sidecared | Exchange Online PowerShell | 7 y |
| **E-12** | Defender for Cloud Apps connector health for any SaaS source feeding IRM (Box, Dropbox, Google Drive, Amazon S3, Azure) | Defender for Cloud Apps — Connectors | 7 y |
| **E-13** | Defender for Endpoint integration state (required for Security policy violations templates) | Defender XDR — Settings > Integrations | 7 y |
| **E-15** | PAYG billing state for Forensic Evidence and other PAYG-dependent capabilities | Azure subscription — Cost Management | 7 y |
| **E-16** | Tenant ID, cloud, affected user/policy/case list, UTC window, role used, identity that performed the failing-state observation, browser, sign-in method | Operator-captured incident header | 7 y |
| **E-17** | SHA-256 manifest sidecar covering every artifact above; stored in Control 1.7 evidence bucket with WORM retention (Control 1.9) | Operator-generated | 7 y (immutable) |

Only after the evidence pack is sealed and hashed should the policy be modified, the case re-assigned, or pseudonymization toggled. The remediation itself becomes a new evidence item — capture the post-remediation state with the same rigor.

### 1.2 Evidence-capture helper (reference)

```powershell
# Evidence capture wrapper — call BEFORE any remediation
# Roles: Insider Risk Management Admin (read-only inventory) + Exchange Online Admin (UAL export)
# Output: timestamped folder with each artifact + SHA-256 manifest

param(
  [Parameter(Mandatory)] [string] $IncidentId,
  [Parameter(Mandatory)] [string] $TenantId,
  [datetime] $WindowStartUtc = (Get-Date).ToUniversalTime().AddDays(-7),
  [datetime] $WindowEndUtc   = (Get-Date).ToUniversalTime()
)

$root = Join-Path -Path $env:FSI_EVIDENCE_BUCKET -ChildPath ("1.12-{0}-{1:yyyyMMddHHmmss}" -f $IncidentId, $WindowEndUtc)
New-Item -ItemType Directory -Path $root -Force | Out-Null

# E-11 — UAL export with proper pagination
Connect-ExchangeOnline -ShowBanner:$false
$sessionId = [guid]::NewGuid().ToString()
$page      = 0
$results   = @()
do {
  $page++
  $batch = Search-UnifiedAuditLog `
    -StartDate $WindowStartUtc -EndDate $WindowEndUtc `
    -RecordType ComplianceCenter `
    -Operations 'CaseAdded','CaseInvestigatorChanged','PolicyAdded','PolicyChanged','PolicyRemoved',`
                'AlertReviewed','UserUnmasked','ForensicEvidenceCaptureRequested',`
                'ForensicEvidenceCaptureApproved','ForensicEvidenceCaptureRejected' `
    -SessionId $sessionId -SessionCommand ReturnLargeSet -ResultSize 5000
  $results += $batch
} while ($batch.Count -gt 0 -and $results.Count -lt 50000)

$results | ConvertTo-Json -Depth 8 | Out-File (Join-Path $root 'E-11-ual.json') -Encoding utf8

# Manifest
Get-ChildItem $root -File | ForEach-Object {
  [pscustomobject]@{
    File   = $_.Name
    Size   = $_.Length
    Sha256 = (Get-FileHash $_.FullName -Algorithm SHA256).Hash
    UTC    = (Get-Date).ToUniversalTime().ToString('o')
  }
} | Export-Csv (Join-Path $root 'E-17-manifest.csv') -NoTypeInformation
```

> **Operation-name caveat.** Microsoft renames audit operations periodically. Always cross-reference the current Microsoft Learn `audit-log-activities` reference at the time of capture; do not hard-code names from a prior incident's runbook. The list above is illustrative.

---

## §2 Decision Matrix — IRM vs CC vs eDiscovery vs DLP vs Sentinel

The single most common cause of misdirected investigation in FSI is reaching for the wrong Purview / Defender / Sentinel solution. Use this matrix to route a symptom to the **correct** control before configuring anything.

| Symptom / question | Use **DLP (1.5)** | Use **DSPM for AI (1.6)** | Use **CC (1.10)** | Use **IRM (1.12)** | Use **eDiscovery (1.19)** | Use **Sentinel UEBA (3.9)** |
|---|---|---|---|---|---|---|
| Where is the **prompt content** (the actual text the user sent to Copilot)? | ❌ | ✅ DSPM surfaces interaction activity, sensitive-info hits, content lineage | ✅ CC review surface for the conduct content of the prompt | ❌ IRM scores the **behavior**; not the prompt body | ⚠️ Discoverable via Copilot interaction record search; not the routine review surface | ❌ |
| Where is the **books-and-records event proof** that the interaction happened? | ❌ | ⚠️ DSPM activity view, not records | ⚠️ CC review record exists while policy is in place; not WORM | ❌ — IRM cases are **not** WORM | ✅ eDiscovery (Premium) collection of the underlying audit record + retention label per Control 1.9 | ❌ |
| Where is **real-time blocking** of risky AI usage at egress? | ✅ DLP-for-Copilot (Block / Block with override / Audit) | ❌ | ❌ | ⚠️ Adaptive Protection can dynamically tighten DLP / DLM / Conditional Access — but only where Adaptive Protection is **available in the cloud** | ❌ | ❌ |
| Where is **cross-signal UEBA** (peer baseline, impossible travel, mass download)? | ❌ | ❌ | ❌ | ⚠️ IRM scores M365-centric behavior; peer-baseline is firm-narrow | ❌ | ✅ Sentinel UEBA — broader signal set across identity, network, endpoint |
| Where is the **behavioral risk score** for an individual user? | ❌ | ❌ | ❌ | ✅ Authoritative — IRM is the risk-scoring plane | ❌ | ⚠️ Sentinel UEBA produces a separate score; correlate but do not conflate |
| **Legal hold + collection** of the activity for litigation / regulatory inquiry | ❌ | ❌ | ❌ | ⚠️ Escalate the IRM case to eDiscovery | ✅ Authoritative — discovery + hold plane (Premium); **dual-authorization** for case creation in regulated FSI | ❌ |
| **Long-horizon (> 120 d) preservation** of Forensic Evidence clips | ❌ | ❌ | ❌ | ❌ — clips **auto-delete at 120 days**; not the long-term store | ✅ Hold + collection; or promote to Records Management retention label (Control 1.9) | ❌ |
| **Departing-user data theft** detection | ⚠️ DLP at egress | ⚠️ DSPM for sensitive-data exposure | ⚠️ CC for conduct content | ✅ Authoritative — `Data theft by departing users` template (HR connector required) | ⚠️ Hold the leaver's mailbox / OneDrive | ⚠️ Sentinel correlation |
| **Risky agent behavior** (agent emitting sensitive content, accessing priority sites, sharing externally) | ❌ | ⚠️ DSPM for grounding/exposure context | ❌ | ✅ Authoritative — **Risky Agents** template (applied by default) | ❌ | ⚠️ Optional correlation |

**Escalation note — IRM case → eDiscovery (Premium) for legal hold.** When an IRM case rises to potential legal action, **promote** rather than convert. The IRM case stays open as the investigation record; in parallel, open an eDiscovery (Premium) case (Control 1.19) with **dual authorization**, place a **hold** on the subject user's mailbox, OneDrive, Teams, and any priority SharePoint sites surfaced in the IRM data-risk graph, and **export Forensic Evidence clips before the 120-day auto-delete clock fires**. Document the IRM-case-to-eDiscovery-case linkage in both systems.

---

## §3 Compensating Controls During an IRM Degradation

Apply one or more while IRM is degraded; document the compensating control in the incident ticket. Do not leave the detection gap open.

- **Tighten Communication Compliance review cadence** (Control 1.10) — temporarily increase review percentage on the in-scope Copilot / conduct-content templates to surface insider-conduct signal that would otherwise have flowed to IRM.
- **Daily Unified Audit Log searches** (Control 1.7 / Audit Premium) for `CopilotInteraction`, file-access bursts, OneDrive sync, SharePoint downloads, USB device events, and external email patterns for the affected user population.
- **Tighten DLP-for-Copilot block actions** (Control 1.5) — temporarily move Block-by-label rules from `TestWithNotifications` to `Enable` for high-risk content categories (NPI, MNPI, regulated keywords).
- **Run targeted DSPM-for-AI hunts** (Control 1.6) for grounding-data exposure during the IRM degradation window.
- **Defender for Cloud Apps anomaly detection hunts** — Cloud App Security UEBA produces independent anomaly signals (mass download, impossible travel, unusual SaaS activity).
- **Microsoft Sentinel UEBA / hunting queries** (Control 3.9) where deployed — Sentinel UEBA produces an independent peer-baseline view; cross-correlate with surviving IRM signals where available.
- **Manual HR notification flow for departures** — if the HR connector is degraded, invoke the firm's documented manual departure notification (HR → IRM Admin → Compliance) for known leavers within the lookback window.
- **Freeze of new Zone 3 agent activations** (Controls 2.1, 2.16) — do not expand the agent surface during an insider-risk detection degradation; freeze new Microsoft Copilot Studio publish actions and new Zone 3 agent registrations until IRM coverage is restored.
- **Manual Forensic Evidence substitute** — for a known high-risk subject during an IRM Forensic Evidence outage, work with Legal to invoke a documented manual evidence-collection procedure (e.g., MDE live response, eDiscovery (Premium) collection on the user's mailbox/OneDrive). Do **not** improvise endpoint-recording mechanisms outside documented procedure.

---

## §4 Symptom-Driven Diagnostics — 23 Scenarios

> **Format for every scenario.** Symptom · Likely Cause · Diagnostic Steps (portal + KQL/PowerShell) · Resolution · Prevention · Regulatory-evidence implications. Do not skip the diagnostic step — fixing without diagnosing is what got you here.

### Scenario 1 — Unified Audit Log not capturing IRM alerts

**Symptom.** An IRM Admin runs a known-bad seed activity (e.g., bulk OneDrive download by a test user in scope of `Data leaks` policy), waits the analytics window, and observes **zero alerts** in the queue. Cross-checking the Unified Audit Log via `Search-UnifiedAuditLog` returns **no `RecordType: ComplianceCenter` rows** for IRM operations, **no `CopilotInteraction` rows**, and no file-access events for the test user. The IRM Cases queue is empty for the period. Compliance asks for the daily supervisory-review evidence and the firm has nothing to produce.

**Likely Cause.** **Unified Audit Log ingestion is disabled at the tenant.** This is the **#1 silent-failure mode** in IRM. UAL is the durable evidence backbone IRM scores against; with UAL off, the entire detection pipeline is silent, but the portal does not display a banner that says "your detection is dead." Investigators infer false negatives ("nothing risky happened") from a configuration defect.

Secondary causes: (a) UAL was on but ingestion was paused during a tenant migration; (b) the IRM admin querying UAL is using a SessionId without `ReturnLargeSet` and is silently truncated; (c) UAL operation names changed in a recent Microsoft Learn refresh and the runbook is using stale operation names.

**Diagnostic Steps.**

*Portal.* Microsoft Purview portal → **Settings** → **Audit** → confirm the banner reads *"Auditing is on for your organization."* If the banner reads *"Start recording user and admin activities,"* UAL is **off**. Then Microsoft Purview portal → **Audit** → search the suspect window with `Activities = Insider Risk Management activities` and confirm rows exist. If the portal search returns zero rows for a confirmed-active period, the portal index has not caught up — wait the documented ingestion window (up to 24 h for new-tenant first-ingest; minutes for steady-state) before concluding hard failure.

*PowerShell.*

```powershell
Connect-ExchangeOnline -ShowBanner:$false
Get-AdminAuditLogConfig | Format-List UnifiedAuditLogIngestionEnabled, UnifiedAuditLogFirstOptInDate
# Expected: UnifiedAuditLogIngestionEnabled : True
# If False: UAL is off — this is SEV-1 against any Zone 3 population

# Probe: confirm IRM admin activity is actually written
$start = (Get-Date).ToUniversalTime().AddDays(-1)
$end   = (Get-Date).ToUniversalTime()
$sid   = [guid]::NewGuid().ToString()
$rows  = @()
do {
  $batch = Search-UnifiedAuditLog -StartDate $start -EndDate $end `
            -RecordType ComplianceCenter `
            -SessionId $sid -SessionCommand ReturnLargeSet -ResultSize 5000
  $rows += $batch
} while ($batch.Count -gt 0 -and $rows.Count -lt 50000)
$rows.Count
```

*KQL (Sentinel — where Audit logs are forwarded via Office 365 connector or Defender XDR connector).*

```kusto
// Last 24 h of IRM-related compliance events
OfficeActivity
| where TimeGenerated > ago(24h)
| where RecordType == "ComplianceCenter"
| where Operation has_any (
    "CaseAdded", "CaseInvestigatorChanged",
    "PolicyAdded", "PolicyChanged", "PolicyRemoved",
    "AlertReviewed", "UserUnmasked",
    "ForensicEvidenceCaptureRequested", "ForensicEvidenceCaptureApproved")
| summarize Events = count(), Operators = dcount(UserId) by Operation
| order by Events desc
```

If the KQL returns **zero rows** while you know IRM admins were active in the window, suspect UAL ingestion is off **or** the Office 365 / Defender XDR connector to Sentinel has stopped (cross-reference Scenario 18).

**Resolution.**

1. Capture E-01..E-17 per §1 **before** flipping UAL on — the failing-state baseline must be preserved (the auditor needs to see what coverage was in effect at the suspect-window UTCs).
2. As **Exchange Online Admin** (UAL toggle requires this role; cannot be performed by IRM Admins alone):
   ```powershell
   Connect-ExchangeOnline -ShowBanner:$false
   Set-AdminAuditLogConfig -UnifiedAuditLogIngestionEnabled $true
   ```
3. Wait the documented ingestion-warmup window. Re-run the seed activity from an in-scope identity. Re-query UAL. Re-check the IRM alerts queue.
4. Open a Compliance ticket recording the dead-window UTCs, the affected user population, and the compensating-control posture in force during the dead window (CC review-cadence increase per Control 1.10; Sentinel UEBA hunt per Control 3.9; manual HR notification for known leavers).

**Prevention.**

- **Daily SRE check.** Run `Get-AdminAuditLogConfig` from a service-principal-backed automation; alert SEV-1 on `UnifiedAuditLogIngestionEnabled : False`.
- **Conditional Access lock-down on the toggle.** Require phishing-resistant MFA + just-in-time PIM elevation to the Exchange Online Admin role for any tenant configuration change touching audit (Control 1.11).
- **Detection canary.** Run a benign daily seed activity from a synthetic test user and assert that an alert (or at minimum an audit row) materializes within the documented window. Silent zero on the canary is SEV-1 even if no real-world bad activity is in flight.

**Regulatory-evidence implications.**

| Authority | Exposure |
|---|---|
| **FINRA Rule 3110(b)** | The supervisory system requires **documented procedures** for review; a silent-zero IRM during a covered window is a documented-procedures gap if the firm cannot demonstrate the supervisory review was performed by an alternate mechanism |
| **FINRA Rule 4511 / SEC Rule 17a-3** | The audit log itself is not the FINRA 4511 record but is **referenced by** the supervisory record; loss of UAL ingestion creates a derived evidence gap |
| **SEC Rule 17a-4(b)(4)** | Non-rewriteable / non-erasable retention applies to required records; UAL exports must be sealed and SHA-256-sidecared into the WORM evidence bucket per Control 1.9 |
| **NYDFS 23 NYCRR 500 §500.06** | Audit-trail requirements; the firm must maintain audit trails sufficient to detect and respond to cybersecurity events; UAL off is a §500.06 finding waiting to happen |
| **GLBA §501(b)** | Safeguards monitoring presupposes that the monitoring is happening; silent UAL is an internal control weakness |

---

### Scenario 2 — Risky Agents (preview) policy not visible in portal

**Symptom.** An IRM Admin opens **Microsoft Purview portal → Insider Risk Management → Policies** and **does not see a Risky Agents policy**. The Create policy wizard does not list `Risky Agents` as a selectable template. Compliance has been told by the AI Governance Lead that Risky Agents is the authoritative detection plane for Copilot Studio agent behavior; absent the policy, Compliance reports zero agent-behavioral-risk coverage to the AI Governance Council.

**Likely Cause.** Microsoft documents Risky Agents as **applied by default when IRM is configured** — it is **not** selected through the Create policy wizard. There are several reasons it may not be visible:

1. **Tenant has not yet been opted into the preview / GA wave** — feature is gated by a rollout ring; the tenant is in a later ring.
2. **IRM has never been initialized** — Risky Agents auto-applies only after IRM is configured (analytics enabled, role groups populated, at least one explicit policy created).
4. **Region or licensing gate** — Microsoft Learn calls out PAYG / licensing prerequisites for selected Copilot-aware IRM features.
5. **AU-restricted observer** — the IRM Admin viewing the Policies list is restricted to an Administrative Unit and the Risky Agents default policy is scoped tenant-wide; the AU view filters it out.

**Diagnostic Steps.**

*Portal.* Microsoft Purview → **Insider Risk Management** → **Policies** — view the **All policies** tab from an **unrestricted** Insider Risk Management Admin context. If still absent, check **What's new** / **Roadmap** within the Purview portal; check the **Microsoft 365 Roadmap** at `microsoft.com/microsoft-365/roadmap` for the Risky Agents feature ID and rollout phase. Microsoft Purview → **Insider Risk Management** → **Settings** → **Analytics** — confirm analytics is on with ≥ 7-day baseline.

*PowerShell.*

```powershell
# Confirm IRM is initialized at the tenant
Connect-IPPSSession -ShowBanner:$false
Get-InsiderRiskPolicy | Select-Object Name, Type, Enabled, CreatedTime, LastModifiedTime
# Look for a policy with Type that resolves to a Risky Agents template name on current Learn
```

*Microsoft Graph (license / region check).*

```http
GET https://graph.microsoft.com/v1.0/organization
  ?$select=id,displayName,assignedPlans,countryLetterCode,verifiedDomains
```

Check `assignedPlans` for Microsoft Purview Insider Risk Management SKU activation; verify `countryLetterCode` against any region-restricted preview gates documented on Microsoft Learn.

*KQL (Sentinel — confirm whether the policy ever fired).*

```kusto
OfficeActivity
| where TimeGenerated > ago(30d)
| where RecordType == "ComplianceCenter"
| where Operation in ("PolicyAdded","PolicyChanged")
| where ObjectId has_cs "RiskyAgent" or PolicyName has_cs "Risky Agent"
| project TimeGenerated, UserId, Operation, ObjectId
| order by TimeGenerated desc
```

**Resolution.**

1. **Confirm cloud and ring.** Capture the cloud (`Get-MgEnvironment`) and the tenant ring (Microsoft 365 Roadmap feature ID).
2. **Initialize IRM** if not already done — populate role groups (Insider Risk Management Admins, Analysts, Investigators, Auditors, Approvers; **Approvers distinct from Investigators**), enable analytics, create at least one explicit policy (e.g., `Data theft by departing users`).
3. **Wait the documented Risky Agents auto-application window** (Microsoft Learn does not publish a definitive SLA — observe; if not present after 7 d post-initialization, open a Microsoft support ticket per §6 L4 with the payload template).
4. **Tune scope, do not delete.** Once visible, do not delete the Risky Agents policy. Tune via priority user groups (agent admins, agent owners) and priority content (sensitive SharePoint sites). Document the tuning rationale.

**Prevention.**

- **Initialization checklist.** Maintain an IRM-readiness checklist that a new IRM Admin must complete before declaring the tenant "IRM-ready" — this checklist must include the Risky Agents auto-application observation step.
- **Roadmap subscription.** AI Governance Lead subscribes to the Microsoft 365 Roadmap RSS for IRM and Copilot features; quarterly review of upcoming gates.

**Regulatory-evidence implications.**

| Authority | Exposure |
|---|---|
| **FINRA RN 24-09 / Rule 3110** | The notice re-states existing 3110/4511 obligations in the context of generative AI and agents; absence of agent-behavioral-risk detection without a documented compensating posture is a 3110(b) gap |
| **FINRA Rule 3110(b)** | Supervisory system must be reasonably designed to achieve compliance; for firms that deploy Copilot Studio agents to FINRA-supervised populations, agent-behavioral-risk detection is a reasonable component of the supervisory design |
| **OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12) / Fed SR 26-2 (formerly SR 11-7)** | Agent behavioral risk is a model-risk surface; absent IRM Risky Agents, the model-risk monitoring obligation falls to manual review (Control 2.6) |
| **NYDFS 23 NYCRR 500 §500.16** | Incident-response plan must address insider-risk events including those originating from automated/agent identities; document the compensating posture in the IR plan |

---

### Scenario 3 — Risky AI usage policy not generating alerts

**Symptom.** A `Risky AI usage` policy is configured, in scope for a Zone 3 trading-desk population, in **On** status (not Test mode), and has been live for > 14 days. The Alerts queue shows **zero alerts** despite IRM Admin's deliberate seed activity (visiting a known-blocked AI site, pasting clipboard content into a non-sanctioned external chatbot, downloading a generative-AI browser extension that violates the firm's AUP). Browser extension was assumed deployed; nobody can produce the deployment evidence.

**Likely Cause.** The signal source for `Risky AI usage` is the **browser extension** — the **Microsoft Insider risk extension** on Edge and the **Microsoft Purview extension** on Chrome — and the extension is **Windows-only**. Common gap modes:

1. **Extension not deployed via Intune** to the in-scope Windows population (admins assumed it was deployed at IRM rollout but never confirmed via Intune coverage report).
2. **Non-Edge / non-Chrome browser usage** — the in-scope population uses Firefox or Safari, which are **not supported** by the IRM browser extension family at the time of writing.
3. **macOS / Linux / iOS / Android population in scope** — the extension is **Windows-only**; non-Windows endpoints produce silent zero.
4. **Intune configuration profile assigned but not applied** — device is in a group that was excluded later; device check-in lag; user installed personal Edge/Chrome that bypasses managed Edge/Chrome extension management.
5. **Browsing indicators disabled** in IRM Settings → Policy indicators.
6. **Device not onboarded** to Microsoft Purview (endpoint signal source).
7. **PAYG dependency** for non-M365 AI sources surfaced in scope (some AI-source coverage requires PAYG enablement per Microsoft Learn).

**Diagnostic Steps.**

*Portal.* Microsoft Purview → **Insider Risk Management** → **Settings** → **Policy indicators** — confirm the relevant browsing / AI indicators (e.g., "Risky AI prompt," "Risky AI response," "Browsing risky AI site") are **enabled** and not disabled tenant-wide. Then **Settings** → **Device onboarding** — confirm the test device appears in the onboarded list. On the test device itself: Edge `edge://extensions/` and Chrome `chrome://extensions/` — confirm the Microsoft Insider risk extension (Edge) and Microsoft Purview extension (Chrome) are present, enabled, and not in error state.

Microsoft Intune admin center → **Devices** → **Configuration profiles** → [extension deployment profile] → **Device assignment status** — confirm coverage against the in-scope Windows population. **Devices** → [test device] → **Discovered apps** — confirm the extension is installed.

*PowerShell.*

```powershell
# Confirm extension policy assignment via Microsoft Graph (Intune)
Connect-MgGraph -Scopes 'DeviceManagementConfiguration.Read.All' -NoWelcome
$policies = Get-MgDeviceManagementDeviceConfiguration -All
$policies | Where-Object { $_.DisplayName -match 'Insider risk|Purview extension|IRM' } |
  Select-Object Id, DisplayName, LastModifiedDateTime

# Per-device assignment state
$policyId = '<insider-risk-extension-policy-id>'
Invoke-MgGraphRequest -Method GET `
  -Uri "https://graph.microsoft.com/beta/deviceManagement/deviceConfigurations/$policyId/deviceStatuses" |
  Select-Object -ExpandProperty value |
  Group-Object status | Select-Object Count, Name
```

*KQL (Defender XDR — extension activity).*

```kusto
DeviceProcessEvents
| where TimeGenerated > ago(7d)
| where InitiatingProcessFileName in~ ("msedge.exe","chrome.exe")
| where ProcessCommandLine has_any ("--load-extension","insider risk","purview-extension")
| summarize First = min(TimeGenerated), Last = max(TimeGenerated), Hosts = dcount(DeviceName)
  by InitiatingProcessFileName
```

```kusto
// Extension self-test: did the extension write any IRM-tagged events in the suspect window?
DeviceEvents
| where TimeGenerated > ago(7d)
| where ActionType has_any ("BrowserSensitiveSiteAccess","BrowserCopyAction","BrowserUploadAction")
| summarize Events = count() by DeviceName, AccountUpn
| order by Events desc
```

**Resolution.**

1. **Push the extension via Intune** to the in-scope Windows population. The extension is delivered as a managed Edge / Chrome extension via the Edge management policies / Chrome enterprise policies under Intune Configuration profiles. Microsoft Learn `insider-risk-management-browser-support` documents the supported deployment method; verify at deployment time.
2. **Enforce managed-browser policy.** Use Conditional Access (Control 1.11) to require that access to in-scope SaaS / AI surfaces happens from a **managed Edge** session, not an unmanaged personal browser. This closes the bypass path.
3. **Document non-Windows as a control exception.** macOS / Linux / iOS / Android in scope of `Risky AI usage` is a documented gap. Compensate via:
   - Defender for Cloud Apps reverse-proxy session controls on the SaaS-side AI surface
   - DLP for Endpoint (Control 1.17) / Endpoint DLP for clipboard / paste controls where the in-scope OS is supported
   - Communication Compliance review-cadence increase (Control 1.10)
   - Sentinel UEBA correlation (Control 3.9)
4. **Enable the relevant browsing indicators** in IRM Settings → Policy indicators if disabled.
5. **Onboard the device** to Microsoft Purview if the device check shows it is not onboarded.
6. **Enable PAYG** for non-M365 AI sources per Microsoft Learn.
7. **Re-run the seed activity** from a managed Edge / Chrome session on a covered Windows device by an in-scope identity. Allow the documented analytics window. Re-check the alerts queue.

**Prevention.**

- **Monthly extension-coverage report.** AI Governance Lead reviews Intune coverage report monthly; coverage gaps below a firm-defined threshold (e.g., 99% of in-scope Windows endpoints) trigger a SEV-2 ticket.
- **Browser-policy enforcement.** Conditional Access policy that **blocks** access to AI surfaces from unmanaged browsers on managed devices.
- **Quarterly canary.** AI Governance runs a quarterly canary seed from a managed test device; absence of the expected alert is SEV-1.
- **Browser-class register.** Inventory of the firm's actively-used browser classes per population; document non-Windows OS as `NotCovered` in the deviation register.

**Regulatory-evidence implications.**

| Authority | Exposure |
|---|---|
| **FINRA Rule 3110(b)** | Supervisory system gap on AI surface; document the compensating posture in the WSP |
| **FINRA RN 24-09 / Rule 3110** | Generative-AI tool supervision; the firm must be able to demonstrate that its AI-usage supervision is reasonably designed even on non-supported OS classes |
| **NYDFS 23 NYCRR 500 §500.06** | Audit-trail completeness; missing browser-extension signal creates an audit-trail gap on the AI surface |
| **GLBA §501(b)** | Safeguards monitoring on AI surfaces that may touch NPI |
| **SEC Reg S-P §248.30** | If the AI surface allows NPI exfiltration without detection, the firm's incident-response readiness is impaired |

---

### Scenario 4 — Data leaks (priority users) over-alerting

**Symptom.** The `Data leaks by priority users` policy is producing **400+ alerts per day**, a 12× increase over the prior baseline. The IRM Analyst queue is overwhelmed; alert review SLA is breached. Compliance is unable to perform supervisory review on the alert volume. Spot-checking shows that most alerts are **routine business activity** (a rep sending a client a standard quarterly statement; a research analyst forwarding a public report).

**Likely Cause.** The **priority user group is too broad**. Common over-broad patterns:

1. **"Everyone" is priority.** A well-meaning admin added the entire FINRA-supervised registered-rep group plus the entire RIA staff plus the entire trading desk plus all client-facing roles, totaling > 60% of the workforce. Priority-user weighting is no longer "priority" — it is the baseline.
2. **Broad SharePoint priority content list.** The priority content list includes SharePoint sites that are routine client-facing (e.g., the Client Portal site that every rep accesses many times daily).
3. **Sensitive-info type drift.** The SITs feeding the policy (Control 1.13 SITs and pattern recognition) have been recently broadened to catch a specific exfiltration vector but are now matching routine content.
4. **Outbound-email indicator over-tuned.** Outbound email to external recipients is over-weighted; routine client communication trips the indicator.
5. **Recent role-based group expansion** that pulled non-priority populations into the priority group.

**Diagnostic Steps.**

*Portal.* Microsoft Purview → **Insider Risk Management** → **Settings** → **Priority user groups** → [group] → **Members** — capture membership count and rationale per group. Then **Settings** → **Priority content** — review SharePoint site list, sensitive-info type list, sensitivity-label list. Then **Policies** → [`Data leaks by priority users`] → **Indicators** — review the indicator weights and threshold profile.

Open **Insider Risk Management → Alerts** — filter by the policy; export the last 14 d to CSV (`Export` button). Pivot in Excel by `User`, `Indicator`, `Risk score`, `Detected source` to identify which user populations and which indicators are driving the volume.

*PowerShell.*

```powershell
Connect-IPPSSession -ShowBanner:$false
# Inventory priority user group memberships (verify cmdlet names against current Learn)
Get-InsiderRiskPolicy | Where-Object { $_.Name -match 'priority' } |
  Select-Object Name, Enabled, PriorityUserGroups, ContentExpansion

# Membership of a named priority user group (via Microsoft Graph if the IRM cmdlet does not expose it)
Connect-MgGraph -Scopes 'Group.Read.All','User.Read.All' -NoWelcome
$priGroup = Get-MgGroup -Filter "displayName eq 'IRM-Priority-FrontOffice'"
Get-MgGroupMember -GroupId $priGroup.Id -All | Measure-Object
```

*KQL (Sentinel — alert-volume distribution).*

```kusto
let irmAlerts =
  OfficeActivity
  | where TimeGenerated > ago(30d)
  | where RecordType == "ComplianceCenter"
  | where Operation == "AlertReviewed" or Operation has "InsiderRisk";
irmAlerts
| extend Day = bin(TimeGenerated, 1d)
| summarize Alerts = count() by Day
| order by Day asc
```

**Resolution.**

1. **Refine the priority user group with Compliance + HR.** A priority user group is **role-based**, not "everyone." For an FSI firm, defensible priority categories include: trading desk; MNPI-handlers; agent admins / agent owners; senior management with access to ICFR-relevant data; named registered representatives with a compliance flag. Document the rationale per group.
2. **Refine the priority content list.** Remove routine client-portal SharePoint sites; keep only content that genuinely warrants priority weighting (e.g., MNPI deal rooms, board materials, regulatory-filing draft sites).
3. **Move the policy to Test mode** during the refinement. Re-baseline. Confirm alert volume drops to a reviewable level. Move back to On.
4. **Open an alert-resolution-rationale review** with Compliance — every alert closed during the over-alerting period requires a documented rationale (the supervisory record must show why the alert was dismissed).
5. **Capture the before/after configuration** as E-01 / E-06 (priority user and content snapshots).

**Prevention.**

- **Priority user group governance.** Quarterly Compliance + HR review of priority user group membership; documented sign-off; SHA-256-sealed snapshot per quarter.
- **Alert-volume SLO.** Define a firm SLO for alerts-per-reviewer-per-day on each policy. Alert breaches > SLO trigger a SEV-3 tuning ticket; do not let analysts "drink from a fire hose" with no governance response.
- **Tuning is a CAB-controlled change.** Threshold / indicator changes go through Control 2.3 Change Management; tuning during an active investigation is forbidden (anti-pattern).
- **Bias check.** Priority user groups must not become a proxy for protected-class characteristics; coordinate with Privacy + Legal + HR (Control 2.11 Bias testing).

**Regulatory-evidence implications.**

| Authority | Exposure |
|---|---|
| **FINRA Rule 3110(b)** | Over-alerting that defeats meaningful supervisory review is itself a 3110(b) finding — the supervisory system is not reasonably designed if reviewers are forced to dismiss alerts without review |
| **FINRA Rule 3110(a)** | Designation of supervisory personnel — reviewer assignment per priority user group must be documented |
| **OCC Bulletin 2026-13 (formerly OCC 2011-12) / Fed SR 26-2 (formerly SR 11-7)** | Threshold tuning is a model-input change; document under Control 2.6 |
| **State employment law** | Priority user group should not become a proxy for protected-class characteristics |

---

### Scenario 5 — Security policy violations not firing

**Symptom.** The `Security policy violations` IRM template is configured and in **On** status. Microsoft Defender for Endpoint (MDE) is deployed across the firm's Windows endpoints and is producing alerts visible in the Defender XDR portal. Yet the IRM `Security policy violations` template has **never produced an alert** in 30+ days, despite a known MDE alert (e.g., a defender-disabled event on a test device by an in-scope user).

**Likely Cause.** The IRM `Security policy violations` template depends on **Microsoft Defender for Endpoint integration** with Microsoft Purview. Without the integration enabled, the template is **silently empty**. Common gap modes:

1. **MDE integration with Purview not enabled** (one-time setup that is easy to miss).
2. **MDE licensing gap** — the in-scope users are not licensed for MDE Plan 2 (some integration features require MDE P2).
3. **Device onboarded to Purview but not to MDE** (or vice versa) — the IRM signal pipeline requires both onboardings to overlap.
4. **MDE alert severity filter** in IRM excludes the severity tier the test alert was raised at.
5. **Time-of-event mismatch** — the user was not in scope of the IRM policy at the time of the MDE alert.

**Diagnostic Steps.**

*Portal.* Microsoft Defender XDR portal (`security.microsoft.com`) → **Settings** → **Endpoints** → **General** → **Advanced features** → confirm **Microsoft Compliance Center** integration toggle is **On**. Then Microsoft Purview → **Insider Risk Management** → **Settings** → **Connectors** → confirm `Microsoft Defender for Endpoint` shows **Connected**. Then Microsoft Purview → **Settings** → **Device onboarding** vs. Defender XDR → **Assets** → **Devices** — set diff the two device populations.

Microsoft 365 admin center → **Billing** → **Licenses** — confirm the in-scope users carry MDE P2 (or the equivalent E5 / E5 Security bundle).

*PowerShell.*

```powershell
# Defender XDR — onboarded device list (requires Defender for Endpoint API access via Microsoft Graph)
Connect-MgGraph -Scopes 'DeviceManagementManagedDevices.Read.All' -NoWelcome
Get-MgDeviceManagementManagedDevice -All |
  Select-Object DeviceName, OperatingSystem, ManagedDeviceOwnerType, ComplianceState, LastSyncDateTime |
  Where-Object { $_.OperatingSystem -match 'Windows' } |
  Group-Object ComplianceState | Select-Object Count, Name
```

*KQL (Defender XDR — confirm the test alert was raised).*

```kusto
AlertInfo
| where TimeGenerated > ago(7d)
| where DetectionSource == "WindowsDefenderAtp" or ServiceSource == "Microsoft Defender for Endpoint"
| where Title has_any ("Security policy","Defender disabled","Tampering","Antivirus disabled")
| project TimeGenerated, AlertId, Title, Severity, Category, AccountUpn = tostring(Entities[0].AccountUpn)
| order by TimeGenerated desc
```

```kusto
// Cross-reference: did the alert account fall in the IRM policy scope at the alert UTC?
let inScope = externaldata(Upn:string)["https://<your-evidence-blob>/irm-scope.csv"];
AlertInfo
| where TimeGenerated > ago(7d)
| extend AccountUpn = tostring(Entities[0].AccountUpn)
| where AccountUpn in (inScope)
```

**Resolution.**

1. **Enable the MDE → Compliance integration toggle** as **Defender Security Admin** (this role is required; not held by IRM Admins).
2. **License gap remediation.** Coordinate with the licensing owner; assign MDE P2 to the in-scope users.
3. **Onboard missing devices** to whichever side is lagging (Purview vs. MDE).
4. **Re-confirm IRM policy indicators** include the MDE-derived security-policy indicators per current Microsoft Learn (`insider-risk-management` — Security policy violations template section).
5. **Re-run the seed event** (or wait for a real MDE event) and confirm an IRM alert materializes.

**Prevention.**

- **Integration health daily check.** Daily Sentinel KQL that asserts the MDE → Compliance connector heartbeat; alert SEV-2 on silence > 24 h.
- **License-assignment automation.** Group-based licensing in Microsoft Entra so that membership in the in-scope groups automatically assigns MDE P2.
- **Device-onboarding parity check.** Weekly automation that set-diffs Purview onboarded vs. MDE onboarded; gap > firm threshold triggers SEV-3.

**Regulatory-evidence implications.**

| Authority | Exposure |
|---|---|
| **FINRA Rule 3110(b)** | Endpoint security-policy circumvention by an insider is a supervisory event; absent IRM correlation, the firm relies on MDE alone |
| **NYDFS 23 NYCRR 500 §500.06** | Endpoint audit-trail completeness |
| **GLBA §501(b)** | Endpoint safeguards monitoring |
| **SEC Reg S-P §248.30** | Endpoint compromise that touches NPI requires the firm's documented incident response — IRM correlation accelerates the determination clock |

---

### Scenario 6 — Defender for Cloud Apps anomaly silence post-June-2025 migration

**Symptom.** The IRM `Data leaks` policy was previously enriched by Defender for Cloud Apps anomaly signals (mass download from third-party cloud, impossible travel, unusual file share). Following the **June 2025 dynamic threat detection migration** by Microsoft, the legacy detections appear to have been renamed or disabled, and IRM alert enrichment has stopped. The Defender for Cloud Apps Activity log still shows raw events; IRM is not consuming them.

**Likely Cause.** Microsoft migrated parts of Defender for Cloud Apps anomaly detection in June 2025 (verify the exact migration name and date on current Microsoft Learn — names change). Common downstream symptoms:

1. **Legacy detection renamed**; the IRM connector mapping references the old detection name and no longer matches.
2. **Legacy detection disabled / retired**; replacement detection requires explicit opt-in.
3. **Connector schema change**; the IRM-side ingestion silently drops events that no longer match the expected schema.
4. **Permission scope expanded** by the migration; the connector's service principal now lacks a newly-required scope.

**Diagnostic Steps.**

*Portal.* Microsoft Defender XDR → **Settings** → **Cloud Apps** → **Threat protection** → **Policies** — review which anomaly detection policies are **enabled** vs. **disabled**; cross-reference to the post-migration policy names per current Microsoft Learn. Then Microsoft Defender XDR → **Cloud Apps** → **Activity log** — confirm raw activity is still ingesting from the connectors. Then Microsoft Purview → **Insider Risk Management** → **Settings** → **Connectors** → **Microsoft Defender for Cloud Apps** → confirm last-sync UTC and error state.

*PowerShell / Microsoft Graph.*

```powershell
# Defender for Cloud Apps activity API — confirm raw activity is flowing
# (uses Microsoft Defender for Cloud Apps REST API; replace <tenant>.<region>.portal.cloudappsecurity.com)
$headers = @{ Authorization = "Bearer $env:DCA_TOKEN" }
$body = @{ filters = @{ date = @{ gte_ndays = 1 } }; limit = 10 } | ConvertTo-Json
Invoke-RestMethod -Method Post `
  -Uri "https://<tenant>.<region>.portal.cloudappsecurity.com/api/v1/activities/" `
  -Headers $headers -Body $body -ContentType 'application/json'
```

*KQL (Sentinel — anomaly-event volume over the migration window).*

```kusto
// Did Defender for Cloud Apps anomaly events drop at the migration UTC?
let migrationUtc = datetime(2025-06-15);
CloudAppEvents
| where TimeGenerated > ago(120d)
| where ActionType has_any ("Anomaly","ImpossibleTravel","MassDownload","UnusualFileShare")
| summarize Events = count() by bin(TimeGenerated, 1d)
| extend WindowSide = iff(TimeGenerated < migrationUtc, "pre", "post")
| order by TimeGenerated asc
```

```kusto
// Cross-reference to IRM enrichment — did IRM stop receiving the enriched signal?
OfficeActivity
| where TimeGenerated > ago(120d)
| where Operation has "InsiderRisk" and AdditionalInfo has "CloudAppSecurity"
| summarize Events = count() by bin(TimeGenerated, 1d)
| order by TimeGenerated asc
```

**Resolution.**

1. **Read the migration release notes** for Defender for Cloud Apps — Microsoft Learn `defender-for-cloud-apps/whats-new`. Identify the specific policies affected, the new policy names, and any opt-in steps.
2. **Re-enable / opt-in to the replacement detections** as **Defender for Cloud Apps Admin**.
3. **Re-map the IRM connector** if the schema or naming change requires it (Microsoft Purview → Insider Risk Management → Settings → Connectors → Defender for Cloud Apps → reconfigure). Document the before/after mapping.
4. **Re-grant any newly-required permission scopes** to the connector service principal.
5. **Validate post-migration enrichment** — generate a benign test signal (e.g., a controlled mass download by a synthetic user from a sanctioned cloud) and confirm the enriched IRM alert materializes.
6. **Document the dead window** — capture the UTC range during which enrichment was silent; report to Compliance with the compensating posture in force during the window.

**Prevention.**

- **Microsoft 365 Roadmap subscription** for Defender for Cloud Apps; quarterly review by AI Governance Lead and CISO delegate.
- **Migration drill** as part of standard release management — when a Microsoft migration is announced, the AI Governance Lead opens a tracking ticket, validates pre/post telemetry, and signs off on the post-migration baseline.
- **Connector heartbeat alerting** — KQL that alerts SEV-2 on > 24 h silence in IRM-bound Defender for Cloud Apps enrichment events.

**Regulatory-evidence implications.**

| Authority | Exposure |
|---|---|
| **NYDFS 23 NYCRR 500 §500.16** | Incident-response plan must address vendor-side detection changes |
| **FINRA Rule 3110(b)** | Document the supervisory-system response to vendor migration windows |
| **OCC Bulletin 2013-29** | Third-party / vendor risk — Microsoft is a critical third party; vendor-side changes must be tracked and assessed |
| **OCC Bulletin 2026-13 (formerly OCC 2011-12) / Fed SR 26-2 (formerly SR 11-7)** | If anomaly detection is treated as a model input, the migration is a model change requiring reassessment |

---

### Scenario 7 — Entra ID Protection signals not feeding IRM

**Symptom.** A user shows **High** risk in **Microsoft Entra ID Protection** (atypical travel + leaked credentials + anomalous token issuance) but no corresponding IRM alert appears for that user even though they are in scope of an IRM `Risky behaviors` policy that is configured to consume Entra ID Protection signals. The Compliance team expects insider-risk correlation when identity risk is elevated; correlation is silent.

**Likely Cause.**

1. **Risk detection in `Remediated` or `Dismissed` state** — IRM consumes **active** risk signals; once IT Helpdesk dismisses a user-risk row, it stops contributing to IRM correlation.
2. **License tier check failure** — Entra ID Protection requires Microsoft Entra ID P2 (or equivalent E5 bundle) on the in-scope users; in-scope users on P1 produce no signal.
3. **IRM connector for Entra ID Protection not enabled** in Microsoft Purview > Insider Risk Management > Settings > Connectors.
4. **Risk-detection type filter mismatch** — IRM may consume only specific Entra risk-detection types; a sign-in risk that the firm cares about may be filtered out by the IRM mapping.
5. **AU restriction** on the IRM Admin checking the alert; the user is outside the admin's AU.

**Diagnostic Steps.**

*Portal.* Microsoft Entra admin center → **Identity Protection** → **Risky users** — confirm the user's `risk state` is **At risk** (not `Confirmed safe`, `Dismissed`, or `Remediated`). Then **Risk detections** — confirm the detection types and timestamps. Microsoft Purview → **Insider Risk Management** → **Settings** → **Connectors** → confirm `Microsoft Entra ID Protection` connector shows **Connected** with recent sync UTC. Microsoft Entra → **Licenses** — confirm the user is licensed for Entra ID P2.

*PowerShell / Microsoft Graph.*

```powershell
Connect-MgGraph -Scopes 'IdentityRiskyUser.Read.All','IdentityRiskEvent.Read.All' -NoWelcome

# Risky user state
Get-MgRiskyUser -All |
  Where-Object { $_.UserPrincipalName -eq 'subject@contoso.com' } |
  Select-Object UserPrincipalName, RiskLevel, RiskState, RiskLastUpdatedDateTime

# Risk detections for that user
Get-MgRiskDetection -All |
  Where-Object { $_.UserPrincipalName -eq 'subject@contoso.com' } |
  Select-Object DetectedDateTime, RiskEventType, RiskLevel, RiskState |
  Sort-Object DetectedDateTime -Descending |
  Select-Object -First 20

# License entitlement
Get-MgUser -UserId 'subject@contoso.com' -Property AssignedPlans |
  Select-Object -ExpandProperty AssignedPlans |
  Where-Object { $_.Service -match 'AAD' } | Format-Table Service, ServicePlanId, CapabilityStatus
```

*KQL (Sentinel — sign-in risk vs IRM correlation).*

```kusto
SigninLogs
| where TimeGenerated > ago(7d)
| where UserPrincipalName == "subject@contoso.com"
| where RiskLevelDuringSignIn in ("medium","high")
| project TimeGenerated, UserPrincipalName, RiskLevelDuringSignIn, RiskEventTypes_V2, IPAddress, AppDisplayName
```

```kusto
// Did IRM ingest the Entra signal?
OfficeActivity
| where TimeGenerated > ago(7d)
| where Operation has "InsiderRisk" and AdditionalInfo has "EntraIdProtection"
| where UserId == "subject@contoso.com"
```

**Resolution.**

1. Re-enable the Entra ID Protection connector in IRM Settings as **Insider Risk Management Admin**.
2. Coordinate with the licensing owner to assign Entra ID P2 to the in-scope population.
3. Update the firm's risk-handling SOP — risk-state dismissal by IT Helpdesk **must** be coordinated with IRM Analyst review, otherwise the dismissal silently terminates IRM correlation.
4. Re-trigger the seed scenario from a synthetic test user with a controlled risky sign-in (e.g., from a documented test-VPN egress IP) and confirm IRM enrichment.
5. Document the dead window and the affected user population.

**Prevention.**

- **Risk-state dismissal governance.** IT Helpdesk SOP requires checking IRM correlation before dismissing a user-risk row; document with a checklist.
- **License-assignment automation.** Group-based licensing for Entra ID P2 per in-scope group.
- **Connector heartbeat alerting** for the Entra ID Protection → IRM signal path.

**Regulatory-evidence implications.**

| Authority | Exposure |
|---|---|
| **NYDFS 23 NYCRR 500 §500.12** | Multi-factor / identity controls — risky sign-in handling is part of the firm's identity-control posture |
| **FFIEC Authentication guidance** | Layered authentication; identity-risk correlation with insider-risk informs the firm's authentication-posture decision |
| **GLBA §501(b)** | Identity-based access control on systems handling NPI |
| **NYDFS §500.16** | Incident-response plan must address compromised-credential events |

---

### Scenario 8 — HR connector health red

**Symptom.** Microsoft Purview → **Data connectors** → **HR (Microsoft 365)** shows **last successful run > 24 h ago**; the status is **Failed** or **Warning**. The `Data theft by departing users` policy has not produced alerts for any of the three known leavers in the suspect window even though their `LastWorkingDate` was set in the HRIS three days ago.

**Likely Cause.**

1. **Certificate or client secret expired** on the Microsoft Entra app registration backing the HR connector.
2. **Schema drift** — the HRIS team added or renamed a column in the upload CSV; the connector's field mapping no longer aligns. `EmployeeID`, `ResignationDate`, `LastWorkingDate`, `EmploymentStatus` are the high-impact fields.
3. **Storage / staging account** issue (where ingestion uses a staging blob; SAS expiry; container ACL change).
4. **Dual-system conflict** — same `EmployeeID` arriving from two HR sources with conflicting `LastWorkingDate`.
5. **Source HRIS does not publish `LastWorkingDate`** for a worker class (e.g., contractors) — the IRM template silently has no trigger date.
6. **Network egress block** — a firewall change broke the egress path used by the upload script.

**Diagnostic Steps.**

*Portal.* Microsoft Purview → **Data connectors** → **HR (Microsoft 365)** → [connector] → confirm last-success UTC, last-error message, ingestion row count, schema. Then Microsoft Purview → **Insider Risk Management** → **Policies** → [`Data theft by departing users`] → **Conditions** → activity lookback. Microsoft Entra admin center → **App registrations** → [HR connector app] → **Certificates & secrets** → confirm expiry > 30 d out.

*PowerShell.*

```powershell
# Pull HR connector job status via Microsoft Purview connector API (verify cmdlet names per current Learn)
Connect-IPPSSession -ShowBanner:$false
Get-PurviewConnectorJob -ConnectorType HR -Top 10 |
  Select-Object JobId, Status, StartedUtc, CompletedUtc, RowsProcessed, RowsFailed, ErrorMessage

# Verify the certificate / secret expiry on the backing app registration
Connect-MgGraph -Scopes 'Application.Read.All' -NoWelcome
$app = Get-MgApplication -Filter "displayName eq 'IRM-HR-Connector'"
$app.PasswordCredentials | Select-Object DisplayName, EndDateTime
$app.KeyCredentials      | Select-Object DisplayName, EndDateTime
```

*Sample row check (the canonical departing-user pattern).*

```powershell
# From the upload CSV staging location — confirm a known leaver row has both fields populated
Import-Csv .\hr-upload-2026-04-15.csv |
  Where-Object EmployeeID -eq 'E000123' |
  Select-Object EmployeeID, ResignationDate, LastWorkingDate, EmploymentStatus
# Expected: ResignationDate AND LastWorkingDate both populated (ISO-8601 dates)
```

**Resolution.**

1. **Rotate the certificate / secret** on the Microsoft Entra app registration; update connector configuration; re-run job.
2. **Re-map fields** if the HRIS schema drifted — particularly `EmployeeID`, `ResignationDate`, `LastWorkingDate`, `EmploymentStatus`. Document the mapping change in the connector's runbook.
3. **Renew the SAS** on the staging blob if storage is in the path; tighten the SAS to least-privilege and time-bounded.
4. **Reconcile dual-source conflicts** at the HRIS side; do not let IRM consume conflicting truth.
5. **Coordinate with HR** for any worker class missing `LastWorkingDate` — for contractors, define a documented manual flag flow.
6. **Allow a network egress exception** for the upload script if a firewall change blocked the path.
7. **Manual leaver flagging during the connector outage** — work with HR to manually flag known leavers in IRM during the dead window; document the manual flagging in the incident ticket.

**Prevention.**

- **Connector freshness SLO** — `last-success ≤ 24 h`; alert SEV-2 on breach.
- **Certificate rotation calendar** — schedule rotation 30 d before expiry; integrate with the firm's secret-management lifecycle.
- **HRIS schema-change advance notice** — HR / HRIS team commits to ≥ 14 d advance notice on schema changes; if not honored, a CAB ticket records the deviation.
- **Synthetic-leaver canary** — a synthetic test user flagged as a leaver weekly; absence of the corresponding IRM alert is SEV-2.

**Regulatory-evidence implications.**

| Authority | Exposure |
|---|---|
| **FINRA Rule 3110(b)** | Departing-user data-theft monitoring is a recognized supervisory practice for FINRA-supervised reps; HR connector silence is a supervisory-coverage gap |
| **FINRA Rule 4530** | If a leaver event surfaces misconduct, the firm's reporting obligations apply |
| **GLBA §501(b)** | Departing-user NPI exfiltration is a classic safeguards-monitoring trigger |
| **SEC Reg S-P §248.30** | Departing-user breach scenarios fall within the firm's incident-response readiness |

---

### Scenario 9 — Forensic Evidence capture stuck "Pending Approval"

**Symptom.** An Insider Risk Management Investigator submitted a Forensic Evidence capture request 6 hours ago for a high-severity case. The request status is **Pending Approval**. The Investigator is the on-call SOC analyst for the case and is blocked from collecting the evidence required for the investigation. Attempting to escalate, the Investigator finds **no Approver listed on the request**.

**Likely Cause.**

1. **Approver group empty** — the role group `Insider Risk Management Approvers` has zero members.
2. **Investigator-Approver overlap (SoD violation)** — the Investigator is also a member of the Approvers role group; some implementations block self-approval, leaving the request orphaned.
3. **Approver group populated but all members are out of office / disabled / on PTO**.
4. **Role-propagation lag** — Approver was added < 30 min ago; permission has not propagated.
5. **Approval workflow notification not delivered** (mailbox rule, Teams notification not enrolled).

**Diagnostic Steps.**

*Portal.* Microsoft Purview → **Insider Risk Management** → **Forensic Evidence** → **Requests** → [request] → confirm assigned Approver, status, request UTC. Then Microsoft Purview → **Permissions** (or **Roles & scopes**) → **Insider Risk Management Approvers** → confirm membership and that members are **not** also in **Insider Risk Management Investigators**.

*PowerShell / Microsoft Graph.*

```powershell
Connect-MgGraph -Scopes 'RoleManagement.Read.Directory','Group.Read.All' -NoWelcome

# Confirm Approvers role group membership and SoD against Investigators
$approvers     = Get-MgGroup -Filter "displayName eq 'Insider Risk Management Approvers'"
$investigators = Get-MgGroup -Filter "displayName eq 'Insider Risk Management Investigators'"

$apprMembers = Get-MgGroupMember -GroupId $approvers.Id     -All | ForEach-Object { $_.Id }
$invMembers  = Get-MgGroupMember -GroupId $investigators.Id -All | ForEach-Object { $_.Id }

# SoD violation = non-empty intersection
$violations = $apprMembers | Where-Object { $invMembers -contains $_ }
if ($violations) { Write-Warning "SoD violation: $($violations.Count) overlap(s)" }
if ($apprMembers.Count -eq 0) { Write-Warning "Approvers role group is EMPTY (zero-approver state) — SEV-1" }
```

*KQL (Sentinel — capture-request lifecycle).*

```kusto
OfficeActivity
| where TimeGenerated > ago(7d)
| where RecordType == "ComplianceCenter"
| where Operation in (
    "ForensicEvidenceCaptureRequested",
    "ForensicEvidenceCaptureApproved",
    "ForensicEvidenceCaptureRejected",
    "ForensicEvidenceCaptureExpired")
| project TimeGenerated, UserId, Operation, ObjectId, AdditionalInfo
| order by TimeGenerated desc
```

**Resolution.**

1. **Populate the Approvers role group** with members **distinct from Investigators** as **Purview Compliance Admin**. Recommended membership: a small set of senior personnel from Compliance + Privacy + an independent senior IRM Analyst, signed off by CISO and General Counsel.
2. **Resolve any Investigator-Approver overlap** — remove the overlap as a SEV-2 SoD remediation per Scenario 21.
3. **Wait the documented role-propagation window** (up to 30 min per Microsoft Learn) before re-attempting submit.
4. **Re-submit the request** as the same Investigator; confirm an Approver is now assigned; Approver reviews and approves with documented justification (state-law notice posture, investigation reason).
5. **Document the dead window** and any compensating evidence-collection (e.g., MDE live response, eDiscovery (Premium) collection) used during the window.

**Prevention.**

- **Approvers-not-empty SLO.** Daily check; alert SEV-1 if `Insider Risk Management Approvers` membership = 0.
- **SoD daily check.** Daily intersection check between Investigators and Approvers; intersection ≠ 0 is SEV-2 (Scenario 21).
- **Approver coverage matrix.** Document at least N=3 active Approvers with distinct PTO / holiday schedules so single-approver absence does not block evidence collection.
- **Approval SLA.** Define a firm SLA for Approver response (e.g., 4 h business hours); breach triggers an escalation to the AI Governance Lead.

**Regulatory-evidence implications.**

| Authority | Exposure |
|---|---|
| **FINRA Rule 3110(b)** | Dual-authorization is itself a supervisory control; an empty Approver group defeats it |
| **NYDFS 23 NYCRR 500 §500.07** | Access privileges — dual-control is a demonstrated FSI hardening pattern |
| **SOX §404 ICFR** | Dual-control on evidence collection is an ITGC pattern |
| **State employee-monitoring law (CT, DE, NY)** | Dual-auth is part of the documented monitoring posture; absence undermines the firm's "reasonable" employer-monitoring posture |

---

### Scenario 10 — Forensic Evidence policy creation rejected

**Symptom.** The IRM Admin attempts to create a Forensic Evidence policy in **Microsoft Purview → Insider Risk Management → Forensic Evidence → Policies → Create policy** and receives an error such as *"Microsoft Purview Client is not deployed to any onboarded device in this scope"* or *"Pay-as-you-go billing is required for Forensic Evidence."* Policy creation is blocked.

**Likely Cause.**

1. **Microsoft Purview Client not deployed** to the in-scope Windows 10/11 Enterprise devices via Intune; Forensic Evidence requires the client.
2. **PAYG billing not enabled** on the tenant; Forensic Evidence is a PAYG capability.
3. **Devices not onboarded** to Microsoft Purview (separate from Microsoft Defender for Endpoint onboarding).
4. **Windows edition mismatch** — devices are Windows 10/11 Pro (not Enterprise); Forensic Evidence is Enterprise-only.
5. **Region unavailability** — Forensic Evidence not available in the tenant's cloud.
6. **Capture-policy prerequisite missing** — the upstream IRM policy referenced by the Forensic Evidence policy is not yet created or is in Test mode.

**Diagnostic Steps.**

*Portal.* Microsoft Purview → **Settings** → **Forensic Evidence** → **Settings** → confirm PAYG is **enabled** and storage cap is set. Microsoft Purview → **Settings** → **Device onboarding** → confirm in-scope devices are onboarded. Microsoft Intune → **Apps** → confirm the Microsoft Purview Client deployment profile and coverage report. Microsoft Intune → **Devices** → [test device] → **Discovered apps** → confirm `Microsoft Purview Client` is installed.

*PowerShell.*

```powershell
# Confirm PAYG enrollment for Forensic Evidence
Connect-IPPSSession -ShowBanner:$false
Get-IRMConfiguration | Format-List ForensicEvidenceEnabled, PayAsYouGoEnabled, ForensicStorageCapGB

# Confirm Purview Client deployment via Intune (Microsoft Graph)
Connect-MgGraph -Scopes 'DeviceManagementApps.Read.All' -NoWelcome
Get-MgDeviceAppManagementMobileApp -All |
  Where-Object { $_.DisplayName -match 'Microsoft Purview Client' } |
  Select-Object Id, DisplayName, Publisher, CreatedDateTime
```

*KQL (confirm device class).*

```kusto
DeviceInfo
| where TimeGenerated > ago(7d)
| where OnboardingStatus == "Onboarded"
| summarize Devices = dcount(DeviceName) by OSPlatform, OSVersionInfo, OSVersion
| order by Devices desc
```

**Resolution.**

1. **Enable PAYG** as **Azure Subscription Owner** in the Azure subscription supporting the tenant; bind to the IRM tenant.
2. **Push the Microsoft Purview Client** via Intune to the in-scope Windows 10/11 Enterprise population. Validate coverage report.
3. **Onboard missing devices** to Microsoft Purview (separate from MDE; both are required).
4. **Edition gap** — coordinate with the device-management team to upgrade Windows 10/11 Pro devices to Enterprise via the firm's licensing program where Forensic Evidence is required.
6. **Re-attempt policy creation** after each prerequisite is satisfied.

**Prevention.**

- **Pre-flight checklist** for Forensic Evidence rollout: PAYG ✓, Purview Client deployed ✓, Devices onboarded ✓, Windows edition Enterprise ✓, Approvers role group populated and distinct from Investigators ✓, state-law notice posture confirmed ✓.
- **Storage cap alerting** — alert SEV-3 at 70% storage cap, SEV-2 at 90%, SEV-1 at 99%.
- **Quarterly client-version drift check** — confirm devices are on the supported Purview Client version; out-of-support versions silently fail to capture.

**Regulatory-evidence implications.**

| Authority | Exposure |
|---|---|
| **FINRA Rule 3110(b)** | Forensic Evidence absence does not by itself create a 3110 finding, but the firm should document its evidence-collection capability in the WSP |
| **State employee-monitoring law (CT, DE, NY)** | The firm must document the monitoring posture **before** capture; pre-flight notice is part of the posture |
| **GLBA §501(b)** | Evidence-collection capability supports the safeguards monitoring program |

---

### Scenario 11 — Forensic clip approaching 120-day expiry without export

**Symptom.** Automated check identifies a Forensic Evidence clip that is **115 days old**, attached to an open IRM case, and has **not been exported**. The clip auto-deletes at 120 days. If lost, the firm cannot reconstruct the visual evidence supporting the investigation; the investigation may stall or have to rely on second-best evidence (audit logs, file-access events) that does not show the user's screen state.

**Likely Cause.** No export workflow was triggered after capture. Common reasons:

1. **Investigator captured the clip but did not own the post-capture export step** — handoff to Records Retention or eDiscovery hold was not in the Investigator's runbook.
2. **Approver pipeline ignored the post-capture step** — Approver focused on capture approval, not retention promotion.
3. **No automated alert** at the 90-day threshold; the case sat in the queue past the warning window.
4. **Records Retention label not yet defined** for Forensic Evidence clips in Control 1.9; the Investigator did not know which label to apply.
5. **eDiscovery (Premium) hold not in place** for the case subject; legal hold path was not invoked.

**Diagnostic Steps.**

*Portal.* Microsoft Purview → **Insider Risk Management** → **Forensic Evidence** → **Captures** → filter by capture UTC > 90 days ago. For each clip: view the capture UTC, the case ID, the requesting Investigator, the approving Approver, and the retention countdown.

*PowerShell.*

```powershell
# Inventory clips approaching expiry
Connect-IPPSSession -ShowBanner:$false
$today = (Get-Date).ToUniversalTime()
$clips = Get-IRMForensicCapture -Top 1000 |
  Select-Object CaptureId, CaseId, CaptureUtc, RequestingInvestigator, ApprovingApprover,
                @{n='AgeDays';e={ ($today - $_.CaptureUtc).Days }},
                @{n='DaysToExpiry';e={ 120 - ($today - $_.CaptureUtc).Days }} |
  Where-Object DaysToExpiry -le 30 |
  Sort-Object DaysToExpiry
$clips | Format-Table -AutoSize
```

*KQL (Sentinel — clip-expiry watchlist).*

```kusto
OfficeActivity
| where TimeGenerated > ago(120d)
| where Operation == "ForensicEvidenceCaptureApproved"
| extend AgeDays = datetime_diff('day', now(), TimeGenerated)
| where AgeDays > 90
| project CaptureUtc = TimeGenerated, AgeDays, CaseId = ObjectId, Investigator = UserId
| order by AgeDays desc
```

**Resolution — Emergency Export Workflow.**

1. **Convene the case team within 4 h** of identifying the at-risk clip — Investigator + Approver + Compliance + Legal + Privacy + Records Retention Custodian.
2. **Determine retention path:**
   - **Path A — Records Retention label (Control 1.9).** Apply the firm's `FSI-Records-7yr-WORM` (or stricter) retention label to the exported clip and store in the immutable evidence bucket.
   - **Path B — eDiscovery (Premium) hold (Control 1.19).** If litigation / regulatory hold is in scope, place the subject's mailbox / OneDrive / Teams on eDiscovery hold and add the exported clip to the eDiscovery case as a custodian-content item.
   - **Path C — Both** — apply the retention label **and** add to the eDiscovery hold; do not let a single point of failure (label deleted, hold released) lose the evidence.
3. **Export the clip** via the Forensic Evidence portal or PowerShell; capture the export manifest with SHA-256 sidecar; store in the Control 1.7 evidence bucket.
4. **Cross-record the export** in both the IRM case and the eDiscovery case (where applicable).
5. **Document the case team's decision** on retention duration with Compliance + Legal sign-off.

**Prevention.**

- **Automated 90-day alert.** Daily Sentinel KQL that lists clips with `DaysToExpiry ≤ 30`; auto-create a SEV-3 ticket assigned to the IRM Admin and Investigator. At `DaysToExpiry ≤ 14` escalate to SEV-2.
- **Post-capture runbook step.** Investigator runbook includes the retention-promotion step as a hard requirement on case open.
- **Quarterly clip-aging review.** AI Governance Lead reviews the clip-aging report quarterly; any clip past 60 days without a documented retention path is a finding.
- **Records Retention label pre-defined** for Forensic Evidence clips per Control 1.9; the Investigator should not have to define the label at the moment of crisis.

**Regulatory-evidence implications.**

| Authority | Exposure |
|---|---|
| **FINRA Rule 4511 / SEC Rule 17a-3** | If the clip is treated as a record (it usually is once attached to a supervisory case), make-and-preserve applies |
| **SEC Rule 17a-4(b)(4)** | WORM retention; Forensic Evidence native storage is **not** WORM — promotion to a WORM substrate is required |
| **CFTC Rule 1.31** | If the case touches covered swap / trading activity, CFTC retention applies |
| **NYDFS §500.06** | Audit-trail completeness; clip loss is an audit-trail gap |

---

### Scenario 12 — State employee-monitoring law non-compliance discovered post-deployment

**Symptom.** Privacy Officer discovers — three weeks after Forensic Evidence policy go-live — that a captured user is a resident of **New York** (or Connecticut or Delaware), and that the firm did **not** post the required prior written employee-monitoring notice before capture. Employment counsel flags potential exposure under the state's employee electronic monitoring statute. The captured clip exists in Forensic Evidence storage.

**Likely Cause.**

1. **State residency was not part of the Forensic Evidence pre-flight check** — the IRM Admin assumed user residency = work location, missing remote workers.
2. **Employee notice posture was assumed** (e.g., signed at hire) but the state statute may require **specific** monitoring notice, not generic boilerplate.
3. **HR did not flag the user's residency change** to Privacy.
4. **Privacy + Legal sign-off was not a hard gate** on policy creation.

**Diagnostic Steps.**

*Portal.* Microsoft Purview → **Insider Risk Management** → **Forensic Evidence** → **Captures** → filter by user. Microsoft Entra → **Users** → [user] → confirm work location and any custom-attribute residency flag. Cross-reference to HR system of record (Workday / SuccessFactors) for residency.

*PowerShell.*

```powershell
# Inventory captures for users in subject states (requires HR integration)
Connect-MgGraph -Scopes 'User.Read.All' -NoWelcome
$users = Get-MgUser -All -Property Id, UserPrincipalName, State, Country, EmployeeOrgData
$inSubjectStates = $users | Where-Object { $_.State -in @('NY','CT','DE') -and $_.Country -eq 'US' }

Connect-IPPSSession -ShowBanner:$false
$captures = Get-IRMForensicCapture -Top 1000
$captures | Where-Object { $_.SubjectUpn -in $inSubjectStates.UserPrincipalName } |
  Select-Object CaptureUtc, SubjectUpn, CaseId, RequestingInvestigator
```

**Resolution — Emergency Suspension and Remediation.**

1. **Immediate suspension of new captures** for all users in the affected states (CT / DE / NY at minimum; check counsel for any other states with applicable statutes). As **Insider Risk Management Admin**, scope-down the Forensic Evidence policy to exclude these users; document the change as an emergency suspension.
2. **Convene Privacy + Legal + HR + Compliance within 4 h** to assess:
   - Whether existing captured clips must be **deleted** (some statutes require destruction of unlawfully-collected evidence) or **preserved** (litigation hold may override).
   - Whether **employee notification** is required and what the notification text should say.
   - Whether **regulator notification** (state AG, NYDFS where applicable) is required.
   - Whether the firm has a remediation timeline obligation.
3. **Implement notice posture** per Legal direction — typically a written monitoring notice acknowledged by the employee before any future capture.
4. **Resume capture only after** Privacy + Legal + HR sign-off and signed notice acknowledgment from the affected employees.
5. **Privacy register update** — log the incident, the affected user count, the remediation, and the sign-off chain.
6. **Post-incident review** within 30 d, with documented control changes (e.g., add residency-state pre-flight check to Forensic Evidence policy creation; add HR integration to flag residency changes).

**Prevention.**

- **Residency-aware pre-flight** — Forensic Evidence policy creation requires confirmation that all in-scope users have the firm's documented monitoring notice on file for their state.
- **HR integration** — residency change in the HRIS triggers a Privacy review of any IRM monitoring scope including the user.
- **Privacy + Legal + HR as hard gates** on Forensic Evidence policy creation, change, and scope expansion.
- **Monitoring notice register** — maintain a register of which employees have signed which version of the monitoring notice; tie to Forensic Evidence eligibility.

**Regulatory-evidence implications.**

| Authority | Exposure |
|---|---|
| **NY Civil Rights Law §52-c** | Electronic monitoring notice obligation; private right of action exposure |
| **CT Gen. Stat. §31-48d** | Electronic monitoring notice obligation; civil penalty |
| **DE Code Title 19 §705** | Electronic monitoring notice obligation; civil penalty |
| **GLBA §501(b)** | Privacy program obligations; non-compliance is a programmatic finding |
| **NYDFS 23 NYCRR 500 §500.16** | Incident-response plan must address monitoring-program incidents |
| **State AG enforcement** | Several state AGs have brought employee-monitoring enforcement actions |

---

### Scenario 13 — Triage Agent fails to refresh after 90 days

**Symptom.** The IRM Triage Agent (Security Copilot–powered) was working for the first 90 days post-enrollment. On day 91 it fails to refresh: alerts are no longer being prioritized; the Triage Agent dashboard shows **"Authentication expired"** or **"Capacity unavailable."** Analysts revert to manual triage; alert-review SLA slips.

**Likely Cause.**

1. **Saved-authentication expired** — Triage Agent uses a delegated/saved-auth context that expires on a schedule documented per current Microsoft Learn.
2. **Security Copilot SCU (Security Compute Unit) capacity exhausted** — concurrent capacity allocation exceeded; Triage Agent silently degrades.
3. **PAYG billing issue** — the underlying PAYG subscription has a billing failure (expired payment method, exceeded budget cap).
4. **Plug-in / role assignment lapsed** during a Security Copilot upgrade.
5. **Feature lifecycle churn** — the Triage Agent moved from one preview ring to another; opt-in must be refreshed.

**Diagnostic Steps.**

*Portal.* Microsoft Security Copilot portal → **Settings** → **Owner settings** → **Capacity** — confirm SCU allocation and current consumption. Microsoft Purview → **Insider Risk Management** → **Triage Agent** → **Status** — confirm last-successful-run UTC and any error message. Azure portal → **Subscriptions** → [Security Copilot subscription] → **Cost analysis** and **Cost alerts** — confirm no billing failure.

*PowerShell.*

```powershell
# Verify Security Copilot capacity (Microsoft Graph beta endpoint — verify naming on current Learn)
Connect-MgGraph -Scopes 'SecurityEvents.Read.All' -NoWelcome
Invoke-MgGraphRequest -Method GET `
  -Uri 'https://graph.microsoft.com/beta/security/copilot/capacities'

# Confirm PAYG subscription health
Connect-AzAccount -Tenant $env:TENANT_ID
Get-AzSubscription -SubscriptionName 'security-copilot-payg' |
  Select-Object Name, State, TenantId
```

*KQL.*

```kusto
// Triage Agent run cadence
OfficeActivity
| where TimeGenerated > ago(120d)
| where Operation has "TriageAgent"
| summarize Runs = count(), LastRun = max(TimeGenerated) by bin(TimeGenerated, 1d)
| order by TimeGenerated desc
```

**Resolution.**

1. Re-enroll the Triage Agent — refresh saved authentication as **Insider Risk Management Admin**.
2. Increase Security Copilot SCU capacity if exhausted; coordinate with the Security Copilot Owner.
3. Resolve any PAYG billing failure with the Azure Subscription Owner.
4. Reassign role / plug-in if a Security Copilot upgrade dropped the assignment.
5. During the Triage Agent outage, increase manual triage cadence; document the compensating posture.

**Prevention.**

- **75-day refresh calendar.** Schedule saved-auth refresh at day 75 of the documented expiry; do not rely on day-91 reactive refresh.
- **SCU capacity headroom.** Maintain documented headroom (e.g., 30% above peak) so transient spikes do not exhaust capacity.
- **PAYG payment-method monitoring** — alert SEV-3 on payment-method nearing expiry.
- **Lifecycle subscription** — AI Governance Lead subscribes to Security Copilot release notes.

**Regulatory-evidence implications.**

| Authority | Exposure |
|---|---|
| **OCC Bulletin 2026-13 (formerly OCC 2011-12) / Fed SR 26-2 (formerly SR 11-7)** | The Triage Agent is a model; its availability is part of the model's operational risk; document outages in the model inventory (Control 2.6) |
| **FINRA Rule 3110(b)** | Manual triage is an acceptable compensating mechanism if documented; silent degradation without compensation is the gap |

---


### Scenario 15 — Pseudonymization broken (anonymization toggled off)

**Symptom.** Privacy Officer notices that the IRM alerts queue suddenly displays raw user UPNs in place of pseudonyms (`user-9c3f-44a7@…` previously; now `jane.doe@contoso.com`). UAL search confirms the Pseudonymization tenant-wide setting was **toggled off** by an IRM Admin two days ago. The privacy-by-design baseline is broken; investigators have been viewing raw identities for two days without going through the per-investigation unmask flow.

**Likely Cause.**

1. **Inadvertent toggle-off** — admin clicked the wrong setting; assumed "Show usernames" was per-session; in fact it was tenant-wide.
2. **Misunderstanding the feature** — admin assumed pseudonymization defeats investigation; the supported pattern is per-investigation unmask, not tenant-wide off.
3. **Deliberate toggle-off without sign-off** — operator change without Privacy + Compliance + Legal sign-off.

**Diagnostic Steps.**

*Portal.* Microsoft Purview → **Insider Risk Management** → **Settings** → **Privacy** → confirm pseudonymization toggle state and last-modified-by/UTC.

*PowerShell.*

```powershell
Connect-IPPSSession -ShowBanner:$false
Get-IRMConfiguration | Format-List PseudonymizationEnabled, LastConfigChangeUtc, LastConfigChangedBy
```

*KQL.*

```kusto
OfficeActivity
| where TimeGenerated > ago(30d)
| where RecordType == "ComplianceCenter"
| where Operation in ("PolicyChanged","TenantSettingChanged") and AdditionalInfo has "Pseudonymization"
| project TimeGenerated, UserId, Operation, AdditionalInfo
```

**Resolution — Emergency Re-anonymization.**

1. **Capture the failing-state evidence** per §1 (E-07 in particular) **before** toggling pseudonymization back on.
2. **Re-enable pseudonymization** as **Insider Risk Management Admin**.
3. **Convene Privacy + Compliance + Legal within 4 h.** Document:
   - Which users had alerts viewed during the dead window
   - Which Investigators viewed which alerts
   - Whether any unmask actions during the window had documented investigation reasons (likely not, since the tenant was de-pseudonymized)
   - Whether the Privacy Officer must notify affected employees
4. **IRM Auditor review.** The IRM Auditor reviews all admin actions during the dead window via UAL; produces a signed audit memo for Compliance.
5. **Post-incident review** with documented control changes — typically: tighten Conditional Access on the IRM Admin role; require dual-control on pseudonymization toggle (e.g., second-Admin approval); add a daily Sentinel canary that asserts pseudonymization is on.
6. **Privacy register entry.**

**Prevention.**

- **Daily SRE check.** Sentinel KQL that asserts `PseudonymizationEnabled : True`; alert SEV-1 on toggle-off.
- **Conditional Access lock-down** on IRM Admin role for pseudonymization toggle (Control 1.11); require step-up MFA + business-justification.
- **Dual-control** on pseudonymization toggle — no single admin can toggle without a second Approver.
- **Privacy training** for all IRM Admins quarterly.

**Regulatory-evidence implications.**

| Authority | Exposure |
|---|---|
| **GLBA §501(b)** | Privacy program obligation; tenant-wide de-pseudonymization is a programmatic defeat of the privacy-by-design model |
| **State employee-monitoring law (CT, DE, NY)** | The reasonable-expectation-of-privacy framework may be undermined |
| **NYDFS 23 NYCRR 500 §500.16** | Incident-response plan covers privacy-program incidents |
| **Internal privacy policy** | The firm's own privacy policy may set a higher bar than statute |

---

### Scenario 16 — Pseudonymization → non-pseudonymized escalation lacks HR + Legal sign-off

**Symptom.** Audit review finds that an Investigator unmasked 14 pseudonymized identities over the last 90 days **without** documented HR + Legal sign-off on each unmask. The unmasks were logged (the audit row exists with the investigator's name and timestamp) but the firm's documented procedure requires HR + Legal sign-off before unmask, which was not captured.

**Likely Cause.** Process gap — the firm's documented procedure required HR + Legal sign-off but the IRM Investigator workflow did not enforce a checkbox / attestation field.

**Diagnostic Steps.**

*Portal.* Microsoft Purview → **Insider Risk Management** → **Cases** → [case] → **Investigation notes** — confirm whether HR + Legal sign-off is documented.

*PowerShell.*

```powershell
# Inventory unmask events from UAL
Connect-ExchangeOnline -ShowBanner:$false
$start = (Get-Date).ToUniversalTime().AddDays(-90)
$end   = (Get-Date).ToUniversalTime()
$sid   = [guid]::NewGuid().ToString()
$rows  = @()
do {
  $batch = Search-UnifiedAuditLog -StartDate $start -EndDate $end `
            -RecordType ComplianceCenter -Operations 'UserUnmasked' `
            -SessionId $sid -SessionCommand ReturnLargeSet -ResultSize 5000
  $rows += $batch
} while ($batch.Count -gt 0)
$rows | Select-Object CreationDate, UserIds, Operations, AuditData
```

**Resolution.**

1. **Convene Privacy + Compliance + Legal + HR within 1 business day** to remediate the process gap retroactively.
2. **Per-unmask remediation** — for each of the 14 unmasks, document retroactively (with sign-off where possible) the investigation reason, business need, and HR + Legal awareness. If a sign-off cannot be recreated, flag as a control deviation in the privacy register.
3. **Forward control change** — implement a workflow gate that requires HR + Legal attestation field before any new unmask. Where the IRM workflow does not natively enforce this, wrap the unmask in a Power Automate flow / ServiceNow ticket that captures the attestation.
4. **IRM Auditor produces a signed memo** documenting the remediation.

**Prevention.**

- **Workflow attestation field.** All unmask actions go through a documented workflow that captures HR + Legal sign-off; no exceptions.
- **Quarterly Auditor review.** IRM Auditor reviews all unmask events quarterly against the documented procedure; deviations are flagged.
- **Investigator training** quarterly; refresher on per-investigation unmask procedure.

**Regulatory-evidence implications.**

| Authority | Exposure |
|---|---|
| **GLBA §501(b)** | Privacy program adherence — process gap is a programmatic finding even if no specific employee is harmed |
| **State employee-monitoring law** | Documented sign-off is part of the reasonable-employer-monitoring posture |
| **FINRA Rule 3110(b)** | Process compliance with the firm's WSP |

---

### Scenario 17 — Communication Compliance correlation missing

**Symptom.** An IRM `Risky AI usage` alert fires on a user. Compliance attempts to cross-reference the user's recent Communication Compliance alerts to view the conduct content (the actual prompts the user sent to Copilot). **No CC alerts exist for the user**, even though the user has been in scope of CC. Compliance asks why behavioral risk is firing without conduct-content correlation; the AI Governance Lead realizes **Control 1.10 (Communication Compliance Monitoring) was never deployed**.

**Likely Cause.** Cross-control gap — Control 1.10 (CC) is a separate workload that was descoped from the initial IRM rollout. Without CC, the firm has the behavioral-risk score (IRM 1.12) but not the conduct-content review (CC 1.10). The two are complementary but not equivalent.

**Diagnostic Steps.**

*Portal.* Microsoft Purview → **Communication Compliance** → **Policies** — empty list confirms CC is not deployed. Microsoft Purview → **Roles & scopes** → **Communication Compliance Admins / Analysts / Investigators / Viewers** — confirm role groups; if empty, CC has never been initialized.

*PowerShell.*

```powershell
Connect-IPPSSession -ShowBanner:$false
Get-SupervisoryReviewPolicyV2 -ErrorAction SilentlyContinue
# Empty result confirms no CC policies exist
```

**Resolution.**

1. **Open a Control 1.10 deployment ticket** with the AI Governance Lead; CC is a Compliance-led control with regulatory framing under FINRA Rule 3110(b) supervisory review and NYDFS 500.06 audit-trail.
2. **Stand up at minimum:**
   - CC Admin / Analyst / Investigator / Viewer role groups (with SoD)
   - A Copilot-conduct-content review template (Microsoft-provided)
   - A regulated-keywords / MNPI / NPI policy
   - Sample-rate calibration; reviewer assignment
3. **Cross-reference IRM cases to CC alerts** — once CC is producing alerts, the IRM case template should include a "Cross-references to CC alerts" field.
4. **Document the cross-control coverage matrix** — IRM 1.12 + CC 1.10 + DSPM 1.6 + DLP 1.5 are the four-corner solution for AI surface monitoring.

**Prevention.**

- **Control coverage matrix** as a quarterly attestation — every dependent control's deployment status is documented.
- **Cross-control runbooks** — IRM runbook includes the "check CC for the user" step; if CC is not deployed, the runbook explicitly says "this control is not in scope of the firm's posture; document gap."

**Regulatory-evidence implications.**

| Authority | Exposure |
|---|---|
| **FINRA Rule 3110(b)** | Supervisory review of communications is a recognized 3110 component for FINRA-supervised firms; CC absence is a 3110 gap on conduct content |
| **FINRA RN 24-09 / Rule 3110** | Generative-AI supervision; the firm's posture should include conduct-content review of AI prompts/responses |
| **SEC Reg S-P** | Conduct-content review on AI surfaces touching NPI |

---

### Scenario 18 — Sentinel UEBA service-principal anomaly not joined with IRM alert

**Symptom.** Microsoft Sentinel UEBA fires an anomaly on a Copilot Studio agent's service-principal sign-in (impossible-travel pattern across two regions). The SOC analyst expects the IRM Risky Agents queue to show a corresponding alert for the agent. **No IRM alert exists.** The two signals do not join; the SOC analyst has to manually correlate.

**Likely Cause.**

1. **Control 3.9 Sentinel integration not configured to enrich IRM** — the join is one-directional (IRM → Sentinel) and not bidirectional.
2. **Service-principal IDs vs. user identities** — Sentinel UEBA scores both; IRM scores user behavior; the join requires explicit KQL.
3. **Missing watchlist** in Sentinel that maps agent service-principal IDs to IRM agent identities.
4. **Office 365 / Defender XDR connector not forwarding IRM alerts** to Sentinel.

**Diagnostic Steps.**

*Portal.* Microsoft Sentinel workspace → **Data connectors** → confirm `Office 365`, `Microsoft Defender XDR`, `Microsoft 365 Insider Risk Management` connectors are healthy with recent ingestion. **Watchlists** → confirm the agent-identity watchlist exists and is current.

*KQL.*

```kusto
// IRM alerts ingestion check
SecurityAlert
| where TimeGenerated > ago(7d)
| where ProductName has_any ("Microsoft 365 Insider Risk Management","Microsoft Purview")
| summarize Alerts = count() by bin(TimeGenerated, 1d)
```

```kusto
// Join: Sentinel UEBA anomaly on a service principal + IRM Risky Agents alert
let agents = _GetWatchlist('AgentIdentities');
BehaviorAnalytics
| where TimeGenerated > ago(7d)
| where ActivityType == "AnomalousSignIn"
| where UserPrincipalName in (agents | project ServicePrincipalUpn)
| join kind=leftouter (
    SecurityAlert
    | where ProductName has "Insider Risk Management"
    | extend AgentUpn = tostring(parse_json(ExtendedProperties).AgentServicePrincipalUpn)
  ) on $left.UserPrincipalName == $right.AgentUpn
| project TimeGenerated, UserPrincipalName, ActivityType, IrmAlertId = AlertName
```

**Resolution.**

1. **Configure / verify the Sentinel connector** for IRM alerts (Control 3.9).
2. **Publish the agent-identity watchlist** to Sentinel — list of agent service-principal UPNs / object IDs cross-referenced to agent display name and owner.
3. **Build the join KQL** as a Sentinel scheduled analytics rule; alert SOC + IRM jointly when the join fires.
4. **Document the bidirectional pattern** in the SOC runbook.

**Prevention.**

- **Watchlist freshness** — agent-identity watchlist refreshed daily from the agent registry (Control 1.2).
- **Connector health alerting** for the IRM → Sentinel ingestion path.
- **Joint runbook** — IRM Admin and SOC Analyst share a single runbook for agent-anomaly correlation.

**Regulatory-evidence implications.**

| Authority | Exposure |
|---|---|
| **FINRA RN 24-09 / Rule 3110** | Agent supervision requires correlation across signals |
| **OCC Bulletin 2013-29** | Third-party / vendor risk on agent-identity providers |
| **NYDFS §500.06 / §500.16** | Audit-trail completeness and incident-response readiness |

---

### Scenario 19 — Risky Agents alert volume from one Copilot Studio agent overwhelms queue

**Symptom.** A single Copilot Studio agent (e.g., a high-traffic customer-service agent) is generating 80%+ of the IRM **Risky Agents** alert volume. Analysts cannot triage real signal; queue SLA collapses.

**Likely Cause.**

1. **Agent design defect** — overly-broad knowledge grounding pulls from sources outside the intended scope; every interaction trips the risk indicator.
2. **Workload identity (Entra Agent ID) over-permissioned** — the agent's service principal has Graph permissions that exceed the agent's purpose, so legitimate use looks risky (Control 2.26).
3. **Indicator over-tuning** — Risky Agents indicator thresholds are too tight for the agent's expected baseline.
4. **Connector misconfiguration** — agent uses an HTTP connector to a non-approved endpoint (cross-ref Control 2.16 RAG).

**Diagnostic Steps.**

*Portal.* Microsoft Purview → **Insider Risk Management** → **Alerts** → filter by `Agent` field; identify the dominant agent. Power Platform Admin Center → **Environments** → [env] → **Agents** → [agent] → **Permissions** and **Knowledge sources**.

*KQL.*

```kusto
SecurityAlert
| where TimeGenerated > ago(7d)
| where ProductName has "Insider Risk Management"
| extend AgentName = tostring(parse_json(ExtendedProperties).AgentDisplayName)
| summarize Alerts = count() by AgentName
| order by Alerts desc
```

**Resolution.**

1. **Suspend the offending agent** via Power Platform Admin Center (or revoke its workload identity sign-ins via Entra) while remediation is in progress; coordinate with the agent owner.
2. **Root-cause via agent-design review** with the Copilot Studio Maker, Power Platform Admin, and AI Governance Lead — narrow knowledge sources, scope permissions, and re-validate against Control 2.16 RAG.
3. **Re-baseline the agent's Entra Agent ID permissions** to least privilege (Control 2.26); remove unused Graph scopes.
4. **Re-tune the Risky Agents indicator threshold** for the agent's expected baseline; do not blanket-suppress.
5. **Re-publish the agent** under Control 2.3 Change Management (CAB) with documented design changes.

**Prevention.**

- **Agent baseline review** at publish time per Control 2.25 (Agent 365 Inventory) and Control 2.16 (RAG).
- **Per-agent indicator tuning** in IRM as part of agent onboarding to production.
- **Workload-identity permissions review** quarterly (Control 2.26).
- **Top-N agent dashboard** in the IRM analyst view; investigate outliers before they overwhelm.

**Regulatory-evidence implications.**

| Authority | Exposure |
|---|---|
| **FINRA RN 24-09 / Rule 3110** | Generative-AI supervision; alert-fatigue from one agent compromises the queue |
| **OCC Bulletin 2026-13 (formerly OCC 2011-12) / Fed SR 26-2 (formerly SR 11-7)** | Agent is a model; over-tripping risk indicators is a model-performance issue |
| **NYDFS §500.16** | Incident-response readiness; queue collapse is an operational-risk event |

---

### Scenario 20 — IRM alert escalates to incident; legal hold + regulator clock

**Symptom.** A high-severity IRM alert (e.g., bulk MNPI exfiltration to personal storage) is confirmed by the IRM Investigator. The case is being escalated to an incident; CISO has been notified. Compliance and Legal need an immediate sequenced response covering: incident-reporting handoff (Control 3.4), legal hold (Control 1.19), and regulator-clock evaluation.

**Likely Cause.** Not a defect — this is the success path. The risk is **process-execution failure**: missing the regulator clock, losing evidence to auto-delete, or skipping legal hold.

**Diagnostic Steps.**

*Portal.* Microsoft Purview → **Insider Risk Management** → [case] — confirm Forensic Evidence captures, content snapshots, and User Activities export are complete. Microsoft Purview → **eDiscovery (Premium)** → **Cases** — confirm a case has been created and a hold is in place.

**Resolution — Sequenced response.**

1. **T+0 (determination):** IRM Investigator confirms; CISO is notified. Start the **NYDFS 500.17 72-hour clock** at determination (not first alert) for NYDFS-regulated entities.
2. **T+1h:** Open eDiscovery (Premium) case (Control 1.19); place all relevant custodian mailboxes, OneDrive, Teams, SharePoint, and Copilot interaction sources on hold. Hold persists across the 120-day Forensic Evidence boundary.
3. **T+2h:** Hand off to Control 3.4 Incident Reporting workflow; Compliance + Legal + Privacy convene.
4. **T+4h:** Forensic Evidence export to immutable storage (Control 1.7 audit); chain-of-custody record initiated.
5. **T+24h:** Promotion of relevant content to Records Retention (Control 1.9) where appropriate; SEC 17a-4(f) WORM target if a books-and-records nexus exists.
6. **T+72h:** NYDFS 500.17 notification to DFS Superintendent if conditions met.
7. **Within applicable windows:** Reg S-P Amendments 30-day notification evaluation; FINRA Rule 4530 reporting evaluation.

**Prevention.**

- **Pre-rehearsed runbook** with timeline above; tabletop exercise quarterly with CISO + Compliance + Legal + Privacy.
- **Auto-link IRM-to-eDiscovery** template — IRM Investigator can launch an eDiscovery (Premium) case from the IRM case with custodians pre-populated.
- **Regulator-clock checklist** at incident kickoff.

**Regulatory-evidence implications.**

| Authority | Exposure |
|---|---|
| **NYDFS 23 NYCRR 500.17(a)** | 72-hour notification to DFS Superintendent on cybersecurity-event determination |
| **SEC Reg S-P Amendments** | 30-day notification on incidents involving sensitive customer information |
| **FINRA Rule 4530** | Reporting of certain events |
| **SEC 17a-4(f)** | Books-and-records preservation in WORM |

---

### Scenario 21 — SoD violation found in IRM role groups

**Symptom.** Quarterly access review finds that user `alice@contoso.com` is a member of **both** the `Insider Risk Management Investigators` and `Insider Risk Management Approvers` role groups, defeating segregation of duties. Audit trail confirms the dual assignment has existed for 47 days.

**Likely Cause.** Manual role assignment without SoD validation. PIM eligibility for both roles assigned by the same Entra Global Admin without exclusion enforcement.

**Diagnostic Steps.**

*PowerShell.*

```powershell
Connect-IPPSSession -ShowBanner:$false
$inv = Get-RoleGroupMember 'InsiderRiskManagementInvestigators' | Select -Expand Name
$apr = Get-RoleGroupMember 'InsiderRiskManagementApprovers'    | Select -Expand Name
Compare-Object $inv $apr -IncludeEqual -ExcludeDifferent | Select InputObject
```

```kusto
OfficeActivity
| where TimeGenerated > ago(180d)
| where Operation in ("Add member to role.","Remove member from role.")
| where Parameters has_any ("InsiderRiskManagementInvestigators","InsiderRiskManagementApprovers")
| project TimeGenerated, UserId, Operation, Parameters
```

**Resolution.**

1. **Emergency removal.** As **Entra Global Admin**, remove the user from one of the two groups (typically remove the Approver assignment so Investigation continues uninterrupted; document the rationale with Compliance).
2. **IRM Auditor review** of all actions taken by the user during the 47-day dual-membership period; produce a signed memo.
3. **Compensating control review** — were any approvals during the period authored by the same user who investigated? Flag any such overlap for Compliance escalation.
4. **Retroactive sign-off** by an independent Approver for any approvals authored during the period.
5. **Forward control change** — implement Entra access-package SoD policy so the two roles are mutually exclusive (Control 1.11).

**Prevention.**

- **Mutually-exclusive Entra access packages** for IRM roles; assignment to one auto-removes eligibility for the other.
- **Quarterly access review** by the IRM Auditor (already required by Control 1.7).
- **PIM activation justification** required for IRM roles; Approver activations are reviewed.

**Regulatory-evidence implications.**

| Authority | Exposure |
|---|---|
| **SOX §404** | SoD is a recognized Internal Controls Over Financial Reporting principle |
| **FINRA Rule 3110(b)** | Supervisory system requires SoD between supervisor and supervised |
| **NYDFS §500.07** | Access-privilege management |
| **GLBA §501(b)** | Privacy-by-design SoD between Investigator and Approver of unmask actions |

---

### Scenario 22 — Forensic Evidence exposed PII to non-cleared reviewer

!!! danger "PII / NPI handling"
    This scenario involves confirmed exposure of personally identifiable information (PII) and possibly nonpublic personal information (NPI) to a non-cleared reviewer. **Stop normal triage; convene Privacy + Compliance + Legal + CISO immediately.** Capture all evidence per §1 before any remediation. Decisions about disclosure to affected individuals and regulators must be made by Legal — do not act unilaterally.

**Symptom.** A Forensic Evidence video clip showing a user's screen during a flagged event was reviewed by an Investigator who did **not** have the documented Privacy + Legal clearance for that data class. The clip contained customer NPI (a brokerage account view) visible on the user's screen. The Investigator viewed the clip before the case template's data-class field was set.

**Likely Cause.**

1. **Forensic Evidence policy scoped too broadly** — the policy captured the user's full screen rather than only the application of interest.
2. **Investigator role assigned without data-class clearance gating** — IRM does not natively gate Forensic Evidence by data class; the firm must layer access-package gating.
3. **Case-template data-class field not enforced** as a pre-view gate.
4. **Pseudonymization on user identity but not on screen-content PII** — pseudonymization is identity-only.

**Diagnostic Steps.**

*Portal.* Microsoft Purview → **Insider Risk Management** → **Forensic Evidence** → [policy] — review capture scope. **Cases** → [case] — confirm who viewed the clip and when (audit trail). UAL search for `ForensicEvidenceClipViewed` on the case.

```kusto
OfficeActivity
| where TimeGenerated > ago(30d)
| where Operation has "ForensicEvidence"
| project TimeGenerated, UserId, Operation, AdditionalInfo
```

**Resolution — Emergency containment.**

1. **Quarantine the clip** — restrict access in IRM to the Privacy Officer + IRM Auditor only; do **not** delete (preserves evidence and chain of custody).
2. **Convene Privacy + Compliance + Legal + CISO within 1 hour.**
3. **Document the exposure scope** — exactly which records the Investigator could see; was data exfiltrated from the IRM portal (e.g., screenshot of the clip)? UAL helps confirm.
4. **Forensic Evidence key-rotation evaluation** — whether to rotate the customer-managed key (CMK) under which Forensic Evidence is encrypted; this is typically a formal Legal-led decision.
5. **Disclosure decision (Legal-led)** — evaluate against:
   - SEC Reg S-P Amendments — sensitive customer information; 30-day clock evaluation
   - State data-breach notification statutes (50-state matrix)
   - NYDFS 500.17 — cybersecurity-event determination
6. **Investigator removed from Forensic Evidence access** pending re-clearance; access reinstated only after documented data-class clearance.
7. **Forward control change** — narrow Forensic Evidence capture scope; layer Entra access-package gating by data class; enforce pre-view data-class checkbox in case template.

**Prevention.**

- **Narrow Forensic Evidence scope** — capture only the specific application or window; do not capture full screen for general indicators.
- **Data-class access packages** — Investigator role split by data class (NPI / MNPI / PII / general); access requires documented clearance.
- **Pre-view gate** on Forensic Evidence clips — Investigator must attest data-class clearance before clip plays.
- **Quarterly data-class clearance review** by Privacy Officer.

**Regulatory-evidence implications.**

| Authority | Exposure |
|---|---|
| **SEC Reg S-P Amendments** | Sensitive customer information exposure; 30-day notification clock evaluation |
| **GLBA §501(b)** | NPI safeguards rule; programmatic finding |
| **State data-breach laws** | 50-state notification matrix; Legal-led evaluation |
| **NYDFS 23 NYCRR 500.17** | Cybersecurity-event determination; 72-hour clock evaluation |
| **Internal privacy policy** | The firm's own policy may require employee-affected notifications |

---

### Scenario 23 — AI-driven risk score (Triage Agent / ML scoring) drifts

**Symptom.** Over a quarter, the Triage Agent's risk-score distribution shifts: the median priority score climbs 18 points; the alert volume in the "high" tier doubles without a corresponding change in workforce composition or business activity. Compliance asks whether the model is drifting.

**Likely Cause.**

1. **Concept drift** — workforce behavior has changed (return-to-office, new SaaS adoption, new agent rollout) and the model has not been retrained against the new baseline.
2. **Indicator-tuning change upstream** — IRM Admin tightened indicators; the Triage Agent re-prioritized accordingly.
3. **Microsoft model-version change** — Triage Agent model upgraded silently; new version has different calibration.
4. **Population-shift** — the priority-user-group composition changed (Control 1.13 SITs).

**Diagnostic Steps.**

*Portal.* Microsoft Purview → **Insider Risk Management** → **Triage Agent** → **Score distribution** — compare current quarter to prior baseline.

```kusto
SecurityAlert
| where TimeGenerated > ago(180d)
| where ProductName has "Insider Risk Management"
| extend Score = toint(tostring(parse_json(ExtendedProperties).TriagePriorityScore))
| summarize MedianScore = percentile(Score, 50), HighTier = countif(Score >= 80) by bin(TimeGenerated, 7d)
| order by TimeGenerated asc
```

**Resolution.**

1. **Open a Control 2.6 (Model Risk Management) feedback ticket** — Triage Agent is in the firm's model inventory under OCC Bulletin 2026-13 (formerly OCC 2011-12) / Fed SR 26-2 (formerly SR 11-7); drift is a documented model-risk event.
2. **Independent model validation** — Compliance / Model Risk Management team re-validates Triage Agent priority-score distribution against a holdout sample of human-triaged alerts.
3. **Recalibration evaluation** — if Microsoft published a model-version change, document the version and the firm's revalidation outcome; if drift is concept drift, recalibrate indicator thresholds upstream.
4. **Documented validation cycle** — quarterly model validation per OCC Bulletin 2026-13 (formerly OCC 2011-12) / Fed SR 26-2 (formerly SR 11-7) ongoing-monitoring expectation.
5. **Bias check** — cross-reference Control 2.11 (Bias Monitoring) — does the drift manifest unevenly across protected classes?

**Prevention.**

- **Quarterly model-validation cycle** with documented sample sizes, holdout methodology, and acceptance criteria.
- **Subscribe to Microsoft model-version change announcements** for the Triage Agent.
- **Population-shift monitoring** — alert when priority-user-group composition shifts >10% quarter-over-quarter.

**Regulatory-evidence implications.**

| Authority | Exposure |
|---|---|
| **OCC Bulletin 2026-13 (formerly OCC 2011-12) / Federal Reserve SR 26-2 (formerly SR 11-7)** | Model risk management; ongoing monitoring expectation |
| **FINRA RN 24-09 / Rule 3110** | Generative-AI supervision; model-performance evidence |
| **NYDFS §500.16** | Incident-response readiness if drift is severe enough to be operational risk |

---


### Scenario 25 — Examiner request for IRM evidence cannot be produced

!!! danger "PII / NPI handling"
    Examiner-evidence requests touch employee-monitoring records, PII, and potentially NPI / MNPI from IRM cases. **All evidence production must be Legal-reviewed before transmission.** Privilege and confidentiality designations are required. Pseudonymization decisions on examiner-bound evidence (whether to pseudonymize, fully unmask, or partially redact) are Legal-led, not Compliance-led.

**Symptom.** A regulator (FINRA, SEC, NYDFS, or OCC) examiner requests IRM-case evidence for a 14-month-old investigation. The IRM portal shows the case as **archived**; Forensic Evidence captures expired at 120 days; case content is not in the IRM live store. Compliance must produce evidence within the examiner deadline (typically 10–30 calendar days depending on authority and request type).

**Likely Cause.**

1. **Forensic Evidence auto-deleted at 120 days** (the central retention boundary; see §0/§1).
2. **Case promotion to Records Retention (Control 1.9) was not performed** at investigation closure.
3. **eDiscovery hold (Control 1.19) was not placed** on case-relevant custodians at investigation start.
4. **Audit log retention boundary** — UAL retention depends on license; confirm Audit (Premium) for 1-year+ retention (Control 1.7).

**Diagnostic Steps.**

*Portal.* Microsoft Purview → **Insider Risk Management** → **Cases** → search for the case ID; confirm archived state and last-action UTC. Microsoft Purview → **Records Management** → **Disposition** — search for retention-promoted artifacts referencing the case ID. Microsoft Purview → **eDiscovery (Premium)** → search for any hold tagged to the custodians at the case time.

*PowerShell.*

```powershell
Connect-IPPSSession -ShowBanner:$false
# UAL search at the case-time window for IRM activities
$start = (Get-Date).AddMonths(-15).ToUniversalTime()
$end   = (Get-Date).AddMonths(-13).ToUniversalTime()
Search-UnifiedAuditLog -StartDate $start -EndDate $end -RecordType ComplianceCenter `
  -Operations 'AlertTriggered','CaseCreated','CaseStatusChanged','UserUnmasked' `
  -ResultSize 5000
```

**Resolution.**

1. **Convene Compliance + Legal + IRM Auditor + Records Management within 1 business day** of examiner request receipt.
2. **Produce what exists, document what does not** — examiners expect honesty about the firm's retention posture; do not fabricate or extrapolate.
3. **Recovery sources, in order of preference:**
   - Records Retention promoted artifacts (Control 1.9) — case summaries, investigation memos, decision records
   - eDiscovery (Premium) holds (Control 1.19) — custodian content if a hold was in place at the time
   - Audit log (Control 1.7) — service-side evidence trail of what was investigated, when, and by whom
   - SEC 17a-4(f) WORM vendor archive — if the firm uses a 17a-4(f) compliant immutable archive for regulated content
   - Sentinel long-term retention (Control 3.9) — if IRM alerts were ingested and the workspace retention covers the period
4. **Evidence package** assembled by IRM Auditor; reviewed by Legal for privilege and confidentiality; signed Compliance attestation cover memo.
5. **Gap memo (Legal-reviewed)** documenting what was not retained and the firm's rationale at the time (typically: investigation closed without escalation; no Records Retention trigger met).
6. **Forward control change** — for all future cases above a documented severity threshold, mandatory promotion to Records Retention at closure regardless of escalation outcome.

**Prevention.**

- **Mandatory Records Retention promotion** at IRM case closure for cases above a documented severity threshold.
- **Mandatory eDiscovery hold** at investigation kickoff for cases above a documented severity threshold; hold persists per Legal direction.
- **Audit (Premium) license** for extended UAL retention (Control 1.7).
- **Annual examiner-readiness tabletop** — exercise the recovery sequence end-to-end with a synthetic 14-month-old case.

**Regulatory-evidence implications.**

| Authority | Exposure |
|---|---|
| **SEC 17a-4(f)** | Books-and-records preservation; failure to produce is a 17a-4 finding |
| **FINRA Rules 4511 / 3110** | Books-and-records and supervisory evidence |
| **NYDFS §500.06** | Audit-trail retention obligations |
| **SEC Rule 204-2 (Advisers Act)** | Adviser books-and-records |
| **Examiner-specific deadlines** | Failure-to-produce is itself a finding distinct from the underlying matter |

---

## §6 Escalation Matrix

### Tiered escalation

| Tier | Owner | Trigger | Time-to-engage |
|---|---|---|---|
| **L1** | Insider Risk Management Admin | Operational alert / configuration drift; non-PII; non-incident | Same business day |
| **L2** | AI Governance Lead + Privacy Officer | Cross-control gap; pseudonymization issue; model drift | 1 business day |
| **L3** | CISO + Compliance + Legal + HR | Confirmed PII/NPI exposure; case escalating to incident; SoD violation; examiner request | 1 hour (PII/NPI) — 1 business day (other) |
| **L4** | Microsoft support (Premier / Unified) | Product defect; service-side failure not attributable to configuration | After L1/L2 root-cause confirms product responsibility |
| **L5** | Internal Compliance + Legal + HR communication | Disclosure decision; regulator-clock evaluation; employee-affected notification | Per regulator / statute clocks |

### L4 — Microsoft support ticket payload template

Use this payload when opening a Microsoft support case for an IRM product issue (after L1/L2 root-cause confirms the issue is product-side, not configuration).

```text
Title: [IRM] <Concise symptom> — <Cloud> — Tenant <TenantId>

Tenant: <TenantId>
Cloud: Commercial
Affected workload: Insider Risk Management
Affected feature: <Triage Agent | Adaptive Protection | Forensic Evidence | Risky Agents | Risky AI usage | Browser extension | HR connector | Other>
Date/time of first observation (UTC): <yyyy-mm-ddThh:mm:ssZ>
Date/time of most recent observation (UTC): <yyyy-mm-ddThh:mm:ssZ>
Severity (firm-internal): SEV-1 | SEV-2 | SEV-3 | SEV-4
Regulator clock active: Y/N — if Y, name the clock and deadline

Symptom (1–3 sentences, factual, no speculation):
<...>

Reproduction steps:
1. <...>
2. <...>
3. <...>

Expected behavior (per Microsoft Learn URL):
<URL + paragraph cited>

Observed behavior:
<...>

Diagnostic evidence already captured (per §1):
- E-01 IRM configuration export — attached
- E-04 alert payload — attached
- E-05 case audit timeline — attached
- E-08 UAL slice — attached
- Other: <...>

Configuration confirmed correct:
- Indicator config: <...>
- Policy scope (AU): <...>
- Connector health: <...>
- License SKU: <...>

Workaround in place: Y/N
If Y, describe: <...>

Privacy / data-handling notes:
This case may contain pseudonymized employee identifiers. Do NOT request raw
PII / NPI / MNPI in unencrypted form. All evidence transfer must be via the
secure Microsoft support portal.

Requested response SLA: <per support contract>
```

### L5 — Internal Compliance + Legal + HR communication template

Use this template when communicating internally to Compliance + Legal + HR + (where indicated) the Privacy Officer + the CISO. **Do not** transmit outside the firm without Legal review.

```text
Subject: [IRM-CONFIDENTIAL] <Case ID> — <One-line summary> — <Severity>

Classification: Confidential — Privileged Attorney-Client Communication
                (where Legal directs the privilege designation)
Distribution: <Named individuals only — do not forward>

1. Summary
   <2–4 sentences: what was detected, what action was taken, current status>

2. Timeline (UTC)
   T+0  <Detection / determination event>
   T+1h <Action>
   T+4h <Action>
   T+24h <Action>
   <... continue per actual timeline>

3. Evidence preserved (per §1)
   - E-01 IRM configuration: <location>
   - E-04 alert payload: <location>
   - E-05 case audit timeline: <location>
   - E-07 Forensic Evidence captures: <location, retention boundary>
   - E-08 UAL: <location, query>
   - eDiscovery (Premium) hold: <case ID, custodians, hold UTC>
   - Records Retention promotion: <label, applied UTC>

4. Regulatory-clock evaluation (Legal-led)
   - NYDFS 23 NYCRR 500.17: <evaluation>
   - SEC Reg S-P Amendments 30-day clock: <evaluation>
   - FINRA Rule 4530: <evaluation>
   - State data-breach statutes: <evaluation>
   - SEC 17a-4(f): <evaluation>

5. Pseudonymization status
   - Tenant pseudonymization: On / Off
   - Per-investigation unmask events for this case: <count, with HR + Legal sign-off Y/N>

6. SoD attestation
   - Investigator: <name>  Approver: <different name>  Auditor: <different name>

7. Compensating controls invoked (where applicable)
   <Per §3>

8. Open decisions (Legal-led)
   - <Decision item, owner, deadline>

9. Next checkpoint
   <Date/time, attendees, agenda>

Authored by: <IRM Auditor or Investigator>
Reviewed by:  <Compliance Officer>
Privileged-communication review: <Legal Counsel>
```

---

## §7 Cross-References

### Cross-control links

- [Control 1.5 — DLP for Microsoft 365 Copilot](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) — content-side prevention complementary to behavioral risk
- [Control 1.6 — DSPM for AI](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md) — sensitive-data discovery on AI surfaces
- [Control 1.7 — Audit and Activity Logging](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) — UAL retention; Audit (Premium)
- [Control 1.9 — Records Retention](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md) — promotion of IRM evidence past the 120-day Forensic Evidence boundary
- [Control 1.10 — Communication Compliance Monitoring](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md) — conduct-content review complement to behavioral risk
- [Control 1.11 — Conditional Access and MFA for Agents](../../../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md) — IRM-role lockdown; Adaptive Protection signal consumption
- [Control 1.13 — Sensitive Information Types](../../../controls/pillar-1-security/1.13-sensitive-information-types-sits-and-pattern-recognition.md) — priority-user-group population; data-class taxonomy
- [Control 1.17 — Endpoint DLP](../../../controls/pillar-1-security/1.17-endpoint-data-loss-prevention-endpoint-dlp.md) — non-Windows browser-extension compensating posture
- [Control 1.19 — eDiscovery for Agent Interactions](../../../controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md) — legal hold; examiner production
- [Control 2.1 — Managed Environments](../../../controls/pillar-2-management/2.1-managed-environments.md) — Power Platform managed-environment baseline
- [Control 2.3 — Change Management / CAB](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md) — agent re-publish under change control
- [Control 2.6 — Model Risk Management](../../../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md) — OCC Bulletin 2026-13 (formerly OCC 2011-12) / Federal Reserve SR 26-2 (formerly SR 11-7) model inventory; Triage Agent drift
- [Control 2.11 — Bias Monitoring](../../../controls/pillar-2-management/2.11-bias-testing-and-fairness-assessment.md) — protected-class fairness review of risk scoring
- [Control 2.16 — RAG / Knowledge Source Controls](../../../controls/pillar-2-management/2.16-rag-source-integrity-validation.md) — agent knowledge-source narrowing
- [Control 2.25 — Agent 365 Inventory](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md) — agent registry; per-agent baseline review
- [Control 2.26 — Entra Agent ID](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md) — workload-identity least privilege
- [Control 3.4 — Incident Reporting](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) — incident handoff; regulator-clock evaluation
- [Control 3.6 — Orphaned Agent Detection](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) — orphan-agent IRM signal correlation
- [Control 3.9 — Microsoft Sentinel Integration](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md) — IRM ingestion; UEBA join

### Sibling 1.12 playbooks

- [1.12 Portal walkthrough](portal-walkthrough.md)
- [1.12 Verification testing](verification-testing.md)

### Reference

- [Role catalog](../../../reference/role-catalog.md) — canonical short names for all Insider Risk Management, Purview, Exchange Online, Entra, Power Platform, and Defender roles cited in this playbook
- [Regulatory mappings](../../../reference/regulatory-mappings.md) — authority-to-control matrix
- [Solutions index](../../../reference/solutions-index.md) — companion deployable artifacts

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
