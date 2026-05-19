# Portal Walkthrough: Control 1.22 — Information Barriers for AI Agents

**Last Updated:** April 2026
**Portals:** Microsoft Purview portal, Microsoft Teams admin center, SharePoint admin center, Power Platform Admin Center (PPAC)
**Estimated Time:** 6–10 hours active configuration, plus 24–72 hours asynchronous policy application before end-to-end testing

---

## Audience and Scope

This walkthrough is for **M365 administrators** in US financial services who own Microsoft Purview Information Barriers (IB) for an organization that deploys M365 Copilot, declarative agents, and Microsoft Copilot Studio agents. It assumes the firm has already classified its regulated business units (e.g., research, sales-and-trading, investment banking public/private side, municipal advisory, fiduciary) under FINRA 2241/2242, FINRA 3110 (with RN 24-09 for AI supervisory guidance), MSRB G-23/G-37, and SEC §15(g).

Use this playbook when implementing Control 1.22 for a Zone 2 (recommended) or Zone 3 (mandatory) environment. Zone 1 deployments still rely on the IB policies configured here, but the operational responsibility is per-user inheritance rather than admin-managed knowledge-source curation.

> **Sovereign clouds.** The Purview portal URL differs for GCC (`https://purview.microsoft.us`), GCC High (`https://purview.microsoft.us`), and DoD (`https://purview.apps.mil`). Use the matching portal for your tenant. PowerShell `Connect-IPPSSession` requires the `-ConnectionUri` and `-AzureADAuthorizationEndpointUri` parameters in sovereign clouds — see the PowerShell baseline.

---

## Prerequisites

- [ ] **Purview Compliance Admin** role for IB configuration (Entra Global Admin not required and discouraged).
- [ ] **Information Barriers license entitlement** — Microsoft 365 E5, Office 365 E5, Microsoft 365 E5 Compliance, Microsoft 365 E5 Insider Risk Management, or Office 365 Advanced Compliance add-on. Verify before configuring.
- [ ] **HR-of-record attribute sync** populated in Microsoft Entra ID (typically `Department`, `CompanyName`, `Division`) via Workday / SuccessFactors / Oracle HCM connector. Hand-edited attributes are not acceptable evidence for FINRA 3110.
- [ ] **AI Administrator** awareness — agent inventory across M365 Copilot, declarative agents, and Copilot Studio confirmed; Channel Agent inventory pulled from PPAC.
- [ ] **SharePoint Admin** for site-segment assignment and IB-mode site provisioning.
- [ ] **Compliance Officer** identified to own wall-crossing approvals and policy attestation.
- [ ] Change ticket open with reviewers from Compliance, Legal, and Security assigned. Capture pre-change `Get-InformationBarrierMode` and `Get-OrganizationSegment` output as baseline evidence.

> **Read first.** The PowerShell snippets in this walkthrough are abbreviated. Before running them in production, read the [PowerShell Authoring Baseline for FSI Implementations](../../_shared/powershell-baseline.md) for module pinning, sovereign-cloud endpoints, `-WhatIf` patterns, and SHA-256 evidence emission.

---

## Step 1 — Confirm IB Mode (Purview Portal + PowerShell)

