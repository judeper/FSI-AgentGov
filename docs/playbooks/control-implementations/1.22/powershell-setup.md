# PowerShell Setup: Control 1.22 — Information Barriers for AI Agents

!!! warning "Read the FSI PowerShell baseline first"
    Before running any command in this playbook, read the [**PowerShell Authoring Baseline for FSI Implementations**](../../_shared/powershell-baseline.md). It is the canonical source for module version pinning, sovereign-cloud (GCC / GCC High / DoD) endpoints, mutation safety (`-WhatIf` / `SupportsShouldProcess`), Dataverse compatibility, and SHA-256 evidence emission. Snippets below show abbreviated patterns; the baseline is authoritative.

**Last Updated:** April 2026
**Modules Required:** `ExchangeOnlineManagement` (Compliance PowerShell — `Connect-IPPSSession`), `Microsoft.Graph` (for HR-of-record attribute reads and segment-coverage reporting), optional `PnP.PowerShell` v2+ (for SharePoint site-segment validation)

---

## Prerequisites

```powershell
# Pin module versions in regulated tenants. Substitute CAB-approved versions.
Install-Module -Name ExchangeOnlineManagement -RequiredVersion '<approved-version>' `
    -Repository PSGallery -Scope CurrentUser -AllowClobber -AcceptLicense

Install-Module -Name Microsoft.Graph -RequiredVersion '<approved-version>' `
    -Repository PSGallery -Scope CurrentUser -AllowClobber -AcceptLicense

# Optional, for SharePoint site-segment validation:
Install-Module -Name PnP.PowerShell -RequiredVersion '<approved-version>' `
    -Repository PSGallery -Scope CurrentUser -AllowClobber -AcceptLicense
```

> Compliance PowerShell (`Connect-IPPSSession`) is **Windows PowerShell 5.1 Desktop edition** for some IB cmdlets and **PowerShell 7+** for others depending on the `ExchangeOnlineManagement` build. Verify the cmdlet's edition requirement before automating.

> All snippets assume an interactive admin session. For unattended automation, use a certificate-based service principal with the **Compliance Administrator** role or the **Information Barriers Manager** role assignment.

---

## Script 1 — Pre-Change Baseline Capture

Always capture state **before** modifying IB. This output is the rollback reference and the evidence baseline for change control (FINRA 3110, SOX 404).

```powershell
<#
.SYNOPSIS
    Captures Information Barriers baseline state for Control 1.22 evidence.

.DESCRIPTION
    Records IB mode, segments, policies, and last application status.
    Writes timestamped CSV/JSON outputs and emits SHA-256 hashes for
    chain-of-custody (SEC 17a-4 / FINRA 4511 alignment).

.EXAMPLE
    .\Get-IBBaseline.ps1 -OutputPath '.\evidence\1.22\baseline'
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$OutputPath
)

$ErrorActionPreference = 'Stop'
if (-not (Test-Path $OutputPath)) { New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null }
$timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'

Connect-IPPSSession -ShowBanner:$false

$mode = Get-InformationBarrierMode
$segments = Get-OrganizationSegment
$policies = Get-InformationBarrierPolicy
$status = Get-InformationBarrierPoliciesApplicationStatus

$mode    | ConvertTo-Json -Depth 5 | Out-File "$OutputPath\IB-Mode-$timestamp.json"   -Encoding utf8
$segments| Select-Object Name, UserGroupFilter, Type, ExoSegmentId, CreatedBy, WhenCreated, WhenChanged |
    Export-Csv "$OutputPath\IB-Segments-$timestamp.csv" -NoTypeInformation -Encoding utf8
$policies| Select-Object Name, AssignedSegment, SegmentsAllowed, SegmentsBlocked, State, ModerationAllowed, WhenChanged |
    Export-Csv "$OutputPath\IB-Policies-$timestamp.csv" -NoTypeInformation -Encoding utf8
$status  | ConvertTo-Json -Depth 5 | Out-File "$OutputPath\IB-AppStatus-$timestamp.json" -Encoding utf8

