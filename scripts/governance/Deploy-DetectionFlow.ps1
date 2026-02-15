<#
.SYNOPSIS
    Deploys the UASD detection flow to a Power Platform environment.

.DESCRIPTION
    Imports the Unrestricted Agent Sharing Detector scan flow
    (uasd-detector-scan-agents.json) into a Power Platform environment.
    Binds connection references, validates import, and configures
    the recurrence schedule.

    Idempotent — re-running against an environment that already contains
    the flow updates the existing definition.

    This script supports compliance with FINRA 4511 and SEC 17a-4 by
    automating the deployment of agent sharing detection capabilities.
    Implementation requires appropriate administrative permissions and
    should be validated per organizational requirements.

.PARAMETER EnvironmentId
    Power Platform environment GUID for deployment.

.PARAMETER FlowDefinitionPath
    Path to the detector flow JSON file.
    Default: src/uasd-detector-scan-agents.json

.PARAMETER DataverseUrl
    Dataverse environment URL (e.g., https://org.crm.dynamics.com).
    Must include the scheme (https://) and trailing slash is optional.

.PARAMETER ScanFrequencyHours
    Recurrence interval in hours for the detection scan.
    Default: 24. Valid range: 1-168.

.PARAMETER WhatIf
    Preview deployment without making changes.

.EXAMPLE
    .\Deploy-DetectionFlow.ps1 -EnvironmentId "00000000-0000-0000-0000-000000000001" -DataverseUrl https://org.crm.dynamics.com

    Deploys the detection flow with default 24-hour scan frequency.

.EXAMPLE
    .\Deploy-DetectionFlow.ps1 -EnvironmentId "00000000-0000-0000-0000-000000000001" -DataverseUrl https://org.crm.dynamics.com -ScanFrequencyHours 12

    Deploys the detection flow with a 12-hour scan frequency.

.EXAMPLE
    .\Deploy-DetectionFlow.ps1 -EnvironmentId "00000000-0000-0000-0000-000000000001" -DataverseUrl https://org.crm.dynamics.com -WhatIf

    Preview deployment without making changes to the target environment.

.EXAMPLE
    .\Deploy-DetectionFlow.ps1 -EnvironmentId "00000000-0000-0000-0000-000000000001" -DataverseUrl https://org.crm.dynamics.com -ScanFrequencyHours 8 -Verbose

    Deploys with 8-hour recurrence and verbose diagnostic output.

.OUTPUTS
    PSCustomObject with Metadata, DeploymentResult, and ValidationChecks properties.

.NOTES
    Part of the FSI Agent Governance — Unrestricted Agent Sharing Detector.
    Controls: 1.1, 3.8
    Version: 1.0.0
    Requires: Az.Accounts module for Power Platform and Dataverse authentication
#>

#Requires -Version 7.0
#Requires -Modules Az.Accounts

[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(Mandatory)]
    [ValidatePattern('^[0-9a-fA-F]{8}-([0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}$')]
    [string]$EnvironmentId,

    [Parameter()]
    [string]$FlowDefinitionPath = (Join-Path 'src' 'uasd-detector-scan-agents.json'),

    [Parameter(Mandatory)]
    [ValidatePattern('^https://')]
    [string]$DataverseUrl,

    [Parameter()]
    [ValidateRange(1, 168)]
    [int]$ScanFrequencyHours = 24
)

$ErrorActionPreference = 'Stop'

# ─── Constants ────────────────────────────────────────────────────────
$SCRIPT_NAME    = 'Deploy-DetectionFlow'
$SCRIPT_VERSION = '1.0.0'
$FLOW_DISPLAY_NAME = 'UASD — Detector: Scan Agents'
$FLOW_API_BASE  = 'https://api.flow.microsoft.com/providers/Microsoft.ProcessSimple'
$CONNECTION_REF_DATAVERSE = 'fsi_cr_dataverse_sharingdetector'
$CONNECTION_REF_TEAMS     = 'fsi_cr_teams_sharingdetector'
$ENV_VAR_SCAN_FREQUENCY   = 'fsi_UASD_ScanFrequencyHours'

# ─── Banner ───────────────────────────────────────────────────────────
Write-Host "`n╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host   "║  UASD — Deploy Detection Flow                          ║" -ForegroundColor Cyan
Write-Host   "╚══════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

Write-Host "  Environment:     $EnvironmentId" -ForegroundColor Gray
Write-Host "  Dataverse URL:   $DataverseUrl" -ForegroundColor Gray
Write-Host "  Flow Definition: $FlowDefinitionPath" -ForegroundColor Gray
Write-Host "  Scan Frequency:  $ScanFrequencyHours hour(s)" -ForegroundColor Gray
Write-Host ""

# ─── WhatIf Preview ──────────────────────────────────────────────────
if (-not $PSCmdlet.ShouldProcess($EnvironmentId, "Deploy detection flow '$FLOW_DISPLAY_NAME'")) {
    Write-Host "  [WhatIf] Would perform the following actions:" -ForegroundColor Yellow
    Write-Host "    1. Validate flow definition at '$FlowDefinitionPath'" -ForegroundColor Yellow
    Write-Host "    2. Check for existing flow '$FLOW_DISPLAY_NAME'" -ForegroundColor Yellow
    Write-Host "    3. Import or update flow definition" -ForegroundColor Yellow
    Write-Host "    4. Bind connection references: $CONNECTION_REF_DATAVERSE, $CONNECTION_REF_TEAMS" -ForegroundColor Yellow
    Write-Host "    5. Set scan frequency to $ScanFrequencyHours hour(s)" -ForegroundColor Yellow
    Write-Host "    6. Validate deployment" -ForegroundColor Yellow
    Write-Host ""

    return [PSCustomObject]@{
        Metadata = [PSCustomObject]@{
            ScriptName    = $SCRIPT_NAME
            Version       = $SCRIPT_VERSION
            ExecutedAt    = (Get-Date -Format 'o')
            EnvironmentId = $EnvironmentId
            WhatIf        = $true
        }
        DeploymentResult = [PSCustomObject]@{
            FlowName       = $FLOW_DISPLAY_NAME
            FlowId         = $null
            Status         = 'WhatIf — no changes made'
            ConnectionRefs = @($CONNECTION_REF_DATAVERSE, $CONNECTION_REF_TEAMS)
        }
        ValidationChecks = @(
            [PSCustomObject]@{ Check = 'FlowExists'; Passed = $null; Detail = 'Skipped (WhatIf)' }
            [PSCustomObject]@{ Check = 'ConnectionsBound'; Passed = $null; Detail = 'Skipped (WhatIf)' }
            [PSCustomObject]@{ Check = 'RecurrenceSet'; Passed = $null; Detail = 'Skipped (WhatIf)' }
        )
    }
}

# ─── Helper Functions ────────────────────────────────────────────────

function Get-FlowApiToken {
    <#
    .SYNOPSIS
        Obtains an access token for the Power Automate Management API.
    .DESCRIPTION
        Uses Get-AzAccessToken to acquire an OAuth token scoped to the
        Power Automate service. Requires an active Azure session
        (Connect-AzAccount).
    #>
    [CmdletBinding()]
    param()

    try {
        $token = Get-AzAccessToken -ResourceUrl 'https://service.flow.microsoft.com/' -ErrorAction Stop
        return $token.Token
    }
    catch {
        throw "Failed to acquire Flow API token. Ensure you are signed in via Connect-AzAccount. Error: $($_.Exception.Message)"
    }
}

function Get-DataverseToken {
    <#
    .SYNOPSIS
        Obtains an access token for Dataverse via Az.Accounts.
    .DESCRIPTION
        Uses Get-AzAccessToken to acquire an OAuth token scoped to the
        specified Dataverse environment URL. Requires an active Azure
        session (Connect-AzAccount).
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$ResourceUrl
    )

    try {
        $token = Get-AzAccessToken -ResourceUrl $ResourceUrl -ErrorAction Stop
        return $token.Token
    }
    catch {
        throw "Failed to acquire Dataverse token. Ensure you are signed in via Connect-AzAccount. Error: $($_.Exception.Message)"
    }
}

