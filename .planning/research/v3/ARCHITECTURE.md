# Architecture Patterns: Agent Observability Foundation

**Domain:** AI Agent Observability for FSI Compliance
**Researched:** February 5, 2026
**Confidence:** HIGH (based on official Microsoft documentation and verified existing FSI-AgentGov patterns)

---

## Executive Summary

Agent Observability Foundation is an Azure-native observability solution for Copilot Studio and Agent 365 SDK agents, providing FSI-compliant monitoring, alerting, and compliance reporting capabilities. The architecture integrates with existing FSI-AgentGov patterns (PowerShell scripts, Dataverse schemas, Power BI dashboards) while introducing Azure Monitor Workbooks and KQL query libraries as new reusable components.

**Key Integration Points:**
- Extends Control 3.2 (Usage Analytics) with Azure-native observability
- Complements Deny Event Correlation Report with real-time monitoring
- Provides separation of duties (SoD) boundaries between operational monitoring and compliance audit
- Shares Entra ID authentication patterns with existing solutions

**New Components Introduced:**
- Azure Monitor Workbook templates (JSON format, ARM-deployable)
- Parameterized KQL query library
- Azure Monitor alert rules with action groups
- Power BI semantic model for Application Insights data

---

## Recommended Architecture

The Agent Observability Foundation follows a **layered observability architecture** with clear separation between operational monitoring (real-time, transient) and compliance audit (historical, immutable).

### High-Level Data Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Agent Layer                                   │
├──────────────────────────┬──────────────────────────────────────────┤
│  Copilot Studio Agents   │  Agent 365 SDK Agents (Preview)          │
│  (Native Instrumentation)│  (OpenTelemetry SDK)                     │
└──────────────┬───────────┴──────────────┬───────────────────────────┘
               │                          │
               └──────────┬───────────────┘
                          ▼
         ┌────────────────────────────────────────┐
         │   Azure Application Insights           │
         │   (Telemetry Aggregation & Storage)    │
         └────────┬───────────────────────────────┘
                  │
                  ├───────► Operational Monitoring Path
                  │         (Real-time, Role: Operations Team)
                  │         ┌──────────────────────────────────┐
                  │         │  KQL Queries (query library)     │
                  │         │  Azure Monitor Workbooks         │
                  │         │  Azure Monitor Alert Rules       │
                  │         └──────────────────────────────────┘
                  │
                  └───────► Compliance Audit Path
                            (Historical, Role: Compliance/Audit)
                            ┌──────────────────────────────────┐
                            │  Continuous Export → ADLS Gen2   │
                            │  Power BI Semantic Model         │
                            │  Compliance Dashboard Integration│
                            └──────────────────────────────────┘
```

### Component Boundaries

| Component | Responsibility | Communicates With | Data Classification |
|-----------|---------------|-------------------|---------------------|
| **Application Insights** | Telemetry ingestion, short-term storage (90 days default) | Copilot Studio agents, Agent 365 SDK apps, Azure Monitor | FSI-Internal (contains conversation metadata, not full content) |
| **KQL Query Library** | Reusable, parameterized queries for operational analysis | Application Insights Log Analytics workspace | N/A (queries, not data) |
| **Azure Monitor Workbooks** | Interactive operational dashboards for monitoring teams | Application Insights, KQL Query Library | FSI-Internal (visualizes telemetry) |
| **Azure Monitor Alerts** | Real-time threshold detection and notification | Application Insights, Action Groups (Teams, Email, ServiceNow) | FSI-Internal (alert conditions) |
| **Continuous Export** | Compliance-grade export to immutable storage | Application Insights → Azure Data Lake Gen2 | FSI-Confidential (long-term audit storage) |
| **Power BI Semantic Model** | Compliance reporting and executive dashboards | Application Insights (DirectQuery for real-time) or ADLS (Import for historical) | FSI-Internal (aggregated metrics) |
| **Compliance Dashboard Integration** | Unified 62-control view with observability metrics | Dataverse Compliance Hub (existing) + Power BI Semantic Model | FSI-Internal (compliance posture) |

---

## Integration with Existing FSI-AgentGov Components

### 1. Extends Control 3.2 (Usage Analytics and Activity Monitoring)

Control 3.2 currently provides:
- Power Platform Admin Center analytics (28-day retention)
- Managed Environment usage insights
- Purview Audit logs for deny events

**Agent Observability Foundation adds:**
- Azure Application Insights integration for Copilot Studio agents
- Real-time performance monitoring (latency, success rate, exceptions)
- Custom telemetry events for business metrics
- 90-day default retention (configurable up to 730 days)

**Integration Point:** Control 3.2 playbooks will reference Agent Observability Foundation as the **Azure-native observability option** for organizations with Azure subscriptions.

### 2. Complements Deny Event Correlation Report

Deny Event Correlation Report (existing solution):
- Batch extraction from Purview Audit, DLP, Application Insights
- Daily PowerShell orchestration
- CSV/Power BI output

**Agent Observability Foundation complements with:**
- Real-time alerting on RAI content filtering events
- Cross-agent anomaly detection (e.g., sudden spike in deny events)
- Workbook for investigating deny events in Application Insights

**Integration Point:** Share KQL queries between solutions. Deny Event Correlation Report uses batch extraction; Agent Observability Foundation uses real-time queries.

### 3. Shares Authentication Patterns

All existing FSI-AgentGov-Solutions use **Entra ID (Azure AD) authentication**:
- `Connect-AzAccount` for Azure resources
- `Connect-ExchangeOnline` for Purview
- Service principal support for automation

**Agent Observability Foundation follows this pattern:**
- PowerShell scripts use `Connect-AzAccount` and `Get-AzAccessToken`
- No API keys or secrets in scripts
- Azure Key Vault for sensitive configuration (connection strings, tenant IDs)

### 4. Integrates with Compliance Dashboard

Compliance Dashboard (existing solution) tracks compliance status for 62 controls across 4 pillars using Dataverse tables and Power BI.

**Agent Observability Foundation integration:**

| Compliance Dashboard Table | Observability Data Source | Metric |
|----------------------------|---------------------------|--------|
| `fsi_compliancescore` | Application Insights KQL aggregation | Control 3.2 compliance score based on agent success rate |
| `fsi_complianceevidence` | Application Insights workbook screenshot + KQL query results | Evidence for Control 3.2 verification |
| `fsi_complianceexception` | Azure Monitor alert rule violations | Open exceptions when agents fail SLA thresholds |

**Data Flow:**
```
Application Insights (KQL query)
         ↓
Power Automate flow (daily aggregation)
         ↓
Dataverse fsi_compliancescore table
         ↓
Compliance Dashboard Power BI report
```

---

## Data Flow: Copilot Studio → Application Insights

### Copilot Studio Telemetry Pipeline

Copilot Studio agents send telemetry to Application Insights when configured with a connection string in the agent's Advanced Settings.

**Configuration Steps:**
1. Create Application Insights resource in Azure
2. Copy connection string (format: `InstrumentationKey=xxx;IngestionEndpoint=https://...`)
3. In Copilot Studio, navigate to Settings > Advanced > Application Insights
4. Paste connection string and save

**Telemetry Tables:**

| Table | Event Type | Schema | Retention |
|-------|-----------|--------|-----------|
| `customEvents` | Custom telemetry logged from topics | `name`, `timestamp`, `customDimensions` (JSON with channelId, TopicName, text, designMode) | 90 days default |
| `traces` | Conversation messages, errors, warnings | `message`, `severityLevel`, `timestamp`, `customDimensions` | 90 days default |
| `exceptions` | Agent runtime exceptions, connector failures | `type`, `message`, `outerMessage`, `timestamp` | 90 days default |
| `pageViews` | Agent conversation starts (if web channel) | `name`, `url`, `timestamp` | 90 days default |

**Custom Dimensions Schema (Copilot Studio):**

Based on official Microsoft documentation, `customDimensions` field contains:

```json
{
  "type": "message",
  "channelId": "msteams",
  "fromId": "user-guid",
  "fromName": "John Doe",
  "locale": "en-us",
  "recipientId": "bot-guid",
  "recipientName": "FSI Compliance Agent",
  "text": "What is our policy on AI usage?",
  "speak": null,
  "designMode": "False",
  "TopicName": "Policy Questions"
}
```

