# Control 2.20 — Portal Walkthrough: Adversarial Testing and Red Team Framework

**Control:** [2.20 — Adversarial Testing and Red Team Framework](../../../controls/pillar-2-management/2.20-adversarial-testing-and-red-team-framework.md)<br>
**Pillar:** Management<br>
**Last UI Verified:** April 2026<br>
**Last Verified:** 2026-11-06 (Microsoft Learn documentation review; not tenant UI verification)<br>
**Estimated time:** 6–10 hours initial setup; 2–8 hours per recurring test cycle (varies by zone and agent surface)<br>
**Governance Levels:** Baseline / Recommended / Regulated

---

!!! warning "Verification boundary and implementation prerequisites"
    Microsoft product guidance was checked against the live sources in [Microsoft documentation reviewed](#microsoft-documentation-reviewed) on 2026-11-06. No tenant actions, screenshots, probes, or license assignments were verified. The historical UI date above is not renewed.

    Copilot Studio solution transport requires a Dataverse environment and solution-management privileges (at least the **System Customizer** Dataverse security role). Assign the test identities the licenses required for the experience under test; a test organizational unit is not a licensing exemption. Managed Environments require qualifying standalone licenses or pay-as-you-go coverage for active usage. PIM requires Microsoft Entra ID P2 or Microsoft Entra ID Governance licensing. Foundry evaluations require an Azure subscription, a supported project/region, the **Foundry User** role, and applicable quota/billing.

    Microsoft 365 Copilot does not run inside a Power Platform sandbox. Use a separately isolated test tenant and synthetic Microsoft 365 content for that surface. The **Microsoft 365 Copilot Chat API is preview**, requires a Microsoft 365 Copilot add-on license and delegated Graph permissions, and does not support application permissions or action/content-generation skills. Interactive testing remains necessary for experiences the API does not cover.

!!! danger "READ FIRST — what this walkthrough is and is NOT"
    This walkthrough configures the **proactive adversarial testing program** (red-team charter, attack library, isolated test environment, golden dataset, pre-deployment gate, evidence pack) for Microsoft 365 Copilot, Microsoft Copilot Studio agents, and Microsoft Foundry (formerly Azure AI Foundry)-backed FSI agents.

    It is **NOT** a substitute for the following sibling controls. Each is a separate configuration surface with its own playbook:

    | If you need… | Use Control | Why this is not 2.20 |
    |---|---|---|
    | **Detection** of prompt injection / jailbreak / XPIA in production | **1.21** — Adversarial Input Logging | 2.20 is preventive (pre-deployment + scheduled probes); 1.21 is detective (production telemetry) |
    | General agent QA, regression testing, suitability validation | **2.5** — Testing & Validation | 2.5 covers functional QA; 2.20 covers adversarial / safety scenarios |
    | Independent model validation per OCC Bulletin 2026-13 (formerly OCC 2011-12) / Fed SR 26-2 (formerly SR 11-7) | **2.6** — Model Risk Management | 2.6 is the program; 2.20 is one input to 2.6 |
    | Bias and fairness testing | **2.11** — Bias Testing & Fairness | 2.11 covers protected-class fairness; 2.20 covers safety / abuse / exfiltration |
    | Sensitive Information Type tuning so DLP / Comm Compliance fires correctly during red-team probes | **1.13** — SITs and Pattern Recognition | SIT tuning is a prerequisite for measuring exfiltration test outcomes |
    | Content Safety / Prompt Shields configuration on the Azure AI deployment under test | **1.21** §3 (Prompt Shields surface) | 2.20 *measures* whether Prompt Shields blocks the attack; it does not configure Prompt Shields |
    | Evidence retention to WORM under SEC 17a-4(f) | **1.19** — eDiscovery for Agent Interactions | 2.20 generates evidence; 1.19 holds it |

!!! warning "Hedged-language reminder — supports, does not guarantee"
    The procedures below **support compliance with** OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12), Federal Reserve SR 26-2 (formerly SR 11-7), FINRA Rule 3110, FINRA RN 24-09 / Rule 3110 (June 2024), SEC Rule 17a-4(b)(4), GLBA 501(b), and the NIST AI RMF Generative AI Profile (NIST AI 600-1). They **do not by themselves guarantee** regulatory compliance. The Compliance Officer, Model Risk Manager, and CISO must independently validate that the firm's WSPs reference the documented testing cadence, the actual defense-rate thresholds in use, and the firm's records-retention horizon.

