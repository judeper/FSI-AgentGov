# KQL Query Library: Agent Usage & Performance Workbook

**Project:** FSI Agent Governance Framework v15
**Phase:** 1 — Telemetry Research & KQL Query Library
**Plan:** 01-02
**Created:** 2026-02-11
**Source:** v13 Research (`.planning/phases/01-workbook-template-kql/01-RESEARCH.md`)

---

## Overview

This document contains the complete KQL query library powering all 3 workbook tabs (23 parameterized queries + 5 global parameters). Each query targets the **native Copilot Studio Application Insights** telemetry schema (`customEvents`, `exceptions`, `dependencies` tables — NOT the Agent 365 SDK `traces` table).

**Design Principles:**
- Time filters first in every query
- `designMode == "False"` filtering excludes test canvas conversations
- Parameterized with `{TimeRange}`, `{AgentFilter}`, `{ChannelFilter}` workbook parameters
- Regulatory reference comments on every query (FINRA, SEC, SOX, OCC)
- Visualization type annotations for Phase 2 workbook JSON construction
- Outlier guards where applicable (latency < 120000ms, anomaly threshold 1.5)

**Known Limitations (documented throughout):**
- Latency is estimated from timestamp deltas, not precise instrumentation
- Resolution rate is inferred from TopicEnd presence (no explicit field)
- Token/cost data is unavailable from Copilot Studio telemetry
- CSAT is not sent to Application Insights (stays in PPAC Analytics)
- RAI content filter details require Purview Audit, not Application Insights

---

## Global Parameters

### P01: TimeRange

**Type:** Time range picker (type 4)
**Default:** Last 24 hours (86400000 ms)
**Purpose:** Global time filter applied to all queries

No KQL query needed — built-in workbook parameter type.

### P02: AgentFilter

**Type:** Multi-select dropdown (type 2)
**Default:** All agents (wildcard `*`)
**Purpose:** Filter all queries by agent name

```kql
// Parameter population: Available agents
customEvents
| where customDimensions.designMode == "False"
| distinct tostring(customDimensions.recipientName)
| order by Column1 asc
```

### P03: ChannelFilter

**Type:** Multi-select dropdown (type 2)
**Default:** All channels (wildcard `*`)
**Purpose:** Filter all queries by channel (Teams, SharePoint, etc.)

```kql
// Parameter population: Available channels
customEvents
| where customDimensions.designMode == "False"
| distinct tostring(customDimensions.channelId)
| order by Column1 asc
```

### P04: MinutesSaved

**Type:** Text input (type 1)
**Default:** 5
**Purpose:** Estimated minutes saved per agent-handled session (business value calculation)

No KQL query needed — static input parameter.

### P05: HourlyRate

**Type:** Text input (type 1)
**Default:** 75
**Purpose:** Hourly labor rate in USD for cost avoidance calculation

No KQL query needed — static input parameter.

---

## Tab 1: Usage & Business Value

### Q01: Session Volume Trend

**Tab:** Usage & Business Value
**Visualization:** timechart (area)
**Tables:** customEvents
**Parameters:** {TimeRange}, {AgentFilter}, {ChannelFilter}

```kql
// FINRA 4511: Agent usage volume — daily session trend
// SEC 17a-3: Recordkeeping evidence of agent interaction volume
customEvents
| where timestamp {TimeRange}
| where customDimensions.designMode == "False"
| where customDimensions.recipientName in ({AgentFilter}) or '*' in ({AgentFilter})
| where customDimensions.channelId in ({ChannelFilter}) or '*' in ({ChannelFilter})
| extend sessionId = tostring(customDimensions.session_Id)
| summarize Sessions = dcount(sessionId) by bin(timestamp, 1d)
| render areachart
```

**Notes:** Uses `dcount(session_Id)` for distinct session counts. Granularity is 1 day to show long-term adoption trends. For intraday granularity, change `bin(timestamp, 1d)` to `bin(timestamp, 1h)`.

---

### Q02: Daily Active Users

**Tab:** Usage & Business Value
**Visualization:** timechart (line)
**Tables:** customEvents
**Parameters:** {TimeRange}, {AgentFilter}, {ChannelFilter}

