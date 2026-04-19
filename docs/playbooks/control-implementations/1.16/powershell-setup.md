# PowerShell Setup: Control 1.16 — Information Rights Management (IRM)

!!! warning "Read the FSI PowerShell baseline first"
    Before running any command in this playbook, read the [**PowerShell Authoring Baseline for FSI Implementations**](../../_shared/powershell-baseline.md). It is the canonical source for module version pinning, sovereign-cloud (GCC / GCC High / DoD) endpoints, mutation safety (`-WhatIf` / `SupportsShouldProcess`), Dataverse compatibility, and SHA-256 evidence emission. Snippets below show the surgical command surface for Control 1.16; the baseline is authoritative for the safe-execution wrapper.

**Last Updated:** April 2026
**Modules Required:** `AIPService` (Azure RMS), `PnP.PowerShell` v2+ (SharePoint), `ExchangeOnlineManagement` (label policies — read-only verification), optional `Microsoft.Graph` (audit log retrieval).

---

## Prerequisites

```powershell
# Pin to versions approved by your Change Advisory Board.
# AIPService: Desktop or Core PowerShell 5.1+ / 7.2+
# PnP.PowerShell v2+: requires PowerShell 7+ AND a tenant Entra app registration with delegated/app permissions
Install-Module -Name AIPService       -RequiredVersion '<approved-version>' -Repository PSGallery -Scope CurrentUser -AcceptLicense
Install-Module -Name PnP.PowerShell   -RequiredVersion '<approved-version>' -Repository PSGallery -Scope CurrentUser -AcceptLicense
```

For PnP.PowerShell v2+ first-time setup in your tenant, run `Register-PnPEntraIDApp -ApplicationName 'PnP-FSI-IRM-Ops' -Tenant '<tenant>.onmicrosoft.com' -Interactive` once with an Entra Global Admin account — recorded in the change ticket. Subsequent connections in this playbook use that registered app.

---

## Script 1 — Verify and Activate Azure RMS

```powershell
<#
.SYNOPSIS
    Reports Azure Rights Management Service status and (optionally) activates it.
.DESCRIPTION
    Read-only by default. Pass -Activate to enable Azure RMS — requires Entra
    Global Admin and is a one-time tenant-level mutation.
.PARAMETER Activate
    Switch. When supplied, will call Enable-AipService if status is not Enabled.
.EXAMPLE
    .\Test-AzureRMS.ps1
.EXAMPLE
    .\Test-AzureRMS.ps1 -Activate -WhatIf
#>
[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'High')]
param(
    [switch]$Activate
)

Connect-AipService

$status = Get-AipService
Write-Host "Azure RMS Status: $status"

if ($status -ne 'Enabled') {
    Write-Warning 'Azure RMS is NOT activated. IRM-enabled labels and library IRM will not function.'
    if ($Activate) {
        if ($PSCmdlet.ShouldProcess('Tenant Azure RMS', 'Enable-AipService')) {
            Enable-AipService
            Write-Host '[OK] Activation requested. Allow 15-30 min for propagation.' -ForegroundColor Green
        }
    }
} else {
    Write-Host '[PASS] Azure RMS is activated.' -ForegroundColor Green
}

$config = Get-AipServiceConfiguration
Write-Host "`nKey Configuration:"
Write-Host "  Functional State                : $($config.FunctionalState)"
Write-Host "  License Validity (days)         : $($config.LicenseValidityDuration)"
Write-Host "  Document Tracking Enabled       : $($config.DocumentTrackingFeatureState)"
Write-Host "  IPC v3 Service Enabled          : $($config.IPCv3ServiceFeatureState)"

Disconnect-AipService
```

---

## Script 2 — Configure the Super-User Group

```powershell
<#
.SYNOPSIS
    Enables the Azure RMS super-user feature and assigns the compliance group.
.PARAMETER SuperUserGroupAddress
    Mail-enabled security group address that will receive super-user rights.
.EXAMPLE
    .\Set-RmsSuperUserGroup.ps1 -SuperUserGroupAddress 'SG-Compliance-RMS-SuperUsers@contoso.com' -WhatIf
#>
[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'High')]
param(
    [Parameter(Mandatory)] [string]$SuperUserGroupAddress
)

Connect-AipService

if ($PSCmdlet.ShouldProcess('Azure RMS', "Enable super-user feature and set group $SuperUserGroupAddress")) {
    Enable-AipServiceSuperUserFeature
    Set-AipServiceSuperUserGroup -GroupEmailAddress $SuperUserGroupAddress
    $current = Get-AipServiceSuperUserGroup
    Write-Host "[OK] Super-user group is now: $($current.SuperUserGroupEmailAddress)" -ForegroundColor Green
}

