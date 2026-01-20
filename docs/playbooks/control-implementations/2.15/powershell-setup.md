# PowerShell Setup: Control 2.15 - Environment Routing and Auto-Provisioning

**Last Updated:** January 2026
**Modules Required:** Microsoft.PowerApps.Administration.PowerShell

## Prerequisites

```powershell
# Install Power Platform admin module
Install-Module -Name Microsoft.PowerApps.Administration.PowerShell -Force -Scope CurrentUser

# Connect to Power Platform
Add-PowerAppsAccount
```

---

## Configuration Scripts

### List All Environment Groups

```powershell
# Note: Environment Groups management is primarily done through PPAC portal
# PowerShell can be used for environment inventory and validation

# List all environments with group information
$environments = Get-AdminPowerAppEnvironment

$envReport = $environments | ForEach-Object {
    [PSCustomObject]@{
        Name = $_.DisplayName
        EnvironmentId = $_.EnvironmentName
        Type = $_.EnvironmentType
        Region = $_.Location
        State = $_.States.Runtime
        IsManagedEnv = if ($_.Properties.protectionLevel -eq "Standard") { "No" } else { "Yes" }
    }
}

$envReport | Format-Table
```

### Validate Environment Routing Configuration

```powershell
<#
.SYNOPSIS
    Validates that environments are properly configured for routing

.DESCRIPTION
    Checks that target environments for routing are:
    - Managed Environments
    - In US region
    - In appropriate state

.EXAMPLE
    .\Validate-EnvironmentRouting.ps1
#>

# Connect to Power Platform
Add-PowerAppsAccount

Write-Host "=== Environment Routing Validation ===" -ForegroundColor Cyan

# Get all environments
$environments = Get-AdminPowerAppEnvironment

# Check each environment
$validationResults = $environments | ForEach-Object {
    $isManaged = $_.Properties.protectionLevel -ne "Standard"
    $isUSRegion = $_.Location -match "unitedstates|US"
    $isActive = $_.States.Runtime -eq "Enabled"

    [PSCustomObject]@{
        Name = $_.DisplayName
        Type = $_.EnvironmentType
        IsManaged = $isManaged
        IsUSRegion = $isUSRegion
        IsActive = $isActive
        RoutingReady = ($isManaged -and $isUSRegion -and $isActive)
    }
}

# Display results
Write-Host "`n=== Routing Readiness ===" -ForegroundColor Cyan
$validationResults | Format-Table Name, Type, IsManaged, IsUSRegion, IsActive, RoutingReady

# Summary
$readyCount = ($validationResults | Where-Object { $_.RoutingReady }).Count
$totalCount = $validationResults.Count

Write-Host "`nRouting Ready: $readyCount / $totalCount environments"

# Flag environments not ready
$notReady = $validationResults | Where-Object { -not $_.RoutingReady }
if ($notReady) {
    Write-Host "`n=== Environments NOT Ready for Routing ===" -ForegroundColor Yellow
    $notReady | Format-Table Name, Type, IsManaged, IsUSRegion, IsActive
}
```

### Export Environment Group Configuration

```powershell
<#
.SYNOPSIS
    Exports environment configuration for documentation

.DESCRIPTION
    Creates a JSON export of all environments for routing documentation

.EXAMPLE
    .\Export-EnvironmentConfig.ps1
#>

# Connect to Power Platform
Add-PowerAppsAccount

# Get all environments
$environments = Get-AdminPowerAppEnvironment

# Build configuration export
$config = @{
    ExportDate = Get-Date -Format "yyyy-MM-dd HH:mm"
    TotalEnvironments = $environments.Count
    Environments = @()
}

foreach ($env in $environments) {
    $envConfig = @{
        Name = $env.DisplayName
        EnvironmentId = $env.EnvironmentName
        Type = $env.EnvironmentType
        Region = $env.Location
        State = $env.States.Runtime
        IsManaged = $env.Properties.protectionLevel -ne "Standard"
        CreatedDate = $env.Properties.createdTime
        CreatedBy = $env.Properties.createdBy.displayName
    }
    $config.Environments += $envConfig
}

# Export to JSON
$config | ConvertTo-Json -Depth 3 | Out-File -FilePath "Environment-Config-$(Get-Date -Format 'yyyyMMdd').json"
Write-Host "Configuration exported to Environment-Config-$(Get-Date -Format 'yyyyMMdd').json"
```

---

## Validation Script

```powershell
<#
.SYNOPSIS
    Validates Control 2.15 - Environment Routing configuration

.DESCRIPTION
    Checks environment routing prerequisites and configuration

.EXAMPLE
    .\Validate-Control-2.15.ps1
#>

Write-Host "=== Control 2.15 Validation ===" -ForegroundColor Cyan

# Connect to Power Platform
Add-PowerAppsAccount

# Check 1: Verify environments exist for routing
Write-Host "`n[Check 1] Production Environments Available" -ForegroundColor Cyan
$prodEnvs = Get-AdminPowerAppEnvironment | Where-Object { $_.EnvironmentType -eq "Production" }
if ($prodEnvs.Count -gt 0) {
    Write-Host "[PASS] Found $($prodEnvs.Count) production environments" -ForegroundColor Green
    $prodEnvs | ForEach-Object { Write-Host "  - $($_.DisplayName)" }
} else {
    Write-Host "[WARN] No production environments found" -ForegroundColor Yellow
}

