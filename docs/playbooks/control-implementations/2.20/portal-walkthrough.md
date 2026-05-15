# Control 2.20 — Portal Walkthrough: Adversarial Testing and Red Team Framework

**Control:** [2.20 — Adversarial Testing and Red Team Framework](../../../controls/pillar-2-management/2.20-adversarial-testing-and-red-team-framework.md)<br>
**Pillar:** Management<br>
**Last UI Verified:** April 2026<br>
**Estimated time:** 6–10 hours initial setup; 2–8 hours per recurring test cycle (varies by zone and agent surface)<br>
**Governance Levels:** Baseline / Recommended / Regulated

---

!!! danger "READ FIRST — what this walkthrough is and is NOT"
    This walkthrough configures the **proactive adversarial testing program** (red-team charter, attack library, isolated test environment, golden dataset, pre-deployment gate, evidence pack) for Microsoft 365 Copilot, Copilot Studio agents, and Azure AI Foundry-backed FSI agents.

    It is **NOT** a substitute for the following sibling controls. Each is a separate configuration surface with its own playbook:

    | If you need… | Use Control | Why this is not 2.20 |
    |---|---|---|
    | **Detection** of prompt injection / jailbreak / XPIA in production | **1.21** — Adversarial Input Logging | 2.20 is preventive (pre-deployment + scheduled probes); 1.21 is detective (production telemetry) |
    | General agent QA, regression testing, suitability validation | **2.5** — Testing & Validation | 2.5 covers functional QA; 2.20 covers adversarial / safety scenarios |
    | Independent model validation per OCC 2011-12 / SR 11-7 | **2.6** — Model Risk Management | 2.6 is the program; 2.20 is one input to 2.6 |
    | Bias and fairness testing | **2.11** — Bias Testing & Fairness | 2.11 covers protected-class fairness; 2.20 covers safety / abuse / exfiltration |
    | Sensitive Information Type tuning so DLP / Comm Compliance fires correctly during red-team probes | **1.13** — SITs and Pattern Recognition | SIT tuning is a prerequisite for measuring exfiltration test outcomes |
    | Content Safety / Prompt Shields configuration on the Azure AI deployment under test | **1.21** §3 (Prompt Shields surface) | 2.20 *measures* whether Prompt Shields blocks the attack; it does not configure Prompt Shields |
    | Evidence retention to WORM under SEC 17a-4(f) | **1.19** — eDiscovery for Agent Interactions | 2.20 generates evidence; 1.19 holds it |

!!! warning "Hedged-language reminder — supports, does not guarantee"
    The procedures below **support compliance with** OCC Bulletin 2011-12, Federal Reserve SR 11-7, FINRA Rule 3110, FINRA Regulatory Notice 25-07 (March 2025), SEC Rule 17a-4(b)(4), GLBA 501(b), and the NIST AI RMF Generative AI Profile (NIST AI 600-1). They **do not by themselves guarantee** regulatory compliance. The Compliance Officer, Model Risk Manager, and CISO must independently validate that the firm's WSPs reference the documented testing cadence, the actual defense-rate thresholds in use, and the firm's records-retention horizon.

!!! info "What this walkthrough covers — surfaces & owners"
    | # | Surface | Portal | Owner role | Notes |
    |---|---|---|---|---|
    | 1 | Red-team program charter (document) | Internal GRC system | AI Governance Lead | Charter must precede any tenant action |
    | 2 | Isolated test environment | `admin.powerplatform.microsoft.com` | Power Platform Admin | Sandbox; no production data |
    | 3 | Test agent deployment (Copilot Studio) | `copilotstudio.microsoft.com` | Copilot Studio Agent Author | Cloned from production at known config snapshot |
    | 4 | Azure AI Foundry deployment under test (if applicable) | `ai.azure.com` | Azure AI Owner | Read-only review of content filters & Prompt Shields |
    | 5 | Attack library + golden dataset (version-controlled) | Internal repo | Security Architect + Model Risk Manager | Reviewed quarterly |
    | 6 | Pre-deployment gate (CI/CD pipeline) | Azure DevOps / GitHub Actions | Cloud Security Architect | Gate threshold defined per zone |
    | 7 | Evidence pack (test results + SHA-256 manifest) | Storage with WORM / immutability lock | Cloud Security Architect | Reconcile with Control 1.19 hold |
    | 8 | Findings register + remediation tracking | Internal GRC system | AI Governance Lead | SLA enforcement; risk-acceptance signatures |

---

