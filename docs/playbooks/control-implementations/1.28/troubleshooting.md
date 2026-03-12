# Troubleshooting: Control 1.28 - Policy-Based Agent Publishing Restrictions

**Last Updated:** February 2026
**Support Level:** L2/L3 Technical Support

## Overview

This playbook provides troubleshooting guidance for common issues related to policy-based agent publishing restrictions, DLP enforcement, approval workflows, and security scan failures.

---

## Issue 1: Agent Publishing Blocked by DLP Violation

### Symptoms
- Agent cannot be published due to DLP policy violation
- Security scan shows red error indicator with DLP connector violation
- Error message: "This agent cannot be published due to DLP policy violations"

### Root Causes
- Agent uses connectors classified as "Blocked" in the environment's DLP policy
- Agent uses connectors in "Non-Business" group that conflict with "Business" connectors
- DLP policy was recently updated and the agent now violates new restrictions

### Diagnostic Steps

1. **Identify the violating connector:**
   ```powershell
   # NOTE: No native Test-PowerAppChatBotDlpCompliance cmdlet exists.
   # Instead, review DLP policies covering Copilot Studio connectors:
   $env = "YOUR_ENVIRONMENT_ID"
   Get-AdminDlpPolicy | Where-Object {
       $_.Environments -contains $env
   } | Select-Object DisplayName, PolicyName
   # Then cross-reference agent connector usage in Power Platform Admin Center.
   ```

2. **Review DLP policy for the environment:**
   - Open Power Platform Admin Center → Policies → Data policies
   - Find the policy assigned to the environment
   - Review connector classifications (Business/Non-Business/Blocked)

3. **Check agent connector usage:**
   - Open Copilot Studio → Agent → Topics
   - Review each topic for connector usage
   - Identify topics using the violating connector

### Resolution Options

**Option 1: Remove or Replace Blocked Connector**
1. Open the agent in Copilot Studio
2. Navigate to topics using the blocked connector
3. Either:
   - Remove the connector action entirely
   - Replace with an approved connector from the Business group
4. Save changes and re-attempt publishing

**Option 2: Request DLP Policy Exception (Zone 1 Only)**
1. Document business justification for connector usage
2. Submit request to Power Platform Admin
3. Admin reviews and optionally adds connector to "Business" group
4. Re-attempt publishing after policy update

**Option 3: Reclassify Connector in DLP Policy (Admin)**
1. Open Power Platform Admin Center → Policies → Data policies
2. Edit the relevant DLP policy
3. Move the connector from "Blocked" to "Business" group
4. Save policy changes
5. Notify agent author to re-attempt publishing

### Prevention
- Review DLP policy requirements before building agents
- Use only approved connectors listed in zone-specific connector catalogs
- Test agents in development environment before promoting to higher zones

---

## Issue 2: Published Agent Blocked from Updates (February 2025 Enforcement)

### Symptoms
- Agent was previously published successfully
- Attempting to publish an update shows DLP violation error
- Error message: "This published agent has DLP violations and cannot be updated"
- Agent remains in previous published version

### Root Causes
- DLP policy was updated after agent was published
- A connector the agent uses was reclassified from "Business" to "Blocked"
- No exemption exists for published agents (February 2025 enforcement change)

### Diagnostic Steps

1. **Check when agent was published vs. DLP policy last updated:**
   ```powershell
   # Get agent last modified date (use Admin variant for cross-tenant visibility)
   Get-AdminPowerAppChatbot -EnvironmentName $env -ChatBotName $agent | Select-Object LastModifiedTime
   
   # Get DLP policy last modified date
   Get-AdminDlpPolicy | Where-Object { $_.Environments -contains $env } | Select-Object LastModifiedTime
   ```

2. **Compare agent connector usage to current DLP policy:**
   - List all connectors used in agent topics
   - Compare to current DLP policy connector classifications
   - Identify which connector was reclassified

### Resolution Options

**Option 1: Reconfigure Agent to Use Approved Connectors**
1. Identify the violating connector from security scan results
2. Open agent in Copilot Studio
3. Reconfigure topics to use approved connectors
4. Test agent functionality with new connector
5. Publish updated agent

