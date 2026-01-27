# Agent Essentials Control Mapping Reference

**Last Updated:** January 2026
**Version:** v1.2.6

---

## Overview

This reference maps Microsoft's Agent Essentials deployment checklist categories to the FSI Agent Governance Framework controls. Use this mapping to align Microsoft's governance recommendations with your existing FSI control implementations.

!!! note "Preview Status"
    Microsoft Agent Essentials and Agent 365 SDK are in preview through the Microsoft 365 Frontier preview program. Category definitions and checklist items may change before general availability.

---

## Agent Essentials Categories

Microsoft's Agent Essentials defines 8 governance categories for enterprise AI agent deployment:

| Category | Focus Area | Primary Concern |
|----------|------------|-----------------|
| 1. Access & Availability | Who can use agents | Identity and access management |
| 2. Copilot Studio Experience | Maker portal configuration | Development environment |
| 3. Agent Builder | In-app agent creation | Citizen development governance |
| 4. Application Lifecycle | DevOps and ALM | Change management |
| 5. Copilot Studio Creation | Agent building controls | Development governance |
| 6. Inventory & Lifecycle | Agent tracking | Asset management |
| 7. Data Security/Compliance | Data protection | Regulatory compliance |
| 8. Billing & Capacity | Cost management | Financial governance |

---

## Category-to-Control Mapping

### Category 1: Access & Availability

**Microsoft Focus:** Configure who can access and use AI agents across the organization.

| FSI Control | Mapping Rationale |
|-------------|-------------------|
| [1.1 - Restrict Agent Publishing](../controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md) | Controls who can publish agents to users |
| [1.11 - Conditional Access](../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md) | Enforces authentication requirements for agent access |
| [2.8 - Segregation of Duties](../controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md) | Separates maker, publisher, and admin roles |

**Implementation Notes:**

- Use Conditional Access policies to require MFA for agent creators (Control 1.11)
- Configure environment security groups to control agent visibility (Control 1.1)
- Implement RBAC to separate development and publishing permissions (Control 2.8)

**Agent Essentials Checklist Items:**

| Checklist Item | FSI Control | Status |
|----------------|-------------|--------|
| Define agent user audience | 1.1 | Implement per zone |
| Configure Conditional Access for agents | 1.11 | Phishing-resistant for Zone 3 |
| Establish maker vs. user permissions | 2.8 | RACI matrix |

---

### Category 2: Copilot Studio Experience

**Microsoft Focus:** Configure the Copilot Studio maker portal experience.

| FSI Control | Mapping Rationale |
|-------------|-------------------|
| [2.1 - Managed Environments](../controls/pillar-2-management/2.1-managed-environments.md) | Enables governance features in development environments |
| [3.8 - Copilot Hub](../controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md) | Provides visibility into agent development activity |

**Implementation Notes:**

- Enable Managed Environments for all Zone 2+ development (Control 2.1)
- Use Copilot Hub dashboards to monitor maker activity (Control 3.8)
- Configure environment-level settings for maker welcome content

**Agent Essentials Checklist Items:**

| Checklist Item | FSI Control | Status |
|----------------|-------------|--------|
| Enable Managed Environments | 2.1 | Required for Zone 2+ |
| Configure maker welcome content | 2.1 | Custom for FSI |
| Monitor studio usage | 3.8 | Weekly review |

---

### Category 3: Agent Builder

**Microsoft Focus:** Govern in-app agent creation (agents built within Microsoft 365 apps).

| FSI Control | Mapping Rationale |
|-------------|-------------------|
| [1.1 - Restrict Agent Publishing](../controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md) | Controls in-app agent creation permissions |
| [1.2 - Agent Registry](../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md) | Tracks agents created through in-app builders |
| [2.1 - Managed Environments](../controls/pillar-2-management/2.1-managed-environments.md) | Routes in-app agents to appropriate environments |

**Implementation Notes:**

- M365 Admin Center "Agent settings" controls in-app agent creation
- Consider disabling for Zone 3 environments where formal governance is required
- Monitor Agent Builder activity through Copilot Hub (Control 3.8)

**Agent Essentials Checklist Items:**

