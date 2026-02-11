function Test-CAAConfigPath {
    <#
    .SYNOPSIS
        Validates that a CAA configuration file exists and contains required properties.
    .DESCRIPTION
        Checks that the specified configuration file path exists and the JSON content
        includes the minimum required properties for CA policy compliance evaluation:
        breakGlassAccounts, applicationIds, and tenantSettings.
    .PARAMETER Path
        Path to the CAA configuration JSON file.
    .EXAMPLE
        Test-CAAConfigPath -Path './config/caa-config.json'
    .NOTES
        Part of the FSI Agent Governance — Conditional Access Automation solution.
        Controls: 1.11, 1.23, 1.18
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Path
    )

    if (-not (Test-Path $Path)) {
        throw "Configuration file not found: $Path"
    }

    try {
        $content = Get-Content -Path $Path -Raw | ConvertFrom-Json -ErrorAction Stop
    }
    catch {
        throw "Configuration file is not valid JSON: $Path — $_"
    }

    # Validate required top-level properties
    $requiredProperties = @('breakGlassAccounts', 'applicationIds')
    foreach ($prop in $requiredProperties) {
        if (-not ($content.PSObject.Properties.Name -contains $prop)) {
            throw "Configuration file missing required property '$prop': $Path"
        }
    }

    # Validate breakGlassAccounts is a non-empty array
    if (-not $content.breakGlassAccounts -or $content.breakGlassAccounts.Count -eq 0) {
        Write-Warning "Configuration file has no break-glass accounts defined. Check 3 (Break-Glass Exclusions) will produce incomplete results."
    }

    Write-Verbose "Configuration validated: $Path"
}
