# PowerShell Setup: Control 1.27 - AI Agent Content Moderation Enforcement

**Last Updated:** February 2026
**PowerShell Module:** Microsoft.PowerApps.Administration.PowerShell

## Prerequisites

- [ ] Power Platform Admin or Entra Global Admin role
- [ ] PowerShell 7.0 or later
- [ ] Microsoft.PowerApps.Administration.PowerShell module v2.0.184+

---

## Module Installation

### Install Required PowerShell Modules

```powershell
# Install or update the Power Platform Administration module
Install-Module -Name Microsoft.PowerApps.Administration.PowerShell -Force -AllowClobber

# Verify module version
Get-Module -Name Microsoft.PowerApps.Administration.PowerShell -ListAvailable |
    Format-Table Name, Version, Path

# Authenticate to Power Platform
Add-PowerAppsAccount
```

---

## Script 1: Get Agent Moderation Configuration Inventory

```powershell
<#
.SYNOPSIS
    Retrieves content moderation configuration for all agents across environments.

.DESCRIPTION
    Exports a CSV report of agent-level and topic-level content moderation settings,
    including governance zone classification and approval status.

.NOTES
    Requires Power Platform Admin role.
    Content moderation settings are stored in agent metadata as of Copilot Studio v8+.
#>

# Get all environments
$environments = Get-AdminPowerAppEnvironment

$moderationInventory = @()

foreach ($env in $environments) {
    $envName = $env.EnvironmentName
    $envDisplay = $env.DisplayName
    
    Write-Host "Processing environment: $envDisplay" -ForegroundColor Cyan
    
    # Get all agents in the environment
    $agents = Get-AdminPowerAppChatbot -EnvironmentName $envName -ErrorAction SilentlyContinue
    
    foreach ($agent in $agents) {
        $agentName = $agent.Properties.DisplayName
        $agentId = $agent.ChatbotName
        
        # Extract moderation level from agent properties
        # Note: This assumes moderation metadata is exposed via API (as of Feb 2026)
        $moderationLevel = if ($agent.Properties.ContentModeration) {
            $agent.Properties.ContentModeration.DefaultLevel
        } else {
            "Not Configured"
        }
        
        $customSafetyMessage = if ($agent.Properties.ContentModeration) {
            $agent.Properties.ContentModeration.SafetyMessage -ne $null
        } else {
            $false
        }
        
        $moderationInventory += [PSCustomObject]@{
            Environment          = $envDisplay
            AgentName            = $agentName
            AgentId              = $agentId
            ModerationLevel      = $moderationLevel
            CustomSafetyMessage  = $customSafetyMessage
            LastModified         = $agent.Properties.LastModifiedTime
            GovernanceZone       = "Not Specified"  # Manual classification required
            ApprovalStatus       = "Pending Review" # Manual review required
        }
    }
}

# Export to CSV
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$outputPath = ".\AgentModerationInventory_$timestamp.csv"
$moderationInventory | Export-Csv -Path $outputPath -NoTypeInformation

Write-Host "`nModeration inventory exported to: $outputPath" -ForegroundColor Green
Write-Host "Total agents assessed: $($moderationInventory.Count)" -ForegroundColor Yellow
```

---

## Script 2: Audit Moderation Configuration Changes

```powershell
<#
.SYNOPSIS
    Queries audit logs for content moderation configuration changes.

.DESCRIPTION
    Retrieves agent moderation changes from the Power Platform audit log,
    including who made changes and when.

.NOTES
    Requires audit logging enabled in the environment.
    May require Microsoft Purview compliance role for full audit access.
#>

param(
    [Parameter(Mandatory = $false)]
    [int]$DaysBack = 30
)

$startDate = (Get-Date).AddDays(-$DaysBack)

Write-Host "Querying moderation changes from $startDate to present..." -ForegroundColor Cyan

$environments = Get-AdminPowerAppEnvironment

$moderationChanges = @()

