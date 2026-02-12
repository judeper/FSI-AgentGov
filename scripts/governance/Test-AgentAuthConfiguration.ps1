<#
.SYNOPSIS
    Validates per-agent authentication configuration against 6 SSPM items with zone-based logic.

.DESCRIPTION
    Scans Power Platform environments for agent authentication configuration using BAP APIs.
    Evaluates 6 SSPM items from Control 1.1 (Agent Authentication Enforcement):
    - SSPM-1.1-01: No Authentication — agents with authentication disabled
    - SSPM-1.1-02: Sign-in Required — agents without mandatory user sign-in
    - SSPM-1.1-03: Authentication Timing — agents using deferred (as-needed) authentication
    - SSPM-1.1-04: Sharing Scope — agents shared with overly broad audiences
    - SSPM-1.1-05: AI Feature Publishing — tenant policy for publishing bots with AI features
    - SSPM-1.1-06: Unapproved Agent Blocking — tenant controls for blocking unapproved agents

    Uses BAP API (api.bap.microsoft.com) for agent enumeration and authentication
    configuration retrieval. Tenant-level checks run once; per-agent checks iterate
    across environments. Zone-based logic applies different thresholds per governance
    zone (Zone 1 = Personal Productivity, Zone 2 = Team Collaboration, Zone 3 = Enterprise Managed).

    Does not write to Dataverse — output is console/JSON/file only.

.PARAMETER OutputFormat
    Output format for results. Valid values: Table, JSON, Object. Default: Table.

.PARAMETER OutputPath
    Optional file path to export JSON results. When omitted, results display to console only.

.PARAMETER EnvironmentFilter
    Optional array of environment names or display names to limit scope.
    When omitted, all environments are checked.

.PARAMETER ZoneMapping
    Optional hashtable mapping environment names to zone numbers (1, 2, or 3).
    Used for zone-specific validation thresholds.
    Example: @{ 'prod-env-1' = 3; 'dev-env-1' = 1 }

.PARAMETER IncludeEvidence
    When specified, computes SHA-256 integrity hash over results for evidence packaging.

.PARAMETER BaselinePath
    Optional path to a baseline JSON file for drift detection.
    Reserved for Plan 01-02 implementation — currently accepted but not processed.

.EXAMPLE
    .\Test-AgentAuthConfiguration.ps1
    Runs all 6 SSPM checks across all environments with default settings.

.EXAMPLE
    .\Test-AgentAuthConfiguration.ps1 -OutputFormat JSON -OutputPath .\evidence\auth-config.json -IncludeEvidence
    Full audit with JSON export and SHA-256 integrity hash.

.EXAMPLE
    .\Test-AgentAuthConfiguration.ps1 -EnvironmentFilter 'prod-env-1','prod-env-2' -ZoneMapping @{ 'prod-env-1' = 3; 'prod-env-2' = 2 }
    Scoped audit with zone-specific thresholds applied.

.OUTPUTS
    PSCustomObject with Metadata, Summary, Checks, and Gaps properties.

.NOTES
    Part of the FSI Agent Governance — Agent Authentication Enforcement.
    Controls: 1.1
    Version: 1.0.0
    Requires: Microsoft.PowerApps.Administration.PowerShell (2.0.0+)
#>

#Requires -Version 7.0
#Requires -Modules @{ ModuleName = 'Microsoft.PowerApps.Administration.PowerShell'; ModuleVersion = '2.0.0' }

[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter()]
    [ValidateSet('Table', 'JSON', 'Object')]
    [string]$OutputFormat = 'Table',

    [Parameter()]
    [string]$OutputPath,

    [Parameter()]
    [string[]]$EnvironmentFilter,

    [Parameter()]
    [hashtable]$ZoneMapping,

    [Parameter()]
    [switch]$IncludeEvidence,

    [Parameter()]
    [string]$BaselinePath
)

$ErrorActionPreference = 'Stop'

# ─── Banner ───────────────────────────────────────────────────────────
Write-Host "`n╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host   "║  FSI Agent Governance — Agent Auth Configuration Check  ║" -ForegroundColor Cyan
Write-Host   "╚══════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# ─── WhatIf Preview ──────────────────────────────────────────────────
if (-not $PSCmdlet.ShouldProcess("Power Platform tenant", "Run agent authentication configuration checks (SSPM-1.1-01 through SSPM-1.1-06)")) {
    Write-Verbose "WhatIf: Would check agent authentication configuration across environments"
    return
}