```kql
// FINRA 4511: User engagement tracking — daily active users
// OCC 2011-12: Model risk — adoption metrics for agent governance
customEvents
| where timestamp {TimeRange}
| where customDimensions.designMode == "False"
| where customDimensions.recipientName in ({AgentFilter}) or '*' in ({AgentFilter})
| where customDimensions.channelId in ({ChannelFilter}) or '*' in ({ChannelFilter})
| extend userId = tostring(customDimensions.fromId)
| summarize DAU = dcount(userId) by bin(timestamp, 1d)
| render timechart
```

**Notes:** Uses `dcount(fromId)` for unique user counts. `fromId` is a GUID always present regardless of sensitive properties setting.

---

### Q03: Monthly Active Users

**Tab:** Usage & Business Value
**Visualization:** tiles (KPI)
**Tables:** customEvents
**Parameters:** {TimeRange}, {AgentFilter}, {ChannelFilter}

```kql
// FINRA 4511: Adoption measurement — 30-day unique user count
// SOX 302: Agent adoption metrics for management reporting
customEvents
| where timestamp {TimeRange}
| where customDimensions.designMode == "False"
| where customDimensions.recipientName in ({AgentFilter}) or '*' in ({AgentFilter})
| where customDimensions.channelId in ({ChannelFilter}) or '*' in ({ChannelFilter})
| extend userId = tostring(customDimensions.fromId)
| summarize MAU = dcount(userId)
```

**Notes:** KPI tile displays single value. When TimeRange is set to "Last 30 days", this yields the standard MAU metric. For rolling MAU on a timechart, a sliding window query would be needed (not included — KPI tile is sufficient for this use case).

---

### Q04: Channel Breakdown

**Tab:** Usage & Business Value
**Visualization:** piechart
**Tables:** customEvents
**Parameters:** {TimeRange}, {AgentFilter}

```kql
// FINRA 3110: Supervisory compliance — channel distribution visibility
// SEC 17a-4: Communication channel recordkeeping
customEvents
| where timestamp {TimeRange}
| where customDimensions.designMode == "False"
| where customDimensions.recipientName in ({AgentFilter}) or '*' in ({AgentFilter})
| where name == "BotMessageReceived"
| extend channel = tostring(customDimensions.channelId)
| summarize Messages = count() by channel
| render piechart
```

**Notes:** Filters to `BotMessageReceived` events to count inbound user messages per channel. ChannelFilter is intentionally NOT applied here — the purpose of this visualization is to show the distribution across all channels. Primary FSI channels: `msteams`, `sharepoint`, `directline`, `webchat`.

---

### Q05: Top Topics by Engagement

**Tab:** Usage & Business Value
**Visualization:** barchart (horizontal)
**Tables:** customEvents
**Parameters:** {TimeRange}, {AgentFilter}, {ChannelFilter}

```kql
// FINRA 4511: Topic usage analysis — agent capability utilization
// OCC 2011-12: Model inventory — which agent capabilities are most used
customEvents
| where timestamp {TimeRange}
| where customDimensions.designMode == "False"
| where customDimensions.recipientName in ({AgentFilter}) or '*' in ({AgentFilter})
| where customDimensions.channelId in ({ChannelFilter}) or '*' in ({ChannelFilter})
| where name == "TopicStart"
| extend topicName = tostring(customDimensions.TopicName)
| summarize Triggers = count() by topicName
| top 10 by Triggers desc
| render barchart
```

**Notes:** Shows top 10 most frequently triggered topics. `TopicName` is present in `customDimensions` on `TopicStart` and `TopicEnd` events. System topics (e.g., "Greeting", "Escalate", "End of Conversation") will appear unless explicitly filtered.

---

### Q06: Resolution Rate

**Tab:** Usage & Business Value
**Visualization:** tiles (KPI)
**Tables:** customEvents
**Parameters:** {TimeRange}, {AgentFilter}, {ChannelFilter}

```kql
// FINRA 4511: Agent effectiveness — estimated resolution rate
// SOX 404: Operational control effectiveness measurement
customEvents
| where timestamp {TimeRange}
| where customDimensions.designMode == "False"
| where customDimensions.recipientName in ({AgentFilter}) or '*' in ({AgentFilter})
| where customDimensions.channelId in ({ChannelFilter}) or '*' in ({ChannelFilter})
| extend sessionId = tostring(customDimensions.session_Id)
| summarize
    HasTopicEnd = countif(name == "TopicEnd"),
    HasTopicStart = countif(name == "TopicStart")
    by sessionId
| summarize
    TotalSessions = count(),
    ResolvedSessions = countif(HasTopicEnd > 0)
| extend ResolutionRate = round(100.0 * ResolvedSessions / TotalSessions, 1)
```

