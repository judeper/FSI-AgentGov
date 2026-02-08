---
phase: 03-automation-and-alerting
verified: 2026-02-06T23:45:00Z
status: gaps_found
score: 3/4 must-haves verified
gaps:
  - truth: "A scheduled Power Automate flow runs daily drift detection that compares live CA session controls against Dataverse baselines and writes results to immutable validation history"
    status: failed
    reason: "Flow executes daily and compares against baselines, BUT validation results are NOT written to fsi_validationhistories table. The immutable audit trail is missing."
    artifacts:
      - path: "session-security-configurator/src/session-validation-flow.json"
        issue: "No action writes Parse_Results output to Dataverse fsi_validationhistories table"
      - path: "session-security-configurator/scripts/Start-SessionValidationRunbook.ps1"
        issue: "Runbook outputs JSON but does not write to ValidationHistory (by design - expects flow to do it)"
    missing:
      - "Power Automate action after Parse_Results that POSTs to Dataverse fsi_validationhistories"
      - "Record should include: fsi_zone, fsi_severity (mapped from OverallStatus), fsi_timestamp, fsi_driftdetected, fsi_rawjson (full validation output)"
      - "Action should run regardless of AlertRequired value (write all results, not just failures)"
  - truth: "Drift detection operates in detect-only mode (no auto-remediation for Zone 3) and all scan results are persisted in Dataverse for audit trail"
    status: failed
    reason: "Drift detection is detect-only (correct), but scan results are NOT persisted to Dataverse. No audit trail exists."
    artifacts:
      - path: "session-security-configurator/src/session-validation-flow.json"
        issue: "Flow routes alerts but never writes scan results to fsi_validationhistories"
    missing:
      - "Same as above - Dataverse write action for immutable audit trail"
---

# Phase 3: Automation and Alerting Verification Report

**Phase Goal:** Session security drift is automatically detected daily and operators receive classified alerts when configuration deviates from baselines

**Verified:** 2026-02-06T23:45:00Z  
**Status:** gaps_found  
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | A scheduled Power Automate flow runs daily drift detection that compares live CA session controls against Dataverse baselines and writes results to immutable validation history | ❌ FAILED | Flow runs daily (Recurrence trigger exists), drift detection executes (Start-SessionValidationRunbook.ps1 queries baselines), BUT validation results are NOT written to fsi_validationhistories. No audit trail created. |
| 2 | When drift is detected (sign-in frequency weakened, auth strength downgraded, policy disabled, exclusions added), a Teams adaptive card alert is sent with severity classification matching the zone affected | ✅ VERIFIED | Flow Check_Alert_Required routes on AlertRequired flag. Check_Severity_For_Teams posts adaptive card for Failed/Error severity. Card displays zone, severity, baseline comparison, validator status. |
| 3 | Operators can capture a baseline snapshot and compare subsequent scans against it, with zone-parameterized thresholds loaded from environment variables | ✅ VERIFIED | Invoke-BaselineCapture.ps1 writes SessionBaseline to Dataverse with zone-specific thresholds. Start-SessionValidationRunbook.ps1 queries fsi_sessionbaselines for comparison. Test-SessionCompliance.ps1 reads thresholds from env vars via Get-DataverseThreshold.ps1. |
| 4 | Drift detection operates in detect-only mode (no auto-remediation for Zone 3) and all scan results are persisted in Dataverse for audit trail | ❌ FAILED | Detect-only: VERIFIED (no remediation actions in flow). Scan results persisted: FAILED (no Dataverse write action for fsi_validationhistories). |

