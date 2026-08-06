<#
.SYNOPSIS
    Collects Power Platform Admin Center configuration data for FSI Agent Governance assessment.

.DESCRIPTION
    Enumerates Power Platform environments, DLP policies, role assignments, tenant
    settings, environment routing rules, inactivity timeout settings, security posture
    score, agent feature flags, environment groups, per-environment tags and group
    membership, and Copilot Studio bot inventory via Dataverse Web API.

    Outputs a structured JSON file (ppac.json) consumed by the assessment engine.

    BAP REST API patterns adapted from:
      - Set-InactivityTimeout.ps1 (Get-BapApiToken, Invoke-BapApi)
      - Invoke-SharingAudit.ps1 (environment enumeration via BAP API)
      - restrict-agent-publishing.ps1 (DLP and role assignment collection)
      - Invoke-HardeningBaselineCheck.ps1 (tenant settings, environment security checks)

.PARAMETER TenantId
    Mandatory. Microsoft Entra tenant ID.

.PARAMETER AuthMode
    Mandatory. Authentication mode: Interactive or ServicePrincipal.

.PARAMETER ClientId
    Optional. Application (client) ID for service principal authentication.

.PARAMETER ClientSecret
    Optional. Client secret as SecureString for service principal authentication.

.PARAMETER OutputDir
    Mandatory. Root output directory. Collected JSON is written to $OutputDir\collected\ppac.json.

.OUTPUTS
    ppac.json — JSON file with environments, DLP policies, role assignments, tenant
    settings, routing rules, inactivity timeout, security posture, agent feature flags,
    environment groups, per-environment tags/group membership, and Copilot Studio bot
    inventory from Dataverse `bot` rows.

.NOTES
    Part of the FSI Agent Governance Assessment Engine — PPAC Collector.
    Exit codes: 0 = success, 1 = partial failure (some sections null), 2 = total failure.
    Version: 1.0.0
#>

#Requires -Version 7.0

[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(Mandatory)]
    [ValidateNotNullOrEmpty()]
    [string]$TenantId,

    [Parameter(Mandatory)]
    [ValidateSet('Interactive', 'ServicePrincipal')]
    [string]$AuthMode,

    [Parameter()]
    [string]$ClientId,

    [Parameter()]
    [securestring]$ClientSecret,

    [Parameter(Mandatory)]
    [ValidateNotNullOrEmpty()]
    [string]$OutputDir
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

# ─── Initialise ──────────────────────────────────────────────────────
$warnings = [System.Collections.Generic.List[string]]::new()
$collectedDir = Join-Path $OutputDir 'collected'
if (-not (Test-Path $collectedDir)) {
    New-Item -ItemType Directory -Path $collectedDir -Force | Out-Null
}
$outputFile = Join-Path $collectedDir 'ppac.json'

# Shared collector helpers — Invoke-CollectorOperation (ShouldProcess wrapper with
# optional execution-status reporting), the DLP projection, and the StrictMode-safe
# property reader — live in the dot-sourced support module so their contracts are
# unit-testable without a live tenant.
$collectorRoot = Split-Path -Parent $PSCommandPath
. (Join-Path $collectorRoot 'lib\PpacCollectorSupport.ps1')

# ─── Module Import ───────────────────────────────────────────────────
Import-Module Microsoft.PowerApps.Administration.PowerShell -ErrorAction Stop
Write-Verbose "Loaded Microsoft.PowerApps.Administration.PowerShell module."

# ─── Authentication ──────────────────────────────────────────────────
# Pattern from restrict-agent-publishing.ps1 — Add-PowerAppsAccount for interactive,
# service principal path for automation.
Write-Verbose "Authenticating in $AuthMode mode..."

if ($AuthMode -eq 'Interactive') {
    Invoke-CollectorOperation -Target "Power Platform tenant $TenantId" -Action 'Connect to Power Platform Admin Center (interactive)' -ScriptBlock {
        Add-PowerAppsAccount -ErrorAction Stop
    } | Out-Null
}
else {
    if (-not $ClientId -or -not $ClientSecret) {
        throw "ServicePrincipal auth requires -ClientId and -ClientSecret parameters."
    }
    $credential = [System.Management.Automation.PSCredential]::new($ClientId, $ClientSecret)
    Invoke-CollectorOperation -Target "Power Platform tenant $TenantId" -Action 'Connect to Power Platform Admin Center (service principal)' -ScriptBlock {
        Add-PowerAppsAccount -Endpoint prod -TenantID $TenantId `
            -ApplicationId $ClientId -ClientSecret (ConvertFrom-SecureString $ClientSecret -AsPlainText) `
            -ErrorAction Stop
    } | Out-Null
}

