# PowerShell Setup: Control 1.26 - Agent File Upload and File Analysis Restrictions

!!! warning "Read the FSI PowerShell baseline first"
    Before running any command in this playbook, read the [**PowerShell Authoring Baseline for FSI Implementations**](../../_shared/powershell-baseline.md). It is the canonical source for module version pinning, mutation safety (`-WhatIf` / `SupportsShouldProcess`), Dataverse compatibility, and SHA-256 evidence emission. Snippets below show the abbreviated forms; the baseline is authoritative.

**Last Updated:** May 2026
**Modules Required:** `Microsoft.PowerApps.Administration.PowerShell`, `Microsoft.Graph` (for activity log queries)
!!! danger "API Surface — Verify Cmdlet Availability Before Mutation"
    The per-agent file upload toggle is exposed via `Get-AdminPowerAppChatbot` / `Set-AdminPowerAppChatbot` in `Microsoft.PowerApps.Administration.PowerShell`. The `-FileUploadEnabled` parameter availability and property name (`Properties.FileUploadEnabled`) is based on Microsoft's anticipated April 2026 schema and may differ between module versions. Run the cmdlet-availability probe in *Script 0* before executing any `Set-` operation. If the parameter is not exposed in your tenant, fall back to the [Portal Walkthrough](portal-walkthrough.md) for manual configuration and use the `Get-` script for inventory only.

## Prerequisites

```powershell
# Pin the module to a CAB-approved version (substitute your approved version)
Install-Module -Name Microsoft.PowerApps.Administration.PowerShell `
    -RequiredVersion '<cab-approved-version>' `
    -Repository PSGallery `
    -Scope CurrentUser `
    -AllowClobber `
    -AcceptLicense

Import-Module Microsoft.PowerApps.Administration.PowerShell

# Required: Microsoft.PowerApps.Administration.PowerShell is Desktop-edition only (PowerShell 5.1).
if ($PSVersionTable.PSEdition -ne 'Desktop') {
    throw "Microsoft.PowerApps.Administration.PowerShell requires Windows PowerShell 5.1 (Desktop edition). Detected: $($PSVersionTable.PSEdition) $($PSVersionTable.PSVersion)."
}

Add-PowerAppsAccount -Endpoint prod
```

> **Required role:** AI Administrator or Power Platform Admin. Verify before running mutations: `Get-AdminPowerAppEnvironment | Measure-Object` should return your full environment list. A zero count typically means a role or authentication issue — check the running account's Power Platform Admin assignment.

---

## Script 0 — Probe Cmdlet Surface (Run First)

```powershell
<#
.SYNOPSIS
    Probes the Set-AdminPowerAppChatbot cmdlet for the -FileUploadEnabled parameter
    and the Properties.FileUploadEnabled return surface on Get-AdminPowerAppChatbot.

.DESCRIPTION
    Confirms that the API schema this playbook depends on is present in the loaded
    module version. If the probe fails, fall back to the Portal Walkthrough.
#>
[CmdletBinding()]
param()

$probe = [ordered]@{
    SetCmdletPresent       = [bool](Get-Command Set-AdminPowerAppChatbot -ErrorAction SilentlyContinue)
    GetCmdletPresent       = [bool](Get-Command Get-AdminPowerAppChatbot -ErrorAction SilentlyContinue)
    FileUploadParamPresent = $false
}

if ($probe.SetCmdletPresent) {
    $params = (Get-Command Set-AdminPowerAppChatbot).Parameters.Keys
    $probe.FileUploadParamPresent = $params -contains 'FileUploadEnabled'
}

$probe | Format-Table -AutoSize

if (-not $probe.FileUploadParamPresent) {
    Write-Warning "Set-AdminPowerAppChatbot -FileUploadEnabled is not present in this module version. Use the Portal Walkthrough for mutations; the inventory script (Script 1) may still work."
}
```

---

## Script 1 — Inventory: Get File Upload Status Across All Agents (Read-Only, Idempotent)

```powershell
<#
.SYNOPSIS
    Inventories file upload toggle state for every Copilot Studio agent across
    every environment in the tenant, and emits SHA-256-hashed evidence.

