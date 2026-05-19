# Troubleshooting: Control 3.11 - Centralized Agent Inventory Enforcement

**Last Updated:** April 2026
**Troubleshooting Level:** Control Implementation

---

## Common Issues and Resolutions

### Issue 1: Inventory Page Not Visible in PPAC

**Symptoms:**
- The unified **Manage > Inventory** node does not appear in PPAC navigation
- Error message: "This feature is not available in your tenant"
- Agent rows are missing even though agents exist in environments

**Root Causes:**
1. User does not hold a tenant-wide admin role (Power Platform Admin or Dynamics 365 Admin)
2. Tenant region has not yet received the GA rollout (some sovereign clouds and slow rings lag)
3. Browser cache is showing stale navigation

**Resolution Steps:**

1. **Verify Role Assignment:**
   - Navigate to Entra ID → Users → [Your User] → Assigned roles
   - Confirm "Power Platform Admin" or "Entra Global Admin" role is assigned (the role catalog also accepts "AI Administrator" for Copilot/agent settings, but the Inventory page requires a Power Platform tenant-admin role today)
   - Wait 15 minutes for role propagation if recently assigned

2. **Check Rollout in Message Center:**
   - Navigate to Microsoft 365 Admin Center → Health → Message Center
   - Search for "MC1223778" (Power Platform Inventory GA) and confirm rollout has reached your tenant

3. **Hard-refresh the portal:** Ctrl+F5 or open PPAC in a private window

4. **Verify Tenant Licensing:**
   - Navigate to Microsoft 365 Admin Center → Billing → Licenses
   - Confirm the tenant has Power Apps or Microsoft Copilot Studio licensing assigned

5. **Contact Microsoft Support:**
   - If the page should be available but is not visible, open a support case
   - Reference: "Power Platform Inventory page not visible (MC1223778, GA Feb 9 2026)"
   - Provide tenant ID and user principal name

**Workaround (Compensating Control):**

While support investigates, use PowerShell-based discovery (Desktop / PS 5.1):

```powershell
# Edition guard
if ($PSVersionTable.PSEdition -ne 'Desktop') {
    throw "Requires Windows PowerShell 5.1 (Desktop) for Microsoft.PowerApps.Administration.PowerShell."
}

$environments = Get-AdminPowerAppEnvironment
$inventory = @()

foreach ($env in $environments) {
    $agents = Get-AdminPowerAppCopilotStudioAgent -EnvironmentName $env.EnvironmentName -ErrorAction SilentlyContinue
    $inventory += $agents | Select-Object DisplayName, Owner, @{N='Environment';E={$env.DisplayName}}, CreatedTime, LastModifiedTime
}

$inventory | Export-Csv -Path "ManualAgentInventory_$(Get-Date -Format 'yyyyMMdd').csv" -NoTypeInformation
```

---

### Issue 2: PowerShell Script Fails with "Access Denied" or "Insufficient Permissions"

**Symptoms:**
- PowerShell scripts fail with error: "Access denied to resource"
- Error: "Insufficient permissions to perform this operation"
- Script cannot retrieve agents from environments

**Root Causes:**
1. User executing script does not have Power Platform Admin role
2. Service principal lacks required API permissions
3. Execution policy blocks script execution

**Resolution Steps:**

1. **Verify Role Assignment:**
   ```powershell
   # Check if user has admin role
   Add-PowerAppsAccount
   Get-AdminPowerAppEnvironment | Select-Object -First 1
   # If this fails, role is missing
   ```

2. **Grant Power Platform Admin Role:**
   - Navigate to Entra ID → Roles and administrators
   - Search for "Power Platform Administrator"
   - Click → Add assignments
   - Add your user account
   - Wait 15 minutes for propagation

