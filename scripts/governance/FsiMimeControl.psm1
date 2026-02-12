#Requires -Version 7.0
<#
.SYNOPSIS
    PowerShell module for zone-based MIME type configuration management in Dataverse environments.

.DESCRIPTION
    FsiMimeControl provides cmdlets to read, apply, and validate MIME type restrictions
    on Power Platform / Dataverse environments using the Organization entity Web API.
    Supports three governance zones with escalating security requirements:
      - Zone 1 (Personal Productivity): Microsoft default blocked extensions
      - Zone 2 (Team Collaboration): Extended blocks + MIME types + allowlist
      - Zone 3 (Enterprise Managed): Comprehensive blocks + strict allowlist + flags

    Cmdlets:
      - Get-FsiMimeConfig      Read current MIME configuration from Dataverse
      - Set-FsiMimeConfig      Apply zone template or custom configuration (with -WhatIf)
      - Test-FsiMimeCompliance  Validate environment against zone requirements

    Connection helpers:
      - Connect-FsiMimeDataverse  Establish module session with Dataverse
      - Get-FsiMimeConnection     Return current connection status

.NOTES
    Part of the FSI Agent Governance — MIME Type Restrictions (Control 1.25).
    Version: 1.0.0
    Requires: PowerShell 7.0+, Az.Accounts (recommended for token acquisition)
#>

$ErrorActionPreference = 'Stop'

# ─── Module State ─────────────────────────────────────────────────────
$script:DataverseUrl    = $null
$script:AccessToken     = $null
$script:Headers         = $null
$script:TemplateBasePath = Join-Path $PSScriptRoot 'mime-templates'

# ─── Banner ───────────────────────────────────────────────────────────
Write-Host "`n╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host   "║  FSI Agent Governance — MIME Type Configuration Module  ║" -ForegroundColor Cyan
Write-Host   "╚══════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# ═══════════════════════════════════════════════════════════════════════
# Internal Helpers
# ═══════════════════════════════════════════════════════════════════════

function Resolve-DataverseHeaders {
    <#
    .SYNOPSIS
        Resolves Dataverse URL and authorization headers from explicit parameters,
        module session, or Az.Accounts fallback.
    #>
    [CmdletBinding()]
    param(
        [Parameter()][string]$DataverseUrl,
        [Parameter()][string]$AccessToken
    )

    $url   = $null
    $token = $null

    # Priority 1: Explicit parameters
    if ($DataverseUrl) { $url = $DataverseUrl.TrimEnd('/') }
    if ($AccessToken)  { $token = $AccessToken }

    # Priority 2: Module session
    if (-not $url   -and $script:DataverseUrl)  { $url   = $script:DataverseUrl }
    if (-not $token -and $script:AccessToken)    { $token = $script:AccessToken }

    # Priority 3: Az.Accounts fallback
    if (-not $token -and $url) {
        try {
            $azToken = Get-AzAccessToken -ResourceUrl $url -ErrorAction Stop
            $token = $azToken.Token
            Write-Verbose "FsiMimeControl: Acquired token via Get-AzAccessToken"
        }
        catch {
            throw "No access token available. Provide -AccessToken, call Connect-FsiMimeDataverse, or authenticate with Connect-AzAccount. Error: $($_.Exception.Message)"
        }
    }

    if (-not $url) {
        throw "No Dataverse URL specified. Provide -DataverseUrl or call Connect-FsiMimeDataverse first."
    }

    $headers = @{
        'Authorization'    = "Bearer $token"
        'OData-MaxVersion' = '4.0'
        'OData-Version'    = '4.0'
        'Accept'           = 'application/json'
        'Prefer'           = 'return=representation'
    }

    return @{
        Url     = $url
        Headers = $headers
    }
}

function New-CheckResult {
    <#
    .SYNOPSIS
        Creates a standardized check result object for compliance validation.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$CheckId,
        [Parameter(Mandatory)][string]$Setting,
        [Parameter(Mandatory)][ValidateSet('Pass','Fail','Warning','Info')][string]$Status,
        [Parameter()][string]$Expected,
        [Parameter()][string]$Actual,
        [Parameter()][string]$Message
    )

    [PSCustomObject]@{
        CheckId  = $CheckId
        Setting  = $Setting
        Status   = $Status
        Expected = $Expected
        Actual   = $Actual
        Message  = $Message
    }
}

