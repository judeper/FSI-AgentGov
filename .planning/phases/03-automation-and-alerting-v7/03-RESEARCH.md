# Phase 3: Automation and Alerting (v7) — Research

**Researched:** 2026-02-10
**Milestone:** v7 — Content Moderation Governance Monitor
**Domain:** Power Automate automation, Teams alerting, drift detection, baseline management
**Requirements:** DDA-01, DDA-02, DDA-03, DDA-04, INF-04
**Confidence:** HIGH

## Summary

Phase 3 creates the automation and alerting layer for the Content Moderation Governance Monitor. This phase bridges the PowerShell validation scripts (Phase 1) and Dataverse infrastructure (Phase 2) into an automated daily workflow: a Power Automate flow triggers an Azure Automation runbook that validates per-agent content moderation levels, detects drift from baselines, persists results to Dataverse, and alerts operators via Teams adaptive cards when violations are detected.

**Key difference from AAM (v6):** CMM validates **per-agent content moderation levels** (Low/Medium/High) rather than per-environment access settings (3 Power Platform properties). This means drift detection operates at the agent level (hundreds of agents) rather than the environment level (tens of environments), and baselines store per-agent moderation levels rather than per-environment access settings.

**Primary recommendation:** Follow the proven AAM (v6) Phase 3 pattern — same 3-plan structure, same wave assignment, same artifact types — adapting from environment-level access settings to agent-level moderation levels. Incorporate the AAM gap fix (Dataverse history write before alerting) from the start.

---

## 1. v6 Phase 3 Plans (Complete Reference)

### Plan 03-01: Runbook Wrapper, Baseline Capture, and CMMClient Functions (Wave 1)

**Must-haves:**
- `Start-ModerationValidationRunbook.ps1` wraps `Test-ContentModerationCompliance.ps1` for non-interactive execution with certificate-based auth, structured JSON pipeline output, and drift detection via active baseline comparison
- Runbook outputs JSON with RunType, Timestamp, TotalAgents, TotalEnvironments, OverallStatus, Reason, ZoneSummary, Violations, Drift, AlertRequired, AlertSeverity
- Drift detection queries `fsi_moderationbaselines` for active baselines per agent and compares current moderation levels to baseline values, failing open on query errors
- `Invoke-ModerationBaselineCapture.ps1` captures live agent moderation levels via `Get-AgentModerationSettings` and writes baseline records to Dataverse with `fsi_is_active` management
- Baseline capture deactivates any existing active baseline for the agent before writing the new baseline (single active baseline per agent)
- CMMClient.psm1 has `Save-CMMBaseline` stub → needs completion with active baseline deactivation; `Get-CMMLastValidation` stub → needs completion with query logic

**AAM v6 03-01 Files Created:**
| File | Lines | Purpose |
|------|-------|---------|
| `Start-AccessValidationRunbook.ps1` | 525 | Runbook wrapper with drift detection |
| `Invoke-AccessBaselineCapture.ps1` | 402 | Operator baseline capture |
| `AAMClient.psm1` | MODIFIED | +Save-AAMBaseline, +Get-AAMLastValidation |

### Plan 03-02: Adaptive Card, Power Automate Flow JSON, and Flow Setup Guide (Wave 2)

**Must-haves:**
- Adaptive card template displays content moderation violation alerts with severity badge, zone summary, per-agent violation details (agent name, environment, zone, expected vs actual moderation level), drift indicators, and action buttons
- Power Automate flow JSON defines daily Recurrence trigger (6:00 AM UTC), variable initialization, Scope_Try/Scope_Catch error handling, Azure Automation job execution, Parse JSON, Dataverse history write, conditional Teams/email alerting
- Flow routes Critical/Failed severity to Teams adaptive card AND email; High/Warning to email only; Passed/Info logged only
- Flow writes every scan result to `fsi_moderationvalidationhistory` after Parse_Results regardless of AlertRequired value
- FLOW_SETUP.md provides step-by-step instructions for importing the flow, configuring variables, binding connection references, and testing
- All placeholders use `${variableName}` convention replaceable by Power Automate `replace()` function
- Scope_Catch sends CRITICAL error email when the flow itself fails

