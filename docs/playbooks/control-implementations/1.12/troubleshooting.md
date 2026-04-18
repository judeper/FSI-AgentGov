# Control 1.12 — Troubleshooting: Insider Risk Management

**Control:** [1.12 Insider Risk Detection and Response](../../../controls/pillar-1-security/1.12-insider-risk-detection-and-response.md)
**Audience:** Microsoft 365 administrator at a US financial services organization, typically under audit pressure or active incident response.
**Sovereign clouds covered:** Commercial, GCC, GCC High, DoD (parity gaps called out inline).
**Last UI Verified:** April 2026

---

## §1 — FSI Incident Handling — READ FIRST

Microsoft Purview Insider Risk Management (IRM) is the **user-behavior risk plane** for the M365 estate and (via browser extensions) selected non-Microsoft AI / SaaS surfaces. For an FSI organization it is a **detective control feeding the supervisory program** under FINRA Rule 3110(b), a **safeguards-monitoring component** under GLBA 501(b), and a **model-driven detection system** subject to model risk governance under OCC Bulletin 2011-12 / Fed SR 11-7. IRM is **not** a books-and-records system: alerts, cases, and Forensic Evidence clips are working investigative artifacts. **Forensic Evidence clips auto-delete 120 days after capture unless exported.** Treat any change to a policy, role-group membership, priority user/content list, pseudonymization setting, or Forensic Evidence approver list as an **evidence-bearing event**: preserve **before** you remediate.

> **Critical Learn-verified constraints.** (1) Insider Risk Management — and **Adaptive Protection** in particular — has **limited / lagging availability in US Government clouds (GCC, GCC High, DoD)**; verify the per-cloud feature matrix on Microsoft Learn before promising coverage. (2) The **Risky Agents** template is **applied by default** when IRM is configured — it is not selected through the Create policy wizard; verify behavior on Learn at the time of writing. (3) **Forensic Evidence** is **off by default**, requires a **separate paired policy**, **dual authorization** (Investigator submits, Approver approves), Windows 10/11 Enterprise with the Microsoft Purview Client, **PAYG billing**, and clips **auto-delete at 120 days**. (4) IRM cases are **not WORM** and are **not** an SEC 17a-4 retention substrate; promote evidence to retention labels / Records Management (Control 1.9) or eDiscovery (Premium) hold (Control 1.13/1.14) before clip expiry or case closure.

### Severity matrix (Zone-aware, firm-defined response windows)

> Microsoft Learn does **not** publish IRM investigation or alert-response SLAs. The response windows below are **firm-defined supervisory commitments** — align them with the firm's WSP and FINRA 3110 supervisory expectations. Do not represent them to a regulator as Microsoft-stated ceilings.

| Severity | Trigger (IRM-specific) | Response window (firm-defined) | Escalation |
|---|---|---|---|
| **SEV-1** | An IRM policy covering a Zone 3 population (FINRA-supervised registered representatives, RIA staff, trading desk, MNPI-handlers, agent admins) is **off, deleted, mis-scoped, or producing zero alerts** during a window where seed/test activity is known to have occurred; the **Risky Agents** default policy is missing or scoped to zero users; HR connector last-success > 24 h while a known leaver's `LastWorkingDate` is within the policy lookback window; Forensic Evidence captures are running **without** dual-auth or **without** state-law notice; pseudonymization was disabled tenant-wide; Unified Audit Log is **off** (silent-zero-row trap); a Forensic Evidence approver group is empty (zero-approver state); priority user group includes the entire tenant ("everyone is priority" defeats focused review) | Immediate | CISO + Compliance + Legal + HR + Privacy within 1 h; NYDFS 23 NYCRR 500 §500.17(a) **72-hour cybersecurity-event clock** evaluated by Legal |
| **SEV-2** | Coverage gap on a Zone 2 population (single business unit excluded from a Risky AI usage policy; browser extension missing from an OS class; non-Windows population excluded silently); HR connector field-mapping drift (e.g., `ResignationDate` populated but `LastWorkingDate` blank → departing-user template silently quiet); Adaptive Protection threshold no longer triggering after a baseline shift; classifier / ML model bump invalidated the prior week's alert baseline; Auditor role group empty (no independent assurance trail for unmask events); Investigator role group also assigned as Approver (separation-of-duties violation for Forensic Evidence) | 4 h | IRM Admin → AI Governance / Insider Risk Lead within 4 h; Compliance notified |
| **SEV-3** | Single-user / single-channel coverage gap; Forensic Evidence storage cap approaching; analytics scan stalled past the documented 48 h window; Triage Agent unavailable (capacity / Preview→GA churn); Defender for Cloud Apps connector for a single SaaS source delayed; case-to-eDiscovery escalation failing for a single case | 1 business day | IRM Admin |
| **SEV-4** | Cosmetic UI drift; tooltip / column-order changes; preview-feature regression that does not affect coverage, evidence, or reviewer access | Best effort | Track in known-issues log |

**Zone-aware reading.** Severity is interpreted against the in-scope user population. The same configuration error is SEV-1 against a Zone 3 broker-dealer population and SEV-3 against a Zone 1 administrator pilot. Always classify by the **regulatory exposure of the affected users**, not by the technical defect.

### Reportability decision tree

> This is an **escalation aid**, not a legal determination. Reportability is decided by Compliance and Legal. Use the matrix to surface the right question to the right desk **inside the response window** — do not self-decide.

| Trigger | Escalate to | Possible obligation (verify with counsel) |
|---|---|---|
| Loss of insider-risk visibility on Zone 3 FINRA-supervised population (policy off, mis-scoped, or zero-alert with seed activity present) | Compliance | **FINRA Rule 3110(b)** supervisory system — documented procedures must be followed; **FINRA Notice 25-07** firm reminders on AI/agent supervision (re-states existing 3110/4511 obligations; do not over-cite as standalone authority) |
| Books-and-records gap — IRM artifacts treated as records and lost (cases closed, clips expired at 120 d, alerts deleted) | Compliance + Legal | **FINRA Rule 4511(a)/(b)** make-and-preserve; **SEC Rule 17a-3** required records; **SEC Rule 17a-4(b)(4)** non-rewriteable / non-erasable retention. **IRM is not the retention plane** — the gap is in the records pipeline (Control 1.9), not in IRM itself |
| Customer NPI / PII surfaced via insider exfiltration alert and not contained | Privacy + Legal | **GLBA 501(b)** safeguards; **SEC Reg S-P §248.30** customer-notification timeline (post-2024 amendments); state breach-notification statutes |
| Cybersecurity event determination — reasonable likelihood of material harm to normal operations | CISO + Legal | **NYDFS 23 NYCRR 500 §500.17(a)** — **72-hour** notice to Department after determination; the clock starts at **determination**, not at first alert |
| Internal control over financial reporting impacted (insider activity touches financial-disclosure data, treasury, close process) | Compliance + Internal Audit | **SOX §302 / §404** ICFR — insider-risk monitoring is referenced in the firm's control inventory |
| Model-risk event — IRM ML risk scoring or the Triage Agent produced demonstrably wrong prioritization that affected an outcome | Model Risk + Compliance | **OCC Bulletin 2011-12** / **Fed SR 11-7** model risk management; AI Triage Agent and ML risk scoring are model-driven and belong in the model inventory (Control 2.6) |
| Records-related event for a covered swap / trading-related insider activity | Compliance | **CFTC Rule 1.31** recordkeeping (full, complete, original; retention period; production timeline) |
| Insider misconduct surfaced through IRM alert (suspected fraud, theft, market manipulation, harassment) | HR + Legal + Compliance | **FINRA Rule 4530** reporting; firm code-of-conduct procedures; coordinate Forensic Evidence preservation with Legal **before** notifying the subject |
| Forensic Evidence captured for a user resident in / employed in a state with employee-monitoring notice statutes (CT, DE, NY) | Privacy + Legal + HR | State employee-monitoring notice law; coordinate notice posture **before** capture; document in the privacy register |
| Pseudonymized usernames re-identified by an investigator | Privacy + Compliance | Privacy-by-design defeat; the unmask must have a logged investigation reason; the IRM Auditor reviews the unmask audit row |

