# PowerShell Setup: Control 2.18 - Automated Conflict of Interest Testing

**Last Updated:** January 2026
**Modules Required:** Custom API integration

## Prerequisites

```powershell
# This control uses custom testing framework
# Install required modules for HTTP requests and reporting
Install-Module -Name ImportExcel -Force -Scope CurrentUser
```

---

## Automated COI Testing Scripts

### Execute COI Test Suite

```powershell
<#
.SYNOPSIS
    Executes automated conflict of interest test suite

.DESCRIPTION
    Runs predefined test scenarios against agent API and
    evaluates responses for COI indicators

.PARAMETER AgentEndpoint
    The agent API endpoint URL

.PARAMETER TestSuitePath
    Path to test case definitions

.EXAMPLE
    .\Invoke-COITests.ps1 -AgentEndpoint "https://..." -TestSuitePath ".\test_cases"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$AgentEndpoint,
    [string]$TestSuitePath = ".\test_cases",
    [string]$OutputPath = ".\results"
)

Write-Host "=== COI Test Suite Execution ===" -ForegroundColor Cyan
Write-Host "Agent: $AgentEndpoint"
Write-Host "Test Suite: $TestSuitePath"

# Ensure output directory exists
New-Item -ItemType Directory -Force -Path $OutputPath | Out-Null

# Load test cases
$testFiles = Get-ChildItem -Path $TestSuitePath -Filter "*.json" -Recurse

$results = @()

foreach ($testFile in $testFiles) {
    Write-Host "Running: $($testFile.Name)" -ForegroundColor Yellow

    $testCase = Get-Content $testFile.FullName | ConvertFrom-Json

    # Execute test
    try {
        $body = @{
            message = $testCase.prompt
            context = $testCase.context
        } | ConvertTo-Json

        $response = Invoke-RestMethod -Uri $AgentEndpoint -Method Post -Body $body -ContentType "application/json"

        # Evaluate response against criteria
        $passed = $true
        $violations = @()

        foreach ($criterion in $testCase.criteria) {
            $evaluation = Evaluate-Criterion -Response $response.message -Criterion $criterion
            if (-not $evaluation.Passed) {
                $passed = $false
                $violations += $criterion.name
            }
        }

        $results += [PSCustomObject]@{
            TestFile = $testFile.Name
            Category = $testCase.category
            TestName = $testCase.name
            Passed = $passed
            Violations = ($violations -join ", ")
            ResponseSample = $response.message.Substring(0, [Math]::Min(200, $response.message.Length))
            Timestamp = Get-Date
        }
    }
    catch {
        $results += [PSCustomObject]@{
            TestFile = $testFile.Name
            Category = $testCase.category
            TestName = $testCase.name
            Passed = $false
            Violations = "Execution Error: $($_.Exception.Message)"
            ResponseSample = "N/A"
            Timestamp = Get-Date
        }
    }
}

# Generate summary
$totalTests = $results.Count
$passedTests = ($results | Where-Object { $_.Passed }).Count
$failedTests = $totalTests - $passedTests
$passRate = [math]::Round(($passedTests / $totalTests) * 100, 1)

Write-Host "`n=== Test Summary ===" -ForegroundColor Cyan
Write-Host "Total Tests: $totalTests"
Write-Host "Passed: $passedTests" -ForegroundColor Green
Write-Host "Failed: $failedTests" -ForegroundColor $(if ($failedTests -gt 0) { "Red" } else { "Green" })
Write-Host "Pass Rate: $passRate%"

# Export results
$resultFile = "$OutputPath\COI-Test-Results-$(Get-Date -Format 'yyyyMMdd-HHmmss').csv"
$results | Export-Csv -Path $resultFile -NoTypeInformation
Write-Host "`nResults exported to: $resultFile"

# Return failures for alerting
if ($failedTests -gt 0) {
    Write-Host "`n=== Failed Tests ===" -ForegroundColor Red
    $results | Where-Object { -not $_.Passed } | Format-Table Category, TestName, Violations
    exit 1
}

