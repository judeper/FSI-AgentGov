# Control 4.5: SharePoint Security and Compliance Monitoring - Portal Walkthrough

> This playbook provides portal configuration guidance for [Control 4.5](../../../controls/pillar-4-sharepoint/4.5-sharepoint-security-and-compliance-monitoring.md).

!!! info "Audience and scope"
    M365 administrators in US financial services organizations configuring SharePoint monitoring for AI agent activity. Portal navigation paths reflect the SharePoint Admin Center and Microsoft Purview portal as of April 2026; verify against your tenant before each change window.

---

## Prerequisites

Before starting, confirm:

| Requirement | Notes |
|---|---|
| **SharePoint Admin** role assigned to the executing administrator | Use Entra Privileged Identity Management (PIM) for just-in-time elevation in Zone 3 tenants |
| **Purview Audit Reader** role for evidence collection | Separate from SharePoint Admin to support segregation of duties (SOX 404, FINRA 3110) |
| **SharePoint Advanced Management (SAM)** entitlement | Bundled with Microsoft 365 Copilot since January 2025; standalone SAM SKU also available. Verify on the Microsoft 365 admin center "Your products" page |
| **Unified audit logging** enabled in Microsoft Purview | See Step 0 below to confirm before relying on any monitoring evidence |
| **Audit retention policy** sized to your regulatory retention period | SEC 17a-4 / FINRA 4511 typically requires 6 years; Standard audit retains 180 days and Premium audit retains 1 year by default — extend via a Purview audit retention policy |

!!! warning "Sovereign cloud tenants"
    GCC, GCC High, and DoD tenants use different admin URLs (e.g., `https://<tenant>-admin.sharepoint.us`). Substitute the correct hostname throughout. Some Advanced Management features may have a delayed rollout in sovereign clouds — verify availability via the Microsoft 365 Roadmap before assuming feature parity.

---

## Step 0: Confirm Foundational Logging is in Place

Skip this step only if audit logging is already attested for another control.

