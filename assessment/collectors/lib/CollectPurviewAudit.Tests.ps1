#Requires -Modules Pester

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Describe 'Purview collector audit session provenance (offline)' {
    BeforeAll {
        $script:collector = Join-Path $PSScriptRoot '..\Collect-Purview.ps1'
        $script:tenant = '11111111-1111-1111-1111-111111111111'

        # Define every external command locally so no installed module or tenant
        # session can be used, even when a mock is not configured.
        function Connect-IPPSSession { [CmdletBinding()] param($AppId, $Organization) }
        function Connect-ExchangeOnline { [CmdletBinding()] param($Prefix, $CommandName) }
        function Get-ConnectionInformation { [CmdletBinding()] param() }
        function Get-AdminAuditLogConfig { [CmdletBinding()] param() }
        function Get-FsiAuditAdminAuditLogConfig { [CmdletBinding()] param() }
        function Get-AuditConfigurationPolicy { [CmdletBinding()] param() }
        function Get-DlpCompliancePolicy { [CmdletBinding()] param() }
        function Get-DlpComplianceRule { [CmdletBinding()] param($Policy) }
        function Get-RetentionCompliancePolicy { [CmdletBinding()] param() }
        function Get-SupervisoryReviewPolicyV2 { [CmdletBinding()] param() }
        function Get-ComplianceCase { [CmdletBinding()] param() }
        function Get-LabelPolicy { [CmdletBinding()] param() }
        function Get-DlpSensitiveInformationType { [CmdletBinding()] param() }

        function Invoke-OfflinePurviewCollector {
            param([switch]$WhatIf, [string]$AuthMode = 'Interactive')
            $outputDir = Join-Path $TestDrive ([guid]::NewGuid().ToString('N'))
            & $script:collector -TenantId $script:tenant -AuthMode $AuthMode `
                -ClientId '22222222-2222-2222-2222-222222222222' `
                -OutputDir $outputDir -WhatIf:$WhatIf -WarningAction SilentlyContinue
            $script:collectorExitCode = $LASTEXITCODE
            $script:outputFile = Join-Path $outputDir 'collected\purview.json'
            if (-not $WhatIf) {
                Get-Content $script:outputFile -Raw | ConvertFrom-Json
            }
        }
    }

    BeforeEach {
        $fixture = @{
            Connected = $false
            AuditValue = $false
            Connection = [PSCustomObject]@{
                ConnectionId = '33333333-3333-3333-3333-333333333333'
                ModulePrefix = 'FsiAudit'
                State = 'Connected'
                TokenStatus = 'Active'
                IsEopSession = $false
                TenantID = $script:tenant
                CertificateAuthentication = $true
                AppId = '22222222-2222-2222-2222-222222222222'
            }
        }
        Mock Import-Module {}
        Mock Connect-IPPSSession {}
        Mock Connect-ExchangeOnline { $fixture.Connected = $true }
        Mock Get-ConnectionInformation { if ($fixture.Connected) { $fixture.Connection } }
        Mock Get-AdminAuditLogConfig {
            [PSCustomObject]@{ UnifiedAuditLogIngestionEnabled = $false; AdminAuditLogAgeLimit = '90.00:00:00' }
        }
        Mock Get-FsiAuditAdminAuditLogConfig {
            [PSCustomObject]@{ UnifiedAuditLogIngestionEnabled = $fixture.AuditValue; AdminAuditLogAgeLimit = '90.00:00:00' }
        }
        Mock Get-DlpCompliancePolicy {
            [PSCustomObject]@{ Name = 'Offline endpoint policy'; Mode = 'Enable'; Enabled = $true; Workload = 'Endpoint' }
        }
        Mock Get-RetentionCompliancePolicy {
            [PSCustomObject]@{
                Name = 'Offline retention'; Enabled = $true; Mode = 'Enable'
                Workload = 'Exchange'; RetentionDuration = 180; RetentionAction = 'Keep'
            }
        }
        Mock Get-SupervisoryReviewPolicyV2 {
            [PSCustomObject]@{ Name = 'Offline review'; RevieweeScope = 'All'; Enabled = $true }
        }
        Mock Get-ComplianceCase {
            [PSCustomObject]@{ Name = 'Offline case'; Description = ''; Status = 'Active'; CaseType = 'eDiscovery'; CreatedDateTime = '2026-01-01' }
        }
        Mock Get-LabelPolicy {
            [PSCustomObject]@{ Name = 'Offline labels'; Enabled = $true; Mode = 'Enable'; Labels = @(); ExchangeLocation = 'All'; Comment = '' }
        }
        Mock Get-DlpSensitiveInformationType {
            [PSCustomObject]@{ Name = 'Offline SIT'; Id = 'offline'; Publisher = 'Microsoft Corporation'; RulePackId = 'offline' }
        }
    }

    It 'collects <Value> only from verified Exchange context' -ForEach @(
        @{ Value = $true }, @{ Value = $false }
    ) {
        $fixture.AuditValue = $Value
        $result = Invoke-OfflinePurviewCollector
        $result.auditConfig.UnifiedAuditLogIngestionEnabled | Should -Be $Value
        $result.auditConfig.CollectionContext.Source | Should -Be 'ExchangeOnline'
        $result.auditConfig.CollectionContext.Verified | Should -BeTrue
        $result.auditConfig.CollectionContext.ConnectionId | Should -Be $fixture.Connection.ConnectionId
        $result.auditConfig.CollectionContext.TenantId | Should -Be $script:tenant
        $result.auditConfig.AdminAuditLogAgeLimit | Should -Be '90.00:00:00'
        $result.insiderRiskEvidence.auditDependency.status | Should -Be 'collected'
        $result.insiderRiskEvidence.auditDependency.unifiedAuditDependencyMet | Should -Be $Value
        if ($Value) {
            $result.insiderRiskEvidence.auditDependency.classification | Should -BeNullOrEmpty
        }
        else {
            $result.insiderRiskEvidence.auditDependency.classification | Should -Be 'audit_dependency_not_met'
        }
        $result.insiderRiskEvidence.policyInventory.status | Should -Be 'manual_required'
        $result.insiderRiskPolicies.Count | Should -Be 0
        $script:collectorExitCode | Should -Be 0
        Should -Invoke Connect-ExchangeOnline -Times 1 -Exactly -ParameterFilter {
            $Prefix -eq 'FsiAudit' -and $CommandName -eq 'Get-AdminAuditLogConfig'
        }
        Should -Invoke Get-FsiAuditAdminAuditLogConfig -Times 1 -Exactly
        Should -Invoke Get-AdminAuditLogConfig -Times 0 -Exactly
    }

    It 'rejects <Field>=<ContextValue> even when the returned audit value is <Value>' -ForEach @(
        @{ Field = 'IsEopSession'; ContextValue = $true; Value = $false }
        @{ Field = 'IsEopSession'; ContextValue = $true; Value = $true }
        @{ Field = 'IsEopSession'; ContextValue = 'false'; Value = $false }
        @{ Field = 'State'; ContextValue = 'Disconnected'; Value = $false }
        @{ Field = 'TokenStatus'; ContextValue = 'Expired'; Value = $false }
        @{ Field = 'TenantID'; ContextValue = '99999999-9999-9999-9999-999999999999'; Value = $false }
        @{ Field = 'ConnectionId'; ContextValue = ''; Value = $false }
        @{ Field = 'ModulePrefix'; ContextValue = 'IPPS'; Value = $false }
    ) {
        $fixture.Connection.$Field = $ContextValue
        $fixture.AuditValue = $Value
        $result = Invoke-OfflinePurviewCollector
        $result.auditConfig | Should -BeNullOrEmpty
        $result.insiderRiskEvidence.auditDependency.status | Should -Be 'unknown'
        $result.insiderRiskEvidence.auditDependency.unifiedAuditDependencyMet | Should -Be $null
        $result.insiderRiskEvidence.auditDependency.classification | Should -Be 'unknown'
        $result._metadata.warnings -join ' ' | Should -Match 'Section 1'
        $script:collectorExitCode | Should -Be 1
        Should -Invoke Get-FsiAuditAdminAuditLogConfig -Times 0 -Exactly
        Should -Invoke Get-AdminAuditLogConfig -Times 0 -Exactly
    }

    It 'does not observe disabled with <Failure> context or collection failure' -ForEach @(
        @{ Failure = 'missing-context' }
        @{ Failure = 'missing-context-field' }
        @{ Failure = 'ambiguous-context' }
        @{ Failure = 'context-unavailable' }
        @{ Failure = 'connection-failure' }
        @{ Failure = 'read-failure' }
        @{ Failure = 'missing-result' }
        @{ Failure = 'missing-flag' }
        @{ Failure = 'non-boolean-flag' }
        @{ Failure = 'changed-context' }
    ) {
        switch ($Failure) {
            'missing-context' { Mock Get-ConnectionInformation {} }
            'missing-context-field' { $fixture.Connection.PSObject.Properties.Remove('IsEopSession') }
            'ambiguous-context' { Mock Get-ConnectionInformation { $fixture.Connection; $fixture.Connection } }
            'context-unavailable' { Mock Get-ConnectionInformation { throw 'Connection metadata unavailable' } }
            'connection-failure' { Mock Connect-ExchangeOnline { throw 'Exchange connection failed' } }
            'read-failure' { Mock Get-FsiAuditAdminAuditLogConfig { throw 'Audit read permission denied' } }
            'missing-result' { Mock Get-FsiAuditAdminAuditLogConfig {} }
            'missing-flag' { Mock Get-FsiAuditAdminAuditLogConfig { [PSCustomObject]@{ AdminAuditLogAgeLimit = '90.00:00:00' } } }
            'non-boolean-flag' { $fixture.AuditValue = 'False' }
            'changed-context' {
                Mock Get-FsiAuditAdminAuditLogConfig {
                    $fixture.Connection = $fixture.Connection | Select-Object *
                    $fixture.Connection.ConnectionId = '44444444-4444-4444-4444-444444444444'
                    [PSCustomObject]@{ UnifiedAuditLogIngestionEnabled = $false; AdminAuditLogAgeLimit = '90.00:00:00' }
                }
            }
        }
        $result = Invoke-OfflinePurviewCollector
        $result.auditConfig | Should -BeNullOrEmpty
        $result.insiderRiskEvidence.auditDependency.status | Should -Be 'unknown'
        $result.insiderRiskEvidence.auditDependency.unifiedAuditDependencyMet | Should -Be $null
        $result.insiderRiskEvidence.policyInventory.status | Should -Be 'manual_required'
        $result._metadata.warnings -join ' ' | Should -Match 'Section 1'
        $script:collectorExitCode | Should -Be 1
        Should -Invoke Get-AdminAuditLogConfig -Times 0 -Exactly
    }

    It 'reuses a verified prefixed app-only connection without interactive authentication' {
        $fixture.Connected = $true
        $result = Invoke-OfflinePurviewCollector -AuthMode ServicePrincipal
        $result.auditConfig.UnifiedAuditLogIngestionEnabled | Should -BeFalse
        $result.insiderRiskEvidence.auditDependency.classification | Should -Be 'audit_dependency_not_met'
        Should -Invoke Connect-ExchangeOnline -Times 0 -Exactly
    }

    It 'requires ExchangeOnlineManagement 3.0.0 or later for connection provenance' {
        Invoke-OfflinePurviewCollector | Out-Null
        Should -Invoke Import-Module -Times 1 -Exactly -ParameterFilter {
            $Name -eq 'ExchangeOnlineManagement' -and $MinimumVersion -eq [version]'3.0.0'
        }
    }

    It 'rejects app-only <Failure> before reading audit evidence' -ForEach @(
        @{ Failure = 'interactive-auth' }
        @{ Failure = 'missing-auth-field' }
        @{ Failure = 'non-boolean-auth' }
        @{ Failure = 'different-app' }
        @{ Failure = 'missing-app-field' }
        @{ Failure = 'empty-app' }
    ) {
        $fixture.Connected = $true
        switch ($Failure) {
            'interactive-auth' { $fixture.Connection.CertificateAuthentication = $false }
            'missing-auth-field' { $fixture.Connection.PSObject.Properties.Remove('CertificateAuthentication') }
            'non-boolean-auth' { $fixture.Connection.CertificateAuthentication = 'true' }
            'different-app' { $fixture.Connection.AppId = '55555555-5555-5555-5555-555555555555' }
            'missing-app-field' { $fixture.Connection.PSObject.Properties.Remove('AppId') }
            'empty-app' { $fixture.Connection.AppId = '' }
        }
        $result = Invoke-OfflinePurviewCollector -AuthMode ServicePrincipal
        $result.auditConfig | Should -BeNullOrEmpty
        $result.insiderRiskEvidence.auditDependency.status | Should -Be 'unknown'
        $script:collectorExitCode | Should -Be 1
        Should -Invoke Get-FsiAuditAdminAuditLogConfig -Times 0 -Exactly
        Should -Invoke Connect-ExchangeOnline -Times 0 -Exactly
    }

    It 'rejects changed app-only <Field> after reading audit evidence' -ForEach @(
        @{ Field = 'AppId'; ChangedValue = '55555555-5555-5555-5555-555555555555' }
        @{ Field = 'CertificateAuthentication'; ChangedValue = $false }
    ) {
        $fixture.Connected = $true
        $fixture.ChangeField = $Field
        $fixture.ChangedValue = $ChangedValue
        Mock Get-FsiAuditAdminAuditLogConfig {
            $fixture.Connection.($fixture.ChangeField) = $fixture.ChangedValue
            [PSCustomObject]@{ UnifiedAuditLogIngestionEnabled = $false; AdminAuditLogAgeLimit = '90.00:00:00' }
        }
        $result = Invoke-OfflinePurviewCollector -AuthMode ServicePrincipal
        $result.auditConfig | Should -BeNullOrEmpty
        $result.insiderRiskEvidence.auditDependency.status | Should -Be 'unknown'
        $script:collectorExitCode | Should -Be 1
        Should -Invoke Get-FsiAuditAdminAuditLogConfig -Times 1 -Exactly
        Should -Invoke Connect-ExchangeOnline -Times 0 -Exactly
    }

    It 'reports missing app-only Exchange context as unknown without prompting' {
        $result = Invoke-OfflinePurviewCollector -AuthMode ServicePrincipal
        $result.auditConfig | Should -BeNullOrEmpty
        $result.insiderRiskEvidence.auditDependency.status | Should -Be 'unknown'
        $result._metadata.warnings -join ' ' | Should -Match 'pre-established Exchange Online'
        Should -Invoke Connect-ExchangeOnline -Times 0 -Exactly
        Should -Invoke Get-FsiAuditAdminAuditLogConfig -Times 0 -Exactly
    }

    It 'does not connect or read tenant configuration with WhatIf' {
        Invoke-OfflinePurviewCollector -WhatIf
        Test-Path $script:outputFile | Should -BeFalse
        Should -Invoke Connect-ExchangeOnline -Times 0 -Exactly
        Should -Invoke Connect-IPPSSession -Times 0 -Exactly
        Should -Invoke Get-FsiAuditAdminAuditLogConfig -Times 0 -Exactly
        Should -Invoke Get-AdminAuditLogConfig -Times 0 -Exactly
    }
}
