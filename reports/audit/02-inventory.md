# Inventory of Reviewable Units

## Summary

| Category | Count | Repo |
|----------|-------|------|
| Controls (Pillar 1 — Security) | 28 | FSI-AgentGov |
| Controls (Pillar 2 — Management) | 24 | FSI-AgentGov |
| Controls (Pillar 3 — Reporting) | 12 | FSI-AgentGov |
| Controls (Pillar 4 — SharePoint) | 7 | FSI-AgentGov |
| Playbooks (per-control, 4 each) | 284 | FSI-AgentGov |
| Framework docs | 11 | FSI-AgentGov |
| Reference docs | 21 | FSI-AgentGov |
| Getting Started docs | 2 | FSI-AgentGov |
| Downloads (Excel templates) | 6 | FSI-AgentGov |
| Advanced playbooks | 15 | FSI-AgentGov |
| Solution packages | 25 | FSI-AgentGov-Solutions |
| Scripts (docs repo) | ~40 | FSI-AgentGov |
| **Total reviewable units** | **~475** | |

## Controls Inventory (71)

### Pillar 1 — Security (28 controls)
| ID | Title | Technologies |
|----|-------|-------------|
| 1.1 | Copilot Studio DLP Governance | Power Platform DLP, Copilot Studio |
| 1.2 | Agent Store and Catalog Security | M365 Admin, Copilot Studio |
| 1.3 | Authentication and Identity for Agents | Entra ID, Conditional Access |
| 1.4 | Data Classification and Sensitivity Labeling | Purview, Sensitivity Labels |
| 1.5 | DLP and Sensitivity Labels | Purview DLP, Power Platform |
| 1.6 | Encryption at Rest and in Transit | Purview CMK, TLS |
| 1.7 | API Security and Connector Governance | Custom Connectors, API Management |
| 1.8 | Runtime Protection and External Threat Detection | Defender, Power Platform |
| 1.9 | Secure Development Lifecycle for Agents | DevOps, ALM |
| 1.10 | Privilege Access Management | Entra PIM |
| 1.11 | Conditional Access and Phishing-Resistant MFA | Entra CA, FIDO2 |
| 1.12 | Network Isolation and Private Endpoints | Azure Networking, Private Link |
| 1.13 | Secrets and Credential Management | Key Vault, Managed Identity |
| 1.14 | Audit Logging and Compliance | Purview Audit, UAL |
| 1.15 | Customer Key and Double Key Encryption | Purview Customer Key |
| 1.16 | Information Barriers | Purview IB |
| 1.17 | Global Secure Access | Entra GSA, Internet Access |
| 1.18 | Communication Compliance | Purview CC |
| 1.19 | eDiscovery for Agent Interactions | Purview eDiscovery |
| 1.20 | Session Security and Timeout | Power Platform Session |
| 1.21 | Agent File Upload Security | Copilot Studio, DLP |
| 1.22 | Content Moderation and Responsible AI | Azure AI Content Safety |
| 1.23 | Agent Configuration Hardening | Power Platform, Copilot Studio |
| 1.24 | Disaster Recovery and Business Continuity | Azure BC/DR |
| 1.25 | MIME Type Security Restrictions | Copilot Studio, DLP |
| 1.26 | Agent Sharing and Access Restriction | Copilot Studio Sharing |
| 1.27 | RAG Source Validation and Drift Detection | Knowledge Sources |
| 1.28 | Unrestricted Agent Sharing Detection | Copilot Studio |

### Pillar 2 — Management (24 controls)
| ID | Title |
|----|-------|
| 2.1–2.24 | Environment Lifecycle, Naming, DLP Tiering, Connector Management, ALM/DevOps, Capacity Planning, Maker Welcome, License Management, Monitoring Strategy, Environment Groups, Change Management, Agent Identity & Lifecycle, Power Platform Governance, Request & Approval, Operational Monitoring, Agent Testing & QA, Update Management, Model Risk Management, Agent Retirement, AI-Specific Risk Assessment, Platform Change Governance, Agent Builder Governance, Copilot Actions and Connectors, Copilot Studio Agents |

