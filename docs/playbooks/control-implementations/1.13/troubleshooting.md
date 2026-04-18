# Control 1.13 — Troubleshooting & Incident Response: Sensitive Information Types and Pattern Recognition

**Parent control:** [1.13 Sensitive Information Types (SITs) and Pattern Recognition](../../../controls/pillar-1-security/1.13-sensitive-information-types-sits-and-pattern-recognition.md)
**Audience:** SOC L1 / DLP analysts, Purview Compliance Admin, Purview Info Protection Admin, Purview Data Security AI Admin, Security Engineering, Compliance & Legal liaisons.
**Last UI verified:** April 2026 (Microsoft Purview portal — `purview.microsoft.com` for Commercial; `purview.microsoft.us` for GCC / GCC High / DoD).
**Scope:** Diagnostic, remediation, and incident-handling guidance for Microsoft Purview Sensitive Information Types (built-in, custom regex, EDM, Named Entities), Trainable Classifiers used as SITs, and their consumption by DLP, Auto-labelling, DSPM for AI, Communication Compliance, and Microsoft 365 Copilot / declarative agents.

> **READ §1 FIRST.** A SIT misfire that allows NPI / PCI / PHI / MNPI to flow into a Copilot grounding result, an outbound email, an external SharePoint share, or a third-party agent connector is a **potential reportable incident** under NY DFS 23 NYCRR 500.17(a) (72-hour determination clock), SEC Reg S-P §248.30(a)(4) (≤30-day customer notice where triggered), FINRA Rules 4530 / 3110 / 4511, GLBA 501(b), and (for trainable-classifier model-risk drift) OCC Bulletin 2011-12 / Federal Reserve SR 11-7. **Do not** begin tuning, deleting, or republishing the SIT, EDM schema, or trainable classifier until evidence is preserved per §1.3 and Compliance/Legal has issued a reportability determination per §1.2. Reportability is a **Compliance/Legal call, not an engineering call** — this playbook supports that determination; it does not make it.

---

## 1. FSI Incident Handling — READ FIRST

This section governs how a SIT-related anomaly is triaged, contained, and (where required) reported. It applies whether the trigger is (a) a DLP rule that fired on data that should not have matched (false positive), (b) a DLP rule that **failed** to fire on data that should have matched (false negative — the higher-risk case), (c) a Copilot or agent response that surfaced data the SIT was supposed to gate, or (d) drift in a Trainable Classifier used in a DLP / Auto-label policy.

### 1.1 Severity Matrix (Zone-aware)

| Severity | Trigger conditions | Zone applicability | Initial responder | Containment SLA |
|----------|--------------------|--------------------|--------------------|-----------------|
| **SEV-1** | Confirmed exposure of NPI / PCI cardholder data / PHI / MNPI to an unauthorized external party, an unmanaged tenant, or a public surface; **or** Copilot / agent response in any zone returned regulated data the SIT was configured to detect; **or** EDM hash table or unsalted source data exposed | All zones; **automatic SEV-1 if Zone 3 (Enterprise)** or any agent-mediated exposure | SOC L1 → immediate page to Purview Info Protection Admin + CISO duty officer + Compliance/Legal | ≤ 1 hour to contain; reportability determination ≤ 24 h, within the NY DFS 72-h clock |
| **SEV-2** | Confirmed false negative on a published SIT that protects regulated data, **internal** exposure only, no agent path; **or** Trainable Classifier accuracy drift > 10 percentage points from baseline; **or** EDM refresh failure > 24 h on a schema backing an active DLP rule | Zone 2 (Team) and Zone 3 (Enterprise) primary; Zone 1 (Personal) if SIT covers regulated data | Purview Compliance Admin + DLP analyst | ≤ 4 hours to contain; reportability assessment ≤ 72 h |
| **SEV-3** | Sustained false-positive volume above the agreed false-positive ceiling (e.g., > 5% of matches over a rolling 7-day window) on a regulated-data SIT, causing analyst fatigue or business workflow blockage | All zones | DLP analyst + control owner | ≤ 5 business days |
| **SEV-4** | Single-instance false positive; a built-in SIT confidence threshold is suboptimal but no regulated data is mishandled; documentation or naming gap | All zones | DLP analyst | Next backlog cycle |

> A SEV-3 or SEV-4 finding **escalates to SEV-2 or SEV-1** the moment evidence shows the same pattern likely allowed regulated data through a Copilot, agent, external email, or external share path. Re-triage on every new piece of evidence; do not anchor on the first call.

### 1.2 Reportability Decision Tree (top-down — stop at first match)

Run this tree **before** changing the SIT, regardless of severity. The output is an evidence package handed to Compliance/Legal; the engineering team does not unilaterally classify an incident as reportable or non-reportable.

1. **Did the failure cause, or is it likely to have caused, unauthorized acquisition of customer NPI?**
   - Yes → Engage Compliance/Legal for **GLBA 501(b)** Safeguards assessment and **SEC Regulation S-P §248.30(a)(4)** customer-notification analysis (≤ 30-day clock from determination of misuse / reasonable likelihood of misuse). For NY-licensed entities also engage the **NY DFS 23 NYCRR 500.17(a)** 72-hour determination workflow.
2. **Is the affected entity a registered broker-dealer, investment adviser, or member firm, and does the failure implicate communications recordkeeping, supervision, or a reportable event?**
   - Yes → Compliance to evaluate **FINRA Rule 4530** (problem reporting), **FINRA Rule 3110** (supervision), **FINRA Rule 4511 / SEC Rule 17a-4** (books-and-records / WORM retention impact). FINRA Notice 25-07 reinforces that AI-mediated communications fall within these obligations.
3. **Did the failure cross a Copilot, declarative agent, Copilot Studio agent, or third-party connector boundary?**
   - Yes → Add **Pillar 4** AI-incident path (parallel to this playbook): preserve `CopilotInteraction` and `AiAppInteraction` audit records, agent-execution logs, plugin/connector identities, and the prompt+response pair (redacted hashes only — never store the raw regulated payload outside Compliance/Legal custody).
4. **Did the failure involve a Trainable Classifier whose drift could be characterized as model performance degradation?**
   - Yes → Engage Model Risk Management under **OCC Bulletin 2011-12** and **Federal Reserve SR 11-7**: capture training-set version, last validation date, accuracy/precision/recall baseline vs. current, and the FSI Governance Gate approval record from the parent control (1.13 §3).
5. **Did cardholder data (PAN) potentially leave the cardholder data environment or enter a non-PCI surface (Copilot index, unmanaged tenant, external share)?**
   - Yes → **PCI DSS 12.10** incident-response procedures; notify the PCI ISA / QSA per the firm's PCI IR plan.
6. **Could the failure have allowed disclosure of MNPI across an information barrier or to a non-wall-side recipient?**
   - Yes → Information-Barrier owner + Compliance immediately; capture the IB segment configuration in effect at the time and the user/group memberships; preserve under **CFTC Rule 1.31** (or SEC equivalent) records-preservation requirements.
7. **None of the above, and the data class is non-regulated, non-confidential business data?**
   - Document, remediate, and close per §5 L1 path. Still preserve evidence for 90 days per the parent control's audit-retention requirement.

> Every "Yes" path requires the §1.3 evidence package **before** any SIT, EDM schema, or trainable-classifier change.

### 1.3 Evidence Preservation (capture before remediation)

Capture all of the following into a single evidence bundle, generate a SHA-256 manifest, and store the bundle in the firm's e-discovery / legal-hold repository. **Do not** modify the SIT or any consuming policy until items 1–10 are captured.

