# Control 1.12 — Troubleshooting: Insider Risk Detection and Response

> **Scope.** This playbook is the symptom-first diagnostic companion to [Control 1.12 — Insider Risk Detection and Response](../../../controls/pillar-1-security/1.12-insider-risk-detection-and-response.md). It covers Microsoft Purview Insider Risk Management (IRM) detection failures across the FSI-relevant surface — Risky Agents, Risky AI usage, Data leaks (priority users), Security policy violations, Adaptive Protection, Forensic Evidence (dual-auth, 120-day clip retention), Triage Agent, HR connector, browser-extension Windows-only constraint, pseudonymization, and the cross-control handoffs to Communication Compliance (1.10), eDiscovery (1.19), Sentinel UEBA (3.9), Incident Reporting (3.4), and Model Risk (2.6).
>
> **Audience.** Insider Risk Management Admin, Insider Risk Management Analyst, Insider Risk Management Investigator, Insider Risk Management Auditor, Insider Risk Management Approver, Purview Compliance Admin, Privacy Officer, General Counsel, HR Privileged, SOC Analyst, AI Governance Lead. Roles named per [`docs/reference/role-catalog.md`](../../../reference/role-catalog.md).
>
> **Sibling playbooks.** [portal-walkthrough.md](portal-walkthrough.md) · [verification-testing.md](verification-testing.md)
>
> **Last UI Verified:** April 2026
>
> **Last Verified:** 2026-10-18 (Microsoft Learn technical-documentation review; no live portal, tenant, or screenshot verification).

!!! important "Separate detection, alert export, and administrator audit evidence"
    Microsoft 365 auditing is a prerequisite for IRM detection, but the **Insider risk audit log** is an independent, always-enabled log with **180-day** retention. Export administrator actions from that log; do not infer their absence from a Unified Audit Log (UAL) or `OfficeActivity` query. For SIEM alert delivery, enable **Export alerts**, then use the documented `SecurityComplianceAlerts` records filtered to `InsiderRiskManagement`, or the dedicated Sentinel IRM connector. Neither path proves forensic capture approval or clip availability. See [IRM audit log](https://learn.microsoft.com/en-us/purview/insider-risk-management-audit-log) and [data sharing](https://learn.microsoft.com/en-us/purview/insider-risk-management-settings-share-data).

> **Technical correction (2026-10-18):** use [the current-source PowerShell evidence boundaries](powershell-setup.md). IRM administrative audit activity is captured by its independent, always-on **180-day** solution log, not by invented UAL operations or a generic `OfficeActivity` feed. HR connector health comes from upload logs, and forensic requests are submitted by **Admins**, approved by **Approvers**, and viewed by **Investigators**. This targeted propagation does not re-certify the other scenario lifecycles or historical tenant UI.

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
2. [ ] **IRM SKU verified** for monitored users; indicator/Triage Agent PAYG enabled where required; forensic evidence capacity add-on verified separately
3. [ ] **Unified Audit Log on** — `Get-AdminAuditLogConfig` from a `Connect-ExchangeOnline` session shows `UnifiedAuditLogIngestionEnabled : True` (UAL off is the **most common silent-failure mode** in IRM); an IPPS result is not valid audit-status evidence
4. [ ] **HR connector last-success ≤ 24 h** (firm threshold); resignation mapping covers UPN, `ResignationDate`, and `LastWorkingDate` with ISO 8601 date/time values
5. [ ] **Administrator evidence exported** from the independent **Insider risk audit log**; alert-export ingestion checked separately
6. [ ] **Analytics state recorded**; initial scans may take **up to 48 h**. A seven-day observation sample, if used by the firm, is not a Microsoft Risky Agents prerequisite
7. [ ] **Pseudonymization state captured before any re-identification**
8. [ ] **Forensic Evidence dual-auth approver list** non-empty and **distinct from Investigators**; state-law notice posture (CT / DE / NY) confirmed with Privacy + Legal before any new capture
9. [ ] **Browser extension / Edge config policy state** — Microsoft Compliance Extension (Edge and Chrome) deployed via Intune to the in-scope **Windows** population; non-Windows excluded explicitly with documented gap
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
| **E-04** | Forensic Evidence clip inventory (actual capture time, trigger, requesting Admin, independent Approver, export deadline) | Purview — Forensic Evidence | 7 y (clip itself: export before capture-based 120-day deletion or earlier applicable preview end) |
| **E-05** | Role-group snapshot for `Insider Risk Management`, `Insider Risk Management Admins`, `Insider Risk Management Analysts`, `Insider Risk Management Investigators`, `Insider Risk Management Auditors`, `Insider Risk Management Approvers` (membership, AU restriction, effective permissions) | Purview > Settings > Roles and groups > Role groups; these are Purview role groups, not Graph `directoryRoles` | 7 y |
| **E-06** | Priority user group snapshot + priority content list snapshot | Purview — Insider Risk Management > Settings | 7 y |
| **E-07** | Pseudonymization state (toggle state, last-toggled-by identity, active "show usernames" sessions) — **captured before any re-identification action** | Purview — Insider Risk Management > Settings > Privacy | 7 y |
| **E-08** | HR connector upload status, row count, source schema, mapping to UPN / `ResignationDate` / `LastWorkingDate`; preserve original timestamps and timezone | Purview — Settings > Data connectors > My connectors | 7 y |
| **E-09** | Browser extension / Edge config policy state (Intune coverage report; per-OS coverage; non-Windows gap documented) | Intune (or equivalent MDM); Edge / Chrome management | 7 y |
| **E-10** | Device onboarding state — devices onboarded to Microsoft Purview, cross-referenced against policy user scope | Purview — Settings > Device onboarding | 7 y |
| **E-11** | Independent Insider risk audit log CSV export for administrator actions; separate UAL export for relevant workload activity — record filters, timezone, and any result limits | Purview > Insider risk audit log; Exchange Online PowerShell for UAL only | 7 y |
| **E-12** | Defender for Cloud Apps connector health for any SaaS source feeding IRM (Box, Dropbox, Google Drive, Amazon S3, Azure) | Defender for Cloud Apps — Connectors | 7 y |
| **E-13** | Defender for Endpoint integration state (required for Security policy violations templates) | Defender XDR — Settings > Integrations | 7 y |
| **E-15** | Forensic evidence capacity add-on and monthly usage; separate PAYG state for indicators / Triage Agent | Forensic evidence > Settings > Forensic evidence capacity; relevant billing surfaces for PAYG | 7 y |
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
  [string[]] $UserIds,
  [string[]] $RecordTypes,
  [string[]] $Operations,
  [string]   $FreeText,
  [datetime] $WindowStartUtc = (Get-Date).ToUniversalTime().AddDays(-7),
  [datetime] $WindowEndUtc   = (Get-Date).ToUniversalTime()
)

