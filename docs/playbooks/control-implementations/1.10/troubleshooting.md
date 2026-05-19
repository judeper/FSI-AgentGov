# Control 1.10 — Troubleshooting: Communication Compliance Monitoring

**Control:** [1.10 Communication Compliance Monitoring](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md)
**Audience:** Microsoft 365 administrator at a US financial services organization, typically under audit pressure or active incident response.
**Sovereign clouds covered:** Commercial, GCC, GCC High, DoD (parity gaps called out inline).
**Last UI Verified:** April 2026

---

## §1 — FSI Incident Handling — READ FIRST

Microsoft Purview Communication Compliance (CC) is the **supervisory review plane** for in-scope conduct content (email, Teams chat, Viva Engage, M365 Copilot interactions, third-party AI). For an FSI organization it is a **books-and-records system** under SEC Rule 17a-4 and a **supervisory system component** under FINRA Rule 3110(b). A loss, mis-scoping, or silent degradation of a CC policy on a population of registered representatives is **not a UI nuisance** — it is a supervisory-system failure. Treat any change to a CC policy, role-group membership, reviewer assignment, or pseudonymization setting as an **evidence-bearing event**: preserve **before** you remediate.

> **Critical Learn-verified constraint:** PowerShell is **not supported** for creating, editing, or deleting CC policies. Per Microsoft Learn (`communication-compliance-policies`), all policy CRUD must be performed in the Microsoft Purview portal. Any "fix" script that purports to mutate CC policy via cmdlets is wrong by construction — see §3 anti-patterns.

### Severity matrix (Zone-aware)

| Severity | Trigger (CC-specific) | Response window | Escalation |
|---|---|---|---|
| **SEV-1** | CC policy covering a Zone 3 population of FINRA-supervised registered representatives is **off, deleted, mis-scoped, or producing zero matches** during a window where messages were known to flow; reviewer role group is empty (zero-administrator state); pseudonymization was disabled without a documented opt-in trail; an unauthorized identity opened message bodies; a Copilot-scoped CC policy is missing for a Zone 3 agent surface | Immediate | CISO + Compliance + Legal + Privacy within 1 h |
| **SEV-2** | Coverage gap on a Zone 2 population (e.g., Teams Shared Channel not captured, Viva Engage scope missing, single business unit excluded); reviewer assigned at the role-group level but cannot open alerts (per-policy reviewer never assigned); PAYG not enabled for in-scope non-M365 AI; classifier model bumped and false-positive volume invalidated the prior week's review evidence; per-policy reviewer left the firm and replacement is not yet documented | 4 h | Communication Compliance Admin → AI Governance Lead within 4 h |
| **SEV-3** | Single-user / single-channel coverage gap on a Zone 2 surface; processing window exceeded (Teams 48 h documented; non-M365 AI longer); OCR / translation regression on attachments; alert-routing notification email failure | 1 business day | Communication Compliance Admin |
| **SEV-4** | Cosmetic UI drift; tooltip / column ordering changes; preview-feature regression that does not affect coverage, reviewer access, or evidence | Best effort | Track in known-issues log |

**Zone-aware reading:** Severity is interpreted against the in-scope user population. The same configuration error is SEV-1 against a Zone 3 broker-dealer population and SEV-3 against a Zone 1 administrator pilot. Always classify by the **regulatory exposure of the affected users**, not by the technical defect.

### Reportability decision tree

> This is an **escalation aid**, not a legal determination. Reportability is decided by Compliance and Legal. Use this matrix to surface the right question to the right desk **inside the response window** — do not self-decide.

| Trigger | Escalate to | Possible obligation (verify with counsel) |
|---|---|---|
| Loss of supervisory visibility on conduct content for FINRA-supervised registered representatives | Compliance | **FINRA Rule 3110(b)** supervisory system; documented procedures must be followed |
| Books-and-records gap — supervisory review records missing or unrecoverable for required period | Compliance + Legal | **FINRA Rule 4511(a)/(b)** make-and-preserve; **SEC Rule 17a-3** required records; **SEC Rule 17a-4(b)(4)** — communications relating to the business as such, retained ≥3 years, first 2 in easily accessible place |
| Off-channel / personal-device communications surfaced via CC for in-scope reps | Compliance + Legal | **FINRA Regulatory Notice 24-09** firm guidance on generative-AI communications supervision; off-channel communications supervision continues to be governed by **FINRA Rules 3110/4511** as restated in [FINRA's 2024-2025 enforcement reports](https://www.finra.org/rules-guidance/notices/24-09) — do not over-cite 25-07 (workplace modernization Regulatory Notice) as an off-channel authority |
| Customer NPI / PII surfaced in a CC-monitored channel without controls | Privacy + Legal | **GLBA 501(b)** safeguards; **SEC Reg S-P** §248.30(a)(4) customer-notification timeline (post-2024 amendments) |
| Internal control over financial reporting impacted by CC supervisory failure (financial-disclosure-related communications) | Compliance + Internal Audit | **SOX §302 / §404** ICFR — supervisory control referenced in the firm's control inventory |
| AI / model-related operational risk event (e.g., classifier model change invalidated supervisory evidence) | Model Risk + Compliance | **OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12)** / **Fed SR 26-2 (formerly SR 11-7)** model risk management |
| Records-related event for a covered swap / trading-related communication | Compliance | **CFTC Rule 1.31** recordkeeping (full, complete, original; retention period; production timeline) |
| Unauthorized access to / disclosure of personal information via reviewer mis-permissioning | Privacy + Legal | State breach-notification statutes (e.g., NY SHIELD, CA AB 1950); NYDFS **23 NYCRR 500** 72-hour determination if cybersecurity event |
| Insider misconduct surfaced through CC alerts (e.g., bribery, market manipulation, harassment) | HR + Legal + Compliance | **FINRA Rule 4530** reporting; firm code-of-conduct procedures |

