# Verification & Testing — Control 2.6: Model Risk Management (OCC Bulletin 2026-13 / SR 26-2 — formerly OCC 2011-12 / SR 11-7)

> **Examiner-defensible verification package** for [Control 2.6 — Model Risk Management Alignment with OCC Bulletin 2026-13 / SR 26-2 (formerly OCC 2011-12 / SR 11-7)](../../../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md). This playbook produces, signs, and retains the artifacts required to demonstrate to the OCC, Federal Reserve, FDIC, NYDFS, FINRA, SEC, and Internal Audit that the firm's **Model Risk Management program** is operating with respect to the AI agents in scope — not that Microsoft tooling is configured.
>
> **Audience:** Compliance Officer, Internal Audit, MRM Committee secretariat, Model Risk Manager (independent validation function), AI Governance Lead. The detailed portal navigation and PowerShell automation that *produce* the evidence consumed here are in the sister [Portal Walkthrough](./portal-walkthrough.md) and [PowerShell Setup](./powershell-setup.md) playbooks; this playbook focuses on the audit and examination question: **is the firm's MRM program actually operating with these agents in it, and is the MRM Committee accepting the validation?**
>
> **Last UI verified:** April 2026.

---

## Document Conventions

| Convention | Value |
|---|---|
| Hedged regulatory language | This playbook **supports compliance with**, but does not by itself ensure compliance with, OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12), Federal Reserve SR 26-2 (formerly SR 11-7), FDIC FIL-22-2017, FFIEC IT Examination Handbook, FINRA Rule 3110 (Supervision), FINRA Rule 4511 (Books and Records), FINRA RN 25-07 (workplace modernization — RFC, contextual only), SEC Rules 17a-3 / 17a-4 (Recordkeeping), SOX §§ 302 / 404, GLBA § 501(b), CFTC Regulation 1.31, and NYDFS 23 NYCRR Part 500. A clean execution of every test in this playbook **does not guarantee** regulatory compliance, **does not replace** the firm's Model Risk Management Committee, **does not replace** independent model validation by qualified personnel, **does not replace** the effective-challenge process required by SR 26-2 (formerly SR 11-7), and **does not replace** the registered-principal supervisory review required by FINRA Rule 3110. |
| Canonical role names | Per [`docs/reference/role-catalog.md`](../../../reference/role-catalog.md). The roles relevant to this playbook are: **Model Risk Manager** (independent validation function — second line), **MRM Committee** (governance body), **AI Governance Lead**, **Compliance Officer**, **Internal Audit** (third line), **AI Administrator**, **Power Platform Admin**, **Purview Compliance Admin**, **Entra Global Reader** (read-only witness). |
| Run identifier | Each verification cycle is tagged `MRM26-yyyyMMdd-HHmmss-<8charGuid>` and embedded in every evidence record and artifact filename. |
| Cycle cadence | Pre-deployment (§2), quarterly ongoing-monitoring (§3), risk-commensurate outcomes-analysis (§4 — *not* fixed annual), per-vendor-event vendor-model (§5), per-MRM-Committee-meeting effective-challenge (§6), continuous retention (§7), quarterly sovereign parity (§8), per-retirement event (§9), on-demand examination rehearsal (§10). |
| Scoring | Every test emits one of `Clean / Anomaly / Pending / NotApplicable / Error` per §11. The MRM Committee — not this playbook — accepts or rejects the underlying validation. |
| Evidence retention | Six (6) years on 17a-4(f)-compliant media (Purview retention label with deletion lock, or an approved 17a-4(f) vendor) for: model-classification decisions, Agent Cards, validation memos, MRM Committee minutes, monitoring reports, outcomes-analysis runs, vendor-model dispositions, and retirement records. The first two years must be readily accessible. |

> **Non-substitution.** Microsoft Purview DSPM for AI, the Agent 365 Admin Center, the Power Platform CoE export, Microsoft Copilot Studio Analytics, Azure AI Foundry monitoring and evaluators, and Microsoft Entra Agent ID are **inventory, evaluation, and evidence-collection surfaces**. They do **not** replace, and must not be presented to the MRM Committee or to examiners as a substitute for, the firm's MRM Committee, independent validation function, effective-challenge process, three-lines-of-defense governance, registered-principal supervision under FINRA Rule 3110, or 17a-4(f) books-and-records retention.

---

## §1 Verification Scope

### 1.1 What this playbook verifies — and what it does not