!!! info "What this walkthrough covers — surfaces & owners"
    | # | Surface | Portal | Owner role | Notes |
    |---|---|---|---|---|
    | 1 | Red-team program charter (document) | Internal GRC system | AI Governance Lead | Charter must precede any tenant action |
    | 2 | Isolated test environment | `admin.powerplatform.microsoft.com` | Power Platform Admin | Sandbox; no production data |
    | 3 | Test agent deployment (Copilot Studio) | `copilotstudio.microsoft.com` | Microsoft Copilot Studio Agent Author | Transport approved release; record differences from production snapshot |
    | 4 | Microsoft Foundry deployment under test (if applicable) | `ai.azure.com` | Cloud Security Architect | Read-only guardrail review with appropriate Foundry/Azure RBAC |
    | 5 | Attack library + golden dataset (version-controlled) | Internal repo | Security Architect + Model Risk Manager | Reviewed quarterly |
    | 6 | Pre-deployment gate (CI/CD pipeline) | Azure DevOps / GitHub Actions | Cloud Security Architect | Gate threshold defined per zone |
    | 7 | Evidence pack (test results + SHA-256 manifest) | Storage with WORM / immutability lock | Cloud Security Architect | Reconcile with Control 1.19 hold |
    | 8 | Findings register + remediation tracking | Internal GRC system | AI Governance Lead | SLA enforcement; risk-acceptance signatures |

---

## §0 Coverage boundary and portal vs script matrix

### 0.1 Coverage boundary

In scope:

- Microsoft 365 Copilot, Copilot Studio agents, and Azure OpenAI / Microsoft Foundry-backed agents in any zone, using the surface-specific isolation and test interfaces described above.
- Adversarial test categories: prompt injection (direct + indirect / XPIA), jailbreak, system-prompt extraction, data exfiltration (NPI / MNPI), suitability bypass, encoded evasion (Base64, Unicode confusables, zero-width), tool / plugin abuse, multi-turn manipulation.
- Pre-deployment probes and scheduled cycles (monthly Z3, quarterly Z2, annual Z1).

Out of scope (handled by sibling controls — see READ FIRST):

- Production detection (1.21), eDiscovery hold (1.19), bias testing (2.11), general QA (2.5), connector / DLP authoring (1.4 / 1.5), and incident response workflow (3.4).

### 0.2 Portal vs script matrix

| Step | Portal? | Script? | Notes |
|---|---|---|---|
| Author program charter | Internal GRC / Word | n/a | Document, sign, store in records system |
| Create isolated test environment | ✅ PPAC | ✅ `New-AdminPowerAppEnvironment` | Portal recommended for first-time setup; script for repeatable refresh |
| Transport a Copilot Studio agent into sandbox | ✅ Copilot Studio (Solutions export/import) | Power Platform CLI, where implemented | Use the approved unmanaged source solution; Step 3 is not an exact clone; the sibling PowerShell playbook does not supply a solution-transport pipeline |
| Maintain attack library | Source repo | n/a | Version control (Git) is the system of record |
| Run probes against agent endpoint | Surface-dependent | PyRIT or firm-implemented runner | Foundry offers automated AI red teaming for supported targets; there is no universal runner across all three surfaces, and this repository does not ship `Invoke-AdversarialTests.ps1` |
| Run risk and safety evaluations | ✅ Foundry **Evaluation → Create** | Foundry SDK | Evaluates supported targets or preexisting outputs; evaluator/target/region restrictions and preview features apply |
| Capture evidence pack (SHA-256) | n/a | ✅ Mandatory script step | See `powershell-setup.md` §5 |
| Track findings & remediation | Internal GRC / DevOps work-item system | API | Out of scope for Microsoft portals |