1. Navigate to [Microsoft Purview portal](https://purview.microsoft.com) > **Audit**.
2. Confirm the banner does not display "Start recording user and admin activity." If it does, click it and wait up to 60 minutes for ingestion to begin.
3. Run a sample search: **Activities** > select `FileAccessed`, set the date range to the last 24 hours, and click **Search**.
4. Capture a screenshot showing non-zero results as baseline evidence.

If the search returns zero results in a tenant with active SharePoint usage, do not proceed — investigate audit ingestion (see [troubleshooting.md](troubleshooting.md)) before relying on any downstream monitoring.

---

## Step 1: Assign Monitoring Roles

Assign roles using the principle of least privilege:

| Role | Purpose | Assignment Path |
|---|---|---|
| **SharePoint Admin** | Tenant-level SharePoint configuration | Entra admin center > Roles & admins |
| **Reports Reader** | Read-only access to SharePoint and Microsoft 365 reports | Entra admin center > Roles & admins |
| **Purview Audit Reader** | Audit log search and export | Purview portal > Roles & scopes > Permissions |

!!! tip "FSI segregation of duties"
    For FINRA-regulated firms, document the role assignments in your Written Supervisory Procedures (WSPs). Use Entra PIM to require approval and time-bound elevation for SharePoint Admin. The reviewer of monitoring evidence should not be the same individual who configures SharePoint sharing settings.

---

## Step 2: Configure Agent Insights Monitoring

Establish baseline visibility into SharePoint agent activity:

1. Navigate to [SharePoint Admin Center](https://admin.sharepoint.com) > **Reports** > **Agent insights**.
2. Under **SharePoint agents**, click **View reports**.
   - Review the count of agents per site and the agents-actively-used metric.
   - Identify sites hosting more agents than expected by your governance baseline.
3. Under **Agent access**, click **View reports**.
   - Review which sites are being read by agents and how often.
   - Cross-reference high-traffic sites against your approved-knowledge-source register.
4. Export both reports to CSV and store the export in your evidence repository (see Step 6).
5. For any site showing agent activity outside the approved register, file a remediation ticket and consider applying Restricted Content Discovery (RCD) — see [Control 4.1](../../../controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md).

!!! note "Initial population delay"
    Agent insights typically requires 24–48 hours to populate after SAM activation. If the page is empty in a freshly licensed tenant, wait one to two business days before troubleshooting.

---

## Step 3: Establish a Data Access Governance (DAG) Baseline

DAG reports surface oversharing risks that AI agents would otherwise inherit through user permissions.

1. Navigate to **Reports** > **Data access governance**.
2. If reports show "Not started," click **Get started** to initialize the snapshot. Generation can take several hours for tenants with more than 10,000 sites.
3. Generate and export the following reports:
   - **Sharing links** (Anyone, People in your organization, Specific people, Existing access)
   - **Sensitivity labels applied to files**
   - **Sharing policies changed**
   - **Site permissions across your organization**
   - **Site permissions for users** (December 2025 GA — pre-Copilot deployment audits)
4. Record the date/time of the baseline snapshot in your evidence log.
5. Identify the top 10 sites with the highest oversharing risk and route them to the AI Governance Lead for action under [Control 4.1](../../../controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md) and [Control 4.8](../../../controls/pillar-4-sharepoint/4.8-item-level-permission-scanning-agent-knowledge-sources.md).

---

## Step 4: Run Advanced Management Assessments

1. Navigate to **Advanced management** > **Overview**.
2. Click **Start assessment** under **Microsoft 365 Copilot readiness**.
3. Review the **Site lifecycle** results (inactivity, missing ownership) and the **Oversharing** results (broken inheritance, org-wide permissions, Anyone links).
4. For each finding, click **View recommendations** and assign an owner. Do not auto-apply remediation in regulated tenants without change control.
5. Schedule the assessment to run quarterly for Zone 2 sites and monthly for Zone 3 sites; record the schedule in the SharePoint governance plan.

---

## Step 5: Configure Alert Policies for SharePoint and Agent Events

Microsoft published service targets for alert generation are typically minutes to a few hours, but latency is not contractually guaranteed. Configure alerts and document the *expected* response window rather than asserting a fixed SLA.

1. Navigate to [Microsoft Purview portal](https://purview.microsoft.com) > **Audit** > **Alert policies**.
2. Create or confirm alert policies for, at minimum:
   - **Sharing link created with "Anyone" scope** on a labeled or restricted site
   - **Anonymous link accessed**
   - **Permission inheritance broken** on a sensitive site
   - **Agent created using a restricted site as a knowledge source** (filter by site URL when available)
   - **External user added to a confidential site**
3. Set severity to **High** for agent-related and sharing-link policies.
4. Route alert recipients to a monitored shared mailbox or distribution group (not an individual administrator) so coverage survives staff changes.
5. For Zone 3, forward alerts to Microsoft Sentinel via the Office 365 connector — see [Control 3.9](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md).

---

## Step 6: Establish Monitoring Cadence and Evidence Storage

Document a single, consistent monitoring cadence that aligns with the control doc and your zone classification:

| Activity | Zone 1 (Personal) | Zone 2 (Team) | Zone 3 (Enterprise) | Responsible Role |
|---|---|---|---|---|
| Home dashboard review | Weekly | Weekly | Daily | SharePoint Admin |
| Agent insights review | Monthly | Weekly | Daily | AI Governance Lead |
| DAG report run + export | Quarterly | Monthly | Weekly | Compliance Officer |
| Advanced Management assessment | Annually | Quarterly | Monthly | Governance Committee |
| Alert review | Weekly | Daily | Continuous (SOC) | Entra Security Admin / SOC Analyst |
| Comprehensive audit | Annually | Annually | Annually | Internal Audit |

**Evidence storage requirements:**

- Store CSV/JSON exports in a controlled SharePoint site or Azure Storage container with retention configured to match your regulatory window (typically 6 years for SEC 17a-4).
- Compute and record a SHA-256 hash of every export at the time of capture (see [PowerShell Setup](powershell-setup.md), Step 7).
- Lock the storage location with sensitivity labeling and Conditional Access; do not allow editing of evidence files after capture.

---

## Validation

After completing the configuration, verify:

1. [ ] SharePoint Admin, Reports Reader, and Purview Audit Reader roles assigned to monitoring personnel and documented in the WSPs (FINRA-regulated firms).
2. [ ] Agent insights reports return non-empty data and have been exported.
3. [ ] Data Access Governance baseline snapshot generated, exported, and hashed.
4. [ ] Advanced Management Copilot readiness assessment completed and findings assigned.
5. [ ] At least five alert policies configured for SharePoint sharing and agent events; recipients route to a monitored mailbox.
6. [ ] Monitoring cadence table populated with names (not just roles) for each activity in your tenant's run book.
7. [ ] Evidence storage location configured with retention matching your regulatory window and SHA-256 hashing in place.

**Expected Result:** SharePoint monitoring portals provide tenant-wide visibility into agent access patterns, oversharing risks, and security posture, with evidence captured in a controlled, retention-aligned repository.

---

[Back to Control 4.5](../../../controls/pillar-4-sharepoint/4.5-sharepoint-security-and-compliance-monitoring.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: April 2026 | Version: v1.4.0*
