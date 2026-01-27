# Agent Audit Event Taxonomy Reference

**Last Updated:** January 2026
**Version:** v1.2.6

---

## Overview

This reference provides a consolidated taxonomy of audit events for Microsoft 365 AI agents, including Copilot Studio custom agents, Microsoft 365 built-in agents (Researcher, Analyst, Facilitator), and Agent 365 Blueprint-registered agents.

!!! note "Preview Features"
    Agent 365 SDK events and Agentic User events are preview features. Event schemas may change as features evolve toward general availability.

---

## Event Categories

| Category | Description | Primary Use Case |
|----------|-------------|------------------|
| **Identity Lifecycle** | Agent identity creation, modification, deletion | Regulatory audit trail, access governance |
| **Blueprint Lifecycle** | Blueprint registration, promotion, demotion | Change management evidence |
| **Agent Interaction** | User-agent conversations, tool invocations | FINRA 25-07 compliance, supervision |
| **Configuration** | Settings changes, permission updates | SOX 404 controls, change tracking |
| **Security** | Authentication events, policy applications | Security investigations, CA monitoring |

---

## Consolidated Event Table

### Identity Lifecycle Events

| Event Name | RecordType | Category | Description | Key Fields |
|------------|------------|----------|-------------|------------|
| `AgentIdentityCreated` | AgentInteraction | Identity | New Agentic User created in Entra ID | UserId, AgentId, SponsorId, AgentType, Zone |
| `AgentIdentityModified` | AgentInteraction | Identity | Agent identity properties changed | AgentId, ModifiedProperties, ModifiedBy |
| `AgentIdentityDeleted` | AgentInteraction | Identity | Agent identity removed from Entra | AgentId, DeletedBy, RetentionStatus |
| `AgentSponsorAssigned` | AgentInteraction | Identity | Human sponsor assigned to agent | AgentId, SponsorId, PreviousSponsorId |
| `AgentSponsorRemoved` | AgentInteraction | Identity | Sponsor removed without replacement | AgentId, RemovedSponsorId, SuspensionStatus |
| `AgentCollectionChanged` | AgentInteraction | Identity | Agent moved between collections | AgentId, SourceCollection, TargetCollection |

### Blueprint Lifecycle Events (Preview)

| Event Name | RecordType | Category | Description | Key Fields |
|------------|------------|----------|-------------|------------|
| `BlueprintRegistration` | AgentInteraction | Blueprint | Agent registered via Blueprint | BlueprintId, AgentId, RegistrationType, Manifest |
| `BlueprintPromotion` | AgentInteraction | Blueprint | Agent promoted to next phase | BlueprintId, SourcePhase, TargetPhase, ApprovalChain |
| `BlueprintDemotion` | AgentInteraction | Blueprint | Agent rolled back to previous phase | BlueprintId, SourcePhase, TargetPhase, Reason |
| `BlueprintValidation` | AgentInteraction | Blueprint | Blueprint validation completed | BlueprintId, ValidationResult, Issues |
| `BlueprintDeployment` | AgentInteraction | Blueprint | Agent deployed to target environment | BlueprintId, TargetEnvironment, DeploymentId |

### Agent Interaction Events

| Event Name | RecordType | Category | Description | Key Fields |
|------------|------------|----------|-------------|------------|
| `CopilotInteraction` | CopilotInteraction | Interaction | M365 Copilot conversation | UserId, ApplicationId, PromptHash, ResponseStatus |
| `CopilotForM365Interaction` | CopilotForM365Interaction | Interaction | Copilot for Microsoft 365 event | UserId, AppContext, DataSources, CitationCount |
| `AgentInteraction` | AgentInteraction | Interaction | Copilot Studio agent conversation | UserId, AgentId, ConversationId, MessageCount |
| `AgentToolInvocation` | AgentInteraction | Interaction | Agent invoked external tool/connector | AgentId, ToolName, ConnectorId, InvocationResult |
| `AgentKnowledgeAccess` | AgentInteraction | Interaction | Agent accessed knowledge source | AgentId, DataSourceId, QueryType, ResultCount |
| `AIAssistanceUsed` | AIAssistanceUsed | Interaction | AI assistance in document creation | UserId, DocumentId, AssistanceType, AcceptedSuggestions |

