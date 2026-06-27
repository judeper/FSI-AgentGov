---
description: "Topic-organized lookup. Each section is one CSA scenario:"
---
<!-- verify-language-rules: allow-second-tier  reason: "CSA quick reference must quote CAPE and vendor marketing language verbatim (in scare quotes) so the CSA can teach reframing to customers and counter-position with examiners." -->

# CSA Quick Reference — FSI Agent Governance Conversations

!!! info "Audience"
    **Microsoft Cloud Solution Architects, Customer Success Architects, and FSI account team specialists** preparing for or running customer conversations about AI agent governance with banks, broker-dealers, insurers, asset managers, and credit unions. This document assumes you have introduced [Microsoft CAPE](https://aka.ms/AgenticTransformationPatterns) materials in customer settings and need an FSI-specific translation layer. Customers should be referred to the [CCO Quick Reference](cco-quick-reference.md) for examiner-facing positioning, and to the [Microsoft CAPE Crosswalk](microsoft-cape-crosswalk.md) for the pattern × control deep-dives.

---

## How to use this document

Topic-organized lookup. Each section is one CSA scenario:

- **Conversation opener** — what to say.
- **Customer signal** — what they say back that confirms or shifts the conversation.
- **FSI-AgentGov anchor** — the doc, playbook, or control to cite live.
- **Watch-out** — what NOT to say (regulatory landmines and vocabulary collisions).

If you are NEW to FSI-AgentGov, read the [CSA Positioning Guide](csa-positioning-guide.md) first.

This document is intentionally short. The companion [CSA Positioning Guide](csa-positioning-guide.md) carries the long-form narrative, the 6-pattern conversation playbook, and the brand-boundary discussion. Use the Positioning Guide when you onboard to the framework; use this Quick Reference live in a customer meeting.

---

## 1. The 60-second elevator: how to introduce FSI-AgentGov in a CAPE conversation

> **"Microsoft CAPE gives you the pattern vocabulary — the 6 Frontier Transformation Patterns, the 5 capability drivers, and the Center of Excellence operating model. FSI-AgentGov is the FSI translation layer: it takes those patterns and tells you, for a US bank or broker-dealer, which governance zone the pattern lands in, which FINRA, SEC, OCC, and Federal Reserve obligations attach, and which of the 79 controls in the framework you need before that pattern goes to production. CAPE is industry-agnostic; FSI-AgentGov is the regulator-grade overlay. They run together."**

That is the verbatim line. After the customer reacts, the next sentence should be one of three pivots, depending on persona — see [§8 Conversation openers](#8-conversation-openers-by-audience).

---

## 2. Pattern × Zone × FSI quick map

One row per CAPE pattern. Pull canonical numbering and the autonomy guardrail from [`transformation-patterns.md`](../framework/transformation-patterns.md).

| Pattern | One-line FSI use case | Default zone | Critical controls (per manifest) | Regulatory landmine | Crosswalk deep-dive |
|---|---|---|---|---|---|
| **1 — Employee AI Enablement** | M365 Copilot for the front office, no customer data writes. | Zone 1 (promote to Zone 2 once output is shared) | [1.1](../controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md), [2.14](../controls/pillar-2-management/2.14-training-and-awareness-program.md) | None typically; watch GLBA 501(b) inadvertent disclosure and FINRA Rule 3110 supervisor visibility into AI-assisted drafts. | [Pattern 1](microsoft-cape-crosswalk.md#pattern-1-employee-ai-enablement) |
| **2 — Business Expert Empowerment** | Compliance policy Q&A, credit risk Q&A, regulatory interpretation assistants. | Zone 2 (internal SME) or Zone 3 (regulated SME domain) | [2.16](../controls/pillar-2-management/2.16-rag-source-integrity-validation.md) | RAG source integrity (FINRA Rule 4511 books-and-records); supervision of advisory output (FINRA Rule 3110). | [Pattern 2](microsoft-cape-crosswalk.md#pattern-2-business-expert-empowerment) |
| **3 — Workplace & IT Services** | HR / IT support agents touching payroll or trade-settlement systems. | Zone 2 baseline; **Zone 3 mandatory** if it touches payroll, trade settlement, registered-person HR records, or customer files | [2.8](../controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md) | SoD failures (SOX 404); insider-risk exposure on registered-person records (FINRA Rule 3110). | [Pattern 3](microsoft-cape-crosswalk.md#pattern-3-workplace-it-services) |
| **4 — Core Business Process Transformation** | KYC / CDD, claims adjudication, financial close, loan origination, regulatory reporting. | **Zone 3 mandatory** | [2.6](../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md), [2.11](../controls/pillar-2-management/2.11-bias-testing-and-fairness-assessment.md), [2.12](../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) | OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12) / Federal Reserve SR 26-2 model risk; ECOA / Reg B fair lending principal-reasons; SOX 302/404; BSA/AML. | [Pattern 4](microsoft-cape-crosswalk.md#pattern-4-core-business-process-transformation-deep-dive) |
| **5 — External Engagement** | Customer servicing chat, retail-comms agents, account-opening intake. | **Zone 3 mandatory** | [1.19](../controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md), [2.11](../controls/pillar-2-management/2.11-bias-testing-and-fairness-assessment.md), [2.12](../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md), [2.19](../controls/pillar-2-management/2.19-customer-ai-disclosure-and-transparency.md), [2.26](../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md), [4.4](../controls/pillar-4-sharepoint/4.4-guest-and-external-user-access-controls.md) | FINRA Rule 3110 supervision (Notice 24-09 technology-neutral), FINRA Rule 2210 retail comms, Reg BI care obligation, GLBA 501(b), Reg E EFT error-resolution, ECOA / Reg B, state AI disclosure laws (CA SB 1001/SB 243, UT SB 149, CO AI Act). | [Pattern 5](microsoft-cape-crosswalk.md#pattern-5-external-engagement-deep-dive) |
| **6 — AI-First Capabilities** | Multi-agent orchestration, agent-built workflows, predictive planning systems. | **Zone 3 mandatory + D3 guardrail** | [2.17](../controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md), [2.20](../controls/pillar-2-management/2.20-adversarial-testing-and-red-team-framework.md), [3.9](../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md), [3.14](../controls/pillar-3-reporting/3.14-agent-365-observability-sdk.md) | Documented regulator pre-approval expected for fully autonomous customer-impacting deployments; OCC Bulletin 2026-13 high-risk model tier; documented model-risk acceptance; vendor-concentration risk. | [Pattern 6](microsoft-cape-crosswalk.md#pattern-6-ai-first-capabilities-deep-dive) |

!!! warning "Pattern 6 D3 guardrail (verbatim from `transformation-patterns.md`)"
    Fully autonomous customer-impacting Pattern 6 deployments are not currently supported in Zone 3 without documented regulator pre-approval.

> **Note on critical controls.** The "Critical controls" column lists only controls flagged `pattern_critical` in [`assessment/manifest/controls.json`](https://github.com/judeper/FSI-AgentGov/blob/main/assessment/manifest/controls.json) — the source of truth for which controls are mission-critical per pattern. Each pattern carries a much wider mandatory-control set in its [crosswalk deep-dive](microsoft-cape-crosswalk.md#4-pattern-deep-dives); cite the deep-dive when the customer asks for the full Zone 3 baseline. The full 78×6 mapping is in the generated [Pattern Coverage matrix](pattern-coverage.md).

---

## 3. The 5 capability drivers — quick translation for FSI customers

The drivers are a **diagnostic**, not a scorecard. CAPE's load-bearing insight is that the *weakest* driver is the scaling ceiling for any pattern, regardless of how strong the others are. Use this to redirect a "we want to deploy Pattern 5" conversation into "let's identify the scale-breaker first."

| Driver | One-sentence FSI translation | Scale-breaker indicator | Conversation hook | Doc cross-link |
|---|---|---|---|---|
| **AI Strategy & Experience** | Whether the firm has a deliberate, board-sponsored AI program with named roles, funding, and an experience point of view. | No board-approved AI strategy, no exec sponsor, AI investment is project-by-project. | "Where does AI sit on your strategic plan, and who at the board is the named sponsor?" | [Driver 1](../framework/agentic-capability-drivers.md#driver-1-ai-strategy-experience) |
| **Business Strategy** | Depth of AI integration into business processes and outcome measurement, including process redesign appetite. | AI use cases are bolted onto existing processes; no end-to-end redesign; outcome measurement is anecdotal. | "When you greenlight an agent, do you redesign the process around it, or do you bolt it onto today's process?" | [Driver 2](../framework/agentic-capability-drivers.md#driver-2-business-strategy) |
| **AI Governance & Security** | Risk management, compliance, monitoring, supervision, identity isolation, and responsible-AI practices. | No autonomy-cap discipline; supervision is ad-hoc; bias testing absent or not stratified; identity isolation not implemented for customer-facing surfaces. | "If FINRA walks in tomorrow and asks who supervises this agent, who does the firm name?" | [Driver 3](../framework/agentic-capability-drivers.md#driver-3-ai-governance-security) |
| **Technology & Data** | Platform maturity, RAG architecture, data quality, telemetry, multi-agent orchestration plumbing. | RAG corpora are stale or unmanaged; no observability SDK; no multi-agent orchestration substrate; data quality issues are surfaced by users not by monitoring. | "How fresh is the RAG corpus your knowledge agent answers from, and who is accountable for keeping it current?" | [Driver 4](../framework/agentic-capability-drivers.md#driver-4-technology-data) |
| **Organization & Culture** | Adoption enablement, supervisor training, builder community, change-management discipline, and AI-positive culture. | Supervisor training is absent; no maker community; builders are isolated; FINRA 3110 acceptable-use program does not exist. | "Have your front-office supervisors been trained on reviewing AI-generated drafts before they reach a customer?" | [Driver 5](../framework/agentic-capability-drivers.md#driver-5-organization-culture) |

> **Diagnostic shortcut for the meeting.** Ask the customer to score each of the five drivers on a 1–5 scale (no need to use CAPE's 100–500 numbering live). The lowest-scored driver is the scale-breaker. Most US FSI firms scale-break on **AI Governance & Security** or **Organization & Culture**. The structured diagnostic lives in the [Frontier Readiness assessment](https://github.com/judeper/FSI-AgentGov/blob/main/assessment/README.md) — recommend running it as the workshop opener (see [§7](#7-which-assessment-do-i-run-with-this-customer)).

---

## 4. The "another framework?" objection — 3 reframes

Customers will push back: "We already have a framework — NIST AI RMF, internal model risk, our own AI governance committee. Why do we need another one?" Use these three reframes in order.

1. **"It is the FSI translation layer for what Microsoft already gave you."** CAPE is industry-agnostic by design — it has to work for a manufacturer, a retailer, and a bank. FSI-AgentGov takes the same patterns Microsoft is already teaching you and adds the FINRA, SEC, OCC, Federal Reserve, and CFPB overlays you need to defend the deployment to your examiner. It is not a replacement for CAPE; it is the FSI extension that the M365 admin, the CCO, and the model risk function can all read in their own dialect.

2. **"You don't pick one. Frontier (capability) and Controls (compliance) answer different questions."** The CAPE *Frontier Readiness* diagnostic and the FSI-AgentGov *78-control assessment* answer different questions. Frontier asks *"is your organization ready to scale?"* — it identifies the capability scale-breaker. Controls asks *"do your tenant configurations satisfy zone thresholds?"* — it identifies the technical compliance gaps. The two are complementary, not redundant. See [the assessment decision tree](#7-which-assessment-do-i-run-with-this-customer) and [`assessment/README.md`](https://github.com/judeper/FSI-AgentGov/blob/main/assessment/README.md).

3. **"It runs on the materials your account team is already showing you."** The framework deliberately re-uses CAPE's six patterns, five drivers, and four CoE functions as its strategic vocabulary — see the [Microsoft CAPE Crosswalk](microsoft-cape-crosswalk.md) for the line-by-line alignment. Adopting FSI-AgentGov does not require your team to learn a new model; it requires them to *translate* CAPE statements into FSI Zones and into specific controls.

---

## 5. Federation guardrail — what NOT to promise

This is the most-watched objection. CAPE explicitly supports a Federated CoE shape, and customers will read federation as relief from supervision. **It is not.** The framework's federation guardrail (see [`agentic-coe.md`](../framework/agentic-coe.md#the-federation-guardrail), reproduced below verbatim) applies in FSI regardless of which CoE shape the customer chooses.

> **Federating CoE roles to business units does NOT transfer regulated supervisory accountability. FINRA 3110 supervision, OCC Bulletin 2026-13 model risk oversight, Fed SR 26-2 obligations, and SOX 302/404 attestations remain with the named FSI roles regardless of where the CoE function operationally sits.**

**In plain English for the customer:** A wealth division can stand up its own builders and ship its own KYC agent, but the named registered principal (broker-dealer) or designated control function (bank) still owns the supervisory record under FINRA Rule 3110, and the central Govern function still owns the OCC Bulletin 2026-13 / Fed SR 26-2 model risk tier and the consolidated agent inventory. Federated execution; central regulatory record. The compliant alternative to "the BU runs its own CoE" is "the BU runs its own CoE chapter; central Govern retains attestation authority and the federation guardrail belongs in the chapter charter."

**What NOT to say:** *"Federate to the business units to scale faster"* — without naming the guardrail. CSAs who say this set the customer up for an examiner finding three quarters later. Always name the guardrail in the same breath as the federation pitch.

---

## 6. Anti-patterns I see in the field — and the fix

Three CAPE anti-patterns translated to FSI symptoms. Two more (federation as relief from supervision; Ghost CoE charter) are equally important and live in [`agentic-coe.md`](../framework/agentic-coe.md#fsi-specific-coe-anti-patterns).

- **The Gatekeeper.** *Symptom in FSI:* every Zone 2 agent requires Legal review before deployment, lead times balloon to 6 weeks, business lines start standing up shadow agents in personal environments to bypass the queue. *Fix:* Govern owns release-gate enforcement on Zone 2 / Zone 3 only, with documented criteria, named approvers, and a written-justification exception process with CRO sign-off. Zone 1 agents move on the maker's authority. The exception process is the safety valve. (See [`agentic-coe.md` Anti-pattern 2](../framework/agentic-coe.md#anti-pattern-2-coe-govern-function-configured-as-advisory-rather-than-as-a-release-gate).)

- **The Ghost.** *Symptom in FSI:* a CoE charter is signed, the four functions (Govern / Enable / Optimize / Scale) are named on paper, the operating rhythm is defined — and then the rhythm never materializes. The weekly standup is cancelled three times in a row, the monthly scorecard is produced once and forgotten. The charter satisfies an audit finding but the operating engine never starts. *Fix:* treat the CoE rhythm as a Pillar 1 audit-logged activity — meeting attendance, decisions, and action items belong in a Control 1.7 audit-logged location (a controlled SharePoint site or Dataverse table). Missed cadence shows up as audit evidence and triggers escalation. (See [`agentic-coe.md` Anti-pattern 6](../framework/agentic-coe.md#anti-pattern-6-ghost-coe-charter).)

- **The Perfectionist.** *Symptom in FSI:* "We can't deploy any agent until we have full FINRA Rule 3110 supervision workflows, OCC Bulletin 2026-13 model validation, examiner-ready evidence trails, bias testing automation, customer disclosure governance, and a board-approved acceptable-use policy." Result: 18-month planning cycles, zero agents in production, and a maker community that gives up. *Fix:* ship Zone 1 agents with Baseline controls now, learn from the operating signal, scale to Zone 2 with Recommended controls, then graduate to Zone 3 with Regulated controls. Adaptive governance is examiner-defensible; analysis paralysis is not.

---

## 7. Which assessment do I run with this customer?

Mirror the language in [`assessment/README.md`](https://github.com/judeper/FSI-AgentGov/blob/main/assessment/README.md). Add CSA-specific context: **use Frontier Readiness as the workshop opener, use Controls as the audit-prep deliverable.**

| Run **Controls** if... | Run **Frontier Readiness** if... | Run **Both** if... |
|---|---|---|
| You are an M365 admin conducting a technical compliance baseline. | You are a CIO / CDAO / AI Program Sponsor evaluating agent program maturity. | You want a comprehensive program assessment with both strategic (Frontier) and tactical (Controls) outputs. |
| Preparing for an audit or examiner readiness review. | Deciding which Frontier Transformation Pattern to prioritize next. | Onboarding a customer at the start of a transformation engagement. |
| You need a 78-control gap report with maturity scores and remediation backlog. | You need to identify the scale-breaker driver before investing in any pattern. | The customer wants the [`capability-driver-rollup.json`](https://github.com/judeper/FSI-AgentGov/blob/main/assessment/README.md#output-files) artifact that cross-references control maturity by driver tag — useful for board-level briefings. |

**Recommended sequencing.** Run **Frontier Readiness first** (25 questions, 15–30 minutes facilitator-led) to identify the scale-breaker. Then run **Controls** (2–4 hour collector run plus manual questionnaire) to remediate the specific control gaps that move the scale-breaker driver forward. Re-run Controls after remediation to confirm uplift.

> **Honesty note for the customer.** The Frontier Readiness assessment is *facilitator-answered* (no auto-evaluators in v1) — it is a structured self-assessment, not auditor-grade evidence. The honest coverage report is at [`docs/reference/frontier-assessment-coverage.md`](frontier-assessment-coverage.md). The 78-control assessment carries the [`docs/reference/assessment-coverage.md`](assessment-coverage.md) honest report — every check is tagged `auto_evaluable`, `manual_only`, or `unimplemented_evaluator`. Lead with these reports — customers respect that we name the gaps.

---

## 8. Conversation openers by audience

Three openers, one per persona. Each gives the canonical opening sentence and the redirect when the customer pushes back.

### Opening with a CIO

**Opener.** *"Most of your AI agent risk lives in the platform configuration — environments, DLP, identity isolation, audit logging, and the agent inventory. Microsoft CAPE gives you the strategic vocabulary to choose which patterns to invest in; FSI-AgentGov gives you the 78-control technical baseline that supports compliance with FINRA, SEC, OCC, and Federal Reserve obligations on the platform side. We can run a 78-control assessment against your tenant in 2–4 hours and hand you a maturity scorecard and remediation backlog that the M365 admin team can act on Monday morning."*

**If they redirect to "we're already a Microsoft shop, why do we need this":** "Exactly the point. The 79 controls are configurations of the M365, Power Platform, Purview, and Sentinel surfaces you already own. The framework tells you which configurations matter for which regulator and which zone. There is nothing here to buy."

### Opening with a CDO / CDAO

**Opener.** *"The CAPE Frontier Transformation Patterns let you classify agent investments by shape — employee enablement, expert empowerment, workplace services, core process, external engagement, AI-first. The five Capability Drivers tell you, before you pick a pattern, what your scale-breaker is — the dimension that will block scale regardless of how much you invest in the others. FSI-AgentGov runs the Frontier Readiness diagnostic in a 25-question facilitator-led session. We then map the scale-breaker to the FSI controls that will move it. That gives you a sequenced program rather than a pattern wish list."*

**If they redirect to "we already use NIST AI RMF":** "Good — they are complementary. NIST gives you GOVERN / MAP / MEASURE / MANAGE; CAPE gives you patterns and capability drivers; FSI-AgentGov gives you the FSI control overlays. We have a [NIST crosswalk](nist-ai-rmf-crosswalk.md) and a [CAPE crosswalk](microsoft-cape-crosswalk.md). Pick whichever is closer to how your governance committee already thinks."

### Opening with a CCO / Chief Risk Officer

**Opener.** *"Pull up the [CCO Quick Reference](cco-quick-reference.md). It is structured by examiner question — twelve questions an OCC, FINRA, or SEC examiner is likely to ask, each with a one-line answer the CCO can give in a meeting before opening any binder, plus the controls, playbooks, and crosswalk sections that back it. The framework's posture for Pattern 6 — fully autonomous customer-impacting deployments are not currently supported in Zone 3 without documented regulator pre-approval — is in there too. The framework is opinionated for US FSI; it does the regulatory translation work the CCO would otherwise build from scratch."*

**If they redirect to "we already have model risk under OCC Bulletin 2026-13 (formerly OCC 2011-12)":** "Right. The framework slots into your existing model risk function. [Control 2.6](../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md) is the alignment artifact, with explicit cross-references to OCC Bulletin 2026-13 and the 2026 SR 26-2 supersession. The agent-specific overlays — supervision under FINRA Rule 3110 ([Control 2.12](../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md)), agent inventory under FINRA Rule 4511 ([Control 3.1](../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md)), customer disclosure under FINRA Rule 2210 ([Control 2.19](../controls/pillar-2-management/2.19-customer-ai-disclosure-and-transparency.md)) — are what's net-new for AI agents."

---

## 9. Decision aids the CSA can use live

Three short decision trees rendered as bullets — read them out loud in the meeting.

**Customer-facing? → Zone 3 → Pattern 5 (or skip).**

- Is the agent talking directly to a customer, prospect, partner, or counterparty? → Yes → **Zone 3 mandatory, Pattern 5 mandatory**, full FINRA 2210 / Reg BI / Reg E / ECOA / GLBA / state-AI-disclosure stack engaged. See [Pattern 5 deep-dive](microsoft-cape-crosswalk.md#pattern-5-external-engagement-deep-dive).
- No → continue to the next decision tree.

**Multi-agent orchestration? → Pattern 6 → D3 guardrail required.**

- Does the deployment chain two or more agents whose decisions cumulatively affect a customer? → Yes → **Pattern 6**. Either (a) keep the chain internal-only (no production decision rights), (b) put a documented human supervisor in the loop for every customer-impacting outcome, or (c) obtain documented regulator pre-approval. See [Pattern 6 deep-dive](microsoft-cape-crosswalk.md#pattern-6-ai-first-capabilities-deep-dive).
- No → continue.

**Existing process or new capability? → Pattern 4 vs Pattern 2/3.**

- Is the agent reshaping a regulated business-critical flow (KYC, claims, financial close, regulatory reporting, lending decisioning, suitability)? → Yes → **Pattern 4, Zone 3 mandatory**, OCC Bulletin 2026-13 / Fed SR 26-2 model risk attaches. See [Pattern 4 deep-dive](microsoft-cape-crosswalk.md#pattern-4-core-business-process-transformation-deep-dive).
- Is it scaling SME judgment (compliance Q&A, policy interpretation, model docs)? → **Pattern 2**, Zone 2 (or Zone 3 if the SME domain is regulated). See [Pattern 2](microsoft-cape-crosswalk.md#pattern-2-business-expert-empowerment).
- Is it an internal service (HR, IT, facilities)? → **Pattern 3**, Zone 2 baseline (Zone 3 if it touches payroll, trade settlement, registered-person HR records, or customer files). See [Pattern 3](microsoft-cape-crosswalk.md#pattern-3-workplace-it-services).

> **In doubt?** Pick the more conservative (higher-numbered) pattern and review with risk and compliance. The cost of starting with stricter controls and relaxing on review is small; the cost of under-classifying a customer-facing or core-business-process deployment and discovering the gap during an examination is large.

---

## 10. Field caveats and brand boundary

**Open-source community framework, not a Microsoft product.** FSI-AgentGov is open-source, community-maintained, and is **NOT a Microsoft product**. Microsoft alignment is intentional — most US FSI firms are M365 shops and the framework adopts CAPE patterns, drivers, and CoE functions as its strategic vocabulary by design — but alignment does not constitute Microsoft endorsement, support, or warranty. Microsoft can co-promote; Microsoft does not endorse. CSAs may **recommend** FSI-AgentGov to a customer; CSAs may **not** represent FSI-AgentGov as a Microsoft offering or say "Microsoft has approved this framework." See the repository [Disclaimer](../disclaimer.md) for the full statement.

**Audience is M365 administrators and compliance officers, not developers or end users.** The 79 controls describe configurations of the M365, Power Platform, Purview, Sentinel, and SharePoint surfaces an admin owns. The CSA Quick Reference and CSA Positioning Guide are an *additional audience layer above the admin focus* — they do not change the underlying audience of the controls themselves. Customers running primarily on AWS Bedrock or Vertex AI need to extend or substitute; the framework's opinion is biased toward the M365 ecosystem.

**Pattern 6 carries an explicit framework guardrail (D3).** Repeated in §2 above and reproduced from [`transformation-patterns.md`](../framework/transformation-patterns.md): *Fully autonomous customer-impacting Pattern 6 deployments are not currently supported in Zone 3 without documented regulator pre-approval.* Do not commit a customer to a Pattern 6 production deployment without naming this guardrail in the same conversation.

---

## Related documents

- [CSA Positioning Guide](csa-positioning-guide.md) — narrative companion for onboarding to the framework and handling positioning objections.
- [CCO Quick Reference](cco-quick-reference.md) — examiner-facing version organized by examiner question.
- [Microsoft CAPE Crosswalk](microsoft-cape-crosswalk.md) — pattern × control deep-dives and Regulatory Exposure callouts.
- [Transformation Patterns](../framework/transformation-patterns.md) — 6-pattern framework summary including the Pattern 6 D3 guardrail.
- [Agentic Capability Drivers](../framework/agentic-capability-drivers.md) — 5-driver framework summary and scale-breaker concept.
- [Agentic Center of Excellence](../framework/agentic-coe.md) — CoE structure (Centralized / Hybrid / Federated), federation guardrail, and the 6 FSI-specific anti-patterns.
- [Zones and Tiers](../framework/zones-and-tiers.md) — Zone 1 / 2 / 3 definitions and per-zone control thresholds.
- [Operating Model](../framework/operating-model.md) — RACI, governance committee, and canonical role assignments.
- [Role Catalog](role-catalog.md) — canonical short role names (e.g., Entra Global Admin, AI Administrator, Power Platform Admin).
- [Frontier Readiness Coverage](frontier-assessment-coverage.md) — honest 0% auto coverage report for the Frontier diagnostic.
- [CAPE Pattern Coverage matrix](pattern-coverage.md) — generated 78×6 control-to-pattern matrix.
- [Assessment README](https://github.com/judeper/FSI-AgentGov/blob/main/assessment/README.md) — when to run Controls vs Frontier vs Both.
- [NIST AI RMF Crosswalk](nist-ai-rmf-crosswalk.md) — complementary GOVERN / MAP / MEASURE / MANAGE alignment.

---

*FSI Agent Governance Framework v1.6.2 | Updated: May 2026 | UI Verification Status: Current*
