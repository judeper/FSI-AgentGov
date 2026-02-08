---
name: "gsd:new-milestone"
description: "Start a new milestone cycle — update PROJECT.md and route to requirements"
tools: ["read", "edit", "search", "execute"]
---

<objective>
Start a new milestone by updating PROJECT.md, creating REQUIREMENTS.md, and routing to roadmap creation.

This is the FSI-AgentGov adapted version. All paths use `.planning/` (not `.gsd/`).
</objective>

<context>
Input: $ARGUMENTS (milestone name/version, e.g., "v6 — Agent Access Governance Monitor")

@.planning/PROJECT.md
@.planning/STATE.md
@.planning/MILESTONES.md
</context>

<process>

<step name="check_session_ownership">
Verify session ownership before writing to shared state files.
</step>

<step name="define_milestone">
Gather milestone information:
- Version number (follows series: v1→v9)
- Name and description
- Key goals and deliverables
- Scope boundaries
</step>

<step name="create_requirements">
Create or update `.planning/REQUIREMENTS.md` with:
- Requirement IDs (REQ-1, REQ-2, etc.)
- Descriptions and acceptance criteria
- Priority levels
- Traceability to milestone goals
</step>

<step name="update_state">
Update STATE.md with new milestone information.
Archive previous milestone to MILESTONES.md if not already done.
</step>

<step name="offer_next">
```
## Milestone Defined

**{version}: {name}** — {requirement_count} requirements

Next steps:
- `/gsd:plan-milestone-gaps` — Create phases from requirements
- `/gsd:add-phase` — Manually add phases to roadmap
```
</step>

</process>
