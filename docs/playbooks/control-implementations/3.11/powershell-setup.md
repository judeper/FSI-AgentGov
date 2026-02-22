# PowerShell Setup: Control 3.11 - Centralized Agent Inventory Enforcement

**Last Updated:** February 2026
**PowerShell Version:** 7.0 or higher recommended
**Required Modules:**
- Microsoft.PowerApps.Administration.PowerShell
- Microsoft.Graph (for Entra ID user validation)
- ExchangeOnlineManagement (for email notifications)

---

## Prerequisites

Before running these scripts, ensure:

- [ ] PowerShell 7.0 or higher installed
- [ ] Required PowerShell modules installed (see Installation section below)
- [ ] Power Platform Admin role assigned to your account
- [ ] Microsoft Graph API permissions: `User.Read.All`, `Group.Read.All`
- [ ] Access to Power Platform Admin Center and Entra ID
- [ ] Change management system or ticketing system for automated ticket creation (optional)
- [ ] Teams webhook URL for notifications (optional but recommended)

---

## Module Installation

Run the following commands to install required PowerShell modules:

```powershell
# Install Power Apps Administration module
Install-Module -Name Microsoft.PowerApps.Administration.PowerShell -Scope CurrentUser -Force

# Install Microsoft Graph module for Entra ID queries
Install-Module -Name Microsoft.Graph -Scope CurrentUser -Force

# Install Exchange Online Management module for email notifications
Install-Module -Name ExchangeOnlineManagement -Scope CurrentUser -Force

# Verify installations
Get-Module -ListAvailable Microsoft.PowerApps.Administration.PowerShell
Get-Module -ListAvailable Microsoft.Graph
Get-Module -ListAvailable ExchangeOnlineManagement
```

---

## Script 1: Get-AgentInventoryReport.ps1

Exports comprehensive agent inventory from Power Platform with metadata completeness analysis.

