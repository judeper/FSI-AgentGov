---
phase: 04
plan: 01
subsystem: power-bi-semantic-model
tags: [power-bi, tmdl, semantic-model, star-schema, rls, dual-grain]
requires:
  - phase: 02
    plan: 01
    provides: KQL query output schemas for fact and dimension table column definitions
  - phase: 02
    plan: 02
    provides: Error categorization taxonomy for DimErrorCategory
  - phase: 02
    plan: 03
    provides: Governance mapping for DimRegulation and DimControl
  - framework: zones-and-tiers.md
    provides: Zone 1/2/3 governance model for DimZone and RLS
provides:
  - Complete TMDL semantic model with dual-grain star schema
  - FactAgentSessions (session-grain) and FactAgentEvents (event-grain) fact tables
  - 8 dimension tables including DimDate with fiscal calendar
  - 10 relationships connecting facts to shared dimensions
  - ZoneBasedAccess RLS role with dynamic USERNAME() filtering
  - Foundation for DAX measures (Plan 02) and executive dashboard (Plan 04)
affects:
  - phase: 04
    plan: 02
    why: DAX measures will reference these tables and relationships
  - phase: 04
    plan: 03
    why: KQL views will align with semantic model grain and columns
  - phase: 04
    plan: 04
    why: Executive dashboard visualizations depend on this model structure
tech-stack:
  added:
    - Power BI TMDL (Tabular Model Definition Language)
  patterns:
    - Dual-grain star schema (session-level and event-level facts)
    - Conformed dimensions shared across multiple fact tables
    - Zone-based RLS with dynamic USERNAME() filtering
    - Inactive relationships for date dimension flexibility
key-files:
  created:
    - agent-observability-foundation/power-bi/semantic-model/database.tmdl
    - agent-observability-foundation/power-bi/semantic-model/model.tmdl
    - agent-observability-foundation/power-bi/semantic-model/tables/FactAgentSessions.tmdl
    - agent-observability-foundation/power-bi/semantic-model/tables/FactAgentEvents.tmdl
    - agent-observability-foundation/power-bi/semantic-model/tables/DimDate.tmdl
    - agent-observability-foundation/power-bi/semantic-model/tables/DimAgent.tmdl
    - agent-observability-foundation/power-bi/semantic-model/tables/DimZone.tmdl
    - agent-observability-foundation/power-bi/semantic-model/tables/DimErrorCategory.tmdl
    - agent-observability-foundation/power-bi/semantic-model/tables/DimRegulation.tmdl
    - agent-observability-foundation/power-bi/semantic-model/tables/DimControl.tmdl
    - agent-observability-foundation/power-bi/semantic-model/tables/DimUser.tmdl
    - agent-observability-foundation/power-bi/semantic-model/tables/DimRole.tmdl
    - agent-observability-foundation/power-bi/semantic-model/tables/UserZoneMapping.tmdl
    - agent-observability-foundation/power-bi/semantic-model/relationships.tmdl
    - agent-observability-foundation/power-bi/semantic-model/roles/ZoneBasedAccess.tmdl
  modified: []
decisions:
  - decision: Dual-grain star schema with session-level and event-level fact tables
    rationale: Session-grain supports trend analysis and KPIs, event-grain enables drill-down investigation
    alternatives: [Single grain (event-only) would require expensive aggregations for session metrics]
    impact: Plan 02 DAX measures can efficiently calculate both session and event metrics
  - decision: EventDateKey → DateKey relationship marked inactive
    rationale: Avoid ambiguous relationship paths between FactAgentEvents and DimDate
    alternatives: [Active relationship would conflict with session date filtering]
    impact: DAX measures use USERELATIONSHIP() when filtering events by date dimension
  - decision: Zone-based RLS applied to DimZone dimension (not fact tables)
    rationale: Filter propagation from dimension to facts is more maintainable than multiple fact filters
    alternatives: [Apply RLS to both fact tables would duplicate logic and risk inconsistency]
    impact: Single RLS definition controls access across all fact tables
  - decision: DimRegulation as denormalized single table
    rationale: Anti-snowflake pattern per research guidance - simple and performant
    alternatives: [Snowflake with RegulationBody dimension would add join complexity]
    impact: Simpler model, faster queries, easier maintenance
  - decision: UserZoneMapping table for RLS USERNAME() lookup
    rationale: Dynamic zone assignment without role proliferation
    alternatives: [Static roles per zone would require 3x role definitions]
    impact: Flexible zone assignment managed via UserZoneMapping table updates
  - decision: PillarWeight in DimControl for compliance score calculation
    rationale: Pillar weighting (40%/30%/20%/10%) needed for overall compliance score DAX measure
    alternatives: [Hard-code weights in DAX would require code changes if weights change]
    impact: Plan 02 ComplianceScore measure references PillarWeight column
