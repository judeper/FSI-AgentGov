# Portal Walkthrough: Control 1.5 - Data Loss Prevention (DLP) and Sensitivity Labels

**Control:** [1.5 Data Loss Prevention and Sensitivity Labels](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md)
**Audience:** M365 administrator (US financial services)
**Last UI Verified:** April 2026
**Cloud coverage:** Commercial · GCC · GCC High · DoD (see sovereign cloud table below)
**Estimated Time:** 3–6 hours (excludes propagation windows and pilot validation)

> This playbook provides portal configuration guidance for [Control 1.5](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md). It is written to support compliance with FINRA 3110/4511, SEC Reg S-P, GLBA 501(b), and SOX 404; it does not, by itself, satisfy any single regulatory obligation. Organizations should verify configuration against their own obligations.

---

!!! warning "Two distinct DLP control planes — do not conflate them"
    This walkthrough covers **two separate Microsoft products** with different portals, cmdlets, and licensing. A change to one does **not** apply to the other.

    | Surface | Governs | Portal (Commercial) | Cmdlet family |
    |---|---|---|---|
    | **Microsoft Purview DLP** (location: *Microsoft 365 Copilot and Copilot Chat*) | First-party Microsoft 365 Copilot and Copilot Chat — prompts and labeled grounding files | `https://purview.microsoft.com` | `Get-DlpCompliancePolicy` / `Get-DlpComplianceRule` |
    | **Power Platform data policies** | Copilot Studio agents, connector classification, channel publishing | `https://admin.powerplatform.microsoft.com` | `Get-DlpPolicy` (PowerApps cmdlets) |

    Reference: [DLP for Microsoft 365 Copilot location (Learn)](https://learn.microsoft.com/en-us/purview/dlp-microsoft365-copilot-location-learn-about) and [Power Platform DLP overview (Learn)](https://learn.microsoft.com/en-us/power-platform/admin/wp-data-loss-prevention).

---

## Sovereign cloud portal endpoints

| Cloud | Purview portal | Power Platform Admin Center | Notes |
|---|---|---|---|
| Commercial | `https://purview.microsoft.com` | `https://admin.powerplatform.microsoft.com` | Reference cloud for this walkthrough |
| GCC | `https://compliance.microsoft.com` (transitioning to `purview.microsoft.com`) | `https://admin.powerplatform.microsoft.us` | Verify rollout per workload |
| GCC High | `https://purview.microsoft.us` | `https://admin.powerplatform.microsoft.us` | Adaptive Protection / IRM **not at parity** |
| DoD | `https://purview.microsoft.us` (DoD instance) | `https://admin.powerplatform.microsoft.us` | Adaptive Protection / IRM **not at parity** |

For PowerShell parity see `docs/playbooks/_shared/powershell-baseline.md`.

---

## Prerequisites

Before starting, confirm:

- Microsoft 365 E5 / E5 Compliance / Microsoft Purview Suite per monitored user (verify against the [Purview DLP licensing guidance](https://learn.microsoft.com/en-us/office365/servicedescriptions/microsoft-365-service-descriptions/microsoft-365-tenantlevel-services-licensing-guidance))
- Microsoft 365 Copilot per-user licensing for users in scope of the Copilot DLP location
- A defined sensitivity label taxonomy (see Step 6) approved by Information Protection / Records
- SITs from [Control 1.13](../../../controls/pillar-1-security/1.13-sensitive-information-types-sits-and-pattern-recognition.md) deployed and validated (with documented confidence threshold and proximity)
- Agent inventory (Control 1.4 / Control 2.16) so you know which agents touch which data
- For endpoint rules: a Defender for Endpoint subscription **or** Purview standalone device onboarding (see Step 4)
- Roles available: **Purview Compliance Admin** (DLP), **Purview Information Protection Admin** (labels), **Power Platform Admin** (data policies), **Insider Risk Management** role group (Adaptive Protection), and an Endpoint admin (Intune) for browser/device coverage

> **Least privilege.** Avoid Entra Global Admin where a workload-specific role is sufficient. The Microsoft 365 Copilot and Copilot Chat DLP location does **not support administrative units** — a Restricted Administrative Unit-scoped admin cannot create or edit a policy that includes this location. Use a tenant-scoped role instead.

---

## Propagation banner (read once, applies to every step)

!!! danger "Plan validation windows around propagation"
    - **Purview DLP for the Microsoft 365 Copilot and Copilot Chat location:** changes can take **up to 4 hours** to take effect. Treat earlier "no match" results as inconclusive, not as failure.
    - **Power Platform data policies:** allow ~1–2 hours for connector-classification changes to propagate to runtime.
    - **Sensitivity labels:** publishing a label policy can take **up to 24 hours** to surface in Office clients.
    - **Auto-labeling:** initial simulation can take hours to days depending on corpus size.

    Always start new policies in **Test with policy tips / Test with notifications** mode and only move to enforcement after the propagation window and a documented validation pass.

---

## Step 1 — Create the Purview DLP policy from the **Custom** template

> **Why Custom?** The Standard templates (Financial, Privacy, etc.) **do not surface** the *Microsoft 365 Copilot and Copilot Chat* location. You must use the Custom > Custom policy path to expose it. Source: [Learn — DLP for Microsoft 365 Copilot location](https://learn.microsoft.com/en-us/purview/dlp-microsoft365-copilot-location-learn-about).

1. Sign in to your tenant cloud's Purview portal (see sovereign cloud table)
2. **Solutions** > **Data Loss Prevention** > **Policies**
3. Select **+ Create policy**
4. On *Choose a category and template*, select **Custom** > **Custom policy** > **Next**
5. Name the policy (e.g., `FSI-Copilot-DLP-Baseline`) and add a description that references this control and the change ticket
6. Set the admin scope. **Do not** select a Restricted Administrative Unit — the Copilot location does not support AUs
7. On *Choose locations*, enable **Microsoft 365 Copilot and Copilot Chat** (and any other locations in scope, e.g., SharePoint sites, OneDrive accounts, Exchange email, Devices). Configure include/exclude scoping to the user/group population from your agent inventory
8. Click **Next** to enter the rule editor (see Step 2)

> Reference click-path: [Create and deploy data loss prevention policies (Learn)](https://learn.microsoft.com/en-us/purview/dlp-create-deploy-policy).

---

## Step 2 — Author **two separate rules** (same policy)

!!! danger "Same-rule restriction (read before authoring rules)"
    For the **Microsoft 365 Copilot and Copilot Chat** location, you **cannot** combine *Content contains > Sensitive info types* and *Content contains > Sensitivity labels* in the **same rule**. The Purview UI will reject saving a single rule that contains both conditions. You must create **two rules in the same policy**: Rule A (SITs) and Rule B (sensitivity labels). Source: [Learn — DLP for Microsoft 365 Copilot location](https://learn.microsoft.com/en-us/purview/dlp-microsoft365-copilot-location-learn-about) (Important callout).

### Rule A — SIT condition (prompts)

1. On the *Customize advanced DLP rules* page click **+ Create rule**
2. Name it `Rule-A-SITs-Copilot-Prompts`
3. Under **Conditions** > **Content contains** > **Add** > **Sensitive info types**, select the SITs from Control 1.13 (e.g., `U.S. Bank Account Number`, `U.S. SSN`, `Credit Card Number`, plus any custom FSI SITs). Record the confidence and proximity used.
4. Leave the *Content contains > Sensitivity labels* row empty for this rule.
5. Configure **Actions** per Step 3 below.
6. Save the rule.

### Rule B — Sensitivity label condition (block-by-label)

1. Click **+ Create rule** again
2. Name it `Rule-B-Labels-Copilot-Grounding`
3. Under **Conditions** > **Content contains** > **Add** > **Sensitivity labels**, select **Highly Confidential** (and **Confidential** if your zone matrix calls for it)
4. Leave the *Sensitive info types* row empty for this rule
5. Configure **Actions** per Step 3 below
6. Save the rule

> If the UI shows a validation banner referencing combined-condition restriction, you have placed both condition types in one rule — split them.

---

## Step 3 — Configure actions and **start in Test with policy tips**

For each rule:

1. **Actions**:
    - Rule A (SITs in prompts): action **Restrict Copilot from processing prompts containing this content** (preview capability — verify Roadmap before relying on it as a sole Zone 3 control)
    - Rule B (label grounding): action **Prevent Microsoft 365 Copilot and Copilot Chat from processing the content** (GA)
2. **User notifications**: enable policy tips with FSI-appropriate text referencing the internal data-handling standard
3. **Incident reports**: send to the DLP / SecOps shared mailbox; severity per zone
4. **Mode**: select **Test with notifications** (also labeled *Test with policy tips* in some UI variants). Do **not** turn on enforcement at first save.
5. Save the policy and capture a screenshot for evidence (filename suggestion: `1.5-06-purview-dlp-create.png`)

!!! warning "Block-by-label scope (read before announcing the policy)"
    The *Prevent Copilot from processing the content* action applies only to:

    - Files in **SharePoint Online** and **OneDrive for Business**
    - **Emails sent on or after January 1, 2025** (Exchange Online)
    - **Calendar invites are NOT supported**
    - Items still appear in **citations with a link** even when content is not summarized into the response
    - **Files uploaded directly into a Copilot prompt are NOT scanned by this DLP location**

    Communicate these boundaries to stakeholders so the control is not assumed to be broader than its documented scope.

After the propagation window (up to 4 hours), proceed to Step 8 (verification) before flipping to enforcement.

---

## Step 4 — Endpoint DLP: device onboarding (prerequisite)

Endpoint DLP rules — including those that watch for sensitive data in browser uploads to consumer AI sites — apply only to **onboarded devices**. If devices are not onboarded, your endpoint rules will silently produce zero matches.

1. **Solutions** > **Settings** > **Device onboarding** in the Purview portal (or use Defender for Endpoint if already deployed; managed devices auto-onboard once Defender is enabled with the shared signal)
2. Choose your onboarding method (local script, Group Policy, Intune, MECM, or VDI). Reference: [Onboarding tools and methods (Learn)](https://learn.microsoft.com/en-us/purview/device-onboarding-overview)
3. Push the onboarding package to a pilot ring first
4. Confirm devices appear in **Device onboarding** > **Devices** with a status of *Active*
5. Reconcile the device inventory to your monitored-user list; record any gap as a coverage exception

> Until devices show as Active, endpoint DLP rules referenced by this control are not evaluated on those endpoints.

---

## Step 5 — Browser coverage: Edge and Chrome / Firefox

Endpoint DLP and the third-party AI signals used by DSPM for AI rely on browser instrumentation:

- **Microsoft Edge:** push the **Edge configuration policy** via Intune (this is the configuration policy, not a browser extension). Document the Intune policy ID and assignment scope.
- **Chrome / Firefox (Windows-only):** push the **Microsoft Purview browser extension** via Intune to in-scope devices.
- For each browser, configure the list of unallowed/restricted apps and unallowed/restricted sites under **Purview** > **Settings** > **Endpoint DLP settings** > **Browser and domain restrictions to sensitive data** (and the per-policy **Service domains** list).
- Capture a per-device coverage report; users without coverage will silently miss third-party AI events.

Cross-reference: [Control 1.6 portal walkthrough — Step 3 (Browser support)](../1.6/portal-walkthrough.md).

---

## Step 6 — Sensitivity labels: create, **publish**, and understand the boundaries

> **Labels do not appear to users until a label policy is published.** Creating a label is not enough.

### 6a. Create labels

1. Purview portal > **Solutions** > **Information Protection** > **Labels**
2. Select **+ Create a label**
3. Define the FSI taxonomy (illustrative — adjust to your scheme):

    | Label | Default posture |
    |---|---|
    | **Public** | Allow; audit optional |
    | **Internal** | Allow; audit recommended |
    | **Confidential** | Warn or restrict; always log |
    | **Highly Confidential** | Block-by-label for Copilot processing; incident report |

4. Configure encryption, content marking, and auto-labeling settings as needed. Save.

### 6b. Publish a label policy

1. **Information Protection** > **Label policies** > **+ Publish labels**
2. Select the labels created in 6a
3. Scope to the users and groups who create or handle content (and to agent owners and to compliance reviewers)
4. Configure default label, justification requirements, and mandatory labeling per zone
5. Save and allow up to 24 hours for clients to refresh

Reference: [Sensitivity labels overview (Learn)](https://learn.microsoft.com/en-us/purview/sensitivity-labels).

### 6c. Auto-labeling — locations and limits

1. **Information Protection** > **Auto-labeling** > **+ Create auto-labeling policy**
2. Select location(s). The **only** auto-labeling locations supported by Purview are:
    - **SharePoint Online** sites
    - **OneDrive for Business** accounts
    - **Exchange Online** mailboxes
3. There is **no "AI interactions" auto-labeling location.** Auto-labeling does not label Copilot prompts or agent responses. Label-based DLP for Copilot relies on labels already present on the underlying SPO / OneDrive / Exchange items at the time of the prompt.
4. Run the policy in **Simulation** first; review matches; then turn on
5. Reference: [Apply a sensitivity label automatically (Learn)](https://learn.microsoft.com/en-us/purview/apply-sensitivity-label-automatically)

### 6d. Container vs. file labels

Labels applied to Microsoft 365 Groups, Teams, and SharePoint sites govern **container-level settings** (privacy, external sharing, device access, default link types). Items inside the container do **not** inherit the container label. File-level labeling requires a published file/email label policy, an auto-labeling policy, or manual application.

---

## Step 7 — Power Platform data policies (Copilot Studio agents)

> This is a **separate product** from Purview DLP. Configure it in PPAC.

### 7a. Create or edit a data policy

1. Sign in to PPAC (`https://admin.powerplatform.microsoft.com` — sovereign URL per the table above)
2. **Policies** > **Data policies**
3. Select an existing policy or **+ New policy**
4. Name and assign environments per zone

### 7b. Classify connectors

In the **Connectors** tab, classify each connector as **Business**, **Non-Business**, or **Blocked**. Connectors classified Business and Non-Business **cannot be combined in the same agent / app / flow**; Blocked connectors cannot be used at all.

> The Power Platform connector catalog is maintained by Microsoft and grows over time. Refer to the live PPAC list for current inventory rather than relying on a static count. AI-related connectors (AI Builder, Copilot Studio knowledge / topics / skills, HTTP with Microsoft Entra ID, HTTP Webhook, Direct Line, channel connectors) are subject to the same classification model.

Cross-reference Control 1.5 (Control Description > *Power Platform Virtual Governance Connectors*) for the recommended per-zone classification matrix. Channels published by Copilot Studio agents are also classified here — block channels you have not approved.

### 7c. Endpoint filtering for HTTP with Microsoft Entra ID (PREVIEW)

!!! info "Preview status"
    **Connector endpoint filtering is in PREVIEW** as of April 2026. Verify rollout in your tenant before relying on it as a sole Zone 3 control. Reference: [Connector endpoint filtering (Learn)](https://learn.microsoft.com/en-us/power-platform/admin/connector-endpoint-filtering).

1. In the data policy, locate **HTTP with Microsoft Entra ID** in the Business group
2. Open the connector configuration > **Endpoint filtering** (or **Connector configurations** depending on UI revision)
3. Choose **Allow list** (Zone 3 default) or **Block list** (Zone 1–2)
4. Add URL patterns. Example FSI patterns are illustrative — substitute your own approved domains and regulatory data sources
5. Save and allow ~1–2 hours for propagation
6. Document the allowed endpoints in your change-control system (Control 2.1) and obtain dual approval (Power Platform Admin + AI Governance Lead) for Zone 3

### 7d. PAYG implications for non-Microsoft channels

When Copilot Studio agents publish to **non-Microsoft channels** (Direct Line custom, Slack via Direct Line, Telegram, etc.), Microsoft's billing model can route consumption through **Purview pay-as-you-go (PAYG)** for some governance signals (DSPM for AI, content capture). Treat non-Microsoft channels as a higher-risk surface:

- Require named agent owner and dual approval before publishing
- Verify the Azure subscription linked to PAYG billing is in scope of your finance / cost-control process
- Cross-reference Control 1.6 for PAYG-related visibility implications

---

## Step 8 — Verify the rule fired: DLP Alerts and Activity Explorer

A "policy created" screenshot is **not** evidence the rule fires. Generate a known event and assert the row exists.

### 8a. Run a deterministic test

1. Wait the propagation window (≥ 4 hours for the Copilot location)
2. Pick a named test user (M365 Copilot-licensed, in policy scope)
3. At a recorded UTC timestamp, have them issue a known prompt that should match Rule A (e.g., paste a synthetic SSN from a controlled test set) **and** a separate prompt that references a SharePoint file labeled Highly Confidential (Rule B)
4. Capture the policy-tip text the user sees (or absence thereof)

### 8b. Confirm in DLP Alerts

1. Purview portal > **Solutions** > **Data Loss Prevention** > **Alerts**
2. Filter by policy name and the test UTC window
3. Confirm an alert appears with the expected severity, user, and matching rule
4. Capture screenshot (`1.5-07-purview-dlp-conditions.png` series — alert detail view)

### 8c. Confirm in Activity Explorer

1. Purview portal > **Solutions** > **Data Loss Prevention** > **Activity Explorer** (or **Solutions** > **Information Protection** > **Activity explorer** in some tenants)
2. Filter by **Activity** = `DLPRuleMatch` (and related), **User**, and the UTC window
3. Assert event count ≥ 1 with matching policy / rule / user
4. Export to CSV for evidence

> Cross-reference [Control 1.7 portal walkthrough](../1.7/portal-walkthrough.md) for the audit-log retention path that backs this evidence.

---

## Step 9 — Adaptive Protection (optional, IRM-dependent)

Adaptive Protection lets DLP rule strength scale with a user's IRM-derived risk tier (low / moderate / elevated). It is the recommended pattern for risk-tiered enforcement on Zone 2 / Zone 3 populations.

!!! warning "Dependencies and sovereign caveat"
    - Requires **Insider Risk Management** to be onboarded with a completed baseline window before risk tiers populate (see [Control 1.12](../../../controls/pillar-1-security/1.12-insider-risk-detection-and-response.md))
    - Requires the **Insider Risk Management** role group to enable
    - **Not at parity in GCC High / DoD** as of April 2026 — record this in your Zone-3 sovereign-cloud exception register and rely on static label/SIT rules in those clouds

1. Purview portal > **Solutions** > **Insider Risk Management** > **Adaptive Protection** (or **Settings** > **Adaptive Protection**)
2. Enable Adaptive Protection and review the default risk-level definitions
3. In your DLP rules from Step 2, add a condition referencing **User's risk level for adaptive protection** = Elevated / Moderate as appropriate
4. Save and validate behavior in a non-production tenant first

Reference: [Adaptive Protection in Microsoft Purview (Learn)](https://learn.microsoft.com/en-us/purview/insider-risk-management-adaptive-protection).

---

## Step 10 — DSPM for AI navigation cross-check

DSPM for AI surfaces an aggregated view of the DLP policies created above and complements them with discovery, risk assessments, and one-click templates. For full DSPM configuration see [Control 1.6 portal walkthrough](../1.6/portal-walkthrough.md). For Control 1.5 verification, confirm:

1. Purview portal > **Solutions** > **DSPM for AI (classic)** > **Policies**
2. Expand the **Data Loss Prevention** section; confirm the policy created in Step 1 appears with current mode (TestWithNotifications / Enable)
3. **DSPM for AI > Reports**: confirm "Sensitive info detected in prompts and responses" reflects the SITs you configured (allow up to 24 h for first surface, up to 3 days for analytics)
4. **DSPM for AI > Data risk assessments**: schedule or run a custom assessment against the SharePoint sites used by agents in scope; remediate oversharing per Control 1.3 / Control 4.1

> Microsoft is rolling out a unified **DSPM (preview)** experience that consolidates DSPM and DSPM for AI (MC1191257). Verify the current click-path against Microsoft Learn at each portal session — do not commit to specific widget names that may change before GA.

---

## Zone-specific configuration summary

| Zone | Purview DLP (Copilot location) | Power Platform DLP | Sensitivity labels |
|---|---|---|---|
| **Zone 1 (Personal)** | Audit / Test with notifications baseline; SIT rule on customer PII | Block list for known-bad endpoints; minimal connector restrictions | Optional labeling; publish taxonomy |
| **Zone 2 (Team)** | Test with notifications → Enforce after pilot; SIT rule + Confidential label rule | Block HTTP Webhook; classify SharePoint / Custom Website channels Non-Business | Recommended labeling on shared content; quarterly oversharing review |
| **Zone 3 (Enterprise)** | Enforce after propagation + validation; SIT rule (preview) + Highly Confidential label rule (GA); Adaptive Protection where available | Allow-list endpoint filtering on HTTP with Microsoft Entra ID (preview); Block all unauthenticated connectors; Block unapproved channels | Mandatory labeling; auto-labeling on SPO/OneDrive/Exchange; monthly oversharing review |

---

## Roles required per step

| Step | Role(s) |
|---|---|
| 1–3 (Purview DLP) | Purview Compliance Admin (tenant-scoped — **not** a Restricted AU admin) |
| 4 (device onboarding) | Defender for Endpoint admin or Purview Compliance Admin (standalone) |
| 5 (browser coverage) | Endpoint admin (Intune) + Purview Compliance Admin |
| 6 (labels) | Purview Information Protection Admin |
| 7 (Power Platform DLP) | Power Platform Admin |
| 8 (verification) | Purview Compliance Admin (Alerts), reviewer with **Purview Data Security AI Content Viewer** for prompt/response content |
| 9 (Adaptive Protection) | **Insider Risk Management** role group + Purview Compliance Admin |
| 10 (DSPM cross-check) | Per Control 1.6 role table |

---

## Evidence pack

Use a consistent file naming convention:

```
Control-1.5_{TenantId}_{Cloud}_{ArtifactType}_{YYYYMMDD-HHmm-UTC}.{ext}
Control-1.5_{TenantId}_{Cloud}_{ArtifactType}_{YYYYMMDD-HHmm-UTC}.{ext}.sha256
```

| Artifact | Source | Format | Frequency |
|---|---|---|---|
| Custom-template selection screenshot | Purview > DLP > Create policy | PNG | On change |
| Two-rule policy export (`Get-DlpComplianceRule`) | Purview / SCC PowerShell | JSON | On change |
| Test-with-notifications mode evidence | Purview > Policy detail | PNG | On change |
| Deterministic test result (user, prompt, UTC, alert ID) | Tester log + DLP Alerts + Activity Explorer | CSV + log | Weekly (Z3) / Monthly (Z2) |
| Sensitivity label list and published label policies | `Get-Label`, `Get-LabelPolicy` | JSON | On change |
| Auto-labeling policy locations | `Get-AutoSensitivityLabelPolicy` | JSON | On change |
| Power Platform data-policy export (`Get-DlpPolicy`) | PowerApps PowerShell | JSON | On change |
| Endpoint device onboarding inventory | Purview > Device onboarding | CSV | Weekly |
| Browser coverage report (Edge config + extension deployment) | Intune | CSV | Weekly |
| Adaptive Protection threshold + policy snapshot (where in scope) | IRM | JSON | On change |
| Sovereign-cloud exception register (GCC High / DoD parity gaps) | Internal tracker | JSON | Quarterly review |

Store in immutable storage (Purview retention label, SharePoint hold, or WORM blob) aligned to Control 1.7 retention.

---

## Validation checklist

After completing the walkthrough, verify:

1. [ ] The Microsoft 365 Copilot and Copilot Chat DLP policy was created from the **Custom > Custom policy** template (Standard templates do not surface this location)
2. [ ] The policy contains **two distinct rules**: Rule A (SITs) and Rule B (sensitivity labels) — the UI rejects same-rule SIT+label conditions for the Copilot location
3. [ ] The policy is in **Test with notifications** mode and the propagation window (≥ 4 hours) has elapsed before any enforcement decision
4. [ ] The administrator who created the policy is **tenant-scoped**, not a Restricted Administrative Unit-scoped admin (the Copilot location does not support AUs)
5. [ ] Block-by-label scope (SPO + OneDrive + Exchange emails on/after Jan 1 2025; no calendar; citations still appear; uploaded-to-prompt files not scanned) has been communicated to stakeholders
6. [ ] Devices are onboarded for any endpoint rules; coverage gaps are recorded
7. [ ] Edge configuration policy and Purview browser extension are deployed per browser
8. [ ] Sensitivity labels exist **and at least one label policy is published** (`Get-LabelPolicy` returns the expected policy with `Mode = Enable`)
9. [ ] Auto-labeling, where used, is scoped to **SharePoint Online**, **OneDrive for Business**, and **Exchange Online** only (no "AI interactions" location exists)
10. [ ] Power Platform data policies are configured in PPAC and AI-related connectors are classified Business / Non-Business / Blocked; refer to the live PPAC list for inventory
11. [ ] Endpoint filtering for HTTP with Microsoft Entra ID is configured in allow-list mode for Zone 3 (and the **preview** status is recorded)
12. [ ] A deterministic test produced an alert in **DLP Alerts** and a row in **Activity Explorer** within the documented window
13. [ ] If Adaptive Protection is in use: IRM baseline is complete and the GCC High / DoD parity gap is recorded in the sovereign-cloud exception register

---

## Cross-references

- [Control 1.5 PowerShell Setup](powershell-setup.md)
- [Control 1.5 Verification & Testing](verification-testing.md)
- [Control 1.5 Troubleshooting](troubleshooting.md)
- [Control 1.6 Portal Walkthrough — DSPM for AI](../1.6/portal-walkthrough.md)
- [Control 1.7 Audit Logging](../1.7/portal-walkthrough.md) — durable evidence backbone
- [Control 1.12 Insider Risk Detection](../1.12/portal-walkthrough.md) — IRM dependency for Adaptive Protection
- [Control 1.13 Sensitive Information Types](../../../controls/pillar-1-security/1.13-sensitive-information-types-sits-and-pattern-recognition.md)
- [Control 1.4 Advanced Connector Policies](../../../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md)

---

## Authoritative Microsoft Learn references

- [DLP for Microsoft 365 Copilot location](https://learn.microsoft.com/en-us/purview/dlp-microsoft365-copilot-location-learn-about) — Custom-template requirement, same-rule restriction, block-by-label scope
- [Create and deploy data loss prevention policies](https://learn.microsoft.com/en-us/purview/dlp-create-deploy-policy)
- [Sensitivity labels overview](https://learn.microsoft.com/en-us/purview/sensitivity-labels)
- [Apply a sensitivity label automatically](https://learn.microsoft.com/en-us/purview/apply-sensitivity-label-automatically)
- [Adaptive Protection in Microsoft Purview](https://learn.microsoft.com/en-us/purview/insider-risk-management-adaptive-protection)
- [Power Platform DLP overview](https://learn.microsoft.com/en-us/power-platform/admin/wp-data-loss-prevention)
- [Connector endpoint filtering (preview)](https://learn.microsoft.com/en-us/power-platform/admin/connector-endpoint-filtering)
- [Endpoint DLP / device onboarding overview](https://learn.microsoft.com/en-us/purview/device-onboarding-overview)

---

[Back to Control 1.5](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: April 2026 | Version: v1.4 | UI Verification Status: Current*
