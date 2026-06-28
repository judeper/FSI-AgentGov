---
search:
  boost: 2
---
# Playbooks

**You need to configure a specific control, verify it is working, or respond to an examiner request.** This layer contains 316 per-control implementation playbooks (79 controls × 4 types), plus governance operations, compliance procedures, and ready-to-deploy advanced solutions. Content is updated continuously as Microsoft portals and capabilities change.

The fastest route to any control's implementation steps is the **Control Explorer** — find your control, then jump directly to its portal walkthrough, PowerShell setup, verification, or troubleshooting guide.

[Open Control Explorer →](../controls/explorer.md){ .md-button .md-button--primary }

**Who uses this:** Power Platform Admins · SharePoint Admins · Compliance Analysts · Security Operations · Implementation Teams

---

## Quick Start: Common Admin Tasks

Jump directly to the right playbook for your immediate goal.

| I need to… | Start here | Playbook type |
|---|---|---|
| **Block an unapproved agent** in M365 or restrict publishing | [1.1 Portal Walkthrough](control-implementations/1.1/portal-walkthrough.md) | Portal |
| **Restrict who can create or publish agents** tenant-wide | [1.1 PowerShell Setup](control-implementations/1.1/powershell-setup.md) | PowerShell |
| **Enable Managed Environments** governance controls | [2.1 Portal Walkthrough](control-implementations/2.1/portal-walkthrough.md) | Portal |
| **Set DLP policies** for agent data access | [1.5 Portal Walkthrough](control-implementations/1.5/portal-walkthrough.md) | Portal |
| **Set up audit logging** and retention for agent conversations | [1.7 Portal Walkthrough](control-implementations/1.7/portal-walkthrough.md) | Portal |
| **Build the agent inventory** (register existing agents) | [3.1 Portal Walkthrough](control-implementations/3.1/portal-walkthrough.md) | Portal |
| **Automate agent inventory** discovery across all planes | [3.1 PowerShell Setup](control-implementations/3.1/powershell-setup.md) | PowerShell |
| **Prepare for a FINRA, SEC, or OCC exam** | [Audit Readiness Checklist](compliance-and-audit/audit-readiness-checklist.md) | Compliance |
| **Assemble examination evidence** from portal exports | [Evidence Pack Assembly](compliance-and-audit/evidence-pack-assembly.md) | Compliance |
| **Respond to an AI governance incident** | [AI Incident Response Playbook](incident-and-risk/ai-incident-response-playbook.md) | Incident |
| **Decommission an agent** securely | [Agent Decommissioning](agent-lifecycle/agent-decommissioning.md) | Lifecycle |
| **Promote an agent to a higher-governance zone** | [Agent Promotion Checklist](agent-lifecycle/agent-promotion-checklist.md) | Lifecycle |
| **Monitor for unauthorized agent sharing** continuously | [Unrestricted Agent Sharing Detector](advanced-implementations/unrestricted-agent-sharing-detector/index.md) | Advanced |
| **Configure human-in-the-loop approvals** for agent actions | [Human-in-the-Loop Triggers](advanced-implementations/human-in-the-loop-triggers.md) | Advanced |

---

## Control Implementations

**The core of this layer — 316 per-control playbooks.** Every control has four standard playbooks:

| Playbook type | What it covers |
|---|---|
| **Portal Walkthrough** | Step-by-step admin-center configuration |
| **PowerShell Setup** | Automation scripts and module setup |
| **Verification & Testing** | How to verify the control is working |
| **Troubleshooting** | Common issues and resolutions |

[Browse all control implementations →](control-implementations/index.md){ .md-button }

> **Tip:** Navigate to any control in the [Control Catalog](../controls/index.md), then click "Implementation Guides" to jump directly to its four playbooks.

---

## Playbook Categories

### Getting Started

Phase-based implementation guides for new deployments.

