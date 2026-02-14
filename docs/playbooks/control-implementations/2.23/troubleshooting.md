# Troubleshooting: Control 2.23 - User Consent and AI Disclosure Enforcement

**Last Updated:** February 2026

## Common Issues and Resolutions

This playbook addresses common issues encountered when implementing and operating Control 2.23.

---

## Issue 1: AI Disclaimer Toggle Not Visible in Microsoft 365 Admin Center

### Symptoms
- AI Disclaimer toggle is not visible under Settings → Org settings → Copilot
- Copilot settings panel exists but does not include AI Disclaimer section
- Error message: "This feature is not yet available in your tenant"

### Root Causes
1. Tenant has not yet received the AI Disclaimer feature rollout (late November 2025+)
2. User account lacks Entra Global Admin role
3. Feature is hidden behind a preview flag or feature control

### Resolution Steps

**Step 1: Verify feature rollout status**
```powershell
# Check Microsoft 365 Message Center for AI Disclaimer rollout announcements
Connect-MgGraph -Scopes "ServiceMessage.Read.All"
Get-MgServiceAnnouncementMessage | Where-Object { $_.Title -like "*AI Disclaimer*" -or $_.Title -like "*Copilot*" }
```

- Look for Message Center announcements referencing AI Disclaimer or Copilot organizational settings
- Note the rollout date and expected availability for your tenant region

**Step 2: Verify admin permissions**
```powershell
# Check current user's admin roles
Connect-MgGraph -Scopes "Directory.Read.All"
$user = Get-MgUser -UserId (Get-MgContext).Account
Get-MgUserMemberOf -UserId $user.Id | Where-Object { $_.AdditionalProperties."@odata.type" -eq "#microsoft.graph.directoryRole" }
```

- Confirm the user has "Entra Global Admin" role
- If not, request Entra Global Admin access or delegate to an admin with the correct role

**Step 3: Contact Microsoft Support**
- If feature rollout is complete for your tenant region and permissions are correct, contact Microsoft Support
- Provide: Tenant ID, Message Center post reference, screenshot of missing AI Disclaimer section
- Request manual enablement of the AI Disclaimer feature for your tenant

**Step 4: Workaround (Interim)**
- While waiting for tenant-level AI Disclaimer, implement agent-level disclosure in all agent greeting topics
- Deploy custom disclosure in Teams app welcome messages
- Document the interim approach and plan to migrate to tenant-level AI Disclaimer when available

---

## Issue 2: Custom Disclosure URL Not Clickable or Link Does Not Work

### Symptoms
- Custom disclosure URL appears in the AI Disclaimer banner but is not clickable
- Clicking the link results in "Page not found" or access denied error
- Link opens a different page than expected