Write-Verbose "Authentication stage complete."

# ─── BAP API Helper ──────────────────────────────────────────────────
# Adapted from Set-InactivityTimeout.ps1 Get-BapApiToken / Invoke-BapApi pattern.

function Get-BapApiToken {
    [CmdletBinding()]
    param()
    try {
        $tokenResult = Invoke-CollectorOperation -Target "BAP API tenant $TenantId" -Action 'Acquire access token' -ScriptBlock {
            Get-AzAccessToken -ResourceUrl "https://api.bap.microsoft.com" -ErrorAction Stop
        }
        if ($null -eq $tokenResult) {
            return $null
        }
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
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$Uri,
        [Parameter(Mandatory)][string]$Token,
        [Parameter()][ValidateSet('GET', 'POST', 'PATCH')][string]$Method = 'GET'
    )
    $headers = @{
        Authorization  = "Bearer $Token"
        'Content-Type' = 'application/json'
    }
    try {
        $response = Invoke-CollectorOperation -Target $Uri -Action "Invoke BAP API ($Method)" -ScriptBlock {
            Invoke-RestMethod -Uri $Uri -Method $Method -Headers $headers -ErrorAction Stop
        }
        return $response
    }
    catch {
        Write-Warning "BAP API call failed ($Method $Uri): $($_.Exception.Message)"
        return $null
    }
}

function Get-DataverseApiToken {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$ResourceUrl,
        [Parameter(Mandatory)][string]$EnvironmentName
    )

    try {
        $tokenResult = Invoke-CollectorOperation -Target $EnvironmentName -Action 'Acquire Dataverse access token' -ScriptBlock {
            Get-AzAccessToken -ResourceUrl $ResourceUrl -ErrorAction Stop
        }
        if ($null -eq $tokenResult) {
            return $null
        }
        if ($tokenResult.Token -is [securestring]) {
            return $tokenResult.Token | ConvertFrom-SecureString -AsPlainText
        }
        return $tokenResult.Token
    }
    catch {
        throw "Failed to acquire Dataverse token for '$EnvironmentName'. Ensure Connect-AzAccount has been completed. Error: $($_.Exception.Message)"
    }
}

# Acquire BAP token once for all REST API calls.
$bapToken = $null
try {
    $bapToken = Get-BapApiToken
    Write-Verbose "BAP API token acquired."
}
catch {
    $warnings.Add("BAP API token acquisition failed — REST-based sections will be skipped: $($_.Exception.Message)")
    Write-Warning $warnings[-1]
}

# ═══════════════════════════════════════════════════════════════════════
# Section 1: Environments
# Supports: Controls 2.1 (Managed Environments), 1.1 (Authentication Enforcement)
# Pattern: restrict-agent-publishing.ps1 Get-AdminPowerAppEnvironment
# ═══════════════════════════════════════════════════════════════════════
$environments = $null
try {
    Write-Verbose "Section 1: Collecting Power Platform environments..."
    $rawEnvs = Invoke-CollectorOperation -Target "Power Platform tenant $TenantId" -Action 'List Power Platform environments' -ScriptBlock {
        Get-AdminPowerAppEnvironment
    }
    $environments = $rawEnvs | ForEach-Object {
        $dataverseUrl = $null
        if ($_.Properties -and $_.Properties.linkedEnvironmentMetadata -and $_.Properties.linkedEnvironmentMetadata.instanceUrl) {
            $dataverseUrl = $_.Properties.linkedEnvironmentMetadata.instanceUrl
        }
        elseif ($_.Internal -and $_.Internal.properties -and $_.Internal.properties.linkedEnvironmentMetadata -and $_.Internal.properties.linkedEnvironmentMetadata.instanceUrl) {
            $dataverseUrl = $_.Internal.properties.linkedEnvironmentMetadata.instanceUrl
        }
        [PSCustomObject]@{
            DisplayName              = $_.DisplayName
            EnvironmentName          = $_.EnvironmentName
            IsDefault                = $_.IsDefault
            EnvironmentSku           = $_.Properties.environmentSku
            LinkedEnvironmentType    = $_.Properties.linkedEnvironmentMetadata.type
            SecurityGroupId          = $_.Properties.linkedEnvironmentMetadata.securityGroupId
            DataverseUrl             = $dataverseUrl
            States                   = $_.States
        }
    }
    Write-Verbose "  Collected $($environments.Count) environment(s)."
}
catch {
    $warnings.Add("Section 1 (Environments) failed: $($_.Exception.Message)")
    Write-Warning $warnings[-1]
}

