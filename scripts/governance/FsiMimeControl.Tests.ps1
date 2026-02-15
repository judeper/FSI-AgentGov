#Requires -Version 7.0
#Requires -Modules Pester

<#
.SYNOPSIS
    Pester 5 test suite for FsiMimeControl PowerShell module.

.DESCRIPTION
    Comprehensive tests covering all 5 exported functions:
      - Connect-FsiMimeDataverse / Get-FsiMimeConnection
      - Get-FsiMimeConfig
      - Set-FsiMimeConfig (including WhatIf)
      - Test-FsiMimeCompliance (Zone 1/2/3 scenarios)

    All Dataverse API calls are mocked via Mock Invoke-RestMethod.
    No external API calls are made during test execution.

    Test categories (6 Describe blocks, ~32 tests):
      1. Module Loading (3 tests)
      2. Zone Templates (6 tests)
      3. Get-FsiMimeConfig (5 tests)
      4. Set-FsiMimeConfig (6 tests)
      5. Test-FsiMimeCompliance (8 tests)
      6. Connection Management (4 tests)

.NOTES
    Run: Invoke-Pester -Path ./scripts/governance/FsiMimeControl.Tests.ps1 -Output Detailed
    Part of the FSI Agent Governance — MIME Type Restrictions (Control 1.25).
#>

BeforeAll {
    # Import the module under test
    Import-Module (Join-Path $PSScriptRoot 'FsiMimeControl.psm1') -Force

    # ── Shared mock data ──────────────────────────────────────────────

    # Full Organization entity response with blocked extensions and MIME types
    $script:mockOrgResponse = @{
        value = @(
            @{
                organizationid      = '00000000-0000-0000-0000-000000000001'
                blockedattachments  = 'ade;adp;app;asa;asp;bat;cdx;cmd;com;cpl;crt;csh;dll;exe;hta;inf;ins;jar;js;jse;lnk;mda;mdb;mde;msc;msi;msp;mst;pcd;pif;reg;scr;sct;shb;shs;tmp;url;vb;vbe;vbs;ws;wsc;wsf;wsh'
                blockedmimetypes    = 'application/x-msdownload;application/x-msdos-program;application/x-bat;application/x-cmd;application/x-vbs;application/javascript;application/x-javascript;text/javascript;application/x-powershell;application/x-msi;application/hta;application/msaccess;text/scriptlet;application/xml;application/prg'
            }
        )
    }

    # Organization entity with empty/null attachment and MIME fields
    $script:mockOrgResponseEmpty = @{
        value = @(
            @{
                organizationid      = '00000000-0000-0000-0000-000000000002'
                blockedattachments  = $null
                blockedmimetypes    = $null
            }
        )
    }

    # Organization entity with blocked extensions but no MIME types
    $script:mockOrgResponsePartial = @{
        value = @(
            @{
                organizationid      = '00000000-0000-0000-0000-000000000003'
                blockedattachments  = 'exe;bat;cmd;dll'
                blockedmimetypes    = $null
            }
        )
    }

    # Full Zone 2 compliant response (extensions + MIME types)
    $script:mockOrgResponseZone2 = @{
        value = @(
            @{
                organizationid      = '00000000-0000-0000-0000-000000000004'
                blockedattachments  = 'ade;adp;app;asa;asp;bat;cdx;cmd;com;cpl;crt;csh;dll;exe;hta;inf;ins;jar;js;jse;lnk;mda;mdb;mde;msc;msi;msp;mst;pcd;pif;ps1;reg;scr;sct;shb;shs;tmp;url;vb;vbe;vbs;ws;wsc;wsf;wsh'
                blockedmimetypes    = 'application/x-msdownload;application/x-msdos-program;application/x-bat;application/x-cmd;application/x-vbs;application/javascript;application/x-javascript;text/javascript;application/x-powershell;application/x-msi;application/hta;application/msaccess;text/scriptlet;application/xml;application/prg'
            }
        )
    }

    # Full Zone 3 compliant response(extensions + MIME + allowlist)
    $script:mockOrgResponseZone3 = @{
        value = @(
            @{
                organizationid      = '00000000-0000-0000-0000-000000000005'
                blockedattachments  = 'ade;adp;app;asa;asp;bat;cab;cdx;cmd;com;cpl;crt;csh;dll;exe;gadget;hta;inf;ins;isp;its;jar;js;jse;lnk;mda;mdb;mde;msc;msi;msp;mst;pcd;pif;ps1;ps1xml;ps2;ps2xml;psc1;psc2;reg;rgs;scr;sct;shb;shs;tmp;url;vb;vbe;vbs;ws;wsc;wsf;wsh'
                blockedmimetypes    = 'application/x-msdownload;application/x-msdos-program;application/x-bat;application/x-cmd;application/x-vbs;application/javascript;application/x-javascript;text/javascript;application/x-powershell;application/x-msi;application/hta;application/msaccess;text/scriptlet;application/xml;application/prg;application/x-shellscript;application/x-sh;application/x-csh;application/java-archive;application/x-ms-shortcut;text/xml'
                allowedmimetypes    = 'application/pdf;image/png;image/jpeg;image/gif;image/tiff;text/plain;text/csv;application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;application/vnd.openxmlformats-officedocument.wordprocessingml.document;application/vnd.openxmlformats-officedocument.presentationml.presentation'
            }
        )
    }

    # Mock access token
    $script:mockToken = [PSCustomObject]@{
        Token     = 'mock-access-token-12345'
        ExpiresOn = (Get-Date).AddHours(1)
    }

    # Standard test parameters
    $script:testUrl   = 'https://orgtest.crm.dynamics.com'
    $script:testToken = 'mock-access-token-12345'
}

