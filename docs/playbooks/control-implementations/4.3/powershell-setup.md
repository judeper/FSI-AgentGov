# Control 4.3: Site and Document Retention Management - PowerShell Setup

!!! warning "Read the FSI PowerShell baseline first"
    Before running any command in this playbook, read the [**PowerShell Authoring Baseline for FSI Implementations**](../../_shared/powershell-baseline.md). It is the canonical source for module version pinning, sovereign-cloud (GCC / GCC High / DoD) endpoints, mutation safety (`-WhatIf` / `SupportsShouldProcess`), Dataverse compatibility, and SHA-256 evidence emission. Snippets below show the canonical patterns; the baseline is authoritative.

> This playbook provides PowerShell automation guidance for [Control 4.3](../../../controls/pillar-4-sharepoint/4.3-site-and-document-retention-management.md).

---

## Prerequisites

Pin module versions to versions approved by your Change Advisory Board. Replace `<version>` with the value recorded in your change ticket.

```powershell
# Pin module versions per the FSI PowerShell Authoring Baseline (Section 1).
# DO NOT use -Force without -RequiredVersion in regulated tenants.
Install-Module -Name ExchangeOnlineManagement `
    -RequiredVersion '<version>' -Repository PSGallery -Scope CurrentUser -AllowClobber -AcceptLicense

Install-Module -Name Microsoft.Online.SharePoint.PowerShell `
    -RequiredVersion '<version>' -Repository PSGallery -Scope CurrentUser -AllowClobber -AcceptLicense
```

**Required roles:**

- **Purview Compliance Admin** or **Purview Records Manager** for `*-RetentionCompliancePolicy`, `*-RetentionComplianceRule`, `*-ComplianceTag` cmdlets
- **SharePoint Admin** for `Get-SPOSite` coverage analysis

---

## Connect to Services (Sovereign-Cloud Aware)

```powershell
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string]$AdminUpn,
    [Parameter(Mandatory)] [string]$SpoAdminUrl,  # e.g. https://contoso-admin.sharepoint.com
    [ValidateSet('Commercial','GCC','GCCHigh','DoD')]
    [string]$Cloud = 'Commercial'
)

$ErrorActionPreference = 'Stop'

# Sovereign-cloud routing for Security & Compliance PowerShell (see baseline §3)
$ippsParams = @{ UserPrincipalName = $AdminUpn }
switch ($Cloud) {
    'GCC'      { $ippsParams.ConnectionUri = 'https://ps.compliance.protection.outlook.com/PowerShell-LiveID' }
    'GCCHigh'  { $ippsParams.ConnectionUri = 'https://ps.compliance.protection.office365.us/PowerShell-LiveID'
                 $ippsParams.AzureADAuthorizationEndpointUri = 'https://login.microsoftonline.us/common' }
    'DoD'      { $ippsParams.ConnectionUri = 'https://l5.ps.compliance.protection.office365.us/PowerShell-LiveID'
                 $ippsParams.AzureADAuthorizationEndpointUri = 'https://login.microsoftonline.us/common' }
}
Connect-IPPSSession @ippsParams

Connect-SPOService -Url $SpoAdminUrl

# Smoke test — silent failure here usually means wrong cloud / wrong UPN
Get-RetentionCompliancePolicy | Select-Object Name, Enabled, Mode | Format-Table
```

> **Verify before run:** check the current sovereign-cloud connection URIs on Microsoft Learn — Microsoft has changed these URLs more than once.

---

## Evidence Helper (SHA-256 + Manifest)

Per baseline §5, every artifact emitted from this control should be hashed and listed in `manifest.json`. Source the helper once, then reuse.

```powershell
function Write-FsiEvidence {
    param(
        [Parameter(Mandatory)] $Object,
        [Parameter(Mandatory)] [string]$Name,
        [Parameter(Mandatory)] [string]$EvidencePath
    )
    New-Item -ItemType Directory -Force -Path $EvidencePath | Out-Null
    $ts = Get-Date -Format 'yyyyMMddTHHmmssZ'
    $jsonPath = Join-Path $EvidencePath "$Name-$ts.json"
    $Object | ConvertTo-Json -Depth 20 | Set-Content -Path $jsonPath -Encoding UTF8
    $hash = (Get-FileHash -Path $jsonPath -Algorithm SHA256).Hash
    $manifestPath = Join-Path $EvidencePath "manifest.json"
    $manifest = @()
    if (Test-Path $manifestPath) { $manifest = @(Get-Content $manifestPath | ConvertFrom-Json) }
    $manifest += [PSCustomObject]@{
        file          = (Split-Path $jsonPath -Leaf)
        sha256        = $hash
        bytes         = (Get-Item $jsonPath).Length
        generated_utc = $ts
        control       = '4.3'
    }
    $manifest | ConvertTo-Json -Depth 5 | Set-Content -Path $manifestPath -Encoding UTF8
    return $jsonPath
}
```