# ═══════════════════════════════════════════════════════════════════════
# Section 2: DLP Policies
# Supports: Control 1.4 (DLP Connector Blocking)
# Pattern: restrict-agent-publishing.ps1 DLP criterion, Invoke-HardeningBaselineCheck.ps1
# ═══════════════════════════════════════════════════════════════════════
$dlpPolicies = $null
$dlpSpBypassWarning = $false
try {
    Write-Verbose "Section 2: Collecting DLP policies..."
    # -ExecutionStatus disambiguates a genuine no-row result (Get-DlpPolicy ran and
    # returned nothing) from a skipped operation (ShouldProcess declined / -WhatIf),
    # both of which return $null. Pre-seed to 'Skipped' so an early return is correct.
    $dlpCollectionStatus = 'Skipped'
    $rawDlp = Invoke-CollectorOperation -Target "Power Platform tenant $TenantId" -Action 'List DLP policies' -ExecutionStatus ([ref]$dlpCollectionStatus) -ScriptBlock {
        Get-DlpPolicy
    }
    if ($dlpCollectionStatus -eq 'Executed') {
        # Project raw Get-DlpPolicy output into the collected DLP contract. The helper
        # drops $null rows before projection so a no-policy tenant (Get-DlpPolicy
        # returned nothing -> $rawDlp is $null) yields [] instead of the
        # "$null | ForEach-Object" phantom that emitted one all-null placeholder policy
        # (which made the scorer report "malformed" and raised a false SP-bypass
        # warning). It also guarantees an array so ConvertTo-Json -Depth 10 cannot
        # collapse a singleton policy, comma-normalizes each policy's object-shaped
        # Environments, and reads every member StrictMode-safely so an absent optional
        # property (e.g. isEnabled) does not drop the policy or its environment scope.
        $dlpPolicies = ConvertTo-PpacDlpPolicyList -RawDlpPolicy $rawDlp
        Write-Verbose "  Collected $($dlpPolicies.Count) DLP policy/policies."
    }
    else {
        # ShouldProcess declined / -WhatIf: no DLP API call was made. Leave
        # $dlpPolicies = $null (unknown to the scorer) rather than [] so a dry-run skip
        # is never scored as "No classic DLP policies found", and dlpPolicies still
        # counts toward the all-null total-failure exit accounting below.
        $dlpSkipMsg = "Section 2 (DLP Policies) skipped (ShouldProcess declined / -WhatIf); " +
                      "DLP policy evidence not collected."
        $warnings.Add($dlpSkipMsg)
        Write-Warning $dlpSkipMsg
    }

    # ── IMPORTANT: Control 1.4 — Service Principal DLP Bypass Check ──
    # DLP policies applied via security groups do NOT cover Service Principal-based
    # connections. When a DLP policy exists but there is no evidence of SP connection
    # auditing, agents using app-only auth can bypass DLP entirely.
    # Flag this gap in output metadata for the assessment engine. A skipped or empty
    # collection leaves $dlpPolicies null/empty, so this check does not fire.
    if ($dlpPolicies -and $dlpPolicies.Count -gt 0) {
        # A full SP connection audit would require Dataverse connector usage logs.
        # At collection time we can only flag the absence of evidence.
        $dlpSpBypassWarning = $true
        $spWarningMsg = "Control 1.4 SP bypass: DLP policies found but no Service Principal " +
                        "connection audit evidence collected. SP-based connections may bypass " +
                        "DLP policies applied via security groups. Manual verification required."
        $warnings.Add($spWarningMsg)
        Write-Warning $spWarningMsg
    }
}
catch {
    $warnings.Add("Section 2 (DLP Policies) failed: $($_.Exception.Message)")
    Write-Warning $warnings[-1]
}

