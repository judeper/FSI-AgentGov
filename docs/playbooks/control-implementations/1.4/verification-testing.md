# Verification & Testing: Control 1.4 — Advanced Connector Policies (ACP)

> Audit-ready verification guide for [Control 1.4 — Advanced Connector Policies (ACP)](../../../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md). Use the numbered checklist as the test plan and the test scenarios as repeatable procedures. Evidence artifacts are mapped to the regulations cited on the control page.

---

## Verification Checklist

Each item below is binary pass/fail. Capture evidence (screenshot, JSON export, audit-log row) per the **Evidence** column.

| # | Verification step | Where | Expected | Evidence |
|---|---|---|---|---|
| 1 | Managed Environments enabled on every in-scope environment | PPAC > **Manage** > **Environments** > environment > **Overview** | `Managed Environments = On` | Screenshot |
| 2 | Each in-scope environment is in the correct environment group with documented zone classification | PPAC > **Manage** > **Environment groups** | Environment listed in expected group | Screenshot of group **Environments** tab |
| 3 | ACP rule **Status: Applied** at the group scope | PPAC > **Environment groups** > [group] > **Rules** tab > **Advanced connector policies (preview)** | Header shows `Status: Applied` | Screenshot |
| 4 | ACP rule **Status: Applied** at any single-environment scope (where used) | PPAC > environment > **Security** > **Data and privacy** > **Advanced connector policies (preview)** | Header shows `Status: Applied` | Screenshot |
| 5 | Allowlist contents match the approved connector catalog | Same panel | Connector list = catalog for that zone | JSON export from PowerShell §6a |
| 6 | Action-level restrictions enforced on each allowlisted connector (read-only by default unless ticketed) | Expand each connector in the panel | Disallowed actions toggled off; deprecated/internal actions marked | Screenshot of one high-risk connector (e.g., SharePoint) |
| 7 | **Publish rules** has cascaded to every member environment | PPAC > each member environment > **Settings** > **History** | `Update Managed Environment Settings` event within last 24h of publish | Screenshot |
| 8 | Mixed mode active (classic DLP still evaluating custom + HTTP) — or ACP-only mode explicitly approved | **Rules** tab toggle `Advanced connector policies only` | Toggle = `Off` (mixed mode) for FSI default | Screenshot |
| 9 | Classic DLP policy covers HTTP, HTTP w/ Entra, and custom connectors at **environment** scope (covers service principals) | PPAC > **Policies** > **Data policies** > policy > **Scope** | Scope = `Add multiple environments` listing the in-scope envs (not security group) | Screenshot |
| 10 | Connector endpoint filtering configured for any allowed HTTP-class connector | Classic DLP policy > HTTP connector > **Configure connector** | Allowed endpoints limited to internal hosts | Screenshot |
| 11 | MCP server inventory matches approved-server list; no unapproved MCP server present in allowlist | ACP panel > MCP servers section | Only approved server IDs present | Screenshot + inventory CSV |
| 12 | Maker test confirms design-time block of a non-allowlisted certified connector | Power Automate maker portal (sign in as test maker, attempt to add a blocked connector) | Error: `This connector is blocked by your administrator` | Screenshot |
| 13 | Maker test confirms cross-classification DLP block | Power Automate maker portal (attempt to use Business + Non-Business in same flow) | DLP policy violation message; flow cannot save | Screenshot |
| 14 | Purview Audit captures the ACP/DLP change events | Purview portal > **Audit** > **Search** > Activities = `UpdateDlpPolicy`, `PublishConnectorRuleSet` (or current operation names); time window covering the change | Each change attributable to a named admin with timestamp | CSV export |
| 15 | Allowlist recertification cadence current (monthly Zone 3 / quarterly Zone 2 / annual Zone 1) | Connector catalog system | Last review date within cadence window | System report |

---

## Test Scenario A — Blocked Certified Connector Cannot Be Added

**Goal:** Prove default-deny posture works in design time.

