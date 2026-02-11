# Phase 1 Research: Workbook Template & KQL

**Project:** Agent Usage & Performance Workbook (v13)
**Phase:** 1 — Workbook Template & KQL
**Researched:** 2026-02-11
**Overall Confidence:** HIGH

---

## 1. Existing Patterns

### 1.1 Workbook Templates Already in the Repo

The Agent 365 Observability Foundation (v3 deliverable) includes **5 workbook JSON templates** embedded inline in [application-insights-workbooks.md](../../docs/playbooks/advanced-implementations/agent-365-observability/application-insights-workbooks.md):

| # | Workbook | Tabs/Sections | JSON Location |
|---|----------|---------------|---------------|
| 1 | Agent Performance Overview | Latency trend (P50/P95/P99), success rate by agent, interaction volume, tool/connector performance | Inline JSON in markdown (~L28-L130) |
| 2 | Interaction Analytics | Top topics, fallback rate trend, human handoff analysis, usage by hour, DAU trend | Inline JSON in markdown (~L140-L215) |
| 3 | Security & Compliance | RAI filter summary, RAI filter trend, DLP blocks, access denials, auth failures, compliance timeline | Inline JSON in markdown (~L225-L315) |
| 4 | Sponsor Accountability | Agents by sponsor, attestation compliance, sponsor activity | Inline JSON in markdown (~L320-L380) |
| 5 | Incident Investigation | Parameterized correlation ID tracing across traces/requests/dependencies/exceptions | Inline JSON in markdown (~L385-L435) |

**Key structural patterns from these templates:**

- All use `"version": "Notebook/1.0"` as the root
- Inline `items[]` array with types: `1` (markdown), `3` (KQL query), `9` (parameters)
- Time range parameter uses `type: 4` with `durationMs`
- Multi-select filters use `type: 2` with KQL-populated dropdowns
- All queries target the `traces` table with custom dimension filtering
- No `fallbackResourceIds` or `$schema` set in existing inline templates

**Gap:** These workbooks target the **Agent 365 SDK / OpenTelemetry** telemetry schema (custom `traces` events like `agent.interaction`, `topic.triggered`, `tool.invocation`, etc.) — NOT native Copilot Studio Application Insights telemetry. The new workbook must target the **native Copilot Studio schema** (`customEvents` table with events like `BotMessageReceived`, `BotMessageSend`, `TopicStart`, etc.).

### 1.2 KQL Queries Already in the Codebase

**v3 Research ARCHITECTURE.md** contains 14+ KQL query patterns organized as:

| Category | Queries | Table(s) | Purpose |
|----------|---------|----------|---------|
| Base queries | `agent-success-rate.kql`, `agent-latency-p95.kql`, `agent-exceptions.kql`, `agent-conversation-volume.kql` | `customEvents` | Core operational metrics |
| Compliance queries | `deny-events-by-agent.kql`, `rai-content-filtered.kql`, `zone3-conversation-audit.kql`, `topic-usage-summary.kql` | `customEvents` | Compliance evidence |
| Anomaly detection | `latency-spike-detection.kql`, `error-rate-anomaly.kql`, `conversation-volume-anomaly.kql` | `customEvents` | Operational health |
| Cross-workspace | `multi-environment-correlation.kql`, `tenant-wide-usage.kql` | `customEvents` | Enterprise scale |

**Alert rule KQL patterns** in alerting-configuration.md:

- High response latency (P95 threshold)
- Low success rate (<95%)
- High fallback rate (>20%)
- RAI content filter events (>5/day)
- DLP blocks (>3/day)
- Authentication failures (>5/hour)

**Note:** These queries were designed conceptually but never extracted into standalone `.kql` files; they exist only inline in documentation. The planned directory structure (`agent-observability-foundation/application-insights/kql/`) was documented but never created.

### 1.3 Workbook JSON Structure (from v3 Architecture Research)

The v3 ARCHITECTURE.md documents the complete Azure Monitor Workbook JSON schema:

```
ARM Template Resource
  └─ properties.serializedData (JSON string)
       └─ version: "Notebook/1.0"
       └─ items[]: array of workbook steps
       │    ├─ type 1: Markdown text
       │    ├─ type 3: KQL query + visualization
       │    ├─ type 9: Parameter controls
       │    └─ type 10: Link to another workbook
       └─ fallbackResourceIds[]: Application Insights resource ID
       └─ isLocked: boolean
```

