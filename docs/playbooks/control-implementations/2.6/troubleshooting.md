# Control 2.6 — Troubleshooting: Model Risk Management (OCC Bulletin 2026-13 / SR 26-2 — formerly OCC 2011-12 / SR 11-7) Evidence Pipeline and Examination Readiness

> **Scope.** This playbook is the diagnostic companion to [Control 2.6 — Model Risk Management (OCC Bulletin 2026-13 / SR 26-2 — formerly OCC 2011-12 / SR 11-7)](../../../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md). It addresses operational failure modes in the **evidence pipeline** the firm relies on to satisfy SR 26-2 (formerly SR 11-7) — the firm's reconciled model inventory, the underlying-model change-detection path (Microsoft Copilot Studio + Message Center), the validation evidence chain (Foundry evaluators, Committee minutes, validation memos), the 17a-4(f)-compliant retention path, the firm's approval workflow alongside Agent 365 requests, the illustrative PowerShell helpers and their manual-evidence gaps, and examination-readiness rehearsal.
>
> **Regulatory framing.** Reliable evidence produced by the surfaces in this control *supports compliance with* OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12), Federal Reserve SR 26-2 (formerly SR 11-7), FDIC FIL-15-2026, FFIEC IT Handbook, FINRA Rule 3110 (Supervision), FINRA Rule 4511 and SEC 17a-3 / 17a-4 (Books and Records — including 17a-4(f) WORM retention of validation evidence and Committee minutes), SOX §§ 302 / 404 (ICFR documentation of AI controls), GLBA 501(b), and NYDFS 23 NYCRR 500 where AI agents touch covered customer information. FINRA RN 25-07 (workplace modernization RFC) is referenced **as contextual material only** and is not cited as an enforceable AI rule. The Microsoft surfaces described here **support** the firm's MRM program; they **do not replace** the firm's Model Risk Management Committee, the independent validation function, the effective-challenge process, three-lines-of-defense governance, or registered-principal supervisory review under FINRA Rule 3110.
>
> **Audience.** Power Platform Admin, Purview Compliance Admin, AI Administrator, Compliance Officer, AI Governance Lead, Model Risk Manager, and second-line MRM staff supporting the firm's response to internal audit, examiner pulls, and Committee inquiries.
>
> **Sibling playbooks.** [portal-walkthrough.md](portal-walkthrough.md) · [powershell-setup.md](powershell-setup.md) · [verification-testing.md](verification-testing.md)

---

!!! warning "Non-Substitution — Tooling Supports MRM, It Does Not Replace It"
    Every diagnostic, helper, and remediation step in this playbook produces or repairs **evidence**. None of them performs validation, exercises effective challenge, or makes a model-tiering or approval decision. Those judgments are reserved to the firm's Model Risk Management Committee, the independent validation function (organizationally separate from the model owner per SR 26-2 §V (formerly SR 11-7 §V)), and registered-principal supervision under FINRA Rule 3110. Any examiner-facing communication arising from an incident in this playbook must be coordinated through Compliance and Legal — **not** by individual administrators acting on their own.

---

## Table of Contents

