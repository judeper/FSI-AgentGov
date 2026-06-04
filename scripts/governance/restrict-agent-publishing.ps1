<#
.SYNOPSIS
    Validates agent publishing restriction governance across 6 criteria.

.DESCRIPTION
    Checks 6 publishing restriction criteria against Power Platform tenant and environment
    settings to support agent publishing governance for US financial services organizations.

    Criteria validated:
    - Criterion 1: Environment Maker Role Removal — verifies broad "All Users" principal does
      not hold the Environment Maker role, helping restrict who can create and publish agents.
    - Criterion 2: Authorized Security Groups — verifies environments have an assigned security
      group controlling access, supporting least-privilege access patterns.
    - Criterion 3: Share with Everyone Disabled — verifies the tenant-level toggle that prevents
      agents from being shared with the entire organization is disabled.
    - Criterion 4: DLP Connector Blocking — verifies Data Loss Prevention policies block
      agent-related connectors in governed environments (semi-automated).
    - Criterion 5: Managed Environment Sharing Limits — verifies Managed Environment status
      and sharing limits are configured within zone-appropriate thresholds.
    - Criterion 6: Approval Workflow Active — verifies an approval workflow is configured for
      agent publishing in Zone 2/3 environments (semi-automated).

    Zone-based logic applies different thresholds per governance zone:
    - Zone 1 (Personal Productivity): Advisory warnings, minimal enforcement
    - Zone 2 (Team Collaboration): Moderate enforcement, sharing limits <= 20
    - Zone 3 (Enterprise Managed): Strict enforcement, sharing limits <= 5

    References Controls 1.1 (Agent Authentication Enforcement), 2.1 (Managed Environments),
    and 3.7 (Publishing Controls). Does not write to Dataverse — output is console/JSON/file only.

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

.EXAMPLE
    .\restrict-agent-publishing.ps1

    Runs all 6 publishing restriction criteria across all environments with default settings.

.EXAMPLE
    .\restrict-agent-publishing.ps1 -OutputFormat JSON -OutputPath .\evidence\publishing-check.json -IncludeEvidence

    Full audit with JSON export and SHA-256 integrity hash for regulatory evidence packaging.

.EXAMPLE
    .\restrict-agent-publishing.ps1 -EnvironmentFilter 'prod-env-1','prod-env-2' -ZoneMapping @{ 'prod-env-1' = 3; 'prod-env-2' = 2 }

    Scoped audit with zone-specific thresholds applied to selected environments.

.OUTPUTS
    PSCustomObject with Metadata, Summary, Checks, and Gaps properties.

.NOTES
    Part of the FSI Agent Governance — Publishing Restriction Governance.
    Controls: 1.1, 2.1, 3.7
    Version: 1.1.0
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
    [switch]$IncludeEvidence
)

$ErrorActionPreference = 'Stop'

# ─── Banner ───────────────────────────────────────────────────────────
Write-Host "`n╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host   "║  FSI Agent Governance — Publishing Restriction Check    ║" -ForegroundColor Cyan
Write-Host   "╚══════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# ─── WhatIf Preview ──────────────────────────────────────────────────
if (-not $PSCmdlet.ShouldProcess("Power Platform tenant", "Check 6 publishing restriction criteria across Power Platform environments")) {
    Write-Verbose "WhatIf: Would check 6 publishing restriction criteria across Power Platform environments"
    return
}

# ─── Helper Functions ────────────────────────────────────────────────

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

function New-PublishingCheckResult {
    <#
    .SYNOPSIS
        Creates a standardized publishing check result object.
    .DESCRIPTION
        Produces a PSCustomObject representing a single publishing restriction
        criterion result with zone context, environment details, and evidence hash.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [int]$CriterionNumber,

        [Parameter(Mandatory)]
        [string]$Setting,

        [Parameter(Mandatory)]
        [string]$CheckGroup,

        [Parameter(Mandatory)]
        [ValidateSet('Pass', 'Fail', 'Skip', 'Warning')]
        [string]$Status,

        [Parameter()]
        [string]$Expected,

        [Parameter()]
        [string]$Actual,

        [Parameter()]
        [string]$Environment,

        [Parameter()]
        [int]$Zone = 1,

        [Parameter()]
        [string]$Message,

        [Parameter()]
        [string]$EvidenceHash
    )

    [PSCustomObject]@{
        CriterionNumber = $CriterionNumber
        Setting         = $Setting
        CheckGroup      = $CheckGroup
        Status          = $Status
        Expected        = $Expected
        Actual          = $Actual
        Environment     = $Environment
        Zone            = $Zone
        Message         = $Message
        EvidenceHash    = $EvidenceHash
    }
}

