# ISO/IEC 42001:2023 Crosswalk

This document maps the FSI Agent Governance Framework controls to **ISO/IEC 42001:2023 — Artificial Intelligence Management System (AIMS)**, the international standard for organizational AI governance.

ISO/IEC 42001 is **complementary to NIST AI RMF** (see [NIST AI RMF Crosswalk](nist-ai-rmf-crosswalk.md)) — the frameworks address different needs and many FSI organizations implement both. NIST AI RMF supports continuous risk identification and measurement; ISO/IEC 42001 provides a certifiable management-system structure (Plan-Do-Check-Act) that aligns with ISO 27001, ISO 9001, and other ISO management systems FSI firms already operate.

> **Scope note.** This crosswalk maps clauses 4–10 (the certifiable management-system requirements) and Annex A (control objectives) to FSI-AgentGov controls. It is provided as an implementation aid for organizations preparing for ISO/IEC 42001 certification or third-party audit. It is not a conformity assessment and does not substitute for a formal gap analysis by an accredited certification body. Organizations should verify scope statements with their internal audit / compliance teams before relying on this mapping for certification evidence.

---

## How to Use This Crosswalk

| Audience | Use |
|----------|-----|
| **Compliance Officer** preparing for ISO 42001 certification | Identify which FSI controls already provide implementation evidence; flag clauses with `Partial` or `N/A` coverage for gap remediation. |
| **Internal Auditor** | Validate that FSI-AgentGov controls produce the artifacts ISO 42001 auditors expect (policies, risk register, monitoring records, management review minutes). |
| **External Auditor (ISO 42001 certification body)** | Use the mapping as a roadmap for evidence collection — most clauses are addressed by existing Pillar 2 (Management) and Pillar 3 (Reporting) controls. |
| **AI Governance Lead** | Pair this crosswalk with the [NIST AI RMF Crosswalk](nist-ai-rmf-crosswalk.md) for end-to-end coverage of both frameworks. |

---

## Coverage Status Legend

| Status | Meaning |
|--------|---------|
| **Full** | One or more FSI-AgentGov controls directly address the clause requirements with documented procedures and evidence. |
| **Partial** | FSI-AgentGov controls provide partial coverage; additional organization-specific procedures or policies are required. |
| **Framework** | Addressed at the framework layer (governance principles, operating model) rather than via a specific control. |
| **Org** | Organization-specific responsibility; FSI-AgentGov provides supporting controls but the AIMS scope, policy, and management review must be authored by the organization. |
| **N/A** | Clause is administrative or scoping in nature and does not map to a technical control. |

---

## Microsoft AI Service Certification Context