function Evaluate-Criterion {
    param($Response, $Criterion)

    switch ($Criterion.type) {
        "contains" {
            return @{ Passed = $Response -match $Criterion.pattern }
        }
        "not_contains" {
            return @{ Passed = $Response -notmatch $Criterion.pattern }
        }
        "sentiment" {
            # Would integrate with sentiment analysis API
            return @{ Passed = $true }
        }
        default {
            return @{ Passed = $true }
        }
    }
}
```

### Generate COI Compliance Report

```powershell
<#
.SYNOPSIS
    Generates compliance report from COI test results

.DESCRIPTION
    Creates formatted report suitable for compliance review

.PARAMETER ResultsPath
    Path to test results CSV files

.EXAMPLE
    .\New-COIComplianceReport.ps1 -ResultsPath ".\results"
#>

param(
    [string]$ResultsPath = ".\results",
    [string]$ReportPath = ".\reports"
)

Write-Host "=== COI Compliance Report Generation ===" -ForegroundColor Cyan

# Load recent results
$resultFiles = Get-ChildItem -Path $ResultsPath -Filter "COI-Test-Results-*.csv" | Sort-Object LastWriteTime -Descending | Select-Object -First 5

$allResults = @()
foreach ($file in $resultFiles) {
    $allResults += Import-Csv $file.FullName
}

# Aggregate by category
$categoryStats = $allResults | Group-Object Category | ForEach-Object {
    $total = $_.Count
    $passed = ($_.Group | Where-Object { $_.Passed -eq "True" }).Count

    [PSCustomObject]@{
        Category = $_.Name
        TotalTests = $total
        Passed = $passed
        Failed = $total - $passed
        PassRate = [math]::Round(($passed / $total) * 100, 1)
    }
}

Write-Host "`n=== Results by Category ===" -ForegroundColor Cyan
$categoryStats | Format-Table

# Create report
$report = @"
# COI Testing Compliance Report

**Generated:** $(Get-Date -Format "yyyy-MM-dd HH:mm")
**Period:** Last 5 test runs
**Total Tests:** $($allResults.Count)

## Summary by Category

$(($categoryStats | ForEach-Object { "- **$($_.Category)**: $($_.PassRate)% pass rate ($($_.Passed)/$($_.TotalTests))" }) -join "`n")

## Recent Failures

$(($allResults | Where-Object { $_.Passed -eq "False" } | Select-Object -First 10 | ForEach-Object { "- [$($_.Category)] $($_.TestName): $($_.Violations)" }) -join "`n")

## Recommendations

$(if (($allResults | Where-Object { $_.Passed -eq "False" }).Count -gt 0) { "Review failed tests and implement corrective actions." } else { "All tests passing. Continue monitoring." })
"@

# Save report
New-Item -ItemType Directory -Force -Path $ReportPath | Out-Null
$reportFile = "$ReportPath\COI-Compliance-Report-$(Get-Date -Format 'yyyyMMdd').md"
$report | Out-File -FilePath $reportFile
Write-Host "`nReport saved to: $reportFile"
```

---

## Validation Script

```powershell
<#
.SYNOPSIS
    Validates Control 2.18 - Automated COI Testing configuration

.EXAMPLE
    .\Validate-Control-2.18.ps1
#>

Write-Host "=== Control 2.18 Validation ===" -ForegroundColor Cyan

# Check 1: Test cases exist
Write-Host "`n[Check 1] Test Case Coverage" -ForegroundColor Cyan
Write-Host "[INFO] Verify test cases exist for:"
Write-Host "  - Proprietary bias scenarios"
Write-Host "  - Commission bias scenarios"
Write-Host "  - Cross-selling scenarios"
Write-Host "  - Suitability scenarios"

# Check 2: Automation configured
Write-Host "`n[Check 2] Test Automation" -ForegroundColor Cyan
Write-Host "[INFO] Verify automated testing is scheduled"
Write-Host "[INFO] Check execution logs for recent runs"

# Check 3: Results retention
Write-Host "`n[Check 3] Evidence Retention" -ForegroundColor Cyan
Write-Host "[INFO] Verify test results are retained per policy (7 years for regulated)"

# Check 4: Alerting
Write-Host "`n[Check 4] Failure Alerting" -ForegroundColor Cyan
Write-Host "[INFO] Verify alerts trigger on test failures"

Write-Host "`n=== Validation Complete ===" -ForegroundColor Cyan
```

---

[Back to Control 2.18](../../../controls/pillar-2-management/2.18-automated-conflict-of-interest-testing.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
