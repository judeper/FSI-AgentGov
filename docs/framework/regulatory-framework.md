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

- 6-year retention + 1 year readily accessible
- All communications with customers
- All agent outputs and decisions
- Approval and supervisory records

**Applicable Controls:**

| Control | Requirement | Mapping |
|---------|-------------|---------|
| [1.7](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) | Comprehensive Audit Logging | 6-year retention + 1 year accessible |
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
- **Zone 3:** Maintain 6-year + 1 year accessible audit logs, comprehensive real-time monitoring, immediate incident escalation

---

### FINRA Rule 3110 — Supervision

**Overview:** Requires written policies and procedures for supervision of agents and AI technologies.

**Key Requirements:**

1. Written supervisory procedures
2. Qualified supervisor assignment
3. Ongoing supervision and review
4. Documentation of supervisory activities

**Applicable Controls:**

| Control | Requirement | Mapping |
|---------|-------------|---------|
| [2.3](../controls/pillar-2-management/2.3-change-management-and-release-planning.md) | Change Management | Change control and approval |
| [2.5](../controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md) | Testing and Validation | QA before production |
| [2.6](../controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md) | Model Risk Management | SR 11-7 alignment |
| [2.11](../controls/pillar-2-management/2.11-bias-testing-and-fairness-assessment-finra-notice-25-07-sr-11-7-alignment.md) | Bias Testing | Fairness assessment |
| [2.12](../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) | Supervision and Oversight | Define supervisory procedures |
| [2.17](../controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md) | Multi-Agent Orchestration Limits | Supervise agent interactions |
| [2.18](../controls/pillar-2-management/2.18-automated-conflict-of-interest-testing.md) | Conflict of Interest Testing | Test for recommendation biases |
| [3.3](../controls/pillar-3-reporting/3.3-compliance-and-regulatory-reporting.md) | Compliance Reporting | Supervision documentation |

**Zone Requirements:**

- **Zone 1:** No formal supervision required
- **Zone 2:** Basic supervisory procedures, quarterly compliance reviews, annual testing
- **Zone 3:** Comprehensive supervision, real-time monitoring, mandatory incident escalation, monthly compliance certification

---

### FINRA Regulatory Notice 25-07 — AI Governance

!!! info "RFC Status"
    FINRA Regulatory Notice 25-07 is a **Request for Comment (RFC)** with comment period
    extending to **July 2025**. Topics described are proposed guidance, not final rules.

**Overview:** Guidance on model risk management considerations for AI and algorithmic systems. Topics include validation, monitoring, bias, and governance.

**Key Topics:**

1. **Model Validation** — Independent testing, performance baseline, bias testing
2. **Ongoing Monitoring** — Performance tracking, anomaly detection, executive escalation
3. **Model Governance** — Committee oversight, change control, incident response

**Applicable Controls:**

| Control | Topic | Mapping |
|---------|-------|---------|
| [1.6](../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md) | DSPM for AI | Data handling governance |
| [1.8](../controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md) | Runtime Protection | Ongoing monitoring and alerting |
| [1.21](../controls/pillar-1-security/1.21-adversarial-input-logging.md) | Adversarial Input Logging | Monitor for manipulation attempts |
| [2.6](../controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md) | Model Risk Management | Formal framework per SR 11-7 |
| [2.11](../controls/pillar-2-management/2.11-bias-testing-and-fairness-assessment-finra-notice-25-07-sr-11-7-alignment.md) | Bias Testing | Quarterly fairness assessment |
| [2.12](../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) | Supervision | Governance procedures |
| [2.16](../controls/pillar-2-management/2.16-rag-source-integrity-validation.md) | RAG Source Integrity | Validate knowledge source quality |
| [2.17](../controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md) | Multi-Agent Orchestration | Govern agent interactions |
| [2.20](../controls/pillar-2-management/2.20-adversarial-testing-and-red-team-framework.md) | Adversarial Testing | Red team framework |
| [3.2](../controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md) | Usage Analytics | Performance monitoring |
| [3.10](../controls/pillar-3-reporting/3.10-hallucination-feedback-loop.md) | Hallucination Feedback Loop | Monitor output accuracy |

**Framework Approach:** The framework treats agents as models requiring governance aligned with SR 11-7 principles.

---

### SEC Rule 17a-3/4 — Recordkeeping

**Overview:** Requires SEC-registered firms to maintain records of all transactions and communications for 6 years + 3 years accessible.

**Record Categories:**

- **Agent Communications:** All user interactions, outputs, decisions (6 years + 3 years accessible)
- **Transaction Records:** If agent processes transactions, provides advice, executes trades (6 years + 3 years accessible)
- **Governance Records:** Approvals, change logs, incident reports, validation results (6 years minimum)

**Applicable Controls:**

| Control | Requirement | Mapping |
|---------|-------------|---------|
| [1.7](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) | Comprehensive Audit Logging | 6-year + 3-year accessible retention |
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
| [2.11](../controls/pillar-2-management/2.11-bias-testing-and-fairness-assessment-finra-notice-25-07-sr-11-7-alignment.md) | Bias Testing | Fairness validation |
| [2.16](../controls/pillar-2-management/2.16-rag-source-integrity-validation.md) | RAG Source Integrity | Input data validation |
| [3.2](../controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md) | Usage Analytics | Performance monitoring |
| [3.10](../controls/pillar-3-reporting/3.10-hallucination-feedback-loop.md) | Hallucination Feedback | Output quality monitoring |

**Applicability:**

- National banks (OCC)
- State member banks (Federal Reserve)
- State non-member banks (FDIC applies interagency guidance)

---

## Regulation-Zone Mapping

### FINRA Examination Focus by Zone

| Zone | FINRA Focus | Key Controls | Examination Depth |
|------|-------------|--------------|-------------------|
| Zone 1 | None | N/A | None |
| Zone 2 | Supervisory controls | Rule 3110 | Moderate |
| Zone 3 | Complete oversight | Rules 3110, 4511, Notice 25-07 | Comprehensive |

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
3. Control 2.11 (Bias Testing) — FINRA 25-07
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
| FINRA 25-07 | 11 controls | AI governance |
| SEC 17a-3/4 | 8 controls | Recordkeeping |
| SOX 302/404 | 6 controls | Internal controls |
| GLBA 501(b) | 6 controls | Safeguards |
| OCC 2011-12 / SR 11-7 | 6 controls | Model risk |

**Total:** 61 controls across 4 pillars providing mapped coverage to primary US financial regulations.

!!! note
    Coverage indicates which framework controls address aspects of each regulation. Actual compliance requires implementation, validation, and ongoing maintenance.

---

*FSI Agent Governance Framework v1.2 - January 2026*
