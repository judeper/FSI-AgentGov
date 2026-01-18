# Control 4.5: SharePoint Security and Compliance Monitoring - PowerShell Setup

> This playbook provides PowerShell automation guidance for [Control 4.5](../../../controls/pillar-4-sharepoint/4.5-sharepoint-security-and-compliance-monitoring.md).

---

## Prerequisites

```powershell
# Install required modules
Install-Module -Name Microsoft.Online.SharePoint.PowerShell -Force
Install-Module -Name ExchangeOnlineManagement -Scope CurrentUser
```

---

## Connect to Services

```powershell
# Connect to SharePoint Online
Connect-SPOService -Url https://contoso-admin.sharepoint.com

# Connect to Security & Compliance Center for Purview
Connect-IPPSSession -UserPrincipalName admin@contoso.com

# Verify connection
Get-SPOTenant | Select-Object SharingCapability, ConditionalAccessPolicy
```

---

## Search Audit Logs for SharePoint Events

```powershell
# Define search parameters
$startDate = (Get-Date).AddDays(-30)
$endDate = Get-Date

# Search for SharePoint file access by agents/Copilot
$sharepointEvents = Search-UnifiedAuditLog -StartDate $startDate -EndDate $endDate `
    -RecordType SharePoint -Operations FileAccessed,FileDownloaded,FileModified `
    -ResultSize 5000

Write-Host "Found $($sharepointEvents.Count) SharePoint events"

# Filter for agent-related access patterns
$agentAccessEvents = $sharepointEvents | Where-Object {
    $_.AuditData -like "*Copilot*" -or $_.AuditData -like "*Agent*"
}

Write-Host "Found $($agentAccessEvents.Count) agent-related events"

# Export to CSV for analysis
$sharepointEvents | Select-Object CreationDate, UserIds, Operations, AuditData |
    Export-Csv -Path "SharePoint-Audit-Log-$(Get-Date -Format 'yyyy-MM-dd').csv" -NoTypeInformation
```

---

## Get Sensitive File Access

```powershell
# Search for access to files with sensitivity labels
$sensitiveFileAccess = Search-UnifiedAuditLog -StartDate $startDate -EndDate $endDate `
    -RecordType SharePoint -Operations FileAccessed,FileDownloaded `
    -FreeText "Sensitivity" -ResultSize 5000

# Parse and analyze results
$accessReport = $sensitiveFileAccess | ForEach-Object {
    $auditData = $_.AuditData | ConvertFrom-Json
    [PSCustomObject]@{
        Timestamp = $_.CreationDate
        User = $_.UserIds
        Operation = $_.Operations
        FileName = $auditData.ObjectId
        SiteUrl = $auditData.SiteUrl
        SensitivityLabel = $auditData.SensitivityLabelId
    }
}

$accessReport | Export-Csv -Path "Sensitive-File-Access-$(Get-Date -Format 'yyyy-MM-dd').csv" -NoTypeInformation
```

---

## Export Security Monitoring Configuration

```powershell
# Export SharePoint security settings
$securityConfig = @{
    TenantSettings = Get-SPOTenant | Select-Object *
    SharingSettings = Get-SPOTenant | Select-Object SharingCapability, DefaultSharingLinkType,
        ExternalUserExpirationRequired, ExternalUserExpireInDays
    ConditionalAccess = Get-SPOTenant | Select-Object ConditionalAccessPolicy,
        AllowDownloadingNonWebViewableFiles
    ExportDate = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
}

$securityConfig | ConvertTo-Json -Depth 10 |
    Out-File "SharePoint-Security-Config-$(Get-Date -Format 'yyyy-MM-dd').json"

# Export site-level settings for high-risk sites
$highRiskSites = Get-SPOSite -Limit All | Where-Object {
    $_.SensitivityLabel -eq "Highly Confidential" -or
    $_.LockState -ne "Unlock"
}

$highRiskSites | Select-Object Url, Owner, SensitivityLabel, SharingCapability,
    ConditionalAccessPolicy, LockState |
    Export-Csv -Path "HighRisk-Sites-$(Get-Date -Format 'yyyy-MM-dd').csv" -NoTypeInformation
```

---

## Create Compliance Reports

```powershell
# Generate comprehensive compliance report
$complianceReport = @{
    ReportDate = Get-Date -Format "yyyy-MM-dd"
    TotalSites = (Get-SPOSite -Limit All).Count
    LabeledSites = (Get-SPOSite -Limit All | Where-Object { $_.SensitivityLabel }).Count
    ExternalSharingSites = (Get-SPOSite -Limit All | Where-Object {
        $_.SharingCapability -ne "Disabled"
    }).Count
    RestrictedSites = (Get-SPOSite -Limit All | Where-Object {
        $_.RestrictedToGeo -or $_.ConditionalAccessPolicy -ne "AllowFullAccess"
    }).Count
}

# Export compliance summary
$complianceReport | ConvertTo-Json |
    Out-File "SharePoint-Compliance-Summary-$(Get-Date -Format 'yyyy-MM-dd').json"

# Create audit event summary for regulators
$auditSummary = Search-UnifiedAuditLog -StartDate (Get-Date).AddDays(-90) -EndDate (Get-Date) `
    -RecordType SharePoint -ResultSize 5000 |
    Group-Object Operations |
    Select-Object Name, Count |
    Sort-Object Count -Descending

$auditSummary | Export-Csv -Path "SharePoint-Audit-Summary-90Days.csv" -NoTypeInformation

Write-Host "Compliance reports generated successfully"
```

---

## Verify Audit Logging Status

```powershell
# Check if unified audit logging is enabled
Get-AdminAuditLogConfig | Select-Object UnifiedAuditLogIngestionEnabled

# Verify SharePoint Admin access
Get-MgUserMemberOf -UserId "admin@contoso.com" |
    Where-Object { $_.AdditionalProperties.displayName -like "*SharePoint*" }
```

---

*Updated: January 2026 | Version: v1.1*
