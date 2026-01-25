# Path B: Dataverse + Azure DevOps Integration

**Status:** January 2026 - FSI-AgentGov v1.2
**Estimated Effort:** 2-4 hours (after Path A complete)
**Prerequisites:** [Path A](implementation-path-a.md) fully implemented

---

## Overview

Path B extends Path A by adding bi-directional synchronization between Dataverse and Azure DevOps. Governance decisions in Dataverse automatically create work items in Azure DevOps, and work item state changes sync back to Dataverse.

**When to use Path B:**

- Engineering teams use Azure DevOps for sprint planning and work management
- Platform changes require technical implementation tracked in ADO
- Organization wants unified view of governance + execution status
- Teams need ALM integration (linked commits, pull requests, CI/CD)

!!! warning "Path A Required First"
    Path B extends Path A. Complete all Path A steps before proceeding. Path B only adds ADO integration; it does not replace Dataverse governance.

---

## Prerequisites

- [ ] Path A fully implemented and tested
- [ ] Azure DevOps organization with Project Administrator access
- [ ] Azure DevOps project for platform changes
- [ ] Service connection or PAT for Power Automate → ADO integration
- [ ] Understanding of ADO work item types and workflows

---

## Step 6: Extend Dataverse Schema for ADO Integration

### Add ADO Columns to DecisionLog

1. Open your solution → **DecisionLog** table
2. Add columns:

| Display Name | Name | Type | Required | Notes |
|--------------|------|------|----------|-------|
| ADO Work Item ID | dl_ado_workitem_id | Whole Number | No | Azure DevOps work item ID |
| ADO Work Item URL | dl_ado_workitem_url | URL | No | Direct link to ADO work item |
| ADO State | dl_ado_state | Text (100) | No | Current ADO work item state |
| ADO Last Modified | dl_ado_lastmodified | Date and Time | No | Last sync timestamp |

3. Publish changes

### Add ADO Columns to MessageCenterPost (Optional)

For quick reference without navigating to DecisionLog:

| Display Name | Name | Type | Notes |
|--------------|------|------|-------|
| Has ADO Work Item | mc_hasadoworkitem | Yes/No | Calculated or updated by flow |
| Latest ADO State | mc_latestadostate | Text (100) | Denormalized for views |

---

## Step 7: Configure Azure DevOps

### Create Work Item Type (Optional)

If using a custom work item type for platform changes:

1. Go to **Azure DevOps** → **Project Settings** → **Process**
2. Create inherited process or modify existing
3. Add work item type: **Platform Change**
4. Add fields:
   - Message Center ID (text)
   - Source Post URL (URL)
   - Governance Decision (choice)
   - Decision Rationale (multiline)

### Configure Area Path

Create dedicated area for Message Center governance:

```
Project
└── Platform Governance
    └── Message Center Changes
```

### Configure Tags Convention

Use consistent tags for traceability:

- `MC:{MessageCenterID}` - Links to original post
- `Governance:Approved` - Decision status
- `Priority:{High|Medium|Low}` - Based on severity

---

## Step 8: Create Dataverse → ADO Sync Flow

### Trigger Configuration

