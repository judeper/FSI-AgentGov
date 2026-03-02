# Regulatory Framework

Comprehensive mapping of framework controls to US financial services regulatory requirements.

---

## Overview

This document maps the FSI Agent Governance Framework controls to applicable US financial regulations. Organizations should use this mapping to prioritize control implementation based on their regulatory profile.

!!! warning "Disclaimer"
    This mapping is provided for informational purposes and does not constitute legal or regulatory advice. Regulatory interpretations vary by institution type and use case. Consult legal counsel for specific compliance requirements.

---

## Primary US Financial Regulations

### FINRA Rule 4511 — Books and Records

**Overview:** Requires firms to maintain records of all agent activities and communications.

**Key Requirements:**

- Retention periods vary by record type (see matrix below)
- All communications with customers
- All agent outputs and decisions
- Approval and supervisory records

!!! warning "Record Type Matters for Retention"
    Retention periods vary by record type. Agent conversation logs typically qualify as "communications" with 3-year retention under SEC 17a-4(b)(4), not the 6-year period for financial/customer records.

### Retention Period Matrix

| Record Type | Retention | Regulation | Access Requirement |
|-------------|-----------|------------|--------------------|
| **Communications** (agent logs, chat, email) | 3 years | SEC 17a-4(b)(4) | First 2 years readily accessible |
| **Accounting/Financial Records** | 6 years | SEC 17a-4(a) | First 2 years readily accessible |
| **Customer Account Records** | 6 years after account close | SEC 17a-4(c)(e)(5) | First 2 years readily accessible |
| **FINRA-Specific Records** (no SEC period) | 6 years | FINRA 4511(b) | First 2 years easily accessible |
| **Partnership/Corporate Records** | Life of enterprise + 3 years | SEC 17a-4(d) | Readily accessible |
| **Audit Workpapers** | 7 years | SOX 802 | Accessible for examination |

!!! info "Agent Logs as Communications"
    Agent conversation logs (prompts, responses, interaction history) typically fall under the 3-year **communications** retention period per SEC 17a-4(b)(4), not the 6-year financial records period. However, if agent interactions generate or modify financial records, those outputs follow the applicable 6-year period.

**Applicable Controls:**

| Control | Requirement | Mapping |
|---------|-------------|---------|
| [1.7](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) | Comprehensive Audit Logging | Retention per record type (3 years for communications, 6 years for financial records) |
| [1.9](../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md) | Data Retention and Deletion | Retention policies per FINRA timeline |
| [1.21](../controls/pillar-1-security/1.21-adversarial-input-logging.md) | Adversarial Input Logging | Record security incidents and attacks |
| [2.12](../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) | Supervision and Oversight | Compliance Officer oversight |
| [2.13](../controls/pillar-2-management/2.13-documentation-and-record-keeping.md) | Documentation and Record Keeping | All records documented |
| [3.1](../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md) | Agent Inventory | Central registry of all agents |
| [3.3](../controls/pillar-3-reporting/3.3-compliance-and-regulatory-reporting.md) | Compliance and Regulatory Reporting | Regular compliance reports |
| [3.4](../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) | Incident Reporting | Document all incidents |
| [3.10](../controls/pillar-3-reporting/3.10-hallucination-feedback-loop.md) | Hallucination Feedback Loop | Record and track accuracy issues |

**Zone Requirements:**

- **Zone 2:** Maintain 1-year audit logs, document approval process, monthly compliance reviews
- **Zone 3:** Maintain audit logs per retention matrix (3 years for communications, 6+ years for financial records; first 2 years readily accessible), comprehensive real-time monitoring, immediate incident escalation

---

### FINRA Rule 3110 — Supervision

**Overview:** Requires written policies and procedures for supervision of agents and AI technologies.

**Key Requirements:**

1. Written supervisory procedures
2. Qualified supervisor assignment
3. Ongoing supervision and review
4. Documentation of supervisory activities

### FINRA Rule 3120 — Supervisory Control System

**Overview:** Requires annual testing and verification of supervisory procedures established under Rule 3110.

**Key Requirements:**

