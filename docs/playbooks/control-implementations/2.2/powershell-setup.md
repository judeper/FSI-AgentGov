# PowerShell Setup: Control 2.2 - Environment Groups and Tier Classification

**Last Updated:** January 2026
**Modules Required:** Microsoft.PowerApps.Administration.PowerShell

## Prerequisites

```powershell
# Install the Power Platform Admin module if not present
Install-Module -Name Microsoft.PowerApps.Administration.PowerShell -Force -AllowClobber -Scope CurrentUser

# Import the module
Import-Module Microsoft.PowerApps.Administration.PowerShell

# Connect to Power Platform (interactive authentication)
Add-PowerAppsAccount

# For service principal authentication (recommended for automation)
$appId = "<Application-Client-ID>"
$secret = "<Client-Secret>"
$tenantId = "<Tenant-ID>"
Add-PowerAppsAccount -ApplicationId $appId -ClientSecret $secret -TenantID $tenantId
```

---

## Query Scripts

### Get Environment Groups

```powershell
# List all environment groups in the tenant
Get-AdminPowerAppEnvironmentGroup

# Get a specific environment group by ID
$groupId = "<EnvironmentGroup-ID>"
Get-AdminPowerAppEnvironmentGroup -EnvironmentGroupId $groupId

# List environments in a specific group
Get-AdminPowerAppEnvironment | Where-Object { $_.EnvironmentGroupId -eq $groupId }
```

### List Environments by Group

```powershell
# Get all environments and group them by environment group
$environments = Get-AdminPowerAppEnvironment

$environments |
    Group-Object -Property EnvironmentGroupId |
    ForEach-Object {
        Write-Host "`nGroup ID: $($_.Name)" -ForegroundColor Cyan
        Write-Host "Environment Count: $($_.Count)"
        $_.Group | Select-Object DisplayName, EnvironmentName | Format-Table
    }
```

### Add Environment to Group

```powershell
# Add an environment to an environment group
$environmentId = "<Environment-ID>"
$groupId = "<EnvironmentGroup-ID>"

# Using Set-AdminPowerAppEnvironment to update group membership
Set-AdminPowerAppEnvironment -EnvironmentName $environmentId -EnvironmentGroupId $groupId

# Verify the assignment
$env = Get-AdminPowerAppEnvironment -EnvironmentName $environmentId
Write-Host "Environment: $($env.DisplayName)"
Write-Host "Environment Group: $($env.EnvironmentGroupId)"
```

### Check Group Rules Application

```powershell
# Get environment group rules (rule management is primarily done via PPAC portal)
# Use the following to query environment settings that reflect group rules

$groupId = "<EnvironmentGroup-ID>"
$environments = Get-AdminPowerAppEnvironment | Where-Object { $_.EnvironmentGroupId -eq $groupId }

foreach ($env in $environments) {
    Write-Host "`nEnvironment: $($env.DisplayName)" -ForegroundColor Cyan
    Write-Host "  Managed: $($env.Properties.governanceConfiguration.protectionLevel)"
    Write-Host "  Group ID: $($env.EnvironmentGroupId)"
    Write-Host "  Region: $($env.Location)"
    Write-Host "  Type: $($env.EnvironmentType)"
}
```

---

## Export Scripts

### Export Environment Group Configuration

```powershell
# Export environment group configuration for documentation
$exportPath = "C:\Exports\EnvironmentGroups"
New-Item -ItemType Directory -Path $exportPath -Force | Out-Null

# Get all environment groups
$groups = Get-AdminPowerAppEnvironmentGroup

# Export group details
$groupExport = $groups | Select-Object @{
    Name = 'GroupId'; Expression = { $_.EnvironmentGroupId }
}, @{
    Name = 'DisplayName'; Expression = { $_.DisplayName }
}, @{
    Name = 'Description'; Expression = { $_.Description }
}, @{
    Name = 'CreatedTime'; Expression = { $_.CreatedTime }
}

$timestamp = Get-Date -Format 'yyyyMMdd'
$groupExport | Export-Csv -Path "$exportPath\EnvironmentGroups_$timestamp.csv" -NoTypeInformation

