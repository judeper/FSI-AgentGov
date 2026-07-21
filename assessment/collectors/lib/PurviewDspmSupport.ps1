Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$script:Microsoft365CopilotLocationId = '470f2276-e011-4e9d-a6ec-20768be3a4b0'

function Get-PurviewDspmPropertyValue {
    [CmdletBinding()]
    param(
        [Parameter()]
        [AllowNull()]
        [object]$InputObject,

        [Parameter(Mandatory)]
        [string[]]$Name
    )

    if ($null -eq $InputObject) {
        return $null
    }

    if ($InputObject -is [System.Collections.IDictionary]) {
        foreach ($candidate in $Name) {
            foreach ($key in $InputObject.Keys) {
                if ([string]::Equals([string]$key, $candidate, [System.StringComparison]::OrdinalIgnoreCase)) {
                    return $InputObject[$key]
                }
            }
        }
        return $null
    }

    foreach ($candidate in $Name) {
        $property = $InputObject.PSObject.Properties |
            Where-Object { [string]::Equals($_.Name, $candidate, [System.StringComparison]::OrdinalIgnoreCase) } |
            Select-Object -First 1
        if ($property) {
            return $property.Value
        }
    }

    return $null
}

function ConvertTo-PurviewDspmStringValues {
    [CmdletBinding()]
    param(
        [Parameter()]
        [AllowNull()]
        [object]$InputObject,

        [Parameter()]
        [ValidateRange(0, 12)]
        [int]$Depth = 0
    )

    if ($null -eq $InputObject -or $Depth -ge 12) {
        return @()
    }

    if ($InputObject -is [string]) {
        $text = $InputObject.Trim()
        if (-not $text) {
            return @()
        }

        if ($text.StartsWith('[') -or $text.StartsWith('{') -or $text.StartsWith('"')) {
            try {
                $parsed = $text | ConvertFrom-Json -ErrorAction Stop
                return @(ConvertTo-PurviewDspmStringValues -InputObject $parsed -Depth ($Depth + 1))
            }
            catch {
                # Preserve malformed serialized values as diagnostics; they cannot match exact signals.
            }
        }

        if ($text.StartsWith('[') -and $text.EndsWith(']')) {
            return @(ConvertTo-PurviewDspmStringValues -InputObject $text.Substring(1, $text.Length - 2) -Depth ($Depth + 1))
        }

        if ($text -match '[,;|]') {
            return @(
                $text -split '\s*[,;|]\s*' |
                    Where-Object { $_ } |
                    ForEach-Object { $_.Trim() }
            )
        }

        return @($text)
    }

    if ($InputObject -is [System.Collections.IDictionary]) {
        return @(
            foreach ($value in $InputObject.Values) {
                ConvertTo-PurviewDspmStringValues -InputObject $value -Depth ($Depth + 1)
            }
        )
    }

    if ($InputObject -is [System.Collections.IEnumerable]) {
        return @(
            foreach ($value in $InputObject) {
                ConvertTo-PurviewDspmStringValues -InputObject $value -Depth ($Depth + 1)
            }
        )
    }

    if ($InputObject -is [PSCustomObject]) {
        return @(
            foreach ($property in $InputObject.PSObject.Properties) {
                ConvertTo-PurviewDspmStringValues -InputObject $property.Value -Depth ($Depth + 1)
            }
        )
    }

    return @([string]$InputObject)
}

function Test-PurviewDspmPropertyPresent {
    [CmdletBinding()]
    param(
        [Parameter()]
        [AllowNull()]
        [object]$InputObject,

        [Parameter(Mandatory)]
        [string]$Name
    )

    if ($null -eq $InputObject) {
        return $false
    }

    if ($InputObject -is [System.Collections.IDictionary]) {
        return [bool]($InputObject.Keys | Where-Object {
            [string]::Equals([string]$_, $Name, [System.StringComparison]::OrdinalIgnoreCase)
        })
    }

    return [bool]($InputObject.PSObject.Properties | Where-Object {
        [string]::Equals($_.Name, $Name, [System.StringComparison]::OrdinalIgnoreCase)
    })
}

