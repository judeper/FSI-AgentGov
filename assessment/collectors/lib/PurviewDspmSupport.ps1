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
        $enabled -eq $true -and
        $normalizedMode -in @('enable', 'enforce')
    )

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
        $reasons.Add('Policy is not proven actively enforced (Enabled=true and Mode must be Enable or Enforce).')
    }

    $qualifies = $locationScopeMatched -and $enforcementPlaneMatched -and $activeEnforcement
    if ($qualifies) {
        $reasons.Add('Qualifying actively enforced Microsoft 365 Copilot DLP policy.')
    }

    [PSCustomObject]@{
        Name                    = Get-PurviewDspmPropertyValue -InputObject $Policy -Name @('Name', 'Identity')
        Qualifies               = [bool]$qualifies
        WorkloadMatched         = [bool]$workloadMatched
        LocationMatched         = [bool]$locationMatched
        EnforcementPlaneMatched = [bool]$enforcementPlaneMatched
        ActiveEnforcement       = [bool]$activeEnforcement
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
            CollectionStatus         = 'failed'
            Detected                 = $null
            PolicyCount              = 0
            PolicyNames              = @()
            DiagnosticPolicyCount    = 0
            PolicyDiagnostics        = @()
            RetentionCoverage        = $RetentionCoverage
            RetentionPolicyNames     = @($RetentionPolicyNames)
            Note                     = 'DLP policy collection failed or was unavailable; DSPM enforcement cannot be determined.'
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

    $note = if ($qualifying.Count -gt 0) {
        "Detected $($qualifying.Count) actively enforced Microsoft 365 Copilot DLP policy/policies with all documented signals."
    }
    else {
        "DLP collection succeeded, but no actively enforced Microsoft 365 Copilot DLP policy matched Workload=Applications, Location=$script:Microsoft365CopilotLocationId, and EnforcementPlane=CopilotExperiences. Retention coverage is informational only and does not satisfy control 1.6."
    }

    [PSCustomObject]@{
        CollectionStatus         = 'collected'
        Detected                 = [bool]($qualifying.Count -gt 0)
        PolicyCount              = $qualifying.Count
        PolicyNames              = @($qualifying | ForEach-Object { $_.Name })
        DiagnosticPolicyCount    = $diagnostics.Count
        PolicyDiagnostics        = @($diagnostics)
        RetentionCoverage        = $RetentionCoverage
        RetentionPolicyNames     = @($RetentionPolicyNames)
        Note                     = $note
    }
}
