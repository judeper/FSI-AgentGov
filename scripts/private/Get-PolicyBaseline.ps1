function Get-CAAPolicyBaseline {
    <#
    .SYNOPSIS
        Captures current CA policy state as baseline snapshots from Microsoft Graph.
    .DESCRIPTION
        Queries all Conditional Access policies via the Microsoft Graph API and returns
        structured policy snapshot objects suitable for baseline comparison and drift
        detection. Each snapshot includes state, conditions, grant controls, session
        controls, zone classification, and a configuration hash.
    .PARAMETER TenantId
        Entra ID tenant GUID.
    .PARAMETER ConfigPath
        Path to CAA configuration JSON file.
    .EXAMPLE
        $baseline = Get-CAAPolicyBaseline -TenantId $tenantId -ConfigPath .\config.json
    .OUTPUTS
        Array of PSCustomObject with PolicyId, PolicyName, State, Zone, Conditions,
        GrantControls, SessionControls, and ConfigHash properties.
    .NOTES
        Part of the FSI Agent Governance — Conditional Access Automation solution.
        Controls: 1.11, 1.23, 1.18
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$TenantId,

        [Parameter(Mandatory)]
        [string]$ConfigPath
    )

    $policies = Get-MgIdentityConditionalAccessPolicy -All
    $snapshots = @()

    foreach ($policy in $policies) {
        # Derive zone from display name convention
        $zone = 0
        if ($policy.DisplayName -match 'Zone3') { $zone = 3 }
        elseif ($policy.DisplayName -match 'Zone2') { $zone = 2 }
        elseif ($policy.DisplayName -match 'Zone1') { $zone = 1 }
        elseif ($policy.DisplayName -match 'AllZones') { $zone = 3 }

        # Build SHA-256 configuration hash for quick drift detection
        $configString = ($policy | ConvertTo-Json -Depth 20 -Compress)
        $hashBytes = [System.Security.Cryptography.SHA256]::Create().ComputeHash(
            [System.Text.Encoding]::UTF8.GetBytes($configString)
        )
        $configHash = [BitConverter]::ToString($hashBytes) -replace '-'

        $snapshots += [PSCustomObject]@{
            PolicyId        = $policy.Id
            PolicyName      = $policy.DisplayName
            State           = $policy.State
            Zone            = $zone
            Conditions      = $policy.Conditions
            GrantControls   = $policy.GrantControls
            SessionControls = $policy.SessionControls
            ConfigHash      = $configHash
        }
    }

    return $snapshots
}