3. **Check Execution Policy:**
   ```powershell
   # Check current policy
   Get-ExecutionPolicy
   
   # If Restricted, change to RemoteSigned
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

4. **Verify Module Installation:**
   ```powershell
   # Confirm modules are installed
   Get-Module -ListAvailable Microsoft.PowerApps.Administration.PowerShell
   Get-Module -ListAvailable Microsoft.Graph
   
   # If missing, reinstall
   Install-Module -Name Microsoft.PowerApps.Administration.PowerShell -Force
   Install-Module -Name Microsoft.Graph -Force
   ```

5. **Use Different Account:**
   - If unable to grant admin role to your user, use a dedicated service account with Power Platform Admin role
   - Configure scheduled tasks with service account credentials

---

### Issue 3: Power Automate Flow Fails to Retrieve Inventory Data

**Symptoms:**
- Flow run history shows failure at the inventory retrieval step
- Error: "HTTP 401 Unauthorized" or "HTTP 403 Forbidden"
- Flow cannot read agents from PPAC

**Root Causes:**
1. The flow still uses the obsolete placeholder URL `api.powerplatform.com/agentInventory/...` instead of the **Power Platform for Admins V2** connector
2. The connection used by the flow does not hold a tenant-wide admin role
3. Service principal or managed identity is not granted the connector's required permissions

**Resolution Steps:**

1. **Migrate to the Power Platform for Admins V2 connector (preferred fix):**
   - In Power Automate, replace the HTTP action with **Power Platform for Admins V2 → List as Admin Inventory Resources**
   - The connector inherits admin permissions from the connection user — no custom token handling
   - The connector is GA and is the supported integration path

2. **Verify Connection Permissions:**
   - Open the flow → Connections
   - Confirm the connection is owned by a Power Platform Admin (or service principal with that role)
   - If using a service principal, grant the Power Platform Admin role to the SP and re-create the connection

3. **Use Alternative Data Source (offline workaround):**

   Where the connector is not yet enabled (some sovereign clouds), fall back to file-based intake:

   - **Step 1:** Export PPAC Inventory to Excel manually (or via the PowerShell script in `powershell-setup.md`)
   - **Step 2:** Upload to a SharePoint document library
   - **Step 3:** Have the flow read the file from SharePoint and parse rows

   ```text
   Trigger: Recurrence (Daily)
   Action 1: SharePoint - Get file content (AgentInventory.xlsx)
   Action 2: Excel Online - List rows present in a table
   Action 3: Filter array (incomplete metadata)
   Action 4: Post adaptive card to Teams
   ```

4. **Use Dataverse as Intermediate Storage:**

   For tenants standardizing on Dataverse-backed governance:
   - Run the PowerShell script daily to populate a Dataverse table with inventory data
   - The Power Automate flow queries the Dataverse table instead of the connector
   - See PowerShell Setup Script 1 for the population pattern

---

### Issue 4: Orphaned Agent Detection Script Returns Empty Results

**Symptoms:**
- `Detect-OrphanedAgents.ps1` completes successfully but reports zero orphaned agents
- Script output: "Total Orphaned Agents: 0"
- Known departed users exist but are not detected

**Root Causes:**
1. Inventory report used by script does not have accurate owner status
2. Microsoft Graph connection failed to validate users
3. Staleness threshold is too high (e.g., >365 days but no agents that old)
4. Owner email format mismatch (UPN vs. email address)

**Resolution Steps:**

1. **Verify Owner Status in Inventory Report:**
   - Open the inventory report CSV in Excel
   - Check "OwnerStatus" column — should show "Active", "Departed", "Invalid", or "Missing"
   - If all show "Unknown", Graph connection failed during inventory generation

2. **Re-run Inventory Generation with Graph Connection:**
   ```powershell
   # Ensure Graph module is installed
   Install-Module Microsoft.Graph -Force
   
   # Connect to Graph explicitly before running inventory
   Connect-MgGraph -Scopes "User.Read.All"
   
   # Run inventory script
   .\Get-AgentInventoryReport.ps1 -OutputPath "C:\Reports"
   
   # Verify OwnerStatus is populated
   Import-Csv "C:\Reports\AgentInventoryReport_*.csv" | Select-Object AgentName, Owner, OwnerStatus
   ```

3. **Lower Staleness Threshold for Testing:**
   ```powershell
   # Test with 180-day threshold instead of 365
   .\Detect-OrphanedAgents.ps1 -InventoryReportPath "C:\Reports\AgentInventory.csv" -StalenessThresholdDays 180
   ```

4. **Manually Verify Departed Users:**
   ```powershell
   # Get list of agent owners
   $inventory = Import-Csv "C:\Reports\AgentInventory.csv"
   $owners = $inventory | Select-Object -ExpandProperty Owner -Unique
   
   # Check each owner in Entra ID
   Connect-MgGraph -Scopes "User.Read.All"
   foreach ($owner in $owners) {
       try {
           $user = Get-MgUser -UserId $owner -ErrorAction SilentlyContinue
           if ($user) {
               Write-Host "$owner - Active" -ForegroundColor Green
           } else {
               Write-Host "$owner - NOT FOUND (Departed)" -ForegroundColor Red
           }
       } catch {
           Write-Host "$owner - ERROR: $_" -ForegroundColor Yellow
       }
   }
   ```

5. **Check Owner Email Format:**
   - Some agents may use email address while others use UPN
   - Verify graph query handles both formats

---

### Issue 5: Teams Notifications Not Delivered

**Symptoms:**
- PowerShell script or Power Automate flow completes successfully
- No error messages related to Teams notification
- Teams channel does not receive expected notification

**Root Causes:**
1. Teams webhook URL is incorrect or expired
2. Adaptive card JSON is malformed
3. Flow bot does not have permission to post to channel
4. Webhook was deleted or disabled by Teams admin

**Resolution Steps:**

1. **Verify Webhook URL:**
   - Navigate to Teams → [Governance Team] → [Agent Governance Alerts channel]
   - Click ⋯ (More options) → Connectors → Incoming Webhook
   - Verify webhook exists and is enabled
   - Copy webhook URL and compare to URL in script/flow

2. **Test Webhook Directly:**
   > **NOTE:** Office 365 Connectors retired 2025-12-31; use Teams Workflows webhooks (`https://prod-NN.<region>.logic.azure.com:443/workflows/...`) with an Adaptive Card v1.5 payload.

   ```powershell
   # Test webhook with simple message
   $webhookUrl = "https://prod-NN.westus.logic.azure.com:443/workflows/<workflow-id>/triggers/manual/paths/invoke?..."
   $body = @{
       text = "Test notification from PowerShell"
   } | ConvertTo-Json
   
   Invoke-RestMethod -Uri $webhookUrl -Method Post -Body $body -ContentType 'application/json'
   ```
   
   Expected result: Message appears in Teams channel within 30 seconds

