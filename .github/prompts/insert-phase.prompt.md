---
name: "gsd:insert-phase"
description: "Insert urgent work as decimal phase (e.g., 2.1) between existing phases"
tools: ["read", "edit", "search"]
---

<objective>
Insert an urgent phase between existing phases using decimal numbering (e.g., 2.1 between Phase 2 and Phase 3) without renumbering existing phases.

This is the FSI-AgentGov adapted version. All paths use `.planning/` (not `.gsd/`).
</objective>

<context>
Input: $ARGUMENTS (insertion point and phase description)

@.planning/ROADMAP.md
@.planning/STATE.md
</context>

<process>

<step name="check_session_ownership">
Verify session ownership before modifying ROADMAP.md.
</step>

<step name="determine_position">
Parse insertion point (e.g., "after 2" → creates Phase 2.1).
Verify both adjacent phases exist.
</step>

<step name="create_phase">
1. Add to ROADMAP.md with decimal number
2. Create directory: `.planning/phases/{NN.N}-{kebab-name}/`
3. Update STATE.md to reflect the insertion
</step>

<step name="offer_next">
```
## Phase {N.N} Inserted

**Phase {N.N}: {Name}** inserted between Phase {N} and Phase {N+1}.

`/gsd:plan-phase {N.N}` — Create execution plans
```
</step>

</process>