# ═══════════════════════════════════════════════════════════════════════
# Section 3: Role Assignments per Environment
# Supports: Control 1.1, 3.7 (Least-Privilege Access)
# Pattern: restrict-agent-publishing.ps1 Criterion 1 (Environment Maker Role)
# ═══════════════════════════════════════════════════════════════════════
$roleAssignments = $null
try {
    Write-Verbose "Section 3: Collecting environment role assignments..."
    if ($environments) {
        $roleAssignments = foreach ($env in $rawEnvs) {
            try {
                $roles = Invoke-CollectorOperation -Target $env.EnvironmentName -Action 'List environment role assignments' -ScriptBlock {
                    Get-AdminPowerAppEnvironmentRoleAssignment -EnvironmentName $env.EnvironmentName -ErrorAction Stop
                }
                [PSCustomObject]@{
                    EnvironmentName    = $env.EnvironmentName
                    DisplayName        = $env.DisplayName
                    Assignments        = $roles | ForEach-Object {
                        [PSCustomObject]@{
                            PrincipalType       = $_.PrincipalType
                            PrincipalObjectId   = $_.PrincipalObjectId
                            RoleDefinition      = $_.RoleDefinition
                        }
                    }
                }
            }
            catch {
                $warnings.Add("Role assignments for environment '$($env.DisplayName)' failed: $($_.Exception.Message)")
                Write-Warning $warnings[-1]
                [PSCustomObject]@{
                    EnvironmentName = $env.EnvironmentName
                    DisplayName     = $env.DisplayName
                    Assignments     = $null
                }
            }
        }
        Write-Verbose "  Collected role assignments for $(@($roleAssignments).Count) environment(s)."
    }
    else {
        $warnings.Add("Section 3 (Role Assignments): Skipped — no environments collected.")
        Write-Warning $warnings[-1]
    }
}
catch {
    $warnings.Add("Section 3 (Role Assignments) failed: $($_.Exception.Message)")
    Write-Warning $warnings[-1]
}

# ═══════════════════════════════════════════════════════════════════════
# Section 4: Tenant Settings
# Supports: Control 1.1.c (disableShareWithEveryone)
# Pattern: Get-TenantSettings
# ═══════════════════════════════════════════════════════════════════════
$tenantSettings = $null
try {
    Write-Verbose "Section 4: Collecting tenant settings..."
    $rawTenantSettings = Invoke-CollectorOperation -Target "Power Platform tenant $TenantId" -Action 'Get tenant settings' -ScriptBlock {
        Get-TenantSettings -ErrorAction Stop
    }

    if ($null -ne $rawTenantSettings) {
        $tenantSettings = [PSCustomObject]@{
            disableShareWithEveryone = $rawTenantSettings.disableShareWithEveryone
        }

        if ($null -eq $tenantSettings.disableShareWithEveryone) {
            $warnings.Add("Section 4 (Tenant Settings): disableShareWithEveryone was not present in Get-TenantSettings output.")
            Write-Warning $warnings[-1]
        }
        else {
            Write-Verbose "  disableShareWithEveryone captured as '$($tenantSettings.disableShareWithEveryone)'."
        }
    }
}
catch {
    $warnings.Add("Section 4 (Tenant Settings) failed: $($_.Exception.Message)")
    Write-Warning $warnings[-1]
}

# ═══════════════════════════════════════════════════════════════════════
# Section 5: Environment Routing Rules (BAP REST API)
# Supports: Control 2.1 (Managed Environments), routing configuration
# Pattern: Invoke-HardeningBaselineCheck.ps1 Item 15 (Environment Routing)
# ═══════════════════════════════════════════════════════════════════════
$routingRules = $null
try {
    Write-Verbose "Section 5: Collecting environment routing rules via BAP API..."
    if ($bapToken -and $environments) {
        $routingRules = foreach ($env in $rawEnvs) {
            $envId = $env.EnvironmentName
            $settingsUri = "https://api.bap.microsoft.com/providers/Microsoft.BusinessAppPlatform/scopes/admin/environments/$envId/settings?api-version=2021-04-01"
            $settings = Invoke-BapApi -Uri $settingsUri -Token $bapToken
            if ($settings) {
                [PSCustomObject]@{
                    EnvironmentName = $envId
                    DisplayName     = $env.DisplayName
                    RoutingRules    = $settings.routingRules
                }
            }
        }
        Write-Verbose "  Collected routing rules for $(@($routingRules).Count) environment(s)."
    }
    else {
        $warnings.Add("Section 5 (Routing Rules): Skipped — BAP token or environments unavailable.")
        Write-Warning $warnings[-1]
    }
}
catch {
    $warnings.Add("Section 5 (Routing Rules) failed: $($_.Exception.Message)")
    Write-Warning $warnings[-1]
}

