# Control 3.8: Copilot Hub and Governance Dashboard — PowerShell Setup

!!! warning "Read the FSI PowerShell baseline first"
    Before running any command in this playbook, read the [**PowerShell Authoring Baseline for FSI Implementations**](../../_shared/powershell-baseline.md). It is the canonical source for module version pinning, sovereign-cloud (GCC / GCC High / DoD) endpoints, mutation safety (`-WhatIf` / `SupportsShouldProcess`), Dataverse compatibility, and SHA-256 evidence emission. The snippets below assume the baseline is in force.

> PowerShell automation for [Control 3.8](../../../controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md). These scripts produce **read-mostly** governance evidence (registry exports, audit pulls, configuration snapshots) and offer mutation helpers (`SupportsShouldProcess` enabled) for the Admin Exclusion Group only. All other admin-center settings are managed in the portal — Microsoft does not yet expose stable cmdlets for the Copilot Hub feature toggles.

---

## Prerequisites

```powershell
# Pin to a CAB-approved version per the FSI PowerShell baseline.
# Replace <version> with your tenant's approved versions.
Install-Module Microsoft.Graph                            -RequiredVersion '<version>' -Repository PSGallery -Scope CurrentUser -AllowClobber -AcceptLicense
Install-Module Microsoft.PowerApps.Administration.PowerShell -RequiredVersion '<version>' -Repository PSGallery -Scope CurrentUser -AllowClobber -AcceptLicense
Install-Module ExchangeOnlineManagement                   -RequiredVersion '<version>' -Repository PSGallery -Scope CurrentUser -AllowClobber -AcceptLicense

# Sovereign-cloud aware Graph connection (see baseline §3 for endpoint table)
$env  = $env:FSI_GRAPH_ENV   # 'Global','USGov','USGovDoD','China'
$ppac = $env:FSI_PPAC_ENDPOINT # 'prod','usgov','usgovhigh','dod','china'

Connect-MgGraph -Scopes @(
    'Organization.Read.All',
    'Policy.Read.All',
    'Reports.Read.All',
    'User.Read.All',
    'Group.ReadWrite.All',
    'AuditLog.Read.All',
    'Directory.Read.All'
) -Environment $env

# Power Apps Administration cmdlets are Windows PowerShell 5.1 (Desktop) only.
if ($PSVersionTable.PSEdition -ne 'Desktop') {
    throw 'Run PPAC governance scripts in Windows PowerShell 5.1 — see baseline §2.'
}
Add-PowerAppsAccount -Endpoint $ppac
```

> **Service principal authentication** for unattended runs: use Entra app registration with `Group.ReadWrite.All`, `AuditLog.Read.All`, `Reports.Read.All` (application). Document the consent in your change ticket and rotate secrets per OCC Bulletin 2026-13 (formerly OCC 2011-12).

---

## Helper: SHA-256 evidence emission

```powershell
function Write-FsiEvidence {
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory)] [string] $Path,
        [Parameter(Mandatory)] [object] $Payload,
        [string] $ControlId = '3.8'
    )
    if ($PSCmdlet.ShouldProcess($Path, 'Write evidence + SHA-256 manifest')) {
        $json = $Payload | ConvertTo-Json -Depth 10
        $json | Out-File -FilePath $Path -Encoding utf8
        $hash = Get-FileHash -Path $Path -Algorithm SHA256
        [PSCustomObject]@{
            ControlId   = $ControlId
            File        = $Path
            SHA256      = $hash.Hash
            BytesLength = (Get-Item $Path).Length
            CapturedAt  = (Get-Date).ToString('o')
        } | Export-Csv -Path "$Path.manifest.csv" -NoTypeInformation
    }
}
```

Use `Write-FsiEvidence` for every export below — the SHA-256 manifest is what examiners need under SEC 17a-4(f) WORM expectations.

---

## 1. Admin Exclusion Group lifecycle

### 1a. Create the exclusion group (idempotent)

```powershell
function New-CopilotAdminExclusionGroup {
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [string] $GroupName   = 'CopilotForM365AdminExclude',
        [string] $Description = 'Users excluded from Microsoft 365 Copilot admin-center features for compliance reasons.'
    )

    $existing = Get-MgGroup -Filter "displayName eq '$GroupName'" -ErrorAction SilentlyContinue
    if ($existing) {
        Write-Verbose "Group already exists: $($existing.Id)"
        return $existing
    }

    if ($PSCmdlet.ShouldProcess($GroupName, 'Create security group')) {
        New-MgGroup -BodyParameter @{
            displayName     = $GroupName
            description     = $Description
            mailEnabled     = $false
            securityEnabled = $true
            mailNickname    = $GroupName
        }
    }
}
```

### 1b. Add users (CSV-driven, audit-friendly)

