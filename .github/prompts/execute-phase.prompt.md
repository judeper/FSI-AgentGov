---
name: "gsd:execute-phase"
description: "Execute all plans in a phase with wave-based parallelization"
tools: ["read", "edit", "search", "execute", "agent", "todo"]
---

<objective>
Execute all plans in a phase using wave-based parallel execution. Orchestrator delegates plan execution to subagents, manages waves, and handles checkpoints.

This is the FSI-AgentGov adapted version. All paths use `.planning/` (not `.gsd/`).
</objective>

<execution_context>
../instructions/checkpoints.instructions.md
../instructions/git-integration.instructions.md
../instructions/verification-patterns.instructions.md
../instructions/session-ownership.instructions.md
../instructions/build-validation.instructions.md
</execution_context>

<context>
Input: $ARGUMENTS (phase number, e.g., "3")
Optional flags: --gaps-only (execute only gap closure plans)

@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/config.json
</context>

<process>

<step name="check_session_ownership">
Read `.planning/STATE.md` and check `Active Tool` field.
- If another tool owns the session, report the conflict and exit without modifying any files
- If no active tool or current tool matches, claim the session by updating STATE.md
- Record the session start timestamp
</step>

<step name="load_project_state">
Read `.planning/config.json` for workflow settings:
- `model_profile` → determines agent model selection
- `workflow.verifier` → whether to run verification after execution
- `commit_docs` → whether to commit planning documents

Read `.planning/ROADMAP.md` for phase goal, success criteria, and expected plan count.
</step>

<step name="validate_phase">
Confirm phase exists and has plans:

```bash
PADDED_PHASE=$(printf "%02d" ${PHASE_ARG} 2>/dev/null || echo "${PHASE_ARG}")
PHASE_DIR=$(ls -d .planning/phases/${PADDED_PHASE}-* .planning/phases/${PHASE_ARG}-* 2>/dev/null | head -1)
if [ -z "$PHASE_DIR" ]; then
  echo "ERROR: No phase directory matching '${PHASE_ARG}'"
  exit 1
fi

PLAN_COUNT=$(ls -1 "$PHASE_DIR"/*-PLAN.md 2>/dev/null | wc -l | tr -d ' ')
if [ "$PLAN_COUNT" -eq 0 ]; then
  echo "ERROR: No plans found in $PHASE_DIR"
  exit 1
fi
```
</step>

<step name="discover_plans">
List all plans and extract metadata:

```bash
ls -1 "$PHASE_DIR"/*-PLAN.md 2>/dev/null | sort
ls -1 "$PHASE_DIR"/*-SUMMARY.md 2>/dev/null | sort
```

For each plan, read YAML frontmatter to extract:
- `wave` — wave number for parallel grouping
- `autonomous` — whether plan can run without user interaction
- `gap_closure` — whether this is a gap closure plan from verification
- `dependencies` — list of plans that must complete first
- `must_haves` — critical deliverables this plan produces

**Skip logic:**
- Plans with a corresponding SUMMARY.md are already complete — skip them
- If `--gaps-only` flag: skip plans without `gap_closure: true` in frontmatter
- If a plan's dependencies are not yet complete (no SUMMARY.md), defer to later wave
</step>

<step name="group_by_wave">
Group remaining plans by wave number from frontmatter.

**Wave assignment rules:**
- Wave 1: Plans with no dependencies (foundation work)
- Wave 2+: Plans that depend on wave 1 outputs
- Plans in the same wave MUST be independent (no cross-dependencies)
- If a plan has unmet dependencies, bump it to the next wave after its dependencies

Report wave structure to user before executing:

```
## Execution Plan

**Phase {X}: {Name}** — {total_plans} plans across {wave_count} waves
({skipped_count} already complete, {remaining_count} to execute)

| Wave | Plans | Dependencies | What it builds |
|------|-------|-------------|----------------|
| 1 | 01-01, 01-02 | none | {from plan objectives} |
| 2 | 01-03 | 01-01 | {from plan objectives} |
```
</step>

<step name="execute_waves">
Execute each wave in sequence. Plans within a wave run in parallel via subagents.

**For each wave:**

1. **Announce wave:** Report which plans are executing and what they build
2. **Create pre-wave checkpoint:**
   ```bash
   git add -A && git stash push -m "checkpoint: pre-wave-{N}-phase-{X}"
   git stash pop
   ```
3. **Spawn executor agents** for all plans in the wave simultaneously:
   ```
   Task(
     prompt="Execute plan {plan_number} of phase {phase_number}.
       Phase dir: {phase_dir}
       Plan file: {plan_file_path}
       Phase goal: {goal_from_roadmap}

       INLINE PLAN CONTENT:
       {full_plan_content}

       RULES:
       - Read the plan file for full task details
       - Execute each task per its acceptance criteria
       - Create atomic commits after each logical unit
       - Write SUMMARY.md when complete
       - If you encounter a blocker, document it in SUMMARY.md and stop
       - FSI language rules: never use 'ensures compliance', 'guarantees', 'will prevent', 'eliminates risk'
       - Run 'mkdocs build --strict' after documentation changes",
     subagent_type="gsd-executor",
     description="Execute Plan {plan_id}"
   )
   ```
   **Important:** Always inline the full plan content in the spawn prompt. Subagents may not have file access context from previous turns.