### Evidence preservation **before** remediation

A common audit finding in FSI is _"the policy was modified before the failing-state evidence was captured, and the firm cannot reconstruct what supervisory review was in effect during the relevant period."_ Do not be that finding. Capture the following artifacts **before** disabling, editing, re-scoping, or replacing reviewers:

1. **Policy export.** Purview portal: Solutions > Communication Compliance > Policies > [policy] > **Export** (CSV of policy modification history, alerts pending review, escalated, resolved). Per Learn, this is the supported export — there is no `Get-CommunicationCompliancePolicy` equivalent.
2. **Role-group snapshot** for: `Communication Compliance`, `Communication Compliance Admins`, `Communication Compliance Analysts`, `Communication Compliance Investigators`, `Communication Compliance Viewers`. Capture membership, AU restriction state, and effective permissions at UTC of capture.
3. **Per-policy reviewer assignment snapshot** for every in-scope policy, including the **User-reported messages** policy (where a reviewer mis-assignment is the most common privacy violation in FSI — see §3).
4. **Pending-queue screenshot** for the affected policy — full page, with the alert count, sample alerts, and timestamp visible.
5. **Privacy / pseudonymization settings screenshot** — Communication Compliance > Settings > Privacy. Capture the pseudonymization state and the identity that last toggled it.
6. **Audit-search export** for the suspect window from a `Connect-ExchangeOnline` session (NOT IPPS): `Search-UnifiedAuditLog` filtered for record types relevant to CC actions and message processing — verify the record-type names against the current Microsoft Learn `audit-log-activities` reference; do not assume names from prior playbooks. Paginate; cap 50,000 per session.
7. **Classifier model version** — for any classifier-based policy, record the classifier and (where surfaced) the model version that was active at the time of the suspect window. A classifier model bump after the fact invalidates the prior baseline.
8. **Sovereign-cloud parity confirmation** — record cloud (Commercial / GCC / GCC High / DoD) and verify against current Microsoft Learn matrix that the in-scope features were available in that cloud at the time of the suspect window.
9. **PAYG billing state** for any in-scope non-Microsoft-365 generative AI source (Copilot in Fabric, Security Copilot, Microsoft Copilot Studio Copilots, connected external AI apps, browser-detected "Other AI apps"). Per Learn (`communication-compliance-channels`), PAYG is **required** for non-M365 AI sources; without it, the scope is silently empty.
10. **Tenant ID, cloud, affected user/policy/channel list, UTC window, role used, identity that performed the failing-state observation, browser, sign-in method.**
11. **SHA-256 manifest sidecar** covering every artifact above; store in the Control 1.7 evidence bucket with WORM retention (Control 1.9 Data Retention and Deletion Policies).

Only after the evidence pack is sealed and hashed should the policy be modified. The remediation itself becomes a new evidence item — capture the post-remediation state with the same rigor.

### Compensating controls during a CC degradation

Apply one or more of the following while CC is degraded; document the compensating control in the incident ticket. Do not leave the supervisory gap open:

- **Manually export Exchange + Teams journal items** for the affected user population via an **eDiscovery (Premium) hold and collection** (Control 1.19). This produces a defensible evidence set even when CC is not generating alerts.
- **Tighten DLP for the Copilot location and Exchange/Teams locations** (Control 1.5) — temporarily move Block-by-label rules from `TestWithNotifications` to `Enable` for high-risk content categories (NPI, MNPI, regulated keywords). DLP is preventive at egress; CC is detective on conduct content. They are complementary, not substitutes.
- **Manual supervisory-procedure overlay** — invoke the firm's documented manual supervision procedure for the affected reps (the procedure that pre-dated CC). Most FSI firms still maintain a manual procedure for exactly this contingency; if yours does not, that is a separate finding to escalate.
- **Increase IRM (Insider Risk Management) sensitivity** (Control 1.12) for the affected user population to surface behavioral risk while CC review is degraded. IRM is _user-behavior risk_, not supervisory review — it is a compensating signal, not a substitute.
- **Freeze new Copilot Studio publish actions** (Control 2.1, 2.16) for the affected environments until CC coverage is restored. Do not expand the AI surface during a supervisory degradation.
- **Daily Unified Audit Log search** (Control 1.7) for `CopilotInteraction`, Exchange message-trace, and Teams message activities for the affected users. This produces durable evidence even when CC alerting is degraded; it is **not** a substitute for supervisory review (see §3 anti-pattern).

### Pre-escalation checklist (≥ 12 items)

