# PowerShell Setup: Control 3.2 - Usage Analytics and Activity Monitoring

**Last Updated:** January 2026
**Modules Required:** Microsoft.PowerApps.Administration.PowerShell, ExchangeOnlineManagement

## Prerequisites

```powershell
# Install Power Platform Admin modules
Install-Module -Name Microsoft.PowerApps.Administration.PowerShell -Scope CurrentUser -Force
Install-Module -Name ExchangeOnlineManagement -Scope CurrentUser -Force

# Connect to Power Platform
Add-PowerAppsAccount

# Connect to Exchange Online (for audit logs)
Connect-ExchangeOnline
```

---

## Configuration Scripts

### Get Usage Metrics from PPAC

```powershell
# Get all environments with usage data
$environments = Get-AdminPowerAppEnvironment

# Retrieve usage metrics for each environment
foreach ($env in $environments) {
    Write-Host "Environment: $($env.DisplayName)" -ForegroundColor Cyan

    # Get environment-level analytics
    $analytics = Get-AdminPowerAppEnvironmentAnalytics -EnvironmentName $env.EnvironmentName -ErrorAction SilentlyContinue

    if ($analytics) {
        Write-Host "  Active Users: $($analytics.ActiveUsers)"
        Write-Host "  Total Sessions: $($analytics.TotalSessions)"
        Write-Host "  Last Updated: $($analytics.LastUpdated)"
    } else {
        Write-Host "  Analytics not available for this environment" -ForegroundColor Yellow
    }
}
```

### Export Copilot Studio Analytics

```powershell
# Get Copilot Studio agent analytics
function Export-CopilotStudioAnalytics {
    param(
        [string]$EnvironmentId,
        [string]$OutputPath = ".\CopilotAnalytics",
        [int]$DaysBack = 30
    )

    # Create output directory
    if (-not (Test-Path $OutputPath)) {
        New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null
    }

    # Calculate date range
    $endDate = Get-Date
    $startDate = $endDate.AddDays(-$DaysBack)

    Write-Host "Exporting analytics for environment: $EnvironmentId" -ForegroundColor Cyan
    Write-Host "Date range: $startDate to $endDate"

    # Get agent list
    $agents = Get-AdminPowerApp -EnvironmentName $EnvironmentId -ErrorAction SilentlyContinue

    $analyticsData = @()

    foreach ($agent in $agents) {
        $agentMetrics = @{
            AgentId = $agent.AppName
            AgentName = $agent.DisplayName
            Environment = $EnvironmentId
            Owner = $agent.Owner.displayName
            CreatedTime = $agent.CreatedTime
            LastModifiedTime = $agent.LastModifiedTime
            ExportDate = Get-Date
        }
        $analyticsData += [PSCustomObject]$agentMetrics
    }

    # Export to CSV
    $fileName = "CopilotAnalytics_$(Get-Date -Format 'yyyyMMdd_HHmmss').csv"
    $analyticsData | Export-Csv -Path (Join-Path $OutputPath $fileName) -NoTypeInformation

    Write-Host "Analytics exported to: $OutputPath\$fileName" -ForegroundColor Green
    Write-Host "Total agents: $($analyticsData.Count)"
    return $analyticsData
}

# Usage
# Export-CopilotStudioAnalytics -EnvironmentId "env-id-here" -DaysBack 30
```

### Query Audit Logs for Agent Activity

