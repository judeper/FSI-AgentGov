#Requires -Modules Pester

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

BeforeAll {
    . "$PSScriptRoot\PpacCollectorSupport.ps1"

    # Build a complete, realistic raw Get-DlpPolicy row. Every property the projection
    # reads must be present (Set-StrictMode -Version Latest throws on missing members),
    # and connectorGroups is an empty array so the connector projection has nothing to
    # iterate — this test targets the no-policy / singleton / multi *shape* contract,
    # not connector classification. isEnabled is $null because classic DLP has no
    # enable/disable property.
    function New-TestDlpPolicy {
        param(
            [string]$DisplayName = 'Test DLP Policy',
            [string]$Name = '00000000-0000-0000-0000-000000000001',
            $EnvironmentType = 'AllEnvironments',
            $Environments = $null
        )
        [PSCustomObject]@{
            displayName     = $DisplayName
            name            = $Name
            createdTime     = '2026-01-01T00:00:00Z'
            isEnabled       = $null
            connectorGroups = @()
            environmentType = $EnvironmentType
            environments    = $Environments
        }
    }

    # Serialize exactly as Collect-PPAC.ps1 does (dlpPolicies nested in the ordered
    # result map, ConvertTo-Json -Depth 10) so the on-the-wire contract is asserted:
    # a successful no-row collection must be [], never null and never a phantom object.
    function ConvertTo-DlpPoliciesJson {
        param($DlpPolicies)
        ([ordered]@{ dlpPolicies = $DlpPolicies }) | ConvertTo-Json -Depth 10
    }
}