```powershell
function Add-CopilotAdminExclusionMembers {
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory)] [string] $CsvPath,                 # cols: UserPrincipalName,Reason,AddedBy
        [string] $GroupName = 'CopilotForM365AdminExclude'
    )

    $group = Get-MgGroup -Filter "displayName eq '$GroupName'" -ErrorAction Stop
    $rows  = Import-Csv $CsvPath
    $log   = New-Object System.Collections.Generic.List[object]

    foreach ($r in $rows) {
        try {
            $u = Get-MgUser -Filter "userPrincipalName eq '$($r.UserPrincipalName)'" -ErrorAction Stop
            if ($PSCmdlet.ShouldProcess($r.UserPrincipalName, "Add to $GroupName")) {
                New-MgGroupMember -GroupId $group.Id -BodyParameter @{
                    '@odata.id' = "https://graph.microsoft.com/v1.0/directoryObjects/$($u.Id)"
                }
                $log.Add([PSCustomObject]@{ UPN=$r.UserPrincipalName; Status='Added';   Reason=$r.Reason; AddedBy=$r.AddedBy; At=(Get-Date).ToString('o') })
            }
        } catch {
            $log.Add([PSCustomObject]@{ UPN=$r.UserPrincipalName; Status='Failed'; Reason=$_.Exception.Message; AddedBy=$r.AddedBy; At=(Get-Date).ToString('o') })
        }
    }

    Write-FsiEvidence -Path ".\evidence\AdminExclusion-Add-$(Get-Date -Format yyyyMMdd-HHmmss).json" -Payload $log
    Write-Warning 'Membership changes can take up to 24 hours to take effect.'
}
```

### 1c. Export current membership (monthly governance evidence)

```powershell
function Export-CopilotAdminExclusionMembers {
    [CmdletBinding()]
    param(
        [string] $GroupName  = 'CopilotForM365AdminExclude',
        [string] $OutputPath = ".\evidence\AdminExclusion-Members-$(Get-Date -Format yyyyMMdd).json"
    )
    $group   = Get-MgGroup -Filter "displayName eq '$GroupName'" -ErrorAction Stop
    $members = Get-MgGroupMember -GroupId $group.Id -All
    $details = foreach ($m in $members) {
        $u = Get-MgUser -UserId $m.Id -ErrorAction SilentlyContinue
        if ($u) {
            [PSCustomObject]@{
                UPN         = $u.UserPrincipalName
                DisplayName = $u.DisplayName
                JobTitle    = $u.JobTitle
                Department  = $u.Department
            }
        }
    }
    Write-FsiEvidence -Path $OutputPath -Payload @{ Group=$GroupName; Members=$details; CapturedAt=(Get-Date).ToString('o') }
}
```

---

## 2. Copilot configuration snapshot (governance evidence)

```powershell
function Export-CopilotConfigurationSnapshot {
    [CmdletBinding()]
    param(
        [string] $OutputDir = ".\evidence\Copilot-Snapshot-$(Get-Date -Format yyyyMMdd-HHmmss)"
    )
    if (-not (Test-Path $OutputDir)) { New-Item -ItemType Directory -Path $OutputDir | Out-Null }

    $org    = Get-MgOrganization | Select-Object -First 1
    $cpSPs  = Get-MgServicePrincipal -All -Filter "startswith(displayName,'Microsoft 365 Copilot') or startswith(displayName,'Copilot')" |
              Select-Object DisplayName, AppId, Id, AccountEnabled, ServicePrincipalType
    $authPo = Get-MgPolicyAuthorizationPolicy
    $skus   = Get-MgSubscribedSku | Where-Object { $_.SkuPartNumber -match 'Copilot' } |
              Select-Object SkuPartNumber, SkuId, ConsumedUnits, @{n='Enabled';e={$_.PrepaidUnits.Enabled}}

    Write-FsiEvidence -Path "$OutputDir\organization.json"            -Payload $org
    Write-FsiEvidence -Path "$OutputDir\copilot-service-principals.json" -Payload $cpSPs
    Write-FsiEvidence -Path "$OutputDir\authorization-policy.json"    -Payload $authPo
    Write-FsiEvidence -Path "$OutputDir\copilot-skus.json"            -Payload $skus

    Write-Host "Snapshot written: $OutputDir" -ForegroundColor Green
}
```

> **Hedged scope:** Microsoft does not currently expose a single Graph endpoint that returns the full state of every Copilot Hub setting. This snapshot captures the surfaces that **are** queryable (org, service principals, authorization policy, SKUs). Portal screenshots remain the authoritative evidence for the User access / Data access / Actions tabs until Microsoft documents stable cmdlets.

---

## 3. Audit pull — Copilot configuration changes

