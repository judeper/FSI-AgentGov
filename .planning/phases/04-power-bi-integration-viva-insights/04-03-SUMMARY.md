---
phase: 04-power-bi-integration-viva-insights
plan: 03
subsystem: power-bi-data-layer
tags: [kql, power-bi, connector, documentation]
requires: [04-01-PLAN]
provides:
  - KQL pre-aggregation functions for Power BI data consumption
  - Connector decision matrix for ADX vs DirectQuery
  - Power BI solution README and quick-start guide
affects: [04-02-PLAN]
tech-stack:
  added: []
  patterns:
    - KQL stored functions with parameterized date ranges
    - Phase 2 header block convention
    - SHA-256 PII hashing for user correlation
    - Static datatable for reference data
key-files:
  created:
    - agent-observability-foundation/power-bi/kql-views/vw_session_fact.kql
    - agent-observability-foundation/power-bi/kql-views/vw_event_fact.kql
    - agent-observability-foundation/power-bi/kql-views/vw_dim_agent.kql
    - agent-observability-foundation/power-bi/kql-views/vw_dim_regulation_control.kql
    - agent-observability-foundation/power-bi/docs/connector-decision-matrix.md
    - agent-observability-foundation/power-bi/README.md
  modified: []
decisions:
  - id: kql-function-date-params
    context: Power BI Import mode has 1GB Pro license limit
    decision: KQL functions accept parameterized date ranges (startDate, endDate)
    rationale: Allows users to control dataset size by restricting date window (90-day for <100 agents, 30-day for >100 agents)
    alternatives: [Fixed date ranges, user-defined variables in Power Query]
  - id: pii-hashing-sha256
    context: Event-level detail includes user identities
    decision: Use hash_sha256() for UserId field in vw_event_fact
    rationale: Persistent hashing (same input = same hash) enables cross-session correlation while protecting PII, consistent with Phase 2 convention
    alternatives: [Drop UserId entirely, encrypt instead of hash, use hash() which is non-deterministic]
  - id: agent-type-heuristic
    context: Telemetry lacks explicit agent type field
    decision: Infer AgentType from customDimensions flags (copilotStudioAgent, agent365Sdk)
    rationale: Best-effort classification based on available telemetry; documented as heuristic requiring validation
    alternatives: [Require explicit agent type in telemetry, use environment metadata, manual classification table]
  - id: regulation-datatable-static
    context: Regulation-to-control mapping changes infrequently
    decision: Use datatable() for static lookup in vw_dim_regulation_control
    rationale: Simple deployment, version-controlled, sufficient for current governance mapping update frequency
    alternatives: [CSV in blob storage, Azure Data Explorer table, external_table()]
  - id: equal-connector-documentation
    context: Plan locked decision to document both ADX and DirectQuery equally
    decision: Connector decision matrix provides equal depth for both paths
    rationale: Users choose based on licensing and requirements, not our preference
    alternatives: [Recommend one over the other, document only Import mode]
metrics:
  duration: 361 seconds
  completed: 2026-02-06
---

# Phase 04 Plan 03: KQL Pre-Aggregation Functions & Connector Decision Matrix Summary

**One-liner:** Created 4 KQL pre-aggregation functions with parameterized date ranges and SHA-256 PII hashing, plus comprehensive connector decision matrix documenting ADX Import and DirectQuery paths equally.

## What Was Delivered

### KQL Pre-Aggregation Functions (4 files)

**1. vw_session_fact.kql** - Session-level aggregation for Power BI Import mode
- Parameterized date range (startDate, endDate) to control dataset size
- Output schema: SessionDate, AgentId, ZoneId, SessionCount, MessageCount, ErrorCount, AvgLatencyMs, P95LatencyMs, CompletionRate
- Pro license 1GB limit guidance: 90-day window for <100 agents, 30-day for >100 agents
- Aligns with FactAgentSessions.tmdl from Plan 01

**2. vw_event_fact.kql** - Event-level detail for drill-down and audit trail
- Parameterized date range with high-volume data warning (DirectQuery recommended)
- SHA-256 PII hashing for UserId field (persistent, privacy-safe correlation)
- Output schema: EventTimestamp, EventDateKey, AgentId, SessionId, EventType, LatencyMs, ErrorCategoryId, UserId, ControlId
- Aligns with FactAgentEvents.tmdl from Plan 01

