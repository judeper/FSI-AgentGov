<#
.SYNOPSIS
    Remediates Power Platform environment inactivity timeout settings via BAP Admin API.

.DESCRIPTION
    PATCHes inactivity timeout configuration on a specified Power Platform environment
    using the BAP Admin API privacy settings endpoint. Supports policy-driven maximum
    durations for US financial services governance zones.

    Execution flow:
    1. Authenticate via Azure AD (Get-AzAccessToken)
    2. GET current privacy settings for the target environment
    3. PATCH inactivity timeout configuration (enable + set durations)
    4. Re-GET settings to verify the PATCH was applied correctly
    5. Optionally write a remediation audit record to Dataverse

    The script uses a GET-PATCH-GET pattern: read current state, apply change,
    then re-read to verify. This supports audit trail requirements for US FSI
    regulatory frameworks including GLBA 501(b), SOX 302, and FINRA 4511.

    Zone-based duration guidance:
    - Zone 1 (Personal Productivity): Optional; recommended ≤120 minutes if enabled
    - Zone 2 (Team Collaboration): Required, maximum 120 minutes
    - Zone 3 (Enterprise Managed): Required, maximum 60 minutes

.PARAMETER EnvironmentName
    Mandatory. The canonical Power Platform Environment Name (GUID-like identifier
    returned by Get-AdminPowerAppEnvironment). This is NOT the display name.

.PARAMETER TimeoutDuration
    Inactivity timeout duration in minutes. Valid range: 5-120. Default: 120.

.PARAMETER WarningDuration
    Warning notification duration in minutes before timeout. Valid range: 1-30. Default: 5.

.PARAMETER DataverseUrl
    Optional. Dataverse environment URL for writing remediation audit records
    to fsi_inactivitytimeoutcompliances table. When omitted, no audit record is written.
    Example: https://org12345.crm.dynamics.com/

.PARAMETER OutputFormat
    Output format for results. Valid values: Table, JSON, Object. Default: Object.

.PARAMETER OutputPath
    Optional file path to export JSON results. When omitted, results display to console only.

.PARAMETER IncludeEvidence
    When specified, computes SHA-256 integrity hash over results for evidence packaging.

.EXAMPLE
    .\Set-InactivityTimeout.ps1 -EnvironmentName 'e1234567-89ab-cdef-0123-456789abcdef'

    Enables inactivity timeout with default 120-minute duration and 5-minute warning.

.EXAMPLE
    .\Set-InactivityTimeout.ps1 -EnvironmentName 'e1234567-89ab-cdef-0123-456789abcdef' -TimeoutDuration 60 -WarningDuration 10

    Sets 60-minute timeout with 10-minute warning (Zone 3 configuration).

.EXAMPLE
    .\Set-InactivityTimeout.ps1 -EnvironmentName 'e1234567-89ab-cdef-0123-456789abcdef' -WhatIf

    Shows current vs target configuration without applying changes.

.EXAMPLE
    .\Set-InactivityTimeout.ps1 -EnvironmentName 'e1234567-89ab-cdef-0123-456789abcdef' -DataverseUrl 'https://org12345.crm.dynamics.com/' -IncludeEvidence -OutputFormat JSON -OutputPath .\evidence\timeout-remediation.json

    Full remediation with Dataverse audit record, SHA-256 evidence hash, and JSON export.

.OUTPUTS
    PSCustomObject with Metadata, Applied, PreviousConfig, NewConfig, Verified, and AuditRecord properties.

.NOTES
    Part of the FSI Agent Governance — Inactivity Timeout Enforcement (Control 2.22).
    Regulatory alignment: GLBA 501(b), SOX 302, FINRA 4511, NIST 800-53 AC-11/AC-12.
    Version: 1.0.0
    Requires: Az.Accounts module for Get-AzAccessToken (Connect-AzAccount session).
#>

#Requires -Version 7.0

