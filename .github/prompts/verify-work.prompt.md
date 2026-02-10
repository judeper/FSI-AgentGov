---
name: "gsd-verify-work"
description: "Validate built features through conversational UAT"
tools: ["read", "search", "execute", "agent"]
---

<objective>
Validate that built features meet their goals through conversational user acceptance testing. Spawns a verifier agent and presents findings interactively.

This is the FSI-AgentGov adapted version. All paths use `.planning/` (not `.gsd/`).
</objective>

<context>
Input: $ARGUMENTS (phase number)

@.planning/ROADMAP.md
@.planning/STATE.md
</context>

<process>

<step name="spawn_verifier">
```
Task(
  prompt="Verify phase {phase_number} goal achievement...",
  subagent_type="gsd-verifier",
  description="Verify Phase {phase}"
)
```
</step>

<step name="present_findings">
Display verification results interactively:
- What was verified
- What passed
- What failed or has gaps
- Build validation results
</step>

<step name="fsi_validation">
FSI-AgentGov specific checks:
```bash
mkdocs build --strict
python scripts/verify_controls.py
```
</step>

<step name="route">
- All passed: `/gsd-progress`
- Gaps found: `/gsd-plan-phase {N} --gaps`
- Manual testing needed: Guide user through verification checklist
</step>

</process>