**Key Fields for FSI Compliance:**

| Field | Purpose | FSI Use Case |
|-------|---------|--------------|
| `channelId` | Identifies user channel (Teams, web, DirectLine) | Zone classification (Teams = Zone 2/3, web = Zone 1) |
| `TopicName` | Agent topic triggered | Control 3.2 usage analytics by topic |
| `designMode` | Test canvas vs. production | Exclude test conversations from compliance metrics |
| `text` | User message content | Only logged if "Log sensitive Activity properties" is enabled (Zone 3 requirement) |

**Privacy Controls:**

| Setting | Default | Zone 1 | Zone 2 | Zone 3 |
|---------|---------|--------|--------|--------|
| Enable Application Insights | Off | Optional | Recommended | Required |
| Log sensitive Activity properties (user messages) | Off | Off | Off | On (with PII scrubbing) |

### Agent 365 SDK Telemetry Pipeline (Preview)

Agent 365 SDK agents use OpenTelemetry instrumentation, providing richer telemetry than Copilot Studio.

**Architecture:**
```
Agent 365 SDK Application
         ↓
    Observability SDK
         ↓
  OpenTelemetry Collector (optional)
         ↓
Azure Monitor (Application Insights)
```

**Additional Tables:**

| Table | Event Type | Schema | Notes |
|-------|-----------|--------|-------|
| `requests` | Agent interaction requests | `name`, `duration`, `resultCode`, `success` | HTTP-style request tracking |
| `dependencies` | External API calls, database queries | `name`, `target`, `duration`, `success` | Tracks connector calls |

**OpenTelemetry Semantic Conventions:**

Agent 365 SDK follows OpenTelemetry semantic conventions for attributes:
- `service.name`: Agent identifier
- `deployment.environment`: Zone classification
- `ai.operation.type`: "chat", "completion", "embedding"
- `ai.token.count`: Token usage for cost tracking

**Correlation IDs:**

OpenTelemetry provides built-in correlation:
- `operation_Id`: Links all events in a single conversation
- `operation_ParentId`: Links agent handoffs (multi-agent scenarios)

This enables cross-agent trace analysis for complex workflows.

---

## KQL Query Organization

### Query Library Structure

KQL queries are organized as **reusable functions** stored in Application Insights Log Analytics workspace.

**Directory Structure:**
```
agent-observability-foundation/
├── application-insights/
│   ├── kql/
│   │   ├── base-queries/
│   │   │   ├── agent-success-rate.kql
│   │   │   ├── agent-latency-p95.kql
│   │   │   ├── agent-exceptions.kql
│   │   │   └── agent-conversation-volume.kql
│   │   ├── compliance-queries/
│   │   │   ├── deny-events-by-agent.kql
│   │   │   ├── rai-content-filtered.kql
│   │   │   ├── zone3-conversation-audit.kql
│   │   │   └── topic-usage-summary.kql
│   │   ├── anomaly-detection/
│   │   │   ├── latency-spike-detection.kql
│   │   │   ├── error-rate-anomaly.kql
│   │   │   └── conversation-volume-anomaly.kql
│   │   └── cross-workspace/
│   │       ├── multi-environment-correlation.kql
│   │       └── tenant-wide-usage.kql
│   └── functions/
│       ├── README.md
│       └── deploy-functions.ps1
```

### KQL Function Pattern

**Parameterized Function (Deployed to Workspace):**

```kql
// Function name: GetAgentSuccessRate
// Description: Calculates success rate for a specific agent over a time range
// Parameters:
//   - AgentId: string (required) - Agent identifier from customDimensions
//   - StartTime: datetime (default: ago(24h))
//   - EndTime: datetime (default: now())

.create-or-alter function with (folder = "AgentMetrics", docstring = "Calculate agent success rate")
GetAgentSuccessRate(AgentId:string, StartTime:datetime = ago(24h), EndTime:datetime = now()) {
    customEvents
    | where timestamp between (StartTime .. EndTime)
    | where customDimensions.recipientName == AgentId
    | where customDimensions.designMode == "False"  // Exclude test
    | summarize
        TotalConversations = count(),
        SuccessfulConversations = countif(customDimensions.type == "message" and customDimensions.text != "")
    | extend SuccessRate = round(100.0 * SuccessfulConversations / TotalConversations, 2)
    | project AgentId, SuccessRate, TotalConversations
}
```

**Deployment via PowerShell:**

```powershell
# Deploy-KqlFunctions.ps1
#Requires -Version 7.0
#Requires -Modules Az.Accounts, Az.OperationalInsights

$functionPath = "./kql/base-queries/agent-success-rate.kql"
$functionDefinition = Get-Content $functionPath -Raw

# Deploy function to workspace
Invoke-AzOperationalInsightsQuery `
    -WorkspaceId $workspaceId `
    -Query $functionDefinition
```

### Best Practices for KQL Queries

Based on official Microsoft documentation and existing FSI-AgentGov patterns:

| Practice | Rationale | Example |
|----------|-----------|---------|
| **Time filters first** | Improves performance by reducing dataset early | `\| where timestamp > ago(1h)` |
| **Project only needed columns** | Reduces memory and speeds up queries | `\| project timestamp, name, duration` |
| **Use summarize for aggregations** | More efficient than multiple where clauses | `\| summarize count() by bin(timestamp, 1h)` |
| **Parse JSON sparingly** | `customDimensions` is already parsed in newer workspaces | Use `customDimensions.channelId` not `parse_json()` |
| **Parameterize common values** | Enables reusable queries | `let AgentId = "FSI-Compliance-Agent";` |
| **Comment query intent** | Critical for compliance audit trail | `// FINRA 4511: Conversation volume by agent` |

### Cross-Workspace Query Limitations

**Critical Constraint:** Workspace references cannot be parameterized.

**What This Means:**

```kql
// ❌ NOT SUPPORTED - Parameterized workspace
let TargetWorkspace = "workspace-guid";
workspace(TargetWorkspace).customEvents | ...

// ✅ SUPPORTED - Explicit workspace reference
workspace("12345678-1234-1234-1234-123456789abc").customEvents | ...
```

**Workaround for Multi-Environment Queries:**

Use Azure Data Explorer (ADX) proxy pattern:
1. Configure ADX cluster as proxy to multiple Log Analytics workspaces
2. Query ADX with parameterized workspace names
3. ADX translates to explicit workspace references

**Recommended for:** Tenant-wide queries across 10+ environments. Not needed for single-tenant FSI deployments with <5 environments.

### Query Performance Targets

| Zone | Query Type | Target Response Time | Max Dataset Size |
|------|-----------|---------------------|------------------|
| Zone 1 | Dashboard queries | <5 seconds | 100K events |
| Zone 2 | Operational queries | <10 seconds | 1M events |
| Zone 3 | Compliance queries | <30 seconds | 10M events |

**Optimization Techniques:**

- **Summarization tables:** Pre-aggregate hourly/daily metrics using continuous export
- **Sampling:** Use `sample 10` for exploratory queries, full dataset for compliance
- **Workspace design:** Separate high-volume agents into dedicated App Insights instances

---

## Azure Monitor Workbook Structure

### Workbook Template JSON Format

Azure Monitor Workbooks are deployed as ARM resources with JSON templates.

**Core Structure:**

```json
{
  "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "workbookDisplayName": {
      "type": "string",
      "defaultValue": "Agent Observability Dashboard"
    },
    "workbookSourceId": {
      "type": "string",
      "defaultValue": "Azure Monitor"
    }
  },
  "resources": [
    {
      "name": "[guid(parameters('workbookDisplayName'))]",
      "type": "Microsoft.Insights/workbooks",
      "location": "[resourceGroup().location]",
      "kind": "shared",
      "apiVersion": "2021-08-01",
      "properties": {
        "displayName": "[parameters('workbookDisplayName')]",
        "serializedData": "{...}",
        "version": "1.0",
        "sourceId": "[parameters('workbookSourceId')]",
        "category": "workbook"
      }
    }
  ]
}
```