# SHA-256 chain-of-custody hashes
Get-ChildItem $OutputPath -Filter "*$timestamp*" | ForEach-Object {
    $hash = Get-FileHash -Path $_.FullName -Algorithm SHA256
    [PSCustomObject]@{ File = $_.Name; SHA256 = $hash.Hash; CapturedAtUtc = (Get-Date).ToUniversalTime() }
} | Export-Csv "$OutputPath\Evidence-Manifest-$timestamp.csv" -NoTypeInformation -Encoding utf8

Disconnect-ExchangeOnline -Confirm:$false
Write-Host "Baseline captured to $OutputPath" -ForegroundColor Green
```

---

## Script 2 — Create Organization Segments

```powershell
<#
.SYNOPSIS
    Creates IB organization segments for FSI ethical walls.

.PARAMETER WhatIf
    Standard ShouldProcess support — preview without mutation.

.EXAMPLE
    .\New-IBSegments.ps1 -WhatIf
    .\New-IBSegments.ps1
#>
[CmdletBinding(SupportsShouldProcess)]
param()

$ErrorActionPreference = 'Stop'
Connect-IPPSSession -ShowBanner:$false

$segments = @(
    @{ Name = 'IB-Research';            Filter = "Department -eq 'Equity Research'" }
    @{ Name = 'IB-Trading';             Filter = "Department -eq 'Sales and Trading'" }
    @{ Name = 'IB-IB-Public';           Filter = "Department -eq 'Investment Banking' -and CompanyName -eq 'Capital Markets'" }
    @{ Name = 'IB-IB-Private';          Filter = "Department -eq 'Investment Banking' -and CompanyName -eq 'M&A'" }
    @{ Name = 'IB-Muni-Underwriting';   Filter = "Department -eq 'Municipal Underwriting'" }
    @{ Name = 'IB-Muni-Advisory';       Filter = "Department -eq 'Municipal Advisory'" }
    @{ Name = 'IB-Compliance';          Filter = "Department -eq 'Compliance'" }
)

foreach ($s in $segments) {
    $existing = Get-OrganizationSegment -Identity $s.Name -ErrorAction SilentlyContinue
    if ($existing) {
        Write-Host "[EXISTS] $($s.Name)" -ForegroundColor Yellow
        continue
    }
    if ($PSCmdlet.ShouldProcess($s.Name, "New-OrganizationSegment")) {
        New-OrganizationSegment -Name $s.Name -UserGroupFilter $s.Filter | Out-Null
        Write-Host "[CREATED] $($s.Name)" -ForegroundColor Green
    }
}

Disconnect-ExchangeOnline -Confirm:$false
```

---

## Script 3 — Create IB Policies (Multi-Segment Allow-List Pattern)

> Multi-Segment mode policies are **allow-lists**. The `-SegmentsAllowed` array names every segment the assigned segment may communicate with. Misconfiguration here is the most common cause of unintended barrier failures.

```powershell
<#
.SYNOPSIS
    Creates IB policies in MultiSegment mode for FSI ethical walls.

.NOTES
    Verifies Get-InformationBarrierMode returns 'MultiSegment' before creating
    allow-list policies. Falls back with an error in other modes.
#>
[CmdletBinding(SupportsShouldProcess)]
param()

$ErrorActionPreference = 'Stop'
Connect-IPPSSession -ShowBanner:$false

$mode = (Get-InformationBarrierMode).Identity
if ($mode -ne 'MultiSegment') {
    throw "IB mode is '$mode'. This script targets MultiSegment. Migrate first or use the SingleSegment block-list variant."
}

$policies = @(
    @{ Name = 'Policy-IB-Research';          Assigned = 'IB-Research';          Allowed = @('IB-Research','IB-Compliance') }
    @{ Name = 'Policy-IB-Trading';           Assigned = 'IB-Trading';           Allowed = @('IB-Trading','IB-Compliance') }
    @{ Name = 'Policy-IB-IB-Public';         Assigned = 'IB-IB-Public';         Allowed = @('IB-IB-Public','IB-Compliance') }
    @{ Name = 'Policy-IB-IB-Private';        Assigned = 'IB-IB-Private';        Allowed = @('IB-IB-Private','IB-Compliance') }
    @{ Name = 'Policy-IB-Muni-Underwriting'; Assigned = 'IB-Muni-Underwriting'; Allowed = @('IB-Muni-Underwriting','IB-Compliance') }
    @{ Name = 'Policy-IB-Muni-Advisory';     Assigned = 'IB-Muni-Advisory';     Allowed = @('IB-Muni-Advisory','IB-Compliance') }
    @{ Name = 'Policy-IB-Compliance';        Assigned = 'IB-Compliance';        Allowed = @('IB-Research','IB-Trading','IB-IB-Public','IB-IB-Private','IB-Muni-Underwriting','IB-Muni-Advisory','IB-Compliance') }
)

