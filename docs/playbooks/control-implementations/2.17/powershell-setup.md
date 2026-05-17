# PowerShell Setup: Control 2.17 — Multi-Agent Orchestration Limits

!!! warning "Read the FSI PowerShell baseline first"
    Before running any command in this playbook, read the [**PowerShell Authoring Baseline for FSI Implementations**](../../_shared/powershell-baseline.md). It is the canonical source for **module version pinning**, **sovereign-cloud (GCC / GCC High / DoD) endpoints**, **mutation safety** (`-WhatIf` / `SupportsShouldProcess`), **Dataverse compatibility**, and **SHA-256 evidence emission**. The snippets below are abbreviated; the baseline is authoritative.

**Last Updated:** April 2026
**Modules required:** `ExchangeOnlineManagement`, `Microsoft.PowerApps.Administration.PowerShell`, `Microsoft.Graph.Reports`
**Operation type:** Read-only (audit-log query, telemetry inspection, configuration reporting). No mutation cmdlets are required for this control — the orchestration controls themselves are authored in Copilot Studio and Power Automate (see *Portal Walkthrough*).

---

## 1. Prerequisites and Environment Setup

```powershell
# --- Edition guard (Power Apps admin module is Desktop-only) -----------------
if ($PSVersionTable.PSEdition -ne 'Desktop') {
    throw "Microsoft.PowerApps.Administration.PowerShell requires Windows PowerShell 5.1 (Desktop). Detected: $($PSVersionTable.PSEdition) $($PSVersionTable.PSVersion)."
}

# --- Module install (pin to CAB-approved versions) ---------------------------
# Replace <version> placeholders with the versions approved by your Change Advisory Board.
$modules = @(
    @{ Name = 'ExchangeOnlineManagement';                    Version = '<approved-version>' },
    @{ Name = 'Microsoft.PowerApps.Administration.PowerShell'; Version = '<approved-version>' },
    @{ Name = 'Microsoft.Graph.Reports';                     Version = '<approved-version>' }
)
foreach ($m in $modules) {
    Install-Module -Name $m.Name -RequiredVersion $m.Version `
        -Repository PSGallery -Scope CurrentUser -AllowClobber -AcceptLicense
}
```

```powershell
# --- Sovereign-cloud aware authentication ------------------------------------
param(
    [ValidateSet('prod','usgov','usgovhigh','dod')]
    [string]$Endpoint = 'prod'
)

$exoEnv = @{ prod = 'O365Default'; usgov = 'O365USGovGCCHigh'; usgovhigh = 'O365USGovGCCHigh'; dod = 'O365USGovDoD' }[$Endpoint]
Connect-ExchangeOnline -ShowBanner:$false -ExchangeEnvironmentName $exoEnv

Add-PowerAppsAccount -Endpoint $Endpoint
# For unattended execution prefer certificate-based service principal auth:
#   Add-PowerAppsAccount -Endpoint $Endpoint -TenantID <tid> -ApplicationId <aid> -CertificateThumbprint <thumb>
# Avoid -ClientSecret in production: secrets cannot be rotated without code changes and are flagged in audit reviews.
```

!!! danger "Sovereign-cloud false-clean risk"
    If you omit `-Endpoint` (Power Apps) or `-ExchangeEnvironmentName` (EXO), the cmdlets authenticate against commercial endpoints, return zero results from your gov-cloud tenant, and produce **false-clean evidence**. Always pass the explicit endpoint and verify the returned tenant ID matches your target before treating output as authoritative.

---

## 2. Query Orchestration Events from the Unified Audit Log

```powershell
<#
.SYNOPSIS
    Queries Microsoft Purview Unified Audit Log for Copilot Studio orchestration events.

.DESCRIPTION
    Read-only. Surfaces agent-to-agent invocations, tool/MCP calls, and any custom
    events emitted by the orchestration topics (Portal Walkthrough Step 6).
    Writes JSON + CSV evidence with SHA-256 manifest per the FSI baseline.

.PARAMETER StartDate
    Start of audit window (UTC). Default: 7 days ago.

.PARAMETER EndDate
    End of audit window (UTC). Default: now.

.PARAMETER EvidencePath
    Output folder for evidence artifacts. Default: .\evidence-2.17

.NOTES
    RecordType "CopilotInteraction" is the current Microsoft-documented record type
    for Copilot Studio agent activity (verified April 2026). Microsoft has historically
    renamed Copilot record types as the product evolved — re-verify against Microsoft
    Learn ("Audit log activities") before each quarterly review and update this script
    if the record type has changed in your tenant.
#>
[CmdletBinding()]
param(
    [datetime]$StartDate = (Get-Date).ToUniversalTime().AddDays(-7),
    [datetime]$EndDate   = (Get-Date).ToUniversalTime(),
    [string]  $EvidencePath = ".\evidence-2.17"
)

