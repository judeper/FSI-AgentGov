# PowerShell Setup: Control 1.28 - Policy-Based Agent Publishing Restrictions

!!! warning "Read the FSI PowerShell baseline first"
    Before running any command in this playbook, read the [**PowerShell Authoring Baseline for FSI Implementations**](../../_shared/powershell-baseline.md). It is the canonical source for module version pinning, sovereign-cloud (GCC / GCC High / DoD) endpoints, mutation safety (`-WhatIf` / `SupportsShouldProcess`), Dataverse compatibility, and SHA-256 evidence emission. Snippets below show abbreviated patterns; the baseline is authoritative.

**Last Updated:** April 2026<br>
**Primary Module:** `Microsoft.PowerApps.Administration.PowerShell` (Windows PowerShell 5.1, Desktop edition)<br>
**Estimated Time:** 30–45 minutes (initial setup); 5–10 minutes per audit run

---

## Prerequisites

- [ ] Windows PowerShell 5.1 (Desktop edition) — required for `Microsoft.PowerApps.Administration.PowerShell`
- [ ] Power Platform Admin role on the target tenant
- [ ] CAB-approved pinned versions of the modules listed below
- [ ] Sovereign-cloud `-Endpoint` value documented (commercial / GCC / GCC High / DoD)

---

## Module Installation (Pinned)

```powershell
# Substitute <version> with the version approved by your CAB (do not use floating versions in regulated tenants).
Install-Module -Name Microsoft.PowerApps.Administration.PowerShell `
    -RequiredVersion '<version>' `
    -Repository PSGallery `
    -Scope CurrentUser `
    -AllowClobber `
    -AcceptLicense

Install-Module -Name Microsoft.PowerApps.PowerShell `
    -RequiredVersion '<version>' `
    -Repository PSGallery `
    -Scope CurrentUser `
    -AllowClobber `
    -AcceptLicense

Import-Module Microsoft.PowerApps.Administration.PowerShell

# Sovereign-aware authentication. Replace -Endpoint with usgov / usgovhigh / dod for US Government clouds.
Add-PowerAppsAccount -Endpoint prod
```

```powershell
# Hard guard — prevents silent false-clean evidence in PowerShell 7.
if ($PSVersionTable.PSEdition -ne 'Desktop') {
    throw "Microsoft.PowerApps.Administration.PowerShell requires Windows PowerShell 5.1 (Desktop edition). Detected: $($PSVersionTable.PSEdition) $($PSVersionTable.PSVersion)."
}
```

!!! note "Cmdlet naming"
    The current canonical DLP cmdlet names in this module are `New-DlpPolicy`, `Get-DlpPolicy`, `Set-DlpPolicy`, `Remove-DlpPolicy`, and `Add-PowerAppEnvironmentToPolicy`. Older "Admin"-prefixed aliases (`New-AdminDlpPolicy`, `Get-AdminDlpPolicy`, etc.) still resolve in current builds of the module but the non-prefixed names are what Microsoft Learn currently documents. Use whichever set is consistent in your existing automation; do not mix.

---

## Script 1 — Discover Current DLP Posture (Read-Only)

Run this first to inventory existing policies and environment assignments before making any changes.

```powershell
<#
.SYNOPSIS
    Read-only inventory of current DLP policies and environment assignments.
.NOTES
    Safe to run in production. Produces a CSV evidence file with SHA-256 hash.
#>

$timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$outDir    = Join-Path -Path (Get-Location) -ChildPath "evidence/1.28"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

$policies = Get-DlpPolicy
$rows = foreach ($p in $policies) {
    [pscustomobject]@{
        DisplayName       = $p.DisplayName
        PolicyName        = $p.PolicyName
        EnvironmentType   = $p.EnvironmentType
        EnvironmentCount  = ($p.Environments | Measure-Object).Count
        CreatedTime       = $p.CreatedTime
        LastModifiedTime  = $p.LastModifiedTime
    }
}

$csvPath = Join-Path $outDir "dlp-policy-inventory-$timestamp.csv"
$rows | Export-Csv -Path $csvPath -NoTypeInformation -Encoding UTF8

# SHA-256 evidence hash
$hash = (Get-FileHash -Path $csvPath -Algorithm SHA256).Hash
"$csvPath`tSHA256:$hash" | Out-File -FilePath (Join-Path $outDir "evidence-manifest-$timestamp.txt") -Append -Encoding UTF8

