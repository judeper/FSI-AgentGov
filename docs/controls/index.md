# Control Catalog

Complete catalog of 60 governance controls for Microsoft 365 AI agents.

---

## Overview

The Control Catalog provides detailed requirements for each governance control. Controls are organized by pillar and include:

- **Control objective** — What the control achieves
- **Regulatory relevance** — Which regulations the control supports
- **Zone requirements** — How the control applies by zone
- **Implementation links** — References to playbooks for step-by-step procedures

---

## Quick Navigation by Role

**I'm a Compliance Officer...**

- Start with [Pillar 2: Management Controls](pillar-2-management/index.md) for supervision and oversight
- Review [Regulatory Framework](../framework/regulatory-framework.md) for mappings
- Focus on: Controls 2.6, 2.11, 2.12, 2.13, 3.3

**I'm a Power Platform Admin...**

- Start with [Pillar 1: Security Controls](pillar-1-security/index.md) for DLP and access
- Review [Pillar 2: Management Controls](pillar-2-management/index.md) for environments
- Focus on: Controls 1.1, 1.5, 2.1, 2.3, 2.15

**I'm a SharePoint Admin...**

- Start with [Pillar 4: SharePoint Controls](pillar-4-sharepoint/index.md)
- Focus on: Controls 4.1-4.7

**I'm preparing for an examination...**

- Review [Evidence Standards](../reference/evidence-standards.md)
- Check applicable controls in [Regulatory Framework](../framework/regulatory-framework.md)

---

## Control Summary by Pillar

### Pillar 1: Security Controls (23)

Protect data and systems from unauthorized access and misuse.

| ID | Control Name | Zone | Regulatory |
|----|--------------|------|------------|
| [1.1](pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md) | Restrict Agent Publishing | All | FINRA 3110 |
| [1.2](pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md) | Agent Registry | 2-3 | FINRA 4511 |
| [1.3](pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md) | SharePoint Content Governance | 2-3 | GLBA |
| [1.4](pillar-1-security/1.4-advanced-connector-policies-acp.md) | Advanced Connector Policies | 2-3 | - |
| [1.5](pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) | DLP and Sensitivity Labels | All | GLBA, SOX |
| [1.6](pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md) | DSPM for AI | 3 | FINRA 25-07 |
| [1.7](pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) | Comprehensive Audit Logging | All | FINRA 4511, SEC 17a-4 |
| [1.8](pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md) | Runtime Protection | 3 | FINRA 25-07 |
| [1.9](pillar-1-security/1.9-data-retention-and-deletion-policies.md) | Data Retention | 2-3 | SEC 17a-4, FINRA 4511 |
| [1.10](pillar-1-security/1.10-communication-compliance-monitoring.md) | Communication Compliance | 3 | FINRA 3110 |
| [1.11](pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md) | Conditional Access and MFA | 2-3 | GLBA, SOX |
| [1.12](pillar-1-security/1.12-insider-risk-detection-and-response.md) | Insider Risk Detection | 3 | - |
| [1.13](pillar-1-security/1.13-sensitive-information-types-sits-and-pattern-recognition.md) | Sensitive Information Types | 2-3 | GLBA |
| [1.14](pillar-1-security/1.14-data-minimization-and-agent-scope-control.md) | Data Minimization | 2-3 | GLBA |
| [1.15](pillar-1-security/1.15-encryption-data-in-transit-and-at-rest.md) | Encryption | All | GLBA, SOX |
| [1.16](pillar-1-security/1.16-information-rights-management-irm-for-documents.md) | Information Rights Management | 2-3 | - |
| [1.17](pillar-1-security/1.17-endpoint-data-loss-prevention-endpoint-dlp.md) | Endpoint DLP | 3 | GLBA |
| [1.18](pillar-1-security/1.18-application-level-authorization-and-role-based-access-control-rbac.md) | Application-Level RBAC | 2-3 | SOX |
| [1.19](pillar-1-security/1.19-ediscovery-for-agent-interactions.md) | eDiscovery | 2-3 | SEC 17a-4 |
| [1.20](pillar-1-security/1.20-network-isolation-private-connectivity.md) | Network Isolation | 3 | - |
| [1.21](pillar-1-security/1.21-adversarial-input-logging.md) | Adversarial Input Logging | 3 | FINRA 25-07 |
| [1.22](pillar-1-security/1.22-information-barriers.md) | Information Barriers | 3 | FINRA 3110 |
| [1.23](pillar-1-security/1.23-step-up-authentication-for-agent-operations.md) | Step-Up Authentication | 3 | SOX |

[View Pillar 1 Overview](pillar-1-security/index.md)

---

### Pillar 2: Management Controls (20)

Govern agent lifecycle, risk, and operational processes.

