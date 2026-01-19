# FSI Agent Governance Framework

**Version:** 1.1 (January 2026)

Comprehensive governance framework for Microsoft 365 AI agents (Copilot Studio, Agent Builder) in US financial services organizations.

!!! warning "Disclaimer"
    This framework is provided for informational purposes only and does not constitute legal, regulatory, or compliance advice. Organizations should consult with their legal counsel and compliance teams. See [Disclaimer](disclaimer.md) for full details.

---

## Quick Start by Role

### I'm a Compliance Officer or AI Governance Lead

Start here to understand the governance framework and regulatory alignment.

1. **Read:** [Executive Summary](framework/executive-summary.md) — Board-level overview
2. **Then:** [Operating Model](framework/operating-model.md) — Roles and RACI
3. **Then:** [Regulatory Framework](framework/regulatory-framework.md) — Control-to-regulation mappings
4. **Action:** [Adoption Roadmap](framework/adoption-roadmap.md) — Phased implementation

### I'm a Power Platform Administrator

Start here for technical implementation guidance.

1. **Read:** [Control Catalog](controls/index.md) — All 61 controls
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

## Framework Structure

The framework is organized into three layers:

| Layer | Audience | Content |
|-------|----------|---------|
| **[Framework](framework/index.md)** | Executives, Compliance, Governance | Principles, zones, regulatory context |
| **[Control Catalog](controls/index.md)** | Compliance Officers, Architects | 61 control requirements |
| **[Playbooks](playbooks/index.md)** | Platform Teams, Operations | Step-by-step procedures |

---

## Control Summary

**61 controls** across four governance pillars:

| Pillar | Controls | Focus |
|--------|----------|-------|
| [Pillar 1: Security](controls/pillar-1-security/index.md) | 23 | DLP, audit, encryption, MFA, eDiscovery |
| [Pillar 2: Management](controls/pillar-2-management/index.md) | 21 | Lifecycle, testing, model risk, supervision |
| [Pillar 3: Reporting](controls/pillar-3-reporting/index.md) | 10 | Inventory, usage, PPAC, Sentinel |
| [Pillar 4: SharePoint](controls/pillar-4-sharepoint/index.md) | 7 | Access, retention, grounding scope |

**Three governance zones** based on risk:

| Zone | Risk | Data Access | Approval |
|------|------|-------------|----------|
| [Zone 1: Personal](framework/zones-and-tiers.md#zone-1) | Low | M365 Graph only | Self-service |
| [Zone 2: Team](framework/zones-and-tiers.md#zone-2) | Medium | Internal data | Manager |
| [Zone 3: Enterprise](framework/zones-and-tiers.md#zone-3) | High | Regulated data | Governance Committee |

---

## Regulatory Coverage

Controls map to major US financial regulations:

- **FINRA 4511/3110/25-07** — Books and records, supervision, AI governance
- **SEC 17a-3/4** — Recordkeeping requirements
- **SOX 302/404** — Internal controls
- **GLBA 501(b)** — Safeguards rule
- **OCC 2011-12 / SR 11-7** — Model risk management

See [Regulatory Framework](framework/regulatory-framework.md) for complete mappings.

---

## Quick Links

**Getting Started:**

- [Quick Start Guide](getting-started/quick-start.md)
- [Implementation Checklist](getting-started/checklist.md)
- [Phase 0 Setup Playbook](playbooks/getting-started/phase-0-governance-setup.md)

**Reference:**

- [Control Index](controls/index.md)
- [Glossary](reference/glossary.md)
- [FAQ](reference/faq.md)
- [Administrator Templates](downloads/index.md)

---

## Stay Current

- [Star this repository](https://github.com/judeper/FSI-AgentGov) on GitHub
- Use **Watch > Releases** for update notifications
- Share with your compliance team for review

---

## Latest Updates

See [CHANGELOG](https://github.com/judeper/FSI-AgentGov/blob/main/CHANGELOG.md) for version history.

**v1.1 (January 2026):**

- Restructured into three layers (Framework, Controls, Playbooks)
- Added Executive Summary and Adoption Roadmap
- Created role-based navigation
- Enhanced examination readiness materials

---

*FSI Agent Governance Framework v1.1 - January 2026*
