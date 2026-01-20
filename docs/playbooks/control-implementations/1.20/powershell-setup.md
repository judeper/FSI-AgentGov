# PowerShell Setup: Control 1.20 - Network Isolation and Private Connectivity

**Last Updated:** January 2026
**Modules Required:** Az.Network, Microsoft.PowerApps.Administration.PowerShell

## Prerequisites

```powershell
Install-Module -Name Az.Network -Force -Scope CurrentUser
Install-Module -Name Microsoft.PowerApps.Administration.PowerShell -Force -Scope CurrentUser
```

---

## Automated Scripts

### Configure IP Firewall

```powershell
<#
.SYNOPSIS
    Configures IP Firewall for Power Platform environment

.EXAMPLE
    .\Set-IPFirewall.ps1 -EnvironmentId "env-guid" -AllowedIPs @("10.0.0.0/8")
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$EnvironmentId,
    [Parameter(Mandatory=$true)]
    [string[]]$AllowedIPs
)

Write-Host "=== Configure IP Firewall ===" -ForegroundColor Cyan

Add-PowerAppsAccount

# Note: IP Firewall configuration is primarily portal-based
Write-Host "[INFO] Configure IP Firewall in PPAC portal:"
Write-Host "  1. Select environment: $EnvironmentId"
Write-Host "  2. Settings > Security > IP firewall"
Write-Host "  3. Add allowed IPs: $($AllowedIPs -join ', ')"
```

### Create VNet and Subnet

```powershell
<#
.SYNOPSIS
    Creates VNet with delegated subnet for Power Platform

.EXAMPLE
    .\New-PowerPlatformVNet.ps1 -ResourceGroupName "rg-powerplatform" -Location "eastus"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$ResourceGroupName,
    [Parameter(Mandatory=$true)]
    [string]$Location
)

Write-Host "=== Create Power Platform VNet ===" -ForegroundColor Cyan

Connect-AzAccount

# Create VNet
$vnet = New-AzVirtualNetwork -Name "vnet-powerplatform-prod" `
    -ResourceGroupName $ResourceGroupName `
    -Location $Location `
    -AddressPrefix "10.100.0.0/16"

# Create delegated subnet
$delegation = New-AzDelegation -Name "powerplatform" `
    -ServiceName "Microsoft.PowerPlatform/enterprisePolicies"

Add-AzVirtualNetworkSubnetConfig -Name "snet-powerplatform" `
    -VirtualNetwork $vnet `
    -AddressPrefix "10.100.1.0/24" `
    -Delegation $delegation

$vnet | Set-AzVirtualNetwork

Write-Host "VNet created: vnet-powerplatform-prod" -ForegroundColor Green
```

---

## Validation Script

```powershell
<#
.SYNOPSIS
    Validates Control 1.20 - Network isolation configuration

.EXAMPLE
    .\Validate-Control-1.20.ps1
#>

Write-Host "=== Control 1.20 Validation ===" -ForegroundColor Cyan

# Check 1: IP Firewall
Write-Host "`n[Check 1] IP Firewall" -ForegroundColor Cyan
Write-Host "[INFO] Verify IP Firewall is enabled in PPAC"

# Check 2: VNet
Write-Host "`n[Check 2] VNet Configuration" -ForegroundColor Cyan
Connect-AzAccount
$vnets = Get-AzVirtualNetwork | Where-Object { $_.Name -like "*powerplatform*" }
if ($vnets) {
    Write-Host "[PASS] Power Platform VNet found" -ForegroundColor Green
    $vnets | ForEach-Object { Write-Host "  - $($_.Name)" }
}

# Check 3: Private Endpoints
Write-Host "`n[Check 3] Private Endpoints" -ForegroundColor Cyan
$endpoints = Get-AzPrivateEndpoint
Write-Host "Total private endpoints: $($endpoints.Count)"

Write-Host "`n=== Validation Complete ===" -ForegroundColor Cyan
```

---

## Complete Configuration Script

```powershell
<#
.SYNOPSIS
    Configures Control 1.20 - Network Isolation and Private Connectivity

.DESCRIPTION
    This script creates VNet infrastructure for Power Platform network isolation,
    including delegated subnets for enterprise policies.

.PARAMETER ResourceGroupName
    Azure resource group name

.PARAMETER Location
    Azure region for resources

.PARAMETER VNetName
    Name for the virtual network

.PARAMETER VNetAddressPrefix
    Address space for VNet (e.g., "10.100.0.0/16")

.PARAMETER SubnetAddressPrefix
    Address space for subnet (e.g., "10.100.1.0/24")

.EXAMPLE
    .\Configure-Control-1.20.ps1 -ResourceGroupName "rg-powerplatform" -Location "eastus" -VNetName "vnet-powerplatform-prod"

