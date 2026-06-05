# Control 4.6 – PowerShell Setup: Grounding Scope Governance

> **DANGER — Mutation safety required.**
> This playbook configures **tenant-wide search behaviour** (Restricted SharePoint Search), **per-site discoverability** (Restricted Content Discoverability), and **Power Platform DLP** for the SharePoint connector consumed by Microsoft Copilot Studio knowledge sources. A misconfiguration can either (a) hide legitimate content from Microsoft 365 Copilot and grounded agents or (b) expose oversharing-risk content to agent grounding. **Every mutating script in this suite uses `[CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]`. Always run with `-WhatIf` first, capture the transcript, review the before-snapshot, and only then re-run with `-Confirm:$false` inside a change window.**

**Control:** [4.6 – Grounding Scope Governance](../../../controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md)
**Pillar:** Pillar 4 — SharePoint
**Audience:** SharePoint Admin, Power Platform Admin, Compliance/Records Admin (read-only DAG)
**Prerequisites:** Read [`_shared/powershell-baseline.md`](../../_shared/powershell-baseline.md) first — module pinning, edition guards, sovereign endpoints, and the `Write-FsiEvidence` SHA-256 helper used throughout this playbook are defined there.

This playbook delivers the six-script PowerShell suite that supports Control 4.6 by:

1. Inventorying current grounding-relevant configuration (Data Access Governance reports, RSS mode, RCD per-site flags, DLP policies covering the SharePoint connector).
2. Curating and applying the **Restricted SharePoint Search (RSS) allow-list** (≤100 sites cap, hub-aware).
3. Applying **Restricted Content Discoverability (RCD)** per site plus optional delegation.
4. Applying a **Power Platform DLP policy** that classifies the SharePoint connector consumed by Copilot Studio.
5. Reconciling intended vs effective state (Get-after-Set on real properties).
6. Emitting tamper-evident SHA-256 evidence manifests for audit (supports SEC 17a-4 / FINRA 4511 / SOX 404 record-keeping; this playbook does not by itself satisfy any regulation).

---

## Section 0 — Wrong-shell trap: session/edition matrix

Each module in this suite has a **different** PowerShell edition requirement. Running the wrong cmdlet in the wrong shell silently fails or returns stale data. Use a dedicated session per module.

| # | Module | Required edition | Connect cmdlet (commercial) | Notes |
|---|---|---|---|---|
| 1 | `Microsoft.Online.SharePoint.PowerShell` (SPO Mgmt Shell) | Windows PowerShell **5.1** preferred. PowerShell **7.x** requires `Import-Module Microsoft.Online.SharePoint.PowerShell -UseWindowsPowerShell`. | `Connect-SPOService -Url https://<tenant>-admin.sharepoint.com` | Owns: `Set-SPOTenantRestrictedSearchMode`, `*-SPOTenantRestrictedSearchAllowedList`, `Set-SPOSite -RestrictContentOrgWideSearch`, `Get-SPODataAccessGovernanceInsight`, `Start-SPORestrictedContentDiscoverabilityReport`. |
| 2 | `PnP.PowerShell` v2+ | PowerShell **7.2+** Core only. Will not load on 5.1. | `Connect-PnPOnline -Url https://<tenant>.sharepoint.com -ClientId <Entra-app-GUID> -Interactive` | v2 **mandates** `-ClientId` (Entra app registration). v1.x is end-of-life. Used here only for site enumeration helpers. |
| 3 | `Microsoft.PowerApps.Administration.PowerShell` | Windows PowerShell **5.1 (Desktop) ONLY**. **Silent failures** under PowerShell 7. | `Add-PowerAppsAccount -Endpoint prod` | Owns: `New-DlpPolicy`, `Get-DlpPolicy`, `Set-DlpPolicy`, `Get-AdminPowerAppConnector`. |
| 4 | `ExchangeOnlineManagement` (Unified Audit Log) | PowerShell **5.1 or 7.x** both supported. | `Connect-ExchangeOnline` | Owns: `Search-UnifiedAuditLog` used by `Audit-GroundingChanges.ps1`. |
| 5 | `Microsoft.Graph` (optional, for site lookups by Group ID) | PowerShell **7.x** preferred. | `Connect-MgGraph -Scopes Sites.Read.All` | Optional — only used in §3 if you need to resolve M365 Group sites. |

**Rule:** open **two PowerShell windows** for this playbook — one Windows PowerShell 5.1 (rows 1, 3, 4) and one PowerShell 7 (rows 2, 5 if used). Pin module versions per `_shared/powershell-baseline.md` §1.

---

## Section 1 — `Initialize-Agt46Session` pre-flight

Run this dot-sourced helper at the top of **every** session before any of the numbered scripts. It enforces edition guards, sovereign endpoint resolution, output folder layout, transcript start, and module version pinning.

