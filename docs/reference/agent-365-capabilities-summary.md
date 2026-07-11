---
description: "This reference consolidates all Microsoft Agent 365 capabilities documented across the FSI-AgentGov framework."
---
# Agent 365 Capabilities Summary

**Last Updated:** May 2026
**Version:** v1.6.2

---

## Overview

This reference consolidates all Microsoft Agent 365 capabilities documented across the FSI-AgentGov framework. Use this page to quickly locate Agent 365-specific guidance and demonstrate comprehensive coverage to stakeholders and auditors.

!!! note "GA Status Update"
    Microsoft Agent 365 reaches general availability on May 1, 2026, as part of Microsoft 365 E7 and standalone Agent 365 per-user licensing. Agent Essentials SDK capabilities are expected to mature alongside the broader Agent 365 platform. Feature availability and documentation may change at or after GA.

---

## What is Agent 365?

Agent 365 is Microsoft's governance control plane for AI agents, announced at Ignite 2025. It treats AI agents as first-class identities with dedicated governance capabilities distinct from traditional Microsoft 365 user governance.

### Key Components

| Component | Description | FSI Framework Coverage |
|-----------|-------------|----------------------|
| **Entra Agent ID** | First-class identity for AI agents in Entra ID | [Agent Identity Architecture](../framework/agent-identity-architecture.md) |
| **Agent Blueprints** | Governance templates for enterprise agent deployment | [Control 1.11](../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md) |
| **Agent Store** | Curated catalog of approved agents | [Control 1.2](../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md) |
| **Agent Registry** | Centralized inventory including shadow agent detection | [Control 3.1](../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md), [Control 3.6](../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) |
| **Observability SDK** | OpenTelemetry-based telemetry for agent monitoring | [Agent 365 Observability Playbook](../playbooks/advanced-implementations/agent-365-observability/index.md) |
| **MCP Server Support** | Cross-platform agent interoperability | [Control 2.17](../controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md) |
| **Windows 365 for Agents** | Cloud PC execution layer for Agent 365 computer-using agents (public preview) | [Windows 365 for Agents Reference](windows-365-for-agents.md) |

---

## Framework Coverage Matrix

### Identity & Access Management

| Agent 365 Capability | FSI Control | Coverage Status |
|---------------------|-------------|-----------------|
| Agentic Users (first-class identity) | [1.11](../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md), [Agent Identity Architecture](../framework/agent-identity-architecture.md) | **Comprehensive** |
| Conditional Access for Agent ID | [1.11](../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md) | **Comprehensive** |
| Agent Sponsorship | [1.11](../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md), [Sponsorship Workflows](../playbooks/control-implementations/1.2/sponsorship-lifecycle-workflows.md) | **Comprehensive** |
| Agent Principals in Entra | [Agent Identity Architecture](../framework/agent-identity-architecture.md) | **Comprehensive** |
| Blueprint lifecycle phases | [Blueprint Promotion Gates](../playbooks/advanced-implementations/agent-blueprint-promotion-gates/index.md) | **Comprehensive** |

### Data Protection

| Agent 365 Capability | FSI Control | Coverage Status |
|---------------------|-------------|-----------------|
| DLP for Copilot Prompts | [1.5](../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) | **Comprehensive** |
| DSPM for AI | [1.6](../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md) | **Comprehensive** |
| Sensitivity Label Inheritance | [1.5](../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) | **Comprehensive** |
| Agent 365 DLP Policy Scope | [1.5](../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) | **Comprehensive** |
| Blueprint data governance | [1.6](../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md) | **Comprehensive** |

### Inventory & Lifecycle

| Agent 365 Capability | FSI Control | Coverage Status |
|---------------------|-------------|-----------------|
| Agent Registry | [1.2](../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md), [3.1](../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md) | **Comprehensive** |
| Shadow Agent Detection | [3.6](../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) | **Comprehensive** |
| Agent Store Curation | [1.2](../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md) | **Comprehensive** |
| Orphaned Agent Remediation | [3.6](../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) | **Comprehensive** |
| Agent Attestation | [Sponsorship Workflows](../playbooks/control-implementations/1.2/sponsorship-lifecycle-workflows.md) | **Comprehensive** |
| Agent Retirement | [Agent Decommissioning](../playbooks/agent-lifecycle/agent-decommissioning.md) | **Comprehensive** |

### Observability & Audit