| ID | Control Name | Zone | Regulatory |
|----|--------------|------|------------|
| [2.1](pillar-2-management/2.1-managed-environments.md) | Managed Environments | 2-3 | - |
| [2.2](pillar-2-management/2.2-environment-groups-and-tier-classification.md) | Environment Groups | 2-3 | - |
| [2.3](pillar-2-management/2.3-change-management-and-release-planning.md) | Change Management | 2-3 | SOX |
| [2.4](pillar-2-management/2.4-business-continuity-and-disaster-recovery.md) | Business Continuity | 3 | - |
| [2.5](pillar-2-management/2.5-testing-validation-and-quality-assurance.md) | Testing and Validation | 2-3 | FINRA 3110 |
| [2.6](pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md) | Model Risk Management | 3 | OCC 2011-12, SR 11-7 |
| [2.7](pillar-2-management/2.7-vendor-and-third-party-risk-management.md) | Vendor Risk Management | 2-3 | GLBA |
| [2.8](pillar-2-management/2.8-access-control-and-segregation-of-duties.md) | Segregation of Duties | 2-3 | SOX |
| [2.9](pillar-2-management/2.9-agent-performance-monitoring-and-optimization.md) | Performance Monitoring | 2-3 | FINRA 4511 |
| [2.10](pillar-2-management/2.10-patch-management-and-system-updates.md) | Patch Management | 2-3 | - |
| [2.11](pillar-2-management/2.11-bias-testing-and-fairness-assessment-finra-notice-25-07-sr-11-7-alignment.md) | Bias Testing | 3 | FINRA 25-07, SR 11-7 |
| [2.12](pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) | Supervision and Oversight | 2-3 | FINRA 3110 |
| [2.13](pillar-2-management/2.13-documentation-and-record-keeping.md) | Documentation | 2-3 | SEC 17a-4 |
| [2.14](pillar-2-management/2.14-training-and-awareness-program.md) | Training Program | All | FINRA 3110 |
| [2.15](pillar-2-management/2.15-environment-routing.md) | Environment Routing | All | - |
| [2.16](pillar-2-management/2.16-rag-source-integrity-validation.md) | RAG Source Integrity | 2-3 | FINRA 25-07 |
| [2.17](pillar-2-management/2.17-multi-agent-orchestration-limits.md) | Multi-Agent Orchestration | 3 | FINRA 3110 |
| [2.18](pillar-2-management/2.18-automated-conflict-of-interest-testing.md) | Conflict of Interest Testing | 3 | FINRA 3110 |
| [2.19](pillar-2-management/2.19-customer-ai-disclosure-and-transparency.md) | AI Disclosure | 3 | - |
| [2.20](pillar-2-management/2.20-adversarial-testing-and-red-team-framework.md) | Adversarial Testing | 3 | FINRA 25-07 |

[View Pillar 2 Overview](pillar-2-management/index.md)

---

### Pillar 3: Reporting Controls (10)

Monitor, track, and report on agent activities and compliance.

| ID | Control Name | Zone | Regulatory |
|----|--------------|------|------------|
| [3.1](pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md) | Agent Inventory | All | FINRA 4511 |
| [3.2](pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md) | Usage Analytics | 2-3 | FINRA 25-07 |
| [3.3](pillar-3-reporting/3.3-compliance-and-regulatory-reporting.md) | Compliance Reporting | 2-3 | FINRA 4511 |
| [3.4](pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) | Incident Reporting | 2-3 | GLBA |
| [3.5](pillar-3-reporting/3.5-cost-allocation-and-budget-tracking.md) | Cost Allocation | 2-3 | - |
| [3.6](pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) | Orphaned Agent Detection | 2-3 | - |
| [3.7](pillar-3-reporting/3.7-ppac-security-posture-assessment.md) | PPAC Security Posture | 2-3 | - |
| [3.8](pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md) | Copilot Hub | 2-3 | - |
| [3.9](pillar-3-reporting/3.9-microsoft-sentinel-integration.md) | Sentinel Integration | 3 | - |
| [3.10](pillar-3-reporting/3.10-hallucination-feedback-loop.md) | Hallucination Feedback | 2-3 | FINRA 25-07 |

[View Pillar 3 Overview](pillar-3-reporting/index.md)

---

### Pillar 4: SharePoint Controls (7)

SharePoint-specific governance for agent knowledge sources.

**Note:** Pillar 4 specializes the governance requirements from Pillars 1-3 for SharePoint as an agent knowledge source. Controls address SharePoint-specific implementation of data protection, access governance, and content management.

| ID | Control Name | Zone | Regulatory |
|----|--------------|------|------------|
| [4.1](pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md) | SharePoint IAG | 2-3 | GLBA |
| [4.2](pillar-4-sharepoint/4.2-site-access-reviews-and-certification.md) | Site Access Reviews | 2-3 | SOX |
| [4.3](pillar-4-sharepoint/4.3-site-and-document-retention-management.md) | Retention Management | 2-3 | SEC 17a-4 |
| [4.4](pillar-4-sharepoint/4.4-guest-and-external-user-access-controls.md) | External User Controls | 2-3 | GLBA |
| [4.5](pillar-4-sharepoint/4.5-sharepoint-security-and-compliance-monitoring.md) | Security Monitoring | 2-3 | - |
| [4.6](pillar-4-sharepoint/4.6-grounding-scope-governance.md) | Grounding Scope | 2-3 | FINRA 4511 |
| [4.7](pillar-4-sharepoint/4.7-microsoft-365-copilot-data-governance.md) | M365 Copilot Data Governance | 2-3 | - |

[View Pillar 4 Overview](pillar-4-sharepoint/index.md)

---

## Control Implementation Status

Use this table to track implementation progress:

| Status | Meaning |
|--------|---------|
| Not Started | Control not yet implemented |
| In Progress | Implementation underway |
| Implemented | Control configured and operational |
| Verified | Control tested and verified effective |

---

## Related Sections

- [Framework](../framework/index.md) — Governance principles and structure
- [Playbooks](../playbooks/index.md) — Step-by-step implementation procedures
- [Reference](../reference/index.md) — Supporting materials

---

*FSI Agent Governance Framework v1.2 - January 2026*
