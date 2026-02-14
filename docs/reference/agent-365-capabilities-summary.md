# Agent 365 Capabilities Summary

**Last Updated:** February 2026
**Version:** v1.2.43

---

## Overview

This reference consolidates all Microsoft Agent 365 capabilities documented across the FSI-AgentGov framework. Use this page to quickly locate Agent 365-specific guidance and demonstrate comprehensive coverage to stakeholders and auditors.

!!! note "Preview Status"
    Microsoft Agent 365 SDK and Agent Essentials remain in preview through the Microsoft 365 Frontier preview program. Feature availability and documentation may change before general availability.

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
| This document | Consolidated capability summary |

### Playbooks

| Playbook | Agent 365 Content |
|----------|-------------------|
| [Agent 365 Observability](../playbooks/advanced-implementations/agent-365-observability/index.md) | OpenTelemetry setup, workbooks, alerting |
| [Blueprint Promotion Gates](../playbooks/advanced-implementations/agent-blueprint-promotion-gates/index.md) | Lifecycle phase transition governance |
| [Sponsorship Lifecycle Workflows](../playbooks/control-implementations/1.2/sponsorship-lifecycle-workflows.md) | Entra Lifecycle Workflows for sponsor governance |

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
| **OCC 2011-12** | Blueprint lifecycle, Registry | Model inventory requirements |
| **Fed SR 11-7** | Agent ID, Attestation | Model governance accountability |
| **SOX 302/404** | Observability, Audit trail | Internal control evidence |
| **GLBA 501(b)** | DLP, DSPM, Defender | Customer data protection |

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

- [Microsoft Learn: Agent 365 Overview (Preview)](https://learn.microsoft.com/en-us/microsoft-agent-365/)
- [Microsoft Learn: Agent Essentials Checklist (Preview)](https://learn.microsoft.com/en-us/copilot/microsoft-365/agent-essentials/m365-agents-checklist)
- [Microsoft Learn: Agent 365 Blueprint (Preview)](https://learn.microsoft.com/en-us/copilot/microsoft-365/agent-essentials/m365-agents-blueprint)
- [Microsoft Learn: Microsoft Entra Agent ID](https://learn.microsoft.com/en-us/entra/agent-id/)
- [Microsoft Learn: Agent 365 Observability (Preview)](https://learn.microsoft.com/en-us/microsoft-agent-365/developer/observability)

### FSI-AgentGov Resources

- [Agent Essentials Control Mapping](agent-essentials-control-mapping.md) - Complete 8-category mapping
- [Agent Identity Architecture](../framework/agent-identity-architecture.md) - Technical architecture guide
- [Solutions Index](solutions-index.md) - Deployable automation solutions

---

*FSI Agent Governance Framework v1.2.43 - February 2026*