Item type 3 (KQL query) structure:
```json
{
  "type": 3,
  "content": {
    "version": "KqlItem/1.0",
    "query": "<KQL query text>",
    "size": 0,
    "timeContext": { "durationMs": 86400000 },
    "queryType": 0,
    "resourceType": "microsoft.insights/components",
    "visualization": "timechart|barchart|table|tiles|piechart"
  }
}
```

### 1.4 Solutions Catalog Format

From [solutions-index.md](../../docs/reference/solutions-index.md), each solution entry follows this pattern:

```markdown
### Solution Name

Description paragraph.

**Components:**
- Bullet list of components

**Related Controls:** Cross-reference links
**Repository Link:** GitHub link
```

The solutions table includes columns: Solution | Version | Status | Description | Related Controls.

---

## 2. Control Context

### 2.1 Control 3.2 — Usage Analytics and Activity Monitoring

**Objective:** Comprehensive monitoring of AI agent usage, performance, and activity patterns through PPAC dashboards, alerts, and audit integration.

**Key capabilities this workbook addresses:**
- PPAC Monitor section (overview, alerts, logs, Copilot Studio Dashboard)
- Agent Dashboard (GA Ignite 2025) — centralized agent adoption measurement
- Action Usage Analytics (GA November 2025) — connector/API tracking per agent
- Copilot Chat Insights — expanded availability February 2026
- New Usage Page (PPAC) — Preview January 2026

**Custom Power BI pipeline documented:** Dataverse → Synapse Link → Azure Data Lake → Power BI — but framed as optional scale-up, not primary analytics path.

**Gap this workbook fills:** Control 3.2 assumes portal access to PPAC Monitor. In ALM environments with separation of duties (Control 2.8), production environment access is restricted. The workbook provides read-only monitoring through Application Insights RBAC without requiring PPAC access.

**Daily Monitoring section** references deny event categories (Policy Block, XPIA Detection, Jailbreak Attempt, RAI Content Filter, DLP Match) with zone-based SLAs (Zone 3: 15-minute response).

**Application Insights telemetry warning:** Control 3.2 documents that "Log sensitive activity properties" must be enabled for conversation-level monitoring, and "Allow conversation transcripts" is a tenant-level prerequisite.

### 2.2 Control 3.9 — Microsoft Sentinel Integration

**Objective:** Integrate AI agent monitoring with Microsoft Sentinel SIEM/XDR for enterprise security visibility.

**Three data ingestion pathways:**
1. Power Platform Admin Activity → `PowerPlatformAdminActivity` table
2. Purview Unified Audit Log → `OfficeActivity` table (CopilotInteraction events)
3. Defender CloudAppEvents → `CloudAppEvents` table

**Custom integration path:** Copilot Studio → Application Insights → Log Analytics Workspace → Microsoft Sentinel

**Workbook gap:** Control 3.9 mentions building workbooks for "agent activity visualization and security metrics" but provides no deployable JSON template. The existing guidance is manual creation only.

**Application Insights telemetry detail:**
- Two settings required: "Log activities" (basic sanitized telemetry) + "Log sensitive activity properties" (conversation text, user IDs)
- Without sensitive properties: `customEvents` table shows event occurrences with **empty `text` fields**

### 2.3 Control 2.9 — Agent Performance Monitoring and Optimization

**Objective:** Comprehensive performance monitoring for reliable operation, SLA compliance, and quality management.

**Six monitoring domains:**
1. KPI Definition — response time, error rate, resolution rate, CSAT, containment rate
2. Platform Analytics — Power Platform and Copilot Studio analytics
3. Custom Dashboards — Power BI for executive reporting
4. Alerting Configuration — threshold-based alerts
5. Anomaly Detection — AI-powered anomaly detection for Zone 3
6. Review Cadence — weekly/monthly/quarterly performance reviews

**Built-in vs. custom capabilities:**
| Built-in | Custom Required |
|----------|-----------------|
| Response time metrics | RAI-specific telemetry |
| Error rates | Hallucination tracking |
| CSAT scores | Grounding accuracy metrics |
| Answer quality scores | — |
| Session/conversation counts | — |

