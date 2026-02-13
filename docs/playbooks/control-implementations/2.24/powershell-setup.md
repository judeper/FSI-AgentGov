# PowerShell Setup: Control 2.24 - Agent Feature Enablement and Restriction Governance

**Last Updated:** February 2026
**Prerequisites:** Power Platform Admin role, PowerShell 7+, Power Platform CLI

## Overview

This playbook provides PowerShell scripts for:
- Deploying the feature catalog to Dataverse
- Auditing feature configuration across environments
- Generating compliance reports for feature usage
- Automating feature restriction validation
- Tracking time-bound exceptions and expiration alerts

---

## Script 1: Deploy Feature Catalog Table

Creates the `fsi_featurecatalog` Dataverse table with all required columns.

```powershell
<#
.SYNOPSIS
    Deploy FSI Feature Catalog table to Dataverse

.DESCRIPTION
    Creates the fsi_featurecatalog table in the specified Dataverse environment
    with all required columns for tracking Copilot Studio feature governance.

.PARAMETER EnvironmentUrl
    URL of the Dataverse environment (e.g., https://contoso.crm.dynamics.com)

.EXAMPLE
    .\Deploy-FeatureCatalog.ps1 -EnvironmentUrl "https://contoso.crm.dynamics.com"
#>

param(
    [Parameter(Mandatory = $true)]
    [string]$EnvironmentUrl
)

# Install required modules
if (-not (Get-Module -ListAvailable -Name Microsoft.PowerApps.Administration.PowerShell)) {
    Install-Module -Name Microsoft.PowerApps.Administration.PowerShell -Scope CurrentUser -Force
}

if (-not (Get-Module -ListAvailable -Name Microsoft.Xrm.Data.PowerShell)) {
    Install-Module -Name Microsoft.Xrm.Data.PowerShell -Scope CurrentUser -Force
}

Import-Module Microsoft.PowerApps.Administration.PowerShell
Import-Module Microsoft.Xrm.Data.PowerShell

# Connect to Dataverse
Write-Host "Connecting to Dataverse environment: $EnvironmentUrl" -ForegroundColor Cyan
$conn = Connect-CrmOnline -ServerUrl $EnvironmentUrl -ForceOAuth

if ($conn.IsReady) {
    Write-Host "Connected successfully to $($conn.ConnectedOrgFriendlyName)" -ForegroundColor Green
} else {
    Write-Error "Failed to connect to Dataverse environment"
    exit 1
}

# Define table schema
$tableName = "fsi_featurecatalog"
$tableDisplayName = "FSI Feature Catalog"
$tableDescription = "Tracks approved and restricted Copilot Studio features per governance zone"

Write-Host "`nCreating table: $tableDisplayName" -ForegroundColor Cyan

# Create table (simplified - actual implementation requires Entity Metadata API calls)
# This is a template - full implementation would use Microsoft.Xrm.Tooling.Connector

$tableDefinition = @{
    LogicalName = $tableName
    DisplayName = @{
        LocalizedLabels = @(
            @{ Label = $tableDisplayName; LanguageCode = 1033 }
        )
    }
    Description = @{
        LocalizedLabels = @(
            @{ Label = $tableDescription; LanguageCode = 1033 }
        )
    }
    OwnershipType = "UserOwned"
    IsActivity = $false
}

Write-Host "Table definition prepared. Columns to create:" -ForegroundColor Cyan