function ConvertTo-PurviewDspmDirectStringValues {
    [CmdletBinding()]
    param(
        [Parameter()]
        [AllowNull()]
        [object]$InputObject,

        [Parameter()]
        [ValidateRange(0, 6)]
        [int]$Depth = 0
    )

    if ($null -eq $InputObject -or $Depth -ge 6) {
        return @()
    }

    if ($InputObject -is [string]) {
        $text = $InputObject.Trim()
        if (-not $text) {
            return @()
        }

        if ($text.StartsWith('[') -or $text.StartsWith('{') -or $text.StartsWith('"')) {
            try {
                $parsed = $text | ConvertFrom-Json -ErrorAction Stop
                if ($parsed -is [System.Collections.IDictionary] -or $parsed -is [PSCustomObject]) {
                    return @()
                }
                return @(ConvertTo-PurviewDspmDirectStringValues -InputObject $parsed -Depth ($Depth + 1))
            }
            catch {
                return @()
            }
        }

        if ($text -match '[,;|]') {
            return @(
                $text -split '\s*[,;|]\s*' |
                    Where-Object { $_ } |
                    ForEach-Object { $_.Trim() }
            )
        }

        return @($text)
    }

    if ($InputObject -is [System.Collections.IDictionary] -or $InputObject -is [PSCustomObject]) {
        return @()
    }

    if ($InputObject -is [System.Collections.IEnumerable]) {
        return @(
            foreach ($value in $InputObject) {
                ConvertTo-PurviewDspmDirectStringValues -InputObject $value -Depth ($Depth + 1)
            }
        )
    }

    return @([string]$InputObject)
}

