# PowerShell Setup: Control 1.17 - Endpoint Data Loss Prevention

**Last Updated:** January 2026
**Modules Required:** ExchangeOnlineManagement (for compliance cmdlets)

## Prerequisites

```powershell
# Install required modules
Install-Module -Name ExchangeOnlineManagement -Force -Scope CurrentUser
```

---

## Automated Scripts

### Get Endpoint DLP Device Status

```powershell
<#
.SYNOPSIS
    Reports on devices onboarded to Endpoint DLP

.DESCRIPTION
    Lists devices and their DLP health status

.EXAMPLE
    .\Get-EndpointDLPStatus.ps1
#>

Write-Host "=== Endpoint DLP Device Status ===" -ForegroundColor Cyan

# Connect to Security & Compliance
Connect-IPPSSession

# Note: Endpoint DLP device management is primarily through
# the Microsoft Purview portal and Defender portal
# PowerShell access is limited

Write-Host "[INFO] For device status, use:"
Write-Host "  1. Microsoft Purview portal > Endpoint DLP settings"
Write-Host "  2. Microsoft Defender portal > Assets > Devices"
Write-Host ""
Write-Host "PowerShell can manage DLP policies but device"
Write-Host "onboarding status requires portal access."

Disconnect-ExchangeOnline -Confirm:$false
```

### Export DLP Policy Configuration

```powershell
<#
.SYNOPSIS
    Exports DLP policy configuration for compliance review

.EXAMPLE
    .\Export-DLPPolicies.ps1
#>

param(
    [string]$OutputPath = ".\DLPPolicyExport.csv"
)

Write-Host "=== DLP Policy Export ===" -ForegroundColor Cyan

Connect-IPPSSession

# Get all DLP policies
$policies = Get-DlpCompliancePolicy

$export = @()

foreach ($policy in $policies) {
    # Get policy rules
    $rules = Get-DlpComplianceRule -Policy $policy.Name

    foreach ($rule in $rules) {
        $export += [PSCustomObject]@{
            PolicyName = $policy.Name
            PolicyMode = $policy.Mode
            RuleName = $rule.Name
            RulePriority = $rule.Priority
            ContentContains = $rule.ContentContainsSensitiveInformation -join "; "
            Actions = $rule.Actions -join "; "
            Workload = $policy.Workload -join "; "
            Enabled = $policy.Enabled
        }
    }
}

$export | Export-Csv -Path $OutputPath -NoTypeInformation
Write-Host "Export saved to: $OutputPath" -ForegroundColor Green

Disconnect-ExchangeOnline -Confirm:$false
```

### Create Endpoint DLP Policy

```powershell
<#
.SYNOPSIS
    Creates Endpoint DLP policy for financial data protection

.EXAMPLE
    .\New-EndpointDLPPolicy.ps1 -PolicyName "FSI-Endpoint-Tier3"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$PolicyName,
    [string]$Mode = "TestWithNotifications"
)

Write-Host "=== Create Endpoint DLP Policy ===" -ForegroundColor Cyan

Connect-IPPSSession

# Create policy
$policy = New-DlpCompliancePolicy -Name $PolicyName `
    -Mode $Mode `
    -EndpointDlpLocation "All" `
    -Comment "FSI Endpoint DLP policy for sensitive financial data"

Write-Host "Policy created: $PolicyName" -ForegroundColor Green

# Create rule for financial data
$rule = New-DlpComplianceRule -Name "$PolicyName-FinancialData" `
    -Policy $PolicyName `
    -ContentContainsSensitiveInformation @(
        @{Name="U.S. Social Security Number (SSN)"; minCount=1},
        @{Name="Credit Card Number"; minCount=1},
        @{Name="U.S. Bank Account Number"; minCount=1}
    ) `
    -BlockAccess $true `
    -NotifyUser "Owner,LastModifier" `
    -NotifyPolicyTipCustomText "This content contains sensitive financial information and cannot be transferred to this location."

Write-Host "Rule created: $($rule.Name)" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Configure endpoint-specific settings in Purview portal"
Write-Host "2. Test policy in simulation mode"
Write-Host "3. Enable enforcement after validation"

Disconnect-ExchangeOnline -Confirm:$false
```

---

## Validation Script

```powershell
<#
.SYNOPSIS
    Validates Control 1.17 - Endpoint DLP configuration

.EXAMPLE
    .\Validate-Control-1.17.ps1
#>

Write-Host "=== Control 1.17 Validation ===" -ForegroundColor Cyan

Connect-IPPSSession

# Check 1: Endpoint DLP policies exist
Write-Host "`n[Check 1] Endpoint DLP Policies" -ForegroundColor Cyan
$policies = Get-DlpCompliancePolicy | Where-Object { $_.EndpointDlpLocation -ne $null }
if ($policies) {
    Write-Host "[PASS] Endpoint DLP policies found: $($policies.Count)" -ForegroundColor Green
    $policies | ForEach-Object { Write-Host "  - $($_.Name): $($_.Mode)" }
} else {
    Write-Host "[FAIL] No Endpoint DLP policies found" -ForegroundColor Red
}

# Check 2: Policy mode
Write-Host "`n[Check 2] Policy Enforcement Mode" -ForegroundColor Cyan
$enforced = $policies | Where-Object { $_.Mode -eq "Enable" }
Write-Host "Enforced policies: $($enforced.Count)"
Write-Host "Test mode policies: $($policies.Count - $enforced.Count)"

# Check 3: Device onboarding (manual)
Write-Host "`n[Check 3] Device Onboarding" -ForegroundColor Cyan
Write-Host "[INFO] Verify devices in Microsoft Defender portal"
Write-Host "[INFO] Check: Assets > Devices for onboarding status"

Disconnect-ExchangeOnline -Confirm:$false

Write-Host "`n=== Validation Complete ===" -ForegroundColor Cyan
```

---

[Back to Control 1.17](../../../controls/pillar-1-security/1.17-endpoint-data-loss-prevention-endpoint-dlp.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
