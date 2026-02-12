# Phase 4 Research: PowerShell Remediation

## Phase Goal

Create `Set-InactivityTimeout.ps1` for BAP Admin API PATCH remediation with audit record writing and validation testing.

## Requirements Covered

- **REM-01:** `Set-InactivityTimeout.ps1` with mandatory `-EnvironmentName`, `-TimeoutDuration` (ValidateRange 5-120, default 120), `-WarningDuration` (ValidateRange 1-30, default 5); PATCH BAP Admin API privacy settings endpoint; `#Requires -Version 7.0`, `SupportsShouldProcess`, `-WhatIf`
- **REM-02:** Remediation audit record writing to Dataverse compliance table; validation test script (`Test-InactivityTimeoutRemediation.ps1`)

## Existing Pattern Analysis

### 1. Script Header & #Requires Conventions

All governance scripts follow a consistent pattern:

**`#Requires` statement** — always `#Requires -Version 7.0`. Module dependencies vary:
- BAP API scripts (`Test-AgentAuthConfiguration.ps1`, `Invoke-SharingAudit.ps1`, `restrict-agent-publishing.ps1`): `#Requires -Modules @{ ModuleName = 'Microsoft.PowerApps.Administration.PowerShell'; ModuleVersion = '2.0.0' }`
- Dataverse-only scripts (`Export-ViolationReport.ps1`, `Import-ApprovedSecurityGroups.ps1`): `#Requires -Modules Az.Accounts`
- Module files (`FsiMimeControl.psm1`): `#Requires -Version 7.0` only (no module dependency)

**For Set-InactivityTimeout.ps1:** Since it uses BAP Admin API directly (not through PP admin cmdlets) and optionally writes to Dataverse, use `#Requires -Version 7.0` with no module requirement — but document Az.Accounts as recommended for token acquisition.

*References:*
- `scripts/governance/Test-AgentAuthConfiguration.ps1` line 79-80
- `scripts/governance/FsiMimeControl.psm1` line 1
- `scripts/governance/Import-ApprovedSecurityGroups.ps1` line 63

### 2. Parameter Patterns

**Common parameter set across detection/audit scripts:**
```powershell
[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter()]
    [ValidateSet('Table', 'JSON', 'Object')]
    [string]$OutputFormat = 'Table',

    [Parameter()]
    [string]$OutputPath,

    [Parameter()]
    [string[]]$EnvironmentFilter,

    [Parameter()]
    [hashtable]$ZoneMapping,

    [Parameter()]
    [switch]$IncludeEvidence
)
```

**Environment identifier patterns:**
- `restrict-agent-publishing.ps1`: `-EnvironmentFilter` (string array, optional filter)
- `Invoke-SharingAudit.ps1`: `-EnvironmentFilter` (string array, optional filter)
- `Deploy-RemediationFlow.ps1`: `-EnvironmentId` (mandatory, GUID-validated)
- `Import-ApprovedSecurityGroups.ps1`: No environment param (Dataverse URL instead)
- `FsiMimeControl.psm1`: `-DataverseUrl` (Dataverse environment URL)

**For Set-InactivityTimeout.ps1:** Use `-EnvironmentName` as mandatory (per REM-01 spec — canonical Power Platform Environment Name identifier). This differs from existing patterns (which use filters or GUIDs) because this is a targeted remediation script, not a scan.

*References:*
- `scripts/governance/Deploy-RemediationFlow.ps1` lines 82-84 (mandatory validated parameter)
- `scripts/governance/restrict-agent-publishing.ps1` lines 77-82

### 3. BAP Admin API Authentication Pattern

All BAP API scripts use the same two-function pattern:

```powershell
function Get-BapApiToken {
    [CmdletBinding()]
    param()
    try {
        $token = Get-AzAccessToken -ResourceUrl "https://api.bap.microsoft.com" -ErrorAction Stop
        return $token.Token
    }
    catch {
        throw "Failed to acquire BAP API token. Ensure you are signed in via Connect-AzAccount. Error: $($_.Exception.Message)"
    }
}

function Invoke-BapApi {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$Uri,
        [Parameter(Mandatory)][string]$Token,
        [Parameter()][ValidateSet('GET', 'POST', 'PUT', 'PATCH', 'DELETE')][string]$Method = 'GET'
    )
    try {
        $headers = @{
            Authorization  = "Bearer $Token"
            'Content-Type' = 'application/json'
        }
        $response = Invoke-RestMethod -Uri $Uri -Method $Method -Headers $headers -ErrorAction Stop
        return $response
    }
    catch {
        Write-Warning "BAP API call failed ($Method $Uri): $($_.Exception.Message)"
        return $null
    }
}
```

**Key observations:**
- `Invoke-BapApi` currently does NOT accept a `-Body` parameter — only GET-style calls work. For Set-InactivityTimeout.ps1, the wrapper needs to be extended to accept `-Body` for PATCH.
- Auth uses `Get-AzAccessToken -ResourceUrl "https://api.bap.microsoft.com"` — requires `Connect-AzAccount` session.
- Error handling pattern: `Get-BapApiToken` throws on failure (hard stop); `Invoke-BapApi` returns `$null` on failure (soft fail with warning).

**For PATCH operations:** Need a modified `Invoke-BapApi` that accepts `-Body` and throws rather than soft-fails (since remediation failures must be surfaced). Pattern from `FsiMimeControl.psm1` `Set-FsiMimeConfig` shows how PATCH with body is done:

```powershell
$body = $patchBody | ConvertTo-Json -Compress
$null = Invoke-RestMethod -Uri $patchUri -Headers $patchHeaders -Method Patch -Body $body
```

*References:*
- `scripts/governance/Test-AgentAuthConfiguration.ps1` lines 108-145 (Get-BapApiToken + Invoke-BapApi)
- `scripts/governance/Invoke-SharingAudit.ps1` lines 170-216
- `scripts/governance/FsiMimeControl.psm1` lines 508-522 (PATCH with body)

### 4. SupportsShouldProcess / -WhatIf Pattern

Two distinct patterns in the codebase:

**Pattern A — Detection scripts (read-only):** WhatIf gates the entire operation.
```powershell
if (-not $PSCmdlet.ShouldProcess("Power Platform tenant", "Run hardening baseline checks")) {
    Write-Verbose "WhatIf: Would check hardening baseline items..."
    return
}
```

**Pattern B — Mutation scripts (Set-FsiMimeConfig):** WhatIf shows preview of changes without applying.
```powershell
if (-not $PSCmdlet.ShouldProcess($conn.Url, "Apply $targetDescription")) {
    Write-Verbose "WhatIf: Current blocked extensions ($($currentConfig.BlockedExtensions.Count)): ..."
    Write-Verbose "WhatIf: Target blocked extensions ($($targetExtensions.Count)): ..."
    return
}
```

**For Set-InactivityTimeout.ps1:** Use Pattern B — show current vs target values, then return without PATCHing. This gives operators a safe preview before remediation.

*References:*
- `scripts/governance/FsiMimeControl.psm1` lines 476-483 (mutation WhatIf)
- `scripts/governance/Invoke-HardeningBaselineCheck.ps1` lines 83-86 (detection WhatIf)

### 5. Banner Pattern

Every script starts with the same box-drawing banner:

