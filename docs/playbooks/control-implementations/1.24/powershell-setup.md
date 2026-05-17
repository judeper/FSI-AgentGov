# PowerShell Setup: Control 1.24 — Defender AI Security Posture Management (AI-SPM)

!!! warning "Read the FSI PowerShell baseline first"
    Before running any command in this playbook, read the [**PowerShell Authoring Baseline for FSI Implementations**](../../_shared/powershell-baseline.md). It is the canonical source for module version pinning, sovereign-cloud (GCC / GCC High / DoD) endpoints, mutation safety (`-WhatIf` / `SupportsShouldProcess`), Dataverse compatibility, and SHA-256 evidence emission. Snippets below show abbreviated patterns; the baseline is authoritative.

**Last Updated:** April 2026
**Modules Required:** `Az.Accounts` ≥ 3.0, `Az.Security` ≥ 1.6, `Az.ResourceGraph` ≥ 1.0
**Audience:** M365 administrators in US financial services

> **Hedging note:** These scripts collect evidence and validate configuration. They help support compliance attestations but do not by themselves satisfy regulatory record-keeping requirements; outputs must be filed in the firm's evidence repository per WORM retention policies.

---

## Prerequisites

```powershell
# Pin to known-good versions (update per your change-management process)
Install-Module -Name Az.Accounts      -RequiredVersion 3.0.4 -Scope CurrentUser -Force
Install-Module -Name Az.Security      -RequiredVersion 1.6.0 -Scope CurrentUser -Force
Install-Module -Name Az.ResourceGraph -RequiredVersion 1.0.0 -Scope CurrentUser -Force

# Sovereign-cloud users: connect with the appropriate environment switch
# Connect-AzAccount -Environment AzureUSGovernment   # GCC High / DoD
```

Required Azure RBAC: **Security Reader** to inspect; **Security Admin** + subscription **Owner/Contributor** to enable plans.

---

## Script 1 — Get-AISPMStatus.ps1 (read-only)

Reports Defender CSPM status and the AI-SPM extension state across all accessible subscriptions.

```powershell
<#
.SYNOPSIS
    Reports Defender CSPM and AI-SPM extension status across subscriptions.

.DESCRIPTION
    Read-only. Use to gather evidence for Control 1.24 verification.

.EXAMPLE
    .\Get-AISPMStatus.ps1 -OutputPath .\evidence\AISPM-Status.csv
#>
[CmdletBinding()]
param(
    [string]$OutputPath = ".\AISPM-Status-$(Get-Date -Format 'yyyyMMdd').csv"
)

if (-not (Get-AzContext)) { Connect-AzAccount | Out-Null }

$results = foreach ($sub in Get-AzSubscription) {
    Set-AzContext -SubscriptionId $sub.Id | Out-Null

    $cspm = Get-AzSecurityPricing -Name 'CloudPosture' -ErrorAction SilentlyContinue
    $aiSpmExt = $cspm.Extensions | Where-Object { $_.Name -eq 'SensitiveDataDiscovery' -or $_.Name -eq 'AIThreatProtection' }
    $aiPlan   = Get-AzSecurityPricing -Name 'AI' -ErrorAction SilentlyContinue   # Defender for AI Services

    [pscustomobject]@{
        SubscriptionId          = $sub.Id
        SubscriptionName        = $sub.Name
        DefenderCSPM_Tier       = $cspm.PricingTier
        AISPM_Extension_Enabled = [bool]($aiSpmExt | Where-Object IsEnabled -EQ 'True')
        DefenderForAI_Tier      = $aiPlan.PricingTier
        ExtensionsList          = ($cspm.Extensions | Where-Object IsEnabled -EQ 'True' | Select-Object -ExpandProperty Name) -join ';'
        CollectedAt             = (Get-Date).ToString('o')
    }
}

$results | Export-Csv -Path $OutputPath -NoTypeInformation -Encoding UTF8
$hash = (Get-FileHash -Path $OutputPath -Algorithm SHA256).Hash
"$OutputPath`tSHA256:$hash" | Out-File "$OutputPath.sha256" -Encoding ascii
Write-Host "Wrote $($results.Count) rows to $OutputPath (SHA256 $hash)" -ForegroundColor Green
```

---

## Script 2 — Get-AIWorkloadInventory.ps1 (read-only AI BOM extract)

```powershell
<#
.SYNOPSIS
    Inventories AI workloads via Resource Graph for AI BOM evidence.

.EXAMPLE
    .\Get-AIWorkloadInventory.ps1 -OutputPath .\evidence\AI-BOM.csv
