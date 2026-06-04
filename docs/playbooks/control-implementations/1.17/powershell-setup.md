# PowerShell Setup: Control 1.17 — Endpoint Data Loss Prevention

!!! warning "Read the FSI PowerShell baseline first"
    Before running any command in this playbook, read the [**PowerShell Authoring Baseline for FSI Implementations**](../../_shared/powershell-baseline.md). It is the canonical source for module version pinning, sovereign-cloud (GCC / GCC High / DoD) endpoints, mutation safety (`-WhatIf` / `SupportsShouldProcess`), Dataverse compatibility, and SHA-256 evidence emission. Snippets below show abbreviated patterns; the baseline is authoritative.

**Last Updated:** May 2026
**Modules Required:** `ExchangeOnlineManagement` (for Security & Compliance PowerShell — `Connect-IPPSSession` and the `*-DlpCompliance*` cmdlet surface)

---

## Scope and Limitations

| Capability | PowerShell Coverage | Notes |
|---|---|---|
| Create / read / update / delete DLP policies and rules | ✅ Full | `New-DlpCompliancePolicy`, `Set-DlpComplianceRule` |
| Set policy mode (Test / Enable / Disable) | ✅ Full | `Set-DlpCompliancePolicy -Mode <value>` |
| Configure rule actions (block, audit, override) | ✅ Full | Via `New-/Set-DlpComplianceRule` parameters |
| Manage Endpoint DLP **global settings** (restricted apps, USB groups, service domains) | ⚠️ Partial / portal-preferred | Cmdlet support is limited and changing; the Purview portal is the supported path |
| Onboard / inventory devices | ❌ None (DLP cmdlets) | Use Defender for Endpoint Graph API or Intune endpoint security policy |
| Edge for Business inline AI DLP toggles | ❌ None (DLP cmdlets) | Portal-only for the location toggle; rule actions configurable via cmdlets once location is enabled |
| Global Secure Access security profiles | ❌ None (DLP cmdlets) | Use Microsoft Graph (`Microsoft.Graph.NetworkAccess`) |

PowerShell is best used to **create policies idempotently, export evidence, and validate state**. UI configuration remains required for global Endpoint DLP settings.

---

## Prerequisites

```powershell
# REQUIRED: Replace <version> with the version approved by your CAB.
# See the PowerShell baseline for the canonical pinning pattern.
Install-Module -Name ExchangeOnlineManagement `
    -RequiredVersion '<version>' `
    -Repository PSGallery `
    -Scope CurrentUser `
    -AllowClobber `
    -AcceptLicense
```

Required role: **Purview Compliance Admin** (canonical) — assigned via Microsoft Purview role groups (`Compliance Administrator` or `Compliance Data Administrator`).

---

## Connection Helper (Sovereign-Cloud Aware)

```powershell
function Connect-FsiCompliance {
    <#
    .SYNOPSIS
        Connects to Security & Compliance PowerShell with sovereign-cloud awareness.
    #>
    [CmdletBinding()]
    param(
        [ValidateSet('Commercial','GCC','GCCHigh','DoD')]
        [string]$Cloud = 'Commercial',

        [Parameter(Mandatory)]
        [string]$UserPrincipalName
    )

    $connectionUri = switch ($Cloud) {
        'Commercial' { 'https://ps.compliance.protection.outlook.com/powershell-liveid/' }
        'GCC'        { 'https://ps.compliance.protection.outlook.com/powershell-liveid/' }
        'GCCHigh'    { 'https://ps.compliance.protection.office365.us/powershell-liveid/' }
        'DoD'        { 'https://l5.ps.compliance.protection.office365.us/powershell-liveid/' }
    }

    try {
        Connect-IPPSSession -UserPrincipalName $UserPrincipalName -ConnectionUri $connectionUri -ErrorAction Stop
        Write-Host "[OK] Connected to Security & Compliance ($Cloud)" -ForegroundColor Green
    }
    catch {
        throw "Failed to connect to Security & Compliance ($Cloud): $($_.Exception.Message)"
    }
}
```

---

## Script 1 — Create or Update the Endpoint DLP Policy (Idempotent)

```powershell
<#
.SYNOPSIS
    Creates or updates an Endpoint DLP policy for FSI financial-data protection.

.DESCRIPTION
    Idempotent: detects existing policy by name and updates rules in place.
    Defaults to TestWithNotifications for safe pilot rollout.
    Supports -WhatIf and -Confirm.

.PARAMETER PolicyName
    Zone-prefixed policy name, e.g. FSI-Z3-Endpoint-FinancialData.

.PARAMETER Zone
    Governance zone: 1 (Personal), 2 (Team), or 3 (Enterprise). Drives action defaults.

