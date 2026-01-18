# Control 2.5: Testing, Validation, and Quality Assurance - PowerShell Setup

> This playbook provides PowerShell automation scripts for [Control 2.5](../../../controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md).

---

## Automated Agent Test Script

```powershell
# Copilot Studio Agent Test Script
param(
    [string]$AgentEndpoint,
    [string]$TestDataPath
)

# Load test cases
$testCases = Import-Csv -Path $TestDataPath
$results = @()

foreach ($test in $testCases) {
    Write-Host "Running test: $($test.TestName)" -ForegroundColor Cyan

    # Send test message to agent
    $body = @{
        message = $test.Input
        userId = "test-user-001"
    } | ConvertTo-Json

    $startTime = Get-Date

    try {
        $response = Invoke-RestMethod -Uri $AgentEndpoint `
            -Method Post `
            -Body $body `
            -ContentType "application/json" `
            -TimeoutSec 30

        $responseTime = ((Get-Date) - $startTime).TotalMilliseconds

        # Validate response
        $passed = $response.text -like "*$($test.ExpectedContains)*"

        $results += [PSCustomObject]@{
            TestName = $test.TestName
            Input = $test.Input
            Expected = $test.ExpectedContains
            Actual = $response.text
            ResponseTime = $responseTime
            Status = if ($passed) { "PASS" } else { "FAIL" }
            Timestamp = Get-Date
        }
    }
    catch {
        $results += [PSCustomObject]@{
            TestName = $test.TestName
            Input = $test.Input
            Status = "ERROR"
            Error = $_.Exception.Message
            Timestamp = Get-Date
        }
    }
}

# Generate report
$passCount = ($results | Where-Object Status -eq "PASS").Count
$failCount = ($results | Where-Object Status -eq "FAIL").Count
$errorCount = ($results | Where-Object Status -eq "ERROR").Count

Write-Host "`n=== Test Summary ===" -ForegroundColor Cyan
Write-Host "Total: $($results.Count) | Pass: $passCount | Fail: $failCount | Error: $errorCount"

# Export results
$results | Export-Csv -Path "TestResults_$(Get-Date -Format 'yyyyMMdd_HHmm').csv" -NoTypeInformation

# Return exit code for CI/CD
if ($failCount -gt 0 -or $errorCount -gt 0) {
    exit 1
}
```

---

## Performance Test Script

```powershell
# Performance Test Script
param(
    [string]$AgentEndpoint,
    [int]$ConcurrentUsers = 50,
    [int]$Duration = 300  # 5 minutes
)

$jobs = @()
$startTime = Get-Date
$endTime = $startTime.AddSeconds($Duration)

# Simulate concurrent users
for ($i = 1; $i -le $ConcurrentUsers; $i++) {
    $jobs += Start-Job -ScriptBlock {
        param($endpoint, $userId, $endTime)

        $results = @()
        while ((Get-Date) -lt $endTime) {
            $start = Get-Date
            try {
                $response = Invoke-RestMethod -Uri $endpoint -Method Post `
                    -Body (@{message="Test query"; userId=$userId} | ConvertTo-Json) `
                    -ContentType "application/json" -TimeoutSec 30

                $results += @{
                    ResponseTime = ((Get-Date) - $start).TotalMilliseconds
                    Success = $true
                }
            }
            catch {
                $results += @{
                    ResponseTime = 30000
                    Success = $false
                }
            }
            Start-Sleep -Milliseconds 500
        }
        return $results
    } -ArgumentList $AgentEndpoint, "user-$i", $endTime
}

# Wait for completion
$allResults = $jobs | Wait-Job | Receive-Job

# Calculate metrics
$responseTimes = $allResults | Where-Object { $_.Success } | ForEach-Object { $_.ResponseTime }
$p50 = ($responseTimes | Sort-Object)[[int]($responseTimes.Count * 0.5)]
$p95 = ($responseTimes | Sort-Object)[[int]($responseTimes.Count * 0.95)]
$successRate = ($allResults | Where-Object Success).Count / $allResults.Count * 100