[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(Mandatory)]
    [ValidateNotNullOrEmpty()]
    [string]$EnvironmentName,

    [Parameter()]
    [ValidateRange(5, 120)]
    [int]$TimeoutDuration = 120,

    [Parameter()]
    [ValidateRange(1, 30)]
    [int]$WarningDuration = 5,

    [Parameter()]
    [string]$DataverseUrl,

    [Parameter()]
    [ValidateSet('Table', 'JSON', 'Object')]
    [string]$OutputFormat = 'Object',

    [Parameter()]
    [string]$OutputPath,

    [Parameter()]
    [switch]$IncludeEvidence
)

$ErrorActionPreference = 'Stop'
$startTime = [DateTime]::UtcNow

# ─── Banner ───────────────────────────────────────────────────────────
Write-Host "`n╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host   "║  FSI Agent Governance — Inactivity Timeout Remediation ║" -ForegroundColor Cyan
Write-Host   "╚══════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# ─── Helper Functions ─────────────────────────────────────────────────

function Get-BapApiToken {
    <#
    .SYNOPSIS
        Acquires a BAP Admin API access token via Azure AD.
    #>
    [CmdletBinding()]
    param()
    try {
        $tokenResult = Get-AzAccessToken -ResourceUrl "https://api.bap.microsoft.com" -ErrorAction Stop
        # Handle both Az.Accounts 2.x (.Token as string) and 3.x+ (.Token as SecureString)
        if ($tokenResult.Token -is [securestring]) {
            return $tokenResult.Token | ConvertFrom-SecureString -AsPlainText
        }
        return $tokenResult.Token
    }
    catch {
        throw "Failed to acquire BAP API token. Ensure you are signed in via Connect-AzAccount. Error: $($_.Exception.Message)"
    }
}

function Invoke-BapApi {
    <#
    .SYNOPSIS
        Invokes a BAP Admin API REST call with optional request body.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Uri,

        [Parameter(Mandatory)]
        [string]$Token,

        [Parameter()]
        [ValidateSet('GET', 'PATCH')]
        [string]$Method = 'GET',

        [Parameter()]
        [hashtable]$Body
    )
    $headers = @{
        Authorization  = "Bearer $Token"
        'Content-Type' = 'application/json'
    }
    $params = @{
        Uri         = $Uri
        Method      = $Method
        Headers     = $headers
        ErrorAction = 'Stop'
    }
    if ($Body -and $Method -eq 'PATCH') {
        $params['Body'] = ($Body | ConvertTo-Json -Depth 10 -Compress)
    }
    try {
        $response = Invoke-RestMethod @params
        return $response
    }
    catch {
        $statusCode = $null
        if ($_.Exception.Response) {
            $statusCode = [int]$_.Exception.Response.StatusCode
        }
        switch ($statusCode) {
            401 { throw "BAP API returned 401 Unauthorized. Token may be expired. Re-authenticate with Connect-AzAccount and retry." }
            403 { throw "BAP API returned 403 Forbidden. Insufficient permissions. Requires Power Platform Admin or Global Admin role." }
            404 { throw "BAP API returned 404 Not Found. Environment '$EnvironmentName' not found. Verify the Environment Name (not display name) via Get-AdminPowerAppEnvironment." }
            429 { throw "BAP API returned 429 Too Many Requests. Rate limited. Retry after a short delay." }
            default { throw "BAP API call failed ($Method $Uri): $($_.Exception.Message)" }
        }
    }
}

function Get-DataverseToken {
    <#
    .SYNOPSIS
        Acquires a Dataverse access token for audit record writing.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$ResourceUrl
    )
    try {
        $tokenResult = Get-AzAccessToken -ResourceUrl $ResourceUrl -ErrorAction Stop
        # Handle both Az.Accounts 2.x (.Token as string) and 3.x+ (.Token as SecureString)
        if ($tokenResult.Token -is [securestring]) {
            return $tokenResult.Token | ConvertFrom-SecureString -AsPlainText
        }
        return $tokenResult.Token
    }
    catch {
        throw "Failed to acquire Dataverse token for $ResourceUrl. Ensure you are signed in via Connect-AzAccount. Error: $($_.Exception.Message)"
    }
}

