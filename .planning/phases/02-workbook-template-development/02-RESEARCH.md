# Phase 2 Research: Workbook Template Development

**Project:** Agent Usage & Performance Workbook (v15)
**Phase:** 2 — Workbook Template Development
**Researched:** 2026-02-11
**Overall Confidence:** HIGH

---

## Research Source

Phase 2 research is fully covered by two prior sources:

| Artifact | Location | Relevance |
|----------|----------|-----------|
| v13 Phase 1 Research | `.planning/phases/01-workbook-template-kql/01-RESEARCH.md` | 665 lines: workbook JSON structure, tab designs, visualization specs, file locations |
| v15 Phase 1 KQL Query Library | `.planning/phases/01-telemetry-research-kql-design/kql-query-library.md` | 847 lines: all 23 queries + 5 parameters, validated schema |

---

## Key Findings for Phase 2

### Workbook JSON Structure (from v13 Research §3.1)

```json
{
  "$schema": "https://github.com/Microsoft/Application-Insights-Workbooks/blob/master/schema/workbook.json",
  "version": "Notebook/1.0",
  "items": [
    { "type": 9, "content": { /* Global parameters */ } },
    { "type": 11, "content": { /* Tab group */ } }
  ],
  "fallbackResourceIds": [
    "/subscriptions/{subscription-id}/resourceGroups/{resource-group}/providers/Microsoft.Insights/components/{app-insights-name}"
  ],
  "isLocked": false
}
```

- Use `type: 11` (native tabs control) — modern Azure Workbook approach
- KQL query items use `type: 3` with `"version": "KqlItem/1.0"`
- Markdown items use `type: 1`
- Parameter items use `type: 9`
- `resourceType: "microsoft.insights/components"` for all KQL items

### Tab Designs (from KQL Query Library)

| Tab | Queries | Visualizations | Parameters Used |
|-----|---------|----------------|-----------------|
| 1: Usage & Business Value | Q01-Q08 | 8 (area, line, tiles, piechart, barchart) | TimeRange, AgentFilter, ChannelFilter, MinutesSaved, HourlyRate |
| 2: Performance & Errors | Q09-Q16 | 8 (timechart, area, barchart, table, tiles) | TimeRange, AgentFilter, ChannelFilter |
| 3: Operational Health | Q17-Q23 | 7 (anomalychart, timechart, table, tiles) | TimeRange, AgentFilter (some), 14d fixed lookback (anomaly) |

### Existing Workbook Patterns in Repo (from v13 Research §1.1)

5 inline workbook templates exist in `docs/playbooks/advanced-implementations/agent-365-observability/application-insights-workbooks.md`:
- All use `"version": "Notebook/1.0"`
- Inline `items[]` with types 1, 3, 9
- Time range parameter uses `type: 4` with `durationMs`
- Multi-select uses `type: 2` with KQL-populated dropdowns

**Gap:** Those target Agent 365 SDK (`traces` table). This workbook targets native Copilot Studio (`customEvents` table).

### Zone-Aware Thresholds (from KQL Library Appendix A)

| Metric | Zone 1 | Zone 2 | Zone 3 |
|--------|--------|--------|--------|
| Error rate alert | >10% | >5% | >2% |
| Latency alert (P95) | — | >5,000 ms | >3,000 ms |
| Anomaly sensitivity | — | 2.0 | 1.5 |
| Escalation rate alert | — | >25% | >15% |
| Resolution rate minimum | — | >60% | >80% |

### File Location

- Workbook JSON: `src/agent-usage-workbook.json` (consistent with existing `src/` conventions)
- Adjacent to: `adaptive-card-caa-alert.json`, `caa-daily-compliance-flow.json`, `caa-provisioning-hook-flow.json`

### Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Large JSON file difficult to maintain | Medium | Low | Organize with clear section comments, structure tabs as logical groups |
| Visualization type mismatch | Low | Medium | Map each query's `render` hint to workbook `visualization` property |
| Parameter reference errors | Low | Medium | Use consistent `{ParameterName}` syntax matching KQL library |
| Tab group nesting complexity | Medium | Medium | Follow Azure Workbook type 11 (tabs) pattern; test structure validity with JSON parser |

---

**No additional research required.** v13 research + Phase 1 KQL query library provide complete technical foundation for workbook construction.

*Research referenced: 2026-02-11*
*Sources: .planning/phases/01-workbook-template-kql/01-RESEARCH.md (v13), .planning/phases/01-telemetry-research-kql-design/kql-query-library.md (v15)*
