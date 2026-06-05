# PowerShell Setup: Control 1.4 — Advanced Connector Policies (ACP)

!!! warning "Read the FSI PowerShell baseline first"
    Before running any command in this playbook, read the [**PowerShell Authoring Baseline for FSI Implementations**](../../_shared/powershell-baseline.md). It is the canonical source for module version pinning, mutation safety (`-WhatIf` / `SupportsShouldProcess`), Dataverse compatibility, and SHA-256 evidence emission. Snippets below show abbreviated patterns; the baseline is authoritative.

> Automation guide for [Control 1.4 — Advanced Connector Policies (ACP)](../../../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md). ACP rule authoring is currently a portal + Power Platform REST API operation — the `Microsoft.PowerApps.Administration.PowerShell` and `Microsoft.PowerApps.PowerShell` modules expose the **prerequisite** Managed Environment, environment group, and classic DLP surface plus **evidence-collection** read paths. Use REST for the ACP rule body itself.

---

## 1. Modules

```powershell
# REQUIRED: pin to versions approved by your CAB. See the FSI PowerShell baseline §1.
Install-Module -Name Microsoft.PowerApps.Administration.PowerShell `
    -RequiredVersion '<version>' -Repository PSGallery -Scope CurrentUser -AllowClobber -AcceptLicense
Install-Module -Name Microsoft.PowerApps.PowerShell `
    -RequiredVersion '<version>' -Repository PSGallery -Scope CurrentUser -AllowClobber -AcceptLicense
```

Both modules are **Windows PowerShell 5.1 (Desktop) only**. Add the edition guard from baseline §2 to every script:

```powershell
if ($PSVersionTable.PSEdition -ne 'Desktop') {
    throw "Microsoft.PowerApps.Administration.PowerShell requires Windows PowerShell 5.1 (Desktop edition). Detected: $($PSVersionTable.PSEdition) $($PSVersionTable.PSVersion)."
}
```

---

## 2. Authenticate

```powershell
param(
    [string]$Endpoint = 'prod'
)

# Interactive (recommended for change windows under PIM elevation)
Add-PowerAppsAccount

# Unattended (service principal). Store secret in Key Vault, never in source.
# Add-PowerAppsAccount -ApplicationId $appId -ClientSecret $secret -TenantID $tenantId
```


---

## 3. Verify Prerequisites Before Authoring ACP

```powershell
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string]$EnvironmentId,
    [Parameter(Mandatory)] [string]$EnvironmentGroupId
)
$ErrorActionPreference = 'Stop'

# 3a. Confirm environment exists and is Managed
$env = Get-AdminPowerAppEnvironment -EnvironmentName $EnvironmentId
if (-not $env) { throw "Environment $EnvironmentId not found (or wrong cloud endpoint)." }

$isManaged = $env.Internal.properties.governanceConfiguration.protectionLevel -eq 'Standard'
if (-not $isManaged) {
    throw "Environment $EnvironmentId is NOT a Managed Environment. ACP requires Managed Environments to block nonblockable connectors. Enable Control 2.1 first."
}

# 3b. Confirm region is United States
if ($env.Location -notmatch '^unitedstates') {
    Write-Warning "Environment region '$($env.Location)' is not US. Confirm zone classification before proceeding."
}

# 3c. Confirm classic DLP policy exists (mixed-mode coverage for custom + HTTP connectors)
$dlp = Get-DlpPolicy
if (-not $dlp) {
    Write-Warning "No classic DLP policies found. ACP does not cover custom or HTTP connectors — at least one classic DLP policy is required for FSI mixed mode."
}
```

---

## 4. Author the ACP Rule via Power Platform REST API

> The PowerShell admin module does not yet expose first-class cmdlets for ACP rule CRUD. Use `Invoke-PowerAppsRequest` (ships in `Microsoft.PowerApps.Administration.PowerShell`) which signs requests with the current `Add-PowerAppsAccount` token.

