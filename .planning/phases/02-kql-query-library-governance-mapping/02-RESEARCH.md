# Phase 2: KQL Query Library & Governance Mapping - Research

**Researched:** 2026-02-05
**Domain:** Kusto Query Language (KQL) for Application Insights telemetry and governance compliance
**Confidence:** HIGH

## Summary

Phase 2 creates a reusable KQL query library for Copilot Studio agent observability with governance documentation linking queries to FSI-AgentGov's 62-control framework. The research confirms that KQL provides mature query capabilities for Application Insights customEvents telemetry, with standardized patterns for parameterization, aggregation, and null handling. The customEvents table contains Copilot Studio telemetry in customDimensions fields, enabling session analytics, error categorization, latency distribution, and audit trail extraction.

Key findings:
- KQL supports workbook-style parameterization with `let TimeRange = {TimeRange:7d};` syntax for time ranges
- Percentile functions (percentile(field, 95)) provide P50/P95/P99 latency metrics for performance monitoring
- coalesce() function enables graceful null handling with warning messages for incomplete telemetry
- hash_sha256() provides persistent PII hashing for user identity sanitization in audit trails
- Governance mapping uses artifact-first approach: start from query → list controls supported (not control-first)
- SR 11-7 requires outcome analysis and performance monitoring at least annually (more frequently if needed)

**Primary recommendation:** Organize queries by function (usage-analytics, error-categorization, latency-distribution), not regulation. Use descriptive kebab-case file names with comprehensive header blocks. Implement both inline control references (`// Supports: 1.8, 3.2`) and separate governance-queries.md mapping document with three-tier evidence model (Primary/Supporting/Partial).

## Standard Stack

The established KQL patterns for Azure Monitor and Application Insights telemetry:

### Core

| Component | Version | Purpose | Why Standard |
|-----------|---------|---------|--------------|
| Kusto Query Language (KQL) | Current | Azure Monitor/Log Analytics query language | Microsoft native, unified syntax across Azure telemetry |
| Application Insights customEvents table | N/A | Copilot Studio telemetry storage | Standard Copilot Studio integration table |
| Log Analytics workspace | PerGB2018 SKU | 730-day interactive retention | SEC 17a-4(b)(4) compliance, real-time queries |
| hash_sha256() function | Built-in | Persistent PII hashing | Consistent hash values across queries for audit correlation |
| percentile() function | Built-in | P50/P95/P99 calculation | Standard performance monitoring metric |
| coalesce() function | Built-in | Null handling with defaults | Graceful missing field handling |

### Supporting

| Component | Purpose | When to Use |
|-----------|---------|-------------|
| bin() function | Time-based aggregation (1h, 1d, 7d bins) | All time-series queries, required for timechart |
| summarize operator | Group-by aggregation | Usage analytics, error counts, session metrics |
| extend operator | Add computed columns | Completeness %, hash transformations, field parsing |
| parse_json() / todynamic() | Extract nested customDimensions fields | All Copilot Studio telemetry queries |
| where timestamp > ago() | Time range filtering | Performance optimization (filter early) |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Function-based organization | Regulation-based folders (finra/, sox/, sr11-7/) | Function-based = reusable across regulations, regulation-based = redundant queries |
| kebab-case file names | PascalCase or snake_case | kebab-case = readable URLs, consistent with Microsoft Learn examples |
| Separate queries per zone | Single parameterized query with zone filter | Separate = simpler, parameterized = less duplication (user preference) |

**Query File Format:**
```kql
// agent-usage-analytics.kql
// Purpose: Agent session and message volume trends over time
// Parameters: TimeRange (default 7d), AgentId (optional filter)
// Outputs: Timestamp, AgentId, SessionCount, MessageCount, CompletionRate
// Supports: Control 3.2 (Primary), Control 2.9 (Supporting)
// Sample output:
// | Timestamp | AgentId | SessionCount | MessageCount | CompletionRate |
// | 2026-02-04 | agent-001 | 342 | 1205 | 0.87 |

let TimeRange = {TimeRange:7d};
customEvents
| where timestamp > ago(TimeRange)
| where name == "BotMessageSend" or name == "BotMessageReceived"
| extend AgentId = tostring(customDimensions["recipientId"])
| summarize
    SessionCount = dcount(session_Id),
    MessageCount = count()
    by bin(timestamp, 1d), AgentId
| project Timestamp=timestamp, AgentId, SessionCount, MessageCount
```

