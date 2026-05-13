# Control 1.14 — PowerShell Setup: Data Minimization and Agent Scope Control

> **Scope.** This playbook is the canonical PowerShell automation reference for Control 1.14 — *Data Minimization and Agent Scope Control*. It enumerates Copilot Studio (Dataverse-backed) agents and Power Platform agent surfaces, builds a dedupe-keyed agent ↔ grounding-surface inventory, joins inventory to Power Platform DLP and to Microsoft Entra ID Governance Access Reviews, detects scope drift from the Unified Audit Log (UAL), reconciles SharePoint grounding against Control 4.6's Restricted Content Discovery (RCD) posture, and emits a SHA-256 evidence manifest. It supports US financial-services tenants in the Microsoft Commercial, GCC, GCC High, and DoD clouds.
>
> **Companion documents.**
>
> - Control specification — `docs/controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md`
> - Portal walkthrough — `./portal-walkthrough.md`
> - Verification & testing — `./verification-testing.md`
> - Troubleshooting — `./troubleshooting.md`
> - Shared baseline — `docs/playbooks/_shared/powershell-baseline.md`
>
> **Important regulatory framing.** Nothing in this playbook *guarantees* regulatory compliance. The cmdlets, scripts, and patterns below *support* control objectives required by GLBA §501(b), SEC Regulation S-P (May 2024 amendments), FINRA Rules 4511, 3110, and Regulatory Notice 25-07 (March 2025), SOX §404, OCC Bulletin 2011-12, Federal Reserve SR 11-7, and CCPA §1798.100. Implementation requires that organizations validate every script against their own change-management, model-risk, supervisory-review, and books-and-records processes before production rollout. The scope-drift detector is a tenant-side correlation built on `CopilotInteraction` and Power Platform record types — there is **no native** `AgentScopeExpansion` audit event. Treat the output as a triage signal, not a control attestation.

!!! warning "Read the FSI PowerShell baseline first"
    Before running any command in this playbook, read the [**PowerShell Authoring Baseline for FSI Implementations**](../../_shared/powershell-baseline.md). It is the canonical source for module version pinning, sovereign-cloud (GCC / GCC High / DoD) endpoints, mutation safety (`-WhatIf` / `SupportsShouldProcess`), Dataverse compatibility, and SHA-256 evidence emission. Snippets below may show abbreviated patterns; the baseline is authoritative when the two diverge.

---

## 0. Wrong-shell trap (READ FIRST)

Control 1.14 spans **five** PowerShell surfaces. Choosing the wrong one (or invoking the right one without sovereign-cloud parameters) produces silent false-clean evidence — empty inventories, missed connector references, missing Access Reviews — that will not survive supervisory testing.

| Surface | Connect cmdlet | Module(s) | What it covers in 1.14 |
|---|---|---|---|
| **Power Platform Admin** | `Add-PowerAppsAccount` | `Microsoft.PowerApps.Administration.PowerShell`, `Microsoft.PowerApps.PowerShell` | Environments, DLP policies, environment-level connector & connection enumeration |
| **Dataverse Web API** | OAuth bearer token via `Get-AzAccessToken` or MSAL | `Az.Accounts` (token broker only) | Copilot Studio bot definitions (`bot`, `botcomponent`, `connectionreference`, `msdyn_aimodel`, `msdyn_knowledgesource`) — the only authoritative agent surface |
| **Microsoft Graph** | `Connect-MgGraph` | `Microsoft.Graph.Authentication`, `Microsoft.Graph.Identity.Governance`, `Microsoft.Graph.Identity.DirectoryManagement` | Agent service principals (Entra Agent ID), Access Reviews, role-assignment evidence |
| **Security & Compliance (IPPS)** | `Connect-IPPSSession` | `ExchangeOnlineManagement` v3.5+ | Unified Audit Log search (`Search-UnifiedAuditLog`) for scope-drift detection; DLP-for-Copilot rule attribution |
| **SharePoint Online** | `Connect-SPOService` / `Connect-PnPOnline` | `Microsoft.Online.SharePoint.PowerShell`, `PnP.PowerShell` v2+ | RCD allow-list reconciliation, site-level data-access governance reports (Control 4.6 join) |

> **There is no separate "Copilot Studio Admin" PowerShell module.** Copilot Studio bot metadata lives in the Dataverse environment that backs the agent. You enumerate it via the Dataverse Web API, authenticated with a Power Platform-scoped bearer token. The community `Microsoft.PowerPlatform.Cds.Client` and Microsoft.Xrm.* assemblies are .NET Framework-only and **do not** load in PowerShell 7 — for PowerShell 7 use `Invoke-RestMethod` against `https://<orgname>.api.crm.dynamics.com/api/data/v9.2/`.

> **There is no `AgentScopeExpansion` operation in the M365 audit schema.** Authors who code against that operation name produce empty result sets and false-clean evidence. The detector in §11 instead correlates `CopilotInteraction`, `BotsRuntimeService`, `MicrosoftFlow`, `PowerAppsPlan`, and `AzureActiveDirectory` record types against the inventory baseline.

### 0.1 Friendly-name vs canonical connector ID — the single most common authoring defect

Power Platform connectors have **two** names and they are not interchangeable in scripts:

| Friendly display name | Canonical connector ID |
|---|---|
| SharePoint | `shared_sharepointonline` |
| Office 365 Users | `shared_office365users` |
| Office 365 Outlook | `shared_office365` |
| OneDrive for Business | `shared_onedriveforbusiness` |
| Microsoft Teams | `shared_teams` |
| Microsoft Dataverse | `shared_commondataserviceforapps` |
| HTTP | `shared_http` |
| HTTP with Microsoft Entra ID | `shared_webcontents` |
| Azure Blob Storage | `shared_azureblob` |
| SQL Server | `shared_sql` |
| Custom connectors | `shared_<unique-name>` (per environment) |

**Authoring rule:** every comparison of a connector reference to a DLP classification must use the canonical ID. Friendly-name comparisons are **localised**, **not unique**, and **change between releases** — they will silently miss matches in non-English tenants, in tenants with two connectors that share a display string, and after Microsoft renames a connector. Every `-eq` / `-in` filter in §9 keys on `connectorid`, never on `displayname`.

### 0.2 PowerShell edition guard

This playbook standardises on **PowerShell 7.4 LTS**. The Power Platform admin modules ship Desktop-only cmdlets (PowerShell 5.1) for some legacy surfaces, but every cmdlet referenced in this playbook is REST-based and runs cleanly on PowerShell 7. PnP.PowerShell v2+ is **PowerShell 7 only**. Standardising on a single edition removes a class of cross-edition serialisation bugs (especially `ConvertTo-Json -Depth` differences) that have historically corrupted evidence packs.

```powershell
#Requires -Version 7.4
#Requires -PSEdition Core

if ($PSVersionTable.PSEdition -ne 'Core') {
    throw "Control 1.14 automation targets PowerShell 7.4+ (Core). Detected: $($PSVersionTable.PSEdition) $($PSVersionTable.PSVersion)."
}
if ($PSVersionTable.PSVersion -lt [version]'7.4.0') {
    throw "PowerShell 7.4.0 or later required. Detected: $($PSVersionTable.PSVersion)."
}
```

---

## 1. Module install and version pinning

Every module must be pinned to a CAB-approved version. The list below is the minimum surface for Control 1.14; record exact versions in your change ticket.

```powershell
#Requires -Version 7.4
#Requires -PSEdition Core

$modules = @(
    @{ Name = 'Microsoft.PowerApps.Administration.PowerShell'; RequiredVersion = '2.0.198' }
    @{ Name = 'Microsoft.PowerApps.PowerShell';                RequiredVersion = '1.0.34'  }
    @{ Name = 'Microsoft.Graph.Authentication';                RequiredVersion = '2.19.0'  }
    @{ Name = 'Microsoft.Graph.Identity.Governance';           RequiredVersion = '2.19.0'  }
    @{ Name = 'Microsoft.Graph.Identity.DirectoryManagement';  RequiredVersion = '2.19.0'  }
    @{ Name = 'Microsoft.Graph.Applications';                  RequiredVersion = '2.19.0'  }
    @{ Name = 'Microsoft.Graph.Users';                         RequiredVersion = '2.19.0'  }
    @{ Name = 'ExchangeOnlineManagement';                      RequiredVersion = '3.5.0'   }
    @{ Name = 'PnP.PowerShell';                                RequiredVersion = '2.4.0'   }
    @{ Name = 'Microsoft.Online.SharePoint.PowerShell';        RequiredVersion = '16.0.25513.12000' }
    @{ Name = 'Az.Accounts';                                   RequiredVersion = '2.15.0'  }
    # Optional — only when forwarding scope-drift findings to Sentinel
    @{ Name = 'Az.OperationalInsights';                        RequiredVersion = '3.2.0'   }
    @{ Name = 'Az.SecurityInsights';                           RequiredVersion = '3.0.0'   }
)

foreach ($m in $modules) {
    if (-not (Get-Module -ListAvailable -Name $m.Name |
              Where-Object Version -EQ $m.RequiredVersion)) {
        Install-Module -Name $m.Name `
                       -RequiredVersion $m.RequiredVersion `
                       -Repository PSGallery `
                       -Scope CurrentUser `
                       -AllowClobber `
                       -AcceptLicense
    }
    Import-Module -Name $m.Name -RequiredVersion $m.RequiredVersion -Force
}
```

**Substitute the versions above for whatever your CAB has approved.** Treat `Install-Module ... -Force` without `-RequiredVersion` as an unacceptable shortcut in regulated tenants — it breaks reproducibility and will fail SOX §404 and OCC 2023-17 evidence requirements.

---

## 2. Pre-flight: `Initialize-Agt114Session` bootstrap

Every Control 1.14 script begins from the same bootstrap: edition pinned, modules pinned, sovereign endpoints resolved, transcript started, IPPS + Graph + Power Apps + Dataverse + SharePoint connections opened, role and licence checks performed. Bundle them into one helper so individual scripts do not drift.

Save as `Initialize-Agt114Session.ps1`:

```powershell
#Requires -Version 7.4
#Requires -PSEdition Core