### Evidence preservation **before** remediation

A common audit finding in FSI is _"the policy was modified before the failing-state evidence was captured, and the firm cannot reconstruct what insider-risk coverage was in effect during the relevant period."_ Do not be that finding. Capture the following artifacts **before** disabling, editing, re-scoping, replacing approvers, or unmasking pseudonymized identities:

1. **Policy snapshot.** Purview portal: Solutions > Insider Risk Management > **Policies** > [policy] — capture the policy template, scope (user groups, AUs), conditions, indicators, threshold profile, status (Test mode vs On), and last-modified-by/UTC. The **Risky Agents** default policy must also be snapshotted (it is not visible through the Create policy wizard but is visible in the Policies list).
2. **Alert and case state snapshot.** Alerts queue (filter by policy, severity, status); Cases queue (status, assignee, last activity); per-alert risk-score breakdown (sequence vs cumulative; weighted indicators that contributed). Export to CSV where the portal supports it; otherwise, full-page screenshots with timestamp and identity visible.
3. **Investigation notes export.** For any active case, export the investigation notes / activity timeline / data-risk graph view; investigator notes are part of the supervisory record (FINRA 3110).
4. **Forensic Evidence clip inventory.** Clip list with capture UTC, capture trigger, requesting Investigator, approving Approver, retention countdown to **120-day auto-delete**. If any clip is within 30 days of expiry and may be needed beyond 120 d, **export to a defensible long-term store before remediation begins** (Records Management retention label per Control 1.9, or eDiscovery (Premium) hold per Control 1.13/1.14).
5. **Role-group snapshot** for: `Insider Risk Management`, `Insider Risk Management Admins`, `Insider Risk Management Analysts`, `Insider Risk Management Investigators`, `Insider Risk Management Auditors`, `Insider Risk Management Approvers`. Capture membership, AU restriction state, and effective permissions at UTC of capture. Confirm Approvers are **distinct** from Investigators (separation-of-duties for Forensic Evidence dual-auth).
6. **Priority user group snapshot** and **priority content list snapshot** — both are inputs to IRM scoring; a quiet change to either can shift alert volume materially.
7. **Pseudonymization state.** Settings > Privacy. Capture the pseudonymization toggle state, the identity that last toggled it, and any active "show usernames" session. **Capture before any re-identification action** — re-identification under investigation is logged; making the snapshot pre-unmask preserves the privacy-by-default baseline.
8. **HR connector last-success.** Microsoft Purview > Data connectors > HR connector — last-success UTC, ingestion row count, schema, field mapping for `EmployeeID` / `ResignationDate` / `LastWorkingDate` / `EmploymentStatus`. Reference: Microsoft Learn `import-hr-data`.
9. **Browser extension / Edge config policy state.** Intune (or equivalent MDM) configuration profile state for the Microsoft Insider risk extension (Edge) and Microsoft Purview extension (Chrome); device coverage report; per-OS coverage. Non-Windows devices are **not supported** — record that gap explicitly so the auditor sees you knew about it.
10. **Device onboarding state.** Devices onboarded to Microsoft Purview (the population that can produce endpoint signals and Forensic Evidence captures); cross-reference against the policy's user scope.
11. **Audit-search export** for the suspect window from a `Connect-ExchangeOnline` session — `Search-UnifiedAuditLog` filtered for IRM admin actions and unmask events. **Verify the record-type names and operation names against the current Microsoft Learn `audit-log-activities` reference**; do not assume names from prior playbooks. Paginate; cap **50,000** rows per session; rotate `SessionId` and use `SessionCommand ReturnLargeSet` for large windows. Preserve raw JSON output before any post-processing.
12. **Defender for Cloud Apps connector health** for any cloud-app SaaS source feeding IRM (Box, Dropbox, Google Drive, Amazon S3, Azure) — last-sync UTC, error state.
13. **Defender for Endpoint integration state** — required for Security policy violations templates; without MDE, the template silently produces no signal.
14. **Sovereign-cloud parity confirmation** — record cloud (Commercial / GCC / GCC High / DoD) and verify against current Microsoft Learn matrix that the in-scope IRM features (Risky AI usage, Risky Agents, Adaptive Protection, Forensic Evidence, Triage Agent) were available in that cloud at the time of the suspect window.
15. **PAYG billing state** for Forensic Evidence and any other PAYG-dependent capability.
16. **Tenant ID, cloud, affected user/policy/case list, UTC window, role used, identity that performed the failing-state observation, browser, sign-in method.**
17. **SHA-256 manifest sidecar** covering every artifact above; store in the Control 1.7 evidence bucket with WORM retention (Control 1.9 Records Retention and Immutability).

Only after the evidence pack is sealed and hashed should the policy be modified, the case re-assigned, or pseudonymization toggled. The remediation itself becomes a new evidence item — capture the post-remediation state with the same rigor.

### Compensating controls during an IRM degradation

Apply one or more while IRM is degraded; document the compensating control in the incident ticket. Do not leave the detection gap open:

- **Tighten Communication Compliance review cadence** (Control 1.10) — temporarily increase review percentage on the in-scope Copilot / conduct-content templates to surface insider-conduct signal that would otherwise have flowed to IRM. CC is supervisory review of conduct content; IRM is user-behavioral risk — overlapping but not equivalent.
- **Daily Unified Audit Log searches** (Control 1.7 / Audit Premium) for `CopilotInteraction`, file-access bursts, OneDrive sync, SharePoint downloads, USB device events (where surfaced), and external email patterns for the affected user population. UAL is the durable evidence backbone; IRM is the scoring layer on top of it.
- **Tighten DLP-for-Copilot block actions** (Control 1.5) — temporarily move Block-by-label rules from `TestWithNotifications` to `Enable` for high-risk content categories (NPI, MNPI, regulated keywords). DLP is preventive at egress; IRM is detective on user behavior. They are complementary.
- **Run targeted DSPM-for-AI hunts** (Control 1.6) for grounding-data exposure during the IRM degradation window — DSPM surfaces overshared SharePoint / OneDrive content that could be the upstream of an exfiltration that IRM would have scored.
- **Defender for Cloud Apps anomaly detection hunts** — Cloud App Security UEBA produces independent anomaly signals (mass download, impossible travel, unusual SaaS activity) that overlap IRM's behavioral scope.
- **Microsoft Sentinel UEBA / hunting queries** where deployed — Sentinel UEBA produces an independent peer-baseline view; cross-correlate with surviving IRM signals where available.
- **Manual HR notification flow for departures** — if the HR connector is degraded, invoke the firm's documented manual departure notification (HR → IRM Admin → Compliance) for known leavers within the lookback window. Document the manual notifications in the incident ticket.
- **Freeze of new Zone 3 agent activations** (Controls 2.1, 2.16) — do not expand the agent surface during an insider-risk detection degradation; freeze new Copilot Studio publish actions and new Zone 3 agent registrations until IRM coverage is restored.
- **Manual Forensic Evidence substitute** — for a known high-risk subject during an IRM Forensic Evidence outage, work with Legal to invoke a documented manual evidence-collection procedure (e.g., MDE live response, eDiscovery (Premium) collection on the user's mailbox/OneDrive). Do **not** improvise endpoint-recording mechanisms outside documented procedure.

### Pre-escalation checklist (≥ 12 items)

1. [ ] **Tenant ID and cloud** confirmed (Commercial / GCC / GCC High / DoD)
2. [ ] **IRM SKU verified** — Microsoft 365 E5, E5 Compliance, Insider Risk Management standalone, or Microsoft Purview Suite (per-user); PAYG enabled where required (notably Forensic Evidence). Verify on Microsoft Learn at deployment time
3. [ ] **Unified Audit Log on** — `Get-AdminAuditLogConfig` from a `Connect-ExchangeOnline` session shows `UnifiedAuditLogIngestionEnabled : True`. UAL off is the **most common silent-failure mode** in IRM
4. [ ] **HR connector last-success ≤ 24 h**; field mapping for `EmployeeID`, `ResignationDate`, `LastWorkingDate`, `EmploymentStatus` verified against the source HRIS schema; CSV row count plausible vs. expected workforce; reference: Learn `import-hr-data`
5. [ ] **Audit ingestion confirmed** for IRM admin actions (verify operation names against current Learn `audit-log-activities`)
6. [ ] **Analytics enabled** with **≥ 7-day baseline** for ML-driven scoring. Learn states analytics scans may take **up to 48 h** to complete; do not conclude "no signal" inside that window
7. [ ] **Pseudonymization state captured before any re-identification** — investigator unmask actions are logged; the auditor must be able to see what the baseline was before the unmask
8. [ ] **Forensic Evidence dual-auth approver list** non-empty and **distinct from Investigators**; state-law notice posture (CT / DE / NY) confirmed with Privacy + Legal before any new capture
9. [ ] **Browser extension / Edge config policy state** — Microsoft Insider risk extension (Edge) and Microsoft Purview extension (Chrome) deployed via Intune to the in-scope Windows population; non-Windows excluded explicitly with documented gap
10. [ ] **Device onboarding state** — devices onboarded to Microsoft Purview cover the in-scope user population; coverage gap documented
11. [ ] **Priority user group membership snapshot** captured (membership at incident UTC); group is **role-based**, not "everyone" — see §3 anti-pattern 11
12. [ ] **Priority content list snapshot** captured (SharePoint sites / sensitive-info types) — material to scoring
13. [ ] **Administrative units exclusion check** — restricted-AU admins/investigators see only their scoped users; an investigator opening the page from the wrong AU may see "no alerts" while alerts exist for an unrestricted admin
14. [ ] **Sovereign-cloud parity row consulted** for every in-scope feature (Risky AI usage, Risky Agents, Adaptive Protection, Forensic Evidence, Triage Agent); GCC / GCC High / DoD lag Commercial — record gaps
15. [ ] **Compliance + Legal + HR notified** per severity matrix; Privacy notified for any pseudonymization-related, NPI-related, or Forensic-Evidence-related event; **NYDFS 72-hour determination** evaluated by Legal where the event meets cybersecurity-event definition
16. [ ] **Evidence preserved** per the §1 evidence list; SHA-256 sidecars captured; manifest stored in Control 1.7 evidence bucket

---

## §2 — Decision matrix: IRM vs Communication Compliance vs eDiscovery vs DLP vs Sentinel

The single most common cause of misdirected investigation in FSI is reaching for the wrong Purview / Defender / Sentinel solution. Use this matrix to route a symptom to the **correct** control before you start configuring anything.

| Symptom / question | Use **DLP (1.5)** | Use **DSPM for AI (1.6)** | Use **CC (1.10)** | Use **IRM (1.12)** | Use **eDiscovery (1.13/1.14)** | Use **Sentinel UEBA** |
|---|---|---|---|---|---|---|
| Where is the **prompt content** (the actual text the user sent to Copilot)? | ❌ DLP sees egress against rules; not content of record | ✅ DSPM surfaces interaction activity, sensitive-info hits, and content lineage | ✅ CC review surface for the conduct content of the prompt | ❌ IRM scores the **behavior**; it does not store the prompt body for review | ⚠️ Discoverable via Copilot interaction record search; not the routine review surface | ❌ |
| Where is the **books-and-records event proof** that the interaction happened? | ❌ | ⚠️ DSPM activity view, not records | ⚠️ CC review record exists while policy is in place; not WORM | ❌ — IRM cases are **not** WORM and **not** an SEC 17a-4 substrate | ✅ eDiscovery (Premium) collection of the underlying audit record + retention label per Control 1.9 | ❌ |
| Where is **real-time blocking** of risky AI usage at egress? | ✅ DLP-for-Copilot (Block / Block with override / Audit) | ❌ | ❌ | ⚠️ Adaptive Protection can dynamically tighten DLP / DLM / Conditional Access — but only where Adaptive Protection is **available in the cloud** (Commercial; GCC/GCC High/DoD lag) | ❌ | ❌ |
| Where is **cross-signal UEBA** (peer baseline, impossible travel, mass download)? | ❌ | ❌ | ❌ | ⚠️ IRM scores M365-centric behavior (with browser / cloud-app extensions); peer-baseline is firm-narrow | ❌ | ✅ Sentinel UEBA — broader signal set across identity, network, endpoint |
| Where is the **behavioral risk score** for an individual user? | ❌ | ❌ | ❌ | ✅ Authoritative — IRM is the risk-scoring plane (sequence-weighted, indicator-weighted) | ❌ | ⚠️ Sentinel UEBA produces a separate score; correlate but do not conflate |
| **Legal hold + collection** of the activity for litigation / regulatory inquiry | ❌ | ❌ | ❌ | ⚠️ Escalate the IRM case to eDiscovery — see escalation note below | ✅ Authoritative — discovery + hold plane (Premium); **dual-authorization** for case creation in regulated FSI | ❌ |
| **Long-horizon (> 120 d) preservation** of Forensic Evidence clips | ❌ | ❌ | ❌ | ❌ — clips **auto-delete at 120 days**; not the long-term store | ✅ Hold + collection; or promote to Records Management retention label (Control 1.9) | ❌ |
| **Departing-user data theft** detection | ⚠️ DLP at egress | ⚠️ DSPM for sensitive-data exposure | ⚠️ CC for conduct content | ✅ Authoritative — `Data theft by departing users` template (HR connector required) | ⚠️ Hold the leaver's mailbox / OneDrive | ⚠️ Sentinel correlation |
| **Risky agent behavior** (agent emitting sensitive content, accessing priority sites, sharing externally) | ❌ | ⚠️ DSPM for grounding/exposure context | ❌ | ✅ Authoritative — **Risky Agents** template (applied by default) | ❌ | ⚠️ Optional correlation |

### Escalation note — IRM case → eDiscovery (Premium) for legal hold

When an IRM case rises to potential legal action, **promote** rather than convert. The IRM case stays open as the investigation record; in parallel, open an eDiscovery (Premium) case (Control 1.13/1.14) with **dual authorization** (per regulated-FSI hardening), place a **hold** on the subject user's mailbox, OneDrive, Teams, and any priority SharePoint sites surfaced in the IRM data-risk graph, and **export Forensic Evidence clips before the 120-day auto-delete clock fires**. Document the IRM-case-to-eDiscovery-case linkage in both systems.

### When two apply (worked examples)

- **Departing rep with elevated risk score and Copilot usage burst.** IRM (1.12) scores the behavior and produces the case; CC (1.10) reviews the conduct content of the Copilot interactions; DSPM (1.6) shows what grounding data was reachable; eDiscovery (1.13/1.14) holds the artifacts; DLP (1.5) blocks egress prospectively. Compliance reviews the IRM case **and** the CC alerts side-by-side.
- **Possible insider trading discussed via Copilot Chat by a priority user.** CC (1.10) surfaces the conduct content; IRM (1.12) elevates the risk score (`Data leaks by priority users`); eDiscovery (1.13/1.14) preserves and collects for legal hold; Forensic Evidence (1.12) may be invoked **only with dual-auth and Legal sign-off**. The IRM alert is the trigger; eDiscovery is the preservation mechanism; CC is the supervisory review record.
- **Risky Agents alert on a Copilot Studio agent over baseline.** IRM (1.12) is authoritative on the behavior; the Power Platform Admin / Copilot Studio Admin (Control 2.1, 2.16) reviews the agent's design; DSPM (1.6) checks the grounding sources; DLP (1.5) checks whether the agent is exfiltrating sensitive content via response patterns.

---

## §3 — Anti-patterns (do not do)

| Anti-pattern | Why it's wrong | What to do instead |
|---|---|---|
| **Tuning thresholds, weights, or priority-content lists during an active investigation** | Mutates the evidence the investigation depends on; auditor cannot reconstruct what the model scored against at alert time | Snapshot per §1 first; tune in a clone or after the case closes; document the change in a separate ticket |
| **Treating a low risk score as "no risk"** | IRM scoring is **sequence-weighted**, not severity-weighted — a single high-severity event surrounded by normal activity can produce a moderate score; conversely, a sequence of small actions can produce an elevated score even if no single action is severe | Read the **sequence** view, not just the score; cross-reference indicator weights; never close on score alone |
| **Re-identifying pseudonymized users without a logged investigation reason** | Pseudonymization is on by default for a reason; unlogged unmask defeats the privacy-by-design model and creates audit-trail liability for the firm | The Investigator role propagates the unmask; the **Auditor role group** reviews the audit row; require investigation-reason text on every unmask; treat unlogged unmasks as SEV-2 privacy events |
| **Using IRM cases as a records-retention store** | Cases are working investigative artifacts; they are **not WORM**, **not** non-rewriteable, and are **not** an SEC 17a-4 / FINRA 4511 retention substrate | Promote evidence to Records Management retention labels (Control 1.9) and / or eDiscovery (Premium) hold (Control 1.13/1.14) **before** case closure or Forensic Evidence 120-day expiry |
| **Skipping the HR connector and relying on Microsoft Entra signals alone** | Departing-user templates depend on HR-connector fields (`ResignationDate`, `LastWorkingDate`); AAD account state alone does not surface a leaver until the disable event, which is often **after** the exfiltration. This is a FINRA supervisory gap | Stand up the HR connector with documented field mapping; verify last-success ≤ 24 h as a daily SRE check; alert on connector stall as SEV-2 |
| **Skipping the browser extension on Chrome** | The Microsoft Purview extension on Chrome (and the Insider risk extension on Edge) is the signal source for `Risky AI usage`, `Risky browser usage`, and several browser-derived indicators; without it, the policy returns silent zero on Chrome users | Push the extension via Intune (or equivalent MDM) to the entire in-scope Windows population on both Edge and Chrome; record non-Windows as an explicit gap |
| **Sampling the FINRA-supervised population instead of universal scope** | FINRA Rule 3110 / 4511 expectations apply to the **population** of supervised reps; sampling for IRM purposes leaves silent gaps on un-sampled reps | Apply IRM templates to the **full** in-scope population; document any deviation under a written supervisory plan and Compliance approval |
| **Enabling Forensic Evidence without dual authorization or state-law notice** | Forensic Evidence is opt-in, dual-auth (Investigator + Approver, distinct), and may trigger employee-monitoring notice statutes in CT / DE / NY (and others). Enabling it as a "more data is better" default is a privacy / employment-law liability | Coordinate Privacy + Legal + HR before enabling; configure Approvers role group **distinct** from Investigators; document state-law notice posture; capture only against named, scoped policies |
| **Marking an alert "Resolved – False Positive" without rationale** | Loss of supervisory trail under FINRA 3110 — the supervisory record requires the reviewer's documented reason; bare resolution loses the reason | Require resolution-reason text on every alert (Compliance configures the workflow); export resolution rationales as part of the supervisory evidence pack |
| **Deleting / closing cases to "clean up the queue"** | Cases are evidence; deletion is destruction of investigative record; closure without notes loses the investigative trail | Closure requires investigation notes export and SHA-256-hashed case snapshot in the evidence bucket; deletion is a documented exception requiring Compliance + Legal sign-off |
| **Single global priority user group instead of role-based groups** | A single "everyone is priority" group defeats focused review, inflates alert volume, and dilutes scoring; the Reviewer role groups also cannot be cleanly limited to a single function | Define **role-based** priority user groups (trading desk; RIA staff; agent admins; client-facing) and define which role groups may **view** each priority user group; document the rationale |
| **Running policies in Test mode indefinitely** | Test mode produces no alerts (or reduced alerts depending on the template); leaving a policy in Test mode is a silent zero — Compliance sees "policy exists" and assumes coverage | Move to On after the documented baseline period; set a calendared review for any policy still in Test mode; Test-mode duration > 30 d is a SEV-3 finding |
| **Treating "Adaptive Protection enabled" as compliance in Government clouds** | Adaptive Protection has **limited / lagging availability in GCC / GCC High / DoD** per Microsoft Learn; assuming parity with Commercial creates a documented gap that auditors will find | In Gov clouds, document the Adaptive Protection gap as a control exception and apply compensating controls (CC review-cadence increase, DLP block-action tightening, Defender for Cloud Apps anomaly hunts, Sentinel UEBA, manual departure notification flow) |
| **Treating IRM behavioral signals as supervisory review of conduct content** | IRM scores user behavior; CC (Control 1.10) reviews conduct content. They have different review queues, different reviewers, different evidence, and different regulatory framings | Keep them separate; cross-reference where appropriate but do not treat one as the other |
| **Authoring IRM policy from a Restricted-AU admin and assuming tenant-wide scope** | If the author is AU-restricted, the policy may be silently scoped to that AU; effective scope can be narrower than intended | Author with an **unrestricted** Insider Risk Management Admin; only use AU-restricted authors when AU scoping is the explicit intent |

---

## §4 — Symptom-driven diagnostics

> Format: **Symptom → Likely cause → Diagnostic → Fix → Reference.** Sovereign-cloud variants are called out inline. Do not skip the diagnostic step — fixing without diagnosing is what got you here.

### Symptom 1 — No alerts on a known-bad seed activity

| Likely cause | Diagnostic | Fix |
|---|---|---|
| **Unified Audit Log off** at the tenant | `Get-AdminAuditLogConfig` from a `Connect-ExchangeOnline` session — `UnifiedAuditLogIngestionEnabled` should be `True`. **This is the #1 silent-zero cause** | Enable UAL; allow ingestion to backfill; re-run the seed activity after the documented analytics window |
| Policy in **Test mode** rather than On | Purview > Insider Risk Management > Policies > [policy] > Status | Move to On after baseline; document the change |
| Pseudonymization state mismatch between the test identity and the lookup | Settings > Privacy; the test rig may be searching for the raw UPN but the alert lists a pseudonym | Search by case ID / activity timestamp, not by UPN; or temporarily use the Investigator role with an unmask action (logged) |
| Wrong **scope** — test user is outside the policy's user group | Policy > Users in scope | Add the user; or run the seed from an in-scope identity |
| **Analytics not run** / incomplete baseline (< 7 d) | Insider Risk Management > Analytics > scan status | Wait the documented baseline period (Learn states scans may take up to **48 h**); do not conclude "no signal" inside that window |
| Administrative-unit-restricted observer is checking from a different AU than the alert's user | Observer's AU vs alert user | Re-check from an unrestricted IRM Admin / Analyst session |

**Sovereign cloud:** UAL behavior is at parity; analytics scan cadence may differ slightly in Gov clouds — verify on current Learn.
**Reference:** Microsoft Learn — `insider-risk-management`, `audit-log-activities`.

### Symptom 2 — Risky AI usage policy returns zero alerts

| Likely cause | Diagnostic | Fix |
|---|---|---|
| **Browser extension not deployed** (Microsoft Insider risk extension on Edge; Microsoft Purview extension on Chrome) | Intune (or equivalent MDM) configuration profile coverage report; Edge `edge://extensions/` on a sample device; Chrome `chrome://extensions/` | Push extension via Intune to the in-scope Windows population on both browsers; allow propagation; re-test |
| **Non-Windows devices** in scope — the browser-signal source is **Windows-only** per Learn (`insider-risk-management-browser-support`) | Device inventory by OS class | Document the non-Windows gap as a control exception; apply compensating controls (CC review cadence, DLP at gateway, Defender for Cloud Apps for SaaS-side AI) |
| Device **not onboarded to Microsoft Purview** | Purview > Settings > Device onboarding; cross-reference against test device | Onboard the device class; allow propagation; re-test |
| **Browsing indicators off** in IRM settings | Settings > Policy indicators > Browsing indicators | Enable the relevant browsing indicators (risky AI prompt, risky AI response, etc.); re-test |
| **PAYG dependency** for non-M365 AI sources surfaced in scope | Purview billing model | Enable PAYG; allow propagation; re-validate |

**Sovereign cloud:** Browser-extension support and Risky AI usage availability lag in GCC High / DoD; verify on current Learn before promising coverage.
**Reference:** Microsoft Learn — `insider-risk-management-browser-support`, `insider-risk-management`.

### Symptom 3 — Risky Agents producing noise

| Likely cause | Diagnostic | Fix |
|---|---|---|
| **Default policy scope** — Risky Agents is applied **by default** when IRM is configured; it is not selected via Create policy and may be over-broad against the firm's agent surface | Policies list — confirm Risky Agents is present; review its scope as displayed | Do not delete; per Learn the template is applied by default. Tune via priority user groups (agent admins) and priority content (sensitive SharePoint sites) where supported; document tuning |
| **Baseline still calibrating** — alert volume is high in the first 7–14 days while the model establishes per-agent / per-tenant baseline | Compare daily alert volume; expect downward trend after baseline | Hold tuning until baseline elapses; capture the calibration window in the operations log |
| **Priority content list is too narrow** — every interaction with a sensitive site triggers; alert volume reflects exposure, not anomaly | Priority content list snapshot vs alert content | Review the priority content list with Compliance / DSPM (Control 1.6); not all sensitive content needs to be priority content for IRM |

**Sovereign cloud:** Risky Agents availability follows IRM general availability per cloud; verify on current Learn.
**Reference:** Microsoft Learn — `insider-risk-management` (Risky Agents section).

### Symptom 4 — HR connector stale (last-success > 24 h)

| Likely cause | Diagnostic | Fix |
|---|---|---|
| **Certificate or token expired** on the Microsoft Entra app backing the connector | Microsoft Entra > App registrations > [HR connector app] > Certificates & secrets | Rotate certificate / secret; update connector configuration; re-run job |
| **CSV schema drift** — HRIS export added/removed columns; field mapping no longer aligns | Connector configuration > Field mapping vs current CSV header | Re-map fields; in particular verify `EmployeeID`, `ResignationDate`, `LastWorkingDate`, `EmploymentStatus`; re-run |
| **Dual-system conflict** — the same EmployeeID arriving from two HR sources with conflicting `LastWorkingDate` | Source CSVs side-by-side | Reconcile at the HRIS side; do not let IRM consume conflicting truth |
| **Storage / staging account** issue (where ingestion uses a staging blob) | Staging account access; SAS expiry | Renew SAS; re-run |

**Sovereign cloud:** HR connector availability is at general parity; verify on current Learn for any preview features.
**Reference:** Microsoft Learn — `import-hr-data`.

### Symptom 5 — Departing-user template not firing for a known leaver

| Likely cause | Diagnostic | Fix |
|---|---|---|
| HR connector field mapping wrong — `ResignationDate` populated but `LastWorkingDate` blank → the **trigger date** is missing | HR connector > Field mapping; sample row for the leaver | Map both fields; re-ingest; re-evaluate the policy lookback window |
| Leaver was added **after** the policy's lookback window started | Policy > Conditions > Activity lookback | Adjust the lookback or add the leaver via manual flag where the template supports; document |
| User not in the policy's **user scope** (e.g., excluded by AU or by group) | Policy > Users in scope | Add user (or the user's group); re-evaluate |
| Cloud-app indicators expected but Defender for Cloud Apps connector for the SaaS source is not configured | Defender for Cloud Apps > Connectors | Configure connector; allow sync; re-evaluate |
| **HR connector last-success > 24 h** (see Symptom 4) | Connector last-success | Resolve connector first; the policy will not see a leaver the connector did not deliver |