1. SIT identity: `Identity`, `Name`, `Type` (Builtin / Custom / EDM / NamedEntity / TrainableClassifier-as-classifier), `Publisher`, `RulePackId`, `Version`, `WhenChanged` — from `Get-DlpSensitiveInformationType -Identity "<name>" | Format-List *`.
2. Full SIT XML (custom and EDM): export via `Get-DlpSensitiveInformationTypeRulePackage -Identity "<RulePackId>" | Select -Expand SerializedRulePackage`.
3. EDM schema definition (where applicable): `Get-DlpEdmSchema -Identity "<schema>" | Format-List *` plus the last successful upload manifest hash from EdmUploadAgent logs at `%LOCALAPPDATA%\Microsoft\EdmUploadAgent\Logs\`.
4. List of every DLP policy and rule consuming the SIT: `Get-DlpComplianceRule | Where-Object { $_.AdvancedRule -match "<sit-name-or-guid>" -or $_.ContentContainsSensitiveInformation -match "<sit-name>" }` and the parent `Get-DlpCompliancePolicy` records.
5. List of every Auto-label policy / retention policy / Information Protection policy consuming the SIT: `Get-LabelPolicy`, `Get-AutoSensitivityLabelPolicy`, `Get-AutoSensitivityLabelRule`.
6. Audit evidence window (T-7d → T+1d at minimum): `Search-UnifiedAuditLog -StartDate <T-7d> -EndDate <T+1d> -RecordType ComplianceDLPSharePoint,ComplianceDLPExchange,DLPRuleMatch,CopilotInteraction,AiAppInteraction -ResultSize 5000` exported to CSV and hashed.
7. The exact match (or non-match) sample, redacted: keep the regex/EDM evaluation context (token offsets, surrounding 50 chars **redacted**) — never store raw NPI/PCI/PHI/MNPI in the engineering bundle; the unredacted artefact goes only to Compliance/Legal custody.
8. `Test-DataClassification -ClassificationNames "<sit-name>" -TestTextFile <redacted-sample.txt>` output (PowerShell), captured as a transcript.
9. For Copilot/agent paths: the `CopilotInteraction` audit record(s), agent identity (`AgentId`, `AppId`), invoked plugin/connector list, and the Purview DSPM-for-AI activity record from Activity Explorer.
10. For Trainable Classifier paths: classifier identity (`Get-DlpClassifier`), last training date, last validation accuracy, current accuracy from the most recent validation run, and the FSI Governance Gate approval ticket reference.
11. Tenant context: tenant ID, sovereign cloud (Commercial / GCC / GCC High / DoD), Purview SKU, and the licence proof for any Premium-gated feature (EDM, Named Entities, Trainable Classifiers, DSPM for AI) — see the parent control's licence matrix.
12. SHA-256 manifest: `Get-ChildItem <bundle-dir> -Recurse -File | Get-FileHash -Algorithm SHA256 | Export-Csv manifest.csv`. Sign or seal per the firm's evidence-handling policy.

### 1.4 Compensating Controls During Containment

While the SIT/EDM/classifier is under investigation and **before** any change is published, apply one or more of the following compensating controls so the regulated-data path is not left unguarded:

| Compensating control | Where applied | Owner | Notes |
|----------------------|---------------|-------|-------|
| Switch the affected DLP rule from **Audit** or **Notify** to **Block** (or **Block with override = false**) for external recipients / external sharing | Exchange, SharePoint, OneDrive, Teams, Endpoint, Copilot location | Purview Compliance Admin | Reduces blast radius without removing the SIT; preserves evidence flow |
| Add a **broader** SIT (e.g., the OOTB U.S. SSN built-in alongside the failing custom SIT) to the same rule | DLP rule's `ContentContainsSensitiveInformation` | DLP analyst | Accept the higher false-positive rate temporarily; document as a temporary control |
| Enable the **DLP for Microsoft 365 Copilot** location with a Block action restricting Copilot from grounding on the affected SharePoint sites or labels | Copilot DLP location (control 1.5) | Purview Data Security AI Admin | Cuts the agent-mediated exit path while the SIT is investigated |
| Apply a **temporary sensitivity label** (e.g., `Highly Confidential — Investigation Hold`) to the source content set with encryption + co-author-only | Sensitivity Labels | Purview Info Protection Admin | Stops further egress regardless of SIT match |
| Restrict the **Trainable Classifier** from the consuming policies (replace with a deterministic SIT) until re-validated | DLP / Auto-label policies | Purview Data Security AI Admin | SR 11-7 model-risk hygiene; reverts to deterministic detection |
| Enable enhanced **Communication Compliance** policy (control 1.10) over the affected user population | Communication Compliance | Purview Communication Compliance Admin | Adds out-of-band detection layer |

Document every compensating control applied (timestamp, scope, owner, planned removal date) in the incident ticket. Compensating controls **do not** substitute for the §1.2 reportability assessment.

### 1.5 Pre-Escalation Checklist (≥ 15 items — complete before paging L3 or filing with Microsoft Support)

- [ ] §1.3 evidence bundle captured and SHA-256 manifest generated.
- [ ] §1.2 reportability tree run; output handed to Compliance/Legal; ticket reference recorded.
- [ ] §1.4 compensating controls applied; scope and removal date documented.
- [ ] SIT type confirmed (Builtin vs. Custom regex vs. EDM vs. Named Entity vs. Trainable Classifier-as-classifier).
- [ ] SIT confidence level inspected in the Purview portal entity definition — confirmed numeric thresholds are read from this SIT's own definition (Low/Medium/High thresholds are **per-SIT**, not a universal scale).
- [ ] `Test-DataClassification` run against the redacted sample with the suspect SIT identity; transcript saved.
- [ ] Every DLP rule consuming the SIT enumerated; rule-mode (Test / Audit / Block) confirmed.
- [ ] Every Auto-label / retention policy consuming the SIT enumerated.
- [ ] EDM (if applicable): last successful refresh timestamp confirmed within SLA; row count and column count captured; salt file custody confirmed (EDM_DataUploaders membership + key vault reference).
- [ ] Trainable Classifier (if applicable): last validation accuracy/precision/recall captured; drift vs. baseline computed; FSI Governance Gate ticket re-opened.
- [ ] Copilot/agent path checked: `CopilotInteraction` and `AiAppInteraction` audit records pulled for the affected window; DSPM for AI Activity Explorer reviewed.
- [ ] Tenant sovereign cloud and licence SKU confirmed; sovereign endpoint variants (§4) used in all repro commands.
- [ ] Audit-log retention confirmed sufficient to cover the investigation window (Audit Premium / extended retention add-on if required).
- [ ] Change-management ticket opened for any planned SIT / EDM / classifier change; approver = Purview Info Protection Admin minimum.
- [ ] Communication Compliance and Insider Risk owners notified if the population is in-scope.
- [ ] Microsoft Support pre-flight (§7.2) data assembled if escalation to Microsoft Premier is anticipated.
- [ ] Stakeholder communications drafted (template per the firm's IR plan) and held pending the §1.2 determination.

### 1.6 Worked Example — Space-Separated SSN Missed by a Custom SIT, Surfaced via Copilot

The following is illustrative, not a template for any specific firm's playbook.

- **T+0** — A wealth-management associate runs a Microsoft 365 Copilot prompt: "Summarize the onboarding documents for client X." Copilot grounds on a SharePoint document that contains `123 45 6789` (space-separated U.S. SSN). Copilot returns the SSN in the response. The custom SIT `Custom_US_SSN_v3` was authored to match `\d{3}-\d{2}-\d{4}` and `\d{9}` only; the space-separated form was not in the regex. The OOTB U.S. SSN built-in SIT was **removed** from the consuming DLP rule six months earlier as a "false-positive reduction" change.
- **T+5 min** — The associate self-reports via the in-product reporting channel. SOC L1 opens an incident; severity provisionally **SEV-1** because (a) NPI and (b) Copilot path.
- **T+15 min** — §1.3 evidence captured: `CopilotInteraction` audit record, agent identity (Microsoft 365 Copilot — first-party), source SharePoint document URL and label, the custom SIT XML, the consuming DLP rule, and the change-history showing removal of the built-in SIT.
- **T+30 min** — §1.4 compensating controls applied: built-in U.S. SSN SIT re-added to the consuming DLP rule (Block on external + Audit on Copilot location); the source SharePoint site relabeled to `Highly Confidential — Investigation Hold`; Copilot DLP location updated to exclude the site from grounding.
- **T+1 h** — §1.2 reportability tree handed to Compliance/Legal. Outputs: GLBA 501(b) safeguards review opened; Reg S-P 30-day clock noted (determination pending); FINRA 4530 problem-reporting log entry drafted; NY DFS 72-h determination clock started for the licensed NY entity; Pillar 4 AI-incident path opened in parallel.
- **T+4 h** — Root-cause confirmed: the original false-positive-reduction change was approved without a regression test for separator variants and without retaining the OOTB SIT as a safety net. Trainable-classifier drift not implicated.
- **T+24 h** — Permanent fix: SIT XML updated to add `\d{3}\s\d{2}\s\d{4}` and `\d{3}\.\d{2}\.\d{4}` patterns; regression test set expanded; OOTB SIT retained as a co-detector; FSI Governance Gate re-approval recorded; change rolled out to Audit mode for 72 h before Block.
- **T+72 h** — NY DFS determination filed (or not, per Compliance's call). Customer-notification analysis under Reg S-P continues on its own clock.
- **T+ ≤ 30 d** — Customer notice issued where Compliance/Legal determines required; FINRA Rule 4530 quarterly filing updated as appropriate.

This example shows why §1.2 must run **before** the SIT is "fixed" — the change history was itself evidence.

---

## 2. Severity / Decision Matrix — Symptom × Scope × Data Class × Copilot Involvement

Use this matrix to translate an observed symptom into the §6 runbook to execute and the §1.1 severity to assign initially. **Re-triage** as evidence accumulates.

| Observed symptom | Likely failure mode (§6) | Data class | Surface | Copilot/agent involved? | Initial severity |
|------------------|---------------------------|------------|---------|--------------------------|------------------|
| Custom SIT does not match a known-good positive sample | F1 — Regex mismatch / separator gap | Regulated NPI/PCI/PHI | Any | No | SEV-2 |
| Same as above, but the same sample was returned in a Copilot response | F1 + F12 — SIT gap exposed via Copilot grounding | Regulated | SharePoint/OneDrive grounding | Yes | **SEV-1** |
| OOTB built-in SIT (e.g., U.S. SSN) over-matches non-PII strings | F2 — Built-in confidence-threshold mis-tune | Mixed | Any | No | SEV-3 |
| EDM rule did not fire on an exact known-good record | F3 — EDM upload / refresh failure | Customer master / accounts | Any | Either | SEV-2 (SEV-1 if Copilot path) |
| EDM upload exceeds row or column limit | F4 — EDM schema sizing | N/A | EdmUploadAgent | No | SEV-3 |
| Trainable Classifier accuracy fell > 10 pp below baseline | F5 — Classifier drift | Class-dependent | Any | Either | SEV-2 |
| Trainable Classifier never reached publishable accuracy | F6 — Insufficient/biased training corpus | Class-dependent | Pre-prod | No | SEV-3 |
| Named Entity SIT does not match in non-English content | F7 — Locale / language coverage gap | Regulated | Any | Either | SEV-2 |
| DLP rule using SIT does not trigger although `Test-DataClassification` matches | F8 — Policy scope / location / mode mismatch | Any | Any | Either | SEV-2 |
| DLP rule fires but no audit event in `Search-UnifiedAuditLog` | F9 — Audit ingestion / retention gap | Any | Any | Either | SEV-2 |
| Copilot returned data the SIT was supposed to gate, but DLP for Copilot is in Audit mode only | F10 — DLP for Copilot mis-scoped or in Audit | Regulated | Copilot | **Yes** | **SEV-1** |
| Sensitivity label not auto-applied although SIT matches | F11 — Auto-label policy lag / scope / simulation-mode | Any | SharePoint/OneDrive/Exchange | Either | SEV-3 |
| Agent (Copilot Studio / declarative agent) surfaced regulated data via a connector | F12 — Agent connector / plugin bypass | Regulated | Agent | **Yes** | **SEV-1** |
| SIT change deployed without governance approval (drift) | F13 — Change-management bypass | N/A | Purview tenant | N/A | SEV-2 |
| Sovereign-cloud command fails with auth error or 404 | F14 — Sovereign endpoint mismatch | N/A | PowerShell / portal | N/A | SEV-3 |

Re-evaluate severity when (a) a Copilot or agent record surfaces in audit, (b) the affected population includes a regulated user role (e.g., registered representative, wealth advisor), or (c) external recipients or unmanaged tenants are confirmed in the egress path.

---

## 3. Anti-Patterns to Avoid (≥ 14)

These are recurring authoring, deployment, and operational mistakes observed across FSI Purview tenants. Each anti-pattern includes the safer practice.

1. **A1 — Treating SIT confidence as a universal scale.** "Set confidence to 75" is meaningless without naming the SIT. Confidence thresholds (Low / Medium / High and their numeric backing values) are **per-SIT** and are read from the SIT's entity definition. Always open the entity definition (portal: *Information protection → Classifiers → Sensitive info types → \<SIT\> → Edit*) and quote the value in the change ticket.
2. **A2 — Removing OOTB built-in SITs when adding a custom SIT.** Custom SITs almost always have lower recall than the built-ins on day one. Run the custom SIT **alongside** the built-in for at least one regression cycle (and in regulated-data DLP rules, indefinitely) before considering removal. Removing built-ins to "reduce false positives" is a recurring root cause of SEV-1 incidents (see §1.6).
3. **A3 — Authoring custom SIT regex without a separator-variant test set.** A SSN-style regex must cover `-`, ` ` (space), `.`, no-separator, and (where business-relevant) tab and en-dash. Build the test set first; fail the change if any variant is missed. `Test-DataClassification` is your gate.
4. **A4 — Publishing a SIT directly to Block in production.** Always promote Test → Audit → Block over a documented soak period (default 7–14 days at each stage for regulated-data SITs). Direct-to-Block on a noisy SIT creates a self-inflicted DoS on a business workflow and erodes trust in DLP.
5. **A5 — Using a Trainable Classifier in a Block rule without the FSI Governance Gate.** Trainable Classifiers are model-risk artefacts (SR 11-7 / OCC 2011-12). Their use as a hard-block detector requires the FSI Governance Gate sign-off referenced in the parent control (1.13 §3) and a documented validation cadence.
6. **A6 — Ignoring EDM refresh failures.** A silent EDM refresh failure converts a precise, exact-match SIT into stale data within hours. Monitor EdmUploadAgent logs and the Purview portal EDM data-source health pane; alert on > 24 h since last successful refresh on any schema backing a regulated-data DLP rule.
7. **A7 — Storing the EDM source CSV with NPI in a non-EDM-isolated path.** The EDM design assumes the source is hashed and discarded; keeping the cleartext CSV on a network share violates the model and expands the blast radius. Use the EDM Upload Agent on a hardened jump host; restrict the source to a least-privileged path; rotate the salt per policy.
8. **A8 — Editing a SIT directly in production without change control.** Every SIT change is a control change. Require a ticket, a peer review of the XML / regex / EDM schema, a regression run of `Test-DataClassification`, and a 72-h Audit-mode soak before re-enabling Block. Capture the prior version XML for rollback.
9. **A9 — Overlapping SITs without a primary detector strategy.** Layering five overlapping SSN SITs in one rule produces correlated false positives, double-counted match counts, and incident-triage noise. Designate a primary detector per data class; layer additional detectors only with documented intent (e.g., "EDM primary, regex fallback").
10. **A10 — Forgetting the Copilot DLP location.** A SIT that protects SharePoint, OneDrive, and Exchange but is not present in the Microsoft 365 Copilot DLP location leaves the agent grounding path unguarded. For every regulated-data SIT, confirm consumption by control 1.5 (DLP for Microsoft 365 Copilot).
11. **A11 — Over-trusting Named Entity SITs in non-English content.** Named-entity recognition coverage varies by language; non-English customer correspondence may not match. Where the firm operates in non-English markets, validate per-locale and add deterministic SIT fallbacks.
12. **A12 — Authoring SIT regex without anchoring or proximity windows.** Unanchored, greedy regex burns Purview content-scanning compute and produces false positives at scale. Use `\b` word boundaries, bounded quantifiers, and proximity / supporting-element windows where the OOTB definitions do.
13. **A13 — Treating false-positive reduction as an unconditional good.** A reduction in false-positive count that is not paired with a regression run on the known-good positive set is a **silent recall regression**. Track precision **and** recall on every change; gate the change on both.
14. **A14 — Mixing Commercial portal URIs with sovereign tenants.** `purview.microsoft.com` and `https://ps.compliance.protection.outlook.com/...` will fail or, worse, connect to the wrong tenant context. For GCC High use `purview.microsoft.us` and `https://ps.compliance.protection.outlook.us/powershell-liveid`; for DoD use `https://l5.ps.compliance.protection.office365.us/powershell-liveid`. See §4.
15. **A15 — Single-timestamp validation on the SIT only.** A SIT change is not "verified" until every consuming DLP rule, Auto-label policy, and Copilot DLP location has been re-tested. Maintain a consumer matrix per SIT and re-run the test suite on every change.
16. **A16 — Tuning a SIT in response to a single false positive.** One report is anecdote; tuning thresholds on anecdote causes the recall regressions described in A13. Require a minimum sample (e.g., ≥ 20 reviewed matches over ≥ 7 days) before a threshold change.

