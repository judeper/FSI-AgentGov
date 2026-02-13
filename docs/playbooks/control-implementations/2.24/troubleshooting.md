# Troubleshooting: Control 2.24 - Agent Feature Enablement and Restriction Governance

**Last Updated:** February 2026

## Common Issues and Resolutions

---

## Issue 1: PPAC Copilot Governance Page Not Available

**Symptoms:**
- Cannot find "Copilot" or "Governance" section in Power Platform Admin Center
- Left navigation does not show Copilot governance option
- Features menu does not include Copilot Studio controls

**Possible Causes:**
1. Feature has not rolled out to your tenant yet
2. Insufficient permissions (not Power Platform Admin or Entra Global Admin)
3. Tenant licensing does not include Copilot Studio features

**Resolution Steps:**

1. **Check Feature Availability:**
   - Navigate to Microsoft 365 Message Center (admin.microsoft.com → Health → Message center)
   - Search for "Copilot governance" or "Power Platform governance"
   - Verify rollout status and expected availability date for your tenant region
   - Some governance features are rolling out Q1-Q2 2026; your tenant may not have access yet

2. **Verify Permissions:**
   ```powershell
   # Check your admin roles
   Connect-MgGraph -Scopes "User.Read.All", "RoleManagement.Read.Directory"
   $userId = (Get-MgContext).Account
   Get-MgUserMemberOf -UserId $userId | Where-Object {$_.AdditionalProperties.'@odata.type' -like '*DirectoryRole*'}
   ```
   - Confirm you have "Power Platform Administrator" or "Global Administrator" role
   - If missing, request role assignment from Entra Global Admin

3. **Verify Licensing:**
   - Check tenant has appropriate Power Platform licensing (Power Apps Premium or Copilot Studio licenses)
   - Navigate to Microsoft 365 Admin Center → Billing → Licenses
   - Confirm "Power Apps Premium" or "Microsoft Copilot Studio" licenses are assigned

4. **Alternative Configuration Paths:**
   If PPAC Copilot governance page is unavailable, use these alternative methods:
   - **Settings → Features in PPAC:** Some feature toggles are available here
   - **DLP policies:** Use DLP to enforce connector restrictions (Control 1.4)
   - **Environment security roles:** Restrict agent author permissions via security roles
   - **Microsoft Support ticket:** Request assistance enabling specific governance features

**Workaround:**
Use DLP policies as the primary enforcement mechanism until PPAC Copilot governance page becomes available. Document this as a compensating control.

---

## Issue 2: GA Feature Cannot Be Disabled

**Symptoms:**
- Feature toggle in PPAC is grayed out (cannot be changed)
- Feature is marked as "General Availability" (GA) with no disable option
- Documentation states feature can be disabled, but toggle is missing
- Feature continues to appear for agent authors despite attempts to disable

**Possible Causes:**
1. Microsoft has marked the feature as "always on" for GA tenants
2. Feature requires Microsoft Support intervention to disable (intentional design)
3. Feature is disabled through a different configuration path
4. Feature visibility is controlled by licensing, not toggles

**Resolution Steps:**

1. **Check Feature Documentation:**
   - Review Microsoft Learn documentation for the specific feature
   - Look for sections titled "How to disable" or "Opt-out"
   - Some GA features have specific requirements for disablement (e.g., must disable in all environments first, then tenant-wide)

2. **Contact Microsoft Support:**
   - Open a Microsoft Support ticket (portal.azure.com → Help + support)
   - Reference the specific feature name and GA announcement
   - Request confirmation on whether feature can be disabled and process to do so
   - Example: "GA feature 'Generative Actions' cannot be disabled in PPAC; request assistance or confirmation this is by design"

3. **Implement Compensating Controls:**
   If feature cannot be disabled at platform level, implement runtime controls:
   - **DLP policies:** Block connectors used by the feature (e.g., block AI Builder connector to prevent generative actions)
   - **Environment security roles:** Restrict "Create" permissions for agents in Zone 3 environments
   - **Monitoring and alerts:** Use audit logs to detect unauthorized feature usage; alert on violations
   - **Documented policy:** Create organizational policy prohibiting use of feature; include in agent author training
   - **Code reviews:** Manually review agents before production deployment to verify prohibited features are not used

