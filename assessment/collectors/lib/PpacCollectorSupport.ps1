Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

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
        contract ({ id, name, type }); a policy with no environments keeps a null
        Environments (All-scope). A collection *exception* never reaches this helper:
        the caller leaves $dlpPolicies = $null on failure so the scorer treats it as
        unknown, which is distinct from a successful empty [] collection.

        The property projection is byte-for-byte the same as the previous inline
        collector projection; only the $null-filtering and the guaranteed array
        return are new.

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
            [PSCustomObject]@{
                DisplayName          = $_.displayName
                PolicyName           = $_.name
                CreatedTime          = $_.createdTime
                IsEnabled            = $_.isEnabled
                BusinessDataGroup    = $_.connectorGroups | Where-Object { $_.classification -eq 'Confidential' } |
                    ForEach-Object { $_.connectors | Select-Object id, name }
                NonBusinessDataGroup = $_.connectorGroups | Where-Object { $_.classification -eq 'General' } |
                    ForEach-Object { $_.connectors | Select-Object id, name }
                BlockedGroup         = $_.connectorGroups | Where-Object { $_.classification -eq 'Blocked' } |
                    ForEach-Object { $_.connectors | Select-Object id, name }
                EnvironmentType      = $_.environmentType
                Environments         = if ($null -ne $_.environments) { , @($_.environments) } else { $null }
            }
        })

    return , $projected
}
