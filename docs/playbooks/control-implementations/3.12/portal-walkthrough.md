# Portal Walkthrough: Control 3.12 - Agent Governance Exception and Override Management

**Last Updated:** April 2026
**Portal:** Power Apps, Power Automate, Microsoft Teams, SharePoint
**Estimated Time:** 90-120 minutes

## Prerequisites

- [ ] Power Platform Admin role or Power Apps Environment Maker role
- [ ] Power Automate Premium license (for approval flows and Dataverse)
- [ ] Access to Dataverse environment (or SharePoint site for lightweight implementation)
- [ ] Microsoft Teams access for notifications
- [ ] Exception management policy documented (exception types, approval authorities, maximum durations)
- [ ] Understanding of governance zone classifications (Control 2.2)
- [ ] Change management process for policy overrides
- [ ] List of approvers by zone (manager, compliance officer, CISO)

---

## Step-by-Step Configuration

### Part 1: Create Dataverse Exception Register Table

#### Step 1: Navigate to Power Apps Maker Portal

1. Open [Power Apps](https://make.powerapps.com)
2. Sign in with your credentials
3. In the top-right corner, select your **Dataverse environment** (use a dedicated governance environment, not Zone 3 production)
4. In the left navigation, click **Tables**
5. Review the existing tables to confirm no exception tracking table exists

> **Environment Selection:** Use a dedicated governance or default environment for exception tracking. Do not create governance tables in Zone 3 production environments to maintain separation between operational and governance data.

#### Step 2: Create Custom Table for Exception Tracking

1. Click **+ New table** → **Set advanced properties**
2. Configure table properties:
   - **Display name:** Governance Exceptions
   - **Plural name:** Governance Exceptions
   - **Name (schema name):** fsi_governanceexception (or your prefix)
   - **Description:** Tracks agent governance policy exceptions with approval workflow and expiration monitoring
   - **Type:** Standard
   - **Enable attachments:** Yes (for supporting documentation)
   - **Track changes:** Yes (required for audit trail)
   - **Audit changes to its data:** Yes (required for compliance)
3. Click **Save**

The system creates the table with default columns: Name, Created On, Created By, Modified On, Modified By, Owner, Status, Status Reason.

#### Step 3: Add Custom Columns to Exception Table

Add the following columns to track exception lifecycle:

**Column 1: Exception Request Date**

1. Click **+ New** → **Column**
2. Configure:
   - **Display name:** Exception Request Date
   - **Data type:** Date and time
   - **Format:** Date only
   - **Behavior:** User local (timezone-aware)
   - **Required:** Business required
   - **Searchable:** Yes
3. Click **Save**

**Column 2: Requestor**

1. Click **+ New** → **Column**
2. Configure:
   - **Display name:** Requestor
   - **Data type:** Lookup
   - **Related table:** User
   - **Required:** Business required
3. Click **Save**

**Column 3: Agent Name**

1. Click **+ New** → **Column**
2. Configure:
   - **Display name:** Agent Name
   - **Data type:** Text
   - **Format:** Text
   - **Maximum length:** 255
   - **Required:** Business required
   - **Searchable:** Yes
3. Click **Save**

**Column 4: Governance Zone**

1. Click **+ New** → **Column**
2. Configure:
   - **Display name:** Governance Zone
   - **Data type:** Choice
   - **Choices:** 
     - Zone 1 - Personal
     - Zone 2 - Team
     - Zone 3 - Enterprise
   - **Required:** Business required
3. Click **Save**

**Column 5: Exception Type**

1. Click **+ New** → **Column**
2. Configure:
   - **Display name:** Exception Type
   - **Data type:** Choice
   - **Choices:**
     - Policy Override
     - Approval Bypass
     - Inventory Grace Period
     - Environment Reclassification
     - Risk Acceptance
     - Other
   - **Required:** Business required
3. Click **Save**

**Column 6: Business Justification**

1. Click **+ New** → **Column**
2. Configure:
   - **Display name:** Business Justification
   - **Data type:** Text
   - **Format:** Text area (multiline)
   - **Maximum length:** 4000
   - **Required:** Business required
3. Click **Save**

**Column 7: Risk Assessment**

1. Click **+ New** → **Column**
2. Configure:
   - **Display name:** Risk Assessment
   - **Data type:** Text
   - **Format:** Text area (multiline)
   - **Maximum length:** 4000
   - **Required:** Business required
3. Click **Save**

**Column 8: Compensating Controls**

1. Click **+ New** → **Column**
2. Configure:
   - **Display name:** Compensating Controls
   - **Data type:** Text
   - **Format:** Text area (multiline)
   - **Maximum length:** 4000
   - **Required:** Business required
3. Click **Save**

**Column 9: Approval Status**

1. Click **+ New** → **Column**
2. Configure:
   - **Display name:** Approval Status
   - **Data type:** Choice
   - **Choices:**
     - Pending
     - Level 1 Approved
     - Level 2 Approved
     - Fully Approved
     - Denied
     - Expired
     - Closed
   - **Default value:** Pending
   - **Required:** Business required
3. Click **Save**

**Column 10-12: Approver 1, 2, 3 (Repeat for each level)**

1. Click **+ New** → **Column**
2. Configure:
   - **Display name:** Approver 1 (Manager)
   - **Data type:** Lookup
   - **Related table:** User
   - **Required:** Optional (populated during approval)
3. Click **Save**
4. Repeat for **Approver 2 (Compliance)** and **Approver 3 (CISO)**

**Column 13-15: Approval Date 1, 2, 3 (Repeat for each level)**

1. Click **+ New** → **Column**
2. Configure:
   - **Display name:** Approval Date 1
   - **Data type:** Date and time
   - **Format:** Date only
   - **Required:** Optional
3. Click **Save**
4. Repeat for **Approval Date 2** and **Approval Date 3**

**Column 16: Expiration Date**

1. Click **+ New** → **Column**
2. Configure:
   - **Display name:** Expiration Date
   - **Data type:** Date and time
   - **Format:** Date only
   - **Required:** Business required
3. Click **Save**

**Column 17: Renewal Count**

1. Click **+ New** → **Column**
2. Configure:
   - **Display name:** Renewal Count
   - **Data type:** Whole number
   - **Minimum value:** 0
   - **Maximum value:** 10
   - **Default value:** 0
   - **Required:** Business required
3. Click **Save**

**Column 18: Closure Date**

1. Click **+ New** → **Column**
2. Configure:
   - **Display name:** Closure Date
   - **Data type:** Date and time
   - **Format:** Date only
   - **Required:** Optional
3. Click **Save**

**Column 19: Closure Reason**

1. Click **+ New** → **Column**
2. Configure:
   - **Display name:** Closure Reason
   - **Data type:** Text
   - **Format:** Text area (multiline)
   - **Maximum length:** 2000
   - **Required:** Optional
3. Click **Save**

#### Step 4: Configure Security Roles for Exception Table

1. In Power Apps, go to **Settings** (gear icon) → **Advanced settings**
2. Navigate to **Settings** → **Security** → **Security Roles**
3. Select the **System Administrator** role (or create a custom **Governance Admin** role)
4. In the **Custom Entities** tab, find **Governance Exceptions**
5. Grant the following privileges:
   - **Create:** Organization (all users can submit exception requests)
   - **Read:** Organization (all users can view exception status)
   - **Write:** Business Unit (only governance team can edit)
   - **Delete:** None (prevent accidental deletion; use closure instead)
   - **Append:** Organization
   - **Append To:** Organization
6. Click **Save and Close**

> **Principle of Least Privilege:** Grant broad Create and Read access to allow all users to submit and view exceptions, but restrict Write and Delete to governance administrators to prevent unauthorized modifications.

---

### Part 2: Build Exception Request Form in Power Apps

#### Step 5: Create Canvas App for Exception Request

1. In Power Apps, click **+ Create** → **Canvas app from blank**
2. Configure:
   - **App name:** Agent Exception Request Form
   - **Format:** Tablet (recommended for form-based apps)
3. Click **Create**

#### Step 6: Connect to Dataverse Exception Table

1. In the app editor, click **Data** (database icon) in the left toolbar
2. Click **+ Add data**
3. Search for **Governance Exceptions**
4. Select the table to add as a data source
5. Verify the connection shows all custom columns

#### Step 7: Design Exception Request Form

1. Click **Insert** → **Forms** → **Edit form**
2. Resize the form to fill the screen (leave space for header and submit button)
3. In the form properties pane:
   - **Data source:** Governance Exceptions
   - **Item:** Blank() (for new record creation)
   - **Default mode:** New
4. Click **Edit fields** and add the following fields:
   - Exception Request Date
   - Requestor (default to User().Email)
   - Agent Name
   - Governance Zone
   - Exception Type
   - Business Justification
   - Risk Assessment
   - Compensating Controls
   - Expiration Date
5. Reorder fields in logical flow (requestor info → exception details → risk → expiration)

#### Step 8: Configure Field Validation and Defaults

**Requestor Field:**

1. Select the **Requestor** card in the form
2. Set **Default:** `User().Email` (auto-populate with current user)
3. Set **DisplayMode:** `DisplayMode.View` (read-only)

**Exception Request Date Field:**

1. Select the **Exception Request Date** card
2. Set **Default:** `Today()` (auto-populate with current date)
3. Set **DisplayMode:** `DisplayMode.View` (read-only)

**Expiration Date Field:**

1. Select the **Expiration Date** card
2. Add a **Label** below the date picker:
   - **Text:** `"Maximum duration: " & If(GovernanceZoneDropdown.Selected.Value = "Zone 3", "30 days", If(GovernanceZoneDropdown.Selected.Value = "Zone 2", "60 days", "90 days"))`
3. Set **OnChange** for the date picker:
   ```powerFx
   If(
       DateDiff(Today(), ExpirationDatePicker.SelectedDate, Days) > 
       If(GovernanceZoneDropdown.Selected.Value = "Zone 3", 30,
          If(GovernanceZoneDropdown.Selected.Value = "Zone 2", 60, 90)),
       Notify("Expiration date exceeds maximum duration for selected zone", NotificationType.Error),
       false
   )
   ```

**Business Justification Field:**

1. Select the **Business Justification** card
2. Add validation to require minimum length:
   - Set **Required:** true
   - Add character count label: `"Characters: " & Len(JustificationTextInput.Text) & " / 100 minimum"`

#### Step 9: Add Submit Button and Workflow Trigger

1. Click **Insert** → **Button**
2. Position button at bottom of form
3. Configure button:
   - **Text:** "Submit Exception Request"
   - **OnSelect:**
   ```powerFx
   If(
       Len(JustificationTextInput.Text) >= 100 && 
       Len(RiskAssessmentTextInput.Text) >= 100 &&
       Len(CompensatingControlsTextInput.Text) >= 50,
       SubmitForm(ExceptionForm);
       Notify("Exception request submitted successfully. You will receive approval notifications via email.", NotificationType.Success);
       ResetForm(ExceptionForm),
       Notify("Please complete all required fields with sufficient detail.", NotificationType.Error)
   )
   ```

#### Step 10: Save and Publish Canvas App

1. Click **File** → **Save**
2. Click **Publish** → **Publish this version**
3. Click **Share** and grant access to all users who may need to request exceptions
4. Test the form by submitting a sample exception request

> **Testing Tip:** Create a test record with all fields populated. Verify it appears in the Dataverse table by navigating to **Tables** → **Governance Exceptions** → **Data**.

---

### Part 3: Build Multi-Level Approval Flow in Power Automate

#### Step 11: Create Approval Flow for Exception Requests

1. Open [Power Automate](https://make.powerautomate.com)
2. Select the same environment as your Dataverse table
3. Click **+ Create** → **Automated cloud flow**
4. Configure:
   - **Flow name:** Agent Exception Approval Workflow
   - **Trigger:** When a row is added, modified or deleted (Dataverse)
   - **Change type:** Added
   - **Table name:** Governance Exceptions
5. Click **Create**

#### Step 12: Add Condition to Filter New Requests

1. Add action: **Condition**
2. Configure:
   - **Left operand:** `Approval Status` (from trigger)
   - **Operator:** is equal to
   - **Right operand:** Pending
3. In the **Yes** branch, continue building the approval workflow

#### Step 13: Configure Zone-Based Approval Routing

1. In the **Yes** branch, add action: **Condition** (to check zone)
2. Configure:
   - **Left operand:** `Governance Zone` (from trigger)
   - **Operator:** is equal to
   - **Right operand:** Zone 1

**Zone 1 Branch (Single Approval):**

1. Add action: **Start and wait for an approval**
2. Configure:
   - **Approval type:** Approve/Reject - First to respond
   - **Title:** `"Agent Exception Request: " & Agent Name`
   - **Assigned to:** (Power Platform Admin email)
   - **Details:**
   ```
   Requestor: [Requestor Email]
   Agent Name: [Agent Name]
   Exception Type: [Exception Type]
   Justification: [Business Justification]
   Risk Assessment: [Risk Assessment]
   Compensating Controls: [Compensating Controls]
   Expiration Date: [Expiration Date]
   ```
   - **Item link:** Link to Dataverse record (for review)
3. Add action: **Condition** (check approval outcome)
4. Configure:
   - **Left operand:** `Outcome` (from approval action)
   - **Operator:** is equal to
   - **Right operand:** Approve
5. In **Yes** branch:
   - Add action: **Update a row** (Dataverse)
   - **Table:** Governance Exceptions
   - **Row ID:** (from trigger)
   - **Approval Status:** Fully Approved
   - **Approver 1:** (Approver email from approval action)
   - **Approval Date 1:** `utcNow()`
6. In **No** branch:
   - Add action: **Update a row** (Dataverse)
   - **Approval Status:** Denied

**Zone 2 Branch (Two-Level Approval):**

1. Duplicate Zone 1 logic but add second approval stage
2. After Level 1 approval, update status to "Level 1 Approved"
3. Add second **Start and wait for an approval** action
   - **Assigned to:** (Compliance Officer email)
   - **Title and Details:** Same as Level 1, plus "Level 1 approved by [Approver 1]"
4. After Level 2 approval, update status to "Fully Approved"

**Zone 3 Branch (Three-Level Approval):**

1. Duplicate Zone 2 logic but add third approval stage
2. After Level 2 approval, update status to "Level 2 Approved"
3. Add third **Start and wait for an approval** action
   - **Assigned to:** (CISO email)
4. After Level 3 approval, update status to "Fully Approved"

#### Step 14: Add Teams Notification for Approved Exceptions

1. After all zone branches converge, add action: **Post adaptive card in a chat or channel**
2. Configure:
   - **Post as:** Flow bot
   - **Post in:** Channel
   - **Team:** (Governance Team)
   - **Channel:** Agent Governance Alerts
   - **Adaptive Card:**
   ```json
   {
       "type": "AdaptiveCard",
       "body": [
           {
               "type": "TextBlock",
               "size": "Large",
               "weight": "Bolder",
               "text": "✅ Exception Approved",
               "color": "Good"
           },
           {
               "type": "FactSet",
               "facts": [
                   {"title": "Agent Name", "value": "${triggerOutputs()?['body/fsi_agentname']}"},
                   {"title": "Requestor", "value": "${triggerOutputs()?['body/_fsi_requestor_value']}"},
                   {"title": "Exception Type", "value": "${triggerOutputs()?['body/fsi_exceptiontype']}"},
                   {"title": "Expiration Date", "value": "${triggerOutputs()?['body/fsi_expirationdate']}"},
                   {"title": "Approvers", "value": "${body('Level_1_Approval')?['responder']}"}
               ]
           }
       ],
       "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
       "version": "1.4"
   }
   ```

#### Step 15: Save and Test Approval Flow

1. Click **Save** to save the flow
2. Test by submitting a new exception request via the Power Apps form
3. Verify:
   - Approval email is sent to appropriate approver(s)
   - Approver can approve/reject from email or Power Automate approval center
   - Dataverse record updates with approval status and approver details
   - Teams notification is posted for approved exceptions

---

### Part 4: Configure Expiration Monitoring and Alerts

#### Step 16: Create Scheduled Flow for Expiration Alerts

1. In Power Automate, click **+ Create** → **Scheduled cloud flow**
2. Configure:
   - **Flow name:** Exception Expiration Monitor
   - **Recurrence:** Daily at 8:00 AM
3. Click **Create**

#### Step 17: Query Active Exceptions Nearing Expiration

1. Add action: **List rows** (Dataverse)
2. Configure:
   - **Table:** Governance Exceptions
   - **Filter rows:**
   ```
   fsi_approvalstatus eq 'Fully Approved' and 
   fsi_expirationdate le @{addDays(utcNow(), 7)} and
   fsi_expirationdate ge @{utcNow()}
   ```
   - This filters for approved exceptions expiring within 7 days

#### Step 18: Send Expiration Alerts

1. Add action: **Apply to each** (loop through filtered exceptions)
2. Inside loop, add action: **Send an email (V2)**
3. Configure:
   - **To:** (Requestor email from loop item)
   - **CC:** (Approver 1, Approver 2, Approver 3)
   - **Subject:** `"URGENT: Agent Exception Expiring in " & dateDifference(utcNow(), item()?['fsi_expirationdate'], 'Day') & " days"`
   - **Body:**
   ```html
   <p>Your agent governance exception is expiring soon.</p>
   <p><strong>Agent Name:</strong> [Agent Name]</p>
   <p><strong>Exception Type:</strong> [Exception Type]</p>
   <p><strong>Expiration Date:</strong> [Expiration Date]</p>
   <p><strong>Action Required:</strong> If the underlying issue has been remediated, close the exception in Dataverse. If additional time is needed, submit a renewal request with updated justification.</p>
   <p><strong>Renewal Limit:</strong> Maximum 2 renewals allowed. Current renewal count: [Renewal Count]</p>
   ```

#### Step 19: Post Teams Alert for Expiring Exceptions

1. Inside the **Apply to each** loop, add action: **Post adaptive card in a chat or channel**
2. Configure:
   - **Post as:** Flow bot
   - **Post in:** Channel
   - **Team:** (Governance Team)
   - **Channel:** Agent Governance Alerts
   - **Adaptive Card:** (similar to approval notification, but with "⚠️ Exception Expiring Soon" title and orange warning color)

#### Step 20: Save and Test Expiration Monitor

1. Click **Save**
2. Test by creating a test exception record with expiration date set to 5 days from now
3. Manually run the flow (click **Test** → **Manually** → **Run flow**)
4. Verify email and Teams notifications are sent

---

### Part 5: Build Exception Dashboard in Power BI (Optional)

#### Step 21: Connect Power BI to Dataverse Exception Table

1. Open **Power BI Desktop**
2. Click **Get Data** → **Dataverse**
3. Enter your environment URL (e.g., `https://org.crm.dynamics.com/`)
4. Select **Governance Exceptions** table
5. Click **Load** to import data

#### Step 22: Create Exception Metrics Visuals

**Active Exceptions by Zone:**

1. Add visual: **Clustered column chart**
2. Configure:
   - **Axis:** Governance Zone
   - **Values:** Count of Exception ID
   - **Legend:** Approval Status
3. Filter to show only "Fully Approved" status

**Exceptions by Type:**

1. Add visual: **Pie chart**
2. Configure:
   - **Legend:** Exception Type
   - **Values:** Count of Exception ID

**Expiring Exceptions (Next 30 Days):**

1. Add visual: **Table**
2. Configure:
   - **Columns:** Agent Name, Requestor, Exception Type, Expiration Date, Days Until Expiration
   - **Filter:** Expiration Date is in next 30 days
   - **Sort:** Days Until Expiration (ascending)

**Renewal Count Distribution:**

1. Add visual: **Clustered bar chart**
2. Configure:
   - **Axis:** Renewal Count
   - **Values:** Count of Exception ID

#### Step 23: Publish Dashboard and Schedule Refresh

1. Click **File** → **Publish** → **Publish to Power BI**
2. Select workspace (e.g., "Agent Governance Workspace")
3. In Power BI Service, configure scheduled refresh (daily at 6:00 AM)
4. Share dashboard with governance team and senior leadership

---

## Verification Steps

After completing the portal walkthrough, verify the exception management system:

1. **Dataverse Table Verification:**
   - Navigate to **Tables** → **Governance Exceptions** → **Data**
   - Verify table exists with all custom columns
   - Confirm audit tracking is enabled (check table settings)

2. **Power Apps Form Verification:**
   - Open the exception request form app
   - Submit a test request with valid data
   - Verify form validation works (minimum character counts, expiration date limits)
   - Check that record appears in Dataverse after submission

3. **Approval Flow Verification:**
   - Submit exception requests for Zone 1, Zone 2, and Zone 3
   - Verify correct number of approval stages (1, 2, or 3)
   - Confirm approvers receive email notifications
   - Test approval and denial workflows
   - Verify Dataverse record updates with approval status and dates

4. **Expiration Monitoring Verification:**
   - Create test exception with expiration date 5 days from now
   - Manually run the expiration monitor flow
   - Verify email notifications are sent to requestor and approvers
   - Check Teams channel for expiration alerts

5. **Dashboard Verification (if implemented):**
   - Open Power BI dashboard
   - Verify all visuals display current exception data
   - Check that scheduled refresh is configured and succeeds

---

## Best Practices

- **Naming Conventions:** Use consistent naming for Dataverse columns (fsi_ prefix) and flows (include "Agent Exception" for easy searching)
- **Documentation:** Maintain a configuration guide documenting approver assignments, zone duration limits, and renewal policies
- **Testing:** Test all approval paths (Zone 1, 2, 3) and edge cases (denial, expiration, renewal) before go-live
- **Training:** Train governance team and frequent requestors on exception request process and approval workflows
- **Monitoring:** Review exception metrics weekly to identify trends and systemic issues requiring policy updates

---

## Next Steps

- Proceed to [PowerShell Setup](powershell-setup.md) for automated exception reporting and audit trail export
- Review [Verification & Testing](verification-testing.md) for comprehensive test cases
- Consult [Troubleshooting](troubleshooting.md) if you encounter issues during implementation

---

[Back to Control 3.12](../../../controls/pillar-3-reporting/3.12-agent-governance-exception-and-override-management.md)

*Updated: April 2026 | Version: v1.3*
