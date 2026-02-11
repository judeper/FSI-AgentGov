---
phase: 2
plan: 2
status: complete
started: 2026-02-11
completed: 2026-02-11
---

# Summary: Plan 02-02 — PowerShell Hardening Baseline Verification Script

## Status: Complete

## Tasks Completed

1. **Script Created** — `scripts/governance/Invoke-HardeningBaselineCheck.ps1` (459 lines) with comment-based help, parameter block, banner, WhatIf support
2. **Check Group 1 (Tenant Settings)** — Items 14-16 via `Get-TenantSettings` (environment creation restriction, routing, tenant isolation)
3. **Check Group 2 (Environment Settings)** — Items 7-8, 17 per-environment with zone-specific thresholds via Dataverse REST API and `Get-AdminPowerAppEnvironment`
4. **Check Group 3 (Tenant Auditing)** — Item 9 via default environment Dataverse Organization entity query
5. **Output and Evidence** — Table/JSON/Object output with SHA-256 evidence hash computation via `-IncludeEvidence` switch
6. **README Updated** — Added `Invoke-HardeningBaselineCheck.ps1` to governance scripts table, renamed "Planned Scripts" to "Scripts", removed "Coming in a future release" note
7. **Validation** — Script parses without syntax errors; runs with graceful skip when Power Platform modules not available

## Files Modified

| File | Action | Description |
|------|--------|-------------|
| `scripts/governance/Invoke-HardeningBaselineCheck.ps1` | Created | PowerShell verification script (459 lines, 7 checks across 3 check groups) |
| `scripts/governance/README.md` | Modified | Added script entry to scripts table, updated heading |

## Decisions Made

- No deviations from plan; all task specifications applied as specified
- Helper functions `Get-EnvironmentZone` and `New-CheckResult` defined inline (not in separate module) following the self-contained script pattern

## Requirements Delivered

- HBL-02: PowerShell hardening baseline verification script validating items 7-9 (audit logging) and 14-17 (environment provisioning) with pass/fail output and evidence export
