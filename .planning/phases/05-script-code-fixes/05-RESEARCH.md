# Phase 5 Research: PowerShell & Script Bug Fixes

**Phase:** 5 — PowerShell & Script Bug Fixes  
**Depends on:** Phase 1 (CAA/DEC scripts already fixed)  
**Research Date:** 2026-02-11  
**Requirements:** SCF-01 through SCF-06

---

## SCF-01: Fix `$isBlock` Variable Scoping in Test-PolicyCompliance.ps1

### Affected Files

| File | Lines | Severity |
|------|-------|----------|
| `scripts/Test-PolicyCompliance.ps1` | L209-210 (definition), L239 (stale usage) | **High** — produces false positives/negatives |

### Current State

In **Check 4: MFA / Grant Controls** (L206-221), `$isBlock` is defined inside the `foreach` loop:

```powershell
# L209-210 (inside Check 4 foreach loop)
$hasMfa = $controls.BuiltInControls -contains 'mfa'
$isBlock = $controls.BuiltInControls -contains 'block'
```

In **Check 5: Session Controls** (L224-250), `$isBlock` is referenced **outside its originating foreach loop** at L239:

```powershell
# L239 (inside Check 5 foreach loop — DIFFERENT loop variable $policy)
if (-not $isBlock) {
```

Because `$isBlock` retains the value from the **last iteration** of Check 4's loop, it has no relationship to the `$policy` being evaluated in Check 5. For every policy evaluated in Check 5, the session control gap logic incorrectly uses the `$isBlock` value from whichever policy happened to be last in Check 4.

### Additional Issue: `$totalGaps` / `$driftCount` Used Before Assignment

At L310 (Dataverse persistence section), the code references `$totalGaps` and `$driftCount`:

```powershell
$overallSeverity = if ($totalGaps -eq 0 -and $driftCount -eq 0) { 1 }
```

But `$totalGaps` and `$driftCount` are not assigned until L393-394 (Summary section), **after** the Dataverse persistence block. These variables will always be `$null` during persistence, causing incorrect severity calculation.

### Fix Required

1. **`$isBlock` fix:** Recalculate `$isBlock` from `$policy.GrantControls.BuiltInControls` at the start of Check 5's foreach loop body.
2. **`$totalGaps`/`$driftCount` fix:** Move summary calculations before the Dataverse persistence block, or compute them inline earlier.

### Technical Approach

```powershell
# Check 5: Add at the top of the foreach body
foreach ($policy in $policies) {
    $session = $policy.SessionControls
    $isBlock = $policy.GrantControls.BuiltInControls -contains 'block'  # FIX: recalculate per-policy
    # ... rest of check 5
}
```

### Risk

- **Low risk** — purely local scope fix. No external API or schema changes.
- Test by reviewing output for a block-type policy to ensure session checks are skipped correctly.

---

## SCF-02: Fix CAA Module Manifest Export List

### Affected Files

| File | Lines | Severity |
|------|-------|----------|
| `scripts/conditional-access-automation.psd1` | L24-30 | **Medium** — module import fails if exported functions don't exist |

### Current State

The manifest (`FunctionsToExport`) lists 5 functions:

```powershell
FunctionsToExport = @(
    'Deploy-CAPolicies'           # NO script file exists
    'Test-PolicyCompliance'       # EXISTS as Test-PolicyCompliance.ps1 (standalone script, not a function)
    'Register-ServicePrincipal'   # NO script file exists
    'Export-PolicyBaseline'       # NO script file exists
    'Watch-PolicyDrift'           # NO script file exists
)
```

**File search results:** None of `Deploy-CAPolicies.ps1`, `Register-ServicePrincipal.ps1`, `Export-PolicyBaseline.ps1`, or `Watch-PolicyDrift.ps1` exist anywhere in the repository.

The nested module `private/CAAClient.psm1` **does** exist at `scripts/private/CAAClient.psm1`.

Existing private helpers under `scripts/private/`:
- `Connect-GraphSession.ps1`
- `Get-ZoneClassification.ps1`
- `Test-ParameterValidation.ps1`
- `Get-PolicyBaseline.ps1`
- `Compare-PolicyBaseline.ps1`

### What Planning Says

Per `.planning/research/ARCHITECTURE.md` and `.planning/phases/04-evidence-export-framework-integration-caa/`, these scripts were planned as part of earlier phases but never materialized as actual files. The CHANGELOG mentions `Register-ServicePrincipal.ps1` was fixed (DEBT-01) but those references point to files that don't exist on disk.