```powershell
# Initialize-Agt46Session.ps1
[CmdletBinding()]
param(
    [ValidateSet('Commercial','GCC','GCCHigh','DoD','China')]
    [string]$Cloud = 'Commercial',

    [Parameter(Mandatory)]
    [string]$TenantName,                 # e.g. 'contoso' (no .onmicrosoft.com)

    [Parameter(Mandatory)]
    [string]$EntraAppClientId,           # Entra app registration GUID for PnP v2

    [string]$OutputRoot = "$PSScriptRoot\..\output\4.6",

    [ValidateSet('SPO','PowerApps','Exchange','Graph','All')]
    [string[]]$Modules = @('SPO')
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

# --- Edition guards ---------------------------------------------------------
$psMajor = $PSVersionTable.PSVersion.Major
$psEdition = $PSVersionTable.PSEdition

if ($Modules -contains 'PowerApps' -or $Modules -contains 'All') {
    if ($psEdition -ne 'Desktop') {
        throw "Microsoft.PowerApps.Administration.PowerShell requires Windows PowerShell 5.1 (Desktop). Current: $psEdition $psMajor. Open a Windows PowerShell 5.1 console and re-run."
    }
}
if ($Modules -contains 'PnP') {
    if ($psMajor -lt 7) {
        throw "PnP.PowerShell v2+ requires PowerShell 7.2+. Current: $psEdition $psMajor."
    }
}

# --- Sovereign endpoint matrix ---------------------------------------------
$endpoints = @{
    Commercial = @{ SPOAdmin='https://{0}-admin.sharepoint.com';            SPORegion=$null;   PnPEnv='Production';     PowerAppsEndpoint='prod'    }
    GCC        = @{ SPOAdmin='https://{0}-admin.sharepoint.com';            SPORegion=$null;   PnPEnv='USGovernment';   PowerAppsEndpoint='usgov'   }
    GCCHigh    = @{ SPOAdmin='https://{0}-admin.sharepoint.us';             SPORegion='ITAR';  PnPEnv='USGovernmentHigh'; PowerAppsEndpoint='usgovhigh' }
    DoD        = @{ SPOAdmin='https://{0}-admin.dps.mil';                   SPORegion='ITAR';  PnPEnv='USGovernmentDoD';  PowerAppsEndpoint='dod'   }
    China      = @{ SPOAdmin='https://{0}-admin.sharepoint.cn';             SPORegion=$null;   PnPEnv='China';          PowerAppsEndpoint='china'   }
}
$ep = $endpoints[$Cloud]
$adminUrl = $ep.SPOAdmin -f $TenantName

# --- Output folder + transcript --------------------------------------------
$runId  = (Get-Date -Format 'yyyyMMdd-HHmmss') + '-' + ([guid]::NewGuid().ToString('N').Substring(0,8))
$runDir = Join-Path $OutputRoot $runId
New-Item -ItemType Directory -Path $runDir -Force | Out-Null
$transcript = Join-Path $runDir 'transcript.log'
Start-Transcript -Path $transcript -IncludeInvocationHeader | Out-Null

# --- Module version pinning -------------------------------------------------
$pins = @{
    'Microsoft.Online.SharePoint.PowerShell'      = '16.0.25212.12000'
    'PnP.PowerShell'                              = '2.12.0'
    'Microsoft.PowerApps.Administration.PowerShell' = '2.0.198'
    'ExchangeOnlineManagement'                    = '3.5.1'
    'Microsoft.Graph.Authentication'              = '2.19.0'
    'Microsoft.Graph.Sites'                       = '2.19.0'
}
foreach ($m in $pins.Keys) {
    if (Get-Module -ListAvailable -Name $m | Where-Object Version -eq $pins[$m]) {
        Write-Verbose "Module $m@$($pins[$m]) present."
    } else {
        Write-Warning "Module $m@$($pins[$m]) not installed at pinned version. Install via: Install-Module $m -RequiredVersion $($pins[$m]) -Scope CurrentUser"
    }
}

# --- Connect ---------------------------------------------------------------
if ($Modules -contains 'SPO' -or $Modules -contains 'All') {
    Import-Module Microsoft.Online.SharePoint.PowerShell -DisableNameChecking -ErrorAction Stop
    if ($ep.SPORegion) {
        Connect-SPOService -Url $adminUrl -Region $ep.SPORegion
    } else {
        Connect-SPOService -Url $adminUrl
    }
}
if ($Modules -contains 'PowerApps' -or $Modules -contains 'All') {
    Import-Module Microsoft.PowerApps.Administration.PowerShell -ErrorAction Stop
    Add-PowerAppsAccount -Endpoint $ep.PowerAppsEndpoint | Out-Null
}
if ($Modules -contains 'Exchange' -or $Modules -contains 'All') {
    Import-Module ExchangeOnlineManagement -ErrorAction Stop
    Connect-ExchangeOnline -ShowBanner:$false
}

# --- Return session context ------------------------------------------------
[pscustomobject]@{
    Cloud         = $Cloud
    TenantName    = $TenantName
    AdminUrl      = $adminUrl
    SPORegion     = $ep.SPORegion
    PnPEnv        = $ep.PnPEnv
    PAEndpoint    = $ep.PowerAppsEndpoint
    EntraAppId    = $EntraAppClientId
    RunId         = $runId
    RunDir        = $runDir
    Transcript    = $transcript
    StartedUtc    = (Get-Date).ToUniversalTime()
}
```

**Usage:**

```powershell
$ctx = .\Initialize-Agt46Session.ps1 `
        -Cloud GCCHigh `
        -TenantName contoso `
        -EntraAppClientId 'a1b2c3d4-...' `
        -Modules SPO,Exchange
```

`$ctx` is then passed to every numbered script. The `$ctx.RunDir` folder is the **only** location any script writes to.

---

## Section 2 — Scope boundary table: RCD vs RSS vs RAC vs DAG

Operators routinely conflate these four mechanisms. Choose the wrong one and you either over-restrict (breaking legitimate Copilot grounding) or under-restrict (leaking oversharing-risk content into agent answers).

| Mechanism | Scope | Effect on Copilot grounding | Cmdlet surface | When to use |
|---|---|---|---|---|
| **RCD** — Restricted Content Discoverability | **Per site** | Site contents excluded from org-wide search results, including Copilot grounding. Direct-link access still works. | `Set-SPOSite -Identity <url> -RestrictContentOrgWideSearch $true`; `Set-SPOTenant -DelegateRestrictedContentDiscoverabilityManagement $true` | Surgical: a small number of sensitive sites you want excluded from Copilot/agent answers. |
| **RSS** — Restricted SharePoint Search | **Tenant**, with allow-list ≤100 sites | When Enabled: Copilot grounding restricted to sites on the allow-list **plus** OneDrive/email/chat. Default search UI restricted to user's frequent sites. | `Set-SPOTenantRestrictedSearchMode -Mode Enabled\|Disabled`; `Add/Remove/Get-SPOTenantRestrictedSearchAllowedList -SitesList` | Bridging control during Copilot rollout while you remediate oversharing org-wide. |
| **RAC** — Restricted Access Control | **Per site** | Hard access policy: only members of a specified Entra group/Team can access the site at all. Stronger than RCD. | `Set-SPOSite -Identity <url> -RestrictedAccessControl $true`; `Set-SPOTenantRestrictedAccessControlPolicy ...` | Confidential sites where even direct-link access must be blocked for non-members. |
| **DAG** — Data Access Governance | **Reporting only (read-only)** | No mutation. Surfaces oversharing-risk sites (everyone-except-external-users sharing, anonymous links, etc.) so you can decide whether to apply RCD/RSS/RAC. | `Get-SPODataAccessGovernanceInsight -ReportEntity <enum>`; `Start-SPORestrictedContentDiscoverabilityReport` | Continuous monitoring; feeds the inventory in §3. |

