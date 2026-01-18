# PowerShell Setup: Control 1.15 - Encryption: Data in Transit and at Rest

**Last Updated:** January 2026
**Modules Required:** Az.KeyVault, ExchangeOnlineManagement

## Prerequisites

```powershell
# Install required modules
Install-Module -Name Az.KeyVault -Force -Scope CurrentUser
Install-Module -Name ExchangeOnlineManagement -Force -Scope CurrentUser
```

---

## Automated Scripts

### Verify Key Vault Configuration

```powershell
<#
.SYNOPSIS
    Validates Azure Key Vault configuration for Customer Key

.DESCRIPTION
    Checks Key Vault settings, permissions, and key status

.EXAMPLE
    .\Test-KeyVaultConfig.ps1 -VaultName "kv-m365-cmk-primary"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$VaultName
)

Write-Host "=== Key Vault Validation ===" -ForegroundColor Cyan

# Connect to Azure
Connect-AzAccount

# Get Key Vault
$vault = Get-AzKeyVault -VaultName $VaultName

if (-not $vault) {
    Write-Host "[FAIL] Key Vault not found: $VaultName" -ForegroundColor Red
    exit 1
}

Write-Host "Key Vault: $($vault.VaultName)" -ForegroundColor Green
Write-Host "Location: $($vault.Location)"
Write-Host "SKU: $($vault.Sku)"

# Check soft delete
if ($vault.EnableSoftDelete) {
    Write-Host "[PASS] Soft delete enabled" -ForegroundColor Green
} else {
    Write-Host "[FAIL] Soft delete not enabled" -ForegroundColor Red
}

# Check purge protection
if ($vault.EnablePurgeProtection) {
    Write-Host "[PASS] Purge protection enabled" -ForegroundColor Green
} else {
    Write-Host "[FAIL] Purge protection not enabled" -ForegroundColor Red
}

# List keys
Write-Host "`nKeys in vault:" -ForegroundColor Cyan
$keys = Get-AzKeyVaultKey -VaultName $VaultName
foreach ($key in $keys) {
    Write-Host "  - $($key.Name): $($key.KeyType) $($key.KeySize)-bit"
    Write-Host "    Enabled: $($key.Enabled)"
    Write-Host "    Created: $($key.Created)"
}
```

### Export Encryption Status Report

```powershell
<#
.SYNOPSIS
    Generates encryption status report for compliance

.DESCRIPTION
    Reports on Customer Key, DEP assignments, and key rotation status

.EXAMPLE
    .\Export-EncryptionReport.ps1
#>

Write-Host "=== Encryption Status Report ===" -ForegroundColor Cyan

# Connect to Exchange Online for Customer Key status
Connect-ExchangeOnline

# Get Data Encryption Policies
Write-Host "`nData Encryption Policies:" -ForegroundColor Cyan
$deps = Get-DataEncryptionPolicy
foreach ($dep in $deps) {
    Write-Host "  DEP: $($dep.Name)"
    Write-Host "    State: $($dep.State)"
    Write-Host "    Created: $($dep.WhenCreated)"
}

# Get mailbox encryption status (sample)
Write-Host "`nSample Mailbox Encryption Status:" -ForegroundColor Cyan
$mailboxes = Get-Mailbox -ResultSize 5
foreach ($mb in $mailboxes) {
    $stats = Get-MailboxStatistics -Identity $mb.Identity
    Write-Host "  $($mb.DisplayName): Encrypted"
}

# Disconnect
Disconnect-ExchangeOnline -Confirm:$false

Write-Host "`n=== Report Complete ===" -ForegroundColor Cyan
```

### Key Rotation Reminder

```powershell
<#
.SYNOPSIS
    Checks key age and sends rotation reminder

.DESCRIPTION
    Validates key age against rotation policy

.EXAMPLE
    .\Test-KeyRotation.ps1 -VaultName "kv-m365-cmk-primary" -MaxAgeDays 90
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$VaultName,
    [int]$MaxAgeDays = 90
)

Write-Host "=== Key Rotation Check ===" -ForegroundColor Cyan

Connect-AzAccount

$keys = Get-AzKeyVaultKey -VaultName $VaultName

foreach ($key in $keys) {
    $keyAge = (Get-Date) - $key.Created
    $daysOld = [math]::Floor($keyAge.TotalDays)

    Write-Host "Key: $($key.Name)"
    Write-Host "  Age: $daysOld days"

    if ($daysOld -gt $MaxAgeDays) {
        Write-Host "  [WARNING] Key exceeds $MaxAgeDays day rotation policy" -ForegroundColor Red
        Write-Host "  Action: Schedule key rotation" -ForegroundColor Yellow
    } else {
        $daysRemaining = $MaxAgeDays - $daysOld
        Write-Host "  [OK] $daysRemaining days until rotation required" -ForegroundColor Green
    }
}
```

---

## Validation Script

```powershell
<#
.SYNOPSIS
    Validates Control 1.15 - Encryption configuration

.EXAMPLE
    .\Validate-Control-1.15.ps1
#>

Write-Host "=== Control 1.15 Validation ===" -ForegroundColor Cyan

# Check 1: TLS Configuration
Write-Host "`n[Check 1] TLS Configuration" -ForegroundColor Cyan
Write-Host "[INFO] Run SSL Labs test manually: https://www.ssllabs.com/ssltest/"
Write-Host "[INFO] Verify Grade A with TLS 1.2+ only"

# Check 2: Key Vault (if using Customer Key)
Write-Host "`n[Check 2] Azure Key Vault" -ForegroundColor Cyan
Write-Host "[INFO] Verify Key Vaults exist in two regions"
Write-Host "[INFO] Verify soft delete and purge protection enabled"

# Check 3: Customer Key Status
Write-Host "`n[Check 3] Customer Key Status" -ForegroundColor Cyan
Write-Host "[INFO] Connect to Exchange Online and run:"
Write-Host "  Get-DataEncryptionPolicy | Format-List Name, State"

# Check 4: Key Rotation
Write-Host "`n[Check 4] Key Rotation Schedule" -ForegroundColor Cyan
Write-Host "[INFO] Verify documented rotation schedule exists"
Write-Host "[INFO] Check last rotation date against policy"

Write-Host "`n=== Validation Complete ===" -ForegroundColor Cyan
```

---

[Back to Control 1.15](../../../controls/pillar-1-security/1.15-encryption-data-in-transit-and-at-rest.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