# Define columns
$columns = @(
    @{ Name = "fsi_featurename"; Type = "String"; DisplayName = "Feature Name"; MaxLength = 200; Required = $true },
    @{ Name = "fsi_featurecategory"; Type = "Picklist"; DisplayName = "Feature Category"; Options = @("Generative Actions", "Preview Feature", "Tool", "Plugin", "Orchestration", "Other") },
    @{ Name = "fsi_zone1status"; Type = "Picklist"; DisplayName = "Zone 1 Status"; Options = @("Allowed", "Restricted", "Prohibited") },
    @{ Name = "fsi_zone2status"; Type = "Picklist"; DisplayName = "Zone 2 Status"; Options = @("Allowed", "Restricted", "Prohibited") },
    @{ Name = "fsi_zone3status"; Type = "Picklist"; DisplayName = "Zone 3 Status"; Options = @("Allowed", "Restricted", "Prohibited") },
    @{ Name = "fsi_approvalrequired"; Type = "Boolean"; DisplayName = "Approval Required"; DefaultValue = $false },
    @{ Name = "fsi_approvaldate"; Type = "DateTime"; DisplayName = "Approval Date" },
    @{ Name = "fsi_changeticket"; Type = "String"; DisplayName = "Change Ticket"; MaxLength = 100 },
    @{ Name = "fsi_expirationdate"; Type = "DateTime"; DisplayName = "Expiration Date" },
    @{ Name = "fsi_riskrating"; Type = "Picklist"; DisplayName = "Risk Rating"; Options = @("High", "Medium", "Low") },
    @{ Name = "fsi_justification"; Type = "Memo"; DisplayName = "Justification"; MaxLength = 2000 }
)

foreach ($col in $columns) {
    Write-Host "  - $($col.DisplayName) ($($col.Type))" -ForegroundColor Gray
}

Write-Host "`nNote: Full table creation requires Entity Metadata API calls." -ForegroundColor Yellow
Write-Host "Use Power Apps Maker Portal (make.powerapps.com) to manually create the table with the columns listed above." -ForegroundColor Yellow
Write-Host "Or use the Power Platform CLI: 'pac table create' command." -ForegroundColor Yellow

# Alternative: Create via Power Platform CLI
Write-Host "`n--- Power Platform CLI Commands ---" -ForegroundColor Magenta
Write-Host "pac auth create --url $EnvironmentUrl" -ForegroundColor Gray
Write-Host "pac table create --name $tableName --display-name '$tableDisplayName' --description '$tableDescription'" -ForegroundColor Gray
foreach ($col in $columns) {
    $cliType = switch ($col.Type) {
        "String" { "text" }
        "Memo" { "multilinetext" }
        "Picklist" { "picklist" }
        "Boolean" { "boolean" }
        "DateTime" { "datetime" }
    }
    Write-Host "pac column create --table-name $tableName --name $($col.Name) --display-name '$($col.DisplayName)' --type $cliType" -ForegroundColor Gray
}

Write-Host "`nScript completed. Table schema defined." -ForegroundColor Green
```

**Save as:** `Deploy-FeatureCatalog.ps1`

---

## Script 2: Populate Feature Catalog with Default Features

Adds initial feature records to the catalog with default zone status.

```powershell
<#
.SYNOPSIS
    Populate Feature Catalog with default Copilot Studio features

.DESCRIPTION
    Inserts baseline feature records into fsi_featurecatalog table
    with zone-appropriate restrictions for FSI governance.

.PARAMETER EnvironmentUrl
    URL of the Dataverse environment

.EXAMPLE
    .\Populate-FeatureCatalog.ps1 -EnvironmentUrl "https://contoso.crm.dynamics.com"
#>

param(
    [Parameter(Mandatory = $true)]
    [string]$EnvironmentUrl
)

Import-Module Microsoft.Xrm.Data.PowerShell

# Connect to Dataverse
$conn = Connect-CrmOnline -ServerUrl $EnvironmentUrl -ForceOAuth

if (-not $conn.IsReady) {
    Write-Error "Failed to connect to Dataverse"
    exit 1
}

Write-Host "Connected to Dataverse. Populating feature catalog..." -ForegroundColor Cyan

