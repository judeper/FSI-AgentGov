# CAAClient.psm1 — Dataverse Web API client for Conditional Access Automation
# Phase 2 — Working Dataverse Web API implementations

# Module-scoped connection state
$script:DataverseUrl = $null
$script:AccessToken = $null
$script:Headers = $null

function Connect-CAADataverse {
    <#
    .SYNOPSIS
        Establishes a connection to a Dataverse environment for CAA operations.
    .DESCRIPTION
        Sets module-scoped connection state (URL, access token, headers) and validates
        connectivity by querying the organizations endpoint.
    .PARAMETER DataverseUrl
        The Dataverse environment URL (e.g., https://org.crm.dynamics.com).
    .PARAMETER AccessToken
        A valid OAuth2 bearer token for the Dataverse environment.
    .EXAMPLE
        Connect-CAADataverse -DataverseUrl 'https://org.crm.dynamics.com' -AccessToken $token
    #>
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory)]
        [string]$DataverseUrl,

        [Parameter(Mandatory)]
        [string]$AccessToken
    )

    $script:DataverseUrl = $DataverseUrl.TrimEnd('/')
    $script:AccessToken = $AccessToken
    $script:Headers = @{
        'Authorization' = "Bearer $AccessToken"
        'OData-MaxVersion' = '4.0'
        'OData-Version' = '4.0'
        'Accept' = 'application/json'
        'Prefer' = 'return=representation'
    }

    # Validate connectivity
    $testUri = "$($script:DataverseUrl)/api/data/v9.2/organizations"
    try {
        $null = Invoke-RestMethod -Uri $testUri -Headers $script:Headers -Method Get
        Write-Verbose "CAAClient: Connected to $($script:DataverseUrl)"
    }
    catch {
        $script:DataverseUrl = $null
        $script:AccessToken = $null
        $script:Headers = $null
        Write-Warning "CAAClient: Failed to connect to Dataverse — $($_.Exception.Message)"
        return
    }
}

function Get-CAAConnection {
    <#
    .SYNOPSIS
        Returns the current Dataverse connection status.
    .DESCRIPTION
        Returns a PSCustomObject with IsConnected and Url properties indicating
        whether a Dataverse connection has been established.
    .EXAMPLE
        $conn = Get-CAAConnection
        if ($conn.IsConnected) { Write-Host "Connected to $($conn.Url)" }
    #>
    [CmdletBinding()]
    param()

    return [PSCustomObject]@{
        IsConnected = ($null -ne $script:DataverseUrl)
        Url         = $script:DataverseUrl
    }
}

function Get-CAAEnvironmentVariable {
    <#
    .SYNOPSIS
        Retrieves a CAA environment variable value from Dataverse.
    .DESCRIPTION
        Queries the environmentvariabledefinitions entity for the specified
        fsi_CAA_{Name} variable, expanding values to return the current override
        or the default value.
    .PARAMETER Name
        The short name of the environment variable (without the fsi_CAA_ prefix).
    .EXAMPLE
        $hours = Get-CAAEnvironmentVariable -Name 'GracePeriodHours'
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Name
    )

    $schemaName = "fsi_CAA_$Name"
    $uri = "$($script:DataverseUrl)/api/data/v9.2/environmentvariabledefinitions" +
           "?`$filter=schemaname eq '$schemaName'" +
           "&`$expand=environmentvariablevalues"
    try {
        $response = Invoke-RestMethod -Uri $uri -Headers $script:Headers -Method Get
        if ($response.value.Count -eq 0) {
            Write-Warning "CAAClient: Environment variable '$schemaName' not found."
            return $null
        }
        $definition = $response.value[0]
        # Return override value if present, otherwise fall back to default
        if ($definition.environmentvariablevalues -and $definition.environmentvariablevalues.Count -gt 0) {
            return $definition.environmentvariablevalues[0].value
        }
        return $definition.defaultvalue
    }
    catch {
        Write-Warning "CAAClient: Failed to query environment variable '$schemaName' — $($_.Exception.Message)"
        return $null
    }
}

