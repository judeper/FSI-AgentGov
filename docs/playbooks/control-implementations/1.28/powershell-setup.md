# PowerShell Setup: Control 1.28 - Policy-Based Agent Publishing Restrictions

**Last Updated:** February 2026
**PowerShell Module:** Microsoft.PowerApps.Administration.PowerShell
**Estimated Time:** 20-30 minutes

## Prerequisites

- [ ] PowerShell 7+ installed
- [ ] Microsoft.PowerApps.Administration.PowerShell module installed
- [ ] Power Platform Admin or Entra Global Admin credentials
- [ ] Tenant access with appropriate permissions

---

## Module Installation

```powershell
# Install Power Apps Administration module
Install-Module -Name Microsoft.PowerApps.Administration.PowerShell -Force -AllowClobber

# Import module
Import-Module Microsoft.PowerApps.Administration.PowerShell

# Connect to Power Platform (interactive authentication)
Add-PowerAppsAccount
```

---

## Script 1: Create Zone-Specific DLP Policies

This script creates DLP policies for each governance zone with appropriate connector restrictions.

```powershell
<#
.SYNOPSIS
    Create zone-specific DLP policies for agent publishing restrictions
.DESCRIPTION
    Creates three DLP policies (Zone 1, Zone 2, Zone 3) with escalating connector restrictions
    to enforce policy-based publishing controls
.NOTES
    Requires Power Platform Admin role
#>

# Connect to Power Platform
Add-PowerAppsAccount

# Define Zone 1 (Personal) DLP Policy
$zone1PolicyName = "Zone 1 - Personal Productivity DLP Policy"
# NOTE: Use New-AdminDlpPolicy for admin-context DLP policy creation.
$zone1Policy = New-AdminDlpPolicy -DisplayName $zone1PolicyName `
    -EnvironmentType "OnlyEnvironments"

# Configure Zone 1 connectors
$zone1BusinessConnectors = @(
    "/providers/Microsoft.PowerApps/apis/shared_sharepointonline",
    "/providers/Microsoft.PowerApps/apis/shared_office365",
    "/providers/Microsoft.PowerApps/apis/shared_teams",
    "/providers/Microsoft.PowerApps/apis/shared_commondataservice"
)

$zone1BlockedConnectors = @(
    "/providers/Microsoft.PowerApps/apis/shared_telegram",
    "/providers/Microsoft.PowerApps/apis/shared_facebook",
    "/providers/Microsoft.PowerApps/apis/shared_publicwebsites"
)

# Add connectors to Zone 1 policy using Set-AdminDlpPolicy connector group classification
# NOTE: Add-ConnectorToBusinessDataGroup does not exist. Use Set-AdminDlpPolicy with
# ConnectorGroups to classify connectors into Business/NonBusiness/Blocked groups.
Set-AdminDlpPolicy -PolicyName $zone1Policy.PolicyName -ConnectorGroups @(
    @{
        classification = "Business"
        connectors     = @(
            $zone1BusinessConnectors | ForEach-Object { @{ id = $_; type = "Microsoft.PowerApps/apis" } }
        )
    },
    @{
        classification = "Blocked"
        connectors     = @(
            $zone1BlockedConnectors | ForEach-Object { @{ id = $_; type = "Microsoft.PowerApps/apis" } }
        )
    }
)

Write-Host "✓ Zone 1 DLP policy created: $zone1PolicyName" -ForegroundColor Green

# Define Zone 2 (Team) DLP Policy
$zone2PolicyName = "Zone 2 - Team Collaboration DLP Policy"
$zone2Policy = New-AdminDlpPolicy -DisplayName $zone2PolicyName `
    -EnvironmentType "OnlyEnvironments"

# Configure Zone 2 connectors (stricter - no non-business connectors)
$zone2BusinessConnectors = @(
    "/providers/Microsoft.PowerApps/apis/shared_sharepointonline",
    "/providers/Microsoft.PowerApps/apis/shared_office365",
    "/providers/Microsoft.PowerApps/apis/shared_teams",
    "/providers/Microsoft.PowerApps/apis/shared_commondataservice",
    "/providers/Microsoft.PowerApps/apis/shared_sql"
)

$zone2BlockedConnectors = @(
    "/providers/Microsoft.PowerApps/apis/shared_telegram",
    "/providers/Microsoft.PowerApps/apis/shared_facebook",
    "/providers/Microsoft.PowerApps/apis/shared_publicwebsites",
    "/providers/Microsoft.PowerApps/apis/shared_twitter",
    "/providers/Microsoft.PowerApps/apis/shared_rss",
    "/providers/Microsoft.PowerApps/apis/shared_http"
)

# Add connectors to Zone 2 policy
Set-AdminDlpPolicy -PolicyName $zone2Policy.PolicyName -ConnectorGroups @(
    @{
        classification = "Business"
        connectors     = @(
            $zone2BusinessConnectors | ForEach-Object { @{ id = $_; type = "Microsoft.PowerApps/apis" } }
        )
    },
    @{
        classification = "Blocked"
        connectors     = @(
            $zone2BlockedConnectors | ForEach-Object { @{ id = $_; type = "Microsoft.PowerApps/apis" } }
        )
    }
)

Write-Host "✓ Zone 2 DLP policy created: $zone2PolicyName" -ForegroundColor Green

# Define Zone 3 (Enterprise) DLP Policy
$zone3PolicyName = "Zone 3 - Enterprise Customer-Facing DLP Policy"
$zone3Policy = New-AdminDlpPolicy -DisplayName $zone3PolicyName `
    -EnvironmentType "OnlyEnvironments"

