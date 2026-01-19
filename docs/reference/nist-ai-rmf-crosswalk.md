# NIST AI Risk Management Framework Crosswalk

This document maps the FSI Agent Governance Framework controls to the NIST AI Risk Management Framework (AI RMF 1.0). The crosswalk demonstrates alignment with federal AI risk management guidance endorsed by the U.S. Treasury for financial services.

---

## Overview

The NIST AI RMF provides a structured approach to managing AI risks through four core functions:

| Function | Purpose | FSI Framework Alignment |
|----------|---------|------------------------|
| **GOVERN** | Establish AI governance structures and policies | Pillar 2 (Management), Framework Layer |
| **MAP** | Identify and categorize AI systems and risks | Pillar 3 (Reporting), Zone Classification |
| **MEASURE** | Assess and analyze AI risks | Pillar 1 (Security), Pillar 2 (Testing) |
| **MANAGE** | Prioritize and treat AI risks | All Pillars, Playbooks Layer |

---

## GOVERN Function Mapping

*Cultivate and implement a culture of risk management within organizations designing, developing, deploying, evaluating, or acquiring AI systems.*

### GOVERN 1: Policies, processes, procedures, and practices across the organization

| NIST AI RMF Category | FSI Controls | Coverage |
|---------------------|--------------|----------|
| **GOVERN 1.1:** Legal/regulatory requirements identified | [2.12](../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md), [3.3](../controls/pillar-3-reporting/3.3-compliance-and-regulatory-reporting.md) | Full |
| **GOVERN 1.2:** Processes to assess compliance | [2.6](../controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md), [2.12](../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) | Full |
| **GOVERN 1.3:** Processes for oversight of third-party AI | [2.7](../controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md) | Full |
| **GOVERN 1.4:** Risk management integrated with enterprise | Framework Layer, [2.6](../controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md) | Full |
| **GOVERN 1.5:** Ongoing monitoring processes established | [3.2](../controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md), [3.4](../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) | Full |
| **GOVERN 1.6:** Mechanisms for inventory of AI systems | [3.1](../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md) | Full |
| **GOVERN 1.7:** Processes for decommissioning AI systems | [Agent Decommissioning Playbook](../playbooks/agent-lifecycle/agent-decommissioning.md) | Full |

### GOVERN 2: Accountability structures established

| NIST AI RMF Category | FSI Controls | Coverage |
|---------------------|--------------|----------|
| **GOVERN 2.1:** Roles and responsibilities defined | [Operating Model](../framework/operating-model.md), RACI Templates | Full |
| **GOVERN 2.2:** Personnel trained in AI risk | [2.14](../controls/pillar-2-management/2.14-training-and-awareness-program.md) | Full |
| **GOVERN 2.3:** Executive leadership oversight | [Executive Summary](../framework/executive-summary.md), [Governance Cadence](../framework/governance-cadence.md) | Full |

### GOVERN 3: Workforce diversity and AI literacy

| NIST AI RMF Category | FSI Controls | Coverage |
|---------------------|--------------|----------|
| **GOVERN 3.1:** Decision-making informed by diverse team | [2.12](../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md), RACI | Partial |
| **GOVERN 3.2:** AI literacy appropriate to roles | [2.14](../controls/pillar-2-management/2.14-training-and-awareness-program.md) | Full |

### GOVERN 4: Organizational culture of AI risk awareness

| NIST AI RMF Category | FSI Controls | Coverage |
|---------------------|--------------|----------|
| **GOVERN 4.1:** Risk culture embedded in organization | [Framework Layer](../framework/index.md), [Adoption Roadmap](../framework/adoption-roadmap.md) | Full |
| **GOVERN 4.2:** Feedback mechanisms for AI concerns | [3.10](../controls/pillar-3-reporting/3.10-hallucination-feedback-loop.md), [3.4](../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) | Full |
| **GOVERN 4.3:** Risk management activities documented | [2.13](../controls/pillar-2-management/2.13-documentation-and-record-keeping.md) | Full |