1. Sign in to `https://make.powerautomate.com` as a maker user assigned only to a regulated environment.
2. **My flows** > **+ New flow** > **Instant cloud flow** > **Manually trigger a flow** > **Create**.
3. Select **+ New step**.
4. Search for a connector that is **not** on the allowlist (e.g., `Twitter` / `X (Twitter)`).
5. Attempt to select the connector.
6. **Expected:** the connector is either not surfaced or, if surfaced, displays `This connector is blocked by your administrator` and cannot be added.
7. Capture the error banner screenshot.

> If design-time enforcement is not yet GA in the maker portal under test (per the Microsoft rollout order: Power Automate → Copilot Studio → Power Apps), the block manifests at runtime instead — repeat the test by attempting to **save and run** a flow built outside the regulated environment and imported.

---

## Test Scenario B — Cross-Classification DLP Block

**Goal:** Prove classic DLP boundary still enforces in mixed mode.

1. As the same maker, create a flow that uses one **Business**-classified connector (e.g., SharePoint, Get items) and one **Non-Business** or **Blocked** connector (e.g., `RSS` if non-business in your tenant).
2. Attempt to **Save**.
3. **Expected:** save fails with `Flow's connectors don't comply with data loss prevention policies`. Flow is not saved or is suspended.
4. Capture the error message.

---

## Test Scenario C — Action-Level Restriction Block

**Goal:** Prove a connector that is on the allowlist still blocks disallowed actions.

1. As the maker, create a flow using SharePoint (which is allowlisted).
2. Attempt to add the **Delete file** action (which should be turned off in the ACP allowlist).
3. **Expected:** the action is hidden, greyed out, or selecting it returns a policy error at design or save time.
4. Capture the screenshot.

---

## Test Scenario D — MCP Server Block

**Goal:** Prove unapproved MCP servers are blocked at server level.

1. Identify an MCP server present in the tenant that is **not** on the approved-server inventory.
2. In Copilot Studio, attempt to add it as a tool to a test agent in a regulated environment.
3. **Expected:** the MCP server cannot be added, or, if added, the agent fails to invoke any tool from it with a policy error.
4. Capture the screenshot.

---

## Test Scenario E — Service-Principal Connection Cannot Bypass

**Goal:** Prove environment-scoped DLP catches service-principal authentications.

1. Identify (or stand up) a Power Automate flow authenticated via a service principal connection in a regulated environment.
2. Reconfigure the flow to use a connector that is **Blocked** by the environment-scoped classic DLP policy.
3. **Expected:** flow run fails with a DLP policy violation logged to Purview Audit, with the service principal as the actor.
4. Capture the run-history error and the corresponding audit row.

---

## Evidence Package for Examiners

Bundle the following per environment group, per test cycle, for FINRA / SEC / OCC examination:

1. **`acp-ruleset-<timestamp>.json`** — current allowlist body (PowerShell §6a) with SHA-256 in `manifest.json`.
2. **Screenshot pack** — items 1–11 from the checklist.
3. **Test-result pack** — Scenarios A–E screenshots with maker UPN, environment ID, and timestamp watermark.
4. **Purview Audit export** — `UpdateDlpPolicy` / ACP rule changes for the period under review (CSV, signed with PowerShell `Get-FileHash`).
5. **Recertification minutes** — CAB or AI Governance Council meeting record approving the current allowlist with date and attendees.
6. **Connector catalog** — current connector and MCP-server inventory listing owner, business purpose, security review date, and zone scope.
7. **Mixed-mode coverage proof** — classic DLP policy export showing custom connector and HTTP connector scope at environment level (not security-group level).

> Land the bundle in WORM-locked storage (Microsoft Purview retention-locked location or Azure Storage immutability container) per SEC 17a-4(f) and FINRA 4511.

---

## Confirmation Sign-Off

- [ ] Checklist items 1–15 pass
- [ ] Test scenarios A–E pass and screenshots captured
- [ ] Evidence bundle landed in WORM storage with manifest hash recorded
- [ ] Power Platform Admin and AI Governance Lead countersigned the cycle

[Back to Control 1.4](../../../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md) | [Portal Walkthrough](portal-walkthrough.md) | [PowerShell Setup](powershell-setup.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