```powershell
<#
.SYNOPSIS
    Exports complete agent inventory from Power Platform environments with metadata completeness analysis.

.DESCRIPTION
    This script queries all Power Platform environments, retrieves Copilot Studio agents, and generates
    a comprehensive inventory report with completeness metrics. Supports zone-based analysis and
    identifies agents with missing or incomplete metadata.

.PARAMETER OutputPath
    Directory where inventory report CSV will be saved. Default: Current directory.

.PARAMETER ZoneMappingFile
    Path to CSV file containing environment-to-zone mappings (columns: EnvironmentId, ZoneName).
    Optional. If not provided, zone classification will be marked as "Unknown".

.PARAMETER IncludeDecommissioned
    Switch to include decommissioned agents in the report. Default: False (exclude decommissioned).

.EXAMPLE
    .\Get-AgentInventoryReport.ps1 -OutputPath "C:\Reports" -ZoneMappingFile "C:\Config\zone-mappings.csv"

.NOTES
    Author: FSI-AgentGov Framework
    Version: 1.0
    Last Updated: February 2026
#>

param(
    [Parameter(Mandatory=$false)]
    [string]$OutputPath = ".",
    
    [Parameter(Mandatory=$false)]
    [string]$ZoneMappingFile = "",
    
    [Parameter(Mandatory=$false)]
    [switch]$IncludeDecommissioned = $false
)

# Import required modules
Import-Module Microsoft.PowerApps.Administration.PowerShell
Import-Module Microsoft.Graph.Users

# Connect to Power Platform
Write-Host "Connecting to Power Platform..." -ForegroundColor Cyan
Add-PowerAppsAccount

# Connect to Microsoft Graph for user validation
Write-Host "Connecting to Microsoft Graph..." -ForegroundColor Cyan
Connect-MgGraph -Scopes "User.Read.All"

# Load zone mappings if provided
$zoneMappings = @{}
if ($ZoneMappingFile -and (Test-Path $ZoneMappingFile)) {
    Write-Host "Loading zone mappings from $ZoneMappingFile..." -ForegroundColor Cyan
    $zoneMappings = Import-Csv $ZoneMappingFile | ForEach-Object { @{$_.EnvironmentId = $_.ZoneName} }
} else {
    Write-Host "No zone mapping file provided. Zone classification will be marked as 'Unknown'." -ForegroundColor Yellow
}

# Get all environments
Write-Host "Retrieving all Power Platform environments..." -ForegroundColor Cyan
$environments = Get-AdminPowerAppEnvironment

$agentInventory = @()
$envCount = 0

foreach ($env in $environments) {
    $envCount++
    Write-Host "[$envCount/$($environments.Count)] Processing environment: $($env.DisplayName)" -ForegroundColor Green
    
    # Get Copilot Studio agents (bots) in this environment
    try {
        # NOTE: Get-AdminPowerAppCopilotStudioAgent is unverified and may not be available
        # in all environments. As a fallback, use the Power Platform Admin Center inventory
        # or the Dataverse API: GET /api/data/v9.2/bots?$select=name,botid,statecode
        $agents = Get-AdminPowerAppCopilotStudioAgent -EnvironmentName $env.EnvironmentName -ErrorAction SilentlyContinue
        
        foreach ($agent in $agents) {
            # Skip decommissioned agents unless explicitly included
            if (-not $IncludeDecommissioned -and $agent.Internal.properties.statecode -eq 1) {
                continue
            }
            
            # Extract metadata
            $owner = $agent.Owner.email
            $createdTime = $agent.CreatedTime
            $lastModifiedTime = $agent.LastModifiedTime
            $displayName = $agent.DisplayName
            
            # Validate owner (check if user still exists in Entra ID)
            $ownerStatus = "Unknown"
            $ownerValid = $false
            if ($owner) {
                try {
                    $user = Get-MgUser -UserId $owner -ErrorAction SilentlyContinue
                    if ($user) {
                        $ownerValid = $true
                        $ownerStatus = "Active"
                    } else {
                        $ownerStatus = "Departed"
                    }
                } catch {
                    $ownerStatus = "Invalid"
                }
            } else {
                $ownerStatus = "Missing"
            }
            
            # Determine zone classification
            $zone = if ($zoneMappings.ContainsKey($env.EnvironmentName)) {
                $zoneMappings[$env.EnvironmentName]
            } else {
                "Unknown"
            }
            
            # Calculate metadata completeness
            $metadataScore = 0
            $maxScore = 7
            if ($owner) { $metadataScore++ }
            if ($displayName) { $metadataScore++ }
            if ($env.DisplayName) { $metadataScore++ }
            if ($createdTime) { $metadataScore++ }
            if ($lastModifiedTime) { $metadataScore++ }
            if ($zone -ne "Unknown") { $metadataScore++ }
            if ($ownerValid) { $metadataScore++ }
            
            $completenessPercent = [math]::Round(($metadataScore / $maxScore) * 100, 2)
            
            # Identify missing fields
            $missingFields = @()
            if (-not $owner) { $missingFields += "Owner" }
            if (-not $displayName) { $missingFields += "DisplayName" }
            if ($zone -eq "Unknown") { $missingFields += "ZoneClassification" }
            if (-not $ownerValid) { $missingFields += "ValidOwner" }
            $missingFieldsString = $missingFields -join "; "
            
            # Calculate staleness (days since last modification)
            $daysSinceModified = if ($lastModifiedTime) {
                [math]::Round((Get-Date).Subtract([datetime]$lastModifiedTime).TotalDays, 0)
            } else {
                "Unknown"
            }
            
            # Build inventory record
            $inventoryRecord = [PSCustomObject]@{
                AgentName = $displayName
                AgentId = $agent.AgentName
                Owner = $owner
                OwnerStatus = $ownerStatus
                Environment = $env.DisplayName
                EnvironmentId = $env.EnvironmentName
                ZoneClassification = $zone
                CreatedDate = $createdTime
                LastModifiedDate = $lastModifiedTime
                DaysSinceModified = $daysSinceModified
                State = if ($agent.Internal.properties.statecode -eq 1) { "Decommissioned" } else { "Active" }
                MetadataCompletenessPercent = $completenessPercent
                MissingFields = $missingFieldsString
            }
            
            $agentInventory += $inventoryRecord
        }
    } catch {
        Write-Host "  Error retrieving agents from environment $($env.DisplayName): $_" -ForegroundColor Red
    }
}

# Generate summary statistics
Write-Host "`n--- Agent Inventory Summary ---" -ForegroundColor Cyan
Write-Host "Total Agents: $($agentInventory.Count)" -ForegroundColor White
Write-Host "Active Agents: $(($agentInventory | Where-Object { $_.State -eq 'Active' }).Count)" -ForegroundColor White
Write-Host "Decommissioned Agents: $(($agentInventory | Where-Object { $_.State -eq 'Decommissioned' }).Count)" -ForegroundColor White
Write-Host "Agents with Valid Owner: $(($agentInventory | Where-Object { $_.OwnerStatus -eq 'Active' }).Count)" -ForegroundColor Green
Write-Host "Agents with Invalid/Missing Owner: $(($agentInventory | Where-Object { $_.OwnerStatus -ne 'Active' }).Count)" -ForegroundColor Red
Write-Host "Agents with Unknown Zone: $(($agentInventory | Where-Object { $_.ZoneClassification -eq 'Unknown' }).Count)" -ForegroundColor Yellow
Write-Host "Average Metadata Completeness: $([math]::Round(($agentInventory | Measure-Object -Property MetadataCompletenessPercent -Average).Average, 2))%" -ForegroundColor White

