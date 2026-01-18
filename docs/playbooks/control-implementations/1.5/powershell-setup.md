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

*Updated: January 2026 | Version: v1.1*