# ═══════════════════════════════════════════════════════════════════════
# Section 6: Inactivity Timeout (BAP REST API)
# Supports: Control 2.22 (Inactivity Timeout Enforcement)
# Pattern: Set-InactivityTimeout.ps1 GET privacy settings endpoint
# ═══════════════════════════════════════════════════════════════════════
$inactivityTimeout = $null
try {
    Write-Verbose "Section 6: Collecting inactivity timeout settings via BAP API..."
    if ($bapToken -and $environments) {
        $inactivityTimeout = foreach ($env in $rawEnvs) {
            $envId = $env.EnvironmentName
            $settingsUri = "https://api.bap.microsoft.com/providers/Microsoft.BusinessAppPlatform/scopes/admin/environments/$envId/settings?api-version=2021-04-01"
            $settings = Invoke-BapApi -Uri $settingsUri -Token $bapToken
            if ($settings) {
                [PSCustomObject]@{
                    EnvironmentName          = $envId
                    DisplayName              = $env.DisplayName
                    SessionTimeoutInMinutes  = $settings.sessionTimeoutInMinutes
                }
            }
        }
        Write-Verbose "  Collected inactivity timeout for $(@($inactivityTimeout).Count) environment(s)."
    }
    else {
        $warnings.Add("Section 6 (Inactivity Timeout): Skipped — BAP token or environments unavailable.")
        Write-Warning $warnings[-1]
    }
}
catch {
    $warnings.Add("Section 6 (Inactivity Timeout) failed: $($_.Exception.Message)")
    Write-Warning $warnings[-1]
}

# ═══════════════════════════════════════════════════════════════════════
# Section 7: PPAC Security Posture Score (BAP REST API)
# Supports: Overall governance scoring
# ═══════════════════════════════════════════════════════════════════════
$securityPosture = $null
try {
    Write-Verbose "Section 7: Collecting PPAC Security Posture score via BAP API..."
    if ($bapToken) {
        $postureUri = "https://api.bap.microsoft.com/providers/Microsoft.BusinessAppPlatform/adminAnalytics/securityPosture?api-version=2021-04-01"
        $securityPosture = Invoke-BapApi -Uri $postureUri -Token $bapToken
        if ($securityPosture) {
            Write-Verbose "  Security Posture score collected."
        }
        else {
            $warnings.Add("Section 7 (Security Posture): API returned no data — endpoint may not be available for this tenant.")
            Write-Warning $warnings[-1]
        }
    }
    else {
        $warnings.Add("Section 7 (Security Posture): Skipped — BAP token unavailable.")
        Write-Warning $warnings[-1]
    }
}
catch {
    $warnings.Add("Section 7 (Security Posture) failed: $($_.Exception.Message)")
    Write-Warning $warnings[-1]
}

# ═══════════════════════════════════════════════════════════════════════
# Section 8: Agent Feature Flags (BAP REST API)
# Supports: Controls for generative AI features, external plugin toggles
# Pattern: Invoke-HardeningBaselineCheck.ps1 tenant settings for AI features
# ═══════════════════════════════════════════════════════════════════════
$agentFeatureFlags = $null
try {
    Write-Verbose "Section 8: Collecting agent feature flags via BAP API..."
    if ($bapToken -and $environments) {
        $agentFeatureFlags = foreach ($env in $rawEnvs) {
            $envId = $env.EnvironmentName
            $settingsUri = "https://api.bap.microsoft.com/providers/Microsoft.BusinessAppPlatform/scopes/admin/environments/$envId/settings?api-version=2021-04-01"
            $settings = Invoke-BapApi -Uri $settingsUri -Token $bapToken
            if ($settings) {
                [PSCustomObject]@{
                    EnvironmentName         = $envId
                    DisplayName             = $env.DisplayName
                    GenerativeAiFeatures    = $settings.generativeAiFeatures
                    ExternalPluginToggles   = $settings.externalPluginToggles
                    CopilotSettings         = $settings.copilotSettings
                }
            }
        }
        Write-Verbose "  Collected agent feature flags for $(@($agentFeatureFlags).Count) environment(s)."
    }
    else {
        $warnings.Add("Section 8 (Agent Feature Flags): Skipped — BAP token or environments unavailable.")
        Write-Warning $warnings[-1]
    }
}
catch {
    $warnings.Add("Section 8 (Agent Feature Flags) failed: $($_.Exception.Message)")
    Write-Warning $warnings[-1]
}