**AAM v6 03-02 Files Created:**
| File | Lines | Purpose |
|------|-------|---------|
| `adaptive-card-access-alert.json` | 358 | Teams adaptive card template |
| `access-validation-flow.json` | 605 | Power Automate flow definition |
| `docs/FLOW_SETUP.md` | ~200 | Flow setup and configuration guide |

### Plan 03-03: Drift Detection Refinement, Integration Verification, and CHANGELOG (Wave 3)

**Must-haves:**
- Drift detection correctly compares per-agent moderation levels against active baselines and classifies drift direction
- FLOW_SETUP.md documents the Write_Validation_History action, Dataverse connection reference binding, and failure troubleshooting
- CHANGELOG.md v0.3.0 entry documents all Phase 3 additions
- End-to-end validation: runbook JSON output → flow Parse_Results schema → Dataverse write → adaptive card rendering are all structurally consistent

---

## 2. Phase 1 and Phase 2 Deliverables (What Exists)

### Phase 1: PowerShell Core (Complete)

| Plan | Script | Lines | Purpose |
|------|--------|-------|---------|
| 01-01 | `scripts/private/CMMClient.psm1` | 640 | Dataverse client module (10 exported functions) |
| 01-01 | `scripts/private/Connect-EnvironmentDataverse.ps1` | — | Per-environment Dataverse auth with token caching |
| 01-01 | `scripts/private/Get-ZoneClassification.ps1` | — | ELM → naming convention → Unknown zone lookup |
| 01-01 | `scripts/private/Get-ExpectedModerationLevel.ps1` | — | Zone-to-moderation compliance check with severity |
| 01-01 | `scripts/private/Test-ParameterValidation.ps1` | — | Parameter validators including Test-ModerationLevel |
| 01-01 | `templates/moderation-baseline.json` | — | Zone-to-moderation-level requirements reference |
| 01-02 | `scripts/Get-AgentModerationSettings.ps1` | ~290 | Enumerates agents across environments, extracts moderation levels |
| 01-02 | `scripts/Compare-ModerationCompliance.ps1` | ~170 | Pipeline-enabled compliance comparison with severity |
| 01-03 | `scripts/Test-ContentModerationCompliance.ps1` | 650 | Full orchestrator: query → compare → summarize → persist → output |

**Key differences from AAM Phase 1:**
- CMM operates at **per-agent level** (queries `bot` table per environment, extracts moderation level from bot configuration JSON)
- AAM operates at **per-environment level** (queries Power Platform admin API for environment-level access settings)
- CMM uses moderation levels: Low, Medium, High (3 discrete values)
- AAM uses 3 properties: `bot-limitSharingMode`, `bot-authoringSharingDisabled`, `bot-publishedBotLimitSharingMode`

### Phase 2: Dataverse Infrastructure (Complete)

| Plan | Script/File | Purpose |
|------|-------------|---------|
| 02-01 | `scripts/cmm_client.py` | CMMClient Python class for Dataverse Web API operations |
| 02-01 | `scripts/create_dataverse_schema.py` | Three-table schema deployment |
| 02-01 | `scripts/requirements.txt` | Python dependencies (msal, requests) |
| 02-02 | `scripts/create_environment_variables.py` | 7 `fsi_CMM_*` operational parameters |
| 02-02 | `scripts/create_connection_references.py` | 3 connection references (Dataverse, O365, Teams) |
| 02-02 | `scripts/deploy.py` | Full deployment orchestrator |
| 02-03 | `Test-ContentModerationCompliance.ps1` | MODIFIED — `-DataverseToken`, `-PersistResults`, Dataverse env var reads |
| 02-03 | `Compare-ModerationCompliance.ps1` | MODIFIED — `EnvironmentId` added to output |
| 02-03 | `CMMClient.psm1` | Version bump to 0.2.0 |

### Dataverse Schema (Deployed by Phase 2)

| Table | Ownership | Columns | EntitySetName | Phase 3 Usage |
|-------|-----------|---------|---------------|---------------|
| `fsi_ModerationBaseline` | UserOwned | 10 + primary | `fsi_moderationbaselines` | Baseline capture writes here; drift detection reads active baseline per agent |
| `fsi_ModerationValidationHistory` | OrganizationOwned (immutable) | 8 + primary | `fsi_moderationvalidationhistory` | Flow writes scan results here after every run |
| `fsi_ModerationViolation` | UserOwned | 11 + primary | `fsi_moderationviolations` | Already written by `-PersistResults`; flow ensures this path is always taken |

