# Control 4.2: Site Access Reviews and Certification — Portal Walkthrough

> Step-by-step portal configuration for [Control 4.2 — Site Access Reviews and Certification](../../../controls/pillar-4-sharepoint/4.2-site-access-reviews-and-certification.md).

This playbook stands up the SharePoint Advanced Management (SAM) Data Access Governance (DAG) baseline, configures Site Attestation Policies, initiates Site Access Reviews on high-risk sites, and pairs them with Microsoft Entra Access Reviews on the underlying Microsoft 365 Groups and Sites.Selected service principals.

---

## Prerequisites

- [ ] **SharePoint Admin** role assigned (canonical role per `docs/reference/role-catalog.md`)
- [ ] **Entra Identity Governance Admin** role assigned (separate operator recommended for separation of duties)
- [ ] **SharePoint Advanced Management** add-on or Microsoft 365 E5 license enabled at the tenant level — required for DAG reports, Site Access Reviews, Site Attestation Policies, and the Oversharing baseline report
- [ ] **Microsoft Entra ID Governance (P2)** licensing for users assigned as reviewers in Entra Access Reviews
- [ ] Access to:
  - [SharePoint Admin Center](https://admin.sharepoint.com)
  - [Microsoft Entra Admin Center](https://entra.microsoft.com)
  - [Microsoft Purview portal](https://purview.microsoft.com) (for retention label assignment to attestation evidence)
- [ ] An owner email address recorded on every site in scope (DAG report or `Get-SPOSite` output should show no orphaned sites)
- [ ] Sensitivity labels published and applied to in-scope sites (dependency on [Control 1.5](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md)) so that attestation policy scoping can target labels rather than URL patterns

!!! note "Site Access Review tenant limit"
    SAM supports up to **1,000 Site Access Reviews per month per tenant**. Plan a triage cadence
    that prioritizes EEEU-shared sites, sites in the Oversharing baseline report, and sites with
    the highest agent activity from Agent Insights. See the limit guidance under
    [Data access governance reports](https://learn.microsoft.com/en-us/sharepoint/data-access-governance-reports).

---

## Step 1 — Baseline current sharing posture with DAG reports

**Portal path:** SharePoint Admin Center → **Reports** → **Data access governance**

1. Open [SharePoint Admin Center](https://admin.sharepoint.com) and select **Reports** → **Data access governance**.
2. If this is the first run, click **Get started** to provision the report pipeline (initial generation can take up to 24 hours on large tenants).
3. Generate and export each of the following reports — they are the primary input to Step 3:
   - **Content shared with Everyone Except External Users (EEEU)** — highest-priority oversharing surface for Microsoft 365 Copilot grounding
   - **Sharing links** — surfaces "Anyone with the link" and high-fan-out internal share links
   - **Site permissions** — sites with large numbers of unique users or unusual permission level distributions
   - **Oversharing baseline using permissions** (GA) — sites whose actual sharing exceeds the baseline expected for their sensitivity label
   - **Agent Insights** and **Agent Access Insights** — sites where Microsoft 365 Copilot agents and Copilot Studio agents are most active
   - **Content Management Assessment** — Copilot readiness scoring per site
4. Export each report (CSV) and stage to your evidence repository.

!!! warning "EEEU is the leading Copilot grounding risk"
    "Everyone Except External Users" grants access to every internal user — and therefore to
    Copilot acting on behalf of every internal user. Treat any EEEU-shared site as in-scope
    for an immediate Site Access Review unless the content is explicitly intended for the
    full workforce. Cross-reference findings with
    [Control 4.7 — Microsoft 365 Copilot Data Governance](../../../controls/pillar-4-sharepoint/4.7-microsoft-365-copilot-data-governance.md).

---

## Step 2 — Configure Site Attestation Policies

**Portal path:** SharePoint Admin Center → **Policies** → **Site lifecycle management** → **Site attestation policies**

1. Click **Open** under **Site attestation policies**, then **Create policy**.
2. **Name and scope:**
   - Name: `FSI Quarterly Attestation — Confidential and above`
   - Scope by **Sensitivity label**: select `Confidential` and `Highly Confidential` (or your equivalent labels)
   - Optionally narrow further by site template or URL prefix for regulated business unit sites
3. **Cadence:**
   - Zone 3 / regulated sites: **Every 3 months (Quarterly)**
   - Zone 2 / team sites: **Every 6 months (Semi-annual)**
4. **Notifications:**
   - Reminder days before due: **30, 14, 7, 1**
   - Escalation: enable **Escalate to admin if overdue**
5. **Custom email template (GA December 2025):**
   - Click **Customize email template**
   - Insert your organization's compliance footer, the WSP reference, and an escalation contact
   - Use the supported placeholders for site URL, owner name, and due date
6. **Non-compliance action:**
   - Zone 3: **Make site read-only** (recommended) — preserves records for audit while preventing further sharing
   - Zone 2: **Archive site** after extended non-response
7. Click **Save** and toggle the policy to **Active**.

Repeat with a separate policy targeting `General` / unlabeled team sites at a longer cadence if Zone 2 coverage is required.

---

## Step 3 — Initiate Site Access Reviews from DAG report rows

**Portal path:** SharePoint Admin Center → **Reports** → **Data access governance** → *(open a report)*

1. Open the **Content shared with EEEU** report.
2. Sort by site sensitivity label, then by activity. For each high-risk row, select the site and click **Create site access review**.
3. Configure the review:
   - **Reviewer:** site owner (the only configurable reviewer for SharePoint Site Access Reviews)
   - **Justification required:** Yes
   - **Decision actions:** allow the reviewer to *Keep access*, *Remove user/group*, or *Stop sharing with EEEU*
   - **Auto-remediation on no response:** apply policy default (read-only)
4. Repeat for sites surfaced by the **Oversharing baseline** report and any high-traffic site from **Agent Access Insights**.
5. Track total reviews initiated this month against the **1,000-per-tenant** SAM limit.

!!! tip "Sequence with Restricted Content Discovery (RCD)"
    For sites that cannot be remediated immediately, apply Restricted Content Discovery via
    [Control 4.1](../../../controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md)
    to remove the site from Microsoft 365 Copilot grounding while the access review runs.

---

## Step 4 — Pair with Entra Access Reviews on underlying groups

**Portal path:** Microsoft Entra Admin Center → **Identity governance** → **Access reviews**

1. In [Microsoft Entra Admin Center](https://entra.microsoft.com), open **Identity governance** → **Access reviews** → **+ New access review**.
2. **Select what to review:**
   - **Teams + Groups** → **Select Teams + groups**
   - Choose the Microsoft 365 Groups that back the in-scope SharePoint sites (one access review can target multiple groups)
3. **Scope:** *All users* (review every member; required for FSI books-and-records sites)
4. **Reviewers:**
   - Primary: **Group owner(s)**
   - Fallback: a named compliance reviewer or distribution list
5. **Settings:**
   - Duration: **14 days**
   - Recurrence: **Quarterly** (Zone 3) or **Semi-annual** (Zone 2)
   - **Auto-apply results to resource:** On
   - **If reviewers don't respond:** **Remove access**
   - **Justification required:** On
   - **Mail notifications:** On
   - **Reminders:** On
6. Click **Create**.

---

## Step 5 — Review AI agent service principals (Sites.Selected)

**Portal path:** Microsoft Entra Admin Center → **Identity governance** → **Access reviews** → **+ New access review**

1. Create a separate access review scoped to **Service principals assigned to applications** for any AI agent app registration that holds **Sites.Selected** Graph permission.
2. Reviewers: the **AI Governance Lead** plus the registered application owner.
3. Cadence: **Quarterly** for any production agent.
4. Justification required: On — the reviewer should restate the business case for each granted site.
5. Cross-reference the result back into [Control 3.1 — Agent Inventory](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md).

---

## Step 6 — Capture evidence under retention

**Portal path:** Microsoft Purview portal → **Solutions** → **Data lifecycle management** → **Retention policies**

1. In Microsoft Purview, ensure a retention policy or label exists that covers the Teams channel, SharePoint library, or mailbox where you stage:
   - Site Access Review decision exports
   - Entra Access Review decision exports
   - Attestation completion reports
   - Custom email templates and escalation records
2. Set the retention period to the longer of: your firm's records retention schedule for access governance evidence, or **6 years** (typical SEC 17a-4 / FINRA 4511 floor).
3. Where required, enable **Preservation Lock** on the retention policy so the schedule cannot be shortened or deleted.

---

## Configuration by Governance Level

| Setting | Baseline (Zone 1) | Recommended (Zone 2) | Regulated (Zone 3) |
|---|---|---|---|
| DAG report cadence | Quarterly review of EEEU rows | Monthly review of EEEU + Oversharing baseline | Weekly review of EEEU, Oversharing baseline, Agent Access Insights |
| Site Attestation Policy | Optional | Semi-annual, owner only | Quarterly, owner + manager + compliance sign-off |
| Site Access Review trigger | Owner-initiated | Initiated from EEEU + Oversharing rows | Initiated from EEEU + Oversharing + Agent Access Insights rows |
| Entra Access Review of underlying groups | Annual | Semi-annual | Quarterly with auto-apply + deny on no response |
| Sites.Selected service principal review | Not required | Annual | Quarterly with named reviewer |
| Non-compliance action | Notify | Archive | Read-only + escalation |
| Evidence retention | 1 year | 3 years | 6 years (SEC 17a-4 / FINRA 4511 aligned), Preservation Lock recommended |

---

## Validation

After completing the steps above, verify:

- [ ] All six DAG report types listed in Step 1 are accessible and refreshed within the last 30 days
- [ ] At least one active Site Attestation Policy exists for the Confidential / Highly Confidential label set
- [ ] Custom attestation email template renders correctly in a test notification
- [ ] At least one Site Access Review has been initiated from the EEEU report and reached the reviewer
- [ ] An Entra Access Review is scheduled for the M365 Groups behind in-scope sites with **Auto-apply** and **Remove access on no response** enabled
- [ ] A separate Entra Access Review covers Sites.Selected service principals for production AI agents
- [ ] A Purview retention policy or label covers the evidence repository with the appropriate (typically 6-year) retention window

---

[Back to Control 4.2](../../../controls/pillar-4-sharepoint/4.2-site-access-reviews-and-certification.md) | [PowerShell Setup](powershell-setup.md) | [Verification & Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