function Invoke-DataverseApi {
    <#
    .SYNOPSIS
        Invokes a Dataverse Web API call with OData 4.0 headers.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Uri,

        [Parameter(Mandatory)]
        [string]$Token,

        [Parameter()]
        [ValidateSet('GET', 'POST')]
        [string]$Method = 'GET',

        [Parameter()]
        [hashtable]$Body
    )
    $headers = @{
        Authorization      = "Bearer $Token"
        'Content-Type'     = 'application/json'
        'OData-MaxVersion' = '4.0'
        'OData-Version'    = '4.0'
        'Prefer'           = 'return=representation'
    }
    $params = @{
        Uri         = $Uri
        Method      = $Method
        Headers     = $headers
        ErrorAction = 'Stop'
    }
    if ($Body -and $Method -eq 'POST') {
        $params['Body'] = ($Body | ConvertTo-Json -Depth 10 -Compress)
    }
    $response = Invoke-RestMethod @params
    return $response
}

function Write-OutputResult {
    <#
    .SYNOPSIS
        Handles OutputFormat switch and optional OutputPath export.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [PSCustomObject]$Result,

        [Parameter(Mandatory)]
        [ValidateSet('Table', 'JSON', 'Object')]
        [string]$OutputFormat,

        [Parameter()]
        [string]$OutputPath
    )
    switch ($OutputFormat) {
        'JSON' {
            $json = $Result | ConvertTo-Json -Depth 10
            if ($OutputPath) {
                $parentDir = Split-Path -Path $OutputPath -Parent
                if ($parentDir -and -not (Test-Path $parentDir)) {
                    New-Item -ItemType Directory -Path $parentDir -Force | Out-Null
                }
                $json | Out-File -FilePath $OutputPath -Encoding utf8
                Write-Verbose "Results exported to $OutputPath"
            }
            else {
                Write-Output $json
            }
        }
        'Table' {
            $Result | Format-Table -Property @(
                @{ Label = 'Environment'; Expression = { $_.Metadata.EnvironmentName } },
                'Applied',
                'Verified',
                @{ Label = 'PrevTimeout'; Expression = { $_.PreviousConfig.InactivityTimeoutInMinutes } },
                @{ Label = 'NewTimeout'; Expression = { $_.NewConfig.InactivityTimeoutInMinutes } }
            ) -AutoSize
            if ($OutputPath) {
                $parentDir = Split-Path -Path $OutputPath -Parent
                if ($parentDir -and -not (Test-Path $parentDir)) {
                    New-Item -ItemType Directory -Path $parentDir -Force | Out-Null
                }
                $Result | ConvertTo-Json -Depth 10 | Out-File -FilePath $OutputPath -Encoding utf8
                Write-Verbose "Results exported to $OutputPath"
            }
        }
        'Object' {
            Write-Output $Result
        }
    }
}

# ─── Step 1: Authenticate ─────────────────────────────────────────────
Write-Host "  Authenticating to BAP Admin API..." -ForegroundColor Gray
$bapToken = Get-BapApiToken
Write-Verbose "BAP API token acquired"

# ─── Step 2: GET current privacy settings ──────────────────────────────
$privacyUri = "https://api.bap.microsoft.com/providers/Microsoft.BusinessAppPlatform/scopes/admin/environments/$EnvironmentName/settings/privacy?api-version=2021-04-01"

Write-Host "  Reading current privacy settings for $EnvironmentName..." -ForegroundColor Gray
$currentResponse = Invoke-BapApi -Uri $privacyUri -Token $bapToken -Method GET

$previousConfig = [PSCustomObject]@{
    InactivityTimeoutEnabled   = $currentResponse.properties.InactivityTimeoutEnabled
    InactivityTimeoutInMinutes = $currentResponse.properties.InactivityTimeoutInMinutes
    InactivityWarningInMinutes = $currentResponse.properties.InactivityWarningInMinutes
}

Write-Verbose "Current settings — Enabled: $($previousConfig.InactivityTimeoutEnabled), Timeout: $($previousConfig.InactivityTimeoutInMinutes) min, Warning: $($previousConfig.InactivityWarningInMinutes) min"