function Get-EvidenceHash {
    <#
    .SYNOPSIS
        Computes SHA-256 hash of evidence JSON for integrity verification.
    #>
    [CmdletBinding()]
    param([Parameter(Mandatory)][string]$EvidenceJson)
    $hashBytes = [System.Security.Cryptography.SHA256]::Create().ComputeHash(
        [System.Text.Encoding]::UTF8.GetBytes($EvidenceJson)
    )
    return [BitConverter]::ToString($hashBytes) -replace '-'
}

# ─── Initialize Results ──────────────────────────────────────────────
$allChecks = [System.Collections.Generic.List[PSCustomObject]]::new()
$gaps = [System.Collections.Generic.List[string]]::new()
$startTime = [DateTime]::UtcNow

# ═══════════════════════════════════════════════════════════════════════
# Check Group 1: Tenant Settings — Criterion 3 (Share with Everyone)
# ═══════════════════════════════════════════════════════════════════════
Write-Verbose "Check Group 1: Tenant Settings — Criterion 3 (Share with Everyone)..."

try {
    $tenantSettings = Get-TenantSettings

    # Compute per-check evidence hash for Criterion 3
    $c3EvidenceHash = $null
    if ($IncludeEvidence) {
        $c3EvidenceJson = $tenantSettings | ConvertTo-Json -Depth 5 -Compress
        $c3EvidenceHash = Get-EvidenceHash -EvidenceJson $c3EvidenceJson
    }

    # Primary path: powerPlatform.powerApps.disableShareWithEveryone
    $shareWithEveryoneDisabled = $tenantSettings.powerPlatform.powerApps.disableShareWithEveryone

    # Fallback path: powerPlatform.copilotStudio.shareWithEveryoneDisabled
    if ($null -eq $shareWithEveryoneDisabled) {
        $shareWithEveryoneDisabled = $tenantSettings.powerPlatform.copilotStudio.shareWithEveryoneDisabled
        if ($null -ne $shareWithEveryoneDisabled) {
            Write-Verbose "  Using fallback path: powerPlatform.copilotStudio.shareWithEveryoneDisabled"
        }
    }

    # Determine which zones are represented in the zone mapping
    $zonesPresent = @(1)  # Default zone
    if ($ZoneMapping -and $ZoneMapping.Count -gt 0) {
        $zonesPresent = @($ZoneMapping.Values | Sort-Object -Unique)
    }

    foreach ($zoneNum in $zonesPresent) {
        if ($shareWithEveryoneDisabled -eq $true) {
            $c3Status = 'Pass'
            $c3Message = "Share with Everyone is disabled at tenant level"
        }
        elseif ($zoneNum -ge 2) {
            $c3Status = 'Fail'
            $c3Message = "Share with Everyone must be disabled for Zone $zoneNum environments"
        }
        else {
            $c3Status = 'Warning'
            $c3Message = "Share with Everyone is not disabled — recommended to disable for all zones"
        }

        $allChecks.Add((New-PublishingCheckResult -CriterionNumber 3 -Setting 'Share with Everyone disabled' `
            -CheckGroup 'TenantSettings' -Status $c3Status `
            -Expected 'disableShareWithEveryone = True' `
            -Actual "disableShareWithEveryone=$shareWithEveryoneDisabled" `
            -Environment 'Tenant' -Zone $zoneNum -Message $c3Message `
            -EvidenceHash $c3EvidenceHash))

        if ($c3Status -eq 'Fail') {
            $gaps.Add("Criterion 3: Share with Everyone not disabled — required for Zone $zoneNum governance")
        }
    }
}
catch {
    Write-Warning "Check Group 1 (Tenant Settings) failed: $($_.Exception.Message)"
    $allChecks.Add((New-PublishingCheckResult -CriterionNumber 3 -Setting 'Share with Everyone disabled' `
        -CheckGroup 'TenantSettings' -Status 'Skip' `
        -Environment 'Tenant' -Message "Error: $($_.Exception.Message)"))
}

# ═══════════════════════════════════════════════════════════════════════
# Check Group 2: Per-Environment Checks — Criteria 1, 2, 5
# ═══════════════════════════════════════════════════════════════════════
Write-Verbose "Check Group 2: Per-Environment Checks — Criteria 1, 2, 5..."

$environments = $null
$envCount = 0

try {
    $environments = Get-AdminPowerAppEnvironment
    if ($EnvironmentFilter) {
        $environments = $environments | Where-Object {
            $EnvironmentFilter -contains $_.EnvironmentName -or
            $EnvironmentFilter -contains $_.DisplayName
        }
    }

    $envCount = @($environments).Count
    Write-Verbose "Scanning $envCount environment(s)..."

    foreach ($env in $environments) {
        $envName = $env.DisplayName
        $envId = $env.EnvironmentName
        $zone = Get-EnvironmentZone -EnvironmentName $envId -Mapping $ZoneMapping

        Write-Verbose "  Environment: $envName (Zone $zone)..."

        # ─── Criterion 1: Environment Maker Role Removal ──────────────
        try {
            $roleAssignments = Get-AdminPowerAppEnvironmentRoleAssignment -EnvironmentName $envId -ErrorAction Stop

            # Compute per-check evidence hash for Criterion 1
            $c1EvidenceHash = $null
            if ($IncludeEvidence) {
                $c1EvidenceJson = $roleAssignments | ConvertTo-Json -Depth 5 -Compress
                $c1EvidenceHash = Get-EvidenceHash -EvidenceJson $c1EvidenceJson
            }

            # Check for "All Users" principal holding Environment Maker role
            # Well-known patterns: PrincipalDisplayName or PrincipalObjectId matching org-wide
            $broadMakerAssignments = $roleAssignments | Where-Object {
                ($_.PrincipalDisplayName -match 'All Users|Everyone|Organization' -or
                 $_.PrincipalObjectId -eq '00000000-0000-0000-0000-000000000000') -and
                $_.RoleDefinition.DisplayName -match 'Environment Maker'
            }

            if ($broadMakerAssignments) {
                $broadPrincipals = ($broadMakerAssignments | ForEach-Object { $_.PrincipalDisplayName }) -join ', '
                if ($zone -ge 2) {
                    $c1Status = 'Fail'
                    $c1Message = "Broad principal(s) hold Environment Maker role — remove for Zone $zone"
                }
                else {
                    $c1Status = 'Warning'
                    $c1Message = "Broad principal(s) hold Environment Maker role — recommended to remove"
                }
                $allChecks.Add((New-PublishingCheckResult -CriterionNumber 1 `
                    -Setting 'Environment Maker role removal' `
                    -CheckGroup 'EnvironmentRoles' -Status $c1Status `
                    -Expected 'No broad principal with Environment Maker role' `
                    -Actual "Broad principals: $broadPrincipals" `
                    -Environment $envName -Zone $zone -Message $c1Message `
                    -EvidenceHash $c1EvidenceHash))

                if ($c1Status -eq 'Fail') {
                    $gaps.Add("Criterion 1: Broad principal(s) '$broadPrincipals' hold Environment Maker role in '$envName' (Zone $zone)")
                }
            }
            else {
                $allChecks.Add((New-PublishingCheckResult -CriterionNumber 1 `
                    -Setting 'Environment Maker role removal' `
                    -CheckGroup 'EnvironmentRoles' -Status 'Pass' `
                    -Expected 'No broad principal with Environment Maker role' `
                    -Actual 'No broad principals detected' `
                    -Environment $envName -Zone $zone `
                    -Message 'Environment Maker role not assigned to broad principals' `
                    -EvidenceHash $c1EvidenceHash))
            }
        }
        catch {
            Write-Warning "  Criterion 1: Could not query role assignments for '$envName': $($_.Exception.Message)"
            $allChecks.Add((New-PublishingCheckResult -CriterionNumber 1 `
                -Setting 'Environment Maker role removal' `
                -CheckGroup 'EnvironmentRoles' -Status 'Skip' `
                -Environment $envName -Zone $zone `
                -Message "API error: $($_.Exception.Message)"))
        }

        # ─── Criterion 2: Authorized Security Groups ─────────────────
        try {
            $securityGroupId = $env.Internal.properties.securityGroupId
            $groupInfo = $null

            # Compute per-check evidence hash for Criterion 2
            $c2EvidenceHash = $null
            if ($IncludeEvidence) {
                $c2EvidenceJson = $env.Internal.properties | ConvertTo-Json -Depth 5 -Compress
                $c2EvidenceHash = Get-EvidenceHash -EvidenceJson $c2EvidenceJson
            }

            if ($securityGroupId) {
                # Attempt Graph API resolution for group name (best-effort)
                try {
                    $graphToken = Get-AzAccessToken -ResourceUrl 'https://graph.microsoft.com' -ErrorAction Stop
                    # Handle both Az.Accounts 2.x (.Token as string) and 3.x+ (.Token as SecureString)
                    $graphPlainToken = if ($graphToken.Token -is [securestring]) { $graphToken.Token | ConvertFrom-SecureString -AsPlainText } else { $graphToken.Token }
                    $group = Invoke-RestMethod -Uri "https://graph.microsoft.com/v1.0/groups/$securityGroupId" `
                        -Headers @{ Authorization = "Bearer $graphPlainToken" } -ErrorAction Stop
                    $groupInfo = $group.displayName
                }
                catch {
                    $groupInfo = "(unable to resolve — verify manually)"
                }

                $actualValue = "SecurityGroupId=$securityGroupId"
                if ($groupInfo) {
                    $actualValue += "; Name=$groupInfo"
                }

                # Check if group name matches recommended FSI-Agent-Makers-* pattern (informational)
                $patternMatch = if ($groupInfo -and $groupInfo -match 'FSI-Agent-Makers-') { ' (matches recommended naming)' } else { '' }

                $allChecks.Add((New-PublishingCheckResult -CriterionNumber 2 `
                    -Setting 'Authorized security group' `
                    -CheckGroup 'EnvironmentRoles' -Status 'Pass' `
                    -Expected 'Security group assigned to environment' `
                    -Actual $actualValue `
                    -Environment $envName -Zone $zone `
                    -Message "Security group configured$patternMatch" `
                    -EvidenceHash $c2EvidenceHash))
            }
            else {
                if ($zone -ge 2) {
                    $c2Status = 'Fail'
                    $c2Message = "No security group assigned — required for Zone $zone environments"
                }
                else {
                    $c2Status = 'Pass'
                    $c2Message = "No security group assigned (advisory for Zone 1)"
                }

                $allChecks.Add((New-PublishingCheckResult -CriterionNumber 2 `
                    -Setting 'Authorized security group' `
                    -CheckGroup 'EnvironmentRoles' -Status $c2Status `
                    -Expected 'Security group assigned to environment' `
                    -Actual 'No security group assigned' `
                    -Environment $envName -Zone $zone -Message $c2Message `
                    -EvidenceHash $c2EvidenceHash))

                if ($c2Status -eq 'Fail') {
                    $gaps.Add("Criterion 2: No security group assigned to environment '$envName' (Zone $zone)")
                }
            }
        }
        catch {
            Write-Warning "  Criterion 2: Could not check security group for '$envName': $($_.Exception.Message)"
            $allChecks.Add((New-PublishingCheckResult -CriterionNumber 2 `
                -Setting 'Authorized security group' `
                -CheckGroup 'EnvironmentRoles' -Status 'Skip' `
                -Environment $envName -Zone $zone `
                -Message "API error: $($_.Exception.Message)"))
        }

        # ─── Criterion 5: Managed Environment Sharing Limits ─────────
        try {
            $govConfig = $env.Internal.properties.governanceConfiguration

            # Compute per-check evidence hash for Criterion 5
            $c5EvidenceHash = $null
            if ($IncludeEvidence -and $null -ne $govConfig) {
                $c5EvidenceJson = $govConfig | ConvertTo-Json -Depth 5 -Compress
                $c5EvidenceHash = Get-EvidenceHash -EvidenceJson $c5EvidenceJson
            }

            if ($null -eq $govConfig) {
                if ($zone -ge 2) {
                    $c5Status = 'Fail'
                    $c5Message = "No governance configuration found — Managed Environment required for Zone $zone"
                }
                else {
                    $c5Status = 'Warning'
                    $c5Message = "No governance configuration found — Managed Environment recommended"
                }

                $allChecks.Add((New-PublishingCheckResult -CriterionNumber 5 `
                    -Setting 'Managed Environment sharing limits' `
                    -CheckGroup 'EnvironmentRoles' -Status $c5Status `
                    -Expected 'Managed Environment with sharing limits configured' `
                    -Actual 'governanceConfiguration not found' `
                    -Environment $envName -Zone $zone -Message $c5Message `
                    -EvidenceHash $c5EvidenceHash))

                if ($c5Status -eq 'Fail') {
                    $gaps.Add("Criterion 5: No governance configuration in '$envName' (Zone $zone) — Managed Environment required")
                }
            }
            else {
                $protectionLevel = $govConfig.protectionLevel
                $isManaged = $protectionLevel -eq 'Standard' -or $protectionLevel -eq 'Enhanced'

                # Read sharing limit from governance configuration
                $sharingLimit = $null
                if ($govConfig.settings -and $govConfig.settings.extendedSettings) {
                    $sharingLimit = $govConfig.settings.extendedSettings.maxLimitUserSharing
                    if ($null -eq $sharingLimit) {
                        $sharingLimit = $govConfig.settings.extendedSettings.limitSharingMode
                    }
                }
                # Also try direct property path
                if ($null -eq $sharingLimit -and $govConfig.settings) {
                    $sharingLimit = $govConfig.settings.maxLimitUserSharing
                }

                $sharingLimitInt = $null
                if ($null -ne $sharingLimit) {
                    $sharingLimitInt = [int]$sharingLimit
                }

                $c5Actual = "Managed=$isManaged; ProtectionLevel=$protectionLevel; SharingLimit=$($sharingLimitInt ?? 'NotConfigured')"

                switch ($zone) {
                    1 {
                        if (-not $isManaged) {
                            $c5Status = 'Warning'
                            $c5Message = "Environment is not Managed — recommended to enable for governance visibility"
                        }
                        else {
                            $c5Status = 'Pass'
                            $c5Message = "Managed Environment enabled (no sharing limit required for Zone 1)"
                        }
                    }
                    2 {
                        if (-not $isManaged) {
                            $c5Status = 'Fail'
                            $c5Message = "Not a Managed Environment — required for Zone 2"
                        }
                        elseif ($null -eq $sharingLimitInt) {
                            $c5Status = 'Fail'
                            $c5Message = "No sharing limit configured — Zone 2 requires limit <= 20"
                        }
                        elseif ($sharingLimitInt -gt 20) {
                            $c5Status = 'Fail'
                            $c5Message = "Sharing limit ($sharingLimitInt) exceeds Zone 2 threshold of 20"
                        }
                        else {
                            $c5Status = 'Pass'
                            $c5Message = "Managed Environment with sharing limit $sharingLimitInt (<= 20)"
                        }
                    }
                    3 {
                        if (-not $isManaged) {
                            $c5Status = 'Fail'
                            $c5Message = "Not a Managed Environment — required for Zone 3"
                        }
                        elseif ($null -eq $sharingLimitInt) {
                            $c5Status = 'Fail'
                            $c5Message = "No sharing limit configured — Zone 3 requires limit <= 5"
                        }
                        elseif ($sharingLimitInt -gt 5) {
                            $c5Status = 'Fail'
                            $c5Message = "Sharing limit ($sharingLimitInt) exceeds Zone 3 threshold of 5"
                        }
                        else {
                            $c5Status = 'Pass'
                            $c5Message = "Managed Environment with sharing limit $sharingLimitInt (<= 5)"
                        }
                    }
                    default {
                        $c5Status = 'Skip'
                        $c5Message = "Unknown zone $zone — cannot evaluate"
                    }
                }

                $allChecks.Add((New-PublishingCheckResult -CriterionNumber 5 `
                    -Setting 'Managed Environment sharing limits' `
                    -CheckGroup 'EnvironmentRoles' -Status $c5Status `
                    -Expected "Managed Environment with zone-appropriate sharing limit" `
                    -Actual $c5Actual `
                    -Environment $envName -Zone $zone -Message $c5Message `
                    -EvidenceHash $c5EvidenceHash))

                if ($c5Status -eq 'Fail') {
                    $gaps.Add("Criterion 5: $c5Message in '$envName' (Zone $zone)")
                }
            }
        }
        catch {
            Write-Warning "  Criterion 5: Could not check governance configuration for '$envName': $($_.Exception.Message)"
            $allChecks.Add((New-PublishingCheckResult -CriterionNumber 5 `
                -Setting 'Managed Environment sharing limits' `
                -CheckGroup 'EnvironmentRoles' -Status 'Skip' `
                -Environment $envName -Zone $zone `
                -Message "API error: $($_.Exception.Message)"))
        }
    }
}
catch {
    Write-Warning "Check Group 2 (Per-Environment) failed: $($_.Exception.Message)"
    @(1, 2, 5) | ForEach-Object {
        $settingName = switch ($_) {
            1 { 'Environment Maker role removal' }
            2 { 'Authorized security group' }
            5 { 'Managed Environment sharing limits' }
        }
        $allChecks.Add((New-PublishingCheckResult -CriterionNumber $_ -Setting $settingName `
            -CheckGroup 'EnvironmentRoles' -Status 'Skip' `
            -Message "Error enumerating environments: $($_.Exception.Message)"))
    }
}