### Root Causes
1. URL is not properly formatted (missing https://, extra spaces, or special characters)
2. Target policy document requires authentication that users do not have
3. SharePoint or internal site URL is not accessible from user's network
4. URL was updated in admin center but changes have not propagated (caching delay)

### Resolution Steps

**Step 1: Verify URL format**
- Open Microsoft 365 Admin Center → Settings → Org settings → Copilot
- Review the custom disclosure URL field
- Ensure the URL includes the full protocol (e.g., `https://contoso.com/policies/ai-transparency`)
- Check for extra spaces, line breaks, or hidden characters (copy to Notepad to inspect)

**Step 2: Test URL accessibility**
```powershell
# Test URL accessibility from PowerShell
$url = "https://contoso.com/policies/ai-transparency"
try {
    $response = Invoke-WebRequest -Uri $url -UseBasicParsing
    Write-Host "URL is accessible. Status: $($response.StatusCode)" -ForegroundColor Green
}
catch {
    Write-Error "URL is not accessible: $_"
}
```

- Test the URL from multiple locations: internal network, VPN, external (off-network)
- Verify the URL opens the correct policy document in a browser

**Step 3: Check SharePoint permissions (if using SharePoint)**
- If the custom URL points to a SharePoint site or document:
  - Open SharePoint Admin Center
  - Navigate to the site/document permissions
  - Verify "Everyone" or "All Authenticated Users" has Read access
  - For external users, enable external sharing for the site/document

**Step 4: Clear cache and test**
- Changes to the custom disclosure URL may take up to 24 hours to propagate
- Clear browser cache and cookies for Microsoft 365 domains
- Test with a new user account that has not yet seen the AI Disclaimer
- If still not working, wait 24 hours and re-test

**Step 5: Use a shortened URL (alternative)**
- If the URL is very long or contains special characters, use a URL shortener or redirect:
  - Create a redirect page: `https://contoso.com/ai-policy` → redirects to full URL
  - Use Microsoft's short link service or internal URL shortener
  - Update the custom disclosure URL to the shortened link

---

## Issue 3: Agent Greeting Topic Does Not Display AI Disclosure

### Symptoms
- Agent greeting topic exists but does not include AI disclosure language
- Greeting topic displays but disclosure text is missing or incomplete
- Disclosure only appears on first use, not on every conversation start (Zone 3 requirement)

### Root Causes
1. Greeting topic was not modified to include AI disclosure language
2. Greeting topic is disabled or not set to trigger on conversation start
3. Custom greeting topic exists but is not published to the live agent
4. Topic trigger conditions prevent the greeting from displaying

### Resolution Steps

**Step 1: Verify greeting topic configuration**
- Open Copilot Studio → Select agent → Topics → System → Greeting
- Review the greeting topic message nodes
- Confirm AI disclosure language is present in the message text
- Ensure the disclosure includes required elements for the agent's governance zone

**Step 2: Check topic trigger settings**
- In the greeting topic editor, click the topic trigger (top of the canvas)
- Review the trigger type: "On conversation start" or "On first use only"
- For Zone 3 agents, ensure trigger is set to "On conversation start" (not "On first use only")
- Save the topic after making changes

**Step 3: Publish the agent**
- After modifying the greeting topic, the agent must be published
- Click **Publish** in the top-right corner of Copilot Studio
- Wait for the publish operation to complete (30 seconds to 2 minutes)
- Test with a new conversation to verify the updated greeting appears

**Step 4: Test in the correct channel**
- Greeting topics may behave differently across channels (Teams vs. web vs. mobile)
- Test the agent in the primary deployment channel (e.g., Microsoft Teams)
- If greeting does not appear in one channel but does in another, check channel-specific settings

**Step 5: Check for conflicting topics**
- If multiple greeting or welcome topics exist, they may conflict
- Review all system topics for duplicate welcome/greeting triggers
- Disable or delete conflicting topics
- Ensure only one greeting topic is active

---

## Issue 4: Consent Records Not Created in Dataverse (Zone 3)

### Symptoms
- User acknowledges consent in the agent, but no record appears in Dataverse `fsi_aiconsent` table
- Consent acknowledgment prompt functions (conversation proceeds), but record is missing
- Error in Power Automate flow logs: "Failed to create record in Dataverse"

### Root Causes
1. Dataverse `fsi_aiconsent` table does not exist or has incorrect schema
2. Power Automate flow is not correctly configured or has authentication issues
3. Service principal or app registration lacks Dataverse write permissions
4. Power Automate flow has a runtime error (timeout, data type mismatch, etc.)

### Resolution Steps

**Step 1: Verify Dataverse table exists**
```powershell
# Query Dataverse to check if fsi_aiconsent table exists
# This is a conceptual example - use Dataverse Web API or Power Platform CLI
$dataverseUrl = "https://contoso.crm.dynamics.com"
$tableName = "fsi_aiconsent"

# Check table existence (requires Dataverse authentication)
# Invoke-RestMethod -Uri "$dataverseUrl/api/data/v9.2/EntityDefinitions(LogicalName='$tableName')" -Headers $authHeader
```

- Open Power Apps (make.powerapps.com) → Select environment → Tables
- Search for `fsi_aiconsent` table
- If not found, create the table with required fields:
  - `fsi_userid` (Single line of text)
  - `fsi_agentname` (Single line of text)
  - `fsi_consenttimestamp` (Date and time)
  - `fsi_disclosureversion` (Single line of text)
  - `fsi_acknowledgmentstatus` (Yes/No)

**Step 2: Verify Power Automate flow configuration**
- Open Power Automate (make.powerautomate.com) → My flows
- Locate the consent logging flow (called from the agent's consent topic)
- Review the flow steps:
  1. Trigger: "When an HTTP request is received" or "Respond to Copilot Studio"
  2. Action: "Add a new row" to Dataverse `fsi_aiconsent` table
  3. Fields: Map input parameters to table fields
- Click **Flow checker** to identify errors
- Test the flow with sample data

**Step 3: Check Power Automate flow permissions**
- Open the consent logging flow → Edit
- Click the Dataverse "Add a new row" action
- Review the connection:
  - If "Connection requires authentication", click to re-authenticate
  - Use a service account with Dataverse write permissions
- Save and re-publish the flow

**Step 4: Review flow run history**
- Open the consent logging flow → 28-day run history
- Locate the failed run corresponding to the test consent acknowledgment
- Click the failed run to view error details:
  - **401 Unauthorized:** Authentication issue; re-authenticate the Dataverse connection
  - **400 Bad Request:** Data type mismatch; verify input parameters match table schema
  - **404 Not Found:** Table or field does not exist; verify table name and field names
  - **Timeout:** Flow took too long; optimize flow steps or increase timeout setting
- Address the specific error and re-test

**Step 5: Test end-to-end**
- Update the agent's consent topic to call the corrected Power Automate flow
- Publish the agent
- Test consent acknowledgment with a new user
- Query Dataverse to confirm the record is created:
  ```sql
  -- FetchXML query
  <fetch>
    <entity name='fsi_aiconsent'>
      <attribute name='fsi_userid' />
      <attribute name='fsi_consenttimestamp' />
      <order attribute='fsi_consenttimestamp' descending='true' />
      <filter>
        <condition attribute='fsi_consenttimestamp' operator='last-x-hours' value='1' />
      </filter>
    </entity>
  </fetch>
  ```

---

## Issue 5: Purview Audit Logs Do Not Show Consent Events

### Symptoms
- Configuration changes to AI Disclaimer settings do not appear in Purview audit logs
- User consent acknowledgments are not logged in Purview
- Audit log search returns no results for expected events

### Root Causes
1. Purview audit logging is not enabled for the tenant
2. Audit log indexing delay (events take 30 minutes to 24 hours to appear)
3. Search query uses incorrect activity names or date range
4. User account lacks permissions to view audit logs

### Resolution Steps

**Step 1: Verify Purview audit logging is enabled**
```powershell
# Check audit logging status
Connect-ExchangeOnline
Get-AdminAuditLogConfig | Select-Object UnifiedAuditLogIngestionEnabled
```

- If `UnifiedAuditLogIngestionEnabled` is False, enable audit logging:
  ```powershell
  Set-AdminAuditLogConfig -UnifiedAuditLogIngestionEnabled $true
  ```
- Allow 30 minutes for audit logging to become active

**Step 2: Wait for audit log indexing**
- Audit events can take 30 minutes to 24 hours to appear in Purview
- After making a configuration change or consent acknowledgment, wait at least 1 hour before searching
- For critical events, wait up to 24 hours for full indexing

**Step 3: Refine audit log search query**
- Open Purview Compliance Portal → Audit → Search
- Set date range to include the event (e.g., last 7 days)
- Search for activities:
  - Configuration changes: "Update organization settings", "Set tenant policy", "Update Copilot settings"
  - Consent events: "User consent", "Chatbot interaction", "Agent usage"
- Filter by user: Admin account (for config changes), test user (for consent)
- Use wildcard searches if exact activity names are unknown (e.g., `*Copilot*`, `*consent*`)

**Step 4: Verify audit log permissions**
- User must have one of these roles to view audit logs:
  - Purview Compliance Admin
  - Entra Global Admin
  - Organization Management (Exchange Online)
- If lacking permissions, request role assignment from an Entra Global Admin

**Step 5: Export audit logs for analysis**
```powershell
# Export audit logs via PowerShell
Connect-ExchangeOnline
$startDate = (Get-Date).AddDays(-7)
$endDate = Get-Date
Search-UnifiedAuditLog -StartDate $startDate -EndDate $endDate -Operations "UserConsent","UpdateOrganizationSettings" | Export-Csv -Path "AuditLogs.csv" -NoTypeInformation
```

- Review the exported CSV for consent and configuration events
- If events are still missing, contact Microsoft Support to investigate audit log ingestion issues

---

## Issue 6: Disclosure Does Not Display on Mobile App

### Symptoms
- AI Disclaimer and agent-level disclosure display correctly in web browser and Teams desktop app
- Mobile app (iOS or Android) does not show the AI Disclaimer banner or agent greeting disclosure
- User experience is inconsistent across platforms

### Root Causes
1. Mobile app has not yet received the AI Disclaimer feature (mobile rollout may lag desktop)
2. Mobile app cache is stale (displaying old version without disclosure)
3. Mobile app authentication uses a different profile that bypasses tenant settings
4. Known bug in mobile app version

### Resolution Steps

**Step 1: Verify mobile app version**
- Open Microsoft Teams mobile app → Settings → About
- Check the app version number
- Compare with the latest version in the App Store (iOS) or Google Play Store (Android)
- Update to the latest version if behind

**Step 2: Clear mobile app cache**
- **iOS:** Teams app → Settings → Privacy → Clear app data → Confirm
- **Android:** Device Settings → Apps → Teams → Storage → Clear cache
- Sign out of the Teams mobile app and sign back in
- Test the AI Disclaimer and agent greeting disclosure again

**Step 3: Check mobile app feature flags**
- Some features may be behind feature flags in mobile apps
- Open Teams mobile app → Settings → Developer (if available) → Feature flags
- Enable any flags related to Copilot or AI Disclaimer
- Restart the app and re-test

**Step 4: Test in mobile browser**
- As an alternative, open the web version of Copilot or the agent in the mobile device's browser
- Navigate to copilot.microsoft.com or the agent's web deployment URL
- Verify disclosure displays correctly in the mobile browser
- If it does, the issue is specific to the mobile app; report to Microsoft

**Step 5: Report mobile app issue**
- If disclosure still does not display in the mobile app after updates and cache clearing:
  - Open Teams mobile app → Settings → Help → Report a problem
  - Describe the issue: "AI Disclaimer does not display on first use in mobile app"
  - Include: Device type, OS version, Teams app version, tenant ID
- Monitor for mobile app updates from Microsoft addressing this issue

---

## Issue 7: Custom Disclosure URL Requires Authentication External Users Cannot Provide

### Symptoms
- Custom disclosure URL points to an internal SharePoint site or intranet page
- External users or guest accounts receive "Access denied" or authentication prompt errors
- Disclosure is accessible to internal users but not external users

### Root Causes
1. SharePoint site or document is restricted to internal users only (no guest access)
2. External sharing is disabled for the site or document
3. Guest user accounts are not provisioned in Entra ID or lack SharePoint permissions
4. Conditional Access policy blocks external access to SharePoint

### Resolution Steps

**Step 1: Enable external sharing for the disclosure document**
- Open SharePoint Admin Center → Policies → Sharing
- Verify external sharing is enabled for the site hosting the disclosure document
- Set sharing level to "Anyone" or "New and existing guests" (based on sensitivity)
- For the specific document:
  - Open SharePoint site → Navigate to disclosure document
  - Click **Share** → Advanced → Allow external sharing
  - Grant "Read" permissions to "Anyone with the link"

**Step 2: Use a public-facing disclosure page**
- Host the AI transparency policy on a public-facing website (outside SharePoint)
- Example: `https://www.contoso.com/policies/ai-transparency`
- Update the custom disclosure URL in Microsoft 365 admin center to the public URL
- Verify the public page does not require authentication

**Step 3: Create a guest-accessible SharePoint page**
- If disclosure must remain in SharePoint:
  - Create a dedicated SharePoint site for governance documentation
  - Enable external sharing for this site only
  - Add guest users to the site with "Read" permissions
  - Move the AI transparency policy to this site
  - Update the custom disclosure URL to the new SharePoint page

**Step 4: Test external access**
- Use a personal email account (gmail.com, outlook.com) to simulate an external user
- Sign in to Microsoft 365 Copilot or the agent as a guest user
- Click the custom disclosure URL link
- Verify the page opens without authentication errors
- If prompted to sign in, use the guest account credentials (should succeed)

**Step 5: Review Conditional Access policies**
```powershell
# Check Conditional Access policies affecting SharePoint
Connect-MgGraph -Scopes "Policy.Read.All"
Get-MgIdentityConditionalAccessPolicy | Where-Object { $_.Conditions.Applications.IncludeApplications -contains "00000003-0000-0ff1-ce00-000000000000" }
```

- Review policies that apply to SharePoint (Application ID: 00000003-0000-0ff1-ce00-000000000000)
- Check for policies that block guest user access or require MFA from external locations
- Create an exception for the governance documentation site or adjust policy scope

---

## Issue 8: Consent Expiration Logic Not Triggering Re-Acknowledgment

### Symptoms
- Consent records in Dataverse show timestamps older than the configured validity period (e.g., 90 days)
- Users with expired consent records are not prompted to re-acknowledge consent
- Conversation proceeds without re-acknowledgment prompt

### Root Causes
1. Consent expiration logic is not implemented in the agent's greeting topic
2. Consent verification flow does not check record age
3. Dataverse query in the verification flow is incorrect or returns no results
4. Cached consent status in the agent session bypasses expiration check

### Resolution Steps

**Step 1: Verify consent expiration logic exists**
- Open Copilot Studio → Select Zone 3 agent → Topics → System → Greeting
- Review the consent prompt logic:
  - Before displaying the consent prompt, check Dataverse for existing consent record
  - Calculate the age of the most recent consent record (current date - fsi_consenttimestamp)
  - If age > validity period (e.g., 90 days), display the consent prompt again
  - If age ≤ validity period, skip the consent prompt and proceed to agent functionality

**Step 2: Implement consent age check**
- Add a Power Automate flow step to calculate consent record age:
  ```
  1. Get user ID from current conversation context
  2. Query Dataverse fsi_aiconsent table for most recent record for this user and agent
  3. If no record found → Display consent prompt
  4. If record found:
     - Calculate daysSinceConsent = (currentDate - fsi_consenttimestamp).days
     - If daysSinceConsent > 90 → Display consent prompt
     - Else → Skip consent prompt
  ```

**Step 3: Test consent expiration with backdated record**
- Manually create a test consent record in Dataverse with a timestamp 91 days in the past:
  ```sql
  -- Insert test record (conceptual - use Dataverse UI or API)
  INSERT INTO fsi_aiconsent (fsi_userid, fsi_agentname, fsi_consenttimestamp, fsi_acknowledgmentstatus)
  VALUES ('testuser@contoso.com', 'Test Agent', '2025-11-13', true)
  ```
- Sign in as the test user and start a conversation with the agent
- Verify the consent prompt displays again (despite having a previous record)
- Acknowledge consent and confirm a new record is created with the current timestamp

**Step 4: Clear session cache**
- If consent status is cached in the agent session:
  - Sign out of the agent and sign back in
  - Clear browser cookies and cache for Microsoft 365 domains
  - Test with a new user account to ensure no cached session data

**Step 5: Schedule periodic consent expiration checks**
- Implement a scheduled Power Automate flow that runs daily:
  - Query fsi_aiconsent table for records older than 90 days
  - Flag these records as expired (add `fsi_isx expired` field)
  - Send notification to users with expired consent to re-acknowledge
- Update the agent's greeting topic to check the `fsi_isexpired` field and prompt accordingly

---

## Issue 9: Disclosure Language Does Not Meet Zone 3 Regulatory Requirements

### Symptoms
- Disclosure language is generic and does not include regulatory-specific elements
- Compliance review identifies missing components: data handling specifics, escalation path, etc.
- Disclosure passes technical implementation but fails regulatory audit

### Root Causes
1. Disclosure language was copied from Zone 1 or Zone 2 template without customization
2. Regulatory requirements were not reviewed during disclosure authoring
3. Legal or compliance team was not consulted for disclosure language approval

### Resolution Steps

**Step 1: Review Zone 3 disclosure requirements**
- Zone 3 agents must include:
  1. **Explicit AI identification:** "I'm an AI assistant"
  2. **Statement about AI-generated responses:** "Responses are generated by AI and should be reviewed"
  3. **Monitoring notice:** "Conversations may be monitored for compliance and quality assurance"
  4. **Link to organizational AI policy:** "For more information, see [AI Policy URL]"
  5. **Data handling specifics:** "Your conversations are processed and stored in [location] for [duration]"
  6. **User rights:** "You have the right to request deletion of your conversation data by contacting [contact]"
  7. **Escalation path:** "If you have concerns about AI usage, contact [compliance officer]"

**Step 2: Collaborate with legal and compliance**
- Schedule a review session with:
  - Legal counsel (regulatory language)
  - Compliance officer (FINRA, SEC, GLBA requirements)
  - Privacy officer (GLBA 501(b) privacy notice requirements)
  - AI Governance Lead (alignment with organizational AI policy)
- Provide draft disclosure language for review
- Incorporate feedback and obtain formal approval

**Step 3: Update agent disclosure language**
- Open Copilot Studio → Select Zone 3 agent → Topics → System → Greeting
- Replace generic disclosure with approved Zone 3 disclosure language:
  ```
  Hello! I'm [Agent Name], an AI assistant created by [Organization Name] to provide [specific purpose].
  
  Important Information:
  - I use artificial intelligence to generate responses. All responses should be reviewed by qualified personnel before making decisions.
  - Your conversations with me may be monitored and recorded for quality assurance, training, and compliance purposes.
  - Conversation data is processed and stored in Microsoft Azure (United States) for up to 90 days, after which it is archived or deleted according to our retention policy.
  - You have the right to request access to or deletion of your conversation data by contacting our Privacy Officer at [email].
  - For questions about AI usage, data handling, or to raise concerns, please contact our Chief Compliance Officer at [email] or call [phone].
  
  For detailed information, please review our [AI Transparency and Data Handling Policy](https://contoso.com/policies/ai-transparency).
  
  Do you agree to these terms and wish to continue?
  ```
- Save and publish the updated agent

**Step 4: Document disclosure approval**
- Create a disclosure approval record:
  - Disclosure language version
  - Approval date and approvers (legal, compliance, privacy)
  - Zone 3 requirement checklist (all 7 elements present)
  - Reference to organizational AI policy document
- Store in governance documentation repository for audit trail

**Step 5: Train agent authors on Zone 3 requirements**
- Conduct training for Copilot Studio agent authors on Zone 3 disclosure requirements
- Provide a disclosure language template with all required elements
- Implement a review workflow: All Zone 3 agent disclosure changes require compliance approval before publication

---

## Escalation Path

If issues cannot be resolved using this troubleshooting guide:

1. **Microsoft Support:** Open a support ticket for Microsoft 365, Power Platform, or Purview issues
   - Portal: [Microsoft 365 Admin Center → Support](https://admin.microsoft.com/AdminPortal/Home#/support)
   - Include: Tenant ID, issue description, troubleshooting steps attempted, screenshots, error messages

2. **Internal Escalation:**
   - **Technical issues:** Escalate to Power Platform Admin or Copilot Studio technical lead
   - **Regulatory issues:** Escalate to Compliance Officer or Chief Compliance Officer
   - **Audit issues:** Escalate to Purview Compliance Admin or IT Audit team

3. **FSI Agent Governance Framework Community:**
   - Post questions in the discussion forum (if available)
   - Consult the framework maintainers for guidance on control implementation

---

## Additional Resources

- [Microsoft Learn: Troubleshooting Copilot Studio](https://learn.microsoft.com/en-us/troubleshoot/power-platform/copilot-studio/welcome-copilot-studio)
- [Microsoft Learn: Purview Audit Log Troubleshooting](https://learn.microsoft.com/en-us/purview/audit-troubleshooting-scenarios)
- [Microsoft Learn: Power Platform Admin Troubleshooting](https://learn.microsoft.com/en-us/troubleshoot/power-platform/administration/welcome-administration)
- [Microsoft Learn: Dataverse Developer Guide](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/)

---

[Back to Control 2.23](../../../controls/pillar-2-management/2.23-user-consent-and-ai-disclosure-enforcement.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md)