```powershell
[CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
param(
    [Parameter(Mandatory)] [string]$EnvironmentGroupId,
    [Parameter(Mandatory)] [string]$AllowlistJsonPath,   # path to allowlist file in source control
    [string]$ApiVersion  = '2022-03-01-preview',
    [string]$EvidencePath = ".\evidence\1.4"
)
$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force -Path $EvidencePath | Out-Null
$ts = Get-Date -Format 'yyyyMMddTHHmmssZ'
Start-Transcript -Path "$EvidencePath\acp-publish-$ts.log" -IncludeInvocationHeader

if (-not (Test-Path $AllowlistJsonPath)) { throw "Allowlist file not found: $AllowlistJsonPath" }
$body = Get-Content -Raw -Path $AllowlistJsonPath

# 4a. Snapshot the current rule (BEFORE) for rollback evidence
$beforeUri = "/providers/Microsoft.BusinessAppPlatform/scopes/admin/environmentGroups/$EnvironmentGroupId/ruleSets/connector?api-version=$ApiVersion"
try {
    $before = Invoke-PowerAppsRequest -Method GET -Route $beforeUri
    $before | ConvertTo-Json -Depth 30 | Set-Content "$EvidencePath\acp-before-$ts.json" -Encoding UTF8
} catch {
    Write-Warning "No existing ACP rule on group $EnvironmentGroupId (first publish): $($_.Exception.Message)"
}

# 4b. Apply the new allowlist
if ($PSCmdlet.ShouldProcess($EnvironmentGroupId, "PUT advanced connector policy ruleset")) {
    $applyUri = "/providers/Microsoft.BusinessAppPlatform/scopes/admin/environmentGroups/$EnvironmentGroupId/ruleSets/connector?api-version=$ApiVersion"
    $resp = Invoke-PowerAppsRequest -Method PUT -Route $applyUri -Body $body
    $resp | ConvertTo-Json -Depth 30 | Set-Content "$EvidencePath\acp-applied-$ts.json" -Encoding UTF8
}

# 4c. Trigger Publish rules (cascades the rule to design-time + runtime infra of every member env)
if ($PSCmdlet.ShouldProcess($EnvironmentGroupId, "POST publishRules")) {
    $publishUri = "/providers/Microsoft.BusinessAppPlatform/scopes/admin/environmentGroups/$EnvironmentGroupId/publishRules?api-version=$ApiVersion"
    $publishResp = Invoke-PowerAppsRequest -Method POST -Route $publishUri
    $publishResp | ConvertTo-Json -Depth 30 | Set-Content "$EvidencePath\acp-publish-result-$ts.json" -Encoding UTF8
}

Stop-Transcript
```

> **Idempotency:** PUT to the ruleSet endpoint is the canonical idempotent operation — re-running with the same body produces no functional change. The publish step should also be re-runnable but emits a new lifecycle event each time.

