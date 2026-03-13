<#
.SYNOPSIS
    Validates Conditional Access policy compliance against FSI governance requirements.

.DESCRIPTION
    Evaluates deployed CA policies against zone-specific requirements for Controls 1.11, 1.23,
    and 1.18. Checks policy existence, state, break-glass exclusions, MFA/grant controls,
    session controls, and optional policy drift analysis.

    Supports multiple output formats and optional baseline drift comparison.

.PARAMETER TenantId
    The Entra ID tenant GUID to evaluate.

.PARAMETER ConfigPath
    Path to the CA configuration JSON file containing tenant settings, group mappings,
    break-glass accounts, and application IDs.

.PARAMETER OutputFormat
    Output format for compliance results. Valid values: Table, JSON, Object.
    Default: Table.

.PARAMETER OutputPath
    Optional. File path to export results. When omitted, results display to console only.

.PARAMETER BaselinePath
    Optional. Path to a previously exported baseline JSON file. When provided, enables
    Check 6 policy drift analysis comparing current state against saved baseline.

.PARAMETER DataverseUrl
    Optional. Dataverse environment URL (e.g., https://org.crm.dynamics.com). When provided
    with -PersistResults, validation results and violations are written to Dataverse.

.PARAMETER DataverseToken
    Optional. OAuth2 bearer token for the Dataverse environment. Required when -DataverseUrl
    is specified.

.PARAMETER PersistResults
    Optional switch. When set together with -DataverseUrl, writes validation history and
    violation records to Dataverse for audit trail purposes.

.EXAMPLE
    .\Test-PolicyCompliance.ps1 -TenantId $tid -ConfigPath .\config.json

.EXAMPLE
    .\Test-PolicyCompliance.ps1 -TenantId $tid -ConfigPath .\config.json -OutputFormat JSON -OutputPath .\results.json

.EXAMPLE
    .\Test-PolicyCompliance.ps1 -TenantId $tid -ConfigPath .\config.json -BaselinePath .\baseline.json

.EXAMPLE
    .\Test-PolicyCompliance.ps1 -TenantId $tid -ConfigPath .\config.json -DataverseUrl 'https://org.crm.dynamics.com' -DataverseToken $token -PersistResults

.OUTPUTS
    PSCustomObject with compliance check results, gaps, and optional drift analysis.

.NOTES
    Part of the FSI Agent Governance — Conditional Access Automation solution.
    Controls: 1.11, 1.23, 1.18
    Requires: Microsoft.Graph.Identity.SignIns (2.0.0+)
#>

#Requires -Version 7.0
#Requires -Modules @{ ModuleName = 'Microsoft.Graph.Identity.SignIns'; ModuleVersion = '2.0.0' }

[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(Mandatory)]
    [string]$TenantId,

    [Parameter(Mandatory)]
    [string]$ConfigPath,

    [Parameter()]
    [ValidateSet('Table', 'JSON', 'Object')]
    [string]$OutputFormat = 'Table',

    [Parameter()]
    [string]$OutputPath,

    [Parameter()]
    [string]$BaselinePath,

    [Parameter()]
    [string]$DataverseUrl,

    [Parameter()]
    [string]$DataverseToken,

    [Parameter()]
    [switch]$PersistResults
)

# Import private helpers
. "$PSScriptRoot/private/Connect-GraphSession.ps1"
. "$PSScriptRoot/private/Get-ZoneClassification.ps1"
. "$PSScriptRoot/private/Test-ParameterValidation.ps1"

# ─── Banner ───────────────────────────────────────────────────────────
Write-Host "`n╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host   "║  FSI Agent Governance — CA Policy Compliance Checker    ║" -ForegroundColor Cyan
Write-Host   "╚══════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# ─── Parameter Validation ────────────────────────────────────────────
Test-CAAConfigPath -Path $ConfigPath
$config = Get-Content -Path $ConfigPath -Raw | ConvertFrom-Json

if ($BaselinePath -and -not (Test-Path $BaselinePath)) {
    Write-Warning "Baseline file not found: $BaselinePath — drift analysis will be skipped."
    $BaselinePath = $null
}

