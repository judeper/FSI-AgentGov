# Verification & Testing: Control 2.23 - User Consent and AI Disclosure Enforcement

**Last Updated:** February 2026
**Estimated Time:** 20-30 minutes

## Test Scope

This playbook provides test cases to verify:
1. Tenant-wide AI Disclaimer displays correctly for Microsoft 365 Copilot users
2. Custom disclosure URL links to the correct organizational policy document
3. Agent-level disclosure appears in greeting topics
4. Consent acknowledgment prompts function correctly (Zone 3)
5. Consent records are created and stored in Dataverse (Zone 3)
6. Purview audit logging captures disclosure and consent events

---

## Test Environment Setup

### Prerequisites

- [ ] Test user accounts in each governance zone (Zone 1, Zone 2, Zone 3)
- [ ] Access to Microsoft 365 Copilot
- [ ] Access to test agents in Copilot Studio
- [ ] Dataverse environment with `fsi_aiconsent` table (for Zone 3 tests)
- [ ] Purview Compliance Portal access for audit log verification
- [ ] Screenshot capture tool for evidence collection

### Test User Roles

| Test User | Role | Purpose |
|-----------|------|---------|
| testuser-zone1@contoso.com | Zone 1 user | Test personal productivity agent disclosure |
| testuser-zone2@contoso.com | Zone 2 user | Test team collaboration agent disclosure |
| testuser-zone3@contoso.com | Zone 3 user | Test enterprise agent consent acknowledgment |
| admin@contoso.com | Administrator | Verify admin configuration and audit logs |

---

## Test Case 1: Tenant-Wide AI Disclaimer Display

**Objective:** Verify the AI Disclaimer banner displays for new Microsoft 365 Copilot users with the custom disclosure URL.

### Test Steps

1. **Prepare test environment:**
   - Identify a user account that has never accessed Microsoft 365 Copilot (or clear previous consent records)
   - Confirm the AI Disclaimer toggle is enabled in Microsoft 365 admin center
   - Confirm the custom disclosure URL is configured

2. **Execute test:**
   - Sign in to Microsoft 365 as the test user
   - Navigate to Microsoft 365 Copilot (copilot.microsoft.com or Teams app)
   - Observe the first-launch experience

3. **Expected Results:**
   - [ ] A banner or modal displays with AI disclosure language
   - [ ] The banner includes text such as "Learn more about how Microsoft uses your data"
   - [ ] A clickable link to the custom disclosure URL is visible
   - [ ] Clicking the link opens the organizational AI policy document in a new tab
   - [ ] The policy document URL matches the configured custom disclosure URL

4. **Evidence Collection:**
   - Screenshot of the AI Disclaimer banner on first launch
   - Screenshot of the custom disclosure URL link
   - Screenshot of the opened organizational policy document
   - Timestamp of test execution

### Pass/Fail Criteria

- **Pass:** Disclaimer displays on first use with correct custom URL that opens the organizational policy document
- **Fail:** Disclaimer does not display, or custom URL is missing/incorrect, or link does not open the policy document

---

## Test Case 2: Agent-Level Disclosure in Greeting Topic

**Objective:** Verify AI disclosure language appears in the agent's greeting topic before user interaction begins.

### Test Steps

1. **Prepare test environment:**
   - Select a test agent configured with AI disclosure in the greeting topic
   - Note the agent's governance zone classification
   - Review the expected disclosure language for that zone

2. **Execute test:**
   - Sign in to Copilot Studio or the agent's deployment channel (Teams, web)
   - Start a new conversation with the test agent
   - Observe the first message from the agent

3. **Expected Results:**
   - [ ] The agent's first message includes AI disclosure language
   - [ ] Disclosure includes: AI system identification, statement about AI-generated responses, monitoring notice (Zone 2+)
   - [ ] Disclosure includes a link to the organizational AI policy (Zone 2+)
   - [ ] Disclosure language matches the governance zone requirements:
     - **Zone 1:** General AI disclosure
     - **Zone 2:** Organizational policy link + monitoring notice
     - **Zone 3:** Regulatory language + data handling specifics + escalation path

4. **Evidence Collection:**
   - Screenshot of the agent greeting message with AI disclosure
   - Copy of the disclosure text for comparison with requirements
   - Agent name and governance zone classification
   - Timestamp of test execution

### Pass/Fail Criteria

- **Pass:** Greeting topic displays AI disclosure language appropriate for the agent's governance zone
- **Fail:** No disclosure in greeting topic, or disclosure language does not meet zone requirements

---

## Test Case 3: Consent Acknowledgment Prompt (Zone 3)

**Objective:** Verify mandatory consent acknowledgment prompts function correctly for Zone 3 agents.

### Test Steps

