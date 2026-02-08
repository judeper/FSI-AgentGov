---
name: "gsd:debug"
description: "Systematic debugging with persistent state across context resets"
tools: ["read", "edit", "search", "execute", "agent"]
---

<objective>
Investigate and resolve issues using the scientific method with persistent debug state. Spawns a debugger agent that tracks hypotheses, tests, and findings.

This is the FSI-AgentGov adapted version. All paths use `.planning/` (not `.gsd/`).
</objective>

<context>
Input: $ARGUMENTS (issue description or "resume" to continue previous session)

@.planning/STATE.md
</context>

<process>

<step name="initialize_or_resume">
If "resume": read existing debug session from `.planning/debug/`.
Otherwise: create new debug session file.
</step>

<step name="spawn_debugger">
```
Task(
  prompt="Debug the following issue: {description}...",
  subagent_type="gsd-debugger",
  description="Debug: {brief_description}"
)
```
</step>

<step name="report_results">
Display findings:
- Root cause (if identified)
- Fix applied (if resolved)
- Next steps (if unresolved)
</step>

</process>