4. **Document as Control Gap:**
   - Add entry to control gap register: "Feature X (GA) cannot be disabled at platform level"
   - Document compensating controls implemented
   - Include in next SOC 2 / ISO audit as "limitation of technology; mitigated by compensating controls"
   - Example entry:
     ```
     Control Gap: Generative Actions cannot be disabled at tenant level (GA feature)
     Compensating Controls:
     - DLP policy blocks AI Builder connector in Zone 3 environments
     - Manual code review required before Zone 3 agent deployment
     - Monitoring alert triggers if generative action is detected in Zone 3 agent
     - Documented policy prohibiting generative actions in Zone 3
     Risk Level: Medium (acceptable with compensating controls)
     Next Review: [Date]
     ```

**Workaround:**
Accept feature is enabled at platform level; enforce restrictions through DLP, security roles, and procedural controls.

---

## Issue 3: Feature Catalog Table Creation Fails

**Symptoms:**
- PowerShell script `Deploy-FeatureCatalog.ps1` fails with error
- Error message: "Access Denied" or "Insufficient Permissions"
- Dataverse table creation times out or hangs

**Possible Causes:**
1. Insufficient permissions in Dataverse environment
2. Environment is managed (production) and requires approval for schema changes
3. Dataverse capacity is exhausted
4. API throttling limits exceeded

**Resolution Steps:**

1. **Check Dataverse Permissions:**
   - Verify you have "System Administrator" security role in the target Dataverse environment
   - Navigate to Power Platform Admin Center → Environments → [Environment] → Settings → Users + permissions → Security roles
   - Confirm your user account is listed with System Administrator role
   - If missing, assign the role through Power Platform Admin Center

2. **Use Default Environment:**
   - Create feature catalog table in the **default environment** (not a production Zone 3 environment)
   - Default environment typically has more permissive permissions
   - After table is created, export as solution and import to other environments if needed

3. **Manual Table Creation (Alternative to PowerShell):**
   - Open Power Apps Maker Portal (make.powerapps.com)
   - Select the target environment
   - Navigate to **Tables** → **+ New table** → **Start from blank**
   - Manually create table with name: `fsi_featurecatalog`
   - Add columns as specified in `Deploy-FeatureCatalog.ps1` script comments
   - This avoids API calls and permission issues

4. **Use Power Platform CLI (Alternative Method):**
   ```bash
   # Install Power Platform CLI if not already installed
   dotnet tool install --global Microsoft.PowerApps.CLI.Tool

   # Authenticate to environment
   pac auth create --url https://contoso.crm.dynamics.com

   # Create table
   pac table create --name fsi_featurecatalog --display-name "FSI Feature Catalog" --description "Tracks feature governance"
   
   # Add columns (example for one column)
   pac column create --table-name fsi_featurecatalog --name fsi_featurename --display-name "Feature Name" --type text --required
   ```

5. **Check Capacity and Throttling:**
   - Navigate to Power Platform Admin Center → Resources → Capacity
   - Verify Dataverse database capacity is not exhausted (must have available storage)
   - If throttling is occurring, wait 1 hour and retry (API limits reset hourly)

**Workaround:**
Use SharePoint list instead of Dataverse table for feature catalog (simpler, no Dataverse permissions required). See Portal Walkthrough Step 8 Option B.

---

## Issue 4: DLP Policy Not Blocking Prohibited Connector

**Symptoms:**
- HTTP connector (or other high-risk connector) is in "Blocked" group in DLP policy
- Agent authors can still add the connector to agents in restricted environments
- Agent with blocked connector saves successfully without errors

**Possible Causes:**
1. DLP policy is not applied to the target environment
2. Environment is excluded from DLP policy scope
3. DLP policy has lower priority than another policy (multiple policies with conflicts)
4. Connector classification has not synchronized yet (can take up to 2 hours)
5. User has "DLP exemption" role or permission

**Resolution Steps:**

1. **Verify DLP Policy Scope:**
   - In Power Platform Admin Center, navigate to **Data policies** → [Select Policy]
   - Click **Edit policy** → Review **Environments** tab
   - Confirm the target environment is included in policy scope
   - If not included, add the environment to policy scope

2. **Check for Multiple DLP Policies:**
   - List all DLP policies in tenant:
     ```powershell
     Add-PowerAppsAccount
     Get-AdminDlpPolicy | Select-Object DisplayName, EnvironmentType, PolicyName
     ```
   - If multiple policies apply to same environment, resolve conflicts:
     - **AllEnvironments policy** applies to all environments (cannot be overridden)
     - **ExceptEnvironments policy** applies to all except specified environments
     - **OnlyEnvironments policy** applies only to specified environments
   - Highest priority: OnlyEnvironments > ExceptEnvironments > AllEnvironments
   - Ensure your Zone 3 policy has correct scope and highest priority