### Pillar 3 — Reporting (12 controls)
| ID | Title |
|----|-------|
| 3.1–3.12 | Compliance Evidence, Usage Analytics, Cost Tracking, Incident Reporting, Regulatory Reporting, Agent Inventory, Executive Dashboards, Copilot Hub Dashboard, Sentinel Integration, Agent Attestation, Centralized Inventory Enforcement, Exception & Override Management |

### Pillar 4 — SharePoint (7 controls)
| ID | Title |
|----|-------|
| 4.1–4.7 | SharePoint Advanced Management, Site Access Reviews, Document Retention, Guest Access, Content Lifecycle, Knowledge Source Security, M365 Copilot Data Governance |

## Solutions Inventory (25)

| # | Solution | Version | Primary Technologies |
|---|---------|---------|---------------------|
| 1 | agent-access-monitor | 1.2.41 | PowerShell, Graph API |
| 2 | agent-observability-foundation | 1.2.41 | KQL, Log Analytics |
| 3 | agent-sharing-access-restriction-detector | 1.2.41 | PowerShell, Copilot Studio API |
| 4 | audit-configuration-validator | 1.2.41 | Python, Dataverse |
| 5 | audit-logging-compliance-automation | 1.2.41 | PowerShell, Exchange, Dataverse |
| 6 | coi-testing | 1.2.41 | Python, Azure AI |
| 7 | compliance-dashboard | 1.2.41 | Python, Dataverse, Power BI |
| 8 | conditional-access-automation | 1.2.41 | PowerShell, Graph API, Entra CA |
| 9 | content-moderation-monitor | 1.2.41 | PowerShell, Azure AI Content Safety |
| 10 | cross-solution-integration | 1.2.41 | PowerShell, Multi-solution |
| 11 | deny-event-correlation-report | 1.2.41 | PowerShell, KQL, Graph |
| 12 | dr-testing-framework | 1.2.41 | PowerShell, Azure BC/DR |
| 13 | environment-lifecycle-management | 1.2.41 | Python, Dataverse, Power Platform |
| 14 | file-upload-security | 1.2.41 | PowerShell, DLP, Copilot Studio |
| 15 | finra-supervision-workflow | 1.2.41 | Power Automate, Dataverse |
| 16 | hallucination-tracker | 1.2.41 | Python, Dataverse, Azure AI |
| 17 | inactivity-timeout-enforcement | 1.2.41 | PowerShell, Power Platform |
| 18 | message-center-monitor | 1.2.41 | Power Automate, Graph API |
| 19 | mime-type-restrictions | 1.2.41 | C#, DLP, Copilot Studio |
| 20 | pipeline-governance-cleanup | 1.2.41 | PowerShell, Power Platform |
| 21 | rag-source-validator | 1.2.41 | PowerShell, Knowledge Sources |
| 22 | scope-drift-monitor | 1.2.41 | PowerShell, Copilot Studio |
| 23 | segregation-detector | 1.2.41 | PowerShell, Entra ID, PIM |
| 24 | session-security-configurator | 1.2.41 | Python, PowerShell, Dataverse |
| 25 | unrestricted-agent-sharing-detector | 1.2.41 | PowerShell, Copilot Studio |

## Framework & Reference Docs

| Category | Count | Key Files |
|----------|-------|-----------|
| Framework | 11 | executive-summary.md, governance-fundamentals.md, zones-and-tiers.md, regulatory-framework.md, operating-model.md, adoption-roadmap.md, agent-lifecycle.md, governance-cadence.md, agent-365-architecture.md, agent-identity.md, solutions-integration.md |
| Reference | 21 | role-catalog.md, glossary.md, license-requirements.md, solutions-index.md, solutions-architecture-guide.md, regulatory-mappings.md, portal-paths-quick-reference.md, monitoring-architecture.md, evidence-standards.md, RACI matrix, NIST crosswalk, FAQ, config guide, SAM licensing, agent capabilities, audit events, agent essentials, Learn monitor reports |
| Getting Started | 2 | overview.md, quick-start.md |
| Downloads | 6 | Excel checklists (pillar-specific + comprehensive) |
