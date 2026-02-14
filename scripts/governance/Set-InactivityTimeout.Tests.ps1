#Requires -Version 7.0
#Requires -Modules Pester

<#
.SYNOPSIS
    Pester 5 test suite for Set-InactivityTimeout.ps1.

.DESCRIPTION
    Comprehensive tests validating the Set-InactivityTimeout.ps1 remediation script:
      - Parameter validation (mandatory, defaults, ranges)
      - BAP API interactions (GET, PATCH, error handling)
      - WhatIf support (preview without mutation)
      - Post-PATCH verification (GET-PATCH-GET pattern)
      - Result object structure and properties
      - Optional Dataverse audit record writing

    All BAP and Dataverse API calls are mocked via Mock Invoke-RestMethod.
    No external API calls are made during test execution.

    Test categories (6 Describe blocks, 27 tests):
      1. Parameter Validation (7 tests)
      2. BAP API Interactions (5 tests)
      3. WhatIf Support (3 tests)
      4. Verification (3 tests)
      5. Result Object (4 tests)
      6. Dataverse Audit Record (5 tests)

.NOTES
    Run: Invoke-Pester -Path ./scripts/governance/Set-InactivityTimeout.Tests.ps1 -Output Detailed
    Part of the FSI Agent Governance — Inactivity Timeout Enforcement (Control 2.22).
#>

BeforeAll {
    $script:scriptPath = Join-Path $PSScriptRoot 'Set-InactivityTimeout.ps1'

    # ── Stub for Get-AzAccessToken (not installed in test environment) ─
    if (-not (Get-Command 'Get-AzAccessToken' -ErrorAction SilentlyContinue)) {
        function global:Get-AzAccessToken {
            [CmdletBinding()]
            param([string]$ResourceUrl)
            throw 'Stub — should be mocked'
        }
    }

    # ── Shared mock data ──────────────────────────────────────────────

    # Mock access token object
    $script:mockTokenObject = [PSCustomObject]@{
        Token     = 'mock-access-token-12345'
        ExpiresOn = (Get-Date).AddHours(1)
    }

    $script:testEnvironmentName = 'e1234567-89ab-cdef-0123-456789abcdef'
    $script:testDataverseUrl    = 'https://org12345.crm.dynamics.com'

    # Privacy settings response — timeout DISABLED (before remediation)
    $script:mockPrivacyDisabled = @{
        properties = @{
            InactivityTimeoutEnabled   = $false
            InactivityTimeoutInMinutes = $null
            InactivityWarningInMinutes = $null
        }
    }

    # Privacy settings response — timeout ENABLED at 120/5 (after remediation with defaults)
    $script:mockPrivacyEnabled = @{
        properties = @{
            InactivityTimeoutEnabled   = $true
            InactivityTimeoutInMinutes = 120
            InactivityWarningInMinutes = 5
        }
    }

    # Privacy settings response — custom config at 60/10
    $script:mockPrivacyCustom = @{
        properties = @{
            InactivityTimeoutEnabled   = $true
            InactivityTimeoutInMinutes = 60
            InactivityWarningInMinutes = 10
        }
    }

    # Dataverse POST response (audit record created)
    $script:mockDataverseResponse = @{
        fsi_inactivitytimeout_complianceid = '00000000-aaaa-bbbb-cccc-111111111111'
        fsi_environmentid                  = $script:testEnvironmentName
        fsi_compliancestatus               = 0
    }
}

# ═══════════════════════════════════════════════════════════════════════
# Category 1: Parameter Validation
# ═══════════════════════════════════════════════════════════════════════

