# Technology Stack: Agent Observability Foundation

**Project:** Agent Observability Foundation
**Researched:** 2026-02-05
**Overall Confidence:** HIGH

## Executive Summary

This stack provides comprehensive AI agent observability for Microsoft 365 / Power Platform in financial services environments. All components are native Microsoft services within the existing M365/Azure ecosystem, minimizing third-party dependencies and maintaining compliance boundaries.

**Key Architecture Decision:** Use Azure Application Insights as the central telemetry hub, with Power BI for executive reporting, Azure Monitor Workbooks for operational dashboards, Viva Insights for adoption metrics, and Microsoft Purview for audit trails.

## Recommended Stack

### Core Telemetry Platform

| Technology | Version | Purpose | Rationale |
|------------|---------|---------|-----------|
| **Azure Application Insights** | Current (OpenTelemetry-based) | Central telemetry repository for agent metrics, traces, and logs | Native integration with Copilot Studio and Power Platform. Stores data in Azure Monitor Logs with 730-day retention. Supports KQL queries for custom analytics. **HIGH confidence** - officially documented integration. |
| **Azure Monitor Logs (Log Analytics)** | Current | Underlying data storage layer for Application Insights | Provides KQL query engine, long-term retention, and RBAC. Required for cross-workspace queries and advanced analytics. **HIGH confidence**. |
| **Kusto Query Language (KQL)** | Current | Query language for telemetry analysis | Industry-standard query language for Azure Monitor. Required for custom queries, workbooks, and alert rules. **HIGH confidence**. |

**Licensing Requirements:**
- Azure subscription required for Application Insights
- Pay-as-you-go pricing based on data ingestion volume (per GB)
- Commitment tiers available starting at 100 GB/day for predictable costs
- No additional license for KQL query capabilities

**Why Application Insights:**
- Native Copilot Studio integration (documented in official Microsoft Learn)
- Automatic collection of conversation data, topic triggers, and custom events
- `customDimensions` field stores agent-specific metadata (designMode, channelId, text, etc.)
- Data flows to `customEvents`, `requests`, and `dependencies` tables
- 5-minute latency from event to queryable data
- OpenTelemetry support for future extensibility

**Integration Points:**
- Copilot Studio: Connect via connection string in Settings → Advanced
- Power Automate: Automatic telemetry export in Managed Environments only
- Power Apps: Model-driven app telemetry via Dataverse integration
- Dataverse: Plug-in telemetry via ILogger interface

### Operational Dashboards

| Technology | Version | Purpose | Rationale |
|------------|---------|---------|-----------|
| **Azure Monitor Workbooks** | Current | Real-time operational health dashboards | Interactive visualizations with parameterization. Can embed KQL queries directly. Supports cross-workspace queries for multi-environment deployments. ARM template deployment for automation. **HIGH confidence**. |

**Licensing Requirements:**
- Included with Azure subscription (no additional cost)
- Requires Reader role on Application Insights resource
- Requires Monitoring Contributor role to create/edit workbooks