function ConvertTo-PurviewDspmLocationScopes {
    [CmdletBinding()]
    param(
        [Parameter()]
        [AllowNull()]
        [object]$InputObject,

        [Parameter()]
        [string[]]$InheritedWorkloads = @(),

        [Parameter()]
        [ValidateRange(0, 6)]
        [int]$Depth = 0
    )

    if ($null -eq $InputObject -or $Depth -ge 6) {
        return @()
    }

    if ($InputObject -is [string]) {
        $text = $InputObject.Trim()
        if (-not $text) {
            return @()
        }

        if ($text.StartsWith('[') -or $text.StartsWith('{') -or $text.StartsWith('"')) {
            try {
                $parsed = $text | ConvertFrom-Json -ErrorAction Stop
                return @(
                    ConvertTo-PurviewDspmLocationScopes `
                        -InputObject $parsed `
                        -InheritedWorkloads $InheritedWorkloads `
                        -Depth ($Depth + 1)
                )
            }
            catch {
                return @()
            }
        }

        return @(
            [PSCustomObject]@{
                Workloads = @($InheritedWorkloads)
                Locations = @($text)
            }
        )
    }

    if ($InputObject -is [System.Collections.IDictionary] -or $InputObject -is [PSCustomObject]) {
        if (-not (Test-PurviewDspmPropertyPresent -InputObject $InputObject -Name 'Location')) {
            return @()
        }

        $workloads = if (Test-PurviewDspmPropertyPresent -InputObject $InputObject -Name 'Workload') {
            @(
                ConvertTo-PurviewDspmDirectStringValues -InputObject (
                    Get-PurviewDspmPropertyValue -InputObject $InputObject -Name @('Workload')
                )
            )
        }
        else {
            @($InheritedWorkloads)
        }
        $locations = @(
            ConvertTo-PurviewDspmDirectStringValues -InputObject (
                Get-PurviewDspmPropertyValue -InputObject $InputObject -Name @('Location')
            )
        )

        return @(
            [PSCustomObject]@{
                Workloads = @($workloads)
                Locations = @($locations)
            }
        )
    }

    if ($InputObject -is [System.Collections.IEnumerable]) {
        return @(
            foreach ($value in $InputObject) {
                ConvertTo-PurviewDspmLocationScopes `
                    -InputObject $value `
                    -InheritedWorkloads $InheritedWorkloads `
                    -Depth ($Depth + 1)
            }
        )
    }

    return @(
        [PSCustomObject]@{
            Workloads = @($InheritedWorkloads)
            Locations = @([string]$InputObject)
        }
    )
}

function ConvertTo-PurviewDspmBoolean {
    [CmdletBinding()]
    param(
        [Parameter()]
        [AllowNull()]
        [object]$InputObject
    )

    if ($InputObject -is [bool]) {
        return $InputObject
    }

    if ($InputObject -is [int] -or $InputObject -is [long]) {
        if ($InputObject -eq 1) {
            return $true
        }
        if ($InputObject -eq 0) {
            return $false
        }
    }

    if ($InputObject -is [string]) {
        $parsed = $false
        if ([bool]::TryParse($InputObject.Trim(), [ref]$parsed)) {
            return $parsed
        }
    }

    return $null
}

function Test-PurviewDspmCriteriaPresent {
    [CmdletBinding()]
    param(
        [Parameter()]
        [AllowNull()]
        [object]$InputObject
    )

    return @(
        ConvertTo-PurviewDspmStringValues -InputObject $InputObject
    ).Count -gt 0
}

function Get-PurviewCopilotDlpRuleClassification {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object]$Rule
    )

    $disabled = ConvertTo-PurviewDspmBoolean -InputObject (
        Get-PurviewDspmPropertyValue -InputObject $Rule -Name @('Disabled')
    )
    $blockAccess = ConvertTo-PurviewDspmBoolean -InputObject (
        Get-PurviewDspmPropertyValue -InputObject $Rule -Name @('BlockAccess')
    )
    $enforcementPlanes = @(
        ConvertTo-PurviewDspmStringValues -InputObject (
            Get-PurviewDspmPropertyValue -InputObject $Rule -Name @('EnforcementPlanes')
        )
    )
    $enforcementPlaneMatched = [bool]($enforcementPlanes | Where-Object {
        [string]::Equals($_, 'CopilotExperiences', [System.StringComparison]::OrdinalIgnoreCase)
    })
    $sensitiveInformation = Get-PurviewDspmPropertyValue `
        -InputObject $Rule `
        -Name @('ContentContainsSensitiveInformation')
    $sensitivityLabels = Get-PurviewDspmPropertyValue `
        -InputObject $Rule `
        -Name @('ContentContainsSensitivityLabel')
    $sensitiveInformationMatched = Test-PurviewDspmCriteriaPresent -InputObject $sensitiveInformation
    $sensitivityLabelMatched = Test-PurviewDspmCriteriaPresent -InputObject $sensitivityLabels
    $activeRule = $disabled -eq $false
    $qualifies = (
        $activeRule -and
        $blockAccess -eq $true -and
        $enforcementPlaneMatched -and
        ($sensitiveInformationMatched -or $sensitivityLabelMatched)
    )

    $reasons = [System.Collections.Generic.List[string]]::new()
    if (-not $activeRule) {
        $reasons.Add('Rule is disabled or does not prove Disabled=false.')
    }
    if ($blockAccess -ne $true) {
        $reasons.Add('Rule does not prove BlockAccess=true.')
    }
    if (-not $enforcementPlaneMatched) {
        $reasons.Add('Rule EnforcementPlanes does not include CopilotExperiences.')
    }
    if (-not ($sensitiveInformationMatched -or $sensitivityLabelMatched)) {
        $reasons.Add('Rule does not contain sensitive-information or sensitivity-label criteria.')
    }
    if ($qualifies) {
        $reasons.Add('Qualifying active Microsoft 365 Copilot blocking rule.')
    }

    [PSCustomObject]@{
        Name                                = Get-PurviewDspmPropertyValue -InputObject $Rule -Name @('Name', 'Identity')
        Priority                            = Get-PurviewDspmPropertyValue -InputObject $Rule -Name @('Priority')
        Qualifies                           = [bool]$qualifies
        ActiveRule                          = [bool]$activeRule
        Disabled                            = $disabled
        BlockAccess                         = $blockAccess
        EnforcementPlaneMatched             = [bool]$enforcementPlaneMatched
        SensitiveInformationMatched         = [bool]$sensitiveInformationMatched
        SensitivityLabelMatched             = [bool]$sensitivityLabelMatched
        EnforcementPlanes                   = @($enforcementPlanes | Sort-Object -Unique)
        ContentContainsSensitiveInformation = $sensitiveInformation
        ContentContainsSensitivityLabel     = $sensitivityLabels
        Diagnostic                          = $reasons -join ' '
    }
}