**Zone-specific requirements:**
| Zone | Review Frequency | Error Rate Alert | Latency Alert |
|------|-----------------|-----------------|---------------|
| 1 | Monthly | Error rate only | — |
| 2 | Weekly | Error + response time | Standard |
| 3 | Daily + real-time | All metrics + RAI | Real-time |

**Gap this workbook fills:** Control 2.9 requires "Custom Dashboards — Power BI dashboards with KPI cards, trend analysis, and SLA compliance" but offers no out-of-box implementation. The workbook provides an immediate implementation path for all built-in KPIs.

---

## 3. Technical Approach

### 3.1 Workbook JSON Structure

The workbook will use a **tabbed layout** (group items) with three tabs, consistent with Azure Monitor Workbook best practices:

```json
{
  "$schema": "https://github.com/Microsoft/Application-Insights-Workbooks/blob/master/schema/workbook.json",
  "version": "Notebook/1.0",
  "items": [
    { "type": 9, "content": { /* Global parameters: TimeRange, AgentFilter, ChannelFilter */ } },
    { "type": 11, "content": { /* Tab group: Usage/Business Value, Performance/Errors, Operational Health */ } }
  ],
  "fallbackResourceIds": [
    "/subscriptions/{subscription-id}/resourceGroups/{resource-group}/providers/Microsoft.Insights/components/{app-insights-name}"
  ],
  "isLocked": false
}
```

**Tab implementation approach:**

Each tab is a `type: 12` group item (conditionally visible based on tab selector). The tab selector uses a `type: 9` parameter of `type: 2` (dropdown) with static values for tab names.

Alternative (simpler): Use `type: 11` (tabs control) which provides native tab UI. This is preferred for readability and is the modern Azure Workbook approach.

### 3.2 Targeting Native Copilot Studio Telemetry

**Critical distinction:** The existing v3 workbooks target Agent 365 SDK / OpenTelemetry traces (using `traces` table). This new workbook targets **native Copilot Studio Application Insights** telemetry (using `customEvents` table).

**Why `customEvents` and not `traces`:**
- Copilot Studio's native Application Insights integration sends conversation events to `customEvents`
- The SDK-based Agent 365 telemetry (in `traces`) is preview and not yet GA
- Most enterprise FSI organizations use Copilot Studio without Agent 365 SDK
- `customEvents` is the documented, GA telemetry path for Copilot Studio

### 3.3 KQL Query Design Principles

From the v3 ARCHITECTURE.md best practices:

1. **Time filters first** — `| where timestamp > ago(1h)` before other filters
2. **Exclude test conversations** — `| where customDimensions.designMode == "False"` or `| where tobool(customDimensions['designMode']) == false`
3. **Project only needed columns** — minimize memory usage
4. **Parameterize agent/time/channel** — use `{TimeRange}`, `{AgentFilter}`, `{ChannelFilter}` workbook parameters
5. **Comment query intent** — include regulatory reference comments (e.g., `// FINRA 4511: Conversation volume`)
6. **Parse JSON consistently** — use `customDimensions.fieldName` syntax (no `parse_json()` needed in modern workspaces)

### 3.4 Visualization Types by Metric

| Metric | Visualization | Rationale |
|--------|--------------|-----------|
| Session volume over time | `timechart` (area) | Shows trends clearly |
| DAU/MAU | `timechart` (line) | Daily/monthly trend |
| Channel breakdown | `piechart` or `barchart` | Categorical comparison |
| Resolution rates | `tiles` (KPI cards) | At-a-glance status |
| Latency percentiles | `timechart` (multi-line) | P50/P95/P99 on same chart |
| Error rates by type | `barchart` (stacked) | Compare error categories |
| Success rates | `tiles` (with threshold coloring) | Red/yellow/green status |
| Anomaly indicators | `timechart` with `series_decompose_anomalies()` | Statistical anomaly detection |
| Business value estimates | `tiles` (KPI cards) | Executive summary |

---

## 4. Copilot Studio Telemetry Schema

### 4.1 Application Insights Tables

Based on Microsoft documentation (confirmed in v3 Perplexity research):