1. [ ] Tenant ID and cloud confirmed (Commercial / GCC / GCC High / DoD)
2. [ ] **Audit ingestion** verified `True` from an **EXO** session (`Get-AdminAuditLogConfig`) — the IPPS value can be cached / stale
3. [ ] **License entitlement** verified for every reviewer and every in-scope user (E5 / E5 Compliance / Purview Suite as applicable; per-user M365 Copilot license verified for Copilot-scoped policies via `Get-MgUserLicenseDetail`)
4. [ ] **Reviewer Exchange Online mailbox** present for every reviewer (a reviewer without an EXO mailbox cannot receive notifications and may not be able to open message bodies)
5. [ ] **Per-policy reviewer assigned** for every in-scope policy (role-group membership alone is not sufficient — see §4 Symptom 12)
6. [ ] **Policy enabled** and within its effective scope (locations, direction, user scope, conditions, review percentage)
7. [ ] **Processing window elapsed** — Teams chats may take up to 48 h per Learn (`communication-compliance-channels`); do not conclude "no match" within that window
8. [ ] **Classifier model version recorded** for any classifier-based condition; model bumps invalidate prior baselines
9. [ ] **Sovereign-cloud parity verified** against current Microsoft Learn matrix — Communication Compliance availability and feature parity in GCC High / DoD lag Commercial; record gaps
10. [ ] **PAYG billing enabled** for non-M365 AI sources in scope (Copilot in Fabric, Security Copilot, Copilot Studio Copilots, connected external AI apps, "Other AI apps") — without PAYG the scope returns zero silently
11. [ ] **Evidence preserved** per the §1 evidence list; SHA-256 sidecars captured; manifest stored in Control 1.7 evidence bucket
12. [ ] **Scope and Administrative Unit** verified — restricted-AU admins see only scoped users / data; an investigator opening the page from the wrong AU may see "no alerts" while alerts exist for an unrestricted admin
13. [ ] **Pseudonymization status documented** — if pseudonymization is off, the opt-out justification, approver, and date are recorded in the privacy register; if on, no investigator should be seeing raw user names without an explicit opt-in audit
14. [ ] **User-reported messages reviewer assignment audited** — default reviewers are `Communication Compliance Admins` (or Global Admin if that role group is empty); for FSI, reassign to a privacy-cleared reviewer set immediately on tenant provisioning (see §3)
15. [ ] **Reviewer notification email** delivered (check EXO message trace for the reviewer mailbox; check that the alert-notification toggle is on per policy)
16. [ ] **Compliance + Legal notified** per severity matrix; Privacy notified for any pseudonymization-related or NPI-related event

---

## §2 — Decision matrix: CC vs IRM vs eDiscovery vs DLP

The single most common cause of misdirected investigation in FSI is reaching for the wrong Purview solution. Use this matrix to route a symptom to the **correct** control before you start configuring anything.

| Symptom / question | Use **DLP (1.5)** | Use **CC (1.10)** | Use **IRM (1.12)** | Use **eDiscovery (1.19)** |
|---|---|---|---|---|
| Prevent NPI / regulated content from being sent or processed by Copilot at egress | ✅ Authoritative — preventive enforcement plane | ⚠️ Detective only; will flag, not block | ❌ | ❌ |
| Supervisory review of conduct content for FINRA-supervised reps | ❌ | ✅ Authoritative — supervisory review plane | ❌ | ⚠️ Useful for collection but not for routine supervision |
| Behavioral risk score for an individual user (cumulative risky activity) | ❌ | ❌ | ✅ Authoritative — user behavioral risk plane | ❌ |
| Legal hold + collection of communications for litigation / regulatory inquiry | ❌ | ❌ | ❌ | ✅ Authoritative — discovery + hold plane |
| Detect inappropriate language / harassment in Teams or Viva Engage | ❌ | ✅ (`Detect inappropriate text` / `Inappropriate content` / `Inappropriate images` templates) | ⚠️ Indicator into IRM but not the review plane | ❌ |
| Detect prompt-injection / protected-material classifier hits in M365 Copilot | ❌ | ✅ (`Detect Microsoft 365 Copilot and Microsoft 365 Copilot Chat interactions` template — Prompt Shields, Protected material classifiers) | ❌ | ❌ |
| Off-channel communications supervision for personal device / unmanaged channel | ⚠️ Endpoint DLP can block known apps | ✅ Where ingested via a data connector or where in-scope channel coverage applies | ⚠️ IRM signals can supplement | ⚠️ Hold only |
| Long-horizon (> 180 d) preservation of supervisory review evidence | ❌ | ⚠️ CC retains review records while policy is in place — **not** WORM and **not** an SEC 17a-4 records mechanism | ❌ | ⚠️ Hold + collection, not a retention substitute |
| Records-retention compliance under SEC 17a-4(b)(4) | ❌ | ❌ — see §3 anti-pattern on Policy Match Preservation | ❌ | ❌ — pair with Records Management (Control 1.9) |

### When two apply (worked examples)

- **Customer NPI surfaced in a Teams chat between reps.** DLP (1.5) should have blocked the egress; CC (1.10) catches the supervisory exposure; IRM (1.12) elevates the sender's risk score. Open a CC alert AND verify the DLP rule did not silently mis-fire — both controls are evidence in the same incident.
- **Possible insider trading discussed in M365 Copilot Chat.** CC (1.10) supervisory review surfaces it; eDiscovery (1.19) preserves and collects it for legal; IRM (1.12) elevates the sender's risk score. CC is the trigger; eDiscovery is the preservation mechanism for legal hold.
- **Reviewer leaves the firm mid-investigation.** Snapshot reviewer assignments per §1 BEFORE replacing — the prior reviewer's identity and decisions are part of the supervisory record (FINRA 3110/4511) and may be discoverable under eDiscovery (1.19).

---

## §3 — Anti-patterns (do not do)