### Configuration Events

| Event Name | RecordType | Category | Description | Key Fields |
|------------|------------|----------|-------------|------------|
| `CopilotAgentCreated` | PowerAppsActivity | Configuration | New Copilot Studio agent created | CreatorId, AgentId, EnvironmentId, AgentType |
| `CopilotAgentPublished` | PowerAppsActivity | Configuration | Agent published to channel | AgentId, PublisherId, Channel, Visibility |
| `CopilotAgentModified` | PowerAppsActivity | Configuration | Agent configuration changed | AgentId, ModifiedBy, ChangeType, PreviousValue |
| `CopilotAgentDeleted` | PowerAppsActivity | Configuration | Agent removed from environment | AgentId, DeletedBy, DeletionType |
| `ConnectorAdded` | PowerAppsActivity | Configuration | Connector added to agent | AgentId, ConnectorId, ConnectorType, Permissions |
| `ConnectorRemoved` | PowerAppsActivity | Configuration | Connector removed from agent | AgentId, ConnectorId, RemovedBy |
| `TopicCreated` | PowerAppsActivity | Configuration | New topic added to agent | AgentId, TopicId, TopicType, TriggerPhrases |
| `TopicModified` | PowerAppsActivity | Configuration | Topic configuration changed | AgentId, TopicId, ChangeType |
| `ObservabilityConfigured` | AgentInteraction | Configuration | Observability SDK settings changed | AgentId, TelemetrySettings, ExporterConfig |

### Security Events

| Event Name | RecordType | Category | Description | Key Fields |
|------------|------------|----------|-------------|------------|
| `AgentSignIn` | SigninLogs | Security | Agent identity authenticated | AgentId, AuthenticationMethod, IPAddress, Location |
| `AgentCAPolicyApplied` | SigninLogs | Security | Conditional Access policy evaluated | AgentId, PolicyId, PolicyResult, GrantControls |
| `AgentAccessDenied` | SigninLogs | Security | Agent access blocked by policy | AgentId, DeniedReason, PolicyId, Resource |
| `DLPPolicyTriggered` | DlpRuleMatch | Security | DLP policy matched agent content | AgentId, PolicyId, ContentLocation, Action |
| `SensitivityLabelApplied` | MIPLabel | Security | Sensitivity label applied by agent | AgentId, LabelId, DocumentId, LabelSource |

---

## Event-to-Control Mapping

| Event Category | Primary Controls | Evidence Purpose |
|----------------|------------------|------------------|
| Identity Lifecycle | 1.2, 1.11, 3.6 | Agent registry, access governance, orphan detection |
| Blueprint Lifecycle | 2.3, 2.5, 2.13 | Change management, testing, documentation |
| Agent Interaction | 1.7, 1.10, 2.12 | Audit logging, compliance monitoring, supervision |
| Configuration | 2.1, 2.3, 3.1 | Managed environments, change management, inventory |
| Security | 1.5, 1.7, 1.11 | DLP, audit logging, conditional access |

---

## Key Field Schemas

### Common Fields (All Events)

| Field | Type | Description |
|-------|------|-------------|
| `TimeGenerated` | datetime | Event timestamp (UTC) |
| `OperationName` | string | Event operation name |
| `UserId` | string | Acting user ID (human initiator) |
| `UserPrincipalName` | string | Acting user UPN |
| `CorrelationId` | guid | Request correlation ID |
| `TenantId` | guid | Tenant identifier |
| `RecordType` | string | Audit record type |
| `Workload` | string | Source workload (PowerApps, Copilot, etc.) |

### Agent-Specific Fields