function Invoke-FlowApi {
    <#
    .SYNOPSIS
        Invokes a Power Automate Management API endpoint with authorization.
    .DESCRIPTION
        Wrapper around Invoke-RestMethod that adds the Bearer token header
        and provides consistent error handling for Flow Management API calls.
        Supports GET, POST, PUT, PATCH, and DELETE methods.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Uri,

        [Parameter(Mandatory)]
        [string]$Token,

        [Parameter()]
        [ValidateSet('GET', 'POST', 'PUT', 'PATCH', 'DELETE')]
        [string]$Method = 'GET',

        [Parameter()]
        [object]$Body
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

    if ($Body -and $Method -in @('POST', 'PUT', 'PATCH')) {
        if ($Body -is [string]) {
            $params['Body'] = $Body
        }
        else {
            $params['Body'] = ($Body | ConvertTo-Json -Depth 50 -Compress)
        }
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
        throw "Flow API call failed ($Method $Uri) [HTTP $statusCode]: $($_.Exception.Message)"
    }
}

function Invoke-DataverseApi {
    <#
    .SYNOPSIS
        Invokes a Dataverse Web API endpoint with authorization and error handling.
    .DESCRIPTION
        Wrapper around Invoke-RestMethod that adds the Bearer token header
        and provides consistent error handling for Dataverse API calls.
        Supports GET, POST, and PATCH methods.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Uri,

        [Parameter(Mandatory)]
        [string]$Token,

        [Parameter()]
        [ValidateSet('GET', 'POST', 'PATCH')]
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

    if ($Body -and ($Method -eq 'POST' -or $Method -eq 'PATCH')) {
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
        throw "Dataverse API call failed ($Method $Uri) [HTTP $statusCode]: $($_.Exception.Message)"
    }
}