## §0 Coverage boundary, sovereign-cloud notes, and portal vs script matrix

### 0.1 Coverage boundary

In scope:

- Microsoft 365 Copilot, Copilot Studio agents, and Azure OpenAI / Azure AI Foundry-backed agents in any zone.
- Adversarial test categories: prompt injection (direct + indirect / XPIA), jailbreak, system-prompt extraction, data exfiltration (NPI / MNPI), suitability bypass, encoded evasion (Base64, Unicode confusables, zero-width), tool / plugin abuse, multi-turn manipulation.
- Pre-deployment probes and scheduled cycles (monthly Z3, quarterly Z2, annual Z1).

Out of scope (handled by sibling controls — see READ FIRST):

- Production detection (1.21), eDiscovery hold (1.19), bias testing (2.11), general QA (2.5), connector / DLP authoring (3.1), and incident response workflow (3.4).

### 0.2 Sovereign-cloud applicability

| Capability | Commercial | GCC | GCC High | DoD | Notes |
|---|---|---|---|---|---|
| Copilot Studio test environment | GA | GA | Limited preview — verify | Limited — verify | Re-confirm against M365 Government service description |
| Azure AI Foundry — Risk and Safety Evaluations | GA | Rolling | Lagging — verify | Lagging — verify | Substitute: PyRIT + custom scoring on Foundry diagnostic logs |
| Microsoft PyRIT | OSS — runs anywhere | OSS | OSS | OSS | The toolkit is open source; sovereign concern is the *target* surface, not PyRIT itself |
| Azure AI Content Safety — Prompt Shields | GA | Rolling | Lagging — verify | Lagging — verify | If Prompt Shields is unavailable, document compensating control (pre-prompt classifier in app code) |