### Fix Required

**Option A (Recommended):** Remove the non-existent exports from `FunctionsToExport`. Since `Test-PolicyCompliance.ps1` is a standalone script (not loaded as a module function), also remove it. Result: `FunctionsToExport = @()` — the manifest only provides module metadata and loads `CAAClient.psm1` via `NestedModules`.

**Option B:** Create stub functions that emit `Write-Warning "Not implemented"`. This preserves the manifest contract for future development.

### Technical Approach

Option A is simpler and honest. Add a comment documenting the planned functions for future implementation.

### Risk

- **Low risk** — the manifest currently cannot be loaded successfully anyway (PowerShell will error on missing exports). The fix makes the manifest loadable.

---

## SCF-03: Fix 4.7 PowerShell SKU Filter

### Affected Files

| File | Lines | Severity |
|------|-------|----------|
| `docs/playbooks/control-implementations/4.7/powershell-setup.md` | L36-42 | **Medium** — SKU filter will never match Copilot licenses |

### Current State

The "Inventory Copilot Licenses" section uses `SkuId` with a regex match:

```powershell
# L36-42
$licensedUsers = Get-MgUser -Filter "assignedLicenses/any()" -All |
    Where-Object {
        $_.AssignedLicenses | Where-Object {
            $_.SkuId -match "copilot" -or $_.SkuId -match "Copilot"
        }
    }
```

**Problem:** `SkuId` is a GUID (e.g., `639dec6b-bb19-468b-871c-c5c441c4b0cb`). It will **never** match the regex `"copilot"`. The correct approach is to resolve SKU IDs via `Get-MgSubscribedSku` and filter by `SkuPartNumber` which contains human-readable names like `Microsoft_365_Copilot`.

### Also Affected

The verification-testing.md for 4.7 at L90-91 has a similar issue:
```powershell
# Count licensed users
$licensedUsers = Get-MgUser -Filter "assignedLicenses/any()" -All
Write-Host "Users with licenses: $($licensedUsers.Count)"
```
This doesn't filter for Copilot specifically (minor — it's just counting all licensed users).

### Fix Required

Replace the SKU filter with a two-step approach:

```powershell
# Step 1: Find Copilot SKU IDs from tenant subscriptions
$copilotSkus = Get-MgSubscribedSku -All | Where-Object {
    $_.SkuPartNumber -match 'Copilot'
} | Select-Object -ExpandProperty SkuId

# Step 2: Filter users by those SKU IDs
$licensedUsers = Get-MgUser -Filter "assignedLicenses/any()" -All |
    Where-Object {
        $_.AssignedLicenses | Where-Object {
            $_.SkuId -in $copilotSkus
        }
    }
```

### Risk

- **Low risk** — documentation-only change. Does not affect any running scripts.
- The fix is more robust because it handles all Copilot SKU variants (e.g., `Microsoft_365_Copilot`, `Copilot_Studio`, etc.).

---

## SCF-04: Mark Non-Existent Cmdlets in Promotion Gates as Pseudocode

### Affected Files

| File | Lines | Cmdlet | Status |
|------|-------|--------|--------|
| `docs/playbooks/advanced-implementations/agent-blueprint-promotion-gates/implementation-guide.md` | L395 | `Invoke-SecurityScan` | **Not a real cmdlet** — custom function not defined in this repo |
| Same file | L464 | `Get-AdminPowerAppAgent -AgentId ... -EnvironmentId ...` | **Non-existent** — no `-AgentId` or `-EnvironmentId` params on this cmdlet |
| Same file | L473 | `Get-AdminPowerAppAgentTopics` | **Non-existent** — no such cmdlet in Power Platform admin module |
| Same file | L487 | `Get-AdminPowerAppAgentConnectors` | **Non-existent** — no such cmdlet |
| Same file | L500 | `Test-DlpPolicyCompliance` | **Custom function** — defined in same file but calls non-existent cmdlets |
| Same file | L530 | `Get-AdminPowerAppAgent -AgentId` (in Test-DlpPolicyCompliance) | Same as above |
| Same file | L618 | `Get-DataverseRecords` | **Non-existent** — no such cmdlet |
| Same file | L627 | `Send-EscalationNotification` | **Non-existent** — custom, not defined |
| Same file | L631 | `Send-ReminderNotification` | **Non-existent** — custom, not defined |
| `docs/playbooks/advanced-implementations/agent-blueprint-promotion-gates/index.md` | L113 | `Get-AdminPowerAppAgent` (no pipe-valid form) | **Exists but not agent-specific** |
| Same file | L115 | `Get-AdminPowerAppAgentMetadata` | **Non-existent** |