<#
.SYNOPSIS
    Bootstraps a Control 1.14 admin session across Power Platform, Dataverse,
    Microsoft Graph, IPPS, and SharePoint Online in the correct sovereign cloud.
.PARAMETER AdminUpn
    UPN of the admin executing the run (used for Graph + IPPS connection and audit attribution).
.PARAMETER Cloud
    One of: Commercial, GCC, GCCHigh, DoD.
.PARAMETER EvidenceRoot
    Absolute path to the evidence directory.
.PARAMETER RequiredRoles
    Entra role display names; operator must hold at least one. Defaults to least-privilege set for 1.14.
.PARAMETER RequiredSkuPartNumbers
    Tenant SKUs that must be present (E5 Compliance for DSPM-for-AI and DLP-for-Copilot;
    Entra ID P2 for Access Reviews). Verified via Get-MgSubscribedSku.
.PARAMETER SharePointAdminUrl
    Tenant SharePoint admin URL, e.g. https://contoso-admin.sharepoint.com (or .sharepoint.us for sovereign).
#>
function Initialize-Agt114Session {
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact = 'Medium')]
    param(
        [Parameter(Mandatory)] [string] $AdminUpn,
        [Parameter(Mandatory)] [ValidateSet('Commercial','GCC','GCCHigh','DoD')] [string] $Cloud,
        [Parameter(Mandatory)] [string] $EvidenceRoot,
        [Parameter(Mandatory)] [string] $SharePointAdminUrl,
        [string[]] $RequiredRoles = @(
            'Power Platform Administrator',
            'Compliance Administrator',
            'Compliance Data Administrator',
            'Identity Governance Administrator'
        ),
        [string[]] $RequiredSkuPartNumbers = @('SPE_E5','EMSPREMIUM')
    )

    $ErrorActionPreference = 'Stop'

    # 1. Resolve sovereign endpoints (full matrix in §13).
    $endpoints = switch ($Cloud) {
        'Commercial' { @{
            PowerAppsEndpoint = 'prod'
            GraphEnvironment  = 'Global'
            ExoEnvironment    = 'O365Default'
            IPPSConnectionUri = $null
            IPPSAuthorityUri  = $null
            SpoRegion         = 'Default'
            AzEnvironment     = 'AzureCloud'
            DataverseSuffix   = 'crm.dynamics.com'
        } }
        'GCC' { @{
            PowerAppsEndpoint = 'usgov'
            GraphEnvironment  = 'USGov'
            ExoEnvironment    = 'O365USGovGCCHigh'   # GCC mailflow uses commercial; IPPS uses commercial endpoints
            IPPSConnectionUri = $null
            IPPSAuthorityUri  = $null
            SpoRegion         = 'ITAR'
            AzEnvironment     = 'AzureCloud'
            DataverseSuffix   = 'crm9.dynamics.com'
        } }
        'GCCHigh' { @{
            PowerAppsEndpoint = 'usgovhigh'
            GraphEnvironment  = 'USGov'
            ExoEnvironment    = 'O365USGovGCCHigh'
            IPPSConnectionUri = 'https://ps.compliance.protection.office365.us/powershell-liveid/'
            IPPSAuthorityUri  = 'https://login.microsoftonline.us/organizations'
            SpoRegion         = 'ITAR'
            AzEnvironment     = 'AzureUSGovernment'
            DataverseSuffix   = 'crm.microsoftdynamics.us'
        } }
        'DoD' { @{
            PowerAppsEndpoint = 'dod'
            GraphEnvironment  = 'USGovDoD'
            ExoEnvironment    = 'O365USGovDoD'
            IPPSConnectionUri = 'https://l5.ps.compliance.protection.office365.us/powershell-liveid/'
            IPPSAuthorityUri  = 'https://login.microsoftonline.us/organizations'
            SpoRegion         = 'ITAR'
            AzEnvironment     = 'AzureUSGovernment'
            DataverseSuffix   = 'crm.high.dynamics365.us'
        } }
    }

    # 2. Evidence root + transcript.
    if (-not (Test-Path $EvidenceRoot)) {
        New-Item -ItemType Directory -Path $EvidenceRoot -Force | Out-Null
    }
    $stamp        = Get-Date -Format 'yyyyMMdd-HHmmss'
    $runId        = [guid]::NewGuid().ToString()
    $transcript   = Join-Path $EvidenceRoot "agt114-$stamp.transcript.log"

    if ($PSCmdlet.ShouldProcess($transcript, 'Start-Transcript')) {
        Start-Transcript -Path $transcript -IncludeInvocationHeader | Out-Null
    }

    Write-Information "Run $runId — Cloud=$Cloud — Evidence=$EvidenceRoot" -InformationAction Continue

    # 3. Power Apps (sovereign-aware).
    if ($PSCmdlet.ShouldProcess("Power Apps ($Cloud)", 'Add-PowerAppsAccount')) {
        Add-PowerAppsAccount -Endpoint $endpoints.PowerAppsEndpoint
    }

    # 4. Microsoft Graph (sovereign-aware).
    if ($PSCmdlet.ShouldProcess("Graph ($Cloud)", 'Connect-MgGraph')) {
        Connect-MgGraph `
            -Environment $endpoints.GraphEnvironment `
            -Scopes @(
                'Directory.Read.All',
                'AccessReview.Read.All',
                'Application.Read.All',
                'AuditLog.Read.All',
                'RoleManagement.Read.Directory'
            ) `
            -NoWelcome
    }

    # 5. IPPS (sovereign-aware).
    $ippsParams = @{ UserPrincipalName = $AdminUpn; ShowBanner = $false }
    if ($endpoints.IPPSConnectionUri) { $ippsParams.ConnectionUri                  = $endpoints.IPPSConnectionUri }
    if ($endpoints.IPPSAuthorityUri)  { $ippsParams.AzureADAuthorizationEndpointUri = $endpoints.IPPSAuthorityUri }
    if ($PSCmdlet.ShouldProcess("IPPS ($Cloud)", 'Connect-IPPSSession')) {
        Connect-IPPSSession @ippsParams
    }

    # 6. SharePoint Online admin (sovereign-aware via SpoRegion).
    if ($PSCmdlet.ShouldProcess($SharePointAdminUrl, 'Connect-SPOService')) {
        $spoParams = @{ Url = $SharePointAdminUrl }
        if ($endpoints.SpoRegion -ne 'Default') { $spoParams.Region = $endpoints.SpoRegion }
        Connect-SPOService @spoParams
    }

    # 7. Az (for Dataverse bearer-token brokering and optional Sentinel forwarding).
    if ($PSCmdlet.ShouldProcess("Az ($Cloud)", 'Connect-AzAccount')) {
        Connect-AzAccount -Environment $endpoints.AzEnvironment -WarningAction SilentlyContinue | Out-Null
    }

    # 8. Role check (Graph).
    $me = Get-MgUser -UserId $AdminUpn -Property Id, DisplayName, UserPrincipalName
    $assignments = Get-MgRoleManagementDirectoryRoleAssignment `
        -Filter "principalId eq '$($me.Id)'" -All
    $roleDefs = $assignments | ForEach-Object {
        Get-MgRoleManagementDirectoryRoleDefinition -UnifiedRoleDefinitionId $_.RoleDefinitionId
    }
    $heldRoleNames = $roleDefs.DisplayName | Sort-Object -Unique
    $missing       = $RequiredRoles | Where-Object { $_ -notin $heldRoleNames }
    if ($missing.Count -eq $RequiredRoles.Count) {
        throw "Operator $AdminUpn holds none of the required roles ($($RequiredRoles -join ', ')). Held: $($heldRoleNames -join ', ')."
    }

    # 9. Licence check.
    $skus     = Get-MgSubscribedSku -All
    $skuParts = $skus.SkuPartNumber
    $missingSku = $RequiredSkuPartNumbers | Where-Object { $_ -notin $skuParts }
    if ($missingSku) {
        Write-Warning "Tenant is missing SKU part numbers: $($missingSku -join ', '). DSPM-for-AI and Access Review code paths may be skipped or fail."
    }

    # 10. Module-version evidence.
    $moduleEvidence = Get-Module -Name 'Microsoft.PowerApps.*','Microsoft.Graph.*','ExchangeOnlineManagement','PnP.PowerShell','Microsoft.Online.SharePoint.PowerShell','Az.*' |
        Select-Object Name, Version, Path, RootModule

    # 11. Return session object.
    [PSCustomObject]@{
        RunId           = $runId
        Stamp           = $stamp
        Cloud           = $Cloud
        Endpoints       = $endpoints
        AdminUpn        = $AdminUpn
        TenantId        = (Get-MgContext).TenantId
        EvidenceRoot    = $EvidenceRoot
        Transcript      = $transcript
        ModuleVersions  = $moduleEvidence
        TenantSkus      = $skuParts
        HeldRoles       = $heldRoleNames
    }
}
```

**Always invoke first with `-WhatIf`** to confirm sovereign endpoints and transcript path before establishing connections in production.

---

## 3. License gating (E5 Compliance + Entra ID P2)

Several scripts in this playbook depend on licences that are **not** universally present. Invoking them without the licence yields `Forbidden` or empty result sets that look like clean inventories. Gate before invoking.

```powershell
function Test-Agt114LicenceGate {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] $Session,
        [Parameter(Mandatory)] [ValidateSet('DspmForAi','AccessReviews','DlpForCopilot','SpoAdvancedManagement')]
                                [string] $Capability
    )

    $required = @{
        DspmForAi             = @('SPE_E5','INFORMATION_PROTECTION_COMPLIANCE')   # E5 or E5 Compliance add-on
        DlpForCopilot         = @('SPE_E5','INFORMATION_PROTECTION_COMPLIANCE')
        AccessReviews         = @('AAD_PREMIUM_P2','EMSPREMIUM','SPE_E5')
        SpoAdvancedManagement = @('Microsoft_SharePoint_Premium','SPE_E5')        # SAM is bundled with E5 + Copilot
    }

    $needed = $required[$Capability]
    $hit    = $needed | Where-Object { $_ -in $Session.TenantSkus }
    if (-not $hit) {
        Write-Warning "Capability '$Capability' requires one of [$($needed -join ', ')]; tenant has none. Skipping dependent code path."
        return $false
    }
    Write-Information "Capability '$Capability' gated on SKU '$($hit[0])' — proceeding." -InformationAction Continue
    return $true
}
```

Use as:

```powershell
if (Test-Agt114LicenceGate -Session $s -Capability 'AccessReviews') {
    Get-Agt114AgentAccessReviews -Session $s
}
```

---

## 4. Enumerate Power Platform environments

Environments are the outer loop for every inventory script. Use `Get-AdminPowerAppEnvironment` and project both the environment ID and the Dataverse organisation URL — the latter is what you pass to the Dataverse Web API in §6.

```powershell
function Get-Agt114Environments {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] $Session,
        [switch] $IncludeDefault,
        [switch] $IncludeTrial
    )

    $envs = Get-AdminPowerAppEnvironment | Where-Object {
        ($IncludeDefault -or $_.EnvironmentType -ne 'Default') -and
        ($IncludeTrial   -or $_.EnvironmentType -ne 'Trial')
    }

    $envs | ForEach-Object {
        [PSCustomObject]@{
            EnvironmentId       = $_.EnvironmentName
            DisplayName         = $_.DisplayName
            EnvironmentType     = $_.EnvironmentType
            Region              = $_.Location
            HasDataverse        = ($_.CommonDataServiceDatabaseProvisioningState -eq 'Succeeded')
            DataverseUrl        = $_.Internal.properties.linkedEnvironmentMetadata.instanceApiUrl
            CreatedTime         = $_.CreatedTime
            CreatedBy           = $_.CreatedBy.userPrincipalName
            SecurityGroupId     = $_.Internal.properties.linkedEnvironmentMetadata.securityGroupId
            ProtectionStatus    = $_.Internal.properties.protectionStatus.keyManagedBy
        }
    }
}
```

If `HasDataverse` is `$false`, **skip the agent enumeration in §6** for that environment — Copilot Studio agents only exist in Dataverse-backed environments. Power Apps without Dataverse cannot host a Copilot Studio bot.

---

## 5. Dataverse Web API token broker

The Dataverse Web API requires a bearer token with audience equal to the Dataverse organisation URL. In PowerShell 7 (where the .NET Framework `Microsoft.Xrm.*` SDK does not load), use `Get-AzAccessToken` to broker the token, then make REST calls with `Invoke-RestMethod`.

```powershell
function Get-Agt114DataverseToken {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string] $DataverseUrl   # e.g. https://contoso.crm.dynamics.com
    )
    if (-not $DataverseUrl) { throw "DataverseUrl is required." }
    $audience = ($DataverseUrl.TrimEnd('/'))
    $token = Get-AzAccessToken -ResourceUrl $audience -ErrorAction Stop
    [PSCustomObject]@{
        Audience    = $audience
        AccessToken = $token.Token
        ExpiresOn   = $token.ExpiresOn
        Header      = @{
            Authorization        = "Bearer $($token.Token)"
            Accept               = 'application/json'
            'OData-MaxVersion'   = '4.0'
            'OData-Version'      = '4.0'
            'Content-Type'       = 'application/json; charset=utf-8'
            Prefer               = 'odata.include-annotations="*"'
        }
    }
}