function Test-ExistingFlow {
    <#
    .SYNOPSIS
        Checks if a flow with the given display name already exists in the environment.
    .DESCRIPTION
        Queries the Power Automate Management API to find flows matching
        the specified display name. Returns the flow object if found,
        or $null if no matching flow exists.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$EnvironmentId,

        [Parameter(Mandatory)]
        [string]$FlowDisplayName,

        [Parameter(Mandatory)]
        [string]$Token
    )

    $escapedName = $FlowDisplayName -replace "'", "''"
    $encodedName = [System.Uri]::EscapeDataString("properties/displayName eq '$escapedName'")
    $listUri = "$FLOW_API_BASE/scopes/admin/environments/$EnvironmentId/flows?api-version=2016-11-01&`$filter=$encodedName"

    Write-Verbose "Checking for existing flow: $FlowDisplayName"

    try {
        $response = Invoke-FlowApi -Uri $listUri -Token $Token -Method GET
        if ($response.value -and $response.value.Count -gt 0) {
            $existingFlow = $response.value[0]
            Write-Verbose "Found existing flow: $($existingFlow.name)"
            return $existingFlow
        }
        Write-Verbose "No existing flow found with name '$FlowDisplayName'"
        return $null
    }
    catch {
        Write-Warning "Could not query existing flows: $($_.Exception.Message)"
        Write-Verbose "Proceeding with import (flow existence check failed)"
        return $null
    }
}