**Notes:** **Limitation — Estimated metric.** Resolution is inferred from the presence of `TopicEnd` events in a session. There is no explicit "resolved" field in Copilot Studio telemetry. A session with a `TopicEnd` is treated as resolved; sessions that timeout or escalate without `TopicEnd` are treated as unresolved. This is a proxy metric and should be interpreted with that caveat.

---

### Q07: Average Messages per Session

**Tab:** Usage & Business Value
**Visualization:** tiles (KPI)
**Tables:** customEvents
**Parameters:** {TimeRange}, {AgentFilter}, {ChannelFilter}

```kql
// FINRA 4511: Agent interaction depth — messages per session
// OCC 2011-12: Agent complexity measurement
customEvents
| where timestamp {TimeRange}
| where customDimensions.designMode == "False"
| where customDimensions.recipientName in ({AgentFilter}) or '*' in ({AgentFilter})
| where customDimensions.channelId in ({ChannelFilter}) or '*' in ({ChannelFilter})
| where name == "BotMessageReceived"
| extend sessionId = tostring(customDimensions.session_Id)
| summarize
    TotalMessages = count(),
    TotalSessions = dcount(sessionId)
| extend AvgMessagesPerSession = round(1.0 * TotalMessages / TotalSessions, 1)
```

**Notes:** Counts only user messages (`BotMessageReceived`), not bot responses. To include both directions, add `| where name in ("BotMessageReceived", "BotMessageSend")`. Lower values may indicate efficient resolution; higher values may indicate complex queries or poor topic matching.

---

### Q08: Business Value Summary

**Tab:** Usage & Business Value
**Visualization:** tiles (4-wide KPI)
**Tables:** customEvents
**Parameters:** {TimeRange}, {AgentFilter}, {ChannelFilter}, {MinutesSaved}, {HourlyRate}

```kql
// SOX 302: Business value reporting — agent ROI estimation
// FINRA 4511: Usage volume for governance reporting
let MinutesPerSession = {MinutesSaved};
let HourlyRate = {HourlyRate};
customEvents
| where timestamp {TimeRange}
| where customDimensions.designMode == "False"
| where customDimensions.recipientName in ({AgentFilter}) or '*' in ({AgentFilter})
| where customDimensions.channelId in ({ChannelFilter}) or '*' in ({ChannelFilter})
| extend sessionId = tostring(customDimensions.session_Id)
| summarize TotalSessions = dcount(sessionId)
| extend
    EstHoursSaved = round(TotalSessions * MinutesPerSession / 60.0, 1),
    EstFTEEquivalent = round(TotalSessions * MinutesPerSession / 60.0 / 160.0, 2),
    EstCostAvoidance = round(TotalSessions * MinutesPerSession / 60.0 * HourlyRate, 0)
```

**Notes:** All values are estimates based on configurable parameters. Default assumptions: 5 minutes saved per session, $75/hour labor rate, 160 hours/month per FTE. Organizations should calibrate `MinutesSaved` based on time-motion studies or process analysis. Cost avoidance is not the same as realized savings — include this caveat in workbook documentation.

---

## Tab 2: Performance & Errors

### Q09: Response Latency (P50/P95/P99)

**Tab:** Performance & Errors
**Visualization:** timechart (multi-line)
**Tables:** customEvents
**Parameters:** {TimeRange}, {AgentFilter}, {ChannelFilter}

```kql
// OCC 2011-12: Model performance monitoring — response latency
// Fed SR 11-7: Model risk — performance degradation detection
// LIMITATION: Latency is estimated from timestamp deltas, not precise instrumentation
customEvents
| where timestamp {TimeRange}
| where customDimensions.designMode == "False"
| where customDimensions.recipientName in ({AgentFilter}) or '*' in ({AgentFilter})
| where customDimensions.channelId in ({ChannelFilter}) or '*' in ({ChannelFilter})
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
| where latencyMs > 0 and latencyMs < 120000
| summarize
    P50 = percentile(latencyMs, 50),
    P95 = percentile(latencyMs, 95),
    P99 = percentile(latencyMs, 99)
    by bin(timestamp, 5m)
| render timechart
```