```powershell
# Query unified audit log for Copilot Studio activities
function Get-AgentAuditLogs {
    param(
        [string]$AgentName = "*",
        [int]$DaysBack = 7,
        [string]$OutputPath = ".\AuditLogs"
    )

    Write-Host "Querying audit logs for agent activity..." -ForegroundColor Cyan

    $endDate = Get-Date
    $startDate = $endDate.AddDays(-$DaysBack)

    # Search for Copilot Studio activities
    $auditLogs = Search-UnifiedAuditLog `
        -StartDate $startDate `
        -EndDate $endDate `
        -RecordType PowerApps `
        -ResultSize 5000

    Write-Host "Found $($auditLogs.Count) audit log entries" -ForegroundColor Cyan

    # Parse and filter results
    $parsedLogs = $auditLogs | ForEach-Object {
        $auditData = $_.AuditData | ConvertFrom-Json
        [PSCustomObject]@{
            Timestamp = $_.CreationDate
            User = $_.UserIds
            Operation = $_.Operations
            ItemName = $auditData.ItemName
            ItemType = $auditData.ItemType
            EnvironmentName = $auditData.EnvironmentName
            ResultStatus = $auditData.ResultStatus
        }
    }

    # Filter by agent name if specified
    if ($AgentName -ne "*") {
        $parsedLogs = $parsedLogs | Where-Object { $_.ItemName -like "*$AgentName*" }
    }

    # Export results
    if (-not (Test-Path $OutputPath)) {
        New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null
    }

    $fileName = "AgentAuditLogs_$(Get-Date -Format 'yyyyMMdd_HHmmss').csv"
    $parsedLogs | Export-Csv -Path (Join-Path $OutputPath $fileName) -NoTypeInformation

    Write-Host "Audit logs exported to: $OutputPath\$fileName" -ForegroundColor Green
    return $parsedLogs
}

# Usage
# Get-AgentAuditLogs -AgentName "CustomerService" -DaysBack 30
```

### Generate FSI Usage Report

```powershell
# Generate comprehensive usage report for FSI governance
function New-FSIUsageReport {
    param(
        [string]$ReportPath = ".\Reports",
        [string]$ReportName = "FSI_Agent_Usage_Report",
        [int]$DaysBack = 30
    )

    Write-Host "Generating FSI Usage Report..." -ForegroundColor Cyan

    # Create report directory
    if (-not (Test-Path $ReportPath)) {
        New-Item -ItemType Directory -Path $ReportPath -Force | Out-Null
    }

    # Get all managed environments
    $environments = Get-AdminPowerAppEnvironment

    $reportData = @()

    foreach ($env in $environments) {
        Write-Host "  Processing: $($env.DisplayName)" -ForegroundColor Yellow

        # Get apps in environment
        $apps = Get-AdminPowerApp -EnvironmentName $env.EnvironmentName -ErrorAction SilentlyContinue

        foreach ($app in $apps) {
            $reportData += [PSCustomObject]@{
                EnvironmentName = $env.DisplayName
                EnvironmentType = $env.EnvironmentType
                IsManaged = $env.Properties.isManaged
                AppName = $app.DisplayName
                Owner = $app.Owner.displayName
                OwnerEmail = $app.Owner.email
                CreatedTime = $app.CreatedTime
                LastModifiedTime = $app.LastModifiedTime
                ReportDate = Get-Date
            }
        }
    }

    # Export report
    $timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
    $csvPath = Join-Path $ReportPath "${ReportName}_${timestamp}.csv"
    $reportData | Export-Csv -Path $csvPath -NoTypeInformation

    # Generate summary
    $summary = @{
        TotalEnvironments = ($environments).Count
        ManagedEnvironments = ($environments | Where-Object { $_.Properties.isManaged -eq $true }).Count
        TotalApps = ($reportData).Count
        ReportDate = Get-Date
    }

    Write-Host "`n=== Report Summary ===" -ForegroundColor Cyan
    Write-Host "Total Environments: $($summary.TotalEnvironments)"
    Write-Host "Managed Environments: $($summary.ManagedEnvironments)"
    Write-Host "Total Apps: $($summary.TotalApps)"
    Write-Host "Report exported to: $csvPath" -ForegroundColor Green

    return $reportData
}

# Usage
# New-FSIUsageReport -DaysBack 30
```

---

## Validation Script

```powershell
# Validation: Check monitoring configuration
Write-Host "`n=== Control 3.2 Validation ===" -ForegroundColor Cyan

# Check 1: Verify environment access
$environments = Get-AdminPowerAppEnvironment
if ($environments.Count -gt 0) {
    Write-Host "[PASS] Environment access verified: $($environments.Count) environments" -ForegroundColor Green
} else {
    Write-Host "[FAIL] Cannot access environments" -ForegroundColor Red
}

# Check 2: Verify managed environments exist
$managedEnvs = $environments | Where-Object { $_.Properties.isManaged -eq $true }
if ($managedEnvs.Count -gt 0) {
    Write-Host "[PASS] Managed environments found: $($managedEnvs.Count)" -ForegroundColor Green
} else {
    Write-Host "[WARN] No managed environments - usage insights unavailable" -ForegroundColor Yellow
}

