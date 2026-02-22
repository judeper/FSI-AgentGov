# PowerShell Setup: Control 2.23 - User Consent and AI Disclosure Enforcement

**Last Updated:** February 2026
**PowerShell Version Required:** 7.2+
**Estimated Time:** 30-40 minutes

## Prerequisites

- [ ] PowerShell 7.2 or later installed
- [ ] Microsoft Graph PowerShell SDK installed (`Install-Module Microsoft.Graph`)
- [ ] Power Platform Admin PowerShell module installed (`Install-Module Microsoft.PowerApps.Administration.PowerShell`)
- [ ] Entra Global Admin or Purview Compliance Admin role
- [ ] Power Platform Admin role
- [ ] Dataverse environment with `fsi_aiconsent` table deployed (Zone 3)

---

## Module Installation and Authentication

### Step 1: Install Required Modules

```powershell
# Install Microsoft Graph PowerShell SDK
Install-Module Microsoft.Graph -Scope CurrentUser -Force

# Install Power Platform Admin module
Install-Module Microsoft.PowerApps.Administration.PowerShell -Scope CurrentUser -Force

# Verify installations
Get-Module Microsoft.Graph -ListAvailable
Get-Module Microsoft.PowerApps.Administration.PowerShell -ListAvailable
```

### Step 2: Authenticate to Microsoft Graph

```powershell
# Connect to Microsoft Graph with required scopes
Connect-MgGraph -Scopes "Organization.Read.All", "Directory.Read.All", "Policy.Read.All"

# Verify connection
Get-MgContext
```

### Step 3: Authenticate to Power Platform

```powershell
# Connect to Power Platform (interactive authentication)
Add-PowerAppsAccount

# Verify connection
Get-AdminPowerAppEnvironment | Select-Object -First 1
```

---

## Script 1: Get Tenant-Wide AI Disclaimer Configuration

### Purpose
Retrieve the current status of the tenant-wide AI Disclaimer toggle and custom disclosure URL from Microsoft 365 admin center settings.

### Script: `Get-TenantAIDisclaimer.ps1`

```powershell
<#
.SYNOPSIS
    Retrieves tenant-wide AI Disclaimer configuration for Microsoft 365 Copilot.

.DESCRIPTION
    Queries Microsoft 365 tenant settings to retrieve the AI Disclaimer toggle status
    and custom disclosure URL. Outputs the configuration for governance reporting.

.EXAMPLE
    .\Get-TenantAIDisclaimer.ps1

.NOTES
    Requires: Microsoft Graph PowerShell SDK, Organization.Read.All scope
    Author: FSI Agent Governance Framework
    Last Updated: February 2026
#>

# Authenticate to Microsoft Graph if not already connected
if (-not (Get-MgContext)) {
    Connect-MgGraph -Scopes "Organization.Read.All"
}

# Retrieve organization settings
Write-Host "Retrieving tenant-wide AI Disclaimer configuration..." -ForegroundColor Cyan

try {
    # Note: This is a conceptual API endpoint; actual Graph API may differ
    # Check Microsoft Graph documentation for the correct endpoint
    $tenantSettings = Invoke-MgGraphRequest -Method GET -Uri "https://graph.microsoft.com/v1.0/admin/copilot/settings"
    
    $disclaimerConfig = [PSCustomObject]@{
        TenantId = (Get-MgOrganization).Id
        TenantName = (Get-MgOrganization).DisplayName
        AIDisclaimerEnabled = $tenantSettings.aiDisclaimerEnabled
        CustomDisclosureURL = $tenantSettings.customDisclosureUrl
        LastModifiedDateTime = $tenantSettings.lastModifiedDateTime
        LastModifiedBy = $tenantSettings.lastModifiedBy
        ComplianceStatus = if ($tenantSettings.aiDisclaimerEnabled) { "Compliant" } else { "Non-Compliant" }
    }
    
    $disclaimerConfig | Format-List
    
    # Export to CSV for reporting
    $outputPath = ".\TenantAIDisclaimer_$(Get-Date -Format 'yyyyMMdd_HHmmss').csv"
    $disclaimerConfig | Export-Csv -Path $outputPath -NoTypeInformation
    Write-Host "Configuration exported to: $outputPath" -ForegroundColor Green
}
catch {
    Write-Error "Failed to retrieve AI Disclaimer configuration: $_"
}
```

