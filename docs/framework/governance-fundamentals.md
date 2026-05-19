# Governance Fundamentals

Core concepts and principles for AI agent governance in financial services.

---

## Adaptive Governance Philosophy

This framework is built on the principle of **adaptive governance**: controls that scale proportionally with risk rather than applying uniform restrictions across all agent use cases. A low-risk personal productivity agent is not the same as an agent connected to a core business system — governance should reflect that difference.

Adaptive governance rests on three operational pillars:

1. **Classify risk clearly** — The [three governance zones](zones-and-tiers.md) (Personal, Team, Enterprise) provide graduated risk classification that determines the level of oversight, approval, and audit requirements for each agent.
2. **Enforce through the platform** — Governance is most effective when it is inherent to the platform, not layered on through policy documents alone. [Managed environments](../controls/pillar-2-management/2.1-managed-environments.md), [environment groups](../controls/pillar-2-management/2.2-environment-groups-and-tier-classification.md), [DLP policies](../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md), and [environment routing](../controls/pillar-2-management/2.15-environment-routing.md) enforce boundaries automatically — reducing reliance on manual processes and individual compliance.
3. **Create promotion paths** — Rather than restricting all agent development, the framework provides a supported path from personal experimentation (Zone 1) through team collaboration (Zone 2) to enterprise production (Zone 3). [Sharing limits](../controls/pillar-2-management/2.1-managed-environments.md) paired with [zone progression criteria](zones-and-tiers.md#zone-progression-model) create a clear on-ramp: agents can scale when they meet the governance requirements of the next zone.

!!! tip "Why This Matters"
    Governance models that only restrict — without providing supported paths for innovation — tend to drive shadow IT. By combining platform-enforced controls with clear promotion criteria, organizations can let teams experiment freely in Zone 1 while requiring deliberate promotion, review, and accountability when agents are ready to reach broader audiences.

---

## Framework Overview

The FSI Agent Governance Framework provides complete guidance for deploying, governing, and managing Microsoft 365 agents (Microsoft Copilot Studio, Agent Builder, and related AI services) in regulated financial services environments.

**Version:** v1.6.2 (May 2026)
**Target Audience:** US Financial Services Organizations
**Regulatory Focus:** FINRA, SEC, SOX, GLBA, OCC, Federal Reserve, FDIC, NCUA, CFTC

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
| Agent 365 control plane | GA (May 1, 2026) | M365 Admin Center |

!!! info "Microsoft Agent 365 — Generally Available May 1, 2026"
    **Microsoft Agent 365** is the centralized control plane for agent governance, announced at Ignite 2025 and **generally available as of May 1, 2026**. It provides centralized agent registry, Entra Agent ID, lifecycle management, and observability dashboards. At GA, Agent 365 transitions from preview per-agent-instance licensing to **per-user** licensing — agents acting on behalf of a licensed user are covered under that user's **Agent 365** or **Microsoft 365 E7** license. See [Agent 365 overview](https://learn.microsoft.com/en-us/microsoft-agent-365/overview) for current details.

!!! info "Entra Agent ID — Generally Available (April 2026)"
    **Entra Agent ID** provides first-class agent identities in Microsoft Entra, enabling Conditional Access, Identity Protection, and lifecycle management for AI agents. The Entra Agent ID platform reached **general availability in April 2026** ([Entra fundamentals — What's new](https://learn.microsoft.com/en-us/entra/fundamentals/whats-new); [Entra Agent ID — What's new](https://learn.microsoft.com/en-us/entra/agent-id/whats-new-agent-id)) after Public Preview since November 2025. The **Microsoft Agent 365** licensing bundle that packages Agent ID into the Agent 365 control plane (and into Microsoft 365 E7) became generally available on **May 1, 2026** — these are two distinct milestones. Some adjacent surfaces (for example the `agentSignIn` log type and specific Lifecycle Workflows agent-sponsor tasks) remain in Public Preview; verify current GA / preview status against Microsoft Learn before relying on a specific behaviour in production. See [Agent Identity Architecture](agent-identity-architecture.md) for implementation guidance and FSI readiness assessment.

### Microsoft-Built Agent Applicability

Microsoft-built agents (Researcher, Analyst, Facilitator) have limited governance options. Control applicability:

| Control Category | Applicability | Notes |
|-----------------|---------------|-------|
| 1.2 Agent Registry | Partial | Visible in M365 Admin Center only |
| 1.5 DLP/Sensitivity Labels | Full | Tenant-wide policies apply |
| 1.7 Audit Logging | Full | Logged via OfficeActivity |
| 2.1 Managed Environments | N/A | Not in Power Platform |
| 2.3 Change Management | N/A | Managed by Microsoft |
| 3.1 Agent Inventory | Full | Visible in M365 Admin Center |
| 3.2 Usage Analytics | Full | Copilot usage reports |
| 4.1-4.9 SharePoint | Full | Grounding data governance applies |

**Zone Classification:** Based on data access - Zone 1 (personal M365), Zone 2 (team sites), Zone 3 (regulated content).

!!! warning "Limited Customization"
    Microsoft-built agents cannot be configured. Governance focuses on data access control,
    usage monitoring, and output supervision.

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
| **Identity and access hygiene** | Existing permissions are correctly scoped before agent deployment |

!!! warning "Agents Expose Existing Permission Problems"
    Agents generally operate under the calling user's identity and permissions — they do not create new access rights. This means agents do not introduce permission problems; they **surface existing over-permissioning faster** by making previously obscure but technically accessible content more discoverable. Organizations should audit and remediate identity and access management (IAM) gaps — particularly oversharing in SharePoint, broad security group memberships, and excessive delegated permissions — **before** deploying agents broadly. See [DSPM for AI](../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md) and [M365 Copilot Data Governance](../controls/pillar-4-sharepoint/4.7-microsoft-365-copilot-data-governance.md) for assessment tools and remediation guidance.

---

## Four Governance Pillars

The framework organizes 78 controls across four pillars:

| Pillar | Controls | Focus | Examples |
|--------|----------|-------|----------|
| **1. [Security](../controls/pillar-1-security/index.md)** | 29 | Protect data and systems | DLP, Audit, Encryption, MFA, eDiscovery, Network Isolation, Information Barriers |
| **2. [Management](../controls/pillar-2-management/index.md)** | 26 | Govern lifecycle and risk | Change Control, Testing, Model Risk, Multi-Agent Orchestration, HITL Framework |
| **3. [Reporting](../controls/pillar-3-reporting/index.md)** | 14 | Monitor and track | Inventory, Usage, PPAC, Sentinel, Hallucination Feedback |
| **4. [SharePoint](../controls/pillar-4-sharepoint/index.md)** | 9 | SharePoint-specific controls | Access, Retention, External Sharing, Grounding Scope, Copilot Data Governance |

**Note:** Pillar 4 specializes Pillars 1-3 for SharePoint as an agent knowledge source. Controls address SharePoint-specific implementation of data protection, access governance, and content management.

---

## Capability Drivers (Organizational Readiness)

The framework's 78 controls describe *what to implement and how to verify it*. [Capability Drivers](../reference/glossary.md) describe *whether your organization is capable of implementing and operating it at scale*.

Microsoft's Copilot Acceleration Engineering (CAPE) materials introduced five **Capability Drivers** as organizational readiness dimensions whose collective maturity determines an enterprise's capacity to deploy AI agents sustainably. FSI-AgentGov adopted Capability Drivers as a first-class framework concept in v1.5.0 (current at v1.6.2), complementing — not replacing — the control-by-control governance lens. The five drivers are:

| Capability Driver | What It Measures |
|-------------------|------------------|
| **AI Strategy & Experience** | AI portfolio governance maturity — how the organization decides what to build, sponsor, and sunset |
| **Business Strategy** | Business value alignment maturity — how AI investments are tied to named outcomes, KPIs, and accountable business owners |
| **AI Governance & Security** | Risk management and control posture maturity — how the organization maintains examiner-defensible governance over the agent estate |
| **Technology & Data** | Platform and data engineering maturity — environment strategy, identity, telemetry, RAG corpus integrity, observability |
| **Organization & Culture** | Workforce enablement and change maturity — supervisor training, maker community, AI-positive but compliance-aware culture |

Each driver is measured on a 100–500 maturity scale (Initial → Repeatable → Defined → Capable → Optimized). Microsoft positions this model as a **diagnostic for finding the weakest link**, not a scorecard to maximize: the weakest driver becomes the ceiling on how far any agentic transformation can scale, regardless of strength in other dimensions.

### Pillars vs. Drivers: Critical Disambiguation

**Pillars** are FSI-AgentGov's four **control families**: Security (29 controls), Management (26), Reporting (14), SharePoint (9). [Pillars](../reference/glossary.md) answer *"What category of control is this?"*

**Drivers** are the five **organizational readiness dimensions** listed above. Drivers answer *"Where is the organization weak?"*

The terms must not be conflated. Microsoft's CAPE source materials occasionally use "pillar" for the five readiness dimensions in slide titles; FSI-AgentGov canonicalizes to "Capability Driver" exclusively to prevent collision with our control families. The framework language linter (`scripts/verify_language_rules.py`) enforces this discipline.

### Framework Conceptual Model

The framework operates through five complementary lenses:

- **Pattern** — names a deployment shape (what is this agent doing?) — Six transformation patterns defined in [Transformation Patterns](transformation-patterns.md)
- **Zone** — names a regulatory classification (Personal / Team / Enterprise) — See [Zones and Tiers](zones-and-tiers.md)
- **Pillar** — names a control family (Security / Management / Reporting / SharePoint)
- **Driver** — names an organizational readiness dimension (one of the five above)
- **Control** — the actionable governance unit (78 total across all four pillars)

A single agent has one pattern, one zone classification, and N applicable controls across all four pillars. Capability Drivers describe the organization's capacity to actually implement those controls at scale — across many agents, many patterns, sustained over time.

**Example:** An FSI firm can pass every Pillar 1 (Security) control on the FSI assessment engine and still be incapable of scaling a Pattern 4 (Core Business Process) deployment because its Business Strategy driver is at Level 200 (no documented agent-supported process redesign, no named business owner, no KPI ownership). The driver lens surfaces that gap before the deployment fails an examination.

### Scale-Breakers

A [scale-breaker](../reference/glossary.md) is the single capability dimension that blocks an organization's ability to scale its agent portfolio, regardless of strength in other areas. Microsoft's diagnostic identifies five common scale-breaker signals:

- Many pilots with no portfolio governance
- One-off agents with no component reuse
- Great demos with low sustained adoption
- Licenses purchased without measurable usage
- Shadow agents appearing outside managed environments

Each Frontier Transformation Pattern has typical scale-breakers documented in the [Microsoft CAPE crosswalk](../reference/microsoft-cape-crosswalk.md). Recognizing and addressing scale-breakers early is essential for sustainable agent deployment in regulated environments.

### For Full Treatment

The framework provides a complete FSI translation of Microsoft's Capability Drivers model:

- [Agentic Capability Drivers](agentic-capability-drivers.md) — Per-driver maturity profiles, scale-breaker analysis by pattern, FSI-translated 100–500 progression, and the explicit position on why FSI-AgentGov does not numerically merge the CAPE maturity scale with the FSI 0–4 control maturity scale
- [Microsoft CAPE Crosswalk](../reference/microsoft-cape-crosswalk.md) — Six transformation patterns mapped to FSI control requirements, autonomy caps, and regulatory exposure analysis

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

### Trust by Design with Built-In Verification

The Governance Triangle reflects a **trust-by-design** approach: strong proactive controls (Policy Layer) set boundaries that allow agents to operate with appropriate autonomy, while reactive controls (Process Layer) verify those boundaries hold through monitoring, diagnostics, and audit trails.

This mirrors how organizations manage other operational risks. Consider expense approvals: humans unintentionally approve incorrect items regularly, and that risk is managed through audits, compensating controls, and limits on blast radius — not by eliminating approvals entirely. Agent governance follows the same principle: know what happened, understand why it happened, and contain the impact when outcomes differ from expectations.

- **Proactive controls** — DLP policies, sharing limits, environment groups, publishing restrictions
- **Reactive controls** — Audit logging, Sentinel integration, compliance reporting, incident response
- **Compensating controls** — Hallucination feedback loops, access reviews, orphaned agent detection

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

!!! info "Maturity Assessment"
    For compliance tracking, use the 5-point maturity scale: Level 0 (Not implemented),
    Level 1 (Baseline), Level 2-3 (Recommended), Level 4 (Regulated).
    See [FAQ](../reference/faq.md#q-how-do-we-measure-compliance) for percentages.

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

- [Control Catalog](../controls/index.md) — All 78 controls
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

## Further Reading

- [Building Trustworthy AI: A Practical Framework for Adaptive Governance](https://www.microsoft.com/en-us/power-platform/blog/2026/04/01/building-trustworthy-ai-a-practical-framework-for-adaptive-governance/) — Microsoft Power Platform Blog (April 2026). Discusses adaptive governance, graduated risk zones, and platform-enforced controls for AI agents.
- [Agent Identity Architecture](agent-identity-architecture.md) — Entra Agent ID and Agent 365 governance architecture
- [Zones and Tiers](zones-and-tiers.md) — Detailed zone definitions and progression criteria

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
