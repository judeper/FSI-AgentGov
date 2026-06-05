# PowerShell Setup: Control 2.9 - Agent Performance Monitoring and Optimization

!!! warning "Read the FSI PowerShell baseline first"
    Before running any command in this playbook, read the [**PowerShell Authoring Baseline for FSI Implementations**](../../_shared/powershell-baseline.md). It is the canonical source for module version pinning, mutation safety (`-WhatIf` / `SupportsShouldProcess`), Dataverse compatibility, and SHA-256 evidence emission. Snippets below show abbreviated patterns; the baseline is authoritative.

**Last Updated:** April 2026
**Modules Required:** `Microsoft.PowerApps.Administration.PowerShell`, `Microsoft.Graph` (Reports + ServiceMessage), `Az.ApplicationInsights`, `Az.Monitor`, `MicrosoftPowerBIMgmt`
**Edition:** Mixed — `Microsoft.PowerApps.Administration.PowerShell` requires Windows PowerShell 5.1 (Desktop). Az and Microsoft.Graph run on PowerShell 7+.

---

## Prerequisites

```powershell
# Pin all versions per your CAB-approved baseline. Replace <version> values.
Install-Module -Name Microsoft.PowerApps.Administration.PowerShell -RequiredVersion '<version>' -Repository PSGallery -Scope CurrentUser -AllowClobber -AcceptLicense
Install-Module -Name Microsoft.Graph                              -RequiredVersion '<version>' -Repository PSGallery -Scope CurrentUser -AllowClobber -AcceptLicense
Install-Module -Name Az.ApplicationInsights                       -RequiredVersion '<version>' -Repository PSGallery -Scope CurrentUser -AllowClobber -AcceptLicense
Install-Module -Name Az.Monitor                                   -RequiredVersion '<version>' -Repository PSGallery -Scope CurrentUser -AllowClobber -AcceptLicense
Install-Module -Name MicrosoftPowerBIMgmt                         -RequiredVersion '<version>' -Repository PSGallery -Scope CurrentUser -AllowClobber -AcceptLicense
```

---

## 1 — Inventory agents and their analytics posture

This script enumerates every Microsoft Copilot Studio agent in the tenant and records whether tenant analytics is reachable. **Read-only.** Safe to run in production.

```powershell
<#
.SYNOPSIS
    Inventories Copilot Studio agents per environment and emits SHA-256 hashed evidence.

.EXAMPLE
    .\Get-AgentInventory.ps1 -EvidencePath .\evidence\2.9
#>

[CmdletBinding()]
param(
    [string]$EvidencePath = ".\evidence\2.9"
)

$ErrorActionPreference = 'Stop'

if ($PSVersionTable.PSEdition -ne 'Desktop') {
    throw "Microsoft.PowerApps.Administration.PowerShell requires Windows PowerShell 5.1 (Desktop). Detected: $($PSVersionTable.PSEdition) $($PSVersionTable.PSVersion)."
}

New-Item -ItemType Directory -Force -Path $EvidencePath | Out-Null
$ts = Get-Date -Format 'yyyyMMdd-HHmmss'
Start-Transcript -Path "$EvidencePath\transcript-inventory-$ts.log" -IncludeInvocationHeader

Add-PowerAppsAccount

$inventory = foreach ($env in (Get-AdminPowerAppEnvironment)) {
    $agents = Get-AdminPowerAppChatBot -EnvironmentName $env.EnvironmentName -ErrorAction SilentlyContinue
    foreach ($agent in $agents) {
        [PSCustomObject]@{
            Environment       = $env.DisplayName
            EnvironmentId     = $env.EnvironmentName
            DataverseBacked   = ($env.CommonDataServiceDatabaseProvisioningState -eq 'Succeeded')
            AgentName         = $agent.DisplayName
            AgentId           = $agent.Name
            CreatedTime       = $agent.CreatedTime
            LastModifiedTime  = $agent.LastModifiedTime
            Status            = $agent.Properties.status
            CollectedUtc      = (Get-Date).ToUniversalTime().ToString('o')
            Endpoint          = $Endpoint
        }
    }
}

# Emit JSON + SHA-256 manifest
$jsonPath = Join-Path $EvidencePath "agent-inventory-$ts.json"
$inventory | ConvertTo-Json -Depth 10 | Set-Content -Path $jsonPath -Encoding UTF8
$hash = (Get-FileHash -Path $jsonPath -Algorithm SHA256).Hash

$manifestPath = Join-Path $EvidencePath "manifest.json"
$manifest = if (Test-Path $manifestPath) { @(Get-Content $manifestPath | ConvertFrom-Json) } else { @() }
$manifest += [PSCustomObject]@{
    file           = (Split-Path $jsonPath -Leaf)
    sha256         = $hash
    bytes          = (Get-Item $jsonPath).Length
    generated_utc  = $ts
    script         = 'Get-AgentInventory.ps1'
    endpoint       = $Endpoint
}
$manifest | ConvertTo-Json -Depth 5 | Set-Content -Path $manifestPath -Encoding UTF8

Write-Host "Inventoried $($inventory.Count) agents. Evidence: $jsonPath  SHA256: $hash" -ForegroundColor Green
Stop-Transcript
```

