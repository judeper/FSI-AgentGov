---
name: "gsd-progress"
description: "Check project progress, show context, and route to next action"
tools: ["read", "search"]
---

<objective>
Display current project progress with phase status, then route to the most appropriate next action (execute or plan).

This is the FSI-AgentGov adapted version. All paths use `.planning/` (not `.gsd/`).
</objective>

<context>
@.planning/STATE.md
@.planning/ROADMAP.md
@.planning/config.json
</context>

<process>

<step name="read_state">
Read STATE.md for current position, recent activity, and pending items.
Read ROADMAP.md for phase structure and completion status.
</step>

<step name="display_progress">
Show progress overview:

```
## Project Progress

**Milestone:** {version} — {name}
**Phase:** {current} of {total}
**Status:** {status}

### Phase Status
| Phase | Name | Status | Plans |
|-------|------|--------|-------|
| 1 | {name} | Complete | {X}/{Y} |
| 2 | {name} | In Progress | {X}/{Y} |
| 3 | {name} | Planned | 0/0 |

### Recent Activity
{from STATE.md session summary}

### Pending Items
{from STATE.md pending todos}
```
</step>

<step name="route_next">
Based on current state, suggest next action:

- If current phase has unexecuted plans: `/gsd-execute-phase {X}`
- If current phase needs planning: `/gsd-plan-phase {X}`
- If current phase needs research: `/gsd-research-phase {X}`
- If milestone complete: `/gsd-complete-milestone`
- If no roadmap exists: `/gsd-new-milestone`
</step>

</process>
