Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Invoke-CollectorOperation {
    <#
    .SYNOPSIS
        Runs a collector operation scriptblock under ShouldProcess, optionally
        reporting whether the operation actually executed or was skipped.

    .DESCRIPTION
        Extracted from Collect-PPAC.ps1 so the skip-vs-execute contract is unit
        testable without a live tenant; behavior for existing call sites (normal
        runs and script-level -WhatIf) is unchanged.

        A -WhatIf / declined ShouldProcess returns $null WITHOUT invoking the
        scriptblock. By return value alone that is indistinguishable from a
        scriptblock (e.g. Get-DlpPolicy) that executed successfully and returned no
        rows. The optional -ExecutionStatus [ref] disambiguates the two: it is set to
        'Skipped' when ShouldProcess declines and 'Executed' once the scriptblock is
        about to run. A caller (only Section 2 / DLP needs this) can then treat a skip
        as unknown evidence rather than as a successful empty result. Call sites that
        omit -ExecutionStatus are entirely unaffected.

    .PARAMETER ExecutionStatus
        Optional [ref] receiving 'Skipped' or 'Executed'. Pre-seeded to 'Skipped' so
        that even an early return leaves a correct value.
    #>
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory)][string]$Target,
        [Parameter(Mandatory)][string]$Action,
        [Parameter(Mandatory)][scriptblock]$ScriptBlock,
        [Parameter()][ref]$ExecutionStatus
    )

    if ($null -ne $ExecutionStatus) { $ExecutionStatus.Value = 'Skipped' }

    if (-not $PSCmdlet.ShouldProcess($Target, $Action)) {
        Write-Verbose "Skipping $Action on $Target because -WhatIf was specified."
        return $null
    }

    if ($null -ne $ExecutionStatus) { $ExecutionStatus.Value = 'Executed' }
    & $ScriptBlock
}

function Get-PpacDlpProperty {
    <#
    .SYNOPSIS
        Reads a named property from a Get-DlpPolicy object without throwing under
        Set-StrictMode -Version Latest when the property is absent.

    .DESCRIPTION
        StrictMode -Version Latest raises PropertyNotFoundStrict on any reference to a
        non-existent property. Classic DLP policy objects vary by module build: a
        member such as isEnabled, createdTime, or connectorGroups may be absent
        entirely (classic DLP has no enable/disable property at all). A direct
        $_.isEnabled dereference would then throw, the whole policy projection would
        fail, and its environment scope would be lost — forcing Control 1.4.a to
        unknown even though valid scope was collected. Reading through the PSObject
        property collection (indexing a missing name returns $null) keeps the
        projection total: a genuinely absent member is reported as $null so the
        evaluator can fail closed on a missing signal without mistaking it for a
        collection failure. Mirrors lib/PurviewDlpSupport.ps1 Get-DlpScopeProperty.

        The value is returned through the unary array-construction operator
        (, $property.Value) so the reader is NON-ENUMERATING. A bare
        `return $property.Value` streams the value as normal function output, which
        PowerShell enumerates: a PRESENT empty array ($property.Value = @()) then
        enumerates to zero output objects and the caller receives $null —
        indistinguishable from an absent property. That silently discarded a valid
        empty environment scope (environments = @()), so an ExceptEnvironments policy
        that excludes nothing was projected as Environments = null instead of [],
        which the Python scorer reads as "malformed (fail closed)" rather than
        "covers all inventory", and an OnlyEnvironments empty scope likewise degraded
        from a clean fail to malformed. Wrapping in a one-element array and letting
        function output unroll exactly that one wrapper emits the underlying value as
        a single object: a present @() stays @() at the caller, a scalar
        (string/bool/datetime) stays a scalar (NOT a one-element array), a populated
        array stays that array, an absent property is still $null (early return), and
        a present $null stays $null.

    .OUTPUTS
        The property value, unchanged in scalar-vs-array shape (a present empty array
        remains an empty array), or $null when the object or property is absent.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][AllowNull()][object]$InputObject,
        [Parameter(Mandatory)][string]$Name
    )

    if ($null -eq $InputObject) { return $null }
    $property = $InputObject.PSObject.Properties[$Name]
    if ($null -eq $property) { return $null }
    # Unary comma: non-enumerating return so a present empty array survives as @()
    # (a bare return would enumerate @() to no output, collapsing it to $null).
    return , $property.Value
}

