<!-- verify-language-rules: allow-second-tier reason: "CCO quick reference must quote CAPE and vendor marketing language verbatim (in scare quotes) so the CCO can teach reframing to staff and counter-position with examiners." -->

# CCO Quick Reference — AI Agent Examination Readiness

!!! info "Audience"
    **Chief Compliance Officer or senior compliance staff** at a US financial services firm. This document assumes a working knowledge of FINRA, SEC, OCC, and Federal Reserve supervisory expectations, and does not assume engineering depth. M365 administrators should consult the [Control Index](../controls/CONTROL-INDEX.md) and the [Microsoft CAPE Crosswalk](microsoft-cape-crosswalk.md) for the implementation view.

---

## How to use this document

This document is structured **by examiner question**, not by control or pattern. The intent is that a CCO can answer any of the twelve questions below in 60 seconds without scrolling — and can name the controls, playbooks, and crosswalk sections that back the answer.

Each question carries five elements:

1. **Question** — phrased the way an examiner would actually ask it during an interview, sweep, or for-cause exam.
2. **Short answer** — a one- to two-sentence headline the CCO can give in a meeting before opening any binder.
3. **Supporting evidence** — the specific FSI controls, playbooks, and crosswalk patterns to cite, with markdown links.
4. **Regulatory anchor** — the specific rules and bulletins in play (FINRA, SEC, OCC, Federal Reserve, GLBA, CFTC, CFPB, ECOA, Reg E, BSA/AML, state AI laws).
5. **Examiner red flag** — the answer shape that would draw further scrutiny and likely a finding.

The two companion artifacts that make this document operational are the [Regulatory Framework](../framework/regulatory-framework.md) (regulation-by-regulation control mapping) and the [Microsoft CAPE Crosswalk](microsoft-cape-crosswalk.md) (pattern-by-pattern Regulatory Exposure callouts). Where the answer to an examiner question depends on which CAPE pattern the agent represents, the supporting-evidence section will cross-link to the relevant pattern deep-dive.

!!! warning "FINRA Notice 25-07 clarification (still important)"
    Counsel and consultants sometimes cite **FINRA Notice 25-07** as the FINRA AI position. It is not — Notice 25-07 addresses workplace modernization rules, not AI governance. The relevant FINRA AI guidance is **Notice 24-09** (technology-neutral application of supervisory rules to AI), together with **FINRA Rule 3110** (supervision), **Rule 4511** (books and records), **Rule 2210** (communications with the public), and FINRA's **Annual Regulatory Oversight Report** for current AI examination priorities. The 2025 FINRA AI sweep is the most active examiner trigger in this lane today; assume any agent that touches a customer or a registered person will be in scope.

---

## The 12 examiner questions

### Q1 — Recordkeeping: "Show me your records of every AI agent interaction with a customer over the last six years."

**Short answer.** Every customer-touching agent interaction is captured by **Control 1.7** (comprehensive audit logging) and inventoried by **Control 3.1** (agent inventory and metadata). Communications retention follows **SEC 17a-4(b)(4)** (3 years for communications, first 2 years readily accessible); records that constitute books-and-records of the firm follow **SEC 17a-4(a)** and **FINRA Rule 4511** (6 years).

**Supporting evidence.**