### Environment Variables (Deployed by Phase 2)

| Variable | Default | Phase 3 Usage |
|----------|---------|---------------|
| `fsi_CMM_ScanFrequencyHours` | 24 | Informational for flow schedule |
| `fsi_CMM_GracePeriodHours` | 48 | Runbook reads for environment filtering |
| `fsi_CMM_IncludeSandbox` | true | Runbook reads for sandbox inclusion |
| `fsi_CMM_IncludeDrafts` | false | Runbook reads for draft agent inclusion |
| `fsi_CMM_BaselineAgeThresholdDays` | 90 | Baseline staleness alerting |
| `fsi_CMM_TeamsGroupId` | (empty) | Flow reads for Teams channel targeting |
| `fsi_CMM_TeamsChannelId` | (empty) | Flow reads for Teams channel targeting |

### Connection References (Deployed by Phase 2)

| Reference | Connector | Phase 3 Usage |
|-----------|-----------|---------------|
| `fsi_cr_dataverse_moderationmonitor` | Dataverse | Flow uses for validation history writes |
| `fsi_cr_office365_moderationmonitor` | Office 365 | Flow uses for email alerts |
| `fsi_cr_teams_moderationmonitor` | Teams | Flow uses for adaptive card posting |

### CMMClient.psm1 Functions (Current State — 10 Exported)

| Function | Status | Phase 3 Need |
|----------|--------|-------------|
| `Connect-CMMDataverse` | ✅ Exists | Used by runbook wrapper |
| `Get-CMMConnection` | ✅ Exists | Used for connection validation |
| `Get-CMMEnvironmentVariable` | ✅ Exists | Used by runbook for operational params |
| `Get-ModerationBaseline` | ✅ Exists | Queries baselines by environment — needs enhancement for per-agent active baseline query |
| `Write-ModerationValidationHistory` | ✅ Exists (with RunId) | Used by `-PersistResults` path |
| `Write-ModerationViolation` | ✅ Exists (with RunId) | Used by `-PersistResults` path |
| `Get-AgentBots` | ✅ Exists | CMM-specific bot table query with pagination |
| `Get-BotModerationLevel` | ✅ Exists | Extracts and normalizes moderation level from bot config |
| `Save-CMMBaseline` | ⚠️ Stub exists | Has basic write — needs active baseline deactivation before save |
| `Get-CMMLastValidation` | ✅ Exists | Queries validation history ordered by timestamp desc |

---

## 3. Current CMM Solution Structure

```
content-moderation-monitor/
├── CHANGELOG.md
├── README.md
├── docs/
│   ├── EVIDENCE_EXPORT.md (stub)
│   ├── PREREQUISITES.md
│   ├── SCHEMA.md (stub)
│   └── TROUBLESHOOTING.md (stub)
├── flows/
│   └── .gitkeep
├── scripts/
│   ├── cmm_client.py
│   ├── Compare-ModerationCompliance.ps1
│   ├── create_connection_references.py
│   ├── create_dataverse_schema.py
│   ├── create_environment_variables.py
│   ├── deploy.py
│   ├── Get-AgentModerationSettings.ps1
│   ├── requirements.txt
│   ├── Test-ContentModerationCompliance.ps1
│   └── private/
│       ├── CMMClient.psm1
│       ├── Connect-EnvironmentDataverse.ps1
│       ├── Get-ExpectedModerationLevel.ps1
│       ├── Get-ZoneClassification.ps1
│       └── Test-ParameterValidation.ps1
├── src/
│   └── dataverse/
│       ├── connection-references/
│       ├── environment-variables/
│       └── tables/
└── templates/
    └── moderation-baseline.json
```

