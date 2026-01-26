# Path A: Dataverse-Only Implementation

**Status:** January 2026 - FSI-AgentGov v1.2
**Estimated Effort:** 4-6 hours for experienced Power Platform administrator
**Prerequisites:** [Architecture](architecture.md) reviewed

---

## Overview

Path A implements the complete Platform Change Governance solution using Dataverse as the sole system-of-record. This path provides full regulatory compliance without Azure DevOps integration.

**When to use Path A:**

- Organization does not use Azure DevOps for change execution
- Primary users are business/compliance stakeholders (not engineering)
- Simpler governance workflow is sufficient
- Minimal training investment desired

---

## Prerequisites

- [ ] Power Platform environment (Developer, Sandbox, or Production)
- [ ] Dataverse System Admin or Power Platform Admin role
- [ ] Azure AD app registration created (for Graph API access)
- [ ] `ServiceMessage.Read.All` application permission granted with admin consent
- [ ] Microsoft 365 E3/E5 licenses

---

## Step 1: Create Solution

All components should be created within a single solution for ALM and deployment purposes.

1. Navigate to [Power Apps Maker Portal](https://make.powerapps.com)
2. Select your target environment
3. Go to **Solutions** → **New solution**
4. Configure solution:
   - **Display name:** Message Center Governance
   - **Name:** MessageCenterGovernance
   - **Publisher:** Select or create your publisher
   - **Version:** 1.0.0.0
5. Click **Create**

---

## Step 2: Create Dataverse Tables

### Table 2.1: MessageCenterPost

1. Open your solution → **Add existing** → **Table** (or **New** → **Table**)
2. Select **New table** with these settings:
   - **Display name:** Message Center Post
   - **Plural name:** Message Center Posts
   - **Name:** mc_messagecenterpost
   - **Primary column:** mc_title
   - **Ownership:** User or team
   - **Enable auditing:** Yes

3. Add columns:

| Display Name | Name | Type | Required | Notes |
|--------------|------|------|----------|-------|
| Message Center ID | mc_messagecenterid | Text (50) | Yes | Primary key, set as Alternate Key |
| Title | mc_title | Text (500) | Yes | Primary column |
| Category | mc_category | Choice | No | Values: preventOrFixIssue, planForChange, stayInformed |
| Severity | mc_severity | Choice | No | Values: normal, high, critical |
| Services | mc_services | Multiline Text | No | JSON array of affected services |
| Tags | mc_tags | Multiline Text | No | JSON array of tags |
| Start Date | mc_startdatetime | Date and Time | No | |
| End Date | mc_enddatetime | Date and Time | No | |
| Action Required By | mc_actionrequiredby | Date and Time | No | |
| Body | mc_body | Multiline Text (Rich) | No | Full HTML content |
| State | mc_state | Choice | Yes | Values: New, Triage, Assess, Decide, Closed |
| Impact Assessment | mc_impactassessment | Choice | No | Values: None, Low, Medium, High |
| Relevance | mc_relevance | Choice | No | Values: Not Applicable, Informational, Action Required |
| Decision | mc_decision | Choice | No | Values: Accept, Defer, Escalate, No Action Required |
| Decision Rationale | mc_decisionrationale | Multiline Text | No | |
| Owner | mc_owner | Lookup (User) | No | |
| Last Modified DateTime | mc_lastmodifieddatetime | Date and Time | No | From Graph API |

4. Create **Alternate Key** on `mc_messagecenterid` for upsert operations

### Table 2.2: AssessmentLog

1. Create new table:
   - **Display name:** Assessment Log
   - **Name:** mc_assessmentlog
   - **Primary column:** al_assessmentid (auto-number or GUID)
   - **Ownership:** User or team
   - **Enable auditing:** Yes

2. Add columns:

| Display Name | Name | Type | Required |
|--------------|------|------|----------|
| Message Center Post | al_messagecenterpost | Lookup | Yes |
| Assessed By | al_assessedby | Lookup (User) | Yes |
| Assessed On | al_assessedon | Date and Time | Yes |
| Impact Assessment | al_impactassessment | Choice | Yes |
| Notes | al_notes | Multiline Text | No |
| Recommended Action | al_recommendedaction | Choice | No |
| Affected Systems | al_affectedsystems | Multiline Text | No |

3. Configure relationship to MessageCenterPost as **Restrict Delete**

### Table 2.3: DecisionLog

1. Create new table:
   - **Display name:** Decision Log
   - **Name:** mc_decisionlog
   - **Primary column:** dl_decisionid (auto-number or GUID)
   - **Ownership:** Organization-owned
   - **Enable auditing:** Yes

2. Add columns:

| Display Name | Name | Type | Required |
|--------------|------|------|----------|
| Message Center Post | dl_messagecenterpost | Lookup | Yes |
| Decided By | dl_decidedby | Lookup (User) | Yes |
| Decided On | dl_decidedon | Date and Time | Yes |
| Decision | dl_decision | Choice | Yes |
| Decision Rationale | dl_decisionrationale | Multiline Text | Yes |
| External Ticket Reference | dl_externalticketreference | Text (200) | No |

3. Configure relationship to MessageCenterPost as **Restrict Delete**

!!! warning "Organization-Owned for Immutability"
    DecisionLog must be organization-owned to prevent user modification after creation. This supports SEC 17a-4 requirements for immutable records.

---

## Step 3: Enable Dataverse Auditing

1. Go to [Power Platform Admin Center](https://admin.powerplatform.microsoft.com)
2. Select your environment → **Settings** → **Audit and logs** → **Audit settings**
3. Enable:
   - [x] Start Auditing
   - [x] Audit user access
   - [x] Read logs (optional, high volume)
4. For each table (MessageCenterPost, AssessmentLog, DecisionLog):
   - Open table settings → **Advanced options** → **Audit changes to its data**
   - Enable auditing for all columns

---

## Step 4: Create Security Roles

### Role 4.1: MC Admin

1. In your solution → **Add existing** → **Security role** → **New security role**
2. Name: **MC Admin**
3. Configure privileges:

| Entity | Create | Read | Write | Delete | Append | Append To |
|--------|--------|------|-------|--------|--------|-----------|
| MessageCenterPost | Org | Org | Org | None | Org | Org |
| AssessmentLog | None | Org | None | None | None | Org |
| DecisionLog | None | Org | None | None | None | Org |

### Role 4.2: MC Owner

1. Create new security role: **MC Owner**
2. Configure privileges:

| Entity | Create | Read | Write | Delete | Append | Append To |
|--------|--------|------|-------|--------|--------|-----------|
| MessageCenterPost | None | User | User | None | User | User |
| AssessmentLog | User | User | User | None | User | User |
| DecisionLog | User | User | None | None | User | User |

### Role 4.3: MC Compliance Reviewer

1. Create new security role: **MC Compliance Reviewer**
2. Configure privileges:

| Entity | Create | Read | Write | Delete | Append | Append To |
|--------|--------|------|-------|--------|--------|-----------|
| MessageCenterPost | None | Org | None | None | None | Org |
| AssessmentLog | None | Org | None | None | None | Org |
| DecisionLog | Org | Org | Org | None | Org | Org |

### Role 4.4: MC Auditor

1. Create new security role: **MC Auditor**
2. Configure privileges (read-only):

| Entity | Create | Read | Write | Delete | Append | Append To |
|--------|--------|------|-------|--------|--------|-----------|
| MessageCenterPost | None | Org | None | None | None | None |
| AssessmentLog | None | Org | None | None | None | None |
| DecisionLog | None | Org | None | None | None | None |

---

## Step 5: Create Power Automate Ingestion Flow

1. Go to [Power Automate](https://make.powerautomate.com) → **My flows** → **New flow** → **Scheduled cloud flow**
2. Configure schedule:
   - **Name:** MC Ingestion - Message Center Posts
   - **Run every:** 15 minutes

### Flow Actions

**Action 1: Initialize Variable - Last Run Timestamp**

```
Name: varLastRunTimestamp
Type: String
Value: @{addMinutes(utcNow(), -30)}
```

**Action 2: HTTP - Get Access Token**

```
Method: POST
URI: https://login.microsoftonline.com/@{variables('TenantId')}/oauth2/v2.0/token
Headers:
  Content-Type: application/x-www-form-urlencoded
Body: grant_type=client_credentials&client_id=@{variables('ClientId')}&client_secret=@{variables('ClientSecret')}&scope=https://graph.microsoft.com/.default
```

**Action 3: Parse JSON - Extract Token**

```
Content: @{body('HTTP_-_Get_Access_Token')}
Schema:
{
  "type": "object",
  "properties": {
    "access_token": { "type": "string" },
    "token_type": { "type": "string" },
    "expires_in": { "type": "integer" }
  }
}
```

**Action 4: HTTP - Get Message Center Posts**

```
Method: GET
URI: https://graph.microsoft.com/v1.0/admin/serviceAnnouncement/messages?$filter=lastModifiedDateTime gt @{variables('varLastRunTimestamp')}&$orderby=lastModifiedDateTime asc
Headers:
  Authorization: Bearer @{body('Parse_JSON_-_Extract_Token')?['access_token']}
```

**Action 5: Apply to Each**

For each item in `body('HTTP_-_Get_Message_Center_Posts')?['value']`:

**Action 5a: Upsert Row (Dataverse)**

```
Table name: Message Center Posts
Alternate Key: mc_messagecenterid = @{items('Apply_to_each')?['id']}
mc_title: @{items('Apply_to_each')?['title']}
mc_category: @{items('Apply_to_each')?['category']}
mc_severity: @{items('Apply_to_each')?['severity']}
mc_services: @{json(items('Apply_to_each')?['services'])}
mc_startdatetime: @{items('Apply_to_each')?['startDateTime']}
mc_enddatetime: @{items('Apply_to_each')?['endDateTime']}
mc_actionrequiredby: @{items('Apply_to_each')?['actionRequiredByDateTime']}
mc_body: @{items('Apply_to_each')?['body']?['content']}
mc_state: New (only if creating new)
mc_lastmodifieddatetime: @{items('Apply_to_each')?['lastModifiedDateTime']}
```

**Action 6: Send Notification (Optional)**

Send email or Teams message on successful completion or errors.

---

## Step 6: Create Model-Driven App

1. In your solution → **New** → **App** → **Model-driven app**
2. Name: **Message Center Governance**
3. Add tables to navigation:
   - Message Center Posts (with views and forms)
   - Assessment Log (as subgrid in MessageCenterPost form)
   - Decision Log (as subgrid in MessageCenterPost form)

### Configure Views

Create these views for MessageCenterPost:

| View Name | Filter |
|-----------|--------|
| New Posts - Awaiting Triage | `mc_state = New` |
| High Severity Posts | `mc_severity IN (high, critical)` |
| My Assigned Posts | `mc_owner = current user` |
| Posts by Category | Group by `mc_category` |
| All Open Posts | `mc_state != Closed` |
| Recently Closed | `mc_state = Closed` ordered by modified desc |

### Configure Main Form

**Tab 1: Overview**

- Title, Category, Severity (header)
- Services, Tags, State
- Owner, Action Required By

**Tab 2: Message Content**

- Body (rich text, read-only)

**Tab 3: Assessment**

- Impact Assessment, Relevance
- AssessmentLog subgrid

**Tab 4: Decision**

- Decision, Decision Rationale
- DecisionLog subgrid

**Tab 5: Audit Trail**

- Timeline control

---

## Step 7: Create Business Process Flow (Optional)

1. In your solution → **New** → **Automation** → **Business process flow**
2. Name: **Message Center Governance Process**
3. Entity: **Message Center Post**

**Stages:**

1. **New** - Trigger: Record created
2. **Triage** - Required: Owner assigned
3. **Assess** - Required: Impact Assessment, Relevance
4. **Decide** - Required: Decision, Decision Rationale (min 50 char)
5. **Closed** - Completion stage

---

## Step 8: Configure Environment Variables

Create environment variables for deployment flexibility:

| Variable | Type | Default Value | Description |
|----------|------|---------------|-------------|
| MCG_TenantId | Text | (tenant GUID) | Azure AD tenant |
| MCG_ClientId | Text | (app GUID) | App registration client ID |
| MCG_ClientSecret | Secret | (stored in Key Vault) | App registration secret |
| MCG_PollingIntervalMinutes | Number | 15 | Ingestion polling interval |

---

## Verification Checklist

- [ ] All three tables created with correct columns and settings
- [ ] Auditing enabled on all tables
- [ ] Alternate key created on MessageCenterPost for upsert
- [ ] Security roles created and assigned to test users
- [ ] Ingestion flow runs successfully and creates/updates posts
- [ ] Model-driven app accessible with correct views
- [ ] Business process flow guides users through workflow
- [ ] Decision rationale enforces minimum 50 character requirement
- [ ] Audit logs capture all field changes

---

## Post-Implementation

After completing Path A:

1. **Assign roles** to production users
2. **Monitor** ingestion flow for errors
3. **Train users** on triage and decision workflows
4. **Configure** quarterly evidence export (see [Evidence and Audit](evidence-and-audit.md))
5. **Optionally** proceed to [Path B](implementation-path-b.md) for ADO integration

---

*FSI Agent Governance Framework v1.2 - January 2026*