!!! warning "Treat any cross-cloud parity claim as time-bound"
    Re-verify against the [Microsoft 365 Government service description](https://learn.microsoft.com/en-us/office365/servicedescriptions/office-365-platform-service-description/office-365-us-government/office-365-us-government) **before** treating any item above as a primary control in GCC / GCC High / DoD. Document the verification date in the change ticket.

### 0.3 Portal vs script matrix

| Step | Portal? | Script? | Notes |
|---|---|---|---|
| Author program charter | Internal GRC / Word | n/a | Document, sign, store in records system |
| Create isolated test environment | ✅ PPAC | ✅ `New-AdminPowerAppEnvironment` | Portal recommended for first-time setup; script for repeatable refresh |
| Clone production agent into sandbox | ✅ Copilot Studio (Solutions export/import) | ✅ Solution CLI | Portal walkthrough below; see `powershell-setup.md` for solution-based pipeline |
| Maintain attack library | Source repo | n/a | Version control (Git) is the system of record |
| Run probes against agent endpoint | ❌ | ✅ PyRIT / `Invoke-AdversarialTests.ps1` | No portal-driven probe runner |
| Run Azure AI Foundry Risk & Safety Evaluations | ✅ AI Foundry | ✅ Foundry SDK | Portal-driven for ad-hoc; SDK for pipeline |
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
- [ ] Sandbox environment **contains no production customer data**. Synthetic data only. Verify via Purview Data Map scan of the sandbox storage.

### 1.3 Identity gate

- [ ] Test users exist in a non-licensed test OU; do not reuse production identities.
- [ ] Operator account uses **Privileged Identity Management (PIM)** for elevation; standing access not granted.
- [ ] Audit logging is enabled in the sandbox (Control 1.7) so probe activity is captured and retrievable.

### 1.4 Tooling gate

- [ ] Microsoft PyRIT installed at a CAB-approved version on the operator workstation or pipeline runner.
- [ ] Attack library repository checked out at a tagged commit; commit SHA recorded for the run.
- [ ] Golden dataset checked out at a tagged version; version recorded.
- [ ] Evidence storage location confirmed and immutability / retention policy verified (link to Control 1.19 hold).

---

## §2 Step-by-step portal configuration

### Step 1 — Author and sign the red-team program charter

The charter is a **documentary** prerequisite, not a portal action. Capture in the firm's GRC system the following sections:

| Section | Required content |
|---|---|
| Purpose | Why the program exists; mapping to OCC Bulletin 2026-13 (formerly OCC 2011-12) / Fed SR 26-2 (formerly SR 11-7) / FINRA 3110 / Notice 25-07 |
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
2. **Environments → New**.
3. Configure:
   - **Name:** `RedTeam-{AgentName}-{YYYYMM}` (e.g. `RedTeam-AdvisoryBot-202604`)
   - **Type:** Sandbox
   - **Region:** Same as production
   - **Dataverse:** Add only if production agent uses Dataverse
   - **Security group:** Restrict to red-team operator group
4. After provisioning, open the environment → **Settings → Privacy + Security**:
   - Confirm DLP policies match production at snapshot date.
   - Enable detailed auditing.
5. Apply the **Managed Environment** posture if production is managed.

!!! note "Do not skip the security-group restriction"
    Without a security group, default-tenant access lets unintended users see test prompts that may contain sensitive synthetic data. Restrict at create-time, not after.

### Step 3 — Clone the production agent into the sandbox

For Copilot Studio agents:

1. Open [Copilot Studio](https://copilotstudio.microsoft.com/).
2. Switch to the **production** environment.
3. Open the agent → **Settings → Solutions → Export as solution → Managed**.
4. Switch to the **sandbox** environment.
5. **Solutions → Import** → upload the exported solution.
6. After import, open the agent and **disable any production connectors** (Graph, SharePoint, custom connectors) or rebind them to sandbox equivalents.
7. Re-publish the agent to a sandbox channel only (do **not** re-publish to Teams / Web for the production audience).

For Azure AI Foundry-backed agents:

1. Open [Azure AI Foundry](https://ai.azure.com/).
2. Select the production project.
3. **Deployments → Export** the model deployment configuration (JSON).
4. In the sandbox project, recreate the deployment with the same model, version, and content-filter (RAI policy) configuration.
5. Confirm Prompt Shields (UPIA + XPIA) state matches production. Record the snapshot in the evidence pack.

### Step 4 — Verify content-safety baseline on the agent under test

Open the test agent's Azure AI Foundry deployment (if applicable):

1. **Deployments → {deployment} → Content filter (RAI policy)**.
2. Verify Prompt Shields:
   - **User prompt attacks** — should be **Annotate and Block** for Zone 3, at least **Annotate** for Zone 2.
   - **Document attacks** (XPIA) — should be **Annotate and Block** where Prompt Shields supports it.
3. Capture screenshots and the policy JSON via the Foundry SDK (see `powershell-setup.md` §3) for the evidence pack.

This baseline is the **expected defense posture** the red-team probes will measure against. If Prompt Shields is not configured, the probe will record near-100 % attack success — the finding is then misattributed (it's a Control 1.21 / Foundry config gap, not an agent design defect).

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

### Step 7 — Run the cycle

For each scheduled cycle:

1. Confirm pre-flight gates §1.1 – §1.4.
2. Execute the probe runner against the test agent's endpoint (see `powershell-setup.md`).
3. Run Azure AI Foundry Risk & Safety Evaluations on the same prompt set for cross-validation.
4. Generate the evidence pack (test results CSV + JSON + SHA-256 manifest + screenshot evidence).
5. Triage findings: assign severity (Critical / High / Medium / Low) and SLA.
6. Open remediation work items for each finding; track to closure.
7. Re-test after remediation (regression probe).
8. Publish executive summary; archive full pack to WORM.

### Step 8 — Reconcile with detection (Control 1.21)

For each test cycle, confirm that probe activity produced expected detection telemetry under Control 1.21:

- Did Prompt Shields fire on the encoded-evasion family? (Cross-check Azure AI Content Safety logs.)
- Did Defender XDR / Defender for Cloud surface AI alerts in the seconds-to-minutes latency window?
- Did Purview Communication Compliance flag the supervisory-relevant prompts?
- Did the Unified Audit Log capture the `CopilotInteraction` records (metadata only — UAL does not contain full prompt body)?

Reconciliation gaps mean either Control 2.20 attack-library coverage is incomplete **or** Control 1.21 detection is mis-tuned. Both findings flow to the Control 1.21 owner and the AI Governance Lead.

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
  control_1_21_event_join_key: ConversationId
  expected_detection_planes:
    - PromptShields (synchronous)
    - DefenderForCloud_AI_workload_alerts (seconds–minutes)
    - DefenderXDR_Copilot_detections (seconds–minutes)
    - Purview_CommComplianceCopilot (minutes–hours)
    - UnifiedAudit_CopilotInteraction (minutes–hours; metadata only)

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

---

[Back to Control 2.20](../../../controls/pillar-2-management/2.20-adversarial-testing-and-red-team-framework.md) · [PowerShell Setup](powershell-setup.md) · [Verification & Testing](verification-testing.md) · [Troubleshooting](troubleshooting.md)