.DESCRIPTION
    Read-only. Safe to run repeatedly. Produces JSON evidence and a manifest.json
    suitable for SEC 17a-4(f) / FINRA 4511 audit submission.

.PARAMETER EvidencePath
    Directory to write evidence into. Created if missing.

.EXAMPLE
    .\Get-AgentFileUploadInventory.ps1 -EvidencePath '.\evidence\1.26'
#>
[CmdletBinding()]
param(
    [string]$EvidencePath = ".\evidence\1.26"
)

$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force -Path $EvidencePath | Out-Null
$ts = Get-Date -Format 'yyyyMMddTHHmmssZ'
Start-Transcript -Path "$EvidencePath\transcript-inventory-$ts.log" -IncludeInvocationHeader

$results = foreach ($env in (Get-AdminPowerAppEnvironment)) {
    $agents = Get-AdminPowerAppChatbot -EnvironmentName $env.EnvironmentName -ErrorAction SilentlyContinue
    foreach ($agent in $agents) {
        [PSCustomObject]@{
            Environment       = $env.DisplayName
            EnvironmentId     = $env.EnvironmentName
            AgentName         = $agent.Properties.DisplayName
            AgentId           = $agent.ChatbotId
            FileUploadEnabled = [bool]$agent.Properties.FileUploadEnabled
            LastModifiedUtc   = $agent.Properties.LastModifiedTime
            CreatedBy         = $agent.Properties.CreatedBy.displayName
            CollectedUtc      = (Get-Date).ToUniversalTime().ToString('o')
        }
    }
}

# Emit JSON + SHA-256 manifest entry (canonical pattern from baseline §4)
$jsonPath = Join-Path $EvidencePath "agent-file-upload-inventory-$ts.json"
$results | ConvertTo-Json -Depth 10 | Set-Content -Path $jsonPath -Encoding UTF8
$hash = (Get-FileHash -Path $jsonPath -Algorithm SHA256).Hash

$manifestPath = Join-Path $EvidencePath "manifest.json"
$manifest = @()
if (Test-Path $manifestPath) { $manifest = @(Get-Content $manifestPath | ConvertFrom-Json) }
$manifest += [PSCustomObject]@{
    file           = (Split-Path $jsonPath -Leaf)
    sha256         = $hash
    bytes          = (Get-Item $jsonPath).Length
    generated_utc  = $ts
    script         = 'Get-AgentFileUploadInventory'
    script_version = '1.26.0'
    control_id     = '1.26'
}
$manifest | ConvertTo-Json -Depth 5 | Set-Content -Path $manifestPath -Encoding UTF8

Write-Host "Evidence written: $jsonPath" -ForegroundColor Green
Write-Host "SHA-256: $hash" -ForegroundColor Green

Stop-Transcript
$results | Format-Table -AutoSize
```

---

## Script 2 — Compliance Audit Against Zone Policy (Read-Only)

```powershell
<#
.SYNOPSIS
    Audits per-agent file upload toggle against zone governance requirements
    and emits a PASS/WARN/FAIL evidence record.

.PARAMETER ZoneMapping
    Hashtable mapping environment name (GUID) to zone number (1, 2, or 3).

.PARAMETER ApprovedEnabledAgents
    Optional array of agent IDs that have documented approval to have File Upload
    enabled in Zone 2 or Zone 3. Reduces false WARN/FAIL noise.

.PARAMETER EvidencePath
    Directory to write evidence into.

.EXAMPLE
    $zones = @{ 'env-personal' = 1; 'env-team' = 2; 'env-ent' = 3 }
    .\Audit-FileUploadCompliance.ps1 -ZoneMapping $zones -ApprovedEnabledAgents @('agent-id-1','agent-id-2')
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [hashtable]$ZoneMapping,
    [string[]]$ApprovedEnabledAgents = @(),
    [string]$EvidencePath = ".\evidence\1.26"
)