# ═══════════════════════════════════════════════════════════════════════
# Category 1: Module Loading
# ═══════════════════════════════════════════════════════════════════════

Describe 'Module Loading' {
    It 'Imports without error' {
        { Import-Module (Join-Path $PSScriptRoot 'FsiMimeControl.psm1') -Force } | Should -Not -Throw
    }

    It 'Exports expected cmdlets (5 functions)' {
        $commands = Get-Command -Module FsiMimeControl
        $commands | Should -HaveCount 5
        $commands.Name | Should -Contain 'Connect-FsiMimeDataverse'
        $commands.Name | Should -Contain 'Get-FsiMimeConnection'
        $commands.Name | Should -Contain 'Get-FsiMimeConfig'
        $commands.Name | Should -Contain 'Set-FsiMimeConfig'
        $commands.Name | Should -Contain 'Test-FsiMimeCompliance'
    }

    It 'Has #Requires -Version 7.0' {
        $moduleContent = Get-Content (Join-Path $PSScriptRoot 'FsiMimeControl.psm1') -Raw
        $moduleContent | Should -Match '#Requires -Version 7\.0'
    }
}

# ═══════════════════════════════════════════════════════════════════════
# Category 2: Zone Template Loading
# ═══════════════════════════════════════════════════════════════════════