```powershell
Write-Host "`n╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host   "║  FSI Agent Governance — [Script Name]                   ║" -ForegroundColor Cyan
Write-Host   "╚══════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan
```

All banners are exactly 58 characters wide inside the box.

*References:*
- Every script in `scripts/governance/` uses this pattern

### 6. Results Aggregation Pattern

Detection scripts build results as:
```powershell
$baselineResults = [PSCustomObject]@{
    Metadata = [PSCustomObject]@{
        CheckedAt           = $startTime
        ScriptVersion       = '1.2.0'
        EnvironmentsScanned = $envCount
        DurationSeconds     = [math]::Round($duration, 2)
        IntegrityHash       = $null
    }
    Summary = [PSCustomObject]@{
        TotalChecks   = $totalChecks
        Passed        = $passCount
        Failed        = $failCount
        ...
    }
    Checks = $allChecks.ToArray()
    Gaps   = $gaps.ToArray()
}
```

Mutation scripts (`Set-FsiMimeConfig`) build results as:
```powershell
$result = [PSCustomObject]@{
    Applied          = $true
    PreviousConfig   = $currentConfig
    NewConfig        = $newConfig
    Template         = $templateName
}
```

**For Set-InactivityTimeout.ps1:** Follow the mutation pattern — return before/after state plus metadata.

*References:*
- `scripts/governance/Invoke-HardeningBaselineCheck.ps1` lines 575-592
- `scripts/governance/FsiMimeControl.psm1` lines 546-553

### 7. Dataverse Record Writing Pattern

`Import-ApprovedSecurityGroups.ps1` provides the canonical pattern for Dataverse writes:

```powershell
function Get-DataverseToken {
    param([Parameter(Mandatory)][string]$ResourceUrl)
    try {
        $token = Get-AzAccessToken -ResourceUrl $ResourceUrl -ErrorAction Stop
        return $token.Token
    }
    catch {
        throw "Failed to acquire Dataverse token. Ensure you are signed in via Connect-AzAccount. Error: $($_.Exception.Message)"
    }
}

function Invoke-DataverseApi {
    param(
        [Parameter(Mandatory)][string]$Uri,
        [Parameter(Mandatory)][string]$Token,
        [Parameter()][ValidateSet('GET', 'POST', 'PATCH')][string]$Method = 'GET',
        [Parameter()][hashtable]$Body
    )
    $headers = @{
        Authorization      = "Bearer $Token"
        'Content-Type'     = 'application/json'
        'OData-MaxVersion' = '4.0'
        'OData-Version'    = '4.0'
        'Prefer'           = 'return=representation'
    }
    $params = @{ Uri = $Uri; Method = $Method; Headers = $headers; ErrorAction = 'Stop' }
    if ($Body -and ($Method -eq 'POST' -or $Method -eq 'PATCH')) {
        $params['Body'] = ($Body | ConvertTo-Json -Depth 10 -Compress)
    }
    $response = Invoke-RestMethod @params
    return $response
}
```

**Dataverse entity naming convention:** All custom tables use `fsi_` prefix (e.g., `fsi_approvedsecuritygroups`, `fsi_SharingViolation`, `fsi_SharingException`).

**For remediation audit records:** Write to `fsi_inactivitytimeout_compliance` table (defined in Phase 2 DVM-02). New rows include: `fsi_environmentid`, `fsi_environmentname`, `fsi_inactivitytimeoutenabled`, `fsi_timeoutduration`, `fsi_requiredmaxduration`, `fsi_compliancestatus`, `fsi_lastscandate`, `fsi_notes`. The remediation record should additionally capture before/after values and the remediation action.

*References:*
- `scripts/governance/Import-ApprovedSecurityGroups.ps1` lines 100-165 (Invoke-DataverseApi)
- `scripts/governance/Import-ApprovedSecurityGroups.ps1` lines 410-470 (POST/PATCH to Dataverse)
- `scripts/governance/Export-ViolationReport.ps1` lines 344-381 (fsi_ field naming)

### 8. SHA-256 Evidence Hash Pattern

Consistent across all scripts:
```powershell
$resultsJson = $result | ConvertTo-Json -Depth 10 -Compress
$hashBytes = [System.Security.Cryptography.SHA256]::Create().ComputeHash(
    [System.Text.Encoding]::UTF8.GetBytes($resultsJson)
)
$result.Metadata.IntegrityHash = [BitConverter]::ToString($hashBytes) -replace '-'
```

*References:*
- `scripts/governance/Invoke-HardeningBaselineCheck.ps1` lines 598-601
- `scripts/governance/restrict-agent-publishing.ps1` (Get-EvidenceHash helper)

### 9. Console Summary Pattern

```powershell
Write-Host "`n── Summary Title ──────────────────────────────────" -ForegroundColor Cyan
Write-Host "  Items checked:     $totalChecks"
Write-Host "  Passed:            $passCount" -ForegroundColor $(if ($passCount -eq $totalChecks) { 'Green' } else { 'White' })
Write-Host "  Failed:            $failCount" -ForegroundColor $(if ($failCount -gt 0) { 'Yellow' } else { 'Green' })
Write-Host "────────────────────────────────────────────────────────────`n" -ForegroundColor Cyan
```

### 10. ErrorActionPreference

Detection scripts set `$ErrorActionPreference = 'Stop'` at script scope. Module functions rely on individual `-ErrorAction Stop` on API calls.

## BAP Admin API Privacy Settings Endpoint Analysis

### Endpoint
```
GET/PATCH https://api.bap.microsoft.com/providers/Microsoft.BusinessAppPlatform/scopes/admin/environments/{EnvironmentName}/settings/privacy?api-version=2021-04-01
```

### Key Details
- **`{EnvironmentName}`** is the canonical Power Platform Environment Name (GUID-like identifier from `Get-AdminPowerAppEnvironment`), NOT the display name.
- **API version:** `2021-04-01` (consistent with other BAP API calls in the codebase which use `2016-11-01` for environment enumeration and `2021-04-01` for bot/agent operations).
- **Auth:** Bearer token from `Get-AzAccessToken -ResourceUrl "https://api.bap.microsoft.com"`.

### Expected Response Shape (GET)
Based on the hardening baseline check (Item 30) and the spec, the privacy settings endpoint returns an object containing timeout fields. The hardening baseline queries via Dataverse Organization entity, but the BAP Admin API endpoint returns:

```json
{
    "properties": {
        "InactivityTimeoutEnabled": true,
        "InactivityTimeoutInMinutes": 120,
        "InactivityWarningInMinutes": 5
    }
}
```

### PATCH Body Shape
```json
{
    "properties": {
        "InactivityTimeoutEnabled": true,
        "InactivityTimeoutInMinutes": 120,
        "InactivityWarningInMinutes": 5
    }
}
```

### Existing Inactivity Timeout Checks in Codebase

`Invoke-HardeningBaselineCheck.ps1` (Item 30) already reads inactivity timeout but via **Dataverse Organization entity**, NOT via BAP Admin API privacy settings:

```powershell
$securityFields = 'blockedattachments,blockedmimetypes,inaborttimeenabled,inactivitytimeoutinmins,' +
    'sessiontimeoutenabled,sessiontimeoutinmins,isaborttimeenabled,' +
    'iscontentsecuritypolicyenabled,contentsecuritypolicyoptions'
