# PowerShell Setup: Control 2.20 - Adversarial Testing and Red Team Framework

**Last Updated:** January 2026
**Modules Required:** Custom test framework integration

## Prerequisites

```powershell
# Install required modules for HTTP testing and reporting
Install-Module -Name ImportExcel -Force -Scope CurrentUser
```

---

## Automated Testing Scripts

### Execute Adversarial Test Suite

```powershell
<#
.SYNOPSIS
    Executes adversarial test scenarios against AI agent

.DESCRIPTION
    Runs predefined attack scenarios and evaluates responses

.PARAMETER AgentEndpoint
    The agent API endpoint URL

.PARAMETER TestCategory
    Category of tests to run (PromptInjection, Jailbreak, DataExfiltration, etc.)

.EXAMPLE
    .\Invoke-AdversarialTests.ps1 -AgentEndpoint "https://..." -TestCategory "PromptInjection"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$AgentEndpoint,
    [Parameter(Mandatory=$true)]
    [ValidateSet("PromptInjection", "Jailbreak", "DataExfiltration", "BoundaryTesting", "All")]
    [string]$TestCategory,
    [string]$TestSuitePath = ".\adversarial_tests",
    [string]$OutputPath = ".\results"
)

Write-Host "=== Adversarial Test Execution ===" -ForegroundColor Cyan
Write-Host "Agent: $AgentEndpoint"
Write-Host "Category: $TestCategory"
Write-Host "CAUTION: Running in authorized test environment only" -ForegroundColor Yellow

# Ensure output directory exists
New-Item -ItemType Directory -Force -Path $OutputPath | Out-Null

# Load test cases
$testPath = if ($TestCategory -eq "All") { $TestSuitePath } else { "$TestSuitePath\$TestCategory" }
$testFiles = Get-ChildItem -Path $testPath -Filter "*.json" -Recurse

$results = @()

foreach ($testFile in $testFiles) {
    Write-Host "Executing: $($testFile.Name)" -ForegroundColor Yellow

    $testCase = Get-Content $testFile.FullName | ConvertFrom-Json

    try {
        $body = @{
            message = $testCase.attack_prompt
        } | ConvertTo-Json

        $response = Invoke-RestMethod -Uri $AgentEndpoint -Method Post -Body $body -ContentType "application/json"

        # Evaluate response
        $attackSucceeded = $false
        $indicators = @()

        # Check for success indicators (these mean the attack worked - BAD)
        foreach ($indicator in $testCase.success_indicators) {
            if ($response.message -match $indicator) {
                $attackSucceeded = $true
                $indicators += $indicator
            }
        }

        # Check for defense indicators (these mean defense worked - GOOD)
        $defenseWorked = $false
        foreach ($defense in $testCase.defense_indicators) {
            if ($response.message -match $defense) {
                $defenseWorked = $true
            }
        }

        $results += [PSCustomObject]@{
            TestId = $testCase.id
            Category = $testCase.category
            AttackType = $testCase.attack_type
            AttackSucceeded = $attackSucceeded
            DefenseWorked = $defenseWorked
            Status = if ($attackSucceeded) { "FAIL - Vulnerable" } elseif ($defenseWorked) { "PASS - Defended" } else { "REVIEW - Uncertain" }
            IndicatorsMatched = ($indicators -join "; ")
            ResponseSample = $response.message.Substring(0, [Math]::Min(500, $response.message.Length))
            Timestamp = Get-Date
        }
    }
    catch {
        $results += [PSCustomObject]@{
            TestId = $testCase.id
            Category = $testCase.category
            AttackType = $testCase.attack_type
            AttackSucceeded = $false
            DefenseWorked = $false
            Status = "ERROR"
            IndicatorsMatched = $_.Exception.Message
            ResponseSample = "N/A"
            Timestamp = Get-Date
        }
    }
}

# Summary
$totalTests = $results.Count
$passed = ($results | Where-Object { $_.Status -eq "PASS - Defended" }).Count
$failed = ($results | Where-Object { $_.Status -eq "FAIL - Vulnerable" }).Count
$review = ($results | Where-Object { $_.Status -eq "REVIEW - Uncertain" }).Count
$errors = ($results | Where-Object { $_.Status -eq "ERROR" }).Count

Write-Host "`n=== Test Summary ===" -ForegroundColor Cyan
Write-Host "Total Tests: $totalTests"
Write-Host "Passed (Defended): $passed" -ForegroundColor Green
Write-Host "Failed (Vulnerable): $failed" -ForegroundColor $(if ($failed -gt 0) { "Red" } else { "Green" })
Write-Host "Review Needed: $review" -ForegroundColor Yellow
Write-Host "Errors: $errors" -ForegroundColor $(if ($errors -gt 0) { "Yellow" } else { "Green" })

# Export results
$resultFile = "$OutputPath\Adversarial-Results-$TestCategory-$(Get-Date -Format 'yyyyMMdd-HHmmss').csv"
$results | Export-Csv -Path $resultFile -NoTypeInformation
Write-Host "`nResults exported to: $resultFile"

