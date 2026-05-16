# PowerShell Setup: Control 1.3 - SharePoint Content Governance and Permissions

!!! warning "Read the FSI PowerShell baseline first"
    Before running any command in this playbook, read the [**PowerShell Authoring Baseline for FSI Implementations**](../../_shared/powershell-baseline.md). It is the canonical source for module version pinning, sovereign-cloud (GCC / GCC High / DoD) endpoints, mutation safety (`-WhatIf` / `SupportsShouldProcess`), Dataverse compatibility, and SHA-256 evidence emission. Snippets below show abbreviated patterns; the baseline is authoritative.

**Last Updated:** May 2026
**Modules Required:** `Microsoft.Online.SharePoint.PowerShell`, `PnP.PowerShell` (v2+ — requires Entra app registration), `Microsoft.Graph` (Identity.Governance, Sites, Groups), `ExchangeOnlineManagement` (only if pairing with retention)
**PowerShell Edition:** PowerShell 7.2+ for `PnP.PowerShell` v2 and `Microsoft.Graph`. `Microsoft.Online.SharePoint.PowerShell` runs on both Desktop 5.1 and Core 7+.

---

## 0. Prerequisites and connection

```powershell
# Pin versions per the FSI PowerShell baseline. Examples below; substitute CAB-approved versions.
Install-Module -Name Microsoft.Online.SharePoint.PowerShell -RequiredVersion '16.0.25515.12000' -Repository PSGallery -Scope CurrentUser -AllowClobber -AcceptLicense
Install-Module -Name PnP.PowerShell                         -RequiredVersion '2.12.0'           -Repository PSGallery -Scope CurrentUser -AllowClobber -AcceptLicense
Install-Module -Name Microsoft.Graph                        -RequiredVersion '2.25.0'           -Repository PSGallery -Scope CurrentUser -AllowClobber -AcceptLicense

# Sovereign-cloud aware connection (Commercial example)
$TenantName  = 'contoso'
$AdminUrl    = "https://$TenantName-admin.sharepoint.com"

Connect-SPOService -Url $AdminUrl                                  # interactive MFA in browser
Connect-MgGraph -Scopes 'Sites.Read.All','Group.Read.All','AccessReview.ReadWrite.All' -NoWelcome
# For PnP v2, pre-register an Entra app and consent the SharePoint scopes you intend to use:
# Connect-PnPOnline -Url $AdminUrl -ClientId $PnPClientId -Interactive
```

For GCC / GCC High / DoD, append the appropriate `-Region` parameter to `Connect-SPOService` and use the matching `Connect-MgGraph -Environment` value (see baseline §3).

> Microsoft Learn now calls for the latest SharePoint Online Management Shell when configuring Restricted Content Discovery. Keep the CAB-approved `Microsoft.Online.SharePoint.PowerShell` pin current enough to expose the RAC / RCD / Restricted Search cmdlets used below; if a cmdlet or parameter is missing, fail closed and use the SharePoint admin center until the module is updated.

---

## 1. Tenant-level sharing baseline (idempotent)

```powershell
[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'High')]
param(
    [ValidateSet('Zone1','Zone2','Zone3')]
    [string]$Zone = 'Zone3'
)

$desired = switch ($Zone) {
    'Zone1' { @{ SharingCapability = 'ExternalUserSharingOnly';         RequireAcceptingAccountMatchInvitedAccount = $true; DefaultSharingLinkType = 'Internal'; DefaultLinkPermission = 'View'; FileAnonymousLinkType = 'View'; FolderAnonymousLinkType = 'View'; RequireAnonymousLinksExpireInDays = 30 } }
    'Zone2' { @{ SharingCapability = 'ExistingExternalUserSharingOnly'; RequireAcceptingAccountMatchInvitedAccount = $true; DefaultSharingLinkType = 'Internal'; DefaultLinkPermission = 'View'; FileAnonymousLinkType = 'View'; FolderAnonymousLinkType = 'View'; RequireAnonymousLinksExpireInDays = 7  } }
    'Zone3' { @{ SharingCapability = 'Disabled';                        RequireAcceptingAccountMatchInvitedAccount = $true; DefaultSharingLinkType = 'Internal'; DefaultLinkPermission = 'View'; FileAnonymousLinkType = 'View'; FolderAnonymousLinkType = 'View'; RequireAnonymousLinksExpireInDays = 0  } }
}

$current = Get-SPOTenant
$drift   = $desired.GetEnumerator() | Where-Object { $current.$($_.Key) -ne $_.Value }

if (-not $drift) {
    Write-Host "[PASS] Tenant sharing already at $Zone baseline." -ForegroundColor Green
    return
}

Write-Host "[CHANGE] Tenant sharing drift detected:" -ForegroundColor Yellow
$drift | ForEach-Object { Write-Host ("  {0}: {1} -> {2}" -f $_.Key, $current.$($_.Key), $_.Value) }

if ($PSCmdlet.ShouldProcess('Tenant', "Apply $Zone sharing baseline")) {
    Set-SPOTenant @desired
    Write-Host "[DONE] Tenant sharing baseline applied." -ForegroundColor Green
}
```

