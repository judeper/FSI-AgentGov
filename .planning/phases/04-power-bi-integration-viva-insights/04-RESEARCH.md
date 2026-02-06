# Phase 4: Power BI Integration & Viva Insights - Research

**Researched:** 2026-02-05
**Domain:** Power BI semantic modeling, TMDL, Azure Data Explorer integration, Viva Insights adoption analytics
**Confidence:** HIGH

## Summary

Phase 4 delivers executive-facing compliance dashboards through Power BI and Viva Insights adoption documentation. The Power BI track requires TMDL-based semantic model templates with dual-grain star schema (session-level + event-level facts), zone-based RLS, comprehensive DAX measures, and support for both ADX connector (Pro license) and DirectQuery (Premium) paths. The Viva Insights track documents Copilot Studio adoption metrics with clear scope limitations and reconciliation workflows with Application Insights.

Research confirms that star schema remains the industry standard for Power BI in 2026, TMDL provides production-ready version control capabilities, and Viva Insights Agent Dashboard reaches GA in March 2026 but only covers Copilot Studio agents (not Agent Builder or Agent 365 SDK). The ADX connector and DirectQuery approaches have distinct licensing and performance tradeoffs that require documented decision matrices.

**Primary recommendation:** Use TMDL folder-based semantic model for git compatibility, implement dynamic RLS with USERNAME() DAX function for zone filtering, create pre-aggregated KQL functions (not materialized views due to Log Analytics limitations) for ADX connector path, and provide prominent Viva Insights scope warnings with gap analysis matrix showing Application Insights fills coverage gaps.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Semantic Model Design:**
- Dual-grain star schema: session-level fact for dashboards + event-level fact for drill-down analysis
- Zone-only RLS (Row-Level Security) — aligned with existing Zone 1/2/3 governance model, no department filtering
- Comprehensive dimension set: DimDate, DimAgent, DimZone, DimErrorCategory, DimRegulation, DimControl, DimUser/DimRole
- Deliverable as TMDL (Tabular Model Definition Language) template files — version-controllable, importable into Power BI Desktop

**Executive Dashboard Content:**
- Landing page: Compliance posture focus — top-level compliance score, control coverage %, regulatory gaps, zone health
- Includes regulation drill-down page where executives select a regulation (FINRA 3110, SEC 17a-4, SR 11-7) and see all related evidence status and gaps — valuable for exam prep
- Page count and layout: Claude's discretion based on available KPIs from Phases 1-3
- Trend measures (WoW/MoM): Claude's discretion on which measures benefit from trends vs. point-in-time

**Connector Strategy:**
- Document both connector paths equally with decision matrix: ADX connector (Pro license) and DirectQuery (Premium license)
- Provide both .pbit template file for quick deployment AND step-by-step documentation for customization
- Pre-aggregated KQL views for ADX connector path — materialized views or functions in Log Analytics that Power BI queries for better performance
- Refresh strategy: Claude's discretion on what patterns to document based on the connector paths

**Viva Insights Scope:**
- Document current preview state with clear preview disclaimers — update when GA lands (expected March 2026)
- Detailed gap analysis matrix: table comparing metrics with Viva column, App Insights column, and coverage notes
- Prominent warning box (admonition/callout) at top of doc calling out that Viva Insights only covers Copilot Studio agents, not Agent Builder/Agent 365 SDK agents
- Documented reconciliation workflow: step-by-step process for reconciling Viva adoption numbers with App Insights telemetry

### Claude's Discretion

- Dashboard page count and layout design
- Which DAX measures get trend calculations (WoW/MoM) vs. point-in-time
- Refresh strategy documentation (Import mode scheduled refresh vs. DirectQuery/live patterns)
- KQL view design for pre-aggregation (materialized views vs. stored functions)

### Deferred Ideas (OUT OF SCOPE)

None — discussion stayed within phase scope
</user_constraints>

## Standard Stack

The established libraries/tools for Power BI semantic modeling and Azure integration:

### Core