**Score:** 2/4 truths fully verified (50%)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `scripts/Start-SessionValidationRunbook.ps1` | Runbook wrapper with drift detection | ✅ VERIFIED | 352 lines, dot-sources Test-SessionCompliance.ps1, includes Get-DriftStatus inline function that queries fsi_validationhistories, outputs JSON with 9 properties (RunType, Timestamp, Zone, OverallStatus, Reason, Validators, Drift, AlertRequired, AlertSeverity) |
| `scripts/Invoke-BaselineCapture.ps1` | Baseline capture to Dataverse | ✅ VERIFIED | 410 lines, queries live CA policies via Graph, deactivates existing active baselines, writes SessionBaseline record with zone option set mapping (Zone1=100000001, Zone2=100000002, Zone3=100000003), supports WhatIf mode |
| `src/adaptive-card-session-alert.json` | Teams adaptive card template | ✅ VERIFIED | Valid Adaptive Card v1.4 JSON, 12 placeholders (overallStatus, timestamp, zone, baselineStatus, currentStatus, baselineDate, reason, sessionControlsStatus, authStrengthStatus, pimStatus, breakGlassStatus, validationHistoryUrl), SSC-specific validators |
| `src/session-validation-flow.json` | Power Automate daily validation flow | ⚠️ PARTIAL | Valid Logic Apps workflow schema, Recurrence trigger (6 AM UTC daily), 10 Initialize Variable actions, Scope_Try with Create_Automation_Job (runbookName: Start-SessionValidationRunbook), Parse_Results with SSC schema, alert routing (Teams+email for Failed/Error, email only for Warning), BUT MISSING Dataverse write action for ValidationHistory |
| `docs/FLOW_SETUP.md` | Flow deployment guide | ✅ VERIFIED | 364 lines, 10 sections (Overview, Prerequisites, Steps 1-5, Multi-Zone, Alert Routing, Troubleshooting), variable configuration table with all 10 variables, alert routing summary, troubleshooting covers 4+ failure scenarios |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|----|--------|---------|
| session-validation-flow.json | Start-SessionValidationRunbook.ps1 | Azure Automation Create Job action with runbookName parameter | ✅ WIRED | Line 197: "runbookName": "Start-SessionValidationRunbook", job parameters include Zone, DataverseUrl, TenantId, ClientId, CertificateThumbprint, ConfigPath |
| session-validation-flow.json | adaptive-card-session-alert.json | Inline adaptive card JSON with replace() substitutions in Post_Teams_Card action | ✅ WIRED | Post_Teams_Card action (line 443) embeds card JSON inline, 11 nested replace() calls for placeholders using body('Parse_Results') dynamic expressions |
| Start-SessionValidationRunbook.ps1 | Test-SessionCompliance.ps1 | Dot-source and call with splatted parameters | ✅ WIRED | Line 129: `. "$scriptRoot\Test-SessionCompliance.ps1"`, line 151: `Test-SessionCompliance @validationParams` |
| Start-SessionValidationRunbook.ps1 | Dataverse ValidationHistory (query) | Inline Get-DriftStatus function with Invoke-RestMethod GET | ✅ WIRED | Line 210: queries `fsi_validationhistories?$filter=fsi_severity eq 1&$orderby=createdon desc&$top=1` for baseline comparison |
| session-validation-flow.json | Dataverse ValidationHistory (write) | POST action to write validation results | ❌ NOT_WIRED | **MISSING:** No action in Scope_Try writes Parse_Results output to fsi_validationhistories table. This breaks audit trail requirement. |
| Invoke-BaselineCapture.ps1 | Dataverse SessionBaseline | POST to fsi_sessionbaselines entity | ✅ WIRED | Line 370: `Invoke-RestMethod -Uri $createUrl -Method Post` with full baseline record including zone option set value, sign-in frequency, auth strength, raw JSON |
| Invoke-BaselineCapture.ps1 | Microsoft Graph | Get-MgIdentityConditionalAccessPolicy for live CA policy state | ✅ WIRED | Line 165: `Get-MgIdentityConditionalAccessPolicy` filters for enabled policies with session controls, extracts SignInFrequency, AuthenticationStrength, RequireCompliantDevice |

### Requirements Coverage

Phase 3 requirements (from ROADMAP.md):

| Requirement | Status | Blocking Issue |
|-------------|--------|----------------|
| DDA-01: Detect session control drift | ✅ SATISFIED | Start-SessionValidationRunbook.ps1 Get-DriftStatus queries fsi_validationhistories for baseline, compares CurrentStatus vs BaselineStatus, returns DriftDetected boolean |
| DDA-02: Teams adaptive card alerts with severity | ✅ SATISFIED | Flow Check_Severity_For_Teams posts card for Failed/Error, adaptive-card-session-alert.json displays zone, severity, baseline comparison, validator status |
| DDA-03: Dataverse immutable validation history | ❌ BLOCKED | **CRITICAL GAP:** Flow does not write validation results to fsi_validationhistories. Immutable audit trail requirement not met. |
| DDA-04: Baseline capture and comparison | ✅ SATISFIED | Invoke-BaselineCapture.ps1 writes SessionBaseline, Start-SessionValidationRunbook.ps1 compares against it |
| INF-04: Power Automate scheduled daily drift scan flow | ✅ SATISFIED | session-validation-flow.json Recurrence trigger (6 AM UTC daily), executes runbook, parses results, routes alerts |

**Coverage:** 4/5 requirements satisfied. DDA-03 blocked by missing Dataverse write action.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| session-validation-flow.json | N/A (missing action) | **Missing critical persistence** | 🛑 Blocker | No validation results written to fsi_validationhistories. Breaks audit trail requirement (success criteria 1 & 4). Drift detection will always fail open (no historical baseline to compare against). |
| Start-SessionValidationRunbook.ps1 | 210-232 | Drift detection queries fsi_validationhistories but flow never populates it | ⚠️ Warning | Drift detection always returns IsFirstRun=true or DriftDetected=true (fail-open). Intended behavior until ValidationHistory is populated, but indicates missing flow action. |

### Gaps Summary

**2 gaps blocking goal achievement:**

#### Gap 1: Validation results not written to Dataverse ValidationHistory

