<#
.SYNOPSIS
    Registers the ValidateMimeTypePlugin assembly and step in a Dataverse environment.

.DESCRIPTION
    Deploys the FSI Agent Governance MIME validation plugin to a Dataverse
    environment via the Dataverse Web API. Performs three operations:

    1. Registers the plugin assembly (ValidateMimeTypePlugin.dll)
    2. Registers the plugin type (ValidateMimeTypePlugin)
    3. Registers the plugin step on Create of annotation (Note) entity
       at the pre-validation stage with MimeConfig.json as secure configuration

    Supports compliance with FINRA 4511 and SEC 17a-4 by automating the
    deployment of server-side file validation capabilities for Zone 3
    Enterprise Managed environments.

    Idempotent — checks for existing registrations before creating new ones.

.PARAMETER DataverseUrl
    Dataverse environment URL (e.g., https://org.crm.dynamics.com).
    Must include the https:// scheme.

.PARAMETER AssemblyPath
    Path to the compiled plugin assembly DLL file.
    Example: ./bin/Release/ValidateMimeTypePlugin.dll

.PARAMETER ConfigPath
    Path to the MimeConfig.json configuration file.
    Default: src/MimeConfig.json

.PARAMETER AccessToken
    OAuth access token for Dataverse. When omitted, falls back to
    Get-AzAccessToken for the specified DataverseUrl resource.

.EXAMPLE
    .\register-plugin.ps1 -DataverseUrl https://org.crm.dynamics.com -AssemblyPath ./bin/Release/ValidateMimeTypePlugin.dll

    Registers the plugin assembly and step using Microsoft Entra ID token from Az.Accounts.

.EXAMPLE
    .\register-plugin.ps1 -DataverseUrl https://org.crm.dynamics.com -AssemblyPath ./bin/Release/ValidateMimeTypePlugin.dll -WhatIf

    Preview registration without making changes.

.EXAMPLE
    $tokenResult = Get-AzAccessToken -ResourceUrl https://org.crm.dynamics.com
    $token = if ($tokenResult.Token -is [securestring]) { $tokenResult.Token | ConvertFrom-SecureString -AsPlainText } else { $tokenResult.Token }
    .\register-plugin.ps1 -DataverseUrl https://org.crm.dynamics.com -AssemblyPath ./bin/Release/ValidateMimeTypePlugin.dll -AccessToken $token

    Registers using an explicitly provided access token.

.OUTPUTS
    PSCustomObject with PluginAssembly, PluginType, and PluginStep registration details.

.NOTES
    Part of the FSI Agent Governance — MIME Type Restrictions (Control 1.25).
    Version: 1.0.0
    Requires: PowerShell 7.0+, Az.Accounts module (for token fallback)
#>

#Requires -Version 7.0

[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(Mandatory)]
    [ValidatePattern('^https://')]
    [string]$DataverseUrl,

    [Parameter(Mandatory)]
    [ValidateScript({ Test-Path $_ -PathType Leaf })]
    [string]$AssemblyPath,

    [Parameter()]
    [string]$ConfigPath = (Join-Path $PSScriptRoot 'mime-templates' 'zone3.json'),

    [Parameter()]
    [string]$AccessToken
)

$ErrorActionPreference = 'Stop'

# ─── Constants ────────────────────────────────────────────────────────
$SCRIPT_NAME    = 'register-plugin'
$SCRIPT_VERSION = '1.0.0'
$API_VERSION    = 'v9.2'
$PLUGIN_TYPE_NAME = 'FsiAgentGovernance.Plugins.ValidateMimeTypePlugin'
$STEP_NAME      = 'FSI-MIME: Validate attachment on Create'
$ENTITY_NAME    = 'annotation'
$MESSAGE_NAME   = 'Create'
$STAGE          = 10  # Pre-validation

# ─── Banner ───────────────────────────────────────────────────────────
Write-Host "`n╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host   "║  FSI Agent Governance — Register MIME Validation Plugin  ║" -ForegroundColor Cyan
Write-Host   "╚══════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

Write-Host "  Dataverse URL:  $DataverseUrl" -ForegroundColor Gray
Write-Host "  Assembly:       $AssemblyPath" -ForegroundColor Gray
Write-Host "  Config:         $ConfigPath" -ForegroundColor Gray
Write-Host ""

# ─── Resolve Token ────────────────────────────────────────────────────
$baseUrl = $DataverseUrl.TrimEnd('/')

