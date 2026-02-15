<#
.SYNOPSIS
    Audits Copilot Studio agent sharing configurations for compliance violations.

.DESCRIPTION
    Scans Power Platform environments for agent sharing violations using BAP APIs.
    Evaluates 5 violation rules:
    - ORG_WIDE_SHARING: Agent shared with entire organization
    - PUBLIC_INTERNET_LINK: Agent accessible via public/anonymous link
    - UNAPPROVED_GROUP: Agent shared with unapproved security group
    - EXCESSIVE_INDIVIDUAL: Agent shared with too many individual users
    - CROSS_TENANT_ACCESS: Agent shared with external tenant principals

    Uses BAP API (api.bap.microsoft.com) for agent enumeration and
    principal retrieval. Does not write to Dataverse — output is
    console/JSON/file only.

    Supports approved security group validation via -ApprovedGroupIds.

.PARAMETER OutputFormat
    Output format for results. Valid values: Table, JSON, Object. Default: Table.

.PARAMETER OutputPath
    Optional file path to export JSON results.

.PARAMETER EnvironmentFilter
    Optional array of environment names to limit scope.

.PARAMETER HomeTenantId
    Home tenant GUID for CROSS_TENANT_ACCESS detection. Required for Rule 5.

.PARAMETER MaxIndividualShares
    Maximum individual shares threshold for EXCESSIVE_INDIVIDUAL rule. Default: 5.

.PARAMETER ApprovedGroupIds
    Optional array of approved Entra security group GUIDs for UNAPPROVED_GROUP rule.

.PARAMETER IncludeEvidence
    When specified, computes SHA-256 integrity hash over results.

.EXAMPLE
    .\Invoke-SharingAudit.ps1
    Runs sharing audit across all environments with default settings.

.EXAMPLE
    .\Invoke-SharingAudit.ps1 -HomeTenantId "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" -OutputFormat JSON -OutputPath .\evidence\sharing-audit.json -IncludeEvidence
    Full audit with cross-tenant detection and evidence export.

.EXAMPLE
    .\Invoke-SharingAudit.ps1 -EnvironmentFilter 'prod-env-1','prod-env-2' -ApprovedGroupIds @('group-guid-1','group-guid-2')
    Scoped audit with approved group validation.

.OUTPUTS
    PSCustomObject with Metadata, Summary, Violations, and AgentSettings properties.

.NOTES
    Part of the FSI Agent Governance — Unrestricted Agent Sharing Detector.
    Controls: 1.1, 3.8
    Version: 1.0.0
    Requires: Microsoft.PowerApps.Administration.PowerShell (2.0.0+)
#>

#Requires -Version 7.0
#Requires -Modules Az.Accounts
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
    [string]$HomeTenantId,

    [Parameter()]
    [int]$MaxIndividualShares = 5,

    [Parameter()]
    [string[]]$ApprovedGroupIds = @(),

    [Parameter()]
    [switch]$IncludeEvidence
)

# ─── Banner ───────────────────────────────────────────────────────────
Write-Host "`n╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host   "║  FSI Agent Governance — Sharing Audit                   ║" -ForegroundColor Cyan
Write-Host   "╚══════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# ─── WhatIf Preview ──────────────────────────────────────────────────
if (-not $PSCmdlet.ShouldProcess("Power Platform tenant", "Run sharing audit")) {
    Write-Verbose "WhatIf: Would scan agent sharing principals across environments"
    return
}

# ─── Helper Functions ────────────────────────────────────────────────