| Checklist Item | FSI Control | Status |
|----------------|-------------|--------|
| Configure Agent Builder access | 1.1 | Per zone policy |
| Route to governed environments | 2.1 | Environment routing rules |
| Track in-app created agents | 1.2, 3.1 | Registry entry required |

---

### Category 4: Application Lifecycle

**Microsoft Focus:** Establish DevOps practices for agent development and deployment.

| FSI Control | Mapping Rationale |
|-------------|-------------------|
| [2.3 - Change Management](../controls/pillar-2-management/2.3-change-management-and-release-planning.md) | Governs agent changes through approval workflows |
| [2.5 - Testing and Validation](../controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md) | Defines testing requirements before deployment |

**Implementation Notes:**

- Power Platform ALM pipelines integrate with Blueprint lifecycle phases
- Blueprint promotion gates align with Control 2.3 approval requirements
- Zone 3 agents require CAB approval before production deployment

**Agent Essentials Checklist Items:**

| Checklist Item | FSI Control | Status |
|----------------|-------------|--------|
| Configure ALM pipelines | 2.3 | Required for Zone 2+ |
| Define testing requirements | 2.5 | Per zone thresholds |
| Implement approval gates | 2.3 | See Blueprint Promotion Gates playbook |

**Related Playbook:** [Agent Blueprint Promotion Gates](../playbooks/advanced-implementations/agent-blueprint-promotion-gates/index.md)

---

### Category 5: Copilot Studio Creation

**Microsoft Focus:** Control how agents are built in Copilot Studio.

| FSI Control | Mapping Rationale |
|-------------|-------------------|
| [1.1 - Restrict Agent Publishing](../controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md) | Controls who can create agents in Copilot Studio |
| [2.1 - Managed Environments](../controls/pillar-2-management/2.1-managed-environments.md) | Governs development environment settings |
| [2.5 - Testing and Validation](../controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md) | Establishes quality gates for agent creation |
| [3.8 - Copilot Hub](../controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md) | Monitors agent creation activity |

**Implementation Notes:**

- Limit Copilot Studio access to approved makers via security groups
- Use Managed Environments to enforce DLP and sharing policies
- Require pre-publish security scans for Zone 3 agents

**Agent Essentials Checklist Items:**

| Checklist Item | FSI Control | Status |
|----------------|-------------|--------|
| Define maker groups | 1.1 | Zone-specific groups |
| Enable pre-publish checks | 2.1, 2.5 | Automatic security scan |
| Configure connector policies | 1.4 | DLP enforcement |
| Monitor creation activity | 3.8 | Dashboard alerts |

---

### Category 6: Inventory & Lifecycle

**Microsoft Focus:** Track agents throughout their lifecycle.

| FSI Control | Mapping Rationale |
|-------------|-------------------|
| [3.1 - Agent Inventory](../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md) | Maintains comprehensive agent registry |
| [3.6 - Orphaned Agent Detection](../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) | Identifies agents without owners or sponsors |

**Implementation Notes:**

- M365 Admin Center provides basic inventory; enhance with custom registry
- Entra Agent ID enables sponsor-based lifecycle management
- Shadow agent detection identifies unregistered agents (Control 3.6)

**Agent Essentials Checklist Items:**

| Checklist Item | FSI Control | Status |
|----------------|-------------|--------|
| Establish agent registry | 3.1 | Dataverse-based recommended |
| Assign sponsors to agents | 1.11, 3.6 | Required for Zone 2+ |
| Configure orphan detection | 3.6 | Weekly scan |
| Define decommissioning process | 3.6 | See agent lifecycle playbooks |

**Related Playbook:** [Sponsorship Lifecycle Workflows](../playbooks/control-implementations/1.2/sponsorship-lifecycle-workflows.md)

---

### Category 7: Data Security/Compliance

**Microsoft Focus:** Protect data accessed and processed by agents.

| FSI Control | Mapping Rationale |
|-------------|-------------------|
| [1.5 - DLP and Sensitivity Labels](../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) | Prevents data leakage through agent channels |
| [1.6 - DSPM for AI](../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md) | Monitors AI data interactions |
| [1.7 - Comprehensive Audit Logging](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) | Captures agent interactions for compliance |
| [1.14 - Data Minimization](../controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md) | Limits agent access to necessary data |