function Get-CAAActiveBaseline {
    <#
    .SYNOPSIS
        Retrieves active CA policy baselines from Dataverse.
    .DESCRIPTION
        Queries the fsi_capolicybaselines entity for records where fsi_is_active
        is true, with optional filtering by policy ID and tenant ID.
    .PARAMETER PolicyId
        Optional. Filter baselines by CA policy GUID.
    .PARAMETER TenantId
        Optional. Filter baselines by tenant GUID.
    .EXAMPLE
        $baselines = Get-CAAActiveBaseline -TenantId $tenantId
    #>
    [CmdletBinding()]
    param(
        [Parameter()]
        [string]$PolicyId,

        [Parameter()]
        [string]$TenantId
    )

    $filters = @('fsi_is_active eq true')
    if ($PolicyId) { $filters += "fsi_policy_id eq '$PolicyId'" }
    if ($TenantId) { $filters += "fsi_tenant_id eq '$TenantId'" }
    $filterString = $filters -join ' and '
    $uri = "$($script:DataverseUrl)/api/data/v9.2/fsi_capolicybaselines?`$filter=$filterString"
    try {
        $response = Invoke-RestMethod -Uri $uri -Headers $script:Headers -Method Get
        return $response.value
    }
    catch {
        Write-Warning "CAAClient: Failed to query fsi_capolicybaselines — $($_.Exception.Message)"
        return $null
    }
}

function Write-CAAValidationHistory {
    <#
    .SYNOPSIS
        Creates an immutable validation history record in Dataverse.
    .DESCRIPTION
        Posts a new record to the fsi_capolicyvalidationhistory entity with
        aggregated compliance scan results. Records are immutable once created.
    .PARAMETER RunId
        Unique validation run identifier (GUID).
    .PARAMETER TotalPolicies
        Number of CA policies evaluated.
    .PARAMETER PassedCount
        Policies passing all checks.
    .PARAMETER WarningCount
        Policies with warnings.
    .PARAMETER FailedCount
        Policies failing validation.
    .PARAMETER DriftCount
        Policies with detected drift from baseline.
    .PARAMETER OverallSeverity
        Worst-case severity (1=Passed through 5=Error).
    .PARAMETER ResultsJson
        Full validation results payload as JSON string.
    .PARAMETER ValidatedBy
        UPN or SPN that executed the validation.
    .PARAMETER TenantId
        Entra ID tenant GUID.
    .EXAMPLE
        Write-CAAValidationHistory -RunId $runId -TotalPolicies 8 -PassedCount 6 -WarningCount 1 -FailedCount 1 -DriftCount 0 -OverallSeverity 4 -ResultsJson $json -ValidatedBy 'admin@contoso.com' -TenantId $tenantId
    #>
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory)]
        [string]$RunId,

        [Parameter(Mandatory)]
        [int]$TotalPolicies,

        [Parameter(Mandatory)]
        [int]$PassedCount,

        [Parameter(Mandatory)]
        [int]$WarningCount,

        [Parameter(Mandatory)]
        [int]$FailedCount,

        [Parameter(Mandatory)]
        [int]$DriftCount,

        [Parameter(Mandatory)]
        [int]$OverallSeverity,

        [Parameter(Mandatory)]
        [string]$ResultsJson,

        [Parameter(Mandatory)]
        [string]$ValidatedBy,

        [Parameter(Mandatory)]
        [string]$TenantId
    )

    $uri = "$($script:DataverseUrl)/api/data/v9.2/fsi_capolicyvalidationhistory"
    $body = @{
        fsi_run_id           = $RunId
        fsi_validation_time  = [DateTime]::UtcNow.ToString('o')
        fsi_total_policies   = $TotalPolicies
        fsi_passed_count     = $PassedCount
        fsi_warning_count    = $WarningCount
        fsi_failed_count     = $FailedCount
        fsi_drift_count      = $DriftCount
        fsi_overall_severity = $OverallSeverity
        fsi_results_json     = $ResultsJson
        fsi_validated_by     = $ValidatedBy
        fsi_tenant_id        = $TenantId
    }
    try {
        if ($PSCmdlet.ShouldProcess('fsi_capolicyvalidationhistory', "Create validation record $RunId")) {
            $response = Invoke-RestMethod -Uri $uri -Headers $script:Headers -Method Post `
                -Body ($body | ConvertTo-Json -Depth 10) -ContentType 'application/json'
            Write-Verbose "CAAClient: Created validation history record $RunId"
            return $response.fsi_capolicyvalidationhistoryid
        }
    }
    catch {
        Write-Warning "CAAClient: Failed to create validation history — $($_.Exception.Message)"
        return $null
    }
}

function Write-CAAViolation {
    <#
    .SYNOPSIS
        Creates a policy violation record in Dataverse.
    .DESCRIPTION
        Posts a new record to the fsi_capolicyviolations entity with details
        about a specific CA policy violation detected during validation.
    .PARAMETER RunId
        Links to the parent validation history run.
    .PARAMETER PolicyId
        Entra ID CA policy GUID.
    .PARAMETER PolicyDisplayName
        CA policy display name.
    .PARAMETER ViolationType
        Type of violation (PolicyDisabled, ConditionWeakened, GrantControlRemoved, etc.).
    .PARAMETER Zone
        Zone classification (1=Zone 1, 2=Zone 2, 3=Zone 3).
    .PARAMETER Severity
        Violation severity (1=Passed through 5=Error).
    .PARAMETER ExpectedValue
        What the baseline expected.
    .PARAMETER ActualValue
        What was found in the tenant.
    .PARAMETER Description
        Human-readable violation description.
    .PARAMETER TenantId
        Entra ID tenant GUID.
    .EXAMPLE
        Write-CAAViolation -RunId $runId -PolicyId $pid -PolicyDisplayName 'CA-M365Copilot-AllZones' -ViolationType 'PolicyDisabled' -Zone 3 -Severity 4 -Description 'Policy was disabled' -TenantId $tid
    #>
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory)]
        [string]$RunId,

        [Parameter(Mandatory)]
        [string]$PolicyId,

        [Parameter(Mandatory)]
        [string]$PolicyDisplayName,

        [Parameter(Mandatory)]
        [string]$ViolationType,

        [Parameter(Mandatory)]
        [int]$Zone,

        [Parameter(Mandatory)]
        [int]$Severity,

        [Parameter()]
        [string]$ExpectedValue,

        [Parameter()]
        [string]$ActualValue,

        [Parameter()]
        [string]$Description,

        [Parameter(Mandatory)]
        [string]$TenantId
    )

    $uri = "$($script:DataverseUrl)/api/data/v9.2/fsi_capolicyviolations"
    $body = @{
        fsi_run_id               = $RunId
        fsi_policy_id            = $PolicyId
        fsi_policy_display_name  = $PolicyDisplayName
        fsi_violation_type       = $ViolationType
        fsi_zone                 = $Zone
        fsi_severity             = $Severity
        fsi_tenant_id            = $TenantId
        fsi_is_resolved          = $false
    }
    if ($ExpectedValue)  { $body['fsi_expected_value'] = $ExpectedValue }
    if ($ActualValue)    { $body['fsi_actual_value']   = $ActualValue }
    if ($Description)    { $body['fsi_description']    = $Description }
    try {
        if ($PSCmdlet.ShouldProcess('fsi_capolicyviolations', "Create violation for policy $PolicyDisplayName")) {
            $response = Invoke-RestMethod -Uri $uri -Headers $script:Headers -Method Post `
                -Body ($body | ConvertTo-Json -Depth 10) -ContentType 'application/json'
            Write-Verbose "CAAClient: Created violation record for $PolicyDisplayName"
            return $response.fsi_capolicyviolationid
        }
    }
    catch {
        Write-Warning "CAAClient: Failed to create violation — $($_.Exception.Message)"
        return $null
    }
}