**Option 2: Request Temporary DLP Exception (Zone 1/Zone 2)**
1. Document the impact of the DLP policy change
2. Submit exception request to Power Platform Admin and Compliance Officer
3. Admin temporarily reclassifies connector to "Business" group
4. Update agent to remove dependency on connector
5. Re-publish agent with approved connectors only
6. Admin reverts DLP policy to original classification

**Option 3: Roll Back DLP Policy Change (Admin)**
1. Review business justification for DLP policy change
2. If change was unintentional, revert connector classification
3. If change was intentional, work with agent authors to reconfigure agents
4. Document affected agents and remediation timeline

### Prevention
- Maintain an inventory of published agents and their connector dependencies
- Test DLP policy changes in development environment before applying to production
- Provide advance notice to agent authors before DLP policy changes
- Run compliance audit before and after DLP policy updates

---

## Issue 3: Security Scan Fails to Trigger Before Publishing

### Symptoms
- Clicking "Publish" does not show security scan results
- Agent publishes without DLP validation
- No security warnings or errors displayed

### Root Causes
- Security scan feature not enabled in tenant (rare)
- Browser caching issue preventing UI update
- Agent is in an older environment not yet updated with February 2026 security features

### Diagnostic Steps

1. **Check tenant feature rollout status:**
   - Open Microsoft 365 Admin Center → Health → Service health
   - Search for "Copilot Studio" or "Chatbot" updates
   - Check for recent rollouts related to security scanning

2. **Verify environment version:**
   ```powershell
   Get-AdminPowerAppEnvironment -EnvironmentName $env | Select-Object EnvironmentName, Version
   ```

3. **Test with browser cache cleared:**
   - Clear browser cache and cookies
   - Log out and log back into Copilot Studio
   - Re-attempt publishing

### Resolution

**If security scan is not available:**
1. Manually verify DLP compliance before publishing:
   - Review agent topics for connector usage
   - Compare to DLP policy connector classifications
   - Verify no blocked channels are configured
2. Run PowerShell compliance check:
   ```powershell
   # NOTE: No native Test-PowerAppChatBotDlpCompliance cmdlet exists.
   # Review DLP policies for the environment and cross-reference with agent connector usage.
   Get-AdminDlpPolicy | Select-Object DisplayName, PolicyName
   ```
3. Contact Microsoft Support if feature is expected but not available

**If browser issue:**
1. Clear browser cache: Ctrl+Shift+Delete (Windows) or Cmd+Shift+Delete (Mac)
2. Try alternate browser (Edge, Chrome, Firefox)
3. Disable browser extensions temporarily
4. Use InPrivate/Incognito mode

### Prevention
- Monitor Microsoft 365 Message Center for Copilot Studio feature rollouts
- Test in multiple browsers during publishing workflow validation
- Document expected security scan behavior for agent authors

---

## Issue 4: Approval Workflow Not Triggering (Zone 2+)

### Symptoms
- Agent publishes immediately without approval request
- No approval notification sent to Power Platform Admin
- "Submit for approval" button not displayed

### Root Causes
- Approval workflow not enabled in environment settings
- User has Power Platform Admin role (bypasses approval)
- Environment is classified as Zone 1 (approval not required)

### Diagnostic Steps

1. **Check environment approval settings:**
   - Open Power Platform Admin Center → Environments → [Environment] → Settings
   - Navigate to Features → Copilot and Power Apps
   - Verify "Require approval for new chatbots" is enabled

2. **Check user role:**
   ```powershell
   # Get user's role assignments in environment
   Get-AdminPowerAppRoleAssignment -EnvironmentName $env -PrincipalDisplayName "User Name"
   ```

3. **Verify environment zone classification:**
   - Confirm environment is designated as Zone 2 or Zone 3
   - Check environment naming convention matches zone classification

### Resolution

**If approval workflow not enabled:**
1. Open Power Platform Admin Center
2. Navigate to Environments → [Environment] → Settings → Features
3. Enable "Require approval for new chatbots"
4. Optionally enable "Require approval for chatbot updates"
5. Click Save
6. Test publishing again

