# Portal Walkthrough: Control 1.28 - Policy-Based Agent Publishing Restrictions

**Last Updated:** October 2026<br>
**Portals:** Power Platform Admin Center (PPAC), Microsoft Copilot Studio, Microsoft Purview, Power Automate<br>
**Estimated Time:** 45–60 minutes (initial setup); 10–15 minutes per environment thereafter

> **Hedging note:** This walkthrough describes how to implement publishing restrictions using the controls Microsoft currently exposes in the portal. Microsoft does **not** ship a single tenant toggle that "requires approval before publishing a Copilot Studio agent." Approval gates are implemented through Power Automate flows, Power Platform Pipelines, or documented change-control processes. The steps below reflect that reality.

---

## Prerequisites

- [ ] **Power Platform Admin** role for DLP policy and environment configuration
- [ ] **AI Administrator** role for tenant-level Copilot Studio governance settings
- [ ] **Entra Global Admin** required only for initial environment routing setup or broad Graph API consent
- [ ] Approved DLP policy design (connector classification, by zone)
- [ ] Microsoft Purview Audit (Standard or Premium) enabled in the tenant — see **Control 3.1**
- [ ] Knowledge of which environments are classified as Zone 1, Zone 2, Zone 3 — see **Control 2.2**

---

## Step 1 — Confirm DLP Enforcement Mode for Copilot Studio Agents