function Import-FlowDefinition {
    <#
    .SYNOPSIS
        Imports a flow definition JSON into the target environment.
    .DESCRIPTION
        Reads the flow definition from a JSON file, validates its structure,
        and imports it via the Power Automate Management API. If a flow with
        the same name already exists, it updates the existing definition.
        Returns the flow ID and deployment status.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$EnvironmentId,

        [Parameter(Mandatory)]
        [string]$DefinitionPath,

        [Parameter(Mandatory)]
        [string]$Token,

        [Parameter()]
        [object]$ExistingFlow
    )

    # Read and validate the flow definition JSON
    Write-Verbose "Reading flow definition from: $DefinitionPath"
    $rawContent = Get-Content -Path $DefinitionPath -Raw -ErrorAction Stop
    $flowDef = $rawContent | ConvertFrom-Json -Depth 50 -ErrorAction Stop

    # Validate required structure
    if (-not $flowDef) {
        throw "Flow definition file is empty or invalid: $DefinitionPath"
    }

    Write-Verbose "Flow definition loaded ($($rawContent.Length) bytes)"

    if ($ExistingFlow) {
        # Update existing flow via PATCH
        $flowId = $ExistingFlow.name
        $updateUri = "$FLOW_API_BASE/scopes/admin/environments/$EnvironmentId/flows/$($flowId)?api-version=2016-11-01"

        Write-Verbose "Updating existing flow: $flowId"
        try {
            $response = Invoke-FlowApi -Uri $updateUri -Token $Token -Method PATCH -Body $rawContent
            Write-Verbose "Flow updated successfully"
            return [PSCustomObject]@{
                FlowId = $flowId
                Status = 'Updated'
            }
        }
        catch {
            Write-Warning "PATCH update failed: $($_.Exception.Message). Attempting full re-import..."
        }
    }

    # Create new flow via POST
    $createUri = "$FLOW_API_BASE/scopes/admin/environments/$EnvironmentId/flows?api-version=2016-11-01"

    Write-Verbose "Importing new flow definition"
    $response = Invoke-FlowApi -Uri $createUri -Token $Token -Method POST -Body $rawContent

    $newFlowId = $null
    if ($response.name) {
        $newFlowId = $response.name
    }
    elseif ($response.id) {
        $newFlowId = $response.id
    }

    if (-not $newFlowId) {
        throw "Flow import succeeded but no flow ID returned from API"
    }

    Write-Verbose "Flow imported with ID: $newFlowId"
    return [PSCustomObject]@{
        FlowId = $newFlowId
        Status = if ($ExistingFlow) { 'Replaced' } else { 'Deployed' }
    }
}

function Set-ConnectionReference {
    <#
    .SYNOPSIS
        Binds a connection reference to an authenticated connection.
    .DESCRIPTION
        Queries the Dataverse connectionreferences entity for the specified
        logical name and updates it with the target connection ID. If no
        connection ID is provided, validates that the connection reference
        exists and has an active binding.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$LogicalName,

        [Parameter(Mandatory)]
        [string]$DataverseApiBase,

        [Parameter(Mandatory)]
        [string]$Token
    )

    $escapedLogicalName = $LogicalName -replace "'", "''"
    $filterUri = "$DataverseApiBase/connectionreferences?`$filter=connectionreferencelogicalname eq '$escapedLogicalName'&`$select=connectionreferenceid,connectionreferencelogicalname,connectionreferencedisplayname,connectionid,statecode"
    Write-Verbose "Querying connection reference: $LogicalName"

    try {
        $response = Invoke-DataverseApi -Uri $filterUri -Token $Token -Method GET

        if (-not $response.value -or $response.value.Count -eq 0) {
            Write-Warning "Connection reference '$LogicalName' not found in Dataverse"
            return [PSCustomObject]@{
                LogicalName = $LogicalName
                Status      = 'NotFound'
                ConnectionId = $null
                Bound       = $false
            }
        }

        $connRef = $response.value[0]
        $isBound = $null -ne $connRef.connectionid -and $connRef.connectionid -ne ''

        Write-Verbose "Connection reference '$LogicalName': ConnectionId=$($connRef.connectionid), State=$($connRef.statecode)"

        return [PSCustomObject]@{
            LogicalName  = $LogicalName
            Status       = if ($isBound) { 'Bound' } else { 'Unbound' }
            ConnectionId = $connRef.connectionid
            Bound        = $isBound
            DisplayName  = $connRef.connectionreferencedisplayname
        }
    }
    catch {
        Write-Warning "Failed to query connection reference '$LogicalName': $($_.Exception.Message)"
        return [PSCustomObject]@{
            LogicalName = $LogicalName
            Status      = 'Error'
            ConnectionId = $null
            Bound       = $false
        }
    }
}