**If user has admin role:**
1. Verify this is expected behavior (admins can bypass approval)
2. If testing approval workflow, use a test account with only Agent Author role
3. Document that admin accounts bypass approval for operational efficiency

**If environment is Zone 1:**
1. Verify zone classification is correct
2. If environment should be Zone 2+, reclassify environment
3. Apply appropriate DLP policy and approval settings for the zone

### Prevention
- Document environment approval settings in governance documentation
- Use separate test accounts without admin roles for approval workflow testing
- Maintain environment inventory with zone classifications and approval requirements

---

## Issue 5: Approval Request Not Received by Admin

### Symptoms
- Agent author submits agent for approval
- Power Platform Admin does not receive approval notification email
- Approval request not visible in Power Platform Admin Center

### Root Causes
- Email notification disabled or filtered to spam
- Admin not assigned to environment or approval group
- Approval routing misconfigured

### Diagnostic Steps

1. **Check admin's email spam/junk folder:**
   - Search for emails from "Microsoft Power Platform"
   - Check quarantine and blocked sender lists

2. **Verify admin role assignment:**
   ```powershell
   # Check if admin is assigned to environment
   Get-AdminPowerAppEnvironment -EnvironmentName $env | Select-Object RoleAssignments
   ```

3. **Check approval queue in Power Platform Admin Center:**
   - Navigate to Power Platform Admin Center
   - Look for "Pending approvals" or "Notifications" section
   - Verify approval is listed even if email not received

### Resolution

**If email notification issue:**
1. Add "powerplatform.microsoft.com" to safe sender list
2. Check email rules that may be filtering notifications
3. Request IT to whitelist Power Platform notification emails
4. Configure alternative notification method (e.g., Teams notification)

**If admin not assigned:**
1. Assign admin to environment:
   ```powershell
   Add-AdminPowerAppRoleAssignment -EnvironmentName $env -RoleName "Environment Admin" -PrincipalObjectId "ADMIN_OBJECT_ID"
   ```
2. Re-submit publishing request

**If approval routing misconfigured:**
1. Review approval workflow configuration in Power Automate
2. Verify approval flow is active and correctly configured
3. Test approval flow with a manual trigger

### Prevention
- Test approval notification delivery during initial setup
- Document admin contact information and notification preferences
- Establish backup approval process if email notifications fail
- Monitor approval queue regularly regardless of email notifications

---

## Issue 6: Multi-Level Approval Workflow Not Enforced (Zone 3)

### Symptoms
- Zone 3 agent approves after single approval
- Second-level approval not required
- Agent publishes with only Power Platform Admin approval (missing Compliance Officer approval)

### Root Causes
- Multi-level approval workflow not configured in Power Automate
- Environment settings only enforce single approval
- Approval workflow configured but not activated

### Diagnostic Steps

1. **Check for custom approval flow:**
   - Open Power Automate
   - Search for flows related to agent publishing approval
   - Verify flow is active and configured for multi-stage approval

2. **Review environment approval settings:**
   - Verify if built-in approval supports multi-level (may require Power Automate)
   - Check if custom approval flow is referenced in environment settings

### Resolution

**Create multi-level approval workflow using Power Automate:**

1. Create a new flow in Power Automate:
   - Trigger: "When an agent publishing request is submitted"
   - Action: "Start and wait for an approval" (First level - Power Platform Admin)
   - Condition: If first approval is approved
   - Action: "Start and wait for an approval" (Second level - Compliance Officer)
   - Condition: If second approval is approved
   - Action: "Publish agent"
   - Else: "Reject agent publishing request"

2. Activate the flow

3. Update environment settings to use custom approval flow

4. Test multi-level approval with a sample agent

### Prevention
- Document multi-level approval requirements in governance policies
- Test approval workflows during initial Zone 3 environment setup
- Establish SLA for each approval level (e.g., 24 hours for L1, 24 hours for L2)
- Monitor approval metrics to ensure multi-level process is followed

---

## Issue 7: Environment Promotion Pipeline Not Enforced (Zone 3)

