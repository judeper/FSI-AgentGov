# Schema Validation: KQL Query Library

**Project:** FSI Agent Governance Framework v15
**Phase:** 1 — Telemetry Research & KQL Query Library
**Plan:** 01-02
**Validated:** 2026-02-11
**Source Schema:** v13 Research (`.planning/phases/01-workbook-template-kql/01-RESEARCH.md`, Sections 4.1–4.7)

---

## Validation Methodology

Each query in the KQL query library (`kql-query-library.md`) was validated against five criteria:

1. **Table validation** — Query references valid Application Insights tables (`customEvents`, `exceptions`, `dependencies`, `pageViews`)
2. **Field validation** — All `customDimensions.*` fields match documented Copilot Studio telemetry schema
3. **Syntax validation** — KQL syntax is valid (proper pipe chains, function calls, operators)
4. **Parameter validation** — All `{ParameterName}` references match declared global parameters (P01–P05)
5. **Visualization validation** — Visualization type matches the data shape produced by the query

---

## Reference Schema

### Valid Tables

| Table | Populated By | Status |
|-------|-------------|--------|
| `customEvents` | Copilot Studio native telemetry | ✅ GA |
| `exceptions` | Runtime exceptions, connector failures | ✅ GA |
| `dependencies` | External API calls (connectors, knowledge sources) | ✅ GA |
| `pageViews` | Web channel conversation starts | ✅ GA (not used in workbook) |
| `requests` | Not natively populated by Copilot Studio | ❌ Not used |
| `traces` | Agent 365 SDK only (NOT Copilot Studio native) | ❌ Not used |

### Valid customDimensions Fields

| Field | Type | Always Present | Used In Queries |
|-------|------|----------------|-----------------|
| `type` | string | Yes | Q12, Q15, Q22 |
| `channelId` | string | Yes | P03, Q04 + standard filter block |
| `fromId` | string | Yes | Q02, Q03 |
| `fromName` | string | Only with sensitive properties | Not used |
| `recipientId` | string | Yes | Not used |
| `recipientName` | string | Yes | P02 + standard filter block |
| `text` | string | Only with sensitive properties | Not used |
| `designMode` | string | Yes | All `customEvents` queries |
| `TopicName` | string | On TopicStart/TopicEnd/Action | Q05, Q12, Q14, Q16 |
| `Kind` | string | Yes | Q15, Q22 |
| `locale` | string | Yes | Not used |
| `session_Id` | string | Yes | Q01, Q02, Q03, Q06, Q07, Q08, Q09, Q16, Q17, Q18, Q20, Q23 |

### Valid customEvents Event Names

| Event Name | Used In Queries |
|------------|-----------------|
| `BotMessageReceived` | Q04, Q07, Q09, Q23 |
| `BotMessageSend` | Q09, Q23 |
| `TopicStart` | Q05, Q14, Q16, Q20, Q23 |
| `TopicEnd` | Q06, Q14, Q20, Q23 |
| `Action` | Q12 |
| `GenerativeAnswers` | Q13, Q15, Q20, Q23 |

### Declared Parameters

| Parameter | ID | Type | Used By |
|-----------|-----|------|---------|
| `{TimeRange}` | P01 | Time range picker (type 4) | Q01–Q16, Q18, Q20–Q23 |
| `{AgentFilter}` | P02 | Multi-select dropdown (type 2) | Q01–Q09, Q12–Q16, Q18, Q20, Q22, Q23 |
| `{ChannelFilter}` | P03 | Multi-select dropdown (type 2) | Q01–Q03, Q05–Q09, Q12–Q16, Q20, Q23 |
| `{MinutesSaved}` | P04 | Text input (type 1) | Q08 |
| `{HourlyRate}` | P05 | Text input (type 1) | Q08 |

---

## Query-by-Query Validation

### Tab 1: Usage & Business Value

