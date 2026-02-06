# Phase 6: Agent 365 & Identity Documentation - Context

**Gathered:** 2026-02-05
**Status:** Ready for planning

<domain>
## Phase Boundary

Unified documentation covering Microsoft's Agent 365 control plane, Entra Agent ID identity architecture, and M365 Admin Center Agent Settings — framed for FSI governance practitioners. Replaces the existing `agent-identity-architecture.md` with a comprehensive document that also updates affected control files with Agent 365 forward references. All content targets the FSI-AgentGov repository (documentation-only phase).

</domain>

<decisions>
## Implementation Decisions

### Documentation structure
- **Single unified document** combining all 3 requirements (A365-01, A365-02, A365-03) — Entra Agent ID → Agent 365 control plane → M365 Admin Center settings
- **Replaces** existing `docs/framework/agent-identity-architecture.md` — fold existing content into the unified doc as single source of truth
- **File location:** Claude's discretion based on navigation structure fit (framework/ vs reference/)
- **Detailed Mermaid diagrams** included: identity flow (Entra Agent ID → sponsorship model), control plane architecture, and admin settings hierarchy — not just one overview diagram
- **Navigation:** Update mkdocs.yml to reflect the replacement

### Migration framing
- **Tone: "Prepare now, migrate later"** — actionable prep steps readers can take before GA, with current-state fallbacks
- **Side-by-side comparison tables** for current governance vs. Agent 365 governance — "Today (per-platform)" vs "Agent 365 (unified)" columns
- **Migration readiness checklist with phases** — pre-GA checklist (identity audit, sponsorship model planning, CA policy review) + post-GA migration steps
- **Single top-level disclaimer** about preview status: "Based on preview features as of [date]. Verify GA status before implementing." — no inline per-feature status badges

### Control mapping depth
- **Expanded mapping table** covering all controls that Agent 365 changes (likely 10-15 controls across identity, DLP, registry, access)
- **Current vs. Agent 365 columns** format: Control | Current Approach | Agent 365 Approach — consistent with existing `agent-365-architecture.md` pattern
- **Phase 6 also updates affected control files** (pillar-1/, pillar-2/ etc.) with Agent 365 forward-reference notes — not deferred to Phase 7

### Audience & prerequisites
- **Dual audience:** M365 administrators (tactical, admin settings) AND security architects (strategic, architecture decisions)
- **Assumes framework knowledge** — readers know the 62 controls and 3 zones. Links to framework docs for newcomers rather than explaining inline
- **Only document confirmed features** — stick to officially documented Microsoft guidance. Skip speculative areas entirely to minimize outdated content risk
- **Link to Microsoft Learn sources** as references — readers can verify and track updates. Consistent with existing framework docs
- **Add new Learn URLs to monitoring list** — any Microsoft Learn URLs referenced in this doc must be added to `scripts/learn_monitor.py` tracking (currently 209 URLs). This keeps the Learn Monitor covering Agent 365 documentation changes

### Claude's Discretion
- Exact file placement within docs/ tree (framework/ or reference/)
- Document section ordering and heading hierarchy
- Which specific controls are affected (determined during research)
- Level of detail in Mermaid diagrams
- Exact wording of preview disclaimer banner

</decisions>

<specifics>
## Specific Ideas

- Replace agent-identity-architecture.md rather than creating alongside it — single source of truth
- Side-by-side comparison tables follow the pattern already established in the existing agent-365-architecture.md
- Control file updates (forward references to Agent 365) should be lightweight notes, not full rewrites — Phase 7 handles deeper control enhancements
- Migration readiness checklist should feel actionable: "Do this now" vs. "Do this at GA"
- Learn Monitor integration ensures the team gets notified when Microsoft updates Agent 365 documentation

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 06-agent-365-identity-documentation*
*Context gathered: 2026-02-05*