#>
[CmdletBinding()]
param([string]$OutputPath = ".\AI-BOM-$(Get-Date -Format 'yyyyMMdd').csv")

if (-not (Get-AzContext)) { Connect-AzAccount | Out-Null }

$query = @"
Resources
| where type in~ (
    'microsoft.cognitiveservices/accounts',
    'microsoft.machinelearningservices/workspaces',
    'microsoft.search/searchservices',
    'microsoft.machinelearningservices/registries'
)
| extend kind = tostring(kind), sku = tostring(properties.sku.name)
| project name, type, kind, sku, resourceGroup, subscriptionId, location, id, tags
| order by type asc, name asc
"@

$results = Search-AzGraph -Query $query -First 1000
$results | Export-Csv -Path $OutputPath -NoTypeInformation -Encoding UTF8
$hash = (Get-FileHash -Path $OutputPath -Algorithm SHA256).Hash
"$OutputPath`tSHA256:$hash" | Out-File "$OutputPath.sha256" -Encoding ascii

Write-Host "AI BOM rows: $($results.Count) — written to $OutputPath" -ForegroundColor Green
$results | Group-Object type | Sort-Object Count -Descending |
    Select-Object Count, Name | Format-Table -AutoSize
```

---

## Script 3 — Export-AIAttackPaths.ps1 (read-only via REST)

```powershell
<#
.SYNOPSIS
    Exports AI-related attack paths from Defender for Cloud (REST).

.EXAMPLE
    .\Export-AIAttackPaths.ps1 -SubscriptionId <guid> -OutputPath .\evidence\AttackPaths.csv
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string]$SubscriptionId,
    [string]$OutputPath = ".\AttackPaths-$(Get-Date -Format 'yyyyMMdd').csv"
)

if (-not (Get-AzContext)) { Connect-AzAccount | Out-Null }
Set-AzContext -SubscriptionId $SubscriptionId | Out-Null

$token   = (Get-AzAccessToken -ResourceUrl 'https://management.azure.com').Token
$headers = @{ Authorization = "Bearer $token"; 'Content-Type' = 'application/json' }
$uri     = "https://management.azure.com/subscriptions/$SubscriptionId/providers/Microsoft.Security/attackPaths?api-version=2024-01-01"

try {
    $response = Invoke-RestMethod -Uri $uri -Method Get -Headers $headers
    $aiPaths = $response.value | Where-Object {
        ($_.properties.displayName + ' ' + $_.properties.description) -match 'AI|ML|cognitive|openai|foundry|copilot'
    }

    $aiPaths | ForEach-Object {
        [pscustomobject]@{
            Id            = $_.name
            DisplayName   = $_.properties.displayName
            RiskLevel     = $_.properties.riskLevel
            RiskCategories = ($_.properties.riskCategories -join ';')
            EntryPoints   = ($_.properties.entryPointEntityInfos | ForEach-Object { $_.id }) -join ';'
            Description   = $_.properties.description
        }
    } | Export-Csv -Path $OutputPath -NoTypeInformation -Encoding UTF8

    $hash = (Get-FileHash -Path $OutputPath -Algorithm SHA256).Hash
    "$OutputPath`tSHA256:$hash" | Out-File "$OutputPath.sha256" -Encoding ascii
    Write-Host "AI attack paths exported: $($aiPaths.Count) — $OutputPath" -ForegroundColor Green
}
catch {
    Write-Error "REST call failed: $($_.Exception.Message)"
}
```

---

## Script 4 — Enable-AISPM.ps1 (mutation; supports `-WhatIf`)

Enables Defender CSPM (Standard) and the AI-SPM extension. **Always run with `-WhatIf` first.**

```powershell
<#
.SYNOPSIS
    Enables Defender CSPM (Standard) and AI security posture management extension.

.EXAMPLE
    .\Enable-AISPM.ps1 -SubscriptionId <guid> -WhatIf
    .\Enable-AISPM.ps1 -SubscriptionId <guid>
#>
[CmdletBinding(SupportsShouldProcess, ConfirmImpact = 'High')]
param([Parameter(Mandatory)] [string]$SubscriptionId)

if (-not (Get-AzContext)) { Connect-AzAccount | Out-Null }
Set-AzContext -SubscriptionId $SubscriptionId | Out-Null

