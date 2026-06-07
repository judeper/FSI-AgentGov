<#
.SYNOPSIS
    Validates M365 Admin Center agent access settings against zone-based governance policies.

.DESCRIPTION
    Checks 4 agent access governance areas against zone-specific policies defined in
    Control 3.8 (Copilot Hub and Governance Dashboard) for US financial services organizations.

    Check areas validated:
    - ZAV-01 (Agent Access Policy): M365 Admin Center agent access control settings compared
      to zone policy (Zone 1: all agents, Zone 2: Org + MS verified, Zone 3: Org only).
    - ZAV-02 (Admin Exclusion Group): Verifies the CopilotForM365AdminExclude Entra security
      group exists, is correctly typed, and has appropriate membership per zone requirements.
    - ZAV-03 (Deployment Groups): Validates staged deployment group configuration per zone
      requirements (optional Zone 1, recommended Zone 2, mandatory Zone 3).
    - ZAV-04 (Web Search Control): Verifies web search grounding setting aligns with zone
      policy (enabled Zone 1, disabled for MNPI in Zone 2, disabled org-wide Zone 3).

    Uses Microsoft Graph API for Entra group validation and M365 Admin Center Copilot
    settings retrieval. Zone-based logic applies different thresholds per governance zone
    (Zone 1 = Personal Productivity, Zone 2 = Team Collaboration, Zone 3 = Enterprise Managed).

    Does not write to Dataverse — output is console/JSON/file only.

.PARAMETER OutputFormat
    Output format for results. Valid values: Table, JSON, Object. Default: Table.

.PARAMETER OutputPath
    Optional file path to export JSON results. When omitted, results display to console only.

.PARAMETER ZoneMapping
    Optional hashtable mapping context identifiers to zone numbers (1, 2, or 3).
    Used for zone-specific validation thresholds. Keys can be deployment group names,
    environment labels, or organizational context identifiers.
    Example: @{ 'production' = 3; 'collaboration' = 2; 'personal' = 1 }

.PARAMETER IncludeEvidence
    When specified, computes SHA-256 integrity hash over results for evidence packaging.

.PARAMETER BaselinePath
    Optional path to a baseline JSON file for drift detection.
    When provided, compares current scan against previous baseline to detect drift.
    After scan, saves current results as the new baseline (unless -WhatIf).

.PARAMETER ExpectedExclusionGroupName
    Name of the Entra security group used for admin exclusion. Default: CopilotForM365AdminExclude.

.EXAMPLE
    .\Test-ZoneAgentAccess.ps1

    Runs all 4 zone access checks with default settings (Zone 1 assumed).

.EXAMPLE
    .\Test-ZoneAgentAccess.ps1 -OutputFormat JSON -OutputPath .\evidence\zone-access.json -IncludeEvidence

    Full audit with JSON export and SHA-256 integrity hash for regulatory evidence packaging.

.EXAMPLE
    .\Test-ZoneAgentAccess.ps1 -ZoneMapping @{ 'production' = 3; 'collaboration' = 2; 'personal' = 1 }

    Zone-specific audit with per-zone thresholds for agent access governance.

.EXAMPLE
    .\Test-ZoneAgentAccess.ps1 -BaselinePath .\baselines\zone-access-baseline.json -IncludeEvidence

    Drift detection scan comparing current settings against previous baseline.

.OUTPUTS
    PSCustomObject with Metadata, Summary, Checks, Drifts, and Gaps properties.

.NOTES
    Part of the FSI Agent Governance — Zone Agent Access Validation.
    Controls: 3.8, 1.1, 2.1
    Version: 1.0.0
    Requires: Az.Accounts module for token acquisition
#>

#Requires -Version 7.0

[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter()]
    [ValidateSet('Table', 'JSON', 'Object')]
    [string]$OutputFormat = 'Table',

    [Parameter()]
    [string]$OutputPath,

    [Parameter()]
    [hashtable]$ZoneMapping,

    [Parameter()]
    [switch]$IncludeEvidence,

    [Parameter()]
    [string]$BaselinePath,

    [Parameter()]
    [string]$ExpectedExclusionGroupName = 'CopilotForM365AdminExclude'
)

$ErrorActionPreference = 'Stop'

# ─── Banner ───────────────────────────────────────────────────────────
Write-Host "`n╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host   "║  FSI Agent Governance — Zone Agent Access Check         ║" -ForegroundColor Cyan
Write-Host   "╚══════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# ─── WhatIf Preview ──────────────────────────────────────────────────
if (-not $PSCmdlet.ShouldProcess("M365 tenant", "Run zone agent access checks (ZAV-01 through ZAV-04)")) {
    Write-Verbose "WhatIf: Would check M365 Admin Center agent access settings against zone-based governance policies"
    return
}

# ─── Helper Functions ────────────────────────────────────────────────

function Get-GraphApiToken {
    <#
    .SYNOPSIS
        Obtains an access token for Microsoft Graph API.
    .DESCRIPTION
        Uses Az.Accounts to acquire an OAuth token scoped to graph.microsoft.com.
        Requires an active Azure session (Connect-AzAccount).
    #>
    [CmdletBinding()]
    param()

    try {
        $tokenResult = Get-AzAccessToken -ResourceUrl "https://graph.microsoft.com" -ErrorAction Stop
        # Handle both Az.Accounts 2.x (.Token as string) and 3.x+ (.Token as SecureString)
        if ($tokenResult.Token -is [securestring]) {
            return $tokenResult.Token | ConvertFrom-SecureString -AsPlainText
        }
        return $tokenResult.Token
    }
    catch {
        throw "Failed to acquire Graph API token. Ensure you are signed in via Connect-AzAccount. Error: $($_.Exception.Message)"
    }
}