| Library/Tool | Version | Purpose | Why Standard |
|--------------|---------|---------|--------------|
| TMDL (Tabular Model Definition Language) | GA (2025+) | Semantic model definition in text format | Microsoft-native, source control friendly, folder-based structure for collaboration |
| Power BI Desktop | June 2022+ | Report authoring and model development | Required for TMDL view, template creation, and RLS testing |
| Azure Data Explorer Connector | Native | Power BI to Log Analytics connectivity | Supports both Import and DirectQuery modes, works with Pro license |
| DAX (Data Analysis Expressions) | Current | Measure calculations and RLS rules | Industry standard for Power BI semantic models |
| KQL (Kusto Query Language) | Current | Log Analytics query layer | Native query language for Azure Monitor, Application Insights |

### Supporting

| Library/Tool | Version | Purpose | When to Use |
|--------------|---------|---------|-------------|
| Power BI Premium/PPU | F-SKU (Fabric) | DirectQuery to dataflows, enhanced refresh | When 1GB Pro limit insufficient or real-time DirectQuery needed |
| Viva Insights | Agent Dashboard GA March 2026 | Copilot Studio adoption metrics | Copilot Studio agents only (not Agent Builder/Agent 365 SDK) |
| Tabular Editor | 3.x (optional) | Advanced TMDL editing | When bulk DAX edits or advanced model operations needed |
| Performance Analyzer | Built-in to Desktop | RLS performance impact testing | Required for validating zone-based RLS overhead |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| TMDL | .pbix files | TMDL chosen for git-friendly diffs, collaboration; .pbix is binary format with merge conflicts |
| .pbit template | .pbix report | .pbit chosen for parameterization (prompts for data source); .pbix hard-codes connections |
| KQL functions | Materialized views | Functions chosen — materialized views not available in Log Analytics workspace, only ADX clusters |
| Dynamic RLS | Static RLS | Dynamic RLS chosen for scalability with zone-based governance; static would require role per zone |

**Installation:**
```bash
# Power BI Desktop (Windows only)
# Download from: https://www.microsoft.com/en-us/download/details.aspx?id=58494

# Viva Insights access (admin prerequisites)
# Requires: Insights Analyst role in Viva Insights
# Requires: Power BI Desktop June 2022 or newer
# Sign in with organizational account used for Viva Insights
```

## Architecture Patterns

### Recommended Project Structure

```
agent-observability-foundation/power-bi/
├── semantic-model/
│   ├── database.tmdl              # Database definition
│   ├── model.tmdl                 # Model-level settings (RLS, perspectives)
│   ├── relationships.tmdl         # All relationships between tables
│   ├── tables/
│   │   ├── FactAgentSessions.tmdl    # Session-grain fact (aggregated)
│   │   ├── FactAgentEvents.tmdl      # Event-grain fact (detailed drill-down)
│   │   ├── DimDate.tmdl              # Date dimension with fiscal calendar
│   │   ├── DimAgent.tmdl             # Agent metadata (name, zone, type)
│   │   ├── DimZone.tmdl              # Zone 1/2/3 hierarchy
│   │   ├── DimErrorCategory.tmdl     # Error categorization
│   │   ├── DimRegulation.tmdl        # FINRA, SEC, SR 11-7 mappings
│   │   ├── DimControl.tmdl           # Framework control catalog
│   │   ├── DimUser.tmdl              # User dimension (PII hashed)
│   │   └── DimRole.tmdl              # Role assignments
│   ├── roles/
│   │   └── ZoneBasedAccess.tmdl      # Dynamic RLS role definition
│   └── measures/
│       └── CoreMetrics.tmdl          # Shared DAX measures
├── templates/
│   └── agent-compliance-dashboard.pbit   # Parameterized template
├── kql-views/
│   ├── vw_session_fact.kql           # Pre-aggregated session data
│   ├── vw_event_fact.kql             # Event-level data for drill-down
│   ├── vw_dim_agent.kql              # Agent dimension builder
│   └── vw_dim_regulation_control.kql # Regulation-to-control mapping
├── docs/
│   ├── power-bi-integration.md       # Implementation guide
│   ├── connector-decision-matrix.md  # ADX vs DirectQuery comparison
│   ├── viva-insights-scope.md        # Viva Insights limitations and gaps
│   └── viva-insights-reconciliation.md  # Reconciliation workflow
└── README.md                         # Quick start guide
```

### Pattern 1: Dual-Grain Star Schema

**What:** Two fact tables at different granularities sharing dimension tables via conformed dimensions.

**When to use:** When dashboard users need high-level KPIs (session-level) but compliance teams need detailed audit trails (event-level).

