# Start Here

**FSI-AgentGov explains how to govern Microsoft 365 AI agents in regulated financial services environments** — especially when your questions are about:

- **Who** can build agents
- **Where** they can run
- **What** data and connectors they can use
- **How** they move into production
- **What evidence** should be retained

!!! warning "Disclaimer"
    This framework is provided for informational purposes only and does not constitute legal, regulatory, or compliance advice. See [full disclaimer](disclaimer.md).

---

## Is This the Right Repository?

### Use this framework if you are:

- an **AI governance lead, Power Platform Admin, compliance lead, security architect, auditor, or business sponsor** responsible for Microsoft 365 AI agents
- deploying **Copilot Studio**, **Agent Builder**, or related custom agent capabilities at a bank, insurer, broker-dealer, or similar US financial institution
- trying to decide what governance controls should exist **before agents move from experimentation into broader use**
- looking for a structured path from **governance strategy** to **technical implementation**

### Start somewhere else if you are:

- governing **Microsoft 365 Copilot** in Word, Excel, PowerPoint, Outlook, Teams, Copilot Chat, or Copilot Pages -> see [FSI-CopilotGov](https://github.com/judeper/FSI-CopilotGov)
- looking for **prompt engineering guidance** or end-user productivity tips
- working outside **regulated US financial services**
- trying to learn basic product capabilities before thinking about governance -> start with [Microsoft Learn](https://learn.microsoft.com/)

---

## Why FSI-AgentGov Exists

Microsoft product documentation explains how to create and configure agents. It does not provide a complete financial-services-focused operating model for:

- governing who can **create, publish, and share** agents
- controlling **environments, connectors, file handling, and data movement**
- scaling controls as agents move from **personal experiments** to **team** and **enterprise** use
- collecting the evidence needed for **oversight, audit, examination preparation, and recurring review**

FSI-AgentGov packages those decisions into **71 controls**, **284 implementation playbooks**, and a **three-zone governance model** so teams can move from ad hoc experimentation to a more structured rollout.

---

## How This Repository Helps a New User

If you are new to the repository, it helps you:

- determine whether an agent belongs in **Zone 1, Zone 2, or Zone 3**
- identify which **foundational controls** to implement first
- route to the right **framework, control, or playbook** page based on your role and scenario
- support risk, compliance, and operational discussions with a common governance reference point

---

## Scenario Guide — Where Should I Go?

| Your Situation | Where to Start |
|---|---|
| "We need to decide whether a new agent belongs in personal, team, or enterprise governance." | [Zones and Tiers](framework/zones-and-tiers.md) + [Agent Lifecycle](framework/agent-lifecycle.md) |
| "We need to control who can create, publish, or move agents into production." | [Control 1.1 - Restrict Agent Publishing](controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md) + [Control 2.1 - Managed Environments](controls/pillar-2-management/2.1-managed-environments.md) + [Control 2.15 - Environment Routing](controls/pillar-2-management/2.15-environment-routing.md) |
| "We need to govern connectors, file handling, and data boundaries." | [Control 1.4 - Advanced Connector Policies](controls/pillar-1-security/1.4-advanced-connector-policies-acp.md) + [Control 1.5 - DLP and Sensitivity Labels](controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) + [Control 1.26 - File Upload Restrictions](controls/pillar-1-security/1.26-agent-file-upload-and-file-analysis-restrictions.md) |
| "We need step-by-step implementation guidance, not just policy statements." | [Quick Start Guide](getting-started/quick-start.md) + [Playbooks Overview](playbooks/index.md) + [Phase 0: Governance Setup](playbooks/getting-started/phase-0-governance-setup.md) |
| "We need evidence for governance, audit, or compliance review." | [Regulatory Framework](framework/regulatory-framework.md) + [Evidence Standards](reference/evidence-standards.md) + [Audit Readiness Checklist](playbooks/compliance-and-audit/audit-readiness-checklist.md) |
| "We are not sure whether AgentGov or CopilotGov is the right starting point." | [Relationship to FSI-CopilotGov](framework/relationship-to-copilotgov.md) |

---

## Recommended First 30 Minutes

1. **Read the [Executive Summary](framework/executive-summary.md)** to understand the governance problem and the operating model.
2. **Confirm scope with [Relationship to FSI-CopilotGov](framework/relationship-to-copilotgov.md)** if your organization also uses Microsoft 365 Copilot.
3. **Review [Zones and Tiers](framework/zones-and-tiers.md)** to understand the three-zone classification model.
4. **Scan the [Control Catalog](controls/index.md)** to see the four pillars and foundational controls.
5. **Open the [Quick Start Guide](getting-started/quick-start.md)** or the [Governance Readiness Assessment](assessment/index.md) to turn orientation into an action plan.

---

## How the Repository Is Organized

| Layer | What it answers | Who uses it |
|---|---|---|
| **[Framework](framework/index.md)** | Why governance matters, how zones work, what regulations apply, and how accountability is structured | Executives, compliance, governance leads |
| **[Controls](controls/index.md)** | What technical and procedural controls should be in place | Architects, admins, control owners |
| **[Playbooks](playbooks/index.md)** | How to implement, verify, and troubleshoot the controls | Hands-on implementers and operations teams |

---

## Next Step

If you want the shortest path from orientation to action, continue to the [Quick Start Guide](getting-started/quick-start.md). If you first need to confirm whether this framework or the Copilot framework applies to your scenario, read [Relationship to FSI-CopilotGov](framework/relationship-to-copilotgov.md).