| Table | What Copilot Studio Sends | Key Fields |
|-------|---------------------------|------------|
| `customEvents` | Conversation events, topic triggers, messages | `name`, `timestamp`, `customDimensions.*` |
| `requests` | Not natively populated by Copilot Studio | — |
| `exceptions` | Runtime exceptions, connector failures | `type`, `message`, `outerMessage` |
| `dependencies` | External API calls (connectors, knowledge sources) | `name`, `target`, `duration`, `success`, `resultCode` |
| `traces` | Not natively populated (Agent 365 SDK only) | — |
| `pageViews` | Web channel conversation starts | `name`, `url`, `timestamp` |

### 4.2 Custom Event Names (Copilot Studio Native)

Confirmed via Perplexity research and Microsoft Dynamics 365 guidance:

| Event Name | Description | When Fired |
|------------|-------------|------------|
| `BotMessageReceived` | User sent a message to the agent | Each user message |
| `BotMessageSend` | Agent sent a response to the user | Each agent response |
| `TopicStart` | A topic was triggered | Topic activation |
| `TopicEnd` | A topic completed | Topic completion |
| `Action` | An action node executed (Power Automate, HTTP, etc.) | Action execution |
| `GenerativeAnswers` | Generative AI was used to formulate a response | Gen AI response |

**Note on naming:** Microsoft uses `BotMessageSend` (not `BotMessageSent`) — confirmed in Perplexity findings.

### 4.3 customDimensions Schema

Each `customEvents` record includes a `customDimensions` JSON bag with:

| Field | Type | Description | Always Present |
|-------|------|-------------|----------------|
| `type` | string | Event type (e.g., "message") | Yes |
| `channelId` | string | Channel: `msteams`, `directline`, `webchat`, `sharepoint` | Yes |
| `fromId` | string | User identifier (GUID) | Yes |
| `fromName` | string | User display name | Only with sensitive properties |
| `recipientId` | string | Bot/agent identifier (GUID) | Yes |
| `recipientName` | string | Agent display name | Yes |
| `text` | string | Message content | Only with sensitive properties enabled |
| `designMode` | string | `"True"` for test canvas, `"False"` for production | Yes |
| `TopicName` | string | Triggered topic name | On `TopicStart`/`TopicEnd` events |
| `Kind` | string | Event kind | Yes |
| `locale` | string | User locale (e.g., "en-us") | Yes |
| `session_Id` | string | Session identifier for conversation grouping | Yes |

### 4.4 Sensitive Properties Warning

Two settings must be enabled for full telemetry:

| Setting | Location | What It Enables |
|---------|----------|-----------------|
| Log activities | Copilot Studio > Agent > Settings > Advanced > Application Insights | Basic (sanitized) telemetry — events without text content |
| Log sensitive activity properties | Same location | Conversation text, user IDs, node details in customDimensions |
| Allow conversation transcripts | PPAC > Environment > Settings > Product > Features | Tenant-level prerequisite for storage |

**Without sensitive properties:** Events appear in `customEvents` but `text` field is empty. Session counts, topic triggers, and channel breakdowns still work. Conversation content-dependent queries (hallucination detection, content analysis) will not function.

### 4.5 Channel Identifiers

| Channel ID | Platform | Deployment Method |
|------------|----------|-------------------|
| `msteams` | Microsoft Teams | Published to Teams |
| `directline` | Web Chat / Custom App | DirectLine API |
| `webchat` | Embedded Web Chat | iframe / Web Chat component |
| `sharepoint` | SharePoint | Published to SharePoint site |
| `facebook` | Facebook Messenger | Facebook channel connector |
| `telephony` | Voice / IVR | Telephony channel |

For FSI enterprise scenarios, primary channels are `msteams` and `sharepoint`.

### 4.6 Session and Conversation Tracking

- **Session:** `customDimensions.session_Id` groups all events in a single conversation
- **Conversation start:** First `BotMessageReceived` event in a session
- **Conversation end:** Last event in session (timeout-based, typically 30 minutes inactivity)
- **Resolution:** No explicit "resolved" field — infer from topic completion (`TopicEnd` without escalation)
- **Escalation:** Infer from `Action` events with handoff-related topic names or specific action types
- **User identification:** `customDimensions.fromId` (GUID) — `dcount()` for unique user counts

### 4.7 What Is NOT Available Natively

