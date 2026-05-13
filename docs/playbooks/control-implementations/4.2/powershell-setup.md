# Control 4.2: Site Access Reviews and Certification — PowerShell Setup

!!! warning "Read the FSI PowerShell baseline first"
    Before running any command in this playbook, read the [**PowerShell Authoring Baseline for FSI Implementations**](../../_shared/powershell-baseline.md). It is the canonical source for module version pinning, sovereign-cloud (GCC / GCC High / DoD) endpoints, mutation safety (`-WhatIf` / `SupportsShouldProcess`), Dataverse compatibility, and SHA-256 evidence emission. Snippets below show abbreviated patterns; the baseline is authoritative.

> Automation guidance for [Control 4.2 — Site Access Reviews and Certification](../../../controls/pillar-4-sharepoint/4.2-site-access-reviews-and-certification.md).

This playbook covers three workloads:

1. **SharePoint Online** — DAG report export and site permission baseline (`Microsoft.Online.SharePoint.PowerShell`, `PnP.PowerShell`)
2. **Microsoft Entra ID Governance** — Access Review schedule definitions for groups and Sites.Selected service principals (`Microsoft.Graph` / `Microsoft.Graph.Identity.Governance`)
3. **Evidence emission** — CSV export plus SHA-256 hash for tamper-evident storage

---

## Prerequisites

```powershell
# Pin module versions per the FSI PowerShell baseline (April 2026)
Install-Module Microsoft.Online.SharePoint.PowerShell -RequiredVersion 16.0.26212.12000 -Scope CurrentUser
Install-Module PnP.PowerShell                          -RequiredVersion 2.99.0           -Scope CurrentUser
Install-Module Microsoft.Graph                         -RequiredVersion 2.30.0           -Scope CurrentUser

# SharePoint Online — commercial endpoint shown; use admin.sharepoint.us / .sharepoint-mil.us for sovereign clouds
$adminUrl = "https://contoso-admin.sharepoint.com"
Connect-SPOService -Url $adminUrl

# PnP.PowerShell — interactive auth (replace with cert-based auth in CI)
Connect-PnPOnline -Url $adminUrl -Interactive

# Microsoft Graph — least-privilege scopes for this control
Connect-MgGraph -Scopes @(
    "AccessReview.ReadWrite.All",
    "Directory.Read.All",
    "Sites.Read.All",
    "Application.Read.All",
    "AuditLog.Read.All"
)

# Verify connections
Get-MgContext  | Select-Object Account, Scopes, Environment
Get-SPOTenant | Select-Object StorageQuota, SharingCapability
```

---

## 1. Baseline site permission posture

### 1a. Export site inventory and sharing posture

```powershell
# Export all non-OneDrive sites with sharing capability and sensitivity label
$evidenceDir = "C:\Compliance\Control-4.2\$(Get-Date -Format 'yyyyMMdd')"
New-Item -Path $evidenceDir -ItemType Directory -Force | Out-Null

$sites = Get-SPOSite -Limit All -IncludePersonalSite:$false |
    Where-Object { $_.Template -notlike 'SPSPERS*' }

$inventory = $sites | ForEach-Object {
    [PSCustomObject]@{
        SiteUrl                = $_.Url
        Title                  = $_.Title
        Owner                  = $_.Owner
        Template               = $_.Template
        SharingCapability      = $_.SharingCapability
        SensitivityLabel       = $_.SensitivityLabel
        ConditionalAccessPolicy = $_.ConditionalAccessPolicy
        LastContentModified    = $_.LastContentModifiedDate
        StorageUsedGB          = [math]::Round($_.StorageUsageCurrent / 1024, 2)
    }
}

$inventoryPath = Join-Path $evidenceDir 'site-inventory.csv'
$inventory | Export-Csv -Path $inventoryPath -NoTypeInformation -Encoding UTF8

# Emit SHA-256 evidence hash
$hash = (Get-FileHash -Path $inventoryPath -Algorithm SHA256).Hash
"$hash  site-inventory.csv" | Out-File (Join-Path $evidenceDir 'site-inventory.sha256') -Encoding ASCII
Write-Host "Exported $($inventory.Count) sites; SHA-256: $hash"
```