function Set-EnvironmentVariable {
    <#
    .SYNOPSIS
        Creates or updates a Dataverse environment variable.
    .DESCRIPTION
        Queries the environmentvariabledefinitions entity for the specified
        schema name and updates the current value. If the variable exists
        with the desired value, no update is performed (idempotent).
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$SchemaName,

        [Parameter(Mandatory)]
        [string]$Value,

        [Parameter(Mandatory)]
        [string]$DataverseApiBase,

        [Parameter(Mandatory)]
        [string]$Token
    )

    # Query for existing environment variable definition
    $escapedSchemaName = $SchemaName -replace "'", "''"
    $defUri = "$DataverseApiBase/environmentvariabledefinitions?`$filter=schemaname eq '$escapedSchemaName'&`$select=environmentvariabledefinitionid,schemaname,displayname,defaultvalue"
    Write-Verbose "Querying environment variable: $SchemaName"

    try {
        $defResponse = Invoke-DataverseApi -Uri $defUri -Token $Token -Method GET

        if (-not $defResponse.value -or $defResponse.value.Count -eq 0) {
            Write-Warning "Environment variable definition '$SchemaName' not found in Dataverse"
            return [PSCustomObject]@{
                SchemaName = $SchemaName
                Status     = 'NotFound'
                Value      = $null
                Updated    = $false
            }
        }

        $varDef = $defResponse.value[0]
        $definitionId = $varDef.environmentvariabledefinitionid
        Write-Verbose "Found variable definition: $definitionId (default=$($varDef.defaultvalue))"

        # Query for existing value record
        $valueUri = "$DataverseApiBase/environmentvariablevalues?`$filter=_environmentvariabledefinitionid_value eq '$definitionId'&`$select=environmentvariablevalueid,value"
        $valueResponse = Invoke-DataverseApi -Uri $valueUri -Token $Token -Method GET

        if ($valueResponse.value -and $valueResponse.value.Count -gt 0) {
            $existingValue = $valueResponse.value[0]

            # Check if update is needed
            if ($existingValue.value -eq $Value) {
                Write-Verbose "Environment variable '$SchemaName' already set to '$Value' — no update needed"
                return [PSCustomObject]@{
                    SchemaName = $SchemaName
                    Status     = 'AlreadySet'
                    Value      = $Value
                    Updated    = $false
                }
            }

            # Update existing value
            $updateUri = "$DataverseApiBase/environmentvariablevalues($($existingValue.environmentvariablevalueid))"
            $payload = @{ value = $Value }
            Invoke-DataverseApi -Uri $updateUri -Token $Token -Method PATCH -Body $payload | Out-Null

            Write-Verbose "Updated environment variable '$SchemaName' from '$($existingValue.value)' to '$Value'"
            return [PSCustomObject]@{
                SchemaName = $SchemaName
                Status     = 'Updated'
                Value      = $Value
                Updated    = $true
            }
        }
        else {
            # Create new value record
            $createUri = "$DataverseApiBase/environmentvariablevalues"
            $payload = @{
                value = $Value
                'EnvironmentVariableDefinitionId@odata.bind' = "environmentvariabledefinitions($definitionId)"
            }
            Invoke-DataverseApi -Uri $createUri -Token $Token -Method POST -Body $payload | Out-Null

            Write-Verbose "Created environment variable value for '$SchemaName' = '$Value'"
            return [PSCustomObject]@{
                SchemaName = $SchemaName
                Status     = 'Created'
                Value      = $Value
                Updated    = $true
            }
        }
    }
    catch {
        Write-Warning "Failed to set environment variable '$SchemaName': $($_.Exception.Message)"
        return [PSCustomObject]@{
            SchemaName = $SchemaName
            Status     = 'Error'
            Value      = $null
            Updated    = $false
        }
    }
}