### GOVERN 5: Legal and regulatory requirements

| NIST AI RMF Category | FSI Controls | Coverage |
|---------------------|--------------|----------|
| **GOVERN 5.1:** Legal compliance integrated | [Regulatory Framework](../framework/regulatory-framework.md), [Regulatory Mappings](regulatory-mappings.md) | Full |
| **GOVERN 5.2:** Ongoing monitoring of legal landscape | Governance Cadence, Compliance Reporting | Full |

### GOVERN 6: External stakeholder risk management

| NIST AI RMF Category | FSI Controls | Coverage |
|---------------------|--------------|----------|
| **GOVERN 6.1:** Policies for AI-related external risks | [2.7](../controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md), [1.4](../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md) | Full |
| **GOVERN 6.2:** Processes for third-party due diligence | [2.7](../controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md) | Full |

---

## MAP Function Mapping

*Establish context to frame risks related to an AI system.*

### MAP 1: Context established and documented

| NIST AI RMF Category | FSI Controls | Coverage |
|---------------------|--------------|----------|
| **MAP 1.1:** Intended purpose documented | [3.1](../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md), [Agent Inventory Entry](../playbooks/agent-lifecycle/agent-inventory-entry.md) | Full |
| **MAP 1.2:** Interdependencies identified | [2.17](../controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md), [Related Controls sections] | Full |
| **MAP 1.3:** Technical specifications documented | Agent metadata, Control documentation | Full |
| **MAP 1.4:** Deployment context documented | [Zones and Tiers](../framework/zones-and-tiers.md), Per-Agent Data Policy | Full |
| **MAP 1.5:** Expected benefits and costs articulated | [3.5](../controls/pillar-3-reporting/3.5-cost-allocation-and-budget-tracking.md), Business justification | Full |
| **MAP 1.6:** Scientific and technical limits known | [3.10](../controls/pillar-3-reporting/3.10-hallucination-feedback-loop.md), Model documentation | Full |

### MAP 2: AI system categorized

| NIST AI RMF Category | FSI Controls | Coverage |
|---------------------|--------------|----------|
| **MAP 2.1:** AI system risk categorized | [Zones and Tiers](../framework/zones-and-tiers.md), Zone 1/2/3 classification | Full |
| **MAP 2.2:** Risk tolerance established | Zone requirements, [2.6](../controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md) | Full |
| **MAP 2.3:** Specific risks identified | [AI Risk Assessment Template](../playbooks/incident-and-risk/ai-risk-assessment-template.md) | Full |

### MAP 3: AI capabilities, targeted usage, and potential misuse documented

| NIST AI RMF Category | FSI Controls | Coverage |
|---------------------|--------------|----------|
| **MAP 3.1:** Expected and potential uses documented | Agent Inventory Entry, Per-Agent Data Policy | Full |
| **MAP 3.2:** Potential misuse identified | [1.8](../controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md), [2.20](../controls/pillar-2-management/2.20-adversarial-testing-and-red-team-framework.md) | Full |
| **MAP 3.3:** Trustworthiness requirements identified | Zone requirements, [2.6](../controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md) | Full |

### MAP 4: Risks associated with third-party entities identified

| NIST AI RMF Category | FSI Controls | Coverage |
|---------------------|--------------|----------|
| **MAP 4.1:** Third-party components inventoried | [2.7](../controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md), Connector inventory | Full |
| **MAP 4.2:** Third-party risks assessed | [2.7](../controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md) | Full |

### MAP 5: Impacts characterized

| NIST AI RMF Category | FSI Controls | Coverage |
|---------------------|--------------|----------|
| **MAP 5.1:** Benefits and harms to individuals characterized | [2.11](../controls/pillar-2-management/2.11-bias-testing-and-fairness-assessment-finra-notice-25-07-sr-11-7-alignment.md), [2.19](../controls/pillar-2-management/2.19-customer-ai-disclosure-and-transparency.md) | Full |
| **MAP 5.2:** Environmental impact considered | Out of scope (not primary FSI concern) | N/A |