foreach ($p in $policies) {
    $existing = Get-InformationBarrierPolicy -Identity $p.Name -ErrorAction SilentlyContinue
    if ($existing) {
        Write-Host "[EXISTS] $($p.Name) — review before re-creating" -ForegroundColor Yellow
        continue
    }
    if ($PSCmdlet.ShouldProcess($p.Name, "New-InformationBarrierPolicy (MultiSegment allow-list)")) {
        New-InformationBarrierPolicy -Name $p.Name `
            -AssignedSegment $p.Assigned `
            -SegmentsAllowed $p.Allowed `
            -State Active | Out-Null
        Write-Host "[CREATED] $($p.Name)" -ForegroundColor Green
    }
}

Write-Host "`nReview policies before applying." -ForegroundColor Cyan
Get-InformationBarrierPolicy | Select-Object Name, AssignedSegment, SegmentsAllowed, State | Format-Table -AutoSize

Disconnect-ExchangeOnline -Confirm:$false
```

---

## Script 4 — Apply IB Policies and Track Status

```powershell
<#
.SYNOPSIS
    Applies IB policies and waits up to N hours for completion.

.PARAMETER MaxWaitHours
    Maximum hours to poll Get-InformationBarrierPoliciesApplicationStatus.
    Default 6; production tenants frequently take 24–72 hours.

.EXAMPLE
    .\Start-IBApplication.ps1 -MaxWaitHours 24
#>
[CmdletBinding(SupportsShouldProcess)]
param(
    [int]$MaxWaitHours = 6,
    [int]$PollSeconds = 300
)

$ErrorActionPreference = 'Stop'
Connect-IPPSSession -ShowBanner:$false

if ($PSCmdlet.ShouldProcess('Tenant', 'Start-InformationBarrierPoliciesApplication')) {
    Start-InformationBarrierPoliciesApplication
    Write-Host "Application started at $(Get-Date -Format 'u')" -ForegroundColor Cyan
}

$deadline = (Get-Date).AddHours($MaxWaitHours)
do {
    Start-Sleep -Seconds $PollSeconds
    $status = Get-InformationBarrierPoliciesApplicationStatus | Sort-Object StartTime -Descending | Select-Object -First 1
    Write-Host "[$(Get-Date -Format 'u')] Status: $($status.Status)  Identity: $($status.Identity)" -ForegroundColor DarkCyan
} while ($status.Status -in @('NotStarted','InProgress') -and (Get-Date) -lt $deadline)

if ($status.Status -ne 'Completed') {
    Write-Warning "Did not reach Completed within $MaxWaitHours hours. Current status: $($status.Status)"
    exit 2
}

Write-Host "[PASS] Application Completed at $($status.EndTime)" -ForegroundColor Green
Disconnect-ExchangeOnline -Confirm:$false
```

---

## Script 5 — Segment Coverage Report (Identify Segment-less Users)

Users without a segment **bypass** IB enforcement and are the highest-impact residual risk. This report identifies them so they can be remediated before policy application.

```powershell
<#
.SYNOPSIS
    Identifies users not covered by any IB segment.

.DESCRIPTION
    Cross-references all enabled member users in Entra ID against current
    IB segment filters and emits a CSV of segment-less users for remediation.

.EXAMPLE
    .\Export-IBSegmentCoverage.ps1 -OutputPath '.\evidence\1.22\coverage'
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$OutputPath
)

$ErrorActionPreference = 'Stop'
if (-not (Test-Path $OutputPath)) { New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null }
$timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'

Connect-MgGraph -Scopes 'User.Read.All' -NoWelcome | Out-Null
$users = Get-MgUser -All -Filter "accountEnabled eq true and userType eq 'Member'" `
    -Property Id,UserPrincipalName,DisplayName,Department,CompanyName,JobTitle

# Heuristic: an HR-of-record-driven segmentation requires Department to be populated.
$uncovered = $users | Where-Object { [string]::IsNullOrWhiteSpace($_.Department) }

$uncovered | Select-Object UserPrincipalName, DisplayName, Department, CompanyName, JobTitle |
    Export-Csv "$OutputPath\IB-UncoveredUsers-$timestamp.csv" -NoTypeInformation -Encoding utf8

$summary = [PSCustomObject]@{
    TotalEnabledMembers = $users.Count
    Uncovered           = $uncovered.Count
    CoveragePercent     = if ($users.Count -gt 0) { [math]::Round((($users.Count - $uncovered.Count) / $users.Count) * 100, 2) } else { 0 }
    GeneratedAtUtc      = (Get-Date).ToUniversalTime()
}
$summary | ConvertTo-Json | Out-File "$OutputPath\IB-CoverageSummary-$timestamp.json" -Encoding utf8

Write-Host "Coverage: $($summary.CoveragePercent)% — $($summary.Uncovered) uncovered users" -ForegroundColor Cyan
Disconnect-MgGraph | Out-Null
```

---

## Script 6 — Validate Configuration End-to-End

```powershell
<#
.SYNOPSIS
    Validates Control 1.22 configuration is in the intended state.

.DESCRIPTION
    Returns 0 on PASS; non-zero on FAIL with reason logged.
    Designed for unattended scheduled runs feeding compliance dashboards.
#>
[CmdletBinding()]
param(
    [string]$ExpectedMode = 'MultiSegment',
    [string[]]$RequiredSegments = @('IB-Research','IB-Trading','IB-IB-Public','IB-IB-Private','IB-Muni-Underwriting','IB-Muni-Advisory','IB-Compliance'),
    [decimal]$MinimumCoveragePercent = 99.5
)

$ErrorActionPreference = 'Stop'
$failures = @()

Connect-IPPSSession -ShowBanner:$false

$mode = (Get-InformationBarrierMode).Identity
if ($mode -ne $ExpectedMode) { $failures += "IB mode is '$mode'; expected '$ExpectedMode'." }

$segments = (Get-OrganizationSegment).Name
$missing = $RequiredSegments | Where-Object { $_ -notin $segments }
if ($missing) { $failures += "Missing segments: $($missing -join ', ')." }

$active = Get-InformationBarrierPolicy | Where-Object State -eq 'Active'
if ($active.Count -lt $RequiredSegments.Count) {
    $failures += "Active policy count ($($active.Count)) less than required segment count ($($RequiredSegments.Count))."
}

$last = Get-InformationBarrierPoliciesApplicationStatus | Sort-Object StartTime -Descending | Select-Object -First 1
if ($last.Status -ne 'Completed') { $failures += "Last application status: $($last.Status)." }

Disconnect-ExchangeOnline -Confirm:$false

if ($failures) {
    $failures | ForEach-Object { Write-Host "[FAIL] $_" -ForegroundColor Red }
    exit 1
}
Write-Host "[PASS] Control 1.22 validation succeeded" -ForegroundColor Green
exit 0
```

---

## Sovereign-Cloud Connection Notes

For GCC High and DoD tenants, `Connect-IPPSSession` requires explicit endpoints:

```powershell
# GCC High
Connect-IPPSSession `
    -ConnectionUri 'https://ps.compliance.protection.office365.us/powershell-liveid/' `
    -AzureADAuthorizationEndpointUri 'https://login.microsoftonline.us/common'

# DoD
Connect-IPPSSession `
    -ConnectionUri 'https://l5.ps.compliance.protection.office365.us/powershell-liveid/' `
    -AzureADAuthorizationEndpointUri 'https://login.microsoftonline.us/common'
```

Refer to the [PowerShell Authoring Baseline](../../_shared/powershell-baseline.md) §6 for current sovereign-cloud endpoint tables.

---

## Rollback

If a misapplied policy must be rolled back:

1. `Set-InformationBarrierPolicy -Identity <name> -State Inactive` to deactivate without deletion (preserves audit history).
2. `Start-InformationBarrierPoliciesApplication` to push the deactivation.
3. Confirm `Get-InformationBarrierPoliciesApplicationStatus` reaches `Completed`.
4. Only delete a policy after Compliance sign-off; deletion is permanent.

---

[Back to Control 1.22](../../../controls/pillar-1-security/1.22-information-barriers.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