| Agent 365 Capability | FSI Control | Coverage Status |
|---------------------|-------------|-----------------|
| OpenTelemetry Integration | [Observability Playbook](../playbooks/advanced-implementations/agent-365-observability/index.md) | **Comprehensive** |
| Agent Activity Dashboard | [3.8](../controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md) | **Comprehensive** |
| AI Usage Events | [1.7](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) | **Comprehensive** |
| Tool Usage Tracking | [Observability Playbook](../playbooks/advanced-implementations/agent-365-observability/opentelemetry-setup.md) | **Comprehensive** |
| Inference Event Logging | [1.7](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) | **Comprehensive** |
| Purview/Defender Integration | [1.7](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md), [3.9](../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md) | **Comprehensive** |
| Blueprint Audit Events | [1.7](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) | **Comprehensive** |

### Security

| Agent 365 Capability | FSI Control | Coverage Status |
|---------------------|-------------|-----------------|
| Defender AI-SPM | [1.24](../controls/pillar-1-security/1.24-defender-ai-security-posture-management.md) | **Comprehensive** |
| AI Threat Detection | [1.8](../controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md), [3.9](../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md) | **Comprehensive** |
| Quarantined Agent Collection | [1.11](../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md) | **Documented** |

### Interoperability

| Agent 365 Capability | FSI Control | Coverage Status |
|---------------------|-------------|-----------------|
| MCP Server Governance | [2.17](../controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md) | **Comprehensive** |
| Cross-Platform Agent Management | [2.17](../controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md) | **Comprehensive** |
| Multi-Agent Orchestration | [2.17](../controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md) | **Comprehensive** |

---

## Quick Reference: Where to Find Agent 365 Guidance

### Framework Documents

| Document | Agent 365 Content |
|----------|-------------------|
| [Agent Identity Architecture](../framework/agent-identity-architecture.md) | Complete Agent ID vs Blueprint architecture guide |
| [Zones and Tiers](../framework/zones-and-tiers.md) | Zone requirements for Agent 365 deployments |
| [Agent Decommissioning](../playbooks/agent-lifecycle/agent-decommissioning.md) | Agent retirement and sponsorship departure handling |

### Reference Documents

| Document | Agent 365 Content |
|----------|-------------------|
| [Agent Essentials Control Mapping](agent-essentials-control-mapping.md) | Microsoft's 8-category checklist mapped to FSI controls |
| [Agent Audit Event Taxonomy](agent-audit-event-taxonomy.md) | Blueprint and Agent ID audit event types |
| [Work IQ Governance Reference](work-iq-governance.md) | Work IQ MCP tools, business skills, admin consent, data-boundary, and audit expectations |
| This document | Consolidated capability summary |

### Playbooks

| Playbook | Agent 365 Content |
|----------|-------------------|
| [Agent 365 Observability](../playbooks/advanced-implementations/agent-365-observability/index.md) | OpenTelemetry setup, workbooks, alerting |
| [Blueprint Promotion Gates](../playbooks/advanced-implementations/agent-blueprint-promotion-gates/index.md) | Lifecycle phase transition governance |
| [Sponsorship Lifecycle Workflows](../playbooks/control-implementations/1.2/sponsorship-lifecycle-workflows.md) | Entra Lifecycle Workflows for sponsor governance |

### Native Admin Center Coverage vs. Deployable Solutions

Microsoft's Agent overview page already provides the tenant-level Agent Registry, pending request queue, ownerless agent queue, and overview analytics surfaces for administrators. In the FSI framework, those native capabilities are covered by [Control 2.25 — Agent 365 Admin Center Governance Console](../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md), [Control 3.13 — Agent 365 Admin Center Analytics and Reporting](../controls/pillar-3-reporting/3.13-agent-365-admin-center-analytics.md), and [Control 3.14 — Agent 365 Observability SDK](../controls/pillar-3-reporting/3.14-agent-365-observability-sdk.md). Deployable solutions should complement those native surfaces rather than duplicate them.

| Need | Primary artifact | Notes |
|------|------------------|-------|
| Native Agent Registry, pending requests, ownerless agents, overview analytics | Controls 2.25 and 3.13 | Use the Microsoft 365 Agent overview and Agent Registry surfaces as the system of record for tenant-level governance monitoring. |
| Automated sponsor enforcement, access reviews, inactivity handling, deactivation workflows | `agent-365-lifecycle-governance` solution | Extends Agent 365 and Entra governance with workflow automation and Dataverse evidence. |
| Custom-agent telemetry, workbooks, and alert routing | Control 3.14 and the `agent-observability-foundation` solution | Use when native overview metrics are insufficient for custom agents or longer-term operational evidence. |

There is no separate live `agent-365-governance-monitor` solution in this repository. If future work is needed, it should stay limited to gaps not already covered by the native Agent 365 admin surfaces and the deployable solutions listed above.

### Controls with Agent 365 Sections

