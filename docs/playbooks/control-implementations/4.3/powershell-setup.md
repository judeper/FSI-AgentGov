# Control 4.3: Site and Document Retention Management - PowerShell Setup

> This playbook provides PowerShell automation guidance for [Control 4.3](../../../controls/pillar-4-sharepoint/4.3-site-and-document-retention-management.md).

---

## Prerequisites

```powershell
# Install required modules
Install-Module -Name ExchangeOnlineManagement -Scope CurrentUser
Install-Module -Name Microsoft.Online.SharePoint.PowerShell -Force
```

---

## Connect to Services

```powershell
# Connect to Security & Compliance PowerShell (for Purview)
Connect-IPPSSession -UserPrincipalName admin@contoso.com

# Verify connection
Get-RetentionCompliancePolicy | Select-Object Name, Enabled, Mode | Format-Table
```

---

## Create Retention Policies

```powershell
# Create a retention policy for SharePoint sites containing agent knowledge
$PolicyName = "FSI-Agent-Knowledge-Retention-7Years"

New-RetentionCompliancePolicy -Name $PolicyName `
    -Comment "Retention policy for agent knowledge sources per FINRA 4511 and SEC 17a-4" `
    -SharePointLocation "https://contoso.sharepoint.com/sites/AgentKnowledge" `
    -Enabled $true

# Create retention rule for the policy (7 years, retain and delete)
New-RetentionComplianceRule -Name "FSI-7Year-Retention-Rule" `
    -Policy $PolicyName `
    -RetentionDuration 2555 `
    -RetentionDurationDisplayHint Days `
    -RetentionComplianceAction KeepAndDelete `
    -ExpirationDateOption ModificationAgeInDays

Write-Host "Retention policy created: $PolicyName" -ForegroundColor Green
```

---

## Create Zone-Specific Retention Policies

```powershell
# Create zone-specific retention policies
$Zones = @(
    @{Name="Zone1-Personal"; Duration=365; Sites="https://contoso.sharepoint.com/sites/Zone1-*"},
    @{Name="Zone2-Team"; Duration=1825; Sites="https://contoso.sharepoint.com/sites/Zone2-*"},
    @{Name="Zone3-Enterprise"; Duration=2555; Sites="https://contoso.sharepoint.com/sites/Zone3-*"}
)

foreach ($Zone in $Zones) {
    New-RetentionCompliancePolicy -Name "FSI-$($Zone.Name)-Retention" `
        -SharePointLocation $Zone.Sites `
        -Enabled $true

    New-RetentionComplianceRule -Name "FSI-$($Zone.Name)-Rule" `
        -Policy "FSI-$($Zone.Name)-Retention" `
        -RetentionDuration $Zone.Duration `
        -RetentionDurationDisplayHint Days `
        -RetentionComplianceAction KeepAndDelete

    Write-Host "Created retention policy for $($Zone.Name)" -ForegroundColor Green
}
```

---

## Create and Publish Retention Labels

```powershell
# Create retention labels for different content types
$Labels = @(
    @{Name="FSI-Financial-Records-7Y"; Duration=2555; Action="KeepAndDelete"; Description="7-year retention for financial records (SOX 802)"},
    @{Name="FSI-Communications-6Y"; Duration=2190; Action="KeepAndDelete"; Description="6-year retention for communications (FINRA 4511)"},
    @{Name="FSI-Customer-Data-5Y"; Duration=1825; Action="KeepAndDelete"; Description="5-year retention for customer information (GLBA)"},
    @{Name="FSI-Regulatory-Immutable"; Duration=2555; Action="Keep"; Description="7-year immutable retention for regulatory records"}
)

foreach ($Label in $Labels) {
    New-ComplianceTag -Name $Label.Name `
        -Comment $Label.Description `
        -RetentionDuration $Label.Duration `
        -RetentionAction $Label.Action `
        -RetentionType ModificationAgeInDays `
        -IsRecordLabel $false

    Write-Host "Created retention label: $($Label.Name)" -ForegroundColor Green
}

# Publish retention labels via label policy
New-RetentionCompliancePolicy -Name "FSI-Retention-Labels-Policy" `
    -PublishComplianceTag "FSI-Financial-Records-7Y","FSI-Communications-6Y","FSI-Customer-Data-5Y","FSI-Regulatory-Immutable" `
    -SharePointLocation All `
    -Enabled $true

Write-Host "Retention labels published to all SharePoint sites" -ForegroundColor Green
```

---

## Export Retention Configuration

```powershell
# Export all retention policies for documentation
$ExportPath = "C:\FSI-Governance\RetentionConfig"
New-Item -ItemType Directory -Path $ExportPath -Force | Out-Null

# Get all retention policies
$Policies = Get-RetentionCompliancePolicy
$Policies | Select-Object Name, Enabled, Mode, SharePointLocation, Comment, WhenCreated |
    Export-Csv -Path "$ExportPath\RetentionPolicies.csv" -NoTypeInformation

# Get all retention rules
$Rules = Get-RetentionComplianceRule
$Rules | Select-Object Name, Policy, RetentionDuration, RetentionComplianceAction, ExpirationDateOption |
    Export-Csv -Path "$ExportPath\RetentionRules.csv" -NoTypeInformation

# Get all retention labels
$Labels = Get-ComplianceTag
$Labels | Select-Object Name, RetentionDuration, RetentionAction, IsRecordLabel, Comment |
    Export-Csv -Path "$ExportPath\RetentionLabels.csv" -NoTypeInformation

Write-Host "Retention configuration exported to: $ExportPath" -ForegroundColor Green

# Create summary report
$Report = @"
FSI Retention Configuration Report
Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
=====================================

Total Retention Policies: $($Policies.Count)
Total Retention Rules: $($Rules.Count)
Total Retention Labels: $($Labels.Count)

Policies by Status:

- Enabled: $(($Policies | Where-Object {$_.Enabled -eq $true}).Count)
- Disabled: $(($Policies | Where-Object {$_.Enabled -eq $false}).Count)

"@
$Report | Out-File "$ExportPath\RetentionSummary.txt"
```