- Controls: [1.7 Comprehensive Audit Logging](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md), [1.9 Data Retention](../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md), [2.13 Documentation and Record Keeping](../controls/pillar-2-management/2.13-documentation-and-record-keeping.md), [3.1 Agent Inventory](../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md), [3.11 Centralized Agent Inventory Enforcement](../controls/pillar-3-reporting/3.11-centralized-agent-inventory-enforcement.md).
- Crosswalk: [Pattern 5 — External Engagement](microsoft-cape-crosswalk.md#pattern-5-external-engagement-deep-dive) Regulatory Exposure callout enumerates the customer-interaction record set; the [Retention Period Matrix](../framework/regulatory-framework.md#retention-period-matrix) gives per-record-type periods.

**Regulatory anchor.** **SEC Rule 17a-3** (record creation) and **SEC Rule 17a-4(a) and 17a-4(b)(4)** (record preservation), **FINRA Rule 4511** (general books-and-records), **CFTC Rule 1.31** (records under the Commodity Exchange Act), **SOX 802** (audit workpapers, 7 years).

**Examiner red flag.** "We capture interactions but the model version, prompt, and retrieved sources for a given interaction are not all stored together" — that is a recordkeeping gap. **SEC 17a-4(f)** also requires that records held in electronic form be preserved in non-rewriteable, non-erasable format (or a permitted equivalent). Records that exist only inside a vendor SaaS log without an evidenced WORM equivalent will draw a finding.

---

### Q2 — Supervision: "Who is the registered principal supervising this agent's communications and recommendations?"

**Short answer.** The agent is not an associated person; it cannot be a supervisor and it cannot be supervised in the abstract. A **named registered principal** (broker-dealer) or designated control function (bank) supervises the agent's outputs under **FINRA Rule 3110**, with the supervisory protocol documented in **Control 2.12**. **FINRA Notice 24-09** confirms the supervisory obligation is technology-neutral.

**Supporting evidence.**

- Controls: [2.12 Supervision and Oversight (FINRA Rule 3110)](../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md), [3.4 Incident Reporting](../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md), [2.14 Training and Awareness](../controls/pillar-2-management/2.14-training-and-awareness-program.md).
- Reference: [Operating Model](../framework/operating-model.md) for the canonical RACI; [Role Catalog](role-catalog.md) for the canonical names.
- Crosswalk: [Pattern 4](microsoft-cape-crosswalk.md#pattern-4-core-business-process-transformation-deep-dive) and [Pattern 5](microsoft-cape-crosswalk.md#pattern-5-external-engagement-deep-dive) Regulatory Exposure callouts both name the designated-supervisor requirement.

**Regulatory anchor.** **FINRA Rule 3110(a)–(b)** (written supervisory procedures, designated supervisor), **FINRA Rule 3120** (annual testing of supervisory system), **FINRA Notice 24-09** (technology-neutral application to AI), **OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12) / Federal Reserve SR 26-2 (formerly SR 11-7)** (model risk supervision for banks), **Reg BI** (15 USC 80b-3a; covered persons retain care obligation).

**Examiner red flag.** "The CoE supervises the agent" or "the platform team owns it" — neither answer satisfies Rule 3110. A **federated CoE does not transfer regulated supervisory accountability**; each business unit running an agent must name a supervisor who individually satisfies the controlling regulation (B-D principal, bank control function, Reg BI covered person). Ex-post sampling alone also does not satisfy Rule 3110 for customer-facing recommendations.

---

### Q3 — Model risk: "Where is your model inventory and the validation report for this AI agent?"

**Short answer.** Every AI agent that influences a decision under a model-risk regime is inventoried in **Control 3.1** with model-risk metadata, validated under **Control 2.6** to a documented model-risk tier, and re-validated on the cadence set by **OCC Bulletin 2026-13** (banks; formerly OCC Bulletin 2011-12) or **Federal Reserve SR 26-2** (formerly SR 11-7; the 2026 supersession). For broker-dealers, equivalent expectations are read into supervision under FINRA Rule 3110 and into recordkeeping under FINRA Rule 4511.

**Supporting evidence.**

- Controls: [2.6 Model Risk Management](../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md), [2.5 Testing, Validation and QA](../controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md), [2.20 Adversarial Testing](../controls/pillar-2-management/2.20-adversarial-testing-and-red-team-framework.md), [2.3 Change Management](../controls/pillar-2-management/2.3-change-management-and-release-planning.md), [3.1 Agent Inventory](../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md).
- Solutions: [Model Risk Management Automation](solutions-index.md#model-risk-management-automation), [Hallucination Tracker](solutions-index.md#hallucination-tracker).
- Crosswalk: [Pattern 4 deep-dive](microsoft-cape-crosswalk.md#pattern-4-core-business-process-transformation-deep-dive) (KYC, claims, financial close).

**Regulatory anchor.** **OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12)** §V (ongoing monitoring, outcomes analysis, change control), **Federal Reserve SR 26-2** (formerly SR 11-7), **OCC Bulletin 2013-29** (third-party model dependency — see Q9), **NYDFS Part 500** for state-chartered institutions, **SOX 302/404** if the model affects ICFR.

**Examiner red flag.** "The model was validated when we onboarded it." Validation is an ongoing obligation. A validation report dated more than 12 months old, or no documented re-validation following a retraining or material prompt change, is a finding. If the firm cannot name an **independent validator** (separate from the model owner and the CoE), the model risk function does not satisfy 2011-12 §IV.

---

### Q4 — Communications with the public: "Show me the principal pre-approval and FINRA 2210 filing for the retail communication this agent generated."

**Short answer.** AI-generated content directed at a retail customer of a broker-dealer is a **FINRA Rule 2210** retail communication and is subject to the same principal pre-approval and (where applicable) filing obligations as any other retail communication. **Control 2.19** (customer disclosure) and **Control 2.21** (marketing claims substantiation) document the disclosure and substantiation chain; **Control 2.12** documents the principal review chain.

**Supporting evidence.**

- Controls: [2.19 Customer AI Disclosure and Transparency](../controls/pillar-2-management/2.19-customer-ai-disclosure-and-transparency.md), [2.21 AI Marketing Claims and Substantiation](../controls/pillar-2-management/2.21-ai-marketing-claims-and-substantiation.md), [2.23 User Consent and AI Disclosure Enforcement](../controls/pillar-2-management/2.23-user-consent-and-ai-disclosure-enforcement.md), [2.12 Supervision](../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md), [1.10 Communication Compliance Monitoring](../controls/pillar-1-security/1.10-communication-compliance-monitoring.md).
- Crosswalk: [Pattern 5 — External Engagement](microsoft-cape-crosswalk.md#pattern-5-external-engagement-deep-dive) Regulatory Exposure callout enumerates the FINRA 2210 / Reg BI / Reg E / Reg B exposure stack.

**Regulatory anchor.** **FINRA Rule 2210(b)(1)** (principal pre-approval), **FINRA Rule 2210(c)** (filing requirements), **Reg BI** (disclosure, care, conflict-of-interest, compliance obligations for B-Ds making recommendations to retail customers), **CFPB UDAAP (12 USC 5531)** for unfair, deceptive, or abusive acts and practices, **state AI disclosure laws** (California SB 1001 and SB 243, Utah SB 149, Colorado AI Act).

**Examiner red flag.** "The agent generated it but a human sent it, so the human is responsible." That position is unlikely to hold. Notice 24-09's technology-neutral framing means the firm bears the same obligation for the agent's output as for an associated person's. The absence of a documented pre-approval workflow for AI-generated retail content — or evidence that the workflow was bypassed for a specific message — would be a 2210 finding.

---

### Q5 — Privacy and data protection: "Show me the GLBA 501(b) safeguards for this agent's data access, and the Annual Privacy Notice provided to the customer."

**Short answer.** Customer non-public personal information (NPI) accessed by the agent is governed by **GLBA Section 501(b)** safeguards and the firm's **Regulation P** Annual Privacy Notice. Access scope is documented in **Control 1.18** (RBAC) and **Control 1.22** (information barriers); data minimization is enforced by **Control 1.14**; the audit trail is in **Control 1.7**.

**Supporting evidence.**

- Controls: [1.5 DLP and Sensitivity Labels](../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md), [1.6 Purview DSPM for AI](../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md), [1.13 Sensitive Information Types](../controls/pillar-1-security/1.13-sensitive-information-types-sits-and-pattern-recognition.md), [1.14 Data Minimization and Agent Scope](../controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md), [1.15 Encryption in Transit and at Rest](../controls/pillar-1-security/1.15-encryption-data-in-transit-and-at-rest.md), [1.18 Application-Level RBAC](../controls/pillar-1-security/1.18-application-level-authorization-and-role-based-access-control-rbac.md), [1.22 Information Barriers](../controls/pillar-1-security/1.22-information-barriers.md), [2.26 Entra Agent ID Identity Governance](../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md).
- Reference: [Regulatory Framework — GLBA](../framework/regulatory-framework.md).

**Regulatory anchor.** **GLBA Section 501(b)** (administrative, technical, and physical safeguards), **Regulation P (12 CFR 1016)** (privacy notices and opt-out), **NYDFS Part 500** (cybersecurity and incident notification for NY-licensed institutions), **SEC Regulation S-P** (16 CFR 248) (consumer notice and safeguarding for SEC registrants), **state breach-notification statutes** (CA, NY, MA, IL, others).

**Examiner red flag.** The agent runs as a generic application identity rather than an isolated agent identity with a documented data-access scope (no [Control 2.26](../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md) implementation), or NPI flowing into a vendor LLM endpoint that has not been disclosed in the firm's Annual Privacy Notice and Service-Provider list.

---

### Q6 — Anti-discrimination and fair lending: "Show me the bias-testing results stratified by protected class for the past four quarters of this agent's outputs."

**Short answer.** Any agent whose output influences credit, insurance, or another consumer decision is in scope for **ECOA (Reg B)** and (where applicable) the **Fair Housing Act**, the **Fair Credit Reporting Act**, and CFPB UDAAP. Bias testing is documented in **Control 2.11**, with quarterly stratified results retained per the records retention matrix; conflict-of-interest testing is in **Control 2.18**. Reg B § 1002.9 requires the firm to be able to state the **principal reasons** for an adverse action — a model whose decisions cannot be explained per applicant cannot satisfy Reg B.

**Supporting evidence.**

- Controls: [2.11 Bias Testing and Fairness Assessment](../controls/pillar-2-management/2.11-bias-testing-and-fairness-assessment.md), [2.18 Automated COI Testing](../controls/pillar-2-management/2.18-automated-conflict-of-interest-testing.md), [2.6 Model Risk Management](../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md), [2.5 Testing, Validation, QA](../controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md).
- Solutions: [COI Testing](solutions-index.md#coi-testing).
- Crosswalk: [Pattern 4](microsoft-cape-crosswalk.md#pattern-4-core-business-process-transformation-deep-dive) (KYC outcomes that influence credit), [Pattern 5](microsoft-cape-crosswalk.md#pattern-5-external-engagement-deep-dive) (any customer-facing agent that surfaces credit terms).

**Regulatory anchor.** **ECOA / Regulation B (12 CFR 1002)**, including **§ 1002.9** (adverse-action notification with principal reasons), **Fair Housing Act (42 USC 3601)**, **FCRA (15 USC 1681)**, **CFPB Circular 2023-03** on adverse-action notices using AI, **CFPB UDAAP (12 USC 5531)**, **Reg E (12 CFR 1005)** for EFT-related decisions (see Q10).

**Examiner red flag.** Adverse-action notices that say "the model recommended denial" or that cite generic factors not tied to the specific applicant. The CFPB's stated position is that creditors using AI must give specific and accurate reasons for adverse action; "the algorithm decided" is not a permissible reason. Bias testing that exists but is not stratified by protected-class proxies is also a finding.

---

### Q7 — Autonomy and human-in-the-loop: "What can this agent do without a human in the loop?"

**Short answer.** The framework requires every agent to carry an explicit **autonomy cap** — the highest-impact action class the agent may execute before a designated human supervisor records approval. Autonomy caps are documented per agent, per zone, per pattern. For Zone 3 customer-impacting actions, the autonomy cap is "no consequential action without recorded supervisor approval" and is enforced through **Control 1.23** (step-up authentication for agent operations) and **Control 2.12** (supervision).

**Supporting evidence.**

- Controls: [1.23 Step-Up Authentication for Agent Operations](../controls/pillar-1-security/1.23-step-up-authentication-for-agent-operations.md), [2.12 Supervision](../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md), [2.17 Multi-Agent Orchestration Limits](../controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md), [3.12 Agent Governance Exception and Override Management](../controls/pillar-3-reporting/3.12-agent-governance-exception-and-override-management.md).
- Solutions: [Action Confirmation Auditor](solutions-index.md#action-confirmation-auditor), [HITL Workflow Governance](solutions-index.md#hitl-workflow-governance).
- Reference: [Glossary — Autonomy Cap](glossary.md) (definition reused in every relevant control and pattern callout).

**Regulatory anchor.** **FINRA Rule 3110** (supervision), **OCC Bulletin 2026-13 / Fed SR 26-2** (model risk for decisioning), **Reg BI** (care obligation), **Reg B** (adverse action principal reasons), **FFIEC IT Examination Handbook** (operational risk).

**Examiner red flag.** Marketing language that the agent operates *"autonomously"* or *"makes routine decisions without human review"* — neither phrasing belongs in a firm's governance artifacts (the framework's `scripts/verify_language_rules.py` linter explicitly blocks both in `docs/framework/**` and `docs/controls/**`). If the autonomy cap is "the agent can do anything within its connector scope," there is no autonomy cap; that itself is the finding.

---

### Q8 — Drift management: "How do you detect when this agent's accuracy or behavior has degraded since deployment?"

**Short answer.** The framework treats agents as **products, not projects** — they accumulate risk if unmonitored, and any production change triggers a re-validation event. Continuous monitoring runs through **Control 3.10** (hallucination feedback loop) and **Control 2.9** (performance monitoring); drift events are inventoried in **Control 3.1** and routed through **Control 2.3** (change management). The "drift thesis" is the regulatory hook for **OCC Bulletin 2026-13 §V (formerly OCC 2011-12 §V)** ongoing monitoring.

**Supporting evidence.**

- Controls: [2.9 Agent Performance Monitoring and Optimization](../controls/pillar-2-management/2.9-agent-performance-monitoring-and-optimization.md), [3.2 Usage Analytics and Activity Monitoring](../controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md), [3.10 Hallucination Feedback Loop](../controls/pillar-3-reporting/3.10-hallucination-feedback-loop.md), [3.14 Agent 365 Observability SDK](../controls/pillar-3-reporting/3.14-agent-365-observability-sdk.md), [2.3 Change Management](../controls/pillar-2-management/2.3-change-management-and-release-planning.md).
- Solutions: [Agent Observability Foundation](solutions-index.md#agent-observability-foundation), [Hallucination Tracker](solutions-index.md#hallucination-tracker).
- Reference: [Agent Lifecycle](../framework/agent-lifecycle.md) for the drift framing and retirement criteria.

**Regulatory anchor.** **OCC Bulletin 2026-13 §V** (ongoing monitoring, outcomes analysis, change control), **Federal Reserve SR 26-2**, **FINRA Rule 3120** (annual supervisory testing), **NYDFS Part 500** (continuous monitoring obligations).

**Examiner red flag.** No documented drift signals (no quarterly hallucination-rate trend, no quality regression alert, no re-baselining after a retraining), or a change-management record that does not trigger re-validation when the underlying model version, prompt, or RAG corpus changed materially. *"The system continuously improves itself"* is a sales claim, not a control — and the `scripts/verify_language_rules.py` linter blocks the sales phrasing for exactly this reason.

---

### Q9 — Vendor and Microsoft model risk: "Walk me through your due-diligence file for Microsoft as the underlying model and platform vendor."

**Short answer.** Microsoft is a third-party model and platform provider under **OCC Bulletin 2013-29** (third-party relationships) and is governed in the framework by **Control 2.7** (vendor and third-party risk management). The diligence file includes the SOC 2 Type II report, the Microsoft 365 trust documentation, the Data Protection Addendum and Service-Provider attestation under GLBA and Reg P, the regulator-specific risk attestations (CSA STAR, FedRAMP where applicable), and the firm's own risk-tier classification of each Microsoft service surface used by an agent.

**Supporting evidence.**

- Controls: [2.7 Vendor and Third-Party Risk Management](../controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md), [2.6 Model Risk Management](../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md), [1.4 Advanced Connector Policies](../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md), [2.10 Patch Management and System Updates](../controls/pillar-2-management/2.10-patch-management-and-system-updates.md).
- Reference: [Regulatory Framework — Vendor Risk](../framework/regulatory-framework.md), [License Requirements](license-requirements.md) for the per-service licensing posture.

**Regulatory anchor.** **OCC Bulletin 2013-29** (third-party relationships), **Federal Reserve / OCC / FDIC Interagency Guidance on Third-Party Relationships (June 2023)**, **NYDFS Part 500.11** (third-party service provider security), **GLBA 501(b)** Service-Provider obligations, **SR 13-19 / OCC 2017-21** for material outsourcing.

**Examiner red flag.** Reliance on the cloud provider's certifications without a firm-side risk tier and ongoing monitoring — examiners will read "we use Microsoft, so it's covered" as a delegation of accountability that the rules do not permit. A material model or service change pushed by Microsoft (e.g., default model version change, retention policy change, capability expansion) without a documented intake into the firm's change-management process is a finding.

---

### Q10 — Incident response: "An agent gave a customer incorrect information about an EFT dispute. Walk me through your response."

**Short answer.** The incident triggers (a) **Reg E (12 CFR 1005)** error-resolution timelines (10 business days for provisional credit, 45 days to complete the investigation, 90 days for new accounts and POS / foreign-initiated transfers), (b) the firm's incident-response playbook under **Control 3.4** (incident reporting and root cause analysis), and (c) for SEC registrants, the **Regulation S-P** customer notification expectations as amended in 2024. The CCO is notified within the cadence specified in the firm's Written Supervisory Procedures, and the agent is taken out of the incident scope (or restricted to non-EFT topics) pending root-cause.

**Supporting evidence.**

- Controls: [3.4 Incident Reporting and Root Cause Analysis](../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md), [3.10 Hallucination Feedback Loop](../controls/pillar-3-reporting/3.10-hallucination-feedback-loop.md), [3.12 Agent Governance Exception and Override Management](../controls/pillar-3-reporting/3.12-agent-governance-exception-and-override-management.md), [1.27 AI Agent Content Moderation Enforcement](../controls/pillar-1-security/1.27-ai-agent-content-moderation-enforcement.md), [2.4 Business Continuity and Disaster Recovery](../controls/pillar-2-management/2.4-business-continuity-and-disaster-recovery.md).
- Playbook: [AI Incident Response Playbook](../playbooks/incident-and-risk/ai-incident-response-playbook.md).
- Reference: [Regulatory Framework — Reg E](../framework/regulatory-framework.md).

**Regulatory anchor.** **Regulation E (12 CFR 1005.11)** (error-resolution timelines and disclosures), **CFPB UDAAP**, **SEC Regulation S-P (2024 amendments)** (customer notification of certain incidents), **NYDFS Part 500.17** (cybersecurity event notification — 72 hours), **state breach-notification statutes**, **GLBA Interagency Guidance on Response Programs (12 CFR Part 30 Appendix B)**.

**Examiner red flag.** No documented kill-switch or restriction path for the agent (no [Control 2.24](../controls/pillar-2-management/2.24-agent-feature-enablement-and-restriction-governance.md) implementation), no record of when the agent was restricted and by whom, no after-action that flowed back into bias testing, hallucination tracking, and supervisor sampling.

---

### Q11 — Frontier patterns: "Your CIO has told us the firm is moving toward CAPE Pattern 5 and Pattern 6 deployments. What is your governance posture?"

**Short answer.** The framework recognizes Microsoft's six **CAPE Frontier Transformation Patterns** as a strategic vocabulary, and overlays each with FSI-specific guardrails published in the [Microsoft CAPE Crosswalk](microsoft-cape-crosswalk.md). **Pattern 5 (External Engagement)** is **mandatory Zone 3** in FSI with the full FINRA 2210 / Reg BI / Reg E / Reg B / GLBA / state-AI-law stack engaged. **Pattern 6 (AI-First Capabilities)** carries an explicit framework guardrail: *"Fully autonomous customer-impacting Pattern 6 deployments are not currently supported in Zone 3 without documented regulator pre-approval."*

**Supporting evidence.**

- Crosswalk: [Pattern 4 deep-dive](microsoft-cape-crosswalk.md#pattern-4-core-business-process-transformation-deep-dive), [Pattern 5 deep-dive](microsoft-cape-crosswalk.md#pattern-5-external-engagement-deep-dive), [Pattern 6 deep-dive](microsoft-cape-crosswalk.md#pattern-6-ai-first-capabilities-deep-dive); the [FSI Maturity Translation Table](microsoft-cape-crosswalk.md#fsi-maturity-translation-table) rewriting CAPE Level 500 descriptors so they remain examiner-defensible.
- Controls: [2.6](../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md), [2.17](../controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md), [2.20](../controls/pillar-2-management/2.20-adversarial-testing-and-red-team-framework.md), [3.14](../controls/pillar-3-reporting/3.14-agent-365-observability-sdk.md) — the Pattern 6 mandatory set.

**Regulatory anchor.** **OCC Bulletin 2026-13 / Federal Reserve SR 26-2** (model risk for any decisioning model in Pattern 4 or Pattern 6), **FINRA Rule 2210 / 3110** (Pattern 5 customer-facing), **Reg BI** (Pattern 5 recommendations), **ECOA / Reg B** and **Fair Housing Act** (Pattern 4 KYC outcomes that influence credit), **BSA/AML 31 CFR 1020.220 + OFAC** (Pattern 4 KYC and CDD), **CFTC Rule 1.31** (records).

**Examiner red flag.** The firm is operating a Pattern 6 deployment described in vendor materials as *"sense-decide-act loops,"* *"continuous learning loops,"* or *"self-improving systems"* against customer-impacting decisions, without documented regulator pre-approval. The framework's posture is that such deployments require a documented engagement with the firm's primary regulator(s) before production. Adopting Microsoft's Maturity Level 500 descriptors (such as *"AI-first culture, autonomous, self-improving"*) verbatim into the firm's own attestations is itself an examination risk — the [FSI Maturity Translation Table](microsoft-cape-crosswalk.md#fsi-maturity-translation-table) provides the reframings counsel should use instead.

---

### Q12 — Audit trail: "Reconstruct what this KYC agent did six years ago today: inputs, model version, prompt, retrieved sources, and the decision rendered."

**Short answer.** Reconstruction is the heart of the books-and-records obligation under **SEC 17a-3 / 17a-4**, **FINRA 4511**, and **CFTC 1.31**. **Control 1.7** captures the audit trail; **Control 2.13** maintains the documentation set; **Control 3.1** keeps the model version and prompt-version metadata bound to each interaction; **Control 2.16** retains the RAG source-integrity record so retrieved sources can be reproduced. The agent's identity and authorization at the moment of decision are captured by **Control 2.26** (Entra Agent ID identity governance).

**Supporting evidence.**

- Controls: [1.7 Comprehensive Audit Logging](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md), [1.19 eDiscovery for Agent Interactions](../controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md), [2.13 Documentation and Record Keeping](../controls/pillar-2-management/2.13-documentation-and-record-keeping.md), [2.16 RAG Source Integrity Validation](../controls/pillar-2-management/2.16-rag-source-integrity-validation.md), [2.26 Entra Agent ID Identity Governance](../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md), [3.1 Agent Inventory](../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md).
- Crosswalk: [Pattern 4 examiner Q&A pre-empts](microsoft-cape-crosswalk.md#pattern-4-core-business-process-transformation-deep-dive).
- Reference: [Retention Period Matrix](../framework/regulatory-framework.md#retention-period-matrix).

**Regulatory anchor.** **SEC Rule 17a-3** and **17a-4** (record creation and 6-year preservation, plus the 17a-4(f) electronic-storage media and audit-system requirements), **FINRA Rule 4511**, **CFTC Rule 1.31**, **SOX 802** (7-year audit-workpaper retention), **OCC Bulletin 2026-13 §V (formerly OCC 2011-12 §V)** (re-validation evidence), **NYDFS Part 500** (cybersecurity event records).

**Examiner red flag.** "We have the conversation log but not the model version / prompt / retrieved sources for that date." Reconstruction is all-or-nothing for KYC, claims, fair-lending, and regulatory-reporting flows. Records held only inside a vendor SaaS log without an evidenced WORM equivalent or designated third-party access (the **17a-4(f)(3)(vii)** designated examining authority undertaking) will draw a finding even if the data is technically present.

---

## Pattern-by-pattern compliance posture

These are the headline compliance answers for each of Microsoft CAPE's six Frontier Transformation Patterns. The full pattern × regulation × control treatment is in the [Microsoft CAPE Crosswalk](microsoft-cape-crosswalk.md).

**Pattern 1 — Employee AI Enablement.** Default **Zone 1** (personal productivity). Promotes to Zone 2 when output is shared into team workflows and to Zone 3 when output reaches a customer or generates regulated content. Headline regulatory exposure is GLBA 501(b) (PII inadvertent disclosure) and FINRA 3110 (supervisor visibility into AI-assisted drafts). [Pattern 1 deep-dive →](microsoft-cape-crosswalk.md#pattern-1-employee-ai-enablement)

**Pattern 2 — Business Expert Empowerment.** Default **Zone 2**; **Zone 3 mandatory** when the SME domain is regulated (compliance, model risk, supervisory). The agent is advisory only — the named SME remains accountable for any answer relied upon for a regulatory or supervisory decision. Books-and-records (FINRA 4511, SEC 17a-4) attaches to the Q&A trail. [Pattern 2 deep-dive →](microsoft-cape-crosswalk.md#pattern-2-business-expert-empowerment)

**Pattern 3 — Workplace & IT Services.** Default **Zone 2** for non-regulated services; **Zone 3 mandatory** when the service touches payroll (SOX 404), trade settlement (FINRA 4511), HR records of registered persons (FINRA 3110), or customer files (Reg P / GLBA). CAPE's default Tier 2 placement understates risk in FSI for these cases — use the FSI Zone, not the CAPE Tier. [Pattern 3 deep-dive →](microsoft-cape-crosswalk.md#pattern-3-workplace-it-services)

**Pattern 4 — Core Business Process Transformation.** **Zone 3 mandatory.** Highest-stakes pattern for FSI — KYC, claims, financial close, regulatory reporting each independently trigger model risk (OCC Bulletin 2026-13 / Fed SR 26-2), books-and-records (FINRA 4511 / SEC 17a-4 / CFTC 1.31), fair lending (Reg B / ECOA), BSA/AML (31 CFR 1020.220 + OFAC), and SOX 302/404 if financial close is in scope. Decisions must be reproducible from logged inputs, model version, and prompt. [Pattern 4 deep-dive →](microsoft-cape-crosswalk.md#pattern-4-core-business-process-transformation-deep-dive)

**Pattern 5 — External Engagement.** **Zone 3 mandatory.** Customer-facing — every interaction is simultaneously a FINRA 2210 communication, a Reg BI recommendation event (B-Ds), a Reg E EFT communication (where applicable), an ECOA / Reg B credit communication, a GLBA 501(b) privacy event, and a state-AI-disclosure event. The Org & Culture maturity threshold is *Defined / 300* before production, regardless of CAPE's lower pattern target. [Pattern 5 deep-dive →](microsoft-cape-crosswalk.md#pattern-5-external-engagement-deep-dive)

**Pattern 6 — AI-First Capabilities.** **Zone 3 mandatory, with the framework guardrail D3:** *"Fully autonomous customer-impacting Pattern 6 deployments are not currently supported in Zone 3 without documented regulator pre-approval."* Permitted Pattern 6 deployments in Zone 3 are (a) internal-only optimization or research orchestration, (b) customer-impacting flows with documented human supervisor approval per decision, or (c) deployments with documented OCC / Federal Reserve / SEC / FINRA / state-regulator pre-approval. Multi-agent chains require individual agent inventory (Control 2.17). [Pattern 6 deep-dive →](microsoft-cape-crosswalk.md#pattern-6-ai-first-capabilities-deep-dive)

---

## Reference shortcuts

| Compliance topic | Crosswalk section | Primary FSI controls | Primary playbook(s) |
|---|---|---|---|
| Books and records (general) | Crosswalk §6 — [Regulatory mapping](microsoft-cape-crosswalk.md#6-cape-fsi-regulatory-mapping-cross-reference) | [1.7](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md), [2.13](../controls/pillar-2-management/2.13-documentation-and-record-keeping.md), [3.1](../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md), [3.11](../controls/pillar-3-reporting/3.11-centralized-agent-inventory-enforcement.md) | [Audit Readiness Checklist](../playbooks/compliance-and-audit/audit-readiness-checklist.md) |
| Supervision (FINRA 3110) | [Pattern 4](microsoft-cape-crosswalk.md#pattern-4-core-business-process-transformation-deep-dive), [Pattern 5](microsoft-cape-crosswalk.md#pattern-5-external-engagement-deep-dive) | [2.12](../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md), [3.4](../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) | [RACI Governance Template](../playbooks/governance-operations/raci-governance-template.md) |
| Model risk (OCC Bulletin 2026-13 / Fed SR 26-2) | [Pattern 4](microsoft-cape-crosswalk.md#pattern-4-core-business-process-transformation-deep-dive), [Pattern 6](microsoft-cape-crosswalk.md#pattern-6-ai-first-capabilities-deep-dive) | [2.6](../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md), [2.5](../controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md), [2.20](../controls/pillar-2-management/2.20-adversarial-testing-and-red-team-framework.md) | [Examination Response Guide](../playbooks/compliance-and-audit/examination-response-guide.md) |
| Customer disclosure (FINRA 2210, state AI laws) | [Pattern 5](microsoft-cape-crosswalk.md#pattern-5-external-engagement-deep-dive) | [2.19](../controls/pillar-2-management/2.19-customer-ai-disclosure-and-transparency.md), [2.21](../controls/pillar-2-management/2.21-ai-marketing-claims-and-substantiation.md), [2.23](../controls/pillar-2-management/2.23-user-consent-and-ai-disclosure-enforcement.md) | [Control 2.19 portal walkthrough](../playbooks/control-implementations/2.19/portal-walkthrough.md) |
| Reg BI care obligation | [Pattern 5](microsoft-cape-crosswalk.md#pattern-5-external-engagement-deep-dive) | [2.12](../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md), [2.19](../controls/pillar-2-management/2.19-customer-ai-disclosure-and-transparency.md) | [Action Authorization Matrix](../playbooks/governance-operations/action-authorization-matrix.md) |
| Fair lending (ECOA / Reg B) | [Pattern 4](microsoft-cape-crosswalk.md#pattern-4-core-business-process-transformation-deep-dive), [Pattern 5](microsoft-cape-crosswalk.md#pattern-5-external-engagement-deep-dive) | [2.11](../controls/pillar-2-management/2.11-bias-testing-and-fairness-assessment.md), [2.18](../controls/pillar-2-management/2.18-automated-conflict-of-interest-testing.md), [2.6](../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md) | [Control 2.11 portal walkthrough](../playbooks/control-implementations/2.11/portal-walkthrough.md) |
| Privacy (GLBA 501(b), Reg P, S-P) | [Pattern 5](microsoft-cape-crosswalk.md#pattern-5-external-engagement-deep-dive) | [1.5](../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md), [1.14](../controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md), [1.18](../controls/pillar-1-security/1.18-application-level-authorization-and-role-based-access-control-rbac.md), [2.26](../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md) | [Control 1.5 portal walkthrough](../playbooks/control-implementations/1.5/portal-walkthrough.md) |
| Reg E error resolution | Q10 above | [3.4](../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md), [3.10](../controls/pillar-3-reporting/3.10-hallucination-feedback-loop.md), [1.27](../controls/pillar-1-security/1.27-ai-agent-content-moderation-enforcement.md) | [AI Incident Response Playbook](../playbooks/incident-and-risk/ai-incident-response-playbook.md) |
| BSA/AML and OFAC (KYC/CDD) | [Pattern 4](microsoft-cape-crosswalk.md#pattern-4-core-business-process-transformation-deep-dive) | [2.6](../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md), [2.13](../controls/pillar-2-management/2.13-documentation-and-record-keeping.md), [3.1](../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md) | [Evidence Pack Assembly](../playbooks/compliance-and-audit/evidence-pack-assembly.md) |
| Vendor / third-party (OCC 2013-29) | Q9 above | [2.7](../controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md), [2.10](../controls/pillar-2-management/2.10-patch-management-and-system-updates.md), [1.4](../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md) | [Decision Log Schema](../playbooks/governance-operations/decision-log-schema.md) |
| Drift management | Q8 above | [2.9](../controls/pillar-2-management/2.9-agent-performance-monitoring-and-optimization.md), [3.10](../controls/pillar-3-reporting/3.10-hallucination-feedback-loop.md), [3.14](../controls/pillar-3-reporting/3.14-agent-365-observability-sdk.md), [2.3](../controls/pillar-2-management/2.3-change-management-and-release-planning.md) | [Agent Promotion Checklist](../playbooks/agent-lifecycle/agent-promotion-checklist.md) |
| Autonomy cap and HITL | Q7 above | [1.23](../controls/pillar-1-security/1.23-step-up-authentication-for-agent-operations.md), [2.12](../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md), [2.17](../controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md), [3.12](../controls/pillar-3-reporting/3.12-agent-governance-exception-and-override-management.md) | [Escalation Matrix](../playbooks/governance-operations/escalation-matrix.md) |
| Incident response | Q10 above | [3.4](../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md), [2.4](../controls/pillar-2-management/2.4-business-continuity-and-disaster-recovery.md), [2.24](../controls/pillar-2-management/2.24-agent-feature-enablement-and-restriction-governance.md), [1.27](../controls/pillar-1-security/1.27-ai-agent-content-moderation-enforcement.md) | [AI Risk Assessment Template](../playbooks/incident-and-risk/ai-risk-assessment-template.md) |
| Multi-agent orchestration (Pattern 6) | [Pattern 6](microsoft-cape-crosswalk.md#pattern-6-ai-first-capabilities-deep-dive) | [2.17](../controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md), [3.1](../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md), [3.14](../controls/pillar-3-reporting/3.14-agent-365-observability-sdk.md) | [Agent Inventory Entry](../playbooks/agent-lifecycle/agent-inventory-entry.md) |
| Audit reconstruction (17a-4) | Q12 above | [1.7](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md), [1.19](../controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md), [2.13](../controls/pillar-2-management/2.13-documentation-and-record-keeping.md), [2.16](../controls/pillar-2-management/2.16-rag-source-integrity-validation.md) | [Audit Readiness Checklist](../playbooks/compliance-and-audit/audit-readiness-checklist.md) |

---

## Source attribution and drift management

This document paraphrases Microsoft CAPE materials and US financial-services regulatory guidance with citation. Where vendor or marketing language is reproduced inline (in scare quotes) for the purpose of teaching CCO staff how to reframe what they hear from sales, partners, or internal CIO presentations, the verbatim phrase carries an explicit reframing. No verbatim Microsoft text is otherwise reproduced.

**Microsoft sources** (paraphrased with citation; full retrieval-date metadata in the [Microsoft CAPE Crosswalk](microsoft-cape-crosswalk.md#8-source-attribution-and-drift-management) and the planned `cape-source-tracker.md`):

- Microsoft. *Agentic Transformation Patterns Playbook*. [aka.ms/AgenticTransformationPatterns](https://aka.ms/AgenticTransformationPatterns). Retrieved 2026-05-09.
- Microsoft. *CAPE Frontier Transformation Patterns Walking Deck*. [aka.ms/CAPEAgenticeCOEWalkingDeck](https://aka.ms/CAPEAgenticeCOEWalkingDeck). Retrieved 2026-05-09.
- Microsoft. *Agentic AI Maturity Model*. [aka.ms/AgentMaturityModel](https://aka.ms/AgentMaturityModel). Retrieved 2026-05-09.

**US financial-services regulatory sources** (cited inline above, listed here for completeness):

- FINRA. Rule 3110 (Supervision); Rule 3120 (Supervisory Control System); Rule 4511 (Books and Records); Rule 2210 (Communications with the Public); Notice 24-09 (technology-neutral application to AI); Notice 25-07 (workplace modernization — *not* AI-specific); Annual Regulatory Oversight Report. [finra.org](https://www.finra.org/).
- SEC. Rule 17a-3 (record creation); Rule 17a-4 (record preservation, including 17a-4(b)(4) and 17a-4(f)); Regulation Best Interest (15 USC 80b-3a); Regulation S-P (16 CFR 248), 2024 amendments. [sec.gov](https://www.sec.gov/).
- OCC. Bulletin 2026-13 (Sound Practices for Model Risk Management — 2026 supersession of Bulletin 2011-12); Bulletin 2013-29 (Third-Party Relationships); 2017-21 (Material Outsourcing). [occ.gov](https://www.occ.gov/).
- Federal Reserve. SR 26-2 (formerly SR 11-7; Model Risk Management — 2026 supersession); SR 13-19 / OCC 2017-21 (third-party risk); FFIEC IT Examination Handbook. [federalreserve.gov](https://www.federalreserve.gov/).
- CFPB. Regulation B (12 CFR 1002, ECOA); Regulation E (12 CFR 1005); Regulation P (12 CFR 1016); Circular 2023-03 (adverse-action notices using AI); UDAAP (12 USC 5531). [consumerfinance.gov](https://www.consumerfinance.gov/).
- CFTC. Rule 1.31 (record retention). [cftc.gov](https://www.cftc.gov/).
- Treasury. *AI in Financial Services* report (December 2024); *AI Cybersecurity Risk Management* report (March 2024).
- FinCEN. 31 CFR 1020.220 (Customer Identification Program — banks); related BSA/AML rules.
- NYDFS. Part 500 (Cybersecurity Requirements for Financial Services Companies).
- State AI disclosure laws: California SB 1001 and SB 243; Utah SB 149; Colorado AI Act.

**Drift management.** Microsoft CAPE materials are subject to vendor update cadence; FSI regulatory guidance is subject to rulemaking cycles (FINRA, SEC, OCC, Federal Reserve, CFPB, CFTC, state regulators). The Twelve Examiner Questions are FSI-authored and stable; the regulatory citations and CAPE pattern paraphrases will require updates when the underlying source changes. The framework maintains a `docs/reference/cape-source-tracker.md` (Phase 1 deliverable) for vendor source drift; the [Regulatory Framework](../framework/regulatory-framework.md) and the framework's `learn-monitor.yml` and `regulatory-monitoring.yml` CI workflows track regulatory drift.

This document is informational and does not constitute legal or regulatory advice. The framework supports compliance with the listed regulations through the cited controls and playbooks; individual firms should consult counsel for the specific application to their regulatory perimeter and use case.

---

*Updated: May-2026 | Version: v1.6.2 | Audience: Chief Compliance Officer*
