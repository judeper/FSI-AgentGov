# PowerShell Setup: Control 1.25 - MIME Type Restrictions for File Uploads

**Last Updated:** February 2026
**Modules Required:** Microsoft.PowerApps.Administration.PowerShell

> **⚠️ Important — Placeholder Cmdlets:** The scripts below use illustrative cmdlet names (e.g., `Get-FsiMimeConfig`, `Set-FsiMimeConfig`, `Test-FsiMimeCompliance`) that represent a **planned custom FSI governance module** (`FsiMimeControl`). These cmdlets do not exist in any published PowerShell module today. For current manual configuration steps, see the [Portal Walkthrough](portal-walkthrough.md). To query environment metadata via PowerShell now, use `Get-AdminPowerAppEnvironment` from the Power Platform Admin module and the Dataverse REST API for MIME type settings.

## Prerequisites

```powershell
# Install the Power Platform Administration module (available today)
Install-Module -Name Microsoft.PowerApps.Administration.PowerShell -Force -AllowClobber
Import-Module Microsoft.PowerApps.Administration.PowerShell

# Connect to Power Platform
Add-PowerAppsAccount

# Verify you can list environments
Get-AdminPowerAppEnvironment | Select-Object DisplayName, EnvironmentName
```

> **Note:** MIME type and file-extension restriction settings are configured per-environment in Dataverse. Use `Get-AdminPowerAppEnvironment` to enumerate environments, then configure MIME restrictions through the Power Platform Admin Center or the Dataverse Web API (`PATCH /api/data/v9.2/organizations({id})`).

---

## Automated Scripts

### Get Current MIME Configuration

```powershell
# NOTE: These cmdlet names are illustrative placeholders for a custom FSI governance module.
# See the portal walkthrough for current manual configuration steps.

<#
.SYNOPSIS
    Retrieves current MIME type and file extension restrictions for a Power Platform environment.

.DESCRIPTION
    Uses the Dataverse Web API to read blocked file extensions, blocked MIME types,
    and allowed MIME types for the specified environment.
    Replace the placeholder cmdlet below with a direct Dataverse REST call or
    the portal walkthrough procedure until a published module is available.

.EXAMPLE
    # Current approach: Use Get-AdminPowerAppEnvironment + Dataverse REST API
    $env = Get-AdminPowerAppEnvironment -EnvironmentName "00000000-0000-0000-0000-000000000001"
    # Then query Dataverse: GET /api/data/v9.2/organizations?$select=blockedattachments,blockedmimetypes
#>

# --- Placeholder pattern (custom module not yet available) ---
# $config = Get-FsiMimeConfig -EnvironmentId "00000000-0000-0000-0000-000000000001"

# --- Current approach: query Dataverse REST API ---
$envId = "00000000-0000-0000-0000-000000000001"
$env = Get-AdminPowerAppEnvironment -EnvironmentName $envId

Write-Host "=== MIME Configuration ===" -ForegroundColor Cyan
Write-Host "Environment: $($env.DisplayName)" -ForegroundColor Yellow
Write-Host "To retrieve MIME restrictions, query the Dataverse Organization entity:"
Write-Host "  GET {envUrl}/api/data/v9.2/organizations?`$select=blockedattachments,blockedmimetypes"
Write-Host "See the portal walkthrough for step-by-step UI instructions."
```

### Apply Zone Template

```powershell
# NOTE: These cmdlet names are illustrative placeholders for a custom FSI governance module.
# See the portal walkthrough for current manual configuration steps.

<#
.SYNOPSIS
    Applies a zone-specific MIME restriction template to a Power Platform environment.

.DESCRIPTION
    Configures blocked file extensions and blocked MIME types according to the
    governance zone template. Until the custom module is published, apply these
    settings via the Power Platform Admin Center or Dataverse REST API:
      PATCH {envUrl}/api/data/v9.2/organizations({orgId})
      Body: { "blockedattachments": "exe;bat;cmd;...", "blockedmimetypes": "..." }

.EXAMPLE
    # Current approach: update via Dataverse REST API
    # See portal walkthrough for the full list of extensions per zone template
#>