function Write-OutputResult {
    <#
    .SYNOPSIS
        Handles OutputFormat switch and optional OutputPath export.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][PSCustomObject]$Result,
        [Parameter(Mandatory)][ValidateSet('Table','JSON','Object')][string]$OutputFormat,
        [Parameter()][string]$OutputPath
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
            if ($Result.PSObject.Properties.Name -contains 'Checks') {
                $Result.Checks | Format-Table -Property CheckId, Setting, Status, Expected, Actual -AutoSize
            }
            else {
                $Result | Format-Table -AutoSize
            }

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

# ═══════════════════════════════════════════════════════════════════════
# Connection Management
# ═══════════════════════════════════════════════════════════════════════

function Connect-FsiMimeDataverse {
    <#
    .SYNOPSIS
        Establishes a module session with a Dataverse environment.

    .DESCRIPTION
        Sets module-scoped connection state (URL, access token, headers) and validates
        connectivity by querying the organizations endpoint. If no AccessToken is
        provided, attempts to acquire one via Get-AzAccessToken.

    .PARAMETER DataverseUrl
        The Dataverse environment URL (e.g., https://org.crm.dynamics.com).

    .PARAMETER AccessToken
        A valid OAuth2 bearer token for the Dataverse environment. If omitted,
        falls back to Get-AzAccessToken.

    .EXAMPLE
        Connect-FsiMimeDataverse -DataverseUrl 'https://org.crm.dynamics.com' -AccessToken $token

    .EXAMPLE
        Connect-FsiMimeDataverse -DataverseUrl 'https://org.crm.dynamics.com'
        # Uses Get-AzAccessToken for token acquisition
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$DataverseUrl,

        [Parameter()]
        [string]$AccessToken
    )

    $url = $DataverseUrl.TrimEnd('/')
    $token = $AccessToken

    # Attempt token acquisition if not provided
    if (-not $token) {
        try {
            $azToken = Get-AzAccessToken -ResourceUrl $url -ErrorAction Stop
            $token = $azToken.Token
            Write-Verbose "FsiMimeControl: Acquired token via Get-AzAccessToken"
        }
        catch {
            Write-Warning "FsiMimeControl: Failed to acquire token via Get-AzAccessToken — $($_.Exception.Message)"
            throw "No access token available. Provide -AccessToken or authenticate with Connect-AzAccount."
        }
    }

    $headers = @{
        'Authorization'    = "Bearer $token"
        'OData-MaxVersion' = '4.0'
        'OData-Version'    = '4.0'
        'Accept'           = 'application/json'
        'Prefer'           = 'return=representation'
    }

    # Validate connectivity
    $testUri = "$url/api/data/v9.2/organizations?`$select=organizationid"
    try {
        $null = Invoke-RestMethod -Uri $testUri -Headers $headers -Method Get
        Write-Verbose "FsiMimeControl: Connected to $url"
    }
    catch {
        Write-Warning "FsiMimeControl: Failed to connect to Dataverse — $($_.Exception.Message)"
        throw "Connection validation failed for $url. Verify URL and credentials."
    }

    # Store in module scope
    $script:DataverseUrl  = $url
    $script:AccessToken   = $token
    $script:Headers       = $headers

    Write-Host "  Connected to $url" -ForegroundColor Green
}

function Get-FsiMimeConnection {
    <#
    .SYNOPSIS
        Returns the current Dataverse connection status for the FsiMimeControl module.

    .EXAMPLE
        $conn = Get-FsiMimeConnection
        if ($conn.IsConnected) { Write-Host "Connected to $($conn.DataverseUrl)" }
    #>
    [CmdletBinding()]
    param()

    return [PSCustomObject]@{
        IsConnected  = ($null -ne $script:DataverseUrl)
        DataverseUrl = $script:DataverseUrl
        TokenExpiry  = $null  # Token introspection not available without JWT parsing
    }
}

# ═══════════════════════════════════════════════════════════════════════
# Cmdlet 1: Get-FsiMimeConfig
# ═══════════════════════════════════════════════════════════════════════