# ─── Step 3: WhatIf preview ───────────────────────────────────────────
if (-not $PSCmdlet.ShouldProcess($EnvironmentName, "Set inactivity timeout to $TimeoutDuration min with $WarningDuration min warning")) {
    Write-Verbose "WhatIf: Current InactivityTimeoutEnabled   = $($previousConfig.InactivityTimeoutEnabled)"
    Write-Verbose "WhatIf: Target  InactivityTimeoutEnabled   = True"
    Write-Verbose "WhatIf: Current InactivityTimeoutInMinutes = $($previousConfig.InactivityTimeoutInMinutes)"
    Write-Verbose "WhatIf: Target  InactivityTimeoutInMinutes = $TimeoutDuration"
    Write-Verbose "WhatIf: Current InactivityWarningInMinutes = $($previousConfig.InactivityWarningInMinutes)"
    Write-Verbose "WhatIf: Target  InactivityWarningInMinutes = $WarningDuration"

    $duration = ([DateTime]::UtcNow - $startTime).TotalSeconds
    $result = [PSCustomObject]@{
        Metadata = [PSCustomObject]@{
            Timestamp       = $startTime
            ScriptVersion   = '1.0.0'
            EnvironmentName = $EnvironmentName
            DurationSeconds = [math]::Round($duration, 2)
            IntegrityHash   = $null
        }
        Applied        = $false
        PreviousConfig = $previousConfig
        NewConfig      = $null
        Verified       = $false
        AuditRecord    = $null
    }

    Write-OutputResult -Result $result -OutputFormat $OutputFormat -OutputPath $OutputPath
    return
}

# ─── Step 4: PATCH privacy settings ───────────────────────────────────
Write-Host "  Applying inactivity timeout: $TimeoutDuration min (warning: $WarningDuration min)..." -ForegroundColor Gray

$patchBody = @{
    properties = @{
        InactivityTimeoutEnabled   = $true
        InactivityTimeoutInMinutes = $TimeoutDuration
        InactivityWarningInMinutes = $WarningDuration
    }
}

$null = Invoke-BapApi -Uri $privacyUri -Token $bapToken -Method PATCH -Body $patchBody

Write-Host "  PATCH applied successfully" -ForegroundColor Green

# ─── Step 5: Verify PATCH (re-GET) ────────────────────────────────────
Write-Host "  Verifying applied settings..." -ForegroundColor Gray

$verified = $false
try {
    $verifyResponse = Invoke-BapApi -Uri $privacyUri -Token $bapToken -Method GET

    $newConfig = [PSCustomObject]@{
        InactivityTimeoutEnabled   = $verifyResponse.properties.InactivityTimeoutEnabled
        InactivityTimeoutInMinutes = $verifyResponse.properties.InactivityTimeoutInMinutes
        InactivityWarningInMinutes = $verifyResponse.properties.InactivityWarningInMinutes
    }

    $verified = (
        $newConfig.InactivityTimeoutEnabled -eq $true -and
        $newConfig.InactivityTimeoutInMinutes -eq $TimeoutDuration -and
        $newConfig.InactivityWarningInMinutes -eq $WarningDuration
    )

    if ($verified) {
        Write-Host "  Verified: settings match target configuration" -ForegroundColor Green
    }
    else {
        Write-Warning "Verification mismatch — post-PATCH values differ from target. Enabled=$($newConfig.InactivityTimeoutEnabled), Timeout=$($newConfig.InactivityTimeoutInMinutes), Warning=$($newConfig.InactivityWarningInMinutes)"
    }
}
catch {
    Write-Warning "Verification GET failed (PATCH may have succeeded): $($_.Exception.Message)"
    $newConfig = [PSCustomObject]@{
        InactivityTimeoutEnabled   = $true
        InactivityTimeoutInMinutes = $TimeoutDuration
        InactivityWarningInMinutes = $WarningDuration
    }
}

# ─── Step 6: Optionally write Dataverse audit record ──────────────────
$auditRecordId = $null

