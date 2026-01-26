# Control 1.12: Insider Risk Detection and Response - PowerShell Setup

> This playbook provides PowerShell automation guidance for [Control 1.12](../../../controls/pillar-1-security/1.12-insider-risk-detection-and-response.md).

---

## Connect to Security & Compliance

```powershell
Connect-IPPSSession
```

---

## Get Insider Risk Policies

```powershell
Get-InsiderRiskPolicy | Select-Object Name, Mode, Enabled, Priority |
    Format-Table -AutoSize
```

---

## Get Priority User Groups

```powershell
Get-InsiderRiskPriorityUserGroup | Select-Object Name, Members | Format-List
```

---

## Get Current Alerts

```powershell
$Alerts = Get-InsiderRiskAlert -Filter "Status -eq 'NeedsReview'"

Write-Host "`nPending Insider Risk Alerts:" -ForegroundColor Yellow
$Alerts | Select-Object AlertId, User, Severity, CreatedTime | Format-Table
```

---

## Audit Log Search for Insider Activities

```powershell
$StartDate = (Get-Date).AddDays(-30)
$EndDate = Get-Date

# Search for bulk file downloads
$BulkDownloads = Search-UnifiedAuditLog `
    -StartDate $StartDate `
    -EndDate $EndDate `
    -Operations FileDownloaded, FileSyncDownloadedFull `
    -ResultSize 5000

# Analyze download patterns
$DownloadByUser = $BulkDownloads | Group-Object UserIds |
    Sort-Object Count -Descending |
    Select-Object -First 20 Name, Count

Write-Host "`nTop File Downloaders (Last 30 days):" -ForegroundColor Cyan
$DownloadByUser | Format-Table

# Identify potential exfiltration (high volume)
$PotentialExfiltration = $DownloadByUser | Where-Object { $_.Count -gt 100 }

if ($PotentialExfiltration) {
    Write-Host "`nPOTENTIAL EXFILTRATION DETECTED:" -ForegroundColor Red
    $PotentialExfiltration | Format-Table
}
```

---

## Search for External Sharing

```powershell
$ExternalSharing = Search-UnifiedAuditLog `
    -StartDate $StartDate `
    -EndDate $EndDate `
    -Operations SharingSet, AnonymousLinkCreated, SecureLinkCreated `
    -ResultSize 1000

Write-Host "`nExternal sharing events: $($ExternalSharing.Count)" -ForegroundColor Yellow

# Parse for risky sharing
$RiskySharing = $ExternalSharing | ForEach-Object {
    $AuditData = $_.AuditData | ConvertFrom-Json

    [PSCustomObject]@{
        Date = $_.CreationDate
        User = $_.UserIds
        Operation = $AuditData.Operation
        Target = $AuditData.ObjectId
        ExternalUser = $AuditData.TargetUserOrGroupName
    }
} | Where-Object { $_.ExternalUser -like "*#ext#*" -or $_.Operation -eq "AnonymousLinkCreated" }

Write-Host "`nRisky sharing events: $($RiskySharing.Count)" -ForegroundColor Yellow
```

---

## Generate Insider Risk Report

```powershell
$PolicyCount = (Get-InsiderRiskPolicy).Count
$AlertCount = (Get-InsiderRiskAlert).Count

$Report = @{
    ActivePolicies = $PolicyCount
    TotalAlerts = $AlertCount
    PendingAlerts = ($Alerts | Measure-Object).Count
    BulkDownloadUsers = $PotentialExfiltration.Count
    RiskySharingEvents = $RiskySharing.Count
    ReportPeriod = "$StartDate to $EndDate"
    ReportDate = Get-Date
}

Write-Host "`n=== INSIDER RISK SUMMARY ===" -ForegroundColor Cyan
$Report | Format-List

# Export details
$RiskySharing | Export-Csv "RiskySharing-$(Get-Date -Format 'yyyyMMdd').csv" -NoTypeInformation
```

---

## Search for USB Activity

```powershell
$UsbActivity = Search-UnifiedAuditLog `
    -StartDate $StartDate `
    -EndDate $EndDate `
    -Operations CopiedToRemovableMedia `
    -ResultSize 1000

Write-Host "`nUSB copy events: $($UsbActivity.Count)" -ForegroundColor Yellow

$UsbActivity | ForEach-Object {
    $AuditData = $_.AuditData | ConvertFrom-Json
    [PSCustomObject]@{
        Date = $_.CreationDate
        User = $_.UserIds
        FileName = $AuditData.ObjectId
    }
} | Format-Table
```

---

## Search for Print Activity

```powershell
$PrintActivity = Search-UnifiedAuditLog `
    -StartDate $StartDate `
    -EndDate $EndDate `
    -Operations PrintedFile `
    -ResultSize 1000

Write-Host "`nPrint events: $($PrintActivity.Count)" -ForegroundColor Yellow
```

---

## Complete Configuration Script

```powershell
<#
.SYNOPSIS
    Configures Control 1.12 - Insider Risk Detection and Response