Microsoft Learn documents tenant-wide enforcement since early 2025 and removal of agent exemptions since **March 2025**. Policies apply to publishing and runtime; a published agent can return `DataLossPreventionViolation`, not merely fail its next update. See [Troubleshoot data policy enforcement](https://learn.microsoft.com/en-us/microsoft-copilot-studio/admin-dlp-troubleshooting).

1. Open [Power Platform Admin Center](https://admin.powerplatform.microsoft.com).
2. Confirm you can see the **Security → Data and privacy → Data policy** section (requires Power Platform Admin).
3. Document the policies assigned to the environment and any actual violations; do not look for a supported exemption/Soft-Enabled switch.

> **FSI Note:** Review existing published agents before tightening policies. Violations can block updates and disrupt running agents until the violation is resolved or the policy is amended.

---

## Step 2 — Create a Zone-Specific Data Policy

Repeat this step once per zone (Zone 1, Zone 2, Zone 3). The escalating restriction profile is described in the parent control.

1. In PPAC, go to **Security → Data and privacy → Data policy**.
2. Select **+ New policy**.
3. **Name:** Use a clear, zone-aligned name (e.g., `FSI - Zone 3 Enterprise Restricted`).
4. On the **Prebuilt connectors** tab, classify connectors into **Business**, **Non-Business**, and **Blocked** groups. Recommended starting baseline:

   | Zone | Business (allow) | Non-Business | Blocked |
   |------|------------------|--------------|---------|
   | Zone 1 | Approved data connectors and channel connectors | Approved productivity connectors; review separation from Business | Selected consumer connectors and unapproved Copilot Studio channels |
   | Zone 2 | Approved data connectors plus Microsoft Teams/Microsoft 365 channel | Minimize; unblockable connectors may remain | Facebook channel in Copilot Studio, Direct Line channels in Copilot Studio where prohibited, HTTP where not approved |
   | Zone 3 | Approved data and channel connectors only; scope access separately | Record unavoidable unblockable connectors | All unapproved **blockable** connectors; review new connectors before use |

5. For a **tenant-level** policy, on **Custom connectors**, add ordered approved host URL patterns classified Business and set the final `*` rule to **Blocked** (its initial default is Ignore). Environment-level policies classify individual custom connectors by name. See [Custom connector policies](https://learn.microsoft.com/en-us/power-platform/admin/dlp-custom-connector-parity).
6. On the **Scope** tab, choose **Add multiple environments** and select the environments classified to this zone. Avoid **Add all environments** for production-bearing zones; explicit selection is auditable.
7. Review and **Create policy**.

> **Tip:** Custom connector host patterns and the default group for new prebuilt connectors are separate settings. Non-business is not a universal deny group: it restricts mixing with Business connectors. SharePoint and other unblockable service connectors cannot be moved to Blocked. HTTP endpoint filtering is also separate from custom connector host patterns. Use [Manage data policies](https://learn.microsoft.com/en-us/power-platform/admin/prevent-data-loss) and the exact [Copilot Studio connector names](https://learn.microsoft.com/en-us/microsoft-copilot-studio/admin-data-loss-prevention); do not substitute Facebook/Telegram service connectors for channel controls.

---

## Step 3 — Verify the Pre-Publish Behavior in Copilot Studio

Copilot Studio runs a pre-publish check that surfaces DLP violations and configuration findings before the agent is published. This is the platform's primary inline enforcement signal.

1. Open [Microsoft Copilot Studio](https://copilotstudio.microsoft.com) and select an agent in a target environment.
2. Click **Publish**.
3. Review any pre-publish messages. Typical findings include:
   - DLP violation (connector used by the agent is in the **Blocked** group for this environment).
   - Channel configuration that conflicts with policy (e.g., a public channel enabled in a Zone 2/3 environment).
4. If findings appear, follow the in-product remediation links or address each finding in the agent topics, channels, or DLP policy before retrying publish.
5. On **Channels**, expand the error details and select **Download** to preserve the workbook's **DLP violations** and **Blocked channels** sheets.
6. Review the separate [automatic security scan warnings](https://learn.microsoft.com/en-us/microsoft-copilot-studio/security-scan) for No authentication, Maker-provided credentials, and sharing with everyone. These are not a DLP pass/fail panel or a zone-specific approval toggle.

> **UI variability:** The exact wording, severity icons, and finding categories shown in the Copilot Studio publish dialog change as Microsoft ships product updates. Treat the in-product messages as authoritative; this playbook describes the categories of finding rather than fixed colors or labels.

---

## Step 4 — Restrict Channels in Copilot Studio (Zone 2 and Zone 3)

For Zone 2+ agents, disable channels that are not on your approved list before publishing.

1. In Copilot Studio, open the target agent.
2. Select **Channels** on the top menu.
3. Have the admin block prohibited channel connectors in the applicable DLP policy: **Facebook channel in Copilot Studio** and **Direct Line channels in Copilot Studio** for website/Direct Line access. Block **Chat without Microsoft Entra ID authentication in Copilot Studio** if authentication is required. Telegram is reached through Azure Bot Service channels, not a standalone Copilot Studio Telegram DLP connector; review that integration's actual coverage separately.
4. For Zone 3 customer-facing agents, restrict to authenticated channels only (e.g., Microsoft Teams, authenticated web channel).
5. Confirm restricted channels are disabled/unavailable and inspect their information icons. Keep at least one permitted channel configured; if all channels are blocked, publishing is prevented.

---

## Step 5 — Implement an Approval Gate (Power Automate Approach)

The documented Copilot Studio Publish flow does not provide the PPAC approval toggles or native submission forms formerly assumed by the screenshot checklist. Use a custom intake/change-ticket process before release, or a configured pipeline gate. A Dataverse `bot` create/update trigger observes row changes, not a documented `Publish Status` event, and cannot intercept publishing.

1. Open [Power Automate](https://make.powerautomate.com).
2. Create an approval flow triggered by the organization's **explicit release request** (intake form, change ticket, or manual request).
3. Include agent ID, environment, solution version, justification, and testing evidence references in the request.
4. Validate the request and retrieve any supporting agent metadata through the configured Dataverse connection.
5. Record the request ID so the decision can be correlated to deployment.
6. Add **Start and wait for an approval** (Approval type: *Approve/Reject — First to respond*).
7. Route the approval to the designated approver group (Power Platform Admin or, for Zone 3, Power Platform Admin **and** Compliance Officer in sequential approvals).
8. On rejection, post a Teams message to the agent author and write an event to a Dataverse `Publish Approval Log` table for audit.
9. On approval, write the approval record (approver, timestamp, justification) to the same log table.

> **Important:** An intake approval does not intercept the native Publish button. Restrict production authoring/editing access with the Dataverse role design in **Control 1.1**, and test effective permissions using a non-admin author. Do not assume a separate `prvPublishBot` privilege or a row-change flow provides prevention. For a technical deployment gate, use Step 6's pipeline extension. Post-change monitoring is detective evidence only.

---

## Step 6 — Implement a Solution Promotion Pipeline (Zone 3)

For Zone 3 environments, use **Power Platform Pipelines** (or ALM Accelerator) so that Copilot Studio agents are authored in a development environment, validated in a test environment, and deployed to production via solution import — not by publishing directly into production.

1. In PPAC, go to **Deployments → New custom host** (or install Power Platform Pipelines in an existing Dataverse host environment). Target environments must be Managed Environments.
2. In Power Apps, select the host environment and open **Deployment Pipeline Configuration**. Add the development environment and Test/Production stages; set Production's **Previous Deployment Stage** to Test.
3. Enable **Pre-deployment Step Required** on the Production stage. Configure a Power Automate flow in the host using Dataverse **When an action is performed**, action **OnPreDeploymentStarted**, to obtain the required approvals and call **UpdatePreDeploymentStepStatus** with completion or rejection. The checkbox alone does not implement approval routing. Personal pipelines cannot be extended. See [Custom host setup](https://learn.microsoft.com/en-us/power-platform/alm/custom-host-pipelines) and [Extend pipelines](https://learn.microsoft.com/en-us/power-platform/alm/extend-pipelines).
4. Train Zone 3 agent authors to package the agent in a solution and submit a deployment request through the pipeline rather than clicking **Publish** in the production environment.
5. Combine with **Control 2.2** (Environment Groups and Tier Classification) to restrict who can author or publish directly in the production environment.

> **Hedging note:** Power Platform Pipelines provides solution-promotion approval gates. It does not prevent a user with sufficient privileges in the production environment from publishing an agent in place. Pair pipelines with the role restrictions in Control 1.1 to make direct production publish operationally infeasible.

---

## Step 7 — Confirm Audit Logging in Microsoft Purview

1. Open [Microsoft Purview](https://purview.microsoft.com) → **Audit**.
2. Confirm auditing is enabled (it is on by default for new tenants since 2023).
3. Filter the Activities list for **Copilot Studio** authoring events, including **BotUpdateOperation-BotPublish** and **BotCreate**. See [Audit Copilot Studio activities](https://learn.microsoft.com/en-us/microsoft-copilot-studio/admin-logging-copilot-studio).
4. Inspect actual Operation, CreationTime, user, ResultStatus, and BotId/BotSchemaName fields where present. Correlate them to the environment and test request. Preserve approval records in Power Automate/pipeline history and DLP findings in Channels workbooks; do not assume those details are present in the publishing event.
5. Validate that retention policies for audit data meet your firm's requirements (e.g., 7-year retention for FINRA 4511 / SEC 17a-4 alignment — see **Control 3.1**).

---

## Configuration by Governance Level

| Setting | Baseline (Zone 1) | Recommended (Zone 2) | Regulated (Zone 3) |
|---------|-------------------|----------------------|---------------------|
| DLP policy assignment | Light restrictions | Restrictive (no Non-Business group) | Strict allowlist only |
| Security scan warnings (process review) | Reviewed | Resolved/reviewed | Resolved/reviewed + sign-off |
| Approval gate | Optional | Power Automate flow or change ticket | Multi-stage (Power Automate or Pipelines) |
| Channel restrictions | Recommended | Public channels disabled | Authenticated channels only |
| Environment separation | Single environment OK | Dev + Prod recommended | Dev + Test + Prod with Pipelines |
| Publishing documentation | Recommended | Required (lightweight) | Required with formal sign-off |

---

## Validation

After completing these steps, confirm:

- [ ] At least one DLP policy exists per zone, with environments explicitly assigned.
- [ ] The Copilot Studio pre-publish check produces a finding when an agent uses a Blocked connector (test in a non-production environment — see the verification playbook).
- [ ] Public channels are disabled for all Zone 2+ agents.
- [ ] A Power Automate approval flow is active for Zone 2+ environments, or an equivalent process control is documented.
- [ ] Power Platform Pipelines stages exist for Zone 3 environments with pre-deployment approval configured.
- [ ] Purview captures documented Copilot Studio publish events; DLP workbooks and approval records are retained separately and correlated.

---

## Visual Reference (where to find each setting)

| Setting | Location |
|---------|----------|
| DLP data policies | PPAC → Security → Data and privacy → Data policy |
| Environment assignment to a policy | PPAC → Security → Data and privacy → Data policy → [Policy] → Scope |
| Custom connector default behavior | PPAC → Security → Data and privacy → Data policy → [Policy] → Custom connectors |
| Copilot Studio pre-publish dialog | Copilot Studio → [Agent] → Publish |
| Channel configuration | Copilot Studio → [Agent] → Channels (top menu) |
| Power Platform Pipelines | PPAC → Deployments; Power Apps → [Host] → Deployment Pipeline Configuration |
| Audit search | Microsoft Purview → Audit |

---

[Back to Control 1.28](../../../controls/pillar-1-security/1.28-policy-based-agent-publishing-restrictions.md) | [PowerShell Setup](powershell-setup.md) | [Verification & Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: October 2026 | Version: v1.6.2 | UI Verification Status: Current (Microsoft Learn review 2026-10-14; tenant UI capture pending)*
