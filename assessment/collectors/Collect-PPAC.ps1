<#
.SYNOPSIS
    Collects Power Platform Admin Center configuration data for FSI Agent Governance assessment.

.DESCRIPTION
    Enumerates Power Platform environments, DLP policies, role assignments, environment
    routing rules, inactivity timeout settings, security posture score, and agent feature
    flags via the PowerApps Administration module and BAP REST API.

    Outputs a structured JSON file (ppac.json) consumed by the assessment engine.

    BAP REST API patterns adapted from:
      - Set-InactivityTimeout.ps1 (Get-BapApiToken, Invoke-BapApi)
      - Invoke-SharingAudit.ps1 (environment enumeration via BAP API)
      - restrict-agent-publishing.ps1 (DLP and role assignment collection)
      - Invoke-HardeningBaselineCheck.ps1 (tenant settings, environment security checks)

.PARAMETER TenantId
    Mandatory. Azure AD tenant ID.

.PARAMETER AuthMode
    Mandatory. Authentication mode: Interactive or ServicePrincipal.

.PARAMETER ClientId
    Optional. Application (client) ID for service principal authentication.

.PARAMETER ClientSecret
    Optional. Client secret as SecureString for service principal authentication.

.PARAMETER OutputDir
    Mandatory. Root output directory. Collected JSON is written to $OutputDir\collected\ppac.json.

.OUTPUTS
    ppac.json — JSON file with environments, DLP policies, role assignments, routing rules,
    inactivity timeout, security posture, and agent feature flags.

.NOTES
    Part of the FSI Agent Governance Assessment Engine — PPAC Collector.
    Exit codes: 0 = success, 1 = partial failure (some sections null), 2 = total failure.
    Version: 1.0.0
#>

#Requires -Version 7.0

[CmdletBinding()]
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

# ─── Module Import ───────────────────────────────────────────────────
Import-Module Microsoft.PowerApps.Administration.PowerShell -ErrorAction Stop
Write-Verbose "Loaded Microsoft.PowerApps.Administration.PowerShell module."

# ─── Authentication ──────────────────────────────────────────────────
# Pattern from restrict-agent-publishing.ps1 — Add-PowerAppsAccount for interactive,
# service principal path for automation.
Write-Verbose "Authenticating in $AuthMode mode..."

if ($AuthMode -eq 'Interactive') {
    Add-PowerAppsAccount -ErrorAction Stop
}
else {
    if (-not $ClientId -or -not $ClientSecret) {
        throw "ServicePrincipal auth requires -ClientId and -ClientSecret parameters."
    }
    $credential = [System.Management.Automation.PSCredential]::new($ClientId, $ClientSecret)
    Add-PowerAppsAccount -Endpoint prod -TenantID $TenantId `
        -ApplicationId $ClientId -ClientSecret (ConvertFrom-SecureString $ClientSecret -AsPlainText) `
        -ErrorAction Stop
}

Write-Verbose "Authentication successful."

# ─── BAP API Helper ──────────────────────────────────────────────────
# Adapted from Set-InactivityTimeout.ps1 Get-BapApiToken / Invoke-BapApi pattern.

