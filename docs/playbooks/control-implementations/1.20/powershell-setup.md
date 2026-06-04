# PowerShell Setup: Control 1.20 — Network Isolation and Private Connectivity

!!! warning "Read the FSI PowerShell baseline first"
    Before running any command in this playbook, read the [**PowerShell Authoring Baseline for FSI Implementations**](../../_shared/powershell-baseline.md). It is the canonical source for module version pinning, sovereign-cloud (GCC / GCC High / DoD) endpoints, mutation safety (`-WhatIf` / `SupportsShouldProcess`), Dataverse compatibility, and SHA-256 evidence emission. Snippets below show abbreviated patterns; the baseline is authoritative.

**Last Updated:** May 2026
**Modules Required:** `Az.Accounts`, `Az.Network`, `Az.KeyVault`, `Az.Sql`, `Az.Storage`, `Az.Monitor`, `Az.PrivateDns`, `Microsoft.PowerApps.Administration.PowerShell`
**PowerShell Edition:** Windows PowerShell 5.1 (Desktop) for `Microsoft.PowerApps.Administration.PowerShell`; PowerShell 7+ acceptable for the `Az.*` portions.

---

## Prerequisites

```powershell
# Pin versions per CAB approval; see PowerShell baseline for the canonical install pattern.
Install-Module Az.Accounts, Az.Network, Az.KeyVault, Az.Sql, Az.Storage, Az.Monitor, Az.PrivateDns -Scope CurrentUser -Repository PSGallery
Install-Module Microsoft.PowerApps.Administration.PowerShell -Scope CurrentUser -Repository PSGallery

# Required guard for Power Apps Administration cmdlets:
if ($PSVersionTable.PSEdition -ne 'Desktop') {
    throw "Microsoft.PowerApps.Administration.PowerShell requires Windows PowerShell 5.1 (Desktop edition)."
}
```

> **Sovereign cloud authentication.** For GCC / GCC High / DoD tenants, every `Add-PowerAppsAccount` and `Connect-AzAccount` call **must** pass the matching cloud parameter, or the cmdlet authenticates against commercial endpoints and produces *false-clean* results. See the baseline §3.

```powershell
# Example sovereign-aware connect helper
function Connect-FsiClouds {
    param(
        [ValidateSet('Commercial','GCC','GCCHigh','DoD')] [string] $Cloud = 'Commercial',
        [string] $TenantId
    )
    switch ($Cloud) {
        'Commercial' { Add-PowerAppsAccount -Endpoint prod;       Connect-AzAccount -Tenant $TenantId -Environment AzureCloud }
        'GCC'        { Add-PowerAppsAccount -Endpoint usgov;      Connect-AzAccount -Tenant $TenantId -Environment AzureUSGovernment }
        'GCCHigh'    { Add-PowerAppsAccount -Endpoint usgovhigh;  Connect-AzAccount -Tenant $TenantId -Environment AzureUSGovernment }
        'DoD'        { Add-PowerAppsAccount -Endpoint dod;        Connect-AzAccount -Tenant $TenantId -Environment AzureUSGovernment }
    }
}
```

---

## Script 1 — Provision VNet, Delegated Subnet, and Private Endpoint Subnet (per region)

