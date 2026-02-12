# PowerShell Setup: Control 1.25 - MIME Type Restrictions for File Uploads

**Last Updated:** February 2026
**Modules Required:** FsiMimeControl

## Prerequisites

```powershell
# FsiMimeControl is part of the FSI Agent Governance toolkit (Phase 2 deliverable)
Install-Module -Name FsiMimeControl -Force -Scope CurrentUser
Import-Module FsiMimeControl
```

> **Note:** The FsiMimeControl module connects to the Dataverse Web API to read and write environment-level MIME and file extension settings. Ensure you have Power Platform Admin or Entra Global Admin permissions before running these cmdlets.

---

## Automated Scripts

### Get Current MIME Configuration

```powershell
<#
.SYNOPSIS
    Retrieves current MIME type and file extension restrictions for a Power Platform environment.

.DESCRIPTION
    Reads blocked file extensions, blocked MIME types, and allowed MIME types
    from the Dataverse Web API for the specified environment.

.PARAMETER EnvironmentId
    The Power Platform environment ID to query.

.EXAMPLE
    Get-FsiMimeConfig -EnvironmentId "00000000-0000-0000-0000-000000000001"

.EXAMPLE
    Get-FsiMimeConfig -EnvironmentId "00000000-0000-0000-0000-000000000001" | Format-List
#>

$config = Get-FsiMimeConfig -EnvironmentId "00000000-0000-0000-0000-000000000001"

Write-Host "=== MIME Configuration ===" -ForegroundColor Cyan
Write-Host "Environment:          $($config.EnvironmentName)" -ForegroundColor Yellow
Write-Host "Blocked Extensions:   $($config.BlockedExtensions -join '; ')"
Write-Host "Blocked MIME Types:   $($config.BlockedMimeTypes -join '; ')"
Write-Host "Allowed MIME Types:   $($config.AllowedMimeTypes -join '; ')"
```

### Apply Zone Template

```powershell
<#
.SYNOPSIS
    Applies a zone-specific MIME restriction template to a Power Platform environment.

.DESCRIPTION
    Configures blocked file extensions, blocked MIME types, and allowed MIME types
    according to the governance zone template. Supports -WhatIf for dry-run preview.

.PARAMETER EnvironmentId
    The Power Platform environment ID to configure.

.PARAMETER ZoneTemplate
    The governance zone template to apply: zone1, zone2, or zone3.

.PARAMETER WhatIf
    Preview changes without applying them.

.EXAMPLE
    Set-FsiMimeConfig -EnvironmentId "00000000-0000-0000-0000-000000000001" -ZoneTemplate zone2 -WhatIf

.EXAMPLE
    Set-FsiMimeConfig -EnvironmentId "00000000-0000-0000-0000-000000000001" -ZoneTemplate zone3
#>

# Preview changes before applying
Set-FsiMimeConfig -EnvironmentId "00000000-0000-0000-0000-000000000001" `
    -ZoneTemplate zone2 `
    -WhatIf

# Sample WhatIf output:
# What if: Performing the operation "Set-FsiMimeConfig" on target "Contoso-Zone2-Env":
#   Blocked Extensions: exe;bat;cmd;com;vbs;js;wsf;scr;pif;msi;dll;ps1;reg;inf;hta;cpl;msp;mst
#   Blocked MIME Types:  application/x-msdownload;application/x-msdos-program;application/x-bat;...
#   Allowed MIME Types:  application/pdf;image/png;image/jpeg;...

# Apply the template
Set-FsiMimeConfig -EnvironmentId "00000000-0000-0000-0000-000000000001" `
    -ZoneTemplate zone2
```

### Validate Compliance

```powershell
<#
.SYNOPSIS
    Checks whether a Power Platform environment meets MIME restriction requirements
    for its assigned governance zone.

.DESCRIPTION
    Compares the current environment MIME configuration against the expected zone
    template and outputs [PASS], [FAIL], or [WARN] for each check.

.PARAMETER EnvironmentId
    The Power Platform environment ID to validate.

.PARAMETER Zone
    The governance zone to validate against (1, 2, or 3).

.EXAMPLE
    Test-FsiMimeCompliance -EnvironmentId "00000000-0000-0000-0000-000000000001" -Zone 2

.EXAMPLE
    Test-FsiMimeCompliance -EnvironmentId "00000000-0000-0000-0000-000000000001" -Zone 3 -Verbose
#>

