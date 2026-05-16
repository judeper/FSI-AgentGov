# Agentic Capability Drivers

> **Audience:** M365 administrators, AI Governance Lead, AI Program Sponsor / CIO / CDAO, FSI architects, Microsoft FSI Customer Success Architects (CSAs).
> **Purpose:** FSI translation of Microsoft's five **Capability Drivers** and the 100–500 maturity scale, with per-driver target profiles by Frontier Transformation Pattern and an explicit position on why FSI-AgentGov does not numerically merge maturity scales.
> **Position:** This document is the framework-layer deep-dive that the [Microsoft CAPE crosswalk](../reference/microsoft-cape-crosswalk.md) §1.2 redirects to. It supplements — it does not replace — the FSI assessment engine, the per-control governance levels, or the Zone classification.

---

## Why drivers matter for FSI governance

Microsoft's Copilot Acceleration Engineering (CAPE) materials introduce **Capability Drivers** as the five organizational dimensions whose collective maturity determines an enterprise's capacity to deploy AI agents at scale. The drivers are AI Strategy & Experience, Business Strategy, AI Governance & Security, Technology & Data, and Organization & Culture. Each is scored on a 100–500 maturity scale (Initial → Repeatable → Defined → Capable → Optimized). Microsoft positions the model as a **diagnostic for finding the weakest link**, not a scorecard to maximize: the weakest driver becomes the ceiling on how far any Frontier Transformation Pattern can scale (Source: *Patterns Playbook*, pp. 25–34; *Walking Deck*, slides 7–8).

FSI-AgentGov adopts Capability Drivers as a first-class framework concept because the 78-control catalog answers a different question. Controls describe *what to implement and how to verify it*; drivers describe *whether the organization is capable of implementing and operating it*. A US financial-services firm can pass every Pillar 1 security control on the FSI assessment engine and still be incapable of scaling a Pattern 4 Core Business Process deployment because its Business Strategy driver is at L200 (no documented agent-supported process redesign, no named outcomes, no KPI ownership). The driver lens surfaces that gap before the deployment fails an examination.

The vocabulary discipline is load-bearing. **Drivers are not Pillars.** *Pillar* in FSI-AgentGov refers to the four control families — Security (29), Management (26), Reporting (14), SharePoint (9) — and is reserved exclusively for them. *Capability Driver* (or simply *Driver*) refers to Microsoft's five organizational readiness dimensions and is reserved exclusively for them. CAPE source materials occasionally use "pillar" for the five dimensions in slide titles; FSI-AgentGov canonicalizes to "Capability Driver" and treats the alternative as non-canonical (see the *Capability Driver* entry in the [Glossary](../reference/glossary.md) and [`scripts/verify_language_rules.py`](https://github.com/judeper/FSI-AgentGov/blob/main/scripts/verify_language_rules.py) for enforcement scope).

The framework promise is layered: **Drivers + the scale-breaker concept** give organizations a strategic readiness lens to plan transformation; **78 controls** give the actionable governance posture; **6 Frontier Transformation Patterns** give the deployment-shape lens; **3 Zones** give the regulatory classification. Each lens answers a different question. This document explains the driver lens; the [Microsoft CAPE crosswalk](../reference/microsoft-cape-crosswalk.md), [Zones and Tiers](zones-and-tiers.md), and [transformation-patterns.md](transformation-patterns.md) explain the others.

---

## The five Capability Drivers

