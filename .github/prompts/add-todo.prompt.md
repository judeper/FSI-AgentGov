---
name: "gsd:add-todo"
description: "Capture idea or task as todo from current conversation context"
tools: ["read", "edit"]
---

<objective>
Capture an idea, task, or follow-up item as a todo in `.planning/todos/pending/`.

This is the FSI-AgentGov adapted version. All paths use `.planning/` (not `.gsd/`).
</objective>

<context>
Input: $ARGUMENTS (todo description)

@.planning/STATE.md
</context>

<process>

<step name="create_todo">
Create todo file: `.planning/todos/pending/YYYY-MM-DD-{kebab-title}.md`

Format:
```markdown
# Todo: {Title}

**Created:** YYYY-MM-DD
**Source:** {conversation context or user request}
**Priority:** {low/medium/high}

## Description
{Detailed description of what needs to be done}

## Context
{Why this todo was captured, what prompted it}

## Acceptance Criteria
- [ ] {Criterion 1}
- [ ] {Criterion 2}
```
</step>

<step name="update_state">
Update STATE.md Pending Todos section with the new todo.
</step>

<step name="confirm">
Report todo created and current todo count.
</step>

</process>