**Decision rule for this playbook:** start with DAG (§3 inventory) → choose RSS allow-list strategy (§4) → apply RCD to anything that must be excluded but is not a candidate for the RSS allow-list (§5) → wrap the SharePoint connector to Copilot Studio with DLP (§6).

---

## Section 3 — `1-Inventory.ps1` (DAG report extraction + baseline)

Read-only. Produces a baseline JSON snapshot of grounding-relevant configuration **before** any mutation.

```powershell
# 1-Inventory.ps1
[CmdletBinding()]
param(
    [Parameter(Mandatory)] $Ctx,

    # ReportEntity values per Get-SPODataAccessGovernanceInsight enum
    [ValidateSet(
        'Everyone','EveryoneExceptExternalUsers','EveryoneExceptExternalUsersAtSite',
        'EveryoneExceptExternalUsersForItems','PermissionedUsers','PermissionsReport',
        'SensitivityLabelForFiles','SharingLinks_Anyone','SharingLinks_Guests',
        'SharingLinks_PeopleInYourOrg'
    )]
    [string[]]$DagReports = @(
        'SharingLinks_Anyone',
        'SharingLinks_PeopleInYourOrg',
        'EveryoneExceptExternalUsersAtSite',
        'SensitivityLabelForFiles'
    )
)

. "$PSScriptRoot\Write-FsiEvidence.ps1"   # from _shared/powershell-baseline.md §4

$ErrorActionPreference = 'Stop'
$out = $Ctx.RunDir
Write-Host "[1-Inventory] Run $($Ctx.RunId) -> $out"

# --- 1. RSS tenant mode ---------------------------------------------------
$rssMode = Get-SPOTenantRestrictedSearchMode    # returns 'Enabled' or 'Disabled' string
$rssMode | ConvertTo-Json | Out-File (Join-Path $out 'rss-mode.json')

# --- 2. RSS allow-list ----------------------------------------------------
$rssAllow = Get-SPOTenantRestrictedSearchAllowedList
$rssAllow | ConvertTo-Json -Depth 4 | Out-File (Join-Path $out 'rss-allowlist.json')

# --- 3. RCD per-site flags (sample by enumerating all sites) -------------
# Note: Get-SPOSite is paged; for very large tenants restrict via -Filter or -Template.
$sites = Get-SPOSite -Limit All -IncludePersonalSite:$false |
         Select-Object Url, Title, Template, Owner, StorageUsageCurrent,
                       RestrictContentOrgWideSearch
$sites | Export-Csv (Join-Path $out 'sites-baseline.csv') -NoTypeInformation -Encoding UTF8
($sites | Where-Object RestrictContentOrgWideSearch) |
    Export-Csv (Join-Path $out 'sites-rcd-on.csv') -NoTypeInformation -Encoding UTF8

# --- 4. RCD delegation flag ----------------------------------------------
$tenant = Get-SPOTenant
$tenant | Select-Object DelegateRestrictedContentDiscoverabilityManagement,
                       SearchResolveExactEmailOrUPN |
    ConvertTo-Json | Out-File (Join-Path $out 'rcd-delegation.json')

# --- 5. DAG insights ------------------------------------------------------
foreach ($rpt in $DagReports) {
    Write-Host "  DAG: $rpt"
    try {
        $insights = Get-SPODataAccessGovernanceInsight -ReportEntity $rpt -Workload SharePoint -ReportType Snapshot
        $insights | Export-Csv (Join-Path $out "dag-$rpt.csv") -NoTypeInformation -Encoding UTF8
    } catch {
        Write-Warning "DAG report $rpt failed: $($_.Exception.Message). (DAG is unavailable in some sovereign clouds — see §11.)"
    }
}

# --- 6. SHA-256 evidence manifest ----------------------------------------
Write-FsiEvidence -RunDir $out -ScriptName '1-Inventory.ps1' -Context $Ctx
```

**Outputs (all in `$Ctx.RunDir`):**

- `rss-mode.json`, `rss-allowlist.json`
- `sites-baseline.csv`, `sites-rcd-on.csv`
- `rcd-delegation.json`
- `dag-<entity>.csv` (one per DAG report)
- `evidence-manifest.json` (SHA-256 hashes of every file above)

---

## Section 4 — `2-Curate-RSSAllowList.ps1` (≤100-site cap, hub-aware)

Builds the RSS allow-list from a curated CSV. Enforces the **100-site cap** (hub-associated sites do **not** count against the cap — only the hub itself does). Mutating; runs `-WhatIf` by default.

