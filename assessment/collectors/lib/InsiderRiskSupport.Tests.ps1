#Requires -Modules Pester

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

BeforeAll {
    function New-VerifiedAuditConfig {
        param([object]$Value)
        @{
            UnifiedAuditLogIngestionEnabled = $Value
            CollectionContext = @{
                Source = 'ExchangeOnline'
                CommandName = 'Get-FsiAuditAdminAuditLogConfig'
                ModulePrefix = 'FsiAudit'
                ConnectionId = '33333333-3333-3333-3333-333333333333'
                TenantId = '11111111-1111-1111-1111-111111111111'
                Verified = $true
            }
        }
    }
}

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

    It 'classifies insufficient license phrases as licensing' {
        $result = Get-InsiderRiskFailureClassification -Message 'Insufficient license assignment for this operation.' -CommandName 'Get-IRMConfiguration'
        $result.Category | Should -Be 'licensing'
    }

    It 'keeps insufficient permission phrases in auth_or_permission' {
        $result = Get-InsiderRiskFailureClassification -Message 'Insufficient privileges to complete this action.' -CommandName 'Get-IRMConfiguration'
        $result.Category | Should -Be 'auth_or_permission'
    }

    It 'classifies unsupported-surface errors explicitly' {
        $result = Get-InsiderRiskFailureClassification -Message 'This operation is not supported for this API surface.' -CommandName 'Get-InsiderRiskPolicy'
        $result.Category | Should -Be 'unsupported_surface'
    }

    It 'falls back to unknown for unclassified errors' {
        $result = Get-InsiderRiskFailureClassification -Message 'Unhandled null reference in downstream parser.' -CommandName 'Get-InsiderRiskPolicy'
        $result.Category | Should -Be 'unknown'
    }
}

Describe 'Get-InsiderRiskUnifiedAuditDependencyState' {
    BeforeAll {
        . "$PSScriptRoot\InsiderRiskSupport.ps1"
    }

    It 'derives unifiedAuditDependencyMet=true from audit configuration' {
        $state = Get-InsiderRiskUnifiedAuditDependencyState -AuditConfig (New-VerifiedAuditConfig $true)
        $state.Status | Should -Be 'collected'
        $state.UnifiedAuditDependencyMet | Should -BeTrue
        $state.Classification | Should -BeNullOrEmpty
    }

    It 'derives unifiedAuditDependencyMet=false from audit configuration' {
        $state = Get-InsiderRiskUnifiedAuditDependencyState -AuditConfig (New-VerifiedAuditConfig $false)
        $state.Status | Should -Be 'collected'
        $state.UnifiedAuditDependencyMet | Should -BeFalse
        $state.Classification | Should -Be 'audit_dependency_not_met'
    }

    It 'emits unknown when section-1 audit configuration is unavailable' {
        $state = Get-InsiderRiskUnifiedAuditDependencyState -AuditConfig $null
        $state.Status | Should -Be 'unknown'
        $state.UnifiedAuditDependencyMet | Should -Be $null
        $state.Classification | Should -Be 'unknown'
    }

    It 'rejects a bare Boolean without session provenance' -ForEach @(
        @{ Value = $true }, @{ Value = $false }
    ) {
        $state = Get-InsiderRiskUnifiedAuditDependencyState -AuditConfig @{ UnifiedAuditLogIngestionEnabled = $Value }
        $state.Status | Should -Be 'unknown'
        $state.UnifiedAuditDependencyMet | Should -Be $null
        $state.Detail | Should -Match 'provenance'
    }

    It 'rejects invalid provenance <Field>=<Value>' -ForEach @(
        @{ Field = 'Source'; Value = 'SecurityCompliance' }
        @{ Field = 'CommandName'; Value = 'Get-AdminAuditLogConfig' }
        @{ Field = 'ModulePrefix'; Value = 'IPPS' }
        @{ Field = 'ConnectionId'; Value = '' }
        @{ Field = 'TenantId'; Value = '' }
        @{ Field = 'Verified'; Value = $false }
        @{ Field = 'Verified'; Value = 'true' }
    ) {
        $config = New-VerifiedAuditConfig $false
        $config.CollectionContext[$Field] = $Value
        $state = Get-InsiderRiskUnifiedAuditDependencyState -AuditConfig $config
        $state.Status | Should -Be 'unknown'
        $state.Classification | Should -Be 'unknown'
        $state.UnifiedAuditDependencyMet | Should -Be $null
    }

    It 'accepts serialized object provenance and Boolean strings' {
        $config = New-VerifiedAuditConfig 'false' | ConvertTo-Json | ConvertFrom-Json
        $state = Get-InsiderRiskUnifiedAuditDependencyState -AuditConfig $config
        $state.Status | Should -Be 'collected'
        $state.UnifiedAuditDependencyMet | Should -BeFalse
    }
}

Describe 'New-InsiderRiskEvidence' {
    BeforeAll {
        . "$PSScriptRoot\InsiderRiskSupport.ps1"
    }

    It 'emits manual-required policy inventory and audit-derived dependency state' {
        $evidence = New-InsiderRiskEvidence -AuditConfig (New-VerifiedAuditConfig $true)
        $evidence.policyInventory.status | Should -Be 'manual_required'
        $evidence.policyInventory.classification | Should -Be 'unsupported_surface'
        $evidence.auditDependency.unifiedAuditDependencyMet | Should -BeTrue
        $evidence.auditDependency.evidenceSource | Should -Match 'auditConfig\.UnifiedAuditLogIngestionEnabled'
    }
}