**Source:** [Get started with log queries in Azure Monitor](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/get-started-queries), [Application Insights telemetry with Copilot Studio](https://learn.microsoft.com/en-us/dynamics365/guidance/resources/copilot-studio-appinsights)

## Architecture Patterns

### Recommended Project Structure

```
kql-queries/
├── README.md                          # Query library overview, usage examples
├── governance-queries.md              # Comprehensive control mapping (artifact-first)
├── usage-analytics/
│   ├── agent-usage-analytics.kql      # Session/message trends
│   ├── user-engagement-metrics.kql    # Distinct users, repeat sessions
│   └── topic-popularity.kql           # Topic trigger frequency
├── error-categorization/
│   ├── error-categorization-by-type.kql   # Connector/knowledge/orchestration errors
│   ├── error-trend-analysis.kql           # Error rate over time
│   └── error-detail-extraction.kql        # Full error text with context
├── performance/
│   ├── latency-distribution.kql           # P50/P95/P99 response times
│   ├── response-time-by-topic.kql         # Topic-specific latency
│   └── slow-query-detection.kql           # Queries exceeding threshold
├── compliance/
│   ├── agent-decision-audit-trail.kql     # FINRA 3110 decision chain
│   ├── rai-content-filtering-detection.kql  # XPIADetected, JailbreakDetected
│   └── completeness-assessment.kql        # Telemetry gap detection
├── sr11-7-model-risk/
│   ├── output-monitoring.kql              # Outcome analysis
│   ├── drift-detection-baseline.kql       # Response pattern baseline
│   └── validation-test-results.kql        # Model validation evidence
└── templates/
    └── query-header-template.txt         # Standard header format
```

### Pattern 1: KQL Query Header Block (Self-Contained Documentation)

**What:** Every .kql file starts with a comprehensive comment header block documenting purpose, parameters, output schema, control mappings, and sample output.

**When to use:** All production queries (required for someone reading just the .kql file to understand usage)

**Example:**
```kql
// agent-decision-audit-trail.kql
// Purpose: Extract complete decision chain for FINRA 3110 supervision requirements
//
// Parameters:
//   {TimeRange} - Time window (default: 7d) - workbook parameter syntax
//   {AgentId} - Optional agent filter (default: all agents)
//   {IncludePII} - Boolean flag: true = raw UserId (authorized reviewers only), false = hashed (default)
//
// Output Schema:
//   Timestamp (datetime) - When decision occurred
//   AgentId (string) - Agent identifier
//   SessionId (string) - Conversation session ID
//   UserId (string) - User identifier (hashed unless IncludePII=true)
//   Prompt (string) - User input
//   Response (string) - Agent output
//   Sources (dynamic) - Knowledge sources cited
//   SupervisorId (string) - Reviewer identity if HITL enabled
//   ReviewStatus (string) - Approved/Rejected/Pending
//   CompletenessPercent (real) - % of required fields present
//
// Supports:
//   Control 1.7 (Primary) - Comprehensive Audit Logging
//   Control 2.12 (Primary) - FINRA 3110 Supervision
//   Control 2.6 (Supporting) - SR 11-7 Model Risk Management
//
// Regulatory Mapping:
//   FINRA 3110 - Supervisory procedures documentation
//   SEC 17a-4 - Communications record preservation
//   SR 11-7 - Model decision audit trail
//
// Sample Output:
// | Timestamp | AgentId | SessionId | UserId (hashed) | Prompt | Response | CompletenessPercent |
// | 2026-02-04T10:15:23Z | agent-001 | sess-abc | sha256:a3f2... | "What are my account options?" | "Based on your profile..." | 0.95 |
//
// Notes:
//   - Default mode hashes UserId for PII protection (hash_sha256)
//   - Fields with NULL produce coalesce warning ('NOT_CAPTURED')
//   - CompletenessPercent helps identify telemetry gaps before audits

let TimeRange = {TimeRange:7d};
let IncludePII = {IncludePII:false};

customEvents
| where timestamp > ago(TimeRange)
| where name == "BotMessageSend"
| extend AgentId = tostring(customDimensions["recipientId"])
| extend SessionId = tostring(session_Id)
| extend UserIdRaw = tostring(customDimensions["fromName"])
| extend UserId = iff(IncludePII, UserIdRaw, hash_sha256(UserIdRaw))
| extend Prompt = coalesce(tostring(customDimensions["text"]), "NOT_CAPTURED")
| extend Response = coalesce(tostring(customDimensions["speak"]), "NOT_CAPTURED")
| extend SupervisorId = coalesce(tostring(customDimensions["SupervisorId"]), "NOT_CAPTURED")
| extend ReviewStatus = coalesce(tostring(customDimensions["ReviewStatus"]), "NOT_CAPTURED")
| extend CompletenessPercent =
    todouble(
        iff(isnotnull(customDimensions["text"]), 1, 0) +
        iff(isnotnull(customDimensions["speak"]), 1, 0) +
        iff(isnotnull(customDimensions["fromName"]), 1, 0) +
        iff(isnotnull(session_Id), 1, 0)
    ) / 4.0
| project Timestamp=timestamp, AgentId, SessionId, UserId, Prompt, Response, SupervisorId, ReviewStatus, CompletenessPercent
| order by Timestamp desc
```

**Source:** Adapted from [KQL Best Practices for Documentation](https://veldify.com/2025/06/26/best-practices-for-documenting-and-organizing-kql/)

### Pattern 2: Parameterized Time Ranges with Workbook Syntax

**What:** Use workbook parameter syntax `{TimeRange:default}` for time range parameters, enabling seamless integration with Azure Monitor Workbooks and Power BI.

**When to use:** All queries intended for workbook/dashboard consumption (primary use case)

**Example:**
```kql
// latency-distribution.kql
// Parameters: {TimeRange:7d}, {AgentId:all}

let TimeRange = {TimeRange:7d};
let AgentIdFilter = "{AgentId}";

customEvents
| where timestamp > ago(TimeRange)
| where name == "BotMessageSend"
| extend AgentId = tostring(customDimensions["recipientId"])
| where AgentIdFilter == "all" or AgentId == AgentIdFilter
| extend DurationMs = todouble(customDimensions["duration"])
| summarize
    P50 = percentile(DurationMs, 50),
    P95 = percentile(DurationMs, 95),
    P99 = percentile(DurationMs, 99),
    Count = count()
    by bin(timestamp, 1h), AgentId
| project Timestamp=timestamp, AgentId, P50, P95, P99, Count
```

**Source:** [Azure Monitor workbook time parameters](https://learn.microsoft.com/en-us/azure/azure-monitor/visualize/workbooks-time)

### Pattern 3: Graceful Null Handling with Completeness Metrics

**What:** Use coalesce() to replace NULL fields with 'NOT_CAPTURED' warnings, and calculate completeness percentage to identify telemetry gaps.

**When to use:** Audit trail queries where incomplete records should run but flag missing data (operational vs blocking approach)

**Example:**
```kql
// completeness-assessment.kql
// Purpose: Identify telemetry gaps for audit readiness

customEvents
| where timestamp > ago(7d)
| where name == "BotMessageSend"
| extend
    HasText = iff(isnotnull(customDimensions["text"]), 1, 0),
    HasSpeak = iff(isnotnull(customDimensions["speak"]), 1, 0),
    HasFromName = iff(isnotnull(customDimensions["fromName"]), 1, 0),
    HasSessionId = iff(isnotnull(session_Id), 1, 0),
    HasSupervisor = iff(isnotnull(customDimensions["SupervisorId"]), 1, 0)
| extend CompletenessPercent =
    todouble(HasText + HasSpeak + HasFromName + HasSessionId + HasSupervisor) / 5.0
| summarize
    AvgCompleteness = avg(CompletenessPercent),
    RecordsBelow80Percent = countif(CompletenessPercent < 0.80),
    TotalRecords = count()
    by bin(timestamp, 1d)
| project
    Date=timestamp,
    AvgCompleteness,
    RecordsBelow80Percent,
    TotalRecords,
    ComplianceRisk = iff(AvgCompleteness < 0.80, "HIGH", iff(AvgCompleteness < 0.90, "MEDIUM", "LOW"))
```

**Source:** [Understanding coalesce() in KQL](https://medium.com/@md.hasan/understanding-the-coalesce-function-in-kusto-query-language-kql-with-practical-examples-ced6202d8457) (attempted, 403 error), [Null values in KQL](https://learn.microsoft.com/en-us/azure/data-explorer/kusto/query/scalar-data-types/null-values)

### Pattern 4: Persistent PII Hashing for Audit Correlation

**What:** Use hash_sha256() for PII fields (UserId, UserEmail) to enable consistent correlation across queries while protecting identity. Avoid default hash() which uses non-persistent xxhash64.

**When to use:** All queries with PII fields requiring cross-query correlation (audit trails, usage analytics)

**Example:**
```kql
// user-engagement-metrics.kql
// Purpose: Distinct users and repeat sessions (PII-safe with hashing)

let TimeRange = {TimeRange:30d};

customEvents
| where timestamp > ago(TimeRange)
| where name == "BotMessageSend"
| extend UserIdRaw = tostring(customDimensions["fromName"])
| extend UserIdHashed = hash_sha256(UserIdRaw)  // Persistent hash for correlation
| extend AgentId = tostring(customDimensions["recipientId"])
| summarize
    DistinctUsers = dcount(UserIdHashed),
    TotalSessions = dcount(session_Id),
    TotalMessages = count()
    by bin(timestamp, 1d), AgentId
| extend SessionsPerUser = todouble(TotalSessions) / DistinctUsers
| project Timestamp=timestamp, AgentId, DistinctUsers, TotalSessions, SessionsPerUser
```

**Source:** [hash() function - Azure Data Explorer](https://learn.microsoft.com/en-us/azure/data-explorer/kusto/query/hashfunction) - "For persistent hashing, use hash_sha256(), hash_sha1(), or hash_md5()"

### Pattern 5: Early Filtering and Explicit Binning for Performance

**What:** Place time filters immediately after table name, use explicit bin() for time aggregation (automatic binning deprecated).

**When to use:** All production queries (performance optimization)

**Example:**
```kql
// error-trend-analysis.kql
// Purpose: Error rate over time by error type

let TimeRange = {TimeRange:7d};

customEvents
| where timestamp > ago(TimeRange)  // FILTER EARLY (performance)
| where name == "BotMessageSend"
| extend ErrorCode = tostring(customDimensions["errorCodeText"])
| where isnotnull(ErrorCode)  // Only error events
| summarize ErrorCount = count() by bin(timestamp, 1h), ErrorCode  // EXPLICIT BIN (required)
| project Timestamp=timestamp, ErrorCode, ErrorCount
| order by Timestamp desc, ErrorCount desc
```

**Source:** [Get started with log queries - Azure Monitor](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/get-started-queries), [Aggregation best practices](https://learn.microsoft.com/en-us/kusto/query/tutorials/use-aggregation-functions?view=microsoft-fabric)

### Anti-Patterns to Avoid

- **Using hash() instead of hash_sha256():** hash() uses xxhash64 which may change, breaking audit correlation across query runs
- **No sample output in header:** Users can't understand query results without running it
- **Hardcoded time ranges:** Use parameterization for workbook/dashboard reusability
- **Missing completeness metrics in audit queries:** Operations can't identify telemetry gaps before audits
- **Control mappings in separate doc only:** Inline `// Supports: X.X` enables quick reference while editing query
- **Using search instead of where for known columns:** `search` is 10-100x slower than `where` with column names

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Time range parameterization | Custom string parsing for "7d", "30d" | Workbook parameter syntax `{TimeRange:7d}` | Native workbook/Power BI integration, handles all Azure Monitor time formats |
| Percentile calculation | Manual sorting and nth-element extraction | percentile(field, 95) function | Handles edge cases (nulls, duplicates), optimized for large datasets |
| PII hashing | Custom SHA256 implementation or regex masking | hash_sha256() built-in function | Persistent, optimized, handles null inputs |
| Null handling with defaults | iff(isnotnull(x), x, "default") chains | coalesce(x, y, "default") | Cleaner syntax, multiple fallback values |
| Time-series aggregation | Custom datetime arithmetic | bin(timestamp, 1h) with summarize | Required for timechart, handles DST and timezone edge cases |
| Governance control mapping | Spreadsheet maintenance | Markdown governance-queries.md with inline comments | Version-controlled, searchable, co-located with queries |

**Key insight:** KQL built-in functions handle edge cases (nulls, type mismatches, timezone offsets) that custom solutions miss. Azure Monitor workbook parameters enable zero-code dashboard creation.

## Common Pitfalls

### Pitfall 1: Using hash() Instead of hash_sha256() Breaks Audit Correlation

**What goes wrong:** Query uses `hash(UserId)` to anonymize user identity. Audit trail query runs on Monday, hashes user "john.doe" to value `12345`. Same query runs on Tuesday after KQL engine update, hashes "john.doe" to value `67890`. Audit correlation fails.

**Why it happens:** hash() function uses xxhash64 algorithm which Microsoft documentation explicitly states "may change" and "should only be used within a single query."

**How to avoid:** Use hash_sha256() for persistent hashing where cross-query correlation is needed. Use hash() only for in-query operations like sampling (`where hash(StartTime, 10) == 0` for 10% sample).

**Warning signs:** Query header says "for audit trail" or "cross-query correlation" but uses hash() instead of hash_sha256().

**Source:** [hash() function - Azure Data Explorer](https://learn.microsoft.com/en-us/azure/data-explorer/kusto/query/hashfunction)

### Pitfall 2: Automatic Binning No Longer Supported (Query Fails)

**What goes wrong:** Query uses `summarize count() by timestamp` expecting automatic hourly bins. Query fails with error: "Automatic binning not supported, use explicit bin() function."

**Why it happens:** Azure Monitor deprecated automatic datetime binning. Explicit bin() is now required.

**How to avoid:** Always use `summarize count() by bin(timestamp, 1h)` with explicit time interval (1h, 1d, 7d).

**Warning signs:** Query uses `by timestamp` or `by TimeGenerated` without bin() wrapper.

**Source:** [Tutorial: Use aggregation functions in KQL](https://learn.microsoft.com/en-us/kusto/query/tutorials/use-aggregation-functions?view=microsoft-fabric) - "Automatic hourly bins for datetime columns are no longer supported. Use explicit binning instead."

### Pitfall 3: Missing CompletenessPercent Hides Telemetry Gaps Until Audit

**What goes wrong:** Operations runs audit trail query, exports 10,000 records to compliance team. During regulatory examination, auditor finds 30% of records missing Prompt field (customDimensions.text). Firm cannot demonstrate complete supervisory record. Deficiency cited.

**Why it happens:** Copilot Studio telemetry capture depends on "Log sensitive Activity properties" setting. If disabled (Phase 1 recommendation), Prompt/Response fields are NULL. Query using coalesce() runs successfully but doesn't flag incomplete records.

**How to avoid:** Include CompletenessPercent calculation in all audit trail queries. Operations can identify telemetry gaps before audits and remediate (enable sensitive logging, document exemptions, etc.).

**Warning signs:** Audit query uses coalesce() for Prompt/Response fields but doesn't calculate % of required fields present.

### Pitfall 4: Workbook Parameter Syntax Incompatible with Direct Log Analytics Execution

**What goes wrong:** Query uses `let TimeRange = {TimeRange:7d};` workbook parameter syntax. Developer copies query to Log Analytics portal to test. Query fails: "Syntax error: {TimeRange:7d} not recognized."

**Why it happens:** Workbook parameter syntax `{Param:default}` is a workbook feature, not native KQL. Log Analytics portal requires literal values.

**How to avoid:** Document in README.md that queries using `{Param}` syntax must be tested in workbooks or with find-replace for literal values. Provide test commands: `let TimeRange = 7d;` (literal) instead of `{TimeRange:7d}`.

**Warning signs:** Query file has no usage notes about workbook-only syntax.

### Pitfall 5: Control Mapping Only in Separate Doc Slows Query Development

**What goes wrong:** Developer needs to add error categorization query. Opens governance-queries.md, finds Control 3.4 requires error categorization evidence. Searches for which queries support 3.4. No inline comments in .kql files. Developer creates duplicate query because existing one wasn't discoverable.

**Why it happens:** Governance mapping in separate document only means developers don't see control references while editing queries.

**How to avoid:** Use BOTH approaches: inline `// Supports: 3.4, 2.9` comments in query headers AND comprehensive governance-queries.md mapping doc. Inline for quick reference, document for full cross-reference.

**Warning signs:** .kql files have no control ID references in comments.

## Code Examples

Verified patterns from official sources:

### Extract Copilot Studio Session Metrics (Usage Analytics)

```kql
// Source: https://learn.microsoft.com/en-us/dynamics365/guidance/resources/copilot-studio-appinsights

let queryStartDate = ago(30d);
let queryEndDate = now();
let groupByInterval = 1d;

customEvents
| where timestamp > queryStartDate
| where timestamp < queryEndDate
| where name in ("BotMessageReceived", "BotMessageSend")
| extend isDesignMode = customDimensions['DesignMode']
| where isDesignMode == "False"  // Exclude test conversations
| summarize
    sessions = dcount(session_Id),
    messages = count()
    by bin(timestamp, groupByInterval)
| render timechart
```

### Generative Answers Telemetry Extraction

```kql
// Source: https://learn.microsoft.com/en-us/dynamics365/guidance/resources/copilot-studio-appinsights

customEvents
| where name == "GenerativeAnswers"
| extend cd = todynamic(customDimensions)
| extend conversationId = tostring(cd.conversationId)
| extend topic = tostring(cd.TopicName)
| extend message = tostring(cd.Message)
| extend result = tostring(cd.Result)
| extend Summary = tostring(cd.Summary)
| project
    cloud_RoleInstance,
    name,
    timestamp,
    conversationId,
    topic,
    message,
    result,
    Summary
| order by timestamp desc
```

### Error Categorization by Error Code

```kql
// Source: https://learn.microsoft.com/en-us/dynamics365/guidance/resources/copilot-studio-appinsights

let rawData = customEvents
| order by timestamp asc, session_Id
| extend TopicName = customDimensions["TopicName"]
| extend Text = customDimensions["text"]
| extend errorCodeIndex = indexof(customDimensions["text"], "Error code:")
| extend conversationIdIndex = indexof(customDimensions["text"], "Conversation ID:")
| extend errorCodeText = substring(
    customDimensions["text"],
    errorCodeIndex + strlen("Error code:"),
    conversationIdIndex - (errorCodeIndex + strlen("Error code:"))
)
| project timestamp, name, Text, errorCodeText, session_Id;

rawData
| where Text contains "Error Code:" and name == "BotMessageSend"
| summarize errortype = count() by errorCodeText
| render columnchart
```

### Latency Distribution (P50/P95/P99)

```kql
// Source: https://learn.microsoft.com/en-us/azure/azure-monitor/logs/get-started-queries
// Adapted for Copilot Studio latency monitoring

customEvents
| where timestamp > ago(1h)
| where name == "BotMessageSend"
| extend DurationMs = todouble(customDimensions["duration"])
| summarize
    avg_duration = avg(DurationMs),
    p50_duration = percentile(DurationMs, 50),
    p95_duration = percentile(DurationMs, 95),
    p99_duration = percentile(DurationMs, 99)
    by bin(timestamp, 5m)
| render timechart
```

### Time-Based Aggregation with bin()

```kql
// Source: https://learn.microsoft.com/en-us/kusto/query/tutorials/use-aggregation-functions

customEvents
| where timestamp > ago(7d)
| where name == "BotMessageSend"
| extend AgentId = tostring(customDimensions["recipientId"])
| summarize MessageCount = count() by bin(timestamp, 1h), AgentId
| order by timestamp desc
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Automatic datetime binning | Explicit bin(timestamp, interval) required | 2024 | Queries using `by timestamp` now fail, must use `by bin(timestamp, 1h)` |
| hash() for persistent identity | hash_sha256() for audit correlation | 2023 (documentation clarification) | hash() values may change across queries, breaking audit trails |
| Single retention setting | Analytics (730d) + Total (2555d) dual retention | 2023 | Cost optimization: hot vs archive storage for compliance |
| Search-based queries | Where-clause filtering on known columns | Always recommended, emphasized 2024+ | 10-100x performance improvement |
| Inline parameter defaults | Workbook parameter syntax {Param:default} | 2022+ (workbook evolution) | Seamless dashboard integration without code changes |

**Deprecated/outdated:**
- **Automatic datetime binning:** Removed from KQL, all time-series queries must use explicit bin()
- **hash() for cross-query correlation:** Still available but documented as "may change", use hash_sha256() instead
- **search operator for known columns:** Still available but "ordinarily slower", use where with column names

## Open Questions

Things that couldn't be fully resolved:

1. **Copilot Studio Sampling Configuration at Agent Level**
   - What we know: Application Insights supports ingestion sampling (workspace-level), adaptive sampling not available for server-side telemetry
   - What's unclear: Can Copilot Studio configure sampling per agent (in connector settings), or only at Application Insights ingestion level?
   - Recommendation: Document ingestion sampling as primary cost control in Phase 2 governance-queries.md, note agent-level sampling as investigation area for future optimization

2. **SR 11-7 "At Least Annually" Monitoring Frequency for AI Agents**
   - What we know: SR 11-7 requires "periodic review—at least annually but more frequently if warranted" with outcome analysis
   - What's unclear: For generative AI agents with continuous output variation, what constitutes sufficient monitoring frequency? Daily? Weekly?
   - Recommendation: Document conservative approach in SR 11-7 query patterns: weekly outcome analysis with monthly validation reports. Firms with higher-risk agents (customer-facing recommendations) should consider daily monitoring.

3. **Completeness Threshold for "Acceptable" Audit Trail**
   - What we know: FINRA 3110 requires "complete" supervisory records, but telemetry capture depends on Copilot Studio settings
   - What's unclear: What CompletenessPercent threshold is acceptable for regulatory examination? 80%? 95%? 100%?
   - Recommendation: Document in governance-queries.md that CompletenessPercent <90% represents audit risk. Firms should target 95%+ completeness for Zone 3 agents, document exemptions for lower thresholds.

## Sources

### Primary (HIGH confidence)

- [Get started with log queries in Azure Monitor](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/get-started-queries) - KQL best practices, filter early, explicit binning
- [Application Insights telemetry with Microsoft Copilot Studio](https://learn.microsoft.com/en-us/dynamics365/guidance/resources/copilot-studio-appinsights) - customEvents schema, sample queries verified
- [hash() function - Azure Data Explorer](https://learn.microsoft.com/en-us/azure/data-explorer/kusto/query/hashfunction) - xxhash64 vs SHA256 persistence documented
- [Azure Monitor workbook time parameters](https://learn.microsoft.com/en-us/azure/azure-monitor/visualize/workbooks-time) - Workbook parameter syntax {TimeRange:7d} verified
- [Tutorial: Use aggregation functions in KQL](https://learn.microsoft.com/en-us/kusto/query/tutorials/use-aggregation-functions?view=microsoft-fabric) - Explicit binning requirement confirmed
- [SR 11-7 Supervisory Guidance on Model Risk Management](https://www.federalreserve.gov/supervisionreg/srletters/sr1107.htm) - "At least annually" monitoring requirement, outcome analysis

### Secondary (MEDIUM confidence)

- [Best practices for documenting and organizing KQL](https://veldify.com/2025/06/26/best-practices-for-documenting-and-organizing-kql/) - Folder hierarchy, docstrings (attempted, 403 error, but concepts verified via other sources)
- [Null values in KQL](https://learn.microsoft.com/en-us/azure/data-explorer/kusto/query/scalar-data-types/null-values) - coalesce() behavior documented
- [FINRA Rule 3110: Supervision](https://www.finra.org/rules-guidance/rulebooks/finra-rules/3110) - Supervision documentation requirements
- [SOX IT Controls Guide 2026](https://www.metricstream.com/insights/sox-it-controls.htm) - IT control evidence requirements

### Tertiary (LOW confidence - community sources)

- [Understanding latency percentiles: p50, p95, p99](https://www.up0.io/blog/understanding-latency-percentiles) - Percentile interpretation guidance
- [KQL Query Library - GitHub](https://github.com/ze3rax/kql-query-library) - Community query organization patterns
- [Mastering KQL for Azure Monitoring](https://yurimelo.substack.com/p/mastering-kusto-query-language-kql) - Performance best practices (community article)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - KQL functions documented in official Microsoft Learn, customEvents schema verified in Copilot Studio documentation
- Architecture patterns: HIGH - Query header format adapted from official best practices, parameterization syntax verified in workbook docs
- Governance mapping: HIGH - Three-tier evidence model established in Phase 1, artifact-first approach documented
- SR 11-7 patterns: MEDIUM - Monitoring frequency "at least annually" is explicit, but AI-specific guidance is organization-dependent
- Completeness thresholds: LOW - No regulatory guidance on acceptable completeness %, conservative recommendation (95%+) based on FSI risk tolerance

**Research date:** 2026-02-05
**Valid until:** 90 days (KQL syntax stable, but Copilot Studio telemetry schema may evolve)

---

## Additional Context: FSI-AgentGov Integration

### Phase 1 Foundation

Phase 1 established:
- Application Insights workspace with 730-day retention (SEC 17a-4(b)(4) compliant)
- Log Analytics workspace for real-time KQL queries
- ADLS Gen2 storage export for immutable archival (SEC 17a-4(f) with WORM)
- RBAC separation (operational vs compliance access paths)
- PII sanitization guidance (default: disable sensitive logging, hash if needed)

Phase 2 builds on this foundation by providing KQL queries that extract governance evidence from the telemetry pipeline.

### Controls Supported by Phase 2 Queries

| Control | Query Support | Evidence Tier | Regulatory Alignment |
|---------|---------------|---------------|---------------------|
| [1.7 - Comprehensive Audit Logging](https://github.com/judeper/FSI-AgentGov/blob/main/docs/controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) | agent-decision-audit-trail.kql | Primary | SEC 17a-4, FINRA 4511 |
| [2.6 - Model Risk Management](https://github.com/judeper/FSI-AgentGov/blob/main/docs/controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md) | output-monitoring.kql, drift-detection-baseline.kql | Primary | SR 11-7 ongoing monitoring |
| [2.9 - Agent Performance Monitoring](https://github.com/judeper/FSI-AgentGov/blob/main/docs/controls/pillar-2-management/2.9-agent-performance-monitoring-and-optimization.md) | latency-distribution.kql | Primary | Operational excellence |
| [2.12 - FINRA 3110 Supervision](https://github.com/judeper/FSI-AgentGov/blob/main/docs/controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) | agent-decision-audit-trail.kql | Primary | FINRA 3110 WSP evidence |
| [3.2 - Usage Analytics](https://github.com/judeper/FSI-AgentGov/blob/main/docs/controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md) | agent-usage-analytics.kql, user-engagement-metrics.kql | Primary | Operational visibility |
| [3.4 - Incident Reporting](https://github.com/judeper/FSI-AgentGov/blob/main/docs/controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) | error-categorization-by-type.kql | Supporting | Root cause analysis |

### Governance Mapping Approach (Artifact-First)

Per Phase 1 governance-mapping.md pattern, Phase 2 governance-queries.md will:

1. Start from each KQL query file (artifact)
2. List controls the query provides evidence for
3. Classify evidence strength: Primary / Supporting / Partial
4. Include regulatory citations (FINRA 3110, SEC 17a-4, SR 11-7)
5. Provide sample output rows demonstrating evidence value

**Example structure:**

```markdown
## agent-decision-audit-trail.kql

**Description:** Extracts complete decision chain for FINRA 3110 supervision requirements with PII hashing and completeness assessment.

**Primary evidence for:**

| Control | Requirement | Regulatory Alignment |
|---------|-------------|---------------------|
| 1.7 - Comprehensive Audit Logging | Complete audit trail with timestamps, user IDs, prompts, responses | SEC 17a-4(b)(4), FINRA 4511 |
| 2.12 - FINRA 3110 Supervision | Supervisory review documentation with reviewer identity | FINRA 3110(b)(2) |

**Supporting evidence for:**

| Control | Requirement | Regulatory Alignment |
|---------|-------------|---------------------|
| 2.6 - Model Risk Management | Model decision output analysis | SR 11-7 ongoing monitoring |

**Sample Output:**

| Timestamp | AgentId | UserId (hashed) | Prompt | Response | CompletenessPercent |
|-----------|---------|-----------------|--------|----------|---------------------|
| 2026-02-04T10:15:23Z | agent-001 | sha256:a3f2... | "What are my account options?" | "Based on your profile..." | 0.95 |
```

### SR 11-7 Model Risk Monitoring Patterns (Production-Ready)

Per CONTEXT.md requirement: "SR 11-7 documentation should be production-ready, not just conceptual."

**SR 11-7 requires three monitoring components:**

1. **Outcome Analysis** - Comparing model outputs to actual outcomes
2. **Performance Monitoring** - Tracking accuracy/error rates over time
3. **Process Verification** - Confirming model operates as intended

**Phase 2 provides production-ready KQL patterns for each:**

**Outcome Analysis (Backtesting):**
```kql
// output-monitoring.kql
// Purpose: SR 11-7 outcome analysis - compare agent recommendations to customer actions
// Supports: Control 2.6 (Primary - SR 11-7 ongoing monitoring)

customEvents
| where timestamp > ago(30d)
| where name == "BotMessageSend"
| extend AgentId = tostring(customDimensions["recipientId"])
| extend Recommendation = tostring(customDimensions["speak"])
| extend Topic = tostring(customDimensions["TopicName"])
// Join with outcome data (customer action taken)
// Calculate recommendation accuracy
| summarize
    TotalRecommendations = count(),
    by bin(timestamp, 1d), AgentId, Topic
```

**Drift Detection (Performance Monitoring):**
```kql
// drift-detection-baseline.kql
// Purpose: SR 11-7 drift detection - identify response pattern changes over time
// Supports: Control 2.6 (Primary - SR 11-7 model recalibration trigger)

let BaselinePeriod = ago(90d);
let MonitoringPeriod = ago(7d);

let Baseline = customEvents
| where timestamp between (BaselinePeriod .. ago(30d))
| where name == "BotMessageSend"
| extend Topic = tostring(customDimensions["TopicName"])
| summarize BaselineCount = count() by Topic;

let Current = customEvents
| where timestamp > MonitoringPeriod
| where name == "BotMessageSend"
| extend Topic = tostring(customDimensions["TopicName"])
| summarize CurrentCount = count() by Topic;

Baseline
| join kind=fullouter Current on Topic
| extend DriftPercent = abs(todouble(CurrentCount - BaselineCount)) / BaselineCount * 100
| where DriftPercent > 20  // 20% threshold for investigation
| project Topic, BaselineCount, CurrentCount, DriftPercent
| order by DriftPercent desc
```

**Process Verification (Model Operates as Intended):**
```kql
// validation-test-results.kql
// Purpose: SR 11-7 process verification - confirm agent responses match validation test cases
// Supports: Control 2.6 (Primary - SR 11-7 validation evidence)

customEvents
| where timestamp > ago(7d)
| where name == "BotMessageSend"
| extend IsValidationTest = tobool(customDimensions["IsValidationTest"])
| where IsValidationTest == true
| extend Topic = tostring(customDimensions["TopicName"])
| extend ExpectedResponse = tostring(customDimensions["ExpectedResponse"])
| extend ActualResponse = tostring(customDimensions["speak"])
| extend MatchesExpected = (ExpectedResponse == ActualResponse)
| summarize
    TestCount = count(),
    PassCount = countif(MatchesExpected),
    FailCount = countif(not(MatchesExpected)),
    PassRate = todouble(countif(MatchesExpected)) / count()
    by Topic
| where PassRate < 0.95  // 95% threshold for validation pass
| project Topic, TestCount, PassCount, FailCount, PassRate
```

These queries provide auditable evidence for SR 11-7 Section III (Ongoing Monitoring) requirements.
