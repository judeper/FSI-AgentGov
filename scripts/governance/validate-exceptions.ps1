#Requires -Version 7.0
<#
.SYNOPSIS
    Validates MIME type exceptions against environment configuration and zone templates.

.DESCRIPTION
    Compares a Dataverse environment's current MIME configuration against the zone
    baseline template and an exception register (CSV). Identifies:
      - MIME types covered by the zone template (compliant)
      - MIME types covered by active exceptions (exception-covered)
      - MIME types present in the environment but not in template or exceptions (unauthorized)
      - Expired or expiring exceptions requiring review

    Uses the FsiMimeControl module to read environment configuration and zone templates.
    Follows the [PASS]/[FAIL]/[WARN] output pattern consistent with other FSI governance scripts.

.PARAMETER DataverseUrl
    Dataverse environment URL (e.g., https://org.crm.dynamics.com).

.PARAMETER AccessToken
    Optional OAuth2 bearer token. If omitted, falls back to Get-AzAccessToken via the
    FsiMimeControl module's built-in token resolution.

.PARAMETER ExceptionRegisterPath
    Path to the MIME type exception register CSV file.
    Default: ./scripts/governance/mime-type-exceptions.csv

.PARAMETER ZoneTemplate
    Zone template to validate against. Valid values: zone1, zone2, zone3.

.PARAMETER OutputFormat
    Output format for results. Valid values: Table, JSON, Object. Default: Table.

.PARAMETER OutputPath
    Optional file path to export results. When omitted, results display to console only.

.PARAMETER IncludeEvidence
    When specified, computes SHA-256 integrity hash over results for evidence packaging.

.EXAMPLE
    .\validate-exceptions.ps1 -DataverseUrl https://org.crm.dynamics.com -ZoneTemplate zone2

    Validates the environment's MIME configuration against Zone 2 template and default exception register.

.EXAMPLE
    .\validate-exceptions.ps1 -DataverseUrl https://org.crm.dynamics.com -ZoneTemplate zone3 -OutputFormat JSON -OutputPath .\evidence\exception-validation.json -IncludeEvidence

    Validates Zone 3 compliance, exports JSON with SHA-256 evidence hash.

.EXAMPLE
    .\validate-exceptions.ps1 -DataverseUrl https://org.crm.dynamics.com -ZoneTemplate zone2 -ExceptionRegisterPath .\custom-exceptions.csv -OutputFormat Object

    Validates using a custom exception register and returns PowerShell objects.

.OUTPUTS
    PSCustomObject with Metadata, Summary, Results, ExpiredExceptions, and ExpiringExceptions properties.

.NOTES
    Part of the FSI Agent Governance — MIME Type Restrictions (Control 1.25).
    Version: 1.0.0
    Requires: PowerShell 7.0+, FsiMimeControl module
#>

[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(Mandatory)]
    [ValidateNotNullOrEmpty()]
    [string]$DataverseUrl,

    [Parameter()]
    [string]$AccessToken,

    [Parameter()]
    [ValidateScript({ Test-Path $_ -PathType Leaf })]
    [string]$ExceptionRegisterPath = (Join-Path $PSScriptRoot 'mime-type-exceptions.csv'),

    [Parameter(Mandatory)]
    [ValidateSet('zone1', 'zone2', 'zone3')]
    [string]$ZoneTemplate,

    [Parameter()]
    [ValidateSet('Table', 'JSON', 'Object')]
    [string]$OutputFormat = 'Table',

    [Parameter()]
    [string]$OutputPath,

    [Parameter()]
    [switch]$IncludeEvidence
)

# ─── Banner ───────────────────────────────────────────────────────────
Write-Host "`n╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host   "║  FSI Agent Governance — MIME Exception Validator         ║" -ForegroundColor Cyan
Write-Host   "╚══════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

$ErrorActionPreference = 'Stop'
$startTime = [DateTime]::UtcNow

