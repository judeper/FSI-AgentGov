# Control 4.4: Guest and External User Access Controls — PowerShell Setup

!!! warning "Read the FSI PowerShell baseline first"
    Before running any command in this playbook, read the [**PowerShell Authoring Baseline for FSI Implementations**](../../_shared/powershell-baseline.md). It is the canonical source for module version pinning, sovereign-cloud (GCC / GCC High / DoD) endpoints, mutation safety (`-WhatIf` / `SupportsShouldProcess`), Dataverse compatibility, and SHA-256 evidence emission. Snippets below show the abbreviated patterns; the baseline is authoritative.

> This playbook provides PowerShell automation guidance for [Control 4.4](../../../controls/pillar-4-sharepoint/4.4-guest-and-external-user-access-controls.md).

---

## Prerequisites

| Module | Purpose | Pinning guidance |
|--------|---------|------------------|
| `Microsoft.Online.SharePoint.PowerShell` | Tenant + site sharing configuration | Pin to a CAB-approved version; some cmdlets behave differently on PS 5.1 vs PS 7 (verify per the baseline) |
| `Microsoft.Graph.Users` | Replacement for retired `Remove-SPOExternalUser` | Pin to the meta-module minor version used elsewhere in your tenant |
| `ExchangeOnlineManagement` | `Search-UnifiedAuditLog` for sharing-event audit | Pin and use session-paginated queries (5,000-record limit) |

```powershell
# Use the canonical pinned-install pattern from the FSI baseline.
# Replace <version> with the version approved by your CAB.
Install-Module -Name Microsoft.Online.SharePoint.PowerShell `
    -RequiredVersion '<version>' -Repository PSGallery -Scope CurrentUser -AllowClobber -AcceptLicense
Install-Module -Name Microsoft.Graph.Users `
    -RequiredVersion '<version>' -Repository PSGallery -Scope CurrentUser -AllowClobber -AcceptLicense
Install-Module -Name ExchangeOnlineManagement `
    -RequiredVersion '<version>' -Repository PSGallery -Scope CurrentUser -AllowClobber -AcceptLicense
```

---

## Sovereign-aware connection (Commercial / GCC / GCC High / DoD)

Per the baseline, sovereign-cloud tenants must pass explicit endpoint parameters or risk **false-clean evidence** from queries hitting the wrong cloud.

```powershell
param(
    [Parameter(Mandatory)] [string]$TenantName,                 # e.g., "contoso" -> contoso-admin.sharepoint.com
    [ValidateSet('Commercial','GCC','GCCHigh','DoD')] [string]$Cloud = 'Commercial'
)

# SharePoint admin URL pattern by cloud (verify on Microsoft Learn for current values)
$adminHost = switch ($Cloud) {
    'Commercial' { "$TenantName-admin.sharepoint.com" }
    'GCC'        { "$TenantName-admin.sharepoint.com" }
    'GCCHigh'    { "$TenantName-admin.sharepoint.us" }
    'DoD'        { "$TenantName-admin.dps.mil" }
}
Connect-SPOService -Url "https://$adminHost"

# Microsoft Graph connection for guest user lifecycle
$graphEnv = @{ Commercial='Global'; GCC='USGov'; GCCHigh='USGovDoD'; DoD='USGovDoD' }[$Cloud]
Connect-MgGraph -Environment $graphEnv -Scopes 'User.ReadWrite.All','Directory.Read.All'
```

---

## Read-only inventory (safe to run anytime)

```powershell
# Tenant-level sharing posture
Get-SPOTenant | Select-Object `
    SharingCapability, `
    SharingDomainRestrictionMode, `
    SharingAllowedDomainList, `
    SharingBlockedDomainList, `
    DefaultSharingLinkType, `
    DefaultLinkPermission, `
    RequireAnonymousLinksExpireInDays, `
    ExternalUserExpirationRequired, `
    ExternalUserExpireInDays, `
    PreventExternalUsersFromResharing, `
    CoreDefaultShareLinkScope, `
    OneDriveDefaultShareLinkScope

