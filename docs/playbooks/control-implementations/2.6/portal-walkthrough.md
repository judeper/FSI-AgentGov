# Portal Walkthrough — Control 2.6: Model Risk Management (OCC 2011-12 / Fed SR 11-7)

!!! danger "READ FIRST — What This Playbook Configures, and What It Does Not"
    This playbook walks a US FSI Microsoft 365 administrator through the **portal configuration of the Microsoft surfaces that produce model-risk-management evidence** for AI agents — Microsoft Purview Data Security Posture Management (DSPM) for AI, the Agent 365 Admin Center, the Agent Card SharePoint inventory, Microsoft Copilot Studio Analytics, Azure AI Foundry monitoring and evaluators, and Microsoft Entra Agent ID. It is the operational companion to [Control 2.6 — Model Risk Management](../../../controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md).

    **These surfaces support compliance with OCC Bulletin 2011-12 and Federal Reserve SR 11-7. They do not replace, and must not be presented in the firm's MRM policy, Written Supervisory Procedures (WSPs), or examiner submissions as a substitute for:**

    | What the firm must do (people, not platforms) | Where it lives |
    |---|---|
    | **Model Risk Management Committee** — formal model definition, tiering, approval, retirement decisions | Firm's MRM charter and minutes |
    | **Independent model validation function** — SR 11-7 §V *independence* test (organizationally and functionally separate from model owner / developer) | Firm's second-line MRM staff (internal is sufficient; third-party is one way, not the only way, to demonstrate independence) |
    | **Effective challenge** — critical, objective review by qualified personnel not involved in model development | MRM Committee or independent reviewer working papers |
    | **Three-lines-of-defense governance** — first line (model owner/developer), second line (MRM/validation/compliance), third line (Internal Audit) | Firm's risk taxonomy and reporting lines |
    | **Registered-principal supervisory review** under FINRA Rule 3110 for any AI-agent business activity | WSPs and supervisory log (see Control 2.12) |
    | **Books-and-records retention** of validation memos and model artifacts under SEC 17a-4 / FINRA 4511 | Purview retention or 17a-4(f) vendor — see §5 and Controls 1.7, 1.9 |

    Microsoft surfaces produce telemetry, inventory, and evaluation runs. **Lines-of-defense judgments are made by people.**

!!! warning "Hedged-Language Reminder"
    Configuring the surfaces in this walkthrough **supports compliance with** OCC Bulletin 2011-12, Federal Reserve SR 11-7, FDIC FIL-22-2017, FFIEC IT Handbook (Management; Information Security), FINRA Rule 3110 (Supervision), FINRA Rule 4511 (Books and Records), SEC Rules 17a-3 / 17a-4, SOX §§ 302 / 404, GLBA 501(b), and NYDFS 23 NYCRR 500. It does not by itself guarantee any regulatory outcome. **FINRA Regulatory Notice 25-07 (AI Tools) is cited only as RFC / contextual material; it is not binding AI guidance.** Implementation requires the firm's existing MRM program, validated change control, and independent testing by the firm's compliance and audit functions. Organizations should verify all configurations against their own examination workpapers and legal counsel before treating these procedures as adequate evidence.

