# PowerShell Setup: Control 1.27 - AI Agent Content Moderation Enforcement

**Last Updated:** February 2026
**PowerShell Module:** Microsoft.PowerApps.Administration.PowerShell

## Prerequisites

- [ ] Power Platform Admin or Entra Global Admin role
- [ ] PowerShell 7.0 or later (Windows PowerShell 5.1 may work but 7+ is recommended; install via `winget install Microsoft.PowerShell`)
- [ ] Microsoft.PowerApps.Administration.PowerShell module (latest version recommended)
- [ ] ExchangeOnlineManagement module (required for Script 2 — audit log queries)

---

## Module Installation

### Install Required PowerShell Modules

```powershell
# Install or update the Power Platform Administration module
Install-Module -Name Microsoft.PowerApps.Administration.PowerShell -Force -AllowClobber

# Install Exchange Online Management module (required for Script 2 -- audit log queries)
Install-Module -Name ExchangeOnlineManagement -Force

# Verify module versions
Get-Module -Name Microsoft.PowerApps.Administration.PowerShell -ListAvailable |
    Format-Table Name, Version, Path

# Authenticate to Power Platform
Add-PowerAppsAccount

# Authenticate to Exchange Online (required for Script 2)
# Replace admin@yourdomain.com with your actual admin UPN (e.g., jsmith@contoso.com)
Connect-ExchangeOnline -UserPrincipalName admin@yourdomain.com
```

---

!!! danger "API Availability — Verify Before Use"
    The cmdlet `Get-AdminPowerAppChatbot` and property paths used in these scripts (e.g., `Properties.ContentModeration.DefaultLevel`) are based on **anticipated API schema** as of February 2026. These scripts are reporting templates — they may not return data in your tenant. Before running any script, test cmdlet availability:

    ```powershell
    Get-AdminPowerAppChatbot -EnvironmentName "your-env" | Select-Object -First 1 | ConvertTo-Json -Depth 5
    ```

    If the cmdlet is not available or returns no `ContentModeration` properties, use the [Portal Walkthrough](portal-walkthrough.md) for manual configuration and inventory.

## Script 1: Get-AgentModerationInventory.ps1

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

> **⚠️ Anticipated Operation Names:** The filter patterns `*UpdateChatbot*` and `*ModifyModeration*` used in this script are anticipated operation names. Validate these against your tenant's actual Unified Audit Log schema before relying on this script in production. Run `Search-UnifiedAuditLog -RecordType "PowerPlatformAdminActivity"` without a `-FreeText` filter first to discover available operation names.

```powershell
<#
.SYNOPSIS
    Queries audit logs for content moderation configuration changes.

.DESCRIPTION
    Retrieves agent moderation changes from the Power Platform audit log,
    including who made changes and when.

.NOTES
    Requires audit logging enabled in the environment.
    May require Purview Compliance Admin role for full audit access.
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
    
    # Query Unified Audit Log for Power Platform administrative changes
    # Uses PowerPlatformAdminActivity record type for admin configuration events
    $auditEvents = Search-UnifiedAuditLog -RecordType "PowerPlatformAdminActivity" `
        -StartDate $startDate -EndDate (Get-Date) -ResultSize 5000 `
        -FreeText $envName -ErrorAction SilentlyContinue
    
    foreach ($event in $auditEvents) {
        # NOTE: Operation names "UpdateChatbot" and "ModifyModeration" are anticipated
        # values. Run a broad Search-UnifiedAuditLog query without operation filters
        # first to discover actual operation names in your tenant.
        if ($event.Operations -like "*UpdateChatbot*" -or $event.Operations -like "*ModifyModeration*") {
            $moderationChanges += [PSCustomObject]@{
                Timestamp    = $event.CreationDate
                Environment  = $envDisplay
                AgentName    = ($event.AuditData | ConvertFrom-Json).ChatbotName
                ModifiedBy   = $event.UserIds
                ChangeType   = $event.Operations
                Details      = $event.AuditData
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
            
            # Compare to required level (case-insensitive)
            $isCompliant = $currentModeration -ieq $zoneInfo.RequiredModeration
            
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
    This script is a reporting template. No native PowerShell cmdlet exists for
    topic-level moderation queries. The $topics variable must be populated via
    Dataverse API or manual CSV import before the script produces results.
    See the "Populating Topic Data" section below for instructions.
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
        # NOTE: No native cmdlet exists for topic-level audit. Use the Copilot Studio
        # web interface or Dataverse API to query bot component metadata.
        # Example Dataverse API: GET /api/data/v9.2/botcomponents?$filter=_parentbotid_value eq '{botId}'
        $topics = @()  # Populate via Dataverse API or manual export; no PowerShell cmdlet available
        
        if ($topics.Count -eq 0) {
            Write-Warning "No topics loaded for agent '$agentName'. Populate `$topics via Dataverse API or manual CSV import. See comment above."
            continue
        }
        
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

### Populating Topic Data for Script 4

Script 4 requires topic-level data that is not available via PowerShell cmdlets. Use one of these approaches to populate the `$topics` variable:

**Option A: Dataverse API query** — Query bot component metadata directly:

```powershell
# Replace {botId} with the agent's Dataverse bot ID (from $agent.ChatbotName in Script 4's loop)
# Replace {orgUrl} with your Dataverse organization URL (e.g., https://contoso.crm.dynamics.com)
$botId = "your-bot-id-here"  # Copy from Script 4 output or Copilot Studio agent URL
$orgUrl = "https://contoso.crm.dynamics.com"

# Acquire an access token for Dataverse (requires Az module or MSAL)
# Option 1: Using Az module (install with Install-Module Az.Accounts)
# Connect-AzAccount
# $accessToken = (Get-AzAccessToken -ResourceUrl $orgUrl).Token
# Option 2: Use an existing token from your authentication flow
$accessToken = "your-access-token"

# Query topic components (componenttype 0 = Topic)
$response = Invoke-RestMethod -Uri "$orgUrl/api/data/v9.2/botcomponents?`$filter=_parentbotid_value eq '$botId' and componenttype eq 0" `
    -Headers @{ Authorization = "Bearer $accessToken" }
$topics = $response.value
```

**Option B: Manual CSV import** — Export topic data from Copilot Studio and import:

```csv
DisplayName,ContentModerationLevel
Customer Inquiry Topic,High
Account Balance Topic,Medium
General FAQ Topic,High
```

```powershell
$topics = Import-Csv -Path ".\AgentTopics.csv" | ForEach-Object {
    [PSCustomObject]@{
        Properties = @{
            DisplayName = $_.DisplayName
            ContentModeration = @{ Level = $_.ContentModerationLevel }
        }
    }
}
```

---

## Sample Zone Mapping File

Create `AgentZoneMapping.csv` for use with Script 3. Classify each agent using the zone decision framework in [Zones and Tiers](../../../framework/zones-and-tiers.md): Zone 1 = personal use only, Zone 2 = shared with team, Zone 3 = customer-facing or regulated.

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
- **Audit Monitoring:** Run Script 2 (audit log) daily in Zone 3 environments to detect unauthorized moderation changes between formal weekly reviews
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

[Back to Control 1.27](../../../controls/pillar-1-security/1.27-ai-agent-content-moderation-enforcement.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification & Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