3. **Validate Adaptive Card JSON:**
   - Copy adaptive card JSON from script
   - Test in Adaptive Cards Designer: https://adaptivecards.io/designer/
   - Verify JSON is valid and renders correctly
   - Common issues: Missing commas, unclosed brackets, invalid schema version

4. **Recreate Webhook:**
   - If webhook is not working, delete and recreate:
     - Teams → Channel → ⋯ → Connectors → Incoming Webhook
     - Click "Remove" on existing webhook
     - Click "Configure" to create new webhook
     - Name: "Agent Inventory Alerts"
     - Upload icon (optional)
     - Copy new webhook URL
     - Update scripts/flows with new URL

5. **Check Flow Bot Permissions (Power Automate):**
   - In Power Automate, check flow run history
   - If error "Flow bot does not have access to the channel":
     - Add Flow bot as a member of the Teams team
     - Grant posting permissions in channel settings

---

### Issue 6: Pre-Publication Checklist Not Enforced

**Symptoms:**
- Agents are published without complete metadata
- Pre-publication checklist is documented but not enforced
- No blocking mechanism prevents incomplete agents from going to production

**Root Causes:**
1. Approval workflow is not configured or agents bypass approval
2. Checklist is manual but not integrated with approval gates
3. No technical enforcement mechanism (DLP, security roles, etc.)

**Resolution Steps:**

**Immediate Mitigation (Manual Process):**

1. **Implement Manual Review Gate:**
   - Require all Zone 2/3 agents to have change management ticket before approval
   - In change request form, include pre-publication checklist as required fields
   - Power Platform Admin reviews checklist before granting sharing permissions

2. **Communicate Policy to Agent Authors:**
   - Send organization-wide email explaining new pre-publication requirements
   - Provide link to checklist document and approval process
   - Include examples of compliant vs. non-compliant agents

**Long-Term Solution (Automated Enforcement):**

3. **Implement Change Management Integration:**
   - Configure ServiceNow/Jira workflow with agent registration request type
   - Make all checklist items required fields (cannot submit without completing)
   - Approval workflow routes to Power Platform Admin → AI Governance Lead → Compliance Officer (Zone 3)
   - Agents cannot be shared until change request is approved

4. **Use DLP to Block Unapproved Sharing:**
   - Create DLP policy for Zone 3 environments
   - Block "Copilot Studio for Microsoft Teams" connector until agent is approved
   - After approval, grant specific agent exemption in DLP policy
   - Requires manual DLP policy updates per agent (labor-intensive but high assurance)