duration: 3 minutes
completed: 2026-02-06
---

# Phase 4 Plan 01: TMDL Semantic Model Foundation

**One-liner:** Dual-grain star schema with session/event fact tables, 8 dimensions, zone-based RLS, and 10 relationships for Power BI executive dashboard.

## What Was Built

Created the complete TMDL semantic model foundation for the Agent Compliance Dashboard in Power BI. This model provides:

1. **Database and Model definitions** - Top-level TMDL structure
2. **2 Fact tables** - Dual-grain design for session and event analysis
3. **8 Dimension tables** - Agent, Date (fiscal), Zone, Error, Regulation, Control, User, Role
4. **1 Security table** - UserZoneMapping for RLS
5. **10 Relationships** - Star schema connecting facts to conformed dimensions
6. **1 RLS role** - ZoneBasedAccess with dynamic USERNAME() filtering

### Architecture Decisions

**Dual-Grain Star Schema:**
- **FactAgentSessions** - Session-grain (one row per agent per day) for trend analysis and KPIs
- **FactAgentEvents** - Event-grain (one row per BotMessage event) for drill-down investigation

**Conformed Dimensions:**
- DimAgent, DimZone, DimDate shared across both fact tables
- Relationships support filter propagation from dimensions to facts

**Zone-Based Security:**
- RLS applied to DimZone dimension (cascades to facts via relationships)
- Dynamic USERNAME() lookup in UserZoneMapping table
- Secure default: FALSE() for users without zone assignment

## Task Commits

| Task | Description | Commit | Files Changed |
|------|-------------|--------|---------------|
| 1 | Create TMDL database, model, and all table definitions | 9a5addc | database.tmdl, model.tmdl, 11 table files |
| 2 | Create relationships and zone-based RLS role | 10130cb | relationships.tmdl, roles/ZoneBasedAccess.tmdl |

## Decisions Made

### 1. Dual-Grain Star Schema

**Decision:** Separate fact tables for session-grain and event-grain analysis.

**Rationale:**
- Session-grain (FactAgentSessions): Efficient for trend analysis, session count, completion rate
- Event-grain (FactAgentEvents): Detailed drill-down for error investigation, latency percentiles

**Alternatives considered:**
- Single event-grain fact: Would require expensive aggregations for session metrics
- Single session-grain fact: Would lose event-level detail needed for investigation

**Impact:** Plan 02 DAX measures can efficiently calculate both session KPIs and event-level diagnostics.

### 2. Inactive EventDateKey → DateKey Relationship

**Decision:** Mark FactAgentEvents[EventDateKey] → DimDate[DateKey] as `isActive: false`.

**Rationale:** Avoid ambiguous relationship paths. With both FactAgentSessions[SessionDate] → DimDate[Date] and FactAgentEvents[EventDateKey] → DimDate[DateKey] active, Power BI couldn't determine which path to use for filtering.

**Alternatives considered:**
- Delete one relationship: Would prevent date filtering on one fact table
- Use separate date dimensions: Violates conformed dimension principle