3. **Wait for Policy Synchronization:**
   - DLP policy changes can take up to 2 hours to fully propagate
   - After changing connector classification, wait 2 hours before testing
   - Clear browser cache and sign out/in to Copilot Studio to force policy refresh

4. **Check User Exemptions:**
   - Some users may have "DLP Exemption" permission (rare, but possible)
   - Verify user security role in environment:
     ```powershell
     # Connect to Dataverse
     Import-Module Microsoft.Xrm.Data.PowerShell
     $conn = Connect-CrmOnline -ServerUrl "https://contoso.crm.dynamics.com" -ForceOAuth
     
     # Query user security roles
     Get-CrmRecords -conn $conn -EntityLogicalName systemuserroles -FilterAttribute systemuserid -FilterOperator eq -FilterValue [UserGUID]
     ```
   - If user has "System Administrator" or custom role with "Override DLP" privilege, they bypass DLP policies
   - Remove override privilege or use service accounts without admin roles for testing

5. **Test DLP Enforcement Directly:**
   ```powershell
   # Use Test-DLPEnforcement.ps1 script from PowerShell Setup playbook
   .\Test-DLPEnforcement.ps1
   ```
   - Script will report if DLP policies are correctly configured
   - If script shows connector as "Allowed" but policy shows "Blocked", there is a synchronization or configuration issue

6. **Escalate to Microsoft Support:**
   - If policy is correctly configured but not enforcing, contact Microsoft Support
   - Provide: Policy name, environment ID, connector name, screenshots of policy configuration, test results showing connector is not blocked

**Workaround:**
Implement procedural control: Manual code review of all agents before production deployment to verify prohibited connectors are not used.

---

## Issue 5: Feature Catalog Shows Expiration Alerts but Feature Still Works

**Symptoms:**
- PowerShell report `Get-FeatureComplianceReport.ps1` shows feature with expired exception (Expiration Date in past)
- Feature is still enabled and functional in environment
- No automatic disablement occurred

**Possible Causes:**
1. Feature expiration is not automatically enforced by platform (expected behavior)
2. Manual disablement process was not followed
3. Expiration date is for tracking purposes only (not runtime enforcement)

**Resolution Steps:**

1. **Understand Expiration Date Purpose:**
   - **Important:** Expiration Date in feature catalog is for governance tracking only, not automatic enforcement
   - Microsoft Power Platform does not automatically disable features based on custom Dataverse table data
   - Expiration alerts are intended to trigger manual review and action

2. **Manual Feature Disablement Process:**
   When a feature expires:
   - AI Governance Lead or Compliance Officer reviews the expiration alert
   - Decision: Renew exception (extend expiration date and update change ticket) OR Revoke access (disable feature)
   - If revoking:
     1. Update PPAC feature toggle to disable feature in environment
     2. Update DLP policy to block related connectors (if applicable)
     3. Notify affected users that feature access has expired
     4. Update feature catalog: Set Zone Status to "Prohibited", clear Expiration Date, add note to Justification field
   - If renewing:
     1. Submit new change request for feature enablement extension
     2. Obtain required approvals (Power Platform Admin, AI Governance Lead, Compliance Officer for Zone 3)
     3. Update feature catalog: New Expiration Date, new Change Ticket reference, updated Justification

3. **Implement Automated Expiration Workflow (Optional):**
   - Create Power Automate flow triggered by Expiration Date in feature catalog
   - Flow logic:
     - Trigger: Daily schedule (recurrence)
     - Condition: Check if any features have Expiration Date < Today
     - Action 1: Send email alert to AI Governance Lead with list of expired features
     - Action 2: Create task in change management system: "Review expired feature: [Feature Name]"
     - Action 3: (Optional) Auto-disable feature by calling Power Platform Admin API (requires API connector and custom logic)
   - Deploy flow to default environment

4. **Document Expiration Process:**
   - Add expiration handling procedure to governance documentation:
     ```
     Feature Exception Expiration Process:
     1. Monthly: Generate feature compliance report (includes expiration alerts)
     2. AI Governance Lead reviews alerts for features expiring within 30 days
     3. For each expiring feature:
        a. Contact business owner: "Feature [X] expires on [Date]. Renew or revoke?"
        b. If renew: Submit change request for extension (requires re-approval)
        c. If revoke: Update PPAC and DLP to disable feature; notify users
     4. Update feature catalog with decision
     5. Report expiration actions to Compliance Officer monthly
     ```

