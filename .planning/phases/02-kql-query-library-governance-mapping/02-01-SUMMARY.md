---
phase: 02-kql-query-library-governance-mapping
plan: 01
subsystem: observability
tags: [kql, application-insights, azure-monitor, telemetry, governance]

# Dependency graph
requires:
  - phase: 01-telemetry-infrastructure-solution-foundation
    provides: Application Insights workspace, governance-mapping.md control references
provides:
  - KQL query library with function-based organization
  - Usage analytics queries (sessions, engagement)
  - Error categorization queries (connector/knowledge/orchestration)
  - Performance queries (P50/P95/P99 latency)
  - Query header format standard with control references
affects: [phase-02-02, phase-02-03, phase-03, phase-04]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - Query header format with Purpose/Parameters/Output Schema/Supports/Sample Output
    - Workbook parameter syntax {TimeRange:default}
    - hash_sha256() for PII-safe user correlation
    - Function-based folder organization (not regulation-based)

key-files:
  created:
    - agent-observability-foundation/queries/README.md
    - agent-observability-foundation/queries/usage-analytics/agent-usage-analytics.kql
    - agent-observability-foundation/queries/usage-analytics/user-engagement-metrics.kql
    - agent-observability-foundation/queries/error-categorization/error-categorization-by-type.kql
    - agent-observability-foundation/queries/error-categorization/error-trend-analysis.kql
    - agent-observability-foundation/queries/performance/latency-distribution.kql
    - agent-observability-foundation/queries/performance/slow-query-detection.kql
  modified: []

key-decisions:
  - "Function-based query organization for reusability across regulations"
  - "Comprehensive header blocks with inline control references"
  - "Workbook parameter syntax for dashboard integration"

patterns-established:
  - "Query header: Purpose, Parameters, Output Schema, Supports, Sample Output"
  - "hash_sha256() for persistent PII hashing"
  - "Early filtering with where timestamp > ago(TimeRange)"

# Metrics
duration: 3min
completed: 2026-02-05
---

# Phase 02 Plan 01: KQL Query Library Foundation Summary

**Function-based KQL query library with 6 production queries covering usage analytics (KQL-01), error categorization (KQL-02), and latency distribution (KQL-03) aligned to FSI-AgentGov controls**

## Performance

- **Duration:** 3 min
- **Started:** 2026-02-05T21:03:53Z
- **Completed:** 2026-02-05T21:06:51Z
- **Tasks:** 2
- **Files created:** 7

## Accomplishments

- Created query library directory structure with 5 function-based folders
- Documented comprehensive README with usage instructions, parameter syntax, and PII handling
- Built 6 KQL queries with standardized header blocks and inline control references
- Established query header format as reusable pattern for future queries

## Task Commits

Each task was committed atomically:

1. **Task 1: Create query library structure and README** - `29da69e` (docs)
2. **Task 2: Create usage analytics, performance, and error queries** - `ce61beb` (feat)

## Files Created/Modified

**Repository:** FSI-AgentGov-Solutions

| File | Purpose |
|------|---------|
| `agent-observability-foundation/queries/README.md` | Query library overview, usage instructions, PII handling |
| `agent-observability-foundation/queries/usage-analytics/agent-usage-analytics.kql` | 30-day session/message trends (Control 3.2 Primary) |
| `agent-observability-foundation/queries/usage-analytics/user-engagement-metrics.kql` | Distinct users with hash_sha256() (Control 3.2 Primary) |
| `agent-observability-foundation/queries/error-categorization/error-categorization-by-type.kql` | Connector/knowledge/orchestration buckets (Control 3.4 Primary) |
| `agent-observability-foundation/queries/error-categorization/error-trend-analysis.kql` | Hourly error rate (Control 3.4 Supporting) |
| `agent-observability-foundation/queries/performance/latency-distribution.kql` | P50/P95/P99 percentiles (Control 2.9 Primary) |
| `agent-observability-foundation/queries/performance/slow-query-detection.kql` | Threshold-based detection (Control 2.9 Supporting) |

## Decisions Made

1. **Function-based organization over regulation-based:** Queries organized by function (usage-analytics, error-categorization, performance) to maximize reusability. A single query often supports multiple regulations.

2. **Comprehensive header blocks:** Every .kql file includes Purpose, Parameters, Output Schema, Supports (control references), and Sample Output for self-contained documentation.

3. **Workbook parameter syntax:** Used `{TimeRange:default}` syntax for seamless Azure Monitor Workbook integration. README documents how to test in Log Analytics with literal values.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

**Ready for 02-02-PLAN.md:** Compliance and audit trail queries

- Query library structure established
- Header format pattern defined
- compliance/ and sr11-7-model-risk/ folders ready for additional queries
- Phase 2 Plan 02 will add agent-decision-audit-trail.kql and completeness-assessment.kql

**Dependencies satisfied:**
- Phase 1 governance-mapping.md provides control references
- Query header format established for consistency

---
*Phase: 02-kql-query-library-governance-mapping*
*Completed: 2026-02-05*