---

## 2 — Verify Application Insights linkage on each Zone 2/3 agent

Detects agents missing the App Insights connection string (a frequent gap that yields the false impression of "monitored"). **Read-only.**

```powershell
<#
.SYNOPSIS
    For each agent in a target list, verifies Application Insights linkage by querying
    the App Insights resource for ingested telemetry within the last 24 hours.

.PARAMETER AgentMappingPath
    CSV with columns: AgentId, AgentName, ApplicationInsightsResourceId
.EXAMPLE
    .\Test-AppInsightsLinkage.ps1 -AgentMappingPath .\agent-appinsights-map.csv
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string]$AgentMappingPath,
    [string]$EvidencePath = ".\evidence\2.9"
)

$ErrorActionPreference = 'Stop'
Connect-AzAccount -ErrorAction Stop | Out-Null

$results = foreach ($row in (Import-Csv $AgentMappingPath)) {
    try {
        $kql = @"
union requests, customEvents, exceptions
| where timestamp > ago(24h)
| summarize Total = count()
"@
        $resp = Invoke-AzOperationalInsightsQuery -ResourceId $row.ApplicationInsightsResourceId -Query $kql -ErrorAction Stop
        $count = [int]$resp.Results[0].Total
        [PSCustomObject]@{
            AgentName    = $row.AgentName
            AgentId      = $row.AgentId
            Telemetry24h = $count
            Status       = if ($count -gt 0) { 'PASS' } else { 'WARN-empty' }
            CheckedUtc   = (Get-Date).ToUniversalTime().ToString('o')
        }
    } catch {
        [PSCustomObject]@{
            AgentName    = $row.AgentName
            AgentId      = $row.AgentId
            Telemetry24h = $null
            Status       = "FAIL: $($_.Exception.Message)"
            CheckedUtc   = (Get-Date).ToUniversalTime().ToString('o')
        }
    }
}

New-Item -ItemType Directory -Force -Path $EvidencePath | Out-Null
$ts = Get-Date -Format 'yyyyMMdd-HHmmss'
$out = Join-Path $EvidencePath "appinsights-linkage-$ts.json"
$results | ConvertTo-Json -Depth 5 | Set-Content -Path $out -Encoding UTF8
$hash = (Get-FileHash $out -Algorithm SHA256).Hash
Write-Host "Wrote $out  SHA256: $hash" -ForegroundColor Green

$results | Format-Table -AutoSize
```

---

## 3 — Pull operational KPIs from Application Insights (KQL)

Produces the latency and error metrics required for Fed SR 26-2 (formerly SR 11-7) / OCC Bulletin 2026-13 (formerly OCC 2011-12) quarterly model performance memos.