| Control | Agent 365 Section |
|---------|-------------------|
| [1.2 - Agent Registry](../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md) | Agent Store Governance, Blueprint Registration |
| [1.5 - DLP](../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) | DLP for Copilot Prompts, Agent 365 DLP Configuration |
| [1.6 - DSPM for AI](../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md) | Blueprint Data Governance |
| [1.7 - Audit Logging](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) | Agent 365 Audit Events |
| [1.11 - Conditional Access](../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md) | Agent ID Governance, Blueprint Decision Matrix |
| [2.17 - Orchestration Limits](../controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md) | MCP Server Governance |
| [3.1 - Agent Inventory](../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md) | Unified Agent Visibility Architecture |

---

## Regulatory Alignment

Agent 365 capabilities support FSI regulatory requirements:

| Regulation | Agent 365 Capability | Benefit |
|------------|---------------------|---------|
| **FINRA 4511** | Audit logging, Agent Registry | Complete interaction records |
| **FINRA 3110** | Observability SDK, Sponsorship | Supervision evidence |
| **SEC 17a-3/4** | DSPM, Audit events | Record retention compliance |
| **OCC Bulletin 2026-13 (formerly OCC 2011-12)** | Blueprint lifecycle, Registry | Model inventory requirements † |
| **Fed SR 26-2 (formerly SR 11-7)** | Agent ID, Attestation | Model governance accountability † |
| **SOX 302/404** | Observability, Audit trail | Internal control evidence |
| **GLBA 501(b)** | DLP, DSPM, Defender | Customer data protection |

† OCC Bulletin 2026-13 / Fed SR 26-2 **expressly exclude generative and agentic AI** from scope ("not within the scope of this guidance"). Treat these mappings as **analogous sound risk-management principles** that can help inform AI-agent governance, not as direct obligations under OCC Bulletin 2026-13 or Federal Reserve SR 26-2. See the [OCC Bulletin 2026-13 / Fed SR 26-2 scope caveat in Regulatory Mappings](regulatory-mappings.md#occ-bulletin-2026-13-fed-sr-26-2-model-risk-management).

---

## Implementation Guidance

### Phased Adoption

| Phase | Agent 365 Components | FSI Controls to Implement |
|-------|---------------------|---------------------------|
| **Phase 1: Foundation** | Entra Agent ID, Basic Registry | 1.2, 1.11, 3.1 |
| **Phase 2: Data Protection** | DLP for Prompts, DSPM | 1.5, 1.6 |
| **Phase 3: Lifecycle** | Blueprints, Sponsorship, Attestation | 1.11 (expanded), 3.6 |
| **Phase 4: Observability** | OpenTelemetry, Workbooks, Alerts | Observability Playbook |
| **Phase 5: Advanced** | MCP Governance, Multi-Agent | 2.17 |

### Zone-Specific Adoption

| Component | Zone 1 | Zone 2 | Zone 3 |
|-----------|--------|--------|--------|
| Agent ID | Optional | Recommended | Required |
| Blueprints | Not needed | Recommended | Required |
| Agent Store access | Open | Curated | Restricted |
| Observability | Basic | Standard | Full |
| MCP Servers | Not allowed | Approved only | Committee approval |

---

## Related Resources

### Microsoft Documentation

- [Microsoft Learn: Microsoft Agent 365 Overview](https://learn.microsoft.com/en-us/microsoft-agent-365/)
- [Microsoft Learn: Microsoft 365 Agents Deployment Checklist](https://learn.microsoft.com/en-us/microsoft-365/copilot/agent-essentials/m365-agents-checklist)
- [Microsoft Learn: Agents Deployment Blueprint for Microsoft 365](https://learn.microsoft.com/en-us/microsoft-365/copilot/agent-essentials/m365-agents-blueprint)
- [Microsoft Learn: Microsoft Entra Agent ID](https://learn.microsoft.com/en-us/entra/agent-id/)
- [Microsoft Learn: Agent 365 Observability (Preview)](https://learn.microsoft.com/en-us/microsoft-agent-365/developer/observability)
- [Microsoft Learn: Copilot Studio Kit — Compliance Hub](https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/whats-new) — additional compliance resource for Microsoft Copilot Studio governance guidance and release tracking

### FSI-AgentGov Resources

- [Agent Essentials Control Mapping](agent-essentials-control-mapping.md) - Complete 8-category mapping
- [Agent Identity Architecture](../framework/agent-identity-architecture.md) - Technical architecture guide
- [Solutions Index](solutions-index.md) - Deployable automation solutions

---

*FSI Agent Governance Framework v1.6.2 - May 2026*
