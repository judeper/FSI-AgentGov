# PowerShell Setup: Control 3.1 - Agent Inventory and Metadata Management

**Last Updated:** January 2026
**Modules Required:** Microsoft.PowerApps.Administration.PowerShell

## Prerequisites

```powershell
# Install Power Platform Admin modules
Install-Module -Name Microsoft.PowerApps.Administration.PowerShell -Scope CurrentUser -Force
Install-Module -Name Microsoft.PowerApps.PowerShell -Scope CurrentUser -Force

# Connect to Power Platform
Add-PowerAppsAccount
```

---

## Configuration Scripts

### Get All Environments

```powershell
# List all environments with details
$environments = Get-AdminPowerAppEnvironment
$environments | Select-Object DisplayName, EnvironmentName, EnvironmentType, CreatedTime, SecurityGroupId |
    Format-Table -AutoSize

# Export environment list to CSV
$environments | Export-Csv -Path "C:\Governance\Environments_$(Get-Date -Format 'yyyyMMdd').csv" -NoTypeInformation
```

### Get Apps and Flows Across Environments

```powershell
# Get all Power Apps across all environments
$allApps = Get-AdminPowerApp
Write-Host "Total Power Apps found: $($allApps.Count)" -ForegroundColor Cyan

$allApps | Select-Object DisplayName, EnvironmentName, Owner, CreatedTime, LastModifiedTime |
    Format-Table -AutoSize

# Get all Power Automate flows across all environments
$allFlows = Get-AdminFlow
Write-Host "Total Power Automate flows found: $($allFlows.Count)" -ForegroundColor Cyan

$allFlows | Select-Object DisplayName, EnvironmentName, Enabled, CreatedTime, LastModifiedTime |
    Format-Table -AutoSize
```

### Export Comprehensive Agent Inventory

```powershell
# Comprehensive Agent Inventory Export Script
# Run this script weekly for compliance documentation

$reportDate = Get-Date -Format "yyyyMMdd_HHmmss"
$exportPath = "C:\Governance\AgentInventory"

# Create export directory if not exists
if (-not (Test-Path $exportPath)) {
    New-Item -ItemType Directory -Path $exportPath -Force
}

# Get all environments
$environments = Get-AdminPowerAppEnvironment

# Initialize inventory collection
$inventoryReport = @()

foreach ($env in $environments) {
    Write-Host "Processing environment: $($env.DisplayName)" -ForegroundColor Yellow

    # Get apps in this environment
    $apps = Get-AdminPowerApp -EnvironmentName $env.EnvironmentName -ErrorAction SilentlyContinue

    foreach ($app in $apps) {
        $inventoryReport += [PSCustomObject]@{
            ItemName = $app.DisplayName
            ItemType = "PowerApp"
            Owner = $app.Owner.displayName
            OwnerEmail = $app.Owner.email
            EnvironmentName = $env.DisplayName
            EnvironmentType = $env.EnvironmentType
            CreatedDate = $app.CreatedTime
            ModifiedDate = $app.LastModifiedTime
            AppType = $app.AppType
            InventoryDate = Get-Date
        }
    }

    # Get flows in this environment
    $flows = Get-AdminFlow -EnvironmentName $env.EnvironmentName -ErrorAction SilentlyContinue

    foreach ($flow in $flows) {
        $inventoryReport += [PSCustomObject]@{
            ItemName = $flow.DisplayName
            ItemType = "Flow"
            Owner = $flow.Owner.displayName
            OwnerEmail = $flow.Owner.email
            EnvironmentName = $env.DisplayName
            EnvironmentType = $env.EnvironmentType
            CreatedDate = $flow.CreatedTime
            ModifiedDate = $flow.LastModifiedTime
            AppType = "N/A"
            InventoryDate = Get-Date
        }
    }
}

# Export inventory to CSV
$inventoryReport | Export-Csv -Path "$exportPath\AgentInventory_$reportDate.csv" -NoTypeInformation
Write-Host "Inventory exported to: $exportPath\AgentInventory_$reportDate.csv" -ForegroundColor Green
Write-Host "Total items inventoried: $($inventoryReport.Count)" -ForegroundColor Cyan

# Evidence integrity: compute and record a SHA-256 hash for the export
$exportFile = "$exportPath\AgentInventory_$reportDate.csv"
$hash = (Get-FileHash -Path $exportFile -Algorithm SHA256).Hash
"$reportDate,AgentInventory,$exportFile,SHA256,$hash" | Out-File -FilePath "$exportPath\AgentInventory_Hashes.csv" -Append -Encoding utf8
Write-Host "Export SHA-256: $hash" -ForegroundColor Cyan
```