### Usage

```powershell
# Run the script to get current configuration
.\Get-TenantAIDisclaimer.ps1

# Expected Output:
# TenantId             : 12345678-1234-1234-1234-123456789012
# TenantName           : Contoso Financial Services
# AIDisclaimerEnabled  : True
# CustomDisclosureURL  : https://contoso.com/policies/ai-transparency
# LastModifiedDateTime : 2026-02-10T14:32:00Z
# LastModifiedBy       : admin@contoso.com
# ComplianceStatus     : Compliant
```

---

## Script 2: Get Agent-Level Disclosure Configuration

### Purpose
Audit all Copilot Studio agents to identify which have AI disclosure configured in their greeting topics.

### Script: `Get-AgentDisclosureInventory.ps1`

```powershell
<#
.SYNOPSIS
    Audits all Copilot Studio agents for AI disclosure configuration in greeting topics.

.DESCRIPTION
    Retrieves all agents across Power Platform environments and checks for AI disclosure
    language in greeting topics. Outputs an inventory for governance reporting.

.PARAMETER EnvironmentName
    Optional. Filter to a specific Power Platform environment. If not specified, scans all environments.

.EXAMPLE
    .\Get-AgentDisclosureInventory.ps1

.EXAMPLE
    .\Get-AgentDisclosureInventory.ps1 -EnvironmentName "Default-12345678-1234-1234-1234-123456789012"

.NOTES
    Requires: Power Platform Admin PowerShell module
    Author: FSI Agent Governance Framework
    Last Updated: February 2026
#>

param(
    [string]$EnvironmentName
)

# Authenticate to Power Platform if not already connected
if (-not (Get-AdminPowerAppEnvironment -ErrorAction SilentlyContinue)) {
    Add-PowerAppsAccount
}

Write-Host "Retrieving agent disclosure configuration inventory..." -ForegroundColor Cyan

$environments = if ($EnvironmentName) {
    Get-AdminPowerAppEnvironment -EnvironmentName $EnvironmentName
} else {
    Get-AdminPowerAppEnvironment
}

$agentInventory = @()

foreach ($env in $environments) {
    Write-Host "Scanning environment: $($env.DisplayName)..." -ForegroundColor Yellow
    
    # Get all bots/agents in the environment
    $agents = Get-AdminPowerAppChatBot -EnvironmentName $env.EnvironmentName
    
    foreach ($agent in $agents) {
        Write-Host "  Checking agent: $($agent.DisplayName)..." -ForegroundColor Gray
        
        # Attempt to retrieve greeting topic (note: actual API may differ)
        try {
            $greetingTopic = Get-AdminPowerAppChatBotTopic -EnvironmentName $env.EnvironmentName -BotName $agent.BotName -TopicName "Greeting"
            
            $hasDisclosure = if ($greetingTopic.Content -match "AI|artificial intelligence|monitoring|consent") {
                $true
            } else {
                $false
            }
            
            $agentRecord = [PSCustomObject]@{
                EnvironmentName = $env.EnvironmentName
                EnvironmentDisplayName = $env.DisplayName
                AgentName = $agent.DisplayName
                AgentId = $agent.BotName
                HasGreetingTopic = $true
                HasAIDisclosure = $hasDisclosure
                LastModified = $agent.LastModifiedTime
                ComplianceStatus = if ($hasDisclosure) { "Compliant" } else { "Review Required" }
            }
        }
        catch {
            $agentRecord = [PSCustomObject]@{
                EnvironmentName = $env.EnvironmentName
                EnvironmentDisplayName = $env.DisplayName
                AgentName = $agent.DisplayName
                AgentId = $agent.BotName
                HasGreetingTopic = $false
                HasAIDisclosure = $false
                LastModified = $agent.LastModifiedTime
                ComplianceStatus = "No Greeting Topic"
            }
        }
        
        $agentInventory += $agentRecord
    }
}

# Display summary
Write-Host "`nAgent Disclosure Inventory Summary:" -ForegroundColor Cyan
$agentInventory | Format-Table -AutoSize

