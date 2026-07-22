#Requires -Modules Pester

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Describe 'Resolve-DlpRuleEvidence' {
    BeforeAll {
        . "$PSScriptRoot\PurviewDlpSupport.ps1"

        # Helper: serialize a rule set into the same nested shape the collector
        # emits (Rules property of a DLP policy object) so tests assert against
        # the on-the-wire purview.json contract, not just in-memory types.
        function ConvertTo-RulesJson {
            param([Parameter()][AllowNull()][object]$Rules)
            [PSCustomObject]@{
                Name    = 'p'
                Mode    = 'Enable'
                Enabled = $true
                Rules   = $Rules
            } | ConvertTo-Json -Depth 10 -Compress
        }
    }

    Context 'collection failure / unavailable' {
        It 'returns $null so the evaluator stays indeterminate (unknown)' {
            $result = Resolve-DlpRuleEvidence -CollectedRules $null -CollectionSucceeded $false
            ($null -eq $result) | Should -BeTrue
        }

        It 'ignores any captured payload when collection did not succeed' {
            $result = Resolve-DlpRuleEvidence -CollectedRules ([PSCustomObject]@{ Name = 'r1' }) -CollectionSucceeded $false
            ($null -eq $result) | Should -BeTrue
        }

        It 'serializes a failed rule set as JSON null (distinct from [])' {
            $result = Resolve-DlpRuleEvidence -CollectedRules $null -CollectionSucceeded $false
            (ConvertTo-RulesJson -Rules $result) | Should -Match '"Rules":null'
        }
    }

    Context 'successful collection with zero rows' {
        It 'returns an empty array (not $null) so the evaluator scores fail' {
            # An empty pipeline capture collapses to $null in PowerShell; the
            # success flag must still yield an explicit empty array.
            $emptyCapture = @() | ForEach-Object { $_ }
            ($null -eq $emptyCapture) | Should -BeTrue

            $result = Resolve-DlpRuleEvidence -CollectedRules $emptyCapture -CollectionSucceeded $true
            ($null -eq $result) | Should -BeFalse
            ($result -is [array]) | Should -BeTrue
            @($result).Count | Should -Be 0
        }

        It 'treats an already-empty array on success as an empty array' {
            $result = Resolve-DlpRuleEvidence -CollectedRules @() -CollectionSucceeded $true
            ($null -eq $result) | Should -BeFalse
            ($result -is [array]) | Should -BeTrue
            @($result).Count | Should -Be 0
        }

        It 'serializes an empty successful rule set as JSON [] (distinct from null)' {
            $result = Resolve-DlpRuleEvidence -CollectedRules (@() | ForEach-Object { $_ }) -CollectionSucceeded $true
            (ConvertTo-RulesJson -Rules $result) | Should -Match '"Rules":\[\]'
        }
    }

    Context 'successful collection with rules (singleton normalization preserved)' {
        It 'normalizes a single rule object to a one-item array' {
            $rule = [PSCustomObject]@{ Name = 'r1'; Disabled = $false }
            $result = Resolve-DlpRuleEvidence -CollectedRules $rule -CollectionSucceeded $true
            ($result -is [array]) | Should -BeTrue
            @($result).Count | Should -Be 1
            $result[0].Name | Should -Be 'r1'
        }

        It 'serializes a single rule as a one-element JSON array' {
            $rule = [PSCustomObject]@{ Name = 'r1'; Disabled = $false }
            $result = Resolve-DlpRuleEvidence -CollectedRules $rule -CollectionSucceeded $true
            (ConvertTo-RulesJson -Rules $result) | Should -Match '"Rules":\[\{'
        }

        It 'preserves a multi-rule array shape' {
            $rules = @(
                [PSCustomObject]@{ Name = 'r1' }
                [PSCustomObject]@{ Name = 'r2' }
            )
            $result = Resolve-DlpRuleEvidence -CollectedRules $rules -CollectionSucceeded $true
            ($result -is [array]) | Should -BeTrue
            @($result).Count | Should -Be 2
            $result[1].Name | Should -Be 'r2'
        }
    }

    Context 'the three evidence states are mutually distinct' {
        It 'produces different JSON for empty-success, failure, and populated' {
            $emptyJson = ConvertTo-RulesJson -Rules (Resolve-DlpRuleEvidence -CollectedRules (@() | ForEach-Object { $_ }) -CollectionSucceeded $true)
            $failJson = ConvertTo-RulesJson -Rules (Resolve-DlpRuleEvidence -CollectedRules $null -CollectionSucceeded $false)
            $fullJson = ConvertTo-RulesJson -Rules (Resolve-DlpRuleEvidence -CollectedRules ([PSCustomObject]@{ Name = 'r1' }) -CollectionSucceeded $true)

            $emptyJson | Should -Not -Be $failJson
            $emptyJson | Should -Match '"Rules":\[\]'
            $failJson | Should -Match '"Rules":null'
            $fullJson | Should -Match '"Rules":\[\{'
        }
    }
}
