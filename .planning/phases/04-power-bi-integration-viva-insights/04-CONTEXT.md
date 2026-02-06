# Phase 4: Power BI Integration & Viva Insights - Context

**Gathered:** 2026-02-05
**Status:** Ready for planning

<domain>
## Phase Boundary

Deliver executive-facing compliance dashboards and adoption metrics that don't require KQL knowledge. Two tracks: (1) Power BI semantic model with TMDL templates and pre-built report for agent observability analytics, and (2) Viva Insights documentation covering Copilot Studio adoption visibility with cross-reference to Application Insights. All artifacts land in FSI-AgentGov-Solutions/agent-observability-foundation/power-bi/.

</domain>

<decisions>
## Implementation Decisions

### Semantic Model Design
- Dual-grain star schema: session-level fact for dashboards + event-level fact for drill-down analysis
- Zone-only RLS (Row-Level Security) — aligned with existing Zone 1/2/3 governance model, no department filtering
- Comprehensive dimension set: DimDate, DimAgent, DimZone, DimErrorCategory, DimRegulation, DimControl, DimUser/DimRole
- Deliverable as TMDL (Tabular Model Definition Language) template files — version-controllable, importable into Power BI Desktop

### Executive Dashboard Content
- Landing page: Compliance posture focus — top-level compliance score, control coverage %, regulatory gaps, zone health
- Includes regulation drill-down page where executives select a regulation (FINRA 3110, SEC 17a-4, SR 11-7) and see all related evidence status and gaps — valuable for exam prep
- Page count and layout: Claude's discretion based on available KPIs from Phases 1-3
- Trend measures (WoW/MoM): Claude's discretion on which measures benefit from trends vs. point-in-time

### Connector Strategy
- Document both connector paths equally with decision matrix: ADX connector (Pro license) and DirectQuery (Premium license)
- Provide both .pbit template file for quick deployment AND step-by-step documentation for customization
- Pre-aggregated KQL views for ADX connector path — materialized views or functions in Log Analytics that Power BI queries for better performance
- Refresh strategy: Claude's discretion on what patterns to document based on the connector paths

### Viva Insights Scope
- Document current preview state with clear preview disclaimers — update when GA lands (expected March 2026)
- Detailed gap analysis matrix: table comparing metrics with Viva column, App Insights column, and coverage notes
- Prominent warning box (admonition/callout) at top of doc calling out that Viva Insights only covers Copilot Studio agents, not Agent Builder/Agent 365 SDK agents
- Documented reconciliation workflow: step-by-step process for reconciling Viva adoption numbers with App Insights telemetry

### Claude's Discretion
- Dashboard page count and layout design
- Which DAX measures get trend calculations (WoW/MoM) vs. point-in-time
- Refresh strategy documentation (Import mode scheduled refresh vs. DirectQuery/live patterns)
- KQL view design for pre-aggregation (materialized views vs. stored functions)

</decisions>

<specifics>
## Specific Ideas

- Regulation drill-down page specifically called out as "valuable for exam prep" — frame it for regulatory examination readiness
- TMDL files chosen for version control compatibility — must work with standard git workflows
- .pbit template (not .pbix) — parameterized template that prompts for data source on first open
- Gap analysis matrix must clearly show where Viva Insights falls short so users know what Application Insights fills

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 04-power-bi-integration-viva-insights*
*Context gathered: 2026-02-05*