**Workaround:**
Manual review of expiration alerts monthly. No automatic enforcement is expected or available in Power Platform.

---

## Issue 6: Agent Author Cannot Request Feature Enablement

**Symptoms:**
- Agent author wants to use a restricted feature but does not know how to request approval
- No clear process communicated to agent authors
- Requests sent via email to admins are informal and lack required documentation

**Possible Causes:**
1. Change management process not documented or communicated
2. Self-service portal for feature requests not available
3. Agent authors lack training on governance procedures

**Resolution Steps:**

1. **Document Feature Request Process:**
   - Create a one-page guide: "How to Request Copilot Studio Feature Enablement"
   - Include:
     - Link to change management system (ServiceNow, Jira, SharePoint form)
     - Step-by-step instructions with screenshots
     - List of required information (Feature Name, Environment, Justification, Risk Assessment)
     - Expected approval timeline (e.g., 3-5 business days for Zone 2, 5-10 days for Zone 3)
     - Contact information for questions (AI Governance Lead email or Teams channel)
   - Publish guide to agent author knowledge base (SharePoint, Confluence, internal wiki)

2. **Create Self-Service Request Form:**
   - Build a Power Apps form or SharePoint form for feature requests:
     - Form fields map directly to change management template
     - Dropdown for Feature Name (populated from feature catalog)
     - Dropdown for Environment (populated from Power Platform environment list)
     - Multi-line text for Business Justification
     - File upload for Risk Assessment document (Zone 3 only)
   - Form submission triggers Power Automate flow:
     - Flow creates change request ticket in change management system
     - Flow sends email to Power Platform Admin and AI Governance Lead
     - Flow sends confirmation email to requester with ticket number

3. **Communicate Process to Agent Authors:**
   - Announce process in organization-wide communication (email, Teams, Yammer)
   - Include link to request form and documentation guide
   - Offer office hours or Q&A session for questions
   - Add feature request process to agent author onboarding training

4. **Embed Request Link in Error Messages:**
   - If possible, customize error messages when agent authors attempt to use restricted features
   - Example: "This feature requires approval. Submit a request here: [Link to Form]"
   - Reduces friction and confusion

5. **Track and Report Request Metrics:**
   - Monthly report: Number of feature requests submitted, approved, rejected, pending
   - Average approval time per zone
   - Most requested features (inform future zone policy adjustments)
   - Share metrics with leadership to demonstrate governance process effectiveness

**Workaround:**
Provide AI Governance Lead email address as interim contact method until formal process is documented. Manually process requests via email until self-service form is available.

---

## Issue 7: Zone Classification Is Unclear for Environment

**Symptoms:**
- Environment exists but governance zone (Zone 1/2/3) is not documented or clear
- Conflicting information: Environment name suggests Zone 2, but usage is Zone 3
- No metadata or tags on environment indicating zone

**Possible Causes:**
1. Environment naming convention does not include zone classification
2. Environment metadata tags not implemented
3. Environment usage changed over time (started as Zone 1, now used for Zone 3 purposes)

**Resolution Steps:**

1. **Establish Environment Naming Convention:**
   - Define naming convention that includes zone classification:
     - Example: `PROD-Z3-CustomerService` (Zone 3 Production for Customer Service)
     - Example: `DEV-Z1-PersonalApps` (Zone 1 Development for Personal Apps)
   - Document naming convention in environment management policy
   - Rename existing environments to match convention (if possible; consider dependencies)

2. **Implement Environment Metadata Tags:**
   - Use Power Platform environment properties to tag zone classification
   - Set custom environment variables:
     ```powershell
     # Example: Set environment variable indicating zone
     # This is a custom solution; Power Platform does not have native zone tagging
     # Alternative: Use environment description field to include zone
     
     Set-AdminPowerAppEnvironment -EnvironmentName [EnvironmentGUID] -EnvironmentDescription "Zone 3 (Enterprise) - Customer Support"
     ```
   - Alternative: Maintain separate inventory (SharePoint list or Dataverse table) mapping Environment ID to Zone
     - Columns: EnvironmentName, EnvironmentID, Zone (Choice: Zone 1/2/3), BusinessOwner, ComplianceContact