**Example:**
```
FactAgentSessions (grain: one row per session per day)
├── SessionDate (FK to DimDate)
├── AgentId (FK to DimAgent)
├── ZoneId (FK to DimZone)
├── SessionCount (measure)
├── MessageCount (measure)
├── AvgLatencyMs (measure)
└── CompletionRate (measure)

FactAgentEvents (grain: one row per BotMessageSend/Received event)
├── EventTimestamp (FK to DimDate)
├── AgentId (FK to DimAgent)
├── SessionId (degenerate dimension)
├── EventType (BotMessageSend/Received)
├── LatencyMs (measure)
└── ErrorCode (FK to DimErrorCategory)

Shared dimensions: DimDate, DimAgent, DimZone, DimErrorCategory
```

**Rationale:** Executive dashboards query session-level fact for speed (fewer rows), compliance analysts drill to event-level fact for FINRA 3110 audit trails. Both facts share dimension tables to ensure consistent filtering.

### Pattern 2: Dynamic RLS with USERNAME()

**What:** Single role definition using DAX USERNAME() function to filter based on user identity mapped to zones.

**When to use:** Zone-based governance model where users should only see their zone's data.

**Example:**
```dax
// In ZoneBasedAccess.tmdl role definition
// Applied to DimZone table

// Safe implementation (returns no rows for unexpected users)
IF(
    LOOKUPVALUE(
        UserZoneMapping[ZoneId],
        UserZoneMapping[UserEmail],
        USERNAME()
    ) = DimZone[ZoneId],
    TRUE(),
    FALSE()
)

// UserZoneMapping table (separate security table)
// | UserEmail              | ZoneId |
// | exec@contoso.com       | Zone3  |
// | manager@contoso.com    | Zone2  |
// | analyst@contoso.com    | Zone1  |
```

**Key principles:**
- Apply RLS filter to **DimZone** (dimension), not FactAgentSessions (fact) — relationships propagate filter
- Default to FALSE() for unmatched users (safer than TRUE())
- Use security group membership via Entra ID when possible (not implemented in Phase 4, noted for future)
- Test with Performance Analyzer: View As command to measure RLS overhead

### Pattern 3: KQL Functions for Pre-Aggregation

**What:** Stored KQL functions in Log Analytics that pre-aggregate data for Power BI consumption.

**When to use:** ADX connector path (Pro license) where Import mode benefits from smaller datasets.

**Example:**
```kql
// vw_session_fact function
// Stored in Log Analytics workspace

.create-or-alter function vw_session_fact(startDate:datetime, endDate:datetime) {
    customEvents
    | where timestamp between (startDate .. endDate)
    | where name in ("BotMessageReceived", "BotMessageSend")
    | where tostring(customDimensions['DesignMode']) == "False"
    | extend AgentId = tostring(customDimensions["recipientId"])
    | extend ZoneId = tostring(customDimensions["Zone"])  // Assumes zone tagging in telemetry
    | summarize
        SessionCount = dcount(session_Id),
        MessageCount = count(),
        AvgLatencyMs = avg(todouble(customDimensions["latencyMs"])),
        CompletionRate = todouble(dcountif(session_Id, name == "BotMessageSend")) / dcount(session_Id)
        by bin(timestamp, 1d), AgentId, ZoneId
    | project
        SessionDate = timestamp,
        AgentId,
        ZoneId,
        SessionCount,
        MessageCount,
        AvgLatencyMs,
        CompletionRate
}

// Power BI M query calls function
vw_session_fact(#datetime(2026-01-01), #datetime(2026-02-01))
```

**Why functions, not materialized views:**
- Materialized views require Azure Data Explorer cluster (not available in Log Analytics workspace)
- Functions parameterizable (date range filtering at source reduces data transfer)
- Functions version-controllable in git alongside TMDL files

### Pattern 4: .pbit Template with Parameters

**What:** Power BI template file (.pbit) that prompts user for workspace URL and date range on first open.

**When to use:** Multi-tenant deployment or when users need to point template at different Log Analytics workspaces.