function Get-PurviewCopilotDlpClassification {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object]$Policy
    )

    $topLevelWorkloads = @(
        ConvertTo-PurviewDspmDirectStringValues -InputObject (
            Get-PurviewDspmPropertyValue -InputObject $Policy -Name @('Workload')
        )
    )
    $locationsInput = Get-PurviewDspmPropertyValue -InputObject $Policy -Name @('Locations')
    $locationInput = Get-PurviewDspmPropertyValue -InputObject $Policy -Name @('Location')
    $locationScopes = @(
        ConvertTo-PurviewDspmLocationScopes `
            -InputObject $locationsInput `
            -InheritedWorkloads $topLevelWorkloads
        ConvertTo-PurviewDspmLocationScopes `
            -InputObject $locationInput `
            -InheritedWorkloads $topLevelWorkloads
    )
    $workloads = @(
        $topLevelWorkloads
        foreach ($scope in $locationScopes) {
            $scope.Workloads
        }
    )
    $locations = @(
        foreach ($scope in $locationScopes) {
            $scope.Locations
        }
    )
    $enforcementPlanes = @(
        ConvertTo-PurviewDspmStringValues -InputObject (
            Get-PurviewDspmPropertyValue -InputObject $Policy -Name @('EnforcementPlanes')
        )
    )

    $mode = Get-PurviewDspmPropertyValue -InputObject $Policy -Name @('Mode')
    $enabled = ConvertTo-PurviewDspmBoolean -InputObject (
        Get-PurviewDspmPropertyValue -InputObject $Policy -Name @('Enabled')
    )
    $normalizedMode = if ($null -eq $mode) { '' } else { ([string]$mode).Trim().ToLowerInvariant() }
    $rulesInput = Get-PurviewDspmPropertyValue -InputObject $Policy -Name @('Rules')
    $ruleCollectionStatusInput = Get-PurviewDspmPropertyValue -InputObject $Policy -Name @('RuleCollectionStatus')
    $ruleCollectionSucceeded = ConvertTo-PurviewDspmBoolean -InputObject (
        Get-PurviewDspmPropertyValue -InputObject $Policy -Name @('RuleCollectionSucceeded')
    )
    $normalizedRuleCollectionStatus = if ($null -eq $ruleCollectionStatusInput) {
        ''
    }
    else {
        ([string]$ruleCollectionStatusInput).Trim().ToLowerInvariant()
    }
    if ($null -eq $ruleCollectionSucceeded) {
        if ($normalizedRuleCollectionStatus -eq 'collected') {
            $ruleCollectionSucceeded = $true
        }
        elseif ($normalizedRuleCollectionStatus -in @('failed', 'unavailable', 'error', 'unknown')) {
            $ruleCollectionSucceeded = $false
        }
        else {
            $ruleCollectionSucceeded = Test-PurviewDspmPropertyPresent -InputObject $Policy -Name 'Rules'
        }
    }
    $ruleCollectionStatus = if ($ruleCollectionSucceeded -eq $true) { 'collected' } else { 'failed' }
    $ruleDiagnostics = @(
        foreach ($rule in @($rulesInput)) {
            if ($null -ne $rule) {
                Get-PurviewCopilotDlpRuleClassification -Rule $rule
            }
        }
    )
    $qualifyingRules = @($ruleDiagnostics | Where-Object { $_.Qualifies })

    $workloadMatched = [bool]($workloads | Where-Object {
        [string]::Equals($_, 'Applications', [System.StringComparison]::OrdinalIgnoreCase)
    })
    $locationMatched = [bool]($locations | Where-Object {
        [string]::Equals($_, $script:Microsoft365CopilotLocationId, [System.StringComparison]::OrdinalIgnoreCase)
    })
    $locationScopeMatched = [bool]($locationScopes | Where-Object {
        $scopeWorkloadMatched = [bool]($_.Workloads | Where-Object {
            [string]::Equals($_, 'Applications', [System.StringComparison]::OrdinalIgnoreCase)
        })
        $scopeLocationMatched = [bool]($_.Locations | Where-Object {
            [string]::Equals($_, $script:Microsoft365CopilotLocationId, [System.StringComparison]::OrdinalIgnoreCase)
        })
        $scopeWorkloadMatched -and $scopeLocationMatched
    })
    $enforcementPlaneMatched = [bool]($enforcementPlanes | Where-Object {
        [string]::Equals($_, 'CopilotExperiences', [System.StringComparison]::OrdinalIgnoreCase)
    })
    $activeEnforcement = (
        $normalizedMode -in @('enable', 'enforce') -and
        $enabled -ne $false
    )
    $policyLevelMatched = $locationScopeMatched -and $enforcementPlaneMatched -and $activeEnforcement
    $ruleEvidenceAvailable = $ruleCollectionSucceeded -eq $true

    $reasons = [System.Collections.Generic.List[string]]::new()
    if (-not $workloadMatched) {
        $reasons.Add('Workload does not include Applications.')
    }
    if (-not $locationMatched) {
        $reasons.Add("Locations/Location does not include $script:Microsoft365CopilotLocationId.")
    }
    elseif (-not $locationScopeMatched) {
        $reasons.Add('Workload=Applications and the Copilot location do not occur in the same location scope.')
    }
    if (($null -ne $locationsInput -or $null -ne $locationInput) -and $locationScopes.Count -eq 0) {
        $reasons.Add('Locations/Location did not expose a supported direct location scope; arbitrary nested values were ignored.')
    }
    if (-not $enforcementPlaneMatched) {
        $reasons.Add('EnforcementPlanes does not include CopilotExperiences.')
    }
    if (-not $activeEnforcement) {
        $reasons.Add('Policy is not proven actively enforced (Mode must be Enable or Enforce and Enabled must not be explicitly false).')
    }
    if ($policyLevelMatched -and -not $ruleEvidenceAvailable) {
        $reasons.Add('Rule evidence collection failed or was unavailable for this otherwise matching policy.')
    }
    elseif ($policyLevelMatched -and $qualifyingRules.Count -eq 0) {
        $reasons.Add('No collected rule was active, blocking, scoped to CopilotExperiences, and conditioned on sensitive information or sensitivity labels.')
    }

    $qualifies = $policyLevelMatched -and $ruleEvidenceAvailable -and $qualifyingRules.Count -gt 0
    if ($qualifies) {
        $reasons.Add('Qualifying actively enforced Microsoft 365 Copilot DLP policy with relevant active blocking rule evidence.')
    }

    [PSCustomObject]@{
        Name                    = Get-PurviewDspmPropertyValue -InputObject $Policy -Name @('Name', 'Identity')
        Qualifies               = [bool]$qualifies
        WorkloadMatched         = [bool]$workloadMatched
        LocationMatched         = [bool]$locationMatched
        EnforcementPlaneMatched = [bool]$enforcementPlaneMatched
        ActiveEnforcement       = [bool]$activeEnforcement
        PolicyLevelMatched      = [bool]$policyLevelMatched
        RuleEvidenceAvailable   = [bool]$ruleEvidenceAvailable
        RuleCollectionStatus    = $ruleCollectionStatus
        RuleCount               = $ruleDiagnostics.Count
        QualifyingRuleCount     = $qualifyingRules.Count
        QualifyingRuleNames     = @($qualifyingRules | ForEach-Object { $_.Name })
        RuleDiagnostics         = @($ruleDiagnostics)
        Mode                    = $mode
        Enabled                 = $enabled
        Workloads               = @($workloads | Sort-Object -Unique)
        Locations               = @($locations | Sort-Object -Unique)
        EnforcementPlanes       = @($enforcementPlanes | Sort-Object -Unique)
        Diagnostic              = $reasons -join ' '
    }
}

