# Portal Walkthrough: Control 1.28 - Policy-Based Agent Publishing Restrictions

**Last Updated:** April 2026<br>
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

Effective February 2025, Microsoft removed the "Soft-Enabled" DLP exemption for published Copilot Studio agents. All published agents are now evaluated against tenant DLP policy at runtime and at publish/update time. There is no portal toggle to revert this — it is the platform default.

1. Open [Power Platform Admin Center](https://admin.powerplatform.microsoft.com).
2. Confirm you can see the **Policies → Data policies** node (requires Power Platform Admin).
3. Document in your change record that DLP enforcement mode is **Enabled** (the only supported mode as of February 2025).

> **FSI Note:** For organizations with existing published agents created before February 2025, conduct a DLP compliance review immediately. Agents whose connector usage no longer aligns with the current DLP policy are blocked from update operations until the violation is resolved or the policy is amended.

---

## Step 2 — Create a Zone-Specific Data Policy

Repeat this step once per zone (Zone 1, Zone 2, Zone 3). The escalating restriction profile is described in the parent control.

1. In PPAC, go to **Policies → Data policies**.
2. Select **+ New policy**.
3. **Name:** Use a clear, zone-aligned name (e.g., `FSI - Zone 3 Enterprise Restricted`).
4. On the **Prebuilt connectors** tab, classify connectors into **Business**, **Non-Business**, and **Blocked** groups. Recommended starting baseline:

   | Zone | Business (allow) | Non-Business | Blocked |
   |------|------------------|--------------|---------|
   | Zone 1 | SharePoint, OneDrive, Office 365 Outlook, Teams, Dataverse | Approved productivity connectors | Public-channel and consumer connectors (Telegram, Facebook Messenger, public-website connector) |
   | Zone 2 | Same as Zone 1 plus business systems (e.g., SQL Server, Salesforce per risk review) | (intentionally empty) | All Zone 1 blocked + Twitter/X, RSS, generic HTTP unless allowlisted via custom connector |
   | Zone 3 | Read-only or scoped variants of Zone 2 business systems only, gated by data risk review | (intentionally empty) | Everything else, including premium connectors not on the approved list |

5. On the **Custom connectors** tab, set the default action (typically **Block**) and add explicit URL patterns for any allowlisted custom connectors (e.g., `https://api.contoso.com/*`).
6. On the **Scope** tab, choose **Add multiple environments** and select the environments classified to this zone. Avoid **Add all environments** for production-bearing zones; explicit selection is auditable.
7. Review and **Create policy**.

> **Tip:** Because there is no native concept of a "wildcard" connector identifier in DLP policies, do not attempt to block "all unknown connectors" via wildcard. Use the **Custom connectors → Default behavior = Block** setting plus the **Non-Business** group as your allowlist boundary.

---

## Step 3 — Verify the Pre-Publish Behavior in Copilot Studio

Copilot Studio runs a pre-publish check that surfaces DLP violations and configuration findings before the agent is published. This is the platform's primary inline enforcement signal.

1. Open [Microsoft Copilot Studio](https://copilotstudio.microsoft.com) and select an agent in a target environment.
2. Click **Publish**.
3. Review any pre-publish messages. Typical findings include:
   - DLP violation (connector used by the agent is in the **Blocked** group for this environment).
   - Channel configuration that conflicts with policy (e.g., a public channel enabled in a Zone 2/3 environment).
4. If findings appear, follow the in-product remediation links or address each finding in the agent topics, channels, or DLP policy before retrying publish.

> **UI variability:** The exact wording, severity icons, and finding categories shown in the Copilot Studio publish dialog change as Microsoft ships product updates. Treat the in-product messages as authoritative; this playbook describes the categories of finding rather than fixed colors or labels.

---

## Step 4 — Restrict Channels in Copilot Studio (Zone 2 and Zone 3)

For Zone 2+ agents, disable channels that are not on your approved list before publishing.

1. In Copilot Studio, open the target agent.
2. Go to **Settings → Channels** (or **Channels** in the left rail, depending on the current build).
3. Disable any channel not on your approved list — at minimum, disable **Facebook**, **Telegram**, and the public **Website (anonymous)** channel for Zone 2+.
4. For Zone 3 customer-facing agents, restrict to authenticated channels only (e.g., Microsoft Teams, authenticated web channel).
5. Save channel settings.

---

## Step 5 — Implement an Approval Gate (Power Automate Approach)

Because Copilot Studio does not surface a built-in "require approval" toggle, model the approval gate using a Power Automate flow that watches for changes to the Dataverse `bot` table (Copilot Studio agents are stored as `bot` rows) or that is triggered from a custom intake form.

1. Open [Power Automate](https://make.powerautomate.com).
2. Create a new **automated cloud flow**.
3. Trigger: **Dataverse — When a row is added, modified, or deleted** on the **Bots** table; scope to the target environment(s).
4. Add a **Get a row by ID** action to retrieve the bot record.
5. Add a **Condition** to check whether `Publish Status` indicates a publish or republish event.
6. Add **Start and wait for an approval** (Approval type: *Approve/Reject — First to respond*).
7. Route the approval to the designated approver group (Power Platform Admin or, for Zone 3, Power Platform Admin **and** Compliance Officer in sequential approvals).
8. On rejection, post a Teams message to the agent author and write an event to a Dataverse `Publish Approval Log` table for audit.
9. On approval, write the approval record (approver, timestamp, justification) to the same log table.

> **Important:** A Power Automate approval flow does **not** technically prevent the publish action itself — it provides documented review and an audit trail. To prevent unauthorized publishes outright, combine the flow with one of: (a) restricting `prvPublishBot` privileges via Dataverse security roles (see **Control 1.1**), (b) using Power Platform Pipelines so authoring happens in a non-production environment, or (c) Conditional Access policies that block the Copilot Studio app for non-approver personas.

---

## Step 6 — Implement a Solution Promotion Pipeline (Zone 3)

For Zone 3 environments, use **Power Platform Pipelines** (or ALM Accelerator) so that Copilot Studio agents are authored in a development environment, validated in a test environment, and deployed to production via solution import — not by publishing directly into production.

1. In PPAC, go to **Resources → Pipelines** and create a host environment if you do not yet have one.
2. Create a pipeline with **Development → Test → Production** stages mapped to your Zone 3 environments.
3. On the **Test → Production** stage, configure **pre-deployment approvals** (this is a built-in Pipelines feature) and route to the Compliance Officer.
4. Train Zone 3 agent authors to package the agent in a solution and submit a deployment request through the pipeline rather than clicking **Publish** in the production environment.
5. Combine with **Control 2.2** (Environment Groups and Tier Classification) to restrict who can author or publish directly in the production environment.

> **Hedging note:** Power Platform Pipelines provides solution-promotion approval gates. It does not prevent a user with sufficient privileges in the production environment from publishing an agent in place. Pair pipelines with the role restrictions in Control 1.1 to make direct production publish operationally infeasible.

---

## Step 7 — Confirm Audit Logging in Microsoft Purview

1. Open [Microsoft Purview](https://compliance.microsoft.com) → **Audit**.
2. Confirm auditing is enabled (it is on by default for new tenants since 2023).
3. Run a search for activities related to Copilot Studio publishing. Useful filters:
   - Workload: **PowerPlatformAdmin** and **Dataverse**.
   - Activities: bot create/update events, DLP policy change events, Power Automate approval events.
4. Confirm that the events captured include the actor UPN, environment, timestamp, and the bot identifier.
5. Validate that retention policies for audit data meet your firm's requirements (e.g., 7-year retention for FINRA 4511 / SEC 17a-4 alignment — see **Control 3.1**).

---

## Configuration by Governance Level

| Setting | Baseline (Zone 1) | Recommended (Zone 2) | Regulated (Zone 3) |
|---------|-------------------|----------------------|---------------------|
| DLP policy assignment | Light restrictions | Restrictive (no Non-Business group) | Strict allowlist only |
| Pre-publish findings | Acknowledged | Must be cleared | Must be cleared + reviewer sign-off |
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
- [ ] Purview audit captures bot create/update events and DLP policy changes for the relevant environments.

---

## Visual Reference (where to find each setting)

| Setting | Location |
|---------|----------|
| DLP data policies | PPAC → Policies → Data policies |
| Environment assignment to a policy | PPAC → Policies → Data policies → [Policy] → Scope |
| Custom connector default behavior | PPAC → Policies → Data policies → [Policy] → Custom connectors |
| Copilot Studio pre-publish dialog | Copilot Studio → [Agent] → Publish |
| Channel configuration | Copilot Studio → [Agent] → Settings → Channels |
| Power Platform Pipelines | PPAC → Resources → Pipelines |
| Audit search | Microsoft Purview → Audit |

---

[Back to Control 1.28](../../../controls/pillar-1-security/1.28-policy-based-agent-publishing-restrictions.md) | [PowerShell Setup](powershell-setup.md) | [Verification & Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: April 2026 | Version: v1.3.3 | UI Verification Status: Current*
