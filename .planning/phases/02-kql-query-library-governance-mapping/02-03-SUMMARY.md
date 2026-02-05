---
phase: 02-kql-query-library-governance-mapping
plan: 03
subsystem: observability
tags: [kql, sr-11-7, model-risk, governance, compliance, finra, sec, sox]

# Dependency graph
requires:
  - phase: 02-01
    provides: Query library foundation with 6 queries (usage-analytics, error-categorization, performance)
  - phase: 02-02
    provides: Compliance queries (audit trail, completeness, RAI, generative answers, flow failures)
  - phase: 01-04
    provides: governance-mapping.md with three-tier evidence model
provides:
  - SR 11-7 model risk monitoring queries (output-monitoring, drift-detection, validation-test-results)
  - governance-queries.md comprehensive query-to-control mapping document
  - Regulatory cross-reference tables (SEC 17a-4, FINRA 3110, SR 11-7, SOX 302/404)
  - SR 11-7 Compliance Guide with investigation protocols
  - SOX 302/404 Control Evidence Guide
affects: [phase-3-workbooks, phase-4-powerbi, phase-5-compliance-automation]

# Tech tracking
tech-stack:
  added: []
  patterns: [drift-detection-baseline, validation-test-threshold, three-tier-evidence-mapping]

key-files:
  created:
    - agent-observability-foundation/queries/sr11-7-model-risk/output-monitoring.kql
    - agent-observability-foundation/queries/sr11-7-model-risk/drift-detection-baseline.kql
    - agent-observability-foundation/queries/sr11-7-model-risk/validation-test-results.kql
    - agent-observability-foundation/queries/governance-queries.md
  modified:
    - agent-observability-foundation/queries/README.md

key-decisions:
  - "20% drift threshold default with configurable parameter for higher-risk agents"
  - "95% pass rate threshold for validation tests with MeetsThreshold boolean"
  - "InvestigationRequired flag for proactive SR 11-7 compliance"
  - "Three-tier evidence model consistent with Phase 1 governance-mapping.md"

patterns-established:
  - "Drift detection: Compare 7-day window against 90-day baseline"
  - "Validation framework: IsValidationTest and TestPassed customDimensions fields"
  - "Query-to-control mapping: artifact-first with Primary/Supporting/Partial tiers"

# Metrics
duration: 4min
completed: 2026-02-05
---

# Phase 2 Plan 03: SR 11-7 Model Risk Queries & Governance Mapping Summary

**Production-ready SR 11-7 model risk KQL queries (drift detection, validation testing, outcome analysis) and comprehensive governance-queries.md mapping all 14 queries to FSI-AgentGov controls with regulatory cross-references**

## Performance

- **Duration:** 4 min
- **Started:** 2026-02-05T21:12:25Z
- **Completed:** 2026-02-05T21:16:32Z
- **Tasks:** 2
- **Files created:** 4
- **Files modified:** 1

## Accomplishments

- SR 11-7 model risk monitoring queries with 20% drift threshold and 95% validation pass rate
- Comprehensive governance-queries.md (507 lines) mapping all 14 queries to 7 FSI-AgentGov controls
- Control-to-Query and Regulatory Cross-Reference tables for audit preparation
- SR 11-7 Compliance Guide with investigation protocols and evidence package specification
- SOX 302/404 Control Evidence Guide with deficiency thresholds

## Task Commits

Each task was committed atomically:

1. **Task 1: Create SR 11-7 model risk monitoring queries** - `dc4fe63` (feat)
   - output-monitoring.kql, drift-detection-baseline.kql, validation-test-results.kql
2. **Task 2: Create comprehensive governance-queries.md mapping document** - `df172a5` (docs)
   - 507-line mapping document with control cross-references and compliance guides

**README update:** `3f83aae` (docs: update README with complete query catalog)

## Files Created/Modified

**Created:**
- `agent-observability-foundation/queries/sr11-7-model-risk/output-monitoring.kql` - SR 11-7 outcome analysis by topic/user distribution
- `agent-observability-foundation/queries/sr11-7-model-risk/drift-detection-baseline.kql` - 20% drift threshold with InvestigationRequired flag
- `agent-observability-foundation/queries/sr11-7-model-risk/validation-test-results.kql` - 95% pass rate threshold with MeetsThreshold flag
- `agent-observability-foundation/queries/governance-queries.md` - Query-to-control mapping with regulatory cross-reference

**Modified:**
- `agent-observability-foundation/queries/README.md` - Updated with complete query catalog (v1.1.0)

## Decisions Made

| Decision | Rationale |
|----------|-----------|
| 20% default drift threshold | Industry standard for general-purpose agents; higher-risk agents use 10% |
| 95% validation pass rate threshold | Production readiness standard; regulatory communications require 99% |
| InvestigationRequired boolean | Proactive flag enables alerting and workflow automation |
| Three-tier evidence model | Consistency with Phase 1 governance-mapping.md terminology |
| Validation framework fields | IsValidationTest and TestPassed customDimensions enable validation separation |

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

**Phase 2 Complete** - All 3 plans executed successfully:
- Plan 01: Query library foundation (6 queries)
- Plan 02: Compliance queries (5 queries)
- Plan 03: SR 11-7 queries (3 queries) + governance-queries.md

**Ready for Phase 3 (Workbooks and Alerts):**
- 14 KQL queries available for workbook integration
- governance-queries.md provides control traceability for dashboard design
- All queries use workbook parameter syntax `{Param:default}`

**Key artifacts for Phase 3:**
- Query library: `/agent-observability-foundation/queries/`
- Governance mapping: `/agent-observability-foundation/queries/governance-queries.md`
- Control cross-reference table enables dashboard-to-compliance linking

---
*Phase: 02-kql-query-library-governance-mapping*
*Completed: 2026-02-05*
