# Troubleshooting: Control 1.28 - Policy-Based Agent Publishing Restrictions

**Last Updated:** April 2026<br>
**Support Level:** L2 / L3 (Power Platform and Copilot Studio admins)

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
Get-DlpPolicy | Where-Object { $_.Environments -contains $envId } |
    Select-Object DisplayName, PolicyName, LastModifiedTime
```

In the portal:

1. Power Platform Admin Center → Policies → Data policies → open the policy → review **Prebuilt connectors** classification.
2. In Copilot Studio, open the agent and review the **Topics** and **Settings → Channels** for the named connector.

### Resolution Options

- **Option A — Adjust the agent.** Replace the blocked connector with an approved one, or remove the topic that uses it.
- **Option B — Reclassify the connector.** If the connector should be allowed, the Power Platform Admin moves it from Blocked to Business in the DLP policy. Document the rationale and route through change control before doing so in Zone 2+.
- **Option C — Move the environment.** If the agent legitimately belongs in a different zone, reassign the environment to a more permissive zone DLP policy. This is an exceptional step in regulated environments and requires zone reclassification per **Control 2.2**.

### Prevention

- Publish the zone-by-zone connector allowlist to agent authors.
- Add a pre-build checklist requiring authors to confirm connector choices against the allowlist for the target environment's zone.

---

## Issue 2 — Update to a Published Agent Is Blocked (February 2025 Behavior)

### Symptoms

- A previously published agent cannot be updated; the publish action surfaces a DLP finding.
- The previously published version of the agent continues to serve users.

### Likely Causes

- DLP policy tightening after publish (for example, a connector moved from Business to Blocked).
- Microsoft removed the "Soft-Enabled" DLP exemption in February 2025; published agents are now subject to DLP at update time, not just at first publish.

### Diagnostics

- Compare DLP policy `LastModifiedTime` to the agent's `LastModifiedTime` to confirm the policy changed after publish.
- Confirm via Purview audit (workload `PowerPlatformAdmin`) which actor changed the DLP policy and when.

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
- The environment's policy assignment was recently changed and the cache has not refreshed (rare; typically resolves within minutes).
- The agent uses a custom connector that the DLP policy does not classify (custom connectors require explicit Default behavior = Block).

### Diagnostics

```powershell
# Confirm policy → environment binding.
Get-DlpPolicy | ForEach-Object {
    $p = $_
    $p.Environments | ForEach-Object {
        [pscustomobject]@{
            PolicyDisplayName = $p.DisplayName
            EnvironmentId     = $_
        }
    }
} | Where-Object EnvironmentId -eq '<environment-id>'
```

In the portal, confirm Policies → Data policies → [Policy] → **Scope** lists the expected environment.

### Resolution Options

- Add the environment to the correct zone DLP policy.
- Move the offending connector from Non-Business to Blocked.
- Set Custom connectors → Default behavior to **Block** in the policy.
- Disable the prohibited channel in **Settings → Channels** as a defense-in-depth control.

### Prevention

- Use explicit environment selection (not "Add all environments") and review scope monthly.
- Avoid the Non-Business group for Zone 2+ policies; the recommended pattern is Business + Blocked only.

---

## Issue 4 — Approval Workflow Did Not Trigger

### Symptoms

- The author publishes in a Zone 2+ environment and the publish completes without any approval being requested.

### Likely Causes

- The Power Automate flow that watches the Dataverse `bot` table is disabled, scoped to the wrong environment, or filtering on the wrong condition.
- The author has the Power Platform Admin role and is exempted from the surrounding approval flow by design.
- The flow's connection reference uses an account that no longer has access to the Dataverse environment.

### Diagnostics

- Open Power Automate → My flows; confirm the approval flow status is **On**.
- Open the flow's run history and confirm runs are appearing for recent agent publishes.
- Confirm the trigger's environment scope matches the environment where the publish happened.
- Confirm the connection references are healthy (no broken connections).

### Resolution Options

- Re-enable or repair the flow.
- If the trigger filter excludes admin accounts deliberately, document this in the control evidence; otherwise, broaden the filter.
- Repair connection references and re-test.

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
- The session authenticated against the wrong cloud (commercial endpoint while the tenant is in GCC / GCC High / DoD).
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
- Re-authenticate with the correct sovereign-cloud endpoint: `Add-PowerAppsAccount -Endpoint usgov` (GCC) / `usgovhigh` (GCC High) / `dod` (DoD).
- Confirm the signed-in account holds the Power Platform Admin role (or use a service principal that does).

### Prevention

- Add the PowerShell guard from the [PowerShell Setup](powershell-setup.md) playbook to every script. It throws when running under a non-Desktop edition rather than producing false-clean evidence.
- Document the sovereign-cloud endpoint in your runbooks; do not rely on per-operator memory.

---

## Issue 8 — DLP Policy Cmdlet Names Do Not Resolve

### Symptoms

- `New-DlpPolicy` (or the older `New-AdminDlpPolicy`) is not recognized as the name of a cmdlet.

### Likely Causes

- The `Microsoft.PowerApps.Administration.PowerShell` module is not installed or not imported in the current session.
- The pinned module version predates the rename of the DLP cmdlets (older versions used the `Admin`-prefixed names; current Microsoft Learn documents the non-prefixed names).

### Diagnostics

```powershell
Get-Module -Name Microsoft.PowerApps.Administration.PowerShell -ListAvailable
Get-Command -Module Microsoft.PowerApps.Administration.PowerShell -Name *Dlp*
```

### Resolution Options

- Install or import the module per the [PowerShell Setup](powershell-setup.md) playbook.
- If your pinned version exposes only `*-AdminDlpPolicy`, use those names consistently. If it exposes both, prefer the non-prefixed names per current Microsoft Learn guidance and use them consistently across your scripts.

### Prevention

- Pin a single module version per CAB-approved baseline and avoid mixing cmdlet name conventions in the same automation.

---

## Issue 9 — Audit Events Missing in Purview

### Symptoms

- Bot publish events do not appear in Purview audit search even though the publish clearly happened.

### Likely Causes

- Events have not yet been ingested (Purview audit ingestion typically lags 30–60 minutes).
- The audit search filter is too narrow (wrong workload or date range).
- Auditing was disabled in the tenant or for the relevant workload.

### Diagnostics

- Wait at least 60 minutes after the activity before re-searching.
- Broaden the search to `All workloads` to confirm ingestion is happening for other activity.
- Confirm Purview Audit (Standard) is enabled for the tenant.

### Resolution Options

- Re-enable auditing if disabled.
- Use the **PowerPlatformAdmin** and **Dataverse** workload filters specifically when looking for agent publish events.
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

*Updated: April 2026 | Version: v1.3.3 | UI Verification Status: Current*