```powershell
function Get-CopilotAuditEvents {
    [CmdletBinding()]
    param(
        [int]    $DaysBack   = 30,
        [string] $OutputPath = ".\evidence\Copilot-Audit-$(Get-Date -Format yyyyMMdd).json"
    )
    $start = (Get-Date).AddDays(-$DaysBack).ToString('o')
    $end   = (Get-Date).ToString('o')

    $events = Get-MgAuditLogDirectoryAudit -All `
        -Filter "activityDateTime ge $start and activityDateTime le $end" |
        Where-Object {
            $_.ActivityDisplayName -match 'Copilot|consent|policy|group member' -or
            ($_.TargetResources.DisplayName -match 'Copilot|CopilotForM365AdminExclude')
        } |
        Select-Object ActivityDateTime, ActivityDisplayName,
            @{n='InitiatedBy';e={$_.InitiatedBy.User.UserPrincipalName ?? $_.InitiatedBy.App.DisplayName}},
            Result, ResultReason,
            @{n='Targets';e={ ($_.TargetResources | ForEach-Object DisplayName) -join '; ' }}

    Write-FsiEvidence -Path $OutputPath -Payload @{ WindowDays=$DaysBack; Events=$events; CapturedAt=$end }
    Write-Host "Captured $($events.Count) audit events to $OutputPath" -ForegroundColor Green
}
```

> If `Get-MgAuditLogDirectoryAudit` returns nothing, confirm Purview Audit (Standard) is enabled and the executing identity holds **AuditLog.Read.All**. See troubleshooting playbook.

---

## 4. PPAC Copilot Studio environment inventory

```powershell
function Export-PpacCopilotStudioInventory {
    [CmdletBinding()]
    param(
        [string] $OutputPath = ".\evidence\Ppac-CopilotStudio-$(Get-Date -Format yyyyMMdd).json"
    )

    $envs = Get-AdminPowerAppEnvironment
    $inv  = foreach ($e in $envs) {
        [PSCustomObject]@{
            EnvironmentName = $e.DisplayName
            EnvironmentId   = $e.EnvironmentName
            Type            = $e.EnvironmentType
            Region          = $e.Location
            CreatedBy       = $e.CreatedBy.userPrincipalName
            CreatedTime     = $e.CreatedTime
            DataverseUrl    = $e.Internal.properties.linkedEnvironmentMetadata.instanceUrl
        }
    }
    Write-FsiEvidence -Path $OutputPath -Payload @{ Environments=$inv; CapturedAt=(Get-Date).ToString('o') }
}
```

> **PPAC Copilot Settings** (AI Prompts, Generative Actions, etc.) are not exposed via stable PowerShell cmdlets as of April 2026. Use the portal walkthrough plus screenshot evidence for SSPM-3.8-01 through SSPM-3.8-09. Track the Power Platform 2026 Wave 1 roadmap for cmdlet availability.

---

## 5. Monthly governance run (orchestrator)

```powershell
<#
.SYNOPSIS
    Control 3.8 monthly governance evidence pack.

.DESCRIPTION
    Captures Copilot configuration snapshot, Admin Exclusion Group membership,
    audit events for the last 30 days, and PPAC environment inventory. All outputs
    are JSON with SHA-256 manifests for SEC 17a-4(f) WORM evidence expectations.

.EXAMPLE
    .\Invoke-Control-3.8-MonthlyEvidence.ps1 -OutputRoot 'D:\Evidence\2026-04'

.NOTES
    Run with AI Administrator + Group.ReadWrite.All consent.
    Pair with portal screenshots for the four Copilot Settings tabs.
#>
[CmdletBinding(SupportsShouldProcess)]
param(
    [string] $OutputRoot = ".\evidence\Control-3.8-$(Get-Date -Format yyyyMM)",
    [int]    $AuditDaysBack = 30
)

try {
    if (-not (Test-Path $OutputRoot)) { New-Item -ItemType Directory -Path $OutputRoot | Out-Null }

    Export-CopilotConfigurationSnapshot   -OutputDir  "$OutputRoot\snapshot"
    Export-CopilotAdminExclusionMembers   -OutputPath "$OutputRoot\admin-exclusion-members.json"
    Get-CopilotAuditEvents                -DaysBack $AuditDaysBack -OutputPath "$OutputRoot\audit-events.json"
    Export-PpacCopilotStudioInventory     -OutputPath "$OutputRoot\ppac-environments.json"

    Write-Host "[PASS] Control 3.8 monthly evidence pack written to $OutputRoot" -ForegroundColor Green
} catch {
    Write-Host "[FAIL] $($_.Exception.Message)" -ForegroundColor Red
    Write-Host $_.ScriptStackTrace -ForegroundColor Yellow
    exit 1
} finally {
    Disconnect-MgGraph -ErrorAction SilentlyContinue
}
```

---

## Hedged language and scope reminders

- These scripts **support** evidence collection for FINRA 4511 / RN 24-09, SEC 17a-3/4, GLBA 501(b), SOX 404. They do not by themselves constitute regulatory compliance.
- Module pinning, sovereign cloud endpoints, and Desktop-edition guards are required per the [PowerShell baseline](../../_shared/powershell-baseline.md) — false-clean evidence is the most common audit gap.
- Mutation cmdlets (group create, member add) implement `SupportsShouldProcess`; use `-WhatIf` in change-window dry runs.

---

## Next Steps

- [Portal Walkthrough](portal-walkthrough.md) — manual configuration
- [Verification & Testing](verification-testing.md) — test cases and evidence collection
- [Troubleshooting](troubleshooting.md) — common issues and resolutions

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