| Playbook | Purpose |
|----------|---------|
| [Phase 0: Governance Setup](getting-started/phase-0-governance-setup.md) | Initial governance structure and core controls |
| [Phase 1: Minimal Viable Controls](getting-started/phase-1-minimal-viable-controls.md) | Production readiness controls |
| [Phase 2: Hardening](getting-started/phase-2-hardening.md) | Advanced security and monitoring |

---

### Governance Operations

Day-to-day governance procedures and templates.

| Playbook | Purpose |
|----------|---------|
| [Governance Operating Calendar](governance-operations/governance-operating-calendar.md) | Scheduled governance activities |
| [RACI Governance Template](governance-operations/raci-governance-template.md) | Role assignment template |
| [Action Authorization Matrix](governance-operations/action-authorization-matrix.md) | Approval requirements by action type |
| [Escalation Matrix](governance-operations/escalation-matrix.md) | Escalation procedures and contacts |
| [Decision Log Schema](governance-operations/decision-log-schema.md) | Governance decision documentation |

---

### Compliance and Audit

Examination preparation and evidence management.

| Playbook | Purpose |
|----------|---------|
| [Evidence Pack Assembly](compliance-and-audit/evidence-pack-assembly.md) | Compile examination evidence |
| [Audit Readiness Checklist](compliance-and-audit/audit-readiness-checklist.md) | Pre-examination preparation |
| [Examination Response Guide](compliance-and-audit/examination-response-guide.md) | Responding to examiner requests |

---

### Incident and Risk

Incident response and risk assessment procedures.

| Playbook | Purpose |
|----------|---------|
| [AI Incident Response Playbook](incident-and-risk/ai-incident-response-playbook.md) | Incident detection and response |
| [AI Risk Assessment Template](incident-and-risk/ai-risk-assessment-template.md) | Agent risk evaluation |
| [Remediation Tracking](incident-and-risk/remediation-tracking.md) | Issue remediation workflow |

---

### Agent Lifecycle

Agent creation, deployment, and retirement procedures.

| Playbook | Purpose |
|----------|---------|
| [Agent Inventory Entry](agent-lifecycle/agent-inventory-entry.md) | Register new agents |
| [Per-Agent Data Policy](agent-lifecycle/per-agent-data-policy.md) | Agent-specific data handling |
| [Agent Promotion Checklist](agent-lifecycle/agent-promotion-checklist.md) | Zone promotion requirements |
| [Agent Decommissioning](agent-lifecycle/agent-decommissioning.md) | Secure agent retirement |

---

### Monitoring and Validation

Ongoing compliance monitoring and health checks.

| Playbook | Purpose |
|----------|---------|
| [Real-time Compliance Dashboard](monitoring-and-validation/real-time-compliance-dashboard.md) | Dashboard configuration |
| [Scope Creep Detection](monitoring-and-validation/scope-creep-detection.md) | Monitor for unauthorized expansion |
| [Health Check Procedures](monitoring-and-validation/health-check-procedures.md) | Regular validation checks |
| [Purview Audit Query Pack](monitoring-and-validation/purview-audit-query-pack.md) | Pre-built audit queries |
| [Semantic Index Governance Queries](monitoring-and-validation/semantic-index-governance-queries.md) | Knowledge index monitoring |

---

### Advanced Implementations

Complex governance scenarios, specialized patterns, and ready-to-deploy solutions.

#### Deployable Solutions

Multi-file implementation packages with architecture guides, deployment steps, and audit evidence procedures.

