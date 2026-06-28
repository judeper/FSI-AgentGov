---
search:
  boost: 2
---
# Playbooks Overview

Operational procedures and implementation guides for AI agent governance.

---

## Purpose

The Playbooks layer provides step-by-step implementation guidance for platform teams and operations. Content here is updated continuously as Microsoft portals and capabilities change.

**Target Audience:**

- Power Platform Admins
- SharePoint Admins
- Compliance Analysts
- Security Operations
- Implementation Teams

---

## When to Use Playbooks

Use playbooks when you need:

- **Portal walkthroughs** — Step-by-step configuration in admin centers
- **PowerShell scripts** — Automation for governance tasks
- **Operational templates** — Forms and schemas for governance processes
- **Troubleshooting guidance** — Common issues and resolutions

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

For the full control-by-control matrix, see [Control Implementations](control-implementations/index.md).

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

Complex governance scenarios and specialized configurations.

| Playbook | Purpose |
|----------|---------|
| [Human-in-the-Loop Triggers](advanced-implementations/human-in-the-loop-triggers.md) | HITL pattern implementation |
| [Confidence and Routing](advanced-implementations/confidence-and-routing.md) | Confidence-based workflows |
| [Zone 1 Minimum Explainability](advanced-implementations/zone1-min-explainability.md) | Transparency requirements |
| [DSPM for AI Policy Pack](advanced-implementations/dspm-for-ai-policy-pack.md) | Data security policies |
| [Platform Change Governance](advanced-implementations/platform-change-governance/index.md) | Message Center change operationalization |

!!! info "Deployable Solutions"
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

### Control Implementations

Per-control implementation guides extracted from control documentation.

**316 per-control playbooks** (79 controls × 4 playbooks each) provide step-by-step implementation guidance for every control in the framework.

Each control has a dedicated folder with:

- `portal-walkthrough.md` — Step-by-step portal configuration
- `powershell-setup.md` — Automation scripts
- `verification-testing.md` — How to verify the control works
- `troubleshooting.md` — Common issues and solutions

!!! success "Available Now"
    All 316 per-control implementation playbooks are available in the [Control Implementations Index](control-implementations/index.md). Navigate to any control in the Control Catalog to find direct links to its 4 playbooks in the "Implementation Guides" section.

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
