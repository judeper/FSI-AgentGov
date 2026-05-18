# Portal Walkthrough: Control 3.11 - Centralized Agent Inventory Enforcement

**Last Updated:** April 2026
**Portal:** Power Platform Admin Center (PPAC), Microsoft 365 Admin Center, Microsoft Copilot Studio
**Estimated Time:** 60-75 minutes

!!! info "Feature status (April 2026)"
    Power Platform Inventory in PPAC reached **General Availability on February 9, 2026** (MC1223778). Inventory data refreshes approximately every 15 minutes; per-environment refresh schedules are no longer configurable. Microsoft Agent 365 (the unified agent control plane) reaches GA on **May 1, 2026**. Steps below reflect the GA experience; legacy preview steps and the placeholder Agent Inventory REST API have been removed in favor of the **Power Platform for Admins V2** connector for workflow integration.

## Prerequisites

- [ ] Power Platform Admin role (tenant-wide; required to view the Inventory page)
- [ ] AI Administrator role (for Agent 365 control plane configuration when GA)
- [ ] Entra Global Admin (for one-time tenant consent only; prefer PIM just-in-time elevation)
- [ ] Access to PPAC, M365 Admin Center, and Copilot Studio
- [ ] Knowledge of governance zone classifications (Control 2.2)
- [ ] List of all Power Platform environments with zone assignments
- [ ] Mandatory metadata requirements documented (owner, zone, risk rating)
- [ ] Change-management process for agent registration and decommissioning
- [ ] Teams channel for governance alerts and notifications

---

## Step-by-Step Configuration

### Part 1: Access and Configure Power Platform Inventory in PPAC

#### Step 1: Navigate to the Inventory Page

