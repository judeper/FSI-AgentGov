# Plan 01-02 Summary: Get-AgentModerationSettings.ps1 and Compare-ModerationCompliance.ps1

**Status:** Complete
**Wave:** 2
**Started:** 2026-02-09T12:00:00Z
**Completed:** 2026-02-09T12:30:00Z

## Commits

- `204f722` — feat(cmm): implement Get-AgentModerationSettings and Compare-ModerationCompliance

## Files Created/Modified

- `content-moderation-monitor/scripts/Get-AgentModerationSettings.ps1` — Full implementation replacing stub (13.1 KB, ~290 lines)
- `content-moderation-monitor/scripts/Compare-ModerationCompliance.ps1` — Full implementation replacing stub (7.0 KB, ~170 lines)

## Implementation Details

### Get-AgentModerationSettings.ps1

Script-level function that enumerates Copilot Studio agents across Power Platform environments:

- **Parameters:** IncludeEnvironments, ExcludeEnvironments, ExcludeSandbox, ExcludeTrial, ExcludeDefault, GracePeriodHours (48), IncludeDrafts, DataverseUrl, Top (0)
- **Helper imports:** Dot-sources `Test-ParameterValidation.ps1`, imports `CMMClient.psm1`, calls `Connect-EnvironmentDataverse.ps1` and `Get-ZoneClassification.ps1` via `&` operator
- **Flow:** Get-AdminPowerAppEnvironment → filter (type/grace/include/exclude) → filter to Dataverse-enabled → per-environment: connect, query bots, extract moderation level, classify zone → emit PSCustomObject per agent
- **Resilience:** Failed environment connections emit Write-Warning and continue; Write-Progress for multi-environment scans
- **Top cap:** Uses `$topReached` flag to break both inner and outer loops cleanly
- **Output schema:** AgentId, AgentName, AgentStatus, ContentModerationLevel, EnvironmentId, EnvironmentDisplayName, EnvironmentType, Zone, DataverseUrl, LastPublished, RetrievedAt

### Compare-ModerationCompliance.ps1

Pipeline-enabled function with begin/process/end pattern:

- **Parameters:** AgentSettings (pipeline, mandatory), BaselinePath, IncludeCompliant
- **begin:** Loads moderation-baseline.json, validates JSON, initializes counters
- **process:** For each agent: normalizes Zone/Level defensively, calls `Get-ExpectedModerationLevel.ps1` with try/catch, builds compliance result, emits if violation or IncludeCompliant
- **end:** Write-Verbose summary (total, compliant, violations by severity)
- **Defensive:** Null/empty Zone → 'Unknown', null/empty ContentModerationLevel → 'Unknown', failed evaluation → Warning severity with error message as RegulatoryContext
- **Output schema:** AgentId, AgentName, EnvironmentDisplayName, Zone, CurrentModerationLevel, ExpectedModerationLevel, IsCompliant, Severity, RegulatoryContext, AgentStatus

## Decisions Made

- Used `Test-EnvironmentPassesFilter` (distinct name) for the local per-environment filter function to avoid shadowing the imported `Test-EnvironmentFilter` parameter validation function from `Test-ParameterValidation.ps1`
- ELM Dataverse token acquired once at the start of the scan (not per-environment) for efficiency; if ELM connection fails, falls back to naming convention with a warning
- Used `[System.Collections.Generic.List[PSCustomObject]]` instead of `@()` array concatenation for results collection (better performance for large tenants)
- Added defensive input normalization in Compare-ModerationCompliance to handle edge cases where upstream data might have null/empty Zone or ContentModerationLevel values
- Passes `$resolvedPath` to `Get-ExpectedModerationLevel.ps1` as `-BaselinePath` so the baseline JSON is loaded only once (path resolution) in the begin block rather than re-discovered per agent

## Self-Check

- [x] All files in manifest exist
- [x] All commits present (204f722)
- [x] PowerShell syntax validates (no parse errors for both scripts)
- [x] Comment-based help with SYNOPSIS, DESCRIPTION, PARAMETER, EXAMPLE, OUTPUTS, NOTES
- [x] FSI language rules followed (no "ensures compliance", "guarantees", etc.)
- [x] Pipeline support in Compare-ModerationCompliance (ValueFromPipeline + begin/process/end)
- [x] Resilient error handling (Write-Warning + continue for failed environments)
- [x] Progress reporting (Write-Progress in Get-AgentModerationSettings)
- [x] Follows AAM pattern (Get-EnvironmentAccessSettings / Compare-ZoneCompliance)
