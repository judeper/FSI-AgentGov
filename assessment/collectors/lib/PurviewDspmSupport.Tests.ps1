#Requires -Modules Pester

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Describe 'Get-PurviewCopilotDlpClassification' {
    BeforeAll {
        . "$PSScriptRoot\PurviewDspmSupport.ps1"
        $copilotLocation = '470f2276-e011-4e9d-a6ec-20768be3a4b0'
    }

    It 'qualifies the documented nested Locations JSON without top-level Workload' {
        $policy = [PSCustomObject]@{
            Name              = 'M365 Copilot DLP'
            Enabled           = $true
            Mode              = 'Enforce'
            Locations         = "{`"Location`":`"$copilotLocation`",`"Workload`":`"Applications`"}"
            EnforcementPlanes = @('CopilotExperiences')
        }

        $result = Get-PurviewCopilotDlpClassification -Policy $policy

        $result.Qualifies | Should -BeTrue
        $result.ActiveEnforcement | Should -BeTrue
        $result.WorkloadMatched | Should -BeTrue
        $result.LocationMatched | Should -BeTrue
        $result.EnforcementPlaneMatched | Should -BeTrue
    }

    It 'qualifies the documented Enable mode when the policy is enabled' {
        $policy = [PSCustomObject]@{
            Name              = 'Enabled M365 Copilot DLP'
            Enabled           = $true
            Mode              = 'Enable'
            Locations         = "{`"Location`":`"$copilotLocation`",`"Workload`":`"Applications`"}"
            EnforcementPlanes = @('CopilotExperiences')
        }

        $result = Get-PurviewCopilotDlpClassification -Policy $policy

        $result.Qualifies | Should -BeTrue
        $result.ActiveEnforcement | Should -BeTrue
    }

    It 'supports dictionary and PSCustomObject location scope entries' {
        $policy = @{
            Name              = 'Object-shaped signals'
            Enabled           = $true
            Mode              = 'Enforce'
            Locations         = @(
                [PSCustomObject]@{ Workload = 'Exchange'; Location = 'exchange-location' }
                @{ Workload = 'Applications'; Location = $copilotLocation }
            )
            EnforcementPlanes = @(@{ Value = 'CopilotExperiences' })
        }

        (Get-PurviewCopilotDlpClassification -Policy $policy).Qualifies | Should -BeTrue
    }

    It 'supports serialized JSON arrays of location scope entries' {
        $policy = @{
            Name              = 'Serialized signals'
            Enabled           = 'true'
            Mode              = 'Enforce'
            Locations         = "[{`"Workload`":`"Applications`",`"Location`":`"$copilotLocation`"}]"
            EnforcementPlanes = 'EndpointDlp;CopilotExperiences'
        }

        (Get-PurviewCopilotDlpClassification -Policy $policy).Qualifies | Should -BeTrue
    }

    It 'accepts the existing top-level Workload and Location representation' {
        $policy = @{
            Name              = 'Singular location'
            Enabled           = $true
            Mode              = 'Enforce'
            Workload          = 'Applications'
            Location          = $copilotLocation
            EnforcementPlanes = 'CopilotExperiences'
        }

        (Get-PurviewCopilotDlpClassification -Policy $policy).Qualifies | Should -BeTrue
    }

    It 'keeps documented non-enforcing modes diagnostic but non-qualifying' -ForEach @(
        @{ Mode = 'Test' }
        @{ Mode = 'AuditAndNotify' }
        @{ Mode = 'Other' }
    ) {
        $policy = @{
            Name              = "Non-enforcing $Mode"
            Enabled           = $true
            Mode              = $Mode
            Locations         = @{ Workload = 'Applications'; Location = $copilotLocation }
            EnforcementPlanes = @('CopilotExperiences')
        }

        $result = Get-PurviewCopilotDlpClassification -Policy $policy

        $result.Qualifies | Should -BeFalse
        $result.ActiveEnforcement | Should -BeFalse
        $result.Diagnostic | Should -Match 'not proven actively enforced'
    }

    It 'rejects a disabled policy in either accepted active mode' -ForEach @(
        @{ Mode = 'Enable' }
        @{ Mode = 'Enforce' }
    ) {
        $policy = @{
            Name              = "Disabled $Mode"
            Enabled           = $false
            Mode              = $Mode
            Locations         = @{ Workload = 'Applications'; Location = $copilotLocation }
            EnforcementPlanes = @('CopilotExperiences')
        }

        (Get-PurviewCopilotDlpClassification -Policy $policy).Qualifies | Should -BeFalse
    }

    It 'rejects a missing mode even when all other signals match' {
        $policy = @{
            Name              = 'Missing mode'
            Enabled           = $true
            Locations         = @{ Workload = 'Applications'; Location = $copilotLocation }
            EnforcementPlanes = @('CopilotExperiences')
        }

        $result = Get-PurviewCopilotDlpClassification -Policy $policy

        $result.Qualifies | Should -BeFalse
        $result.ActiveEnforcement | Should -BeFalse
        $result.Diagnostic | Should -Match 'Mode must be Enable or Enforce'
    }

    It 'rejects a malformed location' {
        $policy = @{
            Name              = 'Malformed location'
            Enabled           = $true
            Mode              = 'Enforce'
            Workload          = 'Applications'
            Locations         = '["not-the-copilot-guid"'
            EnforcementPlanes = @('CopilotExperiences')
        }

        $result = Get-PurviewCopilotDlpClassification -Policy $policy

        $result.Qualifies | Should -BeFalse
        $result.LocationMatched | Should -BeFalse
    }

    It 'inherits top-level Workload only for entries that omit Workload' {
        $policy = @{
            Name              = 'Inherited workload'
            Enabled           = $true
            Mode              = 'Enforce'
            Workload          = 'Applications'
            Locations         = @(
                @{ Location = $copilotLocation }
                @{ Workload = 'Exchange'; Location = 'exchange-location' }
            )
            EnforcementPlanes = @('CopilotExperiences')
        }

        (Get-PurviewCopilotDlpClassification -Policy $policy).Qualifies | Should -BeTrue
    }

    It 'does not mix workload and location signals from unrelated scopes' {
        $policy = @{
            Name              = 'Unrelated scopes'
            Enabled           = $true
            Mode              = 'Enforce'
            Workload          = 'Applications'
            Locations         = @(
                @{ Location = 'other-location' }
                @{ Workload = 'Exchange'; Location = $copilotLocation }
            )
            EnforcementPlanes = @('CopilotExperiences')
        }

        $result = Get-PurviewCopilotDlpClassification -Policy $policy

        $result.WorkloadMatched | Should -BeTrue
        $result.LocationMatched | Should -BeTrue
        $result.Qualifies | Should -BeFalse
        $result.Diagnostic | Should -Match 'same location scope'
    }

    It 'ignores the Copilot GUID in exclusions and unrelated nested properties' -ForEach @(
        @{
            Locations = @{
                Workload  = 'Applications'
                Location  = 'other-location'
                Exclusions = @(@{ Location = '470f2276-e011-4e9d-a6ec-20768be3a4b0' })
            }
        }
        @{
            Locations = @{
                Workload   = 'Applications'
                Diagnostics = @{ ObservedLocation = '470f2276-e011-4e9d-a6ec-20768be3a4b0' }
            }
        }
    ) {
        $policy = @{
            Name              = 'Nested false positive'
            Enabled           = $true
            Mode              = 'Enforce'
            Locations         = $Locations
            EnforcementPlanes = @('CopilotExperiences')
        }

        $result = Get-PurviewCopilotDlpClassification -Policy $policy

        $result.LocationMatched | Should -BeFalse
        $result.Qualifies | Should -BeFalse
    }

    It 'rejects missing required fields conservatively' {
        $result = Get-PurviewCopilotDlpClassification -Policy @{
            Name     = 'Missing fields'
            Workload = 'Applications'
        }

        $result.Qualifies | Should -BeFalse
        $result.ActiveEnforcement | Should -BeFalse
        $result.LocationMatched | Should -BeFalse
        $result.EnforcementPlaneMatched | Should -BeFalse
    }
}

Describe 'New-PurviewDspmEvidence' {
    BeforeAll {
        . "$PSScriptRoot\PurviewDspmSupport.ps1"
        $copilotLocation = '470f2276-e011-4e9d-a6ec-20768be3a4b0'
        $activePolicy = @{
            Name              = 'Active Copilot DLP'
            Enabled           = $true
            Mode              = 'Enforce'
            Locations         = @{ Workload = 'Applications'; Location = $copilotLocation }
            EnforcementPlanes = @('CopilotExperiences')
        }
    }

    It 'counts only qualifying actively enforced policies' {
        $testPolicy = $activePolicy.Clone()
        $testPolicy.Name = 'Test Copilot DLP'
        $testPolicy.Mode = 'Test'

        $evidence = New-PurviewDspmEvidence -Policies @($activePolicy, $testPolicy) -DlpCollectionSucceeded $true

        $evidence.Detected | Should -BeTrue
        $evidence.PolicyCount | Should -Be 1
        $evidence.DiagnosticPolicyCount | Should -Be 2
        $evidence.PolicyNames | Should -Contain 'Active Copilot DLP'
        $evidence.PolicyNames | Should -Not -Contain 'Test Copilot DLP'
    }

    It 'does not let retention-only evidence satisfy DSPM' {
        $evidence = New-PurviewDspmEvidence -Policies @() -DlpCollectionSucceeded $true `
            -RetentionCoverage $true -RetentionPolicyNames @('Copilot Retention')

        $evidence.CollectionStatus | Should -Be 'collected'
        $evidence.Detected | Should -BeFalse
        $evidence.PolicyCount | Should -Be 0
        $evidence.RetentionCoverage | Should -BeTrue
        $evidence.Note | Should -Match 'informational only'
    }

    It 'reports collection errors as unavailable rather than a negative result' {
        $evidence = New-PurviewDspmEvidence -Policies $null -DlpCollectionSucceeded $false

        $evidence.CollectionStatus | Should -Be 'failed'
        $evidence.Detected | Should -BeNullOrEmpty
        $evidence.PolicyCount | Should -Be 0
    }
}