# ─── Helper Functions ────────────────────────────────────────────────

function Get-BapApiToken {
    <#
    .SYNOPSIS
        Obtains an access token for the BAP (Business Application Platform) API.
    .DESCRIPTION
        Uses Az.Accounts to acquire an OAuth token scoped to api.bap.microsoft.com.
        Requires an active Azure session (Connect-AzAccount).
    #>
    [CmdletBinding()]
    param()

    try {
        $token = Get-AzAccessToken -ResourceUrl "https://api.bap.microsoft.com" -ErrorAction Stop
        return $token.Token
    }
    catch {
        throw "Failed to acquire BAP API token. Ensure you are signed in via Connect-AzAccount. Error: $($_.Exception.Message)"
    }
}

function Invoke-BapApi {
    <#
    .SYNOPSIS
        Invokes a BAP API endpoint with authorization and error handling.
    .DESCRIPTION
        Wrapper around Invoke-RestMethod that adds the Bearer token header
        and provides consistent error handling for BAP API calls.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Uri,

        [Parameter(Mandatory)]
        [string]$Token,

        [Parameter()]
        [ValidateSet('GET', 'POST', 'PUT', 'PATCH', 'DELETE')]
        [string]$Method = 'GET'
    )

    try {
        $headers = @{
            Authorization  = "Bearer $Token"
            'Content-Type' = 'application/json'
        }
        $response = Invoke-RestMethod -Uri $Uri -Method $Method -Headers $headers -ErrorAction Stop
        return $response
    }
    catch {
        Write-Warning "BAP API call failed ($Method $Uri): $($_.Exception.Message)"
        return $null
    }
}

function Get-EnvironmentZone {
    <#
    .SYNOPSIS
        Returns the governance zone for a given environment.
    .DESCRIPTION
        Looks up the environment name in the ZoneMapping hashtable.
        Returns zone 1 (Personal Productivity) as default if not mapped.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$EnvironmentName,
        [Parameter()]
        [hashtable]$Mapping
    )
    if ($Mapping -and $Mapping.ContainsKey($EnvironmentName)) {
        return $Mapping[$EnvironmentName]
    }
    return 1  # Default to Zone 1 (least restrictive)
}

function New-AuthCheckResult {
    <#
    .SYNOPSIS
        Creates a standardized authentication check result object.
    .DESCRIPTION
        Produces a PSCustomObject representing a single SSPM check result
        with SSPM ID, status, zone context, and agent/environment details.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$SSPMId,

        [Parameter(Mandatory)]
        [int]$ItemNumber,

        [Parameter(Mandatory)]
        [string]$Setting,

        [Parameter(Mandatory)]
        [ValidateSet('Pass', 'Fail', 'Skip', 'Warning')]
        [string]$Status,

        [Parameter()]
        [string]$Expected,

        [Parameter()]
        [string]$Actual,

        [Parameter()]
        [string]$AgentId,

        [Parameter()]
        [string]$AgentName,

        [Parameter()]
        [string]$EnvironmentId,

        [Parameter()]
        [string]$EnvironmentName,

        [Parameter()]
        [int]$Zone = 1,

        [Parameter()]
        [string]$Message
    )

    [PSCustomObject]@{
        SSPMId          = $SSPMId
        ItemNumber      = $ItemNumber
        Setting         = $Setting
        Status          = $Status
        Expected        = $Expected
        Actual          = $Actual
        AgentId         = $AgentId
        AgentName       = $AgentName
        EnvironmentId   = $EnvironmentId
        EnvironmentName = $EnvironmentName
        Zone            = $Zone
        Message         = $Message
    }
}

# ─── Initialize Results ──────────────────────────────────────────────
$allChecks = [System.Collections.Generic.List[PSCustomObject]]::new()
$gaps = [System.Collections.Generic.List[string]]::new()
$startTime = [DateTime]::UtcNow

