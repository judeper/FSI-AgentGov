---
name: "gsd-research-phase"
description: "Research how to implement a phase (standalone — usually use /gsd-plan-phase instead)"
tools: ["read", "edit", "search", "execute", "agent", "web"]
---

<objective>
Research how to implement a specific phase. Produces RESEARCH.md consumed by the planner. This is a standalone command; `/gsd-plan-phase` runs research automatically when `workflow.research` is true.

This is the FSI-AgentGov adapted version. All paths use `.planning/` (not `.gsd/`).
</objective>

<context>
Input: $ARGUMENTS (phase number)

@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/PROJECT.md
</context>

<process>

<step name="spawn_researcher">
```
Task(
  prompt="Research phase {phase_number} implementation for FSI-AgentGov...",
  subagent_type="gsd-phase-researcher",
  description="Research Phase {phase}"
)
```
</step>

<step name="review_output">
Read `.planning/phases/{NN}-{name}/{NN}-RESEARCH.md` and present key findings to user.
</step>

<step name="offer_next">
```
## Research Complete

**Phase {N}: {Name}** — Confidence: {level}

`/gsd-plan-phase {N}` — Create execution plans using this research
```
</step>

</process>