**Impact:** DAX measures use `USERELATIONSHIP(FactAgentEvents[EventDateKey], DimDate[DateKey])` when filtering events by date dimension.

### 3. Zone-Based RLS Applied to DimZone

**Decision:** Apply RLS filter to DimZone dimension, not fact tables.

**Rationale:**
- Filter propagates from DimZone → DimAgent → FactAgentSessions and DimZone → DimUser → FactAgentEvents
- Single filter definition controls access across all fact tables
- More maintainable than duplicating RLS logic on each fact table

**Alternatives considered:**
- Apply RLS to both fact tables: Duplicate logic, risk inconsistency
- Apply RLS to DimAgent only: Wouldn't filter FactAgentSessions by ZoneId column

**Impact:** Single role definition (`ZoneBasedAccess`) secures entire model.

### 4. DimRegulation Denormalized

**Decision:** Single DimRegulation table with RegulationBody and Category columns (no snowflake).

**Rationale:** Research anti-pattern guidance recommends avoiding snowflake schemas. Denormalized dimension is simpler and more performant.

**Alternatives considered:**
- Snowflake with separate RegulationBody dimension: Adds join complexity, minimal benefit

**Impact:** Simpler model, faster queries, easier maintenance.

### 5. UserZoneMapping for Dynamic RLS

**Decision:** Separate UserZoneMapping table for USERNAME() → ZoneId lookup.

**Rationale:**
- Avoids role proliferation (would need 3 static roles for Zone 1/2/3)
- Dynamic zone assignment via table updates (no Power BI service republish)
- Aligns with enterprise pattern for RLS with external user directories

**Alternatives considered:**
- Static roles per zone: Would require 3 role definitions, harder to manage
- Hard-code user emails in RLS filter: Not scalable

**Impact:** Zone assignments managed by updating UserZoneMapping table (from Entra ID sync or manual maintenance).

### 6. PillarWeight in DimControl

**Decision:** Include PillarWeight column (0.40, 0.30, 0.20, 0.10) in DimControl.

**Rationale:** Compliance score calculation requires pillar weighting. Storing weights in dimension allows weight changes without DAX code changes.

**Alternatives considered:**
- Hard-code weights in DAX measure: Brittle, requires republish to change weights

**Impact:** Plan 02 ComplianceScore measure references `DimControl[PillarWeight]`.

## Technical Implementation

### Fact Tables

**FactAgentSessions** - Session-grain (one row per agent per day):
```
SessionDate (dateTime) → FK to DimDate[Date]
AgentId (string) → FK to DimAgent[AgentId]
ZoneId (string) → FK to DimZone[ZoneId]
SessionCount (int64)
MessageCount (int64)
ErrorCount (int64)
AvgLatencyMs (double)
P95LatencyMs (double)
CompletionRate (double)
```

**FactAgentEvents** - Event-grain (one row per BotMessage event):
```
EventTimestamp (dateTime)
EventDateKey (int64) → FK to DimDate[DateKey] (INACTIVE)
AgentId (string) → FK to DimAgent[AgentId]
SessionId (string) - degenerate dimension
EventType (string) - BotMessageReceived/BotMessageSend
LatencyMs (double)
ErrorCategoryId (string) → FK to DimErrorCategory (nullable)
UserId (string) → FK to DimUser (SHA-256 hashed)
ControlId (string) → FK to DimControl (nullable)
```

### Dimension Tables

**DimDate** - Fiscal calendar with YYYYMMDD DateKey:
- Columns: DateKey (key), Date, Year, Quarter, Month, MonthName, Week, DayOfWeek, DayName, IsWeekend, FiscalYear, FiscalQuarter

**DimAgent** - Agent metadata:
- Columns: AgentId (key), AgentName, AgentType (CopilotStudio/AgentBuilder/Agent365SDK), ZoneId → DimZone, EnvironmentId, IsProduction, CreatedDate, Description

**DimZone** - Static zone hierarchy (Zone1/Zone2/Zone3):
- Columns: ZoneId (key), ZoneName, ZoneLevel (1/2/3), GovernanceTier (Low/Medium/High), Description
- Populated with static M query (3 rows)

