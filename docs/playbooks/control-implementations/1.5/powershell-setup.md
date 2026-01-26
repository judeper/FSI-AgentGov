# Control 1.5: Data Loss Prevention (DLP) and Sensitivity Labels - PowerShell Setup

> This playbook provides PowerShell automation guidance for [Control 1.5](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md).

---

## Prerequisites

```powershell
# Install module if needed
Install-Module -Name ExchangeOnlineManagement -Force
```

---

## Connect to Security & Compliance Center

```powershell
# Connect to Security & Compliance Center
Connect-IPPSSession -UserPrincipalName admin@contoso.com

# Verify connection
Get-DlpCompliancePolicy | Select-Object Name, Mode, Enabled
```

---

## Create AI-Focused DLP Policy

```powershell
# Create DLP policy for AI applications
$policyParams = @{
    Name = "FSI-AI-Data-Protection"
    Comment = "Protect sensitive data in AI applications"
    Mode = "Enable"  # Use "TestWithNotifications" for testing
    Priority = 1
    ExchangeLocation = "All"
    SharePointLocation = "All"
    OneDriveLocation = "All"
    TeamsLocation = "All"
}

$policy = New-DlpCompliancePolicy @policyParams

# Create rule for SSN protection
$ruleParams = @{
    Name = "Block SSN in AI Interactions"
    Policy = "FSI-AI-Data-Protection"
    ContentContainsSensitiveInformation = @{
        Name = "U.S. Social Security Number (SSN)"
        minCount = 1
    }
    BlockAccess = $true
    NotifyUser = "SiteAdmin"
    GenerateIncidentReport = "SiteAdmin"
}

New-DlpComplianceRule @ruleParams
```

---

## Create Sensitivity Label-Based DLP Rule

```powershell
# Rule to block Highly Confidential content in AI
$labelRuleParams = @{
    Name = "Block Highly Confidential from AI"
    Policy = "FSI-AI-Data-Protection"
    ContentPropertyContainsWords = @{
        "Document.SensitivityLabel" = "Highly Confidential"
    }
    BlockAccess = $true
    NotifyUser = "SiteAdmin,LastModifier"
    NotifyEndpointUser = "NotifyUser"
    GenerateIncidentReport = "SiteAdmin"
    IncidentReportContent = "All"
}

New-DlpComplianceRule @labelRuleParams
```

---

## Audit DLP Policies

```powershell
# Get all DLP policies and their status
Get-DlpCompliancePolicy | Format-Table Name, Mode, Enabled, CreatedBy, WhenCreated

# Get DLP rules for a specific policy
Get-DlpComplianceRule -Policy "FSI-AI-Data-Protection" |
    Select-Object Name, Priority, BlockAccess, Disabled

# Get DLP policy details
Get-DlpCompliancePolicy -Identity "FSI-AI-Data-Protection" |
    Select-Object * | Format-List

# Export policy configuration for documentation
Get-DlpCompliancePolicy |
    Select-Object Name, Mode, Enabled, SharePointLocation, TeamsLocation, ExchangeLocation |
    Export-Csv -Path "DLP-Policies-Report.csv" -NoTypeInformation
```

---

## Monitor DLP Alerts

```powershell
# Search audit log for DLP events
$startDate = (Get-Date).AddDays(-30)
$endDate = Get-Date

Search-UnifiedAuditLog -StartDate $startDate -EndDate $endDate `
    -RecordType DLP -ResultSize 5000 |
    Select-Object CreationDate, UserIds, Operations, AuditData |
    Export-Csv -Path "DLP-Audit-Log.csv" -NoTypeInformation

# Parse DLP events for AI-related incidents
$dlpEvents = Search-UnifiedAuditLog -StartDate $startDate -EndDate $endDate `
    -RecordType DLP -ResultSize 1000

foreach ($event in $dlpEvents) {
    $data = $event.AuditData | ConvertFrom-Json
    if ($data.Workload -match "Copilot|Agent") {
        Write-Host "AI DLP Event: $($data.Operation) - $($data.ObjectId)"
    }
}
```

---

## Get Sensitivity Label Statistics

```powershell
# Connect to Microsoft Graph for label info
Connect-MgGraph -Scopes "InformationProtectionPolicy.Read.All"

# Get sensitivity labels
Get-MgBetaInformationProtectionSensitivityPolicyLabel |
    Select-Object Id, Name, Description, IsDefault |
    Format-Table

# Check label usage via compliance search
$labelSearch = New-ComplianceSearch -Name "Highly-Confidential-Content" `
    -ContentMatchQuery 'SensitivityLabelId:<label-guid>' `
    -ExchangeLocation All -SharePointLocation All

Start-ComplianceSearch -Identity "Highly-Confidential-Content"
```

---

## FSI-Specific SIT Configuration

```powershell
# Example: Create rule for financial data types
$fsiRuleParams = @{
    Name = "Block Financial Data in AI"
    Policy = "FSI-AI-Data-Protection"
    ContentContainsSensitiveInformation = @(
        @{Name = "U.S. Social Security Number (SSN)"; minCount = 1},
        @{Name = "ABA Routing Number"; minCount = 1},
        @{Name = "Credit Card Number"; minCount = 1},
        @{Name = "U.S. Bank Account Number"; minCount = 1}
    )
    BlockAccess = $true
    NotifyUser = "SiteAdmin"
    GenerateIncidentReport = "SiteAdmin"
    IncidentReportContent = "All"
}

New-DlpComplianceRule @fsiRuleParams
```

