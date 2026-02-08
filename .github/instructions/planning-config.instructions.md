---
applyTo: ".planning/config.json"
---

# Planning Configuration

The `.planning/config.json` file controls GSD workflow behavior.

## Configuration Schema

```json
{
  "mode": "yolo | careful | ask",
  "depth": "comprehensive | standard | minimal",
  "parallelization": true,
  "commit_docs": true,
  "model_profile": "quality | balanced | budget",
  "workflow": {
    "research": true,
    "plan_check": true,
    "verifier": true
  }
}
```

## Field Reference

| Field | Values | Description |
|-------|--------|-------------|
| `mode` | `yolo`, `careful`, `ask` | Execution autonomy level |
| `depth` | `comprehensive`, `standard`, `minimal` | Research and analysis thoroughness |
| `parallelization` | `true`/`false` | Allow parallel agent execution |
| `commit_docs` | `true`/`false` | Auto-commit documentation after plan execution |
| `model_profile` | `quality`, `balanced`, `budget` | Agent behavior profile |
| `workflow.research` | `true`/`false` | Run phase research before planning |
| `workflow.plan_check` | `true`/`false` | Verify plan quality before execution |
| `workflow.verifier` | `true`/`false` | Run phase verification after execution |

## Mode Descriptions

- **`yolo`** — Execute plans without confirmation. Fast but requires trust in plan quality.
- **`careful`** — Confirm before each major step. Slower but safer.
- **`ask`** — Ask the user before any non-trivial action. Most conservative.

## Current Configuration

This project uses `yolo` mode with `comprehensive` depth — aggressive execution backed by thorough upfront research.