function Invoke-GraphApi {
    <#
    .SYNOPSIS
        Invokes a Microsoft Graph API endpoint with authorization and error handling.
    .DESCRIPTION
        Wrapper around Invoke-RestMethod that adds the Bearer token header
        and provides consistent error handling for Graph API calls.
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
        [hashtable]$AdditionalHeaders
    )

    try {
        $headers = @{
            Authorization  = "Bearer $Token"
            'Content-Type' = 'application/json'
        }
        if ($AdditionalHeaders) {
            foreach ($key in $AdditionalHeaders.Keys) {
                $headers[$key] = $AdditionalHeaders[$key]
            }
        }
        $response = Invoke-RestMethod -Uri $Uri -Method $Method -Headers $headers -ErrorAction Stop
        return $response
    }
    catch {
        $statusCode = $null
        if ($_.Exception.Response) {
            $statusCode = [int]$_.Exception.Response.StatusCode
        }
        Write-Warning "Graph API call failed ($Method $Uri) [HTTP $statusCode]: $($_.Exception.Message)"
        return $null
    }
}

function Get-ZoneForContext {
    <#
    .SYNOPSIS
        Returns the governance zone for a given context identifier.
    .DESCRIPTION
        Looks up the context key in the ZoneMapping hashtable.
        Returns zone 1 (Personal Productivity) as default if not mapped.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$ContextName,
        [Parameter()]
        [hashtable]$Mapping
    )
    if ($Mapping -and $Mapping.ContainsKey($ContextName)) {
        return $Mapping[$ContextName]
    }
    return 1  # Default to Zone 1 (least restrictive)
}

function New-AccessCheckResult {
    <#
    .SYNOPSIS
        Creates a standardized zone access check result object.
    .DESCRIPTION
        Produces a PSCustomObject representing a single zone agent access
        check result with zone context, check group, and evidence hash.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$CheckId,

        [Parameter(Mandatory)]
        [int]$CheckNumber,

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
        [string]$Context,

        [Parameter()]
        [int]$Zone = 1,

        [Parameter()]
        [string]$Message,

        [Parameter()]
        [string]$EvidenceJson
    )

    # Compute SHA-256 evidence hash when evidence data is provided
    $evidenceHash = $null
    if ($EvidenceJson) {
        $evidenceHash = Get-EvidenceHash -EvidenceJson $EvidenceJson
    }

    [PSCustomObject]@{
        CheckId      = $CheckId
        CheckNumber  = $CheckNumber
        Setting      = $Setting
        CheckGroup   = $CheckGroup
        Status       = $Status
        Expected     = $Expected
        Actual       = $Actual
        Context      = $Context
        Zone         = $Zone
        EvidenceHash = $evidenceHash
        Message      = $Message
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

# ─── Drift Detection Functions ────────────────────────────────────────

function Import-AccessBaseline {
    <#
    .SYNOPSIS
        Loads a previous scan baseline for drift detection.
    .DESCRIPTION
        Reads and validates a JSON baseline file from a previous scan.
        Returns $null if the file doesn't exist (first scan scenario).
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Path
    )

    if (-not (Test-Path -Path $Path)) {
        Write-Verbose "No baseline file found at '$Path' — first scan."
        return $null
    }

    try {
        $raw = Get-Content -Path $Path -Raw -ErrorAction Stop
        $baseline = $raw | ConvertFrom-Json -ErrorAction Stop

        # Validate expected schema
        if (-not $baseline.Checks -or -not $baseline.Metadata) {
            Write-Warning "Baseline file '$Path' does not match expected schema (missing Checks or Metadata). Skipping drift detection."
            return $null
        }

        Write-Verbose "Baseline loaded from '$Path' — $($baseline.Checks.Count) checks, scanned at $($baseline.Metadata.CheckedAt)"
        return $baseline
    }
    catch {
        Write-Warning "Failed to load baseline from '$Path': $($_.Exception.Message)"
        return $null
    }
}