function Invoke-Agt114DataverseQuery {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string] $DataverseUrl,
        [Parameter(Mandatory)] [string] $RelativePath  # e.g. /api/data/v9.2/bots?$select=botid,name
    )
    $tok = Get-Agt114DataverseToken -DataverseUrl $DataverseUrl
    $uri = "$($DataverseUrl.TrimEnd('/'))$RelativePath"
    $all = @()
    do {
        $resp = Invoke-RestMethod -Method GET -Uri $uri -Headers $tok.Header
        if ($resp.value) { $all += $resp.value } else { $all += $resp }
        $uri = $resp.'@odata.nextLink'
    } while ($uri)
    return $all
}
```

The paging loop on `@odata.nextLink` is **mandatory**. Dataverse returns 5,000 rows per page by default; large environments will silently truncate at the first page if the loop is omitted, producing false-clean inventories.

---

## 6. Enumerate Copilot Studio agents (Dataverse `bot` table)

Copilot Studio agents are Dataverse `bot` rows. Each bot has zero or more `botcomponent` rows (topics, knowledge sources, plugins, dialogs, settings) and zero or more `connectionreference` rows that bind to Power Platform connections.

```powershell
function Get-Agt114CopilotStudioAgents {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] $Session,
        [Parameter(Mandatory)] [string] $EnvironmentId,
        [Parameter(Mandatory)] [string] $DataverseUrl
    )

    # bot table — top-level agent definition
    $select  = '$select=botid,name,configuration,authenticationmode,iscopilot,_owner_value,createdon,modifiedon,statecode,solutionid,schemaname'
    $bots    = Invoke-Agt114DataverseQuery -DataverseUrl $DataverseUrl `
                  -RelativePath "/api/data/v9.2/bots?$select"

    foreach ($b in $bots) {
        # Components (topics, knowledge, plugins, settings)
        $compFilter = "$('$filter')=_parentbotid_value eq $($b.botid)"
        $compSelect = '$select=botcomponentid,name,componenttype,content,schemaname,_connectionreferenceid_value'
        $components = Invoke-Agt114DataverseQuery -DataverseUrl $DataverseUrl `
                        -RelativePath "/api/data/v9.2/botcomponents?$compFilter&$compSelect"

        [PSCustomObject]@{
            EnvironmentId   = $EnvironmentId
            BotId           = $b.botid
            BotName         = $b.name
            SchemaName      = $b.schemaname
            IsCopilot       = [bool]$b.iscopilot
            AuthMode        = $b.authenticationmode
            State           = if ($b.statecode -eq 0) { 'Active' } else { 'Inactive' }
            OwnerId         = $b.'_owner_value'
            CreatedOn       = $b.createdon
            ModifiedOn      = $b.modifiedon
            ComponentCount  = $components.Count
            Components      = $components
        }
    }
}
```

The `componenttype` column is the discriminator that drives the grounding-surface enumeration in §7. Microsoft documents the enumeration values in the Microsoft Copilot Studio component reference. Common values seen in 1.14:

| `componenttype` | Surface category |
|---|---|
| `0` | Topic |
| `9` | Knowledge source (SharePoint, file, public web, enterprise web, Dataverse) |
| `10` | Action / plugin (Power Automate flow, connector action, custom code) |
| `12` | Custom GPT / declarative agent payload |
| `15` | Settings (file upload, image upload, public web grounding flag, escalation) |

> **Verify the enumeration values against Microsoft Learn before each release** — they have shifted between Copilot Studio GA waves and may shift again.

---

## 7. Enumerate grounding surfaces per agent

Once you have the `botcomponent` rows, parse each component's `content` (JSON) into a normalised `GroundingSurface` record. A single agent typically contributes 5–50 grounding-surface rows.

```powershell
function Get-Agt114GroundingSurfaces {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] $Agent  # output of Get-Agt114CopilotStudioAgents
    )

    $surfaces = New-Object System.Collections.Generic.List[object]

    foreach ($c in $Agent.Components) {
        $payload = $null
        if ($c.content) {
            try { $payload = $c.content | ConvertFrom-Json -Depth 50 -ErrorAction Stop } catch { $payload = $null }
        }

        switch ([int]$c.componenttype) {

            9 {  # Knowledge source
                $kind     = $payload.kind        # e.g. 'SharePoint','PublicWebsite','EnterpriseWebsite','File','Dataverse','Graph'
                $sources  = @()
                if ($payload.sharepointSites) { $sources += $payload.sharepointSites.url }
                if ($payload.urls)            { $sources += $payload.urls }
                if ($payload.fileNames)       { $sources += $payload.fileNames }
                if ($payload.dataverseTables) { $sources += $payload.dataverseTables.name }
                if (-not $sources) { $sources = @($payload.url, $payload.name | Where-Object { $_ }) }

                foreach ($u in $sources) {
                    $surfaces.Add([PSCustomObject]@{
                        AgentId        = $Agent.BotId
                        AgentName      = $Agent.BotName
                        SurfaceClass   = 'KnowledgeSource'
                        SurfaceKind    = $kind
                        SurfaceId      = ($u | Out-String).Trim()
                        ConnectorId    = $null
                        ConnectionId   = $null
                        ComponentId    = $c.botcomponentid
                        Raw            = $payload
                    })
                }
            }

            10 { # Action / plugin / connector binding
                $connectorId  = $payload.connectorId       # canonical, e.g. 'shared_sharepointonline'
                $connectionId = $c.'_connectionreferenceid_value'
                $surfaces.Add([PSCustomObject]@{
                    AgentId       = $Agent.BotId
                    AgentName     = $Agent.BotName
                    SurfaceClass  = 'ConnectorAction'
                    SurfaceKind   = $payload.kind          # 'Flow','ConnectorAction','Plugin','ApiPlugin'
                    SurfaceId     = ($payload.operationId, $payload.flowId, $payload.pluginId | Where-Object { $_ } | Select-Object -First 1)
                    ConnectorId   = $connectorId
                    ConnectionId  = $connectionId
                    ComponentId   = $c.botcomponentid
                    Raw           = $payload
                })
            }

            12 { # Declarative agent / custom GPT / API plugin manifest
                $surfaces.Add([PSCustomObject]@{
                    AgentId       = $Agent.BotId
                    AgentName     = $Agent.BotName
                    SurfaceClass  = 'DeclarativeAgent'
                    SurfaceKind   = $payload.type           # 'apiPlugin','copilotExtension','declarativeAgent'
                    SurfaceId     = $payload.id
                    ConnectorId   = $null
                    ConnectionId  = $null
                    ComponentId   = $c.botcomponentid
                    Raw           = $payload
                })
            }

            15 { # Settings (upload toggles, public web flag, escalation)
                foreach ($k in 'fileUploadEnabled','imageUploadEnabled','publicWebGroundingEnabled','enterpriseWebGroundingEnabled','codeInterpreterEnabled') {
                    if ($null -ne $payload.$k) {
                        $surfaces.Add([PSCustomObject]@{
                            AgentId       = $Agent.BotId
                            AgentName     = $Agent.BotName
                            SurfaceClass  = 'Setting'
                            SurfaceKind   = $k
                            SurfaceId     = ([string]$payload.$k)
                            ConnectorId   = $null
                            ConnectionId  = $null
                            ComponentId   = $c.botcomponentid
                            Raw           = $payload
                        })
                    }
                }
            }
        }
    }

    # Connection references (resolved separately to attach friendly metadata)
    $connRefIds = $Agent.Components | Where-Object { $_.'_connectionreferenceid_value' } |
                  Select-Object -Expand '_connectionreferenceid_value' -Unique
    foreach ($refId in $connRefIds) {
        # Caller is expected to have an environment-level connection-reference cache;
        # see Get-Agt114ConnectionReferenceMap below.
    }

    return $surfaces
}
```

### 7.1 Connection-reference cache (canonical connector ID resolution)

The `connectorid` value on a botcomponent's content payload **may** be missing or stale; the authoritative source is the `connectionreference` Dataverse row. Build the map once per environment.

```powershell
function Get-Agt114ConnectionReferenceMap {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string] $DataverseUrl
    )

    $sel  = '$select=connectionreferenceid,connectionreferencelogicalname,connectionreferencedisplayname,connectorid,connectionid,iscustomizable'
    $rows = Invoke-Agt114DataverseQuery -DataverseUrl $DataverseUrl `
              -RelativePath "/api/data/v9.2/connectionreferences?$sel"

    $map = @{}
    foreach ($r in $rows) {
        $map[$r.connectionreferenceid.ToLower()] = [PSCustomObject]@{
            LogicalName  = $r.connectionreferencelogicalname
            DisplayName  = $r.connectionreferencedisplayname
            ConnectorId  = $r.connectorid                        # canonical, e.g. 'shared_sharepointonline'
            ConnectionId = $r.connectionid
        }
    }
    return $map
}
```