| Field | Type | Description |
|-------|------|-------------|
| `AgentId` | guid | Unique agent identifier |
| `AgentName` | string | Display name of agent |
| `AgentType` | string | Agent type (CustomCopilot, M365Agent, Blueprint) |
| `EnvironmentId` | guid | Power Platform environment ID |
| `Zone` | string | Governance zone (Zone1, Zone2, Zone3) |
| `SponsorId` | guid | Human sponsor Entra ID |

### Blueprint-Specific Fields (Preview)

| Field | Type | Description |
|-------|------|-------------|
| `BlueprintId` | guid | Blueprint registration ID |
| `BlueprintPhase` | string | Current phase (Design, Build, Deploy) |
| `ManifestVersion` | string | Blueprint manifest version |
| `ApprovalChain` | array | Approval records with timestamps |

### Interaction-Specific Fields

| Field | Type | Description |
|-------|------|-------------|
| `ConversationId` | guid | Conversation session ID |
| `MessageId` | guid | Individual message ID |
| `PromptHash` | string | SHA-256 hash of user prompt |
| `ResponseStatus` | string | Success, Filtered, Error |
| `ToolCalls` | array | Tools invoked during interaction |
| `DataSources` | array | Knowledge sources accessed |
| `CitationCount` | int | Number of citations in response |

---

## Alert Severity by Zone

### Recommended Alert Thresholds

| Event | Zone 1 | Zone 2 | Zone 3 |
|-------|--------|--------|--------|
| `AgentIdentityCreated` | Info | Low | Medium |
| `AgentIdentityDeleted` | Info | Medium | High |
| `BlueprintPromotion` | N/A | Medium | High |
| `BlueprintDemotion` | N/A | Medium | Critical |
| `AgentAccessDenied` | Low | Medium | High |
| `DLPPolicyTriggered` | Low | Medium | Critical |
| `AgentSponsorRemoved` | Info | High | Critical |
| `UnauthorizedPublish` | Medium | High | Critical |

### Alert Definitions

```kql
// Critical: Zone 3 Blueprint Demotion
OfficeActivity
| where TimeGenerated > ago(1h)
| where Operation == "BlueprintDemotion"
| extend zone = tostring(parse_json(AuditData).Zone)
| where zone == "Zone3"
| project TimeGenerated, AgentId = parse_json(AuditData).AgentId, Reason = parse_json(AuditData).Reason
```

```kql
// High: Sponsor Removed Without Replacement
OfficeActivity
| where TimeGenerated > ago(24h)
| where Operation == "AgentSponsorRemoved"
| extend
    agentId = tostring(parse_json(AuditData).AgentId),
    zone = tostring(parse_json(AuditData).Zone)
| where zone in ("Zone2", "Zone3")
| project TimeGenerated, agentId, zone, RemovedSponsor = parse_json(AuditData).RemovedSponsorId
```

---

## KQL Query Pack

### Query 1: Blueprint Promotion Tracking

Track all Blueprint promotions with approval chain for change management evidence.

```kql
// Blueprint Promotion Audit Trail
OfficeActivity
| where TimeGenerated > ago(30d)
| where Operation in ("BlueprintPromotion", "BlueprintDemotion", "BlueprintRegistration")
| extend
    blueprintId = tostring(parse_json(AuditData).BlueprintId),
    agentId = tostring(parse_json(AuditData).AgentId),
    sourcePhase = tostring(parse_json(AuditData).SourcePhase),
    targetPhase = tostring(parse_json(AuditData).TargetPhase),
    approvalChain = parse_json(AuditData).ApprovalChain,
    zone = tostring(parse_json(AuditData).Zone)
| project
    TimeGenerated,
    Operation,
    blueprintId,
    agentId,
    Transition = strcat(sourcePhase, " → ", targetPhase),
    zone,
    ApproverCount = array_length(approvalChain),
    InitiatedBy = UserId
| order by TimeGenerated desc
```

### Query 2: Agent Identity Lifecycle Events

Monitor agent identity creation, modification, and deletion for access governance.