```powershell
# 2-Curate-RSSAllowList.ps1
[CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
param(
    [Parameter(Mandatory)] $Ctx,

    # CSV with columns: Url,Justification,DataOwner,SoDApprover,Category
    [Parameter(Mandatory)]
    [string]$AllowListCsvPath,

    # If set, also enable RSS tenant mode after applying the list.
    [switch]$EnableRssMode
)

. "$PSScriptRoot\Write-FsiEvidence.ps1"

$ErrorActionPreference = 'Stop'
$out = $Ctx.RunDir

# --- Validate CSV ---------------------------------------------------------
$rows = Import-Csv $AllowListCsvPath
$required = 'Url','Justification','DataOwner','SoDApprover','Category'
foreach ($col in $required) {
    if (-not ($rows | Get-Member -Name $col -MemberType NoteProperty)) {
        throw "AllowList CSV missing required column: $col"
    }
}
foreach ($r in $rows) {
    foreach ($col in $required) {
        if ([string]::IsNullOrWhiteSpace($r.$col)) {
            throw "Row for $($r.Url): empty value in column $col."
        }
    }
    if ($r.DataOwner -ieq $r.SoDApprover) {
        throw "SoD violation row for $($r.Url): DataOwner and SoDApprover cannot be the same person."
    }
}

# --- Hub-aware count ------------------------------------------------------
$intended = $rows.Url | Sort-Object -Unique
Write-Host "[2-Curate] Intended sites: $($intended.Count)"

# Resolve hub status: hub-associated sites do NOT count, but the hub does.
$hubMap = @{}
foreach ($u in $intended) {
    try {
        $s = Get-SPOSite -Identity $u -Detailed
        $hubMap[$u] = [pscustomobject]@{
            Url        = $u
            HubSiteId  = $s.HubSiteId
            IsHub      = ($s.IsHubSite -eq $true)
        }
    } catch {
        Write-Warning "Cannot resolve $u (skipped from cap calculation): $($_.Exception.Message)"
    }
}
$countsTowardCap = @($hubMap.Values | Where-Object {
    $_.IsHub -or [string]::IsNullOrEmpty($_.HubSiteId) -or $_.HubSiteId -eq '00000000-0000-0000-0000-000000000000'
}).Count

Write-Host "[2-Curate] Sites counted against 100-cap: $countsTowardCap (hub-associated sites do not count)."
if ($countsTowardCap -gt 100) {
    throw "Allow-list exceeds RSS 100-site cap ($countsTowardCap). Consolidate via hub association."
}

# --- Snapshot before -----------------------------------------------------
$before = Get-SPOTenantRestrictedSearchAllowedList
$before | ConvertTo-Json -Depth 4 | Out-File (Join-Path $out 'rss-allowlist-before.json')
$rows | Export-Csv (Join-Path $out 'rss-allowlist-intended.csv') -NoTypeInformation -Encoding UTF8

# --- Apply ---------------------------------------------------------------
if ($PSCmdlet.ShouldProcess("RSS allow-list ($($intended.Count) sites)", "Add-SPOTenantRestrictedSearchAllowedList")) {
    Add-SPOTenantRestrictedSearchAllowedList -SitesList $intended
}

if ($EnableRssMode -and $PSCmdlet.ShouldProcess("Tenant", "Set-SPOTenantRestrictedSearchMode -Mode Enabled")) {
    Set-SPOTenantRestrictedSearchMode -Mode Enabled
}

# --- Snapshot after ------------------------------------------------------
$after = Get-SPOTenantRestrictedSearchAllowedList
$after | ConvertTo-Json -Depth 4 | Out-File (Join-Path $out 'rss-allowlist-after.json')

Write-FsiEvidence -RunDir $out -ScriptName '2-Curate-RSSAllowList.ps1' -Context $Ctx
```

**Notes:**

- Always rehearse with `-WhatIf` (the default `ConfirmImpact='High'` plus omitting `-Confirm:$false` gives an interactive prompt).
- The CSV must include `DataOwner` and `SoDApprover` as distinct identities — enforces segregation-of-duties for the allow-list (supports Control 1.5 evidence).
- `-SitesListFileUrl <localCsvPath> [-ContainsHeader $true]` is also supported by the underlying cmdlet if you prefer file-based input — see Microsoft Learn for `Add-SPOTenantRestrictedSearchAllowedList`.

---

## Section 5 — `3-Apply-RCD.ps1` (per-site + delegation)

Applies Restricted Content Discoverability per site from a curated CSV; optionally toggles delegation so site collection admins can self-manage RCD.

```powershell
# 3-Apply-RCD.ps1
[CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
param(
    [Parameter(Mandatory)] $Ctx,

    # CSV columns: Url,Action(set|unset),Justification,DataOwner,SoDApprover
    [Parameter(Mandatory)] [string]$RcdCsvPath,

    [ValidateSet('Enable','Disable','NoChange')]
    [string]$Delegation = 'NoChange'
)

. "$PSScriptRoot\Write-FsiEvidence.ps1"

$ErrorActionPreference = 'Stop'
$out = $Ctx.RunDir
$rows = Import-Csv $RcdCsvPath

foreach ($r in $rows) {
    if ([string]::IsNullOrWhiteSpace($r.Url) -or $r.Action -notin 'set','unset') {
        throw "Invalid row: $($r | ConvertTo-Json -Compress)"
    }
    if ($r.DataOwner -ieq $r.SoDApprover) {
        throw "SoD violation for $($r.Url)."
    }
}

# Snapshot before
$urls = $rows.Url | Sort-Object -Unique
$before = foreach ($u in $urls) {
    try { Get-SPOSite -Identity $u | Select Url, RestrictContentOrgWideSearch }
    catch { [pscustomobject]@{ Url=$u; RestrictContentOrgWideSearch='UNREADABLE' } }
}
$before | Export-Csv (Join-Path $out 'rcd-sites-before.csv') -NoTypeInformation -Encoding UTF8

# Apply per site
foreach ($r in $rows) {
    $desired = ($r.Action -eq 'set')
    if ($PSCmdlet.ShouldProcess($r.Url, "Set-SPOSite -RestrictContentOrgWideSearch `$$desired")) {
        try {
            Set-SPOSite -Identity $r.Url -RestrictContentOrgWideSearch $desired
        } catch {
            Write-Warning "Failed $($r.Url): $($_.Exception.Message)"
        }
    }
}

# Optional delegation toggle
switch ($Delegation) {
    'Enable'  { if ($PSCmdlet.ShouldProcess('Tenant','Set-SPOTenant -DelegateRestrictedContentDiscoverabilityManagement $true'))  { Set-SPOTenant -DelegateRestrictedContentDiscoverabilityManagement $true  } }
    'Disable' { if ($PSCmdlet.ShouldProcess('Tenant','Set-SPOTenant -DelegateRestrictedContentDiscoverabilityManagement $false')) { Set-SPOTenant -DelegateRestrictedContentDiscoverabilityManagement $false } }
}

# Snapshot after
$after = foreach ($u in $urls) {
    try { Get-SPOSite -Identity $u | Select Url, RestrictContentOrgWideSearch }
    catch { [pscustomobject]@{ Url=$u; RestrictContentOrgWideSearch='UNREADABLE' } }
}
$after | Export-Csv (Join-Path $out 'rcd-sites-after.csv') -NoTypeInformation -Encoding UTF8

