# Playbook 3.13-A: Portal Walkthrough — Accessing and Navigating Agent 365 Analytics

**Playbook ID:** 3.13-A
**Control:** 3.13 — Agent 365 Admin Center Analytics and Reporting
**Pillar:** Reporting
**Estimated Duration:** 30–45 minutes (initial setup); 10–15 minutes (recurring review)
**Required Role:** Entra Global Admin or Microsoft 365 AI Administrator
**Last Verified:** April 2026

---

!!! info "Hero Metrics Availability"
    The hero metrics on the Agent 365 Overview page (Active Users, Total Sessions, Exception Rate, Agent Runtime) reached **General Availability on May 1, 2026** for tenants with Agent 365 or Microsoft 365 E7 licensing. The Agent Registry and governance cards (Pending Requests, Ownerless Agents) were Generally Available pre-Agent-365-GA and remain accessible. Steps that depend on hero metrics require Microsoft Agent 365 or Microsoft 365 E7 licensing — these are flagged **[Requires Agent 365 / E7 licensing]**.

---

## Overview

This playbook walks compliance officers, IT governance leads, and M365 administrators through the complete process of accessing, navigating, and extracting value from the Agent 365 Admin Center Analytics dashboard for supervisory and recordkeeping purposes. It establishes the step-by-step procedure that should be documented in the firm's written supervisory procedures (WSPs) under FINRA Rule 3110.

---

## Prerequisites

Before beginning this walkthrough, confirm the following:

- [ ] You have a Microsoft 365 Entra Global Admin or AI Administrator account for the target tenant.
- [ ] Multi-factor authentication (MFA) is enabled and functioning for your admin account.
- [ ] If accessing hero metrics: the tenant has Microsoft Agent 365 or Microsoft 365 E7 licensing provisioned.
- [ ] You have reviewed Control 3.13 and understand the Zone designation applicable to your organization.
- [ ] A review log (spreadsheet, GRC ticket, or supervisory log entry) is ready to record the date, reviewer identity, and findings of this session.

---

## Step 1: Access the Microsoft 365 Admin Center

**1.1** Open a browser in a private/incognito session to prevent cached credential interference.

**1.2** Navigate to: `https://admin.microsoft.com`

**1.3** Sign in with your Entra Global Admin or AI Administrator credentials. Complete MFA if prompted.

**1.4** Confirm you are in the correct tenant by verifying the tenant name displayed in the upper-right corner of the Admin Center. If you manage multiple tenants, use the tenant switcher before proceeding.

!!! warning "Tenant Verification"
    Always confirm the active tenant before performing governance reviews or exports. An inventory export from a test or development tenant instead of the production tenant will produce an incomplete or misleading examination artifact.

---

## Step 2: Navigate to Agent 365 Overview

**2.1** In the left navigation pane, locate the navigation links. If the "Agents" item is visible directly in the nav, select it and skip to Step 2.3.

**2.2** If "Agents" is not immediately visible, select **"Show all"** at the bottom of the left navigation pane to expand the full navigation tree.

**2.3** In the expanded navigation, select **"Agents"**. This will expand the Agents submenu.

**2.4** Select **"Overview"** from the Agents submenu. The Agent 365 Overview page will load.

!!! note "Navigation Variability"
    The M365 Admin Center navigation layout may vary based on your Microsoft 365 license, tenant configuration, and any Admin Center preview features enabled. If "Agents" is not visible even after selecting "Show all," verify that your account has the required AI Administrator or Global Admin role and that your tenant has M365 Copilot licensing.

---

## Step 3: Review the Agent Registry Count

**3.1** On the Overview page, locate the **Agent Registry** hero card. This displays the total count of all agents deployed in the tenant — including Microsoft-built agents, partner-built (external) agents, and custom/line-of-business agents.

**3.2** Record the Agent Registry count in your supervisory review log with today's date.

**3.3** Compare the current count to the count recorded in the previous review session. If the count has increased, proceed to Step 5 to review the All Agents list and identify new deployments. If the count has decreased, investigate whether agents have been decommissioned or unregistered; document the reason.

---

