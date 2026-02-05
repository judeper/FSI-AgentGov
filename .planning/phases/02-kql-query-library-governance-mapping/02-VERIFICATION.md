---
phase: 02-kql-query-library-governance-mapping
verified: 2026-02-05T16:30:00Z
status: passed
score: 10/10 must-haves verified
re_verification: false
---

# Phase 2: KQL Query Library & Governance Mapping Verification Report

**Phase Goal:** Reusable KQL queries enable consistent metrics across all visualization layers with governance compliance patterns.

**Verified:** 2026-02-05T16:30:00Z

**Status:** PASSED

**Re-verification:** No - initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | User can run agent-usage-analytics.kql and see 30-day trend of sessions | VERIFIED | Query contains `{TimeRange:30d}` parameter, `bin(timestamp, 1d)` aggregation, `SessionCount`, `MessageCount`, `CompletionRate` output columns |
| 2 | User can run latency-distribution.kql and see P50/P95/P99 response times | VERIFIED | Query contains `percentile(DurationMs, 50)`, `percentile(DurationMs, 95)`, `percentile(DurationMs, 99)` function calls |
| 3 | User can run error-categorization-by-type.kql and see connector/knowledge/orchestration buckets | VERIFIED | Query contains `case()` statement categorizing errors into "Connector", "Knowledge", "Orchestration" based on `errorCodeText` patterns |
| 4 | User can generate FINRA 3110 audit trail with timestamps, UserId, Prompt, Response | VERIFIED | `agent-decision-audit-trail.kql` contains `Timestamp`, `UserId`, `Prompt`, `Response`, `CompletenessPercent` with `hash_sha256()` for PII protection |
| 5 | User can detect RAI content filtering events (XPIADetected, JailbreakDetected) | VERIFIED | `rai-content-filtering-detection.kql` filters for `XPIADetected`, `JailbreakDetected`, `ContentFilterResult` with `FilterType` categorization |
| 6 | User can identify telemetry completeness gaps before regulatory audits | VERIFIED | `completeness-assessment.kql` calculates `CompletenessPercent`, `RecordsBelow80Percent`, `ComplianceRisk` (HIGH/MEDIUM/LOW) |
| 7 | User can correlate Power Automate flow failures with agent conversations | VERIFIED | `flow-failure-correlation.kql` filters for "MicrosoftFlow", "ActionFailed" events with join to conversation context |
| 8 | User can identify which KQL queries provide evidence for specific framework controls | VERIFIED | `governance-queries.md` (507 lines) contains Control-to-Query Cross-Reference table at line 353 |
| 9 | User can generate SR 11-7 model risk monitoring report using documented patterns | VERIFIED | `governance-queries.md` contains "SR 11-7 Model Risk Compliance Guide" section at line 381 with outcome analysis, drift detection, validation testing guidance |
| 10 | User can detect response pattern drift exceeding 20% threshold | VERIFIED | `drift-detection-baseline.kql` contains `{DriftThreshold:20}` parameter, `DriftPercent` calculation, `InvestigationRequired` boolean |

**Score:** 10/10 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `queries/README.md` | Query library overview, 50+ lines | VERIFIED | 242 lines, documents all 5 subfolders, {TimeRange} syntax, hash_sha256() PII handling, CompletenessPercent purpose |
| `queries/usage-analytics/agent-usage-analytics.kql` | Session trends, TimeRange parameter | VERIFIED | 48 lines, {TimeRange:30d}, SessionCount, MessageCount, CompletionRate, // Supports: 3.2, 2.9 |
| `queries/usage-analytics/user-engagement-metrics.kql` | Distinct users with hashing | VERIFIED | 48 lines, hash_sha256(UserIdRaw), DistinctUsers, SessionsPerUser |
| `queries/error-categorization/error-categorization-by-type.kql` | Error buckets | VERIFIED | 61 lines, case() with Connector/Knowledge/Orchestration, errorCodeText parsing |
| `queries/error-categorization/error-trend-analysis.kql` | Error rate over time | VERIFIED | 46 lines, hourly ErrorRate calculation |
| `queries/performance/latency-distribution.kql` | P50/P95/P99 | VERIFIED | 53 lines, percentile() function calls for 50, 95, 99 |
| `queries/performance/slow-query-detection.kql` | Threshold-based detection | VERIFIED | 49 lines, {ThresholdMs:5000} parameter, DurationMs > ThresholdMs filter |
| `queries/compliance/agent-decision-audit-trail.kql` | FINRA 3110 audit trail | VERIFIED | 70 lines, {IncludePII:false}, hash_sha256(), CompletenessPercent, Prompt, Response, SupervisorId |
| `queries/compliance/completeness-assessment.kql` | Telemetry gap detection | VERIFIED | 63 lines, CompletenessPercent, ComplianceRisk HIGH/MEDIUM/LOW |
| `queries/compliance/rai-content-filtering-detection.kql` | XPIADetected events | VERIFIED | 66 lines, XPIADetected, JailbreakDetected, ContentFilterResult parsing |
| `queries/compliance/generative-answers-telemetry.kql` | GenerativeAnswers events | VERIFIED | 59 lines, name == "GenerativeAnswers", Topic, Result, Summary, HasFeedback |
| `queries/compliance/flow-failure-correlation.kql` | Power Automate failures | VERIFIED | 85 lines, MicrosoftFlow/ActionFailed filtering, CorrelationId join |
| `queries/sr11-7-model-risk/output-monitoring.kql` | Outcome analysis | VERIFIED | 48 lines, // Supports: 2.6 (Primary), TotalRecommendations, DistinctUsers |
| `queries/sr11-7-model-risk/drift-detection-baseline.kql` | Drift detection | VERIFIED | 69 lines, DriftPercent, DriftThreshold, InvestigationRequired |
| `queries/sr11-7-model-risk/validation-test-results.kql` | Validation pass rates | VERIFIED | 56 lines, PassRate, PassRateThreshold, MeetsThreshold, IsValidationTest filter |
| `queries/governance-queries.md` | Query-to-control mapping | VERIFIED | 507 lines (>200), Control-to-Query table, Regulatory Cross-Reference, SR 11-7 Compliance Guide, SOX 302/404 Evidence Guide |