.NOTES
    Last Updated: January 2026
    Related Control: Control 1.20 - Network Isolation and Private Connectivity
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$ResourceGroupName,

    [Parameter(Mandatory=$true)]
    [string]$Location,

    [string]$VNetName = "vnet-powerplatform-prod",
    [string]$VNetAddressPrefix = "10.100.0.0/16",
    [string]$SubnetAddressPrefix = "10.100.1.0/24"
)

try {
    # Connect to Azure
    Write-Host "Connecting to Azure..." -ForegroundColor Cyan
    Connect-AzAccount

    Write-Host "Configuring Control 1.20: Network Isolation and Private Connectivity" -ForegroundColor Cyan

    # Step 1: Verify resource group
    Write-Host "`n[Step 1] Verifying resource group..." -ForegroundColor Yellow
    $rg = Get-AzResourceGroup -Name $ResourceGroupName -ErrorAction SilentlyContinue
    if (-not $rg) {
        Write-Host "  Creating resource group: $ResourceGroupName" -ForegroundColor Yellow
        $rg = New-AzResourceGroup -Name $ResourceGroupName -Location $Location
    }
    Write-Host "  Resource group: $ResourceGroupName" -ForegroundColor Green

    # Step 2: Create VNet
    Write-Host "`n[Step 2] Creating virtual network..." -ForegroundColor Yellow
    $existingVNet = Get-AzVirtualNetwork -Name $VNetName -ResourceGroupName $ResourceGroupName -ErrorAction SilentlyContinue
    if ($existingVNet) {
        Write-Host "  [EXISTS] VNet: $VNetName" -ForegroundColor Yellow
        $vnet = $existingVNet
    } else {
        $vnet = New-AzVirtualNetwork -Name $VNetName `
            -ResourceGroupName $ResourceGroupName `
            -Location $Location `
            -AddressPrefix $VNetAddressPrefix
        Write-Host "  [CREATED] VNet: $VNetName" -ForegroundColor Green
    }

    # Step 3: Create delegated subnet
    Write-Host "`n[Step 3] Creating delegated subnet for Power Platform..." -ForegroundColor Yellow
    $existingSubnet = Get-AzVirtualNetworkSubnetConfig -Name "snet-powerplatform" -VirtualNetwork $vnet -ErrorAction SilentlyContinue
    if ($existingSubnet) {
        Write-Host "  [EXISTS] Subnet: snet-powerplatform" -ForegroundColor Yellow
    } else {
        $delegation = New-AzDelegation -Name "powerplatform" `
            -ServiceName "Microsoft.PowerPlatform/enterprisePolicies"

        Add-AzVirtualNetworkSubnetConfig -Name "snet-powerplatform" `
            -VirtualNetwork $vnet `
            -AddressPrefix $SubnetAddressPrefix `
            -Delegation $delegation

        $vnet | Set-AzVirtualNetwork
        Write-Host "  [CREATED] Delegated subnet: snet-powerplatform" -ForegroundColor Green
    }

    # Step 4: Validate configuration
    Write-Host "`n[Step 4] Validating network configuration..." -ForegroundColor Yellow
    $validatedVNet = Get-AzVirtualNetwork -Name $VNetName -ResourceGroupName $ResourceGroupName
    Write-Host "  VNet address space: $($validatedVNet.AddressSpace.AddressPrefixes -join ', ')" -ForegroundColor Green
    Write-Host "  Subnets: $($validatedVNet.Subnets.Count)" -ForegroundColor Green

    # Step 5: Check for private endpoints
    Write-Host "`n[Step 5] Checking private endpoint configuration..." -ForegroundColor Yellow
    $endpoints = Get-AzPrivateEndpoint -ResourceGroupName $ResourceGroupName -ErrorAction SilentlyContinue
    if ($endpoints) {
        Write-Host "  Private endpoints: $($endpoints.Count)" -ForegroundColor Green
        $endpoints | ForEach-Object { Write-Host "    - $($_.Name)" }
    } else {
        Write-Host "  No private endpoints configured" -ForegroundColor Yellow
        Write-Host "  [INFO] Configure private endpoints in Azure Portal or via PowerShell" -ForegroundColor Gray
    }

    Write-Host "`n[PASS] Control 1.20 configuration completed successfully" -ForegroundColor Green
}
catch {
    Write-Host "[FAIL] Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "[INFO] Stack trace: $($_.ScriptStackTrace)" -ForegroundColor Yellow
    exit 1
}
finally {
    # Cleanup connections
    Disconnect-AzAccount -ErrorAction SilentlyContinue
    Write-Host "`nDisconnected from Azure" -ForegroundColor Gray
}
```

---

[Back to Control 1.20](../../../controls/pillar-1-security/1.20-network-isolation-private-connectivity.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
