# CAPE Pattern Coverage Matrix

This page is **generated** by `scripts/generate_pattern_coverage.py` from `assessment/manifest/controls.json`. Do not edit by hand.

It maps the 79 FSI-AgentGov controls to the 6 Microsoft CAPE Frontier Transformation Patterns. For each control:

- The **Patterns** column lists patterns where the control applies (`applicable_patterns`).
- The **Critical For** column lists patterns where the control is mission-critical (`pattern_critical`).
- A pattern-critical control means failure in that control would block the named pattern's deployment. Use this lens during pattern-specific risk reviews.

## Pattern legend

| ID | Pattern | Default zones |
|---|---|---|
| 1 | Employee AI Enablement | Z1 (Personal) |
| 2 | Business Expert Empowerment | Z2 (Team) |
| 3 | Workplace & IT Services | Z2 (Team) |
| 4 | Core Business Process Transformation | Z3 (Enterprise) |
| 5 | External Engagement | Z3 (Enterprise) |
| 6 | AI-First Capabilities | Z3 (Enterprise) — D3 guardrail applies |

## Coverage summary

| Pattern | Total controls applicable | Pattern-critical controls | Solutions count |
|---|---|---|---|
| 1 — Employee AI Enablement | 79 | 2 | 16 |
| 2 — Business Expert Empowerment | 79 | 1 | 10 |
| 3 — Workplace & IT Services | 79 | 1 | 5 |
| 4 — Core Business Process Transformation | 79 | 3 | 29 |
| 5 — External Engagement | 79 | 6 | 21 |
| 6 — AI-First Capabilities | 79 | 4 | 12 |

## Pattern-critical controls

The following controls are flagged as mission-critical for one or more patterns. Failure in any of these blocks the named pattern's safe deployment.

### Pattern 1 — Employee AI Enablement

- **1.1** Control 1.1: Restrict Agent Publishing by Authorization
- **2.14** Control 2.14: Training and Awareness Program

### Pattern 2 — Business Expert Empowerment

- **2.16** Control 2.16: RAG Source Integrity Validation

### Pattern 3 — Workplace & IT Services

- **2.8** Control 2.8: Access Control and Segregation of Duties

### Pattern 4 — Core Business Process Transformation

- **2.11** Control 2.11: Bias Testing and Fairness Assessment
- **2.12** Control 2.12: Supervision and Oversight (FINRA Rule 3110)
- **2.6** Control 2.6: Model Risk Management (OCC Bulletin 2026-13 / Fed SR 26-2)

### Pattern 5 — External Engagement

- **1.19** Control 1.19: eDiscovery for Agent Interactions
- **2.11** Control 2.11: Bias Testing and Fairness Assessment
- **2.12** Control 2.12: Supervision and Oversight (FINRA Rule 3110)
- **2.19** Control 2.19: Customer AI Disclosure and Transparency
- **2.26** Control 2.26: Entra Agent ID — Identity Governance for Agents
- **4.4** Control 4.4: Guest and External User Access Controls

### Pattern 6 — AI-First Capabilities

- **2.17** Control 2.17: Multi-Agent Orchestration Limits
- **2.20** Control 2.20: Adversarial Testing and Red Team Framework
- **3.14** Control 3.14: Agent 365 Observability SDK and Custom Agent Telemetry
- **3.9** Control 3.9: Microsoft Sentinel Integration

## Solutions per pattern

