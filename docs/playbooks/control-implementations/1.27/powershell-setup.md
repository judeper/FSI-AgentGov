# PowerShell Setup: Control 1.27 — AI Agent Content Moderation Enforcement

!!! warning "Read the FSI PowerShell baseline first"
    Before running any command in this playbook, read the [**PowerShell Authoring Baseline for FSI Implementations**](../../_shared/powershell-baseline.md). It is the canonical source for module version pinning, mutation safety (`-WhatIf` / `SupportsShouldProcess`), Dataverse compatibility, the `Write-FsiEvidence` SHA-256 evidence pattern, and the Desktop-edition guard. Snippets below intentionally re-use those patterns; the baseline is authoritative.

**Last Updated:** May 2026
**Primary Modules:** `Microsoft.PowerApps.Administration.PowerShell` (Desktop / Windows PowerShell 5.1 only), `ExchangeOnlineManagement` (Search-UnifiedAuditLog).

---

## Prerequisites

- [ ] **Role:** Power Platform Admin (cross-environment inventory) **or** Entra Global Admin. For Script 2 audit queries, also assign **Purview Audit Reader** (least-privilege) or **Purview Compliance Admin**.
- [ ] **PowerShell edition:** Windows PowerShell 5.1 (Desktop) is **required** for `Microsoft.PowerApps.Administration.PowerShell`. The Desktop guard from the baseline (§2) is included in every script below — do not remove it.
- [ ] **Module pinning:** baseline §1. Substitute `<version>` with the version approved by your CAB.

---

## Module Installation (Canonical Pattern)

```powershell
# Pinned per FSI baseline §1. Replace <version> with CAB-approved value.
Install-Module -Name Microsoft.PowerApps.Administration.PowerShell `
    -RequiredVersion '<version>' -Repository PSGallery -Scope CurrentUser -AllowClobber -AcceptLicense

Install-Module -Name ExchangeOnlineManagement `
    -RequiredVersion '<version>' -Repository PSGallery -Scope CurrentUser -AllowClobber -AcceptLicense

Add-PowerAppsAccount -Endpoint prod
# Replace admin@yourdomain.com with your privileged-access workstation account
Connect-ExchangeOnline -UserPrincipalName admin@yourdomain.com -ShowBanner:$false
```

---

!!! danger "API Surface — Verify Before Production Use"
    As of April 2026, `Get-AdminPowerAppChatbot` exposes most agent metadata, but the property path for content moderation (e.g., `Properties.ContentModeration.DefaultLevel`) is **not** documented as a stable schema. The scripts below are **inventory and reporting templates** — they probe the property and degrade gracefully when it is absent. Run the pre-flight probe first:

    ```powershell
    Get-AdminPowerAppEnvironment | Select-Object -First 1 | ForEach-Object {
        Get-AdminPowerAppChatbot -EnvironmentName $_.EnvironmentName -ErrorAction SilentlyContinue |
            Select-Object -First 1 | ConvertTo-Json -Depth 6
    }
    ```

    If `ContentModeration` is absent, fall back to manual inventory via [Portal Walkthrough](portal-walkthrough.md) Step 5 and document that decision in the evidence pack. The Dataverse `botcomponents` table (Script 4) is the authoritative source for per-topic moderation in tenants where the admin cmdlet does not surface it.

---

## Shared evidence helper (used by all scripts)

```powershell
# Re-use Write-FsiEvidence from the baseline (§5). Inlined here for self-containment.
function Write-FsiEvidence {
    param(
        [Parameter(Mandatory)] $Object,
        [Parameter(Mandatory)] [string]$Name,
        [Parameter(Mandatory)] [string]$EvidencePath,
        [string]$ScriptVersion = '1.27.0'
    )
    if (-not (Test-Path $EvidencePath)) { New-Item -ItemType Directory -Force -Path $EvidencePath | Out-Null }
    $ts = Get-Date -Format 'yyyyMMddTHHmmssZ'
    $jsonPath = Join-Path $EvidencePath ("{0}-{1}.json" -f $Name, $ts)
    $Object | ConvertTo-Json -Depth 20 | Set-Content -Path $jsonPath -Encoding UTF8
    $hash = (Get-FileHash -Path $jsonPath -Algorithm SHA256).Hash
    $manifestPath = Join-Path $EvidencePath 'manifest.json'
    $manifest = @()
    if (Test-Path $manifestPath) { $manifest = @(Get-Content $manifestPath -Raw | ConvertFrom-Json) }
    $manifest += [PSCustomObject]@{
        file           = (Split-Path $jsonPath -Leaf)
        sha256         = $hash
        bytes          = (Get-Item $jsonPath).Length
        generated_utc  = $ts
        script_version = $ScriptVersion
        control_id     = '1.27'
    }
    $manifest | ConvertTo-Json -Depth 6 | Set-Content -Path $manifestPath -Encoding UTF8
    return [PSCustomObject]@{ Path = $jsonPath; Sha256 = $hash }
}
```

