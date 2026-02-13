# Troubleshooting: Control 3.12 - Agent Governance Exception and Override Management

**Last Updated:** February 2026
**Support Contacts:** Power Platform Admin team, Dataverse support

## Overview

This playbook provides solutions to common issues encountered when implementing and operating the agent governance exception management system.

---

## Issue 1: Exception Request Form Fails to Load

### Symptoms
- Power Apps form shows "Something went wrong" error
- Form loads but fields are blank/missing
- Cannot open form app from Power Apps portal

### Possible Causes
- Dataverse connection string incorrect
- Missing permissions on Governance Exceptions table
- Table schema changes not synchronized with app

### Resolution Steps

1. **Verify Dataverse Connection**
   - Open Power Apps → Apps → Agent Exception Request Form → Edit
   - Check **Data sources** panel
   - If Governance Exceptions shows with red error icon:
     - Remove the data source
     - Click **+ Add data** and re-add Governance Exceptions table
     - Click **Refresh** to sync latest schema

2. **Check User Permissions**
   - Navigate to Power Apps → Tables → Governance Exceptions → Settings → Security roles
   - Verify user's security role has:
     - **Create:** Organization (to submit requests)
     - **Read:** Organization (to view form)
   - If missing, grant appropriate permissions

3. **Verify Environment Selection**
   - Ensure form is opened in the same environment where Governance Exceptions table exists
   - Check environment selector in top-right corner of Power Apps portal

4. **Test with Simplified Form**
   - Create new test form with only 3 fields (Agent Name, Requestor, Exception Type)
   - If test form works, issue is with field configuration or validation formulas
   - Review OnChange and validation formulas for syntax errors

### Prevention
- Always test form after adding/modifying Dataverse columns
- Document environment-table mappings for troubleshooting
- Use version control for form exports

---

## Issue 2: Approval Workflow Not Triggering

### Symptoms
- Exception request submitted successfully but no approval email received
- Power Automate flow shows no recent runs
- Dataverse record remains in "Pending" status indefinitely

### Possible Causes
- Flow is turned off
- Trigger condition filtering out the record
- Connection to Dataverse expired/invalid
- Flow reached run quota limit

### Resolution Steps

1. **Verify Flow Is Enabled**
   - Navigate to Power Automate → My flows → Agent Exception Approval Workflow
   - Check status in top-right corner
   - If "Off", click **Turn on**

2. **Check Flow Run History**
   - Click on the flow name
   - Review **28-day run history**
   - If no runs appear after submission:
     - Issue is with trigger configuration
   - If runs appear but fail:
     - Open failed run and identify failing action

3. **Verify Trigger Configuration**
   - Edit the flow
   - Open **When a row is added, modified or deleted** trigger
   - Verify:
     - **Change type:** Added
     - **Table name:** Governance Exceptions
     - **Scope:** Organization (not User or Business Unit)
   - Test by manually creating a Dataverse record

4. **Check Dataverse Connection**
   - In flow editor, hover over Dataverse actions
   - If yellow warning icon appears: "This connection is not valid"
   - Delete connection and recreate with valid credentials

5. **Verify Flow Permissions**
   - Flow owner must have:
     - Dataverse System Administrator role (or custom role with full CRUD on Governance Exceptions)
     - Power Automate Premium license
   - If permissions missing, re-share flow with correct owner

6. **Check Run Quota**
   - Power Automate has daily run limits based on license
   - Navigate to Admin center → Analytics → Flows
   - If quota exceeded, flow will not trigger until quota resets

### Prevention
- Set up flow error notifications (Configure → Run only users → Notify when flow fails)
- Monitor flow analytics weekly
- Use service account with Premium license for production flows

---

## Issue 3: Wrong Approver Receives Email

### Symptoms
- Zone 3 exception sends approval to wrong person
- Approver email goes to generic mailbox instead of individual
- Approval email contains "Unknown user" for approver name

### Possible Causes
- Approver email hardcoded incorrectly in flow
- Approver lookup field not properly configured
- Zone classification mismatch in flow routing logic

### Resolution Steps