| Driver | FSI translation | Primary owner |
|---|---|---|
| **AI Strategy & Experience** | AI portfolio governance — how the firm decides what to build, sponsor, and sunset. | AI Program Sponsor (CIO / CDAO) with [AI Governance Lead](../reference/role-catalog.md#governance-roles-non-admin) accountable. |
| **Business Strategy** | Business value alignment — how AI investments are tied to named outcomes, KPIs, and accountable business owners. | Executive Sponsor (CEO/COO) with line-of-business [Business Owners](../reference/role-catalog.md#governance-roles-non-admin) accountable per use case. |
| **AI Governance & Security** | Risk management and control posture — how the firm maintains examiner-defensible governance over the agent estate. | Joint: [Chief Risk Officer](../reference/role-catalog.md), [Chief Compliance Officer](../reference/role-catalog.md), [CISO](../reference/role-catalog.md). |
| **Technology & Data** | Platform and data engineering — environments, identity, telemetry, RAG corpus integrity, observability. | Power Platform Admin and platform engineering teams, accountable to the CTO ([role catalog](../reference/role-catalog.md)). |
| **Organization & Culture** | Workforce enablement and change — supervisor training, maker community, AI-positive but compliance-aware culture. | [AI Governance Lead](../reference/role-catalog.md#governance-roles-non-admin) partnered with HR / Change Management; supervisor accountability per FINRA Rule 3110. |

The sections that follow translate each driver into FSI vocabulary, rewrite the L100–L500 progression in language that does not become Exhibit A in an examination, and list the FSI-AgentGov controls most closely associated with the driver.

---

### Driver 1 — AI Strategy & Experience

**Microsoft framing.** CAPE positions this driver as the deliberate planning, investment, and evolution of AI across the enterprise — moving from ad-hoc pilots to a managed portfolio with executive sponsorship and a coherent experience strategy (Source: *Patterns Playbook*, pp. 28–29; *Walking Deck*, slide 7).

**FSI translation.** AI Strategy & Experience asks *who decides what gets built, who sponsors it, how it integrates with the firm's enterprise architecture, and how the portfolio is rationalized over time.* In FSI, the driver also carries an unspoken regulatory thread: agent investments that bypass the Architecture Review Board, the Model Risk Management committee, or the AI Governance Lead are precisely the agents that will appear in an exam without documentation. A high-maturity FSI organization on this driver has a published AI portfolio, named executive sponsors per pattern, and a documented sunset process for agents that fail to demonstrate value.

**Owner.** AI Program Sponsor (CIO or CDAO) with the [AI Governance Lead](../reference/role-catalog.md#governance-roles-non-admin) accountable for portfolio rationalization. The FSI Architecture Review Board reviews material strategy changes.

**Maturity profile (FSI-translated).**

| Level | FSI indicator |
|---|---|
| **L100 — Initial** | Ad-hoc experimentation by individual makers; no published AI strategy; no portfolio view; investments not tied to a named sponsor or business outcome. |
| **L200 — Repeatable** | Recurring patterns of agent investment within a single business unit; informal sponsor relationships; some agents documented in an inventory but no enterprise portfolio rationalization. |
| **L300 — Defined** | Published enterprise AI strategy reviewed by the Governance Committee; named executive sponsors per pattern; portfolio-level inventory aligned with [Control 3.1](../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md); documented sunset criteria. |
| **L400 — Capable** | Strategy refresh cadence aligned to the [governance cadence](governance-cadence.md); board-level reporting on the agent portfolio; vendor selections supported by [Control 2.7](../controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md) and the AI Governance Lead; budget allocation tracked under [Control 3.5](../controls/pillar-3-reporting/3.5-cost-allocation-and-budget-tracking.md). |
| **L500 — Optimized** | Enterprise-wide AI portfolio with quarterly outcome attestation by named sponsors; agents added or sunset based on documented, audit-trail-ready criteria; experience design discipline applied to internal and external surfaces under change-managed release processes. |

**Common scale-breakers.** AI Strategy & Experience becomes the ceiling when:

- Organizations attempt **Pattern 1 — Employee AI Enablement** at enterprise scale without a portfolio view (the firm cannot answer "who owns Copilot adoption across business lines?").
- Organizations attempt **Pattern 6 — AI-First Capabilities** without an executive-sponsored hypothesis for net-new value (agents become "demos in search of a sponsor").

**Related FSI controls.**

- [3.1 Agent Inventory and Metadata Management](../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md)
- [3.5 Cost Allocation and Budget Tracking](../controls/pillar-3-reporting/3.5-cost-allocation-and-budget-tracking.md)
- [2.7 Vendor and Third-Party Risk Management](../controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md)
- [2.13 Documentation and Record Keeping](../controls/pillar-2-management/2.13-documentation-and-record-keeping.md)
- [3.6 Orphaned Agent Detection and Remediation](../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md)

---

### Driver 2 — Business Strategy

**Microsoft framing.** CAPE positions this driver as the depth of AI integration into business processes and outcome measurement — moving from technology pilots toward redesigned processes with named owners, success metrics, and measurable returns (Source: *Patterns Playbook*, pp. 29–30; *Walking Deck*, slide 7).

**FSI translation.** Business Strategy asks *which processes have been deliberately redesigned around agents, who owns the business outcome, and how value is measured.* In FSI, the driver is regulator-relevant in a specific way: when an agent participates in a regulated process (KYC, claims adjudication, supervisory Q&A, regulatory reporting), the firm must be able to name the process owner, show the redesign artifacts, and produce the KPI evidence that supports the decision to deploy. A weak Business Strategy driver in an FSI shop typically presents as "we have lots of agents but cannot point to a redesigned process or a documented business owner" — which is the same evidence gap an OCC or FINRA examiner will surface.

**Owner.** Executive Sponsor (CEO / COO) accountable to the board; [Business Owner](../reference/role-catalog.md#governance-roles-non-admin) per use case; AI Governance Lead facilitates process-redesign documentation.

**Maturity profile (FSI-translated).**

| Level | FSI indicator |
|---|---|
| **L100 — Initial** | Agents deployed inside existing processes with no redesign; no business KPIs; no named business owner. |
| **L200 — Repeatable** | A small set of agent use cases tied to informal outcome targets within a single business line; success measured anecdotally. |
| **L300 — Defined** | Formal process redesign documentation for production agents; named business owners per use case under the [operating model](operating-model.md); agent KPIs reviewed in the [governance cadence](governance-cadence.md); usage analytics captured per [Control 3.2](../controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md). |
| **L400 — Capable** | End-to-end internal services (Pattern 3) redesigned with documented decision boundaries, escalation rules, and SLAs; performance monitored under [Control 2.9](../controls/pillar-2-management/2.9-agent-performance-monitoring-and-optimization.md); cost attribution under [Control 3.5](../controls/pillar-3-reporting/3.5-cost-allocation-and-budget-tracking.md). |
| **L500 — Optimized** | Core business processes (KYC, claims, financial close, regulatory reporting) operate under formally redesigned agent-supported workflows with version-controlled decision rules, named human supervisors per [Control 2.12](../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md), and documented attestation that material change to the process triggers governance review. |

**Common scale-breakers.** Business Strategy becomes the ceiling when:

- Organizations attempt **Pattern 3 — Workplace & IT Services** at enterprise scale without end-to-end service redesign (the agent gets stuck in process gaps the redesign should have closed).
- Organizations attempt **Pattern 4 — Core Business Process Transformation** without formal process owner attestation (no examiner-defensible answer to "who owns this redesigned process?").

**Related FSI controls.**

- [2.9 Agent Performance Monitoring and Optimization](../controls/pillar-2-management/2.9-agent-performance-monitoring-and-optimization.md)
- [2.13 Documentation and Record Keeping](../controls/pillar-2-management/2.13-documentation-and-record-keeping.md)
- [3.2 Usage Analytics and Activity Monitoring](../controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md)
- [2.12 Supervision and Oversight (FINRA Rule 3110)](../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md)
- [2.5 Testing, Validation, and Quality Assurance](../controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md)

---

### Driver 3 — AI Governance & Security

**Microsoft framing.** CAPE positions this driver as risk management, compliance, monitoring, and responsible-AI practices — moving from informal guardrails toward proactive, integrated risk practices across the agent lifecycle (Source: *Patterns Playbook*, pp. 30–31; *Walking Deck*, slide 7).

**FSI translation.** This is the driver where FSI organizations are typically strongest at the L100–L300 range and where the FSI-AgentGov 78-control catalog provides the most direct lift. The driver asks *whether risk classification is enforced by the platform (not by policy memos), whether audit trails reach the immutable retention thresholds the firm's regulators require, whether model risk is governed under OCC Bulletin 2026-13 (formerly OCC 2011-12) / Fed SR 26-2, whether supervision under FINRA Rule 3110 is discharged by named registered persons, and whether bias and fair-lending exposure under Reg B / ECOA is tested before consumer-impacting deployment.* The L500 frontier in FSI is not "self-governing systems" — it is *predictive governance with human-in-the-loop change control and reasoning capture sufficient for examiner reconstruction* (see the [FSI Maturity Translation Table](../reference/microsoft-cape-crosswalk.md#fsi-maturity-translation-table) for the canonical reframing).

**Owner.** Joint accountability: [Chief Risk Officer](../reference/role-catalog.md), [Chief Compliance Officer](../reference/role-catalog.md), [CISO](../reference/role-catalog.md). The [AI Governance Lead](../reference/role-catalog.md#governance-roles-non-admin) operates the day-to-day program. Federation of CoE roles to business units does **not** transfer this accountability (see [agentic-coe.md](agentic-coe.md) federation guardrail).

**Maturity profile (FSI-translated).**

| Level | FSI indicator |
|---|---|
| **L100 — Initial** | Informal guardrails; no enforced platform classification; audit logs not retained to FINRA 4511 / SEC 17a-4 thresholds; no documented model risk inventory. |
| **L200 — Repeatable** | Some platform controls applied to Zone 3 (DLP, audit logging) but inconsistently; a written AI policy exists but is not platform-enforced; basic supervision evidence is collected manually. |
| **L300 — Defined** | Zone-classified [Managed Environments](../controls/pillar-2-management/2.1-managed-environments.md) with [Environment Groups](../controls/pillar-2-management/2.2-environment-groups-and-tier-classification.md); [comprehensive audit logging](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) at the FINRA 4511 / SEC 17a-4 retention threshold; [supervision under FINRA Rule 3110](../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) with named principals; [model risk tiering](../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md) per OCC Bulletin 2026-13. |
| **L400 — Capable** | Cross-functional risk practices integrated across the lifecycle; [Sentinel detection content](../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md) operational; [adversarial testing program](../controls/pillar-2-management/2.20-adversarial-testing-and-red-team-framework.md); [bias and fairness assessment](../controls/pillar-2-management/2.11-bias-testing-and-fairness-assessment.md) before consumer-impacting deployment; [exception and override management](../controls/pillar-3-reporting/3.12-agent-governance-exception-and-override-management.md) with reason capture. |
| **L500 — Optimized** | Predictive governance: monitoring telemetry triggers proactive review; [hallucination feedback](../controls/pillar-3-reporting/3.10-hallucination-feedback-loop.md) drives change-managed retraining gated by independent validation; [conflict-of-interest testing](../controls/pillar-2-management/2.18-automated-conflict-of-interest-testing.md) and [Reg B principal-reasons capture](../controls/pillar-2-management/2.11-bias-testing-and-fairness-assessment.md) automated; the agent recommends and the named supervisor approves and is accountable. |

> **Reframing notice.** CAPE's L500 descriptor for this driver uses language ("predictive, self-optimising operations") that is a regulatory landmine in FSI. The reframing above ("predictive governance with human-in-the-loop change control") is canonical and is enforced repo-wide for `docs/framework/**`, `docs/controls/**`, and `docs/reference/cape-*.md`. The verbatim CAPE descriptor and the full reframing rationale live in the [FSI Maturity Translation Table](../reference/microsoft-cape-crosswalk.md#fsi-maturity-translation-table).

**Common scale-breakers.** AI Governance & Security becomes the ceiling when:

- Organizations attempt **Pattern 5 — External Engagement** without identity isolation, customer disclosure, and reasoning capture sufficient for Reg BI and ECOA defense (CAPE marks this driver L500 as the Pattern 5 scale-breaker).
- Organizations attempt **Pattern 6 — AI-First Capabilities** with multi-agent chains where individual agents lack inventory entries, change-management coverage, or reasoning capture — i.e., the firm cannot reconstruct who decided what.

**Related FSI controls.**

- [1.7 Comprehensive Audit Logging and Compliance](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md)
- [2.6 Model Risk Management (OCC Bulletin 2026-13 / Fed SR 26-2)](../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md)
- [2.12 Supervision and Oversight (FINRA Rule 3110)](../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md)
- [3.3 Compliance and Regulatory Reporting](../controls/pillar-3-reporting/3.3-compliance-and-regulatory-reporting.md)
- [3.9 Microsoft Sentinel Integration](../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md)

---

### Driver 4 — Technology & Data

**Microsoft framing.** CAPE positions this driver as platform maturity, architecture, data quality, and telemetry — moving from fragmented tooling toward an integrated platform with high-quality grounding data, observability, and reuse (Source: *Patterns Playbook*, pp. 31–32; *Walking Deck*, slide 7).

**FSI translation.** Technology & Data is the driver most often confused with the FSI-AgentGov **Pillar 4 (SharePoint)** because both touch grounding data; the lens is broader. Technology & Data covers *the entire platform substrate* — Power Platform environment hygiene, identity (Entra Agent ID), telemetry pipelines (Sentinel, Agent 365 Observability SDK), RAG corpus integrity, and SharePoint as a knowledge source. In FSI the driver is regulator-relevant because *the data the agent retrieves is the record* — a stale or oversharing-exposed RAG corpus is a FINRA 4511 / SEC 17a-4 record-integrity issue, not just a quality issue. A high-maturity FSI shop on this driver runs Managed Environments with documented tier classification, version-controlled RAG corpora, item-level permission scanning of knowledge sources, and observability sufficient for incident reconstruction.

**Owner.** Power Platform Admin and platform engineering teams, accountable to the CTO ([role catalog](../reference/role-catalog.md)). The AI Governance Lead and CCO consume telemetry; they do not own the platform.

**Maturity profile (FSI-translated).**

| Level | FSI indicator |
|---|---|
| **L100 — Initial** | No managed environments; default tenant used for production agents; no RAG corpus governance; observability limited to Microsoft 365 admin reports. |
| **L200 — Repeatable** | Some [Managed Environments](../controls/pillar-2-management/2.1-managed-environments.md) for high-risk workloads; ad-hoc RAG corpora; basic Power Platform analytics; no SharePoint-as-knowledge-source hardening. |
| **L300 — Defined** | [Environment Groups and Tier Classification](../controls/pillar-2-management/2.2-environment-groups-and-tier-classification.md) operational; [RAG source integrity validation](../controls/pillar-2-management/2.16-rag-source-integrity-validation.md) for production agents; [Grounding Scope Governance](../controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md) applied to SharePoint sources; [item-level permission scanning](../controls/pillar-4-sharepoint/4.8-item-level-permission-scanning-agent-knowledge-sources.md) at deployment. |
| **L400 — Capable** | Integrated platform telemetry: [Sentinel content](../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md), [Agent 365 Observability SDK](../controls/pillar-3-reporting/3.14-agent-365-observability-sdk.md), [Copilot Hub](../controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md); reusable agent templates and patterns curated by the CoE; identity managed under [Entra Agent ID](../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md). |
| **L500 — Optimized** | Continuously monitored, version-controlled platform where multi-agent orchestration is governed by documented architecture, [orchestration limits](../controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md) are enforced, retraining is gated by independent validation, and grounding data integrity is verified on every release under change management. |

**Common scale-breakers.** Technology & Data becomes the ceiling when:

- Organizations attempt **Pattern 2 — Business Expert Empowerment** with low-quality or stale knowledge sources (CAPE marks this driver L300 as the Pattern 2 scale-breaker; in FSI this also produces a books-and-records integrity problem).
- Organizations attempt **Pattern 6 — AI-First Capabilities** without orchestration architecture, multi-agent telemetry, or reusable patterns (CAPE marks this driver L500 as the Pattern 6 scale-breaker).

**Related FSI controls.**

- [2.1 Managed Environments](../controls/pillar-2-management/2.1-managed-environments.md)
- [2.16 RAG Source Integrity Validation](../controls/pillar-2-management/2.16-rag-source-integrity-validation.md)
- [4.6 Grounding Scope Governance](../controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md)
- [4.8 Item-Level Permission Scanning for Agent Knowledge Sources](../controls/pillar-4-sharepoint/4.8-item-level-permission-scanning-agent-knowledge-sources.md)
- [3.14 Agent 365 Observability SDK and Custom Agent Telemetry](../controls/pillar-3-reporting/3.14-agent-365-observability-sdk.md)

---

### Driver 5 — Organization & Culture

**Microsoft framing.** CAPE positions this driver as adoption enablement, skills, and AI-positive culture — moving from low awareness toward an enterprise where AI is part of how work gets done, with documented skills paths and a community of practice (Source: *Patterns Playbook*, pp. 32–33; *Walking Deck*, slide 7).

**FSI translation.** Organization & Culture is the driver where FSI organizations are typically *weakest* relative to Microsoft's industry-agnostic baseline, and where the framework's biggest blind spot lives if drivers are not surfaced separately from controls. The driver asks *whether supervisors are trained to discharge their FINRA 3110 obligations over agent-assisted work, whether the maker community has access to FSI-aware enablement (not just generic training), whether customer-facing communications culture under FINRA 2210 has been updated to address AI-generated content, and whether the firm has documented the difference between an "AI-enabled associated person" and an "associated person who used an AI tool."* In FSI the L500 frontier on this driver is not "AI-first culture" untranslated — it is *trained-supervisor culture with documented review obligations and continuous-improvement discipline within change control* (per the [FSI Maturity Translation Table](../reference/microsoft-cape-crosswalk.md#fsi-maturity-translation-table)).

**Owner.** [AI Governance Lead](../reference/role-catalog.md#governance-roles-non-admin) partnered with HR / Change Management. Supervisor training accountability sits with line management under FINRA 3110.

**Maturity profile (FSI-translated).**

| Level | FSI indicator |
|---|---|
| **L100 — Initial** | No documented AI training; no supervisor enablement program; AI use is reactive ("can I use Copilot for this?"); no maker community. |
| **L200 — Repeatable** | A general AI training module exists but is not differentiated by role or by FSI regulatory context; informal maker channels in Teams; no documented supervisor obligations for AI-assisted work. |
| **L300 — Defined** | Role-based [Training and Awareness Program](../controls/pillar-2-management/2.14-training-and-awareness-program.md) covering supervisors, makers, end users, and customer-facing personnel; [User Consent and AI Disclosure Enforcement](../controls/pillar-2-management/2.23-user-consent-and-ai-disclosure-enforcement.md) operational; [Communication Compliance Monitoring](../controls/pillar-1-security/1.10-communication-compliance-monitoring.md) updated for AI-generated content. |
| **L400 — Capable** | Curated maker community (federated CoE shape) with documented contribution paths; [Customer AI Disclosure](../controls/pillar-2-management/2.19-customer-ai-disclosure-and-transparency.md) and [AI Marketing Claims](../controls/pillar-2-management/2.21-ai-marketing-claims-and-substantiation.md) governance applied to all external surfaces; supervisor training records evidenced for examination. |
| **L500 — Optimized** | Trained-supervisor culture with documented per-decision review obligations; continuous-improvement discipline operationalized within change control; the firm can demonstrate to an examiner that the supervisor — not the agent — is accountable for any decision the agent supported. |

> **Reframing notice.** CAPE's L500 descriptor for this driver uses language ("AI-first culture, autonomous, self-improving") that, if adopted verbatim into supervisor or HR documentation, undermines the firm's FINRA 3110 supervision posture. The reframing above is canonical and matches the [FSI Maturity Translation Table](../reference/microsoft-cape-crosswalk.md#fsi-maturity-translation-table) entry for this driver.

**Common scale-breakers.** Organization & Culture becomes the ceiling when:

- Organizations attempt **Pattern 1 — Employee AI Enablement** at enterprise scale without supervisor training and acceptable-use enforcement (CAPE marks this driver L300 as the Pattern 1 scale-breaker; in FSI it doubles as a FINRA 3110 supervision gap).
- Organizations attempt **Pattern 5 — External Engagement** without trained customer-facing personnel who understand the firm's AI disclosure obligations under state AI laws and FINRA 2210.

**Related FSI controls.**

- [2.14 Training and Awareness Program](../controls/pillar-2-management/2.14-training-and-awareness-program.md)
- [2.23 User Consent and AI Disclosure Enforcement](../controls/pillar-2-management/2.23-user-consent-and-ai-disclosure-enforcement.md)
- [2.19 Customer AI Disclosure and Transparency](../controls/pillar-2-management/2.19-customer-ai-disclosure-and-transparency.md)
- [2.21 AI Marketing Claims and Substantiation](../controls/pillar-2-management/2.21-ai-marketing-claims-and-substantiation.md)
- [1.10 Communication Compliance Monitoring](../controls/pillar-1-security/1.10-communication-compliance-monitoring.md)

---

## Scale-breaker analysis

A **scale-breaker** is the single capability dimension that will block an organization's ability to scale its agent portfolio, regardless of strength on other dimensions (see the *Scale-breaker* entry in the [Glossary](../reference/glossary.md)). The concept is the load-bearing insight of Microsoft's diagnostic: investments in the strongest driver yield diminishing returns once the weakest driver becomes the binding constraint.

US financial-services organizations typically present **asymmetric driver profiles**. The pattern observed in customer engagements is a strong AI Governance & Security driver (often L300 or L400 at baseline because the firm has mature InfoSec, Risk, and Compliance functions that translate naturally into Pillar 1 and Pillar 2 control posture), a middling Technology & Data driver (often L200–L300 because environment hygiene and RAG corpus governance are newer disciplines), and weaker AI Strategy & Experience and Organization & Culture drivers (often L100–L200 because these require executive sponsorship and HR-aligned change programs that lag the technical buildout). Business Strategy is bimodal — strong where the firm has a named AI Program Sponsor with a published portfolio, weak where AI investment is delegated entirely to IT.

**How to identify your scale-breaker (qualitative diagnostic).** Until the FSI assessment engine adds a Frontier Readiness scorer (a Phase 3 deliverable referenced in the *Frontier Readiness* entry of the [Glossary](../reference/glossary.md)), use the following qualitative diagnostic. For each driver, answer the L300 indicator in the maturity table above with **yes** / **partial** / **no**. The driver with the most **no** answers is your candidate scale-breaker. Cross-check by asking: *if I were to attempt the most ambitious pattern in our roadmap tomorrow, which driver would fail first under examiner scrutiny?* The two answers usually converge.

**What to do when your scale-breaker blocks the pattern you want to deploy.** Three FSI-defensible responses, in order of preference:

1. **Reduce the pattern ambition.** A Pattern 4 deployment with a Business Strategy driver at L200 should de-scope to a Pattern 3 internal-services deployment until process redesign is documented. This is governance discipline, not capitulation.
2. **Invest in the scale-breaker driver before the pattern.** A Pattern 5 ambition with an AI Governance & Security driver at L300 should fund the L400 / L500 control buildout (Sentinel content, exception management, bias testing automation, customer disclosure governance) before launching customer-facing agents. The control buildout is documented in the controls listed in the relevant driver section above.
3. **Accept a smaller blast radius.** A Pattern 6 ambition with a Technology & Data driver at L300 should constrain the deployment to a single business unit with strict orchestration limits and human-in-the-loop gates ([Control 2.17](../controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md)) until the platform substrate matures.

The FSI-defensible *anti-pattern* is to declare the scale-breaker "fixed" by a steering-committee artifact that does not change the underlying maturity. Examiners will look at the operating evidence, not the planning deck.

---

## Per-pattern target profiles

The table below records FSI-AgentGov reference targets for each driver, by Frontier Transformation Pattern. The starred cell (`*`) in each row is the scale-breaker per CAPE — the driver that will block that pattern first if not at the indicated level. Cells without a star are the minimum maturity FSI-AgentGov recommends for examiner-defensible posture in the pattern's typical zone.

| # | Pattern | AI Strategy & Experience | Business Strategy | AI Governance & Security | Technology & Data | Organization & Culture |
|---|---|---|---|---|---|---|
| **1** | Employee AI Enablement | L200 | L200 | L300 | L200 | **L300\*** |
| **2** | Business Expert Empowerment | L200 | L300 | L300 | **L300\*** | L300 |
| **3** | Workplace & IT Services | L300 | **L400\*** | L400 | L300 | L300 |
| **4** | Core Business Process Transformation | L400 | **L500\*** | L400 | L400 | L400 |
| **5** | External Engagement | L400 | L400 | **L500\*** | L400 | L400 |
| **6** | AI-First Capabilities | L400 | L400 | L500 | **L500\*** | L400 |

> **Reading the table.** The starred cell records the scale-breaker per CAPE (Source: *Patterns Playbook*, pp. 7–24; *Walking Deck*, slides 9–14, *Key Insight* slide 8). Non-starred cells are FSI-AgentGov's minimum recommended levels — they reflect the maturity an experienced US FSI deployment needs in order to achieve examiner-defensible posture for the pattern in its typical zone (Zone 1/2 for Patterns 1–2, Zone 2/3 for Pattern 3, **Zone 3 mandatory** for Patterns 4–6 per the [Pattern × Zone fit matrix](../reference/microsoft-cape-crosswalk.md#3-pattern-zone-fit-matrix)).

**These targets are FSI-AgentGov reference profiles, not Microsoft mandates.** Microsoft's source materials specify only the scale-breaker per pattern; they do not specify a target maturity for the other four drivers. The non-starred cells above are derived from FSI regulatory exposure: e.g., Pattern 4 requires Technology & Data at L400 (not L300) because [model risk management under OCC Bulletin 2026-13](../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md) requires version-controlled platform telemetry sufficient for independent validation. Pattern 5 requires Organization & Culture at L400 because customer-facing personnel must be trained on AI disclosure obligations before externalization. Pattern 6 requires AI Governance & Security at L500 because multi-agent orchestration without reasoning capture is an examiner red flag (see crosswalk Pattern 6 deep-dive).

For organizations engaging Microsoft Customer Success Architects on Frontier Readiness assessments, present these targets together with the standard CAPE per-pattern profile so the conversation reflects both the industry-agnostic baseline and the FSI overlay.

---

## Why FSI-AgentGov does not mathematically merge maturity scales

FSI-AgentGov customers will encounter **three distinct maturity scales** in normal use of the framework. They each measure a different thing. They are deliberately **not** combined into a single number.

| Scale | Where it lives | What it measures |
|---|---|---|
| **Per-control governance levels** (Baseline / Recommended / Regulated) | Every control file in `docs/controls/pillar-*/` | The implementation depth of a single control, within control. |
| **Assessment engine maturity** (0–4) | `assessment/manifest/controls.json` and the prefilled assessment report | Aggregated control evidence vs zone thresholds, across the 78-control catalog. |
| **CAPE Capability Driver maturity** (100–500) | This document and the (Phase 3) Frontier Readiness parallel assessment | Strategic organizational readiness across the five drivers; diagnostic for finding the scale-breaker. |

The three scales answer different questions. The per-control 3-level scale answers *"how deeply have I implemented this single control?"* The assessment engine 0–4 scale answers *"across the 78-control catalog, how close am I to the zone threshold for each control?"* The CAPE 100–500 driver scale answers *"as an organization, how ready am I to scale a Frontier Pattern across the enterprise?"*

**Numerical merging produces false precision and obscures regulatory accountability.** A naive mapping (e.g., "Baseline = L200, Recommended = L300, Regulated = L400") would imply that implementing a control at Baseline level means the organization's AI Governance & Security driver is at L200. This is false. A Zone 3 agent can have all 78 controls at Regulated (4/4) while the firm's Business Strategy driver is at L100 (no documented outcomes, no KPIs, no business owner). A firm can be at L500 on the AI Governance & Security driver because it has predictive monitoring and reasoning capture, while a specific control like [4.8 (item-level permission scanning)](../controls/pillar-4-sharepoint/4.8-item-level-permission-scanning-agent-knowledge-sources.md) is only at Recommended because the organization has not yet rolled it out to all SharePoint sites. The two readings are both correct because they answer different questions.

**The FSI approach.** Read each scale on its own terms:

- **Use this document's per-pattern target profiles as the strategic alignment lens.** For board reporting, capability-investment planning, and Microsoft CSA conversations.
- **Use the assessment engine output as the operational lens.** For per-control remediation, examiner-facing evidence, and zone-threshold tracking.
- **Use the per-control 3-level scale as the implementation depth lens.** For the playbook step the platform team is working through this week.

For organizations engaging Microsoft on Frontier Readiness assessments, this document is the **translation layer** between Microsoft's industry-agnostic capability vocabulary and the FSI-AgentGov framework. Customers seeking a single "compliance score" should refer to the per-control assessment summary (0–4 maturity per control, plus the rollup), not to the CAPE driver scores.

This design decision is recorded in the council deliberation that produced v1.5.0 (Council Splits S3 and S7, dissent preserved). Mathematical merging of the three scales is explicitly out of scope for v1.5.0 and is not on the v2.0.0 roadmap.

---

## How drivers interact with zones, pillars, patterns, and controls

The five concepts in the FSI-AgentGov + CAPE vocabulary answer different questions and operate at different altitudes. Reading them together — rather than collapsing them into one — is what the framework's middle-layer architecture exists to support.

| Concept | Question it answers | Type of lens |
|---|---|---|
| **Capability Driver** ([glossary](../reference/glossary.md)) | Are we organizationally ready to scale this kind of work? | Organizational readiness dimension. |
| **[Zone](zones-and-tiers.md)** | What regulatory classification applies to this agent? | Regulatory classification (Zone 1 / 2 / 3). |
| **[Pillar](governance-fundamentals.md#four-governance-pillars)** | Which family of FSI controls does this work touch? | Control family (Security / Management / Reporting / SharePoint). |
| **Pattern** ([glossary](../reference/glossary.md)) | What deployment shape is this agent? | Deployment-shape lens (1 — Employee Enablement through 6 — AI-First). |
| **Control** | What specific governance work do I need to evidence? | Actionable governance unit (one of 78). |

**Concrete example.** An FSI organization at L300 on Organization & Culture attempts to deploy **Pattern 5 (External Engagement)** in **Zone 3** to a retail customer-servicing surface. The 78-control assessment passes — Pillar 1 (Security), Pillar 2 (Management), Pillar 3 (Reporting), Pillar 4 (SharePoint) controls are all at the Zone 3 thresholds. The deployment fails, six months in, because customer-facing personnel were not trained on AI disclosure obligations under state AI laws and FINRA 2210, and a state regulator opens an inquiry on a customer-misled allegation. The framework reads this as a *scale-breaker problem* — Organization & Culture at L300 was insufficient for Pattern 5's L400 minimum on this driver — *not a control problem*. The remedial action is not "add another control"; it is "invest in driver maturity" (specifically Controls [2.14](../controls/pillar-2-management/2.14-training-and-awareness-program.md), [2.19](../controls/pillar-2-management/2.19-customer-ai-disclosure-and-transparency.md), and [2.21](../controls/pillar-2-management/2.21-ai-marketing-claims-and-substantiation.md), implemented at the Regulated level for the customer-facing population).

This is the load-bearing reason FSI-AgentGov adopts Capability Driver as a first-class framework concept rather than treating CAPE as a citation-only crosswalk: the driver lens surfaces failure modes that the control-by-control assessment does not.

---

## See also

- [Frontier Transformation Patterns](transformation-patterns.md) — the six patterns this document maps drivers against (Phase 2 sibling).
- [Agentic Center of Excellence](agentic-coe.md) — operational structure that develops driver capacity over time (Phase 2 sibling).
- [Microsoft CAPE crosswalk](../reference/microsoft-cape-crosswalk.md) — pattern-by-pattern regulatory mapping, FSI Maturity Translation Table, vocabulary reconciliation.
- [Zones and Tiers](zones-and-tiers.md) — the regulatory classification this driver lens complements.
- [Governance Fundamentals](governance-fundamentals.md) — the four-pillar control architecture the driver lens supplements.
- [Glossary](../reference/glossary.md) — canonical definitions for *Capability Driver*, *Frontier Readiness*, *Pattern (Frontier Transformation Pattern)*, and *Scale-breaker*.
- [Role catalog](../reference/role-catalog.md) — owner roles for each driver and CAPE-to-FSI role mapping.

---

*Updated: May-2026 | Version: v1.6.2 | Audience: M365 administrators, AI governance leads, FSI architects, CIO/CDAO*