### Current State

These are aspirational cmdlets representing capabilities that Power Platform admin modules do **not** currently expose. The playbook presents them as if they are production-ready code, which could mislead administrators.

**Note:** `Get-DlpPolicy` (L530) **is** a real cmdlet from the `Microsoft.PowerApps.Administration.PowerShell` module. However, the way it's called (`-EnvironmentName (Get-AdminPowerAppAgent ...)`) chains with a non-existent cmdlet.

### Fix Required

Add `# PSEUDOCODE` or `# CONCEPTUAL` comments to all non-existent cmdlets. Wrap the code blocks in an admonition:

```markdown
!!! warning "Pseudocode — Not Production Ready"
    The following PowerShell examples use conceptual cmdlets that do not exist
    as of February 2026. They illustrate the intended automation pattern for when
    Power Platform admin modules support agent-level queries.
```

### Non-Existent Cmdlets Summary

| Cmdlet | Real? | Notes |
|--------|-------|-------|
| `Get-AdminPowerAppAgent` | **Partial** — exists but params differ | No `-AgentId` or `-EnvironmentId` params |
| `Get-AdminPowerAppAgentTopics` | **No** | |
| `Get-AdminPowerAppAgentConnectors` | **No** | |
| `Get-AdminPowerAppAgentMetadata` | **No** | |
| `Invoke-SecurityScan` | **No** | Custom; intent is clear |
| `Test-DlpPolicyCompliance` | **Custom** | Defined in same file but calls non-existent cmdlets |
| `Get-DataverseRecords` | **No** | Should use Dataverse Web API / OData |
| `Send-EscalationNotification` | **No** | Custom notification function |
| `Send-ReminderNotification` | **No** | Custom notification function |

### Risk

- **Low risk** — documentation-only change. Adds clarity without breaking anything.
- Readers currently might waste time trying to run these cmdlets and encountering errors.

---

## SCF-05: Align Cross-Solution Integration Parameter Names

### Affected Files

| File | Parameter Used | Expected | Lines |
|------|---------------|----------|-------|
| `maintainers-local/solutions-staging/cross-solution-integration/scripts/powershell/Sync-SolutionAssessments.ps1` | `-Solution $solution` | `-SolutionId $solution` | L417, L483, L578 |
| `maintainers-local/solutions-staging/cross-solution-integration/scripts/powershell/IntegrationConfig.psm1` | `-SolutionId` (param name) | — | L193, L215 |

### Current State

**In `IntegrationConfig.psm1`:**
- `ConvertTo-DashboardStatus` defines parameter as `-SolutionId` (L215):
  ```powershell
  [string]$SolutionId,
  ```
- `Get-SolutionTableConfig` takes **no parameters** — it returns a full hashtable. Callers are expected to index into it: `$config['DEC']`.

**In `Sync-SolutionAssessments.ps1`:**
- Calls `Get-SolutionTableConfig -Solution $solution` (L417) — **will fail** because the function doesn't accept a `-Solution` parameter. It returns the full hashtable; the caller should use `(Get-SolutionTableConfig)[$solution]`.
- Calls `ConvertTo-DashboardStatus -Solution 'DEC' -InputStatus $severityDist` (L483) — **will fail** because the parameter is named `-SolutionId`, not `-Solution`.
- Same mismatch at L578: `ConvertTo-DashboardStatus -Solution $solution -InputStatus $latestRecord.$statusColumn`

### Fix Required

Two options:

**Option A (Align caller to definition — recommended):** Fix `Sync-SolutionAssessments.ps1`:
1. L417: Change `Get-SolutionTableConfig -Solution $solution` to `(Get-SolutionTableConfig)[$solution]`
2. L483: Change `-Solution 'DEC'` to `-SolutionId 'DEC'`
3. L578: Change `-Solution $solution` to `-SolutionId $solution`

**Option B (Align definition to caller):** Add `-SolutionId` alias or rename param in `IntegrationConfig.psm1`. This is riskier because it changes the module's public API.

