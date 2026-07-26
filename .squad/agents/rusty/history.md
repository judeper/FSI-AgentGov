---
agent: rusty
created: 2026-07-21
---

# Rusty History

## 2026-07-21 — Issue #248: Control 1.3 §4b label-filter regression tests

**Task:** Add focused regression tests for the `Get-MgBetaInformationProtectionPolicyLabel`
`.Name` vs `.DisplayName` fix (issue #248).

**Approach:** Two-layer strategy matching prior art in `test_verify_playbook_powershell_helpers.py`:
- Static Python tests assert property access patterns directly in the playbook markdown.
- Runtime PowerShell harness tests extract `Set-AgentGroundingSite` from the live playbook,
  mock `Get-MgBetaInformationProtectionPolicyLabel` and `Update-MgGroup`, and exercise all
  branches with no tenant access.

**Key lesson:** The sentinel-replace template pattern (`##VAR##` + `.replace()`) cleanly
avoids f-string brace conflicts when embedding PowerShell `@{...}` syntax inside Python
generated scripts.  Use this whenever a PowerShell harness template has many `{ }` literals.

**Outcome:** 12 tests, 12 pass. `ruff check` clean. No edits to docs, workflows, or unrelated tests.

**Requirement gap:** "safe compatibility behavior" in issue #248 does not require a
`.DisplayName` fallback.  Linus's zero-match + warning path is safe and satisfies the
requirement.  Documented in `.squad/decisions/inbox/rusty-248-label-filter-tests.md`.
# Rusty — Agent History

## Learnings

### 2026-07-20 — OceanSquad#250: Control 1.6 DSPM for AI

**Issue pattern:** Collector name-regex heuristics break silently when
Microsoft Purview workload token names don't contain the matched substring.
`CopilotInteraction` contains no "AI" string — the old `$_.Workload -match 'AI'`
check missed the primary AI retention workload entirely.

**Fix pattern:** Always use exact workload token matching from Microsoft's
documented API values, not substring regexes on display names or tokens.

**Evaluator registration:** When adding a new `pass_condition` to the manifest,
the evaluator function must be added to `EVALUATORS` in `score.py` AND a
`dspm_for_ai` normalization entry must be added to `_normalize_purview_data`
(camelCase → snake_case). Without the normalizer, the evaluator receives `None`
even when the collector succeeds.

**Coverage matrix:** Adding a new evaluator always makes `generate_coverage_matrix.py`
go stale. Run `python scripts/generate_coverage_matrix.py` and commit the updated
`docs/reference/assessment-coverage.md` as part of the same PR.

**Test pattern for new evaluators:** Three test tiers work well:
1. Unit test the evaluator function directly (`score._eval_*`)
2. Unit test the normalizer (`score._normalize_purview_data`)
3. Integration test: collector contract fixture → `score.run()` → assert check result

**GitHub auth:** For this repo, `git push` via tokenized URL is reliable when the
Windows credential manager may cache the EMU token. Pattern:
`git push "https://judeper:$(gh auth token --user judeper)@github.com/judeper/FSI-AgentGov.git" <branch>`
