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

## Related Playbooks

- [Portal Walkthrough](./portal-walkthrough.md) - Step-by-step portal configuration
- [Verification & Testing](./verification-testing.md) - Assessment procedures
- [Troubleshooting](./troubleshooting.md) - Common issues and solutions

---

*Updated: January 2026 | Version: v1.1*