**Key Fields:**

| Field | Purpose | FSI Consideration |
|-------|---------|-------------------|
| `displayName` | Human-readable name in workbook gallery | Use naming convention: "FSI - [Zone] - [Purpose]" |
| `serializedData` | JSON-encoded workbook definition (steps, queries, visualizations) | Contains KQL queries; treat as FSI-Internal |
| `sourceId` | Resource scope (specific resource ID or "Azure Monitor" for global) | Use specific App Insights resource ID for zone-scoped workbooks |
| `category` | Gallery grouping: "workbook", "tsg", "usage" | Use "workbook" for dashboards, "tsg" for troubleshooting guides |

### Serialized Data Structure

The `serializedData` field contains the workbook definition:

```json
{
  "version": "Notebook/1.0",
  "items": [
    {
      "type": 1,  // Markdown text
      "content": {
        "json": "# Agent Performance Dashboard\n\nReal-time monitoring for Zone 3 agents."
      }
    },
    {
      "type": 3,  // KQL query visualization
      "content": {
        "version": "KqlItem/1.0",
        "query": "customEvents | summarize count() by bin(timestamp, 1h)",
        "size": 0,
        "timeContext": {
          "durationMs": 86400000  // 24 hours
        },
        "queryType": 0,  // 0 = Application Insights
        "resourceType": "microsoft.insights/components",
        "visualization": "timechart"
      }
    },
    {
      "type": 9,  // Parameter control
      "content": {
        "version": "KqlParameterItem/1.0",
        "parameters": [
          {
            "name": "AgentId",
            "type": 2,  // Dropdown
            "query": "customEvents | distinct customDimensions.recipientName",
            "value": "FSI-Compliance-Agent"
          }
        ]
      }
    }
  ],
  "isLocked": false,
  "fallbackResourceIds": [
    "/subscriptions/{sub-id}/resourceGroups/{rg}/providers/Microsoft.Insights/components/{app-insights-name}"
  ]
}
```

**Item Types:**

| Type | Purpose | Use Case |
|------|---------|----------|
| `1` | Markdown text | Section headers, instructions, compliance disclaimers |
| `3` | KQL query + visualization | Charts, tables, metrics |
| `9` | Parameter controls | Agent selector, time range picker, zone filter |
| `10` | Link to another workbook | Navigation between operational and compliance views |

### Parameterization Patterns

**Workbook Parameters (User-Facing):**

```json
{
  "name": "TimeRange",
  "type": 4,  // Time range picker
  "value": {
    "durationMs": 86400000
  },
  "timeContextFromParameter": "TimeRange"
}
```

**Using Parameters in Queries:**

```kql
customEvents
| where timestamp {TimeRange}
| where customDimensions.recipientName == "{AgentId}"
| summarize count() by bin(timestamp, 1h)
```

**ARM Template Parameters (Deployment-Time):**

- `workbookDisplayName`: Set during deployment for multi-zone workbooks
- `fallbackResourceIds`: Injected based on target environment
- `sourceId`: Set to specific App Insights resource for zone isolation

### Workbook Organization for FSI

**Recommended Workbook Structure:**

| Workbook Name | Purpose | Audience | Zone Scope |
|---------------|---------|----------|------------|
| **FSI - Zone 3 - Operations** | Real-time monitoring, latency, success rate | Operations Team | Zone 3 only |
| **FSI - Zone 3 - Compliance Audit** | Historical compliance queries, deny events | Compliance Team | Zone 3 only |
| **FSI - Zone 2 - Team Agents** | Team agent usage, topic analytics | Team Admins | Zone 2 only |
| **FSI - Executive Summary** | Cross-zone KPIs, compliance posture | Executives, Governance Committee | All zones (aggregated) |
| **FSI - Troubleshooting Guide (TSG)** | Step-by-step investigation workflows | Support Team | All zones |

**Separation of Duties (SoD):**

| Role | Workbooks Accessible | RBAC Requirement |
|------|---------------------|------------------|
| **Operations Team** | Zone 3 Operations, Zone 2 Team Agents, TSG | Application Insights Reader |
| **Compliance Team** | Zone 3 Compliance Audit, Executive Summary | Application Insights Reader + Purview Audit Reader |
| **Executives** | Executive Summary only | Reader on workbook resource (not App Insights) |
| **Support Team** | TSG only | Application Insights Reader |

---

## Alert Rule Architecture

### Metric vs. Log-Based Alerts

Azure Monitor supports two alert types, each with different characteristics:

| Aspect | Metric Alerts | Log Search Alerts |
|--------|--------------|-------------------|
| **Resource Type** | `Microsoft.Insights/metricAlerts` | `Microsoft.Insights/scheduledQueryRules` |
| **Data Source** | Metrics emitted to Azure Monitor Metrics | Log Analytics workspace (KQL queries) |
| **Evaluation Frequency** | 1 minute (high frequency) | 5 minutes minimum (configurable) |
| **Scope** | Single or multiple resources | Query-based (can span workspaces with explicit references) |
| **Stateful/Stateless** | Stateful (auto-resolves when condition clears) | Stateless by default (requires explicit resolution query) |
| **Best For** | Simple threshold conditions (CPU, memory, request rate) | Complex conditions (multi-table joins, anomaly detection, trend analysis) |

**For Agent Observability, use Log Search Alerts** because:
- Copilot Studio telemetry is in Application Insights logs (not Azure Monitor Metrics)
- Complex conditions needed (e.g., "success rate <95% for >30 minutes")
- Correlation across multiple tables (customEvents, traces, exceptions)

### Alert Rule Configuration

**PowerShell Deployment Example:**

```powershell
# Create-AgentSuccessRateAlert.ps1
#Requires -Version 7.0
#Requires -Modules Az.Accounts, Az.Monitor

$alertRuleParams = @{
    Name = "FSI-Zone3-SuccessRate-Critical"
    ResourceGroupName = "rg-fsi-monitoring"
    Location = "eastus"
    Condition = @{
        Query = @"
customEvents
| where timestamp > ago(30m)
| where customDimensions.recipientName == "FSI-Compliance-Agent"
| where customDimensions.designMode == "False"
| summarize
    Total = count(),
    Success = countif(customDimensions.type == "message")
| extend SuccessRate = 100.0 * Success / Total
| where SuccessRate < 95
"@
        TimeAggregation = "Average"
        Operator = "LessThan"
        Threshold = 95
        MetricMeasureColumn = "SuccessRate"
    }
    Severity = 1  # Critical (0=Critical, 1=Error, 2=Warning, 3=Informational, 4=Verbose)
    Frequency = "PT5M"  # Check every 5 minutes
    WindowSize = "PT30M"  # Evaluate over 30-minute window
    ActionGroupId = "/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Insights/actionGroups/FSI-Critical-Alerts"
}

New-AzScheduledQueryRule @alertRuleParams
```

**Alert Rule Structure:**

| Field | Purpose | FSI Guideline |
|-------|---------|---------------|
| `Name` | Alert identifier | Use prefix: "FSI-[Zone]-[Metric]-[Severity]" |
| `Severity` | 0 (Critical) to 4 (Verbose) | Zone 3: 0-1, Zone 2: 1-2, Zone 1: 2-3 |
| `Frequency` | How often to evaluate condition | Zone 3: 5 min, Zone 2: 15 min, Zone 1: 1 hour |
| `WindowSize` | Time range for query | Use 6x frequency (e.g., 30 min window for 5 min frequency) |
| `ActionGroupId` | What actions to trigger | Separate action groups by severity |

### Agent-Specific Threshold Configuration

**Threshold Matrix by Zone:**

| Metric | Zone 1 | Zone 2 | Zone 3 |
|--------|--------|--------|--------|
| Success Rate | >80% | >90% | >95% |
| P95 Latency | <10s | <5s | <2s |
| Exception Rate | <5% | <2% | <1% |
| Content Filtered (RAI) | Not monitored | >10 events/day | >5 events/day |

**Per-Agent Baseline Calculation:**

