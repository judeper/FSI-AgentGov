# FSI Agent Governance Framework

![Version](https://img.shields.io/github/v/release/judeper/FSI-AgentGov?label=version&color=blue)
![Controls](https://img.shields.io/badge/controls-71-green)
![Regulations](https://img.shields.io/badge/FINRA%20%7C%20SEC%20%7C%20SOX%20%7C%20GLBA-covered-orange)

FSI-AgentGov helps US financial services organizations govern Microsoft 365 AI agents such as Copilot Studio agents, Agent Builder agents, and related custom agent deployments. It exists to turn agent governance questions—who can build, publish, connect, approve, monitor, and retire agents—into a practical framework, control catalog, and implementation playbooks.

!!! tip "New to this framework?"
    Start with [Start Here](start-here.md) for newcomer orientation. If you are deciding between this repo and the M365 Copilot framework, also read [Relationship to FSI-CopilotGov](framework/relationship-to-copilotgov.md).

## Why This Framework Exists

Custom agents create governance decisions that standard product setup guidance does not answer consistently. Teams still need to decide how agents are classified, which environments and connectors they may use, what approvals apply before production use, and what evidence should be retained for risk, oversight, audit, and examination review.

This framework helps you:

- classify agents into **Zone 1, Zone 2, or Zone 3**
- identify which controls should be implemented before broader rollout
- move from governance policy to technical implementation with linked playbooks
- support a more defensible operating model for regulated deployments

---

## Framework Structure

The framework is organized into three layers:

| Layer | Audience | Content |
|-------|----------|---------|
| **[Framework](framework/index.md)** | Executives, Compliance, Governance | Principles, zones, regulatory context |
| **[Control Catalog](controls/index.md)** | Compliance Officers, Architects | 71 control requirements |
| **[Playbooks](playbooks/index.md)** | Platform Teams, Operations | Step-by-step procedures |

## Key Concepts for First-Time Users

| Term | What it means |
|------|---------------|
| **Zone** | The risk classification for how broadly an agent is used and what data it can access |
| **Control** | A governance requirement that tells you what should be in place |
| **Playbook** | Step-by-step implementation, verification, or troubleshooting guidance |

## Quick Start by Role

### I'm a Compliance Officer or AI Governance Lead

Start here to understand the governance framework and regulatory alignment.

1. **Assess:** [Governance Readiness Assessment](assessment/index.md) — Evaluate your current posture across all 71 controls
2. **Read:** [Executive Summary](framework/executive-summary.md) — Board-level overview
3. **Then:** [Operating Model](framework/operating-model.md) — Roles and RACI
4. **Then:** [Regulatory Framework](framework/regulatory-framework.md) — Control-to-regulation mappings
5. **Action:** [Adoption Roadmap](framework/adoption-roadmap.md) — Phased implementation

### I'm a Power Platform Admin

Start here for technical implementation guidance.

1. **Read:** [Control Catalog](controls/index.md) — All 71 controls
2. **Then:** [Pillar 1 Security](controls/pillar-1-security/index.md) and [Pillar 2 Management](controls/pillar-2-management/index.md)
3. **Action:** [Implementation Playbooks](playbooks/index.md) — Step-by-step procedures
4. **Use:** [Phase 0 Setup](playbooks/getting-started/phase-0-governance-setup.md) — Initial deployment

### I'm Preparing for FINRA/SEC Examination

Start here for examination readiness materials.

1. **Read:** [Regulatory Framework](framework/regulatory-framework.md) — Regulation mappings
2. **Then:** [Evidence Standards](reference/evidence-standards.md) — Documentation requirements
3. **Action:** [Audit Readiness Checklist](playbooks/compliance-and-audit/audit-readiness-checklist.md)
4. **Use:** [Evidence Pack Assembly](playbooks/compliance-and-audit/evidence-pack-assembly.md)

### I'm a Business Owner Requesting an Agent

Start here to understand what's needed for agent approval.

1. **Read:** [Zones and Tiers](framework/zones-and-tiers.md) — Understand zone requirements
2. **Then:** [Agent Lifecycle](framework/agent-lifecycle.md) — Approval process
3. **Action:** [Agent Promotion Checklist](playbooks/agent-lifecycle/agent-promotion-checklist.md)

---

## Control Summary

**71 controls** across four governance pillars:

| Pillar | Controls | Focus |
|--------|----------|-------|
| [Pillar 1: Security](controls/pillar-1-security/index.md) | 28 | DLP, audit, encryption, MFA, eDiscovery |
| [Pillar 2: Management](controls/pillar-2-management/index.md) | 24 | Lifecycle, testing, model risk, supervision |
| [Pillar 3: Reporting](controls/pillar-3-reporting/index.md) | 12 | Inventory, usage, PPAC, Sentinel |
| [Pillar 4: SharePoint](controls/pillar-4-sharepoint/index.md) | 7 | Access, retention, grounding scope |

**Three governance zones** based on risk:

| Zone | Risk | Data Access | Approval |
|------|------|-------------|----------|
| [Zone 1: Personal](framework/zones-and-tiers.md#zone-1) | Low | M365 Graph only | Self-service |
| [Zone 2: Team](framework/zones-and-tiers.md#zone-2) | Medium | Internal data | Manager |
| [Zone 3: Enterprise](framework/zones-and-tiers.md#zone-3) | High | Regulated data | Governance Committee |

## Regulatory Coverage

Controls map to major US financial regulations:

- **FINRA 4511/3110** — Books and records, supervision
- **SEC 17a-3/4** — Recordkeeping requirements
- **SOX 302/404** — Internal controls
- **GLBA 501(b)** — Safeguards rule
- **OCC 2011-12 / SR 11-7** — Model risk management

See [Regulatory Framework](framework/regulatory-framework.md) for complete mappings.

## Quick Links

**Getting Started:**

- [Start Here](start-here.md) — New user orientation and scope guidance
- [Governance Readiness Assessment](assessment/index.md) — Interactive tool to assess all 71 controls
- [Quick Start Guide](getting-started/quick-start.md)
- [Implementation Checklist](getting-started/checklist.md)
- [Phase 0 Setup Playbook](playbooks/getting-started/phase-0-governance-setup.md)

**Reference:**

- [Relationship to FSI-CopilotGov](framework/relationship-to-copilotgov.md)
- [Control Index](controls/index.md)
- [Glossary](reference/glossary.md)
- [FAQ](reference/faq.md)
- [Administrator Templates](downloads/index.md)

*[Star this repository](https://github.com/judeper/FSI-AgentGov) on GitHub and use **Watch > Releases** for update notifications.*

---

!!! warning "Disclaimer"
    This framework is provided for informational purposes only and does not constitute legal, regulatory, or compliance advice. Organizations should consult with their legal counsel and compliance teams. See [Disclaimer](disclaimer.md) for full details.

---

## Latest Updates

See [CHANGELOG](https://github.com/judeper/FSI-AgentGov/blob/main/CHANGELOG.md) for full version history.
