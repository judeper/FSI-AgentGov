# Portal Walkthrough: Control 1.2 - Agent Registry and Integrated Apps Management

**Last Updated:** January 2026
**Portal:** Microsoft 365 Admin Center, Power Platform Admin Center, SharePoint
**Estimated Time:** 1-2 hours (initial setup)

## Prerequisites

- [ ] Microsoft 365 Global Administrator or Application Administrator role
- [ ] Power Platform System Administrator role
- [ ] Access to [Microsoft 365 Admin Center](https://admin.microsoft.com)
- [ ] Access to [Power Platform Admin Center](https://admin.powerplatform.microsoft.com)
- [ ] SharePoint Site Owner permissions for registry site
- [ ] [Control 2.1: Managed Environments](../../../controls/pillar-2-management/2.1-managed-environments.md) enabled
- [ ] [Control 1.1: Restrict Publishing](../../../controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md) configured

---

## Step-by-Step Configuration

### Step 1: Create Agent Registry Metadata Schema

Before building the registry, define the required metadata fields for FSI compliance:

| Field Name | Required | Description | Example |
|------------|----------|-------------|---------|
| Agent ID | Yes | Unique identifier | `AGT-2025-001` |
| Agent Name | Yes | Display name | `Customer Service Bot` |
| Description | Yes | Purpose and function | `Handles retail banking inquiries` |
| Owner | Yes | Responsible individual | `jane.smith@contoso.com` |
| Business Unit | Yes | Owning department | `Retail Banking` |
| Zone Classification | Yes | Governance zone | `Tier 3 - Enterprise` |
| Environment | Yes | Deployment location | `Production-Enterprise` |
| Data Sources | Yes | Connected data | `SharePoint, CRM` |
| Connectors Used | Yes | External integrations | `SharePoint, Dataverse` |
| Sensitivity Level | Yes | Data classification | `Confidential-FSI` |
| Approval Status | Yes | Governance approval | `Approved` |
| Approval Date | Yes | When approved | `2025-01-15` |
| Approver | Yes | Who approved | `AI Governance Committee` |
| Review Frequency | Yes | How often reviewed | `Quarterly` |
| Last Review Date | Yes | Most recent review | `2025-01-01` |
| Next Review Date | Yes | Scheduled review | `2025-04-01` |
| Risk Rating | Yes | Risk assessment | `Medium` |
| Status | Yes | Current state | `Active` |

### Step 2: Configure Integrated Apps in M365 Admin Center

**Portal Path:** [Microsoft 365 Admin Center](https://admin.microsoft.com) > **Settings** > **Integrated Apps**

1. Sign in to the Microsoft 365 Admin Center
2. Navigate to **Settings** > **Integrated Apps**
3. Review the current list of integrated applications
4. For each Copilot Studio agent:
   - Click the agent name to view details
   - Verify **Publisher** and **Permissions** information
   - Check **User access** configuration
   - Note the **App ID** for registry tracking

**Configure User Consent Settings:**

1. Navigate to **Settings** > **Org settings** > **Services** > **User consent to apps**
2. For FSI environments, set to **Do not allow user consent**
3. This ensures all agents must go through IT/Governance approval

### Step 2b: Configure Agent Settings in M365 Admin Center

**Portal Path:** [Microsoft 365 Admin Center](https://admin.microsoft.com) > **Settings** > **Agent settings**

!!! note "Agent 365 License Required"
    Some settings require Agent 365 licenses. Verify licensing before configuration.

1. Navigate to **Settings** > **Agent settings**
2. Configure **Allowed Agent Types**:
   - Specify which agent types users can create
   - For FSI, consider restricting to approved types only
3. Configure **Sharing Controls**:
   - Set organization-wide sharing defaults
   - For Zone 3 environments, restrict sharing to specific security groups
4. Configure **Templates** (Agent 365 license required):
   - Enable/disable template availability
   - Restrict custom template creation if needed
5. Configure **User Access Controls**:
   - Specify which users can create agents
   - Align with your governance zone requirements

**Recommended FSI Settings:**

| Setting | Zone 1 | Zone 2 | Zone 3 |
|---------|--------|--------|--------|
| Agent Types | All | Restricted | Highly Restricted |
| Sharing | Open | Team-only | Explicit approval |
| Templates | Enabled | Approved only | Admin-controlled |
| Creation | All users | Licensed users | Designated makers |

### Step 3: Create SharePoint Registry List

**Portal Path:** [SharePoint Admin Center](https://admin.microsoft.com/sharepoint) or SharePoint site

1. Create a new SharePoint site or use existing governance site
2. Create a new list named `AI Agent Registry`
3. Add columns matching the metadata schema from Step 1
4. Configure views:
   - **All Agents**: Complete inventory
   - **Active Agents**: Status = Active
   - **Pending Review**: Next Review Date <= Today + 30 days
   - **By Zone**: Grouped by Zone Classification
   - **By Business Unit**: Grouped by Business Unit
5. Set permissions:
   - **Full Control**: AI Governance Team
   - **Contribute**: Agent Owners (their items only)
   - **Read**: Compliance, Audit, Security Teams

### Step 4: Discover Existing Agents

**Portal Path:** [Power Platform Admin Center](https://admin.powerplatform.microsoft.com) > **Environments**

1. For each environment:
   - Click the environment name
   - Navigate to **Resources** > **Power Apps** or **Copilot Studio agents**
   - Export the list of all applications/agents
2. Document each agent's:
   - Name and ID
   - Owner (Created By)
   - Last Modified Date
   - Connectors used (visible in app details)

**Using Copilot Studio:**

1. Navigate to [Copilot Studio](https://copilotstudio.microsoft.com)
2. Select each environment from the environment picker
3. Review **Copilots** list
4. Click each agent to view:
   - Topics and Knowledge sources
   - Channels published to
   - Analytics and usage data

### Step 5: Configure Agent Publishing Requirements

**Portal Path:** Power Platform Admin Center > **Policies** > **Publishing**

Ensure all new agents must be registered before publishing:

1. Navigate to **Environments** > Select production environment
2. Go to **Settings** > **Features**
3. Under **AI-generated content**:
   - Enable **Require admin approval for publishing**
4. Document the approval workflow:
   - Agent must be registered in SharePoint list
   - Zone classification must be assigned
   - Risk assessment must be completed
   - Approval documented before publishing enabled

### Step 6: Set Up Automated Inventory Refresh

**Option A: Power Automate Flow**

Create a scheduled flow to refresh the registry:

1. Navigate to [Power Automate](https://make.powerautomate.com)
2. Create a **Scheduled cloud flow**
3. Set schedule: Weekly (or daily for Tier 3)
4. Add actions:
   - Connect to Power Platform Admin connector
   - List all apps in target environments
   - Compare with SharePoint registry
   - Flag new unregistered agents
   - Send notification email for discrepancies

---

## Configuration by Governance Level

| Setting | Baseline (Personal) | Recommended (Team) | Regulated (Enterprise) |
|---------|-------------------|----------------------|--------------------|
| **Registry format** | Spreadsheet/list | SharePoint list | SharePoint + automation |
| **Update frequency** | Monthly | Weekly | Real-time/Daily |
| **Metadata required** | Basic | Full schema | Full + audit trail |
| **Approval level** | Self-service | Team lead + IT | AI Governance Committee |
| **Risk assessment** | Not required | Checklist | Full assessment |
| **Retention** | 1 year | 3 years | 7 years (SEC 17a-4) |

---

## Validation

After completing these steps, verify:

- [ ] SharePoint registry list created with all required columns
- [ ] All existing agents discovered and documented
- [ ] Integrated Apps visible in M365 Admin Center
- [ ] User consent settings configured appropriately
- [ ] Approval workflow documented and communicated
- [ ] Automation configured (if applicable)

---

[Back to Control 1.2](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
