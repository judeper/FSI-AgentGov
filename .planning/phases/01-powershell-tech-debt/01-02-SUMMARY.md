---
phase: 01-powershell-tech-debt
plan: 02
subsystem: quality
tags: [powershell, requires-statements, deny-event-correlation, pipeline-governance]

requires:
  - phase: none
    provides: "Independent of other plans"
provides:
  - "#Requires declarations for 6 scripts across 2 solutions"
  - "Module dependency validation for ExchangeOnlineManagement, Az.Storage, Az.KeyVault, Az.Accounts, Microsoft.Graph.Users.Actions"
affects: [01-04-validation]

tech-stack:
  added: []
  patterns:
    - "#Requires -Version 7.0 after param block closing"
    - "#Requires -Modules matching actual cmdlet usage"

key-files:
  created: []
  modified:
    - "deny-event-correlation-report/scripts/Export-CopilotDenyEvents.ps1"
    - "deny-event-correlation-report/scripts/Export-DlpCopilotEvents.ps1"
    - "deny-event-correlation-report/scripts/Invoke-DailyDenyReport.ps1"
    - "deny-event-correlation-report/scripts/Export-RaiTelemetry.ps1"
    - "pipeline-governance-cleanup/src/Get-PipelineInventory.ps1"
    - "pipeline-governance-cleanup/src/Send-OwnerNotifications.ps1"

key-decisions:
  - "Get-PipelineInventory.ps1 gets only -Version (uses pac CLI, not PS modules)"
  - "Module declarations match actual cmdlet imports per script"

completed: 2026-02-04
---

# Phase 1 Plan 02: Add #Requires to Deny-Event-Correlation and Pipeline-Governance Scripts Summary

**Added #Requires -Version 7.0 and module declarations to 6 PowerShell scripts across deny-event-correlation-report and pipeline-governance-cleanup solutions**

## Performance

- **Tasks:** 2/2
- **Files modified:** 6

## Accomplishments
- All 4 deny-event-correlation-report scripts have `#Requires -Version 7.0` and appropriate `-Modules` statements
- Both pipeline-governance-cleanup scripts have `#Requires -Version 7.0`
- Module mappings: ExchangeOnlineManagement (audit log scripts), Az.Accounts (RAI telemetry), Az.Storage + Az.KeyVault (orchestrator), Microsoft.Graph.Users.Actions (notifications)
- Get-PipelineInventory.ps1 correctly omits -Modules (uses pac CLI)

## Task Commits

1. **Task 1: Add #Requires to deny-event-correlation scripts** - `6ea0ab6` (chore)
2. **Task 2: Add #Requires to pipeline-governance scripts** - `79c5576` (chore)

## Files Created/Modified
- `deny-event-correlation-report/scripts/Export-CopilotDenyEvents.ps1` - #Requires -Version 7.0, -Modules ExchangeOnlineManagement
- `deny-event-correlation-report/scripts/Export-DlpCopilotEvents.ps1` - #Requires -Version 7.0, -Modules ExchangeOnlineManagement
- `deny-event-correlation-report/scripts/Invoke-DailyDenyReport.ps1` - #Requires -Version 7.0, -Modules ExchangeOnlineManagement, Az.Storage, Az.KeyVault
- `deny-event-correlation-report/scripts/Export-RaiTelemetry.ps1` - #Requires -Version 7.0, -Modules Az.Accounts
- `pipeline-governance-cleanup/src/Get-PipelineInventory.ps1` - #Requires -Version 7.0
- `pipeline-governance-cleanup/src/Send-OwnerNotifications.ps1` - #Requires -Version 7.0, -Modules Microsoft.Graph.Users.Actions

## Decisions Made
- Get-PipelineInventory.ps1 gets only version requirement — uses pac CLI (external tool), not PowerShell modules
- Module declarations precisely match actual cmdlet usage per script (no over-declaring)

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- 6 of 11 DEBT-03 scripts complete
- Remaining 5 scripts covered by Plan 01-03
- Ready for Plan 01-04 validation scan

---
*Phase: 01-powershell-tech-debt*
*Completed: 2026-02-04*