---

## 4. Sovereign Cloud Variants — Commercial / GCC / GCC High / DoD

SIT and DLP feature parity, portal hostnames, and PowerShell endpoints differ by cloud. Validate **per-feature** parity against current Microsoft Learn before committing a control design that depends on a specific feature, since GCC High and DoD parity is delivered on a feature-by-feature cadence.

| Surface / Feature | Commercial | GCC | GCC High | DoD | Compensating control if absent |
|-------------------|------------|-----|----------|-----|--------------------------------|
| Purview portal hostname | `purview.microsoft.com` | `compliance.microsoft.com` (legacy) → `purview.microsoft.com` per Microsoft's announced cutover | `purview.microsoft.us` | `purview.apps.mil` (verify per current Learn) | Use Compliance portal until parity reached |
| IPPS PowerShell endpoint (`Connect-IPPSSession -ConnectionUri`) | `https://ps.compliance.protection.outlook.com/powershell-liveid` | `https://ps.compliance.protection.outlook.com/powershell-liveid` | `https://ps.compliance.protection.outlook.us/powershell-liveid` (with `-AzureADAuthorizationEndpointUri https://login.microsoftonline.us/common`) | `https://l5.ps.compliance.protection.office365.us/powershell-liveid` (with `-AzureADAuthorizationEndpointUri https://login.microsoftonline.us/common`) | N/A — endpoint is not optional |
| Built-in OOTB SITs | All | All (most) | Subset; verify per-SIT availability per Learn | Subset; verify per-SIT availability per Learn | Author equivalent custom SIT; document parity gap |
| Custom SIT (regex / keywords) | Yes | Yes | Yes | Yes | N/A |
| Exact Data Match (EDM) | Yes | Yes | Yes | Yes (verify current parity) | Use deterministic custom SIT during gap |
| Named Entities (built-in NER SITs) | Yes | Yes (most) | Limited; verify per-entity availability | Limited; verify per-entity availability | Use deterministic custom SIT |
| Trainable Classifiers — pre-trained | Yes | Yes | Limited subset; verify per-classifier per Learn | Limited subset; verify per-classifier per Learn | Use deterministic SIT or custom trainable when GA |
| Trainable Classifiers — custom | Yes | Yes | Verify current GA status per Learn | Verify current GA status per Learn | Defer custom-trainable use until GA |
| DSPM for AI | Yes | Yes (verify) | Verify current GA status per Learn | Verify current GA status per Learn | Compensate with control 1.7 audit + 1.10 Comm Compliance |
| DLP for Microsoft 365 Copilot location | Yes | Yes (verify) | Verify current GA status per Learn | Verify current GA status per Learn | Restrict Copilot grounding via labels and site-level isolation |
| Communication Compliance | Yes | Yes | Yes | Yes (verify) | N/A |
| Audit (Premium) — long-term retention add-on | Yes | Yes | Yes | Yes | Export to SIEM via Office 365 Management API |
| `Test-DataClassification` cmdlet | Yes | Yes | Yes | Yes | N/A — required for SIT regression |