# Define default features
$features = @(
    @{
        Name = "Generative Actions (AI Builder)"
        Category = "Generative Actions"
        Zone1 = "Allowed"
        Zone2 = "Restricted"
        Zone3 = "Prohibited"
        ApprovalRequired = $true
        RiskRating = "High"
        Justification = "Zone 1: Allowed for personal productivity. Zone 2: Requires documented approval per action. Zone 3: Prohibited unless explicit exception with Compliance Officer approval."
    },
    @{
        Name = "Web Search Tool"
        Category = "Tool"
        Zone1 = "Allowed"
        Zone2 = "Restricted"
        Zone3 = "Prohibited"
        ApprovalRequired = $true
        RiskRating = "Medium"
        Justification = "Zone 1: Allowed. Zone 2: Approved agents only with domain restrictions. Zone 3: Prohibited or explicit allowlist with limited scope."
    },
    @{
        Name = "Code Interpreter"
        Category = "Tool"
        Zone1 = "Allowed"
        Zone2 = "Prohibited"
        Zone3 = "Prohibited"
        ApprovalRequired = $true
        RiskRating = "High"
        Justification = "High-risk feature allowing arbitrary code execution. Zone 1 only for personal sandboxed environments. Prohibited in Zone 2/3."
    },
    @{
        Name = "Custom Plugins"
        Category = "Plugin"
        Zone1 = "Allowed"
        Zone2 = "Restricted"
        Zone3 = "Restricted"
        ApprovalRequired = $true
        RiskRating = "Medium"
        Justification = "Zone 1: User-installed plugins allowed. Zone 2/3: Plugin allowlist with security validation required."
    },
    @{
        Name = "Multi-Agent Orchestration"
        Category = "Orchestration"
        Zone1 = "Allowed"
        Zone2 = "Restricted"
        Zone3 = "Prohibited"
        ApprovalRequired = $true
        RiskRating = "Medium"
        Justification = "Zone 1: Allowed with monitoring. Zone 2: Depth limit (max 2 levels). Zone 3: Prohibited or approval with audit trail."
    },
    @{
        Name = "Preview Features (General)"
        Category = "Preview Feature"
        Zone1 = "Allowed"
        Zone2 = "Prohibited"
        Zone3 = "Prohibited"
        ApprovalRequired = $true
        RiskRating = "High"
        Justification = "Preview features lack GA support and may have security/stability issues. Zone 1: Testing only. Zone 2/3: Prohibited unless temporary exception."
    },
    @{
        Name = "SharePoint Connector"
        Category = "Connector"
        Zone1 = "Allowed"
        Zone2 = "Allowed"
        Zone3 = "Restricted"
        ApprovalRequired = $true
        RiskRating = "Low"
        Justification = "Standard Microsoft connector. Zone 1/2: Allowed. Zone 3: Requires approval for specific SharePoint sites."
    },
    @{
        Name = "Dataverse Connector"
        Category = "Connector"
        Zone1 = "Allowed"
        Zone2 = "Allowed"
        Zone3 = "Restricted"
        ApprovalRequired = $true
        RiskRating = "Low"
        Justification = "Core Power Platform connector. Zone 1/2: Allowed. Zone 3: Requires approval for specific tables."
    },
    @{
        Name = "HTTP Connector"
        Category = "Connector"
        Zone1 = "Allowed"
        Zone2 = "Restricted"
        Zone3 = "Prohibited"
        ApprovalRequired = $true
        RiskRating = "High"
        Justification = "High-risk connector allowing arbitrary HTTP calls. Zone 1: Allowed. Zone 2: Approved endpoints only. Zone 3: Prohibited."
    }
)

$successCount = 0
$errorCount = 0

