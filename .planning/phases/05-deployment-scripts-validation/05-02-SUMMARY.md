---
phase: 05-deployment-scripts-validation
plan: 02
subsystem: infra
tags: [powershell, azure-cli, arm-templates, alerts, action-groups, logic-app, deployment-automation]

# Dependency graph
requires:
  - phase: 03-azure-monitor-workbooks-alert-rules
    provides: Alert rule ARM templates (ALRT-01, ALRT-02, ALRT-03), Action Group templates, Logic App template
provides:
  - deploy-alerts.ps1 PowerShell script with 3-phase dependency-ordered deployment
  - Idempotent alert infrastructure deployment automation
  - Prerequisites validation and error handling with troubleshooting guidance
affects: [05-03-validation-checklist, deployment-automation]

# Tech tracking
tech-stack:
  added: [PowerShell 7.0, Azure CLI 2.60.0+]
  patterns: [3-phase dependency sequencing, callback URL propagation, resource ID chaining, DryRun preview mode]

key-files:
  created: [agent-observability-foundation/scripts/deploy-alerts.ps1]
  modified: []

key-decisions:
  - "3-phase deployment order enforced: Logic App → Action Groups → Alert Rules"
  - "Callback URL captured from Logic App outputs and passed to Action Groups"
  - "Action Group IDs captured from Phase 2 outputs and passed to Alert Rules"
  - "Prerequisites validation checks ARM template file existence"
  - "DryRun mode for safe preview without resource deployment"
  - "Confirmation prompt required unless -Force (production safety)"
  - "Shared parameters file provides environment-specific values with override capability"
  - "Comprehensive error handling with troubleshooting guidance per phase"

patterns-established:
  - "Phase deployment functions return hashtables with resource IDs/URLs for next phase"
  - "LASTEXITCODE checks after every az command for error detection"
  - "PSScriptRoot-relative path resolution for cross-platform compatibility"
  - "Deployment summary includes next steps (Teams config, baseline wait period)"

# Metrics
duration: 2min
completed: 2026-02-06
---

# Phase 5 Plan 02: Alert Deployment Script Summary

**PowerShell 7 deployment script with 3-phase dependency-ordered alert infrastructure deployment (Logic App → Action Groups → Alert Rules) and comprehensive error handling**

## Performance

- **Duration:** 2 min
- **Started:** 2026-02-06T02:51:35Z
- **Completed:** 2026-02-06T02:53:51Z
- **Tasks:** 1
- **Files created:** 1

## Accomplishments
- deploy-alerts.ps1 script enforces correct deployment order (Logic App → Action Groups → Alert Rules)
- Logic App callback URL captured from deployment outputs and propagated to Action Groups
- Action Group IDs captured and propagated to Alert Rules
- Prerequisites validation checks Azure CLI, authentication, resource group, Application Insights, and template files
- DryRun mode for safe preview without resource deployment
- Confirmation prompt protects production environments (skippable with -Force)
- Comprehensive error handling with troubleshooting guidance per phase
- Deployment summary includes next steps (Teams channel configuration, 10-14 day baseline wait period)

## Task Commits

Each task was committed atomically:

1. **Task 1: Create deploy-alerts.ps1 with 3-phase dependency-ordered deployment** - `b96df45` (feat)

## Files Created/Modified
- `agent-observability-foundation/scripts/deploy-alerts.ps1` (684 lines) - PowerShell script that deploys alert infrastructure in 3 phases with dependency sequencing, prerequisites validation, DryRun mode, and comprehensive error handling

## Decisions Made
- **3-phase deployment order:** Logic App must deploy first to obtain callback URL, Action Groups second to obtain resource IDs, Alert Rules third to reference Action Groups
- **Callback URL propagation:** Logic App outputs captured via `az deployment group show` and passed to Action Groups via parameter override
- **Action Group ID propagation:** Action Group resource IDs captured from deployment outputs and passed to Alert Rules
- **Prerequisites validation:** Checks ARM template file existence before deployment to fail fast with clear error messages
- **DryRun mode:** Allows users to preview deployment without making changes (prints intended actions)
- **Confirmation prompt:** Requires user to type "yes" before production deployment unless -Force flag provided
- **Shared parameters override:** Script accepts shared-parameters.$Environment.json but overrides dynamic values (Logic App URL, Action Group IDs)
- **Error handling per phase:** Each deployment function has try-catch with troubleshooting guidance specific to that phase
- **Deployment summary:** Shows resource inventory (1 Logic App, 3 Action Groups, 9 Alert Rules) and next steps

## Deviations from Plan

None - plan executed exactly as written

## Issues Encountered

None

## User Setup Required

None - no external service configuration required. Script handles all Azure resource deployment.

## Next Phase Readiness

Ready for Phase 5 Plan 03 (Validation Checklist). deploy-alerts.ps1 is complete and ready for manual testing validation.

**Key context for next phase:**
- Script requires Azure CLI 2.60.0+ and authenticated session
- Script validates prerequisites before deployment (resource group, App Insights, template files)
- DryRun mode available for safe preview: `.\deploy-alerts.ps1 -ResourceGroup "..." -ApplicationInsightsId "..." -DryRun`
- Confirmation prompt protects production: user must type "yes" or pass -Force flag
- Dynamic thresholds require 10-14 days baseline before alerts fire (Learning period)
- Teams channel IDs must be configured manually in Logic App after deployment

---
*Phase: 05-deployment-scripts-validation*
*Completed: 2026-02-06*

## Self-Check: PASSED

All files exist:
- agent-observability-foundation/scripts/deploy-alerts.ps1

All commits exist:
- b96df45