# ─── WhatIf Preview ──────────────────────────────────────────────────
if (-not $PSCmdlet.ShouldProcess("Tenant $TenantId", "Run compliance checks against CA policies")) {
    Write-Verbose "WhatIf: Would check CA policies for tenant $TenantId using config $ConfigPath"
    return
}

# ─── Graph Connection ────────────────────────────────────────────────
Connect-CAAGraphSession -TenantId $TenantId -Scopes @('Policy.Read.All')

# ─── Query CA Policies ───────────────────────────────────────────────
Write-Verbose "Querying CA policies for tenant $TenantId..."
$policies = Get-MgIdentityConditionalAccessPolicy -All
Write-Verbose "Found $($policies.Count) CA policies."

# ─── Initialize Results ──────────────────────────────────────────────
$complianceResults = [PSCustomObject]@{
    TenantId      = $TenantId
    CheckedAt     = [DateTime]::UtcNow
    TotalPolicies = $policies.Count
    Checks        = @()
    Gaps          = @()
    DriftAnalysis = $null
    Summary       = $null
}

# ─── Check 1: Policy Existence ───────────────────────────────────────
Write-Verbose "Check 1: Policy Existence..."
$expectedPolicies = @(
    'FSI-AllZones-BlockLegacyAuth'
    'FSI-Z1-AgentCreators-BaselineMFA'
    'FSI-Z2-AgentPublishers-PhishingResistant'
    'FSI-Z2-AgentBuilder-MFA'
    'FSI-Z3-EnterpriseAgentAdmin-Maximum'
    'FSI-Z3-AgentBuilder-StrictMFA'
    'FSI-Z3-RequireCompliantDevice'
    'FSI-Z3-BreakGlass-EmergencyAccess'
)

$existenceResults = @()
foreach ($expected in $expectedPolicies) {
    $found = $policies | Where-Object { $_.DisplayName -eq $expected }
    $existenceResults += [PSCustomObject]@{
        PolicyName = $expected
        Exists     = ($null -ne $found)
        State      = if ($found) { $found.State } else { 'Missing' }
    }
    if (-not $found) {
        $complianceResults.Gaps += "Missing expected policy: $expected"
    }
}
$complianceResults.Checks += [PSCustomObject]@{ Check = 'PolicyExistence'; Results = $existenceResults }

# ─── Check 2: Policy State ──────────────────────────────────────────
Write-Verbose "Check 2: Policy State..."
$stateResults = @()
foreach ($policy in $policies) {
    $stateResults += [PSCustomObject]@{
        PolicyName = $policy.DisplayName
        State      = $policy.State
        IsEnabled  = ($policy.State -eq 'enabled')
    }
    if ($policy.State -eq 'disabled') {
        $complianceResults.Gaps += "Policy disabled: $($policy.DisplayName)"
    }
}
$complianceResults.Checks += [PSCustomObject]@{ Check = 'PolicyState'; Results = $stateResults }

# ─── Check 3: Break-Glass Exclusions ────────────────────────────────
Write-Verbose "Check 3: Break-Glass Exclusions..."
$breakGlassAccounts = $config.breakGlassAccounts
$bgResults = @()
# Skip block-only policies — break-glass exclusion may be intentionally absent
$nonBlockPolicies = $policies | Where-Object {
    $_.GrantControls.BuiltInControls -notcontains 'block'
}
foreach ($policy in $nonBlockPolicies) {
    $excludedUsers = $policy.Conditions.Users.ExcludeUsers
    $allExcluded = $true
    foreach ($bg in $breakGlassAccounts) {
        if ($excludedUsers -notcontains $bg) {
            $allExcluded = $false
            $complianceResults.Gaps += "Policy '$($policy.DisplayName)' missing break-glass exclusion: $bg"
        }
    }
    $bgResults += [PSCustomObject]@{
        PolicyName          = $policy.DisplayName
        BreakGlassExcluded  = $allExcluded
    }
}
$complianceResults.Checks += [PSCustomObject]@{ Check = 'BreakGlassExclusions'; Results = $bgResults }