**Example:**
```powerquery
// In Power Query M code
let
    // Parameters defined in template
    WorkspaceURL = #"Workspace URL" meta [IsParameterQuery=true, Type="Text"],
    StartDate = #"Start Date" meta [IsParameterQuery=true, Type="Date"],
    EndDate = #"End Date" meta [IsParameterQuery=true, Type="Date"],

    Source = AzureDataExplorer.Databases(WorkspaceURL),
    Database = Source{[Name="<database-name>"]}[Data],
    Function = Database{[Name="vw_session_fact"]}[Data],
    InvokedFunction = Function(StartDate, EndDate)
in
    InvokedFunction
```

**Critical .pbit best practices:**
- Remove environment-specific calculated columns/measures before exporting
- Clear all data (no embedded data in template)
- Test parameter prompts show user-friendly descriptions
- Document parameter format requirements (e.g., "https://workspace.kusto.windows.net")

**Known .pbit pitfalls:**
- Measures/calculated columns can be lost during export (validate after save)
- Live connections produce "ghost source" refresh errors (document workaround)
- Cannot publish .pbit directly to service (must open, refresh, save as .pbix first)

### Anti-Patterns to Avoid

- **Snowflake dimensions (over-normalized):** DimRegulation → DimRegulationType → DimRegulatoryBody increases joins and confuses users. Denormalize into single DimRegulation table.
- **RLS on fact tables:** Applying `[ZoneId] = USERPRINCIPALNAME()` filter to FactAgentSessions performs poorly. Apply to DimZone and let relationships propagate.
- **Multiple active relationships without USERELATIONSHIP():** Two date relationships (SessionDate, EventDate) to DimDate causes ambiguity. Mark one inactive, use USERELATIONSHIP() in DAX measures.
- **Hard-coded credentials in .pbit:** Template must prompt for workspace URL, not embed it. Parameterize all connection strings.
- **Ignoring grain mismatches:** Joining session-grain and event-grain facts directly creates Cartesian product. Share dimensions only.

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Time intelligence (WoW, MoM, YoY) | Manual DATEADD calculations per measure | DAX time intelligence functions (DATEADD, SAMEPERIODLASTYEAR, PARALLELPERIOD) with Calendar table | Proper Calendar table with contiguous dates enables all standard functions; custom date math breaks with gaps |
| Compliance score calculation | SUM(ControlsPassed) / COUNT(Controls) | Weighted calculation with control tier mapping: `SUMX(Controls, [Weight] * [Status]) / SUM([Weight])` | Compliance frameworks weight controls differently (Pillar 1 > Pillar 4); equal weights misrepresent risk |
| Viva Insights data collection | Custom telemetry scraping | Native Copilot Studio integration to Viva Insights | Microsoft-supported data flow, pre-built schema, GA March 2026 |
| RLS user-to-zone mapping | Hard-coded DAX IF chains per user | Separate UserZoneMapping table with LOOKUPVALUE() | Scalability (100+ users), audit trail of assignments, no model redeployment for changes |
| Error categorization logic | String parsing in DAX | Pre-categorize in KQL function (error-categorization-by-type.kql exists in Phase 2) | KQL string operations more performant than DAX, reuse existing validated logic |

**Key insight:** Power BI semantic models in financial services require auditability and change control. Hand-rolling calculations creates undocumented business logic that auditors cannot verify. Use declarative patterns (Calendar tables, lookup tables, KQL functions) that surface logic in query-able structures.

## Common Pitfalls

### Pitfall 1: TMDL Changes Not Reflected in .pbix

**What goes wrong:** Developer edits TMDL files in VS Code, expects Power BI Desktop to auto-refresh, but model unchanged.

**Why it happens:** TMDL view in Power BI Desktop is not live-synced. Changes to .tmdl files on disk require explicit "Apply" action.

**How to avoid:**
1. Make TMDL edits in Power BI Desktop's TMDL view (right pane), not external editors
2. If editing externally (e.g., VS Code for bulk find-replace), close .pbix file first
3. Reopen .pbix, Power BI detects changed .tmdl files and prompts to reload

**Warning signs:**
- DAX measure changes visible in .tmdl file but not in Fields pane
- Git diff shows relationship changes but Model View unchanged

### Pitfall 2: ADX Connector Import Mode Dataset Size Explosion

**What goes wrong:** Developer imports FactAgentEvents with 10M+ rows, hits 1GB Pro license limit, deployment fails.

**Why it happens:** Event-grain fact tables grow rapidly. 1GB limit in Pro license reached with ~6 months detailed telemetry.