foreach ($feature in $features) {
    try {
        $record = @{
            "fsi_featurename" = $feature.Name
            "fsi_featurecategory" = [int](("Generative Actions", "Preview Feature", "Tool", "Plugin", "Orchestration", "Other").IndexOf($feature.Category))
            "fsi_zone1status" = [int](("Allowed", "Restricted", "Prohibited").IndexOf($feature.Zone1))
            "fsi_zone2status" = [int](("Allowed", "Restricted", "Prohibited").IndexOf($feature.Zone2))
            "fsi_zone3status" = [int](("Allowed", "Restricted", "Prohibited").IndexOf($feature.Zone3))
            "fsi_approvalrequired" = $feature.ApprovalRequired
            "fsi_riskrating" = [int](("High", "Medium", "Low").IndexOf($feature.RiskRating))
            "fsi_justification" = $feature.Justification
        }
        
        $result = New-CrmRecord -conn $conn -EntityLogicalName "fsi_featurecatalog" -Fields $record
        Write-Host "✓ Created: $($feature.Name)" -ForegroundColor Green
        $successCount++
    }
    catch {
        Write-Host "✗ Failed: $($feature.Name) - $($_.Exception.Message)" -ForegroundColor Red
        $errorCount++
    }
}

Write-Host "`nFeature Catalog Population Summary:" -ForegroundColor Cyan
Write-Host "  Success: $successCount" -ForegroundColor Green
Write-Host "  Errors: $errorCount" -ForegroundColor Red

if ($errorCount -eq 0) {
    Write-Host "`nAll features populated successfully!" -ForegroundColor Green
} else {
    Write-Host "`nSome features failed. Review errors above." -ForegroundColor Yellow
}
```

**Save as:** `Populate-FeatureCatalog.ps1`

---

## Script 3: Audit Environment Feature Configuration

Audits PPAC feature settings across all environments and reports compliance status.

```powershell
<#
.SYNOPSIS
    Audit Copilot Studio feature configuration across environments

.DESCRIPTION
    Retrieves feature settings from Power Platform environments and compares
    against expected zone-based restrictions. Generates compliance report.

.PARAMETER OutputPath
    Path for CSV report output (default: current directory)

.EXAMPLE
    .\Audit-FeatureConfiguration.ps1 -OutputPath "C:\Reports"
#>

param(
    [Parameter(Mandatory = $false)]
    [string]$OutputPath = "."
)

Import-Module Microsoft.PowerApps.Administration.PowerShell

# Connect to Power Platform
Add-PowerAppsAccount

Write-Host "Retrieving Power Platform environments..." -ForegroundColor Cyan
$environments = Get-AdminPowerAppEnvironment

$results = @()

foreach ($env in $environments) {
    Write-Host "Auditing: $($env.DisplayName)" -ForegroundColor Gray
    
    # Determine zone classification (requires environment metadata or naming convention)
    # Example: Environment name contains "PROD-Zone3" or metadata tag
    $zone = "Zone 1"  # Default
    if ($env.DisplayName -match "Zone3|Enterprise|PROD-Z3") {
        $zone = "Zone 3"
    } elseif ($env.DisplayName -match "Zone2|Team|PROD-Z2") {
        $zone = "Zone 2"
    }
    
    # Note: PPAC feature settings are not directly queryable via PowerShell cmdlets as of Feb 2026
    # This script provides a template; actual implementation requires Graph API calls or manual export
    
    $result = [PSCustomObject]@{
        EnvironmentName = $env.DisplayName
        EnvironmentId = $env.EnvironmentName
        Type = $env.EnvironmentType
        Region = $env.Location.name
        Zone = $zone
        GenerativeAIEnabled = "Unknown - Requires Manual Check"
        PreviewFeaturesEnabled = "Unknown - Requires Manual Check"
        CodeInterpreterEnabled = "Unknown - Requires Manual Check"
        ComplianceStatus = "Review Required"
        Notes = "Manual verification needed in PPAC Copilot governance page"
    }
    
    $results += $result
}

# Export results
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$outputFile = Join-Path $OutputPath "FeatureAudit_$timestamp.csv"
$results | Export-Csv -Path $outputFile -NoTypeInformation