> **API version:** `2022-03-01-preview` is the public preview surface as of April 2026. Confirm against the [Power Platform REST API reference for environment groups](https://learn.microsoft.com/en-us/rest/api/power-platform/environmentmanagement/environment-groups) before each change window — preview API versions can change.

---

## 5. Verify Publish Succeeded and Status = Applied

```powershell
$statusUri = "/providers/Microsoft.BusinessAppPlatform/scopes/admin/environmentGroups/$EnvironmentGroupId/ruleSets/connector?api-version=$ApiVersion"
$status = Invoke-PowerAppsRequest -Method GET -Route $statusUri
$applied = $status.properties.status -eq 'Applied'

if (-not $applied) {
    Write-Error "ACP rule status is '$($status.properties.status)' — expected 'Applied'. Investigate via PPAC environment History (look for 'Update Managed Environment Settings' lifecycle event)."
} else {
    Write-Host "[PASS] ACP status = Applied on group $EnvironmentGroupId" -ForegroundColor Green
}
```

---

## 6. Evidence Collection (Read-Only Inventory)

```powershell
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string]$EnvironmentGroupId,
    [string]$EvidencePath = ".\evidence\1.4"
)
$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force -Path $EvidencePath | Out-Null
$ts = Get-Date -Format 'yyyyMMddTHHmmssZ'

# Helper: emit JSON + SHA-256 + manifest entry (see baseline §4)
function Write-FsiEvidence {
    param([Parameter(Mandatory)] $Object, [Parameter(Mandatory)] [string]$Name, [Parameter(Mandatory)] [string]$EvidencePath)
    $stamp = Get-Date -Format 'yyyyMMddTHHmmssZ'
    $jsonPath = Join-Path $EvidencePath "$Name-$stamp.json"
    $Object | ConvertTo-Json -Depth 30 | Set-Content -Path $jsonPath -Encoding UTF8
    $hash = (Get-FileHash -Path $jsonPath -Algorithm SHA256).Hash
    $manifestPath = Join-Path $EvidencePath "manifest.json"
    $manifest = @()
    if (Test-Path $manifestPath) { $manifest = @(Get-Content $manifestPath | ConvertFrom-Json) }
    $manifest += [PSCustomObject]@{
        file = (Split-Path $jsonPath -Leaf); sha256 = $hash; bytes = (Get-Item $jsonPath).Length; generated_utc = $stamp; control = '1.4'
    }
    $manifest | ConvertTo-Json -Depth 5 | Set-Content -Path $manifestPath -Encoding UTF8
    return $jsonPath
}

# 6a. ACP rule body (current allowlist)
$acp = Invoke-PowerAppsRequest -Method GET `
    -Route "/providers/Microsoft.BusinessAppPlatform/scopes/admin/environmentGroups/$EnvironmentGroupId/ruleSets/connector?api-version=2022-03-01-preview"
Write-FsiEvidence -Object $acp -Name 'acp-ruleset' -EvidencePath $EvidencePath

# 6b. Environment group membership
$envs = Get-AdminPowerAppEnvironment | Where-Object { $_.Internal.properties.parentEnvironmentGroup.id -match $EnvironmentGroupId }
Write-FsiEvidence -Object ($envs | Select-Object DisplayName, EnvironmentName, Location, EnvironmentType) -Name 'envgroup-members' -EvidencePath $EvidencePath

# 6c. Classic DLP policies (for mixed-mode coverage proof)
$dlpPolicies = Get-DlpPolicy
Write-FsiEvidence -Object $dlpPolicies -Name 'classic-dlp-policies' -EvidencePath $EvidencePath

# 6d. Connection inventory per member environment (proof allowlist matches reality)
foreach ($e in $envs) {
    $conns = Get-AdminPowerAppConnection -EnvironmentName $e.EnvironmentName
    Write-FsiEvidence -Object ($conns | Select-Object DisplayName, ConnectorName, CreatedBy, CreatedTime) `
        -Name "connections-$($e.EnvironmentName)" -EvidencePath $EvidencePath
}

Write-Host "[DONE] Evidence written to $EvidencePath with manifest.json" -ForegroundColor Green
```

> **WORM landing:** copy `$EvidencePath` to a Microsoft Purview Data Lifecycle retention-locked location (or Azure Storage immutability container) to satisfy SEC 17a-4(f) preservation expectations. See baseline §4.

---

## 7. Rollback (Restore Previous ACP Body)

```powershell
[CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
param(
    [Parameter(Mandatory)] [string]$EnvironmentGroupId,
    [Parameter(Mandatory)] [string]$BeforeJsonPath
)
$ErrorActionPreference = 'Stop'
$body = Get-Content -Raw -Path $BeforeJsonPath
if ($PSCmdlet.ShouldProcess($EnvironmentGroupId, "Rollback ACP ruleset to $BeforeJsonPath")) {
    Invoke-PowerAppsRequest -Method PUT `
        -Route "/providers/Microsoft.BusinessAppPlatform/scopes/admin/environmentGroups/$EnvironmentGroupId/ruleSets/connector?api-version=2022-03-01-preview" `
        -Body $body
    Invoke-PowerAppsRequest -Method POST `
        -Route "/providers/Microsoft.BusinessAppPlatform/scopes/admin/environmentGroups/$EnvironmentGroupId/publishRules?api-version=2022-03-01-preview"
}
```

Always invoke first with `-WhatIf`.

---

## 8. What This Script Does **Not** Do

- **Custom connectors / HTTP connectors:** not yet in ACP scope; govern via classic DLP groups and `Set-DlpPolicyConnectorConfigurations` for endpoint filtering.
- **Microsoft Copilot Studio virtual connectors:** not in ACP scope and not planned. Continue using classic DLP data policies.
- **MCP server tool-level blocking:** ACP supports server-level only. Tool-level toggles are configured in Copilot Studio per agent.
- **Service-principal-bypass safety net:** classic DLP scoped at the **environment level** (not security-group level) is required to cover SP-authenticated connections — see the warning in the control doc.

---

[Back to Control 1.4](../../../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification & Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
