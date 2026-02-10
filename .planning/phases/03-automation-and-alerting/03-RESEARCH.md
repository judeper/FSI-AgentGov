# Phase 3: Automation and Alerting - Research

**Researched:** 2026-02-07
**Domain:** Power Automate scheduled flows, drift detection, Teams alerting, PowerShell-to-Dataverse integration
**Confidence:** HIGH

## Summary

Phase 3 automates daily session security drift detection and routes classified alerts to Microsoft Teams and email. The research focused on three key areas: (1) Power Automate flow patterns for daily scheduled execution with Dataverse integration, (2) drift detection logic using baseline comparison from ValidationHistory, and (3) Teams adaptive card alerting with severity-based routing.

The standard approach follows the ACV v4 pattern: PowerShell runbooks executed via Power Automate scheduled flows (Recurrence trigger at 6:00 AM UTC), drift detection via Compare-ValidationBaseline helper (queries last Passed validation as baseline), and adaptive card alerts to Teams channels for Failed/Error severity with email notifications to distribution lists for all non-Passed results. The runbook wrapper pattern wraps Test-SessionCompliance.ps1 in a Start-SessionValidationRunbook.ps1 that provides certificate-based authentication, JSON output to the pipeline, and drift detection integration.

Key findings: (1) Recurrence triggers should run at specific times (e.g., 6:00 AM UTC) with "At these minutes" configured to avoid load spikes; (2) Drift detection compares current severity against last Passed baseline, failing open (DriftDetected=true) on query errors to avoid suppressing alerts; (3) Office 365 Connectors for Teams are deprecated (March 31, 2026) — new integrations must use Power Automate with adaptive cards; (4) Baseline capture functionality creates SessionBaseline records from live CA policy state, enabling subsequent drift scans to compare against operator-approved configurations; (5) Flow outputs are limited to 10 MB — large validation runs must write detailed results to Dataverse and return summary JSON only.

**Primary recommendation:** Follow the ACV Power Automate pattern with SSC-specific adaptations: create Start-SessionValidationRunbook.ps1 wrapper, build scheduled flow with Recurrence trigger, integrate Compare-ValidationBaseline for drift detection, and route alerts via Teams adaptive cards with zone-based severity classification.

## Standard Stack

The established libraries/tools for Power Automate automation and alerting:

### Core

| Library/Service | Version | Purpose | Why Standard |
|-----------------|---------|---------|--------------|
| Power Automate | Cloud (2026 release) | Scheduled flow orchestration, alerting | Microsoft-native automation platform; tight Dataverse integration; adaptive card support |
| PowerShell 7.0+ | 7.0+ | Validation orchestration wrapper | Proven pattern from ACV; certificate-based auth; JSON output to flow pipeline |
| Microsoft Teams | Current | Alert destination via adaptive cards | Native M365 integration; adaptive cards replace deprecated Office 365 Connectors (March 2026) |
| Dataverse Web API | v9.2 | Baseline queries, history writes | Standard API for all Dataverse operations; OData filters for baseline comparison |

### Supporting

| Library/Service | Version | Purpose | When to Use |
|-----------------|---------|---------|-------------|
| MSAL.PS | 4.37.0+ | PowerShell Dataverse authentication | Certificate-based auth from runbook wrappers to Dataverse Web API |
| requests (Python) | 2.32.0+ | Python drift analysis (if needed) | Alternative to PowerShell for complex drift logic (not needed for Phase 3) |
| ExchangeOnlineManagement | 3.0.0+ | CA policy queries (if extending beyond Phase 1) | Only if drift detection needs live CA policy queries beyond Phase 1 output |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Power Automate Recurrence | Azure Logic Apps Recurrence | Logic Apps has more trigger options but Power Automate integrates better with Dataverse/Teams |
| PowerShell runbook wrapper | Azure Automation Runbook | Automation provides managed execution but adds infrastructure complexity; same pattern works |
| Teams adaptive cards | Email-only alerts | Adaptive cards provide interactive UI (buttons, facts) and better visibility in Teams channels |
| Compare-ValidationBaseline helper | Inline OData query in flow | Helper centralizes drift logic; reusable across multiple flows; easier to test |

**Installation:**

Power Automate flows are created via the web UI (make.powerautomate.com). No local installation required.

PowerShell dependencies (for runbook wrappers):
```powershell
# MSAL.PS for Dataverse authentication
Install-Module -Name MSAL.PS -RequiredVersion 4.37.0 -Force

# Microsoft.Graph.Identity.SignIns (already required by Phase 1)
Install-Module -Name Microsoft.Graph.Identity.SignIns -Force
```

## Architecture Patterns

### Recommended Flow Structure

Following ACV v4 pattern from `audit-configuration-validator/src/tenant-validation-flow.json`:

```
Power Automate Flow: SSC - Session Validation (Daily)
├── Trigger: Recurrence (6:00 AM UTC, daily)
├── Initialize Variables (8 variables)
│   ├── DataverseUrl (String): https://governance.crm.dynamics.com
│   ├── TenantId (String): contoso.onmicrosoft.com
│   ├── ClientId (String): <app-registration-id>
│   ├── CertificateThumbprint (String): <cert-thumbprint>
│   ├── TeamsChannelId (String): <channel-id>
│   ├── ComplianceDistributionList (String): compliance-alerts@contoso.com
│   ├── Zone (String): Zone3
│   └── ConfigPath (String): tenant-config.json
├── Scope: Try
│   ├── Execute Runbook (direct PowerShell call or HTTP webhook)
│   │   └── Calls: Start-SessionValidationRunbook.ps1
│   │       └── Wraps: Test-SessionCompliance.ps1
│   ├── Parse JSON Results
│   │   └── Output schema: { Timestamp, Zone, OverallStatus, Validators, Drift, AlertRequired }
│   ├── Check Alert Required (Condition: AlertRequired = true)
│   │   ├── If Yes:
│   │   │   ├── Check Severity For Teams (Condition: OverallStatus = Failed OR Error)
│   │   │   │   └── If Yes: Post adaptive card to Teams
│   │   │   └── Send Email Alert (Office 365 Outlook)
│   │   │       └── Importance: High if Failed/Error, Normal if Warning
│   │   └── If No: Terminate flow (no alert needed)
│   └── Write Validation History to Dataverse (optional checkpoint)
└── Scope: Catch
    └── Send Error Email to distribution list
```

**Naming conventions:**
- Flow name: `SSC - Session Validation (Daily)` (zone-specific or parameterized)
- Runbook wrapper: `Start-SessionValidationRunbook.ps1`
- Adaptive card template: `adaptive-card-session-alert.json`
- Connection references: `fsi_cr_dataverse_sessionvalidation`, `fsi_cr_teams_sessionvalidation`

### Pattern 1: PowerShell Runbook Wrapper for Automated Execution

**What:** Wrap Test-SessionCompliance.ps1 in a Start-SessionValidationRunbook.ps1 that provides certificate-based authentication, JSON output to pipeline, and drift detection integration.

**When to use:** When Power Automate flows need to execute PowerShell validation scripts with non-interactive authentication and structured output.

**Example:**
```powershell
# Source: ACV Start-TenantValidationRunbook.ps1 adapted for SSC
#Requires -Version 7.0
#Requires -Modules Microsoft.Graph.Identity.SignIns, MSAL.PS

<#
.SYNOPSIS
    Power Automate runbook wrapper for session security validation.

.OUTPUTS
    JSON object with properties:
    - RunType: "SessionValidation"
    - Timestamp: ISO 8601 UTC timestamp
    - Zone: Zone1 | Zone2 | Zone3
    - OverallStatus: Passed | Failed | Warning
    - Reason: Summary explanation
    - Validators: Hashtable with SessionControls, AuthStrength, PimRoleSettings, BreakGlass results
    - Drift: Object with DriftDetected, CurrentStatus, BaselineStatus, BaselineDate
    - AlertRequired: Boolean flag for flow routing
    - AlertSeverity: Status value for alert priority
#>

param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("Zone1", "Zone2", "Zone3")]
    [string]$Zone,

    [Parameter(Mandatory = $true)]
    [string]$DataverseUrl,

    [Parameter(Mandatory = $true)]
    [string]$TenantId,

    [Parameter(Mandatory = $true)]
    [string]$ClientId,

    [Parameter(Mandatory = $true)]
    [string]$CertificateThumbprint,

    [Parameter(Mandatory = $true)]
    [string]$ConfigPath
)

# Dot-source Test-SessionCompliance.ps1 and Compare-ValidationBaseline.ps1
. "$PSScriptRoot\Test-SessionCompliance.ps1"
. "$PSScriptRoot\private\Compare-ValidationBaseline.ps1"

# Execute validation with certificate auth
$validationParams = @{
    Zone                   = $Zone
    ConfigPath             = $ConfigPath
    TenantId               = $TenantId
    ClientId               = $ClientId
    CertificateThumbprint  = $CertificateThumbprint
}

$validationResults = Test-SessionCompliance @validationParams

# Acquire Dataverse token for drift detection
$token = Get-MsalToken -TenantId $TenantId -ClientId $ClientId -CertificateThumbprint $CertificateThumbprint -Scopes "$DataverseUrl/.default"

# Perform drift detection against last Passed baseline
$drift = Compare-ValidationBaseline `
    -DataverseUrl $DataverseUrl `
    -DataverseToken $token.AccessToken `
    -Scope "Tenant" `
    -CurrentStatus $validationResults.OverallStatus

# Construct output for Power Automate
$output = @{
    RunType        = "SessionValidation"
    Timestamp      = (Get-Date).ToUniversalTime().ToString("o")
    Zone           = $Zone
    OverallStatus  = $validationResults.OverallStatus
    Reason         = $validationResults.Reason
    Validators     = $validationResults.Validators
    Drift          = $drift
    AlertRequired  = ($drift.DriftDetected -or $validationResults.OverallStatus -ne "Passed")
    AlertSeverity  = $validationResults.OverallStatus
}

# Output JSON to pipeline (captured by Power Automate)
$output | ConvertTo-Json -Depth 10 -Compress
```

