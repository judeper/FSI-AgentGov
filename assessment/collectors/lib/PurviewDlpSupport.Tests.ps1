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

Describe 'Resolve-DlpPolicyEvidence' {
    BeforeAll {
        . "$PSScriptRoot\PurviewDlpSupport.ps1"

        # Helper: serialize a policy set into the same shape the collector emits
        # (the dlpCompliancePolicies section of purview.json) so tests assert
        # against the on-the-wire contract, not just in-memory types.
        function ConvertTo-PoliciesJson {
            param([Parameter()][AllowNull()][object]$Policies)
            [PSCustomObject]@{
                dlpCompliancePolicies = $Policies
            } | ConvertTo-Json -Depth 10 -Compress
        }
    }

    Context 'collection failure / unavailable' {
        It 'returns $null so the evaluator stays indeterminate (unknown)' {
            $result = Resolve-DlpPolicyEvidence -CollectedPolicies $null -CollectionSucceeded $false
            ($null -eq $result) | Should -BeTrue
        }

        It 'ignores any captured payload when collection did not succeed' {
            $result = Resolve-DlpPolicyEvidence -CollectedPolicies ([PSCustomObject]@{ Name = 'p1' }) -CollectionSucceeded $false
            ($null -eq $result) | Should -BeTrue
        }

        It 'serializes a failed policy set as JSON null (distinct from [])' {
            $result = Resolve-DlpPolicyEvidence -CollectedPolicies $null -CollectionSucceeded $false
            (ConvertTo-PoliciesJson -Policies $result) | Should -Match '"dlpCompliancePolicies":null'
        }
    }

    Context 'successful collection with zero rows' {
        It 'returns an empty array (not $null) so the evaluator scores fail' {
            # A pipeline capture over an empty result collapses to $null in
            # PowerShell; the success flag must still yield an explicit [].
            $emptyCapture = @() | ForEach-Object { $_ }
            ($null -eq $emptyCapture) | Should -BeTrue

            $result = Resolve-DlpPolicyEvidence -CollectedPolicies $emptyCapture -CollectionSucceeded $true
            ($null -eq $result) | Should -BeFalse
            ($result -is [array]) | Should -BeTrue
            @($result).Count | Should -Be 0
        }

        It 'treats an already-empty array on success as an empty array' {
            $result = Resolve-DlpPolicyEvidence -CollectedPolicies @() -CollectionSucceeded $true
            ($null -eq $result) | Should -BeFalse
            ($result -is [array]) | Should -BeTrue
            @($result).Count | Should -Be 0
        }

        It 'serializes an empty successful policy set as JSON [] (distinct from null)' {
            $result = Resolve-DlpPolicyEvidence -CollectedPolicies (@() | ForEach-Object { $_ }) -CollectionSucceeded $true
            (ConvertTo-PoliciesJson -Policies $result) | Should -Match '"dlpCompliancePolicies":\[\]'
        }
    }

    Context 'successful collection with policies (singleton normalization preserved)' {
        It 'normalizes a single policy object to a one-item array' {
            $policy = [PSCustomObject]@{ Name = 'p1'; Mode = 'Enable' }
            $result = Resolve-DlpPolicyEvidence -CollectedPolicies $policy -CollectionSucceeded $true
            ($result -is [array]) | Should -BeTrue
            @($result).Count | Should -Be 1
            $result[0].Name | Should -Be 'p1'
        }

        It 'serializes a single policy as a one-element JSON array' {
            $policy = [PSCustomObject]@{ Name = 'p1'; Mode = 'Enable' }
            $result = Resolve-DlpPolicyEvidence -CollectedPolicies $policy -CollectionSucceeded $true
            (ConvertTo-PoliciesJson -Policies $result) | Should -Match '"dlpCompliancePolicies":\[\{'
        }

        It 'preserves a multi-policy array shape' {
            $policies = @(
                [PSCustomObject]@{ Name = 'p1' }
                [PSCustomObject]@{ Name = 'p2' }
            )
            $result = Resolve-DlpPolicyEvidence -CollectedPolicies $policies -CollectionSucceeded $true
            ($result -is [array]) | Should -BeTrue
            @($result).Count | Should -Be 2
            $result[1].Name | Should -Be 'p2'
        }
    }

    Context 'the three evidence states are mutually distinct' {
        It 'produces different JSON for empty-success, failure, and populated' {
            $emptyJson = ConvertTo-PoliciesJson -Policies (Resolve-DlpPolicyEvidence -CollectedPolicies (@() | ForEach-Object { $_ }) -CollectionSucceeded $true)
            $failJson = ConvertTo-PoliciesJson -Policies (Resolve-DlpPolicyEvidence -CollectedPolicies $null -CollectionSucceeded $false)
            $fullJson = ConvertTo-PoliciesJson -Policies (Resolve-DlpPolicyEvidence -CollectedPolicies ([PSCustomObject]@{ Name = 'p1' }) -CollectionSucceeded $true)

            $emptyJson | Should -Not -Be $failJson
            $emptyJson | Should -Match '"dlpCompliancePolicies":\[\]'
            $failJson | Should -Match '"dlpCompliancePolicies":null'
            $fullJson | Should -Match '"dlpCompliancePolicies":\[\{'
        }
    }
}

