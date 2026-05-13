# Control 4.1: SharePoint Information Access Governance (IAG) — PowerShell Setup

!!! warning "Read the FSI PowerShell baseline first"
    Before running any command in this playbook, read the [**PowerShell Authoring Baseline for FSI Implementations**](../../_shared/powershell-baseline.md). It is the canonical source for module version pinning, sovereign-cloud (GCC / GCC High / DoD) endpoints, mutation safety (`-WhatIf` / `SupportsShouldProcess`), Dataverse compatibility, and SHA-256 evidence emission. Snippets below show abbreviated patterns; the baseline is authoritative.

> Automation guidance for [Control 4.1](../../../controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md). Uses `Microsoft.Online.SharePoint.PowerShell` (SPO Management Shell), `PnP.PowerShell` (DAG and site context), and `Microsoft.Graph` (group resolution / audit log).

---

## Module Prerequisites

```powershell
# Pin known-good versions; confirm in your release notes
Install-Module Microsoft.Online.SharePoint.PowerShell -MinimumVersion 16.0.25814.12000 -Scope CurrentUser -Force
Install-Module PnP.PowerShell                          -MinimumVersion 2.12.0           -Scope CurrentUser -Force
Install-Module Microsoft.Graph                         -MinimumVersion 2.25.0           -Scope CurrentUser -Force

Import-Module Microsoft.Online.SharePoint.PowerShell
Import-Module PnP.PowerShell
Import-Module Microsoft.Graph.Groups
```

**Sovereign clouds:** Use the appropriate `-Region` / endpoint for GCC, GCC High, and DoD per the baseline. Do not hard-code `*.sharepoint.com`.

---

## Connect

```powershell
$AdminUrl = 'https://contoso-admin.sharepoint.com'   # Replace; use *.sharepoint.us for GCC High / DoD
Connect-SPOService -Url $AdminUrl
Connect-MgGraph -Scopes 'Group.Read.All','AuditLog.Read.All' -NoWelcome
```

Verify connection:

```powershell
Get-SPOTenant | Select-Object SignInAccelerationDomain, SharingCapability
```

---

## 1. Inventory: Identify RCD/RAC Posture Across the Tenant

```powershell
$AllSites = Get-SPOSite -Limit All -IncludePersonalSite:$false

$Inventory = $AllSites | Select-Object `
    Url, Title, Owner,
    RestrictContentOrgWideSearch,
    RestrictedAccessControl,
    @{ N = 'RACGroupCount'; E = { ($_.RestrictedAccessControlGroups -split ',' | Where-Object { $_ }).Count } },
    SensitivityLabel, SharingCapability, ConditionalAccessPolicy, LastContentModifiedDate

$ReportPath = Join-Path -Path (Get-Location) -ChildPath ("IAG-Inventory-{0:yyyyMMdd}.csv" -f (Get-Date))
$Inventory | Export-Csv -Path $ReportPath -NoTypeInformation -Encoding UTF8

# Emit SHA-256 evidence hash (per baseline)
$Hash = (Get-FileHash -Path $ReportPath -Algorithm SHA256).Hash
Write-Host ("Inventory: {0} (SHA-256 {1})" -f $ReportPath, $Hash)
```

---

## 2. Enable RCD on a Single Site (Idempotent, `-WhatIf` Aware)

```powershell
function Set-IagRcd {
    [CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'High')]
    param(
        [Parameter(Mandatory)] [string] $SiteUrl,
        [Parameter(Mandatory)] [bool]   $Enable,
        [Parameter(Mandatory)] [string] $Justification
    )

    try {
        $site = Get-SPOSite -Identity $SiteUrl -ErrorAction Stop
    } catch {
        Write-Error "Site not found: $SiteUrl ($($_.Exception.Message))"
        return
    }

    if ($site.RestrictContentOrgWideSearch -eq $Enable) {
        Write-Host "[SKIP] $SiteUrl already RCD=$Enable"
        return
    }

    if ($PSCmdlet.ShouldProcess($SiteUrl, "Set RestrictContentOrgWideSearch=$Enable")) {
        Set-SPOSite -Identity $SiteUrl -RestrictContentOrgWideSearch $Enable -ErrorAction Stop
        Write-Host "[OK]   $SiteUrl RCD=$Enable :: $Justification"
    }
}

# Examples
Set-IagRcd -SiteUrl 'https://contoso.sharepoint.com/sites/FinanceConfidential' `
           -Enable $true -Justification 'Zone 3 SOX-scoped, ticket CHG-1042' -WhatIf
```

The function is idempotent (no-op when desired state already holds) and supports `-WhatIf` for dry runs — required by the baseline.

---

## 3. Bulk Enable RCD from a Governance Manifest

Manifest CSV columns: `Url, Zone, Justification, ChangeTicket`.

```powershell
$Manifest = Import-Csv -Path '.\rcd-manifest.csv'

$Results = foreach ($row in $Manifest) {
    try {
        Set-IagRcd -SiteUrl $row.Url -Enable $true -Justification "$($row.Zone) :: $($row.Justification) ($($row.ChangeTicket))"
        [pscustomobject]@{ Url = $row.Url; Status = 'OK'; Error = $null }
    } catch {
        [pscustomobject]@{ Url = $row.Url; Status = 'FAIL'; Error = $_.Exception.Message }
    }
}

$ResultsPath = Join-Path -Path (Get-Location) -ChildPath ("RCD-BulkApply-{0:yyyyMMddHHmm}.csv" -f (Get-Date))
$Results | Export-Csv -Path $ResultsPath -NoTypeInformation -Encoding UTF8
$Hash = (Get-FileHash $ResultsPath -Algorithm SHA256).Hash
Write-Host ("Bulk apply log: {0} (SHA-256 {1})" -f $ResultsPath, $Hash)
```