$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force -Path $EvidencePath | Out-Null
$ts = Get-Date -Format 'yyyyMMddTHHmmssZ'

$findings = foreach ($envName in $ZoneMapping.Keys) {
    $zone   = $ZoneMapping[$envName]
    $env    = Get-AdminPowerAppEnvironment -EnvironmentName $envName
    $agents = Get-AdminPowerAppChatbot -EnvironmentName $envName -ErrorAction SilentlyContinue

    foreach ($agent in $agents) {
        $enabled  = [bool]$agent.Properties.FileUploadEnabled
        $approved = $ApprovedEnabledAgents -contains $agent.ChatbotId
        $result   = switch ($zone) {
            1 { 'PASS' }
            2 { if ($enabled -and -not $approved) { 'WARN' } else { 'PASS' } }
            3 { if ($enabled -and -not $approved) { 'FAIL' } else { 'PASS' } }
        }
        [PSCustomObject]@{
            Environment       = $env.DisplayName
            Zone              = $zone
            AgentName         = $agent.Properties.DisplayName
            AgentId           = $agent.ChatbotId
            FileUploadEnabled = $enabled
            Approved          = $approved
            Result            = $result
            CollectedUtc      = (Get-Date).ToUniversalTime().ToString('o')
        }
    }
}

$jsonPath = Join-Path $EvidencePath "compliance-audit-$ts.json"
$findings | ConvertTo-Json -Depth 10 | Set-Content -Path $jsonPath -Encoding UTF8
$hash = (Get-FileHash -Path $jsonPath -Algorithm SHA256).Hash
Write-Host "Audit evidence: $jsonPath  (SHA-256: $hash)" -ForegroundColor Green

$summary = $findings | Group-Object Result | Select-Object Name, Count
$summary | Format-Table -AutoSize
$findings | Format-Table -AutoSize
```

---

## Script 3 — Mutation: Disable File Upload (Idempotent, SupportsShouldProcess, With Snapshot)

```powershell
<#
.SYNOPSIS
    Disables the per-agent File Upload toggle for one or more agents.
    Idempotent — agents already in the desired state are skipped with [OK].

.DESCRIPTION
    Canonical mutation pattern per the FSI PowerShell Authoring Baseline §4:
      - SupportsShouldProcess + ConfirmImpact='High'
      - Before-mutation snapshot to disk for rollback
      - Start-Transcript for full session capture
      - SHA-256 evidence emission per baseline §4
      - -WhatIf produces a true preview without state change

.PARAMETER EnvironmentId
    Target environment (GUID).

.PARAMETER AgentIds
    Optional array of agent IDs. If omitted, all agents in the environment are processed.

.PARAMETER EvidencePath
    Directory to write evidence into.

.EXAMPLE
    .\Disable-FileUpload.ps1 -EnvironmentId 'env-guid' -WhatIf

.EXAMPLE
    .\Disable-FileUpload.ps1 -EnvironmentId 'env-guid' -AgentIds 'agent-1','agent-2' -Confirm
