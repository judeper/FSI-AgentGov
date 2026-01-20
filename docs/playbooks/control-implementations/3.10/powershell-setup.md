# Control 3.10: Hallucination Feedback Loop - PowerShell Setup

> This playbook provides PowerShell automation scripts for [Control 3.10](../../../controls/pillar-3-reporting/3.10-hallucination-feedback-loop.md).

---

## Prerequisites

```powershell
# Install required modules
Install-Module -Name PnP.PowerShell -Force -AllowClobber
Install-Module -Name Microsoft.Graph -Force -AllowClobber

# Connect to services
Connect-PnPOnline -Url "https://[tenant].sharepoint.com/sites/AI-Governance" -Interactive
```

---

## Create Hallucination Tracking List

```powershell
function New-HallucinationTrackingList {
    param(
        [string]$SiteUrl = "https://[tenant].sharepoint.com/sites/AI-Governance",
        [string]$ListName = "Hallucination Tracking"
    )

    Write-Host "Creating Hallucination Tracking List..." -ForegroundColor Cyan

    Connect-PnPOnline -Url $SiteUrl -Interactive

    # Create list
    $list = New-PnPList -Title $ListName -Template GenericList

    # Add columns
    Add-PnPField -List $ListName -DisplayName "Issue ID" -InternalName "IssueID" -Type Text
    Add-PnPFieldFromXml -List $ListName -FieldXml "<Field Type='Choice' DisplayName='Category'><CHOICES><CHOICE>Factual Error</CHOICE><CHOICE>Fabrication</CHOICE><CHOICE>Outdated</CHOICE><CHOICE>Misattribution</CHOICE><CHOICE>Calculation Error</CHOICE><CHOICE>Conflation</CHOICE><CHOICE>Overconfidence</CHOICE><CHOICE>Misleading</CHOICE></CHOICES></Field>"
    Add-PnPFieldFromXml -List $ListName -FieldXml "<Field Type='Choice' DisplayName='Severity'><CHOICES><CHOICE>Critical</CHOICE><CHOICE>High</CHOICE><CHOICE>Medium</CHOICE><CHOICE>Low</CHOICE></CHOICES></Field>"
    Add-PnPField -List $ListName -DisplayName "Agent Name" -InternalName "AgentName" -Type Text
    Add-PnPField -List $ListName -DisplayName "User Query" -InternalName "UserQuery" -Type Note
    Add-PnPField -List $ListName -DisplayName "Agent Response" -InternalName "AgentResponse" -Type Note
    Add-PnPField -List $ListName -DisplayName "Correct Information" -InternalName "CorrectInfo" -Type Note
    Add-PnPFieldFromXml -List $ListName -FieldXml "<Field Type='Choice' DisplayName='Status'><CHOICES><CHOICE>New</CHOICE><CHOICE>Investigating</CHOICE><CHOICE>Remediation</CHOICE><CHOICE>Closed</CHOICE></CHOICES></Field>"
    Add-PnPField -List $ListName -DisplayName "Assigned To" -InternalName "AssignedTo" -Type User
    Add-PnPFieldFromXml -List $ListName -FieldXml "<Field Type='Choice' DisplayName='Root Cause'><CHOICES><CHOICE>Knowledge Gap</CHOICE><CHOICE>Prompt Issue</CHOICE><CHOICE>Training Data</CHOICE><CHOICE>Source Conflict</CHOICE><CHOICE>Configuration</CHOICE><CHOICE>Unknown</CHOICE></CHOICES></Field>"
    Add-PnPField -List $ListName -DisplayName "Remediation Actions" -InternalName "Remediation" -Type Note
    Add-PnPField -List $ListName -DisplayName "Resolution Date" -InternalName "ResolutionDate" -Type DateTime

    Write-Host "List created successfully" -ForegroundColor Green
}
```

---

## Report Hallucination

