function Connect-CAAGraphSession {
    <#
    .SYNOPSIS
        Establishes a Microsoft Graph session with the required scopes for CAA policy evaluation.
    .DESCRIPTION
        Wraps Connect-MgGraph for interactive or delegated authentication scenarios.
        For service-principal / certificate authentication (runbook context), use the
        direct Connect-MgGraph call in Start-CAAValidationRunbook.ps1 instead.
    .PARAMETER TenantId
        Entra ID tenant GUID.
    .PARAMETER Scopes
        Graph permission scopes to request. Default: Policy.Read.All.
    .EXAMPLE
        Connect-CAAGraphSession -TenantId '00000000-0000-0000-0000-000000000000' -Scopes @('Policy.Read.All')
    .NOTES
        Part of the FSI Agent Governance — Conditional Access Automation solution.
        Controls: 1.11, 1.23, 1.18
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$TenantId,

        [Parameter()]
        [string[]]$Scopes = @('Policy.Read.All')
    )

    # Verify Microsoft.Graph.Authentication module is available
    if (-not (Get-Module -ListAvailable -Name 'Microsoft.Graph.Authentication')) {
        throw "Microsoft.Graph.Authentication module is not installed. Run: Install-Module Microsoft.Graph.Authentication -Scope CurrentUser"
    }

    Write-Verbose "Connecting to Microsoft Graph for tenant $TenantId with scopes: $($Scopes -join ', ')"
    Connect-MgGraph -TenantId $TenantId -Scopes $Scopes -NoWelcome -ErrorAction Stop

    # Validate connection
    $context = Get-MgContext
    if (-not $context) {
        throw "Failed to establish Microsoft Graph session for tenant $TenantId"
    }

    Write-Verbose "Graph session established. Connected as: $($context.Account)"
}
