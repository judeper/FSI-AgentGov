# PowerShell Setup: Control 1.2 - Agent Registry and Integrated Apps Management

**Last Updated:** January 2026
**Modules Required:** Microsoft.PowerApps.Administration.PowerShell, Microsoft.Graph

## Prerequisites

```powershell
# Install required modules
Install-Module -Name Microsoft.PowerApps.Administration.PowerShell -Force
Install-Module -Name Microsoft.Graph -Force

# Connect to Power Platform
Add-PowerAppsAccount

# Connect to Microsoft Graph
Connect-MgGraph -Scopes "Application.Read.All"
```

---

## Agent Discovery Script

### Get All Copilot Studio Agents Across Environments

```powershell
# Agent Registry Automation Script
# Requires: Power Platform Admin PowerShell module

# Get all Copilot Studio agents across environments
$AllEnvironments = Get-AdminPowerAppEnvironment
$AgentInventory = @()

foreach ($Env in $AllEnvironments) {
    Write-Host "Scanning environment: $($Env.DisplayName)" -ForegroundColor Cyan

    # Get Canvas Apps (includes Copilot Studio agents)
    $Apps = Get-AdminPowerApp -EnvironmentName $Env.EnvironmentName

    foreach ($App in $Apps) {
        $AgentInventory += [PSCustomObject]@{
            AgentName = $App.DisplayName
            AgentID = $App.AppName
            Environment = $Env.DisplayName
            EnvironmentID = $Env.EnvironmentName
            Owner = $App.Owner.displayName
            OwnerEmail = $App.Owner.email
            CreatedTime = $App.CreatedTime
            LastModifiedTime = $App.LastModifiedTime
            AppType = $App.AppType
        }
    }
}

# Export to CSV
$ExportPath = "C:\Governance\AgentInventory-$(Get-Date -Format 'yyyyMMdd').csv"
$AgentInventory | Export-Csv -Path $ExportPath -NoTypeInformation
Write-Host "Exported $($AgentInventory.Count) agents to $ExportPath" -ForegroundColor Green
```

---

## Registry Comparison Script

### Compare Discovered Agents with Registered Agents

```powershell
# Compare with registered agents (from SharePoint list export)
$RegisteredAgents = Import-Csv "C:\Governance\RegisteredAgents.csv"
$RegisteredIDs = $RegisteredAgents.AgentID

$UnregisteredAgents = $AgentInventory | Where-Object { $_.AgentID -notin $RegisteredIDs }

if ($UnregisteredAgents.Count -gt 0) {
    Write-Host "WARNING: Found $($UnregisteredAgents.Count) unregistered agents!" -ForegroundColor Red
    $UnregisteredAgents | Format-Table AgentName, Owner, Environment

    # Send alert email
    $EmailBody = "The following agents are not registered in the AI Agent Registry:`n`n"
    $EmailBody += ($UnregisteredAgents | ForEach-Object { "- $($_.AgentName) in $($_.Environment) (Owner: $($_.Owner))" }) -join "`n"

    # Requires Exchange Online connection
    # Send-MailMessage -To "ai-governance@contoso.com" -Subject "Unregistered Agents Detected" -Body $EmailBody
}
```

---

## Integrated Apps Discovery

### Get Integrated Apps from Microsoft Graph

```powershell
# Get Integrated Apps from M365 (Graph API)
Connect-MgGraph -Scopes "Application.Read.All"

$IntegratedApps = Get-MgServicePrincipal -Filter "tags/any(t:t eq 'WindowsAzureActiveDirectoryIntegratedApp')" -All
$IntegratedApps | Select-Object DisplayName, AppId, PublisherName, CreatedDateTime |
    Export-Csv "C:\Governance\IntegratedApps-$(Get-Date -Format 'yyyyMMdd').csv" -NoTypeInformation