if ($DataverseUrl) {
    Write-Host "  Writing remediation audit record to Dataverse..." -ForegroundColor Gray
    try {
        # Normalize URL
        $dvUrl = $DataverseUrl.TrimEnd('/')

        $dvToken = Get-DataverseToken -ResourceUrl $dvUrl

        $scanTimestamp = Get-Date -Format 'o'
        $auditPayload = @{
            fsi_name                     = "$EnvironmentName - $($scanTimestamp.Substring(0,19)) - Remediated"
            fsi_environmentid            = $EnvironmentName
            fsi_environmentname          = $EnvironmentName
            fsi_inactivitytimeoutenabled = $true
            fsi_timeoutduration          = $TimeoutDuration
            fsi_compliancestatus         = 0  # Compliant (remediated) — matches fsi_ITE_compliancestatus option set
            fsi_lastscandate             = $scanTimestamp
            fsi_notes                    = "Remediated by Set-InactivityTimeout.ps1. Before: Enabled=$($previousConfig.InactivityTimeoutEnabled), Duration=$($previousConfig.InactivityTimeoutInMinutes). After: Enabled=True, Duration=$TimeoutDuration, Warning=$WarningDuration."
        }

        $dvResponse = Invoke-DataverseApi `
            -Uri "$dvUrl/api/data/v9.2/fsi_inactivitytimeoutcompliances" `
            -Token $dvToken `
            -Method POST `
            -Body $auditPayload

        $auditRecordId = $dvResponse.fsi_inactivitytimeoutcomplianceid
        Write-Host "  Audit record written: $auditRecordId" -ForegroundColor Green
    }
    catch {
        Write-Warning "Dataverse audit record write failed (remediation succeeded): $($_.Exception.Message)"
    }
}

# ─── Step 7: Build result object ──────────────────────────────────────
$duration = ([DateTime]::UtcNow - $startTime).TotalSeconds

$result = [PSCustomObject]@{
    Metadata = [PSCustomObject]@{
        Timestamp       = $startTime
        ScriptVersion   = '1.0.0'
        EnvironmentName = $EnvironmentName
        DurationSeconds = [math]::Round($duration, 2)
        IntegrityHash   = $null
    }
    Applied        = $true
    PreviousConfig = $previousConfig
    NewConfig      = $newConfig
    Verified       = $verified
    AuditRecord    = $auditRecordId
}

# SHA-256 evidence hash
if ($IncludeEvidence) {
    $resultsJson = $result | ConvertTo-Json -Depth 10 -Compress
    $hashBytes = [System.Security.Cryptography.SHA256]::Create().ComputeHash(
        [System.Text.Encoding]::UTF8.GetBytes($resultsJson)
    )
    $result.Metadata.IntegrityHash = [BitConverter]::ToString($hashBytes) -replace '-'
}

# ─── Step 8: Console summary and output ───────────────────────────────
Write-Host "`n── Remediation Summary ─────────────────────────────────────" -ForegroundColor Cyan
Write-Host "  Environment:     $EnvironmentName"
Write-Host "  Applied:         $($result.Applied)" -ForegroundColor $(if ($result.Applied) { 'Green' } else { 'Yellow' })
Write-Host "  Verified:        $($result.Verified)" -ForegroundColor $(if ($result.Verified) { 'Green' } else { 'Yellow' })
Write-Host "  Prev Timeout:    $($previousConfig.InactivityTimeoutInMinutes) min (Enabled: $($previousConfig.InactivityTimeoutEnabled))"
Write-Host "  New Timeout:     $($newConfig.InactivityTimeoutInMinutes) min (Warning: $($newConfig.InactivityWarningInMinutes) min)"
if ($auditRecordId) {
    Write-Host "  Audit Record:    $auditRecordId" -ForegroundColor Green
}
if ($result.Metadata.IntegrityHash) {
    Write-Host "  Evidence Hash:   $($result.Metadata.IntegrityHash)" -ForegroundColor Gray
}
Write-Host "────────────────────────────────────────────────────────────`n" -ForegroundColor Cyan

Write-OutputResult -Result $result -OutputFormat $OutputFormat -OutputPath $OutputPath
