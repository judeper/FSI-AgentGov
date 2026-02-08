---
name: "gsd:map-codebase"
description: "Analyze codebase with parallel mapper agents to produce .planning/codebase/ documents"
tools: ["readFile", "listDirectory", "textSearch", "runInTerminal", "runSubagent"]
---

<objective>
Analyze the codebase using parallel mapper agents, each focused on a different dimension (tech, arch, quality, concerns). Results are written to `.planning/codebase/`.

This is the FSI-AgentGov adapted version. All paths use `.planning/` (not `.gsd/`).
</objective>

<context>
Input: $ARGUMENTS (optional focus area: tech, arch, quality, concerns, or "all")

@.planning/STATE.md
</context>

<process>

<step name="spawn_mappers">
If "all" or no argument, spawn 4 parallel mappers:

```
Task(prompt="Map codebase: technology stack...", subagent_type="gsd-codebase-mapper", description="Map: tech")
Task(prompt="Map codebase: architecture...", subagent_type="gsd-codebase-mapper", description="Map: arch")
Task(prompt="Map codebase: quality...", subagent_type="gsd-codebase-mapper", description="Map: quality")
Task(prompt="Map codebase: concerns...", subagent_type="gsd-codebase-mapper", description="Map: concerns")
```

If specific focus area, spawn only that mapper.
</step>

<step name="report">
Summarize findings from `.planning/codebase/` documents.
</step>

</process>