function Compare-AccessBaseline {
    <#
    .SYNOPSIS
        Compares current scan results against a previous baseline to detect drift.
    .DESCRIPTION
        Identifies policy changes, status changes, group membership changes,
        and new checks by comparing current results against a loaded baseline.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [array]$CurrentChecks,

        [Parameter(Mandatory)]
        [PSCustomObject]$Baseline
    )

    $drifts = [System.Collections.Generic.List[PSCustomObject]]::new()
    $now = [DateTime]::UtcNow.ToString('o')

    # Build lookup by composite key: CheckId|Context|Zone
    $currentLookup = @{}
    foreach ($check in $CurrentChecks) {
        $key = "$($check.CheckId)|$($check.Context)|$($check.Zone)"
        $currentLookup[$key] = $check
    }

    $baselineLookup = @{}
    foreach ($check in $Baseline.Checks) {
        $key = "$($check.CheckId)|$($check.Context)|$($check.Zone)"
        $baselineLookup[$key] = $check
    }

    # Detect drifts in current scan vs baseline
    foreach ($key in $currentLookup.Keys) {
        $current = $currentLookup[$key]

        if (-not $baselineLookup.ContainsKey($key)) {
            # New check not in baseline
            $drifts.Add([PSCustomObject]@{
                CheckId        = $current.CheckId
                Context        = $current.Context
                Zone           = $current.Zone
                DriftType      = 'NewCheck'
                PreviousValue  = $null
                CurrentValue   = $current.Actual
                PreviousStatus = $null
                CurrentStatus  = $current.Status
                DetectedAt     = $now
            })
            continue
        }

        $previous = $baselineLookup[$key]

        # Check for status change
        if ($current.Status -ne $previous.Status) {
            $driftType = if ($current.CheckGroup -eq 'ExclusionGroup' -and $current.Actual -ne $previous.Actual) {
                'GroupMembershipChanged'
            }
            else {
                'StatusChanged'
            }
            $drifts.Add([PSCustomObject]@{
                CheckId        = $current.CheckId
                Context        = $current.Context
                Zone           = $current.Zone
                DriftType      = $driftType
                PreviousValue  = $previous.Actual
                CurrentValue   = $current.Actual
                PreviousStatus = $previous.Status
                CurrentStatus  = $current.Status
                DetectedAt     = $now
            })
        }
        # Check for value change (same status but different actual value)
        elseif ($current.Actual -ne $previous.Actual) {
            $driftType = if ($current.CheckGroup -eq 'AgentAccess' -or $current.CheckGroup -eq 'WebSearch') {
                'PolicyChanged'
            }
            elseif ($current.CheckGroup -eq 'ExclusionGroup') {
                'GroupMembershipChanged'
            }
            else {
                'PolicyChanged'
            }
            $drifts.Add([PSCustomObject]@{
                CheckId        = $current.CheckId
                Context        = $current.Context
                Zone           = $current.Zone
                DriftType      = $driftType
                PreviousValue  = $previous.Actual
                CurrentValue   = $current.Actual
                PreviousStatus = $previous.Status
                CurrentStatus  = $current.Status
                DetectedAt     = $now
            })
        }
    }

    # Detect removed checks (in baseline but not current)
    foreach ($key in $baselineLookup.Keys) {
        if (-not $currentLookup.ContainsKey($key)) {
            $previous = $baselineLookup[$key]
            $drifts.Add([PSCustomObject]@{
                CheckId        = $previous.CheckId
                Context        = $previous.Context
                Zone           = $previous.Zone
                DriftType      = 'NewCheck'
                PreviousValue  = $previous.Actual
                CurrentValue   = $null
                PreviousStatus = $previous.Status
                CurrentStatus  = $null
                DetectedAt     = $now
            })
        }
    }

    return $drifts.ToArray()
}

# ─── Initialize Results ──────────────────────────────────────────────
$allChecks = [System.Collections.Generic.List[PSCustomObject]]::new()
$gaps = [System.Collections.Generic.List[string]]::new()
$startTime = [DateTime]::UtcNow

# Determine which zones are represented in the zone mapping
$zonesPresent = @(1)  # Default zone
if ($ZoneMapping -and $ZoneMapping.Count -gt 0) {
    $zonesPresent = @($ZoneMapping.Values | Sort-Object -Unique)
}

# ─── Acquire Graph API Token ─────────────────────────────────────────
Write-Verbose "Acquiring Microsoft Graph API token..."
$graphToken = $null
try {
    $graphToken = Get-GraphApiToken
    Write-Verbose "Graph API token acquired successfully."
}
catch {
    Write-Warning "Could not acquire Graph API token: $($_.Exception.Message)"
    Write-Warning "Checks requiring Graph API will be skipped. Ensure you are signed in via Connect-AzAccount."
}

# ═══════════════════════════════════════════════════════════════════════
# Check 1: Agent Access Control Policy (ZAV-01)
# ═══════════════════════════════════════════════════════════════════════
Write-Verbose "Check 1: Agent Access Control Policy (ZAV-01)..."

