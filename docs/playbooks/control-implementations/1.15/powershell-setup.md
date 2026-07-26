# PowerShell Setup: Control 1.15 — Encryption: Data in Transit and at Rest

!!! warning "Read the FSI PowerShell baseline first"
 Before running any command in this playbook, read the [**PowerShell Authoring Baseline for FSI Implementations**](../../_shared/powershell-baseline.md). It is the canonical source for module version pinning mutation safety (`-WhatIf` / `SupportsShouldProcess`), and SHA-256 evidence emission. Snippets below show the encryption-specific patterns; the baseline is authoritative for the rest.

!!! danger "Customer Key revocation is permanent and destroys data by design"
    Several cmdlets in this playbook (`Set-DataEncryptionPolicy -Refresh`, `Remove-DataEncryptionPolicy`, anything that disables or deletes a vault key under an active DEP) sit on the **data-purge path**. Once you initiate revocation and the purge window completes, Microsoft cannot recover the affected data — by design. Always run with `-WhatIf` first, snapshot before-state, and require dual approval. Revocation belongs to a documented break-glass runbook, not a routine operations script.

**Last Updated:** July 2026
**Modules Required:** `Az.Accounts`, `Az.KeyVault`, `ExchangeOnlineManagement`, `Microsoft.Online.SharePoint.PowerShell`, `Microsoft.Graph` (for service principal lookup)
**PowerShell Edition:** PowerShell 7.4 LTS for Az and Graph modules; **Windows PowerShell 5.1** for `Microsoft.Online.SharePoint.PowerShell`

---

## Prerequisites

```powershell
# Pin versions per the FSI PowerShell baseline; replace <version> with your CAB-approved value.
Install-Module Az.Accounts                          -RequiredVersion '<version>' -Repository PSGallery -Scope CurrentUser -AllowClobber -AcceptLicense
Install-Module Az.KeyVault                          -RequiredVersion '<version>' -Repository PSGallery -Scope CurrentUser -AllowClobber -AcceptLicense
Install-Module ExchangeOnlineManagement             -RequiredVersion '<version>' -Repository PSGallery -Scope CurrentUser -AllowClobber -AcceptLicense
Install-Module Microsoft.Online.SharePoint.PowerShell -RequiredVersion '<version>' -Repository PSGallery -Scope CurrentUser -AllowClobber -AcceptLicense
Install-Module Microsoft.Graph                      -RequiredVersion '<version>' -Repository PSGallery -Scope CurrentUser -AllowClobber -AcceptLicense
```

---

## 1. Provision and Harden the Customer Key Vaults