**How to avoid:**
1. Use KQL function to pre-aggregate to session grain for Import mode
2. Document DirectQuery mode for event-level fact (requires Premium/PPU)
3. Implement incremental refresh (Premium feature) or rolling 90-day window in KQL function

**Warning signs:**
- Power BI Desktop refresh takes >5 minutes
- .pbix file size approaching 500MB (uncompressed data ~1.5-2x compressed)
- "Dataset size exceeds limit" error on publish to service

### Pitfall 3: RLS Performance Degradation with Complex Lookups

**What goes wrong:** Zone-based RLS filter uses nested LOOKUPVALUE() across 3 tables, report visuals timeout.

**Why it happens:** RLS evaluated on every DAX query. Complex filter propagation multiplied by visual count creates query storm.

**How to avoid:**
1. Apply RLS to dimension closest to fact (DimZone, not DimAgent → DimZone)
2. Use active relationships for filter propagation (not LOOKUPVALUE when relationship exists)
3. Test with Performance Analyzer: compare query times with/without RLS using View As

**Warning signs:**
- Visuals load >3 seconds with RLS enabled, <1 second without
- Query plan shows multiple filter iterations
- DMV traces show LOOKUPVALUE scans entire table per evaluation

### Pitfall 4: Viva Insights Metrics Don't Match Application Insights

**What goes wrong:** Viva Insights shows 500 active agents, Application Insights shows 1,200 agents with sessions.

**Why it happens:** Viva Insights only tracks **Copilot Studio agents published to Production environment in default environment**. Agent Builder, Agent 365 SDK, and test/dev agents excluded.

**How to avoid:**
1. Document scope limitation prominently (admonition box in viva-insights-scope.md)
2. Create gap analysis matrix showing which agent types appear in which system
3. Provide reconciliation workflow: identify agents in App Insights but not Viva, classify by type

**Warning signs:**
- Metric discrepancies >10% between systems
- Executives question "missing" agents in Viva dashboard
- Adoption metrics lower than expected

### Pitfall 5: .pbit Template Measure Loss on Export

**What goes wrong:** Developer exports .pbit, user opens template, all DAX measures missing.

**Why it happens:** Known Power BI bug (reported 2023.06+) where measures/calculated columns occasionally not saved to .pbit file.

**How to avoid:**
1. After exporting .pbit, immediately test by opening in new Power BI instance
2. Validate all measures present in Fields pane before distributing
3. Document workaround: If measures missing, export to .pbix instead, document manual connection update steps

**Warning signs:**
- Measures visible in source .pbix but not in opened .pbit
- Sort By columns lost
- Relationships missing (rare but observed)

### Pitfall 6: Fiscal Calendar Mismatch in Time Intelligence

**What goes wrong:** DAX time intelligence functions (TOTALYTD, SAMEPERIODLASTYEAR) use calendar year, but FSI customer uses July 1 fiscal year.

**Why it happens:** Time intelligence functions default to calendar year unless fiscal year_end_date parameter specified.

**How to avoid:**
1. Create DimDate table with IsFiscalYearEnd column
2. Use fiscal parameter in DAX: `TOTALYTD([Sales], DimDate[Date], "6/30")`
3. Document fiscal year assumption in semantic model documentation

**Warning signs:**
- YTD totals reset in January instead of July
- Year-over-year comparisons off by 6 months
- Executive dashboard shows incorrect quarterly rollups

## Code Examples

Verified patterns from official sources:

### Dynamic RLS with Zone Filtering