**Sovereign cloud:** Departing-user template availability follows IRM general availability per cloud.
**Reference:** Microsoft Learn — `insider-risk-management`, `import-hr-data`.

### Symptom 6 — Forensic Evidence policy not capturing

| Likely cause | Diagnostic | Fix |
|---|---|---|
| **Dual-auth not configured** — capture requests have no Approver to review them | Insider Risk Management > Forensic Evidence > Approval settings | Configure Approvers role group; populate with members **distinct from Investigators**; re-submit request |
| **Approvers role group empty** | Role-group membership | Populate; allow up to 30 min role-propagation per Learn |
| **Microsoft Purview Client missing** on the target device | Device app inventory | Push Purview Client via Intune; reboot; re-test |
| **Device not onboarded** to Microsoft Purview | Purview device onboarding state | Onboard; allow propagation; re-test |
| **Storage cap reached** — PAYG storage trial exhausted; new captures rejected | Forensic Evidence > Storage usage | Increase PAYG storage limit; export old captures **before the 120-day expiry** (Control 1.9 / 1.13/1.14) |
| **State-law notice not posted** for affected user's state (CT / DE / NY) — capture suspended pending Privacy/Legal sign-off | Privacy register | Post notice; coordinate with HR; resume |

**Sovereign cloud:** Forensic Evidence availability lags in GCC High / DoD; verify on current Learn.
**Reference:** Microsoft Learn — `insider-risk-management-forensic-evidence`.

