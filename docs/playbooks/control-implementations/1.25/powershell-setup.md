# PowerShell Setup: Control 1.25 - MIME Type Restrictions for File Uploads

**Last Updated:** February 2026
**Modules Required:** Microsoft.PowerApps.Administration.PowerShell, FsiMimeControl

> **Module Available:** The `FsiMimeControl` module ships with this repository at `scripts/governance/FsiMimeControl.psm1`. It provides five cmdlets for zone-based MIME type configuration management via the Dataverse Web API: `Connect-FsiMimeDataverse`, `Get-FsiMimeConnection`, `Get-FsiMimeConfig`, `Set-FsiMimeConfig`, and `Test-FsiMimeCompliance`. For manual configuration steps, see the [Portal Walkthrough](portal-walkthrough.md).

## Prerequisites

```powershell
# Install the Power Platform Administration module
Install-Module -Name Microsoft.PowerApps.Administration.PowerShell -Force -AllowClobber
Import-Module Microsoft.PowerApps.Administration.PowerShell

# Import the FsiMimeControl module (shipped with this repository)
Import-Module ./scripts/governance/FsiMimeControl.psm1 -Force

# Connect to Power Platform
Add-PowerAppsAccount

# Verify you can list environments
Get-AdminPowerAppEnvironment | Select-Object DisplayName, EnvironmentName
```

> **Note:** The `FsiMimeControl` module requires PowerShell 7.0+ and uses the Dataverse Web API to read and write MIME type restriction settings on the Organization entity. Use `Get-AdminPowerAppEnvironment` to enumerate environments and obtain Dataverse URLs.

---

## Automated Scripts

### Get Current MIME Configuration

```powershell
<#
.SYNOPSIS
    Retrieves current MIME type and file extension restrictions for a Power Platform environment.

.DESCRIPTION
    Uses the FsiMimeControl module to query the Dataverse Organization entity for
    blocked file extensions, blocked MIME types, and allowed MIME types.

.EXAMPLE
    Get-FsiMimeConfig -DataverseUrl 'https://org.crm.dynamics.com' -AccessToken $token
#>

# Option 1: Direct call with explicit credentials
$config = Get-FsiMimeConfig -DataverseUrl 'https://org.crm.dynamics.com' -AccessToken $token

Write-Host "=== MIME Configuration ===" -ForegroundColor Cyan
Write-Host "Environment: $($config.DataverseUrl)" -ForegroundColor Yellow
Write-Host "Blocked Extensions: $($config.BlockedExtensions.Count)"
Write-Host "Blocked MIME Types: $($config.BlockedMimeTypes.Count)"
Write-Host "Allowed MIME Types: $(if ($config.AllowedMimeTypes) { $config.AllowedMimeTypes.Count } else { 'N/A' })"

# Option 2: Use module session (connect once, query multiple times)
Connect-FsiMimeDataverse -DataverseUrl 'https://org.crm.dynamics.com' -AccessToken $token
$config = Get-FsiMimeConfig
```

### Apply Zone Template

```powershell
<#
.SYNOPSIS
    Applies a zone-specific MIME restriction template to a Power Platform environment.

.DESCRIPTION
    Uses the FsiMimeControl module to apply blocked file extensions, blocked MIME types,
    and allowed MIME types from a zone template (zone1, zone2, or zone3) via the
    Dataverse Web API. Supports -WhatIf for safe preview.

.EXAMPLE
    Set-FsiMimeConfig -DataverseUrl 'https://org.crm.dynamics.com' -AccessToken $token -ZoneTemplate zone2 -WhatIf
    Set-FsiMimeConfig -DataverseUrl 'https://org.crm.dynamics.com' -AccessToken $token -ZoneTemplate zone2
#>

# Preview changes without applying
Set-FsiMimeConfig -DataverseUrl 'https://org.crm.dynamics.com' -AccessToken $token `
    -ZoneTemplate zone2 -WhatIf

# Apply Zone 2 template
Set-FsiMimeConfig -DataverseUrl 'https://org.crm.dynamics.com' -AccessToken $token `
    -ZoneTemplate zone2

# Apply custom configuration (instead of template)
Set-FsiMimeConfig -DataverseUrl 'https://org.crm.dynamics.com' -AccessToken $token `
    -BlockedExtensions @('exe','bat','cmd','com','vbs','js','wsf','scr','pif','msi','dll','ps1') `
    -BlockedMimeTypes @('application/x-msdownload','application/x-msdos-program','application/x-bat')
```

### Validate Compliance

```powershell
<#
.SYNOPSIS
    Checks whether a Power Platform environment meets MIME restriction requirements
    for its assigned governance zone.

.DESCRIPTION
    Compares the current Dataverse MIME configuration against the specified zone
    template. Returns pass/fail/warning status per check and overall compliance.

.EXAMPLE
    Test-FsiMimeCompliance -DataverseUrl 'https://org.crm.dynamics.com' -AccessToken $token -Zone 2
#>

$result = Test-FsiMimeCompliance -DataverseUrl 'https://org.crm.dynamics.com' -AccessToken $token -Zone 2

# Example output:
# ── MIME Compliance Summary (Zone 2) ────────────────────
#   Checks:    6
#   Passed:    5
#   Failed:    0
#   Warnings:  1
#   Compliant: True
# ────────────────────────────────────────────────────────

# With SHA-256 evidence hash for audit packaging
$result = Test-FsiMimeCompliance -DataverseUrl 'https://org.crm.dynamics.com' -AccessToken $token -Zone 2 -IncludeEvidence
```

