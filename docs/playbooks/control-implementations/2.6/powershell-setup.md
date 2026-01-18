# Control 2.6: Model Risk Management - PowerShell Setup

> This playbook provides PowerShell automation scripts for [Control 2.6](../../../controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md).

---

## Model Performance Monitoring Script

```powershell
# Model Performance Monitoring Script
param(
    [string]$AgentId,
    [int]$DaysToAnalyze = 30
)

# Connect to Dataverse (assumes connection established)
$startDate = (Get-Date).AddDays(-$DaysToAnalyze)

# Calculate metrics
$metrics = @{
    TotalConversations = 0
    SuccessfulResolutions = 0
    Escalations = 0
    AverageResponseTime = 0
    UserSatisfactionAvg = 0
}

# (Query and calculate actual values from conversation logs)

# Calculate performance scores
$resolutionRate = $metrics.SuccessfulResolutions / $metrics.TotalConversations * 100
$escalationRate = $metrics.Escalations / $metrics.TotalConversations * 100

# Determine status
$status = "Green"
if ($resolutionRate -lt 90 -or $escalationRate -gt 15) {
    $status = "Yellow"
}
if ($resolutionRate -lt 80 -or $escalationRate -gt 25) {
    $status = "Red"
}

# Output report
Write-Host "=== Model Performance Report ===" -ForegroundColor Cyan
Write-Host "Agent: $AgentId"
Write-Host "Period: Last $DaysToAnalyze days"
Write-Host "Status: $status"
Write-Host ""
Write-Host "Metrics:"
Write-Host "  Resolution Rate: $([math]::Round($resolutionRate, 2))%"
Write-Host "  Escalation Rate: $([math]::Round($escalationRate, 2))%"
Write-Host "  Avg Response Time: $($metrics.AverageResponseTime)ms"
Write-Host "  User Satisfaction: $($metrics.UserSatisfactionAvg)/5.0"

# Alert if threshold breached
if ($status -ne "Green") {
    Write-Host "`nALERT: Performance threshold breached!" -ForegroundColor $status
    # Send notification (Teams, email, etc.)
}
```

---

## Agent Manifest Export Script

```powershell
# Export Agent Manifest for Version Control
param(
    [Parameter(Mandatory=$true)]
    [string]$AgentId,
    [string]$OutputPath = ".\manifests"
)

# Ensure output directory exists
New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$filename = "$OutputPath\$AgentId-manifest-$timestamp.json"

# Build manifest structure
$manifest = @{
    exportDate = Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ"
    agentId = $AgentId
    version = "1.0.0"  # Update based on your versioning
    components = @{
        systemInstructions = "[Export from Copilot Studio]"
        topics = @()
        knowledgeSources = @()
        actions = @()
        settings = @{}
    }
}

# Export manifest
$manifest | ConvertTo-Json -Depth 10 | Out-File -FilePath $filename -Encoding UTF8

Write-Host "Manifest exported: $filename" -ForegroundColor Green
Write-Host "Commit this file to version control" -ForegroundColor Yellow
```

---

## MRM Compliance Report Generator

```powershell
# Model Risk Management Compliance Report
param(
    [string]$ModelInventoryPath,
    [string]$OutputPath = ".\MRM_Report_$(Get-Date -Format 'yyyyMMdd').html"
)

# Load model inventory
$models = Import-Csv -Path $ModelInventoryPath

# Calculate compliance metrics
$totalModels = $models.Count
$tier1 = ($models | Where-Object Tier -eq "1").Count
$tier2 = ($models | Where-Object Tier -eq "2").Count
$tier3 = ($models | Where-Object Tier -eq "3").Count

$currentDate = Get-Date
$validationCurrent = ($models | Where-Object {
    [datetime]$_.NextValidationDue -gt $currentDate
}).Count
$validationOverdue = ($models | Where-Object {
    [datetime]$_.NextValidationDue -le $currentDate
}).Count

$performanceGreen = ($models | Where-Object PerformanceStatus -eq "Green").Count
$performanceYellow = ($models | Where-Object PerformanceStatus -eq "Yellow").Count
$performanceRed = ($models | Where-Object PerformanceStatus -eq "Red").Count