$totalAgents = $agentInventory.Count
$compliantAgents = ($agentInventory | Where-Object { $_.ComplianceStatus -eq "Compliant" }).Count
$nonCompliantAgents = $totalAgents - $compliantAgents

Write-Host "`nTotal Agents: $totalAgents" -ForegroundColor White
Write-Host "Compliant: $compliantAgents" -ForegroundColor Green
Write-Host "Non-Compliant/Review Required: $nonCompliantAgents" -ForegroundColor Red

# Export to CSV
$outputPath = ".\AgentDisclosureInventory_$(Get-Date -Format 'yyyyMMdd_HHmmss').csv"
$agentInventory | Export-Csv -Path $outputPath -NoTypeInformation
Write-Host "`nInventory exported to: $outputPath" -ForegroundColor Green
```

---

## Script 3: Get Consent Records from Dataverse (Zone 3)

### Purpose
Retrieve user consent acknowledgment records from the Dataverse `fsi_aiconsent` table for Zone 3 agents.

### Script: `Get-ConsentRecords.ps1`

```powershell
<#
.SYNOPSIS
    Retrieves user consent acknowledgment records from Dataverse for Zone 3 agents.

.DESCRIPTION
    Queries the fsi_aiconsent Dataverse table to retrieve consent records, including
    user identity, timestamp, disclosure version, and acknowledgment status.

.PARAMETER EnvironmentUrl
    The Dataverse environment URL (e.g., https://contoso.crm.dynamics.com)

.PARAMETER AgentName
    Optional. Filter consent records for a specific agent.

.PARAMETER DaysBack
    Optional. Retrieve consent records from the last N days. Default is 30 days.

.EXAMPLE
    .\Get-ConsentRecords.ps1 -EnvironmentUrl "https://contoso.crm.dynamics.com"

.EXAMPLE
    .\Get-ConsentRecords.ps1 -EnvironmentUrl "https://contoso.crm.dynamics.com" -AgentName "Customer Service Agent" -DaysBack 7

.NOTES
    Requires: Dataverse environment with fsi_aiconsent table deployed
    Requires: Microsoft.PowerApps.Administration.PowerShell module
    Author: FSI Agent Governance Framework
    Last Updated: February 2026
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$EnvironmentUrl,
    
    [string]$AgentName,
    
    [int]$DaysBack = 30
)

# Helper function to get access token (conceptual - implement based on your auth method)
function Get-AccessToken {
    param([string]$EnvironmentUrl)
    # This is a placeholder - implement actual OAuth token acquisition
    # Example: Use MSAL.PS or Azure CLI to get token
    # az account get-access-token --resource $EnvironmentUrl --query accessToken -o tsv
    Write-Warning "Implement Get-AccessToken function with your authentication method"
    return ""
}

Write-Host "Retrieving consent records from Dataverse..." -ForegroundColor Cyan

# Calculate date filter
$startDate = (Get-Date).AddDays(-$DaysBack).ToString("yyyy-MM-dd")

# Build FetchXML query
$fetchXml = @"
<fetch>
  <entity name='fsi_aiconsent'>
    <attribute name='fsi_userid' />
    <attribute name='fsi_agentname' />
    <attribute name='fsi_consenttimestamp' />
    <attribute name='fsi_disclosureversion' />
    <attribute name='fsi_acknowledgmentstatus' />
    <attribute name='createdon' />
    <filter>
      <condition attribute='fsi_consenttimestamp' operator='on-or-after' value='$startDate' />
"@

if ($AgentName) {
    $fetchXml += @"
      <condition attribute='fsi_agentname' operator='eq' value='$AgentName' />
"@
}

$fetchXml += @"
    </filter>
    <order attribute='fsi_consenttimestamp' descending='true' />
  </entity>
</fetch>
"@

