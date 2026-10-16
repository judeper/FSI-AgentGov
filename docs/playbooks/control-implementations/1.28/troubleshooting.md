# Troubleshooting: Control 1.28 - Policy-Based Agent Publishing Restrictions

**Last Updated:** October 2026<br>
**Support Level:** L2 / L3 (Power Platform and Microsoft Copilot Studio admins)

## Overview

This playbook addresses the issues most often encountered when implementing or operating policy-based agent publishing restrictions. Each entry follows a consistent shape: symptoms, likely root causes, diagnostics, resolution options, and prevention.

> **Hedged outcome language:** The Copilot Studio publish dialog and pre-publish messaging evolve as Microsoft ships product updates. If the wording you see differs from the wording quoted here, treat the in-product message as authoritative and use the diagnostics below to narrow the cause.

---

## Issue 1 — Publish Blocked: "DLP violation" Finding

### Symptoms

- Author clicks **Publish** in Copilot Studio and the pre-publish dialog surfaces a DLP-related finding identifying one or more connectors.
- The agent remains in its prior state.

### Likely Causes

- The agent uses a connector that is in the **Blocked** group of the DLP policy assigned to the environment.
- A DLP policy was recently tightened and the agent's connector usage no longer aligns.
- The environment was recently moved into the scope of a stricter zone DLP policy.

### Diagnostics

```powershell
# Identify which DLP policies cover the target environment.
$envId = '<environment-id>'
Get-DlpPolicy -ErrorAction Stop | ConvertTo-Json -Depth 100
# Inspect actual scope/environment IDs in the response and reconcile in PPAC.
# Do not assume Environments is a flat list or ignore all-environment/exclusion scopes.
```

In the portal:

1. Power Platform Admin Center → Security → Data and privacy → Data policy → open the policy → review **Prebuilt connectors** classification.
2. In Copilot Studio, review **Topics** and **Channels** (top menu). Download the Channels error workbook; identify the exact policy/connector from its DLP violations and Blocked channels sheets.

### Resolution Options

- **Option A — Adjust the agent.** Replace the blocked connector with an approved one, or remove the topic that uses it.
- **Option B — Reclassify the connector.** If the connector should be allowed, the Power Platform Admin moves it from Blocked to Business in the DLP policy. Document the rationale and route through change control before doing so in Zone 2+.
- **Option C — Move the environment.** If the agent legitimately belongs in a different zone, reassign the environment to a more permissive zone DLP policy. This is an exceptional step in regulated environments and requires zone reclassification per **Control 2.2**.

### Prevention

- Publish the zone-by-zone connector allowlist to agent authors.
- Add a pre-build checklist requiring authors to confirm connector choices against the allowlist for the target environment's zone.

---

## Issue 2 — Published Agent Update or Runtime Is Blocked

### Symptoms

- A previously published agent cannot be updated; the publish action surfaces a DLP finding.
- The published agent can also fail for end users with `DataLossPreventionViolation`; continued runtime availability is not assured.

### Likely Causes