function New-PurviewDspmEvidence {
    [CmdletBinding()]
    param(
        [Parameter()]
        [AllowNull()]
        [object[]]$Policies,

        [Parameter(Mandatory)]
        [bool]$DlpCollectionSucceeded,

        [Parameter()]
        [bool]$RetentionCoverage = $false,

        [Parameter()]
        [string[]]$RetentionPolicyNames = @()
    )

    if (-not $DlpCollectionSucceeded) {
        return [PSCustomObject]@{
            CollectionStatus                   = 'failed'
            Detected                           = $null
            PolicyCount                        = 0
            PolicyNames                        = @()
            DiagnosticPolicyCount              = 0
            PolicyDiagnostics                  = @()
            RuleCollectionFailureCount         = 0
            RelevantRuleCollectionFailureCount = 0
            RetentionCoverage                  = $RetentionCoverage
            RetentionPolicyNames               = @($RetentionPolicyNames)
            Note                               = 'DLP policy collection failed or was unavailable; DSPM enforcement cannot be determined.'
        }
    }

    $diagnostics = @(
        foreach ($policy in @($Policies)) {
            if ($null -ne $policy) {
                Get-PurviewCopilotDlpClassification -Policy $policy
            }
        }
    )
    $qualifying = @($diagnostics | Where-Object { $_.Qualifies })
    $ruleCollectionFailures = @($diagnostics | Where-Object { -not $_.RuleEvidenceAvailable })
    $relevantRuleCollectionFailures = @($diagnostics | Where-Object {
        $_.PolicyLevelMatched -and -not $_.RuleEvidenceAvailable
    })

    $collectionStatus = 'collected'
    $detected = [bool]($qualifying.Count -gt 0)
    $note = if ($qualifying.Count -gt 0) {
        "Detected $($qualifying.Count) actively enforced Microsoft 365 Copilot DLP policy/policies with relevant active blocking rule evidence."
    }
    elseif ($relevantRuleCollectionFailures.Count -gt 0) {
        $collectionStatus = 'failed'
        $detected = $null
        $failedNames = @($relevantRuleCollectionFailures | ForEach-Object { $_.Name }) -join ', '
        "DLP policy collection succeeded, but rule evidence failed or was unavailable for otherwise matching Microsoft 365 Copilot DLP policy/policies: $failedNames. DSPM enforcement cannot be determined."
    }
    else {
        "DLP collection succeeded, but no actively enforced Microsoft 365 Copilot DLP policy had all policy-level signals and a relevant active blocking rule. Retention coverage is informational only and does not satisfy control 1.6."
    }

    [PSCustomObject]@{
        CollectionStatus                   = $collectionStatus
        Detected                           = $detected
        PolicyCount                        = $qualifying.Count
        PolicyNames                        = @($qualifying | ForEach-Object { $_.Name })
        DiagnosticPolicyCount              = $diagnostics.Count
        PolicyDiagnostics                  = @($diagnostics)
        RuleCollectionFailureCount         = $ruleCollectionFailures.Count
        RelevantRuleCollectionFailureCount = $relevantRuleCollectionFailures.Count
        RetentionCoverage                  = $RetentionCoverage
        RetentionPolicyNames               = @($RetentionPolicyNames)
        Note                               = $note
    }
}
