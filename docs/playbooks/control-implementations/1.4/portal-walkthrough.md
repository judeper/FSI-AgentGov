# Portal Walkthrough: Control 1.4 — Advanced Connector Policies (ACP)

**Last Updated:** May 2026
**Portal:** Power Platform Admin Center (`https://admin.powerplatform.microsoft.com`)
**Estimated Time:** 45–60 minutes (first environment group); 15 minutes per additional environment
**Primary Owner Admin Role:** Power Platform Admin

> Portal configuration guide for [Control 1.4 — Advanced Connector Policies (ACP)](../../../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md). ACP is the default-deny, action-aware connector governance layer that supersedes the Business / Non-Business / Blocked classification model in classic data policies for **certified connectors**. Custom connectors, HTTP connectors, and Microsoft Copilot Studio virtual connectors continue to require classic DLP coverage.

---

## Prerequisites

| # | Item | Where to confirm |
|---|------|------------------|
| 1 | Target environment is in a **United States** region | PPAC > **Manage** > **Environments** > environment row > **Region** |
| 2 | **Managed Environments** enabled (Control 2.1) | Environment **Overview** > **Managed Environments** = `On` |
| 3 | Environment is in an **Environment Group** (Control 2.2) | PPAC > **Manage** > **Environment groups** |
| 4 | Documented **approved connector catalog** with owner, business purpose, security review date, and zone scope | Internal change-management system (ServiceNow, Jira, etc.) |
| 5 | Classic DLP policy already covering custom connectors and HTTP endpoints (will run in **mixed mode** alongside ACP) | PPAC > **Policies** > **Data policies** |
| 6 | Caller holds **Power Platform Admin** role; sensitive change windows use Entra PIM just-in-time elevation (Control 1.1) | Entra admin center > **Roles and admins** |

> **Mixed mode (recommended for FSI):** Until ACP supports custom connectors, HTTP connectors, and connector endpoint filtering, leave classic DLP policies enabled. The runtime engine evaluates the most restrictive of both systems.

---

## Step 1 — Enable Managed Environments (if not already on)

1. Sign in to the **Power Platform Admin Center**.
2. Navigate **Manage** > **Environments**.
3. Select the target environment row, then **Enable Managed Environments** in the command bar.
4. Set FSI-recommended values:
   - **Limit sharing:** `Exclude sharing with security groups` (or stricter)
   - **Usage insights:** `On`
   - **Maker welcome content:** Point to your internal AI governance landing page
   - **Solution checker enforcement:** `Block`
5. Select **Enable**.

> Managed Environments is required for ACP to block **nonblockable connectors** (Dataverse, Office 365 Users, etc.). On non-Managed Environments, ACP can still be authored, but those connectors remain unblockable.

---

## Step 2 — Confirm or Create the Environment Group

1. **Manage** > **Environment groups**.
2. Select **+ New group** (skip if already created).
3. Name using the FSI tier convention, e.g., `Zone3-Regulated-Production` or `Zone2-Team-Collaboration`.
4. Description must record the regulatory scope, e.g., `Zone 3 — production environments hosting customer-facing agents subject to SEC Reg S-P, FINRA 4511, and SOX 404 ITGCs.`
5. **Add environments** > select the in-scope environments > **Save**.

---

## Step 3 — Author the Advanced Connector Policy (Group Scope)

> **Default-deny:** ACP blocks every certified connector and every action by default. You only ever **add** approvals. Authoring an empty policy = blocking everything except platform nonblockable connectors.

1. Open the environment group from Step 2.
2. Select the **Rules** tab.
3. Select **Advanced connector policies (preview)**.
4. Review the preloaded **nonblockable connectors** (Dataverse, Office 365 Users, Approvals, Notifications). On Managed Environments these can also be removed if your zone policy requires it.
5. Select **+ Add connectors** and add only the connectors on the approved allowlist for this zone.
6. For each added connector, select it to expand the **Actions** panel:
   - Use the **Triggers**, **Actions**, **Internal actions**, and **Deprecated** tags to make explicit allow/deny decisions.
   - Toggle **off** every action that is not required for the documented agent use case.
   - Default to **read / list / get** actions only; require a separate change ticket to enable **create / update / delete**.
7. Select **Save**.
8. Return to the **Rules** tab and select **Publish rules** in the command bar.
9. Confirm the policy panel header displays **Status: Applied**.
10. In each member environment, **Settings** > **History** should show an entry **Update Managed Environment Settings** within 5–10 minutes — this is the cascade of the ACP rule into design-time and runtime infrastructure.

### FSI suggested allowlist (Zone 2 baseline)

| Connector | Allowed actions (illustrative) | Notes |
|---|---|---|
| Microsoft Dataverse | List rows, Get row by ID | Add Create/Update only with CAB approval |
| SharePoint | Get items, Get file content | Block Send HTTP request to SharePoint, Delete file, Set permissions |
| Office 365 Outlook | Send email V2 (to internal recipients only — enforce via Exchange transport rule, not ACP) | No external mailbox actions for Zone 3 |
| Microsoft Teams | Post message in chat or channel | Block Create team / Add member / Export |
| Approvals | Create approval, Wait for approval | Workflow only |

### FSI standing blocklist (Zone 2 / Zone 3)

Do **not** add to the allowlist:

- All social-media connectors (X/Twitter, Facebook, LinkedIn, Instagram, TikTok)
- Consumer cloud storage (Dropbox, Box personal, Google Drive personal, OneDrive consumer)
- Consumer messaging (WhatsApp, Telegram, Discord)
- Public-AI passthrough connectors whose terms permit training on inputs
- Any connector whose data-processing region cannot be constrained to United States

> Connectors are blocked simply by **not being in the allowlist** — there is no separate denylist to maintain.

---

## Step 4 — Single-Environment ACP (Targeted Governance)

Use this path for a single regulated, pilot, or quarantined environment that is not part of a group, or whose policy must differ from its group.

1. **Security** > **Data and privacy**.
2. Select **Advanced connector policies (preview)**.
3. Author the policy using the same connector + actions controls as Step 3.
4. Select **Save**.
5. Confirm **Status: Applied** appears at the top of the panel.

> Each environment supports **one effective ACP**. If the environment was previously in a group, removing it leaves the last group ACP attached until you edit it or use **Remove rule**.

---

## Step 5 — Mixed Mode vs. ACP-Only Mode (Decision)

| Mode | When to use | FSI recommendation |
|---|---|---|
| **Mixed mode** (default) | Any tenant that still needs custom connector, HTTP, virtual connector, or endpoint-filter governance | **Default for FSI.** Keep classic DLP active until ACP gains parity. |
| **ACP-only mode** | Tenants that fully migrated all governance to ACP and want a single policy surface | Only enable after a documented migration sign-off; otherwise classic DLP rules silently stop enforcing. |

To enable **ACP-only mode** at the group scope: **Rules** tab > toggle **Advanced connector policies only** to `On`.
At the single-environment scope: **Security** > **Data and privacy** > toggle **Advanced connector policies only** to `On`.

> ACP-only mode does not delete classic DLP policies — it stops evaluating them. To return to mixed mode, toggle off.

---

## Step 6 — Classic DLP Coverage for the ACP Gap

For every environment covered by ACP, also confirm a classic DLP policy is scoped to it that:

1. Places **HTTP**, **HTTP with Microsoft Entra ID**, and **HTTP Webhook** connectors in **Blocked** unless used by an approved internal flow (then use **connector endpoint filtering** to restrict to internal hosts).
2. Places all **custom connectors** in **Blocked** by default; allowlist only after security review (Control 2.7).
3. Places **Copilot Studio virtual connectors** (knowledge sources, channels, skills) in the appropriate group — these are **not** governed by ACP and will not be in the future.
4. Is scoped at the **environment level**, not security-group level, so service-principal-authenticated connections are also covered (see the Service Principal warning on the control page).

---

## Step 7 — MCP Server Governance (Preview)

1. In the same **Advanced connector policies** panel, scroll to the MCP servers section.
2. Each registered MCP server appears alongside connectors.
3. Block any MCP server that is not on the approved-server inventory by removing it from the allowlist.
4. Document the server-level decision in the connector catalog (server ID, owner, business purpose, supported zones).

> ACP supports **server-level** MCP blocking only. Tool-level granularity is not yet available — combine with the Copilot Studio agent-level tool toggles for layered control.

---

## Step 8 — Verify Publish and Capture Evidence

1. Reopen the policy panel; **Status** must read **Applied**.
2. Open one member environment > **Settings** > **History**; confirm **Update Managed Environment Settings** entry within the last 10 minutes.
3. Sign in as a **maker** (non-admin) and attempt to add a non-allowlisted connector to a flow or Copilot Studio agent — design-time enforcement should display **"This connector is blocked by your administrator"** in Power Automate maker portal (and in Copilot Studio / Power Apps as design-time enforcement reaches GA per the maker portal rollout).
4. Capture the screenshots listed in `docs/images/1.4/EXPECTED.md` and store under `maintainers-local/tenant-evidence/1.4/`.

---

## Configuration Matrix by Governance Zone

| Setting | Zone 1 (Personal) | Zone 2 (Team) | Zone 3 (Enterprise) |
|---|---|---|---|
| ACP rule | Optional | Required (group scope) | Required (group scope, strict allowlist) |
| Classic DLP (mixed mode) | Tenant-wide | Required | Required |
| Action-level allowlisting | N/A | Read by default; CAB for write | Read-only by default; CAB + security review for any write |
| MCP servers | Not allowed | Internal-only, named approval | Internal + vetted vendor only, server-level inventory |
| Allowlist recertification | Annual | Quarterly | Monthly |
| ACP-only mode | Not used | Not recommended | Not recommended until parity achieved |

---

## Related Resources

- [Microsoft Learn — Advanced connector policies](https://learn.microsoft.com/en-us/power-platform/admin/advanced-connector-policies)
- [Microsoft Learn — Connector endpoint filtering](https://learn.microsoft.com/en-us/power-platform/admin/connector-endpoint-filtering)
- [Microsoft Learn — Data policies (classic DLP)](https://learn.microsoft.com/en-us/power-platform/admin/wp-data-loss-prevention)
- [Microsoft Learn — Environment groups](https://learn.microsoft.com/en-us/power-platform/admin/environment-groups)
- [Microsoft Learn — Connector classification](https://learn.microsoft.com/en-us/power-platform/admin/dlp-connector-classification)

[Back to Control 1.4](../../../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md) | [PowerShell Setup](powershell-setup.md) | [Verification & Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
