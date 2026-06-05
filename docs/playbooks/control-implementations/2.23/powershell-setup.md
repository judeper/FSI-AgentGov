# PowerShell Setup: Control 2.23 - User Consent and AI Disclosure Enforcement

!!! warning "Read the FSI PowerShell baseline first"
    Before running any command in this playbook, read the [**PowerShell Authoring Baseline for FSI Implementations**](../../_shared/powershell-baseline.md). It is the canonical source for module version pinning, mutation safety (`-WhatIf` / `SupportsShouldProcess`), Dataverse compatibility, and SHA-256 evidence emission. Snippets below show abbreviated patterns; the baseline is authoritative.

**Last Updated:** April 2026
**PowerShell Version Required:** 7.4+
**Modules Required:** `Microsoft.Graph` (≥ 2.25), `ExchangeOnlineManagement` (≥ 3.5), `Microsoft.PowerApps.Administration.PowerShell` (≥ 2.0.190)
**Optional CLIs:** Power Platform CLI (`pac`) for Dataverse solution import, Azure CLI (`az`) for Dataverse Web API tokens
**Estimated Time:** 30–45 minutes

> **Honesty disclosure.** As of April 2026, Microsoft Graph **does not expose a GA endpoint** for reading or writing the tenant `Copilot AI Disclaimer` policy. A `/beta/admin/copilot/settings` resource is in private preview and **must not** be relied on for production governance evidence. Until the GA endpoint ships, treat the Microsoft 365 admin center UI as authoritative and use the scripts below for surrounding evidence (Message Center, audit logs, Dataverse consent records, agent inventory).

## Prerequisites

- [ ] PowerShell 7.4 or later
- [ ] Module versions pinned per the FSI baseline and approved by your Change Advisory Board (CAB)
- [ ] **AI Administrator** role for Copilot-related Graph reads (preferred); Entra Global Admin for any consent-grant operation
- [ ] **Purview Audit Reader** (or higher) for unified audit log searches
- [ ] **Environment Admin** + Dataverse application user for Dataverse Web API access
- [ ] Output directory exists: `C:\AgentGov\Evidence\2.23\` (or your local equivalent under the tenant-evidence path)

---

## Module Installation (CAB-pinned)

```powershell
# Replace <version> values with the versions approved by your CAB.
$ErrorActionPreference = 'Stop'

Install-Module -Name Microsoft.Graph                           -RequiredVersion <version> -Scope CurrentUser
Install-Module -Name ExchangeOnlineManagement                  -RequiredVersion <version> -Scope CurrentUser
Install-Module -Name Microsoft.PowerApps.Administration.PowerShell -RequiredVersion <version> -Scope CurrentUser

# Verify
Get-Module Microsoft.Graph, ExchangeOnlineManagement, Microsoft.PowerApps.Administration.PowerShell -ListAvailable |
    Select-Object Name, Version
```

---

## Script 1 — Confirm tenant has the AI Disclaimer feature available

### Purpose
Capture Message Center evidence that the AI Disclaimer rollout has reached your tenant. This is the most reliable Graph-side signal until a tenant-policy read endpoint ships.

### `Get-AIDisclaimerRolloutEvidence.ps1`

```powershell
<#
.SYNOPSIS
    Captures Message Center entries relevant to the Copilot AI Disclaimer rollout.
.DESCRIPTION
    Queries Microsoft Graph Service Communications API for messages matching
    'AI Disclaimer' or 'Copilot AI disclaimer' and emits an evidence file with
    a SHA-256 hash for chain-of-custody.
.NOTES
    Required scope: ServiceMessage.Read.All
#>
[CmdletBinding(SupportsShouldProcess)]
param(
    [string]$EvidencePath = 'C:\AgentGov\Evidence\2.23'
)

if (-not (Get-MgContext)) {
    Connect-MgGraph -Scopes 'ServiceMessage.Read.All' -NoWelcome
}