---

## MEASURE Function Mapping

*Employ quantitative, qualitative, or mixed-method tools, techniques, and methodologies to analyze, assess, benchmark, and monitor AI risk.*

### MEASURE 1: Appropriate methods and metrics identified

| NIST AI RMF Category | FSI Controls | Coverage |
|---------------------|--------------|----------|
| **MEASURE 1.1:** Approaches for measurement identified | [2.5](../controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md), [2.6](../controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md) | Full |
| **MEASURE 1.2:** Metrics appropriate to risk | [3.2](../controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md), [3.10](../controls/pillar-3-reporting/3.10-hallucination-feedback-loop.md) | Full |
| **MEASURE 1.3:** Internal/external evaluations conducted | [2.5](../controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md), [2.20](../controls/pillar-2-management/2.20-adversarial-testing-and-red-team-framework.md) | Full |

### MEASURE 2: AI systems evaluated for trustworthiness

| NIST AI RMF Category | FSI Controls | Coverage |
|---------------------|--------------|----------|
| **MEASURE 2.1:** Tested against trustworthiness characteristics | [2.5](../controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md), [2.6](../controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md) | Full |
| **MEASURE 2.2:** Safety evaluated | [1.8](../controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md), [2.20](../controls/pillar-2-management/2.20-adversarial-testing-and-red-team-framework.md) | Full |
| **MEASURE 2.3:** Security and resilience evaluated | [1.8](../controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md), Pillar 1 Security | Full |
| **MEASURE 2.4:** Explainability evaluated | [Zone 1 Explainability](../playbooks/advanced-implementations/zone1-min-explainability.md) | Partial |
| **MEASURE 2.5:** Privacy evaluated | [1.5](../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md), [1.6](../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md), [1.14](../controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md) | Full |
| **MEASURE 2.6:** Fairness evaluated | [2.11](../controls/pillar-2-management/2.11-bias-testing-and-fairness-assessment-finra-notice-25-07-sr-11-7-alignment.md) | Full |
| **MEASURE 2.7:** Human-AI interaction evaluated | [Human-in-the-Loop](../playbooks/advanced-implementations/human-in-the-loop-triggers.md), [2.12](../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) | Full |
| **MEASURE 2.8:** Transparency claims verified | [2.19](../controls/pillar-2-management/2.19-customer-ai-disclosure-and-transparency.md), [2.21](../controls/pillar-2-management/2.21-ai-marketing-claims-and-substantiation.md) | Full |
| **MEASURE 2.9:** Environmental impact evaluated | Out of scope (not primary FSI concern) | N/A |
| **MEASURE 2.10:** Validity and reliability evaluated | [2.5](../controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md), [2.6](../controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md) | Full |
| **MEASURE 2.11:** Third-party evaluated | [2.7](../controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md) | Full |

### MEASURE 3: Mechanisms for tracking identified AI risks

| NIST AI RMF Category | FSI Controls | Coverage |
|---------------------|--------------|----------|
| **MEASURE 3.1:** Risks tracked over time | [3.4](../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md), [AI Risk Assessment Template](../playbooks/incident-and-risk/ai-risk-assessment-template.md) | Full |
| **MEASURE 3.2:** Feedback mechanisms implemented | [3.10](../controls/pillar-3-reporting/3.10-hallucination-feedback-loop.md) | Full |
| **MEASURE 3.3:** Risk assessment updates documented | [3.3](../controls/pillar-3-reporting/3.3-compliance-and-regulatory-reporting.md), Quarterly reviews | Full |

### MEASURE 4: Measurement feedback incorporated

| NIST AI RMF Category | FSI Controls | Coverage |
|---------------------|--------------|----------|
| **MEASURE 4.1:** Feedback integrated into system improvements | [3.10](../controls/pillar-3-reporting/3.10-hallucination-feedback-loop.md), [2.3](../controls/pillar-2-management/2.3-change-management-and-release-planning.md) | Full |
| **MEASURE 4.2:** Measurement approaches reviewed | [Governance Cadence](../framework/governance-cadence.md), Quarterly assessments | Full |