**3. vw_dim_agent.kql** - Agent dimension from telemetry metadata
- No date parameters (returns distinct agents from all time)
- Heuristic AgentType inference from customDimensions flags (CopilotStudio, Agent365SDK, AgentBuilder)
- Output schema: AgentId, AgentName, AgentType, ZoneId, EnvironmentId, IsProduction, CreatedDate, Description
- Documented as heuristic requiring validation after deployment

**4. vw_dim_regulation_control.kql** - Static regulation-to-control mapping
- datatable() with 40+ regulation-to-control mappings from governance-mapping.md
- Covers FINRA 3110/4511, SEC 17a-3/4, SOX 302/404, SR 11-7, OCC 2011-12, GLBA 501(b), CFTC 1.31
- Evidence tier classification (Primary, Supporting, Partial)
- Comment recommends CSV/blob storage for production environments with frequent updates

**Common patterns:**
- Phase 2 header block convention (Function/Purpose/Parameters/Output Schema/Supports/Sample Output)
- Deployment guidance with .create-or-alter function syntax
- Integration pattern examples for Power BI M query

### Connector Decision Matrix (15.7 KB)

Comprehensive comparison document helping administrators choose between ADX Connector (Import) and DirectQuery:

**Core sections:**
- Decision matrix table with 11 criteria (licensing, data freshness, dataset size, performance, cost)
- Mermaid flowchart for decision tree
- Quick decision guide (4 yes/no questions)
- Step-by-step setup for ADX Connector Import mode (7 steps)
- Step-by-step setup for DirectQuery (7 steps)
- .pbit template deployment instructions (8 steps with known measure loss bug warning)
- Mixed mode (Import + DirectQuery) guidance
- Known limitations and troubleshooting tables (3 categories: ADX, DirectQuery, .pbit)

**Key decisions documented:**
- Import mode: Best for daily/weekly executive review, Pro license sufficient, 1GB limit
- DirectQuery: Best for real-time monitoring, requires Premium/PPU/Fabric, no dataset limit
- Mixed mode: Premium only, combine static dimensions (Import) with live facts (DirectQuery)

**Equal treatment:** Both paths documented with same depth (setup steps, limitations, best practices)

### Power BI Solution README (13 KB)

Solution entry point with quick-start guidance and cross-references:

**Structure:**
- What's Included: 5 components (semantic-model, measures, kql-views, templates, docs)
- Quick Start: Option 1 (Template - 10-15 min) and Option 2 (Custom Build - 1-2 hours)
- Prerequisites: Infrastructure, access, licensing
- Choosing Your Connector: Quick comparison table with link to full decision matrix
- Dashboard Pages: 5 pages described (Compliance Posture, Regulation Drill-Down, Operational Health, Adoption Trends, Agent Detail)
- Documentation: 8 cross-references to integration guides and technical docs
- Architecture Overview: Mermaid diagram showing Power BI → ADX connector → Log Analytics → Application Insights
- Related: 11 links to parent solution, framework docs, Microsoft Learn

**18 total cross-references** to sibling and parent documentation

## Task Commits

| Task | Commit | Files | Description |
|------|--------|-------|-------------|
| 1 | a389902 | 4 KQL functions | vw_session_fact (session aggregation), vw_event_fact (event detail), vw_dim_agent (agent dimension), vw_dim_regulation_control (regulation mapping) |
| 2 | c393dd8 | 2 docs | connector-decision-matrix.md (ADX vs DirectQuery), README.md (solution overview) |

**Total commits:** 2
**Total files created:** 6
**Lines added:** 1,080 (374 KQL + 706 Markdown)

## Requirements Satisfied

| Requirement | Status | Evidence |
|-------------|--------|----------|
| **PBI-03 (partial)** | ✅ COMPLETE | 4 KQL pre-aggregation functions with parameterized date ranges, Phase 2 header convention, output schemas aligned to TMDL tables |
| **PBI-03 (connector docs)** | ✅ COMPLETE | Connector decision matrix documents both ADX Import and DirectQuery equally with decision criteria, setup steps, limitations |

**Progress:** PBI-03 is now 100% complete (KQL functions + connector docs).

## Decisions Made

### 1. Parameterized Date Ranges in KQL Functions

**Context:** Power BI Pro has 1GB dataset limit; Premium has 10GB. Large date ranges can exceed limits.

**Decision:** KQL functions accept startDate and endDate parameters, allowing users to control dataset size.