$messages = Get-MgServiceAnnouncementMessage -All |
    Where-Object { $_.Title -match 'AI Disclaimer|Copilot AI' } |
    Select-Object Id, Title, Category, StartDateTime, EndDateTime, LastModifiedDateTime, Severity

if (-not (Test-Path $EvidencePath)) { New-Item -Path $EvidencePath -ItemType Directory | Out-Null }

$stamp   = Get-Date -Format 'yyyyMMdd-HHmmss'
$outFile = Join-Path $EvidencePath "messagecenter-aidisclaimer-$stamp.json"

if ($PSCmdlet.ShouldProcess($outFile, 'Write Message Center evidence')) {
    $messages | ConvertTo-Json -Depth 5 | Out-File -FilePath $outFile -Encoding utf8
    $hash = (Get-FileHash -Path $outFile -Algorithm SHA256).Hash
    "$hash  $(Split-Path $outFile -Leaf)" | Out-File -FilePath "$outFile.sha256" -Encoding ascii
    Write-Host "Evidence: $outFile  (SHA-256 $hash)" -ForegroundColor Green
}
```

---

## Script 2 — Inventory Copilot Studio agents and tag governance zone

### Purpose
Inventory all Microsoft Copilot Studio bots across Power Platform environments and join them with your governance-zone classification (held in a CSV maintained by the FSI team). Disclosure-language presence is **not** programmatically inspectable today (Copilot Studio topic content is not exposed by the admin module), so the script flags every agent as "Manual review required" and emits the inventory for tracking.

### `Get-AgentZoneInventory.ps1`

```powershell
<#
.SYNOPSIS
    Inventories Copilot Studio agents and joins with the FSI zone classification CSV.
.DESCRIPTION
    Uses Get-AdminBot to enumerate bots in every environment the caller administers.
    Joins with .\zone-classification.csv (columns: BotId,Zone,Owner) and writes a
    CSV evidence file with SHA-256 hash.
.NOTES
    Topic content is not exposed via the admin PowerShell module as of April 2026,
    so disclosure-language verification is performed manually (see Verification playbook).
#>
[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(Mandatory)] [string]$ZoneCsvPath,
    [string]$EvidencePath = 'C:\AgentGov\Evidence\2.23'
)

if (-not (Test-Path $ZoneCsvPath)) { throw "Zone classification CSV not found: $ZoneCsvPath" }
$zones = Import-Csv $ZoneCsvPath | Group-Object BotId -AsHashTable -AsString

Add-PowerAppsAccount | Out-Null

$envs = Get-AdminPowerAppEnvironment
$rows = foreach ($env in $envs) {
    try {
        $bots = Get-AdminBot -EnvironmentName $env.EnvironmentName -ErrorAction Stop
    } catch {
        Write-Warning "Skipping environment $($env.DisplayName): $_"; continue
    }
    foreach ($bot in $bots) {
        $z = $zones[$bot.BotName]
        [pscustomobject]@{
            EnvironmentName        = $env.EnvironmentName
            EnvironmentDisplayName = $env.DisplayName
            BotName                = $bot.BotName
            BotDisplayName         = $bot.DisplayName
            CreatedTime            = $bot.CreatedTime
            LastModifiedTime       = $bot.LastModifiedTime
            Zone                   = $z.Zone
            Owner                  = $z.Owner
            DisclosureReviewStatus = 'Manual review required'
        }
    }
}

if (-not (Test-Path $EvidencePath)) { New-Item -Path $EvidencePath -ItemType Directory | Out-Null }
$stamp   = Get-Date -Format 'yyyyMMdd-HHmmss'
$outFile = Join-Path $EvidencePath "agent-zone-inventory-$stamp.csv"

