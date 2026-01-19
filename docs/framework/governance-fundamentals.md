# Governance Fundamentals

Core concepts and principles for AI agent governance in financial services.

---

## Framework Overview

The FSI Agent Governance Framework provides complete guidance for deploying, governing, and managing Microsoft 365 agents (Copilot Studio, Agent Builder, and related AI services) in regulated financial services environments.

**Version:** 1.1 (January 2026)
**Target Audience:** US Financial Services Organizations
**Regulatory Focus:** FINRA, SEC, SOX, GLBA, OCC, Federal Reserve

!!! warning
    This framework is provided for informational purposes only and does not constitute legal,
    regulatory, or compliance advice. See [Disclaimer](../disclaimer.md) for full details.

---

## Scope and Assumptions

### What This Framework Covers

This framework provides governance guidance for:

- **Copilot Studio** agents
- **Agent Builder** agents
- **Power Platform** environments hosting agents
- **SharePoint** as a knowledge source for agents

### Agent Types In Scope

| Agent Type | In Scope? | Governance Location |
|------------|-----------|---------------------|
| Copilot Studio custom agents | Primary focus | Power Platform Admin Center |
| Agent Builder agents (M365) | Primary focus | M365 Admin Center + PPAC |
| Microsoft-built agents (Researcher, Analyst, Facilitator) | Partial | M365 Admin Center (limited controls) |
| Third-party/partner agents | Varies by integration | M365 Admin Center |
| Agent 365 control plane | Future (Frontier preview) | M365 Admin Center |

!!! info "Microsoft Agent 365"
    **Microsoft Agent 365** is a new centralized control plane for agent governance announced at Ignite 2025, currently in **Frontier preview**. It provides centralized agent registry, Entra Agent ID, lifecycle management, and observability dashboards. This framework will incorporate Agent 365 capabilities as they reach general availability.

### What This Framework Does NOT Cover

- **Non-US regulations** (EU AI Act, GDPR, DORA, MiFID II are out of scope)
- **Non-Microsoft AI platforms** (OpenAI direct, AWS Bedrock, Google Vertex AI, etc.)
- Custom ML model development, training, or validation
- Quantitative model risk management (requires dedicated MRM programs)
- State privacy laws (CCPA/CPRA require separate analysis)
- Third-party AI integrations outside Microsoft 365 ecosystem

### Key Assumptions

| Assumption | Rationale |
|------------|-----------|
| **Microsoft 365 E3/E5** | Required for Copilot Studio, Purview, and advanced governance features |
| **Microsoft Entra ID** | Identity and access management foundation |
| **Microsoft Purview** | Compliance and data governance capabilities |
| **Power Platform licensing** | Required for environment management and DLP policies |
| **Foundational IT controls** | Network security, endpoint protection, backup/recovery assumed in place |

---

## Four Governance Pillars

The framework organizes 61 controls across four pillars:

| Pillar | Controls | Focus | Examples |
|--------|----------|-------|----------|
| **1. [Security](../controls/pillar-1-security/index.md)** | 23 | Protect data and systems | DLP, Audit, Encryption, MFA, eDiscovery, Network Isolation, Information Barriers |
| **2. [Management](../controls/pillar-2-management/index.md)** | 21 | Govern lifecycle and risk | Change Control, Testing, Model Risk, Multi-Agent Orchestration, HITL Framework |
| **3. [Reporting](../controls/pillar-3-reporting/index.md)** | 10 | Monitor and track | Inventory, Usage, PPAC, Sentinel, Hallucination Feedback |
| **4. [SharePoint](../controls/pillar-4-sharepoint/index.md)** | 7 | SharePoint-specific controls | Access, Retention, External Sharing, Grounding Scope, Copilot Data Governance |

**Note:** Pillar 4 specializes Pillars 1-3 for SharePoint as an agent knowledge source. Controls address SharePoint-specific implementation of data protection, access governance, and content management.

---

## Three Governance Zones

Agents are classified into zones based on risk level:

| Zone | Risk Level | Data Access | Approval | Audit Retention |
|------|------------|-------------|----------|-----------------|
| **[Zone 1: Personal](zones-and-tiers.md#zone-1)** | Low | M365 Graph only | Self-service | 30 days |
| **[Zone 2: Team](zones-and-tiers.md#zone-2)** | Medium | Internal data | Manager approval | 1 year |
| **[Zone 3: Enterprise](zones-and-tiers.md#zone-3)** | High | Regulated data | Governance Committee | 10 years |

See [Zones and Tiers](zones-and-tiers.md) for detailed zone definitions and selection criteria.

---

## Governance Triangle

Effective agent governance operates through three interconnected layers:

### Policy Layer (Technical Controls)

Automated guardrails that enforce governance without manual intervention:

| Component | Purpose | Implementation |
|-----------|---------|----------------|
| **Environment Groups** | Consistent policy across environments | PPAC environment groups |
| **Group Rules** | Connector, sharing, channel controls | Environment group rules |
| **DLP Policies** | Data boundary enforcement | Data policies |
| **Environment Routing** | Automatic maker placement | Default environment routing |

### Process Layer (Operational Workflows)

How governance decisions are made and executed:

- **Agent Lifecycle Management** — Creation, testing, deployment, monitoring, retirement
- **Approval Workflows** — Zone-appropriate authorization paths
- **Change Control** — Controlled promotion between environments
- **Incident Response** — Detection, investigation, remediation procedures
- **Compliance Reviews** — Scheduled verification of control effectiveness

### People Layer (Organizational Structure)

Accountability and human oversight:

| Role | Governance Function | Zone Focus |
|------|---------------------|------------|
| **AI Governance Lead** | Framework ownership, policy decisions | All zones |
| **Power Platform Admin** | Technical implementation, environment management | Zones 2-3 |
| **Compliance Officer** | Regulatory alignment, audit coordination | Zones 2-3 |
| **Business Owner** | Agent sponsorship, use case validation | Per agent |
| **Security / CISO** | Threat monitoring, incident response | Zone 3 |

### How the Layers Interact

1. **Policy enables Process** — Technical controls automate workflow enforcement
2. **Process guides People** — Defined procedures clarify responsibilities
3. **People inform Policy** — Human judgment shapes control configuration

!!! tip "FSI Note"
    In regulated environments, all three layers must be documented and auditable. Examiners expect
    evidence of policy configuration, process execution, and role assignment.

---

## Governance Maturity Levels

Each control supports three implementation levels:

| Level | Name | Description | Typical Use |
|-------|------|-------------|-------------|
| **Level 1** | Baseline | Minimum required implementation | Initial deployment, Zone 1 |
| **Level 2-3** | Recommended | Best practice implementation | Zone 2, most production agents |
| **Level 4** | Regulated/High-Risk | Comprehensive controls | Zone 3, customer-facing agents |

### Control Implementation Approach

1. **Assess** — Current state vs. required level
2. **Implement** — Follow playbook guidance
3. **Verify** — Use verification procedures
4. **Document** — Record evidence for audit
5. **Review** — Schedule recurring reviews

---

## Integration with Existing Governance

This framework is designed to **complement, not replace** existing enterprise governance programs:

- Integrate controls with your existing IT risk management framework
- Align with enterprise information security policies
- Coordinate with records retention and eDiscovery requirements
- Map to your organization's internal audit program

!!! note
    Organizations should validate all controls against their specific regulatory obligations and
    existing policy frameworks.

---

## Framework Documentation Structure

### Three-Layer Architecture

| Layer | Audience | Update Frequency | Content |
|-------|----------|------------------|---------|
| **Framework** (this layer) | Executives, compliance, governance | 1-2x per year | Principles, zones, regulatory context |
| **Control Catalog** | Compliance officers, architects | Quarterly | Control objectives, requirements |
| **Playbooks** | Platform teams, operations | Continuous | Portal steps, scripts, screenshots |

### Navigation Guide

**For Governance Questions:**

- [Framework Overview](index.md) — This layer
- [Zones and Tiers](zones-and-tiers.md) — Classification requirements
- [Operating Model](operating-model.md) — Roles and responsibilities

**For Control Requirements:**

- [Control Catalog](../controls/index.md) — All 61 controls
- [Regulatory Framework](regulatory-framework.md) — Regulation-to-control mappings

**For Implementation:**

- [Playbooks](../playbooks/index.md) — Step-by-step procedures
- [Adoption Roadmap](adoption-roadmap.md) — Phased implementation

---

## Quick Reference

### Getting Started

1. Read [Executive Summary](executive-summary.md) (10 minutes)
2. Review [Zones and Tiers](zones-and-tiers.md) to classify agents (15 minutes)
3. Check [Regulatory Framework](regulatory-framework.md) for applicable regulations (10 minutes)

### For Implementation

1. Use the [Adoption Roadmap](adoption-roadmap.md) for phased approach
2. Reference [Control Catalog](../controls/index.md) for requirements
3. Follow [Playbooks](../playbooks/index.md) for step-by-step procedures
4. Schedule reviews per [Governance Cadence](governance-cadence.md)

### For Governance

1. Use the [Operating Model](operating-model.md) for roles and responsibilities
2. Establish governance committee per [Zones and Tiers](zones-and-tiers.md)
3. Schedule recurring compliance reviews
4. Track incidents per playbook procedures

---

*FSI Agent Governance Framework v1.1 - January 2026*