# --- Placeholder pattern (custom module not yet available) ---
# Set-FsiMimeConfig -EnvironmentId "00000000-0000-0000-0000-000000000001" `
#     -ZoneTemplate zone2 `
#     -WhatIf
# Set-FsiMimeConfig -EnvironmentId "00000000-0000-0000-0000-000000000001" `
#     -ZoneTemplate zone2

# --- Current approach: Dataverse REST API ---
# Zone 2 reference values (customize per your governance requirements):
$blockedExtensions = "exe;bat;cmd;com;vbs;js;wsf;scr;pif;msi;dll;ps1;reg;inf;hta;cpl;msp;mst"
$blockedMimeTypes  = "application/x-msdownload;application/x-msdos-program;application/x-bat"

Write-Host "Zone template values prepared. Apply via:"
Write-Host "  1. Power Platform Admin Center → Environment → Settings → Email → Email security"
Write-Host "  2. Dataverse REST API PATCH to organizations entity"
Write-Host "  Blocked Extensions: $blockedExtensions"
Write-Host "  Blocked MIME Types:  $blockedMimeTypes"
```

### Validate Compliance

```powershell
# NOTE: These cmdlet names are illustrative placeholders for a custom FSI governance module.
# See the portal walkthrough for current manual configuration steps.

<#
.SYNOPSIS
    Checks whether a Power Platform environment meets MIME restriction requirements
    for its assigned governance zone.

.DESCRIPTION
    Until the custom module is published, validate MIME compliance manually:
    1. Query current settings via Dataverse REST API (see "Get Current MIME Configuration" above)
    2. Compare blocked extensions and MIME types against zone template values
    3. Record pass/fail per check

.EXAMPLE
    # Placeholder — no native compliance-test cmdlet exists today:
    # $result = Test-FsiMimeCompliance -EnvironmentId "..." -Zone 2
    # Use the verification-testing playbook for current manual validation steps.
#>

# --- Placeholder pattern (custom module not yet available) ---
# $result = Test-FsiMimeCompliance -EnvironmentId "00000000-0000-0000-0000-000000000001" -Zone 2

# --- Current approach: manual comparison ---
# Expected sample output once a validation module exists:
# === MIME Compliance Check: Contoso-Zone2-Env (Zone 2) ===
# [PASS] Blocked file extensions configured
# [PASS] All required executable extensions blocked
# [PASS] Blocked MIME types configured
# [PASS] All required MIME types blocked
# [WARN] Allowed MIME types not configured (recommended for Zone 2)
# [INFO] DLP policy validation requires separate check — see Control 1.14
#
# Overall: COMPLIANT (5/5 required checks passed, 1 warning)

Write-Host "Manual validation: Query Dataverse organization entity and compare against zone template."
Write-Host "See verification-testing.md for the full validation checklist."
```

---

## Validation Script

```powershell
# NOTE: These cmdlet names are illustrative placeholders for a custom FSI governance module.
# See the portal walkthrough for current manual configuration steps.
# The script below shows the intended validation pattern. Replace placeholder
# cmdlets with Dataverse REST API calls or manual checks until the module ships.

<#
.SYNOPSIS
    Validates Control 1.25 - MIME Type Restrictions across all environments.

.DESCRIPTION
    Reference implementation pattern. The Get-FsiMimeConfig and Test-FsiMimeCompliance
    cmdlets used below are planned for a custom governance module. Until available,
    validate each environment manually via:
      1. Power Platform Admin Center → Environments → Settings
      2. Dataverse REST API: GET /api/data/v9.2/organizations?$select=blockedattachments,blockedmimetypes

.EXAMPLE
    .\Validate-Control-1.25.ps1
#>

Write-Host "=== Control 1.25 Validation ===" -ForegroundColor Cyan

# Current approach: enumerate environments with the Power Platform Admin module
$environments = Get-AdminPowerAppEnvironment

$results = @()

