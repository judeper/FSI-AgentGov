# FSI Agent Governance Framework - Control Index

## Complete Control Reference (72 Controls)

This directory contains comprehensive control documentation for the FSI Agent Governance Framework across four pillars.

---

## Pillar 1: Security Controls (28 Controls)

| Control ID | Control Name | Implementation |
|-----------|----------|----------------|
| 1.1 | [Restrict Agent Publishing by Authorization](pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md) | Portal / PowerShell, [Hardening Baseline](../playbooks/advanced-implementations/configuration-hardening-baseline/index.md), [UASD](../playbooks/advanced-implementations/unrestricted-agent-sharing-detector/index.md) |
| 1.2 | [Agent Registry and Integrated Apps Management](pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md) | Portal / PowerShell |
| 1.3 | [SharePoint Content Governance and Permissions](pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md) | Portal / PowerShell |
| 1.4 | [Advanced Connector Policies (ACP)](pillar-1-security/1.4-advanced-connector-policies-acp.md) | Portal / PowerShell, [FUS](../reference/solutions-index.md#file-upload-security-configurator), [SDM](../reference/solutions-index.md#scope-drift-monitor) |
| 1.5 | [Data Loss Prevention (DLP) and Sensitivity Labels](pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) | Portal / PowerShell, [Deny Event Correlation](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/deny-event-correlation-report), [SDM](../reference/solutions-index.md#scope-drift-monitor), [MTR](../reference/solutions-index.md#mime-type-restrictions-for-file-uploads) |
| 1.6 | [Microsoft Purview: DSPM for AI](pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md) | Portal |
| 1.7 | [Comprehensive Audit Logging and Compliance](pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) | Portal / PowerShell, [Deny Event Correlation](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/deny-event-correlation-report), [Hardening Baseline](../playbooks/advanced-implementations/configuration-hardening-baseline/index.md), [ACM](../reference/solutions-index.md#audit-compliance-manager), [FSW](../reference/solutions-index.md#finra-supervision-workflow), [CSI](../reference/solutions-index.md#cross-solution-integration) |
| 1.8 | [Runtime Protection and External Threat Detection](pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md) | Portal, [Hardening Baseline](../playbooks/advanced-implementations/configuration-hardening-baseline/index.md), [CMM](../reference/solutions-index.md#content-moderation-governance-monitor), [FUS](../reference/solutions-index.md#file-upload-security-configurator), [CSI](../reference/solutions-index.md#cross-solution-integration) |
| 1.9 | [Data Retention and Deletion Policies](pillar-1-security/1.9-data-retention-and-deletion-policies.md) | Portal / PowerShell |
| 1.10 | [Communication Compliance Monitoring](pillar-1-security/1.10-communication-compliance-monitoring.md) | Portal, [FSW](../reference/solutions-index.md#finra-supervision-workflow), [MTR](../reference/solutions-index.md#mime-type-restrictions-for-file-uploads) |
| 1.11 | [Conditional Access and Phishing-Resistant MFA](pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md) | Portal / PowerShell, [SSC](../reference/solutions-index.md#session-security-configurator), [CAA](../reference/solutions-index.md#conditional-access-automation), [CSI](../reference/solutions-index.md#cross-solution-integration), [MTR](../reference/solutions-index.md#mime-type-restrictions-for-file-uploads) |
| 1.12 | [Insider Risk Detection and Response](pillar-1-security/1.12-insider-risk-detection-and-response.md) | Portal |
| 1.13 | [Sensitive Information Types (SITs) and Pattern Recognition](pillar-1-security/1.13-sensitive-information-types-sits-and-pattern-recognition.md) | Portal / PowerShell, [MTR](../reference/solutions-index.md#mime-type-restrictions-for-file-uploads) |
| 1.14 | [Data Minimization and Agent Scope Control](pillar-1-security/1.14-data-minimization-and-agent-scope-control.md) | Portal, [CMM](../reference/solutions-index.md#content-moderation-governance-monitor), [FUS](../reference/solutions-index.md#file-upload-security-configurator), [SDM](../reference/solutions-index.md#scope-drift-monitor), [CSI](../reference/solutions-index.md#cross-solution-integration), [MTR](../reference/solutions-index.md#mime-type-restrictions-for-file-uploads) |
| 1.15 | [Encryption: Data in Transit and at Rest](pillar-1-security/1.15-encryption-data-in-transit-and-at-rest.md) | Portal |
| 1.16 | [Information Rights Management (IRM) for Documents](pillar-1-security/1.16-information-rights-management-irm-for-documents.md) | Portal / PowerShell |
| 1.17 | [Endpoint Data Loss Prevention (Endpoint DLP)](pillar-1-security/1.17-endpoint-data-loss-prevention-endpoint-dlp.md) | Portal |
| 1.18 | [Application-Level Authorization and Role-Based Access Control (RBAC)](pillar-1-security/1.18-application-level-authorization-and-role-based-access-control-rbac.md) | Portal / PowerShell, [Hardening Baseline](../playbooks/advanced-implementations/configuration-hardening-baseline/index.md), [ASARD](../reference/solutions-index.md#agent-sharing-access-restriction-detector), [CAA](../reference/solutions-index.md#conditional-access-automation) |
| 1.19 | [eDiscovery for Agent Interactions](pillar-1-security/1.19-ediscovery-for-agent-interactions.md) | Portal / PowerShell |
| 1.20 | [Network Isolation and Private Connectivity](pillar-1-security/1.20-network-isolation-private-connectivity.md) | Portal |
| 1.21 | [Adversarial Input Logging](pillar-1-security/1.21-adversarial-input-logging.md) | Portal |
| 1.22 | [Information Barriers for AI Agents](pillar-1-security/1.22-information-barriers.md) | Portal / PowerShell |
| 1.23 | [Step-Up Authentication for AI Agent Operations](pillar-1-security/1.23-step-up-authentication-for-agent-operations.md) | Portal, [SSC](../reference/solutions-index.md#session-security-configurator), [CAA](../reference/solutions-index.md#conditional-access-automation), [ITE](../reference/solutions-index.md#inactivity-timeout-enforcement), [CSI](../reference/solutions-index.md#cross-solution-integration) |
| 1.24 | [Defender AI Security Posture Management (AI-SPM)](pillar-1-security/1.24-defender-ai-security-posture-management.md) | Portal |
| 1.25 | [MIME Type Restrictions for File Uploads](pillar-1-security/1.25-mime-type-restrictions.md) | PowerShell + Portal, [MTR](../reference/solutions-index.md#mime-type-restrictions-for-file-uploads) |
| 1.26 | [Agent File Upload and File Analysis Restrictions](pillar-1-security/1.26-agent-file-upload-and-file-analysis-restrictions.md) | Portal / PowerShell |
| 1.27 | [AI Agent Content Moderation Enforcement](pillar-1-security/1.27-ai-agent-content-moderation-enforcement.md) | Portal / PowerShell, [CMM](../reference/solutions-index.md#content-moderation-governance-monitor) |
| 1.28 | [Policy-Based Agent Publishing Restrictions](pillar-1-security/1.28-policy-based-agent-publishing-restrictions.md) | Portal / PowerShell |

## Pillar 2: Management Controls (24 Controls)

| Control ID | Control Name | Implementation |
|-----------|----------|----------------|
| 2.1 | [Managed Environments](pillar-2-management/2.1-managed-environments.md) | Portal / PowerShell, [ELM](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/environment-lifecycle-management), [Hardening Baseline](../playbooks/advanced-implementations/configuration-hardening-baseline/index.md), [SoDD](../reference/solutions-index.md#segregation-of-duties-detector) |
| 2.2 | [Environment Groups and Tier Classification](pillar-2-management/2.2-environment-groups-and-tier-classification.md) | Portal / PowerShell, [ELM](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/environment-lifecycle-management) |
| 2.3 | [Change Management and Release Planning](pillar-2-management/2.3-change-management-and-release-planning.md) | Portal / PowerShell, [Message Center Monitor](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/message-center-monitor), [Pipeline Cleanup](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/pipeline-governance-cleanup), [SoDD](../reference/solutions-index.md#segregation-of-duties-detector) |
| 2.4 | [Business Continuity and Disaster Recovery](pillar-2-management/2.4-business-continuity-and-disaster-recovery.md) | Portal / PowerShell |
| 2.5 | [Testing, Validation, and Quality Assurance](pillar-2-management/2.5-testing-validation-and-quality-assurance.md) | Portal / PowerShell |
| 2.6 | [Model Risk Management (Alignment with OCC 2011-12/SR 11-7)](pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md) | Portal |
| 2.7 | [Vendor and Third-Party Risk Management](pillar-2-management/2.7-vendor-and-third-party-risk-management.md) | Portal |
| 2.8 | [Access Control and Segregation of Duties](pillar-2-management/2.8-access-control-and-segregation-of-duties.md) | Portal / PowerShell, [ASARD](../reference/solutions-index.md#agent-sharing-access-restriction-detector), [SoDD](../reference/solutions-index.md#segregation-of-duties-detector) |
| 2.9 | [Agent Performance Monitoring and Optimization](pillar-2-management/2.9-agent-performance-monitoring-and-optimization.md) | Portal, [AOF](../reference/solutions-index.md#agent-usage-performance-workbook) |
| 2.10 | [Patch Management and System Updates](pillar-2-management/2.10-patch-management-and-system-updates.md) | Portal, [Message Center Monitor](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/message-center-monitor) |
| 2.11 | [Bias Testing and Fairness Assessment](pillar-2-management/2.11-bias-testing-and-fairness-assessment.md) | Portal |
| 2.12 | [Supervision and Oversight (FINRA Rule 3110)](pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) | Portal, [FSW](../reference/solutions-index.md#finra-supervision-workflow) |
| 2.13 | [Documentation and Record Keeping](pillar-2-management/2.13-documentation-and-record-keeping.md) | Portal |
| 2.14 | [Training and Awareness Program](pillar-2-management/2.14-training-and-awareness-program.md) | Portal |
| 2.15 | [Environment Routing and Auto-Provisioning](pillar-2-management/2.15-environment-routing.md) | Portal / PowerShell, [ELM](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/environment-lifecycle-management) |
| 2.16 | [RAG Source Integrity Validation](pillar-2-management/2.16-rag-source-integrity-validation.md) | Portal |
| 2.17 | [Multi-Agent Orchestration Limits](pillar-2-management/2.17-multi-agent-orchestration-limits.md) | Portal |
| 2.18 | [Automated Conflict of Interest Testing](pillar-2-management/2.18-automated-conflict-of-interest-testing.md) | Portal |
| 2.19 | [Customer AI Disclosure and Transparency](pillar-2-management/2.19-customer-ai-disclosure-and-transparency.md) | Portal |
| 2.20 | [Adversarial Testing and Red Team Framework](pillar-2-management/2.20-adversarial-testing-and-red-team-framework.md) | Portal |
| 2.21 | [AI Marketing Claims and Substantiation](pillar-2-management/2.21-ai-marketing-claims-and-substantiation.md) | Portal |
| 2.22 | [Inactivity Timeout Enforcement](pillar-2-management/2.22-inactivity-timeout-enforcement.md) | PowerShell + Portal, [ITE](../reference/solutions-index.md#inactivity-timeout-enforcement) |
| 2.23 | [User Consent and AI Disclosure Enforcement](pillar-2-management/2.23-user-consent-and-ai-disclosure-enforcement.md) | Portal / PowerShell |
| 2.24 | [Agent Feature Enablement and Restriction Governance](pillar-2-management/2.24-agent-feature-enablement-and-restriction-governance.md) | Portal / PowerShell |

## Pillar 3: Agent Reporting (12 Controls)

| Control ID | Control Name | Implementation |
|-----------|----------|----------------|
| 3.1 | [Agent Inventory and Metadata Management](pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md) | Portal / PowerShell, [CD](../reference/solutions-index.md#compliance-dashboard) |
| 3.2 | [Usage Analytics and Activity Monitoring](pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md) | Portal, [CD](../reference/solutions-index.md#compliance-dashboard), [AOF](../reference/solutions-index.md#agent-usage-performance-workbook) |
| 3.3 | [Compliance and Regulatory Reporting](pillar-3-reporting/3.3-compliance-and-regulatory-reporting.md) | Portal, [CD](../reference/solutions-index.md#compliance-dashboard), [MTR](../reference/solutions-index.md#mime-type-restrictions-for-file-uploads) |
| 3.4 | [Incident Reporting and Root Cause Analysis](pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) | Portal, [Deny Event Correlation](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/deny-event-correlation-report) |
| 3.5 | [Cost Allocation and Budget Tracking](pillar-3-reporting/3.5-cost-allocation-and-budget-tracking.md) | Portal |
| 3.6 | [Orphaned Agent Detection and Remediation](pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) | Portal / PowerShell |
| 3.7 | [PPAC Security Posture Assessment](pillar-3-reporting/3.7-ppac-security-posture-assessment.md) | Portal, [Hardening Baseline](../playbooks/advanced-implementations/configuration-hardening-baseline/index.md), [ITE](../reference/solutions-index.md#inactivity-timeout-enforcement), [MTR](../reference/solutions-index.md#mime-type-restrictions-for-file-uploads) |
| 3.8 | [Copilot Hub](pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md) | Portal, [Hardening Baseline](../playbooks/advanced-implementations/configuration-hardening-baseline/index.md), [UASD](../playbooks/advanced-implementations/unrestricted-agent-sharing-detector/index.md), [AAM](../reference/solutions-index.md#agent-access-governance-monitor), [ITE](../reference/solutions-index.md#inactivity-timeout-enforcement), [CSI](../reference/solutions-index.md#cross-solution-integration) |
| 3.9 | [Microsoft Sentinel Integration](pillar-3-reporting/3.9-microsoft-sentinel-integration.md) | Portal / PowerShell, [AOF](../reference/solutions-index.md#agent-usage-performance-workbook) |
| 3.10 | [Hallucination Feedback Loop](pillar-3-reporting/3.10-hallucination-feedback-loop.md) | Portal |
| 3.11 | [Centralized Agent Inventory Enforcement](pillar-3-reporting/3.11-centralized-agent-inventory-enforcement.md) | Portal / PowerShell |
| 3.12 | [Agent Governance Exception and Override Management](pillar-3-reporting/3.12-agent-governance-exception-and-override-management.md) | Portal / PowerShell |

## Pillar 4: SharePoint Advanced Management (8 Controls)

| Control ID | Control Name | Implementation |
|-----------|----------|----------------|
| 4.1 | [SharePoint Information Access Governance (IAG) / Restricted Content Discovery](pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md) | Portal / PowerShell |
| 4.2 | [Site Access Reviews and Certification](pillar-4-sharepoint/4.2-site-access-reviews-and-certification.md) | Portal |
| 4.3 | [Site and Document Retention Management](pillar-4-sharepoint/4.3-site-and-document-retention-management.md) | Portal / PowerShell, [MTR](../reference/solutions-index.md#mime-type-restrictions-for-file-uploads) |
| 4.4 | [Guest and External User Access Controls](pillar-4-sharepoint/4.4-guest-and-external-user-access-controls.md) | Portal / PowerShell |
| 4.5 | [SharePoint Security and Compliance Monitoring](pillar-4-sharepoint/4.5-sharepoint-security-and-compliance-monitoring.md) | Portal |
| 4.6 | [Grounding Scope Governance](pillar-4-sharepoint/4.6-grounding-scope-governance.md) | Portal |
| 4.7 | [Microsoft 365 Copilot Data Governance](pillar-4-sharepoint/4.7-microsoft-365-copilot-data-governance.md) | Portal |
| 4.8 | [Item-Level Permission Scanning for Agent Knowledge Sources](pillar-4-sharepoint/4.8-item-level-permission-scanning-agent-knowledge-sources.md) | PowerShell, [AKSS](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/agent-knowledge-source-scanner) |

---

## Implementation Reference Legend

The **Implementation** column indicates how each control is implemented:

| Reference | Meaning |
|-----------|---------|
| **Portal** | Configured through Microsoft admin portals (PPAC, Purview, Entra, etc.) |
| **PowerShell** | Automated via PowerShell cmdlets |
| **Solution Link** | Deployable automation from [FSI-AgentGov-Solutions](https://github.com/judeper/FSI-AgentGov-Solutions) |

Solutions provide ready-to-deploy Power Platform components that operationalize controls at scale. See [Solutions Index](../reference/solutions-index.md) for the complete catalog.

---

## How to Use This Framework

1. **Review the Overview** - Start with the framework overview to understand the 3 zones and 4 pillars
2. **Assess Current State** - For each control, review your current implementation level (Baseline, Recommended, or Regulated)
3. **Implement Controls** - Follow the implementation guidance in each control file
4. **Verify & Document** - Use the verification steps to confirm implementation and document evidence
5. **Establish Recurring Reviews** - Schedule quarterly reviews to ensure controls remain effective

---

## Governance Levels

Each control is documented with three governance levels:

- **Baseline**: Minimum required implementation
- **Recommended**: Best practice implementation for Zone 2+ agents
- **Regulated/High-Risk**: Comprehensive implementation for Zone 3 agents and regulated environments

---

## Pillar Descriptions

### Pillar 1: Security Controls (28 Controls)
Focus: Protect data and systems from unauthorized access, misuse, and exploitation.
- Authentication and Authorization
- Data Loss Prevention
- Audit Logging
- Encryption
- Threat Detection
- eDiscovery
- Network Isolation
- Adversarial Input Protection
- Information Barriers
- Step-Up Authentication
- File Upload Governance
- Content Moderation
- Publishing Restrictions

### Pillar 2: Management Controls (24 Controls)
Focus: Govern the agent lifecycle, access control, change management, and model risk.
- Managed Environments
- Change Management
- Business Continuity
- Testing & Validation
- Model Risk Management
- Vendor Management
- Training & Supervision
- RAG Source Validation
- Multi-Agent Orchestration
- Conflict of Interest Testing
- Customer AI Disclosure
- Adversarial Testing & Red Teaming
- AI Marketing Claims & Substantiation
- Inactivity Timeout Enforcement
- User Consent & AI Disclosure
- Feature Enablement Governance

### Pillar 3: Agent Reporting (12 Controls)
Focus: Visibility and monitoring of agent activities, performance, and compliance.
- Agent Inventory
- Usage Analytics
- Compliance Reporting
- Incident Management
- Cost Tracking
- Orphaned Agent Detection
- PPAC Security Posture
- Copilot Hub
- Sentinel Integration
- Hallucination Feedback
- Centralized Inventory Enforcement
- Exception & Override Management

### Pillar 4: SharePoint Advanced Management (8 Controls)
Focus: Govern SharePoint content accessed by agents with specific access, retention, and security controls.
- Information Access Governance
- Access Reviews
- Retention Management
- Guest Access Controls
- Security Monitoring
- Grounding Scope Governance
- M365 Copilot Data Governance
- Item-Level Permission Scanning for Agent Knowledge Sources

---

## Regulatory Alignment

The framework covers compliance requirements for:

- **FINRA**: Rules 3110, 4511, 4512, 2111 (Suitability)
- **SEC**: Rules 17a-3/4, 10b-5, Reg BI, Reg S-P
- **SOX**: Sections 302, 404 (internal controls and reporting)
- **GLBA**: Sections 501, 504, 505 (safeguards and privacy)
- **OCC**: Bulletin 2011-12 and SR 11-7 (model risk management)
- **Federal Reserve**: SR 11-7 (model risk, fair lending)

---

## Governance Zones

Controls are documented for implementation in three governance zones:

- **Zone 1: Personal Productivity** - Individual development, low risk
- **Zone 2: Team Collaboration** - Departmental agents, medium risk
- **Zone 3: Enterprise Managed** - Organization-wide, high risk, customer-facing

---

## Questions & Support

For questions about specific controls or implementation guidance:

- Review the control file for detailed verification steps
- Contact your AI Governance Lead
- Escalate to Compliance Officer for regulatory questions
- Contact your technical implementation team for platform-specific guidance

---

*FSI Agent Governance Framework v1.2 - February 2026*