if ($PSCmdlet.ShouldProcess($SubscriptionId, 'Enable Defender CSPM (Standard) + AI-SPM extension')) {
    # Enable CSPM Standard with AI-SPM + Sensitive Data Discovery + Threat Intelligence extensions
    $extensions = @(
        @{ name = 'SensitiveDataDiscovery'; isEnabled = 'True' },
        @{ name = 'AIThreatProtection';     isEnabled = 'True' }
    )
    Set-AzSecurityPricing -Name 'CloudPosture' -PricingTier 'Standard' -Extension $extensions
    Write-Host "Defender CSPM Standard + AI-SPM enabled on $SubscriptionId" -ForegroundColor Green
}
```

> **Change management:** Mutation scripts must be approved through the firm's change-management process before production runs. Capture `-WhatIf` output as the change ticket attachment.

---

## Script 5 — Validate-Control-1.24.ps1 (composite validator)

```powershell
<#
.SYNOPSIS
    Composite validator for Control 1.24. Returns PASS/FAIL/INFO per check.

.EXAMPLE
    .\Validate-Control-1.24.ps1 -OutputPath .\evidence\Control-1.24-Validation.json
#>
[CmdletBinding()]
param([string]$OutputPath = ".\Control-1.24-Validation-$(Get-Date -Format 'yyyyMMdd').json")

if (-not (Get-AzContext)) { Connect-AzAccount | Out-Null }
$results = New-Object System.Collections.Generic.List[object]

foreach ($sub in Get-AzSubscription) {
    Set-AzContext -SubscriptionId $sub.Id | Out-Null
    $cspm     = Get-AzSecurityPricing -Name 'CloudPosture' -ErrorAction SilentlyContinue
    $aiPlan   = Get-AzSecurityPricing -Name 'AI'           -ErrorAction SilentlyContinue
    $aiSpmOn  = [bool]($cspm.Extensions | Where-Object { $_.Name -eq 'AIThreatProtection' -and $_.IsEnabled -eq 'True' })
    $aiAssets = (Search-AzGraph -Query "Resources | where type in~ ('microsoft.cognitiveservices/accounts','microsoft.machinelearningservices/workspaces') | where subscriptionId == '$($sub.Id)' | count").Count

    $results.Add([pscustomobject]@{
        Subscription          = $sub.Name
        Check_CSPM_Standard   = if ($cspm.PricingTier -eq 'Standard') { 'PASS' } else { 'FAIL' }
        Check_AISPM_Enabled   = if ($aiSpmOn) { 'PASS' } elseif ($aiAssets -eq 0) { 'INFO' } else { 'FAIL' }
        Check_DefenderForAI   = if ($aiPlan.PricingTier -eq 'Standard') { 'PASS' } else { 'INFO' }
        AIAssetCount          = $aiAssets
        CollectedAt           = (Get-Date).ToString('o')
    })
}

$results | ConvertTo-Json -Depth 5 | Out-File $OutputPath -Encoding utf8
$hash = (Get-FileHash -Path $OutputPath -Algorithm SHA256).Hash
"$OutputPath`tSHA256:$hash" | Out-File "$OutputPath.sha256" -Encoding ascii

$results | Format-Table -AutoSize
$failures = $results | Where-Object { $_.Check_CSPM_Standard -eq 'FAIL' -or $_.Check_AISPM_Enabled -eq 'FAIL' }
if ($failures) {
    Write-Host "Validation FAILED on $($failures.Count) subscription(s) — see $OutputPath" -ForegroundColor Red
    exit 2
}
Write-Host "Validation PASSED — evidence: $OutputPath (SHA256 $hash)" -ForegroundColor Green
```

---

## Sovereign-Cloud Notes (GCC / GCC High / DoD)

| Cloud | Az.Accounts environment | AI-SPM availability (April 2026) |
|-------|--------------------------|-----------------------------------|
| Commercial | `AzureCloud` (default) | GA |
| GCC | `AzureCloud` (commercial-backed) | GA |
| GCC High | `AzureUSGovernment` | GA — confirm regional availability |
| DoD | `AzureUSGovernment` | Limited — confirm with Microsoft FedRAMP team |

Replace REST endpoints with `https://management.usgovcloudapi.net/` for sovereign deployments.

---

## Evidence Files Produced

| File | Purpose | Retention |
|------|---------|-----------|
| `AISPM-Status-yyyymmdd.csv` | CSPM + AI-SPM enablement | 6+ years (FINRA) |
| `AI-BOM-yyyymmdd.csv` | AI Bill of Materials | 6+ years; quarterly review evidence |
| `AttackPaths-yyyymmdd.csv` | AI attack paths snapshot | 6+ years |
| `Control-1.24-Validation-yyyymmdd.json` | Validator output | 6+ years; per-attestation evidence |
| `*.sha256` | Integrity hashes | Same as parent file |

---

[Back to Control 1.24](../../../controls/pillar-1-security/1.24-defender-ai-security-posture-management.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