Describe 'Zone Templates' {
    BeforeAll {
        $script:templateDir = Join-Path $PSScriptRoot 'mime-templates'
    }

    It 'zone1.json loads and has valid schema' {
        $path = Join-Path $script:templateDir 'zone1.json'
        $zone1 = Get-Content $path -Raw | ConvertFrom-Json
        $zone1.templateVersion | Should -Not -BeNullOrEmpty
        $zone1.zone | Should -Be 1
        $zone1.zoneName | Should -Be 'Personal Productivity'
        $zone1.PSObject.Properties.Name | Should -Contain 'blockedExtensions'
        $zone1.PSObject.Properties.Name | Should -Contain 'blockedMimeTypes'
        $zone1.PSObject.Properties.Name | Should -Contain 'allowedMimeTypes'
        $zone1.PSObject.Properties.Name | Should -Contain 'flags'
        $zone1.PSObject.Properties.Name | Should -Contain 'metadata'
    }

    It 'zone2.json loads and has valid schema' {
        $path = Join-Path $script:templateDir 'zone2.json'
        $zone2 = Get-Content $path -Raw | ConvertFrom-Json
        $zone2.templateVersion | Should -Not -BeNullOrEmpty
        $zone2.zone | Should -Be 2
        $zone2.zoneName | Should -Be 'Team Collaboration'
        $zone2.PSObject.Properties.Name | Should -Contain 'blockedExtensions'
        $zone2.PSObject.Properties.Name | Should -Contain 'blockedMimeTypes'
        $zone2.PSObject.Properties.Name | Should -Contain 'allowedMimeTypes'
        $zone2.PSObject.Properties.Name | Should -Contain 'flags'
        $zone2.PSObject.Properties.Name | Should -Contain 'metadata'
    }

    It 'zone3.json loads and has valid schema' {
        $path = Join-Path $script:templateDir 'zone3.json'
        $zone3 = Get-Content $path -Raw | ConvertFrom-Json
        $zone3.templateVersion | Should -Not -BeNullOrEmpty
        $zone3.zone | Should -Be 3
        $zone3.zoneName | Should -Be 'Enterprise Managed'
        $zone3.PSObject.Properties.Name | Should -Contain 'blockedExtensions'
        $zone3.PSObject.Properties.Name | Should -Contain 'blockedMimeTypes'
        $zone3.PSObject.Properties.Name | Should -Contain 'allowedMimeTypes'
        $zone3.PSObject.Properties.Name | Should -Contain 'flags'
        $zone3.PSObject.Properties.Name | Should -Contain 'metadata'
    }

    It 'Zone 2 has more blocked MIME types than Zone 1' {
        $z1 = Get-Content (Join-Path $script:templateDir 'zone1.json') -Raw | ConvertFrom-Json
        $z2 = Get-Content (Join-Path $script:templateDir 'zone2.json') -Raw | ConvertFrom-Json
        $z2.blockedMimeTypes.Count | Should -BeGreaterThan $z1.blockedMimeTypes.Count
    }

    It 'Zone 3 has more blocked extensions than Zone 2' {
        $z2 = Get-Content (Join-Path $script:templateDir 'zone2.json') -Raw | ConvertFrom-Json
        $z3 = Get-Content (Join-Path $script:templateDir 'zone3.json') -Raw | ConvertFrom-Json
        $z3.blockedExtensions.Count | Should -BeGreaterThan $z2.blockedExtensions.Count
    }

    It 'Zone 3 flags are all true' {
        $z3 = Get-Content (Join-Path $script:templateDir 'zone3.json') -Raw | ConvertFrom-Json
        $z3.flags.requireServerSideValidation | Should -BeTrue
        $z3.flags.requireDlpIntegration | Should -BeTrue
        $z3.flags.requireSentinelMonitoring | Should -BeTrue
    }
}

# ═══════════════════════════════════════════════════════════════════════
# Category 3: Get-FsiMimeConfig
# ═══════════════════════════════════════════════════════════════════════