| Solution | Related Controls | Value |
|---|---|---|
| [Agent 365 Observability](advanced-implementations/agent-365-observability/index.md) | 3.2, 3.7, 3.9 | Zone-based retention, SIEM/Sentinel export, and regulatory telemetry mapping |
| [Agent Blueprint Promotion Gates](advanced-implementations/agent-blueprint-promotion-gates/index.md) | 2.3, 2.8 | Approval-gate model for blueprint lifecycle promotion with FINRA/SOX audit trail |
| [Agent Usage & Performance Workbook](advanced-implementations/agent-usage-workbook/index.md) | 3.1, 3.2, 3.7, 3.8 | Azure Monitor Workbook for unified agent activity and governance signal visibility |
| [Conditional Access Automation](advanced-implementations/conditional-access-automation/index.md) | 1.11, 1.23 | Automated CA policy compliance validation with drift detection and Dataverse audit trail |
| [Configuration Hardening Baseline](advanced-implementations/configuration-hardening-baseline/index.md) | 1.1, 1.7, 2.1, 2.22 | 32-item cross-portal security checklist for authentication, audit, RBAC, and content moderation |
| [Deny Event Correlation Report](advanced-implementations/deny-event-correlation-report/index.md) | 1.5, 1.7, 3.4 | Correlates deny events across DLP, Purview, and App Insights with SHA-256 evidence export |
| [Environment Lifecycle Management](advanced-implementations/environment-lifecycle-management/index.md) | 2.1, 2.2, 2.3 | Automated, governed Power Platform environment provisioning with zone classification |
| [MCP Server Governance](advanced-implementations/mcp-server-governance/index.md) | 1.4, 1.5, 2.17 | FSI governance guidance for Model Context Protocol server integrations |
| [Platform Change Governance](advanced-implementations/platform-change-governance/index.md) | 2.3, 2.15 | Dataverse-backed Message Center change management and operationalization |
| [SharePoint Copilot Pre-Flight](advanced-implementations/sharepoint-copilot-preflight/index.md) | 4.1, 4.2, 4.7 | Pre-deployment permission audit checklist before assigning Copilot licenses |
| [Unrestricted Agent Sharing Detector](advanced-implementations/unrestricted-agent-sharing-detector/index.md) | 1.1, 1.2, 2.1 | Continuous detection and alerting for unauthorized agent sharing |

#### Pattern Guides

Single-file guides for specific governance patterns and specialized configurations.

| Guide | Purpose |
|---|---|
| [Human-in-the-Loop Triggers](advanced-implementations/human-in-the-loop-triggers.md) | HITL pattern implementation |
| [Confidence and Routing](advanced-implementations/confidence-and-routing.md) | Confidence-based workflows |
| [Zone 1 Minimum Explainability](advanced-implementations/zone1-min-explainability.md) | Transparency requirements |
| [DSPM for AI Policy Pack](advanced-implementations/dspm-for-ai-policy-pack.md) | Data security policies |
| [Microsoft Audit Reporting Tools](advanced-implementations/microsoft-audit-reporting-tools.md) | Built-in audit reporting configuration and retention |

!!! info "Deployable Solutions Repo"
    Ready-to-deploy Power Platform solutions are available in [FSI-AgentGov-Solutions](https://github.com/judeper/FSI-AgentGov-Solutions). See the [Solutions Index](../reference/solutions-index.md) for the complete catalog with control mappings.

---

### Regulatory Modules

Regulation-specific implementation guidance.

| Playbook | Purpose |
|----------|---------|
| [Colorado AI Act Readiness](regulatory-modules/colorado-ai-act-readiness.md) | Colorado AI Act compliance |
| [Colorado AI Impact Assessment](regulatory-modules/colorado-ai-impact-assessment.md) | Impact assessment template |
| [Supply Chain Risk Register](regulatory-modules/supply-chain-risk-register-entry.md) | Third-party risk tracking |

---

## Playbook Maintenance

### Update Frequency

- **Portal walkthroughs:** Updated within 2 weeks of Microsoft UI changes
- **Scripts:** Updated as needed for API changes
- **Templates:** Updated quarterly or as governance requirements change

### Version Tracking

Each playbook includes:

- **Last Updated:** Date of last content revision
- **Tested On:** Portal/API version tested against
- **Last UI Verified:** Date of last screenshot verification

### Reporting Issues

If you find outdated content or broken procedures:

1. Check the playbook's "Last Updated" date
2. Verify against current portal/API
3. Report issues via GitHub Issues

---

## Related Sections

- [Framework](../framework/index.md) — Governance principles and structure
- [Control Catalog](../controls/index.md) — Control requirements and objectives
- [Reference](../reference/index.md) — Supporting materials and quick references

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