# ═══════════════════════════════════════════════════════════════════════
# Check Group 3: DLP Policy Check — Criterion 4
# ═══════════════════════════════════════════════════════════════════════
Write-Verbose "Check Group 3: DLP Policy Check — Criterion 4..."

try {
    $dlpPolicies = Get-AdminDlpPolicy -ErrorAction Stop

    # Compute per-check evidence hash for Criterion 4
    $c4EvidenceHash = $null
    if ($IncludeEvidence) {
        $c4EvidenceJson = $dlpPolicies | ConvertTo-Json -Depth 5 -Compress
        $c4EvidenceHash = Get-EvidenceHash -EvidenceJson $c4EvidenceJson
    }

    # Known connector display names related to agent publishing
    $agentConnectorPatterns = @(
        'Microsoft Copilot Studio',
        'HTTP',
        'HTTP Webhook',
        'HTTP with Microsoft Entra ID'
    )

    if ($environments) {
        foreach ($env in $environments) {
            $envName = $env.DisplayName
            $envId = $env.EnvironmentName
            $zone = Get-EnvironmentZone -EnvironmentName $envId -Mapping $ZoneMapping

            if ($zone -eq 1) {
                # Zone 1: DLP not required for personal productivity
                $allChecks.Add((New-PublishingCheckResult -CriterionNumber 4 `
                    -Setting 'DLP connector blocking' `
                    -CheckGroup 'DLPPolicy' -Status 'Pass' `
                    -Expected 'DLP not required for Zone 1' `
                    -Actual 'Zone 1 — DLP check not applicable' `
                    -Environment $envName -Zone $zone `
                    -Message 'DLP connector blocking not required for Zone 1 (Personal Productivity)' `
                    -EvidenceHash $c4EvidenceHash))
                continue
            }

            # For Zone 2/3, check if any DLP policy blocks agent publishing connectors
            $coveringPolicies = @()

            foreach ($policy in $dlpPolicies) {
                # Check if policy applies to this environment
                $policyEnvironments = $policy.environments
                $appliesToEnv = $false

                if ($null -eq $policyEnvironments -or $policy.environmentType -eq 'AllEnvironments') {
                    $appliesToEnv = $true
                }
                elseif ($policyEnvironments) {
                    $appliesToEnv = $policyEnvironments | Where-Object {
                        $_.name -eq $envId -or $_.id -match $envId
                    }
                }

                if (-not $appliesToEnv) { continue }

                # Check blocked connector groups for agent-related connectors
                $blockedConnectors = @()
                if ($policy.connectorGroups) {
                    $blockedGroup = $policy.connectorGroups | Where-Object { $_.classification -eq 'Blocked' }
                    if ($blockedGroup -and $blockedGroup.connectors) {
                        $blockedConnectors = $blockedGroup.connectors | ForEach-Object {
                            $_.displayName ?? $_.id
                        }
                    }
                }

                $matchedConnectors = $blockedConnectors | Where-Object {
                    $connectorName = $_
                    $agentConnectorPatterns | Where-Object { $connectorName -match [regex]::Escape($_) }
                }

                if ($matchedConnectors) {
                    $coveringPolicies += [PSCustomObject]@{
                        PolicyName        = $policy.displayName
                        BlockedConnectors = ($matchedConnectors -join ', ')
                    }
                }
            }

            if ($coveringPolicies.Count -gt 0) {
                $policyNames = ($coveringPolicies | ForEach-Object { $_.PolicyName }) -join '; '
                $allChecks.Add((New-PublishingCheckResult -CriterionNumber 4 `
                    -Setting 'DLP connector blocking' `
                    -CheckGroup 'DLPPolicy' -Status 'Pass' `
                    -Expected 'DLP policy blocks agent publishing connectors' `
                    -Actual "Covering policies: $policyNames" `
                    -Environment $envName -Zone $zone `
                    -Message "Semi-automated: DLP policy found blocking agent connectors — verify connector list manually" `
                    -EvidenceHash $c4EvidenceHash))
            }
            else {
                $allChecks.Add((New-PublishingCheckResult -CriterionNumber 4 `
                    -Setting 'DLP connector blocking' `
                    -CheckGroup 'DLPPolicy' -Status 'Fail' `
                    -Expected 'DLP policy blocks agent publishing connectors' `
                    -Actual 'No covering DLP policy found' `
                    -Environment $envName -Zone $zone `
                    -Message "Semi-automated: No DLP policy found blocking agent connectors for this environment — verify manually" `
                    -EvidenceHash $c4EvidenceHash))

                $gaps.Add("Criterion 4: No DLP policy blocks agent publishing connectors in '$envName' (Zone $zone)")
            }
        }
    }
    else {
        $allChecks.Add((New-PublishingCheckResult -CriterionNumber 4 `
            -Setting 'DLP connector blocking' `
            -CheckGroup 'DLPPolicy' -Status 'Skip' `
            -Message 'No environments available for DLP policy evaluation'))
    }
}
catch {
    Write-Warning "Check Group 3 (DLP Policy) failed: $($_.Exception.Message)"
    $allChecks.Add((New-PublishingCheckResult -CriterionNumber 4 `
        -Setting 'DLP connector blocking' `
        -CheckGroup 'DLPPolicy' -Status 'Skip' `
        -Message "Error retrieving DLP policies: $($_.Exception.Message)"))
}

# ═══════════════════════════════════════════════════════════════════════
# Check Group 4: Approval Workflow Check — Criterion 6
# ═══════════════════════════════════════════════════════════════════════
Write-Verbose "Check Group 4: Approval Workflow Check — Criterion 6..."

if ($environments) {
    foreach ($env in $environments) {
        $envName = $env.DisplayName
        $envId = $env.EnvironmentName
        $zone = Get-EnvironmentZone -EnvironmentName $envId -Mapping $ZoneMapping

        if ($zone -eq 1) {
            $allChecks.Add((New-PublishingCheckResult -CriterionNumber 6 `
                -Setting 'Approval workflow active' `
                -CheckGroup 'ApprovalWorkflow' -Status 'Pass' `
                -Expected 'Approval workflow not required for Zone 1' `
                -Actual 'Zone 1 — auto-pass' `
                -Environment $envName -Zone $zone `
                -Message 'Approval workflow not required for Zone 1 (Personal Productivity)'))
            continue
        }

        # Zone 2/3: Check for approval indicators
        $approvalFound = $false
        $approvalDetails = @()
        $c6EvidenceData = @()

        # Check 1: Governance configuration for maker onboarding settings
        try {
            $govConfig = $env.Internal.properties.governanceConfiguration
            if ($govConfig) {
                $c6EvidenceData += $govConfig
                $makerOnboarding = $govConfig.settings.extendedSettings.makerOnboardingUrl
                $makerWelcome = $govConfig.settings.extendedSettings.makerOnboardingMarkdown

                if ($makerOnboarding -or $makerWelcome) {
                    $approvalFound = $true
                    $approvalDetails += "Maker onboarding configured"
                }
            }
        }
        catch {
            Write-Verbose "  Could not read governance config for '$envName': $($_.Exception.Message)"
        }

        # Check 2: Attempt to detect approval flows by naming pattern
        try {
            $flows = Get-AdminFlow -EnvironmentName $envId -ErrorAction Stop
            if ($flows) { $c6EvidenceData += $flows }
            $approvalFlows = $flows | Where-Object {
                $_.DisplayName -match 'agent.*publish.*approval|publishing.*approval|maker.*request|agent.*request.*approval'
            }

            if ($approvalFlows) {
                $approvalFound = $true
                $flowNames = ($approvalFlows | ForEach-Object { $_.DisplayName }) -join '; '
                $approvalDetails += "Approval flow(s): $flowNames"
            }
        }
        catch {
            Write-Verbose "  Could not enumerate flows for '$envName': $($_.Exception.Message)"
            $approvalDetails += "Flow enumeration unavailable — verify manually"
        }

        # Compute per-check evidence hash for Criterion 6
        $c6EvidenceHash = $null
        if ($IncludeEvidence -and $c6EvidenceData.Count -gt 0) {
            $c6EvidenceJson = $c6EvidenceData | ConvertTo-Json -Depth 5 -Compress
            $c6EvidenceHash = Get-EvidenceHash -EvidenceJson $c6EvidenceJson
        }

        if ($approvalFound) {
            $allChecks.Add((New-PublishingCheckResult -CriterionNumber 6 `
                -Setting 'Approval workflow active' `
                -CheckGroup 'ApprovalWorkflow' -Status 'Pass' `
                -Expected "Approval workflow configured for Zone $zone" `
                -Actual ($approvalDetails -join '; ') `
                -Environment $envName -Zone $zone `
                -Message "Semi-automated: Approval indicators found — verify workflow is operational" `
                -EvidenceHash $c6EvidenceHash))
        }
        else {
            $c6Message = "Semi-automated: No approval workflow indicators found — verify manually"
            if ($approvalDetails) {
                $c6Message += " ($($approvalDetails -join '; '))"
            }

            $allChecks.Add((New-PublishingCheckResult -CriterionNumber 6 `
                -Setting 'Approval workflow active' `
                -CheckGroup 'ApprovalWorkflow' -Status 'Fail' `
                -Expected "Approval workflow configured for Zone $zone" `
                -Actual 'No approval indicators detected' `
                -Environment $envName -Zone $zone `
                -Message $c6Message `
                -EvidenceHash $c6EvidenceHash))

            $gaps.Add("Criterion 6: No approval workflow found in '$envName' (Zone $zone)")
        }
    }
}
else {
    $allChecks.Add((New-PublishingCheckResult -CriterionNumber 6 `
        -Setting 'Approval workflow active' `
        -CheckGroup 'ApprovalWorkflow' -Status 'Skip' `
        -Message 'No environments available for approval workflow evaluation'))
}

# ═══════════════════════════════════════════════════════════════════════
# Results Aggregation
# ═══════════════════════════════════════════════════════════════════════

$passCount = ($allChecks | Where-Object { $_.Status -eq 'Pass' }).Count
$failCount = ($allChecks | Where-Object { $_.Status -eq 'Fail' }).Count
$skipCount = ($allChecks | Where-Object { $_.Status -eq 'Skip' }).Count
$warnCount = ($allChecks | Where-Object { $_.Status -eq 'Warning' }).Count
$totalChecks = $allChecks.Count
if (-not $envCount -and $environments) { $envCount = @($environments).Count }
$duration = ([DateTime]::UtcNow - $startTime).TotalSeconds

$results = [PSCustomObject]@{
    Metadata = [PSCustomObject]@{
        ScriptName          = 'restrict-agent-publishing'
        ScriptVersion       = '1.1.0'
        CheckedAt           = $startTime.ToString('o')
        DurationSeconds     = [math]::Round($duration, 2)
        EnvironmentsScanned = $envCount
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
Write-Host "`n── Publishing Restriction Summary ──────────────────────────" -ForegroundColor Cyan
Write-Host "  Criteria checked:  $totalChecks"
Write-Host "  Passed:            $passCount" -ForegroundColor $(if ($passCount -eq $totalChecks) { 'Green' } else { 'White' })
Write-Host "  Failed:            $failCount" -ForegroundColor $(if ($failCount -gt 0) { 'Yellow' } else { 'Green' })
Write-Host "  Skipped:           $skipCount" -ForegroundColor $(if ($skipCount -gt 0) { 'DarkYellow' } else { 'White' })
Write-Host "  Warnings:          $warnCount" -ForegroundColor $(if ($warnCount -gt 0) { 'DarkYellow' } else { 'White' })
Write-Host "  Environments:      $envCount"
Write-Host "  Duration:          $([math]::Round($duration, 2))s"
if ($IncludeEvidence -and $results.Metadata.IntegrityHash) {
    Write-Host "  Integrity Hash:    $($results.Metadata.IntegrityHash)" -ForegroundColor DarkGray
}
Write-Host "────────────────────────────────────────────────────────────`n" -ForegroundColor Cyan

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
        $allChecks | Format-Table -Property CriterionNumber, Setting, Environment, Zone, Status, Expected, Actual -AutoSize

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
