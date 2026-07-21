#Requires -Modules Pester

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Describe 'Get-PurviewCopilotDlpClassification' {
    BeforeAll {
        . "$PSScriptRoot\PurviewDspmSupport.ps1"
        $copilotLocation = '470f2276-e011-4e9d-a6ec-20768be3a4b0'
    }

    It 'qualifies an active official-shape Microsoft 365 Copilot DLP policy' {
        $policy = [PSCustomObject]@{
            Name              = 'M365 Copilot DLP'
            Enabled           = $true
            Mode              = 'Enable'
            Workload          = 'Applications'
            Locations         = @($copilotLocation)
            EnforcementPlanes = @('CopilotExperiences')
        }

        $result = Get-PurviewCopilotDlpClassification -Policy $policy

        $result.Qualifies | Should -BeTrue
        $result.ActiveEnforcement | Should -BeTrue
        $result.WorkloadMatched | Should -BeTrue
        $result.LocationMatched | Should -BeTrue
        $result.EnforcementPlaneMatched | Should -BeTrue
    }

    It 'normalizes dictionary and PSCustomObject field values' {
        $policy = @{
            Name              = 'Object-shaped signals'
            Enabled           = $true
            Mode              = 'Enforce'
            Workload          = @([PSCustomObject]@{ Value = 'Applications' })
            Locations         = @([PSCustomObject]@{ Name = 'Microsoft 365 Copilot'; Id = $copilotLocation })
            EnforcementPlanes = @(@{ Value = 'CopilotExperiences' })
        }

        (Get-PurviewCopilotDlpClassification -Policy $policy).Qualifies | Should -BeTrue
    }

    It 'normalizes serialized JSON and delimited string field values' {
        $policy = @{
            Name              = 'Serialized signals'
            Enabled           = 'true'
            Mode              = 'Enable'
            Workload          = '["Exchange","Applications"]'
            Locations         = "[{`"Name`":`"Microsoft 365 Copilot`",`"Id`":`"$copilotLocation`"}]"
            EnforcementPlanes = 'EndpointDlp;CopilotExperiences'
        }

        (Get-PurviewCopilotDlpClassification -Policy $policy).Qualifies | Should -BeTrue
    }

    It 'accepts the singular Location field' {
        $policy = @{
            Name              = 'Singular location'
            Enabled           = $true
            Mode              = 'Enable'
            Workload          = 'Applications'
            Location          = $copilotLocation
            EnforcementPlanes = 'CopilotExperiences'
        }

        (Get-PurviewCopilotDlpClassification -Policy $policy).Qualifies | Should -BeTrue
    }

    It 'keeps test and audit modes diagnostic but non-qualifying' -ForEach @(
        @{ Mode = 'TestWithNotifications' }
        @{ Mode = 'TestWithoutNotifications' }
        @{ Mode = 'Audit' }
    ) {
        $policy = @{
            Name              = "Non-enforcing $Mode"
            Enabled           = $true
            Mode              = $Mode
            Workload          = 'Applications'
            Locations         = @($copilotLocation)
            EnforcementPlanes = @('CopilotExperiences')
        }

        $result = Get-PurviewCopilotDlpClassification -Policy $policy

        $result.Qualifies | Should -BeFalse
        $result.ActiveEnforcement | Should -BeFalse
        $result.Diagnostic | Should -Match 'not proven actively enforced'
    }

    It 'rejects a disabled policy even when all scope signals match' {
        $policy = @{
            Name              = 'Disabled'
            Enabled           = $false
            Mode              = 'Enable'
            Workload          = 'Applications'
            Locations         = @($copilotLocation)
            EnforcementPlanes = @('CopilotExperiences')
        }

        (Get-PurviewCopilotDlpClassification -Policy $policy).Qualifies | Should -BeFalse
    }

    It 'rejects a malformed location' {
        $policy = @{
            Name              = 'Malformed location'
            Enabled           = $true
            Mode              = 'Enable'
            Workload          = 'Applications'
            Locations         = '["not-the-copilot-guid"'
            EnforcementPlanes = @('CopilotExperiences')
        }

        $result = Get-PurviewCopilotDlpClassification -Policy $policy

        $result.Qualifies | Should -BeFalse
        $result.LocationMatched | Should -BeFalse
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
            Mode              = 'Enable'
            Workload          = 'Applications'
            Locations         = @($copilotLocation)
            EnforcementPlanes = @('CopilotExperiences')
        }
    }

    It 'counts only qualifying actively enforced policies' {
        $testPolicy = $activePolicy.Clone()
        $testPolicy.Name = 'Test Copilot DLP'
        $testPolicy.Mode = 'TestWithNotifications'

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
