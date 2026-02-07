---
phase: 03-automation-and-alerting
plan: 01
subsystem: session-security-configurator
tags: [powershell, azure-automation, dataverse, msal, drift-detection]

# Dependency graph
requires:
  - phase-01-plans: [01-01, 01-02, 01-03]
    provides: "Test-SessionCompliance.ps1, private helpers, zone baselines"
  - phase-02-plans: [02-01, 02-02, 02-03]
    provides: "Dataverse schema (ValidationHistory, SessionBaseline), SSC_ env vars, Get-DataverseThreshold.ps1"
provides:
  - artifact: Start-SessionValidationRunbook.ps1
    capability: "Azure Automation runbook wrapper for daily validation with drift detection"
  - artifact: Invoke-BaselineCapture.ps1
    capability: "Operator-initiated baseline snapshot to Dataverse"
affects:
  - phase-03-plans: [03-02, 03-03]
  - reason: "Power Automate flows will consume JSON output from runbook wrapper"

# Tech tracking
tech-stack:
  added: [azure-automation, dataverse-drift-detection]
  patterns: [runbook-wrapper, inline-drift-function, fail-open-on-errors, whatif-preview]

key-files:
  created:
    - session-security-configurator/scripts/Start-SessionValidationRunbook.ps1
    - session-security-configurator/scripts/Invoke-BaselineCapture.ps1
  modified: []

decisions:
  - id: INLINE-DRIFT-FUNCTION
    decision: "Implement Get-DriftStatus as inline function within runbook (not separate helper file)"
    rationale: "Drift detection is specific to runbook context and Dataverse ValidationHistory. Avoids creating SSC equivalent of ACV Compare-ValidationBaseline.ps1 since SSC has different table schema and simpler overall-only drift detection."
    alternatives: ["Create private/Compare-ValidationBaseline.ps1 helper"]
    trade-offs: "Code duplication if future scripts need drift detection vs keeping runbook self-contained"
  - id: FAIL-OPEN-DRIFT-DETECTION
    decision: "Drift detection returns DriftDetected=true on Dataverse query errors"
    rationale: "Fail open to avoid suppressing alerts when baseline query fails. Better to send false-positive alert than miss a real drift condition."
    alternatives: ["Fail closed (DriftDetected=false on errors)"]
    trade-offs: "Potential alert noise vs guaranteed alert delivery"
  - id: SINGLE-ACTIVE-BASELINE
    decision: "Only one active baseline per zone; deactivate previous before creating new"
    rationale: "Drift detection always compares against single known-good baseline. Multiple active baselines would create ambiguity."
    alternatives: ["Allow multiple active baselines with priority field"]
    trade-offs: "Simpler query logic vs flexibility for multiple baseline scenarios"
  - id: WHATIF-PREVIEW-MODE
    decision: "Invoke-BaselineCapture.ps1 supports -WhatIf for preview without writing to Dataverse"
    rationale: "Operators can verify captured settings before committing to baseline. Safe operation for critical baseline management."
    alternatives: ["Always write immediately"]
    trade-offs: "Extra parameter vs operator confidence and safety"

patterns-established:
  - "Runbook wrappers output only JSON to pipeline (no Write-Host except in WhatIf mode)"
  - "Drift detection queries fsi_validationhistories for most recent Passed (severity=1) record"
  - "AlertRequired flag = (DriftDetected OR OverallStatus != Passed) for simple Power Automate routing"
  - "Zone option set mapping: Zone1=100000001, Zone2=100000002, Zone3=100000003"
  - "Baseline capture deactivates existing active baselines via PATCH before POST"

# Metrics
duration: 2min
completed: 2026-02-07
commits: 2
files-created: 2
lines-added: 760
---

# Phase 3 Plan 1: Runbook Wrapper and Baseline Capture Summary

**Azure Automation runbook wrapper with inline drift detection against Dataverse ValidationHistory and operator-initiated baseline snapshot with single-active-per-zone management**

## Performance

- **Duration:** 2 minutes
- **Started:** 2026-02-07T00:06:03Z
- **Completed:** 2026-02-07T00:08:35Z
- **Tasks:** 2
- **Files created:** 2

## Accomplishments