# ─── Check 4: MFA / Grant Controls ──────────────────────────────────
Write-Verbose "Check 4: MFA / Grant Controls..."
$grantResults = @()
foreach ($policy in $policies) {
    $controls = $policy.GrantControls
    $hasMfa = $controls.BuiltInControls -contains 'mfa'
    $isBlock = $controls.BuiltInControls -contains 'block'
    $grantResults += [PSCustomObject]@{
        PolicyName = $policy.DisplayName
        HasMFA     = $hasMfa
        IsBlock    = $isBlock
        Operator   = $controls.Operator
    }
    if (-not $hasMfa -and -not $isBlock -and $policy.State -eq 'enabled') {
        $complianceResults.Gaps += "Policy '$($policy.DisplayName)' has no MFA or block grant control"
    }
}
$complianceResults.Checks += [PSCustomObject]@{ Check = 'GrantControls'; Results = $grantResults }

# ─── Check 5: Session Controls ──────────────────────────────────────
Write-Verbose "Check 5: Session Controls..."
$sessionResults = @()
foreach ($policy in $policies) {
    $session = $policy.SessionControls
    $hasSignInFreq = ($null -ne $session.SignInFrequency -and $session.SignInFrequency.IsEnabled)
    $persistBrowser = $session.PersistentBrowser.Mode
    $isBlock = $policy.GrantControls.BuiltInControls -contains 'block'

    # Match both naming conventions: "Zone3"/"Zone2"/"Zone1" and "Z3"/"Z2"/"Z1"
    # Canonical policy names use short form (e.g., FSI-Z3-EnterpriseAgentAdmin-Maximum)
    $zone = $null
    if ($policy.DisplayName -match 'Zone\s*3|[\-_]Z3[\-_]') { $zone = 3 }
    elseif ($policy.DisplayName -match 'Zone\s*2|[\-_]Z2[\-_]') { $zone = 2 }
    elseif ($policy.DisplayName -match 'Zone\s*1|[\-_]Z1[\-_]') { $zone = 1 }

    $sessionResults += [PSCustomObject]@{
        PolicyName          = $policy.DisplayName
        SignInFreqEnabled   = $hasSignInFreq
        PersistentBrowser   = $persistBrowser
        Zone                = $zone
    }

    if (-not $isBlock) {
        if (-not $hasSignInFreq -and $policy.State -eq 'enabled') {
            Write-Verbose "Policy '$($policy.DisplayName)' has no sign-in frequency configured."
        }
        if ($zone -eq 3 -and $persistBrowser -ne 'never') {
            $complianceResults.Gaps += "Zone 3 policy '$($policy.DisplayName)' should have persistentBrowser mode 'never'"
        }
    }
}
$complianceResults.Checks += [PSCustomObject]@{ Check = 'SessionControls'; Results = $sessionResults }

# ─── Check 6: Policy Drift Analysis (optional) ──────────────────────
if ($BaselinePath) {
    Write-Verbose "Check 6: Policy Drift Analysis..."
    . "$PSScriptRoot/private/Get-PolicyBaseline.ps1"
    . "$PSScriptRoot/private/Compare-PolicyBaseline.ps1"

    $savedBaseline = Get-Content -Path $BaselinePath -Raw | ConvertFrom-Json
    $currentBaseline = Get-CAAPolicyBaseline -TenantId $TenantId -ConfigPath $ConfigPath
    $driftResults = Compare-CAAPolicyBaseline -Baseline $savedBaseline.Policies -Current $currentBaseline

    $complianceResults.DriftAnalysis = $driftResults

    foreach ($drift in $driftResults) {
        if ($drift.Severity -ge 3) {
            $complianceResults.Gaps += "Drift detected: $($drift.PolicyName) — $($drift.ViolationType) (Severity: $($drift.Severity))"
        }
    }
    $complianceResults.Checks += [PSCustomObject]@{ Check = 'PolicyDrift'; Results = $driftResults }
} else {
    Write-Verbose "No baseline path provided — skipping drift analysis. Run Export-PolicyBaseline.ps1 to create a baseline."
}