1. Go to [Power Automate](https://make.powerautomate.com) → **My flows** → **New flow** → **Automated cloud flow**
2. Name: **MCG - Create ADO Work Item on Decision**
3. Trigger: **When a row is added** (Dataverse)
   - Table name: Decision Log
   - Scope: Organization

### Flow Logic

**Action 1: Get Related Message Center Post**

```
Get a row by ID
Table: Message Center Posts
Row ID: @{triggerOutputs()?['body/dl_messagecenterpost']}
```

**Action 2: Condition - Check if Decision = Accept and No Existing Work Item**

```
Condition:
  triggerOutputs()?['body/dl_decision'] equals 'Accept'
  AND
  triggerOutputs()?['body/dl_ado_workitem_id'] equals null
```

**Action 3 (If Yes): Create Work Item**

Use Azure DevOps connector:

```
Organization: {your-org}
Project: {your-project}
Work Item Type: User Story (or Platform Change)
Title: [MC] @{outputs('Get_Related_Message_Center_Post')?['body/mc_title']}
Description:
  <h2>Message Center Post</h2>
  <p><strong>ID:</strong> @{outputs('Get_Related_Message_Center_Post')?['body/mc_messagecenterid']}</p>
  <p><strong>Category:</strong> @{outputs('Get_Related_Message_Center_Post')?['body/mc_category']}</p>
  <p><strong>Severity:</strong> @{outputs('Get_Related_Message_Center_Post')?['body/mc_severity']}</p>
  <p><strong>Action Required By:</strong> @{outputs('Get_Related_Message_Center_Post')?['body/mc_actionrequiredby']}</p>
  <h2>Governance Decision</h2>
  <p>@{triggerOutputs()?['body/dl_decisionrationale']}</p>
  <hr/>
  <p><em>Auto-created from Message Center Governance</em></p>
Tags: MC:@{outputs('Get_Related_Message_Center_Post')?['body/mc_messagecenterid']}
```

**Action 4: Update Decision Log with ADO Details**

```
Update a row
Table: Decision Log
Row ID: @{triggerOutputs()?['body/dl_decisionid']}
dl_ado_workitem_id: @{outputs('Create_a_work_item')?['body/id']}
dl_ado_workitem_url: @{outputs('Create_a_work_item')?['body/_links/html/href']}
dl_ado_state: @{outputs('Create_a_work_item')?['body/fields/System.State']}
dl_ado_lastmodified: @{utcNow()}
```

**Action 5 (If No): Terminate or Log**

Log reason for skipping (decision was not Accept, or work item already exists).

---

## Step 9: Create ADO → Dataverse Webhook Flow

### Configure Azure DevOps Service Hook

1. Go to **Azure DevOps** → **Project Settings** → **Service hooks**
2. Click **Create subscription**
3. Select **Web Hooks**
4. Configure:
   - **Trigger:** Work item updated
   - **Filters:**
     - Area path: Platform Governance/Message Center Changes
     - Changed fields: System.State (or All fields)
5. **Action URL:** (Will be populated after creating Power Automate flow)
6. Complete webhook creation

### Create Power Automate HTTP Trigger Flow

1. Create new flow: **MCG - ADO Webhook Handler**
2. Trigger: **When a HTTP request is received**
3. Method: POST

**Request Body JSON Schema:**

```json
{
  "type": "object",
  "properties": {
    "subscriptionId": { "type": "string" },
    "notificationId": { "type": "integer" },
    "eventType": { "type": "string" },
    "resource": {
      "type": "object",
      "properties": {
        "id": { "type": "integer" },
        "workItemId": { "type": "integer" },
        "fields": {
          "type": "object",
          "properties": {
            "System.State": {
              "type": "object",
              "properties": {
                "newValue": { "type": "string" }
              }
            }
          }
        }
      }
    }
  }
}
```

**Action 1: Parse JSON**

```
Content: @{triggerBody()}
Schema: (above schema)
```

**Action 2: List Rows - Find DecisionLog by ADO Work Item ID**

```
Table: Decision Log
Filter rows: dl_ado_workitem_id eq @{body('Parse_JSON')?['resource']?['workItemId']}
```

**Action 3: Condition - Check if Record Found**

```
Condition: length(outputs('List_rows')?['body/value']) greater than 0
```

**Action 4 (If Yes): Update Decision Log**

```
Update a row
Table: Decision Log
Row ID: @{first(outputs('List_rows')?['body/value'])?['dl_decisionid']}
dl_ado_state: @{body('Parse_JSON')?['resource']?['fields']?['System.State']?['newValue']}
dl_ado_lastmodified: @{utcNow()}
```

**Action 5: Response**

```
Status Code: 200
Body: { "status": "success" }
```

### Update Service Hook with Flow URL

1. Copy the HTTP POST URL from Power Automate trigger
2. Go back to Azure DevOps service hook configuration
3. Update the URL field with the Power Automate URL
4. Test the webhook

---

## Step 10: Update Model-Driven App

### Add ADO Tab to MessageCenterPost Form

1. Open MessageCenterPost main form in solution
2. Add new tab: **ADO Integration**
3. Add fields:
   - ADO Work Item ID (from DecisionLog via lookup)
   - ADO Work Item URL (hyperlink)
   - ADO State
   - ADO Last Modified

### Add ADO View

Create view: **Posts with ADO Work Items**

```
Filter: dl_ado_workitem_id is not null (via related DecisionLog)
Columns: Title, Category, State, ADO Work Item ID, ADO State
```

---

## Step 11: Implement Reconciliation Job (Recommended)

Azure DevOps webhooks may occasionally fail. Implement a scheduled reconciliation flow:

1. Create scheduled flow: **MCG - ADO Reconciliation** (daily at 2 AM)
2. Logic:
   - Query DecisionLog where `dl_ado_workitem_id` is not null
   - For each, call ADO API to get current work item state
   - Update `dl_ado_state` if changed
   - Log discrepancies

---

## Verification Checklist

- [ ] DecisionLog extended with ADO columns
- [ ] Azure DevOps project and area path configured
- [ ] Dataverse → ADO flow creates work items on Accept decision
- [ ] Work item includes MC ID tag for traceability
- [ ] DecisionLog updated with ADO work item ID and URL
- [ ] Service hook configured in Azure DevOps
- [ ] ADO → Dataverse webhook flow receives and processes updates
- [ ] ADO state changes reflect in DecisionLog
- [ ] Model-driven app shows ADO integration status
- [ ] Reconciliation job catches missed webhook updates

---

## End-to-End Test Procedure

1. **Create Test Post:** Manually create MessageCenterPost with State = Decide
2. **Create Decision:** Create DecisionLog with Decision = Accept
3. **Verify ADO:** Check Azure DevOps for new work item with MC tag
4. **Verify Dataverse:** Confirm DecisionLog has ADO work item ID and URL
5. **Update ADO:** Change work item state in Azure DevOps (e.g., New → Active)
6. **Verify Sync:** Check DecisionLog `dl_ado_state` updated
7. **Test Reconciliation:** Disable webhook, make ADO change, run reconciliation, verify sync

---

## Troubleshooting

### Work Item Not Created

| Symptom | Cause | Resolution |
|---------|-------|------------|
| No work item appears | Decision != Accept | Verify decision value |
| No work item appears | Work item already exists | Check `dl_ado_workitem_id` |
| Flow fails | ADO permissions | Verify connection/PAT has Create Work Items |
| Flow fails | Invalid project/area | Verify project and area path exist |

### Webhook Not Updating Dataverse

| Symptom | Cause | Resolution |
|---------|-------|------------|
| No updates in Dataverse | Webhook URL incorrect | Verify URL in service hook |
| No updates in Dataverse | Work item ID mismatch | Check `dl_ado_workitem_id` matches |
| Intermittent failures | ADO webhook retry | Run reconciliation job |
| 401 errors | Expired credentials | Refresh Power Automate connection |

---

## Security Considerations

### Service Connection Security

- Use service principal with minimal permissions (Work Items Read/Write only)
- Store credentials in Azure Key Vault
- Rotate secrets per organizational policy

### Webhook Security

- Power Automate HTTP triggers include SAS token in URL
- Consider adding custom header validation
- Monitor for unusual traffic patterns

### Data Sensitivity

- ADO work item descriptions may contain governance decisions
- Ensure ADO project has appropriate access controls
- Do not sync sensitive customer data to ADO

---

## Related Documents

| Document | Relationship |
|----------|-------------|
| [Overview](index.md) | Path selection guidance |
| [Architecture](architecture.md) | Technical design |
| [Path A Implementation](implementation-path-a.md) | Prerequisite implementation |
| [Labs](labs.md) | Lab 3 covers Path B integration |
| [Evidence and Audit](evidence-and-audit.md) | ADO evidence retention |

---

*FSI Agent Governance Framework v1.2 - January 2026*