function Save-CAABaseline {
    <#
    .SYNOPSIS
        Saves a CA policy baseline snapshot to Dataverse.
    .DESCRIPTION
        Deactivates any existing active baseline for the policy, then creates
        a new active baseline record with the current configuration snapshot.
    .PARAMETER PolicyId
        Entra ID CA policy GUID.
    .PARAMETER PolicyDisplayName
        CA policy display name.
    .PARAMETER PolicyState
        Policy state (enabled, reportOnly, disabled).
    .PARAMETER Zone
        Zone classification (1=Zone 1, 2=Zone 2, 3=Zone 3).
    .PARAMETER ConditionsJson
        Full conditions object as JSON.
    .PARAMETER GrantControlsJson
        Grant control configuration as JSON.
    .PARAMETER SessionControlsJson
        Optional. Session control configuration as JSON.
    .PARAMETER BreakGlassExclusions
        Optional. Break-glass account GUIDs as JSON array.
    .PARAMETER BaselineHash
        SHA-256 hash of policy configuration.
    .PARAMETER CapturedBy
        UPN of user/SPN who captured the baseline.
    .PARAMETER TenantId
        Entra ID tenant GUID.
    .EXAMPLE
        Save-CAABaseline -PolicyId $pid -PolicyDisplayName 'CA-M365Copilot-AllZones' -PolicyState 'enabled' -Zone 3 -ConditionsJson $cjson -GrantControlsJson $gjson -BaselineHash $hash -CapturedBy 'admin@contoso.com' -TenantId $tid
    #>
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory)]
        [string]$PolicyId,

        [Parameter(Mandatory)]
        [string]$PolicyDisplayName,

        [Parameter(Mandatory)]
        [string]$PolicyState,

        [Parameter(Mandatory)]
        [int]$Zone,

        [Parameter(Mandatory)]
        [string]$ConditionsJson,

        [Parameter(Mandatory)]
        [string]$GrantControlsJson,

        [Parameter()]
        [string]$SessionControlsJson,

        [Parameter()]
        [string]$BreakGlassExclusions,

        [Parameter(Mandatory)]
        [string]$BaselineHash,

        [Parameter(Mandatory)]
        [string]$CapturedBy,

        [Parameter(Mandatory)]
        [string]$TenantId
    )

    $entitySet = 'fsi_capolicybaselines'
    try {
        # Step 1: Deactivate existing active baselines for this policy
        $deactivateFilter = "fsi_policy_id eq '$PolicyId' and fsi_is_active eq true"
        $queryUri = "$($script:DataverseUrl)/api/data/v9.2/$entitySet?`$filter=$deactivateFilter"
        $existing = Invoke-RestMethod -Uri $queryUri -Headers $script:Headers -Method Get

        foreach ($record in $existing.value) {
            $patchUri = "$($script:DataverseUrl)/api/data/v9.2/$entitySet($($record.fsi_capolicybaselineid))"
            $patchBody = @{ fsi_is_active = $false } | ConvertTo-Json
            if ($PSCmdlet.ShouldProcess($entitySet, "Deactivate baseline $($record.fsi_capolicybaselineid)")) {
                $null = Invoke-RestMethod -Uri $patchUri -Headers $script:Headers -Method Patch `
                    -Body $patchBody -ContentType 'application/json'
                Write-Verbose "CAAClient: Deactivated baseline $($record.fsi_capolicybaselineid)"
            }
        }

        # Step 2: Create new active baseline
        $body = @{
            fsi_policy_id            = $PolicyId
            fsi_policy_display_name  = $PolicyDisplayName
            fsi_policy_state         = $PolicyState
            fsi_zone                 = $Zone
            fsi_conditions_json      = $ConditionsJson
            fsi_grant_controls_json  = $GrantControlsJson
            fsi_baseline_hash        = $BaselineHash
            fsi_is_active            = $true
            fsi_captured_at          = [DateTime]::UtcNow.ToString('o')
            fsi_captured_by          = $CapturedBy
            fsi_tenant_id            = $TenantId
        }
        if ($SessionControlsJson)   { $body['fsi_session_controls_json']  = $SessionControlsJson }
        if ($BreakGlassExclusions)  { $body['fsi_break_glass_exclusions'] = $BreakGlassExclusions }

        $createUri = "$($script:DataverseUrl)/api/data/v9.2/$entitySet"
        if ($PSCmdlet.ShouldProcess($entitySet, "Create baseline for policy $PolicyDisplayName")) {
            $response = Invoke-RestMethod -Uri $createUri -Headers $script:Headers -Method Post `
                -Body ($body | ConvertTo-Json -Depth 10) -ContentType 'application/json'
            Write-Verbose "CAAClient: Created baseline for $PolicyDisplayName"
            return $response.fsi_capolicybaselineid
        }
    }
    catch {
        Write-Warning "CAAClient: Failed to save baseline for $PolicyDisplayName — $($_.Exception.Message)"
        return $null
    }
}

