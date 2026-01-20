# Control 2.7: Vendor and Third-Party Risk Management - PowerShell Setup

> This playbook provides PowerShell automation scripts for [Control 2.7](../../../controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md).

---

## Prerequisites

```powershell
# Install Power Platform admin module
Install-Module -Name Microsoft.PowerApps.Administration.PowerShell -Force

# Connect to Power Platform
Add-PowerAppsAccount

# Verify connection
Get-AdminPowerAppEnvironment | Select-Object DisplayName, EnvironmentName | Format-Table
```

---

## Get Connectors in Use

```powershell
# Get all apps across environments
$environments = Get-AdminPowerAppEnvironment

$connectorUsage = @()

foreach ($env in $environments) {
    Write-Host "Scanning environment: $($env.DisplayName)" -ForegroundColor Cyan

    # Get apps in environment
    $apps = Get-AdminPowerApp -EnvironmentName $env.EnvironmentName

    foreach ($app in $apps) {
        Write-Host "  App: $($app.DisplayName)"
    }

    # Get flows in environment
    $flows = Get-AdminFlow -EnvironmentName $env.EnvironmentName

    foreach ($flow in $flows) {
        Write-Host "  Flow: $($flow.DisplayName)"
    }
}

Write-Host "`nTotal environments scanned: $($environments.Count)"
```

---

## Export Connector Inventory

```powershell
# Export detailed connector inventory
function Export-ConnectorInventory {
    param(
        [string]$OutputPath = ".\ConnectorInventory.csv"
    )

    $environments = Get-AdminPowerAppEnvironment
    $inventory = @()

    foreach ($env in $environments) {
        # Get DLP policies for environment
        $dlpPolicies = Get-DlpPolicy | Where-Object {
            $_.environments.name -contains $env.EnvironmentName -or
            $_.environmentType -eq "AllEnvironments"
        }

        $inventory += [PSCustomObject]@{
            EnvironmentName = $env.DisplayName
            EnvironmentId = $env.EnvironmentName
            EnvironmentType = $env.EnvironmentType
            DLPPoliciesApplied = ($dlpPolicies | Measure-Object).Count
            AssessmentDate = Get-Date -Format "yyyy-MM-dd"
        }
    }

    $inventory | Export-Csv -Path $OutputPath -NoTypeInformation
    Write-Host "Exported connector inventory to: $OutputPath" -ForegroundColor Green

    return $inventory
}

# Run export
$connectorInventory = Export-ConnectorInventory -OutputPath ".\VendorConnectorInventory.csv"
$connectorInventory | Format-Table
```

---

## Review Connector Permissions

```powershell
# Review DLP policies and connector classifications
function Get-ConnectorPolicyReport {
    $dlpPolicies = Get-DlpPolicy

    $report = @()

    foreach ($policy in $dlpPolicies) {
        Write-Host "`n=== Policy: $($policy.displayName) ===" -ForegroundColor Cyan

        # Get connector groups
        $businessGroup = $policy.connectorGroups | Where-Object { $_.classification -eq "General" }
        $nonBusinessGroup = $policy.connectorGroups | Where-Object { $_.classification -eq "Confidential" }
        $blockedGroup = $policy.connectorGroups | Where-Object { $_.classification -eq "Blocked" }

        $report += [PSCustomObject]@{
            PolicyName = $policy.displayName
            PolicyType = $policy.environmentType
            BusinessConnectors = ($businessGroup.connectors | Measure-Object).Count
            NonBusinessConnectors = ($nonBusinessGroup.connectors | Measure-Object).Count
            BlockedConnectors = ($blockedGroup.connectors | Measure-Object).Count
            CreatedTime = $policy.createdTime
            LastModified = $policy.lastModifiedTime
        }
    }

    return $report
}

$policyReport = Get-ConnectorPolicyReport
$policyReport | Format-Table -AutoSize
$policyReport | Export-Csv -Path ".\DLPPolicyReport.csv" -NoTypeInformation
```

---

## Monitor Custom Connectors

```powershell
# Get all custom connectors across environments
function Get-CustomConnectorInventory {
    $environments = Get-AdminPowerAppEnvironment
    $customConnectors = @()

    foreach ($env in $environments) {
        $connectors = Get-AdminPowerAppConnector -EnvironmentName $env.EnvironmentName

        foreach ($connector in $connectors) {
            $customConnectors += [PSCustomObject]@{
                ConnectorName = $connector.displayName
                ConnectorId = $connector.name
                Environment = $env.DisplayName
                Publisher = $connector.properties.publisher
                CreatedBy = $connector.properties.createdBy.displayName
                CreatedTime = $connector.properties.createdTime
                ApiDefinitionUrl = $connector.properties.apiDefinitionUrl
            }
        }
    }

    return $customConnectors
}

