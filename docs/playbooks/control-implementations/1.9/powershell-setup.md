# Control 1.9: Data Retention and Deletion Policies - PowerShell Setup

> This playbook provides PowerShell automation guidance for [Control 1.9](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md).

---

## Connect to Security & Compliance

```powershell
Connect-IPPSSession
```

---

## Get Current Retention Labels

```powershell
Get-ComplianceTag | Select-Object Name, RetentionDuration, RetentionAction, IsRecordLabel |
    Format-Table -AutoSize
```

---

## Create Retention Labels

```powershell
# Agent Conversations - 7 Year (FINRA/SEC)
New-ComplianceTag -Name "FSI-AgentConversations-7Year" `
    -Comment "Agent conversation logs - FINRA/SEC 7-year retention" `
    -RetentionDuration 2555 `
    -RetentionAction KeepAndDelete `
    -RetentionType CreationAgeInDays `
    -ReviewerEmail "compliance@contoso.com"

# Agent Configuration - 6 Year
New-ComplianceTag -Name "FSI-AgentConfig-6Year" `
    -Comment "Agent configuration and settings history" `
    -RetentionDuration 2190 `
    -RetentionAction Delete `
    -RetentionType CreationAgeInDays

# Agent Audit Logs - 10 Year (Regulatory Record)
New-ComplianceTag -Name "FSI-AgentAudit-10Year" `
    -Comment "Agent audit and compliance logs - extended retention" `
    -RetentionDuration 3650 `
    -RetentionAction KeepAndDelete `
    -RetentionType CreationAgeInDays `
    -IsRecordLabel $true `
    -Regulatory $true `
    -ReviewerEmail "records@contoso.com"
```

---

## Create Retention Policies

```powershell
# Copilot Studio / Power Platform retention
New-RetentionCompliancePolicy -Name "FSI-CopilotStudio-Retention" `
    -Comment "Retain Copilot Studio conversation logs" `
    -ExchangeLocation "All" `
    -SharePointLocation "All"

New-RetentionComplianceRule -Policy "FSI-CopilotStudio-Retention" `
    -Name "FSI-CopilotStudio-7Year-Rule" `
    -RetentionDuration 2555 `
    -RetentionDurationDisplayHint Days `
    -RetentionComplianceAction KeepAndDelete

# Agent-related email retention
New-RetentionCompliancePolicy -Name "FSI-AgentEmail-Retention" `
    -Comment "Retain agent-related email communications" `
    -ExchangeLocation "All"

New-RetentionComplianceRule -Policy "FSI-AgentEmail-Retention" `
    -Name "FSI-AgentEmail-7Year-Rule" `
    -ContentMatchQuery "(copilot OR agent OR 'AI assistant' OR chatbot)" `
    -RetentionDuration 2555 `
    -RetentionComplianceAction KeepAndDelete
```

---

## Publish Labels

```powershell
# Get all FSI agent labels
$AgentLabels = Get-ComplianceTag | Where-Object { $_.Name -like "FSI-Agent*" }

# Create label policy
New-RetentionCompliancePolicy -Name "FSI-AgentLabels-Publish" `
    -Comment "Publish FSI agent retention labels" `
    -SharePointLocation "All" `
    -ExchangeLocation "All"

# Note: Adding labels to policy requires additional configuration via portal
```

---

## Create Audit Log Retention Policy

```powershell
New-UnifiedAuditLogRetentionPolicy -Name "FSI-DeletionAudit-10Year" `
    -Description "Extended retention for deletion events" `
    -Operations FileDeleted, FileVersionRecycled, HardDelete, MoveToDeletedItems `
    -RetentionDuration TenYears `
    -Priority 100
```

---

## Check Policy Status

```powershell
Get-RetentionCompliancePolicy |
    Select-Object Name, Mode, Enabled, DistributionStatus |
    Format-Table -AutoSize
```

---

## Generate Retention Report