$result = Test-FsiMimeCompliance -EnvironmentId "00000000-0000-0000-0000-000000000001" -Zone 2

# Sample output:
# === MIME Compliance Check: Contoso-Zone2-Env (Zone 2) ===
# [PASS] Blocked file extensions configured
# [PASS] All required executable extensions blocked
# [PASS] Blocked MIME types configured
# [PASS] All required MIME types blocked
# [WARN] Allowed MIME types not configured (recommended for Zone 2)
# [INFO] DLP policy validation requires separate check — see Control 1.14
#
# Overall: COMPLIANT (5/5 required checks passed, 1 warning)
```

---

## Validation Script

```powershell
<#
.SYNOPSIS
    Validates Control 1.25 - MIME Type Restrictions across all environments.

.EXAMPLE
    .\Validate-Control-1.25.ps1
#>

Write-Host "=== Control 1.25 Validation ===" -ForegroundColor Cyan

Import-Module FsiMimeControl

$environments = Get-FsiManagedEnvironments

$results = @()

foreach ($env in $environments) {
    Write-Host "`nEnvironment: $($env.DisplayName) (Zone $($env.Zone))" -ForegroundColor Yellow

    # Check 1: Blocked extensions
    $config = Get-FsiMimeConfig -EnvironmentId $env.EnvironmentId
    if ($config.BlockedExtensions.Count -gt 0) {
        Write-Host "  [PASS] Blocked file extensions configured ($($config.BlockedExtensions.Count) extensions)" -ForegroundColor Green
    } else {
        Write-Host "  [FAIL] No blocked file extensions configured" -ForegroundColor Red
    }

    # Check 2: Blocked MIME types (Zone 2+)
    if ($env.Zone -ge 2) {
        if ($config.BlockedMimeTypes.Count -gt 0) {
            Write-Host "  [PASS] Blocked MIME types configured ($($config.BlockedMimeTypes.Count) types)" -ForegroundColor Green
        } else {
            Write-Host "  [FAIL] Blocked MIME types not configured (required for Zone $($env.Zone))" -ForegroundColor Red
        }
    } else {
        Write-Host "  [INFO] Blocked MIME types not required for Zone 1" -ForegroundColor Gray
    }

    # Check 3: Allowed MIME types (Zone 3 required, Zone 2 recommended)
    if ($env.Zone -eq 3) {
        if ($config.AllowedMimeTypes.Count -gt 0) {
            Write-Host "  [PASS] Allowed MIME types allowlist configured ($($config.AllowedMimeTypes.Count) types)" -ForegroundColor Green
        } else {
            Write-Host "  [FAIL] Allowed MIME types allowlist not configured (required for Zone 3)" -ForegroundColor Red
        }
    } elseif ($env.Zone -eq 2) {
        if ($config.AllowedMimeTypes.Count -gt 0) {
            Write-Host "  [PASS] Allowed MIME types allowlist configured ($($config.AllowedMimeTypes.Count) types)" -ForegroundColor Green
        } else {
            Write-Host "  [WARN] Allowed MIME types allowlist not configured (recommended for Zone 2)" -ForegroundColor Yellow
        }
    } else {
        Write-Host "  [INFO] Allowed MIME types allowlist not required for Zone 1" -ForegroundColor Gray
    }

    # Check 4: Zone compliance summary
    $compliance = Test-FsiMimeCompliance -EnvironmentId $env.EnvironmentId -Zone $env.Zone
    if ($compliance.IsCompliant) {
        Write-Host "  [PASS] Environment is compliant with Zone $($env.Zone) requirements" -ForegroundColor Green
    } else {
        Write-Host "  [FAIL] Environment is NOT compliant with Zone $($env.Zone) requirements" -ForegroundColor Red
        foreach ($finding in $compliance.Findings) {
            Write-Host "    - $finding" -ForegroundColor Red
        }
    }

    $results += [PSCustomObject]@{
        Environment   = $env.DisplayName
        Zone          = $env.Zone
        Extensions    = $config.BlockedExtensions.Count
        BlockedMime   = $config.BlockedMimeTypes.Count
        AllowedMime   = $config.AllowedMimeTypes.Count
        Compliant     = $compliance.IsCompliant
    }
}

Write-Host "`n=== Summary ===" -ForegroundColor Cyan
$results | Format-Table -AutoSize
```

---

## Complete Configuration Script

```powershell
<#
.SYNOPSIS
    Configures MIME type restrictions for Control 1.25 across Power Platform environments.