5. **Implement Custom Approval Workflow in Power Automate:**
   - Flow triggered when agent is created (if webhook available)
   - Flow checks if agent metadata is complete (query inventory or metadata table)
   - If incomplete, flow sends notification to author: "Complete metadata before requesting publication"
   - If complete, flow generates approval request and routes to approvers
   - After approval, flow updates metadata with approval date and approver name

---

### Issue 7: Inventory Completeness Metrics Do Not Improve Over Time

**Symptoms:**
- Compliance rate remains stagnant or declines month-over-month
- Remediation efforts do not result in measurable improvement
- Same agents appear in non-compliant reports repeatedly

**Root Causes:**
1. Remediation actions are not being executed (low follow-through)
2. New agents with incomplete metadata are created faster than remediation occurs
3. No accountability or ownership for remediation
4. Metadata requirements are unclear or too burdensome for agent authors

**Resolution Steps:**

1. **Establish Remediation Accountability:**
   - Assign specific governance team member as "Remediation Owner"
   - Weekly review of orphaned/incomplete agent reports
   - Create JIRA/ServiceNow tickets for each remediation item with due dates
   - Track ticket completion rate as KPI

2. **Implement SLA Tracking and Escalation:**
   - Add SLA fields to remediation reports (days since detection, SLA breach status)
   - Automate escalation: If Zone 3 agent exceeds 7-day SLA, escalate to AI Governance Lead
   - Monthly governance meeting: Review SLA compliance and remediation velocity

3. **Use a Phased Metadata Approach:**
   - If metadata collection is causing adoption friction, consider a phased approach: start with mandatory fields (name, owner, zone) and add supplementary fields (description, data classification, regulatory scope) in subsequent phases
   - Do NOT remove mandatory governance fields — these are required for Control 3.11 enforcement
   - Example: Phase 1 requires name, owner, and zone classification; Phase 2 adds description, data classification, and regulatory scope after teams are comfortable with the process

4. **Provide Agent Author Training:**
   - Host monthly training session: "How to Complete Agent Metadata"
   - Record training and make available on-demand
   - Include in onboarding for new Copilot Studio users
   - Provide quick reference guide or checklist template

5. **Block New Agent Creation Until Remediation Backlog Clears:**
   - Temporary measure: Suspend new Zone 3 agent approvals until non-compliance rate drops below 10%
   - Communicate: "We are prioritizing metadata completeness for existing agents before onboarding new agents"
   - Resume normal approvals once backlog is remediated

6. **Celebrate Wins and Progress:**
   - Recognize teams/individuals who achieve 100% metadata completeness
   - Share success stories in governance team meetings
   - Visualize progress with trend charts: "Compliance rate improved from 65% to 85% this quarter"

---

### Issue 8: Decommissioning Process Results in Data Loss

**Symptoms:**
- Decommissioned agent metadata is not properly archived
- Unable to retrieve agent configuration after decommissioning
- Audit trail gaps for decommissioned agents

**Root Causes:**
1. Metadata export step was skipped or failed
2. Archived metadata was stored in temporary location and deleted
3. Agent configuration export did not capture all necessary details
4. Retention policy automatically deleted archived metadata

**Resolution Steps:**

1. **Verify Metadata Archive Location:**
   - Confirm SharePoint library or compliance repository exists: "Decommissioned Agents Archive"
   - Check folder structure: `YYYY/MM/AgentName_DecommissionedYYYYMMDD/`
   - Verify file retention policy is set to 7+ years (FSI requirement)

2. **Recover Metadata from Power Platform:**
   - If agent was recently decommissioned, metadata may still be in environment
   - Use PowerShell to query decommissioned agents:
     ```powershell
     Get-AdminPowerAppCopilotStudioAgent -EnvironmentName [EnvironmentId] | Where-Object { $_.Internal.properties.statecode -eq 1 }
     ```
   - Export metadata to JSON and archive

3. **Implement Automated Archival:**
   - Create Power Automate flow: "Agent Decommissioning Metadata Archive"
   - Triggered when agent status changes to "Decommissioned"
   - Flow exports metadata to SharePoint with timestamp and original owner info
   - Flow sends confirmation email to governance team with archive location

