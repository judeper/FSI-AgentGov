---
created: 2026-02-04T13:59
title: Review Agent 365 meeting notes against framework
area: docs
files:
  - docs/framework/agent-365-architecture.md
  - docs/controls/pillar-1-security/control-1.11.md
  - docs/controls/pillar-2-management/control-2.12.md
  - docs/reference/role-catalog.md
  - docs/controls/pillar-3-reporting/control-3.8.md
---

## Problem

Internal meeting on Agent 365 provided updated information on feature availability, roadmap, technical limitations, and security integration. Need to compare these meeting notes against the framework's current Agent 365 documentation to identify any gaps, inaccuracies, or new content that should be incorporated.

### Key areas requiring review against framework:

**1. Agent Registry and Visibility**
- Copilot Studio agents published to M365 Copilot/Teams visible in Agent 365 registry
- Foundry agents will be included at GA
- Declarative agents (Agent Builder) appear in registry but lack org-wide deployment/pinning
- Shadow AI agent discovery (including GCP/AWS-hosted agents) planned for post-GA

**2. Agent Deployment and Management**
- Declarative agents require export/import for org-wide deployment; direct publish under consideration
- Admins can block/delete agents but cannot deploy declarative agents org-wide from registry today
- Instance creation (digital workers) from Foundry planned for future

**3. Observability and Security**
- Observability integrating with Purview and Defender
- Real-time protection and prompt filtering for Copilot Studio agents available
- Blocked prompt visibility in Defender is inconsistent and under review
- Shadow AI discovery will leverage Entra and Defender capabilities

**4. APIs and Automation**
- Admin APIs planned for Agent 365 (UI automation)
- Multi-tenant API support NOT committed; single-tenant focus
- This may affect solutions that assume API availability

**5. Admin Roles and Access**
- Access limited to Global Administrators and AI Admins only
- No new roles planned for GA
- Feedback being collected on finer-grained/read-only roles
- Framework role catalog (role-catalog.md) should be checked against this

**6. Technical Challenges and Limitations**
- Agent onboarding bugs affecting activation (fixes rolling out)
- Declarative agent deployment not scalable for large orgs
- Security events (prompt filtering) not consistently in Defender advanced hunting
- Multi-tenant management not yet available

**7. Licensing**
- Feature-to-license mappings NOT finalized
- Current preview access does not reflect final licensing requirements
- Framework references to licensing (Control 2.1, etc.) may need review

### Framework documents to check:
- `docs/framework/agent-365-architecture.md` — Core Agent 365 architecture document (Phase 3)
- `docs/controls/pillar-1-security/control-1.11.md` — Agent registration and lifecycle
- `docs/controls/pillar-2-management/control-2.12.md` — Supervisory controls with Entra Agent ID sponsorship
- `docs/controls/pillar-3-reporting/control-3.8.md` — AI Feature Access Control / Copilot Hub governance
- `docs/reference/role-catalog.md` — AI Administrator role entry
- Controls referencing Defender integration (1.8, 1.6)
- Controls referencing DLP/observability (1.5, 1.6)

## Solution

Systematic review:
1. Read each referenced framework document
2. Compare meeting notes against documented capabilities
3. Identify gaps (new info not in framework), inaccuracies (framework states something differently), and preview items that need admonition updates
4. Propose specific changes organized by priority (Critical/High/Medium/Low)
5. Pay special attention to: preview vs GA status changes, role access limitations, deployment friction for declarative agents, and Defender visibility gaps
6. Verify "Frontier program" preview admonitions are still appropriate or need updating based on GA timeline signals
