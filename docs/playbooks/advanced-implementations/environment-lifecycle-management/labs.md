# Environment Lifecycle Management - Labs

**Status:** May 2026 - FSI-AgentGov v1.6.2
**Estimated Time:** 4-6 hours total

---

## Overview

These hands-on labs guide you through implementing Environment Lifecycle Management from scratch. Complete them in order, as each lab builds on the previous.

| Lab | Title | Time | Prerequisites |
|-----|-------|------|---------------|
| 1 | Dataverse Schema | 60 min | Power Platform environment |
| 2 | Copilot Intake Agent | 90 min | Lab 1 complete |
| 3 | Provisioning Flow | 90 min | Lab 1 & 2 complete, Service Principal |
| 4 | End-to-End Test | 60 min | Labs 1-3 complete |

### License Prerequisites

Before starting, ensure you have the required licenses:

| License | Required For | Notes |
|---------|--------------|-------|
| **Power Apps Premium** or **Power Apps per app** | Dataverse tables, Model-driven app | Per user or per app licensing |
| **Copilot Studio** | Lab 2 - Intake Agent | Included in some M365 plans or standalone |
| **Power Automate Premium** | Lab 3 - HTTP actions, custom connectors | Required for HTTP with Entra ID preauthorized |
| **Azure subscription** | Key Vault for secrets | For secure credential storage |

!!! warning "Trial Licenses"
    Trial licenses can be used for labs but may have limitations. For production deployment, ensure proper licensing is in place.

---

## Lab 1: Dataverse Schema

### Objective

Deploy the EnvironmentRequest and ProvisioningLog tables with security roles.

### Prerequisites

- Power Platform environment with Dataverse
- System Administrator or System Customizer role
- Access to make.powerapps.com
- Python 3.10+ (for automated deployment option)

### Option A: Automated Deployment (Recommended for Lab/Dev)

Use the Python deployment scripts from FSI-AgentGov-Solutions for quick setup:

```bash
# Clone the solutions repository
git clone https://github.com/judeper/FSI-AgentGov-Solutions.git
cd FSI-AgentGov-Solutions/environment-lifecycle-management/scripts

# Install dependencies
pip install -r requirements.txt

# Dry run first to preview changes
python deploy.py \
  --environment-url https://<your-org>.crm.dynamics.com \
  --tenant-id <your-tenant-id> \
  --interactive \
  --dry-run

# Full deployment
python deploy.py \
  --environment-url https://<your-org>.crm.dynamics.com \
  --tenant-id <your-tenant-id> \
  --interactive
```

This creates:

- 8 global option sets (State, Zone, Region, etc.)
- EnvironmentRequest table (22 columns, user-owned, auditing enabled)
- ProvisioningLog table (11 columns, org-owned, auditing enabled)
- 4 security roles (Requester, Approver, Admin, Auditor)
- 3 business rules (conditional required fields)
- 8 model-driven app views
- Field security profile for approvers