**DimErrorCategory** - Error taxonomy from Phase 2:
- Columns: ErrorCategoryId (key), ErrorCategory (Connector/Knowledge/Orchestration/Authentication/RateLimit), Severity (Critical/High/Medium/Low), Description
- Populated with static M query (5 rows)

**DimRegulation** - Denormalized regulation catalog:
- Columns: RegulationId (key), RegulationName, RegulationBody (FINRA/SEC/Fed/OCC/CFTC), Category (Supervision/Recordkeeping/Risk/Data Protection), Description
- Populated with static M query (10 rows: FINRA 3110/4511, SEC 17a-3/17a-4, SOX 302/404, SR 11-7, GLBA 501(b), OCC 2011-12, CFTC 1.31)

**DimControl** - Framework control catalog with pillar weights:
- Columns: ControlId (key), ControlName, Pillar, PillarName, PillarWeight (0.40/0.30/0.20/0.10), Description
- Populated from external control metadata source

**DimUser** - PII-hashed user dimension:
- Columns: UserId (key, SHA-256 hash), UserRole, ZoneId → DimZone, Department

**DimRole** - Role assignments with canonical short names:
- Columns: RoleId (key), RoleName (Entra Global Admin, Power Platform Admin, etc.), RoleCategory (Admin/Analyst/Operator/Supervisor), Description
- Populated with static M query (7 rows)

**UserZoneMapping** - RLS lookup table:
- Columns: UserEmail, ZoneId
- Populated from Entra ID sync or manual maintenance

### Relationships

**10 relationships** (9 active, 1 inactive):

1. FactAgentSessions[SessionDate] → DimDate[Date] (active)
2. FactAgentSessions[AgentId] → DimAgent[AgentId] (active)
3. FactAgentSessions[ZoneId] → DimZone[ZoneId] (active)
4. FactAgentEvents[EventDateKey] → DimDate[DateKey] (INACTIVE - use USERELATIONSHIP)
5. FactAgentEvents[AgentId] → DimAgent[AgentId] (active)
6. FactAgentEvents[ErrorCategoryId] → DimErrorCategory[ErrorCategoryId] (active)
7. FactAgentEvents[UserId] → DimUser[UserId] (active)
8. FactAgentEvents[ControlId] → DimControl[ControlId] (active)
9. DimAgent[ZoneId] → DimZone[ZoneId] (active)
10. DimUser[ZoneId] → DimZone[ZoneId] (active)

### Row-Level Security

**ZoneBasedAccess role:**
```dax
tablePermission UserZoneMapping = 'UserZoneMapping'[UserEmail] = USERNAME()

tablePermission DimZone =
    VAR UserZone =
        LOOKUPVALUE(
            UserZoneMapping[ZoneId],
            UserZoneMapping[UserEmail], USERNAME()
        )
    RETURN
        IF(
            NOT ISBLANK(UserZone) && DimZone[ZoneId] = UserZone,
            TRUE(),
            FALSE()
        )
```

**Security behavior:**
- Users see only data for their assigned zone
- Users without zone assignment see no data (secure default)
- Zone assignment managed via UserZoneMapping table updates

## Alignment to Framework

### Controls Supported

This semantic model provides the foundation for observability and reporting that helps support compliance with:

**Control 3.1 - Usage Metrics** - DimAgent and FactAgentSessions tables enable session count and message count tracking.

**Control 3.2 - Error Tracking** - DimErrorCategory and FactAgentEvents support error categorization and severity analysis.

**Control 3.3 - Performance Metrics** - LatencyMs, P95LatencyMs columns support latency monitoring against thresholds.

**Control 3.4 - Audit Logging** - FactAgentEvents with EventTimestamp and UserId (hashed) aids in audit trail analysis.

**Control 3.9 - Executive Dashboards** - Semantic model is the foundation for Zone-aware executive reporting (Plan 04).