foreach ($env in $environments) {
    $envName = $env.EnvironmentName
    $envDisplay = $env.DisplayName
    
    # Query audit logs for chatbot configuration changes
    # Note: This assumes moderation changes are captured in UpdateChatbot events
    $auditEvents = Get-AdminPowerAppChatbotAuditLog -EnvironmentName $envName `
        -StartTime $startDate -ErrorAction SilentlyContinue
    
    foreach ($event in $auditEvents) {
        if ($event.Operation -like "*UpdateChatbot*" -or $event.Operation -like "*ModifyModeration*") {
            $moderationChanges += [PSCustomObject]@{
                Timestamp    = $event.CreationTime
                Environment  = $envDisplay
                AgentName    = $event.ChatbotName
                ModifiedBy   = $event.UserId
                ChangeType   = $event.Operation
                Details      = $event.AdditionalInfo
            }
        }
    }
}

# Export to CSV
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$outputPath = ".\ModerationAuditLog_$timestamp.csv"
$moderationChanges | Export-Csv -Path $outputPath -NoTypeInformation

Write-Host "`nModeration audit log exported to: $outputPath" -ForegroundColor Green
Write-Host "Total configuration changes found: $($moderationChanges.Count)" -ForegroundColor Yellow
```

---

## Script 3: Validate Zone Compliance

```powershell
<#
.SYNOPSIS
    Validates agent moderation configurations against zone requirements.

.DESCRIPTION
    Checks each agent's moderation level against the expected configuration
    for its governance zone classification.

.NOTES
    Requires a governance zone mapping CSV file (AgentZoneMapping.csv).
    Format: AgentName, GovernanceZone, RequiredModeration
#>

param(
    [Parameter(Mandatory = $true)]
    [string]$ZoneMappingFile
)

# Import zone mapping
if (-not (Test-Path $ZoneMappingFile)) {
    Write-Error "Zone mapping file not found: $ZoneMappingFile"
    exit 1
}

$zoneMapping = Import-Csv -Path $ZoneMappingFile

# Get current agent moderation inventory
$environments = Get-AdminPowerAppEnvironment
$complianceResults = @()

foreach ($env in $environments) {
    $envName = $env.EnvironmentName
    $agents = Get-AdminPowerAppChatbot -EnvironmentName $envName -ErrorAction SilentlyContinue
    
    foreach ($agent in $agents) {
        $agentName = $agent.Properties.DisplayName
        
        # Lookup zone classification
        $zoneInfo = $zoneMapping | Where-Object { $_.AgentName -eq $agentName }
        
        if ($zoneInfo) {
            # Extract current moderation level
            $currentModeration = if ($agent.Properties.ContentModeration) {
                $agent.Properties.ContentModeration.DefaultLevel
            } else {
                "Not Configured"
            }
            
            # Compare to required level
            $isCompliant = $currentModeration -eq $zoneInfo.RequiredModeration
            
            $complianceResults += [PSCustomObject]@{
                Environment        = $env.DisplayName
                AgentName          = $agentName
                GovernanceZone     = $zoneInfo.GovernanceZone
                RequiredModeration = $zoneInfo.RequiredModeration
                ActualModeration   = $currentModeration
                Compliant          = $isCompliant
            }
        } else {
            # Agent not in zone mapping
            $complianceResults += [PSCustomObject]@{
                Environment        = $env.DisplayName
                AgentName          = $agentName
                GovernanceZone     = "UNKNOWN"
                RequiredModeration = "N/A"
                ActualModeration   = "Not Classified"
                Compliant          = $false
            }
        }
    }
}

# Export compliance report
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$outputPath = ".\ModerationComplianceReport_$timestamp.csv"
$complianceResults | Export-Csv -Path $outputPath -NoTypeInformation

# Summary
$totalAgents = $complianceResults.Count
$compliantAgents = ($complianceResults | Where-Object { $_.Compliant -eq $true }).Count
$nonCompliantAgents = $totalAgents - $compliantAgents

Write-Host "`nCompliance Report Summary" -ForegroundColor Cyan
Write-Host "Total Agents: $totalAgents" -ForegroundColor Yellow
Write-Host "Compliant: $compliantAgents" -ForegroundColor Green
Write-Host "Non-Compliant: $nonCompliantAgents" -ForegroundColor Red

Write-Host "`nFull compliance report exported to: $outputPath" -ForegroundColor Green
```

---

## Script 4: Export Topic-Level Moderation Overrides

```powershell
<#
.SYNOPSIS
    Exports topic-level moderation overrides for all agents.

.DESCRIPTION
    Retrieves topic-level moderation settings that override agent-level defaults,
    identifying topics that may require approval or review.

.NOTES
    Requires agent metadata API access for topic-level settings.
#>

$environments = Get-AdminPowerAppEnvironment

$topicOverrides = @()

foreach ($env in $environments) {
    $envName = $env.EnvironmentName
    $envDisplay = $env.DisplayName
    
    Write-Host "Processing environment: $envDisplay" -ForegroundColor Cyan
    
    $agents = Get-AdminPowerAppChatbot -EnvironmentName $envName -ErrorAction SilentlyContinue
    
    foreach ($agent in $agents) {
        $agentName = $agent.Properties.DisplayName
        $agentId = $agent.ChatbotName
        
        # Get agent-level default moderation
        $agentModeration = if ($agent.Properties.ContentModeration) {
            $agent.Properties.ContentModeration.DefaultLevel
        } else {
            "Not Configured"
        }
        
        # Query topics for this agent
        # Note: This assumes topic metadata is exposed via API (as of Feb 2026)
        $topics = Get-AdminPowerAppChatbotTopic -EnvironmentName $envName -ChatbotName $agentId -ErrorAction SilentlyContinue
        
        foreach ($topic in $topics) {
            $topicName = $topic.Properties.DisplayName
            
            # Extract topic-level moderation if it differs from agent default
            $topicModeration = if ($topic.Properties.ContentModeration) {
                $topic.Properties.ContentModeration.Level
            } else {
                $null
            }
            
            # Only report if topic override exists and differs from agent default
            if ($topicModeration -and $topicModeration -ne $agentModeration) {
                $topicOverrides += [PSCustomObject]@{
                    Environment       = $envDisplay
                    AgentName         = $agentName
                    TopicName         = $topicName
                    AgentModeration   = $agentModeration
                    TopicModeration   = $topicModeration
                    OverrideDirection = if ($topicModeration -eq "High") { "Stricter" } 
                                        elseif ($topicModeration -eq "Low") { "Permissive" } 
                                        else { "Moderate" }
                    RequiresApproval  = ($topicModeration -eq "Low") # Zone 3 restriction
                }
            }
        }
    }
}

# Export to CSV
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$outputPath = ".\TopicModerationOverrides_$timestamp.csv"
$topicOverrides | Export-Csv -Path $outputPath -NoTypeInformation

Write-Host "`nTopic moderation overrides exported to: $outputPath" -ForegroundColor Green
Write-Host "Total topic overrides found: $($topicOverrides.Count)" -ForegroundColor Yellow

# Highlight overrides requiring approval
$lowOverrides = $topicOverrides | Where-Object { $_.TopicModeration -eq "Low" }
if ($lowOverrides.Count -gt 0) {
    Write-Host "`nWARNING: $($lowOverrides.Count) topic(s) with Low moderation override detected" -ForegroundColor Red
    Write-Host "These require approval in Zone 2+ and are prohibited in Zone 3." -ForegroundColor Red
}
```

---

## Sample Zone Mapping File

Create `AgentZoneMapping.csv` for use with Script 3:

```csv
AgentName,GovernanceZone,RequiredModeration
Customer Support Agent,Zone 3,High
HR Benefits Assistant,Zone 2,High
Personal Task Manager,Zone 1,Medium
Sales Knowledge Bot,Zone 3,High
IT Helpdesk Agent,Zone 2,High
```

---

## Automation Notes

- **Scheduled Execution:** Run Script 1 (inventory) weekly for Zone 3, monthly for Zone 2, quarterly for Zone 1
- **Audit Monitoring:** Run Script 2 (audit log) daily in Zone 3 environments to detect unauthorized moderation changes
- **Compliance Validation:** Run Script 3 (zone compliance) before quarterly governance reviews
- **Topic Override Review:** Run Script 4 (topic overrides) before deploying agents with custom topics

---

## Known Limitations

| Limitation | Impact | Workaround |
|------------|--------|------------|
| Moderation metadata may not be fully exposed via PowerShell API (as of Feb 2026) | Scripts may require manual verification | Use portal walkthrough for manual inventory |
| Topic-level moderation overrides are agent-specific | No bulk topic configuration | Configure topics individually per agent |
| Audit log retention limited to 90 days (default) | Historical moderation changes may not be available | Export audit logs to external SIEM/logging system |
| No native API for bulk moderation configuration | Cannot set moderation levels via script | Use portal configuration; script for reporting only |

---

[Back to Control 1.27](../../../controls/pillar-1-security/1.27-ai-agent-content-moderation-enforcement.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
