# Microsoft Responsible AI Standard v2 — Controls Mapping

This document maps the FSI Agent Governance Framework controls to **Microsoft's Responsible AI Standard v2 (2022)** and its six guiding principles, as articulated on the [Microsoft AI principles and approach page](https://www.microsoft.com/en-us/ai/principles-and-approach) and the annual [Responsible AI Transparency Report](https://www.microsoft.com/corporate-responsibility/responsible-ai-transparency-report).

The Microsoft Responsible AI (RAI) Standard is the internal Microsoft requirement set used to design, build, and ship Microsoft AI products (Microsoft 365 Copilot, Copilot Studio, Microsoft Foundry, GitHub Copilot, Security Copilot, etc.) and is the principle-level document that Microsoft's [ISO/IEC 42001 certification](https://learn.microsoft.com/en-us/compliance/regulatory/offering-iso-42001) is audited against.

> **Why this mapping exists.** FSI organizations adopting Microsoft AI services inherit a portion of Microsoft's RAI implementation when they consume Microsoft 365 Copilot, Copilot Studio, or Microsoft Foundry — but inheriting the platform's RAI implementation is **not** the same as operating an RAI program for the customer's own use of those services. This crosswalk identifies, for each Microsoft RAI principle, the FSI-AgentGov controls a customer must operate themselves to demonstrate end-to-end RAI alignment. Pair this mapping with [Control 2.7 (Vendor and Third-Party Risk Management)](../controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md) when documenting Microsoft's platform-level RAI evidence as part of customer due diligence.

---

## How to Use This Mapping

| Audience | Use |
|----------|-----|
| **AI Governance Lead** | Demonstrate that the customer's own RAI program addresses each Microsoft RAI principle for the agents the firm builds, not just the platform Microsoft ships. |
| **Compliance Officer** | Use as a structural overlay alongside the [NIST AI RMF Crosswalk](nist-ai-rmf-crosswalk.md), [ISO/IEC 42001 Crosswalk](iso-42001-mapping.md), and [Regulatory Mappings](regulatory-mappings.md). Microsoft RAI principles map cleanly to NIST RMF functions and ISO 42001 Annex A controls. |
| **Vendor Risk Manager** | When evaluating Microsoft AI products, validate Microsoft's RAI claims against the linked Microsoft public sources, then document customer-side controls below as compensating measures. |
| **External Reviewer / Examiner** | Use the principle-by-principle table to check that the customer treats Microsoft's RAI commitments as input to — not substitute for — their own AI risk-management program. |

---

## Microsoft Responsible AI Principles

Microsoft's RAI program defines six principles that govern AI design, development, and deployment. Each principle is reinforced by Microsoft's RAI Standard v2 (2022), the annual Responsible AI Transparency Report, and Transparency Notes published per AI service.

| # | Principle | Microsoft definition (paraphrased) |
|---|---|---|
| 1 | **Fairness** | AI systems should treat all people fairly. |
| 2 | **Reliability and Safety** | AI systems should perform reliably and safely. |
| 3 | **Privacy and Security** | AI systems should be secure and respect privacy. |
| 4 | **Inclusiveness** | AI systems should empower everyone and engage people. |
| 5 | **Transparency** | AI systems should be understandable. |
| 6 | **Accountability** | People should be accountable for AI systems. |