# ─── WhatIf Preview ──────────────────────────────────────────────────
if (-not $PSCmdlet.ShouldProcess("Dataverse: $DataverseUrl", "Validate MIME exceptions against $ZoneTemplate template")) {
    Write-Host "  [WhatIf] Would validate MIME configuration against $ZoneTemplate template" -ForegroundColor Yellow
    Write-Host "    Zone template:      $ZoneTemplate" -ForegroundColor Yellow
    Write-Host "    Exception register: $ExceptionRegisterPath" -ForegroundColor Yellow
    Write-Host "    Dataverse URL:      $DataverseUrl" -ForegroundColor Yellow
    return
}

# ─── Import FsiMimeControl Module ─────────────────────────────────────
$modulePath = Join-Path $PSScriptRoot 'FsiMimeControl.psm1'
if (-not (Test-Path $modulePath)) {
    throw "FsiMimeControl module not found at $modulePath. Ensure the module is present in the governance scripts directory."
}
Import-Module $modulePath -Force

# ─── Load Zone Template ──────────────────────────────────────────────
$templatePath = Join-Path $PSScriptRoot "mime-templates/$ZoneTemplate.json"
if (-not (Test-Path $templatePath)) {
    throw "Zone template not found at $templatePath. Verify the mime-templates directory contains $ZoneTemplate.json."
}
$template = Get-Content -Path $templatePath -Raw | ConvertFrom-Json
$allowedBaseline = @($template.allowedMimeTypes)
Write-Verbose "Loaded $ZoneTemplate template: $($allowedBaseline.Count) allowed MIME types"

# ─── Read Environment Configuration ──────────────────────────────────
Write-Host "  Reading MIME configuration from $DataverseUrl..." -ForegroundColor White

$getMimeParams = @{ DataverseUrl = $DataverseUrl }
if ($AccessToken) { $getMimeParams['AccessToken'] = $AccessToken }
$envConfig = Get-FsiMimeConfig @getMimeParams

# Collect all MIME types present in the environment (allowed + any additional)
$envMimeTypes = @()
if ($envConfig.AllowedMimeTypes) {
    $envMimeTypes += $envConfig.AllowedMimeTypes
}
# Also consider blocked MIME types for completeness
$envBlockedMimeTypes = @()
if ($envConfig.BlockedMimeTypes) {
    $envBlockedMimeTypes = $envConfig.BlockedMimeTypes
}

Write-Verbose "Environment has $($envMimeTypes.Count) allowed MIME types and $($envBlockedMimeTypes.Count) blocked MIME types"

# ─── Import Exception Register ───────────────────────────────────────
Write-Host "  Loading exception register from $ExceptionRegisterPath..." -ForegroundColor White

$allExceptions = Import-Csv -Path $ExceptionRegisterPath -Encoding UTF8

# Extract environment ID from Dataverse URL for matching
$envIdFromUrl = $DataverseUrl.TrimEnd('/')

# Filter active exceptions matching this environment (case-insensitive Status comparison)
$activeExceptions = $allExceptions | Where-Object {
    $_.Status -ieq 'Active' -and (
        $_.EnvironmentId -ieq $envIdFromUrl -or
        $_.EnvironmentId -ieq $envConfig.OrganizationId -or
        [string]::IsNullOrWhiteSpace($_.EnvironmentId)
    )
}

if ($activeExceptions.Count -eq 0 -and ($allExceptions | Where-Object { $_.Status -ieq 'Active' }).Count -gt 0) {
    Write-Warning "No exceptions matched this environment. CSV EnvironmentId values may not match the Dataverse URL or Organization ID. URL: $envIdFromUrl, OrgId: $($envConfig.OrganizationId)"
}

Write-Verbose "Found $($allExceptions.Count) total exceptions, $($activeExceptions.Count) active for this environment"

# Build lookup of active exception MIME types (case-insensitive)
$exceptionMimeTypes = [System.Collections.Generic.Dictionary[string,object]]::new(
    [System.StringComparer]::OrdinalIgnoreCase)
foreach ($exc in $activeExceptions) {
    $exceptionMimeTypes[$exc.MimeType] = $exc
}

