# Agent Identity Architecture: Agent ID and Blueprints

**Last Updated:** January 2026

---

## Overview

Microsoft's agent governance model uses a layered architecture where **Agent Identity Blueprints** provide the governance foundation and **Microsoft Entra Agent ID** manages individual agent identities. Understanding this relationship helps organizations select the right approach for their governance requirements.

> **Note:** Agent 365 Blueprints and related SDK features are currently in preview through the Microsoft 365 Frontier preview program. Documentation may change as features evolve toward general availability.

---

## Architecture Layers

### Layer 1: Agent Identity Blueprints (Governance Foundation)

Agent Identity Blueprints define the governance architecture for how agents are registered, managed, and scaled across an organization.

| Aspect | Description |
|--------|-------------|
| **Definition** | Governance architecture defining how agents are registered and managed at scale |
| **Provides** | Permission inheritance, multi-tenant support, governance principals, registration workflows |
| **Required For** | Zone 2+ agents, multi-tenant deployments, formal agent registry |
| **Key Benefit** | Standardized governance patterns across enterprise agent deployments |

**Blueprint Capabilities:**

- **Declarative Registration** - Define agent identity requirements in code
- **Permission Inheritance** - Child agents inherit from parent blueprints
- **Multi-Tenant Support** - Deploy agents across organizational boundaries
- **Lifecycle Governance** - Structured promotion paths from development to production

### Layer 2: Microsoft Entra Agent ID (Identity Management)

Microsoft Entra Agent ID provides identity and access management for AI agents, treating them as first-class identities alongside users and service principals.

| Aspect | Description |
|--------|-------------|
| **Definition** | Identity service managing agent identities for authentication and authorization |
| **Provides** | Conditional Access policies, lifecycle governance, anomaly detection, sponsorship |
| **Can Be Used** | With or without Blueprint (Blueprint recommended for scale) |
| **Key Benefit** | Consistent identity controls across all AI agents |

**Agent ID Capabilities:**

- **Conditional Access** - Apply risk-based policies to agent authentication
- **Lifecycle Governance** - Track agent creation, modification, and decommissioning
- **Anomaly Detection** - Identify unusual agent behavior patterns
- **Human Sponsorship** - Require human accountability for agent lifecycle

### Layer 3: Conditional Access (Policy Enforcement)

Conditional Access policies control how agents access organizational resources based on risk signals and compliance requirements.

| Aspect | Description |
|--------|-------------|
| **Definition** | Risk-based policies controlling agent resource access |
| **Operates On** | Agent identities (whether standalone or Blueprint-managed) |
| **Provides** | Authentication requirements, session controls, access restrictions |
| **Key Benefit** | Consistent security policies across human and agent identities |

---

## Decision Matrix: When to Use What

| Scenario | Agent ID Only | Agent ID + Blueprint |
|----------|---------------|----------------------|
| **Single agent, simple governance** | Sufficient | Optional |
| **Multiple agents, organizational scale** | Possible but complex | Recommended |
| **Multi-tenant deployment** | Not supported | Required |
| **Regulatory audit trail required** | Partial coverage | Full coverage |
| **Zone 1 (Personal)** | Sufficient | Optional |
| **Zone 2 (Team)** | Possible | Recommended |
| **Zone 3 (Enterprise)** | Not recommended | Required |

### Guidance by Governance Zone

**Zone 1 (Personal Productivity):**

- Agent ID provides sufficient identity governance
- Blueprint registration optional for personal agents
- Focus on individual accountability through sponsorship

**Zone 2 (Team Collaboration):**

- Agent ID recommended for all shared agents
- Blueprint recommended for teams with 5+ agents
- Enables consistent permission inheritance across team agents

**Zone 3 (Enterprise Managed):**

- Agent ID required with Conditional Access policies
- Blueprint required for enterprise-scale governance
- Full audit trail and lifecycle management essential
- Supports regulatory examination readiness

---

## Implementation Approach

### Phase 1: Foundation (Agent ID)

1. Enable Microsoft Entra Agent ID in your tenant
2. Assign human sponsors to existing agents
3. Configure Conditional Access policies for agent authentication
4. Establish agent identity lifecycle processes

### Phase 2: Scale (Blueprints)

1. Define organizational blueprint templates by governance zone
2. Register Zone 2/3 agents through blueprint registration
3. Implement permission inheritance hierarchies
4. Configure multi-tenant support if required

### Phase 3: Governance (Integration)

1. Integrate agent registry with blueprint metadata
2. Configure automated compliance checks
3. Establish promotion workflows using blueprint gates
4. Enable comprehensive audit logging across layers

---

## Related Framework Components

| Component | Relationship |
|-----------|--------------|
| [Control 1.2 - Agent Registry](../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md) | Blueprint registration feeds agent registry |
| [Control 1.11 - Conditional Access](../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md) | Agent ID Conditional Access configuration |
| [Control 2.1 - Managed Environments](../controls/pillar-2-management/2.1-managed-environments.md) | Blueprint lifecycle phases align with environment promotion |
| [Control 3.6 - Orphaned Agent Detection](../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) | Agent ID lifecycle governance supports orphan detection |

---

## Additional Resources

- [Microsoft Learn: Agent ID Overview](https://learn.microsoft.com/en-us/entra/agent-id/)
- [Microsoft Learn: Agent Identities for AI Agents](https://learn.microsoft.com/en-us/entra/agent-id/identity-professional/microsoft-entra-agent-identities-for-ai-agents)
- [Microsoft Learn: Governing Agent Identities](https://learn.microsoft.com/en-us/entra/id-governance/agent-id-governance-overview)
- [Microsoft Learn: Agent 365 Blueprint (Preview)](https://learn.microsoft.com/en-us/copilot/microsoft-365/agent-essentials/m365-agents-blueprint)
- [Microsoft Learn: Agent 365 Deployment Checklist (Preview)](https://learn.microsoft.com/en-us/copilot/microsoft-365/agent-essentials/m365-agents-checklist)

---

*Updated: January 2026 | Version: v1.2*
