---
description: "Governance principles, zones, regulatory context, and operating model for Microsoft 365 AI agents in US financial services organizations."
search:
  boost: 2
---
# Framework Overview

!!! info "Current version: v1.6.2 (May 2026)"
    See [What's New](../changelog.md) for the latest release notes and the full version history.

The FSI Agent Governance Framework provides comprehensive governance guidance for Microsoft 365 AI agents (Microsoft Copilot Studio, Agent Builder) in US financial services organizations.

---

## Purpose

This Framework layer establishes the foundational governance principles, organizational structure, and regulatory context for AI agent deployment. Content here is designed for:

- **Executives and Board Members** — Strategic oversight and risk appetite decisions
- **Compliance Officers** — Regulatory alignment and examination readiness
- **AI Governance Committees** — Policy decisions and approval workflows
- **Auditors** — Framework structure and control objectives

---

## Three-Layer Documentation Architecture

The FSI Agent Governance Framework uses a three-layer documentation model to separate stable governance principles from frequently-updated implementation procedures:

| Layer | Content | Update Frequency | Files |
|-------|---------|------------------|-------|
| **1. Framework** (this layer) | Governance principles, zones, lifecycle, regulatory context | 1-2x per year | 15 pages (this Overview + 14 documents) |
| **2. Control Catalog** | 79 technical control specifications across 4 pillars | Quarterly | 79 control files |
| **3. Playbooks** | Step-by-step implementation procedures | Continuous (as Microsoft portals change) | 316 playbook files (4 per control) |

This separation ensures governance stability while allowing rapid updates to implementation guidance as Microsoft 365 and Power Platform evolve.

---

## Framework Concepts at a Glance

Five interlocking concepts structure this framework. **Admins new to FSI AgentGov need Zone, Pillar, and Control to get started** — Pattern and Capability Driver belong to the Advanced & Scaling track and can be deferred until the core model is working.

| Concept | One-line definition | Where defined |
|---------|--------------------|-----------| 
| **Zone** | Risk classification for an agent: Personal (Zone 1), Team (Zone 2), or Enterprise (Zone 3). Determines which controls apply, approval requirements, and retention periods. | [Zones and Tiers](zones-and-tiers.md) |
| **Pillar** | Control family — Security (29 controls), Management (27), Reporting (14), SharePoint (9). Answers "what *category* is this control?" — not to be confused with Capability Drivers. | [Governance Fundamentals](governance-fundamentals.md#four-governance-pillars) |
| **Control** | A single actionable governance unit — 79 total, each with Baseline / Recommended / Regulated implementation levels. The primary unit of day-to-day governance work. | [Control Catalog](../controls/index.md) |
| **Pattern** ⚡ | Deployment shape (one of six CAPE Frontier Transformation Patterns). Useful for translating CIO conversations into zone and control requirements. | [Transformation Patterns](transformation-patterns.md) |
| **Capability Driver** ⚡ | Organizational readiness dimension (one of five). Measured on a *separate* 100–500 CAPE scale — distinct from the 0–4 control implementation level. | [Capability Drivers](agentic-capability-drivers.md) |

> **⚡ = Advanced & Scaling track.** M365 admins implementing controls can skip Pattern and Capability Driver entirely. Navigate to the [Adoption Roadmap](adoption-roadmap.md) or [Control Catalog](../controls/index.md) to begin implementation.

---

## Framework Components

### Core Documents

| Document | Purpose | Audience |
|----------|---------|----------|
| [Executive Summary](executive-summary.md) | Board-level overview of AI agent risks and governance | C-suite, Board |
| [Governance Fundamentals](governance-fundamentals.md) | Core framework concepts, maturity scale definition, and structure | All stakeholders |
| [Zones and Tiers](zones-and-tiers.md) | Three-zone governance model | Governance committees |
| [Agent Lifecycle](agent-lifecycle.md) | Lifecycle phases and governance requirements | Compliance, Operations |
| [Regulatory Framework](regulatory-framework.md) | US regulatory requirements and control mappings | Compliance, Legal |
| [Operating Model](operating-model.md) | RACI, roles, governance structure | All stakeholders |
| [Governance Cadence](governance-cadence.md) | Review schedules and audit readiness | Compliance, Audit |
| [Adoption Roadmap](adoption-roadmap.md) | Phased implementation guidance | Implementation teams |
| [Relationship to FSI-CopilotGov](relationship-to-copilotgov.md) | Scope boundary with the companion Copilot framework | New users, program leads |
| [Solutions Integration](solutions-integration.md) | Companion solution catalog and automation coverage | Implementation teams |

### Advanced & Scaling

> **First-run admins:** Start with the Core Documents above and the [Control Catalog](../controls/index.md). The four documents below support governance leads and architects who need to map CIO conversations onto zones and controls, assess organizational readiness, or design an Agentic CoE — they are not required for initial control implementation.

| Document | Purpose | Audience |
|----------|---------|----------|
| [Frontier Transformation Patterns](transformation-patterns.md) | Six deployment patterns mapped to zone defaults and regulatory exposure profiles | AI governance leads, architects |
| [Agentic Capability Drivers](agentic-capability-drivers.md) | Five organizational readiness dimensions and maturity targets by pattern | AI program sponsors, governance leads |
| [Unified Agent Governance](agent-identity-architecture.md) | Centralized agent identity, authentication, and authorization (Entra Agent ID, Agent 365, Admin Center) | Security architects |
| [Agentic Center of Excellence](agentic-coe.md) | Four-function CoE blueprint for scaling agent governance without gatekeeper bottlenecks | CoE leads, executive sponsors |

---

## Framework Principles

### 1. Risk-Based Governance

Controls scale with risk. Zone 1 (personal productivity) requires minimal oversight while Zone 3 (enterprise/customer-facing) requires comprehensive governance including committee approval, model risk management, and record-class retention as defined in [Control 1.7](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) rather than a blanket retention period.

### 2. Regulatory Alignment

The framework maps controls to US financial regulations including FINRA 4511/3110, SEC 17a-3/4, SOX 302/404, GLBA 501(b), OCC Bulletin 2026-13 (formerly OCC 2011-12), and Fed SR 26-2 (formerly SR 11-7). Organizations should validate mappings against their specific regulatory obligations.

### 3. Microsoft Platform Foundation

All controls leverage native Microsoft 365 and Power Platform capabilities. This framework does not require third-party governance tools, though organizations may integrate additional solutions.

### 4. Separation of Concerns

The framework separates:

- **Framework** (this layer) — Stable governance principles updated 1-2x per year
- **Control Catalog** — Control objectives and requirements updated quarterly
- **Playbooks** — Implementation procedures updated continuously as Microsoft portals change

---

## Quick Navigation

**For Executives:**

1. Start with [Executive Summary](executive-summary.md)
2. Review [Zones and Tiers](zones-and-tiers.md) for risk classification
3. Understand [Operating Model](operating-model.md) for accountability

**For New Users Comparing Frameworks:**

1. Read [Relationship to FSI-CopilotGov](relationship-to-copilotgov.md) to confirm scope
2. Review [Zones and Tiers](zones-and-tiers.md) for the AgentGov operating model
3. Continue to [Executive Summary](executive-summary.md) for governance context

**For Compliance Officers:**

1. Review [Regulatory Framework](regulatory-framework.md)
2. Understand [Governance Cadence](governance-cadence.md) for examination readiness
3. Reference [Control Catalog](../controls/index.md) for specific requirements

**For Implementation Teams:**

1. Run the [Governance Readiness Assessment](../assessment/index.md) to identify gaps and priorities
2. Follow [Adoption Roadmap](adoption-roadmap.md)
3. Reference [Playbooks](../playbooks/index.md) for step-by-step procedures
4. Use [Control Catalog](../controls/index.md) for control objectives

---

## Version Information

- **Framework Version:** 1.6.2 (May 2026)
- **Last Updated:** May 2026
- **Update Frequency:** 1-2 times per year (major regulatory or platform changes)

---

## Related Sections

- [Control Catalog](../controls/index.md) — Detailed control requirements
- [Playbooks](../playbooks/index.md) — Implementation procedures
- [Reference](../reference/index.md) — Supporting materials

---

**Next →** [Executive Summary](executive-summary.md) — Board-level overview of AI agent risks, governance model, and investment requirements.

---

*FSI Agent Governance Framework v1.6.2 - May 2026*