1. **Verify Zone-Based Routing Logic**
   - Edit flow
   - Find **Condition** action that checks Governance Zone
   - Verify zone values match Dataverse choice labels exactly:
     - "Zone 1 - Personal" (not "Zone 1" or "Personal")
     - "Zone 2 - Team"
     - "Zone 3 - Enterprise"

2. **Check Approver Email Configuration**
   - In **Start and wait for an approval** action
   - Verify **Assigned to** field uses:
     - Dynamic content from Dataverse (recommended): `Approver 1` lookup field
     - OR hardcoded email: Must be valid Entra ID user

3. **Update Approver Mapping**
   - If using hardcoded emails, create Dataverse configuration table:
     - Table: fsi_approverconfig
     - Columns: Zone (choice), ApproverLevel (choice), ApproverEmail (text)
   - Update flow to query configuration table based on zone

4. **Test with All Zones**
   - Submit test exception for Zone 1, 2, and 3
   - Verify each goes to correct approver(s)
   - Check email headers to confirm recipient matches expected approver

### Prevention
- Use Dataverse lookup fields for approvers instead of hardcoded emails
- Document approver assignments by zone in governance policy
- Test zone routing logic after any flow modifications

---

## Issue 4: Expiration Monitor Not Sending Alerts

### Symptoms
- Exceptions are expiring without warning emails
- Teams channel shows no expiration alerts
- PowerShell script runs successfully but no output

### Possible Causes
- Flow schedule disabled or incorrect time zone
- Filter query not matching expiring exceptions
- Email action failing silently
- Teams connector authentication expired

### Resolution Steps

1. **Check Flow Schedule**
   - Open Exception Expiration Monitor flow
   - Verify **Recurrence** trigger:
     - **Interval:** 1
     - **Frequency:** Day
     - **Time zone:** Correct for your organization
     - **At these hours/minutes:** 8:00 AM (or desired time)
   - Click **Test** → **Manually** to run immediately

2. **Verify Filter Query Syntax**
   - Edit flow
   - Open **List rows** action
   - Check **Filter rows** expression:
   ```
   fsi_approvalstatus eq 'Fully Approved' and 
   fsi_expirationdate le @{addDays(utcNow(), 7)} and
   fsi_expirationdate ge @{utcNow()}
   ```
   - Ensure date format matches Dataverse column format (ISO 8601: yyyy-MM-dd)

3. **Test Filter Query Manually**
   - Create test exception with expiration date = 5 days from today
   - Manually run flow
   - Check flow run history → **List rows** action output
   - If output count = 0, filter query is incorrect

4. **Check Email Action Configuration**
   - In **Send an email** action
   - Verify **To** field contains valid email address (dynamic content from loop item)
   - Test by replacing dynamic content with static test email

5. **Verify Teams Connection**
   - If Teams notifications not appearing:
     - Edit **Post adaptive card** action
     - Delete Teams connection and re-authenticate
     - Verify **Team** and **Channel** selections are correct

6. **Check for Action Failures in Run History**
   - Open recent flow run
   - Expand each action
   - Look for red X indicating failure
   - Review error message for specific issue (authentication, permissions, syntax)

### Prevention
- Schedule flow to run multiple times per day for critical notifications
- Set up flow failure alerts to notify admin team
- Test expiration monitor weekly with manually created test data

---

## Issue 5: PowerShell Script Connection Failures

### Symptoms
- `Connect-CrmOnline` fails with authentication error
- "Unable to connect to Dataverse" message
- Scripts timeout when querying large datasets

### Possible Causes
- Missing PowerShell modules
- Expired authentication token
- Firewall blocking connection to Dataverse URL
- Insufficient permissions on Dataverse environment

### Resolution Steps

1. **Verify Module Installation**
   ```powershell
   Get-Module -ListAvailable -Name Microsoft.Xrm.Data.PowerShell
   ```
   - If not found:
   ```powershell
   Install-Module -Name Microsoft.Xrm.Data.PowerShell -Scope CurrentUser -Force
   ```

2. **Test Connection Manually**
   ```powershell
   $conn = Connect-CrmOnline -ServerUrl "https://contoso.crm.dynamics.com"
   $conn.IsReady
   ```
   - If returns `False`, authentication failed
   - Re-run Connect-CrmOnline with `-InteractiveLogin` parameter to force new login