```powershell
function New-HallucinationReport {
    param(
        [Parameter(Mandatory=$true)]
        [string]$AgentName,
        [Parameter(Mandatory=$true)]
        [ValidateSet("Factual Error", "Fabrication", "Outdated", "Misattribution", "Calculation Error", "Conflation", "Overconfidence", "Misleading")]
        [string]$Category,
        [Parameter(Mandatory=$true)]
        [ValidateSet("Critical", "High", "Medium", "Low")]
        [string]$Severity,
        [Parameter(Mandatory=$true)]
        [string]$UserQuery,
        [Parameter(Mandatory=$true)]
        [string]$AgentResponse,
        [string]$CorrectInfo = ""
    )

    Write-Host "Reporting hallucination..." -ForegroundColor Cyan

    $issueId = "HAL-$(Get-Date -Format 'yyyyMMdd')-$(Get-Random -Minimum 100 -Maximum 999)"

    $report = @{
        Title = "$AgentName - $Category"
        IssueID = $issueId
        Category = $Category
        Severity = $Severity
        AgentName = $AgentName
        UserQuery = $UserQuery
        AgentResponse = $AgentResponse
        CorrectInfo = $CorrectInfo
        Status = "New"
    }

    Add-PnPListItem -List "Hallucination Tracking" -Values $report

    Write-Host "Hallucination reported: $issueId" -ForegroundColor Green

    if ($Severity -eq "Critical") {
        Write-Host "CRITICAL - Escalation required" -ForegroundColor Red
    }

    return $issueId
}
```

---

## Get Hallucination Metrics

```powershell
function Get-HallucinationMetrics {
    param(
        [int]$DaysBack = 30
    )

    Write-Host "Calculating hallucination metrics..." -ForegroundColor Cyan

    $items = Get-PnPListItem -List "Hallucination Tracking" -PageSize 500

    $recentItems = $items | Where-Object {
        [DateTime]$_["Created"] -ge (Get-Date).AddDays(-$DaysBack)
    }

    $metrics = @{
        TotalReports = $recentItems.Count
        BySeverity = @{
            Critical = ($recentItems | Where-Object { $_["Severity"] -eq "Critical" }).Count
            High = ($recentItems | Where-Object { $_["Severity"] -eq "High" }).Count
            Medium = ($recentItems | Where-Object { $_["Severity"] -eq "Medium" }).Count
            Low = ($recentItems | Where-Object { $_["Severity"] -eq "Low" }).Count
        }
        ByCategory = $recentItems | Group-Object { $_["Category"] } | Select-Object Name, Count
        OpenIssues = ($recentItems | Where-Object { $_["Status"] -ne "Closed" }).Count
    }

    # Calculate MTTR
    $closedItems = $recentItems | Where-Object { $_["Status"] -eq "Closed" -and $_["ResolutionDate"] }
    if ($closedItems.Count -gt 0) {
        $avgHours = ($closedItems | ForEach-Object {
            ([DateTime]$_["ResolutionDate"] - [DateTime]$_["Created"]).TotalHours
        } | Measure-Object -Average).Average
        $metrics.AverageMTTR = [math]::Round($avgHours, 1)
    }

    Write-Host "Metrics Summary (last $DaysBack days):" -ForegroundColor Green
    Write-Host "Total Reports: $($metrics.TotalReports)"
    Write-Host "Critical: $($metrics.BySeverity.Critical) | High: $($metrics.BySeverity.High)"
    Write-Host "Open Issues: $($metrics.OpenIssues)"

    return $metrics
}
```

---

## Generate Hallucination Report

```powershell
function New-HallucinationTrendReport {
    param(
        [int]$DaysBack = 30,
        [string]$OutputPath = ".\HallucinationReport-$(Get-Date -Format 'yyyyMMdd').html"
    )

    Write-Host "Generating hallucination trend report..." -ForegroundColor Cyan

    $metrics = Get-HallucinationMetrics -DaysBack $DaysBack

    $html = @"
<!DOCTYPE html>
<html>
<head>
    <title>Hallucination Feedback Report</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; margin: 40px; }
        h1 { color: #0078d4; }
        .dashboard { display: flex; gap: 20px; flex-wrap: wrap; }
        .card { padding: 20px; background: #f5f5f5; border-radius: 8px; min-width: 120px; }
        .card.critical { background: #fde7e9; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th { background: #0078d4; color: white; padding: 12px; text-align: left; }
        td { border: 1px solid #ddd; padding: 10px; }
    </style>
</head>
<body>
    <h1>Hallucination Feedback Loop Report</h1>
    <p>Period: Last $DaysBack days | Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm')</p>

    <div class="dashboard">
        <div class="card"><h3>Total Reports</h3><p style="font-size:28px;">$($metrics.TotalReports)</p></div>
        <div class="card critical"><h3>Critical</h3><p style="font-size:28px;">$($metrics.BySeverity.Critical)</p></div>
        <div class="card"><h3>Open Issues</h3><p style="font-size:28px;">$($metrics.OpenIssues)</p></div>
        <div class="card"><h3>Avg MTTR</h3><p style="font-size:28px;">$($metrics.AverageMTTR)h</p></div>
    </div>

    <h2>Category Distribution</h2>
    <table>
        <tr><th>Category</th><th>Count</th></tr>
        $($metrics.ByCategory | ForEach-Object { "<tr><td>$($_.Name)</td><td>$($_.Count)</td></tr>" })
    </table>

    <h2>Recommendations</h2>
    <ul>
        $(if ($metrics.BySeverity.Critical -gt 0) { "<li><strong>Critical:</strong> Investigate $($metrics.BySeverity.Critical) critical issues immediately</li>" })
        $(if ($metrics.OpenIssues -gt 10) { "<li><strong>Backlog:</strong> Address $($metrics.OpenIssues) open issues</li>" })
        <li>Review agents with highest hallucination counts</li>
    </ul>
</body>
</html>
"@

    $html | Out-File -FilePath $OutputPath -Encoding UTF8
    Write-Host "Report generated: $OutputPath" -ForegroundColor Green
}
```

