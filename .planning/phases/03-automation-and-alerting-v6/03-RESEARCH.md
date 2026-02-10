# Phase 3: Automation and Alerting (v6) - Research

**Researched:** 2026-02-09
**Milestone:** v6 — Agent Access Governance Monitor
**Domain:** Power Automate automation, Teams alerting, drift detection, baseline management
**Confidence:** HIGH

## Summary

Phase 3 creates the automation and alerting layer for the Agent Access Governance Monitor. This phase bridges the PowerShell validation scripts (Phase 1) and Dataverse infrastructure (Phase 2) into an automated daily workflow: a Power Automate flow triggers an Azure Automation runbook that validates agent access settings, detects drift from baselines, persists results to Dataverse, and alerts operators via Teams adaptive cards when violations are detected.

**Key finding:** Phase 1 and Phase 2 already provide the core validation pipeline (`Test-AgentAccessCompliance.ps1` with `-PersistResults`) and Dataverse infrastructure (3 tables, 6 environment variables, 3 connection references). Phase 3 needs to add: (1) a PowerShell runbook wrapper for non-interactive execution, (2) a baseline capture script, (3) drift detection logic comparing current settings to active baselines, (4) an adaptive card template, and (5) a Power Automate flow JSON with setup documentation.

**Primary recommendation:** Follow the proven SSC (v5) Phase 3 pattern exactly — same 3-plan structure, same wave assignment, same artifact types — adapting content from session security to agent access. Learn from the SSC gap where Dataverse validation history writes were missing from the initial flow design: include the write action in Plan 02 from the start.

---

## 1. Existing Foundation (What Phase 1 & 2 Deliver)

### Phase 1 PowerShell Scripts

| Script | Purpose | Phase 3 Integration Point |
|--------|---------|---------------------------|
| `Get-EnvironmentAccessSettings.ps1` | Queries Power Platform environments, extracts agent access settings | Called by Test-AgentAccessCompliance (orchestrator) |
| `Compare-ZoneCompliance.ps1` | Compares settings against zone baselines, generates violations | Violations feed into adaptive card alerts |
| `Test-AgentAccessCompliance.ps1` | Full orchestrator: query → compare → summarize → output | Runbook wrapper calls this with splatted parameters |
| `AAMClient.psm1` | Dataverse helper functions (Connect, Read, Write) | Baseline capture and drift detection extend this |
| `zone-settings-baseline.json` | Static zone expected values for 3 agent access settings | Still used for zone compliance checking |

### Phase 2 Dataverse Infrastructure

| Component | Details | Phase 3 Usage |
|-----------|---------|---------------|
| `fsi_AccessBaseline` | UserOwned, 11 columns, stores per-environment snapshots | Baseline capture writes here; drift detection reads active baseline |
| `fsi_AccessValidationHistory` | OrganizationOwned (immutable), 10 columns, audit trail | Flow writes scan results here after every run |
| `fsi_AccessViolation` | UserOwned, 15 columns, per-violation records | Already written by `-PersistResults`; flow ensures this path is always taken |
| `fsi_AAM_TeamsGroupId` | Environment variable | Flow reads for Teams channel targeting |
| `fsi_AAM_TeamsChannelId` | Environment variable | Flow reads for Teams channel targeting |
| `fsi_AAM_ScanFrequencyHours` | Environment variable (24) | Could drive flow recurrence (informational) |
| `fsi_cr_dataverse_accessmonitor` | Connection reference | Flow uses for Dataverse writes |
| `fsi_cr_teams_accessmonitor` | Connection reference | Flow uses for Teams adaptive card posting |

### AAMClient.psm1 Functions (Current State)

| Function | Status | Phase 3 Need |
|----------|--------|-------------|
| `Connect-AAMDataverse` | Exists | Used by runbook wrapper |
| `Get-AAMConnection` | Exists | Used for connection validation |
| `Get-AAMEnvironmentVariable` | Exists | Used by runbook for operational params |
| `Get-AAMActiveBaseline` | Exists | Used by drift detection |
| `Write-AAMValidationHistory` | Exists (with RunId) | Used by `-PersistResults` path |
| `Write-AAMViolation` | Exists (with RunId) | Used by `-PersistResults` path |
| `Save-AAMBaseline` | **MISSING** | Needed for baseline capture |
| `Get-AAMLastValidation` | **MISSING** | Needed for drift detection (compare to previous scan) |

---

## 2. Proven Patterns (SSC v5 Phase 3)

### SSC Plan Structure

| Plan | Wave | Content | Duration |
|------|------|---------|----------|
| 03-01 | 1 | Runbook wrapper + baseline capture | ~6 min |
| 03-02 | 2 | Adaptive card + flow JSON + FLOW_SETUP.md | ~8 min |
| 03-03 | 3 | Validation history write action + drift refinement | ~4 min |

**Total SSC Phase 3:** ~18 min across 3 plans. AAM should be comparable.