---

## 4. Configure Restricted SharePoint Search (RSS) Allow-List

!!! warning "Short-term posture"
    Treat RSS as a transitional control. Document an exit plan to RCD + Purview.

```powershell
# Enable tenant-level RSS
Set-SPOTenant -EnableRestrictedAccessControl $false   # Reserved
Set-SPOTenant -EnableRestrictedSearchAllList $true

# Add sites (current documented limit: 100; verify on Microsoft Learn)
$AllowList = @(
    'https://contoso.sharepoint.com/sites/CopilotPilot',
    'https://contoso.sharepoint.com/sites/HRPolicies'
)

foreach ($url in $AllowList) {
    try {
        Add-SPOTenantRestrictedSearchAllowedList -SiteUrl $url -ErrorAction Stop
        Write-Host "[OK] Added $url to RSS allow-list"
    } catch {
        Write-Warning "Add failed for $url :: $($_.Exception.Message)"
    }
}

# Inspect current RSS state
Get-SPOTenant | Select-Object EnableRestrictedSearchAllList
Get-SPOTenantRestrictedSearchAllowedList
```

---

## 5. Configure Restricted Access Control (RAC) per Site

```powershell
function Resolve-EntraGroupId {
    param([Parameter(Mandatory)][string]$DisplayName)
    $g = Get-MgGroup -Filter "displayName eq '$DisplayName'" -ConsistencyLevel eventual -ErrorAction Stop
    if (-not $g) { throw "Group not found: $DisplayName" }
    if ($g.Count -gt 1) { throw "Ambiguous group name: $DisplayName" }
    return $g.Id
}

function Set-IagRac {
    [CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'High')]
    param(
        [Parameter(Mandatory)] [string]   $SiteUrl,
        [Parameter(Mandatory)] [string[]] $GroupDisplayNames,   # max 10
        [Parameter(Mandatory)] [string]   $Justification
    )

    if ($GroupDisplayNames.Count -gt 10) {
        throw "RAC supports a maximum of 10 security groups per site."
    }

    $groupIds = $GroupDisplayNames | ForEach-Object { Resolve-EntraGroupId -DisplayName $_ }

    if ($PSCmdlet.ShouldProcess($SiteUrl, "Enable RAC with $($groupIds.Count) group(s)")) {
        Set-SPOSite -Identity $SiteUrl -RestrictedAccessControl $true -ErrorAction Stop
        Set-SPOSite -Identity $SiteUrl -RestrictedAccessControlGroups ($groupIds -join ',') -ErrorAction Stop
        Write-Host "[OK] RAC applied :: $SiteUrl :: $Justification"
    }
}

# Example: M&A deal room
Set-IagRac -SiteUrl 'https://contoso.sharepoint.com/sites/MandA-ProjectAlpha' `
           -GroupDisplayNames @('MandA-DealTeam-Alpha','Compliance-Surveillance') `
           -Justification 'MNPI ethical wall, ticket CHG-1099' -WhatIf
```

### Delegate RAC Management to Site Admins

```powershell
Set-SPOTenant -DelegateRestrictedAccessControlManagement $true
Get-SPOTenant | Select-Object DelegateRestrictedAccessControlManagement
```

When delegated, site admins must supply a justification on each policy update — captured to the unified audit log.

---

## 6. Generate RAC Insights

```powershell
# Generates an admin report on RAC-protected sites and their access patterns
Start-SPORestrictedAccessForSitesInsights
# Retrieve results from SharePoint admin center > Reports > Restricted access control insights
```

---

## 7. Pull Audit Evidence (Microsoft Graph)

```powershell
# Search the unified audit log for IAG operations (last 30 days)
$Start = (Get-Date).AddDays(-30).ToString('o')
$End   = (Get-Date).ToString('o')

$ops = @('SiteRestrictedFromOrgSearch','RestrictedAccessControlPolicyUpdated')

$events = foreach ($op in $ops) {
    Search-UnifiedAuditLog -StartDate $Start -EndDate $End -Operations $op -ResultSize 5000
}

$AuditPath = Join-Path -Path (Get-Location) -ChildPath ("IAG-Audit-{0:yyyyMMdd}.csv" -f (Get-Date))
$events | Export-Csv -Path $AuditPath -NoTypeInformation -Encoding UTF8
$Hash = (Get-FileHash $AuditPath -Algorithm SHA256).Hash
Write-Host ("Audit evidence: {0} (SHA-256 {1})" -f $AuditPath, $Hash)
```

`Search-UnifiedAuditLog` requires `Connect-IPPSSession` (Exchange Online Management module).

---

## Cleanup

```powershell
Disconnect-SPOService -ErrorAction SilentlyContinue
Disconnect-MgGraph    -ErrorAction SilentlyContinue
```

---

## Error-Handling Patterns

| Scenario | Pattern |
|---|---|
| Site not found | `try/catch` on `Get-SPOSite -ErrorAction Stop`; record FAIL row in results CSV |
| Throttling (`429`) | Wrap mutating cmdlets with exponential backoff (per baseline) |
| Ambiguous group | `Resolve-EntraGroupId` throws; halt and surface to operator |
| Stale module | Pin `-MinimumVersion`; CI fails the script if older module is loaded |
| Sovereign cloud | Use `Connect-SPOService -Region` and `Connect-MgGraph -Environment` per baseline |

---

[Back to Control 4.1](../../../controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification & Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: April 2026 | Version: v1.6.2*