## Step 4: Review Hero Metrics [Requires Agent 365 / E7 licensing]

!!! info "Availability"
    Steps 4.1–4.5 require Frontier enrollment before May 1, 2026 GA. From May 1, 2026, hero metrics are available to all tenants with Agent 365 / Microsoft 365 E7 licensing. If your tenant has neither, skip to Step 5.

**4.1** On the Overview page, locate the four hero metric cards:
- **Active Users**: unique users who interacted with at least one agent in the last 30 days
- **Total Sessions**: complete agent invocations in the last 30 days
- **Exception Rate**: percentage of sessions completing without errors
- **Agent Runtime**: total agent-assisted time in the last 30 days

**4.2** Record all four metric values in your supervisory review log.

**4.3** Exception Rate Assessment (Exception Rate = % of sessions that completed without errors; higher is better):

- If exception rate is **at or above 95%**: within normal operating range. Note the value.
- If exception rate has **declined 5 or more percentage points** since last review: flag as anomaly. Create a remediation ticket and notify the IT governance lead and affected agent owners. Do not close the review without documenting the alert.
- If exception rate is **below 85%**: escalate to the CISO and CCO immediately. Treat as a potential systemic agent reliability event.

**4.4** Active Users and Total Sessions Assessment:
- Unexplained spikes in Active Users or Total Sessions may indicate unauthorized agent usage or a misconfigured agent generating automated sessions. Flag significant anomalies (greater than 20% week-over-week change) for investigation.
- Unexplained declines in Active Users may indicate a user-facing agent failure or access revocation event.

**4.5** Record findings and any remediation actions initiated in the supervisory review log.

---

## Step 5: Review Agent Analytics — Publisher and Platform Breakdown

**5.1** Scroll down on the Overview page to locate the **Agents by Publishers** chart.

**5.2** Review the breakdown between:
- **Created by your organization**: agents built internally, subdivided into (a) shared by creator and (b) used only by creator.
- **Created by external partners**: agents sourced from third-party vendors.

**5.3** If the external partner agent count has increased since the last review, identify the new partner agents in the All Agents list (Step 6) and confirm they have been reviewed through the firm's third-party risk management process.

**5.4** Locate the **Agents by Platforms** chart. Review the distribution across:
- Copilot Studio (Full License)
- Copilot Studio (Lite License)
- Azure AI Foundry
- External partner platforms

**5.5** Record platform distribution in the supervisory review log. Any agents on external partner platforms require confirmation that those platforms are on the firm's approved vendor list.

**5.6** Locate the **Active Users Over Time** chart. Review the 30-day daily trend for:
- Consistent upward trend: adoption is progressing normally.
- Sharp spike followed by decline: may indicate a viral informal deployment or an agent that failed shortly after launch.
- Sustained decline: may indicate user experience issues, access problems, or a deprecated agent still registered.

---

## Step 6: Review Governance Cards

**6.1** Locate the **Pending Requests** governance card.

**6.2** Note the pending request count and the week-over-week delta badge.

**6.3** If pending requests exist:
- Select the **"Manage requests"** button. This navigates to Agent Registry > Requests tab.
- Review each pending request: agent name, requesting user, submission date, and description.
- Disposition each request (approve or deny) within your Zone's defined SLA:
  - Zone 1: 30 days
  - Zone 2: 5 business days
  - Zone 3: 48 hours
- Document each disposition decision (approved/denied, rationale, reviewer identity) in the supervisory review log.

**6.4** Locate the **Ownerless Agents** governance card.

**6.5** Note the ownerless agent count.

**6.6** If ownerless agents exist:
- Select the **"Assign Owner"** button. This navigates to Agent Registry > Ownerless Agents filter.
- For each ownerless agent, identify the appropriate business line owner and assign ownership.
- If the agent has no identifiable business purpose or owner, escalate to the CISO for potential decommissioning review.
- Document all ownership assignments in the supervisory review log.

!!! danger "Ownerless Agents — Regulatory Risk"
    An ownerless agent represents unattended automation with no accountable party. Under FINRA Rule 3110, every automated system performing regulated functions must have an identified supervisory owner. Ownerless agents that process client data or perform regulated functions without an assigned owner create a direct supervisory compliance deficiency. Remediate all ownerless agents within the SLA required by your Zone designation.