3. **Create Environment Registry:**
   - Build Dataverse table or SharePoint list: `fsi_environmentregistry`
   - Fields:
     - EnvironmentName (text)
     - EnvironmentID (text)
     - Zone (choice: Zone 1, Zone 2, Zone 3)
     - EnvironmentType (choice: Production, Development, Test)
     - BusinessOwner (lookup to user)
     - ComplianceContact (lookup to user)
     - DataClassification (choice: Public, Internal, Confidential, Restricted)
     - Notes (multi-line text)
   - Populate with all existing environments
   - Reference this registry in scripts and documentation

4. **Conduct Environment Classification Workshop:**
   - Involve: Power Platform Admin, Business Owners, Compliance Officer, AI Governance Lead
   - Review each environment:
     - What agents are deployed here?
     - Who are the users (internal employees, external customers)?
     - What data is accessed?
     - What are regulatory requirements?
   - Assign zone classification based on criteria:
     - **Zone 1:** Personal productivity, no regulated data, internal users only
     - **Zone 2:** Team collaboration, internal users, organizational data (not customer financial data)
     - **Zone 3:** Customer-facing, regulated data, requires highest governance
   - Document decisions in environment registry

5. **Validate Zone Classification Against Control 2.2:**
   - Control 2.2 (Environment Groups and Tier Classification) defines zone criteria
   - Review Control 2.2 documentation and align environment classifications
   - Ensure feature restrictions in 2.24 align with environment tiers in 2.2

**Workaround:**
Use environment description field (visible in PPAC) to manually document zone classification until formal tagging or registry is implemented.

---

## Issue 8: PowerShell Scripts Fail with Authentication Errors

**Symptoms:**
- PowerShell script execution fails immediately with "Authentication failed" or "Access denied"
- `Connect-CrmOnline` or `Add-PowerAppsAccount` prompts for credentials but then fails
- Multi-factor authentication (MFA) challenges cause scripts to hang or timeout

**Possible Causes:**
1. Account does not have required permissions
2. MFA is required but not supported by authentication method
3. Modern authentication is disabled
4. PowerShell modules are outdated

**Resolution Steps:**

1. **Update PowerShell Modules:**
   ```powershell
   # Update to latest versions
   Update-Module Microsoft.PowerApps.Administration.PowerShell -Force
   Update-Module Microsoft.Xrm.Data.PowerShell -Force
   Update-Module Microsoft.PowerApps.PowerShell -Force
   ```
   - Restart PowerShell console after updates
   - Verify versions:
     ```powershell
     Get-Module Microsoft.PowerApps.Administration.PowerShell -ListAvailable
     Get-Module Microsoft.Xrm.Data.PowerShell -ListAvailable
     ```

2. **Use Interactive Authentication with MFA:**
   - Ensure `-ForceOAuth` parameter is used in connection commands:
     ```powershell
     Connect-CrmOnline -ServerUrl "https://contoso.crm.dynamics.com" -ForceOAuth
     ```
   - `-ForceOAuth` opens a browser window for interactive authentication supporting MFA
   - If browser does not open, check if popup blockers are enabled

3. **Use Service Principal (For Automation):**
   - For unattended scripts (Azure Automation, scheduled tasks), use service principal authentication:
     ```powershell
     # Register app in Entra ID and grant Power Platform API permissions
     $appId = "[Application ID]"
     $clientSecret = "[Client Secret]"
     $tenantId = "[Tenant ID]"
     
     Add-PowerAppsAccount -ApplicationId $appId -ClientSecret $clientSecret -TenantID $tenantId
     ```
   - Grant service principal "Power Platform Administrator" role
   - Document service principal credentials in secure vault (Azure Key Vault)

4. **Check Conditional Access Policies:**
   - Entra Conditional Access policies may block authentication from certain locations or devices
   - Navigate to Entra Admin Center → Protection → Conditional Access
   - Review policies that apply to Power Platform APIs or admin accounts
   - If policy requires compliant device or specific location, run script from compliant device/location
   - Alternative: Exclude service principal from Conditional Access policies (for automation)

5. **Enable Modern Authentication:**
   - Verify modern authentication is enabled in tenant:
   - Navigate to Microsoft 365 Admin Center → Settings → Org settings → Modern authentication
   - Ensure "Enable modern authentication" is toggled on
   - If disabled, enable and wait 24 hours for propagation