function Get-FsiMimeConfig {
    <#
    .SYNOPSIS
        Reads MIME type configuration from a Dataverse environment.

    .DESCRIPTION
        Queries the Organization entity via Dataverse Web API to retrieve blocked
        file extensions, blocked MIME types, and allowed MIME types (if available).
        Parses semicolon-separated Dataverse fields into PowerShell string arrays.

    .PARAMETER DataverseUrl
        The Dataverse environment URL. If omitted, uses the module session.

    .PARAMETER AccessToken
        OAuth2 bearer token. If omitted, uses the module session or Get-AzAccessToken.

    .PARAMETER OutputFormat
        Output format for results. Valid values: Table, JSON, Object. Default: Object.

    .PARAMETER OutputPath
        Optional file path to export JSON results.

    .EXAMPLE
        Get-FsiMimeConfig -DataverseUrl 'https://org.crm.dynamics.com' -AccessToken $token

    .EXAMPLE
        Connect-FsiMimeDataverse -DataverseUrl 'https://org.crm.dynamics.com' -AccessToken $token
        Get-FsiMimeConfig
    #>
    [CmdletBinding()]
    param(
        [Parameter()]
        [string]$DataverseUrl,

        [Parameter()]
        [string]$AccessToken,

        [Parameter()]
        [ValidateSet('Table', 'JSON', 'Object')]
        [string]$OutputFormat = 'Object',

        [Parameter()]
        [string]$OutputPath
    )

    $conn = Resolve-DataverseHeaders -DataverseUrl $DataverseUrl -AccessToken $AccessToken

    # Query Organization entity for MIME configuration
    $selectFields = 'organizationid,blockedattachments,blockedmimetypes'
    $uri = "$($conn.Url)/api/data/v9.2/organizations?`$select=$selectFields"

    try {
        $response = Invoke-RestMethod -Uri $uri -Headers $conn.Headers -Method Get
    }
    catch {
        throw "Failed to query Dataverse Organization entity: $($_.Exception.Message)"
    }

    $org = if ($response.value) { $response.value[0] } else { $response }
    $orgId = $org.organizationid

    # Parse semicolon-separated fields into arrays
    $blockedExtensions = if (-not [string]::IsNullOrWhiteSpace($org.blockedattachments)) {
        @($org.blockedattachments -split ';' | ForEach-Object { $_.Trim().ToLower() } | Where-Object { $_ -ne '' })
    } else { @() }

    $blockedMimeTypes = if (-not [string]::IsNullOrWhiteSpace($org.blockedmimetypes)) {
        @($org.blockedmimetypes -split ';' | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne '' })
    } else { @() }

    # Attempt to read allowedmimetypes (may not exist on all environments)
    $allowedMimeTypes = $null
    try {
        $allowUri = "$($conn.Url)/api/data/v9.2/organizations?`$select=allowedmimetypes"
        $allowResponse = Invoke-RestMethod -Uri $allowUri -Headers $conn.Headers -Method Get
        $allowOrg = if ($allowResponse.value) { $allowResponse.value[0] } else { $allowResponse }
        if ($null -ne $allowOrg.allowedmimetypes) {
            $allowedMimeTypes = ($allowOrg.allowedmimetypes -split ';' | ForEach-Object { $_.Trim() } | Where-Object { $_ })
        }
    }
    catch {
        Write-Verbose "FsiMimeControl: allowedmimetypes field not available on this environment — treating as unsupported"
    }

    # Build result; guard empty arrays against PSCustomObject null-unrolling
    $extArr  = if ($blockedExtensions.Count -gt 0) { [string[]]$blockedExtensions } else { [string[]]::new(0) }
    $mimeArr = if ($blockedMimeTypes.Count  -gt 0) { [string[]]$blockedMimeTypes  } else { [string[]]::new(0) }

    $result = [PSCustomObject]@{
        DataverseUrl       = $conn.Url
        OrganizationId     = $orgId
        BlockedExtensions  = $extArr
        BlockedMimeTypes   = $mimeArr
        AllowedMimeTypes   = $allowedMimeTypes
        RawResponse        = @{
            blockedattachments = $org.blockedattachments
            blockedmimetypes   = $org.blockedmimetypes
        }
    }

    Write-OutputResult -Result $result -OutputFormat $OutputFormat -OutputPath $OutputPath
}

# ═══════════════════════════════════════════════════════════════════════
# Cmdlet 2: Set-FsiMimeConfig
# ═══════════════════════════════════════════════════════════════════════

