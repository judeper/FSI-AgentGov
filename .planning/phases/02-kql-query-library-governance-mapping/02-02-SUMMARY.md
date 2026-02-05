---
phase: 02-kql-query-library-governance-mapping
plan: 02
subsystem: observability
tags: [kql, compliance, finra-3110, sec-17a-4, rai, power-automate, audit-trail]

# Dependency graph
requires:
  - phase: 01-telemetry-infrastructure-solution-foundation
    provides: Application Insights customEvents table with Copilot Studio telemetry
provides:
  - FINRA 3110 audit trail query with PII hashing and completeness metrics
  - RAI content filtering detection (XPIADetected, JailbreakDetected)
  - Generative answers telemetry extraction for SR 11-7 outcome analysis
  - Power Automate flow failure correlation
  - Telemetry completeness assessment with ComplianceRisk categorization
affects: [03-workbooks-alerts, governance-queries.md]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "KQL query header block format with Supports section"
    - "hash_sha256() for persistent PII hashing"
    - "coalesce() with NOT_CAPTURED for graceful null handling"
    - "CompletenessPercent calculation for audit readiness"

key-files:
  created:
    - agent-observability-foundation/queries/compliance/agent-decision-audit-trail.kql
    - agent-observability-foundation/queries/compliance/completeness-assessment.kql
    - agent-observability-foundation/queries/compliance/rai-content-filtering-detection.kql
    - agent-observability-foundation/queries/compliance/generative-answers-telemetry.kql
    - agent-observability-foundation/queries/compliance/flow-failure-correlation.kql
  modified: []

key-decisions:
  - "IncludePII parameter for authorized reviewers (default: hashed)"
  - "ComplianceRisk thresholds: HIGH (<80%), MEDIUM (80-90%), LOW (>90%)"
  - "All queries use workbook parameter syntax for dashboard integration"

patterns-established:
  - "Comprehensive header blocks with Purpose, Parameters, Output Schema, Supports, Regulatory Mapping, Sample Output, Notes"
  - "Privacy-by-default with hash_sha256() for all UserId fields"
  - "Inline control references (Supports section) for governance traceability"

# Metrics
duration: 6min
completed: 2026-02-05
---

# Phase 2 Plan 02: Compliance Queries Summary

**5 compliance-focused KQL queries for FINRA 3110 audit trails, RAI content filtering, generative answers telemetry, and Power Automate flow failure correlation with privacy-by-default PII hashing**

## Performance

- **Duration:** 6 min
- **Started:** 2026-02-05T21:04:59Z
- **Completed:** 2026-02-05T21:11:00Z
- **Tasks:** 2
- **Files created:** 5

## Accomplishments

- FINRA 3110 decision audit trail with CompletenessPercent for pre-audit gap detection
- IncludePII parameter enabling authorized reviewers to access raw UserId while defaulting to hash_sha256()
- XPIADetected and JailbreakDetected event detection from Microsoft Purview RAI filtering
- Generative answers telemetry extraction supporting SR 11-7 outcome analysis
- Power Automate flow failure correlation with conversation context joining

## Task Commits

Each task was committed atomically:

1. **Task 1: Create audit trail and completeness queries** - `09d2f0d` (feat)
2. **Task 2: Create RAI, generative answers, and flow failure queries** - `74b56db` (feat)

## Files Created

- `agent-observability-foundation/queries/compliance/agent-decision-audit-trail.kql` - FINRA 3110 decision chain with PII hashing, CompletenessPercent
- `agent-observability-foundation/queries/compliance/completeness-assessment.kql` - Daily telemetry gap detection with ComplianceRisk (HIGH/MEDIUM/LOW)
- `agent-observability-foundation/queries/compliance/rai-content-filtering-detection.kql` - XPIADetected/JailbreakDetected event filtering
- `agent-observability-foundation/queries/compliance/generative-answers-telemetry.kql` - Topic, result, feedback extraction for response quality
- `agent-observability-foundation/queries/compliance/flow-failure-correlation.kql` - Power Automate failure correlation with MicrosoftFlow events

## Decisions Made

1. **IncludePII parameter with default=false** - Authorized supervisors can toggle to see raw UserId for FINRA 3110 investigations, but default protects privacy
2. **ComplianceRisk thresholds** - HIGH (<80%), MEDIUM (80-90%), LOW (>90%) based on Phase 1 governance-mapping.md guidance (95%+ target for Zone 3)
3. **Workbook parameter syntax** - All queries use `{Parameter:default}` format for seamless Azure Monitor Workbook integration

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- **Ready:** 5 compliance queries available in `queries/compliance/` directory
- **Ready:** All queries have complete header blocks with Supports section for governance-queries.md integration
- **Pending:** Plan 02-03 will update governance-queries.md with comprehensive control mapping
- **Pending:** Phase 3 will create Azure Monitor Workbooks consuming these KQL queries

---
*Phase: 02-kql-query-library-governance-mapping*
*Completed: 2026-02-05*