# Export to CSV
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$reportPath = Join-Path $OutputPath "AgentInventoryReport_$timestamp.csv"
$agentInventory | Export-Csv -Path $reportPath -NoTypeInformation -Encoding UTF8

Write-Host "`n✓ Inventory report saved to: $reportPath" -ForegroundColor Green

# Disconnect
Disconnect-MgGraph | Out-Null
Write-Host "`nScript completed successfully." -ForegroundColor Cyan
```

---

## Script 2: Detect-OrphanedAgents.ps1

Identifies agents with departed owners, stale agents, and unmanaged agents requiring remediation.

```powershell
<#
.SYNOPSIS
    Detects orphaned agents requiring ownership transfer or decommissioning.

.DESCRIPTION
    This script identifies agents with departed owners (no longer in Entra ID), stale agents
    (not modified in >12 months), and unmanaged agents (missing critical metadata). Generates
    a prioritized remediation report and optionally sends Teams notifications.

.PARAMETER InventoryReportPath
    Path to agent inventory CSV file generated by Get-AgentInventoryReport.ps1.
    If not provided, script will generate a fresh inventory.

.PARAMETER StalenessThresholdDays
    Number of days since last modification to consider an agent "stale". Default: 365 days.

.PARAMETER OutputPath
    Directory where orphaned agent report CSV will be saved. Default: Current directory.

.PARAMETER TeamsWebhookUrl
    Optional Teams webhook URL for sending notifications. If provided, script will post
    orphaned agent alert to Teams channel.

.EXAMPLE
    .\Detect-OrphanedAgents.ps1 -InventoryReportPath "C:\Reports\AgentInventory.csv" -StalenessThresholdDays 365 -TeamsWebhookUrl "https://outlook.office.com/webhook/..."

.NOTES
    Author: FSI-AgentGov Framework
    Version: 1.0
    Last Updated: February 2026
#>

param(
    [Parameter(Mandatory=$false)]
    [string]$InventoryReportPath = "",
    
    [Parameter(Mandatory=$false)]
    [int]$StalenessThresholdDays = 365,
    
    [Parameter(Mandatory=$false)]
    [string]$OutputPath = ".",
    
    [Parameter(Mandatory=$false)]
    [string]$TeamsWebhookUrl = ""
)

# Load inventory report
if ($InventoryReportPath -and (Test-Path $InventoryReportPath)) {
    Write-Host "Loading inventory report from $InventoryReportPath..." -ForegroundColor Cyan
    $inventory = Import-Csv $InventoryReportPath
} else {
    Write-Host "No inventory report provided. Generating fresh inventory..." -ForegroundColor Yellow
    # Call Get-AgentInventoryReport.ps1 to generate fresh inventory
    & "$PSScriptRoot\Get-AgentInventoryReport.ps1" -OutputPath $OutputPath
    # Find the most recent inventory report
    $latestReport = Get-ChildItem $OutputPath -Filter "AgentInventoryReport_*.csv" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($latestReport) {
        $inventory = Import-Csv $latestReport.FullName
    } else {
        Write-Host "ERROR: Could not generate or find inventory report." -ForegroundColor Red
        exit 1
    }
}

Write-Host "Analyzing $($inventory.Count) agents for orphaned status..." -ForegroundColor Cyan

# Identify orphaned agents
$orphanedAgents = @()

