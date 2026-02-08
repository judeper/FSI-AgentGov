---
name: "gsd:plan-phase"
description: "Create detailed execution plan for a phase (PLAN.md) with verification loop"
tools: ["read", "edit", "search", "execute", "agent"]
---

<objective>
Create executable plans for a GSD phase. Optionally runs research first, creates plans via planner agent, and verifies plan quality via plan-checker agent.

This is the FSI-AgentGov adapted version. All paths use `.planning/` (not `.gsd/`).
</objective>

<execution_context>
../instructions/gsd-planning.instructions.md
../instructions/session-ownership.instructions.md
../instructions/questioning.instructions.md
</execution_context>

<context>
Input: $ARGUMENTS (phase number, optional flags)
Flags: --gaps (plan only gap closures from VERIFICATION.md)

@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/config.json
</context>

<process>

<step name="check_session_ownership">
Read `.planning/STATE.md` and verify session ownership before writing.
- If another tool owns the session, report and exit
- If no active tool, claim session by updating Active Tool field
</step>

<step name="load_context">
Read phase goal and success criteria from ROADMAP.md.
Read config.json for workflow settings:
- `workflow.research` → whether to run research before planning
- `workflow.plan_check` → whether to verify plans after creation
- `commit_docs` → whether to commit planning documents

If `--gaps` flag: read VERIFICATION.md to identify specific gaps that need closure.
</step>

<step name="extract_must_haves">
From the phase goal and success criteria, extract must_haves — the non-negotiable deliverables:

1. Read each success criterion from ROADMAP.md
2. For each criterion, identify the concrete artifact or state change required
3. List as must_haves that every plan must collectively cover

```
## Must-Haves for Phase {X}

Derived from ROADMAP.md success criteria:

| # | Must-Have | Source Criterion |
|---|----------|-----------------|
| 1 | {artifact or state change} | {criterion text} |
| 2 | ... | ... |
```

**Validation:** If any must-have cannot be traced to a success criterion, it's scope creep. If any success criterion has no must-have, it's a gap.
</step>

<step name="run_research">
If `workflow.research` is true and no RESEARCH.md exists for this phase:

```
Task(
  prompt="Research phase {phase_number} implementation for FSI-AgentGov.
    Phase goal: {goal_from_roadmap}
    Success criteria: {criteria_from_roadmap}
    Project context: {from PROJECT.md}

    Analyze existing codebase patterns, identify technical approach,
    document risks and dependencies.
    Write to: .planning/phases/{NN}-{name}/{NN}-RESEARCH.md",
  subagent_type="gsd-phase-researcher",
  description="Research Phase {phase}"
)
```

Research output: `.planning/phases/{NN}-{name}/{NN}-RESEARCH.md`

After research completes, read the output and validate:
- Does research cover all must-haves?
- Are there new risks that affect planning?
- Does the recommended approach align with existing patterns?
</step>

<step name="create_plans">
Spawn planner agent with full context:

```
Task(
  prompt="Create execution plans for phase {phase_number} of FSI-AgentGov.
    Phase dir: {phase_dir}
    Phase goal: {goal_from_roadmap}
    Success criteria: {criteria_from_roadmap}
    Must-haves: {must_haves_list}

    RESEARCH (if available):
    {research_content_or_'No research — plan from roadmap context'}

    PLANNING RULES:
    1. Every must-have must appear in at least one plan's acceptance criteria
    2. Plans in wave 1 have no dependencies; wave 2+ depend on earlier waves
    3. Each task must be atomic (independently committable)
    4. File manifests must list every file created or modified
    5. Include mkdocs build --strict as validation step for doc plans
    6. Include verify_controls.py for control modification plans
    7. Use FSI regulatory language rules in all documentation tasks

    WAVE ASSIGNMENT:
    - Foundation/infrastructure work → Wave 1
    - Content that builds on wave 1 artifacts → Wave 2
    - Integration/cross-cutting concerns → Wave 3
    - Plans in the same wave MUST be independent

    Write plans to: .planning/phases/{NN}-{name}/{NN}-{PP}-PLAN.md",
  subagent_type="gsd-planner",
  description="Plan Phase {phase}"
)
```

For `--gaps` mode: planner reads VERIFICATION.md and creates gap closure plans with `gap_closure: true` in frontmatter. Gap plans get the next available plan number.
</step>

<step name="validate_plan_coverage">
After plans are created, verify must-have coverage:

1. Read all created PLAN.md files
2. For each must-have, confirm at least one plan task addresses it
3. Report coverage:

```
## Plan Coverage Validation

| Must-Have | Covered By | Status |
|-----------|-----------|--------|
| {must_have_1} | Plan 01, Task 2 | COVERED |
| {must_have_2} | — | MISSING |
```

If any must-have is MISSING, either:
- Ask planner to create an additional plan
- Ask user if the must-have should be deferred
</step>

<step name="verify_plans">
If `workflow.plan_check` is true:

```
Task(
  prompt="Verify phase {phase_number} plans will achieve the phase goal.
    Phase goal: {goal_from_roadmap}
    Success criteria: {criteria_from_roadmap}
    Must-haves: {must_haves_list}

    Read all PLAN.md files in {phase_dir}.
    Check: goal coverage, task quality, feasibility, wave correctness.
    Report findings with APPROVED or NEEDS REVISION.",
  subagent_type="gsd-plan-checker",
  description="Check Phase {phase} plans"
)
```

If plan checker returns NEEDS REVISION:
1. Present specific issues to user
2. Offer options: revise automatically, revise manually, or accept as-is
3. If revising, re-spawn planner with checker feedback
</step>

<step name="commit_plans">
If `commit_docs` is true:
```bash
git add .planning/phases/${PHASE_DIR}/*-PLAN.md
git add .planning/phases/${PHASE_DIR}/*-RESEARCH.md
git commit -m "docs({phase}): create phase execution plans"
```
</step>

<step name="offer_next">
```
## Plans Ready

**Phase {X}: {Name}** — {plan_count} plans across {wave_count} waves

| Plan | Wave | Title | Must-Haves Covered |
|------|------|-------|--------------------|
| {PP} | {W} | {title} | {list} |

`/gsd:execute-phase {X}`
```
</step>

</process>

<success_criteria>
- [ ] Phase RESEARCH.md created (if research enabled)
- [ ] All PLAN.md files created with proper YAML frontmatter (wave, dependencies, must_haves)
- [ ] Every must-have from success criteria is covered by at least one plan
- [ ] Plans verified by plan-checker (if enabled)
- [ ] Wave assignments are correct (no cross-dependencies within waves)
- [ ] File manifests are complete in every plan
- [ ] Plans committed (if commit_docs enabled)
</success_criteria>