# ─── Validate MIME Types ─────────────────────────────────────────────
Write-Host "  Validating MIME types against $ZoneTemplate template and exception register..." -ForegroundColor White

$results = [System.Collections.Generic.List[PSCustomObject]]::new()

# Zone 1 templates define no allowlist — all allowed MIME types are acceptable
$templateHasAllowlist = $allowedBaseline.Count -gt 0

# Check each MIME type in the environment's allowed list against template + exceptions
foreach ($mime in $envMimeTypes) {
    $inTemplate = $templateHasAllowlist -and ($mime -iin $allowedBaseline)
    $inException = $exceptionMimeTypes.ContainsKey($mime)

    if (-not $templateHasAllowlist) {
        # Zone template does not define an allowlist — all allowed MIME types are compliant
        $results.Add([PSCustomObject]@{
            MimeType       = $mime
            Source         = 'Template'
            ExceptionId    = $null
            Status         = 'Compliant'
            ExpirationDate = $null
            Action         = 'OK'
        })
    }
    elseif ($inTemplate) {
        $results.Add([PSCustomObject]@{
            MimeType       = $mime
            Source         = 'Template'
            ExceptionId    = $null
            Status         = 'Compliant'
            ExpirationDate = $null
            Action         = 'OK'
        })
    }
    elseif ($inException) {
        $exc = $exceptionMimeTypes[$mime]
        $expDate = if ($exc.ExpirationDate) { [datetime]::Parse($exc.ExpirationDate, [System.Globalization.CultureInfo]::InvariantCulture) } else { $null }
        $now = [DateTime]::UtcNow

        $action = 'OK'
        $status = 'Exception-Covered'
        if ($expDate -and $expDate -lt $now) {
            $action = 'Expired'
            $status = 'Expired'
        }
        elseif ($expDate -and ($expDate - $now).TotalDays -le 30) {
            $action = 'ReviewNeeded'
            $status = 'ExpiringSoon'
        }

        $results.Add([PSCustomObject]@{
            MimeType       = $mime
            Source         = 'Exception'
            ExceptionId    = $exc.ExceptionId
            Status         = $status
            ExpirationDate = $exc.ExpirationDate
            Action         = $action
        })
    }
    else {
        $results.Add([PSCustomObject]@{
            MimeType       = $mime
            Source         = 'Unauthorized'
            ExceptionId    = $null
            Status         = 'Unauthorized'
            ExpirationDate = $null
            Action         = 'Unauthorized'
        })
    }
}

# ─── Check for Expired and Expiring Exceptions ───────────────────────
$now = [DateTime]::UtcNow
$expiredExceptions = [System.Collections.Generic.List[PSCustomObject]]::new()
$expiringExceptions = [System.Collections.Generic.List[PSCustomObject]]::new()