foreach ($agent in $inventory) {
    $orphanReason = @()
    $priority = "Low"
    
    # Check 1: Owner is departed or invalid
    if ($agent.OwnerStatus -in @("Departed", "Invalid", "Missing")) {
        $orphanReason += "Owner status: $($agent.OwnerStatus)"
        $priority = "High"
    }
    
    # Check 2: Agent is stale (not modified in >$StalenessThresholdDays days)
    if ($agent.DaysSinceModified -ne "Unknown" -and [int]$agent.DaysSinceModified -gt $StalenessThresholdDays) {
        $orphanReason += "Stale (not modified in $($agent.DaysSinceModified) days)"
        if ($priority -eq "Low") { $priority = "Medium" }
    }
    
    # Check 3: Missing critical metadata
    if ($agent.ZoneClassification -eq "Unknown") {
        $orphanReason += "Zone classification missing"
        if ($priority -eq "Low") { $priority = "Medium" }
    }
    
    # If any orphan conditions met, add to report
    if ($orphanReason.Count -gt 0) {
        $orphanedAgents += [PSCustomObject]@{
            AgentName = $agent.AgentName
            Owner = $agent.Owner
            OwnerStatus = $agent.OwnerStatus
            Environment = $agent.Environment
            ZoneClassification = $agent.ZoneClassification
            DaysSinceModified = $agent.DaysSinceModified
            OrphanReason = $orphanReason -join "; "
            Priority = $priority
            RecommendedAction = if ($agent.OwnerStatus -in @("Departed", "Invalid")) {
                "Transfer ownership or decommission"
            } elseif ([int]$agent.DaysSinceModified -gt $StalenessThresholdDays) {
                "Verify usage and decommission if unused"
            } else {
                "Complete metadata"
            }
        }
    }
}

# Sort by priority
$orphanedAgents = $orphanedAgents | Sort-Object @{Expression={
    switch ($_.Priority) {
        "High" { 1 }
        "Medium" { 2 }
        "Low" { 3 }
    }
}}

# Generate summary
Write-Host "`n--- Orphaned Agent Detection Summary ---" -ForegroundColor Cyan
Write-Host "Total Orphaned Agents: $($orphanedAgents.Count)" -ForegroundColor White
Write-Host "  High Priority: $(($orphanedAgents | Where-Object { $_.Priority -eq 'High' }).Count)" -ForegroundColor Red
Write-Host "  Medium Priority: $(($orphanedAgents | Where-Object { $_.Priority -eq 'Medium' }).Count)" -ForegroundColor Yellow
Write-Host "  Low Priority: $(($orphanedAgents | Where-Object { $_.Priority -eq 'Low' }).Count)" -ForegroundColor Green

# Export to CSV
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$reportPath = Join-Path $OutputPath "OrphanedAgentsReport_$timestamp.csv"
$orphanedAgents | Export-Csv -Path $reportPath -NoTypeInformation -Encoding UTF8

Write-Host "`n✓ Orphaned agents report saved to: $reportPath" -ForegroundColor Green

# Send Teams notification if webhook URL provided
if ($TeamsWebhookUrl -and $orphanedAgents.Count -gt 0) {
    Write-Host "`nSending Teams notification..." -ForegroundColor Cyan
    
    $highPriorityCount = ($orphanedAgents | Where-Object { $_.Priority -eq 'High' }).Count
    $mediumPriorityCount = ($orphanedAgents | Where-Object { $_.Priority -eq 'Medium' }).Count
    
    # Build adaptive card
    $adaptiveCard = @{
        type = "message"
        attachments = @(
            @{
                contentType = "application/vnd.microsoft.card.adaptive"
                content = @{
                    type = "AdaptiveCard"
                    body = @(
                        @{
                            type = "TextBlock"
                            size = "Large"
                            weight = "Bolder"
                            text = "⚠️ Orphaned Agent Detection Alert"
                        }
                        @{
                            type = "TextBlock"
                            text = "The following agents require remediation due to invalid ownership or inactivity:"
                            wrap = $true
                        }
                        @{
                            type = "FactSet"
                            facts = @(
                                @{
                                    title = "Total Orphaned Agents:"
                                    value = "$($orphanedAgents.Count)"
                                }
                                @{
                                    title = "High Priority:"
                                    value = "$highPriorityCount"
                                }
                                @{
                                    title = "Medium Priority:"
                                    value = "$mediumPriorityCount"
                                }
                            )
                        }
                        @{
                            type = "TextBlock"
                            text = "📊 View full report: $reportPath"
                            wrap = $true
                        }
                        @{
                            type = "TextBlock"
                            text = "Please review and remediate high-priority agents within 14 days (Zone 2/3)."
                            wrap = $true
                        }
                    )
                    "`$schema" = "http://adaptivecards.io/schemas/adaptive-card.json"
                    version = "1.2"
                }
            }
        )
    }
    
    try {
        $body = $adaptiveCard | ConvertTo-Json -Depth 20
        Invoke-RestMethod -Uri $TeamsWebhookUrl -Method Post -Body $body -ContentType 'application/json'
        Write-Host "✓ Teams notification sent successfully." -ForegroundColor Green
    } catch {
        Write-Host "✗ Failed to send Teams notification: $_" -ForegroundColor Red
    }
}

