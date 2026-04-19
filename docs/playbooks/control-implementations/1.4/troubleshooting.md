# Troubleshooting: Control 1.4 — Advanced Connector Policies (ACP)

> Common failure modes, root causes, and remediations for [Control 1.4 — Advanced Connector Policies (ACP)](../../../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md). Issues use the H2 / H3 (symptom → cause → fix) structure.

---

## Issue 1 — Advanced Connector Policies option is missing from the Rules tab

### Symptom
The environment group's **Rules** tab does not list **Advanced connector policies (preview)**, or the option is greyed out.

### Cause
- Tenant has not been opted into the public-preview feature, **or**
- No environment in the group is enabled as a **Managed Environment**, **or**
- Caller does not hold **Power Platform Admin** (or higher).

### Fix
1. Confirm at least one member environment shows `Managed Environments = On` (Control 2.1).
2. Confirm caller's role: Entra > **Roles and admins** > **Power Platform Administrator** assigned (or active via PIM).
3. If the option is still hidden, the tenant may not have rolled into the preview wave — open a Microsoft support ticket referencing the [ACP Microsoft Learn article](https://learn.microsoft.com/en-us/power-platform/admin/advanced-connector-policies).

---

## Issue 2 — Status shows "Not applied" after Save

### Symptom
ACP panel header shows **Status: Not applied** even after **Save**.

### Cause
**Save** persists the rule body but does not cascade it. The cascade happens during **Publish rules**.

### Fix
1. Return to the **Rules** tab of the environment group.
2. Select **Publish rules** in the command bar.
3. Wait 5–10 minutes; reopen the panel and confirm `Status: Applied`.
4. In a member environment, **Settings** > **History** should show the lifecycle event `Update Managed Environment Settings`.

---

## Issue 3 — Maker still sees a blocked connector at design time

### Symptom
A connector that is **not** on the allowlist still appears selectable to a maker in Power Automate / Copilot Studio / Power Apps.

### Cause (one of)
- Design-time enforcement has not yet rolled out to that maker portal (rollout order: **Power Automate → Copilot Studio → Power Apps**); ACP is enforcing at runtime only for that workload.
- The connector is one of the platform **nonblockable** connectors and the environment is **not** a Managed Environment (nonblockables remain unblockable on non-MEs).
- Maker is in an environment **not** covered by the ACP rule (different group, or single-environment ACP only).

### Fix
1. Confirm the environment is in the targeted group **and** the group's ACP **Status = Applied**.
2. If non-Managed Environment: enable Managed Environments (Control 2.1).
3. Until design-time GA reaches the relevant portal, communicate to makers that runtime enforcement applies and validate via Test Scenario A run-time variant.
4. Validate a runtime block: have the maker save and run; the run should fail with a policy violation logged in Purview Audit.

---

## Issue 4 — Custom connector or HTTP connector cannot be blocked through ACP

### Symptom
Custom connector or HTTP / HTTP with Microsoft Entra ID connector is in use in a regulated environment despite an ACP allowlist.

### Cause
ACP currently applies to **certified connectors only**. Custom and HTTP connectors are out of scope — Microsoft has stated they will arrive as a separate rule type in a future release.

### Fix
1. Use a **classic DLP policy** to place custom connectors and HTTP / HTTP w/ Entra ID / HTTP Webhook in **Blocked** for the environment.
2. For approved internal HTTP usage, use **connector endpoint filtering** to restrict to internal hostnames.
3. Scope the classic DLP at **environment level** (not security-group level) so service-principal connections are also covered.
4. Keep mixed mode `On` (do **not** enable ACP-only mode) until ACP custom-connector support reaches GA.

---

## Issue 5 — Copilot Studio knowledge source / channel / skill is not blocked

### Symptom
A Copilot Studio knowledge source (e.g., public website), channel (e.g., Direct Line), or skill is in use even though ACP appears configured.

### Cause
These are **virtual connectors**. ACP does not support virtual connectors and Microsoft has stated it will not in the future. Copilot Studio virtual connectors will receive their own dedicated governance rules.

### Fix
1. Govern via **classic DLP data policies** until the dedicated rules ship.
2. In Copilot Studio, restrict knowledge sources, channels, and skills at the agent level per Control 1.5 and Control 4.x guidance.
3. Track the dedicated-rule arrival in Microsoft Power Platform release plans and update this troubleshooting entry when GA.

---

## Issue 6 — `Publish rules` fails or does not cascade

### Symptom
Selecting **Publish rules** returns an error, or `Update Managed Environment Settings` does not appear in member environment history within 30 minutes.

### Cause (one of)
- One or more member environments are in **Recovery** or **Disabled** state.
- A member environment is **not** Managed (only Managed Environments accept the cascade).
- A platform-side lifecycle conflict (concurrent environment operation) is blocking.

### Fix
1. PPAC > **Manage** > **Environments** > sort by **State**; remove or repair any environment in non-`Ready` state from the group.
2. Enable Managed Environments on every member that is missing it.
3. Wait for any in-flight environment lifecycle operations to finish, then retry `Publish rules`.
4. If retry still fails, open a support case and attach the publish response body and the failing environment's history.

---

## Issue 7 — Service-principal-authenticated flow bypasses DLP

### Symptom
A Power Automate flow running under a service-principal connection invokes a connector that should be blocked. ACP and DLP appear configured.

### Cause
DLP policy was scoped at **security-group** level. Service principals authenticate as application identities and do not have user-group membership, so security-group-scoped policies do not apply.

### Fix
1. Reauthor the classic DLP policy to scope at **environment** level (`Add multiple environments`) covering the regulated environment.
2. Use **Environment Groups** (Control 2.2) so the policy applies consistently as new environments are added to the group.
3. Audit service-principal connections quarterly: PPAC > **Data** > **Connections** > filter by `Created by = Service Principal`.

---

## Issue 8 — Action-level restriction not honoured for a specific connector

### Symptom
The maker can still invoke a disallowed action (e.g., SharePoint **Delete file**) even though the action is toggled off in ACP.

### Cause (one of)
- Connector publisher categorizes the action as **internal** or **deprecated** with different enforcement semantics.
- Allowlist was saved but `Publish rules` was not run after the action toggle change.
- The action is invoked by a child flow / wrapped solution that was created before ACP was applied (existing connections are not retroactively blocked at the connection level — only at action invocation).

### Fix
1. Re-publish the rule after every action-toggle change.
2. Inspect the action tag in ACP — `Internal` and `Deprecated` actions are explicitly tagged; turn them off individually if not already.
3. Inventory existing connections: PPAC > **Data** > **Connections**; remove or replace connections that predate the policy if they are exercising the disallowed action.
4. Validate via Test Scenario C in the verification playbook.

---

## Issue 9 — MCP server appears in the panel but cannot be blocked

### Symptom
An MCP server is listed in ACP but selecting it does not present a block option, or attempting to remove it returns an error.

### Cause
ACP supports **MCP server-level blocking** in preview. Tool-level granularity is not yet available. Some preview iterations may surface MCP servers in read-only mode for specific tenants.

### Fix
1. Confirm the tenant is on the latest preview ring; if not, open a support ticket.
2. As a compensating control, configure the Copilot Studio agent-level tool toggles to disable the specific MCP tools per agent.
3. Track removal evidence in the connector catalog and review at the next allowlist recertification.

---

## Issue 10 — Removing an environment from the group leaves the ACP rule in force

### Symptom
An environment was removed from a group and is now expected to have no ACP rule — but the previous group's allowlist is still enforcing.

### Cause
By design: each environment retains its **last known ACP configuration** when removed from a group. This prevents an accidental gap during reorganization.

### Fix
1. If the intent was to fully remove ACP from that environment: PPAC > environment > **Security** > **Data and privacy** > **Advanced connector policies (preview)** > **Remove rule**.
2. If the intent was to apply a different ACP: edit the rule directly on the environment via the same panel, or add the environment to the new group.
3. Document the decision in the change ticket so audit can trace why a previously group-managed environment now carries a single-environment policy.

---

## Issue 11 — ACP-only mode silently disabled all classic DLP enforcement

### Symptom
After enabling **Advanced connector policies only**, custom connectors and HTTP connectors that were previously blocked by classic DLP are now usable.

### Cause
ACP-only mode bypasses **all** classic DLP evaluation for affected environments. Classic DLP policies are not deleted but are no longer enforced. Because ACP does not yet cover custom and HTTP connectors, those connectors become unblocked.

### Fix
1. Toggle **Advanced connector policies only** to `Off` to return to mixed mode immediately.
2. Re-verify Test Scenarios B and C from the verification playbook.
3. Do not re-enable ACP-only mode until ACP supports custom connectors, HTTP connectors, and connector endpoint filtering, and a documented migration sign-off has been completed.

---

## Escalation Path

1. **Tier 1 — Power Platform Admin:** Verify environment / group / Managed Environments state, re-publish, capture history events.
2. **Tier 2 — AI Governance Lead:** Review allowlist policy design, mixed-mode vs. ACP-only decision, MCP inventory.
3. **Tier 3 — Microsoft Support:** Platform-side issues (publish failure, preview-feature gating, API errors). Reference the [ACP Microsoft Learn article](https://learn.microsoft.com/en-us/power-platform/admin/advanced-connector-policies) and include the Power Platform REST response body in the case.

---

## Preventive Measures

- Maintain the connector catalog in source control; the ACP allowlist body comes from the catalog, not free-hand portal edits.
- Run the PowerShell evidence script (PowerShell Setup §6) on a schedule and diff against the previous run — drift = an unapproved change.
- Recertify the allowlist on the cadence in the control's Zone matrix (monthly Zone 3 / quarterly Zone 2 / annual Zone 1).
- Configure Purview Audit alerts on `UpdateDlpPolicy` and ACP ruleset PUT operations (Control 1.7).
- Land all evidence in WORM storage so SEC 17a-4(f) preservation is satisfied.

[Back to Control 1.4](../../../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Verification & Testing](verification-testing.md)

---

*Updated: April 2026 | Version: v1.4.0*