---

## Script 1 — `Get-AgentModerationInventory.ps1` (read-only, idempotent)

```powershell
<#
.SYNOPSIS
    Cross-environment inventory of Copilot Studio agents and their effective
    content moderation defaults. Read-only. Idempotent (safe to re-run).
.OUTPUTS
    Evidence: AgentModerationInventory-<utc>.json + SHA-256 entry in manifest.json
#>
[CmdletBinding()]
param(
    [string]$EvidencePath = ".\evidence\1.27",
    [string]$Endpoint = 'prod',
    [string[]]$EnvironmentFilter   # optional: limit to named environments
)

$ErrorActionPreference = 'Stop'

# Baseline §2 — Desktop guard
if ($PSVersionTable.PSEdition -ne 'Desktop') {
    throw "Microsoft.PowerApps.Administration.PowerShell requires Windows PowerShell 5.1 (Desktop). Detected: $($PSVersionTable.PSEdition) $($PSVersionTable.PSVersion)."
}

Add-PowerAppsAccount -Endpoint $Endpoint | Out-Null

$inventory = New-Object System.Collections.Generic.List[object]
$envs = Get-AdminPowerAppEnvironment
if ($EnvironmentFilter) { $envs = $envs | Where-Object { $EnvironmentFilter -contains $_.EnvironmentName } }

foreach ($env in $envs) {
    Write-Host "[1.27] Environment: $($env.DisplayName)" -ForegroundColor Cyan
    $agents = Get-AdminPowerAppChatbot -EnvironmentName $env.EnvironmentName -ErrorAction SilentlyContinue
    foreach ($agent in $agents) {
        $cm  = $agent.Properties.ContentModeration
        $lvl = if ($cm -and $cm.DefaultLevel) { [string]$cm.DefaultLevel } else { 'NotExposedByApi' }
        $msg = if ($cm -and $cm.SafetyMessage) { $true } else { $false }

        $inventory.Add([PSCustomObject]@{
            EnvironmentDisplayName  = $env.DisplayName
            EnvironmentId           = $env.EnvironmentName
            AgentDisplayName        = $agent.Properties.DisplayName
            BotId                   = $agent.ChatbotName
            EffectiveDefaultLevel   = $lvl
            CustomSafetyMessageSet  = $msg
            LastModifiedUtc         = $agent.Properties.LastModifiedTime
            GovernanceZone          = 'NEEDS_CLASSIFICATION'   # join with AgentZoneMapping.csv
            ApprovalStatus          = 'NEEDS_REVIEW'
            CapturedUtc             = (Get-Date).ToUniversalTime().ToString('o')
        })
    }
}

Write-FsiEvidence -Object $inventory -Name 'AgentModerationInventory' -EvidencePath $EvidencePath
Write-Host "[1.27] Inventory rows: $($inventory.Count)" -ForegroundColor Green
```

**Idempotency note.** This script writes a new timestamped JSON each run and **appends** to `manifest.json`. It does not mutate any tenant state.

---

## Script 2 — `Get-ModerationConfigChanges.ps1` (audit log query, read-only)

```powershell
<#
.SYNOPSIS
    Queries the Unified Audit Log for Copilot Studio admin operations that touch
    content moderation. Read-only.
.NOTES
    Operation names below are anticipated. Run a broad discovery query first
    (no -Operations filter) and adjust the $opPattern list to match your tenant.
#>
[CmdletBinding()]
param(
    [int]$DaysBack = 30,
    [string]$EvidencePath = ".\evidence\1.27",
    [string[]]$OpPatterns = @('UpdateChatbot','UpdateBot','ModifyModeration','PublishChatbot')
)

$ErrorActionPreference = 'Stop'

if (-not (Get-Command Search-UnifiedAuditLog -ErrorAction SilentlyContinue)) {
    throw "Search-UnifiedAuditLog not available. Install ExchangeOnlineManagement and run Connect-ExchangeOnline first."
}

$start = (Get-Date).AddDays(-[Math]::Abs($DaysBack))
$end   = Get-Date

Write-Host "[1.27] Querying Unified Audit Log $start → $end" -ForegroundColor Cyan
$raw = Search-UnifiedAuditLog -StartDate $start -EndDate $end `
    -RecordType PowerPlatformAdminActivity -ResultSize 5000 -ErrorAction SilentlyContinue