---

## MANAGE Function Mapping

*Allocate risk resources to mapped and measured risks on a regular basis and as defined by the GOVERN function.*

### MANAGE 1: AI risks based on assessments and priorities treated

| NIST AI RMF Category | FSI Controls | Coverage |
|---------------------|--------------|----------|
| **MANAGE 1.1:** Prioritized risks addressed | Zone classification, [AI Risk Assessment](../playbooks/incident-and-risk/ai-risk-assessment-template.md) | Full |
| **MANAGE 1.2:** Treatment plans implemented | [Remediation Tracking](../playbooks/incident-and-risk/remediation-tracking.md), Control implementation | Full |
| **MANAGE 1.3:** Risk tolerance thresholds acted upon | Zone escalation, [3.4](../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) | Full |
| **MANAGE 1.4:** Negative impacts minimized | Runtime protection, DLP, Access controls | Full |

### MANAGE 2: Strategies to maximize benefits and minimize harms

| NIST AI RMF Category | FSI Controls | Coverage |
|---------------------|--------------|----------|
| **MANAGE 2.1:** Resources allocated to manage risks | [Governance Cadence](../framework/governance-cadence.md), RACI assignments | Full |
| **MANAGE 2.2:** Benefit/harm considerations in deployment | Zone classification, [Per-Agent Data Policy](../playbooks/agent-lifecycle/per-agent-data-policy.md) | Full |
| **MANAGE 2.3:** Decisions documented | [2.13](../controls/pillar-2-management/2.13-documentation-and-record-keeping.md), Decision logs | Full |
| **MANAGE 2.4:** Mechanisms for appeal or recourse | [Human-in-the-Loop](../playbooks/advanced-implementations/human-in-the-loop-triggers.md), Escalation matrix | Full |

### MANAGE 3: AI risks managed throughout lifecycle

| NIST AI RMF Category | FSI Controls | Coverage |
|---------------------|--------------|----------|
| **MANAGE 3.1:** Pre-deployment risk management | [2.5](../controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md), [Agent Promotion Checklist](../playbooks/agent-lifecycle/agent-promotion-checklist.md) | Full |
| **MANAGE 3.2:** Post-deployment monitoring | [3.2](../controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md), [3.10](../controls/pillar-3-reporting/3.10-hallucination-feedback-loop.md) | Full |

### MANAGE 4: Risk treatments monitored and response actions taken

| NIST AI RMF Category | FSI Controls | Coverage |
|---------------------|--------------|----------|
| **MANAGE 4.1:** Post-deployment monitoring implemented | [3.2](../controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md), [1.7](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) | Full |
| **MANAGE 4.2:** Mechanisms to capture emergent risks | [3.4](../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md), [3.10](../controls/pillar-3-reporting/3.10-hallucination-feedback-loop.md) | Full |
| **MANAGE 4.3:** Incident response mechanisms in place | [AI Incident Response Playbook](../playbooks/incident-and-risk/ai-incident-response-playbook.md) | Full |

---

## Coverage Summary

### Methodology

This crosswalk maps FSI Agent Governance Framework controls to the NIST AI RMF 1.0 subcategories. The table below reflects the subcategories explicitly addressed in this document. The official NIST AI RMF 1.0 contains 72 subcategories; this crosswalk addresses 67 subcategories that are most relevant to Microsoft 365 AI agent governance in financial services.

### Subcategory Coverage

| NIST AI RMF Function | Subcategories Addressed | Full Coverage | Partial Coverage | Not Applicable |
|---------------------|-------------------------|---------------|------------------|----------------|
| **GOVERN** | 19 | 18 | 1 | 0 |
| **MAP** | 16 | 15 | 0 | 1 |
| **MEASURE** | 19 | 17 | 1 | 1 |
| **MANAGE** | 13 | 13 | 0 | 0 |
| **TOTAL** | **67** | **63** | **2** | **2** |

