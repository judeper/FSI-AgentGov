# Control 2.25: Microsoft Agent 365 — Admin Center Governance Console — Portal Walkthrough

This playbook provides step-by-step portal configuration guidance for Control 2.25. All steps reflect the Microsoft 365 Admin Center experience as verified in March 2026 under the Frontier Preview program. Screenshots and navigation labels may change at General Availability (May 1, 2026).

!!! info "Frontier Preview Requirement"
    The Agents section in the M365 Admin Center is only visible after Frontier enrollment. Complete Step 1 (Frontier Enrollment) before attempting any subsequent steps. Skipping enrollment will result in the Agents navigation item not appearing.

## Prerequisites

- Global Administrator or delegated M365 Admin Center access with Agents management permissions
- At least one Microsoft 365 Copilot license assigned in the tenant
- Frontier enrollment completed or planned as part of this walkthrough (Step 1)
- Familiarity with your organization's AI governance policy defining Zone 2/Zone 3 boundaries
- Change management ticket open for this configuration activity (per Control 2.3)
- Compliance officer notified if this walkthrough includes Zone 3 agent approvals

## Step 1: Enroll in Copilot Frontier

**Portal Path:** M365 Admin Center > Copilot > Settings > User Access > Copilot Frontier

Navigate to the Microsoft 365 Admin Center at [https://admin.microsoft.com](https://admin.microsoft.com). In the left navigation, expand **Copilot** and select **Settings**. On the Settings page, click the **User Access** tab, then locate the **Copilot Frontier** section.

Toggle Frontier enrollment to **Enabled**. The system will provision Frontier capabilities, including the Agent 365 licenses and the Agents navigation section, within approximately 15–60 minutes. Do not proceed to Step 2 until provisioning completes.

After enabling, navigate to **Billing > Licenses** and confirm that **Agent 365 Frontier** licenses appear in your license inventory. The default allocation is **25 licenses per tenant**.

| Setting | Value | Notes |
|---|---|---|
| Copilot Frontier toggle | Enabled | Required before Agents section appears in nav |
| Agent 365 Frontier licenses | 25 (default) | Confirmed under Billing > Licenses |
| Microsoft 365 Copilot license | At least 1 assigned | Hard prerequisite for Frontier availability |

!!! warning "Provisioning Delay"
    After enabling Frontier, wait up to 60 minutes before the Agents navigation section becomes visible. If the section does not appear after 60 minutes, see the [Troubleshooting playbook](troubleshooting.md) for the Frontier visibility issue.

## Step 2: Access the Agent 365 Overview Dashboard

**Portal Path:** M365 Admin Center > Agents > Overview

Once Frontier provisioning is complete, a new **Agents** section will appear in the left navigation of the M365 Admin Center. Click **Agents** to expand it, then select **Overview**.

Review the following elements on the Overview page:

**Hero Metrics (last 30 days):**

| Metric | Description | Governance Use |
|---|---|---|
| Agent Registry | Total agents in tenant inventory | Baseline count for monthly inventory export |
| Active Users | Unique users who interacted with agents | Tracks adoption; anomalies may indicate unauthorized use |
| Total Sessions | Total agent interaction sessions | Workload baseline; compare month-over-month |
| Exception Rate | % of sessions completing without errors | Primary health indicator; establish your threshold (e.g., >5% = escalate) |
| Agent Runtime | Total cumulative agent execution time | Capacity and cost planning |

!!! note "Metrics Coverage"
    Hero metrics and analytics are currently supported only for agents built with: Copilot Agent Builder, SharePoint, Microsoft 365 Agents Toolkit, and agents instrumented with the Observability SDK. Agents from other sources (e.g., third-party platforms without SDK integration) will appear in the registry but will not contribute metrics data. Document this coverage gap in your monitoring runbook.

**Governance Cards:**

Scroll below the hero metrics to locate the two governance action cards:

- **Pending Requests:** Displays all agent publication and activation requests awaiting admin review, sorted oldest-first. A week-over-week delta badge shows whether the queue is growing or shrinking. Act on these requests per your SLA (5 business days for Zone 2, 1 business day for Zone 3).
- **Ownerless Agents:** Lists all agents in the registry with no assigned owner. Click **Assign Owner** inline for each agent to immediately assign accountability. Every entry on this card is a supervisory risk under FINRA Rule 3110.

**Agent Analytics (lower section):**

| Chart | Description | FSI Use |
|---|---|---|
| Agents by Publishers | Org-created vs. external agents | Tracks shadow AI; unexpected external agent growth warrants investigation |
| Agents by Platforms | Copilot Studio, Azure AI Foundry, partner platforms | Supports vendor risk inventory under OCC 2011-12 |
| Active Users Over Time | Trend chart of agent usage | Detects usage spikes or drops requiring investigation |

## Step 3: Configure the Agent Publishing Approval Workflow

**Portal Path:** M365 Admin Center > Agents > All Agents > Registry > Requests tab

In the Agents section, click **All Agents**, then select the **Registry** view. Within the Registry, locate the **Requests** tab. This tab surfaces all pending publication and activation requests submitted by users or developers in your tenant.

For each pending request, perform the following review:

| Review Item | Action | Regulatory Basis |
|---|---|---|
| Agent description | Confirm it accurately describes the agent's purpose and function | FINRA 3110 — supervisor must understand what is being supervised |
| Agent owner | Verify a named, accountable individual is assigned | FINRA 3110 — supervisory chain; SOX 404 — control ownership |
| Data connections | Review what data sources the agent accesses (SharePoint sites, Exchange, external APIs) | SEC 17a-3/4 — records scope; OCC 2011-12 — data risk |
| Tools | Review what actions the agent can take (send email, create files, call APIs) | OCC 2011-12 — action risk assessment |
| Audience scope | Confirm the proposed user/group scope is appropriate; do not approve org-wide scope without compliance sign-off for Zone 3 agents | SOX 302 — management must understand control scope |

To approve a request, click the request row, review all details, then click **Approve**. You will be prompted to scope the audience before final approval. For Zone 3 agents, confirm compliance officer sign-off exists before clicking the final Approve button.

To reject a request, click **Reject** and provide a written rejection reason. The reason is retained in the approval history and constitutes an audit record.

!!! warning "No Bypass for Zone 2/3 Agents"
    Never approve a Zone 2 or Zone 3 agent request that lacks a named owner, a documented purpose, or compliance sign-off (Zone 3 only). Approving incomplete requests creates a supervisory gap that cannot be retroactively corrected without re-initiating the approval workflow.

## Step 4: Apply a Governance Template During the Publishing Wizard

**Portal Path:** M365 Admin Center > Agents > All Agents > Registry > [Agent] > Publish (or via Requests approval workflow)

When publishing a new agent or approving a publication request, the Publishing Wizard will present a multi-step flow. At the **Apply Template** step, select the appropriate governance template:

| Zone | Template | Required Policies Included |
|---|---|---|
| Zone 1 | None required (optional Default) | — |
| Zone 2 | Default Governance Template (minimum) | Entra Identity Protection for agents, Entra Network Visibility (GSA), Entra Lifecycle Management, SharePoint external sharing restrictions, SharePoint Site Access Control, SharePoint Agent Access Insights, Purview Audit, Purview Know Your Data Policy, Purview AI Compliance Assessment, auto Agent 365 license assignment |
| Zone 3 | Custom Governance Template (mandatory) | All Default policies PLUS Entra Access Package (minimum); add additional policies per your security architecture |

**To apply the Default Template:**
1. In the Apply Template step, select **Default Template** from the template picker.
2. Review the policy bundle displayed in the confirmation panel.
3. Confirm that admin consent is available for all policies listed. If any policy shows a consent required warning, click **Grant Consent** before proceeding.
4. Click **Apply** to attach the template to this agent.

**To create and apply a Custom Template (Zone 3):**
1. Navigate to Agents > Settings (or Governance Templates if available in your build) and click **New Template**.
2. Start from the Default Template as a base.
3. Add **Entra Access Package** from the additional policy picker.
4. Add any additional policies required by your security architecture (e.g., Purview DLP policy, additional Conditional Access policies per Control 1.11).
5. Name the template using your naming convention (e.g., `FSI-Zone3-Custom-v1`).
6. Save the template, then return to the publishing wizard and select your custom template.

!!! note "Auto License Assignment"
    The Default and Custom Governance Templates automatically assign an Agent 365 license to the agent instance. You do not need to manually assign licenses when using governance templates. This eliminates a common manual step that previously caused agents to fail activation.

## Step 5: Configure Researcher with Computer Use

**Portal Path:** M365 Admin Center > Agents > Researcher > Computer Use tab

!!! info "Frontier-Only Feature"
    Researcher with Computer Use is a Frontier Preview feature. It will not appear in the Agents navigation unless your tenant is enrolled in Frontier. At GA (May 1, 2026), this capability's availability and admin configuration surface may change.

In the Agents section, click **Researcher** in the left sub-navigation, then select the **Computer Use** tab.

Make an affirmative configuration decision for each of the three settings. Do not leave these at default without documentation.

**Access Configuration:**

| Setting | Options | Zone 3 Recommendation |
|---|---|---|
| Who has access | All users / Specific groups / No users | Specific groups (named approved group only) |
| Work Access toggle | On / Off | Off unless explicitly approved by CISO in writing |
| Website Access | Allow all / Allow specific URLs / Exclude specific URLs | Allow specific URLs (approved allowlist only) |

**For Zone 3 institutions:**
1. Set **Who has access** to **Specific groups**.
2. Click **Add group** and select the pre-approved security group defined in your AI governance policy (e.g., `sg-agent365-researcher-approved`).
3. Set **Work Access** toggle to **Off** unless a specific, written CISO approval exists permitting agents to use work content in Computer Use sessions.
4. Set **Website Access** to **Allow specific URLs** and enter the approved URL allowlist. For financial services, this list should typically include only internal tools, approved research platforms (e.g., Bloomberg terminal URLs if applicable), and firm-approved external data sources. Exclude social media, personal email, and any site not explicitly reviewed by Information Security.
5. Click **Save** and document the configuration decision with the approving CISO's name and date in your governance log.

**For Zone 2 institutions:**
1. Set **Who has access** to **Specific groups** or **No users** depending on your use case.
2. Set **Website Access** to **Exclude specific URLs** at minimum, with a blocklist covering social media, personal email, and other non-business sites.
3. Document the configuration decision in your governance log.

## Step 6: Export Agent Inventory

**Portal Path:** M365 Admin Center > Agents > All Agents > Export button

Regular inventory exports are required for examination readiness and SEC 17a-4 recordkeeping obligations. Perform this export at least monthly for Zone 3, quarterly for Zone 2.

1. Navigate to **Agents > All Agents**.
2. Optionally apply filters (e.g., by platform, by status) if you need platform-specific reports. For the monthly compliance export, clear all filters to capture the full inventory.
3. Click the **Export** button in the toolbar.
4. Save the downloaded file to your compliance repository. Use a filename convention that includes the ISO 8601 date, for example: `agent-inventory-2026-03-22.csv`.
5. Confirm the export file contains the following fields at minimum: Agent Name, Agent ID, Publisher, Platform, Owner, Status, Deployment Scope, Governance Template Applied, Last Modified Date.
6. Log the export action in your governance activity log with: exporter name, date, scope, retention location, and next scheduled export date.

| Export Field | Compliance Purpose | Regulatory Reference |
|---|---|---|
| Agent Name / ID | Unique identifier for records | SEC 17a-4 records requirement |
| Publisher | Org vs. external vendor tracking | OCC 2011-12 vendor risk |
| Owner | Supervisory chain evidence | FINRA Rule 3110 |
| Status | Active/inactive/blocked state | SOX 404 control state |
| Governance Template | Policy coverage confirmation | OCC 2011-12 / SOX 404 |
| Last Modified Date | Change history anchor | SEC 17a-4 / SOX audit trail |

!!! note "Retention Schedule"
    Store inventory exports in a write-once or immutable storage location consistent with SEC Rule 17a-4(f) electronic storage requirements. Minimum retention is 3 years for general records; 6 years for broker-dealer records related to customer accounts or communications. Consult your records management policy for your firm's specific schedule.

---

[Back to Control 2.25](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

*Updated: March 2026 | Version: v1.3*