After automated deployment, **skip to [Verification](#verification)** below, then continue to Lab 2.

!!! note "Production Deployment"
    For production environments, use the manual process below to ensure full audit trail of who created each component.

---

### Option B: Manual Deployment (Production)

Follow the steps below for manual deployment with full audit trail.

### Step 1.1: Create EnvironmentRequest Table

1. Navigate to **make.powerapps.com** > **Tables**
2. Select **New table** > **New table**
3. Configure:
   - **Display name:** Environment Request
   - **Plural name:** Environment Requests
   - **Schema name prefix:** Uses your publisher prefix (e.g., `fsi_`)

4. **Configure the Primary Column (Request Number):**
   - After creating the table, select the primary column (Name)
   - Change **Data type** to **Autonumber**
   - Configure Autonumber settings:
     - **Format:** `REQ-{SEQNUM:5}` (produces REQ-00001, REQ-00002, etc.)
     - **Seed value:** 1
   - Click **Done**

!!! note "Autonumber Format"
    The format `{SEQNUM:5}` creates a 5-digit sequential number with leading zeros. This ensures consistent sorting and prevents duplicate numbers.

5. Create columns per [Architecture](architecture.md#table-1-environmentrequest-primary-request-table):

!!! note "Choice Field Integer Values"
    When creating Choice columns, you must specify both the label and integer value. See [Architecture - Choice Field Value Definitions](architecture.md#choice-field-value-definitions) for the complete list of integer values for each Choice field.

| Column | Type | Required | Notes |
|--------|------|----------|-------|
| Environment Name | Single line text (100) | Yes | |
| Environment Type | Choice | Yes | Sandbox (1), Production (2), Developer (3) |
| Region | Choice | Yes | United States, Europe, United Kingdom, Australia |
| Zone | Choice | Yes | Zone 1, Zone 2, Zone 3 |
| Zone Rationale | Multiple lines text | No | Business rule: required for Zone 2/3 |
| Zone Auto Flags | Single line text (500) | No | |
| Business Justification | Multiple lines text | Yes | |
| Data Sensitivity | Choice | Yes | Public, Internal, Confidential, Restricted |
| Expected Users | Choice | Yes | Just me (1), Small team (2-10), Large team (11-50), Department (50+) |
| Security Group ID | Single line text (100) | No | |
| Requester | Lookup (User) | Auto | |
| Requested On | Date and time | Auto | |
| State | Choice | Yes | Draft, Submitted, PendingApproval, Approved, Rejected, Provisioning, Completed, Failed |
| Approver | Lookup (User) | No | |
| Approved On | Date and time | No | |
| Approval Comments | Multiple lines text | No | |
| Environment ID | Single line text (100) | No | |
| Environment URL | URL | No | |
| Provisioning Started | Date and time | No | |
| Provisioning Completed | Date and time | No | |

6. **Save** the table

### Step 1.2: Create ProvisioningLog Table

1. Select **New table** > **New table**
2. Configure:
   - **Display name:** Provisioning Log
   - **Plural name:** Provisioning Logs
   - **Schema name prefix:** Uses your publisher prefix (e.g., `fsi_`)
   - **Table ownership:** Organization

3. Create columns:

| Column | Type | Required | Notes |
|--------|------|----------|-------|
| Environment Request | Lookup (Environment Request) | Yes | Cascade: Restrict delete |
| Sequence | Whole number | Yes | |
| Action | Choice | Yes | See architecture for values |
| Action Details | Multiple lines text | No | JSON format |
| Actor | Single line text (200) | Yes | |
| Actor Type | Choice | Yes | User, ServicePrincipal, System |
| Timestamp | Date and time | Auto | Default: Now |
| Success | Yes/No | Yes | Default: Yes |
| Error Message | Multiple lines text | No | |
| Correlation ID | Single line text (100) | No | |

4. **Save** the table

### Step 1.3: Configure Table Relationships

1. Open **ProvisioningLog** table > **Relationships**
2. Verify lookup to EnvironmentRequest:
   - **Type:** Many-to-one
   - **Related table:** Environment Request
   - **Delete behavior:** Restrict

### Step 1.4: Create Security Roles

1. Navigate to **Settings** (gear icon) > **Advanced settings**
2. Select **Settings** > **Security** > **Security roles**
3. Select **New** to create each role

#### Security Role Privilege Matrix

Configure each role with the following privileges. The depth levels are:

- **None** = No access
- **User** = Own records only
- **Business Unit** = Records in user's business unit
- **Parent: Child BU** = User's BU and child BUs
- **Organization** = All records

##### ELM Requester

| Table | Create | Read | Write | Delete | Append | AppendTo |
|-------|--------|------|-------|--------|--------|----------|
| Environment Request | User | User | User | None | User | User |
| Provisioning Log | None | User | None | None | None | None |

##### ELM Approver

| Table | Create | Read | Write | Delete | Append | AppendTo |
|-------|--------|------|-------|--------|--------|----------|
| Environment Request | None | Business Unit | Business Unit | None | None | None |
| Provisioning Log | None | Business Unit | None | None | None | None |

!!! note "Field-Level Security"
    Approvers can only write to `er_state`, `er_approver`, `er_approvedon`, and `er_approvalcomments` fields. Configure field-level security profiles to restrict other fields.

##### ELM Admin

| Table | Create | Read | Write | Delete | Append | AppendTo |
|-------|--------|------|-------|--------|--------|----------|
| Environment Request | Organization | Organization | Organization | None | Organization | Organization |
| Provisioning Log | Organization | Organization | **None** | **None** | Organization | Organization |

!!! danger "ProvisioningLog Immutability"
    The ELM Admin role has **no Write or Delete** privileges on ProvisioningLog. This enforces immutability. Only Create and Read are granted.

##### ELM Auditor

| Table | Create | Read | Write | Delete | Append | AppendTo |
|-------|--------|------|-------|--------|--------|----------|
| Environment Request | None | Organization | None | None | None | None |
| Provisioning Log | None | Organization | None | None | None | None |

4. **Save** each role after configuration

### Step 1.5: Configure Business Rules

1. Navigate to **make.powerapps.com** > **Tables**
2. Select the **Environment Request** table
3. In the table designer, select **Business rules** from the left menu (under **Customizations**)
4. Select **+ New business rule**

**Create Rule: Zone Rationale Required**

1. **Rule name:** Zone Rationale Required
2. In the rule designer:
   - Add **Condition**:
     - Field: **Zone**
     - Operator: **Equals**
     - Value: **Zone 2**
   - Select **+ Or** to add another condition:
     - Field: **Zone**
     - Operator: **Equals**
     - Value: **Zone 3**
   - Add **Action** (on the true branch):
     - Action: **Set Business Required**
     - Field: **Zone Rationale**
     - Status: **Business Required**
3. Select **Save**
4. Select **Activate**

**Create Rule: Security Group Required**

1. Select **+ New business rule**
2. **Rule name:** Security Group Required
3. Follow the same pattern:
   - Condition: Zone equals Zone 2 OR Zone equals Zone 3
   - Action: Set **Security Group ID** as Business Required
4. **Save and Activate**

!!! note "Business Rule Scope"
    By default, business rules apply to all forms. If you need different behavior on different forms, change the **Scope** in the rule properties.

### Verification

- [ ] EnvironmentRequest table has all 22 columns
- [ ] ProvisioningLog table has all 11 columns
- [ ] Relationship cascade is set to Restrict
- [ ] 4 security roles exist with correct permissions
- [ ] Business rules are active

---

## Lab 2: Copilot Intake Agent

### Objective

Build the conversational intake agent that collects environment requests.

### Prerequisites

- Lab 1 complete (Dataverse tables exist)
- Microsoft Copilot Studio license
- Access to copilotstudio.microsoft.com

### Step 2.1: Create New Agent

1. Navigate to **copilotstudio.microsoft.com**
2. In the top-right corner, verify your **environment** matches Lab 1 (click the environment name to switch if needed)
3. From the left navigation, select **Agents**
4. Select the down arrow next to **Create blank agent**, then select **Advanced create** (this lets you set the primary language, solution, and schema name up front)
5. Configure:
   - **Language:** English (United States)
   - **Solution:** (Optional) Select a solution if using ALM
6. Select **Confirm and create** and wait for the agent to be provisioned (this may take 1-2 minutes)
7. On the agent's **Overview** page, select **Edit** in the **Details** section to set:
   - **Name:** Environment Request Agent
   - **Description:** Collects and processes Power Platform environment provisioning requests

### Step 2.2: Configure Authentication

1. Navigate to **Settings** > **Security**
2. **Authentication:** Authenticate with Microsoft
3. **Require users to sign in:** Yes
4. **Scope:** User.Read

### Step 2.3: Create Request Environment Topic

1. Navigate to **Topics** > **New topic** > **From blank**
2. **Name:** Request New Environment
3. Add **Trigger phrases:**
   - I need a new environment
   - Create an environment
   - Request environment
   - New Power Platform environment
   - Provision environment

4. Build conversation flow:

```
[Trigger] → [Message: "I'll help you request a new Power Platform environment."]
         → [Question: environmentName]
         → [Question: environmentType]
         → [Question: region]
         → [Question: businessPurpose]
         → [Question: expectedUsers]
         → [Question: dataSensitivity]
         → [Question: hasCustomerData]
         → [Question: hasFinancialData]
         → [Question: hasExternalAccess]
         → [Action: Zone Classification]
         → [Condition: Zone >= 2]
            → [Question: securityGroupName]
         → [Condition: Zone == 3]
            → [Question: zoneRationale]
         → [Message: Summary]
         → [Question: Confirm]
         → [Action: Call Power Automate]
         → [Message: Confirmation]
```

### Step 2.4: Configure Questions

For each question node, configure the entity type and prompt. In Copilot Studio:

1. Select the **Question** node
2. In the properties pane, set **Identify** to the appropriate entity type
3. Configure the prompt message

**environmentName:**

- **Entity:** User's entire response
- **Prompt:** "What would you like to name this environment? Use format: DEPT-Purpose-TYPE (e.g., FIN-Reporting-PROD)"
- **Save response as:** `Topic.environmentName`

After this question, add a **Condition** node to validate the format:

1. Add **Condition** node
2. Set condition: `IsMatch(Topic.environmentName, "^[A-Z]{2,4}-[A-Za-z0-9]+-[A-Z]+$")`
3. **If false:** Add message "Invalid format. Please use DEPT-Purpose-TYPE format." and redirect back to question

**environmentType:**

- **Entity:** Choice
- **Options:** Define three options: Sandbox, Production, Developer
- **Prompt:** "What type of environment do you need?"
- **Save response as:** `Topic.environmentType`

**expectedUsers:**

- **Entity:** Choice
- **Options:** Just me (1), Small team (2-10), Large team (11-50), Department (50+)
- **Prompt:** "How many users will use this environment?"
- **Save response as:** `Topic.expectedUsers`

**dataSensitivity:**

- **Entity:** Choice
- **Options:** Public, Internal, Confidential, Restricted
- **Prompt:** "What's the highest data sensitivity level for data in this environment?"
- **Save response as:** `Topic.dataSensitivity`

**hasCustomerData, hasFinancialData, hasExternalAccess:**

- **Entity:** Confirmation (not Boolean)
- **Prompts:** As defined in [implementation-copilot-intake.md](implementation-copilot-intake.md#slot-definitions)
- **Save response as:** `Topic.hasCustomerData`, etc.

!!! note "Confirmation Entity"
    The **Confirmation** entity type presents Yes/No options to the user and returns a boolean value. Do not use "Boolean" as an entity type - it doesn't exist in Copilot Studio.

### Step 2.5: Implement Zone Classification

1. Add **Set variable** action after collecting all inputs
2. Create variable `classifiedZone` with Power Fx:

```
If(
    Topic.dataSensitivity = "Restricted" ||
    Topic.hasCustomerData = true ||
    Topic.hasFinancialData = true ||
    Topic.hasExternalAccess = true,
    3,
    If(
        Topic.dataSensitivity = "Confidential" ||
        Topic.environmentType = "Production" ||
        Topic.expectedUsers <> "Just me (1)",
        2,
        1
    )
)
```

3. Create variable `zoneFlags` to capture triggers:

```
Concat(
    If(Topic.dataSensitivity = "Restricted", "RESTRICTED_DATA;", ""),
    If(Topic.hasCustomerData, "CUSTOMER_PII;", ""),
    If(Topic.hasFinancialData, "FINANCIAL_TRANSACTIONS;", ""),
    If(Topic.hasExternalAccess, "EXTERNAL_ACCESS;", "")
)
```

### Step 2.6: Create Summary Message

Add **Message** node with Adaptive Card:

```json
{
  "type": "AdaptiveCard",
  "body": [
    {
      "type": "TextBlock",
      "text": "Environment Request Summary",
      "weight": "Bolder",
      "size": "Large"
    },
    {
      "type": "FactSet",
      "facts": [
        { "title": "Name", "value": "${Topic.environmentName}" },
        { "title": "Type", "value": "${Topic.environmentType}" },
        { "title": "Region", "value": "${Topic.region}" },
        { "title": "Zone", "value": "Zone ${Topic.classifiedZone}" },
        { "title": "Triggers", "value": "${Topic.zoneFlags}" }
      ]
    }
  ],
  "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
  "version": "1.3"
}
```

### Step 2.7: Connect to Power Automate

1. After the confirmation question, add a **Call an action** node
2. In the action panel, select **Power Automate**
3. Select **Create a flow** to build a new flow, or **Add existing flow** if you've already created the intake flow from Lab 3
4. If creating a new flow:
   - The flow will open in Power Automate with a "Run a flow from Copilot" trigger
   - Add input parameters for each topic variable (environmentName, environmentType, region, zone, etc.)
   - Add flow actions to create the Dataverse record (see Lab 3)
   - Add an output parameter for the request number
   - Save and return to Copilot Studio
5. Map topic variables to flow inputs:
   - `Topic.environmentName` → `environmentName`
   - `Topic.environmentType` → `environmentType`
   - `Topic.region` → `region`
   - `Topic.classifiedZone` → `zone`
   - `Topic.zoneFlags` → `zoneFlags`
   - `Topic.dataSensitivity` → `dataSensitivity`
   - `Topic.hasCustomerData` → `hasCustomerData`
   - `Topic.hasFinancialData` → `hasFinancialData`
   - `Topic.hasExternalAccess` → `hasExternalAccess`
   - `Topic.businessPurpose` → `businessPurpose`
   - `Topic.expectedUsers` → `expectedUsers`
   - `Topic.securityGroupName` → `securityGroupName` (if Zone 2/3)
   - `Topic.zoneRationale` → `zoneRationale` (if Zone 3)
6. After the action, add a **Message** node to display the returned request number

### Verification

- [ ] Agent responds to trigger phrases
- [ ] All questions collect valid input
- [ ] Zone classification works correctly for various scenarios
- [ ] Summary displays accurate information
- [ ] Authentication requires sign-in

**Test Scenarios:**

| Scenario | Expected Zone | Triggers |
|----------|---------------|----------|
| Internal docs, no customer data | Zone 1 | None |
| Confidential, team use | Zone 2 | CONFIDENTIAL_DATA |
| Customer data, Production | Zone 3 | CUSTOMER_PII, PRODUCTION_WORKLOAD |

---

## Lab 3: Provisioning Flow

### Objective

Build the Power Automate flow that provisions environments using Service Principal.

### Prerequisites

- Labs 1 & 2 complete
- Service Principal configured per [architecture.md](architecture.md#service-principal-lifecycle)
- Power Platform for Admins V2 connector available

### Step 3.1: Create Service Principal Connection

1. Navigate to **make.powerautomate.com** > **Connections**
2. **New connection** > **Power Platform for Admins V2**
3. Select **Service Principal** authentication
4. Enter:
   - Tenant ID
   - Client ID (from app registration)
   - Client Secret (from Key Vault - consider using Azure Key Vault connector)

### Step 3.2: Create Main Provisioning Flow

1. **Create** > **Automated cloud flow**
2. **Name:** ELM - Main Provisioning
3. **Trigger:** When a row is added, modified or deleted (Dataverse)
   - Table: Environment Requests
   - Scope: Organization
   - Change type: Modified
   - Select columns: State

4. Add **Condition:** State equals Approved

### Step 3.3: Add Logging Action

1. Add **Add a new row** (Dataverse)
2. Table: Provisioning Logs
3. Map fields:
   - Environment Request: `triggerBody()?['er_requestid']`
   - Sequence: 1
   - Action: ProvisioningStarted
   - Actor Type: ServicePrincipal
   - Success: Yes

### Step 3.4: Create Environment

1. Add **Create Environment (V2)** action
2. Map inputs from trigger:
   - Location: `triggerBody()?['er_region']`
   - Display Name: `triggerBody()?['er_environmentname']`
   - Environment Type: `triggerBody()?['er_environmenttype']`

!!! warning "Security Group Binding"
    The Power Platform for Admins V2 connector does **not** support `SecurityGroupId` at environment creation time. After the environment is created and the polling loop confirms success (Step 3.5), add an **Update Environment** action or BAP API call to bind the security group using `triggerBody()?['er_securitygroupid']`. The security group GUID should be the Entra ID Object ID of the target security group.

### Step 3.5: Implement Polling Loop

1. Add **Initialize variable:** `pollCount` (Integer, 0)
2. Add **Do until:**
   - Condition: `pollCount` >= 120 OR provisioningState = Succeeded
   - Limit count: 120
   - Timeout: PT60M

3. Inside loop:
   - **Delay:** 30 seconds
   - **Get Environment (V2)**
   - **Increment variable:** pollCount
   - **Condition:** Check for Failed state → Terminate

### Step 3.6: Enable Managed Environment

1. Add **HTTP with Microsoft Entra ID (preauthorized)**
2. Configure per [implementation-provisioning.md](implementation-provisioning.md#step-4-enable-managed-environment)

### Step 3.7: Assign to Environment Group

1. Add **HTTP** action for group assignment
2. Implement retry policy: 3 attempts, exponential backoff
3. Use **Compose** to select group based on zone:

```json
@{if(equals(triggerBody()?['er_zone'], 1), 'FSI-Personal-Dev',
    if(equals(triggerBody()?['er_zone'], 2), 'FSI-Team-Collaboration',
    'FSI-Enterprise-Production'))}
```

### Step 3.8: Add Error Handling

1. Wrap Create Environment in **Scope**
2. Add parallel **Scope** with `runAfter: Failed`
3. In error scope:
   - Log failure to ProvisioningLog
   - Update EnvironmentRequest state to Failed
   - **Terminate** with Failed status

### Step 3.9: Complete Provisioning

1. Add **Update row** (Dataverse) for EnvironmentRequest:
   - State: Completed
   - Environment ID: from Create Environment output
   - Environment URL: from Create Environment output
   - Provisioning Completed: `utcNow()`

2. Add final **Add a new row** for ProvisioningLog:
   - Action: ProvisioningCompleted
   - Success: Yes

### Verification

- [ ] Flow triggers on Approved state
- [ ] Service Principal connection works
- [ ] Polling loop respects timeout
- [ ] Error handling catches failures
- [ ] Completion updates all fields

---

## Lab 4: End-to-End Test

### Objective

Verify the complete solution works from request to provisioned environment.

### Prerequisites

- Labs 1-3 complete
- Test user account with ELM Requester role
- Approver account with ELM Approver role

### Step 4.1: Prepare Test Data

#### Create Environment Groups (if not already existing)

Environment Groups must exist before environments can be assigned. Create these in Power Platform admin center:

1. Navigate to **Power Platform admin center** (admin.powerplatform.microsoft.com)
2. Select **Environment groups** from the left navigation
3. Select **+ New group** and create each group:

| Group Name | Description | DLP Policies |
|------------|-------------|--------------|
| `FSI-Personal-Dev` | Personal productivity environments | Standard DLP |
| `FSI-Team-Collaboration` | Team collaboration environments | Enhanced DLP |
| `FSI-Enterprise-Production` | Enterprise managed environments | Restrictive DLP |

4. For each group, configure:
   - **Rules:** Add DLP policies appropriate to the zone
   - **Managed environment settings:** Configure sharing limits per zone

!!! note "Environment Groups Prerequisite"
    Environment Groups are a prerequisite for ELM. If your organization hasn't configured them yet, refer to [Control 2.2 - Environment Groups](../../../controls/pillar-2-management/2.2-environment-groups-and-tier-classification.md) for full configuration guidance.

#### Create Test Security Group in Entra ID

1. Navigate to **Microsoft Entra admin center** > **Groups** > **All groups**
2. Select **New group**
3. Configure:
   - **Group type:** Security
   - **Group name:** Test-ELM-Lab4-Users
   - **Group description:** Test security group for ELM Lab 4
   - **Membership type:** Assigned
4. Click **Create**
5. Copy the **Object ID** - you'll need this for the test

### Step 4.2: Test Zone 1 Request

1. **As Requester:** Open Copilot Studio agent
2. Say: "I need a new environment"
3. Provide responses:
   - Name: TEST-Lab4Zone1-DEV
   - Type: Developer
   - Region: United States
   - Purpose: Testing Environment Lifecycle Management
   - Users: Individual developer
   - Sensitivity: Internal
   - Customer data: No
   - Financial data: No
   - External access: No

4. **Verify:**
   - [ ] Agent classifies as Zone 1
   - [ ] No security group required
   - [ ] Request created in Dataverse with State = Submitted

5. **As Approver:** Approve the request
6. **Verify:**
   - [ ] Provisioning flow triggers
   - [ ] Environment created
   - [ ] ProvisioningLog has entries

### Step 4.3: Test Zone 3 Request

1. **As Requester:** Start new conversation
2. Provide responses:
   - Name: TEST-Lab4Zone3-PROD
   - Type: Production
   - Region: United States
   - Purpose: Customer data processing for regulatory compliance
   - Users: Compliance team, 10 users
   - Sensitivity: Confidential
   - Customer data: **Yes**
   - Financial data: **Yes**
   - External access: No

3. **Verify:**
   - [ ] Agent classifies as Zone 3
   - [ ] Zone flags: CUSTOMER_PII, FINANCIAL_TRANSACTIONS
   - [ ] Requires security group
   - [ ] Requires zone rationale — a free-text justification for why this workload requires enterprise-managed governance (e.g., "Environment will process quarterly financial reports containing customer account data")

4. Complete remaining prompts
5. **As Approver:** Approve with Compliance review
6. **Verify environment configuration:**
   - [ ] Managed Environment: Enabled
   - [ ] Environment Group: FSI-Enterprise-Production
   - [ ] Audit retention: 2557 days (7 years)
   - [ ] Session timeout: 120 minutes

### Step 4.4: Test Error Handling

1. Create a request with invalid security group ID
2. **Verify:**
   - [ ] Provisioning flow detects error
   - [ ] ProvisioningLog records failure
   - [ ] EnvironmentRequest state = Failed
   - [ ] Admin notification sent

### Step 4.5: Verify Audit Trail

1. Navigate to Model-Driven App
2. Open a completed request
3. View ProvisioningLog subgrid
4. **Verify entries:**
   - [ ] ProvisioningStarted
   - [ ] EnvironmentCreated
   - [ ] ManagedEnabled
   - [ ] GroupAssigned
   - [ ] AuditingConfigured
   - [ ] SessionTimeoutConfigured
   - [ ] SharingLimitsConfigured
   - [ ] ProvisioningCompleted

### Step 4.6: Clean Up

1. Delete test environments:

   ```powershell
   # First, get the environment IDs (the -EnvironmentName parameter requires the GUID, not display name)
   Get-AdminPowerAppEnvironment | Where-Object { $_.DisplayName -like "TEST-Lab4*" } | Select-Object DisplayName, EnvironmentName

   # Delete using the environment GUID
   Remove-AdminPowerAppEnvironment -EnvironmentName "<environment-guid-from-above>"
   ```

   !!! warning "Parameter Clarification"
       The `-EnvironmentName` parameter expects the environment's **GUID** (e.g., `12345678-1234-1234-1234-123456789012`), not the display name. Use `Get-AdminPowerAppEnvironment` to find the GUID first.

2. Delete test requests from Dataverse (or mark as test data)

### Final Checklist

- [ ] Zone 1 request flows end-to-end
- [ ] Zone 3 request flows with enhanced approval
- [ ] Error handling works correctly
- [ ] Audit trail is complete and immutable
- [ ] Notifications sent to requester

---

## Troubleshooting

### Common Issues

| Issue | Error Message | Cause | Resolution |
|-------|---------------|-------|------------|
| Agent doesn't trigger flow | "Unable to connect to flow" or no response after confirmation | Missing or broken Power Automate connection | 1. In Copilot Studio, go to **Settings** > **Extensions** > **Power Automate**. 2. Verify the flow connection is active. 3. Re-authenticate if prompted. |
| Environment creation fails | `"code": "UnauthorizedAccess", "message": "The caller does not have permission"` | Service Principal not registered as Management Application | 1. Go to **PPAC** > **Settings** > **Admin settings**. 2. Add the Service Principal under **Service principal**. 3. Wait 5 minutes for propagation. |
| Environment creation fails | `"code": "InvalidRequest", "message": "Location is not valid"` | Region value doesn't match Power Platform region codes | Use exact region values: `unitedstates`, `europe`, `unitedkingdom`, `australia` (lowercase, no spaces). **Important:** Dataverse stores region as Choice integers (1=United States, 2=Europe, 3=United Kingdom, 4=Australia). The provisioning flow must map these integers to API strings using the expression documented in [implementation-provisioning.md](implementation-provisioning.md#step-2-create-environment). |
| Group assignment fails | `"code": "ResourceNotFound", "message": "Environment group not found"` | Environment Group doesn't exist or wrong Group ID | 1. Verify group exists in **PPAC** > **Environment groups**. 2. Use the group's GUID, not display name, in API calls. |
| Security group binding fails | `"code": "ObjectNotFound", "message": "The specified security group was not found"` | Security Group ID is incorrect or doesn't exist | 1. Verify group exists in Entra ID. 2. Use the **Object ID**, not the Display Name. 3. Ensure the group is a Security group (not M365 group). |
| Polling timeout | No error - flow just times out | Environment provisioning taking longer than 60 minutes | 1. Check environment status in PPAC manually. 2. If still provisioning, wait and retry. 3. If failed, review PPAC errors and contact support. |
| Flow authentication error | `"code": "InvalidAuthenticationToken", "message": "The access token has expired"` | Service Principal secret expired | 1. Generate new secret in Entra ID. 2. Update Azure Key Vault. 3. Refresh the Power Automate connection. |
| Dataverse write fails | `"code": "0x80040220", "message": "Principal user is missing prvCreate privilege"` | Service account missing security role | Assign **ELM Admin** security role to the Service Principal user in Dataverse. |

### Debug Steps

1. **Check Flow Run History:** Power Automate > Flow > Run history
2. **Check Dataverse Audit:** Advanced Find > ProvisioningLog
3. **Check Power Platform Admin Center:** Environments list for new environment

---

## Next Steps

After completing labs:

1. **Production Deployment:** Export solution and deploy to production environment
2. **Configure Approvers:** Assign real approvers in approval workflow
3. **Enable Monitoring:** Set up alerts for failed provisioning
4. **Train Users:** Onboard requesters to the new process

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
