# Solutions Index

Deployable Power Platform solutions for the FSI Agent Governance Framework.

---

## Overview

The **FSI-AgentGov-Solutions** repository contains ready-to-deploy automation solutions that implement framework controls. Each solution includes Power Automate flows, Dataverse components, and configuration guidance.

**Repository:** [FSI-AgentGov-Solutions](https://github.com/judeper/FSI-AgentGov-Solutions)

---

## Available Solutions

*Control coverage listed here represents the primary controls addressed. See each solution's README for the complete list of related controls.*

| Solution | Version | Status | Description | Related Controls |
|----------|---------|--------|-------------|------------------|
| [Environment Lifecycle Management](#environment-lifecycle-management) | v1.1.2 | Completed | Automated Power Platform environment provisioning with zone-based governance classification | 2.1, 2.2, 2.3, 2.8, 1.7 |
| [Message Center Monitor](#message-center-monitor) | v2.1.1 | Completed | Monitor M365 Message Center for platform changes affecting AI agents | 2.3, 2.10 |
| [Pipeline Governance Cleanup](#pipeline-governance-cleanup) | v1.0.8 | Completed | Discover, notify, and clean up personal pipelines before enforcing centralized ALM governance | 2.3 |
| [Deny Event Correlation Report](#deny-event-correlation-report) | v2.0.0 | Validated | Daily deny event correlation across Purview Audit, DLP, and Application Insights with Dataverse persistence, Power Automate orchestration, and evidence export | 1.5, 1.7, 1.8, 3.4 |
| [File Upload Security Configurator](#file-upload-security-configurator) | v1.0.0 | Completed | Automated per-agent file upload validation against zone governance policies with drift detection | 1.14, 1.8, 1.4 |
| [Audit Compliance Manager](#audit-compliance-manager) | v1.0.0 | Completed | Automated validation, drift detection, and remediation of tenant and environment audit configurations with Managed Identity auth and approval workflows | 1.7 |
| [Session Security Configurator](#session-security-configurator) | v1.0.0 | Completed | Automated session security validation per governance zone with drift detection and compliance evidence export | 1.23, 1.11 |
| [Agent Access Governance Monitor](#agent-access-governance-monitor) | v1.0.0 | Completed | Automated detection of overly permissive agent access configurations per governance zone | 3.8 |
| [Agent Observability Foundation](#agent-observability-foundation) | v1.1.0 | Completed | Foundational observability infrastructure for agent monitoring and diagnostics with Azure Monitor integration | — |
| [Content Moderation Governance Monitor](#content-moderation-governance-monitor) | v1.0.0 | Completed | Automated per-agent content moderation level validation against zone-specific governance requirements | 1.27, 1.8 |
| [FINRA Supervision Workflow](#finra-supervision-workflow) | v1.0.0 | Validated | Automated supervision queue for AI agent outputs (FINRA 3110) | 2.12, 1.10, 1.7 |
| [Conditional Access Automation](#conditional-access-automation) | v1.1.0 | Completed | CA policy deployment, compliance monitoring, drift detection, and evidence export for AI workloads | 1.11, 1.23, 1.18 |
| [Compliance Dashboard](#compliance-dashboard) | v1.0.0 | Completed | Aggregated compliance reporting across 71 controls with zone-based filtering | 3.3, 3.1, 3.2 |
| [Segregation of Duties Detector](#segregation-of-duties-detector) | v1.0.0 | Validated | Role conflict detection for Maker/Checker enforcement in agent pipelines | 2.8, 2.1, 2.3 |
| [Scope Drift Monitor](#scope-drift-monitor) | v1.1.0 | Completed | Detect agent data access beyond declared operational scope | 1.14, 1.4, 1.5 |
| [RAG Source Validator](#rag-source-validator) | v1.0.0 | Work In Progress | Integrity validation for RAG knowledge sources with change detection | 2.16, 1.7, 2.13 |
| [COI Testing Framework](#coi-testing-framework) | v1.0.0 | Work In Progress | Conflict of interest testing for agent recommendations | 2.18, 2.11, 2.5 |
| [Hallucination Tracker](#hallucination-tracker) | v1.0.0 | Work In Progress | Feedback aggregation for hallucination pattern analysis | 3.10, 2.9, 2.12 |
| [DR Testing Framework](#dr-testing-framework) | v1.0.0 | Work In Progress | Automated disaster recovery testing for AI agent infrastructure | 2.4, 2.1, 1.9 |
| [Cross-Solution Integration](#cross-solution-integration) | v1.0.0 | Completed | Wires Tier 2 solutions into Compliance Dashboard, adds ELM hooks, unified evidence export | 1.7, 1.23, 1.11, 3.8, 1.8, 1.14 |
| [Configuration Hardening Baseline](#configuration-hardening-baseline) | v1.1.0 | Completed | PowerShell verification script and 32-item hardening checklist for SSPM-mapped configuration settings | 1.1, 1.7, 1.8, 1.18, 2.1, 2.22, 3.7, 3.8 |
| [Agent Usage & Performance Workbook](#agent-usage-performance-workbook) | v1.0.0 | Completed | Azure Monitor Workbook for Copilot Studio agent usage, performance, and error visibility | 2.9, 3.2, 3.9 |
| [Unrestricted Agent Sharing Detector](#unrestricted-agent-sharing-detector) | v1.0.0 | Completed | Continuous detection of overly permissive agent sharing configurations with automated remediation and exception management | 1.1, 3.8 |
| [Agent Security Configuration Governance](#agent-security-configuration-governance) | v1.0.0 | Completed | Per-agent authentication enforcement, publishing restriction validation, and zone-based access configuration governance scripts | 1.1, 3.7, 3.8 |
| [MIME Type Restrictions for File Uploads](#mime-type-restrictions-for-file-uploads) | v1.0.0 | Completed | Zone-based MIME type configuration, server-side magic bytes validation, DLP policy integration, Sentinel monitoring | 1.5, 1.10, 1.11, 1.13, 1.14, 1.25, 3.3, 3.7, 4.3 |
| [Inactivity Timeout Enforcement](#inactivity-timeout-enforcement) | v1.0.0 | Completed | Policy-driven inactivity timeout validation and enforcement with zone-based maximum duration requirements and Dataverse compliance persistence | 2.22, 1.23, 3.7, 3.8 |
| [Agent Sharing Access Restriction Detector](#agent-sharing-access-restriction-detector) | v1.0.0 | Completed | Continuous detection and restriction of agent sharing configurations exceeding zone-based access policies with approval workflows and exception management | 1.18, 2.8 |

### Status Legend

| Status | Description |
|--------|-------------|
| **Completed** | Production-ready with comprehensive documentation, testing complete, deployed and validated |
| **Validated** | Core functionality complete and validated, production deployment pending broader testing |
| **Work In Progress** | Active development, documentation complete or near-complete, functional testing in progress |
| **Planned** | Designed and documented, implementation not yet started |

---

## Solution Details

### Environment Lifecycle Management

Automates Power Platform environment provisioning using a Copilot Studio intake agent. Supports consistent zone classification and governance controls from day one.

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

!!! warning "Pipeline Governance Required"
    Organizations should run Pipeline Governance Cleanup before Microsoft automatically enables Managed Environments for all pipeline targets. Discover and remediate personal pipelines to avoid unexpected licensing charges.

    See [Control 2.1](../controls/pillar-2-management/2.1-managed-environments.md#critical-deadline-february-2026-pipeline-requirement) for complete deadline details.

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

!!! success "Production Ready"
    v2.0.0 includes PowerShell extraction scripts, shared module, Dataverse infrastructure, Power Automate orchestration flow, Teams/email alerting, and SHA-256 integrity-hashed evidence export pipeline.

Aggregates and correlates deny events from multiple Microsoft sources to provide unified visibility into blocked agent activities with daily trend analysis, anomaly detection, and zone-based alerting.

**Components:**

- PowerShell extraction scripts for Purview Audit, Purview DLP, and Application Insights
- Shared PowerShell module (FSIGovernance.DEC) with common logging, hashing, and Dataverse functions
- Dataverse schema (5 tables) for deny events, correlation results, alert history, and configuration
- Daily correlation engine with 7-day trend analysis and volume anomaly detection
- Power Automate orchestration flow with Azure Automation runbook integration
- Zone-based alerting with Teams adaptive cards and email notifications
- SHA-256 integrity-hashed evidence export with regulatory alignment mapping
- Zone-based retention enforcement (90d/365d/730d)
- Power BI dashboard template for deny event trends and zone compliance

**Regulatory Alignment:**

- FINRA 4511 (Books and Records)
- FINRA 3110 (Supervision)
- FINRA Regulatory Notice 25-07 (Workplace Modernization)
- SEC 17a-3/4 (Recordkeeping)
- SOX 302/404 (Internal Controls)
- GLBA 501(b) (Safeguards)

**Related Controls:**

- [1.5 - DLP and Sensitivity Labels](../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md)
- [1.7 - Comprehensive Audit Logging](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md)
- [1.8 - Runtime Protection](../controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md)
- [3.4 - Incident Reporting](../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md)

**Framework Playbook:** [Deny Event Correlation Report](../playbooks/advanced-implementations/deny-event-correlation-report/index.md)

**Repository Link:** [deny-event-correlation-report](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/deny-event-correlation-report)

---

### File Upload Security Configurator

!!! success "Production Ready"
    Shipped in v8 milestone (February 2026). Fully validated with deployment scripts, Dataverse schema, and compliance evidence export.

Automated per-agent file upload validation against zone governance policies. Detects binary drift (enabled/disabled changes), cross-checks content moderation levels, and exports SHA-256 compliance evidence packages.

**Components:**

- PowerShell scripts for per-agent file upload setting retrieval and compliance comparison
- Daily scheduled drift detection via Power Automate with Azure Automation runbook
- Teams adaptive card alerts with severity classification (Critical/High/Warning/Info)
- Dataverse tables for file upload baselines, validation history, and violations
- Zone-based policy enforcement (Zone 1: Allowed, Zone 2: Restricted, Zone 3: Disabled by default)
- Content moderation cross-check (minimum level per zone when uploads enabled)
- Evidence export with SHA-256 integrity hashing

**Regulatory Alignment:**

- GLBA 501(b) (Safeguards — Data Intake Controls)
- FINRA 4511 (Books and Records — File Upload Configuration)
- SOX 404 (Internal Controls — Data Minimization)
- SEC 17a-3/4 (Recordkeeping — Configuration Governance)

**Related Controls:**

- [1.14 - Data Minimization and Agent Scope Control](../controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md)
- [1.8 - Runtime Protection and External Threat Detection](../controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md)
- [1.4 - Advanced Connector Policies](../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md)

**Repository Link:** [file-upload-security](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/file-upload-security)

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

!!! success "Production Ready"
    v1.1.0 includes PowerShell module, Azure Automation runbook, Power Automate flows, Dataverse persistence, drift detection, Teams alerting, and SHA-256 evidence export.

Automates Conditional Access policy deployment and compliance monitoring for AI workloads, implementing Zero Trust access controls across governance zones with persistent state management, daily compliance scanning, and drift detection.

**Components:**
- CAAClient PowerShell module with 8 Dataverse functions
- 8 CA policy templates for Copilot Studio, Agent Builder, M365 Copilot
- Azure Automation runbook for unattended daily compliance validation
- Power Automate daily compliance scan flow with Dataverse persistence
- ELM provisioning hook for automatic CA policy deployment
- Dataverse tables for baselines, validation history (immutable), and violations
- Teams adaptive card alerts with zone-based severity (CRITICAL/HIGH/WARNING)
- Multi-dimensional drift detection (state, conditions, grants, sessions, additions/removals)
- SHA-256 evidence export with integrity hashing for FINRA/SEC examination support
- Break-glass account exclusion enforcement

**Security Alignment:**
- NIST 800-53 AC-2, IA-2
- Zero Trust architecture
- SOX 404 IT general controls
- GLBA 501(b) safeguards

**Related Controls:**
- [1.11 - Conditional Access and MFA](../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md)
- [1.23 - Step-Up Authentication](../controls/pillar-1-security/1.23-step-up-authentication-for-agent-operations.md)
- [1.18 - RBAC for Agent Management](../controls/pillar-1-security/1.18-application-level-authorization-and-role-based-access-control-rbac.md)

**Repository Link:** [conditional-access-automation](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/conditional-access-automation)

---

### Compliance Dashboard

!!! success "Production Ready"
    v1.0.0 includes Power Automate flows, Dataverse schema, sample data, and deployment documentation. Power BI template requires manual creation following the 883-line specification.

Provides unified compliance visibility across all 71 framework controls with zone-based filtering and trend analysis for regulatory reporting.

**Components:**
- Dataverse tables for control assessments, scores, exceptions, and evidence
- Power Automate flows for score calculation and exception monitoring
- DAX measure library for Power BI
- Sample data with 71 controls
- Python script for demo data loading

**Regulatory Alignment:**
- SOX 404 (ICFR documentation)
- FINRA 3120 (supervisory control testing)
- OCC 2011-12 (model risk reporting)

**Related Control:** [3.3 - Compliance Reporting](../controls/pillar-3-reporting/3.3-compliance-and-regulatory-reporting.md)

**Repository Link:** [compliance-dashboard](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/compliance-dashboard)

---

### Segregation of Duties Detector

Identifies and helps prevent segregation of duties violations where users have incompatible roles in AI agent development and deployment workflows.

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

!!! success "Production Ready"
    v1.1.0 includes PowerShell scripts for baseline capture and drift detection, Power Automate flows for detection and expansion approval, Dataverse schema, and comprehensive deployment documentation.

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

### Audit Compliance Manager

Automated validation, drift detection, and remediation of Microsoft 365 and Power Platform audit configurations to support compliance with US financial services regulations. Combines configuration validation with automated gap detection and approval-gated remediation using enterprise-grade Managed Identity authentication.

!!! success "Production Ready"
    Version 1.0.0 — Consolidates the former Audit Configuration Validator (ACV) and Audit Logging Compliance Automation (ALCA) into a single unified solution.

**Version:** v1.0.0
**Status:** Completed

**Components:**

- `AuditComplianceHelpers.psm1` — Shared PowerShell module (retry logic, MI auth, Dataverse operations, evidence export, email notifications)
- PowerShell validation scripts (tenant-level: Unified Audit Log, mailbox audit, Purview retention)
- Environment-level validation (Power Platform audit retention with zone-based thresholds)
- `Check-AuditLoggingCompliance.ps1` — Detection runbook (environment scanning, Purview + Dataverse audit checks, compliance determination)
- `Enable-AuditLogging.ps1` — Remediation runbook (org-level + entity-level audit enablement for 6 Copilot Studio entities, WhatIf support)
- `Compare-ValidationBaseline.ps1` — Drift detection with SHA-256 evidence hashing
- `Export-AuditValidationEvidence.ps1` — Evidence export with SHA-256 integrity hashing
- `Test-EvidenceIntegrity.ps1` — Evidence hash verification for audit submissions
- Dataverse tables for validation history (immutable), environment registry, and compliance tracking
- Power Automate flows for daily scheduled validation, drift detection alerting, and approval-gated remediation
- Azure Automation runbook wrappers for scheduled execution with System-Assigned Managed Identity
- Pester 5 unit tests (29 test cases)
- Deployment guide, scheduling guide, 15 testing scenarios, 10 troubleshooting issues

**Regulatory Alignment:**

- FINRA 4511 (Books and Records — Audit Configuration)
- SEC 17a-3/4 (Recordkeeping — Audit Trail Requirements)
- SOX 404 (Internal Controls — Audit Logging Verification)
- GLBA 501(b) (Safeguards — Audit Trail Integrity)

**Related Control:** [1.7 - Comprehensive Audit Logging](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md)

**Repository Link:** [audit-compliance-manager](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/audit-compliance-manager)

---

### Session Security Configurator

Automates session security validation and configuration deployment per governance zone. Validates authentication contexts, CA policies, PIM integration, break-glass accounts, and conflict settings with daily drift detection.

**Components:**

- PowerShell scripts for 5-dimension validation (session controls, auth strength, PIM, break-glass, conflict audit)
- Authentication context deployment (c1-c5) with conflict detection
- Zone-specific CA policy templates with 72-hour bake period enforcement
- Power Automate flows for daily drift detection with Teams adaptive card alerts
- Dataverse tables for validation history and compliance tracking
- Evidence export with SHA-256 integrity hashing

**Regulatory Alignment:**

- GLBA 501(b) (Safeguards - Session Security)
- FINRA 4511 (Books and Records - Access Controls)
- SOX 404 (Internal Controls - Authentication)
- NIST SP 800-63B (Authentication Assurance Levels)

**Related Controls:**

- [1.23 - Step-Up Authentication](../controls/pillar-1-security/1.23-step-up-authentication-for-agent-operations.md)
- [1.11 - Conditional Access and MFA](../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md)

**Repository Link:** [session-security-configurator](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/session-security-configurator)

---

### Agent Access Governance Monitor

Automated detection of overly permissive agent access configurations across Power Platform environments. Validates agent sharing, authoring, and publishing settings against governance zone requirements with daily drift detection and compliance evidence export.

**Components:**

- PowerShell scripts for zone-based agent access validation
- Daily scheduled drift detection via Power Automate
- Teams adaptive card alerts with severity classification (Critical/High/Warning/Info)
- Dataverse tables for access baselines, validation history, and violations
- Evidence export with SHA-256 integrity hashing

**Regulatory Alignment:**

- FINRA 4511 (Books and Records — Agent Access Controls)
- SOX 404 (Internal Controls — Configuration Governance)
- SEC 17a-3/4 (Recordkeeping — Access Configuration)
- GLBA 501(b) (Safeguards — Agent Sharing Controls)

**Related Control:** [3.8 - Copilot Hub and Governance Dashboard](../controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md)

**Repository Link:** [agent-access-monitor](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/agent-access-monitor)

---

### Agent Observability Foundation

Foundational observability infrastructure for agent monitoring and diagnostics with Azure Monitor integration. Provides the shared telemetry backbone used by other governance solutions.

**Components:**

- Azure Monitor workspace configuration for agent telemetry
- Log Analytics queries for agent health and performance
- Diagnostic settings templates for Copilot Studio agents
- Shared KQL query library for governance reporting

**Related Control(s):** — (foundational infrastructure, no specific control mapping)

**Repository Link:** [agent-observability-foundation](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/agent-observability-foundation)

---

### Content Moderation Governance Monitor

!!! success "Production Ready"
    Shipped in v7 milestone (February 2026). Fully validated with drift detection, zone compliance, and SHA-256 evidence export.

Automated detection of non-compliant content moderation settings for Copilot Studio agents across Power Platform environments. Validates per-agent moderation levels (Low/Medium/High) against governance zone requirements with daily drift detection and compliance evidence export.

**Components:**

- PowerShell scripts for per-agent content moderation validation
- Daily scheduled drift detection via Power Automate
- Teams adaptive card alerts with severity classification (Critical/High/Medium/Warning)
- Dataverse tables for moderation baselines, validation history, and violations
- Evidence export with SHA-256 integrity hashing

**Regulatory Alignment:**

- FINRA 3110 (Supervisory Controls — Content Moderation Governance)
- SOX 404 (Internal Controls — Configuration Governance)
- GLBA 501(b) (Safeguards — Content Safety Controls)
- SEC AI Priorities (Responsible AI governance)

**Related Control(s):** [1.27 - AI Agent Content Moderation Enforcement](../controls/pillar-1-security/1.27-ai-agent-content-moderation-enforcement.md), [1.8 - Runtime Protection and External Threat Detection](../controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md)

**Repository Link:** [content-moderation-monitor](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/content-moderation-monitor)

---

### Cross-Solution Integration

Wires five Tier 2 governance solutions (ACM, SSC, AAM, CMM, FUS) into the Compliance Dashboard for automated compliance scoring, adds ELM provisioning hooks for environment auto-registration, and provides unified evidence export with SHA-256 hash chain for audit packages.

**Components:**

- IntegrationConfig.psm1 — shared configuration module with solution-to-control mappings and status translation
- Sync-SolutionAssessments.ps1 — batch pipeline for Compliance Dashboard feeds
- cd-solution-feed-collector.json — Power Automate alternative for dashboard feeds
- elm-solution-initializer.json — event-driven ELM provisioning hook
- Register-ProvisionedEnvironment.ps1 — PowerShell ACM registration alternative
- Export-UnifiedComplianceEvidence.ps1 — unified evidence export pipeline
- Test-UnifiedEvidenceIntegrity.ps1 — evidence integrity verification

**Regulatory Alignment:**

- FINRA 4511 (Books and Records — consolidated governance evidence)
- SEC 17a-3/4 (Recordkeeping — unified compliance reporting)
- SOX 302/404 (Internal Controls — cross-solution governance visibility)
- OCC 2011-12 (Model Risk Management — integrated monitoring evidence)

**Related Controls:** 1.7, 1.23, 1.11, 3.8, 1.8, 1.14

**Repository Link:** [cross-solution-integration](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/cross-solution-integration)

---

### Configuration Hardening Baseline

!!! success "Production Ready"
    v1.1.0 includes 32-item hardening checklist, PowerShell verification script for automatable items, manual attestation procedures, evidence export with SHA-256 integrity hashing, and zone-specific review cadence guidance.

Consolidates security-critical configuration settings across Power Platform, Copilot Studio, and M365 Admin Center into a single reviewable hardening baseline. Enables FSI organizations to verify their configuration posture across agent authentication, audit logging, content moderation, RBAC, environment governance, and AI feature access — addressing settings flagged by SSPM security posture assessments.

!!! info "Framework-Integrated Tool"
    Unlike other solutions in the FSI-AgentGov-Solutions repository, the Configuration Hardening Baseline is integrated directly into the FSI-AgentGov framework as a governance script and advanced implementation playbook.

**Components:**

- 32-item master configuration hardening checklist with automation feasibility classification
- `Invoke-HardeningBaselineCheck.ps1` PowerShell verification script for automatable items (audit logging, environment provisioning, environment security settings)
- Manual attestation procedures for agent-level settings without API access
- Zone-specific review cadence (Weekly/Bi-weekly/Monthly) with escalation triggers
- Evidence export with SHA-256 integrity hashing for regulatory examination readiness
- Compliance calendar integration for quarterly examination preparation

**Regulatory Alignment:**

- FINRA 4511 (Books and Records — Configuration Evidence)
- SEC 17a-3/4 (Recordkeeping — Hardening Baseline Documentation)
- SOX 302/404 (Internal Controls — Configuration Governance)
- GLBA 501(b) (Safeguards — Security Posture Verification)
- OCC 2011-12 (Model Risk Management — Infrastructure Controls)

**Related Controls:**

- [1.1 - Restrict Agent Publishing](../controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md)
- [1.7 - Comprehensive Audit Logging](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md)
- [1.8 - Runtime Protection](../controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md)
- [1.18 - Application-Level RBAC](../controls/pillar-1-security/1.18-application-level-authorization-and-role-based-access-control-rbac.md)
- [2.1 - Managed Environments](../controls/pillar-2-management/2.1-managed-environments.md)
- [3.7 - PPAC Security Posture Assessment](../controls/pillar-3-reporting/3.7-ppac-security-posture-assessment.md)
- [3.8 - Copilot Hub](../controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md)

**Framework Playbook:** [Configuration Hardening Baseline](../playbooks/advanced-implementations/configuration-hardening-baseline/index.md)

**Script Location:** `scripts/governance/Invoke-HardeningBaselineCheck.ps1`

---

### Agent Usage & Performance Workbook

Deployable Azure Monitor Workbook template for Copilot Studio agent usage, performance, and error visibility — solving the ALM separation-of-duties gap for FSI organizations where production Analytics tab access is restricted.

**Components:**

- Azure Monitor Workbook JSON template (`agent-observability-foundation/src/agent-usage-workbook.json` in FSI-AgentGov-Solutions)
- 3-tab layout: Usage & Business Value, Performance & Errors, Operational Health
- Parameterized Application Insights resource ID with zone-aware thresholds
- KQL query library targeting native Copilot Studio customEvents telemetry

**Regulatory Alignment:**

- Supports compliance with FINRA 3110 supervisory review requirements through operational visibility dashboards
- Aids in meeting OCC 2011-12 model risk management requirements through performance monitoring
- Supports Fed SR 11-7 model validation via error rate and anomaly detection indicators

**Related Controls:**

- [Control 2.9: Agent Performance Monitoring and Optimization](../controls/pillar-2-management/2.9-agent-performance-monitoring-and-optimization.md)
- [Control 3.2: Usage Analytics and Activity Monitoring](../controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md)
- [Control 3.9: Microsoft Sentinel Integration](../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md)

**Framework Playbook:** [Agent Usage & Performance Workbook](../playbooks/advanced-implementations/agent-usage-workbook/index.md)

**Repository Link:** [agent-observability-foundation](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/agent-observability-foundation)

---

### Unrestricted Agent Sharing Detector

!!! success "Production Ready"
    v1.0.0 includes detection flow with 5 violation rules, approval-based remediation, exception management canvas app, deployment scripts, on-demand audit, and SHA-256 evidence export.

Continuous detection of overly permissive Copilot Studio agent sharing configurations across Power Platform environments. Identifies organization-wide sharing, public internet links, unapproved groups, excessive individual shares, and cross-tenant access — with automated remediation and time-bound exception management.

**Components:**

- Detection flow scanning all agents via BAP APIs with 5 violation rules
- Approval-based remediation flow with BAP PATCH principal overwrite
- Exception approval workflow with sequential dual approval (Security → Data Owner)
- Exception Manager canvas app for submission, status tracking, and expiration display
- On-demand PowerShell audit script (`Invoke-SharingAudit.ps1`)
- Deployment scripts for detection and remediation flows
- Violation export with SHA-256 integrity hashing
- Dataverse schema (5 tables) with zone-based sharing policies
- Teams adaptive card alerts with severity-based styling

**Regulatory Alignment:**

- FINRA 4511 (Books and Records — Agent Sharing Configuration)
- SEC 17a-4 (Recordkeeping — Sharing Change Audit Trail)
- GLBA 501(b) (Safeguards — Agent Access Controls)
- SOX 404 (Internal Controls — Sharing Policy Enforcement)

**Related Controls:**

- [1.1 - Restrict Agent Publishing by Authorization](../controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md)
- [3.8 - Copilot Hub and Governance Dashboard](../controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md)

**Framework Playbook:** [Unrestricted Agent Sharing Detector](../playbooks/advanced-implementations/unrestricted-agent-sharing-detector/index.md)

**Repository Link:** [unrestricted-agent-sharing-detector](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/unrestricted-agent-sharing-detector)

---

### Agent Security Configuration Governance

!!! success "Production Ready"
    v1.0.0 includes 3 PowerShell governance scripts validating per-agent authentication enforcement (6 SSPM items), publishing restriction criteria (6 checks), and zone-based agent access settings (4 check groups) — with drift detection, SHA-256 evidence export, and adaptive card alerting.

Automates agent-level security configuration governance across three critical areas: authentication enforcement per SSPM security posture items, publishing restriction validation, and M365 Admin Center zone-based access settings verification. Converts manual attestation checks to automated validation with structured evidence export.

!!! info "Framework-Integrated Tool"
    These governance scripts are integrated directly into the FSI-AgentGov framework repository under `scripts/governance/`. They do not require the companion FSI-AgentGov-Solutions repository.

**Components:**

- `Test-AgentAuthConfiguration.ps1` — Per-agent authentication configuration validation against 6 SSPM items with zone-based logic and drift detection
- `restrict-agent-publishing.ps1` — Publishing restriction governance validating 6 criteria (Environment Maker role, security groups, sharing, DLP, managed environment limits, approval workflow)
- `Test-ZoneAgentAccess.ps1` — M365 Admin Center agent access settings verification per zone policy with admin exclusion group and deployment group validation
- `agent-access-monitor/src/adaptive-card-zone-access-alert.json` (in FSI-AgentGov-Solutions) — Teams adaptive card template for zone access policy drift notifications
- SHA-256 integrity-hashed evidence export across all scripts
- JSON output structured for Dataverse ingestion

**Regulatory Alignment:**

- FINRA 4511 (Books and Records — Agent Security Configuration Evidence)
- FINRA 3110 (Supervision — Agent Access Controls)
- SEC 17a-3/4 (Recordkeeping — Security Configuration Audit Trail)
- SOX 302/404 (Internal Controls — Authentication and Access Governance)
- GLBA 501(b) (Safeguards — Agent Security Posture Verification)
- OCC 2011-12 (Model Risk Management — Configuration Governance)

**Related Controls:**

- [1.1 - Restrict Agent Publishing by Authorization](../controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md)
- [3.7 - PPAC Security Posture Assessment](../controls/pillar-3-reporting/3.7-ppac-security-posture-assessment.md)
- [3.8 - Copilot Hub and Governance Dashboard](../controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md)

**Script Locations:**

- `scripts/governance/Test-AgentAuthConfiguration.ps1`
- `scripts/governance/restrict-agent-publishing.ps1`
- `scripts/governance/Test-ZoneAgentAccess.ps1`

---

### MIME Type Restrictions for File Uploads

!!! success "Production Ready"
    v1.0.0 includes a PowerShell module for zone-based MIME type configuration management, Dataverse plugin for server-side magic bytes validation in Zone 3, Purview DLP policy template for executable file blocking, Sentinel monitoring queries and analytics alert rules, and exception management workflow.

Helps prevent malicious or high-risk file types from being uploaded to AI agent conversations. Provides zone-aware MIME type restriction configuration, server-side file content validation using magic bytes analysis, DLP policy integration for executable blocking, and centralized monitoring through Microsoft Sentinel.

**Version:** v1.0.0
**Status:** Completed

**Components:**

- `scripts/governance/FsiMimeControl.psm1` — PowerShell module with Get/Set/Test cmdlets and zone templates for MIME type configuration management (in FSI-AgentGov)
- `mime-type-restrictions/src/ValidateMimeTypePlugin.cs` — Dataverse plugin for server-side magic bytes validation in Zone 3 environments (in FSI-AgentGov-Solutions)
- `mime-type-restrictions/src/dlp-policy-template.json` — Purview DLP policy template for executable file blocking (in FSI-AgentGov-Solutions)
- `mime-type-restrictions/src/query-mime-blocks.kql` — Sentinel KQL query for MIME type block event monitoring (in FSI-AgentGov-Solutions)
- `mime-type-restrictions/src/high-volume-blocks.json` — Sentinel analytics alert rule ARM template for high-volume block detection (in FSI-AgentGov-Solutions)
- `scripts/governance/mime-type-exceptions.csv` — Exception register with validation script and request template (in FSI-AgentGov)

**Regulatory Alignment:**

- FINRA 4511/3110 (Books and Records — File Upload Governance Evidence)
- SEC 17a-4 (Recordkeeping — Upload Restriction Audit Trail)
- GLBA 501(b) (Safeguards — File Type Restriction Controls)
- OCC 2011-12 (Model Risk Management — Input Validation Governance)

**Related Controls:**

- [1.5 - Data Loss Prevention (DLP) and Sensitivity Labels](../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md)
- [1.10 - Communication Compliance Monitoring](../controls/pillar-1-security/1.10-communication-compliance-monitoring.md)
- [1.11 - Conditional Access and Phishing-Resistant MFA](../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md)
- [1.13 - Sensitive Information Types (SITs) and Pattern Recognition](../controls/pillar-1-security/1.13-sensitive-information-types-sits-and-pattern-recognition.md)
- [1.14 - Data Minimization and Agent Scope Control](../controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md)
- [1.25 - MIME Type Restrictions for File Uploads](../controls/pillar-1-security/1.25-mime-type-restrictions.md)
- [3.3 - Compliance and Regulatory Reporting](../controls/pillar-3-reporting/3.3-compliance-and-regulatory-reporting.md)
- [3.7 - PPAC Security Posture Assessment](../controls/pillar-3-reporting/3.7-ppac-security-posture-assessment.md)
- [4.3 - Site and Document Retention Management](../controls/pillar-4-sharepoint/4.3-site-and-document-retention-management.md)

**Script Locations:**

- `scripts/governance/FsiMimeControl.psm1` (FSI-AgentGov)
- `mime-type-restrictions/src/ValidateMimeTypePlugin.cs` (FSI-AgentGov-Solutions)
- `mime-type-restrictions/src/dlp-policy-template.json` (FSI-AgentGov-Solutions)
- `mime-type-restrictions/src/query-mime-blocks.kql` (FSI-AgentGov-Solutions)
- `mime-type-restrictions/src/high-volume-blocks.json` (FSI-AgentGov-Solutions)

**Repository Link:** [mime-type-restrictions](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/mime-type-restrictions)

**Version History:**

| Version | Date | Changes |
|---------|------|---------|
| v1.0.0 | February 2026 | Initial release |

---

### Inactivity Timeout Enforcement

!!! success "Production Ready"
    v1.0.0 includes a Cloud Flow for daily compliance scanning, PowerShell remediation script, Dataverse schema for policy management and compliance persistence, and zone-based maximum duration enforcement.

Helps validate and enforce Power Platform user inactivity timeout settings across multiple environments. Provides zone-aware policy-driven maximum duration requirements, automated compliance scanning via BAP Admin API, immutable Dataverse compliance records, and PowerShell-based remediation.

**Version:** v1.0.0
**Status:** Completed

**Components:**

- `inactivity-timeout-enforcement/src/detect-inactivity-timeout-noncompliance.json` — Cloud Flow template for daily compliance detection and evaluation (in FSI-AgentGov-Solutions)
- `scripts/governance/Set-InactivityTimeout.ps1` — PowerShell remediation script for BAP Admin API PATCH operations (in FSI-AgentGov)
- `scripts/governance/Set-InactivityTimeout.Tests.ps1` — Pester 5 validation test suite (28 tests) (in FSI-AgentGov)
- `scripts/create_timeout_dataverse_schema.py` — Dataverse schema creation (environmentpolicy + compliance tables) (in FSI-AgentGov)
- `scripts/create_timeout_errorlog_schema.py` — Dataverse error log table schema (in FSI-AgentGov)
- `scripts/create_timeout_environment_variables.py` — Environment variable definitions (in FSI-AgentGov)
- `scripts/create_timeout_connection_references.py` — Connection reference definitions (in FSI-AgentGov)

**Regulatory Alignment:**

- GLBA 501(b) (Safeguards — Session Security Controls)
- SOX 302 (Management Certification — Access Control Evidence)
- FINRA 4511 (Books and Records — Session Governance Documentation)
- NIST 800-53 AC-11/AC-12 (Session Lock and Termination)

**Related Controls:**

- [2.22 - Inactivity Timeout Enforcement](../controls/pillar-2-management/2.22-inactivity-timeout-enforcement.md)
- [1.23 - Step-Up Authentication for AI Agent Operations](../controls/pillar-1-security/1.23-step-up-authentication-for-agent-operations.md)
- [1.26 - Agent File Upload Restrictions](../controls/pillar-1-security/1.26-agent-file-upload-and-file-analysis-restrictions.md)
- [1.27 - Content Moderation Enforcement](../controls/pillar-1-security/1.27-ai-agent-content-moderation-enforcement.md)
- [2.1 - Managed Environments](../controls/pillar-2-management/2.1-managed-environments.md)
- [3.7 - PPAC Security Posture Assessment](../controls/pillar-3-reporting/3.7-ppac-security-posture-assessment.md)
- [3.8 - Copilot Hub](../controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md)

**Script Locations:**

- `scripts/governance/Set-InactivityTimeout.ps1` (FSI-AgentGov)
- `scripts/governance/Set-InactivityTimeout.Tests.ps1` (FSI-AgentGov)
- `inactivity-timeout-enforcement/src/detect-inactivity-timeout-noncompliance.json` (FSI-AgentGov-Solutions)
- `scripts/create_timeout_dataverse_schema.py` (FSI-AgentGov)
- `scripts/create_timeout_errorlog_schema.py` (FSI-AgentGov)
- `scripts/create_timeout_environment_variables.py` (FSI-AgentGov)
- `scripts/create_timeout_connection_references.py` (FSI-AgentGov)

**Repository Link:** [inactivity-timeout-enforcement](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/inactivity-timeout-enforcement)

**Version History:**

| Version | Date | Changes |
|---------|------|---------|
| v1.0.0 | February 2026 | Initial release |

---

### Agent Sharing Access Restriction Detector

!!! success "Production Ready"
    v1.0.0 includes daily detection flow with 5 restriction rules, approval-based remediation workflow, PowerShell exception management scripts, Dataverse persistence, SHA-256 evidence export, and zone-based policy enforcement.

Continuous detection and proactive restriction of Copilot Studio agent sharing configurations that exceed zone-based access policies. Enforces organizational sharing limits, helps prevent public internet links, validates approved group access, restricts excessive individual shares, and blocks cross-tenant access — with structured approval workflows and time-bound exception management.

**Components:**

- Daily detection flow scanning all agents via BAP APIs with 5 restriction rules per zone policy
- Approval-based remediation workflow with sequential dual approval (Security → Data Owner)
- Exception management PowerShell scripts with approval tracking and expiration enforcement
- Dataverse schema (4 tables) for zone policy definitions, restriction tracking, and exception persistence
- SHA-256 evidence export for examination readiness
- Teams adaptive card alerts with severity-based styling and action buttons
- Deployment scripts for automated environment configuration

**Regulatory Alignment:**

- FINRA 4511 (Books and Records — Agent Sharing Access Configuration)
- SOX 302/404 (Internal Controls — Sharing Policy Enforcement)
- GLBA 501(b) (Safeguards — Agent Access Controls)
- SEC 17a-3/4 (Recordkeeping — Sharing Restriction Audit Trail)
- OCC 2011-12 (Model Risk Management — Access Governance)

**Related Controls:**

- [1.18 - Application-Level Authorization and Role-Based Access Control](../controls/pillar-1-security/1.18-application-level-authorization-and-role-based-access-control-rbac.md)
- [2.8 - Access Control and Segregation of Duties](../controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md)

**Framework Playbooks:**

- [ASARD Deployment Guide](../playbooks/asard-deployment-guide.md)
- [ASARD Exception Management](../playbooks/asard-exception-management.md)
- [ASARD Troubleshooting Guide](../playbooks/asard-troubleshooting-guide.md)

!!! info "Complementary Relationship with UASD"
    ASARD complements the [Unrestricted Agent Sharing Detector](#unrestricted-agent-sharing-detector). UASD provides reactive detection of overly permissive sharing with approval-based remediation. ASARD provides proactive restriction enforcement with policy-based prevention and exception workflows. Together, they provide defense-in-depth for agent sharing governance — UASD for detection and reactive remediation, ASARD for proactive prevention and policy enforcement.

**Version History:**

| Version | Date | Changes |
|---------|------|---------|
| v1.0.0 | February 2026 | Initial release |

**Repository Link:** [agent-sharing-access-restriction-detector](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/agent-sharing-access-restriction-detector)

---

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
| Agent Access Governance Monitor | v1.0.0 | February 2026 |
| Agent Observability Foundation | v1.1.0 | February 2026 |
| Audit Compliance Manager | v1.0.0 | February 2026 |
| Environment Lifecycle Management | v1.1.2 | January 2026 |
| Message Center Monitor | v2.1.1 | January 2026 |
| Pipeline Governance Cleanup | v1.0.8 | January 2026 |
| Deny Event Correlation Report | v2.0.0 | February 2026 |
| FINRA Supervision Workflow | v1.0.0 | February 2026 |
| Conditional Access Automation | v1.1.0 | February 2026 |
| Content Moderation Governance Monitor | v1.0.0 | February 2026 |
| Compliance Dashboard | v1.0.0 | February 2026 |
| Segregation of Duties Detector | v1.0.0 | February 2026 |
| Scope Drift Monitor | v1.1.0 | February 2026 |
| Session Security Configurator | v1.0.0 | February 2026 |
| RAG Source Validator | v1.0.0 | February 2026 |
| COI Testing Framework | v1.0.0 | February 2026 |
| Hallucination Tracker | v1.0.0 | February 2026 |
| DR Testing Framework | v1.0.0 | February 2026 |
| File Upload Security Configurator | v1.0.0 | February 2026 |
| Cross-Solution Integration | v1.0.0 | February 2026 |
| Configuration Hardening Baseline | v1.1.0 | February 2026 |
| Agent Usage & Performance Workbook | v1.0.0 | February 2026 |
| Unrestricted Agent Sharing Detector | v1.0.0 | February 2026 |
| Agent Sharing Access Restriction Detector | v1.0.0 | February 2026 |
| Agent Security Configuration Governance | v1.0.0 | February 2026 |
| MIME Type Restrictions for File Uploads | v1.0.0 | February 2026 |
| Inactivity Timeout Enforcement | v1.0.0 | February 2026 |

---

*FSI Agent Governance Framework v1.2.48 - February 2026*