foreach ($exc in $allExceptions) {
    # Check ReviewDate
    if (-not [string]::IsNullOrWhiteSpace($exc.ReviewDate)) {
        try {
            $reviewDate = [datetime]::Parse($exc.ReviewDate, [System.Globalization.CultureInfo]::InvariantCulture)
            if ($reviewDate -lt $now -and $exc.Status -ieq 'Active') {
                $expiredExceptions.Add([PSCustomObject]@{
                    ExceptionId = $exc.ExceptionId
                    MimeType    = $exc.MimeType
                    Field       = 'ReviewDate'
                    Date        = $exc.ReviewDate
                    Status      = $exc.Status
                    Message     = "Review date has passed — exception requires re-evaluation"
                })
            }
            elseif ($reviewDate -gt $now -and ($reviewDate - $now).TotalDays -le 30 -and $exc.Status -ieq 'Active') {
                $expiringExceptions.Add([PSCustomObject]@{
                    ExceptionId = $exc.ExceptionId
                    MimeType    = $exc.MimeType
                    Field       = 'ReviewDate'
                    Date        = $exc.ReviewDate
                    DaysRemaining = [math]::Floor(($reviewDate - $now).TotalDays)
                    Message     = "Review date approaching — schedule re-evaluation"
                })
            }
        }
        catch {
            Write-Warning "Could not parse ReviewDate '$($exc.ReviewDate)' for exception $($exc.ExceptionId)"
        }
    }

    # Check ExpirationDate
    if (-not [string]::IsNullOrWhiteSpace($exc.ExpirationDate)) {
        try {
            $expDate = [datetime]::Parse($exc.ExpirationDate, [System.Globalization.CultureInfo]::InvariantCulture)
            if ($expDate -lt $now -and $exc.Status -ieq 'Active') {
                $expiredExceptions.Add([PSCustomObject]@{
                    ExceptionId = $exc.ExceptionId
                    MimeType    = $exc.MimeType
                    Field       = 'ExpirationDate'
                    Date        = $exc.ExpirationDate
                    Status      = $exc.Status
                    Message     = "Exception has expired — MIME type allowance should be revoked or renewed"
                })
            }
            elseif ($expDate -gt $now -and ($expDate - $now).TotalDays -le 30 -and $exc.Status -ieq 'Active') {
                $expiringExceptions.Add([PSCustomObject]@{
                    ExceptionId = $exc.ExceptionId
                    MimeType    = $exc.MimeType
                    Field       = 'ExpirationDate'
                    Date        = $exc.ExpirationDate
                    DaysRemaining = [math]::Floor(($expDate - $now).TotalDays)
                    Message     = "Exception expiring soon — initiate renewal or revocation"
                })
            }
        }
        catch {
            Write-Warning "Could not parse ExpirationDate '$($exc.ExpirationDate)' for exception $($exc.ExceptionId)"
        }
    }
}

# ─── Aggregate Counts ────────────────────────────────────────────────
$compliantCount    = ($results | Where-Object { $_.Action -eq 'OK' -and $_.Source -eq 'Template' }).Count
$exceptionCount    = ($results | Where-Object { $_.Source -eq 'Exception' }).Count
$unauthorizedCount = ($results | Where-Object { $_.Action -eq 'Unauthorized' }).Count
$expiredCount      = $expiredExceptions.Count
$expiringCount     = $expiringExceptions.Count

$duration = ([DateTime]::UtcNow - $startTime).TotalSeconds

$overallStatus = if ($unauthorizedCount -gt 0 -or $expiredCount -gt 0) {
    'FAIL'
} elseif ($expiringCount -gt 0) {
    'WARN'
} else {
    'PASS'
}

# ─── Build Result Object ─────────────────────────────────────────────
$validationResult = [PSCustomObject]@{
    Metadata = [PSCustomObject]@{
        DataverseUrl          = $DataverseUrl
        ZoneTemplate          = $ZoneTemplate
        ExceptionRegisterPath = $ExceptionRegisterPath
        ValidatedAt           = $startTime
        ScriptVersion         = '1.0.0'
        DurationSeconds       = [math]::Round($duration, 2)
        IntegrityHash         = $null
    }
    Summary = [PSCustomObject]@{
        OverallStatus    = $overallStatus
        TotalMimeTypes   = $results.Count
        Compliant        = $compliantCount
        ExceptionCovered = $exceptionCount
        Unauthorized     = $unauthorizedCount
        Expired          = $expiredCount
        ExpiringSoon     = $expiringCount
    }
    Results             = $results.ToArray()
    ExpiredExceptions   = $expiredExceptions.ToArray()
    ExpiringExceptions  = $expiringExceptions.ToArray()
}

# ─── SHA-256 Evidence Hash ────────────────────────────────────────────
if ($IncludeEvidence) {
    $resultsJson = $validationResult | ConvertTo-Json -Depth 10 -Compress
    $hashBytes = [System.Security.Cryptography.SHA256]::Create().ComputeHash(
        [System.Text.Encoding]::UTF8.GetBytes($resultsJson)
    )
    $validationResult.Metadata.IntegrityHash = [BitConverter]::ToString($hashBytes) -replace '-'
}

# ─── Console Summary ─────────────────────────────────────────────────
$statusColor = switch ($overallStatus) {
    'PASS' { 'Green' }
    'WARN' { 'Yellow' }
    'FAIL' { 'Red' }
}