**Files that Phase 3 will CREATE:**
- `scripts/Start-ModerationValidationRunbook.ps1` — Azure Automation runbook wrapper
- `scripts/Invoke-ModerationBaselineCapture.ps1` — Operator-initiated baseline capture
- `src/adaptive-card-moderation-alert.json` — Teams adaptive card template
- `src/moderation-validation-flow.json` — Power Automate flow definition (replaces `flows/.gitkeep`)
- `docs/FLOW_SETUP.md` — Flow creation and configuration guide

**Files that Phase 3 will MODIFY:**
- `scripts/private/CMMClient.psm1` — Complete `Save-CMMBaseline` with active baseline deactivation
- `CHANGELOG.md` — Add v0.3.0 entry

---

## 4. Key Function Signatures

### Test-ContentModerationCompliance.ps1 (Orchestrator)

```powershell
function Test-ContentModerationCompliance {
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [ValidateSet('Table', 'Json', 'Object')]
        [string]$OutputFormat = 'Table',
        [string[]]$IncludeEnvironments,
        [string[]]$ExcludeEnvironments,
        [switch]$ExcludeSandbox,
        [switch]$ExcludeTrial,
        [switch]$ExcludeDefault,
        [ValidateRange(0, 168)]
        [int]$GracePeriodHours = 48,
        [switch]$IncludeDrafts,
        [switch]$IncludeCompliant,
        [string]$DataverseUrl,
        [string]$DataverseToken,
        [switch]$PersistResults,
        [string]$BaselinePath,
        [int]$Top = 0
    )
```

**Output (Object mode):** Array of compliance result objects with `AgentId`, `AgentName`, `EnvironmentDisplayName`, `Zone`, `CurrentModerationLevel`, `ExpectedModerationLevel`, `IsCompliant`, `Severity`, `RegulatoryContext`, `AgentStatus`

**Output (Json mode):** `{ metadata: { TotalAgentsScanned, TotalEnvironments, CompliantAgents, ViolationCount, CriticalCount, HighCount, MediumCount, WarningCount, ScanTimestamp, DryRun, OverallStatus }, results: [...] }`

### CMMClient.psm1 Key Functions

```powershell
# Existing — needs enhancement for per-agent active baseline query + deactivation
function Save-CMMBaseline {
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory)][string]$EnvironmentGuid,
        [Parameter(Mandatory)][string]$EnvironmentName,
        [Parameter(Mandatory)][string]$Zone,
        [Parameter(Mandatory)][string]$AgentId,
        [Parameter(Mandatory)][string]$AgentName,
        [Parameter(Mandatory)][string]$ModerationLevel,
        [string]$CapturedBy,
        [string]$RawJson
    )
    # Currently: writes baseline record but does NOT deactivate prior active baseline
    # Needs: query active baseline for this AgentId, PATCH fsi_is_active=false, then POST new
```

```powershell
# Existing — fully functional
function Get-CMMLastValidation {
    [CmdletBinding()]
    param([int]$Top = 1)
    # Queries fsi_moderationvalidationhistory ordered by fsi_validation_time desc
    # Returns PSCustomObject with Name, RunId, OverallStatus, ViolationCount, TotalAgents, SummaryJson, Timestamp
```

```powershell
# Existing — queries baselines by environment
function Get-ModerationBaseline {
    [CmdletBinding()]
    param([string]$EnvironmentId)
    # Queries fsi_moderationbaselines with statecode=0 filter
    # Needs: add -AgentId filter for per-agent drift detection
```

### Get-AgentModerationSettings.ps1

```powershell
# Script-level function — enumerates agents across environments
# Output per agent: AgentId, AgentName, AgentStatus, ContentModerationLevel,
#   EnvironmentId, EnvironmentDisplayName, EnvironmentType, Zone, DataverseUrl,
#   LastPublished, RetrievedAt
```

### Compare-ModerationCompliance.ps1

```powershell
# Pipeline-enabled function (begin/process/end)
# Input: -AgentSettings (from pipeline)
# Output: AgentId, AgentName, EnvironmentDisplayName, EnvironmentId, Zone,
#   CurrentModerationLevel, ExpectedModerationLevel, IsCompliant, Severity,
#   RegulatoryContext, AgentStatus
```

---

## 5. Proven Automation Pattern from AAM v6

### AAM Runbook Wrapper Pattern (Start-AccessValidationRunbook.ps1 — 525 lines)