### Risk

- **Medium risk** — these are runtime bugs. If left unfixed, `Sync-SolutionAssessments.ps1` will fail when executed.
- The `Get-SolutionTableConfig` call with a non-existent parameter will silently ignore the parameter (PowerShell doesn't error on extra named params to advanced functions by default), but the return value won't be filtered — `$tableConfig` will be the full hashtable, not a single solution's config, causing downstream errors.

---

## SCF-06: Add Search-UnifiedAuditLog Pagination Warnings

### Affected Files

Files using `Search-UnifiedAuditLog` with `-ResultSize 5000` (the max single-call limit) but **no pagination handling**:

| File | Lines | ResultSize | Has Pagination? |
|------|-------|-----------|----------------|
| `docs/playbooks/monitoring-and-validation/purview-audit-query-pack.md` | L147-151 | 5000 | **No** |
| Same file | L169-173 | 5000 | **No** |
| Same file | L181-185 | 5000 | **No** |
| `docs/playbooks/control-implementations/4.5/powershell-setup.md` | L40-42 | 5000 | **No** |
| Same file | L64-66 | 5000 | **No** |
| Same file | L135-137 | 5000 | **No** |
| Same file | L228-230 | 5000 | **No** |
| `docs/playbooks/monitoring-and-validation/semantic-index-governance-queries.md` | L173-174 | 1000 | **No** |
| `docs/playbooks/control-implementations/4.4/troubleshooting.md` | L60-61 | 100 | **No** (but small) |
| `docs/playbooks/control-implementations/4.5/verification-testing.md` | L99-100 | 10 | **No** (but test-only) |
| `docs/playbooks/control-implementations/3.2/powershell-setup.md` | L128 | 5000 | **No** |
| `docs/playbooks/validation-testing/script-validation-guide.md` | L131 | 10 | **No** (but test-only) |

### Current State

`Search-UnifiedAuditLog` has a hard maximum of **5000 results per call**. For environments with high audit volume, queries hitting this limit silently truncate results — the cmdlet does not warn you that more records exist. Microsoft's documentation recommends using `-SessionId` and `-SessionCommand ReturnLargeSet` for pagination.

None of the playbook examples include pagination. The most critical ones are `purview-audit-query-pack.md` (the primary audit evidence playbook) and `4.5/powershell-setup.md` (used for SharePoint audit evidence collection).

### Fix Required

Add a pagination warning admonition to each playbook that uses `Search-UnifiedAuditLog` with `ResultSize ≥ 1000`:

```markdown
!!! warning "Pagination Required for Large Tenants"
    `Search-UnifiedAuditLog` returns a maximum of 5,000 records per call.
    For environments with high audit volume, use session-based pagination:

    ```powershell
    $sessionId = [guid]::NewGuid().ToString()
    $allResults = @()
    do {
        $batch = Search-UnifiedAuditLog -StartDate $startDate -EndDate $endDate `
            -RecordType SharePoint -SessionId $sessionId `
            -SessionCommand ReturnLargeSet -ResultSize 5000
        $allResults += $batch
    } while ($batch.Count -eq 5000)
    ```

    See [Microsoft documentation](https://learn.microsoft.com/en-us/powershell/module/exchange/search-unifiedauditlog) for details.
```

### Priority

Focus on these files (highest impact):
1. `docs/playbooks/monitoring-and-validation/purview-audit-query-pack.md` — primary audit evidence playbook
2. `docs/playbooks/control-implementations/4.5/powershell-setup.md` — SharePoint audit evidence

Lower priority (small result sizes or test-only):
- `docs/playbooks/control-implementations/4.4/troubleshooting.md` (ResultSize 100)
- `docs/playbooks/validation-testing/script-validation-guide.md` (ResultSize 10)
- `docs/playbooks/control-implementations/4.5/verification-testing.md` (ResultSize 10)

### Risk

- **Low risk** — documentation-only change (adding warnings/admonitions).
- Significant value for regulated environments where audit completeness is required for compliance evidence.

---

## Dependencies Between Fixes

```
SCF-01 ──────────────────────── (independent)
SCF-02 ──────────────────────── (independent)
SCF-03 ──────────────────────── (independent)
SCF-04 ──────────────────────── (independent)
SCF-05 ──────────────────────── (independent)
SCF-06 ──────────────────────── (independent)
```

All 6 fixes are **independent** — no fix depends on another. This cleanly supports the two-worktree split:

- **Plan A (Worktree A):** SCF-01, SCF-02, SCF-03, SCF-04
- **Plan B (Worktree B):** SCF-05, SCF-06

---

## New Risks Discovered During Research

### Risk 1: `$totalGaps` / `$driftCount` Used Before Assignment (Test-PolicyCompliance.ps1)

At L310, the Dataverse persistence section references `$totalGaps` and `$driftCount`, but these are computed at L393-394 (Summary section). During Dataverse persistence, both will be `$null` (treated as 0 in numeric comparisons), producing incorrect severity calculations. This is a secondary bug within the SCF-01 scope.

**Recommendation:** Include this fix in SCF-01 — move the Summary calculations before the Dataverse block, or compute the values inline earlier.

### Risk 2: `Get-SolutionTableConfig` Silent Parameter Ignoring

At L417 of `Sync-SolutionAssessments.ps1`, calling `Get-SolutionTableConfig -Solution $solution` doesn't error — PowerShell silently ignores unknown named parameters on non-advanced functions. But the return value is the full hashtable, not a single config entry. Downstream code expecting a single config object will fail with confusing errors about missing properties.

**Recommendation:** This is already captured in SCF-05 but worth noting that the failure mode is non-obvious and will manifest as property access errors deeper in the script.

### Risk 3: Module Manifest NestedModules Path

The manifest declares `NestedModules = @('private/CAAClient.psm1')`. The file exists at `scripts/private/CAAClient.psm1`. If the module is imported from a different working directory, the relative path may not resolve. This is an existing design decision (the module is meant to be loaded from the `scripts/` directory) but worth noting.

### Risk 4: `Invoke-AgentSecurityScan` Self-Reference Bug

At L512 in the implementation guide, `$scanResults.Summary.Passed` references `$scanResults.Summary.Critical` — but `$scanResults.Summary` hasn't been assigned yet at that point (it's being constructed). This would always evaluate to `$null -eq 0` → `$true`. Since this is pseudocode (SCF-04), the fix is just adding the pseudocode annotation rather than correcting the logic.