**Impact:**
- Users can adjust date window based on agent count (90-day for <100 agents, 30-day for >100)
- Power BI M query passes literal datetime values: `vw_session_fact(datetime(2026-01-01), datetime(2026-03-31))`
- Reduces data transfer cost and import time

**Alternative considered:** Fixed date ranges (e.g., last 90 days) — rejected because inflexible for varying deployment sizes

### 2. SHA-256 PII Hashing for UserId

**Context:** vw_event_fact includes user identities from customDimensions["from_Id"]. Privacy concern for audit trail visibility.

**Decision:** Hash UserId with hash_sha256() function.

**Rationale:**
- **Persistent:** Same user always produces same hash (enables cross-session correlation)
- **Privacy-safe:** Original identity not exposed in query results
- **Consistent:** Follows Phase 2 PII convention from compliance queries

**Impact:**
- Drill-down analysis can correlate user sessions without exposing PII
- Authorized supervisors can match hashed IDs to source data if needed
- Complies with GLBA 501(b) customer data protection

**Alternative considered:** Drop UserId entirely — rejected because breaks audit trail correlation for FINRA 3110

### 3. Heuristic AgentType Inference

**Context:** Copilot Studio telemetry lacks explicit agent type field. Need to classify agents as CopilotStudio, Agent365SDK, or AgentBuilder.

**Decision:** Infer AgentType from customDimensions flags:
- CopilotStudio: if `copilotStudioAgent` flag present
- Agent365SDK: if `agent365Sdk` flag present
- AgentBuilder: fallback (neither flag)

**Documentation:** Clearly labeled as heuristic requiring validation after deployment.

**Impact:**
- Best-effort classification based on available telemetry
- Users must validate against actual agent inventory
- May need customization based on environment-specific telemetry properties

**Alternative considered:** Require explicit agent type in telemetry — rejected because requires upstream instrumentation changes outside our control

### 4. Static Datatable for Regulation Mapping

**Context:** Regulation-to-control mapping changes infrequently (quarterly at most). Options: datatable(), CSV in blob storage, Azure Data Explorer table.

**Decision:** Use datatable() in vw_dim_regulation_control KQL function.

**Rationale:**
- **Version control:** Mapping changes tracked in git
- **Simple deployment:** No external dependencies
- **Sufficient update frequency:** Governance mapping updates are rare

**Documentation:** Comment recommends CSV/blob storage for production environments with frequent mapping changes.

**Impact:**
- Mapping updates require redeploying KQL function
- 40+ mappings fit easily in datatable (< 2KB)
- No additional storage or ingestion costs

**Alternative considered:** External CSV file — deferred until update frequency justifies complexity

### 5. Equal Connector Path Documentation

**Context:** Plan locked decision requires documenting both ADX Import and DirectQuery equally.

**Decision:** Connector decision matrix provides same depth for both paths (setup steps, limitations, troubleshooting).

**Rationale:**
- Users choose based on licensing (Pro vs Premium) and requirements (static vs real-time)
- Neither path is universally "better" — depends on context
- Avoid bias toward one approach

**Impact:**
- Decision matrix is 15.7 KB (comprehensive)
- Setup sections are parallel structure (7 steps each)
- Known limitations documented for both

**Alternative considered:** Recommend Import mode as default — rejected per plan requirement

## Deviations from Plan

None — plan executed exactly as written.

## Cross-Plan Dependencies

**Depends on:**
- **04-01-PLAN (TMDL semantic model):** KQL function output schemas align with FactAgentSessions.tmdl and FactAgentEvents.tmdl column definitions
  - Verified: vw_session_fact columns match FactAgentSessions (SessionDate, AgentId, ZoneId, SessionCount, MessageCount, ErrorCount, AvgLatencyMs, P95LatencyMs, CompletionRate)
  - Verified: vw_event_fact columns match FactAgentEvents (EventTimestamp, EventDateKey, AgentId, SessionId, EventType, LatencyMs, ErrorCategoryId, UserId, ControlId)

**Provides for:**
- **04-02-PLAN (DAX measures):** Session metrics measures will reference vw_session_fact output columns
- **04-02-PLAN (.pbit template):** Template will call KQL functions via M query data source

## Integration Points

**With Phase 2 (KQL Query Library):**
- Adopted Phase 2 header block convention for consistency
- Referenced agent-usage-analytics.kql for session volume pattern
- Used hash_sha256() PII convention from compliance queries

**With Phase 3 (Azure Monitor Workbooks):**
- KQL functions can also be called from workbooks (not just Power BI)
- Same date range parameters work with {TimeRange:30d} workbook syntax