Write-Host "Exported $(($groups | Measure-Object).Count) environment groups to $exportPath\EnvironmentGroups_$timestamp.csv" -ForegroundColor Green
```

### Export Environment-to-Group Mapping

```powershell
# Export environment-to-group mapping for audit evidence
$exportPath = "C:\Exports\EnvironmentGroups"
New-Item -ItemType Directory -Path $exportPath -Force | Out-Null

$environments = Get-AdminPowerAppEnvironment
$envMapping = $environments | Select-Object @{
    Name = 'EnvironmentName'; Expression = { $_.DisplayName }
}, @{
    Name = 'EnvironmentId'; Expression = { $_.EnvironmentName }
}, @{
    Name = 'EnvironmentGroupId'; Expression = { $_.EnvironmentGroupId }
}, @{
    Name = 'EnvironmentType'; Expression = { $_.EnvironmentType }
}, @{
    Name = 'Region'; Expression = { $_.Location }
}, @{
    Name = 'IsManaged'; Expression = {
        if ($_.Properties.governanceConfiguration.protectionLevel -eq 'Standard') { 'No' } else { 'Yes' }
    }
}, @{
    Name = 'ExportDate'; Expression = { Get-Date -Format 'yyyy-MM-dd HH:mm' }
}

$timestamp = Get-Date -Format 'yyyyMMdd'
$envMapping | Export-Csv -Path "$exportPath\EnvironmentGroupMapping_$timestamp.csv" -NoTypeInformation

Write-Host "Exported $(($environments | Measure-Object).Count) environments to $exportPath\EnvironmentGroupMapping_$timestamp.csv" -ForegroundColor Green
```

### Complete Export for Audit Evidence

```powershell
<#
.SYNOPSIS
    Exports complete environment group configuration for audit evidence

.DESCRIPTION
    Creates comprehensive CSV exports of:
    - All environment groups with details
    - Environment-to-group mappings
    - Summary statistics

.EXAMPLE
    .\Export-EnvironmentGroups.ps1

.NOTES
    Last Updated: January 2026
    Related Control: Control 2.2 - Environment Groups and Tier Classification
#>

