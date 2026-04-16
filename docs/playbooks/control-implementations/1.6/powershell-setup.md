# Control 1.6: Microsoft Purview DSPM for AI - PowerShell Setup

> This playbook provides PowerShell automation guidance for [Control 1.6](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md).

---

## Enable Unified Audit Logging

```powershell
# Connect to Security & Compliance Center
Connect-IPPSSession -UserPrincipalName admin@contoso.com

# Enable unified audit logging (required for DSPM)
Set-AdminAuditLogConfig -UnifiedAuditLogIngestionEnabled $true

# Verify audit logging is enabled
Get-AdminAuditLogConfig | Select-Object UnifiedAuditLogIngestionEnabled
```

---

## Search AI-Related Audit Events

!!! warning "Pagination"
    `Search-UnifiedAuditLog` returns a maximum of 5,000 records per call.
    Use `-SessionId` and `-SessionCommand ReturnLargeSet` for pagination in
    high-volume environments. See [Microsoft documentation](https://learn.microsoft.com/en-us/powershell/module/exchange/search-unifiedauditlog).

```powershell
# Search for Copilot-related audit events
$startDate = (Get-Date).AddDays(-30)
$endDate = Get-Date

# Get recent audit events (filter as needed)
$copilotEvents = Search-UnifiedAuditLog -StartDate $startDate -EndDate $endDate `
    -ResultSize 5000

$copilotEvents = $copilotEvents | Where-Object {
    $_.Operations -match 'Copilot|AI' -or $_.AuditData -match 'Copilot'
}

# Export results for analysis
$copilotEvents | Select-Object CreationDate, UserIds, Operations, AuditData |
    Export-Csv -Path "Copilot-Audit-Events.csv" -NoTypeInformation

# Parse and display recent AI interactions
foreach ($event in $copilotEvents | Select-Object -First 10) {
    $data = $event.AuditData | ConvertFrom-Json
    Write-Host "User: $($event.UserIds) - App: $($data.Application) - Time: $($event.CreationDate)"
}
```

---

## Export DSPM Activity Data

```powershell
# Search for specific sensitive information in AI interactions
$sensitiveSearch = Search-UnifiedAuditLog -StartDate $startDate -EndDate $endDate `
    -ResultSize 5000

# Filter for events with sensitive data
$sensitiveEvents = $sensitiveSearch | ForEach-Object {
    $data = $_.AuditData | ConvertFrom-Json
    if ($data.SensitiveInfoTypes) {
        [PSCustomObject]@{
            Date = $_.CreationDate
            User = $_.UserIds
            SensitiveTypes = ($data.SensitiveInfoTypes -join ", ")
            Application = $data.Application
        }
    }
}

$sensitiveEvents | Export-Csv -Path "DSPM-Sensitive-Events.csv" -NoTypeInformation
```

---

## Verify Policy Status

```powershell
# Get DLP policies for DSPM integration
Get-DlpCompliancePolicy | Where-Object { $_.Mode -eq "Enable" } |
    Select-Object Name, Mode, Enabled, WhenCreated |
    Format-Table

# Check retention policies that may affect AI data
Get-RetentionCompliancePolicy | Where-Object { $_.Enabled -eq $true } |
    Select-Object Name, Mode, RetentionDuration |
    Format-Table
```

---

## Audit Administrator Access to DSPM

```powershell
# Track who has accessed DSPM for AI
$dspmAccess = Search-UnifiedAuditLog -StartDate $startDate -EndDate $endDate `
    -Operations "PageViewed" -ResultSize 1000

$dspmPageViews = $dspmAccess | ForEach-Object {
    $data = $_.AuditData | ConvertFrom-Json
    if ($data.ObjectId -match "DSPM|ai-microsoft-purview") {
        [PSCustomObject]@{
            Date = $_.CreationDate
            User = $_.UserIds
            Page = $data.ObjectId
        }
    }
}

$dspmPageViews | Export-Csv -Path "DSPM-Admin-Access.csv" -NoTypeInformation
```

---

## Generate DSPM Evidence Report

```powershell
# Create comprehensive DSPM evidence export
$evidenceDate = Get-Date -Format "yyyy-MM-dd"
$evidencePath = "DSPM-Evidence-$evidenceDate"

# Create evidence folder
New-Item -ItemType Directory -Path $evidencePath -Force

# Export audit configuration
Get-AdminAuditLogConfig |
    ConvertTo-Json |
    Out-File "$evidencePath\audit-config.json"

# Export DLP policies
Get-DlpCompliancePolicy |
    Select-Object Name, Mode, Enabled, WhenCreated |
    Export-Csv "$evidencePath\dlp-policies.csv" -NoTypeInformation

# Export AI-related events
$aiEvents = Search-UnifiedAuditLog -StartDate (Get-Date).AddDays(-7) -EndDate (Get-Date) `
    -ResultSize 1000 |
    Where-Object { $_.AuditData -match 'Copilot|AI' }

$aiEvents |
    Select-Object CreationDate, UserIds, Operations |
    Export-Csv "$evidencePath\ai-events.csv" -NoTypeInformation

Write-Host "Evidence exported to: $evidencePath"
```

---

## Enhanced DSPM AI Observability - Data Export (Preview)

!!! warning "Preview Feature — Cmdlets may change at GA"
    PowerShell cmdlets for unified DSPM experience are in preview. Command syntax and parameters may change at GA (May 2026).

### Export Activity Explorer Enhanced Data

The unified DSPM experience provides enhanced Activity Explorer exports with additional metadata fields:

```powershell
# Connect to Security & Compliance Center
Connect-IPPSSession -UserPrincipalName admin@contoso.com

# Export enhanced Activity Explorer data for AI interactions
$startDate = (Get-Date).AddDays(-30)
$endDate = Get-Date

# Search for AI interaction events with enhanced metadata
$aiActivityData = Search-UnifiedAuditLog -StartDate $startDate -EndDate $endDate `
    -RecordType "AIPDiscover,AIPFileDeleted,AIPHeartBeat,AIPProtectionAction,AIPSensitivityLabelAction" `
    -ResultSize 5000

# Parse and export with enhanced fields
$enhancedData = $aiActivityData | ForEach-Object {
    $data = $_.AuditData | ConvertFrom-Json
    [PSCustomObject]@{
        EventTimestamp = $_.CreationDate
        User = $_.UserIds
        AgentName = $data.ApplicationDisplayName
        ActivityType = $_.Operations
        DataSource = $data.ObjectId
        SensitivityLabel = $data.SensitivityLabelId
        PolicyActions = ($data.PolicyDetails | ConvertTo-Json -Compress)
        RiskScore = $data.RiskScore  # Preview field - may change at GA
        AccessPattern = $data.AccessPattern  # Preview field - may change at GA
    }
}

$enhancedData | Export-Csv -Path "DSPM-Enhanced-Activity-Export.csv" -NoTypeInformation
Write-Host "Enhanced Activity Explorer data exported to DSPM-Enhanced-Activity-Export.csv"
```

### Generate Weekly DSPM Summary Report

Automated script to generate weekly DSPM summary report combining classic metrics with enhanced observability data:

```powershell
# Generate weekly DSPM summary report
$reportDate = Get-Date -Format "yyyy-MM-dd"
$reportPath = "DSPM-Weekly-Summary-$reportDate.html"

# Collect agent risk summary (preview - API may change)
$agentRiskSummary = @()
# Note: Unified DSPM PowerShell API for agent risk not yet available in preview
# Placeholder for future API once GA - manual export from portal recommended until then

# Collect Activity Explorer summary
$startDate = (Get-Date).AddDays(-7)
$endDate = Get-Date
$weeklyEvents = Search-UnifiedAuditLog -StartDate $startDate -EndDate $endDate `
    -ResultSize 5000 | Where-Object { $_.AuditData -match 'Copilot|AI|Agent' }

$eventSummary = @{
    TotalEvents = $weeklyEvents.Count
    UniqueUsers = ($weeklyEvents.UserIds | Select-Object -Unique).Count
    UniqueAgents = ($weeklyEvents | ForEach-Object {
        ($_.AuditData | ConvertFrom-Json).ApplicationDisplayName
    } | Where-Object { $_ } | Select-Object -Unique).Count
}

# Collect policy violation summary
$policyViolations = $weeklyEvents | Where-Object {
    $data = $_.AuditData | ConvertFrom-Json
    $data.PolicyDetails -and $data.PolicyDetails.Count -gt 0
}

$violationSummary = @{
    TotalViolations = $policyViolations.Count
    DLPViolations = ($policyViolations | Where-Object {
        ($_.AuditData | ConvertFrom-Json).PolicyDetails.PolicyType -eq 'DLP'
    }).Count
}

# Generate HTML report
$htmlReport = @"
<!DOCTYPE html>
<html>
<head><title>DSPM Weekly Summary - $reportDate</title></head>
<body>
<h1>DSPM Weekly Summary Report</h1>
<p>Report Date: $reportDate</p>
<p>Reporting Period: $startDate to $endDate</p>

<h2>Activity Summary</h2>
<ul>
<li>Total AI Events: $($eventSummary.TotalEvents)</li>
<li>Unique Users: $($eventSummary.UniqueUsers)</li>
<li>Unique Agents: $($eventSummary.UniqueAgents)</li>
</ul>

<h2>Policy Violations</h2>
<ul>
<li>Total Violations: $($violationSummary.TotalViolations)</li>
<li>DLP Violations: $($violationSummary.DLPViolations)</li>
</ul>

<p><em>Note: Agent Risk Observability data currently requires manual export from Purview portal. PowerShell API for agent risk scores expected at GA (May 2026).</em></p>
</body>
</html>
"@

$htmlReport | Out-File $reportPath
Write-Host "Weekly DSPM summary report generated: $reportPath"
```

### Export Agent Risk Data (Manual Portal Export Required)

!!! info "PowerShell API Not Yet Available"
    The unified DSPM experience agent risk observability data does not yet have PowerShell cmdlet support in preview. Use portal export until GA.

**Manual Export Steps:**

1. Navigate to **Purview > Data Security Posture Management > AI Risk Dashboard**
2. Click **Export** > **Agent Risk Summary CSV**
3. Save file as `Agent-Risk-Summary-YYYY-MM-DD.csv`
4. Import to PowerShell for processing:

```powershell
# Import manually exported agent risk data
$agentRiskData = Import-Csv -Path "Agent-Risk-Summary-2026-02-06.csv"

# Filter high-risk agents for escalation
$highRiskAgents = $agentRiskData | Where-Object {
    $_.RiskScore -eq 'High' -or [int]$_.RiskScoreNumeric -ge 70
}

# Generate high-risk agent notification email
if ($highRiskAgents.Count -gt 0) {
    $emailBody = "High-risk agents detected in DSPM AI Observability dashboard:`n`n"
    $highRiskAgents | ForEach-Object {
        $emailBody += "- Agent: $($_.AgentName), Risk Score: $($_.RiskScore), Contributing Factors: $($_.RiskFactors)`n"
    }

    # Send notification (configure Send-MailMessage parameters for your environment)
    Write-Host "High-Risk Agent Alert:`n$emailBody"
    # Send-MailMessage -To "compliance@contoso.com" -Subject "DSPM High-Risk Agents Detected" -Body $emailBody
}
```

---

## Complete Configuration Script

```powershell
<#
.SYNOPSIS
    Configures Control 1.6 - Microsoft Purview DSPM for AI

.DESCRIPTION
    This script:
    1. Enables unified audit logging
    2. Validates audit log configuration
    3. Exports AI-related audit events
    4. Generates DSPM evidence report

.PARAMETER EvidencePath
    Path to export evidence files (default: current directory)

.PARAMETER DaysToSearch
    Number of days to search for audit events (default: 30)

.EXAMPLE
    .\Configure-Control-1.6.ps1 -EvidencePath "C:\Compliance\DSPM" -DaysToSearch 30

.NOTES
    Last Updated: January 2026
    Related Control: Control 1.6 - Microsoft Purview DSPM for AI
#>

param(
    [Parameter(Mandatory=$false)]
    [string]$EvidencePath = ".",

    [Parameter(Mandatory=$false)]
    [int]$DaysToSearch = 30
)

try {
    # Connect to Security & Compliance Center
    Connect-IPPSSession

    Write-Host "=== Configuring Control 1.6: Microsoft Purview DSPM for AI ===" -ForegroundColor Cyan

    # Step 1: Enable unified audit logging
    Write-Host "`nStep 1: Enabling unified audit logging..." -ForegroundColor White
    Set-AdminAuditLogConfig -UnifiedAuditLogIngestionEnabled $true
    Write-Host "  [DONE] Unified audit logging enabled" -ForegroundColor Green

    # Step 2: Verify audit logging is enabled
    Write-Host "`nStep 2: Validating audit configuration..." -ForegroundColor White
    $auditConfig = Get-AdminAuditLogConfig
    if ($auditConfig.UnifiedAuditLogIngestionEnabled -eq $true) {
        Write-Host "  [PASS] Unified audit logging is active" -ForegroundColor Green
    } else {
        Write-Host "  [WARN] Unified audit logging may not be fully enabled" -ForegroundColor Yellow
    }

    # Step 3: Search for AI-related audit events
    Write-Host "`nStep 3: Searching for AI-related audit events..." -ForegroundColor White
    $startDate = (Get-Date).AddDays(-$DaysToSearch)
    $endDate = Get-Date

    $copilotEvents = Search-UnifiedAuditLog -StartDate $startDate -EndDate $endDate -ResultSize 5000
    $aiEvents = $copilotEvents | Where-Object {
        $_.Operations -match 'Copilot|AI' -or $_.AuditData -match 'Copilot'
    }
    Write-Host "  [DONE] Found $($aiEvents.Count) AI-related events in last $DaysToSearch days" -ForegroundColor Green

    # Step 4: Create evidence folder
    Write-Host "`nStep 4: Creating evidence export..." -ForegroundColor White
    $evidenceDate = Get-Date -Format "yyyy-MM-dd"
    $evidenceFolder = Join-Path $EvidencePath "DSPM-Evidence-$evidenceDate"
    New-Item -ItemType Directory -Path $evidenceFolder -Force | Out-Null

    # Export audit configuration
    $auditConfig | ConvertTo-Json | Out-File "$evidenceFolder\audit-config.json"

    # Export DLP policies
    Get-DlpCompliancePolicy |
        Select-Object Name, Mode, Enabled, WhenCreated |
        Export-Csv "$evidenceFolder\dlp-policies.csv" -NoTypeInformation

    # Export AI events
    $aiEvents |
        Select-Object CreationDate, UserIds, Operations |
        Export-Csv "$evidenceFolder\ai-events.csv" -NoTypeInformation

    # Export retention policies
    Get-RetentionCompliancePolicy | Where-Object { $_.Enabled -eq $true } |
        Select-Object Name, Mode, RetentionDuration |
        Export-Csv "$evidenceFolder\retention-policies.csv" -NoTypeInformation

    Write-Host "  [DONE] Evidence exported to: $evidenceFolder" -ForegroundColor Green

    # Step 5: Display summary
    Write-Host "`nStep 5: Configuration Summary" -ForegroundColor White
    $summary = @{
        AuditLoggingEnabled = $auditConfig.UnifiedAuditLogIngestionEnabled
        AIEventsFound = $aiEvents.Count
        SearchPeriod = "$startDate to $endDate"
        EvidenceLocation = $evidenceFolder
    }
    $summary | Format-List

    Write-Host "`n[PASS] Control 1.6 configuration completed successfully" -ForegroundColor Green
}
catch {
    Write-Host "[FAIL] Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "[INFO] Stack trace: $($_.ScriptStackTrace)" -ForegroundColor Yellow
    exit 1
}
finally {
    # Disconnect from Security & Compliance Center
    Disconnect-ExchangeOnline -Confirm:$false -ErrorAction SilentlyContinue
}
```

[Back to Control 1.6](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: April 2026 | Version: v1.3*