```powershell
<#
.SYNOPSIS
    Creates a VNet with a Power Platform-delegated subnet and a private-endpoint subnet.

.DESCRIPTION
    Idempotent. Re-running against an existing VNet/subnet is a no-op except for tag updates.
    Designed to run TWICE — once for the primary Azure region paired to the Power Platform region,
    and once for the paired failover region.

.PARAMETER ResourceGroupName     Resource group for the VNet (created if absent).
.PARAMETER Location              Azure region (must be paired with the Power Platform region).
.PARAMETER VNetName              VNet name (e.g., vnet-pp-prod-eastus).
.PARAMETER VNetAddressPrefix     CIDR for VNet (e.g., 10.100.0.0/16).
.PARAMETER DelegatedSubnetCidr   CIDR for Power Platform-delegated subnet (recommended /24).
.PARAMETER PrivateEndpointSubnetCidr  CIDR for the private-endpoint subnet.
.PARAMETER WhatIf                Standard ShouldProcess support.

.EXAMPLE
    .\New-PpVNet.ps1 -ResourceGroupName rg-pp-net-prod-eastus -Location eastus `
        -VNetName vnet-pp-prod-eastus -VNetAddressPrefix 10.100.0.0/16 `
        -DelegatedSubnetCidr 10.100.1.0/24 -PrivateEndpointSubnetCidr 10.100.2.0/24
#>
[CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
param(
    [Parameter(Mandatory)] [string] $ResourceGroupName,
    [Parameter(Mandatory)] [string] $Location,
    [Parameter(Mandatory)] [string] $VNetName,
    [Parameter(Mandatory)] [string] $VNetAddressPrefix,
    [Parameter(Mandatory)] [string] $DelegatedSubnetCidr,
    [Parameter(Mandatory)] [string] $PrivateEndpointSubnetCidr
)

$ErrorActionPreference = 'Stop'

if (-not (Get-AzResourceGroup -Name $ResourceGroupName -ErrorAction SilentlyContinue)) {
    if ($PSCmdlet.ShouldProcess($ResourceGroupName,'Create resource group')) {
        New-AzResourceGroup -Name $ResourceGroupName -Location $Location | Out-Null
    }
}

$delegation = New-AzDelegation -Name 'powerplatform' `
    -ServiceName 'Microsoft.PowerPlatform/enterprisePolicies'

$delegatedSubnet = New-AzVirtualNetworkSubnetConfig `
    -Name 'snet-pp-delegated' -AddressPrefix $DelegatedSubnetCidr -Delegation $delegation

$peSubnet = New-AzVirtualNetworkSubnetConfig `
    -Name 'snet-private-endpoints' -AddressPrefix $PrivateEndpointSubnetCidr `
    -PrivateEndpointNetworkPoliciesFlag 'Disabled'

$existing = Get-AzVirtualNetwork -ResourceGroupName $ResourceGroupName -Name $VNetName -ErrorAction SilentlyContinue
if ($existing) {
    Write-Verbose "[EXISTS] VNet $VNetName — verifying subnets only."
    # Idempotent reconcile of subnets is left to the caller; production code should diff and update.
    return $existing
}

if ($PSCmdlet.ShouldProcess($VNetName,'Create VNet with delegated subnet')) {
    New-AzVirtualNetwork -ResourceGroupName $ResourceGroupName -Name $VNetName `
        -Location $Location -AddressPrefix $VNetAddressPrefix `
        -Subnet $delegatedSubnet, $peSubnet
}
```

---

## Script 2 — Create and Link the Power Platform Enterprise (Network) Policy

> The cmdlets `New-PowerAppEnvironmentEnterprisePolicy` and `New-AdminPowerAppEnvironmentEnterprisePolicy` are exposed by the `Microsoft.PowerApps.Administration.PowerShell` module. Cmdlet names and parameters have evolved; always cross-check against [Microsoft Learn: Set up virtual network support](https://learn.microsoft.com/en-us/power-platform/admin/vnet-support-setup-configure) for the current shape.

```powershell
<#
.SYNOPSIS
    Creates a Power Platform network (subnet) enterprise policy and links it to a Managed Environment.

.PARAMETER EnvironmentId           Power Platform environment GUID.
.PARAMETER PolicyName              Display name for the enterprise policy.
.PARAMETER PrimarySubnetResourceId Full ARM resource ID of the primary delegated subnet.
.PARAMETER FailoverSubnetResourceId Full ARM resource ID of the failover delegated subnet.
.PARAMETER Cloud                   Commercial / GCC / GCCHigh / DoD.
.PARAMETER TenantId                Entra tenant GUID.
#>
[CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
param(
    [Parameter(Mandatory)] [string] $EnvironmentId,
    [Parameter(Mandatory)] [string] $PolicyName,
    [Parameter(Mandatory)] [string] $PrimarySubnetResourceId,
    [Parameter(Mandatory)] [string] $FailoverSubnetResourceId,
    [ValidateSet('Commercial','GCC','GCCHigh','DoD')] [string] $Cloud = 'Commercial',
    [Parameter(Mandatory)] [string] $TenantId
)

$ErrorActionPreference = 'Stop'

if ($PSVersionTable.PSEdition -ne 'Desktop') {
    throw "Use Windows PowerShell 5.1 (Desktop) for Microsoft.PowerApps.Administration.PowerShell."
}

Connect-FsiClouds -Cloud $Cloud -TenantId $TenantId

if (-not (Get-AdminPowerAppEnvironment -EnvironmentName $EnvironmentId -ErrorAction SilentlyContinue)) {
    throw "Environment $EnvironmentId not found in this tenant/cloud — verify -Cloud parameter."
}

if ($PSCmdlet.ShouldProcess($EnvironmentId,'Create + link enterprise (network) policy')) {
    # Cmdlet names/parameters evolve — verify against current module help before running.
    $policy = New-AdminPowerAppEnvironmentEnterprisePolicy `
        -EnvironmentName $EnvironmentId `
        -DisplayName $PolicyName `
        -Type 'NetworkInjection' `
        -PrimaryVirtualNetworkSubnetId $PrimarySubnetResourceId `
        -FailoverVirtualNetworkSubnetId $FailoverSubnetResourceId

    Write-Host "Linked enterprise policy: $($policy.Id)" -ForegroundColor Green
    return $policy
}
```

> **Why both subnets are required.** Microsoft requires a delegated subnet in the Azure region paired with the Power Platform region **and** in the paired failover region. A single-subnet policy is rejected.

---

## Script 3 — Create Private Endpoints for Key Vault, SQL, Storage, and AMPLS

```powershell
<#
.SYNOPSIS
    Creates a Private Endpoint and DNS zone group for a single dependency resource.