**Operational rules:**

- **Always** run `Connect-IPPSSession` with the cloud-correct `-ConnectionUri` and `-AzureADAuthorizationEndpointUri` before any `Get-Dlp*` / `Get-LabelPolicy` / `Search-UnifiedAuditLog` command. A connection to the wrong cloud will appear to succeed against the wrong tenant or fail with a confusing 401.
- **Never** rely on a Commercial Microsoft Learn screenshot as definitive UX guidance for a GCC High or DoD tenant; pane labels, feature-flag flighting, and GA timing differ. Capture screenshots from the sovereign portal.
- **Always** record sovereign cloud + tenant ID in the §1.3 evidence bundle and in any Microsoft Support ticket payload (§7.3) — Microsoft Support routes sovereign cases to a different engineering team.
- **Compensating control during a parity gap:** when a feature (e.g., DSPM for AI in DoD) is not yet GA, document the gap, apply the most stringent deterministic detection (custom SIT + DLP for Copilot in Audit/Block as available), and re-evaluate at each Microsoft roadmap update.

---

## 5. Escalation — L1 → L2 → L3 → L4

| Tier | Owner | Triggers (entry into this tier) | MTTR target | Required evidence to enter | Transition criteria to next tier |
|------|-------|----------------------------------|-------------|-----------------------------|------------------------------------|
| **L1 — SOC / DLP analyst** | SOC L1 on shift; DLP analyst on call | DLP rule alert; user-reported false negative; routine false-positive triage; Activity Explorer anomaly | ≤ 1 h triage; ≤ 8 h close (SEV-3/SEV-4) | §1.3 items 1, 4, 6, 7 captured | Symptom not resolvable from runbook; SEV ≥ 2; Copilot path implicated; or repeat occurrence within 24 h |
| **L2 — Purview Compliance Admin / Purview Info Protection Admin** | Named control owners | L1 escalation; SIT / EDM / classifier change required; suspected policy-scope or audit-ingestion gap | ≤ 4 h triage; ≤ 24 h containment (SEV-2); ≤ 1 h containment (SEV-1) | Full §1.3 bundle; §1.2 reportability draft; §1.4 compensating control plan | Root cause requires platform-level change; Microsoft Support ticket likely; trainable-classifier model-risk review needed |
| **L3 — Security Engineering + Purview Data Security AI Admin** | Engineering lead, AI security lead, model-risk liaison | L2 escalation; Trainable Classifier drift / re-training; sovereign-parity gap requiring redesign; cross-pillar incident (DLP + Copilot + IB) | ≤ 8 h to remediation plan; ≤ 5 BD to permanent fix | All of L2 + classifier validation report + change-management artefacts + FSI Governance Gate ticket | Microsoft engineering required; suspected service-side defect; sovereign cloud routing required |
| **L4 — Microsoft Premier / Unified Support + Compliance & Legal in parallel** | Microsoft Support TAM; firm's Compliance / Legal lead | Suspected Microsoft service defect; sovereign-cloud GA gap blocking remediation; reportable-incident path under §1.2; PR/customer-comms readiness | Per Microsoft severity SLA; firm SLA per Compliance | §7.2 / §7.3 payload; §1.3 bundle; firm IR commander engaged | N/A — terminal tier |

**L1 → L2 specific triggers** (any one promotes the case):

- Symptom matches a §6 failure mode flagged "L2 minimum" (F1, F3, F5, F8, F10, F12, F13).
- Audit shows the SIT was consumed by ≥ 1 Block rule that did not fire on a known-good positive.
- Copilot or agent path appears in the audit window (any `CopilotInteraction` / `AiAppInteraction` record).
- The SIT, EDM schema, or classifier was modified within the last 14 days (change-related regression suspected).
- Incident classification reaches SEV-2 or higher per §1.1.

**L2 → L3 specific triggers:**

- A SIT change cannot be safely deployed without a model-risk review (trainable classifier involved).
- Sovereign-cloud feature gap (§4) blocks the fix; engineering must design a compensating architecture.
- The same SIT failure mode recurs after a documented L2 remediation (suspected platform defect).
- EDM upload pipeline failure spans more than one schema or persists beyond 24 h after restart.
- Cross-pillar coupling: SIT failure interacts with Information Barriers, Conditional Access, or sensitivity-label encryption in non-obvious ways.

**L3 → L4 specific triggers:**

- Reproducible failure with a minimal repro that L3 cannot resolve in ≤ 5 business days.
- Symptom suggests a Purview service-side defect (timing, scoping, or telemetry behaviour not consistent with documentation).
- Sovereign-cloud incident requiring Microsoft sovereign engineering routing.
- §1.2 reportability determination active and Microsoft Premier evidence required for the regulatory file.

Compliance/Legal and the firm's IR commander run in parallel from the moment §1.2 yields any "Yes" path; they do not wait for L4.

---

## 6. Failure-Mode Runbooks (F1 – F14)

Each runbook follows the same structure: **Symptom → Diagnostic (PowerShell + portal) → Root causes → Remediation → Evidence to capture → Reportability check → Exit criteria.** Run §1 first for any failure mode flagged "L2 minimum".

### F1 — Custom SIT regex misses a known-good positive (separator/format gap)

- **Symptom:** A document or message that contains a known regulated identifier (e.g., `123 45 6789` SSN) does not trigger the DLP rule that uses a custom SIT intended to detect it.
- **Diagnostic (PowerShell):**
  ```powershell
  Connect-IPPSSession -ConnectionUri https://ps.compliance.protection.outlook.com/powershell-liveid
  Get-DlpSensitiveInformationType -Identity "Custom_US_SSN_v3" | Format-List Identity,Name,Publisher,RulePackId,Version,WhenChanged
  $rp = Get-DlpSensitiveInformationTypeRulePackage -Identity "<RulePackId-from-above>"
  $rp.SerializedRulePackage | Out-File .\Custom_US_SSN_v3.xml
  Test-DataClassification -ClassificationNames "Custom_US_SSN_v3" -TestTextFile .\redacted-positives.txt
  ```
