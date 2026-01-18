# PowerShell Setup: Control 2.13 - Documentation and Record Keeping

**Last Updated:** January 2026
**Modules Required:** PnP.PowerShell, ExchangeOnlineManagement

## Prerequisites

```powershell
Install-Module -Name PnP.PowerShell -Force -Scope CurrentUser
Install-Module -Name ExchangeOnlineManagement -Force -Scope CurrentUser
```

---

## Automated Scripts

### Create Site Structure

```powershell
<#
.SYNOPSIS
    Creates SharePoint site structure for AI governance documentation

.EXAMPLE
    .\New-AIGovernanceSite.ps1 -AdminUrl "https://tenant-admin.sharepoint.com"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$AdminUrl,
    [string]$SiteUrl = "/sites/AI-Governance"
)

Write-Host "=== Create AI Governance Site ===" -ForegroundColor Cyan

Connect-PnPOnline -Url $AdminUrl -Interactive

# Create site
$site = New-PnPSite -Type TeamSite -Title "AI Governance" -Alias "AI-Governance"

Connect-PnPOnline -Url "$AdminUrl$SiteUrl" -Interactive

# Create libraries
$libraries = @(
    "AgentConfigurations",
    "InteractionLogs",
    "ApprovalRecords",
    "IncidentReports",
    "GovernanceDecisions"
)

foreach ($lib in $libraries) {
    New-PnPList -Title $lib -Template DocumentLibrary
    Write-Host "Created library: $lib" -ForegroundColor Green
}

# Create site columns
New-PnPField -DisplayName "Agent ID" -InternalName "AgentID" -Type Text -Group "AI Governance"
New-PnPField -DisplayName "Document Category" -InternalName "DocCategory" -Type Choice -Choices "Configuration","Log","Approval","Incident","Decision" -Group "AI Governance"
New-PnPField -DisplayName "Regulatory Reference" -InternalName "RegReference" -Type Choice -Choices "FINRA 4511","SEC 17a-4","SOX 404","GLBA" -Group "AI Governance"

Write-Host "Site setup complete" -ForegroundColor Green

Disconnect-PnPOnline
```

### Export Retention Label Status

```powershell
<#
.SYNOPSIS
    Exports retention label application status

.EXAMPLE
    .\Export-RetentionStatus.ps1
#>

Write-Host "=== Retention Label Status ===" -ForegroundColor Cyan

Connect-IPPSSession

# Get retention labels
$labels = Get-RetentionCompliancePolicy | Where-Object { $_.Name -like "*FSI*" -or $_.Name -like "*Agent*" }

Write-Host "Retention policies found: $($labels.Count)"

foreach ($label in $labels) {
    Write-Host "`nPolicy: $($label.Name)" -ForegroundColor Yellow
    Write-Host "  Mode: $($label.Mode)"
    Write-Host "  Enabled: $($label.Enabled)"
    Write-Host "  Locations: $($label.SharePointLocation -join ', ')"
}

Disconnect-ExchangeOnline -Confirm:$false
```

### Audit Document Completeness

```powershell
<#
.SYNOPSIS
    Audits AI governance documentation completeness

.EXAMPLE
    .\Audit-DocumentationCompleteness.ps1 -SiteUrl "https://tenant.sharepoint.com/sites/AI-Governance"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$SiteUrl
)

Write-Host "=== Documentation Completeness Audit ===" -ForegroundColor Cyan

Connect-PnPOnline -Url $SiteUrl -Interactive

$requiredDocs = @(
    @{Library="GovernanceDecisions"; Doc="AI-Governance-Policy"},
    @{Library="GovernanceDecisions"; Doc="WSP-Addendum"},
    @{Library="GovernanceDecisions"; Doc="Examination-Response-Procedure"}
)

foreach ($req in $requiredDocs) {
    $items = Get-PnPListItem -List $req.Library -Query "<View><Query><Where><Contains><FieldRef Name='FileLeafRef'/><Value Type='Text'>$($req.Doc)</Value></Contains></Where></Query></View>"

    if ($items) {
        Write-Host "[PASS] Found: $($req.Doc) in $($req.Library)" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] Missing: $($req.Doc) in $($req.Library)" -ForegroundColor Red
    }
}

Disconnect-PnPOnline
```

---

## Validation Script

```powershell
<#
.SYNOPSIS
    Validates Control 2.13 - Documentation and record keeping

.EXAMPLE
    .\Validate-Control-2.13.ps1
#>

Write-Host "=== Control 2.13 Validation ===" -ForegroundColor Cyan

# Check 1: Site structure
Write-Host "`n[Check 1] SharePoint Site Structure" -ForegroundColor Cyan
Write-Host "[INFO] Verify AI Governance site and libraries exist"

# Check 2: Retention labels
Write-Host "`n[Check 2] Retention Labels" -ForegroundColor Cyan
Connect-IPPSSession
$labels = Get-RetentionCompliancePolicy | Where-Object { $_.Name -like "*Agent*" }
if ($labels) {
    Write-Host "[PASS] Retention policies found: $($labels.Count)" -ForegroundColor Green
} else {
    Write-Host "[WARN] No agent retention policies found" -ForegroundColor Yellow
}
Disconnect-ExchangeOnline -Confirm:$false

# Check 3: WORM storage (manual)
Write-Host "`n[Check 3] WORM Storage" -ForegroundColor Cyan
Write-Host "[INFO] Verify immutable storage for Zone 3 (SEC 17a-4)"

# Check 4: Examination procedures
Write-Host "`n[Check 4] Examination Procedures" -ForegroundColor Cyan
Write-Host "[INFO] Verify examination response procedure is documented"

Write-Host "`n=== Validation Complete ===" -ForegroundColor Cyan
```

---

[Back to Control 2.13](../../../controls/pillar-2-management/2.13-documentation-and-record-keeping.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