Write-FsiEvidence -RunDir $out -ScriptName '3-Apply-RCD.ps1' -Context $Ctx
```

---

## Section 6 — `4-Apply-SPConnectorDLP.ps1` (Power Platform DLP for SharePoint connector)

Wraps the SharePoint connector consumed by Copilot Studio knowledge sources in a Power Platform DLP policy. **Connector ID is a parameter** — do not hardcode. Run in **Windows PowerShell 5.1 only**.

### 6.1 — Discover the connector ID first (one-time)

The SharePoint connector's invariant `Name` (e.g. `shared_sharepointonline`) is documented but should always be **verified in your tenant** because some sovereign clouds expose connector variants with different names. PPAC also shows it under **Data → Connectors**.

```powershell
# Run once to confirm the connector ID for this tenant + cloud.
Get-AdminPowerAppConnector |
    Where-Object { $_.DisplayName -match 'SharePoint' -or $_.DisplayName -match 'Copilot' } |
    Select-Object DisplayName, Name, Publisher | Format-Table -AutoSize
```

Verify the result against PPAC (`https://admin.powerplatform.microsoft.com` → **Data → Connectors**) before passing to the script below.

### 6.2 — Apply policy

```powershell
# 4-Apply-SPConnectorDLP.ps1
#requires -PSEdition Desktop          # Power Platform admin module is Desktop-only.
[CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
param(
    [Parameter(Mandatory)] $Ctx,

    [Parameter(Mandatory)] [string]$PolicyDisplayName,    # e.g. 'FSI-4.6-CopilotKnowledgeSources'

    # Verified via discovery snippet in §6.1.
    [Parameter(Mandatory)] [string]$SharePointConnectorId,  # typically 'shared_sharepointonline'

    [ValidateSet('AllEnvironments','OnlyEnvironments','ExceptEnvironments')]
    [string]$EnvironmentType = 'OnlyEnvironments',

    [string[]]$EnvironmentIds = @(),                       # Required when scope != AllEnvironments

    [ValidateSet('Confidential','General','Blocked')]
    [string]$SharePointClassification = 'Confidential',

    [ValidateSet('Confidential','General','Blocked')]
    [string]$DefaultClassification = 'General'
)

. "$PSScriptRoot\Write-FsiEvidence.ps1"
$ErrorActionPreference = 'Stop'
$out = $Ctx.RunDir

# --- Snapshot before -----------------------------------------------------
$before = Get-DlpPolicy
$before | ConvertTo-Json -Depth 6 | Out-File (Join-Path $out 'dlp-before.json')

# --- Create policy --------------------------------------------------------
if ($PSCmdlet.ShouldProcess($PolicyDisplayName, "New-DlpPolicy -EnvironmentType $EnvironmentType")) {
    $newArgs = @{
        DisplayName                    = $PolicyDisplayName
        EnvironmentType                = $EnvironmentType
        DefaultConnectorClassification = $DefaultClassification
    }
    if ($EnvironmentType -ne 'AllEnvironments') {
        if (-not $EnvironmentIds) { throw "EnvironmentIds required when EnvironmentType=$EnvironmentType." }
        $newArgs.Environments = $EnvironmentIds | ForEach-Object {
            @{ id = $_ ; name = $_ ; type = 'Microsoft.PowerApps/scopes/environments' }
        }
    }
    $policy = New-DlpPolicy @newArgs
}

# --- Move SharePoint connector into the chosen group ---------------------
if ($PSCmdlet.ShouldProcess($SharePointConnectorId, "Add-CustomConnectorToPolicy -GroupName $SharePointClassification")) {
    Add-ConnectorToBusinessDataGroup -PolicyName $policy.PolicyName -ConnectorName $SharePointConnectorId
    # Note: `Add-ConnectorToBusinessDataGroup` places the connector in the Confidential group;
    # if your target classification is General/Blocked, use the appropriate move cmdlet:
    # `Remove-ConnectorFromBusinessDataGroup` then `Add-ConnectorToNonBusinessDataGroup` / `Add-ConnectorToBlockedList`.
}

# --- Snapshot after ------------------------------------------------------
$after = Get-DlpPolicy
$after | ConvertTo-Json -Depth 6 | Out-File (Join-Path $out 'dlp-after.json')

Write-FsiEvidence -RunDir $out -ScriptName '4-Apply-SPConnectorDLP.ps1' -Context $Ctx
```

**Why parameterise the connector ID:** the invariant name has historically changed during connector renames; sovereign-cloud variants may differ. Hardcoding causes silent drift between docs and reality. The §6.1 discovery snippet is the source of truth for *your* tenant.

---

## Section 7 — `5-Reconcile.ps1` (Get-after-Set on real properties)

Verifies intended state against effective state. Emits `[OK]`, `[WARN]`, `[ALERT]` lines and a JSON reconciliation report. **Read-only** — no `SupportsShouldProcess`.