if ($graphToken) {
    try {
        # NOTE (technical accuracy): This is NOT a documented Microsoft Graph endpoint. The
        # documented Copilot admin surface is /copilot/admin/settings/limitedMode and
        # /copilot/admin/policySettings/* (Graph beta) — neither exposes an agent-access policy.
        # As a result this request does not resolve and the check degrades to manual verification
        # (the catch/Skip branch). Do NOT repoint this URL to a real endpoint without tenant
        # validation: a 200 response lacking the assumed properties sets policyValue='Unknown'
        # and would flip the Zone 3 result to a false 'Fail'. Re-evaluate if/when Microsoft Graph
        # exposes these Copilot governance settings.
        $copilotSettings = Invoke-GraphApi -Uri "https://graph.microsoft.com/beta/admin/microsoft365/copilot/settings" -Token $graphToken

        # Compute evidence hash
        $c1EvidenceHash = $null
        $c1EvidenceJson = $null
        if ($copilotSettings -and $IncludeEvidence) {
            $c1EvidenceJson = $copilotSettings | ConvertTo-Json -Depth 5 -Compress
        }

        if ($copilotSettings) {
            # Extract agent access policy setting
            # Expected property paths (beta API — may vary):
            #   .agentAccess.allowedAgentTypes or .settings.agentAccess
            $agentAccessPolicy = $null

            # Try known property paths
            if ($copilotSettings.agentAccess) {
                $agentAccessPolicy = $copilotSettings.agentAccess
            }
            elseif ($copilotSettings.settings -and $copilotSettings.settings.agentAccess) {
                $agentAccessPolicy = $copilotSettings.settings.agentAccess
            }
            elseif ($copilotSettings.allowedAgentTypes) {
                $agentAccessPolicy = $copilotSettings.allowedAgentTypes
            }

            # Normalize to expected values
            $policyValue = if ($agentAccessPolicy) {
                switch -Wildcard ($agentAccessPolicy.ToString().ToLower()) {
                    '*all*'          { 'AllAgents' }
                    '*org*ms*'       { 'OrgAndMicrosoftVerified' }
                    '*org*verified*' { 'OrgAndMicrosoftVerified' }
                    '*org*only*'     { 'OrgOnly' }
                    '*org*'          { 'OrgOnly' }
                    default          { $agentAccessPolicy.ToString() }
                }
            }
            else {
                'Unknown'
            }

            foreach ($zoneNum in $zonesPresent) {
                $c1Expected = switch ($zoneNum) {
                    1 { 'AllAgents (any setting acceptable)' }
                    2 { 'OrgAndMicrosoftVerified or OrgOnly' }
                    3 { 'OrgOnly' }
                }

                $c1Status = switch ($zoneNum) {
                    1 { 'Pass' }  # Zone 1: any setting acceptable
                    2 {
                        if ($policyValue -eq 'AllAgents') { 'Warning' }
                        else { 'Pass' }
                    }
                    3 {
                        if ($policyValue -eq 'OrgOnly') { 'Pass' }
                        else { 'Fail' }
                    }
                }

                $c1Message = switch ($zoneNum) {
                    1 { "Agent access policy: $policyValue — acceptable for Zone 1" }
                    2 {
                        if ($policyValue -eq 'AllAgents') { "Agent access allows all agents — Zone 2 recommends Org + MS Verified" }
                        else { "Agent access policy: $policyValue — appropriate for Zone 2" }
                    }
                    3 {
                        if ($policyValue -eq 'OrgOnly') { "Agent access restricted to organizational only — Zone 3 compliant" }
                        else { "Agent access policy: $policyValue — Zone 3 requires OrgOnly" }
                    }
                }

                $allChecks.Add((New-AccessCheckResult -CheckId 'ZAV-01' -CheckNumber 1 `
                    -Setting 'Agent access control policy' `
                    -CheckGroup 'AgentAccess' -Status $c1Status `
                    -Expected $c1Expected `
                    -Actual "AgentAccessPolicy=$policyValue" `
                    -Context 'Tenant' -Zone $zoneNum -Message $c1Message `
                    -EvidenceJson $c1EvidenceJson))

                if ($c1Status -eq 'Fail') {
                    $gaps.Add("ZAV-01: Agent access policy is '$policyValue' — Zone $zoneNum requires 'OrgOnly'")
                }
            }
        }
        else {
            # API returned null — endpoint may not be available
            foreach ($zoneNum in $zonesPresent) {
                $allChecks.Add((New-AccessCheckResult -CheckId 'ZAV-01' -CheckNumber 1 `
                    -Setting 'Agent access control policy' `
                    -CheckGroup 'AgentAccess' -Status 'Skip' `
                    -Context 'Tenant' -Zone $zoneNum `
                    -Message "Semi-automated: Copilot settings API returned no data — verify agent access policy manually in M365 Admin Center > Copilot > Settings > Actions"))
            }
        }
    }
    catch {
        Write-Warning "Check 1 (Agent Access Policy) failed: $($_.Exception.Message)"
        foreach ($zoneNum in $zonesPresent) {
            $allChecks.Add((New-AccessCheckResult -CheckId 'ZAV-01' -CheckNumber 1 `
                -Setting 'Agent access control policy' `
                -CheckGroup 'AgentAccess' -Status 'Skip' `
                -Context 'Tenant' -Zone $zoneNum `
                -Message "Error: $($_.Exception.Message) — verify manually in M365 Admin Center"))
        }
    }
}
else {
    foreach ($zoneNum in $zonesPresent) {
        $allChecks.Add((New-AccessCheckResult -CheckId 'ZAV-01' -CheckNumber 1 `
            -Setting 'Agent access control policy' `
            -CheckGroup 'AgentAccess' -Status 'Skip' `
            -Context 'Tenant' -Zone $zoneNum `
            -Message "No Graph API token — sign in via Connect-AzAccount to enable this check"))
    }
}

# ═══════════════════════════════════════════════════════════════════════
# Check 2: Admin Exclusion Group (ZAV-02)
# ═══════════════════════════════════════════════════════════════════════
Write-Verbose "Check 2: Admin Exclusion Group (ZAV-02) — '$ExpectedExclusionGroupName'..."

$exclusionGroupId = $null

