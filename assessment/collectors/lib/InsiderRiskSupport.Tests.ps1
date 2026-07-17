#Requires -Modules Pester

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Describe 'Get-InsiderRiskFailureClassification' {
    BeforeAll {
        . "$PSScriptRoot\InsiderRiskSupport.ps1"
    }

    It 'classifies missing cmdlet as command_not_found (not licensing)' {
        $result = Get-InsiderRiskFailureClassification -Message 'Get-InsiderRiskPolicy is not recognized as the name of a cmdlet' -CommandName 'Get-InsiderRiskPolicy'
        $result.Category | Should -Be 'command_not_found'
        $result.Guidance | Should -Match 'Do not map this to licensing'
    }

    It 'classifies permission errors as auth_or_permission' {
        $result = Get-InsiderRiskFailureClassification -Message 'Access is denied. You are not authorized to perform this action.' -CommandName 'Get-IRMConfiguration'
        $result.Category | Should -Be 'auth_or_permission'
    }

    It 'classifies licensing errors as licensing' {
        $result = Get-InsiderRiskFailureClassification -Message 'This feature requires an eligible license or service plan.' -CommandName 'Get-IRMConfiguration'
        $result.Category | Should -Be 'licensing'
    }
}