```
Structure:
1. #Requires -Version 7.0 / #Requires -Modules MSAL.PS
2. Parameters: TenantId, ClientId, CertificateThumbprint, DataverseUrl, ExcludeSandbox, ExcludeTrial, GracePeriodHours
3. Helper functions: Get-DriftDirection, Get-SharingDriftDirection (inline)
4. Certificate-based MSAL auth → Dataverse token
5. Connect AAMClient, read Dataverse env vars for operational overrides
6. Call Test-AgentAccessCompliance -PersistResults -DataverseUrl -DataverseToken -OutputFormat Object
7. Per-environment drift detection: query active baselines → compare 3 settings → classify direction
8. Build violations array from scan result
9. Determine AlertRequired, AlertSeverity, Reason
10. Build enriched ZoneSummary with Total/Compliant/Violations per zone
11. Emit single JSON to pipeline (ConvertTo-Json -Depth 10)
12. Error catch → emit error JSON with AlertRequired=true, AlertSeverity="Error"
```

**Key design decisions from AAM:**
- NO Write-Host — only Write-Verbose for diagnostics, JSON to pipeline
- Scans all zones in single run (unlike SSC which is per-zone)
- Enriches ZoneSummary from flat counts to `{ Total, Compliant, Violations }` objects for flow/card consumption
- Fail-open on Dataverse errors: `HasDrift=false, IsFirstRun=true`
- `AlertRequired` = true when violations detected OR drift detected
- `AlertSeverity` = highest severity from violations

### AAM Adaptive Card Pattern (adaptive-card-access-alert.json — 358 lines)

```
Structure (Adaptive Card schema 1.4):
├── Container: Header — "[ALERT] Agent Access Governance Monitor" + ${AlertSeverity}
│   └── Timestamp (isSubtle)
├── Container: Run Summary — FactSet with Status, Total Environments, Severity, Reason
├── Container: Zone Summary — ColumnSet table (Zone/Compliant/Total × 3 rows)
├── Container: Violations — ${ViolationSummary} + FactSet (Env, Zone, Setting, Expected, Actual, Severity)
├── Container: Drift Detection — FactSet (Drifted Environments, Env, Setting, Baseline, Current, Direction)
└── Actions: "View in Power Platform Admin", "Run Manual Check", "View Documentation"

Placeholder convention: ${variableName}
Severity drives accent: Critical=attention(red), High=warning(orange), Info=accent(blue)
```

### AAM Power Automate Flow Pattern (access-validation-flow.json — 605 lines)

```
Trigger: Recurrence (Daily, 6:00 AM UTC)

Variables (10 Initialize_Variable actions):
├── DataverseUrl, TenantId, ClientId, CertificateThumbprint
├── SubscriptionId, ResourceGroup, AutomationAccount
├── TeamsGroupId, TeamsChannelId, ComplianceDistributionList

Scope_Try:
├── Create_Automation_Job (Azure Automation connector)
├── Wait_For_Job (Until loop: Delay 30s → Get_Job_Status, max 2h)
├── Check_Job_Failed → Send_Job_Failure_Email → Terminate_Failed
├── Get_Job_Output
├── Parse_Results (JSON schema matching runbook output)
├── Write_Validation_History (HTTP POST to Dataverse, BEFORE alerting)
├── Check_Alert_Required (runAfter Write_Validation_History [Succeeded, Failed])
│   ├── If true:
│   │   ├── Check_Severity_For_Teams
│   │   │   ├── Critical/Failed/Error → Post_Teams_Card (adaptive card with replace())
│   │   │   └── else → (skip Teams)
│   │   └── Send_Alert_Email (always for alert-required)
│   └── If false: (no action)

Scope_Catch (runAfter Scope_Try [Failed, Skipped, TimedOut]):
└── Send_Critical_Error_Email

Connection references: azureautomation, teams, office365
```

**Critical AAM lesson applied:** `Write_Validation_History` runs BEFORE `Check_Alert_Required` to ensure audit trail exists even if alert delivery fails. `Check_Alert_Required` has `runAfter: ["Succeeded", "Failed"]` on Write_Validation_History so alerting proceeds even if Dataverse write fails.