Use the map to backfill the canonical `ConnectorId` on the surface rows where the component payload was missing it:

```powershell
function Resolve-Agt114SurfaceConnectors {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [object[]] $Surfaces,
        [Parameter(Mandatory)] [hashtable] $ConnectionRefMap
    )
    foreach ($s in $Surfaces) {
        if ($s.ConnectorId) { continue }
        if ($s.ConnectionId -and $ConnectionRefMap.ContainsKey($s.ConnectionId.ToLower())) {
            $s.ConnectorId = $ConnectionRefMap[$s.ConnectionId.ToLower()].ConnectorId
        }
    }
    return $Surfaces
}
```

---

## 8. Build a dedupe-keyed inventory (no cartesian)

The historic version of this playbook iterated `apps × connections` and emitted a row per pair, producing a cartesian explosion. The correct primary key for a 1.14 inventory row is:

```
(EnvironmentId, AgentId, SurfaceClass, ConnectorId | SurfaceId, ComponentId)
```

Hash the key, dedupe, and project a single row per logical surface.

```powershell
function Build-Agt114Inventory {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] $Session,
        [string[]] $EnvironmentIds,        # null = all
        [switch]   $IncludeInactive
    )

    $inv = New-Object System.Collections.Generic.List[object]
    $envs = Get-Agt114Environments -Session $Session
    if ($EnvironmentIds) { $envs = $envs | Where-Object EnvironmentId -in $EnvironmentIds }

    foreach ($e in $envs) {
        if (-not $e.HasDataverse)  { continue }
        if (-not $e.DataverseUrl)  { continue }

        $connMap = Get-Agt114ConnectionReferenceMap -DataverseUrl $e.DataverseUrl
        $agents  = Get-Agt114CopilotStudioAgents -Session $Session `
                                                 -EnvironmentId $e.EnvironmentId `
                                                 -DataverseUrl $e.DataverseUrl
        if (-not $IncludeInactive) { $agents = $agents | Where-Object State -EQ 'Active' }

        foreach ($a in $agents) {
            $surfaces = Get-Agt114GroundingSurfaces -Agent $a
            $surfaces = Resolve-Agt114SurfaceConnectors -Surfaces $surfaces -ConnectionRefMap $connMap

            foreach ($s in $surfaces) {
                $inv.Add([PSCustomObject]@{
                    EnvironmentId   = $e.EnvironmentId
                    EnvironmentName = $e.DisplayName
                    AgentId         = $a.BotId
                    AgentName       = $a.BotName
                    AgentState      = $a.State
                    SurfaceClass    = $s.SurfaceClass
                    SurfaceKind     = $s.SurfaceKind
                    SurfaceId       = $s.SurfaceId
                    ConnectorId     = $s.ConnectorId
                    ConnectionId    = $s.ConnectionId
                    ComponentId     = $s.ComponentId
                })
            }
        }
    }

    # Dedupe: hash the natural key and keep one row per key.
    $deduped = $inv | Group-Object -Property `
        EnvironmentId, AgentId, SurfaceClass, ConnectorId, SurfaceId, ComponentId |
        ForEach-Object { $_.Group | Select-Object -First 1 }

    return $deduped
}
```

The grouping ensures no cartesian explosion: a single agent with five connections to SharePoint and three knowledge sources resolves to exactly eight rows, not fifteen. Verify with:

```powershell
$inv = Build-Agt114Inventory -Session $s
($inv | Group-Object EnvironmentId, AgentId, ConnectorId, SurfaceId, ComponentId |
        Where-Object Count -GT 1).Count   # must be 0
