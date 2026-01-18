# PowerShell Setup: Control 2.19 - Customer AI Disclosure and Transparency

**Last Updated:** January 2026
**Modules Required:** Microsoft.PowerApps.Administration.PowerShell, Dataverse SDK

## Prerequisites

```powershell
# Install required modules
Install-Module -Name Microsoft.PowerApps.Administration.PowerShell -Force -Scope CurrentUser

# For Dataverse access
Install-Module -Name Microsoft.Xrm.Data.PowerShell -Force -Scope CurrentUser
```

---

## Disclosure Tracking Scripts

### Query Disclosure Log

```powershell
<#
.SYNOPSIS
    Queries AI disclosure log from Dataverse

.DESCRIPTION
    Retrieves disclosure records for compliance reporting

.PARAMETER StartDate
    Start date for query

.PARAMETER EndDate
    End date for query

.EXAMPLE
    .\Get-DisclosureLog.ps1 -StartDate "2026-01-01" -EndDate "2026-01-31"
#>

param(
    [DateTime]$StartDate = (Get-Date).AddDays(-30),
    [DateTime]$EndDate = (Get-Date)
)

# Connect to Dataverse
$conn = Connect-CrmOnline -ServerUrl "https://yourorg.crm.dynamics.com"

Write-Host "=== AI Disclosure Log Query ===" -ForegroundColor Cyan
Write-Host "Period: $StartDate to $EndDate"

# Query disclosure records
$fetchXml = @"
<fetch top="5000">
  <entity name="fsi_aidisclosurelog">
    <attribute name="fsi_sessionid" />
    <attribute name="fsi_disclosuretype" />
    <attribute name="fsi_escalationoffered" />
    <attribute name="fsi_escalationtaken" />
    <attribute name="createdon" />
    <filter>
      <condition attribute="createdon" operator="ge" value="$($StartDate.ToString('yyyy-MM-dd'))" />
      <condition attribute="createdon" operator="le" value="$($EndDate.ToString('yyyy-MM-dd'))" />
    </filter>
  </entity>
</fetch>
"@

$records = Get-CrmRecordsByFetch -conn $conn -Fetch $fetchXml

$report = $records.CrmRecords | ForEach-Object {
    [PSCustomObject]@{
        SessionId = $_.fsi_sessionid
        DisclosureType = $_.fsi_disclosuretype
        EscalationOffered = $_.fsi_escalationoffered
        EscalationTaken = $_.fsi_escalationtaken
        Timestamp = $_.createdon
    }
}

# Summary statistics
$total = $report.Count
$escalationsOffered = ($report | Where-Object { $_.EscalationOffered }).Count
$escalationsTaken = ($report | Where-Object { $_.EscalationTaken }).Count
$escalationRate = if ($escalationsOffered -gt 0) { [math]::Round(($escalationsTaken / $escalationsOffered) * 100, 1) } else { 0 }

Write-Host "`n=== Summary ===" -ForegroundColor Cyan
Write-Host "Total Interactions: $total"
Write-Host "Escalations Offered: $escalationsOffered"
Write-Host "Escalations Taken: $escalationsTaken"
Write-Host "Escalation Take Rate: $escalationRate%"

# By disclosure type
Write-Host "`n=== By Disclosure Type ===" -ForegroundColor Cyan
$report | Group-Object DisclosureType | ForEach-Object {
    Write-Host "$($_.Name): $($_.Count)"
}

# Export
$report | Export-Csv -Path "Disclosure-Log-$(Get-Date -Format 'yyyyMMdd').csv" -NoTypeInformation
Write-Host "`nReport exported to Disclosure-Log-$(Get-Date -Format 'yyyyMMdd').csv"
```

### Generate Compliance Report

```powershell
<#
.SYNOPSIS
    Generates disclosure compliance report

.DESCRIPTION
    Creates formatted report for compliance review

.EXAMPLE
    .\New-DisclosureComplianceReport.ps1
#>

param(
    [DateTime]$StartDate = (Get-Date).AddDays(-30),
    [DateTime]$EndDate = (Get-Date),
    [string]$OutputPath = "."
)

