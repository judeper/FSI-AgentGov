---
name: "gsd-check-todos"
description: "List pending todos and select one to work on"
tools: ["read", "search"]
---

<objective>
List all pending todos from `.planning/todos/pending/` and help the user select one to work on.

This is the FSI-AgentGov adapted version. All paths use `.planning/` (not `.gsd/`).
</objective>

<context>
@.planning/STATE.md
</context>

<process>

<step name="list_todos">
Read all files in `.planning/todos/pending/`.
Display as numbered list with title, date, and priority.
</step>

<step name="offer_actions">
For each todo, offer:
- Work on it now (route to appropriate command)
- Convert to phase (if large enough)
- Dismiss (move to `.planning/todos/done/`)
</step>

</process>