**Source:** [Microsoft Learn - RLS Guidance](https://learn.microsoft.com/en-us/power-bi/guidance/rls-guidance)

```dax
// Applied to DimZone table in ZoneBasedAccess role

// Pattern: Safe default (no rows for unexpected users)
IF(
    LOOKUPVALUE(
        UserZoneMapping[ZoneId],
        UserZoneMapping[UserEmail],
        USERNAME()
    ) = DimZone[ZoneId],
    TRUE(),
    FALSE()
)

// UserZoneMapping table structure:
// UserEmail (text): user@contoso.com
// ZoneId (text): Zone1, Zone2, Zone3
// Maintained by governance team, loaded from Entra ID group membership (future)
```

### WoW and MoM Trend Measures

**Source:** [DataDevX - Time Intelligence DAX](https://datadevx.com/power-bi/how-to-calculate-mom-yoy-wow-and-qoq-growth-in-power-bi-using-dax/)

```dax
// Base measure
Total Sessions = SUM(FactAgentSessions[SessionCount])

// Week-over-Week change
Sessions WoW =
VAR CurrentWeekSessions = [Total Sessions]
VAR PriorWeekSessions =
    CALCULATE(
        [Total Sessions],
        DATEADD(DimDate[Date], -7, DAY)
    )
RETURN
    DIVIDE(
        CurrentWeekSessions - PriorWeekSessions,
        PriorWeekSessions
    )

// Month-over-Month change
Sessions MoM =
VAR CurrentMonthSessions = [Total Sessions]
VAR PriorMonthSessions =
    CALCULATE(
        [Total Sessions],
        DATEADD(DimDate[Date], -1, MONTH)
    )
RETURN
    DIVIDE(
        CurrentMonthSessions - PriorMonthSessions,
        PriorMonthSessions
    )

// Prerequisite: Contiguous DimDate table created via CALENDARAUTO()
```

### Compliance Score Weighted Calculation

**Source:** Industry best practice for regulatory compliance dashboards

```dax
// Compliance Score (0-100)
// Weights: Pillar 1 Security = 40%, Pillar 2 Management = 30%,
//          Pillar 3 Reporting = 20%, Pillar 4 SharePoint = 10%

Compliance Score =
VAR ControlsWithEvidence =
    CALCULATE(
        COUNTROWS(FactControlEvidence),
        FactControlEvidence[EvidenceStatus] = "Complete"
    )
VAR TotalWeightedControls =
    SUMX(
        DimControl,
        SWITCH(
            DimControl[Pillar],
            "Pillar 1", 0.40,
            "Pillar 2", 0.30,
            "Pillar 3", 0.20,
            "Pillar 4", 0.10,
            0
        )
    )
VAR WeightedCompleteControls =
    SUMX(
        FILTER(
            FactControlEvidence,
            FactControlEvidence[EvidenceStatus] = "Complete"
        ),
        VAR ControlId = FactControlEvidence[ControlId]
        VAR ControlPillar = LOOKUPVALUE(DimControl[Pillar], DimControl[ControlId], ControlId)
        RETURN
            SWITCH(
                ControlPillar,
                "Pillar 1", 0.40,
                "Pillar 2", 0.30,
                "Pillar 3", 0.20,
                "Pillar 4", 0.10,
                0
            )
    )
RETURN
    DIVIDE(WeightedCompleteControls, TotalWeightedControls) * 100
```

### KQL Function for Session-Level Fact

**Source:** [Microsoft Learn - Azure Data Explorer Best Practices](https://learn.microsoft.com/en-us/azure/data-explorer/power-bi-best-practices)

```kql
// Stored function in Log Analytics workspace
// Signature: vw_session_fact(startDate:datetime, endDate:datetime)

.create-or-alter function vw_session_fact(startDate:datetime, endDate:datetime) {
    customEvents
    | where timestamp between (startDate .. endDate)
    | where name in ("BotMessageReceived", "BotMessageSend")
    | where tostring(customDimensions['DesignMode']) == "False"
    | extend
        AgentId = tostring(customDimensions["recipientId"]),
        ZoneId = tostring(customDimensions["Zone"]),
        ErrorCode = tostring(customDimensions["errorCodeText"]),
        LatencyMs = todouble(customDimensions["latencyMs"])
    | summarize
        SessionCount = dcount(session_Id),
        MessageCount = count(),
        ErrorCount = countif(isnotempty(ErrorCode)),
        AvgLatencyMs = avg(LatencyMs),
        P95LatencyMs = percentile(LatencyMs, 95),
        CompletionRate = todouble(dcountif(session_Id, name == "BotMessageSend")) / dcount(session_Id)
        by SessionDate = bin(timestamp, 1d), AgentId, ZoneId
    | project
        SessionDate,
        AgentId,
        ZoneId,
        SessionCount,
        MessageCount,
        ErrorCount,
        AvgLatencyMs,
        P95LatencyMs,
        CompletionRate
    | order by SessionDate desc, SessionCount desc
}

// Usage in Power BI M query:
// let
//     Source = AzureDataExplorer.Contents("https://workspace.kusto.windows.net", "DatabaseName",
//         "vw_session_fact(datetime(2026-01-01), datetime(2026-02-01))", [])
// in
//     Source
```

### M Query Parameter Definition for .pbit

**Source:** [Microsoft Learn - Power BI Templates](https://learn.microsoft.com/en-us/power-bi/create-reports/desktop-templates)

```powerquery
// Parameter definitions in .pbit template

let
    // Workspace URL parameter
    WorkspaceURL = #"Workspace URL" meta
    [
        IsParameterQuery = true,
        Type = "Text",
        Description = "Log Analytics workspace URL (e.g., https://workspace.kusto.windows.net)"
    ],

    // Start Date parameter
    StartDate = #"Start Date" meta
    [
        IsParameterQuery = true,
        Type = "Date",
        Description = "Reporting period start date"
    ],

    // End Date parameter
    EndDate = #"End Date" meta
    [
        IsParameterQuery = true,
        Type = "Date",
        Description = "Reporting period end date"
    ],

    // Data source query using parameters
    Source = AzureDataExplorer.Databases(WorkspaceURL),
    Database = Source{[Name="<database>"]}[Data],
    SessionData = Database{[Name="vw_session_fact"]}[Data],
    InvokedFunction = SessionData(StartDate, EndDate)
in
    InvokedFunction
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| .pbix-only development | TMDL folder-based semantic models | GA 2025 | Git-friendly, enables CI/CD pipelines, multi-developer collaboration without merge conflicts |
| Static RLS per role | Dynamic RLS with USERNAME() | Established pattern | Scalable to 100+ users without role proliferation |
| Premium-only DirectQuery | ADX connector for Pro license | 2024+ | DirectQuery requires Premium, but ADX connector Import mode works with Pro |
| Manual Viva Insights queries | Native Copilot Studio integration | Agent Dashboard GA March 2026 | Automated data flow, pre-built schema, 50-license threshold removed (now 1+ license) |
| Calendar year only | Fiscal year parameter support | Long-standing DAX capability | Use `year_end_date` parameter in TOTALYTD, SAMEPERIODLASTYEAR functions |

**Deprecated/outdated:**
- **Power BI Premium P-SKU (per capacity):** Retired January 2026 for non-EA customers, migrating to Microsoft Fabric F-SKU. DirectQuery guidance must reference "Premium/PPU or Fabric F-SKU."
- **Viva Insights 50-license minimum:** Removed. Now requires 1+ Copilot license for dashboard access (full capabilities require 50+ for anonymization thresholds).
- **Materialized views in Log Analytics:** Not available. Only in Azure Data Explorer clusters. Use stored functions instead.

## Open Questions

Things that couldn't be fully resolved:

1. **Agent 365 SDK telemetry in Viva Insights**
   - What we know: Viva Insights Agent Dashboard only covers Copilot Studio agents published to Production environment (confirmed via Microsoft Learn documentation)
   - What's unclear: Whether Agent Builder agents or Agent 365 SDK agents will be included in future roadmap
   - Recommendation: Document as out-of-scope for Phase 4, reference Application Insights as authoritative source for all agent types

2. **Optimal refresh schedule for DirectQuery vs Import**
   - What we know: DirectQuery queries live, Import requires scheduled refresh (8/day Pro, 48/day Premium)
   - What's unclear: Compliance dashboard use case — does executive need real-time or is daily refresh sufficient?
   - Recommendation: Document both patterns with decision criteria (real-time compliance monitoring → DirectQuery, daily/weekly executive review → Import with 1x daily refresh)

3. **Zone tagging in Copilot Studio telemetry**
   - What we know: Existing KQL queries assume `customDimensions["Zone"]` field exists
   - What's unclear: Whether Phase 1 telemetry infrastructure includes zone tagging at ingestion, or if it needs to be joined from separate metadata
   - Recommendation: Review Phase 1 telemetry configuration. If not present, add zone lookup via DimAgent dimension table (AgentId → ZoneId mapping)

4. **Fiscal year end date for FSI customers**
   - What we know: DAX time intelligence supports fiscal year via `year_end_date` parameter
   - What's unclear: Whether target FSI customers use calendar year (12/31) or fiscal year (common: 6/30, 9/30 for financial services)
   - Recommendation: Parameterize fiscal year end in DimDate table creation script, document assumption clearly, provide examples for both calendar and fiscal patterns

5. **Viva Insights historical data depth**
   - What we know: Initial queries limited to last 1 month, wider periods available as data accumulates
   - What's unclear: How long until 12-month trend analysis possible (required for YoY comparisons)
   - Recommendation: Document limitation, note that Application Insights provides full historical data for trend analysis in interim

## Sources

### Primary (HIGH confidence)

- [Microsoft Learn - TMDL Overview](https://learn.microsoft.com/en-us/analysis-services/tmdl/tmdl-overview) - TMDL file structure, version control benefits
- [Microsoft Learn - Power BI Star Schema Guidance](https://learn.microsoft.com/en-us/power-bi/guidance/star-schema) - Fact/dimension design principles, performance implications
- [Microsoft Learn - RLS Guidance](https://learn.microsoft.com/en-us/power-bi/guidance/rls-guidance) - Dynamic RLS patterns, USERNAME() implementation, performance testing
- [Microsoft Learn - Azure Data Explorer Power BI Best Practices](https://learn.microsoft.com/en-us/azure/data-explorer/power-bi-best-practices) - ADX connector vs DirectQuery, Import/DirectQuery mode selection
- [Microsoft Learn - Copilot Studio Agents in Viva Insights](https://learn.microsoft.com/en-us/viva/insights/advanced/analyst/templates/copilot-studio-agents) - Metrics available, scope limitations, data quality requirements
- [Microsoft Learn - Viva Insights Analytics for Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-viva-insights) - Agent coverage (not available for generative orchestration/autonomous agents)
- [Microsoft Learn - Power BI Templates](https://learn.microsoft.com/en-us/power-bi/create-reports/desktop-templates) - .pbit parameterization, best practices

### Secondary (MEDIUM confidence)

- [endjin - Why Power BI Developers Should Care About TMDL](https://endjin.com/blog/2025/01/why-power-bi-developers-should-care-about-the-tabular-model-definition-language-tmdl) - Version control advantages, collaboration benefits
- [Power BI Consulting Blog - Time Intelligence DAX Patterns 2026](https://powerbiconsulting.com/blog/time-intelligence-dax-patterns-2026) - WoW/MoM/YoY calculation patterns
- [DataDevX - Calculate MoM, YoY, WoW in Power BI](https://datadevx.com/power-bi/how-to-calculate-mom-yoy-wow-and-qoq-growth-in-power-bi-using-dax/) - Time intelligence function examples
- [Power BI Consulting Blog - Star Schema Best Practices 2026](https://powerbiconsulting.com/blog/data-modeling-star-schema-best-practices-2026) - Dual-grain fact table patterns
- [Microsoft Message Center Archive - MC1166852](https://mc.merill.net/message/MC1166852) - Viva Insights Agent Dashboard GA timeline (March 2026)
- [Power BI Consulting Blog - Microsoft Fabric Governance 2026](https://powerbiconsulting.com/blog/microsoft-fabric-data-governance-compliance-2026) - Compliance dashboard patterns for financial services

### Tertiary (LOW confidence - marked for validation)

- [Rod Trent Substack - KQL Materialized Views](https://rodtrent.substack.com/p/kusto-query-language-kql-materialized) - Materialized views vs functions (ADX-specific, not Log Analytics)
- [Multishoring - Power BI Compliance Dashboards](https://multishoring.com/blog/power-bi-compliance-dashboard-2/) - Compliance score calculation examples (generic, not FSI-specific)
- Community forum reports of .pbit measure loss issues (various Fabric Community threads)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All tools Microsoft-native with official documentation, TMDL GA confirmed 2025
- Architecture: HIGH - Star schema, RLS, time intelligence are established Power BI patterns with extensive Microsoft Learn coverage
- Pitfalls: MEDIUM - Combination of official docs (RLS performance, .pbit limitations) and community-reported issues (.pbit measure loss bug)
- Viva Insights scope: HIGH - Microsoft Learn explicitly documents limitations (no generative orchestration, Production environment only)
- KQL functions vs materialized views: HIGH - Log Analytics lacks materialized view capability (ADX clusters only), confirmed via Azure Monitor documentation

**Research date:** 2026-02-05
**Valid until:** 60 days (TMDL/Power BI stable, Viva Insights Agent Dashboard GA March 2026 may change metrics available)