$orgResponse = Invoke-RestMethod `
    -Uri "${dataverseUrl}api/data/v9.2/organizations?$select=$securityFields" `
    -Headers @{ Authorization = "Bearer $((Get-AzAccessToken -ResourceUrl $dataverseUrl).Token)" } `
    -Method Get

$inactivityEnabled = $org.inaborttimeenabled -eq $true -or $org.isaborttimeenabled -eq $true
$inactivityMinutes = $org.inactivitytimeoutinmins
```

**Important:** Hardening baseline uses Dataverse field names (`inaborttimeenabled`, `inactivitytimeoutinmins`) which differ from BAP Admin API property names (`InactivityTimeoutEnabled`, `InactivityTimeoutInMinutes`). The Set-InactivityTimeout.ps1 script uses BAP Admin API, so property names will be PascalCase.

*References:*
- `scripts/governance/Invoke-HardeningBaselineCheck.ps1` lines 437-438, 493-507

### Error Codes

Based on existing BAP API usage patterns and common Azure REST API behavior:

| Code | Meaning | Handling |
|------|---------|----------|
| 200 | Success (GET/PATCH) | Normal flow |
| 401 | Unauthorized — token expired or invalid | Re-throw with auth guidance |
| 403 | Forbidden — insufficient permissions (not PP admin) | Re-throw with permission guidance |
| 404 | Environment not found — invalid EnvironmentName | Re-throw with parameter validation guidance |
| 429 | Rate limited | Retry with backoff (or throw with guidance) |
| 500 | Server error | Re-throw |

## Pester Test Pattern Analysis

### From `FsiMimeControl.Tests.ps1` (32 tests, 6 Describe blocks)