Write-Host "`nAudit completed. Results saved to:" -ForegroundColor Green
Write-Host $outputFile -ForegroundColor Yellow

# Display summary
Write-Host "`n--- Audit Summary ---" -ForegroundColor Cyan
Write-Host "Total Environments: $($results.Count)" -ForegroundColor Gray
Write-Host "Zone 1: $(($results | Where-Object {$_.Zone -eq 'Zone 1'}).Count)" -ForegroundColor Gray
Write-Host "Zone 2: $(($results | Where-Object {$_.Zone -eq 'Zone 2'}).Count)" -ForegroundColor Gray
Write-Host "Zone 3: $(($results | Where-Object {$_.Zone -eq 'Zone 3'}).Count)" -ForegroundColor Gray

Write-Host "`nNote: Feature-level settings (generative AI, preview features, tools) are not directly" -ForegroundColor Yellow
Write-Host "accessible via PowerShell cmdlets. Manual verification required in PPAC Copilot governance page." -ForegroundColor Yellow
Write-Host "Alternative: Use Power Platform Admin API or manual CSV export from portal." -ForegroundColor Yellow
```

**Save as:** `Audit-FeatureConfiguration.ps1`

---

## Script 4: Generate Feature Compliance Report

Queries feature catalog and generates compliance report showing feature status and exceptions.

```powershell
<#
.SYNOPSIS
    Generate feature compliance report from feature catalog

.DESCRIPTION
    Retrieves all feature records from Dataverse fsi_featurecatalog table
    and generates compliance report with expiration alerts.

.PARAMETER EnvironmentUrl
    URL of the Dataverse environment containing feature catalog

.PARAMETER OutputPath
    Path for report output

.EXAMPLE
    .\Get-FeatureComplianceReport.ps1 -EnvironmentUrl "https://contoso.crm.dynamics.com" -OutputPath "C:\Reports"
#>

param(
    [Parameter(Mandatory = $true)]
    [string]$EnvironmentUrl,
    
    [Parameter(Mandatory = $false)]
    [string]$OutputPath = "."
)

Import-Module Microsoft.Xrm.Data.PowerShell

# Connect to Dataverse
$conn = Connect-CrmOnline -ServerUrl $EnvironmentUrl -ForceOAuth

if (-not $conn.IsReady) {
    Write-Error "Failed to connect to Dataverse"
    exit 1
}

Write-Host "Connected to Dataverse. Retrieving feature catalog..." -ForegroundColor Cyan

# Query all feature records
$fetchXml = @"
<fetch>
  <entity name="fsi_featurecatalog">
    <attribute name="fsi_featurename" />
    <attribute name="fsi_featurecategory" />
    <attribute name="fsi_zone1status" />
    <attribute name="fsi_zone2status" />
    <attribute name="fsi_zone3status" />
    <attribute name="fsi_approvalrequired" />
    <attribute name="fsi_approvaldate" />
    <attribute name="fsi_changeticket" />
    <attribute name="fsi_expirationdate" />
    <attribute name="fsi_riskrating" />
    <attribute name="fsi_justification" />
  </entity>
</fetch>
"@

$features = Get-CrmRecordsByFetch -conn $conn -Fetch $fetchXml

Write-Host "Retrieved $($features.Count) feature records" -ForegroundColor Green

# Transform to report format
$report = @()
$today = Get-Date