```

---

## Registry Report Generation

### Generate HTML Report

```powershell
# Generate Registry Report
$ReportPath = "C:\Governance\AgentRegistryReport-$(Get-Date -Format 'yyyyMMdd').html"
$HTML = @"
<!DOCTYPE html>
<html>
<head>
    <title>Agent Registry Report - $(Get-Date -Format 'yyyy-MM-dd')</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #0078d4; color: white; }
        tr:nth-child(even) { background-color: #f2f2f2; }
        .warning { background-color: #fff3cd; }
        .error { background-color: #f8d7da; }
    </style>
</head>
<body>
    <h1>AI Agent Registry Report</h1>
    <p>Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm')</p>
    <h2>Summary</h2>
    <ul>
        <li>Total Agents Discovered: $($AgentInventory.Count)</li>
        <li>Registered Agents: $($RegisteredAgents.Count)</li>
        <li>Unregistered Agents: $($UnregisteredAgents.Count)</li>
    </ul>
</body>
</html>
"@
$HTML | Out-File $ReportPath
Write-Host "Report generated: $ReportPath" -ForegroundColor Green
```

---

## Complete Configuration Script

```powershell
<#
.SYNOPSIS
    Agent Registry Inventory and Compliance Check

.DESCRIPTION
    This script:
    1. Discovers all agents across Power Platform environments
    2. Compares with registered agents in SharePoint
    3. Identifies unregistered agents
    4. Generates compliance report

.PARAMETER ExportPath
    Path to export inventory CSV

.PARAMETER RegisteredAgentsPath
    Path to CSV of registered agents from SharePoint

.EXAMPLE
    .\Get-AgentInventory.ps1 -ExportPath "C:\Governance" -RegisteredAgentsPath "C:\Governance\RegisteredAgents.csv"

.NOTES
    Last Updated: January 2026
    Related Control: Control 1.2 - Agent Registry and Integrated Apps Management
#>

param(
    [Parameter(Mandatory=$false)]
    [string]$ExportPath = "C:\Governance",

    [Parameter(Mandatory=$false)]
    [string]$RegisteredAgentsPath = "C:\Governance\RegisteredAgents.csv"
)

# Connect to Power Platform
Add-PowerAppsAccount

Write-Host "=== Agent Registry Inventory ===" -ForegroundColor Cyan

# Step 1: Discover all agents
$AllEnvironments = Get-AdminPowerAppEnvironment
$AgentInventory = @()

foreach ($Env in $AllEnvironments) {
    Write-Host "  Scanning: $($Env.DisplayName)" -ForegroundColor Gray
    $Apps = Get-AdminPowerApp -EnvironmentName $Env.EnvironmentName

    foreach ($App in $Apps) {
        $AgentInventory += [PSCustomObject]@{
            AgentName = $App.DisplayName
            AgentID = $App.AppName
            Environment = $Env.DisplayName
            Owner = $App.Owner.displayName
            OwnerEmail = $App.Owner.email
            CreatedTime = $App.CreatedTime
            LastModifiedTime = $App.LastModifiedTime
        }
    }
}

Write-Host "  [DONE] Discovered $($AgentInventory.Count) agents" -ForegroundColor Green

# Step 2: Export inventory
$InventoryFile = Join-Path $ExportPath "AgentInventory-$(Get-Date -Format 'yyyyMMdd').csv"
$AgentInventory | Export-Csv -Path $InventoryFile -NoTypeInformation
Write-Host "  [DONE] Exported to $InventoryFile" -ForegroundColor Green

# Step 3: Compare with registered agents (if file exists)
if (Test-Path $RegisteredAgentsPath) {
    $RegisteredAgents = Import-Csv $RegisteredAgentsPath
    $RegisteredIDs = $RegisteredAgents.AgentID
    $UnregisteredAgents = $AgentInventory | Where-Object { $_.AgentID -notin $RegisteredIDs }

    if ($UnregisteredAgents.Count -gt 0) {
        Write-Host "`n  [WARN] Found $($UnregisteredAgents.Count) unregistered agents:" -ForegroundColor Yellow
        $UnregisteredAgents | Format-Table AgentName, Owner, Environment
    } else {
        Write-Host "  [PASS] All agents are registered" -ForegroundColor Green
    }
} else {
    Write-Host "  [INFO] No registered agents file found - skipping comparison" -ForegroundColor Gray
}

Write-Host "`nAgent Registry inventory complete!" -ForegroundColor Cyan
```

---

[Back to Control 1.2](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