3. **Check Dataverse URL Format**
   - Ensure URL format is correct:
     - ✅ Correct: `https://orgname.crm.dynamics.com`
     - ❌ Incorrect: `https://make.powerapps.com` (this is Power Apps portal, not Dataverse)

4. **Verify User Permissions**
   - User running script must have:
     - Dataverse System Administrator role OR
     - Custom security role with Read access to Governance Exceptions table

5. **Use Service Principal for Automation**
   - For scheduled scripts, use service principal instead of user credentials:
   ```powershell
   $conn = Connect-CrmOnline `
       -ServerUrl "https://contoso.crm.dynamics.com" `
       -ClientId "app-registration-id" `
       -ClientSecret "secret"
   ```

6. **Handle Timeouts for Large Datasets**
   - If script times out on large exception registers:
   - Add paging to FetchXML query:
   ```xml
   <fetch page="1" count="500">
     <!-- query definition -->
   </fetch>
   ```
   - Implement loop to retrieve multiple pages

### Prevention
- Document service principal setup for automation
- Test scripts in non-production environment first
- Implement retry logic for transient connection failures

---

## Issue 6: Dataverse Table Missing or Not Found

### Symptoms
- Power Apps shows "Table not found: fsi_governanceexception"
- PowerShell script error: "Entity 'fsi_governanceexception' not found"
- Flow trigger cannot find Governance Exceptions table

### Possible Causes
- Table created in different environment
- Table name/schema name mismatch
- Table was deleted or renamed
- User viewing wrong environment

### Resolution Steps

1. **Verify Table Exists**
   - Navigate to Power Apps → Tables
   - Ensure correct environment selected (top-right dropdown)
   - Search for "Governance Exceptions"
   - If not found, table does not exist in this environment

2. **Check Table Schema Name**
   - If table exists but shows different name:
   - Click on table → Settings → Properties
   - Verify **Name (schema name)**: Should be `fsi_governanceexception`
   - If different, update all references in flows and scripts

3. **Recreate Table if Deleted**
   - Follow [Portal Walkthrough](portal-walkthrough.md) steps to recreate table
   - Re-import any backed-up data

4. **Verify Environment Consistency**
   - Ensure all components (table, form, flows) are in same environment:
     - Dataverse table: Environment X
     - Power Apps form: Environment X
     - Power Automate flows: Environment X
   - If mismatched, export/import components to correct environment

### Prevention
- Use solution packages to deploy related components together
- Document environment architecture (dev, test, prod)
- Implement change control for table modifications

---

## Issue 7: Approval Status Not Updating

### Symptoms
- Approver clicks "Approve" but Dataverse record stays "Pending"
- Multiple approvals but status does not progress (e.g., stuck at "Level 1 Approved")
- Dataverse shows update error in flow run history

### Possible Causes
- Flow does not have write permissions to Dataverse
- Update action targeting wrong record
- Choice label mismatch between flow and Dataverse
- Concurrent update conflict

### Resolution Steps

1. **Check Flow Run History**
   - Open flow run where approval occurred
   - Expand **Update a row** action
   - Review output:
     - If green checkmark: Update succeeded (issue is elsewhere)
     - If red X: Read error message

2. **Verify Row ID Parameter**
   - In **Update a row** action
   - **Row ID** must be: `fsi_governanceexceptionid` from trigger (not static GUID)

3. **Check Choice Label Values**
   - In Dataverse, go to Tables → Governance Exceptions → Columns → Approval Status
   - Click on column → Edit
   - Verify choice labels match exactly what flow is setting:
     - "Pending"
     - "Level 1 Approved"
     - "Level 2 Approved"
     - "Fully Approved"
   - If labels differ, update flow or Dataverse to match

4. **Test Update Action Manually**
   - Add **Compose** action after **Update a row**
   - Set inputs to: `outputs('Update_a_row')`
   - Run flow and review Compose output for detailed response

5. **Handle Concurrent Updates**
   - If multiple flows modify same record simultaneously:
   - Add **Delay** action before update (e.g., 2 seconds)
   - Or implement optimistic concurrency check

### Prevention
- Use dynamic content for all Dataverse references (no hardcoded values)
- Test flows in isolated test environment before production deployment
- Document exact choice label values

---

## Issue 8: Teams Notifications Not Appearing

### Symptoms
- Approval completes successfully but no Teams adaptive card posted
- Teams channel exists but bot posts are not visible
- Flow shows Teams action succeeded but message not found

### Possible Causes
- Incorrect Team or Channel selection
- Flow bot not added to Teams channel
- Adaptive card JSON syntax error
- User permissions to view channel

### Resolution Steps

1. **Verify Team and Channel Selection**
   - Edit flow
   - Open **Post adaptive card** action
   - Click on **Team** dropdown:
     - If "Custom value" selected, Teams ID may be incorrect
     - Select team from dropdown list instead
   - Click on **Channel** dropdown and select from list

2. **Add Flow Bot to Channel**
   - Open Microsoft Teams
   - Navigate to target team and channel
   - Click **...** → **Manage channel** → **Settings** → **Apps**
   - Verify "Flow" or "Power Automate" app is installed
   - If missing, add app to team

3. **Test Adaptive Card JSON**
   - Copy adaptive card JSON from flow
   - Paste into [Adaptive Card Designer](https://adaptivecards.io/designer/)
   - Verify card renders without errors
   - Fix any syntax issues (missing commas, invalid schema version)

4. **Check Channel Permissions**
   - Verify user has access to view the channel
   - Some organizations restrict bot posts
   - Contact Teams admin to verify bot posting is allowed

5. **Alternative: Use Simple Teams Message**
   - If adaptive cards not working, replace with simpler action:
   - Use **Post message in a chat or channel** (not adaptive card)
   - Send plain text notification to test connectivity

### Prevention
- Test Teams notifications in non-production channel first
- Save working adaptive card JSON as template
- Monitor Teams admin policies for bot posting restrictions

---

## Issue 9: SHA-256 Hash Verification Fails

### Symptoms
- Hash from certutil does not match SHA256_HASH.txt
- Evidence export script completes but hash file is empty
- Hash changes between generations of same data

### Possible Causes
- File modified after hash generation
- Character encoding differences (UTF-8 vs. UTF-8 with BOM)
- Line ending differences (CRLF vs. LF)
- PowerShell script error during hash calculation

### Resolution Steps

1. **Verify File Not Modified**
   - Check file modification timestamp
   - If modified after hash generation, hash will not match
   - Regenerate hash after any file changes

2. **Check Character Encoding**
   - In PowerShell export script:
   ```powershell
   Export-Csv -Path $outputFile -NoTypeInformation -Encoding UTF8
   ```
   - Ensure `-Encoding UTF8` parameter is specified
   - Some editors add BOM (Byte Order Mark) which changes hash

3. **Test Hash Calculation**
   ```powershell
   $hash = Get-FileHash -Path "ExceptionRegister.csv" -Algorithm SHA256
   $hash.Hash.ToLower()
   ```
   - Compare to script-generated hash
   - If different, script has bug in hash calculation

4. **Verify certutil Output Format**
   - Run: `certutil -hashfile ExceptionRegister.csv SHA256`
   - Output format:
   ```
   SHA256 hash of ExceptionRegister.csv:
   a1b2c3d4...
   CertUtil: -hashfile command completed successfully.
   ```
   - Copy only the hex hash line (not header or footer)

5. **Use PowerShell for Verification Instead**
   ```powershell
   $scriptHash = Get-Content "SHA256_HASH.txt" | Select-Object -First 1 | ForEach-Object { $_.Split()[0] }
   $fileHash = (Get-FileHash -Path "ExceptionRegister.csv" -Algorithm SHA256).Hash.ToLower()
   if ($scriptHash -eq $fileHash) { Write-Host "✓ Hash verified" -ForegroundColor Green }
   ```

### Prevention
- Document hash verification procedure in audit guide
- Test evidence export process quarterly
- Store evidence files as read-only to prevent accidental modification

---

## Issue 10: High Renewal Counts Not Flagged

### Symptoms
- Exception has 4 renewals but compliance report shows "Compliant"
- Renewal count not incrementing when exceptions are extended
- Compliance script does not detect renewal limit violations

### Possible Causes
- Renewal count column not updated when extending exception
- Compliance script checking wrong threshold
- Manual record edits bypassing renewal workflow

### Resolution Steps

1. **Implement Renewal Workflow**
   - Create separate Power Automate flow: "Exception Renewal Workflow"
   - Trigger: When Expiration Date is modified and status = "Fully Approved"
   - Action: Increment Renewal Count by 1
   - Action: Check if Renewal Count > 2, if yes set status to "Expired - Max Renewals"

2. **Audit Existing Renewal Counts**
   ```powershell
   # Query all exceptions with renewal count > 2
   $fetchXml = @"
   <fetch>
     <entity name="fsi_governanceexception">
       <attribute name="fsi_name" />
       <attribute name="fsi_renewalcount" />
       <filter>
         <condition attribute="fsi_renewalcount" operator="gt" value="2" />
       </filter>
     </entity>
   </fetch>
   "@
   ```
   - Review and remediate violations

3. **Update Compliance Script Threshold**
   - In Get-ExceptionComplianceReport.ps1
   - Verify line:
   ```powershell
   if ($record.fsi_renewalcount -gt 2) {
       $issues += "Renewal count exceeds limit..."
   }
   ```
   - Ensure threshold matches policy (2 renewals = 3 total approval periods)

4. **Document Renewal Process**
   - Create governance procedure: "Exception Renewal Request"
   - Require:
     - Updated justification
     - New risk assessment
     - Approval from original approvers
     - Automatic increment of renewal count

### Prevention
- Automate renewal count updates via Power Automate
- Restrict direct Dataverse editing to prevent bypass
- Include renewal count in all reporting dashboards

---

## General Troubleshooting Tips

### Enable Detailed Logging

For Power Automate flows:
1. Add **Compose** actions after each major step
2. Set inputs to output of previous action
3. Review run history to see intermediate values

For PowerShell scripts:
```powershell
# Add at start of script
$VerbosePreference = "Continue"
$DebugPreference = "Continue"