| Anti-pattern | Why it's wrong | What to do instead |
|---|---|---|
| Treating an empty Pending queue as a PASS | Silent-zero-row trap. Empty can mean "no violations" OR "policy off / mis-scoped / processing window not elapsed / classifier model bumped / PAYG off / reviewer AU-restricted" | Assert a **deterministic positive event**: send a known-match test message from an in-scope user; verify it appears in Pending within the documented processing window; record artifact |
| Tuning policy settings during an active investigation | Mutates the evidence the investigation depends on; auditor cannot reconstruct what was in scope at the time of the alert | Snapshot per §1 first; tune in a clone or after the investigation closes; document the change in a separate ticket |
| Leaving the **User-reported messages** policy default reviewers as `Communication Compliance Admins` (or Global Admin) | Per Learn, that is the default; in FSI it is a **privacy violation** because user-reported messages can contain protected-class information that must not be visible to unscoped admins | Immediately reassign reviewers on tenant provisioning to a **privacy-cleared, named reviewer set**; document the reassignment in the privacy register |
| Using `Search-UnifiedAuditLog -RecordType CopilotInteraction` as evidence of CC supervisory review | `CopilotInteraction` audit rows prove the **interaction occurred**; they do **not** prove a reviewer reviewed the interaction. Supervisory review under FINRA 3110 is the reviewer's documented action, not the existence of the underlying record | Use the CC policy export, reviewer-decision history, and per-alert remediation actions as supervisory-review evidence; pair with audit (Control 1.7) for the underlying message |
| Pseudonymization opted off without an audit trail | Per Learn, pseudonymization is **on by default**; turning it off without a documented privacy-register entry exposes raw user names to investigators and breaks the privacy-by-design model that CC is built on | Treat pseudonymization changes as evidence-bearing; require approver, date, justification, and review cadence; capture before/after screenshots |
| Sampling instead of 100% review for FINRA-supervised registered representatives without a documented basis | The Learn-documented `Detect financial regulatory compliance` template defaults to **10% review** — that default is **not** appropriate for FINRA-supervised reps without a documented sampling methodology and supervisory plan | Use 100% review for the Copilot template (default) and Conflict-of-interest template (default); document any sampling deviation under FINRA 3110 procedures |
| Treating Policy Match Preservation as the records-retention mechanism for SEC 17a-4 | CC retains copies of analyzed messages **for as long as the policy is in place** (Learn `communication-compliance-channels`); it is not WORM, not non-rewriteable, and is **deleted with the policy**. SEC 17a-4(b)(4) requires non-rewriteable, non-erasable retention for the required period | Pair CC with Records Management retention labels (Control 1.9) and an evidence export pipeline (Control 1.7) for SEC 17a-4 obligations; document the integration in the records-retention schedule |
| Concluding "no match" within the Teams 48-hour processing window | Per Learn, Teams chats matching CC policy conditions may take up to 48 h to process; non-M365 AI sources can take longer | Wait the documented window before declaring a negative; record the message UTC and the assessment UTC |
| Attempting CC policy CRUD via PowerShell | Per Learn (`communication-compliance-policies`), PowerShell is **not supported** for creating or managing CC policies. Any "fix" script that purports to mutate CC policy is wrong by construction | Perform all policy CRUD in the Microsoft Purview portal; if you need automation, use the documented Power Automate flows for **remediation actions on alerts** (a different surface) |
| Removing or replacing a reviewer mid-investigation without preserving the prior reviewer-assignment snapshot | The reviewer's identity, assignment window, and decisions are part of the supervisory record; replacing them without snapshotting destroys the chain of custody | Snapshot per §1 BEFORE replacement; attach the prior reviewer's decision history to the incident ticket |
| Disabling a policy as remediation before snapshotting its configuration | The disable action itself can clear in-flight alerts from the Pending queue and changes the evidence baseline | Snapshot per §1 first; if disable is required, capture the post-disable state too |
| Using the **`Inappropriate content`** template for Copilot scope | Per Learn `communication-compliance-policies`, the `Inappropriate content` template locations are **Microsoft Teams and Viva Engage only**, with Hate / Violence / Sexual / Self-harm classifiers — it does **not** cover M365 Copilot. Using it for Copilot scope produces a silent zero | Use the **`Detect Microsoft 365 Copilot and Microsoft 365 Copilot Chat interactions`** template (location: M365 Copilot + Copilot Chat; Prompt Shields + Protected material classifiers; 100% review by default) |
| Mistaking IRM behavioral signals for supervisory review | IRM is user-behavior risk (Control 1.12); CC is supervisory review of conduct content. They have different review queues, different reviewers, different evidence, and different regulatory framings | Keep them separate; cross-reference where appropriate but do not treat one as the other |
| Authoring CC policy from a Restricted-AU admin and assuming tenant-wide effect | If the author is AU-restricted, the policy may be scoped to that AU silently; the effective scope can be narrower than intended | Author with an **unrestricted** Communication Compliance Admin; only use AU-restricted authors when AU scoping is the explicit intent |

---

## §4 — Symptom-driven diagnostics

> Format: **Symptom → Likely cause → Diagnostic → Fix → Reference.** Sovereign-cloud variants are called out inline. Do not skip the diagnostic step — fixing without diagnosing is what got you here.

### Symptom 1 — Known test message never creates a match

