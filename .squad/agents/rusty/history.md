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