Describe 'Parameter Validation' {
    BeforeAll {
        $script:cmdInfo = Get-Command $script:scriptPath
    }

    It 'EnvironmentName is mandatory' {
        $param = $script:cmdInfo.Parameters['EnvironmentName']
        $param.Attributes | Where-Object { $_ -is [System.Management.Automation.ParameterAttribute] } |
            ForEach-Object { $_.Mandatory | Should -BeTrue }
    }

    It 'TimeoutDuration defaults to 120' {
        $param = $script:cmdInfo.Parameters['TimeoutDuration']
        $param.ParameterType.Name | Should -Be 'Int32'
        # Default is set in param block, verify via AST
        $ast = [System.Management.Automation.Language.Parser]::ParseFile($script:scriptPath, [ref]$null, [ref]$null)
        $paramBlock = $ast.ParamBlock
        $tdParam = $paramBlock.Parameters | Where-Object { $_.Name.VariablePath.UserPath -eq 'TimeoutDuration' }
        $tdParam.DefaultValue.Value | Should -Be 120
    }

    It 'TimeoutDuration rejects value below 5' {
        { & $script:scriptPath -EnvironmentName $script:testEnvironmentName -TimeoutDuration 2 -Confirm:$false 2>$null } |
            Should -Throw
    }

    It 'TimeoutDuration rejects value above 120' {
        { & $script:scriptPath -EnvironmentName $script:testEnvironmentName -TimeoutDuration 200 -Confirm:$false 2>$null } |
            Should -Throw
    }

    It 'WarningDuration defaults to 5' {
        $ast = [System.Management.Automation.Language.Parser]::ParseFile($script:scriptPath, [ref]$null, [ref]$null)
        $paramBlock = $ast.ParamBlock
        $wdParam = $paramBlock.Parameters | Where-Object { $_.Name.VariablePath.UserPath -eq 'WarningDuration' }
        $wdParam.DefaultValue.Value | Should -Be 5
    }

    It 'WarningDuration rejects value below 1' {
        { & $script:scriptPath -EnvironmentName $script:testEnvironmentName -WarningDuration 0 -Confirm:$false 2>$null } |
            Should -Throw
    }

    It 'WarningDuration rejects value above 30' {
        { & $script:scriptPath -EnvironmentName $script:testEnvironmentName -WarningDuration 50 -Confirm:$false 2>$null } |
            Should -Throw
    }
}

# ═══════════════════════════════════════════════════════════════════════
# Category 2: BAP API Interactions
# ═══════════════════════════════════════════════════════════════════════