1. Open [Power Platform Admin Center](https://admin.powerplatform.microsoft.com)
2. Sign in with Power Platform Admin credentials
3. In the left navigation, expand **Manage** and select **Inventory** (the unified Inventory page; agents, apps, flows, environments, and environment groups appear as tabs or filters)
4. Select the **Agents** view to see Copilot Studio agents and Microsoft 365 Copilot Agent Builder agents tenant-wide
5. Review the dashboard layout:
   - **Agent List:** Table showing all discovered agents with key attributes
   - **Filter and Sort Controls:** Filter by environment, environment group, owner, creation date
   - **Customize Columns:** Add/remove columns including Authentication Method, Sharing Status
   - **Export to Excel:** Export current view for offline analysis or evidence retention
   - **Last refresh timestamp:** Inventory refreshes automatically (~15 minutes); no manual refresh schedule is exposed

> **Note:** Power Platform Inventory is GA as of February 9, 2026. If the Inventory page is not visible, confirm the signed-in user holds a tenant-wide admin role (Power Platform Admin or Dynamics 365 Admin) and that the tenant region has received the rollout. There are no read-only or fine-grained admin variants today; track Microsoft 365 Roadmap for future RBAC granularity.

#### Step 2: Confirm Inventory Refresh and Coverage

1. On the Inventory page, note the **Last refreshed** timestamp shown above the agent list
2. The platform refreshes inventory data approximately every 15 minutes; no per-environment refresh configuration is required
3. Validate coverage by spot-checking that recently created agents appear within ~15-30 minutes
4. If newly created agents do not appear after 30 minutes, open a Microsoft support case referencing MC1223778 and Power Platform Inventory GA

> **Zone 3 expectation:** For regulated environments, the ~15-minute refresh interval typically meets near-real-time governance needs. Pair the platform refresh with the Power Automate flow in Part 3 (built on the **Power Platform for Admins V2** connector) for active alerting.

#### Step 3: Review Current Agent Inventory

1. In the Agent Inventory page, review the **Agent List** table
2. Verify the following columns are displayed (add/remove columns as needed):
   - Agent Name
   - Owner (responsible individual)
   - Environment (Power Platform environment or M365 context)
   - Creation Date
   - Last Modified Date
   - Authentication Method (service principal, managed identity, user delegation)
   - Sharing Status (Private, Team, Organizational)
   - Feature Usage (Connectors, Generative Actions, Tools)
3. Review the list and identify agents with **missing or incomplete metadata:**
   - Owner: "Unknown" or blank
   - Environment: Not classified to a governance zone
   - No description or documentation link
4. Export the current inventory to CSV for baseline documentation:
   - Click **Export** button
   - Save file as `AgentInventory_Baseline_YYYYMMDD.csv`
   - Store in governance documentation repository

> **Baseline Documentation:** This export serves as the pre-enforcement baseline. After implementing enforcement mechanisms, you'll compare future inventory exports to measure improvement in completeness and compliance.

#### Step 4: Configure Mandatory Metadata Requirements

While PPAC Agent Inventory tracks certain attributes automatically, you need to define *mandatory* metadata fields that agents must have before approval/publication:

1. Create a governance document (Word, SharePoint, or Wiki page): **Agent Metadata Requirements**
2. Define mandatory fields by zone:

**Universal Requirements (All Zones):**

| Field | Required? | Validation |
|-------|-----------|------------|
| Agent Name | Yes | Non-empty, descriptive, follows naming convention |
| Owner | Yes | Valid Entra ID user, active account |
| Environment | Yes | Must map to known Power Platform environment |
| Zone Classification | Yes | Zone 1, Zone 2, or Zone 3 |
| Creation Date | Yes | Auto-populated, read-only |

**Zone 2 and Zone 3 Additional Requirements:**

| Field | Required? | Validation |
|-------|-----------|------------|
| Description | Yes | Minimum 50 characters explaining agent purpose |
| Risk Rating | Yes | High, Medium, or Low based on data access and capabilities |
| Approval Date | Yes (Zone 2/3) | Date when agent was approved for deployment |
| Approver | Yes (Zone 2/3) | Name of AI Governance Lead or Compliance Officer who approved |
| Documentation Link | Yes (Zone 2/3) | Link to SharePoint or Wiki page with detailed agent documentation |
| Last Reviewed Date | Yes (Zone 3) | Date of most recent governance review |
| Decommissioning Plan | Yes (Zone 3) | Documented plan for agent retirement when no longer needed |

3. Document these requirements in your governance repository
4. Communicate requirements to all agent authors via email, Teams announcement, or training session
5. Integrate requirements into pre-publication checklist (see Step 6)

> **Best Practice:** Store mandatory metadata requirements in a version-controlled document (e.g., SharePoint with version history enabled). Update and republish when requirements change, and notify agent authors of changes.

---

### Part 2: Implement Ownership Validation and Orphaned Agent Detection

#### Step 5: Set Up Ownership Validation Process

Ownership validation ensures that every agent has an active, accountable owner who can maintain and govern the agent.

1. In the Agent Inventory, filter agents by **Owner** field
2. Identify agents with problematic ownership:
   - Owner field is blank or "Unknown"
   - Owner is a departed user (no longer in Entra ID)
   - Owner is a generic service account (e.g., "admin@contoso.com")
   - Owner is a shared account used by multiple people
3. Document the list of agents with ownership issues
4. For each problematic agent, research the correct owner:
   - Review agent metadata (creator, last modified by)
   - Check environment ownership (who owns the Power Platform environment?)
   - Contact business stakeholders using the agent
   - Review change management tickets related to the agent's creation
5. Assign or transfer ownership:
   - In PPAC, navigate to **Environments** > [Select environment] > **Resources** > **Apps** or **Copilot Studio agents**
   - Select the agent and click **Manage sharing** or **Transfer ownership**
   - Assign the correct owner and click **Save**
   - Document ownership change in change management system
6. Create a recurring task (quarterly for Zone 1, monthly for Zone 2/3): **Agent Ownership Validation**
   - Export Agent Inventory to CSV
   - Cross-reference owners against active Entra ID users
   - Identify orphaned agents (owner departed or invalid)
   - Initiate ownership transfer or decommissioning process

> **Orphaned Agent Definition:** An agent is considered "orphaned" if: (1) the assigned owner is no longer an active user in Entra ID, (2) the owner has moved to a different role and no longer maintains the agent, (3) the agent is part of a discontinued project, or (4) the agent has not been modified in >12 months and owner cannot be contacted.

#### Step 6: Create Pre-Publication Checklist for Agent Registration

To enforce inventory completeness, agents should not be published or shared until they meet mandatory metadata requirements.

1. Create a pre-publication checklist document (SharePoint, Word, or embedded in agent approval workflow)
2. Include the following checklist items:

**Agent Registration Pre-Publication Checklist:**

- [ ] **Agent Name:** Descriptive name following naming convention (e.g., `[Zone]-[Department]-[Purpose]-Agent`)
- [ ] **Owner Assigned:** Valid Entra ID user identified and assigned as owner
- [ ] **Environment:** Agent deployed to correct environment for its zone classification
- [ ] **Zone Classification:** Agent assigned to Zone 1, Zone 2, or Zone 3 based on data access and risk
- [ ] **Risk Rating:** Risk rating assigned (High/Medium/Low) based on assessment criteria
- [ ] **Description:** Minimum 50-character description of agent purpose and use cases
- [ ] **Documentation Link:** Link to full agent documentation (architecture, data sources, approvals)
- [ ] **Approval Obtained:** (Zone 2/3 only) AI Governance Lead or Compliance Officer approval documented
- [ ] **Change Ticket:** Change management ticket created and approved for agent deployment
- [ ] **Metadata Complete:** All mandatory metadata fields populated in inventory system (Agent Inventory or custom registry)
- [ ] **Security Review:** (Zone 3 only) Security team review completed and documented
- [ ] **Decommissioning Plan:** (Zone 3 only) Plan documented for agent retirement or ownership transfer

3. Integrate the checklist into your agent approval workflow:
   - If using a formal change management system (ServiceNow, Jira), add checklist as required fields in the agent approval request template
   - If using SharePoint or manual approvals, require requestor to complete checklist and submit as part of approval package
   - Configure approval gates to block publication until checklist is verified complete
4. Train agent authors on the pre-publication checklist requirements
5. Test the checklist by submitting a test agent approval request and verifying all fields are validated

> **Enforcement Strategy:** The pre-publication checklist is your primary enforcement mechanism for inventory completeness. By requiring metadata completion *before* approval, you prevent unmanaged agents from entering production. This is more effective than retroactive remediation.

---

### Part 3: Automate Incomplete Metadata Detection with Power Automate

#### Step 7: Create Power Automate Flow for Metadata Completeness Monitoring

Automated monitoring detects agents with missing or incomplete metadata and alerts the governance team for remediation.

1. Open [Power Automate](https://make.powerautomate.com)
2. Select your **default environment** or a dedicated governance environment (not Zone 3 production)
3. Click **+ Create** > **Scheduled cloud flow**
4. Name the flow: `Agent Inventory Completeness Monitor`
5. Configure schedule:
   - **Recurrence:** Daily
   - **Start time:** 3:00 AM (after Agent Inventory refresh completes)
   - Click **Create**

**Flow Steps:**

**Step 1: Get Agent Inventory Data**

1. Add action: **Power Platform for Admins V2** → **List as Admin Inventory Resources** (or the equivalent inventory operation exposed by your tenant; the connector is GA and exposes the same data the PPAC Inventory page surfaces)
2. Configure the action to filter by **Resource Type = Agent** (and optionally by environment group)
3. The action returns inventory rows directly — no parsing of a custom HTTP response is required

> **Why the connector instead of a custom HTTP call:** Earlier preview guidance referenced an unreleased `api.powerplatform.com/agentInventory` endpoint. That endpoint is not the supported integration path. The **Power Platform for Admins V2** connector is the GA-supported way to query inventory from Power Automate; it inherits the connection's admin role and avoids managing service-principal secrets directly in the flow.

> **API Availability Note:** The supported integration path for inventory data is the **Power Platform for Admins V2** connector (GA), not a custom REST endpoint. If you previously authored flows against the placeholder URL `api.powerplatform.com/agentInventory/...`, migrate them to the connector. Alternative offline paths remain available for air-gapped scenarios: (1) PPAC Inventory → **Export to Excel** → SharePoint document library, then parse in Power Automate, or (2) PowerShell discovery (see PowerShell Setup) writing to a Dataverse table queried by the flow.

**Step 2: Filter Agents with Incomplete Metadata**

1. Add action: **Filter array**
2. Configure filter conditions to identify agents with incomplete metadata:
   - **Condition 1:** Owner is empty or "Unknown"
   - **Condition 2:** Zone Classification is empty
   - **Condition 3:** Risk Rating is empty
   - **Condition 4:** (Zone 2/3) Description is empty or less than 50 characters
   - **Condition 5:** (Zone 3) Approval Date is empty
3. Output: Array of agents with incomplete metadata

**Step 3: Check if Any Agents Have Issues**

1. Add condition: **Condition**
2. Check if the filtered array length is greater than 0:
   - **If yes:** Proceed to send alert
   - **If no:** Flow completes successfully with no action

**Step 4: Format Alert Message**

1. In the **Yes** branch, add action: **Compose**
2. Create a formatted message listing agents with incomplete metadata:

```
⚠️ Agent Inventory Completeness Alert

The following agents have incomplete metadata and require remediation:

1. Agent Name: [Agent Name 1]
   - Environment: [Environment]
   - Missing Fields: Owner, Zone Classification
   - Action Required: Assign owner and classify zone within 7 days

2. Agent Name: [Agent Name 2]
   - Environment: [Environment]
   - Missing Fields: Risk Rating, Description
   - Action Required: Complete metadata within 7 days

Total agents with issues: [Count]

📊 View full inventory: [Link to PPAC Agent Inventory]
📝 Metadata requirements: [Link to governance document]

Please remediate within SLA timeframes:
- Zone 1: 30 days
- Zone 2: 14 days
- Zone 3: 7 days
```

3. Use dynamic content from the filtered array to populate agent details

**Step 5: Send Teams Notification**

1. Add action: **Microsoft Teams - Post adaptive card in a chat or channel**
2. Configure notification:
   - **Post as:** Flow bot
   - **Post in:** Channel
   - **Team:** [Your governance team]
   - **Channel:** Agent Governance Alerts
   - **Adaptive Card:** Paste formatted message (or use adaptive card designer for rich formatting)
3. Add action buttons to the adaptive card:
   - **View Inventory:** Link to PPAC Agent Inventory
   - **View Metadata Requirements:** Link to governance document
   - **Create Remediation Ticket:** Link to change management system

**Step 6: Log Alert to Audit Trail**

1. Add action: **Dataverse - Add a new row**
2. Configure to log alert to audit table:
   - **Table name:** fsi_inventoryalerts (create this table first; see Step 8)
   - **Fields:**
     - fsi_alertdate: Current date/time
     - fsi_agentstaffected: Count of agents with issues
     - fsi_agentlist: JSON string of agent names and missing fields
     - fsi_alerttype: "Incomplete Metadata"
     - fsi_status: "Open"
3. This creates a persistent audit trail of all inventory alerts

4. Click **Save** to save the flow
5. Click **Test** > **Manually** to test the flow with current inventory data
6. Verify Teams notification is delivered and audit record is created

> **Teams Channel Setup:** Before configuring the flow, create a dedicated Teams channel (e.g., "Agent Governance Alerts") for inventory alerts. Add Power Platform Admins, AI Governance Lead, and Compliance Officer as channel members. Pin the channel for visibility.

#### Step 8: Create Audit Trail Table in Dataverse

1. Open [Power Apps](https://make.powerapps.com) and select your default or governance environment
2. Navigate to **Tables** in the left navigation
3. Click **+ New table** > **Start from blank**
4. Name the table: `fsi_inventoryalerts`
5. Add the following columns:
   - **fsi_alertdate** (Date and Time) — When the alert was generated
   - **fsi_agentstaffected** (Whole Number) — Count of agents with issues in this alert
   - **fsi_agentlist** (Multiple lines of text) — JSON or delimited list of affected agents
   - **fsi_alerttype** (Choice) — Options: Incomplete Metadata, Orphaned Agent, Unmanaged Agent, Other
   - **fsi_status** (Choice) — Options: Open, In Progress, Resolved, Closed
   - **fsi_assignedto** (Lookup to User) — Person responsible for remediation
   - **fsi_resolutiondate** (Date and Time) — When the issue was resolved
   - **fsi_resolutionnotes** (Multiple lines of text) — Remediation actions taken
6. Click **Create** to deploy the table
7. Configure security roles to allow Power Automate flows to write to this table (grant Create and Update permissions)
8. Use this table to track remediation progress and generate compliance reports

---

### Part 4: Configure Orphaned Agent Detection and Remediation

#### Step 9: Set Up PowerShell Script for Orphaned Agent Detection

While Power Automate handles real-time metadata monitoring, PowerShell scripts provide deeper analysis for orphaned agent detection.

1. Create a new PowerShell script: `Detect-OrphanedAgents.ps1` (see PowerShell Setup playbook for full script)
2. Schedule the script to run:
   - **Zone 1:** Weekly
   - **Zone 2:** Weekly
   - **Zone 3:** Daily
3. Use Windows Task Scheduler or Azure Automation to execute the script on schedule
4. Configure script to:
   - Query Agent Inventory (via API or exported CSV)
   - Cross-reference agent owners against active Entra ID users
   - Identify agents with departed owners or owners who cannot be contacted
   - Identify agents with no modifications in >12 months (stale agents)
   - Generate report of orphaned agents with recommended remediation actions
   - Send report via email to governance team or post to Teams channel
5. Test the script by executing it manually and reviewing the report output

> **Scheduled Execution:** For Zone 3 environments, configure the script to run daily at 4:00 AM (after Agent Inventory refresh and before business hours). Set up email alerts if the script fails to execute or encounters errors.

#### Step 10: Create Orphaned Agent Remediation Workflow

When orphaned agents are detected, a structured remediation workflow ensures timely resolution.

1. Document the **Orphaned Agent Remediation Workflow** in your governance repository:

**Workflow Steps:**

a. **Detection:** PowerShell script or Power Automate flow identifies orphaned agents and generates alert
b. **Notification:** Governance team receives Teams or email notification with list of orphaned agents
c. **Investigation:** Power Platform Admin researches the agent:
   - Who created the agent?
   - What environment and zone is it in?
   - Is the agent still in use? (Check usage analytics)
   - Can the original owner or team be contacted?
d. **Decision:**
   - **Option 1 - Ownership Transfer:** If agent is still in use, identify new owner and transfer ownership
   - **Option 2 - Decommissioning:** If agent is unused or abandoned, initiate decommissioning process
   - **Option 3 - Temporary Hold:** If decision is unclear, place agent in "Under Review" status and escalate to AI Governance Lead
e. **Execution:**
   - If transferring ownership: Update owner in PPAC, notify new owner, update inventory
   - If decommissioning: Follow decommissioning workflow (Step 11), archive metadata, disable agent
f. **Documentation:** Record remediation action in change management system and update audit trail table
g. **Verification:** Confirm orphaned agent no longer appears in next scheduled detection run

2. Communicate the workflow to governance team members
3. Conduct a dry-run test by simulating an orphaned agent detection and walking through the workflow
4. Measure and track remediation SLAs:
   - **Zone 1:** Resolve within 60 days
   - **Zone 2:** Resolve within 30 days
   - **Zone 3:** Resolve within 14 days

---

### Part 5: Establish Agent Decommissioning Process

#### Step 11: Create Agent Decommissioning Workflow

Decommissioning removes or disables abandoned agents while preserving metadata for audit trail.

1. Document the **Agent Decommissioning Workflow** in governance repository:

**Decommissioning Workflow Steps:**

a. **Trigger:** Orphaned agent identified, or agent marked for retirement by owner
b. **Business Validation:** Confirm agent is no longer in use:
   - Check usage analytics for last 90 days (zero usage indicates abandonment)
   - Contact business stakeholders to verify no dependencies
   - Review agent documentation for any critical business process dependencies
c. **Change Request:** Create change request in change management system:
   - Change type: Agent Decommissioning
   - Agent name, environment, owner (original)
   - Business justification for decommissioning
   - Risk assessment (impact of removal)
   - Approvals required: Power Platform Admin, AI Governance Lead (Zone 2/3), Business Owner
d. **Metadata Archival:**
   - Export agent metadata from Agent Inventory
   - Export agent configuration from Copilot Studio (if applicable)
   - Store archived metadata in SharePoint or compliance repository
   - Retain for minimum 7 years (regulatory requirement for FSI)
e. **Agent Disablement:**
   - Disable agent sharing (set to "Private" or "Only me")
   - Remove agent from organizational catalog or Teams app store
   - Disable any scheduled triggers or background processes
   - Revoke service principal or managed identity permissions (if applicable)
f. **Inventory Update:**
   - Update Agent Inventory status to "Decommissioned"
   - Add decommissioning date and reason to metadata
   - Preserve record in inventory (do not delete) for audit trail
g. **Final Deletion (Optional):**
   - After retention period (7 years for FSI), agent may be permanently deleted
   - Requires additional approval from Compliance Officer and Records Manager
   - Document deletion in audit log
h. **Notification:**
   - Notify original owner (if still employed) of decommissioning
   - Notify business stakeholders of agent removal
   - Update governance team via Teams channel

2. Create a decommissioning request template in your change management system with required fields:
   - Agent name, environment, owner
   - Business justification for decommissioning
   - Usage analytics (last 90 days)
   - Business owner approval (confirming no dependencies)
   - Risk assessment
   - Metadata archival confirmation
3. Test the workflow by decommissioning a test agent and verifying all steps are completed

> **Regulatory Retention:** FSI organizations must retain agent metadata and audit trails for minimum 7 years per FINRA 4511 and SEC 17a-4. Do not permanently delete agent records until retention period expires and appropriate approvals are obtained.

---

### Part 6: Prepare for Agent 365 Control Plane (GA May 1, 2026)

#### Step 12: Plan the Agent 365 Migration

Microsoft Agent 365 is the unified agent control plane reaching GA on **May 1, 2026**, included in the M365 E7 SKU (and as a standalone Agent 365 license at $15/user/month per Microsoft's published pricing). It introduces fine-grained RBAC, per-agent Entra Agent ID, audit logging, and policy-based blocking and quarantine for both sanctioned and shadow agents.

1. Inventory current agent governance touchpoints (PPAC Inventory, Integrated Apps, Copilot Studio sharing, DLP policies)
2. Identify which workflows in this playbook should migrate to Agent 365 once GA:
   - Discovery → Agent 365 unified registry
   - Owner validation → Entra Agent ID + Conditional Access for agents
   - Unmanaged-agent blocking → Agent 365 quarantine policy (replaces DLP-based compensating controls)
3. Confirm licensing path with Microsoft account team before May 1, 2026
4. After GA, sign in to the Agent 365 admin experience (M365 Admin Center or dedicated portal — surfaced under **Settings > Agent 365** when provisioned) using AI Administrator or Entra Global Admin
5. Enable unified discovery across Copilot Studio, M365 Copilot, Declarative Agents, and Microsoft Foundry sources
6. Configure quarantine policy thresholds (e.g., block agents missing owner metadata after 7 days in Zone 3)

> **Role limitation today:** As of April 2026, the role catalog notes that Agent 365 administrative access is initially limited to Entra Global Admin and AI Administrator. Microsoft has signaled fine-grained RBAC at GA; verify current role granularity in the role catalog ([role-catalog.md](../../../reference/role-catalog.md)) before designing operational handoffs.

#### Step 13: Configure Observability and Alerting (Post-GA)

1. In the Agent 365 admin experience, open **Observability** (or **Monitoring**)
2. Configure **Inventory Completeness Metrics** dashboards:
   - Percentage of agents with complete metadata
   - Trend charts showing improvement over time
   - Breakdown by zone, environment, owner
3. Configure alerts for: new agent without owner; ownership becomes invalid; agent exceeds staleness threshold
4. Route alerts to Teams channel, distribution list, or webhook into ServiceNow/Jira

---

### Part 7: Verification and Reporting

#### Step 14: Generate Inventory Completeness Report

1. In PPAC Agent Inventory, click **Export** to download current inventory to CSV
2. Open the CSV file in Excel or Power BI
3. Calculate **Completeness Metrics:**

| Metric | Calculation | Target |
|--------|-------------|--------|
| **Owner Assignment Rate** | (Agents with valid owner) / (Total agents) * 100% | >95% Zone 1, >98% Zone 2, >99% Zone 3 |
| **Zone Classification Rate** | (Agents with zone assigned) / (Total agents) * 100% | 100% all zones |
| **Risk Rating Completeness** | (Agents with risk rating) / (Total agents) * 100% | >90% Zone 2/3 |
| **Description Completeness** | (Agents with description ≥50 chars) / (Total agents) * 100% | >90% Zone 2/3 |
| **Approval Documentation** | (Zone 2/3 agents with approval date) / (Zone 2/3 agents) * 100% | >95% Zone 2/3 |
| **Orphaned Agent Rate** | (Agents with departed/invalid owner) / (Total agents) * 100% | <5% all zones |

4. Create visualizations (bar charts, trend lines) showing progress toward completeness targets
5. Generate monthly or quarterly report for governance leadership:
   - Executive summary of completeness metrics
   - Count of agents remediated since last report
   - Outstanding remediation items with SLA status
   - Trend analysis showing improvement or degradation
   - Recommendations for improving enforcement effectiveness

#### Step 15: Conduct Quarterly Inventory Audit

1. Schedule quarterly inventory audits (add to governance calendar)
2. For each audit, perform the following:
   - Export Agent Inventory to CSV
   - Review completeness metrics against targets
   - Identify agents with incomplete metadata and initiate remediation
   - Validate orphaned agent remediation is on track
   - Review decommissioned agents and verify metadata retention
   - Cross-reference Agent Inventory against change management tickets (verify all production agents have approved change tickets)
   - Identify any unmanaged agents (agents not registered in inventory) and investigate
   - Update mandatory metadata requirements if needed (based on lessons learned)
3. Document audit findings in a formal audit report
4. Present audit report to AI Governance Lead and Compliance Officer
5. Update enforcement procedures based on audit recommendations

---

## Configuration by Governance Level

| Setting | Baseline (Zone 1) | Recommended (Zone 2) | Regulated (Zone 3) |
|---------|-------------------|----------------------|---------------------|
| **Agent Inventory refresh frequency** | Platform-managed (~15 min) | Platform-managed (~15 min) + flow-driven daily report | Platform-managed (~15 min) + flow-driven hourly report and Teams alerts |
| **Mandatory metadata fields** | Owner, Name, Environment | + Zone, Risk Rating, Description, Approval | + Compliance Status, Audit Trail, Decommissioning Plan |
| **Pre-publication checklist enforcement** | Recommended | Required (approval gate) | Required (multi-stage approval) |
| **Orphaned agent detection schedule** | Quarterly | Monthly | Weekly |
| **Remediation SLA (metadata issues)** | 30 days | 14 days | 7 days |
| **Remediation SLA (orphaned agents)** | 60 days | 30 days | 14 days |
| **Decommissioning SLA** | 90 days | 30 days | 7 days |
| **Automated monitoring (Power Automate)** | Optional | Recommended (daily) | Required (daily + real-time) |
| **Audit trail persistence** | 3 years | 5 years | 7 years (regulatory requirement) |
| **Quarterly inventory audit** | Recommended | Required | Required (+ external audit verification) |

---

## Validation

After completing these steps, verify:

- [ ] Power Platform Inventory accessible to designated Power Platform Admins (refresh ~15 min)
- [ ] Baseline inventory export captured for pre-enforcement comparison
- [ ] Mandatory metadata requirements documented and communicated to agent authors
- [ ] Pre-publication checklist created and integrated into agent approval workflow
- [ ] Ownership validation process established with recurring tasks scheduled
- [ ] Power Automate flow built on **Power Platform for Admins V2** connector deployed and tested
- [ ] Teams channel for governance alerts is created and team members added
- [ ] Audit trail table (fsi_inventoryalerts) deployed in Dataverse
- [ ] PowerShell script for orphaned agent detection deployed and scheduled
- [ ] Orphaned agent remediation workflow documented and tested
- [ ] Agent decommissioning workflow documented with change request template
- [ ] Agent 365 migration plan documented (target: post-May 1, 2026 GA)
- [ ] Inventory completeness report generated and reviewed by governance team
- [ ] Quarterly inventory audit scheduled and first audit completed
- [ ] Completeness metrics meet or exceed targets (>95% owner assignment, >90% zone classification)

---

## Visual Reference

Expected portal locations:

- **PPAC Power Platform Inventory:** Power Platform Admin Center → Manage → Inventory → Agents
- **Inventory Filters / Columns:** PPAC → Inventory → Filter and Customize Columns toolbar
- **Ownership Transfer:** PPAC → Environments → [Environment] → Resources → [Agent] → Manage sharing → Transfer ownership
- **Power Automate Completeness Monitor:** Power Automate (make.powerautomate.com) → My flows → Agent Inventory Completeness Monitor (built on Power Platform for Admins V2 connector)
- **Dataverse Audit Table:** Power Apps (make.powerapps.com) → Tables → fsi_inventoryalerts → Data
- **Agent 365 Control Plane:** M365 Admin Center → Settings → Agent 365 (post-May 1, 2026 GA)
- **Teams Alerts Channel:** Microsoft Teams → [Governance Team] → Agent Governance Alerts channel

> **UI Note:** Power Platform Inventory is GA (Feb 9, 2026). Navigation labels can shift; Microsoft has merged the inventory under the unified **Manage > Inventory** node. If labels differ, search the PPAC global search bar for "Inventory".

---

[Back to Control 3.11](../../../controls/pillar-3-reporting/3.11-centralized-agent-inventory-enforcement.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