$customConnectors = Get-CustomConnectorInventory
Write-Host "`nCustom Connectors Found: $($customConnectors.Count)" -ForegroundColor Yellow
$customConnectors | Format-Table -AutoSize
$customConnectors | Export-Csv -Path ".\CustomConnectorInventory.csv" -NoTypeInformation
```

---

## Audit Dynamic Tool Usage

```powershell
# Audit tool and plugin usage across agents
function Get-DynamicToolUsage {
    param(
        [DateTime]$StartDate = (Get-Date).AddDays(-30),
        [string]$OutputPath = ".\Tool-Usage-Audit"
    )

    New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null

    Write-Host "Auditing dynamic tool usage..." -ForegroundColor Cyan

    # Get all environments
    $environments = Get-AdminPowerAppEnvironment

    $toolUsage = @()

    foreach ($env in $environments) {
        Write-Host "Scanning: $($env.DisplayName)" -ForegroundColor Yellow

        # Get connectors in use
        $connectors = Get-AdminPowerAppConnector -EnvironmentName $env.EnvironmentName

        foreach ($connector in $connectors) {
            $toolUsage += [PSCustomObject]@{
                Environment = $env.DisplayName
                ConnectorName = $connector.displayName
                ConnectorId = $connector.name
                Publisher = $connector.properties.publisher
                PublisherType = if ($connector.properties.publisher -eq "Microsoft") { "First-Party" }
                    elseif ($connector.properties.isTrusted) { "Verified" }
                    else { "Community/Custom" }
                CreatedBy = $connector.properties.createdBy.displayName
                CreatedTime = $connector.properties.createdTime
                RiskLevel = if ($connector.properties.publisher -ne "Microsoft") { "Review Required" } else { "Standard" }
            }
        }
    }

    # Export findings
    $toolUsage | Export-Csv -Path "$OutputPath\Tool-Usage-Audit.csv" -NoTypeInformation

    # Identify high-risk tools
    $highRisk = $toolUsage | Where-Object { $_.PublisherType -eq "Community/Custom" }

    if ($highRisk.Count -gt 0) {
        Write-Host "`nHIGH-RISK TOOLS DETECTED: $($highRisk.Count)" -ForegroundColor Red
        $highRisk | Format-Table Environment, ConnectorName, Publisher -AutoSize
        $highRisk | Export-Csv -Path "$OutputPath\High-Risk-Tools.csv" -NoTypeInformation
    }

    Write-Host "`nAudit complete. Output: $OutputPath" -ForegroundColor Green
    return $toolUsage
}

# Run audit
# Get-DynamicToolUsage
```

---

## Complete Configuration Script

```powershell
<#
.SYNOPSIS
    Complete vendor and third-party risk assessment for Control 2.7

.DESCRIPTION
    Executes end-to-end vendor risk assessment including:
    - Connector inventory collection
    - DLP policy analysis
    - Third-party risk identification
    - Compliance report generation

.PARAMETER OutputPath
    Path for output reports

.EXAMPLE
    .\Configure-Control-2.7.ps1 -OutputPath ".\VendorRisk"

.NOTES
    Last Updated: January 2026
    Related Control: Control 2.7 - Vendor and Third-Party Risk Management
#>

param(
    [string]$OutputPath = ".\VendorRisk-Report"
)

try {
    Write-Host "=== Control 2.7: Vendor and Third-Party Risk Configuration ===" -ForegroundColor Cyan

    # Connect to Power Platform
    Add-PowerAppsAccount

    # Ensure output directory exists
    New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null

    # Get all environments
    $environments = Get-AdminPowerAppEnvironment
    Write-Host "[INFO] Found $($environments.Count) environments" -ForegroundColor Cyan

    # Collect connector inventory
    $connectorInventory = @()
    foreach ($env in $environments) {
        Write-Host "  Scanning: $($env.DisplayName)" -ForegroundColor Yellow
        $connectors = Get-AdminPowerAppConnector -EnvironmentName $env.EnvironmentName -ErrorAction SilentlyContinue

        foreach ($connector in $connectors) {
            $connectorInventory += [PSCustomObject]@{
                Environment = $env.DisplayName
                ConnectorName = $connector.displayName
                Publisher = $connector.properties.publisher
                IsFirstParty = $connector.properties.publisher -eq "Microsoft"
                CreatedBy = $connector.properties.createdBy.displayName
                CreatedTime = $connector.properties.createdTime
                AssessmentDate = Get-Date -Format "yyyy-MM-dd"
            }
        }
    }

    # Export connector inventory
    $connectorInventory | Export-Csv -Path "$OutputPath\ConnectorInventory.csv" -NoTypeInformation
    Write-Host "`n[INFO] Connector inventory exported: $($connectorInventory.Count) connectors" -ForegroundColor Cyan

    # Get DLP policies
    $dlpPolicies = Get-DlpPolicy -ErrorAction SilentlyContinue
    if ($dlpPolicies) {
        Write-Host "[INFO] Found $($dlpPolicies.Count) DLP policies" -ForegroundColor Cyan
        $dlpPolicies | Select-Object displayName, environmentType, createdTime |
            Export-Csv -Path "$OutputPath\DLPPolicies.csv" -NoTypeInformation
    }

    # Identify third-party connectors
    $thirdParty = $connectorInventory | Where-Object { -not $_.IsFirstParty }
    if ($thirdParty.Count -gt 0) {
        Write-Host "[WARN] Third-party connectors found: $($thirdParty.Count)" -ForegroundColor Yellow
        $thirdParty | Export-Csv -Path "$OutputPath\ThirdPartyConnectors.csv" -NoTypeInformation
    }

    # Summary
    Write-Host "`n=== Summary ===" -ForegroundColor Cyan
    Write-Host "Total Environments: $($environments.Count)"
    Write-Host "Total Connectors: $($connectorInventory.Count)"
    Write-Host "First-Party: $(($connectorInventory | Where-Object { $_.IsFirstParty }).Count)"
    Write-Host "Third-Party: $($thirdParty.Count)"

    Write-Host "`n[PASS] Control 2.7 configuration completed successfully" -ForegroundColor Green
}
catch {
    Write-Host "[FAIL] Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "[INFO] Stack trace: $($_.ScriptStackTrace)" -ForegroundColor Yellow
    exit 1
}
finally {
    # Cleanup connections if applicable
    # Note: Add-PowerAppsAccount does not require explicit disconnect
}
```

---

## Related Playbooks

- [Portal Walkthrough](./portal-walkthrough.md) - Step-by-step portal configuration
- [Verification & Testing](./verification-testing.md) - Assessment procedures
- [Troubleshooting](./troubleshooting.md) - Common issues and solutions

---

*Updated: January 2026 | Version: v1.1*
