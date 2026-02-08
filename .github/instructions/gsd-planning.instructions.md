---
applyTo: ".planning/**"
---

# GSD Planning Structure

This repository uses the GSD (Get Stuff Done) planning framework. All planning files are in `.planning/` — NOT `.gsd/`.

## Directory Structure

```
.planning/
├── PROJECT.md          # Project identity, scope, key decisions
├── ROADMAP.md          # Phase breakdown with success criteria
├── STATE.md            # Current position, session continuity
├── REQUIREMENTS.md     # Requirements with traceability matrix
├── MILESTONES.md       # Historical milestone achievements
├── config.json         # Workflow toggles and model profile
├── phases/             # Phase execution artifacts
│   └── {NN}-{kebab-name}/
│       ├── {NN}-RESEARCH.md
│       ├── {NN}-{PP}-PLAN.md
│       ├── {NN}-{PP}-SUMMARY.md
│       └── {NN}-VERIFICATION.md
├── research/           # Cross-phase research documents
├── codebase/           # Codebase analysis documents
└── todos/pending/      # Deferred work items
```

## File Formats

### Plan Files (`{NN}-{PP}-PLAN.md`)

YAML frontmatter required:
```yaml
---
phase: 3
plan: 2
title: "Daily validation flow and adaptive card"
wave: 1
dependencies: ["03-01-PLAN.md"]
must_haves:
  - "Power Automate daily orchestrator"
  - "Teams adaptive card template"
---
```

Body contains:
- Goal statement
- Task breakdown with acceptance criteria
- File manifest (what will be created/modified)
- Verification steps

### Summary Files (`{NN}-{PP}-SUMMARY.md`)

Post-execution record containing:
- Dependency graph
- Tech stack used
- Key files created/modified
- Decisions made during execution
- Self-check results (pass/fail)

### Research Files (`{NN}-RESEARCH.md`)

Pre-planning research containing:
- Technical analysis
- Architecture decisions
- Risk assessment
- Recommended approach

### Verification Files (`{NN}-VERIFICATION.md`)

Phase completion verification:
- Goal-backward analysis
- Success criteria check
- Gaps identified

## Configuration (`config.json`)

```json
{
  "mode": "yolo",
  "depth": "comprehensive",
  "parallelization": true,
  "commit_docs": true,
  "model_profile": "balanced",
  "workflow": {
    "research": true,
    "plan_check": true,
    "verifier": true
  }
}
```

## Naming Conventions

- Phase directories: `{NN}-{kebab-case-name}/` (e.g., `01-powershell-tech-debt/`)
- Plan files: `{NN}-{PP}-PLAN.md` (e.g., `03-02-PLAN.md`)
- Summary files: `{NN}-{PP}-SUMMARY.md`
- Research: `{NN}-RESEARCH.md`
- Verification: `{NN}-VERIFICATION.md`
- Todos: `.planning/todos/pending/YYYY-MM-DD-{kebab-title}.md`

## Important

- **Path:** Always use `.planning/` — never `.gsd/`
- **Check session ownership** in STATE.md before writing to shared state files
- **Phase artifacts** are scoped to the executing plan and safe to write