```powershell
# 5-Reconcile.ps1
[CmdletBinding()]
param(
    [Parameter(Mandatory)] $Ctx,
    [Parameter(Mandatory)] [string]$IntendedRssAllowListCsv,
    [Parameter(Mandatory)] [string]$IntendedRcdCsv,
    [string]$IntendedDlpPolicyName,
    [string]$IntendedSharePointConnectorId
)

. "$PSScriptRoot\Write-FsiEvidence.ps1"
$ErrorActionPreference = 'Stop'
$out = $Ctx.RunDir
$report = [System.Collections.Generic.List[object]]::new()

function Add-Finding($Severity, $Area, $Detail) {
    $line = "[$Severity] $Area :: $Detail"
    Write-Host $line
    $report.Add([pscustomobject]@{ Severity=$Severity; Area=$Area; Detail=$Detail; TsUtc=(Get-Date).ToUniversalTime() })
}

# --- 1. RSS mode ---------------------------------------------------------
$mode = Get-SPOTenantRestrictedSearchMode
if ($mode -eq 'Enabled') { Add-Finding 'OK'    'RSS-Mode' "RSS mode = Enabled" }
else                     { Add-Finding 'WARN'  'RSS-Mode' "RSS mode = $mode (expected Enabled if rollout complete)" }

# --- 2. RSS allow-list ---------------------------------------------------
$intendedRss = (Import-Csv $IntendedRssAllowListCsv).Url | Sort-Object -Unique
$effectiveRss = (Get-SPOTenantRestrictedSearchAllowedList).Sites | Sort-Object -Unique
$missing = $intendedRss | Where-Object { $_ -notin $effectiveRss }
$extra   = $effectiveRss | Where-Object { $_ -notin $intendedRss }
foreach ($m in $missing) { Add-Finding 'ALERT' 'RSS-AllowList' "Intended site missing from allow-list: $m" }
foreach ($x in $extra)   { Add-Finding 'WARN'  'RSS-AllowList' "Allow-list contains site not in intended CSV: $x" }
if (-not $missing -and -not $extra) { Add-Finding 'OK' 'RSS-AllowList' "Allow-list matches intended ($($intendedRss.Count) sites)" }

# --- 3. RCD per site -----------------------------------------------------
$rcdRows = Import-Csv $IntendedRcdCsv
foreach ($r in $rcdRows) {
    $desired = ($r.Action -eq 'set')
    try {
        $effective = (Get-SPOSite -Identity $r.Url).RestrictContentOrgWideSearch
        if ($effective -eq $desired) {
            Add-Finding 'OK' 'RCD-Site' "$($r.Url) RestrictContentOrgWideSearch=$effective"
        } else {
            Add-Finding 'ALERT' 'RCD-Site' "$($r.Url) intended=$desired effective=$effective"
        }
    } catch {
        Add-Finding 'ALERT' 'RCD-Site' "$($r.Url) UNREADABLE: $($_.Exception.Message)"
    }
}

# --- 4. DLP policy --------------------------------------------------------
if ($IntendedDlpPolicyName) {
    $pol = Get-DlpPolicy | Where-Object DisplayName -eq $IntendedDlpPolicyName
    if (-not $pol) {
        Add-Finding 'ALERT' 'DLP-Policy' "Policy '$IntendedDlpPolicyName' not found."
    } else {
        Add-Finding 'OK' 'DLP-Policy' "Policy '$IntendedDlpPolicyName' present (Name=$($pol.PolicyName))."
        if ($IntendedSharePointConnectorId) {
            $confidential = $pol.ConnectorGroups | Where-Object Classification -eq 'Confidential'
            $hit = $confidential.Connectors | Where-Object Id -match [regex]::Escape($IntendedSharePointConnectorId)
            if ($hit) { Add-Finding 'OK'    'DLP-Connector' "$IntendedSharePointConnectorId in Confidential group." }
            else      { Add-Finding 'ALERT' 'DLP-Connector' "$IntendedSharePointConnectorId NOT in Confidential group." }
        }
    }
}

$report | Export-Csv (Join-Path $out 'reconcile.csv') -NoTypeInformation -Encoding UTF8
$report | ConvertTo-Json -Depth 4 | Out-File (Join-Path $out 'reconcile.json')

Write-FsiEvidence -RunDir $out -ScriptName '5-Reconcile.ps1' -Context $Ctx

$alerts = ($report | Where-Object Severity -eq 'ALERT').Count
if ($alerts -gt 0) { exit 2 } else { exit 0 }
```

Non-zero exit (`2`) on any `[ALERT]` lets schedulers (e.g. Azure Automation, scheduled task) raise an incident.

---

## Section 8 — `Audit-GroundingChanges.ps1` (Unified Audit Log collector)

Pulls grounding-relevant audit records from the Unified Audit Log. **Paged**, with a 50,000-row safety ceiling per run to prevent runaway pulls.

```powershell
# Audit-GroundingChanges.ps1
[CmdletBinding()]
param(
    [Parameter(Mandatory)] $Ctx,
    [DateTime]$StartUtc = (Get-Date).ToUniversalTime().AddDays(-7),
    [DateTime]$EndUtc   = (Get-Date).ToUniversalTime(),
    [int]$PageSize      = 5000,
    [int]$MaxRows       = 50000
)

. "$PSScriptRoot\Write-FsiEvidence.ps1"
$ErrorActionPreference = 'Stop'
$out = $Ctx.RunDir

$ops = @(
    'TenantRestrictedSearchModeUpdated',
    'TenantRestrictedSearchAllowedListUpdated',
    'SiteRestrictedContentDiscoverabilityUpdated',
    'TenantDelegateRestrictedContentDiscoverabilityManagementUpdated',
    'DlpPolicyCreated','DlpPolicyUpdated','DlpPolicyDeleted',
    'CopilotInteraction'
)

$all = [System.Collections.Generic.List[object]]::new()
$sessionId = [guid]::NewGuid().ToString()
$page = 0
do {
    $page++
    $batch = Search-UnifiedAuditLog `
        -StartDate $StartUtc -EndDate $EndUtc `
        -Operations $ops `
        -ResultSize $PageSize `
        -SessionId $sessionId -SessionCommand ReturnLargeSet
    if ($batch) { $all.AddRange($batch) }
    Write-Host "  page $page collected $($batch.Count) (total $($all.Count))"
    if ($all.Count -ge $MaxRows) {
        Write-Warning "Hit MaxRows ceiling ($MaxRows). Re-run with narrower window."
        break
    }
} while ($batch -and $batch.Count -eq $PageSize)

$all | Export-Csv (Join-Path $out 'audit-grounding.csv') -NoTypeInformation -Encoding UTF8
$all | ConvertTo-Json -Depth 6 | Out-File (Join-Path $out 'audit-grounding.json')

Write-FsiEvidence -RunDir $out -ScriptName 'Audit-GroundingChanges.ps1' -Context $Ctx
```

**Notes:**

- `Search-UnifiedAuditLog` is rate-limited; large windows must be split.
- Audit availability and retention depend on licence (E5 / Audit Premium) — see Control 1.7.
- `CopilotInteraction` records grounding-source citations; correlate against RCD/RSS changes when investigating an incident (Control 1.7 + the [AI Incident Response Playbook](../../incident-and-risk/ai-incident-response-playbook.md)).

---

## Section 9 — SHA-256 evidence manifest schema + validator

Every script in this suite calls `Write-FsiEvidence` (defined in `_shared/powershell-baseline.md` §4). The emitted manifest schema:

```json
{
  "schemaVersion": "1.0",
  "control":      "4.6",
  "scriptName":   "2-Curate-RSSAllowList.ps1",
  "runId":        "20260415-093212-7f3a9b21",
  "runDir":       "C:\\fsi\\agt-output\\4.6\\20260415-093212-7f3a9b21",
  "tenantName":   "contoso",
  "cloud":        "GCCHigh",
  "startedUtc":   "2026-04-15T09:32:12Z",
  "completedUtc": "2026-04-15T09:34:48Z",
  "operator":     "DOMAIN\\jane.doe",
  "files": [
    { "name": "rss-allowlist-before.json",   "bytes": 18421, "sha256": "f3a1...e29c" },
    { "name": "rss-allowlist-intended.csv",  "bytes": 12044, "sha256": "9b40...a715" },
    { "name": "rss-allowlist-after.json",    "bytes": 18602, "sha256": "1c77...88e0" },
    { "name": "transcript.log",              "bytes": 41108, "sha256": "ad0c...3392" }
  ]
}
```

**Validator** (run before any audit hand-over):

```powershell
# Verify-EvidenceManifest.ps1
param([Parameter(Mandatory)][string]$ManifestPath)
$m = Get-Content $ManifestPath -Raw | ConvertFrom-Json
$root = Split-Path $ManifestPath -Parent
$bad = 0
foreach ($f in $m.files) {
    $p = Join-Path $root $f.name
    if (-not (Test-Path $p)) { Write-Warning "MISSING $($f.name)"; $bad++; continue }
    $h = (Get-FileHash $p -Algorithm SHA256).Hash.ToLower()
    if ($h -ne $f.sha256.ToLower()) { Write-Warning "HASH MISMATCH $($f.name) actual=$h"; $bad++ }
}
if ($bad -gt 0) { throw "$bad evidence file(s) failed verification." }
"OK: $($m.files.Count) files verified for run $($m.runId)."
```

Hand the manifest **plus** the file set to records management (supports SEC 17a-4 / FINRA 4511 evidentiary requirements; does not by itself satisfy any regulation — see Control 1.7 for the records-management governance wrap).

---

## Section 10 — `Rollback-Agt46.ps1` + §10a explicit disconnect

### 10. Rollback

```powershell
# Rollback-Agt46.ps1
[CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
param(
    [Parameter(Mandatory)] $Ctx,
    [Parameter(Mandatory)] [string]$BeforeRunDir,    # the $RunDir of a prior baseline run
    [string]$DlpPolicyDisplayNameToRemove
)

. "$PSScriptRoot\Write-FsiEvidence.ps1"
$ErrorActionPreference = 'Stop'
$out = $Ctx.RunDir

# 1. RSS mode
$beforeMode = Get-Content (Join-Path $BeforeRunDir 'rss-mode.json') -Raw | ConvertFrom-Json
if ($PSCmdlet.ShouldProcess('Tenant',"Set-SPOTenantRestrictedSearchMode -Mode $beforeMode")) {
    Set-SPOTenantRestrictedSearchMode -Mode $beforeMode
}

# 2. RSS allow-list (replace with prior contents)
$beforeAllow = Get-Content (Join-Path $BeforeRunDir 'rss-allowlist.json') -Raw | ConvertFrom-Json
$current = Get-SPOTenantRestrictedSearchAllowedList
if ($current.Sites) {
    if ($PSCmdlet.ShouldProcess('AllowList','Remove-SPOTenantRestrictedSearchAllowedList -SitesList $current.Sites')) {
        Remove-SPOTenantRestrictedSearchAllowedList -SitesList @($current.Sites)
    }
}
if ($beforeAllow.Sites) {
    if ($PSCmdlet.ShouldProcess('AllowList','Add-SPOTenantRestrictedSearchAllowedList -SitesList $beforeAllow.Sites')) {
        Add-SPOTenantRestrictedSearchAllowedList -SitesList @($beforeAllow.Sites)
    }
}

# 3. RCD per-site (restore from baseline CSV)
$beforeSites = Import-Csv (Join-Path $BeforeRunDir 'sites-baseline.csv')
foreach ($s in $beforeSites) {
    $desired = [bool]::Parse($s.RestrictContentOrgWideSearch)
    try {
        $cur = (Get-SPOSite -Identity $s.Url).RestrictContentOrgWideSearch
        if ($cur -ne $desired) {
            if ($PSCmdlet.ShouldProcess($s.Url,"Set-SPOSite -RestrictContentOrgWideSearch $desired")) {
                Set-SPOSite -Identity $s.Url -RestrictContentOrgWideSearch $desired
            }
        }
    } catch { Write-Warning "Skip $($s.Url): $($_.Exception.Message)" }
}

# 4. DLP policy removal (optional)
if ($DlpPolicyDisplayNameToRemove) {
    $pol = Get-DlpPolicy | Where-Object DisplayName -eq $DlpPolicyDisplayNameToRemove
    if ($pol -and $PSCmdlet.ShouldProcess($pol.DisplayName,'Remove-DlpPolicy')) {
        Remove-DlpPolicy -PolicyName $pol.PolicyName
    }
}

Write-FsiEvidence -RunDir $out -ScriptName 'Rollback-Agt46.ps1' -Context $Ctx
```

### 10a. Explicit disconnect at end of session

Always disconnect — leaving stale tokens around is an audit finding under Control 1.14 (data minimisation):

```powershell
try { Disconnect-SPOService }       catch {}
try { Disconnect-PnPOnline }        catch {}
try { Remove-PowerAppsAccount }     catch {}
try { Disconnect-ExchangeOnline -Confirm:$false } catch {}
try { Disconnect-MgGraph }          catch {}
Stop-Transcript | Out-Null
```

---

## Section 11 — Sovereign cloud matrix