if (-not ($UserIds -or $RecordTypes -or $Operations -or $FreeText)) {
  throw 'Specify at least one UAL scope filter (-UserIds, -RecordTypes, -Operations, or -FreeText) before running Search-UnifiedAuditLog so unrelated tenant workload activity does not trip the 50,000-row ceiling.'
}

$root = Join-Path -Path $env:FSI_EVIDENCE_BUCKET -ChildPath ("1.12-{0}-{1:yyyyMMddHHmmss}" -f $IncidentId, $WindowEndUtc)
New-Item -ItemType Directory -Path $root -Force | Out-Null

# E-11 supplemental workload evidence; export the independent IRM audit log separately
Connect-ExchangeOnline -ShowBanner:$false
$sessionId = [guid]::NewGuid().ToString()
$page      = 0
$results   = @()
$ualParams = @{
  StartDate      = $WindowStartUtc
  EndDate        = $WindowEndUtc
  SessionId      = $sessionId
  SessionCommand = 'ReturnLargeSet'
  ResultSize     = 5000
}
if ($UserIds)     { $ualParams['UserIds']    = $UserIds }
if ($RecordTypes) { $ualParams['RecordType'] = $RecordTypes }
if ($Operations)  { $ualParams['Operations'] = $Operations }
if ($FreeText)    { $ualParams['FreeText']   = $FreeText }

do {
  $page++
  $batch = Search-UnifiedAuditLog @ualParams
  $results += $batch
} while ($batch.Count -gt 0 -and $results.Count -lt 50000)
if ($results.Count -ge 50000) {
  throw 'UAL result ceiling reached. Narrow the scope filters or split the UTC window and rerun; do not attest completeness.'
}

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