| Query | Tables Used | Fields Referenced | Table ✅ | Fields ✅ | Syntax ✅ | Params ✅ | Viz ✅ | Notes |
|-------|-----------|-------------------|----------|-----------|----------|----------|-------|-------|
| Q01 | customEvents | timestamp, session_Id, designMode, recipientName, channelId | ✅ | ✅ | ✅ | ✅ | ✅ areachart with time-binned data | — |
| Q02 | customEvents | timestamp, fromId, designMode, recipientName, channelId | ✅ | ✅ | ✅ | ✅ | ✅ timechart with time-binned data | — |
| Q03 | customEvents | timestamp, fromId, designMode, recipientName, channelId | ✅ | ✅ | ✅ | ✅ | ✅ tiles with scalar value | — |
| Q04 | customEvents | timestamp, channelId, designMode, recipientName, name | ✅ | ✅ | ✅ | ✅ | ✅ piechart with categorical data | ChannelFilter intentionally excluded |
| Q05 | customEvents | timestamp, TopicName, designMode, recipientName, channelId, name | ✅ | ✅ | ✅ | ✅ | ✅ barchart with categorical data | — |
| Q06 | customEvents | timestamp, session_Id, designMode, recipientName, channelId, name | ✅ | ✅ | ✅ | ✅ | ✅ tiles with scalar ratio | Estimated metric ⚠️ |
| Q07 | customEvents | timestamp, session_Id, designMode, recipientName, channelId, name | ✅ | ✅ | ✅ | ✅ | ✅ tiles with scalar ratio | — |
| Q08 | customEvents | timestamp, session_Id, designMode, recipientName, channelId | ✅ | ✅ | ✅ | ✅ (uses {MinutesSaved}, {HourlyRate}) | ✅ tiles with computed scalars | Estimate ⚠️ |

### Tab 2: Performance & Errors

| Query | Tables Used | Fields Referenced | Table ✅ | Fields ✅ | Syntax ✅ | Params ✅ | Viz ✅ | Notes |
|-------|-----------|-------------------|----------|-----------|----------|----------|-------|-------|
| Q09 | customEvents | timestamp, session_Id, designMode, recipientName, channelId, name | ✅ | ✅ | ✅ | ✅ | ✅ timechart multi-line with time-binned percentiles | Estimated latency ⚠️; uses `serialize`+`prev()` |
| Q10 | exceptions | timestamp | ✅ | ✅ | ✅ | ✅ | ✅ areachart with time-binned data | No agent/channel filter (exceptions table) |
| Q11 | exceptions | timestamp, outerType, type | ✅ | ✅ | ✅ | ✅ | ✅ barchart with categorical data | Uses `coalesce()` for outer/inner type |
| Q12 | customEvents | timestamp, name, designMode, recipientName, channelId, TopicName, type | ✅ | ✅ | ✅ | ✅ | ✅ table with rows | Success inferred from `type != "error"` |
| Q13 | customEvents | timestamp, name, designMode, recipientName, channelId | ✅ | ✅ | ✅ | ✅ | ✅ timechart with time-binned data | — |
| Q14 | customEvents | timestamp, name, designMode, recipientName, channelId, TopicName | ✅ | ✅ | ✅ | ✅ | ✅ table with per-topic rows | `Starts > 5` filter for relevance |
| Q15 | customEvents | timestamp, name, designMode, recipientName, channelId, type, Kind | ✅ | ✅ | ✅ | ✅ | ✅ tiles + timechart | Partial visibility ⚠️; depends on custom telemetry |
| Q16 | customEvents | timestamp, name, designMode, recipientName, channelId, TopicName, session_Id | ✅ | ✅ | ✅ | ✅ | ✅ areachart with time-binned data | Topic name matching via `has_any` |

### Tab 3: Operational Health

