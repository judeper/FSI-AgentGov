# Work IQ Governance Reference

!!! info "Preview and availability note"
    Microsoft Learn describes Work IQ as the intelligence layer that personalizes Microsoft 365 Copilot and agents through data, context, and skills/tools. Several extensibility surfaces covered here are currently documented as preview, including Work IQ MCP tools in Agent 365 and Copilot Studio, Business skills with Dataverse intelligence, and Work IQ CLI. Validate current availability, regional support, supplemental terms, and production readiness in Microsoft Learn before adopting these capabilities for regulated workflows. Sources: [Work IQ overview](https://learn.microsoft.com/microsoft-365/copilot/extensibility/work-iq), [Work IQ MCP overview](https://learn.microsoft.com/microsoft-agent-365/tooling-servers-overview), [Add Work IQ MCP to your agents](https://learn.microsoft.com/microsoft-copilot-studio/use-work-iq), [Business skills overview](https://learn.microsoft.com/power-apps/maker/data-platform/data-platform-business-skill-overview), and [Work IQ CLI overview](https://learn.microsoft.com/microsoft-365/copilot/extensibility/workiq-overview).

---

## Overview

Work IQ is the Microsoft 365 Copilot intelligence layer that brings together organizational data, work context, and skills/tools so Copilot and agents can reason over work artifacts and invoke approved tools. Microsoft Learn describes Work IQ as combining tenant data, context, and skills/tools across Microsoft 365, Dynamics 365, Power Apps, Dataverse, Copilot connectors, and MCP tools. See [Microsoft Learn: Work IQ overview](https://learn.microsoft.com/microsoft-365/copilot/extensibility/work-iq).

For governance purposes, treat Work IQ as a platform capability that can expose Microsoft 365 and business-system context to agents. It is not a separate control catalog entry or a separate license row in this framework; licensing prerequisites should be validated against the specific Work IQ MCP, Copilot Studio, Agent 365, Microsoft 365 Copilot, and Dataverse surfaces used. Microsoft Learn states that Work IQ MCP servers require a Microsoft 365 Copilot license. See [Work IQ MCP prerequisites](https://learn.microsoft.com/microsoft-agent-365/tooling-servers-overview#prerequisites).

## MCP tool catalog implications

Work IQ MCP tools are published through the Agent 365 tooling model and are documented as a preview feature. Microsoft Learn lists examples including Work IQ Copilot, Work IQ Calendar, Work IQ Mail, Work IQ SharePoint, Work IQ OneDrive, Work IQ Teams, Work IQ User, Work IQ Word, and Dataverse and Dynamics 365. See [Work IQ MCP overview](https://learn.microsoft.com/microsoft-agent-365/tooling-servers-overview#agent-365-tools-catalog).

Governance implications for the MCP tool inventory:

- Record each Work IQ MCP server as an approved tool source in the MCP inventory used by [Control 2.17](../controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md).
- Track whether the tool is Microsoft-published, custom, or BYO MCP, and document status, publisher, type, requested-by, approval date, and block state using the Microsoft 365 admin center Agent Tools registry. See [Manage tools for agents](https://learn.microsoft.com/microsoft-365/admin/manage/manage-tools-for-agent).
- Classify the data each Work IQ tool can reach, such as mail, calendar, Teams, SharePoint, OneDrive, Word, or Dataverse, because Work IQ MCP tools can perform actions and retrieve context across these workloads. See [Work IQ MCP tool catalog](https://learn.microsoft.com/microsoft-agent-365/tooling-servers-overview#agent-365-tools-catalog).
- Require pre-production testing for high-impact tools that can create, update, delete, send, or publish content, and retain the approval evidence under the same review cadence used for custom MCP servers in [Control 2.17](../controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md).

## Business-skill publishing governance

Business skills with Dataverse intelligence are documented as prerelease / preview. Microsoft Learn describes business skills as natural-language instructions that capture business processes, policies, and domain knowledge; the same page states that business skills are not executable code and follow Dataverse security patterns. See [Business skills overview](https://learn.microsoft.com/power-apps/maker/data-platform/data-platform-business-skill-overview).

Recommended governance pattern:

- Treat each business skill as a governed reusable process artifact with an owner, approval record, business purpose, applicable agents, and review cadence.
- Use Dataverse security and sharing controls for creation, use, publishing, and environment-wide deployment. Microsoft Learn lists Basic User, Environment Maker, and Dataverse System Administrator or System Customizer roles as examples of role-based privileges for business skills. See [Business skills security and governance](https://learn.microsoft.com/power-apps/maker/data-platform/data-platform-business-skill-overview#security-and-governance).
- Require change-management review before sharing a skill across multiple agents, especially where the skill affects customer communications, trading operations, account servicing, or regulated advice workflows.
- Promote skills through managed Dataverse solutions where possible, because Microsoft Learn describes business skills as solution-aware objects. See [Business skills key capabilities](https://learn.microsoft.com/power-apps/maker/data-platform/data-platform-business-skill-overview).

## Admin consent surfaces

Work IQ governance uses both admin-center controls and runtime connection consent surfaces:

- **Microsoft 365 admin center — Agent Tools registry:** Admins can view tools under **Agents > Tools > Registry**, filter by status and publisher, and block or unblock tools. See [View the Agent Tools registry](https://learn.microsoft.com/microsoft-365/admin/manage/manage-tools-for-agent#view-the-agent-tools-registry).
- **Microsoft 365 admin center — Requests:** For BYO MCP servers, admins review requests under **Agents > Tools > Requests**, approve or reject the server, and consent to the required Microsoft Entra permissions after approval. See [Review and approve tool requests](https://learn.microsoft.com/microsoft-365/admin/manage/manage-tools-for-agent#review-and-approve-tool-requests).
- **Agent 365 application permissions:** Microsoft Learn states that each MCP server corresponds to a permission on the Agent 365 application and that an agent gains access to the MCP server only after required consent. See [Governance using Microsoft 365 admin center](https://learn.microsoft.com/microsoft-agent-365/tooling-servers-overview#governance-using-microsoft-365-admin-center).
- **Copilot Studio connection prompt:** When adding Work IQ MCP tools in Copilot Studio, makers select a Work IQ tool, create a connection, complete sign-in, and may be prompted to allow the Work IQ tool to connect and use services. See [Connect your agent to Work IQ](https://learn.microsoft.com/microsoft-copilot-studio/use-work-iq#connect-your-agent-to-work-iq).

!!! note "Regional control availability"
    Microsoft Learn notes that the ability to allow or disallow tooling and MCP servers in the Microsoft 365 admin center might not be available in every region yet. Confirm tenant-region support before making the Agent Tools block state your sole approval control. See [Work IQ MCP governance in Microsoft 365 admin center](https://learn.microsoft.com/microsoft-copilot-studio/use-work-iq#governance-using-microsoft-365-admin-center).

## Data-boundary considerations

Work IQ can operate over permission-scoped Microsoft 365 tenant data, Dataverse business data, Copilot connector data, semantic index signals, and MCP tool calls. Microsoft Learn states that Microsoft Graph tenant data includes permission-based and information-protected SharePoint and OneDrive content, Outlook emails, Teams meetings and chats, and collaboration signals; it also states that the semantic index respects organizational boundaries and permission structures. See [Work IQ data layer](https://learn.microsoft.com/microsoft-365/copilot/extensibility/work-iq#data) and [Work IQ semantic index](https://learn.microsoft.com/microsoft-365/copilot/extensibility/work-iq#semantic-index).

FSI implementation considerations:

- Map each Work IQ MCP tool to the tenant workloads and data classifications it can reach before approval.
- Confirm whether external Copilot connectors or federated connectors introduce additional data residency, indexing, retention, or vendor-review obligations. Microsoft Learn describes Copilot connectors and federated connectors as extensions to the Work IQ data layer, with federated connectors documented as early access preview. See [External business data from Copilot connectors](https://learn.microsoft.com/microsoft-365/copilot/extensibility/work-iq#external-business-data-from-copilot-connectors).
- For U.S. government or sovereign-cloud tenants, validate feature availability separately. Microsoft Learn states that Microsoft 365 Copilot is available in GCC, GCC High, and DoD, but that feature availability may differ, release timing typically lags commercial environments, and third-party integrations are more restricted in higher-isolation environments. See [Microsoft 365 Copilot government cloud overview](https://learn.microsoft.com/microsoft-365/copilot/gov-overview).
- Do not assume a commercial Work IQ MCP, business-skill, or Agent Tools feature is available in GCC, GCC High, DoD, or other sovereign deployments until the specific tenant and Microsoft Learn availability statement are verified.

## Audit-log expectations

Use [Control 1.7 — Comprehensive Audit Logging](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) as the audit foundation for Work IQ. Microsoft Purview's audit activity reference includes an **Agent 365 activities** category with `AIExecuteTool`, `AIInvokeAgent`, and `AIInferenceCall` operations for tool calls, agent invocation, and AI inference calls. The same reference includes **Application administration activities** such as service principal and delegation changes, which are relevant when Agent 365 permissions or application consent change. See [Microsoft Purview audit log activities](https://learn.microsoft.com/purview/audit-log-activities).

For MCP server activity, Microsoft Learn also documents Defender Advanced Hunting queries against `CloudAppEvents` with `ActionType` values such as `ExecuteToolByGateway` to observe MCP server invocations. See [Monitor and observe MCP server activity](https://learn.microsoft.com/microsoft-365/admin/manage/manage-tools-for-agent#monitor-and-observe-mcp-server-activity).

Expected evidence sources:

| Evidence source | Work IQ relevance | Framework control |
|-----------------|-------------------|-------------------|
| Purview audit — Agent 365 activities | Tool execution, agent invocation, and inference events | [1.7](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md), [3.14](../controls/pillar-3-reporting/3.14-agent-365-observability-sdk.md) |
| Purview audit — Application administration activities | Service principal, delegated permission, and consent changes tied to Agent 365 tooling | [1.7](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md), [2.25](../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md) |
| Microsoft 365 admin center Agent Tools registry and Requests | Tool status, publisher, block state, request review, approval or rejection evidence | [2.25](../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md), [3.13](../controls/pillar-3-reporting/3.13-agent-365-admin-center-analytics.md) |
| Defender Advanced Hunting | MCP server invocation monitoring and anomaly investigation | [3.14](../controls/pillar-3-reporting/3.14-agent-365-observability-sdk.md) |
| Dataverse solution and security records | Business-skill owner, sharing, and deployment evidence | [2.17](../controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md), [2.25](../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md) |

## Mappings to existing controls in this framework

| Work IQ governance surface | Primary framework mapping | Governance expectation |
|----------------------------|---------------------------|------------------------|
| Work IQ MCP tool catalog | [2.17 — Multi-Agent Orchestration Limits](../controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md) | Approve and inventory MCP servers and tools before agent use; classify high-impact tool actions. |
| Agent Tools registry, Requests, allow/block status, and Entra consent | [2.25 — Agent 365 Admin Center Governance Console](../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md) | Use the admin center as the system of record for tool approval, block state, and admin-consent evidence where the tenant supports the feature. |
| Admin-center tool metrics and inventory exports | [3.13 — Agent 365 Admin Center Analytics](../controls/pillar-3-reporting/3.13-agent-365-admin-center-analytics.md) | Include Work IQ MCP tools and business-skill-enabled agents in periodic analytics review and exception reporting. |
| Tool-call, inference, and custom-agent telemetry | [3.14 — Agent 365 Observability SDK](../controls/pillar-3-reporting/3.14-agent-365-observability-sdk.md) | Confirm Work IQ-related tool invocations are visible through Purview, Defender, or SDK telemetry before production reliance. |
| Purview audit retention and search | [1.7 — Comprehensive Audit Logging](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) | Retain Work IQ tool-call, agent-invocation, application-consent, and downstream workload evidence consistent with firm records-retention requirements. |

## Practical review questions

Use these questions during AI governance committee or technology-risk review:

1. Which Work IQ MCP tools are available, blocked, or pending in the Microsoft 365 admin center Agent Tools registry?
2. Which agents can invoke each Work IQ MCP tool, and which users or service principals provided consent?
3. Which business skills are shared across agents, who owns them, and when were they last reviewed?
4. Which Work IQ tool calls are visible in Purview audit, Defender Advanced Hunting, or SDK telemetry?
5. Does the tenant operate in commercial, GCC, GCC High, DoD, or another sovereign environment, and has feature availability been verified for that environment?
6. Are high-impact Work IQ tool actions tied to change tickets, supervisory review, or human approval checkpoints?

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