### Symptoms
- Agents can be published directly to production from development
- No validation that agent passed through test environment
- Promotion pipeline bypassed

### Root Causes
- Environment groups not configured to link dev/test/prod
- No technical enforcement of promotion sequence
- Manual process not followed by agent authors

### Diagnostic Steps

1. **Check environment group configuration:**
   ```powershell
   # Check if environment groups exist
   Get-AdminPowerAppEnvironmentGroup
   ```

2. **Verify promotion pipeline documentation:**
   - Review governance policies for promotion requirements
   - Check if technical enforcement exists vs. process enforcement

### Resolution

**Configure environment promotion pipeline:**

1. Create environment group linking dev/test/prod:
   - Open Power Platform Admin Center → Environment groups
   - Create group with development, test, and production environments

2. Implement promotion workflow using Power Automate:
   - Trigger: "When agent is published in development"
   - Action: "Create promotion request to test environment"
   - Require approval before promoting to test
   - Trigger: "When agent is published in test"
   - Action: "Create promotion request to production"
   - Require approval before promoting to production

3. Document promotion pipeline in governance policies

4. Train agent authors on promotion process

**Alternative - Manual enforcement:**
1. Document promotion checklist requiring:
   - Evidence of successful development publishing
   - Evidence of successful test environment validation
   - Approval to promote to production
2. Power Platform Admin verifies checklist before approving production publishing

### Prevention
- Implement technical enforcement of promotion pipeline where possible
- Audit production publishing events to identify bypassed promotions
- Require promotion evidence in approval requests
- Use naming conventions for agents to track promotion status (e.g., "AgentName-Dev", "AgentName-Test", "AgentName-Prod")

---

## Issue 8: PowerShell Script Fails - Insufficient Permissions

### Symptoms
- PowerShell compliance audit script fails with permission error
- Error message: "Access denied" or "Insufficient privileges"
- Unable to retrieve agent or DLP policy information

### Root Causes
- PowerShell module not run with Power Platform Admin role
- Service principal used for automation lacks required permissions
- Tenant policies block PowerShell access

### Diagnostic Steps

1. **Verify current user role:**
   ```powershell
   Get-AdminPowerAppEnvironment | Select-Object -First 1
   # If this fails, user lacks admin permissions
   ```

2. **Check module version:**
   ```powershell
   Get-Module -Name Microsoft.PowerApps.Administration.PowerShell -ListAvailable
   ```

3. **Test authentication:**
   ```powershell
   Add-PowerAppsAccount
   # Verify authentication completes successfully
   ```

### Resolution

**If permission issue:**
1. Verify user has Power Platform Admin role assigned
2. Request role assignment from Entra Global Admin if needed
3. Re-run script after role assignment propagates (may take 15-60 minutes)

**If service principal issue:**
1. Grant service principal Power Platform Admin role:
   ```powershell
   # Add service principal as admin
   Add-PowerAppsAccount -TenantID "YOUR_TENANT_ID" -ApplicationId "YOUR_APP_ID" -ClientSecret "YOUR_SECRET"
   ```
2. Update automation to use service principal authentication

**If tenant policy blocks PowerShell:**
1. Contact tenant administrator
2. Request exception for Power Platform PowerShell module
3. Use Azure Automation or Azure Functions as alternative execution environment

### Prevention
- Document required roles for PowerShell automation
- Use service principal with least-privilege permissions for scheduled automation
- Test PowerShell scripts in pre-production before deploying to production automation
- Monitor PowerShell execution logs for permission errors

---

## Issue 9: Audit Logs Not Capturing Publishing Events

### Symptoms
- Publishing events not visible in Microsoft Purview audit logs
- Audit search returns no results for agent publishing
- Missing approval, rejection, or DLP violation events

### Root Causes
- Audit logging not enabled in Microsoft Purview
- Audit log retention policy not configured
- Search parameters incorrect (wrong date range, keywords)

### Diagnostic Steps

1. **Verify audit logging is enabled:**
   - Open Microsoft Purview Compliance Portal → Audit
   - Check if auditing is turned on for the organization