4. **Enhance Decommissioning Workflow:**
   - Update decommissioning checklist to include explicit verification step:
     - [ ] Metadata exported and saved to archive location
     - [ ] Agent configuration exported (YAML or JSON)
     - [ ] Archive location path documented in change ticket
     - [ ] Compliance Officer verifies archive before final deletion approval

5. **Test Archive Retrieval:**
   - Quarterly, randomly select 3 decommissioned agents
   - Attempt to retrieve archived metadata
   - Verify all required fields are present and readable
   - Document test results as part of compliance evidence

---

### Issue 9: Zone Mappings Are Incorrect or Outdated

**Symptoms:**
- Agents are classified to wrong governance zone
- Zone mapping file does not include new environments
- Inventory reports show many agents with "Unknown" zone classification

**Root Causes:**
1. Zone mapping CSV file is not maintained when new environments are created
2. Environment IDs in mapping file do not match actual environment IDs
3. Environments are renamed but mapping file is not updated

**Resolution Steps:**

1. **Regenerate Zone Mapping File:**
   ```powershell
   # Get all environments with IDs
   $environments = Get-AdminPowerAppEnvironment | Select-Object EnvironmentName, DisplayName
   
   # Export to CSV for manual zone assignment
   $environments | Export-Csv -Path "C:\Config\environments_for_zone_mapping.csv" -NoTypeInformation
   
   # Manually edit CSV and add ZoneName column (Zone 1, Zone 2, Zone 3)
   # Save as zone-mappings.csv
   ```

2. **Establish Zone Mapping Maintenance Process:**
   - When new environment is created, immediately add to zone mapping file
   - Power Platform Admin responsible for zone mapping updates
   - Quarterly review: Audit all environments and verify zone classifications are accurate
   - Version control zone mapping file in Git or SharePoint with version history

3. **Validate Zone Mappings:**
   ```powershell
   # Load zone mappings
   $zoneMappings = Import-Csv "C:\Config\zone-mappings.csv"
   
   # Get all environments
   $environments = Get-AdminPowerAppEnvironment
   
   # Check for unmapped environments
   foreach ($env in $environments) {
       $mapping = $zoneMappings | Where-Object { $_.EnvironmentId -eq $env.EnvironmentName }
       if (-not $mapping) {
           Write-Host "UNMAPPED: $($env.DisplayName) ($($env.EnvironmentName))" -ForegroundColor Red
       }
   }
   ```

4. **Use Environment Naming Convention:**
   - Include zone indicator in environment display name: "PROD-Z3-Sales", "DEV-Z1-Personal"
   - Update zone mapping script to auto-detect zone from environment name:
     ```powershell
     $zone = if ($env.DisplayName -match "-Z(\d)-") { "Zone $($Matches[1])" } else { "Unknown" }
     ```

---

### Issue 10: Script Performance Issues with Large Inventories

**Symptoms:**
- PowerShell script takes >30 minutes to complete
- Script consumes excessive memory (>2GB)
- Script times out before completing all environments

**Root Causes:**
1. Large number of environments (100+)
2. Many agents per environment (>50 agents)
3. Inefficient API calls (e.g., validating each owner individually against Graph)
4. Script is not optimized for parallelization

**Resolution Steps:**

1. **Optimize Script with Parallel Processing:**
   ```powershell
   # Use ForEach-Object -Parallel (PowerShell 7+)
   $environments | ForEach-Object -Parallel {
       $env = $_
       $agents = Get-AdminPowerAppCopilotStudioAgent -EnvironmentName $env.EnvironmentName
       # Process agents...
   } -ThrottleLimit 5
   ```

2. **Batch Graph API Calls:**
   ```powershell
   # Instead of querying Graph for each owner individually, get all users once
   $allUsers = Get-MgUser -All
   
   # Create lookup hashtable
   $userLookup = @{}
   foreach ($user in $allUsers) {
       $userLookup[$user.UserPrincipalName] = $user
   }
   
   # Validate owners against lookup table (no API calls)
   foreach ($agent in $agents) {
       $ownerValid = $userLookup.ContainsKey($agent.Owner.email)
   }
   ```

3. **Implement Incremental Inventory Updates:**
   - Instead of full inventory scan daily, detect only changes
   - Store previous inventory in Dataverse or database
   - Query only agents modified since last run (`$filter=lastmodifiedon gt [timestamp]`)
   - Merge incremental changes with previous inventory