try {
    # Connect to Power Platform
    Add-PowerAppsAccount

    $exportPath = "C:\Exports\EnvironmentGroups"
    $timestamp = Get-Date -Format 'yyyyMMdd_HHmm'
    New-Item -ItemType Directory -Path "$exportPath\$timestamp" -Force | Out-Null

    Write-Host "=== Environment Groups Export ===" -ForegroundColor Cyan
    Write-Host "Export Path: $exportPath\$timestamp"

    # Export groups
    $groups = Get-AdminPowerAppEnvironmentGroup
    $groups | Select-Object EnvironmentGroupId, DisplayName, Description, CreatedTime |
        Export-Csv -Path "$exportPath\$timestamp\Groups.csv" -NoTypeInformation
    Write-Host "  Groups: $(($groups | Measure-Object).Count)" -ForegroundColor Green

    # Export environments
    $environments = Get-AdminPowerAppEnvironment
    $environments | Select-Object DisplayName, EnvironmentName, EnvironmentGroupId, EnvironmentType, Location,
        @{ Name = 'IsManaged'; Expression = { $_.Properties.governanceConfiguration.protectionLevel -ne 'Standard' }} |
        Export-Csv -Path "$exportPath\$timestamp\Environments.csv" -NoTypeInformation
    Write-Host "  Environments: $(($environments | Measure-Object).Count)" -ForegroundColor Green

    # Summary by group
    $summary = $environments | Group-Object EnvironmentGroupId | Select-Object @{
        Name = 'GroupId'; Expression = { $_.Name }
    }, @{
        Name = 'EnvironmentCount'; Expression = { $_.Count }
    }, @{
        Name = 'Environments'; Expression = { ($_.Group | Select-Object -ExpandProperty DisplayName) -join '; ' }
    }
    $summary | Export-Csv -Path "$exportPath\$timestamp\Summary.csv" -NoTypeInformation

    Write-Host "`nExport complete: $exportPath\$timestamp" -ForegroundColor Green

    Write-Host "`n[PASS] Control 2.2 configuration completed successfully" -ForegroundColor Green
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

## Validation Script

```powershell
<#
.SYNOPSIS
    Validates Control 2.2 - Environment Groups and Tier Classification

.DESCRIPTION
    Validates:
    1. Environment groups exist
    2. Environments are assigned to groups
    3. Critical environments are in appropriate tier groups
    4. All grouped environments are Managed Environments

.PARAMETER GroupId
    Optional: Specific group ID to validate

.EXAMPLE
    .\Validate-Control-2.2.ps1
    .\Validate-Control-2.2.ps1 -GroupId "abc123"

.NOTES
    Last Updated: January 2026
    Related Control: Control 2.2 - Environment Groups and Tier Classification
#>

param(
    [string]$GroupId
)

# Connect to Power Platform
Add-PowerAppsAccount

Write-Host "=== Control 2.2 Validation ===" -ForegroundColor Cyan

# Check 1: Verify environment groups exist
$groups = Get-AdminPowerAppEnvironmentGroup
if ($groups) {
    Write-Host "[PASS] $(($groups | Measure-Object).Count) environment groups found" -ForegroundColor Green
    $groups | Select-Object DisplayName, EnvironmentGroupId | Format-Table
} else {
    Write-Host "[FAIL] No environment groups found" -ForegroundColor Red
}

# Check 2: Verify environments are assigned to groups
$environments = Get-AdminPowerAppEnvironment
$groupedEnvs = $environments | Where-Object { $_.EnvironmentGroupId }
$ungroupedEnvs = $environments | Where-Object { -not $_.EnvironmentGroupId }

Write-Host "`n[INFO] Environment Assignment Summary:" -ForegroundColor Cyan
Write-Host "  Grouped environments: $(($groupedEnvs | Measure-Object).Count)"
Write-Host "  Ungrouped environments: $(($ungroupedEnvs | Measure-Object).Count)"

if ($ungroupedEnvs) {
    Write-Host "`n[WARN] Ungrouped environments:" -ForegroundColor Yellow
    $ungroupedEnvs | Select-Object DisplayName, EnvironmentType | Format-Table
}

# Check 3: Verify grouped environments are Managed
$unmanagedGrouped = $groupedEnvs | Where-Object {
    $_.Properties.governanceConfiguration.protectionLevel -eq 'Standard'
}

if ($unmanagedGrouped) {
    Write-Host "`n[WARN] Grouped environments that are NOT Managed:" -ForegroundColor Yellow
    $unmanagedGrouped | Select-Object DisplayName, EnvironmentGroupId | Format-Table
} else {
    Write-Host "`n[PASS] All grouped environments are Managed Environments" -ForegroundColor Green
}

# Check 4: Production environments should be in groups
$prodEnvs = $environments | Where-Object { $_.EnvironmentType -eq 'Production' }
$ungroupedProd = $prodEnvs | Where-Object { -not $_.EnvironmentGroupId }

if ($ungroupedProd) {
    Write-Host "`n[WARN] Production environments not in a group:" -ForegroundColor Yellow
    $ungroupedProd | Select-Object DisplayName | Format-Table
} else {
    Write-Host "[PASS] All production environments are in groups" -ForegroundColor Green
}

# Summary
Write-Host "`n=== Validation Summary ===" -ForegroundColor Cyan
Write-Host "Total Groups: $(($groups | Measure-Object).Count)"
Write-Host "Total Environments: $(($environments | Measure-Object).Count)"
Write-Host "Grouped: $(($groupedEnvs | Measure-Object).Count)"
Write-Host "Ungrouped: $(($ungroupedEnvs | Measure-Object).Count)"
```

---

## Notes

> **Environment group creation** is primarily performed through the Power Platform Admin Center portal. PowerShell support for group creation may be limited or require preview modules.

> **Rule management** is done via PPAC portal. PowerShell can be used to query environment settings that reflect applied group rules.

---

[Back to Control 2.2](../../../controls/pillar-2-management/2.2-environment-groups-and-tier-classification.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
