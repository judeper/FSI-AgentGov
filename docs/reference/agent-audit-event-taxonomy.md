# Agent Audit Event Taxonomy Reference

!!! warning "Published Operations vs. Conceptual Categories"
    This taxonomy separates **published, searchable audit operations** ([Section 1](#published-searchable-audit-operations)) from **conceptual governance categories** ([Section 2](#conceptual-governance-categories-no-dedicated-microsoft-audit-operation)) that have no dedicated Microsoft audit operation as of June 2026. Build production KQL / `Search-UnifiedAuditLog` queries **only** from operations listed in Section 1. Each operation in Section 1 is cited to a specific Microsoft Learn page. See [Purview Audit Log Activities](https://learn.microsoft.com/en-us/purview/audit-log-activities) for the full catalog.

**Last Updated:** June 2026
**Version:** v1.6.2

---

## Overview

This reference provides a consolidated taxonomy of audit events relevant to Microsoft 365 AI agent governance, including Copilot Studio custom agents, Microsoft 365 built-in agents, and Agent 365 Blueprint-registered agents. It is organized into two sections:

1. **Published & Searchable Operations** — real Operation values you can use in KQL and `Search-UnifiedAuditLog`.
2. **Conceptual Governance Categories** — governance-driven categories from this framework that map to real operations but are not themselves searchable values.

!!! note "Preview Features"
    Agent 365 SDK events and the Entra Agent ID `agentType` property extensions are evolving features. Event schemas may change as these capabilities move toward general availability. The Entra Agent ID audit properties require the `Prefer: include-unknown-enum-members` request header for evolvable enum values.

---

## Published & Searchable Audit Operations

All operations below are documented in Microsoft Learn as of June 2026. Use these exact strings in KQL `Operation` or `-Operations` filters.

### Purview UAL — Agent 365 Activities

Source: [Purview Audit Log Activities — Agent 365 activities](https://learn.microsoft.com/en-us/purview/audit-log-activities)

| Operation | Friendly Name | Description | RecordType | Status |
|-----------|---------------|-------------|------------|--------|
| `AIExecuteTool` | Executed AI tool | Agent executed a tool call | `CopilotInteraction`¹ | GA |
| `AIInvokeAgent` | Invoked AI agent | AI agent invoked by a user, agent, or event | `CopilotInteraction`¹ | GA |
| `AIInferenceCall` | Made AI inference call | AI agent leveraged an AI model to produce an answer or determine next steps | `CopilotInteraction`¹ | GA |

¹ RecordType not explicitly stated for Agent 365 ops; likely shares `CopilotInteraction`. See [Supported services](https://learn.microsoft.com/en-us/purview/audit-supported-services).

### Purview UAL — M365 Admin Center Agent Management Activities

Source: [Purview Audit Log Activities — M365 Admin Center Agent Management](https://learn.microsoft.com/en-us/purview/audit-log-activities)

| Operation | Friendly Name | Description | Status |
|-----------|---------------|-------------|--------|
| `BlockedAgent` | Blocked Agent | Admin blocked an agent; users cannot use it | GA |
| `DeletedAgent` | Deleted Agent | Admin deleted a shared agent and its underlying files | GA |
| `DeployedAgent` | Deployed Agent | Admin deployed an agent for specific users/groups/org | GA |
| `RemovedAgent` | Removed Agent | Admin removed a previously installed agent | GA |
| `UnblockedAgent` | Unblocked Agent | Admin unblocked a previously blocked agent | GA |
| `UpdatedAgent` | Updated Agent | Admin updated a custom agent by uploading latest manifest | GA |
| `UpdatedTenantSettings` | Updated Tenant-level Agent Settings | Admin updated tenant-level settings that apply to agents | GA |

### Purview UAL — Microsoft 365 Copilot Admin Activities

Source: [Purview Audit Log Activities — M365 Copilot admin activities](https://learn.microsoft.com/en-us/purview/audit-log-activities) | [Copilot audit details](https://learn.microsoft.com/en-us/purview/audit-copilot)

| Operation | Friendly Name | Description | RecordType | Status |
|-----------|---------------|-------------|------------|--------|
| `CopilotInteraction` | Interacted with Copilot | User entered prompts in Copilot (M365 Copilot, Security Copilot, or Copilot Studio agent) | `CopilotInteraction` | GA |
| `CreatePlugin` | Created a new Copilot plugin | User created a new Copilot plugin | `CopilotInteraction` | GA |
| `DeletePlugin` | Deleted a Copilot plugin | User deleted a Copilot plugin | `CopilotInteraction` | GA |
| `DisableCopilotPlugin` | Disabled a Copilot plugin | User disabled a Copilot plugin | `CopilotInteraction` | GA |
| `EnablePlugin` | Enabled a Copilot plugin | User enabled a Copilot plugin | `CopilotInteraction` | GA |
| `UpdatePlugin` | Updated a Copilot plugin setting | User updated a Copilot plugin setting | `CopilotInteraction` | GA |
| `AIEnterpriseInteractionsExported` | Exported AI Interactions | Admin exported interactions with Copilot | `CopilotInteraction` | GA |
| `AIInteractionCreatedNotification` | Change notification — AI interaction created | Notification for new Copilot AI interaction | `CopilotInteraction` | GA |
| `AIInteractionDeletedNotification` | Change notification — AI interaction deleted | Notification for deleted Copilot AI interaction | `CopilotInteraction` | GA |
| `AIInteractionUpdatedNotification` | Change notification — AI interaction updated | Notification for updated Copilot AI interaction | `CopilotInteraction` | GA |
| `SubscribedToAIInteractions` | Subscribed to AI interactions | Subscription created for Copilot AI interaction notifications | `CopilotInteraction` | GA |

### Power Platform / Copilot Studio — Agent Authoring Events

Source: [Copilot Studio audit logging](https://learn.microsoft.com/en-us/microsoft-copilot-studio/admin-logging-copilot-studio) | [Power Platform activity logging](https://learn.microsoft.com/en-us/power-platform/admin/logging-powerapps)

RecordType: `PowerPlatformAdministratorActivity`

| Operation | Category | Description | Status |
|-----------|----------|-------------|--------|
| `BotCreate` | Agents | Creation of a new agent | GA |
| `BotDelete` | Agents | Deletion of an agent | GA |
| `BotDeleteCleanup` | Agents | Cleanup of dependencies after agent deletion | GA |
| `BotUpdateOperation-BotNameUpdate` | Agents | Updating agent name | GA |
| `BotUpdateOperation-BotAuthUpdate` | Agents | Updating authentication settings | GA |
| `BotUpdateOperation-BotIconUpdate` | Agents | Updating agent icon | GA |
| `BotUpdateOperation-BotPublish` | Agents | Publishing an agent | GA |
| `BotUpdateOperation-BotShare` | Agents | Sharing an agent to other users | GA |
| `BotAppInsightsUpdate` | Agents | Updating App Insights logging configuration | GA |
| `BotComponentCreate` | Agent Component | Creation of a component (topic, skill) | GA |
| `BotComponentUpdate` | Agent Component | Update of a component | GA |
| `BotComponentDelete` | Agent Component | Deletion of a component | GA |
| `BotComponentCollectionCreate` | Agent Component Collection | Creation of a component collection | GA |
| `BotComponentCollectionDelete` | Agent Component Collection | Deletion of a component collection | GA |
| `BotComponentCollectionUpdate` | Agent Component Collection | Update of a component collection | GA |
| `AIPluginOperationCreate` | AI Plugin | Creating an AI Plugin | GA |
| `AIPluginOperationUpdate` | AI Plugin | Updating an AI Plugin | GA |
| `AIPluginOperationDelete` | AI Plugin | Removing an AI Plugin | GA |
| `EnvironmentVariableCreate` | Environment Variable | Creating an environment variable | GA |
| `EnvironmentVariableUpdate` | Environment Variable | Updating an environment variable | GA |
| `EnvironmentVariableDelete` | Environment Variable | Deleting an environment variable | GA |

### Power Platform / Copilot Studio — Agent Usage Events

Source: [Copilot Studio audit logging — agent usage](https://learn.microsoft.com/en-us/microsoft-copilot-studio/admin-logging-copilot-studio) (§ "See audited events (agent usage)")

The Copilot Studio admin-logging page documents a separate **"agent usage"** audit table distinct from the authoring events above. This captures end-user interactions with Copilot Studio-built agents.

| Operation | Category | RecordType | Description | Governance Use | Status |
|-----------|----------|------------|-------------|----------------|--------|
| `CopilotInteraction` | Users | `CopilotInteraction` | End-user interaction with a Copilot Studio-built agent | Supervision of CS-built agents (FINRA 3110); distinguish from M365 Copilot interactions via `AppHost` value identifying Copilot Studio origin | GA |

!!! tip "Distinguishing Copilot Studio Agent Usage from M365 Copilot"
    Both Copilot Studio agent usage and M365 Copilot prompt interactions emit `CopilotInteraction` as the Operation and RecordType. The `AppHost` property in the audit record differentiates the source — Copilot Studio-built agents report a distinct `AppHost` value. Filter on `AppHost` to isolate supervision evidence for custom agents built in Copilot Studio.

### Microsoft Entra — Agent Identity Audit Events

Source: [Microsoft Entra Agent ID logs](https://learn.microsoft.com/en-us/entra/agent-id/sign-in-audit-logs-agents)

!!! info "No Dedicated Agent Operations"
    Microsoft Entra does **not** define new agent-specific Operation names. Agent identity activities are captured by existing Entra audit operations, differentiated by the `agentType` property on `initiatedBy`, `performedBy`, and `targetResources` fields.

| Existing Entra Operation | Agent Action | `agentType` Value | Audit Category |
|--------------------------|--------------|-------------------|----------------|
| `Add application` | Create agent identity blueprint | `agenticApp` | ApplicationManagement |
| `Add service principal` | Create agent identity instance | `agenticAppInstance` | ApplicationManagement |
| `Add user` | Create agent's user account | `agentIDuser` | UserManagement |
| `Update application` | Update agent identity blueprint | `agenticApp` | ApplicationManagement |
| `Update service principal` | Update agent identity instance | `agenticAppInstance` | ApplicationManagement |
| `Delete application` | Delete agent identity blueprint | `agenticApp` | ApplicationManagement |
| `Delete service principal` | Delete agent identity instance | `agenticAppInstance` | ApplicationManagement |

**`agentType` enum values:** `notAgentic`, `agenticApp`, `agenticAppInstance`, `agentIdentityBlueprintPrincipal`, `agentIDuser`, `unknownFutureValue`

### DLP / Defender — Coverage Model

Source: [Purview Audit Log Activities](https://learn.microsoft.com/en-us/purview/audit-log-activities) | [Copilot audit details](https://learn.microsoft.com/en-us/purview/audit-copilot)

!!! info "No Agent-Specific DLP/Defender Operations"
    Microsoft publishes no agent-specific DLP or Defender operations. Agent content policy enforcement appears as metadata within `CopilotInteraction` records (the `AccessedResources.PolicyDetails` field captures PolicyId, PolicyName, rules, and block status). Standard DLP RecordTypes apply to agent-generated content.

| RecordType | Scope | Description |
|------------|-------|-------------|
| `ComplianceDLPSharePoint` | DLP | DLP rule matches on SharePoint/OneDrive content (including agent-generated) |
| `ComplianceDLPExchange` | DLP | DLP rule matches on Exchange content |
| `DlpSensitiveInformationType` | DLP | Sensitive information type detection events |
| `MIPLabel` | Labels | Sensitivity label applied/changed/removed (ops: `SensitivityLabelApplied`, `FileSensitivityLabelApplied`, `SensitivityLabelUpdated`, `SensitivityLabelRemoved`) |

---

## Conceptual Governance Categories (No Dedicated Microsoft Audit Operation)

The governance categories below were originally presented as searchable operations in this file. **They are NOT valid UAL Operation or RecordType values.** They remain useful as governance planning categories; the table maps each to real adjacent events that provide equivalent evidence.

### Identity Lifecycle (Conceptual)

| Governance Category | Purpose | How to Actually Obtain This Evidence |
|---------------------|---------|--------------------------------------|
| Agent identity created | Track new agent identities | Entra: `Add application` or `Add service principal` filtered by `agentType` ∈ {`agenticApp`, `agenticAppInstance`} |
| Agent identity modified | Track identity property changes | Entra: `Update application` / `Update service principal` with `agentType` filter |
| Agent identity deleted | Track identity removal | Entra: `Delete application` / `Delete service principal` with `agentType` filter |
| Sponsor assigned/removed | Track human sponsor accountability | No dedicated audit event. Implement via custom logging in your governance process or monitor Entra group membership changes for sponsor-linked groups |
| Agent collection changed | Track agent regrouping | No dedicated audit event. Monitor Entra group membership audit logs for collection-group changes |

### Blueprint Lifecycle (Conceptual)

| Governance Category | Purpose | How to Actually Obtain This Evidence |
|---------------------|---------|--------------------------------------|
| Blueprint registration | Track new agent blueprints | Entra: `Add application` with `agentType = agenticApp` |
| Blueprint promotion/demotion | Track lifecycle phase transitions | No dedicated audit event. Implement promotion/demotion tracking via your change management system (e.g., ServiceNow, Azure DevOps); deploy events map to Admin Center `DeployedAgent` |
| Blueprint validation | Track validation completeness | No dedicated audit event. Capture in your CI/CD pipeline or governance tooling |
| Blueprint deployment | Track environment deployments | Admin Center: `DeployedAgent` (different scope — admin-managed agents) |

### Security (Conceptual)

| Governance Category | Purpose | How to Actually Obtain This Evidence |
|---------------------|---------|--------------------------------------|
| Agent sign-in | Track agent authentication | Entra sign-in logs (separate from UAL): event type `agentSignIn`; Graph filter: `signInEventTypes/any(t: t eq 'servicePrincipal') and agent/agentType eq 'AgentIdentity'`. Source: [Entra Agent ID sign-in logs](https://learn.microsoft.com/en-us/entra/agent-id/sign-in-audit-logs-agents) (§ "Sign-in logs") |
| CA policy applied/denied | Track Conditional Access evaluation for agents | Entra sign-in logs: `conditionalAccessStatus` and `appliedConditionalAccessPolicies` fields on service principal sign-ins |
| DLP policy triggered (agent-specific) | Track policy enforcement on agent content | `CopilotInteraction` record → `AccessedResources.PolicyDetails` field; or standard `ComplianceDLPSharePoint` / `ComplianceDLPExchange` events for content created by agents |
| Unauthorized publish | Track blocked publish attempts | Copilot Studio: failed `BotUpdateOperation-BotPublish` events (check operation outcome/status); Admin Center: no equivalent |

---

## Event-to-Control Mapping

| Evidence Domain | Primary Controls | Evidence Purpose |
|-----------------|------------------|------------------|
| Entra Agent Identity (via `agentType` filter) | 1.2, 1.11, 3.6 | Agent registry, access governance, orphan detection |
| Admin Center Agent Mgmt + Copilot Studio authoring | 2.1, 2.3, 3.1 | Managed environments, change management, inventory |
| CopilotInteraction + Agent 365 ops | 1.7, 1.10, 2.12 | Audit logging, compliance monitoring, supervision |
| Copilot Studio authoring (`Bot*`, `AIPlugin*`) | 2.3, 2.5, 2.13 | Change management, testing, configuration tracking |
| DLP RecordTypes + CopilotInteraction PolicyDetails | 1.5, 1.7, 1.11 | DLP, audit logging, conditional access |

---

## KQL Query Pack

### Query 1: Agent 365 Tool Execution Tracking

Track Agent 365 tool executions for change management and supervision evidence.

```kql
// Agent 365 Tool Execution Audit Trail
OfficeActivity
| where TimeGenerated > ago(30d)
| where Operation in ("AIExecuteTool", "AIInvokeAgent", "AIInferenceCall")
| extend
    agentId = tostring(parse_json(AuditData).AgentId),
    toolName = tostring(parse_json(AuditData).ToolName),
    userId = UserId
| project
    TimeGenerated,
    Operation,
    agentId,
    toolName,
    userId
| order by TimeGenerated desc
```

### Query 2: Copilot Studio Agent Configuration Changes

Monitor agent creation, deletion, publishing, and component changes.

```kql
// Copilot Studio Configuration Audit
OfficeActivity
| where TimeGenerated > ago(7d)
| where Operation in (
    "BotCreate", "BotDelete", "BotUpdateOperation-BotPublish",
    "BotUpdateOperation-BotShare", "BotUpdateOperation-BotAuthUpdate",
    "BotComponentCreate", "BotComponentUpdate", "BotComponentDelete"
)
| extend
    botId = tostring(parse_json(AuditData).BotId),
    environmentId = tostring(parse_json(AuditData).EnvironmentId)
| project
    TimeGenerated,
    Operation,
    botId,
    environmentId,
    InitiatedBy = UserId
| order by TimeGenerated desc
```

### Query 3: CopilotInteraction Audit for FINRA 3110/4511

Capture Copilot interactions with prompt/response tracking for regulatory record-keeping.

```kql
// FINRA 3110/4511 Copilot Interaction Audit
OfficeActivity
| where TimeGenerated > ago(24h)
| where RecordType == "CopilotInteraction"
| where Operation == "CopilotInteraction"
| extend
    userId = UserId,
    appHost = tostring(parse_json(AuditData).AppHost),
    conversationId = tostring(parse_json(AuditData).ConversationId),
    accessedResources = parse_json(AuditData).AccessedResources
| mv-expand AccessedResources = accessedResources
| extend
    policyDetails = AccessedResources.PolicyDetails
| summarize
    ResourceCount = dcount(tostring(AccessedResources)),
    PolicyBlocked = countif(isnotempty(policyDetails))
    by TimeGenerated, userId, appHost, conversationId
| order by TimeGenerated desc
```

### Query 4: Admin Center Agent Deployment and Blocking

Track admin-level agent management actions (deployments, blocks, removals).

```kql
// Admin Center Agent Management Audit
OfficeActivity
| where TimeGenerated > ago(30d)
| where Operation in ("DeployedAgent", "BlockedAgent", "UnblockedAgent", "RemovedAgent", "DeletedAgent", "UpdatedAgent")
| project
    TimeGenerated,
    Operation,
    UserId,
    AgentName = tostring(parse_json(AuditData).AgentName),
    TargetScope = tostring(parse_json(AuditData).TargetScope)
| order by TimeGenerated desc
```

### Query 5: DLP Policy Matches on Agent-Adjacent Content

Track DLP rule matches that may involve agent-generated content.

```kql
// DLP Policy Matches (filter for agent-related where possible)
OfficeActivity
| where TimeGenerated > ago(7d)
| where RecordType in ("ComplianceDLPSharePoint", "ComplianceDLPExchange")
| extend
    policyName = tostring(parse_json(AuditData).PolicyName),
    ruleName = tostring(parse_json(AuditData).RuleName),
    action = tostring(parse_json(AuditData).Actions),
    sensitiveInfoTypes = parse_json(AuditData).SensitiveInfoTypeData
| summarize
    MatchCount = count(),
    Policies = make_set(policyName)
    by ruleName, action, bin(TimeGenerated, 1d)
| order by MatchCount desc
```

---

## UAL Search Equivalents

For environments without Microsoft Sentinel, use the Unified Audit Log via PowerShell.

!!! warning "Pagination"
    `Search-UnifiedAuditLog` returns a maximum of 5,000 records per call.
    Use `-SessionId` and `-SessionCommand ReturnLargeSet` for pagination in
    high-volume environments. See [Microsoft documentation](https://learn.microsoft.com/en-us/powershell/module/exchange/search-unifiedauditlog).

### PowerShell: Agent 365 Operations

```powershell
# Search for Agent 365 tool execution events
$startDate = (Get-Date).AddDays(-7)
$endDate = Get-Date

$results = Search-UnifiedAuditLog `
    -StartDate $startDate `
    -EndDate $endDate `
    -Operations "AIExecuteTool", "AIInvokeAgent", "AIInferenceCall" `
    -ResultSize 5000

$results | ForEach-Object {
    $auditData = $_.AuditData | ConvertFrom-Json
    [PSCustomObject]@{
        Timestamp  = $_.CreationDate
        Operation  = $_.Operations
        AgentId    = $auditData.AgentId
        ToolName   = $auditData.ToolName
        UserId     = $_.UserIds
    }
} | Export-Csv -Path "Agent365Audit.csv" -NoTypeInformation
```

### PowerShell: Copilot Interactions (FINRA 3110/4511)

```powershell
# Search for Copilot interactions (regulatory record-keeping evidence)
$results = Search-UnifiedAuditLog `
    -StartDate $startDate `
    -EndDate $endDate `
    -RecordType CopilotInteraction `
    -Operations "CopilotInteraction" `
    -ResultSize 5000

$results | ForEach-Object {
    $auditData = $_.AuditData | ConvertFrom-Json
    [PSCustomObject]@{
        Timestamp      = $_.CreationDate
        UserId         = $_.UserIds
        AppHost        = $auditData.AppHost
        ConversationId = $auditData.ConversationId
        ResourceCount  = ($auditData.AccessedResources | Measure-Object).Count
    }
} | Export-Csv -Path "CopilotInteractionAudit.csv" -NoTypeInformation
```

### PowerShell: Copilot Studio Configuration Changes

```powershell
# Search for Copilot Studio agent authoring events
$results = Search-UnifiedAuditLog `
    -StartDate $startDate `
    -EndDate $endDate `
    -Operations "BotCreate", "BotDelete", "BotUpdateOperation-BotPublish", "BotUpdateOperation-BotShare", "BotComponentCreate", "BotComponentUpdate", "BotComponentDelete" `
    -ResultSize 5000

$results | ForEach-Object {
    $auditData = $_.AuditData | ConvertFrom-Json
    [PSCustomObject]@{
        Timestamp     = $_.CreationDate
        Operation     = $_.Operations
        BotId         = $auditData.BotId
        EnvironmentId = $auditData.EnvironmentId
        InitiatedBy   = $_.UserIds
    }
} | Export-Csv -Path "CopilotStudioAudit.csv" -NoTypeInformation
```

---

## Alert Severity by Zone (Recommended)

The thresholds below reference real operations and evidence sources. Implement alerts using the actual operations from Section 1 or the adjacent evidence paths from Section 2.

| Evidence Source | Alert Trigger | Zone 1 | Zone 2 | Zone 3 |
|----------------|---------------|--------|--------|--------|
| Entra: `Add service principal` (agentType filter) | New agent identity created | Info | Low | Medium |
| Entra: `Delete service principal` (agentType filter) | Agent identity deleted | Info | Medium | High |
| Admin Center: `DeployedAgent` | Agent deployed to production | Info | Medium | High |
| Admin Center: `BlockedAgent` | Agent blocked by admin | Low | Medium | High |
| `CopilotInteraction` → PolicyDetails blocked | DLP policy blocked agent access | Low | Medium | Critical |
| Copilot Studio: `BotUpdateOperation-BotPublish` | Agent published (potential unauthorized) | Low | Medium | High |
| Entra sign-in logs: SP sign-in failure | Agent access denied | Low | Medium | High |

---

## Retention Requirements

| Evidence Domain | Zone 1 | Zone 2 | Zone 3 | Regulatory Driver |
|-----------------|--------|--------|--------|-------------------|
| Agent Identity (Entra audit) | 180 days | 1 year | 7–10 years | FINRA 4511, SEC 17a-4 |
| Agent Configuration (Copilot Studio + Admin Center) | 180 days | 1 year | 7–10 years | SOX 404, SEC 17a-4 |
| CopilotInteraction records | 180 days | 1 year | 7–10 years | FINRA 4511, SEC 17a-3 |
| DLP / Sensitivity Labels | 180 days | 1 year | 7–10 years | GLBA 501(b) |
| Entra Sign-in Logs (agent SPs) | 180 days | 1 year | 7–10 years | GLBA 501(b) |

---

## Related Resources

- [Control 1.7 — Comprehensive Audit Logging](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md)
- [Control 3.9 — Microsoft Sentinel Integration](../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md)
- [Purview Audit Query Pack](../playbooks/monitoring-and-validation/purview-audit-query-pack.md)
- [Microsoft Learn: Audit Log Activities](https://learn.microsoft.com/en-us/purview/audit-log-activities)
- [Microsoft Learn: Copilot Studio Audit Logging](https://learn.microsoft.com/en-us/microsoft-copilot-studio/admin-logging-copilot-studio)
- [Microsoft Learn: Entra Agent ID Logs](https://learn.microsoft.com/en-us/entra/agent-id/sign-in-audit-logs-agents)
- [Microsoft Learn: Copilot Audit Details](https://learn.microsoft.com/en-us/purview/audit-copilot)
- [Microsoft Learn: Agent 365 SDK (Preview)](https://learn.microsoft.com/en-us/microsoft-agent-365/developer/)

---

*FSI Agent Governance Framework v1.6.2 — June 2026*