```

---

## 9. Power Platform DLP join — flag agent use of Non-Business / Blocked connectors

Power Platform DLP classifies every connector in an environment into one of three groups: **Business**, **Non-Business**, **Blocked**. Combining a Business connector with a Non-Business connector in a single Power Automate flow or agent is what DLP prevents. For 1.14 we additionally want to flag any agent that **uses** a connector classified Non-Business or Blocked at all — that signals scope creep regardless of the cross-group rule.

```powershell
function Get-Agt114DlpJoin {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] $Session,
        [Parameter(Mandatory)] [object[]] $Inventory   # output of Build-Agt114Inventory
    )

    $policies = Get-DlpPolicy -ErrorAction Stop
    if (-not $policies) { Write-Warning "No DLP policies returned. Verify Power Platform DLP is configured."; return @() }

    # Build (environment, connectorId) -> classification map.
    # Classification values are 'Confidential' (Business), 'General' (Non-Business), 'Blocked'.
    $map = @{}
    foreach ($p in $policies) {
        $envs = @()
        if ($p.Environments) { $envs += $p.Environments.name }
        if ($p.EnvironmentType -eq 'AllEnvironments') { $envs = '*' }

        foreach ($targetEnv in $envs) {
            foreach ($cg in $p.ConnectorGroups) {
                foreach ($cn in $cg.Connectors) {
                    $key = "$targetEnv|$($cn.id)"
                    $map[$key] = [PSCustomObject]@{
                        PolicyName     = $p.DisplayName
                        Classification = $cg.classification     # 'Confidential' | 'General' | 'Blocked'
                        ConnectorId    = $cn.id                 # canonical, e.g. 'shared_sharepointonline'
                        ConnectorName  = $cn.name               # friendly — for reporting only
                    }
                }
            }
        }
    }

    foreach ($row in $Inventory | Where-Object ConnectorId) {
        $key  = "$($row.EnvironmentId)|$($row.ConnectorId)"
        $star = "*|$($row.ConnectorId)"
        $hit  = $map[$key]; if (-not $hit) { $hit = $map[$star] }

        if (-not $hit) {
            [PSCustomObject]@{
                AgentId         = $row.AgentId
                AgentName       = $row.AgentName
                EnvironmentId   = $row.EnvironmentId
                ConnectorId     = $row.ConnectorId
                Classification  = 'Unclassified'
                Severity        = 'High'
                Finding         = "Connector $($row.ConnectorId) is not covered by any DLP policy in environment $($row.EnvironmentId). Default policy posture must be confirmed."
            }
            continue
        }

        $sev = switch ($hit.Classification) {
            'Confidential' { 'Info' }      # Business — expected
            'General'      { 'Medium' }    # Non-Business — flag
            'Blocked'      { 'Critical' }  # Blocked — investigate immediately
            default        { 'Medium' }
        }

        [PSCustomObject]@{
            AgentId         = $row.AgentId
            AgentName       = $row.AgentName
            EnvironmentId   = $row.EnvironmentId
            ConnectorId     = $row.ConnectorId
            ConnectorName   = $hit.ConnectorName
            PolicyName      = $hit.PolicyName
            Classification  = $hit.Classification
            Severity        = $sev
            Finding         = "Agent uses connector classified $($hit.Classification) under DLP policy '$($hit.PolicyName)'."
        }
    }
}
```

**All comparisons key on canonical `ConnectorId`** (`shared_sharepointonline`, `shared_office365`, `shared_http`, etc.). The `ConnectorName` field is carried through for human-readable reporting only. Authoring rule: never write `where { $_.ConnectorName -eq 'SharePoint' }` — write `where { $_.ConnectorId -eq 'shared_sharepointonline' }`.

---

## 10. Entra ID Governance Access Reviews on agent identities

Each agent that authenticates with its own Entra Agent ID has a service principal and (where applicable) an associated managed identity or app registration. Control 1.14 requires Access Reviews on those principals at zone cadence (Zone 1 annual, Zone 2 quarterly, Zone 3 monthly). Enumerate active reviews and reconcile against the agent inventory.

```powershell
function Get-Agt114AgentAccessReviews {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] $Session,
        [Parameter(Mandatory)] [object[]] $Inventory
    )

    if (-not (Test-Agt114LicenceGate -Session $Session -Capability 'AccessReviews')) { return @() }

    # All active access-review definitions
    $defs = Get-MgIdentityGovernanceAccessReviewDefinition -All -Filter "status eq 'InProgress' or status eq 'Initializing'"

    # Resolve service-principal IDs for each unique agent
    $agents = $Inventory | Group-Object AgentId | ForEach-Object { $_.Group | Select-Object -First 1 }
    $spMap  = @{}
    foreach ($a in $agents) {
        # Agent service principal naming convention varies; lookup by displayName begins-with on agent name.
        # Replace with your tenant's lookup convention if you use a different naming scheme.
        $sp = Get-MgServicePrincipal -Filter "startsWith(displayName,'$($a.AgentName -replace ""'"",""''""")')" -Top 5 -ErrorAction SilentlyContinue
        if ($sp) { $spMap[$a.AgentId] = $sp }
    }

    foreach ($a in $agents) {
        $sps      = $spMap[$a.AgentId]
        $matches  = @()
        if ($sps) {
            foreach ($d in $defs) {
                $scopeJson = $d.Scope | ConvertTo-Json -Depth 6 -Compress
                foreach ($sp in $sps) {
                    if ($scopeJson -match $sp.Id) {
                        $matches += [PSCustomObject]@{
                            ReviewId        = $d.Id
                            ReviewName      = $d.DisplayName
                            ReviewerType    = $d.Reviewers[0].Query
                            RecurrenceType  = $d.Settings.Recurrence.Pattern.Type
                            RecurrenceInt   = $d.Settings.Recurrence.Pattern.Interval
                            ServicePrincipal= $sp.DisplayName
                            LastModified    = $d.LastModifiedDateTime
                        }
                    }
                }
            }
        }
        [PSCustomObject]@{
            AgentId               = $a.AgentId
            AgentName             = $a.AgentName
            ServicePrincipalCount = ($sps | Measure-Object).Count
            ActiveReviews         = $matches
            ReviewCount           = $matches.Count
            ComplianceStatus      = if ($matches.Count -ge 1) { 'Covered' } else { 'NoActiveReview' }
        }
    }
}
```

**Caveat.** This function infers the agent → service-principal mapping by display-name prefix. If your tenant uses a different naming convention (for example `cps-<bot-schema-name>` or `agent-<botid>`), substitute that lookup. The mapping should ideally be authoritative in your Control 1.2 agent registry and propagated here as a parameter.

---

## 11. Scope-drift detector (paged Unified Audit Log + inventory baseline)

There is **no** single audit operation called `AgentScopeExpansion`. The detector instead correlates five record types against an inventory baseline. A drift event is any audit record whose target connector / SharePoint URL / Dataverse table / public web URL is **not** in the baseline inventory for the agent that issued the request.

```powershell
function Find-Agt114ScopeDrift {
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact = 'Low')]
    param(
        [Parameter(Mandatory)] $Session,
        [Parameter(Mandatory)] [object[]] $InventoryBaseline,
        [int] $LookbackDays = 7,
        [int] $PageSize     = 5000
    )

    $start = (Get-Date).AddDays(-$LookbackDays).ToUniversalTime()
    $end   = (Get-Date).ToUniversalTime()

    $recordTypes = @(
        'CopilotInteraction',          # Copilot-side prompt + grounding events
        'BotsRuntimeService',           # Copilot Studio runtime
        'MicrosoftFlow',                # Power Automate runs
        'PowerAppsPlan',                # Power Apps and connector activity
        'AzureActiveDirectory'          # SP sign-ins for agent identities
    )

    # Build O(1) lookup of allowed surfaces per agent.
    $allowed = @{}
    foreach ($row in $InventoryBaseline) {
        if (-not $allowed.ContainsKey($row.AgentId)) { $allowed[$row.AgentId] = @{} }
        $key = "$($row.SurfaceClass)|$($row.ConnectorId)|$($row.SurfaceId)"
        $allowed[$row.AgentId][$key] = $true
    }

    # Paged UAL pull — Search-UnifiedAuditLog truncates at 5000 per page; loop on SessionId/SessionCommand.
    $allEvents = New-Object System.Collections.Generic.List[object]
    foreach ($rt in $recordTypes) {
        $sessionId = [guid]::NewGuid().ToString()
        do {
            $page = Search-UnifiedAuditLog `
                       -StartDate $start -EndDate $end `
                       -RecordType $rt `
                       -ResultSize $PageSize `
                       -SessionId $sessionId `
                       -SessionCommand 'ReturnLargeSet'
            if ($page) { $allEvents.AddRange($page) }
        } while ($page -and $page.Count -eq $PageSize)
    }

    Write-Information "$($allEvents.Count) raw audit events pulled across $($recordTypes.Count) record types." -InformationAction Continue

    $drifts = New-Object System.Collections.Generic.List[object]
    foreach ($evt in $allEvents) {
        $data = $evt.AuditData | ConvertFrom-Json -ErrorAction SilentlyContinue
        if (-not $data) { continue }

        # Heuristics — record-type specific extraction
        $agentId   = $data.BotId           ; if (-not $agentId) { $agentId = $data.CopilotAgentId }
        $surface   = $null
        $surfClass = $null
        $connId    = $null

        if ($data.AccessedResources) {
            foreach ($r in $data.AccessedResources) {
                $surface   = $r.Url
                $surfClass = if ($r.Type -match 'sharepoint|onedrive') { 'KnowledgeSource' } else { 'KnowledgeSource' }
            }
        }
        if ($data.ConnectorId)   { $connId = $data.ConnectorId; $surfClass = 'ConnectorAction' }
        if ($data.OperationName -match 'Plugin|Extension') { $surfClass = 'DeclarativeAgent' }

        if (-not $agentId) { continue }
        if (-not $allowed.ContainsKey($agentId)) {
            $drifts.Add([PSCustomObject]@{
                Timestamp     = $evt.CreationDate
                AgentId       = $agentId
                Operation     = $evt.Operations
                Severity      = 'High'
                Finding       = "Audit event from agent $agentId — agent not in inventory baseline."
                Raw           = $evt
            })
            continue
        }

        $key = "$surfClass|$connId|$surface"
        if (-not $allowed[$agentId].ContainsKey($key)) {
            $drifts.Add([PSCustomObject]@{
                Timestamp     = $evt.CreationDate
                AgentId       = $agentId
                SurfaceClass  = $surfClass
                ConnectorId   = $connId
                SurfaceId     = $surface
                Operation     = $evt.Operations
                Severity      = 'Medium'
                Finding       = "Agent $agentId touched surface ($surfClass / $connId / $surface) not in inventory baseline."
                Raw           = $evt
            })
        }
    }

    Write-Information "$($drifts.Count) scope-drift candidates flagged." -InformationAction Continue
    return $drifts
}
```

**Authoring caveats.**

1. The mapping of `AuditData` fields to inventory surfaces is **heuristic** — Microsoft has not committed a stable schema for `AccessedResources` across all record types. Calibrate the field-extraction logic against samples from your own tenant before relying on the output for supervisory evidence.
2. A drift candidate is a **triage signal**, not an incident. Pipe results through your SIEM (Sentinel) for analyst review and the AI incident-response playbook (`docs/playbooks/incident-and-risk/ai-incident-response-playbook.md`).
3. UAL has a documented ingestion latency of up to **24 hours** for some record types. Any "real-time" claim built on top of `Search-UnifiedAuditLog` is overclaim. For lower latency, use Activity Explorer + DSPM-for-AI (separate code path; not exposed via stable PowerShell at the time of writing).

---

## 12. SharePoint Site → RCD reconciliation (Control 4.6 join)

Control 4.6 maintains the Restricted Content Discovery (RCD) exclusion list and the Restricted SharePoint Search (RSS) ≤100-site allowed list. For each SharePoint URL in the 1.14 inventory, verify either (a) the site is on the RCD exclusion list (preferred for high-risk content), or (b) the site is acknowledged in the 4.6 register as out-of-scope for restriction.

```powershell
function Get-Agt114RcdReconciliation {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] $Session,
        [Parameter(Mandatory)] [object[]] $Inventory,
        [string] $Control46RegisterPath  # JSON exported from Control 4.6 portal walkthrough
    )

    if (-not (Test-Agt114LicenceGate -Session $Session -Capability 'SpoAdvancedManagement')) {
        Write-Warning "SharePoint Advanced Management not licensed — skipping RCD reconciliation."
        return @()
    }

    $sharepointSurfaces = $Inventory | Where-Object {
        $_.SurfaceClass -eq 'KnowledgeSource' -and
        $_.SurfaceKind  -eq 'SharePoint'      -and
        $_.SurfaceId    -match 'https?://[^/]+\.sharepoint\.(com|us)'
    }

    # Pull RCD exclusion list via PnP (canonical SPO Advanced Management cmdlet surface).
    $rcdSites = @()
    try {
        $rcdSites = Get-PnPTenantRestrictedSearchAllowedList -ErrorAction Stop
    } catch {
        Write-Warning "Get-PnPTenantRestrictedSearchAllowedList failed: $($_.Exception.Message). Verify PnP.PowerShell v2.4+ and SAM licence."
    }

    $register = @()
    if ($Control46RegisterPath -and (Test-Path $Control46RegisterPath)) {
        $register = Get-Content $Control46RegisterPath | ConvertFrom-Json
    }

    foreach ($s in $sharepointSurfaces) {
        $siteUrl = ([uri]$s.SurfaceId).GetLeftPart([UriPartial]::Authority + [UriPartial]::Path)
        $onRcd   = $rcdSites | Where-Object { $siteUrl -like "$($_.Url)*" }
        $onReg   = $register | Where-Object { $_.SiteUrl -eq $siteUrl }

        $status = switch ($true) {
            { $onRcd } { 'OnRcdAllowedList' }
            { $onReg } { 'AcknowledgedInRegister' }
            default    { 'Unreconciled' }
        }
        [PSCustomObject]@{
            AgentId     = $s.AgentId
            AgentName   = $s.AgentName
            SiteUrl     = $siteUrl
            Status      = $status
            Severity    = if ($status -eq 'Unreconciled') { 'High' } else { 'Info' }
            Finding     = if ($status -eq 'Unreconciled') {
                "SharePoint site grounded by agent $($s.AgentName) is neither on the RCD allowed list nor acknowledged in the Control 4.6 register."
            } else {
                "Site reconciled ($status)."
            }
        }
    }
}
```

The cmdlet name `Get-PnPTenantRestrictedSearchAllowedList` reflects the PnP.PowerShell v2.4 surface; verify the cmdlet name against the PnP changelog before each deployment, as PnP renames cmdlets between minor versions.

---

## 13. Sovereign-cloud reference

Cloud selection is made **once**, in `Initialize-Agt114Session`. Get this wrong and every subsequent function authenticates against the wrong tenant ring, returns empty results, and produces false-clean evidence.

| Cloud | `Add-PowerAppsAccount -Endpoint` | `Connect-MgGraph -Environment` | `Connect-IPPSSession -ConnectionUri` | `Connect-AzAccount -Environment` | Dataverse URL suffix |
|---|---|---|---|---|---|
| **Commercial** | `prod` | `Global` | *(default)* | `AzureCloud` | `crm.dynamics.com` |
| **GCC** | `usgov` | `USGov` | *(default)* | `AzureCloud` | `crm9.dynamics.com` |
| **GCC High** | `usgovhigh` | `USGov` | `https://ps.compliance.protection.office365.us/powershell-liveid/` | `AzureUSGovernment` | `crm.microsoftdynamics.us` |
| **DoD** | `dod` | `USGovDoD` | `https://l5.ps.compliance.protection.office365.us/powershell-liveid/` | `AzureUSGovernment` | `crm.high.dynamics365.us` |

### 13.1 Per-function sovereign variants

| Function | Commercial | GCC | GCC High | DoD |
|---|---|---|---|---|
| `Initialize-Agt114Session` | All endpoints default | `-Endpoint usgov`; Graph `Global` (rolling to `USGov`) | `-Endpoint usgovhigh`; Graph `USGov`; IPPS sovereign URI | `-Endpoint dod`; Graph `USGovDoD`; IPPS DoD URI |
| `Get-Agt114Environments` | No change | No change | No change — but verify SAM licence parity | Verify Copilot Studio availability; was limited preview as of early 2026 |
| `Get-Agt114CopilotStudioAgents` | `crm.dynamics.com` | `crm9.dynamics.com` | `crm.microsoftdynamics.us` | `crm.high.dynamics365.us` |
| `Get-Agt114DlpJoin` | Parity | Parity | Parity | Parity |
| `Get-Agt114AgentAccessReviews` | Parity | Parity | Parity | Parity |
| `Find-Agt114ScopeDrift` | UAL up to 24 h latency | Same | Same | Same |
| `Get-Agt114RcdReconciliation` | SAM GA | SAM GA | **SAM availability limited** — verify; function will return warning + empty if cmdlet absent | **Limited** — confirm SAM availability before relying |
| `Test-Agt114LicenceGate` | All gates apply | DSPM-for-AI rolling — gate may warn-skip | DSPM-for-AI lag — gate may warn-skip | DSPM-for-AI lag — gate may warn-skip |

> **Verify the DoD endpoint URLs before each change window.** The DoD ring is the most volatile of the four sovereign rings; the URLs above were current as of the playbook's last verification date but change without notice.

---

## 14. SHA-256 evidence manifest and JSON export

Every Control 1.14 run emits an evidence pack containing the inventory, DLP join, Access Review report, drift report, RCD reconciliation, transcript, and a `manifest.json` binding them with SHA-256 hashes and run metadata.

```powershell
function Write-Agt114Evidence {
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact = 'Low')]
    param(
        [Parameter(Mandatory)] $Session,
        [Parameter(Mandatory)] [hashtable] $Artifacts,   # @{ inventory = $inv; dlp = $dlpJoin; ... }
        [string] $ChangeRef = 'AGT114-AUTO'
    )

    $dir   = Join-Path $Session.EvidenceRoot "agt114-$($Session.Stamp)"
    if ($PSCmdlet.ShouldProcess($dir, 'Create evidence directory')) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }

    foreach ($name in $Artifacts.Keys) {
        $path = Join-Path $dir "$name.json"
        $Artifacts[$name] | ConvertTo-Json -Depth 20 |
            Set-Content -Path $path -Encoding utf8
    }

    # Manifest with run metadata
    $files = Get-ChildItem $dir -File | ForEach-Object {
        [PSCustomObject]@{
            File         = $_.Name
            SHA256       = (Get-FileHash $_.FullName -Algorithm SHA256).Hash
            Bytes        = $_.Length
            ModifiedUtc  = $_.LastWriteTimeUtc
        }
    }

    $manifest = [PSCustomObject]@{
        ControlId       = '1.14'
        ChangeRef       = $ChangeRef
        RunId           = $Session.RunId
        Timestamp       = $Session.Stamp
        Cloud           = $Session.Cloud
        TenantId        = $Session.TenantId
        Operator        = $Session.AdminUpn
        HeldRoles       = $Session.HeldRoles
        ModuleVersions  = $Session.ModuleVersions | Select-Object Name, Version
        Files           = $files
        SchemaVersion   = '1.4'
        GeneratedUtcIso = (Get-Date).ToUniversalTime().ToString('o')
    }

    $manifestPath = Join-Path $dir 'manifest.json'
    $manifest | ConvertTo-Json -Depth 10 | Set-Content -Path $manifestPath -Encoding utf8
    Write-Information "Evidence manifest: $manifestPath ($($files.Count) artifacts)" -InformationAction Continue

    return [PSCustomObject]@{
        Directory    = $dir
        ManifestPath = $manifestPath
        FileCount    = $files.Count
    }
}
```

Call `Write-Agt114Evidence` as the **last** step of every run — after any mutating cmdlets, after `Stop-Transcript`, but inside the same script invocation so the transcript itself is hashed. Land the directory in WORM-enabled storage (Purview Records Management with a regulatory record label, or Azure Storage immutability policy). Retention follows FINRA Rule 4511 / SEC Rule 17a-4(f) — six years, first two years readily accessible.

---

## 15. End-to-end driver script

The canonical end-to-end run for a single change window:

```powershell
#Requires -Version 7.4
#Requires -PSEdition Core

param(
    [Parameter(Mandatory)] [string] $AdminUpn,
    [Parameter(Mandatory)] [ValidateSet('Commercial','GCC','GCCHigh','DoD')] [string] $Cloud,
    [Parameter(Mandatory)] [string] $EvidenceRoot,
    [Parameter(Mandatory)] [string] $SharePointAdminUrl,
    [string] $Control46RegisterPath,
    [int]    $LookbackDays = 7,
    [string] $ChangeRef    = 'AGT114-DRY-RUN'
)

. (Join-Path $PSScriptRoot 'Initialize-Agt114Session.ps1')
. (Join-Path $PSScriptRoot 'Agt114-Functions.ps1')

$session = Initialize-Agt114Session `
    -AdminUpn $AdminUpn `
    -Cloud $Cloud `
    -EvidenceRoot $EvidenceRoot `
    -SharePointAdminUrl $SharePointAdminUrl `
    -WhatIf:$false

try {
    $inventory  = Build-Agt114Inventory          -Session $session
    $dlpJoin    = Get-Agt114DlpJoin              -Session $session -Inventory $inventory
    $reviews    = Get-Agt114AgentAccessReviews   -Session $session -Inventory $inventory
    $drift      = Find-Agt114ScopeDrift          -Session $session -InventoryBaseline $inventory -LookbackDays $LookbackDays
    $rcd        = Get-Agt114RcdReconciliation    -Session $session -Inventory $inventory -Control46RegisterPath $Control46RegisterPath

    $artifacts = @{
        inventory                = $inventory
        dlp_join                 = $dlpJoin
        access_reviews           = $reviews
        scope_drift_candidates   = $drift
        rcd_reconciliation       = $rcd
    }

    Write-Agt114Evidence -Session $session -Artifacts $artifacts -ChangeRef $ChangeRef
}
finally {
    Disconnect-ExchangeOnline -Confirm:$false -ErrorAction SilentlyContinue
    Disconnect-MgGraph -ErrorAction SilentlyContinue
    Disconnect-SPOService -ErrorAction SilentlyContinue
    Stop-Transcript | Out-Null
}
```

Run first with `$ChangeRef = 'AGT114-DRY-RUN'` and review the `manifest.json` before submitting the change record.

---

## 16. Validation checks (real queries, not `Write-Host`)

These five checks run after the driver script and produce machine-readable pass/fail records that supervisory testing consumes directly.

### 16.1 Check 1 — every active agent appears in the inventory

```powershell
function Test-Agt114InventoryCompleteness {
    [CmdletBinding()] param([Parameter(Mandatory)] $Session, [Parameter(Mandatory)] $Inventory)

    $envs        = Get-Agt114Environments -Session $Session | Where-Object HasDataverse
    $expected    = 0
    $invertedIds = $Inventory.AgentId | Sort-Object -Unique

    foreach ($e in $envs) {
        $bots = Invoke-Agt114DataverseQuery -DataverseUrl $e.DataverseUrl `
                  -RelativePath '/api/data/v9.2/bots?$select=botid,statecode&$filter=statecode eq 0'
        $expected += $bots.Count
        $missing = $bots.botid | Where-Object { $_ -notin $invertedIds }
        if ($missing) {
            Write-Warning "Environment $($e.DisplayName): $($missing.Count) active agents missing from inventory."
        }
    }

    [PSCustomObject]@{
        Check         = 'InventoryCompleteness'
        ExpectedAgents= $expected
        InventoryAgents= ($invertedIds | Measure-Object).Count
        Pass          = ($invertedIds.Count -ge $expected)
    }
}
```

### 16.2 Check 2 — no inventory row has a duplicate natural key

```powershell
function Test-Agt114NoDuplicateKeys {
    [CmdletBinding()] param([Parameter(Mandatory)] $Inventory)

    $dupes = $Inventory |
        Group-Object EnvironmentId, AgentId, SurfaceClass, ConnectorId, SurfaceId, ComponentId |
        Where-Object Count -GT 1

    [PSCustomObject]@{
        Check       = 'NoDuplicateKeys'
        DuplicateGroups = $dupes.Count
        Pass        = ($dupes.Count -eq 0)
    }
}
```

### 16.3 Check 3 — every agent connector reference resolves to a canonical connector ID

```powershell
function Test-Agt114CanonicalConnectorIds {
    [CmdletBinding()] param([Parameter(Mandatory)] $Inventory)

    $connectorRows  = $Inventory | Where-Object SurfaceClass -EQ 'ConnectorAction'
    $missing        = $connectorRows | Where-Object { -not $_.ConnectorId -or $_.ConnectorId -notlike 'shared_*' }

    [PSCustomObject]@{
        Check          = 'CanonicalConnectorIds'
        ConnectorRows  = $connectorRows.Count
        Unresolved     = $missing.Count
        Pass           = ($missing.Count -eq 0)
        Examples       = $missing | Select-Object -First 5 AgentName, ConnectorId, SurfaceId
    }
}
```

This is the check that historically read `Write-Host "Looks good"` and produced no evidence. Replacing it with a real query on the inventory output is the single highest-value defect fix in the v1.4 rewrite.

### 16.4 Check 4 — Zone 3 agents have public-web grounding disabled

```powershell
function Test-Agt114Zone3PublicWebOff {
    [CmdletBinding()] param(
        [Parameter(Mandatory)] $Inventory,
        [Parameter(Mandatory)] [string[]] $Zone3AgentIds   # from Control 1.2 registry
    )

    $violations = $Inventory | Where-Object {
        $_.AgentId -in $Zone3AgentIds -and
        $_.SurfaceClass -eq 'Setting' -and
        $_.SurfaceKind  -eq 'publicWebGroundingEnabled' -and
        $_.SurfaceId    -eq 'True'
    }

    [PSCustomObject]@{
        Check       = 'Zone3PublicWebOff'
        Violations  = $violations.Count
        Pass        = ($violations.Count -eq 0)
        Offending   = $violations | Select-Object AgentId, AgentName
    }
}
```

### 16.5 Check 5 — no agent uses a Blocked or Unclassified connector

```powershell
function Test-Agt114NoBlockedConnectors {
    [CmdletBinding()] param([Parameter(Mandatory)] $DlpJoin)

    $bad = $DlpJoin | Where-Object Severity -in 'Critical','High'

    [PSCustomObject]@{
        Check       = 'NoBlockedOrUnclassifiedConnectors'
        Findings    = $bad.Count
        Pass        = ($bad.Count -eq 0)
        Offending   = $bad | Select-Object AgentId, AgentName, ConnectorId, Classification, Finding
    }
}
```

### 16.6 Driver

```powershell
$checks = @(
    Test-Agt114InventoryCompleteness   -Session $session -Inventory $inventory
    Test-Agt114NoDuplicateKeys         -Inventory $inventory
    Test-Agt114CanonicalConnectorIds   -Inventory $inventory
    Test-Agt114Zone3PublicWebOff       -Inventory $inventory -Zone3AgentIds $zone3Ids
    Test-Agt114NoBlockedConnectors     -DlpJoin   $dlpJoin
)
$checks | Format-Table Check, Pass -AutoSize
$checks | ConvertTo-Json -Depth 10 |
    Set-Content (Join-Path $session.EvidenceRoot "agt114-$($session.Stamp)\validation-checks.json") -Encoding utf8
```

A run is **pass** only if all five checks return `Pass = $true`. Any false result is a finding that must be remediated or risk-accepted by the AI Governance Lead and CISO before sign-off.

---

## 17. Idempotency, drift detection, and rollback

### 17.1 Idempotency

Every read-only function in this playbook is idempotent by construction — re-running produces the same output (modulo `ModifiedOn` updates on Dataverse rows and any genuine tenant change). The mutating helpers (the `[CmdletBinding(SupportsShouldProcess)]` ones in §2 and §14) follow the canonical before-snapshot / mutate / after-snapshot / diff pattern from the shared baseline.

### 17.2 Day-over-day drift

```powershell
$today     = Get-Content "$EvidenceRoot\agt114-$todayStamp\inventory.json"     | ConvertFrom-Json
$yesterday = Get-Content $LastKnownGoodPath                                    | ConvertFrom-Json

$diff = Compare-Object $yesterday $today `
            -Property EnvironmentId, AgentId, SurfaceClass, ConnectorId, SurfaceId `
            -PassThru
if ($diff) {
    $diff | ConvertTo-Json -Depth 10 |
        Set-Content "$EvidenceRoot\agt114-$todayStamp\drift-day-over-day.json" -Encoding utf8
    Write-Warning "$($diff.Count) inventory changes since last known good — review."
}
```

### 17.3 Rollback

Inventory is a read-only artifact; there is nothing to roll back from `Build-Agt114Inventory`. Mutations made elsewhere — for example, removing a connector from an agent because §16.5 flagged it — must be tracked in their own change record with their own before/after snapshots and `Set-` invocation. The 1.14 evidence pack records the **state at run time**; remediation is the next change ticket.

---

## 18. Anti-patterns

The patterns below have all caused production incidents in FSI tenants. None is acceptable in a Control 1.14 runbook.

| # | Anti-pattern | Why it fails | Correct pattern |
|---|---|---|---|
| 1 | Targeting Power Apps via `Get-AdminPowerApp` and treating those as "agents" | Power Apps are not Copilot Studio agents. The two surfaces are distinct; an apps-only enumeration misses every Copilot Studio agent in the tenant. | Enumerate Dataverse `bot` table per environment via the Web API (§6). |
| 2 | Iterating `apps × connections` and emitting one row per pair | Cartesian explosion; duplicate rows with different `ComponentId`s skew DLP join counts and produce false-positive scope-drift alerts. | Dedupe on `(EnvironmentId, AgentId, SurfaceClass, ConnectorId, SurfaceId, ComponentId)` (§8). |
| 3 | Comparing connector references by friendly name (`"SharePoint"`, `"Office 365 Outlook"`) | Friendly names are localised and non-unique; comparisons silently miss matches in non-English tenants and after Microsoft renames. | Compare on canonical `ConnectorId` (`shared_sharepointonline`, `shared_office365`); never on display name (§0.1, §9). |
| 4 | `Write-Host "Validation passed"` as a validation check | Produces no evidence; cannot be rolled into a `manifest.json`; supervisory testing has nothing to verify. | Write `Test-*` functions that return `[PSCustomObject]@{ Check; Pass; ... }` and serialise to JSON (§16). |
| 5 | `Add-PowerAppsAccount` without `-Endpoint` in GCC / GCC High / DoD | Authenticates against the commercial endpoint; returns zero environments; produces a clean-looking but **empty** inventory. False-clean evidence. | `Add-PowerAppsAccount -Endpoint usgov` / `usgovhigh` / `dod` (§2, §13). |
| 6 | Mutating cmdlets without `[CmdletBinding(SupportsShouldProcess)]` | No `-WhatIf` preview; no `ShouldProcess` audit trail; mutation cannot be safely run dry. | Declare `SupportsShouldProcess` and gate every mutation on `if ($PSCmdlet.ShouldProcess(...))` (shared baseline §4). |
| 7 | No PSEdition / version guard | Script silently runs on Windows PowerShell 5.1, hits cmdlets that only exist in 7.x (PnP v2+), and either errors opaquely or returns wrong-shape objects. | `#Requires -Version 7.4` + `#Requires -PSEdition Core` + the explicit guard in §0.2. |
| 8 | Skipping `@odata.nextLink` paging on Dataverse Web API queries | Truncation at 5,000 rows; large environments emit incomplete inventories. | Loop until `@odata.nextLink` is null (§5). |
| 9 | Skipping `SessionId` / `SessionCommand 'ReturnLargeSet'` paging on `Search-UnifiedAuditLog` | Truncation at 5,000 records; high-volume tenants miss the bulk of drift evidence. | Use the paging idiom in §11. |
| 10 | Coding against an `AgentScopeExpansion` audit operation | The operation does not exist. Returns empty; produces false-clean drift report. | Correlate `CopilotInteraction`, `BotsRuntimeService`, `MicrosoftFlow`, `PowerAppsPlan`, `AzureActiveDirectory` against the inventory baseline (§11). |
| 11 | Assuming Copilot Studio cmdlets exist as a separate module | There is no standalone "Copilot Studio Admin PowerShell" module. Bot metadata lives in Dataverse. | Use Dataverse Web API + `Get-AzAccessToken` (§5–§6). |
| 12 | Hard-coded admin UPN in scripts | Operator identity is wrong in audit logs; rotation requires a code change. | `param([Parameter(Mandatory)] [string] $AdminUpn)` and pass per run. |
| 13 | Treating drift candidates as incidents | False-positive rate is non-trivial; analyst burnout follows. | Pipe through SIEM and the AI incident-response playbook for triage. |
| 14 | Asserting a latency SLA for UAL or DSPM-for-AI signals | Microsoft does not publish hard SLAs for either surface; up to 24 h is documented for UAL. Inventing one creates a false expectation that supervisory testing depends on. | Document the empirical observation; link to Microsoft Learn rather than asserting an SLA. |
| 15 | Calling `Disconnect-IPPSSession` | The cmdlet does not exist; raises `CommandNotFoundException` and may leave the session open. | `Disconnect-ExchangeOnline -Confirm:$false`. |

---

## 19. Cross-links

- **Control 1.2 — Agent registry and integrated apps.** Source-of-truth agent inventory; this playbook reconciles to it. `docs/controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md`
- **Control 1.4 — Advanced connector policies (ACP).** DLP policy authoring and connector classification; this playbook **joins** to its output. `docs/controls/pillar-1-security/1.4-advanced-connector-policies-acp.md`
- **Control 1.13 — Sensitive Information Types.** SIT signal feeds DLP-for-Copilot rule attribution and the scope-drift detector. `docs/controls/pillar-1-security/1.13-sensitive-information-types-sits-and-pattern-recognition.md`
- **Control 1.18 — RBAC and OAuth scope minimization.** Agent identity (Entra Agent ID) role-assignment posture; OAuth delegated-permission minimization on custom connectors and Graph connectors. `docs/controls/pillar-1-security/1.18-application-level-authorization-and-role-based-access-control-rbac.md`
- **Control 1.19 — eDiscovery for agent interactions.** Evidence retrieval over `CopilotInteraction` records — the same record type the drift detector consumes for scope-expansion signals. `docs/controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md`
- **Control 4.6 — Grounding scope governance.** The SharePoint enforcement layer (RCD, RSS allowed list, Data Access Governance reports). The reconciliation function in §12 joins to its output. `docs/controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md`
- **AI incident-response playbook.** Standing on-call runbook for scope-drift candidates. `docs/playbooks/incident-and-risk/ai-incident-response-playbook.md`
- **Shared PowerShell baseline.** Module pinning, sovereign endpoints, mutation safety, evidence emission. `docs/playbooks/_shared/powershell-baseline.md`

---

*Updated: April 2026 | Version: v1.6.2 | UI Verification Status: Current*