```powershell
<#
.SYNOPSIS
    Computes p50/p95/p99 latency, error rate, and session counts per agent over a window.

.EXAMPLE
    .\Get-AgentKpis.ps1 -ResourceId '/subscriptions/.../components/ai-fsi-agents' -DaysBack 30
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string]$ResourceId,
    [int]$DaysBack = 30,
    [string]$EvidencePath = ".\evidence\2.9"
)

$ErrorActionPreference = 'Stop'
Connect-AzAccount -ErrorAction Stop | Out-Null

$kql = @"
let lookback = $DaysBack`d;
requests
| where timestamp > ago(lookback)
| extend AgentName = tostring(customDimensions['botName'])
| summarize
    sessions   = dcount(session_Id),
    requests   = count(),
    failures   = countif(success == false),
    p50_ms     = percentile(duration, 50),
    p95_ms     = percentile(duration, 95),
    p99_ms     = percentile(duration, 99)
  by AgentName
| extend errorRatePct = round(100.0 * failures / requests, 3)
| order by sessions desc
"@

$resp = Invoke-AzOperationalInsightsQuery -ResourceId $ResourceId -Query $kql

New-Item -ItemType Directory -Force -Path $EvidencePath | Out-Null
$ts = Get-Date -Format 'yyyyMMdd-HHmmss'
$out = Join-Path $EvidencePath "kpis-$DaysBack-day-$ts.json"
$resp.Results | ConvertTo-Json -Depth 5 | Set-Content -Path $out -Encoding UTF8
$hash = (Get-FileHash $out -Algorithm SHA256).Hash
Write-Host "KPI export: $out  SHA256: $hash" -ForegroundColor Green
```

---

## 4 — Threshold check against zone KPIs

Compares actual KPIs from script 3 against the zone thresholds. Returns non-zero exit code on breach (suitable for CI / scheduled runbook).

```powershell
<#
.SYNOPSIS
    Evaluates KPI export against per-zone thresholds. Exits non-zero if any agent breaches.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string]$KpiJsonPath,
    [Parameter(Mandatory)] [ValidateSet('1','2','3')] [string]$Zone
)

$thresholds = @{
    '1' = @{ ErrorRatePct = 5.0; P95Ms = 30000 }
    '2' = @{ ErrorRatePct = 2.0; P95Ms = 15000 }
    '3' = @{ ErrorRatePct = 1.0; P95Ms = 5000  }
}[$Zone]

$kpis = Get-Content $KpiJsonPath | ConvertFrom-Json
$breaches = $kpis | Where-Object {
    $_.errorRatePct -gt $thresholds.ErrorRatePct -or $_.p95_ms -gt $thresholds.P95Ms
}

foreach ($k in $kpis) {
    $tag = if ($breaches.AgentName -contains $k.AgentName) { '[BREACH]' } else { '[OK]    ' }
    "{0} {1,-40} err={2,6:N2}%  p95={3,7:N0}ms  sessions={4}" -f $tag, $k.AgentName, $k.errorRatePct, $k.p95_ms, $k.sessions | Write-Host
}

if ($breaches) {
    Write-Host "`n$($breaches.Count) agent(s) breached Zone $Zone thresholds." -ForegroundColor Red
    exit 2
}
Write-Host "All agents within Zone $Zone thresholds." -ForegroundColor Green
```

---

## 5 — Idempotent provisioning of an Azure Monitor alert rule (Zone 3)

This **mutates tenant state**. Uses `SupportsShouldProcess`; always invoke with `-WhatIf` first.

```powershell
<#
.SYNOPSIS
    Creates or updates an Azure Monitor metric alert on Application Insights request failure rate.

.EXAMPLE
    .\Set-FailureRateAlert.ps1 `
        -ResourceId '/subscriptions/.../components/ai-fsi-agents' `
        -ActionGroupId '/subscriptions/.../actionGroups/ag-fsi-ai-oncall' `
        -ThresholdPct 1.0 `
        -WhatIf
#>

[CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
param(
    [Parameter(Mandatory)] [string]$ResourceId,
    [Parameter(Mandatory)] [string]$ActionGroupId,
    [double]$ThresholdPct  = 1.0,
    [string]$AlertRuleName = 'fsi-ai-failure-rate-zone3',
    [string]$ResourceGroup = (Split-Path $ResourceId -Parent | Split-Path -Parent | Split-Path -Leaf),
    [string]$EvidencePath  = ".\evidence\2.9"
)

$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force -Path $EvidencePath | Out-Null
$ts = Get-Date -Format 'yyyyMMdd-HHmmss'
Start-Transcript -Path "$EvidencePath\transcript-alert-$ts.log" -IncludeInvocationHeader

Connect-AzAccount -ErrorAction Stop | Out-Null

# BEFORE snapshot
$before = Get-AzMetricAlertRuleV2 -ResourceGroupName $ResourceGroup -Name $AlertRuleName -ErrorAction SilentlyContinue
$before | ConvertTo-Json -Depth 10 | Set-Content "$EvidencePath\alert-before-$ts.json"

if ($PSCmdlet.ShouldProcess($AlertRuleName, "Create/update failure-rate alert at $ThresholdPct%")) {
    $criteria = New-AzMetricAlertRuleV2Criteria `
        -MetricName 'requests/failed' `
        -TimeAggregation Total `
        -Operator GreaterThan `
        -Threshold $ThresholdPct

    Add-AzMetricAlertRuleV2 `
        -Name              $AlertRuleName `
        -ResourceGroupName $ResourceGroup `
        -WindowSize        ([TimeSpan]::FromMinutes(5)) `
        -Frequency         ([TimeSpan]::FromMinutes(1)) `
        -TargetResourceId  $ResourceId `
        -Description       'FSI AI failure rate breach (Zone 3) — Control 2.9' `
        -Severity          1 `
        -ActionGroupId     $ActionGroupId `
        -Condition         $criteria | Out-Null

    $after = Get-AzMetricAlertRuleV2 -ResourceGroupName $ResourceGroup -Name $AlertRuleName
    $after | ConvertTo-Json -Depth 10 | Set-Content "$EvidencePath\alert-after-$ts.json"
}

Stop-Transcript
```

---

## 6 — Validation script (Control 2.9 self-check)

```powershell
<#
.SYNOPSIS
    Read-only validation that Control 2.9 components are in place.
#>

[CmdletBinding()]
param(
    [string]$EvidencePath = ".\evidence\2.9"
)

$ErrorActionPreference = 'Continue'
$results = @()

# 1. Native analytics reachable
try {
    Add-PowerAppsAccount -Endpoint prod | Out-Null
    $envs = Get-AdminPowerAppEnvironment
    $results += [PSCustomObject]@{ Check='PPAC analytics reachable'; Status='PASS'; Detail="$($envs.Count) environments" }
} catch {
    $results += [PSCustomObject]@{ Check='PPAC analytics reachable'; Status='FAIL'; Detail=$_.Exception.Message }
}

# 2. Power BI workspace exists
try {
    Connect-PowerBIServiceAccount | Out-Null
    $ws = Get-PowerBIWorkspace -Name 'Agent-Performance-Analytics' -ErrorAction SilentlyContinue
    if ($ws) {
        $reports = Get-PowerBIReport -WorkspaceId $ws.Id
        $results += [PSCustomObject]@{ Check='Power BI workspace'; Status='PASS'; Detail="$($reports.Count) reports" }
    } else {
        $results += [PSCustomObject]@{ Check='Power BI workspace'; Status='FAIL'; Detail='Agent-Performance-Analytics not found' }
    }
    Disconnect-PowerBIServiceAccount | Out-Null
} catch {
    $results += [PSCustomObject]@{ Check='Power BI workspace'; Status='WARN'; Detail=$_.Exception.Message }
}

# 3. Evidence freshness
$latest = Get-ChildItem $EvidencePath -Filter '*.json' -ErrorAction SilentlyContinue |
          Sort-Object LastWriteTime -Descending | Select-Object -First 1
if ($latest -and $latest.LastWriteTime -gt (Get-Date).AddDays(-7)) {
    $results += [PSCustomObject]@{ Check='Evidence freshness'; Status='PASS'; Detail="$($latest.Name) ($($latest.LastWriteTime))" }
} else {
    $results += [PSCustomObject]@{ Check='Evidence freshness'; Status='FAIL'; Detail='No evidence in last 7 days' }
}

$results | Format-Table -AutoSize
$failed = ($results | Where-Object Status -eq 'FAIL').Count
exit $failed
```

---

[Back to Control 2.9](../../../controls/pillar-2-management/2.9-agent-performance-monitoring-and-optimization.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification & Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