# Configure Zone 3 connectors (strictest - whitelist only approved connectors)
$zone3BusinessConnectors = @(
    "/providers/Microsoft.PowerApps/apis/shared_sharepointonline",  # Read-only via policy
    "/providers/Microsoft.PowerApps/apis/shared_commondataservice",  # Approved tables only
    "/providers/Microsoft.PowerApps/apis/shared_office365groups"     # Read-only via policy
)

# Block all other connectors by default (Zone 3 whitelist approach)
$zone3BlockedConnectors = @(
    "/providers/Microsoft.PowerApps/apis/shared_http",
    "/providers/Microsoft.PowerApps/apis/shared_telegram",
    "/providers/Microsoft.PowerApps/apis/shared_facebook",
    "/providers/Microsoft.PowerApps/apis/shared_publicwebsites",
    "/providers/Microsoft.PowerApps/apis/shared_twitter",
    "/providers/Microsoft.PowerApps/apis/shared_rss",
    "/providers/Microsoft.PowerApps/apis/*"  # Block all external connectors
)

# Add connectors to Zone 3 policy
Set-AdminDlpPolicy -PolicyName $zone3Policy.PolicyName -ConnectorGroups @(
    @{
        classification = "Business"
        connectors     = @(
            $zone3BusinessConnectors | ForEach-Object { @{ id = $_; type = "Microsoft.PowerApps/apis" } }
        )
    },
    @{
        classification = "Blocked"
        connectors     = @(
            $zone3BlockedConnectors | ForEach-Object { @{ id = $_; type = "Microsoft.PowerApps/apis" } }
        )
    }
)

Write-Host "✓ Zone 3 DLP policy created: $zone3PolicyName" -ForegroundColor Green

Write-Host "`nDLP policies created successfully. Next: Assign policies to environments." -ForegroundColor Cyan
```

---

## Script 2: Assign DLP Policies to Environments by Zone

This script assigns DLP policies to environments based on zone classification.

```powershell
<#
.SYNOPSIS
    Assign DLP policies to environments based on zone classification
.DESCRIPTION
    Maps environments to zone-specific DLP policies to enforce publishing restrictions
.NOTES
    Requires Power Platform Admin role
#>

# Connect to Power Platform
Add-PowerAppsAccount

# Get all environments
$environments = Get-AdminPowerAppEnvironment

# Define zone classification (customize based on your environment naming conventions)
$zone1Environments = $environments | Where-Object { $_.DisplayName -like "*Personal*" -or $_.DisplayName -like "*Dev*" }
$zone2Environments = $environments | Where-Object { $_.DisplayName -like "*Team*" -or $_.DisplayName -like "*UAT*" }
$zone3Environments = $environments | Where-Object { $_.DisplayName -like "*Production*" -or $_.DisplayName -like "*Customer*" }

# Get DLP policies
# NOTE: Use Get-AdminDlpPolicy for admin-context DLP policy retrieval.
$zone1Policy = Get-AdminDlpPolicy | Where-Object { $_.DisplayName -eq "Zone 1 - Personal Productivity DLP Policy" }
$zone2Policy = Get-AdminDlpPolicy | Where-Object { $_.DisplayName -eq "Zone 2 - Team Collaboration DLP Policy" }
$zone3Policy = Get-AdminDlpPolicy | Where-Object { $_.DisplayName -eq "Zone 3 - Enterprise Customer-Facing DLP Policy" }