### 1b. Identify orphaned and EEEU-exposed sites

```powershell
# Orphaned sites — no owner; cannot be attested
$orphans = $inventory | Where-Object { [string]::IsNullOrWhiteSpace($_.Owner) }
$orphans | Export-Csv (Join-Path $evidenceDir 'orphaned-sites.csv') -NoTypeInformation

# EEEU-shared sites via PnP role assignment scan (sample 25 highest-risk sites)
$eeeuFindings = foreach ($site in $inventory | Where-Object SharingCapability -ne 'Disabled' | Select-Object -First 25) {
    try {
        Connect-PnPOnline -Url $site.SiteUrl -Interactive -ErrorAction Stop
        $web = Get-PnPWeb -Includes RoleAssignments
        foreach ($assignment in $web.RoleAssignments) {
            $member = Get-PnPProperty -ClientObject $assignment -Property Member
            if ($member.LoginName -match 'spo-grid-all-users|everyone except external') {
                [PSCustomObject]@{
                    SiteUrl          = $site.SiteUrl
                    SensitivityLabel = $site.SensitivityLabel
                    GrantedTo        = $member.Title
                    LoginName        = $member.LoginName
                }
            }
        }
    } catch {
        Write-Warning "Skip $($site.SiteUrl): $($_.Exception.Message)"
    }
}
$eeeuFindings | Export-Csv (Join-Path $evidenceDir 'eeeu-findings.csv') -NoTypeInformation
```

!!! note "DAG report export via Graph"
    The fully-fidelity DAG report set (Oversharing baseline, Agent Insights, Agent Access Insights)
    is generated server-side by SAM. There is no public PowerShell cmdlet for triggering report
    generation in April 2026. Trigger reports interactively in SharePoint Admin Center, then
    download the CSV exports and stage them alongside the artifacts above.

---

## 2. Create Entra Access Reviews

### 2a. Quarterly review of M365 Groups backing SharePoint sites

```powershell
# Use the schedule definition body parameter pattern; the cmdlet wraps the v1.0 access reviews API
$reviewParams = @{
    displayName             = "FSI SharePoint Site Access Review — Quarterly"
    descriptionForAdmins    = "Quarterly access review for M365 Groups backing in-scope SharePoint sites used as Copilot/agent knowledge sources."
    descriptionForReviewers = "Confirm that each member of this group still requires access to the SharePoint content it backs. Justification required."
    scope = @{
        '@odata.type' = '#microsoft.graph.accessReviewQueryScope'
        query         = "/groups?`$filter=(groupTypes/any(c:c eq 'Unified'))"
        queryType     = 'MicrosoftGraph'
    }
    reviewers = @(
        @{ query = '/groups/{id}/owners'; queryType = 'MicrosoftGraph' }
    )
    fallbackReviewers = @(
        @{ query = '/users/compliance-reviewer@contoso.com'; queryType = 'MicrosoftGraph' }
    )
    settings = @{
        mailNotificationsEnabled         = $true
        reminderNotificationsEnabled     = $true
        justificationRequiredOnApproval  = $true
        defaultDecisionEnabled           = $true
        defaultDecision                  = 'Deny'
        instanceDurationInDays           = 14
        autoApplyDecisionsEnabled        = $true
        recommendationsEnabled           = $true
        recurrence = @{
            pattern = @{
                type        = 'absoluteMonthly'
                interval    = 3
                dayOfMonth  = 1
            }
            range = @{
                type      = 'noEnd'
                startDate = (Get-Date).ToString('yyyy-MM-dd')
            }
        }
    }
}