```kql
// Calculate agent-specific baseline (7-day rolling average)
let BaselineWindow = 7d;
let AgentId = "FSI-Compliance-Agent";
customEvents
| where timestamp > ago(BaselineWindow)
| where customDimensions.recipientName == AgentId
| summarize
    AvgSuccessRate = avg(todouble(customDimensions.successRate)),
    StdDev = stdev(todouble(customDimensions.successRate))
| extend
    AlertThreshold = AvgSuccessRate - (2 * StdDev)  // 2 standard deviations
| project AgentId, AlertThreshold
```

**Dynamic Thresholds:**

Azure Monitor supports **dynamic thresholds** (machine learning-based) that adapt to agent behavior:

```powershell
$dynamicCondition = @{
    Query = "customEvents | where customDimensions.recipientName == 'FSI-Compliance-Agent' | summarize SuccessRate = avg(success)"
    TimeAggregation = "Average"
    Operator = "LessThan"
    AlertSensitivity = "Medium"  # Low, Medium, High
    FailingPeriods = @{
        NumberOfEvaluationPeriods = 4
        MinFailingPeriodsToAlert = 3  # Must fail 3 of 4 checks
    }
}
```

**Recommendation:** Use static thresholds for Zone 3 (regulatory SLAs), dynamic thresholds for Zone 2 (operational anomalies).

### Action Groups

Action groups define **who gets notified** and **what automated actions** occur when an alert fires.

**Action Group Structure:**

```powershell
# Create-ActionGroup.ps1
$actionGroupParams = @{
    Name = "FSI-Critical-Alerts"
    ResourceGroupName = "rg-fsi-monitoring"
    ShortName = "FSICrit"  # Max 12 characters, used in SMS
    EmailReceiver = @(
        @{ Name = "Compliance-Team"; EmailAddress = "compliance@fsi-bank.com" }
        @{ Name = "Operations-Lead"; EmailAddress = "ops-lead@fsi-bank.com" }
    )
    SmsReceiver = @(
        @{ Name = "On-Call-Engineer"; CountryCode = "1"; PhoneNumber = "5551234567" }
    )
    WebhookReceiver = @(
        @{
            Name = "ServiceNow-Incident"
            ServiceUri = "https://fsi-bank.service-now.com/api/now/table/incident"
            UseCommonAlertSchema = $true
        }
    )
    AzureFunctionReceiver = @(
        @{
            Name = "AutoRemediation"
            FunctionAppResourceId = "/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Web/sites/fsi-auto-remediate"
            FunctionName = "RestartAgent"
            HttpTriggerUrl = "https://fsi-auto-remediate.azurewebsites.net/api/RestartAgent"
        }
    )
}

New-AzActionGroup @actionGroupParams
```

**Action Types Supported:**

| Action Type | Use Case | FSI Consideration |
|-------------|----------|-------------------|
| **Email** | Notify compliance/operations teams | Use distribution lists, not individual emails |
| **SMS** | On-call engineer notifications | Zone 3 critical alerts only (cost and fatigue) |
| **Teams** | Post to Teams channel | Recommended for Zone 2/3 operational alerts |
| **Webhook** | ServiceNow, PagerDuty integration | Requires HTTPS endpoint with AAD authentication |
| **Logic App** | Complex workflows (e.g., create Jira ticket) | Use for multi-step remediation |
| **Azure Function** | Automated remediation | Disable agent, trigger backup, etc. |
| **ITSM Connector** | ServiceNow, BMC Remedy | Direct incident creation |

**SoD Boundaries for Action Groups:**

| Action Group | Recipients | Purpose | Deployment Zone |
|--------------|-----------|---------|-----------------|
| `FSI-Zone3-Critical` | Compliance Team, Operations Lead, On-Call Engineer | Zone 3 SLA violations | Production only |
| `FSI-Zone3-Operational` | Operations Team | Zone 3 warnings, non-critical | Production only |
| `FSI-Zone2-Alerts` | Team Admins, Operations Team | Zone 2 performance issues | Production + UAT |
| `FSI-Compliance-Audit` | Compliance Team ONLY | Compliance violations (no operations) | Production only |

**Critical:** Compliance-focused action groups must NOT include operations team members to maintain audit independence (SOX 404 requirement).

---

## Power BI Integration

### DirectQuery vs. Import for Application Insights

Power BI supports two connectivity modes for Application Insights data:

| Mode | Description | Pros | Cons | FSI Use Case |
|------|-------------|------|------|--------------|
| **DirectQuery** | Queries Application Insights in real-time | Always current data, no refresh needed | Slower performance, 3-minute query timeout | Operational dashboards (real-time metrics) |
| **Import** | Imports data into Power BI dataset | Fast performance, advanced modeling | Requires scheduled refresh, data staleness | Compliance dashboards (historical analysis) |
| **Composite (Hybrid)** | Mix of DirectQuery and Import tables | Best of both worlds | Complex to maintain | Executive dashboards (real-time KPIs + historical trends) |

**Recommendation by Dashboard Type:**

| Dashboard | Mode | Refresh Schedule | Retention |
|-----------|------|------------------|-----------|
| **Operations Dashboard** | DirectQuery | N/A (real-time) | 90 days (App Insights retention) |
| **Compliance Dashboard** | Import | Daily at 7 AM | 7 years (export to ADLS) |
| **Executive Dashboard** | Composite | Daily for Import tables | 90 days + 7 years archived |

### Semantic Model Design

**Star Schema for Agent Metrics:**

```
┌──────────────────────┐
│   FactConversations  │  (Import or DirectQuery)
├──────────────────────┤
│ ConversationId (PK)  │
│ AgentId (FK)         │
│ Timestamp            │
│ Duration             │
│ Success              │
│ ExceptionCount       │
│ TokenCount           │
└──────────────────────┘
         │
         ├──────► ┌────────────────┐
         │        │   DimAgent     │  (Import)
         │        ├────────────────┤
         │        │ AgentId (PK)   │
         │        │ AgentName      │
         │        │ Zone           │
         │        │ Owner          │
         │        │ ComplianceTag  │
         │        └────────────────┘
         │
         ├──────► ┌────────────────┐
         │        │   DimTopic     │  (Import)
         │        ├────────────────┤
         │        │ TopicId (PK)   │
         │        │ TopicName      │
         │        │ Category       │
         │        └────────────────┘
         │
         └──────► ┌────────────────┐
                  │   DimDate      │  (Import)
                  ├────────────────┤
                  │ DateKey (PK)   │
                  │ Date           │
                  │ Year           │
                  │ Quarter        │
                  │ Month          │
                  │ DayOfWeek      │
                  └────────────────┘
```

**Power Query M Code for Application Insights (DirectQuery):**

```m
let
    Source = ApplicationInsights.Contents(
        "12345678-1234-1234-1234-123456789abc",  // App Insights App ID
        #duration(90, 0, 0, 0),  // 90-day lookback
        null
    ),

    // KQL query for conversation facts
    Query = "
        customEvents
        | where timestamp > ago(90d)
        | where customDimensions.designMode == 'False'
        | extend
            AgentId = tostring(customDimensions.recipientName),
            TopicName = tostring(customDimensions.TopicName),
            Duration = todouble(customDimensions.duration),
            Success = customDimensions.type == 'message'
        | project
            ConversationId = operation_Id,
            Timestamp = timestamp,
            AgentId,
            TopicName,
            Duration,
            Success
    ",

    Result = ApplicationInsights.Query(Source, Query)
in
    Result
```

**DAX Measures for Compliance Metrics:**

```dax
// Success Rate (Control 3.2 compliance)
SuccessRate =
DIVIDE(
    CALCULATE(
        COUNTROWS(FactConversations),
        FactConversations[Success] = TRUE
    ),
    COUNTROWS(FactConversations),
    0
) * 100

// P95 Latency
P95Latency =
PERCENTILE.INC(
    FactConversations[Duration],
    0.95
)

// Zone 3 Compliance Score (>95% success rate = compliant)
Zone3ComplianceScore =
VAR AgentSuccessRate = [SuccessRate]
RETURN
    IF(
        AgentSuccessRate >= 95,
        "Compliant",
        IF(
            AgentSuccessRate >= 90,
            "Partial",
            "Non-Compliant"
        )
    )

// Daily Conversation Volume (with day-over-day change)
DailyConversations =
CALCULATE(
    COUNTROWS(FactConversations),
    USERELATIONSHIP(FactConversations[Timestamp], DimDate[Date])
)

DailyConversationsChange =
VAR Yesterday = [DailyConversations] - 1
VAR Today = [DailyConversations]
RETURN
    DIVIDE(Today - Yesterday, Yesterday, 0) * 100
```