**Truth:** "A scheduled Power Automate flow runs daily drift detection that compares live CA session controls against Dataverse baselines and writes results to immutable validation history"

**Status:** Failed (50% complete — runs daily, compares baselines, but does NOT write results)

**What's missing:**
1. Power Automate action in Scope_Try (after Parse_Results) that POSTs to Dataverse Web API
2. Target: `{DataverseUrl}/api/data/v9.2/fsi_validationhistories`
3. Payload mapping:
   - `fsi_name`: "{Zone}-{Timestamp}" 
   - `fsi_zone`: Zone option set value (100000001/100000002/100000003)
   - `fsi_severity`: Map OverallStatus to option set (Passed=1, Warning=2, Failed=3, Error=4)
   - `fsi_timestamp`: Parse_Results Timestamp (ISO 8601)
   - `fsi_driftdetected`: Parse_Results Drift.DriftDetected (boolean)
   - `fsi_baselinestatus`: Parse_Results Drift.BaselineStatus (string)
   - `fsi_rawjson`: Full Parse_Results JSON (ConvertTo-Json for audit)
4. This action must run REGARDLESS of AlertRequired value (write all scan results, not just failures)

**Why it matters:**
- FINRA 4511/SEC 17a-4 require tamper-proof audit trails
- Without ValidationHistory writes, there's no evidence that validation scans occurred
- Drift detection becomes non-functional (always IsFirstRun=true or fail-open)
- Regulatory examiners cannot verify continuous monitoring

#### Gap 2: Audit trail requirement not satisfied

**Truth:** "Drift detection operates in detect-only mode (no auto-remediation for Zone 3) and all scan results are persisted in Dataverse for audit trail"

**Status:** Failed (detect-only verified, but scan results NOT persisted)

**What's missing:**
- Same as Gap 1 — the missing Dataverse write action breaks the "all scan results are persisted" requirement
- Even successful scans (Passed status, no drift) must be written for continuous monitoring proof

**Impact on drift detection:**
- Get-DriftStatus (line 178-301 in Start-SessionValidationRunbook.ps1) queries fsi_validationhistories for the most recent Passed validation
- If no records exist, drift detection returns IsFirstRun=true
- If ValidationHistory is never populated, every scan will be treated as "first run"
- Drift alerts will be generated incorrectly (false positives)

---

## Recommendations

### Fix Required Before Phase Completion

**Add Dataverse write action to session-validation-flow.json:**

1. Insert new action after Parse_Results (before Check_Alert_Required)
2. Name: `Write_Validation_History`
3. Type: HTTP connector or Dataverse connector
4. Method: POST
5. URI: `@{variables('DataverseUrl')}/api/data/v9.2/fsi_validationhistories`
6. Headers:
   ```json
   {
     "Authorization": "Bearer {dataverse_token}",
     "Content-Type": "application/json"
   }
   ```
7. Body:
   ```json
   {
     "fsi_name": "@{body('Parse_Results')?['Zone']}-@{body('Parse_Results')?['Timestamp']}",
     "fsi_zone": "@{if(equals(body('Parse_Results')?['Zone'], 'Zone1'), 100000001, if(equals(body('Parse_Results')?['Zone'], 'Zone2'), 100000002, 100000003))}",
     "fsi_severity": "@{switch(body('Parse_Results')?['OverallStatus'], 'Passed', 1, 'Warning', 2, 'Failed', 3, 'Error', 4)}",
     "fsi_timestamp": "@{body('Parse_Results')?['Timestamp']}",
     "fsi_driftdetected": "@{body('Parse_Results')?['Drift']?['DriftDetected']}",
     "fsi_baselinestatus": "@{body('Parse_Results')?['Drift']?['BaselineStatus']}",
     "fsi_rawjson": "@{string(body('Parse_Results'))}"
   }
   ```
8. runAfter: `Parse_Results: ["Succeeded"]`
9. Configure failure handling: Continue on failure (don't block alerting if Dataverse write fails)

**Connection reference:**
- Add Dataverse connection reference to flow parameters
- Bind to fsi_cr_dataverse_sessionvalidation (create if needed)

**Update FLOW_SETUP.md:**
- Add connection reference binding step for Dataverse
- Document ValidationHistory write action in "What this flow does" section
- Add troubleshooting scenario for Dataverse write failures

### Verification After Fix

Run these checks after adding Dataverse write action:

1. Deploy updated flow to Power Automate
2. Trigger manual test run
3. Verify Write_Validation_History action succeeds
4. Query Dataverse: `GET {DataverseUrl}/api/data/v9.2/fsi_validationhistories?$orderby=createdon desc&$top=5`
5. Confirm records exist with correct fsi_zone, fsi_severity, fsi_timestamp, fsi_driftdetected
6. Run second validation scan
7. Verify drift detection now compares against first scan's baseline (IsFirstRun=false)

---

_Verified: 2026-02-06T23:45:00Z_  
_Verifier: Claude (gsd-verifier)_