Disconnect-AipService
```

> Membership of the super-user group should be reviewed quarterly per [Control 1.18](../../../controls/pillar-1-security/1.18-application-level-authorization-and-role-based-access-control-rbac.md). Anyone in this group can decrypt every IRM-protected document in the tenant.

---

## Script 3 — Enable IRM on a SharePoint Library

```powershell
<#
.SYNOPSIS
    Enables IRM on a SharePoint document library with Zone-aware policy settings.
.PARAMETER SiteUrl
    Full URL of the SharePoint site.
.PARAMETER LibraryName
    Title of the document library (must be BaseTemplate 101).
.PARAMETER Zone
    Governance zone: 1, 2, or 3. Drives expiration, offline, print/copy defaults.
.EXAMPLE
    .\Enable-LibraryIRM.ps1 -SiteUrl 'https://contoso.sharepoint.com/sites/Advisory' `
        -LibraryName 'ClientDocuments' -Zone 3 -WhatIf
#>
[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'High')]
param(
    [Parameter(Mandatory)] [string]$SiteUrl,
    [Parameter(Mandatory)] [string]$LibraryName,
    [Parameter(Mandatory)] [ValidateSet(1, 2, 3)] [int]$Zone
)

# Map zone to settings (mirrors the control doc and portal walkthrough)
$policy = switch ($Zone) {
    1 { @{ Expire = $false; ExpireDays = 0;   AllowPrint = $true;  CredentialInterval = 30; PolicyTitle = '1.16 - Zone 1 Agent KB IRM' } }
    2 { @{ Expire = $true;  ExpireDays = 180; AllowPrint = $false; CredentialInterval = 14; PolicyTitle = '1.16 - Zone 2 Agent KB IRM' } }
    3 { @{ Expire = $true;  ExpireDays = 90;  AllowPrint = $false; CredentialInterval = 7;  PolicyTitle = '1.16 - Zone 3 Agent KB IRM' } }
}

Connect-PnPOnline -Url $SiteUrl -Interactive

$library = Get-PnPList -Identity $LibraryName -ErrorAction Stop
if ($library.BaseTemplate -ne 101) {
    throw "Library '$LibraryName' is not a document library (BaseTemplate $($library.BaseTemplate))."
}

if ($PSCmdlet.ShouldProcess("$SiteUrl/$LibraryName", "Enable IRM with Zone $Zone policy")) {
    Set-PnPList -Identity $LibraryName `
        -EnableIRM $true `
        -EnableIRMExpire $policy.Expire `
        -EnableIRMReject $true   # Reject uploads of file types that do not support IRM

    # Apply detailed policy via the IrmSettings property
    $ctx = Get-PnPContext
    $list = Get-PnPList -Identity $LibraryName -Includes IrmSettings
    $list.IrmSettings.AllowPrint                = [bool]$policy.AllowPrint
    $list.IrmSettings.AllowScript               = $false
    $list.IrmSettings.AllowWriteCopy            = $false
    $list.IrmSettings.DocumentAccessExpireDays  = [int]$policy.ExpireDays
    $list.IrmSettings.EnableDocumentAccessExpire = [bool]$policy.Expire
    $list.IrmSettings.EnableLicenseCacheExpire  = $true
    $list.IrmSettings.LicenseCacheExpireDays    = [int]$policy.CredentialInterval
    $list.IrmSettings.PolicyTitle               = $policy.PolicyTitle
    $list.IrmSettings.PolicyDescription         = "Documents downloaded from this library are protected per FSI Control 1.16 (Zone $Zone)."
    $list.IrmSettings.Update()
    $list.Update()
    $ctx.ExecuteQuery()

    Write-Host "[PASS] IRM enabled on $SiteUrl/$LibraryName (Zone $Zone)" -ForegroundColor Green
}

Disconnect-PnPOnline
```

---

## Script 4 — Tenant-Wide IRM Inventory and Drift Report

```powershell
<#
.SYNOPSIS
    Inventories every document library in the tenant and reports IRM status.
    Highlights libraries flagged as agent knowledge sources but missing IRM.
