---
phase: 01-powershell-tech-debt
plan: 03
subsystem: quality
tags: [powershell, requires-statements, python, dependencies, segregation-detector, scope-drift, rag-validator, dr-testing, finra]

requires:
  - phase: none
    provides: "Independent of other plans"
provides:
  - "#Requires -Version 7.0 for remaining 5 PowerShell scripts"
  - "Clean FINRA requirements.txt with only stdlib documentation"
affects: [01-04-validation]

tech-stack:
  added: []
  patterns:
    - "REST API scripts get only -Version (no -Modules needed)"

key-files:
  created: []
  modified:
    - "segregation-detector/scripts/Invoke-SoDScan.ps1"
    - "segregation-detector/scripts/Import-ConflictRules.ps1"
    - "scope-drift-monitor/scripts/New-AgentBaseline.ps1"
    - "rag-source-validator/scripts/Invoke-SourceValidation.ps1"
    - "dr-testing-framework/scripts/Invoke-DRTest.ps1"
    - "finra-supervision-workflow/scripts/requirements.txt"

key-decisions:
  - "All 5 scripts use Invoke-RestMethod directly — no #Requires -Modules needed"
  - "FINRA requirements.txt replaced with stdlib-only documentation comments"

completed: 2026-02-04
---

# Phase 1 Plan 03: Add #Requires to Remaining Scripts and Clean FINRA Dependencies Summary

**Added #Requires -Version 7.0 to 5 remaining PowerShell scripts and removed 6 unused third-party dependencies from FINRA requirements.txt**

## Performance

- **Tasks:** 2/2
- **Files modified:** 6

## Accomplishments
- All 5 remaining PowerShell scripts have `#Requires -Version 7.0`
- Correctly omitted `-Modules` for all 5 (they use `Invoke-RestMethod` directly)
- Removed 6 unused packages from FINRA requirements.txt: msal, azure-identity, requests, pandas, tabulate, python-dotenv
- ELM requirements.txt confirmed unchanged (all 4 dependencies actively used)
- DEBT-03 now complete: all 11 scripts have #Requires statements
- DEBT-04 complete: no unused dependencies remain

## Task Commits

1. **Task 1: Add #Requires to 5 remaining scripts** - `a31fed2` (chore)
2. **Task 2: Clean FINRA requirements.txt** - `8f6f3fe` (chore)

## Files Created/Modified
- `segregation-detector/scripts/Invoke-SoDScan.ps1` - #Requires -Version 7.0
- `segregation-detector/scripts/Import-ConflictRules.ps1` - #Requires -Version 7.0
- `scope-drift-monitor/scripts/New-AgentBaseline.ps1` - #Requires -Version 7.0
- `rag-source-validator/scripts/Invoke-SourceValidation.ps1` - #Requires -Version 7.0
- `dr-testing-framework/scripts/Invoke-DRTest.ps1` - #Requires -Version 7.0
- `finra-supervision-workflow/scripts/requirements.txt` - Replaced with stdlib-only documentation

## Decisions Made
- All 5 scripts use Invoke-RestMethod for Graph/Dataverse — no PowerShell module dependencies to declare
- FINRA requirements.txt kept as documentation of stdlib modules used (not deleted entirely)

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- DEBT-03 fully complete (11/11 scripts)
- DEBT-04 fully complete (FINRA cleaned, ELM preserved)
- Ready for Plan 01-04 validation scan

---
*Phase: 01-powershell-tech-debt*
*Completed: 2026-02-04*