2. **Check audit log retention policy:**
   - Navigate to Purview → Audit → Retention policies
   - Verify policy exists for Power Platform events

3. **Test with broader search:**
   - Search for all activities in last 7 days
   - Verify audit logs are being captured for other services

### Resolution

**If audit logging not enabled:**
1. Open Microsoft Purview Compliance Portal
2. Navigate to Audit → Turn on auditing
3. Wait 30-60 minutes for auditing to activate
4. Perform a test publishing action
5. Search for the test event after 1-2 hours

**If retention policy not configured:**
1. Navigate to Purview → Audit → Retention policies
2. Create new retention policy:
   - Name: "Power Platform Agent Publishing Audit Retention"
   - Record types: "Chatbot activities", "Power Apps activities"
   - Retention period: 7 years (FSI regulatory requirement)
3. Save policy

**If search parameters incorrect:**
1. Use these search parameters:
   - Activities: "Chatbot activities" or "All activities"
   - Keywords: "Chatbot", "Copilot", "Publish", "Approval"
   - Date range: Expand to last 30 days
2. Export results to CSV for detailed review

### Prevention
- Verify audit logging is enabled during initial tenant setup
- Test audit log capture for key events monthly
- Document audit search procedures for compliance team
- Set up alerts for audit log failures or gaps

---

## Issue 10: Blocked Channel Not Detected by Security Scan

### Symptoms
- Agent configured with Facebook or Telegram channel
- Security scan passes without detecting blocked channel
- Agent publishes successfully despite channel restrictions

### Root Causes
- Channel restrictions not enforced via DLP policy
- Security scan not configured to check channel restrictions
- Channel was enabled after agent was published

### Diagnostic Steps

1. **Verify DLP policy includes channel restrictions:**
   - Open Power Platform Admin Center → Policies → Data policies
   - Check if Facebook, Telegram, Public Website connectors are in "Blocked" group

2. **Check agent channel configuration:**
   - Open Copilot Studio → Agent → Settings → Channels
   - List all enabled channels

3. **Test publishing with explicitly blocked channel:**
   - Create a test agent
   - Enable Facebook channel
   - Attempt to publish
   - Verify security scan detects violation

### Resolution

**Update DLP policy to block channels:**
1. Open Power Platform Admin Center → Policies → Data policies
2. Edit the relevant DLP policy
3. Add the following connectors to "Blocked" group:
   - Facebook
   - Telegram
   - Public Website
4. Save policy
5. Re-test agent publishing

**Disable blocked channels on existing agents:**
1. Audit all published agents for channel configuration:
   ```powershell
   Get-AdminPowerAppChatbot -EnvironmentName $env | Select-Object DisplayName, Channels
   ```
2. For each agent with blocked channels:
   - Open agent in Copilot Studio
   - Navigate to Settings → Channels
   - Disable prohibited channels
   - Save changes

### Prevention
- Include channel restrictions in zone-specific DLP policies
- Document approved channels for each zone in governance policies
- Audit agent channel configuration monthly
- Require channel justification in publishing approval requests

---

## Escalation Paths

If issues cannot be resolved using this playbook:

1. **Level 1 (Agent Authors):** Contact Power Platform Admin
2. **Level 2 (Power Platform Admin):** Contact Entra Global Admin or Microsoft Support
3. **Level 3 (Microsoft Support):**
   - Open support ticket via Microsoft 365 Admin Center
   - Select "Power Platform" → "Copilot Studio" → "Publishing and DLP"
   - Provide diagnostic information from troubleshooting steps

---

## Additional Resources

- [Microsoft Learn: Data loss prevention policies troubleshooting](https://learn.microsoft.com/en-us/power-platform/admin/wp-data-loss-prevention)
- [Microsoft Learn: Copilot Studio troubleshooting](https://learn.microsoft.com/en-us/troubleshoot/power-platform/copilot-studio/welcome-copilot-studio)
- [Microsoft Support: Power Platform support](https://aka.ms/powerplatformsupport)

---

[Back to Control 1.28](../../../controls/pillar-1-security/1.28-policy-based-agent-publishing-restrictions.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification & Testing](verification-testing.md)
