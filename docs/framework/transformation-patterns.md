# Frontier Transformation Patterns

!!! info "Audience"
    Primary: AI Governance Lead, CIO/CDO, AI Program Sponsor, FSI architect engaging with Microsoft FSI Customer Success Architects (CSAs).
    M365 admins implementing controls — you can safely skip this page and start with the [Adoption Roadmap](adoption-roadmap.md) or the [Control Catalog](../controls/index.md). Patterns name *what shape* an agent deployment takes; zones name *what regulatory exposure* it carries. Admin work is driven by zones and controls.

> **Position:** Pattern is a first-class FSI-AgentGov framework concept (parallel to Zones, Pillars, and Capability Drivers). This page is the **lean upstream summary**. The deep-dive — Regulatory Exposure callouts, mandatory FSI-AgentGov controls, autonomy caps, examiner red flags, and CAPE-language reframings per pattern — lives in the [Microsoft CAPE × FSI-AgentGov Crosswalk](../reference/microsoft-cape-crosswalk.md).

---

## Why patterns matter for FSI governance

Microsoft's Copilot Acceleration Engineering (CAPE) materials describe six **Frontier Transformation Patterns** — recurring deployment shapes that organizations adopt when scaling agentic AI. The patterns are framed as *design choices, not stages*: most organizations run two or three concurrently, each with a distinct user, data flow, and decision boundary (Source: Microsoft CAPE *Agentic Transformation Patterns Playbook*, pp. 4–6; *CAPE Walking Deck*, slides 4–14, paraphrased).

FSI-AgentGov adopts "Pattern" as a first-class framework concept for three reasons:

1. **Shared vocabulary with Microsoft conversations.** When a CSA, partner, or executive sponsor opens a discussion with "we want to deploy Pattern 5 in Q3," the FSI governance program needs to recognize the term, place it in the framework, and translate it into FSI zones and controls without re-litigating the vocabulary.
2. **Pattern-aware governance defaults.** Each pattern has a typical deployment shape — who the agent talks to, what data it touches, and how much decision authority it holds. Those defaults determine the **default FSI Zone**, the headline **regulatory exposure profile**, and the **subset of FSI controls that "light up"** for a given initiative. Naming the pattern up front shortens the path from intent to control list.
3. **Loose, attribution-clean alignment.** Pattern is a *descriptive* classification of a deployment shape. It does **not** change the underlying 78-control framework, override the [zone classification authority](zones-and-tiers.md), or relieve the firm of any regulatory obligation. Where CAPE language and FSI requirements diverge, FSI requirements govern; the [crosswalk](../reference/microsoft-cape-crosswalk.md) documents each reframing.

Patterns are an *additive lens*, not a replacement for the existing zones, pillars, or controls. An admin who never uses the word "pattern" can still implement the framework correctly; a governance lead who needs to map a CIO conversation onto controls benefits from the explicit mapping below.

---

## Pattern × Zone summary