### Symptom 7 — Forensic Evidence clip approaching 120-day auto-delete

| Likely cause | Diagnostic | Fix |
|---|---|---|
| Clip captured > 90 d ago and still relevant to an open case | Clip inventory with capture UTC and retention countdown | **Promote** before expiry: (a) export clip; (b) apply Records Management retention label (Control 1.9) for required period; OR (c) add to eDiscovery (Premium) hold (Control 1.13/1.14). Document handoff path; do not let the clock fire on an evidence-relevant clip |
| Bulk export needed for a multi-clip case | Clip count for the case | Schedule export with Forensic Evidence Approver dual-auth; capture export manifest with SHA-256 sidecar |

**Sovereign cloud:** 120-day auto-delete behavior is at parity (where the feature is available).
**Reference:** Microsoft Learn — `insider-risk-management-forensic-evidence`; Control 1.9 Records Retention; Control 1.13/1.14 eDiscovery.

### Symptom 8 — Adaptive Protection not adjusting DLP / DLM / Conditional Access

| Likely cause | Diagnostic | Fix |
|---|---|---|
| **Sovereign-cloud parity gap** — Adaptive Protection has limited / lagging availability in GCC / GCC High / DoD per Learn | Confirm tenant cloud; check current Learn matrix | Document the gap as a control exception; apply compensating controls (manual DLP tightening, CC review cadence, Defender for Cloud Apps anomaly hunts, Sentinel UEBA) |
| **Insufficient signal volume** — baseline still calibrating; risk-level threshold not yet crossed | Insider Risk Management > Adaptive Protection > User risk distribution | Wait the calibration window; do not pre-tune the threshold during the baseline |
| Adaptive Protection consumes signals from `Risky AI usage` / `Risky Agents` / data-leak templates — the upstream policy is in Test mode or zero-alert | Upstream policy state | Resolve upstream first; Adaptive Protection cannot adjust from a silent input |
| Conditional Access policy that should consume the Adaptive Protection user-risk insider-risk-level signal is not configured for it | Microsoft Entra > Conditional Access > [policy] > Conditions | Configure the Conditional Access policy to consume the insider risk level signal per Learn; test with a known-elevated user |