# ═══════════════════════════════════════════════════════════════════════
# Section 9: Environment Groups (BAP REST API)
# Supports: Frontier Q17 (tagged_environments_with_basic_telemetry)
# Pattern: BAP admin API for environment group enumeration
# ═══════════════════════════════════════════════════════════════════════
$environmentGroups = $null
try {
    Write-Verbose "Section 9: Collecting environment groups via BAP API..."
    if ($bapToken) {
        $groupsUri = "https://api.bap.microsoft.com/providers/Microsoft.BusinessAppPlatform/scopes/admin/environmentGroups?api-version=2021-04-01"
        $groupsResponse = Invoke-BapApi -Uri $groupsUri -Token $bapToken
        if ($null -ne $groupsResponse) {
            $groupItems = @()
            if ($groupsResponse.value) {
                $groupItems = $groupsResponse.value
            }
            elseif ($groupsResponse -is [System.Collections.IEnumerable] -and $groupsResponse -isnot [string]) {
                $groupItems = @($groupsResponse)
            }
            $environmentGroups = @(foreach ($grp in $groupItems) {
                $envCount = 0
                if ($grp.properties.environments) {
                    $envCount = @($grp.properties.environments).Count
                }
                [PSCustomObject]@{
                    Id               = $grp.id
                    DisplayName      = $grp.properties.displayName
                    Description      = $grp.properties.description
                    CreatedTime      = $grp.properties.createdTime
                    EnvironmentCount = $envCount
                }
            })
            Write-Verbose "  Collected $($environmentGroups.Count) environment group(s)."
        }
        else {
            $environmentGroups = @()
            $warnings.Add("Section 9 (Environment Groups): API returned no data — tenant may not have environment groups.")
            Write-Warning $warnings[-1]
        }
    }
    else {
        $warnings.Add("Section 9 (Environment Groups): Skipped — BAP token unavailable.")
        Write-Warning $warnings[-1]
    }
}
catch {
    $warnings.Add("Section 9 (Environment Groups) failed: $($_.Exception.Message)")
    Write-Warning $warnings[-1]
}

# ═══════════════════════════════════════════════════════════════════════
# Section 10: Per-Environment Tags + Group Membership (BAP REST API)
# Supports: Frontier Q17 (tagged_environments_with_basic_telemetry)
# Pattern: BAP admin API per-environment detail with $expand
# ═══════════════════════════════════════════════════════════════════════
try {
    Write-Verbose "Section 10: Enriching environments with tags and group membership..."
    if ($bapToken -and $environments) {
        foreach ($env in $environments) {
            $envId = $env.EnvironmentName
            try {
                $detailUri = "https://api.bap.microsoft.com/providers/Microsoft.BusinessAppPlatform/scopes/admin/environments/${envId}?api-version=2021-04-01&`$expand=permissions,properties.environmentGroup"
                $detail = Invoke-BapApi -Uri $detailUri -Token $bapToken
                if ($detail) {
                    $tags = @{}
                    if ($detail.properties.tags -and $detail.properties.tags -is [System.Collections.IDictionary]) {
                        $tags = $detail.properties.tags
                    }
                    elseif ($detail.properties.tags -is [psobject]) {
                        $detail.properties.tags.PSObject.Properties | ForEach-Object {
                            $tags[$_.Name] = $_.Value
                        }
                    }
                    $env | Add-Member -NotePropertyName 'Tags' -NotePropertyValue $tags -Force
                    $groupId = $null
                    if ($detail.properties.environmentGroup -and $detail.properties.environmentGroup.id) {
                        $groupId = $detail.properties.environmentGroup.id
                    }
                    $env | Add-Member -NotePropertyName 'EnvironmentGroupId' -NotePropertyValue $groupId -Force
                }
                else {
                    $env | Add-Member -NotePropertyName 'Tags' -NotePropertyValue @{} -Force
                    $env | Add-Member -NotePropertyName 'EnvironmentGroupId' -NotePropertyValue $null -Force
                    $warnings.Add("Section 10 (Tags): Detail API returned null for environment '$envId'.")
                    Write-Warning $warnings[-1]
                }
            }
            catch {
                $env | Add-Member -NotePropertyName 'Tags' -NotePropertyValue $null -Force
                $env | Add-Member -NotePropertyName 'EnvironmentGroupId' -NotePropertyValue $null -Force
                $warnings.Add("Section 10 (Tags) failed for environment '${envId}': $($_.Exception.Message)")
                Write-Warning $warnings[-1]
            }
        }
        Write-Verbose "  Enriched $(@($environments).Count) environment(s) with tags and group membership."
    }
    else {
        $warnings.Add("Section 10 (Tags): Skipped — BAP token or environments unavailable.")
        Write-Warning $warnings[-1]
    }
}
catch {
    $warnings.Add("Section 10 (Tags) failed: $($_.Exception.Message)")
    Write-Warning $warnings[-1]
}

