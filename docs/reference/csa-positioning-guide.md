<!-- verify-language-rules: allow-second-tier  reason: "CSA positioning guide must quote CAPE and competitor marketing language verbatim (in scare quotes) to teach CSAs how to reframe and respond to common positioning objections." -->

# CSA Positioning Guide — FSI Agent Governance in Microsoft CAPE Conversations

!!! info "Audience"
    **Microsoft Cloud Solution Architects, Customer Success Architects, and FSI account team specialists** who introduce [Microsoft CAPE](https://aka.ms/AgenticTransformationPatterns) acceleration content into US financial services customer engagements. This document is a positioning narrative — it teaches you how to position FSI-AgentGov as the FSI extension to CAPE, when to lead with which artifact, and how to handle the most common objections. For in-meeting lookups, use the [CSA Quick Reference](csa-quick-reference.md). For examiner-facing positioning, point your customer's CCO to the [CCO Quick Reference](cco-quick-reference.md). For pattern × control depth, send them to the [Microsoft CAPE Crosswalk](microsoft-cape-crosswalk.md).

---

## Why this document exists

Microsoft is already teaching pattern vocabulary in FSI customer meetings. CAPE's six Frontier Transformation Patterns, five Capability Drivers, and four-function CoE model are landing on customer whiteboards every week. The CIO and CDAO arrive at the conversation already pattern-aware. They use phrases like *"we're doing Pattern 2 — business expert empowerment for compliance Q&A"* or *"we're at Maturity Level 300 in Governance & Security."* They expect the CSA across the table to be fluent in the same vocabulary, and to translate it into something their CCO and their model risk function can actually defend.

That translation is the gap. CAPE is industry-agnostic by design — it has to work for a manufacturer, a retailer, and a bank simultaneously. The FSI customer hears the pattern, agrees with the strategic framing, and then asks: *"OK, but what does Pattern 4 mean for FINRA Rule 3110 supervision? Which of OCC 2011-12's model-risk obligations does it trigger? Where do my Reg B principal-reasons obligations land if a KYC agent declines a credit-related application?"* Without an answer, the conversation stalls. With FSI-AgentGov as the translation layer, the CSA can pivot from CAPE's strategic vocabulary to the specific FSI controls, the specific regulatory anchors, and the specific examiner red flags that the pattern triggers — usually in the same meeting.

This guide tells you how to do that pivot. It is opinionated, it is field-tested, and it is intentionally narrow: it focuses on US FSI conversations where the customer is a Microsoft shop and CAPE has already entered the room. It does not try to cover every governance conversation or every cloud platform. The guide's audience is Microsoft Cloud Solution Architects and Customer Success Architects in the FSI segment, plus the broader account team specialists who support them.

Read this guide once when you onboard to the framework. After that, refer back to specific sections as objections arise. The companion [CSA Quick Reference](csa-quick-reference.md) is the in-meeting lookup; this document is the playbook.

---

## Section 1 — Position: FSI-AgentGov as the FSI translation layer for Microsoft CAPE

### 1.1 The frame: pattern × control × evidence

The cleanest framing is three words: **patterns are HOW, controls are WHAT, evidence is PROOF.** CAPE gives the customer the pattern vocabulary — what shape the deployment takes, who the agent talks to, what the scale-breaker is. FSI-AgentGov's 78-control catalog gives the customer the WHAT — which technical configurations of the M365, Power Platform, Purview, Sentinel, and SharePoint surfaces support compliance with the regulator's expectations for that pattern. FSI-AgentGov's playbooks, evidence templates, and assessment engine give the customer the PROOF — the artifacts they can hand an examiner.

This frame is load-bearing because it disposes of the most common positioning collision live in the room. When a customer says *"we're already using NIST AI RMF, why do we need another framework?"*, the answer is not "FSI-AgentGov is better." The answer is "NIST AI RMF gives you the GOVERN/MAP/MEASURE/MANAGE program structure; CAPE gives you the pattern shape; FSI-AgentGov gives you the FSI-specific controls and the evidence pack. They sit at different layers." See [`nist-ai-rmf-crosswalk.md`](nist-ai-rmf-crosswalk.md) for the explicit alignment.

### 1.2 What CAPE answers, what FSI-AgentGov answers

CAPE answers *strategic* questions: *Which patterns should we invest in? Where is our scale-breaker? How should the CoE be shaped? What is the 90-day operating play?* CAPE is deliberately industry-agnostic — it carries five Capability Drivers (AI Strategy & Experience, Business Strategy, AI Governance & Security, Technology & Data, Organization & Culture) at a 100–500 maturity scale, and it identifies the *weakest* driver as the scaling ceiling regardless of how strong the others are. That diagnostic insight is genuinely useful and genuinely portable across industries.

FSI-AgentGov answers *regulator-specific* questions: *Which FINRA, SEC, OCC, Federal Reserve, GLBA, ECOA, Reg E, BSA/AML, CFPB, and state-AI-law obligations attach to this pattern in this zone? Which of the 78 controls supports compliance with those obligations? What is the audit retention period? What does the examiner ask, and what is the one-line answer the CCO can give before opening any binder?* The answers live in the [Microsoft CAPE Crosswalk](microsoft-cape-crosswalk.md), the [Regulatory Mappings](regulatory-mappings.md), the [Zones and Tiers](../framework/zones-and-tiers.md) doc, and the per-pillar control documentation. The [CCO Quick Reference](cco-quick-reference.md) is the conversational summary.

The two are not competitive. Customers do not pick CAPE *or* FSI-AgentGov; they run CAPE for the strategy lens and FSI-AgentGov for the regulatory overlay. The CSA's job is to make sure the customer never sees the two as alternatives.

### 1.3 Where the two converge: the Frontier Readiness diagnostic and the 78-control catalog

The convergence point is the assessment surface. FSI-AgentGov ships two assessments in `assessment/`:

- The **Frontier Readiness assessment** is a 25-question facilitator-led diagnostic that scores each of the five CAPE Capability Drivers on the Microsoft 100–500 scale and identifies the scale-breaker. It runs in 15–30 minutes. It is the right artifact to open a CIO / CDAO workshop with — see [§4.1](#41-frontier-readiness-as-the-workshop-opener).
- The **Controls assessment** is a 78-control technical assessment that runs five PowerShell collectors against the customer's tenant, evaluates checks against zone thresholds, and emits a maturity scorecard plus a remediation backlog plus a manual questionnaire. It runs in 2–4 hours of collector time plus the manual questionnaire. It is the right artifact to deliver after a customer has committed to the program — see [§4.2](#42-controls-as-the-examiner-prep-deliverable).

The two assessments share the `applicable_drivers` tag on every control. When you run **Both** in a single engagement, the framework emits a `capability-driver-rollup.json` artifact that cross-references control maturity by driver — useful for board-level briefings where the CDAO wants to show the AI Governance & Security driver progressing from L300 to L400 over a quarter, with the specific underlying control uplifts named. See the [Assessment README](https://github.com/judeper/FSI-AgentGov/blob/main/assessment/README.md) for the canonical decision tree.

### 1.4 The brand boundary: open-source community framework, not a Microsoft product

This boundary is non-negotiable and is the single CSA discipline that protects both the framework's credibility and Microsoft's. **FSI-AgentGov is open-source, community-maintained, and is NOT a Microsoft product. Microsoft alignment is intentional but does not constitute Microsoft endorsement, support, or warranty.**

CSAs may *recommend* FSI-AgentGov to a customer; CSAs may *not* represent FSI-AgentGov as a Microsoft offering. Statements like *"Microsoft recommends FSI-AgentGov"* or *"Microsoft has approved FSI-AgentGov as the FSI control framework"* are not accurate and should not appear in customer materials. Statements like *"This is the framework I take into customer meetings — it's the FSI extension to CAPE that I find most useful"* are accurate and helpful. The full repository [Disclaimer](../disclaimer.md) is the authoritative statement; Section 8 below expands on the brand boundary in narrative form.

---

## Section 2 — Three audiences, three openings

The CSA conversation is shaped by who is in the room. Three personas, three openings.

### 2.1 Opening with a CIO

The CIO cares about platform configuration, supplier consolidation, technical debt, the M365 admin team's ability to operate at scale, and the cost of saying no to a board-mandated AI program. The CIO is rarely the day-one regulatory expert; they have a CCO and CRO for that. What the CIO needs from you is a credible *"this is the technical baseline"* answer that the M365 admin team can act on without inventing the framework themselves.

**The opening sentence.** *"Most of your AI agent risk lives in platform configuration — environments, DLP, identity isolation, audit logging, and the agent inventory. CAPE gives you the strategic vocabulary to choose which patterns to invest in; FSI-AgentGov gives you the 78-control technical baseline that supports compliance with FINRA, SEC, OCC, and Federal Reserve obligations on the platform side. We can run a 78-control assessment against your tenant in 2–4 hours and hand you a maturity scorecard and remediation backlog the M365 admin team can act on Monday morning."*

**The pivot.** From here, the natural next step is to walk the CIO through [the Pattern × Zone fit matrix](microsoft-cape-crosswalk.md#3-pattern-zone-fit-matrix). The CIO will recognize their current portfolio in the matrix immediately — *"we're heavy in Pattern 1 today, we're piloting Pattern 2 for compliance Q&A, the CDAO wants Pattern 4 for KYC next year, the business wants Pattern 5 for retail servicing."* That conversation puts you in a position to map each pattern's controls to the customer's M365 admin backlog, and to surface where the customer needs Frontier Readiness work before pursuing the more aggressive patterns.

**The artifact you leave behind.** The Controls assessment summary plus the [`docs/reference/portal-paths-quick-reference.md`](portal-paths-quick-reference.md) for the M365 admin team. The CIO will not read either; the admin team will.

**Common CIO objection.** *"We're already a Microsoft shop, why do we need this?"* The answer: *"Exactly the point. The 78 controls are configurations of the M365, Power Platform, Purview, and Sentinel surfaces you already own. The framework tells you which configurations matter for which regulator and which zone. There is nothing here to buy. The framework is open-source community content; the value is the FSI translation work that would otherwise sit on your CCO's desk."*

### 2.2 Opening with a CDAO

The CDAO cares about portfolio shape, capability maturity, scale-breaker diagnostics, executive sponsorship, and the AI program's narrative for the board. The CDAO is the persona most fluent in CAPE vocabulary because CAPE was authored for them. They walk into the meeting having already digested the Walking Deck and the Patterns Playbook. What they want from you is the FSI-specific *"so what?"* — the translation from generic capability maturity to specific FSI investments and the order in which to make them.

**The opening sentence.** *"The CAPE Frontier Transformation Patterns let you classify agent investments by shape — employee enablement, expert empowerment, workplace services, core process, external engagement, AI-first. The five Capability Drivers tell you, before you pick a pattern, what your scale-breaker is — the dimension that will block scale regardless of how much you invest in the others. FSI-AgentGov runs the Frontier Readiness diagnostic in a 25-question facilitator-led session. We then map the scale-breaker to the FSI controls that will move it. That gives you a sequenced program rather than a pattern wish list."*

**The pivot.** Open the Frontier Readiness manifest live ([`assessment/manifest/frontier-readiness.json`](https://github.com/judeper/FSI-AgentGov/blob/main/assessment/manifest/frontier-readiness.json)). Walk the CDAO through the question structure — five drivers × five questions per driver, scored 100–500 with FSI-anchored anchor statements. Then surface the [per-pattern target profiles](../framework/agentic-capability-drivers.md#per-pattern-target-profiles) — the table that records, for each Frontier Transformation Pattern, the FSI-AgentGov reference target for each driver, with the scale-breaker per CAPE marked with a star. The CDAO will instantly see why their Pattern 5 ambition with an Org & Culture driver at L300 is doomed without supervisor training and acceptable-use enforcement.

**The artifact you leave behind.** The Frontier Readiness pre-filled report ([`output/frontier-prefilled.md`](https://github.com/judeper/FSI-AgentGov/blob/main/assessment/README.md#output-files)) plus the executive-facing [Capability Drivers narrative](../framework/agentic-capability-drivers.md). The CDAO will read both and bring excerpts to the next executive committee meeting.

**Common CDAO objection.** *"We already use NIST AI RMF as our framework."* The answer: *"Good — they are complementary, not competing. NIST gives you the GOVERN / MAP / MEASURE / MANAGE program structure. CAPE gives you the pattern shape and the scale-breaker diagnostic. FSI-AgentGov gives you the FSI control overlays and the regulatory mappings. We carry a [NIST crosswalk](nist-ai-rmf-crosswalk.md) and a [CAPE crosswalk](microsoft-cape-crosswalk.md). Pick whichever vocabulary your governance committee already thinks in. The 78 controls underneath are the same."*

### 2.3 Opening with a CCO / Chief Risk Officer

The CCO and CRO care about examiner readiness, named principal accountability, supervisory documentation, model risk tiering, books-and-records reconstruction, customer disclosure, fair lending defensibility, and incident response. They walk into the meeting having either lived through an AI-related sweep recently or expecting one in the next 12 months. What they want from you is a framework that the examiner will *recognize* — that uses regulatory anchors the examiner cites verbatim, that names the obligations under FINRA Rule 3110, FINRA Rule 4511, SEC 17a-4, OCC 2011-12 / SR 26-2, GLBA 501(b), Reg P, ECOA / Reg B, and Reg E — and that comes with evidence templates the CCO can hand over without rewriting.

**The opening sentence.** *"Pull up the [CCO Quick Reference](cco-quick-reference.md). It is structured by examiner question — twelve questions an OCC, FINRA, or SEC examiner is likely to ask, each with a one-line answer the CCO can give in a meeting before opening any binder, plus the controls, playbooks, and crosswalk sections that back it. The framework's posture for Pattern 6 — fully autonomous customer-impacting deployments are not currently supported in Zone 3 without documented regulator pre-approval — is in there too. The framework is opinionated for US FSI; it does the regulatory translation work the CCO would otherwise build from scratch."*

**The pivot.** Walk the CCO through Q1 (recordkeeping), Q2 (supervision), Q3 (model risk), and Q11 (frontier patterns) of the CCO Quick Reference. Each question has the same five-element shape: short answer, supporting evidence, regulatory anchor, examiner red flag. The CCO will recognize the structure immediately — it mirrors how an examination workpaper is organized.

**The artifact you leave behind.** The full [CCO Quick Reference](cco-quick-reference.md) plus the [Regulatory Mappings](regulatory-mappings.md). The CCO may also want the [Examination Response Guide](../playbooks/compliance-and-audit/examination-response-guide.md) and the [Evidence Pack Assembly](../playbooks/compliance-and-audit/evidence-pack-assembly.md) playbooks — both surface in CCO Quick Reference Q1, Q3, and Q12.

**Common CCO objection.** *"We already have model risk under OCC 2011-12, run by our model validation function. Why is this different?"* The answer: *"It isn't different — it slots in. [Control 2.6](../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md) is the alignment artifact, with explicit cross-references to OCC 2011-12 and the 2026 SR 26-2 supersession. The agent-specific overlays — supervision under FINRA Rule 3110 ([Control 2.12](../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md)), agent inventory under FINRA Rule 4511 ([Control 3.1](../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md)), customer disclosure under FINRA Rule 2210 ([Control 2.19](../controls/pillar-2-management/2.19-customer-ai-disclosure-and-transparency.md)), Entra Agent ID identity governance ([Control 2.26](../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md)) — are what's net-new for AI agents. Your model validation function still validates; the framework gives you the agent-specific controls that did not exist as a category before agents."*

---

## Section 3 — Handling the four most common objections

### 3.1 "We already have a governance framework"

*Vendor-neutral objection — typically pointed at a competing FSI framework, an internal home-grown framework, or a consultancy-authored one.*

**Reframe.** Two facts are usually true at once. (1) The customer does have a governance framework. (2) The framework was almost certainly designed before agents existed as a deployment category — most internal FSI governance frameworks predate Copilot Studio, Agent 365, and multi-agent orchestration. Your role is not to displace their framework; it is to surface the *gap* their framework leaves around AI agents specifically. The 78 controls in FSI-AgentGov are agent-specific configurations of M365 / Power Platform / Purview / Sentinel / SharePoint surfaces. They sit *underneath* a customer's existing program-level governance, not in tension with it.

**Redirect.** *"Your governance framework probably tells you to do bias testing. FSI-AgentGov tells you that, for an agent in a Pattern 5 retail-servicing surface, bias testing means [Control 2.11](../controls/pillar-2-management/2.11-bias-testing-and-fairness-assessment.md), stratified by protected-class proxies, retained per the records-retention matrix, surfaced in [Control 3.10](../controls/pillar-3-reporting/3.10-hallucination-feedback-loop.md) telemetry, with re-baselining triggered by [Control 2.3](../controls/pillar-2-management/2.3-change-management-and-release-planning.md) on every retraining. Your framework gives you the obligation; FSI-AgentGov gives you the M365-native implementation pattern."*

**Watch-out.** Do not say *"your framework is incomplete"* — that puts the CCO on the defensive. Say *"your framework was scoped before agents existed as a category."* That is almost always factually true and lets the customer save face.

### 3.2 "Why not just use Microsoft CAPE directly?"

*Common from a CDAO who has just digested the CAPE materials and is wondering what FSI-AgentGov adds.*

**Reframe.** CAPE is industry-agnostic by design. Microsoft built it to work for a manufacturer, a retailer, a hospital system, and a bank simultaneously. That portability is its strength — the patterns and capability drivers translate across industries. It is also its limitation in regulated FSI: CAPE does not name FINRA Rule 2210 (because most industries are not broker-dealer regulated), it does not name OCC 2011-12 (because most industries are not bank-supervised), and it does not name Reg B (because most industries do not extend credit). When CAPE describes Pattern 4 as *"agents make routine decisions autonomously and escalate exceptions to humans,"* that phrasing is fine for a manufacturer but lands directly on §V of OCC 2011-12 (ongoing monitoring, outcomes analysis, change control) for a bank.

**Redirect.** *"Use CAPE for the strategic vocabulary — patterns, drivers, CoE shapes, scale-breakers. Use FSI-AgentGov for the regulatory translation. Every CAPE pattern in the [crosswalk](microsoft-cape-crosswalk.md) carries a six-row Regulatory Exposure callout that names the FINRA, SEC, OCC, Federal Reserve, GLBA, ECOA, Reg E, and CFPB obligations that pattern triggers in FSI, plus the specific FSI controls that support compliance with each. CAPE gives you the *what*; FSI-AgentGov gives you the *what under FINRA Rule 3110*."*

**Watch-out.** Do not say *"CAPE is not enough."* CAPE was never meant to be FSI-specific. Say *"CAPE is industry-agnostic; FSI-AgentGov is the FSI overlay."* That positions the two as layered, not as competitive.

### 3.3 "Can my business unit run its own CoE? CAPE supports federation."

*Common from a CIO at a global SIFI or a large diversified financial-holding company where federation is operationally attractive.*

**Reframe — and this is the most-watched objection in the field.** CAPE explicitly describes three CoE shapes — Centralized, Hybrid, and Federated — chosen by pattern. A customer reading CAPE will see Federation as a legitimate design choice. *In FSI, federation is a legitimate design choice for operating shape; it is not a transfer of supervisory accountability.* The federation guardrail in [`agentic-coe.md`](../framework/agentic-coe.md#the-federation-guardrail) is reproduced verbatim from the framework's Regulatory Counsel input:

> **Federating CoE roles to business units does NOT transfer regulated supervisory accountability. FINRA 3110 supervision, OCC 2011-12 model risk oversight, SR 26-2 obligations, and SOX 302/404 attestations remain with the named FSI roles regardless of where the CoE function operationally sits.**

In plain English: a wealth division can stand up its own builders, run its own intake, and operate its own KYC agent. The named registered principal still owns the FINRA Rule 3110 supervisory record; the central Govern function still owns the OCC 2011-12 / SR 26-2 model risk tier and the consolidated agent inventory; the central CCO still owns customer-facing disclosure approval. Federated execution; central regulatory record. The two scenarios in [`agentic-coe.md` §The federation guardrail](../framework/agentic-coe.md#two-specific-scenarios) walk through Pattern 4 (federated wealth) and Pattern 5 (federated retail bank) explicitly.

**Redirect.** *"Federation is a workable design choice in FSI when (a) the central Govern function has disproportionately strong [Pillar 3 Reporting controls](../controls/CONTROL-INDEX.md) — particularly [3.1 Agent Inventory](../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md), [3.2 Usage Analytics](../controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md), [3.10 Hallucination Feedback](../controls/pillar-3-reporting/3.10-hallucination-feedback-loop.md), [3.14 Observability SDK](../controls/pillar-3-reporting/3.14-agent-365-observability-sdk.md) — to give the central principal end-to-end visibility, and (b) the federation guardrail is documented explicitly in the CoE charter and in each business-line CoE chapter charter. Without those two preconditions, default Centralized."*

**Watch-out.** Do not promise *"federate to scale faster"* without naming the guardrail in the same conversation. CSAs who do this set the customer up for an examiner finding three quarters later. The single most common framework anti-pattern in FSI ([Anti-pattern 5 in `agentic-coe.md`](../framework/agentic-coe.md#anti-pattern-5-federation-read-as-relief-from-supervision)) is *Federation read as relief from supervision* — a business line interpreting its CoE chapter as a transfer of supervisory accountability. Naming the guardrail aloud is the field discipline that prevents this.

### 3.4 "Is FSI-AgentGov a Microsoft offering?"

*Common from a procurement or vendor-management function evaluating whether to add FSI-AgentGov to an approved-vendor list.*

**Reframe.** FSI-AgentGov is open-source, community-maintained content. It is not a Microsoft product; Microsoft does not endorse, support, or warrant it. Microsoft alignment is intentional — the framework adopts CAPE patterns, drivers, and CoE functions as its strategic vocabulary by design — but alignment is not endorsement. The repository [Disclaimer](../disclaimer.md) is the authoritative statement.

**Redirect.** *"FSI-AgentGov is open-source content under an open-source license. There is nothing to procure. The 78 controls are configurations of M365 / Power Platform / Purview / Sentinel / SharePoint surfaces you already license. The framework is the translation work between Microsoft's industry-agnostic CAPE materials and the FSI regulatory landscape; the implementation lives entirely in your existing Microsoft tenant. Treat it like you treat NIST AI RMF — open content you adopt, adapt, and operationalize. The fact that I (a Microsoft CSA) recommend it does not make it a Microsoft offering."*

**Watch-out.** Do not represent FSI-AgentGov as a Microsoft offering. See [§8](#section-8-microsoft-alignment-is-intentional-here-is-the-brand-boundary) for the brand boundary discussion.

---

## Section 4 — When to lead with which assessment

### 4.1 Frontier Readiness as the workshop opener

The Frontier Readiness assessment is a 25-question facilitator-led diagnostic that scores each of the five CAPE Capability Drivers on the Microsoft 100–500 maturity scale. It runs in 15–30 minutes of interview time. It is *not* an automated assessment — there are no auto-evaluators in v1, and the [`docs/reference/frontier-assessment-coverage.md`](frontier-assessment-coverage.md) report names this honestly as 0% auto coverage. Every question is facilitator-answered against FSI-anchored anchor statements.

**Why it is the right opener.** A Frontier Readiness session opens an executive workshop because it produces a single high-signal output the CDAO and CIO can both react to: *the scale-breaker driver*. The output identifies the dimension of organizational capability that will block agent program scale regardless of how strong the others are. Most US FSI firms scale-break on **AI Governance & Security** (no autonomy-cap discipline, supervision is ad-hoc, identity isolation absent) or **Organization & Culture** (supervisor training absent, no maker community, no acceptable-use program). The diagnostic surfaces this in a way that is hard to argue with — the customer answered the questions themselves.

**Pattern readiness analysis.** The Frontier Readiness output also includes a per-pattern readiness analysis: which of the six Frontier Transformation Patterns the customer is ready to scale today, which require investment in specific drivers first, and which are blocked by the scale-breaker. This is the artifact that converts a *"we want to do Pattern 5 next year"* aspiration into a sequenced *"first invest in Org & Culture L400, then deploy Pattern 5 in Q3"* program.

**Sequencing recommendation.** Run Frontier Readiness *first*. Identify the scale-breaker. Then run Controls to remediate the specific control gaps that move the scale-breaker driver forward. The two assessments are linked through the `applicable_drivers` tag on every control — the framework knows which controls move which drivers, and the [`capability-driver-rollup.json`](https://github.com/judeper/FSI-AgentGov/blob/main/assessment/README.md#output-files) artifact (generated when you run **Both**) makes the cross-reference explicit. See [`assessment/README.md`](https://github.com/judeper/FSI-AgentGov/blob/main/assessment/README.md) for the canonical decision tree.

**Limitations to name explicitly.** Frontier Readiness is facilitator-answered. It is a structured self-assessment, not auditor-grade evidence. It is best used as a strategic conversation aid; it should not be cited in an examination workpaper as objective evidence. The honest coverage report at [`docs/reference/frontier-assessment-coverage.md`](frontier-assessment-coverage.md) names this gap; lead with the limitation when you introduce the assessment.

### 4.2 Controls as the examiner-prep deliverable

The Controls assessment is a 78-control technical assessment that runs five PowerShell collectors against the customer's tenant — Power Platform Admin Center (PPAC), Microsoft Graph, Purview, SharePoint, and Sentinel — evaluates each check against the relevant zone thresholds, and emits a maturity scorecard (0–4 per control), a remediation backlog, a manual questionnaire for the controls that cannot be auto-evaluated, and per-control evidence pointers. Total run time is 2–4 hours of collector time plus the manual questionnaire.

**Why it is the right examiner-prep deliverable.** The Controls assessment produces auditor-grade evidence. Every check carries an `evaluator_state` field with one of three values — `auto_evaluable`, `manual_only`, or `unimplemented_evaluator` — and the per-control output includes the specific tenant configuration that satisfies (or fails) the check. The honest coverage report at [`docs/reference/assessment-coverage.md`](assessment-coverage.md) names exactly how many of the 78 controls are auto-evaluated versus manual-only versus awaiting evaluator implementation. That transparency is what makes it credible to an internal audit function or an external examiner.

**When in the engagement.** Run Controls *after* the customer has committed to the program. Frontier Readiness opens the workshop and identifies the scale-breaker; Controls delivers the technical baseline and the remediation backlog. The Controls output is the artifact the M365 admin team and the CCO will both reference for the next 12–24 months. It is also the artifact that supports CCO answers to the twelve examiner questions in the [CCO Quick Reference](cco-quick-reference.md).

**Mode and authentication.** The Controls assessment supports interactive (delegated) authentication for first-time customer engagements and service-principal authentication for repeat runs. See [`assessment/README.md` Quick Start](https://github.com/judeper/FSI-AgentGov/blob/main/assessment/README.md#quick-start) for the parameter table. Customers will ask about scoping; the answer is the assessment runs read-only and emits to a customer-controlled `output/` directory that is gitignored — no customer data is ever committed to the FSI-AgentGov repository.

**Limitations to name explicitly.** Some checks are manual-only because the underlying signal cannot be reliably collected via API (e.g., supervisor training program documentation, governance committee meeting minutes, exception-rationale narratives). These show up in the manual questionnaire. The honest coverage report names which controls are in this state. Do not promise customers a fully-automated assessment; the framework's discipline is to be honest about coverage.

### 4.3 Both as the comprehensive program assessment

Running both assessments in a single engagement produces three artifacts that are useful together:

- The **Frontier Readiness pre-filled report** ([`output/frontier-prefilled.md`](https://github.com/judeper/FSI-AgentGov/blob/main/assessment/README.md#output-files)) names the scale-breaker driver and the per-pattern readiness analysis.
- The **Controls pre-filled report** ([`output/assessment-prefilled.md`](https://github.com/judeper/FSI-AgentGov/blob/main/assessment/README.md#output-files)) names the 78-control maturity scorecard and the remediation backlog.
- The **Capability Driver Rollup** ([`output/capability-driver-rollup.json`](https://github.com/judeper/FSI-AgentGov/blob/main/assessment/README.md#output-files)) cross-references the Controls maturity scores by CAPE driver tag — answering "which of our control gaps are blocking which of our drivers?"

The third artifact is the high-signal output for board-level briefings. It lets the CDAO show the board *"we are at L300 on AI Governance & Security; the specific control gaps blocking L400 are 2.6 (model risk), 2.11 (bias testing), 2.12 (supervision), and 2.18 (COI testing); remediation will close these in Q3 and move us to L400 by year-end."* That narrative is hard to assemble without the rollup.

Recommend the Both run for new customer onboarding, board-level program reviews, and the start of a multi-quarter transformation engagement. For ongoing operations and audit cycles, run Controls alone on a quarterly cadence and Frontier Readiness annually.

---

## Section 5 — The 6 patterns: FSI conversation playbook

Use this section as the per-pattern conversation script. Each subsection includes FSI use cases, zone fit, the headline regulatory exposure, the common CSA conversation flow, the CAPE deck slide where the pattern is named, and the FSI-AgentGov cross-links you should be ready to surface live.

### 5.1 Pattern 1 — Employee AI Enablement

**FSI use cases.** M365 Copilot for the front office (drafting, summarization, research, scheduling). Personal Copilot Studio agents that automate individual workflows. Personal-scope Power Automate flows that draft emails or summarize meetings. The hallmark is that the agent serves the individual employee and the human retains decision authority on every output that reaches a customer or a colleague.

**Zone fit.** Default **Zone 1**. Promotes to Zone 2 the moment output is shared into team channels. Promotes to Zone 3 if the output reaches a customer or generates regulated content. The CAPE pattern is described as *"every employee uses capable AI assistants"* — in FSI, the framing must include the supervisor visibility loop, because a draft generated by Copilot and sent to a customer becomes a FINRA Rule 2210 communication subject to principal review.

**Headline regulatory exposure.** GLBA 501(b) inadvertent disclosure (PII / MNPI / customer files reaching personal drafts), FINRA Rule 3110 supervisor visibility into AI-assisted drafts, FINRA Rule 2210 if the draft reaches a retail customer, state privacy law (CCPA / CPRA) where applicable.

**CSA conversation flow.** *"Pattern 1 is the typical entry point for M365 Copilot in your front office. The risk profile is dominated by inadvertent disclosure and supervision gaps. The framework's mandatory controls for this pattern are [1.1 Restrict Agent Publishing](../controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md) and [2.14 Training and Awareness](../controls/pillar-2-management/2.14-training-and-awareness-program.md), plus the broader Zone 1 baseline ([1.5 DLP](../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md), [1.7 Audit Logging](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md), [1.11 Conditional Access + MFA](../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md), [2.23 Disclosure Enforcement](../controls/pillar-2-management/2.23-user-consent-and-ai-disclosure-enforcement.md), [3.2 Usage Analytics](../controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md)). The CAPE scale-breaker for this pattern is Organization & Culture L300 — supervisor training and acceptable-use enforcement under FINRA Rule 3110 and the firm's WSP."*

**Cross-links to surface.** [Pattern 1 deep-dive](microsoft-cape-crosswalk.md#pattern-1-employee-ai-enablement). [Driver 5 — Organization & Culture](../framework/agentic-capability-drivers.md#driver-5-organization-culture). [Zone 1 in Zones and Tiers](../framework/zones-and-tiers.md#zone-1).

### 5.2 Pattern 2 — Business Expert Empowerment

**FSI use cases.** Compliance policy Q&A (a knowledge agent over the firm's WSP). Credit risk Q&A. Regulatory interpretation assistants. Model documentation lookup. Supervisory support agents. The pattern scales the judgment of a small number of subject-matter experts via a knowledge agent, with the named SME remaining accountable for any answer relied upon for a regulatory or supervisory decision.

**Zone fit.** Default **Zone 2**. Promotes to **Zone 3** when the SME domain is regulated (compliance, supervision, model risk, fair lending). The CAPE scale-breaker for this pattern is Technology & Data L300 — knowledge quality is the credibility of the agent — and in FSI this also produces a books-and-records integrity problem: the Q&A trail is itself a record under FINRA Rule 4511 and SEC 17a-4.

**Headline regulatory exposure.** FINRA Rule 3110 supervision of advisory output, FINRA Rule 4511 books-and-records (the Q&A trail is a record), SEC 17a-4 record retention, OCC 2011-12 / Fed SR 26-2 if the SME content is model-related.

**CSA conversation flow.** *"Pattern 2 is the most-attempted Zone 2 deployment shape in FSI right now — compliance Q&A is everybody's first 'real' agent use case. The risk profile centers on RAG corpus drift, hallucination, and the failure mode where associated persons start treating the agent as the firm's de facto policy interpretation instead of as an advisory tool. Mandatory controls are [2.16 RAG Source Integrity](../controls/pillar-2-management/2.16-rag-source-integrity-validation.md), [2.5 Testing/Validation](../controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md), [2.13 Documentation/Records](../controls/pillar-2-management/2.13-documentation-and-record-keeping.md), [3.10 Hallucination Feedback](../controls/pillar-3-reporting/3.10-hallucination-feedback-loop.md), [4.1 SharePoint IAG](../controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md), and [4.6 Grounding Scope](../controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md). When the SME domain is regulated, supervision under [Control 2.12](../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) attaches and the deployment moves to Zone 3."*

**Cross-links to surface.** [Pattern 2 deep-dive](microsoft-cape-crosswalk.md#pattern-2-business-expert-empowerment). [Driver 4 — Technology & Data](../framework/agentic-capability-drivers.md#driver-4-technology-data).

### 5.3 Pattern 3 — Workplace & IT Services

**FSI use cases.** HR helpdesk agents. IT support agents. Facilities ticket triage. The pattern shape is "agents running internal services end-to-end, with humans handling escalations." In FSI the pattern is straightforward when the service is purely internal and non-regulated; it becomes Zone 3 the moment it touches payroll (SOX 404 ICFR), trade settlement support (FINRA Rule 4511 books-and-records), HR records of registered persons (FINRA Rule 3110 supervision implications), or customer files (Reg P privacy, GLBA).

**Zone fit.** Default **Zone 2** for non-regulated internal services. **Zone 3 mandatory** when the service touches payroll, trade settlement, registered-person HR records, or customer files. CAPE's default Tier 2 placement understates the risk for FSI in those cases — this is one of the cleanest examples of the FSI Zone overriding the CAPE Tier.

**Headline regulatory exposure.** FINRA Rule 3110 (registered-person HR), FINRA Rule 4511 (records), SOX 302/404 (payroll/financial close), Reg P / GLBA 501(b) (customer files), state breach notification statutes.

**CSA conversation flow.** *"Pattern 3 is the pattern where the FSI Zone most often diverges from the CAPE Tier. The conversation question is 'what does the service touch?' If it's facilities tickets and conference-room booking, you're in Zone 2 and the controls are straightforward. If it's payroll, trade-settlement support, or customer files, you're in Zone 3 with [2.8 SoD](../controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md), [2.1 Managed Environments](../controls/pillar-2-management/2.1-managed-environments.md), [2.3 Change Management](../controls/pillar-2-management/2.3-change-management-and-release-planning.md), [3.1 Agent Inventory](../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md), and [3.4 Incident Reporting](../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) all attaching."*

**Cross-links to surface.** [Pattern 3 deep-dive](microsoft-cape-crosswalk.md#pattern-3-workplace-it-services). [Driver 2 — Business Strategy](../framework/agentic-capability-drivers.md#driver-2-business-strategy).

### 5.4 Pattern 4 — Core Business Process Transformation

**FSI use cases.** KYC / Customer Due Diligence (intake, identity verification, sanctions screening, beneficial-ownership analysis, ongoing CDD refresh). Insurance and lending claims processing (first-notice-of-loss intake, document classification, fraud-signal triage, adjuster routing, payment authorization). Financial close (accruals, reconciliations, journal-entry generation, variance investigation, sub-ledger consolidation). Order-to-cash and procure-to-pay (invoice extraction, three-way match, exception routing, payment release). Regulatory reporting (data aggregation, schedule preparation, narrative generation, attestation routing).

**Zone fit.** **Zone 3 mandatory.** Pattern 4 cannot deploy below Zone 3 in FSI. The Zone 3 prerequisites — Governance Committee approval, Managed Environments, comprehensive testing, full audit retention, business continuity plan — are non-negotiable and predate any Pattern 4 work.

**Headline regulatory exposure.** OCC Bulletin 2011-12 / Federal Reserve SR 26-2 (model risk for any decisioning model in the flow), SOX 302/404 (financial close ICFR), BSA/AML 31 CFR 1020.220 + OFAC (KYC/CDD), Reg B / ECOA 12 CFR 1002.9 (fair lending principal-reasons for adverse action), FINRA Rule 3110 (supervision), FINRA Rule 4511 / SEC 17a-3 and 17a-4 / CFTC Rule 1.31 (books and records).

**CSA conversation flow.** *"Pattern 4 is the highest-stakes pattern for FSI and the one most likely to draw the OCC, FINRA, or Fed examiner first. The CAPE phrasing — 'agents make routine decisions autonomously and escalate exceptions to humans' — lands directly on §V of OCC 2011-12 (ongoing monitoring, outcomes analysis, change control). The framework's posture is that every Pattern 4 decision must be reproducible from logged inputs, the model version, and the prompt. Mandatory controls are [2.6 Model Risk](../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md), [2.11 Bias Testing](../controls/pillar-2-management/2.11-bias-testing-and-fairness-assessment.md), [2.12 Supervision](../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md), plus the full Zone 3 baseline and the [Pattern 4 deep-dive control list](microsoft-cape-crosswalk.md#pattern-4-core-business-process-transformation-deep-dive). The CAPE scale-breaker is Business Strategy L500 — the customer must redesign the underlying process around the agent rather than bolting the agent onto today's process."*

**Cross-links to surface.** [Pattern 4 deep-dive](microsoft-cape-crosswalk.md#pattern-4-core-business-process-transformation-deep-dive). [Control 2.6](../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md). [CCO Quick Reference Q3 (model risk)](cco-quick-reference.md#q3-model-risk-where-is-your-model-inventory-and-the-validation-report-for-this-ai-agent).

### 5.5 Pattern 5 — External Engagement *(LANDMINE pattern — longest treatment)*

This is the pattern most likely to put a CSA in a difficult conversation. CAPE positions it as *"agents engage customers, partners, and ecosystems directly,"* with the framing that *"one bad customer interaction is a brand crisis."* That framing dramatically understates the FSI exposure. In US financial services, every customer-facing agent interaction is *simultaneously*: a communication subject to FINRA Rule 2210 (if a broker-dealer); a recommendation subject to Reg BI's care, conflict, and disclosure obligations (if recommending securities or accounts); a credit-related communication subject to ECOA / Reg B (if discussing credit terms); an electronic-fund-transfer communication subject to Reg E error-resolution obligations (if discussing EFTs); a privacy event subject to GLBA 501(b) (any PII path); and increasingly a state-AI-disclosure event under California SB 1001 / SB 243, Utah SB 149, and the Colorado AI Act. The exposure stack is wider than any other pattern and the failure surface is examiner-visible.

**FSI use cases.** Customer servicing agents (account inquiries, transaction lookups, statement explanations). Advisory support agents that surface educational content (must not give individualized investment advice without principal pre-approval). Claims intake agents (insurance, deposit dispute) that capture but do not adjudicate. Loan or account-opening intake agents that collect application data but do not make credit decisions. The framing discipline is *"intake, not decision; advisory, not recommendation; servicing, not advice."*

**Zone fit.** **Zone 3 mandatory.** Pattern 5 cannot deploy below Zone 3 in FSI. CAPE's Org & Culture L200 target maturity for this pattern is, in FSI terms, *insufficient* — supervisor culture and training must reach the *Defined / 300* equivalent before Pattern 5 enters production, regardless of CAPE's pattern-specific target.

**Headline regulatory exposure.** FINRA Rule 2210 (retail communications and principal pre-approval), FINRA Rule 3110 (supervision; Notice 24-09 technology-neutral), Reg BI (15 USC 80b-3a; care, disclosure, conflict, compliance obligations), ECOA / Reg B (fair lending; principal-reasons for adverse action), Reg E (EFT error resolution disclosure), GLBA 501(b) (safeguards), CFPB UDAAP, state AI disclosure laws, state breach notification statutes.

**CSA conversation flow.** *"Before we talk implementation, we need to lock the autonomy cap. Pattern 5 in FSI means: the agent may answer factual questions about the customer's existing account, surface educational content, and route to a human. The agent may NOT recommend securities, recommend accounts, give individualized investment advice, make credit decisions, or resolve a Reg E error dispute without a designated human supervisor recording approval per [Control 2.12](../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md). With that cap in place, the mandatory control set is [1.19 eDiscovery for Agent Interactions](../controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md), [2.11 Bias Testing](../controls/pillar-2-management/2.11-bias-testing-and-fairness-assessment.md), [2.12 Supervision](../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md), [2.19 Customer Disclosure](../controls/pillar-2-management/2.19-customer-ai-disclosure-and-transparency.md), [2.21 Marketing Claims Substantiation](../controls/pillar-2-management/2.21-ai-marketing-claims-and-substantiation.md), [2.23 Consent Enforcement](../controls/pillar-2-management/2.23-user-consent-and-ai-disclosure-enforcement.md), [2.26 Entra Agent ID](../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md), [4.4 SharePoint Agent Deployment](../controls/pillar-4-sharepoint/4.4-guest-and-external-user-access-controls.md), plus [1.27 Content Moderation](../controls/pillar-1-security/1.27-ai-agent-content-moderation-enforcement.md) for runtime protection."*

**The CAPE phrase to reframe in customer materials.** *"One bad customer interaction is a brand crisis"* → *"A non-compliant customer-facing interaction is a UDAAP, FINRA Rule 2210, or Reg BI exposure event."* The brand-crisis framing is true but inadequate; the regulatory framing is what the CCO needs.

**Cross-links to surface.** [Pattern 5 deep-dive](microsoft-cape-crosswalk.md#pattern-5-external-engagement-deep-dive). [CCO Quick Reference Q4 (FINRA 2210)](cco-quick-reference.md#q4-communications-with-the-public-show-me-the-principal-pre-approval-and-finra-2210-filing-for-the-retail-communication-this-agent-generated). [CCO Quick Reference Q5 (GLBA 501(b))](cco-quick-reference.md#q5-privacy-and-data-protection-show-me-the-glba-501b-safeguards-for-this-agents-data-access-and-the-annual-privacy-notice-provided-to-the-customer). [CCO Quick Reference Q6 (ECOA / Reg B)](cco-quick-reference.md#q6-anti-discrimination-and-fair-lending-show-me-the-bias-testing-results-stratified-by-protected-class-for-the-past-four-quarters-of-this-agents-outputs).

### 5.6 Pattern 6 — AI-First Capabilities

**FSI use cases (where Pattern 6 is appropriate without regulator pre-approval).** Internal continuous-optimization engines (e.g., trading-cost analysis, internal capacity planning) where the output informs a human decision. Predictive planning agents for liquidity forecasting where the output is a recommendation to Treasury. Multi-agent research orchestration where each component agent is individually inventoried and individually supervisable. Internal anomaly-detection multi-agent systems whose outputs feed into existing AML/fraud workflows under the supervision of [Control 2.12](../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md).

**Zone fit.** **Zone 3 mandatory** with the autonomy guardrail below.

!!! warning "Pattern 6 D3 guardrail (verbatim from `transformation-patterns.md`)"
    Fully autonomous customer-impacting Pattern 6 deployments are not currently supported in Zone 3 without documented regulator pre-approval.

**Headline regulatory exposure.** OCC Bulletin 2011-12 / Fed SR 26-2 (model risk — presumed high-risk tier), FINRA Rule 3110 (supervision; multi-agent attribution), FINRA Rule 4511 / SEC 17a-3 and 17a-4 / CFTC 1.31 (books and records — agent-to-agent messages), Reg B / ECOA 12 CFR 1002.9 (principal-reasons for adverse action), SOX 302/404 (where the system affects financial reporting), NYDFS Cybersecurity Regulation 23 NYCRR 500 (where in scope).

**CSA conversation flow — and why most FSI customers should NOT pursue Pattern 6 in production today.** Most FSI customers should pursue Pattern 4 with multi-agent design intent, not Pattern 6. The CAPE descriptors for Pattern 6 — *"sense-decide-act autonomous loops,"* *"continuous learning loops,"* *"agents that design and optimize their own processes"* — are each a textbook OCC 2011-12 high-risk model description with the additional regulatory complication that "learning from outcomes" implies in-production drift outside change management. No major US regulator has yet blessed this deployment shape with precedent. The framework's posture is that customers wishing to deploy outside the D3 guardrail should engage their primary regulator(s) directly and document the engagement before relying on FSI-AgentGov as an attestation framework.

**The redirect to Pattern 4 with multi-agent design intent.** *"Most of what you describe as Pattern 6 is achievable as Pattern 4 with multi-agent orchestration design intent. Each agent in the chain is individually inventoried under [Control 3.1](../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md), individually supervisable under [Control 2.12](../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md), and bounded by [Control 2.17 Multi-Agent Orchestration Limits](../controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md). You get the orchestration capability without the regulatory novelty. If you genuinely need Pattern 6's continuous-learning shape — as opposed to its multi-agent shape — that's a regulator conversation, not a vendor conversation."*

**Mandatory controls for permitted Pattern 6 shapes.** [2.17 Multi-Agent Orchestration Limits](../controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md), [2.20 Adversarial Testing](../controls/pillar-2-management/2.20-adversarial-testing-and-red-team-framework.md), [3.9 Agent Utilization & ROI Reporting](../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md), [3.14 Observability SDK](../controls/pillar-3-reporting/3.14-agent-365-observability-sdk.md), plus [2.6 Model Risk](../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md) at the high-risk tier.

**Cross-links to surface.** [Pattern 6 deep-dive](microsoft-cape-crosswalk.md#pattern-6-ai-first-capabilities-deep-dive). [Pattern 6 in transformation-patterns.md](../framework/transformation-patterns.md#pattern-6-ai-first-capabilities). [CCO Quick Reference Q11 (frontier patterns)](cco-quick-reference.md#q11-frontier-patterns-your-cio-has-told-us-the-firm-is-moving-toward-cape-pattern-5-and-pattern-6-deployments-what-is-your-governance-posture).

---

## Section 6 — The 5 capability drivers as a diagnostic conversation tool

The five Capability Drivers — **AI Strategy & Experience**, **Business Strategy**, **AI Governance & Security**, **Technology & Data**, **Organization & Culture** — are not a scorecard. CAPE deliberately builds them as a diagnostic for finding the *scale-breaker* — the single dimension that will block agent program scale regardless of how much the customer invests in the others. That diagnostic insight is the highest-value piece of CAPE for an FSI conversation, and the FSI-AgentGov [Capability Drivers narrative](../framework/agentic-capability-drivers.md) extends it with FSI-anchored maturity descriptors and per-pattern target profiles.

The use of the drivers as a conversation tool follows three steps. **First, get the customer to score their five drivers.** The Frontier Readiness assessment is the structured way to do this — 25 questions, facilitator-led, 15–30 minutes, scored on the Microsoft 100–500 scale. In a less formal meeting, ask the customer to score each driver on a 1–5 scale (no need to invoke the 100–500 scale live). The scoring is reflective; customers nearly always know their own weak driver if they think about it for 30 seconds.

**Second, identify the scale-breaker — the lowest-scored driver — and name what it blocks.** This is where the [per-pattern target profiles in `agentic-capability-drivers.md`](../framework/agentic-capability-drivers.md#per-pattern-target-profiles) become load-bearing. The table records, for each Frontier Transformation Pattern, the FSI-AgentGov reference target for each driver, with the CAPE scale-breaker per pattern marked with a star. A customer at L300 on AI Governance & Security cannot scale Pattern 5 to production in Zone 3 — the [identity isolation, customer disclosure, and reasoning capture](../framework/agentic-capability-drivers.md#driver-3-ai-governance-security) requirements are not met. A customer at L300 on Organization & Culture cannot scale Pattern 1 across the front office — the supervisor training and acceptable-use enforcement under FINRA Rule 3110 are not in place. Naming what the scale-breaker blocks turns an abstract maturity score into a sequencing decision.

**Third, recommend an investment plan that moves the scale-breaker driver before the pattern launches.** The [scale-breaker analysis in `agentic-capability-drivers.md`](../framework/agentic-capability-drivers.md#scale-breaker-analysis) names three FSI-defensible responses, in order of preference: (1) defer the pattern until the driver matures; (2) invest in the driver before the pattern; (3) deploy the pattern at lower scale (e.g., a pilot with named users) while the driver matures in parallel. The FSI-defensible *anti-pattern* is to declare the scale-breaker "fixed" by a steering-committee artifact that does not change the underlying maturity. Examiners will look at the operating evidence, not the planning deck.

**The link from drivers to controls.** Every control in the FSI-AgentGov manifest carries an `applicable_drivers` tag. When you run the [Both assessment](#43-both-as-the-comprehensive-program-assessment), the [`capability-driver-rollup.json`](https://github.com/judeper/FSI-AgentGov/blob/main/assessment/README.md#output-files) artifact cross-references control maturity by driver, answering *"which control gaps are blocking which drivers?"* This makes the scale-breaker conversation operational — the CDAO can see exactly which controls to invest in to move the scale-breaker forward, and the CIO can see exactly which configurations the M365 admin team needs to ship to deliver the driver uplift.

The diagnostic discipline matters more than the specific number on the maturity scale. A customer who answers honestly that their AI Governance & Security driver is *"barely there, we have a policy doc but no operating cadence"* is more useful to work with than a customer who self-scores L500 because their CISO has a strong reputation. The Frontier Readiness facilitator notes ([`assessment/manifest/frontier-readiness.json`](https://github.com/judeper/FSI-AgentGov/blob/main/assessment/manifest/frontier-readiness.json)) include question-level prompts that nudge the customer toward honest self-assessment; lean on them when the scoring feels generous.

---

## Section 7 — CoE structure conversations

### 7.1 Centralized vs Hybrid vs Federated — when each applies in FSI

CAPE describes three CoE shapes: **Centralized** (a single CoE team owns all four functions and serves the whole institution), **Hybrid** (Govern and Enable stay central; Optimize and Scale federate to the business lines), and **Federated** (only Govern remains centrally accountable; Build and Deploy federate fully). The framework's [`agentic-coe.md`](../framework/agentic-coe.md#the-three-coe-shapes) doc maps each shape to FSI institution archetypes and is the canonical reference. Three rules of thumb for the CSA conversation:

- **Default to Centralized for most FSI institutions.** Centralized is the right starting shape for specialized broker-dealers, community banks, regional banks with one or two business lines, and mid-tier asset managers. It produces consistent regulatory artifacts and avoids early federation mistakes. The major exception is when the institution already has high operating-model maturity (mature model risk function, standing technology change committees, established audit-evidence pipelines) and runs three or more business lines pursuing agent work simultaneously — in that case, Hybrid is workable.

- **Hybrid is the right shape for institutions running 4+ patterns across 3+ business lines** where central control consistency matters for regulatory artifacts but business-line proximity matters for prioritization and operational signal interpretation. Regional banks with multiple business lines and mid-tier asset managers are typical fits. The discipline is that Govern and Enable stay central — the central function owns the disclosure language, the supervisor RACI, and the maker-community standards — while Optimize and Scale federate to business-line operational ownership.

- **Federated is reserved for global SIFIs and large diversified financial-holding companies** where each business line is large enough to staff its own CoE chapter and where centralizing all four functions would create unworkable bottlenecks across hundreds of agents. Federated is the shape where the federation guardrail (see [§7.4](#74-decision-rights-as-the-bottleneck-buster) and [Section 3.3](#33-can-my-business-unit-run-its-own-coe-cape-supports-federation)) does the most work. Federated also requires disproportionately strong Pillar 3 reporting infrastructure — without it, the central Govern function loses visibility into business-line activity and cannot satisfy its supervisory accountability.

### 7.2 The 3 generic anti-patterns and their FSI symptoms

CAPE names three generic CoE anti-patterns that translate cleanly to FSI. Each is one of the most common failure modes in the field.

- **The Gatekeeper.** Govern reviews everything and becomes the bottleneck. Lead times balloon, business lines stand up shadow agents in personal environments to bypass the queue, and the framework's controls become a brake instead of an enabler. *FSI fix:* Govern owns release-gate enforcement on Zone 2 and Zone 3 only, with documented criteria, named approvers, and a written-justification exception process with CRO sign-off. Zone 1 agents move on the maker's authority. The exception process is the safety valve. (See [`agentic-coe.md` Anti-pattern 2](../framework/agentic-coe.md#anti-pattern-2-coe-govern-function-configured-as-advisory-rather-than-as-a-release-gate).)

- **The Ghost.** A CoE charter is signed, the four functions are named on paper, the operating rhythm is defined — and then the rhythm never materializes. The weekly standup is cancelled three times in a row, the monthly scorecard is produced once and forgotten. The charter satisfies an audit finding but the operating engine never starts. *FSI fix:* treat the CoE rhythm as a Pillar 1 audit-logged activity. Meeting attendance, decisions, and action items belong in a Control 1.7 audit-logged location (a controlled SharePoint site, a Dataverse table, or equivalent). Missed cadence shows up in audit evidence and triggers escalation. (See [`agentic-coe.md` Anti-pattern 6 — Ghost CoE charter](../framework/agentic-coe.md#anti-pattern-6-ghost-coe-charter).)

- **The Perfectionist.** "We can't deploy any agent until we have full FINRA Rule 3110 supervision workflows, OCC 2011-12 model validation, examiner-ready evidence trails, bias testing automation, customer disclosure governance, and a board-approved acceptable-use policy." Result: 18-month planning cycles, zero agents in production, and a maker community that gives up. *FSI fix:* ship Zone 1 agents with Baseline controls now, learn from the operating signal, scale to Zone 2 with Recommended controls, then graduate to Zone 3 with Regulated controls. Adaptive governance is examiner-defensible; analysis paralysis is not.

### 7.3 The 6 FSI-specific anti-patterns from `agentic-coe.md`

Beyond the three generic anti-patterns, [`agentic-coe.md`](../framework/agentic-coe.md#fsi-specific-coe-anti-patterns) names six FSI-specific anti-patterns. The CSA should be able to recognize each in the field.

1. **Federated maker enablement without federated audit reporting.** Business lines stand up their own builders and ship agents into production; the central CoE learns about deployments after the fact. *Fix:* make agent registration in the central Pillar 3 inventory a release-gate prerequisite. ([Anti-pattern 1](../framework/agentic-coe.md#anti-pattern-1-federated-maker-enablement-without-federated-audit-reporting).)
2. **CoE Govern function configured as advisory rather than as a release gate.** Govern issues recommendations; the business line decides whether to deploy. Controls become aspirational. *Fix:* Govern owns release-gate enforcement with named approvers and an exception process. ([Anti-pattern 2](../framework/agentic-coe.md#anti-pattern-2-coe-govern-function-configured-as-advisory-rather-than-as-a-release-gate).)
3. **Treating the CoE as an IT function rather than a cross-functional governance function.** The CoE reports up through the CIO; Compliance, Risk, and Internal Audit participate as consulted parties at best. *Fix:* the CoE is chaired by the AI Governance Lead (not by an IT function), with the CCO and CRO in standing membership. ([Anti-pattern 3](../framework/agentic-coe.md#anti-pattern-3-treating-the-coe-as-an-it-function-rather-than-a-cross-functional-governance-function).)
4. **Skipping the Retire stage.** Agents are deployed, run for years, and accumulate. Retired agents are not formally decommissioned; their data, audit logs, and connector permissions linger. *Fix:* build the Retire stage into the operating rhythm; quarterly Optimize flags retirement candidates; Govern owns the retirement decision and records-retention disposition. ([Anti-pattern 4](../framework/agentic-coe.md#anti-pattern-4-skipping-the-retire-stage).)
5. **Federation read as relief from supervision.** A business line interprets its CoE chapter as a transfer of supervisory accountability — *"we run our own AI now, so the central CCO doesn't need to attest."* *Fix:* document the federation guardrail explicitly in the CoE charter and in each business-line CoE chapter charter. ([Anti-pattern 5](../framework/agentic-coe.md#anti-pattern-5-federation-read-as-relief-from-supervision).)
6. **Ghost CoE charter.** The charter satisfies an audit finding but the operating engine never starts. *Fix:* treat the rhythm as a Pillar 1 audit-logged activity; missed cadence triggers escalation. ([Anti-pattern 6](../framework/agentic-coe.md#anti-pattern-6-ghost-coe-charter).)

### 7.4 Decision rights as the bottleneck-buster

The cleanest framing of the CoE conversation comes from CAPE itself: *"Centralize HOW scale works, delegate WHO builds."* Translated to FSI: the central Govern function owns release gates, security policies, autonomy limits, disclosure language, supervisor RACI, and audit retention; the business line owns use-case prioritization, knowledge curation within approved categories, design within architecture standards, and day-to-day operations post-approval.

This split is what prevents the Gatekeeper anti-pattern. If Legal reviews *everything*, you are the Gatekeeper. If Legal reviews autonomy limits and disclosure language only (centralized) while the business owner decides knowledge sources within approved categories (delegated), you have decision rights. The framework's [Operating Model](../framework/operating-model.md) carries the canonical RACI by zone, and the [Role Catalog](role-catalog.md) names the roles that hold each decision right.

For a federated customer, decision rights also enforce the federation guardrail. The named central principals — AI Governance Lead, Chief Compliance Officer, Chief Risk Officer, CISO — retain accountability for the regulated supervisory functions regardless of CoE shape. Federated execution; central regulatory record. Document this explicitly in the CoE charter and in each business-line CoE chapter charter; do not leave it implicit. The Anti-pattern 5 fix in [`agentic-coe.md`](../framework/agentic-coe.md#anti-pattern-5-federation-read-as-relief-from-supervision) makes this explicit.

---

## Section 8 — Microsoft alignment is intentional. Here is the brand boundary.

The framework's Microsoft alignment is a deliberate design decision. The reasoning is field-grounded: most US FSI firms are Microsoft shops; CAPE is the strategic vocabulary their account teams are already teaching them; aligning with that vocabulary reduces customer cognitive overhead and increases the probability that the framework gets adopted into the customer's existing governance program. Strong Microsoft alignment is a *net positive* for FSI-AgentGov adoption in the Microsoft FSI customer base. The framework adopts CAPE patterns, drivers, and CoE functions as its strategic vocabulary by design — see the [Microsoft CAPE Crosswalk](microsoft-cape-crosswalk.md) for the line-by-line alignment, the [transformation-patterns.md](../framework/transformation-patterns.md) framework summary, and the [agentic-capability-drivers.md](../framework/agentic-capability-drivers.md) and [agentic-coe.md](../framework/agentic-coe.md) framework docs for the full FSI treatment of each.

**The brand boundary is that alignment is not endorsement.** FSI-AgentGov is open-source, community-maintained, and is **NOT a Microsoft product**. Microsoft does not endorse, support, or warrant it. Microsoft can co-promote — and the framework's existence is a useful artifact for Microsoft FSI conversations because it lets a CSA bring a credible regulator-grade overlay to a customer who has already digested CAPE. But Microsoft does not certify or attest to the framework's contents.

**The CSA's discipline.** A CSA may *recommend* FSI-AgentGov to a customer ("this is the framework I take into customer meetings — it's the FSI extension to CAPE that I find most useful"). A CSA may *not* represent FSI-AgentGov as a Microsoft offering ("Microsoft recommends FSI-AgentGov" or "Microsoft has approved FSI-AgentGov as the FSI control framework" are both inaccurate and should not appear in customer materials, slide decks, or written follow-ups). The repository [Disclaimer](../disclaimer.md) is the authoritative statement and should be linked in any customer-facing materials that reference the framework.

**Non-Microsoft customers.** Customers running primarily on AWS Bedrock or Vertex AI need to extend or substitute large parts of the framework. The 78 controls are configurations of M365 / Power Platform / Purview / Sentinel / SharePoint surfaces specifically. The pattern, driver, and CoE vocabulary translates portably (because CAPE is industry-agnostic), but the implementation specifics do not. A customer running on AWS should be referred to AWS's equivalent governance content (the AWS Well-Architected ML lens and the AWS responsible-AI guidance); FSI-AgentGov can serve as conceptual inspiration but should not be presented as the implementation framework. The framework is opinionated toward M365 and the opinion is not portable.

**The trade-off the CSA should be honest about.** The framework's M365 bias is a strength for the Microsoft FSI customer base and a limitation everywhere else. CSAs should not over-position FSI-AgentGov to AWS- or GCP-anchored customers; the framework is unlikely to be the right fit for them. This honesty preserves the framework's credibility with the customers who *are* the right fit.

---

## Section 9 — Field caveats and known gaps

The framework is opinionated, ships frequently, and is honest about what it does not yet do. The following gaps should be named in the customer conversation rather than glossed over.

- **Bias toward M365 / Copilot Studio / Power Platform / Purview / Sentinel / SharePoint.** Customers running primarily on AWS Bedrock or Vertex AI need to extend or substitute. The pattern, driver, and CoE vocabulary is portable; the 78-control implementation is not. See [Section 8](#section-8-microsoft-alignment-is-intentional-here-is-the-brand-boundary) for the brand-boundary discussion.

- **Frontier Readiness diagnostic is facilitator-answered (no auto-evaluators in v1).** It is a structured self-assessment, not auditor-grade evidence. The honest coverage report at [`docs/reference/frontier-assessment-coverage.md`](frontier-assessment-coverage.md) names this as 0% auto coverage. Lead with the limitation when introducing the assessment.

- **The 78-control catalog is opinionated for US FSI regulation** (FINRA, SEC, OCC, Federal Reserve, GLBA, CFTC, CFPB, ECOA, Reg E, BSA/AML, NYDFS Part 500). Non-US customers need supplementary content for their regulators (BaFin, FCA, OSFI, ASIC, MAS, EU AI Act, etc.). The framework does not currently carry crosswalks for non-US regulatory regimes. Customers in those jurisdictions can adapt the control set conceptually but need to author the regulatory mappings themselves.

- **Pattern 6 is not currently safely deployable in regulated FSI** without explicit regulator pre-approval. The framework's D3 guardrail — *"Fully autonomous customer-impacting Pattern 6 deployments are not currently supported in Zone 3 without documented regulator pre-approval"* — reflects this. Customers wishing to deploy outside the guardrail should engage their primary regulator(s) directly and document the engagement before relying on FSI-AgentGov as an attestation framework.

- **The framework does NOT cover** end-user AI literacy curricula, prompt engineering training, agent UX/UI design, vendor selection beyond the M365 ecosystem, or industry-specific business process design. Those are scope-out by design; the framework is governance content, not enablement curriculum.

- **Some controls are manual-only.** The honest coverage report at [`docs/reference/assessment-coverage.md`](assessment-coverage.md) names exactly which controls are auto-evaluated, which are manual-only, and which are awaiting evaluator implementation. Do not promise customers a fully-automated assessment; the framework's discipline is to name the coverage gaps explicitly.

- **The framework ships frequently.** v1.5.0 is the Microsoft CAPE Alignment Release; future minor versions will add controls, refine zone thresholds, and deepen the assessment evaluator coverage. Customers should subscribe to releases (the [Versioning and Support](versioning-and-support.md) reference describes the cadence and the SBOM / Sigstore attestation chain attached to release tags).

- **Sovereign-cloud parity is uneven and now quantified.** For FSI tenants in **GCC, GCC High, DoD IL5, or 21Vianet** — including public-sector-adjacent broker-dealers, federal-advisory RIAs, and FFIEC-regulated entities with US-Gov subsidiaries — capability parity with commercial varies materially. Roughly 36% of the 78-control catalog has a documented sovereign-cloud caveat (Insider Risk Adaptive Protection, Entra Agent ID, Agent 365 Admin Center, several DSPM-for-AI surfaces, Power Platform Usage insights, Anthropic Claude in M365 Copilot, and others). The new [Sovereign Cloud Parity Matrix](sovereign-cloud-parity-matrix.md) aggregates the per-control caveats into a single scannable view so CSAs can answer the *"will this work in our Government cloud tenant?"* question without re-deriving it per opportunity. Use it as the reference data when handling the sovereign-cloud objection in Section 3 and when scoping public-sector-adjacent FSI conversations.

---

## Related documents

- [CSA Quick Reference](csa-quick-reference.md) — in-meeting lookup.
- [CCO Quick Reference](cco-quick-reference.md) — examiner-facing companion organized by examiner question.
- [Microsoft CAPE Crosswalk](microsoft-cape-crosswalk.md) — pattern × control deep-dives, Regulatory Exposure callouts, and the FSI Maturity Translation Table.
- [Transformation Patterns](../framework/transformation-patterns.md) — 6-pattern framework summary including the Pattern 6 D3 guardrail.
- [Agentic Capability Drivers](../framework/agentic-capability-drivers.md) — 5-driver framework summary, scale-breaker concept, and per-pattern target profiles.
- [Agentic Center of Excellence](../framework/agentic-coe.md) — CoE structure, federation guardrail, and the 6 FSI-specific anti-patterns.
- [Zones and Tiers](../framework/zones-and-tiers.md) — Zone 1 / 2 / 3 definitions and per-zone control thresholds.
- [Operating Model](../framework/operating-model.md) — RACI, governance committee, and canonical role assignments.
- [Frontier Readiness Coverage](frontier-assessment-coverage.md) — honest 0% auto coverage report for the Frontier diagnostic.
- [Assessment Coverage](assessment-coverage.md) — honest auto / manual / unimplemented coverage report for the 78-control assessment.
- [CAPE Pattern Coverage matrix](pattern-coverage.md) — generated 78×6 control-to-pattern matrix.
- [NIST AI RMF Crosswalk](nist-ai-rmf-crosswalk.md) — complementary GOVERN / MAP / MEASURE / MANAGE alignment.
- [Regulatory Mappings](regulatory-mappings.md) — regulation-to-control reference (FINRA, SEC, OCC, Federal Reserve, GLBA, ECOA, Reg E, CFTC, NYDFS).
- [Role Catalog](role-catalog.md) — canonical short role names with Microsoft CAPE role mapping cross-reference.
- [Glossary](glossary.md) — canonical definitions for autonomy cap, scale-breaker, federation guardrail, and other framework terms.
- [Assessment README](https://github.com/judeper/FSI-AgentGov/blob/main/assessment/README.md) — when to run Controls vs Frontier vs Both.
- [Versioning and Support](versioning-and-support.md) — release cadence, SBOM, and Sigstore attestation chain.
- [Disclaimer](../disclaimer.md) — repository-level disclaimer and brand-boundary statement.

---

*FSI Agent Governance Framework v1.5.0 — Microsoft CAPE Alignment Release | Updated: May 2026 | UI Verification Status: Current*