Write-Host "`nScript completed successfully." -ForegroundColor Cyan
```

---

## Script 3: Test-InventoryCompleteness.ps1

Validates agent inventory against mandatory metadata requirements and generates compliance report.

```powershell
<#
.SYNOPSIS
    Validates agent inventory completeness against mandatory metadata requirements.

.DESCRIPTION
    This script validates that all agents meet mandatory metadata requirements defined by governance
    policies. Generates a compliance report showing completeness rates by zone and identifies
    agents requiring metadata updates.

.PARAMETER InventoryReportPath
    Path to agent inventory CSV file generated by Get-AgentInventoryReport.ps1.

.PARAMETER OutputPath
    Directory where compliance report CSV will be saved. Default: Current directory.

.PARAMETER MandatoryFieldsConfig
    Path to JSON file defining mandatory fields by zone. If not provided, uses default requirements.

.EXAMPLE
    .\Test-InventoryCompleteness.ps1 -InventoryReportPath "C:\Reports\AgentInventory.csv" -OutputPath "C:\Reports"

.NOTES
    Author: FSI-AgentGov Framework
    Version: 1.0
    Last Updated: February 2026
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$InventoryReportPath,
    
    [Parameter(Mandatory=$false)]
    [string]$OutputPath = ".",
    
    [Parameter(Mandatory=$false)]
    [string]$MandatoryFieldsConfig = ""
)

# Default mandatory fields by zone (if config file not provided)
$defaultMandatoryFields = @{
    "Zone 1" = @("AgentName", "Owner", "Environment", "ZoneClassification")
    "Zone 2" = @("AgentName", "Owner", "Environment", "ZoneClassification", "OwnerStatus")
    "Zone 3" = @("AgentName", "Owner", "Environment", "ZoneClassification", "OwnerStatus")
    "Unknown" = @("AgentName", "Owner", "Environment")
}

# Load mandatory fields config
$mandatoryFields = $defaultMandatoryFields
if ($MandatoryFieldsConfig -and (Test-Path $MandatoryFieldsConfig)) {
    Write-Host "Loading mandatory fields config from $MandatoryFieldsConfig..." -ForegroundColor Cyan
    $mandatoryFields = Get-Content $MandatoryFieldsConfig | ConvertFrom-Json -AsHashtable
}

# Load inventory report
Write-Host "Loading inventory report from $InventoryReportPath..." -ForegroundColor Cyan
$inventory = Import-Csv $InventoryReportPath

Write-Host "Validating $($inventory.Count) agents against mandatory metadata requirements..." -ForegroundColor Cyan

# Validate completeness
$complianceReport = @()

foreach ($agent in $inventory) {
    $zone = $agent.ZoneClassification
    $requiredFields = $mandatoryFields[$zone]
    
    if (-not $requiredFields) {
        Write-Host "Warning: No mandatory fields defined for zone '$zone'. Skipping agent $($agent.AgentName)." -ForegroundColor Yellow
        continue
    }
    
    $missingFields = @()
    $fieldsComplete = $true
    
    foreach ($field in $requiredFields) {
        $value = $agent.$field
        if (-not $value -or $value -eq "Unknown" -or $value -eq "Missing") {
            $missingFields += $field
            $fieldsComplete = $false
        }
    }
    
    $complianceStatus = if ($fieldsComplete) { "Compliant" } else { "Non-Compliant" }
    
    $complianceReport += [PSCustomObject]@{
        AgentName = $agent.AgentName
        Environment = $agent.Environment
        ZoneClassification = $zone
        ComplianceStatus = $complianceStatus
        MissingFields = if ($missingFields.Count -gt 0) { $missingFields -join "; " } else { "None" }
        MetadataCompletenessPercent = $agent.MetadataCompletenessPercent
    }
}