**Structure:**
```
#Requires -Version 7.0
#Requires -Modules Pester

BeforeAll {
    Import-Module (Join-Path $PSScriptRoot 'Module.psm1') -Force
    # Shared mock data definitions
    $script:mockResponse = @{ ... }
    $script:testToken = 'mock-access-token-12345'
}

Describe 'Category Name' {
    BeforeAll {
        Mock Invoke-RestMethod { $script:mockResponse } -ModuleName ModuleName
    }

    It 'Test description' {
        $result = Function-Under-Test -Param $value
        $result.Property | Should -Be 'expected'
    }

    Context 'Sub-scenario' {
        BeforeAll {
            Mock Invoke-RestMethod { $script:mockAltResponse } -ModuleName ModuleName
        }
        It 'Sub-test' { ... }
    }
}
```

**Mock patterns:**
1. **Method-filtered mocks** for PATCH vs GET:
   ```powershell
   Mock Invoke-RestMethod -ParameterFilter { $Method -ne 'Patch' } -MockWith { $script:mockGetResponse } -ModuleName FsiMimeControl
   Mock Invoke-RestMethod -ParameterFilter { $Method -eq 'Patch' } -MockWith { $script:mockPatchResponse } -ModuleName FsiMimeControl
   ```

2. **Body capture for PATCH validation:**
   ```powershell
   $script:capturedBody = $null
   Mock Invoke-RestMethod -ParameterFilter { $Method -eq 'Patch' } -MockWith {
       $script:capturedBody = $Body
       $script:mockOrgResponse
   } -ModuleName FsiMimeControl
   ```

3. **WhatIf assertion — PATCH not called:**
   ```powershell
   Set-FsiMimeConfig ... -WhatIf
   Should -Not -Invoke Invoke-RestMethod -ParameterFilter { $Method -eq 'Patch' } -ModuleName FsiMimeControl
   ```

4. **Error simulation:**
   ```powershell
   Mock Invoke-RestMethod { throw 'Simulated API error' } -ModuleName FsiMimeControl
   { Function-Under-Test ... } | Should -Throw
   ```

**Key: Since `Set-InactivityTimeout.ps1` is a script (not a module), mocking is different.** For standalone scripts, mocks target global functions or use `-CommandName` without `-ModuleName`. The test will need to dot-source the script or use a wrapper approach.

**Test approach for standalone .ps1 scripts:** The test can mock `Invoke-RestMethod` and `Get-AzAccessToken` globally, then invoke the script via `& $scriptPath`. However, since `ShouldProcess` is involved, tests need `-Confirm:$false` or similar handling.

*References:*
- `scripts/governance/FsiMimeControl.Tests.ps1` lines 34-117 (BeforeAll + mock data)
- `scripts/governance/FsiMimeControl.Tests.ps1` lines 259-330 (Set-FsiMimeConfig tests with PATCH mocks)

## Recommended Technical Approach

### Plan A: Set-InactivityTimeout.ps1 (REM-01)

#### Script Structure

```
#Requires -Version 7.0
<# .SYNOPSIS / .DESCRIPTION / .PARAMETER / .EXAMPLE / .NOTES #>

[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(Mandatory)]
    [ValidateNotNullOrEmpty()]
    [string]$EnvironmentName,

    [Parameter()]
    [ValidateRange(5, 120)]
    [int]$TimeoutDuration = 120,

    [Parameter()]
    [ValidateRange(1, 30)]
    [int]$WarningDuration = 5,

    [Parameter()]
    [string]$DataverseUrl,          # Optional — for audit record writing

    [Parameter()]
    [ValidateSet('Table', 'JSON', 'Object')]
    [string]$OutputFormat = 'Object',

    [Parameter()]
    [string]$OutputPath,

    [Parameter()]
    [switch]$IncludeEvidence
)

$ErrorActionPreference = 'Stop'

# ─── Banner (58-char wide) ─────────────────────────
# ─── Helper Functions ──────────────────────────────
#   Get-BapApiToken (reuse existing pattern)
#   Invoke-BapApi (extended with -Body for PATCH)
#   Get-DataverseToken (conditional — only if DataverseUrl provided)
#   Invoke-DataverseApi (conditional — only if DataverseUrl provided)

# ─── Step 1: Authenticate ──────────────────────────
# ─── Step 2: GET current privacy settings ──────────
# ─── Step 3: WhatIf preview (current vs target) ────
# ─── Step 4: PATCH privacy settings ────────────────
# ─── Step 5: Verify PATCH (re-GET) ─────────────────
# ─── Step 6: Optionally write Dataverse audit ──────
# ─── Step 7: Build result object ───────────────────
# ─── Step 8: Output ────────────────────────────────
```