- **Diagnostic (portal):** *Information protection → Classifiers → Sensitive info types → Custom_US_SSN_v3 → Test* (paste the redacted positive sample); compare expected vs. actual matches and confidence.
- **Root causes:** (a) regex omits a separator variant (space, dot, en-dash, tab); (b) regex anchored too tightly (`^`/`$` instead of `\b`); (c) supporting-element / proximity window required by the rule is not satisfied in the sample; (d) confidence threshold on the consuming DLP rule is set above the SIT's per-pattern confidence.
- **Remediation:** Add the missing pattern variants to the SIT XML; run `Test-DataClassification` against the full regression set (positives **and** known negatives) before publishing; soak in Audit for 7–14 days; promote to Block.
- **Evidence to capture:** SIT XML before and after; `Test-DataClassification` transcripts (before/after); change-management ticket; consumer matrix re-test results.
- **Reportability check:** If the gap allowed a Copilot/agent or external-egress event, run §1.2 in full before publishing the fix.
- **Exit criteria:** All known-good positives match at the configured confidence on the consuming DLP rule; no regression on the negative test set; soak completed; audit evidence shows the rule firing on subsequent positives.
- **Reference:** [Custom SITs](https://learn.microsoft.com/en-us/purview/sit-create-a-custom-sensitive-information-type) · [SIT entity definitions](https://learn.microsoft.com/en-us/purview/sit-sensitive-information-type-entity-definitions) · [`Test-DataClassification`](https://learn.microsoft.com/en-us/powershell/module/exchange/test-dataclassification) · **L2 minimum.**

### F2 — Built-in OOTB SIT over-matches non-regulated content

- **Symptom:** A built-in SIT (e.g., U.S. SSN) generates a high false-positive volume (> 5% of matches over 7 days) that overwhelms analyst triage.
- **Diagnostic (PowerShell):**
  ```powershell
  Get-DlpSensitiveInformationType -Identity "U.S. Social Security Number (SSN)" | Format-List *
  Search-UnifiedAuditLog -StartDate (Get-Date).AddDays(-7) -EndDate (Get-Date) `
    -RecordType ComplianceDLPSharePoint,ComplianceDLPExchange -ResultSize 5000 |
    Where-Object { $_.AuditData -match "U.S. Social Security Number" } |
    Export-Csv .\ssn-matches-7d.csv -NoTypeInformation
  ```
- **Diagnostic (portal):** Compute precision from a reviewed sample (analyst marks each match true-positive vs. false-positive); inspect the entity definition to read the actual Low/Medium/High numeric thresholds for **this** SIT.
- **Root causes:** (a) confidence threshold on the consuming rule set to Low when Medium/High would suffice; (b) supporting-element keywords too broad; (c) policy scope includes content sets where SSN-like strings appear legitimately (e.g., test data, sandboxed datasets).
- **Remediation:** Raise the consuming rule to the SIT's Medium or High confidence (read the entity definition first — see A1); narrow the supporting-element keyword list; exclude legitimate datasets via location scoping or a sensitivity label exception; preserve recall by retaining a co-detector (e.g., EDM) for known customer records.
- **Evidence:** Precision/recall sample; rule before/after; change ticket; 14-day Audit-mode result.
- **Reportability check:** Tuning **down** can hide future true positives; if the SIT is on a regulated-data rule, run a recall-regression set in parallel and confirm no known-good positives are missed.
- **Exit criteria:** False-positive rate ≤ agreed ceiling; recall on the regression set unchanged.
- **Reference:** [Learn about SITs](https://learn.microsoft.com/en-us/purview/sit-sensitive-information-type-learn-about) · [Entity definitions](https://learn.microsoft.com/en-us/purview/sit-sensitive-information-type-entity-definitions).

### F3 — EDM rule does not fire on a known-good exact record

- **Symptom:** A DLP rule using an EDM-based SIT does not match a record that is in the source CSV uploaded to the EDM data store.
- **Diagnostic (PowerShell):**
  ```powershell
  Get-DlpEdmSchema -Identity "<schema-name>" | Format-List Identity,Name,DataStoreName,WhenChanged
  Get-DlpSensitiveInformationType | Where-Object { $_.Type -eq "ExactDataMatch" } | Format-Table Name,Identity,WhenChanged
  Test-DataClassification -ClassificationNames "<edm-sit-name>" -TestTextFile .\redacted-edm-positive.txt
  ```
- **Diagnostic (EDM Upload Agent host):** Inspect logs at `%LOCALAPPDATA%\Microsoft\EdmUploadAgent\Logs\` for the most recent upload. Confirm `Get-Item` timestamp, row count, and "upload completed" entry; check for hash-mismatch or schema-validation errors.
- **Diagnostic (portal):** *Data classification → Exact data matches → \<schema\> → Data sources* — confirm last successful refresh < 24 h and row count matches expectation.
- **Root causes:** (a) EDM upload failed silently and stale or empty hash table is in production; (b) source CSV column mapping does not match the schema XML (case, order, primary-element designation); (c) salt rotation occurred without re-upload; (d) record contains characters normalized differently than the upload (whitespace, casing) and the schema does not define a case-insensitive / whitespace-tolerant match; (e) schema's primary element is not present in the test sample; (f) row exceeds current per-row capacity (verify per current Learn).
- **Remediation:** Re-run upload from a clean source on the EDM Upload Agent host; verify the schema XML matches the CSV; re-confirm primary-element presence; if normalization is the cause, redefine the schema with a case-insensitive primary element and re-upload.
- **Evidence:** EdmUploadAgent log files (manifest + last upload); schema XML; redacted source row; salt-rotation log; `Test-DataClassification` transcript.
- **Reportability check:** Treat any EDM stale-data window as a potential gap on every consuming DLP rule for that window — run §1.2 if the gap covered active business hours and regulated data was in motion.
- **Exit criteria:** Last-successful-refresh < 24 h; `Test-DataClassification` matches; consuming DLP rule fires in Audit on a controlled positive.
- **Reference:** [EDM SITs overview](https://learn.microsoft.com/en-us/purview/sit-learn-about-exact-data-match-based-sits) · [Get started with EDM](https://learn.microsoft.com/en-us/purview/sit-get-started-exact-data-match-based-sits-overview) · [Create EDM (unified UX)](https://learn.microsoft.com/en-us/purview/sit-create-edm-sit-unified-ux-schema-rule-package) · **L2 minimum.**

### F4 — EDM upload exceeds row, column, or refresh-cadence limits

- **Symptom:** EDM upload fails with a schema-size or row-count error; refresh job blocks past its scheduled window.
- **Diagnostic:** Inspect the EdmUploadAgent log; confirm the schema's `searchable column` count is within the documented limit (≤ 32 searchable columns per current Learn) and the row count is within the per-tenant cap published in Learn (verify the current number — do not hard-code a stale figure).
- **Root causes:** (a) too many searchable columns marked in schema; (b) source dataset grew past published row cap; (c) per-tenant EDM job concurrency reached; (d) salt or encoding mismatch causing entire-file rejection.
- **Remediation:** Reduce searchable-column count to the minimum business-required (a column is "searchable" only if you intend to detect on it); split the dataset across multiple schemas where business segmentation allows; stagger refresh windows across schemas to avoid concurrency contention; reissue salt and re-upload if encoding mismatch is confirmed.
- **Evidence:** Schema XML; agent logs; row/column counts before and after; refresh schedule.
- **Exit criteria:** Upload completes within SLA; downstream `Test-DataClassification` matches.
- **Reference:** [EDM overview](https://learn.microsoft.com/en-us/purview/sit-learn-about-exact-data-match-based-sits) (verify current limits per Learn).

### F5 — Trainable Classifier accuracy drift > 10 pp from baseline

- **Symptom:** A Trainable Classifier consumed by a DLP or Auto-label policy shows accuracy / precision / recall ≥ 10 percentage points below the validation baseline recorded at FSI Governance Gate approval.
- **Diagnostic (PowerShell):**
  ```powershell
  Get-DlpClassifier | Format-Table Identity,Name,Type,Mode,Status,WhenChanged
  ```
- **Diagnostic (portal):** *Information protection → Classifiers → Trainable classifiers → \<classifier\> → Performance* — compare the latest validation run to the baseline recorded at gate approval; review prediction-distribution shift.
- **Root causes:** (a) population/content drift (new business line or document template not represented in training corpus); (b) language or locale shift; (c) re-training with a biased validation set; (d) Microsoft platform model update (rare but possible — capture build/version where surfaced).
- **Remediation:** Pause use as a Block detector; switch consuming rules to deterministic SIT or to Audit on the classifier; collect a fresh, representative training set; re-train; submit a fresh validation report through the FSI Governance Gate before re-promoting to Block. Document under the firm's MRM (SR 11-7 / OCC 2011-12) framework.
- **Evidence:** Baseline validation report; current validation report; training-corpus version and provenance; gate approval ticket; consumer matrix.
- **Reportability check:** If the drift caused regulated-data leakage (Audit shows non-matches that should have matched), run §1.2 in full.
- **Exit criteria:** New validation passes baseline + agreed margin; gate re-approval recorded; consuming rules restored to Block (if applicable) under change control.
- **Reference:** [Trainable classifiers](https://learn.microsoft.com/en-us/purview/trainable-classifiers-learn-about) · **L2 minimum.**

### F6 — Trainable Classifier never reaches publishable accuracy

- **Symptom:** A custom Trainable Classifier remains below the publication accuracy threshold after multiple training rounds.
- **Diagnostic (portal):** Review the classifier's training-set size, balance (positive vs. negative ratio), and the per-round accuracy curve. Inspect failed-prediction examples for systematic patterns.
- **Root causes:** (a) training corpus too small or unbalanced; (b) positives and negatives are not lexically separable (the underlying data does not support a learnable boundary); (c) labelling noise (mislabelled examples in the training set); (d) seed-keyword set too narrow.
- **Remediation:** Expand and balance the training corpus; relabel ambiguous examples; if the data is fundamentally non-separable, fall back to a deterministic SIT (regex / EDM / keyword list) — not every detection problem is a learnable problem. Document the decision and gate exit through the FSI Governance Gate.
- **Evidence:** Training-set manifests; round-by-round accuracy; sample of failed predictions; decision memo.
- **Exit criteria:** Either the classifier publishes at the agreed accuracy with gate approval, **or** the project is closed with a documented fallback to a deterministic SIT.
- **Reference:** [Trainable classifiers](https://learn.microsoft.com/en-us/purview/trainable-classifiers-learn-about).

### F7 — Named Entity SIT under-matches in non-English content

- **Symptom:** A Named Entity SIT (e.g., All Full Names, All Physical Addresses) does not match in non-English client correspondence even though the content clearly contains the entity type.
- **Diagnostic:** Identify the locale of the affected content; review the Named Entity coverage matrix in current Microsoft Learn; run `Test-DataClassification` with samples in the affected language.
- **Root causes:** (a) Named Entity model coverage is language-dependent and may not GA in all locales simultaneously; (b) text encoding or normalization stripping diacritics confuses the model.
- **Remediation:** Layer a deterministic SIT (regex / keyword list per locale) under the Named Entity SIT for affected languages; document the parity gap; track the Microsoft roadmap for the missing locale; revisit at each release.
- **Evidence:** Locale-tagged samples; `Test-DataClassification` transcripts per locale; current Learn coverage table; consumer matrix.
- **Exit criteria:** Per-locale recall meets the agreed bar via deterministic fallback; gap and remediation logged in the parent control's caveats.
- **Reference:** [Named Entities](https://learn.microsoft.com/en-us/purview/named-entities-learn).

### F8 — DLP rule does not trigger although `Test-DataClassification` matches

- **Symptom:** `Test-DataClassification` confirms the SIT detects the sample, but the DLP rule does not appear to fire when the same content is placed in a real workload (Exchange, SharePoint, OneDrive, Teams, Endpoint, Copilot).
- **Diagnostic (PowerShell):**
  ```powershell
  Get-DlpCompliancePolicy -Identity "<policy>" | Format-List Name,Mode,Enabled,*Location*
  Get-DlpComplianceRule -Policy "<policy>" | Format-List Name,Disabled,Mode,ContentContainsSensitiveInformation,AdvancedRule,ExceptIf*
  ```
- **Diagnostic (portal):** *Data Loss Prevention → Policies → \<policy\>* — confirm `Status = On`, `Mode = Enforce` (not Test/Audit), location toggles include the surface where content was placed, and rule conditions do not have an exception that excludes the test content (user, group, label, domain, file type).
- **Root causes:** (a) policy in Test or Audit mode; (b) location not enabled for the surface tested (e.g., rule covers Exchange but not SharePoint); (c) scope filter (user, group, site) excludes the test user; (d) rule uses `ExceptIf*` clauses that match the test content; (e) confidence threshold on the rule higher than the SIT match's confidence; (f) policy / rule disabled; (g) recent change has not propagated (allow up to several hours for tenant-wide propagation, longer in some sovereign clouds).
- **Remediation:** Correct the misconfiguration identified above; if propagation is suspected, wait the documented window and retest; for cross-location parity, ensure the SIT is consumed in **every** required DLP location including Microsoft 365 Copilot.
- **Evidence:** Policy + rule definitions; scope filters; mode; consumer matrix; propagation window observed; retest result.
- **Reportability check:** A scope or mode misconfiguration on a regulated-data rule is a control gap — run §1.2 if the gap covered live business data.
- **Exit criteria:** Rule fires in Audit on the controlled positive across all in-scope surfaces; consumer matrix re-validated.
- **Reference:** [Create / deploy DLP policy](https://learn.microsoft.com/en-us/purview/dlp-create-deploy-policy) · **L2 minimum.**

### F9 — DLP rule fires but no audit event in `Search-UnifiedAuditLog`

- **Symptom:** Analyst observes a DLP banner / notification, but `Search-UnifiedAuditLog` returns no `DLPRuleMatch` / `ComplianceDLP*` record for the corresponding window.
- **Diagnostic (PowerShell):**
  ```powershell
  # Confirm audit ingestion is enabled
  Connect-ExchangeOnline
  Get-AdminAuditLogConfig | Format-List UnifiedAuditLogIngestionEnabled,*Retention*
  # Pull the window
  Search-UnifiedAuditLog -StartDate (Get-Date).AddHours(-2) -EndDate (Get-Date) `
    -RecordType DLPRuleMatch,ComplianceDLPSharePoint,ComplianceDLPExchange -ResultSize 1000
  ```
- **Root causes:** (a) Unified Audit Log ingestion disabled on the tenant; (b) audit record type not yet ingested for the workload (some Endpoint DLP and Copilot DLP records have separate ingestion paths); (c) audit retention shorter than the search window (default 180 days for many record types — verify per current Learn and per add-on SKU); (d) E5 / Audit Premium long-term retention required for the lookback period; (e) Office 365 Management API consumer outpacing search index.
- **Remediation:** Enable UAL ingestion (`Set-AdminAuditLogConfig -UnifiedAuditLogIngestionEnabled $true`); engage Audit Premium for ≥ 1-year retention on regulated populations; export to SIEM via Office 365 Management API for independent retention; confirm record-type coverage per current Learn.
- **Evidence:** Tenant audit-config snapshot; record-type inventory; SIEM ingestion proof.
- **Reportability check:** A 17a-4 / 4511 books-and-records dependency rests on this audit chain; if records are missing for an investigative window, escalate to L3 and to Compliance immediately — gaps in supervisory evidence are themselves a finding.
- **Exit criteria:** UAL ingestion confirmed enabled for ≥ 30 days; record types cover all in-scope DLP surfaces including Copilot; SIEM mirror in place.
- **Reference:** [`Search-UnifiedAuditLog`](https://learn.microsoft.com/en-us/powershell/module/exchange/search-unifiedauditlog) · related control 1.7.

### F10 — Copilot returned regulated data; DLP for Copilot is in Audit mode (or not configured)

- **Symptom:** A Microsoft 365 Copilot response contained regulated data the SIT was supposed to gate; the Copilot DLP location was either not configured or set to Audit-only.
- **Diagnostic (PowerShell):**
  ```powershell
  Get-DlpCompliancePolicy | Where-Object { $_.CopilotLocation -or $_.MicrosoftCopilotExperiences } |
    Format-List Name,Mode,*Copilot*
  Search-UnifiedAuditLog -StartDate (Get-Date).AddHours(-24) -EndDate (Get-Date) `
    -RecordType CopilotInteraction,AiAppInteraction -ResultSize 5000 |
    Export-Csv .\copilot-window.csv -NoTypeInformation
  ```
- **Diagnostic (portal):** *Data Loss Prevention → Policies* — confirm a policy with the **Microsoft 365 Copilot** location enabled is present, and that the SIT in question is included in the rule's `ContentContainsSensitiveInformation`. Cross-check **DSPM for AI → Activity Explorer** for the user/window.
- **Root causes:** (a) Copilot DLP location not enabled in the tenant; (b) policy created but in Audit / Test mode; (c) SIT consumed only by Exchange / SharePoint rules and not by the Copilot-location rule; (d) Copilot DLP scope excludes the user or site; (e) sovereign-cloud parity gap (see §4) for the Copilot DLP location.
- **Remediation:** Enable the Microsoft 365 Copilot DLP location (control 1.5); add the regulated-data SIT to the Copilot rule's content-detection conditions; promote to Block where the data class warrants; confirm scope covers the affected population. Where sovereign parity is the cause, apply compensating controls (label-based isolation; restrict grounding sources).
- **Evidence:** Policy snapshot before/after; Copilot interaction record(s) (redacted hashes only outside Compliance custody); DSPM for AI activity record; scope diff.
- **Reportability check:** **Run §1.2 in full.** Any Copilot-mediated regulated-data exposure is presumptively SEV-1 and triggers Pillar 4 AI-incident handling in parallel.
- **Exit criteria:** Copilot DLP rule blocks the controlled positive in test; consumer matrix updated; FSI Governance Gate re-approval recorded for the SIT-Copilot pairing.
- **Reference:** [DLP for Microsoft 365 Copilot](https://learn.microsoft.com/en-us/purview/dlp-microsoft365-copilot-location-learn-about) · [DSPM for AI](https://learn.microsoft.com/en-us/purview/dspm-for-ai) · related controls 1.5, 1.6 · **L2 minimum, presumptive SEV-1.**

### F11 — Sensitivity label not auto-applied although SIT matches

- **Symptom:** An Auto-label policy uses a SIT that matches content, but the expected sensitivity label is not applied.
- **Diagnostic (PowerShell):**
  ```powershell
  Get-AutoSensitivityLabelPolicy | Format-List Name,Mode,*Location*,Workload,WhenChanged
  Get-AutoSensitivityLabelRule -Policy "<policy>" | Format-List Name,Disabled,ContentContainsSensitiveInformation
  ```
- **Diagnostic (portal):** *Information protection → Auto-labelling → \<policy\>* — confirm the policy is **on**, not in **simulation** mode, scope includes the affected location, and the rule's SIT and confidence match expectations.
- **Root causes:** (a) policy in Simulation mode (no actual label applied); (b) crawl/scan cycle has not yet processed the content (Auto-label has a service-defined cadence — consult current Learn for SLA); (c) label scope or publishing policy excludes the user; (d) label requires encryption and the user is outside the encryption rights scope (label fails to apply rather than apply-without-encryption).
- **Remediation:** Move policy from Simulation to Enforce after validation; allow the documented crawl SLA before re-checking; correct label-publishing policy scope; confirm encryption rights cover the affected population.
- **Evidence:** Policy mode + scope before/after; sample document; label publishing policy; crawl-cycle observation.
- **Exit criteria:** Label applies on the controlled positive within SLA across all in-scope locations.
- **Reference:** [Auto-labelling overview](https://learn.microsoft.com/en-us/purview/apply-sensitivity-label-automatically).

### F12 — Agent (Copilot Studio / declarative agent / connector) surfaces regulated data

- **Symptom:** A custom agent (Copilot Studio, declarative agent, or third-party agent invoked via a connector) returns regulated data that the SIT was supposed to gate. Often the SIT is correctly configured for first-party Copilot but the agent path was not in scope.
- **Diagnostic (PowerShell):**
  ```powershell
  Search-UnifiedAuditLog -StartDate (Get-Date).AddHours(-24) -EndDate (Get-Date) `
    -RecordType AiAppInteraction,CopilotInteraction -ResultSize 5000 |
    Export-Csv .\agent-window.csv -NoTypeInformation
  # Inventory Power Platform / Copilot Studio agents
  # (Power Platform Admin or PnP modules required)
  ```
- **Diagnostic (portal):** *Purview → DSPM for AI → Activity Explorer* — filter by app/agent identity; *Power Platform admin centre → Environments → Agents* — confirm agent connector list and data sources; *Entra → Enterprise applications* — confirm the agent's app registration and consented permissions.
- **Root causes:** (a) agent uses a connector (e.g., Dataverse, Graph, third-party API) that bypasses the SharePoint/Exchange grounding path the DLP rule covers; (b) agent runs under an app identity not in the DLP rule scope; (c) custom agent's grounding source is a regulated dataset not labelled / not covered by the SIT-aware Auto-label policy; (d) agent's plugin/connector token has broader permissions than the agent's user.
- **Remediation:** Bring the agent under the FSI Governance Gate per the parent control (1.13 §3) and Pillar 4; restrict the agent's data sources via labels and connector DLP; add the agent's identity to the DLP for Copilot rule scope; add Communication Compliance and Insider Risk policies covering the agent's user population; pause the agent if compensating controls are insufficient.
- **Evidence:** Agent identity (`AppId`, `AgentId`); connector inventory; consented permissions; Activity Explorer record; redacted prompt+response hash; agent change history.
- **Reportability check:** **Run §1.2 in full.** Presumptive SEV-1.
- **Exit criteria:** Agent restricted; SIT detection confirmed in agent path; FSI Governance Gate re-approval; Pillar 4 IR closure recorded.
- **Reference:** [DSPM for AI](https://learn.microsoft.com/en-us/purview/dspm-for-ai) · related control 4.6 · **L2 minimum, presumptive SEV-1.**

### F13 — SIT change deployed without governance approval (drift)

- **Symptom:** A SIT, EDM schema, or trainable classifier change appears in production without a corresponding change ticket or FSI Governance Gate approval.
- **Diagnostic (PowerShell):**
  ```powershell
  Get-DlpSensitiveInformationType | Sort-Object WhenChanged -Descending |
    Select-Object Name,WhenChanged,Publisher | Select-Object -First 25
  Search-UnifiedAuditLog -StartDate (Get-Date).AddDays(-30) -EndDate (Get-Date) `
    -Operations "New-DlpSensitiveInformationType","Set-DlpSensitiveInformationType","Remove-DlpSensitiveInformationType","New-DlpEdmSchema","Set-DlpEdmSchema","Remove-DlpEdmSchema" `
    -ResultSize 1000 | Export-Csv .\sit-changes-30d.csv -NoTypeInformation
  ```
- **Root causes:** (a) admin role over-assigned (write access on Purview Compliance / Info Protection roles granted to a population beyond the named control owners); (b) emergency-change process used without follow-up ratification; (c) automation pipeline pushed change without gate; (d) third-party (MSSP) change without notification.
- **Remediation:** Roll back the unapproved change to the prior version XML (preserve evidence first); reduce write scope on the affected role group to the named control owners; require PIM activation for SIT-write roles; add an approval gate to any automation pipeline; brief the FSI Governance Gate on the incident.
- **Evidence:** Change-history audit export; role-assignment snapshot before/after; rollback artefact; gate briefing record.
- **Reportability check:** If the unapproved change covered a regulated-data SIT and a gap exists in Audit while it was in effect, run §1.2.
- **Exit criteria:** Roles tightened; PIM enforced; pipeline gated; no further unapproved changes for 30 days.
- **Reference:** [Search-UnifiedAuditLog](https://learn.microsoft.com/en-us/powershell/module/exchange/search-unifiedauditlog) · related control 1.7.

### F14 — Sovereign endpoint mismatch / portal hostname error

- **Symptom:** PowerShell `Connect-IPPSSession` fails with auth error or returns a 404; the Purview portal redirects to a Commercial host and the tenant is not visible; cmdlets succeed but show no data.
- **Diagnostic:** Confirm tenant cloud (`Get-AzureADTenantDetail` or Entra portal); compare portal hostname and PowerShell `-ConnectionUri` against §4; inspect the sign-in flow for the correct authority host.
- **Root causes:** (a) Commercial endpoint used against a sovereign tenant (or vice versa); (b) `-AzureADAuthorizationEndpointUri` omitted for GCC High / DoD; (c) bookmarked Commercial portal URL re-used; (d) browser cached a Commercial sign-in.
- **Remediation:** Use the cloud-correct endpoint per §4 for every command and bookmark; clear cached credentials; for automation, parameterize the cloud and validate it before running.
- **Evidence:** Connection transcript; tenant ID + cloud; corrected command; successful re-run.
- **Exit criteria:** Cmdlets return expected tenant data; runbooks updated to use cloud-correct endpoints.
- **Reference:** [Connect to Security & Compliance PowerShell](https://learn.microsoft.com/en-us/powershell/exchange/connect-to-scc-powershell).

---

## 7. Microsoft Support Escalation

### 7.1 When to file a Microsoft Support / Premier ticket

File when **any one** of the following holds:

1. L3 root-cause analysis points to a suspected Microsoft service-side defect (timing, scoping, or telemetry behaviour not consistent with current Microsoft Learn documentation, reproducible in a minimal repro).
2. A sovereign-cloud parity or GA gap (§4) blocks remediation and architectural compensation is insufficient.
3. EDM upload failure persists after a clean re-upload from a hardened Upload Agent host with verified schema, source data, and salt.
4. A reportable-incident determination per §1.2 is active (any "Yes" path) and Microsoft engineering evidence is required for the regulatory file.

For SEV-1 / SEV-2 with active customer-data exposure, file at the highest severity available on the firm's support contract and notify the firm's Microsoft TAM in parallel.

### 7.2 Required evidence (assemble before opening the case)

- Tenant ID and sovereign cloud (Commercial / GCC / GCC High / DoD).
- Purview SKU and licence proof for any Premium-gated feature in scope.
- SIT identity, type, version, and full XML (export per §1.3 item 2).
- EDM schema XML and last-successful-upload manifest hash (where applicable).
- Trainable Classifier identity, baseline + current validation report (where applicable).
- Consumer matrix: every DLP / Auto-label / retention policy and rule that consumes the SIT.
- Audit window export (`Search-UnifiedAuditLog` CSV) covering the failure period.
- Minimal repro: a redacted positive sample plus the exact command/portal action that fails.
- `Test-DataClassification` transcript demonstrating the discrepancy.
- For Copilot/agent paths: `CopilotInteraction` / `AiAppInteraction` record IDs (do not paste regulated content into the ticket — provide IDs and SHA-256 hashes; raw payload moves through the firm's legal-hold channel only).
- §1.3 evidence-bundle SHA-256 manifest reference.
- Severity per §1.1 and current containment status per §1.4.

### 7.3 Microsoft Support payload template

```
Subject: [SEV-<n>] Purview SIT detection failure impacting regulated-data DLP — Tenant <tenant-id> (<cloud>)

1. Tenant context
   - Tenant ID: <guid>
   - Cloud: <Commercial | GCC | GCC High | DoD>
   - Purview SKU: <e.g., E5 Compliance + Data Security AI add-on>
   - Affected region(s): <region list>

2. Incident summary
   - One-line description: <e.g., Custom SIT "Custom_US_SSN_v3" fails to match space-separated SSNs; consumed by DLP rule "Block Outbound NPI"; Copilot grounding returned the unredacted value at <UTC timestamp>.>
   - First observed (UTC): <timestamp>
   - Reported by: <role>
   - Severity (firm): <SEV-1..SEV-4 per §1.1>
   - Reportability status: <under Compliance/Legal review per §1.2 | non-reportable per §1.2 | reportable, ticket #...>

3. Affected artefacts
   - SIT identity: <Name + GUID + Type + Publisher + Version + WhenChanged>
   - SIT XML: attached as <filename.xml> (SHA-256: <hash>)
   - EDM schema (if applicable): <Name + last-upload timestamp + manifest hash>
   - Trainable Classifier (if applicable): <Name + baseline accuracy + current accuracy + last validation date>
   - Consumer matrix: attached as <consumers.csv>

4. Reproduction
   - Steps to reproduce: <numbered steps>
   - Redacted positive sample: attached as <sample.txt> (SHA-256: <hash>)
   - Test-DataClassification transcript: attached as <test-dc.txt>
   - Expected behaviour: <e.g., SIT matches at Medium confidence; DLP rule fires in Audit>
   - Observed behaviour: <e.g., SIT does not match; DLP rule does not fire; Copilot returns unredacted value>

5. Audit evidence
   - Audit window: <UTC start> to <UTC end>
   - Record types pulled: ComplianceDLPSharePoint, ComplianceDLPExchange, DLPRuleMatch, CopilotInteraction, AiAppInteraction
   - Export: attached as <ual-window.csv> (SHA-256: <hash>)
   - Notable record IDs: <comma-separated IDs — do not include regulated payload>

6. Containment
   - Compensating controls applied (per §1.4): <list with timestamps>
   - Mode of consuming rules during investigation: <Test | Audit | Block>

7. Evidence bundle
   - SHA-256 manifest reference: <bundle-id or repo path under legal hold>
   - Custodian: <named role>

8. Engagement requested
   - <e.g., engineering-level confirmation of expected SIT behaviour for separator variants; root-cause analysis on EDM upload failure; parity timeline for DLP for Copilot in GCC High; etc.>

9. Firm contacts
   - Incident commander: <name, role, contact>
   - Purview Compliance Admin on call: <name, contact>
   - Compliance/Legal liaison: <name, contact>
   - Microsoft TAM (cc): <name>
```

### 7.4 Expected Microsoft response and next steps

- Microsoft will request the §7.2 artefacts; ensure they are uploaded to the case via the customer-approved secure channel only. **Do not** paste raw NPI / PCI / PHI / MNPI into the case body.
- For sovereign tenants, confirm the case is routed to the sovereign-cloud engineering queue.
- Track the case in the firm's incident ticket; mirror the Microsoft case ID into the §1.3 evidence bundle.
- Upon resolution, capture the Microsoft engineering response in writing; if the resolution includes a configuration change, run it through the firm's change-management and FSI Governance Gate before applying in production.
- If Microsoft confirms a service-side defect, capture the build/version, the workaround, the GA / fix ETA, and update the firm's risk register with the residual risk and compensating control until the fix lands.

---

## 8. Cross-References

### 8.1 Related controls (this framework)

- [1.5 Data Loss Prevention (DLP) and Sensitivity Labels](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) — the consuming surface for SITs in DLP and (where in scope) the Copilot/agent path.
- [1.6 Microsoft Purview DSPM for AI](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md) — Activity Explorer evidence path for SIT-mediated AI events.
- [1.7 Comprehensive Audit Logging and Compliance](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) — Unified Audit Log dependency for §1.3, F9, and §7.
- [1.10 Communication Compliance Monitoring](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md) — out-of-band detection layer used as compensating control in §1.4.
- [4.6 Grounding Scope Governance](../../../controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md) — bounds the SharePoint/OneDrive grounding surface that SITs and DLP-for-Copilot operate over.

### 8.2 Sibling 1.13 playbooks

- [Portal walkthrough](portal-walkthrough.md) — UI-driven SIT, EDM, and trainable-classifier authoring.
- [PowerShell setup](powershell-setup.md) — IPPS automation for SIT lifecycle.
- [Verification & testing](verification-testing.md) — `Test-DataClassification` regression suite and consumer-matrix tests.

### 8.3 Cross-pillar incident playbook

- [AI Incident Response Playbook](../../../playbooks/incident-and-risk/ai-incident-response-playbook.md) — invoked in parallel any time §1.2 yields a Copilot/agent path or any time F10 / F12 fires.

### 8.4 Microsoft Learn anchors

- [Learn about Sensitive Information Types](https://learn.microsoft.com/en-us/purview/sit-sensitive-information-type-learn-about)
- [Sensitive Information Type entity definitions](https://learn.microsoft.com/en-us/purview/sit-sensitive-information-type-entity-definitions)
- [Create a custom Sensitive Information Type](https://learn.microsoft.com/en-us/purview/sit-create-a-custom-sensitive-information-type)
- [Learn about Exact Data Match (EDM)-based SITs](https://learn.microsoft.com/en-us/purview/sit-learn-about-exact-data-match-based-sits)
- [Get started with EDM](https://learn.microsoft.com/en-us/purview/sit-get-started-exact-data-match-based-sits-overview)
- [Create EDM SIT (unified UX)](https://learn.microsoft.com/en-us/purview/sit-create-edm-sit-unified-ux-schema-rule-package)
- [Named Entities — learn about](https://learn.microsoft.com/en-us/purview/named-entities-learn)
- [Trainable classifiers — learn about](https://learn.microsoft.com/en-us/purview/trainable-classifiers-learn-about)
- [DLP for Microsoft 365 Copilot location](https://learn.microsoft.com/en-us/purview/dlp-microsoft365-copilot-location-learn-about)
- [Data Security Posture Management for AI](https://learn.microsoft.com/en-us/purview/dspm-for-ai)
- [`Test-DataClassification`](https://learn.microsoft.com/en-us/powershell/module/exchange/test-dataclassification)
- [`Search-UnifiedAuditLog`](https://learn.microsoft.com/en-us/powershell/module/exchange/search-unifiedauditlog)
- [Connect to Security & Compliance PowerShell (sovereign URIs)](https://learn.microsoft.com/en-us/powershell/exchange/connect-to-scc-powershell)

### 8.5 Regulatory anchors (informational — Compliance/Legal owns interpretation)

- **NY DFS 23 NYCRR 500.17(a)** — 72-hour cybersecurity-event notification determination clock.
- **SEC Regulation S-P §248.30(a)(4)** — customer notification within ≤ 30 days where the firm determines (or reasonably should have determined) that misuse of customer information has occurred or is reasonably likely.
- **FINRA Rule 4530** — problem reporting for member firms.
- **FINRA Rule 3110** — supervision of communications and AI-mediated workflows.
- **FINRA Rule 4511 / SEC Rule 17a-4** — books-and-records / WORM retention; SIT-mediated detections supporting supervision are themselves records.
- **FINRA Notice 25-07** — reinforces application of supervision and recordkeeping to AI-mediated communications.
- **GLBA 501(b)** — Safeguards Rule; SIT controls form part of the administrative/technical safeguards for NPI.
- **PCI DSS 12.10** — incident-response procedures for cardholder-data environments.
- **OCC Bulletin 2011-12 / Federal Reserve SR 11-7** — Model Risk Management; applies to Trainable Classifiers used as detective controls.
- **CFTC Rule 1.31** — records retention obligations relevant to MNPI and information-barrier failures (or SEC equivalent for non-CFTC entities).

This list is illustrative and is **not** a determination of applicability for any specific firm or incident. Compliance and Legal own the regulatory analysis. This playbook supports that analysis; it does not substitute for it.

---

*Updated: April 2026 | Version: v1.4 | UI Verification Status: Current*