```powershell
$Policies = Get-RetentionCompliancePolicy

$PolicyReport = foreach ($Policy in $Policies) {
    $Rules = Get-RetentionComplianceRule -Policy $Policy.Name

    foreach ($Rule in $Rules) {
        [PSCustomObject]@{
            PolicyName = $Policy.Name
            RuleName = $Rule.Name
            RetentionDays = $Rule.RetentionDuration
            Action = $Rule.RetentionComplianceAction
            Status = $Policy.DistributionStatus
            Enabled = $Policy.Enabled
        }
    }
}

$PolicyReport | Export-Csv "RetentionPolicies-$(Get-Date -Format 'yyyyMMdd').csv" -NoTypeInformation
```

---

## Check Disposition Reviews

```powershell
$Dispositions = Get-ComplianceTagStorage | Get-DispositionItem -Status Pending

Write-Host "`nPending Disposition Reviews:" -ForegroundColor Yellow
$Dispositions | Select-Object ItemName, Location, RetentionLabel, DispositionDate |
    Format-Table -AutoSize
```

---

## Compliance Summary

```powershell
$Summary = @{
    TotalRetentionLabels = (Get-ComplianceTag).Count
    TotalRetentionPolicies = $Policies.Count
    PoliciesEnabled = ($Policies | Where-Object { $_.Enabled }).Count
    PendingDispositions = ($Dispositions | Measure-Object).Count
    AuditRetentionPolicies = (Get-UnifiedAuditLogRetentionPolicy).Count
    ReportDate = Get-Date
}

Write-Host "`n=== DATA RETENTION COMPLIANCE SUMMARY ===" -ForegroundColor Cyan
$Summary | Format-List
```

---

## Complete Configuration Script

```powershell
<#
.SYNOPSIS
    Configures Control 1.9 - Data Retention and Deletion Policies

.DESCRIPTION
    This script:
    1. Creates retention labels for agent data (7-year, 6-year, 10-year)
    2. Creates retention policies for Copilot Studio and agent email
    3. Creates audit log retention policy for deletion events
    4. Validates and exports policy configuration

.PARAMETER ReviewerEmail
    Email for disposition review notifications (default: compliance@contoso.com)

.PARAMETER RecordsEmail
    Email for records management (default: records@contoso.com)

.EXAMPLE
    .\Configure-Control-1.9.ps1 -ReviewerEmail "compliance@contoso.com"

.NOTES
    Last Updated: January 2026
    Related Control: Control 1.9 - Data Retention and Deletion Policies
#>

param(
    [Parameter(Mandatory=$false)]
    [string]$ReviewerEmail = "compliance@contoso.com",

    [Parameter(Mandatory=$false)]
    [string]$RecordsEmail = "records@contoso.com"
)