#### Parameter Design Rationale

| Parameter | Type | Required | Default | Source |
|-----------|------|----------|---------|--------|
| `-EnvironmentName` | string | Yes | — | REM-01 spec: "mandatory EnvironmentName parameter (canonical Power Platform Environment Name)" |
| `-TimeoutDuration` | int[5-120] | No | 120 | REM-01 spec: "ValidateRange 5-120, default 120" |
| `-WarningDuration` | int[1-30] | No | 5 | REM-01 spec: "ValidateRange 1-30, default 5" |
| `-DataverseUrl` | string | No | — | REM-02: "optionally write records to Dataverse" |
| `-OutputFormat` | string | No | 'Object' | Consistent with all governance scripts |
| `-OutputPath` | string | No | — | Consistent with all governance scripts |
| `-IncludeEvidence` | switch | No | — | Consistent with all governance scripts |

#### BAP API Call Sequence

1. **GET** current settings:
   ```
   GET https://api.bap.microsoft.com/providers/Microsoft.BusinessAppPlatform/scopes/admin/environments/{EnvironmentName}/settings/privacy?api-version=2021-04-01
   ```
2. **PATCH** new settings:
   ```
   PATCH https://api.bap.microsoft.com/providers/Microsoft.BusinessAppPlatform/scopes/admin/environments/{EnvironmentName}/settings/privacy?api-version=2021-04-01
   Body: { "properties": { "InactivityTimeoutEnabled": true, "InactivityTimeoutInMinutes": 120, "InactivityWarningInMinutes": 5 } }
   ```
3. **GET** verification (re-read to confirm):
   ```
   GET https://api.bap.microsoft.com/providers/Microsoft.BusinessAppPlatform/scopes/admin/environments/{EnvironmentName}/settings/privacy?api-version=2021-04-01
   ```

#### WhatIf Behavior

When `-WhatIf` is specified:
1. GET current settings (still executed — read-only)
2. Display comparison table:
   ```
   WhatIf: Current InactivityTimeoutEnabled = False
   WhatIf: Target  InactivityTimeoutEnabled = True
   WhatIf: Current InactivityTimeoutInMinutes = N/A
   WhatIf: Target  InactivityTimeoutInMinutes = 120
   WhatIf: Current InactivityWarningInMinutes = N/A
   WhatIf: Target  InactivityWarningInMinutes = 5
   ```
3. Return without PATCH

#### Result Object Shape

```powershell
[PSCustomObject]@{
    Metadata = [PSCustomObject]@{
        Timestamp       = [DateTime]::UtcNow
        ScriptVersion   = '1.0.0'
        EnvironmentName = $EnvironmentName
        DurationSeconds = [math]::Round($duration, 2)
        IntegrityHash   = $null
    }
    Applied        = $true
    PreviousConfig = [PSCustomObject]@{
        InactivityTimeoutEnabled   = $false
        InactivityTimeoutInMinutes = $null
        InactivityWarningInMinutes = $null
    }
    NewConfig = [PSCustomObject]@{
        InactivityTimeoutEnabled   = $true
        InactivityTimeoutInMinutes = 120
        InactivityWarningInMinutes = 5
    }
    Verified       = $true       # Re-GET verification result
    AuditRecord    = $null       # Dataverse record ID if written
}
```

#### Error Handling