if ($graphToken) {
    try {
        # Search for the exclusion group by display name
        $groupFilter = [System.Uri]::EscapeDataString("displayName eq '$ExpectedExclusionGroupName'")
        $groupResponse = Invoke-GraphApi -Uri "https://graph.microsoft.com/v1.0/groups?`$filter=$groupFilter&`$select=id,displayName,securityEnabled,mailEnabled,groupTypes,description" -Token $graphToken

        $c2EvidenceJson = $null
        if ($groupResponse -and $IncludeEvidence) {
            $c2EvidenceJson = $groupResponse | ConvertTo-Json -Depth 5 -Compress
        }

        if ($groupResponse -and $groupResponse.value -and $groupResponse.value.Count -gt 0) {
            $group = $groupResponse.value[0]
            $exclusionGroupId = $group.id

            # Check 2a: Group type validation (must be Security group)
            $isSecurityGroup = ($group.securityEnabled -eq $true) -and ($group.mailEnabled -ne $true)

            if (-not $isSecurityGroup) {
                foreach ($zoneNum in $zonesPresent) {
                    $allChecks.Add((New-AccessCheckResult -CheckId 'ZAV-02' -CheckNumber 2 `
                        -Setting 'Admin exclusion group type' `
                        -CheckGroup 'ExclusionGroup' -Status 'Fail' `
                        -Expected "Security group (securityEnabled=True, mailEnabled=False)" `
                        -Actual "securityEnabled=$($group.securityEnabled); mailEnabled=$($group.mailEnabled)" `
                        -Context $ExpectedExclusionGroupName -Zone $zoneNum `
                        -Message "$ExpectedExclusionGroupName exists but is not a security group — recreate as Security type" `
                        -EvidenceJson $c2EvidenceJson))

                    $gaps.Add("ZAV-02: $ExpectedExclusionGroupName is not a security group (Zone $zoneNum)")
                }
            }
            else {
                foreach ($zoneNum in $zonesPresent) {
                    $allChecks.Add((New-AccessCheckResult -CheckId 'ZAV-02' -CheckNumber 2 `
                        -Setting 'Admin exclusion group type' `
                        -CheckGroup 'ExclusionGroup' -Status 'Pass' `
                        -Expected "Security group (securityEnabled=True, mailEnabled=False)" `
                        -Actual "securityEnabled=True; mailEnabled=False; id=$($group.id)" `
                        -Context $ExpectedExclusionGroupName -Zone $zoneNum `
                        -Message "$ExpectedExclusionGroupName exists as security group" `
                        -EvidenceJson $c2EvidenceJson))
                }
            }

            # Check 2b: Group membership count
            try {
                $memberCountResponse = Invoke-GraphApi `
                    -Uri "https://graph.microsoft.com/v1.0/groups/$exclusionGroupId/members/`$count" `
                    -Token $graphToken `
                    -AdditionalHeaders @{ 'ConsistencyLevel' = 'eventual' }

                $memberCount = if ($memberCountResponse -is [int]) { $memberCountResponse }
                               elseif ($memberCountResponse -is [long]) { [int]$memberCountResponse }
                               elseif ($memberCountResponse -is [string] -and $memberCountResponse -match '^\d+$') { [int]$memberCountResponse }
                               else { -1 }

                $c2bEvidenceJson = $null
                if ($IncludeEvidence) {
                    $c2bEvidenceJson = @{ GroupId = $exclusionGroupId; MemberCount = $memberCount } | ConvertTo-Json -Compress
                }

                foreach ($zoneNum in $zonesPresent) {
                    $c2bExpected = switch ($zoneNum) {
                        1 { 'Members optional (exclusion group not required for Zone 1)' }
                        2 { 'Members present (compliance-sensitive roles)' }
                        3 { 'Members present (traders, restricted persons, investigated employees)' }
                    }

                    if ($memberCount -le 0) {
                        $c2bStatus = switch ($zoneNum) {
                            1 { 'Pass' }
                            2 { 'Warning' }
                            3 { 'Fail' }
                        }
                        $c2bMessage = switch ($zoneNum) {
                            1 { "Exclusion group has no members — acceptable for Zone 1" }
                            2 { "Exclusion group is empty — Zone 2 should include compliance-sensitive roles" }
                            3 { "Exclusion group is empty — Zone 3 must include traders, restricted persons, investigated employees" }
                        }
                    }
                    else {
                        $c2bStatus = 'Pass'
                        $c2bMessage = "Exclusion group has $memberCount member(s)"
                    }

                    $allChecks.Add((New-AccessCheckResult -CheckId 'ZAV-02' -CheckNumber 2 `
                        -Setting 'Admin exclusion group membership' `
                        -CheckGroup 'ExclusionGroup' -Status $c2bStatus `
                        -Expected $c2bExpected `
                        -Actual "MemberCount=$memberCount" `
                        -Context $ExpectedExclusionGroupName -Zone $zoneNum `
                        -Message $c2bMessage `
                        -EvidenceJson $c2bEvidenceJson))

                    if ($c2bStatus -eq 'Fail') {
                        $gaps.Add("ZAV-02: $ExpectedExclusionGroupName has no members — Zone $zoneNum requires populated group")
                    }
                }
            }
            catch {
                Write-Warning "  Could not query member count for ${ExpectedExclusionGroupName}: $($_.Exception.Message)"
                foreach ($zoneNum in $zonesPresent) {
                    $allChecks.Add((New-AccessCheckResult -CheckId 'ZAV-02' -CheckNumber 2 `
                        -Setting 'Admin exclusion group membership' `
                        -CheckGroup 'ExclusionGroup' -Status 'Skip' `
                        -Context $ExpectedExclusionGroupName -Zone $zoneNum `
                        -Message "Could not query member count — verify manually in Entra ID"))
                }
            }
        }
        else {
            # Group does not exist
            foreach ($zoneNum in $zonesPresent) {
                $c2Status = switch ($zoneNum) {
                    1 { 'Pass' }     # Not required for Zone 1
                    2 { 'Fail' }
                    3 { 'Fail' }
                }
                $c2Message = switch ($zoneNum) {
                    1 { "$ExpectedExclusionGroupName does not exist — not required for Zone 1" }
                    2 { "$ExpectedExclusionGroupName does not exist — required for Zone 2 (compliance-sensitive role exclusion)" }
                    3 { "$ExpectedExclusionGroupName does not exist — required for Zone 3 (trader and restricted person exclusion)" }
                }

                $allChecks.Add((New-AccessCheckResult -CheckId 'ZAV-02' -CheckNumber 2 `
                    -Setting 'Admin exclusion group exists' `
                    -CheckGroup 'ExclusionGroup' -Status $c2Status `
                    -Expected "$ExpectedExclusionGroupName security group exists in Entra ID" `
                    -Actual 'Group not found' `
                    -Context $ExpectedExclusionGroupName -Zone $zoneNum `
                    -Message $c2Message `
                    -EvidenceJson $c2EvidenceJson))

                if ($c2Status -eq 'Fail') {
                    $gaps.Add("ZAV-02: $ExpectedExclusionGroupName does not exist — required for Zone $zoneNum")
                }
            }
        }
    }
    catch {
        Write-Warning "Check 2 (Admin Exclusion Group) failed: $($_.Exception.Message)"
        foreach ($zoneNum in $zonesPresent) {
            $allChecks.Add((New-AccessCheckResult -CheckId 'ZAV-02' -CheckNumber 2 `
                -Setting 'Admin exclusion group' `
                -CheckGroup 'ExclusionGroup' -Status 'Skip' `
                -Context $ExpectedExclusionGroupName -Zone $zoneNum `
                -Message "Error: $($_.Exception.Message)"))
        }
    }
}
else {
    foreach ($zoneNum in $zonesPresent) {
        $allChecks.Add((New-AccessCheckResult -CheckId 'ZAV-02' -CheckNumber 2 `
            -Setting 'Admin exclusion group' `
            -CheckGroup 'ExclusionGroup' -Status 'Skip' `
            -Context $ExpectedExclusionGroupName -Zone $zoneNum `
            -Message "No Graph API token — sign in via Connect-AzAccount to enable this check"))
    }
}

# ═══════════════════════════════════════════════════════════════════════
# Check 3: Deployment Group Configuration (ZAV-03)
# ═══════════════════════════════════════════════════════════════════════
Write-Verbose "Check 3: Deployment Group Configuration (ZAV-03)..."

if ($graphToken) {
    try {
        # NOTE (technical accuracy): Not a documented Microsoft Graph endpoint (see Check 1).
        # Copilot deployment-group configuration is not exposed via Graph; this request does not
        # resolve and the check degrades to the semi-automated/manual path below. Do not repoint
        # this URL without tenant validation.
        $deploymentConfig = Invoke-GraphApi -Uri "https://graph.microsoft.com/beta/admin/microsoft365/copilot/settings" -Token $graphToken

        $c3EvidenceJson = $null
        if ($deploymentConfig -and $IncludeEvidence) {
            $c3EvidenceJson = $deploymentConfig | ConvertTo-Json -Depth 5 -Compress
        }

        # Try to extract deployment group information
        $deploymentGroupsFound = $false
        $deploymentGroupDetails = @()

        if ($deploymentConfig) {
            # Check for deployment group related properties
            $deploymentProps = @(
                'deploymentGroups', 'deployment', 'rolloutSettings',
                'settings.deployment', 'settings.deploymentGroups'
            )

            foreach ($prop in $deploymentProps) {
                $parts = $prop -split '\.'
                $value = $deploymentConfig
                foreach ($part in $parts) {
                    if ($value -and $value.PSObject.Properties[$part]) {
                        $value = $value.$part
                    }
                    else {
                        $value = $null
                        break
                    }
                }
                if ($value) {
                    $deploymentGroupsFound = $true
                    $deploymentGroupDetails += "Found via $prop"
                    break
                }
            }
        }

        foreach ($zoneNum in $zonesPresent) {
            if ($deploymentGroupsFound) {
                $c3Status = 'Pass'
                $c3Message = "Deployment groups configured ($($deploymentGroupDetails -join '; '))"
                $c3Actual = "DeploymentGroups=Configured"
            }
            else {
                # API available but no deployment groups detected
                # This is semi-automated — deployment group configuration may not be
                # exposed via API in all tenants
                $c3Status = switch ($zoneNum) {
                    1 { 'Pass' }     # Optional for Zone 1
                    2 { 'Warning' }  # Recommended for Zone 2
                    3 { 'Fail' }     # Mandatory for Zone 3
                }
                $c3Message = switch ($zoneNum) {
                    1 { "Semi-automated: No deployment groups detected — optional for Zone 1" }
                    2 { "Semi-automated: No deployment groups detected — recommended for Zone 2 phased rollout. Verify in M365 Admin Center > Copilot > Settings > Deployment" }
                    3 { "Semi-automated: No deployment groups detected — mandatory for Zone 3 controlled rollout. Verify in M365 Admin Center > Copilot > Settings > Deployment" }
                }
                $c3Actual = "DeploymentGroups=NotDetected"
            }

            $c3Expected = switch ($zoneNum) {
                1 { 'Deployment groups optional (phased rollout recommended but not required)' }
                2 { 'Deployment groups recommended for phased rollout' }
                3 { 'Deployment groups mandatory with approval gate' }
            }

            $allChecks.Add((New-AccessCheckResult -CheckId 'ZAV-03' -CheckNumber 3 `
                -Setting 'Deployment group configuration' `
                -CheckGroup 'DeploymentGroup' -Status $c3Status `
                -Expected $c3Expected `
                -Actual $c3Actual `
                -Context 'Tenant' -Zone $zoneNum -Message $c3Message `
                -EvidenceJson $c3EvidenceJson))

            if ($c3Status -eq 'Fail') {
                $gaps.Add("ZAV-03: No deployment groups configured — Zone $zoneNum requires mandatory phased rollout with approval gate")
            }
        }
    }
    catch {
        Write-Warning "Check 3 (Deployment Groups) failed: $($_.Exception.Message)"
        foreach ($zoneNum in $zonesPresent) {
            $allChecks.Add((New-AccessCheckResult -CheckId 'ZAV-03' -CheckNumber 3 `
                -Setting 'Deployment group configuration' `
                -CheckGroup 'DeploymentGroup' -Status 'Skip' `
                -Context 'Tenant' -Zone $zoneNum `
                -Message "Semi-automated: $($_.Exception.Message) — verify deployment groups in M365 Admin Center > Copilot > Settings > Deployment"))
        }
    }
}
else {
    foreach ($zoneNum in $zonesPresent) {
        $allChecks.Add((New-AccessCheckResult -CheckId 'ZAV-03' -CheckNumber 3 `
            -Setting 'Deployment group configuration' `
            -CheckGroup 'DeploymentGroup' -Status 'Skip' `
            -Context 'Tenant' -Zone $zoneNum `
            -Message "No Graph API token — sign in via Connect-AzAccount to enable this check"))
    }
}

# ═══════════════════════════════════════════════════════════════════════
# Check 4: Web Search Control (ZAV-04)
# ═══════════════════════════════════════════════════════════════════════
Write-Verbose "Check 4: Web Search Control (ZAV-04)..."

if ($graphToken) {
    try {
        # Re-use copilot settings from Check 1 if available, otherwise re-fetch.
        # NOTE (technical accuracy): same undocumented endpoint as Check 1 — web-search governance
        # is not exposed via Microsoft Graph, so this degrades to manual verification.
        if (-not $copilotSettings) {
            $copilotSettings = Invoke-GraphApi -Uri "https://graph.microsoft.com/beta/admin/microsoft365/copilot/settings" -Token $graphToken
        }

        $c4EvidenceJson = $null
        if ($copilotSettings -and $IncludeEvidence) {
            $c4EvidenceJson = $copilotSettings | ConvertTo-Json -Depth 5 -Compress
        }

        if ($copilotSettings) {
            # Extract web search setting
            $webSearchEnabled = $null

            # Try known property paths
            if ($null -ne $copilotSettings.webSearch) {
                $webSearchEnabled = $copilotSettings.webSearch
            }
            elseif ($copilotSettings.settings -and $null -ne $copilotSettings.settings.webSearch) {
                $webSearchEnabled = $copilotSettings.settings.webSearch
            }
            elseif ($null -ne $copilotSettings.isWebSearchEnabled) {
                $webSearchEnabled = $copilotSettings.isWebSearchEnabled
            }
            elseif ($copilotSettings.settings -and $null -ne $copilotSettings.settings.isWebSearchEnabled) {
                $webSearchEnabled = $copilotSettings.settings.isWebSearchEnabled
            }

            if ($null -ne $webSearchEnabled) {
                foreach ($zoneNum in $zonesPresent) {
                    $c4Expected = switch ($zoneNum) {
                        1 { 'Web search enabled (acceptable for Zone 1)' }
                        2 { 'Web search disabled for MNPI teams' }
                        3 { 'Web search disabled organization-wide' }
                    }

                    $c4Status = switch ($zoneNum) {
                        1 { 'Pass' }  # Zone 1: any setting acceptable
                        2 {
                            if ($webSearchEnabled -eq $true) { 'Warning' }
                            else { 'Pass' }
                        }
                        3 {
                            if ($webSearchEnabled -eq $true) { 'Fail' }
                            else { 'Pass' }
                        }
                    }

                    $c4Message = switch ($zoneNum) {
                        1 { "Web search is $(if ($webSearchEnabled) { 'enabled' } else { 'disabled' }) — acceptable for Zone 1" }
                        2 {
                            if ($webSearchEnabled) { "Web search is enabled — Zone 2 recommends disabling for teams handling MNPI" }
                            else { "Web search is disabled — appropriate for Zone 2 teams handling MNPI" }
                        }
                        3 {
                            if ($webSearchEnabled) { "Web search is enabled — Zone 3 requires web search disabled organization-wide to prevent external data leakage" }
                            else { "Web search is disabled — Zone 3 compliant" }
                        }
                    }

                    $allChecks.Add((New-AccessCheckResult -CheckId 'ZAV-04' -CheckNumber 4 `
                        -Setting 'Web search control' `
                        -CheckGroup 'WebSearch' -Status $c4Status `
                        -Expected $c4Expected `
                        -Actual "WebSearchEnabled=$webSearchEnabled" `
                        -Context 'Tenant' -Zone $zoneNum -Message $c4Message `
                        -EvidenceJson $c4EvidenceJson))

                    if ($c4Status -eq 'Fail') {
                        $gaps.Add("ZAV-04: Web search is enabled — Zone $zoneNum requires it disabled organization-wide")
                    }
                }
            }
            else {
                # Web search setting not found in API response
                foreach ($zoneNum in $zonesPresent) {
                    $allChecks.Add((New-AccessCheckResult -CheckId 'ZAV-04' -CheckNumber 4 `
                        -Setting 'Web search control' `
                        -CheckGroup 'WebSearch' -Status 'Skip' `
                        -Context 'Tenant' -Zone $zoneNum `
                        -Message "Semi-automated: Web search setting not found in API response — verify in M365 Admin Center > Copilot > Settings > Data access"))
                }
            }
        }
        else {
            foreach ($zoneNum in $zonesPresent) {
                $allChecks.Add((New-AccessCheckResult -CheckId 'ZAV-04' -CheckNumber 4 `
                    -Setting 'Web search control' `
                    -CheckGroup 'WebSearch' -Status 'Skip' `
                    -Context 'Tenant' -Zone $zoneNum `
                    -Message "Semi-automated: Copilot settings API not available — verify web search in M365 Admin Center"))
            }
        }
    }
    catch {
        Write-Warning "Check 4 (Web Search Control) failed: $($_.Exception.Message)"
        foreach ($zoneNum in $zonesPresent) {
            $allChecks.Add((New-AccessCheckResult -CheckId 'ZAV-04' -CheckNumber 4 `
                -Setting 'Web search control' `
                -CheckGroup 'WebSearch' -Status 'Skip' `
                -Context 'Tenant' -Zone $zoneNum `
                -Message "Error: $($_.Exception.Message) — verify manually in M365 Admin Center"))
        }
    }
}
else {
    foreach ($zoneNum in $zonesPresent) {
        $allChecks.Add((New-AccessCheckResult -CheckId 'ZAV-04' -CheckNumber 4 `
            -Setting 'Web search control' `
            -CheckGroup 'WebSearch' -Status 'Skip' `
            -Context 'Tenant' -Zone $zoneNum `
            -Message "No Graph API token — sign in via Connect-AzAccount to enable this check"))
    }
}

# ═══════════════════════════════════════════════════════════════════════
# Drift Detection
# ═══════════════════════════════════════════════════════════════════════

$drifts = @()
$baseline = $null

if ($BaselinePath) {
    $baseline = Import-AccessBaseline -Path $BaselinePath
    if ($baseline) {
        $drifts = Compare-AccessBaseline -CurrentChecks $allChecks.ToArray() -Baseline $baseline
        Write-Verbose "Drift detection complete: $($drifts.Count) drift(s) detected."
    }
    else {
        Write-Verbose "No baseline for comparison — first scan, will save as baseline."
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
        ScriptName      = 'Test-ZoneAgentAccess'
        ScriptVersion   = '1.0.0'
        CheckedAt       = $startTime.ToString('o')
        DurationSeconds = [math]::Round($duration, 2)
        ZonesEvaluated  = $zonesPresent
        DriftCount      = $drifts.Count
        IntegrityHash   = $null
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
    Drifts = $drifts
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
Write-Host   "║  Zone Agent Access Check Complete                      ║" -ForegroundColor Cyan
Write-Host   "╠══════════════════════════════════════════════════════════╣" -ForegroundColor Cyan
Write-Host   "║  Checks: $($totalChecks.ToString().PadRight(7)) Passed: $($passCount.ToString().PadRight(7)) Failed: $($failCount.ToString().PadRight(7))║" -ForegroundColor Cyan
Write-Host   "║  Skipped: $($skipCount.ToString().PadRight(6)) Warnings: $($warnCount.ToString().PadRight(17))║" -ForegroundColor Cyan
Write-Host   "║  Zones: $(($zonesPresent -join ',').PadRight(9)) Duration: $("$([math]::Round($duration, 2))s".PadRight(21))║" -ForegroundColor Cyan
Write-Host   "╚══════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

if ($IncludeEvidence -and $results.Metadata.IntegrityHash) {
    Write-Host "  Integrity Hash: $($results.Metadata.IntegrityHash)" -ForegroundColor DarkGray
}

# ─── Drift Summary ─────────────────────────────────────────────────
if ($BaselinePath) {
    Write-Host "`n── Drift Detection ─────────────────────────────────────────" -ForegroundColor DarkCyan
    if (-not $baseline) {
        Write-Host "  No baseline — first scan, saving as baseline" -ForegroundColor DarkCyan
    }
    else {
        $baselineTime = $baseline.Metadata.CheckedAt
        Write-Host "  Baseline:        $BaselinePath" -ForegroundColor DarkCyan
        Write-Host "  Previous scan:   $baselineTime" -ForegroundColor DarkCyan
        if ($drifts.Count -eq 0) {
            Write-Host "  No drifts detected since previous scan" -ForegroundColor Green
        }
        else {
            $policyChangedCount = @($drifts | Where-Object { $_.DriftType -eq 'PolicyChanged' }).Count
            $statusChangedCount = @($drifts | Where-Object { $_.DriftType -eq 'StatusChanged' }).Count
            $groupChangedCount = @($drifts | Where-Object { $_.DriftType -eq 'GroupMembershipChanged' }).Count
            $newCheckCount = @($drifts | Where-Object { $_.DriftType -eq 'NewCheck' }).Count
            Write-Host "  Drifts detected: $($drifts.Count)" -ForegroundColor Yellow
            Write-Host "    Policy changed:       $policyChangedCount" -ForegroundColor DarkCyan
            Write-Host "    Status changed:       $statusChangedCount" -ForegroundColor DarkCyan
            Write-Host "    Group membership:     $groupChangedCount" -ForegroundColor DarkCyan
            Write-Host "    New checks:           $newCheckCount" -ForegroundColor DarkCyan
        }
    }
    Write-Host "────────────────────────────────────────────────────────────`n" -ForegroundColor DarkCyan
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
        $allChecks | Format-Table -Property CheckId, Setting, Context, Zone, Status, Expected, Actual -AutoSize

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

# ─── Baseline Auto-Save ────────────────────────────────────────────
if ($BaselinePath -and $PSCmdlet.ShouldProcess($BaselinePath, "Save scan results as new baseline")) {
    $baselineParentDir = Split-Path -Path $BaselinePath -Parent
    if ($baselineParentDir -and -not (Test-Path $baselineParentDir)) {
        New-Item -ItemType Directory -Path $baselineParentDir -Force | Out-Null
    }
    $results | ConvertTo-Json -Depth 10 | Out-File -FilePath $BaselinePath -Encoding utf8
    Write-Host "Baseline saved to $BaselinePath" -ForegroundColor Cyan
}