### Data Source Integration Pattern

**Option 1: Direct Application Insights Connector (DirectQuery)**

```powershell
# Get-AppInsightsCredentials.ps1
$appInsightsAppId = "12345678-1234-1234-1234-123456789abc"
$apiKey = Get-AzKeyVaultSecret -VaultName "kv-fsi-monitoring" -Name "AppInsights-ApiKey" -AsPlainText

# Note: API key authentication is deprecated (March 2026).
# Use Azure AD service principal authentication instead.
$servicePrincipal = Get-AzADServicePrincipal -DisplayName "PowerBI-AppInsights-Reader"
$tenantId = "tenant-guid"
```

**Option 2: Continuous Export to ADLS + Power BI Import (Compliance)**

```
Application Insights
         ↓
Continuous Export (configured via Azure Portal)
         ↓
Azure Data Lake Storage Gen2
    /raw/
        /year=2026/
            /month=02/
                /day=05/
                    /PT1H.json  (hourly export)
         ↓
Azure Data Factory (transform and aggregate)
         ↓
    /processed/
        /conversations/
        /metrics/
         ↓
Power BI Import (scheduled refresh)
```

**Continuous Export Configuration:**

```powershell
# Enable-ContinuousExport.ps1
$exportConfig = @{
    ResourceGroupName = "rg-fsi-monitoring"
    ComponentName = "appi-fsi-agents"
    StorageAccountId = "/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Storage/storageAccounts/stfsiaudit"
    DestinationPath = "appinsights-export"
    RecordTypes = @("Request", "Exception", "CustomEvent", "Trace")
}

# Note: Continuous Export is a legacy feature.
# Microsoft recommends using Diagnostic Settings with Log Analytics workspace.
# However, for FSI compliance requiring immutable storage, Continuous Export to ADLS remains valid.
```

**Modern Alternative: Diagnostic Settings**

```powershell
# Configure-DiagnosticSettings.ps1
$diagSettings = @{
    ResourceId = "/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Insights/components/appi-fsi-agents"
    StorageAccountId = "/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Storage/storageAccounts/stfsiaudit"
    WorkspaceId = "/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.OperationalInsights/workspaces/law-fsi-monitoring"
    Enabled = $true
    Category = @("AllMetrics", "AppTraces", "AppExceptions")
    RetentionInDays = 2555  # 7 years for SEC 17a-4
}

Set-AzDiagnosticSetting @diagSettings -Name "FSI-Compliance-Export"
```

### Row-Level Security (RLS) for Multi-Zone Access

Power BI RLS ensures users only see data for their authorized zones.

**RLS DAX Filters:**

```dax
// RLS Role: Zone1Users
[Zone] = "Zone 1"

// RLS Role: Zone2Users
[Zone] IN {"Zone 1", "Zone 2"}

// RLS Role: Zone3Users (Operations)
[Zone] = "Zone 3"

// RLS Role: ComplianceAuditors (Read-Only, All Zones)
[Zone] IN {"Zone 1", "Zone 2", "Zone 3"}
&& [DataClassification] <> "Operational"  // Exclude real-time operational data

// RLS Role: Executives (Summary Only)
[AggregationLevel] = "Summary"
```

**Deployment Pattern:**

1. Power BI Desktop: Define RLS roles and DAX filters
2. Publish to Power BI Service
3. Map Azure AD security groups to RLS roles:
   - `SG-FSI-Zone1-Users` → Zone1Users role
   - `SG-FSI-Compliance-Auditors` → ComplianceAuditors role

**Testing RLS:**

```powershell
# Test-PowerBIRLS.ps1
# Use "View as Role" in Power BI Service to validate filters
# Or use Power BI REST API to programmatically test

$testParams = @{
    WorkspaceId = "workspace-guid"
    ReportId = "report-guid"
    RoleName = "Zone3Users"
    UserPrincipalName = "testuser@fsi-bank.com"
}

# Expected: Only Zone 3 data visible to test user
```

---

## Separation of Duties (SoD) Architecture

### SoD Requirements for FSI Compliance

Financial services organizations must maintain independence between:
1. **Operational monitoring** - Real-time performance, troubleshooting
2. **Compliance audit** - Historical analysis, regulatory evidence

**Regulatory Drivers:**
- **SOX 404:** Internal control independence
- **FINRA 3120:** Supervisory procedures separation
- **OCC 2011-12:** Model risk validation independence

### SoD Boundaries in Agent Observability

**Logical Separation:**

```
┌─────────────────────────────────────────────────────────────────┐
│                   Application Insights                           │
│                   (Shared Data Source)                           │
└────────────────────────┬────────────────────────────────────────┘
                         │
         ┌───────────────┴───────────────┐
         │                               │
         ▼                               ▼
┌─────────────────────┐         ┌──────────────────────┐
│  Operational Path   │         │  Compliance Path     │
├─────────────────────┤         ├──────────────────────┤
│ Azure Monitor       │         │ Continuous Export    │
│ Workbooks           │         │ → ADLS Gen2          │
│ (Real-time)         │         │ (Immutable)          │
│                     │         │                      │
│ Alert Rules         │         │ Power BI             │
│ (Actions)           │         │ (Import Mode)        │
│                     │         │                      │
│ RBAC: Operations    │         │ RBAC: Compliance     │
│ Team                │         │ Team ONLY            │
└─────────────────────┘         └──────────────────────┘
         │                               │
         ▼                               ▼
   [Auto-remediation]             [Regulatory Reports]
   [Incident Response]            [Audit Evidence]
```

### RBAC Matrix for SoD

| Role | Application Insights | Workbooks (Operational) | Workbooks (Compliance) | ADLS (Compliance Export) | Power BI (Operational) | Power BI (Compliance) | Alert Action Groups |
|------|---------------------|-------------------------|------------------------|--------------------------|------------------------|----------------------|---------------------|
| **Operations Team** | Reader | Reader | No Access | No Access | Viewer | No Access | Member |
| **Compliance Team** | Reader | No Access | Reader | Reader | No Access | Viewer | No Access |
| **Auditors (External)** | No Access | No Access | Reader | Reader | No Access | Viewer | No Access |
| **Executives** | No Access | No Access | Reader | No Access | No Access | Viewer | No Access |
| **Platform Admins** | Contributor | Contributor | Contributor | Contributor | Admin | Admin | Owner |

**Azure RBAC Roles:**

```powershell
# Assign-SoDRoles.ps1

# Operations Team: Application Insights Reader
New-AzRoleAssignment `
    -ObjectId (Get-AzADGroup -DisplayName "SG-FSI-Operations-Team").Id `
    -RoleDefinitionName "Monitoring Reader" `
    -Scope "/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Insights/components/appi-fsi-agents"

# Compliance Team: ADLS Reader (compliance export only)
New-AzRoleAssignment `
    -ObjectId (Get-AzADGroup -DisplayName "SG-FSI-Compliance-Team").Id `
    -RoleDefinitionName "Storage Blob Data Reader" `
    -Scope "/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Storage/storageAccounts/stfsiaudit/blobServices/default/containers/appinsights-export"

# External Auditors: ADLS Reader (time-limited)
$auditorAssignment = New-AzRoleAssignment `
    -ObjectId (Get-AzADUser -UserPrincipalName "external.auditor@audit-firm.com").Id `
    -RoleDefinitionName "Storage Blob Data Reader" `
    -Scope "/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Storage/storageAccounts/stfsiaudit" `
    -ExpirationDate (Get-Date).AddDays(90)  # 90-day audit window
```

### Data Flow with SoD Enforcement

**Operational Path (Real-Time, Mutable):**

```
Application Insights
    ↓ (queries executed in real-time)
KQL Queries (operational)
    ↓
Azure Monitor Workbooks (operational dashboards)
    ↓
Alert Rules → Action Groups → Teams/Email/Auto-Remediation
    ↓
Operations Team responds with changes to agents
```

