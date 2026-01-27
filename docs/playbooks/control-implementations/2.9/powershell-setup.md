# PowerShell Setup: Control 2.9 - Agent Performance Monitoring and Optimization

**Last Updated:** January 2026
**Modules Required:** Microsoft.PowerApps.Administration.PowerShell, MicrosoftPowerBIMgmt

## Prerequisites

```powershell
Install-Module -Name Microsoft.PowerApps.Administration.PowerShell -Force -Scope CurrentUser
Install-Module -Name MicrosoftPowerBIMgmt -Force -Scope CurrentUser
```

---

## Automated Scripts

### Export Agent Analytics Summary

```powershell
<#
.SYNOPSIS
    Exports agent usage and performance analytics summary

.EXAMPLE
    .\Export-AgentAnalytics.ps1
#>

Write-Host "=== Agent Analytics Export ===" -ForegroundColor Cyan

# Connect to Power Platform (interactive authentication)
Add-PowerAppsAccount

# For automated/unattended scenarios, use service principal authentication:
# $appId = "<Application-Client-ID>"
# $secret = "<Client-Secret>"
# $tenantId = "<Tenant-ID>"
# Add-PowerAppsAccount -ApplicationId $appId -ClientSecret $secret -TenantID $tenantId

# Get all environments
$environments = Get-AdminPowerAppEnvironment

$analytics = @()

foreach ($env in $environments) {
    Write-Host "Processing: $($env.DisplayName)" -ForegroundColor Yellow

    # Get Copilot Studio agents (bots)
    $agents = Get-AdminPowerAppCopilot -EnvironmentName $env.EnvironmentName -ErrorAction SilentlyContinue

    foreach ($agent in $agents) {
        $analytics += [PSCustomObject]@{
            Environment = $env.DisplayName
            AgentName = $agent.DisplayName
            AgentId = $agent.Name
            CreatedTime = $agent.CreatedTime
            LastModifiedTime = $agent.LastModifiedTime
            Status = $agent.Properties.status
        }
    }
}

$analytics | Export-Csv -Path ".\AgentAnalytics_$(Get-Date -Format 'yyyyMMdd').csv" -NoTypeInformation
Write-Host "`nExported $($analytics.Count) agents to AgentAnalytics_$(Get-Date -Format 'yyyyMMdd').csv" -ForegroundColor Green
```

### Check Agent Error Rates

```powershell
<#
.SYNOPSIS
    Checks agent error rates against defined thresholds

.EXAMPLE
    .\Test-AgentErrorRates.ps1 -Tier 2
#>

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("1", "2", "3")]
    [string]$Tier = "2"
)

Write-Host "=== Agent Error Rate Check (Tier $Tier) ===" -ForegroundColor Cyan

# Define thresholds by tier
$thresholds = @{
    "1" = 5.0   # 5%
    "2" = 2.0   # 2%
    "3" = 1.0   # 1%
}

$threshold = $thresholds[$Tier]
Write-Host "Error rate threshold: $threshold%" -ForegroundColor Yellow

# Note: Actual error rate data would come from Copilot Studio analytics API
# This is a template for integration with your analytics data source

Write-Host "`n[INFO] Connect to your analytics data source (Azure Data Lake, Power BI, etc.)" -ForegroundColor Yellow
Write-Host "[INFO] Query agent error rates and compare against threshold" -ForegroundColor Yellow

# Example output format
$sampleResults = @(
    @{Agent="CustomerService-Bot"; ErrorRate=0.8; Status="PASS"},
    @{Agent="HR-Assistant"; ErrorRate=1.5; Status="PASS"},
    @{Agent="Finance-Helper"; ErrorRate=2.5; Status="FAIL"}
)

foreach ($result in $sampleResults) {
    if ($result.ErrorRate -le $threshold) {
        Write-Host "[PASS] $($result.Agent): $($result.ErrorRate)% error rate" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] $($result.Agent): $($result.ErrorRate)% error rate (exceeds $threshold%)" -ForegroundColor Red
    }
}
```

### Create Performance Report

```powershell
<#
.SYNOPSIS
    Generates a performance report for agent governance review

.EXAMPLE
    .\New-PerformanceReport.ps1 -OutputPath ".\report.html"
#>

param(
    [string]$OutputPath = ".\AgentPerformanceReport_$(Get-Date -Format 'yyyyMMdd').html"
)