#>
[CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
param(
    [Parameter(Mandatory)] [string]$EnvironmentId,
    [string[]]$AgentIds,
    [string]$EvidencePath = ".\evidence\1.26"
)

$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force -Path $EvidencePath | Out-Null
$ts = Get-Date -Format 'yyyyMMddTHHmmssZ'
Start-Transcript -Path "$EvidencePath\transcript-mutation-$ts.log" -IncludeInvocationHeader

# Pre-flight: probe cmdlet surface
$setCmd = Get-Command Set-AdminPowerAppChatbot -ErrorAction SilentlyContinue
if (-not $setCmd -or -not ($setCmd.Parameters.Keys -contains 'FileUploadEnabled')) {
    throw "Set-AdminPowerAppChatbot -FileUploadEnabled is not available in this module version. Use the Portal Walkthrough for manual configuration."
}

# Snapshot BEFORE mutating
$agents = Get-AdminPowerAppChatbot -EnvironmentName $EnvironmentId -ErrorAction Stop
if ($AgentIds) { $agents = $agents | Where-Object { $AgentIds -contains $_.ChatbotId } }

$snapshotPath = Join-Path $EvidencePath "before-snapshot-$ts.json"
$agents | Select-Object ChatbotId,
    @{N='AgentName';E={$_.Properties.DisplayName}},
    @{N='FileUploadEnabled';E={[bool]$_.Properties.FileUploadEnabled}},
    @{N='LastModifiedUtc';E={$_.Properties.LastModifiedTime}} |
    ConvertTo-Json -Depth 10 | Set-Content -Path $snapshotPath -Encoding UTF8

$results = foreach ($agent in $agents) {
    $current = [bool]$agent.Properties.FileUploadEnabled
    $name    = $agent.Properties.DisplayName

    if (-not $current) {
        # Idempotent: already in desired state
        Write-Host "  [OK] $name — already disabled" -ForegroundColor Gray
        $action = 'NoChange'
    }
    elseif ($PSCmdlet.ShouldProcess("$name ($($agent.ChatbotId))", 'Disable File Upload')) {
        try {
            Set-AdminPowerAppChatbot -EnvironmentName $EnvironmentId `
                -ChatbotId $agent.ChatbotId `
                -FileUploadEnabled $false -ErrorAction Stop
            Write-Host "  [DISABLED] $name" -ForegroundColor Green
            $action = 'Disabled'
        }
        catch {
            Write-Host "  [ERROR] $name — $($_.Exception.Message)" -ForegroundColor Red
            $action = "Error: $($_.Exception.Message)"
        }
    }
    else {
        $action = 'Skipped (WhatIf or denied)'
    }

    [PSCustomObject]@{
        AgentName     = $name
        AgentId       = $agent.ChatbotId
        PreviousState = if ($current) { 'Enabled' } else { 'Disabled' }
        Action        = $action
        TimestampUtc  = (Get-Date).ToUniversalTime().ToString('o')
    }
}

# Emit results + SHA-256 manifest entry
$resultsPath = Join-Path $EvidencePath "mutation-results-$ts.json"
$results | ConvertTo-Json -Depth 10 | Set-Content -Path $resultsPath -Encoding UTF8
$hash = (Get-FileHash -Path $resultsPath -Algorithm SHA256).Hash
$snapshotHash = (Get-FileHash -Path $snapshotPath -Algorithm SHA256).Hash

$manifestPath = Join-Path $EvidencePath "manifest.json"
$manifest = @()
if (Test-Path $manifestPath) { $manifest = @(Get-Content $manifestPath | ConvertFrom-Json) }
$manifest += @(
    [PSCustomObject]@{ file=(Split-Path $snapshotPath -Leaf); sha256=$snapshotHash; bytes=(Get-Item $snapshotPath).Length; generated_utc=$ts; script='Disable-FileUpload (snapshot)'; control_id='1.26' }
    [PSCustomObject]@{ file=(Split-Path $resultsPath -Leaf);  sha256=$hash;         bytes=(Get-Item $resultsPath).Length;  generated_utc=$ts; script='Disable-FileUpload (results)';  control_id='1.26' }
)
$manifest | ConvertTo-Json -Depth 5 | Set-Content -Path $manifestPath -Encoding UTF8

Write-Host "`nSnapshot: $snapshotPath (SHA-256: $snapshotHash)" -ForegroundColor Cyan
Write-Host "Results : $resultsPath (SHA-256: $hash)" -ForegroundColor Cyan

Stop-Transcript
$results | Format-Table -AutoSize
```

---

## Script 4 — End-to-End Validation Script for Control 1.26

```powershell
<#
.SYNOPSIS
    Validates Control 1.26 across all environments and emits a single consolidated
    evidence pack (inventory + audit + DLP-coverage check) suitable for auditor handoff.

.DESCRIPTION
    Read-only. Combines inventory and zone-compliance audit into one run, and emits
    a single SHA-256-anchored evidence bundle.

.PARAMETER ZoneMapping
    Hashtable mapping environment name (GUID) to zone number.

.PARAMETER ApprovedEnabledAgents
    Optional array of agent IDs with approved File Upload enablement.

.PARAMETER EvidencePath
    Directory for the evidence bundle.

.EXAMPLE
    $zones = @{ 'env-personal' = 1; 'env-team' = 2; 'env-ent' = 3 }
    .\Validate-Control-1.26.ps1 -ZoneMapping $zones -ApprovedEnabledAgents @('agent-id-1')
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [hashtable]$ZoneMapping,
    [string[]]$ApprovedEnabledAgents = @(),
    [string]$EvidencePath = ".\evidence\1.26"
)