**Compliance Path (Historical, Immutable):**

```
Application Insights
    ↓ (continuous export every 1 hour)
Azure Data Lake Storage Gen2 (immutable blob storage)
    ↓ (append-only, no delete/modify)
Power BI Import (daily refresh)
    ↓
Compliance Dashboard (read-only)
    ↓
Compliance Team generates regulatory reports
    ↓
External Auditors review (no write access)
```

**Key SoD Controls:**

| Control | Implementation | Audit Evidence |
|---------|---------------|----------------|
| **No operational access to compliance data** | Operations Team has no RBAC on ADLS | Azure Activity Log: No access attempts by operations |
| **No compliance team in alert action groups** | Compliance Team excluded from action groups | Alert rule configuration export |
| **Immutable compliance storage** | ADLS immutable blob policy (WORM) | Blob policy JSON export |
| **Time-limited auditor access** | Azure PIM (Privileged Identity Management) for auditor roles | PIM access reviews |
| **Separate Power BI workspaces** | Operational workspace ≠ Compliance workspace | Power BI workspace member lists |

---

## Deployment Automation

### Idempotent Deployment Principles

All Agent Observability Foundation components must be deployable idempotently using ARM templates, Azure CLI, or PowerShell.

**Idempotency Definition:** Running the same deployment multiple times produces the same result without errors or duplicate resources.

**Techniques:**

| Resource Type | Idempotency Approach |
|---------------|---------------------|
| **Application Insights** | Use `az deployment group create` with `--mode Incremental` |
| **Workbooks** | Use GUID from workbook display name as resource name: `guid('FSI-Zone3-Operations')` |
| **Alert Rules** | Use `New-AzScheduledQueryRule` with `-Force` (overwrites existing) |
| **Action Groups** | Check existence with `Get-AzActionGroup` before creating |
| **KQL Functions** | Use `.create-or-alter function` (KQL native idempotency) |

### Deployment Orchestration Script

**Master Deployment Script (PowerShell):**

```powershell
# Deploy-AgentObservability.ps1
<#
.SYNOPSIS
    Deploys Agent Observability Foundation to an Azure subscription.

.DESCRIPTION
    Idempotent deployment of Application Insights, workbooks, alert rules,
    and KQL functions for FSI agent monitoring.

.PARAMETER SubscriptionId
    Target Azure subscription.

.PARAMETER ResourceGroupName
    Target resource group (created if doesn't exist).

.PARAMETER EnvironmentName
    Environment name (dev, uat, prod).

.PARAMETER Zone
    Governance zone (Zone1, Zone2, Zone3).

.EXAMPLE
    Connect-AzAccount
    .\Deploy-AgentObservability.ps1 -SubscriptionId "xxx" -ResourceGroupName "rg-fsi-monitoring" -EnvironmentName "prod" -Zone "Zone3"
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$SubscriptionId,

    [Parameter(Mandatory)]
    [string]$ResourceGroupName,

    [Parameter(Mandatory)]
    [ValidateSet("dev", "uat", "prod")]
    [string]$EnvironmentName,

    [Parameter(Mandatory)]
    [ValidateSet("Zone1", "Zone2", "Zone3")]
    [string]$Zone
)

#Requires -Version 7.0
#Requires -Modules Az.Accounts, Az.Resources, Az.Monitor, Az.OperationalInsights

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Set subscription context
Set-AzContext -SubscriptionId $SubscriptionId

Write-Host "Deploying Agent Observability Foundation..."
Write-Host "  Subscription: $SubscriptionId"
Write-Host "  Resource Group: $ResourceGroupName"
Write-Host "  Environment: $EnvironmentName"
Write-Host "  Zone: $Zone"

# 1. Ensure resource group exists (idempotent)
$rg = Get-AzResourceGroup -Name $ResourceGroupName -ErrorAction SilentlyContinue
if (-not $rg) {
    Write-Host "Creating resource group $ResourceGroupName..."
    New-AzResourceGroup -Name $ResourceGroupName -Location "eastus" -Tag @{
        Environment = $EnvironmentName
        Zone = $Zone
        ManagedBy = "FSI-AgentGov"
    }
} else {
    Write-Host "Resource group $ResourceGroupName already exists."
}

# 2. Deploy Application Insights (idempotent via ARM)
Write-Host "Deploying Application Insights..."
$appInsightsDeployment = New-AzResourceGroupDeployment `
    -ResourceGroupName $ResourceGroupName `
    -TemplateFile "./arm-templates/application-insights.json" `
    -TemplateParameterObject @{
        appInsightsName = "appi-fsi-$EnvironmentName-$Zone".ToLower()
        location = "eastus"
        retentionInDays = if ($Zone -eq "Zone3") { 365 } else { 90 }
    } `
    -Mode Incremental

$appInsightsName = $appInsightsDeployment.Outputs.appInsightsName.Value
$workspaceId = $appInsightsDeployment.Outputs.workspaceId.Value

Write-Host "Application Insights deployed: $appInsightsName"

# 3. Deploy KQL functions (idempotent via .create-or-alter)
Write-Host "Deploying KQL functions..."
$kqlFunctions = Get-ChildItem "./kql/base-queries/*.kql"
foreach ($function in $kqlFunctions) {
    Write-Host "  Deploying function: $($function.Name)"
    $functionDef = Get-Content $function.FullName -Raw

    # Execute KQL function deployment
    Invoke-AzOperationalInsightsQuery `
        -WorkspaceId $workspaceId `
        -Query $functionDef
}

# 4. Deploy workbooks (idempotent via ARM)
Write-Host "Deploying workbooks..."
$workbookTemplates = Get-ChildItem "./arm-templates/workbooks/*.json"
foreach ($template in $workbookTemplates) {
    Write-Host "  Deploying workbook: $($template.BaseName)"

    New-AzResourceGroupDeployment `
        -ResourceGroupName $ResourceGroupName `
        -TemplateFile $template.FullName `
        -TemplateParameterObject @{
            workbookSourceId = "/subscriptions/$SubscriptionId/resourceGroups/$ResourceGroupName/providers/Microsoft.Insights/components/$appInsightsName"
            workbookDisplayName = "$($template.BaseName) - $Zone"
        } `
        -Mode Incremental
}

# 5. Deploy alert rules (idempotent via -Force)
Write-Host "Deploying alert rules..."
$alertConfigs = Get-Content "./config/alert-rules-$Zone.json" | ConvertFrom-Json

foreach ($alertConfig in $alertConfigs) {
    Write-Host "  Deploying alert: $($alertConfig.name)"

    $actionGroupId = "/subscriptions/$SubscriptionId/resourceGroups/$ResourceGroupName/providers/Microsoft.Insights/actionGroups/$($alertConfig.actionGroupName)"

    # Check if action group exists
    $actionGroup = Get-AzActionGroup -ResourceGroupName $ResourceGroupName -Name $alertConfig.actionGroupName -ErrorAction SilentlyContinue
    if (-not $actionGroup) {
        Write-Warning "Action group $($alertConfig.actionGroupName) not found. Skipping alert rule."
        continue
    }

    # Deploy alert rule (overwrites if exists)
    $alertParams = @{
        Name = $alertConfig.name
        ResourceGroupName = $ResourceGroupName
        Location = "eastus"
        WindowSize = [TimeSpan]::FromMinutes($alertConfig.windowSizeMinutes)
        Frequency = [TimeSpan]::FromMinutes($alertConfig.frequencyMinutes)
        Severity = $alertConfig.severity
        ActionGroupId = $actionGroupId
        Query = $alertConfig.query
        Threshold = $alertConfig.threshold
        Operator = $alertConfig.operator
        TimeAggregation = $alertConfig.timeAggregation
        Force = $true  # Idempotency: overwrite if exists
    }

    New-AzScheduledQueryRule @alertParams
}

Write-Host "Deployment complete!"
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Configure Copilot Studio agents with Application Insights connection string"
Write-Host "  2. Assign RBAC roles to operations and compliance teams"
Write-Host "  3. Test alert rules with synthetic events"
Write-Host "  4. Configure continuous export to ADLS for compliance"
```

