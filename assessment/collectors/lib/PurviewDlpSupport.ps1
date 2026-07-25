Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Resolve-DlpRuleEvidence {
    <#
    .SYNOPSIS
        Normalizes a collected DLP compliance rule set into the purview.json
        evidence contract consumed by the assessment engine (control 1.13.b,
        _eval_dlp_references_sits).

    .DESCRIPTION
        The DLP rule evidence must distinguish three states so the evaluator can
        score them correctly and never conflate "no active rules" with "not
        collected":

          * Successful collection, one or more rules -> array of rule objects
            (the evaluator inspects each rule for SIT conditions).
          * Successful collection, zero rules        -> empty array []; the
            evaluator scores this fail (an enforced policy with no SIT-backed
            active rules).
          * Collection failure / unavailable         -> $null; the evaluator
            treats the rule set as indeterminate and returns unknown. The
            caller records a diagnostic warning separately so a null rule set is
            only ever produced when collection is genuinely indeterminate.

        A successfully collected empty rule set must therefore serialize as [],
        NOT as null. PowerShell collapses an empty pipeline to $null and a lone
        item to a scalar, so this helper re-establishes a stable array shape on
        success (empty stays empty; a single rule becomes a one-item array,
        which the evaluator's singleton normalization still accepts). The array
        is returned with the unary comma operator so the function's return value
        is not flattened back to a scalar/$null by PowerShell output enumeration.

    .PARAMETER CollectedRules
        The raw rule payload captured from Get-DlpComplianceRule (may be $null,
        a single rule object, or an array). Ignored when -CollectionSucceeded is
        $false.

    .PARAMETER CollectionSucceeded
        $true when the rule query completed without throwing (even if it
        returned zero rows); $false when the query failed or was unavailable.

    .OUTPUTS
        System.Object[] on success (possibly empty), or $null on failure.
    #>
    [CmdletBinding()]
    param(
        [Parameter()]
        [AllowNull()]
        [object]$CollectedRules,

        [Parameter(Mandatory)]
        [bool]$CollectionSucceeded
    )

    if (-not $CollectionSucceeded) {
        # Genuine collection failure/unavailability: keep the rule set null so
        # the evaluator treats it as indeterminate (unknown), never as an
        # affirmatively-empty rule set.
        return $null
    }

    if ($null -eq $CollectedRules) {
        # Successful collection that yielded zero rows. Represent it as an
        # explicit empty array so the evidence records "collected, none active"
        # (evaluator: fail) rather than "not collected" (evaluator: unknown).
        return , @()
    }

    # Successful collection with one or more rows. Force a stable array shape
    # (a lone rule becomes a one-item array) and return it without enumeration.
    return , @($CollectedRules)
}

function Resolve-DlpPolicyEvidence {
    <#
    .SYNOPSIS
        Normalizes a collected DLP compliance policy set into the purview.json
        evidence contract consumed by the assessment engine (control 1.13.b,
        _eval_dlp_references_sits).

    .DESCRIPTION
        This is the policy-set analogue of Resolve-DlpRuleEvidence, applying the
        same successful-empty-versus-collection-failure distinction one level up.
        Get-DlpCompliancePolicy is captured into a foreach projection, which
        PowerShell collapses to $null when the query succeeds but returns zero
        rows — indistinguishable, without a success flag, from a query that
        actually failed. The evaluator, however, must treat the two differently:

          * Successful collection, one or more policies -> array of policy
            objects (the evaluator inspects each for Mode=Enable + SIT rules).
          * Successful collection, zero policies         -> empty array []; the
            evaluator scores this fail ("No Mode=Enable DLP compliance policies
            found"), because the absence of any policy was affirmatively
            observed.
          * Collection failure / unavailable            -> $null; the evaluator
            returns unknown ("dlpCompliancePolicies not collected"). The caller
            records a diagnostic warning separately so a null policy set is only
            ever produced when collection is genuinely indeterminate.

        A successfully collected empty policy set must therefore serialize as [],
        NOT as null. As with rules, the success flag — not the captured shape —
        drives the empty-vs-failure distinction, and this helper re-establishes a
        stable array on success: an empty set stays [], while a single policy is
        normalized to a one-item array (which the evaluator's singleton
        normalization still accepts). The array is returned with the unary comma
        operator so it is not flattened back to a scalar/$null by PowerShell
        output enumeration.

    .PARAMETER CollectedPolicies
        The raw policy payload projected from Get-DlpCompliancePolicy (may be
        $null, a single policy object, or an array). Ignored when
        -CollectionSucceeded is $false.

    .PARAMETER CollectionSucceeded
        $true when the policy query completed without throwing (even if it
        returned zero rows); $false when the query failed or was unavailable.

    .OUTPUTS
        System.Object[] on success (possibly empty), or $null on failure.
    #>
    [CmdletBinding()]
    param(
        [Parameter()]
        [AllowNull()]
        [object]$CollectedPolicies,

        [Parameter(Mandatory)]
        [bool]$CollectionSucceeded
    )

    if (-not $CollectionSucceeded) {
        # Genuine collection failure/unavailability: keep the policy set null so
        # the evaluator treats it as indeterminate (unknown), never as an
        # affirmatively-empty policy set.
        return $null
    }

    if ($null -eq $CollectedPolicies) {
        # Successful collection that yielded zero rows. Represent it as an
        # explicit empty array so the evidence records "collected, none present"
        # (evaluator: fail) rather than "not collected" (evaluator: unknown).
        return , @()
    }

    # Successful collection with one or more rows. Force a stable array shape
    # (a lone policy becomes a one-item array) and return it without enumeration.
    return , @($CollectedPolicies)
}

function Get-DlpScopeProperty {
    <#
    .SYNOPSIS
        Reads a named property from a Get-DlpCompliancePolicy object without
        throwing under Set-StrictMode when the property is absent.

    .DESCRIPTION
        StrictMode -Version Latest raises a PropertyNotFoundStrict error on any
        reference to a non-existent property. Get-DlpCompliancePolicy builds vary
        (a property such as EnforcementPlanes or Locations may be absent on older
        module versions), so scope fields are read through the PSObject property
        collection — indexing it by a missing name returns $null rather than
        throwing — and a genuinely absent property is reported as $null so the
        evaluator can fail closed on a missing scope signal without mistaking it
        for a collection failure.

    .OUTPUTS
        The property value, or $null when the object or property is absent.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [AllowNull()]
        [object]$InputObject,

        [Parameter(Mandatory)]
        [string]$Name
    )

    if ($null -eq $InputObject) { return $null }
    $property = $InputObject.PSObject.Properties[$Name]
    if ($null -eq $property) { return $null }
    return $property.Value
}

function ConvertTo-DlpStringArray {
    <#
    .SYNOPSIS
        Normalizes a Get-DlpCompliancePolicy MultiValuedProperty (e.g.
        EnforcementPlanes) into a stable array of non-empty strings.

    .DESCRIPTION
        EnforcementPlanes is a MultiValuedProperty that can surface as a single
        scalar string, an array, or $null. This helper re-establishes a stable
        string array (returned with the unary comma operator so PowerShell output
        enumeration does not flatten it) and drops null/blank entries. Absent or
        all-blank input collapses to $null so the evaluator treats the enforcement
        plane as simply missing (fail closed) rather than present-but-empty.

    .OUTPUTS
        System.String[] with at least one entry, or $null.
    #>
    [CmdletBinding()]
    param(
        [Parameter()]
        [AllowNull()]
        [object]$Value
    )

    if ($null -eq $Value) { return $null }

    $out = [System.Collections.Generic.List[string]]::new()
    foreach ($item in @($Value)) {
        if ($null -eq $item) { continue }
        $text = [string]$item
        if (-not [string]::IsNullOrWhiteSpace($text)) { $out.Add($text) }
    }

    if ($out.Count -eq 0) { return $null }
    return , $out.ToArray()
}

function ConvertTo-DlpLocationArray {
    <#
    .SYNOPSIS
        Normalizes a Get-DlpCompliancePolicy Locations value into a stable array
        of location objects for control 1.13.b Copilot-scope evaluation.

    .DESCRIPTION
        The DLP-for-Copilot binding is documented (Microsoft Learn
        New-DlpCompliancePolicy Example 4 / DLP for Microsoft 365 Copilot
        location; 1.13 powershell-setup.md §9) as a Locations array of
        { Workload = 'Applications'; Location = '<Copilot GUID>'; Inclusions = ... }
        objects. The -Locations input is a JSON *string*, and ConvertTo-Json can
        collapse a one-element array to a bare object, so this helper accepts an
        object array, a singleton object, or a JSON string that parses to either,
        and returns a stable array (unary comma so output enumeration does not
        flatten it). The location objects are preserved verbatim — the evaluator,
        not the collector, decides scope from the structural Location identity, so
        Inclusions/Exclusions decoys cannot create a false positive here. A
        malformed / empty / unparseable value collapses to $null (fail closed).

    .OUTPUTS
        System.Object[] with at least one entry, or $null.
    #>
    [CmdletBinding()]
    param(
        [Parameter()]
        [AllowNull()]
        [object]$Value
    )

    if ($null -eq $Value) { return $null }

    if ($Value -is [string]) {
        $text = $Value.Trim()
        if ([string]::IsNullOrWhiteSpace($text)) { return $null }
        try { $Value = $text | ConvertFrom-Json -ErrorAction Stop }
        catch { return $null }
    }

    if ($null -eq $Value) { return $null }
    $items = @($Value)
    if ($items.Count -eq 0) { return $null }
    return , $items
}

function Resolve-DlpPolicyScope {
    <#
    .SYNOPSIS
        Extracts the DLP-for-Copilot scope evidence (Workload, EnforcementPlanes,
        Locations) from a Get-DlpCompliancePolicy object into the purview.json
        contract consumed by control 1.13.b (_eval_dlp_references_sits /
        _policy_is_copilot_scoped).

    .DESCRIPTION
        Control 1.13.b must credit a policy only when it binds the Microsoft 365
        Copilot scope, evidenced structurally by three documented signals
        (Microsoft Learn New-DlpCompliancePolicy Example 4 / DLP for Microsoft 365
        Copilot location; 1.13 powershell-setup.md §9):

          * Workload = Applications
          * a Locations entry whose Location is the Copilot location GUID
            470f2276-e011-4e9d-a6ec-20768be3a4b0
          * EnforcementPlanes = CopilotExperiences

        An ordinary Exchange/SharePoint SIT policy therefore never qualifies, and
        scope is never inferred from the policy name or any unrelated string. The
        fields are preserved verbatim (only shape-normalized) so the evaluator
        makes the scope decision. Properties are read defensively so a build that
        omits a scope property yields $null (fail closed) instead of failing the
        whole collection under StrictMode.

    .OUTPUTS
        A PSCustomObject with Workload, EnforcementPlanes and Locations.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [AllowNull()]
        [object]$Policy
    )

    if ($null -eq $Policy) {
        return [PSCustomObject]@{
            Workload          = $null
            EnforcementPlanes = $null
            Locations         = $null
        }
    }

    [PSCustomObject]@{
        Workload          = (Get-DlpScopeProperty -InputObject $Policy -Name 'Workload')
        EnforcementPlanes = (ConvertTo-DlpStringArray -Value (Get-DlpScopeProperty -InputObject $Policy -Name 'EnforcementPlanes'))
        Locations         = (ConvertTo-DlpLocationArray -Value (Get-DlpScopeProperty -InputObject $Policy -Name 'Locations'))
    }
}
