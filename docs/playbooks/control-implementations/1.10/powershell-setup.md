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

## Complete Configuration Script

```powershell
<#
.SYNOPSIS
    Configures Control 1.10 - Communication Compliance Monitoring

.DESCRIPTION
    This script:
    1. Configures Communication Compliance role group memberships
    2. Searches for Copilot interaction audit events
    3. Exports communication data for compliance review
    4. Generates compliance summary report

.PARAMETER AnalystEmail
    Email for Communication Compliance Analyst role

.PARAMETER InvestigatorEmail
    Email for Communication Compliance Investigator role

.PARAMETER AdminEmail
    Email for Communication Compliance Admin role

.PARAMETER DaysToSearch
    Number of days to search for audit events (default: 7)

.EXAMPLE
    .\Configure-Control-1.10.ps1 -AnalystEmail "analyst@contoso.com" -InvestigatorEmail "investigator@contoso.com"

.NOTES
    Last Updated: January 2026
    Related Control: Control 1.10 - Communication Compliance Monitoring
#>

param(
    [Parameter(Mandatory=$false)]
    [string]$AnalystEmail,

    [Parameter(Mandatory=$false)]
    [string]$InvestigatorEmail,

    [Parameter(Mandatory=$false)]
    [string]$AdminEmail,

    [Parameter(Mandatory=$false)]
    [int]$DaysToSearch = 7
)

try {
    # Connect to Security & Compliance Center
    Connect-IPPSSession

    Write-Host "=== Configuring Control 1.10: Communication Compliance Monitoring ===" -ForegroundColor Cyan

    # Step 1: Configure role group memberships (if emails provided)
    Write-Host "`nStep 1: Configuring role group memberships..." -ForegroundColor White

    if ($AnalystEmail) {
        Add-RoleGroupMember -Identity "Communication Compliance Analysts" -Member $AnalystEmail -ErrorAction SilentlyContinue
        Write-Host "  [DONE] Added $AnalystEmail to Analysts role group" -ForegroundColor Green
    }

    if ($InvestigatorEmail) {
        Add-RoleGroupMember -Identity "Communication Compliance Investigators" -Member $InvestigatorEmail -ErrorAction SilentlyContinue
        Write-Host "  [DONE] Added $InvestigatorEmail to Investigators role group" -ForegroundColor Green
    }

    if ($AdminEmail) {
        Add-RoleGroupMember -Identity "Communication Compliance Admins" -Member $AdminEmail -ErrorAction SilentlyContinue
        Write-Host "  [DONE] Added $AdminEmail to Admins role group" -ForegroundColor Green
    }

    if (-not $AnalystEmail -and -not $InvestigatorEmail -and -not $AdminEmail) {
        Write-Host "  [SKIP] No role assignments specified" -ForegroundColor Gray
    }

    # Step 2: List current role group members
    Write-Host "`nStep 2: Auditing role group memberships..." -ForegroundColor White
    $RoleGroups = @(
        "Communication Compliance Admins",
        "Communication Compliance Analysts",
        "Communication Compliance Investigators",
        "Communication Compliance Viewers"
    )

    foreach ($Group in $RoleGroups) {
        $members = Get-RoleGroupMember -Identity $Group -ErrorAction SilentlyContinue
        $memberCount = if ($members) { $members.Count } else { 0 }
        Write-Host "  $Group`: $memberCount members" -ForegroundColor Cyan
    }

    # Step 3: Search for Copilot interactions
    Write-Host "`nStep 3: Searching for Copilot interactions..." -ForegroundColor White
    $StartDate = (Get-Date).AddDays(-$DaysToSearch)
    $EndDate = Get-Date

    $CopilotComms = Search-UnifiedAuditLog `
        -StartDate $StartDate `
        -EndDate $EndDate `
        -RecordType CopilotInteraction `
        -ResultSize 5000

    Write-Host "  [DONE] Found $($CopilotComms.Count) Copilot interactions" -ForegroundColor Green

    # Step 4: Parse and analyze communications
    Write-Host "`nStep 4: Analyzing communications..." -ForegroundColor White
    $CommAnalysis = $CopilotComms | ForEach-Object {
        $AuditData = $_.AuditData | ConvertFrom-Json

        [PSCustomObject]@{
            Date = $_.CreationDate
            User = $_.UserIds
            Operation = $AuditData.Operation
            AppName = $AuditData.AppName
        }
    }

    # Step 5: Export for compliance review
    Write-Host "`nStep 5: Exporting for compliance review..." -ForegroundColor White
    $CommAnalysis | Export-Csv "CopilotComms-$(Get-Date -Format 'yyyyMMdd').csv" -NoTypeInformation
    $CopilotComms | Export-Csv "CopilotComms-Raw-$(Get-Date -Format 'yyyyMMdd').csv" -NoTypeInformation
    Write-Host "  [DONE] Exported communication data" -ForegroundColor Green

    # Step 6: Get current policy status
    Write-Host "`nStep 6: Checking policy status..." -ForegroundColor White
    $Policies = Get-SupervisoryReviewPolicyV2 -ErrorAction SilentlyContinue
    $enabledPolicies = if ($Policies) { ($Policies | Where-Object { $_.Enabled }).Count } else { 0 }
    $totalPolicies = if ($Policies) { $Policies.Count } else { 0 }

    Write-Host "  Total policies: $totalPolicies" -ForegroundColor Cyan
    Write-Host "  Enabled policies: $enabledPolicies" -ForegroundColor Cyan

    # Step 7: Check sensitive info types for FSI
    Write-Host "`nStep 7: Checking FSI-relevant sensitive info types..." -ForegroundColor White
    $fsiTypes = Get-DlpSensitiveInformationType |
        Where-Object { $_.Name -like "*Financial*" -or $_.Name -like "*Account*" -or $_.Name -like "*Bank*" }
    Write-Host "  [DONE] Found $($fsiTypes.Count) FSI-relevant sensitive info types" -ForegroundColor Green

    # Step 8: Generate summary report
    Write-Host "`nStep 8: Generating summary..." -ForegroundColor White
    $Report = @{
        TotalPolicies = $totalPolicies
        EnabledPolicies = $enabledPolicies
        CopilotInteractions = $CopilotComms.Count
        FSISensitiveTypes = $fsiTypes.Count
        ReportPeriod = "$StartDate to $EndDate"
        ReportDate = Get-Date
    }

    Write-Host "`n=== COMMUNICATION COMPLIANCE SUMMARY ===" -ForegroundColor Cyan
    $Report | Format-List

    Write-Host "`n[PASS] Control 1.10 configuration completed successfully" -ForegroundColor Green
    Write-Host "[INFO] Policy creation and classifier configuration require portal access" -ForegroundColor Yellow
}
catch {
    Write-Host "[FAIL] Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "[INFO] Stack trace: $($_.ScriptStackTrace)" -ForegroundColor Yellow
    exit 1
}
finally {
    # Disconnect from Security & Compliance Center
    Disconnect-ExchangeOnline -Confirm:$false -ErrorAction SilentlyContinue
}
```

---

*Updated: January 2026 | Version: v1.2*