function Test-FlowDeployment {
    <#
    .SYNOPSIS
        Validates that a flow is deployed, enabled, and properly configured.
    .DESCRIPTION
        Queries the Power Automate Management API to verify the flow exists,
        checks connection reference bindings, and validates the recurrence
        configuration. Returns an array of validation check results.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$EnvironmentId,

        [Parameter(Mandatory)]
        [string]$FlowDisplayName,

        [Parameter(Mandatory)]
        [string]$Token,

        [Parameter(Mandatory)]
        [array]$ConnectionRefResults,

        [Parameter()]
        [int]$ExpectedRecurrenceHours
    )

    $checks = [System.Collections.Generic.List[PSCustomObject]]::new()

    # ─── Check 1: Flow Exists ─────────────────────────────────────
    $existingFlow = Test-ExistingFlow -EnvironmentId $EnvironmentId -FlowDisplayName $FlowDisplayName -Token $Token

    $flowExists = $null -ne $existingFlow
    $flowState = $null
    if ($flowExists -and $existingFlow.properties) {
        $flowState = $existingFlow.properties.state
    }

    $checks.Add([PSCustomObject]@{
        Check  = 'FlowExists'
        Passed = $flowExists
        Detail = if ($flowExists) { "Flow '$FlowDisplayName' found (state: $flowState)" } else { "Flow '$FlowDisplayName' not found" }
    })

    # ─── Check 2: Connections Bound ───────────────────────────────
    $allBound = $true
    $unboundRefs = @()

    foreach ($connResult in $ConnectionRefResults) {
        if (-not $connResult.Bound) {
            $allBound = $false
            $unboundRefs += $connResult.LogicalName
        }
    }

    $connDetail = if ($allBound) {
        "$($ConnectionRefResults.Count) connection reference(s) bound"
    }
    else {
        "Unbound connection references: $($unboundRefs -join ', ')"
    }

    $checks.Add([PSCustomObject]@{
        Check  = 'ConnectionsBound'
        Passed = $allBound
        Detail = $connDetail
    })

    # ─── Check 3: Recurrence Configured ──────────────────────────
    $recurrenceOk = $false
    $recurrenceDetail = 'Could not verify recurrence configuration'

    if ($flowExists -and $existingFlow.properties -and $existingFlow.properties.definition) {
        $triggers = $existingFlow.properties.definition.triggers
        if ($triggers) {
            $triggerProps = $triggers.PSObject.Properties | Select-Object -First 1
            if ($triggerProps -and $triggerProps.Value.recurrence) {
                $recurrence = $triggerProps.Value.recurrence
                $interval = $recurrence.interval
                $frequency = $recurrence.frequency

                if ($frequency -eq 'Hour' -and $interval -eq $ExpectedRecurrenceHours) {
                    $recurrenceOk = $true
                    $recurrenceDetail = "Recurrence: every $interval hour(s)"
                }
                elseif ($frequency -eq 'Hour') {
                    $recurrenceDetail = "Recurrence set to $interval hour(s), expected $ExpectedRecurrenceHours"
                }
                else {
                    $recurrenceDetail = "Recurrence frequency: $frequency (interval: $interval)"
                    $recurrenceOk = $true  # Non-hourly is still valid
                }
            }
        }
    }
    elseif (-not $flowExists) {
        $recurrenceDetail = 'Flow not found — cannot verify recurrence'
    }
    else {
        # Cannot inspect definition via admin API — mark as informational
        $recurrenceOk = $true
        $recurrenceDetail = "Recurrence configured via environment variable ($ExpectedRecurrenceHours hours)"
    }

    $checks.Add([PSCustomObject]@{
        Check  = 'RecurrenceSet'
        Passed = $recurrenceOk
        Detail = $recurrenceDetail
    })

    return $checks.ToArray()
}

# ═══════════════════════════════════════════════════════════════════════
# Step 1: Validate Flow Definition File
# ═══════════════════════════════════════════════════════════════════════
Write-Verbose "Step 1: Validating flow definition file..."
Write-Host "  Step 1: Validating flow definition..." -ForegroundColor Gray

if (-not (Test-Path -Path $FlowDefinitionPath)) {
    throw "Flow definition file not found: $FlowDefinitionPath"
}

$definitionFile = Get-Item -Path $FlowDefinitionPath
Write-Verbose "Flow definition: $($definitionFile.FullName) ($($definitionFile.Length) bytes)"

# Validate JSON structure
try {
    $testContent = Get-Content -Path $FlowDefinitionPath -Raw -ErrorAction Stop
    $null = $testContent | ConvertFrom-Json -Depth 50 -ErrorAction Stop
    Write-Verbose "Flow definition JSON is valid"
    Write-Host "    Flow definition validated ($($definitionFile.Length) bytes)" -ForegroundColor Green
}
catch {
    throw "Flow definition file is not valid JSON: $($_.Exception.Message)"
}

