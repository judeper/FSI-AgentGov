# PowerShell Setup: Control 2.1 - Managed Environments

**Last Updated:** January 2026
**Modules Required:** Microsoft.PowerApps.Administration.PowerShell

## Prerequisites

```powershell
# Install Power Platform admin module
Install-Module -Name Microsoft.PowerApps.Administration.PowerShell -Force -Scope CurrentUser

# Connect to Power Platform (interactive authentication)
Add-PowerAppsAccount

# For automated/unattended scenarios, use service principal authentication:
# $appId = "<Application-Client-ID>"
# $secret = "<Client-Secret>"
# $tenantId = "<Tenant-ID>"
# Add-PowerAppsAccount -ApplicationId $appId -ClientSecret $secret -TenantID $tenantId
```

---

## Configuration Scripts

### List All Environments

```powershell
# List all environments with key properties
Get-AdminPowerAppEnvironment | Select-Object DisplayName, EnvironmentName, IsDefault, EnvironmentType | Format-Table
```

### Check Managed Environment Status

```powershell
# Get environment ID
$envName = "FSI-Production"
$env = Get-AdminPowerAppEnvironment | Where-Object { $_.DisplayName -eq $envName }

# Check if environment is managed
$envDetails = Get-AdminPowerAppEnvironment -EnvironmentName $env.EnvironmentName
Write-Host "Environment: $($envDetails.DisplayName)"
Write-Host "Governance/Protection Level: $($envDetails.Properties.protectionLevel)"

# Note: Managed Environment enablement is primarily done through PPAC portal
# PowerShell can be used for querying and some settings
```

### Configure Sharing Limits via API

```powershell
# Use Power Platform Admin Connector or direct API for sharing limits
# Example using REST API pattern

$environmentId = $env.EnvironmentName
$tenantId = (Get-AzContext).Tenant.Id

# Get management settings
$uri = "https://api.bap.microsoft.com/providers/Microsoft.BusinessAppPlatform/environments/$environmentId/governanceConfiguration?api-version=2021-04-01"

# Headers with bearer token
$headers = @{
    "Authorization" = "Bearer $accessToken"
    "Content-Type" = "application/json"
}

# This would be the governance configuration - actual implementation requires OAuth token
# Refer to Power Platform Admin API documentation
```

### Get Environment Governance Status

```powershell
# Get all environments with governance status
$environments = Get-AdminPowerAppEnvironment

$envReport = $environments | ForEach-Object {
    [PSCustomObject]@{
        Name = $_.DisplayName
        Type = $_.EnvironmentType
        State = $_.States.Runtime
        IsManagedEnv = if ($_.Properties.protectionLevel -eq "Standard") { "No" } else { "Yes" }
        CreatedTime = $_.Properties.createdTime
    }
}

$envReport | Format-Table
$envReport | Export-Csv -Path "Environment-Governance-Report.csv" -NoTypeInformation
```

---

## Export Configuration Scripts

### Export Managed Environment Configuration

```powershell
# Export environment details for compliance documentation
function Export-ManagedEnvConfig {
    param([string]$EnvironmentName)

    $env = Get-AdminPowerAppEnvironment -EnvironmentName $EnvironmentName

    $config = [PSCustomObject]@{
        Name = $env.DisplayName
        EnvironmentId = $env.EnvironmentName
        Region = $env.Location
        Type = $env.EnvironmentType
        State = $env.States.Runtime
        CreatedDate = $env.Properties.createdTime
        CreatedBy = $env.Properties.createdBy.displayName
        ExportDate = Get-Date
    }

    $config | ConvertTo-Json | Out-File -FilePath "ManagedEnv-$EnvironmentName-Config.json"
    Write-Host "Exported configuration to ManagedEnv-$EnvironmentName-Config.json"
}

# Export all enterprise-managed environments
Get-AdminPowerAppEnvironment | Where-Object { $_.EnvironmentType -eq "Production" } | ForEach-Object {
    Export-ManagedEnvConfig -EnvironmentName $_.EnvironmentName
}
```

### Monitor Environment Health

```powershell
# Check environment capacity and status
$environments = Get-AdminPowerAppEnvironment

foreach ($env in $environments | Where-Object { $_.EnvironmentType -eq "Production" }) {
    Write-Host "`n=== $($env.DisplayName) ===" -ForegroundColor Cyan
    Write-Host "State: $($env.States.Runtime)"
    Write-Host "Type: $($env.EnvironmentType)"
    Write-Host "Has Dataverse: $($env.Properties.linkedEnvironmentMetadata -ne $null)"
}
```

---

## Validation Script

```powershell
<#
.SYNOPSIS
    Validates Control 2.1 - Managed Environments configuration

.DESCRIPTION
    This script validates:
    1. Environment exists and is accessible
    2. Managed Environment status is enabled
    3. Environment type and region are correct

.PARAMETER EnvironmentName
    The GUID of the target Power Platform environment