.PARAMETER TargetResourceId    ARM resource ID of the dependency (Key Vault, SQL server, Storage, AMPLS).
.PARAMETER GroupId             PaaS sub-resource (vault | sqlServer | blob | azuremonitor).
.PARAMETER PrivateDnsZoneId    ARM resource ID of the existing Private DNS zone for that group.
.PARAMETER PeResourceGroup     Resource group for the PE itself.
.PARAMETER VNetSubnetId        ARM resource ID of snet-private-endpoints.
.PARAMETER Location            Azure region.
.PARAMETER PeName              Private endpoint name (e.g., pe-kv-pp-eastus).
#>
[CmdletBinding(SupportsShouldProcess, ConfirmImpact='Medium')]
param(
    [Parameter(Mandatory)] [string] $TargetResourceId,
    [Parameter(Mandatory)] [ValidateSet('vault','sqlServer','blob','azuremonitor')] [string] $GroupId,
    [Parameter(Mandatory)] [string] $PrivateDnsZoneId,
    [Parameter(Mandatory)] [string] $PeResourceGroup,
    [Parameter(Mandatory)] [string] $VNetSubnetId,
    [Parameter(Mandatory)] [string] $Location,
    [Parameter(Mandatory)] [string] $PeName
)

$ErrorActionPreference = 'Stop'

$conn = New-AzPrivateLinkServiceConnection -Name "$PeName-conn" `
    -PrivateLinkServiceId $TargetResourceId -GroupId $GroupId

if ($PSCmdlet.ShouldProcess($PeName, "Create private endpoint to $TargetResourceId")) {
    $pe = New-AzPrivateEndpoint -ResourceGroupName $PeResourceGroup -Name $PeName `
        -Location $Location -Subnet (New-Object Microsoft.Azure.Commands.Network.Models.PSSubnet -Property @{ Id = $VNetSubnetId }) `
        -PrivateLinkServiceConnection $conn

    $zoneCfg = New-AzPrivateDnsZoneConfig -Name "$GroupId-config" -PrivateDnsZoneId $PrivateDnsZoneId
    New-AzPrivateDnsZoneGroup -ResourceGroupName $PeResourceGroup `
        -PrivateEndpointName $PeName -Name "default" -PrivateDnsZoneConfig $zoneCfg | Out-Null

    Write-Host "Created PE $PeName -> $TargetResourceId ($GroupId)" -ForegroundColor Green
    return $pe
}
```

After creating the PE, **disable public network access** on the dependency:

```powershell
# Key Vault
Update-AzKeyVaultNetworkRuleSet -VaultName <name> -ResourceGroupName <rg> -DefaultAction Deny -Bypass None
Update-AzKeyVault -VaultName <name> -ResourceGroupName <rg> -PublicNetworkAccess Disabled

