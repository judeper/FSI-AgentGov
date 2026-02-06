---
phase: 05-deployment-scripts-validation
plan: 01
subsystem: deployment-automation
tags: [powershell, azure-cli, workbooks, arm-templates, idempotent-deployment]

# Dependency graph
requires:
  - phase: 03-azure-monitor-workbooks-alert-rules
    provides: 3 Azure Monitor Workbook ARM templates with dev/prod parameter files
provides:
  - PowerShell 7.0+ deployment script for all 3 workbooks (operational-health, error-diagnostics, usage-overview)
  - Prerequisite validation (Azure CLI, authentication, resource group, Application Insights)
  - Idempotent deployment with Incremental mode (fixed workbookId GUIDs prevent duplicates)
  - DryRun mode for safe preview without changes
  - Path resolution via $PSCommandPath (works from any working directory)
affects: [05-02-deploy-alerts, 05-03-validation-checklist, deployment-automation]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - PowerShell CmdletBinding with param validation (Mandatory, ValidateSet)
    - $LASTEXITCODE checks after every az CLI command (critical for error detection)
    - Path resolution via $PSCommandPath + Join-Path + Resolve-Path (no relative paths)
    - DryRun mode showing exact commands without execution
    - Color-coded terminal output with ANSI escape codes
    - Comprehensive error messages with remediation guidance

key-files:
  created:
    - agent-observability-foundation/scripts/deploy-workbooks.ps1
  modified: []

key-decisions:
  - "Use $PSCommandPath instead of $PSScriptRoot for PowerShell 7.0+ path resolution"
  - "Check $LASTEXITCODE after every az command because Azure CLI doesn't throw exceptions on failure"
  - "Use --mode Incremental (default) for safe idempotent deployment (add/update, don't delete)"
  - "Resolve paths with Join-Path + Resolve-Path to fail fast if template/parameter files missing"
  - "DryRun mode shows exact az CLI commands for transparency and debugging"
  - "Color-coded output (Cyan=info, Green=success, Red=error, Yellow=warning) for clear status"

patterns-established:
  - "PowerShell deployment script pattern: Show-Banner → Test-Prerequisites → Deploy-* functions → Summary table"
  - "Prerequisite validation pattern: Check CLI installed → Check CLI version → Check auth → Check resource existence"
  - "Idempotent deployment pattern: Fixed workbookId in parameter files + Incremental mode = safe re-runs"

# Metrics
duration: 1min 53sec
completed: 2026-02-06
---

# Phase 05 Plan 01: Workbook Deployment Script Summary

**PowerShell 7.0+ script deploys all 3 Azure Monitor Workbooks with prerequisite validation, idempotent updates, and DryRun preview**

## Performance

- **Duration:** 1 minute 53 seconds
- **Started:** 2026-02-06T02:50:50Z
- **Completed:** 2026-02-06T02:52:43Z
- **Tasks:** 1
- **Files created:** 1
- **Repository:** FSI-AgentGov-Solutions

## Accomplishments

- Created deploy-workbooks.ps1 with comprehensive prerequisite validation
- Implemented idempotent deployment using fixed workbookId GUIDs and Incremental mode
- Added DryRun mode for safe preview showing exact az CLI commands
- Established PowerShell deployment script pattern for deploy-alerts.ps1 (plan 05-02)

## Task Commits

Each task was committed atomically to FSI-AgentGov-Solutions:

1. **Task 1: Create deploy-workbooks.ps1 with prerequisite validation and workbook deployment** - `847aeb8` (feat)

**Plan metadata:** (pending - will be committed after STATE.md update)

## Files Created/Modified

**FSI-AgentGov-Solutions:**
- `agent-observability-foundation/scripts/deploy-workbooks.ps1` - PowerShell script deploying all 3 workbooks with validation, DryRun, color-coded output

## Decisions Made

**1. $PSCommandPath path resolution instead of $PSScriptRoot**
- Rationale: PowerShell 7.0+ best practice, more reliable for script invocation
- Pattern: `$scriptDir = Split-Path -Parent $PSCommandPath; Join-Path $scriptDir $relativePath | Resolve-Path`

**2. $LASTEXITCODE checks after every az CLI command**
- Rationale: Azure CLI doesn't throw PowerShell exceptions on failure - must explicitly check exit code
- Pattern: `$result = az ...; if ($LASTEXITCODE -ne 0) { ... }`

**3. Incremental deployment mode (default)**
- Rationale: Safe for idempotent updates - adds/updates resources without deleting existing ones
- Alternative: Complete mode would delete resources not in template (too dangerous)

**4. Resolve-Path with -ErrorAction Stop**
- Rationale: Fail fast if template or parameter files missing - prevents cryptic az CLI errors
- Benefit: Clear error message with exact missing file path

**5. DryRun shows exact az CLI commands**
- Rationale: Transparency for debugging, enables users to run commands manually if needed
- Pattern: Show all parameters including final `--mode Incremental` flag

**6. Color-coded output using ANSI escape codes**
- Rationale: Visual clarity for status (✓ success in green, ✗ error in red, warnings in yellow)
- Pattern: Define color constants at top, reset after each colored segment

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None - script development followed provision.py patterns successfully.

## User Setup Required

None - no external service configuration required.

Script requires:
- Azure CLI 2.50.0+ installed
- Authenticated Azure session (az login)
- Contributor or Owner role on target resource group
- Valid Application Insights resource ID

All prerequisites are validated by Test-Prerequisites function with clear error messages.

## Self-Check: PASSED

**Created files verified:**
- agent-observability-foundation/scripts/deploy-workbooks.ps1: EXISTS

**Commits verified:**
- 847aeb8: EXISTS

## Next Phase Readiness

**Ready for Plan 05-02 (deploy-alerts.ps1):**
- Deployment script pattern established and validated
- Can reuse prerequisite validation structure
- Alert rule deployment follows identical ARM template pattern

**No blockers or concerns.**

---
*Phase: 05-deployment-scripts-validation*
*Completed: 2026-02-06*