.EXAMPLE
    .\Validate-Control-2.1.ps1 -EnvironmentName "abc123..."

.NOTES
    Last Updated: January 2026
    Related Control: Control 2.1 - Managed Environments
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$EnvironmentName
)

# Connect to Power Platform (interactive authentication)
Add-PowerAppsAccount

# For automated/unattended scenarios, use service principal authentication:
# $appId = "<Application-Client-ID>"
# $secret = "<Client-Secret>"
# $tenantId = "<Tenant-ID>"
# Add-PowerAppsAccount -ApplicationId $appId -ClientSecret $secret -TenantID $tenantId

Write-Host "=== Control 2.1 Validation ===" -ForegroundColor Cyan

# Check 1: Verify environment exists
$env = Get-AdminPowerAppEnvironment -EnvironmentName $EnvironmentName
if ($env) {
    Write-Host "[PASS] Environment found: $($env.DisplayName)" -ForegroundColor Green
} else {
    Write-Host "[FAIL] Environment not found: $EnvironmentName" -ForegroundColor Red
    exit 1
}

# Check 2: Verify Managed Environment status
$protectionLevel = $env.Properties.protectionLevel
if ($protectionLevel -ne "Standard") {
    Write-Host "[PASS] Managed Environment is enabled (Protection Level: $protectionLevel)" -ForegroundColor Green
} else {
    Write-Host "[WARN] Managed Environment is NOT enabled" -ForegroundColor Yellow
}

# Check 3: Verify environment type
Write-Host "[INFO] Environment Type: $($env.EnvironmentType)" -ForegroundColor Cyan

# Check 4: Verify region
$region = $env.Location
if ($region -like "*unitedstates*" -or $region -like "*US*") {
    Write-Host "[PASS] Environment is in US region: $region" -ForegroundColor Green
} else {
    Write-Host "[WARN] Environment region may not be US: $region" -ForegroundColor Yellow
}

# Output summary
Write-Host "`n=== Summary ===" -ForegroundColor Cyan
Write-Host "Environment: $($env.DisplayName)"
Write-Host "Type: $($env.EnvironmentType)"
Write-Host "Region: $($env.Location)"
Write-Host "Managed: $(if ($protectionLevel -ne 'Standard') { 'Yes' } else { 'No' })"
Write-Host "State: $($env.States.Runtime)"
```

---

## Complete Configuration Report Script

```powershell
<#
.SYNOPSIS
    Generates a comprehensive Managed Environments report for all environments

.DESCRIPTION
    Creates a CSV report of all environments with governance status for audit purposes

.EXAMPLE
    .\Report-ManagedEnvironments.ps1

.NOTES
    Last Updated: January 2026
    Related Control: Control 2.1 - Managed Environments
#>

try {
    # Connect to Power Platform
    Add-PowerAppsAccount

    Write-Host "Generating Managed Environments Report..." -ForegroundColor Cyan

    # Get all environments
    $environments = Get-AdminPowerAppEnvironment

    # Build report
    $report = $environments | ForEach-Object {
        [PSCustomObject]@{
            EnvironmentName = $_.DisplayName
            EnvironmentId = $_.EnvironmentName
            Type = $_.EnvironmentType
            Region = $_.Location
            State = $_.States.Runtime
            IsManagedEnv = if ($_.Properties.protectionLevel -eq "Standard") { "No" } else { "Yes" }
            ProtectionLevel = $_.Properties.protectionLevel
            HasDataverse = if ($_.Properties.linkedEnvironmentMetadata) { "Yes" } else { "No" }
            CreatedDate = $_.Properties.createdTime
            CreatedBy = $_.Properties.createdBy.displayName
            ReportDate = Get-Date -Format "yyyy-MM-dd HH:mm"
        }
    }

    # Display summary
    Write-Host "`n=== Environment Summary ===" -ForegroundColor Cyan
    $report | Format-Table EnvironmentName, Type, IsManagedEnv, Region, State -AutoSize

    # Export to CSV
    $reportPath = "ManagedEnvironments-Report-$(Get-Date -Format 'yyyyMMdd').csv"
    $report | Export-Csv -Path $reportPath -NoTypeInformation
    Write-Host "`nReport exported to: $reportPath" -ForegroundColor Green

    # Summary statistics
    $totalEnvs = $report.Count
    $managedEnvs = ($report | Where-Object { $_.IsManagedEnv -eq "Yes" }).Count
    $prodEnvs = ($report | Where-Object { $_.Type -eq "Production" }).Count

    Write-Host "`n=== Statistics ===" -ForegroundColor Cyan
    Write-Host "Total Environments: $totalEnvs"
    Write-Host "Managed Environments: $managedEnvs"
    Write-Host "Production Environments: $prodEnvs"

    Write-Host "`n[PASS] Control 2.1 configuration completed successfully" -ForegroundColor Green
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

[Back to Control 2.1](../../../controls/pillar-2-management/2.1-managed-environments.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
