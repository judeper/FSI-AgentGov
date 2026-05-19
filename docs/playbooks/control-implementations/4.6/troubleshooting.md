# Control 4.6: Grounding Scope Governance — Troubleshooting

> This playbook provides FSI-grade troubleshooting for [Control 4.6 — Grounding Scope Governance](../../../controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md).
>
> **Last UI Verified:** April 2026
> **Audience:** SharePoint Admin, Power Platform Admin, Purview Compliance Admin, AI Governance Lead, Compliance Officer, Privacy Officer, Incident Response Lead.
> **Sovereign clouds covered:** Commercial, GCC, GCC High, DoD (parity caveats noted in §4).
> **Severity-of-control statement.** Grounding-scope failures expose the firm to: customer NPI / MNPI / supervisory-record / draft-filing disclosure via Microsoft 365 Copilot; loss of supervisory visibility; books-and-records integrity gaps. **Treat suspected scope leaks as cybersecurity events first, configuration issues second.**

> **Disclaimer.** This playbook supports compliance with FINRA, SEC, NY DFS, GLBA, OCC, Fed, and CFTC requirements; it does not by itself satisfy any regulatory obligation. Implementation requires firm-specific policy, role assignment, and Compliance / Legal review. Microsoft does not publish per-incident SLAs for grounding-scope misconfiguration; all response windows below are firm-defined targets, not vendor commitments.

---

## §1 — FSI Incident Handling — READ THIS FIRST

A confirmed grounding-scope failure is, by default, treated as a potential **NY DFS 23 NYCRR 500 §500.17(a)** cybersecurity event, a potential **SEC Regulation S-P §248.30(a)(4)** customer-notification event (where customer NPI is implicated), a **FINRA Rule 4511 / SEC 17a-4(f)** books-and-records integrity event, and — where the agent involved is in scope of the firm's supervisory program — a **FINRA Rule 3110 / FINRA RN 24-09** AI-supervision event. Engineering does not make any reportability decision. Engineering's job is to (a) preserve evidence, (b) put compensating controls in place, (c) escalate to Compliance, Legal, Privacy, and the CISO per the matrix below.

### 1.1 Severity matrix — grounding-scope events

| Severity | Trigger | Firm-defined response window | Escalation |
|---|---|---|---|
| **SEV-1** | Confirmed disclosure via Microsoft 365 Copilot, a Microsoft Copilot Studio agent, or Business Chat of: customer NPI; draft regulatory filing; supervisory record; MNPI / restricted-list / watch-list content; insider list; PII; OR a reproducible bypass of an in-effect RCD or RSS scope on a Zone 3 workload; OR personal OneDrive content surfaced inside a published declarative agent | Immediate (sample target ≤ 1 h to acknowledge) | CISO + Compliance Officer + General Counsel + Privacy Officer within 1 h (firm-defined) |
| **SEV-2** | RCD or RSS configuration regressed on an in-scope site (no confirmed disclosure yet); DLP-for-Copilot connector block bypassed via a direct-URL knowledge source; Copilot Studio knowledge source pointing at an unsanctioned site discovered in inventory; suspected scope leak under investigation | Sample target ≤ 4 h | AI Governance Lead + SharePoint Admin + Power Platform Admin |
| **SEV-3** | RSS allow-list ceiling reached blocking a sanctioned business request; classic-page indexing gap on a single site; DAG report stale beyond the documented Microsoft Learn cadence; Copilot Studio knowledge source change not visible after the documented sync window | Sample target ≤ 1 business day | SharePoint Admin |
| **SEV-4** | Cosmetic / preview-feature regression; single-user "I cannot see content I should" on a non-regulated site | Best effort | Track in known-issues log; review at next governance cadence |

> Response windows above are **firm-defined** sample targets for FSI environments. Microsoft does not publish per-incident SLAs for grounding-scope misconfiguration. Adjust to your firm's IR runbook and supervisory commitments.

### 1.2 Reportability decision tree (escalate; do not decide internally)

| Trigger | Escalate to | Possible obligation (Legal owns the determination) |
|---|---|---|
| Customer NPI / PII surfaced via Copilot grounding | Privacy Officer + General Counsel | **GLBA 501(b)**; **SEC Regulation S-P §248.30(a)(4)** customer-notification (30 days from determination of misuse / reasonable likelihood of misuse) |
| Cybersecurity event materially affecting normal operations OR involving NPI of a NY-resident consumer | CISO + General Counsel | **NY DFS 23 NYCRR 500 §500.17(a)** — 72-hour Superintendent notification (clock starts at **determination**, not first alert) |
| Loss of supervisory visibility on AI-surfaced communications (e.g., grounding scope drifted such that Communication Compliance no longer covers the surface) | Compliance Officer | **FINRA Rule 3110** supervisory system; **FINRA RN 24-09 / Rule 3110** AI / agent supervision reminder |
| Books-and-records gap (RCD or RSS change not auditable; grounding-scope change not retained) | Compliance Officer + General Counsel | **FINRA Rule 4511** / **SEC 17a-4(f)** books-and-records integrity |
| Insider misconduct using Copilot to bypass a known RCD scope | HR + General Counsel + Compliance Officer | **FINRA Rule 4530(b)** disclosure obligations; firm misconduct reporting |
| Records event affecting covered swap / trading content | Compliance Officer | **CFTC Rule 1.31** record retention |
| Agent grounded on uncontrolled scope and deployed to production (operational risk from the model surface itself) | Model Risk + Compliance Officer | **OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12) / Fed SR 26-2 (formerly SR 11-7)** model risk management |
| Aggregated AI-surfaced data reaches financial-disclosure-adjacent processes | Internal Audit + Compliance Officer | **SOX §302 / §404** ICFR |

**Engineering rule.** Engineering surfaces facts to Compliance / Legal / Privacy. Engineering does not assert "this is not a reportable event."

### 1.3 Evidence preservation — capture before remediation

Capture **all** of the following before any change is made, in this order. Hash each artifact (SHA-256) and record the storage location in the evidence pack.