> **Collection boundary.** This helper collects supplemental UAL workload records, not the independent IRM administrator audit log. Export that log as CSV using an Insider Risk Management Auditor, preserve its original local-time values and timezone, and record normalized UTC separately. The UAL helper fails at the 50,000-result ceiling rather than presenting a truncated export as complete. See [Search-UnifiedAuditLog](https://learn.microsoft.com/en-us/powershell/module/exchangepowershell/search-unifiedauditlog).

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

**Symptom.** A known test activity produces no expected IRM alert, and Microsoft 365 Audit has no expected source-activity records. Check the audit prerequisite separately from the IRM solution audit log and from SIEM alert forwarding; no `ComplianceCenter` record is required to prove an IRM administrative action occurred.

**Likely Cause.** Microsoft 365 auditing may be disabled. IRM policies and analytics scans use this log to detect activity. Zero alerts alone do not establish this cause: check policy scope, triggering events, indicators, thresholds, and processing status as well. The independent Insider risk audit log continues recording administrator activity even when Microsoft 365 auditing is disabled.

Also check query scope, permissions, pagination, and timezones. Do not treat a guessed IRM UAL operation name as a supported query contract.

**Diagnostic Steps.**

*Portal.* Open **Microsoft Purview → Solutions → Audit** and check whether auditing must be enabled. Separately, open **Insider risk audit log** at the top-right of an IRM tab and export the administrator activity for the suspect window. A zero-row query is inconclusive until permissions, filters, retention, workload ingestion, and a known positive-control event have been checked. See [turn auditing on or off](https://learn.microsoft.com/en-us/purview/audit-log-enable-disable).

*PowerShell.*

```powershell
Connect-ExchangeOnline -ShowBanner:$false
Get-AdminAuditLogConfig | Format-List UnifiedAuditLogIngestionEnabled
# Expected: UnifiedAuditLogIngestionEnabled : True
# If False: UAL is off — this is SEV-1 against any Zone 3 population

# Probe: confirm scoped source workload activity for the test user is actually written to UAL
# (Export IRM administrator activity separately from the portal Insider risk audit log.)
$testUserUpn = 'canary-irm-test@contoso.com'
$start = (Get-Date).ToUniversalTime().AddDays(-1)
$end   = (Get-Date).ToUniversalTime()
$sid   = [guid]::NewGuid().ToString()
$rows  = @()
do {
  $batch = Search-UnifiedAuditLog -StartDate $start -EndDate $end `
            -UserIds $testUserUpn `
            -SessionId $sid -SessionCommand ReturnLargeSet -ResultSize 5000
  $rows += $batch
} while ($batch.Count -gt 0 -and $rows.Count -lt 50000)
if ($rows.Count -ge 50000) { throw 'Narrow the UAL filter or split the UTC window; the export may be incomplete.' }
$rows.Count
```

*SIEM check.* Validate alert delivery through the dedicated IRM connector using a known alert ID and the connector's documented destination table (Scenario 18). Do not use `OfficeActivity` as a substitute for the independent Insider risk audit log.

**Resolution.**

1. Capture E-01..E-17 per §1 **before** flipping UAL on — the failing-state baseline must be preserved (the auditor needs to see what coverage was in effect at the suspect-window UTCs).
2. As an operator assigned the Exchange **Audit Logs** role (IRM membership alone is insufficient):
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

**Likely Cause.** [Risky Agents (preview)](https://learn.microsoft.com/en-us/purview/insider-risk-management-monitoring-agents) is available by default after service setup for organizations with supported licenses. Confirm licensing, auditing, supported hosts, and observer permissions. Supported hosts include Copilot Studio, Microsoft Foundry, and agents built using the P4AI SDK, not every agent architecture. **Administrative units are not supported for agent alerts**: a scoped analyst cannot see them. Do not assert an undocumented requirement to create an unrelated policy, a seven-day baseline, or a tenant rollout ring.

**Diagnostic Steps.**

*Portal.* Microsoft Purview → **Insider Risk Management** → **Policies** — view the available policy tabs from an **unrestricted** Insider Risk Management Admin context. Compare observed availability with the current supported-host/licensing documentation; record analytics state separately. Do not invent an in-portal Roadmap tab or require a seven-day baseline.

*PowerShell (supported audit-status checks only).*

```powershell
# Confirm Unified Audit dependency from Exchange Online, not an IPPS session
Connect-ExchangeOnline -ShowBanner:$false
Get-AdminAuditLogConfig | Select-Object UnifiedAuditLogIngestionEnabled, AdminAuditLogAgeLimit
# Policy inventory + Adaptive Protection state are portal/manual evidence:
# export Purview > Insider Risk > Policies and Settings pages for this cycle.
```

*Microsoft Graph (license / region check).*

```http
GET https://graph.microsoft.com/v1.0/organization
  ?$select=id,displayName,assignedPlans,countryLetterCode,verifiedDomains
```

Use the licensing service description and monitored-user license assignments to verify entitlement. Organization `assignedPlans` is only supplemental inventory; `countryLetterCode` does not identify the tenant's rollout ring or prove feature availability.

*Alert evidence.* Inspect actual Risky Agents alerts in Purview, or reconcile known alert IDs with the dedicated Sentinel IRM connector. Policy-change records do not prove that a policy fired, and no `OfficeActivity.PolicyName` contract is asserted.

**Resolution.**

1. **Confirm entitlement and supported agent hosts.** Roadmap status describes rollout, not the tenant's assigned ring. Record the observed tenant feature state and use Microsoft support for unresolved availability questions.
2. **Complete documented service setup and permissions**; preserve the firm's Investigator/Approver separation. Do not require an unrelated departing-user policy to initialize Risky Agents.
3. **Record observed availability** and escalate unresolved entitlement/setup issues with evidence. Microsoft does not publish the previously asserted auto-application SLA.
4. **Inspect supported settings** and actual alert details before tuning; do not assume priority user/content settings from user policies apply to agent identities.

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

**Symptom.** A `Risky AI usage` policy is configured for a Zone 3 trading-desk population and has been observed for > 14 days (firm diagnostic window). The Alerts queue shows **zero alerts** despite approved seed activity. Browser collection was assumed deployed; nobody can produce deployment evidence. Do not infer a DLP-style IRM Test/On switch or assume every seed action is a supported indicator.

**Likely Cause.** The signal source for `Risky AI usage` is the **browser extension** — the **Microsoft Compliance Extension** on Edge and Chrome — and the extension is **Windows-only**. Common gap modes:

1. **Extension not deployed via Intune** to the in-scope Windows population (admins assumed it was deployed at IRM rollout but never confirmed via Intune coverage report).
2. **Non-Edge / non-Chrome browser usage** — the in-scope population uses Firefox or Safari, which are **not supported** by the IRM browser extension family at the time of writing.
3. **macOS / Linux / iOS / Android population in scope** — the extension is **Windows-only**; non-Windows endpoints produce silent zero.
4. **Intune configuration profile assigned but not applied** — device is in a group that was excluded later; device check-in lag; user installed personal Edge/Chrome that bypasses managed Edge/Chrome extension management.
5. **Browsing indicators disabled** in IRM Settings → Policy indicators.
6. **Device not onboarded** to Microsoft Purview (endpoint signal source).
7. **PAYG dependency** for non-M365 AI sources surfaced in scope (some AI-source coverage requires PAYG enablement per Microsoft Learn).

**Diagnostic Steps.**

*Portal.* Microsoft Purview → **Insider Risk Management** → **Settings** → **Policy indicators** — confirm the relevant browsing / AI indicators (e.g., "Risky AI prompt," "Risky AI response," "Browsing risky AI site") are **enabled** and not disabled tenant-wide. Then **Settings** → **Device onboarding** — confirm the test device appears in the onboarded list. On the test device itself: Edge `edge://extensions/` and Chrome `chrome://extensions/` — confirm the Microsoft Compliance Extension (Edge and Chrome) are present, enabled, and not in error state.

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

*Endpoint evidence.* Capture the managed browser policy and extension state on the test endpoint, then inspect the corresponding activity in IRM. Browser process command lines and unverified `DeviceEvents.ActionType` strings do not prove extension health. Intune assignment is not proof that a device applied a policy; record device-side results as well.

**Resolution.**

1. **Push the extension via Intune** to the in-scope Windows population. The extension is delivered as a managed Edge / Chrome extension via the Edge management policies / Chrome enterprise policies under Intune Configuration profiles. Microsoft Learn `insider-risk-management-browser-support` documents the supported deployment method; verify at deployment time.
2. **Review managed-browser enforcement.** Validate the supported Conditional Access and device-management controls for each application (Control 1.11). Do not assume Conditional Access can force every external AI website into managed Edge.
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
- **Browser-policy enforcement.** Test application-specific access and endpoint browser policies; document unsupported external AI sites rather than claiming universal Conditional Access coverage.
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

*PowerShell + exported evidence.*

```powershell
Connect-IPPSSession -ShowBanner:$false
# Inventory priority policy evidence from portal export
$priorityPolicies = Import-Csv '.\evidence\irm-priority-policies.csv'
$priorityPolicies | Select-Object PolicyName, Status, PriorityUserGroups, ContentExpansion

# Membership of a named priority user group (Microsoft Graph)
Connect-MgGraph -Scopes 'Group.Read.All','User.Read.All' -NoWelcome
$priGroup = Get-MgGroup -Filter "displayName eq 'IRM-Priority-FrontOffice'"
Get-MgGroupMember -GroupId $priGroup.Id -All | Measure-Object
```

*Alert-volume evidence.* Use **IRM → Reports → Alerts** or the alert export, counting distinct alert IDs rather than administrator review operations. See [IRM reports](https://learn.microsoft.com/en-us/purview/insider-risk-management-reports).

**Resolution.**

1. **Refine the priority user group with Compliance + HR.** A priority user group is **role-based**, not "everyone." For an FSI firm, defensible priority categories include: trading desk; MNPI-handlers; agent admins / agent owners; senior management with access to ICFR-relevant data; named registered representatives with a compliance flag. Document the rationale per group.
2. **Refine the priority content list.** Remove routine client-portal SharePoint sites; keep only content that genuinely warrants priority weighting (e.g., MNPI deal rooms, board materials, regulatory-filing draft sites).
3. **Tune under change control** using the policy's supported thresholds and indicator settings. Record any coverage reduction and compensating controls; do not assume IRM offers DLP-style Test/On policy modes.
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

*Portal.* Microsoft Defender portal (`security.microsoft.com`) → **Settings → Endpoints → Advanced features** → verify **Share endpoint alerts with Microsoft Compliance Center**. In **Purview → Settings → Insider Risk Management → Intelligent detections**, verify the Defender for Endpoint alert triage statuses selected for import. Microsoft documents **daily** import and the statuses Unknown, New, In progress, and Resolved; this is not an IRM **Settings → Connectors** heartbeat. See [intelligent detections](https://learn.microsoft.com/en-us/purview/insider-risk-management-settings-intelligent-detections) and [Defender advanced features](https://learn.microsoft.com/en-us/defender-endpoint/advanced-features#share-endpoint-alerts-with-microsoft-compliance-center).

Microsoft 365 admin center → **Billing** → **Licenses** — confirm the in-scope users carry MDE P2 (or the equivalent E5 / E5 Security bundle).

*Device inventory.* Export the device inventory and onboarding status from Defender. Intune `managedDevices` inventory measures management state, not Defender onboarding, and cannot prove MDE signal coverage.

*KQL (Defender XDR — confirm the test alert was raised).*

```kusto
AlertInfo
| where Timestamp > ago(7d)
| where DetectionSource == "WindowsDefenderAtp" or ServiceSource == "Microsoft Defender for Endpoint"
| where Title has_any ("Security policy","Defender disabled","Tampering","Antivirus disabled")
| join kind=leftouter (
    AlertEvidence
    | where Timestamp > ago(7d)
    | where isnotempty(AccountUpn)
    | project AlertId, AccountUpn
  ) on AlertId
| project Timestamp, AlertId, Title, Severity, Category, AccountUpn
| order by Timestamp desc
```

Compare the returned account with the time-stamped policy-scope evidence. Defender advanced hunting uses `Timestamp`; account entities are in `AlertEvidence`, joined on `AlertId`, not an `Entities` column in `AlertInfo`. See [AlertInfo](https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-alertinfo-table) and [AlertEvidence](https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-alertevidence-table).

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

**Likely Cause.** Treat the timing as a correlation, not proof of an IRM connector-mapping defect. Check the current Defender for Cloud Apps detection inventory and the separately configured IRM cloud-storage indicators. A threat-detection change does not establish that every Defender anomaly should generate an IRM alert.

**Diagnostic Steps.**

*Portal.* Review **Defender → Cloud Apps → Policies → Policy management** and **Activity log**, plus the health of the app connector for the affected storage source. In Purview, verify the corresponding IRM cloud-storage indicators and policy scope. Record the actual app activity, rather than inventing a generic IRM Defender for Cloud Apps connector sync status.

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

*Evidence comparison.* Compare app-connector activity, Defender alerts, and IRM activity/alerts as separate datasets over an available retention window. Use the actual service change date from release notes; do not substitute a fabricated 2025-06-15 cutover or search activity `ActionType` values as though they were anomaly alert names.

**Resolution.**

1. **Read the migration release notes** for Defender for Cloud Apps — Microsoft Learn `defender-for-cloud-apps/whats-new`. Identify the specific policies affected, the new policy names, and any opt-in steps.
2. **Re-enable / opt-in to the replacement detections** as **Defender for Cloud Apps Admin**.
3. **Verify the supported IRM cloud-storage indicators** and their documented prerequisites; do not attempt an undocumented IRM connector remapping.
4. **Change permissions only for a demonstrated connector error** and the documented app-connector requirements, not a presumed migration-related scope expansion.
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

**Likely Cause.** The expectation of a one-to-one Entra-risk-to-IRM-alert mapping may be wrong. The [policy indicator reference](https://learn.microsoft.com/en-us/purview/insider-risk-management-settings-policy-indicators) says only Entra alerts in **ConfirmedCompromised** or **Remediated** state are evaluated. A High risk level alone is not sufficient. Verify the enabled indicator, trigger, and scope; do not assume a generic IRM **Entra ID Protection connector** or that dismissing Entra user risk deletes IRM evidence.

**Diagnostic Steps.**

*Portal.* Review **Entra ID Protection → Risky users / Risk detections** with appropriate read permissions and licensing, then separately review IRM policy triggers, indicators, user scope, and AU visibility. Correlate evidence manually or through the firm's tested SIEM rule; an elevated Entra risk level alone does not prove an IRM alert should exist.

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

Compare the sign-in evidence with actual IRM user activity and alert details; no documented `OfficeActivity.AdditionalInfo` marker is required for this correlation.

**Resolution.**

1. Confirm the documented IRM signal path for the activity; record unsupported correlations as a coverage gap, not an instruction to enable a nonexistent connector.
2. Coordinate with the licensing owner to assign Entra ID P2 to the in-scope population.
3. Coordinate identity-risk disposition with the IRM Analyst under the firm's SOP; preserve both datasets rather than assuming dismissal terminates IRM correlation.
4. Re-trigger the seed scenario from a synthetic test user with a controlled risky sign-in (e.g., from a documented test-VPN egress IP) and confirm IRM enrichment.
5. Document the dead window and the affected user population.

**Prevention.**

- **Risk-state dismissal governance.** IT Helpdesk SOP requires checking IRM correlation before dismissing a user-risk row; document with a checklist.
- **License-assignment automation.** Group-based licensing for Entra ID P2 per in-scope group.
- **Correlation checks** against documented IRM indicators and the firm's tested SIEM mappings.

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
2. **Schema drift** — the CSV no longer maps to the resignation scenario's required UPN, `ResignationDate`, and `LastWorkingDate` data. Source column names are configurable; `EmployeeID` is not the connector's required identity key.
3. **Storage / staging account** issue (where ingestion uses a staging blob; SAS expiry; container ACL change).
4. **Dual-system conflict** — same `UserPrincipalName` arriving from two HR sources with conflicting `LastWorkingDate`.
5. **Source HRIS does not publish `LastWorkingDate`** for a worker class (e.g., contractors) — the IRM template silently has no trigger date.
6. **Network egress block** — a firewall change broke the egress path used by the upload script.

**Diagnostic Steps.**

*Portal.* Microsoft Purview → **Settings** → **Data connectors** → **My connectors** → [HR connector] → confirm last-success UTC, last-error message, ingestion row count (`RecordsSaved`), and schema; use **Progress → Download log** to compare upload timestamps and errors against the source CSV. Then Microsoft Purview → **Insider Risk Management** → **Policies** → [`Data theft by departing users`] → **Conditions** → activity lookback. Microsoft Entra admin center → **App registrations** → [HR connector app] → **Certificates & secrets** → confirm expiry > 30 d out.

*PowerShell.*

```powershell
# Verify the certificate / secret expiry on the backing app registration
Connect-MgGraph -Scopes 'Application.Read.All' -NoWelcome
$app = Get-MgApplication -Filter "displayName eq 'IRM-HR-Connector'"
$app.PasswordCredentials | Select-Object DisplayName, EndDateTime
$app.KeyCredentials      | Select-Object DisplayName, EndDateTime
```

*Sample row check (example headers, not a fixed connector schema).*

```powershell
# Match these example headers to the connector's actual mapping
Import-Csv .\hr-upload.csv |
  Where-Object UserPrincipalName -eq 'subject@contoso.com' |
  Select-Object UserPrincipalName, ResignationDate, LastWorkingDate
# Validate mapped values against the HR source and ISO 8601 date/time requirements.
```

**Resolution.**

1. **Rotate the certificate / secret** on the Microsoft Entra app registration; update connector configuration; re-run job.
2. **Re-map scenario fields** if the HRIS schema drifted. For resignation, map UPN, `ResignationDate`, and `LastWorkingDate`; use ISO 8601 date/time, not an assumed date-only format. The last-working date must be no more than six months before or one year after upload. Use at most 500 records per CSV ingestion. See [Import HR data](https://learn.microsoft.com/en-us/purview/import-hr-data).
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

**Symptom.** An Insider Risk Management Admin submitted a Forensic Evidence capture request 6 hours ago for a high-severity case. The request is awaiting approval. The Investigator cannot yet review captures and cannot identify an available Approver.

**Likely Cause.**

1. **Approver group empty** — the role group `Insider Risk Management Approvers` has zero members.
2. **Role overlap (firm SoD violation)** — review Admin requester, Approver, Investigator, and catch-all memberships. Do not assume the service enforces the firm's distinct-human approval rule.
3. **Approver group populated but all members are out of office / disabled / on PTO**.
4. **Role-propagation lag** — Approver was added < 30 min ago; permission has not propagated.
5. **Approval workflow notification not delivered** (mailbox rule, Teams notification not enrolled).

**Diagnostic Steps.**

*Portal.* Microsoft Purview → **Insider Risk Management** → **Forensic evidence** → **User management** → review the actual request, decision, requester, and timestamps. Then **Settings → Roles and groups → Role groups** → review Approvers, Admins, Investigators, catch-all membership, and AU scope; verify distinct requester and approver as well as the firm's Investigator separation.

*Role and approval evidence.* Review the actual **Purview** role groups under **Settings → Roles and groups → Role groups**, not similarly named Entra groups. Per [IRM permissions](https://learn.microsoft.com/en-us/purview/insider-risk-management-permissions), **Admins** create capture requests, **Approvers** approve them, and **Investigators** view captures. An Investigator-only assignment cannot submit a request. Review the request in the Forensic evidence page and export the independent Insider risk audit log; do not require undocumented UAL operation names.

**Resolution.**

1. **Populate the Approvers role group** with members **distinct from Investigators** as **Purview Compliance Admin**. Recommended membership: a small set of senior personnel from Compliance + Privacy + an independent senior IRM Analyst, signed off by CISO and General Counsel.
2. **Resolve any Investigator-Approver overlap** — remove the overlap as a SEV-2 SoD remediation per Scenario 21.
3. **Wait the documented role-propagation window** (up to 30 min per Microsoft Learn) before re-attempting submit.
4. **Have an unrestricted IRM Admin submit the request**; an independent Approver reviews it with documented justification. Preserve the firm's Investigator/Approver separation as well as requester/approver separation.
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

**Symptom.** The IRM Admin cannot create the required forensic evidence policy, or approved users produce no captures. Record the actual error text and distinguish policy creation, per-user approval, device capture, upload, and capacity failures.

**Likely Cause.**

1. **Microsoft Purview Client not deployed** to the in-scope Windows 10/11 Enterprise devices via Intune; Forensic Evidence requires the client.
2. **Forensic evidence capacity unavailable** — the add-on or eligible legacy-platform trial is absent or exhausted. This is separate from IRM indicator PAYG.
3. **Devices not onboarded** to Microsoft Purview (separate from Microsoft Defender for Endpoint onboarding).
4. **Windows edition mismatch** — devices are Windows 10/11 Pro (not Enterprise); Forensic Evidence is Enterprise-only.
5. **Region unavailability** — Forensic Evidence not available in the tenant's cloud.
6. **Capture-policy prerequisite missing** — verify the forensic policy and approved per-user request; a forensic policy alone does not authorize user capture.

**Diagnostic Steps.**

*Portal.* **Insider Risk Management → Forensic evidence → Settings → Forensic evidence capacity**: check add-on entitlement and monthly ingestion usage. Confirm device onboarding, Microsoft Purview Client deployment, supported hardware/OS, policy assignment, and per-user request approval. Adding a user to a policy does not authorize capture. Follow [configure forensic evidence](https://learn.microsoft.com/en-us/purview/insider-risk-management-forensic-evidence-configure) and [manage forensic evidence](https://learn.microsoft.com/en-us/purview/insider-risk-management-forensic-evidence-manage).

*PowerShell (audit-status evidence only).*

```powershell
Connect-ExchangeOnline -ShowBanner:$false
Get-AdminAuditLogConfig | Select-Object UnifiedAuditLogIngestionEnabled, AdminAuditLogAgeLimit
# Capture forensic capacity entitlement and usage from the portal separately.

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

1. **Resolve forensic evidence capacity entitlement** with the licensing owner. Paid capacity uses 100 GB/month ingestion units; unused capacity does not carry forward. A 20 GB trial is limited to the legacy commerce platform and expires when consumed or one year after activation, whichever is earlier.
2. **Push the Microsoft Purview Client** via Intune to the in-scope Windows 10/11 Enterprise population. Validate coverage report.
3. **Onboard missing devices** to Microsoft Purview (separate from MDE; both are required).
4. **Edition gap** — coordinate with the device-management team to upgrade Windows 10/11 Pro devices to Enterprise via the firm's licensing program where Forensic Evidence is required.
6. **Re-attempt policy creation** after each prerequisite is satisfied.

**Prevention.**

- **Pre-flight checklist** for Forensic Evidence rollout: capacity add-on ✓, Purview Client deployed ✓, devices/hardware supported ✓, unrestricted Admin requester and independent Approver ✓, Investigator access ✓, state-law notice posture confirmed ✓.
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

**Symptom.** A manual clip review or firm-implemented expiry ledger identifies a Forensic Evidence clip that is **115 days old from capture**, attached to an open IRM case, and has **not been exported**. The clip auto-deletes at 120 days after capture. If lost, the firm cannot reconstruct the visual evidence supporting the investigation; the investigation may stall or have to rely on second-best evidence (audit logs, file-access events) that does not show the user's screen state.

**Likely Cause.** No export workflow was triggered after capture. Common reasons:

1. **The clip was captured without an assigned post-capture export owner** — handoff to Records Retention or eDiscovery hold was not in the Investigator's runbook.
2. **Approver pipeline ignored the post-capture step** — Approver focused on capture approval, not retention promotion.
3. **No automated alert** at the 90-day threshold; the case sat in the queue past the warning window.
4. **Records Retention label not yet defined** for Forensic Evidence clips in Control 1.9; the Investigator did not know which label to apply.
5. **eDiscovery (Premium) hold not in place** for the case subject; legal hold path was not invoked.

**Diagnostic Steps.**

*Portal.* Review actual captured activity and maintain a firm aging register from capture time (not approval time), request/decision evidence, and required export deadline. Do not assume a native `Captures` filter or countdown field; preserve actual portal labels and timezone.

*Inventory evidence.* Use the **Forensic evidence** page's captured activity and actual capture timestamps. Maintain a firm-owned aging register with capture time, case reference, export decision, and exported-file hash. Microsoft does not document `Get-IRMForensicCapture`; an approval timestamp is not a clip's capture timestamp. Base reminders on captured clips, not request approvals.

**Resolution — Emergency Export Workflow.**

1. **Convene the case team within 4 h** of identifying the at-risk clip — Investigator + Approver + Compliance + Legal + Privacy + Records Retention Custodian.
2. **Determine retention path:**
   - **Path A — Records Retention label (Control 1.9).** Apply the firm's `FSI-Records-7yr-WORM` (or stricter) retention label to the exported clip and store in the immutable evidence bucket.
   - **Path B — eDiscovery (Premium) hold (Control 1.19).** If litigation / regulatory hold is in scope, place the subject's mailbox / OneDrive / Teams on eDiscovery hold and add the exported clip to the eDiscovery case as a custodian-content item.
   - **Path C — Both** — apply the retention label **and** add to the eDiscovery hold; do not let a single point of failure (label deleted, hold released) lose the evidence.
3. **Download the clip** using the documented Forensic evidence portal workflow; capture the export manifest with SHA-256 sidecar; store in the Control 1.7 evidence bucket. No forensic clip PowerShell export cmdlet is asserted here.
4. **Cross-record the export** in both the IRM case and the eDiscovery case (where applicable).
5. **Document the case team's decision** on retention duration with Compliance + Legal sign-off.

**Prevention.**

- **Firm-owned aging reminders.** Calculate export deadlines from the capture register and review them daily; use the firm's 90-day/14-day escalation targets only after validating register ingestion. No native Sentinel `DaysToExpiry` field or forensic-inventory API is asserted.
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

$inSubjectStates | Select-Object Id, UserPrincipalName, State, Country
```

Use the HR system of record to confirm residency; an Entra profile's `State` is not legal residency evidence. Reconcile the approved HR roster with the portal capture inventory. There is no documented `Get-IRMForensicCapture` cmdlet.

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

**Symptom.** The IRM Triage Agent stops prioritizing new alerts. Record the actual dashboard error and agent state; elapsed time since setup alone does not identify the cause.

**Likely Cause.**

1. **Saved authentication expired** — the [get-started guide](https://learn.microsoft.com/en-us/purview/copilot-in-purview-triage-irm-agent-get-started) documents that user-context authentication lasts **90 days**; the agent stops until its configuration is manually saved again. This is an authentication-renewal rule, not an alert reassessment interval. Confirm identity mode because the agents overview also documents a dedicated agent-identity option.
2. **Security Copilot SCU (Security Compute Unit) capacity exhausted** — concurrent capacity allocation exceeded; Triage Agent silently degrades.
3. **PAYG billing issue** — the underlying PAYG subscription has a billing failure (expired payment method, exceeded budget cap).
4. **Plug-in / role assignment lapsed** during a Security Copilot upgrade.
5. **Feature lifecycle churn** — the Triage Agent moved from one preview ring to another; opt-in must be refreshed.

**Diagnostic Steps.**

*Portal.* Microsoft Security Copilot portal → **Settings** → **Owner settings** → **Capacity** — confirm SCU allocation and current consumption. Microsoft Purview → **Insider Risk Management** → **Triage Agent** → **Status** — confirm last-successful-run UTC and any error message. Azure portal → **Subscriptions** → [Security Copilot subscription] → **Cost analysis** and **Cost alerts** — confirm no billing failure.

*Capacity and run evidence.* Inspect the configured Security Copilot capacity in its supported management surface and the agent's actual run history. No Microsoft Graph `/beta/security/copilot/capacities` endpoint is documented for this task. A subscription being enabled does not prove available SCUs, and a search for invented `TriageAgent` UAL operations is not run-health evidence. Follow [Triage Agent setup](https://learn.microsoft.com/en-us/purview/copilot-in-purview-triage-irm-agent-get-started).

**Resolution.**

1. Re-enroll the Triage Agent — refresh saved authentication as **Insider Risk Management Admin**.
2. Increase Security Copilot SCU capacity if exhausted; coordinate with the Security Copilot Owner.
3. Resolve any PAYG billing failure with the Azure Subscription Owner.
4. Reassign role / plug-in if a Security Copilot upgrade dropped the assignment.
5. During the Triage Agent outage, increase manual triage cadence; document the compensating posture.

**Prevention.**

- **Connection review calendar.** For the documented user-context setup, renew before the 90-day authentication expiry by saving configuration again. Record the actual identity mode and next renewal; obtain clarification for dedicated-identity behavior rather than assuming parity.
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

**Symptom.** Privacy Officer notices raw user UPNs in place of pseudonyms. Check the actual privacy setting and independent IRM administrator audit log before attributing this to a toggle change: documented Triage Agent, metadata/content, and API/eDiscovery export exceptions can expose identities while anonymization remains enabled. If a setting change is confirmed, follow the firm's change/approval procedure.

**Likely Cause.**

1. **Inadvertent toggle-off** — admin clicked the wrong setting; assumed "Show usernames" was per-session; in fact it was tenant-wide.
2. **Misunderstanding the feature** — admin assumed pseudonymization defeats investigation; the supported pattern is per-investigation unmask, not tenant-wide off.
3. **Deliberate toggle-off without sign-off** — operator change without Privacy + Compliance + Legal sign-off.

**Diagnostic Steps.**

*Portal.* Microsoft Purview → **Insider Risk Management** → **Settings** → **Privacy** → confirm pseudonymization toggle state and last-modified-by/UTC.

*Audit and actor evidence.* Export **Insider risk audit log** filtered to Settings and the relevant actors/date range, then capture **Settings → Insider Risk Management → Privacy** separately. Preserve original local timestamps and timezone. Do not require undocumented `InsiderRiskMgmtUserUnmasked` or `TenantSettingChanged` UAL operations.

*Privacy boundaries.* [Microsoft's privacy settings reference](https://learn.microsoft.com/en-us/purview/insider-risk-management-settings-privacy) documents exceptions: prioritized Triage Agent alerts are not anonymized; activity/file metadata and file content can contain names; API and eDiscovery exports display usernames, while alert/case CSV exports preserve anonymization. Raw names in these surfaces do not by themselves prove the tenant setting was disabled.

**Resolution — Emergency Re-anonymization.**

1. **Capture the failing-state evidence** per §1 (E-07 in particular) **before** toggling pseudonymization back on.
2. **Re-enable pseudonymization** as **Insider Risk Management Admin**.
3. **Convene Privacy + Compliance + Legal within 4 h.** Document:
   - Which users had alerts viewed during the dead window
   - Which Investigators viewed which alerts
   - Whether any unmask actions during the window had documented investigation reasons (likely not, since the tenant was de-pseudonymized)
   - Whether the Privacy Officer must notify affected employees
4. **IRM Auditor review.** The IRM Auditor reviews all admin actions during the dead window via the independent IRM audit log; produces a signed audit memo for Compliance.
5. **Post-incident review** with documented control changes — typically: tighten Conditional Access on the IRM Admin role; require dual-control on pseudonymization toggle (e.g., second-Admin approval); add a daily Sentinel canary that asserts pseudonymization is on.
6. **Privacy register entry.**

**Prevention.**

- **Daily configuration review.** Capture the actual Privacy setting and review changes in the independent IRM audit log; no native Sentinel `PseudonymizationEnabled` state field is asserted.
- **Conditional Access lock-down** on IRM Admin role for pseudonymization toggle (Control 1.11); require step-up MFA + business-justification.
- **Firm-defined dual-control** on privacy changes — record a second review in the change-management system; the IRM Approvers role does not supply a native privacy-toggle approval gate.
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

*Evidence.* Reconcile the firm's re-identification approval register with the independent IRM audit log, privacy-setting changes, case notes, and export-access evidence. A universal per-investigator `UserUnmasked` event is not documented by the privacy settings reference. Do not treat its absence as proof that no identity was exposed.

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
Get-SupervisoryReviewPolicyV2 -ErrorAction Stop
# A successful query is inventory only; confirm permissions, AU scope, policy status, and user coverage.
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

1. **The correlation is not implemented** — the documented IRM connector exports alerts to Sentinel; it does not turn a Sentinel anomaly into an IRM alert.
2. **Service-principal IDs vs. user identities** — resolve actual immutable identifiers from each payload; do not invent a service-principal UPN.
3. **Missing watchlist** in Sentinel that maps agent service-principal IDs to IRM agent identities.
4. **Office 365 / Defender XDR connector not forwarding IRM alerts** to Sentinel.

**Diagnostic Steps.**

*Portal.* Microsoft Sentinel workspace → **Data connectors** → verify the dedicated **Microsoft 365 Insider Risk Management** connector and its **SecurityAlert** ingestion, and verify the actual Entra sign-in source separately. Check **Export alerts** in IRM and the permissions of each reviewer. The general Office 365 connector is not evidence of IRM administrator-log ingestion.

*KQL.*

```kusto
// IRM alerts ingestion check
SecurityAlert
| where TimeGenerated > ago(7d)
| where ProductName has_any ("Microsoft 365 Insider Risk Management","Microsoft Purview")
| summarize Alerts = count() by bin(TimeGenerated, 1d)
```

Inspect actual `SecurityAlert` entities and source sign-in records before designing a join. `AgentServicePrincipalUpn`, `AgentDisplayName`, and a universal `BehaviorAnalytics.ActivityType == "AnomalousSignIn"` contract are not documented for this integration. Use immutable object IDs from the payload and the firm's agent registry; a missing counterpart can be legitimate because the products detect different behavior. See [Sentinel UEBA sources and schema](https://learn.microsoft.com/en-us/azure/sentinel/ueba-reference).

**Resolution.**

1. **Configure / verify the Sentinel connector** for IRM alerts (Control 3.9).
2. **Publish the agent-identity watchlist** to Sentinel — immutable service-principal/object IDs cross-referenced to agent host, display name, and owner.
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

*Evidence.* Group the actual IRM alert export by the agent identity exposed in that export and reconcile it with the agent registry. Do not depend on an undocumented `ExtendedProperties.AgentDisplayName` field.

**Resolution.**

1. **Suspend the offending agent** via Power Platform Admin Center (or revoke its workload identity sign-ins via Entra) while remediation is in progress; coordinate with the agent owner.
2. **Root-cause via agent-design review** with the Copilot Studio Maker, Power Platform Admin, and AI Governance Lead — narrow knowledge sources, scope permissions, and re-validate against Control 2.16 RAG.
3. **Re-baseline the agent's Entra Agent ID permissions** to least privilege (Control 2.26); remove unused Graph scopes.
4. **Review supported agent-policy tuning** against the current agent-monitoring documentation; do not assume a per-agent threshold control exists or blanket-suppress the agent.
5. **Re-publish the agent** under Control 2.3 Change Management (CAB) with documented design changes.

**Prevention.**

- **Agent baseline review** at publish time per Control 2.25 (Agent 365 Inventory) and Control 2.16 (RAG).
- **Agent signal validation** during onboarding; record the tuning controls actually exposed by the service.
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
2. **T+1h:** Open eDiscovery (Premium) case (Control 1.19); place all relevant custodian mailboxes, OneDrive, Teams, SharePoint, and Copilot interaction sources on hold. A custodian hold does not extend native forensic clip retention; export required clips separately before expiry.
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
$inv = Get-RoleGroupMember -Identity 'Insider Risk Management Investigators' -ResultSize Unlimited -ErrorAction Stop | Select-Object -ExpandProperty Name
$apr = Get-RoleGroupMember -Identity 'Insider Risk Management Approvers' -ResultSize Unlimited -ErrorAction Stop | Select-Object -ExpandProperty Name
Compare-Object $inv $apr -IncludeEqual -ExcludeDifferent | Select InputObject
```

Also review Admins versus Approvers for requester/approver separation. Confirm actual Purview role-group membership and AU scope in the portal; Entra directory-role/PIM membership alone is not the Purview role-group record.

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

*Portal.* Review Forensic evidence capture settings, the request/approval, clip access, and the independent IRM audit log. Preserve available actor and time evidence; do not require an undocumented `ForensicEvidenceClipViewed` UAL operation.

**Resolution — Emergency containment.**

1. **Contain access** — preserve the clip and review unrestricted Investigator/catch-all role membership with the authorized role administrator. An Auditor cannot view clips; do not assume a native per-clip quarantine ACL for Privacy + Auditor.
2. **Convene Privacy + Compliance + Legal + CISO within 1 hour.**
3. **Document the exposure scope** — exactly which records the Investigator could see; was data exfiltrated from the IRM portal (e.g., screenshot of the clip)? The independent IRM audit export, case records, and UAL workload records support the review.
4. **Storage protection review** — document the service's supported encryption and access controls. Do not assume a tenant-managed forensic clip CMK or attempt key rotation without a documented supported configuration.
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

*Portal.* Review prioritized alerts, explanations, and analyst feedback in the Triage Agent dashboard. Keep a firm-owned comparison of agent prioritization and human dispositions. Do not assume a native **Score distribution** tab or a documented `SecurityAlert.ExtendedProperties.TriagePriorityScore` numeric field; define any derived metric and its scale explicitly.

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

**Symptom.** A regulator (FINRA, SEC, NYDFS, or OCC) examiner requests IRM-case evidence for a 14-month-old investigation. The IRM case is **Closed** or no longer available; required clips or exports cannot be located. Compliance must produce evidence within the examiner deadline (typically 10–30 calendar days depending on authority and request type).

**Likely Cause.**

1. **Forensic Evidence auto-deleted at 120 days** (the central retention boundary; see §0/§1).
2. **Case promotion to Records Retention (Control 1.9) was not performed** at investigation closure.
3. **eDiscovery hold (Control 1.19) was not placed** on case-relevant custodians at investigation start.
4. **Audit log retention boundary** — the IRM solution audit log retains activity for 180 days independently of Microsoft 365 Audit licensing; export before expiry.

**Diagnostic Steps.**

*Portal.* Microsoft Purview → **Insider Risk Management** → **Cases** → search for the case ID; confirm archived state and last-action UTC. Microsoft Purview → **Records Management** → **Disposition** — search for retention-promoted artifacts referencing the case ID. Microsoft Purview → **eDiscovery (Premium)** → search for any hold tagged to the custodians at the case time.

*Retention check.* The independent IRM administrator audit log retains data for 180 days, so a 14-month-old administrator action requires a previously preserved export. UAL retention and eDiscovery holds do not extend this independent log or native forensic clip retention. Search the firm's preserved evidence first; use UAL only for workload records actually captured and retained there.

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

### Technical verification record — 2026-10-18

This review used live Microsoft Learn search/fetch, not tenant access or screenshots. **Last Verified** records the technical documentation review; the historical **Last UI Verified** stamp is unchanged. Firm SLAs, policy names, case registers, approval workflows, aging reminders, and custom SIEM joins are implementation requirements/examples, not Microsoft features or delivered automation. Regulatory mappings and legal interpretations were not re-evaluated.

| Claims checked / discrepancies corrected | Primary sources |
|---|---|
| Independent, always-enabled 180-day administrator audit log; separate alert export and SIEM evidence | [IRM audit log](https://learn.microsoft.com/en-us/purview/insider-risk-management-audit-log), [data sharing](https://learn.microsoft.com/en-us/purview/insider-risk-management-settings-share-data), [enable auditing](https://learn.microsoft.com/en-us/purview/audit-log-enable-disable) |
| Risky Agents supported hosts, preview/default behavior, AU and guest-content limits; no asserted rollout ring, initialization SLA, or invented policy schema | [Monitor agents](https://learn.microsoft.com/en-us/purview/insider-risk-management-monitoring-agents), [policy templates](https://learn.microsoft.com/en-us/purview/insider-risk-management-policy-templates), [setup/licensing](https://learn.microsoft.com/en-us/purview/insider-risk-management-configure) |
| Browser Windows-only signal boundary, native-vs-extension activities, and both extension-store IDs | [Browser support](https://learn.microsoft.com/en-us/purview/insider-risk-management-browser-support), [policy indicators](https://learn.microsoft.com/en-us/purview/insider-risk-management-settings-policy-indicators) |
| Defender sharing/import statuses, Entra accepted alert states, and Cloud Apps separation; unsupported June 2025 migration narrative removed | [Intelligent detections](https://learn.microsoft.com/en-us/purview/insider-risk-management-settings-intelligent-detections), [Defender advanced features](https://learn.microsoft.com/en-us/defender-endpoint/advanced-features), [policy indicators](https://learn.microsoft.com/en-us/purview/insider-risk-management-settings-policy-indicators) |
| Forensic Admin requester / Approver / Investigator roles, AU limits, policy plus per-user approval, supported endpoint/client/hardware, capacity add-on, export/aging boundary | [Permissions](https://learn.microsoft.com/en-us/purview/insider-risk-management-permissions), [forensic overview](https://learn.microsoft.com/en-us/purview/insider-risk-management-forensic-evidence), [configure](https://learn.microsoft.com/en-us/purview/insider-risk-management-forensic-evidence-configure), [manage](https://learn.microsoft.com/en-us/purview/insider-risk-management-forensic-evidence-manage) |
| HR mapped UPN/resignation/last-workday data, ISO timestamps, upload bounds, and 500-record cap; no asserted connector-health Graph API | [Import HR data](https://learn.microsoft.com/en-us/purview/import-hr-data) |
| Triage Agent user-context authentication expiry, configuration renewal, capacity/plugin/data-sharing prerequisites; identity-mode uncertainty | [Get started](https://learn.microsoft.com/en-us/purview/copilot-in-purview-triage-irm-agent-get-started), [agent identities](https://learn.microsoft.com/en-us/purview/copilot-in-purview-agents-overview), [agents](https://learn.microsoft.com/en-us/purview/copilot-in-purview-agents), [billing](https://learn.microsoft.com/en-us/purview/purview-billing-models), [activity dashboards](https://learn.microsoft.com/en-us/purview/insider-risk-management-activities) |
| Privacy exceptions, separate firm re-identification approvals, and case evidence; no universal unmask UAL event | [Privacy](https://learn.microsoft.com/en-us/purview/insider-risk-management-settings-privacy), [case workflow](https://learn.microsoft.com/en-us/purview/insider-risk-management-cases) |
| Adaptive Protection risk levels versus alert severity / Entra user risk; quick-setup test/report-only enforcement; supported DLP condition | [Adaptive Protection](https://learn.microsoft.com/en-us/purview/insider-risk-management-adaptive-protection), [Set-DlpComplianceRule](https://learn.microsoft.com/en-us/powershell/module/exchangepowershell/set-dlpcompliancerule) |
| Advanced-hunting timestamp/entity joins and Sentinel identity-schema boundaries; unsupported audit/agent fields withdrawn | [AlertInfo](https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-alertinfo-table), [AlertEvidence](https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-alertevidence-table), [UEBA reference](https://learn.microsoft.com/en-us/azure/sentinel/ueba-reference) |

**Unresolved source conflicts:** forensic articles disagree on capture versus ingestion aging and whether export is possible after deletion; the overview also mentions earlier deletion at preview end. Export required clips before the earliest applicable boundary and seek Microsoft clarification; post-expiry recovery is unverified. Triage Agent's dedicated-identity mode is documented separately from the 90-day user-context procedure; renewal parity is not established. Live UI, tenant entitlements, ingestion, capture, approval enforcement, and custom automation remain untested.

---

*Updated: October 2026 | Version: v1.6.2 | UI Verification Status: Needs Review (live UI not tested)*