function Set-FsiMimeConfig {
    <#
    .SYNOPSIS
        Applies MIME type configuration to a Dataverse environment.

    .DESCRIPTION
        Applies a zone template or custom MIME configuration via Dataverse Web API
        PATCH. Supports -WhatIf for safe preview of changes. Template mode loads
        zone-specific JSON files with escalating restrictions.

    .PARAMETER DataverseUrl
        The Dataverse environment URL. If omitted, uses the module session.

    .PARAMETER AccessToken
        OAuth2 bearer token. If omitted, uses the module session or Get-AzAccessToken.

    .PARAMETER ZoneTemplate
        Zone template to apply: zone1, zone2, or zone3. Loads the corresponding
        JSON file from the mime-templates directory.

    .PARAMETER BlockedExtensions
        Custom array of file extensions to block. Used in 'Custom' parameter set.

    .PARAMETER BlockedMimeTypes
        Custom array of MIME types to block. Used in 'Custom' parameter set.

    .PARAMETER AllowedMimeTypes
        Custom array of MIME types to allow. Used in 'Custom' parameter set.

    .PARAMETER OutputFormat
        Output format for results. Valid values: Table, JSON, Object. Default: Object.

    .PARAMETER OutputPath
        Optional file path to export JSON results.

    .EXAMPLE
        Set-FsiMimeConfig -DataverseUrl 'https://org.crm.dynamics.com' -AccessToken $token -ZoneTemplate zone2

    .EXAMPLE
        Set-FsiMimeConfig -ZoneTemplate zone3 -WhatIf

    .EXAMPLE
        Set-FsiMimeConfig -BlockedExtensions @('exe','bat','cmd') -BlockedMimeTypes @('application/x-msdownload')
    #>
    [CmdletBinding(SupportsShouldProcess, DefaultParameterSetName = 'Template')]
    param(
        [Parameter()]
        [string]$DataverseUrl,

        [Parameter()]
        [string]$AccessToken,

        [Parameter(Mandatory, ParameterSetName = 'Template')]
        [ValidateSet('zone1', 'zone2', 'zone3')]
        [string]$ZoneTemplate,

        [Parameter(Mandatory, ParameterSetName = 'Custom')]
        [string[]]$BlockedExtensions,

        [Parameter(ParameterSetName = 'Custom')]
        [string[]]$BlockedMimeTypes,

        [Parameter(ParameterSetName = 'Custom')]
        [string[]]$AllowedMimeTypes,

        [Parameter()]
        [ValidateSet('Table', 'JSON', 'Object')]
        [string]$OutputFormat = 'Object',

        [Parameter()]
        [string]$OutputPath
    )

    $conn = Resolve-DataverseHeaders -DataverseUrl $DataverseUrl -AccessToken $AccessToken

    # Resolve target configuration
    $targetExtensions = @()
    $targetMimeTypes  = @()
    $targetAllowed    = @()
    $templateName     = $null

    if ($PSCmdlet.ParameterSetName -eq 'Template') {
        $templatePath = Join-Path $script:TemplateBasePath "$ZoneTemplate.json"
        if (-not (Test-Path $templatePath)) {
            throw "Zone template not found: $templatePath"
        }
        $template = Get-Content -Path $templatePath -Raw | ConvertFrom-Json
        $targetExtensions = $template.blockedExtensions
        $targetMimeTypes  = $template.blockedMimeTypes
        $targetAllowed    = $template.allowedMimeTypes
        $templateName     = $ZoneTemplate
    }
    else {
        $targetExtensions = $BlockedExtensions
        $targetMimeTypes  = if ($BlockedMimeTypes) { $BlockedMimeTypes } else { @() }
        $targetAllowed    = if ($AllowedMimeTypes)  { $AllowedMimeTypes }  else { @() }
    }

    # Get current configuration for comparison
    $currentConfig = Get-FsiMimeConfig -DataverseUrl $conn.Url -AccessToken ($conn.Headers['Authorization'] -replace '^Bearer ', '')

    # WhatIf preview
    $targetDescription = if ($templateName) { "zone template '$templateName'" } else { 'custom configuration' }
    if (-not $PSCmdlet.ShouldProcess($conn.Url, "Apply $targetDescription")) {
        Write-Verbose "WhatIf: Current blocked extensions ($($currentConfig.BlockedExtensions.Count)): $($currentConfig.BlockedExtensions -join '; ')"
        Write-Verbose "WhatIf: Target blocked extensions ($($targetExtensions.Count)): $($targetExtensions -join '; ')"
        Write-Verbose "WhatIf: Current blocked MIME types ($($currentConfig.BlockedMimeTypes.Count)): $($currentConfig.BlockedMimeTypes -join '; ')"
        Write-Verbose "WhatIf: Target blocked MIME types ($($targetMimeTypes.Count)): $($targetMimeTypes -join '; ')"
        Write-Verbose "WhatIf: Current allowed MIME types ($( if ($currentConfig.AllowedMimeTypes) { $currentConfig.AllowedMimeTypes.Count } else { 'N/A' } ))"
        Write-Verbose "WhatIf: Target allowed MIME types ($($targetAllowed.Count))"
        return
    }

    # Build PATCH body
    $patchBody = @{
        blockedattachments = ($targetExtensions -join ';')
        blockedmimetypes   = ($targetMimeTypes -join ';')
    }

    # Attempt to include allowedmimetypes
    $allowedMimeTypesSupported = $true
    if ($targetAllowed.Count -gt 0) {
        $patchBody['allowedmimetypes'] = ($targetAllowed -join ';')
    }

    $orgId = $currentConfig.OrganizationId
    $patchUri = "$($conn.Url)/api/data/v9.2/organizations($orgId)"
    $patchHeaders = $conn.Headers.Clone()
    $patchHeaders['Content-Type'] = 'application/json'

    try {
        $body = $patchBody | ConvertTo-Json -Compress
        $null = Invoke-RestMethod -Uri $patchUri -Headers $patchHeaders -Method Patch -Body $body
        Write-Verbose "FsiMimeControl: PATCH applied successfully"
    }
    catch {
        # If allowedmimetypes field is unsupported, retry without it
        if ($patchBody.ContainsKey('allowedmimetypes')) {
            Write-Warning "FsiMimeControl: allowedmimetypes field not supported by this environment. Retrying without allowlist."
            $allowedMimeTypesSupported = $false
            $patchBody.Remove('allowedmimetypes')
            try {
                $body = $patchBody | ConvertTo-Json -Compress
                $null = Invoke-RestMethod -Uri $patchUri -Headers $patchHeaders -Method Patch -Body $body
                Write-Verbose "FsiMimeControl: PATCH applied successfully (without allowedmimetypes)"
            }
            catch {
                throw "Failed to apply MIME configuration: $($_.Exception.Message)"
            }
        }
        else {
            throw "Failed to apply MIME configuration: $($_.Exception.Message)"
        }
    }

    Write-Host "  MIME configuration applied to $($conn.Url)" -ForegroundColor Green
    if (-not $allowedMimeTypesSupported) {
        Write-Host "  Note: allowedmimetypes field not supported — allowlist was not applied" -ForegroundColor Yellow
    }
    Write-Host "  Note: Configuration changes may take up to 15 minutes to propagate" -ForegroundColor Yellow

    # Verify post-apply state
    $newConfig = Get-FsiMimeConfig -DataverseUrl $conn.Url -AccessToken ($conn.Headers['Authorization'] -replace '^Bearer ', '')

    $result = [PSCustomObject]@{
        Applied                  = $true
        PreviousConfig           = $currentConfig
        NewConfig                = $newConfig
        Template                 = $templateName
        AllowedMimeTypesSupported = $allowedMimeTypesSupported
    }

    Write-OutputResult -Result $result -OutputFormat $OutputFormat -OutputPath $OutputPath
}