# ═══════════════════════════════════════════════════════════════════════
# Step 1: Authenticate and Get BAP API Token
# ═══════════════════════════════════════════════════════════════════════
Write-Verbose "Step 1: Acquiring BAP API token..."

try {
    $token = Get-BapApiToken
    Write-Verbose "BAP API token acquired successfully."
}
catch {
    Write-Error "Cannot proceed without BAP API token: $($_.Exception.Message)"
    return
}

# ═══════════════════════════════════════════════════════════════════════
# Step 2: Tenant-Level Checks (SSPM-1.1-05, SSPM-1.1-06)
# ═══════════════════════════════════════════════════════════════════════
Write-Verbose "Step 2: Tenant-level checks (SSPM-1.1-05, SSPM-1.1-06)..."

# ─── SSPM-1.1-05: AI Feature Publishing ──────────────────────────────
# Check tenant setting: powerPlatform.copilotStudio.publishBotsWithAIFeatures
# Zone 1: Pass (personal productivity — AI publishing acceptable)
# Zone 2/3: Fail if enabled (team/enterprise zones require restriction)

try {
    $tenantSettings = Get-TenantSettings

    $aiPublishingEnabled = $tenantSettings.powerPlatform.copilotStudio.publishBotsWithAIFeatures

    # Collect all unique zones present in the environment set
    # We need to enumerate environments first to know which zones are in scope
    # but we generate one result per zone for this tenant-level setting
    $zonesPresent = [System.Collections.Generic.HashSet[int]]::new()

    if ($ZoneMapping) {
        foreach ($z in $ZoneMapping.Values) {
            [void]$zonesPresent.Add([int]$z)
        }
    }

    # Always include Zone 1 (default)
    if ($zonesPresent.Count -eq 0) {
        [void]$zonesPresent.Add(1)
    }

    foreach ($zone in ($zonesPresent | Sort-Object)) {
        if ($zone -eq 1) {
            # Zone 1: AI publishing is acceptable for personal productivity
            $item05Status = 'Pass'
            $item05Message = 'AI feature publishing acceptable for Zone 1 (Personal Productivity)'
        }
        else {
            # Zone 2/3: AI publishing should be restricted
            $item05Status = if ($aiPublishingEnabled -eq $true) { 'Fail' } else { 'Pass' }
            $item05Message = if ($aiPublishingEnabled -eq $true) {
                "AI feature publishing is enabled but should be restricted for Zone $zone"
            }
            else {
                "AI feature publishing appropriately restricted for Zone $zone"
            }
        }

        $allChecks.Add((New-AuthCheckResult -SSPMId 'SSPM-1.1-05' -ItemNumber 5 `
            -Setting 'AI feature publishing (tenant-level)' `
            -Status $item05Status `
            -Expected "Zone ${zone}: $(if ($zone -eq 1) { 'No restriction required' } else { 'Publishing restricted' })" `
            -Actual "publishBotsWithAIFeatures=$aiPublishingEnabled" `
            -Zone $zone -Message $item05Message))

        if ($item05Status -eq 'Fail') {
            $gaps.Add("SSPM-1.1-05: AI feature publishing enabled — Zone $zone requires restriction")
        }
    }
}
catch {
    Write-Warning "SSPM-1.1-05 (AI Feature Publishing) failed: $($_.Exception.Message)"
    $allChecks.Add((New-AuthCheckResult -SSPMId 'SSPM-1.1-05' -ItemNumber 5 `
        -Setting 'AI feature publishing (tenant-level)' `
        -Status 'Skip' -Message "Error: $($_.Exception.Message)"))
}

# ─── SSPM-1.1-06: Unapproved Agent Blocking ──────────────────────────
# Attempt M365 Admin Center API. Gracefully Skip if unavailable.

try {
    # Attempt to check M365 Admin Center API for agent blocking policy
    # This API endpoint may not be available in all tenants
    $m365Token = Get-AzAccessToken -ResourceUrl "https://admin.microsoft.com" -ErrorAction Stop
    $blockingApiUrl = 'https://admin.microsoft.com/admin/api/settings/apps/botsapps'
    $blockingHeaders = @{
        Authorization  = "Bearer $($m365Token.Token)"
        'Content-Type' = 'application/json'
    }
    $blockingResponse = Invoke-RestMethod -Uri $blockingApiUrl -Method GET -Headers $blockingHeaders -ErrorAction Stop

    $blockingEnabled = $blockingResponse.isBlockingEnabled -eq $true
    $item06Status = if ($blockingEnabled) { 'Pass' } else { 'Fail' }
    $item06Actual = "BlockingEnabled=$blockingEnabled"

    $allChecks.Add((New-AuthCheckResult -SSPMId 'SSPM-1.1-06' -ItemNumber 6 `
        -Setting 'Unapproved agent blocking (tenant-level)' `
        -Status $item06Status `
        -Expected 'Unapproved agent blocking enabled' `
        -Actual $item06Actual))

    if ($item06Status -eq 'Fail') {
        $gaps.Add("SSPM-1.1-06: Unapproved agent blocking is not enabled at tenant level")
    }
}
catch {
    Write-Warning "SSPM-1.1-06 (Unapproved Agent Blocking) — API unavailable: $($_.Exception.Message)"
    $allChecks.Add((New-AuthCheckResult -SSPMId 'SSPM-1.1-06' -ItemNumber 6 `
        -Setting 'Unapproved agent blocking (tenant-level)' `
        -Status 'Skip' `
        -Message "M365 Admin Center API unavailable — verify manually in admin.microsoft.com > Settings > Org settings > Bot apps. Error: $($_.Exception.Message)"))
}

# ═══════════════════════════════════════════════════════════════════════
# Step 3: Enumerate Environments
# ═══════════════════════════════════════════════════════════════════════
Write-Verbose "Step 3: Enumerating Power Platform environments..."

$envApiUrl = 'https://api.bap.microsoft.com/providers/Microsoft.BusinessAppPlatform/scopes/admin/environments?api-version=2016-11-01'
$envResponse = Invoke-BapApi -Uri $envApiUrl -Token $token

if (-not $envResponse -or -not $envResponse.value) {
    Write-Warning "No environments returned from BAP API. Verify admin permissions."
    $environments = @()
}
else {
    $environments = $envResponse.value
    Write-Verbose "Found $($environments.Count) environment(s)."
}

# Apply environment filter if specified
if ($EnvironmentFilter -and $environments.Count -gt 0) {
    $environments = $environments | Where-Object {
        $envName = $_.name
        $envDisplayName = $_.properties.displayName
        ($EnvironmentFilter -contains $envName) -or ($EnvironmentFilter -contains $envDisplayName)
    }
    Write-Verbose "After filtering: $($environments.Count) environment(s) in scope."
}

$envCount = @($environments).Count

if ($envCount -eq 0) {
    Write-Warning "No environments in scope. Check -EnvironmentFilter values or admin permissions."
}

# ═══════════════════════════════════════════════════════════════════════
# Step 4: Per-Agent Checks (SSPM-1.1-01 through SSPM-1.1-04)
# ═══════════════════════════════════════════════════════════════════════
Write-Verbose "Step 4: Scanning per-agent authentication configuration..."

$totalAgentsScanned = 0
$environmentIndex = 0

foreach ($env in $environments) {
    $environmentIndex++
    $envId = $env.name
    $envDisplayName = $env.properties.displayName
    $zone = Get-EnvironmentZone -EnvironmentName $envId -Mapping $ZoneMapping

    Write-Verbose "[$environmentIndex/$envCount] Scanning environment: $envDisplayName ($envId) — Zone $zone"

    # ─── Step 4a: List agents in this environment ─────────────────────
    $agentsApiUrl = "https://api.bap.microsoft.com/providers/Microsoft.BusinessAppPlatform/environments/$envId/bots?api-version=2021-04-01"
    $agentsResponse = Invoke-BapApi -Uri $agentsApiUrl -Token $token

    if (-not $agentsResponse -or -not $agentsResponse.value) {
        Write-Verbose "  No agents found in environment '$envDisplayName'."
        continue
    }

    $agents = $agentsResponse.value
    Write-Verbose "  Found $($agents.Count) agent(s) in '$envDisplayName'."

    # ─── Step 4b: Evaluate each agent ─────────────────────────────────
    $agentIndex = 0
    foreach ($agent in $agents) {
        $agentIndex++
        $totalAgentsScanned++
        $agentId = $agent.name
        $agentName = $agent.properties.displayName
        if (-not $agentName) { $agentName = $agentId }

        Write-Verbose "    [$agentIndex/$($agents.Count)] Evaluating agent: $agentName ($agentId)"

        $authMode = $agent.properties.authenticationMode
        $requireUserAuth = $agent.properties.requireUserAuthentication
        $authTiming = $agent.properties.authenticationTiming

        # ─── SSPM-1.1-01: No Authentication ───────────────────────────
        # Check authenticationMode. NoAuthentication → Fail ALL zones.
        $noAuthDetected = ($authMode -eq 'NoAuthentication' -or $authMode -eq 'None' -or $null -eq $authMode)

        if ($noAuthDetected) {
            $allChecks.Add((New-AuthCheckResult -SSPMId 'SSPM-1.1-01' -ItemNumber 1 `
                -Setting 'Authentication mode' `
                -Status 'Fail' `
                -Expected 'Authentication enabled (any mode)' `
                -Actual "AuthenticationMode=$authMode" `
                -AgentId $agentId -AgentName $agentName `
                -EnvironmentId $envId -EnvironmentName $envDisplayName `
                -Zone $zone `
                -Message "Agent '$agentName' has no authentication configured — fails all zones"))

            $gaps.Add("SSPM-1.1-01: Agent '$agentName' in '$envDisplayName' (Zone $zone) has no authentication")
        }
        else {
            $allChecks.Add((New-AuthCheckResult -SSPMId 'SSPM-1.1-01' -ItemNumber 1 `
                -Setting 'Authentication mode' `
                -Status 'Pass' `
                -Expected 'Authentication enabled (any mode)' `
                -Actual "AuthenticationMode=$authMode" `
                -AgentId $agentId -AgentName $agentName `
                -EnvironmentId $envId -EnvironmentName $envDisplayName `
                -Zone $zone))
        }

        # ─── SSPM-1.1-02: Sign-in Required ────────────────────────────
        # If auth mode is Manual, check requireUserAuthentication.
        # Not enabled → Zone 1: Warning, Zone 2/3: Fail.
        if ($authMode -eq 'Manual' -or $authMode -eq 'GenericOAuth' -or $authMode -eq 'MicrosoftEntraId') {
            $signInRequired = ($requireUserAuth -eq $true)

            if (-not $signInRequired) {
                $item02Status = if ($zone -eq 1) { 'Warning' } else { 'Fail' }
                $item02Message = if ($zone -eq 1) {
                    "Sign-in not required — advisory for Zone 1"
                }
                else {
                    "Sign-in not required — Zone $zone requires mandatory user sign-in"
                }

                $allChecks.Add((New-AuthCheckResult -SSPMId 'SSPM-1.1-02' -ItemNumber 2 `
                    -Setting 'User sign-in requirement' `
                    -Status $item02Status `
                    -Expected "Zone ${zone}: User sign-in required" `
                    -Actual "RequireUserAuthentication=$requireUserAuth" `
                    -AgentId $agentId -AgentName $agentName `
                    -EnvironmentId $envId -EnvironmentName $envDisplayName `
                    -Zone $zone -Message $item02Message))

                if ($item02Status -eq 'Fail') {
                    $gaps.Add("SSPM-1.1-02: Agent '$agentName' in '$envDisplayName' (Zone $zone) does not require user sign-in")
                }
            }
            else {
                $allChecks.Add((New-AuthCheckResult -SSPMId 'SSPM-1.1-02' -ItemNumber 2 `
                    -Setting 'User sign-in requirement' `
                    -Status 'Pass' `
                    -Expected "Zone ${zone}: User sign-in required" `
                    -Actual "RequireUserAuthentication=$requireUserAuth" `
                    -AgentId $agentId -AgentName $agentName `
                    -EnvironmentId $envId -EnvironmentName $envDisplayName `
                    -Zone $zone))
            }
        }
        elseif ($noAuthDetected) {
            # Already captured by SSPM-1.1-01 — skip duplicate
            $allChecks.Add((New-AuthCheckResult -SSPMId 'SSPM-1.1-02' -ItemNumber 2 `
                -Setting 'User sign-in requirement' `
                -Status 'Skip' `
                -AgentId $agentId -AgentName $agentName `
                -EnvironmentId $envId -EnvironmentName $envDisplayName `
                -Zone $zone `
                -Message 'Skipped — agent has no authentication (see SSPM-1.1-01)'))
        }
        else {
            # Unknown or integrated auth — report actual value
            $allChecks.Add((New-AuthCheckResult -SSPMId 'SSPM-1.1-02' -ItemNumber 2 `
                -Setting 'User sign-in requirement' `
                -Status 'Pass' `
                -Expected "Zone ${zone}: User sign-in required" `
                -Actual "AuthenticationMode=$authMode (integrated auth)" `
                -AgentId $agentId -AgentName $agentName `
                -EnvironmentId $envId -EnvironmentName $envDisplayName `
                -Zone $zone `
                -Message 'Authentication mode provides integrated sign-in'))
        }

        # ─── SSPM-1.1-03: Authentication Timing ───────────────────────
        # Check authenticationTiming. "AsNeeded" → Zone 1: Warning, Zone 2/3: Fail.
        # "Always" → Pass.
        if (-not $noAuthDetected) {
            $timingIsDeferred = ($authTiming -eq 'AsNeeded' -or $authTiming -eq 'OnDemand' -or $authTiming -eq 'Deferred')
            $timingIsAlways = ($authTiming -eq 'Always' -or $authTiming -eq 'OnStart')

            if ($timingIsDeferred) {
                $item03Status = if ($zone -eq 1) { 'Warning' } else { 'Fail' }
                $item03Message = if ($zone -eq 1) {
                    "Deferred authentication timing — advisory for Zone 1"
                }
                else {
                    "Deferred authentication timing — Zone $zone requires authentication at start"
                }

                $allChecks.Add((New-AuthCheckResult -SSPMId 'SSPM-1.1-03' -ItemNumber 3 `
                    -Setting 'Authentication timing' `
                    -Status $item03Status `
                    -Expected "Zone ${zone}: Authentication at conversation start (Always)" `
                    -Actual "AuthenticationTiming=$authTiming" `
                    -AgentId $agentId -AgentName $agentName `
                    -EnvironmentId $envId -EnvironmentName $envDisplayName `
                    -Zone $zone -Message $item03Message))

                if ($item03Status -eq 'Fail') {
                    $gaps.Add("SSPM-1.1-03: Agent '$agentName' in '$envDisplayName' (Zone $zone) uses deferred authentication timing")
                }
            }
            elseif ($timingIsAlways) {
                $allChecks.Add((New-AuthCheckResult -SSPMId 'SSPM-1.1-03' -ItemNumber 3 `
                    -Setting 'Authentication timing' `
                    -Status 'Pass' `
                    -Expected "Zone ${zone}: Authentication at conversation start (Always)" `
                    -Actual "AuthenticationTiming=$authTiming" `
                    -AgentId $agentId -AgentName $agentName `
                    -EnvironmentId $envId -EnvironmentName $envDisplayName `
                    -Zone $zone))
            }
            else {
                # Unknown timing value — report for investigation
                $allChecks.Add((New-AuthCheckResult -SSPMId 'SSPM-1.1-03' -ItemNumber 3 `
                    -Setting 'Authentication timing' `
                    -Status 'Warning' `
                    -Expected "Zone ${zone}: Authentication at conversation start (Always)" `
                    -Actual "AuthenticationTiming=$authTiming" `
                    -AgentId $agentId -AgentName $agentName `
                    -EnvironmentId $envId -EnvironmentName $envDisplayName `
                    -Zone $zone `
                    -Message "Unknown authentication timing value '$authTiming' — verify manually"))
            }
        }
        else {
            # No authentication — skip timing check
            $allChecks.Add((New-AuthCheckResult -SSPMId 'SSPM-1.1-03' -ItemNumber 3 `
                -Setting 'Authentication timing' `
                -Status 'Skip' `
                -AgentId $agentId -AgentName $agentName `
                -EnvironmentId $envId -EnvironmentName $envDisplayName `
                -Zone $zone `
                -Message 'Skipped — agent has no authentication (see SSPM-1.1-01)'))
        }

        # ─── SSPM-1.1-04: Sharing Scope ───────────────────────────────
        # Query permissions endpoint. Org/Tenant/Public principal → Zone 1: Warning, Zone 2/3: Fail.
        $permissionsApiUrl = "https://api.bap.microsoft.com/providers/Microsoft.BusinessAppPlatform/environments/$envId/bots/$agentId/permissions?api-version=2021-04-01"
        $permissionsResponse = Invoke-BapApi -Uri $permissionsApiUrl -Token $token

        if ($permissionsResponse) {
            $principals = @()
            if ($permissionsResponse.value) {
                $principals = @($permissionsResponse.value)
            }

            # Check for overly broad sharing
            $broadPrincipals = @($principals | Where-Object {
                $pType = $_.properties.principalType
                $accessType = $_.properties.accessType
                ($pType -eq 'Organization' -or $pType -eq 'Tenant' -or
                 $pType -eq 'Public' -or $pType -eq 'Anonymous' -or
                 $accessType -eq 'Public')
            })

            if ($broadPrincipals.Count -gt 0) {
                $broadTypes = ($broadPrincipals | ForEach-Object {
                    $_.properties.principalType ?? $_.properties.accessType ?? 'Unknown'
                }) -join ', '

                $item04Status = if ($zone -eq 1) { 'Warning' } else { 'Fail' }
                $item04Message = if ($zone -eq 1) {
                    "Broad sharing detected ($broadTypes) — advisory for Zone 1"
                }
                else {
                    "Broad sharing detected ($broadTypes) — Zone $zone requires restricted sharing"
                }

                $allChecks.Add((New-AuthCheckResult -SSPMId 'SSPM-1.1-04' -ItemNumber 4 `
                    -Setting 'Sharing scope' `
                    -Status $item04Status `
                    -Expected "Zone ${zone}: Sharing restricted to specific users/groups" `
                    -Actual "BroadPrincipals=$($broadPrincipals.Count) ($broadTypes)" `
                    -AgentId $agentId -AgentName $agentName `
                    -EnvironmentId $envId -EnvironmentName $envDisplayName `
                    -Zone $zone -Message $item04Message))

                if ($item04Status -eq 'Fail') {
                    $gaps.Add("SSPM-1.1-04: Agent '$agentName' in '$envDisplayName' (Zone $zone) has broad sharing ($broadTypes)")
                }
            }
            else {
                $allChecks.Add((New-AuthCheckResult -SSPMId 'SSPM-1.1-04' -ItemNumber 4 `
                    -Setting 'Sharing scope' `
                    -Status 'Pass' `
                    -Expected "Zone ${zone}: Sharing restricted to specific users/groups" `
                    -Actual "Principals=$($principals.Count) (no broad sharing)" `
                    -AgentId $agentId -AgentName $agentName `
                    -EnvironmentId $envId -EnvironmentName $envDisplayName `
                    -Zone $zone))
            }
        }
        else {
            Write-Warning "    Could not retrieve permissions for agent '$agentName' in '$envDisplayName'."
            $allChecks.Add((New-AuthCheckResult -SSPMId 'SSPM-1.1-04' -ItemNumber 4 `
                -Setting 'Sharing scope' `
                -Status 'Skip' `
                -AgentId $agentId -AgentName $agentName `
                -EnvironmentId $envId -EnvironmentName $envDisplayName `
                -Zone $zone `
                -Message "Could not retrieve permissions — API returned null"))
        }
    }
}

# ═══════════════════════════════════════════════════════════════════════
# Results Aggregation
# ═══════════════════════════════════════════════════════════════════════

$passCount = ($allChecks | Where-Object { $_.Status -eq 'Pass' }).Count
$failCount = ($allChecks | Where-Object { $_.Status -eq 'Fail' }).Count
$skipCount = ($allChecks | Where-Object { $_.Status -eq 'Skip' }).Count
$warnCount = ($allChecks | Where-Object { $_.Status -eq 'Warning' }).Count
$totalChecks = $allChecks.Count
$duration = ([DateTime]::UtcNow - $startTime).TotalSeconds

$results = [PSCustomObject]@{
    Metadata = [PSCustomObject]@{
        ScriptName          = 'Test-AgentAuthConfiguration'
        ScriptVersion       = '1.0.0'
        CheckedAt           = $startTime.ToString('o')
        DurationSeconds     = [math]::Round($duration, 2)
        EnvironmentsScanned = $envCount
        AgentsScanned       = $totalAgentsScanned
        IntegrityHash       = $null
    }
    Summary = [PSCustomObject]@{
        TotalChecks   = $totalChecks
        Passed        = $passCount
        Failed        = $failCount
        Skipped       = $skipCount
        Warnings      = $warnCount
        OverallStatus = if ($failCount -eq 0) { 'Passed' } else { 'GapsFound' }
    }
    Checks = $allChecks.ToArray()
    Gaps   = $gaps.ToArray()
}

# ─── SHA-256 Evidence Hash ────────────────────────────────────────────
if ($IncludeEvidence) {
    $resultsJson = $results | ConvertTo-Json -Depth 10 -Compress
    $hashBytes = [System.Security.Cryptography.SHA256]::Create().ComputeHash(
        [System.Text.Encoding]::UTF8.GetBytes($resultsJson)
    )
    $results.Metadata.IntegrityHash = [BitConverter]::ToString($hashBytes) -replace '-'
}

# ─── Console Summary ─────────────────────────────────────────────────
Write-Host "`n╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host   "║  Agent Auth Configuration Check Complete                ║" -ForegroundColor Cyan
Write-Host   "╠══════════════════════════════════════════════════════════╣" -ForegroundColor Cyan
Write-Host   "║  Checks: $($totalChecks.ToString().PadRight(7)) Passed: $($passCount.ToString().PadRight(7)) Failed: $($failCount.ToString().PadRight(7))║" -ForegroundColor Cyan
Write-Host   "║  Skipped: $($skipCount.ToString().PadRight(6)) Warnings: $($warnCount.ToString().PadRight(5)) Agents: $($totalAgentsScanned.ToString().PadRight(7))║" -ForegroundColor Cyan
Write-Host   "║  Environments: $($envCount.ToString().PadRight(5)) Duration: $("$([math]::Round($duration, 2))s".PadRight(21))║" -ForegroundColor Cyan
Write-Host   "╚══════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

if ($IncludeEvidence -and $results.Metadata.IntegrityHash) {
    Write-Host "  Integrity Hash: $($results.Metadata.IntegrityHash)" -ForegroundColor DarkGray
}

# ─── Output ──────────────────────────────────────────────────────────
switch ($OutputFormat) {
    'JSON' {
        $json = $results | ConvertTo-Json -Depth 10
        if ($OutputPath) {
            $parentDir = Split-Path -Path $OutputPath -Parent
            if ($parentDir -and -not (Test-Path $parentDir)) {
                New-Item -ItemType Directory -Path $parentDir -Force | Out-Null
            }
            $json | Out-File -FilePath $OutputPath -Encoding utf8
            Write-Host "Results exported to: $OutputPath" -ForegroundColor Cyan
            if ($IncludeEvidence -and $results.Metadata.IntegrityHash) {
                Write-Host "Integrity hash: $($results.Metadata.IntegrityHash)" -ForegroundColor DarkGray
            }
        }
        else {
            Write-Output $json
        }
    }
    'Table' {
        $allChecks | Format-Table -Property SSPMId, Setting, AgentName, EnvironmentName, Zone, Status, Expected, Actual -AutoSize

        if ($gaps.Count -gt 0) {
            Write-Host "Gaps:" -ForegroundColor Yellow
            $gaps | ForEach-Object { Write-Host "  - $_" -ForegroundColor Yellow }
        }

        if ($OutputPath) {
            $parentDir = Split-Path -Path $OutputPath -Parent
            if ($parentDir -and -not (Test-Path $parentDir)) {
                New-Item -ItemType Directory -Path $parentDir -Force | Out-Null
            }
            $results | ConvertTo-Json -Depth 10 | Out-File -FilePath $OutputPath -Encoding utf8
            Write-Host "Results exported to: $OutputPath" -ForegroundColor Cyan
        }
    }
    'Object' {
        Write-Output $results
    }
}