**Sovereign cloud:** Adaptive Protection lag in GCC / GCC High / DoD is the most common source of this symptom; document and compensate.
**Reference:** Microsoft Learn — `insider-risk-management-adaptive-protection`.

### Symptom 9 — IRM portal access denied for a scoped admin

| Likely cause | Diagnostic | Fix |
|---|---|---|
| **Administrative-unit exclusion** — the admin is restricted to an AU that does not contain the requested users / data | Microsoft Entra > Roles > Admin's AU assignments | Either re-scope the AU, or use an unrestricted IRM Admin for the action; document |
| **Role propagation 30-min delay** has not elapsed since the role-group change | Role-group membership change UTC vs current UTC | Wait the documented window; re-test |
| Admin in the wrong role group for the action (e.g., Analyst attempting to view file content; Investigator without Approver authority attempting Forensic Evidence approval) | Role-group permissions table on Learn | Reassign per least-privilege; **never** add an Investigator to Approvers — that defeats dual-auth |

**Sovereign cloud:** Behavior at parity; AU support has historically lagged in DoD — verify on current Learn.
**Reference:** Microsoft Learn — `insider-risk-management-permissions`.

### Symptom 10 — Pseudonymized usernames cannot be unmasked

| Likely cause | Diagnostic | Fix |
|---|---|---|
| Investigator does not have the Investigator role group; Analysts cannot unmask | Role-group membership | Assign Investigator role; allow propagation |
| Unmask attempted without an investigation reason text — workflow rejects | Investigation note state | Add reason text per the firm's documented investigation procedure; re-attempt; the **Auditor role group** will see this row |
| Pseudonymization is on at tenant level and the investigator expected raw UPNs in the alerts list — not how the feature works | Settings > Privacy state | Pseudonymization is by design; unmask is per-investigation, logged. Re-train the investigator if needed |

**Sovereign cloud:** Behavior at parity; privacy obligations remain jurisdictional.
**Reference:** Microsoft Learn — `insider-risk-management` (Privacy by design); `insider-risk-management-permissions`.

### Symptom 11 — Triage Agent not appearing

| Likely cause | Diagnostic | Fix |
|---|---|---|
| **Preview / GA lifecycle churn** — the Triage Agent capability has moved between Preview and GA states; verify current lifecycle on Microsoft Learn at the time of the incident | Learn `insider-risk-management` Triage Agent section | If Preview, opt in per the documented preview enrollment; if GA, verify region availability |
| **Capacity prerequisites** not met — Security Copilot SCU capacity / Copilot capacity required | Security Copilot capacity allocation | Allocate capacity; allow propagation; re-test |
| **Security Copilot prereqs** missing (license, role assignment, plug-in availability) | Security Copilot setup | Resolve the Security Copilot setup before re-attempting Triage Agent enablement |

**Sovereign cloud:** Triage Agent availability lags Commercial; verify on current Learn before relying on it in Gov clouds.
**Reference:** Microsoft Learn — `insider-risk-management` (Triage Agent section); Security Copilot setup docs.

### Symptom 12 — Case escalation to eDiscovery fails

| Likely cause | Diagnostic | Fix |
|---|---|---|
| **License / SKU** for eDiscovery (Premium) missing for the escalating user or for the subject's mailbox | License entitlement check | Assign the required license; document |
| **Role assignment** missing — the IRM Investigator does not also have the eDiscovery Manager / Reviewer role required to create the case | Microsoft Purview > Permissions > eDiscovery role groups | Assign the role; allow propagation; re-attempt. In regulated FSI, prefer **dual-authorization** for eDiscovery case creation |
| **Scope mismatch** — the IRM case is scoped to an AU; the eDiscovery user is scoped to a different AU | AU scope cross-check | Use an unrestricted user for the escalation; document |
| Case linkage broken — IRM case ID not propagating into the eDiscovery case for traceability | Linkage field state | Manually record the IRM case ID in the eDiscovery case description; document the dual-record-keeping practice |

**Sovereign cloud:** eDiscovery (Premium) availability is at general parity; verify any preview features per Learn.
**Reference:** Microsoft Learn — eDiscovery (Premium) docs; Control 1.13/1.14.

### Symptom 13 — IRM admin actions not appearing in Unified Audit Log

| Likely cause | Diagnostic | Fix |
|---|---|---|
| **`Search-UnifiedAuditLog` paging** — default page size is small; large-window queries silently truncate | Use `-SessionId` + `-SessionCommand ReturnLargeSet` and paginate; cap 50,000 rows per session | Re-run with proper pagination; preserve raw output; SHA-256 the export |
| **RecordType / Operations names** assumed from prior playbooks — Microsoft renames operations periodically | Cross-reference current Learn `audit-log-activities` for IRM operation names | Use the current Learn-canonical operation names; never hard-code names from a prior incident's runbook |
| Action performed by an account whose audit ingestion is restricted (rare; verify) | Audit configuration | Verify `Get-AdminAuditLogConfig` from EXO; the IPPS value can be cached / stale |
| Query window starts before audit ingestion was enabled | UAL ingestion-enabled UTC | Adjust query window; re-run |

**Sovereign cloud:** Operation-name parity is generally close; record any naming differences in the deviation register.
**Reference:** Microsoft Learn — `audit-log-activities`; Control 1.7 Audit.

### Symptom 14 — Cloud-app exfiltration signals missing

| Likely cause | Diagnostic | Fix |
|---|---|---|
| **Defender for Cloud Apps connectors not configured** for the SaaS source (Box, Dropbox, Google Drive, Amazon S3, Azure) | Defender for Cloud Apps > Connectors | Configure connector; allow initial sync (can take 24–48 h); re-evaluate |
| Connector configured but in **error / delayed** state | Connector health page | Resolve credential / API quota issue; re-sync |
| Cloud-app indicators not enabled in IRM policy | Policy > Indicators > Cloud-app indicators | Enable; re-evaluate after lookback |

**Sovereign cloud:** Defender for Cloud Apps connector parity differs in GCC High / DoD — verify on current Learn.
**Reference:** Microsoft Learn — Defender for Cloud Apps connector docs; `insider-risk-management`.

### Symptom 15 — Security policy violations template producing nothing

| Likely cause | Diagnostic | Fix |
|---|---|---|
| **Microsoft Defender for Endpoint integration not configured** — the template depends on MDE for security-control evasion, unwanted software, MDE alerts; without MDE the template is silently empty | Defender for Endpoint > Settings > Integrations; cross-reference with IRM Settings > Connectors | Configure MDE integration; allow propagation; re-evaluate |
| MDE is configured but the device is not onboarded to MDE (only to Purview) | Device onboarding state in both portals | Onboard to MDE; allow propagation; re-test |
| Policy in Test mode | Policy status | Move to On |