6. **Check Account Permissions:**
   ```powershell
   # Verify you have admin roles
   Connect-MgGraph
   Get-MgUserMemberOf -UserId (Get-MgContext).Account | Where-Object {$_.AdditionalProperties.'@odata.type' -like '*DirectoryRole*'}
   ```
   - Confirm "Power Platform Administrator" or "Dynamics 365 Administrator" role
   - For Dataverse operations, confirm "System Administrator" in target environment

**Workaround:**
Run scripts manually from a workstation with interactive authentication instead of automated scheduled execution until service principal authentication is configured.

---

## Issue 9: Feature Compliance Report Shows No Data

**Symptoms:**
- PowerShell script `Get-FeatureComplianceReport.ps1` completes but CSV file is empty or has only headers
- Console output shows: "Retrieved 0 feature records"
- Feature catalog table exists but appears empty

**Possible Causes:**
1. Feature catalog table was not populated with initial data
2. Script is querying wrong environment
3. Data retrieval permissions issue
4. Table name is incorrect (typo in script parameter)

**Resolution Steps:**

1. **Verify Feature Catalog Has Data:**
   - Manually check feature catalog table:
     - Open Power Apps (make.powerapps.com)
     - Navigate to Tables → fsi_featurecatalog → Data
     - Confirm records exist
   - If table is empty, run `Populate-FeatureCatalog.ps1` script to add baseline features

2. **Check Environment URL Parameter:**
   - Verify `-EnvironmentUrl` parameter in script call matches the environment where feature catalog is deployed
   - Get correct URL:
     ```powershell
     # List all environments and their URLs
     Add-PowerAppsAccount
     Get-AdminPowerAppEnvironment | Select-Object DisplayName, EnvironmentName, Properties | Format-Table
     ```
   - Dataverse URL format: `https://[orgname].crm[region].dynamics.com`
   - Re-run script with correct URL

3. **Verify Table Name:**
   - Confirm table logical name is exactly `fsi_featurecatalog` (case-sensitive in some APIs)
   - If table was created with different name, update FetchXML query in script:
     ```xml
     <entity name="fsi_featurecatalog">  <!-- Update this line if table name is different -->
     ```

4. **Check Data Retrieval Permissions:**
   - User running script must have Read permission on fsi_featurecatalog table
   - Verify security role includes Read privilege for custom tables
   - Alternative: Run script with System Administrator account

5. **Test FetchXML Query Manually:**
   - Use XrmToolBox (free tool for Dataverse) to test FetchXML query
   - Install XrmToolBox: https://www.xrmtoolbox.com/
   - Use "FetchXML Builder" plugin to execute the query from `Get-FeatureComplianceReport.ps1`
   - Verify query returns data when executed manually
   - If manual query works but script fails, issue is with PowerShell module or connection

**Workaround:**
Manually export feature catalog data from Power Apps Maker Portal (Tables → fsi_featurecatalog → Data → Export to Excel) until script issue is resolved.

---

## Issue 10: Change Management System Does Not Support Copilot Feature Requests

**Symptoms:**
- Change management system (ServiceNow, Jira, etc.) does not have template or workflow for Copilot Studio feature enablement
- Existing change request types do not fit this use case
- No integration between change management system and Power Platform

**Possible Causes:**
1. Change management system is not configured for Power Platform governance
2. Change management team is not aware of Copilot Studio governance requirements
3. Integration automation (Power Automate → Change System) not implemented

**Resolution Steps:**

1. **Create Custom Change Request Type:**
   - Work with Change Management team to create new request type: "Copilot Studio Feature Enablement"
   - Map required fields from Control 2.24 (Feature Name, Environment, Zone, Justification, Risk Assessment) to change request form
   - Configure approval workflow routing:
     - Zone 1: Power Platform Admin
     - Zone 2: Power Platform Admin → AI Governance Lead
     - Zone 3: Power Platform Admin → AI Governance Lead → Compliance Officer
   - Assign request type to appropriate change category (e.g., "Application Configuration Change")

2. **Use Standard Change Template (Interim):**
   - If custom type cannot be created immediately, use existing "Configuration Change" or "Application Change" template
   - Add Copilot-specific fields in description or notes section:
     ```
     Change Description: Copilot Studio Feature Enablement
     Feature Name: [X]
     Environment: [Y]
     Governance Zone: [Zone 1/2/3]
     Business Justification: [Text]
     Risk Assessment: [Text]
     ```
   - Document interim process in governance handbook

