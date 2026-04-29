@{
    # PSScriptAnalyzer settings for FSI-AgentGov
    # Conservative ruleset focused on real bugs and security issues.
    # See: https://github.com/PowerShell/PSScriptAnalyzer

    Severity = @('Error', 'Warning')

    # Exclude noisy rules where the project's existing style is intentional.
    ExcludeRules = @(
        'PSAvoidUsingWriteHost',           # Collectors print human-readable progress to host.
        'PSUseShouldProcessForStateChangingFunctions',  # Collectors are read-only by design.
        'PSAvoidUsingPositionalParameters'
    )

    # Always include these even at lower severities — they catch real issues.
    IncludeRules = @(
        'PSAvoidUsingPlainTextForPassword',
        'PSAvoidUsingConvertToSecureStringWithPlainText',
        'PSAvoidUsingInvokeExpression',
        'PSUsePSCredentialType',
        'PSAvoidUsingUsernameAndPasswordParams',
        'PSAvoidGlobalVars'
    )
}
