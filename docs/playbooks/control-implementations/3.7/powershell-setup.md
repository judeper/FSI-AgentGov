# Control 3.7: PPAC Security Posture Assessment - PowerShell Setup

> This playbook provides PowerShell automation scripts for [Control 3.7](../../../controls/pillar-3-reporting/3.7-ppac-security-posture-assessment.md).

---

## Prerequisites

```powershell
# Install required modules
Install-Module -Name Microsoft.PowerApps.Administration.PowerShell -Force -AllowClobber
Install-Module -Name Microsoft.Graph -Force -AllowClobber

# Connect to services
Add-PowerAppsAccount
Connect-MgGraph -Scopes "SecurityEvents.Read.All", "Policy.Read.All"
```

---

## Get Environment Security Configuration

```powershell
function Get-EnvironmentSecurityPosture {
    param(
        [string]$EnvironmentName = ""
    )

    Write-Host "Analyzing environment security posture..." -ForegroundColor Cyan

    $environments = if ($EnvironmentName) {
        Get-AdminPowerAppEnvironment -EnvironmentName $EnvironmentName
    } else {
        Get-AdminPowerAppEnvironment
    }

    $posture = @()

    foreach ($env in $environments) {
        $envDetails = Get-AdminPowerAppEnvironment -EnvironmentName $env.EnvironmentName

        $assessment = [PSCustomObject]@{
            Name = $env.DisplayName
            Type = $env.EnvironmentType
            IsManaged = $envDetails.Internal.properties.governanceConfiguration.enableManagedEnvironment -eq $true
            HasDLP = $null -ne (Get-DlpPolicy -EnvironmentName $env.EnvironmentName -ErrorAction SilentlyContinue)
            SecurityGroupRequired = $envDetails.Internal.properties.linkedEnvironmentMetadata.securityGroupId -ne $null
            Created = $env.CreatedTime
        }

        # Calculate score
        $score = 0
        if ($assessment.IsManaged) { $score += 40 }
        if ($assessment.HasDLP) { $score += 35 }
        if ($assessment.SecurityGroupRequired) { $score += 25 }

        $assessment | Add-Member -NotePropertyName "SecurityScore" -NotePropertyValue $score

        $posture += $assessment
    }

    Write-Host "Posture assessment complete for $($posture.Count) environments" -ForegroundColor Green

    return $posture
}
```

---

## Check DLP Policy Coverage

```powershell
function Test-DlpPolicyCoverage {

    Write-Host "Checking DLP policy coverage..." -ForegroundColor Cyan

    $environments = Get-AdminPowerAppEnvironment
    $policies = Get-DlpPolicy

    $coverage = @()

    foreach ($env in $environments) {
        $applicablePolicies = $policies | Where-Object {
            $_.environments -contains $env.EnvironmentName -or
            $_.environments.Count -eq 0  # Tenant-wide
        }

        $coverage += [PSCustomObject]@{
            Environment = $env.DisplayName
            Type = $env.EnvironmentType
            PolicyCount = $applicablePolicies.Count
            PolicyNames = ($applicablePolicies | Select-Object -ExpandProperty DisplayName) -join ", "
            HasCoverage = $applicablePolicies.Count -gt 0
        }
    }

    $uncovered = $coverage | Where-Object { -not $_.HasCoverage }

    if ($uncovered.Count -gt 0) {
        Write-Host "UNCOVERED ENVIRONMENTS:" -ForegroundColor Red
        $uncovered | Format-Table Environment, Type
    } else {
        Write-Host "All environments have DLP coverage" -ForegroundColor Green
    }

    return $coverage
}
```

---

## Generate Security Posture Report