!!! warning "Sovereign Cloud Availability — GCC, GCC High, DoD, China"
    Several Microsoft surfaces this playbook depends on have parity gaps in sovereign clouds as of the verification date. **If your tenant authenticates against `login.microsoftonline.us` (GCC, GCC High, DoD) or operates in 21Vianet China**, stop and read [§1 — Sovereign Cloud Variant](#1-sovereign-cloud-variant-and-compensating-controls) before continuing. Re-verify status against the [Microsoft 365 Government roadmap](https://aka.ms/m365gov-roadmap) and the [Power Platform release plan](https://learn.microsoft.com/en-us/power-platform/release-plan/) at least quarterly.

    | Cloud | DSPM for AI | Foundry evaluators | Agent 365 Admin Center | Entra Agent ID lifecycle | Anthropic Claude in Copilot Studio | Compensating control |
    |---|---|---|---|---|---|---|
    | M365 Commercial | GA | GA | GA (May 1, 2026) | GA / preview by surface | Verify per region | n/a |
    | GCC | Verify regional parity | Verify; some judge models commercial-only | Not announced | Verify | Not available | §1 manual SharePoint inventory + 17a-4(f) WORM |
    | GCC High | Verify; lag expected | Limited; commercial-hosted judges may be unavailable | Not announced | Verify | Not available | §1 manual SharePoint inventory + 17a-4(f) WORM |
    | DoD | Verify; lag expected | Limited | Not announced | Verify | Not available | §1 manual SharePoint inventory + 17a-4(f) WORM |
    | China (21Vianet) | Verify operator availability | Verify | Not available | Verify | Not available | §1 manual SharePoint inventory + 17a-4(f) WORM |

    Sovereign endpoint resolution: [`../../_shared/powershell-baseline.md#3-sovereign-cloud-endpoints-gcc-gcc-high-dod`](../../_shared/powershell-baseline.md#3-sovereign-cloud-endpoints-gcc-gcc-high-dod).

---

## Document Map

| § | Section | SR 11-7 pillar | Verification Criterion |
|---|---|---|---|
| 0 | [Pre-flight Prerequisites](#0-pre-flight-prerequisites) | All | VC-1, VC-2 |
| 1 | [Sovereign Cloud Variant and Compensating Controls](#1-sovereign-cloud-variant-and-compensating-controls) | All (substitute path) | VC-1 |
| 2 | [Conceptual Soundness Evidence Surfaces](#2-conceptual-soundness-evidence-surfaces) | Conceptual soundness | VC-3, VC-4 |
| 3 | [Ongoing Monitoring Evidence Surfaces](#3-ongoing-monitoring-evidence-surfaces) | Ongoing monitoring | VC-5, VC-6 |
| 4 | [Outcomes Analysis Evidence Surfaces](#4-outcomes-analysis-evidence-surfaces) | Outcomes analysis | VC-7 |
| 5 | [Vendor Model Governance (SR 11-7 §V)](#5-vendor-model-governance-sr-11-7-v) | Vendor models | VC-8 |
| 6 | [Validation Evidence Retention Path](#6-validation-evidence-retention-path) | Books and records | VC-9 |
| 7 | [Verification Checklist](#7-verification-checklist) | All | VC-1 → VC-10 |
| 8 | [Common Pitfalls](#8-common-pitfalls) | All | Operational |
| 9 | [Related Playbooks](#9-related-playbooks) | — | Routing |

---

## 0. Pre-flight Prerequisites

Skipping a pre-flight gate is itself an auditable finding. Log every gate result on the control-session worksheet and retain under [§6](#6-validation-evidence-retention-path).

### 0.1 MRM Committee charter and policy prerequisite (NOT a tooling step)

Before configuring any portal:

1. Confirm the firm's **Model Risk Management Committee charter** exists, names a Model Risk Manager, and defines model-tiering criteria (Tier 1 / Tier 2 / Tier 3) and validation cadence.
2. Confirm the firm's **MRM policy** explicitly addresses AI agents — that is, it states whether and when an AI agent meets the firm's definition of a "model" under OCC 2011-12 / SR 11-7, and assigns first-line, second-line, and third-line responsibilities.
3. Confirm the **WSPs** (broker-dealers) or equivalent supervisory procedures (banks, IAs, NYDFS-covered firms) name the registered principal or supervisor responsible for AI-agent supervision under **FINRA Rule 3110**. This designation must exist in writing **before** any in-scope agent is published.
4. Confirm the **independent validation function** under SR 11-7 §V is identified by name and reporting line. Internal second-line MRM staff who are organizationally and functionally separate from the model owner / developer satisfy the *independence* test. Third-party engagement is one way to demonstrate independence; it is not required and is not equivalent.

If any of these are missing, **stop**. The Microsoft surfaces below have nothing to evidence until the firm's MRM governance exists.

### 0.2 Required licenses and SKUs

| Capability | License / SKU |
|---|---|
| Microsoft Purview Data Security Posture Management for AI | Microsoft 365 E5 Compliance, Purview Premium, or DSPM for AI standalone — verify in your tenant |
| Azure AI Foundry evaluation harness and monitoring | Azure subscription with Foundry compute (AI Hub project, evaluator quota) |
| Microsoft Copilot Studio Analytics | Copilot Studio per-tenant or per-message capacity license |
| Microsoft 365 Copilot grounding for in-scope agents | Microsoft 365 Copilot per-user license |
| Microsoft Agent 365 Admin Center | Microsoft 365 E7 ("Frontier Suite") or standalone Agent 365 layered on M365 Copilot |
| Microsoft Entra Agent ID | Microsoft Entra ID Governance (P1 + ID Governance add-on, or Entra Suite) |
| Microsoft Purview Audit (long retention for telemetry) | M365 E5 Compliance or Audit Premium add-on |
| 17a-4(f) WORM retention for validation evidence | Purview retention with locked policy **or** approved 17a-4(f) vendor (Smarsh, Global Relay, Proofpoint, Mimecast) |

### 0.3 Required canonical roles

Activate every role through **Entra Privileged Identity Management (PIM)** with a justification ticket and time-bound session.

| Canonical role (per [role catalog](../../../reference/role-catalog.md)) | Surfaces required for | Session recommendation |
|---|---|---|
| **AI Administrator** | Agent 365 Admin Center governance templates and approval workflows | 4 h, ticket justification |
| **Entra Global Admin** | Initial Agent 365 enrollment; broad consent scenarios only | Time-boxed; PIM-only |
| **Purview Data Security AI Admin** | DSPM for AI policies and AI-activity dashboards | 4 h |
| **Purview Data Security AI Viewer** | Read-only DSPM for AI inventory exports for the MRM Committee | 8 h |
| **Purview Compliance Admin** | Retention labels, policies, and 17a-4(f)-aligned holds | 4 h |
| **Purview Records Manager** | Records retention configuration for validation memos | 4 h |
| **Power Platform Admin** | Copilot Studio Analytics, environment-level analytics settings | 4 h |
| **Environment Admin** | Per-environment Copilot Studio agent settings | 4 h |
| **Entra Agent ID Admin** | Agent identity registration and lifecycle for in-scope agents | 4 h |
| **SharePoint Site Owner** | Agent Card inventory list (model-inventory SharePoint site) | 8 h |
| **Model Risk Manager** (governance role) | Sign-off on tiering decisions, validation memos, retirement | n/a — governance, not a directory role |
| **AI Governance Lead** (governance role) | Cross-pillar coordination and examiner packet sign-off | n/a |

### 0.4 Sovereign-cloud verification step

1. In the **Microsoft 365 admin center**, confirm tenant region and cloud at **Settings → Org settings → Organization profile**. Record the Tenant ID GUID and the cloud (Commercial / GCC / GCC High / DoD / China).
2. If the cloud is sovereign, jump to [§1](#1-sovereign-cloud-variant-and-compensating-controls) **before** proceeding. Do not assume parity for any of the surfaces listed in the sovereign-cloud admonition above.
3. Record the verification date and roadmap source consulted (e.g., [`https://aka.ms/m365gov-roadmap`](https://aka.ms/m365gov-roadmap)) on the session worksheet.

### 0.5 FINRA Rule 3110 supervisory designation prerequisite

Per Rule 3110, AI-agent business activity at a broker-dealer requires a **registered principal** with appropriate qualifications designated in writing as the supervisor. Before publishing any in-scope agent in Zone 2 or Zone 3:

1. Confirm the WSPs name the registered principal responsible for the agent's business line.
2. Confirm the principal's CRD record reflects the supervisory designation.
3. Capture written acknowledgment that the principal has reviewed the agent's Agent Card and validation memo.
4. File the acknowledgment in the firm's WSP supervisory evidence repository (see Control 2.12).

This designation is a **regulatory prerequisite**, not a Microsoft tooling step. Copilot Studio Analytics and DSPM for AI dashboards are evidence the principal can use; they do not constitute the supervisory review.

---

## 1. Sovereign Cloud Variant and Compensating Controls

If your tenant is in GCC, GCC High, DoD, or China, treat this section as the primary path until Microsoft announces parity for the surfaces in §§2–4.

1. Maintain a **manual model inventory in a SharePoint list** on a site governed by Purview retention. Required columns mirror the Agent Card schema in [§2.3](#23-agent-card-sharepoint-inventory).
2. The MRM Committee performs validation using the firm's existing MRM policy and methodology. Microsoft Foundry built-in evaluators may not be available; substitute manual or in-house evaluation harnesses.
3. Retain validation memos, MRM Committee minutes, and ongoing-monitoring reports under **17a-4(f)-compliant retention** — either Purview retention with a locked policy or an approved 17a-4(f) vendor (Smarsh, Global Relay, Proofpoint, Mimecast). See [§6](#6-validation-evidence-retention-path).
4. Subscribe the AI Governance Lead to the Microsoft 365 Government roadmap and review quarterly. When parity is announced for a given surface, schedule a controlled migration from the manual path to the platform path.
5. Capture the quarterly roadmap-review attestation in the same evidence library used for validation memos. This attestation is itself examiner evidence that the firm is monitoring sovereign-parity status.

---

## 2. Conceptual Soundness Evidence Surfaces

SR 11-7 conceptual soundness asks whether the model is appropriately designed for its intended use, with reasonable assumptions and clearly documented limitations. The surfaces below produce **inventory and design evidence** the MRM Committee uses to evaluate conceptual soundness. They do not perform the evaluation.

### 2.1 Microsoft Purview DSPM for AI inventory

**Portal path:** [Microsoft Purview portal](https://purview.microsoft.com) → **Data Security Posture Management** → **AI activities** (or **DSPM for AI**, depending on tenant release wave).

1. Sign in as **Purview Data Security AI Admin**.
2. Open **DSPM for AI → Overview** and confirm the dashboard renders AI activity counts for Microsoft 365 Copilot, Copilot Studio, Foundry-registered AI apps, and Entra-registered third-party AI apps. If a connector tile shows "Not configured", open **Settings → AI app connectors** and complete onboarding per [Microsoft Learn — DSPM for AI](https://learn.microsoft.com/en-us/purview/dspm-for-ai). *(TODO: verify the canonical Learn slug for your tenant release wave.)*
3. Open **DSPM for AI → AI activities** and filter to the in-scope environments hosting Zone 2 / Zone 3 agents. Export the activity inventory as CSV; this snapshot is the **starting inventory** the MRM Committee reconciles against the firm's authoritative Agent Card list.
4. Configure **DSPM for AI policies** that detect prompts and responses containing sensitive information types relevant to the firm (for example, account numbers, MNPI, customer PII). These policies do not validate the model — they generate signals the MRM Committee reviews when assessing whether the model is being used as designed.
5. Schedule a recurring monthly export of DSPM for AI inventory and route it to the MRM Committee distribution list. Capture the schedule definition itself as evidence.

*Screenshot anchor: capture the DSPM for AI Overview blade and the AI activities filter showing in-scope environments.*

!!! note "DSPM for AI is inventory and signal — not validation"
    The DSPM for AI dashboard tells the MRM Committee **what** AI activity is occurring across the tenant. It does not assess whether a model is conceptually sound. Conceptual soundness is the MRM Committee's judgment based on the agent's design, knowledge sources, and intended use.

### 2.2 Agent 365 Admin Center publication-approval workflow with governance template

**Portal path:** [Microsoft 365 admin center](https://admin.microsoft.com) → **Agent 365** → **Pending Requests** → **Publishing**, and **Agent 365 → Governance → Templates**.

1. Sign in as **AI Administrator**. Confirm the Agent 365 node is visible (entitlement check — see Control 2.25 if missing).
2. Open **Governance → Templates** and create or review the **MRM-aligned governance template** that will be applied at publish time for in-scope agents. Recommended template fields:
    - Required Agent Card metadata (model tier, knowledge sources, last validation date, next validation date)
    - Required approver chain (Model Risk Manager + registered principal under FINRA Rule 3110 for broker-dealers)
    - Required retention label for the agent's audit trail (links to [§6](#6-validation-evidence-retention-path))
    - Zone-appropriate model allow-list (verify against the underlying-model availability disclosure in Control 2.6 §"Underlying Model Availability in Copilot Studio")
3. Open **Pending Requests → Publishing** and confirm the queue rhythm (daily for Zone 3, weekly for Zone 2) is documented in the firm's runbook.
4. For each pending publication, the AI Administrator validates that the request package includes:
    - A completed Agent Card (see §2.3)
    - The MRM Committee's tiering decision (Tier 1 / 2 / 3) and validation memo reference
    - The registered-principal supervisory acknowledgment (broker-dealers, per §0.5)
5. Approval in Agent 365 records an admin-attributed audit event. **This event is evidence of the publication decision, not evidence of validation.** The validation memo itself lives in the retention store described in §6.

Cross-link: [Control 2.25 — Agent 365 Admin Center Governance Console](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md) for full publish/activate workflow detail.

### 2.3 Agent Card SharePoint inventory

The Agent Card is the firm's **authoritative model inventory record** for each in-scope agent. The SharePoint list is governed by Purview retention so that inventory snapshots are retained alongside validation memos.

**Portal path:** [SharePoint admin center](https://admin.microsoft.com/sharepoint) → create governed site → **Site contents → New → List**.

1. Sign in as **SharePoint Admin** (site provisioning) and **SharePoint Site Owner** (list configuration).
2. Create a site named (e.g.) `MRM-AgentInventory` in a site collection covered by a Purview retention label that matches the firm's model-records retention requirement (commonly life-of-model + 7 years, aligning with SOX §802 and SEC 17a-4 minimums).
3. Create a list named `Agent Card Registry` with the following columns (minimum):

    | Column | Type | Notes |
    |---|---|---|
    | Agent Name | Single line | Matches Copilot Studio / Agent 365 display name |
    | Agent ID | Single line | Entra Agent ID GUID where applicable |
    | Model | Single line | Underlying foundation model (e.g., GPT-5, Claude — verify per tenant) |
    | Model version | Single line | Capture exact version string at publication time |
    | Owner (first line) | Person | Agent Owner / business owner |
    | Tier | Choice | Tier 1 / Tier 2 / Tier 3 per MRM Committee decision |
    | Knowledge sources | Multi-line | SharePoint sites, Dataverse tables, connectors, web search scope |
    | Vendor model? | Yes/No | Triggers §5 vendor-model evidence path |
    | Last validation date | Date | Date of last MRM Committee validation memo |
    | Next validation date | Date | Per tier cadence (Tier 1 annual, Tier 2 annual, Tier 3 biennial — confirm with firm policy) |
    | Validation memo URI | Hyperlink | Pointer to retained memo (see §6) |
    | Registered principal | Person | FINRA Rule 3110 designee (broker-dealers) |
    | Status | Choice | Proposed / Active / Suspended / Retired |

4. Enable **versioning** on the list with a long version retention to preserve inventory history.
5. Apply the Purview retention label to the site at **Microsoft Purview → Information Protection → Retention labels → Apply to SharePoint site**.
6. Schedule a monthly snapshot export (CSV) of the list and route to the MRM Committee distribution list. The snapshot is the inventory the firm produces on demand for examiners (VC-1).

!!! tip "Reconcile Agent Card against DSPM for AI monthly"
    The MRM Committee should reconcile the Agent Card list against the DSPM for AI inventory monthly. Any agent appearing in DSPM for AI but not in the Agent Card list is an unregistered model and must be either tiered and registered or blocked. Conversely, any retired agent must be removed from active production surfaces and its Agent Card row marked **Retired** with retirement evidence retained under §6.

---

## 3. Ongoing Monitoring Evidence Surfaces

SR 11-7 ongoing monitoring asks whether the model continues to perform as intended after deployment. The surfaces below produce **operational telemetry** the MRM Committee uses to detect drift, degradation, and abnormal behavior.

### 3.1 Copilot Studio Analytics — summary and event-trigger reports

**Portal path:** [Copilot Studio](https://copilotstudio.microsoft.com) → select agent → **Analytics**.

1. Sign in as **Power Platform Admin** or **Environment Admin** for the environment hosting the agent.
2. Open **Analytics → Summary** and review session counts, resolution rate, escalation rate, and customer satisfaction (where surveys are configured).
3. Open the per-agent analytics tabs that apply (conversational analytics, autonomous-agent / event-trigger analytics where the agent is configured for event triggers). The exact tab labels evolve — anchor on the page title and consult [Microsoft Learn — Copilot Studio analytics](https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-overview). *(TODO: verify slug for current release wave.)*
4. Define **monitoring thresholds** per agent tier in the firm's runbook. Suggested starting thresholds (the MRM Committee owns the final values):

    | Metric | Tier 1 threshold | Tier 2 threshold | Tier 3 threshold |
    |---|---|---|---|
    | Resolution rate | ≥ 90% | ≥ 80% | ≥ 70% |
    | Escalation / fallback rate | ≤ 10% | ≤ 20% | ≤ 30% |
    | Negative feedback rate | ≤ 5% | ≤ 10% | ≤ 15% |
    | Autonomous trigger error rate | ≤ 1% | ≤ 5% | n/a |

5. Name a **threshold-breach owner** (typically the Agent Owner with notification to the Model Risk Manager). Document the named owner on the Agent Card.
6. Schedule a recurring monthly Analytics export per in-scope agent and route to the MRM Committee.

!!! warning "Analytics is the evidence — not the validation"
    Copilot Studio Analytics produces operational telemetry. It is one input the MRM Committee uses to perform ongoing monitoring under SR 11-7. The committee's review, judgment, and effective challenge are the validation — Analytics dashboards are not.

### 3.2 Foundry monitoring (when underlying model is on Azure AI Foundry)

**Portal path:** [Azure AI Foundry portal](https://ai.azure.com) → select project → **Monitoring**.

1. Sign in as **AI Administrator** (or the Azure RBAC role with Foundry project access).
2. For agents whose underlying model or evaluation harness runs on Foundry, open **Monitoring** and confirm telemetry is flowing for groundedness, relevance, latency, and safety signals (where the model is wrapped in a Foundry deployment).
3. Configure **Foundry alerts** for drift in groundedness or safety scores. Alerts route to the Agent Owner and the Model Risk Manager.
4. Capture the alert configuration export as evidence.
5. Confirm Foundry evaluator parity in your cloud (commercial vs. sovereign) — see the sovereign-cloud admonition above.

Reference: [Microsoft Learn — Azure AI Foundry monitoring](https://learn.microsoft.com/en-us/azure/ai-foundry/). *(TODO: verify exact monitoring article slug.)*

### 3.3 Application Insights / Azure Monitor telemetry routing to Sentinel

**Portal path:** [Azure portal](https://portal.azure.com) → **Application Insights** → workspace → **Diagnostic settings**, and **Microsoft Sentinel** → workspace → **Data connectors**.

1. For Foundry-hosted models and any custom orchestration code wrapping the agent, send Application Insights telemetry to a Log Analytics workspace.
2. From the workspace, configure **Diagnostic settings → Send to Microsoft Sentinel** so that operational anomalies (latency spikes, error bursts, unexpected tool-call patterns) are correlated with security signals.
3. This telemetry path is **operational monitoring**, not 17a-4(f) WORM retention. See [Control 3.9 — Centralized SIEM Integration](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md) for SIEM/Sentinel architecture and [Control 1.7 — Comprehensive Audit Logging](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) for the audit-log retention story.
4. Validation memos and MRM Committee minutes do **not** belong in Application Insights or Sentinel. They live in the retention path described in §6.

---

## 4. Outcomes Analysis Evidence Surfaces

SR 11-7 outcomes analysis compares model output to actual outcomes (or to a reference standard) to assess accuracy. The surfaces below produce **evaluator runs** the MRM Committee uses to assess outcome quality.

### 4.1 Foundry built-in evaluators

**Portal path:** [Azure AI Foundry portal](https://ai.azure.com) → project → **Evaluation** → **New evaluation**.

1. Sign in as **AI Administrator**.
2. Create an evaluation run that includes the Foundry built-in evaluators relevant to the agent's risk profile:
    - **Quality evaluators:** groundedness, relevance, coherence, fluency
    - **Safety evaluators:** content safety, protected material, indirect attack
    - **Agent-specific evaluators:** tool-call accuracy, intent resolution, task adherence / task completion
3. Confirm evaluator availability in your cloud. In sovereign clouds, some evaluators rely on commercial-cloud-hosted judge models and may be unavailable — substitute manual review per §1.
4. Schedule periodic re-evaluation runs. Recommended cadence:

    | Tier | Re-evaluation cadence | Trigger-based re-evaluation |
    |---|---|---|
    | Tier 1 | Quarterly minimum | On any model-version change, knowledge-source change, or vendor default-model migration |
    | Tier 2 | Semi-annual | On any material change |
    | Tier 3 | Annual | On any material change |

5. Export each evaluation run and attach it to the validation memo retained under §6.

Reference: [Microsoft Learn — Azure AI Foundry evaluation](https://learn.microsoft.com/en-us/azure/ai-foundry/concepts/evaluation-approach-gen-ai). *(TODO: verify slug.)*

### 4.2 Custom evaluator setup

For agents handling firm-specific risk (e.g., regulation-classification accuracy, MNPI handling), built-in evaluators are insufficient. Configure custom evaluators:

1. In the Foundry project, open **Evaluation → Evaluators → New custom evaluator**.
2. Implement the evaluator as a prompt-based or code-based evaluator referencing a firm-defined ground-truth dataset.
3. Version-control the evaluator definition (Git or Foundry asset versioning) so that the evaluator used for each validation memo is reproducible.
4. The MRM Committee reviews the evaluator definition itself as part of conceptual soundness — an evaluator that is not appropriate to the agent's intended use produces evidence that is not fit for purpose.

### 4.3 Evaluation dataset preparation

1. Curate a dataset that is representative of production prompts for the agent. For Tier 1 agents, this dataset must be reviewed and approved by the MRM Committee.
2. Sanitize the dataset for sensitive information types per firm DLP policy before uploading to Foundry.
3. Version-control the dataset and capture the version reference in each evaluation run.
4. Retain the dataset version, the evaluator version, and the evaluation output together. This bundle is the **outcomes-analysis evidence package** for that validation cycle.

### 4.4 Periodic re-validation cadence

The MRM Committee owns re-validation cadence. The platform schedules evaluation runs; the committee performs the validation. Re-validation is **mandatory** when any of the following occurs:

- Underlying foundation-model version change (including Microsoft default-model migration — see §5)
- Knowledge-source addition, removal, or material change
- Material prompt change (system prompt, grounding instructions)
- Vendor model provider change
- Material change in regulatory expectations or firm policy

Capture each re-validation as a discrete validation memo retained under §6.

---

## 5. Vendor Model Governance (SR 11-7 §V)

SR 11-7 §V applies to vendor and externally developed models with the same rigor as internal models. The validation function must assess the vendor model and document independence.

### 5.1 Capture vendor-model selection and provider evidence

**Portal path:** [Copilot Studio](https://copilotstudio.microsoft.com) → select agent → **Settings** → **Generative AI** → **Model**.

1. Sign in as **Environment Admin** for the agent's environment.
2. Open **Settings → Generative AI** and capture the **model provider** (Microsoft / OpenAI via Microsoft / Anthropic / other), the **model name**, and the **model version string** as displayed in the tenant.
3. Verify the model is on the firm's MRM-approved allow-list (defined in the Agent 365 governance template — see §2.2).
4. For Anthropic Claude or other third-party providers, capture additional vendor-model evidence:
    - **Provider identity** and contractual relationship (which entity Microsoft routes the model call through, what data-handling commitments apply)
    - **Cross-geography routing** posture — confirm whether prompts and responses are processed only in approved regions
    - **Data-handling and training commitments** as published by Microsoft for that provider
    - **Approval evidence** from the firm's vendor-risk function (see Control 2.7) and the MRM Committee
5. Reference: [Copilot Studio — Choose a generative AI model](https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-generative-actions). Verify availability and GA status of any third-party model in **your** tenant; sovereign-cloud parity is independently gated.

### 5.2 Detect Microsoft default-model migrations as model changes

A Microsoft-driven default-model migration (for example, a tenant's default Copilot Studio model moving from one foundation model to a successor) is a **model change** for SR 11-7 purposes and triggers re-validation.

1. Subscribe the AI Governance Lead and Model Risk Manager to the **Microsoft 365 Message Center** and the **Power Platform release plan** ([https://learn.microsoft.com/en-us/power-platform/release-plan/](https://learn.microsoft.com/en-us/power-platform/release-plan/)).
2. Configure Message Center email digest delivery; Message Center posts are the authoritative tenant-targeted notice for Copilot and Copilot Studio model changes.
3. Establish a runbook so that when a default-model migration is announced:
    - The Agent Card list is updated with the new model and version
    - The MRM Committee schedules re-validation per §4.4
    - A validation memo for the post-migration model is produced and retained under §6
4. Capture the Message Center subscription configuration and the runbook itself as evidence that the firm has a control over vendor-driven model changes.

Cross-link: [Control 2.7 — Vendor and Third-Party Risk Management](../../../controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md) for vendor-risk assessment workflow.

---

## 6. Validation Evidence Retention Path

Validation memos, MRM Committee minutes, ongoing-monitoring reports, outcomes-analysis evaluation runs, retirement decisions, and vendor-model assessments are **books and records** under SEC Rule 17a-4 and FINRA Rule 4511 for broker-dealers, and equivalent records under SOX §802 and OCC / FRB recordkeeping expectations for banks. They must land in 17a-4(f)-compliant WORM storage.

### 6.1 Choose a retention path

| Path | Configuration | Use when |
|---|---|---|
| **Microsoft Purview retention** with locked records-management policy | Purview portal → **Records Management → Retention labels** → label marked as **Regulatory Record**; apply to the SharePoint site holding validation memos | Firm has accepted Purview as the 17a-4(f)-compliant store and has documented the locked-policy configuration |
| **Approved 17a-4(f) vendor** — Smarsh, Global Relay, Proofpoint, Mimecast | Configure vendor connector to the SharePoint validation site and to the Agent Card list export pipeline | Firm uses a designated third-party records vendor for all 17a-4(f) records |

### 6.2 Configure Purview retention (if chosen)

1. Sign in as **Purview Records Manager** at [https://purview.microsoft.com](https://purview.microsoft.com).
2. Navigate to **Records Management → File plan → Create label**. Mark the label as a **Regulatory Record** (this is the configuration that produces immutable, locked retention; verify the firm's compliance counsel has accepted this configuration as 17a-4(f)-aligned).
3. Set retention duration to the firm's standard for model artifacts (commonly life-of-model + 7 years).
4. Apply the label to the SharePoint site holding the Agent Card list, validation memos, MRM Committee minutes, and evaluation-run exports.
5. Document the locked-policy attestation per Control 1.9.

### 6.3 What does NOT count as 17a-4(f) WORM

- **Microsoft 365 Audit (Premium) retention** is operational telemetry, not WORM. It is appropriate for Control 1.7 audit-log retention but is not the 17a-4(f) store for validation memos.
- **Copilot Studio Analytics dashboards** and **Foundry evaluation-run history** in the platform are operational; export and retain in WORM separately.
- **Application Insights / Sentinel** workspaces are operational; not WORM.

Cross-link: [Control 1.7 — Comprehensive Audit Logging](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) and [Control 1.9 — Records Retention and 17a-4(f) Compliance](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md). *(TODO: verify Control 1.9 filename.)*

---

## 7. Verification Checklist

The MRM Committee, on demand, can produce each of the following. The verification is the production of the artifact, not the existence of a portal screen.

1. **VC-1 — In-scope agent inventory.** A current inventory of all in-scope AI agents with: agent name, owner, tier, model, model version, knowledge sources, validation status, last validation date, next validation date — produced from the Agent Card SharePoint list, reconciled monthly against DSPM for AI inventory.
2. **VC-2 — MRM Committee charter and policy reference.** The firm's MRM Committee charter and the MRM policy section addressing AI agents are current, named, and accessible.
3. **VC-3 — Validation memo demonstrating effective challenge.** For any in-scope agent, a validation memo authored by the independent validation function, referencing the conceptual-soundness analysis, the validator's challenge points, and the resolution. Independence is substantiated by the validator's reporting line (organizationally and functionally separate from the model owner / developer); third-party engagement is one way to demonstrate independence but is not required.
4. **VC-4 — Tiering and approval audit trail.** Agent 365 Admin Center publication-approval audit events and the linked governance template that was applied at publish time.
5. **VC-5 — Ongoing-monitoring report.** A monthly Copilot Studio Analytics export and (for Foundry-hosted models) Foundry monitoring export per in-scope agent, with named threshold-breach owner and any breach-response memos.
6. **VC-6 — Threshold breach response evidence.** For any threshold breach during the reporting period, the response memo and any resulting re-validation.
7. **VC-7 — Outcomes-analysis evaluation run.** For any in-scope agent, a recent evaluator run (Foundry built-in or custom) bundled with the dataset version and evaluator version used.
8. **VC-8 — Vendor-model evidence.** For any agent using a vendor model (including Microsoft default-model migrations), the provider, data-handling, cross-geography, and approval evidence; the Message Center / release-plan subscription configuration; and a runbook activation log if a default-model migration occurred during the period.
9. **VC-9 — 17a-4(f) retention attestation.** Evidence that validation memos, MRM Committee minutes, and evaluation runs are retained in 17a-4(f)-compliant WORM (Purview locked policy or approved vendor).
10. **VC-10 — Model retirement evidence.** For any agent retired during the period, the MRM Committee retirement decision, the Agent Card row marked **Retired**, the Agent 365 lifecycle action audit event, and confirmation that production access has been removed.

---

## 8. Common Pitfalls

| Pitfall | Why it fails | What to do instead |
|---|---|---|
| **Treating Copilot Studio Analytics as the validation.** Pointing examiners at a dashboard and saying "monitoring is in place." | Analytics is operational telemetry — it is **the evidence**, not the validation. The validation is the MRM Committee's review and effective challenge using that evidence. | Produce the validation memo that **references** the Analytics export, authored by the independent validation function. |
| **Calling third-party engagement "independent validation" without substantiating independence.** Engaging an external firm and inferring SR 11-7 §V independence from the engagement alone. | SR 11-7 independence is a **functional and organizational** test, not a contractual one. An internal second-line MRM team that is functionally separate from the model owner / developer satisfies independence. A third party that is not appropriately scoped or qualified does not. | Document the validator's reporting line, scope of work, qualifications, and absence of conflicts. Independence is the test; third-party is one way to demonstrate it, not the test itself. |
| **Not capturing vendor-model changes as model changes.** Treating a Microsoft default-model migration as a routine platform update. | A foundation-model change alters the model under SR 11-7 and triggers re-validation. Missing this is a recordkeeping and validation gap. | Subscribe to Microsoft 365 Message Center and the Power Platform release plan; activate the §5.2 runbook on every announced default-model migration. |
| **Relying on M365 Audit Premium retention as 17a-4(f) WORM.** Storing validation memos in audit logs and assuming they meet broker-dealer recordkeeping. | M365 Audit Premium is **operational telemetry**, not WORM. It does not meet 17a-4(f) attestation requirements. | Retain validation memos under Purview retention with a locked Regulatory Record label, or in an approved 17a-4(f) vendor (Smarsh, Global Relay, Proofpoint, Mimecast). See [Control 1.9](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md). |
| **Treating DSPM for AI inventory as the model inventory.** Using DSPM for AI as the firm's authoritative Agent Card record. | DSPM for AI captures activity; it does not capture tier, owner-of-record, validation memo URI, or registered-principal designee. | Maintain the Agent Card SharePoint list as the authoritative inventory and reconcile against DSPM for AI monthly. |
| **Assuming sovereign-cloud parity.** Configuring the platform path in GCC, GCC High, or DoD without verifying availability. | Several surfaces in this playbook have not been announced for sovereign clouds. Configurations that fail silently produce no evidence. | Run §0.4 verification, jump to §1 if sovereign, and re-verify quarterly against the Microsoft 365 Government roadmap. |
| **Confusing FINRA Notice 25-07 with binding AI rules.** Citing Notice 25-07 as a regulatory requirement. | Notice 25-07 is RFC / contextual material, not binding AI guidance. | Cite the binding regulations (OCC 2011-12, SR 11-7, FINRA 3110, FINRA 4511, SEC 17a-3 / 17a-4, SOX, GLBA, NYDFS 23 NYCRR 500) and reference Notice 25-07 only as contextual background. |

---

## 9. Related Playbooks

| Playbook | Use for |
|---|---|
| [`./powershell-setup.md`](./powershell-setup.md) | Microsoft Graph PowerShell automation for inventory exports, Agent Card list provisioning, retention-label application, Message Center subscription |
| [`./verification-testing.md`](./verification-testing.md) | Test cases that exercise each of VC-1 through VC-10, sample evidence packages, evaluator-run reproducibility checks |
| [`./troubleshooting.md`](./troubleshooting.md) | DSPM for AI connector failures, Agent 365 entitlement gaps, Foundry evaluator quota errors, Message Center subscription gaps, sovereign-cloud parity diagnostics |
| [Control 2.6 — Model Risk Management](../../../controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md) | Control specification, regulatory mapping, and zone requirements |

### Cross-control references

- [Control 1.6 — Microsoft Purview DSPM for AI](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md) — DSPM for AI authoring control
- [Control 1.7 — Comprehensive Audit Logging](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) — operational audit log retention
- [Control 1.9 — Records Retention and 17a-4(f) Compliance](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md) — books-and-records retention for validation evidence *(TODO: verify filename)*
- [Control 2.7 — Vendor and Third-Party Risk Management](../../../controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md) — vendor-model risk assessment
- [Control 2.12 — FINRA Rule 3110 Supervisory Procedures](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) — registered-principal supervisory designation *(TODO: verify filename)*
- [Control 2.25 — Agent 365 Admin Center Governance Console](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md) — publish/activate workflow and governance templates
- [Control 2.26 — Entra Agent ID Identity Governance](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md) — agent identity attribution
- [Control 3.9 — Centralized SIEM Integration](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md) — Sentinel routing for operational telemetry

---

*Updated: April 2026 | Version: v1.4 | UI Verification Status: Current*