---

## §1 Pre-flight gates

Complete every gate **before** opening any portal. Most defects in red-team programs trace to a missed pre-flight.

### 1.1 Authorization gate

- [ ] Red-team program charter signed by **AI Governance Lead**, **CISO**, and **Compliance Officer**.
- [ ] Rules of Engagement (ROE) document lists in-scope agents, test categories, time windows, and prohibited actions (no destructive payloads, no exfiltration of real customer data, no production-data targeting).
- [ ] Out-of-scope assets explicitly listed (production tenants, customer-facing endpoints, third-party SaaS not owned by the firm).
- [ ] Operator separation-of-duties attestation: red-team operators are **not** the agent's primary developer or owner. Co-signer attestation captured if exception granted.
- [ ] Legal review confirms ROE does not violate Computer Fraud and Abuse Act (CFAA) or vendor terms of service for any in-scope SaaS.

### 1.2 Environment gate

- [ ] Sandbox Power Platform environment exists, labelled `RedTeam-{agent}-{yyyymm}`, type **Sandbox**, region matched to production.
- [ ] DLP and Managed Environment posture in the sandbox matches production at a known snapshot date (record snapshot ID).
- [ ] Sandbox environment **contains no production customer data**. Synthetic data only. Review every imported table, file, knowledge source, connection reference, flow, and tool destination. Purview Data Map scans of supported sources are supplementary classification evidence, not proof that all content is synthetic; scanning samples content.

### 1.3 Identity gate

- [ ] Dedicated test identities exist with the required experience-specific licenses and least-privileged roles; do not reuse production identities.
- [ ] Operator account uses **Privileged Identity Management (PIM)** for elevation; standing access not granted.
- [ ] Audit logging is enabled in the sandbox (Control 1.7) so probe activity is captured and retrievable.

### 1.4 Tooling gate

- [ ] Microsoft PyRIT (Python Risk Identification Tool) installed at a CAB-approved version on the operator workstation or pipeline runner; validate that version's Python requirements and target adapter.
- [ ] Attack library repository checked out at a tagged commit; commit SHA recorded for the run.
- [ ] Golden dataset checked out at a tagged version; version recorded.
- [ ] Evidence storage location confirmed and immutability / retention policy verified (link to Control 1.19 hold).

---

## §2 Step-by-step portal configuration

### Step 1 — Author and sign the red-team program charter

The charter is a **documentary** prerequisite, not a portal action. Capture in the firm's GRC system the following sections:

| Section | Required content |
|---|---|
| Purpose | Why the program exists; mapping to OCC Bulletin 2026-13 (formerly OCC 2011-12) / Fed SR 26-2 (formerly SR 11-7) / FINRA 3110 / RN 24-09 |
| Scope | Which agents, which zones, which Microsoft surfaces |
| Authorization | Signatures: AI Governance Lead, CISO, Compliance Officer, Legal acknowledgment |
| Rules of Engagement | Permitted tactics, prohibited actions, time windows, communication protocol |
| Operator roster + separation-of-duties | Names, roles, exceptions with co-signer attestations |
| Cadence | Z1 annual, Z2 quarterly, Z3 monthly + annual independent third-party |
| Evidence policy | Artefact taxonomy, SHA-256 manifest requirement, WORM destination, retention horizon |
| Remediation SLA | Critical (24 h), High (7 d), Medium (30 d), Low (next release) |
| Reporting | Cadence and audience for executive summary, technical report, board report |

