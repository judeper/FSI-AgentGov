# Portal Walkthrough — Control 2.6: Model Risk Management (OCC Bulletin 2026-13 / Fed SR 26-2 — formerly OCC 2011-12 / Fed SR 11-7)

!!! danger "READ FIRST — What This Playbook Configures, and What It Does Not"
    This playbook walks a US FSI Microsoft 365 administrator through the **portal configuration of the Microsoft surfaces that produce model-risk-management evidence** for AI agents — Microsoft Purview Data Security Posture Management (DSPM) for AI, the Agent 365 Admin Center, the Agent Card SharePoint inventory, Microsoft Copilot Studio Analytics, Azure AI Foundry monitoring and evaluators, and Microsoft Entra Agent ID. It is the operational companion to [Control 2.6 — Model Risk Management](../../../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md).

    **These surfaces support compliance with OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12) and Federal Reserve SR 26-2 (formerly SR 11-7). They do not replace, and must not be presented in the firm's MRM policy, Written Supervisory Procedures (WSPs), or examiner submissions as a substitute for:**

    | What the firm must do (people, not platforms) | Where it lives |
    |---|---|
    | **Model Risk Management Committee** — formal model definition, tiering, approval, retirement decisions | Firm's MRM charter and minutes |
    | **Independent model validation function** — SR 26-2 (formerly SR 11-7) *independence* test (organizationally and functionally separate from model owner / developer) | Firm's second-line MRM staff (internal is sufficient; third-party is one way, not the only way, to demonstrate independence) |
    | **Effective challenge** — critical, objective review by qualified personnel not involved in model development | MRM Committee or independent reviewer working papers |
    | **Three-lines-of-defense governance** — first line (model owner/developer), second line (MRM/validation/compliance), third line (Internal Audit) | Firm's risk taxonomy and reporting lines |
    | **Registered-principal supervisory review** under FINRA Rule 3110 for any AI-agent business activity | WSPs and supervisory log (see Control 2.12) |
    | **Books-and-records retention** of validation memos and model artifacts under SEC 17a-4 / FINRA 4511 | Purview retention or 17a-4(f) vendor — see §5 and Controls 1.7, 1.9 |

    Microsoft surfaces produce telemetry, inventory, and evaluation runs. **Lines-of-defense judgments are made by people.**

!!! warning "Hedged-Language Reminder"
    Configuring the surfaces in this walkthrough **supports compliance with** OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12), Federal Reserve SR 26-2 (formerly SR 11-7), FDIC FIL-15-2026, FFIEC IT Handbook (Management; Information Security), FINRA Rule 3110 (Supervision), FINRA Rule 4511 (Books and Records), SEC Rules 17a-3 / 17a-4, SOX §§ 302 / 404, GLBA 501(b), and NYDFS 23 NYCRR 500. It does not by itself guarantee any regulatory outcome. **FINRA RN 25-07 (workplace modernization RFC) is cited only as contextual material; it is not binding AI guidance.** Implementation requires the firm's existing MRM program, validated change control, and independent testing by the firm's compliance and audit functions. Organizations should verify all configurations against their own examination workpapers and legal counsel before treating these procedures as adequate evidence.


---

## Document Map

