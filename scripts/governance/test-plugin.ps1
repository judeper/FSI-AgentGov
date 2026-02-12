<#
.SYNOPSIS
    Integration tests for the ValidateMimeTypePlugin in a Dataverse environment.

.DESCRIPTION
    Creates test annotation records with various file types to validate the
    server-side MIME validation plugin behavior. Tests cover:

    1. PDF file upload (should pass — valid signature)
    2. PNG image upload (should pass — valid signature)
    3. EXE file disguised as .txt (should fail — PE header detected)
    4. Clean text file (should pass — no binary content)
    5. Oversized file (should fail — size guard)

    Reports results using [PASS]/[FAIL] pattern consistent with other FSI
    governance test scripts. Cleans up test annotations after verification.

    Supports compliance with FINRA 4511 and SEC 17a-4 by validating that
    server-side file type controls are functioning as expected in Zone 3
    environments.

.PARAMETER DataverseUrl
    Dataverse environment URL (e.g., https://org.crm.dynamics.com).
    Must include the https:// scheme.

.PARAMETER AccessToken
    OAuth access token for Dataverse. When omitted, falls back to
    Get-AzAccessToken for the specified DataverseUrl resource.

.PARAMETER SkipCleanup
    When specified, test annotation records are not deleted after testing.
    Useful for troubleshooting failed validations.

.EXAMPLE
    .\test-plugin.ps1 -DataverseUrl https://org.crm.dynamics.com

    Runs all integration tests using Azure AD token from Az.Accounts.

.EXAMPLE
    .\test-plugin.ps1 -DataverseUrl https://org.crm.dynamics.com -SkipCleanup

    Runs tests and leaves test annotations in place for inspection.

.EXAMPLE
    $token = (Get-AzAccessToken -ResourceUrl https://org.crm.dynamics.com).Token
    .\test-plugin.ps1 -DataverseUrl https://org.crm.dynamics.com -AccessToken $token

    Runs tests with an explicitly provided access token.

.OUTPUTS
    PSCustomObject with Metadata, TestResults array, and Summary.

.NOTES
    Part of the FSI Agent Governance — MIME Type Restrictions (Control 1.25).
    Version: 1.0.0
    Requires: PowerShell 7.0+, Az.Accounts module (for token fallback)
    Prerequisites: ValidateMimeTypePlugin must be registered via register-plugin.ps1
#>

#Requires -Version 7.0

[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidatePattern('^https://')]
    [string]$DataverseUrl,

    [Parameter()]
    [string]$AccessToken,

    [Parameter()]
    [switch]$SkipCleanup
)

$ErrorActionPreference = 'Stop'

# ─── Constants ────────────────────────────────────────────────────────
$SCRIPT_NAME    = 'test-plugin'
$SCRIPT_VERSION = '1.0.0'
$API_VERSION    = 'v9.2'
$TEST_PREFIX    = 'FSI-MIME-TEST'

# ─── Banner ───────────────────────────────────────────────────────────
Write-Host "`n╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host   "║  FSI Agent Governance — MIME Plugin Integration Tests   ║" -ForegroundColor Cyan
Write-Host   "╚══════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

Write-Host "  Dataverse URL: $DataverseUrl" -ForegroundColor Gray
Write-Host ""

# ─── Resolve Token ────────────────────────────────────────────────────
$baseUrl = $DataverseUrl.TrimEnd('/')

if (-not $AccessToken) {
    try {
        Write-Verbose "No AccessToken provided — acquiring via Get-AzAccessToken."
        $azToken = Get-AzAccessToken -ResourceUrl $baseUrl -ErrorAction Stop
        $AccessToken = $azToken.Token
        Write-Host "  [OK] Token acquired via Az.Accounts" -ForegroundColor Green
    }
    catch {
        throw "Failed to acquire access token. Provide -AccessToken or sign in via Connect-AzAccount. Error: $($_.Exception.Message)"
    }
}

$headers = @{
    'Authorization'    = "Bearer $AccessToken"
    'Content-Type'     = 'application/json'
    'OData-MaxVersion' = '4.0'
    'OData-Version'    = '4.0'
    'Accept'           = 'application/json'
}

$apiBase = "$baseUrl/api/data/$API_VERSION"

# ─── Test Infrastructure ──────────────────────────────────────────────

$testResults = [System.Collections.Generic.List[PSCustomObject]]::new()
$createdAnnotations = [System.Collections.Generic.List[string]]::new()

function New-TestAnnotation {
    <#
    .SYNOPSIS
        Creates a test annotation in Dataverse and records the result.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$TestName,
        [Parameter(Mandatory)][string]$FileName,
        [Parameter(Mandatory)][string]$MimeType,
        [Parameter(Mandatory)][string]$Base64Content,
        [Parameter(Mandatory)][bool]$ShouldSucceed,
        [Parameter()][string]$Description
    )

    $payload = @{
        subject      = "$TEST_PREFIX — $TestName"
        filename     = $FileName
        mimetype     = $MimeType
        documentbody = $Base64Content
        notetext     = "Integration test: $Description"
    }

    $body = $payload | ConvertTo-Json -Depth 5 -Compress

    $passed = $false
    $detail = ''

    try {
        $response = Invoke-RestMethod -Method POST -Uri "$apiBase/annotations" `
            -Headers $headers -Body $body -ErrorAction Stop

        $annotationId = $response.annotationid
        if ($annotationId) {
            $createdAnnotations.Add($annotationId)
        }

        if ($ShouldSucceed) {
            $passed = $true
            $detail = "Upload accepted as expected (ID: $annotationId)"
        }
        else {
            $passed = $false
            $detail = "Upload was accepted but should have been blocked by plugin"
        }
    }
    catch {
        $statusCode = $null
        $errorMessage = $_.Exception.Message

        if ($_.Exception.Response) {
            $statusCode = [int]$_.Exception.Response.StatusCode
        }

        if ($_.ErrorDetails.Message) {
            try {
                $errorDetail = $_.ErrorDetails.Message | ConvertFrom-Json
                $errorMessage = $errorDetail.error.message
            }
            catch {
                $errorMessage = $_.ErrorDetails.Message
            }
        }

        if ($ShouldSucceed) {
            $passed = $false
            $detail = "Upload was blocked but should have succeeded: $errorMessage"
        }
        else {
            $passed = $true
            $detail = "Upload correctly blocked: $errorMessage"
        }
    }

    $result = [PSCustomObject]@{
        Test     = $TestName
        Status   = if ($passed) { '[PASS]' } else { '[FAIL]' }
        Passed   = $passed
        Detail   = $detail
    }

    $testResults.Add($result)

    $color = if ($passed) { 'Green' } else { 'Red' }
    Write-Host "  $($result.Status) $TestName" -ForegroundColor $color
    if (-not $passed) {
        Write-Host "         $detail" -ForegroundColor DarkGray
    }
}

# ─── Generate Test Files ─────────────────────────────────────────────

function ConvertTo-Base64FromBytes {
    param([byte[]]$Bytes)
    return [Convert]::ToBase64String($Bytes)
}

# PDF: valid %PDF header + minimal content
$pdfBytes = [byte[]]@(0x25, 0x50, 0x44, 0x46, 0x2D, 0x31, 0x2E, 0x34) + # %PDF-1.4
            [System.Text.Encoding]::ASCII.GetBytes("`n1 0 obj`n<< /Type /Catalog >>`nendobj`n%%EOF")

# PNG: valid PNG header
$pngBytes = [byte[]]@(0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A) + # PNG signature
            [byte[]]@(0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52)    # IHDR chunk start

# EXE: PE/MZ header disguised as .txt
$exeBytes = [byte[]]@(0x4D, 0x5A, 0x90, 0x00, 0x03, 0x00, 0x00, 0x00) + # MZ header
            [byte[]]@(0x04, 0x00, 0x00, 0x00, 0xFF, 0xFF, 0x00, 0x00)    # PE stub

# Clean text: ASCII-only content
$textContent = "This is a clean text file for FSI governance testing.`nLine 2 of test content.`n"
$textBytes = [System.Text.Encoding]::UTF8.GetBytes($textContent)

# Oversized file: 11 MB of zeros (exceeds 10 MB limit)
$oversizedBytes = [byte[]]::new(11 * 1024 * 1024)

# ─── Execute Tests ────────────────────────────────────────────────────
Write-Host "  Running integration tests..." -ForegroundColor White
Write-Host ""

# Test 1: Valid PDF
New-TestAnnotation `
    -TestName 'PDF-Valid-Signature' `
    -FileName 'test-report.pdf' `
    -MimeType 'application/pdf' `
    -Base64Content (ConvertTo-Base64FromBytes $pdfBytes) `
    -ShouldSucceed $true `
    -Description 'Valid PDF with correct magic bytes — should be accepted'

# Test 2: Valid PNG
New-TestAnnotation `
    -TestName 'PNG-Valid-Signature' `
    -FileName 'test-image.png' `
    -MimeType 'image/png' `
    -Base64Content (ConvertTo-Base64FromBytes $pngBytes) `
    -ShouldSucceed $true `
    -Description 'Valid PNG with correct magic bytes — should be accepted'

# Test 3: EXE disguised as text (should be blocked)
New-TestAnnotation `
    -TestName 'EXE-Disguised-As-Text' `
    -FileName 'readme.txt' `
    -MimeType 'text/plain' `
    -Base64Content (ConvertTo-Base64FromBytes $exeBytes) `
    -ShouldSucceed $false `
    -Description 'PE executable disguised as .txt — should be blocked by signature scan'

# Test 4: Clean text file
New-TestAnnotation `
    -TestName 'Text-Clean-Content' `
    -FileName 'notes.txt' `
    -MimeType 'text/plain' `
    -Base64Content (ConvertTo-Base64FromBytes $textBytes) `
    -ShouldSucceed $true `
    -Description 'Clean text file with no binary content — should be accepted'

# Test 5: Oversized file (should be blocked)
New-TestAnnotation `
    -TestName 'Oversized-File-Guard' `
    -FileName 'large-data.csv' `
    -MimeType 'text/csv' `
    -Base64Content (ConvertTo-Base64FromBytes $oversizedBytes) `
    -ShouldSucceed $false `
    -Description 'File exceeding 10 MB limit — should be blocked by size guard'

# ─── Cleanup ──────────────────────────────────────────────────────────
Write-Host ""

if ($SkipCleanup) {
    Write-Host "  [SKIP] Cleanup skipped — $($createdAnnotations.Count) test annotation(s) remain" -ForegroundColor Yellow
}
else {
    Write-Host "  Cleaning up $($createdAnnotations.Count) test annotation(s)..." -ForegroundColor White

    foreach ($annotationId in $createdAnnotations) {
        try {
            Invoke-RestMethod -Method DELETE -Uri "$apiBase/annotations($annotationId)" `
                -Headers $headers -ErrorAction Stop
            Write-Verbose "Deleted annotation: $annotationId"
        }
        catch {
            Write-Warning "Failed to delete test annotation $annotationId`: $($_.Exception.Message)"
        }
    }

    Write-Host "  [OK] Cleanup complete" -ForegroundColor Green
}