foreach ($env in $environments) {
    Write-Host "`nEnvironment: $($env.DisplayName)" -ForegroundColor Yellow

    # NOTE: The checks below use placeholder cmdlets. Replace with Dataverse REST
    # API queries to read blockedattachments and blockedmimetypes columns from the
    # Organization entity for each environment.

    # Placeholder — Check 1: Blocked extensions
    # $config = Get-FsiMimeConfig -EnvironmentId $env.EnvironmentName
    # if ($config.BlockedExtensions.Count -gt 0) { ... }

    # Placeholder — Check 2: Blocked MIME types
    # if ($config.BlockedMimeTypes.Count -gt 0) { ... }

    # Placeholder — Check 3: Allowed MIME types
    # if ($config.AllowedMimeTypes.Count -gt 0) { ... }

    # Placeholder — Check 4: Zone compliance summary
    # $compliance = Test-FsiMimeCompliance -EnvironmentId $env.EnvironmentName -Zone $zone

    Write-Host "  [INFO] Validate MIME settings via Dataverse REST API or Admin Center" -ForegroundColor Yellow
    Write-Host "  [INFO] See verification-testing.md for the full manual checklist" -ForegroundColor Yellow

    $results += [PSCustomObject]@{
        Environment   = $env.DisplayName
        EnvironmentId = $env.EnvironmentName
        Status        = "Manual verification required"
    }
}

Write-Host "`n=== Summary ===" -ForegroundColor Cyan
$results | Format-Table -AutoSize
```

---

## Complete Configuration Script

```powershell
# NOTE: These cmdlet names are illustrative placeholders for a custom FSI governance module.
# See the portal walkthrough for current manual configuration steps.
# Replace FsiMimeControl cmdlets with Dataverse REST API calls or Admin Center
# procedures until the planned module is available.

<#
.SYNOPSIS
    Configures MIME type restrictions for Control 1.25 across Power Platform environments.

.DESCRIPTION
    Reference implementation pattern showing the intended automation flow.
    The Set-FsiMimeConfig and Test-FsiMimeCompliance cmdlets are planned for a
    custom governance module (FsiMimeControl). Until available:
      - Use Get-AdminPowerAppEnvironment to enumerate environments
      - Apply MIME settings via Dataverse REST API or Power Platform Admin Center
      - Validate manually using the verification-testing playbook

.PARAMETER EnvironmentId
    The Power Platform environment ID to configure. If not specified, processes all managed environments.

.PARAMETER ZoneTemplate
    The governance zone template to apply: zone1, zone2, or zone3.

.PARAMETER OutputFormat
    Output format for the report: Table, JSON, or CSV. Default: Table.

.PARAMETER OutputPath
    File path to export results. If not specified, results are written to the console.

.EXAMPLE
    .\Configure-Control-1.25.ps1 -ZoneTemplate zone2

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
    [string]$OutputPath
)

try {
    Import-Module Microsoft.PowerApps.Administration.PowerShell -ErrorAction Stop
    Add-PowerAppsAccount

    Write-Host "=== Control 1.25: MIME Type Restrictions Configuration ===" -ForegroundColor Cyan
    Write-Host "Zone Template: $ZoneTemplate" -ForegroundColor Yellow

    # Determine target environments
    if ($EnvironmentId) {
        $environments = @(Get-AdminPowerAppEnvironment -EnvironmentName $EnvironmentId)
    } else {
        $environments = Get-AdminPowerAppEnvironment
    }

    $results = @()

    foreach ($env in $environments) {
        Write-Host "`nProcessing: $($env.DisplayName)" -ForegroundColor Yellow

        # NOTE: Apply MIME restrictions via Dataverse REST API:
        #   PATCH {envUrl}/api/data/v9.2/organizations({orgId})
        #   Body: { "blockedattachments": "exe;bat;cmd;...", "blockedmimetypes": "..." }
        # Placeholder cmdlet (not yet available):
        # Set-FsiMimeConfig -EnvironmentId $env.EnvironmentName -ZoneTemplate $ZoneTemplate

        # NOTE: Validate via Dataverse REST API or manual inspection.
        # Placeholder cmdlet (not yet available):
        # $validation = Test-FsiMimeCompliance -EnvironmentId $env.EnvironmentName -Zone ([int]$ZoneTemplate[-1].ToString())

        $results += [PSCustomObject]@{
            Environment     = $env.DisplayName
            EnvironmentId   = $env.EnvironmentName
            ZoneTemplate    = $ZoneTemplate
            Status          = "Apply via Admin Center or Dataverse REST API"
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
