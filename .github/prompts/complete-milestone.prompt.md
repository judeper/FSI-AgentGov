---
name: "gsd:complete-milestone"
description: "Archive completed milestone and prepare for next version"
tools: ["readFile", "editFiles", "listDirectory", "textSearch", "runInTerminal"]
---

<objective>
Archive a completed milestone to MILESTONES.md, update STATE.md, and prepare for the next milestone.

This is the FSI-AgentGov adapted version. All paths use `.planning/` (not `.gsd/`).
</objective>

<context>
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/MILESTONES.md
@.planning/REQUIREMENTS.md
</context>

<process>

<step name="verify_completion">
Confirm all phases are marked complete in ROADMAP.md.
If not, suggest `/gsd:audit-milestone` first.
</step>

<step name="archive">
1. Append milestone summary to MILESTONES.md
2. Record: version, name, phases completed, plans executed, key deliverables
3. Update STATE.md Milestone Series Plan
4. Update performance metrics in STATE.md
</step>

<step name="commit">
```bash
git add .planning/MILESTONES.md .planning/STATE.md .planning/ROADMAP.md
git commit -m "docs: complete milestone {version}"
```
</step>

<step name="offer_next">
```
## Milestone {version} Archived

Next in series: {next_version} — {next_name}

`/gsd:new-milestone` — Define the next milestone
```
</step>

</process>
