---
name: "gsd-settings"
description: "Configure GSD workflow toggles and model profile"
tools: ["read", "edit"]
---

<objective>
View and modify GSD workflow settings in `.planning/config.json`.

This is the FSI-AgentGov adapted version. All paths use `.planning/` (not `.gsd/`).
</objective>

<context>
Input: $ARGUMENTS (optional: setting=value pairs)

@.planning/config.json
</context>

<process>

<step name="display_settings">
Read and display current config.json:

```
## GSD Settings

| Setting | Value | Description |
|---------|-------|-------------|
| mode | {value} | Execution autonomy (yolo/careful/ask) |
| depth | {value} | Research thoroughness |
| parallelization | {value} | Allow parallel agents |
| commit_docs | {value} | Auto-commit planning docs |
| model_profile | {value} | Agent model selection |
| workflow.research | {value} | Run phase research |
| workflow.plan_check | {value} | Verify plan quality |
| workflow.verifier | {value} | Run phase verification |
```
</step>

<step name="modify_settings">
If arguments provided, update the specified settings.
Validate values before writing.
</step>

</process>