4. **Collect results:** Read each plan's SUMMARY.md to confirm completion
5. **Handle failures** (see deviation rules below)
6. **Report wave results:**
   ```
   ### Wave {N} Results

   | Plan | Status | Duration | Key Files |
   |------|--------|----------|-----------|
   | 01-01 | Complete | 3min | file1.md, file2.md |
   | 01-02 | Failed | 2min | See deviation |
   ```
7. **Proceed to next wave** only if current wave succeeded
</step>

<step name="deviation_handling">
**Four deviation rules:**

1. **Minor deviation** (task done differently than planned but goal met):
   - Note in SUMMARY.md under "Decisions Made"
   - Continue execution
   - No user intervention required

2. **Scope addition** (executor discovers additional work needed):
   - Document as "Discovered Work" in SUMMARY.md
   - Continue with current plan
   - Report at wave end — user decides whether to add plans

3. **Task blocker** (task cannot be completed as planned):
   - Executor stops and documents the blocker in SUMMARY.md
   - Orchestrator reports to user with options:
     a. Skip the blocked task and continue
     b. Modify the approach and retry
     c. Stop execution and replanning

4. **Build failure** (mkdocs build or verify_controls fails):
   - Executor attempts one fix cycle (read error, fix, rebuild)
   - If still failing after fix attempt, stop and report
   - Never commit code that fails build validation
</step>

<step name="checkpoint_protocol">
**Three checkpoint types:**

1. **Pre-wave checkpoint:** Before each wave starts, ensure working tree is clean
   - All previous wave commits are pushed
   - No uncommitted changes from previous waves

2. **Intra-plan checkpoint:** Executor creates atomic commits per task
   - Commit message format: `type(scope): description`
   - Stage specific files, never `git add -A`
   - Each commit should be independently revertable

3. **Post-wave checkpoint:** After all plans in a wave complete
   - Verify all SUMMARY.md files exist for completed plans
   - Run build validation
   - Update STATE.md with progress
</step>

<step name="resumption_logic">
If execution was previously interrupted (some plans have SUMMARY.md, others don't):

1. Read existing SUMMARY.md files to determine what completed
2. Check for any partial state (uncommitted changes, incomplete SUMMARY.md)
3. Report resumption point:
   ```
   ## Resuming Phase {X} Execution

   **Completed:** Plans 01, 02 (wave 1)
   **Remaining:** Plan 03 (wave 2)
   **State:** Clean (no partial work detected)
   ```
4. Continue from the next incomplete wave
5. Never re-execute plans that have valid SUMMARY.md files
</step>

<step name="verify_phase_goal">
If `workflow.verifier` is true, spawn verifier:

```
Task(
  prompt="Verify phase {phase_number} goal achievement.
    Phase dir: {phase_dir}
    Phase goal: {goal_from_roadmap}
    Success criteria: {criteria_from_roadmap}

    Read all SUMMARY.md files in the phase directory.
    Check if the codebase now delivers the phase goal (goal-backward analysis).
    Run: mkdocs build --strict
    Run: python scripts/verify_controls.py
    Write VERIFICATION.md with findings.",
  subagent_type="gsd-verifier",
  description="Verify Phase {phase}"
)
```

Route by verification status:
- `passed` → update roadmap, celebrate
- `gaps_found` → report gaps, offer `/gsd:plan-phase {X} --gaps`
</step>

<step name="fsi_build_validation">
FSI-AgentGov specific: Run build validation after phase execution:

```bash
mkdocs build --strict
python scripts/verify_controls.py
```

Report any failures. Build must pass before marking phase complete.
</step>

<step name="update_roadmap">
Mark phase complete in ROADMAP.md. Update STATE.md with:
- Phase completion status
- Plan count and duration
- Last activity timestamp
- Next action context

If `commit_docs` is true:
```bash
git add .planning/ROADMAP.md .planning/STATE.md .planning/phases/${PHASE_DIR}/*-VERIFICATION.md
git commit -m "docs(phase-{X}): complete phase execution"
```
</step>

<step name="offer_next">
If more phases remain:
```
## Next Up

**Phase {X+1}: {Name}** — {Goal}

`/gsd:plan-phase {X+1}`
```

If milestone complete:
```
MILESTONE COMPLETE!

All {N} phases executed across {plan_count} plans.

`/gsd:complete-milestone`
```
</step>

</process>

<success_criteria>
- [ ] All plans in phase executed (or gaps documented)
- [ ] Each plan has SUMMARY.md with commits and file manifest
- [ ] Phase VERIFICATION.md created (if verifier enabled)
- [ ] Build validation passes (mkdocs build --strict)
- [ ] Control validation passes (verify_controls.py)
- [ ] ROADMAP.md updated with phase status
- [ ] STATE.md updated with progress and next action
- [ ] All commits follow atomic commit pattern
</success_criteria>