function New-ViolationResult {
    <#
    .SYNOPSIS
        Creates a standardized violation result object.
    .DESCRIPTION
        Produces a PSCustomObject representing a single sharing violation
        with type, severity, agent context, and optional evidence hash.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [ValidateSet('ORG_WIDE_SHARING', 'PUBLIC_INTERNET_LINK', 'UNAPPROVED_GROUP',
                     'EXCESSIVE_INDIVIDUAL', 'CROSS_TENANT_ACCESS')]
        [string]$ViolationType,

        [Parameter(Mandatory)]
        [string]$AgentId,

        [Parameter(Mandatory)]
        [string]$AgentName,

        [Parameter(Mandatory)]
        [string]$EnvironmentId,

        [Parameter(Mandatory)]
        [string]$EnvironmentName,

        [Parameter(Mandatory)]
        [ValidateSet('Critical', 'High', 'Medium', 'Low')]
        [string]$Severity,

        [Parameter(Mandatory)]
        [string]$Description,

        [Parameter()]
        [string]$EvidenceJson,

        [Parameter()]
        [string]$PrincipalDetails
    )

    $evidenceHash = $null
    if ($EvidenceJson) {
        $sha256 = [System.Security.Cryptography.SHA256]::Create()
        try {
            $hashBytes = $sha256.ComputeHash(
                [System.Text.Encoding]::UTF8.GetBytes($EvidenceJson)
            )
            $evidenceHash = [BitConverter]::ToString($hashBytes) -replace '-'
        }
        finally {
            $sha256.Dispose()
        }
    }

    $violationName = "$ViolationType — $AgentName"
    if ($violationName.Length -gt 256) {
        $violationName = $violationName.Substring(0, 256)
    }

    [PSCustomObject]@{
        ViolationName    = $violationName
        ViolationType    = $ViolationType
        AgentId          = $AgentId
        AgentName        = $AgentName
        EnvironmentId    = $EnvironmentId
        EnvironmentName  = $EnvironmentName
        Severity         = $Severity
        ViolationStatus  = 'Open'
        Description      = $Description
        EvidenceJson     = $EvidenceJson
        EvidenceHash     = $evidenceHash
        PrincipalDetail  = $PrincipalDetails
        DetectedAt       = (Get-Date -Format 'o')
    }
}

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

function Get-SharingScope {
    <#
    .SYNOPSIS
        Classifies the highest sharing scope from a principal array.
    .DESCRIPTION
        Evaluates an array of permission principals and returns the highest
        sharing scope in priority order: Organization > Public > SecurityGroup > Individual.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [AllowEmptyCollection()]
        [array]$Principals
    )

    if ($Principals.Count -eq 0) {
        return 'None'
    }

    # Check in priority order (most permissive first)
    foreach ($principal in $Principals) {
        $pType = $principal.properties.principalType
        if ($pType -eq 'Organization' -or $pType -eq 'Tenant') {
            return 'Organization'
        }
    }

    foreach ($principal in $Principals) {
        $pType = $principal.properties.principalType
        $accessType = $principal.properties.accessType
        if ($pType -eq 'Public' -or $pType -eq 'Anonymous' -or $accessType -eq 'Public') {
            return 'Public'
        }
    }

    foreach ($principal in $Principals) {
        $pType = $principal.properties.principalType
        if ($pType -eq 'Group' -or $pType -eq 'SecurityGroup' -or $pType -eq 'AADSecurityGroup') {
            return 'SecurityGroup'
        }
    }

    return 'Individual'
}

function Get-PrincipalSummary {
    <#
    .SYNOPSIS
        Builds a human-readable summary string from a principal array.
    .DESCRIPTION
        Counts principals by type and returns a formatted summary
        suitable for violation descriptions and console output.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [AllowEmptyCollection()]
        [array]$Principals
    )

    if ($Principals.Count -eq 0) {
        return 'No principals'
    }

    $grouped = $Principals | Group-Object { $_.properties.principalType }
    $parts = $grouped | ForEach-Object { "$($_.Count) $($_.Name)" }
    return ($parts -join ', ')
}

# ─── Initialize Results ──────────────────────────────────────────────
$startTime = [DateTime]::UtcNow
$allViolations = [System.Collections.Generic.List[PSCustomObject]]::new()
$allAgentSettings = [System.Collections.Generic.List[PSCustomObject]]::new()

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
# Step 2: Enumerate Environments
# ═══════════════════════════════════════════════════════════════════════
Write-Verbose "Step 2: Enumerating Power Platform environments..."

$envApiUrl = 'https://api.bap.microsoft.com/providers/Microsoft.BusinessAppPlatform/scopes/admin/environments?api-version=2016-11-01'
$envResponse = Invoke-BapApi -Uri $envApiUrl -Token $token

