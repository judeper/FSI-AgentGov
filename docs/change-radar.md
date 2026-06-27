---
description: A curated, periodically refreshed watch list that maps recent Microsoft 365 agent-platform roadmap changes to the FSI Agent Governance controls they affect.
---

# Change Radar

!!! note "Beta — curated watch list, refreshed periodically"
    Change Radar is a **curated** view of recent Microsoft 365 agent-platform changes mapped to
    this framework's controls. It is refreshed on a periodic cadence (not yet a live automated
    feed). **Curated as of June 26, 2026.**

The **Change Radar** highlights relevant Microsoft 365 agent-platform changes — drawn from the
public [Microsoft 365 roadmap](https://www.microsoft.com/microsoft-365/roadmap) — and maps each
one to the framework control(s) it touches, with a short "what to review" prompt to help teams
keep their governance posture current as the platform evolves.

!!! warning "How to use these mappings"
    The control mappings below are **community-suggested and maintainer-reviewed** — they are
    starting points, not determinations. Verify each item against your own control set and against
    Microsoft's official notice (linked from each entry) before acting. Roadmap dates and scope are
    set by Microsoft and can change or be withdrawn.

## How to read this

- The **change** links to its entry on the public Microsoft 365 roadmap.
- **Affected controls** link to the relevant control pages in this framework.
- **What to review** is a short prompt for the governance evidence or configuration to check.
- **Status** reflects the roadmap state at curation time; confirm current status on the roadmap.

## Roadmap watch

### Available now

| Change | Status | Affected controls | What to review |
| --- | --- | --- | --- |
| [Admin control for org-wide agent sharing](https://www.microsoft.com/microsoft-365/roadmap?featureid=500376) — admins can govern who may create org-wide sharing links for agents built in Copilot Studio agent builder. | GA Oct 2025 | [1.1](controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md), [1.28](controls/pillar-1-security/1.28-policy-based-agent-publishing-restrictions.md) | Confirm your agent publishing and sharing authorization limits who can share agents organization-wide. |
| [Agent ownership reassignment](https://www.microsoft.com/microsoft-365/roadmap?featureid=502867) — admins can reassign ownership of shared agents created in Copilot Studio or the Microsoft 365 Agents Toolkit. | GA Oct 2025 | [1.2](controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md), [3.6](controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) | Add ownership reassignment to your orphaned-agent detection and remediation runbook. |
| [Audit logs for agent management](https://www.microsoft.com/microsoft-365/roadmap?featureid=498227) — agent admin actions such as publishing and blocking are recorded in Purview unified audit logs. | GA Oct 2025 | [1.7](controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md), [3.3](controls/pillar-3-reporting/3.3-compliance-and-regulatory-reporting.md) | Confirm agent admin actions are captured and retained per your recordkeeping obligations (for example, SEC 17a-4, FINRA 4511). |
| [Purview DSPM for AI — apps and agents](https://www.microsoft.com/microsoft-365/roadmap?featureid=489492) — a dashboard of apps and agents used across the organization to surface potential data-security risks. | GA Sep 2025 | [1.6](controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md), [1.24](controls/pillar-1-security/1.24-defender-ai-security-posture-management.md) | Enable the apps-and-agents view and triage flagged agents. |
| [Agent metadata in inventory export](https://www.microsoft.com/microsoft-365/roadmap?featureid=502878) — inventory export adds metadata fields (capabilities, data sources, actions, created-in, created-by). | GA Oct 2025 | [3.1](controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md), [1.2](controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md) | Fold the expanded export fields into your inventory and evidence collection. |
| [Graph APIs for app and agent inventory](https://www.microsoft.com/microsoft-365/roadmap?featureid=502875) — new Microsoft Graph endpoints provide programmatic access to app and agent inventory and details. | GA Apr 2026 | [1.2](controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md), [3.1](controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md), [3.11](controls/pillar-3-reporting/3.11-centralized-agent-inventory-enforcement.md) | Evaluate adopting the Graph endpoints to automate agent inventory evidence. |
| [SharePoint agents in the Agents page](https://www.microsoft.com/microsoft-365/roadmap?featureid=487857) — SharePoint agents appear as shared agents in the Microsoft 365 admin center, with block/unblock from inventory. | GA Oct 2025 | [4.5](controls/pillar-4-sharepoint/4.5-sharepoint-security-and-compliance-monitoring.md), [1.1](controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md), [3.11](controls/pillar-3-reporting/3.11-centralized-agent-inventory-enforcement.md) | Bring SharePoint agents into your unified inventory and block/unblock governance. |
| [Security and compliance info for more agents](https://www.microsoft.com/microsoft-365/roadmap?featureid=503102) — the Teams admin center shows security and compliance information for more certified or publisher-attested apps and agents. | GA Oct 2025 | [2.7](controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md), [1.2](controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md) | Use the certification and attestation signals in agent vetting and third-party risk review. |
| [Larger file uploads in agent builder](https://www.microsoft.com/microsoft-365/roadmap?featureid=500375) — Copilot Studio agent builder supports larger file uploads (up to 512 MB). | GA Sep 2025 | [1.26](controls/pillar-1-security/1.26-agent-file-upload-and-file-analysis-restrictions.md), [1.25](controls/pillar-1-security/1.25-mime-type-restrictions.md) | Larger uploads widen the ingestion surface; verify your file-upload and file-type restrictions. |

### In development

| Change | Status | Affected controls | What to review |
| --- | --- | --- | --- |
| [Approval flow for Frontier and Microsoft agents](https://www.microsoft.com/microsoft-365/roadmap?featureid=494809) — Frontier-program and Microsoft-built agents can be reviewed through an admin request-approval flow in the Microsoft 365 admin center. | GA Jul 2026 | [1.1](controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md), [2.24](controls/pillar-2-management/2.24-agent-feature-enablement-and-restriction-governance.md), [2.25](controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md) | Decide who owns agent approval decisions and how requests are triaged. |
| [MCP-compliant tools in agent workflows](https://www.microsoft.com/microsoft-365/roadmap?featureid=562221) — Copilot Studio agents can use MCP-compliant tools to reach external systems and custom actions. | Preview May 2026, GA Jun 2026 | [1.4](controls/pillar-1-security/1.4-advanced-connector-policies-acp.md), [1.14](controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md), [2.7](controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md) | Extend connector and DLP policies and third-party risk review to cover MCP tools. |
| [Invoke agents as workflow steps (agent node)](https://www.microsoft.com/microsoft-365/roadmap?featureid=562222) — an agent node lets one workflow invoke another agent as a single reasoning step. | Preview Apr 2026, GA Sep 2026 | [2.17](controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md) | Set limits and oversight for agent-to-agent orchestration depth. |

## How Change Radar relates to other pages

- **[Changelog](changelog.md)** — records changes to *this framework* (controls, playbooks, docs).
- **Change Radar** (this page) — tracks changes to *Microsoft's platform* and the controls to review.
- **[Readiness Assessment](assessment/index.md)** — check where your environment stands today.
- **[Control Explorer](controls/explorer.md)** — browse and filter the full control catalog.

!!! warning "Disclaimer"
    This is a community framework and does not constitute legal, regulatory, or compliance advice,
    nor official Microsoft guidance. Organizations should consult their own legal and compliance
    teams. See [Disclaimer](disclaimer.md) for full details.