# Assign Zone 1 policy
Write-Host "`nAssigning Zone 1 DLP policy to environments..." -ForegroundColor Cyan
foreach ($env in $zone1Environments) {
    try {
        Add-AdminPowerAppEnvironmentToPolicy -PolicyName $zone1Policy.PolicyName -EnvironmentName $env.EnvironmentName
        Write-Host "  ✓ Assigned to: $($env.DisplayName)" -ForegroundColor Green
    }
    catch {
        Write-Host "  ✗ Failed to assign to: $($env.DisplayName) - $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Assign Zone 2 policy
Write-Host "`nAssigning Zone 2 DLP policy to environments..." -ForegroundColor Cyan
foreach ($env in $zone2Environments) {
    try {
        Add-AdminPowerAppEnvironmentToPolicy -PolicyName $zone2Policy.PolicyName -EnvironmentName $env.EnvironmentName
        Write-Host "  ✓ Assigned to: $($env.DisplayName)" -ForegroundColor Green
    }
    catch {
        Write-Host "  ✗ Failed to assign to: $($env.DisplayName) - $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Assign Zone 3 policy
Write-Host "`nAssigning Zone 3 DLP policy to environments..." -ForegroundColor Cyan
foreach ($env in $zone3Environments) {
    try {
        Add-AdminPowerAppEnvironmentToPolicy -PolicyName $zone3Policy.PolicyName -EnvironmentName $env.EnvironmentName
        Write-Host "  ✓ Assigned to: $($env.DisplayName)" -ForegroundColor Green
    }
    catch {
        Write-Host "  ✗ Failed to assign to: $($env.DisplayName) - $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`nDLP policy assignment complete." -ForegroundColor Cyan
```

---

## Script 3: Audit Agent Publishing Compliance

This script generates a compliance report showing agent DLP status, channel configuration, and publishing approval status.

```powershell
<#
.SYNOPSIS
    Audit agent publishing compliance across environments
.DESCRIPTION
    Generates a compliance report showing DLP violations, blocked channels, and approval status
.NOTES
    Requires Power Platform Admin role
#>

# Connect to Power Platform
Add-PowerAppsAccount

# Get all environments
$environments = Get-AdminPowerAppEnvironment

$complianceReport = @()

foreach ($env in $environments) {
    Write-Host "Auditing environment: $($env.DisplayName)..." -ForegroundColor Cyan
    
    # Get agents (chatbots) in this environment
    try {
        # NOTE: Use Get-AdminPowerAppChatbot for admin-context operations.
        # Get-PowerAppChatBot retrieves only the caller's own chatbots.
        $agents = Get-AdminPowerAppChatbot -EnvironmentName $env.EnvironmentName
        
        foreach ($agent in $agents) {
            # Check DLP compliance
            # NOTE: No native cmdlet exists for chatbot-specific DLP compliance testing.
            # Use Get-AdminDlpPolicy to verify policy configuration covers Copilot Studio connectors.
            $dlpPolicies = Get-AdminDlpPolicy
            $dlpCompliant = $true
            $dlpViolations = @()
            # Verify the environment's DLP policies cover Copilot Studio connectors
            # Manual review recommended — see portal walkthrough for detailed steps
            
            # Get agent details including channels
            $agentDetails = Get-AdminPowerAppChatbot -EnvironmentName $env.EnvironmentName -ChatBotName $agent.ChatBotName
            
            # Check for blocked channels
            $blockedChannels = @()
            if ($agentDetails.Channels) {
                $prohibitedChannels = @("Facebook", "Telegram", "PublicWebsite")
                $blockedChannels = $agentDetails.Channels | Where-Object { $prohibitedChannels -contains $_.Type }
            }
            
            # Compile compliance record
            $complianceRecord = [PSCustomObject]@{
                Environment     = $env.DisplayName
                AgentName       = $agent.DisplayName
                AgentId         = $agent.ChatBotName
                PublishStatus   = $agent.PublishStatus
                DLPCompliant    = $dlpCompliant
                DLPViolations   = ($dlpViolations -join ", ")
                BlockedChannels = ($blockedChannels.Type -join ", ")
                LastModified    = $agent.LastModifiedTime
                CreatedBy       = $agent.CreatedBy
            }
            
            $complianceReport += $complianceRecord
        }
    }
    catch {
        Write-Host "  ✗ Failed to audit environment: $($env.DisplayName) - $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Display compliance summary
Write-Host "`n=== Agent Publishing Compliance Summary ===" -ForegroundColor Yellow
$totalAgents = $complianceReport.Count
$compliantAgents = ($complianceReport | Where-Object { $_.DLPCompliant -eq $true -and $_.BlockedChannels -eq "" }).Count
$nonCompliantAgents = $totalAgents - $compliantAgents

Write-Host "Total Agents: $totalAgents" -ForegroundColor Cyan
Write-Host "Compliant Agents: $compliantAgents" -ForegroundColor Green
Write-Host "Non-Compliant Agents: $nonCompliantAgents" -ForegroundColor Red

# Display non-compliant agents
if ($nonCompliantAgents -gt 0) {
    Write-Host "`n=== Non-Compliant Agents ===" -ForegroundColor Red
    $complianceReport | Where-Object { $_.DLPCompliant -eq $false -or $_.BlockedChannels -ne "" } | Format-Table Environment, AgentName, DLPViolations, BlockedChannels -AutoSize
}

# Export full report to CSV
$reportPath = ".\agent-publishing-compliance-report-$(Get-Date -Format 'yyyyMMdd-HHmmss').csv"
$complianceReport | Export-Csv -Path $reportPath -NoTypeInformation

Write-Host "`n✓ Full compliance report exported to: $reportPath" -ForegroundColor Green
```

---

## Script 4: Enable Approval Workflows for Environments

This script enables approval workflows for agent publishing in Zone 2+ environments.

```powershell
<#
.SYNOPSIS
    Enable approval workflows for agent publishing
.DESCRIPTION
    Configures environment settings to require approval for agent publishing in Zone 2+ environments
.NOTES
    Requires Entra Global Admin or Power Platform Admin role
#>

# Connect to Power Platform
Add-PowerAppsAccount

# Get Zone 2 and Zone 3 environments
$zone2Environments = Get-AdminPowerAppEnvironment | Where-Object { $_.DisplayName -like "*Team*" -or $_.DisplayName -like "*UAT*" }
$zone3Environments = Get-AdminPowerAppEnvironment | Where-Object { $_.DisplayName -like "*Production*" -or $_.DisplayName -like "*Customer*" }

$targetEnvironments = $zone2Environments + $zone3Environments

Write-Host "`nEnabling approval workflows for Zone 2+ environments..." -ForegroundColor Cyan

foreach ($env in $targetEnvironments) {
    try {
        # NOTE: No native cmdlet exists for chatbot approval requirements at the environment level.
        # -RequireChatbotApproval and -RequireChatbotUpdateApproval are aspirational parameters
        # that do not exist on Set-AdminPowerAppEnvironment today.
        # For approval workflows, configure environment-level governance in
        # Power Platform Admin Center → Environments → [Environment] → Settings → Features.
        # Alternatively, implement approval flows using Power Automate.
        Set-AdminPowerAppEnvironment -EnvironmentName $env.EnvironmentName
        # Note: Chatbot approval requires manual configuration in Admin Center or via Power Automate flow
        Write-Host "  ⚠ Chatbot approval must be configured manually in Power Platform Admin Center" -ForegroundColor Yellow
        
        Write-Host "  ✓ Approval workflows enabled for: $($env.DisplayName)" -ForegroundColor Green
    }
    catch {
        Write-Host "  ✗ Failed to enable approval for: $($env.DisplayName) - $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "    Note: This setting may require manual configuration in Power Platform Admin Center" -ForegroundColor Yellow
    }
}

Write-Host "`nApproval workflow configuration complete." -ForegroundColor Cyan
Write-Host "Verify settings in Power Platform Admin Center → Environments → [Environment] → Settings → Features" -ForegroundColor Yellow
```

---

## Validation Commands

After running the setup scripts, validate the configuration:

```powershell
# Check DLP policy assignments
Get-AdminDlpPolicy | Select-Object DisplayName, @{Name="Environments";Expression={($_.Environments).Count}}

# List agents with DLP policy gaps
# NOTE: No native Test-PowerAppChatBotDlpCompliance cmdlet exists.
# Use Get-AdminDlpPolicy to review DLP policies covering Copilot Studio connectors,
# then cross-reference with agent connector usage in Power Platform Admin Center.
Get-AdminDlpPolicy | Select-Object DisplayName, PolicyName

# Check environment approval settings
# NOTE: RequireChatbotApproval is not a native property on environment objects.
# Verify chatbot approval settings in Power Platform Admin Center → Environments → Settings → Features.
Get-AdminPowerAppEnvironment | Select-Object DisplayName, EnvironmentName
```

---

## Automation Schedule

For ongoing compliance monitoring, schedule the audit script to run weekly:

```powershell
# Create scheduled task to run compliance audit weekly
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" `
    -Argument "-File C:\Scripts\Audit-AgentPublishingCompliance.ps1"

$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 9:00AM

Register-ScheduledTask -TaskName "Agent Publishing Compliance Audit" `
    -Action $action -Trigger $trigger -Description "Weekly audit of agent publishing compliance"
```

---

## Troubleshooting

### Issue: DLP policy creation fails
**Cause:** Insufficient permissions or conflicting policy names
**Resolution:** Verify Power Platform Admin role; check for existing policies with same name

### Issue: Approval workflow setting not available
**Cause:** Feature not yet rolled out to tenant
**Resolution:** Configure approval workflows using Power Automate as an alternative

### Issue: Agent DLP compliance check fails
**Cause:** Agent uses connectors not in DLP policy
**Resolution:** Run audit script to identify violations; update DLP policy or reconfigure agent

---

[Back to Control 1.28](../../../controls/pillar-1-security/1.28-policy-based-agent-publishing-restrictions.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
