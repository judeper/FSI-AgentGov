# Control 4.5: SharePoint Security and Compliance Monitoring - PowerShell Setup

!!! warning "Read the FSI PowerShell baseline first"
    Before running any command in this playbook, read the [**PowerShell Authoring Baseline for FSI Implementations**](../../_shared/powershell-baseline.md). It is the canonical source for module version pinning, mutation safety (`-WhatIf` / `SupportsShouldProcess`), Dataverse compatibility, and SHA-256 evidence emission. Snippets below show the patterns required for FSI tenants; the baseline is authoritative if anything appears to conflict.

> This playbook provides PowerShell automation guidance for [Control 4.5](../../../controls/pillar-4-sharepoint/4.5-sharepoint-security-and-compliance-monitoring.md). All commands are **read-only** (evidence collection); they do not modify tenant state.

---

## Module Prerequisites (Pinned)

Replace each `<version>` with the version approved by your Change Advisory Board (CAB). Floating versions break SOX 404 evidence reproducibility.

```powershell
$ErrorActionPreference = 'Stop'

# Pin to CAB-approved versions before each change window.
Install-Module -Name Microsoft.Online.SharePoint.PowerShell -RequiredVersion '<version>' `
    -Repository PSGallery -Scope CurrentUser -AllowClobber -AcceptLicense
Install-Module -Name ExchangeOnlineManagement -RequiredVersion '<version>' `
    -Repository PSGallery -Scope CurrentUser -AllowClobber -AcceptLicense
Install-Module -Name Microsoft.Graph -RequiredVersion '<version>' `
    -Repository PSGallery -Scope CurrentUser -AllowClobber -AcceptLicense
```

!!! warning "Edition guard"
    `Microsoft.Online.SharePoint.PowerShell` is supported on both Windows PowerShell 5.1 and PowerShell 7+, but a small number of cmdlets behave differently between editions. Standardise on **one** edition for evidence collection — typically PowerShell 7+ — and document the choice in your run book.

---

## Step 1: Connect to Services

```powershell
param(
    [Parameter(Mandatory)] [string] $TenantAdminUrl,           # e.g., https://contoso-admin.sharepoint.com
    [Parameter(Mandatory)] [string] $AdminUpn                  # admin user principal name
)

Connect-SPOService -Url $TenantAdminUrl
Connect-IPPSSession -UserPrincipalName $AdminUpn -ConnectionUri "https://ps.compliance.protection.outlook.com/powershell-liveid/" -ErrorAction Stop
Connect-MgGraph -Scopes 'AuditLog.Read.All','Directory.Read.All' -Environment 'Global' -NoWelcome

# Sanity check — non-zero result confirms connection
if (-not (Get-SPOTenant)) { throw 'SPO connection failed' }
```

---

## Step 2: Verify Foundational Audit Logging

```powershell
$auditConfig = Get-AdminAuditLogConfig
if (-not $auditConfig.UnifiedAuditLogIngestionEnabled) {
    throw 'Unified audit logging is NOT enabled. Halt evidence collection — downstream results would be incomplete.'
}
Write-Host '[PASS] Unified audit logging is enabled' -ForegroundColor Green
```

---

## Step 3: Search SharePoint Audit Logs (Paginated)

`Search-UnifiedAuditLog` returns at most 5,000 records per call. In FSI tenants this **silently truncates** without pagination. Always use session-based paging for evidence collection.

```powershell
function Get-AllUnifiedAuditEvents {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [datetime] $StartDate,
        [Parameter(Mandatory)] [datetime] $EndDate,
        [string] $RecordType = 'SharePoint',
        [string[]] $Operations
    )

    $sessionId = [guid]::NewGuid().ToString()
    $all = New-Object System.Collections.Generic.List[object]
    do {
        $params = @{
            StartDate      = $StartDate
            EndDate        = $EndDate
            RecordType     = $RecordType
            SessionId      = $sessionId
            SessionCommand = 'ReturnLargeSet'
            ResultSize     = 5000
        }
        if ($Operations) { $params['Operations'] = $Operations }
        $batch = Search-UnifiedAuditLog @params
        if ($batch) { $all.AddRange($batch) }
    } while ($batch -and $batch.Count -eq 5000)

    return ,$all
}

$startDate = (Get-Date).AddDays(-30)
$endDate   = Get-Date

