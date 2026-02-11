function Get-CAAZoneClassification {
    <#
    .SYNOPSIS
        Determines the governance zone (1, 2, or 3) from a CA policy display name.
    .DESCRIPTION
        Parses the FSI-Z{n} prefix convention used by the governance framework to
        classify Conditional Access policies into zones. Supports both the canonical
        FSI-Z{n} naming and the legacy CA-*-Zone{n} pattern for backward compatibility.
    .PARAMETER DisplayName
        The display name of the Conditional Access policy.
    .OUTPUTS
        [int] Zone number (1, 2, or 3). Returns 0 if zone cannot be determined.
    .EXAMPLE
        Get-CAAZoneClassification -DisplayName 'FSI-Z3-EnterpriseAgentAdmin-Maximum'
        # Returns: 3
    .EXAMPLE
        Get-CAAZoneClassification -DisplayName 'FSI-AllZones-BlockLegacyAuth'
        # Returns: 3
    .NOTES
        Part of the FSI Agent Governance — Conditional Access Automation solution.
        Controls: 1.11, 1.23, 1.18
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory, ValueFromPipeline)]
        [string]$DisplayName
    )

    process {
        # FSI-Z{n} prefix convention (canonical)
        if ($DisplayName -match '^FSI-Z(\d)') {
            return [int]$Matches[1]
        }
        # FSI-AllZones convention — defaults to highest zone for severity escalation
        if ($DisplayName -match 'AllZones') {
            return 3
        }
        # Legacy CA-*-Zone{n} pattern (backward compatibility)
        if ($DisplayName -match 'Zone(\d)') {
            return [int]$Matches[1]
        }
        # Zone cannot be determined
        return 0
    }
}