---

## Step 7: Export Agent Inventory

**7.1** In the Agents submenu, select **"All Agents"** to navigate to the full agent list.

**7.2** Review the agent list briefly to confirm completeness. Verify that:
- Agents you are aware of are listed.
- No unexpected agents appear that were not previously known.

**7.3** Locate the **Export** button in the top-right area of the agent list (above the table).

**7.4** Select **Export**. The admin center will generate and download a CSV file containing the full agent inventory.

**7.5** Immediately rename the exported file using the following naming convention to create a dated examination artifact:

```
AgentInventory_[TenantName]_[YYYYMMDD].csv
```

Example: `AgentInventory_ContosoCapital_20260322.csv`

**7.6** Store the renamed file in the firm's designated records repository (SharePoint records library, immutable blob storage, or document management system) in accordance with the firm's SEC 17a-4 retention policy.

**7.7** Record the export in the supervisory review log: date exported, filename, storage location, and reviewer identity.

!!! warning "Export Retention Schedule"
    - **Zone 1**: Export quarterly; retain 3 years minimum.
    - **Zone 2**: Export quarterly; retain 3 years minimum.
    - **Zone 3**: Export monthly; retain 6 years minimum in WORM-compliant storage per SEC Rule 17a-4(f).

---

## Step 8: Review Researcher Computer Use Configuration [Requires Researcher with Computer Use licensing]

**8.1** If your firm has deployed the Researcher agent with Computer Use capability:

**8.2** In the Agents submenu, select **"Researcher"** > **"Computer Use"** (visible only on tenants where the Researcher with Computer Use feature is licensed and enabled).

**8.3** Review the allowed websites list and excluded websites list. Confirm that:
- Allowed websites are limited to business-approved sources.
- The excluded websites list includes any domains prohibited by firm policy (e.g., personal social media, competitor data sources).

**8.4** Document the current allowed/excluded website configuration in the supervisory review log.

---

## Step 9: Complete the Supervisory Review Log Entry

**9.1** Ensure the supervisory review log entry for this session contains:
- Date and time of review
- Reviewer name and title
- Tenant name and environment (production/test)
- Agent Registry count (current and prior period comparison)
- Hero metric values where available (Active Users, Sessions, Exception Rate, Runtime)
- Exception rate assessment (normal/anomaly/escalated)
- Pending request count and disposition actions taken
- Ownerless agent count and remediation actions taken
- Publisher breakdown (internal vs. external partner count)
- Inventory export filename and storage location
- Any anomalies identified and follow-up actions with responsible parties and due dates

**9.2** Save and retain the supervisory review log entry as a business record. For Zone 3 firms, this log is an examination evidence artifact subject to FINRA 4511 recordkeeping requirements.

---

## Step 10: Schedule the Next Review

**10.1** Based on your Zone designation, schedule the next review:
- Zone 1: Next review date = current date + 30 days
- Zone 2: Next review date = current date + 7 days
- Zone 3: Next review date = current date + 1 business day

**10.2** Create a recurring calendar event or GRC system task for the next review. Assign a backup reviewer in case the primary reviewer is unavailable.

---

## Completion Checklist

- [ ] Successfully accessed Agent 365 Overview page
- [ ] Agent Registry count recorded
- [ ] Hero metrics reviewed and recorded (where available)
- [ ] Exception rate assessed against threshold criteria
- [ ] Pending requests reviewed and dispositioned within SLA
- [ ] Ownerless agents reviewed and ownership assignment initiated if applicable
- [ ] Publisher and platform breakdown reviewed
- [ ] Active Users trend reviewed for anomalies
- [ ] Agent inventory exported and stored with dated filename
- [ ] Supervisory review log entry completed
- [ ] Next review date scheduled

---

[Back to Control 3.13](../../../controls/pillar-3-reporting/3.13-agent-365-admin-center-analytics.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

*Updated: April 2026 | Version: v1.4.0*