The following companion solutions in [FSI-AgentGov-Solutions](https://github.com/judeper/FSI-AgentGov-Solutions) declare support for each pattern (via `applicable_patterns` frontmatter in each solution README).

### Pattern 1 — Employee AI Enablement

- [`agent-access-monitor`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/agent-access-monitor)
- [`agent-cost-reporting`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/agent-cost-reporting)
- [`agent-registry-automation`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/agent-registry-automation)
- [`agent-sharing-access-restriction-detector`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/agent-sharing-access-restriction-detector)
- [`content-moderation-monitor`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/content-moderation-monitor)
- [`copilot-agent-inventory`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/copilot-agent-inventory)
- [`copilot-studio-analytics`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/copilot-studio-analytics)
- [`cross-tenant-external-sharing-governance`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/cross-tenant-external-sharing-governance)
- [`environment-lifecycle-management`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/environment-lifecycle-management)
- [`file-upload-security`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/file-upload-security)
- [`generative-ai-config-auditor`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/generative-ai-config-auditor)
- [`inactivity-timeout-enforcement`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/inactivity-timeout-enforcement)
- [`mime-type-restrictions`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/mime-type-restrictions)
- [`pipeline-governance-cleanup`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/pipeline-governance-cleanup)
- [`session-security-configurator`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/session-security-configurator)
- [`unrestricted-agent-sharing-detector`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/unrestricted-agent-sharing-detector)

### Pattern 2 — Business Expert Empowerment

- [`agent-knowledge-source-scanner`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/agent-knowledge-source-scanner)
- [`agent-registry-automation`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/agent-registry-automation)
- [`agent-sharing-access-restriction-detector`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/agent-sharing-access-restriction-detector)
- [`copilot-agent-inventory`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/copilot-agent-inventory)
- [`environment-lifecycle-management`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/environment-lifecycle-management)
- [`generative-ai-config-auditor`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/generative-ai-config-auditor)
- [`hallucination-tracker`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/hallucination-tracker)
- [`mime-type-restrictions`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/mime-type-restrictions)
- [`rag-source-validator`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/rag-source-validator)
- [`scope-drift-monitor`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/scope-drift-monitor)

### Pattern 3 — Workplace & IT Services

- [`credential-oversharing-detector`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/credential-oversharing-detector)
- [`file-upload-security`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/file-upload-security)
- [`inactivity-timeout-enforcement`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/inactivity-timeout-enforcement)
- [`mime-type-restrictions`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/mime-type-restrictions)
- [`segregation-detector`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/segregation-detector)

### Pattern 4 — Core Business Process Transformation

- [`action-confirmation-auditor`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/action-confirmation-auditor)
- [`agent-365-lifecycle-governance`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/agent-365-lifecycle-governance)
- [`agent-access-monitor`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/agent-access-monitor)
- [`agent-cost-reporting`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/agent-cost-reporting)
- [`agent-observability-foundation`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/agent-observability-foundation)
- [`agent-registry-automation`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/agent-registry-automation)
- [`audit-compliance-manager`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/audit-compliance-manager)
- [`coi-testing`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/coi-testing)
- [`compliance-dashboard`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/compliance-dashboard)
- [`conditional-access-automation`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/conditional-access-automation)
- [`copilot-agent-inventory`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/copilot-agent-inventory)
- [`copilot-billing-governance`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/copilot-billing-governance)
- [`copilot-studio-analytics`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/copilot-studio-analytics)
- [`credential-oversharing-detector`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/credential-oversharing-detector)
- [`cross-solution-integration`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/cross-solution-integration)
- [`deny-event-correlation-report`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/deny-event-correlation-report)
- [`dr-testing-framework`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/dr-testing-framework)
- [`early-release-validation`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/early-release-validation)
- [`environment-lifecycle-management`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/environment-lifecycle-management)
- [`finra-supervision-workflow`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/finra-supervision-workflow)
- [`generative-ai-config-auditor`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/generative-ai-config-auditor)
- [`hallucination-tracker`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/hallucination-tracker)
- [`hitl-workflow-governance`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/hitl-workflow-governance)
- [`message-center-monitor`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/message-center-monitor)
- [`model-risk-management-automation`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/model-risk-management-automation)
- [`pipeline-governance-cleanup`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/pipeline-governance-cleanup)
- [`scope-drift-monitor`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/scope-drift-monitor)
- [`segregation-detector`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/segregation-detector)
- [`session-security-configurator`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/session-security-configurator)

### Pattern 5 — External Engagement

- [`action-confirmation-auditor`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/action-confirmation-auditor)
- [`agent-365-lifecycle-governance`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/agent-365-lifecycle-governance)
- [`agent-observability-foundation`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/agent-observability-foundation)
- [`audit-compliance-manager`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/audit-compliance-manager)
- [`coi-testing`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/coi-testing)
- [`compliance-dashboard`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/compliance-dashboard)
- [`conditional-access-automation`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/conditional-access-automation)
- [`content-moderation-monitor`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/content-moderation-monitor)
- [`copilot-billing-governance`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/copilot-billing-governance)
- [`cross-solution-integration`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/cross-solution-integration)
- [`cross-tenant-external-sharing-governance`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/cross-tenant-external-sharing-governance)
- [`deny-event-correlation-report`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/deny-event-correlation-report)
- [`dr-testing-framework`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/dr-testing-framework)
- [`early-release-validation`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/early-release-validation)
- [`finra-supervision-workflow`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/finra-supervision-workflow)
- [`hallucination-tracker`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/hallucination-tracker)
- [`hitl-workflow-governance`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/hitl-workflow-governance)
- [`message-center-monitor`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/message-center-monitor)
- [`model-risk-management-automation`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/model-risk-management-automation)
- [`session-security-configurator`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/session-security-configurator)
- [`unrestricted-agent-sharing-detector`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/unrestricted-agent-sharing-detector)

### Pattern 6 — AI-First Capabilities

- [`action-confirmation-auditor`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/action-confirmation-auditor)
- [`agent-365-lifecycle-governance`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/agent-365-lifecycle-governance)
- [`agent-communication-restriction-detector`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/agent-communication-restriction-detector)
- [`agent-observability-foundation`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/agent-observability-foundation)
- [`audit-compliance-manager`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/audit-compliance-manager)
- [`compliance-dashboard`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/compliance-dashboard)
- [`conditional-access-automation`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/conditional-access-automation)
- [`cross-solution-integration`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/cross-solution-integration)
- [`deny-event-correlation-report`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/deny-event-correlation-report)
- [`hitl-workflow-governance`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/hitl-workflow-governance)
- [`message-center-monitor`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/message-center-monitor)
- [`model-risk-management-automation`](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/model-risk-management-automation)

## Per-pillar control × pattern matrix

### Pillar 1 — Security (29 controls)

| Control | Title | P1 | P2 | P3 | P4 | P5 | P6 | Critical For |
|---------|-------|---- | ---- | ---- | ---- | ---- | ----|--------------|
| 1.1 | Control 1.1: Restrict Agent Publishing by Authorization | 🎯 | ✅ | ✅ | ✅ | ✅ | ✅ | P1 |
| 1.10 | Control 1.10: Communication Compliance Monitoring | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| 1.11 | Control 1.11: Conditional Access and Phishing-Resistant MFA | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| 1.12 | Control 1.12: Insider Risk Detection and Response | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| 1.13 | Control 1.13: Sensitive Information Types (SITs) and Pattern Recognition | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| 1.14 | Control 1.14: Data Minimization and Agent Scope Control | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| 1.15 | Control 1.15: Encryption: Data in Transit and at Rest | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| 1.16 | Control 1.16: Information Rights Management (IRM) for Documents | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| 1.17 | Control 1.17: Endpoint Data Loss Prevention (Endpoint DLP) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| 1.18 | Control 1.18: Application-Level Authorization and Role-Based Access Control (RBAC) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| 1.19 | Control 1.19: eDiscovery for Agent Interactions | ✅ | ✅ | ✅ | ✅ | 🎯 | ✅ | P5 |
| 1.2 | Control 1.2: Agent Registry and Integrated Apps Management | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| 1.20 | Control 1.20: Network Isolation and Private Connectivity | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| 1.21 | Control 1.21: Adversarial Input Logging | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| 1.22 | Control 1.22: Information Barriers for AI Agents | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| 1.23 | Control 1.23: Step-Up Authentication for AI Agent Operations | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| 1.24 | Control 1.24: Defender AI Security Posture Management (AI-SPM) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| 1.25 | Control 1.25: MIME Type Restrictions for File Uploads | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| 1.26 | Control 1.26: Agent File Upload and File Analysis Restrictions | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| 1.27 | Control 1.27: AI Agent Content Moderation Enforcement | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| 1.28 | Control 1.28: Policy-Based Agent Publishing Restrictions | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| 1.29 | Control 1.29: Global Secure Access: Network Controls for Copilot Studio Agents | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| 1.3 | Control 1.3: SharePoint Content Governance and Permissions | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| 1.4 | Control 1.4: Advanced Connector Policies (ACP) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| 1.5 | Control 1.5: Data Loss Prevention (DLP) and Sensitivity Labels | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| 1.6 | Control 1.6: Microsoft Purview DSPM for AI | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| 1.7 | Control 1.7: Comprehensive Audit Logging and Compliance | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| 1.8 | Control 1.8: Runtime Protection and External Threat Detection | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| 1.9 | Control 1.9: Data Retention and Deletion Policies | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |

### Pillar 2 — Management (27 controls)

| Control | Title | P1 | P2 | P3 | P4 | P5 | P6 | Critical For |
|---------|-------|---- | ---- | ---- | ---- | ---- | ----|--------------|
| 2.1 | Control 2.1: Managed Environments | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| 2.10 | Control 2.10: Patch Management and System Updates | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| 2.11 | Control 2.11: Bias Testing and Fairness Assessment | ✅ | ✅ | ✅ | 🎯 | 🎯 | ✅ | P4, P5 |
| 2.12 | Control 2.12: Supervision and Oversight (FINRA Rule 3110) | ✅ | ✅ | ✅ | 🎯 | 🎯 | ✅ | P4, P5 |
| 2.13 | Control 2.13: Documentation and Record Keeping | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| 2.14 | Control 2.14: Training and Awareness Program | 🎯 | ✅ | ✅ | ✅ | ✅ | ✅ | P1 |
| 2.15 | Control 2.15: Environment Routing and Auto-Provisioning | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| 2.16 | Control 2.16: RAG Source Integrity Validation | ✅ | 🎯 | ✅ | ✅ | ✅ | ✅ | P2 |
| 2.17 | Control 2.17: Multi-Agent Orchestration Limits | ✅ | ✅ | ✅ | ✅ | ✅ | 🎯 | P6 |
| 2.18 | Control 2.18: Automated Conflict of Interest Testing | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| 2.19 | Control 2.19: Customer AI Disclosure and Transparency | ✅ | ✅ | ✅ | ✅ | 🎯 | ✅ | P5 |
| 2.2 | Control 2.2: Environment Groups and Tier Classification | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| 2.20 | Control 2.20: Adversarial Testing and Red Team Framework | ✅ | ✅ | ✅ | ✅ | ✅ | 🎯 | P6 |
| 2.21 | Control 2.21: AI Marketing Claims and Substantiation | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| 2.22 | Control 2.22: Inactivity Timeout Enforcement | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| 2.23 | Control 2.23: User Consent and AI Disclosure Enforcement | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| 2.24 | Control 2.24: Agent Feature Enablement and Restriction Governance | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| 2.25 | Control 2.25: Microsoft Agent 365 — Admin Center Governance Console | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| 2.26 | Control 2.26: Entra Agent ID — Identity Governance for Agents | ✅ | ✅ | ✅ | ✅ | 🎯 | ✅ | P5 |
| 2.27 | Control 2.27: Consumption-Entitlement Governance | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| 2.3 | Control 2.3: Change Management and Release Planning | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| 2.4 | Control 2.4: Business Continuity and Disaster Recovery | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| 2.5 | Control 2.5: Testing, Validation, and Quality Assurance | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| 2.6 | Control 2.6: Model Risk Management (OCC Bulletin 2026-13 / Fed SR 26-2) | ✅ | ✅ | ✅ | 🎯 | ✅ | ✅ | P4 |
| 2.7 | Control 2.7: Vendor and Third-Party Risk Management | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| 2.8 | Control 2.8: Access Control and Segregation of Duties | ✅ | ✅ | 🎯 | ✅ | ✅ | ✅ | P3 |
| 2.9 | Control 2.9: Agent Performance Monitoring and Optimization | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |

### Pillar 3 — Reporting (14 controls)

| Control | Title | P1 | P2 | P3 | P4 | P5 | P6 | Critical For |
|---------|-------|---- | ---- | ---- | ---- | ---- | ----|--------------|
| 3.1 | Control 3.1: Agent Inventory and Metadata Management | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| 3.10 | Control 3.10: Hallucination Feedback Loop | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| 3.11 | Control 3.11: Centralized Agent Inventory Enforcement | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| 3.12 | Control 3.12: Agent Governance Exception and Override Management | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| 3.13 | Control 3.13: Agent 365 Admin Center Analytics and Reporting | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| 3.14 | Control 3.14: Agent 365 Observability SDK and Custom Agent Telemetry | ✅ | ✅ | ✅ | ✅ | ✅ | 🎯 | P6 |
| 3.2 | Control 3.2: Usage Analytics and Activity Monitoring | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| 3.3 | Control 3.3: Compliance and Regulatory Reporting | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| 3.4 | Control 3.4: Incident Reporting and Root Cause Analysis | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| 3.5 | Control 3.5: Cost Allocation and Budget Tracking | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| 3.6 | Control 3.6: Orphaned Agent Detection and Remediation | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| 3.7 | Control 3.7: PPAC Security Posture Assessment | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| 3.8 | Control 3.8: Copilot Hub and Governance Dashboard | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| 3.9 | Control 3.9: Microsoft Sentinel Integration | ✅ | ✅ | ✅ | ✅ | ✅ | 🎯 | P6 |

### Pillar 4 — SharePoint (9 controls)

| Control | Title | P1 | P2 | P3 | P4 | P5 | P6 | Critical For |
|---------|-------|---- | ---- | ---- | ---- | ---- | ----|--------------|
| 4.1 | Control 4.1: SharePoint Information Access Governance (IAG) / Restricted Content Discovery | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| 4.2 | Control 4.2: Site Access Reviews and Certification | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| 4.3 | Control 4.3: Site and Document Retention Management | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| 4.4 | Control 4.4: Guest and External User Access Controls | ✅ | ✅ | ✅ | ✅ | 🎯 | ✅ | P5 |
| 4.5 | Control 4.5: SharePoint Security and Compliance Monitoring | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| 4.6 | Control 4.6: Grounding Scope Governance | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| 4.7 | Control 4.7: Microsoft 365 Copilot Data Governance | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| 4.8 | Control 4.8: Item-Level Permission Scanning for Agent Knowledge Sources | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| 4.9 | Control 4.9: Embedded File Content Governance | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |

<!-- This page is generated by scripts/generate_pattern_coverage.py. Do not edit by hand. -->