### ARM Template Structure (Application Insights)

```json
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "appInsightsName": {
      "type": "string",
      "metadata": {
        "description": "Name of the Application Insights resource"
      }
    },
    "location": {
      "type": "string",
      "defaultValue": "[resourceGroup().location]"
    },
    "retentionInDays": {
      "type": "int",
      "defaultValue": 90,
      "allowedValues": [30, 60, 90, 120, 180, 270, 365, 550, 730],
      "metadata": {
        "description": "Data retention in days (Zone 3: 365, Zone 1/2: 90)"
      }
    }
  },
  "variables": {
    "workspaceName": "[concat('law-', parameters('appInsightsName'))]"
  },
  "resources": [
    {
      "type": "Microsoft.OperationalInsights/workspaces",
      "apiVersion": "2021-06-01",
      "name": "[variables('workspaceName')]",
      "location": "[parameters('location')]",
      "properties": {
        "sku": {
          "name": "PerGB2018"
        },
        "retentionInDays": "[parameters('retentionInDays')]",
        "features": {
          "enableLogAccessUsingOnlyResourcePermissions": true
        }
      }
    },
    {
      "type": "Microsoft.Insights/components",
      "apiVersion": "2020-02-02",
      "name": "[parameters('appInsightsName')]",
      "location": "[parameters('location')]",
      "kind": "web",
      "dependsOn": [
        "[resourceId('Microsoft.OperationalInsights/workspaces', variables('workspaceName'))]"
      ],
      "properties": {
        "Application_Type": "web",
        "WorkspaceResourceId": "[resourceId('Microsoft.OperationalInsights/workspaces', variables('workspaceName'))]",
        "RetentionInDays": "[parameters('retentionInDays')]",
        "IngestionMode": "LogAnalytics",
        "publicNetworkAccessForIngestion": "Enabled",
        "publicNetworkAccessForQuery": "Enabled"
      },
      "tags": {
        "ManagedBy": "FSI-AgentGov",
        "Compliance": "SOX-404"
      }
    }
  ],
  "outputs": {
    "appInsightsName": {
      "type": "string",
      "value": "[parameters('appInsightsName')]"
    },
    "instrumentationKey": {
      "type": "string",
      "value": "[reference(resourceId('Microsoft.Insights/components', parameters('appInsightsName'))).InstrumentationKey]"
    },
    "connectionString": {
      "type": "string",
      "value": "[reference(resourceId('Microsoft.Insights/components', parameters('appInsightsName'))).ConnectionString]"
    },
    "workspaceId": {
      "type": "string",
      "value": "[resourceId('Microsoft.OperationalInsights/workspaces', variables('workspaceName'))]"
    }
  }
}
```

### Deployment Validation Checklist

After deployment, validate each component:

```powershell
# Test-AgentObservabilityDeployment.ps1

# 1. Verify Application Insights exists and is configured
$appInsights = Get-AzApplicationInsights -ResourceGroupName $ResourceGroupName -Name $appInsightsName
if ($appInsights.RetentionInDays -ne $expectedRetention) {
    Write-Error "Retention mismatch: Expected $expectedRetention, got $($appInsights.RetentionInDays)"
}

# 2. Verify KQL functions are deployed
$functions = Invoke-AzOperationalInsightsQuery `
    -WorkspaceId $workspaceId `
    -Query ".show functions"

$expectedFunctions = @("GetAgentSuccessRate", "GetAgentLatencyP95", "DetectAnomalies")
foreach ($func in $expectedFunctions) {
    if ($functions.Results.Name -notcontains $func) {
        Write-Error "Missing KQL function: $func"
    }
}

# 3. Verify workbooks are deployed
$workbooks = Get-AzResource `
    -ResourceGroupName $ResourceGroupName `
    -ResourceType "Microsoft.Insights/workbooks"

Write-Host "Workbooks deployed: $($workbooks.Count)"

# 4. Verify alert rules are active
$alerts = Get-AzScheduledQueryRule -ResourceGroupName $ResourceGroupName
foreach ($alert in $alerts) {
    Write-Host "Alert: $($alert.Name) - Enabled: $($alert.Enabled)"
    if (-not $alert.Enabled) {
        Write-Warning "Alert $($alert.Name) is disabled"
    }
}

# 5. Test KQL query execution
Write-Host "Testing KQL query execution..."
$testQuery = "customEvents | take 10"
$testResult = Invoke-AzOperationalInsightsQuery `
    -WorkspaceId $workspaceId `
    -Query $testQuery

if ($testResult.Results.Count -eq 0) {
    Write-Warning "No telemetry data found. Verify Copilot Studio agents are configured with connection string."
}

Write-Host "Deployment validation complete!"
```

---

## Suggested Build Order Based on Dependencies

### Phase 1: Foundation (Weeks 1-2)

**Goal:** Establish core telemetry infrastructure.

**Components:**
1. Application Insights resource (ARM template)
2. Log Analytics workspace (automatically created with App Insights)
3. RBAC role assignments (operations vs. compliance)
4. Basic KQL query library (5-10 core queries)

**Validation:**
- Application Insights connection string obtained
- Test Copilot Studio agent configured with connection string
- Telemetry flowing into `customEvents` table
- Operations team can query Log Analytics

**Dependencies:** None (foundational)

### Phase 2: Operational Monitoring (Weeks 3-4)

**Goal:** Enable real-time operational dashboards and alerts.

**Components:**
1. Azure Monitor Workbooks (operational dashboards)
   - Zone 3 Operations Workbook
   - Zone 2 Team Agents Workbook
   - Troubleshooting Guide (TSG) Workbook
2. Alert rules (critical and warning)
   - Success rate alerts
   - Latency alerts
   - Exception alerts
3. Action groups (Teams, email, ServiceNow)

**Validation:**
- Operations team can view workbooks
- Test alert fires when simulated
- Teams notification received

**Dependencies:**
- Phase 1 complete (Application Insights with telemetry)

### Phase 3: Compliance Integration (Weeks 5-6)

**Goal:** Integrate with Compliance Dashboard and establish audit trail.

**Components:**
1. Continuous Export to ADLS Gen2 (immutable storage)
2. Compliance-focused KQL queries
3. Compliance Audit Workbook (separate from operational)
4. Power Automate flow: Application Insights → Dataverse Compliance Hub
5. SoD RBAC enforcement (remove operations team access to ADLS)

**Validation:**
- Compliance team can query ADLS (not Application Insights)
- Operations team CANNOT access ADLS
- Compliance Dashboard shows Control 3.2 metrics from App Insights

**Dependencies:**
- Phase 1 complete (Application Insights)
- Existing Compliance Dashboard deployed (from FSI-AgentGov-Solutions)

### Phase 4: Advanced Analytics (Weeks 7-8)

**Goal:** Power BI dashboards and executive reporting.

**Components:**
1. Power BI semantic model (star schema)
2. DirectQuery connection for operational dashboard
3. Import connection for compliance dashboard
4. DAX measures for compliance scoring
5. Row-level security (RLS) configuration
6. Executive Summary dashboard

**Validation:**
- Operational dashboard refreshes in real-time (DirectQuery)
- Compliance dashboard refreshes daily (Import)
- RLS enforces zone-based access
- Executives can view summary without raw data access

**Dependencies:**
- Phase 2 complete (operational monitoring)
- Phase 3 complete (compliance data export)

### Phase 5: Automation and Optimization (Weeks 9-10)

**Goal:** Automated remediation and cost optimization.

**Components:**
1. Azure Functions for auto-remediation (e.g., disable failing agents)
2. Dynamic alert thresholds (machine learning-based)
3. Cost optimization (sampling, aggregation tables)
4. Cross-environment correlation (multi-workspace queries)
5. Anomaly detection queries (ML-enhanced KQL)

**Validation:**
- Auto-remediation function triggers on alert
- Dynamic thresholds adapt to agent behavior
- Cost reduced by 30% via sampling (target)

**Dependencies:**
- Phase 2 complete (alert rules and action groups)
- 30 days of historical data for ML training

### Dependency Graph

