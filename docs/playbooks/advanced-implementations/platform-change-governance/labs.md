# Platform Change Governance - Hands-On Labs

**Status:** January 2026 - FSI-AgentGov v1.2
**Total Duration:** 5-6 hours across 3 labs

---

## Overview

These hands-on labs guide you through building the Platform Change Governance solution from scratch. Each lab builds on the previous, creating a complete governance system by the end.

| Lab | Duration | Focus | Prerequisite |
|-----|----------|-------|--------------|
| Lab 1 | 45 min | Message Center Ingestion | None |
| Lab 2 | 2 hours | Path A Baseline (Model-Driven App) | Lab 1 |
| Lab 3 | 2 hours | Path B Integration (Azure DevOps) | Lab 2 |

---

## Lab 1: Message Center Ingestion

**Objective:** Build non-production ingestion pipeline from Microsoft Graph API to Dataverse

**Duration:** 45 minutes

### Prerequisites

- Power Platform environment (Developer or Sandbox)
- Azure AD tenant with Entra Global Admin or Entra App Admin role
- Microsoft 365 E3/E5 licenses

---

### Phase 1: Azure App Registration (15 minutes)

**Step 1.1:** Navigate to Azure Portal

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Azure Active Directory** → **App registrations**
3. Click **New registration**

**Step 1.2:** Configure App Registration

```
Name: MessageCenterAPI_Lab
Supported account types: Accounts in this organizational directory only (Single tenant)
Redirect URI: (leave blank)
```

4. Click **Register**

**Step 1.3:** Note Application Details

