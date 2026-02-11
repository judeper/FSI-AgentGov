---
phase: 2
plan: 1
title: "Workbook shell + Usage & Business Value tab + Performance & Errors tab"
status: Complete
completed: 2026-02-11
---

# Plan 02-01 Summary: Workbook Shell + Tabs 1-2

**Status:** Complete
**Completed:** 2026-02-11

## Files Created

| File | Size | Purpose |
|------|------|---------|
| `src/agent-usage-workbook.json` | 29,346 bytes (28.7 KB) | Azure Monitor Workbook JSON template |

## What Was Built

### Workbook JSON Shell
- Root structure: `$schema`, `version: "Notebook/1.0"`, `items[]`, `fallbackResourceIds[]`, `isLocked: false`
- Parameterized `fallbackResourceIds` with `{subscription-id}`, `{resource-group}`, `{app-insights-name}` placeholders
- Markdown header (type 1) with title, version, description, and regulatory scope note

### Global Parameters (type 9, 5 parameters)
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| TimeRange | 4 (time range picker) | 86400000ms (24h) | 8 selectable ranges + custom |
| AgentFilter | 2 (multi-select dropdown) | All | KQL-populated from `customEvents.recipientName` |
| ChannelFilter | 2 (multi-select dropdown) | All | KQL-populated from `customEvents.channelId` |
| MinutesSaved | 1 (text input) | "5" | Business value calculation input |
| HourlyRate | 1 (text input) | "75" | Business value calculation input |

### Tab Container (type 11, 3 tabs)
- Tab 1: "Usage & Business Value" → `selectedTab = 1`
- Tab 2: "Performance & Errors" → `selectedTab = 2`
- Tab 3: "Operational Health" → `selectedTab = 3` (placeholder for Plan 02-02)

### Tab 1: Usage & Business Value (8 query items)
| Query | Title | Visualization | Size |
|-------|-------|---------------|------|
| Q01 | Session Volume Trend | timechart | 0 |
| Q02 | Daily Active Users | timechart | 0 |
| Q03 | Monthly Active Users | tiles | 4 |
| Q04 | Channel Breakdown | piechart | 1 |
| Q05 | Top Topics by Engagement | barchart | 1 |
| Q06 | Resolution Rate | tiles | 4 |
| Q07 | Average Messages per Session | tiles | 4 |
| Q08 | Business Value Summary | tiles | 1 |

### Tab 2: Performance & Errors (9 query items + 1 markdown caveat)
| Query | Title | Visualization | Size |
|-------|-------|---------------|------|
| — | Latency Estimation Caveat | markdown (type 1) | — |
| Q09 | Response Latency P50/P95/P99 | timechart | 0 |
| Q10 | Error Rate Trend | timechart | 0 |
| Q11 | Error Types Breakdown | barchart | 1 |
| Q12 | Connector/Action Success Rate | table | 1 |
| Q13 | Generative AI Usage Trend | timechart | 0 |
| Q14 | Topic Completion Rate | table | 1 |
| Q15a | RAI Content Filtering Events | tiles | 4 |
| Q15b | RAI Content Filtering Trend | timechart | 0 |
| Q16 | Fallback/Escalation Volume | timechart | 0 |

### Tab 3: Operational Health (placeholder)
- Single markdown item: "Operational Health tab — populated in Plan 02-02"

## Key Decisions

1. **Q04 Channel Breakdown** — intentionally omits ChannelFilter to show full distribution
2. **Q10, Q11 Exceptions** — intentionally omit AgentFilter/ChannelFilter (exceptions table does not have `customDimensions` with those fields)
3. **Q15 dual items** — split into Q15a (tiles KPI count) and Q15b (timechart trend) per design spec
4. **Latency caveat** — markdown note (type 1) placed before Q09 explaining the timestamp-delta estimation limitation
5. **Parameter defaults** — AgentFilter and ChannelFilter default to `value::all` with `multiSelect: true` and proper quote/delimiter settings for KQL `in()` syntax
6. **Deterministic GUIDs** — used `a1b2c3d4-XXXX-XXXX-XXXX-XXXXXXXXXXXX` pattern for all id fields

## Verification Results

| Check | Result |
|-------|--------|
| JSON valid (parseable) | Pass |
| Top-level items | 6 (header, params, tabs, tab1-group, tab2-group, tab3-group) |
| Tab 1 query items | 8 (Q01-Q08) |
| Tab 2 query items | 9 (Q09-Q16 with Q15 dual) |
| Tab 2 markdown items | 1 (latency caveat) |
| Tab 3 placeholder items | 1 |
| Total visualization items | 17 queries + 1 markdown = 18 content items |
| Parameters declared | 5 (TimeRange, AgentFilter, ChannelFilter, MinutesSaved, HourlyRate) |
| All parameter refs match | Pass |
| File size | 29,346 bytes |

## Dependency for Next Plan

Plan 02-02 will populate Tab 3 (Operational Health) with Q17-Q20 queries and zone-aware threshold logic.
