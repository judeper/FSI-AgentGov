<#
.SYNOPSIS
    Azure Automation runbook for daily CA policy compliance validation.

.DESCRIPTION
    Wraps Test-PolicyCompliance logic for unattended execution in Azure Automation with
    certificate-based authentication, Dataverse baseline integration, multi-dimensional
    drift detection, and structured JSON output compatible with the Power Automate flow's
    Parse_Results action.

    Designed for Azure Automation scheduled execution — no interactive prompts.
    All errors produce valid JSON output with AlertRequired=true for downstream processing.

    Compliance checks performed:
      1. Policy existence against expected templates
      2. Policy state (enabled vs report-only vs disabled)
      3. Break-glass exclusion verification
      4. MFA/grant control verification
      5. Zone coverage completeness (session controls)
      6. Drift analysis against Dataverse baselines (5 dimensions)

    Part of the FSI Agent Governance — Conditional Access Automation solution.
    Controls: 1.11, 1.23, 1.18

.PARAMETER TenantId
    (Mandatory) Entra ID tenant GUID.

.PARAMETER ClientId
    (Mandatory) App registration client ID for certificate-based authentication.

.PARAMETER CertificateThumbprint
    (Mandatory) Certificate thumbprint for unattended authentication.
    Certificate must be installed in the Automation Account certificate store.

.PARAMETER ConfigPath
    (Mandatory) Path to the CA configuration JSON file containing tenant settings,
    group mappings, break-glass accounts, and application IDs.