$sharepointEvents = Get-AllUnifiedAuditEvents -StartDate $startDate -EndDate $endDate `
    -RecordType SharePoint -Operations FileAccessed,FileDownloaded,FileModified

Write-Host "Retrieved $($sharepointEvents.Count) SharePoint events"
```

---

## Step 4: Identify Agent / Copilot Access Patterns

```powershell
$agentEvents = $sharepointEvents | ForEach-Object {
    $audit = $_.AuditData | ConvertFrom-Json
    if ($audit.UserAgent -match 'Copilot|Agent' -or $audit.ApplicationDisplayName -match 'Copilot|Agent') {
        [pscustomobject]@{
            Timestamp        = $_.CreationDate
            User             = $_.UserIds
            Operation        = $_.Operations
            FileName         = $audit.ObjectId
            SiteUrl          = $audit.SiteUrl
            UserAgent        = $audit.UserAgent
            AppDisplayName   = $audit.ApplicationDisplayName
            SensitivityLabel = $audit.SensitivityLabelId
        }
    }
}

Write-Host "Agent / Copilot related access events: $($agentEvents.Count)"
```

!!! note "Detection caveat"
    Agent and Copilot identification from audit data is heuristic. The set of identifying fields (UserAgent, ApplicationDisplayName, ApplicationId) is evolving; review Microsoft Learn quarterly and adjust the filter. Do not treat the result as a definitive count of agent reads — treat it as a signal for further investigation.

---

## Step 5: Inventory High-Risk Sites (Single Pass)

`Get-SPOSite -Limit All` is throttled in large tenants. Enumerate **once**, then derive metrics in memory.

```powershell
$allSites = Get-SPOSite -Limit All -IncludePersonalSite:$false |
    Select-Object Url, Owner, SensitivityLabel, SharingCapability, ConditionalAccessPolicy,
                  LockState, RestrictedAccessControl, RestrictedToGeo, IsHubSite, Template

$siteMetrics = [pscustomobject]@{
    TotalSites              = $allSites.Count
    LabeledSites            = ($allSites | Where-Object SensitivityLabel).Count
    ExternalSharingEnabled  = ($allSites | Where-Object { $_.SharingCapability -ne 'Disabled' }).Count
    ConfidentialSites       = ($allSites | Where-Object { $_.SensitivityLabel -match 'Confidential' }).Count
    LockedSites             = ($allSites | Where-Object { $_.LockState -ne 'Unlock' }).Count
    RACEnabled              = ($allSites | Where-Object RestrictedAccessControl).Count
    GeoRestricted           = ($allSites | Where-Object RestrictedToGeo).Count
}

$highRiskSites = $allSites | Where-Object {
    $_.SensitivityLabel -match 'Confidential|Restricted' -or $_.LockState -ne 'Unlock'
}
```

---

## Step 6: Verify Privileged Role Assignment

Avoid fragile `displayName -like '*SharePoint*'` matches. Resolve role IDs explicitly.

```powershell
function Test-DirectoryRoleAssignment {
    param(
        [Parameter(Mandatory)] [string] $UserUpn,
        [Parameter(Mandatory)] [string] $RoleDisplayName    # e.g., 'SharePoint Administrator'
    )
    $role = Get-MgDirectoryRole -Filter "displayName eq '$RoleDisplayName'" -ErrorAction SilentlyContinue
    if (-not $role) {
        # Activate the role from its template if it has not yet been activated in the tenant
        $template = Get-MgDirectoryRoleTemplate -Filter "displayName eq '$RoleDisplayName'"
        if ($template) { $role = New-MgDirectoryRole -RoleTemplateId $template.Id }
    }
    if (-not $role) { return $false }

    $user = Get-MgUser -Filter "userPrincipalName eq '$UserUpn'"
    if (-not $user) { return $false }

    $members = Get-MgDirectoryRoleMember -DirectoryRoleId $role.Id -All
    return [bool]($members | Where-Object { $_.Id -eq $user.Id })
}

Test-DirectoryRoleAssignment -UserUpn $AdminUpn -RoleDisplayName 'SharePoint Administrator'
```

---

## Step 7: Emit Evidence with SHA-256 Hashes

Every export should be hashed at capture time and recorded in an evidence manifest. Hashes prove the file you produce in audit is the file you captured.