if ($PSCmdlet.ShouldProcess($outFile, 'Write agent inventory')) {
    $rows | Export-Csv -Path $outFile -NoTypeInformation
    $hash = (Get-FileHash -Path $outFile -Algorithm SHA256).Hash
    "$hash  $(Split-Path $outFile -Leaf)" | Out-File -FilePath "$outFile.sha256" -Encoding ascii
    Write-Host "Inventory: $outFile  ($($rows.Count) bots)  SHA-256 $hash" -ForegroundColor Green
}
```

---

## Script 3 — Deploy the `fsi_aiconsent` Dataverse table via `pac` CLI

### Purpose
Repeatable, source-controlled deployment of the `fsi_aiconsent` table as a managed solution. This replaces the click-through Step 9 in the Portal Walkthrough.

### Workflow

```powershell
# 1. Authenticate pac CLI to the target environment.
pac auth create --name fsi-zone3 --environment '<environment-id-or-url>'

# 2. Import the FSI managed solution that contains the fsi_aiconsent table.
#    The solution zip lives in FSI-AgentGov-Solutions:
#      solutions/2.23-ai-consent/FSI_AIConsent_managed.zip
pac solution import `
    --path .\FSI_AIConsent_managed.zip `
    --activate-plugins `
    --skip-dependency-check $false `
    --publish-changes

# 3. Capture import evidence.
$stamp   = Get-Date -Format 'yyyyMMdd-HHmmss'
$evidence = "C:\AgentGov\Evidence\2.23\solution-import-$stamp.log"
pac solution list | Out-File -FilePath $evidence -Encoding utf8
Get-FileHash -Path $evidence -Algorithm SHA256 |
    ForEach-Object { "$($_.Hash)  $(Split-Path $evidence -Leaf)" } |
    Out-File -FilePath "$evidence.sha256" -Encoding ascii
```

> The companion managed solution is tracked in the **FSI-AgentGov-Solutions** repository. If your tenant uses a different publisher prefix, fork the unmanaged solution, change the prefix, and rebuild before importing.

---

## Script 4 — Read consent records from Dataverse Web API

### Purpose
Honest, working query against the `fsi_aiconsents` Web API endpoint using OData filters (Web API does **not** accept inline `fetchXml` as a query string parameter — that pattern from older versions of this playbook was incorrect).

### `Get-ConsentRecords.ps1`

```powershell
<#
.SYNOPSIS
    Reads recent consent records from the fsi_aiconsents Dataverse table.
.DESCRIPTION
    Acquires an access token via Azure CLI for the Dataverse environment, then
    issues an OData query against the Web API.
.NOTES
    Dataverse Web API uses OData query options ($filter, $orderby, $top).
    FetchXML is supported via the FetchXml HTTP header, NOT as a URI parameter.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string]$EnvironmentUrl,   # e.g., https://contoso.crm.dynamics.com
    [int]$DaysBack = 30,
    [string]$AgentId,
    [string]$EvidencePath = 'C:\AgentGov\Evidence\2.23'
)

# Token from Azure CLI; in non-interactive contexts, use a service principal + MSAL.PS.
$token = az account get-access-token --resource $EnvironmentUrl --query accessToken -o tsv
if (-not $token) { throw 'Failed to acquire Dataverse access token via az CLI.' }

$since = (Get-Date).AddDays(-$DaysBack).ToString('o')
$filter = "fsi_consenttimestamp ge $since"
if ($AgentId) { $filter += " and fsi_agentid eq '$AgentId'" }

$select = 'fsi_userupn,fsi_useraadid,fsi_agentname,fsi_agentid,fsi_consenttimestamp,fsi_disclosureversion,fsi_acknowledgmentstatus,fsi_sourcechannel,createdon'
$uri    = "$EnvironmentUrl/api/data/v9.2/fsi_aiconsents?`$filter=$([uri]::EscapeDataString($filter))&`$select=$select&`$orderby=fsi_consenttimestamp desc"

$headers = @{
    'Authorization'    = "Bearer $token"
    'Accept'           = 'application/json'
    'OData-Version'    = '4.0'
    'OData-MaxVersion' = '4.0'
}