try {
    # Note: This uses a conceptual approach; actual Dataverse PowerShell cmdlet may differ
    # You may need to use Invoke-RestMethod with Dataverse Web API
    
    $authHeader = @{
        "Authorization" = "Bearer $(Get-AccessToken -EnvironmentUrl $EnvironmentUrl)"
        "Content-Type" = "application/json"
        "OData-MaxVersion" = "4.0"
        "OData-Version" = "4.0"
    }
    
    $apiUrl = "$EnvironmentUrl/api/data/v9.2/fsi_aiconsents?fetchXml=$([uri]::EscapeDataString($fetchXml))"
    $response = Invoke-RestMethod -Uri $apiUrl -Headers $authHeader -Method Get
    
    $consentRecords = $response.value | ForEach-Object {
        [PSCustomObject]@{
            UserId = $_.fsi_userid
            AgentName = $_.fsi_agentname
            ConsentTimestamp = $_.fsi_consenttimestamp
            DisclosureVersion = $_.fsi_disclosureversion
            AcknowledgmentStatus = $_.fsi_acknowledgmentstatus
            CreatedOn = $_.createdon
        }
    }
    
    # Display records
    Write-Host "`nConsent Records:" -ForegroundColor Cyan
    $consentRecords | Format-Table -AutoSize
    
    # Summary
    $totalRecords = $consentRecords.Count
    $acknowledgedCount = ($consentRecords | Where-Object { $_.AcknowledgmentStatus -eq $true }).Count
    
    Write-Host "`nTotal Consent Records (last $DaysBack days): $totalRecords" -ForegroundColor White
    Write-Host "Acknowledged: $acknowledgedCount" -ForegroundColor Green
    
    # Export to CSV
    $outputPath = ".\ConsentRecords_$(Get-Date -Format 'yyyyMMdd_HHmmss').csv"
    $consentRecords | Export-Csv -Path $outputPath -NoTypeInformation
    Write-Host "Consent records exported to: $outputPath" -ForegroundColor Green
}
catch {
    Write-Error "Failed to retrieve consent records: $_"
}
```

---

## Script 4: Verify Consent Compliance (Zone 3)

### Purpose
Check for users who have interacted with Zone 3 agents without valid consent acknowledgment records.

### Script: `Verify-ConsentCompliance.ps1`

```powershell
<#
.SYNOPSIS
    Verifies consent compliance by checking for Zone 3 agent interactions without valid consent.

.DESCRIPTION
    Cross-references agent usage logs with consent records to identify users who have
    accessed Zone 3 agents without valid consent acknowledgment within the required timeframe.

.PARAMETER EnvironmentUrl
    The Dataverse environment URL

.PARAMETER ConsentValidityDays
    Number of days a consent record remains valid before re-acknowledgment is required. Default is 90.

.EXAMPLE
    .\Verify-ConsentCompliance.ps1 -EnvironmentUrl "https://contoso.crm.dynamics.com"

.EXAMPLE
    .\Verify-ConsentCompliance.ps1 -EnvironmentUrl "https://contoso.crm.dynamics.com" -ConsentValidityDays 60

.NOTES
    Requires: Dataverse environment with fsi_aiconsent and usage log tables
    Author: FSI Agent Governance Framework
    Last Updated: February 2026
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$EnvironmentUrl,
    
    [int]$ConsentValidityDays = 90
)

Write-Host "Verifying consent compliance for Zone 3 agents..." -ForegroundColor Cyan

# Calculate valid consent date threshold
$validConsentDate = (Get-Date).AddDays(-$ConsentValidityDays)

# This is a conceptual script - actual implementation would:
# 1. Query agent usage logs for Zone 3 agents
# 2. For each user interaction, check for valid consent record
# 3. Identify users without valid consent

# Placeholder for actual implementation
Write-Host "Consent compliance verification requires:" -ForegroundColor Yellow
Write-Host "  1. Agent usage log table in Dataverse" -ForegroundColor Gray
Write-Host "  2. Zone 3 agent classification data" -ForegroundColor Gray
Write-Host "  3. Cross-reference with fsi_aiconsent table" -ForegroundColor Gray
Write-Host "`nImplement this script based on your specific Dataverse schema." -ForegroundColor Yellow