| # | Pattern | Default FSI Zone | Regulatory exposure (headline) | Deep dive |
|---|---|---|---|---|
| 1 | **Employee AI Enablement** | Zone 1 (promote to Zone 2 on share, Zone 3 on regulated content) | Limited at Zone 1; supervision and disclosure obligations attach as soon as output reaches a customer. | [Pattern 1 deep dive](../reference/microsoft-cape-crosswalk.md#pattern-1-employee-ai-enablement) |
| 2 | **Business Expert Empowerment** | Zone 2 (Zone 3 when SME domain is regulated) | SME-domain dependent: low for non-regulated knowledge, full books-and-records and supervision exposure when the SME content is compliance, model risk, or supervisory. | [Pattern 2 deep dive](../reference/microsoft-cape-crosswalk.md#pattern-2-business-expert-empowerment) |
| 3 | **Workplace & IT Services** | Zone 2 (Zone 3 when service touches PII, payroll, trade settlement, or customer files) | Low for purely internal services; SOX 404, FINRA 4511/3110, GLBA, and Reg P engage when the service crosses into regulated workflow. | [Pattern 3 deep dive](../reference/microsoft-cape-crosswalk.md#pattern-3-workplace-it-services) |
| 4 | **Core Business Process Transformation** | **Zone 3 (mandatory)** | High and multi-regime: OCC Bulletin 2026-13 (formerly OCC 2011-12) / Fed SR 26-2 model risk, SOX 302/404, BSA/AML, Reg B/ECOA, FINRA 3110/4511, SEC 17a-3/4, CFTC 1.31. | [Pattern 4 deep dive](../reference/microsoft-cape-crosswalk.md#pattern-4-core-business-process-transformation-deep-dive) |
| 5 | **External Engagement** | **Zone 3 (mandatory)** | Customer-facing: FINRA 2210 communications with the public, Reg BI, ECOA/Reg B, Reg E, GLBA 501(b), state AI disclosure statutes. | [Pattern 5 deep dive](../reference/microsoft-cape-crosswalk.md#pattern-5-external-engagement-deep-dive) |
| 6 | **AI-First Capabilities** | **Zone 3 (mandatory) — with autonomy guardrail** | Highest residual risk: OCC Bulletin 2026-13 / Fed SR 26-2 model risk for novel decisioning; Fed SR 26-2 (formerly SR 11-7) validation thresholds for any consumer-impacting output. | [Pattern 6 deep dive](../reference/microsoft-cape-crosswalk.md#pattern-6-ai-first-capabilities-deep-dive) |

For the full Pattern × Zone fit matrix (which zones are *typical*, *permitted with caveats*, or *not appropriate* for each pattern), see the [Pattern × Zone fit matrix](../reference/microsoft-cape-crosswalk.md#3-pattern-zone-fit-matrix) in the crosswalk.

---

## Pattern overviews

The following overviews state the Microsoft framing (paraphrased), the typical FSI deployment shape, the default FSI Zone, and the headline regulatory exposure. Each overview ends with a link to the full crosswalk entry, which carries the mandatory FSI-AgentGov controls, autonomy caps, examiner red flags, and CAPE language to reframe.

### Pattern 1 — Employee AI Enablement

**Microsoft framing.** Personal productivity and drafting assistance — research, summarization, scheduling, and individual workflow automation — where the human retains decision authority (paraphrased from CAPE *Patterns Playbook* pp. 7–8).

**Typical FSI shape.** The default entry point for Microsoft 365 Copilot and personal Microsoft Copilot Studio agents inside the firm. Common examples: drafting client communications before supervisor review, summarizing meeting notes, structuring research briefs, organizing calendar and inbox, generating internal memos. The human authors and is accountable for any output that reaches an external party.

**Default FSI Zone.** Zone 1 by default; Zone 2 as soon as the output is shared into a team channel or used in a customer workflow; Zone 3 when regulated content is generated.

**Regulatory exposure (headline).** Limited at Zone 1. The exposure surfaces when individual output becomes a customer communication (FINRA Rule 2210) or when supervision evidence is required (FINRA Rule 3110, GLBA 501(b) safeguards for any PII handled).

**For full mapping** — including mandatory controls, autonomy cap, and examiner red flags — see [Pattern 1 in the crosswalk](../reference/microsoft-cape-crosswalk.md#pattern-1-employee-ai-enablement).

### Pattern 2 — Business Expert Empowerment

**Microsoft framing.** Knowledge agents that scale the judgment of a small number of subject-matter experts across a wider audience (paraphrased from CAPE *Patterns Playbook* pp. 9–10).

**Typical FSI shape.** Knowledge agents grounded on the firm's policies, procedures, or reference data. Common examples: a compliance Q&A agent over the firm's WSP, a policy-interpretation assistant for branch managers, a model-documentation lookup for analysts, a supervisory-procedures helper for principals. The named SME — not the agent — owns each answer relied upon for a regulatory or supervisory decision.

**Default FSI Zone.** Zone 2 for non-regulated SME content; Zone 3 the moment the SME domain is regulated (compliance, supervision, model risk, fair lending, suitability).

**Regulatory exposure (headline).** SME-domain dependent. Low when the knowledge base is non-regulated; full FINRA 3110/4511 supervision-and-records exposure (and SEC 17a-4 retention) when the agent is answering regulated questions. Books-and-records exposure attaches because the Q&A trail itself becomes a record.

**For full mapping** — see [Pattern 2 in the crosswalk](../reference/microsoft-cape-crosswalk.md#pattern-2-business-expert-empowerment).

### Pattern 3 — Workplace & IT Services

**Microsoft framing.** Internal services (HR helpdesk, IT support, facilities) where agents operate end-to-end with human escalation (paraphrased from CAPE *Patterns Playbook* pp. 11–12).

**Typical FSI shape.** Internal-service agents resolving routine requests within documented routing rules. Common examples: facilities ticket triage, IT password-reset assistance, HR benefits Q&A, equipment-request workflow. Pattern 3 is straightforward when the service is purely internal and non-regulated; it changes character as soon as it touches a regulated workflow.

**Default FSI Zone.** Zone 2 for non-regulated internal services; Zone 3 when the service touches payroll (SOX 404 ICFR), trade settlement support (FINRA 4511 books and records), HR records of registered persons (FINRA 3110 supervision), or customer files (Reg P, GLBA).

**Regulatory exposure (headline).** Low for purely internal services; SOX 302/404, FINRA 4511/3110, GLBA 501(b), and Reg P engage when the service crosses into financial close, supervision, customer-data, or payroll workflow. CAPE's industry-agnostic Tier 2 default understates the FSI exposure for those crossover cases.

**For full mapping** — see [Pattern 3 in the crosswalk](../reference/microsoft-cape-crosswalk.md#pattern-3-workplace-it-services).

### Pattern 4 — Core Business Process Transformation

**Microsoft framing.** Agents woven into business-critical end-to-end flows. The CAPE *Patterns Playbook* explicitly cites claims processing (p. 16) and references invoice, supply-chain, and compliance workflows in the *Walking Deck* (slide 13, paraphrased).

**Typical FSI shape.** The highest-stakes deployment shape in US financial services. Candidate flows include Know-Your-Customer (KYC) and ongoing customer due diligence; insurance and lending claims processing (intake, document classification, fraud-signal triage, adjuster routing, payment authorization); financial close (accruals, reconciliations, journal-entry generation, sub-ledger consolidation); order-to-cash and procure-to-pay; and regulatory reporting (data aggregation, schedule preparation, narrative drafting). Each candidate flow independently triggers a different US regulatory regime.

**Default FSI Zone.** **Zone 3 — mandatory.** Pattern 4 cannot deploy below Zone 3 in FSI. The Zone 3 prerequisites in [Zones and Tiers](zones-and-tiers.md) — Governance Committee approval, Managed Environments, comprehensive testing, full audit retention, business continuity plan — are non-negotiable and predate any Pattern 4 work.

**Regulatory exposure (headline).** High and multi-regime. Decisioning models trigger OCC Bulletin 2026-13 (formerly OCC 2011-12) and Fed SR 26-2 (formerly SR 11-7) model risk requirements; KYC/CDD flows trigger BSA/AML 31 CFR 1020.220 and OFAC sanctions screening; outcomes that influence credit trigger Reg B/ECOA fair-lending principal-reasons obligations; financial-close flows trigger SOX 302/404 ICFR; supervision is governed by FINRA Rule 3110; and every decision is a record under FINRA 4511, SEC 17a-3/4, and CFTC 1.31.

**For full mapping** — including the mandatory FSI-AgentGov controls, the autonomy cap (decisions must be reproducible from logged inputs, model version, prompt, and retrieved sources), examiner pre-empts, and CAPE phrases to reframe — see [Pattern 4 in the crosswalk](../reference/microsoft-cape-crosswalk.md#pattern-4-core-business-process-transformation-deep-dive).

### Pattern 5 — External Engagement

**Microsoft framing.** Customer- and partner-facing agents handling servicing, advisory support, intake, and engagement (paraphrased from CAPE *Patterns Playbook* pp. 19–22).

**Typical FSI shape.** Agents that interact directly with end customers, prospects, or external partners. Common examples: a customer-servicing chat agent on the firm's website, an account-opening intake agent that captures customer information for a registered representative to review, a self-service insurance-claims FNOL (first notice of loss) agent, a partner-portal support agent for introducing brokers. Every customer-visible utterance is a "communication with the public" under FINRA Rule 2210 and may trigger Reg BI care obligations, Reg E disclosure requirements, ECOA/Reg B for any credit-touching interaction, and state AI-disclosure statutes (e.g., Colorado AI Act, NYC AEDT) where applicable.

**Default FSI Zone.** **Zone 3 — mandatory.** External-facing agents do not deploy in Zone 1 or Zone 2 in FSI. The CAPE scale-breaker for this pattern (*Governance & Security at Level 500* — identity isolation and disclosure) maps directly to FSI's identity, disclosure, and supervision controls.

**Regulatory exposure (headline).** Customer-facing: FINRA Rule 2210 (communications with the public — including pre-use principal approval and recordkeeping), Reg BI (care obligation, conflict-of-interest disclosure), ECOA/Reg B and FHA (fair lending in any credit-adjacent interaction), Reg E (electronic-funds disclosures), GLBA 501(b) for safeguarding of customer information, and state AI-disclosure statutes that increasingly require explicit notice that the customer is interacting with an AI. Customer-facing autonomy is the highest single source of examination and litigation exposure in the framework.

**For full mapping** — including mandatory FSI-AgentGov controls, the autonomy cap (no agent action that creates a regulated obligation to the customer without a human in the loop), and the AI-disclosure requirements — see [Pattern 5 in the crosswalk](../reference/microsoft-cape-crosswalk.md#pattern-5-external-engagement-deep-dive).

### Pattern 6 — AI-First Capabilities

**Microsoft framing.** Net-new capabilities that did not exist before and are only possible with agentic AI — continuous optimization, predictive planning, multi-agent orchestration of novel workflows (paraphrased from CAPE *Patterns Playbook* pp. 23–24).

**Typical FSI shape.** Capabilities that have no pre-AI analogue inside the firm. Candidate examples (illustrative, not endorsed): continuous portfolio-rebalancing recommendation engines, multi-agent workflows that orchestrate research analysts and trade-execution agents, predictive operational-resilience capabilities. By definition these capabilities are novel — there is no established control baseline, no examiner precedent, no peer comparison, and (often) no existing model risk inventory entry. That novelty itself is the risk.

**Default FSI Zone.** **Zone 3 — mandatory** with the autonomy guardrail below. Internal-only sandbox capabilities with no production decision rights may live in Zone 2 only as proofs of concept; production deployment is Zone 3 only.

**Regulatory exposure (headline).** Highest residual risk in the framework. Any consumer-impacting output triggers OCC Bulletin 2026-13 (formerly OCC 2011-12) and Fed SR 26-2 (formerly SR 11-7) model risk validation; multi-agent chains create cascading model-risk and accountability concerns that current regulator guidance does not yet address with precedent.

!!! warning "Pattern 6 autonomy guardrail (FSI-AgentGov)"
    Fully autonomous customer-impacting Pattern 6 deployments are not currently supported in Zone 3 without documented regulator pre-approval.

**For full mapping** — including mandatory FSI-AgentGov controls (Pattern 6 ties to controls 2.6, 2.17, 2.20, 3.14 and the full Zone 3 baseline), the autonomy cap, and the CAPE phrases that must be reframed before they reach any Pattern 6 documentation — see [Pattern 6 in the crosswalk](../reference/microsoft-cape-crosswalk.md#pattern-6-ai-first-capabilities-deep-dive).

---

## How patterns interact with zones, pillars, drivers, and controls

A single agent deployment carries five distinct FSI-AgentGov classifications. They answer different questions and must not be conflated:

| Concept | Question it answers | How many per deployment |
|---|---|---|
| **Pattern** | What *shape* does this deployment take? Who does the agent talk to and what does it do? | One primary pattern; some deployments span two patterns at the seam (e.g., Pattern 1 → Pattern 5 when employee drafts become customer communications). |
| **Zone** | What *regulatory exposure* does this deployment carry? | Exactly one zone per agent at any point in time. See [Zones and Tiers](zones-and-tiers.md). |
| **Pillar** | Which FSI control *family* does a given control live in? | Four pillars (Security, Management, Reporting, SharePoint) cover all 78 controls. A single deployment is governed by controls drawn from all four. |
| **Capability Driver** | What *organizational readiness dimension* must mature to scale this pattern? | Five drivers (AI Strategy & Experience, Business Strategy, AI Governance & Security, Technology & Data, Organization & Culture). See [Capability Drivers](agentic-capability-drivers.md). |
| **Controls** | What *actionable governance units* must be implemented? | Variable: a Pattern 1 / Zone 1 deployment may engage ~10 controls; a Pattern 4 / Zone 3 deployment engages most of the 78. |

The diagnostic insight from Microsoft's CAPE materials — that the *weakest* Capability Driver is the scaling ceiling regardless of how strong the others are — applies to FSI but does not change the framework's per-control compliance posture. A firm may be capable of executing Pattern 4 organizationally yet still be required to implement the Pattern 4 mandatory controls before deployment. Capability maturity describes *capacity*; controls describe *obligation*.

A note on operating model: when a CoE federates Pattern 4 or Pattern 5 work across business-unit teams, the operational federation does **not** transfer the regulated supervisory accountability that FINRA 3110, OCC Bulletin 2026-13, or Fed SR 26-2 places on the firm. See [Agentic Center of Excellence](agentic-coe.md) for the FSI federation guardrails.

---

## How to choose a pattern when classifying a new initiative

Pattern selection is a brief intake question, not a flowchart. Four questions answer it for the great majority of initiatives:

1. **Who or what is the agent talking to?** If the audience is the employee themselves (drafting, summarizing, personal workflow), the initiative is **Pattern 1**. If the audience is an external customer, prospect, partner, or counterparty — for any meaningful interaction — the initiative is **Pattern 5**, regardless of the underlying technology stack. Customer-facing reclassification is the single most common mis-scoping in early FSI deployments.

2. **Is the work the agent is doing a *new capability* or *an existing process being reshaped*?** New capabilities that did not exist before AI go to **Pattern 6**. Existing processes go to one of Patterns 2, 3, or 4 depending on what kind of process it is.

3. **For an existing process — is it a regulated business-critical flow?** KYC, claims, financial close, regulatory reporting, lending decisioning, suitability, and equivalent flows are **Pattern 4** (Zone 3 mandatory). Internal services that do not cross those flows are **Pattern 3**. Knowledge-and-judgment scaling (compliance Q&A, policy interpretation) is **Pattern 2**.

4. **When in doubt, pick the more conservative (higher-numbered) pattern and review with risk and compliance.** The cost of starting with stricter controls and relaxing on review is small; the cost of under-classifying a customer-facing or core-business-process deployment and discovering the gap during an examination is large. The crosswalk's [Pattern × Zone fit matrix](../reference/microsoft-cape-crosswalk.md#3-pattern-zone-fit-matrix) is the reference for edge cases — multi-pattern deployments, internal-to-external transitions, and proofs of concept that may scale.

---

## See also

- [Microsoft CAPE × FSI-AgentGov Crosswalk](../reference/microsoft-cape-crosswalk.md) — deep-dive with Regulatory Exposure callouts, mandatory FSI controls, autonomy caps, examiner red flags, and CAPE language to reframe per pattern.
- [Capability Drivers](agentic-capability-drivers.md) — the five organizational readiness dimensions used to diagnose the scale-breaker for a given pattern.
- [Agentic Center of Excellence](agentic-coe.md) — CoE blueprint (Govern / Enable / Optimize / Scale) for governing pattern deployments at scale, with the FSI federation guardrails.
- [Zones and Tiers](zones-and-tiers.md) — the FSI zone classification system that determines control depth for any chosen pattern.
- [Regulatory Framework](regulatory-framework.md) — full FSI regulatory mapping (FINRA, SEC, OCC, Fed, GLBA, SOX, CFTC, BSA/AML).
- [Control Catalog](../controls/index.md) — the 78 controls across four pillars.

---

*Updated: May-2026 | Version: v1.6.2 | Audience: M365 admins, AI governance leads, FSI architects*