---

## Create Retention Policy for Agent Knowledge Sources

```powershell
[CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
param(
    [Parameter(Mandatory)] [string[]]$KnowledgeSiteUrls,
    [string]$EvidencePath = ".\evidence\4.3"
)

$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force -Path $EvidencePath | Out-Null
$ts = Get-Date -Format 'yyyyMMdd-HHmmss'
Start-Transcript -Path "$EvidencePath\transcript-$ts.log" -IncludeInvocationHeader

$PolicyName = "FSI-Agent-Knowledge-Retention-7Years"

# Snapshot existing policy state (if any) before mutation
$before = Get-RetentionCompliancePolicy -Identity $PolicyName -ErrorAction SilentlyContinue
Write-FsiEvidence -Object $before -Name "policy-before-$PolicyName" -EvidencePath $EvidencePath | Out-Null

if ($PSCmdlet.ShouldProcess($PolicyName, "Create or update retention policy for agent knowledge sources")) {
    if (-not $before) {
        New-RetentionCompliancePolicy -Name $PolicyName `
            -Comment "Retention policy for agent knowledge sources per FINRA 4511 and SEC 17a-4 (Control 4.3)" `
            -SharePointLocation $KnowledgeSiteUrls `
            -Enabled $true | Out-Null
    } else {
        Set-RetentionCompliancePolicy -Identity $PolicyName -AddSharePointLocation $KnowledgeSiteUrls | Out-Null
    }

    # 7-year retain-and-delete from last modification
    $existingRule = Get-RetentionComplianceRule -Policy $PolicyName -ErrorAction SilentlyContinue
    if (-not $existingRule) {
        New-RetentionComplianceRule -Name "FSI-7Year-Retention-Rule" `
            -Policy $PolicyName `
            -RetentionDuration 2555 `
            -RetentionDurationDisplayHint Days `
            -RetentionComplianceAction KeepAndDelete `
            -ExpirationDateOption ModificationAgeInDays | Out-Null
    }
}

$after = Get-RetentionCompliancePolicy -Identity $PolicyName
Write-FsiEvidence -Object $after -Name "policy-after-$PolicyName" -EvidencePath $EvidencePath | Out-Null

Stop-Transcript
```

> **Always invoke first with `-WhatIf`** before running for real. `-SharePointLocation` does **not** support wildcards — pass explicit URLs or use `-SharePointLocation All` to scope to every SharePoint site.

---

## Create Zone-Specific Retention Policies

```powershell
$Zones = @(
    @{Name='Zone1-Personal';    Duration=365;  Sites=@('https://contoso.sharepoint.com/sites/Zone1-PersonalAgents')},
    @{Name='Zone2-Team';        Duration=1825; Sites=@('https://contoso.sharepoint.com/sites/Zone2-TeamAgents')},
    @{Name='Zone3-Enterprise';  Duration=2555; Sites=@('https://contoso.sharepoint.com/sites/Zone3-EnterpriseAgents')}
)

foreach ($Zone in $Zones) {
    $name = "FSI-$($Zone.Name)-Retention"
    if ($PSCmdlet.ShouldProcess($name, "Create zone retention policy")) {
        New-RetentionCompliancePolicy -Name $name -SharePointLocation $Zone.Sites -Enabled $true | Out-Null
        New-RetentionComplianceRule -Name "FSI-$($Zone.Name)-Rule" `
            -Policy $name `
            -RetentionDuration $Zone.Duration `
            -RetentionDurationDisplayHint Days `
            -RetentionComplianceAction KeepAndDelete | Out-Null
    }
}
```

---

## Create Retention Labels

```powershell
$Labels = @(
    @{ Name='FSI-Communications-3Y';      Duration=1095; Action='KeepAndDelete'; Description='3-year retention for communications (SEC 17a-4(b)(4))' },
    @{ Name='FSI-Financial-Records-6Y';   Duration=2190; Action='KeepAndDelete'; Description='6-year retention for financial/accounting records (SEC 17a-4(a) / FINRA 4511)' },
    @{ Name='FSI-Audit-Workpapers-7Y';    Duration=2555; Action='KeepAndDelete'; Description='7-year retention for audit workpapers (SOX 802 / SEC Reg S-X Rule 2-06)' },
    @{ Name='FSI-Customer-Data-5Y';       Duration=1825; Action='KeepAndDelete'; Description='5-year retention for customer information (industry practice; GLBA does not mandate a specific period)' },
    @{ Name='FSI-Regulatory-Record-7Y';   Duration=2555; Action='Keep';          Description='7-year regulatory record (immutable retain-only)' }
)

foreach ($l in $Labels) {
    if (-not (Get-ComplianceTag -Identity $l.Name -ErrorAction SilentlyContinue)) {
        if ($PSCmdlet.ShouldProcess($l.Name, "Create retention label")) {
            New-ComplianceTag -Name $l.Name `
                -Comment $l.Description `
                -RetentionDuration $l.Duration `
                -RetentionAction $l.Action `
                -RetentionType ModificationAgeInDays `
                -IsRecordLabel $false | Out-Null
        }
    }
}
```

> To declare a **regulatory record** (immutable for end users **and** admins), use `-IsRecordLabel $true -Regulatory $true`. This is one-way and requires Records Management; coordinate with Legal first.

---

## Apply Preservation Lock to a Regulatory Policy

Preservation Lock satisfies SEC 17a-4(f)-style requirements that the retention configuration cannot be disabled, shortened, or removed. **It is irreversible.**

```powershell
[CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
param([Parameter(Mandatory)][string]$PolicyName, [string]$EvidencePath = ".\evidence\4.3")

$before = Get-RetentionCompliancePolicy -Identity $PolicyName
Write-FsiEvidence -Object $before -Name "lock-before-$PolicyName" -EvidencePath $EvidencePath | Out-Null

if ($PSCmdlet.ShouldProcess($PolicyName, "IRREVERSIBLE: enable Preservation Lock")) {
    Set-RetentionCompliancePolicy -Identity $PolicyName -RestrictiveRetention $true
}

$after = Get-RetentionCompliancePolicy -Identity $PolicyName
Write-FsiEvidence -Object $after -Name "lock-after-$PolicyName" -EvidencePath $EvidencePath | Out-Null
```

---

## Coverage Report — Sites With and Without Retention

```powershell
Connect-SPOService -Url $SpoAdminUrl  # if not already connected

$RetentionPolicies = Get-RetentionCompliancePolicy | Where-Object { $_.SharePointLocation }

$SiteRetention = foreach ($Policy in $RetentionPolicies) {
    $Rule = Get-RetentionComplianceRule -Policy $Policy.Name
    foreach ($Site in $Policy.SharePointLocation) {
        [PSCustomObject]@{
            SiteUrl           = $Site
            PolicyName        = $Policy.Name
            RetentionDuration = $Rule.RetentionDuration
            Action            = $Rule.RetentionComplianceAction
            Locked            = $Policy.RestrictiveRetention
            PolicyEnabled     = $Policy.Enabled
        }
    }
}

$AllSites             = Get-SPOSite -Limit All
$CoveredUrls          = $SiteRetention.SiteUrl | Select-Object -Unique
$SitesWithoutCoverage = $AllSites | Where-Object { $_.Url -notin $CoveredUrls -and $CoveredUrls -notcontains 'All' }

Write-FsiEvidence -Object $SiteRetention         -Name 'site-retention-mapping' -EvidencePath $EvidencePath | Out-Null
Write-FsiEvidence -Object $SitesWithoutCoverage  -Name 'sites-without-coverage' -EvidencePath $EvidencePath | Out-Null

Write-Host "Sites without retention coverage: $($SitesWithoutCoverage.Count)" -ForegroundColor Yellow
```

`SitesWithoutCoverage` is the gap list — every site here that is also a Copilot/agent knowledge source (per Control 4.1) is a finding.

---

## Cleanup

```powershell
Disconnect-ExchangeOnline -Confirm:$false -ErrorAction SilentlyContinue
Disconnect-SPOService -ErrorAction SilentlyContinue
```

---

[Back to Control 4.3](../../../controls/pillar-4-sharepoint/4.3-site-and-document-retention-management.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: April 2026 | Version: v1.4.0*