Follow layered approach from existing scripts:
1. `Get-BapApiToken` — throws on auth failure (hard stop)
2. GET current settings — throw with environment-specific guidance if 404
3. PATCH — throw with specific remediation guidance per error code:
   - 401: "BAP API token expired. Re-authenticate with Connect-AzAccount."
   - 403: "Insufficient permissions. Requires Power Platform Admin or Global Admin role."
   - 404: "Environment '$EnvironmentName' not found. Verify the Environment Name (not display name) via Get-AdminPowerAppEnvironment."
   - 429: "Rate limited. Retry after delay."
4. Verification GET — warn but don't throw (PATCH may have succeeded even if re-read fails)
5. Dataverse write — warn but don't throw (remediation succeeded even if audit write fails)

### Plan B: Remediation Audit Records + Validation Test Script (REM-02)

#### Dataverse Audit Record Writing

**When `-DataverseUrl` is provided**, write a compliance record to `fsi_inactivitytimeout_compliance`:

```powershell
$auditPayload = @{
    fsi_environmentid              = $EnvironmentName
    fsi_environmentname            = $envDisplayName  # resolved from GET response
    fsi_inactivitytimeoutenabled   = $true
    fsi_timeoutduration            = $TimeoutDuration
    fsi_requiredmaxduration        = $null  # Not known without policy lookup
    fsi_compliancestatus           = 0      # Compliant (just remediated)
    fsi_lastscandate               = (Get-Date -Format 'o')
    fsi_notes                      = "Remediated by Set-InactivityTimeout.ps1. Before: Enabled=$($previousConfig.InactivityTimeoutEnabled), Duration=$($previousConfig.InactivityTimeoutInMinutes). After: Enabled=True, Duration=$TimeoutDuration, Warning=$WarningDuration."
}
```

This is optional — only attempted when `-DataverseUrl` is specified. Failure does not block the main remediation result.

#### Test-InactivityTimeoutRemediation.ps1

**Purpose:** Pester 5 test suite validating `Set-InactivityTimeout.ps1` behavior.

**Structure (following FsiMimeControl.Tests.ps1 pattern):**

```
#Requires -Version 7.0
#Requires -Modules Pester

BeforeAll {
    $script:scriptPath = Join-Path $PSScriptRoot 'Set-InactivityTimeout.ps1'
    # Mock data
    $script:mockPrivacyResponse = @{ properties = @{ ... } }
}

Describe 'Parameter Validation' {
    It 'EnvironmentName is mandatory'
    It 'TimeoutDuration defaults to 120'
    It 'TimeoutDuration rejects values outside 5-120'
    It 'WarningDuration defaults to 5'
    It 'WarningDuration rejects values outside 1-30'
}

Describe 'BAP API Interactions' {
    Context 'GET current settings' {
        It 'Calls privacy settings endpoint with correct URL'
        It 'Handles 404 with clear error message'
        It 'Handles 401 with auth guidance'
    }
    Context 'PATCH remediation' {
        It 'Sends correct body with InactivityTimeoutEnabled, InactivityTimeoutInMinutes, InactivityWarningInMinutes'
        It 'PATCH body matches specified parameters'
    }
}

Describe 'WhatIf Support' {
    It '-WhatIf does NOT invoke PATCH'
    It '-WhatIf outputs current vs target to Verbose stream'
    It '-WhatIf still executes GET (read-only)'
}

Describe 'Verification' {
    It 'Re-reads settings after PATCH to confirm'
    It 'Sets Verified = $true when post-PATCH values match'
    It 'Sets Verified = $false when post-PATCH values do not match'
}

Describe 'Result Object' {
    It 'Returns PSCustomObject with Applied, PreviousConfig, NewConfig, Verified'
    It 'PreviousConfig captures pre-PATCH state'
    It 'NewConfig captures post-PATCH state'
}

Describe 'Dataverse Audit Record' {
    Context 'Without -DataverseUrl' {
        It 'Does not attempt Dataverse write'
    }
    Context 'With -DataverseUrl' {
        It 'Writes compliance record to fsi_inactivitytimeout_compliance'
        It 'Audit record contains before/after values'
        It 'Failure does not block main result'
    }
}
```

**Mocking strategy for standalone scripts:**
Since `Set-InactivityTimeout.ps1` is a standalone script (not a module), test mocking requires:
1. Mock `Invoke-RestMethod` and `Get-AzAccessToken` globally in the test scope
2. Use `& $script:scriptPath` to invoke the script
3. Use parameter filters on mocks to distinguish GET vs PATCH calls

