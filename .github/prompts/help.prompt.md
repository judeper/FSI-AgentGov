---
name: "gsd-help"
description: "Show available GSD commands and usage guide"
tools: ["read"]
---

<objective>
Display all available GSD commands with descriptions and usage guidance.
</objective>

<reference>
## GSD Commands (FSI-AgentGov)

### Core Workflow
| Command | Description |
|---------|-------------|
| `/gsd-progress` | Check project progress and route to next action |
| `/gsd-plan-phase {N}` | Create execution plans for a phase |
| `/gsd-execute-phase {N}` | Execute all plans in a phase |
| `/gsd-verify-work {N}` | Validate built features through conversational UAT |
| `/gsd-quick` | Execute a quick task with GSD guarantees |

### Project Setup
| Command | Description |
|---------|-------------|
| `/gsd-new-project` | Initialize a new project with research |
| `/gsd-new-milestone` | Start a new milestone cycle |
| `/gsd-plan-milestone-gaps` | Create phases to close gaps identified by audit |

### Phase Management
| Command | Description |
|---------|-------------|
| `/gsd-add-phase` | Add phase to end of current milestone |
| `/gsd-insert-phase` | Insert urgent work as decimal phase (e.g., 2.1) |
| `/gsd-remove-phase` | Remove a future phase and renumber |
| `/gsd-discuss-phase {N}` | Gather phase context before planning |
| `/gsd-research-phase {N}` | Research how to implement a phase |
| `/gsd-list-phase-assumptions {N}` | Surface assumptions about a phase |

### Research & Analysis
| Command | Description |
|---------|-------------|
| `/gsd-map-codebase` | Analyze codebase with parallel mappers |
| `/gsd-debug` | Systematic debugging with persistent state |

### Session Management
| Command | Description |
|---------|-------------|
| `/gsd-pause-work` | Create context handoff when pausing |
| `/gsd-resume-work` | Resume work from previous session |

### Maintenance
| Command | Description |
|---------|-------------|
| `/gsd-audit-milestone` | Audit milestone completion before archiving |
| `/gsd-complete-milestone` | Archive completed milestone |
| `/gsd-check-todos` | List pending todos and select one |
| `/gsd-add-todo` | Capture idea or task as todo |
| `/gsd-set-profile` | Switch model profile (quality/balanced/budget) |
| `/gsd-settings` | Configure workflow toggles |
| `/gsd-update` | Update GSD to latest version |

### Typical Workflow
```
/gsd-progress              → See where you are
/gsd-plan-phase 3          → Create plans for next phase
/gsd-execute-phase 3       → Execute the plans
/gsd-verify-work 3         → Validate the results
/gsd-progress              → Route to next action
```

### FSI-AgentGov Specific
- All GSD state lives in `.planning/` (not `.gsd/`)
- Build validation: `mkdocs build --strict` is always required
- Language rules: Never use "ensures compliance" or "guarantees"
- Session ownership: Check STATE.md before writing to shared state
</reference>
