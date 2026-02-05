# Phase 2: KQL Query Library & Governance Mapping - Context

**Gathered:** 2026-02-05
**Status:** Ready for planning

<domain>
## Phase Boundary

Reusable KQL queries that enable consistent metrics across all visualization layers (workbooks, Power BI, alerts) with governance compliance patterns. Includes governance documentation linking queries to the 62-control framework for FSI audit requirements (FINRA 3110, SEC 17a-4, SR 11-7). Workbooks, alerts, and Power BI integration are separate phases.

</domain>

<decisions>
## Implementation Decisions

### Query Organization
- Organize by function (usage-analytics, error-categorization, latency-distribution), not by regulation or visualization target
- Descriptive kebab-case file names (agent-usage-analytics.kql, error-categorization-by-type.kql)
- Header block per query with: Purpose, Parameters, Output schema, Related controls, Sample output
- Claude's discretion on whether to group related queries in single files or separate

### Output Format & Parameters
- Parameterized time ranges with defaults: `let TimeRange = {TimeRange:7d};`
- Standardized column names across all queries: Timestamp, AgentId, SessionId, MetricValue — predictable for all consumers
- Claude's discretion on zone filtering approach (parameter vs separate queries)
- Claude's discretion on aggregation approach (parameter vs separate granularity files)

### Governance Evidence Mapping
- Both inline comments AND separate mapping document
- Inline: `// Supports: 1.8, 3.2` in query headers
- Mapping doc: comprehensive governance-queries.md with full control cross-references
- Use three-tier evidence model (Primary/Supporting/Partial) consistent with Phase 1 governance-mapping.md
- Include sample output rows in query headers for audit evidence examples
- Detailed SR 11-7 patterns with production-ready examples for drift detection, backtesting, output monitoring

### Audit Trail Query Design
- Full decision chain fields for FINRA 3110: Timestamp, AgentId, SessionId, UserId, Prompt, Response, Sources, SupervisorId, ReviewStatus
- Graceful nulls with warnings: `coalesce(field, 'NOT_CAPTURED')` — queries run, flag incomplete records
- Include completeness percentage per record showing % of required fields present
- PII handling: hashed by default (`hash(UserId)`), raw value variant for authorized reviewers

### Claude's Discretion
- File grouping: one query vs related queries grouped per file
- Zone filtering implementation (parameter vs separate queries)
- Aggregation granularity approach
- Technical KQL patterns for SR 11-7 compliance

</decisions>

<specifics>
## Specific Ideas

- Query headers should be self-contained — someone reading just the .kql file understands purpose and usage
- Completeness % helps operations identify telemetry gaps before audits
- Three-tier evidence model (Primary/Supporting/Partial) provides nuance for compliance teams
- SR 11-7 documentation should be production-ready, not just conceptual

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 02-kql-query-library-governance-mapping*
*Context gathered: 2026-02-05*
