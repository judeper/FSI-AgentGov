---
name: "gsd:pause-work"
description: "Create context handoff when pausing work mid-phase"
tools: ["readFile", "editFiles", "runInTerminal"]
---

<objective>
Create a comprehensive context handoff in STATE.md when pausing work mid-phase, so the next session (same or different tool) can resume seamlessly.

This is the FSI-AgentGov adapted version. All paths use `.planning/` (not `.gsd/`).
</objective>

<context>
@.planning/STATE.md
@.planning/ROADMAP.md
</context>

<process>

<step name="capture_state">
Gather current state:
- What was accomplished this session
- What files were created/modified
- What decisions were made
- What's next
- Any blockers or context that would be lost
</step>

<step name="update_state_md">
Update STATE.md Session Continuity section with:

```markdown
### Last Session Summary (YYYY-MM-DD)

**What happened:**
- [Completed actions with commit hashes]

### Context for Next Session

If resuming this project:

1. **Read these files first:**
   - `.planning/STATE.md`
   - [Phase-specific files]

2. **Current state:**
   - [What's been built]
   - [What artifacts exist]

3. **Next action:**
   - [Specific next step]
```
</step>

<step name="commit">
```bash
git add .planning/STATE.md
git commit -m "docs: pause work — {brief description of state}"
```
</step>

</process>