### SSC Runbook Wrapper Pattern (Start-SessionValidationRunbook.ps1)

Key design elements to replicate for AAM:
- `#Requires -Version 7.0` with `#Requires -Modules MSAL.PS`
- Certificate-based auth: `-TenantId`, `-ClientId`, `-CertificateThumbprint`
- Zone-specific execution: `-Zone` parameter targets a single zone per run
- Drift detection: queries last Dataverse validation history, compares current severity numerically
- Structured JSON output only (no Write-Host, only Write-Verbose for diagnostics)
- Output schema: `RunType`, `Timestamp`, `Zone`, `OverallStatus`, `Reason`, `Validators`, `Drift`, `AlertRequired`, `AlertSeverity`
- `AlertRequired` set when: status is Failed/Error OR drift is detected (status regressed)

### SSC Adaptive Card Pattern

- Uses `${variableName}` convention for Power Automate `replace()` substitution
- Sections: header (solution name + severity badge), zone info, violation summary table, action buttons
- Action buttons: "View in Purview" / "Run Manual Check" / "View Documentation"
- Severity drives card accent color: Critical=attention, High=warning, Info=accent

### SSC Flow Pattern (session-validation-flow.json)

- **Trigger:** Recurrence (daily, 6:00 AM UTC)
- **Variables:** DataverseUrl, TeamsGroupId, TeamsChannelId (initialized from config)
- **Scope_Try:** Azure Automation Create Job → Wait for Job → Get Job Output → Parse_Results JSON → Write_Validation_History → Check_Alert_Required → conditional Teams/email
- **Scope_Catch:** CRITICAL error email when flow itself fails
- **Alert routing:** Failed/Error → Teams adaptive card AND email; Warning → email only
- **Connection references:** `fsi_cr_teams_sessionvalidation`, `fsi_cr_dataverse_sessionvalidation`

### SSC Gap Lesson

In SSC, the validation history Dataverse write was initially missing from the flow (plan 02), causing:
- Drift detection always returned `IsFirstRun=true` (no prior records to compare)
- No regulatory audit trail in Dataverse
- Required a gap closure plan (03-03)

**AAM must include the Dataverse write action in the flow from plan 02**, but plan 03 still adds refinements for drift detection comparison depth and CHANGELOG update.

---

## 3. AAM-Specific Design Decisions

### Drift Detection Strategy

AAM drift detection differs from SSC because it compares *agent access settings* (3 discrete Power Platform properties) rather than *Conditional Access policy configurations*:

| Aspect | SSC | AAM |
|--------|-----|-----|
| **What drifts** | CA policy session controls, auth strengths, PIM settings | `bot-limitSharingMode`, `bot-authoringSharingDisabled`, `bot-publishedBotLimitSharingMode` |
| **Drift source** | Compare CA policies to baseline snapshot | Compare Power Platform env settings to active baseline |
| **Severity on drift** | Numeric comparison of validation severity | Zone-based: Zone 3 drift → CRITICAL, Zone 2 → HIGH |
| **Baseline storage** | `fsi_SessionBaseline` | `fsi_AccessBaseline` |
| **Comparison method** | Runbook queries Dataverse for last passed scan | Runbook queries `fsi_accessbaselines` for active baseline per environment |

**AAM drift detection approach:**
1. For each environment in the scan, query active baseline from `fsi_accessbaselines`
2. Compare current settings to baseline settings (3 properties each)
3. If any setting has changed (weakened or strengthened), flag as drift
4. Drift direction matters: weakened → alert as violation; strengthened → informational
5. If no active baseline exists, use static `zone-settings-baseline.json` (Phase 1 behavior)

### Baseline Capture Design

`Invoke-AccessBaselineCapture.ps1` needs to:
1. Run `Get-EnvironmentAccessSettings.ps1` to capture live settings for all (or targeted) environments
2. For each environment, call `Save-AAMBaseline` to write to `fsi_accessbaselines`
3. Set `fsi_isactive = true` on new baseline, deactivate any prior active baseline for that environment
4. Store all 3 access settings + zone classification + raw JSON snapshot
5. Support `-Zone` parameter to capture only environments in a specific zone
6. Support `-WhatIf` for preview mode

### Runbook Output Schema

```json
{
  "RunType": "Scheduled",
  "Timestamp": "2026-02-09T06:00:00Z",
  "TotalEnvironments": 15,
  "OverallStatus": "Failed",
  "Reason": "3 environments have agent access violations",
  "ZoneSummary": {
    "Zone1": { "Total": 5, "Compliant": 5, "Violations": 0 },
    "Zone2": { "Total": 6, "Compliant": 4, "Violations": 2 },
    "Zone3": { "Total": 4, "Compliant": 3, "Violations": 1 }
  },
  "Violations": [
    {
      "Environment": "Trading-Z3-Prod",
      "Zone": 3,
      "Setting": "bot-limitSharingMode",
      "Expected": "ExcludeExternalUsers",
      "Actual": "NoRestrictions",
      "Severity": "Critical",
      "RegulatoryContext": "FINRA 4511, SOX 404"
    }
  ],
  "Drift": {
    "HasDrift": true,
    "IsFirstRun": false,
    "DriftedEnvironments": 1,
    "Details": [
      {
        "Environment": "Trading-Z3-Prod",
        "Setting": "bot-limitSharingMode",
        "BaselineValue": "ExcludeExternalUsers",
        "CurrentValue": "NoRestrictions",
        "Direction": "Weakened"
      }
    ]
  },
  "AlertRequired": true,
  "AlertSeverity": "Critical"
}
```