# ═══════════════════════════════════════════════════════════════════════
# Cmdlet 3: Test-FsiMimeCompliance
# ═══════════════════════════════════════════════════════════════════════

function Test-FsiMimeCompliance {
    <#
    .SYNOPSIS
        Validates a Dataverse environment's MIME configuration against zone requirements.

    .DESCRIPTION
        Reads the current MIME configuration from Dataverse and compares it against
        the specified zone template. Runs 6 checks covering blocked extensions,
        blocked MIME types, allowed MIME types, and zone flags. Returns a compliance
        result with pass/fail/warning status per check.

    .PARAMETER DataverseUrl
        The Dataverse environment URL. If omitted, uses the module session.

    .PARAMETER AccessToken
        OAuth2 bearer token. If omitted, uses the module session or Get-AzAccessToken.

    .PARAMETER Zone
        Target governance zone (1, 2, or 3) to validate against.

    .PARAMETER OutputFormat
        Output format for results. Valid values: Table, JSON, Object. Default: Object.

    .PARAMETER OutputPath
        Optional file path to export JSON results.

    .PARAMETER IncludeEvidence
        When specified, computes SHA-256 integrity hash over results for evidence packaging.

    .EXAMPLE
        Test-FsiMimeCompliance -DataverseUrl 'https://org.crm.dynamics.com' -AccessToken $token -Zone 2

    .EXAMPLE
        Test-FsiMimeCompliance -Zone 3 -OutputFormat JSON -OutputPath .\evidence\mime-compliance.json -IncludeEvidence
    #>
    [CmdletBinding()]
    param(
        [Parameter()]
        [string]$DataverseUrl,

        [Parameter()]
        [string]$AccessToken,

        [Parameter(Mandatory)]
        [ValidateSet(1, 2, 3)]
        [int]$Zone,

        [Parameter()]
        [ValidateSet('Table', 'JSON', 'Object')]
        [string]$OutputFormat = 'Object',

        [Parameter()]
        [string]$OutputPath,

        [Parameter()]
        [switch]$IncludeEvidence
    )

    $conn = Resolve-DataverseHeaders -DataverseUrl $DataverseUrl -AccessToken $AccessToken

    # Load zone template
    $templatePath = Join-Path $script:TemplateBasePath "zone$Zone.json"
    if (-not (Test-Path $templatePath)) {
        throw "Zone template not found: $templatePath"
    }
    $template = Get-Content -Path $templatePath -Raw | ConvertFrom-Json

    # Get current configuration
    $config = Get-FsiMimeConfig -DataverseUrl $conn.Url -AccessToken ($conn.Headers['Authorization'] -replace '^Bearer ', '')

    $checks   = [System.Collections.Generic.List[PSCustomObject]]::new()
    $findings = [System.Collections.Generic.List[string]]::new()

    # ── MIME-01: Blocked file extensions configured ──────────────────
    $hasBlockedExtensions = ($config.BlockedExtensions.Count -gt 0)
    $checks.Add((New-CheckResult -CheckId 'MIME-01' `
        -Setting 'Blocked file extensions configured' `
        -Status $(if ($hasBlockedExtensions) { 'Pass' } else { 'Fail' }) `
        -Expected "Blocked extensions list populated" `
        -Actual "$($config.BlockedExtensions.Count) extensions configured" `
        -Message $(if (-not $hasBlockedExtensions) { "No blocked extensions configured — environment allows all file types" } else { $null })))

    if (-not $hasBlockedExtensions) {
        $findings.Add("No blocked file extensions configured. Zone $Zone requires $($template.blockedExtensions.Count) blocked extensions.")
    }

    # ── MIME-02: All required extensions present ─────────────────────
    $requiredExtensions = $template.blockedExtensions
    $missingExtensions = $requiredExtensions | Where-Object { $_ -notin $config.BlockedExtensions }
    $allPresent = ($missingExtensions.Count -eq 0)

    $checks.Add((New-CheckResult -CheckId 'MIME-02' `
        -Setting 'All required extensions present' `
        -Status $(if ($allPresent) { 'Pass' } else { 'Fail' }) `
        -Expected "$($requiredExtensions.Count) required extensions" `
        -Actual "$($requiredExtensions.Count - $missingExtensions.Count) present, $($missingExtensions.Count) missing" `
        -Message $(if (-not $allPresent) { "Missing: $($missingExtensions -join ', ')" } else { $null })))

    if (-not $allPresent) {
        $findings.Add("Missing $($missingExtensions.Count) required blocked extensions: $($missingExtensions -join ', ')")
    }

    # ── MIME-03: Blocked MIME types configured ───────────────────────
    $hasBlockedMime = ($config.BlockedMimeTypes.Count -gt 0)
    $requiredMimeCount = $template.blockedMimeTypes.Count
    $mime03Status = if ($Zone -eq 1) {
        if ($hasBlockedMime) { 'Pass' } else { 'Info' }
    } else {
        if ($hasBlockedMime) { 'Pass' } else { 'Fail' }
    }

    $checks.Add((New-CheckResult -CheckId 'MIME-03' `
        -Setting 'Blocked MIME types configured' `
        -Status $mime03Status `
        -Expected $(if ($Zone -eq 1) { "Optional for Zone 1" } else { "$requiredMimeCount blocked MIME types" }) `
        -Actual "$($config.BlockedMimeTypes.Count) MIME types configured" `
        -Message $(if ($mime03Status -eq 'Fail') { "Zone $Zone requires blocked MIME types to be configured" } elseif ($mime03Status -eq 'Info') { "Zone 1 does not require MIME type blocking" } else { $null })))

    if ($mime03Status -eq 'Fail') {
        $findings.Add("No blocked MIME types configured. Zone $Zone requires $requiredMimeCount blocked MIME types.")
    }

    # ── MIME-04: All required MIME types present ─────────────────────
    $requiredMimes = $template.blockedMimeTypes
    if ($requiredMimes.Count -gt 0) {
        $missingMimes = $requiredMimes | Where-Object { $_ -notin $config.BlockedMimeTypes }
        $allMimesPresent = ($missingMimes.Count -eq 0)
        $mime04Status = if ($Zone -eq 1) {
            if ($allMimesPresent -or $requiredMimes.Count -eq 0) { 'Info' } else { 'Info' }
        } else {
            if ($allMimesPresent) { 'Pass' } else { 'Fail' }
        }
    }
    else {
        $missingMimes = @()
        $allMimesPresent = $true
        $mime04Status = 'Info'
    }

    $checks.Add((New-CheckResult -CheckId 'MIME-04' `
        -Setting 'All required MIME types present' `
        -Status $mime04Status `
        -Expected $(if ($Zone -eq 1) { "N/A for Zone 1" } else { "$($requiredMimes.Count) required MIME types" }) `
        -Actual "$($requiredMimes.Count - $missingMimes.Count) present, $($missingMimes.Count) missing" `
        -Message $(if ($mime04Status -eq 'Fail') { "Missing: $($missingMimes -join ', ')" } elseif ($Zone -eq 1) { "Zone 1 does not require MIME type blocking" } else { $null })))

    if ($mime04Status -eq 'Fail') {
        $findings.Add("Missing $($missingMimes.Count) required blocked MIME types: $($missingMimes -join ', ')")
    }

    # ── MIME-05: Allowed MIME types configured ───────────────────────
    $templateAllowed = $template.allowedMimeTypes
    $apiAllowedSupported = ($null -ne $config.AllowedMimeTypes)

    if (-not $apiAllowedSupported) {
        # Field not available in this environment — advisory mode
        $mime05Status = switch ($Zone) {
            3 { 'Warning' }
            2 { 'Info' }
            1 { 'Info' }
        }
        $mime05Message = switch ($Zone) {
            3 { "Allowlist recommended for Zone 3 but allowedmimetypes field not available in this environment" }
            2 { "Allowlist optional for Zone 2; allowedmimetypes field not available" }
            1 { "Allowlist not required for Zone 1" }
        }
    }
    else {
        $hasAllowlist = ($config.AllowedMimeTypes.Count -gt 0)
        $mime05Status = switch ($Zone) {
            3 { if ($hasAllowlist) { 'Pass' } else { 'Fail' } }
            2 { if ($hasAllowlist) { 'Pass' } else { 'Warning' } }
            1 { 'Info' }
        }
        $mime05Message = switch ($Zone) {
            3 { if (-not $hasAllowlist) { "Zone 3 requires an explicit allowlist of permitted MIME types" } else { $null } }
            2 { if (-not $hasAllowlist) { "Zone 2 recommends an allowlist of permitted MIME types" } else { $null } }
            1 { "Allowlist not required for Zone 1" }
        }
    }

    $checks.Add((New-CheckResult -CheckId 'MIME-05' `
        -Setting 'Allowed MIME types configured' `
        -Status $mime05Status `
        -Expected $(if ($Zone -eq 3) { "$($templateAllowed.Count) allowed MIME types" } elseif ($Zone -eq 2) { "Allowlist recommended" } else { "N/A" }) `
        -Actual $(if ($apiAllowedSupported -and $config.AllowedMimeTypes) { "$($config.AllowedMimeTypes.Count) types in allowlist" } elseif (-not $apiAllowedSupported) { "Field not available" } else { "No allowlist" }) `
        -Message $mime05Message))

    if ($mime05Status -eq 'Fail') {
        $findings.Add("Zone $Zone requires an explicit allowlist of permitted MIME types ($($templateAllowed.Count) types in template).")
    }
    elseif ($mime05Status -eq 'Warning') {
        $findings.Add("Allowlist recommended but not configured. Template defines $($templateAllowed.Count) allowed types.")
    }

    # ── MIME-06: Zone flags satisfied ────────────────────────────────
    $templateFlags = $template.flags
    $flagMessages = @()
    if ($templateFlags.requireDlpIntegration) {
        $flagMessages += "DLP integration required"
    }
    if ($templateFlags.requireSentinelMonitoring) {
        $flagMessages += "Sentinel monitoring required"
    }
    if ($templateFlags.requireServerSideValidation) {
        $flagMessages += "Server-side validation required"
    }

    $mime06Status = if ($Zone -eq 3) { 'Warning' } else { 'Info' }
    $mime06Message = if ($flagMessages.Count -gt 0) {
        "Advisory — verify manually: $($flagMessages -join '; ')"
    } else {
        "No additional flags required for Zone $Zone"
    }

    $checks.Add((New-CheckResult -CheckId 'MIME-06' `
        -Setting 'Zone flags satisfied' `
        -Status $mime06Status `
        -Expected $(if ($flagMessages.Count -gt 0) { "$($flagMessages.Count) flags required" } else { "No flags" }) `
        -Actual "Manual verification required" `
        -Message $mime06Message))

    # ── Compliance Summary ──────────────────────────────────────────
    $passCount = ($checks | Where-Object { $_.Status -eq 'Pass' }).Count
    $failCount = ($checks | Where-Object { $_.Status -eq 'Fail' }).Count
    $warnCount = ($checks | Where-Object { $_.Status -eq 'Warning' }).Count
    $infoCount = ($checks | Where-Object { $_.Status -eq 'Info' }).Count
    $isCompliant = ($failCount -eq 0)

    $result = [PSCustomObject]@{
        DataverseUrl = $conn.Url
        Zone         = $Zone
        IsCompliant  = $isCompliant
        Checks       = $checks.ToArray()
        Findings     = $findings.ToArray()
        Summary      = [PSCustomObject]@{
            PassCount = $passCount
            FailCount = $failCount
            WarnCount = $warnCount
            InfoCount = $infoCount
        }
        EvidenceHash = $null
    }

    # ── SHA-256 Evidence Hash ────────────────────────────────────────
    if ($IncludeEvidence) {
        $resultsJson = $result | ConvertTo-Json -Depth 10 -Compress
        $hashBytes = [System.Security.Cryptography.SHA256]::Create().ComputeHash(
            [System.Text.Encoding]::UTF8.GetBytes($resultsJson)
        )
        $result.EvidenceHash = [BitConverter]::ToString($hashBytes) -replace '-'
    }

    # ── Console Summary ──────────────────────────────────────────────
    Write-Host "`n── MIME Compliance Summary (Zone $Zone) ────────────────────" -ForegroundColor Cyan
    Write-Host "  Checks:    $($checks.Count)"
    Write-Host "  Passed:    $passCount" -ForegroundColor $(if ($passCount -eq $checks.Count) { 'Green' } else { 'White' })
    Write-Host "  Failed:    $failCount" -ForegroundColor $(if ($failCount -gt 0) { 'Red' } else { 'Green' })
    Write-Host "  Warnings:  $warnCount" -ForegroundColor $(if ($warnCount -gt 0) { 'Yellow' } else { 'White' })
    Write-Host "  Compliant: $isCompliant" -ForegroundColor $(if ($isCompliant) { 'Green' } else { 'Red' })
    if ($IncludeEvidence) {
        Write-Host "  Evidence:  $($result.EvidenceHash)" -ForegroundColor DarkGray
    }
    Write-Host "────────────────────────────────────────────────────────────`n" -ForegroundColor Cyan

    Write-OutputResult -Result $result -OutputFormat $OutputFormat -OutputPath $OutputPath
}

# ═══════════════════════════════════════════════════════════════════════
# Module Export
# ═══════════════════════════════════════════════════════════════════════

Export-ModuleMember -Function @(
    'Connect-FsiMimeDataverse',
    'Get-FsiMimeConnection',
    'Get-FsiMimeConfig',
    'Set-FsiMimeConfig',
    'Test-FsiMimeCompliance'
)
