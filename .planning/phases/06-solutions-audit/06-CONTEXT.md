# Phase 6: Solutions Audit - Context

**Gathered:** 2026-02-03
**Status:** Ready for planning

<domain>
## Phase Boundary

Audit all 13 deployable solutions in the FSI-AgentGov-Solutions companion repository for completeness, documentation accuracy, technical correctness, and alignment with the 62-control framework. Resolve 5 known technical debt items (TECH-03 through TECH-07). Classify each solution's maturity status and update framework documentation to reflect current solution landscape. Solutions are enterprise automation for implementing, validating, and monitoring framework controls at scale — not every control has or needs a solution.

</domain>

<decisions>
## Implementation Decisions

### Audit Methodology
- Full review of both documentation AND scripts at equal depth for all 13 solutions
- Same audit depth for all solutions regardless of maturity (no preferential treatment for older vs newer)
- Update scripts that reference deprecated APIs (e.g., x-api-key auth in deny-event-correlation) — rewrite to use current auth methods (Entra ID), not just document the deprecation
- Verify all regulatory alignment claims in each solution against framework regulatory mappings — cross-check every FINRA/SEC/SOX/GLBA/OCC reference

### Status Classification
- Status labels: **Planned** (documentation exists, not functional — may be deleted before implementation), **Work In Progress** (partially functional), **Validated** (functional and reviewed), **Completed** (production-ready, fully tested)
- Treat solutions as documentation artifacts, not code — status reflects documentation/implementation maturity
- Display status in two locations: README badge at top of each solution's README.md AND status column in framework's solutions-index.md
- Full documentation review for all solutions including Planned ones — ensure docs are accurate for when implementation begins
- Claude proposes status for each solution based on evidence examination, user confirms/overrides before finalizing

### Technical Debt Resolution
- Fix TECH issues in BOTH repositories — solution docs in FSI-AgentGov-Solutions AND framework controls in FSI-AgentGov where inaccuracy exists
- TECH-04 (Service Principal security group bypass): Use !!! warning admonition in affected controls and solution docs
- Verify TECH issues via documentation review and API reference checking only — no live testing against Microsoft services
- If a TECH issue has been resolved by Microsoft, remove the warning entirely — no historical clutter

### Framework Alignment Depth
- Expand solutions-integration.md to cover all 13 solutions at equal depth (matching the existing 4 production solutions)
- Add solution references to control documents where a solution maps to a control (e.g., "See [Solution Name] for automated implementation")
- Not all controls will have solutions — solutions are enterprise automation, not 1:1 control coverage
- Audit should evaluate whether each Planned solution is needed or should be cut — Claude produces keep/cut recommendation with rationale where appropriate

### Claude's Discretion
- Specific audit checklist items and ordering
- How to structure audit findings reports (per-solution vs consolidated)
- Which TECH issues affect which specific files
- Whether to batch solutions by pillar or audit sequentially
- Status label determination methodology (what evidence constitutes each status level)
- Format of solution references added to control documents

</decisions>

<specifics>
## Specific Ideas

- Solutions are automation for enterprise-scale control management — think of them as tools for implementing, validating, and monitoring controls in bulk
- Some Planned solutions may get deleted before implementation starts — no dates committed for Planned solutions
- The 4 older solutions (ELM, MCM, PGC, DEC) have deeper documentation and more iterative versions; 9 newer solutions (Feb 2026) may be in planning stages only despite having folders and files
- Compliance Dashboard is explicitly v1.0.0-beta (Power BI template requires manual creation)
- Deny Event Correlation has x-api-key auth deprecated with March 31, 2026 deadline — scripts need Entra ID migration

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 06-solutions-audit*
*Context gathered: 2026-02-03*