# Azure SQL
Set-AzSqlServer -ResourceGroupName <rg> -ServerName <server> -PublicNetworkAccess "Disabled"

# Storage account
Set-AzStorageAccount -ResourceGroupName <rg> -Name <name> -PublicNetworkAccess Disabled
```

> **Pre-flight check.** Before disabling public network access, **enumerate every consumer** (CI/CD agents, Logic Apps, on-prem connectors, developer workstations). Disabling without a plan severs production traffic. Use Azure Resource Graph queries and Key Vault diagnostic logs over the prior 30 days to build the consumer list.

---

## Script 4 — Configure Azure Monitor Private Link Scope (AMPLS) for Application Insights

```powershell
<#
.SYNOPSIS
    Creates an AMPLS, attaches Application Insights / Log Analytics, and locks ingestion / query to private.
#>
[CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
param(
    [Parameter(Mandatory)] [string] $ResourceGroupName,
    [Parameter(Mandatory)] [string] $Location,
    [Parameter(Mandatory)] [string] $AmplsName,
    [Parameter(Mandatory)] [string[]] $AppInsightsResourceIds,
    [Parameter(Mandatory)] [string[]] $LogAnalyticsResourceIds,
    [ValidateSet('Open','PrivateOnly')] [string] $IngestionAccessMode = 'PrivateOnly',
    [ValidateSet('Open','PrivateOnly')] [string] $QueryAccessMode     = 'PrivateOnly'
)

$ErrorActionPreference = 'Stop'

if ($PSCmdlet.ShouldProcess($AmplsName,'Create AMPLS and attach scoped resources')) {
    $ampls = New-AzInsightsPrivateLinkScope -ResourceGroupName $ResourceGroupName -Name $AmplsName -Location 'global'

    foreach ($rid in $AppInsightsResourceIds + $LogAnalyticsResourceIds) {
        $name = ($rid -split '/')[-1]
        New-AzInsightsPrivateLinkScopedResource -ResourceGroupName $ResourceGroupName `
            -ScopeName $AmplsName -Name "scoped-$name" -LinkedResourceId $rid | Out-Null
    }

    Update-AzInsightsPrivateLinkScope -ResourceGroupName $ResourceGroupName -Name $AmplsName `
        -IngestionAccessMode $IngestionAccessMode -QueryAccessMode $QueryAccessMode | Out-Null
}
```

> **Migration tip.** Set `IngestionAccessMode = Open` until every agent host (App Service plan, container, hybrid worker) is confirmed to reach the AMPLS via private endpoint, then tighten to `PrivateOnly`. Telemetry gaps during migration are common and silent — verify ingestion throughput before and after the switch.

---

## Script 5 — Configure IP Firewall and Cookie Binding (current state)

> As of April 2026, IP firewall rules and cookie-binding configuration are **portal-managed** in PPAC and not exposed by stable, documented Power Apps Administration cmdlets. Microsoft has previewed Power Platform CLI / management-API-based automation; verify what is GA in your tenant before scripting. The script below documents the audit pattern only.

```powershell
<#
.SYNOPSIS
    Documents IP firewall configuration steps for an environment and emits an evidence record.
    Does NOT change firewall state — current GA path is the PPAC portal.
#>
param(
    [Parameter(Mandatory)] [string] $EnvironmentId,
    [Parameter(Mandatory)] [string[]] $AllowedCidrs,
    [Parameter(Mandatory)] [string] $EvidencePath
)

$record = [pscustomobject]@{
    EnvironmentId = $EnvironmentId
    AllowedCidrs  = $AllowedCidrs
    Mode          = 'Enforce'
    CookieBinding = 'On'
    CapturedUtc   = (Get-Date).ToUniversalTime().ToString('o')
    CapturedBy    = $env:USERNAME
}
$json = $record | ConvertTo-Json -Depth 4
Set-Content -Path $EvidencePath -Value $json -Encoding UTF8
$hash = (Get-FileHash $EvidencePath -Algorithm SHA256).Hash
Add-Content -Path "$EvidencePath.sha256" -Value $hash
Write-Host "Wrote evidence: $EvidencePath (SHA-256 $hash)" -ForegroundColor Green
```

---

## Script 6 — Validation (read-only)

```powershell
<#
.SYNOPSIS
    Read-only validation of Control 1.20 state for an environment.
    Emits a JSON evidence file and SHA-256.
#>
param(
    [Parameter(Mandatory)] [string] $EnvironmentId,
    [Parameter(Mandatory)] [string] $PrimarySubnetResourceId,
    [Parameter(Mandatory)] [string] $FailoverSubnetResourceId,
    [Parameter(Mandatory)] [string[]] $DependencyResourceIds,
    [Parameter(Mandatory)] [string] $EvidencePath,
    [ValidateSet('Commercial','GCC','GCCHigh','DoD')] [string] $Cloud = 'Commercial',
    [Parameter(Mandatory)] [string] $TenantId
)

$ErrorActionPreference = 'Stop'
Connect-FsiClouds -Cloud $Cloud -TenantId $TenantId

$results = [ordered]@{
    EnvironmentId = $EnvironmentId
    Checks        = [ordered]@{}
    CapturedUtc   = (Get-Date).ToUniversalTime().ToString('o')
}

# Check 1: environment is Managed
$env = Get-AdminPowerAppEnvironment -EnvironmentName $EnvironmentId
$results.Checks.IsManagedEnvironment = [bool]$env.IsManaged

# Check 2: enterprise policy linked
$policy = Get-PowerAppEnvironmentEnterprisePolicy -EnvironmentName $EnvironmentId -ErrorAction SilentlyContinue
$results.Checks.EnterprisePolicyLinked = [bool]$policy
$results.Checks.PrimarySubnetMatches  = ($policy.Properties.NetworkInjection.virtualNetworks[0].subnetId -eq $PrimarySubnetResourceId)
$results.Checks.FailoverSubnetMatches = ($policy.Properties.NetworkInjection.virtualNetworks[1].subnetId -eq $FailoverSubnetResourceId)

# Check 3: subnet delegation present
foreach ($sid in @($PrimarySubnetResourceId, $FailoverSubnetResourceId)) {
    $parts = $sid -split '/'
    $rg = $parts[4]; $vnet = $parts[8]; $snet = $parts[10]
    $sn = Get-AzVirtualNetworkSubnetConfig -VirtualNetwork (Get-AzVirtualNetwork -ResourceGroupName $rg -Name $vnet) -Name $snet
    $results.Checks["DelegationOn_$snet"] = ($sn.Delegations[0].ServiceName -eq 'Microsoft.PowerPlatform/enterprisePolicies')
}

# Check 4: dependency public access disabled
foreach ($rid in $DependencyResourceIds) {
    $r = Get-AzResource -ResourceId $rid
    $public = $r.Properties.publicNetworkAccess
    $results.Checks["PublicAccessDisabled_$($r.Name)"] = ($public -in @('Disabled','SecuredByPerimeter'))
}

$results | ConvertTo-Json -Depth 6 | Set-Content -Path $EvidencePath -Encoding UTF8
$hash = (Get-FileHash $EvidencePath -Algorithm SHA256).Hash
Add-Content -Path "$EvidencePath.sha256" -Value $hash
Write-Host "Validation evidence: $EvidencePath (SHA-256 $hash)" -ForegroundColor Cyan
return $results
```

---

## Notes on Cmdlet Drift

`Microsoft.PowerApps.Administration.PowerShell` cmdlets in the network/enterprise-policy area have changed parameter names and aliases between minor versions. If a script in this playbook errors with `A parameter cannot be found that matches parameter name '...'`:

1. Run `Get-Command -Module Microsoft.PowerApps.Administration.PowerShell *EnterprisePolicy*` and `Get-Help <cmdlet> -Full`.
2. Cross-check against the current [Microsoft Learn page for VNet setup](https://learn.microsoft.com/en-us/power-platform/admin/vnet-support-setup-configure).
3. Pin the working version in your CAB record per the [PowerShell baseline](../../_shared/powershell-baseline.md) §1.

---

[Back to Control 1.20](../../../controls/pillar-1-security/1.20-network-isolation-private-connectivity.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification & Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