Describe 'ConvertTo-PpacDlpPolicyList' {

    Context 'No classic DLP policies (Get-DlpPolicy returned no rows -> $null)' {
        It 'returns an empty array, not a one-item phantom placeholder' {
            $result = ConvertTo-PpacDlpPolicyList -RawDlpPolicy $null
            $result -is [array] | Should -BeTrue
            @($result).Count | Should -Be 0
        }

        It 'serializes dlpPolicies as [] (never null, never an all-null phantom object)' {
            $dlpPolicies = ConvertTo-PpacDlpPolicyList -RawDlpPolicy $null
            $json = ConvertTo-DlpPoliciesJson $dlpPolicies
            $json | Should -Match '"dlpPolicies":\s*\[\s*\]'
            $json | Should -Not -Match '"DisplayName":\s*null'
        }
    }

    Context 'Empty array input (defensive)' {
        It 'returns an empty array' {
            $result = ConvertTo-PpacDlpPolicyList -RawDlpPolicy @()
            @($result).Count | Should -Be 0
        }
    }

    Context 'Single policy (Get-DlpPolicy returned one row)' {
        It 'returns a one-element array (singleton not collapsed to a bare object)' {
            $result = ConvertTo-PpacDlpPolicyList -RawDlpPolicy (New-TestDlpPolicy)
            $result -is [array] | Should -BeTrue
            @($result).Count | Should -Be 1
        }

        It 'projects the real policy fields, proving no all-null phantom row' {
            $result = ConvertTo-PpacDlpPolicyList -RawDlpPolicy (New-TestDlpPolicy -DisplayName 'Prod DLP' -Name 'prod-1')
            $result[0].DisplayName | Should -Be 'Prod DLP'
            $result[0].PolicyName | Should -Be 'prod-1'
            $result[0].EnvironmentType | Should -Be 'AllEnvironments'
        }

        It 'serializes a single policy as a JSON array' {
            $dlpPolicies = ConvertTo-PpacDlpPolicyList -RawDlpPolicy (New-TestDlpPolicy)
            $parsed = (ConvertTo-DlpPoliciesJson $dlpPolicies) | ConvertFrom-Json
            $parsed.dlpPolicies -is [array] | Should -BeTrue
            @($parsed.dlpPolicies).Count | Should -Be 1
        }
    }

    Context 'Object-shaped Environments normalization (7c267020 contract preserved)' {
        It 'keeps a singleton object-shaped Environments entry as an array' {
            $env = [PSCustomObject]@{
                id   = '/providers/Microsoft.BusinessAppPlatform/scopes/admin/environments/env-a-guid'
                name = 'env-a-guid'
                type = 'Microsoft.BusinessAppPlatform/scopes/admin/environments'
            }
            $result = ConvertTo-PpacDlpPolicyList -RawDlpPolicy (New-TestDlpPolicy -EnvironmentType 'OnlyEnvironments' -Environments $env)
            $result[0].Environments -is [array] | Should -BeTrue
            @($result[0].Environments).Count | Should -Be 1
            $result[0].Environments[0].name | Should -Be 'env-a-guid'
        }

        It 'leaves Environments null when the policy has none (All scope)' {
            $result = ConvertTo-PpacDlpPolicyList -RawDlpPolicy (New-TestDlpPolicy -EnvironmentType 'AllEnvironments' -Environments $null)
            $result[0].Environments | Should -BeNullOrEmpty
        }
    }

    Context 'Empty environment scope preserved as [] (pr1040 empty-scope regression)' {
        # Regression for the enumerating property reader (Get-PpacDlpProperty used a
        # bare `return $property.Value`). A PRESENT empty environments array
        # (environments = @()) was streamed as normal function output, which
        # PowerShell enumerates: @() yields zero objects, so the caller received
        # $null — indistinguishable from an absent scope. The policy then projected
        # Environments = null instead of []. The Python scorer
        # (assessment/engine/score.py _eval_dlp_policy_exists / _extract_dlp_scope_ids)
        # reads a null scope on Except/Only as "malformed (fail closed)", so:
        #   * ExceptEnvironments []  -> should COVER ALL inventory (excludes nothing)
        #     but degraded to malformed/unverifiable.
        #   * OnlyEnvironments []    -> should be a CLEAN fail (covers nothing)
        #     but degraded to malformed.
        # test_score.py::test_except_environments_empty_scope_covers_all and
        # ::test_only_environments_empty_scope_covers_nothing lock the scorer side;
        # these assert the collector emits [] (not null) so those semantics hold.
        # The raw policy is built inline (not via New-TestDlpPolicy) so environments
        # is unambiguously a PRESENT empty array.

        BeforeAll {
            function New-EmptyScopePolicy {
                param([Parameter(Mandatory)][string]$EnvironmentType)
                [PSCustomObject]@{
                    displayName     = "Empty $EnvironmentType"
                    name            = 'empty-scope-1'
                    createdTime     = '2026-01-01T00:00:00Z'
                    isEnabled       = $null
                    connectorGroups = @()
                    environmentType = $EnvironmentType
                    environments    = @()   # PRESENT empty scope
                }
            }
        }

        It 'projects ExceptEnvironments environments=@() as an empty (non-null) array' {
            $result = ConvertTo-PpacDlpPolicyList -RawDlpPolicy (New-EmptyScopePolicy -EnvironmentType 'ExceptEnvironments')
            $result[0].EnvironmentType | Should -Be 'ExceptEnvironments'
            # -is [array] is $false for $null (the bug) and $true for @() (the fix).
            $result[0].Environments -is [array] | Should -BeTrue
            # @($null).Count == 1, @(@()).Count == 0 — discriminates null from empty.
            @($result[0].Environments).Count | Should -Be 0
        }

        It 'serializes ExceptEnvironments empty scope as "Environments": [] (never null)' {
            $dlpPolicies = ConvertTo-PpacDlpPolicyList -RawDlpPolicy (New-EmptyScopePolicy -EnvironmentType 'ExceptEnvironments')
            $json = ConvertTo-DlpPoliciesJson $dlpPolicies
            # The on-the-wire contract the Python scorer consumes: [] not null.
            $json | Should -Match '"Environments":\s*\[\s*\]'
            $json | Should -Not -Match '"Environments":\s*null'
        }

        It 'projects OnlyEnvironments environments=@() as an empty (non-null) array' {
            $result = ConvertTo-PpacDlpPolicyList -RawDlpPolicy (New-EmptyScopePolicy -EnvironmentType 'OnlyEnvironments')
            $result[0].EnvironmentType | Should -Be 'OnlyEnvironments'
            $result[0].Environments -is [array] | Should -BeTrue
            @($result[0].Environments).Count | Should -Be 0
        }

        It 'serializes OnlyEnvironments empty scope as "Environments": [] (clean-fail scorer input)' {
            $dlpPolicies = ConvertTo-PpacDlpPolicyList -RawDlpPolicy (New-EmptyScopePolicy -EnvironmentType 'OnlyEnvironments')
            $json = ConvertTo-DlpPoliciesJson $dlpPolicies
            $json | Should -Match '"Environments":\s*\[\s*\]'
            $json | Should -Not -Match '"Environments":\s*null'
        }
    }

    Context 'Multiple policies (Get-DlpPolicy returned many rows)' {
        It 'returns an array with one element per policy' {
            $result = ConvertTo-PpacDlpPolicyList -RawDlpPolicy @(
                (New-TestDlpPolicy -Name 'p1'),
                (New-TestDlpPolicy -Name 'p2'),
                (New-TestDlpPolicy -Name 'p3')
            )
            @($result).Count | Should -Be 3
            $result.PolicyName | Should -Contain 'p2'
        }
    }

    Context 'StrictMode-safe projection of absent optional members (Finding 2)' {
        # Real classic DLP objects vary by module build. Under Set-StrictMode -Version
        # Latest a direct $_.isEnabled on an object with no isEnabled member throws
        # PropertyNotFoundStrict, which previously killed the whole projection and lost
        # the policy's environment scope -> Control 1.4.a stuck at unknown. These rows
        # deliberately OMIT members (they are simply absent from the hashtable) to prove
        # the projection reads every member defensively via Get-PpacDlpProperty.

        It 'projects a policy with NO isEnabled member as IsEnabled=null without throwing' {
            $noIsEnabled = [PSCustomObject]@{
                displayName     = 'No IsEnabled'
                name            = 'no-isenabled-1'
                createdTime     = '2026-01-01T00:00:00Z'
                connectorGroups = @()
                environmentType = 'AllEnvironments'
                environments    = $null
                # isEnabled deliberately absent
            }
            { ConvertTo-PpacDlpPolicyList -RawDlpPolicy $noIsEnabled } | Should -Not -Throw
            $result = ConvertTo-PpacDlpPolicyList -RawDlpPolicy $noIsEnabled
            $result[0].IsEnabled | Should -BeNullOrEmpty
            $result[0].DisplayName | Should -Be 'No IsEnabled'
            $result[0].PolicyName | Should -Be 'no-isenabled-1'
        }

        It 'preserves environment scope on a minimal row that omits displayName/name/isEnabled/createdTime' {
            $env = [PSCustomObject]@{
                id   = '/providers/Microsoft.BusinessAppPlatform/scopes/admin/environments/env-guid'
                name = 'env-guid'
                type = 'Microsoft.BusinessAppPlatform/scopes/admin/environments'
            }
            $minimal = [PSCustomObject]@{
                environmentType = 'OnlyEnvironments'
                environments    = $env
                # every other member absent
            }
            { ConvertTo-PpacDlpPolicyList -RawDlpPolicy $minimal } | Should -Not -Throw
            $result = ConvertTo-PpacDlpPolicyList -RawDlpPolicy $minimal
            $result[0].EnvironmentType | Should -Be 'OnlyEnvironments'
            $result[0].Environments -is [array] | Should -BeTrue
            $result[0].Environments[0].name | Should -Be 'env-guid'
            # Absent required/optional fields reach the scorer as null (fail closed), not fabricated.
            $result[0].PolicyName | Should -BeNullOrEmpty
            $result[0].IsEnabled | Should -BeNullOrEmpty
            $result[0].CreatedTime | Should -BeNullOrEmpty
        }

        It 'projects a policy with NO connectorGroups member as empty groups without throwing' {
            $noGroups = [PSCustomObject]@{
                displayName     = 'No Groups'
                name            = 'no-groups-1'
                environmentType = 'AllEnvironments'
                environments    = $null
                # connectorGroups, isEnabled, createdTime all absent
            }
            { ConvertTo-PpacDlpPolicyList -RawDlpPolicy $noGroups } | Should -Not -Throw
            $result = ConvertTo-PpacDlpPolicyList -RawDlpPolicy $noGroups
            $result[0].BusinessDataGroup | Should -BeNullOrEmpty
            $result[0].NonBusinessDataGroup | Should -BeNullOrEmpty
            $result[0].BlockedGroup | Should -BeNullOrEmpty
        }

        It 'still projects populated connectorGroups through the safe reads (regression)' {
            $withGroups = [PSCustomObject]@{
                displayName     = 'Grouped'
                name            = 'grouped-1'
                createdTime     = '2026-01-01T00:00:00Z'
                isEnabled       = $null
                connectorGroups = @(
                    [PSCustomObject]@{ classification = 'Confidential'; connectors = @([PSCustomObject]@{ id = 'shared_sql'; name = 'SQL Server' }) },
                    [PSCustomObject]@{ classification = 'General'; connectors = @([PSCustomObject]@{ id = 'shared_o365'; name = 'Office 365 Outlook' }) },
                    [PSCustomObject]@{ classification = 'Blocked'; connectors = @([PSCustomObject]@{ id = 'shared_twitter'; name = 'Twitter' }) }
                )
                environmentType = 'AllEnvironments'
                environments    = $null
            }
            $result = ConvertTo-PpacDlpPolicyList -RawDlpPolicy $withGroups
            $result[0].BusinessDataGroup.id | Should -Be 'shared_sql'
            $result[0].BusinessDataGroup.name | Should -Be 'SQL Server'
            $result[0].NonBusinessDataGroup.id | Should -Be 'shared_o365'
            $result[0].BlockedGroup.id | Should -Be 'shared_twitter'
        }

        It 'excludes a connector group with NO classification member without throwing' {
            $badGroup = [PSCustomObject]@{
                displayName     = 'Bad Group'
                name            = 'bad-group-1'
                isEnabled       = $null
                connectorGroups = @( [PSCustomObject]@{ connectors = @([PSCustomObject]@{ id = 'c1'; name = 'n1' }) } )
                environmentType = 'AllEnvironments'
                environments    = $null
            }
            { ConvertTo-PpacDlpPolicyList -RawDlpPolicy $badGroup } | Should -Not -Throw
            $result = ConvertTo-PpacDlpPolicyList -RawDlpPolicy $badGroup
            $result[0].BusinessDataGroup | Should -BeNullOrEmpty
            $result[0].NonBusinessDataGroup | Should -BeNullOrEmpty
            $result[0].BlockedGroup | Should -BeNullOrEmpty
        }
    }
}