| Metric | Status | Workaround |
|--------|--------|------------|
| Token/cost per conversation | Not available | Cannot be measured from Copilot Studio telemetry |
| CSAT score | Built-in to Copilot Studio Analytics tab, NOT sent to App Insights | Requires custom topic to log CSAT to App Insights |
| Hallucination detection | Not native | Requires Azure AI Evaluation SDK or custom implementation |
| Grounding accuracy | Not native | Requires custom citation validation logic |
| RAI content filter details | Limited | `GenerativeAnswers` events may indicate filtering, but details require Purview Audit |
| Response latency (precise) | Not directly in `customEvents` | Estimate from timestamp delta between `BotMessageReceived` and `BotMessageSend` pairs |

---

## 5. File Locations

### 5.1 Workbook Template

**Recommended location:** `src/agent-usage-workbook.json`

**Rationale:**
- The `src/` directory already contains solution JSON artifacts (3 existing files: `adaptive-card-caa-alert.json`, `caa-daily-compliance-flow.json`, `caa-provisioning-hook-flow.json`)
- Consistent with existing naming pattern: kebab-case descriptive names
- The companion repo `FSI-AgentGov-Solutions` hosts deployable packages; `src/` in the main repo holds source artifacts

**Alternative considered:** `docs/playbooks/advanced-implementations/agent-365-observability/workbook-agent-usage.json` — rejected because existing workbook templates in that directory are inline in markdown, not standalone files. Adding a standalone file there breaks the pattern.

### 5.2 Deployment Script

**Recommended location:** `scripts/Deploy-AgentUsageWorkbook.ps1`

**Rationale:**
- `scripts/` directory contains PowerShell automation scripts
- Naming convention: PascalCase verb-noun (matches `Start-CAAValidationRunbook.ps1`, `Test-PolicyCompliance.ps1`)
- Includes ARM template deployment or `New-AzApplicationInsightsWorkbook` cmdlet

### 5.3 Documentation

| Document | Location | Purpose |
|----------|----------|---------|
| Deployment guide | `docs/playbooks/advanced-implementations/agent-usage-workbook/index.md` | Prerequisites, deployment, validation |
| Customization guide | `docs/playbooks/advanced-implementations/agent-usage-workbook/customization.md` | Extending tabs, modifying queries |
| ALM scenario doc | `docs/playbooks/advanced-implementations/agent-usage-workbook/alm-scenario.md` | Why workbooks solve ALM visibility gap |

### 5.4 Navigation Integration

Add to `mkdocs.yml` under `Playbooks > Advanced Implementations`:
```yaml
- Agent Usage & Performance Workbook:
  - playbooks/advanced-implementations/agent-usage-workbook/index.md
  - playbooks/advanced-implementations/agent-usage-workbook/customization.md
  - playbooks/advanced-implementations/agent-usage-workbook/alm-scenario.md
```

---

## 6. Risks and Dependencies

### 6.1 Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **Copilot Studio telemetry schema changes** | Medium | High — queries break | Use `customDimensions` bag accessor pattern (resilient to additions); document minimum schema version |
| **`designMode` field format variation** | Low | Medium — test data pollutes metrics | Always filter with both `== "False"` and `== false` (string and boolean) |
| **No explicit resolution event** | Certain | Medium — resolution rate is estimated | Document estimation logic clearly; use topic completion as proxy |
| **Latency must be estimated** | Certain | Medium — not precise | Calculate from `BotMessageReceived` → `BotMessageSend` timestamp delta; document limitation |
| **Empty `text` without sensitive properties** | Certain (by design) | Low — most metrics still work | Workbook functions without text content; add note that content-based metrics require sensitive properties |
| **Token/cost data unavailable** | Certain | Low — business value tab uses session-based estimates | Use configurable "average minutes saved per session" parameter for ROI calculations |
| **Cross-workspace query limitation** | Medium | Low — most orgs use single workspace | Document limitation; provide guidance for ADX proxy pattern if needed |

### 6.2 Dependencies

| Dependency | Required For | Status |
|------------|-------------|--------|
| Application Insights resource | All workbook functionality | Customer prerequisite |
| Copilot Studio → App Insights connection string | Telemetry flow | Customer prerequisite (documented in Control 3.2) |
| "Log activities" enabled | Basic telemetry | Customer prerequisite |
| "Log sensitive activity properties" enabled | Conversation content queries | Optional (workbook functions without it) |
| Azure Monitor Workbook Reader role | Viewing workbook | Customer RBAC setup |
| Application Insights Reader role | KQL query execution | Customer RBAC setup |
| Azure subscription | Workbook deployment | Customer prerequisite |