Describe 'Get-FsiMimeConfig' {
    BeforeAll {
        Mock Invoke-RestMethod { $script:mockOrgResponse } -ModuleName FsiMimeControl
    }

    It 'Returns PSCustomObject with expected properties' {
        $result = Get-FsiMimeConfig -DataverseUrl $script:testUrl -AccessToken $script:testToken
        $result | Should -BeOfType [PSCustomObject]
        $result.PSObject.Properties.Name | Should -Contain 'DataverseUrl'
        $result.PSObject.Properties.Name | Should -Contain 'OrganizationId'
        $result.PSObject.Properties.Name | Should -Contain 'BlockedExtensions'
        $result.PSObject.Properties.Name | Should -Contain 'BlockedMimeTypes'
    }

    It 'Parses semicolon-separated blockedattachments into array' {
        $result = Get-FsiMimeConfig -DataverseUrl $script:testUrl -AccessToken $script:testToken
        $result.BlockedExtensions | Should -BeOfType [string]
        $result.BlockedExtensions | Should -Contain 'exe'
        $result.BlockedExtensions | Should -Contain 'bat'
        $result.BlockedExtensions | Should -Contain 'dll'
    }

    It 'Parses semicolon-separated blockedmimetypes into array' {
        $result = Get-FsiMimeConfig -DataverseUrl $script:testUrl -AccessToken $script:testToken
        $result.BlockedMimeTypes | Should -Contain 'application/x-msdownload'
        $result.BlockedMimeTypes | Should -Contain 'application/javascript'
    }

    Context 'Empty fields' {
        BeforeAll {
            Mock Invoke-RestMethod { $script:mockOrgResponseEmpty } -ModuleName FsiMimeControl
        }

        It 'Returns empty arrays for null/empty fields' {
            $result = Get-FsiMimeConfig -DataverseUrl $script:testUrl -AccessToken $script:testToken
            $result.BlockedExtensions | Should -HaveCount 0
            $result.BlockedMimeTypes | Should -HaveCount 0
        }
    }

    Context 'API error' {
        BeforeAll {
            Mock Invoke-RestMethod { throw 'Simulated API error' } -ModuleName FsiMimeControl
        }

        It 'Handles API error with exception' {
            { Get-FsiMimeConfig -DataverseUrl $script:testUrl -AccessToken $script:testToken } | Should -Throw '*Failed to query*'
        }
    }

    Context 'Table output' {
        BeforeAll {
            Mock Invoke-RestMethod { $script:mockOrgResponse } -ModuleName FsiMimeControl
        }

        It '-OutputFormat Table returns result object to pipeline' {
            $result = Get-FsiMimeConfig -DataverseUrl $script:testUrl -AccessToken $script:testToken -OutputFormat Table 6>&1
            ($result | Where-Object { $_ -is [PSCustomObject] -and $_.OrganizationId }).OrganizationId | Should -Be '00000000-0000-0000-0000-000000000001'
        }
    }
}

# ═══════════════════════════════════════════════════════════════════════
# Category 4: Set-FsiMimeConfig
# ═══════════════════════════════════════════════════════════════════════

