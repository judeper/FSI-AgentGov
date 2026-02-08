---
name: "gsd:resume-work"
description: "Resume work from previous session with full context restoration"
tools: ["readFile", "listDirectory", "textSearch", "runInTerminal"]
---

<objective>
Resume work from a previous session by reading STATE.md context, verifying build state, and routing to the appropriate next action.

This is the FSI-AgentGov adapted version. All paths use `.planning/` (not `.gsd/`).
</objective>

<context>
@.planning/STATE.md
@.planning/ROADMAP.md
@.planning/config.json
</context>

<process>

<step name="restore_context">
1. Read STATE.md — current position, last session summary, context for next session
2. Read ROADMAP.md — phase structure
3. Read any files mentioned in "Read these files first" section
4. Verify build: `mkdocs build --strict`
</step>

<step name="claim_session">
Update STATE.md with session ownership:
```markdown
**Active Tool:** {current tool}
**Session Started:** YYYY-MM-DD HH:MM
```
</step>

<step name="display_context">
```
## Resuming Work

**Milestone:** {version} — {name}
**Phase:** {current phase}
**Last Activity:** {from STATE.md}

### What Was Done
{from last session summary}

### Next Action
{from context for next session}
```
</step>

<step name="route">
Route to appropriate command based on next action.
</step>

</process>