### AAM Baseline Capture Pattern (Invoke-AccessBaselineCapture.ps1 — 402 lines)

```
Structure:
1. #Requires -Version 5.1 (supports both interactive and certificate auth)
2. Parameters: TenantId, ClientId, CertificateThumbprint, DataverseUrl, Zone, EnvironmentGuid, ExcludeSandbox, CapturedBy, Interactive
3. Parameter validation (CertThumb required unless -Interactive; -Zone and -EnvironmentGuid mutually exclusive)
4. MSAL token acquisition (interactive or certificate)
5. Connect AAMClient
6. Call Get-EnvironmentAccessSettings for live settings
7. Filter by -Zone or -EnvironmentGuid
8. WhatIf preview (formatted console output showing what would be captured)
9. For each environment: build raw JSON, call Save-AAMBaseline, track zone breakdown
10. Emit structured JSON result: CapturedOn, CapturedBy, TotalCaptured, ZoneBreakdown, Environments[]
```

---

## 6. ACV Flow Pattern (Reference)

The ACV solution has two flow JSON files in `src/`:
- `environment-validation-flow.json` (509 lines)
- `tenant-validation-flow.json`

Both follow the same pattern as AAM:
- Daily Recurrence trigger (ACV uses 7:00 AM UTC)
- Same Initialize_Variable chain (DataverseUrl, TenantId, ClientId, CertThumb, SubscriptionId, ResourceGroup, AutomationAccount, TeamsGroupId, TeamsChannelId, ComplianceDistributionList)
- Same Scope_Try/Scope_Catch structure
- Same Azure Automation connector for runbook execution
- Same Parse_Results → Write_Validation_History → Check_Alert_Required flow

This confirms the automation pattern is stable across 3 solutions (SSC → ACV → AAM) and can be confidently applied to CMM.

---

## 7. CMM-Specific Design Decisions

### Drift Detection: Agent-Level vs Environment-Level

| Aspect | AAM (v6) | CMM (v7) |
|--------|----------|----------|
| **What drifts** | 3 environment-level access settings | Per-agent content moderation level |
| **Granularity** | ~10-50 environments | ~10-500 agents |
| **Settings compared** | `bot-limitSharingMode`, `bot-authoringSharingDisabled`, `bot-publishedBotLimitSharingMode` | `ContentModerationLevel` (Low/Medium/High) |
| **Baseline storage** | `fsi_AccessBaseline` (per-environment) | `fsi_ModerationBaseline` (per-agent) |
| **Drift direction** | Weakened (more permissive) / Strengthened / Changed | Weakened (level lowered from High→Medium or High→Low or Medium→Low) / Strengthened / Changed |
| **Severity on drift** | Zone-based (Zone 3 drift → Critical) | Zone-based (Zone 3 agent drift → Critical) plus severity from baseline |
| **Baseline key** | EnvironmentGuid (unique per environment) | AgentId (unique per agent) |
| **New agent detection** | New environment with no baseline → IsFirstRun | New agent with no baseline → IsFirstRun |

**CMM drift detection approach:**
1. For each agent in the scan results, query active baseline from `fsi_moderationbaselines` by AgentId
2. Compare current `ContentModerationLevel` to baseline `fsi_moderation_level`
3. If level differs: classify direction
   - **Weakened:** Level decreased (High→Medium, High→Low, Medium→Low)
   - **Strengthened:** Level increased (Low→Medium, Low→High, Medium→High)
   - **Changed:** Unexpected transition
4. No active baseline → `IsFirstRun=true` for that agent (skip drift detection)
5. On Dataverse query failure → fail open (`HasDrift=false, IsFirstRun=true`)

**Moderation level ordering (most restrictive first):**
```
High (1) → Medium (2) → Low (3)
```
If `currentRank > baselineRank` → Weakened; `currentRank < baselineRank` → Strengthened.

### Runbook Output Schema (CMM-Specific)