---

## Complete Configuration Script

```powershell
<#
.SYNOPSIS
    Configures Control 1.5 - Data Loss Prevention (DLP) and Sensitivity Labels

.DESCRIPTION
    This script:
    1. Creates an AI-focused DLP policy
    2. Creates DLP rules for sensitive information types
    3. Creates sensitivity label-based DLP rule
    4. Validates policy deployment

.PARAMETER PolicyName
    Name for the DLP policy (default: FSI-AI-Data-Protection)

.PARAMETER TestMode
    If true, creates policy in test mode with notifications

.EXAMPLE
    .\Configure-Control-1.5.ps1 -PolicyName "FSI-AI-Data-Protection"

.NOTES
    Last Updated: January 2026
    Related Control: Control 1.5 - Data Loss Prevention (DLP) and Sensitivity Labels
#>

param(
    [Parameter(Mandatory=$false)]
    [string]$PolicyName = "FSI-AI-Data-Protection",

    [Parameter(Mandatory=$false)]
    [switch]$TestMode
)

try {
    # Connect to Security & Compliance Center
    Connect-IPPSSession

    Write-Host "=== Configuring Control 1.5: DLP and Sensitivity Labels ===" -ForegroundColor Cyan

    $PolicyMode = if ($TestMode) { "TestWithNotifications" } else { "Enable" }

    # Step 1: Create AI-focused DLP policy
    Write-Host "`nStep 1: Creating DLP policy..." -ForegroundColor White
    $policyParams = @{
        Name = $PolicyName
        Comment = "Protect sensitive data in AI applications"
        Mode = $PolicyMode
        Priority = 1
        ExchangeLocation = "All"
        SharePointLocation = "All"
        OneDriveLocation = "All"
        TeamsLocation = "All"
    }

    $policy = New-DlpCompliancePolicy @policyParams
    Write-Host "  [DONE] Created DLP policy: $PolicyName" -ForegroundColor Green

    # Step 2: Create rule for SSN protection
    Write-Host "`nStep 2: Creating SSN protection rule..." -ForegroundColor White
    $ssnRuleParams = @{
        Name = "Block SSN in AI Interactions"
        Policy = $PolicyName
        ContentContainsSensitiveInformation = @{
            Name = "U.S. Social Security Number (SSN)"
            minCount = 1
        }
        BlockAccess = $true
        NotifyUser = "SiteAdmin"
        GenerateIncidentReport = "SiteAdmin"
    }

    New-DlpComplianceRule @ssnRuleParams
    Write-Host "  [DONE] Created SSN protection rule" -ForegroundColor Green

    # Step 3: Create rule for financial data types
    Write-Host "`nStep 3: Creating financial data protection rule..." -ForegroundColor White
    $fsiRuleParams = @{
        Name = "Block Financial Data in AI"
        Policy = $PolicyName
        ContentContainsSensitiveInformation = @(
            @{Name = "ABA Routing Number"; minCount = 1},
            @{Name = "Credit Card Number"; minCount = 1},
            @{Name = "U.S. Bank Account Number"; minCount = 1}
        )
        BlockAccess = $true
        NotifyUser = "SiteAdmin"
        GenerateIncidentReport = "SiteAdmin"
        IncidentReportContent = "All"
    }

    New-DlpComplianceRule @fsiRuleParams
    Write-Host "  [DONE] Created financial data protection rule" -ForegroundColor Green

    # Step 4: Create sensitivity label-based rule
    Write-Host "`nStep 4: Creating sensitivity label rule..." -ForegroundColor White
    $labelRuleParams = @{
        Name = "Block Highly Confidential from AI"
        Policy = $PolicyName
        ContentPropertyContainsWords = @{
            "Document.SensitivityLabel" = "Highly Confidential"
        }
        BlockAccess = $true
        NotifyUser = "SiteAdmin,LastModifier"
        GenerateIncidentReport = "SiteAdmin"
        IncidentReportContent = "All"
    }

    New-DlpComplianceRule @labelRuleParams
    Write-Host "  [DONE] Created sensitivity label rule" -ForegroundColor Green

    # Step 5: Validate and export policy configuration
    Write-Host "`nStep 5: Validating configuration..." -ForegroundColor White
    Get-DlpCompliancePolicy -Identity $PolicyName |
        Select-Object Name, Mode, Enabled, SharePointLocation, TeamsLocation |
        Format-List

    Get-DlpComplianceRule -Policy $PolicyName |
        Select-Object Name, Priority, BlockAccess, Disabled |
        Format-Table -AutoSize

    # Export for documentation
    Get-DlpCompliancePolicy |
        Select-Object Name, Mode, Enabled, SharePointLocation, TeamsLocation, ExchangeLocation |
        Export-Csv -Path "DLP-Policies-Report-$(Get-Date -Format 'yyyyMMdd').csv" -NoTypeInformation
    Write-Host "  [DONE] Policy configuration exported" -ForegroundColor Green

    Write-Host "`n[PASS] Control 1.5 configuration completed successfully" -ForegroundColor Green
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