```powershell
<#
.SYNOPSIS
    Idempotently provisions an Azure Key Vault hardened for Microsoft 365 Customer Key.

.DESCRIPTION
    - Premium SKU + RSA-HSM key for Zone 3, Standard for Zone 2.
    - Soft delete retention 90 days, purge protection ENABLED (irreversible).
    - Adds the M365 workload service principal with Get/WrapKey/UnwrapKey only.
    - Emits before/after JSON evidence with SHA-256 hash.

.PARAMETER WorkloadPrincipalName
    'Office 365 Exchange Online' or 'Office 365 SharePoint Online'.

.EXAMPLE
    .\New-FsiCustomerKeyVault.ps1 `
        -SubscriptionId <sub> `
        -ResourceGroup rg-fsi-customerkey `
        -VaultName kv-fsi-ck-eo-pri-eastus `
        -Location eastus `
        -Sku Premium `
        -KeyName m365-ck-key `
        -KeyType RSA-HSM `
        -KeySize 3072 `
        -WorkloadPrincipalName 'Office 365 Exchange Online' `
        -EvidencePath .\evidence -WhatIf
#>
[CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
param(
    [Parameter(Mandatory)] [string] $SubscriptionId,
    [Parameter(Mandatory)] [string] $ResourceGroup,
    [Parameter(Mandatory)] [string] $VaultName,
    [Parameter(Mandatory)] [string] $Location,
    [ValidateSet('Standard','Premium')] [string] $Sku = 'Premium',
    [Parameter(Mandatory)] [string] $KeyName,
    [ValidateSet('RSA','RSA-HSM')] [string] $KeyType = 'RSA-HSM',
    [ValidateSet(2048,3072,4096)] [int] $KeySize = 3072,
    [Parameter(Mandatory)] [ValidateSet('Office 365 Exchange Online','Office 365 SharePoint Online')]
    [string] $WorkloadPrincipalName,
    [string] $EvidencePath = '.\evidence'
)

$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force -Path $EvidencePath | Out-Null
$ts = Get-Date -Format 'yyyyMMddTHHmmssZ'
Start-Transcript -Path "$EvidencePath\customerkey-vault-$VaultName-$ts.log" -IncludeInvocationHeader

Connect-AzAccount -SubscriptionId $SubscriptionId | Out-Null
Set-AzContext -SubscriptionId $SubscriptionId | Out-Null

# Idempotency: get existing vault if present
$vault = Get-AzKeyVault -VaultName $VaultName -ResourceGroupName $ResourceGroup -ErrorAction SilentlyContinue
$beforeSnapshot = if ($vault) { $vault | ConvertTo-Json -Depth 8 } else { '{}' }
$beforeSnapshot | Set-Content "$EvidencePath\before-$VaultName-$ts.json"

if (-not $vault) {
    if ($PSCmdlet.ShouldProcess($VaultName, "Create Key Vault $Sku in $Location with purge protection")) {
        # -EnableSoftDelete is not a valid parameter in Az.KeyVault 3.x+; soft delete is always enabled by default.
        $vault = New-AzKeyVault `
            -Name $VaultName `
            -ResourceGroupName $ResourceGroup `
            -Location $Location `
            -Sku $Sku `
            -SoftDeleteRetentionInDays 90 `
            -EnablePurgeProtection
    }
} else {
    Write-Verbose "Vault $VaultName already exists; verifying hardening flags."
    if (-not $vault.EnableSoftDelete -or -not $vault.EnablePurgeProtection) {
        if ($PSCmdlet.ShouldProcess($VaultName, "Enable purge protection (irreversible)")) {
            Update-AzKeyVault -VaultName $VaultName -ResourceGroupName $ResourceGroup -EnablePurgeProtection
        }
    }
}

# Create the wrapping key (idempotent: skip if exists)
$key = Get-AzKeyVaultKey -VaultName $VaultName -Name $KeyName -ErrorAction SilentlyContinue
if (-not $key) {
    if ($PSCmdlet.ShouldProcess("$VaultName/$KeyName", "Create $KeyType $KeySize-bit key")) {
        $key = Add-AzKeyVaultKey -VaultName $VaultName -Name $KeyName -Destination ($KeyType -replace 'RSA-HSM','HSM' -replace 'RSA','Software') -Size $KeySize
    }
}

# Resolve the workload service principal (object id varies per tenant)
$sp = Get-AzADServicePrincipal -DisplayName $WorkloadPrincipalName | Select-Object -First 1
if (-not $sp) {
    throw "Service principal '$WorkloadPrincipalName' not found. Confirm the workload is provisioned in this tenant."
}

if ($PSCmdlet.ShouldProcess($VaultName, "Grant '$WorkloadPrincipalName' Get/WrapKey/UnwrapKey")) {
    Set-AzKeyVaultAccessPolicy `
        -VaultName $VaultName `
        -ObjectId $sp.Id `
        -PermissionsToKeys Get,WrapKey,UnwrapKey
}

# After-state evidence with SHA-256
$after = @{
    vault = (Get-AzKeyVault -VaultName $VaultName -ResourceGroupName $ResourceGroup)
    key   = (Get-AzKeyVaultKey -VaultName $VaultName -Name $KeyName)
    grantedPrincipal = @{ DisplayName = $sp.DisplayName; ObjectId = $sp.Id }
}
$jsonPath = "$EvidencePath\after-$VaultName-$ts.json"
$after | ConvertTo-Json -Depth 10 | Set-Content $jsonPath
$hash = (Get-FileHash $jsonPath -Algorithm SHA256).Hash

[PSCustomObject]@{
    file = (Split-Path $jsonPath -Leaf)
    sha256 = $hash
    bytes = (Get-Item $jsonPath).Length
    generated_utc = $ts
    control = '1.15'
    operation = 'provision-customer-key-vault'
} | ConvertTo-Json | Add-Content "$EvidencePath\manifest.jsonl"