```json
{
  "RunType": "ModerationValidation",
  "Timestamp": "2026-02-10T06:00:00Z",
  "TotalAgents": 42,
  "TotalEnvironments": 8,
  "OverallStatus": "Failed",
  "Reason": "3 agents have content moderation violations",
  "ZoneSummary": {
    "Zone1": { "Total": 15, "Compliant": 15, "Violations": 0 },
    "Zone2": { "Total": 18, "Compliant": 16, "Violations": 2 },
    "Zone3": { "Total": 9, "Compliant": 8, "Violations": 1 }
  },
  "Violations": [
    {
      "AgentId": "bot-guid-1",
      "AgentName": "Trading Assistant",
      "EnvironmentId": "env-guid-1",
      "EnvironmentName": "Trading-Z3-Prod",
      "Zone": "Zone3",
      "ExpectedModerationLevel": "High",
      "ActualModerationLevel": "Low",
      "Severity": "Critical",
      "RegulatoryContext": "FINRA 3110 - Unmoderated customer-facing AI agent"
    }
  ],
  "Drift": {
    "HasDrift": true,
    "IsFirstRun": false,
    "DriftedAgents": 1,
    "Details": [
      {
        "AgentId": "bot-guid-1",
        "AgentName": "Trading Assistant",
        "EnvironmentName": "Trading-Z3-Prod",
        "Zone": "Zone3",
        "BaselineLevel": "High",
        "CurrentLevel": "Low",
        "Direction": "Weakened"
      }
    ]
  },
  "AlertRequired": true,
  "AlertSeverity": "Critical"
}
```

**Key differences from AAM output:**
- `TotalAgents` instead of `TotalEnvironments` as primary count
- `TotalEnvironments` still included as secondary metric
- Violations contain `AgentId`, `AgentName`, `ExpectedModerationLevel`, `ActualModerationLevel` (agent-specific)
- Drift.Details contain agent-level fields instead of environment-level settings
- RunType = "ModerationValidation" instead of "AccessValidation"

### Baseline Capture Design (CMM-Specific)

`Invoke-ModerationBaselineCapture.ps1` needs to:
1. Run `Get-AgentModerationSettings` to capture live moderation levels for all (or targeted) agents
2. For each agent, call `Save-CMMBaseline` to write to `fsi_moderationbaselines`
3. `Save-CMMBaseline` must deactivate any existing active baseline for that AgentId before writing new one
4. Store: AgentId, AgentName, EnvironmentGuid, EnvironmentName, Zone, ModerationLevel, CapturedBy, RawJson
5. Support `-Zone` parameter to capture only agents in a specific zone
6. Support `-EnvironmentGuid` to capture agents in a single environment
7. Support `-WhatIf` for preview mode
8. Support both interactive and certificate-based authentication

### Save-CMMBaseline Enhancement Required

The current `Save-CMMBaseline` writes a new baseline record but does NOT deactivate prior active baselines for the same agent. This needs to be enhanced:

```powershell
# BEFORE write:
# 1. Query fsi_moderationbaselines: $filter=fsi_is_active eq true and fsi_agent_id eq '{AgentId}'
# 2. If found, PATCH fsi_is_active = false (deactivate previous)
# THEN:
# 3. POST new baseline record with fsi_is_active = true
```

### Get-ModerationBaseline Enhancement Required

The current function queries by `EnvironmentId` only. For drift detection, it needs to support per-agent queries:

```powershell
# Add -AgentId parameter
# When provided: $filter += " and fsi_agent_id eq '{AgentId}' and fsi_is_active eq true"
# This enables: "get the active baseline for agent X"
```

### Adaptive Card Design (CMM-Specific)

CMM adaptive card should show:
- **Header:** "Content Moderation Governance Monitor" + severity badge
- **Run summary:** Total agents, total environments, violations, drift count
- **Zone breakdown table:** Zone 1/2/3 with compliant vs violation counts (agents, not environments)
- **Violation details:** Agent name, environment, zone, expected vs actual moderation level, severity, regulatory context
- **Drift indicators:** Baseline vs current moderation level for drifted agents
- **Action buttons:** "View in Power Platform Admin" / "Run Manual Check" / "View Documentation"

### Power Automate Flow Design (CMM-Specific)

