# Control 4.9 — Portal Walkthrough: Embedded File Content Governance

**Playbook Type:** Portal Walkthrough
**Control:** [4.9 — Embedded File Content Governance](../../../controls/pillar-4-sharepoint/4.9-embedded-file-content-governance.md)
**Audience:** M365 Administrators, SharePoint Admins, Compliance Officers
**Estimated Time:** 30–60 minutes (initial setup); 20–30 minutes (quarterly audit cycle)
**Last UI Verified:** April 2026

!!! danger "Critical IB Limitation — Read Before Proceeding"
    Microsoft Purview Information Barriers are NOT enforced on SharePoint Embedded containers. Any user with access to an agent can receive content from embedded knowledge files regardless of IB policy assignments. Complete the IB assessment steps in this walkthrough (Section 4) before approving any agent with embedded files for Zone 2 or Zone 3 deployment. See Control 4.9 for the full compliance risk analysis.

## Overview

This walkthrough covers all portal-based administrative procedures for Control 4.9, including:

1. Identifying all agents that use embedded file knowledge sources
2. Reviewing per-agent embedded file metadata (file names, sensitivity labels, container IDs)
3. Performing the quarterly sensitivity label audit
4. Auditing SharePoint Embedded containers via SharePoint Admin Center
5. Conducting an IB boundary assessment before file uploads
6. Configuring the default sensitivity label policy for unlabeled files
7. Configuring SharePoint container creation alerts

---

## Section 1: Identify All Agents Using Embedded Files

This step produces the complete list of agents that require Control 4.9 governance attention. Run this procedure at the start of every quarterly audit cycle and whenever a new agent is created.

### Step 1.1 — Open the All Agents Page

