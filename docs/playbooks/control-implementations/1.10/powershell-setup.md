# Control 1.10: Communication Compliance Monitoring - PowerShell Setup

> This playbook provides PowerShell automation guidance for [Control 1.10](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md).

---

## Connect to Security & Compliance

```powershell
Connect-IPPSSession
```

---

## Get Current Policies

```powershell
Get-SupervisoryReviewPolicyV2 | Select-Object Name, Enabled, ReviewerEmail |
    Format-Table -AutoSize
```

---

## Get Communication Compliance Role Groups

```powershell
Get-RoleGroup | Where-Object { $_.Name -like "*Communication*" } |
    Select-Object Name, Members | Format-List
```

---

## Add Members to Role Groups

```powershell
# Add analyst to Communication Compliance Analysts
Add-RoleGroupMember -Identity "Communication Compliance Analysts" `
    -Member "compliance-analyst@contoso.com"

# Add investigator
Add-RoleGroupMember -Identity "Communication Compliance Investigators" `
    -Member "compliance-investigator@contoso.com"

# Add admin
Add-RoleGroupMember -Identity "Communication Compliance Admins" `
    -Member "compliance-admin@contoso.com"
```

---

## Audit Log Search for Agent Communications

```powershell
$StartDate = (Get-Date).AddDays(-7)
$EndDate = Get-Date

# Search for Copilot interactions
$CopilotComms = Search-UnifiedAuditLog `
    -StartDate $StartDate `
    -EndDate $EndDate `
    -RecordType CopilotInteraction `
    -ResultSize 5000

Write-Host "Copilot interactions found: $($CopilotComms.Count)" -ForegroundColor Yellow

# Parse for review
$CommAnalysis = $CopilotComms | ForEach-Object {
    $AuditData = $_.AuditData | ConvertFrom-Json

    [PSCustomObject]@{
        Date = $_.CreationDate
        User = $_.UserIds
        Operation = $AuditData.Operation
        AppName = $AuditData.AppName
    }
}

# Export for compliance review
$CommAnalysis | Export-Csv "CopilotComms-$(Get-Date -Format 'yyyyMMdd').csv" -NoTypeInformation

# Export raw audit results (immutable copy)
$CopilotComms | Export-Csv "CopilotComms-Raw-$(Get-Date -Format 'yyyyMMdd').csv" -NoTypeInformation
```

---

## Check Sensitive Info Type Matches

```powershell
Get-DlpSensitiveInformationType |
    Where-Object { $_.Name -like "*Financial*" -or $_.Name -like "*Account*" } |
    Select-Object Name, Publisher | Format-Table
```

---

## Generate Compliance Report

```powershell
$Policies = Get-SupervisoryReviewPolicyV2

$Report = @{
    TotalPolicies = $Policies.Count
    EnabledPolicies = ($Policies | Where-Object { $_.Enabled }).Count
    CopilotInteractions = $CopilotComms.Count
    ReportPeriod = "$StartDate to $EndDate"
    ReportDate = Get-Date
}

Write-Host "`n=== COMMUNICATION COMPLIANCE SUMMARY ===" -ForegroundColor Cyan
$Report | Format-List
```

---

## List Role Group Members

```powershell
$RoleGroups = @(
    "Communication Compliance Admins",
    "Communication Compliance Analysts",
    "Communication Compliance Investigators",
    "Communication Compliance Viewers"
)

foreach ($Group in $RoleGroups) {
    Write-Host "`n$Group Members:" -ForegroundColor Cyan
    Get-RoleGroupMember -Identity $Group | Select-Object Name, PrimarySmtpAddress
}
```

---

## Note on PowerShell Limitations

Communication Compliance has limited PowerShell support. Most policy configuration, including:
- Creating policies
- Configuring classifiers
- Setting up OCR
- Configuring priority user groups

Must be done via the Microsoft Purview portal.

---

*Updated: January 2026 | Version: v1.1*
