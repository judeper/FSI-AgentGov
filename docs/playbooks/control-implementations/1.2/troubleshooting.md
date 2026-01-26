# Troubleshooting: Control 1.2 - Agent Registry and Integrated Apps Management

**Last Updated:** January 2026

## Common Issues

| Issue | Cause | Resolution |
|-------|-------|------------|
| Agents not appearing in Integrated Apps | Agent not published to Teams | Verify agent is published to a Teams channel |
| PowerShell discovery missing agents | Insufficient permissions | Verify Power Platform Admin role |
| Registry drift detected | Manual processes not followed | Increase automation; add workflow enforcement |
| Orphaned agents found | Owner left organization | Implement offboarding checklist with agent transfer |
| Approval workflow bypassed | Settings not enforced | Enable "Require admin approval" in environment settings |
| Duplicate entries in registry | No unique identifier enforcement | Add validation rules to SharePoint list |

---

## Detailed Troubleshooting

### Issue: Agents Not Appearing in Integrated Apps

**Symptoms:** Published Copilot Studio agents don't show in M365 Admin Center

**Diagnostic Steps:**

1. Verify agent is published (not just created)
2. Check that the agent is published to a Teams channel
3. Wait 24 hours for sync (can take time)
4. Verify agent is in a Managed Environment
5. Check if app registration was created in Entra ID

**Resolution:**
- Publish agent to Microsoft Teams channel
- Wait for sync to complete
- If still missing after 48 hours, contact Microsoft support

---

### Issue: PowerShell Discovery Missing Agents

**Symptoms:** Script doesn't find all known agents

**Diagnostic Steps:**

1. Verify account has Power Platform Admin role:
   ```powershell
   # Check current user's admin roles
   Get-AdminPowerAppEnvironment | Select-Object -First 1
   # If this fails, you lack admin permissions
   ```

2. Check all environments are accessible:
   ```powershell
   Get-AdminPowerAppEnvironment | Format-Table DisplayName, EnvironmentName
   ```

3. Run discovery for each environment individually:
   ```powershell
   $EnvName = "specific-environment-id"
   Get-AdminPowerApp -EnvironmentName $EnvName | Format-Table DisplayName, Owner
   ```

4. Some agent types may require different API calls

**Resolution:**
- Request Power Platform Admin role in Entra ID
- Check if tenant isolation is blocking access to some environments
- Use Graph API for Copilot Studio-specific discovery

---

### Issue: Registry Drift - Mismatches Between Registry and Actual

**Symptoms:** Registry shows different agents than discovery

**Diagnostic Steps:**

1. Export both sources (registry and discovery) to CSV
2. Compare using PowerShell or Excel:
   ```powershell
   $Registry = Import-Csv "Registry.csv"
   $Discovered = Import-Csv "Discovered.csv"

   # Find agents in discovered but not registry
   $Missing = $Discovered | Where-Object { $_.AgentID -notin $Registry.AgentID }
   $Missing | Export-Csv "MissingFromRegistry.csv"

   # Find agents in registry but not discovered (potentially deleted)
   $Stale = $Registry | Where-Object { $_.AgentID -notin $Discovered.AgentID }
   $Stale | Export-Csv "StaleInRegistry.csv"
   ```

**Resolution:**
- Implement more frequent automated scans
- Add workflow to require registry update before publishing
- Enable Power Platform audit logging to track changes
- Create reconciliation report for weekly review

---

### Issue: Orphaned Agents (Owner Left Organization)

**Symptoms:** Agent owner email is invalid/disabled

**Diagnostic Steps:**

1. Query Entra ID to identify orphaned agent owners:
   ```powershell
   Connect-MgGraph -Scopes "User.Read.All"

   foreach ($Agent in $AgentInventory) {
       try {
           $User = Get-MgUser -UserId $Agent.OwnerEmail -ErrorAction Stop
           Write-Host "Valid: $($Agent.AgentName)" -ForegroundColor Green
       } catch {
           Write-Host "ORPHAN: $($Agent.AgentName) - Owner: $($Agent.OwnerEmail)" -ForegroundColor Red
       }
   }
   ```

2. Check if owner account is disabled vs. deleted

**Resolution:**
- Establish ownership transfer process in offboarding
- Assign backup owners for all Tier 2-3 agents
- Flag orphaned agents for immediate reassignment
- Add "Backup Owner" field to registry schema

---

### Issue: Approval Workflow Not Enforcing

**Symptoms:** Agents being published without approval records

**Diagnostic Steps:**

1. Verify environment settings:
   - Power Platform Admin Center > Environments > [env] > Settings > Features
   - Check "Require admin approval for publishing"

2. Review audit logs for publishing events:
   ```powershell
   Search-UnifiedAuditLog -StartDate (Get-Date).AddDays(-7) -EndDate (Get-Date) `
       -Operations "Published bot" -ResultSize 100
   ```

3. Check if user has Dataverse System Admin role (bypasses restrictions)

**Resolution:**
- Enable "Require admin approval" in environment settings
- Remove Dataverse System Admin role from non-admin users
- Implement DLP policies to block channel connectors until approved

---

## How to Confirm Configuration is Active

### Via Portal (M365 Admin Center)

1. Navigate to **Settings** > **Integrated Apps**
2. Verify all published agents are listed
3. Check user consent settings are configured

### Via Portal (Power Platform)

1. Navigate to **Manage** > **Environments**
2. Select environment > **Settings** > **Features**
3. Verify approval settings are enabled

### Via SharePoint

1. Navigate to registry list
2. Verify columns match metadata schema
3. Check permissions are correctly configured
4. Review automation flow status

### Via PowerShell

```powershell
# Quick validation check
Write-Host "=== Registry Configuration Check ===" -ForegroundColor Cyan

# Check 1: Can access environments
$Envs = Get-AdminPowerAppEnvironment
Write-Host "Environments accessible: $($Envs.Count)" -ForegroundColor Cyan

# Check 2: Count agents across environments
$TotalAgents = 0
foreach ($Env in $Envs) {
    $Apps = Get-AdminPowerApp -EnvironmentName $Env.EnvironmentName
    $TotalAgents += $Apps.Count
}
Write-Host "Total agents discovered: $TotalAgents" -ForegroundColor Cyan

# Check 3: Verify Graph API access for Integrated Apps
try {
    Connect-MgGraph -Scopes "Application.Read.All" -NoWelcome
    Write-Host "Graph API: Connected" -ForegroundColor Green
} catch {
    Write-Host "Graph API: Connection failed" -ForegroundColor Red
}
```

---

## Escalation Path

If issues persist after troubleshooting:

1. **AI Governance Lead** - Registry policy and metadata standards
2. **Power Platform Admin Team** - Environment and agent management
3. **IT Operations** - Technical setup and automation
4. **Compliance Officer** - Regulatory requirements and retention
5. **Microsoft Support** - Platform bugs or feature issues

---

[Back to Control 1.2](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md)
