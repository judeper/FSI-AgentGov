@{
    # Module manifest for FSI Agent Governance — Conditional Access Automation
    # Controls: 1.11, 1.23, 1.18

    RootModule        = $null
    ModuleVersion     = '1.2.0'
    GUID              = 'a1b2c3d4-5e6f-7a8b-9c0d-1e2f3a4b5c6d'
    Author            = 'FSI Agent Governance'
    CompanyName       = 'Microsoft'
    Copyright         = '(c) Microsoft. All rights reserved.'
    Description       = 'FSI Agent Governance — Conditional Access Automation for Controls 1.11, 1.23, 1.18. Deploys and validates CA policies with zone-specific requirements, drift detection, compliance reporting, and Dataverse persistence for audit trail and operational state.'
    PowerShellVersion = '7.0'
    CompatiblePSEditions = @('Core')

    RequiredModules   = @(
        @{ ModuleName = 'Microsoft.Graph.Identity.SignIns'; ModuleVersion = '2.0.0' }
        @{ ModuleName = 'Microsoft.Graph.Applications'; ModuleVersion = '2.0.0' }
    )

    NestedModules     = @(
        'private/CAAClient.psm1'
    )

    # Future module functions (not yet implemented):
    #   Deploy-CAPolicies, Register-ServicePrincipal,
    #   Export-PolicyBaseline, Watch-PolicyDrift
    # Test-PolicyCompliance.ps1 is a standalone script (not a module function).
    FunctionsToExport = @()

    CmdletsToExport   = @()
    VariablesToExport  = @()
    AliasesToExport    = @()

    PrivateData = @{
        PSData = @{
            Tags         = @('ConditionalAccess', 'Governance', 'FSI', 'MFA', 'ZeroTrust')
            ProjectUri   = 'https://github.com/microsoft/fsi-agent-gov'
            ReleaseNotes = 'v1.2.0: Added Start-CAAValidationRunbook.ps1 — Azure Automation runbook wrapper for daily CA policy compliance validation with certificate-based auth, Dataverse drift detection, and structured JSON output. Added Compare-PolicyBaseline.ps1 and Get-PolicyBaseline.ps1 private helpers.'
        }
    }
}