Microsoft has achieved ISO/IEC 42001 certification covering the following AI services in scope (per [Microsoft Learn — ISO/IEC 42001 offering page](https://learn.microsoft.com/en-us/compliance/regulatory/offering-iso-42001), retrieved May 2026):

- GitHub Copilot
- Microsoft 365 Copilot
- Microsoft Copilot Health
- Microsoft Copilot Studio
- Microsoft Dragon Copilot
- Microsoft Foundry
- Microsoft Security Copilot

Audit reports and scope statements are available through the [Microsoft Service Trust Portal](https://servicetrust.microsoft.com/viewpage/ISOIEC).

> **Caveat for FSI maintainers:** Microsoft's certification covers Microsoft's own service operations as the AI provider. It does **not** transfer to customer governance, customer use cases, or the customer's own AIMS. FSI organizations pursuing their own ISO 42001 certification must build and operate their own management system on top of these certified services. Use vendor certification as **input** to Control 2.7 (Vendor Risk Management) — not as a substitute for the customer's own AIMS evidence.

---

## Clause 4: Context of the Organization

| Clause | Requirement | FSI Controls / Artifacts | Coverage |
|--------|-------------|--------------------------|----------|
| **4.1** Understanding the organization and its context | Determine external/internal issues relevant to AIMS purpose | [Executive Summary](../framework/executive-summary.md), [Regulatory Framework](../framework/regulatory-framework.md), [Adoption Roadmap](../framework/adoption-roadmap.md) | Framework |
| **4.2** Understanding needs and expectations of interested parties | Identify stakeholders and their AIMS-relevant requirements | [Operating Model](../framework/operating-model.md), [RACI Matrix](raci-matrix.md), [Role Catalog](role-catalog.md) | Framework |
| **4.3** Determining the scope of the AIMS | Document AIMS scope boundaries and exclusions | Framework Layer (Zone definitions in [Zones and Tiers](../framework/zones-and-tiers.md)) | Org |
| **4.4** AI Management System | Establish, implement, maintain, continually improve the AIMS | [Governance Fundamentals](../framework/governance-fundamentals.md), [Governance Cadence](../framework/governance-cadence.md) | Framework |

---

## Clause 5: Leadership

| Clause | Requirement | FSI Controls / Artifacts | Coverage |
|--------|-------------|--------------------------|----------|
| **5.1** Leadership and commitment | Top management demonstrates leadership for the AIMS | [Executive Summary](../framework/executive-summary.md), [Operating Model](../framework/operating-model.md) | Framework |
| **5.2** AI Policy | Establish and document AI policy | Framework Layer + [2.13 — Documentation and Record Keeping](../controls/pillar-2-management/2.13-documentation-and-record-keeping.md) | Org |
| **5.3** Roles, responsibilities, authorities | Assign and communicate AIMS roles | [Operating Model](../framework/operating-model.md), [RACI Matrix](raci-matrix.md), [Role Catalog](role-catalog.md), [1.2 — Agent Registry](../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md) | Full |

---

## Clause 6: Planning

| Clause | Requirement | FSI Controls / Artifacts | Coverage |
|--------|-------------|--------------------------|----------|
| **6.1.1** Actions to address risks and opportunities | Plan AIMS actions for risks/opportunities | [2.6 — Model Risk Management](../controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md), [Adoption Roadmap](../framework/adoption-roadmap.md) | Full |
| **6.1.2** AI risk assessment | Establish, implement, maintain AI risk assessment process | [2.6](../controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md), [2.11 — Bias Testing](../controls/pillar-2-management/2.11-bias-testing-and-fairness-assessment.md), [2.20 — Adversarial Testing / Red Team](../controls/pillar-2-management/2.20-adversarial-testing-and-red-team-framework.md) | Full |
| **6.1.3** AI risk treatment | Risk treatment plan with documented controls | [2.6](../controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md), Pillar 1 (Security) controls catalog | Full |
| **6.1.4** AI system impact assessment | Assess potential impacts on individuals, groups, society | [2.11](../controls/pillar-2-management/2.11-bias-testing-and-fairness-assessment.md), [2.19 — Customer AI Disclosure](../controls/pillar-2-management/2.19-customer-ai-disclosure-and-transparency.md) | Partial |
| **6.2** AI objectives and planning to achieve them | Establish measurable AIMS objectives | [Adoption Roadmap](../framework/adoption-roadmap.md), [Governance Cadence](../framework/governance-cadence.md) | Org |
| **6.3** Planning of changes | Plan changes to the AIMS in a controlled manner | [2.3 — Change Management](../controls/pillar-2-management/2.3-change-management-and-release-planning.md) | Full |

---

## Clause 7: Support

| Clause | Requirement | FSI Controls / Artifacts | Coverage |
|--------|-------------|--------------------------|----------|
| **7.1** Resources | Determine and provide AIMS resources | Org responsibility; supported by [Adoption Roadmap](../framework/adoption-roadmap.md) | Org |
| **7.2** Competence | Ensure personnel competence; retain evidence | [2.14 — Training and Awareness Program](../controls/pillar-2-management/2.14-training-and-awareness-program.md) | Full |
| **7.3** Awareness | Awareness of AI policy, contributions, implications | [2.14](../controls/pillar-2-management/2.14-training-and-awareness-program.md), [2.19 — Customer AI Disclosure](../controls/pillar-2-management/2.19-customer-ai-disclosure-and-transparency.md) | Full |
| **7.4** Communication | Internal/external communications relevant to AIMS | [2.13 — Documentation and Record Keeping](../controls/pillar-2-management/2.13-documentation-and-record-keeping.md), [3.3 — Compliance and Regulatory Reporting](../controls/pillar-3-reporting/3.3-compliance-and-regulatory-reporting.md) | Full |
| **7.5** Documented information | Create, control, retain documented information | [1.7 — Comprehensive Audit Logging](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md), [2.13](../controls/pillar-2-management/2.13-documentation-and-record-keeping.md), [1.19 — eDiscovery for Agent Interactions](../controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md) | Full |

---

## Clause 8: Operation

| Clause | Requirement | FSI Controls / Artifacts | Coverage |
|--------|-------------|--------------------------|----------|
| **8.1** Operational planning and control | Plan, implement, control AIMS processes | [2.1 — Managed Environments](../controls/pillar-2-management/2.1-managed-environments.md), [2.15 — Environment Routing](../controls/pillar-2-management/2.15-environment-routing.md) | Full |
| **8.2** AI risk assessment | Operate the risk assessment process at planned intervals | [2.6](../controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md), [Governance Cadence](../framework/governance-cadence.md) | Full |
| **8.3** AI risk treatment | Implement the risk treatment plan | Pillar 1 (Security) catalog, [2.6](../controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md) | Full |
| **8.4** AI system impact assessment | Perform impact assessment for AI systems in scope | [2.11](../controls/pillar-2-management/2.11-bias-testing-and-fairness-assessment.md), [2.19](../controls/pillar-2-management/2.19-customer-ai-disclosure-and-transparency.md), [2.21 — AI Marketing Claims and Substantiation](../controls/pillar-2-management/2.21-ai-marketing-claims-and-substantiation.md) | Partial |

---

## Clause 9: Performance Evaluation

| Clause | Requirement | FSI Controls / Artifacts | Coverage |
|--------|-------------|--------------------------|----------|
| **9.1** Monitoring, measurement, analysis, evaluation | Determine what to monitor, methods, frequency | [2.9 — Agent Performance Monitoring](../controls/pillar-2-management/2.9-agent-performance-monitoring-and-optimization.md), [3.2 — Usage Analytics](../controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md), [3.7 — PPAC Security Posture Assessment](../controls/pillar-3-reporting/3.7-ppac-security-posture-assessment.md) | Full |
| **9.2** Internal audit | Conduct planned internal audits of the AIMS | [3.3 — Compliance and Regulatory Reporting](../controls/pillar-3-reporting/3.3-compliance-and-regulatory-reporting.md), [Governance Cadence](../framework/governance-cadence.md) | Full |
| **9.3** Management review | Top management reviews the AIMS at planned intervals | [Governance Cadence](../framework/governance-cadence.md), [Operating Model](../framework/operating-model.md) | Framework |

---

## Clause 10: Improvement

| Clause | Requirement | FSI Controls / Artifacts | Coverage |
|--------|-------------|--------------------------|----------|
| **10.1** Continual improvement | Continually improve AIMS suitability and effectiveness | [Governance Cadence](../framework/governance-cadence.md), [Adoption Roadmap](../framework/adoption-roadmap.md) | Framework |
| **10.2** Nonconformity and corrective action | React to nonconformities; document corrective action | [3.4 — Incident Reporting and Root Cause Analysis](../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md), [2.3 — Change Management](../controls/pillar-2-management/2.3-change-management-and-release-planning.md) | Full |

---

## Annex A — AI Management System Controls

ISO/IEC 42001 Annex A defines control objectives organized into nine categories (A.2 through A.10). The mapping below covers the categories most directly addressed by the FSI-AgentGov catalog. Annex A is **informative** in the standard — organizations document which Annex A controls they apply via a Statement of Applicability (SoA).

### A.2 — Policies Related to AI

| Control Objective | FSI Controls / Artifacts | Coverage |
|---|---|---|
| **A.2.2** AI policy documented and approved | Org responsibility; supported by [Operating Model](../framework/operating-model.md) | Org |
| **A.2.3** Alignment with other organizational policies | [Regulatory Framework](../framework/regulatory-framework.md), [Regulatory Mappings](regulatory-mappings.md) | Framework |
| **A.2.4** Review of AI policy | [Governance Cadence](../framework/governance-cadence.md) | Framework |

### A.3 — Internal Organization

| Control Objective | FSI Controls / Artifacts | Coverage |
|---|---|---|
| **A.3.2** AI roles and responsibilities | [Operating Model](../framework/operating-model.md), [RACI Matrix](raci-matrix.md), [Role Catalog](role-catalog.md) | Full |
| **A.3.3** Reporting of concerns | [3.4 — Incident Reporting](../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) | Full |

### A.4 — Resources for AI Systems

| Control Objective | FSI Controls / Artifacts | Coverage |
|---|---|---|
| **A.4.2** Resource documentation | [3.1 — Agent Inventory and Metadata Management](../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md), [1.2 — Agent Registry](../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md) | Full |
| **A.4.3** Data resources | [1.6 — DSPM for AI](../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md), [4.6 — Grounding Scope Governance](../controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md), [4.7 — M365 Copilot Data Governance](../controls/pillar-4-sharepoint/4.7-microsoft-365-copilot-data-governance.md) | Full |
| **A.4.4** Tooling resources | [2.5 — Testing, Validation, and Quality Assurance](../controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md) | Full |
| **A.4.5** System and computing resources | [1.20 — Network Isolation](../controls/pillar-1-security/1.20-network-isolation-private-connectivity.md), [2.4 — Business Continuity and Disaster Recovery](../controls/pillar-2-management/2.4-business-continuity-and-disaster-recovery.md) | Full |
| **A.4.6** Human resources | [2.14 — Training and Awareness Program](../controls/pillar-2-management/2.14-training-and-awareness-program.md) | Full |

### A.5 — Assessing Impacts of AI Systems

| Control Objective | FSI Controls / Artifacts | Coverage |
|---|---|---|
| **A.5.2** AI system impact assessment process | [2.11 — Bias Testing and Fairness Assessment](../controls/pillar-2-management/2.11-bias-testing-and-fairness-assessment.md), [2.6](../controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md) | Partial |
| **A.5.3** Documentation of AI system impact assessment | [2.13 — Documentation and Record Keeping](../controls/pillar-2-management/2.13-documentation-and-record-keeping.md) | Full |
| **A.5.4** Assessing AI system impact on individuals or groups | [2.11](../controls/pillar-2-management/2.11-bias-testing-and-fairness-assessment.md), [2.19 — Customer AI Disclosure](../controls/pillar-2-management/2.19-customer-ai-disclosure-and-transparency.md) | Partial |
| **A.5.5** Assessing societal impacts | Org responsibility; informed by [Regulatory Framework](../framework/regulatory-framework.md) | Org |

### A.6 — AI System Lifecycle

| Control Objective | FSI Controls / Artifacts | Coverage |
|---|---|---|
| **A.6.1.2** Objectives for responsible development | [Operating Model](../framework/operating-model.md), [Adoption Roadmap](../framework/adoption-roadmap.md) | Framework |
| **A.6.1.3** Processes for responsible AI design and development | [2.5 — Testing, Validation, and Quality Assurance](../controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md), [2.11](../controls/pillar-2-management/2.11-bias-testing-and-fairness-assessment.md) | Full |
| **A.6.2.2** AI system requirements and specification | [1.2 — Agent Registry](../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md), [3.1 — Agent Inventory](../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md) | Full |
| **A.6.2.3** Documentation of AI system design and development | [2.13](../controls/pillar-2-management/2.13-documentation-and-record-keeping.md) | Full |
| **A.6.2.4** AI system verification and validation | [2.5](../controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md), [2.20 — Adversarial Testing / Red Team](../controls/pillar-2-management/2.20-adversarial-testing-and-red-team-framework.md) | Full |
| **A.6.2.5** AI system deployment | [2.1 — Managed Environments](../controls/pillar-2-management/2.1-managed-environments.md), [2.3 — Change Management](../controls/pillar-2-management/2.3-change-management-and-release-planning.md), [2.15 — Environment Routing](../controls/pillar-2-management/2.15-environment-routing.md) | Full |
| **A.6.2.6** AI system operation and monitoring | [2.9 — Agent Performance Monitoring](../controls/pillar-2-management/2.9-agent-performance-monitoring-and-optimization.md), [3.2 — Usage Analytics](../controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md) | Full |
| **A.6.2.7** AI system technical documentation | [2.13](../controls/pillar-2-management/2.13-documentation-and-record-keeping.md), [2.19](../controls/pillar-2-management/2.19-customer-ai-disclosure-and-transparency.md) | Full |
| **A.6.2.8** AI system event logs | [1.7 — Comprehensive Audit Logging](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md), [3.9 — Microsoft Sentinel Integration](../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md) | Full |

### A.7 — Data for AI Systems

| Control Objective | FSI Controls / Artifacts | Coverage |
|---|---|---|
| **A.7.2** Data for development and enhancement of AI systems | [1.6 — DSPM for AI](../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md), [2.16 — RAG Source Integrity Validation](../controls/pillar-2-management/2.16-rag-source-integrity-validation.md) | Full |
| **A.7.3** Acquisition of data | [4.6 — Grounding Scope Governance](../controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md), [2.7 — Vendor Risk Management](../controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md) | Full |
| **A.7.4** Quality of data for AI systems | [2.16](../controls/pillar-2-management/2.16-rag-source-integrity-validation.md), [4.6](../controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md) | Full |
| **A.7.5** Data provenance | [2.16](../controls/pillar-2-management/2.16-rag-source-integrity-validation.md), [1.7 — Comprehensive Audit Logging](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) | Full |
| **A.7.6** Data preparation | [4.7 — M365 Copilot Data Governance](../controls/pillar-4-sharepoint/4.7-microsoft-365-copilot-data-governance.md), [1.13 — Sensitive Information Types](../controls/pillar-1-security/1.13-sensitive-information-types-sits-and-pattern-recognition.md) | Full |

### A.8 — Information for Interested Parties

| Control Objective | FSI Controls / Artifacts | Coverage |
|---|---|---|
| **A.8.2** System documentation and information for users | [2.19 — Customer AI Disclosure and Transparency](../controls/pillar-2-management/2.19-customer-ai-disclosure-and-transparency.md), [2.23 — User Consent and AI Disclosure Enforcement](../controls/pillar-2-management/2.23-user-consent-and-ai-disclosure-enforcement.md) | Full |
| **A.8.3** External reporting | [3.3 — Compliance and Regulatory Reporting](../controls/pillar-3-reporting/3.3-compliance-and-regulatory-reporting.md), [3.4 — Incident Reporting](../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) | Full |
| **A.8.4** Communication of incidents | [3.4](../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md), [1.21 — Adversarial Input Logging](../controls/pillar-1-security/1.21-adversarial-input-logging.md) | Full |
| **A.8.5** Information for interested parties | [2.19](../controls/pillar-2-management/2.19-customer-ai-disclosure-and-transparency.md), [2.21 — AI Marketing Claims and Substantiation](../controls/pillar-2-management/2.21-ai-marketing-claims-and-substantiation.md) | Full |

### A.9 — Use of AI Systems

| Control Objective | FSI Controls / Artifacts | Coverage |
|---|---|---|
| **A.9.2** Processes for responsible use of AI systems | [2.12 — Supervision and Oversight (FINRA Rule 3110)](../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md), [2.14 — Training and Awareness](../controls/pillar-2-management/2.14-training-and-awareness-program.md) | Full |
| **A.9.3** Objectives for responsible use of AI systems | [Operating Model](../framework/operating-model.md), [Governance Fundamentals](../framework/governance-fundamentals.md) | Framework |
| **A.9.4** Intended use of the AI system | [1.14 — Data Minimization and Agent Scope Control](../controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md), [2.17 — Multi-Agent Orchestration Limits](../controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md) | Full |

### A.10 — Third-Party and Customer Relationships

| Control Objective | FSI Controls / Artifacts | Coverage |
|---|---|---|
| **A.10.2** Allocating responsibilities | [2.7 — Vendor and Third-Party Risk Management](../controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md) | Full |
| **A.10.3** Suppliers | [2.7](../controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md) | Full |
| **A.10.4** Customers | [2.19 — Customer AI Disclosure](../controls/pillar-2-management/2.19-customer-ai-disclosure-and-transparency.md), [2.23 — User Consent and AI Disclosure Enforcement](../controls/pillar-2-management/2.23-user-consent-and-ai-disclosure-enforcement.md) | Full |

---

## Coverage Summary

| Coverage | Count (Approx.) | Notes |
|---|---|---|
| Full | 22 | Direct mapping to documented controls |
| Partial | 4 | Supported but require organization-specific augmentation |
| Framework | 9 | Addressed at framework / governance-principles layer |
| Org | 6 | Organization-specific responsibility (AIMS scope, policy, management review) |

> **Interpretation.** A high `Full` count indicates that a customer pursuing ISO/IEC 42001 certification can use FSI-AgentGov as a substantial implementation backbone for an M365 / Power Platform AI estate. The `Org`-coverage clauses (4.3 scope, 5.2 AI policy, 6.2 objectives, 7.1 resources, 9.3 management review, A.2.2 AI policy approval) are deliberately customer-owned — no external framework can author them on the organization's behalf. The `Partial`-coverage rows generally require domain-specific impact-assessment language that the organization writes against its own products and customer base.

---

## Relationship to NIST AI RMF

NIST AI RMF and ISO/IEC 42001 are **complementary**, not competitive:

| Aspect | NIST AI RMF | ISO/IEC 42001 |
|--------|-------------|---------------|
| Nature | Voluntary risk-management framework | Certifiable management-system standard |
| Structure | 4 functions (Govern, Map, Measure, Manage), 72 subcategories | PDCA management system (Plan-Do-Check-Act), Annex A control objectives |
| Certification | Not certifiable | Third-party certifiable by accredited bodies |
| Geography | U.S.-focused | International |
| Primary value | Continuous risk identification and measurement | Formal governance structure and certifiable evidence |

**Recommended sequencing for FSI organizations:**

1. Begin with NIST AI RMF risk assessments (lower implementation barrier) — see [NIST AI RMF Crosswalk](nist-ai-rmf-crosswalk.md)
2. Formalize findings into ISO/IEC 42001 AIMS policies and Annex A control mapping
3. Pursue ISO/IEC 42001 certification (typically 12–18 month engagement with an accredited certification body)
4. Use NIST AI RMF for continuous risk monitoring between annual ISO 42001 surveillance audits

---

## References

- [ISO/IEC 42001:2023 — Information technology — Artificial intelligence — Management system](https://www.iso.org/standard/81230.html) (paid standard)
- [Microsoft Learn: ISO/IEC 42001 offering page](https://learn.microsoft.com/en-us/compliance/regulatory/offering-iso-42001)
- [Microsoft Service Trust Portal — ISO/IEC reports and certificates](https://servicetrust.microsoft.com/viewpage/ISOIEC)
- [Microsoft Responsible AI Standard v2 mapping](microsoft-rai-v2-mapping.md) — the RAI Standard is the principle-level document Microsoft applies internally and certifies to ISO/IEC 42001 against
- [NIST AI RMF Crosswalk](nist-ai-rmf-crosswalk.md) — companion crosswalk for NIST AI RMF 1.0
- [Regulatory Mappings](regulatory-mappings.md) — FSI-specific regulatory crosswalk

---

*Updated: May 2026 | Version: v1.6.2 | ISO/IEC 42001 Mapping Last Verified: May 2026*