| Likely cause | Diagnostic | Fix |
|---|---|---|
| Test sender is **out of scope** of the policy's user list | Purview > Communication Compliance > Policies > [policy] > Users in scope; verify sender UPN | Add sender to scope OR send from an in-scope identity |
| **Direction** of the test message does not match the policy direction (Inbound / Outbound / Internal) | Policy > Conditions > Direction; cross-reference with how the test message was sent | Resend in a direction the policy covers; or widen the policy direction with documented approval |
| **Processing window not elapsed** — Teams up to 48 h per Learn (`communication-compliance-channels`); non-M365 AI longer | Record message UTC vs assessment UTC | Wait the documented window before declaring negative |
| Policy in **`TestWithoutNotifications`** or saved-but-not-enabled state | Policy > Status / mode | Move to enabled; allow propagation |
| Review percentage is **< 100%** and the test message was outside the sampled set | Policy > Review percentage | Set 100% for in-scope FINRA-supervised reps; document any sampling deviation |
| Classifier-only condition and the test content is below the classifier confidence threshold | Test with content that previously matched the classifier | Add a deterministic SIT or keyword condition for the test; do not rely on classifier confidence for go/no-go validation |

**Sovereign cloud:** GCC High / DoD may lag on classifier model availability; verify the classifier exists in the cloud before testing.
**Reference:** Microsoft Learn — `communication-compliance-policies`, `communication-compliance-channels`.

### Symptom 2 — Reviewer can see alert count but cannot open the message body

| Likely cause | Diagnostic | Fix |
|---|---|---|
| Reviewer assigned to a role group that **lists alerts but not bodies** (e.g., `Communication Compliance Viewers` — reports only; or `Communication Compliance Analysts` — investigate alerts but cannot view Conversation/Translation tabs) | Cross-reference the reviewer's role group against the Learn permissions table (`communication-compliance-permissions`) | Reassign to `Communication Compliance Investigators` (can view Conversation/Translation tabs) or `Communication Compliance` (full) per the firm's role separation |
| Reviewer assigned at the **role-group level only** but **not as per-policy reviewer** on this policy | Policy > Reviewers list | Add the reviewer as a per-policy reviewer; allow propagation (up to 30 min per Learn) |
| Reviewer is **AU-restricted** and the alert's user is outside their AU scope | Reviewer's AU scope vs alert's user | Use an unrestricted reviewer; or re-scope the AU; document |
| Reviewer's **EXO mailbox** is missing or disabled | EXO recipient lookup | Provision / re-enable mailbox; CC reviewer access requires an active EXO mailbox |

**Sovereign cloud:** Role-group permissions are at parity across clouds; AU support has historically lagged in DoD — verify against current Learn.
**Reference:** Microsoft Learn — `communication-compliance-permissions`.

### Symptom 3 — Teams private / public / shared channel items not captured

| Likely cause | Diagnostic | Fix |
|---|---|---|
| Public/private channel: scoped user is **not a member** of the channel and the policy direction is not `Inbound` for channel coverage | Per Learn, "if any member of the channel is a scoped user within a policy and the **Inbound** direction is configured, all messages sent within the channel are subject to review" | Add direction `Inbound` OR add the user to the channel as scoped member |
| Shared channel with **external** team — only the internal organization's scoped users are covered | Per Learn `communication-compliance-channels` | Document the external-tenant gap; route external-side coverage to the partner tenant's CC posture (out of your control) |
| Modern attachment (`.docx`, `.xlsx`, `.xls`, `.csv`, `.pptx`, `.txt`, `.pdf`) text not extracted | Verify file type is in the supported list per Learn; non-supported types are not extracted | Convert to a supported type for review; do not expect extraction outside the documented list |
| Teams chat propagation up to 48 h | Record UTC | Wait the window |

**Sovereign cloud:** Teams parity is generally close in GCC High; verify any preview channel-type coverage against current Learn.
**Reference:** Microsoft Learn — `communication-compliance-channels`.

### Symptom 4 — Copilot interactions appear under "Other AI apps" but not under "Microsoft Copilot experiences"

| Likely cause | Diagnostic | Fix |
|---|---|---|
| Policy was built from a **non-Copilot template** (e.g., `Inappropriate content`) — that template's location is Teams + Viva Engage, not Copilot. The CC `Other AI apps` category is browser-detected via Defender for Cloud Apps catalog and is unrelated to the M365 Copilot scope | Confirm template used and locations selected on the policy | Create a new policy from `Detect Microsoft 365 Copilot and Microsoft 365 Copilot Chat interactions`; do not retrofit a Teams template |
| User license does not include M365 Copilot | `Get-MgUserLicenseDetail` | Assign Copilot license; document gap |
| PAYG enabled for non-M365 AI but the user's M365 Copilot interactions are routed to a Copilot Studio Copilot (which is a non-M365 AI source) | Cross-reference the agent surface against Learn's `Microsoft Copilot experiences` vs `Enterprise AI apps` vs `Other AI apps` definitions | Confirm the source category; add the correct policy template (Copilot Studio Copilots fall under non-M365 AI sources and require PAYG) |

**Sovereign cloud:** Copilot scope availability in CC lags in GCC High / DoD; verify per current Learn before promising coverage.
**Reference:** Microsoft Learn — `communication-compliance-channels` (Generative AI section).

### Symptom 5 — OCR text not extracted from attachments

| Likely cause | Fix |
|---|---|
| OCR not enabled in CC global settings | Communication Compliance > Settings > enable OCR; allow propagation |
| Image quality below threshold or unsupported image format | Verify the format is supported per current Learn; re-test with higher-quality sample |
| Attachment over the supported size limit | Verify size limit on current Learn; surface large-file gap as a known limitation |
| Image embedded in a Teams modern attachment that itself is not in the supported file list | Confirm container file type is in the supported modern-attachment list |