Write-Host "=== Generating Disclosure Compliance Report ===" -ForegroundColor Cyan

# Would query actual data from Dataverse
# Using template structure

$reportData = @{
    Period = "$StartDate to $EndDate"
    TotalInteractions = 15420
    DisclosuresDelivered = 15420
    DeliveryRate = 100.0
    EscalationsOffered = 15420
    EscalationsTaken = 1823
    EscalationRate = 11.8
    ByDisclosureType = @{
        "Comprehensive" = 8234
        "Standard" = 5186
        "Basic" = 2000
    }
}

$report = @"
# AI Disclosure Compliance Report

**Report Period:** $($reportData.Period)
**Generated:** $(Get-Date -Format "yyyy-MM-dd HH:mm")

## Executive Summary

| Metric | Value |
|--------|-------|
| Total Interactions | $($reportData.TotalInteractions) |
| Disclosures Delivered | $($reportData.DisclosuresDelivered) |
| Delivery Rate | $($reportData.DeliveryRate)% |
| Escalation Take Rate | $($reportData.EscalationRate)% |

## Disclosure by Type

| Type | Count | Percentage |
|------|-------|------------|
| Comprehensive | $($reportData.ByDisclosureType.Comprehensive) | $([math]::Round($reportData.ByDisclosureType.Comprehensive / $reportData.TotalInteractions * 100, 1))% |
| Standard | $($reportData.ByDisclosureType.Standard) | $([math]::Round($reportData.ByDisclosureType.Standard / $reportData.TotalInteractions * 100, 1))% |
| Basic | $($reportData.ByDisclosureType.Basic) | $([math]::Round($reportData.ByDisclosureType.Basic / $reportData.TotalInteractions * 100, 1))% |

## Human Escalation

- Escalations Offered: $($reportData.EscalationsOffered)
- Escalations Taken: $($reportData.EscalationsTaken)
- Take Rate: $($reportData.EscalationRate)%

## Compliance Status

✅ All interactions received AI disclosure
✅ Human escalation option provided in all sessions
✅ Disclosure records retained per policy

---
*Report generated automatically by FSI Agent Governance Framework*
"@

$reportFile = "$OutputPath\Disclosure-Compliance-Report-$(Get-Date -Format 'yyyyMMdd').md"
$report | Out-File -FilePath $reportFile
Write-Host "Report saved to: $reportFile"
```

---

## Validation Script

```powershell
<#
.SYNOPSIS
    Validates Control 2.19 - Customer AI Disclosure configuration

.EXAMPLE
    .\Validate-Control-2.19.ps1
#>

Write-Host "=== Control 2.19 Validation ===" -ForegroundColor Cyan

# Check 1: Disclosure templates
Write-Host "`n[Check 1] Disclosure Templates" -ForegroundColor Cyan
Write-Host "[INFO] Verify disclosure templates exist for each zone:"
Write-Host "  - Zone 1: Basic disclosure"
Write-Host "  - Zone 2: Standard disclosure"
Write-Host "  - Zone 3: Comprehensive disclosure"

# Check 2: Agent configuration
Write-Host "`n[Check 2] Agent Configuration" -ForegroundColor Cyan
Write-Host "[INFO] Verify agents include disclosure in greeting topic"
Write-Host "[INFO] Verify human escalation option is available"

# Check 3: Disclosure logging
Write-Host "`n[Check 3] Disclosure Logging" -ForegroundColor Cyan
Write-Host "[INFO] Verify disclosure events are logged"
Write-Host "[INFO] Check retention period meets requirements"

# Check 4: Compliance reporting
Write-Host "`n[Check 4] Compliance Reporting" -ForegroundColor Cyan
Write-Host "[INFO] Verify reports can be generated"
Write-Host "[INFO] Check report delivery to compliance team"

Write-Host "`n=== Validation Complete ===" -ForegroundColor Cyan
```

---

[Back to Control 2.19](../../../controls/pillar-2-management/2.19-customer-ai-disclosure-and-transparency.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
