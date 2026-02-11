---
phase: 2
plan: 2
title: "Operational Health tab + template finalization + zone-aware thresholds"
status: Complete
completed: 2026-02-11
---

# Plan 02-02 Summary: Operational Health Tab + Template Finalization

**Status:** Complete
**Completed:** 2026-02-11

## Files Modified

| File | Before | After | Purpose |
|------|--------|-------|---------|
| `src/agent-usage-workbook.json` | 29,346 bytes / 552 lines | 46,707 bytes / 795 lines | Added Tab 3, zone thresholds, enhanced header |

## What Was Built

### 1. Operational Health Tab (Tab 3) — Q17-Q23

Replaced the Tab 3 placeholder with 8 query items + 3 markdown items:

| Query | Title | Visualization | Size | TimeRange | Filters |
|-------|-------|---------------|------|-----------|---------|
| — | Tab 3 Header | markdown (type 1) | — | — | — |
| Q17 | Session Volume Anomaly Detection | timechart | 0 | Fixed 14d | None (global anomaly) |
| — | Availability Proxy Caveat | markdown (type 1) | — | — | — |
| Q18 | Availability (Uptime Trend) | timechart | 0 | Yes | AgentFilter only |
| Q19 | Exception Spike Detection | timechart | 0 | Fixed 14d | None |
| Q20 | Generative Answers Quality | tiles | 4 | Yes | Agent + Channel |
| Q21 | Dependency Health | table | 1 | Yes | None (dependencies table) |
| — | DLP Custom Telemetry Caveat | markdown (type 1) | — | — | — |
| Q22a | DLP/Security Events (count) | tiles | 4 | Yes | AgentFilter only |
| Q22b | DLP/Security Event Detail | table | 1 | Yes | AgentFilter only |
| Q23 | Agent Health Summary | table | 0 | Yes | Agent + Channel |

### 2. Zone-Aware Threshold Formatting

Applied conditional formatting thresholds across all 3 tabs:

| Query | Column | Green | Yellow | Red | Type |
|-------|--------|-------|--------|-----|------|
| Q06 | ResolutionRate | ≥80% | ≥60% | <60% | tileSettings.thresholds |
| Q12 | SuccessRate | ≥95% | ≥90% | <90% | gridSettings.thresholdsGrid |
| Q14 | CompletionRate | ≥80% | ≥60% | <60% | gridSettings.thresholdsGrid |
| Q20 | EstFallbackRate | <15% | <25% | ≥25% | tileSettings.thresholds |
| Q21 | SuccessRate | ≥95% | ≥90% | <90% | gridSettings.thresholdsGrid |
| Q23 | CompletionRate | ≥80% | ≥60% | <60% | gridSettings.thresholdsGrid |

All thresholds default to Zone 3 (Enterprise Managed) targets.

### 3. Enhanced Header

Updated the workbook header markdown to include:
- Title: "Agent Usage & Performance Workbook"
- Version: v1.0.0
- Framework: FSI Agent Governance Framework v1.2.38
- Description referencing Control 2.8 ALM gap
- 3-tab overview table
- Prerequisites (Application Insights, telemetry export, Reader access)
- Zone threshold customization guidance note

### 4. Design Decisions

1. **Q17, Q19 fixed lookback** — No `timeContext`/`timeContextFromParameter` to maintain stable 14-day anomaly baselines
2. **Q18 excludes ChannelFilter** — Availability is measured across all channels
3. **Q21 excludes AgentFilter/ChannelFilter** — `dependencies` table does not contain agent-specific custom dimensions
4. **Q22 excludes ChannelFilter** — DLP events filtered by agent but channel not reliably present in security event telemetry
5. **Q20 inverted thresholds** — EstFallbackRate uses `<` operators since lower values are better
6. **Q22 dual items** — Split into Q22a (KPI tile count) and Q22b (detail table) for at-a-glance + drill-down pattern
7. **Availability proxy caveat** — Explicit markdown note that Q18 uses session activity, not actual uptime monitoring
8. **DLP custom telemetry caveat** — Explicit note that Q22 requires custom event types beyond default Copilot Studio telemetry

## Verification Results

| Check | Result |
|-------|--------|
| JSON valid (parseable) | ✓ Pass |
| Query items (type 3) | 25 |
| Markdown items (type 1) | 5 |
| Q01-Q23 all present | ✓ Pass (all 23 unique query IDs) |
| Q15 dual items | 2 (Q15a + Q15b) |
| Q22 dual items | 2 (Q22a + Q22b) |
| No `traces` table references | ✓ Pass |
| `designMode` in all customEvents queries | ✓ Pass (24 customEvents / 24 designMode) |
| No hardcoded GUIDs | ✓ Pass (only a1b2c3d4-* parameter GUIDs) |
| Parameters declared | 5 (TimeRange, AgentFilter, ChannelFilter, MinutesSaved, HourlyRate) |
| All `{ParameterName}` references resolve | ✓ Pass |
| Tile thresholds (tileSettings) | 2 (Q06, Q20) |
| Grid thresholds (thresholdsGrid) | 4 (Q12, Q14, Q21, Q23) |
| `isLocked` | false |
| `fallbackResourceIds` | Parameterized placeholder |
| File size | 46,707 bytes (45.6 KB) |
| Total lines | 795 |

### Item Counts by Tab

| Tab | Query Items | Markdown Items | Total Items |
|-----|-------------|----------------|-------------|
| Tab 1: Usage & Business Value | 8 | 0 | 8 |
| Tab 2: Performance & Errors | 9 | 1 | 10 |
| Tab 3: Operational Health | 8 | 3 | 11 |
| **Total (in groups)** | **25** | **4** | **29** |
| Header (top-level) | — | 1 | 1 |
| **Grand Total** | **25** | **5** | **30** |

## Completed Plan Requirements

- [x] WBK-03: Operational Health tab with Q17-Q23 visualizations
- [x] WBK-04: Deployable template finalization with zone-aware thresholds
- [x] All 23 KQL queries from Phase 1 query library present in workbook
- [x] Zone-aware conditional formatting on applicable KPI tiles
- [x] Enhanced header with version, framework reference, prerequisites, threshold guidance
- [x] Template importable via Azure Portal → Monitor → Workbooks → Advanced Editor

## Dependency for Next Plan

The complete `src/agent-usage-workbook.json` (795 lines, 25 queries, 3 tabs) is ready for Phase 3, which covers deployment documentation, customization guidance, and ARM template integration.

---

*Summary completed: 2026-02-11*
