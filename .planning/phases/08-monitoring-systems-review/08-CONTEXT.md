# Phase 8: Monitoring Systems Review - Context

**Gathered:** 2026-02-04
**Status:** Ready for planning

<domain>
## Phase Boundary

Review and improve the monitoring systems (Learn Monitor + Regulatory Monitor) so detected changes are clear, actionable, and maintainable. Covers simplification, change visibility, maintenance model, and regulatory monitoring approach. Building new framework controls or solutions is out of scope.

</domain>

<decisions>
## Implementation Decisions

### Simplification scope
- Unified monitoring approach — combine Learn documentation and regulatory monitoring into one coherent strategy (not two separate systems)
- Open to replacing the current Python-based approach with alternatives if simpler and more effective
- Must keep some automation — removing all monitors and going fully manual is not acceptable
- If a monitor isn't providing value, simplify or replace it, but don't eliminate automated monitoring entirely

### Change visibility format
- Keep 4-tier classification: CRITICAL / HIGH / MEDIUM / NOISE
- Change reports should include both: summary for quick scan + expandable diff for details
- Map detected changes back to specific framework controls (e.g., "learn.microsoft.com/purview/dlp-policies changed → affects Controls 1.3, 1.5")
- AI-assisted review should be active — not aspirational. The `/review-learn-changes` workflow should work end-to-end

### Maintenance model
- Moderate effort target: ~30 min/week regular review cadence
- Sophistication in tooling is acceptable if results justify it (not restricted to standard library)
- Configurable cadence per source type (e.g., daily for Learn, weekly for regulatory)
- Auto-draft PRs: when monitoring detects a change requiring a framework update, AI generates a proposed documentation update as a PR for human review

### Regulatory monitoring approach
- Regulatory monitor may not exist as code yet — Claude should investigate the codebase to determine current state
- Monitor official sources directly: FINRA.org, SEC.gov, Federal Register, state legislature sites
- All regulatory sources relevant (FINRA notices, SEC/CFTC rules, state AI legislation), prioritized by impact to FSI AI agent governance specifically
- Broad FSI capture: don't pre-filter to AI-only keywords; capture all FSI regulatory changes and let the reviewer triage relevance

### Claude's Discretion
- Notification delivery mechanism (PR-based, markdown report, or other)
- Specific Python libraries or tooling choices
- Architecture of the unified monitoring system
- How to implement control-to-URL mapping for change reports
- Whether to keep, rewrite, or replace the existing learn_monitor.py
- Specific cadence defaults per source type

</decisions>

<specifics>
## Specific Ideas

- The existing Learn Monitor AI enhancement design (`docs/reference/learn-monitor-ai-enhancement.md`) should be reviewed and either implemented or revised — it's meant to be active, not a design doc only
- Auto-drafted PRs should follow the same quality standards as manual updates (regulatory language compliance, consistent formatting)
- Regulatory monitoring should focus on changes relevant to the framework's supported AI agents (Copilot Studio, Agent Builder) within FSI, not all AI regulation broadly

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 08-monitoring-systems-review*
*Context gathered: 2026-02-04*