### 6.3 Compatibility

| Component | Minimum Version | Notes |
|-----------|-----------------|-------|
| Azure Monitor Workbooks | Current (GA) | No version constraint; stable feature |
| Application Insights | Workspace-based (required) | Classic App Insights deprecated |
| KQL | Current | All queries use standard KQL functions |
| Copilot Studio | GA (current) | Application Insights integration is GA |
| PowerShell Az module | 7.0+ | For deployment script |

---

## 7. Recommended Tab Structure

### Tab 1: Usage & Business Value

**Purpose:** Answer "how much value is the agent delivering?" for leadership reporting.

| # | Visualization | Type | KQL Target | Key Fields |
|---|--------------|------|------------|------------|
| 1 | **Session Volume Trend** | Timechart (area) | `customEvents` | `dcount(session_Id)` by `bin(timestamp, 1d)` |
| 2 | **Daily/Monthly Active Users** | Timechart (dual-axis) | `customEvents` | `dcount(fromId)` by day and by month |
| 3 | **Channel Breakdown** | Piechart | `customEvents` | `count()` by `channelId` |
| 4 | **Top Topics by Engagement** | Barchart (horizontal) | `customEvents` where `name == "TopicStart"` | `count()` by `TopicName`, top 10 |
| 5 | **Resolution Rate** | Tiles (KPI card) | `customEvents` | Ratio of sessions with `TopicEnd` vs total sessions |
| 6 | **Average Messages per Session** | Tiles (KPI card) | `customEvents` | `count()` of `BotMessageReceived` / `dcount(session_Id)` |
| 7 | **Assisted Hours Estimate** | Tiles (KPI card) | `customEvents` | `dcount(session_Id)` × configurable "minutes saved" parameter |
| 8 | **Business Value Summary** | Tiles (4-wide) | Computed | Sessions handled, est. hours saved, est. FTE equivalent, est. cost avoidance |

**KQL pattern for Session Volume:**
```kql
// FINRA 4511: Agent usage volume
customEvents
| where timestamp {TimeRange}
| where customDimensions.designMode == "False"
| where customDimensions.recipientName in ({AgentFilter}) or '*' in ({AgentFilter})
| where customDimensions.channelId in ({ChannelFilter}) or '*' in ({ChannelFilter})
| extend sessionId = tostring(customDimensions.session_Id)
| summarize Sessions = dcount(sessionId) by bin(timestamp, 1d)
| render areachart
```

**KQL pattern for Business Value:**
```kql
// Business value estimation
let MinutesPerSession = {MinutesSaved};  // Configurable parameter (default: 5)
let HourlyRate = {HourlyRate};  // Configurable parameter (default: 75)
customEvents
| where timestamp {TimeRange}
| where customDimensions.designMode == "False"
| where customDimensions.recipientName in ({AgentFilter}) or '*' in ({AgentFilter})
| extend sessionId = tostring(customDimensions.session_Id)
| summarize TotalSessions = dcount(sessionId)
| extend
    EstHoursSaved = round(TotalSessions * MinutesPerSession / 60.0, 1),
    EstFTEEquivalent = round(TotalSessions * MinutesPerSession / 60.0 / 160.0, 2),
    EstCostAvoidance = round(TotalSessions * MinutesPerSession / 60.0 * HourlyRate, 0)
```

### Tab 2: Performance & Errors

**Purpose:** Operational monitoring of agent response quality and reliability.