**Notes:** **Limitation — Estimated metric.** Latency is approximated by measuring the time delta between a `BotMessageReceived` event and the immediately following `BotMessageSend` event within the same session. This includes server processing time but may be inflated by network latency, message queuing, or multi-turn topic processing. Outliers >120 seconds are filtered. The `serialize` operator is required for `prev()` to work correctly. 5-minute bins balance granularity with readability.

---

### Q10: Error Rate Trend

**Tab:** Performance & Errors
**Visualization:** timechart (area)
**Tables:** exceptions
**Parameters:** {TimeRange}

```kql
// OCC 2011-12: Operational risk — error volume monitoring
// SOX 404: Control effectiveness — error rate trends
exceptions
| where timestamp {TimeRange}
| summarize Errors = count() by bin(timestamp, 1h)
| render areachart
```

**Notes:** Uses `exceptions` table which captures runtime exceptions and connector failures. The `exceptions` table does not contain `customDimensions.designMode` or agent-specific fields, so AgentFilter and ChannelFilter are not applicable. If agent-specific error correlation is needed, join `exceptions` with `customEvents` on `operation_Id`.

---

### Q11: Error Types Breakdown

**Tab:** Performance & Errors
**Visualization:** barchart (stacked)
**Tables:** exceptions
**Parameters:** {TimeRange}

```kql
// OCC 2011-12: Operational risk — error classification
// Fed SR 11-7: Model risk — error categorization for root cause analysis
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

**Notes:** Uses `coalesce(outerType, type)` to prefer the outer exception type when available (wrapping exceptions). Common error types include connector timeouts, authentication failures, and Power Automate flow errors. AgentFilter/ChannelFilter not applicable to `exceptions` table.

---

### Q12: Connector/Action Success Rate

**Tab:** Performance & Errors
**Visualization:** table (grid)
**Tables:** customEvents
**Parameters:** {TimeRange}, {AgentFilter}, {ChannelFilter}

```kql
// SOX 404: Control effectiveness — connector reliability
// OCC 2011-12: Third-party risk — external dependency success rates
customEvents
| where timestamp {TimeRange}
| where name == "Action"
| where customDimensions.designMode == "False"
| where customDimensions.recipientName in ({AgentFilter}) or '*' in ({AgentFilter})
| where customDimensions.channelId in ({ChannelFilter}) or '*' in ({ChannelFilter})
| extend
    actionName = tostring(customDimensions.TopicName),
    success = customDimensions.type != "error"
| summarize
    Total = count(),
    Successes = countif(success),
    Failures = countif(not(success)),
    SuccessRate = round(100.0 * countif(success) / count(), 2)
    by actionName
| order by SuccessRate asc
```

**Notes:** Filters to `Action` events which represent Power Automate flows, HTTP requests, and other action nodes. Success is inferred from the absence of `type == "error"` in `customDimensions`. Action names come from `TopicName` which identifies the action node's parent topic. Low success rates indicate connector or external service issues.

---

### Q13: Generative AI Usage Trend

**Tab:** Performance & Errors
**Visualization:** timechart (line)
**Tables:** customEvents
**Parameters:** {TimeRange}, {AgentFilter}, {ChannelFilter}

```kql
// FINRA 25-07: AI governance — generative AI usage monitoring
// OCC 2011-12: Model risk — AI-powered response tracking
customEvents
| where timestamp {TimeRange}
| where customDimensions.designMode == "False"
| where customDimensions.recipientName in ({AgentFilter}) or '*' in ({AgentFilter})
| where customDimensions.channelId in ({ChannelFilter}) or '*' in ({ChannelFilter})
| where name == "GenerativeAnswers"
| summarize GenAIResponses = count() by bin(timestamp, 1h)
| render timechart
```

**Notes:** Tracks volume of responses generated by Copilot Studio's generative AI capability (knowledge-grounded answers). A sudden increase may indicate topic coverage gaps (users falling through to generative answers). A sudden decrease may indicate topic improvements. FINRA 25-07 regulatory notice specifically addresses AI governance in financial services.

---

### Q14: Topic Completion Rate

**Tab:** Performance & Errors
**Visualization:** table (grid)
**Tables:** customEvents
**Parameters:** {TimeRange}, {AgentFilter}, {ChannelFilter}

```kql
// SOX 404: Process control effectiveness — topic completion rates
// OCC 2011-12: Model performance — per-topic success measurement
customEvents
| where timestamp {TimeRange}
| where customDimensions.designMode == "False"
| where customDimensions.recipientName in ({AgentFilter}) or '*' in ({AgentFilter})
| where customDimensions.channelId in ({ChannelFilter}) or '*' in ({ChannelFilter})
| where name in ("TopicStart", "TopicEnd")
| extend topicName = tostring(customDimensions.TopicName)
| summarize
    Starts = countif(name == "TopicStart"),
    Completions = countif(name == "TopicEnd")
    by topicName