.PARAMETER Mode
    Policy mode: TestWithNotifications | TestWithoutNotifications | Enable | Disable.
    Begin with TestWithNotifications; promote to Enable only after pilot validation.

.EXAMPLE
    .\Set-Control117Policy.ps1 -PolicyName 'FSI-Z3-Endpoint-FinancialData' -Zone 3 -Mode 'TestWithNotifications' -WhatIf
#>
[CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
param(
    [Parameter(Mandatory)][string]$PolicyName,
    [Parameter(Mandatory)][ValidateSet(1,2,3)][int]$Zone,
    [ValidateSet('TestWithNotifications','TestWithoutNotifications','Enable','Disable')]
    [string]$Mode = 'TestWithNotifications',
    [string]$ContactEmail = 'compliance@contoso.com',
    [string]$EvidencePath = ".\Control-1.17_PolicyState_$(Get-Date -Format 'yyyyMMdd-HHmmss').json"
)

$ErrorActionPreference = 'Stop'

# Zone-driven action defaults
$blockAccess         = $Zone -ge 2
$allowOverride       = $Zone -eq 2
$endpointActions     = switch ($Zone) {
    1 { 'Audit' }
    2 { 'Block' }
    3 { 'Block' }
}

try {
    Write-Host "[Step 1/4] Locating existing policy '$PolicyName'..." -ForegroundColor Cyan
    $existing = Get-DlpCompliancePolicy -Identity $PolicyName -ErrorAction SilentlyContinue

    if ($existing) {
        Write-Host "  Found existing policy (current mode: $($existing.Mode))." -ForegroundColor Yellow
        if ($PSCmdlet.ShouldProcess($PolicyName, "Update DLP policy mode to $Mode")) {
            Set-DlpCompliancePolicy -Identity $PolicyName -Mode $Mode | Out-Null
            Write-Host "  [OK] Policy mode set to $Mode" -ForegroundColor Green
        }
    }
    else {
        if ($PSCmdlet.ShouldProcess($PolicyName, "Create new Endpoint DLP policy (Zone $Zone, mode $Mode)")) {
            New-DlpCompliancePolicy -Name $PolicyName `
                -Mode $Mode `
                -EndpointDlpLocation 'All' `
                -Comment "FSI Endpoint DLP — Zone $Zone — created $(Get-Date -Format 'u')" | Out-Null
            Write-Host "  [OK] Policy created" -ForegroundColor Green
        }
    }

    $ruleName = "$PolicyName-FinancialData"
    Write-Host "[Step 2/4] Locating rule '$ruleName'..." -ForegroundColor Cyan
    $existingRule = Get-DlpComplianceRule -Identity $ruleName -ErrorAction SilentlyContinue

    $sits = @(
        @{Name='U.S. Social Security Number (SSN)';   minCount=1; confidencelevel='High'}
        @{Name='Credit Card Number';                  minCount=1; confidencelevel='High'}
        @{Name='U.S. Bank Account Number';            minCount=1; confidencelevel='High'}
        @{Name='ABA Routing Number';                  minCount=1; confidencelevel='High'}
    )

    $policyTip = "This content contains sensitive financial information. " +
                 "Per firm policy, this action is restricted. " +
                 "Contact $ContactEmail for assistance."

    $ruleParams = @{
        ContentContainsSensitiveInformation = $sits
        BlockAccess                         = $blockAccess
        AllowOverride                       = $allowOverride
        NotifyUser                          = @('Owner','LastModifier','SiteAdmin')
        NotifyPolicyTipCustomText           = $policyTip
        GenerateAlert                       = 'SiteAdmin'
        ReportSeverityLevel                 = 'High'
    }

    if ($existingRule) {
        if ($PSCmdlet.ShouldProcess($ruleName, "Update DLP rule (Zone $Zone)")) {
            Set-DlpComplianceRule -Identity $ruleName @ruleParams | Out-Null
            Write-Host "  [OK] Rule updated" -ForegroundColor Green
        }
    }
    else {
        if ($PSCmdlet.ShouldProcess($ruleName, "Create DLP rule (Zone $Zone)")) {
            New-DlpComplianceRule -Name $ruleName -Policy $PolicyName @ruleParams | Out-Null
            Write-Host "  [OK] Rule created" -ForegroundColor Green
        }
    }

    Write-Host "[Step 3/4] Re-reading policy state..." -ForegroundColor Cyan
    $finalPolicy = Get-DlpCompliancePolicy -Identity $PolicyName
    $finalRule   = Get-DlpComplianceRule   -Identity $ruleName

    Write-Host "[Step 4/4] Writing evidence artefact..." -ForegroundColor Cyan
    $evidence = [PSCustomObject]@{
        Control          = '1.17'
        PolicyName       = $PolicyName
        Zone             = $Zone
        Mode             = $finalPolicy.Mode
        EndpointLocation = $finalPolicy.EndpointDlpLocation -join ','
        RuleName         = $finalRule.Name
        BlockAccess      = $finalRule.BlockAccess
        AllowOverride    = $finalRule.AllowOverride
        NotifyUser       = $finalRule.NotifyUser -join ','
        AlertSeverity    = $finalRule.ReportSeverityLevel
        Sits             = ($sits | ForEach-Object { $_.Name }) -join ','
        CapturedUtc      = (Get-Date).ToUniversalTime().ToString('o')
        CapturedBy       = $env:USERNAME
        TenantUpn        = (Get-ConnectionInformation | Select-Object -ExpandProperty UserPrincipalName -First 1)
    }

    $evidence | ConvertTo-Json -Depth 4 | Out-File -FilePath $EvidencePath -Encoding utf8
    $hash = (Get-FileHash -Path $EvidencePath -Algorithm SHA256).Hash
    "$hash  $(Split-Path $EvidencePath -Leaf)" | Out-File -FilePath "$EvidencePath.sha256" -Encoding ascii

    Write-Host "[DONE] Evidence: $EvidencePath" -ForegroundColor Green
    Write-Host "[DONE] SHA-256:  $hash" -ForegroundColor Green
}
catch {
    Write-Error "Control 1.17 policy configuration failed: $($_.Exception.Message)"
    Write-Host $_.ScriptStackTrace -ForegroundColor DarkGray
    throw
}
```

---

## Script 2 — Inventory and Export Endpoint DLP Posture (Read-Only Evidence)

```powershell
<#
.SYNOPSIS
    Read-only export of all Endpoint DLP policies and rules for compliance evidence.

.EXAMPLE
    .\Get-Control117Posture.ps1 -OutputDir 'C:\Audit\1.17'
#>
[CmdletBinding()]
param(
    [string]$OutputDir = ".\Control-1.17-Posture_$(Get-Date -Format 'yyyyMMdd')"
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir | Out-Null
}

try {
    Write-Host "Enumerating Endpoint DLP policies..." -ForegroundColor Cyan
    $allPolicies = Get-DlpCompliancePolicy
    $endpointPolicies = $allPolicies | Where-Object {
        $_.EndpointDlpLocation -and $_.EndpointDlpLocation.Count -gt 0
    }

    if (-not $endpointPolicies) {
        Write-Warning "No Endpoint DLP policies found. Control 1.17 is NOT configured."
    }

    $rows = foreach ($p in $endpointPolicies) {
        $rules = Get-DlpComplianceRule -Policy $p.Name
        foreach ($r in $rules) {
            [PSCustomObject]@{
                PolicyName        = $p.Name
                PolicyMode        = $p.Mode
                PolicyEnabled     = $p.Enabled
                EndpointLocation  = $p.EndpointDlpLocation -join ','
                RuleName          = $r.Name
                Priority          = $r.Priority
                BlockAccess       = $r.BlockAccess
                AllowOverride     = $r.AllowOverride
                NotifyUser        = ($r.NotifyUser -join ',')
                ReportSeverity    = $r.ReportSeverityLevel
                ContentContains   = ($r.ContentContainsSensitiveInformation | ForEach-Object { $_.Name }) -join ';'
                CapturedUtc       = (Get-Date).ToUniversalTime().ToString('o')
            }
        }
    }

    $csvPath = Join-Path $OutputDir 'Control-1.17_Posture.csv'
    $rows | Export-Csv -Path $csvPath -NoTypeInformation -Encoding utf8

    $jsonPath = Join-Path $OutputDir 'Control-1.17_Posture.json'
    $rows | ConvertTo-Json -Depth 5 | Out-File -FilePath $jsonPath -Encoding utf8

    foreach ($file in @($csvPath, $jsonPath)) {
        $hash = (Get-FileHash -Path $file -Algorithm SHA256).Hash
        "$hash  $(Split-Path $file -Leaf)" | Out-File -FilePath "$file.sha256" -Encoding ascii
    }

    Write-Host "[OK] Posture exported: $OutputDir" -ForegroundColor Green
    Write-Host "  Policies discovered: $($endpointPolicies.Count)" -ForegroundColor Green
    Write-Host "  Rules captured:      $($rows.Count)" -ForegroundColor Green
}
catch {
    Write-Error "Posture export failed: $($_.Exception.Message)"
    throw
}
```

---

## Script 3 — Validation Script (Pass/Fail Gates for Pre-Audit)

```powershell
<#
.SYNOPSIS
    Validates Control 1.17 posture against zone-based pass/fail criteria.

.PARAMETER MinPolicies
    Minimum number of Endpoint DLP policies expected (default 1).

.PARAMETER RequireEnforcement
    If specified, fails any policy not in 'Enable' mode.

.EXAMPLE
    .\Test-Control117.ps1 -RequireEnforcement
#>
[CmdletBinding()]
param(
    [int]$MinPolicies = 1,
    [switch]$RequireEnforcement
)

$ErrorActionPreference = 'Stop'
$results = [System.Collections.Generic.List[object]]::new()

function Add-Check {
    param($Name, $Status, $Detail)
    $results.Add([PSCustomObject]@{ Check = $Name; Status = $Status; Detail = $Detail })
}

try {
    $endpointPolicies = Get-DlpCompliancePolicy | Where-Object {
        $_.EndpointDlpLocation -and $_.EndpointDlpLocation.Count -gt 0
    }

    # Check 1: At least one Endpoint DLP policy
    if ($endpointPolicies.Count -ge $MinPolicies) {
        Add-Check 'Endpoint DLP policy exists' 'PASS' "$($endpointPolicies.Count) policy(ies) found"
    } else {
        Add-Check 'Endpoint DLP policy exists' 'FAIL' "Found $($endpointPolicies.Count); required >= $MinPolicies"
    }

    # Check 2: Enforcement mode (optional gate)
    $enabled = $endpointPolicies | Where-Object { $_.Mode -eq 'Enable' }
    if ($RequireEnforcement) {
        if ($enabled.Count -eq $endpointPolicies.Count -and $enabled.Count -gt 0) {
            Add-Check 'All policies enforced' 'PASS' "$($enabled.Count)/$($endpointPolicies.Count) in Enable mode"
        } else {
            Add-Check 'All policies enforced' 'FAIL' "$($enabled.Count)/$($endpointPolicies.Count) in Enable mode"
        }
    } else {
        Add-Check 'All policies enforced' 'INFO' "$($enabled.Count)/$($endpointPolicies.Count) in Enable mode (gate not required)"
    }

    # Check 3: Each policy has a rule with BlockAccess for Z2/Z3 naming convention
    foreach ($p in $endpointPolicies) {
        $rules = Get-DlpComplianceRule -Policy $p.Name
        if ($rules.Count -eq 0) {
            Add-Check "Policy '$($p.Name)' has rules" 'FAIL' 'No rules attached'
            continue
        }
        $blockingRules = $rules | Where-Object { $_.BlockAccess -eq $true }
        if ($p.Name -match 'Z[23]' -and $blockingRules.Count -eq 0) {
            Add-Check "Policy '$($p.Name)' enforces blocking" 'FAIL' 'Z2/Z3 naming convention but no blocking rule'
        } else {
            Add-Check "Policy '$($p.Name)' enforces blocking" 'PASS' "$($blockingRules.Count) blocking rule(s)"
        }
    }

    # Output
    Write-Host "`n=== Control 1.17 Validation ===" -ForegroundColor Cyan
    $results | Format-Table -AutoSize

    $failures = ($results | Where-Object { $_.Status -eq 'FAIL' }).Count
    if ($failures -gt 0) {
        Write-Host "[OVERALL] FAIL ($failures failures)" -ForegroundColor Red
        exit 1
    }
    Write-Host "[OVERALL] PASS" -ForegroundColor Green
}
catch {
    Write-Error "Validation failed: $($_.Exception.Message)"
    throw
}
```

---

## Manual Steps That PowerShell Cannot Cover

These configuration items **must** be performed in the portal (see [Portal Walkthrough](portal-walkthrough.md)):

1. **Restricted apps and app groups** — `Purview > Endpoint DLP settings > Restricted apps`
2. **Removable storage device groups** (USB allowlist by Vendor/Product ID) — `Purview > Endpoint DLP settings > Removable storage device groups`
3. **Service domain groups** (allow/block lists for cloud and AI services) — `Purview > Endpoint DLP settings > Service domains`
4. **Browser and domain restrictions** (unallowed browsers) — `Purview > Endpoint DLP settings > Browser and domain restrictions to sensitive data`
5. **Just-in-time protection** toggle and fallback action — `Purview > Endpoint DLP settings > Just-in-time protection`
6. **Edge for Business location** toggle on each DLP policy — `Purview > DLP > Policies > <policy> > Locations`
7. **Global Secure Access security profiles** — `Microsoft Entra > Global Secure Access > Secure > Security profiles`
8. **Defender for Endpoint device onboarding** — `Microsoft Intune > Endpoint security > Endpoint detection and response`

Capture screenshots of each portal-only setting and store under `maintainers-local/tenant-evidence/1.17/` for audit evidence.

---

## Cleanup

```powershell
Disconnect-ExchangeOnline -Confirm:$false -ErrorAction SilentlyContinue
```

---

[Back to Control 1.17](../../../controls/pillar-1-security/1.17-endpoint-data-loss-prevention-endpoint-dlp.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