### Adaptive Card Design

AAM adaptive card should show:
- **Header:** "Agent Access Governance Monitor" + severity badge
- **Run summary:** Total environments, violations, drift count
- **Zone breakdown table:** Zone 1/2/3 with compliant vs violation counts
- **Violation details:** Environment, zone, setting, expected vs actual, severity
- **Drift indicators:** Baseline vs current for drifted settings
- **Action buttons:** "View in Power Platform Admin" / "Run Manual Check" / "View Documentation"

### Power Automate Flow Design

- **Name:** "AAM - Agent Access Validation"
- **Trigger:** Recurrence (daily, 6:00 AM UTC) — matches SSC pattern
- **Execution:** Azure Automation runbook (`Start-AccessValidationRunbook.ps1`)
- **Post-processing:** Parse JSON → Write to Dataverse → Check AlertRequired → Route alerts
- **Alert routing:**
  - Critical/Failed → Teams adaptive card + email
  - High/Warning → email only
  - Info/Passed → log only (no alert)
- **Connection references:** `fsi_cr_dataverse_accessmonitor`, `fsi_cr_teams_accessmonitor`

---

## 4. New AAMClient.psm1 Functions Needed

### Save-AAMBaseline

```powershell
function Save-AAMBaseline {
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory)][string]$EnvironmentGuid,
        [Parameter(Mandatory)][string]$EnvironmentName,
        [Parameter(Mandatory)][int]$Zone,
        [Parameter(Mandatory)][string]$BotLimitSharingMode,
        [Parameter(Mandatory)][bool]$BotAuthoringSharingDisabled,
        [Parameter(Mandatory)][string]$BotPublishedBotLimitSharingMode,
        [string]$CapturedBy,
        [string]$RawJson
    )
    # 1. Query fsi_accessbaselines for active baseline with this EnvironmentGuid
    # 2. If found, PATCH fsi_isactive = false (deactivate)
    # 3. POST new baseline record with fsi_isactive = true
}
```

### Get-AAMLastValidation

```powershell
function Get-AAMLastValidation {
    [CmdletBinding()]
    param(
        [int]$Top = 1
    )
    # Query fsi_accessvalidationhistory ordered by fsi_timestamp desc, top $Top
    # Returns most recent scan summary for drift comparison
}
```

---

## 5. Risks and Mitigations

| Risk | Severity | Mitigation |
|------|----------|------------|
| Azure Automation not available in tenant | HIGH | Document Azure Automation prerequisites; provide manual script execution alternative |
| Teams channel not configured for alerts | MEDIUM | Flow gracefully skips Teams alert when TeamsGroupId/ChannelId env vars are empty |
| No active baseline for environment | LOW | Fallback to static zone-settings-baseline.json for compliance check; drift detection returns `IsFirstRun=true` |
| Dataverse write failure in flow | MEDIUM | Scope_Catch handles errors; flow continues alerting even if history write fails |
| Large environment count impacts flow runtime | LOW | Azure Automation handles long-running scripts; flow has configurable timeout |

---

## 6. File Manifest

### New Files (Phase 3 Creates)

| File | Repository | Purpose |
|------|------------|---------|
| `scripts/Start-AccessValidationRunbook.ps1` | FSI-AgentGov-Solutions | Azure Automation runbook wrapper |
| `scripts/Invoke-AccessBaselineCapture.ps1` | FSI-AgentGov-Solutions | Operator-initiated baseline capture |
| `src/adaptive-card-access-alert.json` | FSI-AgentGov-Solutions | Teams adaptive card template |
| `src/access-validation-flow.json` | FSI-AgentGov-Solutions | Power Automate flow definition |
| `docs/FLOW_SETUP.md` | FSI-AgentGov-Solutions | Flow creation and configuration guide |

### Modified Files (Phase 3 Modifies)

| File | Repository | Change |
|------|------------|--------|
| `scripts/private/AAMClient.psm1` | FSI-AgentGov-Solutions | Add Save-AAMBaseline and Get-AAMLastValidation functions |
| `CHANGELOG.md` | FSI-AgentGov-Solutions | Add v0.3.0 entry for automation and alerting |

---

*Research completed: 2026-02-09*
*Confidence: HIGH — SSC v5 Phase 3 provides a proven pattern; AAM adaptation is straightforward*
*Recommended approach: 3 plans across 3 waves following SSC structure exactly*