$matches = foreach ($e in $raw) {
    $op = [string]$e.Operations
    if ($OpPatterns | Where-Object { $op -like "*$_*" }) {
        $audit = try { $e.AuditData | ConvertFrom-Json } catch { $null }
        [PSCustomObject]@{
            CreationDateUtc = $e.CreationDate
            Operation       = $op
            User            = $e.UserIds
            EnvironmentId   = $audit.EnvironmentName
            BotId           = $audit.ChatbotName
            RawAuditData    = $audit
        }
    }
}

Write-FsiEvidence -Object @{
    QueryWindowStart = $start.ToUniversalTime().ToString('o')
    QueryWindowEnd   = $end.ToUniversalTime().ToString('o')
    OperationFilters = $OpPatterns
    EventCount       = ($matches | Measure-Object).Count
    Events           = $matches
} -Name 'ModerationConfigChanges' -EvidencePath $EvidencePath

Write-Host "[1.27] Matching events: $(($matches | Measure-Object).Count)" -ForegroundColor Green
```

---

## Script 3 — `Test-ZoneCompliance.ps1` (drift detection, read-only)

```powershell
<#
.SYNOPSIS
    Joins the inventory from Script 1 with an AgentZoneMapping.csv and flags
    drift from required moderation level per zone.
.PARAMETER ZoneMappingFile
    CSV: BotId,AgentDisplayName,GovernanceZone,RequiredModeration
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string]$InventoryJsonPath,
    [Parameter(Mandatory)] [string]$ZoneMappingFile,
    [string]$EvidencePath = ".\evidence\1.27"
)

$ErrorActionPreference = 'Stop'
if (-not (Test-Path $InventoryJsonPath)) { throw "Inventory not found: $InventoryJsonPath" }
if (-not (Test-Path $ZoneMappingFile))   { throw "Zone mapping not found: $ZoneMappingFile" }

$inv = Get-Content $InventoryJsonPath -Raw | ConvertFrom-Json
$map = Import-Csv -Path $ZoneMappingFile

$results = foreach ($a in $inv) {
    $z = $map | Where-Object { $_.BotId -eq $a.BotId } | Select-Object -First 1
    $required = if ($z) { $z.RequiredModeration } else { 'UNKNOWN' }
    $zone     = if ($z) { $z.GovernanceZone } else { 'UNCLASSIFIED' }

    # Treat "Medium" and "Moderate" as synonyms (UI vs Learn terminology)
    $norm = { param($s) ($s -replace '(?i)^medium$','Moderate') }
    $compliant = ((& $norm $a.EffectiveDefaultLevel) -ieq (& $norm $required))

    [PSCustomObject]@{
        EnvironmentDisplayName = $a.EnvironmentDisplayName
        AgentDisplayName       = $a.AgentDisplayName
        BotId                  = $a.BotId
        Zone                   = $zone
        RequiredModeration     = $required
        ActualModeration       = $a.EffectiveDefaultLevel
        Compliant              = $compliant
        Severity               = if (-not $compliant -and $zone -eq 'Zone 3') { 'High' }
                                  elseif (-not $compliant -and $zone -eq 'Zone 2') { 'Medium' }
                                  elseif (-not $compliant) { 'Low' }
                                  else { 'None' }
    }
}

$summary = [PSCustomObject]@{
    Total          = ($results | Measure-Object).Count
    Compliant      = ($results | Where-Object Compliant).Count
    NonCompliant   = ($results | Where-Object { -not $_.Compliant }).Count
    HighSeverity   = ($results | Where-Object { $_.Severity -eq 'High' }).Count
    Results        = $results
}
Write-FsiEvidence -Object $summary -Name 'ZoneComplianceReport' -EvidencePath $EvidencePath
$summary | Select-Object Total, Compliant, NonCompliant, HighSeverity | Format-Table -AutoSize
```

---

## Script 4 — `Get-TopicModerationOverrides.ps1` (Dataverse Web API)

> No PowerShell admin cmdlet exposes per-topic moderation. The authoritative source is the Dataverse `botcomponents` entity (filter `componenttype eq 0` for topics) inside the agent's environment. This script issues an authenticated GET and emits hashed evidence.

```powershell
<#
.SYNOPSIS
    Pulls per-topic Generative answers nodes for a given agent via Dataverse Web API.