if (-not $envResponse) {
    Write-Error "BAP API call to enumerate environments failed. Cannot produce a valid audit. Check authentication and permissions."
    return
}
if (-not $envResponse.value) {
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
# Step 3: Scan Agents Per Environment
# ═══════════════════════════════════════════════════════════════════════
Write-Verbose "Step 3: Scanning agent sharing configurations..."

$environmentIndex = 0
foreach ($env in $environments) {
    $environmentIndex++
    $envId = $env.name
    $envDisplayName = $env.properties.displayName
    Write-Verbose "[$environmentIndex/$envCount] Scanning environment: $envDisplayName ($envId)"

    # ─── Step 3a: List agents in this environment (with pagination) ──
    $agentsApiUrl = "https://api.bap.microsoft.com/providers/Microsoft.BusinessAppPlatform/environments/$envId/bots?api-version=2021-04-01"
    $agents = [System.Collections.Generic.List[PSCustomObject]]::new()
    $agentsPageUrl = $agentsApiUrl

    while ($agentsPageUrl) {
        $agentsResponse = Invoke-BapApi -Uri $agentsPageUrl -Token $token

        if (-not $agentsResponse) {
            Write-Verbose "  Failed to retrieve agents from '$envDisplayName'."
            break
        }

        if ($agentsResponse.value) {
            foreach ($a in $agentsResponse.value) {
                $agents.Add($a)
            }
        }

        $agentsPageUrl = $agentsResponse.'@odata.nextLink'
    }

    if ($agents.Count -eq 0) {
        Write-Verbose "  No agents found in environment '$envDisplayName'."
        continue
    }

    Write-Verbose "  Found $($agents.Count) agent(s) in '$envDisplayName'."

    # ─── Step 3b: Evaluate each agent ─────────────────────────────────
    foreach ($agent in $agents) {
        $agentId = $agent.name
        $agentName = $agent.properties.displayName
        if (-not $agentName) { $agentName = $agentId }

        Write-Verbose "    Evaluating agent: $agentName ($agentId)"

        # Get sharing principals for this agent
        $permissionsApiUrl = "https://api.bap.microsoft.com/providers/Microsoft.BusinessAppPlatform/environments/$envId/bots/$agentId/permissions?api-version=2021-04-01"
        $permissionsResponse = Invoke-BapApi -Uri $permissionsApiUrl -Token $token

        if (-not $permissionsResponse) {
            Write-Warning "    Could not retrieve permissions for agent '$agentName' in '$envDisplayName'."
            continue
        }

        $principals = @()
        if ($permissionsResponse.value) {
            $principals = @($permissionsResponse.value)
        }

        # Classify sharing scope
        $sharingScope = Get-SharingScope -Principals $principals
        $principalSummary = Get-PrincipalSummary -Principals $principals

        # Count principals by type
        $orgPrincipals = @($principals | Where-Object {
            $_.properties.principalType -eq 'Organization' -or
            $_.properties.principalType -eq 'Tenant'
        })
        $publicPrincipals = @($principals | Where-Object {
            $_.properties.principalType -eq 'Public' -or
            $_.properties.principalType -eq 'Anonymous' -or
            $_.properties.accessType -eq 'Public'
        })
        $groupPrincipals = @($principals | Where-Object {
            $_.properties.principalType -eq 'Group' -or
            $_.properties.principalType -eq 'SecurityGroup' -or
            $_.properties.principalType -eq 'AADSecurityGroup'
        })
        $individualPrincipals = @($principals | Where-Object {
            $_.properties.principalType -eq 'User'
        })

        # Record agent sharing setting
        $agentSetting = [PSCustomObject]@{
            AgentId          = $agentId
            AgentName        = $agentName
            EnvironmentId    = $envId
            EnvironmentName  = $envDisplayName
            SharingScope     = $sharingScope
            TotalPrincipals  = $principals.Count
            OrgPrincipals    = $orgPrincipals.Count
            PublicPrincipals = $publicPrincipals.Count
            GroupPrincipals  = $groupPrincipals.Count
            UserPrincipals   = $individualPrincipals.Count
            PrincipalSummary = $principalSummary
            ScannedAt        = (Get-Date -Format 'o')
        }
        $allAgentSettings.Add($agentSetting)

        # ═══ Rule Evaluation ══════════════════════════════════════════

        # ─── Rule 1: ORG_WIDE_SHARING ────────────────────────────────
        # Any principal with type "Organization" or "Tenant" → Critical
        if ($orgPrincipals.Count -gt 0) {
            $evidenceData = $orgPrincipals | ConvertTo-Json -Depth 5 -Compress
            $principalDetail = ($orgPrincipals | ForEach-Object {
                "$($_.properties.principalType): $($_.properties.principalId ?? $_.properties.displayName ?? 'N/A')"
            }) -join '; '

            $violation = New-ViolationResult `
                -ViolationType 'ORG_WIDE_SHARING' `
                -AgentId $agentId `
                -AgentName $agentName `
                -EnvironmentId $envId `
                -EnvironmentName $envDisplayName `
                -Severity 'Critical' `
                -Description "Agent '$agentName' is shared with the entire organization ($($orgPrincipals.Count) org-wide principal(s))" `
                -EvidenceJson $evidenceData `
                -PrincipalDetails $principalDetail

            $allViolations.Add($violation)
            Write-Verbose "      [CRITICAL] ORG_WIDE_SHARING detected for '$agentName'"
        }

        # ─── Rule 2: PUBLIC_INTERNET_LINK ─────────────────────────────
        # Any principal with public/anonymous scope → Critical
        if ($publicPrincipals.Count -gt 0) {
            $evidenceData = $publicPrincipals | ConvertTo-Json -Depth 5 -Compress
            $principalDetail = ($publicPrincipals | ForEach-Object {
                "$($_.properties.principalType): $($_.properties.accessType ?? $_.properties.principalId ?? 'N/A')"
            }) -join '; '

            $violation = New-ViolationResult `
                -ViolationType 'PUBLIC_INTERNET_LINK' `
                -AgentId $agentId `
                -AgentName $agentName `
                -EnvironmentId $envId `
                -EnvironmentName $envDisplayName `
                -Severity 'Critical' `
                -Description "Agent '$agentName' is accessible via public/anonymous link ($($publicPrincipals.Count) public principal(s))" `
                -EvidenceJson $evidenceData `
                -PrincipalDetails $principalDetail

            $allViolations.Add($violation)
            Write-Verbose "      [CRITICAL] PUBLIC_INTERNET_LINK detected for '$agentName'"
        }

        # ─── Rule 3: UNAPPROVED_GROUP ─────────────────────────────────
        # Group principals not in ApprovedGroupIds → High
        if ($groupPrincipals.Count -gt 0 -and $ApprovedGroupIds.Count -gt 0) {
            foreach ($group in $groupPrincipals) {
                $groupId = $group.properties.principalId
                $groupDisplayName = $group.properties.displayName

                if ($groupId -notin $ApprovedGroupIds) {
                    $evidenceData = $group | ConvertTo-Json -Depth 5 -Compress
                    $principalDetail = "GroupId=$groupId; DisplayName=$($groupDisplayName ?? 'Unknown')"

                    $violation = New-ViolationResult `
                        -ViolationType 'UNAPPROVED_GROUP' `
                        -AgentId $agentId `
                        -AgentName $agentName `
                        -EnvironmentId $envId `
                        -EnvironmentName $envDisplayName `
                        -Severity 'High' `
                        -Description "Agent '$agentName' shared with unapproved security group '$($groupDisplayName ?? $groupId)'" `
                        -EvidenceJson $evidenceData `
                        -PrincipalDetails $principalDetail

                    $allViolations.Add($violation)
                    Write-Verbose "      [HIGH] UNAPPROVED_GROUP detected for '$agentName': $groupId"
                }
            }
        }
        elseif ($groupPrincipals.Count -gt 0 -and $ApprovedGroupIds.Count -eq 0) {
            Write-Warning "Agent '$agentName' shared with $($groupPrincipals.Count) security group(s) but no -ApprovedGroupIds supplied — UNAPPROVED_GROUP rule skipped"
        }

        # ─── Rule 4: EXCESSIVE_INDIVIDUAL ─────────────────────────────
        # Individual user count exceeds MaxIndividualShares → Medium
        if ($individualPrincipals.Count -gt $MaxIndividualShares) {
            $evidenceData = @{
                UserCount            = $individualPrincipals.Count
                MaxIndividualShares  = $MaxIndividualShares
                ExcessCount          = $individualPrincipals.Count - $MaxIndividualShares
            } | ConvertTo-Json -Depth 5 -Compress
            $principalDetail = "UserCount=$($individualPrincipals.Count); Threshold=$MaxIndividualShares"

            $violation = New-ViolationResult `
                -ViolationType 'EXCESSIVE_INDIVIDUAL' `
                -AgentId $agentId `
                -AgentName $agentName `
                -EnvironmentId $envId `
                -EnvironmentName $envDisplayName `
                -Severity 'Medium' `
                -Description "Agent '$agentName' shared with $($individualPrincipals.Count) individual users (threshold: $MaxIndividualShares)" `
                -EvidenceJson $evidenceData `
                -PrincipalDetails $principalDetail

            $allViolations.Add($violation)
            Write-Verbose "      [MEDIUM] EXCESSIVE_INDIVIDUAL detected for '$agentName': $($individualPrincipals.Count) users"
        }

        # ─── Rule 5: CROSS_TENANT_ACCESS ──────────────────────────────
        # Principal tenantId differs from HomeTenantId → Critical (only if HomeTenantId provided)
        if ($HomeTenantId) {
            $crossTenantPrincipals = @($principals | Where-Object {
                $tenantId = $_.properties.tenantId
                $tenantId -and ($tenantId -ne $HomeTenantId)
            })

            foreach ($xtp in $crossTenantPrincipals) {
                $xtpTenantId = $xtp.properties.tenantId
                $xtpDisplayName = $xtp.properties.displayName
                $xtpPrincipalId = $xtp.properties.principalId

                $evidenceData = $xtp | ConvertTo-Json -Depth 5 -Compress
                $principalDetail = "PrincipalId=$($xtpPrincipalId ?? 'N/A'); TenantId=$xtpTenantId; DisplayName=$($xtpDisplayName ?? 'Unknown')"

                $violation = New-ViolationResult `
                    -ViolationType 'CROSS_TENANT_ACCESS' `
                    -AgentId $agentId `
                    -AgentName $agentName `
                    -EnvironmentId $envId `
                    -EnvironmentName $envDisplayName `
                    -Severity 'Critical' `
                    -Description "Agent '$agentName' shared with external tenant principal (TenantId: $xtpTenantId)" `
                    -EvidenceJson $evidenceData `
                    -PrincipalDetails $principalDetail

                $allViolations.Add($violation)
                Write-Verbose "      [CRITICAL] CROSS_TENANT_ACCESS detected for '$agentName': TenantId=$xtpTenantId"
            }
        }
    }
}

# ═══════════════════════════════════════════════════════════════════════
# Results Aggregation
# ═══════════════════════════════════════════════════════════════════════

$duration = ([DateTime]::UtcNow - $startTime).TotalSeconds
$criticalCount = @($allViolations | Where-Object { $_.Severity -eq 'Critical' }).Count
$highCount = @($allViolations | Where-Object { $_.Severity -eq 'High' }).Count
$mediumCount = @($allViolations | Where-Object { $_.Severity -eq 'Medium' }).Count
$lowCount = @($allViolations | Where-Object { $_.Severity -eq 'Low' }).Count

$results = [PSCustomObject]@{
    Metadata = [PSCustomObject]@{
        ScriptName          = 'Invoke-SharingAudit'
        ScriptVersion       = '1.0.0'
        CheckedAt           = $startTime.ToString('o')
        DurationSeconds     = [math]::Round($duration, 2)
        EnvironmentsScanned = $envCount
        AgentsScanned       = $allAgentSettings.Count
        HomeTenantId        = $HomeTenantId
        MaxIndividualShares = $MaxIndividualShares
        ApprovedGroupCount  = $ApprovedGroupIds.Count
        Rule3Skipped        = ($ApprovedGroupIds.Count -eq 0)
        IntegrityHash       = $null
    }
    Summary = [PSCustomObject]@{
        TotalViolations = $allViolations.Count
        Critical        = $criticalCount
        High            = $highCount
        Medium          = $mediumCount
        Low             = $lowCount
        OverallStatus   = if ($allViolations.Count -eq 0) { 'Clean' } else { 'ViolationsFound' }
    }
    Violations    = $allViolations.ToArray()
    AgentSettings = $allAgentSettings.ToArray()
}

# ─── SHA-256 Evidence Hash ────────────────────────────────────────────
if ($IncludeEvidence) {
    $resultsJson = $results | ConvertTo-Json -Depth 10 -Compress
    $sha256 = [System.Security.Cryptography.SHA256]::Create()
    try {
        $hashBytes = $sha256.ComputeHash(
            [System.Text.Encoding]::UTF8.GetBytes($resultsJson)
        )
        $results.Metadata.IntegrityHash = [BitConverter]::ToString($hashBytes) -replace '-'
    }
    finally {
        $sha256.Dispose()
    }
}

# ─── Console Summary Banner ──────────────────────────────────────────
$bannerColor = if ($allViolations.Count -gt 0) { 'Red' } else { 'Green' }

Write-Host "`n╔══════════════════════════════════════════════════════════╗" -ForegroundColor $bannerColor
Write-Host   "║  Sharing Audit Complete                                 ║" -ForegroundColor $bannerColor
Write-Host   "╠══════════════════════════════════════════════════════════╣" -ForegroundColor $bannerColor
$line1 = "  Environments: $envCount   Agents: $($allAgentSettings.Count)   Violations: $($allViolations.Count)"
Write-Host   "║$($line1.PadRight(58).Substring(0, 58))║" -ForegroundColor $bannerColor

if ($allViolations.Count -gt 0) {
    $line2 = "  Critical: $criticalCount   High: $highCount   Medium: $mediumCount"
    Write-Host "║$($line2.PadRight(58).Substring(0, 58))║" -ForegroundColor $bannerColor
}

Write-Host   "╚══════════════════════════════════════════════════════════╝`n" -ForegroundColor $bannerColor

if ($IncludeEvidence -and $results.Metadata.IntegrityHash) {
    Write-Host "  Integrity Hash: $($results.Metadata.IntegrityHash)" -ForegroundColor DarkGray
}

Write-Host "  Duration: $([math]::Round($duration, 2))s" -ForegroundColor DarkGray
Write-Host ""

# ─── Output ──────────────────────────────────────────────────────────
switch ($OutputFormat) {
    'JSON' {
        $json = $results | ConvertTo-Json -Depth 10
        if ($OutputPath) {
            $parentDir = Split-Path -Path $OutputPath -Parent
            if ($parentDir -and -not (Test-Path $parentDir)) {
                New-Item -ItemType Directory -Path $parentDir -Force | Out-Null
            }
            $json | Out-File -FilePath $OutputPath -Encoding utf8NoBOM
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
        if ($allViolations.Count -gt 0) {
            Write-Host "Violations:" -ForegroundColor Yellow
            $allViolations | Format-Table -Property ViolationType, AgentName, EnvironmentName, Severity, Description -AutoSize

            # Group summary by type
            Write-Host "Violations by Type:" -ForegroundColor Yellow
            $allViolations | Group-Object ViolationType | ForEach-Object {
                Write-Host "  $($_.Name): $($_.Count)" -ForegroundColor Yellow
            }
        }
        else {
            Write-Host "No sharing violations found." -ForegroundColor Green
        }

        # Show agent settings summary
        if ($allAgentSettings.Count -gt 0) {
            Write-Host "`nAgent Sharing Summary:" -ForegroundColor Cyan
            $allAgentSettings | Format-Table -Property AgentName, EnvironmentName, SharingScope, TotalPrincipals, UserPrincipals, GroupPrincipals -AutoSize
        }

        if ($OutputPath) {
            $parentDir = Split-Path -Path $OutputPath -Parent
            if ($parentDir -and -not (Test-Path $parentDir)) {
                New-Item -ItemType Directory -Path $parentDir -Force | Out-Null
            }
            $results | ConvertTo-Json -Depth 10 | Out-File -FilePath $OutputPath -Encoding utf8NoBOM
            Write-Host "Results exported to: $OutputPath" -ForegroundColor Cyan
            if ($IncludeEvidence -and $results.Metadata.IntegrityHash) {
                Write-Host "Integrity hash: $($results.Metadata.IntegrityHash)" -ForegroundColor DarkGray
            }
        }
    }
    'Object' {
        Write-Output $results
    }
}