### Coverage Calculation

- **Subcategories addressed:** 67 of 72 NIST AI RMF subcategories (93%)
- **Full coverage:** 63 of 67 addressed subcategories (94%)
- **Partial coverage:** 2 subcategories (GOVERN 3.1, MEASURE 2.4)
- **Not applicable to FSI agent governance:** 2 subcategories (MAP 5.2, MEASURE 2.9 - environmental impact)
- **Not explicitly addressed:** 5 subcategories (MEASURE 2.12, 2.13, and others focused on large-scale AI system development not applicable to Microsoft 365 agents)

**Effective Coverage of Applicable Subcategories:** 97% (63 full + 2 partial of 65 applicable)

---

## Alignment Gaps and Remediation

### Partial Coverage Areas

| Category | Gap | Remediation |
|----------|-----|-------------|
| **GOVERN 3.1** (Diverse team) | Framework does not mandate diversity requirements | Organizational hiring/team practices; out of technical scope |
| **MEASURE 2.4** (Explainability) | Basic explainability guidance only | Enhance Zone 1 explainability playbook for enterprise needs |

### Not Applicable Areas

| Category | Rationale |
|----------|-----------|
| **MAP 5.2** (Environmental) | Environmental impact not primary FSI regulatory concern |
| **MEASURE 2.9** (Environmental) | Environmental impact not primary FSI regulatory concern |

### Subcategories Not Explicitly Addressed

The following NIST AI RMF subcategories are not explicitly addressed in this crosswalk because they pertain to large-scale AI system development, training, and data curation rather than governance of pre-built Microsoft 365 agents:

| Category | Description | Rationale |
|----------|-------------|-----------|
| **MEASURE 2.12** | Environmental impact quantified | Not applicable - Microsoft manages infrastructure environmental impact |
| **MEASURE 2.13** | Effectiveness of risk mitigations verified | Covered implicitly through testing controls (2.5, 2.6) but not separately tracked |
| **MAP 3.4** | Assumptions about data validated | Microsoft manages Copilot training data; organization controls grounding data via Pillar 4 |
| **MAP 3.5** | Data provenance documented | Microsoft manages model data provenance; framework covers grounding data governance |
| **GOVERN 4.4** | Documentation of AI system development | Not applicable - framework governs deployed agents, not AI development |

Organizations developing custom AI models beyond Microsoft 365 agents should consult the full NIST AI RMF for these additional requirements.

---

## Using This Crosswalk

### For Compliance Officers

1. Reference this document when responding to regulator inquiries about AI risk management frameworks
2. Map specific control implementations to NIST AI RMF categories for examination documentation
3. Use coverage summary to identify areas requiring additional organizational controls

### For AI Governance Leads

1. Use NIST AI RMF categories as checklist for new agent deployments
2. Reference specific controls when designing governance procedures
3. Identify gaps in current implementations vs. NIST expectations

### For External Auditors

1. Framework demonstrates substantive alignment with NIST AI RMF (93% of subcategories addressed, 97% effective coverage of applicable areas)
2. Partial coverage areas and N/A designations are documented with rationale
3. Control documentation provides implementation evidence
4. Five NIST subcategories not explicitly addressed relate to large-scale AI development (not applicable to Microsoft 365 agent governance)

---

## References

- [NIST AI Risk Management Framework 1.0](https://www.nist.gov/itl/ai-risk-management-framework)
- [NIST AI RMF Playbook](https://airc.nist.gov/AI_RMF_Knowledge_Base/Playbook)
- [Treasury AI in Financial Services Report (March 2024)](https://home.treasury.gov/news/press-releases/jy2212)
- [FSI Agent Governance Framework](../framework/index.md)

---

*FSI Agent Governance Framework v1.1 | Updated: January 2026 | NIST AI RMF Crosswalk Last Verified: January 19, 2026*