# Calculate summary metrics
$totalAgents = $complianceReport.Count
$compliantAgents = ($complianceReport | Where-Object { $_.ComplianceStatus -eq 'Compliant' }).Count
$nonCompliantAgents = $totalAgents - $compliantAgents
$complianceRate = if ($totalAgents -gt 0) { [math]::Round(($compliantAgents / $totalAgents) * 100, 2) } else { 0 }

Write-Host "`n--- Inventory Completeness Summary ---" -ForegroundColor Cyan
Write-Host "Total Agents: $totalAgents" -ForegroundColor White
Write-Host "Compliant: $compliantAgents" -ForegroundColor Green
Write-Host "Non-Compliant: $nonCompliantAgents" -ForegroundColor Red
Write-Host "Compliance Rate: $complianceRate%" -ForegroundColor White

# Zone-specific compliance
Write-Host "`n--- Compliance by Zone ---" -ForegroundColor Cyan
foreach ($zone in ($complianceReport | Select-Object -ExpandProperty ZoneClassification -Unique)) {
    $zoneAgents = $complianceReport | Where-Object { $_.ZoneClassification -eq $zone }
    $zoneCompliant = ($zoneAgents | Where-Object { $_.ComplianceStatus -eq 'Compliant' }).Count
    $zoneRate = if ($zoneAgents.Count -gt 0) { [math]::Round(($zoneCompliant / $zoneAgents.Count) * 100, 2) } else { 0 }
    Write-Host "$zone`: $zoneCompliant / $($zoneAgents.Count) ($zoneRate%)" -ForegroundColor White
}

# Export to CSV
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$reportPath = Join-Path $OutputPath "InventoryComplianceReport_$timestamp.csv"
$complianceReport | Export-Csv -Path $reportPath -NoTypeInformation -Encoding UTF8

Write-Host "`n✓ Compliance report saved to: $reportPath" -ForegroundColor Green

# Alert if compliance rate is below target
$targetComplianceRate = 95
if ($complianceRate -lt $targetComplianceRate) {
    Write-Host "`n⚠ WARNING: Compliance rate ($complianceRate%) is below target ($targetComplianceRate%)!" -ForegroundColor Red
    Write-Host "Review non-compliant agents and initiate remediation." -ForegroundColor Yellow
}

Write-Host "`nScript completed successfully." -ForegroundColor Cyan
```

---

## Script 4: Invoke-InventoryEnforcementSuite.ps1

Master orchestration script that runs all inventory enforcement scripts in sequence.

```powershell
<#
.SYNOPSIS
    Master script to run complete agent inventory enforcement suite.

.DESCRIPTION
    This orchestration script executes all inventory enforcement scripts in sequence:
    1. Generate fresh agent inventory report
    2. Detect orphaned agents
    3. Validate inventory completeness
    4. Send consolidated Teams notification with all findings

.PARAMETER OutputPath
    Directory where all reports will be saved. Default: .\Reports

.PARAMETER ZoneMappingFile
    Path to CSV file containing environment-to-zone mappings.

.PARAMETER TeamsWebhookUrl
    Teams webhook URL for notifications.

.PARAMETER StalenessThresholdDays
    Number of days since last modification to consider an agent "stale". Default: 365.

.EXAMPLE
    .\Invoke-InventoryEnforcementSuite.ps1 -OutputPath "C:\Reports" -ZoneMappingFile "C:\Config\zone-mappings.csv" -TeamsWebhookUrl "https://outlook.office.com/webhook/..."

.NOTES
    Author: FSI-AgentGov Framework
    Version: 1.0
    Last Updated: February 2026
#>

param(
    [Parameter(Mandatory=$false)]
    [string]$OutputPath = ".\Reports",
    
    [Parameter(Mandatory=$false)]
    [string]$ZoneMappingFile = "",
    
    [Parameter(Mandatory=$false)]
    [string]$TeamsWebhookUrl = "",
    
    [Parameter(Mandatory=$false)]
    [int]$StalenessThresholdDays = 365
)