Write-Host "Inventory exported: $csvPath" -ForegroundColor Green
Write-Host "SHA-256: $hash" -ForegroundColor Cyan
```

---

## Script 2 — Create a Zone-Specific DLP Policy (Mutation; `-WhatIf` Supported)

This script is the canonical pattern for creating one zone DLP policy. Run it once per zone (Zone 1, Zone 2, Zone 3) with the appropriate connector lists.

```powershell
<#
.SYNOPSIS
    Create a zone-aligned DLP policy for Copilot Studio agent publishing restrictions.
.PARAMETER PolicyDisplayName
    Display name for the new policy (e.g., 'FSI - Zone 3 Enterprise Restricted').
.PARAMETER BusinessConnectors
    Array of connector IDs (full path: /providers/Microsoft.PowerApps/apis/<name>) to classify as Business.
.PARAMETER BlockedConnectors
    Array of connector IDs to classify as Blocked.
.PARAMETER WhatIf
    Standard PowerShell -WhatIf: prints the intended mutation without executing.
.NOTES
    Requires Power Platform Admin. Verify cmdlet/parameter availability against your pinned module version.
#>
[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'High')]
param(
    [Parameter(Mandatory)] [string]   $PolicyDisplayName,
    [Parameter(Mandatory)] [string[]] $BusinessConnectors,
    [Parameter(Mandatory)] [string[]] $BlockedConnectors
)

if ($PSCmdlet.ShouldProcess($PolicyDisplayName, "Create DLP policy")) {
    $policy = New-DlpPolicy -DisplayName $PolicyDisplayName -EnvironmentType 'OnlyEnvironments'

    $connectorGroups = @(
        @{
            classification = 'Confidential'   # 'Confidential' is the API value for the Business group
            connectors     = $BusinessConnectors | ForEach-Object {
                @{ id = $_; type = 'Microsoft.PowerApps/apis' }
            }
        },
        @{
            classification = 'Blocked'
            connectors     = $BlockedConnectors | ForEach-Object {
                @{ id = $_; type = 'Microsoft.PowerApps/apis' }
            }
        }
    )

    Set-DlpPolicy -PolicyName $policy.PolicyName -ConnectorGroups $connectorGroups | Out-Null
    Write-Host "Created DLP policy: $PolicyDisplayName ($($policy.PolicyName))" -ForegroundColor Green
}
```

> **API caveat:** The `Set-DlpPolicy -ConnectorGroups` request body, including the `classification` token used for the "Business" group (historically `Confidential` in the underlying API), can change between module releases. Run `Get-Help Set-DlpPolicy -Full` against your pinned version and confirm the parameter shape with `(Get-Command Set-DlpPolicy).Parameters` before running in production.

---

## Script 3 — Assign a Policy to Environments by Zone Tag

This script reads environment metadata and assigns each environment to the appropriate zone DLP policy. It uses environment metadata (display name pattern or environment group) as the zone signal — adapt the matching logic to your own classification convention.

```powershell
<#
.SYNOPSIS
    Assign a DLP policy to all environments matching a zone signal.
.PARAMETER PolicyDisplayName
    The display name of the target DLP policy.
.PARAMETER ZoneSignalPattern
    A wildcard pattern matched against environment DisplayName (e.g., '*Zone3*' or '*-Prod').
#>
[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'High')]
param(
    [Parameter(Mandatory)] [string] $PolicyDisplayName,
    [Parameter(Mandatory)] [string] $ZoneSignalPattern
)

$policy = Get-DlpPolicy | Where-Object { $_.DisplayName -eq $PolicyDisplayName }
if (-not $policy) { throw "DLP policy '$PolicyDisplayName' not found." }

$targets = Get-AdminPowerAppEnvironment | Where-Object { $_.DisplayName -like $ZoneSignalPattern }
Write-Host "Matched $($targets.Count) environment(s) for pattern '$ZoneSignalPattern'." -ForegroundColor Cyan

foreach ($env in $targets) {
    if ($PSCmdlet.ShouldProcess($env.DisplayName, "Assign DLP policy '$PolicyDisplayName'")) {
        try {
            Add-PowerAppEnvironmentToPolicy -PolicyName $policy.PolicyName -EnvironmentName $env.EnvironmentName -ErrorAction Stop
            Write-Host "  Assigned: $($env.DisplayName)" -ForegroundColor Green
        } catch {
            Write-Warning "  Failed: $($env.DisplayName) — $($_.Exception.Message)"
        }
    }
}
```

---

## Script 4 — Audit Published Copilot Studio Agents (Read-Only Evidence)

This script enumerates Copilot Studio agents (Dataverse `bot` rows) per environment and exports their key publish-status fields to CSV with a SHA-256 evidence hash. It does **not** attempt to evaluate DLP compliance per agent — there is no first-party cmdlet that returns "this agent passes DLP" today, so connector-by-connector compliance must be reconciled against the in-product Copilot Studio publish dialog or a Dataverse query of the agent's component set.

```powershell
<#
.SYNOPSIS
    Inventory Copilot Studio agents per environment for evidence collection.