| Cloud | `Connect-SPOService -Region` | `Connect-PnPOnline -AzureEnvironment` | `Add-PowerAppsAccount -Endpoint` | DAG availability | Notes |
|---|---|---|---|---|---|
| **Commercial** | *(omit)* | *(default `Production`)* | `prod` | Yes | Baseline. |
| **GCC** | *(omit)* | `USGovernment` | `usgov` | Yes | SPO admin host: `<tenant>-admin.sharepoint.com`. |
| **GCC High** | `ITAR` | `USGovernmentHigh` | `usgovhigh` | Yes | SPO admin host: `<tenant>-admin.sharepoint.us`. **Must** specify `-Region ITAR`. |
| **DoD** | `ITAR` | `USGovernmentDoD` | `dod` | Yes | SPO admin host: `<tenant>-admin.dps.mil`. **Must** specify `-Region ITAR`. |
| **China (21Vianet)** | *(cloud-specific)* | `China` | `china` | **No** (DAG unavailable per Microsoft Learn) | Replace DAG step in §3 with manual Sites-of-interest CSV; rest of suite functions. |

The `Initialize-Agt46Session` helper (§1) parameterises all of the above via `-Cloud`.

---

## Section 12 — Anti-pattern catalog (read before running)

Every item in this list has been observed in field engagements. Each maps to a `Write-Warning` or hard `throw` somewhere in this suite.

1. **`Set-SPOTenant -EnableRestrictedSearchAllList`** — does **not** exist. The correct cmdlet is `Set-SPOTenantRestrictedSearchMode -Mode Enabled|Disabled`.
2. **`Add-SPOTenantRestrictedSearchAllowedList -SiteUrl`** — `-SiteUrl` parameter does **not** exist. Use `-SitesList @(...)` or `-SitesListFileUrl <path>`.
3. **`Add-SPOTenantRestrictedSearchAllowedListSites`** — wrong cmdlet name; the correct name is `Add-SPOTenantRestrictedSearchAllowedList` (no `Sites` suffix).
4. **Running `New-DlpPolicy` / `Get-AdminPowerAppConnector` in PowerShell 7** — `Microsoft.PowerApps.Administration.PowerShell` is Desktop-edition only and fails silently. Always use Windows PowerShell 5.1.
5. **Omitting `-Region ITAR` on GCC High / DoD** — `Connect-SPOService` will appear to succeed against the wrong region and return zero data. Always pass `-Region ITAR` for those clouds.
6. **Hardcoding `shared_sharepointonline`** — connector invariant names have changed historically and differ across sovereign clouds. Discover (§6.1) and parameterise.
7. **Inferring site `ContentCategory` from URL substrings** (e.g. assuming `/sites/legal-*` is "Legal Confidential") — URL conventions drift; categorise from sensitivity labels and site metadata, not regex on URL.
8. **Counting hub-associated sites against the 100-site RSS cap** — they do not count; only the hub itself does. The §4 cap calculation reflects this.
9. **Rerunning `Add-SPOTenantRestrictedSearchAllowedList` instead of `Remove`-then-`Add`** when the intent is replacement — `Add` is additive, so the list grows past the cap.
10. **Running mutating scripts without `-WhatIf` first** — the `ConfirmImpact='High'` prompts can be muscle-memoried away. Always rehearse with `-WhatIf`, review the before-snapshot, then re-run.
11. **Using PnP.PowerShell v1.x** — end of life. v2+ requires `-ClientId <Entra app GUID>`; certificate or interactive auth.
12. **Skipping the SHA-256 evidence manifest** — hand-typed CSVs are not audit evidence. Always run `Verify-EvidenceManifest.ps1` (§9) before hand-over.
13. **Pulling Unified Audit Log without paging or a row ceiling** — `Search-UnifiedAuditLog` will time out or paginate forever. Use `-SessionId`/`-SessionCommand ReturnLargeSet` and the 50,000-row ceiling in §8.
14. **Treating DAG output as a remediation queue** — DAG is informational. Each flagged site needs a human decision (RCD, RSS allow-list, RAC, sensitivity label, owner contact) — see Control 4.1.
15. **Forgetting to `Disconnect-SPOService` / `Remove-PowerAppsAccount` / `Disconnect-ExchangeOnline`** — stale tokens linger. Always run §10a at end of session.
16. **Reading `Get-SPOTenantRestrictedSearchMode` as a boolean** — it returns the string `'Enabled'` or `'Disabled'`, not `$true`/`$false`. Compare with `-eq 'Enabled'`.
17. **Setting `RestrictContentOrgWideSearch` to a string** (`'true'`) — the parameter is `[bool]`. Pass `$true` / `$false`, not strings.
18. **Allowing the same identity to be DataOwner and SoDApprover** — segregation-of-duties violation; the §4 / §5 scripts hard-throw on this.

---

## Section 13 — Cross-links

| Asset | Why it matters here |
|---|---|
| [Control 4.6 — Grounding Scope Governance](../../../controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md) | Parent control: scope, regulatory references, governance levels. |
| [Control 4.1 — SharePoint IAG / Restricted Content Discovery](../../../controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md) | Upstream IAG capabilities feeding §3 inventory. |
| [Control 4.8 — Item-level Permission Scanning for Agent Knowledge Sources](../../../controls/pillar-4-sharepoint/4.8-item-level-permission-scanning-agent-knowledge-sources.md) | Item-level oversharing inside sites that are RSS-allowlisted. |
| [Control 1.5 — DLP and Sensitivity Labels](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) | Sensitivity-label inputs to DAG; DLP policy in §6 complements purview DLP. |
| [Control 1.7 — Comprehensive Audit Logging and Compliance](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) | UAL availability, retention, evidentiary handling for §8 + §9. |
| [Control 1.14 — Data Minimization and Agent Scope Control](../../../controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md) | Disconnect/token hygiene (§10a); minimum-scope grounding philosophy. |
| [Control 2.16 — RAG Source Integrity Validation](../../../controls/pillar-2-management/2.16-rag-source-integrity-validation.md) | Downstream: validates that allow-listed sources remain trustworthy. |
| [AI Incident Response Playbook](../../incident-and-risk/ai-incident-response-playbook.md) | When `5-Reconcile.ps1` or §8 audit pulls reveal unauthorised changes. |
| [`_shared/powershell-baseline.md`](../../_shared/powershell-baseline.md) | Module pinning, edition guards, sovereign endpoints, `Write-FsiEvidence` helper used everywhere above. |

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
