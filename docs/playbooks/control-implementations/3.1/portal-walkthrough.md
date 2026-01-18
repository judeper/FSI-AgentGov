# Portal Walkthrough: Control 3.1 - Agent Inventory and Metadata Management

**Last Updated:** January 2026
**Portal:** Power Platform Admin Center, Microsoft 365 Admin Center
**Estimated Time:** 1-2 hours

## Prerequisites

- [ ] Power Platform Administrator role assigned
- [ ] Access to [Power Platform Admin Center](https://admin.powerplatform.microsoft.com)
- [ ] Access to [Microsoft 365 Admin Center](https://admin.microsoft.com)
- [ ] Global Reader role for compliance review access
- [ ] [Control 2.1: Managed Environments](../../../controls/pillar-2-management/2.1-managed-environments.md) enabled
- [ ] Inventory export location prepared (SharePoint, network share, or GRC tool)

---

## Step-by-Step Configuration

### Step 1: Access Power Platform Inventory

1. Sign in to **Power Platform Admin Center** ([https://admin.powerplatform.microsoft.com](https://admin.powerplatform.microsoft.com))
2. Navigate to **Manage** > **Inventory**
3. View the complete list of maker creations across all environments
4. Note the item count displayed (e.g., "Showing 297 of 297 items")

### Step 2: Review Available Columns

Review the following columns in the inventory view:

| Column | Description | Governance Use |
|--------|-------------|----------------|
| **Item name** | Name of the agent/app/flow | Identification |
| **Item type** | Agent, Model-driven app, Code app | Filter for agents |
| **Owner** | User who created/owns the item | Accountability |
| **Modified on** | Last modification date | Change tracking |
| **Created on** | Creation date | Lifecycle tracking |
| **Environment** | Environment name (clickable link) | Location tracking |
| **Environment type** | Sandbox, Default, Developer, Production | Risk classification |
| **Environment region** | Geographic location | Data residency |

### Step 3: Filter by Agent Type

1. Click on the **Item type** column filter
2. Select **Agent** to filter the view
3. Review only agents (excluding apps and flows)
4. Document the total agent count for your records

### Step 4: Identify Orphaned Agents

1. Review the **Owner** column for each agent
2. Look for indicators of orphaned agents:
   - "System Account" in owner field
   - Deleted user names
   - Empty owner fields
3. Document any orphaned agents for remediation

### Step 5: Export Inventory to CSV

1. Click the **Export** button in the toolbar
2. Select CSV format
3. Save to your designated governance location
4. Name the file with date: `AgentInventory_YYYYMMDD.csv`

### Step 6: Access M365 Admin Center Agent Registry

1. Open [Microsoft 365 Admin Center](https://admin.microsoft.com)
2. Navigate to **Settings** > **Integrated apps**
3. Select the **Agents** tab
4. Review declarative agents and M365 Copilot extensions

### Step 7: Reconcile Both Inventories

1. Export the M365 Agent Registry list
2. Compare against Power Platform inventory export
3. Identify any agents appearing in only one location
4. Document discrepancies for investigation

---

## Configuration by Governance Level

| Setting | Baseline (Level 1) | Recommended (Level 2-3) | Regulated (Level 4) |
|---------|-------------------|------------------------|---------------------|
| **Review frequency** | Monthly | Weekly | Daily |
| **Metadata tracked** | Basic (owner, env, dates) | Extended (purpose, data sources) | Comprehensive (risk, validation) |
| **Export retention** | 1 year | 3 years | 6+ years |
| **Orphan detection** | Monthly | Weekly | Daily |
| **GRC integration** | Optional | Recommended | Required |
| **Hash verification** | Optional | Recommended | Required |

---

## System of Record Setup

### Option A: SharePoint List (Recommended for most FSI)

1. Create a SharePoint site for governance records
2. Create a list named "Agent Inventory Register"
3. Add columns:
   - AgentID (text, required)
   - Agent Name (text)
   - Owner (person)
   - Owner Manager (person)
   - Environment (choice)
   - Governance Tier (choice: 1/2/3)
   - Data Classification (choice)
   - Business Purpose (multiline text)
   - Approval Date (date)
   - RTO Minutes (number)
   - RPO Minutes (number)
   - Operational State (choice)
4. Enable version history for audit trail

### Option B: GRC Tool Integration

1. Configure API connection to your GRC platform
2. Map inventory fields to GRC asset records
3. Establish automated sync schedule
4. Configure change notifications

---

## NYDFS Part 500 Compliance Fields

For organizations subject to NYDFS Part 500 Section 500.13, add these fields to your inventory:

| Field | Value Type | Example |
|-------|------------|---------|
| Recovery Time Objective (RTO) | Minutes | 60 |
| Recovery Point Objective (RPO) | Minutes | 15 |
| Support Expiration Date | Date | 2027-12-31 |
| Criticality Tier | 1-4 | 2 |
| Backup Compliance Status | Choice | Compliant |
| Operational State | Choice | Active |

---

## Validation

After completing these steps, verify:

- [ ] Power Platform inventory displays all environments
- [ ] Agent count matches expected total
- [ ] Orphaned agents identified and documented
- [ ] CSV export completed and saved
- [ ] M365 Agent Registry reviewed
- [ ] Both inventories reconciled
- [ ] System of record established

---

[Back to Control 3.1](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