> Source: [Microsoft AI principles and approach](https://www.microsoft.com/en-us/ai/principles-and-approach), retrieved May 2026. The RAI Standard v2 (2022) and the [Responsible AI Transparency Report](https://www.microsoft.com/corporate-responsibility/responsible-ai-transparency-report) are the public artifacts Microsoft publishes to evidence the program.

---

## Principle 1 — Fairness

**What Microsoft does:** Microsoft RAI engineering practices include disaggregated model evaluations, bias evaluation tooling in Microsoft Foundry, and Transparency Notes that document known fairness limitations per AI service.

**What FSI customers must do themselves:** Validate that agents built on Microsoft AI services do not introduce unfair outcomes within the customer's specific use case, customer base, and regulatory perimeter (ECOA, Fair Housing, FCRA where applicable).

| FSI Control | Why it supports Fairness |
|---|---|
| [2.11 — Bias Testing and Fairness Assessment](../controls/pillar-2-management/2.11-bias-testing-and-fairness-assessment.md) | Direct customer-side bias / disparate-impact testing for agent decisions and outputs. |
| [2.18 — Automated Conflict of Interest Testing](../controls/pillar-2-management/2.18-automated-conflict-of-interest-testing.md) | Helps surface decision-bias drivers tied to advisor incentives. |
| [2.20 — Adversarial Testing and Red Team Framework](../controls/pillar-2-management/2.20-adversarial-testing-and-red-team-framework.md) | Red-team exercises include fairness-stress prompts and protected-class probes. |
| [2.5 — Testing, Validation, and Quality Assurance](../controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md) | Test sets include fairness evaluators (Hate / Unfairness, Protected Materials) where supported. |
| [3.4 — Incident Reporting and Root Cause Analysis](../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) | Fairness incidents and customer complaints feed root-cause analysis. |

---

## Principle 2 — Reliability and Safety

**What Microsoft does:** Microsoft Foundry observability (built-in evaluators, monitoring, distributed tracing) provides quality, safety, and operational metrics for AI applications. Azure AI Content Safety provides Prompt Shields (with optional Spotlighting for indirect attacks) at the inference boundary. Defender for Cloud Threat Protection for AI Workloads detects misuse at runtime.

**What FSI customers must do themselves:** Establish reliability gates before production publishing, validate behavior under adversarial conditions, monitor in-production drift, and operate an incident-response process tied to model-risk management (OCC Bulletin 2026-13 / SR 26-2).

| FSI Control | Why it supports Reliability and Safety |
|---|---|
| [2.5 — Testing, Validation, and Quality Assurance](../controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md) | Pre-publish quality gates, Microsoft Foundry Evaluations integration, golden datasets, evaluator coverage. |
| [2.6 — Model Risk Management (OCC Bulletin 2026-13 / SR 26-2)](../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md) | Effective challenge, ongoing monitoring, and supervisor sign-off for material AI models. |
| [2.9 — Agent Performance Monitoring and Optimization](../controls/pillar-2-management/2.9-agent-performance-monitoring-and-optimization.md) | Production monitoring with quality and operational metrics. |
| [1.21 — Adversarial Input Logging](../controls/pillar-1-security/1.21-adversarial-input-logging.md) | Prompt-injection / jailbreak detection (Prompt Shields, Spotlighting) and SOC alerting. |
| [2.20 — Adversarial Testing and Red Team Framework](../controls/pillar-2-management/2.20-adversarial-testing-and-red-team-framework.md) | Periodic red-team exercises against Zone 3 agents. |
| [2.4 — Business Continuity and Disaster Recovery](../controls/pillar-2-management/2.4-business-continuity-and-disaster-recovery.md) | Recovery objectives and continuity testing for material AI agents. |
| [3.4 — Incident Reporting and Root Cause Analysis](../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) | Incident handling for safety / reliability events. |

---

## Principle 3 — Privacy and Security

**What Microsoft does:** Microsoft 365 Copilot, Copilot Studio, and Microsoft Foundry inherit Microsoft 365 / Azure platform security baselines. Purview DSPM for AI surfaces sensitive-data exposure across AI interactions; Defender XDR provides Copilot-specific threat detection.

**What FSI customers must do themselves:** Operate identity, conditional access, encryption, sensitivity labeling, audit, and supervisory monitoring on top of the platform — and tie those operations to GLBA Safeguards, NYDFS Part 500, and (where applicable) state privacy regimes.

| FSI Control | Why it supports Privacy and Security |
|---|---|
| [1.1 — Restrict Agent Publishing by Authorization](../controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md) | Identity-perimeter enforcement and authorization gating for agent publishing. |
| [1.2 — Agent Registry and Integrated Apps Management](../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md) | Agent-identity inventory and consent governance. |
| [1.3 — SharePoint Content Governance and Permissions](../controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md) | Content-permission discipline for what agents can ground on. |
| [1.5 — Data Loss Prevention (DLP) and Sensitivity Labels](../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) | DLP and sensitivity-label enforcement at the agent boundary. |
| [1.6 — Microsoft Purview DSPM for AI](../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md) | Sensitive-data exposure visibility for AI interactions. |
| [1.7 — Comprehensive Audit Logging and Compliance](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) | `CopilotInteraction` audit trail for evidence preservation. |
| [1.8 — Runtime Protection and External Threat Detection](../controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md) | Defender XDR for Copilot detection plane. |
| [1.13 — Sensitive Information Types (SITs)](../controls/pillar-1-security/1.13-sensitive-information-types-sits-and-pattern-recognition.md) | Pattern recognition for NPI / MNPI prevention in agent flows. |
| [1.14 — Data Minimization and Agent Scope Control](../controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md) | Limit grounding scope to what agents actually require. |
| [1.20 — Network Isolation / Private Connectivity](../controls/pillar-1-security/1.20-network-isolation-private-connectivity.md) | Network-layer isolation for AI workloads. |
| [1.24 — Defender AI Security Posture Management (AI-SPM)](../controls/pillar-1-security/1.24-defender-ai-security-posture-management.md) | Multi-cloud AI security posture, Shadow AI discovery, attack-path analysis. |
| [4.7 — Microsoft 365 Copilot Data Governance](../controls/pillar-4-sharepoint/4.7-microsoft-365-copilot-data-governance.md) | M365 Copilot data-governance posture. |

---

## Principle 4 — Inclusiveness

**What Microsoft does:** Microsoft publishes accessibility commitments (WCAG, Section 508), supports localized models, and documents accessibility limitations in Transparency Notes per AI service.

**What FSI customers must do themselves:** Verify that the agent UX is usable across customer demographics (accessibility, language, channel), and that supervisory and disclosure flows are equally available to all customer segments — particularly when AI is in the customer journey under Reg BI, fiduciary, or fair-dealing obligations.

| FSI Control | Why it supports Inclusiveness |
|---|---|
| [2.19 — Customer AI Disclosure and Transparency](../controls/pillar-2-management/2.19-customer-ai-disclosure-and-transparency.md) | Disclosure language available in customer-appropriate channels and languages. |
| [2.23 — User Consent and AI Disclosure Enforcement](../controls/pillar-2-management/2.23-user-consent-and-ai-disclosure-enforcement.md) | Consent flows operate equally for accessibility / assistive-technology users. |
| [2.14 — Training and Awareness Program](../controls/pillar-2-management/2.14-training-and-awareness-program.md) | Internal training covers inclusive design considerations for agent authors. |

> **Coverage note.** Inclusiveness is the FSI principle area where customer-side controls are least mature in this catalog by design — accessibility and inclusive-channel review traditionally live in product / digital-experience teams rather than AI governance. Customers should pair the controls above with their existing accessibility program (typically WCAG 2.1 AA at minimum for US FSI public-facing channels).

---

## Principle 5 — Transparency

**What Microsoft does:** Microsoft publishes [Transparency Notes](https://learn.microsoft.com/en-us/azure/foundry/responsible-ai/openai/transparency-note) per AI service that document intended use, limitations, evaluation methodology, and data handling. Microsoft Foundry observability (tracing) provides per-request execution visibility.

**What FSI customers must do themselves:** Document customer-built agents, disclose AI use to customers and supervisors, retain explainability evidence for material decisions, and ensure marketing claims about AI are substantiated.

| FSI Control | Why it supports Transparency |
|---|---|
| [2.13 — Documentation and Record Keeping](../controls/pillar-2-management/2.13-documentation-and-record-keeping.md) | Documented agent design, intended use, training data sources, evaluation methodology. |
| [2.19 — Customer AI Disclosure and Transparency](../controls/pillar-2-management/2.19-customer-ai-disclosure-and-transparency.md) | Customer-facing disclosure of AI involvement. |
| [2.21 — AI Marketing Claims and Substantiation](../controls/pillar-2-management/2.21-ai-marketing-claims-and-substantiation.md) | Substantiation of AI marketing claims against actual capability. |
| [2.23 — User Consent and AI Disclosure Enforcement](../controls/pillar-2-management/2.23-user-consent-and-ai-disclosure-enforcement.md) | Consent and disclosure enforced at the agent boundary. |
| [3.3 — Compliance and Regulatory Reporting](../controls/pillar-3-reporting/3.3-compliance-and-regulatory-reporting.md) | Reporting of AI governance posture to leadership and examiners. |
| [3.1 — Agent Inventory and Metadata Management](../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md) | Authoritative agent register with intended-use metadata. |

---

## Principle 6 — Accountability

**What Microsoft does:** Microsoft publishes the annual Responsible AI Transparency Report, maintains the RAI Standard, and operates an Office of Responsible AI plus an Aether Committee for oversight.

**What FSI customers must do themselves:** Establish documented accountability for AI governance — named owners for every agent, supervisory review, model risk approval, audit trail, and reporting up to the board / risk committee.

| FSI Control | Why it supports Accountability |
|---|---|
| [1.2 — Agent Registry and Integrated Apps Management](../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md) | Named Agent Owner / Sponsor for every Zone 2/3 agent; sponsorship lifecycle workflows. |
| [2.6 — Model Risk Management (OCC Bulletin 2026-13 / SR 26-2)](../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md) | Effective-challenge governance, model risk register, supervisor sign-off. |
| [2.7 — Vendor and Third-Party Risk Management](../controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md) | Documented evidence of Microsoft's platform-level RAI commitments and vendor due diligence. |
| [2.12 — Supervision and Oversight (FINRA Rule 3110)](../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) | Supervisory accountability for AI-mediated communications. |
| [2.13 — Documentation and Record Keeping](../controls/pillar-2-management/2.13-documentation-and-record-keeping.md) | Documented governance decisions, approval records, exception handling. |
| [2.14 — Training and Awareness Program](../controls/pillar-2-management/2.14-training-and-awareness-program.md) | Documented training records for personnel operating AI systems. |
| [3.1 — Agent Inventory and Metadata Management](../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md) | Authoritative inventory tying every agent to a named owner and approval record. |
| [3.3 — Compliance and Regulatory Reporting](../controls/pillar-3-reporting/3.3-compliance-and-regulatory-reporting.md) | Reporting cadence to leadership, board, and regulators. |
| [3.4 — Incident Reporting and Root Cause Analysis](../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) | Accountability for incident response and corrective action. |
| [Operating Model](../framework/operating-model.md) + [RACI Matrix](raci-matrix.md) | Framework-level accountability structure. |

---

## Cross-Walk Summary

The matrix below summarizes which FSI controls touch which Microsoft RAI principles. A given control can address more than one principle; only the most direct relationships are marked.

| Control | Fairness | Reliability & Safety | Privacy & Security | Inclusiveness | Transparency | Accountability |
|---|---|---|---|---|---|---|
| 1.1 Restrict Agent Publishing by Authorization | | | ✓ | | | ✓ |
| 1.2 Agent Registry | | | ✓ | | | ✓ |
| 1.3 SharePoint Content Governance | | | ✓ | | | |
| 1.5 DLP / Sensitivity Labels | | | ✓ | | | |
| 1.6 DSPM for AI | | | ✓ | | | |
| 1.7 Audit Logging | | | ✓ | | ✓ | ✓ |
| 1.8 Runtime / Defender XDR | | ✓ | ✓ | | | |
| 1.13 SITs | | | ✓ | | | |
| 1.14 Data Minimization | | | ✓ | | | |
| 1.20 Network Isolation | | | ✓ | | | |
| 1.21 Adversarial Input Logging | | ✓ | ✓ | | | |
| 1.24 Defender AI-SPM | | ✓ | ✓ | | | |
| 2.4 BCDR | | ✓ | | | | |
| 2.5 Testing & Validation | ✓ | ✓ | | | | |
| 2.6 Model Risk Management | | ✓ | | | | ✓ |
| 2.7 Vendor Risk Management | | | | | | ✓ |
| 2.9 Performance Monitoring | | ✓ | | | | |
| 2.11 Bias Testing | ✓ | | | | | |
| 2.12 Supervision (FINRA 3110) | | | | | | ✓ |
| 2.13 Documentation & Record Keeping | | | | | ✓ | ✓ |
| 2.14 Training & Awareness | | | | ✓ | | ✓ |
| 2.18 COI Testing | ✓ | | | | | |
| 2.19 Customer AI Disclosure | | | | ✓ | ✓ | |
| 2.20 Adversarial Testing / Red Team | ✓ | ✓ | | | | |
| 2.21 AI Marketing Claims | | | | | ✓ | |
| 2.23 User Consent & Disclosure | | | | ✓ | ✓ | |
| 3.1 Agent Inventory | | | | | ✓ | ✓ |
| 3.3 Compliance Reporting | | | | | ✓ | ✓ |
| 3.4 Incident Reporting | ✓ | ✓ | | | | ✓ |
| 4.7 M365 Copilot Data Governance | | | ✓ | | | |

---

## Relationship to Other Frameworks

| Microsoft RAI Principle | NIST AI RMF Function (closest) | ISO/IEC 42001 Clause / Annex A (closest) |
|---|---|---|
| Fairness | MEASURE 2.11 (Fairness/bias) | A.5 (Impact assessment), A.6.2.4 (Verification & validation) |
| Reliability and Safety | MEASURE 2.5 / MANAGE 4 | A.6.2.4, A.6.2.6 (Operation & monitoring) |
| Privacy and Security | MEASURE 2.7 / MANAGE 1 | A.7 (Data for AI systems), A.6.2.8 (Event logs) |
| Inclusiveness | GOVERN 3.1 / MEASURE 2.11 | A.5.4 (Impact on individuals or groups) |
| Transparency | MEASURE 2.8 / MANAGE 4.3 | A.8 (Information for interested parties) |
| Accountability | GOVERN 1 / GOVERN 2 | Clause 5 (Leadership), A.3 (Internal organization) |

For full mappings see the [NIST AI RMF Crosswalk](nist-ai-rmf-crosswalk.md) and [ISO/IEC 42001 Crosswalk](iso-42001-mapping.md).

---

## References

- [Microsoft AI principles and approach](https://www.microsoft.com/en-us/ai/principles-and-approach) — public landing page (retrieved May 2026)
- [Responsible AI Transparency Report](https://www.microsoft.com/corporate-responsibility/responsible-ai-transparency-report) — annual public report
- [Microsoft Responsible AI Standard v2 (2022)](https://blogs.microsoft.com/wp-content/uploads/prod/sites/5/2022/06/Microsoft-Responsible-AI-Standard-v2-General-Requirements-3.pdf) — public RAI Standard PDF
- [Microsoft AI Customer Commitments (June 2023)](https://blogs.microsoft.com/blog/2023/06/08/announcing-microsofts-ai-customer-commitments/) — customer-facing commitments
- [Microsoft Learn: ISO/IEC 42001 offering](https://learn.microsoft.com/en-us/compliance/regulatory/offering-iso-42001) — services in scope and audit-report access
- [Microsoft Learn: Microsoft Foundry — Responsible use of AI overview](https://learn.microsoft.com/en-us/azure/foundry/responsible-use-of-ai-overview) — Transparency Notes per service
- [NIST AI RMF Crosswalk](nist-ai-rmf-crosswalk.md)
- [ISO/IEC 42001 Crosswalk](iso-42001-mapping.md)
- [Regulatory Mappings](regulatory-mappings.md)

---

*Updated: May 2026 | Version: v1.6.2 | Microsoft RAI v2 Mapping Last Verified: May 2026*
