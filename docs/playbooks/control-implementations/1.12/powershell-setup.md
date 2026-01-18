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

*Updated: January 2026 | Version: v1.1*
