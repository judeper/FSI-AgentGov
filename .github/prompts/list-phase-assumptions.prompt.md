---
name: "gsd:list-phase-assumptions"
description: "Surface assumptions about a phase approach before planning"
tools: ["readFile", "listDirectory", "textSearch"]
---

<objective>
Surface implicit assumptions about how a phase will be implemented. Helps identify risks and unknowns before planning begins.

This is the FSI-AgentGov adapted version. All paths use `.planning/` (not `.gsd/`).
</objective>

<context>
Input: $ARGUMENTS (phase number)

@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/PROJECT.md
</context>

<process>

<step name="analyze_phase">
Read phase goal, success criteria, and any existing research.
Analyze the codebase for relevant patterns.
</step>

<step name="list_assumptions">
Surface assumptions in categories:

```markdown
## Phase {N} Assumptions

### Technical Assumptions
- [ ] {Assumption about technology, APIs, or tools}

### Scope Assumptions
- [ ] {Assumption about what's in/out of scope}

### Dependency Assumptions
- [ ] {Assumption about what exists or will be available}

### Risk Assumptions
- [ ] {Assumption about what could go wrong}
```
</step>

<step name="offer_next">
Ask user to confirm, correct, or add to assumptions. Then route to planning.
</step>

</process>