| # | Visualization | Type | KQL Target | Key Fields |
|---|--------------|------|------------|------------|
| 1 | **Response Latency (P50/P95/P99)** | Timechart (multi-line) | `customEvents` | Timestamp delta between sequential `BotMessageReceived` → `BotMessageSend` pairs |
| 2 | **Error Rate Trend** | Timechart (area) | `exceptions` | `count()` by `bin(timestamp, 1h)` |
| 3 | **Error Types Breakdown** | Barchart (stacked) | `exceptions` | `count()` by `type` or `outerType` |
| 4 | **Connector/Action Success Rate** | Table (grid) | `customEvents` where `name == "Action"` | Success/failure by action name |
| 5 | **Generative AI Usage** | Timechart | `customEvents` where `name == "GenerativeAnswers"` | Volume and trend |
| 6 | **Topic Completion Rate** | Table (grid) | `customEvents` | Ratio of `TopicEnd` to `TopicStart` per topic |
| 7 | **RAI Content Filtering** | Tiles + trend | `customEvents` | Content filter events (if custom telemetry) |
| 8 | **Fallback/Escalation Volume** | Timechart | `customEvents` | Sessions with escalation topics |

**KQL pattern for Estimated Latency:**
```kql
// Response latency estimation
// Approximates latency by measuring time between user message and bot response within same session
customEvents
| where timestamp {TimeRange}
| where customDimensions.designMode == "False"
| where name in ("BotMessageReceived", "BotMessageSend")
| extend
    sessionId = tostring(customDimensions.session_Id),
    eventType = name
| order by sessionId, timestamp asc
| serialize
| extend
    prevEvent = prev(name),
    prevTimestamp = prev(timestamp),
    prevSession = prev(tostring(customDimensions.session_Id))
| where name == "BotMessageSend" and prevEvent == "BotMessageReceived" and sessionId == prevSession
| extend latencyMs = datetime_diff('millisecond', timestamp, prevTimestamp)
| where latencyMs > 0 and latencyMs < 120000  // Filter outliers (>2 min)
| summarize
    P50 = percentile(latencyMs, 50),
    P95 = percentile(latencyMs, 95),
    P99 = percentile(latencyMs, 99)
    by bin(timestamp, 5m)
| render timechart
```

**KQL pattern for Error Types:**
```kql
// Error analysis
exceptions
| where timestamp {TimeRange}
| extend errorType = coalesce(outerType, type, "Unknown")
| summarize
    Count = count(),
    LastSeen = max(timestamp)
    by errorType
| order by Count desc
| render barchart
```

**KQL pattern for Connector Success:**
```kql
// Action/connector success rates
customEvents
| where timestamp {TimeRange}
| where name == "Action"
| where customDimensions.designMode == "False"
| extend
    actionName = tostring(customDimensions.TopicName),
    success = customDimensions.type != "error"
| summarize
    Total = count(),
    Successes = countif(success),
    SuccessRate = round(100.0 * countif(success) / count(), 2)
    by actionName
| order by SuccessRate asc
```

### Tab 3: Operational Health

**Purpose:** Proactive monitoring of anomalies, availability, and compliance events.

| # | Visualization | Type | KQL Target | Key Fields |
|---|--------------|------|------------|------------|
| 1 | **Session Volume Anomaly Detection** | Timechart with anomaly overlay | `customEvents` | `series_decompose_anomalies()` on hourly session counts |
| 2 | **Availability (Uptime Trend)** | Timechart | `customEvents` | Hourly session count — gaps indicate downtime |
| 3 | **Exception Spike Detection** | Timechart with anomaly overlay | `exceptions` | `series_decompose_anomalies()` on hourly exception counts |
| 4 | **Generative Answers Quality** | Tiles (KPI cards) | `customEvents` | GenerativeAnswers event volume, estimated fallback rate |
| 5 | **Dependency Health** | Table (grid) | `dependencies` | External dependency success rates and latency |
| 6 | **DLP/Security Events** | Tiles + table | `customEvents` (custom telemetry) | DLP match events if custom-logged |
| 7 | **Agent Health Summary** | Tiles (per-agent) | Composite | Per-agent: sessions, errors, est. latency — red/yellow/green |

**KQL pattern for Anomaly Detection:**
```kql
// Session volume anomaly detection
let lookback = 14d;
customEvents
| where timestamp > ago(lookback)
| where customDimensions.designMode == "False"
| extend sessionId = tostring(customDimensions.session_Id)
| summarize Sessions = dcount(sessionId) by bin(timestamp, 1h)
| make-series SessionSeries = sum(Sessions) default=0 on timestamp step 1h
| extend (anomalies, score, baseline) = series_decompose_anomalies(SessionSeries, 1.5)
| render anomalychart with (anomalycolumns=anomalies)
```

