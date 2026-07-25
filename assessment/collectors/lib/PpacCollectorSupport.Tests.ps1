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
}