# ═══════════════════════════════════════════════════════════════════════
# Section 11: Copilot Studio Bot Inventory (Dataverse Web API)
# Supports: Controls 1.2 / 3.1 inventory reconciliation
# Pattern: Dataverse `bot` table query (authoritative for Copilot Studio)
# ═══════════════════════════════════════════════════════════════════════
$copilotStudioBotInventory = $null
try {
    Write-Verbose "Section 11: Collecting Copilot Studio bot inventory via Dataverse Web API..."
    if ($environments) {
        $copilotStudioBotInventory = @(foreach ($env in $environments) {
            $envId = $env.EnvironmentName
            $dataverseUrl = $env.DataverseUrl
            $linkedEnvironmentType = [string]$env.LinkedEnvironmentType
            $linkedTypeNormalized = $linkedEnvironmentType.Trim().ToLowerInvariant()
            $isDataverseLinked = $linkedTypeNormalized -in @('dataverse', 'commondataservice')
            if ([string]::IsNullOrWhiteSpace($dataverseUrl)) {
                $status = if ($isDataverseLinked) { 'MissingDataverseUrl' } else { 'NoDataverse' }
                [PSCustomObject]@{
                    EnvironmentName      = $envId
                    DisplayName          = $env.DisplayName
                    LinkedEnvironmentType = $linkedEnvironmentType
                    DataverseUrl         = $null
                    Status               = $status
                    BotCount             = 0
                    Bots                 = @()
                }
                continue
            }

            $resourceUrl = $dataverseUrl.TrimEnd('/')
            $dataverseToken = $null
            try {
                $dataverseToken = Get-DataverseApiToken -ResourceUrl $resourceUrl -EnvironmentName $envId
            }
            catch {
                $warnings.Add("Section 11 (Bot Inventory): Token acquisition failed for environment '$envId': $($_.Exception.Message)")
                Write-Warning $warnings[-1]
                [PSCustomObject]@{
                    EnvironmentName      = $envId
                    DisplayName          = $env.DisplayName
                    LinkedEnvironmentType = $linkedEnvironmentType
                    DataverseUrl         = $resourceUrl
                    Status               = 'TokenFailed'
                    BotCount             = 0
                    Bots                 = $null
                }
                continue
            }

            if ([string]::IsNullOrWhiteSpace($dataverseToken)) {
                $warnings.Add("Section 11 (Bot Inventory): Empty Dataverse token for environment '$envId'.")
                Write-Warning $warnings[-1]
                [PSCustomObject]@{
                    EnvironmentName      = $envId
                    DisplayName          = $env.DisplayName
                    LinkedEnvironmentType = $linkedEnvironmentType
                    DataverseUrl         = $resourceUrl
                    Status               = 'TokenFailed'
                    BotCount             = 0
                    Bots                 = $null
                }
                continue
            }

            $headers = @{
                Authorization  = "Bearer $dataverseToken"
                'Content-Type' = 'application/json'
            }
            $nextLink = "$resourceUrl/api/data/v9.2/bots?`$select=botid,name,statecode,statuscode,createdon,modifiedon,schemaname,_ownerid_value"
            $rows = New-Object System.Collections.Generic.List[object]
            $pageGuard = 0

            try {
                while ($nextLink) {
                    $pageGuard++
                    if ($pageGuard -gt 200) {
                        throw "Pagination guard hit while collecting Dataverse bots for '$envId'."
                    }

                    $response = Invoke-CollectorOperation -Target $envId -Action 'List Dataverse bot rows' -ScriptBlock {
                        Invoke-RestMethod -Uri $nextLink -Method GET -Headers $headers -ErrorAction Stop
                    }

                    if ($null -eq $response) {
                        break
                    }

                    if ($response.value) {
                        foreach ($row in @($response.value)) {
                            if ($row -is [psobject]) {
                                $rows.Add([PSCustomObject]@{
                                    BotId       = $row.botid
                                    Name        = $row.name
                                    OwnerId     = $row.'_ownerid_value'
                                    StateCode   = $row.statecode
                                    StatusCode  = $row.statuscode
                                    CreatedOn   = $row.createdon
                                    ModifiedOn  = $row.modifiedon
                                    SchemaName  = $row.schemaname
                                })
                            }
                        }
                    }

                    $nextLink = $response.'@odata.nextLink'
                }

                [PSCustomObject]@{
                    EnvironmentName      = $envId
                    DisplayName          = $env.DisplayName
                    LinkedEnvironmentType = $linkedEnvironmentType
                    DataverseUrl         = $resourceUrl
                    Status               = 'Collected'
                    BotCount             = $rows.Count
                    Bots                 = @($rows)
                }
            }
            catch {
                $warnings.Add("Section 11 (Bot Inventory): Dataverse bot query failed for environment '$envId': $($_.Exception.Message)")
                Write-Warning $warnings[-1]
                [PSCustomObject]@{
                    EnvironmentName      = $envId
                    DisplayName          = $env.DisplayName
                    LinkedEnvironmentType = $linkedEnvironmentType
                    DataverseUrl         = $resourceUrl
                    Status               = 'QueryFailed'
                    BotCount             = 0
                    Bots                 = $null
                }
            }
        })

        Write-Verbose "  Collected Copilot Studio bot inventory for $($copilotStudioBotInventory.Count) environment record(s)."
    }
    else {
        $warnings.Add("Section 11 (Bot Inventory): Skipped — no environments collected.")
        Write-Warning $warnings[-1]
    }
}
catch {
    $warnings.Add("Section 11 (Bot Inventory) failed: $($_.Exception.Message)")
    Write-Warning $warnings[-1]
}