```kql
// Agent Identity Lifecycle Audit
OfficeActivity
| where TimeGenerated > ago(7d)
| where Operation in ("AgentIdentityCreated", "AgentIdentityModified", "AgentIdentityDeleted", "AgentSponsorAssigned", "AgentSponsorRemoved")
| extend
    agentId = tostring(parse_json(AuditData).AgentId),
    sponsorId = tostring(parse_json(AuditData).SponsorId),
    zone = tostring(parse_json(AuditData).Zone),
    agentType = tostring(parse_json(AuditData).AgentType)
| summarize
    EventCount = count(),
    LastEvent = max(TimeGenerated),
    Operations = make_set(Operation)
    by agentId, zone, agentType
| order by EventCount desc
```

### Query 3: Agent Interaction Audit for FINRA 25-07

Capture agent interactions with prompt/response tracking for regulatory compliance.

```kql
// FINRA 25-07 Agent Interaction Audit
OfficeActivity
| where TimeGenerated > ago(24h)
| where RecordType in ("CopilotInteraction", "AgentInteraction", "CopilotForM365Interaction")
| extend
    userId = UserId,
    agentId = coalesce(
        tostring(parse_json(AuditData).AgentId),
        tostring(parse_json(AuditData).ApplicationId)
    ),
    conversationId = tostring(parse_json(AuditData).ConversationId),
    promptHash = tostring(parse_json(AuditData).PromptHash),
    responseStatus = tostring(parse_json(AuditData).ResponseStatus),
    dataSources = parse_json(AuditData).DataSources,
    citationCount = toint(parse_json(AuditData).CitationCount)
| project
    TimeGenerated,
    userId,
    agentId,
    conversationId,
    promptHash,
    responseStatus,
    SourceCount = array_length(dataSources),
    citationCount
| order by TimeGenerated desc
```

### Query 4: Anomaly Detection Patterns

Identify unusual agent behavior patterns for security monitoring.

```kql
// Agent Behavior Anomaly Detection
let baseline = OfficeActivity
| where TimeGenerated between (ago(30d) .. ago(7d))
| where RecordType == "AgentInteraction"
| extend agentId = tostring(parse_json(AuditData).AgentId)
| summarize
    avgDailyInteractions = count() / 23,
    avgDataSources = avg(array_length(parse_json(AuditData).DataSources))
    by agentId;

OfficeActivity
| where TimeGenerated > ago(24h)
| where RecordType == "AgentInteraction"
| extend agentId = tostring(parse_json(AuditData).AgentId)
| summarize
    currentInteractions = count(),
    currentAvgSources = avg(array_length(parse_json(AuditData).DataSources))
    by agentId
| join kind=leftouter baseline on agentId
| extend
    interactionAnomaly = currentInteractions > (avgDailyInteractions * 3),
    sourceAnomaly = currentAvgSources > (avgDataSources * 2)
| where interactionAnomaly or sourceAnomaly
| project agentId, currentInteractions, avgDailyInteractions, interactionAnomaly, sourceAnomaly
```

### Query 5: DLP Policy Enforcement on Agent Content

Track DLP policy matches for agent-generated content.

```kql
// Agent DLP Policy Enforcement
OfficeActivity
| where TimeGenerated > ago(7d)
| where RecordType == "DlpRuleMatch"
| extend
    agentId = tostring(parse_json(AuditData).AgentId),
    policyName = tostring(parse_json(AuditData).PolicyName),
    ruleName = tostring(parse_json(AuditData).RuleName),
    action = tostring(parse_json(AuditData).Action),
    sensitiveInfoTypes = parse_json(AuditData).SensitiveInfoTypes
| where isnotempty(agentId)
| summarize
    MatchCount = count(),
    BlockCount = countif(action == "Block"),
    WarnCount = countif(action == "Warn"),
    SITTypes = make_set(sensitiveInfoTypes)
    by agentId, policyName, ruleName, bin(TimeGenerated, 1d)
| order by MatchCount desc
```

---

## UAL Search Equivalents

For environments without Microsoft Sentinel, use the Unified Audit Log search.

### PowerShell: Agent Lifecycle Events

