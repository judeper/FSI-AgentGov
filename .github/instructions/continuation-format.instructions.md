---
applyTo: ".planning/**"
---

# Context Continuation Across Sessions

When pausing or resuming work, use these formats to preserve context.

## Pause Format (STATE.md Session Continuity)

Update STATE.md with:

```markdown
### Last Session Summary (YYYY-MM-DD)

**What happened:**
- [Bullet list of completed actions]
- [Include commit hashes for traceability]

### Context for Next Session

If resuming this project:

1. **Read these files first:**
   - `.planning/STATE.md` — Current position
   - `.planning/ROADMAP.md` — Phase structure
   - [Phase-specific files as relevant]

2. **Current state:**
   - [What's been built so far]
   - [What artifacts exist and where]

3. **Next action:**
   - [Specific next step to take]
   - [Any blockers or dependencies]
```

## Resume Checklist

When starting a new session:

1. Read `.planning/STATE.md` — understand current position
2. Read `.planning/ROADMAP.md` — understand phase structure
3. Read the current phase's latest SUMMARY.md — understand recent work
4. Check session ownership — claim if available
5. Verify build still passes: `mkdocs build --strict`
6. Continue from where the last session left off

## Context Handoff Between Tools

When handing off between Copilot and Claude Code:

1. Complete current plan or reach a checkpoint
2. Update STATE.md with comprehensive session summary
3. Commit the STATE.md update
4. Update `Active Tool` field
5. The receiving tool reads STATE.md to understand context