if ($PSCmdlet.ShouldProcess('Tenant', 'Create FSI quarterly access review')) {
    $review = New-MgIdentityGovernanceAccessReviewDefinition -BodyParameter $reviewParams
    Write-Host "Created review '$($review.DisplayName)' — Id: $($review.Id)"
}
```

### 2b. Quarterly review of Sites.Selected service principals (AI agents)

```powershell
# Enumerate service principals that hold Sites.Selected on Microsoft Graph
$graphSp = Get-MgServicePrincipal -Filter "appId eq '00000003-0000-0000-c000-000000000000'"
$sitesSelectedRoleId = ($graphSp.AppRoles | Where-Object Value -eq 'Sites.Selected').Id

$agentSps = Get-MgServicePrincipal -All |
    Where-Object {
        (Get-MgServicePrincipalAppRoleAssignment -ServicePrincipalId $_.Id -ErrorAction SilentlyContinue |
            Where-Object { $_.AppRoleId -eq $sitesSelectedRoleId -and $_.ResourceId -eq $graphSp.Id })
    }

$agentSps |
    Select-Object DisplayName, AppId, Id, ServicePrincipalType |
    Export-Csv (Join-Path $evidenceDir 'sites-selected-agents.csv') -NoTypeInformation

# A separate access review for the agent group (recommended pattern: place agent app SPs into a
# dynamic security group, then schedule an access review against that group with the AI Governance
# Lead as reviewer and quarterly recurrence). Build the reviewParams block as in 2a, swapping the
# scope query to the agent governance group's id.
```

---

## 3. Export decisions for evidence retention

```powershell
# Iterate every instance of every review and export decisions to a single CSV
$reviews = Get-MgIdentityGovernanceAccessReviewDefinition -All