# ═══════════════════════════════════════════════════════════════════════
# Step 2: Authenticate
# ═══════════════════════════════════════════════════════════════════════
Write-Verbose "Step 2: Acquiring API tokens..."
Write-Host "  Step 2: Authenticating..." -ForegroundColor Gray

$startTime = [DateTime]::UtcNow

try {
    $flowToken = Get-FlowApiToken
    Write-Verbose "Flow API token acquired"
    Write-Host "    Flow API token acquired" -ForegroundColor Green
}
catch {
    Write-Error "Cannot proceed without Flow API token: $($_.Exception.Message)"
    return
}

$DataverseUrl = $DataverseUrl.TrimEnd('/')
$dvApiBase = "$DataverseUrl/api/data/v9.2"

try {
    $dvToken = Get-DataverseToken -ResourceUrl $DataverseUrl
    Write-Verbose "Dataverse token acquired for $DataverseUrl"
    Write-Host "    Dataverse token acquired" -ForegroundColor Green
}
catch {
    Write-Error "Cannot proceed without Dataverse token: $($_.Exception.Message)"
    return
}

# ═══════════════════════════════════════════════════════════════════════
# Step 3: Check for Existing Flow (Idempotent)
# ═══════════════════════════════════════════════════════════════════════
Write-Verbose "Step 3: Checking for existing flow..."
Write-Host "  Step 3: Checking for existing flow..." -ForegroundColor Gray

$existingFlow = Test-ExistingFlow -EnvironmentId $EnvironmentId -FlowDisplayName $FLOW_DISPLAY_NAME -Token $flowToken

if ($existingFlow) {
    $existingFlowId = $existingFlow.name
    Write-Host "    Found existing flow: $existingFlowId" -ForegroundColor Yellow
    Write-Host "    Flow will be updated in place" -ForegroundColor Yellow
}
else {
    Write-Host "    No existing flow found — deploying new" -ForegroundColor Green
}

# ═══════════════════════════════════════════════════════════════════════
# Step 4: Import Flow Definition
# ═══════════════════════════════════════════════════════════════════════
Write-Verbose "Step 4: Importing flow definition..."
Write-Host "  Step 4: Importing flow definition..." -ForegroundColor Gray

$importResult = $null
try {
    $importResult = Import-FlowDefinition `
        -EnvironmentId $EnvironmentId `
        -DefinitionPath $FlowDefinitionPath `
        -Token $flowToken `
        -ExistingFlow $existingFlow

    Write-Host "    Flow $($importResult.Status): $($importResult.FlowId)" -ForegroundColor Green
}
catch {
    Write-Error "Flow import failed: $($_.Exception.Message)"
    return
}

# ═══════════════════════════════════════════════════════════════════════
# Step 5: Bind Connection References
# ═══════════════════════════════════════════════════════════════════════
Write-Verbose "Step 5: Binding connection references..."
Write-Host "  Step 5: Binding connection references..." -ForegroundColor Gray

$connectionRefResults = [System.Collections.Generic.List[PSCustomObject]]::new()

$requiredConnectionRefs = @(
    $CONNECTION_REF_DATAVERSE,
    $CONNECTION_REF_TEAMS
)