.PARAMETER DataverseUrl
    (Mandatory) Dataverse environment URL (e.g., https://org.crm.dynamics.com).

.PARAMETER Zone
    (Optional) Filter compliance checks to a single zone (1, 2, or 3).
    When omitted, all zones are evaluated.

.PARAMETER Scope
    (Optional) 'Full' (default) for scheduled daily scans or 'Targeted' for
    provisioning-triggered scans with reduced scope tagging.

.EXAMPLE
    .\Start-CAAValidationRunbook.ps1 -TenantId $tid -ClientId $cid `
        -CertificateThumbprint $thumb -ConfigPath .\config.json `
        -DataverseUrl 'https://org.crm.dynamics.com'

.EXAMPLE
    .\Start-CAAValidationRunbook.ps1 -TenantId $tid -ClientId $cid `
        -CertificateThumbprint $thumb -ConfigPath .\config.json `
        -DataverseUrl 'https://org.crm.dynamics.com' -Zone 3 -Scope Targeted

.OUTPUTS
    JSON string matching the Power Automate flow Parse_Results schema.

.NOTES
    Requires: Microsoft.Graph.Identity.SignIns (2.0.0+)
    Auth: Certificate-based (no interactive prompts)
    Output: Single JSON object to pipeline (captured by Get-AzAutomationJobOutput)
#>

#Requires -Version 7.0
#Requires -Modules @{ ModuleName = 'Microsoft.Graph.Identity.SignIns'; ModuleVersion = '2.0.0' }

[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$TenantId,

    [Parameter(Mandatory)]
    [string]$ClientId,

    [Parameter(Mandatory)]
    [string]$CertificateThumbprint,

    [Parameter(Mandatory)]
    [string]$ConfigPath,

    [Parameter(Mandatory)]
    [string]$DataverseUrl,

    [Parameter()]
    [ValidateRange(1, 3)]
    [int]$Zone,

    [Parameter()]
    [ValidateSet('Full', 'Targeted')]
    [string]$Scope = 'Full'
)

# ─── Severity Constants ──────────────────────────────────────────────
$severityLabels = @{
    1 = 'Passed'
    2 = 'Info'
    3 = 'Warning'
    4 = 'Error'
    5 = 'Critical'
}

# ─── Helper: Acquire Dataverse Token via Certificate Assertion ───────
function script:New-DataverseAccessToken {
    <#
    .SYNOPSIS
        Acquires an OAuth2 access token for Dataverse using certificate-based
        client credentials (JWT assertion). No external module dependencies.
    #>
    param(
        [Parameter(Mandatory)][string]$TokenTenantId,
        [Parameter(Mandatory)][string]$TokenClientId,
        [Parameter(Mandatory)][string]$TokenCertThumbprint,
        [Parameter(Mandatory)][string]$TokenResourceUrl
    )

    $cert = Get-Item "Cert:\CurrentUser\My\$TokenCertThumbprint" -ErrorAction Stop

    # Base64url encoding helper
    $toBase64Url = { param($bytes) [Convert]::ToBase64String($bytes) -replace '\+','-' -replace '/','_' -replace '=' }

    # x5t: base64url-encoded SHA-1 certificate thumbprint
    $x5t = & $toBase64Url $cert.GetCertHash()

    # JWT header
    $headerBytes = [Text.Encoding]::UTF8.GetBytes(
        (@{ alg = 'RS256'; typ = 'JWT'; x5t = $x5t } | ConvertTo-Json -Compress)
    )
    $headerB64 = & $toBase64Url $headerBytes

    # JWT payload
    $now = [DateTimeOffset]::UtcNow
    $payloadObj = @{
        aud = "https://login.microsoftonline.com/$TokenTenantId/oauth2/v2.0/token"
        iss = $TokenClientId
        sub = $TokenClientId
        jti = [Guid]::NewGuid().ToString()
        nbf = $now.ToUnixTimeSeconds()
        exp = $now.AddMinutes(10).ToUnixTimeSeconds()
    }
    $payloadBytes = [Text.Encoding]::UTF8.GetBytes(($payloadObj | ConvertTo-Json -Compress))
    $payloadB64 = & $toBase64Url $payloadBytes

    # RSA-SHA256 signature
    $signingInput = "$headerB64.$payloadB64"
    $rsa = [System.Security.Cryptography.X509Certificates.RSACertificateExtensions]::GetRSAPrivateKey($cert)
    $signatureBytes = $rsa.SignData(
        [Text.Encoding]::UTF8.GetBytes($signingInput),
        [Security.Cryptography.HashAlgorithmName]::SHA256,
        [Security.Cryptography.RSASignaturePadding]::Pkcs1
    )
    $signatureB64 = & $toBase64Url $signatureBytes

    $clientAssertion = "$signingInput.$signatureB64"

    # Token request
    $resource = $TokenResourceUrl.TrimEnd('/')
    $tokenResponse = Invoke-RestMethod `
        -Uri "https://login.microsoftonline.com/$TokenTenantId/oauth2/v2.0/token" `
        -Method Post `
        -ContentType 'application/x-www-form-urlencoded' `
        -Body @{
            client_id             = $TokenClientId
            scope                 = "$resource/.default"
            client_assertion_type = 'urn:ietf:params:oauth:client-assertion-type:jwt-bearer'
            client_assertion      = $clientAssertion
            grant_type            = 'client_credentials'
        }

    return $tokenResponse.access_token
}

# ─── Helper: Determine zone from policy display name ─────────────────
function script:Get-PolicyZone {
    param([string]$DisplayName)
    if ($DisplayName -match 'Zone3') { return 3 }
    elseif ($DisplayName -match 'Zone2') { return 2 }
    elseif ($DisplayName -match 'Zone1') { return 1 }
    elseif ($DisplayName -match 'AllZones') { return 3 }
    else { return 0 }
}

# ─── Helper: Apply zone severity escalation ──────────────────────────
function script:Get-EscalatedSeverity {
    param(
        [int]$BaseSeverity,
        [int]$PolicyZone,
        [bool]$EscalationEnabled
    )
    if ($EscalationEnabled -and $PolicyZone -eq 3) {
        return [Math]::Min($BaseSeverity + 1, 5)
    }
    return $BaseSeverity
}

# ═══════════════════════════════════════════════════════════════════════
# Main Execution — wrapped in try/catch for guaranteed JSON output
# ═══════════════════════════════════════════════════════════════════════
try {
    $checkedAt = [DateTime]::UtcNow
    $runId = (New-Guid).ToString()

    # ─── Import Modules and Helpers ──────────────────────────────────
    Import-Module "$PSScriptRoot/private/CAAClient.psm1" -Force -ErrorAction Stop
    . "$PSScriptRoot/private/Compare-PolicyBaseline.ps1"
    . "$PSScriptRoot/private/Get-PolicyBaseline.ps1"

    # ─── Certificate-Based Graph Authentication ──────────────────────
    Write-Verbose "Connecting to Microsoft Graph for tenant $TenantId..."
    Connect-MgGraph -TenantId $TenantId -ClientId $ClientId `
        -CertificateThumbprint $CertificateThumbprint -NoWelcome

    # ─── Dataverse Connection ────────────────────────────────────────
    Write-Verbose "Acquiring Dataverse access token..."
    $dvToken = New-DataverseAccessToken `
        -TokenTenantId $TenantId `
        -TokenClientId $ClientId `
        -TokenCertThumbprint $CertificateThumbprint `
        -TokenResourceUrl $DataverseUrl

    Connect-CAADataverse -DataverseUrl $DataverseUrl -AccessToken $dvToken

    $conn = Get-CAAConnection
    if (-not $conn.IsConnected) {
        throw "Dataverse connection failed for $DataverseUrl"
    }

    # ─── Read Operational Parameters ─────────────────────────────────
    Write-Verbose "Reading operational parameters from Dataverse..."
    $gracePeriodHours    = Get-CAAEnvironmentVariable -Name 'GracePeriodHours'
    $baselineMaxAgeDays  = Get-CAAEnvironmentVariable -Name 'BaselineMaxAgeDays'
    $driftSeverityEsc    = Get-CAAEnvironmentVariable -Name 'DriftSeverityEscalation'
    $includeReportOnly   = Get-CAAEnvironmentVariable -Name 'IncludeReportOnlyPolicies'
    $teamsGroupId        = Get-CAAEnvironmentVariable -Name 'TeamsGroupId'
    $teamsChannelId      = Get-CAAEnvironmentVariable -Name 'TeamsChannelId'
    $escalationEnabled   = ($driftSeverityEsc -eq 'true')

    Write-Verbose ("Operational params — GracePeriodHours: {0}, BaselineMaxAgeDays: {1}, " +
        "DriftSeverityEscalation: {2}, IncludeReportOnlyPolicies: {3}") -f `
        $gracePeriodHours, $baselineMaxAgeDays, $driftSeverityEsc, $includeReportOnly

    # ─── Load Configuration ──────────────────────────────────────────
    if (-not (Test-Path $ConfigPath)) {
        throw "Configuration file not found: $ConfigPath"
    }
    $config = Get-Content -Path $ConfigPath -Raw | ConvertFrom-Json

    # ─── Query CA Policies ───────────────────────────────────────────
    Write-Verbose "Querying CA policies for tenant $TenantId..."
    $allPolicies = Get-MgIdentityConditionalAccessPolicy -All

    # Apply zone filter when -Zone is specified
    if ($Zone) {
        $policies = $allPolicies | Where-Object {
            $pz = Get-PolicyZone -DisplayName $_.DisplayName
            # Include: policies matching target zone, all-zones policies, or zone-agnostic policies
            ($pz -eq $Zone) -or ($pz -eq 0)
        }
    } else {
        $policies = $allPolicies
    }

    # Filter out report-only policies if configured
    if ($includeReportOnly -eq 'false') {
        $policies = $policies | Where-Object { $_.State -ne 'reportOnly' }
    }

    Write-Verbose "Evaluating $($policies.Count) CA policies (of $($allPolicies.Count) total)."

    # ─── Initialize Tracking ─────────────────────────────────────────
    $violations = [System.Collections.Generic.List[PSCustomObject]]::new()
    $driftItems = [System.Collections.Generic.List[PSCustomObject]]::new()
    $policyResults = @{}  # PolicyName -> 'Passed'|'Failed'|'Warning'

    # Expected policies from governance framework
    $expectedPolicies = @(
        'CA-M365Copilot-AllZones'
        'CA-BlockLegacyAuth-AI'
        'CA-CopilotStudio-Zone1'
        'CA-CopilotStudio-Zone2'
        'CA-CopilotStudio-Zone3'
        'CA-AgentBuilder-Zone2'
        'CA-AgentBuilder-Zone3'
        'CA-RequireCompliantDevice-Zone3'
    )

    # Filter expected policies by zone if specified
    if ($Zone) {
        $expectedPolicies = $expectedPolicies | Where-Object {
            $epZone = Get-PolicyZone -DisplayName $_
            ($epZone -eq $Zone) -or ($epZone -eq 0)
        }
    }

    # ═════════════════════════════════════════════════════════════════
    # Check 1: Policy Existence
    # ═════════════════════════════════════════════════════════════════
    Write-Verbose "Check 1: Policy Existence..."
    foreach ($expected in $expectedPolicies) {
        $found = $policies | Where-Object { $_.DisplayName -eq $expected }
        if (-not $found) {
            $policyZone = Get-PolicyZone -DisplayName $expected
            $severity = Get-EscalatedSeverity -BaseSeverity 4 -PolicyZone $policyZone `
                -EscalationEnabled $escalationEnabled

            $violations.Add([PSCustomObject]@{
                PolicyId          = ''
                PolicyName        = $expected
                ViolationType     = 'PolicyMissing'
                Zone              = $policyZone
                ExpectedValue     = 'Policy should exist'
                ActualValue       = 'Policy not found'
                Severity          = $severity
                SeverityLabel     = $severityLabels[$severity]
                RegulatoryContext = 'FINRA 4511, SOX 302'
            })
            $policyResults[$expected] = 'Failed'
        }
    }

    # ═════════════════════════════════════════════════════════════════
    # Check 2: Policy State
    # ═════════════════════════════════════════════════════════════════
    Write-Verbose "Check 2: Policy State..."
    foreach ($policy in $policies) {
        if ($policy.State -eq 'disabled') {
            $policyZone = Get-PolicyZone -DisplayName $policy.DisplayName
            $severity = Get-EscalatedSeverity -BaseSeverity 4 -PolicyZone $policyZone `
                -EscalationEnabled $escalationEnabled

            $violations.Add([PSCustomObject]@{
                PolicyId          = $policy.Id
                PolicyName        = $policy.DisplayName
                ViolationType     = 'PolicyDisabled'
                Zone              = $policyZone
                ExpectedValue     = 'enabled'
                ActualValue       = 'disabled'
                Severity          = $severity
                SeverityLabel     = $severityLabels[$severity]
                RegulatoryContext = 'FINRA 4511, SOX 302'
            })
            $policyResults[$policy.DisplayName] = 'Failed'
        }
        elseif (-not $policyResults.ContainsKey($policy.DisplayName)) {
            $policyResults[$policy.DisplayName] = 'Passed'
        }
    }

    # ═════════════════════════════════════════════════════════════════
    # Check 3: Break-Glass Exclusions
    # ═════════════════════════════════════════════════════════════════
    Write-Verbose "Check 3: Break-Glass Exclusions..."
    $breakGlassAccounts = $config.breakGlassAccounts
    foreach ($policy in $policies) {
        if ($policy.State -eq 'disabled') { continue }
        $excludedUsers = $policy.Conditions.Users.ExcludeUsers
        foreach ($bg in $breakGlassAccounts) {
            if ($excludedUsers -notcontains $bg) {
                $policyZone = Get-PolicyZone -DisplayName $policy.DisplayName
                $severity = Get-EscalatedSeverity -BaseSeverity 4 -PolicyZone $policyZone `
                    -EscalationEnabled $escalationEnabled

                $violations.Add([PSCustomObject]@{
                    PolicyId          = $policy.Id
                    PolicyName        = $policy.DisplayName
                    ViolationType     = 'BreakGlassExclusionMissing'
                    Zone              = $policyZone
                    ExpectedValue     = "Break-glass account $bg excluded"
                    ActualValue       = 'Account not in exclusion list'
                    Severity          = $severity
                    SeverityLabel     = $severityLabels[$severity]
                    RegulatoryContext = 'FINRA 4511, OCC 2011-12'
                })
                $policyResults[$policy.DisplayName] = 'Failed'
            }
        }
    }

    # ═════════════════════════════════════════════════════════════════
    # Check 4: MFA / Grant Controls
    # ═════════════════════════════════════════════════════════════════
    Write-Verbose "Check 4: MFA / Grant Controls..."
    foreach ($policy in $policies) {
        if ($policy.State -eq 'disabled') { continue }
        $controls = $policy.GrantControls
        $hasMfa = $controls.BuiltInControls -contains 'mfa'
        $isBlock = $controls.BuiltInControls -contains 'block'

        if (-not $hasMfa -and -not $isBlock) {
            $policyZone = Get-PolicyZone -DisplayName $policy.DisplayName
            $severity = Get-EscalatedSeverity -BaseSeverity 4 -PolicyZone $policyZone `
                -EscalationEnabled $escalationEnabled

            $violations.Add([PSCustomObject]@{
                PolicyId          = $policy.Id
                PolicyName        = $policy.DisplayName
                ViolationType     = 'GrantControlRemoved'
                Zone              = $policyZone
                ExpectedValue     = 'MFA required'
                ActualValue       = 'No grant controls'
                Severity          = $severity
                SeverityLabel     = $severityLabels[$severity]
                RegulatoryContext = 'FINRA 4511, SOX 302'
            })
            $policyResults[$policy.DisplayName] = 'Failed'
        }
    }

    # ═════════════════════════════════════════════════════════════════
    # Check 5: Session Controls (Zone Coverage)
    # ═════════════════════════════════════════════════════════════════
    Write-Verbose "Check 5: Session Controls..."
    foreach ($policy in $policies) {
        if ($policy.State -eq 'disabled') { continue }
        $controls = $policy.GrantControls
        $isBlock = $controls.BuiltInControls -contains 'block'
        if ($isBlock) { continue }

        $policyZone = Get-PolicyZone -DisplayName $policy.DisplayName
        $session = $policy.SessionControls

        # Zone 3 policies must have persistentBrowser mode 'never'
        if ($policyZone -eq 3 -and $session.PersistentBrowser.Mode -ne 'never') {
            $severity = Get-EscalatedSeverity -BaseSeverity 3 -PolicyZone $policyZone `
                -EscalationEnabled $escalationEnabled

            $violations.Add([PSCustomObject]@{
                PolicyId          = $policy.Id
                PolicyName        = $policy.DisplayName
                ViolationType     = 'SessionControlWeakened'
                Zone              = $policyZone
                ExpectedValue     = "persistentBrowser mode 'never'"
                ActualValue       = "persistentBrowser mode '$($session.PersistentBrowser.Mode)'"
                Severity          = $severity
                SeverityLabel     = $severityLabels[$severity]
                RegulatoryContext = 'FINRA 4511, GLBA 501(b)'
            })
            if ($policyResults[$policy.DisplayName] -ne 'Failed') {
                $policyResults[$policy.DisplayName] = 'Warning'
            }
        }
    }

    # ═════════════════════════════════════════════════════════════════
    # Check 6: Drift Detection Against Dataverse Baselines
    # ═════════════════════════════════════════════════════════════════
    Write-Verbose "Check 6: Drift Detection Against Dataverse Baselines..."
    $baselines = Get-CAAActiveBaseline -TenantId $TenantId

    # Filter baselines by zone when -Zone is specified
    if ($Zone -and $baselines) {
        $baselines = $baselines | Where-Object { $_.fsi_zone -eq $Zone }
    }

    if ($baselines -and $baselines.Count -gt 0) {
        # Build current policy snapshots for comparison
        $currentSnapshots = @()
        foreach ($policy in $policies) {
            $policyZone = Get-PolicyZone -DisplayName $policy.DisplayName
            $currentSnapshots += [PSCustomObject]@{
                PolicyId        = $policy.Id
                PolicyName      = $policy.DisplayName
                State           = $policy.State
                Zone            = $policyZone
                Conditions      = $policy.Conditions
                GrantControls   = $policy.GrantControls
                SessionControls = $policy.SessionControls
            }
        }

        # Convert Dataverse baseline records to comparison format
        $baselineSnapshots = @()
        foreach ($bl in $baselines) {
            $blObj = [PSCustomObject]@{
                PolicyId        = $bl.fsi_policy_id
                PolicyName      = $bl.fsi_policy_display_name
                State           = $bl.fsi_policy_state
                Zone            = $bl.fsi_zone
                Conditions      = if ($bl.fsi_conditions_json) {
                                      $bl.fsi_conditions_json | ConvertFrom-Json
                                  } else { $null }
                GrantControls   = if ($bl.fsi_grant_controls_json) {
                                      $bl.fsi_grant_controls_json | ConvertFrom-Json
                                  } else { $null }
                SessionControls = if ($bl.fsi_session_controls_json) {
                                      $bl.fsi_session_controls_json | ConvertFrom-Json
                                  } else { $null }
            }
            $baselineSnapshots += $blObj
        }

        # Run 5-dimension drift comparison
        $rawDrift = Compare-CAAPolicyBaseline -Baseline $baselineSnapshots -Current $currentSnapshots

        foreach ($drift in $rawDrift) {
            # Apply zone severity escalation for Zone 3
            $severity = Get-EscalatedSeverity -BaseSeverity $drift.Severity `
                -PolicyZone $drift.Zone -EscalationEnabled $escalationEnabled

            $driftItem = [PSCustomObject]@{
                PolicyId      = $drift.PolicyId
                PolicyName    = $drift.PolicyName
                DriftType     = $drift.DriftType
                Dimension     = $drift.Dimension
                Direction     = $drift.Direction
                BaselineValue = $drift.BaselineValue
                CurrentValue  = $drift.CurrentValue
                Zone          = $drift.Zone
                Severity      = $severity
            }
            $driftItems.Add($driftItem)

            # Write each drift violation to Dataverse
            Write-CAAViolation `
                -RunId $runId `
                -PolicyId $(if ($drift.PolicyId) { $drift.PolicyId } else { '' }) `
                -PolicyDisplayName $drift.PolicyName `
                -ViolationType $drift.ViolationType `
                -Zone $drift.Zone `
                -Severity $severity `
                -ExpectedValue ($drift.BaselineValue | Out-String).Trim() `
                -ActualValue ($drift.CurrentValue | Out-String).Trim() `
                -Description "Drift detected: $($drift.DriftType) in $($drift.Dimension) dimension" `
                -TenantId $TenantId

            # Update policy result status
            if ($severity -ge 4) {
                $policyResults[$drift.PolicyName] = 'Failed'
            }
            elseif ($policyResults[$drift.PolicyName] -ne 'Failed') {
                $policyResults[$drift.PolicyName] = 'Warning'
            }
        }
    }
    else {
        Write-Verbose "No active baselines found — drift analysis skipped."
    }

    # Write compliance check violations to Dataverse
    foreach ($v in $violations) {
        Write-CAAViolation `
            -RunId $runId `
            -PolicyId $(if ($v.PolicyId) { $v.PolicyId } else { '' }) `
            -PolicyDisplayName $v.PolicyName `
            -ViolationType $v.ViolationType `
            -Zone $v.Zone `
            -Severity $v.Severity `
            -ExpectedValue $v.ExpectedValue `
            -ActualValue $v.ActualValue `
            -Description "$($v.ViolationType): $($v.PolicyName)" `
            -TenantId $TenantId
    }

    # ═════════════════════════════════════════════════════════════════
    # Aggregate Results
    # ═════════════════════════════════════════════════════════════════
    $totalPolicies = ($policyResults.Keys | Measure-Object).Count
    if ($totalPolicies -eq 0) { $totalPolicies = ($policies | Measure-Object).Count }
    $passedCount  = ($policyResults.Values | Where-Object { $_ -eq 'Passed' } | Measure-Object).Count
    $failedCount  = ($policyResults.Values | Where-Object { $_ -eq 'Failed' } | Measure-Object).Count
    $warningCount = ($policyResults.Values | Where-Object { $_ -eq 'Warning' } | Measure-Object).Count
    $driftCount   = $driftItems.Count

    $complianceRate = if ($totalPolicies -gt 0) {
        [Math]::Round(($passedCount / $totalPolicies) * 100, 1)
    } else { 0.0 }

    # Overall severity = worst-case across all violations and drift
    $allSeverities = @($violations | ForEach-Object { $_.Severity }) +
                     @($driftItems | ForEach-Object { $_.Severity })
    $overallSeverity = if ($allSeverities.Count -gt 0) {
        ($allSeverities | Measure-Object -Maximum).Maximum
    } else { 1 }

    $overallStatus = if ($failedCount -gt 0) { 'Failed' }
                     elseif ($warningCount -gt 0 -or $driftCount -gt 0) { 'Warning' }
                     else { 'Passed' }

    $alertRequired = ($failedCount -gt 0 -or $driftCount -gt 0)
    $alertSeverity = $severityLabels[$overallSeverity]

    # ─── Zone Summary ────────────────────────────────────────────────
    $zoneSummaryList = @()
    foreach ($z in @(1, 2, 3)) {
        if ($Zone -and $Zone -ne $z) { continue }

        # Find policies belonging to this zone
        $zonePolicyNames = $policyResults.Keys | Where-Object {
            $zp = Get-PolicyZone -DisplayName $_
            $zp -eq $z
        }
        $zoneTotal  = ($zonePolicyNames | Measure-Object).Count
        $zonePassed = ($zonePolicyNames | Where-Object { $policyResults[$_] -eq 'Passed' } |
                       Measure-Object).Count

        # Zone worst-case severity
        $zoneMaxSev = 1
        $zoneViolations = $violations | Where-Object { $_.Zone -eq $z }
        $zoneDrift = $driftItems | Where-Object { $_.Zone -eq $z }
        $allZoneSev = @($zoneViolations | ForEach-Object { $_.Severity }) +
                      @($zoneDrift | ForEach-Object { $_.Severity })
        if ($allZoneSev.Count -gt 0) {
            $zoneMaxSev = ($allZoneSev | Measure-Object -Maximum).Maximum
        }

        $zoneSummaryList += [PSCustomObject]@{
            Zone     = $z
            Total    = $zoneTotal
            Passed   = $zonePassed
            Severity = $severityLabels[$zoneMaxSev]
        }
    }

    # ═════════════════════════════════════════════════════════════════
    # Build Output Payload
    # ═════════════════════════════════════════════════════════════════
    $outputPayload = [ordered]@{
        CheckedAt       = $checkedAt.ToString('o')
        TenantId        = $TenantId
        TotalPolicies   = $totalPolicies
        PassedCount     = $passedCount
        FailedCount     = $failedCount
        WarningCount    = $warningCount
        DriftCount      = $driftCount
        OverallSeverity = $overallSeverity
        OverallStatus   = $overallStatus
        ComplianceRate  = $complianceRate
        AlertRequired   = $alertRequired
        AlertSeverity   = $alertSeverity
        ZoneSummary     = @($zoneSummaryList)
        Violations      = @($violations)
        DriftItems      = @($driftItems)
    }

    # Tag as provisioning-triggered if Targeted scope
    if ($Scope -eq 'Targeted') {
        $outputPayload['ScanScope'] = 'Targeted'
        $outputPayload['ProvisioningTriggered'] = $true
    }

    $resultsJson = $outputPayload | ConvertTo-Json -Depth 20

    # ═════════════════════════════════════════════════════════════════
    # Audit-First: Write Validation History Before Output
    # ═════════════════════════════════════════════════════════════════
    Write-Verbose "Writing validation history to Dataverse (RunId: $runId)..."
    Write-CAAValidationHistory `
        -RunId $runId `
        -TotalPolicies $totalPolicies `
        -PassedCount $passedCount `
        -WarningCount $warningCount `
        -FailedCount $failedCount `
        -DriftCount $driftCount `
        -OverallSeverity $overallSeverity `
        -ResultsJson $resultsJson `
        -ValidatedBy $ClientId `
        -TenantId $TenantId

    # ═════════════════════════════════════════════════════════════════
    # Output Structured JSON (captured by Get-AzAutomationJobOutput)
    # ═════════════════════════════════════════════════════════════════
    Write-Output $resultsJson
}
catch {
    # ─── Error Handler: Emit Valid JSON for Downstream Processing ────
    $errorOutput = [ordered]@{
        CheckedAt       = [DateTime]::UtcNow.ToString('o')
        TenantId        = $TenantId
        TotalPolicies   = 0
        PassedCount     = 0
        FailedCount     = 0
        WarningCount    = 0
        DriftCount      = 0
        OverallSeverity = 5
        OverallStatus   = 'Error'
        ComplianceRate  = 0.0
        AlertRequired   = $true
        AlertSeverity   = 'Critical'
        ZoneSummary     = @()
        Violations      = @()
        DriftItems      = @()
        Error           = $_.Exception.Message
        ErrorDetails    = $_.ScriptStackTrace
    }
    Write-Output ($errorOutput | ConvertTo-Json -Depth 10)
}
finally {
    # Disconnect Graph session regardless of outcome
    try { Disconnect-MgGraph -ErrorAction SilentlyContinue } catch { }
}