> Always run with `-WhatIf` first. Pair the change with a CAB ticket — `Set-SPOTenant` mutates tenant-global state.

---

## 2. Inventory agent grounding sites with sharing posture

```powershell
$InventoryPath = "C:\Governance\1.3\agent-sites-$(Get-Date -Format 'yyyy-MM-dd').csv"
New-Item -ItemType Directory -Force -Path (Split-Path $InventoryPath) | Out-Null

# Optionally narrow to an explicit allow-list maintained by the AI Governance Lead
$AllowList = Get-Content "C:\Governance\1.3\agent-grounding-sites.txt" -ErrorAction SilentlyContinue

$sites = Get-SPOSite -Limit All -IncludePersonalSite:$false -Detailed |
    Where-Object { -not $AllowList -or ($AllowList -contains $_.Url) } |
    Select-Object Url, Title, Owner, Template, SharingCapability,
                  ConditionalAccessPolicy, SensitivityLabel,
                  RestrictedAccessControl,
                  @{ N='RestrictContentOrgWideSearch'; E={ $_.RestrictContentOrgWideSearch } },
                  StorageUsageCurrent, LastContentModifiedDate

$sites | Export-Csv -Path $InventoryPath -NoTypeInformation -Encoding utf8
$sha = (Get-FileHash -Path $InventoryPath -Algorithm SHA256).Hash
"$sha  $InventoryPath" | Out-File "$InventoryPath.sha256"

Write-Host "[DONE] Exported $($sites.Count) sites to $InventoryPath (SHA256 emitted)." -ForegroundColor Green
```

---

## 3. Remove `Everyone` and `Everyone except external users` from a site

```powershell
function Remove-BroadClaim {
    [CmdletBinding(SupportsShouldProcess = $true)]
    param(
        [Parameter(Mandatory)] [string]$SiteUrl
    )

    $claims = @(
        @{ Name = 'Everyone';                       LoginName = 'c:0(.s|true' },
        @{ Name = 'Everyone except external users'; LoginName = "c:0-.f|rolemanager|spo-grid-all-users/$((Get-SPOTenant).RootSiteUrl -replace 'https://([^\.]+)\..*','$1')" }
    )

    foreach ($claim in $claims) {
        $found = Get-SPOUser -Site $SiteUrl -Limit All -ErrorAction SilentlyContinue |
                 Where-Object { $_.LoginName -eq $claim.LoginName -or $_.LoginName -match 'spo-grid-all-users|^c:0\(\.s\|true$' }

        if (-not $found) {
            Write-Host "[OK] $($claim.Name) not present on $SiteUrl" -ForegroundColor Gray
            continue
        }

        if ($PSCmdlet.ShouldProcess($SiteUrl, "Remove claim $($claim.Name)")) {
            try {
                Remove-SPOUser -Site $SiteUrl -LoginName $found.LoginName -ErrorAction Stop
                Write-Host "[DONE] Removed $($claim.Name) from $SiteUrl" -ForegroundColor Yellow
            } catch {
                Write-Warning "Failed to remove $($claim.Name) from $SiteUrl: $($_.Exception.Message)"
            }
        }
    }
}

# Apply across the agent grounding inventory
Get-Content "C:\Governance\1.3\agent-grounding-sites.txt" |
    ForEach-Object { Remove-BroadClaim -SiteUrl $_ -WhatIf }   # remove -WhatIf after CAB approval
```

> The exact LoginName for `Everyone except external users` includes the tenant short name; the function above derives it from `Get-SPOTenant`. If your tenant uses a vanity domain, validate the claim string with `Get-SPOUser -Site $SiteUrl | Where-Object LoginName -like '*spo-grid-all-users*'` before running in production.

---