```powershell
# Search for agent identity lifecycle events
$startDate = (Get-Date).AddDays(-7)
$endDate = Get-Date

$results = Search-UnifiedAuditLog `
    -StartDate $startDate `
    -EndDate $endDate `
    -RecordType AgentInteraction `
    -Operations "AgentIdentityCreated", "AgentIdentityModified", "AgentIdentityDeleted" `
    -ResultSize 5000

$results | ForEach-Object {
    $auditData = $_.AuditData | ConvertFrom-Json
    [PSCustomObject]@{
        Timestamp = $_.CreationDate
        Operation = $_.Operations
        AgentId = $auditData.AgentId
        SponsorId = $auditData.SponsorId
        Zone = $auditData.Zone
        PerformedBy = $_.UserIds
    }
} | Export-Csv -Path "AgentLifecycleAudit.csv" -NoTypeInformation
```

### PowerShell: Agent Interactions (FINRA 25-07)

```powershell
# Search for agent interactions (regulatory evidence)
$results = Search-UnifiedAuditLog `
    -StartDate $startDate `
    -EndDate $endDate `
    -RecordType CopilotInteraction, AgentInteraction `
    -ResultSize 5000

$results | ForEach-Object {
    $auditData = $_.AuditData | ConvertFrom-Json
    [PSCustomObject]@{
        Timestamp = $_.CreationDate
        RecordType = $_.RecordType
        UserId = $_.UserIds
        AgentId = $auditData.AgentId ?? $auditData.ApplicationId
        ConversationId = $auditData.ConversationId
        ResponseStatus = $auditData.ResponseStatus
        DataSourceCount = ($auditData.DataSources | Measure-Object).Count
    }
} | Export-Csv -Path "AgentInteractionAudit.csv" -NoTypeInformation
```

### PowerShell: Blueprint Promotions

```powershell
# Search for Blueprint lifecycle events
$results = Search-UnifiedAuditLog `
    -StartDate $startDate `
    -EndDate $endDate `
    -RecordType AgentInteraction `
    -Operations "BlueprintPromotion", "BlueprintDemotion", "BlueprintRegistration" `
    -ResultSize 5000

$results | ForEach-Object {
    $auditData = $_.AuditData | ConvertFrom-Json
    [PSCustomObject]@{
        Timestamp = $_.CreationDate
        Operation = $_.Operations
        BlueprintId = $auditData.BlueprintId
        AgentId = $auditData.AgentId
        SourcePhase = $auditData.SourcePhase
        TargetPhase = $auditData.TargetPhase
        ApproverCount = ($auditData.ApprovalChain | Measure-Object).Count
        InitiatedBy = $_.UserIds
    }
} | Export-Csv -Path "BlueprintPromotionAudit.csv" -NoTypeInformation
```

---

## Retention Requirements

| Event Category | Zone 1 | Zone 2 | Zone 3 | Regulatory Driver |
|----------------|--------|--------|--------|-------------------|
| Identity Lifecycle | 180 days | 1 year | 7-10 years | FINRA 4511, SEC 17a-4 |
| Blueprint Lifecycle | N/A | 1 year | 7-10 years | SOX 404, SEC 17a-4 |
| Agent Interaction | 180 days | 1 year | 7-10 years | FINRA 25-07, SEC 17a-3 |
| Configuration | 180 days | 1 year | 7-10 years | SOX 404 |
| Security | 180 days | 1 year | 7-10 years | GLBA 501(b) |

---

## Related Resources

- [Control 1.7 - Comprehensive Audit Logging](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md)
- [Control 3.9 - Microsoft Sentinel Integration](../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md)
- [Purview Audit Query Pack](../playbooks/monitoring-and-validation/purview-audit-query-pack.md)
- [Microsoft Learn: Audit Log Activities](https://learn.microsoft.com/en-us/purview/audit-log-activities)
- [Microsoft Learn: Agent 365 SDK (Preview)](https://learn.microsoft.com/en-us/microsoft-agent-365/developer/)

---

*FSI Agent Governance Framework v1.2.6 - January 2026*