- **Start-SessionValidationRunbook.ps1** — Azure Automation runbook wrapper that calls Test-SessionCompliance.ps1 with certificate-based auth, queries Dataverse ValidationHistory for drift detection, and outputs structured JSON with AlertRequired flag for Power Automate consumption
- **Invoke-BaselineCapture.ps1** — Operator-initiated baseline capture that queries live CA policies, deactivates existing active baselines for the zone, and writes new SessionBaseline record to Dataverse with WhatIf preview support
- Inline Get-DriftStatus function implements fail-open drift detection (returns DriftDetected=true on query errors to avoid suppressing alerts)

## Task Commits

Each task was committed atomically to FSI-AgentGov-Solutions repo:

1. **Task 1: Create Start-SessionValidationRunbook.ps1** - `d88875d` (feat)
2. **Task 2: Create Invoke-BaselineCapture.ps1** - `2c9da94` (feat)

## Files Created/Modified

**Created:**
- `session-security-configurator/scripts/Start-SessionValidationRunbook.ps1` (351 lines) — Azure Automation runbook wrapper with inline drift detection
- `session-security-configurator/scripts/Invoke-BaselineCapture.ps1` (409 lines) — Operator baseline capture with WhatIf mode

**Modified:** None

## Decisions Made

### 1. Inline Drift Function (INLINE-DRIFT-FUNCTION)

**Decision:** Implement Get-DriftStatus as inline function within Start-SessionValidationRunbook.ps1 rather than creating a separate private helper file.