| extend CompletionRate = round(100.0 * Completions / Starts, 1)
| where Starts > 5
| order by CompletionRate asc
```

**Notes:** Measures the ratio of `TopicEnd` to `TopicStart` events per topic. Topics with low completion rates may indicate user abandonment, errors during conversation flow, or escalation before completion. The `Starts > 5` filter excludes rarely-used topics that would skew percentages. System topics like "Greeting" may show artificially low completion rates if they redirect to other topics.

---

### Q15: RAI Content Filtering Events

**Tab:** Performance & Errors
**Visualization:** tiles + timechart
**Tables:** customEvents
**Parameters:** {TimeRange}, {AgentFilter}, {ChannelFilter}

**Query A — KPI Tile:**

```kql
// FINRA 25-07: AI governance — responsible AI event monitoring
// GLBA 501(b): Information security — content safety events
customEvents
| where timestamp {TimeRange}
| where customDimensions.designMode == "False"
| where customDimensions.recipientName in ({AgentFilter}) or '*' in ({AgentFilter})
| where customDimensions.channelId in ({ChannelFilter}) or '*' in ({ChannelFilter})
| where name == "GenerativeAnswers"
| where customDimensions.type == "contentFilter" or customDimensions.Kind has "filter"
| summarize RAIEvents = count()
```

**Query B — Trend:**

```kql
// FINRA 25-07: AI governance — RAI event trend
customEvents
| where timestamp {TimeRange}
| where customDimensions.designMode == "False"
| where customDimensions.recipientName in ({AgentFilter}) or '*' in ({AgentFilter})
| where customDimensions.channelId in ({ChannelFilter}) or '*' in ({ChannelFilter})
| where name == "GenerativeAnswers"
| where customDimensions.type == "contentFilter" or customDimensions.Kind has "filter"
| summarize RAIEvents = count() by bin(timestamp, 1h)
| render timechart
```

**Notes:** **Limitation — Partial visibility.** Copilot Studio's native Application Insights telemetry provides limited RAI content filter detail. The `GenerativeAnswers` event may include filtering indicators in `customDimensions.type` or `customDimensions.Kind`, but granular filter categories (hate, violence, sexual, self-harm) require Purview Audit logs, not Application Insights. If no RAI events appear, the workbook should display a "No content filtering events detected" message. Organizations requiring detailed RAI monitoring should implement Purview Audit integration (Control 3.9).

---

### Q16: Fallback/Escalation Volume

**Tab:** Performance & Errors
**Visualization:** timechart (area)
**Tables:** customEvents
**Parameters:** {TimeRange}, {AgentFilter}, {ChannelFilter}

```kql
// FINRA 3110: Supervisory escalation — agent escalation tracking
// SOX 404: Control effectiveness — escalation volume trends
customEvents
| where timestamp {TimeRange}
| where customDimensions.designMode == "False"
| where customDimensions.recipientName in ({AgentFilter}) or '*' in ({AgentFilter})
| where customDimensions.channelId in ({ChannelFilter}) or '*' in ({ChannelFilter})
| where name == "TopicStart"
| extend topicName = tostring(customDimensions.TopicName)
| where topicName has_any ("Escalate", "Transfer", "Handoff", "Fallback", "End of Conversation")
| summarize EscalationSessions = dcount(tostring(customDimensions.session_Id)) by bin(timestamp, 1d)
| render areachart
```

**Notes:** Identifies escalation by matching topic names that indicate human handoff or fallback behavior. The `has_any` filter catches common Copilot Studio system topics for escalation: "Escalate", "Transfer Agent", "Handoff", "Fallback", and "End of Conversation". Custom topic names that indicate escalation should be added to the filter list based on the organization's topic naming conventions. High escalation volumes may indicate agent capability gaps.

---

## Tab 3: Operational Health

### Q17: Session Volume Anomaly Detection

**Tab:** Operational Health
**Visualization:** anomalychart
**Tables:** customEvents
**Parameters:** None (uses fixed 14-day lookback for statistical baseline)

```kql
// OCC 2011-12: Operational risk — anomalous usage pattern detection
// Fed SR 11-7: Model risk — automated change detection
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