.DESCRIPTION
    Applies zone-appropriate MIME type and file extension restriction templates
    to Power Platform environments. Supports dry-run preview with -WhatIf,
    multiple output formats, and file export.

.PARAMETER EnvironmentId
    The Power Platform environment ID to configure. If not specified, processes all managed environments.

.PARAMETER ZoneTemplate
    The governance zone template to apply: zone1, zone2, or zone3.

.PARAMETER OutputFormat
    Output format for the report: Table, JSON, or CSV. Default: Table.

.PARAMETER OutputPath
    File path to export results. If not specified, results are written to the console.

.PARAMETER WhatIf
    Preview changes without applying them.

.EXAMPLE
    .\Configure-Control-1.25.ps1 -ZoneTemplate zone2 -WhatIf

.EXAMPLE
    .\Configure-Control-1.25.ps1 -EnvironmentId "00000000-0000-0000-0000-000000000001" -ZoneTemplate zone3 -OutputFormat JSON -OutputPath ".\results.json"
#>

param(
    [Parameter()]
    [string]$EnvironmentId,

    [Parameter(Mandatory)]
    [ValidateSet("zone1", "zone2", "zone3")]
    [string]$ZoneTemplate,

    [Parameter()]
    [ValidateSet("Table", "JSON", "CSV")]
    [string]$OutputFormat = "Table",

    [Parameter()]
    [string]$OutputPath,

    [Parameter()]
    [switch]$WhatIf
)

try {
    Import-Module FsiMimeControl -ErrorAction Stop
    Write-Host "=== Control 1.25: MIME Type Restrictions Configuration ===" -ForegroundColor Cyan
    Write-Host "Zone Template: $ZoneTemplate" -ForegroundColor Yellow
    Write-Host "Mode: $(if ($WhatIf) { 'Preview (WhatIf)' } else { 'Apply' })" -ForegroundColor Yellow

    # Determine target environments
    if ($EnvironmentId) {
        $environments = @(Get-FsiMimeConfig -EnvironmentId $EnvironmentId)
    } else {
        $environments = Get-FsiManagedEnvironments
    }

    $results = @()

    foreach ($env in $environments) {
        Write-Host "`nProcessing: $($env.DisplayName)" -ForegroundColor Yellow

        # Apply zone template
        $applyParams = @{
            EnvironmentId = $env.EnvironmentId
            ZoneTemplate  = $ZoneTemplate
        }
        if ($WhatIf) {
            $applyParams['WhatIf'] = $true
        }

        $applyResult = Set-FsiMimeConfig @applyParams

        # Validate after apply (skip validation in WhatIf mode)
        $compliant = $false
        if (-not $WhatIf) {
            $validation = Test-FsiMimeCompliance -EnvironmentId $env.EnvironmentId -Zone ([int]$ZoneTemplate[-1].ToString())
            $compliant = $validation.IsCompliant
        }

        $results += [PSCustomObject]@{
            Environment     = $env.DisplayName
            EnvironmentId   = $env.EnvironmentId
            ZoneTemplate    = $ZoneTemplate
            Applied         = -not $WhatIf
            Compliant       = if ($WhatIf) { "N/A (WhatIf)" } else { $compliant }
            Timestamp       = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        }
    }

    # Output results
    switch ($OutputFormat) {
        "Table" { $results | Format-Table -AutoSize }
        "JSON"  { $results | ConvertTo-Json -Depth 3 }
        "CSV"   { $results | ConvertTo-Csv -NoTypeInformation }
    }

    # Export to file if OutputPath specified
    if ($OutputPath) {
        switch ($OutputFormat) {
            "Table" { $results | Format-Table -AutoSize | Out-File -FilePath $OutputPath }
            "JSON"  { $results | ConvertTo-Json -Depth 3 | Out-File -FilePath $OutputPath }
            "CSV"   { $results | Export-Csv -Path $OutputPath -NoTypeInformation }
        }
        Write-Host "`nResults exported to: $OutputPath" -ForegroundColor Green
    }
}
catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Stack trace: $($_.ScriptStackTrace)" -ForegroundColor Red
    exit 1
}
finally {
    Write-Host "`n=== Configuration Complete ===" -ForegroundColor Cyan
}
```

---

[Back to Control 1.25](../../../controls/pillar-1-security/1.25-mime-type-restrictions.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