1. Screenshots of: SharePoint Admin Center site detail page showing `RestrictContentOrgWideSearch` state; tenant Restricted SharePoint Search (RSS) state; Copilot Studio knowledge-source list per affected environment; the actual Copilot citation in Business Chat showing the leaked content (with timestamp visible).
2. `Get-SPOSite -Identity <url> | Select Url, RestrictContentOrgWideSearch, LockState, LastContentModifiedDate, Status` — full output for every affected site.
3. `Get-SPOTenant | Select EnableRestrictedSearchAllList, *Search*, *Copilot*, *AI*` — tenant-level state snapshot.
4. `Get-SPOTenantRestrictedSearchAllowedList` — full allow-list export with row count and SHA-256 sidecar.
5. `Get-MgSubscribedSku | Select SkuPartNumber, ConsumedUnits, PrepaidUnits` — Copilot SKU presence and consumption (rules in / rules out F3 silent no-op).
6. Copilot Studio knowledge-source inventory per environment (Power Platform Admin Center export and / or `Get-PowerPlatformEnvironment` plus per-environment knowledge-source list).
7. Unified Audit Log search for `SharePointFileOperation`, `CopilotInteraction` (and the documented Copilot / agent activity event names current at the time), and SPO admin events for the affected window — paginated CSV / JSON export with SHA-256 sidecar.
8. Data Access Governance (DAG) report for the affected sites at time of detection — capture **report generation timestamp**, not just download timestamp.
9. DLP-for-Copilot policy snapshot: `Get-DlpCompliancePolicy`, `Get-DlpComplianceRule` for any policy with the Copilot location enabled.
10. Zone classification register entry for the affected site / agent (per Control 2.1).
11. Tenant ID, cloud (Commercial / GCC / GCC High / DoD), UTC window of the incident, role used for capture, requesting user, affected user(s), and citation URL(s).
12. Record-retention proof: confirmation that the audit window covering the change is within retention (per Control 1.7) and that holds (per Control 1.13 / 1.14) are in place if litigation or examination is foreseeable.
13. Page composition snapshot for the affected site (modern vs classic ASPX) to rule in / rule out F10.

### 1.4 Compensating controls — apply during the gap

Apply as many as are operationally feasible without destroying evidence. Document each in the incident timeline.

- Tighten **DLP-for-Copilot** (Control 1.5) on the affected sensitive information type / sensitivity label from `TestWithNotifications` to `Enable` (Block) on the Copilot location.
- **Freeze new Copilot Studio publishes** touching the affected site or scope (Control 2.1 environment governance freeze).
- Run daily **Unified Audit Log** searches for `CopilotInteraction` against the affected user set during the gap (Control 1.7).
- Increase **Communication Compliance** review cadence on AI-assisted content from in-scope users (Control 1.10).
- **Suspend** the offending Copilot Studio agent (Control 2.16 agent lifecycle) until its knowledge source is corrected and re-reviewed.
- Apply **RCD = `True`** on the affected site as a containment action even if RSS is the long-term answer.
- Engage **eDiscovery hold** (Control 1.13 / 1.14) if litigation, examination, or arbitration is foreseeable.

### 1.5 Pre-escalation checklist (≥ 15 items — complete before opening a Microsoft Support ticket)

1. [ ] Tenant ID and cloud (Commercial / GCC / GCC High / DoD) confirmed.
2. [ ] Copilot SKU inventory verified — at least one user has a Microsoft 365 Copilot license (rules out F3 silent no-op).
3. [ ] Affected site URL(s), RCD state, and RSS allow-list membership state captured per §1.3.
4. [ ] Surface confirmed: **Business Chat** vs **in-app Copilot** (Word / Excel / PowerPoint / Outlook sidecar) vs **Copilot Studio agent** (rules in / out F1).
5. [ ] Time elapsed since the most recent RCD or RSS change recorded (rules out propagation-window false negative; verify the documented Microsoft Learn propagation window at the time of operation).
6. [ ] Copilot Studio knowledge-source inventory captured for every environment whose agents are in scope.
7. [ ] Direct-URL bypass check completed: any knowledge source pointing at a URL not in the sanctioned connector list (rules in F4).
8. [ ] OneDrive content path check for declarative agents — no personal OneDrive paths in any in-scope agent's knowledge source (rules in F6).
9. [ ] Page composition check: modern vs classic ASPX site contents enumerated (rules in F10).
10. [ ] DAG report generation timestamp recorded; staleness assessed against the documented Microsoft Learn cadence (rules in F5).
11. [ ] Sovereign cloud parity verified for **every** capability invoked in §4 (rules in F9).
12. [ ] Restricted-AU admin scenario ruled out (rules in F15) — confirm the operating admin is tenant-scoped, not Administrative Unit-scoped.
13. [ ] Bulk-change idempotency verified — no half-applied state left by a prior batched `Set-SPOSite` run (rules in F13).
14. [ ] Audit retention sufficient to evidence the change end-to-end (per Control 1.7 backbone).
15. [ ] Compliance Officer + General Counsel notified per the §1.1 severity matrix.
16. [ ] Privacy Officer notified if customer NPI / PII may be implicated.
17. [ ] Evidence pack hash + storage location recorded in the incident ticket.
18. [ ] Communication Compliance scope reviewed (does the affected surface still fall under a CC policy?).
19. [ ] Compensating controls listed in §1.4 applied or explicitly deferred with reason.

### 1.6 Worked example — confidential legal / M&A memo via mis-scoped surface