**Notes:** Uses `series_decompose_anomalies()` with a sensitivity threshold of 1.5 (standard deviation). A 14-day lookback provides sufficient baseline for weekly patterns. The anomaly detection identifies both positive anomalies (unusual spikes) and negative anomalies (unusual drops). Agent and channel filters are intentionally excluded to maintain a stable baseline across the full population. Threshold sensitivity is zone-dependent — see Appendix A.

---

### Q18: Availability (Uptime Trend)

**Tab:** Operational Health
**Visualization:** timechart (line)
**Tables:** customEvents
**Parameters:** {TimeRange}, {AgentFilter}

```kql
// SOX 404: System availability — agent uptime monitoring
// OCC 2011-12: Business continuity — service availability trend
customEvents
| where timestamp {TimeRange}
| where customDimensions.designMode == "False"
| where customDimensions.recipientName in ({AgentFilter}) or '*' in ({AgentFilter})
| extend sessionId = tostring(customDimensions.session_Id)
| summarize SessionCount = dcount(sessionId) by bin(timestamp, 1h)
| render timechart
```

**Notes:** **Limitation — Proxy metric.** Copilot Studio does not emit explicit availability/health check telemetry to Application Insights. This query uses hourly session presence as a proxy: gaps in the timechart (hours with zero sessions) may indicate downtime, but could also indicate low-traffic periods (nights, weekends). For true availability monitoring, organizations should combine this with Azure Service Health alerts and Power Platform service status. Business hours filtering is recommended for meaningful interpretation.

---

### Q19: Exception Spike Detection

**Tab:** Operational Health
**Visualization:** anomalychart
**Tables:** exceptions
**Parameters:** None (uses fixed 14-day lookback for statistical baseline)

```kql
// OCC 2011-12: Operational risk — exception spike detection
// Fed SR 11-7: Model risk — automated error pattern detection
let lookback = 14d;
exceptions
| where timestamp > ago(lookback)
| summarize Errors = count() by bin(timestamp, 1h)
| make-series ErrorSeries = sum(Errors) default=0 on timestamp step 1h
| extend (anomalies, score, baseline) = series_decompose_anomalies(ErrorSeries, 1.5)
| render anomalychart with (anomalycolumns=anomalies)
```

**Notes:** Complements Q17 (session anomaly) by detecting abnormal error volume patterns. Same sensitivity threshold (1.5) and lookback period (14 days). Agent/channel filters excluded from `exceptions` table (not agent-specific). Positive anomalies (error spikes) are the primary concern — these should trigger investigation workflows.

---

### Q20: Generative Answers Quality

**Tab:** Operational Health
**Visualization:** tiles (KPI)
**Tables:** customEvents
**Parameters:** {TimeRange}, {AgentFilter}, {ChannelFilter}

```kql
// FINRA 25-07: AI governance — generative AI quality assessment
// OCC 2011-12: Model risk — AI response quality monitoring
customEvents
| where timestamp {TimeRange}
| where customDimensions.designMode == "False"
| where customDimensions.recipientName in ({AgentFilter}) or '*' in ({AgentFilter})
| where customDimensions.channelId in ({ChannelFilter}) or '*' in ({ChannelFilter})
| extend sessionId = tostring(customDimensions.session_Id)
| summarize
    GenAnswerCount = countif(name == "GenerativeAnswers"),
    TotalSessions = dcount(sessionId),
    TopicStartCount = countif(name == "TopicStart"),
    TopicEndCount = countif(name == "TopicEnd")
| extend
    GenAnswerRate = round(100.0 * GenAnswerCount / TotalSessions, 1),
    EstFallbackRate = iff(TopicStartCount > 0,
        round(100.0 * (TopicStartCount - TopicEndCount) / TopicStartCount, 1),
        0.0)
```

**Notes:** Provides two KPI tiles: (1) Gen AI answer rate — percentage of sessions involving generative answers (high rates may indicate insufficient topic coverage), and (2) Estimated fallback rate — sessions where topics started but did not complete. Neither metric directly measures response quality (hallucination, grounding accuracy) — those require Azure AI Evaluation SDK or custom implementation, which is not available in native Copilot Studio telemetry.

---

### Q21: Dependency Health

**Tab:** Operational Health
**Visualization:** table (grid)
**Tables:** dependencies
**Parameters:** {TimeRange}

