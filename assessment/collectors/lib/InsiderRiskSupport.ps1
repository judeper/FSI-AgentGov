Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-InsiderRiskFailureClassification {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$Message,
        [Parameter()][string]$CommandName = ''
    )

    $text = $Message.ToLowerInvariant()
    $category = 'unknown'
    $guidance = 'Collect portal evidence manually and escalate to Purview engineering support if required.'

    if (
        $text -match 'commandnotfoundexception' -or
        $text -match 'is not recognized as the name of a cmdlet' -or
        $text -match 'could not find command' -or
        $text -match 'cmdlet .+ not (present|found|available)'
    ) {
        $category = 'command_not_found'
        $guidance = 'Treat as unsupported automation surface. Do not map this to licensing. Collect Insider Risk policy evidence manually from the Purview portal.'
    }
    elseif (
        $text -match 'access is denied' -or
        $text -match 'unauthorized' -or
        $text -match 'forbidden' -or
        $text -match 'insufficient' -or
        $text -match 'not authorized' -or
        $text -match 'permission'
    ) {
        $category = 'auth_or_permission'
        $guidance = 'Validate IRM role-group assignment and Security & Compliance session permissions.'
    }
    elseif (
        $text -match 'license' -or
        $text -match 'licensing' -or
        $text -match 'service plan' -or
        $text -match 'subscription' -or
        $text -match 'sku' -or
        $text -match 'not enabled for your organization' -or
        $text -match 'feature is not available'
    ) {
        $category = 'licensing'
        $guidance = 'Validate Purview Insider Risk licensing and service-plan assignment.'
    }
    elseif ($text -match 'unsupported' -or $text -match 'not supported' -or $text -match 'preview') {
        $category = 'unsupported_surface'
        $guidance = 'Use only first-party documented GA surfaces. Collect policy inventory through manual portal export.'
    }

    [PSCustomObject]@{
        Category    = $category
        CommandName = $CommandName
        Message     = $Message
        Guidance    = $guidance
    }
}