> **Scenario.** Compliance reports that a draft policy memo marked `Confidential — Legal` (alternate scenario: a draft M&A memo containing a non-public counterparty name) appeared as a citation in a Business Chat response for a user who is not on the deal team and should not have access. RCD was applied to `/sites/legal-drafts` last week.
>
> **Triage (first 30 minutes).** Severity = **SEV-1** candidate (confirmed disclosure of a supervisory / legal record; potential MNPI). Pause: confirm whether the surface was Business Chat (in scope of RCD / RSS) or in-app Copilot inside Word with the file already open (out of RCD scope — see F1). Capture the citation URL, the citation timestamp, the user account, and the tenant cloud. Run `Get-SPOSite -Identity https://contoso.sharepoint.com/sites/legal-drafts | Select Url, RestrictContentOrgWideSearch, LockState` — confirms `RestrictContentOrgWideSearch = True`. Run `Get-SPOTenantRestrictedSearchAllowedList` — site is **not** on the RSS allow-list. Run a Unified Audit Log search for the user's `CopilotInteraction` events in a tight UTC window around the citation; export paginated with SHA-256 sidecar.
>
> **Root cause path — investigate in this order.** (a) Propagation incomplete — rules in if the change is recent and the documented Learn propagation window has not elapsed. (b) **F11** — site is also on the RSS allow-list (RSS allow-list contains a site whose RCD is also `True`; depending on order of evaluation the user may experience apparent inclusion); fix is to remove from one of the two and document. (c) **F1** — user invoked Copilot in-app inside Word with the file already open; RCD does not scope the open-document grounding inside an Office app. (d) **F6** — file was duplicated to a OneDrive that backs a published declarative agent's knowledge source; the agent grounded on the OneDrive copy, not the SharePoint copy. (e) **F4** — a Copilot Studio agent has a direct-URL knowledge source pointing at the legal-drafts site that bypasses the SharePoint connector DLP block.
>
> **Containment.** Suspend any Copilot Studio agents whose knowledge source includes the site or any related OneDrive (Control 2.16). Tighten DLP-for-Copilot to Block on the relevant sensitive information type / label (Control 1.5). Freeze new Copilot Studio publishes in the affected environment (Control 2.1). Notify Compliance + Legal + Privacy. **Start the NY DFS §500.17(a) 72-hour determination clock with Legal** if NY-resident NPI or material cybersecurity-event criteria are implicated. **Open the Reg S-P §248.30(a)(4) 30-day customer-notification assessment** with Legal if customer NPI is implicated. If the memo concerns non-public deal information, notify the firm's MNPI / information-barrier monitor.
>
> **Remediation + evidence.** Resolve the actual cause path (e.g., remove the site from the RSS allow-list; remove the OneDrive knowledge source; correct the Copilot Studio agent's knowledge source list; verify DLP-for-Copilot block is in effect with a test interaction). Re-test from a non-deal-team user account. Preserve all captures with SHA-256 sidecar in the Control 1.7 evidence bucket. Produce the reportability memo to Compliance and the timeline export to Legal. Update the Zone classification register and the RSS allow-list change log.

---

## §2 — Decision matrix (symptom → likely cause → diagnostic → action → owner)

This matrix covers the dominant grounding-scope failure modes (F1–F16). Use it as a triage map before opening a Microsoft Support case.

| # | Symptom (what the user / admin sees) | Likely cause(s) | Deterministic diagnostic | Action | Owner |
|---|---|---|---|---|---|
| F1 | RCD applied; content still surfaces in **in-app Copilot** (Word / Excel / PowerPoint / Outlook sidecar) | Scope confusion — RCD governs enterprise grounding / Business Chat; in-app Copilot operates on the open document inside the Office app | Reproduce in **Business Chat** (cleared cache) vs in-app Copilot; if only in-app, F1 is in scope | Educate users; tighten **DLP-for-Copilot** (Control 1.5) on the SIT / sensitivity label so the in-app surface is blocked at runtime; apply sensitivity-label encryption to prevent open-document Copilot grounding | AI Governance Lead + Purview Compliance Admin |
| F2 | RSS allowed-list change not in effect after the change was made | Index rebuild / propagation pending — verify the documented Microsoft Learn propagation window at the time of operation (historically observed at 24–48 h; verify current) | Note change UTC; compare to documented window; re-test after the window | Wait the documented window; re-test; do not escalate before window elapses unless a SEV-1 disclosure has occurred | SharePoint Admin |
| F3 | RCD enabled; tenant has **no Microsoft 365 Copilot license assigned** → control silently no-op | Admin believes the control is enforcing; in fact nothing is being grounded by Copilot at all because no user can invoke it | `Get-MgSubscribedSku | Where SkuPartNumber -like '*COPILOT*' | Select SkuPartNumber, ConsumedUnits, PrepaidUnits` | Document the no-op state; either license at least one user or remove the false PASS from the control evidence pack; do not assert RCD effectiveness without at least one Copilot-licensed user | Entra Global Admin + AI Governance Lead |
| F4 | DLP blocks the SharePoint connector; maker still ingests the site by adding a **direct URL** in a Copilot Studio knowledge source | Connector-block ≠ URL-block; need both enforcement vectors | Inventory Copilot Studio knowledge sources per environment; cross-check URLs against the sanctioned connector list | Block at both layers: connector DLP + URL pattern policy; freeze publishes (Control 2.1) until inventory is clean | Power Platform Admin + Purview Compliance Admin |
| F5 | DAG report shows oversharing on a site that is RCD-protected | DAG cadence is delayed; report may pre-date the RCD change; OR RCD was rolled back | Capture DAG **report generation timestamp**; compare to RCD effective time; re-run DAG and compare | Re-run DAG; if oversharing persists in fresh report, treat as a real RCD failure and follow F1 / F11 path | SharePoint Admin |
| F6 | **Personal OneDrive content** appears in a declarative agent's grounding | Zone misconfiguration — Zone 1 personal-productivity content path reaching a Zone 2 / Zone 3 agent's knowledge source | Inventory each in-scope agent's knowledge sources; flag any OneDrive personal path | Remove the OneDrive knowledge source; suspend the agent (Control 2.16); update Zone register; cross-reference Controls 4.7, 1.5 | Power Platform Admin + AI Governance Lead |
| F7 | RSS 100-site ceiling reached; new site cannot be added | Governance-ceiling event, not a config event; RSS at the ceiling has effectively become a manually curated allow-list | `(Get-SPOTenantRestrictedSearchAllowedList).Count` | Convene RSS allow-list change-control board; document add / remove with business case ledger; do not "make room" without governance approval | SharePoint Admin + AI Governance Lead |
| F8 | Copilot Studio knowledge-source change not visible | Sync window — verify current sync window on Microsoft Learn | Note change UTC; re-test after documented window | Wait documented window; re-test; do not escalate before window elapses | Power Platform Admin |
| F9 | Sovereign cloud (GCC / GCC High / DoD): RCD / RSS / SAM / DAG / DLP-for-Copilot not at parity with Commercial | Operations fail silently with no portal warning | Re-confirm capability at https://learn.microsoft.com cloud parity matrix at time of operation | Document parity gap and apply fallback per §4; flag the affected control evidence as "operating with documented parity exception" | AI Governance Lead + SharePoint Admin |
| F10 | Modern pages indexed; classic ASPX pages on the same site still leak | Modern and classic pages flow through different indexing paths; site appears RCD-protected but classic content leaks | Enumerate site page library; classify modern vs classic | Convert classic to modern OR explicitly scope classic page content out via permissions / archive | SharePoint Admin |
| F11 | RSS allow-list contains a site whose RCD is also `True` | Conflicting scopes; depending on order of evaluation user may experience apparent inclusion or apparent zero results | `Get-SPOTenantRestrictedSearchAllowedList` cross-joined with `Get-SPOSite ... | Select RestrictContentOrgWideSearch` | Decide the intended state; remove the site from one of the two; document the decision in the RSS change log | SharePoint Admin |
| F12 | `CopilotReady` (or any custom) property bag value not persisting | PnP module stale; site read-only / archive; site collection admin missing | `Update-Module PnP.PowerShell`; check `Get-SPOSite ... | Select LockState, Status`; verify SCA on the site | Update PnP; resolve site state; re-add SCA; retry idempotently | SharePoint Admin |
| F13 | Bulk `Set-SPOSite -RestrictContentOrgWideSearch $true` partial failure | Throttling; locked sites; archive state — needs an idempotent retry pattern, not a one-shot loop | Re-run with per-site try / catch; collect failures; verify by re-querying every site | Implement idempotent retry with exponential backoff; produce a per-site PASS / FAIL report and remediate failures individually | SharePoint Admin |
| F14 | Guest / external user appears to inherit broader grounding than internal users | RCD does not change SharePoint permissions; B2B + grounding interaction surfaces what the guest already had access to | Audit the guest's effective SharePoint permissions; cross-reference Control 4.4 external sharing posture | Tighten SharePoint sharing posture; re-evaluate guest access model; do not treat as an RCD failure unless permissions are correct and grounding still leaks | SharePoint Admin + Entra Global Admin |
| F15 | Restricted-AU (Administrative Unit) admin attempting an RCD / RSS change and receiving an unexpected error | Some SPO admin surfaces do not honor AU scoping; the operating admin needs tenant scope | Confirm admin role assignment scope; reproduce as a tenant-scoped SharePoint Admin | Use a tenant-scoped admin; document the AU limitation in the runbook | Entra Global Admin + SharePoint Admin |
| F16 | Audit evidence of the RCD / RSS change cannot be produced for an examiner | Audit retention insufficient OR event-type filter incorrect OR the event was never written | Re-run UAL search with the documented event-type list; check retention setting per Control 1.7 | Extend retention; engage Microsoft Support if events are missing; document the gap in the Compliance file | Compliance Officer + Purview Compliance Admin |

---

## §3 — Anti-pattern catalog

| # | Anti-pattern | Why it is wrong / risk |
|---|---|---|
| A1 | Marking RCD as enforcing because it was set last week, without re-running the deterministic check today | Propagation, license absence (F3), or RSS conflict (F11) can leave the control no-op; control evidence becomes false PASS |
| A2 | Treating an empty `Get-SPOTenantRestrictedSearchAllowedList` as "RSS not in effect" | Silent-zero-row trap; confirm `Get-SPOTenant.EnableRestrictedSearchAllList` first |
| A3 | Blocking only the SharePoint connector via DLP-for-Copilot | F4 — makers add the site via direct URL in Copilot Studio knowledge sources; both enforcement vectors are required |
| A4 | Using Commercial portal URLs (e.g., `purview.microsoft.com`) on a `.us` (GCC High / DoD) tenant | Wrong scope; misleads the admin into believing a feature is missing when it is the wrong portal |
| A5 | Asserting RCD effectiveness without first verifying that any user has a Microsoft 365 Copilot license | F3 — RCD without Copilot is a no-op; admin gets a false PASS |
| A6 | Diagnosing "RCD did not work" without distinguishing Business Chat from in-app Copilot | F1 — RCD does not scope the open-document grounding inside Word / Excel / PowerPoint |
| A7 | Treating the DAG report as real-time | F5 — DAG cadence is delayed; check the report generation timestamp before declaring a real failure |
| A8 | Removing a low-traffic RSS allow-list entry without governance approval to make room for a new one | RSS allow-list is a regulated-scope decision (FINRA 3110 / RN 24-09 supervisory surface), not a housekeeping decision |
| A9 | Adding a Copilot Studio knowledge source pointing at a personal OneDrive | F6 — Zone leak; the agent inherits a personal-productivity grounding scope and exits the firm's controlled grounding plane |
| A10 | One-shot `Set-SPOSite ... -RestrictContentOrgWideSearch $true` against many sites with no retry / idempotence | F13 — partial failure leaves a half-protected estate that audits as PASS at the policy level |
| A11 | Operating RCD / RSS / DAG / DLP-for-Copilot in GCC High or DoD without documenting parity gaps | F9 — features fail silently with no portal warning; sovereign-cloud evidence pack is incomplete |
| A12 | Closing an incident before producing the audit-evidenced timeline of the RCD / RSS change | FINRA 4511 / SEC 17a-4(f) books-and-records integrity gap; examiner cannot reconstruct the change |
| A13 | Using `$variable -eq $null` instead of `$null -eq $variable` in PowerShell detection scripts | PowerShell idiom; comparison against a collection on the left side returns the filtered collection rather than `$true` / `$false` and produces silent false negatives |
| A14 | Treating Restricted SharePoint Search as a security boundary | RSS is a **scope** mechanism, not a security boundary. Recent-interaction, sharing, and ownership carve-outs are by design; permissions and DLP remain the security plane |
| A15 | Re-using a single RSS allow-list across sovereign and Commercial tenants without per-cloud verification | Capability and operational behavior differ per cloud; the same allow-list can produce different effective scope |

---

## §4 — Sovereign cloud matrix

The matrix below records the operating posture per cloud. **Microsoft cloud-feature parity changes; verify against the Microsoft Learn cloud-parity matrix at the time of operation.** Document the verification date in the evidence pack.

| Capability | Commercial | GCC | GCC High | DoD | Fallback when not at parity |
|---|---|---|---|---|---|
| RCD (`RestrictContentOrgWideSearch` per site) | Available | Verify | Verify per release | Verify per release | Manual site-scoping plus RSS allow-list curation; document exception in evidence pack |
| RSS (`EnableRestrictedSearchAllList` plus allow-list) | Available | Verify | Verify per release | Verify per release | Manual site-by-site scoping; agent-level knowledge-source allow-listing in Copilot Studio |
| SharePoint Advanced Management (SAM) features that RCD / RSS depend on | Available | Verify | Verify | Verify | Confirm SAM SKU availability for the cloud; if absent, RCD itself may be unavailable |
| Data Access Governance (DAG) reports | Available | Verify | Verify | Verify | Manual oversharing review via site-permission export; cross-reference Control 4.8 |
| Copilot Studio knowledge source on SharePoint Online | Available | Varies | Verify per release | Verify per release | Restrict to first-party connectors only; document in environment policy (Control 2.1) |
| Microsoft 365 Copilot (license SKU) | Available | Varies | Verify per release | Verify per release | If Copilot SKU unavailable for the cloud, RCD / RSS still configurable but a no-op until SKU lands; record as documented exception |
| DLP-for-Copilot location | Available | Verify | Verify | Verify | Tighten upstream DLP on SharePoint and OneDrive locations to compensate |
| Adaptive Protection / IRM signals into grounding-scope decisions | Available | Verify | Typically not available | Typically not available | Static scoping; periodic manual review per Control 1.6 cadence |

> Operating any of the above in GCC High or DoD without confirming current parity creates a silent-failure surface. Document the parity verification date and the operating posture in the evidence pack. Where a capability is unavailable, record the fallback explicitly so an examiner can reconstruct the firm's compensating posture.

---

## §5 — Escalation L1 → L4

> **Response windows below are firm-defined sample targets**, not Microsoft commitments. Microsoft does not publish per-incident SLAs for grounding-scope misconfiguration. Tune to your firm's IR runbook.

### L1 — SharePoint Admin (operational triage)

- Preserve evidence per §1.3 **before** any remediation.
- Run the §1.5 pre-escalation checklist (≥ 15 items).
- Apply §1.4 compensating controls; do not leave the gap open.
- For SEV-3 / SEV-4 issues, attempt resolution at L1 and document.
- Sample target: acknowledge SEV-1 / SEV-2 within 1 h; resolve SEV-3 within 1 business day (firm-defined).

### L2 — AI Governance Lead + Power Platform Admin + Purview Compliance Admin

- Triage cross-control impact: Controls 1.5 (DLP-for-Copilot), 1.6 (DSPM for AI), 1.7 (audit backbone), 2.1 (environment governance), 2.16 (agent lifecycle), 4.1 (sensitivity labels in SPO), 4.7 (Copilot data governance), 4.8 (item-level permission scanning).
- Inventory all Copilot Studio knowledge sources in the affected environment; quarantine any unsanctioned source.
- Confirm Zone classification register entries for the affected sites and agents (per Control 2.1).
- Coordinate with SharePoint Admin on RCD / RSS state and bulk remediation idempotency (F13).
- Sample target: SEV-1 within 1 h; SEV-2 within 4 h.

### L3 — CISO + Compliance Officer + General Counsel + Privacy Officer

- Reportability determination per the §1.2 decision tree. **Legal owns the determination.**
- **NY DFS 23 NYCRR 500 §500.17(a) 72-hour clock** evaluation — clock starts at **determination**, not first alert.
- **SEC Regulation S-P §248.30(a)(4)** customer-notification assessment if customer NPI is implicated.
- **FINRA Rule 4530** disclosure assessment if firm misconduct is implicated.
- Coordinate with HR on any insider-misconduct angle (Control 1.12 IRM cross-reference).
- Decide the regulator-notification path (FINRA / SEC / NY DFS / state AGs / OCC / Federal Reserve / CFTC / state-level) — Compliance and Legal own this decision, not Engineering.
- Sample target: SEV-1 within 1 h.

### L4 — Microsoft Support ticket

Open a Microsoft Support ticket only after L1, L2, and L3 are engaged. Use the §7 payload template. Attach the evidence pack reference (do not attach raw evidence to the ticket without a redaction review). For any artifact containing customer NPI / MNPI, share **out of band** under NDA.

### L5 — Internal Compliance / Legal / HR communication

Use the §7 internal communication template alongside the L4 Microsoft ticket. The internal communication is the official intake into the firm's compliance file and the basis for the regulator-notification posture.

---

## §6 — Detailed failure modes

For each failure mode below: symptom, likely cause, deterministic diagnostic (PowerShell / Graph / portal path), fix, verification, and Microsoft Learn references.

### F1 — RCD applied; content still surfaces in in-app Copilot

**Symptom.** A site is RCD-protected; users invoking **Business Chat** see no content from the site. Users invoking **Copilot inside Word / Excel / PowerPoint / Outlook** with a file from the site already open continue to see Copilot summarize / answer over that document.

**Likely cause.** Scope confusion. RCD scopes enterprise grounding (Business Chat / agent grounding). It does not prevent Copilot in an Office app from operating on the open document the user already has access to.

**Diagnostic.**
```powershell
# Confirm RCD state on the site
Get-SPOSite -Identity 'https://contoso.sharepoint.com/sites/legal-drafts' |
    Select Url, RestrictContentOrgWideSearch
# Reproduce in Business Chat with cache cleared; reproduce in-app Copilot in Word with the file open
# If only in-app reproduces, F1 is in scope
```

**Fix.** Educate users on the surface distinction. Apply sensitivity-label encryption to the document so in-app Copilot cannot operate on it (Microsoft documents that encryption is the enforcement plane for in-app open-document grounding). Tighten DLP-for-Copilot (Control 1.5) on the SIT / label.

**Verification.** Re-test in-app with an encrypted document from the site; Copilot should be blocked at the runtime DLP layer or by encryption.

**Learn.**
- https://learn.microsoft.com/sharepoint/restricted-content-discovery
- https://learn.microsoft.com/en-us/microsoft-365/copilot/microsoft-365-copilot-privacy
- https://learn.microsoft.com/en-us/purview/dlp-microsoft365-copilot-location-default-policy

---

### F2 — RSS allowed-list change not in effect

**Symptom.** A site was added to the RSS allow-list; users still report Copilot does not return content from it (or, after removal, users still see content from a removed site).

**Likely cause.** Index rebuild and propagation. **Verify the documented Microsoft Learn propagation window at the time of operation** (historically observed at 24–48 h; verify current).

**Diagnostic.**
```powershell
# Confirm RSS is enabled and the allow-list state
Get-SPOTenant | Select EnableRestrictedSearchAllList
Get-SPOTenantRestrictedSearchAllowedList
# Note the UTC time the change was made; compare to documented window
```

**Fix.** Wait the documented window and re-test before escalation. If a SEV-1 disclosure has occurred in the meantime, treat per §1.

**Verification.** Re-test from a clean Business Chat session after the documented window.

**Learn.**
- https://learn.microsoft.com/sharepoint/restricted-sharepoint-search

---

### F3 — RCD enabled but tenant has no Copilot license assigned (silent no-op)

**Symptom.** Admin asserts RCD is enforcing across the estate. Control evidence file shows PASS. In reality, **no user has a Microsoft 365 Copilot license assigned**, so Copilot is not grounding on anything regardless of RCD state.

**Likely cause.** Control evidence collected from configuration state only, not from the runtime / SKU plane.

**Diagnostic.**
```powershell
# Confirm Copilot SKU presence and consumption
Connect-MgGraph -Scopes 'Directory.Read.All'
Get-MgSubscribedSku |
    Where SkuPartNumber -like '*COPILOT*' |
    Select SkuPartNumber, ConsumedUnits, @{n='Total';e={$_.PrepaidUnits.Enabled}}
```

**Fix.** Either (a) assign at least one Copilot license to a non-production canary user and re-validate RCD effectiveness, or (b) document the no-op state explicitly in the control evidence pack — do **not** assert RCD effectiveness without at least one Copilot-licensed canary.

**Verification.** With a Copilot-licensed canary, attempt a Business Chat query expected to be blocked by RCD; confirm zero results / expected scope.

**Learn.**
- https://learn.microsoft.com/microsoft-365-copilot/microsoft-365-copilot-licensing
- https://learn.microsoft.com/sharepoint/restricted-content-discovery

---

### F4 — DLP blocks SharePoint connector; maker adds direct URL in Copilot Studio

**Symptom.** DLP-for-Copilot policy blocks the SharePoint connector for a sensitive label / SIT. A Copilot Studio agent still grounds on a site that should be blocked because the maker added the site as a **direct URL** knowledge source.

**Likely cause.** Connector-block ≠ URL-block. Two enforcement vectors are required.

**Diagnostic.**
```powershell
# Inventory Copilot Studio knowledge sources per environment via Power Platform Admin Center export
# Cross-check each URL against the sanctioned connector list and the DLP-allowed connector list
# In Power Platform Admin Center: Environments -> select environment -> Copilot Studio -> Knowledge sources
```

**Fix.** Block at both layers. Tighten the Copilot Studio environment policy (Control 2.1) to disallow direct-URL knowledge sources for in-scope environments. Add URL pattern blocks to DLP. Freeze publishes (Control 2.1) until the inventory is clean.

**Verification.** Attempt to publish an agent with a direct-URL knowledge source pointing at a blocked site; the publish should fail.

**Learn.**
- https://learn.microsoft.com/power-platform/admin/wp-data-loss-prevention
- https://learn.microsoft.com/microsoft-copilot-studio/security-and-governance
- https://learn.microsoft.com/en-us/purview/dlp-microsoft365-copilot-location-default-policy

> **Latency note.** DLP enforcement messaging in Copilot Studio has shown latency historically. Verify in-tenant by attempting the prohibited operation immediately after policy change and again after the documented Learn propagation window.

---

### F5 — DAG report shows oversharing on RCD-protected site

**Symptom.** DAG report flags a site as oversharing despite RCD being applied to it.

**Likely cause.** DAG cadence is delayed. The report may pre-date the RCD change. Alternative: RCD was rolled back (configuration drift).

**Diagnostic.**
```powershell
# Capture the DAG report's generation timestamp (visible in the report header / export metadata)
# Compare to the RCD change time on the site
Get-SPOSite -Identity 'https://contoso.sharepoint.com/sites/legal-drafts' |
    Select Url, RestrictContentOrgWideSearch
# Re-run DAG and compare
```

**Fix.** Re-run DAG. If the fresh report still shows oversharing, treat as a real RCD failure and follow the F1 / F11 / F4 path. If the fresh report is clean, the prior result was stale; document and close.

**Verification.** Two consecutive DAG runs after the RCD change show no oversharing.

**Learn.**
- https://learn.microsoft.com/sharepoint/data-access-governance-reports

---

### F6 — Personal OneDrive content in declarative agent

**Symptom.** A published Copilot Studio declarative agent surfaces content from a user's personal OneDrive in its responses.

**Likely cause.** Zone misconfiguration. Zone 1 personal-productivity content reached a Zone 2 / Zone 3 agent's knowledge source, by direct knowledge-source addition or by a connector-driven duplication path.

**Diagnostic.** Inventory each in-scope agent's knowledge sources. Flag any path under `https://<tenant>-my.sharepoint.com/personal/...` or any OneDrive URL.

**Fix.** Remove the OneDrive knowledge source. Suspend the agent (Control 2.16) until the publisher re-asserts a sanctioned knowledge-source posture. Update the Zone register (Control 2.1). Cross-reference Controls 4.7 and 1.5.

**Verification.** Re-test the agent; confirm no OneDrive citations.

**Learn.**
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-studio
- https://learn.microsoft.com/en-us/microsoft-365/copilot/microsoft-365-copilot-privacy

---

### F7 — RSS 100-site ceiling reached

**Symptom.** `Add-SPOTenantRestrictedSearchAllowedListSites` fails. Inventory shows 100 sites already on the allow-list.

**Likely cause.** The RSS allow-list ceiling has been reached. This is a **governance** event — at the ceiling, the firm has effectively converted Copilot grounding into a manually curated allow-list that requires a documented add / remove flow.

**Diagnostic.**
```powershell
$count = (Get-SPOTenantRestrictedSearchAllowedList).Count
"Current allowed sites: $count / 100"
```

**Fix.** Convene the RSS allow-list change-control board (AI Governance Lead + SharePoint Admin + Compliance Officer + business-line representative). For each candidate site, document the business case in the RSS change ledger. Removals require the same ledger entry and a justification. Do **not** "make room" by removing low-traffic entries without governance approval — that violates A8.

**Verification.** RSS change ledger shows a documented add / remove pair for any net-zero churn. New site is on the allow-list and the displaced site is documented.

**Learn.**
- https://learn.microsoft.com/sharepoint/restricted-sharepoint-search

---

### F8 — Copilot Studio knowledge source change not visible

**Symptom.** Maker adds, removes, or modifies a knowledge source in Copilot Studio; the change does not appear to take effect when an agent is invoked.

**Likely cause.** Sync / cache propagation. **Verify the current Microsoft Learn-stated sync window at the time of operation.**

**Diagnostic.** Note the change UTC. Re-test after the documented window.

**Fix.** Wait the documented window. Re-test. Do not escalate before the window elapses unless a SEV-1 disclosure has occurred.

**Verification.** Agent invocation reflects the new knowledge-source posture.

**Learn.**
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-studio

---

### F9 — Sovereign cloud parity gap

**Symptom.** A capability that operates in Commercial does not behave the same way (or is unavailable) in GCC, GCC High, or DoD.

**Likely cause.** Cloud-feature parity gap. Microsoft does not publish a single SLA for parity; capabilities land at different times in sovereign clouds.

**Diagnostic.** Re-confirm the capability against the Microsoft Learn cloud-parity matrix at the time of operation. Do not rely on cached parity assumptions older than the operating quarter.

**Fix.** Apply the §4 fallback for the affected capability. Document the parity verification date and the operating posture in the evidence pack.

**Verification.** Evidence pack contains the parity verification date, the cloud, and the fallback posture.

**Learn.**
- https://learn.microsoft.com/en-us/office365/servicedescriptions/office-365-platform-service-description/office-365-us-government/gcc-high-and-dod
- https://learn.microsoft.com/en-us/office365/servicedescriptions/office-365-platform-service-description/office-365-us-government/gcc-high-and-dod

---

### F10 — Modern indexed; classic ASPX not

**Symptom.** A site is RCD-protected and the modern pages are correctly excluded from grounding; classic ASPX page content from the same site continues to surface.

**Likely cause.** Modern and classic pages flow through different indexing paths. The site appears RCD-protected but classic content can reach grounding via a different code path.

**Diagnostic.** Enumerate the site's page library and classify modern vs classic.

**Fix.** Convert classic pages to modern, OR explicitly scope classic page content out via permissions / archive, OR remove classic page content from the site.

**Verification.** Re-test grounding from a non-privileged user; classic content no longer appears.

**Learn.**
- https://learn.microsoft.com/en-us/sharepoint/dev/transform/modernize-classic-sites
- https://learn.microsoft.com/sharepoint/restricted-content-discovery

---

### F11 — Site is on RSS allow-list AND has RCD = `True`

**Symptom.** A site appears on the RSS allow-list but returns no content (or appears to return content despite RCD = `True`). Conflicting scopes.

**Likely cause.** RCD and RSS are evaluating against the same site with conflicting intent.

**Diagnostic.**
```powershell
$allowList = Get-SPOTenantRestrictedSearchAllowedList
$site = 'https://contoso.sharepoint.com/sites/legal-drafts'
"$site on RSS allow-list: $($allowList -contains $site)"
Get-SPOSite -Identity $site | Select Url, RestrictContentOrgWideSearch
```

**Fix.** Decide the intended state. Remove the site from one of the two scopes. Document the decision in the RSS change log and the RCD evidence pack so an examiner can reconstruct the intent.

**Verification.** After remediation, the site appears in exactly one of (RSS allow-list, RCD-protected) and Business Chat behavior matches the intent.

**Learn.**
- https://learn.microsoft.com/sharepoint/restricted-content-discovery
- https://learn.microsoft.com/sharepoint/restricted-sharepoint-search

---

### F12 — Property bag value not persisting

**Symptom.** PnP-based property-bag writes (e.g., `CopilotReady = True`) do not persist on the site.

**Likely cause.** PnP module stale; site read-only / archive; site-collection admin missing on the operating account.

**Diagnostic.**
```powershell
Update-Module -Name PnP.PowerShell
Get-SPOSite -Identity $siteUrl | Select Url, LockState, Status
# Add SCA if missing
Set-SPOUser -Site $siteUrl -LoginName <admin-upn> -IsSiteCollectionAdmin $true
```

**Fix.** Update PnP. Resolve site state (unlock, restore from archive). Re-add SCA. Retry idempotently.

**Verification.** `Get-PnPPropertyBag` returns the expected value after re-connect.

**Learn.**
- https://learn.microsoft.com/powershell/sharepoint/sharepoint-pnp/sharepoint-pnp-cmdlets

---

### F13 — Bulk `Set-SPOSite` partial failure

**Symptom.** A bulk operation to apply RCD across many sites reports success in the orchestrator log but spot-checks reveal that some sites did not receive the change. Audits at the policy level show PASS while a subset of sites is unprotected.

**Likely cause.** Throttling, locked sites, archived sites, or transient errors in a one-shot loop with no retry.

**Diagnostic.**
```powershell
# After the bulk run, re-query every site individually and produce a PASS / FAIL report
$sites = Get-SPOSite -Limit All
$report = $sites | ForEach-Object {
    [pscustomobject]@{
        Url = $_.Url
        RCD = $_.RestrictContentOrgWideSearch
        LockState = $_.LockState
        Status = $_.Status
    }
}
$report | Where { -not $_.RCD } | Export-Csv -Path .\rcd-misses.csv -NoTypeInformation
```

**Fix.** Implement an idempotent retry pattern with exponential backoff and per-site try / catch. Re-apply RCD to the failures individually. Do not declare the bulk operation complete until the per-site verification report is clean.

**Verification.** Per-site verification report shows zero misses across the in-scope estate.

**Learn.**
- https://learn.microsoft.com/sharepoint/restricted-content-discovery
- https://learn.microsoft.com/powershell/sharepoint/sharepoint-online/connect-sharepoint-online

---

### F14 — Guest / external user inherits broader grounding than internal users

**Symptom.** A B2B guest user appears to surface content via Copilot grounding that internal users do not see, OR a guest sees content they should not.

**Likely cause.** RCD does not change SharePoint permissions. The guest's effective permissions are the security plane; grounding inherits from permissions.

**Diagnostic.** Audit the guest's effective SharePoint permissions on the affected sites. Cross-reference Control 4.4 external sharing posture and Control 4.8 item-level permission scanning.

**Fix.** Tighten SharePoint sharing posture. Re-evaluate the guest access model. Do not treat as an RCD failure unless permissions are correct and grounding still leaks.

**Verification.** With permissions corrected, the guest's grounding matches the intended scope.

**Learn.**
- https://learn.microsoft.com/sharepoint/external-sharing-overview

---

### F15 — Restricted Administrative Unit admin attempting RCD / RSS change

**Symptom.** An admin assigned to an Administrative Unit (AU) cannot complete an RCD / RSS change and receives an unexpected error or no-op.

**Likely cause.** Some SharePoint admin surfaces do not honor AU scoping. The operation requires a tenant-scoped admin role.

**Diagnostic.** Confirm the operating admin's role assignment scope (AU vs tenant). Reproduce the operation as a tenant-scoped SharePoint Admin.

**Fix.** Use a tenant-scoped admin for RCD / RSS operations. Document the AU limitation in the runbook so it is not re-discovered each time.

**Verification.** Operation completes as tenant-scoped admin.

**Learn.**
- https://learn.microsoft.com/entra/identity/role-based-access-control/administrative-units

---

### F16 — Audit evidence of RCD / RSS change cannot be produced for examiner

**Symptom.** During an examination or internal audit, the RCD / RSS change history for a site cannot be produced from the Unified Audit Log.

**Likely cause.** Audit retention insufficient for the period in question; OR the wrong event-type filter was used; OR the event was never written (a sovereign-cloud or licensing parity gap can mute certain admin-event categories).

**Diagnostic.** Re-run the UAL search with the documented event-type list current at the time of the change. Check the audit retention setting per Control 1.7. Verify the audit log was enabled at the time of the change.

**Fix.** Extend retention going forward (Control 1.7). Engage Microsoft Support if events are confirmed missing. Document the gap explicitly in the Compliance file; the gap itself is a books-and-records integrity concern under FINRA 4511 / SEC 17a-4(f).

**Verification.** The change history for the site is reproducible from UAL within the retention window.

**Learn.**
- https://learn.microsoft.com/purview/audit-solutions-overview
- https://learn.microsoft.com/purview/audit-log-retention-policies

---

## §7 — Microsoft Support escalation payload + internal Compliance / Legal communication template

### 7.1 Microsoft Support ticket payload (paste verbatim; fill bracketed fields)

```
Severity: [SEV-1 | SEV-2 | SEV-3]
Tenant ID: [GUID]
Cloud: [Commercial | GCC | GCC High | DoD]
Affected workload: Microsoft 365 Copilot grounding scope (RCD / RSS / Copilot Studio knowledge source / DLP-for-Copilot)
Affected feature: [RCD | RSS | SharePoint Advanced Management | DAG | Copilot Studio knowledge source | DLP-for-Copilot | combination]
Affected scope:
  - Site URL(s): [list]
  - Copilot Studio environment(s): [list]
  - Agent(s): [list]
  - User population: [count and characterization, e.g., "1 confirmed disclosure, 200 potentially in scope based on RSS allow-list"]
  - UTC window start - end: [YYYY-MM-DDTHH:MM:SSZ - YYYY-MM-DDTHH:MM:SSZ]
Symptom (one line):
  [e.g., "RCD applied to /sites/legal-drafts on 2026-04-10T14:00Z; site not on RSS allow-list; Business Chat returned a citation from the site to a non-privileged user on 2026-04-17T11:32Z; in-app vs Business Chat surface confirmed (Business Chat); no RCD rollback in audit log; pre-escalation checklist items 1-19 pass."]
Pre-escalation checklist: items 1-19 confirmed PASS (per §1.5 of internal playbook).
Business impact:
  Confirmed / suspected disclosure of [supervisory record | draft regulatory filing | customer NPI | MNPI]; potential FINRA Rule 3110 / 4511 (with RN 24-09 for AI supervisory guidance) supervisory and books-and-records exposure; NY DFS 23 NYCRR 500 §500.17(a) 72-hour determination clock evaluation: [pending Legal | not applicable | clock running since UTC X]; SEC Reg S-P §248.30(a)(4) customer-notification assessment: [pending Legal | not applicable | active]; firm is in [active examination | quarter-end | none].
RCD / RSS state dump:
  Get-SPOSite output: [attached / inline]
  Get-SPOTenant search/Copilot fields: [attached / inline]
  Get-SPOTenantRestrictedSearchAllowedList: [attached, row count, SHA-256]
  Get-MgSubscribedSku Copilot SKU: [attached]
Copilot Studio knowledge-source inventory: [attached per environment]
Audit-log export: [paginated CSV/JSON, SHA-256 sidecar; DO NOT attach raw NPI; share out of band under NDA]
Evidence pack reference: [internal evidence ID; storage location; offer to share artifacts under NDA]
Steps already taken:
  - Pre-escalation checklist items 1-19 confirmed
  - Compensating controls in place: DLP-for-Copilot tightened to Block on [SIT/label] (Control 1.5); Copilot Studio publish freeze in environment [name] (Control 2.1); offending agent suspended (Control 2.16); daily UAL searches running for affected user set (Control 1.7); Communication Compliance review cadence increased on AI-assisted content (Control 1.10)
Engineer of record: [name, role, email, phone, time zone]
Compliance contact: [name, role, email]
Privacy contact (if NPI in scope): [name, role, email]
```

### 7.2 Internal Compliance / Legal / HR / Privacy communication template

```
To: Compliance Officer; General Counsel; Privacy Officer; CISO; (HR if insider misconduct in scope)
From: [AI Governance Lead]
Severity: [SEV-1 | SEV-2]
Subject: Microsoft 365 Copilot grounding-scope event — [date]

1. What happened
   - [Plain-language description, no jargon]
   - Affected site(s): [list]
   - Affected agent(s) / environment(s): [list]
   - Affected user population: [N users; characterize: registered representatives, RIA staff, external guests, etc.]
   - Surface: [Business Chat | in-app Copilot | Copilot Studio agent | combination]
   - UTC window: [start - end]
   - Confirmed disclosure: [yes / no / under investigation]
   - Content category at risk: [customer NPI | MNPI | supervisory record | draft regulatory filing | restricted-list / watch-list | other]

2. Possible regulatory exposure (§1.2 reportability triage; Legal owns determination)
   - FINRA Rule 3110 supervisory system: [yes / unclear / no]
   - FINRA RN 24-09 / Rule 3110 AI / agent supervision
   - FINRA Rule 4511 / SEC 17a-4(f) books-and-records integrity: [yes / unclear / no]
   - GLBA 501(b) / SEC Reg S-P §248.30(a)(4): [if customer NPI in scope; 30-day customer-notification timeline]
   - SOX §302 / §404 ICFR: [if financial-disclosure-adjacent]
   - NY DFS 23 NYCRR 500 §500.17(a) 72-hour cybersecurity-event clock: [pending Legal | not applicable | clock running since UTC X]
   - OCC 2026-13 (formerly OCC 2011-12) / Fed SR 26-2 (formerly SR 11-7) model risk: [if the agent surface itself produced a model-risk-adjacent failure]
   - CFTC Rule 1.31: [if covered swap / trading content]
   - FINRA Rule 4530: [if firm misconduct in scope]

3. Evidence preserved (per §1.3)
   - Site state dumps, tenant state, RSS allow-list export, Copilot SKU inventory, Copilot Studio knowledge-source inventory, paginated UAL export with SHA-256 sidecars, DAG report with generation timestamp, DLP-for-Copilot policy snapshot, Zone register entries, page composition snapshot, parity verification date for sovereign cloud
   - Stored in Control 1.7 evidence bucket reference [ID]

4. Compensating controls in place (per §1.4)
   - DLP-for-Copilot tightened to Block on [SIT/label] (Control 1.5)
   - Copilot Studio publish freeze in environment [name] (Control 2.1)
   - Offending agent suspended (Control 2.16)
   - Daily UAL searches running for affected user set (Control 1.7)
   - Communication Compliance review cadence increased (Control 1.10)
   - eDiscovery hold engaged where litigation / examination is foreseeable (Control 1.13 / 1.14)

5. Open questions for Compliance / Legal / Privacy / HR
   - Reportability determination per §1.2 tree
   - NY DFS 72-hour determination
   - Customer-notification timeline if customer NPI in scope (SEC Reg S-P)
   - Examiner-disclosure obligation if firm is in active examination
   - HR coordination if insider-misconduct angle exists
   - Privacy register update for any pseudonymization / re-identification performed during the incident

6. Next status update: [UTC]
```

---

## §8 — Cross-references

- [Control 4.6 — Grounding Scope Governance](../../../controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md) (parent control)
- [Control 4.6 portal walkthrough](portal-walkthrough.md)
- [Control 4.6 PowerShell setup](powershell-setup.md)
- [Control 4.6 verification & testing](verification-testing.md)
- [Control 4.7 — Microsoft 365 Copilot data governance — troubleshooting](../4.7/troubleshooting.md) (companion control on the SharePoint pillar)
- [Control 4.8 — Item-level permission scanning of agent knowledge sources — troubleshooting](../4.8/troubleshooting.md) (detects oversharing that grounding inherits)
- [Control 4.1 — SharePoint sensitivity label deployment — troubleshooting](../4.1/troubleshooting.md)
- [Control 1.5 — DLP for Microsoft 365 Copilot — troubleshooting](../1.5/troubleshooting.md) (runtime block at the Copilot location)
- [Control 1.6 — DSPM for AI — troubleshooting](../1.6/troubleshooting.md) (detection plane for AI data exposure)
- [Control 1.7 — Audit log backbone — troubleshooting](../1.7/troubleshooting.md) (books-and-records evidence backbone)
- [Control 2.1 — Power Platform environment governance — troubleshooting](../2.1/troubleshooting.md) (publish freeze; environment policy for Copilot Studio)
- [Control 2.16 — Agent lifecycle and suspension — troubleshooting](../2.16/troubleshooting.md) (suspend offending agents during incident)
- [AI incident response playbook](../../incident-and-risk/ai-incident-response-playbook.md)
- [Role catalog](../../../reference/role-catalog.md) (canonical role names used throughout)

External (verify URL currency at time of operation):
- https://learn.microsoft.com/sharepoint/restricted-content-discovery
- https://learn.microsoft.com/sharepoint/restricted-sharepoint-search
- https://learn.microsoft.com/sharepoint/advanced-management
- https://learn.microsoft.com/sharepoint/data-access-governance-reports
- https://learn.microsoft.com/en-us/microsoft-365/copilot/microsoft-365-copilot-privacy
- https://learn.microsoft.com/microsoft-365-copilot/microsoft-365-copilot-licensing
- https://learn.microsoft.com/en-us/purview/dlp-microsoft365-copilot-location-default-policy
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-studio
- https://learn.microsoft.com/microsoft-copilot-studio/security-and-governance
- https://learn.microsoft.com/power-platform/admin/wp-data-loss-prevention
- https://learn.microsoft.com/purview/audit-solutions-overview
- https://learn.microsoft.com/purview/audit-log-retention-policies

---

[Back to Control 4.6](../../../controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification & Testing](verification-testing.md)

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
