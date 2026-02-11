# Summary: Plan 05-01 — PowerShell & Script Bugs

**Status:** Complete

## Requirements Delivered

| Req | Description | Status |
|-----|-------------|--------|
| SCF-01 | `$isBlock` scoped correctly + `$totalGaps`/`$driftCount` ordering fixed | Done |
| SCF-02 | Module manifest exports only existing functions | Done |
| SCF-03 | 4.7 SKU filter uses `SkuPartNumber` | Done |
| SCF-04 | Non-existent cmdlets annotated as pseudocode | Done |

## Tasks Completed

1. **Fix `$isBlock` variable scoping in Test-PolicyCompliance.ps1** — Added `$isBlock` recalculation inside Check 5's foreach loop so each policy gets its own value from `$policy.GrantControls.BuiltInControls`. Moved `$totalGaps`/`$driftCount` computation from the Summary section to before the Dataverse persistence block, so these variables are defined when first consumed.

2. **Fix module manifest FunctionsToExport** — Replaced the 5-function export list with an empty `@()` array, since none of the listed functions exist as module functions. Added comments documenting the planned functions for future reference.

3. **Fix 4.7 PowerShell SKU filter** — Replaced the broken `$_.SkuId -match "copilot"` pattern (GUID field never contains "copilot") with a two-step approach: first resolve Copilot SKU IDs via `Get-MgSubscribedSku` filtering on `SkuPartNumber`, then filter users whose `AssignedLicenses.SkuId` is in the resolved set.

4. **Annotate non-existent cmdlets in promotion gates** — Added `# PSEUDOCODE` inline comments on all 9 non-existent cmdlet references across both `implementation-guide.md` and `index.md`. Added MkDocs `!!! warning` admonitions before each PowerShell code block containing pseudocode cmdlets (4 admonitions total: Security Scan Automation, DLP Compliance Check, Escalation Flow in implementation-guide.md, and Quick Start in index.md).

## Commits Made

| Hash | Message |
|------|---------|
| `599ce8c` | `fix(scripts): fix $isBlock scoping, $totalGaps ordering, and manifest exports (SCF-01, SCF-02)` |
| `016997c` | `fix(docs): use SkuPartNumber instead of SkuId for Copilot license filter (SCF-03)` |
| `8e185e8` | `docs(playbooks): annotate non-existent cmdlets as pseudocode in promotion gates (SCF-04)` |

## Files Modified

- `scripts/Test-PolicyCompliance.ps1` — `$isBlock` recalculation in Check 5; `$totalGaps`/`$driftCount` moved before Dataverse block
- `scripts/conditional-access-automation.psd1` — `FunctionsToExport` set to `@()` with explanatory comments
- `docs/playbooks/control-implementations/4.7/powershell-setup.md` — SKU filter rewritten to use `SkuPartNumber`
- `docs/playbooks/advanced-implementations/agent-blueprint-promotion-gates/implementation-guide.md` — 8 pseudocode annotations + 3 warning admonitions
- `docs/playbooks/advanced-implementations/agent-blueprint-promotion-gates/index.md` — 2 pseudocode annotations + 1 warning admonition

## Decisions Made

- **Module manifest validation:** `Test-ModuleManifest` reports a pre-existing error about missing `RequiredModules` (Graph modules not installed in the dev environment). This is not caused by our change — `Import-PowerShellDataFile` confirms `FunctionsToExport` is correctly empty.
- **YAML code block in implementation-guide.md:** Added inline `# PSEUDOCODE` comment to the `Invoke-SecurityScan` call within the DevOps pipeline YAML, but did not add a full MkDocs warning admonition before the YAML block since it is not a standalone PowerShell code block.
- **`Test-DlpPolicyCompliance`** is a locally-defined function within the pseudocode section, not a non-existent module cmdlet, so it was not annotated.

## Discovered Work

- None — all four requirements were addressed cleanly.

## Validation Results

- **PowerShell parse check:** `PASS: No parse errors` (Parser::ParseFile on Test-PolicyCompliance.ps1)
- **Module manifest data:** `FunctionsToExport count: 0`
- **mkdocs build --strict:** Passed — documentation built in ~65s with no errors (only pre-existing INFO messages about excluded file links)