.NOTES
    Read-only. Requires Power Platform Admin. Output includes SHA-256 hash for audit.
#>

$timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$outDir    = Join-Path (Get-Location) "evidence/1.28"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

$rows = foreach ($env in Get-AdminPowerAppEnvironment) {
    try {
        $agents = Get-AdminPowerAppCdsDatabaseLanguages -EnvironmentName $env.EnvironmentName -ErrorAction SilentlyContinue
        # Use the Power Platform admin API for chatbots if available in your pinned module:
        $bots = Get-AdminPowerAppChatbot -EnvironmentName $env.EnvironmentName -ErrorAction SilentlyContinue
        foreach ($bot in $bots) {
            [pscustomobject]@{
                Environment      = $env.DisplayName
                EnvironmentId    = $env.EnvironmentName
                AgentDisplayName = $bot.Properties.DisplayName
                AgentId          = $bot.ChatBotName
                PublishStatus    = $bot.Properties.PublishStatus
                LastModifiedTime = $bot.Properties.LastModifiedTime
                CreatedBy        = $bot.Properties.CreatedBy.userPrincipalName
            }
        }
    } catch {
        Write-Warning "Environment '$($env.DisplayName)': $($_.Exception.Message)"
    }
}

$csvPath = Join-Path $outDir "agent-publish-inventory-$timestamp.csv"
$rows | Export-Csv -Path $csvPath -NoTypeInformation -Encoding UTF8

$hash = (Get-FileHash -Path $csvPath -Algorithm SHA256).Hash
"$csvPath`tSHA256:$hash" | Out-File -FilePath (Join-Path $outDir "evidence-manifest-$timestamp.txt") -Append -Encoding UTF8

Write-Host "Agent inventory: $csvPath" -ForegroundColor Green
Write-Host "SHA-256: $hash" -ForegroundColor Cyan
```

> **What this does not do:** It does not declare an agent "DLP compliant." It captures the inventory and publish state. DLP compliance is enforced at runtime and at publish time by the platform; per-agent compliance status must be reviewed via the Copilot Studio publish dialog or via Dataverse component queries.

---

## Script 5 — Schedule the Inventory as a Weekly Evidence Job

```powershell
$action  = New-ScheduledTaskAction -Execute 'powershell.exe' `
    -Argument '-NoProfile -ExecutionPolicy Bypass -File "C:\Scripts\Audit-AgentPublishInventory.ps1"'
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 6:00AM
$principal = New-ScheduledTaskPrincipal -UserId "DOMAIN\svc-pp-audit" -LogonType ServiceAccount -RunLevel Highest

Register-ScheduledTask -TaskName "FSI-1.28-AgentPublishInventory" `
    -Action $action -Trigger $trigger -Principal $principal `
    -Description "Weekly Copilot Studio agent inventory for Control 1.28 evidence."
```

> **Service account guidance:** Use a dedicated service principal (not a person's UPN) with the minimum role required (Power Platform Admin scoped to required environments where possible). Document the principal in your privileged-access registry.

---

## Validation Commands

```powershell
# Confirm DLP policies and environment counts
Get-DlpPolicy | Select-Object DisplayName, @{N='Environments';E={($_.Environments | Measure-Object).Count}}, LastModifiedTime

# Confirm a specific policy's connector groups
Get-DlpPolicy -PolicyName '<policy-id>' | Select-Object -ExpandProperty ConnectorGroups | Format-List

# Confirm cmdlet availability against your pinned module
Get-Command -Module Microsoft.PowerApps.Administration.PowerShell -Name *Dlp*, *EnvironmentToPolicy*, *Chatbot*
```

---

## Known Gaps in PowerShell Coverage

- **No first-party "test agent against DLP" cmdlet.** Use the in-product Copilot Studio publish dialog as the authoritative signal. PowerShell can inventory agents and policies but cannot evaluate per-agent DLP compliance directly.
- **No first-party cmdlet to require approval before publish.** Implement approval gates with Power Automate or Power Platform Pipelines (see the Portal Walkthrough).
- **`Get-AdminPowerAppChatbot` availability varies by module version.** If the cmdlet is not present in your pinned version, query the Dataverse `bot` table directly via the Web API for the same data.

---

[Back to Control 1.28](../../../controls/pillar-1-security/1.28-policy-based-agent-publishing-restrictions.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification & Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: April 2026 | Version: v1.4.0 | UI Verification Status: Current*
