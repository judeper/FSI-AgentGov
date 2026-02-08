---
applyTo: ".planning/**"
---

# Session Ownership Protocol

This repository uses multiple AI tools (Codex CLI, GitHub Copilot, Claude Code). Only one tool writes to GSD shared state files at a time.

## Before Writing to `.planning/`

1. Read `.planning/STATE.md`
2. Check the `Active Tool` field in the Session Continuity section
3. If another tool owns the session — **only read, do not write**
4. If no active tool is set — claim the session by updating STATE.md

## Shared State Files (Require Ownership)

These files require session ownership to write:
- `STATE.md` — Current position and session continuity
- `ROADMAP.md` — Phase structure and success criteria
- `config.json` — Workflow configuration

## Phase Artifacts (Safe to Write)

These files are scoped to the executing plan and do not require session ownership:
- `phases/{NN}-{name}/{NN}-{PP}-PLAN.md`
- `phases/{NN}-{name}/{NN}-{PP}-SUMMARY.md`
- `phases/{NN}-{name}/{NN}-RESEARCH.md`
- `phases/{NN}-{name}/{NN}-VERIFICATION.md`

## Claiming a Session

Add to STATE.md Session Continuity section:

```markdown
**Active Tool:** copilot
**Session Started:** 2026-02-08 14:30
**Handoff Summary:** Starting Phase 3 Plan 3 execution
```

## Handing Off

Before another tool begins:

1. Update STATE.md with:
   - What was accomplished
   - What's next
   - Change `Active Tool` to indicate handoff available
2. Commit the STATE.md update
3. The next tool claims the session by updating `Active Tool`

## Conflict Resolution

- If STATE.md shows a stale session (>24h old), it is safe to claim
- If unsure, ask the user before writing
- Phase artifacts are always safe — conflicts only apply to shared state files