Write-Host "`n── MIME Exception Validation Summary ───────────────────────" -ForegroundColor Cyan
Write-Host "  Overall:           [$overallStatus]" -ForegroundColor $statusColor
Write-Host "  Zone Template:     $ZoneTemplate"
Write-Host "  MIME Types Checked: $($results.Count)"
Write-Host "  Compliant:         $compliantCount" -ForegroundColor $(if ($compliantCount -gt 0) { 'Green' } else { 'White' })
Write-Host "  Exception-Covered: $exceptionCount" -ForegroundColor $(if ($exceptionCount -gt 0) { 'Cyan' } else { 'White' })
Write-Host "  Unauthorized:      $unauthorizedCount" -ForegroundColor $(if ($unauthorizedCount -gt 0) { 'Red' } else { 'Green' })
Write-Host "  Expired:           $expiredCount" -ForegroundColor $(if ($expiredCount -gt 0) { 'Red' } else { 'Green' })
Write-Host "  Expiring Soon:     $expiringCount" -ForegroundColor $(if ($expiringCount -gt 0) { 'Yellow' } else { 'Green' })
Write-Host "  Duration:          $([math]::Round($duration, 2))s"
if ($IncludeEvidence) {
    Write-Host "  Integrity Hash:    $($validationResult.Metadata.IntegrityHash)" -ForegroundColor DarkGray
}
Write-Host "────────────────────────────────────────────────────────────`n" -ForegroundColor Cyan

# Detail output for unauthorized items
if ($unauthorizedCount -gt 0) {
    Write-Host "  [FAIL] Unauthorized MIME types detected:" -ForegroundColor Red
    $results | Where-Object { $_.Action -eq 'Unauthorized' } | ForEach-Object {
        Write-Host "         - $($_.MimeType)" -ForegroundColor Red
    }
    Write-Host ""
}

if ($expiredCount -gt 0) {
    Write-Host "  [FAIL] Expired exceptions requiring action:" -ForegroundColor Red
    $expiredExceptions | ForEach-Object {
        Write-Host "         - $($_.ExceptionId): $($_.MimeType) ($($_.Field) = $($_.Date))" -ForegroundColor Red
    }
    Write-Host ""
}

if ($expiringCount -gt 0) {
    Write-Host "  [WARN] Exceptions approaching expiration:" -ForegroundColor Yellow
    $expiringExceptions | ForEach-Object {
        Write-Host "         - $($_.ExceptionId): $($_.MimeType) ($($_.DaysRemaining) days remaining)" -ForegroundColor Yellow
    }
    Write-Host ""
}

if ($overallStatus -eq 'PASS') {
    Write-Host "  [PASS] All MIME types are covered by zone template or active exceptions." -ForegroundColor Green
    Write-Host ""
}

# ─── Output ──────────────────────────────────────────────────────────
switch ($OutputFormat) {
    'JSON' {
        $json = $validationResult | ConvertTo-Json -Depth 10
        if ($OutputPath) {
            $parentDir = Split-Path -Path $OutputPath -Parent
            if ($parentDir -and -not (Test-Path $parentDir)) {
                New-Item -ItemType Directory -Path $parentDir -Force | Out-Null
            }
            $json | Out-File -FilePath $OutputPath -Encoding utf8
            Write-Host "  Results exported to $OutputPath" -ForegroundColor Green
        }
        else {
            Write-Output $json
        }
    }
    'Table' {
        $results | Format-Table -Property MimeType, Source, ExceptionId, Status, ExpirationDate, Action -AutoSize

        if ($OutputPath) {
            $parentDir = Split-Path -Path $OutputPath -Parent
            if ($parentDir -and -not (Test-Path $parentDir)) {
                New-Item -ItemType Directory -Path $parentDir -Force | Out-Null
            }
            $validationResult | ConvertTo-Json -Depth 10 | Out-File -FilePath $OutputPath -Encoding utf8
            Write-Host "  Results exported to $OutputPath" -ForegroundColor Green
        }
    }
    'Object' {
        Write-Output $validationResult
    }
}