$response = Invoke-RestMethod -Uri $uri -Headers $headers -Method Get
$records  = $response.value

Write-Host "Records returned: $($records.Count) (last $DaysBack days)" -ForegroundColor Cyan
$records | Format-Table fsi_userupn, fsi_agentname, fsi_consenttimestamp, fsi_disclosureversion, fsi_acknowledgmentstatus -AutoSize

if (-not (Test-Path $EvidencePath)) { New-Item -Path $EvidencePath -ItemType Directory | Out-Null }
$stamp   = Get-Date -Format 'yyyyMMdd-HHmmss'
$outFile = Join-Path $EvidencePath "consent-records-$stamp.csv"
$records | Export-Csv -Path $outFile -NoTypeInformation
$hash = (Get-FileHash -Path $outFile -Algorithm SHA256).Hash
"$hash  $(Split-Path $outFile -Leaf)" | Out-File -FilePath "$outFile.sha256" -Encoding ascii
Write-Host "Evidence: $outFile  SHA-256 $hash" -ForegroundColor Green
```

---

## Script 5 — Audit log evidence (Purview unified audit log)

### Purpose
Pull configuration-change and consent-flow events from the unified audit log for the regulator-facing evidence binder.

### `Search-DisclosureAuditEvidence.ps1`

```powershell
<#
.SYNOPSIS
    Searches the Purview unified audit log for events related to Control 2.23.
.NOTES
    Required role: Purview Audit Reader (or higher).
    Operations and RecordTypes evolve; verify against your tenant before relying
    on a specific operation name.
#>
[CmdletBinding()]
param(
    [datetime]$StartDate = (Get-Date).AddDays(-7),
    [datetime]$EndDate   = (Get-Date),
    [string]$EvidencePath = 'C:\AgentGov\Evidence\2.23'
)

Connect-ExchangeOnline -ShowBanner:$false

# Cast a wide net; refine after observing live data.
$results = Search-UnifiedAuditLog `
    -StartDate $StartDate -EndDate $EndDate `
    -ResultSize 5000 `
    -FreeText 'CopilotAIDisclaimer Copilot AI Disclaimer fsi_aiconsent'

if (-not (Test-Path $EvidencePath)) { New-Item -Path $EvidencePath -ItemType Directory | Out-Null }
$stamp   = Get-Date -Format 'yyyyMMdd-HHmmss'
$outFile = Join-Path $EvidencePath "audit-evidence-$stamp.csv"
$results | Export-Csv -Path $outFile -NoTypeInformation
$hash = (Get-FileHash -Path $outFile -Algorithm SHA256).Hash
"$hash  $(Split-Path $outFile -Leaf)" | Out-File -FilePath "$outFile.sha256" -Encoding ascii
Write-Host "Audit evidence: $outFile  ($($results.Count) rows)  SHA-256 $hash" -ForegroundColor Green

Disconnect-ExchangeOnline -Confirm:$false
```

---

## Scheduling

Schedule **Get-AIDisclaimerRolloutEvidence**, **Get-AgentZoneInventory**, **Get-ConsentRecords**, and **Search-DisclosureAuditEvidence** on a weekly cadence. Prefer **Azure Automation** or a hardened **Power Automate Desktop** runner over Windows Task Scheduler for FSI tenants — both provide centralized identity, secret management, and run history that map cleanly to FINRA 3110 supervisory evidence requirements.

---

## Deployment Checklist

- [ ] All five scripts execute without error in a non-production environment first
- [ ] Output directory `C:\AgentGov\Evidence\2.23\` exists and is access-controlled
- [ ] Module versions match the CAB-approved baseline
- [ ] Service principal used for Dataverse writes is documented in the access register
- [ ] SHA-256 hashes are emitted for every CSV / JSON evidence file
- [ ] Scheduled runs feed the governance evidence binder (Control 2.13)

---

[Back to Control 2.23](../../../controls/pillar-2-management/2.23-user-consent-and-ai-disclosure-enforcement.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