Describe 'Resolve-DlpPolicyScope' {
    BeforeAll {
        . "$PSScriptRoot\PurviewDlpSupport.ps1"

        $script:CopilotGuid = '470f2276-e011-4e9d-a6ec-20768be3a4b0'

        # A Get-DlpCompliancePolicy object scoped to Microsoft 365 Copilot, per
        # Microsoft Learn New-DlpCompliancePolicy Example 4 / 1.13 §9.
        function New-CopilotScopedPolicy {
            [PSCustomObject]@{
                Name              = 'FSI-Copilot-Block-MNPI'
                Mode              = 'Enable'
                Enabled           = $null
                Workload          = 'Applications'
                EnforcementPlanes = @('CopilotExperiences')
                Locations         = @(
                    [PSCustomObject]@{
                        Workload   = 'Applications'
                        Location   = '470f2276-e011-4e9d-a6ec-20768be3a4b0'
                        Inclusions = @([PSCustomObject]@{ Type = 'Tenant'; Identity = 'All' })
                    }
                )
            }
        }
    }

    Context 'StrictMode-safe property access (Get-DlpScopeProperty)' {
        It 'returns $null for an absent property instead of throwing' {
            $policy = [PSCustomObject]@{ Name = 'p'; Mode = 'Enable' }
            (Get-DlpScopeProperty -InputObject $policy -Name 'EnforcementPlanes') | Should -BeNullOrEmpty
        }

        It 'returns the value for a present property' {
            $policy = [PSCustomObject]@{ Workload = 'Applications' }
            (Get-DlpScopeProperty -InputObject $policy -Name 'Workload') | Should -Be 'Applications'
        }

        It 'returns $null for a $null input object' {
            (Get-DlpScopeProperty -InputObject $null -Name 'Workload') | Should -BeNullOrEmpty
        }
    }

    Context 'EnforcementPlanes normalization (ConvertTo-DlpStringArray)' {
        It 'wraps a single scalar plane into a one-element array' {
            $result = ConvertTo-DlpStringArray -Value 'CopilotExperiences'
            ($result -is [array]) | Should -BeTrue
            @($result).Count | Should -Be 1
            $result[0] | Should -Be 'CopilotExperiences'
        }

        It 'preserves a multi-value plane array' {
            $result = ConvertTo-DlpStringArray -Value @('Browser', 'CopilotExperiences')
            @($result).Count | Should -Be 2
            $result[1] | Should -Be 'CopilotExperiences'
        }

        It 'drops null/blank entries' {
            $result = ConvertTo-DlpStringArray -Value @('CopilotExperiences', $null, '   ')
            @($result).Count | Should -Be 1
            $result[0] | Should -Be 'CopilotExperiences'
        }

        It 'collapses an absent/all-blank value to $null' {
            (ConvertTo-DlpStringArray -Value $null) | Should -BeNullOrEmpty
            (ConvertTo-DlpStringArray -Value @()) | Should -BeNullOrEmpty
            (ConvertTo-DlpStringArray -Value @('  ', $null)) | Should -BeNullOrEmpty
        }

        It 'serializes a single plane as a one-element JSON array (no collapse)' {
            $json = [PSCustomObject]@{ EnforcementPlanes = (ConvertTo-DlpStringArray -Value 'CopilotExperiences') } |
                ConvertTo-Json -Depth 5 -Compress
            $json | Should -Match '"EnforcementPlanes":\["CopilotExperiences"\]'
        }
    }

    Context 'Locations normalization (ConvertTo-DlpLocationArray)' {
        It 'preserves an object-array Locations shape' {
            $locations = @(
                [PSCustomObject]@{ Workload = 'Applications'; Location = $script:CopilotGuid }
            )
            $result = ConvertTo-DlpLocationArray -Value $locations
            ($result -is [array]) | Should -BeTrue
            $result[0].Location | Should -Be $script:CopilotGuid
        }

        It 'wraps a singleton location object (ConvertTo-Json collapse) into an array' {
            $single = [PSCustomObject]@{ Workload = 'Applications'; Location = $script:CopilotGuid }
            $result = ConvertTo-DlpLocationArray -Value $single
            ($result -is [array]) | Should -BeTrue
            @($result).Count | Should -Be 1
            $result[0].Location | Should -Be $script:CopilotGuid
        }

        It 'parses a raw -Locations JSON string into location objects' {
            $json = '[{"Workload":"Applications","Location":"470f2276-e011-4e9d-a6ec-20768be3a4b0","Inclusions":[{"Type":"Tenant","Identity":"All"}]}]'
            $result = ConvertTo-DlpLocationArray -Value $json
            @($result).Count | Should -Be 1
            $result[0].Location | Should -Be $script:CopilotGuid
            $result[0].Workload | Should -Be 'Applications'
        }

        It 'collapses an empty/malformed/unparseable value to $null (fail closed)' {
            (ConvertTo-DlpLocationArray -Value $null) | Should -BeNullOrEmpty
            (ConvertTo-DlpLocationArray -Value '') | Should -BeNullOrEmpty
            (ConvertTo-DlpLocationArray -Value '   ') | Should -BeNullOrEmpty
            (ConvertTo-DlpLocationArray -Value '{ not json') | Should -BeNullOrEmpty
            (ConvertTo-DlpLocationArray -Value @()) | Should -BeNullOrEmpty
        }
    }

    Context 'a Copilot-scoped policy' {
        It 'preserves all three documented scope signals verbatim' {
            $scope = Resolve-DlpPolicyScope -Policy (New-CopilotScopedPolicy)
            $scope.Workload | Should -Be 'Applications'
            $scope.EnforcementPlanes[0] | Should -Be 'CopilotExperiences'
            $scope.Locations[0].Location | Should -Be $script:CopilotGuid
        }

        It 'serializes to the on-the-wire purview.json scope contract' {
            $policy = New-CopilotScopedPolicy
            $scope = Resolve-DlpPolicyScope -Policy $policy
            $json = [PSCustomObject]@{
                Name              = $policy.Name
                Mode              = $policy.Mode
                Workload          = $scope.Workload
                EnforcementPlanes = $scope.EnforcementPlanes
                Locations         = $scope.Locations
                Enabled           = $policy.Enabled
            } | ConvertTo-Json -Depth 10 -Compress

            $json | Should -Match '"Workload":"Applications"'
            $json | Should -Match '"EnforcementPlanes":\["CopilotExperiences"\]'
            $json | Should -Match "\`"Location\`":\`"$($script:CopilotGuid)\`""
            $json | Should -Match '"Enabled":null'
        }
    }

    Context 'a non-Copilot policy and absent scope evidence' {
        It 'preserves an Exchange/SharePoint workload with no Copilot scope fields' {
            $policy = [PSCustomObject]@{
                Name = 'Exchange DLP'; Mode = 'Enable'; Workload = 'Exchange,SharePoint'
            }
            $scope = Resolve-DlpPolicyScope -Policy $policy
            $scope.Workload | Should -Be 'Exchange,SharePoint'
            $scope.EnforcementPlanes | Should -BeNullOrEmpty
            $scope.Locations | Should -BeNullOrEmpty
        }

        It 'returns null scope fields for a $null policy' {
            $scope = Resolve-DlpPolicyScope -Policy $null
            $scope.Workload | Should -BeNullOrEmpty
            $scope.EnforcementPlanes | Should -BeNullOrEmpty
            $scope.Locations | Should -BeNullOrEmpty
        }
    }
}

Describe 'DLP policy Enabled projection is StrictMode-safe (control 1.13.b regression)' {
    # Regression for the P1 blocker: Collect-Purview.ps1 Section 2 dereferenced
    # $policy.Enabled directly. Real Get-DlpCompliancePolicy objects (older
    # module builds) omit the Enabled property because Mode governs enforcement,
    # so under Set-StrictMode -Version Latest the dereference threw
    # PropertyNotFoundStrict before Resolve-DlpPolicyEvidence, nulling the whole
    # DLP evidence set and making 1.13.b unscorable for otherwise-valid
    # Copilot-scoped policies. Enabled is now read through the same
    # PSObject.Properties helper as the scope fields (Get-DlpScopeProperty).
    BeforeAll {
        . "$PSScriptRoot\PurviewDlpSupport.ps1"

        $script:CopilotGuid = '470f2276-e011-4e9d-a6ec-20768be3a4b0'

        # Faithful mirror of the Collect-Purview.ps1 Section 2 per-policy record
        # projection: Name/Mode are read directly (always present on a
        # Get-DlpCompliancePolicy object), scope via Resolve-DlpPolicyScope,
        # rules via Resolve-DlpRuleEvidence, and Enabled via the StrictMode-safe
        # Get-DlpScopeProperty helper. A scriptblock (not a function) keeps the
        # analyzer's state-changing-verb rule quiet.
        $script:NewPolicyRecord = {
            param(
                [Parameter(Mandatory)][AllowNull()][object]$Policy,
                [Parameter()][AllowNull()][object]$CollectedRules,
                [Parameter(Mandatory)][bool]$RulesCollected
            )
            $scope = Resolve-DlpPolicyScope -Policy $Policy
            [PSCustomObject]@{
                Name              = $Policy.Name
                Mode              = $Policy.Mode
                Workload          = $scope.Workload
                EnforcementPlanes = $scope.EnforcementPlanes
                Locations         = $scope.Locations
                Enabled           = (Get-DlpScopeProperty -InputObject $Policy -Name 'Enabled')
                Rules             = (Resolve-DlpRuleEvidence -CollectedRules $CollectedRules -CollectionSucceeded $RulesCollected)
            }
        }

        # A Copilot-scoped, Mode=Enable policy that GENUINELY lacks an Enabled
        # property. No Enabled key is added, so a direct $policy.Enabled throws
        # PropertyNotFoundStrict under Set-StrictMode -Version Latest, exactly as
        # the real-world objects the blocker describes.
        $script:MakePolicyMissingEnabled = {
            [PSCustomObject]@{
                Name              = 'FSI-Copilot-Block-MNPI'
                Mode              = 'Enable'
                Workload          = 'Applications'
                EnforcementPlanes = @('CopilotExperiences')
                Locations         = @(
                    [PSCustomObject]@{
                        Workload = 'Applications'
                        Location = '470f2276-e011-4e9d-a6ec-20768be3a4b0'
                    }
                )
            }
        }

        # A single collected rule with a SIT-bearing AdvancedRule, matching the
        # collector's projected rule shape, so the regression proves rules are
        # preserved alongside the absent Enabled.
        $script:SampleRule = [PSCustomObject]@{
            Name         = 'Block MNPI to Copilot'
            Disabled     = $false
            AdvancedRule = '{"Condition":{"SensitiveInformationType":"MNPI"}}'
            BlockAccess  = $true
            Priority     = 0
        }
    }

    BeforeEach {
        # The collector runs under StrictMode; reproduce that in every case so
        # the absent-property throw (and its absence after the fix) is genuine.
        Set-StrictMode -Version Latest
    }

    Context 'a policy object that truly lacks Enabled under StrictMode' {
        It 'the raw policy genuinely omits Enabled (a direct dereference throws)' {
            $policy = & $script:MakePolicyMissingEnabled
            # Negative control: proves the fixture reproduces the failing shape.
            $policy.PSObject.Properties['Enabled'] | Should -BeNullOrEmpty
            { $policy.Enabled } | Should -Throw -ErrorId 'PropertyNotFoundStrict'
        }

        It 'projects without throwing and preserves Mode, Copilot scope, and rules' {
            $policy = & $script:MakePolicyMissingEnabled
            { & $script:NewPolicyRecord -Policy $policy -CollectedRules $script:SampleRule -RulesCollected $true | Out-Null } |
                Should -Not -Throw
            $record = & $script:NewPolicyRecord -Policy $policy -CollectedRules $script:SampleRule -RulesCollected $true
            $record.Mode | Should -Be 'Enable'
            $record.Workload | Should -Be 'Applications'
            $record.EnforcementPlanes[0] | Should -Be 'CopilotExperiences'
            $record.Locations[0].Location | Should -Be $script:CopilotGuid
            @($record.Rules).Count | Should -Be 1
            $record.Rules[0].Name | Should -Be 'Block MNPI to Copilot'
        }

        It 'serializes an absent Enabled as JSON null (evaluator: absent/null -> qualify)' {
            $policy = & $script:MakePolicyMissingEnabled
            $record = & $script:NewPolicyRecord -Policy $policy -CollectedRules $script:SampleRule -RulesCollected $true
            ($record | ConvertTo-Json -Depth 10 -Compress) | Should -Match '"Enabled":null'
        }
    }

    Context 'an explicitly provided Enabled reaches the evaluator verbatim (truth table preserved)' {
        It 'passes an explicit $false through unchanged (evaluator: reject)' {
            $policy = & $script:MakePolicyMissingEnabled |
                Add-Member -NotePropertyName Enabled -NotePropertyValue $false -PassThru
            $record = & $script:NewPolicyRecord -Policy $policy -CollectedRules $null -RulesCollected $false
            ($record.Enabled -is [bool]) | Should -BeTrue
            ($record | ConvertTo-Json -Depth 10 -Compress) | Should -Match '"Enabled":false'
        }

        It 'passes an explicit $true through unchanged (evaluator: qualify)' {
            $policy = & $script:MakePolicyMissingEnabled |
                Add-Member -NotePropertyName Enabled -NotePropertyValue $true -PassThru
            $record = & $script:NewPolicyRecord -Policy $policy -CollectedRules $null -RulesCollected $false
            ($record.Enabled -is [bool]) | Should -BeTrue
            ($record | ConvertTo-Json -Depth 10 -Compress) | Should -Match '"Enabled":true'
        }

        It 'passes a malformed present value through unchanged (evaluator: malformed)' {
            $policy = & $script:MakePolicyMissingEnabled |
                Add-Member -NotePropertyName Enabled -NotePropertyValue 'yes' -PassThru
            $record = & $script:NewPolicyRecord -Policy $policy -CollectedRules $null -RulesCollected $false
            $record.Enabled | Should -Be 'yes'
            ($record | ConvertTo-Json -Depth 10 -Compress) | Should -Match '"Enabled":"yes"'
        }

        It 'passes an explicit $null through as JSON null (evaluator: qualify)' {
            $policy = & $script:MakePolicyMissingEnabled |
                Add-Member -NotePropertyName Enabled -NotePropertyValue $null -PassThru
            # The property is present (unlike the absent case) but still null.
            $policy.PSObject.Properties['Enabled'] | Should -Not -BeNullOrEmpty
            $record = & $script:NewPolicyRecord -Policy $policy -CollectedRules $null -RulesCollected $false
            ($record | ConvertTo-Json -Depth 10 -Compress) | Should -Match '"Enabled":null'
        }
    }

    Context 'the shipped collector reads Enabled through the safe helper' {
        BeforeAll {
            $script:CollectorPath = Join-Path (Split-Path -Parent $PSScriptRoot) 'Collect-Purview.ps1'
            $tokens = $null
            $errors = $null
            $script:CollectorAst = [System.Management.Automation.Language.Parser]::ParseFile(
                $script:CollectorPath, [ref]$tokens, [ref]$errors)
            $script:CollectorParseErrors = $errors
        }

        It 'parses without errors' {
            Test-Path $script:CollectorPath | Should -BeTrue
            @($script:CollectorParseErrors).Count | Should -Be 0
        }

        It 'contains no bare $policy.Enabled member access (regression guard)' {
            $bareEnabled = $script:CollectorAst.FindAll({
                param($node)
                $node -is [System.Management.Automation.Language.MemberExpressionAst] -and
                $node.Member -is [System.Management.Automation.Language.StringConstantExpressionAst] -and
                $node.Member.Value -eq 'Enabled' -and
                $node.Expression -is [System.Management.Automation.Language.VariableExpressionAst] -and
                $node.Expression.VariablePath.UserPath -eq 'policy'
            }, $true)
            @($bareEnabled).Count | Should -Be 0
        }

        It 'reads policy Enabled via Get-DlpScopeProperty' {
            $helperCalls = $script:CollectorAst.FindAll({
                param($node)
                $node -is [System.Management.Automation.Language.CommandAst] -and
                $node.GetCommandName() -eq 'Get-DlpScopeProperty' -and
                @($node.CommandElements | Where-Object {
                    $_ -is [System.Management.Automation.Language.StringConstantExpressionAst] -and $_.Value -eq 'Enabled'
                }).Count -gt 0 -and
                @($node.CommandElements | Where-Object {
                    $_ -is [System.Management.Automation.Language.VariableExpressionAst] -and $_.VariablePath.UserPath -eq 'policy'
                }).Count -gt 0
            }, $true)
            @($helperCalls).Count | Should -BeGreaterThan 0
        }
    }
}