1. **Prepare test environment:**
   - Select a Zone 3 agent configured with consent acknowledgment
   - Identify a test user account without a recent consent record
   - Ensure the Dataverse `fsi_aiconsent` table is deployed and accessible

2. **Execute test - Positive acknowledgment:**
   - Sign in as the test user
   - Start a new conversation with the Zone 3 agent
   - Observe the consent prompt
   - Respond with "yes", "I agree", or "I understand" (as configured)

3. **Expected Results (Positive):**
   - [ ] A consent prompt displays after the greeting message
   - [ ] Prompt text includes: AI system disclosure, monitoring notice, request for acknowledgment
   - [ ] After responding "yes", the conversation proceeds to agent functionality
   - [ ] A consent record is created in Dataverse `fsi_aiconsent` table with:
     - User ID
     - Agent name
     - Consent timestamp
     - Disclosure version
     - Acknowledgment status = True

4. **Execute test - Negative acknowledgment:**
   - Repeat the test with a different test user
   - Respond with "no" or "I do not agree" to the consent prompt

5. **Expected Results (Negative):**
   - [ ] The agent displays a message such as "I'm unable to assist without consent acknowledgment. Please contact [support] for assistance."
   - [ ] The conversation ends or does not proceed to agent functionality
   - [ ] A consent record is created in Dataverse with Acknowledgment status = False (or no record is created)

6. **Evidence Collection:**
   - Screenshot of the consent prompt
   - Screenshot of the positive acknowledgment flow (conversation proceeds)
   - Screenshot of the negative acknowledgment flow (conversation ends)
   - Dataverse query results showing the consent record
   - Timestamp of test execution

### Pass/Fail Criteria

- **Pass:** Consent prompt displays, positive acknowledgment allows conversation, negative acknowledgment ends conversation, consent records are created in Dataverse
- **Fail:** Consent prompt missing, acknowledgment logic does not work, or consent records are not created

---

## Test Case 4: Consent Record Persistence in Dataverse

**Objective:** Verify consent records are correctly stored in Dataverse with all required fields.

### Test Steps

1. **Prepare test environment:**
   - Complete Test Case 3 (Consent Acknowledgment Prompt) to generate consent records
   - Access Dataverse environment with `fsi_aiconsent` table
   - Prepare a query to retrieve recent consent records

2. **Execute test:**
   - Query Dataverse `fsi_aiconsent` table for records created in the last hour
   - Filter by test user ID or agent name

3. **Expected Results:**
   - [ ] Consent record exists in Dataverse for the test user
   - [ ] Record includes all required fields:
     - `fsi_userid`: Test user's email or ID
     - `fsi_agentname`: Zone 3 agent name
     - `fsi_consenttimestamp`: Timestamp of consent acknowledgment (matches test execution time)
     - `fsi_disclosureversion`: Disclosure version number (e.g., "v1.0")
     - `fsi_acknowledgmentstatus`: True (for positive acknowledgment) or False (for negative)
   - [ ] Record is immutable (no modification timestamp or modified by field)

4. **Evidence Collection:**
   - Screenshot or export of Dataverse query results
   - Full consent record details
   - Timestamp of query execution

### Pass/Fail Criteria

- **Pass:** Consent record exists in Dataverse with all required fields populated correctly
- **Fail:** Consent record missing, or required fields are empty/incorrect

---

## Test Case 5: Consent Expiration and Re-Acknowledgment

**Objective:** Verify consent expiration logic triggers re-acknowledgment prompts after the configured validity period.

### Test Steps

1. **Prepare test environment:**
   - Configure consent validity period (e.g., 90 days for Zone 3)
   - Identify a test user with a consent record older than the validity period (or manually backdate a record for testing)
   - Access the Zone 3 agent

2. **Execute test:**
   - Sign in as the test user with expired consent
   - Start a new conversation with the Zone 3 agent
   - Observe whether the consent prompt displays again

3. **Expected Results:**
   - [ ] The consent prompt displays again even though the user has a previous consent record
   - [ ] The prompt indicates that re-acknowledgment is required (e.g., "It's been 90 days since your last acknowledgment. Please confirm you understand...")
   - [ ] Upon acknowledgment, a new consent record is created in Dataverse with a current timestamp

4. **Evidence Collection:**
   - Screenshot of the re-acknowledgment prompt
   - Dataverse query showing the old consent record and the new consent record
   - Timestamp of test execution

### Pass/Fail Criteria

- **Pass:** Consent prompt displays for users with expired consent, new consent record is created upon re-acknowledgment
- **Fail:** No prompt displays for expired consent, or new consent record is not created

---

## Test Case 6: Cross-Platform Disclosure Consistency

**Objective:** Verify disclosure displays consistently across Microsoft Teams, web browser, and mobile app (if applicable).

### Test Steps