**Artifact Count:** 16/16 artifacts verified

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| README.md | all .kql files | folder documentation | VERIFIED | README documents all 5 subfolders with query descriptions |
| each .kql file | FSI-AgentGov controls | // Supports: X.X comments | VERIFIED | 15 files contain "Supports:" header (14 .kql + README) |
| governance-queries.md | all .kql files | query-to-control mapping tables | VERIFIED | All 14 queries documented with Primary/Supporting evidence tiers |
| governance-queries.md | governance-mapping.md (Phase 1) | consistent evidence tier terminology | VERIFIED | Uses same "Primary evidence", "Supporting evidence", "Partial coverage" terminology |
| sr11-7-model-risk/*.kql | Control 2.6 | // Supports: 2.6 (Primary) | VERIFIED | All 3 SR 11-7 queries reference Control 2.6 as Primary |
| agent-decision-audit-trail.kql | Control 1.7, 2.12 | // Supports comments | VERIFIED | Header contains Control 1.7 (Primary), Control 2.12 (Primary), Control 2.6 (Supporting) |

### Requirements Coverage

| Requirement | Status | Evidence |
|-------------|--------|----------|
| KQL-01: Agent usage analytics query | SATISFIED | agent-usage-analytics.kql with sessions, messages, completion rates |
| KQL-02: Error categorization query | SATISFIED | error-categorization-by-type.kql with connector/knowledge/orchestration |
| KQL-03: Latency distribution query | SATISFIED | latency-distribution.kql with P50/P95/P99 |
| KQL-04: Generative answers telemetry query | SATISFIED | generative-answers-telemetry.kql with topic, result, feedback |
| KQL-05: Flow failure correlation query | SATISFIED | flow-failure-correlation.kql with MicrosoftFlow correlation |
| KQL-06: Agent decision audit trail query | SATISFIED | agent-decision-audit-trail.kql with CompletenessPercent, hash_sha256, IncludePII |
| KQL-07: RAI content filtering detection query | SATISFIED | rai-content-filtering-detection.kql with XPIADetected |
| GOV-01: Governance mapping document | SATISFIED | governance-queries.md with Control-to-Query Cross-Reference table |
| GOV-02: SR 11-7 model risk monitoring patterns | SATISFIED | sr11-7-model-risk/ queries with drift threshold (20%) and pass rate threshold (95%) |
| GOV-03: SOX 302/404 control evidence documentation | SATISFIED | governance-queries.md SOX 302/404 Control Evidence Guide section |

**Requirements:** 10/10 satisfied

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| None found | - | - | - | - |

All files scanned for TODO/FIXME/placeholder patterns - none found. All queries have substantive implementations with complete header blocks.

### Human Verification Required

#### 1. Query Execution in Log Analytics

**Test:** Copy any .kql file, replace `{TimeRange:7d}` with `7d`, run in Azure Log Analytics against a workspace with Copilot Studio telemetry.

**Expected:** Query executes without syntax errors and returns expected columns.

**Why human:** Requires live Azure environment with telemetry data.

#### 2. Workbook Parameter Integration

**Test:** Create Azure Monitor Workbook with TimeRange parameter, paste agent-usage-analytics.kql, verify parameter substitution.

**Expected:** Workbook renders with time picker controlling query results.

**Why human:** Requires Azure portal interaction for workbook creation.

#### 3. SR 11-7 Drift Detection Threshold

**Test:** Run drift-detection-baseline.kql with `{DriftThreshold:10}` against production data, verify InvestigationRequired flags appropriate topics.

**Expected:** Topics with >10% change from baseline flagged for investigation.

**Why human:** Requires production telemetry data and business judgment on threshold appropriateness.

## Verification Summary

Phase 2 goal is **achieved**. All 14 KQL queries exist, are substantive (not stubs), contain proper header blocks with control references, and are documented in governance-queries.md. The queries enable:

1. **Operational visibility:** Usage analytics, error categorization, latency monitoring
2. **Regulatory compliance:** FINRA 3110 audit trails, SR 11-7 model risk monitoring, SOX control evidence
3. **Governance traceability:** Every query maps to FSI-AgentGov framework controls via inline comments and governance-queries.md cross-reference tables

**Key evidence:**
- 14 .kql files with complete header blocks (Purpose, Parameters, Output Schema, Supports, Sample Output)
- governance-queries.md at 507 lines with Control-to-Query Cross-Reference, Regulatory Cross-Reference, SR 11-7 Compliance Guide
- README.md at 242 lines with usage instructions for workbooks, Log Analytics, and Power BI
- All SR 11-7 queries include configurable thresholds (20% drift, 95% pass rate)
- All compliance queries use hash_sha256() for PII protection with IncludePII toggle option

---

*Verified: 2026-02-05T16:30:00Z*
*Verifier: Claude (gsd-verifier)*