$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force -Path $EvidencePath | Out-Null
$ts = Get-Date -Format 'yyyyMMddTHHmmssZ'
Start-Transcript -Path (Join-Path $EvidencePath "transcript-$ts.log") -IncludeInvocationHeader

Write-Host "[INFO] Querying Copilot audit events $StartDate -> $EndDate (UTC)" -ForegroundColor Cyan

# Page through results — Search-UnifiedAuditLog is capped at 5000 per call.
$all = New-Object System.Collections.Generic.List[object]
$session = "fsi-2.17-$ts"
do {
    $page = Search-UnifiedAuditLog `
        -StartDate $StartDate -EndDate $EndDate `
        -RecordType 'CopilotInteraction' `
        -SessionId $session -SessionCommand ReturnLargeSet `
        -ResultSize 5000
    if ($page) { $all.AddRange($page) }
} while ($page -and $page.Count -eq 5000)

Write-Host "[INFO] Retrieved $($all.Count) raw audit records" -ForegroundColor Cyan

$events = foreach ($r in $all) {
    $d = $r.AuditData | ConvertFrom-Json -ErrorAction SilentlyContinue
    [PSCustomObject]@{
        TimestampUtc     = $r.CreationDate.ToUniversalTime().ToString('o')
        UserIds          = $r.UserIds
        Operation        = $d.Operation
        AgentId          = $d.AgentId
        AgentName        = $d.AgentName
        TargetAgent      = $d.TargetAgent
        DelegationDepth  = $d.DelegationDepth
        CorrelationId    = $d.CorrelationId
        Success          = ($d.ResultStatus -eq 'Success')
        ResultStatus     = $d.ResultStatus
    }
}

# Emit evidence (JSON + CSV + SHA-256 manifest per baseline §5)
$jsonPath = Join-Path $EvidencePath "orchestration-events-$ts.json"
$csvPath  = Join-Path $EvidencePath "orchestration-events-$ts.csv"
$events | ConvertTo-Json -Depth 10 | Set-Content -Path $jsonPath -Encoding UTF8
$events | Export-Csv      -Path $csvPath -NoTypeInformation -Encoding UTF8

$manifest = foreach ($f in @($jsonPath, $csvPath)) {
    [PSCustomObject]@{
        file          = Split-Path $f -Leaf
        sha256        = (Get-FileHash -Path $f -Algorithm SHA256).Hash
        bytes         = (Get-Item $f).Length
        generated_utc = $ts
        script        = 'fsi-2.17-orchestration-events'
        window_start  = $StartDate.ToString('o')
        window_end    = $EndDate.ToString('o')
    }
}
$manifest | ConvertTo-Json -Depth 5 | Set-Content -Path (Join-Path $EvidencePath "manifest-$ts.json") -Encoding UTF8

Stop-Transcript
Write-Host "[PASS] Evidence written to $EvidencePath" -ForegroundColor Green
```

!!! warning "Zero events ≠ control passing"
    A query that returns zero events is **not** evidence the control is working. It can equally indicate: (a) no orchestration occurred in the window, (b) audit logging is not enabled (Control 1.7), (c) the record type was renamed, or (d) wrong cloud endpoint. Cross-check against expected orchestration volume from the agent inventory (Control 2.1) and document the interpretation in the evidence manifest.

---

## 3. Inspect Application Insights Custom Orchestration Telemetry

The orchestration topics emit five custom events (see *Portal Walkthrough* Step 6). Query them via Azure CLI or KQL to validate emission volume and surface depth-limit violations.

```powershell
# Requires Az.ApplicationInsights module (pinned per baseline §1)
$kql = @'
union customEvents
| where timestamp >= ago(7d)
| where name startswith "Orchestration."
| extend correlationId = tostring(customDimensions.correlationId),
         depth         = toint(customDimensions.depth),
         zone          = tostring(customDimensions.zone),
         childAgentId  = tostring(customDimensions.childAgentId)
| summarize Events=count(),
            MaxDepth=max(depth),
            UniqueChains=dcount(correlationId)
        by name, zone
| order by zone, name
'@

$result = Invoke-AzOperationalInsightsQuery `
    -WorkspaceId $WorkspaceId `
    -Query $kql `
    -Timespan (New-TimeSpan -Days 7)

$result.Results | Format-Table -AutoSize
```

**Interpretation guide:**