Record these values (you'll need them later):

| Value | Location |
|-------|----------|
| Application (client) ID | Overview page |
| Directory (tenant) ID | Overview page |

**Step 1.4:** Create Client Secret

1. Go to **Certificates & secrets** → **Client secrets**
2. Click **New client secret**
3. Description: `Lab Secret`
4. Expires: 90 days (sufficient for lab)
5. Click **Add**
6. **Immediately copy the secret value** (shown only once)

**Step 1.5:** Configure API Permissions

1. Go to **API permissions**
2. Click **Add a permission**
3. Select **Microsoft Graph**
4. Select **Application permissions**
5. Search for and add: `ServiceMessage.Read.All`
6. Click **Add permissions**
7. Click **Grant admin consent for [tenant]**
8. Verify status shows green checkmark

!!! success "Checkpoint"
    You should have: Application ID, Tenant ID, Client Secret, and `ServiceMessage.Read.All` permission with admin consent.

---

### Phase 2: Dataverse Schema Setup (15 minutes)

**Step 2.1:** Create Solution

1. Go to [Power Apps Maker Portal](https://make.powerapps.com)
2. Select your lab environment
3. Go to **Solutions** → **New solution**
4. Configure:
   - Display name: `MessageCenterGovernance_Lab`
   - Publisher: Select default or create new
   - Version: `1.0.0.0`
5. Click **Create**

**Step 2.2:** Create MessageCenterPost Table

1. Open your solution
2. Click **New** → **Table** → **Table**
3. Configure:
   - Display name: `Message Center Post`
   - Plural name: `Message Center Posts`
   - Enable auditing: Yes
4. Click **Save**

**Step 2.3:** Add Columns

Add these columns to MessageCenterPost:

| Display Name | Name | Type | Length/Values |
|--------------|------|------|---------------|
| Message Center ID | mc_messagecenterid | Single line of text | 50 |
| Title | mc_title | Single line of text | 500 |
| Category | mc_category | Choice | preventOrFixIssue, planForChange, stayInformed |
| Severity | mc_severity | Choice | normal, high, critical |
| Services | mc_services | Multiple lines of text | - |
| Body | mc_body | Multiple lines of text (Rich text) | - |
| Start Date | mc_startdatetime | Date and Time | - |
| State | mc_state | Choice | New, Triage, Assess, Decide, Closed |
| Last Modified | mc_lastmodifieddatetime | Date and Time | - |

**Step 2.4:** Create Alternate Key

1. Open MessageCenterPost table → **Keys**
2. Click **New key**
3. Display name: `Message Center ID Key`
4. Columns: Select `mc_messagecenterid`
5. Click **Save**

**Step 2.5:** Enable Table Auditing

1. Open table → **Properties** (gear icon)
2. Expand **Advanced options**
3. Enable **Audit changes to its data**
4. Click **Save**

!!! success "Checkpoint"
    MessageCenterPost table created with all columns, alternate key, and auditing enabled.

---

### Phase 3: Power Automate Ingestion Flow (15 minutes)

**Step 3.1:** Create Scheduled Flow

1. Go to [Power Automate](https://make.powerautomate.com)
2. Click **Create** → **Scheduled cloud flow**
3. Configure:
   - Flow name: `Lab - MC Ingestion`
   - Run every: 15 minutes
4. Click **Create**

**Step 3.2:** Add HTTP Action - Get Token

1. Click **New step** → Search for **HTTP**
2. Configure:

```
Method: POST
URI: https://login.microsoftonline.com/{YOUR_TENANT_ID}/oauth2/v2.0/token
Headers:
  Content-Type: application/x-www-form-urlencoded
Body: grant_type=client_credentials&client_id={YOUR_CLIENT_ID}&client_secret={YOUR_CLIENT_SECRET}&scope=https://graph.microsoft.com/.default
```

Replace placeholders with your values from Phase 1.

**Step 3.3:** Add Parse JSON

1. Click **New step** → **Parse JSON**
2. Content: `@body('HTTP')`
3. Schema:
```json
{
  "type": "object",
  "properties": {
    "access_token": { "type": "string" },
    "token_type": { "type": "string" },
    "expires_in": { "type": "integer" }
  }
}
```

**Step 3.4:** Add HTTP Action - Get Messages

1. Click **New step** → **HTTP**
2. Configure:

```
Method: GET
URI: https://graph.microsoft.com/v1.0/admin/serviceAnnouncement/messages?$top=10&$orderby=lastModifiedDateTime desc
Headers:
  Authorization: Bearer @{body('Parse_JSON')?['access_token']}
```

**Step 3.5:** Add Apply to Each

1. Click **New step** → **Apply to each**
2. Select output: `@body('HTTP_2')?['value']`

**Step 3.6:** Add Dataverse Upsert (inside Apply to Each)

1. Inside the loop, click **Add an action**
2. Search for **Dataverse** → **Add a new row**
3. Configure:
   - Table name: Message Center Posts
   - mc_messagecenterid: `@items('Apply_to_each')?['id']`
   - mc_title: `@items('Apply_to_each')?['title']`
   - mc_category: (map to choice value)
   - mc_severity: (map to choice value)
   - mc_services: `@json(items('Apply_to_each')?['services'])`
   - mc_body: `@items('Apply_to_each')?['body']?['content']`
   - mc_startdatetime: `@items('Apply_to_each')?['startDateTime']`
   - mc_state: New
   - mc_lastmodifieddatetime: `@items('Apply_to_each')?['lastModifiedDateTime']`

**Step 3.7:** Save and Test

1. Click **Save**
2. Click **Test** → **Manually** → **Test**
3. Wait for completion

!!! success "Lab 1 Complete"
    Check your Dataverse table - you should see Message Center posts!

---

## Lab 2: Path A Baseline

**Objective:** Build model-driven app for triage, assessment, and decision workflows

**Duration:** 2 hours

### Prerequisites

- Lab 1 completed successfully
- MessageCenterPost table populated with data

---

### Phase 1: Create Additional Tables (30 minutes)

**Step 2.1:** Create AssessmentLog Table

1. In your solution, click **New** → **Table**
2. Configure:
   - Display name: `Assessment Log`
   - Primary column: `Assessment ID` (auto-generated)
   - Enable auditing: Yes
   - Ownership: User or team

3. Add columns:

| Display Name | Name | Type |
|--------------|------|------|
| Message Center Post | al_messagecenterpost | Lookup (Message Center Post) |
| Assessed By | al_assessedby | Lookup (User) |
| Assessed On | al_assessedon | Date and Time |
| Impact Assessment | al_impactassessment | Choice (None, Low, Medium, High) |
| Notes | al_notes | Multiple lines of text |
| Recommended Action | al_recommendedaction | Choice (Implement, Defer, Dismiss, Escalate) |

4. Configure relationship: Restrict delete on MessageCenterPost lookup

**Step 2.2:** Create DecisionLog Table

1. Create new table:
   - Display name: `Decision Log`
   - Ownership: Organization-owned
   - Enable auditing: Yes

2. Add columns:

| Display Name | Name | Type |
|--------------|------|------|
| Message Center Post | dl_messagecenterpost | Lookup (Message Center Post) |
| Decided By | dl_decidedby | Lookup (User) |
| Decided On | dl_decidedon | Date and Time |
| Decision | dl_decision | Choice (Accept, Defer, Escalate, No Action Required) |
| Decision Rationale | dl_decisionrationale | Multiple lines of text |
| External Reference | dl_externalreference | Single line of text |

3. Configure relationship: Restrict delete on MessageCenterPost lookup

---

### Phase 2: Create Model-Driven App (45 minutes)

**Step 2.3:** Create App

1. In your solution, click **New** → **App** → **Model-driven app**
2. Name: `Message Center Governance Lab`
3. Click **Create**

**Step 2.4:** Configure Site Map

1. In app designer, click **Navigation**
2. Add area: `Governance`
3. Add group: `Message Center`
4. Add pages:
   - Message Center Posts (table page)
   - Assessment Log (table page)
   - Decision Log (table page)

**Step 2.5:** Configure MessageCenterPost Form

1. Go to **Pages** → **Message Center Post** → **Forms**
2. Edit main form
3. Create tabs:

**Tab 1: Overview**
- Title, Category, Severity (section)
- Services, State, Owner (section)
- Start Date, Action Required By (section)

**Tab 2: Content**
- Body (full width, rich text)

**Tab 3: Assessment**
- Impact Assessment, Relevance (section)
- Subgrid: Assessment Log (related records)

**Tab 4: Decision**
- Decision, Decision Rationale (section)
- Subgrid: Decision Log (related records)

4. Save and publish form

**Step 2.6:** Create Views

Create these views for MessageCenterPost:

1. **New Posts Awaiting Triage**
   - Filter: State equals New
   - Columns: Title, Category, Severity, Start Date

2. **My Assigned Posts**
   - Filter: Owner equals current user
   - Columns: Title, State, Category, Severity

3. **High Severity Posts**
   - Filter: Severity equals high OR critical
   - Columns: Title, State, Owner, Action Required By

4. **Recently Closed**
   - Filter: State equals Closed
   - Sort: Modified On descending
   - Columns: Title, Decision, Decided By, Modified On

**Step 2.7:** Save and Publish App

1. Click **Save**
2. Click **Publish**

---

### Phase 3: Configure Security Roles (30 minutes)

**Step 2.8:** Create MC Admin Role

1. In your solution → **Add existing** → **Security role**
2. Click **New security role**
3. Name: `MC Admin Lab`
4. Set privileges:

| Table | Create | Read | Write | Delete |
|-------|--------|------|-------|--------|
| Message Center Post | Org | Org | Org | None |
| Assessment Log | None | Org | None | None |
| Decision Log | None | Org | None | None |

**Step 2.9:** Create MC Owner Role

1. Create new role: `MC Owner Lab`
2. Set privileges:

| Table | Create | Read | Write | Delete |
|-------|--------|------|-------|--------|
| Message Center Post | None | User | User | None |
| Assessment Log | User | User | User | None |
| Decision Log | User | User | None | None |

**Step 2.10:** Assign Roles

1. Go to Power Platform Admin Center
2. Select environment → **Users**
3. Select test user → **Manage security roles**
4. Assign appropriate role

---

### Phase 4: End-to-End Test (15 minutes)

**Step 2.11:** Test Complete Workflow

1. Open model-driven app
2. Navigate to **New Posts Awaiting Triage**
3. Open a post
4. **Triage:** Assign Owner to yourself, change State to Triage
5. **Assess:** Change State to Assess, set Impact Assessment
6. Create Assessment Log record with notes
7. **Decide:** Change State to Decide, set Decision
8. Create Decision Log record with rationale (50+ characters)
9. **Close:** Change State to Closed
10. Verify audit trail shows all changes

!!! success "Lab 2 Complete"
    You have a working governance app with triage, assessment, and decision workflows!

---

## Lab 3: Path B Integration

**Objective:** Demonstrate bi-directional Dataverse ↔ Azure DevOps integration

**Duration:** 2 hours

### Prerequisites

- Lab 2 completed successfully
- Azure DevOps organization access
- Project with Work Items enabled

---

### Phase 1: Extend Dataverse Schema (15 minutes)

**Step 3.1:** Add ADO Columns to DecisionLog

1. Open DecisionLog table
2. Add columns:

| Display Name | Name | Type |
|--------------|------|------|
| ADO Work Item ID | dl_ado_workitem_id | Whole Number |
| ADO Work Item URL | dl_ado_workitem_url | URL |
| ADO State | dl_ado_state | Single line of text (100) |
| ADO Last Modified | dl_ado_lastmodified | Date and Time |

3. Save and publish

---

### Phase 2: Configure Azure DevOps (20 minutes)

**Step 3.2:** Create Project Area

1. Go to Azure DevOps → Your project
2. **Project Settings** → **Boards** → **Project configuration**
3. Create area path: `Platform Governance\Message Center`

**Step 3.3:** Configure Service Hook

1. **Project Settings** → **Service hooks**
2. Click **Create subscription**
3. Select **Web Hooks**
4. Trigger: **Work item updated**
5. Filters:
   - Area path: Under Platform Governance
6. Leave URL blank (will update after creating flow)
7. Click **Finish** (we'll update URL later)

---

### Phase 3: Create Dataverse → ADO Flow (30 minutes)

**Step 3.4:** Create Flow

1. Go to Power Automate → **Create** → **Automated cloud flow**
2. Name: `Lab - Create ADO Work Item`
3. Trigger: **When a row is added** (Microsoft Dataverse)
   - Table name: Decision Logs
   - Scope: Organization

**Step 3.5:** Add Get Parent Post

1. Add action: **Get a row by ID** (Dataverse)
2. Table: Message Center Posts
3. Row ID: `@{triggerOutputs()?['body/_al_messagecenterpost_value']}`

**Step 3.6:** Add Condition

1. Add **Condition**
2. Configure:
   - `triggerOutputs()?['body/dl_decision']` equals `Accept`
   - AND `triggerOutputs()?['body/dl_ado_workitem_id']` is equal to `null`

**Step 3.7:** Add Create Work Item (If Yes branch)

1. Add action: **Create a work item** (Azure DevOps)
2. Configure:
   - Organization: Your org
   - Project: Your project
   - Work Item Type: User Story
   - Title: `[MC] @{outputs('Get_a_row_by_ID')?['body/mc_title']}`
   - Description: (include MC ID, decision rationale)
   - Area Path: Platform Governance\Message Center
   - Tags: `MC:@{outputs('Get_a_row_by_ID')?['body/mc_messagecenterid']}`

**Step 3.8:** Add Update DecisionLog

1. Add action: **Update a row** (Dataverse)
2. Table: Decision Logs
3. Row ID: `@{triggerOutputs()?['body/dl_decisionlogid']}`
4. Set:
   - dl_ado_workitem_id: `@{outputs('Create_a_work_item')?['body/id']}`
   - dl_ado_workitem_url: `@{outputs('Create_a_work_item')?['body/_links/html/href']}`
   - dl_ado_state: `@{outputs('Create_a_work_item')?['body/fields/System.State']}`
   - dl_ado_lastmodified: `@{utcNow()}`

5. Save flow

---

### Phase 4: Create ADO → Dataverse Webhook Flow (30 minutes)

**Step 3.9:** Create HTTP Trigger Flow

1. Create new flow: `Lab - ADO Webhook Handler`
2. Trigger: **When a HTTP request is received**
3. Method: POST

**Step 3.10:** Add Parse JSON

1. Add action: **Parse JSON**
2. Content: `@{triggerBody()}`
3. Use sample payload from Azure DevOps webhook documentation

**Step 3.11:** Add Query DecisionLog

1. Add action: **List rows** (Dataverse)
2. Table: Decision Logs
3. Filter: `dl_ado_workitem_id eq @{body('Parse_JSON')?['resource']?['workItemId']}`

**Step 3.12:** Add Update Logic

1. Add **Condition**: Check if rows returned > 0
2. If yes, add **Update a row**:
   - Row ID: First record's ID
   - dl_ado_state: New state from webhook
   - dl_ado_lastmodified: `@{utcNow()}`

3. Add **Response** action: Status 200

4. Save flow

**Step 3.13:** Update Service Hook

1. Copy the HTTP POST URL from Power Automate
2. Go to Azure DevOps → Service hooks
3. Edit your webhook subscription
4. Update URL with the Power Automate URL
5. Save

---

### Phase 5: End-to-End Test (15 minutes)

**Step 3.14:** Test Full Integration

1. Open model-driven app
2. Select a MessageCenterPost in Decide state
3. Create new DecisionLog record:
   - Decision: Accept
   - Decision Rationale: "Approved for implementation in Q1 sprint. Low risk, standard update."
4. Save the record
5. Wait 30 seconds
6. **Verify in Dataverse:** DecisionLog has ADO Work Item ID and URL
7. **Verify in Azure DevOps:** Work item exists with MC tag
8. **In Azure DevOps:** Change work item state to "Active"
9. Wait 30 seconds
10. **Verify in Dataverse:** dl_ado_state updated to "Active"

!!! success "Lab 3 Complete"
    You have bi-directional sync between Dataverse and Azure DevOps!

---

## Lab Cleanup

After completing labs, consider:

1. **Keep for reference:** Leave solution for future testing
2. **Delete test data:** Remove test MessageCenterPost records
3. **Disable flows:** Turn off scheduled flows to prevent unnecessary API calls
4. **Delete app registration:** Remove Azure AD app if not needed

---

## Troubleshooting Common Lab Issues

| Issue | Cause | Resolution |
|-------|-------|------------|
| HTTP 401 on Graph API | Invalid token or permissions | Verify app registration, grant admin consent |
| No posts returned | No recent Message Center posts | Increase $top parameter or remove date filter |
| Upsert fails | Alternate key not configured | Verify key on mc_messagecenterid |
| ADO work item not created | Flow condition failed | Check Decision value and existing ADO ID |
| Webhook not firing | URL misconfigured | Verify URL in service hook matches flow |

---

*FSI Agent Governance Framework v1.2 - January 2026*