### Identify Orphaned Agents

```powershell
# Identify Orphaned Agents Script
# Finds agents with missing or invalid owners

$orphanedAgents = @()

# Get all apps
$allApps = Get-AdminPowerApp

foreach ($app in $allApps) {
    # Check if owner email is empty or contains system account indicators
    if ([string]::IsNullOrEmpty($app.Owner.email) -or
        $app.Owner.email -like "*system*" -or
        $app.Owner.email -like "*deleted*") {

        $orphanedAgents += [PSCustomObject]@{
            ItemName = $app.DisplayName
            ItemType = "PowerApp"
            OwnerInfo = $app.Owner.displayName
            EnvironmentName = $app.EnvironmentName
            CreatedDate = $app.CreatedTime
            LastModified = $app.LastModifiedTime
            Status = "Orphaned - No Valid Owner"
        }
    }
}

# Display orphaned agents
if ($orphanedAgents.Count -gt 0) {
    Write-Host "Found $($orphanedAgents.Count) orphaned agents requiring remediation:" -ForegroundColor Red
    $orphanedAgents | Format-Table -AutoSize

    # Export for remediation
    $orphanedAgents | Export-Csv -Path "C:\Governance\OrphanedAgents_$(Get-Date -Format 'yyyyMMdd').csv" -NoTypeInformation
} else {
    Write-Host "No orphaned agents found." -ForegroundColor Green
}
```

### Create Inventory Summary Report

```powershell
# Generate Inventory Summary Report
# Provides executive-level summary for governance committee

$environments = Get-AdminPowerAppEnvironment
$summaryReport = @()

foreach ($env in $environments) {
    $apps = Get-AdminPowerApp -EnvironmentName $env.EnvironmentName -ErrorAction SilentlyContinue
    $flows = Get-AdminFlow -EnvironmentName $env.EnvironmentName -ErrorAction SilentlyContinue

    $summaryReport += [PSCustomObject]@{
        EnvironmentName = $env.DisplayName
        EnvironmentType = $env.EnvironmentType
        TotalApps = $apps.Count
        TotalFlows = $flows.Count
        TotalItems = $apps.Count + $flows.Count
        Region = $env.Location
        SecurityGroupEnabled = if ($env.SecurityGroupId) { "Yes" } else { "No" }
        ReportDate = Get-Date
    }
}

# Display summary
Write-Host "`n=== AGENT INVENTORY SUMMARY REPORT ===" -ForegroundColor Cyan
$summaryReport | Format-Table -AutoSize

# Total counts
$totalApps = ($summaryReport | Measure-Object -Property TotalApps -Sum).Sum
$totalFlows = ($summaryReport | Measure-Object -Property TotalFlows -Sum).Sum

Write-Host "`nTotal Apps Across All Environments: $totalApps" -ForegroundColor Green
Write-Host "Total Flows Across All Environments: $totalFlows" -ForegroundColor Green
Write-Host "Total Environments: $($environments.Count)" -ForegroundColor Green

# Export summary
$summaryReport | Export-Csv -Path "C:\Governance\InventorySummary_$(Get-Date -Format 'yyyyMMdd').csv" -NoTypeInformation
```

---

## Validation Script

```powershell
# Validation: Check inventory access and export capability
Write-Host "`n=== Control 3.1 Validation ===" -ForegroundColor Cyan

# Check 1: Can access environments
$environments = Get-AdminPowerAppEnvironment
if ($environments.Count -gt 0) {
    Write-Host "[PASS] Can access environments: $($environments.Count) found" -ForegroundColor Green
} else {
    Write-Host "[FAIL] No environments accessible - check permissions" -ForegroundColor Red
}

# Check 2: Can retrieve apps
$allApps = Get-AdminPowerApp
if ($allApps -ne $null) {
    Write-Host "[PASS] Can retrieve Power Apps: $($allApps.Count) found" -ForegroundColor Green
} else {
    Write-Host "[WARN] No Power Apps found or access issue" -ForegroundColor Yellow
}