function ConvertTo-PpacDlpPolicyList {
    <#
    .SYNOPSIS
        Projects raw Get-DlpPolicy output into the collected DLP-policy contract
        (ppac.json .dlpPolicies) consumed by the assessment engine's Control 1.4
        classic-DLP evaluator.

    .DESCRIPTION
        Get-DlpPolicy emits nothing when a tenant has no classic DLP policies. In
        that case the caller's raw result is $null, and a bare

            $null | ForEach-Object { [PSCustomObject]@{ ... } }

        still executes its body once with $_ = $null, projecting a single all-null
        phantom policy. Downstream that made the scorer report the evidence as
        "malformed" instead of "No classic DLP policies found", and raised a false
        Service-Principal-bypass warning (the SP check fires whenever one or more
        policies are present).

        This helper drops $null entries before projection, so the three collection
        outcomes map to distinct, stable shapes:

          * no rows   -> [] (empty array; serializes as "dlpPolicies": [], which the
                         evaluator scores as "No classic DLP policies found" — a clean
                         fail, never "malformed").
          * one row   -> single-element array. The trailing comma operator preserves
                         the array shape through ConvertTo-Json -Depth 10 so a lone
                         policy is never collapsed to a bare object.
          * many rows -> multi-element array.

        Each policy's Environments is normalized to an array with the comma operator
        for the same anti-collapse reason, preserving the object-shaped Environments
        contract ({ id, name, type }). The three scope shapes are kept distinct so the
        scorer's All/Except/Only semantics hold:

          * environments absent or null          -> Environments = null (All-scope;
                                                    the scope was never restricted).
          * environments present but empty (@())  -> Environments = [] (an explicitly
                                                    empty scope: ExceptEnvironments []
                                                    excludes nothing so it covers ALL
                                                    inventory; OnlyEnvironments []
                                                    includes nothing so it covers
                                                    nothing — a clean fail). This
                                                    relies on Get-PpacDlpProperty being
                                                    non-enumerating; a bare read would
                                                    collapse a present @() to null and
                                                    the scorer would misreport it as
                                                    "malformed (fail closed)".
          * environments populated                -> Environments = the object array.

        A collection *exception* never reaches this helper: the caller leaves
        $dlpPolicies = $null on failure so the scorer treats it as unknown, which is
        distinct from a successful empty [] collection.

        Every property is read through Get-PpacDlpProperty so the projection never
        throws under Set-StrictMode when a classic DLP object omits an optional member
        (isEnabled/createdTime/connectorGroups); the resulting evidence for a
        well-formed policy is unchanged. Because that reader is non-enumerating, a
        collection it returns (connectorGroups, connectors) is staged into a variable
        before being piped, so Where-Object/Select-Object still see one pipeline object
        per element; piping the reader call directly would hand the whole collection to
        the first filter as a single element. Only the $null-filtering, the
        StrictMode-safe reads, and the guaranteed array return differ from the original
        inline projection.

    .PARAMETER RawDlpPolicy
        The raw pipeline output of Get-DlpPolicy: $null (no rows), a single policy
        object, or many. Accepted positionally; not bound from the pipeline so that
        a $null argument is preserved (rather than suppressing invocation).

    .OUTPUTS
        System.Object[]. Always an array (possibly empty); never $null and never a
        phantom placeholder.
    #>
    param(
        [Parameter(Mandatory = $false, Position = 0)]
        $RawDlpPolicy
    )

    $rawList = @($RawDlpPolicy | Where-Object { $null -ne $_ })
    $projected = @($rawList | ForEach-Object {
            $policy = $_
            # Get-PpacDlpProperty is non-enumerating (returns via unary comma so a
            # present empty scope survives as @()). Its output must therefore be staged
            # into a variable before piping: piping the *variable* enumerates the
            # collection, whereas piping the reader *call* would deliver the whole
            # collection to Where-Object as a single element.
            $connectorGroupsRaw = Get-PpacDlpProperty -InputObject $policy -Name 'connectorGroups'
            $connectorGroups = @($connectorGroupsRaw | Where-Object { $null -ne $_ })
            $environments = Get-PpacDlpProperty -InputObject $policy -Name 'environments'
            [PSCustomObject]@{
                DisplayName          = Get-PpacDlpProperty -InputObject $policy -Name 'displayName'
                PolicyName           = Get-PpacDlpProperty -InputObject $policy -Name 'name'
                CreatedTime          = Get-PpacDlpProperty -InputObject $policy -Name 'createdTime'
                IsEnabled            = Get-PpacDlpProperty -InputObject $policy -Name 'isEnabled'
                BusinessDataGroup    = $connectorGroups |
                    Where-Object { (Get-PpacDlpProperty -InputObject $_ -Name 'classification') -eq 'Confidential' } |
                    ForEach-Object {
                        $connectors = Get-PpacDlpProperty -InputObject $_ -Name 'connectors'
                        $connectors | Where-Object { $null -ne $_ } | Select-Object id, name
                    }
                NonBusinessDataGroup = $connectorGroups |
                    Where-Object { (Get-PpacDlpProperty -InputObject $_ -Name 'classification') -eq 'General' } |
                    ForEach-Object {
                        $connectors = Get-PpacDlpProperty -InputObject $_ -Name 'connectors'
                        $connectors | Where-Object { $null -ne $_ } | Select-Object id, name
                    }
                BlockedGroup         = $connectorGroups |
                    Where-Object { (Get-PpacDlpProperty -InputObject $_ -Name 'classification') -eq 'Blocked' } |
                    ForEach-Object {
                        $connectors = Get-PpacDlpProperty -InputObject $_ -Name 'connectors'
                        $connectors | Where-Object { $null -ne $_ } | Select-Object id, name
                    }
                EnvironmentType      = Get-PpacDlpProperty -InputObject $policy -Name 'environmentType'
                Environments         = if ($null -ne $environments) { , @($environments) } else { $null }
            }
        })

    return , $projected
}