Describe 'Invoke-CollectorOperation' {

    Context 'Execution-status reporting (Finding 1: skip vs successful zero rows)' {
        It 'runs the scriptblock, returns its output, and reports Executed' {
            $status = 'unset'
            $result = Invoke-CollectorOperation -Target 'tenant X' -Action 'List DLP policies' -ExecutionStatus ([ref]$status) -ScriptBlock { 'policy-output' }
            $result | Should -Be 'policy-output'
            $status | Should -Be 'Executed'
        }

        It 'reports Executed with $null output when a successful operation returns no rows' {
            # Mirrors Get-DlpPolicy on a no-policy tenant: the op ran, produced nothing.
            $status = 'unset'
            $result = Invoke-CollectorOperation -Target 'tenant X' -Action 'List DLP policies' -ExecutionStatus ([ref]$status) -ScriptBlock { }
            $status | Should -Be 'Executed'
            $result | Should -BeNullOrEmpty
        }

        It 'under -WhatIf returns $null, reports Skipped, and does NOT invoke the scriptblock' {
            $status = 'unset'
            $probe = [PSCustomObject]@{ Ran = $false }
            $sb = { $probe.Ran = $true; 'should-not-run' }.GetNewClosure()
            $result = Invoke-CollectorOperation -Target 'tenant X' -Action 'List DLP policies' -ExecutionStatus ([ref]$status) -ScriptBlock $sb -WhatIf
            $result | Should -BeNullOrEmpty
            $status | Should -Be 'Skipped'
            $probe.Ran | Should -BeFalse
        }

        It 'is backward compatible when -ExecutionStatus is omitted (normal run returns output)' {
            $result = Invoke-CollectorOperation -Target 'tenant X' -Action 'List DLP policies' -ScriptBlock { 'compat-output' }
            $result | Should -Be 'compat-output'
        }

        It 'is backward compatible when -ExecutionStatus is omitted (-WhatIf returns $null)' {
            $result = Invoke-CollectorOperation -Target 'tenant X' -Action 'List DLP policies' -ScriptBlock { 'x' } -WhatIf
            $result | Should -BeNullOrEmpty
        }
    }

    Context 'Section 2 decision contract: skip (unknown/null) is distinct from executed-no-row ([])' {
        # Reproduces exactly how Collect-PPAC.ps1 Section 2 consumes the status: only an
        # Executed status feeds ConvertTo-PpacDlpPolicyList; a Skipped status leaves
        # $dlpPolicies = $null so a dry-run/declined artifact scores as unknown (and still
        # counts toward the all-null total-failure exit), never as "No classic DLP policies".
        It 'executed-no-row yields [] (clean fail, scorer: No classic DLP policies found)' {
            $status = 'Skipped'
            $raw = Invoke-CollectorOperation -Target 'tenant X' -Action 'List DLP policies' -ExecutionStatus ([ref]$status) -ScriptBlock { }
            $dlpPolicies = $null
            if ($status -eq 'Executed') { $dlpPolicies = ConvertTo-PpacDlpPolicyList -RawDlpPolicy $raw }
            $status | Should -Be 'Executed'
            $dlpPolicies -is [array] | Should -BeTrue
            @($dlpPolicies).Count | Should -Be 0
        }

        It 'skip/-WhatIf leaves dlpPolicies $null (unknown), never []' {
            $status = 'Skipped'
            $raw = Invoke-CollectorOperation -Target 'tenant X' -Action 'List DLP policies' -ExecutionStatus ([ref]$status) -ScriptBlock { 'x' } -WhatIf
            $dlpPolicies = $null
            if ($status -eq 'Executed') { $dlpPolicies = ConvertTo-PpacDlpPolicyList -RawDlpPolicy $raw }
            $status | Should -Be 'Skipped'
            $dlpPolicies | Should -BeNullOrEmpty
        }
    }
}