# Check 3: Can retrieve flows
$allFlows = Get-AdminFlow
if ($allFlows -ne $null) {
    Write-Host "[PASS] Can retrieve Power Automate flows: $($allFlows.Count) found" -ForegroundColor Green
} else {
    Write-Host "[WARN] No flows found or access issue" -ForegroundColor Yellow
}

# Check 4: Verify export location exists
$exportPath = "C:\Governance\AgentInventory"
if (Test-Path $exportPath) {
    Write-Host "[PASS] Export directory exists: $exportPath" -ForegroundColor Green
} else {
    Write-Host "[WARN] Export directory does not exist - will be created on first export" -ForegroundColor Yellow
}
```

---

## Complete Configuration Script

```powershell
<#
.SYNOPSIS
    Configures Control 3.1 - Agent Inventory and Metadata Management

.DESCRIPTION
    This script performs comprehensive agent inventory by:
    1. Enumerating all environments
    2. Collecting all apps and flows
    3. Identifying orphaned agents
    4. Exporting to CSV with SHA-256 hash
    5. Generating summary report

.PARAMETER ExportPath
    The directory path for inventory exports

.EXAMPLE
    .\Export-AgentInventory.ps1 -ExportPath "C:\Governance\AgentInventory"

.NOTES
    Last Updated: January 2026
    Related Control: Control 3.1 - Agent Inventory and Metadata Management
#>

param(
    [Parameter(Mandatory=$false)]
    [string]$ExportPath = "C:\Governance\AgentInventory"
)

# Connect to Power Platform
Add-PowerAppsAccount

Write-Host "Executing Control 3.1 Agent Inventory Export" -ForegroundColor Cyan

# Create export directory
if (-not (Test-Path $ExportPath)) {
    New-Item -ItemType Directory -Path $ExportPath -Force | Out-Null
}

$reportDate = Get-Date -Format "yyyyMMdd_HHmmss"
$environments = Get-AdminPowerAppEnvironment
$inventoryReport = @()
$orphanedAgents = @()

foreach ($env in $environments) {
    Write-Host "  Processing: $($env.DisplayName)" -ForegroundColor Yellow

    $apps = Get-AdminPowerApp -EnvironmentName $env.EnvironmentName -ErrorAction SilentlyContinue

    foreach ($app in $apps) {
        $isOrphaned = [string]::IsNullOrEmpty($app.Owner.email) -or
                      $app.Owner.email -like "*system*" -or
                      $app.Owner.email -like "*deleted*"

        $record = [PSCustomObject]@{
            ItemName = $app.DisplayName
            ItemType = "PowerApp"
            Owner = $app.Owner.displayName
            OwnerEmail = $app.Owner.email
            EnvironmentName = $env.DisplayName
            EnvironmentType = $env.EnvironmentType
            CreatedDate = $app.CreatedTime
            ModifiedDate = $app.LastModifiedTime
            IsOrphaned = $isOrphaned
            InventoryDate = Get-Date
        }

        $inventoryReport += $record
        if ($isOrphaned) { $orphanedAgents += $record }
    }
}

# Export full inventory
$fullExport = "$ExportPath\AgentInventory_$reportDate.csv"
$inventoryReport | Export-Csv -Path $fullExport -NoTypeInformation
$hash = (Get-FileHash -Path $fullExport -Algorithm SHA256).Hash
"$reportDate,AgentInventory,$fullExport,SHA256,$hash" | Out-File -FilePath "$ExportPath\Hashes.csv" -Append

# Export orphaned agents
if ($orphanedAgents.Count -gt 0) {
    $orphanedAgents | Export-Csv -Path "$ExportPath\OrphanedAgents_$reportDate.csv" -NoTypeInformation
    Write-Host "  [ALERT] $($orphanedAgents.Count) orphaned agents found" -ForegroundColor Red
}

Write-Host "`nInventory complete!" -ForegroundColor Cyan
Write-Host "  Total items: $($inventoryReport.Count)" -ForegroundColor Green
Write-Host "  Export file: $fullExport" -ForegroundColor Green
Write-Host "  SHA-256: $hash" -ForegroundColor Green
```

---

[Back to Control 3.1](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
