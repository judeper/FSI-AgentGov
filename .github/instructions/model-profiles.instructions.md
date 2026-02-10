---
applyTo: ".planning/config.json"
---

# Model Profile Settings

The `.planning/config.json` file includes a `model_profile` setting that controls agent behavior.

## Available Profiles

### `quality` (Recommended for complex phases)
- Maximum depth in research and planning
- All optional workflow steps enabled
- Thorough verification with goal-backward analysis
- Best for: New solution development, regulatory content, architecture decisions

### `balanced` (Default)
- Standard depth for research and planning
- Optional workflow steps enabled per config
- Standard verification
- Best for: Most documentation work, control updates, routine phases

### `budget`
- Minimal research, focused planning
- Skip optional workflow steps
- Basic verification
- Best for: Simple fixes, minor documentation updates, typo corrections

## Changing Profile

Update `.planning/config.json`:
```json
{
  "model_profile": "quality"
}
```

Or use the `/gsd-set-profile` command.

## Workflow Toggles

The `workflow` section controls optional GSD steps:

```json
{
  "workflow": {
    "research": true,      // Run phase research before planning
    "plan_check": true,    // Verify plan quality before execution
    "verifier": true       // Run phase verification after execution
  }
}
```

These can be overridden per-profile or toggled independently.
