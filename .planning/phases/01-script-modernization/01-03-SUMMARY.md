---
phase: 1
plan: 3
status: complete
started: 2026-02-10
completed: 2026-02-10
---

# Summary: Plan 01-03 — Policy Drift Detection Scripts

## Status: COMPLETE

## What Was Built

Four new PowerShell scripts implementing policy baseline capture and drift detection for Conditional Access policies, plus integration into the existing compliance checker and module manifest:

- **Get-CAAPolicyBaseline** (private helper) — Queries Graph API for CA policies matching FSI naming patterns (`CA-CopilotStudio-*`, `CA-AgentBuilder-*`, `CA-M365Copilot-*`, `CA-BlockLegacyAuth-*`, `CA-RequireCompliantDevice-*`, plus custom prefixes). Returns normalized policy objects with zone classification derived from policy name patterns, conditions, grant/session controls, and UTC snapshot timestamps. Supports `-WhatIf`, `-ConfigPath` for custom prefix override, and `-All` pagination.

- **Compare-CAAPolicyBaseline** (private helper) — Compares two baseline snapshots across 5 dimensions: state changes, condition changes (users, apps, risk levels), grant control changes (operator AND→OR weakening, MFA removal), session control changes (frequency, persistent browser), and policy additions/removals. Assigns ACV severity (1–5) with Zone 3 escalation (+1 capped at 5). Handles both hashtable and PSCustomObject property access for JSON round-trip compatibility.

- **Export-PolicyBaseline.ps1** (public orchestrator) — Connects to Graph, captures baseline via `Get-CAAPolicyBaseline`, and exports to JSON with metadata envelope (capturedAt, capturedBy from `Get-MgContext.Account`, tenantId, policyCount, schemaVersion). Supports `-WhatIf`, `-OutputFormat`, and auto-creates output directories.

- **Watch-PolicyDrift.ps1** (public orchestrator) — Loads saved baseline JSON, queries current state, compares via `Compare-CAAPolicyBaseline`, filters by `-SeverityThreshold` (Passed/Warning/GracePeriod/Failed/Error mapped to 1–5), displays Unicode box-drawing summary banner with color-coded severity counts, writes optional JSON report. Exit code 0 = no drift above threshold, 1 = drift detected.

- **Test-PolicyCompliance.ps1** — Added optional `-BaselinePath` parameter and "Check 6: Policy Drift Analysis" after existing 5 checks. When baseline provided, loads it, compares against current policies, adds drift findings to `$complianceResults.driftAnalysis` and gap entries. Drift count shown in summary output.

- **Module manifest** — Added `Watch-PolicyDrift` and `Export-PolicyBaseline` to `FunctionsToExport`.

## Commits

| Hash | Message |
|------|---------|
| `59816ad` | feat(caa): add policy baseline and drift comparison private helpers |
| `6f1bb5c` | feat(caa): add Export-PolicyBaseline orchestrator script |
| `ef5f688` | feat(caa): add Watch-PolicyDrift drift detection orchestrator |
| `84d3d93` | feat(caa): integrate drift detection into Test-PolicyCompliance and update module manifest |

## Files Created

- `scripts/private/Get-PolicyBaseline.ps1` — `Get-CAAPolicyBaseline` function (180 lines)
- `scripts/private/Compare-PolicyBaseline.ps1` — `Compare-CAAPolicyBaseline` function (507 lines)
- `scripts/Export-PolicyBaseline.ps1` — Baseline export orchestrator (182 lines)
- `scripts/Watch-PolicyDrift.ps1` — Drift detection orchestrator (300 lines)

## Files Modified

- `scripts/Test-PolicyCompliance.ps1` — Added `-BaselinePath` parameter, drift imports, Check 6 drift analysis section, drift summary in output (496 → 559 lines)
- `scripts/conditional-access-automation.psd1` — Added `Watch-PolicyDrift` and `Export-PolicyBaseline` to `FunctionsToExport`

## Decisions Made

- **Dual property access pattern**: `Compare-CAAPolicyBaseline` uses a `Get-PolicyProp` helper that handles both hashtable (`$obj[$key]`) and PSCustomObject (`$obj.$key`) access. This is necessary because baseline data round-trips through JSON serialization (hashtable → JSON → PSCustomObject on reimport).
- **Zone derivation from policy name**: Zone classification uses simple regex matching on DisplayName (`Zone1`, `Zone2`, `Zone3`, `AllZones`, fallback `Common`) rather than requiring the ELM Dataverse lookup, keeping the drift detection standalone.
- **Severity escalation model**: Zone 3 policies get +1 severity (capped at 5) matching the ACV canonical scale. This reflects the higher governance requirements for enterprise-managed environments.
- **Exit codes on Watch-PolicyDrift**: Uses `exit 1` for drift detected (above threshold) and `exit 0` for clean, enabling CI/CD pipeline integration.
- **Non-destructive drift integration**: The `-BaselinePath` parameter on `Test-PolicyCompliance.ps1` is optional — existing workflows are unaffected when not provided (verbose message suggests running `Export-PolicyBaseline.ps1`).

## Discovered Work

- None — all plan tasks completed as specified.
