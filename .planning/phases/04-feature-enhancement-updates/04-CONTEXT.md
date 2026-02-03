# Phase 4: Feature Enhancement Updates - Context

**Gathered:** 2026-02-03
**Status:** Ready for planning

<domain>
## Phase Boundary

Update existing controls with GA and preview governance features released in 2025-2026. Five requirements: virtual connectors DLP (Control 1.5), DSPM/AI observability (Control 1.6), AI Feature Access Control (Control 3.8), Defender for Power Platform verification and expansion (FEAT-06), and role catalog updates for AI Administrator and Defender XDR Administrator (FEAT-07).

This phase enhances existing documentation — no new controls or framework documents are created.

</domain>

<decisions>
## Implementation Decisions

### Preview vs GA treatment
- Preview features documented inline where they logically fit, wrapped in `!!! warning "Preview — Requires Frontier Program"` admonition (consistent with Phase 3 pattern)
- Preview features receive full implementation detail — portal walkthroughs, PowerShell, verification — same depth as GA content
- When a preview feature reaches GA, simply remove the admonition — no "New" badge or transition marker
- Same preview treatment applies to all feature types including security (Defender) features — no special caution level for security previews

### Feature depth & detail level
- Virtual connectors table (Control 1.5) integrated into existing DLP section as natural extension, not a separate subsection
- DSPM coverage (Control 1.6) gets full comprehensive section: risk assessment schedules, observability metrics, dashboard guidance, remediation workflows
- AI Feature Access Control (Control 3.8) enhances existing control scope — new capability added within current control structure, same sections with richer content
- Standardized table format across all feature updates: consistent columns (Feature | Status | Description | Configuration) for cross-control comparison

### Defender capabilities scope
- Verify existing documentation accuracy AND expand with new Defender for Power Platform capabilities discovered during research
- Coordinated cross-control updates — ensure consistent terminology, cross-references, and no contradictions across all affected controls (1.6, 1.11, 3.x)
- Focus on Defender for Power Platform specifically — not broader Defender XDR capabilities
- No separate Defender mapping table — capabilities documented inline within each control
- New Defender content merged seamlessly into existing Defender sections — no visible seams between old and new content
- Both control documentation and playbooks updated with Defender configuration steps

### Role catalog updates
- AI Administrator and Defender XDR Administrator added as standalone entries with permission matrix comparison table showing how they relate to existing roles
- Controls referencing related roles updated to include new role references where applicable
- Permission matrix table format: key permissions per role with checkmarks showing what each role can/cannot do
- FSI-specific least-privilege role assignment guidance included (e.g., "For FINRA-regulated firms, prefer AI Administrator over Global Admin for agent governance")

### Claude's Discretion
- Exact placement of feature tables within each control's existing structure
- Which specific controls need Defender cross-reference updates beyond the obvious (1.6, 1.11)
- Which controls warrant AI Administrator role reference additions
- Standardized table column specifics beyond the Feature | Status | Description | Configuration baseline

</decisions>

<specifics>
## Specific Ideas

- Phase 3 established the `!!! warning "Preview — Requires Frontier Program"` pattern — this phase continues that pattern for consistency
- Phase 2 already verified all 62 controls, so existing content accuracy is the baseline — Phase 4 builds on that foundation
- Agent 365 architecture document from Phase 3 provides strategic context for how these features fit into the unified governance direction
- Permission matrix table for roles should help FSI compliance teams make role assignment decisions without guessing

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 04-feature-enhancement-updates*
*Context gathered: 2026-02-03*