Describe 'BAP API Interactions' {
    BeforeAll {
        Mock Get-AzAccessToken { [PSCustomObject]@{ Token = 'mock-bap-token' } }

        # GET returns disabled state first, then enabled state for verification
        $script:getCallCount = 0
        Mock Invoke-RestMethod -ParameterFilter { $Method -ne 'Patch' } -MockWith {
            $script:getCallCount++
            if ($script:getCallCount -le 1) {
                return @{ properties = @{ InactivityTimeoutEnabled = $false; InactivityTimeoutInMinutes = $null; InactivityWarningInMinutes = $null } }
            }
            return @{ properties = @{ InactivityTimeoutEnabled = $true; InactivityTimeoutInMinutes = 120; InactivityWarningInMinutes = 5 } }
        }

        # PATCH returns success
        Mock Invoke-RestMethod -ParameterFilter { $Method -eq 'Patch' } -MockWith {
            @{ properties = @{ InactivityTimeoutEnabled = $true; InactivityTimeoutInMinutes = 120; InactivityWarningInMinutes = 5 } }
        }
    }

    BeforeEach {
        $script:getCallCount = 0
    }

    It 'Calls GET privacy settings with correct URL' {
        & $script:scriptPath -EnvironmentName $script:testEnvironmentName -Confirm:$false | Out-Null
        Should -Invoke Invoke-RestMethod -ParameterFilter {
            $Uri -like "*$($script:testEnvironmentName)*/settings/privacy*"  -and $Method -ne 'Patch'
        } -Times 2 -Exactly -Scope It
    }

    It 'Calls PATCH with correct body properties' {
        & $script:scriptPath -EnvironmentName $script:testEnvironmentName -TimeoutDuration 60 -WarningDuration 10 -Confirm:$false | Out-Null
        Should -Invoke Invoke-RestMethod -ParameterFilter {
            $Method -eq 'Patch' -and
            $Body -like '*InactivityTimeoutEnabled*' -and
            $Body -like '*60*' -and
            $Body -like '*10*'
        } -Times 1 -Exactly -Scope It
    }

    Context 'Error handling' {
        It 'Handles 404 with environment not found error' {
            Mock Invoke-RestMethod -ParameterFilter { $Method -ne 'Patch' } -MockWith {
                $ex = [System.Net.Http.HttpRequestException]::new('Not Found')
                $response = [System.Net.Http.HttpResponseMessage]::new([System.Net.HttpStatusCode]::NotFound)
                $errorRecord = [System.Management.Automation.ErrorRecord]::new($ex, 'WebCmdletWebResponseException', 'InvalidOperation', $null)
                $errorRecord.ErrorDetails = [System.Management.Automation.ErrorDetails]::new('{"error":{"code":"EnvironmentNotFound"}}')
                # Attach response to exception for status code extraction
                $ex | Add-Member -NotePropertyName 'Response' -NotePropertyValue $response -Force
                throw $errorRecord
            }
            { & $script:scriptPath -EnvironmentName 'invalid-env-name' -Confirm:$false } | Should -Throw
        }

        It 'Handles 401 with auth guidance' {
            Mock Invoke-RestMethod -ParameterFilter { $Method -ne 'Patch' } -MockWith {
                $ex = [System.Net.Http.HttpRequestException]::new('Unauthorized')
                $response = [System.Net.Http.HttpResponseMessage]::new([System.Net.HttpStatusCode]::Unauthorized)
                $ex | Add-Member -NotePropertyName 'Response' -NotePropertyValue $response -Force
                $errorRecord = [System.Management.Automation.ErrorRecord]::new($ex, 'WebCmdletWebResponseException', 'InvalidOperation', $null)
                throw $errorRecord
            }
            { & $script:scriptPath -EnvironmentName $script:testEnvironmentName -Confirm:$false } | Should -Throw -ExceptionType ([System.Exception])
        }

        It 'Handles 403 with permission guidance' {
            Mock Invoke-RestMethod -ParameterFilter { $Method -ne 'Patch' } -MockWith {
                $ex = [System.Net.Http.HttpRequestException]::new('Forbidden')
                $response = [System.Net.Http.HttpResponseMessage]::new([System.Net.HttpStatusCode]::Forbidden)
                $ex | Add-Member -NotePropertyName 'Response' -NotePropertyValue $response -Force
                $errorRecord = [System.Management.Automation.ErrorRecord]::new($ex, 'WebCmdletWebResponseException', 'InvalidOperation', $null)
                throw $errorRecord
            }
            { & $script:scriptPath -EnvironmentName $script:testEnvironmentName -Confirm:$false } | Should -Throw -ExceptionType ([System.Exception])
        }
    }
}

# ═══════════════════════════════════════════════════════════════════════
# Category 3: WhatIf Support
# ═══════════════════════════════════════════════════════════════════════

Describe 'WhatIf Support' {
    BeforeAll {
        Mock Get-AzAccessToken { [PSCustomObject]@{ Token = 'mock-bap-token' } }

        Mock Invoke-RestMethod -ParameterFilter { $Method -ne 'Patch' } -MockWith {
            @{ properties = @{ InactivityTimeoutEnabled = $false; InactivityTimeoutInMinutes = $null; InactivityWarningInMinutes = $null } }
        }

        Mock Invoke-RestMethod -ParameterFilter { $Method -eq 'Patch' } -MockWith {
            @{ properties = @{ InactivityTimeoutEnabled = $true; InactivityTimeoutInMinutes = 120; InactivityWarningInMinutes = 5 } }
        }
    }

    It '-WhatIf does NOT invoke PATCH' {
        & $script:scriptPath -EnvironmentName $script:testEnvironmentName -WhatIf | Out-Null
        Should -Not -Invoke Invoke-RestMethod -ParameterFilter { $Method -eq 'Patch' }
    }

    It '-WhatIf still executes GET (read-only)' {
        & $script:scriptPath -EnvironmentName $script:testEnvironmentName -WhatIf | Out-Null
        Should -Invoke Invoke-RestMethod -ParameterFilter { $Method -ne 'Patch' } -Times 1 -Exactly
    }

    It '-WhatIf returns result with Applied = $false' {
        $result = & $script:scriptPath -EnvironmentName $script:testEnvironmentName -WhatIf
        $result.Applied | Should -BeFalse
    }
}