.PARAMETER AdminUrl
    SharePoint Admin Center URL (https://<tenant>-admin.sharepoint.com).
.PARAMETER AgentKbInventoryCsv
    Optional CSV with columns SiteUrl,LibraryName listing libraries that ground
    Copilot Studio agents. Libraries on this list missing IRM will be flagged FAIL.
.PARAMETER OutputPath
    Destination CSV for the report. Defaults to .\Control-1.16_IRMReport_<date>.csv
.EXAMPLE
    .\Export-IRMReport.ps1 -AdminUrl 'https://contoso-admin.sharepoint.com' `
        -AgentKbInventoryCsv .\agent-kb-libraries.csv
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string]$AdminUrl,
    [string]$AgentKbInventoryCsv,
    [string]$OutputPath = ".\Control-1.16_IRMReport_$(Get-Date -Format 'yyyyMMdd').csv"
)

$kb = @{}
if ($AgentKbInventoryCsv -and (Test-Path $AgentKbInventoryCsv)) {
    Import-Csv $AgentKbInventoryCsv | ForEach-Object {
        $kb["$($_.SiteUrl.TrimEnd('/'))|$($_.LibraryName)"] = $true
    }
}

Connect-PnPOnline -Url $AdminUrl -Interactive
$sites = Get-PnPTenantSite -Detailed | Where-Object { $_.Template -notlike 'REDIRECT*' }

$report = foreach ($site in $sites) {
    try {
        Connect-PnPOnline -Url $site.Url -Interactive -ErrorAction Stop
        $libs = Get-PnPList -Includes IrmSettings | Where-Object { $_.BaseTemplate -eq 101 -and -not $_.Hidden }
        foreach ($l in $libs) {
            $key   = "$($site.Url.TrimEnd('/'))|$($l.Title)"
            $isKb  = [bool]$kb[$key]
            $stat  = if ($l.IrmEnabled) { 'PASS' } elseif ($isKb) { 'FAIL' } else { 'INFO' }
            [PSCustomObject]@{
                SiteUrl              = $site.Url
                LibraryName          = $l.Title
                IsAgentKnowledgeBase = $isKb
                IRMEnabled           = $l.IrmEnabled
                ExpireEnabled        = $l.IrmSettings.EnableDocumentAccessExpire
                ExpireDays           = $l.IrmSettings.DocumentAccessExpireDays
                AllowPrint           = $l.IrmSettings.AllowPrint
                LicenseCacheDays     = $l.IrmSettings.LicenseCacheExpireDays
                ItemCount            = $l.ItemCount
                LastModified         = $l.LastItemModifiedDate
                Status               = $stat
            }
        }
    } catch {
        Write-Warning "Skipped $($site.Url): $($_.Exception.Message)"
    }
}

$report | Export-Csv -Path $OutputPath -NoTypeInformation
Disconnect-PnPOnline

$fails = @($report | Where-Object Status -eq 'FAIL')
$pass  = @($report | Where-Object Status -eq 'PASS')
Write-Host "`nReport: $OutputPath"
Write-Host ("  PASS (IRM enabled)                    : {0}" -f $pass.Count)  -ForegroundColor Green
Write-Host ("  FAIL (agent KB library missing IRM)   : {0}" -f $fails.Count) -ForegroundColor Red
if ($fails.Count -gt 0) { $fails | Format-Table SiteUrl, LibraryName -AutoSize }

# Emit SHA-256 evidence hash per the PowerShell baseline
$hash = (Get-FileHash -Path $OutputPath -Algorithm SHA256).Hash
Write-Host "`nSHA-256: $hash"
```

---

## Script 5 — Aggregate Validation for Control 1.16

```powershell
<#
.SYNOPSIS
    End-to-end validation harness for Control 1.16. Returns a summary object.
.EXAMPLE
    .\Validate-Control-1.16.ps1 -SuperUserGroup 'SG-Compliance-RMS-SuperUsers@contoso.com'
#>
[CmdletBinding()]
param(
    [string]$SuperUserGroup
)

$results = [ordered]@{}

# Check 1: Azure RMS activation
Connect-AipService
$results['AzureRMS_Enabled'] = ((Get-AipService) -eq 'Enabled')

# Check 2: Document tracking feature state
$cfg = Get-AipServiceConfiguration
$results['DocumentTracking_Enabled'] = ($cfg.DocumentTrackingFeatureState -eq 'Enabled')

# Check 3: Super-user feature
$results['SuperUserFeature_Enabled'] = ((Get-AipServiceSuperUserFeature) -eq 'Enabled')

# Check 4: Super-user group matches expected
if ($SuperUserGroup) {
    $current = Get-AipServiceSuperUserGroup
    $results['SuperUserGroup_Matches'] = ($current.SuperUserGroupEmailAddress -eq $SuperUserGroup)
}

Disconnect-AipService

# Surface result
$results.GetEnumerator() | ForEach-Object {
    $tag = if ($_.Value) { '[PASS]' } else { '[FAIL]' }
    $color = if ($_.Value) { 'Green' } else { 'Red' }
    Write-Host ("{0} {1,-30} = {2}" -f $tag, $_.Key, $_.Value) -ForegroundColor $color
}

[PSCustomObject]$results
```

> Library-level checks are intentionally separated into Script 4 because they require per-site connections that are slow and are best run as a scheduled drift report rather than in a synchronous validation harness.

---

[Back to Control 1.16](../../../controls/pillar-1-security/1.16-information-rights-management-irm-for-documents.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