# Generate HTML report
$html = @"
<!DOCTYPE html>
<html>
<head>
<title>Model Risk Management Report</title>
<style>
body { font-family: 'Segoe UI', sans-serif; margin: 20px; }
h1, h2 { color: #0078d4; }
.dashboard { display: flex; gap: 20px; flex-wrap: wrap; margin: 20px 0; }
.card { padding: 20px; background: #f3f2f1; border-radius: 8px; min-width: 150px; }
.card.green { background: #dff6dd; }
.card.yellow { background: #fff4ce; }
.card.red { background: #fed9cc; }
table { width: 100%; border-collapse: collapse; margin-top: 20px; }
th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
th { background: #0078d4; color: white; }
.overdue { color: red; font-weight: bold; }
</style>
</head>
<body>
<h1>Model Risk Management Compliance Report</h1>
<p>Report Date: $(Get-Date -Format 'MMMM dd, yyyy')</p>

<h2>Model Inventory Summary</h2>
<div class="dashboard">
<div class="card"><h3>Total Models</h3><p style="font-size:28px;">$totalModels</p></div>
<div class="card"><h3>Tier 1 (High)</h3><p style="font-size:28px;">$tier1</p></div>
<div class="card"><h3>Tier 2 (Medium)</h3><p style="font-size:28px;">$tier2</p></div>
<div class="card"><h3>Tier 3 (Low)</h3><p style="font-size:28px;">$tier3</p></div>
</div>

<h2>Validation Status</h2>
<div class="dashboard">
<div class="card green"><h3>Current</h3><p style="font-size:28px;">$validationCurrent</p></div>
<div class="card red"><h3>Overdue</h3><p style="font-size:28px;">$validationOverdue</p></div>
</div>

<h2>Performance Status</h2>
<div class="dashboard">
<div class="card green"><h3>Green</h3><p style="font-size:28px;">$performanceGreen</p></div>
<div class="card yellow"><h3>Yellow</h3><p style="font-size:28px;">$performanceYellow</p></div>
<div class="card red"><h3>Red</h3><p style="font-size:28px;">$performanceRed</p></div>
</div>

<h2>Model Details</h2>
<table>
<tr><th>Model ID</th><th>Name</th><th>Tier</th><th>Owner</th><th>Last Validation</th><th>Next Due</th><th>Status</th></tr>
$(
$models | ForEach-Object {
    $overdueClass = if ([datetime]$_.NextValidationDue -le $currentDate) { "overdue" } else { "" }
    "<tr><td>$($_.ModelID)</td><td>$($_.ModelName)</td><td>$($_.Tier)</td><td>$($_.ModelOwner)</td><td>$($_.LastValidation)</td><td class='$overdueClass'>$($_.NextValidationDue)</td><td>$($_.PerformanceStatus)</td></tr>"
}
)
</table>
</body>
</html>
"@

$html | Out-File -FilePath $OutputPath -Encoding UTF8
Write-Host "MRM Report generated: $OutputPath" -ForegroundColor Green
```

---

## Model Change Monitoring

```yaml
# Model Change Monitoring Checklist
model_change:
  agent_id: "[Agent ID]"
  previous_model: "GPT-4o"
  new_model: "GPT-5"
  change_date: "[Date]"

  baseline_metrics:
    accuracy_before: "[%]"
    accuracy_after: "[%]"
    response_time_before: "[ms]"
    response_time_after: "[ms]"
    user_satisfaction_before: "[score]"
    user_satisfaction_after: "[score]"

  validation:
    - [ ] Performance meets or exceeds baseline
    - [ ] No regression in accuracy
    - [ ] Bias testing completed (if Tier 1/2 model)
    - [ ] User acceptance testing passed
    - [ ] MRM notification submitted (if material)
```

---

## Related Playbooks

- [Portal Walkthrough](./portal-walkthrough.md) - Step-by-step portal configuration
- [Verification & Testing](./verification-testing.md) - Validation procedures
- [Troubleshooting](./troubleshooting.md) - Common issues and solutions

---

*Updated: January 2026 | Version: v1.1*