3. **Build Integration with Power Automate:**
   - Create Power Automate flow to integrate Power Platform with change management system:
     - Trigger: Manual button or SharePoint form submission (feature request)
     - Action 1: Create change request in change system via REST API or connector
     - Action 2: Send approval notifications to reviewers
     - Action 3: On approval, update feature catalog in Dataverse
     - Action 4: Notify requester of approval status
   - Most change management systems have REST APIs or Power Automate connectors available

4. **Document Process Without Change System (Temporary):**
   - If change management system cannot be configured in short term, create interim process:
     - Use SharePoint list to track feature requests (columns: Requester, Feature, Environment, Status, Approvers, Approval Date)
     - Manual email approval workflow: Requester → Power Platform Admin → AI Governance Lead → Compliance Officer
     - Update SharePoint list status after each approval stage
     - Migrate to formal change system when available
   - Document this as temporary process with planned migration date

5. **Engage Change Advisory Board (CAB):**
   - Present Copilot Studio governance requirements to CAB
   - Request prioritization of change management system updates to support Power Platform governance
   - Provide business justification: Regulatory compliance (SOX, FINRA, GLBA), risk management, audit trail requirements

**Workaround:**
Use email-based approval with manual tracking in spreadsheet or SharePoint list until change management system is configured. Ensure audit trail is maintained (approval emails saved, decision documentation).

---

## Diagnostic Commands

Use these commands to troubleshoot issues:

```powershell
# Check Power Platform environments
Add-PowerAppsAccount
Get-AdminPowerAppEnvironment | Select-Object DisplayName, EnvironmentName, EnvironmentType | Format-Table

# List DLP policies
Get-AdminDlpPolicy | Select-Object DisplayName, EnvironmentType, PolicyName | Format-Table

# Check connector classifications in DLP policy
$policy = Get-AdminDlpPolicy -PolicyName "[PolicyGUID]"
$policy.ConnectorGroups | ForEach-Object { Write-Host "Classification: $($_.classification)"; $_.connectors | Select-Object id, name }

# Verify user roles in Entra ID
Connect-MgGraph
Get-MgUserMemberOf -UserId (Get-MgContext).Account | Select-Object @{N='RoleName';E={$_.AdditionalProperties.displayName}}

# Test Dataverse connection
Import-Module Microsoft.Xrm.Data.PowerShell
$conn = Connect-CrmOnline -ServerUrl "https://contoso.crm.dynamics.com" -ForceOAuth
$conn.IsReady  # Should return True

# Query feature catalog records
Get-CrmRecords -conn $conn -EntityLogicalName fsi_featurecatalog -Fields fsi_featurename,fsi_zone3status

# Check PowerShell module versions
Get-Module Microsoft.PowerApps.Administration.PowerShell -ListAvailable
Get-Module Microsoft.Xrm.Data.PowerShell -ListAvailable
```

---

## Escalation Path

If issues cannot be resolved with troubleshooting steps:

1. **Power Platform Admin → Microsoft Support:**
   - Issues with PPAC feature toggles, DLP policies, API limits
   - Open ticket at portal.azure.com → Help + support → New support request
   - Select "Power Platform" or "Copilot Studio" as service

2. **AI Governance Lead → Compliance Officer:**
   - Issues requiring policy decisions (e.g., cannot disable GA feature, need compensating controls)
   - Document issue, proposed compensating controls, residual risk
   - Obtain approval for workaround from Compliance Officer

3. **Change Management Team → IT Leadership:**
   - Issues with change management system configuration or integration
   - Escalate if CAB does not prioritize Copilot governance requirements
   - Provide business case: Regulatory risk, audit findings, compliance obligations

---

## Additional Resources

- [Microsoft Support: Power Platform](https://learn.microsoft.com/en-us/troubleshoot/power-platform/)
- [Power Platform Community Forums](https://powerusers.microsoft.com/t5/Power-Platform-Community/ct-p/PowerPlatform)
- [Microsoft Learn: Troubleshooting Power Platform](https://learn.microsoft.com/en-us/troubleshoot/power-platform/administration/welcome-administration)
- [XrmToolBox (Dataverse debugging)](https://www.xrmtoolbox.com/)

---

[Back to Control 2.24](../../../controls/pillar-2-management/2.24-agent-feature-enablement-and-restriction-governance.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md)