**Implementation Notes:**

- Configure DLP policies specifically for Copilot Studio channels
- Enable DSPM for AI to monitor prompt/response data flows
- Retain audit logs per regulatory requirements (FINRA 4511, SEC 17a-4)

**Agent Essentials Checklist Items:**

| Checklist Item | FSI Control | Status |
|----------------|-------------|--------|
| Configure DLP for agent channels | 1.5 | Block sensitive data exfil |
| Enable DSPM for AI | 1.6 | Required for Zone 3 |
| Configure audit retention | 1.7 | 7-10 years for Zone 3 |
| Implement data minimization | 1.14 | Least privilege access |

---

### Category 8: Billing & Capacity

**Microsoft Focus:** Manage costs and capacity allocation for AI agents.

| FSI Control | Mapping Rationale |
|-------------|-------------------|
| [3.5 - Cost Allocation](../controls/pillar-3-reporting/3.5-cost-allocation-and-budget-tracking.md) | Tracks agent-related costs by department/zone |
| [3.2 - Usage Analytics](../controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md) | Monitors agent usage patterns for capacity planning |

**Implementation Notes:**

- AI Builder capacity allocated per environment; track consumption
- Message units and capacity units require monitoring
- Consider chargeback models for Zone 2 departmental agents

**Agent Essentials Checklist Items:**

| Checklist Item | FSI Control | Status |
|----------------|-------------|--------|
| Configure cost tracking | 3.5 | Per environment |
| Monitor capacity usage | 3.2 | Weekly review |
| Establish chargeback model | 3.5 | Department allocation |
| Set usage alerts | 3.2 | Threshold notifications |

---

## Quick Reference Matrix

| MS Category | Primary Controls | Zone 2 | Zone 3 |
|-------------|------------------|--------|--------|
| 1. Access & Availability | 1.1, 1.11, 2.8 | MFA required | Phishing-resistant MFA |
| 2. Copilot Studio Experience | 2.1, 3.8 | Managed Environment | + Approval workflows |
| 3. Agent Builder | 1.1, 1.2, 2.1 | Controlled access | Disabled or restricted |
| 4. Application Lifecycle | 2.3, 2.5 | ALM pipelines | + CAB approval |
| 5. Copilot Studio Creation | 1.1, 2.1, 2.5, 3.8 | Security groups | + Pre-publish scan |
| 6. Inventory & Lifecycle | 3.1, 3.6 | Registry + sponsor | + Weekly reviews |
| 7. Data Security/Compliance | 1.5, 1.6, 1.7, 1.14 | DLP + logging | + DSPM + 10yr retention |
| 8. Billing & Capacity | 3.5, 3.2 | Monitoring | + Chargeback |

---

## Implementation Priority

For organizations beginning Agent Essentials implementation, prioritize:

### Phase 1: Foundation (Week 1-2)

1. **Category 1 (Access)** - Establish identity controls
2. **Category 7 (Data Security)** - Configure DLP and logging
3. **Category 6 (Inventory)** - Set up agent registry

### Phase 2: Development Governance (Week 3-4)

4. **Category 2 (Studio Experience)** - Configure Managed Environments
5. **Category 5 (Studio Creation)** - Set maker permissions
6. **Category 3 (Agent Builder)** - Control in-app creation

### Phase 3: Lifecycle Management (Week 5-6)

7. **Category 4 (Application Lifecycle)** - Implement ALM pipelines
8. **Category 8 (Billing)** - Configure cost tracking

---

## Related Resources

- [Agent Identity Architecture](../framework/agent-identity-architecture.md) - Agent ID vs Blueprint guidance
- [Microsoft Learn: Agent Essentials Checklist (Preview)](https://learn.microsoft.com/en-us/copilot/microsoft-365/agent-essentials/m365-agents-checklist)
- [Microsoft Learn: Agent Essentials Visual Guide (Preview)](https://learn.microsoft.com/en-us/copilot/microsoft-365/agent-essentials/m365-agents-visual-map)
- [Microsoft Learn: Agent 365 Blueprint (Preview)](https://learn.microsoft.com/en-us/copilot/microsoft-365/agent-essentials/m365-agents-blueprint)

---

*FSI Agent Governance Framework v1.2.6 - January 2026*
