# Phase 02 Research: Detection Engine

**Phase:** 02-detection-engine
**Researched:** 2026-02-12
**Status:** Complete

---

## 1. Technical Analysis

### 1.1 Power Automate Flow JSON Pattern

**Reference file:** `src/caa-daily-compliance-flow.json` (1332 lines)

The CAA daily compliance flow establishes the JSON structure pattern that the UASD detector flow must follow.

#### Top-Level Structure

```
{
  "properties": {
    "connectionReferences": { ... },
    "definition": {
      "$schema": "https://schema.management.azure.com/.../workflowdefinition.json#",
      "contentVersion": "1.0.0.0",
      "parameters": { "$connections", "$authentication" },
      "triggers": { ... },
      "actions": { ... }
    },
    "displayName": "...",
    "description": "...",
    "state": "Started"
  },
  "schemaVersion": "1.0.0.0"
}
```

#### Connection References

CAA defines 3 connection references:

| Logical Name | Connector | Source |
|---|---|---|
| `fsi_cr_dataverse_conditionalaccessautomation` | `shared_commondataserviceforapps` | Invoker |
| `fsi_cr_office365_conditionalaccessautomation` | `shared_office365` | Invoker |
| `fsi_cr_teams_conditionalaccessautomation` | `shared_teams` | Invoker |

**UASD needs 2** (from `scripts/create_uasd_connection_references.py`):

| Logical Name | Connector | Purpose |
|---|---|---|
| `fsi_cr_dataverse_sharingdetector` | `shared_commondataserviceforapps` | Dataverse table CRUD |
| `fsi_cr_teams_sharingdetector` | `shared_teams` | Teams adaptive card alerts |

No Office 365 (email) connector — UASD uses Teams-only alerting per the simpler detection scope.

#### Trigger Structure

CAA uses a daily recurrence trigger:

```json
"Recurrence_Daily_0600_UTC": {
  "type": "Recurrence",
  "recurrence": {
    "frequency": "Day",
    "interval": 1,
    "startTime": "2026-01-01T06:00:00Z",
    "timeZone": "UTC",
    "schedule": { "hours": ["6"], "minutes": ["0"] }
  },
  "metadata": { "operationMetadataId": "recurrence-daily-0600" }
}
```

**UASD detector flow** should follow this pattern but with the frequency driven by `fsi_UASD_ScanFrequencyHours` (default 24h). Since environment variables can't dynamically set triggers, the JSON should default to daily (24h) with a note that administrators can adjust the recurrence after import.

#### Variable Initialization Pattern

CAA chains 10 `InitializeVariable` actions in a sequential `runAfter` dependency chain. Each variable:
- Has `type: "InitializeVariable"` with a `variables` array containing one entry
- Uses `runAfter` on the preceding variable to enforce sequential initialization
- Includes a `description` field referencing the environment variable it maps to
- Uses empty string default values (bound to environment variables at deployment)

**UASD needs these variables:**

| Variable | Type | Maps To |
|---|---|---|
| `DataverseUrl` | string | fsi_UASD_DataverseUrl (or reuse existing pattern) |
| `HomeTenantId` | string | fsi_UASD_HomeTenantId |
| `TeamsGroupId` | string | Teams notification target |
| `TeamsChannelId` | string | Teams notification target |
| `ScanRunId` | string | Generated GUID per scan run |
| `ViolationCards` | array | Accumulator for adaptive card elements |
| `TotalAgents` | integer | Counter for scan summary |
| `ViolationCount` | integer | Counter for violations found |

#### Scope_Try / Scope_Catch Error Handling

CAA wraps all main logic in `Scope_Try` (type: "Scope") and catches failures in `Scope_Catch`:

```json
"Scope_Try": {
  "type": "Scope",
  "actions": { /* all main logic */ },
  "runAfter": { "Initialize_LastVariable": ["Succeeded"] }
},
"Scope_Catch": {
  "type": "Scope",
  "actions": { /* error notification */ },
  "runAfter": { "Scope_Try": ["Failed", "TimedOut"] }
}
```

The `Scope_Catch` sends a CRITICAL email notification. UASD should follow this but post to Teams instead (no email connector).

#### HTTP Action Pattern (for BAP API)

CAA uses HTTP actions with managed identity auth for Azure Management API:

```json
"Create_Automation_Job": {
  "type": "Http",
  "inputs": {
    "method": "PUT",
    "uri": "https://management.azure.com/...",
    "headers": { "Content-Type": "application/json" },
    "body": { ... },
    "authentication": {
      "type": "ManagedServiceIdentity",
      "audience": "https://management.azure.com"
    }
  }
}
```