foreach ($feature in $features) {
    $expirationDate = $feature.fsi_expirationdate
    $daysToExpiration = if ($expirationDate) {
        (New-TimeSpan -Start $today -End $expirationDate).Days
    } else {
        $null
    }
    
    $expirationAlert = if ($daysToExpiration -lt 0) {
        "EXPIRED"
    } elseif ($daysToExpiration -le 30) {
        "EXPIRES SOON ($daysToExpiration days)"
    } else {
        "OK"
    }
    
    $reportRow = [PSCustomObject]@{
        FeatureName = $feature.fsi_featurename
        Category = $feature.fsi_featurecategoryname  # Option set formatted value
        Zone1Status = $feature.fsi_zone1statusname
        Zone2Status = $feature.fsi_zone2statusname
        Zone3Status = $feature.fsi_zone3statusname
        ApprovalRequired = $feature.fsi_approvalrequired
        ApprovalDate = $feature.fsi_approvaldate
        ChangeTicket = $feature.fsi_changeticket
        ExpirationDate = $expirationDate
        DaysToExpiration = $daysToExpiration
        ExpirationAlert = $expirationAlert
        RiskRating = $feature.fsi_riskratingname
        Justification = $feature.fsi_justification
    }
    
    $report += $reportRow
}

# Export full report
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$fullReportFile = Join-Path $OutputPath "FeatureComplianceReport_$timestamp.csv"
$report | Export-Csv -Path $fullReportFile -NoTypeInformation

Write-Host "`nFull report saved to:" -ForegroundColor Green
Write-Host $fullReportFile -ForegroundColor Yellow

# Export expiration alerts
$alerts = $report | Where-Object { $_.ExpirationAlert -ne "OK" -and $_.ExpirationAlert -ne $null }
if ($alerts.Count -gt 0) {
    $alertsFile = Join-Path $OutputPath "FeatureExpirationAlerts_$timestamp.csv"
    $alerts | Export-Csv -Path $alertsFile -NoTypeInformation
    Write-Host "`nExpiration alerts saved to:" -ForegroundColor Yellow
    Write-Host $alertsFile -ForegroundColor Yellow
    Write-Host "  - Features expiring or expired: $($alerts.Count)" -ForegroundColor Red
}

# Display summary
Write-Host "`n--- Feature Compliance Summary ---" -ForegroundColor Cyan
Write-Host "Total Features: $($features.Count)" -ForegroundColor Gray
Write-Host "High Risk: $(($report | Where-Object {$_.RiskRating -eq 'High'}).Count)" -ForegroundColor Red
Write-Host "Medium Risk: $(($report | Where-Object {$_.RiskRating -eq 'Medium'}).Count)" -ForegroundColor Yellow
Write-Host "Low Risk: $(($report | Where-Object {$_.RiskRating -eq 'Low'}).Count)" -ForegroundColor Green

Write-Host "`nZone 3 Prohibited Features: $(($report | Where-Object {$_.Zone3Status -eq 'Prohibited'}).Count)" -ForegroundColor Magenta
Write-Host "Zone 3 Restricted (Exceptions): $(($report | Where-Object {$_.Zone3Status -eq 'Restricted'}).Count)" -ForegroundColor Yellow

if ($alerts.Count -gt 0) {
    Write-Host "`n⚠ WARNING: $($alerts.Count) feature(s) have expired or expiring exceptions!" -ForegroundColor Red
    Write-Host "Review expiration alerts report and renew or revoke access." -ForegroundColor Red
} else {
    Write-Host "`n✓ All time-bound exceptions are current (no expirations within 30 days)" -ForegroundColor Green
}
```

**Save as:** `Get-FeatureComplianceReport.ps1`

---

## Script 5: Validate DLP Policy Enforcement

Tests that DLP policies are correctly blocking prohibited connectors.

```powershell
<#
.SYNOPSIS
    Validate DLP policy enforcement for feature restrictions

.DESCRIPTION
    Tests DLP policies across environments to ensure prohibited connectors
    are blocked and allowed connectors are accessible.

.EXAMPLE
    .\Test-DLPEnforcement.ps1
#>

Import-Module Microsoft.PowerApps.Administration.PowerShell

Add-PowerAppsAccount

Write-Host "Retrieving DLP policies..." -ForegroundColor Cyan
$dlpPolicies = Get-AdminDlpPolicy

Write-Host "Found $($dlpPolicies.Count) DLP policies`n" -ForegroundColor Green