Write-Host "=== Performance Results ===" -ForegroundColor Cyan
Write-Host "P50 Response Time: $([math]::Round($p50, 0))ms"
Write-Host "P95 Response Time: $([math]::Round($p95, 0))ms"
Write-Host "Success Rate: $([math]::Round($successRate, 2))%"
```

---

## Golden Dataset Regression Test

```powershell
# Golden Dataset Regression Test
param(
    [Parameter(Mandatory=$true)]
    [string]$AgentEndpoint,
    [Parameter(Mandatory=$true)]
    [string]$GoldenDatasetPath,
    [decimal]$MinPassRate = 0.95,
    [decimal]$MinRegulatoryRate = 1.0
)

$dataset = Import-Csv -Path $GoldenDatasetPath
$results = @()

foreach ($entry in $dataset) {
    Write-Host "Testing: $($entry.entry_id) - $($entry.category)" -ForegroundColor Cyan

    try {
        $body = @{
            message = $entry.question
            userId = "regression-test"
        } | ConvertTo-Json

        $response = Invoke-RestMethod -Uri $AgentEndpoint `
            -Method Post `
            -Body $body `
            -ContentType "application/json" `
            -TimeoutSec 30

        # Check if expected content is in response
        $passed = $false
        if ($entry.expected_answer_contains) {
            $keywords = $entry.expected_answer_contains -split '\|'
            foreach ($keyword in $keywords) {
                if ($response.text -like "*$keyword*") {
                    $passed = $true
                    break
                }
            }
        }

        $results += [PSCustomObject]@{
            EntryId = $entry.entry_id
            Category = $entry.category
            Question = $entry.question
            Passed = $passed
            IsRegulatory = $entry.regulatory_flag -eq "true"
            Response = $response.text
        }
    }
    catch {
        $results += [PSCustomObject]@{
            EntryId = $entry.entry_id
            Category = $entry.category
            Passed = $false
            IsRegulatory = $entry.regulatory_flag -eq "true"
            Error = $_.Exception.Message
        }
    }
}

# Calculate rates
$passRate = ($results | Where-Object Passed).Count / $results.Count
$regulatoryResults = $results | Where-Object IsRegulatory
$regulatoryRate = if ($regulatoryResults.Count -gt 0) {
    ($regulatoryResults | Where-Object Passed).Count / $regulatoryResults.Count
} else { 1.0 }

Write-Host "`n=== Regression Test Results ===" -ForegroundColor Cyan
Write-Host "Overall Pass Rate: $([math]::Round($passRate * 100, 2))%"
Write-Host "Regulatory Pass Rate: $([math]::Round($regulatoryRate * 100, 2))%"

# Export results
$results | Export-Csv -Path "RegressionResults_$(Get-Date -Format 'yyyyMMdd_HHmm').csv" -NoTypeInformation

# Check thresholds
if ($passRate -lt $MinPassRate) {
    Write-Error "REGRESSION DETECTED: Pass rate $([math]::Round($passRate * 100, 2))% below threshold $($MinPassRate * 100)%"
    exit 1
}

if ($regulatoryRate -lt $MinRegulatoryRate) {
    Write-Error "CRITICAL: Regulatory entries failing - deployment blocked"
    exit 2
}

Write-Host "All regression tests passed" -ForegroundColor Green
exit 0
```

---

## Generate Test Report

```powershell
# Comprehensive Test Report Generator
param(
    [string]$AgentName,
    [string]$TestResultsPath,
    [string]$OutputPath = ".\TestReport_$(Get-Date -Format 'yyyyMMdd').html"
)

# Load test results
$results = Import-Csv -Path $TestResultsPath

# Calculate statistics
$totalTests = $results.Count
$passed = ($results | Where-Object Status -eq "PASS").Count
$failed = ($results | Where-Object Status -eq "FAIL").Count
$passRate = [math]::Round(($passed / $totalTests) * 100, 2)