Store the signed charter in records-retention scope (link to Control 1.19 hold to satisfy SEC 17a-4(b)(4) / 18a-6 preservation).

### Step 2 — Create an isolated test environment (PPAC)

1. Open [Power Platform Admin Center](https://admin.powerplatform.microsoft.com/).
2. **Manage → Environments → New**.
3. Configure:
   - **Name:** `RedTeam-{AgentName}-{YYYYMM}` (e.g. `RedTeam-AdvisoryBot-202604`)
   - **Type:** Sandbox
   - **Region:** Same as production
   - **Add a Dataverse data store?:** Yes for Copilot Studio agents and solution import
   - **Security group:** Restrict to red-team operator group
4. After provisioning, verify each configuration separately:
   - **Security → Data and privacy → Data policy**: review all policies applicable to the sandbox and compare their effective scope/connector rules with the production snapshot.
   - **Manage → Environments → {sandbox} → Settings → Audit and logs → Audit settings**: enable Dataverse auditing and the required table/column auditing. Dataverse audit settings do not by themselves enable every Copilot or Microsoft 365 audit stream; verify Control 1.7 separately.
5. Apply the **Managed Environment** posture if production is managed, after confirming qualifying licensing/meter coverage.

!!! note "Do not skip the security-group restriction"
    Set the Microsoft Entra security group at create-time and review Dataverse security roles, agent sharing, and channel authentication separately. A group is not a complete isolation boundary: Power Platform Admin access and application users have documented exceptions. Without a group, eligible licensed users can be provisioned into the environment, but data access still requires security roles.

### Step 3 — Transport the approved agent release into the sandbox

For Copilot Studio agents:

1. Open [Copilot Studio](https://copilotstudio.microsoft.com/).
2. Use the approved **unmanaged source solution** corresponding to the production release. A managed solution installed in production cannot be exported; do not alter production to manufacture an export.
3. Select the side-bar **… → Solutions** to open the solution explorer. Create/select a custom solution, add the agent, and use **Advanced → Add required objects** for its required components. Include flows, environment variables, connection references, and custom connectors.
4. Select the unmanaged solution → **Export solution**. Choose the managed/unmanaged package type appropriate to the approved test workflow. Managed components must allow any sandbox customization needed for tests.
5. Switch to the **sandbox** environment → solution explorer → **Import solution**. Import custom connectors before the connection references/agent solution when required.
6. Review missing or nontransported knowledge sources, topics, IDs, channel details, and other properties; solution import is **not an exact clone**. Reconfigure user authentication. Before publishing or invoking the agent, replace production connections, tool/flow destinations, environment-variable values, and grounding sources with synthetic sandbox equivalents.
7. Publish the imported agent only after that review and restrict its channels/audience to authorized test users. Record remaining differences from the production release in the evidence pack.

For Microsoft Foundry-backed agents:

1. Open [Microsoft Foundry](https://ai.azure.com/) and record whether the tenant uses the new or classic portal experience.
2. Review the production project/deployment read-only. Capture deployment metadata through the documented Azure resource APIs or `Get-AzCognitiveServicesAccountDeployment`, and the referenced RAI policy through `Get-AzCognitiveServicesAccountRaiPolicy` where applicable. There is no assumed **Deployments → Export** portal action.
3. Have the authorized deployment owner recreate the approved configuration in a separate test project/resource using the firm's deployment process. Verify current availability/quota for the chosen model/version/region; a historical model name in §4 is not an availability assertion.
4. Compare model/version, assigned guardrails or content-filter policy, tools, identities, and synthetic grounding sources with the production snapshot. An exported policy alone does not prove that it is assigned or enforced.
5. Confirm Prompt Shields (user prompt attacks + document attacks) state and supported intervention points. Record differences and actual policy/deployment identifiers in the evidence pack.

### Step 4 — Verify content-safety baseline on the agent under test

Open the test project in Microsoft Foundry (if applicable):

1. In the new portal, select **Build** (top right) → **Guardrails** (left navigation). Review the guardrail assigned to the deployment/agent rather than creating or changing one during baseline capture. Classic deployments can expose content filters/RAI policies instead; record which configuration surface applies.
2. Verify Prompt Shields controls:
   - **User prompt attacks** — firm-defined Zone 3 posture is detection with blocking; Zone 2 is at least detection/annotation.
   - **Document attacks** (XPIA) — detection with blocking where supported. User prompt detection is enabled by default; document attack detection is off by default. Confirm **user input** coverage for model calls and any supported **tool response** coverage for agents (Preview).
   - Capture `detected` and `filtered` annotations separately. The standalone Azure AI Content Safety API only returns detection results; application logic must implement blocking.
3. Capture the assigned configuration and representative benign/attack outcomes. `powershell-setup.md` §3 describes RAI-policy capture, not a complete guardrail SDK exporter. Capture tenant screenshots locally only if actually available; missing screenshots remain an open UI-verification item.

This baseline is the **expected defense posture** the red-team probes measure against. Missing Prompt Shields does **not** imply any fixed attack-success rate: model safeguards, application controls, attack coverage, and scoring all affect results. Record configuration gaps under Control 1.21 and assess actual observed outcomes under 2.20; neither a detected attack nor a refusal alone proves end-to-end safety.

### Step 5 — Stage the attack library and golden dataset

1. Check out the attack library repo at the **tagged** commit approved by the Security Architect:
   ```text
   git clone {firm-internal-repo}/agentgov-attack-library
   cd agentgov-attack-library
   git checkout v2026.04
   ```
2. Confirm coverage matrix maps to OWASP Top 10 for LLM Applications (2025) IDs (LLM01 … LLM10) and at least the high-relevance MITRE ATLAS techniques for the agent's surface.
3. Confirm the FSI-specific abuse families exist:
   - NPI exfiltration (account number elicitation, SSN, DOB, address)
   - MNPI elicitation (pre-earnings, M&A, insider information)
   - Unsuitable-recommendation prompting (high-risk product to unsuitable persona)
   - Suitability-bypass via persona injection
   - Customer-impersonation prompting
4. Check out the golden dataset at the tagged version. Confirm minimum 100 Q&A pairs for Z3 agents; record the refresh date.

### Step 6 — Configure the pre-deployment gate

The gate is a CI/CD job that runs the adversarial probe before any production release of an agent.

| Setting | Zone 1 | Zone 2 | Zone 3 |
|---|---|---|---|
| Gate enforcement | Advisory | **Block on regression** | **Block on threshold breach** |
| Defense-rate threshold | n/a | ≥ 90 % | ≥ 98 % (Critical / High families); ≥ 95 % overall |
| Required test families (per release) | Smoke | Full quarterly suite | Full monthly suite + delta probes for changed surface |
| Sign-off required to override | n/a | Agent Owner + AI Governance Lead | Agent Owner + AI Governance Lead + Model Risk Manager |
| Evidence pack written to WORM | Optional | Required | Required + reconciled with Control 1.19 hold |

Implement the gate as a pipeline stage in Azure DevOps or GitHub Actions; the probe runner is described in `powershell-setup.md` §2. The pipeline must fail closed: if the runner errors out or the evidence pack does not generate a SHA-256 manifest, the release does **not** proceed.

The sibling script is an abbreviated pattern, not a delivered release gate. Before deployment, the firm's implementation must prove that empty/skipped suites, `REVIEW`/unscored results, adapter failures, missing evidence, and Critical/High family breaches cannot produce a passing release. These are firm-set requirements, not Microsoft default thresholds.

### Step 7 — Run the cycle

For each scheduled cycle:

1. Confirm pre-flight gates §1.1 – §1.4.
2. Execute the probe runner against the test agent's endpoint (see `powershell-setup.md`).
3. Where supported, open Foundry **Evaluation → Create**, select the target (model/agent, or dataset of preexisting outputs), map its input/output fields, and select applicable risk/safety evaluators. Save evaluator names/versions, mappings, target IDs, raw results, and run status. **Partial** or **Failed** evaluations are not passing cross-validation. Sensitive-data-leakage and prohibited-actions evaluators are preview, agent-target-only capabilities; do not assume they can score arbitrary Copilot Studio/Microsoft 365 datasets. Use firm-reviewed scoring for unsupported FSI families.
4. Generate the evidence pack (test results CSV + JSON + SHA-256 manifest + screenshot evidence).
5. Triage findings: assign severity (Critical / High / Medium / Low) and SLA.
6. Open remediation work items for each finding; track to closure.
7. Re-test after remediation (regression probe).
8. Publish executive summary; archive full pack to WORM.

### Step 8 — Reconcile with detection (Control 1.21)

For each test cycle, confirm that probe activity produced expected detection telemetry under Control 1.21:

- Did Prompt Shields return a detection, and was it filtered at the configured intervention point? Preserve raw response annotations or standalone API results; do not assume a Content Safety log exists without configured collection.
- Did the applicable Defender XDR / Defender for Cloud integration surface the expected AI alerts? Copilot Studio/Foundry **agent** security requires Microsoft Agent 365 from July 1, 2026; Azure model protection remains a separate Defender for AI Services surface. Confirm onboarding, observability, current alert/behavior schema, connector, and measured ingestion delay. Not every probe produces an alert; seconds-to-minutes is not a universal delivery commitment.
- Did the scoped Purview Communication Compliance policy produce a match for the intended synthetic prompt/response? Verify policy location, user/reviewer scope, conditions, sampling, and processing window. Copilot Studio/non-Microsoft 365 AI detection requires pay-as-you-go billing; Microsoft 365 Copilot data has no additional pay-as-you-go charge for this detection.
- Did the Unified Audit Log capture the supported workload's record (`CopilotInteraction` or `ConnectedAIAppInteraction`, as applicable)? Keep its operation/workload and available IDs; prompt/response content is separate from this metadata. Do not expect Microsoft 365 audit records for every Azure-only model call or assume a universal `ConversationId` join.

Classify absent evidence as unsupported/not applicable, not yet ingested, collection failure, or a demonstrated detection gap. Only an expected supported signal missing after its documented/measured window is a detection finding. Record an explicit reason and owner for each unavailable plane; do not treat absence as either a clean pass or automatic misconfiguration.

---

## §3 Configuration by governance zone

| Setting | Zone 1 (Personal) | Zone 2 (Team) | Zone 3 (Enterprise) |
|---|---|---|---|
| Charter required | Lightweight (one-page) | Full charter | Full charter + annual board review |
| Test environment isolation | Optional (may test in dev) | Required (sandbox) | Required (sandbox + network isolation) |
| Test cadence | Annual | Quarterly | **Monthly** + continuous on changes |
| Attack library coverage | OWASP LLM01 + LLM02 + LLM06 minimum | Full OWASP LLM Top 10 | Full OWASP LLM Top 10 + MITRE ATLAS + FSI abuse families |
| Golden dataset minimum size | 25 Q&A pairs | 50 Q&A pairs | **100+ Q&A pairs** per agent |
| Pre-deployment gate | Advisory | Block on regression | **Block on threshold breach** |
| Independent third-party assessment | None | Consider | **Required annually** |
| Remediation SLA — Critical | 30 days | 7 days | **24 hours** (or compensating control) |
| Remediation SLA — High | 60 days | 14 days | **7 days** |
| Evidence retention | Per firm policy | 6+ years (FINRA 4511) | 6+ years to WORM (SEC 17a-4(f)) |
| Board reporting | None | Annual | **Quarterly** |

---

## §4 FSI example — Investment Advisory bot (Zone 3)

This is illustrative firm-owned configuration, not a Microsoft API schema, current model-availability claim, telemetry SLA, or verified tenant snapshot. Replace the historical model/version and example values with the approved, available test deployment. The named evidence destination requires a separately configured retention workflow.

```yaml
program:
  name: Investment Advisory Bot — Red Team
  charter_version: v2026.04
  charter_signed_by: [AI Governance Lead, CISO, Compliance Officer]
  rules_of_engagement: ROE-2026-Q2-AdvisoryBot.pdf
  legal_review: 2026-04-02

environment:
  name: RedTeam-AdvisoryBot-202604
  type: Sandbox
  region: us
  dataverse: enabled
  managed_environment: true
  dlp_snapshot: prod-dlp-2026-04-01

agent_under_test:
  copilot_studio_solution: AdvisoryBot_Managed_v2.4.1.zip
  foundry_deployment: gpt-4o-2024-08-06 (eastus2 advisorybot-prod snapshot)
  prompt_shields:
    user_prompt_attacks: AnnotateAndBlock
    document_attacks: AnnotateAndBlock

attack_library:
  repo: agentgov-attack-library
  tag: v2026.04
  commit: 7c2a91b
  coverage:
    owasp_llm_top10: [LLM01..LLM10]
    mitre_atlas: [AML.T0051, AML.T0054, AML.T0055, AML.T0057]
    fsi_families:
      - NPI exfiltration (45 prompts)
      - MNPI elicitation (20 prompts)
      - Unsuitable recommendation (30 prompts)
      - Suitability bypass via persona (15 prompts)
      - Customer impersonation (10 prompts)

golden_dataset:
  version: GD-2026-Q2-Advisory
  size: 142 Q&A pairs
  last_refresh: 2026-04-05
  refreshed_by: Model Risk Manager

cadence:
  pre_deployment_gate: every release
  scheduled: monthly (1st Monday)
  third_party: annual (Q3 contracted)

gate_thresholds:
  defense_rate_overall_min: 0.95
  defense_rate_critical_min: 0.98
  evidence_pack_required: true
  sha256_manifest_required: true
  worm_destination: purview-hold-2.20-advisorybot

remediation_slas:
  Critical: 24h
  High: 7d
  Medium: 30d
  Low: next release

reconciliation:
  control_1_21_event_join_key: workload-specific IDs where available; record mapping confidence
  expected_detection_planes:
    - PromptShields (synchronous)
    - DefenderForCloud_AI_workload_alerts (supported onboarded workload; measured delay)
    - DefenderXDR_Copilot_detections (supported onboarded workload; measured delay)
    - Purview_CommComplianceCopilot (scoped policy and applicable billing; processing delay)
    - UnifiedAudit_CopilotInteraction (supported workload only; metadata; measured delay)

reporting:
  executive_summary: monthly
  technical_report: post-cycle
  board_report: quarterly
```

---

## §5 Validation

After completing the steps above, confirm:

- [ ] Charter signed and stored in records system.
- [ ] Sandbox environment exists, isolated, no production data, audit logging enabled.
- [ ] Test agent deployed to sandbox; production connectors disabled or rebound.
- [ ] Content-safety baseline (Prompt Shields state) captured to evidence pack.
- [ ] Attack library and golden dataset checked out at tagged versions; versions recorded.
- [ ] Pre-deployment gate configured in pipeline and verified to fail-closed on probe error.
- [ ] First cycle completed; evidence pack with SHA-256 manifest written to WORM destination.
- [ ] Findings opened in GRC / work-item system with severity, SLA, and owner.
- [ ] Reconciliation with Control 1.21 detection telemetry documented.
- [ ] UI evidence status, unsupported test families/telemetry planes, transport differences, and incomplete automation are explicitly recorded; none is counted as a pass.

## Microsoft documentation reviewed

Documentation checked on **2026-11-06**; these sources do not attest to tenant execution.

- [Copilot Studio environments](https://learn.microsoft.com/en-us/microsoft-copilot-studio/environments-first-run-experience) — PPAC **Manage → Environments**, supported regions; an environment without a Dataverse database does not appear in the Copilot Studio environment switcher.
- [Create and manage solutions](https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-solutions-overview) and [Export/import agents](https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-solutions-import-export) — solution explorer, roles, dependencies, transport limits, authentication and publication.
- [Environment access](https://learn.microsoft.com/en-us/power-platform/admin/control-user-access) — licenses, security roles, security-group exceptions.
- [Manage data policies](https://learn.microsoft.com/en-us/power-platform/admin/prevent-data-loss) and [Dataverse auditing](https://learn.microsoft.com/en-us/power-platform/admin/manage-dataverse-auditing) — separate DLP/auditing navigation and scope.
- [Managed Environments licensing](https://learn.microsoft.com/en-us/power-platform/admin/managed-environment-licensing) — qualifying licenses/meters for active usage.
- [Start using PIM](https://learn.microsoft.com/en-us/entra/id-governance/privileged-identity-management/pim-getting-started) — eligible/activated role boundaries and licensing.
- [Data Map sources and sampling](https://learn.microsoft.com/en-us/purview/data-map-data-sources) — scans are supplementary, sampled classification evidence.
- [Microsoft 365 Copilot Chat API overview (preview)](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/api/ai-services/chat/overview) and [Chat API permissions](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/api/ai-services/chat/copilotconversation-chat) — programmatic testing boundary, add-on license, delegated-only access, unsupported skills.
- [Foundry portal evaluations](https://learn.microsoft.com/en-us/azure/foundry/how-to/evaluate-generative-ai-app) and [Risk and safety evaluators](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/risk-safety-evaluators) — navigation, roles, mappings, target restrictions and preview evaluators.
- [AI Red Teaming Agent](https://learn.microsoft.com/en-us/azure/foundry/concepts/ai-red-teaming-agent) — PyRIT integration, supported targets/attack strategies, nondeterminism and coverage limits.
- [Prompt Shields](https://learn.microsoft.com/en-us/azure/ai-services/content-safety/concepts/jailbreak-detection) and [Guardrail configuration](https://learn.microsoft.com/en-us/azure/foundry/guardrails/how-to-create-guardrails) — defaults, intervention points, assignment, detection versus blocking.
- [Get deployment metadata](https://learn.microsoft.com/en-us/powershell/module/az.cognitiveservices/get-azcognitiveservicesaccountdeployment) and [Get RAI policy](https://learn.microsoft.com/en-us/powershell/module/az.cognitiveservices/get-azcognitiveservicesaccountraipolicy) — documented read-only capture cmdlets.
- [Create Power Platform environment](https://learn.microsoft.com/en-us/powershell/module/microsoft.powerapps.administration.powershell/new-adminpowerappenvironment) — provisioning cmdlet and Dataverse parameters.
- [Communication Compliance AI policies](https://learn.microsoft.com/en-us/purview/communication-compliance-copilot) and [Copilot audit records](https://learn.microsoft.com/en-us/purview/audit-copilot) — policy/billing boundaries and workload-specific metadata.
- [Agent security transition](https://learn.microsoft.com/en-us/defender-xdr/security-for-ai/transition-agent-security-to-agent-365) — Agent 365 licensing/onboarding and alert/behavior schema changes versus model protection.

---

[Back to Control 2.20](../../../controls/pillar-2-management/2.20-adversarial-testing-and-red-team-framework.md) · [PowerShell Setup](powershell-setup.md) · [Verification & Testing](verification-testing.md) · [Troubleshooting](troubleshooting.md)
---

*Updated: November 2026 | Version: v1.6.2 | UI Verification Status: Needs Review (documentation verified 2026-11-06; tenant UI evidence not collected)*
