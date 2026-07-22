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
