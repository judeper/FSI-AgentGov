# PowerShell Setup: Control 1.14 - Data Minimization and Agent Scope Control

**Last Updated:** January 2026
**Modules Required:** Microsoft.PowerApps.Administration.PowerShell, PnP.PowerShell

## Prerequisites

```powershell
# Install required modules
Install-Module -Name Microsoft.PowerApps.Administration.PowerShell -Force -Scope CurrentUser
Install-Module -Name PnP.PowerShell -Force -Scope CurrentUser
```

---

## Automated Scripts

### Export Agent Data Source Inventory

```powershell
<#
.SYNOPSIS
    Exports data source inventory for all agents in an environment

.DESCRIPTION
    Generates report of connectors and knowledge sources per agent

.EXAMPLE
    .\Export-AgentDataInventory.ps1 -EnvironmentId "env-guid"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$EnvironmentId,
    [string]$OutputPath = ".\AgentDataInventory.csv"
)

Write-Host "=== Agent Data Source Inventory ===" -ForegroundColor Cyan

# Connect to Power Platform
Add-PowerAppsAccount

# Get all apps (agents) in environment
$apps = Get-AdminPowerApp -EnvironmentName $EnvironmentId

$inventory = @()

foreach ($app in $apps) {
    Write-Host "Processing: $($app.DisplayName)" -ForegroundColor Yellow

    # Get connections used by app
    $connections = Get-AdminPowerAppConnection -EnvironmentName $EnvironmentId |
        Where-Object { $_.ConnectorName -ne $null }

    foreach ($conn in $connections) {
        $inventory += [PSCustomObject]@{
            AgentName = $app.DisplayName
            AgentId = $app.AppName
            ConnectorType = $conn.ConnectorName
            ConnectionId = $conn.ConnectionId
            CreatedTime = $conn.CreatedTime
            Status = $conn.Statuses.Status
            Environment = $EnvironmentId
            ExportDate = Get-Date
        }
    }
}

$inventory | Export-Csv -Path $OutputPath -NoTypeInformation
Write-Host "Inventory exported to: $OutputPath" -ForegroundColor Green
Write-Host "Total connections found: $($inventory.Count)"
```

### Audit Connector Usage

```powershell
<#
.SYNOPSIS
    Audits connector usage across environments for compliance

.DESCRIPTION
    Identifies unused or unauthorized connectors

.EXAMPLE
    .\Audit-ConnectorUsage.ps1 -ApprovedConnectors @("SharePoint", "Dataverse")
#>

param(
    [Parameter(Mandatory=$true)]
    [string[]]$ApprovedConnectors,
    [string]$EnvironmentId
)

Write-Host "=== Connector Usage Audit ===" -ForegroundColor Cyan

Add-PowerAppsAccount

$environments = if ($EnvironmentId) {
    Get-AdminPowerAppEnvironment -EnvironmentName $EnvironmentId
} else {
    Get-AdminPowerAppEnvironment
}

$violations = @()

foreach ($env in $environments) {
    Write-Host "Checking environment: $($env.DisplayName)" -ForegroundColor Yellow

    $connections = Get-AdminPowerAppConnection -EnvironmentName $env.EnvironmentName

    foreach ($conn in $connections) {
        $isApproved = $ApprovedConnectors -contains $conn.ConnectorName

        if (-not $isApproved) {
            $violations += [PSCustomObject]@{
                Environment = $env.DisplayName
                ConnectorName = $conn.ConnectorName
                ConnectionId = $conn.ConnectionId
                CreatedBy = $conn.CreatedBy.displayName
                CreatedTime = $conn.CreatedTime
                Status = "UNAUTHORIZED"
            }
        }
    }
}

if ($violations.Count -gt 0) {
    Write-Host "`n=== UNAUTHORIZED CONNECTORS FOUND ===" -ForegroundColor Red
    $violations | Format-Table -AutoSize
    $violations | Export-Csv -Path ".\ConnectorViolations.csv" -NoTypeInformation
} else {
    Write-Host "`nNo unauthorized connectors found." -ForegroundColor Green
}
```

### Configure SharePoint Agent Access Group

```powershell
<#
.SYNOPSIS
    Creates SharePoint group for agent access with minimum permissions

.DESCRIPTION
    Creates dedicated security group for agent service account access

.EXAMPLE
    .\New-AgentAccessGroup.ps1 -SiteUrl "https://tenant.sharepoint.com/sites/HR" -AgentName "HRBot"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$SiteUrl,
    [Parameter(Mandatory=$true)]
    [string]$AgentName,
    [string]$PermissionLevel = "Read"
)

Write-Host "=== Create Agent Access Group ===" -ForegroundColor Cyan

# Connect to SharePoint
Connect-PnPOnline -Url $SiteUrl -Interactive

$groupName = "SG-AgentAccess-$AgentName"

# Check if group exists
$existingGroup = Get-PnPGroup -Identity $groupName -ErrorAction SilentlyContinue

if ($existingGroup) {
    Write-Host "Group already exists: $groupName" -ForegroundColor Yellow
} else {
    # Create new group
    $group = New-PnPGroup -Title $groupName -Description "Agent access group for $AgentName - $PermissionLevel only"
    Write-Host "Created group: $groupName" -ForegroundColor Green

    # Set permissions
    Set-PnPGroupPermissions -Identity $groupName -AddRole $PermissionLevel
    Write-Host "Assigned permission level: $PermissionLevel" -ForegroundColor Green
}

Write-Host "`nNext steps:"
Write-Host "1. Add agent service account to group: $groupName"
Write-Host "2. Document in agent data inventory"
Write-Host "3. Set review date for access validation"
```

---

## Validation Script

```powershell
<#
.SYNOPSIS
    Validates Control 1.14 - Data Minimization configuration

.EXAMPLE
    .\Validate-Control-1.14.ps1 -EnvironmentId "env-guid"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$EnvironmentId
)

Write-Host "=== Control 1.14 Validation ===" -ForegroundColor Cyan

Add-PowerAppsAccount

# Check 1: DLP policies exist
Write-Host "`n[Check 1] DLP Policy Configuration" -ForegroundColor Cyan
$dlpPolicies = Get-DlpPolicy | Where-Object { $_.environments -contains $EnvironmentId }
if ($dlpPolicies) {
    Write-Host "[PASS] DLP policy found for environment" -ForegroundColor Green
    $dlpPolicies | ForEach-Object { Write-Host "  - $($_.displayName)" }
} else {
    Write-Host "[FAIL] No DLP policy for environment" -ForegroundColor Red
}

# Check 2: Connector restrictions
Write-Host "`n[Check 2] Connector Restrictions" -ForegroundColor Cyan
$connections = Get-AdminPowerAppConnection -EnvironmentName $EnvironmentId
$connectorTypes = $connections | Select-Object -ExpandProperty ConnectorName -Unique
Write-Host "Active connector types: $($connectorTypes -join ', ')"

# Check 3: Recent scope changes
Write-Host "`n[Check 3] Recent Scope Changes" -ForegroundColor Cyan
Write-Host "[INFO] Review Purview audit log for ConnectorAdded events"
Write-Host "[INFO] Query: Activities = ConnectorAdded, last 30 days"

Write-Host "`n=== Validation Complete ===" -ForegroundColor Cyan
```

---

[Back to Control 1.14](../../../controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