# ─── Compute gap/drift counts (used by Dataverse persistence and Summary) ──
$totalGaps = $complianceResults.Gaps.Count
$driftCount = if ($complianceResults.DriftAnalysis) { $complianceResults.DriftAnalysis.Count } else { 0 }

# ─── Dataverse Persistence (opt-in) ─────────────────────────────────────
if ($PersistResults -and -not $DataverseUrl) {
    Write-Warning "Cannot persist results: -DataverseUrl is required with -PersistResults"
}
elseif ($DataverseUrl -and -not $PersistResults) {
    Write-Verbose "Dataverse URL provided but -PersistResults not specified. Results not persisted."
}
elseif ($DataverseUrl -and $PersistResults) {
    Write-Verbose "Persisting results to Dataverse..."
    try {
        # Import CAAClient if not already loaded
        $caaModule = Get-Module -Name CAAClient -ErrorAction SilentlyContinue
        if (-not $caaModule) {
            Import-Module "$PSScriptRoot/private/CAAClient.psm1" -Force -ErrorAction Stop
        }

        # Connect to Dataverse
        Connect-CAADataverse -DataverseUrl $DataverseUrl -AccessToken $DataverseToken
        $conn = Get-CAAConnection
        if (-not $conn.IsConnected) {
            Write-Warning "Dataverse connection failed — results will not be persisted."
        }
        else {
            # Read operational parameters from Dataverse environment variables
            $gracePeriodHours     = Get-CAAEnvironmentVariable -Name 'GracePeriodHours'
            $baselineMaxAgeDays   = Get-CAAEnvironmentVariable -Name 'BaselineMaxAgeDays'
            $driftSeverityEsc     = Get-CAAEnvironmentVariable -Name 'DriftSeverityEscalation'
            $includeReportOnly    = Get-CAAEnvironmentVariable -Name 'IncludeReportOnlyPolicies'

            Write-Verbose "Operational params — GracePeriodHours: $gracePeriodHours, BaselineMaxAgeDays: $baselineMaxAgeDays, DriftSeverityEscalation: $driftSeverityEsc, IncludeReportOnlyPolicies: $includeReportOnly"

            # Generate correlation RunId
            $runId = (New-Guid).ToString()

            # Determine overall severity
            $overallSeverity = if ($totalGaps -eq 0 -and $driftCount -eq 0) { 1 }
                               elseif ($totalGaps -gt 0 -and $driftCount -eq 0) { 3 }
                               elseif ($driftCount -gt 0) { 4 }
                               else { 2 }

            # Persist validation history
            $resultsJson = $complianceResults | ConvertTo-Json -Depth 10
            # Count unique policies that generated gaps (a single policy can have multiple gaps)
            $failedPolicyNames = @($complianceResults.Gaps | ForEach-Object {
                if ($_ -match "Policy '([^']+)'") { $Matches[1] }
                elseif ($_ -match 'Missing expected policy:\s*(.+)$') { $Matches[1].Trim() }
            } | Select-Object -Unique)
            $passedPolicies = $policies.Count - $failedPolicyNames.Count
            $historyId = Write-CAAValidationHistory `
                -RunId $runId `
                -TotalPolicies $policies.Count `
                -PassedCount $passedPolicies `
                -WarningCount 0 `
                -FailedCount $totalGaps `
                -DriftCount $driftCount `
                -OverallSeverity $overallSeverity `
                -ResultsJson $resultsJson `
                -ValidatedBy ([System.Security.Principal.WindowsIdentity]::GetCurrent().Name) `
                -TenantId $TenantId

            # Persist individual violations
            $violationCount = 0
            foreach ($gap in $complianceResults.Gaps) {
                # Determine violation type and zone from gap description
                $violationType = 'ComplianceGap'
                $violationZone = 0
                $violationPolicyName = 'Unknown'
                $violationSeverity = 3

                if ($gap -match 'Missing expected policy: (.+)') {
                    $violationType = 'PolicyMissing'
                    $violationPolicyName = $Matches[1]
                    $violationSeverity = 4
                }
                elseif ($gap -match "Policy disabled: (.+)") {
                    $violationType = 'PolicyDisabled'
                    $violationPolicyName = $Matches[1]
                    $violationSeverity = 4
                }
                elseif ($gap -match "Policy '([^']+)' missing break-glass") {
                    $violationType = 'BreakGlassExclusionMissing'
                    $violationPolicyName = $Matches[1]
                    $violationSeverity = 4
                }
                elseif ($gap -match "Policy '([^']+)' has no MFA") {
                    $violationType = 'GrantControlMissing'
                    $violationPolicyName = $Matches[1]
                    $violationSeverity = 4
                }
                elseif ($gap -match "Zone 3 policy '([^']+)'") {
                    $violationType = 'SessionControlWeakened'
                    $violationPolicyName = $Matches[1]
                    $violationZone = 3
                    $violationSeverity = 3
                }
                elseif ($gap -match 'Drift detected: ([^ ]+)') {
                    $violationType = 'PolicyDrift'
                    $violationPolicyName = $Matches[1]
                    $violationSeverity = 4
                }

                # Determine zone from policy name if not already set
                if ($violationZone -eq 0) {
                    if ($violationPolicyName -match 'Zone3') { $violationZone = 3 }
                    elseif ($violationPolicyName -match 'Zone2') { $violationZone = 2 }
                    elseif ($violationPolicyName -match 'Zone1') { $violationZone = 1 }
                }

                $null = Write-CAAViolation `
                    -RunId $runId `
                    -PolicyId '' `
                    -PolicyDisplayName $violationPolicyName `
                    -ViolationType $violationType `
                    -Zone $violationZone `
                    -Severity $violationSeverity `
                    -Description $gap `
                    -TenantId $TenantId
                $violationCount++
            }

            Write-Verbose "Persisted $($complianceResults.Checks.Count) results and $violationCount violations to Dataverse (RunId: $runId)"
        }
    }
    catch {
        Write-Warning "Dataverse persistence failed — $($_.Exception.Message). Compliance results are still available."
    }
}