| § | Section | SR 26-2 (formerly SR 11-7) pillar | Verification Criterion |
|---|---|---|---|
| 0 | [Pre-flight Prerequisites](#0-pre-flight-prerequisites) | All | VC-1, VC-2 |
| 1 | [Conceptual Soundness Evidence Surfaces](#1-conceptual-soundness-evidence-surfaces) | Conceptual soundness | VC-3, VC-4 |
| 2 | [Ongoing Monitoring Evidence Surfaces](#2-ongoing-monitoring-evidence-surfaces) | Ongoing monitoring | VC-5, VC-6 |
| 3 | [Outcomes Analysis Evidence Surfaces](#3-outcomes-analysis-evidence-surfaces) | Outcomes analysis | VC-7 |
| 4 | [Vendor Model Governance (SR 26-2, formerly SR 11-7)](#4-vendor-model-governance-sr-26-2) | Vendor models | VC-8 |
| 5 | [Validation Evidence Retention Path](#5-validation-evidence-retention-path) | Books and records | VC-9 |
| 6 | [Verification Checklist](#6-verification-checklist) | All | VC-1 → VC-10 |
| 7 | [Common Pitfalls](#7-common-pitfalls) | All | Operational |
| 8 | [Related Playbooks](#8-related-playbooks) | — | Routing |

---

## 0. Pre-flight Prerequisites

Skipping a pre-flight gate is itself an auditable finding. Log every gate result on the control-session worksheet and retain under [§5](#5-validation-evidence-retention-path).

### 0.1 MRM Committee charter and policy prerequisite (NOT a tooling step)

Before configuring any portal:

1. Confirm the firm's **Model Risk Management Committee charter** exists, names a Model Risk Manager, and defines model-tiering criteria (Tier 1 / Tier 2 / Tier 3) and validation cadence.
2. Confirm the firm's **MRM policy** explicitly addresses AI agents — that is, it states whether and when an AI agent meets the firm's definition of a "model" under OCC Bulletin 2026-13 / SR 26-2 (formerly OCC 2011-12 / SR 11-7), and assigns first-line, second-line, and third-line responsibilities.
3. Confirm the **WSPs** (broker-dealers) or equivalent supervisory procedures (banks, IAs, NYDFS-covered firms) name the registered principal or supervisor responsible for AI-agent supervision under **FINRA Rule 3110**. This designation must exist in writing **before** any in-scope agent is published.
4. Confirm the **independent validation function** under SR 26-2 (formerly SR 11-7) is identified by name and reporting line. Internal second-line MRM staff who are organizationally and functionally separate from the model owner / developer satisfy the *independence* test. Third-party engagement is one way to demonstrate independence; it is not required and is not equivalent.

If any of these are missing, **stop**. The Microsoft surfaces below have nothing to evidence until the firm's MRM governance exists.

### 0.2 Required licenses and SKUs

| Capability | License / SKU |
|---|---|
| Microsoft Purview Data Security Posture Management for AI | Verify feature-specific entitlements against the [Purview service description](https://learn.microsoft.com/en-us/office365/servicedescriptions/microsoft-365-service-descriptions/microsoft-365-tenantlevel-services-licensing-guidance/microsoft-purview-service-description); Copilot Studio non-Microsoft-channel interaction protection requires Purview pay-as-you-go billing |
| Microsoft Foundry evaluation and monitoring | Azure subscription, supported project/evaluation workflow, applicable model quota and consumption billing; an AI Hub project is not a universal prerequisite |
| Copilot Studio Analytics | Copilot Studio prepaid Copilot Credit pack subscription, Copilot Credits prepurchase plan, or PAYG billing policy |
| Microsoft 365 Copilot grounding for in-scope agents | Microsoft 365 Copilot per-user license |
| Microsoft Agent 365 | Per-user Agent 365 licensing; at least one qualifying user license enables Agent 365. Verify feature-level prerequisites in the [Agent 365 overview](https://learn.microsoft.com/en-us/microsoft-agent-365/overview), not a blanket Copilot-license dependency |
| Microsoft Entra Agent ID | Base Agent ID is available to all Entra customers; extending Entra security features to agents requires Agent 365. Verify the [identity platform prerequisites](https://learn.microsoft.com/en-us/entra/agent-id/what-is-agent-id-platform) for the capability used |
| Microsoft Purview Audit (long retention for telemetry) | M365 E5 Compliance or Audit Premium add-on |
| 17a-4(f) WORM retention for validation evidence | Purview retention with locked policy **or** approved 17a-4(f) vendor (Smarsh, Global Relay, Proofpoint, Mimecast) |

### 0.3 Required canonical roles

Activate every role through **Entra Privileged Identity Management (PIM)** with a justification ticket and time-bound session.

| Canonical role (per [role catalog](../../../reference/role-catalog.md)) | Surfaces required for | Session recommendation |
|---|---|---|
| **AI Administrator** | Agent 365 Admin Center governance templates and approval workflows | 4 h, ticket justification |
| **Entra Global Admin** | Initial Agent 365 enrollment; broad consent scenarios only | Time-boxed; PIM-only |
| **Purview Compliance Admin** | DSPM for AI (classic) configuration; additional solution permissions may be required | 4 h |
| **Purview Data Security AI Viewer** | Read-only DSPM for AI reports/activity evidence for the MRM Committee | 8 h |
| **Purview Compliance Admin** | Retention labels, policies, and 17a-4(f)-aligned holds | 4 h |
| **Purview Records Manager** | Records retention configuration for validation memos | 4 h |
| **Power Platform Admin** | Power Platform inventory and environment-level settings; per-agent Monitor access is checked separately | 4 h |
| **Environment Admin** | Per-environment Copilot Studio agent settings | 4 h |
| **Entra Agent ID Admin** | Agent identity registration and lifecycle for in-scope agents | 4 h |
| **SharePoint Site Owner** | Agent Card inventory list (model-inventory SharePoint site) | 8 h |
| **Model Risk Manager** (governance role) | Sign-off on tiering decisions, validation memos, retirement | n/a — governance, not a directory role |
| **AI Governance Lead** (governance role) | Cross-pillar coordination and examiner packet sign-off | n/a |


### 0.4 FINRA Rule 3110 supervisory designation prerequisite

Per Rule 3110, AI-agent business activity at a broker-dealer requires a **registered principal** with appropriate qualifications designated in writing as the supervisor. Before publishing any in-scope agent in Zone 2 or Zone 3:

1. Confirm the WSPs name the registered principal responsible for the agent's business line.
2. Confirm the principal's CRD record reflects the supervisory designation.
3. Capture written acknowledgment that the principal has reviewed the agent's Agent Card and validation memo.
4. File the acknowledgment in the firm's WSP supervisory evidence repository (see Control 2.12).

This designation is a **regulatory prerequisite**, not a Microsoft tooling step. Copilot Studio Analytics and DSPM for AI dashboards are evidence the principal can use; they do not constitute the supervisory review.

---


## 1. Conceptual Soundness Evidence Surfaces

SR 26-2 (formerly SR 11-7) conceptual soundness asks whether the model is appropriately designed for its intended use, with reasonable assumptions and clearly documented limitations. The surfaces below produce **inventory and design evidence** the MRM Committee uses to evaluate conceptual soundness. They do not perform the evaluation.

### 1.1 Microsoft Purview DSPM for AI inventory

**Portal path:** [Microsoft Purview portal](https://purview.microsoft.com) → **Solutions → DSPM for AI (classic)**; the current **Data Security Posture Management** experience also exposes AI activity in activity explorer. Record which experience was used.

1. Sign in with **Purview Compliance Admin** or the least-privileged permissions for the action in [Microsoft's permissions matrix](https://learn.microsoft.com/en-us/purview/ai-microsoft-purview-permissions). Viewing prompt/response content requires additional content-viewer permission.
2. In **DSPM for AI (classic) → Overview**, verify auditing and supported app-specific onboarding. Do not assume one generic connector screen onboards every AI app.
3. Use **Reports → Copilot experiences & agents → View details** and activity-explorer filters actually available for the source. Retain the report/activity export, filter scope and coverage limitations; this is observed activity, not a complete agent inventory. Reconcile against the Agent Card list, the Agent 365 registry and Power Platform inventory per [Verification §1.2](./verification-testing.md#12-population-of-in-scope-agents).
4. Configure **DSPM for AI policies** that detect prompts and responses containing sensitive information types relevant to the firm (for example, account numbers, MNPI, customer PII). These policies do not validate the model — they generate signals the MRM Committee reviews when assessing whether the model is being used as designed.
5. Arrange a recurring monthly evidence collection through the firm's approved export process; do not assume a native scheduled-inventory-export feature. Capture collection ownership and delivery evidence.

*Screenshot anchor: capture the actual Overview/Reports experience, activity filters and coverage limitations. Use the [Copilot Studio-specific Purview procedure](https://learn.microsoft.com/en-us/purview/ai-copilot-studio); inactive or unsupported agents may have no activity.*

!!! note "DSPM for AI is inventory and signal — not validation"
    The DSPM for AI dashboard tells the MRM Committee **what** AI activity is occurring across the tenant. It does not assess whether a model is conceptually sound. Conceptual soundness is the MRM Committee's judgment based on the agent's design, knowledge sources, and intended use.

### 1.2 Agent 365 Admin Center publication-approval workflow with governance template

**Portal path:** [Microsoft 365 admin center](https://admin.microsoft.com) → **Agents → All agents → Requests**; policy templates are under **Agents → Settings → Templates**.

1. Sign in as **AI Administrator**. Confirm access to the relevant agent/request type and its prerequisites.
2. Review available policy templates under **Agents → Settings → Templates**. These bundle supported security policies; they do not supply a built-in MRM approval chain, model-name allowlist, Agent Card schema or per-document retention label. Maintain those requirements in the firm's approval register/workflow:
    - Agent Card metadata (model tier, knowledge sources, last validation date, next validation date)
    - Approver chain (Model Risk Manager + registered principal under FINRA Rule 3110 for broker-dealers)
    - Evidence-retention reference (links to [§5](#5-validation-evidence-retention-path))
    - Zone-appropriate approved-model register and separate supported provider/environment controls
3. Open **Requests**, inspect the request state and confirm the queue rhythm (daily for Zone 3, weekly for Zone 2) in the firm's runbook.
4. For each pending publication, the AI Administrator validates that the request package includes:
    - A completed Agent Card (see §1.3)
    - The MRM Committee's tiering decision (Tier 1 / 2 / 3) and validation memo reference
    - The registered-principal supervisory acknowledgment (broker-dealers, per §0.4)
5. For a supported publish request, select **Publish to store**, review audience, available policy template and permissions, and retain the actual decision and available audit evidence. **This is evidence of the publication decision, not evidence of validation.** The validation memo itself lives in the retention store described in §5. Other distribution channels require their own access/deployment checks.

Sources: [Manage agent requests](https://learn.microsoft.com/en-us/microsoft-agent-365/admin/agent-requests), [Policy templates](https://learn.microsoft.com/en-us/microsoft-agent-365/admin/policy-template), [Agent settings](https://learn.microsoft.com/en-us/microsoft-agent-365/admin/agent-settings). Template support varies by agent/scenario; Microsoft's template page retains preview/custom-policy limitations, while settings documents a one-time bulk apply action for eligible agent identities. Do not assume an environment-bound, continuously scheduled MRM gate.

Cross-link: [Control 2.25 — Agent 365 Admin Center Governance Console](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md) for full publish/activate workflow detail.

### 1.3 Agent Card SharePoint inventory

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
    | Model version | Single line | Capture exposed version identifiers; record when a precise model snapshot is not exposed |
    | Owner (first line) | Person | Agent Owner / business owner |
    | Tier | Choice | Tier 1 / Tier 2 / Tier 3 per MRM Committee decision |
    | Knowledge sources | Multi-line | SharePoint sites, Dataverse tables, connectors, web search scope |
    | Vendor model? | Yes/No | Triggers §4 vendor-model evidence path |
    | Last validation date | Date | Date of last MRM Committee validation memo |
    | Next validation date | Date | Per tier cadence (Tier 1 annual, Tier 2 annual, Tier 3 biennial — confirm with firm policy) |
    | Validation memo URI | Hyperlink | Pointer to retained memo (see §5) |
    | Registered principal | Person | FINRA Rule 3110 designee (broker-dealers) |
    | Status | Choice | Proposed / Active / Suspended / Retired |

4. Enable **versioning** on the list with a long version retention to preserve inventory history.
5. Publish the appropriate retention labels to the SharePoint location, then verify application to actual items. Site publication does not label every item. Retain protected snapshots of the mutable Agent Card register; apply record protection to finalized evidence per §5.
6. Schedule a monthly snapshot export (CSV) of the list and route to the MRM Committee distribution list. The snapshot is the inventory the firm produces on demand for examiners (VC-1).

!!! tip "Reconcile the Agent Card register with supported sources monthly"
    Compare Power Platform/Agent 365 inventories and supported Purview activity with the firm's register, recording scope and unresolved deltas. Investigate activity without a registered agent; absence from activity reports does not prove absence from production. Any retired agent must be removed from active production surfaces and its Agent Card row marked **Retired** with retirement evidence retained under §5.

---

## 2. Ongoing Monitoring Evidence Surfaces

SR 26-2 (formerly SR 11-7) ongoing monitoring asks whether the model continues to perform as intended after deployment. The surfaces below produce **operational telemetry** the MRM Committee uses to detect drift, degradation, and abnormal behavior.

### 2.1 Copilot Studio Analytics — summary and event-trigger reports

**Portal path:** [Copilot Studio](https://copilotstudio.microsoft.com) → select agent → **Monitor**.

1. Sign in with agent access; an environment administration role alone is not evidence that the reviewer can access this agent's monitoring data.
2. Open **Monitor** and review applicable session counts, outcomes, escalation and satisfaction metrics.
3. Select conversational, event-triggered or hybrid views as applicable, following the [Monitor overview](https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-overview). Test-panel sessions are excluded. A trigger that fails before delivering a payload produces no analytics session; corroborate failures with trigger/flow telemetry.
4. Define **monitoring thresholds** per agent tier in the firm's runbook. Suggested starting thresholds (the MRM Committee owns the final values):

    | Metric | Tier 1 threshold | Tier 2 threshold | Tier 3 threshold |
    |---|---|---|---|
    | Resolution rate | ≥ 90% | ≥ 80% | ≥ 70% |
    | Escalation / fallback rate | ≤ 10% | ≤ 20% | ≤ 30% |
    | Negative feedback rate | ≤ 5% | ≤ 10% | ≤ 15% |
    | Autonomous trigger error rate | ≤ 1% | ≤ 5% | n/a |

5. Name a **threshold-breach owner** (typically the Agent Owner with notification to the Model Risk Manager). Document the named owner on the Agent Card.
6. Arrange recurring evidence exports through the firm's approved process; collect transcripts before the 28-day UI window closes. Sentiment/customer-comment summaries belong to Copilot Studio, not Purview; the customer comments summary is preview.

!!! info "Copilot Studio Analytics Retention Windows (May 2026)"
    Monitor data is available for up to **360 days**; session details and transcript information in Copilot Studio are available for the last **28 days**. Dataverse transcript retention is separate. Ongoing-monitoring evidence required beyond these windows — session transcripts, KPI trend snapshots, threshold-breach records — must be exported to Log Analytics or the retention path described in [§5](#5-validation-evidence-retention-path) before the applicable window closes. Validation memos and MRM Committee minutes are not stored in Copilot Studio Analytics and must be routed to the §5 retention path directly.

!!! warning "Analytics is the evidence — not the validation"
    Copilot Studio Analytics produces operational telemetry. It is one input the MRM Committee uses to perform ongoing monitoring under SR 26-2 (formerly SR 11-7). The committee's review, judgment, and effective challenge are the validation — Analytics dashboards are not.

#### 2.1.1 Granting read-only Analytics access to independent validators (Analytics Viewer sharing role)

The Model Risk Manager, Internal Audit, and the MRM Committee secretariat typically need read-only visibility into the Copilot Studio Analytics page **without** being granted Co-owner or edit rights on the agent. Granting edit rights to the independent validation function violates the SR 26-2 (formerly SR 11-7) effective-challenge principle (a validator must not also hold operational change rights on the model under review).

**Portal path:** [Copilot Studio](https://copilotstudio.microsoft.com) → select agent → **three-dots (...)** menu (top-right of the agent header) → **Share**.

1. Sign in as the **agent owner** (or a Co-owner authorized to share).
2. In the Share dialog, search for the named validator individual.
3. Set the role to **Analytics viewer**. This grants read-only access to the agent's **Monitor** page without edit permissions on the agent.
4. Optionally also assign **Bot Transcript Viewer** to the same individual when conversation transcripts are needed as outcomes-analysis evidence (§3).
5. Save and capture a screenshot of the Share dialog as evidence in the validation work-paper.

!!! warning "Individual users only — security groups are not supported"
    The Analytics Viewer role **can only be assigned to individual users**. Microsoft Entra security groups, distribution lists, and Microsoft 365 groups are **not** valid assignment targets. Maintain a named-individual attestation list (suggested location: the Agent Card, §1.3) and review at the agent's quarterly governance cycle. The list supports examiner traceability of who held read-only Analytics access during any supervisory or validation period and helps meet OCC Bulletin 2026-13 / SR 26-2 (formerly OCC 2011-12 / SR 11-7) documentation expectations for the model-validation function.

Reference: [Microsoft Learn — Share an agent](https://learn.microsoft.com/en-us/microsoft-copilot-studio/admin-share-bots).

### 2.2 Foundry monitoring (when underlying model is on Azure AI Foundry)

Use the [Microsoft Foundry monitoring dashboard procedure](https://learn.microsoft.com/en-us/azure/ai-foundry/observability/how-to/how-to-monitor-agents-dashboard) for the actual project experience rather than assuming a universal **Monitoring** blade.

1. Sign in as **AI Administrator** (or the Azure RBAC role with Foundry project access).
2. Confirm Application Insights linkage and supported instrumentation; configure quality/safety evaluation separately and record sampling. Model hosting alone does not populate every metric.
3. Configure supported **Azure Monitor alerts** for collected metrics/logs. Alerts route to the Agent Owner and the Model Risk Manager.
4. Capture the alert configuration export as evidence.
5. Confirm Foundry evaluator availability in the tenant before relying on the run as evidence.

Reference: [Microsoft Foundry observability](https://learn.microsoft.com/en-us/azure/ai-foundry/concepts/observability). Record preview boundaries and any missing telemetry as gaps, not zero failures.

### 2.3 Application Insights / Azure Monitor telemetry routing to Sentinel

**Portal path:** [Azure portal](https://portal.azure.com) → **Application Insights** → workspace → **Diagnostic settings**, and **Microsoft Sentinel** → workspace → **Data connectors**.

1. For Foundry-hosted models and any custom orchestration code wrapping the agent, send Application Insights telemetry to a Log Analytics workspace.
2. Use the approved Sentinel-enabled Log Analytics workspace and supported ingestion/query design in Control 3.9 to correlate operational anomalies with security signals. There is no generic **Send to Microsoft Sentinel** diagnostic-setting destination.
3. This telemetry path is **operational monitoring**, not 17a-4(f) WORM retention. See [Control 3.9 — Centralized SIEM Integration](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md) for SIEM/Sentinel architecture and [Control 1.7 — Comprehensive Audit Logging](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) for the audit-log retention story.
4. Validation memos and MRM Committee minutes do **not** belong in Application Insights or Sentinel. They live in the retention path described in §5.

---

## 3. Outcomes Analysis Evidence Surfaces

SR 26-2 (formerly SR 11-7) outcomes analysis compares model output to actual outcomes (or to a reference standard) to assess accuracy. The surfaces below produce **evaluator runs** the MRM Committee uses to assess outcome quality.

### 3.1 Foundry built-in evaluators

**Portal path:** [Azure AI Foundry portal](https://ai.azure.com) → project → **Evaluation** → **New evaluation**.

1. Sign in as **AI Administrator**.
2. Create an evaluation run that includes the Foundry built-in evaluators relevant to the agent's risk profile:
    - **Quality evaluators:** groundedness, relevance, coherence, fluency
    - **Safety evaluators:** content safety, protected material, indirect attack
    - **Agent-specific evaluators:** Tool Call Accuracy; Intent Resolution, Task Adherence and Task Completion are **preview** in the current built-in reference
3. Confirm supported evaluator inputs, region, judge-model prerequisites and release state against the [built-in evaluator reference](https://learn.microsoft.com/en-us/azure/ai-foundry/concepts/built-in-evaluators). Record skipped/unsupported results; do not treat them as passes or preview evaluators as GA production dependencies.
4. Schedule periodic re-evaluation runs. Recommended cadence:

    | Tier | Re-evaluation cadence | Trigger-based re-evaluation |
    |---|---|---|
    | Tier 1 | Quarterly minimum | On any model-version change, knowledge-source change, or vendor default-model migration |
    | Tier 2 | Semi-annual | On any material change |
    | Tier 3 | Annual | On any material change |

5. Export each evaluation run and attach it to the validation memo retained under §5.

Reference: [Microsoft Learn — Azure AI Foundry evaluation](https://learn.microsoft.com/en-us/azure/ai-foundry/concepts/evaluation-approach-gen-ai). *(TODO: verify slug.)*

### 3.2 Custom evaluator setup

For agents handling firm-specific risk (e.g., regulation-classification accuracy, MNPI handling), built-in evaluators are insufficient. Configure custom evaluators:

1. Follow the [custom evaluator workflow](https://learn.microsoft.com/en-us/azure/ai-foundry/concepts/evaluation-evaluators/custom-evaluators) supported by the project/API version; do not assume a universal **New custom evaluator** portal command.
2. Implement the approved evaluator against firm-defined ground truth and record its release/support status; custom evaluators are marked preview in the current Foundry reference.
3. Version-control the evaluator definition (Git or Foundry asset versioning) so that the evaluator used for each validation memo is reproducible.
4. The MRM Committee reviews the evaluator definition itself as part of conceptual soundness — an evaluator that is not appropriate to the agent's intended use produces evidence that is not fit for purpose.

### 3.3 Evaluation dataset preparation

1. Curate a dataset that is representative of production prompts for the agent. For Tier 1 agents, this dataset must be reviewed and approved by the MRM Committee.
2. Sanitize the dataset for sensitive information types per firm DLP policy before uploading to Foundry.
3. Version-control the dataset and capture the version reference in each evaluation run.
4. Retain the dataset version, the evaluator version, and the evaluation output together. This bundle is the **outcomes-analysis evidence package** for that validation cycle.

### 3.4 Periodic re-validation cadence

The MRM Committee owns re-validation cadence. The platform schedules evaluation runs; the committee performs the validation. Re-validation is **mandatory** when any of the following occurs:

- Underlying foundation-model version change (including Microsoft default-model migration — see §4)
- Knowledge-source addition, removal, or material change
- Material prompt change (system prompt, grounding instructions)
- Vendor model provider change
- Material change in regulatory expectations or firm policy

Capture each re-validation as a discrete validation memo retained under §5.

---

## 4. Vendor Model Governance (SR 26-2, formerly SR 11-7) {#4-vendor-model-governance-sr-26-2}

SR 26-2 (formerly SR 11-7) applies to vendor and externally developed models with the same rigor as internal models. The validation function must assess the vendor model and document independence.

### 4.1 Capture vendor-model selection and provider evidence

**Portal path (primary model, standard harness):** [Copilot Studio](https://copilotstudio.microsoft.com) → select agent → **Overview → Model**.

1. Sign in as **Environment Admin** for the agent's environment.
2. Open **Overview → Model** and capture the selected primary model, provider/hosting route, release tag, region and any visible version identifier. If an exact snapshot version is not exposed, record that limitation and available lifecycle notices rather than inventing a version. Prompt builder and other AI model settings are separate.
3. Verify the model is on the firm's MRM-approved register (separate from the native Agent 365 policy template — see §1.2).
4. For Anthropic Claude or other third-party providers, capture additional vendor-model evidence:
    - **Provider identity** and contractual relationship (which entity Microsoft routes the model call through, what data-handling commitments apply)
    - **Cross-geography routing** posture — confirm whether prompts and responses are processed only in approved regions
    - **Data-handling and training commitments** as published by Microsoft for that provider
    - **Approval evidence** from the firm's vendor-risk function (see Control 2.7) and the MRM Committee
5. Reference: [Copilot Studio — Select a primary AI model](https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-select-agent-model). Verify availability, GA/preview/experimental tags and retirement/fallback behavior for the specific model in **your** tenant.

**Targeted documentation check (2026-11-06):** External providers need Microsoft 365 provider access plus separate PPAC environment/group controls ([external model settings](https://learn.microsoft.com/en-us/power-platform/admin/allow-llm-generative-responses)). Anthropic is a Microsoft subprocessor for covered routes, but models labeled **Anthropic models with Data Retention** have separate enablement/terms and independent-processor handling ([provider guidance](https://learn.microsoft.com/en-us/copilot/implement/connect-to-ai-subprocessor)). Native selection does not establish uniform contract, residency or certification coverage. No tenant UI, screenshots or API calls were tested; this does not reverify other sections.

### 4.2 Operate the Copilot Studio model lifecycle

Use Microsoft's [model lifecycle guidance](https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/plan-agent-model-lifecycle) as the procedural source for model-change operations. For each production agent:

1. **Discover** new, updated, default, and retiring models through the current model-selection documentation, the model list visible for the specific agent, tenant-targeted notifications, and release guidance.
2. **Inventory** affected agents, environments, owners, business processes, configured model, release classification, regional constraints, and whether the agent follows the default model.
3. **Evaluate** the candidate model against the agent's established regression baseline, including quality, safety, tool selection, latency, and capacity consumption.
4. **Approve** the migration through the firm's existing change, validation, and MRM disposition process.
5. **Deploy** through the organization's ALM process; do not treat an in-place model selection as exempt from change control.
6. **Monitor** production results and add newly observed failure scenarios to the regression suite.
7. **Repeat** as model availability, defaults, retirements, administrator settings, and agent requirements change.

Do not maintain a static model list in this playbook or the firm's policy. Capture the model and version actually configured for each agent at decision time, with the source and verification date.

### 4.3 Detect Microsoft default-model migrations as model changes

A Microsoft-driven default-model migration (for example, a tenant's default Copilot Studio model moving from one foundation model to a successor) is a **model change** for SR 26-2 (formerly SR 11-7) purposes and triggers re-validation.

1. Subscribe the AI Governance Lead and Model Risk Manager to the **Microsoft 365 Message Center** and the **Power Platform release plan** ([https://learn.microsoft.com/en-us/power-platform/release-plan/](https://learn.microsoft.com/en-us/power-platform/release-plan/)).
2. Configure Message Center email digest delivery; Message Center posts are the authoritative tenant-targeted notice for Copilot and Copilot Studio model changes.
3. Establish a runbook so that when a default-model migration is announced:
    - The Agent Card list is updated with the new model and version
    - The MRM Committee schedules re-validation per §3.4
    - A validation memo for the post-migration model is produced and retained under §5
4. Capture the Message Center subscription configuration and the runbook itself as evidence that the firm has a control over vendor-driven model changes.

Cross-link: [Control 2.7 — Vendor and Third-Party Risk Management](../../../controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md) for vendor-risk assessment workflow.

---

## 5. Validation Evidence Retention Path

Validation memos, MRM Committee minutes, ongoing-monitoring reports, outcomes-analysis evaluation runs, retirement decisions, and vendor-model assessments are **books and records** under SEC Rule 17a-4 and FINRA Rule 4511 for broker-dealers, and equivalent records under SOX §802 and OCC / FRB recordkeeping expectations for banks. They must land in 17a-4(f)-compliant WORM storage.

### 5.1 Choose a retention path

| Path | Configuration | Use when |
|---|---|---|
| **Microsoft Purview retention** with locked records-management policy | Publish the approved record label to the SharePoint location and verify application to each finalized evidence item; document any policy-level Preservation Lock separately | Firm has accepted Purview as the 17a-4(f)-compliant store and has documented the locked-policy configuration |
| **Approved 17a-4(f) vendor** — Smarsh, Global Relay, Proofpoint, Mimecast | Configure vendor connector to the SharePoint validation site and to the Agent Card list export pipeline | Firm uses a designated third-party records vendor for all 17a-4(f) records |

### 5.2 Configure Purview retention (if chosen)

1. Sign in as **Purview Records Manager** at [https://purview.microsoft.com](https://purview.microsoft.com).
2. Navigate to **Records Management → File plan → Create a label** and follow the approved record-label design. Regulatory-record declaration must first be enabled and is irreversible once applied; ordinary records can be unlockable. Verify the firm's compliance counsel has accepted the chosen configuration as 17a-4(f)-aligned.
3. Set retention duration to the firm's standard for model artifacts (commonly life-of-model + 7 years).
4. Publish the label to the SharePoint location, then apply it to finalized evidence items and verify item-level label/status. Preserve snapshots of the active Agent Card register separately so ongoing updates do not require editing a regulatory record.
5. Document label settings, item application and any policy-level Preservation Lock separately per Control 1.9 and [Verification §7.2](./verification-testing.md#72-retention-label-binding-test). `Get-ComplianceTag` reads labels; `Get-RetentionCompliancePolicy` reads policies and their `RestrictiveRetention` state. Neither alone proves item application.

Sources: [Records management restrictions](https://learn.microsoft.com/en-us/purview/records-management), [Publish and apply labels](https://learn.microsoft.com/en-us/purview/create-apply-retention-labels), [Preservation Lock](https://learn.microsoft.com/en-us/purview/retention-preservation-lock). Preservation Lock is configured through PowerShell under authorized change control, not a portal deletion-lock toggle.

### 5.3 What does NOT count as 17a-4(f) WORM

- **Microsoft 365 Audit (Premium) retention** is operational telemetry, not WORM. It is appropriate for Control 1.7 audit-log retention but is not the 17a-4(f) store for validation memos.
- **Copilot Studio Analytics dashboards** and **Foundry evaluation-run history** in the platform are operational; export and retain in WORM separately.
- **Application Insights / Sentinel** workspaces are operational; not WORM.

Cross-link: [Control 1.7 — Comprehensive Audit Logging](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) and [Control 1.9 — Records Retention and 17a-4(f) Compliance](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md). *(TODO: verify Control 1.9 filename.)*

---

## 6. Verification Checklist

The MRM Committee, on demand, can produce each of the following. The verification is the production of the artifact, not the existence of a portal screen.

1. **VC-1 — In-scope agent inventory.** A current inventory of all in-scope AI agents with: agent name, owner, tier, model, available model-version identifiers/limitations, knowledge sources, validation status, last validation date, next validation date — produced from the firm's Agent Card list, reconciled monthly with supported inventory and activity sources with explicit coverage deltas.
2. **VC-2 — MRM Committee charter and policy reference.** The firm's MRM Committee charter and the MRM policy section addressing AI agents are current, named, and accessible.
3. **VC-3 — Validation memo demonstrating effective challenge.** For any in-scope agent, a validation memo authored by the independent validation function, referencing the conceptual-soundness analysis, the validator's challenge points, and the resolution. Independence is substantiated by the validator's reporting line (organizationally and functionally separate from the model owner / developer); third-party engagement is one way to demonstrate independence but is not required.
4. **VC-4 — Tiering and approval audit trail.** Firm's MRM approval record, actual Agent 365 publication/activation decision and available audit evidence, plus supported policy-template application where applicable. A native template is not an MRM approval gate.
5. **VC-5 — Ongoing-monitoring report.** A monthly Copilot Studio Analytics export and (for Foundry-hosted models) Foundry monitoring export per in-scope agent, with named threshold-breach owner and any breach-response memos.
6. **VC-6 — Threshold breach response evidence.** For any threshold breach during the reporting period, the response memo and any resulting re-validation.
7. **VC-7 — Outcomes-analysis evaluation run.** For any in-scope agent, a recent evaluator run (Foundry built-in or custom) bundled with the dataset version and evaluator version used.
8. **VC-8 — Vendor-model evidence.** For any agent using a vendor model (including Microsoft default-model migrations), the provider, data-handling, cross-geography, and approval evidence; the Message Center / release-plan subscription configuration; and a runbook activation log if a default-model migration occurred during the period.
9. **VC-9 — 17a-4(f) retention attestation.** Evidence that validation memos, MRM Committee minutes, and evaluation runs are retained in 17a-4(f)-compliant WORM (Purview locked policy or approved vendor).
10. **VC-10 — Model retirement evidence.** For any agent retired during the period, the MRM Committee retirement decision, the Agent Card row marked **Retired**, actual channel-specific administrative action/audit evidence where supported, and confirmation that production access has been removed. Do not assume one Agent 365 action revokes every channel or identity.

---

## 7. Common Pitfalls

| Pitfall | Why it fails | What to do instead |
|---|---|---|
| **Treating Copilot Studio Analytics as the validation.** Pointing examiners at a dashboard and saying "monitoring is in place." | Analytics is operational telemetry — it is **the evidence**, not the validation. The validation is the MRM Committee's review and effective challenge using that evidence. | Produce the validation memo that **references** the Analytics export, authored by the independent validation function. |
| **Calling third-party engagement "independent validation" without substantiating independence.** Engaging an external firm and inferring SR 26-2 (formerly SR 11-7) independence from the engagement alone. | SR 26-2 (formerly SR 11-7) independence is a **functional and organizational** test, not a contractual one. An internal second-line MRM team that is functionally separate from the model owner / developer satisfies independence. A third party that is not appropriately scoped or qualified does not. | Document the validator's reporting line, scope of work, qualifications, and absence of conflicts. Independence is the test; third-party is one way to demonstrate it, not the test itself. |
| **Not capturing vendor-model changes as model changes.** Treating a Microsoft default-model migration as a routine platform update. | A foundation-model change alters the model under SR 26-2 (formerly SR 11-7) and triggers re-validation. Missing this is a recordkeeping and validation gap. | Operate the §4.2 lifecycle and activate the §4.3 migration runbook on every announced default-model migration. |
| **Relying on M365 Audit Premium retention as 17a-4(f) WORM.** Storing validation memos in audit logs and assuming they meet broker-dealer recordkeeping. | M365 Audit Premium is **operational telemetry**, not WORM. It does not meet 17a-4(f) attestation requirements. | Retain validation memos under Purview retention with a locked Regulatory Record label, or in an approved 17a-4(f) vendor (Smarsh, Global Relay, Proofpoint, Mimecast). See [Control 1.9](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md). |
| **Treating DSPM for AI inventory as the model inventory.** Using DSPM for AI as the firm's authoritative Agent Card record. | DSPM for AI captures activity; it does not capture tier, owner-of-record, validation memo URI, or registered-principal designee. | Maintain the Agent Card SharePoint list as the authoritative inventory and reconcile against DSPM for AI monthly. |
| **Confusing FINRA RN 25-07 with binding AI rules.** Citing Notice 25-07 as a regulatory requirement. | Notice 25-07 is RFC / contextual material, not binding AI guidance. | Cite the binding regulations (OCC Bulletin 2026-13 (formerly OCC 2011-12), SR 26-2 (formerly SR 11-7), FINRA 3110, FINRA 4511, SEC 17a-3 / 17a-4, SOX, GLBA, NYDFS 23 NYCRR 500) and reference Notice 25-07 only as contextual background. |

---

## 8. Related Playbooks

| Playbook | Use for |
|---|---|
| [`./powershell-setup.md`](./powershell-setup.md) | Illustrative read-only helpers; unimplemented inventory/Foundry adapters explicitly require manual evidence. No Agent Card provisioning, label application or signed examination assembler is supplied |
| [`./verification-testing.md`](./verification-testing.md) | Test cases that exercise each of VC-1 through VC-10, sample evidence packages, evaluator-run reproducibility checks |
| [`./troubleshooting.md`](./troubleshooting.md) | Source-coverage gaps, Agent 365 entitlement/approval scope, Foundry evaluator support and Message Center subscription gaps |
| [Control 2.6 — Model Risk Management](../../../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md) | Control specification, regulatory mapping, and zone requirements |

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

**Last Verified:** 2026-11-09 — targeted inventory, monitoring, evaluator, template and retention documentation corrections; no tenant UI, screenshots or execution.

*Updated: November 2026 | Version: v1.6.2 | UI Verification Status: Needs Review (documentation-only corrections; tenant UI not tested)*
