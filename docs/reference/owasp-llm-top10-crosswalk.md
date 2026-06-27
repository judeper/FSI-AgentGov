---
description: "This document maps the FSI Agent Governance Framework controls to the OWASP Top 10 for LLM Applications (2025), the community-maintained list of the most…"
---
# OWASP Top 10 for LLM Applications Crosswalk

This document maps the FSI Agent Governance Framework controls to the **[OWASP Top 10 for LLM Applications (2025)](https://genai.owasp.org/llm-top-10/)**, the community-maintained list of the most critical security risks for applications built on large language models. Where the [NIST AI RMF Crosswalk](nist-ai-rmf-crosswalk.md) and the [ISO/IEC 42001 Crosswalk](iso-42001-mapping.md) address governance and management-system structure, the OWASP Top 10 is an **attacker-centric** view that helps M365 administrators and security teams reason about how Copilot Studio and Agent Builder agents can be abused — and which FSI-AgentGov controls reduce that exposure.

> **Scope note.** This crosswalk is an implementation aid, not a security certification or penetration-test substitute. A mapping to one or more controls indicates that those controls **help reduce** exposure to the associated risk in a Microsoft 365 / Power Platform agent estate; it does not imply that the risk is fully mitigated. The OWASP LLM risks were written for general-purpose LLM applications, so some risks (for example, model-training poisoning of a self-hosted base model) apply only partially to managed Microsoft 365 Copilot and Copilot Studio agents, where Microsoft operates the underlying models. Organizations should pair this mapping with their own threat modeling, adversarial testing (Control 2.20), and a formal security review before relying on it for assurance evidence.

---

## How to Use This Crosswalk

| Audience | Use |
|----------|-----|
| **Security Architect** threat-modeling an agent | Start from the OWASP risk most relevant to the agent's data and actions, then implement the mapped controls as compensating safeguards. |
| **M365 Administrator** | Confirm that the controls mapped to high-priority OWASP risks (LLM01, LLM02, LLM06) are configured in your tenant. |
| **AI Governance Lead** | Pair this attacker-centric view with the [NIST AI RMF Crosswalk](nist-ai-rmf-crosswalk.md) and [ISO/IEC 42001 Crosswalk](iso-42001-mapping.md) for risk-management and management-system coverage. |
| **Red Team / Adversarial Tester** | Use the per-risk control list as a checklist of safeguards to attempt to bypass during a Control 2.20 engagement. |

---

## Coverage Status Legend

| Status | Meaning |
|--------|---------|
| **Direct** | One or more FSI-AgentGov controls are designed to address this risk class and provide a configurable safeguard. |
| **Partial** | Controls reduce exposure but do not fully address the risk; additional organization-specific safeguards or threat modeling are required. |
| **Indirect** | The risk is addressed as a side effect of a control with a different primary purpose, or applies only partially to managed Microsoft 365 / Copilot Studio agents. |

---

## LLM01: Prompt Injection

An attacker crafts inputs — directly, or indirectly through grounded content such as a document or web page — that manipulate the agent into ignoring its instructions, exfiltrating data, or taking unintended actions. Indirect prompt injection through knowledge sources is the most relevant variant for grounded Microsoft 365 agents.

| FSI Control | How It Helps | Coverage |
|-------------|--------------|----------|
| [1.8 — Runtime Protection and External Threat Detection](../controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md) | Detects and blocks prompt-injection and jailbreak attempts at runtime | Direct |
| [1.21 — Adversarial Input Logging](../controls/pillar-1-security/1.21-adversarial-input-logging.md) | Captures suspicious inputs for detection, investigation, and tuning | Direct |
| [1.27 — AI Agent Content Moderation Enforcement](../controls/pillar-1-security/1.27-ai-agent-content-moderation-enforcement.md) | Moderates inputs/outputs to catch manipulation and unsafe content | Direct |
| [2.16 — RAG Source Integrity Validation](../controls/pillar-2-management/2.16-rag-source-integrity-validation.md) | Reduces indirect injection via poisoned or untrusted grounding sources | Direct |
| [1.26 — Agent File Upload and File Analysis Restrictions](../controls/pillar-1-security/1.26-agent-file-upload-and-file-analysis-restrictions.md) | Limits file-borne injection payloads delivered through uploads | Partial |
| [2.20 — Adversarial Testing and Red Team Framework](../controls/pillar-2-management/2.20-adversarial-testing-and-red-team-framework.md) | Proactively tests agents for injection susceptibility before release | Direct |

---

## LLM02: Sensitive Information Disclosure

The agent reveals sensitive data — PII, financial records, secrets, or restricted documents — through its outputs, either because it was grounded on over-permissioned content or because access controls were too broad. This is the highest-impact risk for FSI agents and the most heavily covered by the framework.

| FSI Control | How It Helps | Coverage |
|-------------|--------------|----------|
| [1.5 — Data Loss Prevention (DLP) and Sensitivity Labels](../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) | Prevents labeled/sensitive data from being surfaced or exfiltrated | Direct |
| [1.6 — Microsoft Purview: DSPM for AI](../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md) | Discovers and monitors sensitive-data exposure across AI interactions | Direct |
| [1.13 — Sensitive Information Types (SITs) and Pattern Recognition](../controls/pillar-1-security/1.13-sensitive-information-types-sits-and-pattern-recognition.md) | Identifies sensitive data so it can be protected and policy-controlled | Direct |
| [1.14 — Data Minimization and Agent Scope Control](../controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md) | Limits the data an agent can access to what it genuinely needs | Direct |
| [1.16 — Information Rights Management (IRM) for Documents](../controls/pillar-1-security/1.16-information-rights-management-irm-for-documents.md) | Enforces usage rights on documents the agent may reference | Direct |
| [1.22 — Information Barriers for AI Agents](../controls/pillar-1-security/1.22-information-barriers.md) | Segregates data between groups to prevent cross-disclosure | Direct |
| [4.1 — SharePoint IAG / Restricted Content Discovery](../controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md) | Surfaces over-shared content before it reaches an agent's grounding scope | Direct |
| [4.7 — Microsoft 365 Copilot Data Governance](../controls/pillar-4-sharepoint/4.7-microsoft-365-copilot-data-governance.md) | Governs what Copilot can ground on across the M365 estate | Direct |
| [4.8 — Item-Level Permission Scanning for Agent Knowledge Sources](../controls/pillar-4-sharepoint/4.8-item-level-permission-scanning-agent-knowledge-sources.md) | Detects over-permissioned items in agent knowledge sources | Direct |

---

## LLM03: Supply Chain

Vulnerabilities introduced through third-party components — connectors, plugins, models, or integrated apps — that the agent depends on. For managed Microsoft 365 agents, the most relevant supply-chain surface is connectors, integrated apps, and vendor services rather than the base model.

| FSI Control | How It Helps | Coverage |
|-------------|--------------|----------|
| [2.7 — Vendor and Third-Party Risk Management](../controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md) | Governs due diligence and ongoing risk for third-party AI components | Direct |
| [1.4 — Advanced Connector Policies (ACP)](../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md) | Restricts which connectors agents may use and how data flows through them | Direct |
| [1.2 — Agent Registry and Integrated Apps Management](../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md) | Inventories and governs integrated apps in the agent supply chain | Direct |
| [1.24 — Defender AI Security Posture Management (AI-SPM)](../controls/pillar-1-security/1.24-defender-ai-security-posture-management.md) | Surfaces posture and vulnerability findings across the AI surface | Partial |
| [2.10 — Patch Management and System Updates](../controls/pillar-2-management/2.10-patch-management-and-system-updates.md) | Tracks platform/component updates that remediate known weaknesses | Partial |

---

## LLM04: Data and Model Poisoning

Manipulation of training data, fine-tuning data, or grounding/knowledge sources to introduce backdoors, bias, or false information. For managed Microsoft 365 agents, base-model training is operated by Microsoft, so the practical exposure is concentrated in **grounding-source poisoning** rather than model-weight poisoning.

| FSI Control | How It Helps | Coverage |
|-------------|--------------|----------|
| [2.16 — RAG Source Integrity Validation](../controls/pillar-2-management/2.16-rag-source-integrity-validation.md) | Validates the integrity and trustworthiness of grounding sources | Direct |
| [1.3 — SharePoint Content Governance and Permissions](../controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md) | Controls who can write to content the agent grounds on | Direct |
| [4.6 — Grounding Scope Governance](../controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md) | Constrains grounding to approved, governed source sets | Direct |
| [1.26 — Agent File Upload and File Analysis Restrictions](../controls/pillar-1-security/1.26-agent-file-upload-and-file-analysis-restrictions.md) | Limits poisoned content entering via file uploads | Partial |
| [2.5 — Testing, Validation, and Quality Assurance](../controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md) | Detects degraded or anomalous behavior from tainted sources | Partial |
| **Base-model training poisoning** | Operated by Microsoft for managed Copilot/Copilot Studio models; out of customer scope | Indirect |

---

## LLM05: Improper Output Handling

The agent's output is consumed downstream (rendered in a browser, executed, or passed to another system) without adequate validation, enabling XSS, code execution, or data injection in connected systems.

| FSI Control | How It Helps | Coverage |
|-------------|--------------|----------|
| [1.27 — AI Agent Content Moderation Enforcement](../controls/pillar-1-security/1.27-ai-agent-content-moderation-enforcement.md) | Moderates generated output before it is surfaced or acted upon | Direct |
| [1.25 — MIME Type Restrictions for File Uploads](../controls/pillar-1-security/1.25-mime-type-restrictions.md) | Restricts file types in agent input/output handling paths | Partial |
| [1.18 — Application-Level Authorization and RBAC](../controls/pillar-1-security/1.18-application-level-authorization-and-role-based-access-control-rbac.md) | Limits what downstream actions an agent's output can trigger | Partial |
| [2.5 — Testing, Validation, and Quality Assurance](../controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md) | Validates output behavior across downstream integration points | Partial |

---

## LLM06: Excessive Agency

The agent is granted excessive functionality, permissions, or autonomy, so that a manipulated or malfunctioning agent can take damaging actions. Constraining what an agent is permitted to *do* — and requiring confirmation for sensitive operations — is the primary mitigation.

| FSI Control | How It Helps | Coverage |
|-------------|--------------|----------|
| [1.14 — Data Minimization and Agent Scope Control](../controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md) | Restricts agent access to the minimum data and capability needed | Direct |
| [1.18 — Application-Level Authorization and RBAC](../controls/pillar-1-security/1.18-application-level-authorization-and-role-based-access-control-rbac.md) | Scopes agent permissions to least privilege | Direct |
| [1.23 — Step-Up Authentication for AI Agent Operations](../controls/pillar-1-security/1.23-step-up-authentication-for-agent-operations.md) | Requires additional verification before sensitive agent actions | Direct |
| [1.4 — Advanced Connector Policies (ACP)](../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md) | Limits the external actions an agent can perform via connectors | Direct |
| [2.8 — Access Control and Segregation of Duties](../controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md) | Prevents any single agent or identity from holding excessive authority | Direct |
| [2.17 — Multi-Agent Orchestration Limits](../controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md) | Bounds agent-to-agent delegation and chained autonomy | Direct |
| [2.26 — Entra Agent ID — Identity Governance for Agents](../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md) | Gives agents governed identities so their privileges can be managed and revoked | Direct |

---

## LLM07: System Prompt Leakage

The agent's system prompt — which may contain instructions, configuration, or (poorly placed) secrets — is exposed to users through extraction attacks. The framework addresses this **indirectly**: it has no control dedicated to system-prompt protection, but adversarial-testing, logging, and data-minimization controls reduce both the likelihood of leakage and its impact.

| FSI Control | How It Helps | Coverage |
|-------------|--------------|----------|
| [2.20 — Adversarial Testing and Red Team Framework](../controls/pillar-2-management/2.20-adversarial-testing-and-red-team-framework.md) | Tests agents for prompt-extraction susceptibility before release | Partial |
| [1.21 — Adversarial Input Logging](../controls/pillar-1-security/1.21-adversarial-input-logging.md) | Records extraction attempts for detection and investigation | Partial |
| [1.8 — Runtime Protection and External Threat Detection](../controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md) | Detects manipulation attempts that target the system prompt | Partial |
| [1.14 — Data Minimization and Agent Scope Control](../controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md) | Reduces impact by keeping secrets and sensitive data out of prompts | Indirect |

---

## LLM08: Vector and Embedding Weaknesses

Weaknesses in how grounding/RAG content is indexed, embedded, and retrieved — including embedding inversion, retrieval of over-permissioned content, and cross-tenant or cross-user leakage through the vector store. For Microsoft 365 agents this maps closely to **knowledge-source permission and grounding governance**.

| FSI Control | How It Helps | Coverage |
|-------------|--------------|----------|
| [4.8 — Item-Level Permission Scanning for Agent Knowledge Sources](../controls/pillar-4-sharepoint/4.8-item-level-permission-scanning-agent-knowledge-sources.md) | Detects over-permissioned items that could be retrieved improperly | Direct |
| [4.1 — SharePoint IAG / Restricted Content Discovery](../controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md) | Identifies restricted content before it enters retrieval scope | Direct |
| [4.6 — Grounding Scope Governance](../controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md) | Constrains which sources an agent can retrieve from | Direct |
| [2.16 — RAG Source Integrity Validation](../controls/pillar-2-management/2.16-rag-source-integrity-validation.md) | Validates the integrity of retrieved grounding content | Direct |
| [4.9 — Embedded File Content Governance](../controls/pillar-4-sharepoint/4.9-embedded-file-content-governance.md) | Governs embedded file content within grounding sources | Direct |
| [1.16 — Information Rights Management (IRM) for Documents](../controls/pillar-1-security/1.16-information-rights-management-irm-for-documents.md) | Enforces document rights even when content is indexed for retrieval | Partial |

---

## LLM09: Misinformation

The agent produces false, fabricated, or misleading output (including hallucinations) that users may act on. For FSI firms this carries regulatory exposure where customer-facing or advice-adjacent content is involved.

| FSI Control | How It Helps | Coverage |
|-------------|--------------|----------|
| [3.10 — Hallucination Feedback Loop](../controls/pillar-3-reporting/3.10-hallucination-feedback-loop.md) | Captures, tracks, and remediates hallucinated/incorrect output | Direct |
| [2.16 — RAG Source Integrity Validation](../controls/pillar-2-management/2.16-rag-source-integrity-validation.md) | Grounds responses in validated sources to reduce fabrication | Direct |
| [2.5 — Testing, Validation, and Quality Assurance](../controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md) | Validates accuracy before and during production use | Direct |
| [2.11 — Bias Testing and Fairness Assessment](../controls/pillar-2-management/2.11-bias-testing-and-fairness-assessment.md) | Detects skewed or unfair output that misinforms users | Partial |
| [2.12 — Supervision and Oversight (FINRA Rule 3110)](../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) | Applies human supervision to agent communications | Direct |
| [2.19 — Customer AI Disclosure and Transparency](../controls/pillar-2-management/2.19-customer-ai-disclosure-and-transparency.md) | Discloses AI involvement so users can weigh reliability | Partial |
| [2.21 — AI Marketing Claims and Substantiation](../controls/pillar-2-management/2.21-ai-marketing-claims-and-substantiation.md) | Requires substantiation for AI-generated marketing claims | Partial |

---

## LLM10: Unbounded Consumption

Uncontrolled resource use — including denial-of-service, denial-of-wallet, and runaway agent loops — that drives cost or degrades availability. The framework addresses this through consumption governance, budgeting, monitoring, and orchestration limits.

| FSI Control | How It Helps | Coverage |
|-------------|--------------|----------|
| [2.27 — Consumption-Entitlement Governance](../controls/pillar-2-management/2.27-consumption-entitlement-governance.md) | Bounds agent consumption against allocated entitlements | Direct |
| [3.5 — Cost Allocation and Budget Tracking](../controls/pillar-3-reporting/3.5-cost-allocation-and-budget-tracking.md) | Tracks and attributes spend so runaway usage is detected | Direct |
| [2.22 — Inactivity Timeout Enforcement](../controls/pillar-2-management/2.22-inactivity-timeout-enforcement.md) | Terminates idle sessions to limit wasted consumption | Direct |
| [2.17 — Multi-Agent Orchestration Limits](../controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md) | Bounds chained/looping agent calls that amplify consumption | Direct |
| [3.2 — Usage Analytics and Activity Monitoring](../controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md) | Surfaces anomalous usage spikes for investigation | Direct |
| [2.9 — Agent Performance Monitoring and Optimization](../controls/pillar-2-management/2.9-agent-performance-monitoring-and-optimization.md) | Monitors performance/resource patterns to catch degradation | Partial |

---

## Coverage Summary

| OWASP Risk | Mapped Controls | Strength of Coverage |
|------------|-----------------|----------------------|
| **LLM01** Prompt Injection | 6 | Strong |
| **LLM02** Sensitive Information Disclosure | 9 | Very strong |
| **LLM03** Supply Chain | 5 | Strong |
| **LLM04** Data and Model Poisoning | 5 + base-model note | Strong (grounding); base-model training out of customer scope |
| **LLM05** Improper Output Handling | 4 | Moderate |
| **LLM06** Excessive Agency | 7 | Very strong |
| **LLM07** System Prompt Leakage | 4 | Indirect — no dedicated control |
| **LLM08** Vector and Embedding Weaknesses | 6 | Strong |
| **LLM09** Misinformation | 7 | Strong |
| **LLM10** Unbounded Consumption | 6 | Strong |

> **Interpretation and coverage signals.** The framework's deepest coverage is in **LLM02 (Sensitive Information Disclosure)** and **LLM06 (Excessive Agency)** — the two risks most consequential for regulated financial services, and the areas where Microsoft 365 data-governance and access controls are most mature.
>
> Two risks show genuinely thinner coverage. **LLM07 (System Prompt Leakage)** has *no control dedicated to protecting the system prompt itself*; it is addressed only indirectly through adversarial testing, logging, and data minimization (keeping secrets out of prompts). Organizations that embed sensitive logic or configuration in agent instructions should treat this as a residual risk and validate it through Control 2.20 red-team exercises. **LLM05 (Improper Output Handling)** is also lighter, because downstream consumption of agent output frequently occurs in customer-built integrations outside the FSI-AgentGov control surface.
>
> For **LLM04**, the framework's controls address *grounding-source* poisoning — the practically reachable surface for managed agents — but base-model training poisoning is operated by Microsoft and is therefore outside customer scope rather than an uncovered gap.

---

## References

- [OWASP Top 10 for LLM Applications (2025)](https://genai.owasp.org/llm-top-10/)
- [OWASP GenAI Security Project](https://genai.owasp.org/)
- [NIST AI RMF Crosswalk](nist-ai-rmf-crosswalk.md) — risk-management framework crosswalk
- [ISO/IEC 42001 Crosswalk](iso-42001-mapping.md) — AI management-system standard crosswalk
- [Regulatory Mappings](regulatory-mappings.md) — FSI-specific regulatory crosswalk
- [Control Index](../controls/CONTROL-INDEX.md) — master list of all 79 controls

---

*Updated: June 2026 | Version: v1.6.2 | OWASP LLM Top 10 Crosswalk Last Verified: June 2026*