# ─── Summary ─────────────────────────────────────────────────────────
$complianceResults.Summary = [PSCustomObject]@{
    TotalPolicies = $policies.Count
    TotalChecks   = $complianceResults.Checks.Count
    TotalGaps     = $totalGaps
    DriftCount    = $driftCount
    OverallStatus = if ($totalGaps -eq 0) { 'Passed' } else { 'GapsFound' }
}

Write-Host "`n── Compliance Summary ──────────────────────────────────────" -ForegroundColor Cyan
Write-Host "  Policies checked: $($policies.Count)"
Write-Host "  Checks run:       $($complianceResults.Checks.Count)"
Write-Host "  Gaps found:       $totalGaps" -ForegroundColor $(if ($totalGaps -gt 0) { 'Yellow' } else { 'Green' })
Write-Host "  Drift detected:   $driftCount" -ForegroundColor $(if ($driftCount -gt 0) { 'Yellow' } else { 'Green' })
Write-Host "────────────────────────────────────────────────────────────`n" -ForegroundColor Cyan

# ─── Output ──────────────────────────────────────────────────────────
switch ($OutputFormat) {
    'JSON' {
        $json = $complianceResults | ConvertTo-Json -Depth 10
        if ($OutputPath) {
            $json | Out-File -FilePath $OutputPath -Encoding utf8
            Write-Verbose "Results exported to $OutputPath"
        } else {
            Write-Output $json
        }
    }
    'Table' {
        if ($complianceResults.Gaps.Count -gt 0) {
            Write-Host "Gaps:" -ForegroundColor Yellow
            $complianceResults.Gaps | ForEach-Object { Write-Host "  - $_" -ForegroundColor Yellow }
        }
        if ($OutputPath) {
            $complianceResults | ConvertTo-Json -Depth 10 | Out-File -FilePath $OutputPath -Encoding utf8
            Write-Verbose "Results exported to $OutputPath"
        }
    }
    'Object' {
        Write-Output $complianceResults
    }
}
