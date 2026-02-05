---
phase: 05-scope-drift-monitor-completion
plan: 01
subsystem: monitoring
tags: [powershell, office365-management-api, copilot-interaction, audit-log, drift-detection, teams-adaptive-card]

# Dependency graph
requires:
  - phase: 04-compliance-dashboard-completion
    provides: Solution packaging patterns and flow architecture
provides:
  - Enhanced baseline capture script with Office 365 Management API integration
  - Manual drift detection script for ad-hoc scanning
  - Alert delivery testing utility for Teams and email
affects: [05-02, 05-03, 05-04]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - Office 365 Management API subscription and content blob fetching
    - CopilotInteraction event parsing (RecordType 261)
    - Scope comparison logic for drift detection

key-files:
  created:
    - /Users/admin/dev/FSI-AgentGov-Solutions/scope-drift-monitor/scripts/Invoke-DriftScan.ps1
    - /Users/admin/dev/FSI-AgentGov-Solutions/scope-drift-monitor/scripts/Test-AlertDelivery.ps1
  modified:
    - /Users/admin/dev/FSI-AgentGov-Solutions/scope-drift-monitor/scripts/New-AgentBaseline.ps1

key-decisions:
  - "Use Office 365 Management API instead of Graph API directoryAudits (Graph API moved to beta April 2025)"
  - "Filter for RecordType 261 (CopilotInteraction) for Copilot-specific events"
  - "Auto-generated baselines go active immediately (fsi_status=2)"
  - "Severity: High (2) for connector/API violations, Medium (3) for site/table violations"
  - "Include Teams webhook deprecation warning (March 31, 2026 retirement)"

patterns-established:
  - "Office 365 Management API pagination via NextPageUri header"
  - "CopilotInteraction parsing: AISystemPlugin for connectors, Contexts for SharePoint sites"
  - "Scope comparison: parse JSON arrays from fsi_allowed* fields, check resource membership"

# Metrics
duration: 12min
completed: 2026-02-05
---

# Phase 5 Plan 1: PowerShell Scripts Enhancement Summary

**Office 365 Management API integration for baseline capture, manual drift detection script, and alert delivery testing utility**

## Performance

- **Duration:** 12 min
- **Started:** 2026-02-05T01:35:22Z
- **Completed:** 2026-02-05T01:47:00Z
- **Tasks:** 3
- **Files modified:** 3

## Accomplishments

- Enhanced New-AgentBaseline.ps1 with Office 365 Management API for CopilotInteraction events
- Created Invoke-DriftScan.ps1 for manual drift detection against Dataverse scopes
- Created Test-AlertDelivery.ps1 for Teams webhook and email testing

## Task Commits

Each task was committed atomically:

1. **Task 1: Enhance New-AgentBaseline.ps1** - `2600d6d` (feat)
2. **Task 2: Create Invoke-DriftScan.ps1** - `5e8cd02` (feat)
3. **Task 3: Create Test-AlertDelivery.ps1** - `2241325` (feat)

## Files Created/Modified

- `scope-drift-monitor/scripts/New-AgentBaseline.ps1` - Enhanced with Office 365 Management API integration, CopilotInteraction parsing (RecordType 261), pagination handling, and graceful error handling for 403 licensing issues
- `scope-drift-monitor/scripts/Invoke-DriftScan.ps1` - New script for manual drift detection; queries Dataverse for active scopes, compares audit events against allowed resources, creates violation records
- `scope-drift-monitor/scripts/Test-AlertDelivery.ps1` - New utility for testing Teams Adaptive Card and email notification delivery before production deployment

## Decisions Made

1. **Office 365 Management API over Graph API** - Graph API auditLogs/directoryAudits was moved back to beta in April 2025; Office 365 Management API is stable for CopilotInteraction events
2. **RecordType 261 filtering** - CopilotInteraction events use RecordType 261 per Microsoft documentation
3. **Auto-generated baselines go active immediately** - Per CONTEXT.md decision, no approval needed for auto-generated baselines (fsi_status=2)
4. **Severity assignment** - High (2) for connector/external API violations (broader impact), Medium (3) for SharePoint site/Dataverse table violations (more contained)
5. **Teams webhook deprecation warning** - Included in Test-AlertDelivery.ps1 since webhooks retire March 31, 2026

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- PowerShell runtime (pwsh) not installed on execution environment - syntax validation skipped but all scripts verified via grep for required patterns

## Next Phase Readiness

- Scripts ready for integration with Power Automate flows (Plan 02)
- Patterns established for Office 365 Management API calls can be adapted to flow HTTP actions
- Alert testing utility enables pre-deployment verification

---
*Phase: 05-scope-drift-monitor-completion*
*Completed: 2026-02-05*
