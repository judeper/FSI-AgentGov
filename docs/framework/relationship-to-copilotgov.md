# Relationship to FSI-CopilotGov

Scope boundary between FSI-AgentGov and FSI-CopilotGov, with guidance on when to use each framework.

---

## Why Two Repositories Exist

Microsoft 365 AI governance spans two related but distinct questions:

1. How should an organization govern **Microsoft 365 Copilot experiences** embedded in apps such as Word, Outlook, Teams, and Copilot Chat?
2. How should an organization govern **custom and managed AI agents** built through Microsoft Copilot Studio, Agent Builder, and related Microsoft 365 / Power Platform controls?

**FSI-CopilotGov** addresses the first question. **FSI-AgentGov** addresses the second.

Both repositories are standalone and complementary. Where governance topics overlap, each repository explains them from the perspective of its own scope.

---

## Comparison Table

| Aspect | FSI-AgentGov | FSI-CopilotGov |
|--------|--------------|----------------|
| **Primary subject** | Copilot Studio, Agent Builder, and related Microsoft 365 AI agents | Microsoft 365 Copilot embedded across M365 apps |
| **What it governs** | Agent creation, publishing, environments, connectors, lifecycle, approvals, and monitoring | Copilot access, oversharing exposure, feature governance, and Copilot usage across M365 surfaces |
| **Governance model** | Zone 1 / Zone 2 / Zone 3 | Baseline / Recommended / Regulated |
| **Pillars** | Security, Management, Reporting, SharePoint | Readiness, Security, Compliance, Operations |
| **Controls** | 78 | 54 |
| **Playbooks** | 312 | 216 |
| **Primary operating question** | How do we govern agents as managed assets? | How do we govern Copilot as an embedded user-facing capability? |
| **Primary risk emphasis** | Unmanaged agent creation, publishing, connector use, lifecycle drift, and insufficient oversight | Oversharing amplification, Copilot-generated content risk, and per-surface operational governance |

---

## Use FSI-AgentGov When

| Scenario | Why |
|----------|-----|
| Building or governing **Copilot Studio** agents | AgentGov focuses on agent-specific lifecycle, publishing, and control requirements |
| Governing **Agent Builder** usage in Microsoft 365 | AgentGov covers the operating model for agents as governed assets |
| Managing **managed environments, environment groups, or environment routing** | These are central AgentGov control topics |
| Controlling **connectors, data movement, file handling, or agent promotion** | AgentGov provides the relevant controls and linked playbooks |
| Preparing governance reviews for **custom agents with regulated data access** | AgentGov organizes controls, approvals, verification, and evidence expectations around agent deployments |

---

## Use FSI-CopilotGov When

| Scenario | Why |
|----------|-----|
| Governing **Microsoft 365 Copilot** in Word, Excel, PowerPoint, Outlook, Teams, or Copilot Chat | CopilotGov focuses on M365 Copilot as an embedded productivity capability |
| Assessing **oversharing exposure** before enabling Copilot broadly | CopilotGov emphasizes Copilot-specific data exposure and readiness questions |
| Managing **per-app Copilot controls, web grounding, or Copilot feature toggles** | Those are CopilotGov topics rather than agent platform controls |
| Preparing governance guidance for **user-facing Copilot rollout** across M365 applications | CopilotGov is the better starting point for that program scope |

---

## Use Both Repositories When

| Scenario | How they complement each other |
|----------|--------------------------------|
| Your organization deploys both **Microsoft 365 Copilot** and **custom AI agents** | CopilotGov covers the embedded Copilot estate; AgentGov covers custom agents and their platform controls |
| You need one governance program spanning **Copilot usage** and **agent development** | CopilotGov helps frame user-facing Copilot risk; AgentGov helps govern agents as buildable, deployable assets |
| Shared topics such as **DLP, audit logging, retention, and SharePoint governance** apply to both | Each repository explains the shared topic from the viewpoint of its own scope |

---

## Shared Topics, Different Emphasis

| Topic | AgentGov emphasis | CopilotGov emphasis |
|-------|-------------------|---------------------|
| **DLP and sensitivity labels** | Agent connectors, data boundaries, and agent data handling | Copilot access to labeled content across M365 surfaces |
| **Audit logging and evidence** | Agent actions, promotion, lifecycle oversight, and agent governance evidence | Copilot interactions, Copilot-generated content, and operational review |
| **SharePoint governance** | SharePoint as an agent knowledge source and controlled grounding surface | SharePoint content as surfaced and amplified by Microsoft 365 Copilot |
| **Risk-based governance** | Zone progression from personal to enterprise-managed agents | Tiered governance expectations for Copilot deployment maturity |

---

## Recommended Decision Rule

- Start with **FSI-AgentGov** when your main question is **how an agent is built, governed, published, or controlled**.
- Start with **FSI-CopilotGov** when your main question is **how Microsoft 365 Copilot should be governed across user-facing applications**.
- Use **both** when your program includes both custom agents and Microsoft 365 Copilot.

---

## Next Step

If you are new to this repository, return to [Start Here](../start-here.md). If you are ready to understand AgentGov's operating model, continue to [Zones and Tiers](zones-and-tiers.md) or the [Executive Summary](executive-summary.md).

---

*FSI Agent Governance Framework v1.6.2 - June 2026*