# Per-site posture for an inventoried subset
$sites = Import-Csv -Path '.\zone3-sites.csv'  # Url,Zone columns
$sites | ForEach-Object {
    Get-SPOSite -Identity $_.Url -ErrorAction SilentlyContinue |
        Select-Object Url, SharingCapability, DisableSharingForNonOwnersStatus, ExternalUserExpirationInDays
} | Export-Csv -Path ".\evidence\4.4\site-posture-$(Get-Date -Format 'yyyyMMdd').csv" -NoTypeInformation
```

!!! note "`CoreDefaultShareLinkScope` and `OneDriveDefaultShareLinkScope`"
    Newer SharePoint tenants expose `CoreDefaultShareLinkScope` and `OneDriveDefaultShareLinkScope` as the modern replacements for `DefaultSharingLinkType`. Both values are surfaced through `Get-SPOTenant`. Inspect both when documenting baseline state — Microsoft is gradually transitioning configuration semantics from the legacy parameter to the scoped parameters.

---

## Tenant-level configuration (mutating — requires change control)

This is a **tenant-affecting** mutation. Follow the baseline's mutation-safety pattern: declare `SupportsShouldProcess`, snapshot state before changes, run with `-WhatIf` first, and emit hashed evidence.

```powershell
[CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
param(
    [Parameter(Mandatory)] [string]$AdminUrl,
    [string]$EvidencePath = '.\evidence\4.4'
)

$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force -Path $EvidencePath | Out-Null
$ts = Get-Date -Format 'yyyyMMdd-HHmmss'
Start-Transcript -Path "$EvidencePath\tenant-mutation-$ts.log" -IncludeInvocationHeader

Connect-SPOService -Url $AdminUrl

# Snapshot BEFORE mutating (rollback evidence)
$before = Get-SPOTenant
$before | ConvertTo-Json -Depth 10 | Set-Content "$EvidencePath\tenant-before-$ts.json"

if ($PSCmdlet.ShouldProcess($AdminUrl, 'Apply Control 4.4 tenant sharing baseline')) {
    Set-SPOTenant `
        -SharingCapability ExistingExternalUserSharingOnly `
        -DefaultSharingLinkType Direct `
        -DefaultLinkPermission View `
        -RequireAnonymousLinksExpireInDays 30 `
        -ExternalUserExpirationRequired $true `
        -ExternalUserExpireInDays 30 `
        -PreventExternalUsersFromResharing $true
}

# Snapshot AFTER + integrity hash
$after = Get-SPOTenant
$afterPath = "$EvidencePath\tenant-after-$ts.json"
$after | ConvertTo-Json -Depth 10 | Set-Content $afterPath
$hash = (Get-FileHash -Path $afterPath -Algorithm SHA256).Hash
"{ ""file"": ""$(Split-Path $afterPath -Leaf)"", ""sha256"": ""$hash"", ""generated_utc"": ""$ts"" }" |
    Add-Content -Path "$EvidencePath\manifest.json"

Stop-Transcript
```

!!! danger "Always run with -WhatIf first"
    `Set-SPOTenant -SharingCapability` propagates within minutes and can disconnect active guest sessions on every site that previously inherited a more permissive value. Run with `-WhatIf`, communicate the change window, and have a rollback plan that re-applies the snapshot file.

### Optional: domain allow-list

```powershell
# Run AFTER the SharingCapability change has propagated (typically 5-15 minutes)
Set-SPOTenant `
    -SharingDomainRestrictionMode AllowList `
    -SharingAllowedDomainList 'approvedpartner.com trustedvendor.com regulator.gov'
```

---

## Site-level configuration per zone

```powershell
[CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
param(
    [Parameter(Mandatory)] [string]$SiteCsvPath,    # Columns: Url, Zone
    [string]$EvidencePath = '.\evidence\4.4'
)

$sites = Import-Csv -Path $SiteCsvPath
$ts = Get-Date -Format 'yyyyMMdd-HHmmss'
$results = @()

foreach ($row in $sites) {
    try {
        $before = Get-SPOSite -Identity $row.Url -ErrorAction Stop
        $action = switch ($row.Zone) {
            '3' { @{ SharingCapability = 'Disabled' } }
            '2' { @{ SharingCapability = 'ExistingExternalUserSharingOnly'; ExternalUserExpirationInDays = 30; DisableSharingForNonOwnersStatus = $true } }
            '1' { @{ SharingCapability = 'ExternalUserSharingOnly'; ExternalUserExpirationInDays = 90 } }
            default { $null }
        }
        if (-not $action) { continue }

        if ($PSCmdlet.ShouldProcess($row.Url, "Apply Zone $($row.Zone) sharing baseline")) {
            Set-SPOSite -Identity $row.Url @action
            $after = Get-SPOSite -Identity $row.Url
            $results += [pscustomobject]@{
                Url = $row.Url; Zone = $row.Zone
                Before = $before.SharingCapability; After = $after.SharingCapability
                Status = 'Applied'
            }
        }
    } catch {
        $results += [pscustomobject]@{
            Url = $row.Url; Zone = $row.Zone
            Before = $null; After = $null
            Status = "Failed: $($_.Exception.Message)"
        }
    }
}

$out = "$EvidencePath\site-changes-$ts.csv"
$results | Export-Csv -Path $out -NoTypeInformation
"{ ""file"": ""$(Split-Path $out -Leaf)"", ""sha256"": ""$((Get-FileHash $out -Algorithm SHA256).Hash)"", ""generated_utc"": ""$ts"" }" |
    Add-Content -Path "$EvidencePath\manifest.json"
```

---

## Guest user inventory and lifecycle

`Remove-SPOExternalUser` was retired by Microsoft on **July 29, 2024**. Use Microsoft Graph PowerShell (`Remove-MgUser`) for guest removal going forward.

```powershell
# Tenant-wide external user inventory (paged)
$externalUsers = @()
$page = Get-SPOExternalUser -PageSize 50 -Position 0
while ($page) {
    $externalUsers += $page
    if ($page.Count -lt 50) { break }
    $page = Get-SPOExternalUser -PageSize 50 -Position ($externalUsers.Count)
}
$externalUsers | Select-Object DisplayName, Email, AcceptedAs, WhenCreated, InvitedBy |
    Export-Csv -Path ".\evidence\4.4\external-users-$(Get-Date -Format 'yyyyMMdd').csv" -NoTypeInformation

# Remove a specific external user (replacement for Remove-SPOExternalUser)
# Requires Microsoft.Graph.Users with User.ReadWrite.All
$guest = Get-MgUser -Filter "userType eq 'Guest' and mail eq 'user@external.com'"
if ($guest) {
    if ($PSCmdlet.ShouldProcess($guest.UserPrincipalName, 'Remove guest user')) {
        Remove-MgUser -UserId $guest.Id
    }
}
```

---

## Audit-log query for sharing events

```powershell
Connect-IPPSSession    # Security & Compliance PowerShell

$sessionId = [guid]::NewGuid().ToString()
$startDate = (Get-Date).AddDays(-30)
$endDate   = Get-Date
$events    = @()
do {
    $batch = Search-UnifiedAuditLog -StartDate $startDate -EndDate $endDate `
        -RecordType SharePointSharingOperation `
        -SessionId $sessionId -SessionCommand ReturnLargeSet -ResultSize 5000
    $events += $batch
} while ($batch.Count -eq 5000)

$events | Select-Object CreationDate, UserIds, Operations, AuditData |
    Export-Csv -Path ".\evidence\4.4\sharing-events-$(Get-Date -Format 'yyyyMMdd').csv" -NoTypeInformation
```

!!! warning "Pagination is mandatory in FSI tenants"
    A single `Search-UnifiedAuditLog` call returns at most 5,000 records and **silently truncates** beyond that. The pagination loop above is the audit-defensible pattern.

---

## Rollback

If a tenant or site change must be reverted:

1. Locate the most recent `tenant-before-*.json` (or `site-changes-*.csv`) under `evidence\4.4\`.
2. For tenant changes, re-apply the snapshot values via `Set-SPOTenant` using the captured property values.
3. For site changes, run the bulk site script again with `Zone` column values that map to the prior `Before` `SharingCapability`.
4. Document the rollback in the original change ticket.

---

[Back to Control 4.4](../../../controls/pillar-4-sharepoint/4.4-guest-and-external-user-access-controls.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: April 2026 | Version: v1.6.2 | UI Verification Status: Current*