1. **Prepare test environment:**
   - Access the test agent through multiple channels:
     - Microsoft Teams desktop app
     - Web browser (copilot.microsoft.com or Copilot Studio deployment)
     - Microsoft Teams mobile app (iOS or Android)
   - Use the same test user account across all channels

2. **Execute test:**
   - Open the agent in Microsoft Teams desktop app and verify disclosure displays
   - Open the agent in a web browser and verify disclosure displays
   - Open the agent in Microsoft Teams mobile app and verify disclosure displays

3. **Expected Results:**
   - [ ] AI disclosure language appears in the greeting topic across all channels
   - [ ] Disclosure content is identical across channels
   - [ ] Custom disclosure URL link functions correctly in all channels
   - [ ] Consent acknowledgment prompt displays and functions correctly in all channels (Zone 3)

4. **Evidence Collection:**
   - Screenshot of disclosure in Microsoft Teams desktop
   - Screenshot of disclosure in web browser
   - Screenshot of disclosure in mobile app
   - Timestamp of test execution

### Pass/Fail Criteria

- **Pass:** Disclosure displays consistently with identical content and functional links across all channels
- **Fail:** Disclosure is missing or inconsistent across channels, or links do not function

---

## Test Case 7: Purview Audit Log Capture

**Objective:** Verify Purview audit logging captures disclosure configuration changes and consent events.

### Test Steps

1. **Prepare test environment:**
   - Ensure Purview audit logging is enabled for the tenant
   - Access Purview Compliance Portal with Purview Compliance Admin role
   - Note the timestamp before executing test actions

2. **Execute test - Configuration change:**
   - As an admin, modify the tenant-wide AI Disclaimer setting (toggle off then on, or change the custom URL)
   - Wait 10-15 minutes for audit log indexing

3. **Execute test - Consent event:**
   - As a test user, complete a consent acknowledgment with a Zone 3 agent (Test Case 3)
   - Wait 10-15 minutes for audit log indexing

4. **Execute test - Query audit logs:**
   - In Purview Compliance Portal, navigate to Audit → Search
   - Set date range to include the test actions
   - Search for activities related to:
     - "Update Copilot settings" or similar for configuration changes
     - "User consent" or "Chatbot interaction" for consent events
   - Filter by user (admin account for config, test user for consent)

5. **Expected Results:**
   - [ ] Audit log entry exists for the AI Disclaimer configuration change:
     - Activity: Update Copilot settings (or similar)
     - User: Admin account
     - Timestamp: Matches configuration change time
     - Details: Shows AI Disclaimer toggle status change or URL update
   - [ ] Audit log entry exists for the consent acknowledgment event:
     - Activity: User consent or Chatbot interaction (or similar)
     - User: Test user account
     - Timestamp: Matches consent acknowledgment time
     - Details: Shows agent name, consent status

6. **Evidence Collection:**
   - Screenshot of audit log search results
   - Screenshot of audit log entry details for configuration change
   - Screenshot of audit log entry details for consent event
   - Timestamp of query execution

### Pass/Fail Criteria

- **Pass:** Audit log entries exist for both configuration changes and consent events with accurate details
- **Fail:** Audit log entries are missing, or details are incomplete/incorrect

---

## Test Case 8: Custom Disclosure URL Accessibility

**Objective:** Verify the custom disclosure URL is accessible to all target user populations (internal and external).

### Test Steps

1. **Prepare test environment:**
   - Identify the configured custom disclosure URL
   - Prepare test accounts for:
     - Internal user (on corporate network)
     - External user (off corporate network, VPN disconnected)
   - Document the expected URL and hosting location (SharePoint, public website, etc.)

2. **Execute test - Internal user:**
   - Sign in as an internal user on the corporate network
   - Open Microsoft 365 Copilot or a Copilot Studio agent
   - Click the custom disclosure URL link in the disclaimer or greeting

3. **Execute test - External user:**
   - Sign in as an external user off the corporate network (or a contractor/guest account)
   - Open Microsoft 365 Copilot or a Copilot Studio agent
   - Click the custom disclosure URL link in the disclaimer or greeting

4. **Expected Results:**
   - [ ] Internal users can access the custom disclosure URL without authentication errors
   - [ ] External users can access the custom disclosure URL (with authentication if required, but no access denied errors)
   - [ ] The policy document loads correctly in both scenarios
   - [ ] The document includes all required disclosure elements:
     - Description of AI system usage
     - Data handling and privacy practices
     - Monitoring and compliance notice
     - User rights and escalation path

5. **Evidence Collection:**
   - Screenshot of the policy document as accessed by an internal user
   - Screenshot of the policy document as accessed by an external user
   - URL of the policy document
   - Timestamp of test execution

### Pass/Fail Criteria

- **Pass:** Custom disclosure URL is accessible to both internal and external users, policy document loads correctly, and includes required elements
- **Fail:** URL is not accessible to external users, or policy document is missing required elements