- DLP policy tightening after publish (for example, a connector moved from Business to Blocked).
- [Microsoft documents](https://learn.microsoft.com/en-us/microsoft-copilot-studio/admin-dlp-troubleshooting) removal of agent exemptions since March 2025 and enforcement for published agents at runtime as well as publication.

### Diagnostics

- Compare the saved policy's modification information in PPAC with the actual agent publish history.
- Download the Channels violation workbook and correlate policy ID, connector, environment, and timestamps. Review policy-change audit evidence where available, separately from the publish event.

### Resolution Options

- Adjust the agent to remove the now-blocked connector dependency, then republish.
- If the policy change was unintentional, revert the connector classification with documented change-control approval.
- For a temporary exception, document the business impact, route through Compliance review, and reclassify the connector with a defined revert date.

### Prevention

- Run the inventory script (PowerShell Setup, Script 4) before any DLP policy tightening to identify agents that will be affected.
- Notify agent owners in advance of DLP policy changes and provide a remediation window.

---

## Issue 3 — Pre-Publish Dialog Shows No Findings, but Agent Should Be Blocked

### Symptoms

- An author publishes an agent that you expect to be blocked (e.g., uses Facebook channel in a Zone 2 environment), and the publish completes.

### Likely Causes

- The DLP policy is not actually assigned to the environment (assignment was scoped incorrectly).
- The connector or channel is in **Non-Business** rather than **Blocked**.
- The policy change has not yet taken effect; confirm the saved scope and actual behavior rather than assuming a fixed propagation delay.
- The tenant policy's final custom connector `*` rule is still Ignore instead of Blocked, or another ordered rule classifies the host differently.

### Diagnostics

```powershell
# Confirm policy → environment binding.
Get-DlpPolicy -ErrorAction Stop | ConvertTo-Json -Depth 100
```

In the portal, confirm the saved **Scope / Applied to** includes the target environment. Tenant-wide and exclusion scopes must be evaluated too; filtering only a flat Environments list misses those policies.

### Resolution Options

- Add the environment to the correct zone DLP policy.
- Move the offending connector from Non-Business to Blocked.
- In a tenant policy's Custom connectors rules, classify approved host patterns and set the final `*` rule to **Blocked**. Environment policies classify custom connectors individually.
- Block the exact Copilot Studio channel connector in DLP and verify **Channels** displays the restriction. Facebook service connectors are not the Facebook channel policy surface; website access uses **Direct Line channels in Copilot Studio**.

### Prevention

- Use explicit environment selection (not "Add all environments") and review scope monthly.
- Minimize Non-business where appropriate, but record unblockable connectors. Non-business is not a universal deny group, and SharePoint cannot be moved to Blocked.

---

## Issue 4 — Approval Workflow Did Not Trigger

### Symptoms

- A configured release request produces no approval, or an author publishes directly without using the intake/pipeline process.

### Likely Causes

- The explicit intake or pipeline-extension flow is disabled or configured for the wrong trigger/stage. A `bot` row-change flow does not intercept native Publish.
- The author has the Power Platform Admin role and is exempted from the surrounding approval flow by design.
- The flow's connection reference uses an account that no longer has access to the Dataverse environment.

### Diagnostics

- Open Power Automate → My flows; confirm the approval flow status is **On**.
- Open the flow's run history and confirm runs for the actual release requests. For pipeline gates, check the configured extension and `OnPreDeploymentStarted` / `OnApprovalStarted` action.
- Confirm the trigger's environment scope matches the environment where the publish happened.
- Confirm the connection references are healthy (no broken connections).

### Resolution Options

- Re-enable or repair the flow.
- If the trigger filter excludes admin accounts deliberately, document this in the control evidence; otherwise, broaden the filter.
- Repair connection references and re-test.
- For bypassed intake, restrict direct production editing and test with a non-admin author; for pipelines, confirm the flow completes/rejects the pending stage through the documented status action.

### Prevention

- Add a daily flow-health check (a simple scheduled flow that pings the approval flow's run history and alerts if no runs in N days).
- Treat the approval flow as production code: source control, CAB-approved changes, and ownership documented.

---

## Issue 5 — Approver Did Not Receive the Approval Request

### Symptoms

- The Power Automate flow ran successfully, but the designated approver reports they never received the request.

### Likely Causes

- The approval was routed to a group whose membership has changed.
- The approver's Microsoft Teams Approvals app or Outlook email is filtering the message.
- The flow uses **First to respond** with multiple approvers and a different approver acted before the expected one.

### Diagnostics

- Open the flow run; inspect the **Start and wait for an approval** action's outputs to confirm the assigned approver and the response.
- Check the approver's Teams Approvals app and email Junk / Quarantine folders.

### Resolution Options

- Update the approver group or named approver list in the flow.
- Whitelist Power Automate notification senders in the firm's mail filtering rules.
- For Zone 3, switch to **Everyone must approve** rather than First to respond to enforce multi-party review.

### Prevention

- Quarterly access review of the approver group to confirm current membership.
- Send a monthly synthetic approval to confirm end-to-end delivery.

---

## Issue 6 — Power Platform Pipelines Did Not Stop a Direct Production Publish

### Symptoms

- A Zone 3 agent was published directly in the production environment, bypassing the Dev → Test → Prod pipeline.

### Likely Causes

- The actor had `prvCreateBot` / `prvWriteBot` privileges in the production environment via a Dataverse security role.
- The actor used the Copilot Studio app directly in the production environment instead of submitting a deployment from a lower environment.

### Diagnostics

- Review the Dataverse security role assignments in the production environment for the actor and any group memberships.
- Pull the Purview audit event for the publish and confirm the actor and the environment.

### Resolution Options

- Tighten Dataverse role assignments per **Control 1.1** so that only the pipeline service principal has bot create/update privileges in production.
- For human admins who must retain access for break-glass scenarios, gate the role assignment behind Entra Privileged Identity Management (PIM) just-in-time elevation.

### Prevention

- Treat Power Platform Pipelines as the supported deployment path and remove direct authoring permissions in Zone 3 production environments.
- Review Dataverse role assignments quarterly.

---

## Issue 7 — PowerShell Returns Empty Results, No Errors

### Symptoms

- `Get-DlpPolicy` or `Get-AdminPowerAppEnvironment` returns no rows in a tenant where you can see policies or environments in the portal.

### Likely Causes

- The session is running in PowerShell 7 (Core) instead of Windows PowerShell 5.1; `Microsoft.PowerApps.Administration.PowerShell` requires Desktop edition and silently returns empty results otherwise.
- The signed-in account does not have Power Platform Admin (read access only via the portal does not grant cmdlet access to all properties).

### Diagnostics

```powershell
$PSVersionTable.PSEdition       # Should be 'Desktop' for these cmdlets
$PSVersionTable.PSVersion       # Should be 5.1.x

# Confirm the endpoint the session is bound to:
(Get-PowerAppsAccount).Endpoint
```

### Resolution Options

- Switch to a Windows PowerShell 5.1 session.
- Confirm the signed-in account holds the Power Platform Admin role (or use a service principal that does).

### Prevention

- Add the PowerShell guard from the [PowerShell Setup](powershell-setup.md) playbook to every script. It throws when running under a non-Desktop edition rather than producing false-clean evidence.
- Document authentication details in your runbooks.

---

## Issue 8 — DLP Policy Cmdlet or Parameter Does Not Resolve

### Symptoms

- A DLP command is unavailable, or `Set-DlpPolicy -ConnectorGroups` fails parameter binding.

### Likely Causes

- The `Microsoft.PowerApps.Administration.PowerShell` module is not installed or not imported in the current session.
- The example assumes an undocumented command, alias, or parameter. Current Learn documents `Set-DlpPolicy -PolicyName -UpdatedPolicy`, not `-ConnectorGroups`; reviewed sources do not establish `Add-PowerAppEnvironmentToPolicy` or `Get-AdminPowerAppChatbot`.

### Diagnostics

```powershell
Get-Module -Name Microsoft.PowerApps.Administration.PowerShell -ListAvailable
Get-Command -Module Microsoft.PowerApps.Administration.PowerShell -Name *Dlp*
```

### Resolution Options

- Install or import the module per the [PowerShell Setup](powershell-setup.md) playbook.
- Check `Get-Help New-DlpPolicy -Full` and `Get-Help Set-DlpPolicy -Full`; use a complete approved definition per the updated PowerShell playbook. Do not assume older commands are aliases.
- Use the documented Dataverse Bots inventory approach rather than substituting an unverified chatbot cmdlet. Stop on collection failures; an empty result is not evidence of compliance.

### Prevention

- Pin a single module version per CAB-approved baseline and avoid mixing cmdlet name conventions in the same automation.

---

## Issue 9 — Audit Events Missing in Purview

### Symptoms

- Bot publish events do not appear in Purview audit search even though the publish clearly happened.

### Likely Causes

- Events have not yet been ingested; record the activity time and allow for ingestion latency.
- The audit search filter is too narrow (wrong workload or date range).
- Auditing was disabled in the tenant or for the relevant workload.

### Diagnostics

- Re-search after allowing for ingestion latency; do not treat a fixed 60-minute window as a delivery guarantee.
- Broaden the search to `All workloads` to confirm ingestion is happening for other activity.
- Confirm Purview Audit (Standard) is enabled for the tenant.

### Resolution Options

- Re-enable auditing if disabled.
- Filter the Activities list for Copilot Studio's documented **BotUpdateOperation-BotPublish** event. See [Audit Copilot Studio activities](https://learn.microsoft.com/en-us/microsoft-copilot-studio/admin-logging-copilot-studio).
- Do not search for invented native DLP-violation/approval event names. Use Channels workbooks for DLP and configured Power Automate/pipeline records for approvals; preserve and correlate them separately.
- For Zone 3 evidence, use Audit (Premium) where available to extend retention beyond the default 180 days.

### Prevention

- Validate audit capture as part of the test pass (Verification & Testing, Test Case 8) and on a quarterly basis thereafter.

---

## Escalation Path

If an issue is not resolved by the steps above:

1. Capture the in-product wording of the finding, the exact agent and environment IDs, the relevant DLP policy ID, and the timestamp.
2. Open a Microsoft support case under the Power Platform / Copilot Studio severity appropriate to your firm's regulatory exposure.
3. Notify your AI Governance Lead and, for Zone 3 issues, your Compliance Officer.

---

[Back to Control 1.28](../../../controls/pillar-1-security/1.28-policy-based-agent-publishing-restrictions.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification & Testing](verification-testing.md)

---

*Updated: October 2026 | Version: v1.6.2 | UI Verification Status: Current (Microsoft Learn review 2026-10-14; tenant UI capture pending)*