| Query | Tables Used | Fields Referenced | Table ✅ | Fields ✅ | Syntax ✅ | Params ✅ | Viz ✅ | Notes |
|-------|-----------|-------------------|----------|-----------|----------|----------|-------|-------|
| Q17 | customEvents | timestamp, session_Id, designMode | ✅ | ✅ | ✅ | N/A (fixed 14d lookback) | ✅ anomalychart with series data | `make-series` + `series_decompose_anomalies()` |
| Q18 | customEvents | timestamp, session_Id, designMode, recipientName | ✅ | ✅ | ✅ | ✅ | ✅ timechart with time-binned data | Proxy availability metric ⚠️ |
| Q19 | exceptions | timestamp | ✅ | ✅ | ✅ | N/A (fixed 14d lookback) | ✅ anomalychart with series data | `make-series` + `series_decompose_anomalies()` |
| Q20 | customEvents | timestamp, session_Id, designMode, recipientName, channelId, name | ✅ | ✅ | ✅ | ✅ | ✅ tiles with computed scalars | GenAI quality proxy ⚠️ |
| Q21 | dependencies | timestamp, name, target, duration, success | ✅ | ✅ | ✅ | ✅ | ✅ table with rows | Standard App Insights schema |
| Q22 | customEvents | timestamp, designMode, recipientName, type, Kind, channelId, session_Id | ✅ | ✅ | ✅ | ✅ | ✅ tiles + table | Custom telemetry dependency ⚠️ |
| Q23 | customEvents + exceptions | timestamp, session_Id, designMode, recipientName, channelId, name, TopicName | ✅ | ✅ | ✅ | ✅ | ✅ tiles per-agent | Composite query with `let` + `join` |

### Parameter Queries

| Parameter | Tables Used | Fields Referenced | Table ✅ | Fields ✅ | Syntax ✅ | Notes |
|-----------|-----------|-------------------|----------|-----------|----------|-------|
| P02 (AgentFilter) | customEvents | designMode, recipientName | ✅ | ✅ | ✅ | `distinct` with `tostring()` |
| P03 (ChannelFilter) | customEvents | designMode, channelId | ✅ | ✅ | ✅ | `distinct` with `tostring()` |

---

## Validation Summary

### Overall Results

| Criterion | Queries Checked | Pass | Fail | Notes |
|-----------|----------------|------|------|-------|
| Table validation | 25 (23 + 2 params) | 25 | 0 | All queries use valid tables |
| Field validation | 25 | 25 | 0 | All fields match documented schema |
| Syntax validation | 25 | 25 | 0 | Valid KQL syntax throughout |
| Parameter validation | 25 | 25 | 0 | All parameter references resolve |
| Visualization validation | 23 | 23 | 0 | All viz types match data shapes |

**Overall status: ✅ ALL PASS**

### Caveats and Limitations Documented

| Query | Caveat | Severity |
|-------|--------|----------|
| Q06 | Resolution rate is estimated from TopicEnd presence | ⚠️ Medium — proxy metric, documented |
| Q08 | Business value calculations use configurable estimates, not measured data | ⚠️ Low — clearly labeled as estimates |
| Q09 | Latency estimated from timestamp deltas, not precise | ⚠️ Medium — proxy metric, documented |
| Q15 | RAI content filter detail limited in native telemetry | ⚠️ Medium — may show zero events |
| Q17/Q19 | Anomaly detection uses fixed lookback, not parameterized | ℹ️ Low — by design for stable baseline |
| Q18 | Availability inferred from session presence, not health checks | ⚠️ Medium — proxy metric, documented |
| Q20 | Gen AI quality inferred from volume/fallback, not measured accuracy | ⚠️ Medium — proxy metric, documented |
| Q22 | DLP events require custom telemetry integration | ⚠️ Medium — may show zero events |

### Unavailable Data Verification

The following metrics are confirmed **NOT referenced** in any query (per plan acceptance criteria):

| Metric | Status | Reason |
|--------|--------|--------|
| Token costs per conversation | ✅ Not referenced | Not available in Copilot Studio telemetry |
| CSAT scores | ✅ Not referenced | Stays in PPAC Analytics, not sent to App Insights |
| Hallucination detection | ✅ Not referenced | Requires Azure AI Evaluation SDK |
| Grounding accuracy | ✅ Not referenced | Requires custom citation validation |

---

*Validated: 2026-02-11*
*Validator: Plan 01-02 execution*
*Schema source: v13 Research Section 4 (Copilot Studio Telemetry Schema)*