1. Navigate to the **Microsoft 365 Admin Center**: [https://admin.microsoft.com](https://admin.microsoft.com)
2. In the left navigation, select **Copilot** (you may need to expand the navigation panel).
3. Select **Agents**.
4. Select **All Agents** from the sub-navigation.

> Portal path: **M365 Admin Center › Copilot › Agents › All Agents**

### Step 1.2 — Apply the Embedded Files Filter

1. On the All Agents page, locate the **Filter** control above the agent list.
2. Click **Filter** and select or search for the **"Embedded files"** filter option.
3. Apply the filter.

The page now displays only agents that have at least one embedded file knowledge source.

!!! note "Filter Scope"
    This filter shows agents created via Agent Builder that have files stored in SharePoint Embedded containers. Agents built in Copilot Studio or agents that use SharePoint site knowledge (not uploaded files) will not appear under this filter. If you expect an agent to appear and it does not, see the Troubleshooting playbook Section 1.

### Step 1.3 — Export the Agent List for Audit Records

1. Use the **Export** option on the All Agents page (if available in your tenant) to export the filtered list to CSV.
2. If export is not available, manually record: Agent Name, Agent Owner, Creation Date, Last Modified Date, for each agent in the filtered view.
3. Save the exported file as: `embedded-file-agents-audit-YYYY-QN.csv` (e.g., `embedded-file-agents-audit-2026-Q1.csv`).
4. Store in your designated audit evidence repository.

---

## Section 2: Review Per-Agent Embedded File Metadata

For each agent identified in Section 1, review the detailed embedded file information. This step validates that files are labeled and provides the container ID for cross-referencing with SharePoint Admin Center.

### Step 2.1 — Open the Agent Detail View

1. From the filtered All Agents list, click the **agent name** to open the agent detail panel or page.

### Step 2.2 — Review the Data & Tools Tab

1. Select the **Data & tools** tab in the agent detail view.
2. Review the following fields for each embedded file:

   | Field | What to Check |
   |---|---|
   | **File name** | Record each file name. Does the name suggest IB-restricted content (e.g., "deal-pipeline-Q1.pdf", "research-report-AAPL.docx")? Flag for IB review. |
   | **File sensitivity** | Is a sensitivity label present? If blank or "None", this is a gap — flag for remediation. |
   | **SharePoint Container ID** | Record the container ID (GUID format). This is used to cross-reference in SharePoint Admin Center. |

3. Record findings in your audit worksheet.

### Step 2.3 — Review the Overview Tab for Agent-Level Sensitivity Label

1. Select the **Overview** tab in the agent detail view.
2. Locate the **Sensitivity label** field.
3. Verify the label reflects the most restrictive label of the embedded files (per Microsoft's label inheritance behavior).
4. If the field is blank, the agent has no sensitivity label — this is a compliance gap requiring remediation.

!!! warning "Sensitivity Label Gap — Remediation Required"
    If an agent shows no sensitivity label on the Overview tab, either the uploaded files were unlabeled and no default label policy is configured, or the label policy has not yet applied. See Section 6 (Configure Default Sensitivity Label Policy) and the Troubleshooting playbook for remediation steps.

---

## Section 3: Audit SharePoint Embedded Containers

This step provides a view of all SharePoint Embedded containers across the tenant associated with the Declarative Agent application. Use this as a secondary inventory check and to verify container health.

### Step 3.1 — Access SharePoint Admin Center

1. Navigate to the **SharePoint Admin Center**: [https://admin.microsoft.com/sharepoint](https://admin.microsoft.com/sharepoint) or via M365 Admin Center › SharePoint.
2. In the left navigation, select **More features** or navigate directly to the appropriate SharePoint Admin URL for your tenant.

> Direct URL pattern: `https://[tenant]-admin.sharepoint.com`

### Step 3.2 — Filter for Declarative Agent Containers

1. In SharePoint Admin Center, locate the **Active sites** section or the container management view (this may appear under **Content services** depending on your admin center version).
2. Apply a filter or search for application name: **"Declarative Agent"**.
3. The resulting list shows all SharePoint Embedded containers associated with M365 Copilot agents that use embedded file knowledge sources.

### Step 3.3 — Reconcile Containers Against the Agent Inventory

1. For each container in the SharePoint Admin Center list, record:
   - Container ID (GUID)
   - Application name ("Declarative Agent")
   - Container creation date
   - Storage used
2. Cross-reference each Container ID against the container IDs recorded from agent metadata in Section 2.
3. Identify any containers that do not match a known active agent — these may be orphaned containers from deleted agents that did not follow proper deletion workflow.

!!! warning "Orphaned Containers"
    Orphaned containers (containers with no associated active agent) may contain residual file content. These containers should be documented and reviewed by the compliance team before any remediation action. Do not delete containers without confirming there is no active agent dependency. See the Troubleshooting playbook for the correct recovery procedure if a container was accidentally deleted.

### Step 3.4 — Verify No Containers Were Directly Deleted

1. Review the SharePoint audit log for any container deletion events.
2. Navigate to: **Microsoft Purview Compliance Portal › Audit** and search for audit operations on SharePoint Embedded containers.
3. If any container deletion events appear outside of agent deletion workflows, investigate immediately and escalate to the agent owner and compliance team.

---

## Section 4: IB Boundary Assessment Before File Uploads (Zone 2 and Zone 3)

This section must be completed before any file is uploaded to an agent operating in Zone 2 (team/departmental) or Zone 3 (enterprise). This is a procedural control that compensates for the platform-level IB limitation.

### Step 4.1 — Identify the Agent's User Population

1. Determine who will have access to the agent. Review:
   - Agent sharing settings (who the agent is shared with)
   - Group memberships for shared groups
   - Anticipated user base as documented by the agent owner

2. Identify the **business lines** represented by the user population. Examples:
   - Sales and Trading
   - Investment Banking / Capital Markets
   - Equity Research
   - Asset Management
   - Retail Banking
   - Compliance / Legal

### Step 4.2 — Identify the Content of Each File to Be Uploaded

1. For each file the agent owner proposes to upload, determine:
   - What business function created the file
   - Whether the file contains information that is subject to an IB wall (e.g., deal pipeline data, research pre-publication, material non-public information)
   - The file's current sensitivity label (if any)

### Step 4.3 — Assess for IB Wall Conflicts

1. Using the firm's current IB segment map (maintained by Compliance), determine whether any IB wall exists between:
   - The business line that owns/created the file content, and
   - Any business line represented in the agent's user population

2. If an IB wall conflict is identified:
   - **Zone 2:** Block the file upload. Notify the agent owner that the file cannot be embedded without a compliance review.
   - **Zone 3:** Block the file upload. The entire embedded files capability must be prohibited for this agent unless the compliance officer provides Zone 3 exception sign-off (see Step 4.4).

3. If no IB wall conflict is identified:
   - Document the assessment result: "No IB wall conflict identified between content source [Business Line A] and agent user population [Business Lines B, C]."
   - Store the assessment in the agent inventory record (Control 3.1).

### Step 4.4 — Zone 3 Exception Process (If Required)

If the agent owner requires embedded files for a Zone 3 agent and the compliance team determines all content is genuinely IB-exempt for the full user population:

1. Agent owner submits a written request to the Compliance Officer documenting:
   - Agent name and ID
   - Each file proposed for embedding (name, sensitivity label, content summary)
   - Each IB segment in the agent's user population
   - Justification that the content is IB-exempt for all segments

2. Compliance Officer reviews and, if approved, provides written sign-off stating:
   - All listed files are IB-exempt for the stated user population
   - The approval date and any conditions or expiration (recommend annual renewal)

3. Store the signed exception document in the agent inventory record (Control 3.1) and in the examination-ready compliance file.

---

## Section 5: Register Agent in the Agent Inventory (Control 3.1)

All agents with embedded files must be registered in the enterprise agent inventory (Control 3.1) with the following embedded-file-specific metadata fields populated.

### Step 5.1 — Open Agent Inventory

Navigate to your organization's agent inventory system (SharePoint list, ServiceNow catalog, or equivalent as defined in Control 3.1).

### Step 5.2 — Create or Update the Agent Record

For the agent, populate or verify the following fields in the inventory record:

| Field | Value |
|---|---|
| Agent Name | As shown in M365 Admin Center |
| Agent ID / Container ID | Container ID from Data & tools tab |
| Embedded Files (Y/N) | Y |
| Embedded File Names | Comma-separated list of all file names |
| Embedded File Sensitivity Labels | Labels for each file; flag any unlabeled files |
| Zone | 1 / 2 / 3 |
| IB Assessment Status | Assessed — No Conflict / Assessed — IB-Exempt (with sign-off reference) / Pending |
| IB Assessment Date | Date of last assessment |
| IB Exception Sign-Off Reference | Reference to exception document (Zone 3 only) |
| Last Container Audit Date | Date of most recent quarterly container audit |

---

## Section 6: Configure Default Sensitivity Label Policy for Unlabeled Files

Configuring a default sensitivity label policy ensures that any file uploaded to an agent without an existing sensitivity label automatically receives a baseline label — preventing unlabeled containers.

### Step 6.1 — Open Microsoft Purview Information Protection

1. Navigate to the **Microsoft Purview Compliance Portal**: [https://compliance.microsoft.com](https://compliance.microsoft.com)
2. In the left navigation, expand **Information protection**.
3. Select **Label policies**.

> Portal path: **Microsoft Purview › Information Protection › Label policies**

### Step 6.2 — Review Existing Default Label Policy

1. Review the list of label policies. Identify any policy that is marked as the default or global policy.
2. Click the policy to review its settings.
3. Locate the **Default label settings** section.
4. Verify that a default label is configured for **documents** (this applies to files uploaded to SharePoint Embedded containers).

### Step 6.3 — Configure or Update Default Label

If no default label is configured for documents:

1. Edit the label policy.
2. In the **Default label settings**, for the **Documents** category, select a label appropriate for your organization's baseline classification (e.g., "Internal Use", "General").
3. Confirm the policy scope includes the users and groups who will be uploading files to agents.
4. Save the policy.

!!! note "Label Policy Propagation Time"
    Changes to label policies may take up to 24 hours to propagate across the tenant. Plan accordingly when deploying new agents with embedded files.

### Step 6.4 — Test Default Label Application

1. Ask a test user to upload an unclassified document to a test agent via Agent Builder.
2. After upload, navigate to M365 Admin Center › Copilot › Agents › [Test Agent] › Overview tab.
3. Verify the Sensitivity label field shows the expected default label.
4. Document the test result as evidence of label policy configuration effectiveness.

---

## Section 7: Configure SharePoint Container Creation Alerts

Configuring alerts for new Declarative Agent container creation provides proactive visibility into embedded file agent deployments.

### Step 7.1 — Access SharePoint Admin Center Alerts (If Available)

Depending on your tenant configuration and admin center version:

1. Navigate to **SharePoint Admin Center**.
2. Review available alert and notification settings under **Settings** or **Content services**.
3. If container creation alerts are available as a native feature, configure an alert to notify SharePoint administrators and the compliance mailbox when a new container with application "Declarative Agent" is created.

### Step 7.2 — PowerShell-Based Monitoring (Alternative)

If native portal alerts are not available for container creation, use the PowerShell monitoring approach documented in the [PowerShell Setup playbook](powershell-setup.md), Section 4.

### Step 7.3 — M365 Audit Log Alert (Recommended)

1. Navigate to **Microsoft Purview Compliance Portal › Audit › Alert policies**.
2. Create a new alert policy for SharePoint file and container events related to Declarative Agent application activity.
3. Configure the alert to notify the SharePoint admin and compliance teams.
4. Test the alert by creating a test agent with an embedded file.

---

## Quarterly Audit Checklist

Use this checklist at the start of each quarterly audit cycle:

- [ ] Step 1: Run M365 Admin Center embedded files filter — export agent list
- [ ] Step 2: For each agent, review Data & tools tab (file names, sensitivity, container ID)
- [ ] Step 2.3: For each agent, verify Overview tab sensitivity label is populated
- [ ] Step 3: Run SharePoint Admin Center Declarative Agent container list — reconcile with agent inventory
- [ ] Step 3.3: Identify and document any orphaned containers
- [ ] Step 3.4: Review audit log for unauthorized container deletions
- [ ] Step 5: Verify agent inventory (Control 3.1) records are current for all embedded file agents
- [ ] Step 6.2: Verify default sensitivity label policy is still configured and scoped correctly
- [ ] Document: Date, auditor name, findings, and remediation actions in quarterly audit report
- [ ] Archive: Quarterly audit report in examination-ready compliance file

---
[Back to Control 4.9](../../../controls/pillar-4-sharepoint/4.9-embedded-file-content-governance.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
*Updated: April 2026 | Version: v1.4.0 | UI Verification Status: Current*