Describe 'Get-PpacDlpProperty' {
    It 'returns the value of a present property' {
        $obj = [PSCustomObject]@{ isEnabled = $false; name = 'p1' }
        Get-PpacDlpProperty -InputObject $obj -Name 'name' | Should -Be 'p1'
        Get-PpacDlpProperty -InputObject $obj -Name 'isEnabled' | Should -Be $false
    }

    It 'returns $null for an absent property without throwing under StrictMode' {
        $obj = [PSCustomObject]@{ name = 'p1' }
        { Get-PpacDlpProperty -InputObject $obj -Name 'isEnabled' } | Should -Not -Throw
        Get-PpacDlpProperty -InputObject $obj -Name 'isEnabled' | Should -BeNullOrEmpty
    }

    It 'returns $null when the input object itself is $null' {
        Get-PpacDlpProperty -InputObject $null -Name 'anything' | Should -BeNullOrEmpty
    }

    It 'returns $null when a present property holds $null' {
        $obj = [PSCustomObject]@{ isEnabled = $null }
        Get-PpacDlpProperty -InputObject $obj -Name 'isEnabled' | Should -BeNullOrEmpty
    }

    Context 'Non-enumerating shape preservation (pr1040 empty-scope regression)' {
        # The reader must NOT enumerate its return value, or a present empty array
        # collapses to $null. Assign (never pipe) so an empty array is not swallowed
        # by the pipeline before Should sees it.

        It 'returns a PRESENT empty array as an empty array, not $null' {
            $obj = [PSCustomObject]@{ environments = @() }
            $result = Get-PpacDlpProperty -InputObject $obj -Name 'environments'
            $result -is [array] | Should -BeTrue
            @($result).Count | Should -Be 0
        }

        It 'preserves a single-element array as a one-element array (not collapsed to scalar)' {
            $obj = [PSCustomObject]@{ environments = @('env-a') }
            $result = Get-PpacDlpProperty -InputObject $obj -Name 'environments'
            $result -is [array] | Should -BeTrue
            @($result).Count | Should -Be 1
            $result[0] | Should -Be 'env-a'
        }

        It 'preserves a multi-element array' {
            $obj = [PSCustomObject]@{ environments = @('env-a', 'env-b') }
            $result = Get-PpacDlpProperty -InputObject $obj -Name 'environments'
            $result -is [array] | Should -BeTrue
            @($result).Count | Should -Be 2
        }

        It 'returns a scalar string as a scalar, not a one-element array' {
            $obj = [PSCustomObject]@{ name = 'p1' }
            $result = Get-PpacDlpProperty -InputObject $obj -Name 'name'
            $result -is [array] | Should -BeFalse
            $result | Should -Be 'p1'
        }

        It 'returns a scalar bool as a scalar, not a one-element array' {
            $obj = [PSCustomObject]@{ isEnabled = $false }
            $result = Get-PpacDlpProperty -InputObject $obj -Name 'isEnabled'
            $result -is [array] | Should -BeFalse
            $result | Should -Be $false
        }

        It 'returns a nested object as a scalar object, not wrapped in an array' {
            $env = [PSCustomObject]@{ id = 'x'; name = 'n' }
            $obj = [PSCustomObject]@{ environments = $env }
            $result = Get-PpacDlpProperty -InputObject $obj -Name 'environments'
            $result -is [array] | Should -BeFalse
            $result.name | Should -Be 'n'
        }
    }
}