# Generate HTML report
$html = @"
<!DOCTYPE html>
<html>
<head>
<title>Agent Test Report - $AgentName</title>
<style>
body { font-family: 'Segoe UI', sans-serif; margin: 20px; }
h1 { color: #0078d4; }
.summary { display: flex; gap: 20px; margin: 20px 0; }
.metric { padding: 20px; background: #f3f2f1; border-radius: 8px; text-align: center; }
.metric.pass { background: #dff6dd; }
.metric.fail { background: #fed9cc; }
table { width: 100%; border-collapse: collapse; margin-top: 20px; }
th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
th { background: #0078d4; color: white; }
.status-pass { color: green; font-weight: bold; }
.status-fail { color: red; font-weight: bold; }
</style>
</head>
<body>
<h1>Agent Test Report</h1>
<p><strong>Agent:</strong> $AgentName</p>
<p><strong>Report Date:</strong> $(Get-Date)</p>

<div class="summary">
<div class="metric"><h3>Total Tests</h3><p style="font-size:24px;">$totalTests</p></div>
<div class="metric pass"><h3>Passed</h3><p style="font-size:24px;">$passed</p></div>
<div class="metric fail"><h3>Failed</h3><p style="font-size:24px;">$failed</p></div>
<div class="metric"><h3>Pass Rate</h3><p style="font-size:24px;">$passRate%</p></div>
</div>

<h2>Test Results</h2>
<table>
<tr><th>Test Name</th><th>Status</th><th>Response Time</th><th>Details</th></tr>
$(
$results | ForEach-Object {
    $statusClass = if ($_.Status -eq "PASS") { "status-pass" } else { "status-fail" }
    "<tr><td>$($_.TestName)</td><td class='$statusClass'>$($_.Status)</td><td>$($_.ResponseTime)ms</td><td>$($_.Actual)</td></tr>"
}
)
</table>
</body>
</html>
"@

$html | Out-File -FilePath $OutputPath -Encoding UTF8
Write-Host "Report generated: $OutputPath" -ForegroundColor Green
```

---

## Azure DevOps Pipeline Integration

```yaml
# test-stage.yml
- stage: Test
  displayName: 'Run Agent Tests'
  jobs:
  - job: AutomatedTests
    steps:
    - task: PowerShell@2
      displayName: 'Run Functional Tests'
      inputs:
        filePath: 'tests/Run-AgentTests.ps1'
        arguments: '-AgentEndpoint "$(AgentEndpoint)" -TestDataPath "tests/testcases.csv"'

    - task: PowerShell@2
      displayName: 'Run Golden Dataset Regression'
      inputs:
        filePath: 'tests/Run-GoldenDatasetTest.ps1'
        arguments: '-AgentEndpoint "$(AgentEndpoint)" -GoldenDatasetPath "tests/golden-dataset.csv"'

    - task: PublishTestResults@2
      displayName: 'Publish Test Results'
      inputs:
        testResultsFormat: 'JUnit'
        testResultsFiles: '**/TestResults*.xml'
```

---

## Regression Test Configuration

```yaml
# regression-test-config.yml
regression_testing:
  trigger:
    - on_knowledge_source_update
    - on_prompt_change
    - on_action_change
    - scheduled_daily

  golden_dataset:
    path: "./golden-datasets/agent-cs-001.csv"
    minimum_pass_rate: 0.95

  evaluation_metrics:
    - accuracy
    - groundedness
    - regulatory_compliance

  notifications:
    on_regression:
      - ai-governance-team@company.com
      - agent-owner@company.com
    on_critical_failure:
      - compliance@company.com
      - ciso@company.com

  blocking:
    block_deployment_on_failure: true
    minimum_regulatory_score: 1.0  # 100% required
```

---

## Related Playbooks

- [Portal Walkthrough](./portal-walkthrough.md) - Step-by-step portal configuration
- [Verification & Testing](./verification-testing.md) - Test procedures
- [Troubleshooting](./troubleshooting.md) - Common issues and solutions

---

*Updated: January 2026 | Version: v1.1*
