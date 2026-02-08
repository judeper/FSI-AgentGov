---
name: "gsd:plan-milestone-gaps"
description: "Create phases to close all gaps identified by milestone audit"
tools: ["readFile", "editFiles", "listDirectory", "textSearch", "runInTerminal"]
---

<objective>
After a milestone audit identifies gaps, create new phases to close them. Reads the audit report and generates targeted phases.

This is the FSI-AgentGov adapted version. All paths use `.planning/` (not `.gsd/`).
</objective>

<context>
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/REQUIREMENTS.md
</context>

<process>

<step name="read_audit">
Read the milestone audit report (from `/gsd:audit-milestone`).
Identify unmet requirements and verified gaps.
</step>

<step name="create_gap_phases">
For each gap or group of related gaps:
1. Create a new phase in ROADMAP.md
2. Define goal as closing the specific gap
3. Map to unmet requirements
4. Create phase directory
</step>

<step name="offer_next">
```
## Gap Closure Phases Created

{count} phases added to close {gap_count} gaps.

`/gsd:plan-phase {N}` — Plan the first gap closure phase
```
</step>

</process>