**Sovereign cloud:** OCR availability in DoD has historically lagged; verify per current Learn.
**Reference:** Microsoft Learn — `communication-compliance-feature-reference` (verify; if 404, use `communication-compliance` index).

### Symptom 6 — Non-English messages need translation

| Likely cause | Fix |
|---|---|
| Reviewer role group does not include `Conversation` and `Translation` tab access (e.g., `Communication Compliance Analysts`) | Reassign to `Communication Compliance Investigators` or `Communication Compliance` per Learn permissions table |
| Translation feature not enabled in tenant region | Verify per current Learn; document if unavailable |
| Language not in the supported translation list | Verify supported languages on current Learn; document unsupported languages as a known gap; supplement with manual translation in the supervisory record |

**Sovereign cloud:** Translation availability in GCC High / DoD lags; verify per current Learn.
**Reference:** Microsoft Learn — `communication-compliance-investigate-remediate`, `communication-compliance-permissions`.

### Symptom 7 — False-positive spike after classifier model update

| Likely cause | Diagnostic | Fix |
|---|---|---|
| Microsoft published a classifier model update; the classifier behaves differently than the prior baseline | Compare alert volume week-over-week; check the classifier name in alert details against the recorded baseline classifier model version | Re-baseline the classifier; document the model-version change in the supervisory record; **do not** silently re-tune the policy without preserving the prior baseline (auditor needs to see what changed and when) |
| Tuning that previously suppressed a class of alerts no longer applies under the new model | Review tuning rules / exclusions | Re-validate exclusions; re-test against the prior known-match corpus |

**Sovereign cloud:** Classifier model rollout cadence may differ in sovereign clouds; record cloud-specific model versions.
**Reference:** Microsoft Learn — `communication-compliance-feature-reference` (classifiers section); supervisory-record template in Control 2.12.

### Symptom 8 — Historical matches disappeared due to Policy Match Preservation expiry

| Likely cause | Diagnostic | Fix |
|---|---|---|
| Policy was **deleted** — per Learn, deleting a CC policy deletes the copies of messages associated with it | Audit-log search for policy deletion event; reconcile against the policy export captured before deletion (you did capture it per §1, right?) | Restore from the pre-deletion evidence pack and the Records Management retention pipeline (Control 1.9); CC is **not** the SEC 17a-4 records mechanism — see §3 |
| Reviewer cleared / resolved alerts past the firm's review-record retention | Cross-reference with retention schedule | Re-export the policy CSV; pair with eDiscovery (Control 1.19) hold for the relevant period |

**Sovereign cloud:** Behavior is at parity; the records-retention substrate is the same.
**Reference:** Microsoft Learn — `communication-compliance-channels` (retention section); Control 1.9 Data Retention and Deletion Policies; Control 1.19 eDiscovery.

### Symptom 9 — External / non-Microsoft source delayed or appears out of scope

| Likely cause | Fix |
|---|---|
| **PAYG billing not enabled** in Azure subscription — non-M365 AI sources silently produce zero | Enable Purview PAYG; allow propagation; re-validate with deterministic test |
| Source ingested via a **Microsoft data connector** that is in a delayed or failed state | Purview > Data Map / Connectors; check connector health and last-sync timestamp |
| `Other AI apps` category — relies on Defender for Cloud Apps browser-activity detection; affected user's device is not onboarded or browser extension missing | Verify Defender for Cloud Apps coverage on the device class; push browser extension via Intune |
| External email / chat ingested via a third-party connector — connector schema mismatch | Verify connector schema against current Learn; do not assume internal CC behavior maps to external connectors 1:1 |

**Sovereign cloud:** PAYG availability and connector parity differ in GCC High / DoD; verify per current Learn before relying on non-M365 AI scope.
**Reference:** Microsoft Learn — `communication-compliance-channels` (Generative AI), `purview-billing-models`.

### Symptom 10 — "Encrypted email" symptom that actually belongs to OME / Message Encryption

| Likely cause | Fix |
|---|---|
| Message is encrypted with **Office Message Encryption (OME)** / Microsoft Purview Message Encryption — CC analyzes content **after** transport-level handling; encryption-related visibility issues belong to the OME control, not CC | Triage to OME / Message Encryption configuration; verify the message was actually delivered and indexed; do not assume CC failure |
| Message has a sensitivity label with encryption applied; CC analyzes content but reviewer perception of "encrypted" may reflect label-driven rights, not CC visibility | Verify the label rights and the reviewer's role group access; CC reviewer access is governed by role group, not label |
| Inbound encrypted email from external sender — content may not be decrypted for CC analysis | Document the external-encryption gap; route via DLP at the gateway or via a documented decryption pipeline |

**Sovereign cloud:** OME parity differs slightly in DoD; verify per current Learn.
**Reference:** Microsoft Learn — Office Message Encryption documentation (out of scope for this control); Control 1.5 DLP.

### Symptom 11 — GCC High parity gap mistaken for break/fix

| Likely cause | Fix |
|---|---|
| Feature in question is **not yet available** in GCC High / DoD; engineer assumed parity with Commercial and opened a "broken" ticket | Cross-reference current Microsoft Learn US Government cloud service description against the feature; record the gap in the deviation register |
| Portal hostname is wrong — engineer is hitting `purview.microsoft.com` on a `.us` tenant and getting a silently-different scope | Use `purview.microsoft.us` (GCC High) or the documented DoD hostname per current Learn; never `.com` on a `.us` tenant |
| PowerShell endpoint is wrong cloud (`-ExchangeEnvironmentName` mismatch) | Use `O365USGovGCCHigh` / `O365USGovDoD` / `O365USGovGCC` per cloud |