Write-Host "=== Generate Agent Performance Report ===" -ForegroundColor Cyan

$html = @"
<!DOCTYPE html>
<html>
<head>
    <title>Agent Performance Report - $(Get-Date -Format 'yyyy-MM-dd')</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #0078d4; }
        table { border-collapse: collapse; width: 100%; margin: 20px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #0078d4; color: white; }
        .pass { color: green; }
        .fail { color: red; }
        .kpi-card { display: inline-block; padding: 20px; margin: 10px; border: 1px solid #ddd; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>Agent Performance Report</h1>
    <p>Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm')</p>

    <h2>KPI Summary</h2>
    <div class="kpi-card">
        <h3>Total Agents</h3>
        <p style="font-size: 24px;">--</p>
    </div>
    <div class="kpi-card">
        <h3>Avg Error Rate</h3>
        <p style="font-size: 24px;">--</p>
    </div>
    <div class="kpi-card">
        <h3>Avg Response Time</h3>
        <p style="font-size: 24px;">--</p>
    </div>

    <h2>Agent Details</h2>
    <table>
        <tr>
            <th>Agent Name</th>
            <th>Environment</th>
            <th>Tier</th>
            <th>Error Rate</th>
            <th>Avg Response Time</th>
            <th>Status</th>
        </tr>
        <tr>
            <td colspan="6">[Connect to analytics data source to populate]</td>
        </tr>
    </table>

    <h2>Recommendations</h2>
    <ul>
        <li>Review agents exceeding error rate thresholds</li>
        <li>Investigate response time outliers</li>
        <li>Schedule optimization for underperforming agents</li>
    </ul>
</body>
</html>
"@

$html | Out-File -FilePath $OutputPath -Encoding utf8
Write-Host "Report generated: $OutputPath" -ForegroundColor Green
```

---

## Validation Script

```powershell
<#
.SYNOPSIS
    Validates Control 2.9 - Agent Performance Monitoring and Optimization

.EXAMPLE
    .\Validate-Control-2.9.ps1
#>

Write-Host "=== Control 2.9 Validation ===" -ForegroundColor Cyan

# Check 1: Copilot Studio analytics
Write-Host "`n[Check 1] Copilot Studio Analytics" -ForegroundColor Cyan
Write-Host "[INFO] Verify analytics enabled in Power Platform Admin Center > Analytics > Copilot Studio" -ForegroundColor Yellow

# Check 2: Data export configured
Write-Host "`n[Check 2] Data Export" -ForegroundColor Cyan
Write-Host "[INFO] Verify data export to Azure Data Lake is active" -ForegroundColor Yellow

# Check 3: Power BI dashboard
Write-Host "`n[Check 3] Performance Dashboard" -ForegroundColor Cyan
try {
    Connect-PowerBIServiceAccount
    $workspace = Get-PowerBIWorkspace -Name "Agent-Performance-Analytics" -ErrorAction SilentlyContinue
    if ($workspace) {
        Write-Host "[PASS] Agent-Performance-Analytics workspace exists" -ForegroundColor Green
        $reports = Get-PowerBIReport -WorkspaceId $workspace.Id
        Write-Host "  Reports: $($reports.Count)" -ForegroundColor Green
    } else {
        Write-Host "[WARN] Agent-Performance-Analytics workspace not found" -ForegroundColor Yellow
    }
    Disconnect-PowerBIServiceAccount
} catch {
    Write-Host "[INFO] Cannot connect to Power BI - verify manually" -ForegroundColor Yellow
}

# Check 4: Alerting configured
Write-Host "`n[Check 4] Performance Alerts" -ForegroundColor Cyan
Write-Host "[INFO] Verify Power Automate flows for threshold alerting" -ForegroundColor Yellow

# Check 5: Review cadence
Write-Host "`n[Check 5] Review Cadence" -ForegroundColor Cyan
Write-Host "[INFO] Verify review meetings are scheduled:" -ForegroundColor Yellow
Write-Host "  - Weekly operational review" -ForegroundColor Yellow
Write-Host "  - Monthly business review" -ForegroundColor Yellow
Write-Host "  - Quarterly executive review" -ForegroundColor Yellow

Write-Host "`n=== Validation Complete ===" -ForegroundColor Cyan
```

---

[Back to Control 2.9](../../../controls/pillar-2-management/2.9-agent-performance-monitoring-and-optimization.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