## 4. Apply Zone 3 site posture (sharing, label, RAC, RCD)

```powershell
function Set-AgentGroundingSite {
    [CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'High')]
    param(
        [Parameter(Mandatory)][string]$SiteUrl,
        [Parameter(Mandatory)][ValidateSet('Zone1','Zone2','Zone3')][string]$Zone,
        [string]$SensitivityLabelName,        # e.g. 'Confidential-FSI'
        [string]$RestrictAccessGroupId,       # required for Zone3 RAC
        [switch]$EnableRCD
    )

    $site = Get-SPOSite -Identity $SiteUrl -Detailed -ErrorAction Stop

    # 4a — sharing capability
    $desiredSharing = @{ Zone1 = 'ExternalUserSharingOnly'; Zone2 = 'ExistingExternalUserSharingOnly'; Zone3 = 'Disabled' }[$Zone]
    if ($site.SharingCapability -ne $desiredSharing -and $PSCmdlet.ShouldProcess($SiteUrl, "Set SharingCapability=$desiredSharing")) {
        Set-SPOSite -Identity $SiteUrl -SharingCapability $desiredSharing -DisableSharingForNonOwners
        Write-Host "[DONE] $SiteUrl SharingCapability -> $desiredSharing" -ForegroundColor Yellow
    }

    # 4b — container sensitivity label (Microsoft.Graph route preferred)
    if ($SensitivityLabelName -and $site.SensitivityLabel -ne $SensitivityLabelName -and $PSCmdlet.ShouldProcess($SiteUrl, "Apply label $SensitivityLabelName")) {
        $groupId = (Get-SPOSite -Identity $SiteUrl -Detailed).GroupId
        if ($groupId -and $groupId -ne [Guid]::Empty) {
            $label = Get-MgBetaInformationProtectionPolicyLabel -All | Where-Object DisplayName -eq $SensitivityLabelName
            if ($label) {
                Update-MgGroup -GroupId $groupId -BodyParameter @{ assignedLabels = @(@{ labelId = $label.Id }) }
                Write-Host "[DONE] Label $SensitivityLabelName applied to group $groupId" -ForegroundColor Yellow
            } else {
                Write-Warning "Label $SensitivityLabelName not found in published policy."
            }
        } else {
            Write-Warning "$SiteUrl is not group-connected; apply container label via SharePoint admin UI."
        }
    }

    # 4c — Restricted Access Control (Zone 3)
    if ($Zone -eq 'Zone3') {
        if (-not $RestrictAccessGroupId) { throw "RestrictAccessGroupId is mandatory for Zone3." }
        if ($PSCmdlet.ShouldProcess($SiteUrl, "Enable RAC bound to group $RestrictAccessGroupId")) {
            Set-SPOSite -Identity $SiteUrl -RestrictedAccessControl $true
            Add-SPOSiteCollectionAppCatalog -Site $SiteUrl -ErrorAction SilentlyContinue | Out-Null
            Set-SPOSiteGroup -Site $SiteUrl -Identity 'RestrictedAccessControlGroups' -Users @($RestrictAccessGroupId) -ErrorAction SilentlyContinue
            # SAM RAC API surface evolves; if Set-SPOSiteGroup is unavailable, manage via the SharePoint admin UI flyout.
            Write-Host "[DONE] RAC enabled on $SiteUrl" -ForegroundColor Yellow
        }
    }

    # 4d — Restricted Content Discovery (suppress from search/Copilot)
    if ($EnableRCD -and $PSCmdlet.ShouldProcess($SiteUrl, "Enable Restricted Content Discovery")) {
        Set-SPOSite -Identity $SiteUrl -RestrictContentOrgWideSearch $true
        Write-Host "[DONE] RCD enabled on $SiteUrl" -ForegroundColor Yellow
    }
}

# Example
Set-AgentGroundingSite -SiteUrl 'https://contoso.sharepoint.com/sites/Agent-CustomerService' `
                       -Zone Zone3 `
                       -SensitivityLabelName 'Confidential-FSI' `
                       -RestrictAccessGroupId 'a3f1c2b4-...' `
                       -EnableRCD `
                       -WhatIf