---

## Usage Examples

```powershell
# Create tracking list
New-HallucinationTrackingList

# Report a hallucination
New-HallucinationReport -AgentName "Account Bot" -Category "Factual Error" -Severity "High" -UserQuery "What is the current savings rate?" -AgentResponse "The rate is 5.5%" -CorrectInfo "Rate is 4.25%"

# Get metrics
Get-HallucinationMetrics -DaysBack 30

# Generate report
New-HallucinationTrendReport
```

---

## Complete Configuration Script

```powershell
<#
.SYNOPSIS
    Configures Control 3.10 - Hallucination Feedback Loop

.DESCRIPTION
    This script sets up hallucination tracking infrastructure:
    1. Creates SharePoint tracking list
    2. Configures hallucination categories
    3. Generates trend reports

.PARAMETER SiteUrl
    SharePoint site URL for hallucination tracking

.EXAMPLE
    .\Configure-Control-3.10.ps1 -SiteUrl "https://contoso.sharepoint.com/sites/AI-Governance"

.NOTES
    Last Updated: January 2026
    Related Control: Control 3.10 - Hallucination Feedback Loop
#>

param(
    [Parameter(Mandatory=$false)]
    [string]$SiteUrl = "https://[tenant].sharepoint.com/sites/AI-Governance"
)

try {
    # Connect to SharePoint
    Write-Host "Connecting to SharePoint..." -ForegroundColor Cyan
    Connect-PnPOnline -Url $SiteUrl -Interactive

    Write-Host "Configuring Control 3.10 Hallucination Feedback Loop" -ForegroundColor Cyan

    # Check if list exists
    $existingList = Get-PnPList -Identity "Hallucination Tracking" -ErrorAction SilentlyContinue

    if (-not $existingList) {
        Write-Host "Creating Hallucination Tracking List..." -ForegroundColor Yellow
        New-HallucinationTrackingList -SiteUrl $SiteUrl
    } else {
        Write-Host "Hallucination Tracking List already exists" -ForegroundColor Green
    }

    # Get metrics
    Write-Host "`nRetrieving hallucination metrics..." -ForegroundColor Yellow
    $metrics = Get-HallucinationMetrics -DaysBack 30

    # Verify configuration
    $list = Get-PnPList -Identity "Hallucination Tracking"
    $fields = Get-PnPField -List "Hallucination Tracking"

    Write-Host "`nHallucination Tracking Configuration:" -ForegroundColor Cyan
    Write-Host "  List: $($list.Title)" -ForegroundColor Green
    Write-Host "  Fields configured: $($fields.Count)" -ForegroundColor Green
    Write-Host "  Total reports (30 days): $($metrics.TotalReports)" -ForegroundColor Green
    Write-Host "  Open issues: $($metrics.OpenIssues)" -ForegroundColor $(if ($metrics.OpenIssues -gt 0) { "Yellow" } else { "Green" })

    Write-Host "`n[PASS] Control 3.10 configuration completed successfully" -ForegroundColor Green
}
catch {
    Write-Host "[FAIL] Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "[INFO] Stack trace: $($_.ScriptStackTrace)" -ForegroundColor Yellow
    exit 1
}
finally {
    # Cleanup SharePoint connection
    Disconnect-PnPOnline -ErrorAction SilentlyContinue
}
```

---

## Next Steps

- [Portal Walkthrough](./portal-walkthrough.md) - Manual configuration
- [Verification & Testing](./verification-testing.md) - Test procedures
- [Troubleshooting](./troubleshooting.md) - Common issues

---

*Updated: January 2026 | Version: v1.1*