**UASD detector flow** will use HTTP actions targeting `api.bap.microsoft.com` with:
- `authentication.audience`: `https://api.bap.microsoft.com` (Power Platform API)
- `method`: GET (enumerate agents, get principals)
- Response parsing via `ParseJson` actions

#### Dataverse OpenApiConnection Pattern

CAA uses Dataverse connector operations:

```json
"List_Validation_Records": {
  "type": "OpenApiConnection",
  "inputs": {
    "parameters": {
      "entityName": "fsi_capolicyvalidationhistories",
      "$filter": "...",
      "$top": 1
    },
    "host": {
      "apiId": "/providers/Microsoft.PowerApps/apis/shared_commondataserviceforapps",
      "connectionName": "shared_commondataserviceforapps",
      "operationId": "ListRecords"
    }
  }
}
```

For creating records:
```json
"operationId": "CreateRecord",
"parameters": {
  "entityName": "fsi_sharingviolations",
  "item/fsi_field_name": "@{expression}"
}
```

**UASD needs:**
- `ListRecords` on `fsi_agentsharingsettings` (to check existing baselines)
- `ListRecords` on `fsi_approvedsecuritygroups` (to load approved groups for rule evaluation)
- `ListRecords` on `fsi_sharingpolicies` (to load thresholds for EXCESSIVE_INDIVIDUAL rule)
- `ListRecords` on `fsi_sharingexceptions` (to check for active exceptions before creating violations)
- `CreateRecord` on `fsi_agentsharingsettings` (upsert current state)
- `CreateRecord` on `fsi_sharingviolations` (create violations)

#### Teams Adaptive Card Posting

CAA posts cards via the Teams connector:

```json
"Post_Teams_Alert": {
  "type": "OpenApiConnection",
  "inputs": {
    "parameters": {
      "poster": "Flow bot",
      "location": "Channel",
      "body/recipient/groupId": "@variables('TeamsGroupId')",
      "body/recipient/channelId": "@variables('TeamsChannelId')",
      "body/messageBody": "@{string(outputs('Compose_Adaptive_Card'))}"
    },
    "host": {
      "apiId": "/providers/Microsoft.PowerApps/apis/shared_teams",
      "connectionName": "shared_teams",
      "operationId": "PostCardToConversation"
    }
  }
}
```

The card is first composed via a `Compose` action, then stringified for the Teams API.

#### Action Dependency Chain (runAfter)

CAA establishes dependencies via `runAfter`:
- Sequential: `"runAfter": { "PreviousAction": ["Succeeded"] }`
- Multiple dependencies: `"runAfter": { "ActionA": ["Succeeded"], "ActionB": ["Succeeded"] }`
- First action in scope: `"runAfter": {}`
- Error catch: `"runAfter": { "Scope_Try": ["Failed", "TimedOut"] }`

#### Foreach Pattern (for iterating agents)

CAA iterates results with:

```json
"Apply_to_Each_Violation": {
  "type": "Foreach",
  "foreach": "@body('Parse_Results')?['Violations']",
  "actions": { ... },
  "operationOptions": "Sequential"
}
```

UASD will need:
1. `Apply_to_Each_Environment` — iterate environments from BAP
2. `Apply_to_Each_Agent` (nested) — iterate agents per environment
3. `Apply_to_Each_Principal` (nested) — evaluate each principal against rules

### 1.2 Adaptive Card Template Pattern

**Reference file:** `src/adaptive-card-caa-alert.json` (492 lines)

#### Card Structure

```
AdaptiveCard v1.4
├── headerSection (Container, severity-styled)
│   ├── Title: "[ALERT] ... — ${OverallStatus}"
│   ├── Subtitle: "Solution Name · ${CheckedAt}"
│   └── Severity Badge: "${OverallSeverityBadge}"
├── runSummarySection (Container)
│   └── ColumnSet with 2 FactSets (counts, rates)
├── zoneComplianceSection (Container)
│   └── Zone 1/2/3 rows with pass counts + severity badge
├── violationsSection (Container)
│   ├── Header: "Violations (${ViolationCount})"
│   └── violationItem template (repeating)
│       ├── ColumnSet: Type | Name | Zone
│       └── FactSet: Expected, Actual, Severity, Regulatory
├── driftSection (Container)
│   ├── Header: "Drift Detection (${DriftCount})"
│   └── driftItem template (repeating)
└── Actions: View in Portal, Run Manual Check, View Documentation
```

#### Key Conventions

1. **Severity styling** uses container `style` property bound to severity:
   - CRITICAL → `attention` (red)
   - HIGH → `warning` (orange)
   - WARNING → `accent` (blue)
   - Passed → `good` (green)

