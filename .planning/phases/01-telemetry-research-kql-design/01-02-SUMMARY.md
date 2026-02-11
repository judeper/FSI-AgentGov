# Plan 01-02 Summary: KQL Query Library for All Workbook Tabs

**Phase:** 1 — Telemetry Research & KQL Query Library
**Plan:** 02
**Wave:** 1
**Status:** COMPLETE
**Executed:** 2026-02-11

---

## Dependency Graph

```
Plan 01-01 (Telemetry Schema)  ──┐
                                 ├──► Phase 2 (Workbook JSON Construction)
Plan 01-02 (KQL Query Library) ──┘
```

Plan 01-02 has no dependencies — executed in parallel with Plan 01-01 (Wave 1).

## Tech Stack

| Component | Usage |
|-----------|-------|
| KQL (Kusto Query Language) | All 23 queries |
| Application Insights | Target telemetry store (customEvents, exceptions, dependencies) |
| Azure Monitor Workbooks | Visualization layer (Phase 2) |
| Copilot Studio Native Telemetry | Source data schema |

## Key Files

| File | Action | Description |
|------|--------|-------------|
| `.planning/phases/01-telemetry-research-kql-design/kql-query-library.md` | Created | Complete KQL query library — 23 queries + 5 parameters |
| `.planning/phases/01-telemetry-research-kql-design/schema-validation.md` | Created | Schema validation results — 25/25 pass all criteria |
| `.planning/phases/01-telemetry-research-kql-design/01-02-SUMMARY.md` | Created | This summary |

## Deliverables

### KQL Query Library (kql-query-library.md)

**Tab 1: Usage & Business Value — 8 queries:**
- Q01: Session Volume Trend (timechart/area)
- Q02: Daily Active Users (timechart/line)
- Q03: Monthly Active Users (tiles/KPI)
- Q04: Channel Breakdown (piechart)
- Q05: Top Topics by Engagement (barchart/horizontal)
- Q06: Resolution Rate (tiles/KPI) — *estimated metric*
- Q07: Average Messages per Session (tiles/KPI)
- Q08: Business Value Summary (tiles/4-wide KPI) — uses {MinutesSaved}, {HourlyRate}

**Tab 2: Performance & Errors — 8 queries:**
- Q09: Response Latency P50/P95/P99 (timechart/multi-line) — *estimated metric*
- Q10: Error Rate Trend (timechart/area)
- Q11: Error Types Breakdown (barchart/stacked)
- Q12: Connector/Action Success Rate (table/grid)
- Q13: Generative AI Usage Trend (timechart/line)
- Q14: Topic Completion Rate (table/grid)
- Q15: RAI Content Filtering Events (tiles + timechart) — *partial visibility*
- Q16: Fallback/Escalation Volume (timechart/area)

**Tab 3: Operational Health — 7 queries:**
- Q17: Session Volume Anomaly Detection (anomalychart)
- Q18: Availability/Uptime Trend (timechart/line) — *proxy metric*
- Q19: Exception Spike Detection (anomalychart)
- Q20: Generative Answers Quality (tiles/KPI)
- Q21: Dependency Health (table/grid)
- Q22: DLP/Security Events (tiles + table) — *requires custom telemetry*
- Q23: Agent Health Summary (tiles/per-agent) — *composite query*

**Global Parameters — 5:**
- P01: TimeRange (type 4 — time range picker, default 24h)
- P02: AgentFilter (type 2 — KQL-populated multi-select dropdown)
- P03: ChannelFilter (type 2 — KQL-populated multi-select dropdown)
- P04: MinutesSaved (type 1 — text input, default 5)
- P05: HourlyRate (type 1 — text input, default 75)

### Schema Validation (schema-validation.md)

| Criterion | Queries | Pass | Fail |
|-----------|---------|------|------|
| Table validation | 25 | 25 | 0 |
| Field validation | 25 | 25 | 0 |
| Syntax validation | 25 | 25 | 0 |
| Parameter validation | 25 | 25 | 0 |
| Visualization validation | 23 | 23 | 0 |

**Overall: ✅ ALL PASS**

### Zone-Aware Thresholds (Appendix A)

| Metric | Zone 1 | Zone 2 | Zone 3 |
|--------|--------|--------|--------|
| Error rate alert | >10% | >5% | >2% |
| Latency alert (P95) | — | >5s | >3s |
| Anomaly sensitivity | — | 2.0 | 1.5 |
| Review frequency | Monthly | Weekly | Daily + real-time |

## Acceptance Criteria Status

- [x] 8 Usage/Business Value queries documented with full KQL, visualization type, and regulatory comments
- [x] 8 Performance/Errors queries documented with full KQL, visualization type, and regulatory comments
- [x] 7 Operational Health queries documented with full KQL, visualization type, and regulatory comments
- [x] 5 global parameters defined (3 KQL-populated dropdowns, 2 text inputs)
- [x] All queries include designMode filtering (`customDimensions.designMode == "False"`)
- [x] All queries parameterized with {TimeRange}, {AgentFilter}, {ChannelFilter} where applicable
- [x] Schema validation: all queries reference valid tables
- [x] Schema validation: all customDimensions fields match documented schema
- [x] Schema validation: visualization types match data shapes
- [x] Zone-aware threshold notes documented
- [x] Latency estimation logic clearly documented with limitations caveat
- [x] Resolution rate inference logic documented with limitations caveat
- [x] No queries reference unavailable data (token costs, CSAT, hallucination metrics)

## Design Decisions

1. **ChannelFilter excluded from Q04 (Channel Breakdown)** — The purpose of this visualization is to show distribution across all channels; applying a channel filter would defeat that purpose.

2. **Exceptions table queries (Q10, Q11, Q19) lack agent/channel filters** — The `exceptions` table does not include Copilot Studio-specific `customDimensions` fields. An `operation_Id` join pattern is documented in Appendix B for advanced use but excluded from standard queries for performance.

3. **Anomaly detection queries (Q17, Q19) use fixed 14d lookback** — TimeRange parameter is not applied to ensure a stable statistical baseline. Sensitivity threshold of 1.5 matches Zone 3 requirements.

4. **RAI events (Q15) and DLP events (Q22) may return empty results** — Native Copilot Studio telemetry has limited RAI/DLP event detail. Queries are designed to degrade gracefully (show 0 instead of errors). Full RAI/DLP monitoring requires Purview Audit or custom telemetry integration.

5. **Q23 (Agent Health Summary) excludes per-agent error counts** — The `exceptions` table cannot be correlated to specific agents without `operation_Id` joins. Error analysis is handled by Q10/Q11 at the aggregate level.

## Issues Encountered

None. All queries were successfully refined from v13 research patterns with consistent parameterization and regulatory comments.

## Git Commits

| Commit | Description |
|--------|-------------|
| `4074a0e` | feat(v15): Plan 01-02 KQL query library and schema validation |

---

*Summary created: 2026-02-11*
*Next: Phase 2 — Workbook JSON Construction (consumes this query library)*