# Check 2: Verify Managed Environment status
Write-Host "`n[Check 2] Managed Environment Status" -ForegroundColor Cyan
$managedEnvs = $prodEnvs | Where-Object { $_.Properties.protectionLevel -ne "Standard" }
if ($managedEnvs.Count -eq $prodEnvs.Count) {
    Write-Host "[PASS] All production environments are Managed Environments" -ForegroundColor Green
} else {
    Write-Host "[WARN] Not all production environments are Managed" -ForegroundColor Yellow
    $unmanaged = $prodEnvs | Where-Object { $_.Properties.protectionLevel -eq "Standard" }
    $unmanaged | ForEach-Object { Write-Host "  - $($_.DisplayName) is NOT managed" -ForegroundColor Yellow }
}

# Check 3: Verify US region
Write-Host "`n[Check 3] US Region Compliance" -ForegroundColor Cyan
$usEnvs = $prodEnvs | Where-Object { $_.Location -match "unitedstates|US" }
if ($usEnvs.Count -eq $prodEnvs.Count) {
    Write-Host "[PASS] All production environments are in US region" -ForegroundColor Green
} else {
    Write-Host "[WARN] Some environments may not be in US region" -ForegroundColor Yellow
}

Write-Host "`n=== Validation Complete ===" -ForegroundColor Cyan
Write-Host "Note: Environment Groups and Routing Rules must be verified in PPAC portal"
```

---

## Complete Configuration Script

```powershell
<#
.SYNOPSIS
    Complete environment routing configuration for Control 2.15

.DESCRIPTION
    Executes end-to-end environment routing setup including:
    - Environment inventory collection
    - Routing readiness validation
    - Configuration export for documentation

.PARAMETER OutputPath
    Path for output reports

.EXAMPLE
    .\Configure-Control-2.15.ps1 -OutputPath ".\EnvironmentRouting"

.NOTES
    Last Updated: January 2026
    Related Control: Control 2.15 - Environment Routing and Auto-Provisioning
#>

param(
    [string]$OutputPath = ".\EnvironmentRouting-Report"
)

try {
    Write-Host "=== Control 2.15: Environment Routing Configuration ===" -ForegroundColor Cyan

    # Connect to Power Platform
    Add-PowerAppsAccount

    # Ensure output directory exists
    New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null

    # Get all environments
    $environments = Get-AdminPowerAppEnvironment
    Write-Host "[INFO] Found $($environments.Count) environments" -ForegroundColor Cyan

    # Build routing readiness report
    $routingReport = $environments | ForEach-Object {
        $isManaged = $_.Properties.protectionLevel -ne "Standard"
        $isUSRegion = $_.Location -match "unitedstates|US"
        $isActive = $_.States.Runtime -eq "Enabled"
        $isProduction = $_.EnvironmentType -eq "Production"

        [PSCustomObject]@{
            Name = $_.DisplayName
            EnvironmentId = $_.EnvironmentName
            Type = $_.EnvironmentType
            Region = $_.Location
            State = $_.States.Runtime
            IsManaged = $isManaged
            IsUSRegion = $isUSRegion
            IsActive = $isActive
            RoutingReady = ($isManaged -and $isUSRegion -and $isActive)
            CreatedDate = $_.Properties.createdTime
            CreatedBy = $_.Properties.createdBy.displayName
        }
    }

    # Export full inventory
    $routingReport | Export-Csv -Path "$OutputPath\EnvironmentInventory.csv" -NoTypeInformation

    # Display readiness summary
    Write-Host "`n=== Routing Readiness Summary ===" -ForegroundColor Cyan
    $readyCount = ($routingReport | Where-Object { $_.RoutingReady }).Count
    $prodCount = ($routingReport | Where-Object { $_.Type -eq "Production" }).Count
    $managedCount = ($routingReport | Where-Object { $_.IsManaged }).Count

    Write-Host "Total Environments: $($routingReport.Count)"
    Write-Host "Production Environments: $prodCount"
    Write-Host "Managed Environments: $managedCount"
    Write-Host "Routing Ready: $readyCount"

    # Flag environments not ready
    $notReady = $routingReport | Where-Object { $_.Type -eq "Production" -and -not $_.RoutingReady }
    if ($notReady.Count -gt 0) {
        Write-Host "`n[WARN] Production environments NOT ready for routing:" -ForegroundColor Yellow
        $notReady | Select-Object Name, IsManaged, IsUSRegion, IsActive | Format-Table -AutoSize
        $notReady | Export-Csv -Path "$OutputPath\NotRoutingReady.csv" -NoTypeInformation
    } else {
        Write-Host "`n[PASS] All production environments are routing-ready" -ForegroundColor Green
    }

    # Export configuration for documentation
    $config = @{
        ExportDate = Get-Date -Format "yyyy-MM-dd HH:mm"
        TotalEnvironments = $environments.Count
        ProductionEnvironments = $prodCount
        ManagedEnvironments = $managedCount
        RoutingReadyEnvironments = $readyCount
    }
    $config | ConvertTo-Json | Out-File -FilePath "$OutputPath\RoutingConfig.json"

    Write-Host "`n[PASS] Control 2.15 configuration completed successfully" -ForegroundColor Green
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

[Back to Control 2.15](../../../controls/pillar-2-management/2.15-environment-routing.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