**KQL pattern for Dependency Health:**
```kql
// External dependency health
dependencies
| where timestamp {TimeRange}
| summarize
    TotalCalls = count(),
    SuccessRate = round(100.0 * countif(success == true) / count(), 2),
    AvgDuration = round(avg(duration), 1),
    P95Duration = round(percentile(duration, 95), 1)
    by name, target
| order by SuccessRate asc
```

### Global Parameters

The workbook will have the following global parameters at the top:

| Parameter | Type | Default | Purpose |
|-----------|------|---------|---------|
| `TimeRange` | Time range picker (type 4) | Last 24 hours | Filter all queries |
| `AgentFilter` | Multi-select dropdown (type 2) | All agents | Filter by agent name |
| `ChannelFilter` | Multi-select dropdown (type 2) | All channels | Filter by channel (Teams, SharePoint, etc.) |
| `MinutesSaved` | Text input (type 1) | 5 | Business value: estimated minutes saved per session |
| `HourlyRate` | Text input (type 1) | 75 | Business value: hourly labor rate for cost calculation |

**Agent filter population query:**
```kql
customEvents
| where customDimensions.designMode == "False"
| distinct tostring(customDimensions.recipientName)
| order by Column1 asc
```

**Channel filter population query:**
```kql
customEvents
| where customDimensions.designMode == "False"
| distinct tostring(customDimensions.channelId)
| order by Column1 asc
```

---

## 8. Implementation Recommendations

### 8.1 Plan A Scope (01-01-PLAN)

Build Tab 1 (Usage & Business Value) and Tab 2 (Performance & Errors):

| Deliverable | File | Format |
|-------------|------|--------|
| Workbook JSON (partial — Tabs 1 & 2) | `src/agent-usage-workbook.json` | Azure Monitor Workbook JSON |

**Estimated query count:** 16 KQL queries (8 per tab) + 3 parameter queries

### 8.2 Plan B Scope (01-02-PLAN)

Build Tab 3 (Operational Health), assemble full template, validate:

| Deliverable | File | Format |
|-------------|------|--------|
| Workbook JSON (complete — all 3 tabs) | `src/agent-usage-workbook.json` | Azure Monitor Workbook JSON |
| Validation results | Plan summary | Pass/fail |

**Estimated query count:** 7 KQL queries + full template assembly and validation

### 8.3 KQL Validation Strategy

Since we cannot connect to a live Application Insights instance, validation will be **structural**:

1. **Schema validation** — All queries reference valid Application Insights tables (`customEvents`, `exceptions`, `dependencies`, `pageViews`)
2. **Field validation** — All `customDimensions.*` fields match documented Copilot Studio schema
3. **Syntax validation** — KQL syntax is valid (no missing operators, proper pipe chains)
4. **Parameter validation** — All `{ParameterName}` references resolve to declared workbook parameters
5. **JSON validation** — Workbook JSON is valid and parseable; all required fields present (`version`, `items`, `fallbackResourceIds`)
6. **Cross-reference validation** — Visualization types match data shapes (e.g., `timechart` with time-binned data)

### 8.4 Differentiation from Existing v3 Workbooks

| Aspect | v3 Observability Workbooks | This Workbook (v13) |
|--------|---------------------------|---------------------|
| **Telemetry source** | Agent 365 SDK (`traces` table) | Copilot Studio native (`customEvents` table) |
| **Event names** | `agent.interaction`, `topic.triggered`, `tool.invocation` | `BotMessageReceived`, `BotMessageSend`, `TopicStart`, `Action` |
| **Target audience** | SDK developers, platform engineers | M365 admins, compliance officers, leadership |
| **Business value** | Not included | Core feature (sessions handled, hours saved, ROI) |
| **Deployment** | Inline in documentation | Standalone JSON template file |
| **ALM scenario** | Not addressed | Primary use case (separation of duties) |
| **Channel analysis** | Not included | Core feature (SharePoint vs Teams breakdown) |

---

*Research completed: 2026-02-11*
*Sources: Repository codebase, v3 ARCHITECTURE.md, v3 PERPLEXITY-FINDINGS.md, v3 STACK.md, Controls 3.2/3.9/2.9, application-insights-workbooks.md, solutions-index.md*
*Confidence: HIGH — all patterns confirmed from existing repo artifacts and Microsoft documentation*