### Regulatory Mapping

The semantic model structure aids in meeting regulatory requirements:

**FINRA 3110 (Supervision):**
- DimUser, UserZoneMapping enable supervisor-to-agent assignment reporting
- FactAgentEvents with UserId supports supervisory review workflows

**SEC 17a-4 (Recordkeeping):**
- DimDate with fiscal calendar supports retention period tracking
- EventTimestamp supports chronological audit trail reconstruction

**SR 11-7 (Model Risk Management):**
- DimControl with ControlId supports model validation evidence tracking
- FactAgentEvents with ControlId links events to control testing

**SOX 302/404 (Internal Controls):**
- DimControl with PillarWeight supports control maturity scoring
- Relationships enable traceability from events to controls

## Deviations from Plan

None - plan executed exactly as written.

## Next Phase Readiness

**Phase 4, Plan 02 (DAX Measures)** is ready to proceed:
- Semantic model provides all tables and relationships needed for measure development
- Inactive EventDateKey relationship documented for USERELATIONSHIP usage
- PillarWeight column available for ComplianceScore calculation

**Blockers:** None.

**Concerns:** None.

## Files Created

All files created in `/Users/admin/dev/FSI-AgentGov-Solutions/agent-observability-foundation/power-bi/semantic-model/`:

**Database & Model:**
- `database.tmdl` - Database-level definition
- `model.tmdl` - Model-level settings (culture, data source version)

**Fact Tables:**
- `tables/FactAgentSessions.tmdl` - Session-grain fact table
- `tables/FactAgentEvents.tmdl` - Event-grain fact table

**Dimension Tables:**
- `tables/DimDate.tmdl` - Fiscal calendar dimension
- `tables/DimAgent.tmdl` - Agent metadata dimension
- `tables/DimZone.tmdl` - Zone hierarchy dimension (static 3 rows)
- `tables/DimErrorCategory.tmdl` - Error taxonomy dimension (static 5 rows)
- `tables/DimRegulation.tmdl` - Denormalized regulation catalog (static 10 rows)
- `tables/DimControl.tmdl` - Framework control catalog with pillar weights
- `tables/DimUser.tmdl` - PII-hashed user dimension
- `tables/DimRole.tmdl` - Role assignments with canonical names (static 7 rows)

**Security Tables:**
- `tables/UserZoneMapping.tmdl` - RLS lookup table for USERNAME() → ZoneId

**Relationships:**
- `relationships.tmdl` - 10 relationships connecting fact and dimension tables

**Security Roles:**
- `roles/ZoneBasedAccess.tmdl` - Dynamic RLS role with USERNAME() filtering

## Self-Check: PASSED

**Files created verification:**
```
✓ database.tmdl exists
✓ model.tmdl exists
✓ 11 table TMDL files exist (2 facts, 8 dimensions, 1 security table)
✓ relationships.tmdl exists
✓ roles/ZoneBasedAccess.tmdl exists
```

**Commits verification:**
```
✓ Commit 9a5addc exists (Task 1: database, model, tables)
✓ Commit 10130cb exists (Task 2: relationships, RLS role)
```

**Semantic correctness:**
```
✓ FactAgentSessions has SessionCount, MessageCount, AvgLatencyMs, CompletionRate
✓ FactAgentEvents has EventTimestamp, EventType, LatencyMs, ErrorCategoryId
✓ All 8 dimension tables have isKey: true columns
✓ DimDate includes FiscalYear and FiscalQuarter
✓ DimRegulation is denormalized (RegulationBody and Category in single table)
✓ DimControl includes PillarWeight column
✓ 10 relationships defined
✓ 1 relationship marked isActive: false (EventDateKey → DateKey)
✓ ZoneBasedAccess role uses USERNAME() and LOOKUPVALUE()
✓ RLS defaults to FALSE() for unmatched users
```

**Result:** All verification criteria met. TMDL semantic model is complete and ready for import into Power BI Desktop.