# ═══════════════════════════════════════════════════════════════════════
# Category 4: Verification
# ═══════════════════════════════════════════════════════════════════════

Describe 'Verification' {
    BeforeAll {
        Mock Get-AzAccessToken { [PSCustomObject]@{ Token = 'mock-bap-token' } }
    }

    It 'Re-reads settings after PATCH (GET called at least twice)' {
        $script:getCallCount = 0
        Mock Invoke-RestMethod -ParameterFilter { $Method -ne 'Patch' } -MockWith {
            $script:getCallCount++
            if ($script:getCallCount -le 1) { return @{ properties = @{ InactivityTimeoutEnabled = $false; InactivityTimeoutInMinutes = $null; InactivityWarningInMinutes = $null } } }
            return @{ properties = @{ InactivityTimeoutEnabled = $true; InactivityTimeoutInMinutes = 120; InactivityWarningInMinutes = 5 } }
        }
        Mock Invoke-RestMethod -ParameterFilter { $Method -eq 'Patch' } -MockWith { @{ properties = @{ InactivityTimeoutEnabled = $true; InactivityTimeoutInMinutes = 120; InactivityWarningInMinutes = 5 } } }

        & $script:scriptPath -EnvironmentName $script:testEnvironmentName -Confirm:$false | Out-Null
        Should -Invoke Invoke-RestMethod -ParameterFilter { $Method -ne 'Patch' } -Times 2 -Exactly
    }

    It 'Sets Verified = $true when post-PATCH values match' {
        $script:getCallCount = 0
        Mock Invoke-RestMethod -ParameterFilter { $Method -ne 'Patch' } -MockWith {
            $script:getCallCount++
            if ($script:getCallCount -le 1) { return @{ properties = @{ InactivityTimeoutEnabled = $false; InactivityTimeoutInMinutes = $null; InactivityWarningInMinutes = $null } } }
            return @{ properties = @{ InactivityTimeoutEnabled = $true; InactivityTimeoutInMinutes = 120; InactivityWarningInMinutes = 5 } }
        }
        Mock Invoke-RestMethod -ParameterFilter { $Method -eq 'Patch' } -MockWith { @{ properties = @{ InactivityTimeoutEnabled = $true; InactivityTimeoutInMinutes = 120; InactivityWarningInMinutes = 5 } } }

        $result = & $script:scriptPath -EnvironmentName $script:testEnvironmentName -Confirm:$false
        $result.Verified | Should -BeTrue
    }

    It 'Sets Verified = $false when post-PATCH values differ' {
        $script:getCallCount = 0
        Mock Invoke-RestMethod -ParameterFilter { $Method -ne 'Patch' } -MockWith {
            $script:getCallCount++
            if ($script:getCallCount -le 1) { return @{ properties = @{ InactivityTimeoutEnabled = $false; InactivityTimeoutInMinutes = $null; InactivityWarningInMinutes = $null } } }
            # Return mismatched values (timeout=90 instead of expected 120)
            return @{
                properties = @{
                    InactivityTimeoutEnabled   = $true
                    InactivityTimeoutInMinutes = 90
                    InactivityWarningInMinutes = 5
                }
            }
        }
        Mock Invoke-RestMethod -ParameterFilter { $Method -eq 'Patch' } -MockWith { @{ properties = @{ InactivityTimeoutEnabled = $true; InactivityTimeoutInMinutes = 120; InactivityWarningInMinutes = 5 } } }

        $result = & $script:scriptPath -EnvironmentName $script:testEnvironmentName -Confirm:$false 3>$null
        $result.Verified | Should -BeFalse
    }
}