if (-not $AccessToken) {
    try {
        Write-Verbose "No AccessToken provided — acquiring via Get-AzAccessToken."
        $azToken = Get-AzAccessToken -ResourceUrl $baseUrl -ErrorAction Stop
        # Handle SecureString .Token (Az.Accounts 3.0+) or plain string (older)
        if ($azToken.Token -is [securestring]) {
            $AccessToken = $azToken.Token | ConvertFrom-SecureString -AsPlainText
        } else {
            $AccessToken = $azToken.Token
        }
        Write-Host "  [OK] Token acquired via Az.Accounts" -ForegroundColor Green
    }
    catch {
        throw "Failed to acquire access token. Provide -AccessToken or sign in via Connect-AzAccount. Error: $($_.Exception.Message)"
    }
}

$headers = @{
    'Authorization' = "Bearer $AccessToken"
    'OData-MaxVersion' = '4.0'
    'OData-Version'    = '4.0'
    'Accept'           = 'application/json'
    'Prefer'           = 'return=representation'
}

$apiBase = "$baseUrl/api/data/$API_VERSION"

# ─── Load Configuration ──────────────────────────────────────────────
if (-not (Test-Path $ConfigPath)) {
    throw "MimeConfig.json not found at '$ConfigPath'. Provide a valid -ConfigPath."
}

$mimeConfig = Get-Content -Path $ConfigPath -Raw
Write-Host "  [OK] Loaded configuration from '$ConfigPath'" -ForegroundColor Green

# ─── Load Assembly Bytes ──────────────────────────────────────────────
$assemblyBytes = [System.IO.File]::ReadAllBytes((Resolve-Path $AssemblyPath).Path)
$assemblyBase64 = [Convert]::ToBase64String($assemblyBytes)
$assemblyName = [System.IO.Path]::GetFileNameWithoutExtension($AssemblyPath)

Write-Host "  [OK] Assembly loaded: $assemblyName ($($assemblyBytes.Length) bytes)" -ForegroundColor Green
Write-Host ""

# ─── WhatIf Preview ──────────────────────────────────────────────────
if (-not $PSCmdlet.ShouldProcess($baseUrl, "Register plugin '$PLUGIN_TYPE_NAME'")) {
    Write-Host "  [WhatIf] Would perform the following actions:" -ForegroundColor Yellow
    Write-Host "    1. Register plugin assembly '$assemblyName'" -ForegroundColor Yellow
    Write-Host "    2. Register plugin type '$PLUGIN_TYPE_NAME'" -ForegroundColor Yellow
    Write-Host "    3. Register step on $MESSAGE_NAME of $ENTITY_NAME (stage $STAGE)" -ForegroundColor Yellow
    Write-Host "    4. Attach secure configuration from '$ConfigPath'" -ForegroundColor Yellow
    Write-Host ""

    return [PSCustomObject]@{
        ScriptName = $SCRIPT_NAME
        Version    = $SCRIPT_VERSION
        WhatIf     = $true
        Steps      = @(
            'Register plugin assembly',
            'Register plugin type',
            'Register step on Create of annotation (pre-validation)',
            'Attach secure configuration (MimeConfig.json)'
        )
    }
}

# ─── Helper: Invoke Dataverse API ─────────────────────────────────────

function Invoke-DataverseApi {
    <#
    .SYNOPSIS
        Invokes a Dataverse Web API endpoint with authorization and error handling.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$Method,
        [Parameter(Mandatory)][string]$Uri,
        [Parameter()][object]$Body
    )

    $params = @{
        Method  = $Method
        Uri     = $Uri
        Headers = $headers
    }

    if ($Body) {
        $params['Body'] = ($Body | ConvertTo-Json -Depth 10 -Compress)
        $params['ContentType'] = 'application/json'
    }

    try {
        $response = Invoke-RestMethod @params -ErrorAction Stop
        return $response
    }
    catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
        $detail = $_.ErrorDetails.Message
        throw "Dataverse API call failed (HTTP $statusCode): $detail"
    }
}

# ─── Step 1: Check for Existing Assembly ──────────────────────────────
Write-Host "  Step 1: Checking for existing plugin assembly..." -ForegroundColor White

$existingAssembly = $null
try {
    $filter = "name eq '$assemblyName'"
    $result = Invoke-DataverseApi -Method GET -Uri "$apiBase/pluginassemblies?`$filter=$filter&`$select=pluginassemblyid,name,version"
    if ($result.value -and $result.value.Count -gt 0) {
        $existingAssembly = $result.value[0]
        Write-Host "    Found existing assembly: $($existingAssembly.pluginassemblyid)" -ForegroundColor Yellow
    }
}
catch {
    Write-Verbose "No existing assembly found or query failed: $($_.Exception.Message)"
}