**Key points:**
- Certificate-based auth replaces interactive prompts (no browser flow)
- JSON output to pipeline (no Write-Host) for Power Automate Parse JSON action
- Drift detection integrated via Compare-ValidationBaseline helper
- AlertRequired flag simplifies flow routing logic

### Pattern 2: Recurrence Trigger Configuration

**What:** Configure Power Automate Recurrence trigger to run daily at a specific time with proper load distribution.

**When to use:** All scheduled validation flows that need to run at consistent intervals.

**Example:**
```json
{
  "triggers": {
    "Recurrence": {
      "recurrence": {
        "frequency": "Day",
        "interval": 1,
        "schedule": {
          "hours": ["6"],
          "minutes": [0]
        },
        "timeZone": "UTC"
      },
      "type": "Recurrence"
    }
  }
}
```

**Key points:**
- Specify exact hours and minutes (not just interval) to avoid Microsoft load-leveling during the hour
- Use UTC timezone for consistency across geographies
- Daily interval = 1 for once per day
- For weekdays only: use advanced schedule with days filter (Monday-Friday)

**Best practices (from research):**
- Prefer event-based triggers when possible; use Recurrence only when true scheduling is needed
- Configure "At these minutes" to ensure exact execution time (source: [Power Automate Recurrence Trigger Reference](https://manueltgomes.com/reference/power-automate-trigger-reference/recurrence-trigger/))
- Avoid too-frequent schedules that burn through quota (source: [Run a cloud flow on a schedule](https://learn.microsoft.com/en-us/power-automate/run-scheduled-tasks))
- Control start time explicitly; if not defined, flow fires immediately on save (source: [Understanding the Power Automate Recurrence Trigger](https://www.serverlessnotes.com/docs/understanding-the-power-automate-recurrence-schedule-trigger))

### Pattern 3: Drift Detection via Baseline Comparison

**What:** Query Dataverse ValidationHistory for the most recent Passed validation and compare current severity to detect regression.

**When to use:** When automated flows need to determine if current validation status represents a new failure or expected state.

**Example:**
```powershell
# Source: ACV Compare-ValidationBaseline.ps1 adapted for SSC
function Compare-ValidationBaseline {
    param(
        [string]$DataverseUrl,
        [string]$DataverseToken,
        [ValidateSet("Passed", "Warning", "Failed", "Error")]
        [string]$CurrentStatus
    )

    # Map status to severity (higher = worse)
    $severityMap = @{
        "Passed"  = 1
        "Warning" = 2
        "Failed"  = 3
        "Error"   = 4
    }

    $currentSeverity = $severityMap[$CurrentStatus]

    # Query for last Passed validation (baseline)
    $filter = "fsi_severity eq 1"  # 1 = Passed
    $apiUrl = "$DataverseUrl/api/data/v9.2/fsi_validationhistories"
    $apiUrl += "?`$filter=$filter&`$orderby=createdon desc&`$top=1"

    $headers = @{
        "Authorization" = "Bearer $DataverseToken"
        "Accept" = "application/json"
    }

    $response = Invoke-RestMethod -Uri $apiUrl -Method Get -Headers $headers
    $baseline = $response.value | Select-Object -First 1

    if ($null -eq $baseline) {
        # First run - any non-Passed result is drift
        return [PSCustomObject]@{
            DriftDetected = ($CurrentStatus -ne "Passed")
            CurrentStatus = $CurrentStatus
            BaselineStatus = $null
            IsFirstRun = $true
        }
    }
    else {
        # Compare severities
        $baselineSeverity = $baseline.fsi_severity
        $driftDetected = $currentSeverity -gt $baselineSeverity

        return [PSCustomObject]@{
            DriftDetected = $driftDetected
            CurrentStatus = $CurrentStatus
            BaselineStatus = "Passed"
            BaselineDate = $baseline.createdon
            IsFirstRun = $false
        }
    }
}
```

**Key points:**
- Baseline is the most recent Passed (severity=1) validation
- Drift detected when current severity > baseline severity (numeric comparison)
- First run (no baseline): any non-Passed result triggers drift
- Fail open on query errors: return DriftDetected=$true to avoid suppressing alerts

**Drift detection logic:**
| Current Status | Baseline Status | Drift Detected? | Alert Sent? |
|----------------|-----------------|-----------------|-------------|
| Passed | Passed | No | No |
| Passed | (none - first run) | No | No |
| Warning | Passed | Yes | Yes |
| Failed | Passed | Yes | Yes (High importance) |
| Error | Passed | Yes | Yes (High importance) |
| Passed | Failed | No | No (improvement, not drift) |
| Warning | Failed | No | No (improvement, not drift) |

### Pattern 4: Teams Adaptive Card Alerting

**What:** Post adaptive cards to Microsoft Teams channels with severity-based styling and action buttons.

**When to use:** When Failed or Error severity alerts require visibility in Teams channels with rich formatting.

**Example:**
```json
{
  "type": "AdaptiveCard",
  "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
  "version": "1.4",
  "body": [
    {
      "type": "Container",
      "style": "attention",
      "items": [
        {
          "type": "ColumnSet",
          "columns": [
            {
              "type": "Column",
              "width": "auto",
              "items": [
                {
                  "type": "TextBlock",
                  "text": "[ALERT] Session Security Drift",
                  "weight": "Bolder",
                  "size": "Medium",
                  "color": "Attention"
                }
              ]
            },
            {
              "type": "Column",
              "width": "stretch",
              "items": [
                {
                  "type": "TextBlock",
                  "text": "${overallStatus}",
                  "weight": "Bolder",
                  "horizontalAlignment": "Right",
                  "color": "Attention"
                }
              ]
            }
          ]
        }
      ]
    },
    {
      "type": "Container",
      "items": [
        {
          "type": "TextBlock",
          "text": "Drift Detected",
          "weight": "Bolder",
          "size": "Medium"
        },
        {
          "type": "FactSet",
          "facts": [
            { "title": "Zone", "value": "${zone}" },
            { "title": "Drift From", "value": "${baselineStatus} → ${currentStatus}" },
            { "title": "Baseline Date", "value": "${baselineDate}" }
          ]
        }
      ]
    },
    {
      "type": "Container",
      "items": [
        {
          "type": "TextBlock",
          "text": "Validator Status",
          "weight": "Bolder"
        },
        {
          "type": "FactSet",
          "facts": [
            { "title": "Session Controls", "value": "${sessionControlsStatus}" },
            { "title": "Auth Strength", "value": "${authStrengthStatus}" },
            { "title": "PIM Settings", "value": "${pimStatus}" },
            { "title": "Break-Glass", "value": "${breakGlassStatus}" }
          ]
        }
      ]
    }
  ],
  "actions": [
    {
      "type": "Action.OpenUrl",
      "title": "View in Power Platform",
      "url": "https://make.powerapps.com"
    },
    {
      "type": "Action.OpenUrl",
      "title": "View Validation History",
      "url": "${validationHistoryUrl}"
    }
  ]
}
```

**Power Automate integration:**
```javascript
// In Power Automate "Post adaptive card in a chat or channel" action
// Use replace() function to substitute placeholders
replace(replace(replace(
    body('Get_Adaptive_Card_Template'),
    '${overallStatus}', body('Parse_JSON')?['OverallStatus']
),
    '${zone}', body('Parse_JSON')?['Zone']
),
    '${baselineStatus}', body('Parse_JSON')?['Drift']?['BaselineStatus']
)
```

**Key points:**
- `style: "attention"` provides red border for severity emphasis
- FactSets display key-value pairs in table format
- Action buttons link to Power Platform and validation history
- Placeholders (`${variableName}`) replaced by Power Automate `replace()` function

**Office 365 Connector deprecation:**
- **CRITICAL:** Office 365 Connectors are being retired March 31, 2026 (source: [Create Approvals via Adaptive Cards](https://blog.admindroid.com/how-to-create-approvals-via-adaptive-cards-using-power-automate/))
- New Teams integrations MUST use Power Automate with adaptive cards
- Existing connectors will stop working after March 2026 deadline

### Pattern 5: Baseline Capture for Future Drift Detection

**What:** Create SessionBaseline records from live CA policy state, enabling subsequent drift scans to compare against operator-approved configurations.

**When to use:** When operators need to "snapshot" current CA policy state as the approved baseline for future drift detection.

**Example:**
```powershell
# New script: Invoke-BaselineCapture.ps1
<#
.SYNOPSIS
    Captures current CA policy session controls as a baseline in Dataverse.

.DESCRIPTION
    Queries live CA policies, extracts session control settings, and writes a SessionBaseline
    record to Dataverse. This baseline becomes the reference for future drift detection.

.PARAMETER Zone
    Governance zone to capture baseline for.

.PARAMETER DataverseUrl
    Dataverse organization URL.

.PARAMETER TenantId
    Azure AD tenant ID.

.PARAMETER ClientId
    Azure AD application ID.

.PARAMETER CertificateThumbprint
    Certificate thumbprint for authentication.

.OUTPUTS
    PSCustomObject with BaselineId, Zone, CapturedOn, SignInFrequencyMinutes
#>

param(
    [ValidateSet("Zone1", "Zone2", "Zone3")]
    [string]$Zone,
    [string]$DataverseUrl,
    [string]$TenantId,
    [string]$ClientId,
    [string]$CertificateThumbprint
)

# Connect to Microsoft Graph
Connect-MgGraph -TenantId $TenantId -ClientId $ClientId -CertificateThumbprint $CertificateThumbprint

# Query CA policies with session controls
$policies = Get-MgIdentityConditionalAccessPolicy -Filter "state eq 'enabled'" | Where-Object {
    $_.SessionControls -and $_.SessionControls.SignInFrequency
}

# Extract session control settings
$sessionSettings = $policies | ForEach-Object {
    @{
        PolicyId = $_.Id
        PolicyName = $_.DisplayName
        SignInFrequencyValue = $_.SessionControls.SignInFrequency.Value
        SignInFrequencyUnit = $_.SessionControls.SignInFrequency.Type
        AuthenticationStrength = $_.GrantControls.AuthenticationStrength.Id
        RequireCompliantDevice = ($_.GrantControls.BuiltInControls -contains "compliantDevice")
    }
}

# Normalize to minutes
$signInFrequencyMinutes = switch ($Zone) {
    "Zone1" { 480 }  # 8 hours
    "Zone2" { 240 }  # 4 hours
    "Zone3" { 60 }   # 1 hour
}

# Acquire Dataverse token
$token = Get-MsalToken -TenantId $TenantId -ClientId $ClientId -CertificateThumbprint $CertificateThumbprint -Scopes "$DataverseUrl/.default"

# Create SessionBaseline record
$baseline = @{
    "fsi_name" = "$Zone-$(Get-Date -Format 'yyyy-MM-ddTHH:mm:ssZ')"
    "fsi_zone" = $zoneOptionSetValue  # Map Zone1/2/3 to option set value
    "fsi_signInfrequencyminutes" = $signInFrequencyMinutes
    "fsi_authstrength" = $sessionSettings[0].AuthenticationStrength
    "fsi_requirecompliantdevice" = $sessionSettings[0].RequireCompliantDevice
    "fsi_isactive" = $true
    "fsi_capturedon" = (Get-Date).ToUniversalTime().ToString("o")
    "fsi_rawjson" = ($sessionSettings | ConvertTo-Json -Depth 10)
}

$headers = @{
    "Authorization" = "Bearer $($token.AccessToken)"
    "Content-Type" = "application/json"
}

$response = Invoke-RestMethod `
    -Uri "$DataverseUrl/api/data/v9.2/fsi_sessionbaselines" `
    -Method Post `
    -Headers $headers `
    -Body ($baseline | ConvertTo-Json)

Write-Host "Baseline captured: $($baseline.fsi_name)" -ForegroundColor Green
```

**Key points:**
- Baseline capture is manual operation (operator-initiated, not automated)
- Captured baseline becomes reference for drift detection
- `fsi_isactive` flag identifies current active baseline (only one per zone)
- `fsi_rawjson` stores full policy snapshot for deep analysis

### Anti-Patterns to Avoid

- **Don't poll Dataverse continuously:** Use Recurrence trigger with appropriate interval (daily); avoid "When a record is created" trigger for scheduled validation
- **Don't skip drift detection:** Always compare against baseline to avoid alert fatigue from transient failures
- **Don't use Write-Host in runbook wrappers:** Use JSON output only; Write-Host content is not captured by Power Automate
- **Don't hardcode credentials:** Use certificate-based authentication with parameters
- **Don't ignore Teams connector deprecation:** Office 365 Connectors retire March 31, 2026 — use Power Automate adaptive cards
- **Don't return massive JSON from runbooks:** Power Automate flow outputs limited to 10 MB; write detailed results to Dataverse, return summary JSON

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Drift detection logic | Custom baseline tracking | Compare-ValidationBaseline helper | Handles first-run edge case, fail-open on errors, numeric severity comparison |
| Teams adaptive cards | Plain text Teams messages | Adaptive card JSON templates | Richer formatting, action buttons, severity styling, better visibility |
| Runbook authentication | Username/password prompts | Certificate-based service principal | Non-interactive; no credentials in flow; Azure Automation compatible |
| Flow error handling | Try/catch in each action | Scope: Try + Scope: Catch pattern | Centralized error handling; single email notification; clean flow structure |
| JSON output parsing | String manipulation | Power Automate Parse JSON action | Type-safe property access; schema validation; IntelliSense in subsequent actions |

**Key insight:** The ACV solution established the complete pattern for scheduled Dataverse validation with Teams alerting — SSC should follow the exact flow structure, substituting session-specific validation logic and adaptive card content.

## Common Pitfalls

### Pitfall 1: Recurrence Trigger Fires at Unpredictable Times

**What goes wrong:** Flow scheduled for "6:00 AM daily" runs anytime between 6:00-6:59 AM, causing inconsistent execution.

**Why it happens:** Power Automate load-levels requests during the hour if "At these minutes" is not configured, causing flows to run at random times within the hour.

**How to avoid:** Always configure "At these minutes" in advanced schedule settings to ensure exact execution time.

**Warning signs:** Flow run history shows execution times vary (6:12 AM one day, 6:47 AM next day) despite "daily at 6:00 AM" configuration.

**Mitigation:**
```json
{
  "recurrence": {
    "frequency": "Day",
    "interval": 1,
    "schedule": {
      "hours": ["6"],
      "minutes": [0]  // CRITICAL: specifies exact minute
    },
    "timeZone": "UTC"
  }
}
```

Source: [Understanding the Power Automate Recurrence Trigger](https://www.serverlessnotes.com/docs/understanding-the-power-automate-recurrence-schedule-trigger)

### Pitfall 2: Drift Detection False Positives on First Run

**What goes wrong:** First validation run triggers drift alert even though no baseline exists, causing confusion.

**Why it happens:** Drift logic compares current status to baseline; on first run with no baseline, any non-Passed result appears as drift.

**How to avoid:** Check `IsFirstRun` flag in drift detection output; suppress alerts or adjust messaging for first-run scenario.

**Warning signs:** Alert says "Drift detected: (none) → Failed" when baseline is null.

**Mitigation:**
```powershell
if ($drift.IsFirstRun -and $drift.DriftDetected) {
    $alertMessage = "Initial validation run: $($drift.CurrentStatus). Baseline will be established for future drift detection."
} elseif ($drift.DriftDetected) {
    $alertMessage = "Drift detected: $($drift.BaselineStatus) → $($drift.CurrentStatus) since $($drift.BaselineDate)"
} else {
    $alertMessage = "No drift detected. Status remains: $($drift.CurrentStatus)"
}
```

### Pitfall 3: Runbook Output Exceeds Power Automate 10 MB Limit

**What goes wrong:** Large validation runs (50+ CA policies, detailed PIM settings) return JSON that exceeds 10 MB, causing flow Parse JSON action to fail.

**Why it happens:** Runbook includes full policy JSON, verbose logging, or large arrays in output; Power Automate has hard 10 MB limit on action outputs.

**How to avoid:** Write detailed results to Dataverse ValidationHistory; return summary-only JSON with counts and status.

**Warning signs:** Parse JSON action fails with "Response too large" error; flow run history shows output truncated.

**Mitigation:**
```powershell
# BAD: Include all policy details in output
$output = @{
    Policies = $allPolicies  # Could be 100+ policies with full JSON
    Validators = $detailedResults
}

# GOOD: Write to Dataverse, return summary
# Write detailed results to Dataverse
Write-ValidationHistoryRecord -Details $detailedResults

# Return summary only
$output = @{
    OverallStatus = "Failed"
    PolicyCount = $allPolicies.Count
    FailedCount = ($allPolicies | Where-Object { $_.Status -eq "Failed" }).Count
    RunId = $runId  # Reference for Dataverse query
}
```

### Pitfall 4: Certificate Authentication Fails in Production

**What goes wrong:** Runbook works in local testing but fails with "Certificate not found" in Power Automate production.

**Why it happens:** Certificate stored locally for testing but not uploaded to Azure Key Vault or not accessible to flow's managed identity.

**How to avoid:** Store certificate in Azure Key Vault; grant flow's managed identity "Get" permission on secrets; retrieve thumbprint at runtime.

**Warning signs:** Flow fails with "Cannot find certificate with thumbprint" error; local testing passes.

**Mitigation:**
```powershell
# Option 1: Azure Key Vault retrieval (best for production)
$thumbprint = Get-AzKeyVaultSecret -VaultName "kv-governance" -Name "SSC-Cert-Thumbprint" -AsPlainText

# Option 2: Flow variable (simpler but less secure)
# Set CertificateThumbprint as flow variable, populate from secure source
```

### Pitfall 5: Teams Adaptive Card Placeholders Not Replaced

**What goes wrong:** Adaptive card posted to Teams shows literal `${overallStatus}` instead of actual value.

**Why it happens:** Power Automate `replace()` function not used to substitute placeholders; card posted with raw template.

**How to avoid:** Use nested `replace()` calls for all placeholders in adaptive card JSON template.

**Warning signs:** Teams card displays `${variableName}` strings instead of actual data.

**Mitigation:**
```javascript
// In "Post adaptive card" action body:
replace(
  replace(
    replace(
      replace(
        body('Get_Adaptive_Card_Template'),
        '${overallStatus}', body('Parse_JSON')?['OverallStatus']
      ),
      '${zone}', body('Parse_JSON')?['Zone']
    ),
    '${currentStatus}', body('Parse_JSON')?['Drift']?['CurrentStatus']
  ),
  '${baselineStatus}', body('Parse_JSON')?['Drift']?['BaselineStatus']
)
```

Alternative: Use Power Automate compose action to build card JSON dynamically without placeholders.

Source: [Post Teams Adaptive Card with Power Automate](https://powerplatformuniverse.com/power-automate/post-teams-adaptive-card-with-power-automate/)

## Code Examples

Verified patterns from ACV implementation and Microsoft Learn:

### Runbook Wrapper Main Execution Block

```powershell
# Source: ACV Start-TenantValidationRunbook.ps1 (lines 115-180)
try {
    Write-Verbose "Starting session validation runbook"

    # Dot-source required scripts
    . "$PSScriptRoot\Test-SessionCompliance.ps1"
    . "$PSScriptRoot\private\Compare-ValidationBaseline.ps1"

    # Build parameters for validation orchestrator
    $validationParams = @{
        Zone                   = $Zone
        ConfigPath             = $ConfigPath
        TenantId               = $TenantId
        ClientId               = $ClientId
        CertificateThumbprint  = $CertificateThumbprint
    }

    # Execute validation
    $validationResults = Test-SessionCompliance @validationParams
    Write-Verbose "Validation complete. Overall status: $($validationResults.OverallStatus)"

    # Acquire Dataverse token for drift detection
    $tokenParams = @{
        TenantId               = $TenantId
        ClientId               = $ClientId
        CertificateThumbprint  = $CertificateThumbprint
        Scopes                 = "$DataverseUrl/.default"
    }
    $token = Get-MsalToken @tokenParams

    # Perform drift detection
    $driftParams = @{
        DataverseUrl  = $DataverseUrl
        DataverseToken = $token.AccessToken
        Scope         = "Tenant"
        CurrentStatus = $validationResults.OverallStatus
    }
    $drift = Compare-ValidationBaseline @driftParams

    # Construct output
    $output = @{
        RunType       = "SessionValidation"
        Timestamp     = (Get-Date).ToUniversalTime().ToString("o")
        Zone          = $Zone
        OverallStatus = $validationResults.OverallStatus
        Reason        = $validationResults.Reason
        Validators    = $validationResults.Validators
        Drift         = $drift
        AlertRequired = ($drift.DriftDetected -or $validationResults.OverallStatus -ne "Passed")
        AlertSeverity = $validationResults.OverallStatus
    }

    # Output JSON to pipeline
    $output | ConvertTo-Json -Depth 10 -Compress

} catch {
    # Error handling
    $errorOutput = @{
        RunType       = "SessionValidation"
        Timestamp     = (Get-Date).ToUniversalTime().ToString("o")
        OverallStatus = "Error"
        Reason        = "Runbook execution failed: $($_.Exception.Message)"
        AlertRequired = $true
        AlertSeverity = "Error"
    }

    $errorOutput | ConvertTo-Json -Depth 10 -Compress
    throw
}
```

### Power Automate Flow Variable Initialization

```json
{
  "actions": {
    "Initialize_DataverseUrl": {
      "runAfter": {},
      "type": "InitializeVariable",
      "inputs": {
        "variables": [
          {
            "name": "DataverseUrl",
            "type": "string",
            "value": "https://governance.crm.dynamics.com"
          }
        ]
      }
    },
    "Initialize_TenantId": {
      "runAfter": { "Initialize_DataverseUrl": ["Succeeded"] },
      "type": "InitializeVariable",
      "inputs": {
        "variables": [
          {
            "name": "TenantId",
            "type": "string",
            "value": "contoso.onmicrosoft.com"
          }
        ]
      }
    },
    "Initialize_Zone": {
      "runAfter": { "Initialize_TenantId": ["Succeeded"] },
      "type": "InitializeVariable",
      "inputs": {
        "variables": [
          {
            "name": "Zone",
            "type": "string",
            "value": "Zone3"
          }
        ]
      }
    }
  }
}
```

Source: ACV tenant-validation-flow.json

### Scope-Based Error Handling

```json
{
  "actions": {
    "Scope_Try": {
      "type": "Scope",
      "actions": {
        "Execute_Runbook": { "type": "...", "..." },
        "Parse_Results": { "type": "...", "..." },
        "Send_Alerts": { "type": "...", "..." }
      }
    },
    "Scope_Catch": {
      "type": "Scope",
      "runAfter": {
        "Scope_Try": ["Failed", "Skipped", "TimedOut"]
      },
      "actions": {
        "Send_Error_Email": {
          "type": "ApiConnection",
          "inputs": {
            "host": { "connection": { "name": "@parameters('$connections')['office365']['connectionId']" } },
            "method": "post",
            "path": "/v2/Mail",
            "body": {
              "To": "@variables('ComplianceDistributionList')",
              "Subject": "[CRITICAL] Session Validation Flow Error",
              "Body": "<p>Flow execution failed. Check run history for details.</p>",
              "Importance": "High"
            }
          }
        }
      }
    }
  }
}
```

Source: ACV tenant-validation-flow.json

### Drift Detection OData Query

```powershell
# Query for last Passed validation (baseline)
$filter = "fsi_severity eq 1"  # 1 = Passed
$apiUrl = "$DataverseUrl/api/data/v9.2/fsi_validationhistories"
$apiUrl += "?`$filter=$filter"
$apiUrl += "&`$orderby=createdon desc"
$apiUrl += "&`$top=1"
$apiUrl += "&`$select=fsi_severity,fsi_timestamp,createdon"

$headers = @{
    "Authorization"    = "Bearer $DataverseToken"
    "Accept"           = "application/json"
    "OData-MaxVersion" = "4.0"
    "OData-Version"    = "4.0"
}

$response = Invoke-RestMethod -Uri $apiUrl -Method Get -Headers $headers
$baseline = $response.value | Select-Object -First 1
```

Source: ACV Compare-ValidationBaseline.ps1

### Adaptive Card with Severity Styling

```json
{
  "type": "Container",
  "style": "attention",
  "items": [
    {
      "type": "ColumnSet",
      "columns": [
        {
          "type": "Column",
          "width": "auto",
          "items": [
            {
              "type": "TextBlock",
              "text": "[ALERT] Session Security Drift",
              "weight": "Bolder",
              "size": "Medium",
              "color": "Attention"
            }
          ]
        },
        {
          "type": "Column",
          "width": "stretch",
          "items": [
            {
              "type": "TextBlock",
              "text": "${overallStatus}",
              "weight": "Bolder",
              "horizontalAlignment": "Right",
              "color": "Attention"
            }
          ]
        }
      ]
    }
  ]
}
```

Source: ACV adaptive-card-tenant-alert.json

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Office 365 Connectors for Teams | Power Automate with adaptive cards | March 31, 2026 (retirement) | Adaptive cards provide richer UI; connectors no longer supported |
| Manual validation runs | Scheduled Power Automate flows | v4 (ACV milestone) | Daily automated drift detection; consistent execution timing |
| Email-only alerts | Teams adaptive cards + email | v4 (ACV milestone) | Better visibility in Teams channels; interactive action buttons |
| Inline PowerShell in flows | Runbook wrapper pattern | v4 (ACV milestone) | Certificate-based auth; structured JSON output; centralized error handling |
| Hardcoded baselines | Dynamic baseline capture | v5 (SSC milestone) | Operators approve current config as baseline; drift detection against approved state |

**Deprecated/outdated:**
- **Office 365 Connectors:** Retiring March 31, 2026; replaced by Power Automate for all new Teams integrations
- **Azure Automation runbooks via HTTP webhook:** Still supported but direct PowerShell execution in flows preferred where licensing allows
- **Parse JSON without schema:** Power Automate now generates schema from sample JSON, providing type safety and IntelliSense

## Open Questions

Things that couldn't be fully resolved:

1. **Should baseline capture be manual or automated?**
   - What we know: Manual capture gives operators control over "approved" baseline; automated capture risks using drift state as baseline
   - What's unclear: Best practice for enterprise customers with change control requirements
   - Recommendation: Manual baseline capture (Invoke-BaselineCapture.ps1) run by operators after approved CA policy changes; automated drift detection compares against last operator-approved baseline

2. **How should flows execute PowerShell runbooks?**
   - What we know: Options include Azure Automation runbooks (ACV pattern), Azure Functions with PowerShell runtime, or direct HTTP webhook to Azure VM
   - What's unclear: Best practice for SSC given Azure Automation licensing requirements and complexity
   - Recommendation: Follow ACV pattern (Azure Automation runbooks) for consistency; document Azure Automation Account setup as prerequisite in Phase 3 plans

3. **Should drift detection baseline be per-zone or per-environment?**
   - What we know: Validation runs per-zone (Zone1/Zone2/Zone3); baselines could be zone-specific or environment-specific
   - What's unclear: If customer has multiple dev/test/prod environments, should each have separate baselines?
   - Recommendation: Per-zone baselines (simpler model); single baseline per zone applies across all environments validating that zone

## Sources

### Primary (HIGH confidence)

- [Microsoft Learn - Create flows that post adaptive cards to Microsoft Teams](https://learn.microsoft.com/en-us/power-automate/create-adaptive-cards) - Official adaptive card documentation
- [Microsoft Learn - Overview of adaptive cards for Teams](https://learn.microsoft.com/en-us/power-automate/overview-adaptive-cards) - Adaptive card capabilities and patterns
- [Microsoft Learn - Run a cloud flow on a schedule](https://learn.microsoft.com/en-us/power-automate/run-scheduled-tasks) - Recurrence trigger configuration
- ACV v4 implementation - `C:/dev/FSI-AgentGov-Solutions/audit-configuration-validator/scripts/` - Established pattern for FSI-AgentGov solutions
- ACV Phase 3 docs - `C:/dev/FSI-AgentGov-Solutions/audit-configuration-validator/docs/FLOW_SETUP.md` - Flow creation guide with drift detection
- ACV runbook wrapper - `Start-TenantValidationRunbook.ps1` - Runbook pattern with JSON output and drift integration

### Secondary (MEDIUM confidence)

- [Power Automate Recurrence Trigger Reference](https://manueltgomes.com/reference/power-automate-trigger-reference/recurrence-trigger/) - Detailed recurrence configuration
- [Understanding the Power Automate Recurrence Trigger](https://www.serverlessnotes.com/docs/understanding-the-power-automate-recurrence-schedule-trigger) - Best practices for scheduling
- [Post Teams Adaptive Card with Power Automate](https://powerplatformuniverse.com/power-automate/post-teams-adaptive-card-with-power-automate/) - Adaptive card placeholder replacement patterns
- [Send Alerts to Microsoft Teams with Power Automate](https://docs.edgedelta.com/send-to-teams-power-automate/) - Teams alerting patterns
- [Create Approvals via Adaptive Cards Using Power Automate](https://blog.admindroid.com/how-to-create-approvals-via-adaptive-cards-using-power-automate/) - Office 365 Connector retirement notice

### Tertiary (LOW confidence - requires validation)

- [Microsoft Learn - Manage Dataverse auditing](https://learn.microsoft.com/en-us/power-platform/admin/manage-dataverse-auditing) - Organization-owned table immutability (not directly about append-only pattern)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Power Automate, PowerShell runbook wrappers, and Teams adaptive cards are established ACV v4 patterns
- Architecture: HIGH - Direct examination of ACV flows and runbook wrappers; Microsoft Learn verification for adaptive cards
- Pitfalls: MEDIUM - Derived from ACV implementation notes and Power Automate community best practices; not all tested in SSC context

**Research date:** 2026-02-07
**Valid until:** 2026-03-07 (30 days — Power Automate patterns are stable; Office 365 Connector deadline is fixed March 31, 2026)

**Key assumptions:**
- ACV v4 Power Automate pattern is appropriate for SSC (both are Tier 2 solutions with similar automation needs)
- Azure Automation Account will be available for runbook execution (prerequisite for Phase 3)
- Operators will manually capture baselines after CA policy changes (not automated baseline updates)
- Phase 2 Dataverse infrastructure is deployed and functioning (ValidationHistory table exists)