# ═══════════════════════════════════════════════════════════════════════
# Category 5: Result Object
# ═══════════════════════════════════════════════════════════════════════

Describe 'Result Object' {
    BeforeAll {
        Mock Get-AzAccessToken { [PSCustomObject]@{ Token = 'mock-bap-token' } }

        $script:getCallCount = 0
        Mock Invoke-RestMethod -ParameterFilter { $Method -ne 'Patch' } -MockWith {
            $script:getCallCount++
            if ($script:getCallCount -le 1) {
                return @{ properties = @{ InactivityTimeoutEnabled = $false; InactivityTimeoutInMinutes = $null; InactivityWarningInMinutes = $null } }
            }
            return @{ properties = @{ InactivityTimeoutEnabled = $true; InactivityTimeoutInMinutes = 120; InactivityWarningInMinutes = 5 } }
        }
        Mock Invoke-RestMethod -ParameterFilter { $Method -eq 'Patch' } -MockWith {
            @{ properties = @{ InactivityTimeoutEnabled = $true; InactivityTimeoutInMinutes = 120; InactivityWarningInMinutes = 5 } }
        }
    }

    BeforeEach {
        $script:getCallCount = 0
    }

    It 'Returns PSCustomObject with expected properties' {
        $result = & $script:scriptPath -EnvironmentName $script:testEnvironmentName -Confirm:$false
        $result.PSObject.Properties.Name | Should -Contain 'Metadata'
        $result.PSObject.Properties.Name | Should -Contain 'Applied'
        $result.PSObject.Properties.Name | Should -Contain 'PreviousConfig'
        $result.PSObject.Properties.Name | Should -Contain 'NewConfig'
        $result.PSObject.Properties.Name | Should -Contain 'Verified'
        $result.PSObject.Properties.Name | Should -Contain 'AuditRecord'
    }

    It 'PreviousConfig captures pre-PATCH state' {
        $result = & $script:scriptPath -EnvironmentName $script:testEnvironmentName -Confirm:$false
        $result.PreviousConfig.InactivityTimeoutEnabled | Should -BeFalse
    }

    It 'NewConfig captures post-PATCH state' {
        $result = & $script:scriptPath -EnvironmentName $script:testEnvironmentName -Confirm:$false
        $result.NewConfig.InactivityTimeoutEnabled | Should -BeTrue
        $result.NewConfig.InactivityTimeoutInMinutes | Should -Be 120
    }

    It 'Metadata includes EnvironmentName' {
        $result = & $script:scriptPath -EnvironmentName $script:testEnvironmentName -Confirm:$false
        $result.Metadata.EnvironmentName | Should -Be $script:testEnvironmentName
    }
}

# ═══════════════════════════════════════════════════════════════════════
# Category 6: Dataverse Audit Record
# ═══════════════════════════════════════════════════════════════════════