1. Open the [Microsoft Purview portal](https://purview.microsoft.com).
2. **Solutions** → **Information barriers**. The landing page displays current mode and segment count.
3. From a Windows PowerShell session connected via `Connect-IPPSSession`, run:

    ```powershell
    Get-InformationBarrierMode
    ```

    Expected return values:

    - `Legacy` — IB v1; ABP-based; required ABP cleanup; **flag for remediation** in any FSI tenant onboarded after August 2023.
    - `SingleSegment` — IB v2 single-segment-per-user; suitable for firms with strictly non-overlapping mandates.
    - `MultiSegment` — IB v2 with up to 10 segments per user; **recommended for FSI** with overlapping mandates (e.g., a banker who is also a Reg BI compliance-officer-of-record, a research analyst loaned to a deal team).

4. If the mode is `Legacy`, plan a maintenance window to migrate. Migration is one-way and requires Compliance + IT change-board approval. Reference: [Microsoft Learn — Use multi-segment support](https://learn.microsoft.com/en-us/purview/information-barriers-multi-segment).

> **Do not change IB mode in production without Compliance Officer sign-off.** Mode changes affect message routing, group creation, and SharePoint site provisioning across the tenant.

---

## Step 2 — Define Organization Segments (Purview Portal)

1. Purview portal → **Information barriers** → **Segments** → **+ New segment**.
2. Name segments using a stable, regulator-recognizable naming convention. Recommended pattern: `IB-<BusinessUnit>-<Side>`:

    | Segment Name | User-attribute filter (example) | Purpose |
    |---|---|---|
    | `IB-Research` | `Department -eq 'Equity Research'` | Equity / debt research analysts (FINRA 2241/2242) |
    | `IB-Trading` | `Department -eq 'Sales and Trading'` | Sales-and-trading personnel (FINRA 5270/5280) |
    | `IB-IB-Public` | `Department -eq 'Investment Banking' -and CompanyName -eq 'Capital Markets'` | Public-side bankers |
    | `IB-IB-Private` | `Department -eq 'Investment Banking' -and CompanyName -eq 'M&A'` | Private-side bankers (MNPI custodians) |
    | `IB-Muni-Underwriting` | `Department -eq 'Municipal Underwriting'` | MSRB G-23 segregation |
    | `IB-Muni-Advisory` | `Department -eq 'Municipal Advisory'` | MSRB G-23 segregation |
    | `IB-Compliance` | `Department -eq 'Compliance'` | Wall-crossing approvers; typically permitted both sides |

3. Use **HR-of-record attributes**. Avoid `extensionAttribute*` unless those attributes are owned by an automated sync.
4. Save each segment. The portal validates filter syntax against current directory data and displays an estimated user count — **review the count** with Compliance before proceeding.

---

## Step 3 — Create Information Barrier Policies (Purview Portal)

> **Multi-Segment mode policies are allow-lists.** Each segment is permitted to communicate **only with** the segments listed. Plan the matrix on paper first.

1. Purview portal → **Information barriers** → **Policies** → **+ Create policy**.
2. For each segment, define which segments it may communicate with. Example matrix for a broker-dealer:

    | Segment | Permitted to communicate with |
    |---|---|
    | `IB-Research` | `IB-Research`, `IB-Compliance` |
    | `IB-Trading` | `IB-Trading`, `IB-Sales`, `IB-Compliance` |
    | `IB-IB-Public` | `IB-IB-Public`, `IB-Sales`, `IB-Compliance` |
    | `IB-IB-Private` | `IB-IB-Private`, `IB-Compliance` |
    | `IB-Muni-Underwriting` | `IB-Muni-Underwriting`, `IB-Compliance` |
    | `IB-Muni-Advisory` | `IB-Muni-Advisory`, `IB-Compliance` |

3. Name each policy after the source segment (`Policy-IB-Research`, `Policy-IB-Trading`, …).
4. Set **Policy status** to **Active**.
5. Save. **Do not yet apply** — apply in Step 5 after coverage validation.

---

## Step 4 — Validate Segment Coverage Before Applying

1. Open the **Segments** page; confirm estimated user counts roll up to the firm's headcount within tolerance (≥99.5% Zone 2; 100% Zone 3 for MNPI-handling personnel).
2. Pull a coverage report via PowerShell to identify segment-less users (see [PowerShell Setup](powershell-setup.md), `Export-IBSegmentCoverage`).
3. Remediate segment-less users **before** applying policies. Users without segments **bypass** IB enforcement and are a residual risk.
4. Capture `Get-OrganizationSegment` and the coverage report as pre-application evidence.

---

## Step 5 — Apply Information Barrier Policies

1. From a connected Compliance PowerShell session:

    ```powershell
    Start-InformationBarrierPoliciesApplication
    ```

2. Application is **asynchronous**. Track status with:

    ```powershell
    Get-InformationBarrierPoliciesApplicationStatus
    ```

3. Plan for **24–72 hours** to reach `Completed` in production tenants. Notify Compliance, the help desk, and Teams/SharePoint admins of the change window.
4. Capture the final `Completed` status and timestamp as evidence in the change ticket.

---

## Step 6 — Align SharePoint Sites with Segment Coverage

1. Open the [SharePoint admin center](https://admin.microsoft.com/sharepoint).
2. **Sites** → **Active sites**. Filter to sites used as agent knowledge sources or storing regulated content.
3. For each in-scope site, open the site's **Settings** → **More settings** → **Information barriers**.
4. Assign a **site segment** corresponding to the owning business unit (e.g., a research SharePoint site → `IB-Research`).
5. Set the site's **IB mode** appropriately:
    - **Explicit** — only members of the assigned segments may access; recommended for MNPI-bearing sites.
    - **OwnerModerated** — owner approves cross-segment additions; suitable for cross-functional projects with documented exception.
    - **Mixed** — only after Compliance review.
6. Validate that Copilot Studio knowledge-source references and Graph connector indexes do not reach across segment boundaries. Graph connectors **do not** segment-trim by default; document any connector index that contains cross-barrier content and apply Control 1.4 (connector DLP) as a compensating control.

---

## Step 7 — Validate Teams Behavior

1. Open the [Teams admin center](https://admin.teams.microsoft.com).
2. Confirm IB enforcement is applied at the policy level (Teams admin center → **Org-wide settings** → **Information barriers**; the page surfaces the active IB mode).
3. Have a tester from `IB-Research` and a tester from `IB-Trading` attempt:
    - 1:1 chat between each other → expected: blocked.
    - Group creation including users from both segments → expected: blocked at creation.
    - M365 Copilot prompt referencing the other segment's known content → expected: not retrieved.
    - Copilot Studio per-user agent invocation → expected: IB-trimmed retrieval.
    - **Channel Agent** posted to a shared channel that includes both segments → expected: **does not** consistently enforce per-invoker IB; document as residual risk and apply Compensating Controls per the control doc.

---

## Step 8 — Configure Wall-Crossing Workflow

Wall-crossing is the controlled, time-boxed exception process. Implement it in your existing GRC platform (ServiceNow GRC, Archer, OneTrust, or a Power Platform solution governed by Control 2.1 Managed Environments):

1. **Request form** captures: requesting user, source segment, target segment, deal/project code, business justification, requested duration, expected closeout date.
2. **Approval routing**: Compliance Officer → Legal → Source-segment Business-Unit Head → Target-segment Business-Unit Head.
3. **Provisioning**: Approved request triggers a temporary segment reassignment or temporary group membership; the IB policy must be re-applied (`Start-InformationBarrierPoliciesApplication`) for the change to take effect — schedule accordingly.
4. **Closeout**: On expiration, automation reverts the segment assignment, notifies the user, and writes a closeout record.
5. **Retention**: Wall-crossing records — request, approvals, provisioning evidence, closeout — retained **6+ years** per SEC 17a-4(b) and FINRA 4511(b).

---

## Step 9 — Review Channel Agent Inventory (PPAC)

1. Open the [Power Platform Admin Center](https://admin.powerplatform.microsoft.com).
2. **Copilot agents** → filter to agents deployed via **Teams channel** publishing.
3. For every Channel Agent in scope, confirm:
    - The hosting Teams channel does **not** span barrier-protected segments.
    - The agent's knowledge sources contain no cross-barrier content.
    - Connector / DLP scoping (Control 1.4) restricts cross-segment data flow.
4. Channel Agents that fail any check are flagged for remediation: re-publish as a per-user Teams app, restrict the channel membership, or retire the agent. Zone 3 environments **prohibit** Channel Agents in mixed-segment channels.

---

## Configuration by Governance Level

| Setting | Zone 1 (Personal) | Zone 2 (Team) | Zone 3 (Enterprise) |
|---|---|---|---|
| **IB mode** | `MultiSegment` recommended | `MultiSegment` required | `MultiSegment` required |
| **Segment coverage** | Best-effort (≥95%) | ≥99.5% | 100% of MNPI-handling personnel |
| **SharePoint site segments** | Inherited from user | Required for agent knowledge-source sites | Required for all regulated-content sites |
| **Wall-crossing** | Documented in standard help-desk ticket | Compliance approval required | Compliance + Legal + BU-head; hard expiration |
| **Channel Agents in mixed-segment channels** | Discouraged | Restricted to non-protected content only | Prohibited |
| **Monitoring** | Periodic audit | Weekly audit | Real-time Defender XDR / Sentinel detection |
| **Retention of wall-crossing evidence** | 1 year minimum | 6 years | 6+ years; legal hold-aware |

---

## Validation

After completing Steps 1–9, verify:

- [ ] `Get-InformationBarrierMode` returns the intended mode.
- [ ] `Get-OrganizationSegment` lists all designed segments with non-zero estimated users.
- [ ] `Get-InformationBarrierPolicy | Where-Object State -eq Active` matches the design matrix.
- [ ] `Get-InformationBarrierPoliciesApplicationStatus` shows `Completed`.
- [ ] Segment coverage report shows ≥99.5% (Zone 2) or 100% (Zone 3 for MNPI population).
- [ ] End-to-end retrieval test (research user vs. trading canary document) returns no cross-segment content via M365 Copilot, declarative agent, and Copilot Studio per-user agent.
- [ ] Channel Agent inventory reviewed; no agents in mixed-segment channels (Zone 3).
- [ ] Wall-crossing workflow tested end-to-end with a synthetic request.

---

[Back to Control 1.22](../../../controls/pillar-1-security/1.22-information-barriers.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