```kql
// SOX 404: Third-party control effectiveness — external dependency monitoring
// OCC 2011-12: Third-party risk — connector and API health
dependencies
| where timestamp {TimeRange}
| summarize
    TotalCalls = count(),
    SuccessRate = round(100.0 * countif(success == true) / count(), 2),
    AvgDurationMs = round(avg(duration), 1),
    P95DurationMs = round(percentile(duration, 95), 1),
    FailureCount = countif(success == false)
    by name, target
| order by SuccessRate asc
```

**Notes:** The `dependencies` table captures external API calls made by connectors and knowledge sources. Fields `name` (dependency type), `target` (endpoint), `duration` (ms), `success` (boolean), and `resultCode` are standard Application Insights schema. Low success rates or high P95 latency indicate external service degradation. Agent/channel filters are not available in the `dependencies` table.

---

### Q22: DLP/Security Events

**Tab:** Operational Health
**Visualization:** tiles + table
**Tables:** customEvents
**Parameters:** {TimeRange}, {AgentFilter}

**Query A — KPI Tile:**

```kql
// GLBA 501(b): Information security — DLP event monitoring
// FINRA 3110: Supervisory compliance — security event visibility
customEvents
| where timestamp {TimeRange}
| where customDimensions.designMode == "False"
| where customDimensions.recipientName in ({AgentFilter}) or '*' in ({AgentFilter})
| where customDimensions.type in ("dlpMatch", "securityEvent", "policyBlock")
    or customDimensions.Kind has_any ("DLP", "Security", "Policy")
| summarize DLPEvents = count()
```

**Query B — Detail Table:**

```kql
// GLBA 501(b): DLP event detail for investigation
customEvents
| where timestamp {TimeRange}
| where customDimensions.designMode == "False"
| where customDimensions.recipientName in ({AgentFilter}) or '*' in ({AgentFilter})
| where customDimensions.type in ("dlpMatch", "securityEvent", "policyBlock")
    or customDimensions.Kind has_any ("DLP", "Security", "Policy")
| extend
    eventType = tostring(customDimensions.type),
    agentName = tostring(customDimensions.recipientName),
    channel = tostring(customDimensions.channelId),
    sessionId = tostring(customDimensions.session_Id)
| project timestamp, agentName, eventType, channel, sessionId
| order by timestamp desc
| take 100
```

**Notes:** **Limitation — Custom telemetry dependency.** DLP match events are not part of the standard Copilot Studio Application Insights schema. They require either: (1) custom telemetry from DLP policy integration, or (2) Purview DLP integration sending events to the same Application Insights resource. If no DLP events are present, the tiles should display "0" with a note that DLP telemetry integration is required. For comprehensive DLP monitoring, use Microsoft Sentinel integration (Control 3.9).

---

### Q23: Agent Health Summary

**Tab:** Operational Health
**Visualization:** tiles (per-agent)
**Tables:** customEvents + exceptions
**Parameters:** {TimeRange}, {AgentFilter}, {ChannelFilter}

```kql
// FINRA 4511: Per-agent operational summary
// OCC 2011-12: Model inventory — individual agent health assessment
// SOX 404: Control effectiveness — per-agent monitoring
let sessionData = customEvents
| where timestamp {TimeRange}
| where customDimensions.designMode == "False"
| where customDimensions.recipientName in ({AgentFilter}) or '*' in ({AgentFilter})
| where customDimensions.channelId in ({ChannelFilter}) or '*' in ({ChannelFilter})
| extend
    agentName = tostring(customDimensions.recipientName),
    sessionId = tostring(customDimensions.session_Id)
| summarize
    Sessions = dcount(sessionId),
    Messages = countif(name == "BotMessageReceived"),
    TopicStarts = countif(name == "TopicStart"),
    TopicEnds = countif(name == "TopicEnd"),
    GenAIResponses = countif(name == "GenerativeAnswers")
    by agentName;
let latencyData = customEvents
| where timestamp {TimeRange}
| where customDimensions.designMode == "False"
| where customDimensions.recipientName in ({AgentFilter}) or '*' in ({AgentFilter})
| where name in ("BotMessageReceived", "BotMessageSend")
| extend
    agentName = tostring(customDimensions.recipientName),
    sessionId = tostring(customDimensions.session_Id)
| order by sessionId, timestamp asc
| serialize
| extend
    prevEvent = prev(name),
    prevTimestamp = prev(timestamp),
    prevSession = prev(tostring(customDimensions.session_Id)),
    prevAgent = prev(tostring(customDimensions.recipientName))
| where name == "BotMessageSend" and prevEvent == "BotMessageReceived" and sessionId == prevSession
| extend latencyMs = datetime_diff('millisecond', timestamp, prevTimestamp)
| where latencyMs > 0 and latencyMs < 120000
| summarize
    EstP50LatencyMs = percentile(latencyMs, 50),
    EstP95LatencyMs = percentile(latencyMs, 95)
    by agentName;
let errorData = exceptions
| where timestamp {TimeRange}
| summarize ErrorCount = count();
sessionData
| join kind=leftouter latencyData on agentName
| extend
    CompletionRate = iff(TopicStarts > 0, round(100.0 * TopicEnds / TopicStarts, 1), 0.0),
    EstP50LatencyMs = coalesce(EstP50LatencyMs, 0),
    EstP95LatencyMs = coalesce(EstP95LatencyMs, 0)
| project
    agentName,
    Sessions,
    Messages,
    CompletionRate,
    GenAIResponses,
    EstP50LatencyMs,
    EstP95LatencyMs
| order by Sessions desc
```

