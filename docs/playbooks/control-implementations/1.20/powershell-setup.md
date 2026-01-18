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

[Back to Control 1.20](../../../controls/pillar-1-security/1.20-network-isolation-private-connectivity.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
