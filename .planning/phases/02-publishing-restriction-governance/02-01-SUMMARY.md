---
phase: 2
plan: 1
status: complete
started: 2026-02-12T21:00:00Z
completed: 2026-02-12T21:30:00Z
---

# Summary: Plan 02-01 — Script Core + 6 Publishing Criteria Validation

## Status: Complete

## What Was Built

Created `scripts/governance/restrict-agent-publishing.ps1` (836 lines) — a governance script that validates 6 agent publishing restriction criteria with zone-based logic and SHA-256 evidence export. The script was previously listed in the governance README as a phantom reference (file did not exist). It now follows established conventions from `Test-AgentAuthConfiguration.ps1` and `Invoke-HardeningBaselineCheck.ps1`.

The script checks:
- **Criterion 1** — Environment Maker Role Removal (per-environment, `Get-AdminPowerAppEnvironmentRoleAssignment`)
- **Criterion 2** — Authorized Security Groups (per-environment, with optional Graph API name resolution)
- **Criterion 3** — Share with Everyone Disabled (tenant-level, `Get-TenantSettings` with fallback path)
- **Criterion 4** — DLP Connector Blocking (semi-automated, `Get-AdminDlpPolicy`)
- **Criterion 5** — Managed Environment Sharing Limits (per-environment, `governanceConfiguration`)
- **Criterion 6** — Approval Workflow Active (semi-automated, `Get-AdminFlow` + governance config)

Zone-based logic: Zone 1 = Warning/advisory, Zone 2 = moderate enforcement (sharing ≤20), Zone 3 = strict enforcement (sharing ≤5).

## Tasks Completed

- [x] **Task 1: Script Scaffolding and Parameters** — Comment-based help (.SYNOPSIS, .DESCRIPTION, .PARAMETER, .EXAMPLE ×3, .OUTPUTS, .NOTES), `#Requires` directives, standard parameter block, cyan banner, WhatIf support
- [x] **Task 2: Helper Functions** — `Get-EnvironmentZone` (identical pattern), `New-PublishingCheckResult` with all 10 fields (CriterionNumber, Setting, CheckGroup, Status, Expected, Actual, Environment, Zone, Message, EvidenceHash)
- [x] **Task 3: Criterion 3 — Share with Everyone** — Tenant-level check with primary/fallback property paths, zone-aware status (Warning for Zone 1, Fail for Zone 2/3), try/catch with Skip on API failure
- [x] **Task 4: Per-Environment Checks — Criteria 1, 2, 5** — Environment enumeration with filter, Criterion 1 (broad principal detection), Criterion 2 (security group with Graph API resolution), Criterion 5 (Managed Environment + sharing limits with zone thresholds)
- [x] **Task 5: DLP Policy Check — Criterion 4** — DLP policy enumeration, connector blocking detection, semi-automated with Zone 1 auto-pass
- [x] **Task 6: Approval Workflow Check — Criterion 6** — Maker onboarding config + flow enumeration with naming patterns, Zone 1 auto-pass, semi-automated qualifier
- [x] **Task 7: Results Aggregation and Console Output** — Standard results PSCustomObject (Metadata/Summary/Checks/Gaps), SHA-256 evidence hash, console summary banner, JSON/Table/Object output switch with parent directory creation

## Commits

| Hash | Message |
|------|---------|
| `759e95b` | feat(phase-2): create restrict-agent-publishing.ps1 governance script |

## Files Created/Modified

| Action | File | Lines |
|--------|------|-------|
| Created | `scripts/governance/restrict-agent-publishing.ps1` | 836 |

## Validation Results

- **Parse check**: PowerShell parser reports zero errors
- **Help check**: `Get-Help -Full` renders complete documentation (synopsis, description, 3 examples, all parameters, outputs, notes)

## Decisions Made

- Script is 836 lines (slightly above the 500–700 estimate) due to thorough error handling per check group with individual try/catch blocks, detailed zone-based switch statements, and comprehensive inline documentation
- Criterion 3 (Share with Everyone) evaluates once per zone represented in the zone mapping, emitting per-zone results rather than a single tenant-wide result, to provide zone-specific status context
- DLP check (Criterion 4) and Approval Workflow check (Criterion 6) both include "Semi-automated" qualifiers in result messages per the plan's guidance
- No `$BaselinePath` / drift detection parameter — plan did not specify it (unlike `Test-AgentAuthConfiguration.ps1`)

## Discovered Work

- The governance README (`scripts/governance/README.md`) references other phantom scripts (`configure-managed-environment.ps1`, `setup-sod-groups.ps1`, `enable-dlp-policies.ps1`) that also do not exist — these could be addressed in future phases
- Plan 02-02 (README update + documentation alignment) is the next step in Phase 2
