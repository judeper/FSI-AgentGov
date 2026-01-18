# Control 1.6: Microsoft Purview DSPM for AI - PowerShell Setup

> This playbook provides PowerShell automation guidance for [Control 1.6](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md).

---

## Enable Unified Audit Logging

```powershell
# Connect to Security & Compliance Center
Connect-IPPSSession -UserPrincipalName admin@contoso.com

# Enable unified audit logging (required for DSPM)
Set-AdminAuditLogConfig -UnifiedAuditLogIngestionEnabled $true

# Verify audit logging is enabled
Get-AdminAuditLogConfig | Select-Object UnifiedAuditLogIngestionEnabled
```

---

## Search AI-Related Audit Events

```powershell
# Search for Copilot-related audit events
$startDate = (Get-Date).AddDays(-30)
$endDate = Get-Date

# Get recent audit events (filter as needed)
$copilotEvents = Search-UnifiedAuditLog -StartDate $startDate -EndDate $endDate `
    -ResultSize 5000

$copilotEvents = $copilotEvents | Where-Object {
    $_.Operations -match 'Copilot|AI' -or $_.AuditData -match 'Copilot'
}

# Export results for analysis
$copilotEvents | Select-Object CreationDate, UserIds, Operations, AuditData |
    Export-Csv -Path "Copilot-Audit-Events.csv" -NoTypeInformation

# Parse and display recent AI interactions
foreach ($event in $copilotEvents | Select-Object -First 10) {
    $data = $event.AuditData | ConvertFrom-Json
    Write-Host "User: $($event.UserIds) - App: $($data.Application) - Time: $($event.CreationDate)"
}
```

---

## Export DSPM Activity Data

```powershell
# Search for specific sensitive information in AI interactions
$sensitiveSearch = Search-UnifiedAuditLog -StartDate $startDate -EndDate $endDate `
    -ResultSize 5000

# Filter for events with sensitive data
$sensitiveEvents = $sensitiveSearch | ForEach-Object {
    $data = $_.AuditData | ConvertFrom-Json
    if ($data.SensitiveInfoTypes) {
        [PSCustomObject]@{
            Date = $_.CreationDate
            User = $_.UserIds
            SensitiveTypes = ($data.SensitiveInfoTypes -join ", ")
            Application = $data.Application
        }
    }
}

$sensitiveEvents | Export-Csv -Path "DSPM-Sensitive-Events.csv" -NoTypeInformation
```

---

## Verify Policy Status

```powershell
# Get DLP policies for DSPM integration
Get-DlpCompliancePolicy | Where-Object { $_.Mode -eq "Enable" } |
    Select-Object Name, Mode, Enabled, WhenCreated |
    Format-Table

# Check retention policies that may affect AI data
Get-RetentionCompliancePolicy | Where-Object { $_.Enabled -eq $true } |
    Select-Object Name, Mode, RetentionDuration |
    Format-Table
```

---

## Audit Administrator Access to DSPM

```powershell
# Track who has accessed DSPM for AI
$dspmAccess = Search-UnifiedAuditLog -StartDate $startDate -EndDate $endDate `
    -Operations "PageViewed" -ResultSize 1000

$dspmPageViews = $dspmAccess | ForEach-Object {
    $data = $_.AuditData | ConvertFrom-Json
    if ($data.ObjectId -match "DSPM|ai-microsoft-purview") {
        [PSCustomObject]@{
            Date = $_.CreationDate
            User = $_.UserIds
            Page = $data.ObjectId
        }
    }
}

$dspmPageViews | Export-Csv -Path "DSPM-Admin-Access.csv" -NoTypeInformation
```

---

## Generate DSPM Evidence Report

```powershell
# Create comprehensive DSPM evidence export
$evidenceDate = Get-Date -Format "yyyy-MM-dd"
$evidencePath = "DSPM-Evidence-$evidenceDate"

# Create evidence folder
New-Item -ItemType Directory -Path $evidencePath -Force

# Export audit configuration
Get-AdminAuditLogConfig |
    ConvertTo-Json |
    Out-File "$evidencePath\audit-config.json"

# Export DLP policies
Get-DlpCompliancePolicy |
    Select-Object Name, Mode, Enabled, WhenCreated |
    Export-Csv "$evidencePath\dlp-policies.csv" -NoTypeInformation

# Export AI-related events
$aiEvents = Search-UnifiedAuditLog -StartDate (Get-Date).AddDays(-7) -EndDate (Get-Date) `
    -ResultSize 1000 |
    Where-Object { $_.AuditData -match 'Copilot|AI' }

$aiEvents |
    Select-Object CreationDate, UserIds, Operations |
    Export-Csv "$evidencePath\ai-events.csv" -NoTypeInformation

Write-Host "Evidence exported to: $evidencePath"
```

---

*Updated: January 2026 | Version: v1.1*
