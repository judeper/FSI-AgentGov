# Phase 1: Critical Technical Remediation - Context

**Gathered:** 2026-02-02
**Status:** Ready for planning

<domain>
## Phase Boundary

Document time-sensitive compliance deadlines and API deprecations for FSI customers. Add warnings with specific dates, explicit consequences, and migration guidance to affected controls and playbooks. Scope includes both FSI-AgentGov documentation and FSI-AgentGov-Solutions repositories.

</domain>

<decisions>
## Implementation Decisions

### Warning Prominence
- Danger (red) callouts for all time-sensitive items (February 2026 pipeline deadline AND API deprecations)
- Placement: Within relevant section of each control (not duplicated at top)
- Date included in callout header (e.g., "CRITICAL: Action Required by February 2026")
- Include explicit consequences — state what happens if reader doesn't act
- Playbook warnings: At first mention of deprecated API/method in instructions
- Cross-reference related warnings where connected impacts exist
- No centralized summary page — warnings live inline in affected docs only

### Migration Guidance Depth
- Step-by-step instructions (self-contained guidance, not just links to Microsoft Learn)
- Both portal walkthrough AND PowerShell automation for each migration
- Include verification steps to confirm migration succeeded
- Pipeline deadline: Cover both remediation paths (license procurement AND pipeline cleanup)

### Affected Scope Discovery
- Systematic search of entire codebase (grep for x-api-key, App Insights API, etc.)
- Include FSI-AgentGov-Solutions repository — both repos get consistent warnings
- Add warnings to all files where deprecated APIs are found (no selective filtering)

### Deadline Communication Tone
- Professional advisory tone ("Organizations should plan to..." not "You must...")
- Regulatory framing — connect deadlines to compliance implications where relevant
- Include "Last verified: [date]" in each warning for currency

### Claude's Discretion
- Which deprecations beyond x-api-key to search for (EWS, SharePoint Add-Ins, Key Vault based on TECH-02)
- Whether to include "who this affects" role statements in warnings
- Exact callout header wording within the established patterns

</decisions>

<specifics>
## Specific Ideas

- Warning pattern: Danger callout with date in header, consequence statement, then migration guidance
- Both repos (FSI-AgentGov docs + FSI-AgentGov-Solutions scripts) should have matching warnings
- Verification steps should be testable commands, not just "confirm it works"

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 01-critical-technical-remediation*
*Context gathered: 2026-02-02*