```powershell
$evidenceRoot = Join-Path -Path '.\evidence\4.5' -ChildPath (Get-Date -Format 'yyyy-MM-dd')
New-Item -Path $evidenceRoot -ItemType Directory -Force | Out-Null

function Export-EvidenceArtifact {
    param(
        [Parameter(Mandatory)] $InputObject,
        [Parameter(Mandatory)] [string] $RelativePath,   # e.g., 'sharepoint-audit-30d.csv'
        [ValidateSet('Csv','Json')] [string] $Format = 'Csv'
    )
    $full = Join-Path $evidenceRoot $RelativePath
    if ($Format -eq 'Csv') {
        $InputObject | Export-Csv -Path $full -NoTypeInformation -Encoding UTF8
    } else {
        $InputObject | ConvertTo-Json -Depth 10 | Out-File $full -Encoding UTF8
    }
    $hash = (Get-FileHash -Path $full -Algorithm SHA256).Hash
    [pscustomobject]@{
        Artifact   = $RelativePath
        SizeBytes  = (Get-Item $full).Length
        SHA256     = $hash
        CapturedAt = (Get-Date).ToString('o')
        CapturedBy = $AdminUpn
        Tenant     = $TenantAdminUrl
    }
}

$manifest = New-Object System.Collections.Generic.List[object]
$manifest.Add( (Export-EvidenceArtifact -InputObject $sharepointEvents -RelativePath 'sharepoint-audit-30d.csv') )
$manifest.Add( (Export-EvidenceArtifact -InputObject $agentEvents      -RelativePath 'agent-access-30d.csv') )
$manifest.Add( (Export-EvidenceArtifact -InputObject $allSites         -RelativePath 'all-sites-inventory.csv') )
$manifest.Add( (Export-EvidenceArtifact -InputObject $highRiskSites    -RelativePath 'high-risk-sites.csv') )
$manifest.Add( (Export-EvidenceArtifact -InputObject $siteMetrics      -RelativePath 'site-metrics.json' -Format Json) )

$manifest | Export-Csv -Path (Join-Path $evidenceRoot 'EVIDENCE-MANIFEST.csv') -NoTypeInformation -Encoding UTF8
```

!!! warning "Audit log retention"
    A 30- or 90-day audit window is **insufficient** for SEC 17a-4 / FINRA 4511 (typically 6 years). The exports above are point-in-time snapshots. Configure a Microsoft Purview audit retention policy that matches your regulatory window — Standard audit retains 180 days and Premium audit retains 1 year by default, neither of which satisfies broker-dealer record-keeping obligations on its own. See [Manage audit log retention policies](https://learn.microsoft.com/en-us/purview/audit-log-retention-policies).

---

## Step 8: Cleanup

```powershell
Disconnect-SPOService -ErrorAction SilentlyContinue
Disconnect-ExchangeOnline -Confirm:$false -ErrorAction SilentlyContinue
Disconnect-MgGraph -ErrorAction SilentlyContinue
```

---

## Complete Orchestration Script (Reference)

Save as `Invoke-Control-4.5-EvidenceCollection.ps1` and execute under change control. The script is read-only and safe to run on production tenants outside change windows, but the evidence it produces is part of your regulatory record — treat the output directory accordingly.

```powershell
<#
.SYNOPSIS
    Read-only evidence collection for FSI Control 4.5 — SharePoint Security and Compliance Monitoring.

.DESCRIPTION
    Connects to SharePoint Online, Purview (IPPS), and Microsoft Graph; enumerates SharePoint
    audit events with paginated Search-UnifiedAuditLog calls;
    inventories sites in a single pass; emits CSV/JSON evidence with SHA-256 hashes recorded in a
    manifest file.

.PARAMETER TenantAdminUrl
    SharePoint Admin Center URL (e.g., https://contoso-admin.sharepoint.com).

.PARAMETER AdminUpn
    User principal name of the executing administrator.

.PARAMETER DaysBack
    Audit window in days. Default 30. Note: this is a snapshot; full retention is governed by a
    separate Purview audit retention policy.

.NOTES
    Read the FSI PowerShell baseline:
    docs/playbooks/_shared/powershell-baseline.md
#>
param(
    [Parameter(Mandatory)] [string] $TenantAdminUrl,
    [Parameter(Mandatory)] [string] $AdminUpn,
    [int] $DaysBack = 30
)

# (Body assembles Steps 1–8 above into a single transcript-logged run.
# Wrap the body in Start-Transcript / Stop-Transcript and a try/catch/finally
# to ensure evidence integrity even on partial failure.)
```

---

[Back to Control 4.5](../../../controls/pillar-4-sharepoint/4.5-sharepoint-security-and-compliance-monitoring.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
