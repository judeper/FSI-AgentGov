---
name: "gsd:discuss-phase"
description: "Gather phase context through adaptive questioning before planning"
tools: ["readFile", "listDirectory", "textSearch"]
---

<objective>
Discuss a phase with the user to gather context, clarify scope, and surface assumptions before creating execution plans.

This is the FSI-AgentGov adapted version. All paths use `.planning/` (not `.gsd/`).
</objective>

<execution_context>
../instructions/questioning.instructions.md
</execution_context>

<context>
Input: $ARGUMENTS (phase number)

@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/PROJECT.md
</context>

<process>

<step name="understand_phase">
Read phase goal and success criteria from ROADMAP.md.
Read project context from PROJECT.md.
</step>

<step name="adaptive_questioning">
1. Open with understanding: "Based on the roadmap, Phase N focuses on [X]..."
2. Identify gaps in understanding
3. Offer concrete approach options
4. Confirm scope boundaries
</step>

<step name="capture_context">
Write discussion outcomes to `.planning/phases/{NN}-{name}/{NN}-CONTEXT.md` if significant context was gathered.
</step>

<step name="offer_next">
```
## Phase {N} Context Gathered

`/gsd:plan-phase {N}` — Create execution plans
`/gsd:research-phase {N}` — Research before planning
```
</step>

</process>
