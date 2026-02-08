---
name: "gsd:set-profile"
description: "Switch model profile for GSD agents (quality/balanced/budget)"
tools: ["read", "edit"]
---

<objective>
Switch the model profile used by GSD agents. Profiles control the depth and quality of research, planning, and execution.

This is the FSI-AgentGov adapted version. All paths use `.planning/` (not `.gsd/`).
</objective>

<context>
Input: $ARGUMENTS (profile name: quality, balanced, or budget)

@.planning/config.json
</context>

<process>

<step name="update_profile">
Update `model_profile` in `.planning/config.json`.

Available profiles:
- **quality** — Maximum depth, all workflow steps, thorough verification
- **balanced** — Standard depth, configurable workflow steps (default)
- **budget** — Minimal research, focused planning, basic verification
</step>

<step name="confirm">
```
## Profile Updated

**Model Profile:** {profile}

| Setting | Value |
|---------|-------|
| Research depth | {high/standard/minimal} |
| Plan verification | {enabled/disabled} |
| Phase verification | {enabled/disabled} |
```
</step>

</process>