---

## Test Case 9: Disclosure Version Tracking

**Objective:** Verify disclosure version numbers are tracked and consent records reference the correct version.

### Test Steps

1. **Prepare test environment:**
   - Document the current disclosure version number (e.g., "v1.0")
   - Create a test consent record with a known disclosure version
   - Update the disclosure language and increment the version number (e.g., "v1.1")

2. **Execute test:**
   - After updating disclosure language, have a test user acknowledge consent
   - Query Dataverse `fsi_aiconsent` table for the new consent record

3. **Expected Results:**
   - [ ] New consent record includes the updated disclosure version number (e.g., "v1.1")
   - [ ] Old consent records retain their original disclosure version number (e.g., "v1.0")
   - [ ] A version history document or table exists tracking disclosure language changes over time

4. **Evidence Collection:**
   - Dataverse query showing consent records with different disclosure versions
   - Version history document or table
   - Timestamp of test execution

### Pass/Fail Criteria

- **Pass:** Consent records reference the correct disclosure version, and version history is maintained
- **Fail:** Consent records do not include version numbers, or all records show the same version regardless of when they were created

---

## Test Case 10: Compliance Reporting

**Objective:** Verify PowerShell scripts generate accurate compliance reports for disclosure and consent coverage.

### Test Steps

1. **Prepare test environment:**
   - Ensure PowerShell scripts from the PowerShell Setup playbook are available
   - Prepare test data: agents with and without disclosure, users with and without consent

2. **Execute test:**
   - Run `Get-TenantAIDisclaimer.ps1` to retrieve tenant-wide configuration
   - Run `Get-AgentDisclosureInventory.ps1` to audit agent-level disclosure
   - Run `Get-ConsentRecords.ps1` to retrieve consent records (Zone 3)
   - Run `New-DisclosureComplianceReport.ps1` to generate a comprehensive report

3. **Expected Results:**
   - [ ] `Get-TenantAIDisclaimer.ps1` outputs the correct AI Disclaimer toggle status and custom URL
   - [ ] `Get-AgentDisclosureInventory.ps1` lists all agents with accurate disclosure status (Compliant/Review Required)
   - [ ] `Get-ConsentRecords.ps1` retrieves consent records with all required fields
   - [ ] `New-DisclosureComplianceReport.ps1` aggregates data into a single report with summary statistics
   - [ ] Reports are exported to CSV files for documentation

4. **Evidence Collection:**
   - PowerShell script output screenshots
   - Generated CSV files
   - Summary statistics (total agents, compliant agents, consent records count)
   - Timestamp of script execution

### Pass/Fail Criteria

- **Pass:** All scripts execute successfully, reports show accurate data, and CSV files are generated
- **Fail:** Scripts fail to execute, reports show incorrect data, or CSV export fails

---

## Evidence Collection Summary

For each test case, collect:
1. Screenshots of portal/app UI showing disclosure, consent prompts, or configuration
2. Dataverse query results for consent records
3. Purview audit log entries
4. PowerShell script output
5. CSV exports of compliance reports
6. Timestamp of test execution
7. Test user account information (username, role, zone classification)

Store all evidence in a governance documentation repository (e.g., SharePoint document library) with the naming convention:
```
Control-2.23_TestCase-[Number]_[Description]_[YYYYMMDD].png
Control-2.23_TestCase-[Number]_[Description]_[YYYYMMDD].csv
```

---

## Regression Testing

After configuration changes or Microsoft portal updates, re-run these test cases to verify:
- Tenant-wide AI Disclaimer still displays correctly (Test Case 1)
- Agent-level disclosure still appears in greeting topics (Test Case 2)
- Consent acknowledgment logic still functions (Test Case 3, 5)
- Purview audit logging still captures events (Test Case 7)

---

## Compliance Validation Checklist

After completing all test cases:

- [ ] Test Case 1: Tenant-wide AI Disclaimer displays with custom URL - PASS
- [ ] Test Case 2: Agent-level disclosure appears in greeting topics - PASS
- [ ] Test Case 3: Consent acknowledgment prompts function correctly (Zone 3) - PASS
- [ ] Test Case 4: Consent records are stored in Dataverse with required fields - PASS
- [ ] Test Case 5: Consent expiration triggers re-acknowledgment - PASS
- [ ] Test Case 6: Disclosure displays consistently across all platforms - PASS
- [ ] Test Case 7: Purview audit logging captures configuration and consent events - PASS
- [ ] Test Case 8: Custom disclosure URL is accessible to all user populations - PASS
- [ ] Test Case 9: Disclosure version numbers are tracked in consent records - PASS
- [ ] Test Case 10: Compliance reports generate accurate data - PASS

---

[Back to Control 2.23](../../../controls/pillar-2-management/2.23-user-consent-and-ai-disclosure-enforcement.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)
