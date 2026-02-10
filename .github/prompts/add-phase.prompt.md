---
name: "gsd-add-phase"
description: "Add phase to end of current milestone in roadmap"
tools: ["read", "edit", "search"]
---

<objective>
Add a new phase to the end of the current milestone in ROADMAP.md.

This is the FSI-AgentGov adapted version. All paths use `.planning/` (not `.gsd/`).
</objective>

<context>
Input: $ARGUMENTS (phase name and description)

@.planning/ROADMAP.md
@.planning/STATE.md
</context>

<process>

<step name="check_session_ownership">
Verify session ownership before writing to ROADMAP.md.
</step>

<step name="determine_phase_number">
Read ROADMAP.md to find the last phase number. New phase = last + 1.
</step>

<step name="gather_details">
If not provided in arguments, ask for:
- Phase name (kebab-case for directory)
- Phase goal (clear, measurable)
- Success criteria (verifiable conditions)
- Estimated number of plans
</step>

<step name="add_to_roadmap">
Append new phase to ROADMAP.md Phase Details section.
Create phase directory: `.planning/phases/{NN}-{kebab-name}/`
</step>

<step name="offer_next">
```
## Phase Added

**Phase {N}: {Name}** added to roadmap.

`/gsd-plan-phase {N}` — Create execution plans
`/gsd-discuss-phase {N}` — Gather context before planning
```
</step>

</process>