**Notes:** Composite query that joins session metrics with estimated latency per agent. The `exceptions` table cannot be joined per-agent (lacks agent identifiers), so error correlation is omitted from the per-agent view — use Q10/Q11 for error analysis. The `leftouter` join ensures agents with no measured latency still appear (with 0ms defaults). This query powers a per-agent tile display with conditional formatting (Phase 2).

---

## Appendix A: Zone-Aware Threshold Guidance

These thresholds feed into Phase 2 workbook conditional formatting (tile color coding).

| Metric | Zone 1 (Personal) | Zone 2 (Team) | Zone 3 (Enterprise) | Source |
|--------|-------------------|---------------|---------------------|--------|
| Error rate alert threshold | >10% | >5% | >2% | Control 2.9 |
| Latency alert (P95) | — | >5,000 ms | >3,000 ms | Control 2.9 |
| Anomaly detection sensitivity | — | 2.0 | 1.5 | Research recommendation |
| Review frequency | Monthly | Weekly | Daily + real-time | Control 2.9 |
| Escalation rate alert | — | >25% | >15% | Control 2.9 (derived) |
| Resolution rate minimum | — | >60% | >80% | Research recommendation (estimated metric) |

**Zone application notes:**
- Zone 1 agents have minimal monitoring requirements — monthly review of session counts is sufficient
- Zone 2 agents require weekly performance reviews and standard alerting thresholds
- Zone 3 agents require daily monitoring with real-time alerts and tighter thresholds
- Anomaly detection sensitivity of 1.5 (Zone 3) catches more deviations than 2.0 (Zone 2), producing more alerts
- Resolution rate thresholds are advisory — the metric is estimated (see Q06 notes)

---

## Appendix B: Query Design Patterns

### Standard Filter Block

All `customEvents` queries that support agent/channel filtering use this standard block:

```kql
| where timestamp {TimeRange}
| where customDimensions.designMode == "False"
| where customDimensions.recipientName in ({AgentFilter}) or '*' in ({AgentFilter})
| where customDimensions.channelId in ({ChannelFilter}) or '*' in ({ChannelFilter})
```

### Exceptions Table Limitation

The `exceptions` table does not include Copilot Studio-specific `customDimensions` fields (`recipientName`, `channelId`, `designMode`). Queries against `exceptions` (Q10, Q11, Q19) cannot be filtered by agent or channel. For agent-specific error correlation, join on `operation_Id`:

```kql
exceptions
| where timestamp {TimeRange}
| join kind=inner (
    customEvents
    | where customDimensions.recipientName in ({AgentFilter}) or '*' in ({AgentFilter})
    | project operation_Id
    | distinct operation_Id
) on operation_Id
```

This join pattern is not included in the standard queries due to performance cost, but is documented here for advanced use cases.

### Dependencies Table Limitation

The `dependencies` table similarly lacks agent-specific fields. Dependencies are tracked at the Application Insights resource level, not per-agent. If multiple agents share a single Application Insights resource, dependency metrics reflect the aggregate.

---

*Created: 2026-02-11*
*Source: v13 Research + Plan 01-02*
*Query count: 23 queries + 3 parameter queries + 2 static parameters = 28 total*