```powershell
function New-SecurityPostureReport {
    param(
        [string]$OutputPath = ".\SecurityPostureReport-$(Get-Date -Format 'yyyyMMdd').html"
    )

    Write-Host "Generating security posture report..." -ForegroundColor Cyan

    $posture = Get-EnvironmentSecurityPosture
    $dlpCoverage = Test-DlpPolicyCoverage

    $avgScore = ($posture | Measure-Object -Property SecurityScore -Average).Average
    $managedCount = ($posture | Where-Object { $_.IsManaged }).Count
    $dlpCoveredCount = ($dlpCoverage | Where-Object { $_.HasCoverage }).Count

    $html = @"
<!DOCTYPE html>
<html>
<head>
    <title>Power Platform Security Posture Report</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; margin: 40px; }
        h1 { color: #0078d4; }
        .metric { display: inline-block; padding: 20px; margin: 10px; background: #f0f0f0; border-radius: 8px; text-align: center; }
        .metric-value { font-size: 32px; font-weight: bold; color: #0078d4; }
        .good { color: #107c10; }
        .warning { color: #ff8c00; }
        .bad { color: #d13438; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th { background: #0078d4; color: white; padding: 12px; text-align: left; }
        td { border: 1px solid #ddd; padding: 10px; }
    </style>
</head>
<body>
    <h1>Power Platform Security Posture Report</h1>
    <p>Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm')</p>

    <div class="metric">
        <div class="metric-value $( if ($avgScore -ge 70) {'good'} elseif ($avgScore -ge 40) {'warning'} else {'bad'} )">$([math]::Round($avgScore))%</div>
        <div>Average Security Score</div>
    </div>
    <div class="metric">
        <div class="metric-value">$managedCount/$($posture.Count)</div>
        <div>Managed Environments</div>
    </div>
    <div class="metric">
        <div class="metric-value">$dlpCoveredCount/$($dlpCoverage.Count)</div>
        <div>DLP Covered</div>
    </div>

    <h2>Environment Security Scores</h2>
    <table>
        <tr><th>Environment</th><th>Type</th><th>Managed</th><th>DLP</th><th>Security Group</th><th>Score</th></tr>
        $($posture | ForEach-Object {
            "<tr>
                <td>$($_.Name)</td>
                <td>$($_.Type)</td>
                <td>$(if ($_.IsManaged) {'Yes'} else {'No'})</td>
                <td>$(if ($_.HasDLP) {'Yes'} else {'No'})</td>
                <td>$(if ($_.SecurityGroupRequired) {'Yes'} else {'No'})</td>
                <td class='$(if ($_.SecurityScore -ge 70) {'good'} elseif ($_.SecurityScore -ge 40) {'warning'} else {'bad'})'>$($_.SecurityScore)%</td>
            </tr>"
        })
    </table>

    <h2>Recommendations</h2>
    <ul>
        $(if ($managedCount -lt $posture.Count) { "<li><strong>High:</strong> Enable managed environments for remaining $(($posture.Count - $managedCount)) environments</li>" })
        $(if ($dlpCoveredCount -lt $dlpCoverage.Count) { "<li><strong>High:</strong> Apply DLP policies to $(($dlpCoverage.Count - $dlpCoveredCount)) uncovered environments</li>" })
        <li>Review and address recommendations in PPAC Security > Health</li>
    </ul>
</body>
</html>
"@

    $html | Out-File -FilePath $OutputPath -Encoding UTF8
    Write-Host "Report generated: $OutputPath" -ForegroundColor Green

    return $OutputPath
}
```

---

## Usage Examples

```powershell
# Get security posture for all environments
$posture = Get-EnvironmentSecurityPosture

# Check DLP coverage
Test-DlpPolicyCoverage

# Generate full report
New-SecurityPostureReport
```

---

## Complete Configuration Script

```powershell
<#
.SYNOPSIS
    Configures Control 3.7 - PPAC Security Posture Assessment

.DESCRIPTION
    This script performs security posture assessment:
    1. Analyzes environment security configuration
    2. Checks DLP policy coverage
    3. Generates security posture report

.PARAMETER OutputPath
    Path for the generated security posture report

.EXAMPLE
    .\Configure-Control-3.7.ps1 -OutputPath "C:\Reports"

.NOTES
    Last Updated: January 2026
    Related Control: Control 3.7 - PPAC Security Posture Assessment
#>

param(
    [Parameter(Mandatory=$false)]
    [string]$OutputPath = ".\SecurityPostureReport-$(Get-Date -Format 'yyyyMMdd').html"
)

try {
    # Connect to Power Platform
    Write-Host "Connecting to Power Platform..." -ForegroundColor Cyan
    Add-PowerAppsAccount

    Write-Host "Executing Control 3.7 Security Posture Assessment" -ForegroundColor Cyan

    # Get environment security posture
    Write-Host "`nAnalyzing environment security..." -ForegroundColor Yellow
    $posture = Get-EnvironmentSecurityPosture

    # Check DLP coverage
    Write-Host "Checking DLP policy coverage..." -ForegroundColor Yellow
    $dlpCoverage = Test-DlpPolicyCoverage

    # Calculate summary metrics
    $avgScore = ($posture | Measure-Object -Property SecurityScore -Average).Average
    $managedCount = ($posture | Where-Object { $_.IsManaged }).Count
    $dlpCoveredCount = ($dlpCoverage | Where-Object { $_.HasCoverage }).Count

    Write-Host "`nSecurity Posture Summary:" -ForegroundColor Cyan
    Write-Host "  Average Security Score: $([math]::Round($avgScore))%" -ForegroundColor $(if ($avgScore -ge 70) { "Green" } elseif ($avgScore -ge 40) { "Yellow" } else { "Red" })
    Write-Host "  Managed Environments: $managedCount / $($posture.Count)" -ForegroundColor Green
    Write-Host "  DLP Covered: $dlpCoveredCount / $($dlpCoverage.Count)" -ForegroundColor Green

    # Generate report
    Write-Host "`nGenerating security posture report..." -ForegroundColor Yellow
    New-SecurityPostureReport -OutputPath $OutputPath

    Write-Host "`n[PASS] Control 3.7 configuration completed successfully" -ForegroundColor Green
}
catch {
    Write-Host "[FAIL] Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "[INFO] Stack trace: $($_.ScriptStackTrace)" -ForegroundColor Yellow
    exit 1
}
```

---

## Next Steps

- [Portal Walkthrough](./portal-walkthrough.md) - Manual configuration
- [Verification & Testing](./verification-testing.md) - Test procedures
- [Troubleshooting](./troubleshooting.md) - Common issues

---

*Updated: January 2026 | Version: v1.2*