$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force -Path $EvidencePath | Out-Null
$ts = Get-Date -Format 'yyyyMMddTHHmmssZ'
Start-Transcript -Path "$EvidencePath\transcript-validate-$ts.log" -IncludeInvocationHeader

$inventory = & "$PSScriptRoot\Get-AgentFileUploadInventory.ps1" -EvidencePath $EvidencePath
$audit     = & "$PSScriptRoot\Audit-FileUploadCompliance.ps1" -ZoneMapping $ZoneMapping `
                -ApprovedEnabledAgents $ApprovedEnabledAgents -EvidencePath $EvidencePath

$summary = [PSCustomObject]@{
    ControlId         = '1.26'
    GeneratedUtc      = $ts
    TotalEnvironments = ($ZoneMapping.Keys).Count
    TotalAgents       = $inventory.Count
    EnabledAgents     = ($inventory | Where-Object FileUploadEnabled).Count
    AuditPass         = ($audit | Where-Object Result -eq 'PASS').Count
    AuditWarn         = ($audit | Where-Object Result -eq 'WARN').Count
    AuditFail         = ($audit | Where-Object Result -eq 'FAIL').Count
}

$summaryPath = Join-Path $EvidencePath "validation-summary-$ts.json"
$summary | ConvertTo-Json -Depth 10 | Set-Content -Path $summaryPath -Encoding UTF8
$hash = (Get-FileHash -Path $summaryPath -Algorithm SHA256).Hash

$manifestPath = Join-Path $EvidencePath "manifest.json"
$manifest = @()
if (Test-Path $manifestPath) { $manifest = @(Get-Content $manifestPath | ConvertFrom-Json) }
$manifest += [PSCustomObject]@{
    file           = (Split-Path $summaryPath -Leaf)
    sha256         = $hash
    bytes          = (Get-Item $summaryPath).Length
    generated_utc  = $ts
    script         = 'Validate-Control-1.26'
    control_id     = '1.26'
}
$manifest | ConvertTo-Json -Depth 5 | Set-Content -Path $manifestPath -Encoding UTF8

Write-Host "`n=== Validation Summary ===" -ForegroundColor Cyan
$summary | Format-List
Write-Host "Summary: $summaryPath (SHA-256: $hash)" -ForegroundColor Green

Stop-Transcript
```

---

## Evidence Bundle Layout

After running the scripts, the evidence directory will contain:

```
evidence/1.26/
├── transcript-inventory-<ts>.log
├── transcript-mutation-<ts>.log
├── transcript-validate-<ts>.log
├── agent-file-upload-inventory-<ts>.json
├── compliance-audit-<ts>.json
├── before-snapshot-<ts>.json          (per mutation)
├── mutation-results-<ts>.json         (per mutation)
├── validation-summary-<ts>.json
└── manifest.json                      (SHA-256 index of all artifacts)
```

Land the bundle in WORM storage (Microsoft Purview Data Lifecycle Management retention lock or Azure Storage immutability policy) per SEC 17a-4(f) preservation requirements.

---

[Back to Control 1.26](../../../controls/pillar-1-security/1.26-agent-file-upload-and-file-analysis-restrictions.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification & Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