**Rationale:**
- Drift detection is specific to runbook execution context and Dataverse ValidationHistory table
- SSC has different table schema than ACV (fsi_validationhistories vs fsi_auditvalidationhistories)
- SSC uses overall-only drift detection (simpler than ACV's per-validator drift)
- Avoids creating SSC equivalent of ACV Compare-ValidationBaseline.ps1 when logic differs significantly

**Alternatives considered:**
- Create `private/Compare-ValidationBaseline.ps1` helper (rejected: different schema, different use case)
- Reuse ACV Compare-ValidationBaseline.ps1 (rejected: wrong table names, wrong option set values)

**Trade-offs:**
- Code duplication if future scripts need drift detection vs keeping runbook self-contained
- Accepted: Drift detection is runbook-specific, unlikely to be reused elsewhere

### 2. Fail-Open Drift Detection (FAIL-OPEN-DRIFT-DETECTION)

**Decision:** When Dataverse query fails or errors occur, drift detection returns DriftDetected=true to ensure alerts fire.

**Rationale:**
- Better to send false-positive alert than miss a real drift condition
- Regulatory context (FINRA 4511, SEC 17a-4) requires tamper-proof audit trails
- If ValidationHistory is unavailable, system should assume drift and alert operators
- Consistent with ACV fail-open pattern

**Alternatives considered:**
- Fail closed (DriftDetected=false on errors) — rejected: could suppress critical alerts
- Return error status only — rejected: Power Automate would need additional error handling

**Trade-offs:**
- Potential alert noise during Dataverse outages vs guaranteed alert delivery
- Accepted: Transient failures should generate alerts for investigation

### 3. Single Active Baseline Per Zone (SINGLE-ACTIVE-BASELINE)

**Decision:** Only one active baseline allowed per zone. Invoke-BaselineCapture.ps1 deactivates existing active baselines (PATCH fsi_isactive=false) before creating new one.

**Rationale:**
- Drift detection needs single authoritative baseline to compare against
- Multiple active baselines would create ambiguity (which one to use?)
- Simpler query logic (filter on zone + isactive=true, guaranteed 0 or 1 result)
- Deactivated baselines preserved for historical audit

**Alternatives considered:**
- Allow multiple active baselines with priority field (rejected: unnecessary complexity)
- Delete previous baselines (rejected: loses audit history)

**Trade-offs:**
- Simpler implementation vs flexibility for multiple baseline scenarios
- Accepted: Single active baseline covers all current use cases

### 4. WhatIf Preview Mode (WHATIF-PREVIEW-MODE)

**Decision:** Invoke-BaselineCapture.ps1 supports -WhatIf parameter that displays preview to console without writing to Dataverse.

**Rationale:**
- Baseline capture is critical operation (sets the "known good" state for drift detection)
- Operators should be able to verify captured settings before committing
- Follows PowerShell SupportsShouldProcess pattern
- Console output acceptable in WhatIf mode (not used in automation)

**Alternatives considered:**
- Always write immediately (rejected: no safety net for operator errors)
- Confirmation prompt (rejected: not suitable for automation scenarios)

**Trade-offs:**
- Extra parameter to implement vs operator confidence and safety
- Accepted: WhatIf is standard PowerShell pattern, operators expect it

## Deviations from Plan

None — plan executed exactly as written.

## Verification Results

All verification checks passed:

1. ✅ Start-SessionValidationRunbook.ps1 exists in scripts/
2. ✅ Has #Requires for Version 7.0, Microsoft.Graph.Identity.SignIns, MSAL.PS
3. ✅ All 7 parameters: Zone, DataverseUrl, TenantId, ClientId, CertificateThumbprint, ConfigPath, SkipPimValidation
4. ✅ Dot-sources Test-SessionCompliance.ps1
5. ✅ Contains inline Get-DriftStatus function with Dataverse query to fsi_validationhistories
6. ✅ Drift detection filters for fsi_severity eq 1 (Passed records only)
7. ✅ Output object has all 9 properties: RunType, Timestamp, Zone, OverallStatus, Reason, Validators, Drift, AlertRequired, AlertSeverity
8. ✅ AlertRequired = ($drift.DriftDetected -or $validationResults.OverallStatus -ne "Passed")
9. ✅ Catch block outputs error JSON with RunType="SessionValidation" and AlertRequired=$true
10. ✅ No Write-Host in runbook wrapper (only Write-Verbose)
11. ✅ JSON output via ConvertTo-Json -Depth 10
12. ✅ Invoke-BaselineCapture.ps1 exists in scripts/
13. ✅ Has #Requires for Version 7.0, Microsoft.Graph.Identity.SignIns, MSAL.PS
14. ✅ All 7 parameters: Zone, DataverseUrl, TenantId, ClientId, CertificateThumbprint, Interactive, WhatIf
15. ✅ Connects to Microsoft Graph for CA policy queries
16. ✅ Queries Get-MgIdentityConditionalAccessPolicy for enabled policies with session controls
17. ✅ Deactivates existing active baselines (PATCH fsi_isactive=false)
18. ✅ Creates new SessionBaseline record via POST to fsi_sessionbaselines
19. ✅ Zone option set mapping: Zone1=100000001, Zone2=100000002, Zone3=100000003
20. ✅ fsi_rawjson contains full session settings JSON (ConvertTo-Json -Depth 5 -Compress)
21. ✅ WhatIf mode displays preview without writing to Dataverse
22. ✅ Output JSON includes BaselineId, Zone, CapturedOn, SignInFrequencyMinutes, AuthStrength, PoliciesCaptured

## Integration Points

### Upstream Dependencies (Phase 1 & 2)

- **Phase 1 (01-03)**: Test-SessionCompliance.ps1 called by runbook wrapper with splatted parameters
- **Phase 2 (02-01)**: Queries fsi_validationhistories table for drift detection
- **Phase 2 (02-01)**: Writes to fsi_sessionbaselines table for baseline storage
- **Phase 2 (02-03)**: Passes -DataverseUrl to Test-SessionCompliance.ps1 for threshold override

### Downstream Dependencies (This Phase)

- **Plan 03-02**: Power Automate daily validation flow will trigger Start-SessionValidationRunbook.ps1
- **Plan 03-03**: Power Automate alerting flow will parse JSON output and route based on AlertRequired flag

### Cross-Solution Integration

- **ACV (v4)**: Shares fail-open drift detection pattern
- **ACV (v4)**: Similar runbook wrapper structure (Start-TenantValidationRunbook.ps1)
- **Future validators**: Can follow same runbook wrapper pattern with certificate auth and JSON output

## Next Phase Readiness

**Phase 3 Plan 2 can proceed** — Power Automate daily validation orchestrator flow is next.

**Readiness checklist:**
- ✅ Runbook wrapper exists with certificate-based auth
- ✅ JSON output schema defined (9 properties documented)
- ✅ AlertRequired flag enables simple condition routing in Power Automate
- ✅ Drift detection operational (queries ValidationHistory)
- ✅ Baseline capture operational (writes SessionBaseline records)

**Blockers:** None

**Concerns:** None

**Recommendations for next plan:**
1. Power Automate daily validation flow should use Azure Automation webhook trigger
2. Parse JSON action schema should match 9 properties from Start-SessionValidationRunbook output
3. Condition action should check AlertRequired flag for Teams notification routing
4. Consider separate flows for validation orchestration vs alerting (separation of concerns)

## Usage Patterns

### Runbook Deployment

```powershell
# Import to Azure Automation
Import-AzAutomationRunbook `
    -ResourceGroupName "rg-governance" `
    -AutomationAccountName "aa-governance" `
    -Path ".\Start-SessionValidationRunbook.ps1" `
    -Type PowerShell7 `
    -Name "SSC-DailyValidation"

# Publish runbook
Publish-AzAutomationRunbook `
    -ResourceGroupName "rg-governance" `
    -AutomationAccountName "aa-governance" `
    -Name "SSC-DailyValidation"

# Create schedule (daily at 2 AM UTC)
New-AzAutomationSchedule `
    -ResourceGroupName "rg-governance" `
    -AutomationAccountName "aa-governance" `
    -Name "SSC-DailySchedule" `
    -StartTime (Get-Date "2:00 AM").AddDays(1) `
    -DayInterval 1

# Link runbook to schedule
Register-AzAutomationScheduledRunbook `
    -ResourceGroupName "rg-governance" `
    -AutomationAccountName "aa-governance" `
    -RunbookName "SSC-DailyValidation" `
    -ScheduleName "SSC-DailySchedule" `
    -Parameters @{
        Zone = "Zone3"
        DataverseUrl = "https://governance.crm.dynamics.com"
        TenantId = "contoso.onmicrosoft.com"
        ClientId = "12345-app-id"
        CertificateThumbprint = "ABCDEF123456"
        ConfigPath = "D:\RunbookAssets\tenant-config.json"
    }
```

### Baseline Capture

```powershell
# Preview what would be captured (WhatIf mode)
.\Invoke-BaselineCapture.ps1 `
    -Zone Zone3 `
    -DataverseUrl "https://governance.crm.dynamics.com" `
    -TenantId "contoso.onmicrosoft.com" `
    -ClientId "12345-app-id" `
    -Interactive `
    -WhatIf

# Capture baseline after reviewing preview
.\Invoke-BaselineCapture.ps1 `
    -Zone Zone3 `
    -DataverseUrl "https://governance.crm.dynamics.com" `
    -TenantId "contoso.onmicrosoft.com" `
    -ClientId "12345-app-id" `
    -Interactive
```

### JSON Output Schema

**Start-SessionValidationRunbook.ps1 output:**

```json
{
  "RunType": "SessionValidation",
  "Timestamp": "2026-02-07T00:00:00Z",
  "Zone": "Zone3",
  "OverallStatus": "Passed",
  "Reason": "All validators passed successfully.",
  "Validators": {
    "SessionControls": { "Status": "Passed", "Confidence": "HIGH", "Reason": "...", "Timestamp": "..." },
    "AuthenticationStrength": { "Status": "Passed", "Confidence": "MEDIUM", "Reason": "...", "Timestamp": "..." },
    "PimRoleSettings": { "Status": "Skipped", "Confidence": "N/A", "Reason": "...", "Timestamp": "..." },
    "BreakGlassExclusions": { "Status": "Passed", "Confidence": "HIGH", "Reason": "...", "Timestamp": "..." }
  },
  "Drift": {
    "DriftDetected": false,
    "CurrentStatus": "Passed",
    "BaselineStatus": "Passed",
    "BaselineDate": "2026-02-06T12:00:00Z",
    "IsFirstRun": false
  },
  "AlertRequired": false,
  "AlertSeverity": "Passed"
}
```

**Invoke-BaselineCapture.ps1 output:**

```json
{
  "BaselineId": "12345678-1234-1234-1234-123456789abc",
  "Zone": "Zone3",
  "CapturedOn": "2026-02-07T00:00:00Z",
  "SignInFrequencyMinutes": 60,
  "AuthStrength": "phishing-resistant",
  "RequireCompliantDevice": true,
  "PoliciesCaptured": 2,
  "PreviousBaselinesDeactivated": 1
}
```

## Repository Context

**Solution repository:** FSI-AgentGov-Solutions
**Commits:** d88875d, 2c9da94 (committed to FSI-AgentGov-Solutions)
**Documentation repository:** FSI-AgentGov
**Planning docs:** .planning/phases/03-automation-and-alerting/

## Self-Check: PASSED

All verification checks passed:
- ✅ Start-SessionValidationRunbook.ps1 exists on disk
- ✅ Invoke-BaselineCapture.ps1 exists on disk
- ✅ Commit d88875d exists in git log
- ✅ Commit 2c9da94 exists in git log