```

> The exact RAC parameter surface on `Set-SPOSite` shipped over multiple SharePoint Online Management Shell releases. Verify with `Get-Help Set-SPOSite -Parameter RestrictedAccessControl` after each module update; if the parameter is not present, fall back to the SharePoint admin center flyout (Step 5 of the Portal Walkthrough).

---

## 5. Restricted SharePoint Search allow-list (temporary safeguard)

```powershell
[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [string[]]$AllowedSites = @(
        'https://contoso.sharepoint.com/sites/Agent-CustomerService',
        'https://contoso.sharepoint.com/sites/Agent-Compliance'
    )
)

if ($AllowedSites.Count -gt 100) { throw "Restricted SharePoint Search supports at most 100 sites." }

if ($PSCmdlet.ShouldProcess('Tenant', 'Enable Restricted SharePoint Search')) {
    Set-SPOTenant -RestrictedSharePointSearchEnabled $true
    foreach ($url in $AllowedSites) {
        Add-SPOTenantRestrictedSearchAllowedList -SitesList $url
    }
    Write-Host "[DONE] Restricted SharePoint Search enabled with $($AllowedSites.Count) sites." -ForegroundColor Green
    Write-Warning "Restricted SharePoint Search is a temporary safeguard. Schedule a follow-up to disable once sites are remediated."
}
```

> Cmdlet names (`Add-SPOTenantRestrictedSearchAllowedList`, `Set-SPOTenant -RestrictedSharePointSearchEnabled`) shipped during the Microsoft 365 Copilot rollout. Confirm with `Get-Command -Module Microsoft.Online.SharePoint.PowerShell *RestrictedSearch*` against your pinned module version.

---

## 6. Permission report for evidence (per-site)

```powershell
function Get-AgentSitePermissionReport {
    param([Parameter(Mandatory)][string[]]$SiteUrls)

    $report = foreach ($url in $SiteUrls) {
        try {
            $site  = Get-SPOSite -Identity $url -Detailed -ErrorAction Stop
            $users = Get-SPOUser -Site $url -Limit All -ErrorAction Stop
            foreach ($u in $users) {
                [PSCustomObject]@{
                    Site               = $url
                    SiteSensitivity    = $site.SensitivityLabel
                    SharingCapability  = $site.SharingCapability
                    LoginName          = $u.LoginName
                    DisplayName        = $u.DisplayName
                    IsSiteAdmin        = $u.IsSiteAdmin
                    Groups             = ($u.Groups -join '; ')
                    IsBroadClaim       = $u.LoginName -match 'spo-grid-all-users|^c:0\(\.s\|true$'
                }
            }
        } catch {
            Write-Warning "Skipped $url : $($_.Exception.Message)"
        }
    }

    $out = "C:\Governance\1.3\permissions-$(Get-Date -Format 'yyyy-MM-dd').csv"
    $report | Export-Csv -Path $out -NoTypeInformation -Encoding utf8
    $sha = (Get-FileHash -Path $out -Algorithm SHA256).Hash
    "$sha  $out" | Out-File "$out.sha256"
    Write-Host "[DONE] Permission report: $out (SHA256 emitted)." -ForegroundColor Green
    return $out
}

Get-Content "C:\Governance\1.3\agent-grounding-sites.txt" | Get-AgentSitePermissionReport
```

---

## 7. Create access reviews on M365 groups via Microsoft Graph

```powershell
# Requires: Connect-MgGraph -Scopes 'AccessReview.ReadWrite.All','Group.Read.All'
$GroupIds = @('11111111-1111-1111-1111-111111111111','22222222-2222-2222-2222-222222222222')

$reviewBody = @{
    displayName        = 'Agent grounding sites — quarterly access review'
    descriptionForAdmins = 'Quarterly recertification of M365 groups backing Copilot Studio agent grounding sites (Control 1.3).'
    descriptionForReviewers = 'Confirm each member still requires access to the agent grounding site backing this group. Justification required.'
    scope = @{
        '@odata.type' = '#microsoft.graph.principalResourceMembershipsScope'
        principalScopes = @(@{ '@odata.type' = '#microsoft.graph.accessReviewQueryScope'; query = '/users'; queryType = 'MicrosoftGraph' })
        resourceScopes  = $GroupIds | ForEach-Object { @{ '@odata.type' = '#microsoft.graph.accessReviewQueryScope'; query = "/groups/$_"; queryType = 'MicrosoftGraph' } }
    }
    reviewers           = @(@{ query = "/groups/<governance-group-id>/transitiveMembers"; queryType = 'MicrosoftGraph' })
    settings = @{
        mailNotificationsEnabled    = $true
        reminderNotificationsEnabled = $true
        justificationRequiredOnApproval = $true
        defaultDecisionEnabled      = $true
        defaultDecision             = 'Deny'
        instanceDurationInDays      = 14
        autoApplyDecisionsEnabled   = $true
        recommendationsEnabled      = $true
        recurrence = @{
            pattern = @{ type = 'absoluteMonthly'; interval = 3 }
            range   = @{ type = 'noEnd'; startDate = (Get-Date -Format 'yyyy-MM-dd') }
        }
    }
}