# ─── Step 2: Register or Update Assembly ──────────────────────────────
Write-Host "  Step 2: Registering plugin assembly..." -ForegroundColor White

$assemblyPayload = @{
    name                = $assemblyName
    content             = $assemblyBase64
    isolationmode       = 2  # Sandbox
    sourcetype          = 0  # Database
    version             = '1.0.0.0'
    description         = 'FSI Agent Governance — Zone 3 server-side MIME type validation plugin. Supports compliance with FINRA 4511 and SEC 17a-4.'
    publickeytoken      = $null
    culture             = 'neutral'
}

$assemblyId = $null

if ($existingAssembly) {
    # Update existing assembly
    $assemblyId = $existingAssembly.pluginassemblyid
    Invoke-DataverseApi -Method PATCH -Uri "$apiBase/pluginassemblies($assemblyId)" -Body $assemblyPayload
    Write-Host "    [OK] Assembly updated: $assemblyId" -ForegroundColor Green
}
else {
    # Create new assembly
    $newAssembly = Invoke-DataverseApi -Method POST -Uri "$apiBase/pluginassemblies" -Body $assemblyPayload
    $assemblyId = $newAssembly.pluginassemblyid
    Write-Host "    [OK] Assembly registered: $assemblyId" -ForegroundColor Green
}

# ─── Step 3: Register Plugin Type ─────────────────────────────────────
Write-Host "  Step 3: Registering plugin type..." -ForegroundColor White

$existingType = $null
try {
    $filter = "typename eq '$PLUGIN_TYPE_NAME'"
    $result = Invoke-DataverseApi -Method GET -Uri "$apiBase/plugintypes?`$filter=$filter&`$select=plugintypeid,typename"
    if ($result.value -and $result.value.Count -gt 0) {
        $existingType = $result.value[0]
        Write-Host "    Found existing type: $($existingType.plugintypeid)" -ForegroundColor Yellow
    }
}
catch {
    Write-Verbose "No existing type found: $($_.Exception.Message)"
}

$typeId = $null

if ($existingType) {
    $typeId = $existingType.plugintypeid
    Write-Host "    [OK] Plugin type already registered: $typeId" -ForegroundColor Green
}
else {
    $typePayload = @{
        typename                       = $PLUGIN_TYPE_NAME
        friendlyname                   = 'FSI MIME Validation Plugin'
        name                           = $PLUGIN_TYPE_NAME
        description                    = 'Validates file attachments against Zone 3 MIME restrictions.'
        'pluginassemblyid@odata.bind'  = "pluginassemblies($assemblyId)"
    }

    $newType = Invoke-DataverseApi -Method POST -Uri "$apiBase/plugintypes" -Body $typePayload
    $typeId = $newType.plugintypeid
    Write-Host "    [OK] Plugin type registered: $typeId" -ForegroundColor Green
}

# ─── Step 4: Retrieve SdkMessage and Filter ───────────────────────────
Write-Host "  Step 4: Resolving SDK message and filter..." -ForegroundColor White

# Get Create message ID
$msgResult = Invoke-DataverseApi -Method GET -Uri "$apiBase/sdkmessages?`$filter=name eq '$MESSAGE_NAME'&`$select=sdkmessageid"
if (-not $msgResult.value -or $msgResult.value.Count -eq 0) {
    throw "SDK message '$MESSAGE_NAME' not found in target environment."
}
$messageId = $msgResult.value[0].sdkmessageid
Write-Verbose "SdkMessage '$MESSAGE_NAME' ID: $messageId"

# Get message filter for annotation entity
$filterResult = Invoke-DataverseApi -Method GET -Uri "$apiBase/sdkmessagefilters?`$filter=_sdkmessageid_value eq $messageId and primaryobjecttypecode eq '$ENTITY_NAME'&`$select=sdkmessagefilterid"
if (-not $filterResult.value -or $filterResult.value.Count -eq 0) {
    throw "SDK message filter for '$MESSAGE_NAME' on '$ENTITY_NAME' not found."
}
$filterId = $filterResult.value[0].sdkmessagefilterid

Write-Host "    [OK] Message: $messageId, Filter: $filterId" -ForegroundColor Green

# ─── Step 5: Register Plugin Step ─────────────────────────────────────
Write-Host "  Step 5: Registering plugin step..." -ForegroundColor White