.PARAMETER OrgUrl
    e.g., https://contoso.crm.dynamics.com
.PARAMETER BotId
    The Dataverse bot id (ChatbotName from Script 1 output).
.PARAMETER AccessToken
    Bearer token with Dataverse user impersonation rights for the target org.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string]$OrgUrl,
    [Parameter(Mandatory)] [string]$BotId,
    [Parameter(Mandatory)] [string]$AccessToken,
    [string]$EvidencePath = ".\evidence\1.27"
)

$ErrorActionPreference = 'Stop'
$uri = "$OrgUrl/api/data/v9.2/botcomponents?`$filter=_parentbotid_value eq $BotId and componenttype eq 0&`$select=name,componentidunique,content"
$headers = @{
    Authorization      = "Bearer $AccessToken"
    'OData-Version'    = '4.0'
    'OData-MaxVersion' = '4.0'
    Accept             = 'application/json'
}
$resp = Invoke-RestMethod -Uri $uri -Headers $headers -Method GET

$topics = foreach ($t in $resp.value) {
    # Topic content is a YAML/JSON blob. We probe for any "moderation" key but do not parse the entire schema.
    $contentRaw = [string]$t.content
    $hasModeration = $contentRaw -match '(?i)contentmoderation|moderationlevel'
    [PSCustomObject]@{
        TopicName           = $t.name
        ComponentId         = $t.componentidunique
        HasGenerativeAnswers= ($contentRaw -match '(?i)GenerativeAnswers')
        HasModerationToken  = $hasModeration
        ContentPreviewSha256= ([System.BitConverter]::ToString(
                                  [System.Security.Cryptography.SHA256]::Create().ComputeHash(
                                      [System.Text.Encoding]::UTF8.GetBytes($contentRaw))).Replace('-',''))
    }
}

Write-FsiEvidence -Object @{
    BotId  = $BotId
    OrgUrl = $OrgUrl
    Topics = $topics
} -Name "TopicModerationOverrides-$BotId" -EvidencePath $EvidencePath

$topics | Format-Table -AutoSize
```

> **Why hash content instead of dumping it.** Topic YAML may contain prompt text, knowledge source URIs, or PII patterns — capturing it verbatim into evidence can create new SEC 17a-4 / GLBA exposure. The hash supports tamper-evidence without the raw content.

---

## Sample `AgentZoneMapping.csv`

```csv
BotId,AgentDisplayName,GovernanceZone,RequiredModeration
00000000-0000-0000-0000-000000000001,Customer Support Agent,Zone 3,High
00000000-0000-0000-0000-000000000002,HR Benefits Assistant,Zone 2,High
00000000-0000-0000-0000-000000000003,Personal Task Helper,Zone 1,Moderate
```

---

## Scheduling and Cadence

| Script | Zone 1 | Zone 2 | Zone 3 |
|---|---|---|---|
| `Get-AgentModerationInventory.ps1` | Quarterly | Monthly | Weekly |
| `Get-ModerationConfigChanges.ps1` (audit log) | Quarterly | Monthly | **Daily** between formal weekly reviews |
| `Test-ZoneCompliance.ps1` | Quarterly | Monthly | Weekly |
| `Get-TopicModerationOverrides.ps1` | On change | On change | Pre-publish + weekly |

---

## Known Limitations

| Limitation | Impact | Mitigation |
|---|---|---|
| `Properties.ContentModeration` is not a documented stable schema | Inventory may report `NotExposedByApi` | Fall back to portal inventory; document in evidence pack |
| No PS cmdlet for per-topic moderation | Script 4 requires Dataverse Web API + bearer token | Use service principal with least-privilege Dataverse role |
| Unified Audit Log default retention is 90 days (180 days with audit add-on) | Long-tail moderation history is lost | Forward to Sentinel / external SIEM with WORM retention (SEC 17a-4(f)) |
| Audit log operation names not all documented | Filters in Script 2 may miss events | Run discovery query first; widen `$OpPatterns` |
| `Microsoft.PowerApps.Administration.PowerShell` is Desktop-only | Scripts must run on Windows PS 5.1 | Desktop guard built into every script; do not strip it |

---

[Back to Control 1.27](../../../controls/pillar-1-security/1.27-ai-agent-content-moderation-enforcement.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification & Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
