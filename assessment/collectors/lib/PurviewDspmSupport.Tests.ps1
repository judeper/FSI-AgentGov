#Requires -Modules Pester

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Describe 'Get-PurviewCopilotDlpClassification' {
    BeforeAll {
        . "$PSScriptRoot\PurviewDspmSupport.ps1"
        $copilotLocation = '470f2276-e011-4e9d-a6ec-20768be3a4b0'

        function New-TestPurviewQualifyingRule {
            [PSCustomObject]@{
                Name                                = 'Block sensitive Copilot content'
                Priority                            = 0
                Disabled                            = $false
                BlockAccess                         = $true
                EnforcementPlanes                   = @('CopilotExperiences')
                ContentContainsSensitiveInformation = @(@{ Name = 'U.S. Social Security Number' })
                ContentContainsSensitivityLabel     = @()
            }
        }

        function New-TestPurviewAdvancedRule {
            param(
                [Parameter(Mandatory)]
                [ValidateSet(
                    'ContentContainsSensitiveInformation',
                    'ContentContainsSensitivityLabel'
                )]
                [string]$ConditionName
            )

            [PSCustomObject]@{
                Version   = '1.0'
                Condition = [PSCustomObject]@{
                    Operator      = 'And'
                    SubConditions = @(
                        [PSCustomObject]@{
                            ConditionName = $ConditionName
                            Operator      = 'Include'
                            Value         = @('criterion-id')
                        }
                    )
                }
            }
        }

        function Add-TestPurviewQualifyingRuleEvidence {
            param(
                [Parameter(Mandatory)]
                [object]$Policy
            )

            $rules = @(New-TestPurviewQualifyingRule)
            if ($Policy -is [System.Collections.IDictionary]) {
                $Policy['Rules'] = $rules
                $Policy['RuleCollectionSucceeded'] = $true
            }
            else {
                $Policy | Add-Member -NotePropertyName Rules -NotePropertyValue $rules -Force
                $Policy | Add-Member -NotePropertyName RuleCollectionSucceeded -NotePropertyValue $true -Force
            }
            return $Policy
        }
    }

    It 'qualifies Enforce compatibility with documented nested Locations JSON' {
        $policy = [PSCustomObject]@{
            Name              = 'M365 Copilot DLP'
            Enabled           = $true
            Mode              = 'Enforce'
            Locations         = "{`"Location`":`"$copilotLocation`",`"Workload`":`"Applications`"}"
            EnforcementPlanes = @('CopilotExperiences')
        }
        $policy = Add-TestPurviewQualifyingRuleEvidence -Policy $policy

        $result = Get-PurviewCopilotDlpClassification -Policy $policy

        $result.Qualifies | Should -BeTrue
        $result.ActiveEnforcement | Should -BeTrue
        $result.WorkloadMatched | Should -BeTrue
        $result.LocationMatched | Should -BeTrue
        $result.EnforcementPlaneMatched | Should -BeTrue
    }

    It 'qualifies the documented Enable mode when Enabled is absent' {
        $policy = [PSCustomObject]@{
            Name              = 'Enabled M365 Copilot DLP'
            Mode              = 'Enable'
            Locations         = "{`"Location`":`"$copilotLocation`",`"Workload`":`"Applications`"}"
            EnforcementPlanes = @('CopilotExperiences')
        }
        $policy = Add-TestPurviewQualifyingRuleEvidence -Policy $policy

        $result = Get-PurviewCopilotDlpClassification -Policy $policy

        $result.Qualifies | Should -BeTrue
        $result.ActiveEnforcement | Should -BeTrue
        $result.Enabled | Should -BeNullOrEmpty
        $result.QualifyingRuleCount | Should -Be 1
        $result.RuleDiagnostics[0].ContentContainsSensitiveInformation.Count | Should -Be 1
    }

    It 'qualifies the documented policy-level plane with RestrictAccess and AdvancedRule SIT evidence' {
        $policy = @{
            Name                    = 'Documented Copilot rule shape'
            Mode                    = 'Enable'
            Locations               = @{ Workload = 'Applications'; Location = $copilotLocation }
            EnforcementPlanes       = @('CopilotExperiences')
            RuleCollectionSucceeded = $true
            Rules                   = @(
                @{
                    Name              = 'Block sensitive Copilot processing'
                    Disabled          = $false
                    BlockAccess       = $null
                    RestrictAccess    = '[{"setting":"ExcludeContentProcessing","value":"Block"}]'
                    EnforcementPlanes = $null
                    AdvancedRule      = (
                        New-TestPurviewAdvancedRule `
                            -ConditionName 'ContentContainsSensitiveInformation' |
                            ConvertTo-Json -Depth 6 -Compress
                    )
                }
            )
        }

        $result = Get-PurviewCopilotDlpClassification -Policy $policy
        $ruleResult = $result.RuleDiagnostics[0]

        $result.Qualifies | Should -BeTrue
        $ruleResult.BlockAccess | Should -BeNullOrEmpty
        $ruleResult.RestrictAccessMatched | Should -BeTrue
        $ruleResult.BlockingMatched | Should -BeTrue
        $ruleResult.EnforcementPlaneSpecified | Should -BeFalse
        $ruleResult.EnforcementPlaneMatched | Should -BeTrue
        $ruleResult.AdvancedRuleSensitiveInformationMatched | Should -BeTrue
    }

    It 'qualifies an AdvancedRule sensitivity-label criterion' {
        $policy = @{
            Name                    = 'AdvancedRule label policy'
            Mode                    = 'Enable'
            Locations               = @{ Workload = 'Applications'; Location = $copilotLocation }
            EnforcementPlanes       = @('CopilotExperiences')
            RuleCollectionSucceeded = $true
            Rules                   = @(
                @{
                    Name           = 'Block labeled Copilot processing'
                    Disabled       = $false
                    RestrictAccess = [PSCustomObject]@{ ExcludeContentProcessing = 'Block' }
                    AdvancedRule   = New-TestPurviewAdvancedRule `
                        -ConditionName 'ContentContainsSensitivityLabel'
                }
            )
        }

        $result = Get-PurviewCopilotDlpClassification -Policy $policy

        $result.Qualifies | Should -BeTrue
        $result.RuleDiagnostics[0].AdvancedRuleSensitivityLabelMatched | Should -BeTrue
    }

    It 'supports direct, dictionary, object, and serialized RestrictAccess Block shapes' -ForEach @(
        @{ RestrictAccess = 'Block' }
        @{ RestrictAccess = @{ ExcludeContentProcessing = 'Block' } }
        @{ RestrictAccess = [PSCustomObject]@{ Setting = 'ExcludeContentProcessing'; Value = 'Block' } }
        @{ RestrictAccess = @(@{ Setting = 'ExcludeContentProcessing'; Value = 'Block' }) }
        @{ RestrictAccess = '[{"setting":"ExcludeContentProcessing","value":"Block"}]' }
    ) {
        Test-PurviewDspmRestrictAccessBlock -InputObject $RestrictAccess | Should -BeTrue
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
        $policy = Add-TestPurviewQualifyingRuleEvidence -Policy $policy

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
        $policy = Add-TestPurviewQualifyingRuleEvidence -Policy $policy

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
        $policy = Add-TestPurviewQualifyingRuleEvidence -Policy $policy

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
        $policy = Add-TestPurviewQualifyingRuleEvidence -Policy $policy

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
        $policy = Add-TestPurviewQualifyingRuleEvidence -Policy $policy

        (Get-PurviewCopilotDlpClassification -Policy $policy).Qualifies | Should -BeFalse
    }

    It 'rejects a missing mode even when all other signals match' {
        $policy = @{
            Name              = 'Missing mode'
            Enabled           = $true
            Locations         = @{ Workload = 'Applications'; Location = $copilotLocation }
            EnforcementPlanes = @('CopilotExperiences')
        }
        $policy = Add-TestPurviewQualifyingRuleEvidence -Policy $policy

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
        $policy = Add-TestPurviewQualifyingRuleEvidence -Policy $policy

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
        $policy = Add-TestPurviewQualifyingRuleEvidence -Policy $policy

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
        $policy = Add-TestPurviewQualifyingRuleEvidence -Policy $policy

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
        $policy = Add-TestPurviewQualifyingRuleEvidence -Policy $policy

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

    It 'qualifies a sensitivity-label blocking rule without SIT criteria' {
        $policy = @{
            Name                    = 'Sensitivity label policy'
            Mode                    = 'Enable'
            Locations               = @{ Workload = 'Applications'; Location = $copilotLocation }
            EnforcementPlanes       = @('CopilotExperiences')
            RuleCollectionSucceeded = $true
            Rules                   = @(
                @{
                    Name                            = 'Block Confidential'
                    Disabled                        = $false
                    BlockAccess                     = $true
                    EnforcementPlanes               = @('CopilotExperiences')
                    ContentContainsSensitivityLabel = @(@{ Name = 'Confidential' })
                }
            )
        }

        $result = Get-PurviewCopilotDlpClassification -Policy $policy

        $result.Qualifies | Should -BeTrue
        $result.RuleDiagnostics[0].SensitivityLabelMatched | Should -BeTrue
        $result.RuleDiagnostics[0].ContentContainsSensitivityLabel.Count | Should -Be 1
    }

    It 'rejects unrelated or malformed AdvancedRule content' -ForEach @(
        @{
            Description  = 'generic JSON'
            AdvancedRule = '{"Condition":{"Operator":"And","SubConditions":[{"ConditionName":"OtherCondition","Value":["x"]}]}}'
        }
        @{
            Description  = 'malformed JSON'
            AdvancedRule = '{"Condition":{"SubConditions":['
        }
        @{
            Description  = 'random text'
            AdvancedRule = 'ContentContainsSensitiveInformation'
        }
        @{
            Description  = 'generic non-empty object'
            AdvancedRule = @{ Version = '1.0'; Comment = 'configured' }
        }
        @{
            Description  = 'known name without criterion values'
            AdvancedRule = @{
                Condition = @{
                    SubConditions = @(
                        @{ ConditionName = 'ContentContainsSensitiveInformation'; Value = @() }
                    )
                }
            }
        }
    ) {
        $policy = @{
            Name                    = $Description
            Mode                    = 'Enable'
            Locations               = @{ Workload = 'Applications'; Location = $copilotLocation }
            EnforcementPlanes       = @('CopilotExperiences')
            RuleCollectionSucceeded = $true
            Rules                   = @(
                @{
                    Disabled       = $false
                    RestrictAccess = @{ ExcludeContentProcessing = 'Block' }
                    AdvancedRule   = $AdvancedRule
                }
            )
        }

        (Get-PurviewCopilotDlpClassification -Policy $policy).Qualifies | Should -BeFalse
    }

    It 'rejects RestrictAccess values other than Block' -ForEach @(
        @{ RestrictAccess = 'Allow' }
        @{ RestrictAccess = @{ ExcludeContentProcessing = 'Allow' } }
        @{ RestrictAccess = '[{"setting":"ExcludeContentProcessing","value":"Audit"}]' }
        @{ RestrictAccess = @{ OtherAction = 'Block' } }
        @{ RestrictAccess = @(@{ Setting = 'OtherSetting'; Value = 'Block' }) }
    ) {
        $policy = @{
            Name                    = 'Nonblocking RestrictAccess'
            Mode                    = 'Enable'
            Locations               = @{ Workload = 'Applications'; Location = $copilotLocation }
            EnforcementPlanes       = @('CopilotExperiences')
            RuleCollectionSucceeded = $true
            Rules                   = @(
                @{
                    Disabled       = $false
                    RestrictAccess = $RestrictAccess
                    AdvancedRule   = New-TestPurviewAdvancedRule `
                        -ConditionName 'ContentContainsSensitiveInformation'
                }
            )
        }

        (Get-PurviewCopilotDlpClassification -Policy $policy).Qualifies | Should -BeFalse
    }

    It 'rejects an explicitly unrelated rule plane while allowing the policy plane when omitted' {
        $baseRule = @{
            Disabled       = $false
            RestrictAccess = @{ ExcludeContentProcessing = 'Block' }
            AdvancedRule   = New-TestPurviewAdvancedRule `
                -ConditionName 'ContentContainsSensitiveInformation'
        }
        $policy = @{
            Name                    = 'Rule plane behavior'
            Mode                    = 'Enable'
            Locations               = @{ Workload = 'Applications'; Location = $copilotLocation }
            EnforcementPlanes       = @('CopilotExperiences')
            RuleCollectionSucceeded = $true
            Rules                   = @($baseRule.Clone())
        }

        (Get-PurviewCopilotDlpClassification -Policy $policy).Qualifies | Should -BeTrue

        $policy.Rules[0].EnforcementPlanes = @('EndpointDlp')
        $result = Get-PurviewCopilotDlpClassification -Policy $policy

        $result.Qualifies | Should -BeFalse
        $result.RuleDiagnostics[0].EnforcementPlaneSpecified | Should -BeTrue
        $result.RuleDiagnostics[0].EnforcementPlaneMatched | Should -BeFalse
    }

    It 'does not accept CopilotExperiences text in an unrelated nested rule-plane property' {
        $policy = @{
            Name                    = 'Nested rule plane'
            Mode                    = 'Enable'
            Locations               = @{ Workload = 'Applications'; Location = $copilotLocation }
            EnforcementPlanes       = @('CopilotExperiences')
            RuleCollectionSucceeded = $true
            Rules                   = @(
                @{
                    Disabled          = $false
                    RestrictAccess    = @{ ExcludeContentProcessing = 'Block' }
                    EnforcementPlanes = @{ Diagnostics = 'CopilotExperiences' }
                    AdvancedRule      = New-TestPurviewAdvancedRule `
                        -ConditionName 'ContentContainsSensitiveInformation'
                }
            )
        }

        $result = Get-PurviewCopilotDlpClassification -Policy $policy

        $result.Qualifies | Should -BeFalse
        $result.RuleDiagnostics[0].EnforcementPlaneSpecified | Should -BeTrue
        $result.RuleDiagnostics[0].EnforcementPlaneMatched | Should -BeFalse
    }

    It 'does not accept known words in unrelated nested RestrictAccess or AdvancedRule properties' {
        $policy = @{
            Name                    = 'Nested text false positive'
            Mode                    = 'Enable'
            Locations               = @{ Workload = 'Applications'; Location = $copilotLocation }
            EnforcementPlanes       = @('CopilotExperiences')
            RuleCollectionSucceeded = $true
            Rules                   = @(
                @{
                    Disabled       = $false
                    RestrictAccess = @{
                        Diagnostics = @{ ExcludeContentProcessing = 'Block' }
                    }
                    AdvancedRule   = @{
                        Diagnostics = @{
                            Text = 'ContentContainsSensitiveInformation'
                        }
                        Condition = @{
                            SubConditions = @(
                                @{
                                    ConditionName = 'OtherCondition'
                                    Value         = @('ContentContainsSensitivityLabel')
                                }
                            )
                        }
                    }
                }
            )
        }

        $result = Get-PurviewCopilotDlpClassification -Policy $policy

        $result.Qualifies | Should -BeFalse
        $result.RuleDiagnostics[0].RestrictAccessMatched | Should -BeFalse
        $result.RuleDiagnostics[0].AdvancedRuleSensitiveInformationMatched | Should -BeFalse
        $result.RuleDiagnostics[0].AdvancedRuleSensitivityLabelMatched | Should -BeFalse
    }

    It 'rejects <Description> as successfully collected negative rule evidence' -ForEach @(
        @{
            Description = 'an empty rule set'
            Rules       = @()
        }
        @{
            Description = 'a disabled blocking rule'
            Rules       = @(
                @{
                    Disabled                            = $true
                    BlockAccess                         = $true
                    EnforcementPlanes                   = @('CopilotExperiences')
                    ContentContainsSensitiveInformation = @('SIT')
                }
            )
        }
        @{
            Description = 'a nonblocking rule'
            Rules       = @(
                @{
                    Disabled                            = $false
                    BlockAccess                         = $false
                    EnforcementPlanes                   = @('CopilotExperiences')
                    ContentContainsSensitiveInformation = @('SIT')
                }
            )
        }
        @{
            Description = 'a rule on an unrelated enforcement plane'
            Rules       = @(
                @{
                    Disabled                            = $false
                    BlockAccess                         = $true
                    EnforcementPlanes                   = @('EndpointDlp')
                    ContentContainsSensitiveInformation = @('SIT')
                }
            )
        }
        @{
            Description = 'a rule without SIT or sensitivity-label criteria'
            Rules       = @(
                @{
                    Disabled              = $false
                    BlockAccess           = $true
                    EnforcementPlanes     = @('CopilotExperiences')
                }
            )
        }
    ) {
        $policy = @{
            Name                    = $Description
            Mode                    = 'Enable'
            Locations               = @{ Workload = 'Applications'; Location = $copilotLocation }
            EnforcementPlanes       = @('CopilotExperiences')
            RuleCollectionSucceeded = $true
            Rules                   = $Rules
        }

        $evidence = New-PurviewDspmEvidence -Policies @($policy) -DlpCollectionSucceeded $true

        $evidence.CollectionStatus | Should -Be 'collected'
        $evidence.Detected | Should -BeFalse
        $evidence.PolicyCount | Should -Be 0
    }
}

Describe 'New-PurviewDspmEvidence' {
    BeforeAll {
        . "$PSScriptRoot\PurviewDspmSupport.ps1"
        $copilotLocation = '470f2276-e011-4e9d-a6ec-20768be3a4b0'
        function New-TestPurviewQualifyingRule {
            [PSCustomObject]@{
                Name                                = 'Block sensitive Copilot content'
                Priority                            = 0
                Disabled                            = $false
                BlockAccess                         = $true
                EnforcementPlanes                   = @('CopilotExperiences')
                ContentContainsSensitiveInformation = @(@{ Name = 'U.S. Social Security Number' })
                ContentContainsSensitivityLabel     = @()
            }
        }
        $activePolicy = @{
            Name              = 'Active Copilot DLP'
            Enabled           = $true
            Mode              = 'Enforce'
            Locations         = @{ Workload = 'Applications'; Location = $copilotLocation }
            EnforcementPlanes = @('CopilotExperiences')
            Rules             = @(New-TestPurviewQualifyingRule)
            RuleCollectionSucceeded = $true
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

    It 'returns unknown when rule collection fails for an otherwise matching policy' {
        $policy = @{
            Name                    = 'Rules unavailable'
            Mode                    = 'Enable'
            Locations               = @{ Workload = 'Applications'; Location = $copilotLocation }
            EnforcementPlanes       = @('CopilotExperiences')
            Rules                   = @()
            RuleCollectionSucceeded = $false
            RuleCollectionStatus    = 'failed'
        }

        $evidence = New-PurviewDspmEvidence -Policies @($policy) -DlpCollectionSucceeded $true

        $evidence.CollectionStatus | Should -Be 'failed'
        $evidence.Detected | Should -BeNullOrEmpty
        $evidence.RelevantRuleCollectionFailureCount | Should -Be 1
        $evidence.Note | Should -Match 'rule evidence failed or was unavailable'
    }

    It 'passes a fully qualifying policy despite an unrelated rule collection failure' {
        $unrelatedPolicy = @{
            Name                    = 'Unrelated policy with failed rules'
            Mode                    = 'Enable'
            Locations               = @{ Workload = 'Exchange'; Location = 'exchange-location' }
            EnforcementPlanes       = @('CopilotExperiences')
            Rules                   = @()
            RuleCollectionSucceeded = $false
            RuleCollectionStatus    = 'failed'
        }

        $evidence = New-PurviewDspmEvidence `
            -Policies @($activePolicy, $unrelatedPolicy) `
            -DlpCollectionSucceeded $true

        $evidence.CollectionStatus | Should -Be 'collected'
        $evidence.Detected | Should -BeTrue
        $evidence.PolicyCount | Should -Be 1
        $evidence.RuleCollectionFailureCount | Should -Be 1
        $evidence.RelevantRuleCollectionFailureCount | Should -Be 0
    }
}