1. Annual testing of supervisory control systems
2. Documented testing procedures and results
3. Escalation of identified exceptions
4. Remediation of control deficiencies

**AI Agent Governance Application:**

| Test Area | Annual Testing Requirement |
|-----------|---------------------------|
| WSP Adherence | Verify AI agent supervision procedures are followed |
| HITL Functionality | Test that human review triggers function correctly |
| Escalation Procedures | Verify escalation routing works as designed |
| Review Queue SLA | Audit that reviews complete within target timeframes |
| Sampling Protocol | Confirm sampling rates match policy |

See: [FINRA Rule 3120](https://www.finra.org/rules-guidance/rulebooks/finra-rules/3120)

**Applicable Controls:**

| Control | Requirement | Mapping |
|---------|-------------|---------|
| [2.3](../controls/pillar-2-management/2.3-change-management-and-release-planning.md) | Change Management | Change control and approval |
| [2.5](../controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md) | Testing and Validation | QA before production |
| [2.6](../controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md) | Model Risk Management | SR 11-7 alignment |
| [2.11](../controls/pillar-2-management/2.11-bias-testing-and-fairness-assessment.md) | Bias Testing | Fairness assessment |
| [2.12](../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) | Supervision and Oversight | Define supervisory procedures |
| [2.17](../controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md) | Multi-Agent Orchestration Limits | Supervise agent interactions |
| [2.18](../controls/pillar-2-management/2.18-automated-conflict-of-interest-testing.md) | Conflict of Interest Testing | Test for recommendation biases |
| [3.3](../controls/pillar-3-reporting/3.3-compliance-and-regulatory-reporting.md) | Compliance Reporting | Supervision documentation |

**Zone Requirements:**

- **Zone 1:** No formal supervision required
- **Zone 2:** Basic supervisory procedures, quarterly compliance reviews, annual testing
- **Zone 3:** Comprehensive supervision, real-time monitoring, mandatory incident escalation, monthly compliance certification

---

### FINRA AI Supervision Requirements

!!! warning "FINRA Notice 25-07 Clarification"
    FINRA Regulatory Notice 25-07 (April 2025) addresses **workplace modernization rules**, not AI governance. For AI supervision requirements, refer to **FINRA Regulatory Notice 24-09** (Gen AI guidance), **FINRA Rule 3110** (Supervision), **FINRA Rule 2111** (Suitability), and **FINRA's Annual Regulatory Oversight Report** for current AI examination priorities.

!!! info "FINRA Regulatory Notice 24-09 (June 2024)"
    FINRA Notice 24-09 provides official guidance on generative AI and large language model (LLM) obligations. Key points:

    - **Technology-neutral principle:** Existing FINRA rules apply equally to AI-generated content
    - **Rule 3110 supervision:** Firms must establish supervisory procedures for AI tools
    - **Rule 2210 communications:** AI-generated customer communications must meet content standards
    - **Model risk management:** Firms should apply appropriate governance to AI systems

    See: [FINRA Regulatory Notice 24-09](https://www.finra.org/rules-guidance/notices/24-09)

### FINRA 2026 Annual Regulatory Oversight Report (December 2025)

The 2026 Annual Regulatory Oversight Report contains FINRA's most detailed AI agent supervision guidance to date, with a dedicated section on generative AI and agentic systems.

!!! tip "Key AI Agent Guidance from 2026 Report"
    | Topic | Requirement | Framework Control |
    |-------|-------------|-------------------|
    | **AI as Supervisory Function** | Document WSPs for AI supervision substitution; define boundaries for AI vs. human oversight | [2.12](../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) |
    | **Audit Trail Completeness** | Retain prompts, model state, and reasoning chain—not just outputs | [1.7](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) |
    | **Decision Reconstruction** | Demonstrate how agents reached conclusions for examination | [1.7](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md), [2.13](../controls/pillar-2-management/2.13-documentation-and-record-keeping.md) |
    | **Agent Autonomy Limits** | Dedicated supervisory procedures for autonomous AI agents | [2.12](../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md), [2.17](../controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md) |
    | **Rule 3120 Testing** | Annual testing of AI supervisory controls per Rule 3120 | [2.12](../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) |

    See: [FINRA 2026 Annual Regulatory Oversight Report](https://www.finra.org/rules-guidance/guidance/reports/2026-finra-annual-regulatory-oversight-report)

**Overview:** FINRA's AI supervision requirements derive from existing rules that apply to associated persons' use of AI tools for customer communications and recommendations.

**Key Requirements:**

1. **Written Supervisory Procedures (Rule 3110)** — Document AI tool approval, supervisory review, escalation paths
2. **Suitability (Rule 2111)** — Validate AI recommendations meet suitability standards
3. **Recordkeeping (Rule 4511)** — Retain AI-generated communications and agent logs

**Applicable Controls:**

| Control | Topic | Mapping |
|---------|-------|---------|
| [1.7](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) | Comprehensive Audit Logging | Records retention for AI communications |
| [2.5](../controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md) | Testing and Validation | Agent accuracy testing |
| [2.6](../controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md) | Model Risk Management | Formal framework per SR 11-7 |
| [2.11](../controls/pillar-2-management/2.11-bias-testing-and-fairness-assessment.md) | Bias Testing | Fairness assessment per SR 11-7 |
| [2.12](../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) | Supervision | Written supervisory procedures |
| [3.2](../controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md) | Usage Analytics | Performance monitoring |
| [3.10](../controls/pillar-3-reporting/3.10-hallucination-feedback-loop.md) | Hallucination Feedback Loop | Monitor output accuracy |

**Framework Approach:** The framework applies FINRA's existing supervision principles to AI agents, treating them as tools requiring documented procedures, ongoing monitoring, and supervisory oversight.

---

### SEC Rule 17a-3/4 — Recordkeeping

**Overview:** Requires SEC-registered firms to maintain records of all transactions and communications. Retention periods vary by record type — see the Retention Period Matrix in the FINRA 4511 section above for details.

**Record Categories:**

- **Agent Communications:** All user interactions, outputs, decisions (3 years per SEC 17a-4(b)(4), first 2 years readily accessible)
- **Transaction Records:** If agent processes transactions, provides advice, executes trades (6 years per SEC 17a-4(a), first 2 years readily accessible)
- **Governance Records:** Approvals, change logs, incident reports, validation results (6 years minimum per FINRA 4511(b))

**Applicable Controls:**

| Control | Requirement | Mapping |
|---------|-------------|---------|
| [1.7](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) | Comprehensive Audit Logging | Retention per record type (3-6 years), first 2 years readily accessible |
| [1.9](../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md) | Data Retention | Retention policies enforced |
| [1.19](../controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md) | eDiscovery for Agent Interactions | Search and export for regulators |
| [2.13](../controls/pillar-2-management/2.13-documentation-and-record-keeping.md) | Documentation and Record Keeping | All records documented |
| [3.1](../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md) | Agent Inventory | Registry of agents as records |
| [3.3](../controls/pillar-3-reporting/3.3-compliance-and-regulatory-reporting.md) | Compliance Reporting | Evidence retention |
| [4.6](../controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md) | Grounding Scope Governance | Knowledge source records |
| [4.7](../controls/pillar-4-sharepoint/4.7-microsoft-365-copilot-data-governance.md) | M365 Copilot Data Governance | M365 Copilot usage logging |

---

### SOX Sections 302/404 — Internal Controls

**Overview:** Requires public companies to maintain effective internal controls over financial reporting.

**Key Requirements:**

- Management certification of internal controls (302)
- Assessment of internal control effectiveness (404)
- Audit trail for financial data access
- Change control for systems affecting financials

**Applicable Controls:**

| Control | Requirement | Mapping |
|---------|-------------|---------|
| [1.7](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) | Comprehensive Audit Logging | Audit trail for all access |
| [1.11](../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md) | Conditional Access and MFA | Access control |
| [1.18](../controls/pillar-1-security/1.18-application-level-authorization-and-role-based-access-control-rbac.md) | Application-Level RBAC | Role-based access |
| [2.3](../controls/pillar-2-management/2.3-change-management-and-release-planning.md) | Change Management | Change control procedures |
| [2.8](../controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md) | Segregation of Duties | SoD controls |
| [3.3](../controls/pillar-3-reporting/3.3-compliance-and-regulatory-reporting.md) | Compliance Reporting | Control effectiveness evidence |

**Zone Requirements:**

- **Zone 1:** Not applicable
- **Zone 2:** Limited scope if agent touches financial data
- **Zone 3:** Full SOX compliance for agents affecting financial reporting

!!! info "AI System Coverage"
    SOX does not explicitly address AI or automated systems. AI agents affecting financial reporting are governed implicitly through existing ICFR frameworks. The PCAOB is conducting research to determine whether new standards are needed for AI in audits and financial reporting (July 2024 Spotlight on GenAI).

---

### GLBA Section 501(b) — Safeguards Rule

**Overview:** Requires financial institutions to protect the security and confidentiality of customer information.

**Key Requirements:**

- Administrative, technical, and physical safeguards
- Risk assessment and management
- Service provider oversight
- Incident response procedures

**Applicable Controls:**

| Control | Requirement | Mapping |
|---------|-------------|---------|
| [1.5](../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) | DLP and Sensitivity Labels | Data protection |
| [1.11](../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md) | Conditional Access and MFA | Access safeguards |
| [1.15](../controls/pillar-1-security/1.15-encryption-data-in-transit-and-at-rest.md) | Encryption | Technical safeguards |
| [1.17](../controls/pillar-1-security/1.17-endpoint-data-loss-prevention-endpoint-dlp.md) | Endpoint DLP | Endpoint protection |
| [2.7](../controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md) | Vendor Risk Management | Service provider oversight |
| [3.4](../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) | Incident Reporting | Incident response |

---

### OCC 2011-12 / Federal Reserve SR 11-7 — Model Risk Management

**Overview:** Guidance on model risk management for banks using models in decision-making.

**Key Requirements:**

1. Model validation and testing
2. Ongoing monitoring and performance tracking
3. Model governance and documentation
4. Independent validation

**Applicable Controls:**

| Control | Requirement | Mapping |
|---------|-------------|---------|
| [2.5](../controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md) | Testing and Validation | Model testing |
| [2.6](../controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md) | Model Risk Management | Comprehensive MRM framework |
| [2.11](../controls/pillar-2-management/2.11-bias-testing-and-fairness-assessment.md) | Bias Testing | Fairness validation |
| [2.16](../controls/pillar-2-management/2.16-rag-source-integrity-validation.md) | RAG Source Integrity | Input data validation |
| [3.2](../controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md) | Usage Analytics | Performance monitoring |
| [3.10](../controls/pillar-3-reporting/3.10-hallucination-feedback-loop.md) | Hallucination Feedback | Output quality monitoring |

**Applicability:**

- National banks (OCC)
- State member banks (Federal Reserve)
- State non-member banks (FDIC applies interagency guidance)

---

### CFTC Rule 1.31 — Recordkeeping for Swap Dealers

**Overview:** CFTC Rule 1.31 requires swap dealers and major swap participants to maintain records of transactions, communications, and related activities in a format that is identifiable and searchable.

**AI Agent Relevance:** Agent interactions in commodities trading contexts — including automated communications, trade-related outputs, and decision logs — may fall within 1.31 record-keeping scope. Organizations subject to CFTC oversight should consider mapping agent governance controls (particularly Controls 1.7, 1.9, and 2.13) to their 1.31 record-keeping requirements. Implementation specifics depend on institutional use of agents in CFTC-regulated activities.

---

## Regulation-Zone Mapping

### FINRA Examination Focus by Zone

| Zone | FINRA Focus | Key Controls | Examination Depth |
|------|-------------|--------------|-------------------|
| Zone 1 | None | N/A | None |
| Zone 2 | Supervisory controls | Rule 3110 | Moderate |
| Zone 3 | Complete oversight | Rules 3110, 4511 | Comprehensive |

### SEC Examination Focus by Zone

| Zone | SEC Focus | Key Controls | Examination Depth |
|------|-----------|--------------|-------------------|
| Zone 1 | None | N/A | None |
| Zone 2 | Data handling | Reg S-P | Limited |
| Zone 3 | Complete compliance | Rules 17a-3/4, AI disclosure | Comprehensive |

### SOX Internal Controls by Zone

| Zone | SOX Scope | Documentation | Testing |
|------|-----------|---------------|---------|
| Zone 1 | None | N/A | None |
| Zone 2 | Limited | Process docs | Annual |
| Zone 3 | Full | All controls | Annual + Continuous |

---

## Regulatory Priority by Institution Type

### Broker-Dealers (FINRA/SEC)

**Priority Controls:**

1. Control 2.12 (Supervision) — FINRA 3110
2. Control 1.7 (Audit Logging) — FINRA 4511, SEC 17a-4
3. Control 2.11 (Bias Testing) — FINRA 3110 (supervision of AI tools)
4. Control 3.3 (Compliance Reporting) — Examination readiness

### Banks (OCC/Fed)

**Priority Controls:**

1. Control 2.6 (Model Risk Management) — OCC 2011-12, SR 11-7
2. Control 2.11 (Bias Testing) — Fair lending
3. Control 1.7 (Audit Logging) — Records requirements
4. Control 1.5 (DLP) — GLBA 501(b)

### Investment Advisers (SEC)

**Priority Controls:**

1. Control 2.12 (Supervision) — Reg BI
2. Control 2.19 (AI Disclosure) — Client communication
3. Control 1.7 (Audit Logging) — SEC 17a-4
4. Control 3.1 (Agent Inventory) — Examination readiness

### Credit Unions (NCUA)

**Priority Controls:**

1. Control 1.5 (DLP) — Part 748 security program
2. Control 1.7 (Audit Logging) — Records requirements
3. Control 2.8 (Segregation of Duties) — Internal controls
4. Control 3.4 (Incident Reporting) — Security program

---

## State-Level Regulations (For Awareness)

The following state regulations may apply but are beyond the primary scope of this framework:

| Regulation | Jurisdiction | Focus | Framework Relevance |
|------------|--------------|-------|---------------------|
| **NYDFS Part 500** | New York | Cybersecurity | Controls 1.11, 1.15, 3.4 |
| **CCPA/CPRA** | California | Consumer privacy | Controls 1.5, 1.9, 4.4 |
| **Colorado AI Act** | Colorado | High-risk AI | Controls 2.6, 2.11, 2.19 |

Organizations should conduct separate analysis for state-specific requirements.

---

## Examination Readiness Checklist

### Pre-Examination Preparation

- [ ] Agent inventory current and complete (Control 3.1)
- [ ] Audit logs accessible for required retention period (Control 1.7)
- [ ] Supervisory procedures documented (Control 2.12)
- [ ] Change records available (Control 2.3)
- [ ] Incident reports filed (Control 3.4)
- [ ] Training records current (Control 2.14)

### Common Examiner Requests

| Request | Control | Documentation |
|---------|---------|---------------|
| List of all AI agents | 3.1 | Agent inventory |
| Agent approval records | 2.12 | Governance committee minutes |
| Audit logs for specific agent | 1.7 | Purview Audit export |
| Supervisory procedures | 2.12 | Written procedures document |
| Incident history | 3.4 | Incident reports |
| Testing documentation | 2.5 | Test results and validation |

---

## Framework Coverage Summary

| Regulation | Controls Mapped | Framework Coverage |
|------------|-----------------|-------------------|
| FINRA 4511 | 9 controls | Books and records |
| FINRA 3110 | 8 controls | Supervision |
| FINRA 3110/2111 | 11 controls | AI supervision |
| SEC 17a-3/4 | 8 controls | Recordkeeping |
| SOX 302/404 | 6 controls | Internal controls |
| GLBA 501(b) | 6 controls | Safeguards |
| OCC 2011-12 / SR 11-7 | 6 controls | Model risk |
| CFTC 1.31 | 3 controls | Recordkeeping |

**Total:** 71 controls across 4 pillars providing mapped coverage to primary US financial regulations.

!!! note
    Coverage indicates which framework controls address aspects of each regulation. Actual compliance requires implementation, validation, and ongoing maintenance.

---

*FSI Agent Governance Framework v1.2.51 - February 2026*