$existingStep = $null
try {
    $filter = "name eq '$STEP_NAME'"
    $result = Invoke-DataverseApi -Method GET -Uri "$apiBase/sdkmessageprocessingsteps?`$filter=$filter&`$select=sdkmessageprocessingstepid,name,_sdkmessageprocessingstepsecureconfigid_value"
    if ($result.value -and $result.value.Count -gt 0) {
        $existingStep = $result.value[0]
        Write-Host "    Found existing step: $($existingStep.sdkmessageprocessingstepid)" -ForegroundColor Yellow
    }
}
catch {
    Write-Verbose "No existing step found: $($_.Exception.Message)"
}

$stepPayload = @{
    name                                    = $STEP_NAME
    description                             = 'Validates annotation file attachments against Zone 3 MIME restrictions. Aids in meeting regulatory requirements for file type governance.'
    stage                                   = $STAGE
    rank                                    = 1
    mode                                    = 0  # Synchronous
    supporteddeployment                     = 0  # Server only
    filteringattributes                     = 'documentbody,mimetype,filename'
    'sdkmessageid@odata.bind'               = "sdkmessages($messageId)"
    'sdkmessagefilterid@odata.bind'         = "sdkmessagefilters($filterId)"
    'plugintypeid@odata.bind'               = "plugintypes($typeId)"
}

# Create or update secure configuration record for the MIME policy
Write-Host "    Creating secure configuration record..." -ForegroundColor Yellow
$secureConfigPayload = @{ secureconfig = $mimeConfig }

$stepId = $null

if ($existingStep) {
    $stepId = $existingStep.sdkmessageprocessingstepid
    # Update existing secure config if present, otherwise create new
    $existingSecureConfigId = $existingStep._sdkmessageprocessingstepsecureconfigid_value
    if ($existingSecureConfigId) {
        Invoke-DataverseApi -Method PATCH -Uri "$apiBase/sdkmessageprocessingstepsecureconfigs($existingSecureConfigId)" -Body $secureConfigPayload
    }
    else {
        $secureConfigResp = Invoke-DataverseApi -Method POST -Uri "$apiBase/sdkmessageprocessingstepsecureconfigs" -Body $secureConfigPayload
        $stepPayload['sdkmessageprocessingstepsecureconfigid@odata.bind'] = "sdkmessageprocessingstepsecureconfigs($($secureConfigResp.sdkmessageprocessingstepsecureconfigid))"
    }
    Invoke-DataverseApi -Method PATCH -Uri "$apiBase/sdkmessageprocessingsteps($stepId)" -Body $stepPayload
    Write-Host "    [OK] Step updated: $stepId" -ForegroundColor Green
}
else {
    $secureConfigResp = Invoke-DataverseApi -Method POST -Uri "$apiBase/sdkmessageprocessingstepsecureconfigs" -Body $secureConfigPayload
    $stepPayload['sdkmessageprocessingstepsecureconfigid@odata.bind'] = "sdkmessageprocessingstepsecureconfigs($($secureConfigResp.sdkmessageprocessingstepsecureconfigid))"
    $newStep = Invoke-DataverseApi -Method POST -Uri "$apiBase/sdkmessageprocessingsteps" -Body $stepPayload
    $stepId = $newStep.sdkmessageprocessingstepid
    Write-Host "    [OK] Step registered: $stepId" -ForegroundColor Green
}

# ─── Summary ──────────────────────────────────────────────────────────
Write-Host ""
Write-Host "  ✓ Plugin registration complete" -ForegroundColor Green
Write-Host ""

$result = [PSCustomObject]@{
    Metadata = [PSCustomObject]@{
        ScriptName  = $SCRIPT_NAME
        Version     = $SCRIPT_VERSION
        ExecutedAt  = (Get-Date -Format 'o')
        DataverseUrl = $baseUrl
    }
    PluginAssembly = [PSCustomObject]@{
        AssemblyId   = $assemblyId
        AssemblyName = $assemblyName
        IsolationMode = 'Sandbox'
    }
    PluginType = [PSCustomObject]@{
        TypeId   = $typeId
        TypeName = $PLUGIN_TYPE_NAME
    }
    PluginStep = [PSCustomObject]@{
        StepId      = $stepId
        StepName    = $STEP_NAME
        Entity      = $ENTITY_NAME
        Message     = $MESSAGE_NAME
        Stage       = $STAGE
        Mode        = 'Synchronous'
    }
}

$result | Format-List | Out-Host
return $result