# Show vulnerabilities
if ($failed -gt 0) {
    Write-Host "`n=== VULNERABILITIES IDENTIFIED ===" -ForegroundColor Red
    $results | Where-Object { $_.Status -eq "FAIL - Vulnerable" } | Format-Table TestId, AttackType, IndicatorsMatched
    exit 1
}
```

### Generate Red Team Report

```powershell
<#
.SYNOPSIS
    Generates comprehensive red team testing report

.DESCRIPTION
    Creates formatted report for security and compliance review

.EXAMPLE
    .\New-RedTeamReport.ps1 -ResultsPath ".\results"
#>

param(
    [string]$ResultsPath = ".\results",
    [string]$ReportPath = ".\reports"
)

Write-Host "=== Red Team Report Generation ===" -ForegroundColor Cyan

# Load recent results
$resultFiles = Get-ChildItem -Path $ResultsPath -Filter "Adversarial-Results-*.csv" | Sort-Object LastWriteTime -Descending

$allResults = @()
foreach ($file in $resultFiles) {
    $allResults += Import-Csv $file.FullName
}

# Aggregate statistics
$stats = @{
    TotalTests = $allResults.Count
    Passed = ($allResults | Where-Object { $_.Status -eq "PASS - Defended" }).Count
    Failed = ($allResults | Where-Object { $_.Status -eq "FAIL - Vulnerable" }).Count
    Review = ($allResults | Where-Object { $_.Status -eq "REVIEW - Uncertain" }).Count
}

$stats.PassRate = if ($stats.TotalTests -gt 0) { [math]::Round(($stats.Passed / $stats.TotalTests) * 100, 1) } else { 0 }

# By category
$categoryStats = $allResults | Group-Object Category | ForEach-Object {
    $total = $_.Count
    $failed = ($_.Group | Where-Object { $_.Status -eq "FAIL - Vulnerable" }).Count
    [PSCustomObject]@{
        Category = $_.Name
        Total = $total
        Vulnerable = $failed
        Defended = $total - $failed
    }
}

# Generate report
$report = @"
# Red Team Testing Report

**Generated:** $(Get-Date -Format "yyyy-MM-dd HH:mm")
**Test Period:** [Last 30 days]

## Executive Summary

| Metric | Value |
|--------|-------|
| Total Attack Scenarios Tested | $($stats.TotalTests) |
| Defended Successfully | $($stats.Passed) |
| Vulnerabilities Identified | $($stats.Failed) |
| Defense Rate | $($stats.PassRate)% |

## Results by Attack Category

$(($categoryStats | ForEach-Object { "| $($_.Category) | $($_.Total) | $($_.Vulnerable) | $($_.Defended) |" }) -join "`n")

## Vulnerabilities Requiring Remediation

$(($allResults | Where-Object { $_.Status -eq "FAIL - Vulnerable" } | ForEach-Object { "- **$($_.TestId)** [$($_.Category)]: $($_.AttackType)" }) -join "`n")

## Recommendations

1. Address critical vulnerabilities within 24 hours
2. Re-test after remediation
3. Update attack scenario library based on findings
4. Schedule next red team exercise: [Date]

---
*This report contains sensitive security information. Handle according to information security policy.*
"@

# Save report
New-Item -ItemType Directory -Force -Path $ReportPath | Out-Null
$reportFile = "$ReportPath\RedTeam-Report-$(Get-Date -Format 'yyyyMMdd').md"
$report | Out-File -FilePath $reportFile
Write-Host "Report saved to: $reportFile"
```

---

## Validation Script

```powershell
<#
.SYNOPSIS
    Validates Control 2.20 - Adversarial Testing configuration

.EXAMPLE
    .\Validate-Control-2.20.ps1
#>

Write-Host "=== Control 2.20 Validation ===" -ForegroundColor Cyan

# Check 1: Test environment
Write-Host "`n[Check 1] Isolated Test Environment" -ForegroundColor Cyan
Write-Host "[INFO] Verify red team test environment exists and is isolated"
Write-Host "[INFO] Environment should have no production data"

# Check 2: Attack scenarios
Write-Host "`n[Check 2] Attack Scenario Library" -ForegroundColor Cyan
Write-Host "[INFO] Verify scenarios exist for:"
Write-Host "  - Prompt injection"
Write-Host "  - Jailbreak attempts"
Write-Host "  - Data exfiltration"
Write-Host "  - Boundary testing"

# Check 3: Testing schedule
Write-Host "`n[Check 3] Testing Schedule" -ForegroundColor Cyan
Write-Host "[INFO] Verify testing schedule is established"
Write-Host "[INFO] Check last test date and next scheduled"

# Check 4: Remediation process
Write-Host "`n[Check 4] Remediation Process" -ForegroundColor Cyan
Write-Host "[INFO] Verify SLAs are defined"
Write-Host "[INFO] Check for open vulnerabilities"

# Check 5: Evidence retention
Write-Host "`n[Check 5] Evidence Retention" -ForegroundColor Cyan
Write-Host "[INFO] Verify test results are retained per policy"

Write-Host "`n=== Validation Complete ===" -ForegroundColor Cyan
```

---

[Back to Control 2.20](../../../controls/pillar-2-management/2.20-adversarial-testing-and-red-team-framework.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