.DESCRIPTION
    This script audits insider risk indicators including bulk downloads,
    external sharing, USB activity, and generates compliance reports.

.PARAMETER DaysBack
    Number of days to search back in audit logs (default: 30)

.PARAMETER ExportPath
    Path for report exports (default: current directory)

.PARAMETER BulkDownloadThreshold
    Number of downloads to flag as potential exfiltration (default: 100)

.EXAMPLE
    .\Configure-Control-1.12.ps1 -DaysBack 30 -BulkDownloadThreshold 100

.NOTES
    Last Updated: January 2026
    Related Control: Control 1.12 - Insider Risk Detection and Response
#>

param(
    [int]$DaysBack = 30,
    [string]$ExportPath = ".",
    [int]$BulkDownloadThreshold = 100
)

try {
    # Connect to Security & Compliance
    Write-Host "Connecting to Security & Compliance Center..." -ForegroundColor Cyan
    Connect-IPPSSession

    Write-Host "Configuring Control 1.12: Insider Risk Detection and Response" -ForegroundColor Cyan

    $StartDate = (Get-Date).AddDays(-$DaysBack)
    $EndDate = Get-Date

    # Step 1: Check Insider Risk Policies
    Write-Host "`n[Step 1] Checking Insider Risk Policies..." -ForegroundColor Yellow
    $policies = Get-InsiderRiskPolicy
    Write-Host "  Active policies: $($policies.Count)" -ForegroundColor Green
    $policies | ForEach-Object { Write-Host "    - $($_.Name): $($_.Mode)" }

    # Step 2: Check current alerts
    Write-Host "`n[Step 2] Checking pending alerts..." -ForegroundColor Yellow
    $Alerts = Get-InsiderRiskAlert -Filter "Status -eq 'NeedsReview'" -ErrorAction SilentlyContinue
    if ($Alerts) {
        Write-Host "  Pending alerts: $($Alerts.Count)" -ForegroundColor Yellow
    } else {
        Write-Host "  No pending alerts" -ForegroundColor Green
    }

    # Step 3: Audit bulk downloads
    Write-Host "`n[Step 3] Auditing bulk file downloads..." -ForegroundColor Yellow
    $BulkDownloads = Search-UnifiedAuditLog `
        -StartDate $StartDate `
        -EndDate $EndDate `
        -Operations FileDownloaded, FileSyncDownloadedFull `
        -ResultSize 5000

    $DownloadByUser = $BulkDownloads | Group-Object UserIds |
        Sort-Object Count -Descending |
        Select-Object -First 20 Name, Count

    $PotentialExfiltration = $DownloadByUser | Where-Object { $_.Count -gt $BulkDownloadThreshold }
    if ($PotentialExfiltration) {
        Write-Host "  WARNING: Potential exfiltration detected for $($PotentialExfiltration.Count) users" -ForegroundColor Red
    } else {
        Write-Host "  No bulk download anomalies detected" -ForegroundColor Green
    }

    # Step 4: Audit external sharing
    Write-Host "`n[Step 4] Auditing external sharing..." -ForegroundColor Yellow
    $ExternalSharing = Search-UnifiedAuditLog `
        -StartDate $StartDate `
        -EndDate $EndDate `
        -Operations SharingSet, AnonymousLinkCreated, SecureLinkCreated `
        -ResultSize 1000

    Write-Host "  External sharing events: $($ExternalSharing.Count)" -ForegroundColor Green

    # Step 5: Generate report
    Write-Host "`n[Step 5] Generating compliance report..." -ForegroundColor Yellow
    $Report = [PSCustomObject]@{
        ReportDate = Get-Date
        ReportPeriod = "$StartDate to $EndDate"
        ActivePolicies = $policies.Count
        PendingAlerts = if ($Alerts) { $Alerts.Count } else { 0 }
        BulkDownloadEvents = $BulkDownloads.Count
        PotentialExfiltrationUsers = if ($PotentialExfiltration) { $PotentialExfiltration.Count } else { 0 }
        ExternalSharingEvents = $ExternalSharing.Count
    }

    $reportFile = Join-Path $ExportPath "InsiderRisk-Report-$(Get-Date -Format 'yyyyMMdd').csv"
    $Report | Export-Csv -Path $reportFile -NoTypeInformation
    Write-Host "  Report exported to: $reportFile" -ForegroundColor Green

    Write-Host "`n[PASS] Control 1.12 configuration completed successfully" -ForegroundColor Green
}
catch {
    Write-Host "[FAIL] Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "[INFO] Stack trace: $($_.ScriptStackTrace)" -ForegroundColor Yellow
    exit 1
}
finally {
    # Cleanup connections
    Disconnect-ExchangeOnline -Confirm:$false -ErrorAction SilentlyContinue
    Write-Host "`nDisconnected from Security & Compliance Center" -ForegroundColor Gray
}
```

---

*Updated: January 2026 | Version: v1.2*