function Get-BapApiToken {
    [CmdletBinding()]
    param()
    try {
        $tokenResult = Get-AzAccessToken -ResourceUrl "https://api.bap.microsoft.com" -ErrorAction Stop
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
        $response = Invoke-RestMethod -Uri $Uri -Method $Method -Headers $headers -ErrorAction Stop
        return $response
    }
    catch {
        Write-Warning "BAP API call failed ($Method $Uri): $($_.Exception.Message)"
        return $null
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
    $rawEnvs = Get-AdminPowerAppEnvironment
    $environments = $rawEnvs | ForEach-Object {
        [PSCustomObject]@{
            DisplayName              = $_.DisplayName
            EnvironmentName          = $_.EnvironmentName
            IsDefault                = $_.IsDefault
            EnvironmentSku           = $_.Properties.environmentSku
            LinkedEnvironmentType    = $_.Properties.linkedEnvironmentMetadata.type
            SecurityGroupId          = $_.Properties.linkedEnvironmentMetadata.securityGroupId
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
    $rawDlp = Get-DlpPolicy
    $dlpPolicies = $rawDlp | ForEach-Object {
        [PSCustomObject]@{
            DisplayName             = $_.displayName
            PolicyName              = $_.name
            CreatedTime             = $_.createdTime
            IsEnabled               = $_.isEnabled
            BusinessDataGroup       = $_.connectorGroups | Where-Object { $_.classification -eq 'Confidential' } |
                                        ForEach-Object { $_.connectors | Select-Object id, name }
            NonBusinessDataGroup    = $_.connectorGroups | Where-Object { $_.classification -eq 'General' } |
                                        ForEach-Object { $_.connectors | Select-Object id, name }
            BlockedGroup            = $_.connectorGroups | Where-Object { $_.classification -eq 'Blocked' } |
                                        ForEach-Object { $_.connectors | Select-Object id, name }
            EnvironmentType         = $_.environmentType
            Environments            = $_.environments
        }
    }

    # ── IMPORTANT: Control 1.4 — Service Principal DLP Bypass Check ──
    # DLP policies applied via security groups do NOT cover Service Principal-based
    # connections. When a DLP policy exists but there is no evidence of SP connection
    # auditing, agents using app-only auth can bypass DLP entirely.
    # Flag this gap in output metadata for the assessment engine.
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

    Write-Verbose "  Collected $($dlpPolicies.Count) DLP policy/policies."
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
                $roles = Get-AdminPowerAppEnvironmentRoleAssignment -EnvironmentName $env.EnvironmentName -ErrorAction Stop
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
# Section 4: Environment Routing Rules (BAP REST API)
# Supports: Control 2.1 (Managed Environments), routing configuration
# Pattern: Invoke-HardeningBaselineCheck.ps1 Item 15 (Environment Routing)
# ═══════════════════════════════════════════════════════════════════════
$routingRules = $null
try {
    Write-Verbose "Section 4: Collecting environment routing rules via BAP API..."
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
        $warnings.Add("Section 4 (Routing Rules): Skipped — BAP token or environments unavailable.")
        Write-Warning $warnings[-1]
    }
}
catch {
    $warnings.Add("Section 4 (Routing Rules) failed: $($_.Exception.Message)")
    Write-Warning $warnings[-1]
}

# ═══════════════════════════════════════════════════════════════════════
# Section 5: Inactivity Timeout (BAP REST API)
# Supports: Control 2.22 (Inactivity Timeout Enforcement)
# Pattern: Set-InactivityTimeout.ps1 GET privacy settings endpoint
# ═══════════════════════════════════════════════════════════════════════
$inactivityTimeout = $null
try {
    Write-Verbose "Section 5: Collecting inactivity timeout settings via BAP API..."
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
        $warnings.Add("Section 5 (Inactivity Timeout): Skipped — BAP token or environments unavailable.")
        Write-Warning $warnings[-1]
    }
}
catch {
    $warnings.Add("Section 5 (Inactivity Timeout) failed: $($_.Exception.Message)")
    Write-Warning $warnings[-1]
}

# ═══════════════════════════════════════════════════════════════════════
# Section 6: PPAC Security Posture Score (BAP REST API)
# Supports: Overall governance scoring
# ═══════════════════════════════════════════════════════════════════════
$securityPosture = $null
try {
    Write-Verbose "Section 6: Collecting PPAC Security Posture score via BAP API..."
    if ($bapToken) {
        $postureUri = "https://api.bap.microsoft.com/providers/Microsoft.BusinessAppPlatform/adminAnalytics/securityPosture?api-version=2021-04-01"
        $securityPosture = Invoke-BapApi -Uri $postureUri -Token $bapToken
        if ($securityPosture) {
            Write-Verbose "  Security Posture score collected."
        }
        else {
            $warnings.Add("Section 6 (Security Posture): API returned no data — endpoint may not be available for this tenant.")
            Write-Warning $warnings[-1]
        }
    }
    else {
        $warnings.Add("Section 6 (Security Posture): Skipped — BAP token unavailable.")
        Write-Warning $warnings[-1]
    }
}
catch {
    $warnings.Add("Section 6 (Security Posture) failed: $($_.Exception.Message)")
    Write-Warning $warnings[-1]
}

# ═══════════════════════════════════════════════════════════════════════
# Section 7: Agent Feature Flags (BAP REST API)
# Supports: Controls for generative AI features, external plugin toggles
# Pattern: Invoke-HardeningBaselineCheck.ps1 tenant settings for AI features
# ═══════════════════════════════════════════════════════════════════════
$agentFeatureFlags = $null
try {
    Write-Verbose "Section 7: Collecting agent feature flags via BAP API..."
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
        $warnings.Add("Section 7 (Agent Feature Flags): Skipped — BAP token or environments unavailable.")
        Write-Warning $warnings[-1]
    }
}
catch {
    $warnings.Add("Section 7 (Agent Feature Flags) failed: $($_.Exception.Message)")
    Write-Warning $warnings[-1]
}

# ═══════════════════════════════════════════════════════════════════════
# Build Output
# ═══════════════════════════════════════════════════════════════════════
$result = [ordered]@{
    environments       = $environments
    dlpPolicies        = $dlpPolicies
    roleAssignments    = $roleAssignments
    routingRules       = $routingRules
    inactivityTimeout  = $inactivityTimeout
    securityPosture    = $securityPosture
    agentFeatureFlags  = $agentFeatureFlags
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
    $environments, $dlpPolicies, $roleAssignments, $routingRules,
    $inactivityTimeout, $securityPosture, $agentFeatureFlags
) | Where-Object { $null -eq $_ }

if ($nullSections.Count -eq 7) {
    Write-Error "All sections failed to collect data. See warnings for details."
    exit 2
}
elseif ($nullSections.Count -gt 0) {
    Write-Warning "Partial collection: $($nullSections.Count)/7 sections returned null."
    exit 1
}
else {
    Write-Verbose "All sections collected successfully."
    exit 0
}