**Why Workbooks:**
- Native integration with Application Insights data
- Real-time refresh (no data latency beyond Application Insights ingestion)
- Parameterization for filtering by environment, agent, date range
- Template deployment via ARM templates or PowerShell
- No separate hosting infrastructure required
- GitHub repository with 100+ community templates: [microsoft/Application-Insights-Workbooks](https://github.com/microsoft/Application-Insights-Workbooks)

**Capabilities:**
- Grid visualizations for performance metrics (latency, throughput)
- Time series charts for trend analysis
- Heat maps for usage patterns
- Drill-through to raw telemetry
- Export to Excel or JSON

**Key Limitation:**
- Workbooks are view-only for users without Contributor role
- Cannot schedule automatic exports (use Power Automate for scheduled reporting)

### Executive Reporting

| Technology | Version | Purpose | Rationale |
|------------|---------|---------|-----------|
| **Power BI Premium/Pro** | Current | Executive dashboards and compliance reports | Standard reporting tool in financial services. Semantic models with DAX measures. DirectQuery to Azure Log Analytics for near-real-time data. **HIGH confidence**. |
| **Azure Log Analytics Connector** | Current (Preview) | Power BI data source for Application Insights data | Native connector supporting DirectQuery and Import modes. Uses KQL queries as data source. **MEDIUM confidence** - connector in preview, but officially documented. |

**Licensing Requirements:**
- **Power BI Pro**: $10/user/month (minimum requirement for scheduled refresh and sharing)
- **Power BI Premium**: Required for Azure Log Analytics connector and DirectQuery
  - Premium workspace (P1 or higher) required for Log Analytics integration
  - DirectQuery to Log Analytics requires Premium capacity
- **Azure Log Analytics**: Pay-as-you-go data ingestion pricing

**Why Power BI + Log Analytics Connector:**
- DirectQuery support eliminates data import latency (5-minute delay from Application Insights only)
- KQL queries define data extraction, then DAX measures provide business logic
- Semantic models enable reusable metrics (e.g., "Agent Uptime %", "Average Response Time")
- Row-level security (RLS) for multi-environment deployments
- Scheduled refresh for Import mode (if DirectQuery not available)

**Connection Method:**
```
Power BI Desktop → Get Data → Azure Log Analytics
→ Workspace ID + KQL query → DirectQuery or Import
```

**Key Limitation:**
- Log Analytics connector requires Premium workspace (not available in Pro-only licenses)
- Alternative: Use Azure Data Explorer (ADX) connector with Application Insights proxy
  - ADX connector supports DirectQuery in both Pro and Premium
  - Application Insights data accessible via ADX proxy endpoint

**Recommended Approach:**
- **For Premium customers:** Use Azure Log Analytics connector (DirectQuery)
- **For Pro customers:** Use Azure Data Explorer connector with Application Insights proxy endpoint

### Adoption Metrics

| Technology | Version | Purpose | Rationale |
|------------|---------|---------|-----------|
| **Viva Insights - Copilot Dashboard** | Current (Agent Dashboard GA March 2026) | Agent adoption, retention, and Copilot credit usage | Native Microsoft 365 integration. Provides pre-built adoption metrics without custom development. **HIGH confidence** - officially documented, GA in March 2026. |

**Licensing Requirements:**
- **Minimum 50 assigned licenses** required for data processing (Copilot licenses OR Viva Insights licenses)
- No additional license needed to view dashboard (viewing is free)
- Full feature access with either:
  - 50+ Microsoft 365 Copilot licenses, OR
  - 50+ Viva Insights licenses
- Tenants with <50 Copilot licenses get limited tenant-level metrics only (no group-level filtering)

**Why Viva Insights:**
- **Agent Dashboard** (rolled out publicly January 2026, GA March 2026) provides:
  - Active agents count
  - Active users per agent
  - Agent responses count
  - Copilot credit usage tracking
  - Monthly and weekly user retention trends
  - Top agents by usage
- Covers agents built in Copilot Studio, SharePoint, and Microsoft 365 Agents Toolkit
- Does NOT require custom instrumentation (data collected automatically)
- 28-day rolling window with daily refresh (up to 6-day delay)
- Supports filtering by organization, department, job function, license type

**Key Limitations:**
- **Does NOT track custom-built agents outside Microsoft ecosystem** (e.g., third-party agents)
- Does NOT track Microsoft prebuilt agents or SharePoint agents blocked through Agent 365
- Minimum group size threshold for privacy (groups below threshold not displayed)
- GCC environments have limited features (no team views, no sentiment data)
- Data delay: Up to 7 days for new license assignments to appear

**Data Retention:**
- Previous 28 days (rolling window)
- Historical data cannot be exported beyond 28-day window

**Integration with Application Insights:**
- Viva Insights = High-level adoption metrics (who, how many, how often)
- Application Insights = Deep technical telemetry (errors, latency, conversation flows)
- Complementary, not overlapping

### Alert and Automation

| Technology | Version | Purpose | Rationale |
|------------|---------|---------|-----------|
| **Azure Monitor Alerts** | Current | Proactive failure detection and threshold breaches | Native alerting on Application Insights metrics and logs. Supports metric alerts, log search alerts, and smart detection. **HIGH confidence**. |
| **Action Groups** | Current | Notification and remediation workflows | Routes alerts to email, SMS, Teams, Logic Apps, or Azure Functions. Single action group reusable across multiple alert rules. **HIGH confidence**. |
| **Power Automate** | Current | Custom automation workflows | Orchestrate remediation actions (e.g., create tickets, notify stakeholders, trigger runbooks). Managed Environments enable telemetry correlation. **HIGH confidence**. |

**Licensing Requirements:**
- Azure Monitor Alerts: Included with Azure subscription (pay-per-alert-evaluation pricing)
- Action Groups: Included (pay-per-notification for SMS, webhooks)
- Power Automate: Requires Power Automate Premium for Managed Environments ($15/user/month or $100/flow/month)

**Why Azure Monitor Alerts:**
- **Metric Alerts**: Fast evaluation (1-minute granularity), ideal for latency thresholds
- **Log Search Alerts**: KQL-based conditions, ideal for complex scenarios (e.g., "Alert if >10 agent failures in 5 minutes")
- **Smart Detection Alerts**: AI-powered anomaly detection for Application Insights (automatic, no configuration)
- 30-day alert history retention
- Stateful vs. stateless alert types (control re-firing behavior)

**Alert Rule Types for Agent Scenarios:**

| Scenario | Alert Type | KQL/Metric | Rationale |
|----------|------------|------------|-----------|
| Agent failure rate >5% | Log Search Alert | KQL query on `customEvents` or `requests` table | Requires custom logic to calculate failure rate |
| Response time >3 seconds | Metric Alert | Application Insights → Server Response Time | Fast evaluation, built-in metric |
| Agent conversation volume drop | Metric Alert with Dynamic Thresholds | Application Insights → Custom Events count | Adapts to normal usage patterns |
| Specific error pattern | Log Search Alert | KQL query filtering `exceptions` table | Requires text matching or error code logic |
| Anomaly detection | Smart Detection Alert | Automatic (no query needed) | Zero-config, ML-based anomaly detection |

**Action Group Patterns:**

| Scenario | Actions | Rationale |
|----------|---------|-----------|
| Critical failure (production agent down) | Email + SMS + Teams webhook + Power Automate (create incident) | Multi-channel notification, automatic ticketing |
| Performance degradation (latency spike) | Email + Power Automate (scale resources) | Notification + remediation |
| Threshold breach (usage quota) | Email + Logic App (update capacity) | Notification + capacity management |
| Anomaly detected | Email + Teams webhook | Awareness, manual investigation |

**Power Automate Integration:**
- Managed Environments requirement: Power Automate telemetry ONLY flows to Application Insights in Managed Environments
- Telemetry table structure:
  - Cloud flow runs → `requests` table
  - Cloud flow triggers/actions → `dependencies` table
- `operation_Id` field enables correlation between agent conversation and triggered flows
- 24-hour SLA for telemetry delivery (not real-time)

**Key Limitation:**
- Power Automate telemetry NOT available in GCC, GCC High, or DoD sovereign clouds
- Telemetry is "not 100% lossless" (small data losses may occur due to service issues)
- Use Power Automate run history as authoritative source (Application Insights is supplementary)

### Compliance and Audit

| Technology | Version | Purpose | Rationale |
|------------|---------|---------|-----------|
| **Microsoft Purview Audit Logs** | Current (Audit Standard) | Regulatory audit trail for agent activities | Automatic logging of Copilot Studio agent interactions. Required for FINRA 4511, SEC 17a-4, SOX 302/404 compliance. **HIGH confidence**. |
| **Microsoft Purview Compliance Portal** | Current | Centralized audit log search and export | UI and API access to audit logs. Retention policies, legal hold, eDiscovery integration. **HIGH confidence**. |

**Licensing Requirements:**
- **Audit (Standard)**: Included with Microsoft 365 E3/E5 (no additional cost)
- Microsoft Copilot Studio activities included in Audit Standard
- Non-Microsoft AI applications use pay-as-you-go billing (180-day retention)
- **Audit (Premium)**: Optional upgrade for 10-year retention and advanced hunting (requires E5 Compliance license)

**Why Purview Audit Logs:**
- **Automatic audit logging** for Copilot Studio (enabled by default, no configuration)
- Admin activities logged: Plugin management, tenant settings, promptbook enablement
- User activities logged: Agent interactions with AgentId, AgentName, AgentVersion
- Custom Copilot Studio agents tracked with format: `CopilotStudio.Declarative.[GUID]` or `CopilotStudio.CustomEngine.[GUID]`
- Regulatory-grade audit properties:
  - `AccessedResources`: Files/documents with sensitivity labels and DLP policies
  - `XPIADetected`: Cross Prompt Injection Attack detection
  - `JailbreakDetected`: Prompt injection attempt detection
  - `SensitivityLabelId`: Data classification tracking
  - `PolicyDetails`: Blocked/restricted access events
  - `ModelTransparencyDetails`: AI model name, version, provider

**Audit Log Search:**
- Microsoft Purview portal → Audit → Search by Operation, RecordType, Workload
- Office 365 Management API for programmatic access
- Export to CSV, JSON, or Power BI for offline analysis

**Retention Periods:**
- Microsoft applications (including Copilot Studio): 90 days (Standard) or 10 years (Premium)
- Non-Microsoft AI applications: 180 days (pay-as-you-go)

**Key Limitations:**
- **Does NOT log Microsoft prebuilt agents** (e.g., Microsoft Sales Copilot, Microsoft Service Copilot)
- **Does NOT log SharePoint agents** even when blocked through Agent 365
- Audit logs reflect "who did what" but NOT deep conversation content (use Application Insights for conversation logs)

**Compliance Mapping:**

| Regulation | Requirement | How Purview Audit Logs Support |
|------------|-------------|-------------------------------|
| **FINRA 4511** | Retention of books and records | Audit logs capture agent deployment, modification, and deletion events |
| **FINRA 3110** | Supervision of agent outputs | Logs capture agent interactions; export to supervision queue (use FSI-AgentGov FINRA Supervision Workflow solution) |
| **SEC 17a-3/4** | Recordkeeping for communications | Audit logs capture agent conversations as business records |
| **SOX 302/404** | Internal controls over financial reporting | Audit logs provide evidence of access controls and change management |
| **GLBA 501(b)** | Safeguards for customer information | Audit logs track access to sensitive data via `AccessedResources` field |
| **OCC 2011-12** | Supervisory guidance on model risk | Audit logs capture model version and provider via `ModelTransparencyDetails` |
| **Fed SR 11-7** | Guidance on model risk management | Audit logs provide model lineage and change history |
| **GDPR Art 22** | Right to explanation for automated decisions | Audit logs capture model details and decision context |

**Integration with Application Insights:**
- Purview Audit Logs = Immutable compliance record (who, when, what agent)
- Application Insights = Operational telemetry (how agent performed, errors, latency)
- Complementary, not overlapping
- Use audit log `AgentId` to correlate with Application Insights `customDimensions['resourceId']`

## Supporting Libraries and Tools

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| **Azure Monitor OpenTelemetry Distro** | Current (recommended for .NET, Java, Node.js, Python) | Custom instrumentation for agents with embedded logic | When building custom agents outside Copilot Studio (e.g., Azure Functions, Bot Framework). Provides automatic tracing, metrics, and logs. |
| **Application Insights JavaScript SDK** | Current | Client-side telemetry for web-based agents | When deploying agents in web applications. Captures client-side errors, page views, and user interactions. |
| **Power BI REST API** | Current | Programmatic report generation and distribution | When automating report delivery to stakeholders (e.g., weekly compliance reports). Requires Power BI Premium. |
| **Microsoft Graph API** | Current | Programmatic access to Purview audit logs | When building custom compliance dashboards or exporting audit data to SIEM systems. Requires appropriate Graph API permissions. |
| **Azure CLI / Azure PowerShell** | Current | Infrastructure-as-code deployment | When deploying Application Insights, Workbooks, and Alert Rules via CI/CD pipelines. |

## Alternatives Considered

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| Telemetry Platform | Azure Application Insights | Dataverse Analytics | Dataverse Analytics does not natively capture Copilot Studio conversation telemetry. Requires custom development to log events. Application Insights provides out-of-the-box integration. |
| Telemetry Platform | Azure Application Insights | Azure Data Explorer (ADX) | ADX is lower-level and requires custom ingestion pipelines. Application Insights provides native integrations and is the recommended approach per Microsoft documentation. Use ADX only when Application Insights data retention (730 days) is insufficient. |
| Operational Dashboards | Azure Monitor Workbooks | Power BI | Power BI requires data refresh latency (Import mode) or Premium licenses (DirectQuery). Workbooks provide real-time views at no additional cost. Use Power BI for executive reporting, Workbooks for operational dashboards. |
| Operational Dashboards | Azure Monitor Workbooks | Grafana | Grafana requires separate hosting infrastructure and lacks native RBAC integration with Azure resources. Workbooks are fully managed and integrate with Azure AD. Use Grafana only when cross-cloud monitoring is required (AWS + Azure). |
| Adoption Metrics | Viva Insights | Custom Power BI dashboard | Custom dashboards require building adoption data pipelines from scratch (Graph API, usage logs). Viva Insights provides pre-built metrics with no development effort. Use Viva Insights unless custom metrics beyond adoption are required. |
| Alerting | Azure Monitor Alerts | Third-party APM (Datadog, New Relic) | Third-party APM tools introduce data egress costs and compliance risk (data leaves Microsoft ecosystem). Azure Monitor Alerts is native, compliant, and cost-effective. Use third-party APM only when monitoring non-Azure infrastructure. |
| Audit Logs | Microsoft Purview | SIEM (Splunk, QRadar) | SIEM systems require exporting audit logs via API, increasing complexity and cost. Purview provides native search and retention. Export to SIEM only when cross-system correlation is required (e.g., correlating agent activity with network logs). |

## Installation and Configuration

### 1. Core Telemetry Platform (Application Insights)

**Prerequisites:**
- Azure subscription
- Contributor role on resource group
- Copilot Studio admin role

**Create Application Insights instance:**
```powershell
# Create Application Insights resource
az monitor app-insights component create \
  --app FSI-AgentGov-Observability \
  --location eastus \
  --resource-group FSI-AgentGov-RG \
  --workspace /subscriptions/{subscription-id}/resourceGroups/{rg}/providers/Microsoft.OperationalInsights/workspaces/{workspace}

# Get connection string
$connectionString = az monitor app-insights component show \
  --app FSI-AgentGov-Observability \
  --resource-group FSI-AgentGov-RG \
  --query connectionString -o tsv
```

**Connect Copilot Studio agents:**
1. Navigate to agent → Settings → Advanced
2. In "Application Insights" section, paste connection string
3. Enable "Log activities" (logs incoming/outgoing messages)
4. Enable "Log sensitive Activity properties" (includes user IDs, names, text) **only if required for compliance**

**Connect Power Automate (Managed Environments only):**
1. Navigate to Power Platform Admin Center → Environments
2. Enable Managed Environment for target environment
3. Navigate to Settings → Integrations → Application Insights
4. Paste connection string
5. Telemetry flows automatically (24-hour SLA)

**Data retention configuration:**
```powershell
# Set retention to 730 days (maximum for Application Insights)
az monitor app-insights component update \
  --app FSI-AgentGov-Observability \
  --resource-group FSI-AgentGov-RG \
  --retention-time 730
```

### 2. Operational Dashboards (Azure Monitor Workbooks)

**Deploy workbook via ARM template:**
```powershell
# Deploy workbook ARM template
New-AzResourceGroupDeployment `
  -ResourceGroupName FSI-AgentGov-RG `
  -TemplateFile ./workbook-template.json `
  -TemplateParameterFile ./workbook-parameters.json
```

**Sample workbook template structure:**
- See [microsoft/Application-Insights-Workbooks](https://github.com/microsoft/Application-Insights-Workbooks) for reference templates
- Customize queries to filter by agent ID, environment, date range

### 3. Executive Reporting (Power BI)

**Connect to Azure Log Analytics:**

**Option A: Premium customers (DirectQuery)**
1. Power BI Desktop → Get Data → Azure Log Analytics
2. Enter Workspace ID (from Application Insights resource)
3. Write KQL query to extract agent metrics
4. Select DirectQuery mode
5. Publish to Premium workspace

**Option B: Pro customers (ADX connector)**
1. Power BI Desktop → Get Data → Azure Data Explorer
2. Enter Application Insights ADX proxy endpoint:
   ```
   https://ade.applicationinsights.io/subscriptions/{subscription-id}/resourceGroups/{rg}/providers/Microsoft.Insights/components/{appinsights-name}
   ```
3. Write KQL query
4. Select DirectQuery or Import mode

**Sample KQL query for Power BI:**
```kusto
// Agent conversation volume by day
customEvents
| where timestamp > ago(30d)
| extend agentId = tostring(customDimensions['resourceId'])
| extend isDesignMode = tobool(customDimensions['designMode'])
| where isDesignMode == false  // Exclude test conversations
| summarize ConversationCount = count() by bin(timestamp, 1d), agentId
| order by timestamp desc
```

### 4. Adoption Metrics (Viva Insights)

**Prerequisites:**
- Minimum 50 Copilot licenses OR Viva Insights licenses assigned
- Wait 7 days after license assignment for data processing

**Access Copilot Dashboard:**
1. Navigate to Viva Insights → Microsoft Copilot Dashboard
2. Select "Agent Dashboard" tab (available January 2026, GA March 2026)
3. Filter by organization, department, job function, license type
4. Export metrics via Export button (CSV or Excel)

**No configuration required** - data collection is automatic.

### 5. Alert and Automation (Azure Monitor Alerts)

**Create log search alert for agent failures:**
```powershell
# Create action group
$actionGroup = New-AzActionGroup `
  -ResourceGroupName FSI-AgentGov-RG `
  -Name "Agent-Failures-ActionGroup" `
  -ShortName "AgentFail" `
  -EmailReceiver @{Name="SOC";EmailAddress="soc@example.com"}

# Create log search alert rule
$condition = New-AzScheduledQueryRuleCondition `
  -Query "customEvents | where customDimensions['resourceProvider'] == 'Copilot Studio' | where success == false | summarize FailureCount = count() by bin(timestamp, 5m) | where FailureCount > 10" `
  -TimeAggregation "Count" `
  -Threshold 1 `
  -Operator "GreaterThan"

New-AzScheduledQueryRule `
  -ResourceGroupName FSI-AgentGov-RG `
  -Name "Agent-High-Failure-Rate" `
  -Location eastus `
  -DisplayName "Agent Failure Rate >10 in 5min" `
  -Scope /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Insights/components/FSI-AgentGov-Observability `
  -Severity 2 `
  -WindowSize (New-TimeSpan -Minutes 5) `
  -EvaluationFrequency (New-TimeSpan -Minutes 5) `
  -Condition $condition `
  -ActionGroup $actionGroup.Id
```

### 6. Compliance and Audit (Microsoft Purview)

**Prerequisites:**
- Microsoft 365 E3 or E5 license
- Compliance Administrator or Global Administrator role

**Enable auditing (if not already enabled):**
```powershell
# Connect to Security & Compliance PowerShell
Connect-IPPSSession

# Enable audit logging
Set-AdminAuditLogConfig -UnifiedAuditLogIngestionEnabled $true
```

**Search audit logs for Copilot Studio activities:**
1. Navigate to Microsoft Purview portal → Audit
2. Search criteria:
   - Workload: "Microsoft Copilot Studio"
   - Operation: "CopilotInteraction"
   - Date range: Last 90 days (or custom)
3. Export results to CSV

**Programmatic access via Graph API:**
```powershell
# Get audit logs via Graph API
$auditLogs = Invoke-MgGraphRequest -Method GET -Uri "https://graph.microsoft.com/v1.0/auditLogs/directoryAudits?\$filter=activityDisplayName eq 'CopilotInteraction'"
```

## Configuration Matrix by Environment Type

| Environment Type | Application Insights | Workbooks | Power BI | Viva Insights | Purview Audit |
|------------------|---------------------|-----------|----------|---------------|---------------|
| **Development** | Single shared instance | Dev-specific workbook | Optional (Import mode) | Not required | Audit enabled (standard retention) |
| **Test** | Separate instance per test env | Test-specific workbook | Optional | Not required | Audit enabled (standard retention) |
| **Production** | Dedicated instance per zone | Zone-specific workbooks | Required (DirectQuery preferred) | Required | Audit enabled (Premium retention recommended) |
| **Disaster Recovery** | Geo-redundant instance | Replicated workbooks | Replicated reports | Not required | Audit enabled (Premium retention) |

## Licensing Summary

| Component | License Required | Estimated Cost (per month) | Notes |
|-----------|------------------|---------------------------|-------|
| Azure Application Insights | Azure subscription | $2.30/GB ingested + $0.10/GB retained | Commitment tiers available (100 GB/day = ~$230/month) |
| Azure Monitor Workbooks | Azure subscription | Included (no additional cost) | - |
| Power BI Pro | $10/user/month | $10/user | For scheduled refresh and sharing |
| Power BI Premium | P1: $4,995/month | $4,995/capacity | Required for DirectQuery to Log Analytics |
| Viva Insights - Copilot Dashboard | 50+ Copilot licenses OR 50+ Viva Insights licenses | No additional cost | Dashboard viewing is free; data processing requires minimum 50 licenses |
| Microsoft Purview Audit (Standard) | Microsoft 365 E3/E5 | Included | 90-day retention |
| Microsoft Purview Audit (Premium) | Microsoft 365 E5 Compliance | $12/user/month | 10-year retention |
| Power Automate Premium | $15/user/month OR $100/flow/month | $15/user or $100/flow | Required for Managed Environments |
| Azure Monitor Alerts | Azure subscription | $0.10/alert evaluation (first 1M evaluations free) | Pay-per-evaluation pricing |

**Total Estimated Cost for 100-user organization:**
- Application Insights (10 GB/month): $30/month
- Power BI Premium (P1): $4,995/month
- Purview Audit (Premium): $1,200/month (100 users × $12)
- Power Automate Premium: $1,500/month (100 users × $15)
- Azure Monitor Alerts: <$10/month (typically within free tier)
- **Total: ~$7,735/month**

**Cost Optimization Strategies:**
- Use Power BI Pro instead of Premium if DirectQuery not required ($1,000/month for 100 users vs. $4,995/month for Premium)
- Use Application Insights commitment tiers for predictable costs (if ingesting >100 GB/day)
- Use Audit Standard instead of Premium if 90-day retention is sufficient (saves $1,200/month)
- Use Azure Monitor free tier for basic alerting (1M evaluations/month free)

## Technology Maturity Assessment

| Component | Maturity | Release Status | Risk Level |
|-----------|----------|----------------|------------|
| Azure Application Insights | **Stable** | GA (Generally Available) | **Low** |
| Application Insights + Copilot Studio integration | **Stable** | GA | **Low** |
| Azure Monitor Workbooks | **Stable** | GA | **Low** |
| Power BI + Log Analytics connector | **Preview** | Public Preview | **Medium** (use ADX connector as fallback) |
| Viva Insights - Agent Dashboard | **Stable** | GA March 2026 (rolling out January 2026) | **Low** (fully released by milestone timeline) |
| Microsoft Purview Audit Logs | **Stable** | GA | **Low** |
| OpenTelemetry Distro for Azure Monitor | **Stable** | GA for .NET, Java, Node.js, Python | **Low** (recommended over legacy SDKs) |
| Power Automate telemetry in Managed Environments | **Stable** | GA | **Low** (Managed Environment requirement is known) |

## Known Limitations and Workarounds

| Limitation | Impact | Workaround |
|------------|--------|------------|
| Power BI Log Analytics connector requires Premium | Blocks DirectQuery for Pro customers | Use Azure Data Explorer connector with Application Insights proxy endpoint |
| Power Automate telemetry only in Managed Environments | Blocks correlation for non-Managed flows | Migrate to Managed Environments (required by Feb 2026 for pipelines) |
| Viva Insights requires 50+ licenses | Blocks adoption metrics for small deployments | Use custom Power BI dashboard with Graph API (UserAnalytics endpoint) |
| Purview Audit does not log prebuilt agents | Visibility gap for Microsoft prebuilt agents | Document exception in governance framework; monitor via Application Insights if instrumented |
| Application Insights 730-day retention limit | Long-term retention gap for SEC 17a-4 (6 years) | Export audit logs to Azure Data Lake or immutable blob storage; implement retention policy |
| Power Automate telemetry is "not 100% lossless" | Small data losses may occur | Use Power Automate run history as authoritative source; Application Insights is supplementary |
| Smart Detection Alerts cannot be customized | Limited control over anomaly detection sensitivity | Supplement with custom log search alerts for critical scenarios |

## Integration Patterns

### Pattern 1: End-to-End Conversation Tracing

**Use Case:** Trace a user's conversation from Copilot Studio agent → Power Automate flow → Dataverse API call

**Implementation:**
1. Copilot Studio logs conversation to Application Insights with `operation_Id`
2. Power Automate flow (in Managed Environment) logs to Application Insights with same `operation_Id`
3. Dataverse plug-in logs to Application Insights with same `operation_Id`
4. KQL query correlates all events:
   ```kusto
   union customEvents, requests, dependencies
   | where operation_Id == "{guid}"
   | order by timestamp asc
   ```

### Pattern 2: Compliance Reporting Workflow

**Use Case:** Generate weekly compliance report for FINRA 4511 (agent conversation records)

**Implementation:**
1. Power Automate scheduled flow (weekly trigger)
2. Query Purview Audit API for Copilot Studio interactions (last 7 days)
3. Query Application Insights for conversation details (last 7 days)
4. Merge datasets (join on AgentId and timestamp)
5. Generate Power BI report (paginated report for PDF export)
6. Email report to compliance team

### Pattern 3: Real-Time Failure Alerting

**Use Case:** Alert SOC when agent failure rate exceeds 5% in 5-minute window

**Implementation:**
1. Azure Monitor log search alert with KQL query:
   ```kusto
   customEvents
   | where timestamp > ago(5m)
   | extend success = tobool(customDimensions['success'])
   | summarize TotalConversations = count(), Failures = countif(success == false)
   | extend FailureRate = (Failures * 100.0) / TotalConversations
   | where FailureRate > 5
   ```
2. Action group sends email + Teams webhook notification
3. Power Automate flow creates incident in ServiceNow
4. Workbook dashboard updates in real-time for SOC team

### Pattern 4: Executive Adoption Dashboard

**Use Case:** Executive dashboard showing agent adoption, usage trends, and ROI metrics

**Implementation:**
1. Viva Insights Agent Dashboard provides:
   - Active agents count
   - Active users per agent
   - Retention trends
2. Power BI DirectQuery to Application Insights provides:
   - Average conversation duration (DAX measure)
   - Topic distribution (DAX measure)
   - Error rates (DAX measure)
3. Combine datasets in Power BI with calculated columns:
   - ROI = (Time Saved × Hourly Rate) - (Copilot Credit Cost)
4. Publish to Power BI Premium workspace
5. Share with executive stakeholders (view-only access)

## Deployment Checklist

- [ ] Azure subscription created or identified
- [ ] Resource group created: `FSI-AgentGov-RG`
- [ ] Application Insights instance deployed with 730-day retention
- [ ] Copilot Studio agents connected to Application Insights (connection string configured)
- [ ] Power Platform Managed Environments enabled and connected to Application Insights
- [ ] Azure Monitor Workbooks deployed (agent health, conversation volume, error tracking)
- [ ] Power BI workspace created (Premium or Pro depending on DirectQuery requirement)
- [ ] Power BI semantic model created with KQL queries and DAX measures
- [ ] Viva Insights Copilot Dashboard access verified (minimum 50 licenses assigned)
- [ ] Microsoft Purview Audit logging enabled (verify with test search)
- [ ] Azure Monitor alert rules created (failure rate, latency, anomaly detection)
- [ ] Action groups configured (email, SMS, Teams, Power Automate)
- [ ] Power Automate workflows created (compliance reporting, incident creation)
- [ ] Role-based access control (RBAC) configured:
  - Application Insights Reader: SOC team, compliance team
  - Workbooks Contributor: Platform team
  - Power BI Viewer: Executive stakeholders
  - Purview Audit Reader: Compliance team, legal team
- [ ] Data retention policies documented and configured
- [ ] Export automation configured for long-term compliance retention (if required)
- [ ] Disaster recovery plan documented (geo-redundant Application Insights, workbook replication)
- [ ] Cost monitoring configured (Azure Cost Management alerts)

## Next Steps

1. **Phase 1 - Core Telemetry:**
   - Deploy Application Insights
   - Connect Copilot Studio agents
   - Validate telemetry flow with test conversations
   - Create initial KQL queries for baseline metrics

2. **Phase 2 - Operational Monitoring:**
   - Deploy Azure Monitor Workbooks
   - Create alert rules for critical failures
   - Configure action groups for notification routing
   - Integrate with existing incident management system

3. **Phase 3 - Executive Reporting:**
   - Connect Power BI to Application Insights
   - Build semantic model with DAX measures
   - Create executive dashboards (adoption, usage, ROI)
   - Schedule automated report distribution

4. **Phase 4 - Compliance Integration:**
   - Enable Purview Audit logging (if not already enabled)
   - Create compliance reporting workflows (FINRA, SEC, SOX)
   - Configure long-term retention export (if >730 days required)
   - Document audit trail for regulatory exams

5. **Phase 5 - Advanced Capabilities:**
   - Implement end-to-end conversation tracing
   - Create cross-system correlation queries (agent + flow + Dataverse)
   - Build predictive analytics (usage forecasting, capacity planning)
   - Integrate with FSI-AgentGov Compliance Dashboard solution

## Sources

### High Confidence Sources (Official Microsoft Documentation)

- [Capture telemetry with Application Insights - Microsoft Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-bot-framework-composer-capture-telemetry)
- [Overview of integration with Application Insights - Power Platform](https://learn.microsoft.com/en-us/power-platform/admin/overview-integration-application-insights)
- [Set up Application Insights with Power Automate - Power Platform](https://learn.microsoft.com/en-us/power-platform/admin/app-insights-cloud-flow)
- [Application Insights OpenTelemetry observability overview - Azure Monitor](https://learn.microsoft.com/en-us/azure/azure-monitor/app/app-insights-overview)
- [Azure Workbooks overview - Azure Monitor](https://learn.microsoft.com/en-us/azure/azure-monitor/visualize/workbooks-overview)
- [Azure Monitor workbooks and Azure Resource Manager templates](https://learn.microsoft.com/en-us/azure/azure-monitor/visualize/workbooks-automate)
- [Overview of Azure Monitor alerts - Azure Monitor](https://learn.microsoft.com/en-us/azure/azure-monitor/alerts/alerts-overview)
- [Connect to the Microsoft Copilot Dashboard for Microsoft 365 customers - Viva Insights](https://learn.microsoft.com/en-us/viva/insights/org-team-insights/copilot-dashboard)
- [Audit logs for Copilot and AI applications - Microsoft Purview](https://learn.microsoft.com/en-us/purview/audit-copilot)
- [Using Azure Log Analytics in Power BI](https://learn.microsoft.com/en-us/power-bi/transform-model/log-analytics/desktop-log-analytics-overview)
- [Licensing - Managed Environments - Power Platform](https://learn.microsoft.com/en-us/power-platform/admin/managed-environment-licensing)
- [Enable OpenTelemetry in Application Insights - Azure Monitor](https://learn.microsoft.com/en-us/azure/azure-monitor/app/opentelemetry-enable)

### Medium Confidence Sources (Community and Third-Party Documentation)

- [Application Insights telemetry with Microsoft Copilot Studio - Dynamics 365 Guidance](https://learn.microsoft.com/en-us/dynamics365/guidance/resources/copilot-studio-appinsights)
- [Connect to Application Insights and Log Analytics with Direct Query in Power BI](https://whitepages.bifocal.show/2020/06/connect-to-application-insights-and-log-analytics-with-direct-query-in-power-bi/)
- [Phase 5 of Governance and Security best practices: Monitoring and optimization - Microsoft Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/sec-gov-phase5)
- [Measuring for Improvement - Capturing Telemetry in Microsoft Copilot Studio with Azure Application Insights](https://holgerimbery.blog/analytics-with-azure-insights)

### Low Confidence Sources (Require Verification)

- [MC1166852 - Microsoft Viva Copilot Analytics launches new agent dashboard - Message Center Archive](https://mc.merill.net/message/MC1166852) - Message Center announcement, verified by official Learn documentation
- [FINRA Publishes 2026 Regulatory Oversight Report](https://www.finra.org/media-center/newsreleases/2025/finra-publishes-2026-regulatory-oversight-report-empower-member-firm) - FINRA official website
- [Auditing Copilot agent changes with Microsoft Purview - Topedia Blog](https://blog-en.topedia.com/2026/02/auditing-copilot-agent-changes-with-microsoft-purview/) - Community blog, verified by Purview official documentation

## Version History

- **v1.0** (2026-02-05): Initial research compilation with HIGH confidence assessment