4. **Run Script in Azure Automation:**
   - Migrate script to Azure Automation Runbook
   - Benefit from Azure-hosted execution (better network connectivity to APIs)
   - Use Hybrid Runbook Worker if on-premises connectivity required

5. **Split Script by Environment:**
   - For very large tenants, split execution:
     - Script 1: Environments 1-50
     - Script 2: Environments 51-100
     - Run in parallel or staggered schedule
   - Merge results afterward

---

## Diagnostic Commands

### Check Inventory Connector Availability

The Power Platform Inventory page and the **Power Platform for Admins V2** connector are the supported integration surfaces (GA Feb 9, 2026 / MC1223778). There is no separate `api.powerplatform.com/agentInventory` endpoint to call — earlier preview guidance that referenced one is obsolete. To verify access, build a one-step Power Automate flow with **Power Platform for Admins V2 → List as Admin Inventory Resources** and run it; success indicates the connector is reachable from your tenant.

### Validate PowerShell Module Versions

```powershell
# Check installed module versions
Get-Module -ListAvailable | Where-Object { $_.Name -like "*PowerApps*" -or $_.Name -like "*Graph*" } | Select-Object Name, Version
```

### Test Power Platform Connectivity

```powershell
# Verify Power Platform connection
Add-PowerAppsAccount
Get-AdminPowerAppEnvironment | Select-Object -First 1 | Format-List

# If successful, connection is working
# If error, check credentials and role assignment
```

### Test Microsoft Graph Connectivity

```powershell
# Verify Graph connection
Connect-MgGraph -Scopes "User.Read.All"
Get-MgUser -UserId "test@contoso.com"

# If successful, Graph connection is working
# If error, check permissions and authentication
```

---

## Error Code Reference

| Error Code | Description | Resolution |
|------------|-------------|------------|
| `HTTP 401` | Unauthorized - Authentication failed | Re-authenticate with `Add-PowerAppsAccount` or `Connect-MgGraph` |
| `HTTP 403` | Forbidden - Insufficient permissions | Grant Power Platform Admin role or required API permissions |
| `HTTP 404` | Not Found - Resource does not exist | Verify environment ID, agent ID, or API endpoint is correct |
| `HTTP 429` | Too Many Requests - Rate limit exceeded | Implement exponential backoff or reduce API call frequency |
| `HTTP 500` | Internal Server Error - Microsoft service issue | Wait and retry; if persistent, open support case |
| `PSInvalidOperationException` | PowerShell operation failed | Check syntax, cmdlet name, and module version |
| `ModuleNotFoundError` | PowerShell module not installed | Run `Install-Module` for required module |

---

## Support Escalation

If issues persist after troubleshooting:

1. **Internal Escalation:**
   - Escalate to Power Platform Admin team
   - Escalate to Entra ID Admin team (for role/permission issues)
   - Escalate to Security Operations (for DLP or conditional access issues)

2. **Microsoft Support:**
   - Open support case via M365 Admin Center → Support → New service request
   - Severity: Sev B (if impacting governance, not production outage)
   - Provide: Tenant ID, user ID, error messages, script version, troubleshooting steps attempted
   - Reference: Control 3.11 - Centralized Agent Inventory Enforcement

3. **Community Resources:**
   - Power Platform Community Forums: https://powerusers.microsoft.com/
   - Microsoft Tech Community: https://techcommunity.microsoft.com/t5/microsoft-365/ct-p/microsoft365
   - Stack Overflow: Tag `power-platform`, `copilot-studio`, `microsoft-graph`

---

## Known Limitations

As of April 2026:

1. **Inventory granularity:** Power Platform Inventory is GA but exposes only tenant-wide admin access; no read-only or environment-scoped admin variant exists yet
2. **Zone classification:** Not native to PPAC; supplied by zone-mapping CSV or naming convention
3. **Real-time enforcement:** Native unmanaged-agent blocking remains on the roadmap; today, use DLP and security roles as compensating controls (until Agent 365 GA on May 1, 2026 brings policy-based quarantine)
4. **Cross-platform discovery:** Microsoft Foundry agents may not be fully represented in PPAC; Agent 365 GA will unify these sources
5. **Metadata extensibility:** Cannot add custom metadata fields to the native Inventory schema — extend via Dataverse

Monitor Microsoft 365 Roadmap and Message Center for updates that address these limitations.

---

[Back to Control 3.11](../../../controls/pillar-3-reporting/3.11-centralized-agent-inventory-enforcement.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md)

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