function Get-CAALastValidation {
    <#
    .SYNOPSIS
        Retrieves the most recent validation history record from Dataverse.
    .DESCRIPTION
        Queries the fsi_capolicyvalidationhistory entity ordered by validation
        time descending, returning the single most recent record.
    .PARAMETER TenantId
        Optional. Filter by tenant GUID.
    .EXAMPLE
        $last = Get-CAALastValidation -TenantId $tenantId
    #>
    [CmdletBinding()]
    param(
        [Parameter()]
        [string]$TenantId
    )

    $uri = "$($script:DataverseUrl)/api/data/v9.2/fsi_capolicyvalidationhistory" +
           "?`$orderby=fsi_validation_time desc&`$top=1"
    if ($TenantId) {
        $uri += "&`$filter=fsi_tenant_id eq '$TenantId'"
    }
    try {
        $response = Invoke-RestMethod -Uri $uri -Headers $script:Headers -Method Get
        if ($response.value.Count -eq 0) {
            return $null
        }
        return $response.value[0]
    }
    catch {
        Write-Warning "CAAClient: Failed to query last validation — $($_.Exception.Message)"
        return $null
    }
}

Export-ModuleMember -Function @(
    'Connect-CAADataverse'
    'Get-CAAConnection'
    'Get-CAAEnvironmentVariable'
    'Get-CAAActiveBaseline'
    'Write-CAAValidationHistory'
    'Write-CAAViolation'
    'Save-CAABaseline'
    'Get-CAALastValidation'
)