---

## File Manifest (All Affected Files)

### Plan A (SCF-01 through SCF-04)

| Action | File | Requirement |
|--------|------|-------------|
| Modify | `scripts/Test-PolicyCompliance.ps1` | SCF-01 |
| Modify | `scripts/conditional-access-automation.psd1` | SCF-02 |
| Modify | `docs/playbooks/control-implementations/4.7/powershell-setup.md` | SCF-03 |
| Modify | `docs/playbooks/advanced-implementations/agent-blueprint-promotion-gates/implementation-guide.md` | SCF-04 |
| Modify | `docs/playbooks/advanced-implementations/agent-blueprint-promotion-gates/index.md` | SCF-04 |

### Plan B (SCF-05 through SCF-06)

| Action | File | Requirement |
|--------|------|-------------|
| Modify | `maintainers-local/solutions-staging/cross-solution-integration/scripts/powershell/Sync-SolutionAssessments.ps1` | SCF-05 |
| Modify | `docs/playbooks/monitoring-and-validation/purview-audit-query-pack.md` | SCF-06 |
| Modify | `docs/playbooks/control-implementations/4.5/powershell-setup.md` | SCF-06 |
| Modify | `docs/playbooks/monitoring-and-validation/semantic-index-governance-queries.md` | SCF-06 (lower priority) |
| Modify | `docs/playbooks/control-implementations/3.2/powershell-setup.md` | SCF-06 (lower priority) |

---

## Validation Plan

After all fixes:

1. `mkdocs build --strict` — verify no broken links from documentation changes
2. PowerShell syntax check: `pwsh -c "& { . ./scripts/Test-PolicyCompliance.ps1 -? }" 2>&1` — verify script parses
3. Module manifest validity: `pwsh -c "Test-ModuleManifest ./scripts/conditional-access-automation.psd1"` — verify manifest loads
4. Grep verification:
   - `grep -n 'SkuId -match' docs/playbooks/control-implementations/4.7/` → 0 results
   - `grep -n '\-Solution ' maintainers-local/solutions-staging/cross-solution-integration/` → 0 results (only `-SolutionId`)
   - `grep -n 'PSEUDOCODE\|CONCEPTUAL' docs/playbooks/advanced-implementations/agent-blueprint-promotion-gates/` → multiple results
