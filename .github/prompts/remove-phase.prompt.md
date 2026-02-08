---
name: "gsd:remove-phase"
description: "Remove a future phase from roadmap and renumber subsequent phases"
tools: ["read", "edit", "search", "execute"]
---

<objective>
Remove an unstarted phase from the roadmap and renumber subsequent phases to close the gap.

This is the FSI-AgentGov adapted version. All paths use `.planning/` (not `.gsd/`).
</objective>

<context>
Input: $ARGUMENTS (phase number to remove)

@.planning/ROADMAP.md
@.planning/STATE.md
</context>

<process>

<step name="check_session_ownership">
Verify session ownership before modifying ROADMAP.md.
</step>

<step name="validate">
- Phase must exist in ROADMAP.md
- Phase must NOT be completed or in progress
- Warn if other phases depend on it
</step>

<step name="remove">
1. Remove phase from ROADMAP.md
2. Remove phase directory if it exists (only if empty or has no executed plans)
3. Renumber subsequent phases
4. Update STATE.md
</step>

<step name="confirm">
Report what was removed and new phase numbering.
</step>

</process>