$validationResults = @()

foreach ($policy in $dlpPolicies) {
    Write-Host "Analyzing Policy: $($policy.DisplayName)" -ForegroundColor Yellow
    
    # Get connector classifications
    $businessConnectors = $policy.ConnectorGroups | Where-Object { $_.classification -eq "Business" } | Select-Object -ExpandProperty connectors
    $blockedConnectors = $policy.ConnectorGroups | Where-Object { $_.classification -eq "Blocked" } | Select-Object -ExpandProperty connectors
    
    # Check for high-risk connectors in Business group (should be blocked)
    $highRiskConnectors = @("shared_http", "shared_custom")  # HTTP and Custom connectors
    
    foreach ($riskConnector in $highRiskConnectors) {
        $isBlocked = $blockedConnectors.id -contains "/providers/Microsoft.PowerApps/apis/$riskConnector"
        
        $result = [PSCustomObject]@{
            PolicyName = $policy.DisplayName
            Connector = $riskConnector
            ExpectedStatus = "Blocked (High Risk)"
            ActualStatus = if ($isBlocked) { "Blocked" } else { "Allowed" }
            Compliance = if ($isBlocked) { "Compliant" } else { "NON-COMPLIANT" }
            EnvironmentScope = $policy.EnvironmentType
        }
        
        $validationResults += $result
        
        if ($result.Compliance -eq "NON-COMPLIANT") {
            Write-Host "  ✗ $riskConnector is NOT blocked (should be blocked for high-risk environments)" -ForegroundColor Red
        } else {
            Write-Host "  ✓ $riskConnector is blocked" -ForegroundColor Green
        }
    }
}

# Export results
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$outputFile = "DLPValidation_$timestamp.csv"
$validationResults | Export-Csv -Path $outputFile -NoTypeInformation

Write-Host "`nValidation results saved to: $outputFile" -ForegroundColor Green

# Summary
$nonCompliant = $validationResults | Where-Object { $_.Compliance -eq "NON-COMPLIANT" }
if ($nonCompliant.Count -gt 0) {
    Write-Host "`n⚠ WARNING: $($nonCompliant.Count) non-compliant connector(s) found!" -ForegroundColor Red
    Write-Host "Review DLP policies and move high-risk connectors to Blocked group." -ForegroundColor Red
} else {
    Write-Host "`n✓ All high-risk connectors are properly blocked" -ForegroundColor Green
}
```

**Save as:** `Test-DLPEnforcement.ps1`

---

## Usage Guide

### Initial Setup (One-Time)

1. Deploy feature catalog table:
   ```powershell
   .\Deploy-FeatureCatalog.ps1 -EnvironmentUrl "https://contoso.crm.dynamics.com"
   ```

2. Populate with default features:
   ```powershell
   .\Populate-FeatureCatalog.ps1 -EnvironmentUrl "https://contoso.crm.dynamics.com"
   ```

### Ongoing Operations

**Monthly:** Generate feature compliance report:
```powershell
.\Get-FeatureComplianceReport.ps1 -EnvironmentUrl "https://contoso.crm.dynamics.com" -OutputPath "C:\Reports"
```

**Quarterly:** Audit environment configuration:
```powershell
.\Audit-FeatureConfiguration.ps1 -OutputPath "C:\Reports"
```

**After DLP Changes:** Validate DLP enforcement:
```powershell
.\Test-DLPEnforcement.ps1
```

---

## Automation Recommendations

1. **Schedule monthly report generation** using Azure Automation or Windows Task Scheduler
2. **Email expiration alerts** to AI Governance Lead when features expire within 30 days
3. **Integrate with change management system** to auto-update feature catalog on approval
4. **Export to Power BI** for dashboard visualization of feature usage and compliance trends

---

[Back to Control 2.24](../../../controls/pillar-2-management/2.24-agent-feature-enablement-and-restriction-governance.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