- **Name:** "CMM - Content Moderation Validation"
- **Trigger:** Recurrence (daily, 6:00 AM UTC)
- **Runbook:** `Start-ModerationValidationRunbook`
- **Parse_Results schema:** Matches CMM-specific output schema (TotalAgents, agent-level violations, agent-level drift)
- **Write action:** HTTP POST to `fsi_moderationvalidationhistory` with CMM columns
- **Connection references:** `fsi_cr_dataverse_moderationmonitor`, `fsi_cr_teams_moderationmonitor`, `fsi_cr_office365_moderationmonitor`
- **Alert routing:** Same as AAM (Critical/Failed → Teams + email; High/Warning → email; Passed → none)

---

## 8. Risks and Mitigations

| Risk | Severity | Mitigation |
|------|----------|------------|
| Azure Automation not available in tenant | HIGH | Document prerequisites; provide manual script execution alternative |
| Large agent count slows drift detection (100+ agents × Dataverse queries) | MEDIUM | Batch query baselines for all agents in single OData request with `$filter=fsi_is_active eq true` then match in-memory, rather than per-agent Dataverse calls |
| Teams channel not configured for alerts | MEDIUM | Flow gracefully skips Teams alert when TeamsGroupId/ChannelId env vars are empty |
| No active baseline for agent (first run) | LOW | Return `IsFirstRun=true`, skip drift detection for that agent; use static `moderation-baseline.json` for compliance check |
| Dataverse write failure in flow | MEDIUM | Scope_Catch handles errors; alerting proceeds even if history write fails (`runAfter: [Succeeded, Failed]`) |
| Save-CMMBaseline baseline deactivation race condition | LOW | Single-threaded PowerShell execution; query + patch + post in sequence |
| Bot configuration JSON schema variations | LOW | Already handled by Get-BotModerationLevel with multi-key lookup and normalization map |

### Performance Consideration: Batch Baseline Query

AAM queries one baseline per environment (~10-50 queries). CMM needs per-agent baselines (~50-500 agents). Per-agent Dataverse queries would be slow.

**Recommended approach:** Query ALL active baselines in a single request:
```
GET fsi_moderationbaselines?$filter=fsi_is_active eq true&$select=fsi_agent_id,fsi_moderation_level,fsi_environment_guid,fsi_zone
```
Then build an in-memory hashtable keyed by AgentId for O(1) lookups during drift detection. This is a significant optimization over the AAM pattern.

---

## 9. File Manifest (Phase 3 Creates/Modifies)

### New Files

| File | Repository | Purpose |
|------|------------|---------|
| `scripts/Start-ModerationValidationRunbook.ps1` | FSI-AgentGov-Solutions | Azure Automation runbook wrapper |
| `scripts/Invoke-ModerationBaselineCapture.ps1` | FSI-AgentGov-Solutions | Operator-initiated baseline capture |
| `src/adaptive-card-moderation-alert.json` | FSI-AgentGov-Solutions | Teams adaptive card template |
| `src/moderation-validation-flow.json` | FSI-AgentGov-Solutions | Power Automate flow definition |
| `docs/FLOW_SETUP.md` | FSI-AgentGov-Solutions | Flow setup and configuration guide |

### Modified Files

| File | Repository | Change |
|------|------------|--------|
| `scripts/private/CMMClient.psm1` | FSI-AgentGov-Solutions | Complete Save-CMMBaseline with deactivation; add Get-ActiveModerationBaseline or enhance Get-ModerationBaseline with -AgentId and -ActiveOnly |
| `CHANGELOG.md` | FSI-AgentGov-Solutions | Add v0.3.0 entry |

---

## 10. Recommended Plan Structure

Following the proven AAM v6 pattern exactly:

| Plan | Wave | Content | Est. Duration |
|------|------|---------|---------------|
| 03-01 | 1 | Runbook wrapper + baseline capture + CMMClient enhancements | ~8 min |
| 03-02 | 2 | Adaptive card + flow JSON + FLOW_SETUP.md | ~8 min |
| 03-03 | 3 | Integration verification + drift refinement + CHANGELOG | ~4 min |

---

*Research completed: 2026-02-10*
*Confidence: HIGH — AAM v6 Phase 3 provides a proven and tested pattern across 3 solutions; CMM adaptation is straightforward with the main variation being agent-level vs environment-level granularity*
*Recommended approach: 3 plans across 3 waves following AAM structure exactly, with batch baseline query optimization for agent-level scale*