**Reference:** Microsoft Learn — Service Description for US Government clouds (verify against current page).

### Symptom 12 — Per-policy reviewer present in role group but cannot view alerts

| Likely cause | Diagnostic | Fix |
|---|---|---|
| Reviewer is in `Communication Compliance Investigators` (or similar) role group but was **not added as a per-policy reviewer** on this specific policy | Policy > Reviewers list — confirm the named reviewer | Add as per-policy reviewer; allow up to 30 min per Learn for permission propagation |
| Up to 30 min permission propagation has not elapsed since role-group change | Compare role-group change UTC to test UTC | Wait the documented window |
| Reviewer is AU-restricted and the policy / alert user is outside their AU | Reviewer AU vs alert user | Re-scope or use unrestricted reviewer |

**Sovereign cloud:** Permission propagation behavior is at parity; AU support varies — verify per current Learn.
**Reference:** Microsoft Learn — `communication-compliance-permissions`.

### Symptom 13 — Pseudonymization on but investigator sees raw user names without opt-in audit

| Likely cause | Diagnostic | Fix |
|---|---|---|
| **Show usernames** has been toggled by the investigator without an opt-in audit trail | Communication Compliance > Privacy settings; audit-log search for the toggle event; reviewer identity that performed it | Re-enable pseudonymization; require opt-in via documented privacy procedure (named approver, justification, time-bound); capture before/after evidence; treat as a SEV-2 privacy event under §1 |
| Reviewer has been granted a role group that bypasses pseudonymization (e.g., escalated to a role with full identity access) | Cross-reference role group | Reassign to least-privilege role group consistent with the investigation's needs |
| Pseudonymization was disabled at tenant level historically without a documented change | Settings audit | Document the historical change; restore default; raise to Privacy + Compliance |

**Sovereign cloud:** Behavior is at parity; the privacy obligations are jurisdictional (state breach laws may apply to mishandling).
**Reference:** Microsoft Learn — `communication-compliance` (Privacy by design); Control 2.12 supervision.

### Symptom 14 — PAYG not enabled — non-M365 AI scope silently produces zero matches

| Likely cause | Diagnostic | Fix |
|---|---|---|
| **Pay-as-you-go billing not enabled** in the Azure subscription backing Purview — per Learn, PAYG is required to detect inappropriate or risky interactions for non-M365 AI data (Copilot in Fabric, Security Copilot, Copilot Studio Copilots, connected external AI apps) | Azure portal > Cost Management + Billing; Purview billing model state | Enable Purview PAYG; allow propagation; re-validate with a deterministic test from an in-scope user against an in-scope source |
| Engineer assumed M365 Copilot pricing covers non-M365 AI (it does not) | Cross-reference billing model against scope | Document the billing dependency in the deployment runbook |

**Sovereign cloud:** PAYG availability differs across clouds — verify per current Learn before promising non-M365 AI scope.
**Reference:** Microsoft Learn — `purview-billing-models`, `communication-compliance-channels` (Generative AI section).

### Symptom 15 — Reviewer notification email never delivered

| Likely cause | Fix |
|---|---|
| Reviewer EXO mailbox missing / disabled | Provision / re-enable |
| Notification toggle off on the policy | Policy > Notifications > enable |
| Mail flow blocked by a transport rule (Exchange Online) | Message trace from the CC notification sender to the reviewer mailbox; remove blocking rule |
| Reviewer in a recipient block list / quarantine | Remove from block list; release from quarantine |

**Sovereign cloud:** EXO mail flow at parity across clouds; verify connector configuration in GCC High / DoD.
**Reference:** Microsoft Learn — `communication-compliance-investigate-remediate`.

---

## §5 — Sovereign cloud notes (summary)

| Capability | Commercial | GCC | GCC High | DoD |
|---|---|---|---|---|
| Communication Compliance core (policy, alerts, role groups) | ✅ GA | ✅ | ✅ (verify per Learn) | ✅ (verify per Learn) |
| `Detect Microsoft 365 Copilot and Microsoft 365 Copilot Chat interactions` template | ✅ | ⚠️ Verify per Learn | ⚠️ Lagging — verify per Learn | ⚠️ Lagging — verify per Learn |
| Non-M365 AI sources (Copilot in Fabric, Security Copilot, Copilot Studio Copilots, connected external AI) — requires PAYG | ✅ | ⚠️ Verify PAYG availability | ⚠️ Lagging | ⚠️ Lagging |
| `Other AI apps` (Defender for Cloud Apps browser-detected) | ✅ | ⚠️ Verify | ⚠️ Lagging | ⚠️ Lagging |
| OCR / Translation | ✅ | ✅ (verify language list) | ⚠️ Verify | ⚠️ Lagging |
| Administrative units in CC | ✅ | ✅ | ✅ (verify per Learn) | ⚠️ Verify |
| Pseudonymization (default on) | ✅ | ✅ | ✅ | ✅ |
| Power Automate flows on alerts | ✅ | ✅ | ⚠️ Verify | ⚠️ Verify |
| Portal hostname | `purview.microsoft.com` | `compliance.microsoft.com` | `purview.microsoft.us` | `purview.apps.mil` (verify current) |