| Question this playbook *does* answer | Question this playbook *does not* answer |
|---|---|
| Is every AI agent that meets the firm's model-classification criteria recorded in the firm's model inventory? | Is every AI agent in the tenant a "model"? (Classification is an MRM judgement, not a tool output.) |
| Has each in-scope agent been pre-deployment validated by personnel functionally independent of the model owner / developer? | Is the validation methodology adequate? (That is the MRM Committee's judgement.) |
| Has the MRM Committee accepted the validation, with effective-challenge questions and dispositions documented in minutes? | Does acceptance equal regulatory compliance? (It does not.) |
| Are ongoing-monitoring reports produced quarterly, with thresholds, named owners, and breach escalation to the firm's IR / RCA workflow? | Are the thresholds set at the right values? (That is a model-risk-policy decision.) |
| Are vendor-model changes (Microsoft default-model migration, Foundry deprecations, Anthropic Claude availability) detected and dispositioned **before** they take effect? | Will Microsoft ship a model change without notice? (This is a vendor-risk concern handled in Control 2.7.) |
| Is validation evidence retained on 17a-4(f)-compliant media for 6 years? | Is the firm's retention vendor itself 17a-4(f)-attested? (That is a vendor-due-diligence question.) |

### 1.2 Population of in-scope agents

The verification population is the **set of AI agents that the firm's model-classification process has classified as Tier 1 or Tier 2**. The population is anchored to three independent sources reconciled together:

| Source | Surface | What it provides | Reconciliation rule |
|---|---|---|---|
| **A. Authoritative AI inventory** | Microsoft Purview DSPM for AI inventory export (cross-reference [Control 1.6](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md)) | Every Copilot, Copilot Studio, Foundry, and Entra-registered AI app the tenant has produced or exposed | Source of truth for "does this agent exist in the tenant?" |
| **B. Agent 365 Admin Center inventory** | Agent 365 Admin Center → Agents (cross-reference [Control 2.25](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md)) | Every Agent 365-surfaced agent with publication / activation approval, governance template, owner, and license state | Source of truth for "is this agent governance-bound?" |
| **C. Power Platform CoE export** | CoE Starter Kit → Copilot Studio inventory export (CSV / Power BI) | Every Copilot Studio agent across managed environments with environment, owner, last-modified, model selection | Source of truth for "is this agent under Power Platform governance?" |

**Reconciliation produces a single in-scope register.** Every agent that appears in source A but not in source B is investigated as a potential governance gap (escalate to [Control 2.25](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md)) or as orphaned (escalate to [Control 3.6](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md)). Every agent in source C without a corresponding entry in source A is flagged as a DSPM coverage gap.

### 1.3 Model-tiering coverage check

For each agent in the reconciled register, confirm exactly one of the following classifications has been recorded by the firm's MRM-designated classifier (typically the Model Risk Manager with input from the AI Governance Lead and business owner):

| Classification | MRM treatment | Verification expectation |
|---|---|---|
| **Tier 1** (high — material business impact, customer decisions, financial calculations, risk scoring) | Full MRM treatment with independent validation | In §2–§9 below |
| **Tier 2** (medium — customer-facing recommendations, significant but not material impact) | Full MRM treatment with independent validation | In §2–§9 below |
| **Tier 3** (low — internal use, minimal business impact) | Lightweight self-assessment plus second-line review | Subset coverage in §2–§9; not the focus of this playbook |
| **Non-model** (information retrieval only, internal productivity, no decision influence) | Standard agent governance only — out of scope for MRM | Recorded with rationale; periodically re-evaluated by Compliance |

**Coverage assertion:** every agent in the reconciled register has exactly one classification, with rationale, classifier identity, classifier date, and classifier-independence statement. Any agent without a classification is `Pending` and the MRM Committee secretariat is notified within five business days.

### 1.4 Evidence record schema

Every test in §2–§10 emits one JSON evidence record conforming to the following schema. The §10.4 examination-readiness pack assembler refuses to publish a pack containing a record that fails schema validation.

```json
{
  "control_id": "2.6",
  "run_id": "MRM26-20260415-093012-a1b2c3d4",
  "run_timestamp": "2026-04-15T09:30:12Z",
  "tenant_id": "11111111-2222-3333-4444-555555555555",
  "tenant_display_name": "Contoso Bank, N.A.",
  "cloud": "Commercial",
  "namespace": "PREDEPLOY | MONITOR | OUTCOMES | VENDOR | CHALLENGE | RETAIN | SOV | RETIRE | EXAM",
  "agent_id": "agt-22001",
  "agent_name": "Wealth-Mgmt Investment-Calculator",
  "model_tier": "1",
  "underlying_model": "GPT-5 (Foundry)",
  "underlying_model_version": "2026-03-15",
  "criterion": "VC-1",
  "subject_type": "validation_memo | committee_minute | monitoring_report | foundry_eval_run | vendor_disposition | retention_label | sov_attestation | retirement_record",
  "status": "Clean | Anomaly | Pending | NotApplicable | Error",
  "assertion": "<plain-English statement of what was tested>",
  "observed_value": { "...": "..." },
  "expected_value": { "...": "..." },
  "evidence_artifacts": ["validation-memo-agt-22001-2026Q1.pdf"],
  "evidence_sha256": "f3a1...",
  "regulator_mappings": ["OCC-2011-12","SR-11-7","FINRA-3110","FINRA-4511","SEC-17a-4","SOX-404"],
  "operator_upn": "model.risk.manager@contoso.com",
  "mrm_committee_acceptance_ref": "MRMC-2026Q1-min-§4.b",
  "schema_version": "1.0"
}
```

---

## §2 Pre-Deployment Validation Evidence Checklist (PREDEPLOY namespace)

**Criterion mapping:** Control 2.6 Verification Criteria 1, 2, 3, 4 (pre-deployment subset), 5.

For **every agent classified Tier 1 or Tier 2** in §1.3, confirm the following five evidence artifacts exist, are dated, are signed, are version-pinned, and are retained per §7.

### 2.1 Evidence artifact 1 — Model-classification decision

| Item | Expectation | Source |
|---|---|---|
| Classification (Tier 1 / 2 / 3 / Non-model) | Recorded with a written rationale ≥ 200 words referencing the OCC Bulletin 2026-13 (formerly OCC 2011-12) model definition | Model inventory record (Dataverse / SharePoint per [Portal Walkthrough §3](./portal-walkthrough.md)) |
| Classifier identity | Named individual, role, employee ID | Inventory record |
| Classifier independence statement | "The classifier is not the model owner / developer for this agent" or, where the same person plays both roles, an explicit second-line counter-signature | Inventory record + e-signature |
| Classification date | UTC timestamp; not back-dated more than 5 business days from approval | Inventory record version history |
| Re-classification trigger | Recorded next-review date, plus material-change triggers (model change, knowledge-source change, business-purpose change) | Inventory record |

`Anomaly` if any field is missing. `Pending` if the agent is in pre-classification triage and within the 30-day grace period defined in the firm's model risk policy.

### 2.2 Evidence artifact 2 — Agent Card

The Agent Card is the firm's plain-language model card. It is the document the validators read first and the document the MRM Committee references.

Required sections (verifier checks each is present and non-empty):

1. **Intended use** — what business decisions or recommendations the agent supports
2. **Out-of-scope use** — what the agent must not be used for
3. **Data** — every knowledge source, RAG corpus, training input, and customer-data category the agent touches (cross-reference [Control 2.16](../../../controls/pillar-2-management/2.16-rag-source-integrity-validation.md))
4. **Underlying model and version** — the specific foundation model and provider; "Copilot Studio default" is **not** acceptable per the control's underlying-model admonition
5. **Limitations** — failure modes, edge cases, populations or scenarios where the agent is known to underperform
6. **Performance benchmarks** — quantitative results from pre-deployment outcomes analysis (§4)
7. **Known failure modes** — categorical list with mitigation or compensating control
8. **Change history** — every prompt change, knowledge-source change, model change, with date, approver, and material/non-material classification

`Anomaly` if any of sections 1–7 is empty for a Tier 1 agent or if section 8 has no entries since the agent's last validation.

### 2.3 Evidence artifact 3 — Pre-deployment validation memo

The validation memo is authored by **personnel functionally independent of the model owner / developer**, per SR 26-2 (formerly SR 11-7) § V. Internal second-line MRM staff satisfy the independence test; external assessment is one way to demonstrate independence (often used for Tier 1) but is not required and is not equivalent.

| Section | Expectation |
|---|---|
| Conceptual soundness | Validator's assessment of design appropriateness, methodology, assumptions, and stated limitations — citing the Agent Card, DSPM for AI inventory record, and Agent 365 governance template binding |
| Data assessment | Validator's review of knowledge sources for appropriateness, quality, representativeness (cross-reference [Control 2.16](../../../controls/pillar-2-management/2.16-rag-source-integrity-validation.md)) |
| Outcomes-analysis interpretation | Validator's reading of the Foundry evaluator runs (§4) — including any evaluator scores below the firm's threshold and the validator's recommendation (accept / accept-with-condition / reject) |
| Implementation verification | Validator's confirmation that the agent in production matches the validated configuration — includes manifest hash, governance-template binding, Entra Agent ID binding (cross-reference [Control 2.26](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md)) |
| Limitations and caveats | Validator's plain statement of what the validation does not cover |
| Validator identity & independence | Named validator, role, line-of-defense, independence statement |
| Validator signature | Wet, e-signature, or cryptographic signature with timestamp |

`Anomaly` if the validator and the model owner / developer are the same individual without a documented compensating second-line counter-signature.

### 2.4 Evidence artifact 4 — MRM Committee minutes

For each Tier 1 agent, the MRM Committee must have formally accepted the validation. Minutes must reference the agent by ID and capture:

- Date and attendees (with line-of-defense designation)
- Specific challenge questions raised by the independent validator and other Committee members not involved in model development
- Disposition of each challenge question (accepted / requires-condition / requires-revalidation / rejected)
- Conditions imposed on production use (if any)
- Final decision: **approved / approved-with-conditions / rejected**
- Next scheduled re-validation date (risk-commensurate; see §4.1)
- Secretariat signature

`Anomaly` if minutes reference the agent but do not record at least one specific challenge question and disposition. `Anomaly` if the decision is "approved" but at least one Committee member counter-flagged the agent and no rationale for overriding is recorded.

### 2.5 Evidence artifact 5 — Identity attribution

Confirm the agent has a Microsoft Entra Agent ID (or, where Entra Agent ID is not yet at parity, a documented compensating identity binding) recorded in the inventory record. Cross-reference [Control 2.26](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md). Without an attributable identity the agent cannot be supervised under FINRA Rule 3110 and cannot be retired cleanly under §9.

### 2.6 PREDEPLOY scoring

| Status | Condition |
|---|---|
| `Clean` | All five evidence artifacts present, dated, signed, retained per §7, and MRM Committee minutes reference the agent. |
| `Anomaly` | Any artifact missing a required field; classifier or validator independence cannot be demonstrated; Committee minutes lack challenge-and-disposition. |
| `Pending` | Agent is within the firm's documented pre-production grace window; classification or validation is in flight with target completion date. |
| `NotApplicable` | Agent re-classified as Non-model with rationale; or agent retired before validation cycle (cross-reference §9). |
| `Error` | Inventory record unreachable; e-signature service down; evidence-store retrieval failure. Re-run cycle and escalate. |

---

## §3 Ongoing-Monitoring Evidence Test (MONITOR namespace)

**Criterion mapping:** Control 2.6 Verification Criteria 4 (ongoing-monitoring subset), 6.

**Cadence:** Quarterly per agent at minimum; more frequently if the firm's model risk policy requires.

### 3.1 Per-agent monitoring report

For each in-scope agent, the firm's monitoring report for the quarter combines:

| Source | What the validator consumes |
|---|---|
| Copilot Studio Analytics | Conversation count, escalation / fallback rate, user-satisfaction (CSAT) where collected, response latency, error rate |
| Azure AI Foundry monitoring (where the underlying model runs on Foundry) | Token usage, latency percentiles, model-side error rates, throttling events, content-filter triggers |
| Microsoft Purview DSPM for AI interaction reports | Sensitive-prompt rate, sensitive-response rate, sentiment, customer-comment topic clustering, label-applied rate |
| Application Insights / Azure Monitor (where wired up by the agent's developer) | Custom application telemetry: tool-call counts, knowledge-source-hit rates, downstream API latency |

The validator (second line, not the model owner) signs a one-page summary stating: KPIs for the quarter, drift versus prior quarters, threshold-breach count, and whether the validator recommends continued operation or escalation.

### 3.2 Threshold-breach routing

| Item | Expectation |
|---|---|
| Thresholds defined per agent | Documented in the model inventory and Agent Card |
| Alerts route to a named owner | Single named individual (not a distribution list) plus secondary on-call; recorded in inventory record |
| Threshold breach → IR ticket | Every breach opens an incident per [Control 3.4](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md), with Root Cause Analysis |
| RCA feedback loop | RCA findings feed back to the MRM Committee at the next regular meeting; material findings trigger out-of-cycle review |

`Anomaly` if any in-scope Tier 1 / Tier 2 agent lacks defined thresholds, lacks a named owner, or has a breach this quarter without a corresponding [Control 3.4](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) IR ticket.

### 3.3 MONITOR scoring

| Status | Condition |
|---|---|
| `Clean` | Quarterly monitoring report produced for the agent, signed by an independent validator, with thresholds, owner, breach count, and RCA references. |
| `Anomaly` | Report produced but missing signature; thresholds undefined; owner unnamed; breach without IR ticket. |
| `Pending` | Quarter not yet closed; report in draft within firm's documented production window (typically 15 business days after quarter end). |
| `NotApplicable` | Agent newly deployed mid-quarter; first full quarter not yet observable. |
| `Error` | Telemetry surface unavailable; analytics export failed. Re-run after surface restored. |

---

## §4 Outcomes-Analysis Evidence Test (OUTCOMES namespace)

**Criterion mapping:** Control 2.6 Verification Criterion 4 (outcomes-analysis subset).

### 4.1 Risk-commensurate cadence — not fixed annual

SR 26-2 (formerly SR 11-7) § V requires outcomes analysis at a frequency commensurate with **risk, model complexity, and change activity** — not on a fixed annual basis. The firm's model risk policy must define how cadence is set per agent. The verifier confirms the cadence is documented and being followed; the verifier does **not** opine on whether the cadence is correct.

| Driver | Effect on cadence |
|---|---|
| Tier 1 agent, customer-facing | More frequent (commonly quarterly or per material change) |
| Tier 2 agent, internal decision support | Commonly semi-annual or per material change |
| Material change (model, prompt, knowledge source) | Outcomes-analysis run before the change is approved for production |
| Vendor-driven model change | Outcomes-analysis run as part of vendor-model disposition (§5) |
| Threshold breach (§3) | Out-of-cycle outcomes-analysis run as part of RCA |

### 4.2 Foundry built-in evaluator coverage

For each outcomes-analysis run, confirm the following Foundry built-in evaluators were exercised against a representative evaluation dataset (the dataset itself is approved by the MRM Committee and version-controlled):

| Evaluator family | Specific evaluators | What it tells the validator |
|---|---|---|
| Quality | groundedness, relevance, coherence, fluency | How accurately and coherently the agent answers from its grounding |
| Safety | hate / unfairness, violence, sexual, self-harm, protected materials | Whether the agent produces or amplifies disallowed content |
| Agent-specific | tool-call accuracy, task-completion, intent-resolution | Whether the agent invokes the correct tools, completes multi-step tasks, and resolves user intent |
| Custom (firm-defined) | FSI-specific evaluators (e.g., Reg BI suitability heuristics, AML red-flag detection) | Validator-defined business-specific quality checks |

**Evaluation dataset expectations:**

- Representative of intended-use scenarios documented in the Agent Card
- Includes adversarial / edge-case scenarios proportionate to risk tier
- Versioned and retained alongside the run (so that re-runs are reproducible)
- Reviewed by the MRM Committee at least annually, or upon material change to intended use

### 4.3 Run record

Each Foundry evaluator run produces a record retained alongside the validation memo. The verifier confirms each run record contains:

- Agent ID and version (manifest hash)
- Underlying model and version at the time of the run
- Evaluation dataset name and version
- Per-evaluator score (numeric) plus any failed thresholds
- Validator's interpretation: pass / pass-with-condition / fail
- Validator signature
- Cross-reference into the MRM Committee minutes that disposed the run

### 4.4 OUTCOMES scoring

| Status | Condition |
|---|---|
| `Clean` | Run executed within the cadence defined in the model risk policy; all relevant evaluator families exercised; run record signed; Committee disposition recorded. |
| `Anomaly` | Run skipped beyond the policy-defined cadence; safety evaluators omitted for a Tier 1 / Tier 2 agent; run executed but no validator interpretation. |
| `Pending` | Run scheduled but not yet complete within policy window. |
| `NotApplicable` | Tier 3 or Non-model agent under firm's policy; or agent retired (§9). |
| `Error` | Foundry evaluator harness unavailable; dataset retrieval failure. |

---

## §5 Vendor-Model Governance Test (VENDOR namespace, SR 26-2 (formerly SR 11-7) § V)

**Criterion mapping:** Control 2.6 Verification Criterion 7. SR 26-2 (formerly SR 11-7) § V requires vendor-supplied models be validated with the same rigour as internally-developed models.

### 5.1 Vendor-event watchlist

For each Microsoft / vendor surface that can change the underlying model behind an in-scope agent, confirm the firm has a **subscribed** monitoring channel, a **named** disposition owner, and a **documented** lead time:

| Vendor event | Surface to monitor | Disposition owner | Required lead time |
|---|---|---|---|
| Copilot Studio default-model migration (e.g., GPT-5 → next default) | Microsoft 365 Message Center; Power Platform release plan | AI Governance Lead + Model Risk Manager | ≥ 30 days before effective date for Tier 1; per policy for lower tiers |
| Foundry model deprecation | Azure AI Foundry "Models" page; Azure Service Health | AI Administrator + Model Risk Manager | Per Microsoft published deprecation window |
| Foundry evaluator changes (judge-model updates, evaluator GA / deprecation) | Foundry release notes | Model Risk Manager | Before next outcomes-analysis run |
| Anthropic Claude availability changes in Copilot Studio (commercial-cloud and sovereign-cloud delta) | Copilot Studio release notes; sovereign roadmap | AI Governance Lead | Before publication / activation in production |
| Azure OpenAI Service model version pinning changes | Azure portal / Azure OpenAI release notes | AI Administrator | Before next in-scope agent deployment |
| Third-party connector / partner-model availability | Partner channel | AI Governance Lead | Per firm vendor-risk policy ([Control 2.7](../../../controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md)) |

### 5.2 Disposition record

For each vendor event affecting an in-scope agent, the firm produces a **vendor-model disposition record** before the event takes effect. The verifier confirms each record contains:

| Field | Expectation |
|---|---|
| Vendor event description | Short narrative + link to vendor announcement |
| Effective date (vendor-stated) | UTC timestamp |
| Disposition decision date | Must precede the effective date |
| Affected in-scope agents | List of agent IDs from the §1.2 register |
| Impact assessment | Per-agent: does this materially change behaviour, performance, safety, or supervisory profile? |
| Decision | accept-as-non-material / accept-with-revalidation / pin-to-prior-version / suspend agent / retire agent (cross-reference §9) |
| Re-validation reference | If "accept-with-revalidation": pointer to the §4 outcomes-analysis run executed against the new model |
| Agent Card and validation memo updates | Confirm both updated to reference the new underlying model and version |
| MRM Committee acceptance | Pointer to minutes accepting the disposition |
| Signatures | Disposition owner + Model Risk Manager + (for Tier 1) MRM Committee Chair |

`Anomaly` if a vendor event has taken effect in production without a dated disposition record, or if the disposition decision date is after the effective date (i.e., disposed retrospectively).

### 5.3 VENDOR scoring

| Status | Condition |
|---|---|
| `Clean` | All vendor-event channels subscribed with named owners; every event with potential in-scope impact has a dated, signed disposition record predating the effective date; Agent Card and validation memo updated. |
| `Anomaly` | Vendor event with in-scope impact dispositioned after effective date; Agent Card not updated to reflect new underlying model; subscription gap on a watchlist channel. |
| `Pending` | Vendor event detected; impact assessment in flight within firm's documented disposition window. |
| `NotApplicable` | Vendor event affects only Non-model agents under firm's classification. |
| `Error` | Vendor channel feed unavailable; disposition store unreachable. |

---

## §6 Effective-Challenge Test (CHALLENGE namespace)

**Criterion mapping:** Control 2.6 Verification Criterion 5; SR 26-2 (formerly SR 11-7) § III ("effective challenge").

> **Effective challenge is the cornerstone of SR 26-2 (formerly SR 11-7).** Microsoft tooling cannot perform it. This test confirms that the firm's MRM Committee minutes evidence challenge questions raised by personnel **not involved in model development** for each in-scope Tier 1 agent, and that those questions were dispositioned.

### 6.1 Per-Tier-1-agent assertions

For each Tier 1 agent reviewed in the quarter, the MRM Committee minutes must:

1. **Identify the challenger.** A named individual functionally independent of the model owner / developer raised at least one substantive challenge question. "Substantive" excludes administrative or scheduling questions.
2. **Record the question.** The challenge question is recorded verbatim or paraphrased with sufficient specificity to be examined later.
3. **Record the disposition.** The model owner / validator's response is recorded; the Committee accepted, conditionally accepted, or rejected the response.
4. **Record any conditions.** Conditions imposed on continued production use are tracked to closure in subsequent meetings (verifier traces forward at least one quarter).
5. **Independence of challenger.** The challenger is not the model owner, the model developer, or anyone reporting to the model owner. Where the challenger reports up through the same business line, a documented second-line counter-signature is required.

### 6.2 FINRA Rule 3110 supervisory linkage

For each Tier 1 agent that supports an in-scope FINRA business activity (broker-dealer customer interactions, investment recommendations, AML monitoring, trade surveillance, communications with the public), the verifier confirms the registered-principal supervisory layer ([Control 2.12](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md)) is linked into the MRM workflow:

| Linkage point | Expectation |
|---|---|
| Registered-principal sign-off on validation acceptance | Recorded in MRM Committee minutes or in a parallel supervisory log |
| Supervisory review of Communication Compliance findings ([Control 1.10](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md)) | Findings flow into the §3 monitoring report |
| Books-and-records preservation of supervisory review evidence | 6-year 17a-4(f) retention per §7 |

`Anomaly` if a Tier 1 agent supports an in-scope FINRA activity and no registered-principal sign-off appears in either the MRM minutes or the supervisory log for the quarter under review.

### 6.3 CHALLENGE scoring

| Status | Condition |
|---|---|
| `Clean` | Every Tier 1 agent in scope has at least one substantive challenge question and disposition recorded in minutes for the cycle; conditions tracked forward; FINRA Rule 3110 linkage in place where applicable. |
| `Anomaly` | Tier 1 agent reviewed without recorded challenge; challenger independence not demonstrable; conditions imposed but not tracked forward; FINRA linkage missing where required. |
| `Pending` | Committee meeting deferred within the firm's documented tolerance window. |
| `NotApplicable` | No Tier 1 agents in scope this cycle (rare; document the population check from §1.2). |
| `Error` | Minutes repository unreachable; secretariat signature service down. |

---

## §7 Retention Test (RETAIN namespace)

**Criterion mapping:** Control 2.6 Verification Criterion 9; SEC Rule 17a-4(f); FINRA Rule 4511; SOX § 802.

### 7.1 Population of records to retain

| Record class | Minimum retention | Acceptable medium |
|---|---|---|
| Model-classification decisions | 6 years (life-of-model + 6 years for Tier 1) | Purview retention label with deletion lock; or approved 17a-4(f) vendor |
| Agent Cards (every version) | 6 years (life-of-model + 6 years for Tier 1) | Purview retention label with version history; or approved 17a-4(f) vendor |
| Pre-deployment validation memos | 6 years | Purview retention label; or approved 17a-4(f) vendor |
| MRM Committee minutes | 7 years (firm-wide governance practice; minimum 6 for SEC 17a-4) | Purview retention label; or approved 17a-4(f) vendor |
| Quarterly monitoring reports | 6 years | Purview retention label; or approved 17a-4(f) vendor |
| Foundry outcomes-analysis run records (with evaluation datasets) | 6 years | Purview retention label; or approved 17a-4(f) vendor |
| Vendor-model dispositions | 6 years | Purview retention label; or approved 17a-4(f) vendor |
| Model-retirement records | 6 years from retirement date | Purview retention label; or approved 17a-4(f) vendor |

> Copilot Studio Analytics dashboards and Foundry monitoring dashboards are **not** 17a-4(f) WORM-compliant on their own. Periodic exports of these dashboards are the records of the business and must land in the retention medium above. Cross-reference [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) and [Control 1.9](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md).

### 7.2 Retention-label binding test

For a sample of 10 records (or 100% if fewer than 10 exist this cycle) drawn proportionally across record classes, the verifier confirms the binding of a Purview retention label with `retentionDuration ≥ 6 years` and `deletionLocked = true` (or, for vendor-stored records, the vendor's 17a-4(f) attestation reference). Confirm via Purview compliance portal or via `Get-RetentionCompliancePolicy` per [PowerShell Setup](./powershell-setup.md) and [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md).

### 7.3 Sample retrieve-and-restore test

For one record from each of the eight record classes, the verifier (Purview Compliance Admin or equivalent) executes a retrieval from the retention store and confirms:

| Test step | Expectation |
|---|---|
| Retrieval latency | Within firm's documented "readily accessible" SLA for records less than 2 years old (typically same business day) |
| Content integrity | SHA-256 of retrieved bytes matches the SHA-256 stored in the original evidence record |
| Immutability proof | Retention label still bound; deletion lock still enforced; tampering attempt would be auditable |
| Restoration to working location | Record can be restored to a read-only working location for examiner inspection without removing the immutability binding |

`Anomaly` if any sample record fails latency, integrity, immutability, or restoration. `Anomaly` if a record older than 2 years cannot be retrieved within the firm's documented "near-line" SLA.

### 7.4 RETAIN scoring

| Status | Condition |
|---|---|
| `Clean` | All eight record classes have policy-bound retention; sample of 10 + 8 retrieve-and-restore passes integrity and immutability checks. |
| `Anomaly` | Any record class lacks policy binding; sample retrieval fails; immutability binding broken; deletion-lock not enforced. |
| `Pending` | Retention policy migration in progress with documented target date. |
| `NotApplicable` | Record class produced zero records this cycle (document why). |
| `Error` | Purview surface unavailable; vendor 17a-4(f) portal unreachable. |

---

## §8 Sovereign-Cloud Parity Test (SOV namespace)

**Criterion mapping:** Control 2.6 Sovereign-cloud admonition; applies to GCC, GCC High, DoD tenants.

### 8.1 Surface-by-surface parity check

The Microsoft surfaces this control depends on have known parity gaps in sovereign clouds at the verification date. For tenants in GCC / GCC High / DoD, the verifier confirms the firm has identified the gap and has a compensating manual control in place — re-verified quarterly.

| Surface | Commercial behaviour | Sovereign expectation | Compensating control if absent |
|---|---|---|---|
| Microsoft Purview DSPM for AI inventory | Authoritative AI inventory across Copilot, Copilot Studio, Foundry, Entra-registered AI apps | Verify regional availability and connector parity per [Microsoft 365 Government roadmap](https://aka.ms/m365gov-roadmap) | Manual SharePoint-list inventory reconciled monthly to Power Platform CoE export and Agent 365 inventory; sourced from operational sweeps documented in the model risk policy |
| Azure AI Foundry evaluator harness | Built-in groundedness / safety / agent-specific evaluators | Verify Foundry availability and judge-model parity in Azure Government / DoD; some evaluators rely on commercial-cloud-hosted judge models | Documented manual evaluation procedure per agent tier; rubric scored by independent validator |
| Agent 365 Admin Center governance console | Publication / activation approval surface; governance templates | Microsoft has not announced sovereign parity at Agent 365 GA; cross-reference [Control 2.25](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md) | Manual change-ticket-driven publish / activate workflow; AI Governance Lead approval recorded in firm ticketing system with retention binding |
| Microsoft Entra Agent ID lifecycle workflows | Identity-bound agent governance | Verify lifecycle-workflow parity per [Control 2.26](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md) | Manual Entra service-principal-based identity binding with documented sponsor and review cadence |
| Anthropic Claude in Copilot Studio | Available in commercial cloud | Independently gated per region | Treat as unavailable for in-scope agents until verified; pin to GA Microsoft / Azure OpenAI models |

### 8.2 Quarterly dual-signed sovereign attestation

Each quarter, for sovereign tenants only, produce a dual-signed attestation:

| Field | Expectation |
|---|---|
| Cloud | GCC / GCC High / DoD |
| As-of date | Last business day of the quarter |
| Surface-by-surface parity statement | Available / partial / unavailable per surface |
| Compensating control statement | For each unavailable surface, the compensating control reference and its operating effectiveness |
| In-scope agent count under compensating controls | Number of agents whose MRM evidence depends on a manual compensating control this quarter |
| Re-check date | Start of next quarter |
| Signatures | AI Governance Lead + Compliance Officer |

### 8.3 SOV scoring

| Status | Condition |
|---|---|
| `Clean` | Tenant is Commercial (test passes by definition); or sovereign tenant with current quarterly dual-signed attestation and compensating controls demonstrably operating. |
| `Anomaly` | Sovereign tenant lacks current attestation; compensating control not demonstrably operating for an in-scope agent. |
| `Pending` | Attestation in production within firm's quarterly close window. |
| `NotApplicable` | Not applicable for Commercial tenants other than to record the cloud detection result. |
| `Error` | Cloud detection unavailable; sovereign roadmap reference unreachable. |

---

## §9 Model-Retirement Test (RETIRE namespace)

**Criterion mapping:** Control 2.6 Verification Criterion 10.

### 9.1 Per-cycle assertion

At least once per verification cycle (quarterly), the firm exercises its documented model-retirement / sunset workflow against a real in-scope agent. If no in-scope agent is being retired in the cycle, the firm exercises a tabletop walkthrough against a hypothetical retirement and records the artifacts the workflow would produce.

### 9.2 Retirement record

For each retirement (real or tabletop), the verifier confirms a retirement record exists containing:

| Field | Expectation |
|---|---|
| Agent ID and name | Matches the §1.2 register |
| Retirement decision date | Recorded in MRM Committee minutes |
| Retirement effective date | UTC timestamp; date the agent ceased availability |
| Reason for retirement | Business-driven / model-risk-driven / vendor-driven (model deprecation) / replacement / regulatory |
| Disposition of in-flight conversations and pending tasks | Drained, transferred to replacement, or terminated with user notification |
| Identity disposal | Entra Agent ID disabled; Power Platform solution archived; Agent 365 publication revoked |
| Knowledge-source / RAG corpus disposition | Retained for retention period or transferred to replacement agent (cross-reference [Control 2.16](../../../controls/pillar-2-management/2.16-rag-source-integrity-validation.md)) |
| Communications to users | Notification text retained |
| Evidence preservation | Development, validation, monitoring, outcomes-analysis, and retirement evidence bundled and bound to retention label per §7 |
| Retirement signatures | AI Governance Lead + Model Risk Manager + (for Tier 1) MRM Committee Chair |

### 9.3 Post-retirement orphan check

After retirement, confirm via [Control 3.6](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) detection cycles that the retired agent does not re-appear as an orphan. A re-appearance indicates the retirement was incomplete (typically: identity disabled but solution still resolvable in the tenant).

### 9.4 RETIRE scoring

| Status | Condition |
|---|---|
| `Clean` | At least one retirement (real or tabletop) exercised this cycle with all required record fields and signatures; post-retirement orphan check passes. |
| `Anomaly` | Retirement record missing fields; identity not disabled; evidence not preserved; retired agent re-appears as orphan in [Control 3.6](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) cycle. |
| `Pending` | Retirement in flight; effective date in future. |
| `NotApplicable` | Tabletop only this cycle; record the rationale. |
| `Error` | Retirement record store unreachable. |

---

## §10 Examination-Readiness Rehearsal (EXAM namespace)

**Criterion mapping:** Aggregates §1–§9; supports OCC, Federal Reserve, FDIC, NYDFS, FINRA, SEC examination requests.

> The examiner will not ask "is DSPM for AI configured?" The examiner will ask: *"Show me your AI model inventory. Pick one Tier 1 agent. Show me the validation memo, the MRM Committee minutes that accepted it, the last four quarters of monitoring, and the most recent outcomes-analysis run."* This rehearsal confirms the firm can produce those artifacts on demand within examiner-acceptable timeframes.

### 10.1 Rehearsal cadence

The rehearsal is exercised at least annually, and additionally:

- 30 days before any pre-announced regulatory examination
- After any material change to the MRM program, the model inventory schema, or the retention medium
- After any change in MRM Committee chair or Model Risk Manager

### 10.2 Rehearsal scenarios

The MRM Committee secretariat selects one scenario from each of the four families and times the response. Target SLAs are illustrative; the firm sets its own SLAs in the model risk policy.

| Scenario family | Examiner-style request | Target SLA |
|---|---|---|
| **Inventory completeness** | "Provide the full inventory of in-scope AI agents with tier, underlying model, validation status, and last-validation date." | ≤ 1 business day |
| **Per-agent validation pack** | "For agent [randomly selected Tier 1], provide the model-classification decision, Agent Card, pre-deployment validation memo, and MRM Committee minutes accepting the validation." | ≤ 2 business days |
| **Per-agent ongoing operations** | "For agent [randomly selected Tier 1 or Tier 2], provide the last four quarters of monitoring reports and the most recent outcomes-analysis runs." | ≤ 3 business days |
| **MRM Committee operating effectiveness** | "Provide the MRM Committee minutes for any approved Tier 1 agent over the past year, with documented effective-challenge questions and dispositions." | ≤ 3 business days |

### 10.3 Rehearsal record

Each rehearsal produces a record containing: scenario selected, agent or population queried, time-to-produce, completeness of produced bundle, gaps identified, and remediation actions assigned. The record is signed by the MRM Committee Chair and retained per §7.

### 10.4 Examination-pack assembler

For automated rehearsals, the firm runs an examination-pack assembler (a wrapper around the §1.4 evidence schema) that:

1. Accepts an agent ID or population filter
2. Pulls every PREDEPLOY, MONITOR, OUTCOMES, VENDOR, CHALLENGE, RETAIN, and RETIRE evidence record for the agent / population
3. Validates each record against the §1.4 schema; refuses to assemble if any record fails
4. Produces a single signed bundle (Merkle-rooted SHA-256 chain over the canonical-JSON evidence records) plus a plain-language summary suitable for examiner delivery
5. Logs assembly to the audit trail per [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md)

### 10.5 EXAM scoring

| Status | Condition |
|---|---|
| `Clean` | All four rehearsal scenarios completed within firm-set SLAs; pack assembler produces a complete, signed bundle; gaps remediated. |
| `Anomaly` | One or more rehearsal scenarios missed SLA; pack assembler refused due to schema-invalid records; gap identified without remediation owner. |
| `Pending` | Rehearsal scheduled; in flight within firm's documented tolerance. |
| `NotApplicable` | First-cycle rehearsal not yet due (newly stood-up MRM-for-AI program within firm's documented grace window). |
| `Error` | Pack assembler unavailable; evidence store offline. |

---

## §11 Scoring Rubric

Every test in §2–§10 emits exactly one of the following statuses. The MRM Committee secretariat aggregates statuses into the cycle attestation; **the MRM Committee — not this playbook — accepts or rejects the underlying validation**.

| Status | Definition | What it means for the cycle |
|---|---|---|
| **`Clean`** | The assertion was tested, the expected evidence was found, and it satisfies the criterion as defined in this playbook and in Control 2.6's Verification Criteria. | No remediation required for this assertion; the assertion contributes to a "clean" cycle. |
| **`Anomaly`** | The assertion was tested and the evidence was either missing, incomplete, unsigned, mis-dated, mis-bound to retention, lacking independence, lacking effective challenge, lacking owner, or otherwise non-conforming to the criterion. | Remediation owner assigned; remediation tracked to closure in next cycle; aggregated into the cycle attestation as an open finding to the MRM Committee. |
| **`Pending`** | The assertion is in flight within a firm-documented tolerance window — for example, quarterly monitoring report still in draft within the 15-business-day production window, or a vendor-event disposition under review within the firm's documented disposition window. | Re-tested at next cycle close; if still `Pending` past the tolerance window, automatically escalates to `Anomaly`. |
| **`NotApplicable`** | The assertion does not apply this cycle — for example, no Tier 1 agents in scope, or agent re-classified as Non-model with rationale, or no retirements (real) this cycle and tabletop performed instead. | Recorded with rationale; reviewed at next quarterly cycle to confirm the rationale still holds. |
| **`Error`** | The test could not be executed because of a tooling or surface failure (Purview portal unreachable, retention store offline, vendor channel feed down, signature service unavailable). The status reflects test execution, not the firm's compliance posture. | Re-run within firm-documented retry window; if persistent, escalate to AI Administrator and to the Microsoft support channel; document the workaround used to produce evidence in the interim. |

### 11.1 Cycle-level aggregation

The cycle attestation rolls up every assertion into a single MRM cycle status:

| Cycle status | Aggregation rule |
|---|---|
| **Clean cycle** | All assertions are `Clean`, `NotApplicable`, or `Pending` within tolerance. Zero `Anomaly` and zero `Error`. |
| **Cycle with findings** | One or more `Anomaly`. Cycle attestation lists each finding with remediation owner, target close date, and risk rating. MRM Committee disposes each finding at next regular meeting. |
| **Cycle blocked** | One or more `Error` that prevents production of evidence required by Control 2.6 Verification Criteria. Cycle attestation lists each blocker with restoration plan and interim manual control. |

### 11.2 What a clean cycle does not mean

> A clean cycle indicates the firm's MRM program is operating with the in-scope AI agents and producing the evidence the framework expects. **It does not mean** the agents are safe, the models are accurate, the validations are correct, the MRM Committee's challenge was sufficient, or the firm is in regulatory compliance. Those judgements remain with the MRM Committee, the Compliance Officer, the Internal Audit function, and the firm's regulators. The Microsoft surfaces this control depends on **support**, but do not **substitute for**, those judgements.

---

## Related Playbooks

- [Portal Walkthrough](./portal-walkthrough.md) — Step-by-step portal configuration that produces the inventory, Agent Card, and monitoring evidence consumed here
- [PowerShell Setup](./powershell-setup.md) — Automation scripts for inventory export, monitoring report generation, and pack assembly
- [Troubleshooting](./troubleshooting.md) — Common issues and resolutions

## Related Controls

- [Control 1.6 — Microsoft Purview DSPM for AI](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md) — Authoritative AI inventory feeding §1.2
- [Control 1.7 — Comprehensive Audit Logging](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) — 17a-4(f) WORM retention path for §7
- [Control 1.9 — Data Retention and Deletion](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md) — Retention schedule for validation evidence
- [Control 1.10 — Communication Compliance](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md) — Supervisory review feeding §6.2
- [Control 2.3 — Change Management](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md) — Vendor-driven change capture for §5
- [Control 2.7 — Vendor and Third-Party Risk Management](../../../controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md) — Vendor-model governance under SR 26-2 (formerly SR 11-7) § V
- [Control 2.12 — FINRA Rule 3110 Supervision](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) — Registered-principal linkage in §6.2
- [Control 2.16 — RAG Source Integrity Validation](../../../controls/pillar-2-management/2.16-rag-source-integrity-validation.md) — Knowledge-source integrity feeding §2.2 and §9.2
- [Control 2.25 — Agent 365 Admin Center Governance Console](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md) — Publication / activation approval surface
- [Control 2.26 — Entra Agent ID Identity Governance](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md) — Identity attribution for §2.5 and §9.2
- [Control 3.4 — Incident Reporting and Root Cause Analysis](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) — Threshold-breach escalation in §3.2
- [Control 3.6 — Orphaned Agent Detection](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) — Post-retirement orphan check in §9.3

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