Describe 'Dataverse Audit Record' {
    BeforeAll {
        Mock Get-AzAccessToken { [PSCustomObject]@{ Token = 'mock-bap-token' } }
    }

    Context 'Without -DataverseUrl' {
        BeforeAll {
            $script:getCallCount = 0
            Mock Invoke-RestMethod -ParameterFilter { $Method -ne 'Patch' -and $Uri -notlike '*crm.dynamics.com*' } -MockWith {
                $script:getCallCount++
                if ($script:getCallCount -le 1) {
                    return @{ properties = @{ InactivityTimeoutEnabled = $false; InactivityTimeoutInMinutes = $null; InactivityWarningInMinutes = $null } }
                }
                return @{ properties = @{ InactivityTimeoutEnabled = $true; InactivityTimeoutInMinutes = 120; InactivityWarningInMinutes = 5 } }
            }
            Mock Invoke-RestMethod -ParameterFilter { $Method -eq 'Patch' } -MockWith {
                @{ properties = @{ InactivityTimeoutEnabled = $true; InactivityTimeoutInMinutes = 120; InactivityWarningInMinutes = 5 } }
            }
        }

        BeforeEach {
            $script:getCallCount = 0
        }

        It 'Does not attempt Dataverse write' {
            & $script:scriptPath -EnvironmentName $script:testEnvironmentName -Confirm:$false | Out-Null
            Should -Not -Invoke Invoke-RestMethod -ParameterFilter { $Uri -like '*crm.dynamics.com*' }
        }
    }

    Context 'With -DataverseUrl' {
        BeforeAll {
            $script:getCallCount = 0
            Mock Invoke-RestMethod -ParameterFilter { $Method -ne 'Patch' -and $Uri -like '*api.bap.microsoft.com*' } -MockWith {
                $script:getCallCount++
                if ($script:getCallCount -le 1) {
                    return @{ properties = @{ InactivityTimeoutEnabled = $false; InactivityTimeoutInMinutes = $null; InactivityWarningInMinutes = $null } }
                }
                return @{ properties = @{ InactivityTimeoutEnabled = $true; InactivityTimeoutInMinutes = 120; InactivityWarningInMinutes = 5 } }
            }
            Mock Invoke-RestMethod -ParameterFilter { $Method -eq 'Patch' -and $Uri -like '*api.bap.microsoft.com*' } -MockWith {
                @{ properties = @{ InactivityTimeoutEnabled = $true; InactivityTimeoutInMinutes = 120; InactivityWarningInMinutes = 5 } }
            }

            Mock Invoke-RestMethod -ParameterFilter { $Uri -like '*crm.dynamics.com*' } -MockWith {
                @{
                    fsi_inactivitytimeout_complianceid = '00000000-aaaa-bbbb-cccc-111111111111'
                    fsi_environmentid                  = 'e1234567-89ab-cdef-0123-456789abcdef'
                    fsi_compliancestatus               = 0
                }
            }
        }

        BeforeEach {
            $script:getCallCount = 0
        }

        It 'Writes compliance record to Dataverse' {
            & $script:scriptPath -EnvironmentName $script:testEnvironmentName -DataverseUrl $script:testDataverseUrl -Confirm:$false | Out-Null
            Should -Invoke Invoke-RestMethod -ParameterFilter {
                $Uri -like '*crm.dynamics.com*/api/data/v9.2/fsi_inactivitytimeoutcompliances*'
            } -Times 1 -Exactly
        }

        It 'Audit record contains before/after values in notes' {
            & $script:scriptPath -EnvironmentName $script:testEnvironmentName -DataverseUrl $script:testDataverseUrl -Confirm:$false | Out-Null
            Should -Invoke Invoke-RestMethod -ParameterFilter {
                $Uri -like '*crm.dynamics.com*' -and
                $Body -like '*Before:*' -and
                $Body -like '*After:*'
            } -Times 1 -Exactly
        }

        It 'Audit record contains timestamp' {
            & $script:scriptPath -EnvironmentName $script:testEnvironmentName -DataverseUrl $script:testDataverseUrl -Confirm:$false | Out-Null
            Should -Invoke Invoke-RestMethod -ParameterFilter {
                $Uri -like '*crm.dynamics.com*' -and
                $Body -like '*fsi_lastscandate*'
            } -Times 1 -Exactly
        }

        It 'Dataverse write failure does not block result' {
            Mock Invoke-RestMethod -ParameterFilter { $Uri -like '*crm.dynamics.com*' } -MockWith {
                throw 'Simulated Dataverse API error'
            }

            $result = & $script:scriptPath -EnvironmentName $script:testEnvironmentName -DataverseUrl $script:testDataverseUrl -Confirm:$false 3>$null
            $result.Applied | Should -BeTrue
            $result.AuditRecord | Should -BeNullOrEmpty
        }
    }
}