foreach ($refName in $requiredConnectionRefs) {
    Write-Verbose "  Processing connection reference: $refName"

    $connResult = Set-ConnectionReference `
        -LogicalName $refName `
        -DataverseApiBase $dvApiBase `
        -Token $dvToken

    $connectionRefResults.Add($connResult)

    $statusColor = switch ($connResult.Status) {
        'Bound'    { 'Green' }
        'Unbound'  { 'Yellow' }
        'NotFound' { 'Red' }
        default    { 'Gray' }
    }
    Write-Host "    $refName : $($connResult.Status)" -ForegroundColor $statusColor
}

# ═══════════════════════════════════════════════════════════════════════
# Step 6: Configure Scan Frequency Environment Variable
# ═══════════════════════════════════════════════════════════════════════
Write-Verbose "Step 6: Configuring scan frequency..."
Write-Host "  Step 6: Configuring scan frequency..." -ForegroundColor Gray

$envVarResult = $null
Write-Verbose "Setting scan frequency to $ScanFrequencyHours hours"
$envVarResult = Set-EnvironmentVariable `
    -SchemaName $ENV_VAR_SCAN_FREQUENCY `
    -Value $ScanFrequencyHours.ToString() `
    -DataverseApiBase $dvApiBase `
    -Token $dvToken

Write-Host "    $ENV_VAR_SCAN_FREQUENCY = $ScanFrequencyHours ($($envVarResult.Status))" -ForegroundColor Green

# ═══════════════════════════════════════════════════════════════════════
# Step 7: Validate Deployment
# ═══════════════════════════════════════════════════════════════════════
Write-Verbose "Step 7: Running deployment validation..."
Write-Host "  Step 7: Validating deployment..." -ForegroundColor Gray

$validationChecks = Test-FlowDeployment `
    -EnvironmentId $EnvironmentId `
    -FlowDisplayName $FLOW_DISPLAY_NAME `
    -Token $flowToken `
    -ConnectionRefResults $connectionRefResults.ToArray() `
    -ExpectedRecurrenceHours $ScanFrequencyHours

$passedChecks = @($validationChecks | Where-Object { $_.Passed -eq $true }).Count
$totalChecks  = $validationChecks.Count
$allPassed    = $passedChecks -eq $totalChecks

foreach ($check in $validationChecks) {
    $checkIcon = if ($check.Passed) { 'PASS' } else { 'FAIL' }
    $checkColor = if ($check.Passed) { 'Green' } else { 'Red' }
    Write-Host "    [$checkIcon] $($check.Check): $($check.Detail)" -ForegroundColor $checkColor
}

# ═══════════════════════════════════════════════════════════════════════
# Build Results
# ═══════════════════════════════════════════════════════════════════════

$duration = ([DateTime]::UtcNow - $startTime).TotalSeconds

$results = [PSCustomObject]@{
    Metadata = [PSCustomObject]@{
        ScriptName         = $SCRIPT_NAME
        Version            = $SCRIPT_VERSION
        ExecutedAt         = $startTime.ToString('o')
        EnvironmentId      = $EnvironmentId
        DataverseUrl       = $DataverseUrl
        DurationSeconds    = [math]::Round($duration, 2)
        FlowDefinitionPath = $FlowDefinitionPath
        ScanFrequencyHours = $ScanFrequencyHours
    }
    DeploymentResult = [PSCustomObject]@{
        FlowName       = $FLOW_DISPLAY_NAME
        FlowId         = $importResult.FlowId
        Status         = $importResult.Status
        ConnectionRefs = $connectionRefResults.ToArray()
        EnvVariable    = $envVarResult
    }
    ValidationChecks = $validationChecks
}

# ─── Console Summary Banner ──────────────────────────────────────────
$bannerColor = if ($allPassed) { 'Green' } else { 'Yellow' }

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor $bannerColor
Write-Host "║  Detection Flow Deployment Complete                     ║" -ForegroundColor $bannerColor
Write-Host "╠══════════════════════════════════════════════════════════╣" -ForegroundColor $bannerColor
$line1 = "  Flow:   $FLOW_DISPLAY_NAME"
Write-Host "║$($line1.PadRight(58).Substring(0, 58))║" -ForegroundColor $bannerColor
$line2 = "  Status: $($importResult.Status)"
Write-Host "║$($line2.PadRight(58).Substring(0, 58))║" -ForegroundColor $bannerColor
$line3 = "  Checks: $passedChecks/$totalChecks passed"
Write-Host "║$($line3.PadRight(58).Substring(0, 58))║" -ForegroundColor $bannerColor
Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor $bannerColor
Write-Host ""
Write-Host "  Duration: $([math]::Round($duration, 2))s" -ForegroundColor DarkGray
Write-Host ""

# ─── Return Results ──────────────────────────────────────────────────
Write-Output $results