2. **Severity colors** for TextBlock elements: `Attention`, `Warning`, `Accent`, `Good`

3. **Template variables** use `${VariableName}` syntax in the standalone template

4. **In-flow card composition** replaces `${}` with `@{expression}` Power Automate expressions

5. **`_metadata` section** at card bottom documents:
   - Template name, version, solution name
   - Severity color/style mappings
   - Template variable inventory (scalar, perViolation, perDrift)
   - Flow integration notes

6. **`msteams: { "width": "Full" }`** for full-width rendering

7. **Action buttons** use `Action.OpenUrl` pointing to relevant portals and documentation

#### UASD Adaptive Card Requirements

The UASD card should follow this pattern with UASD-specific sections:

| Section | UASD Equivalent | Variables |
|---------|-----------------|-----------|
| headerSection | Same pattern | `[ALERT] Agent Sharing Violation — ${OverallStatus}` |
| runSummarySection | Scan Summary | TotalAgents, TotalViolations, EnvironmentsScanned, ScanRunId |
| zoneComplianceSection | Not needed (agents aren't zone-classified in UASD) | — |
| violationsSection | Sharing Violations | ViolationType, AgentName, EnvironmentName, Severity, PrincipalDetails |
| driftSection | Not needed (UASD doesn't track drift) | — |
| Actions | PPAC Portal, Run Audit Script, View Documentation | — |

### 1.3 PowerShell Governance Script Pattern

**Reference file:** `scripts/governance/Invoke-HardeningBaselineCheck.ps1` (630 lines)

#### Standard Header Format

```powershell
<#
.SYNOPSIS
    One-line description of what the script does.

.DESCRIPTION
    Multi-line detailed description including:
    - What items/checks are covered
    - API methods used
    - Zone-specific behavior

.PARAMETER OutputFormat
    Output format for results. Valid values: Table, JSON, Object. Default: Table.

.PARAMETER OutputPath
    Optional file path to export JSON results.

.PARAMETER IncludeEvidence
    When specified, computes SHA-256 integrity hash over results.

.EXAMPLE
    .\ScriptName.ps1
    Brief description.

.EXAMPLE
    .\ScriptName.ps1 -OutputFormat JSON -OutputPath .\evidence\output.json -IncludeEvidence
    Full invocation with evidence.

.OUTPUTS
    PSCustomObject with Metadata, Summary, Checks, and Gaps properties.

.NOTES
    Part of the FSI Agent Governance — Solution Name.
    Controls: X.X, Y.Y
    Version: 1.0.0
    Requires: Module requirements
#>

#Requires -Version 7.0
#Requires -Modules @{ ModuleName = 'Microsoft.PowerApps.Administration.PowerShell'; ModuleVersion = '2.0.0' }
```

#### Parameter Block

```powershell
[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter()]
    [ValidateSet('Table', 'JSON', 'Object')]
    [string]$OutputFormat = 'Table',

    [Parameter()]
    [string]$OutputPath,

    [Parameter()]
    [string[]]$EnvironmentFilter,

    [Parameter()]
    [switch]$IncludeEvidence
)
```

**UASD `Invoke-SharingAudit.ps1` parameters** should include:
- `-OutputFormat` (Table/JSON/Object) — standard
- `-OutputPath` — standard
- `-IncludeEvidence` — standard SHA-256 hash
- `-EnvironmentFilter` — optional scope limiter
- `-HomeTenantId` — required for CROSS_TENANT_ACCESS rule (or read from env var)

#### Helper Function Pattern

The hardening baseline script uses helper functions with `[CmdletBinding()]` and `[Parameter(Mandatory)]`:

```powershell
function New-CheckResult {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][int]$ItemNumber,
        [Parameter(Mandatory)][string]$Setting,
        [Parameter(Mandatory)][ValidateSet('Pass', 'Fail', 'Skip', 'Warning')][string]$Status,
        [Parameter()][string]$Expected,
        [Parameter()][string]$Actual,
        [Parameter()][string]$Environment,
        [Parameter()][string]$Message
    )
    [PSCustomObject]@{
        ItemNumber  = $ItemNumber
        Setting     = $Setting
        Status      = $Status
        Expected    = $Expected
        Actual      = $Actual
        Environment = $Environment
        Message     = $Message
    }
}
```

**UASD equivalent:** `New-ViolationResult` helper with fields matching the 5 violation types.

#### Banner Pattern

```powershell
Write-Host "`n╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host   "║  FSI Agent Governance — Solution Name                   ║" -ForegroundColor Cyan
Write-Host   "╚══════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan
```

#### WhatIf Support

```powershell
if (-not $PSCmdlet.ShouldProcess("Power Platform tenant", "Run sharing audit")) {
    Write-Verbose "WhatIf: Would scan agent sharing principals across environments"
    return
}
```

#### Results Object Structure

```powershell
$results = [PSCustomObject]@{
    Metadata = [PSCustomObject]@{
        CheckedAt           = $startTime
        ScriptVersion       = '1.0.0'
        EnvironmentsScanned = $envCount
        DurationSeconds     = [math]::Round($duration, 2)
        IntegrityHash       = $null
    }
    Summary = [PSCustomObject]@{
        TotalChecks   = $totalChecks
        Passed        = $passCount
        Failed        = $failCount
        Skipped       = $skipCount
        OverallStatus = if ($failCount -eq 0) { 'Passed' } else { 'ViolationsFound' }
    }
    Checks = $allChecks.ToArray()
    Gaps   = $gaps.ToArray()
}
```

#### SHA-256 Evidence Hash Pattern

```powershell
if ($IncludeEvidence) {
    $resultsJson = $results | ConvertTo-Json -Depth 10 -Compress
    $hashBytes = [System.Security.Cryptography.SHA256]::Create().ComputeHash(
        [System.Text.Encoding]::UTF8.GetBytes($resultsJson)
    )
    $results.Metadata.IntegrityHash = [BitConverter]::ToString($hashBytes) -replace '-'
}
```

#### Output Switch Pattern

Table, JSON, and Object output modes with optional file export and parent directory auto-creation.

#### Check Group Organization

Checks are organized into labeled groups with `Write-Verbose` progress messages and try/catch per group:

```powershell
# ═══════════════════════════════════════════════════════════════════════
# Check Group N: Description (Items X-Y)
# ═══════════════════════════════════════════════════════════════════════
Write-Verbose "Check Group N: Description..."
try { ... } catch { ... }
```

### 1.4 UASD Dataverse Schema Context

**Reference file:** `scripts/create_uasd_dataverse_schema.py` (844 lines)

#### Tables the Detection Engine Targets

| Table | Entity Set Name | Detection Engine Role |
|-------|----------------|----------------------|
| `fsi_AgentSharingSetting` | `fsi_agentsharingsettings` | **Write** — upsert current sharing state per agent |
| `fsi_SharingViolation` | `fsi_sharingviolations` | **Write** — create violations when rules are violated |
| `fsi_ApprovedSecurityGroup` | `fsi_approvedsecuritygroups` | **Read** — load approved groups for UNAPPROVED_GROUP rule |
| `fsi_SharingPolicy` | `fsi_sharingpolicies` | **Read** — load thresholds for EXCESSIVE_INDIVIDUAL rule |
| `fsi_SharingException` | `fsi_sharingexceptions` | **Read** — check for active exceptions before creating violations |

#### Option Set Values for Violation Rules

**`fsi_UASD_violationtype`** — maps 1:1 to the 5 rules:

| Value | Label | Rule |
|-------|-------|------|
| 0 | ORG_WIDE_SHARING | principal type = Organization |
| 1 | PUBLIC_INTERNET_LINK | principal with public/anonymous scope |
| 2 | UNAPPROVED_GROUP | group principal not in fsi_ApprovedSecurityGroup |
| 3 | EXCESSIVE_INDIVIDUAL | individual count > fsi_SharingPolicy.max_individual_shares |
| 4 | CROSS_TENANT_ACCESS | principal tenant ≠ HomeTenantId |

**`fsi_UASD_sharingscope`** — derived from BAP API principal type:

| Value | Label | BAP Principal Type |
|-------|-------|--------------------|
| 0 | Individual | `type = User` |
| 1 | SecurityGroup | `type = Group` |
| 2 | Organization | `type = Organization` |
| 3 | Public | `type` with anonymous/public scope |

**`fsi_UASD_violationstatus`** — new violations always created as `Open` (value 0):

| Value | Label | When Used |
|-------|-------|-----------|
| 0 | Open | Detection engine creates violations with this status |
| 1 | Remediated | Set by remediation flow after successful PATCH |
| 2 | Exception_Granted | Set when active exception covers the violation |
| 3 | False_Positive | Set manually by admin |

**`fsi_acv_severity`** — shared option set, mapped from spec severity:

| Spec Severity | Option Set Value | Label |
|---------------|-----------------|-------|
| Critical | 4 | Failed |
| High | 5 | Error |
| Medium | 2 | Warning |
| Low | 3 | GracePeriod |

#### Key Columns for Detection Logic

**fsi_AgentSharingSetting columns:**
- `fsi_agent_id` (String, 100, required) — BAP agent/bot ID
- `fsi_agent_name` (String, 200, required) — display name for alerts
- `fsi_environment_id` (String, 100, required) — environment scope
- `fsi_environment_name` (String, 200) — for human-readable output
- `fsi_sharing_scope` (Picklist → `fsi_UASD_sharingscope`, required) — classified sharing level
- `fsi_principal_count` (Integer) — total principal count
- `fsi_principals_json` (Memo) — raw BAP principal array (audit trail)
- `fsi_auth_mode` (Picklist → `fsi_UASD_authmode`) — agent authentication mode
- `fsi_last_scanned` (DateTime, required) — scan timestamp

**fsi_SharingViolation columns:**
- `fsi_violation_name` (String, 256, required) — formatted: `{ViolationType} — {AgentName} ({EnvName})`
- `fsi_agent_id`, `fsi_agent_name`, `fsi_environment_id` — inline agent identity
- `fsi_violation_type` (Picklist → `fsi_UASD_violationtype`, required)
- `fsi_violation_status` (Picklist → `fsi_UASD_violationstatus`, required) — always `Open` (0) at creation
- `fsi_severity` (Picklist → `fsi_acv_severity`, required) — per-rule severity
- `fsi_description` (Memo) — human-readable violation description
- `fsi_evidence_json` (Memo) — serialized principal evidence
- `fsi_evidence_hash` (String, 64) — SHA-256 of evidence JSON
- `fsi_detected_at` (DateTime, required) — detection timestamp
- `fsi_scan_run_id` (String, 100) — links to scan batch

**fsi_ApprovedSecurityGroup columns (read by UNAPPROVED_GROUP rule):**
- `fsi_entraid_group_id` (String, 100, required) — Entra group GUID to match against
- `fsi_zone` (Picklist → `fsi_acv_zone`, required) — zone scope
- `fsi_is_active` (Boolean, default true) — only active groups are approved

**fsi_SharingPolicy columns (read by EXCESSIVE_INDIVIDUAL rule):**
- `fsi_max_individual_shares` (Integer, required) — threshold (default: 100)
- `fsi_governance_zone` (Picklist → `fsi_acv_zone`, required)
- `fsi_is_active` (Boolean, default true) — only active policies apply

---

## 2. Architecture Decisions

### 2.1 Detection Flow Architecture

**Decision:** The UASD detector flow performs all detection inline (HTTP → evaluate → write) rather than delegating to an external runbook.

**Rationale:** CAA delegates to Azure Automation because it runs complex PowerShell logic. UASD detection is simpler — enumerate agents via BAP API, evaluate 5 rules against Dataverse reference data, write violations. This fits natively in Power Automate without an external compute dependency.

**Flow skeleton:**

```
Trigger (Recurrence) →
  Initialize Variables →
  Scope_Try:
    Generate_Scan_Run_Id →
    Load_Approved_Groups (Dataverse ListRecords) →
    Load_Sharing_Policy (Dataverse ListRecords) →
    List_Environments (HTTP → BAP API) →
    Apply_to_Each_Environment:
      List_Agents_In_Environment (HTTP → BAP API) →
      Apply_to_Each_Agent:
        Get_Agent_Principals (HTTP → BAP API) →
        Upsert_Agent_Sharing_Setting (Dataverse) →
        Evaluate_Rules (Compose/Condition actions):
          Rule 1: ORG_WIDE_SHARING →
          Rule 2: PUBLIC_INTERNET_LINK →
          Rule 3: UNAPPROVED_GROUP →
          Rule 4: EXCESSIVE_INDIVIDUAL →
          Rule 5: CROSS_TENANT_ACCESS →
        For each violation → Check_Active_Exception → Create_Violation_Record →
        Append_Violation_Card →
    Check_Violations_Found →
      Compose_Adaptive_Card →
      Post_Teams_Alert →
  Scope_Catch:
    Post_Error_Notification →
```

### 2.2 Exception-Aware Violation Creation

**Decision:** Before creating a violation, the flow checks `fsi_SharingException` for an active, non-expired exception matching the agent + violation type. If found, skip violation creation.

**Implementation:** Dataverse `ListRecords` with filter:
```
fsi_agent_id eq '{agentId}' and fsi_violation_type eq {violationType} and fsi_exception_status eq 1 and fsi_expires_at ge {utcNow()}
```

### 2.3 Duplicate Violation Prevention

**Decision:** Check for existing `Open` violations before creating new ones to prevent duplicate rows on consecutive scan runs.

**Implementation:** Dataverse `ListRecords` with filter:
```
fsi_agent_id eq '{agentId}' and fsi_violation_type eq {violationType} and fsi_violation_status eq 0
```

If a matching open violation exists, skip creation.

### 2.4 BAP API Authentication in Flow

**Decision:** Use Managed Service Identity authentication in HTTP actions targeting `api.bap.microsoft.com`.

**Alternative considered:** Custom connector. Rejected — HTTP actions are simpler and follow the CAA pattern.

```json
"authentication": {
  "type": "ManagedServiceIdentity",
  "audience": "https://api.bap.microsoft.com"
}
```

### 2.5 PowerShell Script Scope

**Decision:** `Invoke-SharingAudit.ps1` implements the same 5 violation rules as the flow but uses `Microsoft.PowerApps.Administration.PowerShell` and direct REST calls rather than Power Automate connectors.

**Rationale:** On-demand audit capability for ad-hoc investigations, environment-scoped checks, and situations where the flow isn't deployed yet.

**Does NOT:** Write to Dataverse. Output is console/JSON/file only. Dataverse writes are the flow's responsibility.

---

## 3. Pattern References

### 3.1 Flow JSON Patterns

| Pattern | CAA Reference | UASD Application |
|---------|--------------|-------------------|
| Connection references | `src/caa-daily-compliance-flow.json` lines 3-25 | 2 refs: `fsi_cr_dataverse_sharingdetector`, `fsi_cr_teams_sharingdetector` |
| Recurrence trigger | `src/caa-daily-compliance-flow.json` lines 36-57 | Daily recurrence, adjustable post-import |
| Variable initialization chain | `src/caa-daily-compliance-flow.json` lines 59-236 | 8 variables with sequential runAfter |
| Scope_Try/Scope_Catch | `src/caa-daily-compliance-flow.json` lines 238-240, 1294-1325 | Same pattern, Teams-only error notification |
| HTTP action with MSI auth | `src/caa-daily-compliance-flow.json` lines 256-283 | 3 BAP API endpoints |
| Dataverse ListRecords | `src/caa-daily-compliance-flow.json` lines 843-856 | Load approved groups, policies, exceptions |
| Dataverse CreateRecord | `src/caa-daily-compliance-flow.json` lines 862-894 | Create violation and sharing setting records |
| Foreach with Sequential option | `src/caa-daily-compliance-flow.json` lines 616-712 | Iterate environments, agents, principals |
| Adaptive card Compose + Post | `src/caa-daily-compliance-flow.json` lines 894-1191, 1195-1217 | Compose UASD card + post to Teams |
| Severity badge computation | `src/caa-daily-compliance-flow.json` lines 544-561 | Map violation severity to emoji badges |

### 3.2 Adaptive Card Patterns

| Pattern | CAA Reference | UASD Application |
|---------|--------------|-------------------|
| Header with severity style | `src/adaptive-card-caa-alert.json` lines 6-43 | `[ALERT] Agent Sharing Violation — ${Status}` |
| FactSet summary | `src/adaptive-card-caa-alert.json` lines 62-112 | Scan summary facts |
| Repeating violation items | `src/adaptive-card-caa-alert.json` lines 239-302 | Sharing violation items |
| Action buttons | `src/adaptive-card-caa-alert.json` lines 395-417 | PPAC, audit script, docs links |
| `_metadata` section | `src/adaptive-card-caa-alert.json` lines 421-492 | Template documentation |
| `msteams.width: "Full"` | `src/adaptive-card-caa-alert.json` line 419 | Full-width rendering |

### 3.3 PowerShell Patterns

| Pattern | Hardening Baseline Reference | UASD Application |
|---------|------------------------------|-------------------|
| Comment-based help header | `scripts/governance/Invoke-HardeningBaselineCheck.ps1` lines 1-59 | Same 7-section format |
| `#Requires` statements | `scripts/governance/Invoke-HardeningBaselineCheck.ps1` lines 60-61 | Same modules + version |
| `[CmdletBinding(SupportsShouldProcess)]` | `scripts/governance/Invoke-HardeningBaselineCheck.ps1` line 63 | Same |
| Parameter block with `ValidateSet` | `scripts/governance/Invoke-HardeningBaselineCheck.ps1` lines 64-79 | Add `-HomeTenantId` param |
| ASCII banner | `scripts/governance/Invoke-HardeningBaselineCheck.ps1` lines 82-84 | `FSI Agent Governance — Sharing Audit` |
| WhatIf preview | `scripts/governance/Invoke-HardeningBaselineCheck.ps1` lines 87-90 | Same pattern |
| `New-CheckResult` helper | `scripts/governance/Invoke-HardeningBaselineCheck.ps1` lines 94-114 | `New-ViolationResult` helper |
| Check group organization | `scripts/governance/Invoke-HardeningBaselineCheck.ps1` lines 119-400+ | 5 violation rule groups |
| Results aggregation object | `scripts/governance/Invoke-HardeningBaselineCheck.ps1` lines 499-518 | Same structure: Metadata, Summary, Violations, Findings |
| SHA-256 evidence hash | `scripts/governance/Invoke-HardeningBaselineCheck.ps1` lines 521-527 | Identical pattern |
| Console summary banner | `scripts/governance/Invoke-HardeningBaselineCheck.ps1` lines 530-540 | Scan summary with counts |
| Output format switch | `scripts/governance/Invoke-HardeningBaselineCheck.ps1` lines 543-580 | Table/JSON/Object with file export |

---

## 4. Violation Rule Mapping to Dataverse

### Rule 1: ORG_WIDE_SHARING

| Aspect | Value |
|--------|-------|
| **Detection logic** | Any principal in agent's sharing list with `type = Organization` |
| **BAP API field** | Principal array → filter where `type == "Organization"` |
| **Violation type** | `fsi_UASD_violationtype` = 0 (ORG_WIDE_SHARING) |
| **Severity** | Critical → `fsi_acv_severity` = 4 (Failed) |
| **Evidence** | Full principals JSON for the agent |
| **Description format** | `Agent '{name}' in environment '{env}' is shared with the entire organization` |

### Rule 2: PUBLIC_INTERNET_LINK

| Aspect | Value |
|--------|-------|
| **Detection logic** | Any principal with public/anonymous scope (e.g., `type = "Public"` or unauthenticated access) |
| **BAP API field** | Principal array → filter for public/anonymous markers |
| **Violation type** | `fsi_UASD_violationtype` = 1 (PUBLIC_INTERNET_LINK) |
| **Severity** | Critical → `fsi_acv_severity` = 4 (Failed) |
| **Evidence** | Public principal details |
| **Description format** | `Agent '{name}' in environment '{env}' is accessible via public internet link` |
| **Note** | May be auto-remediated when `fsi_UASD_AutoRemediatePublicLink = true` |

### Rule 3: UNAPPROVED_GROUP

| Aspect | Value |
|--------|-------|
| **Detection logic** | Group principal whose ID is NOT in `fsi_ApprovedSecurityGroup` (where `fsi_is_active = true`) |
| **BAP API field** | Principal array → filter `type == "Group"` → check group ID against approved list |
| **Dataverse query** | `fsi_approvedsecuritygroups?$filter=fsi_is_active eq true` → collect `fsi_entraid_group_id` values |
| **Violation type** | `fsi_UASD_violationtype` = 2 (UNAPPROVED_GROUP) |
| **Severity** | High → `fsi_acv_severity` = 5 (Error) |
| **Evidence** | Unapproved group ID + name |
| **Description format** | `Agent '{name}' is shared with unapproved security group '{groupName}' ({groupId})` |

### Rule 4: EXCESSIVE_INDIVIDUAL

| Aspect | Value |
|--------|-------|
| **Detection logic** | Count of `type = User` principals exceeds `fsi_SharingPolicy.fsi_max_individual_shares` |
| **BAP API field** | Principal array → count where `type == "User"` |
| **Dataverse query** | `fsi_sharingpolicies?$filter=fsi_is_active eq true&$top=1` → read `fsi_max_individual_shares` |
| **Violation type** | `fsi_UASD_violationtype` = 3 (EXCESSIVE_INDIVIDUAL) |
| **Severity** | Medium → `fsi_acv_severity` = 2 (Warning) |
| **Evidence** | Individual count + threshold |
| **Description format** | `Agent '{name}' is shared with {count} individual users (threshold: {max})` |

### Rule 5: CROSS_TENANT_ACCESS

| Aspect | Value |
|--------|-------|
| **Detection logic** | Any principal whose tenant ID differs from `HomeTenantId` environment variable |
| **BAP API field** | Principal properties → tenant ID field |
| **Environment variable** | `fsi_UASD_HomeTenantId` |
| **Violation type** | `fsi_UASD_violationtype` = 4 (CROSS_TENANT_ACCESS) |
| **Severity** | High → `fsi_acv_severity` = 5 (Error) |
| **Evidence** | External tenant ID + principal details |
| **Description format** | `Agent '{name}' is shared with principal from external tenant ({tenantId})` |

---

## 5. Risk Assessment

### 5.1 Technical Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| **BAP API endpoint structure** — per-agent sharing principal endpoints are spec-defined but not publicly documented | Medium | Follow spec literally. Document endpoints in flow comments. Lab-grade allows rapid iteration. |
| **Nested Foreach depth** — 3 levels of nesting (environments → agents → principals) may hit Power Automate limits | Low | Power Automate supports nesting. Use Sequential operationOptions to avoid concurrency issues. |
| **Large tenant scanning** — environments with hundreds of agents may cause flow timeouts | Medium | Add pagination handling for BAP API responses. Consider environment filtering in flow. |
| **Duplicate violation creation** — consecutive scans could create duplicate violations for the same issue | Low | Pre-check for existing Open violations before creation (Architecture Decision 2.3). |
| **Exception check performance** — querying exceptions per-agent per-rule adds Dataverse calls | Low | Batch exception load at scan start, filter in-memory rather than per-agent query. |

### 5.2 Pattern Compliance Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| **Flow JSON invalid** — hand-crafted JSON may have structural errors preventing import | Low | Validate against CAA flow structure. Use consistent action naming conventions. |
| **Adaptive card rendering** — card may not render correctly on all Teams clients | Low | Follow CAA card pattern exactly. Use Adaptive Card Designer to validate. |
| **PowerShell script divergence** — `Invoke-SharingAudit.ps1` may implement rules differently than the flow | Medium | Document the 5 rules as a shared specification. Both flow and script reference the same rule definitions. |

### 5.3 Dependency Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| **Phase 1 tables not deployed** — flow references Dataverse entities that don't exist locally | Low | Phase 1 is complete. Flow JSON is portable — import creates bindings at deploy time. |
| **Shared option sets missing** — `fsi_acv_zone` and `fsi_acv_severity` not in target environment | Low | Schema script checks for shared option sets. Deployment guide will list prerequisites. |

---

## 6. Recommended Approach

### 6.1 Plan Structure

Split Phase 2 into 2 plans per ROADMAP.md guidance:

**Plan A (02-01): Detector Flow + Adaptive Card**
- Create `src/uasd-detector-scan-agents.json` following CAA flow JSON pattern
- Create `src/adaptive-card-uasd-alert.json` following CAA adaptive card pattern
- No overlapping files with Plan B

**Plan B (02-02): PowerShell Audit Script**
- Create `scripts/governance/Invoke-SharingAudit.ps1` following hardening baseline pattern
- No overlapping files with Plan A

### 6.2 Flow JSON Construction Order

1. Start with connection references (2 refs)
2. Add trigger (daily recurrence)
3. Chain variable initializations (8 variables)
4. Build Scope_Try with:
   a. Reference data loading (approved groups, policy thresholds)
   b. BAP API environment enumeration
   c. Nested agent iteration with principal evaluation
   d. 5 rule evaluation branches
   e. Exception-aware violation creation
   f. Card composition and Teams posting
5. Build Scope_Catch with error notification

### 6.3 Adaptive Card Construction

1. Copy CAA card structure
2. Replace header text and solution context
3. Replace run summary facts with UASD-specific fields
4. Remove zone compliance section (not applicable)
5. Adapt violation item template for sharing violations
6. Remove drift section (not applicable)
7. Update action buttons for UASD portals/docs
8. Write `_metadata` section

### 6.4 PowerShell Script Construction

1. Copy header format from `Invoke-HardeningBaselineCheck.ps1`
2. Define UASD-specific parameters (`-HomeTenantId`)
3. Implement `New-ViolationResult` helper
4. Implement 5 check groups (one per violation rule):
   - Group 1: ORG_WIDE_SHARING
   - Group 2: PUBLIC_INTERNET_LINK
   - Group 3: UNAPPROVED_GROUP (requires approved groups input)
   - Group 4: EXCESSIVE_INDIVIDUAL (requires threshold input)
   - Group 5: CROSS_TENANT_ACCESS (requires HomeTenantId)
5. Aggregate results with Metadata/Summary/Violations structure
6. Implement SHA-256 evidence hash
7. Implement output format switch

### 6.5 Validation Criteria

- Flow JSON: valid JSON, parseable, all required fields present
- Adaptive card: valid Adaptive Card v1.4 schema
- PowerShell: `pwsh -c "& { . ./scripts/governance/Invoke-SharingAudit.ps1 -WhatIf }"` exits 0 (syntax validation)
- No `mkdocs build` impact (no docs changes in Phase 2)

---

*Research completed: 2026-02-12*
*Sources: src/caa-daily-compliance-flow.json, src/adaptive-card-caa-alert.json, scripts/governance/Invoke-HardeningBaselineCheck.ps1, scripts/create_uasd_dataverse_schema.py, scripts/create_uasd_connection_references.py, scripts/create_uasd_environment_variables.py, .planning/research/v16-*.md*