Stop-Transcript
```

Run twice (primary region + secondary region) **before** activating the DEP.

---

## 2. Exchange Online Customer Key Activation

```powershell
<#
.SYNOPSIS
    Creates and assigns the multi-workload (Exchange Online) Customer Key DEP.

.DESCRIPTION
    Use only AFTER both Key Vaults are provisioned and the Office 365 Exchange Online
    service principal has Get/WrapKey/UnwrapKey on the keys.

.EXAMPLE
    .\Enable-FsiExchangeCustomerKey.ps1 `
        -DepName 'FSI-EO-Root-DEP' `
        -PrimaryKeyUri 'https://kv-fsi-ck-eo-pri-eastus.vault.azure.net/keys/m365-ck-key/<ver>' `
        -SecondaryKeyUri 'https://kv-fsi-ck-eo-sec-westus.vault.azure.net/keys/m365-ck-key/<ver>' `
        -EvidencePath .\evidence -WhatIf
#>
[CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
param(
    [Parameter(Mandatory)] [string] $DepName,
    [Parameter(Mandatory)] [string] $PrimaryKeyUri,
    [Parameter(Mandatory)] [string] $SecondaryKeyUri,
    [string] $Description = 'FSI Customer Key DEP for Exchange Online — agent-bearing mailboxes',
    [string] $EvidencePath = '.\evidence'
)

$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force -Path $EvidencePath | Out-Null
$ts = Get-Date -Format 'yyyyMMddTHHmmssZ'
Start-Transcript -Path "$EvidencePath\eo-customerkey-$DepName-$ts.log" -IncludeInvocationHeader

Connect-ExchangeOnline -ShowBanner:$false

# Idempotency: skip if a DEP with this name already exists
$existing = Get-M365DataAtRestEncryptionPolicy -Identity $DepName -ErrorAction SilentlyContinue
if ($existing) {
    Write-Warning "DEP $DepName already exists in state '$($existing.PolicyState)'. Aborting create; use Set-/Refresh- pattern for updates."
    $existing | ConvertTo-Json -Depth 6 | Set-Content "$EvidencePath\existing-$DepName-$ts.json"
} elseif ($PSCmdlet.ShouldProcess($DepName, "Create M365 Data-at-Rest DEP for Exchange Online")) {
    New-M365DataAtRestEncryptionPolicy `
        -Name $DepName `
        -AzureKeyIDs @($PrimaryKeyUri, $SecondaryKeyUri) `
        -Description $Description | Out-Null
}

if ($PSCmdlet.ShouldProcess('Tenant', "Assign DEP $DepName tenant-wide")) {
    Set-M365DataAtRestEncryptionPolicyAssignment -DataEncryptionPolicy $DepName
}

# Capture state for evidence
$state = Get-M365DataAtRestEncryptionPolicy -Identity $DepName
$jsonPath = "$EvidencePath\state-$DepName-$ts.json"
$state | ConvertTo-Json -Depth 8 | Set-Content $jsonPath

[PSCustomObject]@{
    file = (Split-Path $jsonPath -Leaf)
    sha256 = (Get-FileHash $jsonPath -Algorithm SHA256).Hash
    bytes = (Get-Item $jsonPath).Length
    generated_utc = $ts
    control = '1.15'
    operation = 'activate-eo-customer-key'
    initial_state = $state.PolicyState
} | ConvertTo-Json | Add-Content "$EvidencePath\manifest.jsonl"

Disconnect-ExchangeOnline -Confirm:$false
Stop-Transcript

Write-Host "Activation initiated. Re-check state with: Get-M365DataAtRestEncryptionPolicy -Identity $DepName" -ForegroundColor Cyan
Write-Host "Expected progression: PendingActivation -> Active (minutes to ~24h)." -ForegroundColor Cyan
```

---

## 3. SharePoint Online / OneDrive Customer Key Activation

`Microsoft.Online.SharePoint.PowerShell` is **Windows PowerShell 5.1 only**.

```powershell
<#
.SYNOPSIS
    Registers the SharePoint/OneDrive Customer Key (tenant-wide).

.DESCRIPTION
    Tenant-wide one-shot registration. Cannot be re-run while activation is in progress.

.EXAMPLE
    .\Enable-FsiSpoCustomerKey.ps1 `
        -TenantAdminUrl 'https://contoso-admin.sharepoint.com' `
        -PrimaryVault kv-fsi-ck-spo-pri-eastus -PrimaryKey m365-ck-key -PrimaryKeyVersion <ver> `
        -SecondaryVault kv-fsi-ck-spo-sec-westus -SecondaryKey m365-ck-key -SecondaryKeyVersion <ver> `
        -EvidencePath .\evidence -WhatIf
#>
[CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
param(
    [Parameter(Mandatory)] [string] $TenantAdminUrl,
    [Parameter(Mandatory)] [string] $PrimaryVault,
    [Parameter(Mandatory)] [string] $PrimaryKey,
    [Parameter(Mandatory)] [string] $PrimaryKeyVersion,
    [Parameter(Mandatory)] [string] $SecondaryVault,
    [Parameter(Mandatory)] [string] $SecondaryKey,
    [Parameter(Mandatory)] [string] $SecondaryKeyVersion,
    [string] $EvidencePath = '.\evidence'
)

if ($PSVersionTable.PSEdition -ne 'Desktop') {
    throw "Microsoft.Online.SharePoint.PowerShell requires Windows PowerShell 5.1 (Desktop edition). Detected: $($PSVersionTable.PSEdition) $($PSVersionTable.PSVersion)."
}

$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force -Path $EvidencePath | Out-Null
$ts = Get-Date -Format 'yyyyMMddTHHmmssZ'
Start-Transcript -Path "$EvidencePath\spo-customerkey-$ts.log" -IncludeInvocationHeader

Connect-SPOService -Url $TenantAdminUrl

# Idempotency: bail out if a DEP is already registered or activation is in flight
$existing = Get-SPODataEncryptionPolicy -ErrorAction SilentlyContinue
if ($existing -and $existing.State -ne 'Unregistered') {
    Write-Warning "SPO Customer Key already in state '$($existing.State)'. Aborting register; rotation is a different operation."
    $existing | ConvertTo-Json | Set-Content "$EvidencePath\spo-existing-$ts.json"
    Disconnect-SPOService
    Stop-Transcript
    return
}

if ($PSCmdlet.ShouldProcess($TenantAdminUrl, "Register SPO Customer Key (tenant-wide, irreversible without revocation)")) {
    Register-SPODataEncryptionPolicy `
        -PrimaryKeyVaultName $PrimaryVault -PrimaryKeyName $PrimaryKey -PrimaryKeyVersion $PrimaryKeyVersion `
        -SecondaryKeyVaultName $SecondaryVault -SecondaryKeyName $SecondaryKey -SecondaryKeyVersion $SecondaryKeyVersion
}

$state = Get-SPODataEncryptionPolicy
$jsonPath = "$EvidencePath\spo-state-$ts.json"
$state | ConvertTo-Json -Depth 8 | Set-Content $jsonPath

[PSCustomObject]@{
    file = (Split-Path $jsonPath -Leaf)
    sha256 = (Get-FileHash $jsonPath -Algorithm SHA256).Hash
    generated_utc = $ts
    control = '1.15'
    operation = 'register-spo-customer-key'
} | ConvertTo-Json | Add-Content "$EvidencePath\manifest.jsonl"

Disconnect-SPOService
Stop-Transcript
```

---

## 4. TLS Posture Audit Across Tenant Endpoints

```powershell
<#
.SYNOPSIS
    Probes a list of public tenant endpoints and reports the negotiated TLS version + cipher.

.DESCRIPTION
    Uses .NET SslStream to attempt handshakes at TLS 1.0, 1.1, 1.2, 1.3 and reports each result.
    Read-only — no mutation. Safe to run in production.
#>
param(
    [Parameter(Mandatory)] [string[]] $Endpoints,
    [string] $EvidencePath = '.\evidence'
)

$ErrorActionPreference = 'Continue'
New-Item -ItemType Directory -Force -Path $EvidencePath | Out-Null
$ts = Get-Date -Format 'yyyyMMddTHHmmssZ'

$protocols = @(
    @{ Name='Tls10'; Value=[System.Security.Authentication.SslProtocols]::Tls   }
    @{ Name='Tls11'; Value=[System.Security.Authentication.SslProtocols]::Tls11 }
    @{ Name='Tls12'; Value=[System.Security.Authentication.SslProtocols]::Tls12 }
    @{ Name='Tls13'; Value=[System.Security.Authentication.SslProtocols]::Tls13 }
)

$results = foreach ($endpoint in $Endpoints) {
    foreach ($p in $protocols) {
        $client = New-Object System.Net.Sockets.TcpClient
        $row = [ordered]@{ Endpoint=$endpoint; Protocol=$p.Name; Negotiated=$false; Cipher=$null; Error=$null }
        try {
            $client.Connect($endpoint, 443)
            $stream = New-Object System.Net.Security.SslStream($client.GetStream(), $false, { param($s,$c,$ch,$e) $true })
            $stream.AuthenticateAsClient($endpoint, $null, $p.Value, $false)
            $row.Negotiated = $true
            $row.Cipher = "$($stream.CipherAlgorithm)/$($stream.HashAlgorithm) $($stream.SslProtocol)"
        } catch {
            $row.Error = $_.Exception.Message
        } finally {
            $client.Close()
        }
        [PSCustomObject]$row
    }
}

$jsonPath = "$EvidencePath\tls-posture-$ts.json"
$results | ConvertTo-Json -Depth 4 | Set-Content $jsonPath

# Flag any endpoint where TLS 1.0 or 1.1 negotiated successfully
$weak = $results | Where-Object { $_.Negotiated -and $_.Protocol -in 'Tls10','Tls11' }
if ($weak) {
    Write-Warning "Weak TLS negotiated on $($weak.Count) endpoint/protocol combinations."
    $weak | Format-Table Endpoint,Protocol,Cipher
} else {
    Write-Host "[PASS] No TLS 1.0/1.1 negotiation succeeded on any tested endpoint." -ForegroundColor Green
}

[PSCustomObject]@{
    file = (Split-Path $jsonPath -Leaf)
    sha256 = (Get-FileHash $jsonPath -Algorithm SHA256).Hash
    generated_utc = $ts
    control = '1.15'
    operation = 'tls-posture-audit'
    weak_findings = $weak.Count
} | ConvertTo-Json | Add-Content "$EvidencePath\manifest.jsonl"
```

---

## 5. Key Rotation (Routine — Non-Destructive)

Routine rotation creates a **new key version** in the existing Key Vault key. Customer Key automatically uses the latest enabled version on the next wrap.

```powershell
<#
.SYNOPSIS
    Creates a new version of an existing Customer Key wrapping key.

.DESCRIPTION
    SAFE rotation: new version, both old and new versions remain enabled until Microsoft
    confirms wrap on the new version. Does NOT delete or disable the previous version.

.EXAMPLE
    .\Invoke-FsiKeyRotation.ps1 -VaultName kv-fsi-ck-eo-pri-eastus -KeyName m365-ck-key -EvidencePath .\evidence -WhatIf
#>
[CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
param(
    [Parameter(Mandatory)] [string] $VaultName,
    [Parameter(Mandatory)] [string] $KeyName,
    [string] $EvidencePath = '.\evidence'
)

$ErrorActionPreference = 'Stop'
$ts = Get-Date -Format 'yyyyMMddTHHmmssZ'
New-Item -ItemType Directory -Force -Path $EvidencePath | Out-Null
Start-Transcript -Path "$EvidencePath\rotate-$VaultName-$KeyName-$ts.log" -IncludeInvocationHeader

$beforeVersions = Get-AzKeyVaultKey -VaultName $VaultName -Name $KeyName -IncludeVersions
$beforeVersions | ConvertTo-Json -Depth 5 | Set-Content "$EvidencePath\rotate-before-$ts.json"

if ($PSCmdlet.ShouldProcess("$VaultName/$KeyName", "Create new key version")) {
    $new = Add-AzKeyVaultKey -VaultName $VaultName -Name $KeyName -Destination HSM
    Write-Host "New version created: $($new.Version)" -ForegroundColor Green
}

$after = Get-AzKeyVaultKey -VaultName $VaultName -Name $KeyName -IncludeVersions
$after | ConvertTo-Json -Depth 5 | Set-Content "$EvidencePath\rotate-after-$ts.json"

Stop-Transcript

Write-Host "Do NOT disable the previous version until Microsoft confirms wrap on the new version." -ForegroundColor Yellow
Write-Host "Verify with: (Get-DataEncryptionPolicy <name>).PrimaryKeyVaultUri  -- should reflect new version after wrap." -ForegroundColor Yellow
```

---

## 6. Customer Key Revocation — Break-Glass Only

!!! danger "This is a destructive break-glass procedure"
    The script below is **deliberately not provided**. Customer Key revocation triggers an irreversible data-purge path. Microsoft cannot recover data after the purge window completes. Revocation must follow your CISO-approved break-glass runbook with named dual-control approvers; it is not a routine PowerShell operation. Your runbook should:

    - Require explicit CISO + Records Officer + Legal sign-off (recorded in your change-management system)
    - Be rehearsed in a non-production tenant first
    - Document the data-purge timeline and the workloads it affects
    - Confirm there is no business-continuity expectation for the data being purged
    - Use Microsoft Support for the actual cmdlet sequence (`Set-DataEncryptionPolicy -Refresh`, key disable/delete, support ticket gating)

    Refer to Microsoft Learn: [Manage Customer Key — revoke and start the data purge path](https://learn.microsoft.com/en-us/purview/customer-key-manage).

---

## 7. End-to-End Validation

```powershell
<#
.SYNOPSIS
    Read-only validation of all configured Customer Key DEPs and vault hardening.
#>
param([string] $EvidencePath = '.\evidence')

$ErrorActionPreference = 'Continue'
$ts = Get-Date -Format 'yyyyMMddTHHmmssZ'
New-Item -ItemType Directory -Force -Path $EvidencePath | Out-Null

Write-Host "=== Control 1.15 — Customer Key Validation ===" -ForegroundColor Cyan

Connect-ExchangeOnline -ShowBanner:$false
$eoDeps = Get-M365DataAtRestEncryptionPolicy -ErrorAction SilentlyContinue
$workloadDeps = Get-DataEncryptionPolicy -ErrorAction SilentlyContinue

foreach ($d in @($eoDeps + $workloadDeps | Where-Object { $_ })) {
    $marker = if ($d.PolicyState -eq 'Active' -or $d.State -eq 'Active') { 'PASS' } else { 'INVESTIGATE' }
    $color  = if ($marker -eq 'PASS') { 'Green' } else { 'Yellow' }
    $state  = if ($d.PolicyState) { $d.PolicyState } else { $d.State }
    Write-Host ("[{0}] DEP '{1}' state={2}" -f $marker, $d.Name, $state) -ForegroundColor $color
}

Disconnect-ExchangeOnline -Confirm:$false

# Vault hardening
$vaults = Get-AzKeyVault | Where-Object { $_.VaultName -like 'kv-*ck*' }
foreach ($v in $vaults) {
    $detail = Get-AzKeyVault -VaultName $v.VaultName -ResourceGroupName $v.ResourceGroupName
    $sd = $detail.EnableSoftDelete
    $pp = $detail.EnablePurgeProtection
    $marker = if ($sd -and $pp) { 'PASS' } else { 'FAIL' }
    Write-Host ("[{0}] Vault '{1}' soft-delete={2} purge-protection={3}" -f $marker, $v.VaultName, $sd, $pp) -ForegroundColor (if ($marker -eq 'PASS') { 'Green' } else { 'Red' })
}

# Emit evidence
$report = @{
    eo_deps        = $eoDeps
    workload_deps  = $workloadDeps
    vaults         = $vaults | ForEach-Object { Get-AzKeyVault -VaultName $_.VaultName -ResourceGroupName $_.ResourceGroupName }
    timestamp_utc  = $ts
}
$jsonPath = "$EvidencePath\validate-control-1.15-$ts.json"
$report | ConvertTo-Json -Depth 8 | Set-Content $jsonPath

[PSCustomObject]@{
    file = (Split-Path $jsonPath -Leaf)
    sha256 = (Get-FileHash $jsonPath -Algorithm SHA256).Hash
    generated_utc = $ts
    control = '1.15'
    operation = 'validate'
} | ConvertTo-Json | Add-Content "$EvidencePath\manifest.jsonl"
```

---

[Back to Control 1.15](../../../controls/pillar-1-security/1.15-encryption-data-in-transit-and-at-rest.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
---

*Updated: July 2026 | Version: v1.6.2 | UI Verification Status: Current*