# Check 3: Verify audit log access
try {
    $testAudit = Search-UnifiedAuditLog -StartDate (Get-Date).AddDays(-1) -EndDate (Get-Date) -ResultSize 1
    Write-Host "[PASS] Audit log access verified" -ForegroundColor Green
} catch {
    Write-Host "[FAIL] Cannot access audit logs: $($_.Exception.Message)" -ForegroundColor Red
}

# Check 4: Verify app visibility
$allApps = Get-AdminPowerApp
if ($allApps -ne $null) {
    Write-Host "[PASS] App visibility verified: $($allApps.Count) apps" -ForegroundColor Green
} else {
    Write-Host "[WARN] No apps found or access issue" -ForegroundColor Yellow
}

Write-Host "`n=== Validation Complete ===" -ForegroundColor Cyan
```

---

## Complete Configuration Script

```powershell
<#
.SYNOPSIS
    Configures Control 3.2 - Usage Analytics and Activity Monitoring

.DESCRIPTION
    This script validates and exports usage analytics by:
    1. Checking environment access and managed status
    2. Exporting app inventory with usage data
    3. Querying audit logs for activity monitoring
    4. Generating comprehensive FSI usage report

.PARAMETER ExportPath
    The directory path for analytics exports

.PARAMETER DaysBack
    Number of days of history to include

.EXAMPLE
    .\Export-UsageAnalytics.ps1 -ExportPath "C:\Governance\Analytics" -DaysBack 30

.NOTES
    Last Updated: January 2026
    Related Control: Control 3.2 - Usage Analytics and Activity Monitoring
#>

param(
    [Parameter(Mandatory=$false)]
    [string]$ExportPath = "C:\Governance\UsageAnalytics",

    [Parameter(Mandatory=$false)]
    [int]$DaysBack = 30
)

# Connect to Power Platform
Add-PowerAppsAccount

Write-Host "Executing Control 3.2 Usage Analytics Export" -ForegroundColor Cyan

# Create export directory
if (-not (Test-Path $ExportPath)) {
    New-Item -ItemType Directory -Path $ExportPath -Force | Out-Null
}

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

# Step 1: Get environment summary
Write-Host "`n[Step 1] Collecting environment data..." -ForegroundColor Yellow
$environments = Get-AdminPowerAppEnvironment

$envSummary = $environments | Select-Object DisplayName, EnvironmentType,
    @{N='IsManaged';E={$_.Properties.isManaged}},
    Location, CreatedTime

$envSummary | Export-Csv -Path "$ExportPath\Environments_$timestamp.csv" -NoTypeInformation
Write-Host "  Environments exported: $($environments.Count)"

# Step 2: Get app inventory
Write-Host "`n[Step 2] Collecting app inventory..." -ForegroundColor Yellow
$allApps = Get-AdminPowerApp

$appInventory = $allApps | Select-Object DisplayName, EnvironmentName,
    @{N='Owner';E={$_.Owner.displayName}},
    @{N='OwnerEmail';E={$_.Owner.email}},
    CreatedTime, LastModifiedTime

$appInventory | Export-Csv -Path "$ExportPath\AppInventory_$timestamp.csv" -NoTypeInformation
Write-Host "  Apps exported: $($allApps.Count)"

# Step 3: Summary report
Write-Host "`n[Step 3] Generating summary report..." -ForegroundColor Yellow

$summary = [PSCustomObject]@{
    ReportDate = Get-Date
    DaysBack = $DaysBack
    TotalEnvironments = $environments.Count
    ManagedEnvironments = ($environments | Where-Object { $_.Properties.isManaged -eq $true }).Count
    TotalApps = $allApps.Count
    ExportPath = $ExportPath
}

$summary | ConvertTo-Json | Out-File "$ExportPath\Summary_$timestamp.json"

Write-Host "`n=== Export Complete ===" -ForegroundColor Cyan
Write-Host "Files saved to: $ExportPath" -ForegroundColor Green
$summary
```

---

[Back to Control 3.2](../../../controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