Document any sovereign-cloud exception in the control's deviation register; re-check on each Microsoft Learn refresh.

---

## §6 — Escalation

### L1 — Communication Compliance Admin (within 1 h SEV-1; 4 h SEV-2)

- Preserve evidence per §1
- Run pre-escalation checklist (≥ 12 items)
- Apply documented compensating controls; do not leave the supervisory gap open

### L2 — AI Governance Lead + Privacy Officer (within 1 h SEV-1)

- Triage cross-control impact (1.5 DLP, 1.7 Audit, 1.9 Records, 1.12 IRM, 1.19 eDiscovery, 2.12 Supervision)
- Privacy review for any pseudonymization-related, NPI-related, or user-identity-related event

### L3 — CISO + Compliance Officer + Legal (within 1 h SEV-1)

- Reportability determination per §1 decision tree
- Decide regulator notification path (FINRA / SEC / NYDFS / state AGs / OCC / Fed / CFTC) — this is **their** decision, not Engineering's

### L4 — Microsoft support ticket

Use this payload template when opening the Microsoft support ticket (paste into the description verbatim and fill the bracketed fields):

```
Severity: [SEV-1 | SEV-2 | SEV-3]
Tenant ID: [GUID]
Cloud: [Commercial | GCC | GCC High | DoD]
Affected workload: Microsoft Purview Communication Compliance
Affected scope: [policy name(s); user count; channel(s); UTC window start–end]
Symptom: [one-line description, e.g., "CC policy 'Reps-Copilot-Supervision' producing zero matches since 2026-04-12T14:00Z despite known-match test message at 2026-04-12T15:30Z; outside Teams 48h processing window."]
Business impact: Supervisory review degradation for [N] FINRA-supervised registered representatives; potential FINRA Rule 3110(b) supervisory-system gap; firm is in [active examination | quarter-end review | none].
Evidence pack: [reference to internal evidence ID; offer to share artifacts under NDA]
Steps already taken: [pre-escalation checklist items 1–16 confirmed; compensating controls in place: eDiscovery hold on affected users (Control 1.19), DLP tightened on Copilot location (Control 1.5)]
Engineer of record: [name, role, email, phone, time zone]
Compliance contact: [name, role, email]
```

### L5 — Internal Compliance / Legal escalation template

Use this payload when handing off to internal Compliance and Legal (separate from the Microsoft support ticket):

```
To: Compliance Officer; General Counsel; Privacy Officer; CISO
From: [AI Governance Lead]
Severity: [SEV-1 | SEV-2]
Subject: Communication Compliance supervisory-review degradation — [date]

1. What happened
   - [Plain-language description, no jargon]
   - Affected user population: [N FINRA-supervised reps in BU X; Y registered investment advisers in BU Y]
   - UTC window: [start – end]

2. Possible regulatory exposure (§1 reportability triage)
   - FINRA Rule 3110(b) supervisory system: [yes / unclear / no — Compliance to confirm]
   - FINRA Rule 4511 / SEC 17a-4(b)(4) books-and-records: [yes / unclear / no]
   - GLBA 501(b) / SEC Reg S-P: [if NPI in scope]
   - SOX 302/404 ICFR: [if financial-disclosure communications in scope]
   - Other: [NYDFS 23 NYCRR 500 72-hour determination; OCC Bulletin 2026-13 / Fed SR 26-2; CFTC 1.31; FINRA 4530]

3. Evidence preserved (§1)
   - Policy export, role-group snapshot, reviewer-assignment snapshot, Pending-queue screenshot,
     audit-search export, classifier model version, PAYG state, sovereign-cloud parity confirmation,
     SHA-256 manifest. Stored in Control 1.7 evidence bucket reference [ID].

4. Compensating controls in place
   - [eDiscovery (Control 1.19) hold on affected users at UTC X]
   - [DLP (Control 1.5) Copilot rules moved from TestWithNotifications to Enable for NPI / MNPI categories]
   - [Manual supervisory procedure invoked per firm playbook section X.Y]
   - [IRM (Control 1.12) sensitivity elevated for affected user population]

5. Open questions for Compliance / Legal
   - Reportability determination (per §1 tree)
   - Customer-notification timeline if NPI in scope (SEC Reg S-P)
   - Examiner-disclosure obligation if firm is in active examination

6. Next status update: [UTC]
```

---

## §7 — Cross-links

- [Control 1.10 Communication Compliance Monitoring](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md) — control of record
- [Control 1.10 Portal Walkthrough](portal-walkthrough.md)
- [Control 1.10 PowerShell Setup](powershell-setup.md) — note the Learn-documented constraint that PowerShell is not supported for CC policy CRUD
- [Control 1.5 DLP and Sensitivity Labels](../1.5/troubleshooting.md) — preventive enforcement plane; compensating control during CC degradation
- [Control 1.7 Audit](../1.7/troubleshooting.md) — durable evidence backbone; pair with CC for SEC 17a-4 evidence
- [Control 1.9 Data Retention and Deletion Policies](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md) — the records-retention mechanism for SEC 17a-4(b)(4); CC is not a substitute
- [Control 1.12 Insider Risk Management](../1.12/troubleshooting.md) — user behavioral risk plane; complementary to CC
- [Control 1.19 eDiscovery](../1.19/troubleshooting.md) — legal hold + collection; compensating control during CC degradation
- [Control 2.12 Supervision and Manual Review](../2.12/troubleshooting.md) — supervisory procedures, sampling methodology, supervisory-record template

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
