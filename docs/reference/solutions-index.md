# Solutions Index

Deployable Power Platform solutions for the FSI Agent Governance Framework.

---

## Overview

The **FSI-AgentGov-Solutions** repository contains ready-to-deploy automation solutions that implement framework controls. Each solution includes Power Automate flows, Dataverse components, and configuration guidance.

**Repository:** [FSI-AgentGov-Solutions](https://github.com/judeper/FSI-AgentGov-Solutions)

---

## Available Solutions

| Solution | Version | Description | Related Controls |
|----------|---------|-------------|------------------|
| [Environment Lifecycle Management](#environment-lifecycle-management) | v1.1.2 | Automated Power Platform environment provisioning with zone-based governance classification | 2.1, 2.2, 2.15 |
| [Message Center Monitor](#message-center-monitor) | v2.1.1 | Monitor M365 Message Center for platform changes affecting AI agents | 2.3, 2.10 |
| [Pipeline Governance Cleanup](#pipeline-governance-cleanup) | v1.0.8 | Discover, notify, and clean up personal pipelines before enforcing centralized ALM governance | 2.3 |
| [Deny Event Correlation Report](#deny-event-correlation-report) | v1.1.0 | Daily deny event correlation across Purview Audit, DLP, and Application Insights | 1.5, 1.7, 3.4 |
| [FINRA Supervision Workflow](#finra-supervision-workflow) | v1.0.0 | Automated supervision queue for AI agent outputs (FINRA 3110) | 2.12, 1.10, 1.7 |
| [Conditional Access Automation](#conditional-access-automation) | v1.0.0 | CA policy deployment and compliance monitoring for AI workloads | 1.11, 1.23, 1.18 |
| [Compliance Dashboard](#compliance-dashboard) | v1.0.0-beta | Aggregated compliance reporting across all 62 controls with zone-based filtering | 3.3, 3.1, 3.2 |
| [Segregation of Duties Detector](#segregation-of-duties-detector) | v1.0.0 | Role conflict detection for Maker/Checker enforcement in agent pipelines | 2.8, 2.1, 2.3 |
| [Scope Drift Monitor](#scope-drift-monitor) | v1.0.0 | Detect agent data access beyond declared operational scope | 1.14, 1.4, 1.5 |
| [RAG Source Validator](#rag-source-validator) | v1.0.0 | Integrity validation for RAG knowledge sources with change detection | 2.16, 1.7, 2.13 |
| [COI Testing Framework](#coi-testing-framework) | v1.0.0 | Conflict of interest testing for agent recommendations | 2.18, 2.11, 2.5 |
| [Hallucination Tracker](#hallucination-tracker) | v1.0.0 | Feedback aggregation for hallucination pattern analysis | 3.10, 2.9, 2.12 |
| [DR Testing Framework](#dr-testing-framework) | v1.0.0 | Automated disaster recovery testing for AI agent infrastructure | 2.4, 2.1, 1.9 |

---

## Solution Details

### Environment Lifecycle Management

Automates Power Platform environment provisioning using a Copilot Studio intake agent. Ensures consistent zone classification and governance controls from day one.

**Components:**
- Copilot Studio intake agent for environment requests
- Power Automate provisioning flows
- Dataverse tables for request tracking
- Zone classification automation

**Framework Playbook:** [Environment Lifecycle Management](../playbooks/advanced-implementations/environment-lifecycle-management/index.md)

**Repository Link:** [environment-lifecycle-management](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/environment-lifecycle-management)

---

### Message Center Monitor

Polls Microsoft 365 Message Center for platform announcements and delivers structured notifications to Teams. Supports governance workflows for change assessment and decision documentation.

**Components:**
- Power Automate polling flow (Graph API)
- Teams adaptive card notifications
- Microsoft Entra ID app registration with `ServiceMessage.Read.All`
- Dataverse integration (optional)

**Framework Playbook:** [Platform Change Governance](../playbooks/advanced-implementations/platform-change-governance/index.md)

**Repository Link:** [message-center-monitor](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/message-center-monitor)

---

### Pipeline Governance Cleanup

!!! warning "February 2026 Deadline"
    Microsoft will automatically enable Managed Environments for pipeline target environments starting February 2026. Use this solution to audit and remediate personal pipelines before enforcement. See [Control 2.1](../controls/pillar-2-management/2.1-managed-environments.md#critical-deadline-february-2026-pipeline-requirement) for details.

Discovers personal deployment pipelines across environments and notifies owners before enforcing centralized ALM governance. Supports transition from ad-hoc to governed deployment patterns.

**Components:**
- PowerShell discovery scripts
- Owner notification workflows
- Cleanup automation with safety checks
- Dry-run mode for impact assessment

**Related Control:** [2.3 - Change Management](../controls/pillar-2-management/2.3-change-management-and-release-planning.md)

**Repository Link:** [pipeline-governance-cleanup](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/pipeline-governance-cleanup)

---

### Deny Event Correlation Report

Aggregates and correlates deny events from multiple Microsoft sources to provide unified visibility into blocked agent activities.

**Data Sources:**
- Purview Unified Audit Log
- DLP policy violations
- Application Insights RAI telemetry

**Components:**
- Power BI report template
- Data extraction scripts
- Correlation logic

**Framework Playbook:** [Deny Event Correlation Report](../playbooks/advanced-implementations/deny-event-correlation-report/index.md)

**Repository Link:** [deny-event-correlation-report](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/deny-event-correlation-report)

---

### FINRA Supervision Workflow

Automates the supervision workflow for AI agent outputs to support FINRA Rule 3110 compliance. Routes flagged content from Communication Compliance to designated supervisory principals with configurable SLAs and escalation.

**Components:**
- Dataverse tables for supervision queue and audit trail
- Power Automate flows for ingestion, assignment, and escalation
- Communication Compliance API integration
- Power BI supervision dashboard
- Evidence export with SHA-256 integrity hashing

**Regulatory Alignment:**
- FINRA Rule 3110 (Supervision)
- FINRA Rule 3120 (Testing)
- FINRA Notice 24-09 (Gen AI)
- SEC 17a-3/4 (Recordkeeping)

**Related Control:** [2.12 - Supervision and Oversight](../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md)

**Repository Link:** [finra-supervision-workflow](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/finra-supervision-workflow)

---

### Conditional Access Automation

Automates Conditional Access policy deployment and compliance monitoring for AI workloads, implementing Zero Trust access controls across governance zones.

**Components:**
- 8 CA policy templates for Copilot Studio, Agent Builder, M365 Copilot
- PowerShell scripts for deployment, compliance testing, drift detection
- Zone-based policy requirements (risk-based → always MFA → compliant device)
- Break-glass account exclusion enforcement
- ELM integration for new environment provisioning

**Security Alignment:**
- NIST 800-53 AC-2, IA-2
- Zero Trust architecture
- SOX 404 IT general controls
- GLBA 501(b) safeguards

**Related Controls:**
- [1.11 - Conditional Access and MFA](../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md)
- [1.23 - Step-Up Authentication](../controls/pillar-1-security/1.23-step-up-authentication-for-agent-operations.md)

**Repository Link:** [conditional-access-automation](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/conditional-access-automation)

---

### Compliance Dashboard

!!! info "Beta Release"
    Documentation and Dataverse schemas are complete. Power BI template requires manual creation following the provided specifications.

Provides unified compliance visibility across all 62 framework controls with zone-based filtering and trend analysis for regulatory reporting.

**Components:**
- Dataverse tables for control assessments, scores, exceptions, and evidence
- Power Automate flows for score calculation and exception monitoring
- DAX measure library for Power BI
- Sample data with all 62 controls
- Python script for demo data loading

**Regulatory Alignment:**
- SOX 404 (ICFR documentation)
- FINRA 3120 (supervisory control testing)
- OCC 2011-12 (model risk reporting)

**Related Control:** [3.3 - Compliance Reporting](../controls/pillar-3-reporting/3.3-compliance-and-regulatory-reporting.md)

**Repository Link:** [compliance-dashboard](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/compliance-dashboard)

---

### Segregation of Duties Detector

Identifies and prevents segregation of duties violations where users have incompatible roles in AI agent development and deployment workflows.

**Components:**
- Dataverse tables for conflict rules, violations, exceptions, and audit log
- PowerShell scripts for SoD scanning and rule import
- 10 predefined conflict rules across 3 categories (Maker/Checker, Segregation, Privileged Access)
- Exception workflow with multi-level approval

**Regulatory Alignment:**
- SOX 404 (IT General Controls)
- COSO Framework (Control Activities)
- OCC Heightened Standards (Risk Management)

**Related Control:** [2.8 - Segregation of Duties](../controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md)

**Repository Link:** [segregation-detector](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/segregation-detector)

---

### Scope Drift Monitor

Tracks agent data access and alerts when access extends beyond declared operational scope, supporting data minimization principles.

**Components:**
- Dataverse tables for agent scope definitions, violations, and expansion requests
- PowerShell script for baseline generation
- Scope expansion workflow with data owner and security approval
- Integration with Unified Audit Log and Defender CloudAppEvents

**Regulatory Alignment:**
- GDPR Article 5(1)(c) (Data Minimization)
- GLBA 501(b) (Customer Information Safeguards)
- CCPA (Purpose Limitation)

**Related Control:** [1.14 - Data Minimization](../controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md)

**Repository Link:** [scope-drift-monitor](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/scope-drift-monitor)

---

### RAG Source Validator

Validates the integrity of Retrieval-Augmented Generation (RAG) knowledge sources, detecting unauthorized changes and content drift.

**Components:**
- Dataverse tables for knowledge source registry, validation results, and change tracking
- PowerShell script for SHA-256 hash validation
- Support for SharePoint, Dataverse, and Azure Blob sources
- Schema drift detection and freshness monitoring

**Regulatory Alignment:**
- SEC 17a-4 (Record Integrity)
- FINRA 4511 (Books and Records Accuracy)
- SOX 404 (Data Integrity Controls)

**Related Control:** [2.16 - RAG Source Integrity](../controls/pillar-2-management/2.16-rag-source-integrity-validation.md)

**Repository Link:** [rag-source-validator](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/rag-source-validator)

---

### COI Testing Framework

Automated testing framework for detecting conflicts of interest in AI agent recommendations, addressing FINRA suitability requirements.

**Components:**
- Python test runner with 10 predefined scenarios
- Test categories: Proprietary bias, Suitability, Fee transparency, Cross-selling
- Dataverse integration for result storage
- Integration with FINRA Supervision Workflow

**Regulatory Alignment:**
- FINRA Rule 2111 (Suitability)
- FINRA Rule 2010 (Standards of Commercial Honor)
- FINRA Rule 2210 (Communications)
- SEC Regulation Best Interest

**Related Control:** [2.18 - Conflict of Interest Testing](../controls/pillar-2-management/2.18-automated-conflict-of-interest-testing.md)

**Repository Link:** [coi-testing](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/coi-testing)

---

### Hallucination Tracker

Collects and analyzes feedback on AI agent hallucinations to identify patterns and enable targeted improvements.

**Components:**
- Multi-source feedback collection (user reactions, supervisor rejections, automated checks)
- Python script for pattern detection and clustering
- 5 hallucination categories with severity scoring
- Agent accuracy scoring and rating system
- Integration with FINRA Supervision Workflow

**Regulatory Alignment:**
- FINRA 2210 (Communications Accuracy)
- SEC Marketing Rule (Substantiation)
- CFPB Chatbot Guidance (Accuracy)

**Related Control:** [3.10 - Hallucination Feedback](../controls/pillar-3-reporting/3.10-hallucination-feedback-loop.md)

**Repository Link:** [hallucination-tracker](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/hallucination-tracker)

---

### DR Testing Framework

Validates AI agent disaster recovery procedures against defined RTO/RPO targets, supporting operational resilience requirements.

**Components:**
- 4 test scenarios: Agent Restore, Environment Failover, Data Recovery, Full DR
- PowerShell script with RTO/RPO measurement
- Validation checks for agent, connector, data, and security
- Gap identification and tracking
- Evidence export for compliance

**Regulatory Alignment:**
- OCC Heightened Standards (Operational Resilience)
- FFIEC BCP (Business Continuity Planning)
- SEC Rule 17a-4 (Record Recovery)
- FINRA Rule 4370 (Business Continuity Plans)

**Related Control:** [2.4 - Business Continuity](../controls/pillar-2-management/2.4-business-continuity-and-disaster-recovery.md)

**Repository Link:** [dr-testing-framework](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/dr-testing-framework)

---

## Getting Started

1. Review the relevant framework playbook for architecture and requirements
2. Clone the [FSI-AgentGov-Solutions](https://github.com/judeper/FSI-AgentGov-Solutions) repository
3. Navigate to the solution folder and follow the README
4. Configure Microsoft Entra ID app registrations as documented
5. Deploy Power Automate flows and test in a non-production environment

---

## Version History

Solutions follow semantic versioning. See each solution's README for detailed changelog.

| Solution | Current | Last Updated |
|----------|---------|--------------|
| Environment Lifecycle Management | v1.1.2 | January 2026 |
| Message Center Monitor | v2.1.1 | January 2026 |
| Pipeline Governance Cleanup | v1.0.8 | January 2026 |
| Deny Event Correlation Report | v1.1.0 | January 2026 |
| FINRA Supervision Workflow | v1.0.0 | February 2026 |
| Conditional Access Automation | v1.0.0 | February 2026 |
| Compliance Dashboard | v1.0.0-beta | February 2026 |
| Segregation of Duties Detector | v1.0.0 | February 2026 |
| Scope Drift Monitor | v1.0.0 | February 2026 |
| RAG Source Validator | v1.0.0 | February 2026 |
| COI Testing Framework | v1.0.0 | February 2026 |
| Hallucination Tracker | v1.0.0 | February 2026 |
| DR Testing Framework | v1.0.0 | February 2026 |

---

*FSI Agent Governance Framework v1.2.36 - February 2026*