**Sovereign cloud:** MDE integration availability is at general parity; verify on current Learn.
**Reference:** Microsoft Learn — `insider-risk-management` (Security policy violations template); MDE integration docs.

### Symptom 16 — Priority user group not viewable by an analyst

| Likely cause | Diagnostic | Fix |
|---|---|---|
| **Review-scope step missing** — when defining a priority user group, IRM also requires defining **which role groups may view that priority user group**; if not configured, only Admins see it | Settings > Priority user groups > [group] > Reviewers | Define the role groups permitted to view; allow propagation; re-test from the analyst's session |
| Analyst is AU-restricted and the priority user group's members are outside the analyst's AU | AU scope vs group membership | Either re-scope the AU or assign an unrestricted analyst; document |

**Sovereign cloud:** Behavior at parity.
**Reference:** Microsoft Learn — `insider-risk-management` (Priority user groups section).

### Symptom 17 — Adaptive Protection threshold trigger never fires

| Likely cause | Diagnostic | Fix |
|---|---|---|
| **Insufficient signal volume** — the upstream IRM policies have not produced enough activity to cross the configured insider risk-level threshold | Adaptive Protection > User risk distribution view | Wait the calibration window (depends on tenant signal density); do not pre-tune the threshold during baseline |
| Threshold set higher than realistic for the firm's signal density | Threshold setting vs distribution | Re-tune **after** baseline, with documented rationale; capture before/after distribution |
| Sovereign-cloud gap (see Symptom 8) — Adaptive Protection unavailable in cloud | Cloud check | Document exception; apply compensating controls |
| Upstream `Risky AI usage` / `Risky Agents` / data-leak template in Test mode (silent input) | Upstream policy state | Move upstream policy to On; allow window; re-evaluate Adaptive Protection distribution |

**Sovereign cloud:** Adaptive Protection lag in Gov clouds is the most common root cause.
**Reference:** Microsoft Learn — `insider-risk-management-adaptive-protection`.

### Symptom 18 — IRM cases queue showing zero after recent admin activity

| Likely cause | Diagnostic | Fix |
|---|---|---|
| AU-restricted observer | AU scope | Re-check from unrestricted IRM Admin |
| Cases were **closed** by an admin (intentionally or not) | Cases > Status filter > Closed | Re-open if closed in error; capture the closure event from UAL; treat unexplained mass closure as SEV-2 (potential anti-pattern violation) |
| **Cases deleted** to "clean the queue" — anti-pattern (§3) | UAL search for case deletion operations (verify operation names per Learn) | Restore from evidence pack if available; treat as SEV-1 evidence-destruction event; escalate to Compliance + Legal |

**Sovereign cloud:** Behavior at parity.
**Reference:** Microsoft Learn — `insider-risk-management-cases`; `audit-log-activities`.

---

## §5 — Sovereign cloud notes (summary)

| Capability | Commercial | GCC | GCC High | DoD |
|---|---|---|---|---|
| Insider Risk Management core (policies, alerts, cases, role groups, pseudonymization) | ✅ GA | ✅ (verify per Learn) | ⚠️ Verify per Learn | ⚠️ Verify per Learn |
| **Risky Agents** (default policy template) | ✅ | ⚠️ Follows IRM general availability | ⚠️ Lagging — verify per Learn | ⚠️ Lagging — verify per Learn |
| **Risky AI usage** (requires browser extension) | ✅ | ⚠️ Verify | ⚠️ Lagging | ⚠️ Lagging |
| **Adaptive Protection** | ✅ | ⚠️ **Limited / verify per Learn** | ⚠️ **Limited / lagging — document exception** | ⚠️ **Limited / lagging — document exception** |
| **Forensic Evidence** (PAYG, dual-auth, 120-d clip retention) | ✅ | ⚠️ Verify PAYG availability | ⚠️ Lagging | ⚠️ Lagging |
| **Triage Agent** (Security Copilot–powered) | ⚠️ Verify lifecycle on Learn (Preview → GA churn) | ⚠️ Verify | ⚠️ Lagging | ⚠️ Lagging |
| Microsoft 365 HR connector | ✅ | ✅ | ✅ (verify) | ⚠️ Verify |
| Defender for Endpoint integration | ✅ | ✅ | ✅ | ⚠️ Verify |
| Defender for Cloud Apps connectors (Box / Dropbox / Google Drive / S3 / Azure) | ✅ | ⚠️ Verify per connector | ⚠️ Lagging | ⚠️ Lagging |
| Browser signal source — Microsoft Insider risk extension (Edge) and Microsoft Purview extension (Chrome); **Windows-only** | ✅ | ✅ (verify per cloud) | ⚠️ Verify | ⚠️ Verify |
| Administrative units in IRM | ✅ | ✅ | ✅ (verify per Learn) | ⚠️ Verify |
| Pseudonymization (default on) | ✅ | ✅ | ✅ | ✅ |
| Portal hostname | `purview.microsoft.com` | `compliance.microsoft.com` | `purview.microsoft.us` | `purview.apps.mil` (verify current) |

Document any sovereign-cloud exception in the control's deviation register; re-check on each Microsoft Learn refresh. **For tenants where Adaptive Protection or Forensic Evidence is unavailable, the gap is documented and compensated — it is not "broken."** Do not open Microsoft support tickets on documented Gov-cloud parity gaps.

---

## §6 — Escalation

### L1 — IRM Admin (within 1 h SEV-1; 4 h SEV-2)

- Preserve evidence per §1 **before** any remediation
- Run pre-escalation checklist (≥ 12 items)
- Apply documented compensating controls; do not leave the detection gap open

### L2 — AI Governance Lead / Insider Risk Lead + Privacy Officer (within 1 h SEV-1)

- Triage cross-control impact (1.5 DLP, 1.6 DSPM, 1.7 Audit, 1.9 Records, 1.10 CC, 1.13/1.14 eDiscovery, 2.1 / 2.16 Agent governance)
- Privacy review for any pseudonymization-related, NPI-related, Forensic-Evidence-related, or unmask event
- Coordinate Forensic Evidence state-law notice posture (CT / DE / NY) before any new capture during the incident

### L3 — CISO + Compliance Officer + Legal + HR (within 1 h SEV-1)

- Reportability determination per §1 decision tree
- **NYDFS 23 NYCRR 500 §500.17(a) 72-hour cybersecurity-event determination** — Legal owns the decision; clock starts at **determination**, not first alert
- Coordinate HR for any departing-user, misconduct, or Forensic Evidence subject-notification matter
- Decide regulator notification path (FINRA / SEC / NYDFS / state AGs / OCC / Fed / CFTC) — this is **their** decision, not Engineering's

### L4 — Microsoft support ticket

Use this payload template when opening the Microsoft support ticket (paste into the description verbatim and fill the bracketed fields). For Forensic Evidence clips shared with Microsoft Support, **redact to the minimum necessary** and document the redaction state:

```
Severity: [SEV-1 | SEV-2 | SEV-3]
Tenant ID: [GUID]
Cloud: [Commercial | GCC | GCC High | DoD]
Affected workload: Microsoft Purview Insider Risk Management
Affected feature: [IRM core | Risky AI usage | Risky Agents | Adaptive Protection | Forensic Evidence | Triage Agent | HR connector | other]
Affected scope: [policy ID(s); user count; UTC window start–end]
Alert / case ID(s): [comma-separated]
Symptom: [one-line description, e.g., "Risky AI usage policy 'Reps-Risky-AI' producing zero alerts since 2026-04-12T14:00Z despite known seed activity at 2026-04-12T15:30Z; browser extension confirmed deployed; UAL confirmed enabled; pre-escalation checklist items 1-16 pass."]
Business impact: Insider-risk detection degradation for [N] FINRA-supervised registered representatives / [M] priority users; potential FINRA Rule 3110(b) supervisory-system gap; firm is in [active examination | quarter-end review | none]; NYDFS 72-hour clock evaluation: [pending Legal | not applicable | clock running].
Evidence pack reference: [internal evidence ID; offer to share artifacts under NDA]
Forensic Evidence clip redaction state (if any clip is shared): [unredacted | redacted to subject-of-investigation only | redacted to specific frames; identifying third parties removed]
Steps already taken: [pre-escalation checklist items 1-16 confirmed; compensating controls in place: CC review cadence increased (Control 1.10), DLP-for-Copilot block actions tightened (Control 1.5), Defender for Cloud Apps anomaly hunts running, Sentinel UEBA correlation, manual departure notifications via HR, freeze of new Zone 3 agent activations (Control 2.1, 2.16)]
Engineer of record: [name, role, email, phone, time zone]
Compliance contact: [name, role, email]
Privacy contact (if Forensic Evidence / pseudonymization in scope): [name, role, email]
```

### L5 — Internal Compliance / Legal / HR communication template

Use this payload when handing off to internal Compliance, Legal, and HR (separate from the Microsoft support ticket):

```
To: Compliance Officer; General Counsel; Privacy Officer; CISO; Head of HR
From: [AI Governance Lead / Insider Risk Lead]
Severity: [SEV-1 | SEV-2]
Subject: Insider Risk Management detection degradation — [date]

1. What happened
   - [Plain-language description, no jargon]
   - Affected user population: [N FINRA-supervised reps in BU X; Y priority users (trading desk / RIA staff / agent admins)]
   - UTC window: [start – end]
   - Forensic Evidence in scope: [yes / no; if yes, subject's state of residence and notice posture]

2. Possible regulatory exposure (§1 reportability triage)
   - FINRA Rule 3110(b) supervisory system: [yes / unclear / no — Compliance to confirm]
   - FINRA Notice 25-07 AI/agent supervision reminder: [contextual]
   - FINRA Rule 4511 / SEC 17a-4(b)(4) books-and-records: [if IRM artifacts treated as records and lost; gap is in records pipeline, not IRM]
   - GLBA 501(b) / SEC Reg S-P §248.30: [if NPI in scope]
   - SOX 302/404 ICFR: [if financial-disclosure-adjacent insider activity]
   - NYDFS 23 NYCRR 500 §500.17(a) 72-hour cybersecurity-event clock: [pending Legal determination | not applicable | clock running since UTC X]
   - OCC 2011-12 / Fed SR 11-7 model risk: [if ML risk scoring or Triage Agent produced demonstrably wrong prioritization]
   - CFTC 1.31: [if covered swap / trading-related activity]
   - FINRA 4530: [if misconduct surfaced]
   - State employee-monitoring notice law (CT / DE / NY): [if Forensic Evidence captured for resident of those states]

3. Evidence preserved (§1)
   - Policy snapshot, alert/case state snapshot, investigation notes export, Forensic Evidence clip
     inventory with retention countdown, role-group snapshot, priority user/content snapshots,
     pseudonymization state (pre-unmask), HR connector last-success + field mapping, browser
     extension/Edge config policy state, device onboarding state, audit-search export (paged,
     SHA-256 sidecared), Defender for Cloud Apps connector health, MDE integration state,
     sovereign-cloud parity confirmation, PAYG state, SHA-256 manifest. Stored in Control 1.7
     evidence bucket reference [ID].

4. Compensating controls in place
   - [CC review cadence increased on in-scope Copilot / conduct-content templates (Control 1.10)]
   - [Daily UAL searches running for affected user population (Control 1.7)]
   - [DLP-for-Copilot block actions tightened from TestWithNotifications to Enable for NPI/MNPI (Control 1.5)]
   - [DSPM hunts for grounding-data exposure on subject's reachable sites (Control 1.6)]
   - [Defender for Cloud Apps anomaly hunts]
   - [Sentinel UEBA correlation queries running]
   - [Manual HR departure notification flow invoked for known leavers within lookback window]
   - [Freeze of new Zone 3 agent activations / Copilot Studio publishes (Controls 2.1, 2.16)]
   - [Forensic Evidence clip exports completed before 120-day expiry where applicable (handed off to Records Management per Control 1.9 and/or eDiscovery hold per Control 1.13/1.14)]

5. Open questions for Compliance / Legal / HR
   - Reportability determination (per §1 tree)
   - NYDFS 72-hour determination
   - Customer-notification timeline if NPI in scope (SEC Reg S-P)
   - Examiner-disclosure obligation if firm is in active examination
   - HR coordination for any departing-user subject and any Forensic Evidence subject-notification posture
   - Privacy register update for any pseudonymization re-identification performed during the incident

6. Next status update: [UTC]
```

---

## §7 — Cross-links

- [Control 1.12 Insider Risk Detection and Response](../../../controls/pillar-1-security/1.12-insider-risk-detection-and-response.md) — control of record
- [Control 1.12 Portal Walkthrough](portal-walkthrough.md)
- [Control 1.12 PowerShell Setup](powershell-setup.md)
- Control 1.12 Verification & Testing (planned — see playbook directory)
- [Control 1.5 DLP and Sensitivity Labels](../1.5/troubleshooting.md) — preventive enforcement plane; compensating control during IRM degradation; tightened by Adaptive Protection where available
- [Control 1.6 Grounding Data Protection / DSPM for AI](../1.6/troubleshooting.md) — DSPM signals feed Risky AI usage; canonical §1 FSI Incident Handling source
- [Control 1.7 Comprehensive Audit Logging](../1.7/troubleshooting.md) — durable evidence backbone; UAL is the substrate IRM scores against
- [Control 1.9 Data Retention and Deletion Policies](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md) — the records-retention boundary; **IRM is not a records substrate**; promote Forensic Evidence clips here before 120-day auto-delete
- [Control 1.10 Communication Compliance Monitoring](../1.10/troubleshooting.md) — supervisory review of conduct content; complementary to IRM behavioral risk
- [Control 1.13 / 1.14 eDiscovery (Standard / Premium)](../../../controls/pillar-1-security/index.md) — legal hold + collection; promote IRM cases here for legal hold; export Forensic Evidence clips here before 120-day expiry
- [Control 2.1 Managed Environments](../../../controls/pillar-2-management/2.1-managed-environments.md) — agent surface; freeze new publishes during IRM degradation
- [Control 2.6 Model Risk Management (OCC 2011-12 / SR 11-7)](../../../controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md) — ML risk scoring + Triage Agent must be in the model inventory
- [Control 2.12 Supervision and Oversight (FINRA Rule 3110)](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) — supervisory procedures; sampling methodology; supervisory-record template
- [Control 2.16 RAG Source Integrity Validation](../../../controls/pillar-2-management/2.16-rag-source-integrity-validation.md) — Zone 3 agent freeze coordination point
- [Role Catalog](../../../reference/role-catalog.md) — canonical role names (Insider Risk Management Admins / Analysts / Investigators / Auditors / Approvers; Purview Compliance Admin; Entra Global Admin; Power Platform Admin; Exchange Online Admin)
- Microsoft Sentinel UEBA — where deployed, an independent peer-baseline view; cross-correlate but do not conflate with IRM scoring

---

*Updated: April 2026 | Version: v1.4 | UI Verification Status: Current*