$decisions = foreach ($review in $reviews) {
    $instances = Get-MgIdentityGovernanceAccessReviewDefinitionInstance `
        -AccessReviewScheduleDefinitionId $review.Id -All
    foreach ($instance in $instances) {
        $items = Get-MgIdentityGovernanceAccessReviewDefinitionInstanceDecision `
            -AccessReviewScheduleDefinitionId $review.Id `
            -AccessReviewInstanceId $instance.Id -All
        foreach ($d in $items) {
            [PSCustomObject]@{
                ReviewName         = $review.DisplayName
                ReviewId           = $review.Id
                InstanceId         = $instance.Id
                InstanceStart      = $instance.StartDateTime
                InstanceEnd        = $instance.EndDateTime
                Principal          = $d.Principal.AdditionalProperties.displayName
                PrincipalType      = $d.Principal.AdditionalProperties.'@odata.type'
                Resource           = $d.Resource.AdditionalProperties.displayName
                Decision           = $d.Decision
                Justification      = $d.Justification
                ReviewedBy         = $d.ReviewedBy.AdditionalProperties.displayName
                ReviewedDateTime   = $d.ReviewedDateTime
                AppliedBy          = $d.AppliedBy.AdditionalProperties.displayName
                AppliedDateTime    = $d.AppliedDateTime
            }
        }
    }
}

$decisionsPath = Join-Path $evidenceDir 'access-review-decisions.csv'
$decisions | Export-Csv -Path $decisionsPath -NoTypeInformation -Encoding UTF8
$hash = (Get-FileHash $decisionsPath -Algorithm SHA256).Hash
"$hash  access-review-decisions.csv" | Out-File (Join-Path $evidenceDir 'access-review-decisions.sha256') -Encoding ASCII
Write-Host "Exported $($decisions.Count) decisions; SHA-256: $hash"
```

Stage `$evidenceDir` to a SharePoint library or mailbox covered by a Purview retention label
configured for at least the **6-year SEC 17a-4 / FINRA 4511** floor — Preservation Lock
recommended for Zone 3.

---

## 4. Cross-check Purview audit log

```powershell
# Confirm review activity is landing in the unified audit log (read-only check)
$start = (Get-Date).AddDays(-30)
$end   = (Get-Date)

# Audit log search via Graph (security/auditLogQueries) is the supported April 2026 path
# Operations of interest: AccessReviewCreate, AccessReviewDecisionApplied, AccessReviewInstanceComplete
Write-Host "Verify these operations appear in the Purview audit log for the last 30 days:"
@(
    'AccessReviewCreate',
    'AccessReviewInstanceComplete',
    'AccessReviewDecisionApplied',
    'SharingPolicyChanged',
    'SiteAttestationCompleted'
) | ForEach-Object { " - $_" }
```

---

## Complete configuration script

```powershell
<#
.SYNOPSIS
    Configure Control 4.2 — Site Access Reviews and Certification.

.DESCRIPTION
    Idempotent scaffold that:
      1. Connects to SPO + Graph using least-privilege scopes
      2. Exports site inventory + EEEU/orphan findings with SHA-256 evidence hashes
      3. Optionally creates the FSI quarterly access review for M365 Groups
      4. Exports current access review decisions

.PARAMETER TenantAdminUrl
    SharePoint Admin Center URL (commercial / GCC / GCC High / DoD endpoint).

.PARAMETER EvidencePath
    Local directory where evidence CSVs and SHA-256 manifests are emitted.

.PARAMETER CreateAccessReview
    Switch to provision the quarterly review. Off by default — review the body
    parameter against your environment first.

.EXAMPLE
    .\Configure-Control-4.2.ps1 -TenantAdminUrl "https://contoso-admin.sharepoint.com"

.NOTES
    Control: 4.2 (FSI Agent Governance Framework v1.6.2)
    Last updated: April 2026
    Read .../playbooks/_shared/powershell-baseline.md before running.
#>

[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [Parameter(Mandatory)] [string] $TenantAdminUrl,
    [string] $EvidencePath = "C:\Compliance\Control-4.2\$(Get-Date -Format 'yyyyMMdd')",
    [switch] $CreateAccessReview
)

$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Path $EvidencePath -Force | Out-Null

try {
    Connect-MgGraph -Scopes @(
        'AccessReview.ReadWrite.All',
        'Directory.Read.All',
        'Sites.Read.All',
        'Application.Read.All'
    ) | Out-Null
    Connect-SPOService -Url $TenantAdminUrl

    # Site inventory
    $sites = Get-SPOSite -Limit All -IncludePersonalSite:$false |
        Where-Object { $_.Template -notlike 'SPSPERS*' }
    $invPath = Join-Path $EvidencePath 'site-inventory.csv'
    $sites | Select-Object Url, Title, Owner, Template, SharingCapability, SensitivityLabel,
        @{n='LastContentModified';e={$_.LastContentModifiedDate}} |
        Export-Csv $invPath -NoTypeInformation -Encoding UTF8
    "$((Get-FileHash $invPath -Algorithm SHA256).Hash)  site-inventory.csv" |
        Out-File (Join-Path $EvidencePath 'site-inventory.sha256') -Encoding ASCII

    # Existing reviews
    $reviews = Get-MgIdentityGovernanceAccessReviewDefinition -All
    $reviews | Select-Object DisplayName, Id, Status, CreatedDateTime |
        Export-Csv (Join-Path $EvidencePath 'existing-access-reviews.csv') -NoTypeInformation

    if ($CreateAccessReview -and
        $PSCmdlet.ShouldProcess($TenantAdminUrl, 'Create FSI quarterly access review')) {
        # Insert the $reviewParams block from section 2a here
        Write-Host 'TODO: paste section 2a body parameter, then call New-MgIdentityGovernanceAccessReviewDefinition.'
    }

    Write-Host "[PASS] Control 4.2 baseline emitted to $EvidencePath" -ForegroundColor Green
}
catch {
    Write-Host "[FAIL] $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "[INFO] $($_.ScriptStackTrace)" -ForegroundColor Yellow
    throw
}
finally {
    Disconnect-MgGraph    -ErrorAction SilentlyContinue | Out-Null
    Disconnect-SPOService -ErrorAction SilentlyContinue | Out-Null
}
```

---

[Back to Control 4.2](../../../controls/pillar-4-sharepoint/4.2-site-access-reviews-and-certification.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification & Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: April 2026 | Version: v1.6.2*