Describe 'Set-FsiMimeConfig' {
    BeforeAll {
        # Mock GET requests (for Get-FsiMimeConfig calls within Set-FsiMimeConfig)
        Mock Invoke-RestMethod -ParameterFilter { $Method -eq 'Get' -or -not $Method } -MockWith {
            $script:mockOrgResponse
        } -ModuleName FsiMimeControl

        # Mock PATCH requests
        Mock Invoke-RestMethod -ParameterFilter { $Method -eq 'Patch' } -MockWith {
            $null
        } -ModuleName FsiMimeControl
    }

    It '-WhatIf does NOT invoke Patch' {
        Set-FsiMimeConfig -DataverseUrl $script:testUrl -AccessToken $script:testToken -ZoneTemplate zone1 -WhatIf
        Should -Not -Invoke Invoke-RestMethod -ParameterFilter { $Method -eq 'Patch' } -ModuleName FsiMimeControl
    }

    It '-WhatIf outputs planned changes visible without -Verbose' {
        $output = Set-FsiMimeConfig -DataverseUrl $script:testUrl -AccessToken $script:testToken -ZoneTemplate zone2 -WhatIf 6>&1
        $hostText = ($output | Where-Object { $_ -is [System.Management.Automation.InformationRecord] }).MessageData -join ' '
        # WhatIf uses Write-Host so content shows on the information stream
        ($output | Out-String) | Should -Match 'WhatIf'
    }

    It 'Template mode loads correct zone file' {
        # Reset the PATCH mock to capture body
        $script:capturedBody = $null
        Mock Invoke-RestMethod -ParameterFilter { $Method -eq 'Patch' } -MockWith {
            $script:capturedBody = $Body
            $script:mockOrgResponse
        } -ModuleName FsiMimeControl

        Set-FsiMimeConfig -DataverseUrl $script:testUrl -AccessToken $script:testToken -ZoneTemplate zone2
        $script:capturedBody | Should -Not -BeNullOrEmpty
        $bodyObj = $script:capturedBody | ConvertFrom-Json
        # Zone 2 should have ps1 in blocked extensions
        $bodyObj.blockedattachments | Should -Match 'ps1'
    }

    It 'Custom mode accepts individual arrays' {
        $script:capturedBody = $null
        Mock Invoke-RestMethod -ParameterFilter { $Method -eq 'Patch' } -MockWith {
            $script:capturedBody = $Body
            $script:mockOrgResponse
        } -ModuleName FsiMimeControl

        Set-FsiMimeConfig -DataverseUrl $script:testUrl -AccessToken $script:testToken `
            -BlockedExtensions @('exe', 'bat') -BlockedMimeTypes @('application/x-msdownload')
        $script:capturedBody | Should -Not -BeNullOrEmpty
    }

    It 'PATCH body contains semicolon-joined strings' {
        $script:capturedBody = $null
        Mock Invoke-RestMethod -ParameterFilter { $Method -eq 'Patch' } -MockWith {
            $script:capturedBody = $Body
            $script:mockOrgResponse
        } -ModuleName FsiMimeControl

        Set-FsiMimeConfig -DataverseUrl $script:testUrl -AccessToken $script:testToken `
            -BlockedExtensions @('exe', 'bat', 'cmd')
        $bodyObj = $script:capturedBody | ConvertFrom-Json
        $bodyObj.blockedattachments | Should -Be 'exe;bat;cmd'
    }

    It 'Returns result object with Applied = $true' {
        Mock Invoke-RestMethod -ParameterFilter { $Method -eq 'Patch' } -MockWith {
            $script:mockOrgResponse
        } -ModuleName FsiMimeControl

        $result = Set-FsiMimeConfig -DataverseUrl $script:testUrl -AccessToken $script:testToken -ZoneTemplate zone1
        $result.Applied | Should -BeTrue
    }

    It 'Custom mode omits blockedmimetypes when -BlockedMimeTypes not specified' {
        $script:capturedBody = $null
        Mock Invoke-RestMethod -ParameterFilter { $Method -eq 'Patch' } -MockWith {
            $script:capturedBody = $Body
            $script:mockOrgResponse
        } -ModuleName FsiMimeControl

        Set-FsiMimeConfig -DataverseUrl $script:testUrl -AccessToken $script:testToken `
            -BlockedExtensions @('exe', 'bat')
        $bodyObj = $script:capturedBody | ConvertFrom-Json
        $bodyObj.blockedattachments | Should -Be 'exe;bat'
        $bodyObj.PSObject.Properties.Name | Should -Not -Contain 'blockedmimetypes'
    }

    It 'Custom mode includes blockedmimetypes when -BlockedMimeTypes specified' {
        $script:capturedBody = $null
        Mock Invoke-RestMethod -ParameterFilter { $Method -eq 'Patch' } -MockWith {
            $script:capturedBody = $Body
            $null
        } -ModuleName FsiMimeControl

        Set-FsiMimeConfig -DataverseUrl $script:testUrl -AccessToken $script:testToken `
            -BlockedExtensions @('exe') -BlockedMimeTypes @('application/x-msdownload')
        $bodyObj = $script:capturedBody | ConvertFrom-Json
        $bodyObj.PSObject.Properties.Name | Should -Contain 'blockedmimetypes'
        $bodyObj.blockedmimetypes | Should -Be 'application/x-msdownload'
    }

    It 'Template mode zone1 includes blockedmimetypes (empty string) in PATCH' {
        $script:capturedBody = $null
        Mock Invoke-RestMethod -ParameterFilter { $Method -eq 'Patch' } -MockWith {
            $script:capturedBody = $Body
            $null
        } -ModuleName FsiMimeControl

        $result = Set-FsiMimeConfig -DataverseUrl $script:testUrl -AccessToken $script:testToken -ZoneTemplate zone1 -WarningAction SilentlyContinue
        $result.Applied | Should -BeTrue
        $bodyObj = $script:capturedBody | ConvertFrom-Json
        # Zone 1 template mode always sends blockedmimetypes (empty string to clear)
        $bodyObj.PSObject.Properties.Name | Should -Contain 'blockedmimetypes'
        $bodyObj.blockedmimetypes | Should -Be ''
    }

    It 'Template mode zone3 retries PATCH without allowedmimetypes on field error' {
        $script:patchCallCount = 0
        Mock Invoke-RestMethod -ParameterFilter { $Method -eq 'Patch' } -MockWith {
            $script:patchCallCount++
            if ($script:patchCallCount -eq 1) {
                $ex = [System.Net.Http.HttpRequestException]::new('Bad Request: allowedmimetypes field not found')
                throw $ex
            }
            $null
        } -ModuleName FsiMimeControl

        $result = Set-FsiMimeConfig -DataverseUrl $script:testUrl -AccessToken $script:testToken -ZoneTemplate zone3 -WarningAction SilentlyContinue
        $result.Applied | Should -BeTrue
        $result.AllowedMimeTypesSupported | Should -BeFalse
        $script:patchCallCount | Should -Be 2
    }

    It 'Custom mode normalizes extensions to lowercase' {
        $script:capturedBody = $null
        Mock Invoke-RestMethod -ParameterFilter { $Method -eq 'Patch' } -MockWith {
            $script:capturedBody = $Body
            $null
        } -ModuleName FsiMimeControl

        Set-FsiMimeConfig -DataverseUrl $script:testUrl -AccessToken $script:testToken `
            -BlockedExtensions @('EXE', 'Bat', 'CMD')
        $bodyObj = $script:capturedBody | ConvertFrom-Json
        $bodyObj.blockedattachments | Should -Be 'exe;bat;cmd'
    }
}

# ═══════════════════════════════════════════════════════════════════════
# Category 5: Test-FsiMimeCompliance
# ═══════════════════════════════════════════════════════════════════════

Describe 'Test-FsiMimeCompliance' {
    Context 'Zone 1 compliance' {
        BeforeAll {
            # Zone 1 compliant: full blocked extensions (44 items)
            Mock Invoke-RestMethod { $script:mockOrgResponse } -ModuleName FsiMimeControl
        }

        It 'Full blocked extensions → IsCompliant = $true' {
            $result = Test-FsiMimeCompliance -DataverseUrl $script:testUrl -AccessToken $script:testToken -Zone 1
            $result.IsCompliant | Should -BeTrue
        }
    }

    Context 'Zone 1 non-compliance' {
        BeforeAll {
            # Only 4 extensions configured - missing many required
            Mock Invoke-RestMethod { $script:mockOrgResponsePartial } -ModuleName FsiMimeControl
        }

        It 'Missing blocked extensions → IsCompliant = $false' {
            $result = Test-FsiMimeCompliance -DataverseUrl $script:testUrl -AccessToken $script:testToken -Zone 1
            $result.IsCompliant | Should -BeFalse
        }
    }

    Context 'Zone 2 compliance' {
        BeforeAll {
            # Zone 2 compliant: extensions + MIME types
            Mock Invoke-RestMethod { $script:mockOrgResponseZone2 } -ModuleName FsiMimeControl
        }

        It 'Extensions + MIME types → IsCompliant = $true' {
            $result = Test-FsiMimeCompliance -DataverseUrl $script:testUrl -AccessToken $script:testToken -Zone 2
            $result.IsCompliant | Should -BeTrue
        }
    }

    Context 'Zone 2 missing MIME types' {
        BeforeAll {
            # Has extensions but no MIME types
            Mock Invoke-RestMethod {
                @{
                    value = @(@{
                        organizationid      = '00000000-0000-0000-0000-000000000006'
                        blockedattachments  = 'ade;adp;app;asa;asp;bat;cdx;cmd;com;cpl;crt;csh;dll;exe;hta;inf;ins;jar;js;jse;lnk;mda;mdb;mde;msc;msi;msp;mst;pcd;pif;ps1;reg;scr;sct;shb;shs;tmp;url;vb;vbe;vbs;ws;wsc;wsf;wsh'
                        blockedmimetypes    = $null
                    })
                }
            } -ModuleName FsiMimeControl
        }

        It 'Missing MIME types → IsCompliant = $false' {
            $result = Test-FsiMimeCompliance -DataverseUrl $script:testUrl -AccessToken $script:testToken -Zone 2
            $result.IsCompliant | Should -BeFalse
        }
    }

    Context 'Zone 3 compliance' {
        BeforeAll {
            Mock Invoke-RestMethod { $script:mockOrgResponseZone3 } -ModuleName FsiMimeControl
        }

        It 'Missing allowlist → produces check result' {
            # When allowedmimetypes query throws (field unsupported), MIME-05 should be Warning not Fail
            Mock Invoke-RestMethod -ParameterFilter { $Uri -match 'allowedmimetypes' } -MockWith {
                throw 'Field not found'
            } -ModuleName FsiMimeControl

            $result = Test-FsiMimeCompliance -DataverseUrl $script:testUrl -AccessToken $script:testToken -Zone 3
            $mime05 = $result.Checks | Where-Object { $_.CheckId -eq 'MIME-05' }
            $mime05 | Should -Not -BeNullOrEmpty
            # Advisory mode: Warning not Fail when field is unsupported
            $mime05.Status | Should -Be 'Warning'
        }

        It 'Full config → IsCompliant = $true' {
            Mock Invoke-RestMethod { $script:mockOrgResponseZone3 } -ModuleName FsiMimeControl
            $result = Test-FsiMimeCompliance -DataverseUrl $script:testUrl -AccessToken $script:testToken -Zone 3
            $result.IsCompliant | Should -BeTrue
        }
    }

    Context 'Output details' {
        BeforeAll {
            Mock Invoke-RestMethod { $script:mockOrgResponsePartial } -ModuleName FsiMimeControl
        }

        It 'Missing extensions produce specific findings' {
            $result = Test-FsiMimeCompliance -DataverseUrl $script:testUrl -AccessToken $script:testToken -Zone 1
            $result.Findings | Should -Not -BeNullOrEmpty
            $result.Findings.Count | Should -BeGreaterThan 0
            # Should mention specific missing extensions
            ($result.Findings -join ' ') | Should -Match 'missing|Missing'
        }

        It '-IncludeEvidence computes SHA-256 hash' {
            $result = Test-FsiMimeCompliance -DataverseUrl $script:testUrl -AccessToken $script:testToken -Zone 1 -IncludeEvidence
            $result.EvidenceHash | Should -Not -BeNullOrEmpty
            # SHA-256 hash should be 64 hex characters
            $result.EvidenceHash | Should -Match '^[A-F0-9]{64}$'
        }
    }
}

# ═══════════════════════════════════════════════════════════════════════
# Category 6: Connection Management
# ═══════════════════════════════════════════════════════════════════════

Describe 'Connection Management' {
    BeforeAll {
        # Reset module state before connection tests
        Import-Module (Join-Path $PSScriptRoot 'FsiMimeControl.psm1') -Force
    }

    It 'Connect-FsiMimeDataverse sets module state' {
        Mock Invoke-RestMethod { @{ value = @(@{ organizationid = '00000000-0000-0000-0000-000000000001' }) } } -ModuleName FsiMimeControl

        Connect-FsiMimeDataverse -DataverseUrl $script:testUrl -AccessToken $script:testToken
        $conn = Get-FsiMimeConnection
        $conn.IsConnected | Should -BeTrue
        $conn.DataverseUrl | Should -Be $script:testUrl
    }

    It 'Get-FsiMimeConnection returns correct status' {
        Mock Invoke-RestMethod { @{ value = @(@{ organizationid = '00000000-0000-0000-0000-000000000001' }) } } -ModuleName FsiMimeControl

        Connect-FsiMimeDataverse -DataverseUrl $script:testUrl -AccessToken $script:testToken
        $conn = Get-FsiMimeConnection
        $conn | Should -BeOfType [PSCustomObject]
        $conn.PSObject.Properties.Name | Should -Contain 'IsConnected'
        $conn.PSObject.Properties.Name | Should -Contain 'DataverseUrl'
        $conn.PSObject.Properties.Name | Should -Contain 'TokenExpiry'
    }

    It 'Token fallback to Get-AzAccessToken when no explicit token' {
        # Define a global stub so Pester can mock the non-existent cmdlet
        function global:Get-AzAccessToken { param($ResourceUrl, $ErrorAction) }

        # Reset module state first, then apply mocks to the fresh module scope
        Import-Module (Join-Path $PSScriptRoot 'FsiMimeControl.psm1') -Force

        Mock Invoke-RestMethod { @{ value = @(@{ organizationid = '00000000-0000-0000-0000-000000000001' }) } } -ModuleName FsiMimeControl
        Mock Get-AzAccessToken { [PSCustomObject]@{ Token = 'mock-az-token' } } -ModuleName FsiMimeControl

        Connect-FsiMimeDataverse -DataverseUrl $script:testUrl
        Should -Invoke Get-AzAccessToken -ModuleName FsiMimeControl

        # Cleanup global stub
        Remove-Item Function:\Get-AzAccessToken -ErrorAction SilentlyContinue
    }

    It 'Connection validation fails gracefully on bad URL' {
        Mock Invoke-RestMethod { throw 'Connection refused' } -ModuleName FsiMimeControl

        { Connect-FsiMimeDataverse -DataverseUrl 'https://invalid.example.com' -AccessToken $script:testToken } | Should -Throw
    }

    It 'Handles SecureString token from Az.Accounts 5.0+' {
        function global:Get-AzAccessToken { param($ResourceUrl, $ErrorAction) }
        Import-Module (Join-Path $PSScriptRoot 'FsiMimeControl.psm1') -Force
        Mock Invoke-RestMethod { @{ value = @(@{ organizationid = '00000000-0000-0000-0000-000000000001' }) } } -ModuleName FsiMimeControl
        $secureToken = ConvertTo-SecureString 'mock-secure-token-12345' -AsPlainText -Force
        Mock Get-AzAccessToken { [PSCustomObject]@{ Token = $secureToken } } -ModuleName FsiMimeControl
        Connect-FsiMimeDataverse -DataverseUrl $script:testUrl
        Should -Invoke Get-AzAccessToken -ModuleName FsiMimeControl
        $conn = Get-FsiMimeConnection
        $conn.IsConnected | Should -BeTrue
        Remove-Item Function:\Get-AzAccessToken -ErrorAction SilentlyContinue
    }

    It 'Get-FsiMimeConfig throws when no URL and no session' {
        # Re-import to clear module state
        Import-Module (Join-Path $PSScriptRoot 'FsiMimeControl.psm1') -Force
        { Get-FsiMimeConfig } | Should -Throw '*No Dataverse URL*'
    }
}