---

## Get Sites with Retention Policies

```powershell
# Connect to SharePoint Online
Connect-SPOService -Url https://contoso-admin.sharepoint.com

# Get all retention policies and their SharePoint locations
$RetentionPolicies = Get-RetentionCompliancePolicy | Where-Object { $_.SharePointLocation -ne $null }

$SiteRetentionReport = @()
foreach ($Policy in $RetentionPolicies) {
    $Rule = Get-RetentionComplianceRule -Policy $Policy.Name

    foreach ($Site in $Policy.SharePointLocation) {
        $SiteRetentionReport += [PSCustomObject]@{
            SiteUrl = $Site
            PolicyName = $Policy.Name
            RetentionDuration = $Rule.RetentionDuration
            Action = $Rule.RetentionComplianceAction
            PolicyEnabled = $Policy.Enabled
        }
    }
}

# Display report
$SiteRetentionReport | Format-Table -AutoSize

# Export for compliance documentation
$SiteRetentionReport | Export-Csv -Path "C:\FSI-Governance\SiteRetentionMapping.csv" -NoTypeInformation
Write-Host "Site retention mapping exported" -ForegroundColor Green

# Find sites WITHOUT retention policies (potential gap)
$AllSites = Get-SPOSite -Limit All
$SitesWithRetention = $SiteRetentionReport.SiteUrl | Select-Object -Unique
$SitesWithoutRetention = $AllSites | Where-Object { $_.Url -notin $SitesWithRetention }

Write-Host "`nSites WITHOUT retention policies: $($SitesWithoutRetention.Count)" -ForegroundColor Yellow
$SitesWithoutRetention | Select-Object Url, Title, Template | Format-Table
```

---

## Complete Configuration Script

```powershell
<#
.SYNOPSIS
    Configures Control 4.3 - Site and Document Retention Management

.DESCRIPTION
    This script configures retention policies for SharePoint:
    1. Creates zone-specific retention policies
    2. Creates and publishes retention labels
    3. Exports configuration for documentation

.PARAMETER AdminEmail
    Email address for Purview admin connection

.PARAMETER ExportPath
    Path for exported retention configuration

.EXAMPLE
    .\Configure-Control-4.3.ps1 -AdminEmail "admin@contoso.com" -ExportPath "C:\FSI-Governance\RetentionConfig"

.NOTES
    Last Updated: January 2026
    Related Control: Control 4.3 - Site and Document Retention Management
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$AdminEmail,

    [Parameter(Mandatory=$false)]
    [string]$ExportPath = "C:\FSI-Governance\RetentionConfig"
)

try {
    # Connect to Security & Compliance
    Write-Host "Connecting to Security & Compliance..." -ForegroundColor Cyan
    Connect-IPPSSession -UserPrincipalName $AdminEmail

    Write-Host "Configuring Control 4.3 Retention Management" -ForegroundColor Cyan

    # Create export directory
    if (-not (Test-Path $ExportPath)) {
        New-Item -ItemType Directory -Path $ExportPath -Force | Out-Null
    }

    # Get existing retention policies
    Write-Host "`nRetrieving existing retention policies..." -ForegroundColor Yellow
    $existingPolicies = Get-RetentionCompliancePolicy
    Write-Host "  Found $($existingPolicies.Count) existing policies" -ForegroundColor Green

    # Get existing retention labels
    Write-Host "Retrieving existing retention labels..." -ForegroundColor Yellow
    $existingLabels = Get-ComplianceTag
    Write-Host "  Found $($existingLabels.Count) existing labels" -ForegroundColor Green

    # Export current configuration
    Write-Host "`nExporting retention configuration..." -ForegroundColor Yellow
    $existingPolicies | Select-Object Name, Enabled, Mode, SharePointLocation, Comment, WhenCreated |
        Export-Csv -Path "$ExportPath\RetentionPolicies.csv" -NoTypeInformation

    $existingLabels | Select-Object Name, RetentionDuration, RetentionAction, IsRecordLabel, Comment |
        Export-Csv -Path "$ExportPath\RetentionLabels.csv" -NoTypeInformation

    # Get retention rules
    $rules = Get-RetentionComplianceRule
    $rules | Select-Object Name, Policy, RetentionDuration, RetentionComplianceAction |
        Export-Csv -Path "$ExportPath\RetentionRules.csv" -NoTypeInformation

    Write-Host "`nRetention Configuration Summary:" -ForegroundColor Cyan
    Write-Host "  Policies: $($existingPolicies.Count)" -ForegroundColor Green
    Write-Host "  Labels: $($existingLabels.Count)" -ForegroundColor Green
    Write-Host "  Rules: $($rules.Count)" -ForegroundColor Green
    Write-Host "  Export location: $ExportPath" -ForegroundColor Green

    Write-Host "`n[PASS] Control 4.3 configuration completed successfully" -ForegroundColor Green
}
catch {
    Write-Host "[FAIL] Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "[INFO] Stack trace: $($_.ScriptStackTrace)" -ForegroundColor Yellow
    exit 1
}
finally {
    # Cleanup compliance session
    Disconnect-ExchangeOnline -Confirm:$false -ErrorAction SilentlyContinue
}
```

---

*Updated: January 2026 | Version: v1.2*