New-MgIdentityGovernanceAccessReviewDefinition -BodyParameter $reviewBody
```

---

## 8. Drift-detection scheduled job (idempotent)

Run nightly under a least-privileged service account; raise an incident if any Zone 3 site drifts.

```powershell
$Inventory = Import-Csv "C:\Governance\1.3\agent-grounding-sites.csv"  # columns: Url,Zone,ExpectedLabel
$violations = foreach ($row in $Inventory) {
    try {
        $s = Get-SPOSite -Identity $row.Url -Detailed
        $broad = Get-SPOUser -Site $row.Url -Limit All | Where-Object LoginName -match 'spo-grid-all-users|^c:0\(\.s\|true$'
        $issues = New-Object System.Collections.Generic.List[string]
        if ($row.Zone -eq 'Zone3' -and $s.SharingCapability -ne 'Disabled') { $issues.Add("SharingCapability=$($s.SharingCapability)") }
        if ($row.ExpectedLabel -and $s.SensitivityLabel -ne $row.ExpectedLabel) { $issues.Add("Label=$($s.SensitivityLabel)") }
        if ($broad) { $issues.Add("BroadClaim=$($broad.LoginName -join ',')") }
        if ($issues.Count) { [PSCustomObject]@{ Url=$row.Url; Zone=$row.Zone; Issues=($issues -join '; ') } }
    } catch { Write-Warning "Probe failed for $($row.Url): $($_.Exception.Message)" }
}

if ($violations) {
    $out = "C:\Governance\1.3\drift-$(Get-Date -Format 'yyyy-MM-dd-HHmm').csv"
    $violations | Export-Csv -Path $out -NoTypeInformation -Encoding utf8
    # Send to ITSM / Sentinel / Compliance Officer mailbox per your runbook
    Write-Host "[ALERT] $($violations.Count) drift events written to $out" -ForegroundColor Red
    exit 2
} else {
    Write-Host "[PASS] No drift detected." -ForegroundColor Green
    exit 0
}
```

---

## 9. End-to-end orchestration (read-only by default)

```powershell
<#
.SYNOPSIS
    Orchestrates Control 1.3 baseline checks and (optionally) remediation.

.PARAMETER SitesPath
    File listing the agent grounding sites, one URL per line.

.PARAMETER Zone
    Governance zone for the in-scope sites. Defaults to Zone3.

.PARAMETER Apply
    Switch — when set, mutating operations (claim removal, RAC, RCD) execute.
    When omitted, the script runs in read-only / WhatIf mode.

.EXAMPLE
    .\Invoke-Control-1.3.ps1 -SitesPath 'C:\Governance\1.3\agent-grounding-sites.txt'
    .\Invoke-Control-1.3.ps1 -SitesPath '...' -Zone Zone3 -Apply
#>
[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'High')]
param(
    [Parameter(Mandatory)][string]$SitesPath,
    [ValidateSet('Zone1','Zone2','Zone3')][string]$Zone = 'Zone3',
    [switch]$Apply
)

$WhatIfPreference = -not $Apply

$sites = Get-Content $SitesPath
Write-Host "=== Control 1.3 :: $($sites.Count) sites :: $Zone :: Apply=$Apply ===" -ForegroundColor Cyan

# 1. Tenant baseline
& $PSScriptRoot\01-Set-TenantSharing.ps1 -Zone $Zone

# 2. Inventory
& $PSScriptRoot\02-Inventory.ps1 -SitesPath $SitesPath

# 3+4. Per-site posture
foreach ($url in $sites) {
    Remove-BroadClaim -SiteUrl $url
    Set-AgentGroundingSite -SiteUrl $url -Zone $Zone -EnableRCD:($Zone -eq 'Zone3')
}

# 6. Permission report
Get-AgentSitePermissionReport -SiteUrls $sites | Out-Null

Write-Host "Control 1.3 orchestration complete." -ForegroundColor Cyan
```

---

[Back to Control 1.3](../../../controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: May 2026 | Version: v1.6.2*