try {
    # Connect to Security & Compliance Center
    Connect-IPPSSession

    Write-Host "=== Configuring Control 1.9: Data Retention and Deletion ===" -ForegroundColor Cyan

    # Step 1: Create retention labels
    Write-Host "`nStep 1: Creating retention labels..." -ForegroundColor White

    # Agent Conversations - 7 Year (FINRA/SEC)
    New-ComplianceTag -Name "FSI-AgentConversations-7Year" `
        -Comment "Agent conversation logs - FINRA/SEC 7-year retention" `
        -RetentionDuration 2555 `
        -RetentionAction KeepAndDelete `
        -RetentionType CreationAgeInDays `
        -ReviewerEmail $ReviewerEmail
    Write-Host "  [DONE] Created FSI-AgentConversations-7Year label" -ForegroundColor Green

    # Agent Configuration - 6 Year
    New-ComplianceTag -Name "FSI-AgentConfig-6Year" `
        -Comment "Agent configuration and settings history" `
        -RetentionDuration 2190 `
        -RetentionAction Delete `
        -RetentionType CreationAgeInDays
    Write-Host "  [DONE] Created FSI-AgentConfig-6Year label" -ForegroundColor Green

    # Agent Audit Logs - 10 Year (Regulatory Record)
    New-ComplianceTag -Name "FSI-AgentAudit-10Year" `
        -Comment "Agent audit and compliance logs - extended retention" `
        -RetentionDuration 3650 `
        -RetentionAction KeepAndDelete `
        -RetentionType CreationAgeInDays `
        -IsRecordLabel $true `
        -Regulatory $true `
        -ReviewerEmail $RecordsEmail
    Write-Host "  [DONE] Created FSI-AgentAudit-10Year label" -ForegroundColor Green

    # Step 2: Create retention policies
    Write-Host "`nStep 2: Creating retention policies..." -ForegroundColor White

    # Copilot Studio / Power Platform retention
    New-RetentionCompliancePolicy -Name "FSI-CopilotStudio-Retention" `
        -Comment "Retain Copilot Studio conversation logs" `
        -ExchangeLocation "All" `
        -SharePointLocation "All"

    New-RetentionComplianceRule -Policy "FSI-CopilotStudio-Retention" `
        -Name "FSI-CopilotStudio-7Year-Rule" `
        -RetentionDuration 2555 `
        -RetentionDurationDisplayHint Days `
        -RetentionComplianceAction KeepAndDelete
    Write-Host "  [DONE] Created FSI-CopilotStudio-Retention policy" -ForegroundColor Green

    # Agent-related email retention
    New-RetentionCompliancePolicy -Name "FSI-AgentEmail-Retention" `
        -Comment "Retain agent-related email communications" `
        -ExchangeLocation "All"

    New-RetentionComplianceRule -Policy "FSI-AgentEmail-Retention" `
        -Name "FSI-AgentEmail-7Year-Rule" `
        -ContentMatchQuery "(copilot OR agent OR 'AI assistant' OR chatbot)" `
        -RetentionDuration 2555 `
        -RetentionComplianceAction KeepAndDelete
    Write-Host "  [DONE] Created FSI-AgentEmail-Retention policy" -ForegroundColor Green

    # Step 3: Create audit log retention policy
    Write-Host "`nStep 3: Creating audit log retention policy..." -ForegroundColor White
    New-UnifiedAuditLogRetentionPolicy -Name "FSI-DeletionAudit-10Year" `
        -Description "Extended retention for deletion events" `
        -Operations FileDeleted, FileVersionRecycled, HardDelete, MoveToDeletedItems `
        -RetentionDuration TenYears `
        -Priority 100
    Write-Host "  [DONE] Created FSI-DeletionAudit-10Year audit policy" -ForegroundColor Green

    # Step 4: Validate configuration
    Write-Host "`nStep 4: Validating configuration..." -ForegroundColor White
    $labels = Get-ComplianceTag | Where-Object { $_.Name -like "FSI-Agent*" }
    Write-Host "  Labels created: $($labels.Count)" -ForegroundColor Cyan

    $policies = Get-RetentionCompliancePolicy | Where-Object { $_.Name -like "FSI-*" }
    Write-Host "  Retention policies created: $($policies.Count)" -ForegroundColor Cyan

    # Step 5: Export policy report
    Write-Host "`nStep 5: Exporting policy report..." -ForegroundColor White
    $Policies = Get-RetentionCompliancePolicy

    $PolicyReport = foreach ($Policy in $Policies) {
        $Rules = Get-RetentionComplianceRule -Policy $Policy.Name -ErrorAction SilentlyContinue

        foreach ($Rule in $Rules) {
            [PSCustomObject]@{
                PolicyName = $Policy.Name
                RuleName = $Rule.Name
                RetentionDays = $Rule.RetentionDuration
                Action = $Rule.RetentionComplianceAction
                Status = $Policy.DistributionStatus
                Enabled = $Policy.Enabled
            }
        }
    }

    $PolicyReport | Export-Csv "RetentionPolicies-$(Get-Date -Format 'yyyyMMdd').csv" -NoTypeInformation

    # Step 6: Generate summary
    Write-Host "`nStep 6: Configuration Summary" -ForegroundColor White
    $Summary = @{
        TotalRetentionLabels = (Get-ComplianceTag | Where-Object { $_.Name -like "FSI-Agent*" }).Count
        TotalRetentionPolicies = (Get-RetentionCompliancePolicy | Where-Object { $_.Name -like "FSI-*" }).Count
        AuditRetentionPolicies = (Get-UnifiedAuditLogRetentionPolicy | Where-Object { $_.Name -like "FSI-*" }).Count
        ReportDate = Get-Date
    }

    Write-Host "`n=== DATA RETENTION COMPLIANCE SUMMARY ===" -ForegroundColor Cyan
    $Summary | Format-List

    Write-Host "`n[PASS] Control 1.9 configuration completed successfully" -ForegroundColor Green
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

*Updated: January 2026 | Version: v1.1*
