# Phase 7: Control Enhancements & Role Updates - Context

**Gathered:** 2026-02-06
**Status:** Ready for planning

<domain>
## Phase Boundary

Update existing framework controls and role catalog to reflect Q1 2026 Microsoft governance capabilities. Six requirements: virtual connectors in Control 1.5, DSPM AI Observability in Control 1.6, AI Feature Access Control in Control 3.8, AI Administrator role, Defender XDR Administrator role, and SharePoint Restricted Search in Control 4.6. All work is in FSI-AgentGov (documentation repository). No new controls — enhancements to existing controls only.

</domain>

<decisions>
## Implementation Decisions

### Content Depth Per Control
- Add **new subsections within existing control sections** — each enhancement gets a dedicated subsection (e.g., "## Virtual Connectors" under Control 1.5's relevant section)
- **Comprehensive detail** for all enhancements — full enumeration, configuration guidance, zone-specific notes, implementation steps (match depth of existing control content)
- **Inline regulatory mapping** per enhancement — each new subsection includes a brief note on which regulations the capability helps support
- **MkDocs admonition for GA/Preview status** — use `!!! warning 'Preview Feature'` or `!!! info 'GA Feature'` at top of each new subsection to indicate rollout status

### Role Catalog Integration
- **Full role-catalog entries** for both AI Administrator and Defender XDR Administrator — standard format: description, permissions, controls affected, zone applicability, licensing notes
- **Update all affected controls** — audit controls for role references and add AI Administrator / Defender XDR Admin where they apply (comprehensive cross-referencing)
- **Include role selection guidance** — add a "Role Selection Guidance" subsection explaining when AI Admin is preferred over Power Platform Admin (separation of duties, least privilege rationale)
- **Defender XDR Admin in security controls** — add to role catalog AND update Pillar 1 controls that reference Defender capabilities (e.g., 1.6 DSPM, Defender for Cloud Apps references)

### SharePoint Restricted Search
- **Document now with preview admonition** — write full enhancement content with `!!! warning 'Preview Feature'` admonition; update when GA lands
- **Place in Control 4.6** (Content Governance) — Restricted Search is about controlling what content surfaces in results
- **AI agent grounding focus** — frame primarily as "how Restricted Search limits what AI agents can access for grounding data," directly relevant to agent governance
- **Include 'prepare now' checklist** — pre-GA preparation steps organizations can take today (audit current search scopes, identify sensitive sites, etc.), similar to Phase 6 Agent 365 migration roadmap pattern

### Playbook Updates
- **Update all 4 playbooks** for each enhanced control — portal-walkthrough, powershell-setup, verification-testing, troubleshooting all get new sections for each enhancement
- **Preview features get playbook content with disclaimer** — write steps based on preview UI with `!!! warning 'Preview — UI may change at GA'` admonition; update at GA
- **Update playbooks for role references** — any playbook step that says "assign X role" gets updated to include AI Administrator or Defender XDR Admin where appropriate
- **Specific test cases per enhancement** — each enhancement gets 2-3 verification test cases with expected outcomes in verification-testing playbooks

### Claude's Discretion
- Exact section placement within each control's 10-section structure (which of the 10 sections each subsection lands under)
- Order of enhancements within multi-enhancement controls
- Whether to add new troubleshooting entries or extend existing ones
- Specific verification test case wording and expected outcomes

</decisions>

<specifics>
## Specific Ideas

- Follow the Phase 6 pattern for preview feature documentation — single top-level preview disclaimer plus per-section admonitions worked well for Agent 365
- SharePoint Restricted Search should emphasize the AI agent grounding angle since this is an agent governance framework — broader SharePoint search scope is secondary context
- Role selection guidance between AI Admin and Power Platform Admin should be framed through FSI lens (separation of duties for regulatory compliance)
- "Prepare now" checklist for SharePoint Restricted Search mirrors the "prepare now, migrate later" tone from Phase 6 Agent 365 migration roadmap

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 07-control-enhancements-role-updates*
*Context gathered: 2026-02-06*