```
Phase 1 (Foundation)
    ↓
    ├──► Phase 2 (Operational Monitoring)
    │         ↓
    │         └──► Phase 5 (Automation)
    │
    └──► Phase 3 (Compliance Integration)
              ↓
              └──► Phase 4 (Advanced Analytics)
```

**Critical Path:** Phase 1 → Phase 3 → Phase 4 (for compliance dashboards)
**Parallel Path:** Phase 2 → Phase 5 (for operational optimization)

---

## Integration Points with Existing FSI-AgentGov Solutions

### 1. Environment Lifecycle Management (ELM)

**ELM Solution:** Automates environment provisioning with zone classification.

**Integration:**
- ELM provisions new environments with Application Insights pre-configured
- Zone tag from ELM determines retention policy (Zone 3 = 365 days, Zone 1/2 = 90 days)
- Application Insights connection string stored in environment variable

**Shared Components:**
- PowerShell authentication pattern (Connect-AzAccount)
- Dataverse schema for environment metadata

**Data Flow:**
```
ELM creates environment
    ↓
ELM creates Application Insights resource (using Agent Observability ARM template)
    ↓
ELM stores connection string in Dataverse fsi_environment table
    ↓
Agent Observability queries Dataverse for environment list
```

### 2. Message Center Monitor

**Message Center Monitor:** Polls M365 Message Center for platform changes.

**Integration:**
- Both solutions use Dataverse for operational data
- Both use Teams notifications for alerts
- Shared authentication pattern (service principal + Azure Key Vault)

**Complementary Functionality:**
- Message Center Monitor: Platform-level changes
- Agent Observability: Agent-level performance

**No direct data exchange** (solutions operate independently).

### 3. Deny Event Correlation Report

**Deny Event Correlation Report:** Batch extraction of deny events from Purview, DLP, Application Insights.

**Integration:**
- **Shared Data Source:** Both query Application Insights for RAI content filtering events
- **Shared KQL Queries:** Agent Observability KQL library includes deny event queries used by Deny Event Correlation Report
- **Complementary Cadence:** Deny Event Correlation runs daily (batch), Agent Observability monitors real-time

**Shared KQL Query Example:**
```kql
// kql/compliance-queries/rai-content-filtered.kql
// Used by both solutions
customEvents
| where name == "ContentFiltered"
| extend
    AgentId = tostring(customDimensions.recipientName),
    Reason = tostring(customDimensions.filterReason)
| summarize Count = count() by AgentId, Reason, bin(timestamp, 1h)
```

### 4. Compliance Dashboard

**Compliance Dashboard:** Unified compliance reporting across 62 controls.

**Integration:**
- **Data Flow:** Application Insights → Power Automate → Dataverse `fsi_compliancescore` table → Compliance Dashboard
- **Control 3.2 Metrics:** Agent success rate, latency, exception rate calculated from Application Insights
- **Evidence Storage:** Workbook screenshots and KQL query results stored in `fsi_complianceevidence` table

**Power Automate Flow (New):**
```
Trigger: Daily recurrence (8 AM)
    ↓
Query Application Insights (KQL: GetAgentSuccessRate)
    ↓
Calculate Control 3.2 compliance score (>95% = Compliant)
    ↓
Upsert to Dataverse fsi_compliancescore table
    ↓
Log evidence link to Application Insights workbook
```

### 5. Scope Drift Monitor

**Scope Drift Monitor:** Detects agent data access beyond declared scope.

**Integration:**
- Both solutions query Unified Audit Log for agent activity
- Scope Drift Monitor focuses on connector/site access
- Agent Observability focuses on performance/availability

**Potential Future Integration:**
- Agent Observability could surface scope drift anomalies (e.g., sudden access to new connector)
- Shared anomaly detection KQL patterns

**No direct data exchange in v1.**

### 6. Shared Infrastructure Components

| Component | Used By | Purpose |
|-----------|---------|---------|
| **Azure Key Vault** | All solutions | Store Application Insights connection strings, tenant IDs, service principal secrets |
| **Dataverse** | ELM, Compliance Dashboard, Scope Drift Monitor, Agent Observability (via Power Automate) | Operational metadata, compliance scores |
| **Power Automate** | Message Center Monitor, Compliance Dashboard, Agent Observability | Orchestration and data transformation |
| **Teams** | Message Center Monitor, Agent Observability | Notifications and alerts |
| **Entra ID Authentication** | All solutions | Service principal + Managed Identity for automation |

---

## Compliance and Regulatory Alignment

### FINRA 4511 (Recordkeeping)

**Requirement:** Maintain records of AI agent interactions.

**Agent Observability Support:**
- Application Insights stores conversation telemetry (90-365 days)
- Continuous Export to ADLS provides 7-year retention
- Immutable blob storage prevents tampering
- KQL queries provide audit trail of who accessed data

### SEC 17a-3/4 (Records Retention)

**Requirement:** 7-year retention for customer-facing systems.

**Agent Observability Support:**
- ADLS Gen2 with 7-year retention policy
- Append-only blob storage (WORM)
- Correlation IDs link multi-turn conversations
- Export format: JSON (machine-readable for examination)

### SOX 404 (Internal Controls)

**Requirement:** Demonstrate internal control effectiveness.

**Agent Observability Support:**
- SoD enforcement (operations vs. compliance paths)
- RBAC audit trail (Azure Activity Log)
- Control 3.2 compliance scoring (automated calculation)
- Quarterly compliance attestation reports (Power BI)

### GLBA 501(b) (Safeguards)

**Requirement:** Protect customer information systems.

**Agent Observability Support:**
- Real-time alerting on security events (RAI content filtering, XPIA)
- Exception monitoring for system failures
- Performance monitoring ensures availability (99.9% SLA)

---

## Sources

**Official Microsoft Documentation (HIGH Confidence):**

- [Capture telemetry with Application Insights - Microsoft Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-bot-framework-composer-capture-telemetry)
- [Application Insights telemetry with Microsoft Copilot Studio - Dynamics 365](https://learn.microsoft.com/en-us/dynamics365/guidance/resources/copilot-studio-appinsights)
- [Azure Monitor workbooks and Azure Resource Manager templates](https://learn.microsoft.com/en-us/azure/azure-monitor/visualize/workbooks-automate)
- [Create workbook parameters - Azure Monitor](https://learn.microsoft.com/en-us/azure/azure-monitor/visualize/workbooks-parameters)
- [Types of Azure Monitor alerts](https://learn.microsoft.com/en-us/azure/azure-monitor/alerts/alerts-types)
- [Create Azure Monitor alert rules using CLI, PowerShell, or ARM template](https://learn.microsoft.com/en-us/azure/azure-monitor/alerts/alerts-create-rule-cli-powershell-arm)
- [Query across resources with Azure Monitor](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/cross-workspace-query)
- [Semantic model modes in Power BI service](https://learn.microsoft.com/en-us/power-bi/connect-data/service-dataset-modes-understand)
- [Use DirectQuery in Power BI Desktop](https://learn.microsoft.com/en-us/power-bi/connect-data/desktop-use-directquery)

**Community Resources (MEDIUM Confidence):**

- [Integrating Azure Application Insights with Microsoft Copilot Studio for Enhanced Monitoring](https://fusiondevblogs.com/Production/2024-07-28-Copilot-Application-Insights/)
- [Using KQL in Azure for Application Monitoring and Insights](https://www.cloudthat.com/resources/blog/using-kql-in-azure-for-application-monitoring-and-insights)
- [Segregation of Duties (SoD) Risks to Address in 2026](https://www.zluri.com/blog/segregation-of-duties-risks)

**Existing FSI-AgentGov Solutions (HIGH Confidence):**

- FSI-AgentGov-Solutions: Message Center Monitor v2.1.1
- FSI-AgentGov-Solutions: Deny Event Correlation Report v1.1.0
- FSI-AgentGov-Solutions: Compliance Dashboard v1.0.0
- FSI-AgentGov Control 3.2: Usage Analytics and Activity Monitoring

---

*Research completed: February 5, 2026*
*Confidence: HIGH (verified with official Microsoft documentation and existing FSI-AgentGov patterns)*