- [§0 Triage Tree](#0-triage-tree)
- [§1 Issue 1 — DSPM for AI Inventory Missing Agents](#1-issue-1-dspm-for-ai-inventory-missing-agents)
- [§2 Issue 2 — Default-Model Migration Not Detected Before It Took Effect](#2-issue-2-default-model-migration-not-detected-before-it-took-effect)
- [§3 Issue 3 — Independent Validation Challenged Because Validator Reports to Model Owner](#3-issue-3-independent-validation-challenged-because-validator-reports-to-model-owner)
- [§4 Issue 4 — Anthropic Claude (or Other Vendor Model) Selected Without Vendor-Model Assessment](#4-issue-4-anthropic-claude-or-other-vendor-model-selected-without-vendor-model-assessment)
- [§5 Issue 5 — Foundry Evaluator Runs Missing for Tier 1 Agent](#5-issue-5-foundry-evaluator-runs-missing-for-tier-1-agent)
- [§6 Issue 6 — Effective-Challenge Evidence Weak: Committee Minutes Generic](#6-issue-6-effective-challenge-evidence-weak-committee-minutes-generic)
- [§7 Issue 7 — Validation Evidence Retention Not 17a-4(f)-Compliant](#7-issue-7-validation-evidence-retention-not-17a-4f-compliant)
- [§8 Issue 8 — Agent 365 Publication-Approval Workflow Not Blocking Publish](#8-issue-8-agent-365-publication-approval-workflow-not-blocking-publish)
- [§9 Issue 9 — Model-Retirement Evidence Missing](#9-issue-9-model-retirement-evidence-missing)
- [§10 Issue 10 — PowerShell Helper Returns Status=Error](#10-issue-10-powershell-helper-returns-statuserror)
- [§11 Issue 11 — Examiner Asks for Inventory of In-Scope Agents and Firm Cannot Produce in Real Time](#11-issue-11-examiner-asks-for-inventory-of-in-scope-agents-and-firm-cannot-produce-in-real-time)
- [§12 Escalation Paths](#12-escalation-paths)
- [§13 Cross-References](#13-cross-references)

---

## §0 Triage Tree

### 0.1 Symptom → Issue Map

| # | Presenting Symptom | Likely Issue | First Diagnostic |
|---|---|---|---|
| 1 | Agent visible in Power Platform / Agent 365 but absent from Purview activity | [§1](#1-issue-1-dspm-for-ai-inventory-missing-agents) | Scope, onboarding, activity and permissions check |
| 2 | Agent Card references a model no longer in production; vendor migrated default | [§2](#2-issue-2-default-model-migration-not-detected-before-it-took-effect) | Message Center subscription audit |
| 3 | Examiner challenges validator independence — validator reports to model owner | [§3](#3-issue-3-independent-validation-challenged-because-validator-reports-to-model-owner) | Org-chart trace + MRM charter |
| 4 | Vendor model (e.g., Anthropic Claude) selected in Copilot Studio without vendor-model assessment | [§4](#4-issue-4-anthropic-claude-or-other-vendor-model-selected-without-vendor-model-assessment) | Agent Card vs. approved-model list |
| 5 | Tier 1 agent has no Foundry evaluator runs; outcomes-analysis evidence gap | [§5](#5-issue-5-foundry-evaluator-runs-missing-for-tier-1-agent) | Foundry evaluator history |
| 6 | Committee minutes describe approvals in generic terms; effective-challenge evidence weak | [§6](#6-issue-6-effective-challenge-evidence-weak-committee-minutes-generic) | Minute-template review |
| 7 | Validation memos / Committee minutes stored only in M365 Audit Premium or general SharePoint | [§7](#7-issue-7-validation-evidence-retention-not-17a-4f-compliant) | Retention-label / WORM audit |
| 8 | Agent published without the firm's MRM approval | [§8](#8-issue-8-agent-365-publication-approval-workflow-not-blocking-publish) | Actual distribution path and separate approval gate |
| 9 | Tier 1 agent retired; decision, last validation, and final monitoring snapshot not retained | [§9](#9-issue-9-model-retirement-evidence-missing) | Change-history reconstruction |
| 10 | PowerShell helper returns `Status=Error` | [§10](#10-issue-10-powershell-helper-returns-statuserror) | Module / connection / endpoint check |
| 11 | Examiner asks for in-scope agent inventory in real time and firm cannot produce | [§11](#11-issue-11-examiner-asks-for-inventory-of-in-scope-agents-and-firm-cannot-produce-in-real-time) | On-demand PS helper + rehearsal review |

### 0.2 Severity Matrix

| Severity | Criteria | Response Target | Notifications |
|---|---|---|---|
| **SEV-1** | Examiner / regulator on-the-clock; inventory cannot be produced; or material model change detected post-fact in production for a Tier 1 agent | Triage within 1h; mitigation within 4h | AI Governance Lead, MRM Committee Chair, Compliance Officer, Legal |
| **SEV-2** | Tier 1 outcomes-analysis evidence missing; validator-independence finding; vendor model in production without assessment | Triage within 4h; mitigation within 24h | AI Governance Lead, Model Risk Manager, Compliance Officer |
| **SEV-3** | Tier 2 evidence gap; Committee-minute template defect; publication-workflow misconfiguration with no Tier 1 exposure | Triage within 1 business day | Model Risk Manager, AI Governance Lead |
| **SEV-4** | Tier 3 evidence gap; cosmetic / reporting defect | Triage within 5 business days | AI Governance Lead |

### 0.3 Pre-Remediation Checklist

Before taking any remediation action recorded in this playbook:

1. **Preserve current state.** Snapshot the affected agent's Agent Card, model-inventory row, current validation memo, and most recent Committee disposition to a Purview-retention-protected location before edits.
2. **Confirm scope.** Tier (1 / 2 / 3), Zone (1 / 2 / 3), business owner, and whether the agent is customer-facing or decision-support.
3. **Examination flag.** Confirm with Compliance / Legal whether the affected agent is subject to an active examination, internal investigation, subpoena, or litigation hold. If yes, proceed only under written direction.
4. **Reserve MRM judgment.** Record that any remediation produces or repairs **evidence**; the MRM Committee retains the substantive validation, tiering, and approval decisions.

---

## §1 Issue 1 — DSPM for AI Inventory Missing Agents

**Symptom.** An agent in Power Platform or the Agent 365 registry has no corresponding Purview activity evidence. This is a reconciliation delta, not automatic proof of a discovery defect or an unregistered model.

**Root causes (typical).**

- **Different source contracts.** Purview reports observed supported interactions, while inventories can include inactive agents.
- **Onboarding, billing or policy gap.** Verify app/channel-specific prerequisites; Copilot Studio non-Microsoft-channel protection requires Purview pay-as-you-go.
- **Filters or permissions.** Report filters and content-viewer permissions can hide relevant evidence.
- **Collection timing or failure.** Record the collection window and actual error; do not assume an identity-propagation SLA or a universal connector refresh contract.

**Resolution.**

1. **Check supported coverage.** Follow [Purview's Copilot Studio procedure](https://learn.microsoft.com/en-us/purview/ai-copilot-studio), the app-specific onboarding and the feature-specific service description, not a generic Compliance Manager license assumption.
2. **Inspect actual reports.** In Purview **Solutions → DSPM for AI (classic) → Reports → Copilot experiences & agents → View details**, inspect the available activity-explorer filters. Record current-DSPM equivalents if that experience is used. Do not invent a generic **Connectors** or **Discover → AI applications** route.
3. **Check activity and timing.** Use an approved test interaction and record when it becomes visible. Microsoft advises waiting at least a day for initial policy report data; that is not a tenant-wide agent-discovery SLA.
4. **Reconcile supported inventories.** Compare the firm's Agent Card register with Power Platform inventory/model exports and **Agents → All agents → Registry**. The illustrative PowerShell inventory adapters deliberately emit `ManualEvidenceRequired`; reinstalling modules does not complete them.

**Verification.**

- Every delta has a documented source-scope/onboarding/activity explanation or an unresolved finding; do not require identical activity and inventory populations.
- Retain raw collection evidence, scope, errors and any remediation in the change ticket. See [Verification §1.2](./verification-testing.md#12-population-of-in-scope-agents).

**Cross-link.** [Control 2.25 — Agent 365 Admin Center Governance Console](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md) · [Control 2.26 — Entra Agent ID Identity Governance](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md) · [Control 3.1 — Agent Inventory and Metadata Management](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md).

---

## §2 Issue 2 — Default-Model Migration Not Detected Before It Took Effect

**Symptom.** Microsoft migrated the default underlying foundation model in Copilot Studio (for example, GPT-family default upgrade or replacement). The firm's Agent Card for one or more agents now references a model that is no longer the production default, and no impact assessment was performed before the migration took effect. The MRM Committee learned of the change after deployment.

**Root causes (typical).**

- **No subscription to vendor change signals.** The Microsoft 365 Message Center, the Power Platform release plan, and the Copilot Studio "What's new" feed are not routed to a monitored mailbox / Teams channel staffed by the AI Administrator and the Model Risk Manager.
- **Agent Card records "Copilot Studio default" rather than the specific model and version.** When the default rolls forward, the Agent Card silently changes meaning.
- **No change-management gate** treating an underlying-model change as a model change under SR 26-2 §VI (formerly SR 11-7 §VI).

**Resolution.**

1. **Subscribe vendor change signals to a monitored mailbox.** Route the Microsoft 365 Message Center, Power Platform release plan, and Copilot Studio release notes to a shared mailbox / Teams channel with the AI Administrator, AI Governance Lead, Model Risk Manager, and second-line MRM as members. Document the subscription owners and the SLA for triage of model-impacting messages (recommended: 1 business day).
2. **Update Agent Card schema.** Record the selected model, provider, default-versus-specific selection and visible version identifiers on **Overview → Model**. If an exact snapshot version is not exposed, record that limitation with dated lifecycle evidence, not a fabricated version. Follow [Microsoft's model-selection guidance](https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-select-agent-model).
3. **Treat the migration as a model change.** Under SR 26-2 §VI (formerly SR 11-7 §VI), a vendor-driven default-model migration is a model change. Open a change ticket per agent, perform impact assessment proportionate to tier (Tier 1: full re-validation; Tier 2: abbreviated re-validation; Tier 3: documented review), and obtain MRM Committee disposition.
4. **Backfill evidence.** For the migration that took effect without prior assessment, document the gap in the Committee minutes, the date the firm became aware, the post-fact impact assessment, and any compensating monitoring (e.g., enhanced Foundry evaluator cadence for the next monitoring period).

**Verification.**

- Message Center routing produces a triage record within the documented SLA on the next vendor-issued model-change message (test by waiting for, or simulating receipt of, a representative message).
- 100% of in-scope Agent Cards record actual model selection and available version evidence, with explicit limitations where the service exposes no snapshot version.
- Committee minutes for the next cycle reflect the post-fact impact assessment for the missed migration.

**Cross-link.** [Control 2.3 — Change Management and Release Planning](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md) · [Control 2.7 — Vendor and Third-Party Risk Management](../../../controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md).

---

## §3 Issue 3 — Independent Validation Challenged Because Validator Reports to Model Owner

**Symptom.** During an examination, internal audit, or Committee review, a finding is raised that the validator who signed the validation memo for one or more agents reports — directly or via dotted line — to the model owner / model developer. SR 26-2 §V (formerly SR 11-7 §V) independence test failed.

**Root causes (typical).**

- Validation function was stood up inside the first line of defense (within the business that owns the model) rather than in the second line.
- MRM charter does not explicitly require organizational independence between validator and model owner.
- Resource pressure led to first-line staff being asked to validate work produced by colleagues in the same reporting chain.

**Resolution.**

1. **Re-route validators to second-line MRM.** Reassign the validation function to personnel organizationally and functionally separate from the model owner / developer (SR 26-2 §V (formerly SR 11-7 §V)). Internal second-line MRM staff can satisfy independence; third-party engagement is one way to demonstrate it but is **not required** and is **not equivalent** to the regulatory independence test.
2. **Document organizational independence in the MRM charter.** Update the firm's Model Risk Management policy / charter to explicitly state: (a) the reporting line of the validation function, (b) that validators have authority and competence to challenge the model, and (c) the prohibition on validators sitting in the same reporting chain as the model owner. Obtain MRM Committee approval and Compliance sign-off.
3. **Re-validate affected agents.** For every agent whose validation is challenged, perform a new validation by an organizationally independent validator. Retain both memos: the original (with the noted independence finding) and the re-validation, with a cover memo explaining the remediation. Do not delete the original.
4. **Retain remediation evidence.** Route the original memo, the independence finding, the charter update, the re-validation memo, and the Committee disposition to the 17a-4(f)-compliant retention path (see [§7](#7-issue-7-validation-evidence-retention-not-17a-4f-compliant)).

**Verification.**

- The MRM charter version with explicit independence language is published, dated, and signed off by the Committee.
- An organizational chart trace from each validator to the model owner shows no shared reporting line short of a sufficiently senior independent officer (typically the CRO or equivalent).
- Re-validation memos for affected agents are filed and accepted by the Committee.

**Cross-link.** [Control 2.7 — Vendor and Third-Party Risk Management](../../../controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md) · [Control 2.12 — Supervision and Oversight (FINRA Rule 3110)](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md).

---

## §4 Issue 4 — Anthropic Claude (or Other Vendor Model) Selected Without Vendor-Model Assessment

**Symptom.** Review of an Agent Card or Copilot Studio model-selection screen shows an agent configured to use a third-party / vendor model (for example, Anthropic Claude where available in the firm's tenant) without a documented vendor-model assessment. SR 26-2 §V (formerly SR 11-7 §V) vendor-model governance gap.

**Root causes (typical).**

- Copilot Studio surfaces vendor models in the model-selection UI as availability rolls out; agent owners may select a vendor model without recognizing the vendor-model governance obligation.
- Supported Microsoft 365 provider access and separate PPAC external/preview model settings were not aligned with the firm's approval register; generic connector DLP is not a universal model-name allowlist.
- MRM policy does not yet enumerate vendor-model providers or pre-approval status.

**Resolution.**

1. **Quarantine or dispose.** Pending assessment, the MRM Committee may direct the agent owner to either (a) revert to a pre-approved model on the firm's approved-model list, or (b) restrict the agent to Zone 1 / non-production use until assessment completes. Record the disposition.
2. **Perform post-hoc vendor-model assessment.** Apply the firm's vendor-model assessment under SR 26-2 §V (formerly SR 11-7 §V) — covering the vendor's model documentation, training-data disclosures, evaluation results, terms-of-service review, data-handling commitments, and the vendor's incident-disclosure history. Coordinate with Vendor Risk Management (Control 2.7).
3. **MRM Committee disposition.** The Committee renders an explicit disposition: approved / approved-with-conditions / not approved. Disposition, conditions, and effective dates are recorded in Committee minutes and routed to retention.
4. **Update Agent Card and approved-model list.** Update the Agent Card to record the specific vendor model and version, the assessment reference, and the Committee disposition. Update the firm's approved-model list and re-publish to model owners.
5. **Add a technical guardrail (forward-looking).** Configure supported Microsoft 365 provider access and PPAC environment/group external/preview model settings ([external model controls](https://learn.microsoft.com/en-us/power-platform/admin/allow-llm-generative-responses)). Compare **Overview → Model** against the firm's approved-model register; do not assume a native arbitrary-model allowlist or governance-template publish gate. Where unsupported, document a controlled review/monitoring gap rather than inventing a switch. Review actual Anthropic routing and retention terms ([provider guidance](https://learn.microsoft.com/en-us/copilot/implement/connect-to-ai-subprocessor)).

**Verification.**

- Vendor-model assessment memo is filed with Committee disposition.
- Agent Card reflects the specific vendor model, version, and approval reference.
- Test supported provider/preview restrictions in an approved non-production environment. Reconcile the agent's actual model choice against the organizational approval register and document any selection that cannot be technically prevented.

**Cross-link.** [Control 2.7 — Vendor and Third-Party Risk Management](../../../controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md) · [Control 2.3 — Change Management and Release Planning](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md).

---

## §5 Issue 5 — Foundry Evaluator Runs Missing for Tier 1 Agent

**Symptom.** A Tier 1 agent has no Azure AI Foundry evaluator runs in the current monitoring period, or the most recent evaluator run is older than the cadence specified in the firm's MRM policy. The outcomes-analysis pillar of SR 26-2 (formerly SR 11-7) has an evidence gap.

**Root causes (typical).**

- Foundry project for the agent was never linked to the Copilot Studio agent / endpoint.
- Evaluator suite was scoped at design time but not scheduled, or schedule was disabled after a quota change.
- Evaluation dataset is empty or stale; runs were skipped because no inputs were available.

**Resolution.**

1. **Configure the Foundry built-in evaluators.** For each Tier 1 agent, configure the relevant subset of Foundry built-in evaluators against a representative evaluation dataset:
    - **Quality:** groundedness, relevance, coherence, fluency.
    - **Safety:** content-safety / harm evaluators (verify per region and judge-model availability).
    - **Agentic behavior:** Tool Call Accuracy; Task Completion and Intent Resolution are preview in the [current built-in reference](https://learn.microsoft.com/en-us/azure/ai-foundry/concepts/built-in-evaluators).
2. **Curate a representative evaluation dataset.** The dataset must reflect the agent's production use cases, including known edge cases, adversarial prompts, and golden-answer cases. The dataset is itself an MRM artifact and must be versioned and retained.
3. **Document cadence in MRM policy.** The MRM policy should specify evaluator cadence by tier — for example, Tier 1 monthly, Tier 2 quarterly, Tier 3 annually or on material change. Cadence is set by the firm; the values above are illustrative.
4. **Schedule and monitor the runs.** Configure the runs on the documented cadence; route run-failure alerts to a monitored channel. Backfill the missed period by running the evaluator suite against the current production configuration and recording the gap as a finding.
5. **Reserve MRM judgment.** Foundry evaluator output is **evidence** consumed by validators; it does not constitute validation in itself. The Committee remains responsible for outcomes-analysis disposition.

**Verification.**

- Native evaluation evidence shows applicable runs at the documented cadence, with release state, inputs, judge model and skipped/unsupported evaluators recorded. Preview evaluators are not assumed to be GA production dependencies.
- Evaluation dataset is versioned and retained under the 17a-4(f) path.
- Backfill memo is filed with the Committee.

**Cross-link.** [Control 1.7 — Comprehensive Audit Logging and Compliance](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) · [Control 3.9 — Microsoft Sentinel Integration](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md).

---

## §6 Issue 6 — Effective-Challenge Evidence Weak: Committee Minutes Generic

**Symptom.** Internal audit or examiner review finds Committee minutes that record approvals in generic terms ("the Committee reviewed and approved") without capturing the specific challenge questions raised, validator responses, disposition rationale, dissenting views, or follow-up actions. Effective-challenge evidence under SR 26-2 (formerly SR 11-7) is weak.

**Root causes (typical).**

- Minute template is summary-only and does not prompt the secretary to capture challenge specifics.
- Discussion happens in the room but is not transcribed into the record.
- Follow-up actions are tracked outside the minutes (in a separate tracker), making it difficult to demonstrate closure during examination.

**Resolution.**

1. **Overhaul the minute template.** The new template, at minimum, captures per-agenda-item:
    - **Specific challenge questions** raised by Committee members or invited challengers.
    - **Validator / model-owner responses** to each challenge.
    - **Disposition** (approved / approved-with-conditions / deferred / not approved) with rationale.
    - **Dissenting views** and the names of dissenting members.
    - **Follow-up actions** with owner, due date, and the agenda item where closure will be reported.
2. **Pre-meeting challenge package.** Require the secretary to circulate a challenge package in advance of the meeting (validation memo, Foundry evaluator results, prior findings, open follow-ups). Capture in the minutes which materials were reviewed.
3. **Re-issue prior minutes only on Legal direction.** Do not retroactively edit historical minutes. If a historical minute is materially incomplete, file a **supplemental memo** with the dated correction, signed by the Committee Chair, and route both the original and the supplement to retention.
4. **Train the secretary.** Brief the Committee secretary on the new template and the SR 26-2 (formerly SR 11-7) effective-challenge standard. Record the training as evidence of remediation.

**Verification.**

- The next Committee meeting produces minutes that pass a documented quality review against the new template.
- A sample of three subsequent meetings confirms sustained adoption.
- Open follow-ups are visibly tracked across meetings.

**Cross-link.** [Control 2.12 — Supervision and Oversight (FINRA Rule 3110)](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) · [Control 1.7 — Comprehensive Audit Logging and Compliance](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md).

---

## §7 Issue 7 — Validation Evidence Retention Not 17a-4(f)-Compliant

**Symptom.** Validation memos, Committee minutes, vendor-model assessments, and / or Foundry evaluator results are stored only in **M365 Audit Premium** logs or in a general-purpose SharePoint site without an immutable retention label. Retention does not meet SEC 17a-4(f) for books-and-records of model artifacts.

> **Important.** **M365 Audit Premium is operational telemetry** for activity audit (extended retention up to one year for Premium SKUs). It is **not** 17a-4(f) WORM-compliant retention for model artifacts and validation evidence. Long-term model documentation and validation evidence must land in **Microsoft Purview retention with an immutable / record-label policy** or be routed to an **approved 17a-4(f) third-party vendor** (e.g., Cohasset-attested archival service).

**Root causes (typical).**

- Retention design treated audit-log retention and books-and-records retention as the same problem.
- SharePoint sites used by MRM lack a configured Purview retention label or have a label that permits modification / deletion before the retention period expires.
- No formal mapping exists between MRM artifact types and the 17a-4(f) retention path.

**Resolution.**

1. **Define the retention map.** Map each MRM artifact type (validation memo, Committee minute, vendor-model assessment, Foundry evaluator dataset and results, Agent Card version, change-ticket package, model-retirement memo) to its retention class, retention period, and storage path.
2. **Verify actual record protection.** Distinguish ordinary retention, locked/unlocked records and regulatory records using [Microsoft's restriction table](https://learn.microsoft.com/en-us/purview/records-management). Publish the approved labels to the location, then verify application and status on actual finalized evidence items. A standard retention label can preserve a copy while permitting deletion; a record can be unlockable. Regulatory-record labeling and policy-level Preservation Lock are separate, irreversible decisions requiring authorized change control.
3. **Or route to an approved 17a-4(f) vendor.** Where the firm uses an approved third-party archive (Cohasset-attested or equivalent), route the artifact via the documented connector and retain the connector's confirmation of receipt and immutability attestation.
4. **Backfill historical artifacts.** For artifacts already in non-compliant locations, copy them under change control to the compliant store, apply the retention label / archival route, and record the move in a remediation memo. Retain the originals in place where deletion is not authorized.
5. **Decouple from M365 Audit Premium.** Do not rely on M365 Audit Premium retention for model artifacts. Audit Premium remains useful for operational telemetry and for evidencing access to the artifacts.

**Verification.**

- Sampled items show the actual applied label/status and approved retention start/duration. `Get-ComplianceTag` reads label settings; `Get-RetentionCompliancePolicy` reads policy settings, including `RestrictiveRetention` for Preservation Lock. A publication-scope report alone does not prove item protection; there is no documented per-item `deletionLocked` test.
- An attempt to delete a protected artifact (test in Zone 1 with a non-evidence document) is blocked by the label.
- Vendor-archive confirmations exist for any artifact routed to an external 17a-4(f) vendor.

**Cross-link.** [Control 1.7 — Comprehensive Audit Logging and Compliance](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) · [Control 1.9 — Data Retention and Deletion Policies](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md).

---

## §8 Issue 8 — Agent 365 Publication-Approval Workflow Not Blocking Publish

**Symptom.** An agent is published to Zone 2 / Zone 3 without MRM Committee approval. Determine which distribution channel was used and whether the firm's separate approval gate was exercised; native policy-template assignment alone does not enforce an MRM Committee decision.

**Root causes (typical).**

- The firm's MRM approval record was not checked before the supported publication/activation action.
- A distribution channel outside the reviewed store-approval path remained available.
- A policy-template security bundle was mistaken for a custom MRM approver chain or model-name allowlist.
- Template support or underlying Entra authentication prerequisites were assumed rather than verified.

**Resolution.**

1. **Inspect the real request.** Review **Agents → All agents → Requests**, request state, audience and actual approval decision per [Microsoft's request procedure](https://learn.microsoft.com/en-us/microsoft-agent-365/admin/agent-requests).
2. **Review policy evidence separately.** Inspect **Agents → Settings → Templates** and the policies actually applied. [Policy templates](https://learn.microsoft.com/en-us/microsoft-agent-365/admin/policy-template) bundle supported policies, not arbitrary MRM fields or a universal environment-scoped enforce/report-only switch. Verify scenario/release limitations and actual Entra authentication before relying on runtime policy.
3. **Verify the firm's MRM gate.** The organization's workflow must check current Committee disposition and blocking conditions before an authorized administrator publishes/activates an in-scope agent. Retain the decision independently of the native security template.
4. **Backfill remediation for the agent that slipped through.** Treat the unapproved publication as a control failure. Quarantine or unpublish the agent pending Committee disposition; document the slip in Committee minutes; route the remediation memo to retention.
5. **Check all deployment paths.** Include new environments and channels in the approval/access review; do not infer universal blocking from store approval or from a one-time bulk template action.

**Verification.**

- Every in-scope publication has the firm's MRM disposition and actual supported request/template evidence.
- A controlled negative test demonstrates the firm's configured approval gate for each relevant channel; missing native support remains an explicit gap.
- Administrative access and exceptions are documented and minimized; do not invent template-bypass roles.

**Cross-link.** [Control 2.25 — Agent 365 Admin Center Governance Console](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md) · [Control 2.3 — Change Management and Release Planning](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md).

---


## §9 Issue 9 — Model-Retirement Evidence Missing

**Symptom.** A Tier 1 agent was retired, but the firm cannot produce, on demand, the **retirement decision** (who, when, why), the **last validation memo** that was current at retirement, and the **final monitoring snapshot** (Foundry evaluator results, Copilot Studio analytics, Agent 365 usage). Retired-model evidence gap.

**Root causes (typical).**

- Retirement was treated as a deletion / decommissioning task rather than as a model lifecycle event.
- No retirement workflow existed to capture the artifacts before the underlying surfaces were torn down.
- Inventory record was deleted instead of being marked retired with retention preserved.

**Resolution.**

1. **Reconstruct the artifacts retroactively.**
    - **Decision and timing.** Reconstruct from change history (Power Platform admin change log), Sentinel events (Control 3.9), unified audit log (Control 1.7), and the change ticket.
    - **Last validation memo.** Retrieve from the 17a-4(f) retention path; if the memo was never routed there, retrieve from the original SharePoint location and route under change control.
    - **Final monitoring snapshot.** Retrieve from Foundry evaluator history (within retention window), Copilot Studio analytics export (where retained), and any Sentinel events captured around the retirement window.
2. **File a reconstruction memo.** Document the reconstruction methodology, the sources used, the gaps that could not be reconstructed (with rationale), and Committee disposition. The reconstruction memo itself becomes evidence and is routed to retention.
3. **Update the model-retirement workflow going forward.** Add explicit steps to the workflow:
    - Follow the **Discover → Inventory → Evaluate → Approve → Deploy → Monitor → Repeat** lifecycle in [Microsoft's Copilot Studio model lifecycle guidance](https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/plan-agent-model-lifecycle); do not rely on a copied model list.
    - Capture the retirement decision (Committee minute reference, owner, effective date).
    - Snapshot the current Agent Card, validation memo, Foundry evaluator dataset and results, and final monitoring report.
    - Route all artifacts to 17a-4(f) retention before any underlying surface is torn down.
    - Mark the inventory record **retired** (do not delete); retain the inventory row for the longer of the regulatory retention period and the firm's policy.
4. **Drill the workflow.** Run a tabletop exercise on the next planned retirement to confirm the workflow operates end-to-end.

**Verification.**

- Reconstruction memo is filed and accepted by the Committee.
- The updated model-retirement workflow is published, owned, and referenced in the MRM policy.
- The next planned retirement produces a complete artifact set on first attempt.

**Cross-link.** [Control 1.7 — Comprehensive Audit Logging and Compliance](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) · [Control 1.9 — Data Retention and Deletion Policies](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md) · [Control 3.9 — Microsoft Sentinel Integration](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md).

---

## §10 Issue 10 — PowerShell Helper Returns Status=Error

**Symptom.** A PowerShell helper from [`powershell-setup.md`](powershell-setup.md) (model-inventory enumeration, manifest export, MRM compliance report, model-change monitoring, end-to-end configuration) returns `Status=Error`, throws an unhandled exception, or exits non-zero.

**Common causes and resolutions.**

| Cause | Symptom | Resolution |
|---|---|---|
| **Microsoft Graph throttling (HTTP 429)** | Intermittent failures on inventory enumeration; `Retry-After` header in error | Apply exponential backoff per [`_shared/powershell-baseline.md`](../../_shared/powershell-baseline.md); reduce page size; partition by environment |
| **Required module missing or wrong version** | `The term 'Add-PowerAppsAccount' is not recognized`; cmdlet-not-found | Pin module versions per the baseline; reinstall with `-Force -Scope CurrentUser`; verify with `Get-Module -ListAvailable` |
| **Not connected to Power Platform admin endpoint** | `Unauthorized`; empty result sets | Re-run `Add-PowerAppsAccount` (or the service-principal variant); confirm the connection token has not expired |
| **Not connected to Exchange Online** | `Search-UnifiedAuditLog` not recognized | Re-run `Connect-ExchangeOnline` with the appropriate role assignment |
| **Insufficient role assignment** | `Forbidden` on specific endpoints | Confirm the executing principal holds the documented roles (Power Platform Admin, Entra Global Reader for inventory, Purview Compliance Admin where DSPM for AI is queried) |
| **Dataverse compatibility** | Date / decimal serialization mismatch | Use the baseline's Dataverse-safe serialization helpers; do not pass raw `[datetime]` to Dataverse without ISO-8601 conversion |
| **Missing inventory CSV / file path** | `[WARN] Model inventory not found` | Confirm the `-ModelInventoryPath` parameter resolves to a real file; the helper will create a template if absent — verify the template was not committed as production inventory |

**Resolution (general).**

1. Re-read [**PowerShell Authoring Baseline for FSI Implementations**](../../_shared/powershell-baseline.md). It is the authoritative source for module pinning, mutation safety (`-WhatIf` / `SupportsShouldProcess`), and SHA-256 evidence emission.
2. Run the helper with `-Verbose` and `-Debug` to surface the failing call.
3. For Graph throttling, capture the `Retry-After` header and back off; for persistent throttling, open a Microsoft Support case.
5. Capture the failing run output and command line in the incident record before retrying.

**Verification.**

- Helper output uses the documented `Clean / Anomaly / Pending / NotApplicable / Error` vocabulary, not `OK`. Unsupported inventory/Foundry adapters remain `Error` with `ManualEvidenceRequired` until separately collected evidence is reconciled; an emitted folder or matching hashes do not prove complete inventory or validation.

**Cross-link.** [`_shared/powershell-baseline.md`](../../_shared/powershell-baseline.md) · [Control 3.9 — Microsoft Sentinel Integration](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md).

---

## §11 Issue 11 — Examiner Asks for Inventory of In-Scope Agents and Firm Cannot Produce in Real Time

**Symptom.** A regulator (OCC, Federal Reserve, SEC, FINRA, FDIC, NYDFS) requests, during an examination, an inventory of AI agents the firm treats as models under SR 26-2 (formerly SR 11-7). The firm cannot produce the inventory within the requested window (typically same-day or next business day for routine pulls). Process and tooling gap.

**Root causes (typical).**

- Inventory exists as a manually maintained SharePoint list updated quarterly; the as-of inventory at the examiner's requested date is reconstructable but not at-hand.
- The firm's authoritative register has not been reconciled with supported Power Platform/Agent 365 inventories and bounded Purview activity evidence.
- No examination-readiness rehearsal has been performed; the runbook to assemble the response packet does not exist.

**Resolution.**

1. **Stand up a quarterly inventory pull as the standing baseline.** Use the inventory PowerShell helper from [`powershell-setup.md`](powershell-setup.md) on a scheduled quarterly cadence; sign and route the output to 17a-4(f) retention as the as-of-quarter inventory of record. The as-of-quarter snapshots become the firm's defensible baseline for examiner pulls.
2. **Pre-stage an ad-hoc on-demand query.** Document and rehearse the procedure to run the helper on demand against the current state, reconcile against DSPM for AI and the manual list, and produce an examiner-ready package within a documented SLA (recommended: same business day for routine pulls).
3. **Pre-stage an examination-readiness rehearsal.** At least annually — ideally semi-annually — run a tabletop exercise: a senior officer (Compliance Officer or designee) issues a simulated examiner request; the team executes the procedure; the AI Governance Lead reviews the package for completeness, hedged language, and alignment with the MRM policy. Record the rehearsal as a finding-and-remediation cycle.
4. **Designate a single inventory of record.** The MRM policy must designate which of DSPM for AI, the Power Platform admin enumeration, or the manual SharePoint list is the inventory of record. The other sources are corroborating. Reconciliation deltas are tracked as findings until closed.
5. **Coordinate examiner-facing communications through Compliance and Legal.** No individual administrator transmits inventory or evidence directly to a regulator. The package is reviewed and transmitted by Compliance / Legal.

**Verification.**

- Quarterly inventory snapshots exist for the trailing four quarters under 17a-4(f) retention.
- The ad-hoc procedure has been rehearsed within the trailing 12 months and the rehearsal record is filed.
- The MRM policy designates the inventory of record.

**Cross-link.** [Control 3.1 — Agent Inventory and Metadata Management](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md) · [Control 1.9 — Data Retention and Deletion Policies](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md) · [Control 2.12 — Supervision and Oversight (FINRA Rule 3110)](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md).

---

## §12 Escalation Paths

The matrix below describes **when** to escalate and to **whom**. Substantive MRM judgments — model tiering, validation disposition, effective challenge, model retirement — are reserved to the MRM Committee and the independent validation function and are not delegable to administrators.

| Trigger | Escalate To | Purpose |
|---|---|---|
| Tier 1 agent in production with missing or stale validation evidence | **MRM Committee** (Chair + Model Risk Manager) | Validation disposition; quarantine or compensating-control direction |
| Validator-independence finding (SR 26-2 §V (formerly SR 11-7 §V)) | **MRM Committee** + **Compliance Officer** | Charter remediation; re-validation direction |
| Vendor model in production without assessment | **MRM Committee** + **Vendor Risk Management** (Control 2.7) | Vendor-model assessment; disposition |
| Material model change (vendor-driven default migration) detected post-fact for Tier 1 | **MRM Committee** + **Compliance Officer** | Impact assessment; disclosure decision |
| 17a-4(f) retention gap on validation evidence or Committee minutes | **Compliance Officer** + **Records Management** | Books-and-records remediation; potential self-disclosure decision |
| Examiner / regulator request the firm cannot satisfy in-window | **Compliance Officer** + **Legal** (immediate) | All examiner-facing communications coordinated; rehearsal failure tracked as a finding |
| Subpoena, litigation hold, or active examination touching an in-scope agent | **Legal** (immediate) | Preservation direction; remediation gating |
| Microsoft surface defect impacting MRM evidence (DSPM for AI, Foundry evaluators, Agent 365) | **Microsoft Support** (Premier / Unified per the firm's contract) | Vendor-side root-cause and resolution; evidence collection for the firm's record |
| Cross-jurisdictional examination, novel regulatory question, or potential rule violation | **External counsel** (via Legal) | Specialist guidance |

**Examiner-facing communication — non-delegation.** No administrator, helper script, or evidence-collection tool transmits inventory, validation memos, Committee minutes, or any other record directly to a regulator, examiner, or external auditor. **All examiner-facing communications are coordinated through Compliance and Legal.** Administrators provide the underlying evidence artifacts on request and, where appropriate, attend in a technical-support capacity at the direction of Compliance / Legal.

**Microsoft Support engagement.** When opening a Premier / Unified Support case for a surface defect, attach the diagnostic output from [§10](#10-issue-10-powershell-helper-returns-statuserror), identify affected surfaces and label the case severity per the firm's support contract. Retain the case correspondence as evidence; route to 17a-4(f) retention if the case touches an in-scope model artifact.

---

## §13 Cross-References

**Sibling playbooks.** [portal-walkthrough.md](portal-walkthrough.md) · [powershell-setup.md](powershell-setup.md) · [verification-testing.md](verification-testing.md)

**Closely related controls.**

- [Control 1.7 — Comprehensive Audit Logging and Compliance](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md)
- [Control 1.9 — Data Retention and Deletion Policies](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md)
- [Control 2.3 — Change Management and Release Planning](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md)
- [Control 2.7 — Vendor and Third-Party Risk Management](../../../controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md)
- [Control 2.12 — Supervision and Oversight (FINRA Rule 3110)](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md)
- [Control 2.25 — Agent 365 Admin Center Governance Console](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md)
- [Control 2.26 — Entra Agent ID Identity Governance](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md)
- [Control 3.1 — Agent Inventory and Metadata Management](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md)
- [Control 3.9 — Microsoft Sentinel Integration](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md)

**Shared baselines.** [`_shared/powershell-baseline.md`](../../_shared/powershell-baseline.md)

**External references.**

- OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12) — Sound Practices for Model Risk Management
- Federal Reserve SR 26-2 (formerly SR 11-7) — Supervisory Guidance on Model Risk Management
- FDIC FIL-15-2026 — FDIC adoption of revised interagency Model Risk Management guidance (April 17, 2026)
- FFIEC IT Examination Handbook — Management; Information Security
- FINRA Rule 3110 (Supervision); FINRA Rule 4511 (Books and Records)
- SEC Rule 17a-3 / 17a-4 (Recordkeeping; 17a-4(f) WORM retention)
- SOX §§ 302 / 404 (Internal Controls over Financial Reporting)
- GLBA 501(b) (Safeguards Rule); NYDFS 23 NYCRR 500
- FINRA RN 25-07 (workplace modernization — RFC, contextual only)

---

**Last Verified:** 2026-11-09 — targeted inventory, evaluator, template, retention and helper-contract documentation corrections; no tenant UI, screenshots or execution.

*Updated: November 2026 | Version: v1.6.2 | UI Verification Status: Needs Review (targeted documentation-only corrections)*
