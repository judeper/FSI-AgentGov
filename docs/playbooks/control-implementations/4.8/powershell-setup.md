# Control 4.8: PowerShell Setup — Item-Level Permission Scanning for Agent Knowledge Sources

> **Parent Control:** [Control 4.8 — Item-Level Permission Scanning](../../../controls/pillar-4-sharepoint/4.8-item-level-permission-scanning-agent-knowledge-sources.md)
>
> **Related Playbooks:** [Portal Walkthrough](portal-walkthrough.md) | [Verification & Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

---

## Overview

This playbook provides PowerShell automation for item-level permission scanning of SharePoint libraries connected as Copilot Studio agent knowledge sources. The primary automation is the `Get-KnowledgeSourceItemPermissions.ps1` script from the [FSI-AgentGov-Solutions](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/agent-knowledge-source-scanner) companion repository.

---

## Prerequisites

### Required Modules

```powershell
# Install required PowerShell modules
Install-Module -Name PnP.PowerShell -Scope CurrentUser -Force
Install-Module -Name Microsoft.Graph -Scope CurrentUser -Force
Install-Module -Name ExchangeOnlineManagement -Scope CurrentUser -Force
```

### Required Permissions

| Permission | Scope | Purpose |
|------------|-------|---------|
| SharePoint Admin | Tenant | Access to all site collections for scanning |
| Sites.FullControl.All | Microsoft Graph | Read item-level permissions |
| Group.Read.All | Microsoft Graph | Resolve security group memberships |

### Required Files

Download from [FSI-AgentGov-Solutions/agent-knowledge-source-scanner](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/agent-knowledge-source-scanner):

- `Get-KnowledgeSourceItemPermissions.ps1` — Main scanning script
- `config/item-scope-config.json` — Sensitivity label and risk classification configuration

---

## Step 1: Configure Scan Scope

### 1.1 — Update Sensitivity Label Configuration

Edit `config/item-scope-config.json` to match your organization's sensitivity label taxonomy:

```json
{
  "sensitivityLabels": {
    "critical": [
      "Highly Confidential",
      "Confidential - Financial",
      "Confidential - PII"
    ],
    "high": [
      "Confidential",
      "Internal Only"
    ],
    "medium": [
      "General",
      "Internal"
    ]
  },
  "riskThresholds": {
    "criticalSharingScopes": [
      "Anyone",
      "ExternalUsers",
      "EveryoneExceptExternalUsers"
    ],
    "highSharingScopes": [
      "Anyone",
      "ExternalUsers"
    ]
  },
  "scanSettings": {
    "maxItemsPerLibrary": 10000,
    "includeSubfolders": true,
    "exportPath": "./output",
    "retentionDays": 2555
  }
}
```

!!! warning "Label Names Must Match Exactly"
    Sensitivity label names in the configuration must match your organization's Microsoft Purview sensitivity labels exactly, including capitalization and spacing.

---

## Step 2: Identify Agent Knowledge Sources

### 2.1 — Enumerate Agent Knowledge Sources

Use the following script to identify all SharePoint libraries connected as agent knowledge sources:

```powershell
# Connect to Power Platform
Connect-PnPOnline -Url "https://<tenant>-admin.sharepoint.com" -Interactive

# Get all Copilot Studio agents with SharePoint knowledge sources
# Note: This requires agent-knowledge-source-scanner site-level output
# or manual export from Copilot Studio

$AgentSources = @()

# Option A: Import from agent-knowledge-source-scanner site-level output
# $AgentSources = Import-Csv -Path "./output/agent-knowledge-sources.csv"

# Option B: Manual inventory (update with your agent details)
$AgentSources = @(
    @{
        AgentName    = "HR Policy Agent"
        Environment  = "Production"
        SiteUrl      = "https://contoso.sharepoint.com/sites/hr-policies"
        LibraryPath  = "Documents/Current Policies"
    },
    @{
        AgentName    = "Compliance FAQ Agent"
        Environment  = "Production"
        SiteUrl      = "https://contoso.sharepoint.com/sites/compliance"
        LibraryPath  = "Shared Documents"
    }
)

Write-Host "`nIdentified $($AgentSources.Count) agent knowledge sources for scanning." -ForegroundColor Cyan
```

---

## Step 3: Run Item-Level Permission Scan

### 3.1 — Execute the Scanner

```powershell
# Run Get-KnowledgeSourceItemPermissions.ps1 against each knowledge source
# Refer to FSI-AgentGov-Solutions documentation for full parameter reference

.\Get-KnowledgeSourceItemPermissions.ps1 `
    -AdminUrl "https://<tenant>-admin.sharepoint.com" `
    -ConfigPath "./config/item-scope-config.json" `
    -OutputPath "./output" `
    -Verbose
```

### 3.2 — Manual Item-Level Permission Scan

If the companion script is not available, use this standalone scanning approach:

```powershell
<#
.SYNOPSIS
    Scans a SharePoint library for item-level permission risks.
.DESCRIPTION
    Identifies items with unique permissions in agent knowledge source libraries
    and classifies risk based on sensitivity labels and sharing scope.
.PARAMETER SiteUrl
    The SharePoint site URL containing the knowledge source library.
.PARAMETER LibraryName
    The name of the document library to scan.
.PARAMETER OutputPath
    Path to export the scan results CSV.
#>
param(
    [Parameter(Mandatory = $true)]
    [string]$SiteUrl,

    [Parameter(Mandatory = $true)]
    [string]$LibraryName,

    [Parameter(Mandatory = $false)]
    [string]$OutputPath = "./output"
)

try {
    # Connect to the site
    Write-Host "Connecting to $SiteUrl..." -ForegroundColor Cyan
    Connect-PnPOnline -Url $SiteUrl -Interactive

    # Get all items in the library
    Write-Host "Scanning library '$LibraryName'..." -ForegroundColor Cyan
    $Items = Get-PnPListItem -List $LibraryName -PageSize 500

    $Results = @()
    $ItemCount = 0
    $UniquePermCount = 0

    foreach ($Item in $Items) {
        $ItemCount++
        Write-Progress -Activity "Scanning items" -Status "$ItemCount of $($Items.Count)" `
            -PercentComplete (($ItemCount / $Items.Count) * 100)

        # Check for unique permissions (broken inheritance)
        $HasUniquePerms = Get-PnPProperty -ClientObject $Item -Property "HasUniqueRoleAssignments"

        if ($HasUniquePerms) {
            $UniquePermCount++

            # Get role assignments for this item
            $RoleAssignments = Get-PnPProperty -ClientObject $Item -Property "RoleAssignments"

            # Get sensitivity label if available
            $SensitivityLabel = $Item.FieldValues["_ComplianceTag"]
            if (-not $SensitivityLabel) { $SensitivityLabel = "None" }

            # Analyze sharing scope
            $SharingScopes = @()
            foreach ($Assignment in $RoleAssignments) {
                $Member = Get-PnPProperty -ClientObject $Assignment -Property "Member"
                $MemberName = $Member.Title

                if ($MemberName -match "Everyone except external users") {
                    $SharingScopes += "EEEU"
                }
                elseif ($MemberName -match "Everyone") {
                    $SharingScopes += "Everyone"
                }

                $LoginName = $Member.LoginName
                if ($LoginName -match "anonymous") {
                    $SharingScopes += "Anyone"
                }
                elseif ($LoginName -match "#ext#") {
                    $SharingScopes += "ExternalUser"
                }
            }

            # Classify risk
            $RiskLevel = "LOW"
            if ($SensitivityLabel -match "Highly Confidential|Confidential" -and
                ($SharingScopes -contains "Anyone" -or
                 $SharingScopes -contains "ExternalUser" -or
                 $SharingScopes -contains "EEEU" -or
                 $SharingScopes -contains "Everyone")) {
                $RiskLevel = "CRITICAL"
            }
            elseif ($SharingScopes -contains "Anyone" -or $SharingScopes -contains "ExternalUser") {
                $RiskLevel = "HIGH"
            }
            elseif ($SharingScopes -contains "EEEU" -or $SharingScopes -contains "Everyone") {
                $RiskLevel = "MEDIUM"
            }

            $Results += [PSCustomObject]@{
                SiteUrl          = $SiteUrl
                LibraryName      = $LibraryName
                ItemId           = $Item.Id
                FileName         = $Item.FieldValues["FileLeafRef"]
                FilePath         = $Item.FieldValues["FileRef"]
                SensitivityLabel = $SensitivityLabel
                SharingScopes    = ($SharingScopes -join "; ")
                RiskLevel        = $RiskLevel
                HasUniquePerms   = $true
                ScannedDate      = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
            }
        }
    }

    # Export results
    if (-not (Test-Path $OutputPath)) {
        New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null
    }

    $Timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $OutputFile = Join-Path $OutputPath "item-permissions-scan-$Timestamp.csv"
    $Results | Export-Csv -Path $OutputFile -NoTypeInformation

    # Summary
    Write-Host "`n=== Scan Complete ===" -ForegroundColor Green
    Write-Host "Total items scanned: $ItemCount" -ForegroundColor Cyan
    Write-Host "Items with unique permissions: $UniquePermCount" -ForegroundColor Yellow
    Write-Host "CRITICAL findings: $(($Results | Where-Object { $_.RiskLevel -eq 'CRITICAL' }).Count)" -ForegroundColor Red
    Write-Host "HIGH findings: $(($Results | Where-Object { $_.RiskLevel -eq 'HIGH' }).Count)" -ForegroundColor Red
    Write-Host "MEDIUM findings: $(($Results | Where-Object { $_.RiskLevel -eq 'MEDIUM' }).Count)" -ForegroundColor Yellow
    Write-Host "LOW findings: $(($Results | Where-Object { $_.RiskLevel -eq 'LOW' }).Count)" -ForegroundColor Green
    Write-Host "Results exported to: $OutputFile" -ForegroundColor Cyan
}
catch {
    Write-Host "Error during scan: $_" -ForegroundColor Red
    throw
}
finally {
    Disconnect-PnPOnline -ErrorAction SilentlyContinue
}
```

---

## Step 4: Review Scan Output

### 4.1 — Load and Analyze Results

```powershell
# Load scan results
$ScanResults = Import-Csv -Path "./output/item-permissions-scan-*.csv" |
    Sort-Object -Property @{Expression = {
        switch ($_.RiskLevel) {
            "CRITICAL" { 0 }
            "HIGH" { 1 }
            "MEDIUM" { 2 }
            "LOW" { 3 }
        }
    }}

# Display summary by risk level
Write-Host "`n=== Risk Summary ===" -ForegroundColor Cyan
$ScanResults | Group-Object RiskLevel | ForEach-Object {
    $Color = switch ($_.Name) {
        "CRITICAL" { "Red" }
        "HIGH" { "Red" }
        "MEDIUM" { "Yellow" }
        "LOW" { "Green" }
    }
    Write-Host "$($_.Name): $($_.Count) items" -ForegroundColor $Color
}

# Display CRITICAL items requiring immediate action
$CriticalItems = $ScanResults | Where-Object { $_.RiskLevel -eq "CRITICAL" }
if ($CriticalItems) {
    Write-Host "`n=== CRITICAL Items — Immediate Action Required ===" -ForegroundColor Red
    $CriticalItems | Format-Table FileName, SensitivityLabel, SharingScopes, FilePath -AutoSize
}
```

### 4.2 — Generate Compliance Report

```powershell
# Generate formatted compliance report
$ReportPath = "./output/compliance-report-$(Get-Date -Format 'yyyyMMdd').md"

$Report = @"
# Item-Level Permission Scan Report

**Date:** $(Get-Date -Format 'yyyy-MM-dd HH:mm')
**Scanned By:** $env:USERNAME
**Total Items Scanned:** $($ScanResults.Count)

## Risk Summary

| Risk Level | Count | SLA |
|-----------|-------|-----|
| CRITICAL | $(($ScanResults | Where-Object { $_.RiskLevel -eq 'CRITICAL' }).Count) | 4 hours |
| HIGH | $(($ScanResults | Where-Object { $_.RiskLevel -eq 'HIGH' }).Count) | 24 hours |
| MEDIUM | $(($ScanResults | Where-Object { $_.RiskLevel -eq 'MEDIUM' }).Count) | 5 business days |
| LOW | $(($ScanResults | Where-Object { $_.RiskLevel -eq 'LOW' }).Count) | Next scheduled review |

## Pre-Deployment Gate Status

$(if (($ScanResults | Where-Object { $_.RiskLevel -eq 'CRITICAL' }).Count -gt 0) {
    "**STATUS: BLOCKED** — CRITICAL items detected. Agent deployment must not proceed."
} else {
    "**STATUS: CLEARED** — No CRITICAL items detected. Agent may proceed to deployment."
})
"@

$Report | Out-File -FilePath $ReportPath -Encoding UTF8
Write-Host "`nCompliance report exported to: $ReportPath" -ForegroundColor Cyan
```

---

## Step 5: Schedule Recurring Scans

### 5.1 — Windows Task Scheduler (Zone 1/2)

```powershell
# Create a scheduled task for monthly scanning
$Action = New-ScheduledTaskAction `
    -Execute "PowerShell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"C:\Scripts\Get-KnowledgeSourceItemPermissions.ps1`" -AdminUrl `"https://<tenant>-admin.sharepoint.com`" -ConfigPath `"C:\Scripts\config\item-scope-config.json`" -OutputPath `"C:\Output\item-scans`""

$Trigger = New-ScheduledTaskTrigger -Monthly -DaysOfMonth 1 -At "02:00AM"

$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable

Register-ScheduledTask `
    -TaskName "AgentKnowledgeSourceScan-Monthly" `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Description "Monthly item-level permission scan of agent knowledge source libraries (Control 4.8)" `
    -RunLevel Highest
```

### 5.2 — Azure Automation (Zone 3 — Recommended)

For Zone 3 regulated environments, configure Azure Automation:

1. Import `Get-KnowledgeSourceItemPermissions.ps1` as an Azure Automation runbook
2. Configure a managed identity with required SharePoint permissions
3. Create a monthly schedule trigger
4. Configure output to Azure Storage with 7-year retention policy
5. Set up Azure Monitor alerts for CRITICAL findings

---

## Step 6: Integrate with Compliance Dashboard

```powershell
# Feed scan output into compliance-dashboard
# (Requires compliance-dashboard solution from FSI-AgentGov-Solutions)

$ScanResults = Import-Csv -Path "./output/item-permissions-scan-*.csv"

# Format for dashboard ingestion
$DashboardPayload = $ScanResults | Select-Object @{
    Name = "ControlId"; Expression = { "4.8" }
}, @{
    Name = "ControlName"; Expression = { "Item-Level Permission Scanning" }
}, @{
    Name = "ScanDate"; Expression = { $_.ScannedDate }
}, RiskLevel, FileName, SiteUrl, SharingScopes, SensitivityLabel

$DashboardPayload | Export-Csv -Path "./output/dashboard-feed-4.8.csv" -NoTypeInformation

Write-Host "Dashboard feed exported. Import into compliance-dashboard for unified view." -ForegroundColor Cyan
```

---

## Validation

After completing PowerShell setup, verify:

- [ ] All required modules installed and authenticated
- [ ] `item-scope-config.json` configured with organization's sensitivity labels
- [ ] Scan executes successfully against at least one knowledge source library
- [ ] CSV output contains expected columns (RiskLevel, FileName, SharingScopes, etc.)
- [ ] CRITICAL/HIGH items correctly classified
- [ ] Recurring scan schedule is configured and tested
- [ ] Output retention meets 7-year requirement

---

*Updated: March 2026 | Version: v1.2*
