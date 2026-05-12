# Solutions Index

Live inventory reference for the companion FSI-AgentGov-Solutions repository.

---

## Overview

This index tracks the **35 live solution implementations** in the companion **[FSI-AgentGov-Solutions](https://github.com/judeper/FSI-AgentGov-Solutions)** repository.

Companion solutions provide deployment documentation, governance scripts, KQL queries, and templates for manual Power Platform builds. They do not store exported Power Platform runtime artifacts in this catalog.

This file is intentionally folder-driven to reduce drift: live solution implementations are derived from top-level companion repository folders with root `README.md` files. Framework-native assets without matching solution folders remain documented in FSI-AgentGov and are not counted as companion solutions here.

*Control coverage listed below reflects the primary controls published with each live solution.*

## Coverage scope

Not all 78 controls have a companion solution in FSI-AgentGov-Solutions. Solution mapping is selective by design.

Companion solutions are published when dedicated automation adds value beyond what Microsoft's native admin surfaces already provide. Many controls are operated entirely via native admin surfaces — Microsoft Purview, Entra ID, and the Power Platform Admin Center — and verified by the framework's own assessment-engine collectors rather than by a standalone solution.

Each control's `automation` field in [`assessment/manifest/controls.json`](https://github.com/judeper/FSI-AgentGov/blob/main/assessment/manifest/controls.json) (`full`, `partial`, or `manual`) describes verification feasibility independent of whether a companion solution exists. A control can be fully automated through collectors without needing a dedicated solution folder.

Absence of a control from this catalog is not a coverage gap — it reflects the framework's selective-mapping principle, which helps keep the companion repository focused on automation that supports outcomes the native surfaces do not deliver on their own.

## Discovering by CAPE alignment

Each live solution declares the Microsoft CAPE [Frontier Transformation Pattern](../framework/transformation-patterns.md) it supports, the [Agentic Capability Driver](../framework/agentic-capability-drivers.md) it strengthens, and the [Center of Excellence function](../framework/agentic-coe.md) (Govern, Enable, Optimize, or Scale) it serves. These tags let admins, AI Governance Leads, and CSAs filter the catalog by the lens that matters for the conversation in front of them — a pattern-first conversation pulls a different shortlist than a CoE-readiness conversation.

Pattern, Driver, and CoE columns appear in the live inventory table below and are repeated as bullets in each solution's detail block. The companion [Pattern coverage matrix (showing which solutions support each pattern)](pattern-coverage.md) aggregates the same metadata across all 78 controls and 35 solutions for portfolio-level review.

## Live Inventory (35 Solutions)

| Solution | Repository folder | Version | Primary controls | Patterns | Drivers | CoE | Summary |
|----------|-------------------|---------|------------------|----------|---------|-----|---------|
| [Action Confirmation Auditor](#action-confirmation-auditor) | [`action-confirmation-auditor`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/action-confirmation-auditor) | v1.2.0 | 1.23 | P4, P5, P6 | AI Governance, Technology & Data | Govern | Step-up confirmation validation for agent actions. |
| [Agent 365 Lifecycle Governance](#agent-365-lifecycle-governance) | [`agent-365-lifecycle-governance`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/agent-365-lifecycle-governance) | v1.1.4 | 2.3, 1.2, 1.11, 2.1, 2.8, 2.12, 3.1 | P4, P5, P6 | AI Governance, AI Strategy, Technology & Data | Enable | Automated lifecycle governance for AI agents using Agent 365 and Entra ID Governance. |
| [Agent Access Monitor](#agent-access-monitor) | [`agent-access-monitor`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/agent-access-monitor) | v1.1.1 | 3.8 | P1, P4 | AI Governance, Technology & Data | Optimize | Automated detection of overly permissive agent access configurations. |
| [Agent Communication Restriction Detector](#agent-communication-restriction-detector) | [`agent-communication-restriction-detector`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/agent-communication-restriction-detector) | v1.2.0 | 2.17 | P6 | AI Governance, Technology & Data | Govern | Inter-agent communication restriction validation. |
| [Agent Knowledge Source Scanner](#agent-knowledge-source-scanner) | [`agent-knowledge-source-scanner`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/agent-knowledge-source-scanner) | v1.1.1 | 4.3, 1.4, 1.5 | P2 | AI Governance, Technology & Data | Govern | Item-level permission scanning for agent knowledge source SharePoint libraries. |
| [Agent Observability Foundation](#agent-observability-foundation) | [`agent-observability-foundation`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/agent-observability-foundation) | v1.2.1 | — | P4, P5, P6 | Technology & Data, AI Governance | Optimize | Foundational observability infrastructure for agent monitoring. |
| [Agent Registry Automation](#agent-registry-automation) | [`agent-registry-automation`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/agent-registry-automation) | v2.1.0 | 1.2, 1.7, 2.1, 2.13 | P1, P2, P4 | AI Governance, AI Strategy, Technology & Data | Enable | Automated discovery, registration, approval, and lifecycle governance of AI agents. |
| [Agent Sharing Access Restriction Detector](#agent-sharing-access-restriction-detector) | [`agent-sharing-access-restriction-detector`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/agent-sharing-access-restriction-detector) | v2.0.1 | 1.18, 2.8 | P1, P2 | AI Governance, Technology & Data | Govern | Zone-based agent sharing policy enforcement with approval workflows. |
| [Audit Compliance Manager](#audit-compliance-manager) | [`audit-compliance-manager`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/audit-compliance-manager) | v1.0.4 | 1.7 | P4, P5, P6 | AI Governance, Technology & Data | Govern | Audit configuration validation, gap detection, and remediation workflows. |
| [COI Testing](#coi-testing) | [`coi-testing`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/coi-testing) | v1.1.1 | 2.18, 2.11, 2.5 | P4, P5 | AI Governance | Govern | Conflict of interest testing for agent recommendations. |
| [Compliance Dashboard](#compliance-dashboard) | [`compliance-dashboard`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/compliance-dashboard) | v1.0.4 | 3.3, 3.1, 3.2 | P4, P5, P6 | AI Governance, Technology & Data | Optimize | Aggregated compliance reporting across the framework control catalog with Exchange coverage. |
| [Conditional Access Automation](#conditional-access-automation) | [`conditional-access-automation`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/conditional-access-automation) | v2.0.1 | 1.11, 1.23, 1.18 | P4, P5, P6 | AI Governance, Technology & Data | Govern | CA policy deployment, compliance monitoring, and drift detection. |
| [Content Moderation Monitor](#content-moderation-monitor) | [`content-moderation-monitor`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/content-moderation-monitor) | v1.1.1 | 1.8, 1.14 | P1, P5 | AI Governance, Technology & Data | Optimize | Per-agent content moderation validation against zone requirements. |
| [Copilot Studio Analytics](#copilot-studio-analytics) | [`copilot-studio-analytics`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/copilot-studio-analytics) | v2.0.1 | 3.2 | P1, P4 | AI Governance, Technology & Data | Optimize | Business impact analytics for Copilot Studio agents. |
| [Credential Oversharing Detector](#credential-oversharing-detector) | [`credential-oversharing-detector`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/credential-oversharing-detector) | v2.1.0 | 1.14, 1.4, 1.18 | P3, P4 | AI Governance, Technology & Data | Govern | Scans Copilot Studio agent credentials against zone policy to detect overprivileged connectors, excessive OAuth scopes, unauthorized service accounts, cross-environment sharing, and stale credentials. |
| [Cross-Solution Integration](#cross-solution-integration)| [`cross-solution-integration`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/cross-solution-integration) | v2.0.2 | 1.7, 1.23, 1.11, 3.8, 1.8, 1.14 | P4, P5, P6 | AI Governance, Technology & Data | Scale | Wires Tier 2 companion solutions into Compliance Dashboard. |
| [Cross-Tenant External Sharing Governance](#cross-tenant-external-sharing-governance) | [`cross-tenant-external-sharing-governance`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/cross-tenant-external-sharing-governance) | v1.0.3 | 1.1, 1.18, 2.1, 2.8, 3.1, 1.11 | P1, P5 | AI Governance, Technology & Data | Govern | Three-layer cross-tenant access governance covering tenant isolation, Entra cross-tenant access, and agent sharing. |
| [Deny Event Correlation Report](#deny-event-correlation-report) | [`deny-event-correlation-report`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/deny-event-correlation-report) | v2.0.3 | 1.5, 1.7, 1.8, 3.4 | P4, P5, P6 | AI Governance, Technology & Data | Optimize | Daily deny event correlation across Purview, DLP, and Application Insights. |
| [DR Testing Framework](#dr-testing-framework) | [`dr-testing-framework`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/dr-testing-framework) | v2.0.1 | 2.4, 2.1, 1.9 | P4, P5 | AI Governance, Technology & Data | Govern | Automated disaster recovery testing for AI agents. |
| [Environment Lifecycle Management](#environment-lifecycle-management) | [`environment-lifecycle-management`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/environment-lifecycle-management) | v1.2.1 | 2.1, 2.2, 2.3, 2.8, 1.7 | P1, P2, P4 | AI Governance, Technology & Data | Enable | Automated environment provisioning with zone-based governance. |
| [File Upload Security](#file-upload-security) | [`file-upload-security`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/file-upload-security) | v1.1.1 | 1.14, 1.8, 1.4 | P1, P3 | AI Governance, Technology & Data | Govern | Per-agent file upload validation against zone governance policies. |
| [FINRA Supervision Workflow](#finra-supervision-workflow) | [`finra-supervision-workflow`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/finra-supervision-workflow) | v1.1.0 | 2.12, 1.10, 1.7 | P4, P5 | AI Governance, Business Strategy, Organization & Culture | Govern | Automated supervision queue for AI agent outputs. |
| [Generative AI Config Auditor](#generative-ai-config-auditor) | [`generative-ai-config-auditor`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/generative-ai-config-auditor) | v1.2.0 | 2.24 | P1, P2, P4 | AI Governance | Govern | GenAI feature enablement governance by governance zone. |
| [Hallucination Tracker](#hallucination-tracker) | [`hallucination-tracker`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/hallucination-tracker) | v1.2.0 | 3.10, 2.9, 2.12 | P2, P4, P5 | AI Governance, Business Strategy, Technology & Data | Optimize | Feedback aggregation for hallucination pattern analysis. |
| [HITL Workflow Governance](#hitl-workflow-governance) | [`hitl-workflow-governance`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/hitl-workflow-governance) | v1.1.1 | 2.12, 2.17, 1.10 | P4, P5, P6 | AI Governance, Organization & Culture | Govern | Validates that Copilot Studio agent flows include required human-in-the-loop checkpoints per zone governance policy using the Request for Information and Run a Multistage Approval actions from the advancedapprovals connector. |
| [Inactivity Timeout Enforcement](#inactivity-timeout-enforcement)| [`inactivity-timeout-enforcement`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/inactivity-timeout-enforcement) | v1.1.1 | 2.22, 1.23, 3.7, 3.8 | P1, P3 | AI Governance, Technology & Data | Govern | Policy-driven inactivity timeout validation with zone-based durations. |
| [Message Center Monitor](#message-center-monitor) | [`message-center-monitor`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/message-center-monitor) | v2.5.1 | 2.3, 2.10 | P4, P5, P6 | AI Governance, Technology & Data | Scale | M365 Message Center monitoring for platform changes. |
| [MIME Type Restrictions](#mime-type-restrictions) | [`mime-type-restrictions`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/mime-type-restrictions) | v1.2.1 | 1.5, 1.10, 1.11, 1.13, 1.14, 1.25, 3.3, 3.7, 4.3 | P1, P2, P3 | AI Governance, Technology & Data | Govern | Zone-based MIME type configuration with server-side validation. |
| [Model Risk Management Automation](#model-risk-management-automation) | [`model-risk-management-automation`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/model-risk-management-automation) | v1.0.3 | 2.6, 2.5, 2.9, 2.11, 2.13, 3.1, 1.2 | P4, P5, P6 | AI Governance, AI Strategy | Govern | OCC 2011-12 / SR 26-2 (formerly SR 11-7) model risk management with inventory, risk scoring, validation workflows, and Agent Card generation. |
| [Pipeline Governance Cleanup](#pipeline-governance-cleanup) | [`pipeline-governance-cleanup`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/pipeline-governance-cleanup) | v1.2.1 | 2.3, 2.1 | P1, P4 | AI Governance, Technology & Data | Enable | Personal pipeline discovery and ALM governance enforcement. |
| [RAG Source Validator](#rag-source-validator) | [`rag-source-validator`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/rag-source-validator) | v1.3.0 | 2.16, 1.7, 2.13 | P2 | AI Governance, Technology & Data | Govern | Integrity validation for RAG knowledge sources. |
| [Scope Drift Monitor](#scope-drift-monitor) | [`scope-drift-monitor`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/scope-drift-monitor) | v1.2.1 | 1.14, 1.4, 1.5 | P2, P4 | AI Governance, Technology & Data | Optimize | Detect agent data access beyond declared scope. |
| [Segregation Detector](#segregation-detector) | [`segregation-detector`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/segregation-detector) | v1.2.0 | 2.8, 2.1, 2.3 | P3, P4 | AI Governance, Technology & Data | Govern | Role conflict detection for Maker/Checker enforcement. |
| [Session Security Configurator](#session-security-configurator) | [`session-security-configurator`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/session-security-configurator) | v1.2.0 | 1.23, 1.11 | P1, P4, P5 | AI Governance, Technology & Data | Govern | Session security validation per governance zone with drift detection. |
| [Unrestricted Agent Sharing Detector](#unrestricted-agent-sharing-detector) | [`unrestricted-agent-sharing-detector`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/unrestricted-agent-sharing-detector) | v2.0.1 | 1.1, 3.8 | P1, P5 | AI Governance, Technology & Data | Optimize | Continuous detection of overly permissive agent sharing. |

## Solution Details

### Action Confirmation Auditor
- **Repository folder:** [`action-confirmation-auditor`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/action-confirmation-auditor)
- **Version:** v1.2.0
- **Primary controls:** 1.23
- **Patterns:** P4, P5, P6
- **Drivers:** AI Governance, Technology & Data
- **CoE function:** Govern
- **Summary:** Step-up confirmation validation for agent actions.

### Agent 365 Lifecycle Governance
- **Repository folder:** [`agent-365-lifecycle-governance`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/agent-365-lifecycle-governance)
- **Version:** v1.1.4
- **Primary controls:** 2.3, 1.2, 1.11, 2.1, 2.8, 2.12, 3.1
- **Patterns:** P4, P5, P6
- **Drivers:** AI Governance, AI Strategy, Technology & Data
- **CoE function:** Enable
- **Summary:** Automated lifecycle governance for AI agents using Agent 365 and Entra ID Governance.

### Agent Access Monitor
- **Repository folder:** [`agent-access-monitor`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/agent-access-monitor)
- **Version:** v1.1.1
- **Primary controls:** 3.8
- **Patterns:** P1, P4
- **Drivers:** AI Governance, Technology & Data
- **CoE function:** Optimize
- **Summary:** Automated detection of overly permissive agent access configurations.

### Agent Communication Restriction Detector
- **Repository folder:** [`agent-communication-restriction-detector`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/agent-communication-restriction-detector)
- **Version:** v1.2.0
- **Primary controls:** 2.17
- **Patterns:** P6
- **Drivers:** AI Governance, Technology & Data
- **CoE function:** Govern
- **Summary:** Inter-agent communication restriction validation.

### Agent Knowledge Source Scanner
- **Repository folder:** [`agent-knowledge-source-scanner`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/agent-knowledge-source-scanner)
- **Version:** v1.1.1
- **Primary controls:** 4.3, 1.4, 1.5
- **Patterns:** P2
- **Drivers:** AI Governance, Technology & Data
- **CoE function:** Govern
- **Summary:** Item-level permission scanning for agent knowledge source SharePoint libraries.

### Agent Observability Foundation
- **Repository folder:** [`agent-observability-foundation`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/agent-observability-foundation)
- **Version:** v1.2.1
- **Primary controls:** —
- **Patterns:** P4, P5, P6
- **Drivers:** Technology & Data, AI Governance
- **CoE function:** Optimize
- **Summary:** Foundational observability infrastructure for agent monitoring.

### Agent Registry Automation
- **Repository folder:** [`agent-registry-automation`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/agent-registry-automation)
- **Version:** v2.1.0
- **Primary controls:** 1.2, 1.7, 2.1, 2.13
- **Patterns:** P1, P2, P4
- **Drivers:** AI Governance, AI Strategy, Technology & Data
- **CoE function:** Enable
- **Summary:** Automated discovery, registration, approval, and lifecycle governance of AI agents.

### Agent Sharing Access Restriction Detector
- **Repository folder:** [`agent-sharing-access-restriction-detector`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/agent-sharing-access-restriction-detector)
- **Version:** v2.0.1
- **Primary controls:** 1.18, 2.8
- **Patterns:** P1, P2
- **Drivers:** AI Governance, Technology & Data
- **CoE function:** Govern
- **Summary:** Zone-based agent sharing policy enforcement with approval workflows.

### Audit Compliance Manager
- **Repository folder:** [`audit-compliance-manager`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/audit-compliance-manager)
- **Version:** v1.0.4
- **Primary controls:** 1.7
- **Patterns:** P4, P5, P6
- **Drivers:** AI Governance, Technology & Data
- **CoE function:** Govern
- **Summary:** Audit configuration validation, gap detection, and remediation workflows.

### COI Testing
- **Repository folder:** [`coi-testing`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/coi-testing)
- **Version:** v1.1.1
- **Primary controls:** 2.18, 2.11, 2.5
- **Patterns:** P4, P5
- **Drivers:** AI Governance
- **CoE function:** Govern
- **Summary:** Conflict of interest testing for agent recommendations.

### Compliance Dashboard
- **Repository folder:** [`compliance-dashboard`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/compliance-dashboard)
- **Version:** v1.0.4
- **Primary controls:** 3.3, 3.1, 3.2
- **Patterns:** P4, P5, P6
- **Drivers:** AI Governance, Technology & Data
- **CoE function:** Optimize
- **Summary:** Aggregated compliance reporting across the framework control catalog with Exchange coverage.

### Conditional Access Automation
- **Repository folder:** [`conditional-access-automation`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/conditional-access-automation)
- **Version:** v2.0.1
- **Primary controls:** 1.11, 1.23, 1.18
- **Patterns:** P4, P5, P6
- **Drivers:** AI Governance, Technology & Data
- **CoE function:** Govern
- **Summary:** CA policy deployment, compliance monitoring, and drift detection.

### Content Moderation Monitor
- **Repository folder:** [`content-moderation-monitor`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/content-moderation-monitor)
- **Version:** v1.1.1
- **Primary controls:** 1.8, 1.14
- **Patterns:** P1, P5
- **Drivers:** AI Governance, Technology & Data
- **CoE function:** Optimize
- **Summary:** Per-agent content moderation validation against zone requirements.

### Copilot Studio Analytics
- **Repository folder:** [`copilot-studio-analytics`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/copilot-studio-analytics)
- **Version:** v2.0.1
- **Primary controls:** 3.2
- **Patterns:** P1, P4
- **Drivers:** AI Governance, Technology & Data
- **CoE function:** Optimize
- **Summary:** Business impact analytics for Copilot Studio agents.

### Credential Oversharing Detector
- **Repository folder:** [`credential-oversharing-detector`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/credential-oversharing-detector)
- **Version:** v2.1.0
- **Primary controls:** 1.14, 1.4, 1.18
- **Patterns:** P3, P4
- **Drivers:** AI Governance, Technology & Data
- **CoE function:** Govern
- **Summary:** Scans Copilot Studio agent credentials against zone policy to detect overprivileged connectors, excessive OAuth scopes, unauthorized service accounts, cross-environment sharing, and stale credentials.

### Cross-Solution Integration
- **Repository folder:** [`cross-solution-integration`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/cross-solution-integration)
- **Version:** v2.0.2
- **Primary controls:** 1.7, 1.23, 1.11, 3.8, 1.8, 1.14
- **Patterns:** P4, P5, P6
- **Drivers:** AI Governance, Technology & Data
- **CoE function:** Scale
- **Summary:** Wires Tier 2 companion solutions into Compliance Dashboard.

### Cross-Tenant External Sharing Governance
- **Repository folder:** [`cross-tenant-external-sharing-governance`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/cross-tenant-external-sharing-governance)
- **Version:** v1.0.3
- **Primary controls:** 1.1, 1.18, 2.1, 2.8, 3.1, 1.11
- **Patterns:** P1, P5
- **Drivers:** AI Governance, Technology & Data
- **CoE function:** Govern
- **Summary:** Three-layer cross-tenant access governance covering tenant isolation, Entra cross-tenant access, and agent sharing.

### Deny Event Correlation Report
- **Repository folder:** [`deny-event-correlation-report`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/deny-event-correlation-report)
- **Version:** v2.0.3
- **Primary controls:** 1.5, 1.7, 1.8, 3.4
- **Patterns:** P4, P5, P6
- **Drivers:** AI Governance, Technology & Data
- **CoE function:** Optimize
- **Summary:** Daily deny event correlation across Purview, DLP, and Application Insights.

### DR Testing Framework
- **Repository folder:** [`dr-testing-framework`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/dr-testing-framework)
- **Version:** v2.0.1
- **Primary controls:** 2.4, 2.1, 1.9
- **Patterns:** P4, P5
- **Drivers:** AI Governance, Technology & Data
- **CoE function:** Govern
- **Summary:** Automated disaster recovery testing for AI agents.

### Environment Lifecycle Management
- **Repository folder:** [`environment-lifecycle-management`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/environment-lifecycle-management)
- **Version:** v1.2.1
- **Primary controls:** 2.1, 2.2, 2.3, 2.8, 1.7
- **Patterns:** P1, P2, P4
- **Drivers:** AI Governance, Technology & Data
- **CoE function:** Enable
- **Summary:** Automated environment provisioning with zone-based governance.

### File Upload Security
- **Repository folder:** [`file-upload-security`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/file-upload-security)
- **Version:** v1.1.1
- **Primary controls:** 1.14, 1.8, 1.4
- **Patterns:** P1, P3
- **Drivers:** AI Governance, Technology & Data
- **CoE function:** Govern
- **Summary:** Per-agent file upload validation against zone governance policies.

### FINRA Supervision Workflow
- **Repository folder:** [`finra-supervision-workflow`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/finra-supervision-workflow)
- **Version:** v1.1.0
- **Primary controls:** 2.12, 1.10, 1.7
- **Patterns:** P4, P5
- **Drivers:** AI Governance, Business Strategy, Organization & Culture
- **CoE function:** Govern
- **Summary:** Automated supervision queue for AI agent outputs.

### Generative AI Config Auditor
- **Repository folder:** [`generative-ai-config-auditor`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/generative-ai-config-auditor)
- **Version:** v1.2.0
- **Primary controls:** 2.24
- **Patterns:** P1, P2, P4
- **Drivers:** AI Governance
- **CoE function:** Govern
- **Summary:** GenAI feature enablement governance by governance zone.

### Hallucination Tracker
- **Repository folder:** [`hallucination-tracker`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/hallucination-tracker)
- **Version:** v1.2.0
- **Primary controls:** 3.10, 2.9, 2.12
- **Patterns:** P2, P4, P5
- **Drivers:** AI Governance, Business Strategy, Technology & Data
- **CoE function:** Optimize
- **Summary:** Feedback aggregation for hallucination pattern analysis.

### HITL Workflow Governance
- **Repository folder:** [`hitl-workflow-governance`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/hitl-workflow-governance)
- **Version:** v1.1.1
- **Primary controls:** 2.12, 2.17, 1.10
- **Patterns:** P4, P5, P6
- **Drivers:** AI Governance, Organization & Culture
- **CoE function:** Govern
- **Summary:** Validates that Copilot Studio agent flows include required human-in-the-loop checkpoints per zone governance policy using the Request for Information and Run a Multistage Approval actions from the advancedapprovals connector.

### Inactivity Timeout Enforcement
- **Repository folder:** [`inactivity-timeout-enforcement`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/inactivity-timeout-enforcement)
- **Version:** v1.1.1
- **Primary controls:** 2.22, 1.23, 3.7, 3.8
- **Patterns:** P1, P3
- **Drivers:** AI Governance, Technology & Data
- **CoE function:** Govern
- **Summary:** Policy-driven inactivity timeout validation with zone-based durations.

### Message Center Monitor
- **Repository folder:** [`message-center-monitor`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/message-center-monitor)
- **Version:** v2.5.1
- **Primary controls:** 2.3, 2.10
- **Patterns:** P4, P5, P6
- **Drivers:** AI Governance, Technology & Data
- **CoE function:** Scale
- **Summary:** M365 Message Center monitoring for platform changes.

### MIME Type Restrictions
- **Repository folder:** [`mime-type-restrictions`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/mime-type-restrictions)
- **Version:** v1.2.1
- **Primary controls:** 1.5, 1.10, 1.11, 1.13, 1.14, 1.25, 3.3, 3.7, 4.3
- **Patterns:** P1, P2, P3
- **Drivers:** AI Governance, Technology & Data
- **CoE function:** Govern
- **Summary:** Zone-based MIME type configuration with server-side validation.

### Model Risk Management Automation
- **Repository folder:** [`model-risk-management-automation`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/model-risk-management-automation)
- **Version:** v1.0.3
- **Primary controls:** 2.6, 2.5, 2.9, 2.11, 2.13, 3.1, 1.2
- **Patterns:** P4, P5, P6
- **Drivers:** AI Governance, AI Strategy
- **CoE function:** Govern
- **Summary:** OCC 2011-12 / SR 26-2 (formerly SR 11-7) model risk management with inventory, risk scoring, validation workflows, and Agent Card generation.

### Pipeline Governance Cleanup
- **Repository folder:** [`pipeline-governance-cleanup`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/pipeline-governance-cleanup)
- **Version:** v1.2.1
- **Primary controls:** 2.3, 2.1
- **Patterns:** P1, P4
- **Drivers:** AI Governance, Technology & Data
- **CoE function:** Enable
- **Summary:** Personal pipeline discovery and ALM governance enforcement.

### RAG Source Validator
- **Repository folder:** [`rag-source-validator`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/rag-source-validator)
- **Version:** v1.3.0
- **Primary controls:** 2.16, 1.7, 2.13
- **Patterns:** P2
- **Drivers:** AI Governance, Technology & Data
- **CoE function:** Govern
- **Summary:** Integrity validation for RAG knowledge sources.

### Scope Drift Monitor
- **Repository folder:** [`scope-drift-monitor`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/scope-drift-monitor)
- **Version:** v1.2.1
- **Primary controls:** 1.14, 1.4, 1.5
- **Patterns:** P2, P4
- **Drivers:** AI Governance, Technology & Data
- **CoE function:** Optimize
- **Summary:** Detect agent data access beyond declared scope.

### Segregation Detector
- **Repository folder:** [`segregation-detector`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/segregation-detector)
- **Version:** v1.2.0
- **Primary controls:** 2.8, 2.1, 2.3
- **Patterns:** P3, P4
- **Drivers:** AI Governance, Technology & Data
- **CoE function:** Govern
- **Summary:** Role conflict detection for Maker/Checker enforcement.

### Session Security Configurator
- **Repository folder:** [`session-security-configurator`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/session-security-configurator)
- **Version:** v1.2.0
- **Primary controls:** 1.23, 1.11
- **Patterns:** P1, P4, P5
- **Drivers:** AI Governance, Technology & Data
- **CoE function:** Govern
- **Summary:** Session security validation per governance zone with drift detection.

### Unrestricted Agent Sharing Detector
- **Repository folder:** [`unrestricted-agent-sharing-detector`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/unrestricted-agent-sharing-detector)
- **Version:** v2.0.1
- **Primary controls:** 1.1, 3.8
- **Patterns:** P1, P5
- **Drivers:** AI Governance, Technology & Data
- **CoE function:** Optimize
- **Summary:** Continuous detection of overly permissive agent sharing.
