function Compare-CAAPolicyBaseline {
    <#
    .SYNOPSIS
        Compares current CA policies against baseline snapshots across 5 dimensions.
    .DESCRIPTION
        Performs multi-dimensional drift detection between stored baseline snapshots
        and current policy state. Evaluates 5 dimensions:

        1. State (enabled/disabled/reportOnly)
        2. Conditions (users, applications, platforms, locations)
        3. Grant controls (MFA, compliant device, block)
        4. Session controls (sign-in frequency, persistent browser)
        5. Additions/removals (new or deleted policies)

        Returns structured drift results with violation classification and severity
        ratings for downstream alerting and Dataverse persistence.
    .PARAMETER Baseline
        Array of baseline policy snapshot objects. Each object should have PolicyId,
        PolicyName, State, Zone, Conditions, GrantControls, and SessionControls.
    .PARAMETER Current
        Array of current policy snapshot objects with the same structure as Baseline.
    .EXAMPLE
        $drift = Compare-CAAPolicyBaseline -Baseline $savedBaseline -Current $currentState
    .OUTPUTS
        Array of PSCustomObject with PolicyId, PolicyName, DriftType, Dimension,
        Direction, BaselineValue, CurrentValue, Zone, Severity, ViolationType.
    .NOTES
        Part of the FSI Agent Governance — Conditional Access Automation solution.
        Controls: 1.11, 1.23, 1.18
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [AllowNull()]
        [AllowEmptyCollection()]
        [object[]]$Baseline,

        [Parameter(Mandatory)]
        [AllowNull()]
        [AllowEmptyCollection()]
        [object[]]$Current
    )

    $driftResults = @()

    if (-not $Baseline) { $Baseline = @() }
    if (-not $Current) { $Current = @() }

    # ─── Compare each baseline policy against current state ──────────
    foreach ($baselinePolicy in $Baseline) {
        # Match by PolicyId first, fall back to PolicyName
        $currentPolicy = $Current | Where-Object {
            ($_.PolicyId -and $_.PolicyId -eq $baselinePolicy.PolicyId) -or
            ($_.PolicyName -and $_.PolicyName -eq $baselinePolicy.PolicyName)
        } | Select-Object -First 1

        if (-not $currentPolicy) {
            # Dimension 5: Policy removed from tenant
            $driftResults += [PSCustomObject]@{
                PolicyId      = $baselinePolicy.PolicyId
                PolicyName    = $baselinePolicy.PolicyName
                DriftType     = 'PolicyMissing'
                Dimension     = 'additions_removals'
                Direction     = 'Removed'
                BaselineValue = "Policy existed (state: $($baselinePolicy.State))"
                CurrentValue  = 'Policy not found in tenant'
                Zone          = if ($baselinePolicy.Zone) { [int]$baselinePolicy.Zone } else { 0 }
                Severity      = 4
                ViolationType = 'PolicyMissing'
            }
            continue
        }

        $policyZone = if ($currentPolicy.Zone) { [int]$currentPolicy.Zone }
                      elseif ($baselinePolicy.Zone) { [int]$baselinePolicy.Zone }
                      else { 0 }

        # ─── Dimension 1: State ──────────────────────────────────────
        $baseState = $baselinePolicy.State
        $currState = $currentPolicy.State
        if ($baseState -and $currState -and $baseState -ne $currState) {
            $severity = if ($currState -eq 'disabled') { 4 }
                        elseif ($currState -eq 'reportOnly' -and $baseState -eq 'enabled') { 3 }
                        else { 2 }
            $violationType = if ($currState -eq 'disabled') { 'PolicyDisabled' }
                             else { 'StateChanged' }
            $direction = if ($severity -ge 3) { 'Weakened' } else { 'Changed' }

            $driftResults += [PSCustomObject]@{
                PolicyId      = $baselinePolicy.PolicyId
                PolicyName    = $baselinePolicy.PolicyName
                DriftType     = $violationType
                Dimension     = 'state'
                Direction     = $direction
                BaselineValue = $baseState
                CurrentValue  = $currState
                Zone          = $policyZone
                Severity      = $severity
                ViolationType = $violationType
            }
        }

        # ─── Dimension 2: Conditions ─────────────────────────────────
        $baseConditions = $baselinePolicy.Conditions | ConvertTo-Json -Depth 10 -Compress
        $currConditions = $currentPolicy.Conditions | ConvertTo-Json -Depth 10 -Compress
        if ($baseConditions -ne $currConditions) {
            $driftResults += [PSCustomObject]@{
                PolicyId      = $baselinePolicy.PolicyId
                PolicyName    = $baselinePolicy.PolicyName
                DriftType     = 'ConditionWeakened'
                Dimension     = 'conditions'
                Direction     = 'Weakened'
                BaselineValue = $baseConditions
                CurrentValue  = $currConditions
                Zone          = $policyZone
                Severity      = 3
                ViolationType = 'ConditionWeakened'
            }
        }

        # ─── Dimension 3: Grant Controls ─────────────────────────────
        $baseGrants = $baselinePolicy.GrantControls | ConvertTo-Json -Depth 10 -Compress
        $currGrants = $currentPolicy.GrantControls | ConvertTo-Json -Depth 10 -Compress
        if ($baseGrants -ne $currGrants) {
            # Check specifically whether MFA was removed
            $baseMfa = $false
            $currMfa = $false
            if ($baselinePolicy.GrantControls) {
                $baseMfa = $baselinePolicy.GrantControls.BuiltInControls -contains 'mfa'
            }
            if ($currentPolicy.GrantControls) {
                $currMfa = $currentPolicy.GrantControls.BuiltInControls -contains 'mfa'
            }

            $violationType = if ($baseMfa -and -not $currMfa) { 'GrantControlRemoved' }
                             else { 'GrantControlChanged' }
            $severity = if ($violationType -eq 'GrantControlRemoved') { 4 } else { 3 }

            $driftResults += [PSCustomObject]@{
                PolicyId      = $baselinePolicy.PolicyId
                PolicyName    = $baselinePolicy.PolicyName
                DriftType     = $violationType
                Dimension     = 'grant_controls'
                Direction     = 'Weakened'
                BaselineValue = $baseGrants
                CurrentValue  = $currGrants
                Zone          = $policyZone
                Severity      = $severity
                ViolationType = $violationType
            }
        }

        # ─── Dimension 4: Session Controls ───────────────────────────
        $baseSession = $baselinePolicy.SessionControls | ConvertTo-Json -Depth 10 -Compress
        $currSession = $currentPolicy.SessionControls | ConvertTo-Json -Depth 10 -Compress
        if ($baseSession -ne $currSession) {
            $driftResults += [PSCustomObject]@{
                PolicyId      = $baselinePolicy.PolicyId
                PolicyName    = $baselinePolicy.PolicyName
                DriftType     = 'SessionControlWeakened'
                Dimension     = 'session_controls'
                Direction     = 'Weakened'
                BaselineValue = $baseSession
                CurrentValue  = $currSession
                Zone          = $policyZone
                Severity      = 3
                ViolationType = 'SessionControlWeakened'
            }
        }
    }

    # ─── Dimension 5: Additions — new policies not in baseline ───────
    foreach ($currentPolicy in $Current) {
        $inBaseline = $Baseline | Where-Object {
            ($_.PolicyId -and $_.PolicyId -eq $currentPolicy.PolicyId) -or
            ($_.PolicyName -and $_.PolicyName -eq $currentPolicy.PolicyName)
        } | Select-Object -First 1

        if (-not $inBaseline) {
            $driftResults += [PSCustomObject]@{
                PolicyId      = $currentPolicy.PolicyId
                PolicyName    = $currentPolicy.PolicyName
                DriftType     = 'PolicyAdded'
                Dimension     = 'additions_removals'
                Direction     = 'Added'
                BaselineValue = 'Not in baseline'
                CurrentValue  = "Policy added (state: $($currentPolicy.State))"
                Zone          = if ($currentPolicy.Zone) { [int]$currentPolicy.Zone } else { 0 }
                Severity      = 2
                ViolationType = 'PolicyAdded'
            }
        }
    }

    return $driftResults
}
