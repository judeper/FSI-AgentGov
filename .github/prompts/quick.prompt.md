---
name: "gsd-quick"
description: "Execute a quick task with GSD guarantees (atomic commits, state tracking) but skip optional agents"
tools: ["read", "edit", "search", "execute"]
---

<objective>
Execute a quick, well-defined task with GSD guarantees (atomic commits, state tracking) but without the full research → plan → execute → verify cycle.

This is the FSI-AgentGov adapted version. All paths use `.planning/` (not `.gsd/`).
</objective>

<context>
Input: $ARGUMENTS (task description)

@.planning/STATE.md
@.planning/config.json
</context>

<process>

<step name="understand_task">
Parse the task description. Determine:
- What files need to change
- Whether this is documentation, code, or configuration
- Whether build validation is needed
</step>

<step name="execute">
Implement the task directly:
1. Make the changes
2. Commit atomically: `git commit -m "type(scope): description"`
3. Run validation if documentation changed: `mkdocs build --strict`
</step>

<step name="update_state">
Update STATE.md with what was done. Do not create PLAN.md or SUMMARY.md for quick tasks.
</step>

</process>

<commit_rules>
- Atomic commits per logical change
- Format: `type(scope): description`
- FSI-AgentGov types: feat, fix, docs, refactor, chore
</commit_rules>