**With governance-mapping.md:**
- Extracted 40+ regulation-to-control mappings for vw_dim_regulation_control datatable
- Covers all Phase 1-3 artifact mappings (FINRA, SEC, SOX, SR 11-7, etc.)

## Validation Results

**Phase 2 Header Convention:**
- ✅ All 4 KQL files have Function/Purpose/Parameters/Output Schema/Supports header blocks
- ✅ Deployment guidance with .create-or-alter function syntax
- ✅ Integration pattern examples

**Schema Alignment:**
- ✅ vw_session_fact output matches FactAgentSessions.tmdl (9 columns)
- ✅ vw_event_fact output matches FactAgentEvents.tmdl (9 columns)
- ✅ vw_dim_agent output matches DimAgent.tmdl (8 columns)

**PII Handling:**
- ✅ vw_event_fact uses hash_sha256() for UserId
- ✅ WARNING comment about high-volume data in vw_event_fact

**Date Parameters:**
- ✅ vw_session_fact and vw_event_fact accept (startDate, endDate)
- ✅ vw_dim_agent and vw_dim_regulation_control have no date parameters (all-time data)

**Documentation Quality:**
- ✅ Connector decision matrix has 9 sections, 11 criteria in comparison table
- ✅ Both ADX Import and DirectQuery documented equally (7 setup steps each)
- ✅ .pbit template deployment instructions included
- ✅ README has 18 cross-references to related docs
- ✅ No prohibited compliance guarantee language ("ensures", "guarantees", "will prevent")

## Known Issues and Future Work

**KQL Function Deployment:**
- Functions are defined but not deployed to Log Analytics workspace
- Plan 04-02 or manual deployment required before Power BI can connect
- Deployment command: `.create-or-alter function vw_session_fact(startDate:datetime, endDate:datetime) { ... }`

**AgentType Heuristic:**
- Inference logic may need customization based on actual telemetry properties
- Users should validate against agent inventory after deployment
- Future: Request explicit agentType field in Copilot Studio telemetry

**Regulation Mapping Updates:**
- datatable() requires function redeployment when governance mapping changes
- Consider CSV in blob storage if update frequency increases
- Monitor governance-mapping.md for quarterly updates

**Power BI Integration Guide:**
- README references `docs/power-bi-integration.md` which doesn't exist yet
- Will be created in Plan 04-02 (comprehensive deployment guide)
- Current connector-decision-matrix.md provides sufficient setup guidance

## Next Phase Readiness

**Blocker check:** None

**Ready for Plan 04-02 (DAX Measures & .pbit Template):**
- ✅ KQL functions define output schemas for DAX measures to reference
- ✅ Session metrics (SessionCount, MessageCount, AvgLatencyMs, CompletionRate) available
- ✅ Connector decision matrix provides context for template deployment instructions

**Ready for Plan 04-04 (already complete):**
- Plan 04-04 (Viva Insights) is independent of Power BI KQL functions

**Phase 4 status:**
- Plan 04-01: ✅ COMPLETE (Semantic Model)
- Plan 04-02: Pending (DAX Measures & .pbit Template)
- Plan 04-03: ✅ COMPLETE (This plan)
- Plan 04-04: ✅ COMPLETE (Viva Insights)

**Phase 4 completion:** 3/4 plans complete (75%)

## Self-Check

Verifying all claims in this summary...

**Files created:**
```bash
cd C:/dev/FSI-AgentGov-Solutions
ls agent-observability-foundation/power-bi/kql-views/vw_session_fact.kql → EXISTS
ls agent-observability-foundation/power-bi/kql-views/vw_event_fact.kql → EXISTS
ls agent-observability-foundation/power-bi/kql-views/vw_dim_agent.kql → EXISTS
ls agent-observability-foundation/power-bi/kql-views/vw_dim_regulation_control.kql → EXISTS
ls agent-observability-foundation/power-bi/docs/connector-decision-matrix.md → EXISTS
ls agent-observability-foundation/power-bi/README.md → EXISTS
```

**Commits exist:**
```bash
cd C:/dev/FSI-AgentGov-Solutions
git log --oneline | grep a389902 → FOUND
git log --oneline | grep c393dd8 → FOUND
```

## Self-Check: PASSED

All 6 files exist, both commits present in git history, requirements satisfied.

---

*Summary created: 2026-02-06*
*Plan duration: 361 seconds (6 minutes)*
*Status: Complete*