# Example output structure
$complianceReport = @(
    [PSCustomObject]@{
        UserId = "user1@contoso.com"
        AgentName = "Investment Advisory Agent"
        LastInteraction = "2026-02-10"
        ConsentStatus = "Valid"
        ConsentDate = "2025-12-15"
        DaysSinceConsent = 57
    },
    [PSCustomObject]@{
        UserId = "user2@contoso.com"
        AgentName = "Customer Service Agent"
        LastInteraction = "2026-02-11"
        ConsentStatus = "Expired"
        ConsentDate = "2025-09-01"
        DaysSinceConsent = 163
    }
)

$complianceReport | Format-Table -AutoSize

# Export results
$outputPath = ".\ConsentComplianceReport_$(Get-Date -Format 'yyyyMMdd_HHmmss').csv"
$complianceReport | Export-Csv -Path $outputPath -NoTypeInformation
Write-Host "Compliance report exported to: $outputPath" -ForegroundColor Green
```

---

## Script 5: Generate Disclosure Compliance Report

### Purpose
Generate a comprehensive compliance report showing disclosure configuration status across tenant, agents, and consent tracking.

### Script: `New-DisclosureComplianceReport.ps1`

```powershell
<#
.SYNOPSIS
    Generates a comprehensive disclosure compliance report.

.DESCRIPTION
    Aggregates data from tenant-wide AI Disclaimer settings, agent-level disclosure
    configurations, and consent records to produce a compliance report.

.EXAMPLE
    .\New-DisclosureComplianceReport.ps1

.NOTES
    Calls other scripts in this playbook to gather data
    Author: FSI Agent Governance Framework
    Last Updated: February 2026
#>

Write-Host "Generating Disclosure Compliance Report..." -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan

# Section 1: Tenant-Wide Configuration
Write-Host "`n[1/3] Retrieving Tenant-Wide AI Disclaimer Configuration..." -ForegroundColor Yellow
& .\Get-TenantAIDisclaimer.ps1

# Section 2: Agent-Level Disclosure Inventory
Write-Host "`n[2/3] Retrieving Agent-Level Disclosure Inventory..." -ForegroundColor Yellow
& .\Get-AgentDisclosureInventory.ps1

# Section 3: Consent Records (if Dataverse URL provided)
Write-Host "`n[3/3] Consent Records..." -ForegroundColor Yellow
$dataverseUrl = Read-Host "Enter Dataverse environment URL for Zone 3 consent records (or press Enter to skip)"
if ($dataverseUrl) {
    & .\Get-ConsentRecords.ps1 -EnvironmentUrl $dataverseUrl -DaysBack 30
} else {
    Write-Host "Consent records section skipped." -ForegroundColor Gray
}

# Summary
Write-Host "`n" + "=" * 80 -ForegroundColor Cyan
Write-Host "Disclosure Compliance Report Complete" -ForegroundColor Green
Write-Host "Review the generated CSV files for detailed analysis." -ForegroundColor White
```

---

## Deployment Checklist

After running these scripts, verify:

- [ ] Tenant-wide AI Disclaimer toggle is enabled (Get-TenantAIDisclaimer.ps1 shows Compliant)
- [ ] Custom disclosure URL is configured and accessible
- [ ] All Zone 2 and Zone 3 agents have AI disclosure in greeting topics (Get-AgentDisclosureInventory.ps1 shows Compliant)
- [ ] Zone 3 agents have consent records in Dataverse for all active users (Get-ConsentRecords.ps1)
- [ ] No expired consent records for users who have recently interacted with Zone 3 agents (Verify-ConsentCompliance.ps1)
- [ ] Compliance reports are generated and stored for audit trail (New-DisclosureComplianceReport.ps1)

---

## Automation and Scheduling

To schedule automated compliance checks:

```powershell
# Create a scheduled task to run daily compliance report
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" `
    -Argument "-File C:\Scripts\New-DisclosureComplianceReport.ps1"

$trigger = New-ScheduledTaskTrigger -Daily -At 6:00AM

Register-ScheduledTask -TaskName "AI Disclosure Compliance Check" `
    -Action $action -Trigger $trigger -Description "Daily disclosure compliance report"
```

---

[Back to Control 2.23](../../../controls/pillar-2-management/2.23-user-consent-and-ai-disclosure-enforcement.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