# ─── Summary ──────────────────────────────────────────────────────────
$passCount = ($testResults | Where-Object { $_.Passed }).Count
$failCount = ($testResults | Where-Object { -not $_.Passed }).Count
$totalCount = $testResults.Count

Write-Host ""
Write-Host "  ═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Test Summary: $passCount/$totalCount passed" -ForegroundColor $(if ($failCount -eq 0) { 'Green' } else { 'Red' })
Write-Host "  ═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Display results table
$testResults | Format-Table -Property @(
    @{ Label = 'Status'; Expression = { $_.Status }; Width = 8 }
    @{ Label = 'Test'; Expression = { $_.Test }; Width = 30 }
    @{ Label = 'Detail'; Expression = { $_.Detail } }
) -AutoSize

$result = [PSCustomObject]@{
    Metadata = [PSCustomObject]@{
        ScriptName  = $SCRIPT_NAME
        Version     = $SCRIPT_VERSION
        ExecutedAt  = (Get-Date -Format 'o')
        DataverseUrl = $baseUrl
    }
    TestResults = $testResults.ToArray()
    Summary = [PSCustomObject]@{
        Total  = $totalCount
        Passed = $passCount
        Failed = $failCount
        AllPassed = ($failCount -eq 0)
    }
}

if ($failCount -gt 0) {
    Write-Warning "$failCount test(s) failed. Review results above for details."
}

return $result