---

## Validation Script

```powershell
<#
.SYNOPSIS
    Validates Control 1.25 - MIME Type Restrictions across all environments.

.DESCRIPTION
    Enumerates Power Platform environments and validates each against the
    appropriate zone template using Test-FsiMimeCompliance.

.EXAMPLE
    .\Validate-Control-1.25.ps1
#>

Import-Module ./scripts/governance/FsiMimeControl.psm1 -Force

Write-Host "=== Control 1.25 Validation ===" -ForegroundColor Cyan

# Connect once (uses Az.Accounts token fallback if no explicit token)
Connect-FsiMimeDataverse -DataverseUrl 'https://org.crm.dynamics.com' -AccessToken $token

# Enumerate environments
$environments = Get-AdminPowerAppEnvironment

$results = @()

foreach ($env in $environments) {
    Write-Host "`nEnvironment: $($env.DisplayName)" -ForegroundColor Yellow

    # Determine zone from your environment classification (customize this mapping)
    $zone = 2  # Default to Zone 2; replace with your environment-to-zone mapping logic

    # Validate compliance
    $envUrl = $env.Internal.properties.linkedEnvironmentMetadata.instanceUrl
    if ($envUrl) {
        $compliance = Test-FsiMimeCompliance -DataverseUrl $envUrl -AccessToken $token -Zone $zone
        $results += [PSCustomObject]@{
            Environment = $env.DisplayName
            Zone        = $zone
            Compliant   = $compliance.IsCompliant
            Passed      = $compliance.Summary.PassCount
            Failed      = $compliance.Summary.FailCount
            Warnings    = $compliance.Summary.WarnCount
        }
    } else {
        Write-Host "  [SKIP] No Dataverse URL for this environment" -ForegroundColor Yellow
        $results += [PSCustomObject]@{
            Environment = $env.DisplayName
            Zone        = $zone
            Compliant   = 'N/A'
            Passed      = 'N/A'
            Failed      = 'N/A'
            Warnings    = 'N/A'
        }
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
    Applies zone-based MIME restriction templates using the FsiMimeControl module
    and validates compliance after application.

.PARAMETER DataverseUrl
    The Dataverse environment URL to configure.

.PARAMETER AccessToken
    OAuth2 bearer token for the Dataverse environment.

.PARAMETER ZoneTemplate
    The governance zone template to apply: zone1, zone2, or zone3.

.PARAMETER OutputFormat
    Output format for the report: Table, JSON, or CSV. Default: Table.

.PARAMETER OutputPath
    File path to export results. If not specified, results are written to the console.

.EXAMPLE
    .\Configure-Control-1.25.ps1 -DataverseUrl 'https://org.crm.dynamics.com' -AccessToken $token -ZoneTemplate zone2

.EXAMPLE
    .\Configure-Control-1.25.ps1 -DataverseUrl 'https://org.crm.dynamics.com' -AccessToken $token -ZoneTemplate zone3 -OutputFormat JSON -OutputPath ".\results.json"
#>

param(
    [Parameter(Mandatory)]
    [string]$DataverseUrl,

    [Parameter(Mandatory)]
    [string]$AccessToken,

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
    Import-Module ./scripts/governance/FsiMimeControl.psm1 -Force

    Write-Host "=== Control 1.25: MIME Type Restrictions Configuration ===" -ForegroundColor Cyan
    Write-Host "Zone Template: $ZoneTemplate" -ForegroundColor Yellow

    # Preview changes
    Write-Host "`nPreviewing changes..." -ForegroundColor Yellow
    Set-FsiMimeConfig -DataverseUrl $DataverseUrl -AccessToken $AccessToken -ZoneTemplate $ZoneTemplate -WhatIf -Verbose

    # Apply template
    Write-Host "`nApplying $ZoneTemplate template..." -ForegroundColor Yellow
    $applyResult = Set-FsiMimeConfig -DataverseUrl $DataverseUrl -AccessToken $AccessToken -ZoneTemplate $ZoneTemplate

    # Validate compliance
    $zoneNum = [int]$ZoneTemplate[-1].ToString()
    Write-Host "`nValidating compliance..." -ForegroundColor Yellow
    $validation = Test-FsiMimeCompliance -DataverseUrl $DataverseUrl -AccessToken $AccessToken -Zone $zoneNum -IncludeEvidence

    $result = [PSCustomObject]@{
        Environment     = $DataverseUrl
        ZoneTemplate    = $ZoneTemplate
        Applied         = $applyResult.Applied
        Compliant       = $validation.IsCompliant
        PassedChecks    = $validation.Summary.PassCount
        FailedChecks    = $validation.Summary.FailCount
        EvidenceHash    = $validation.EvidenceHash
        Timestamp       = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    }

    # Output results
    switch ($OutputFormat) {
        "Table" { $result | Format-Table -AutoSize }
        "JSON"  { $result | ConvertTo-Json -Depth 3 }
        "CSV"   { $result | ConvertTo-Csv -NoTypeInformation }
    }

    # Export to file if OutputPath specified
    if ($OutputPath) {
        switch ($OutputFormat) {
            "Table" { $result | Format-Table -AutoSize | Out-File -FilePath $OutputPath }
            "JSON"  { $result | ConvertTo-Json -Depth 3 | Out-File -FilePath $OutputPath }
            "CSV"   { $result | Export-Csv -Path $OutputPath -NoTypeInformation }
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
