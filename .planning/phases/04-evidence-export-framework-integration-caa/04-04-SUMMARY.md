# Plan 04-04 Summary: Compliance Dashboard Feed Integration

**Phase:** 04 — Evidence Export & Framework Integration (CAA)
**Plan:** 04-04
**Status:** Complete
**Executed:** 2026-02-10

## Objective

Extended the v9 cross-solution integration infrastructure to include CAA as the 6th solution, feeding automated Control 1.11 (primary), 1.23, and 1.18 (secondary) assessment scores to the Compliance Dashboard.

## Tasks Completed

### Task 1: Add CAA to IntegrationConfig.psm1
**File:** `C:/dev/FSI-AgentGov-Solutions/cross-solution-integration/scripts/powershell/IntegrationConfig.psm1`
**Commit:** `150a39f`

Changes:
- `Get-SolutionControlMapping`: Added `'CAA' = @('1.11', '1.23', '1.18')`
- `Get-SolutionTableConfig`: Added CAA entry with `fsi_capolicyvalidationhistories`, Choice-based severity, v1.1.0
- `ConvertTo-DashboardStatus`: Added 'CAA' to ValidateSet; updated switch from `'ACV', 'SSC'` to `'ACV', 'SSC', 'CAA'`
- `Get-EvidenceExportScripts`: Added `'CAA' = 'Export-CAAComplianceEvidence.ps1'`
- `Get-SolutionDirectories`: Added `'CAA' = 'conditional-access-automation'`
- Header comment updated from 5 to 6 solutions

### Task 2: Add CAA handling to Sync-SolutionAssessments.ps1
**File:** `C:/dev/FSI-AgentGov-Solutions/cross-solution-integration/scripts/powershell/Sync-SolutionAssessments.ps1`
**Commit:** `03a81ff`

Changes:
- `-Solutions` ValidateSet expanded to include 'CAA'
- Default value expanded to include 'CAA' (6 solutions)
- Header updated to reference 6 solutions
- Added worst-of-two resolution region after main sync loop:
  - Compares SSC and CAA assessments for Control 1.11
  - Uses highest (worst) status value when they differ
  - Updates existing same-day assessment with resolved status
  - Supports DryRun mode
  - Logs alignment when both solutions agree

### Task 3: Update cd-solution-feed-collector.json flow
**File:** `C:/dev/FSI-AgentGov-Solutions/cross-solution-integration/flows/cd-solution-feed-collector.json`
**Commit:** `dde4235`

Changes:
- Added `Sync_CAA` scope with 3 upsert actions (Controls 1.11, 1.23, 1.18)
- Query: `fsi_capolicyvalidationhistories`, ordered by `fsi_timestamp desc`, `$top: 1`
- Status mapping: severity 1 → status 1, severity 2/3 → status 2, severity 4/5 → status 3
- `runAfter`: `Sync_AAM` succeeded/failed
- `Send_Summary_Teams` wired to run after `Sync_CAA` instead of `Sync_AAM`
- Teams summary message updated to include CAA
- Flow description and metadata updated (version → 1.1.0, mentions 6 solutions)

### Task 4: Update STATUS_MAPPING.md
**File:** `C:/dev/FSI-AgentGov-Solutions/cross-solution-integration/docs/STATUS_MAPPING.md`
**Commit:** `77e220d`

Changes:
- Added 3 CAA rows to Solution-to-Control Mapping table (Controls 1.11, 1.23, 1.18)
- Updated total from "5 solutions → 7 control assessments" to "6 solutions → 10 control assessments"
- Added full CAA section with severity-to-dashboard translation table
- Documented control mapping with primary/secondary roles
- Documented dual-feed resolution logic for Control 1.11 (worst-of-two)
- Version bumped to v1.1.0

## Verification

- IntegrationConfig.psm1: 0 parse errors, all functions return correct CAA values
- Sync-SolutionAssessments.ps1: 0 parse errors
- cd-solution-feed-collector.json: valid JSON
- STATUS_MAPPING.md: complete with all sections

## Commits

| # | Hash | Description |
|---|------|-------------|
| 1 | `150a39f` | feat(INT): add CAA as 6th solution in IntegrationConfig.psm1 |
| 2 | `03a81ff` | feat(INT): add CAA to Sync-SolutionAssessments with worst-of-two logic |
| 3 | `dde4235` | feat(INT): add Sync_CAA scope to CD-SolutionFeedCollector flow |
| 4 | `77e220d` | docs(INT): add CAA status mapping and dual-feed documentation |

## Decisions

- CAA uses the same Choice-based severity (1-5) pattern as ACV and SSC, sharing the same switch branch in `ConvertTo-DashboardStatus`
- Worst-of-two resolution for Control 1.11 compares status labels (Compliant=1, Partial=2, Non-Compliant=3) and takes the maximum, then updates the existing same-day assessment record in Dataverse
- Flow `Sync_CAA` creates 3 separate upsert actions (one per control) rather than a loop, matching the explicit pattern used by other solutions in the flow template

## Discovered Work

None — all tasks completed as specified.