| Observation | Likely meaning | Action |
|-------------|----------------|--------|
| `Orchestration.DelegationStart` count > 0 but `Orchestration.DelegationEnd` ≪ start count | Delegations time out or fail silently | Check circuit-breaker thresholds; review error handling in topics |
| `MaxDepth` exceeds zone limit | Depth tracking broken or limit not enforced | Treat as policy violation; trigger Control 3.4 incident workflow |
| `Orchestration.CircuitBreakerOpen` > 0 in 24h | Cascading failure or unhealthy downstream | Investigate target agent; do not just raise threshold |
| `Orchestration.HitlDecision` with very short `waitDurationMs` | Possible rubber-stamping | Sample for quality review (FINRA Rule 3110 supervisory review evidence) |
| `Orchestration.MCP.ToolInvocation` for unapproved `mcpServer` | Drift from approved registry | Block at DLP layer; investigate how the unapproved server was added |

---

## 4. Validate Per-Agent Tool-Count Headroom

Each Copilot Studio agent is capped at 128 tools. Multi-agent designs that grow over time can hit this ceiling and silently start dropping new tool registrations.

```powershell
# Pulls tool counts via the Power Apps admin API (read-only).
Get-AdminPowerApp | Where-Object { $_.AppType -eq 'CopilotAgent' } | ForEach-Object {
    [PSCustomObject]@{
        AgentName       = $_.DisplayName
        EnvironmentName = $_.EnvironmentName
        ToolCount       = ($_.Internal.properties.tools | Measure-Object).Count
        Headroom        = 128 - (($_.Internal.properties.tools | Measure-Object).Count)
        Owner           = $_.Owner.email
    }
} | Sort-Object Headroom | Format-Table -AutoSize
```

!!! note "API surface volatility"
    The Copilot Studio agent inventory surface in Power Apps admin cmdlets has changed across module versions. If `properties.tools` returns `$null`, your module version may not yet expose this property — fall back to per-agent inspection in the Copilot Studio portal and log a control-debt item.

---

## 5. Quarterly Compliance Validation Script

Run this once per quarter as part of your governance cadence (see Control 2.12) and retain evidence per SEC 17a-4 (typically 6 years for FSI).

```powershell
<#
.SYNOPSIS  Quarterly Control 2.17 attestation pack generator.
.DESCRIPTION  Read-only. Aggregates 90 days of orchestration evidence into a
              single attestation pack with SHA-256 manifest for the AI
              Governance Lead's signature.
#>
[CmdletBinding()]
param(
    [string]$EvidencePath = ".\evidence-2.17-quarterly-$((Get-Date).ToString('yyyyMM'))"
)

$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force -Path $EvidencePath | Out-Null

# 1. 90-day audit-log pull
& "$PSScriptRoot\Get-OrchestrationEvents.ps1" `
    -StartDate (Get-Date).AddDays(-90).ToUniversalTime() `
    -EvidencePath $EvidencePath

# 2. Tool-count snapshot
& "$PSScriptRoot\Get-AgentToolCounts.ps1" `
    -EvidencePath $EvidencePath

# 3. Approved MCP-server registry export (placeholder — adapt to your registry source)
#    Example: pull from SharePoint list, Dataverse, or governance ITSM.

# 4. Generate attestation cover sheet
$cover = [PSCustomObject]@{
    Control                 = '2.17'
    Title                   = 'Multi-Agent Orchestration Limits'
    PeriodStartUtc          = (Get-Date).AddDays(-90).ToUniversalTime().ToString('o')
    PeriodEndUtc            = (Get-Date).ToUniversalTime().ToString('o')
    GeneratedUtc            = (Get-Date).ToUniversalTime().ToString('o')
    GeneratedByUpn          = (whoami /upn 2>$null)
    EvidencePath            = (Resolve-Path $EvidencePath).Path
    AttestationStatement    = 'Reviewed and confirmed compliant — _____________________'
    SignerUpn               = ''
    SignerDateUtc           = ''
}
$cover | ConvertTo-Json -Depth 5 | Set-Content -Path (Join-Path $EvidencePath 'attestation.json') -Encoding UTF8

Write-Host "[PASS] Attestation pack at $EvidencePath" -ForegroundColor Green
Write-Host "[NEXT] AI Governance Lead must review, sign attestation.json, and lodge in WORM storage." -ForegroundColor Yellow
```

---

## 6. What This Script Does NOT Do

To keep the FSI threat model honest, the script set above explicitly does **not**:

- **Configure** orchestration limits — those live in Copilot Studio topics and Power Automate flows (*Portal Walkthrough*).
- **Enforce** depth limits or circuit breakers in the Copilot Studio runtime — there is no admin API surface for this as of April 2026.
- **Modify** any tenant or environment state — all cmdlets are read-only.
- **Substitute** for SOC monitoring — these scripts produce *evidence*; real-time detection belongs in Sentinel / your SIEM (Control 1.24).

If a future Microsoft release adds admin API surface for orchestration limits, this playbook will be updated and the change recorded in the control's footer date.

---

[Back to Control 2.17](../../../controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification & Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