Alternatively, wrap the script logic in a function within the script and test the function. But per existing patterns, the simpler approach (global mocks + script invocation) is preferred for standalone .ps1 files.

**Estimated test count:** 18-22 tests across 6 Describe blocks.

## File Manifest

| File | Phase Plan | Purpose |
|------|-----------|---------|
| `scripts/governance/Set-InactivityTimeout.ps1` | 04-01 | PowerShell remediation script — PATCH BAP Admin API privacy settings for inactivity timeout |
| `scripts/governance/Test-InactivityTimeoutRemediation.ps1` | 04-02 | Pester 5 validation test suite for Set-InactivityTimeout.ps1 |

## Risk Assessment

| # | Risk | Severity | Mitigation |
|---|------|----------|------------|
| 1 | BAP Admin API privacy settings response shape uncertainty — exact field names in API response may differ from documentation | High | Use GET before PATCH to discover actual field names; include field-name normalization logic; test against mock data matching known Dataverse Organization entity fields |
| 2 | Standalone script mocking complexity — scripts without modules are harder to mock in Pester | Medium | Use global `Mock Invoke-RestMethod` without `-ModuleName`; verify pattern works before committing; alternative: wrap in .psm1 but spec says .ps1 |
| 3 | `Invoke-BapApi` duplication — helper function is copy-pasted across 3+ existing scripts | Low | Accept duplication per existing pattern; future refactoring to shared module is out of scope |
| 4 | Dataverse compliance table may not exist yet (Phase 2 dependency) | Low | Make Dataverse write fully optional (`-DataverseUrl`); script succeeds even without Dataverse; document dependency |
| 5 | PATCH idempotency — applying same settings twice should be safe | Low | BAP API PATCH is idempotent; verify in tests that re-application returns same result |
| 6 | `WarningDuration` field name uncertainty — may be `InactivityWarningInMinutes` or `InactivityWarningDurationInMinutes` | Medium | GET response before PATCH will reveal actual field name; use the exact field name from GET response |

## Architecture Decisions

1. **Standalone .ps1 script** (not .psm1 module) — per spec and consistent with `Invoke-HardeningBaselineCheck.ps1`, `restrict-agent-publishing.ps1` patterns for automation scripts. Module pattern (`FsiMimeControl.psm1`) is reserved for multi-cmdlet packages.

2. **`-EnvironmentName` as mandatory string** (not GUID-validated) — Power Platform Environment Names can have varied formats; validation is handled by the API returning 404 for invalid names.

3. **GET-PATCH-GET pattern** — read current state, apply change, re-read to verify. Follows `Set-FsiMimeConfig` pattern which does pre-read, PATCH, post-read.

4. **Optional Dataverse audit** (`-DataverseUrl` parameter) — remediation script should work independently of Dataverse infrastructure (Phase 2). When `-DataverseUrl` is provided and Phase 2 tables exist, writes audit records. Failure silently warns.

5. **Extended `Invoke-BapApi` with `-Body`** — the existing pattern does not support PATCH with body. New version adds body parameter following the same pattern as `Invoke-DataverseApi` from `Import-ApprovedSecurityGroups.ps1`.

6. **Test file naming: `Test-InactivityTimeoutRemediation.ps1`** — follows `FsiMimeControl.Tests.ps1` pattern of collocated test files in the same directory.

## Wave Assignment

Plans 04-01 and 04-02 target non-overlapping files:
- 04-01: `scripts/governance/Set-InactivityTimeout.ps1`
- 04-02: `scripts/governance/Test-InactivityTimeoutRemediation.ps1`

**Wave 1** (parallel-eligible). However, 04-02 (test script) logically depends on 04-01 (script under test). Recommended execution: **04-01 first, then 04-02**, even though files don't conflict.

---
*Research completed: 2026-02-12*
*Phase: 04 — PowerShell Remediation*
*Milestone: v19 — Inactivity Timeout Enforcement (Policy-Driven Maximum)*