# Ensure output directory exists
if (-not (Test-Path $OutputPath)) {
    New-Item -Path $OutputPath -ItemType Directory -Force | Out-Null
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Agent Inventory Enforcement Suite" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Step 1: Generate agent inventory report
Write-Host "[1/3] Generating agent inventory report..." -ForegroundColor Green
$inventoryParams = @{
    OutputPath = $OutputPath
}
if ($ZoneMappingFile) {
    $inventoryParams.Add("ZoneMappingFile", $ZoneMappingFile)
}

& "$PSScriptRoot\Get-AgentInventoryReport.ps1" @inventoryParams

# Find the most recent inventory report
$latestInventory = Get-ChildItem $OutputPath -Filter "AgentInventoryReport_*.csv" | Sort-Object LastWriteTime -Descending | Select-Object -First 1

if (-not $latestInventory) {
    Write-Host "ERROR: Inventory report not generated. Aborting." -ForegroundColor Red
    exit 1
}

Write-Host "`n✓ Inventory report generated: $($latestInventory.FullName)`n" -ForegroundColor Green

# Step 2: Detect orphaned agents
Write-Host "[2/3] Detecting orphaned agents..." -ForegroundColor Green
$orphanedParams = @{
    InventoryReportPath = $latestInventory.FullName
    StalenessThresholdDays = $StalenessThresholdDays
    OutputPath = $OutputPath
}
if ($TeamsWebhookUrl) {
    $orphanedParams.Add("TeamsWebhookUrl", $TeamsWebhookUrl)
}

& "$PSScriptRoot\Detect-OrphanedAgents.ps1" @orphanedParams

Write-Host "`n✓ Orphaned agent detection completed`n" -ForegroundColor Green

# Step 3: Validate inventory completeness
Write-Host "[3/3] Validating inventory completeness..." -ForegroundColor Green
& "$PSScriptRoot\Test-InventoryCompleteness.ps1" -InventoryReportPath $latestInventory.FullName -OutputPath $OutputPath

Write-Host "`n✓ Completeness validation completed`n" -ForegroundColor Green

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Enforcement Suite Completed" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "All reports saved to: $OutputPath" -ForegroundColor White
Write-Host "`nNext Steps:" -ForegroundColor Yellow
Write-Host "1. Review orphaned agent report and initiate remediation" -ForegroundColor White
Write-Host "2. Review completeness report and contact agent authors for metadata updates" -ForegroundColor White
Write-Host "3. Update zone mappings if any agents have 'Unknown' classification" -ForegroundColor White
Write-Host "4. Schedule this suite to run daily for Zone 2/3 environments" -ForegroundColor White
```

---

## Scheduled Execution with Windows Task Scheduler

To run the enforcement suite on a schedule:

```powershell
# Create scheduled task (run as administrator)
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-File C:\Scripts\Invoke-InventoryEnforcementSuite.ps1 -OutputPath C:\Reports -ZoneMappingFile C:\Config\zone-mappings.csv -TeamsWebhookUrl 'https://outlook.office.com/webhook/...'"

# Run daily at 4:00 AM
$trigger = New-ScheduledTaskTrigger -Daily -At 4:00AM

# Run with highest privileges
$principal = New-ScheduledTaskPrincipal -UserId "DOMAIN\ServiceAccount" -LogonType Password -RunLevel Highest

# Register the task
Register-ScheduledTask -TaskName "Agent Inventory Enforcement Suite" -Action $action -Trigger $trigger -Principal $principal -Description "Daily agent inventory enforcement and orphaned agent detection"
```

---

## Zone Mapping CSV Template

Create a CSV file with environment-to-zone mappings:

```csv
EnvironmentId,ZoneName
00000000-0000-0000-0000-000000000001,Zone 1
00000000-0000-0000-0000-000000000002,Zone 2
00000000-0000-0000-0000-000000000003,Zone 3
```

Get environment IDs by running:
```powershell
Get-AdminPowerAppEnvironment | Select-Object EnvironmentName, DisplayName
```

---

## Additional Resources

- [Microsoft.PowerApps.Administration.PowerShell Documentation](https://learn.microsoft.com/en-us/powershell/module/microsoft.powerapps.administration.powershell/)
- [Microsoft Graph PowerShell SDK](https://learn.microsoft.com/en-us/powershell/microsoftgraph/)
- [Teams Incoming Webhooks](https://learn.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/add-incoming-webhook)

---

[Back to Control 3.11](../../../controls/pillar-3-reporting/3.11-centralized-agent-inventory-enforcement.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: February 2026 | Version: v1.0*