# ═══════════════════════════════════════════════════════════════════════
# Build Output
# ═══════════════════════════════════════════════════════════════════════
$result = [ordered]@{
    environments       = $environments
    dlpPolicies        = $dlpPolicies
    roleAssignments    = $roleAssignments
    tenantSettings     = $tenantSettings
    routingRules       = $routingRules
    inactivityTimeout  = $inactivityTimeout
    securityPosture    = $securityPosture
    agentFeatureFlags  = $agentFeatureFlags
    environmentGroups  = $environmentGroups
    copilotStudioBotInventory = $copilotStudioBotInventory
    _metadata          = [ordered]@{
        collector               = 'Collect-PPAC'
        timestamp               = (Get-Date -Format 'o')
        tenant_id               = $TenantId
        warnings                = @($warnings)
        dlpSpBypassWarning      = $dlpSpBypassWarning
    }
}

$json = $result | ConvertTo-Json -Depth 10
$json | Out-File -FilePath $outputFile -Encoding utf8
Write-Verbose "Output written to $outputFile"

# ─── Exit Code ───────────────────────────────────────────────────────
$nullSections = @(
    $environments, $dlpPolicies, $roleAssignments, $tenantSettings, $routingRules,
    $inactivityTimeout, $securityPosture, $agentFeatureFlags, $environmentGroups,
    $copilotStudioBotInventory
) | Where-Object { $null -eq $_ }

if ($nullSections.Count -eq 10) {
    Write-Error "All sections failed to collect data. See warnings for details."
    exit 2
}
elseif ($nullSections.Count -gt 0) {
    Write-Warning "Partial collection: $($nullSections.Count)/10 sections returned null."
    exit 1
}
else {
    Write-Verbose "All sections collected successfully."
    exit 0
}