# Add throughout script
Write-Verbose "Connecting to Dataverse at $(Get-Date)"
Write-Debug "Query returned $($results.Count) records"
```

### Common Error Messages

| Error Message | Likely Cause | Solution |
|---------------|--------------|----------|
| "Principal user is missing prvReadUser privilege" | Insufficient Dataverse permissions | Grant Read user privilege in security role |
| "The requested operation requires a connection" | Flow connection expired | Re-authenticate connection in flow |
| "Invalid FetchXML" | FetchXML syntax error | Validate XML structure, check attribute names |
| "Approval action timed out" | Approver did not respond within timeout period | Increase timeout or remind approver to respond |
| "Adaptive card schema version not supported" | Teams doesn't support card version | Change to version 1.4 or lower |

---

## Escalation Paths

If issues cannot be resolved using this guide:

1. **Power Apps/Dataverse Issues**
   - Contact: Microsoft Support via Admin Center → Support → New service request
   - Required info: Environment ID, table name, error messages, screenshots

2. **Power Automate Issues**
   - Contact: Microsoft Support
   - Required info: Flow name, run ID, error details, flow export (.zip)

3. **Governance Policy Questions**
   - Contact: AI Governance Lead or Compliance Officer
   - Review: Exception management policy document

4. **Technical Assistance**
   - Contact: Internal Power Platform Admin team
   - Escalate to Microsoft FastTrack if available

---

## Additional Resources

- [Power Platform Admin Center Troubleshooting](https://learn.microsoft.com/en-us/power-platform/admin/troubleshooting)
- [Power Automate Flow Troubleshooting](https://learn.microsoft.com/en-us/power-automate/fix-flow-failures)
- [Dataverse Connection Issues](https://learn.microsoft.com/en-us/powershell/module/microsoft.xrm.data.powershell/)
- [Adaptive Cards Debugging](https://adaptivecards.io/designer/)

---

[Back to Control 3.12](../../../controls/pillar-3-reporting/3.12-agent-governance-exception-and-override-management.md)
