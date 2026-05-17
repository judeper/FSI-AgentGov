# Portal Walkthrough — Control 2.25: Microsoft Agent 365 Admin Center Governance Console

!!! danger "READ FIRST — Scope and Sibling Routing"
    **This playbook configures the Microsoft Agent 365 Admin Center governance console** — the unified control plane for agent lifecycle management, publication and activation approval workflows, governance template enforcement, ownerless-agent remediation, and operational monitoring. It walks you through the **Microsoft 365 admin center**, the **Agent 365** blades (Overview, Agent Registry, Pending Requests, Governance Templates, Analytics), and the **Integrated Apps > Agents > Researcher** surface required to satisfy Verification Criteria 1–8 of [Control 2.25](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md).

    **This walkthrough IS for:**

    | In Scope | Surface | Outcome |
    |---|---|---|
    | Validating Agent 365 licensing (E7 Frontier Suite or standalone Agent 365) | M365 admin center → Billing → Licenses | Confirmed entitlement before any governance change |
    | Daily/weekly governance card rhythm (Pending Requests, Ownerless Agents) | M365 admin center → Agent 365 → Overview | Documented review cadence and SLA adherence |
    | Filtering, inspecting, and exporting the Agent Registry | Agent 365 → Agents → All Agents | Audit-ready CSV/Excel inventory snapshots |
    | Admin-gated publishing approval workflow with template application | Agent 365 → Pending Requests → Publishing | Zero unreviewed Zone 2 / Zone 3 publications |
    | Admin-gated activation approval workflow | Agent 365 → Pending Requests → Activation | Phased rollout control evidence |
    | Lifecycle actions — Deploy, Pin, Block, Remove, Delete, Approve Updates | Agent 365 → Agents → \[Agent\] → Manage | Documented lifecycle decisions with admin attribution |
    | Default and Custom Governance Template configuration | Agent 365 → Governance → Templates | Zone-appropriate policy bundles applied at publish/activate time |
    | Researcher with Computer Use access scoping | M365 admin center → Integrated Apps → Agents → Researcher → Computer Use | Affirmative restrictive decision per zone, recorded |
    | Agent Analytics navigation for capacity and risk planning | Agent 365 → Analytics | Trend evidence for the firm's AI risk register |
    | Inventory Export for examiner submission and 6-year WORM retention | Agent 365 → Agents → All Agents → Export | ISO 8601-named monthly snapshots in compliance archive |

    **This walkthrough is NOT for:**

    | Out of Scope | Use Instead |
    |---|---|
    | Discovery, classification, or first-time inventory of agents at the tenant level | [Control 1.2 — Agent Registry and Integrated Apps Management](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md) |
    | Identity governance for autonomous agent identities (sponsor, access packages, lifecycle workflows) | [Control 2.26 — Entra Agent ID Identity Governance](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md) |
    | Detecting and remediating fully orphaned agents (sponsor departed) | [Control 3.6 — Orphaned Agent Detection and Remediation](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) |
    | Change management approval records and release planning | [Control 2.3 — Change Management and Release Planning](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md) |
    | Segregation of duties between authoring, approving, and operating roles | [Control 2.8 — Access Control and Segregation of Duties](../../../controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md) |
    | DLP / sensitivity-label enforcement on agent outputs and grounding data | Pillar 2 data-protection controls (2.4–2.10) |
    | PowerShell / Microsoft Graph automation for the same surfaces | [`./powershell-setup.md`](./powershell-setup.md) |
    | Test cases, sample queries, and evidence collection scripts | [`./verification-testing.md`](./verification-testing.md) |
    | Common errors, missing blades, console behavior anomalies, and remediation steps | [`./troubleshooting.md`](./troubleshooting.md) |

!!! warning "Hedged-Language Reminder"
    This playbook helps your organization **support compliance with** FINRA Rule 3110 (Supervision), FINRA Rule 4511 (Books and Records), FINRA Regulatory Notice 25-07 (AI Tools), SEC Rules 17a-3 / 17a-4 (Recordkeeping), SOX Sections 302/404 (Internal Controls), GLBA 501(b) (Safeguards Rule), OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12) (Technology Risk Management), and NYDFS 23 NYCRR 500 (Cybersecurity). It does **not** by itself guarantee any regulatory outcome and **does not substitute for** the firm's obligation to assign an appropriately registered principal where Rule 3110 requires registered supervisory responsibility. Implementation requires Agent 365 licensing (Microsoft 365 E7 "Frontier Suite" or standalone Agent 365 layered on Microsoft 365 Copilot), validated change-control procedures, and independent testing by your compliance function. Organizations should verify all configurations against their own examination workpapers and legal counsel before treating these procedures as adequate evidence.

!!! info "Generally Available — May 1, 2026"
    Microsoft Agent 365 reached **general availability on May 1, 2026**. Licensing options:

    | Option | Composition | Notes |
    |---|---|---|
    | Microsoft 365 E7 ("Frontier Suite") | E5 + Microsoft 365 Copilot + Microsoft Entra Suite + Agent 365 | Bundled SKU; covers OBO agents under user license |
    | Standalone Microsoft Agent 365 | Per-user license layered on a Microsoft 365 Copilot prerequisite | OBO agents covered by user license; autonomous agent identities still in preview at GA |

    Tenants that did not participate in the pre-GA Frontier feature program can adopt Agent 365 directly at GA without prior enrollment. Microsoft now documents a tenant-enablement prerequisite: at least one user must be assigned a qualifying Microsoft Agent 365 license before Agent 365 can be enabled. See [Agent 365 overview](https://learn.microsoft.com/en-us/microsoft-agent-365/overview) for current SKU and entitlement guidance. Configuration steps in this playbook were verified against the pre-GA Frontier experience in March 2026, refreshed for the GA release in April 2026, and updated for the May 2026 Learn prerequisite clarification — re-verify portal navigation periodically as 2026 Wave 1 and Wave 2 release cycles are expected to evolve naming, entry points, and the Default Governance Template policy composition.

!!! warning "Sovereign Cloud Availability — GCC, GCC High, DoD"
    As of GA (May 1, 2026), Microsoft has **not announced parity availability for the Agent 365 Admin Center, governance templates, or admin-gated publish/activate workflows in GCC, GCC High, or DoD**. Underlying Copilot agents (Researcher, Analyst) are rolling into US Gov clouds on a separate, lagging schedule, and no public Microsoft roadmap item names "Agent 365 admin center governance console" parity for sovereign clouds. **If your tenant URL ends in `admin.microsoft.us` or you authenticate against `login.microsoftonline.us`, stop here and jump to [§1 — Sovereign Cloud Variant](#1-sovereign-cloud-variant-and-compensating-controls).**

    | Cloud | Agent 365 Admin Center | Governance Templates | Substitute approach |
    |---|---|---|---|
    | M365 Commercial | ✅ GA (May 1, 2026) | ✅ GA | Follow this playbook end-to-end |
    | GCC | ❌ Not announced | ❌ Not announced | §1 manual quarterly attestation + Control 1.2 + Control 2.3 + Control 2.8 |
    | GCC High | ❌ Not announced | ❌ Not announced | §1 manual quarterly attestation + Control 1.2 + Control 2.3 + Control 2.8 |
    | DoD | ❌ Not announced | ❌ Not announced | §1 manual quarterly attestation + Control 1.2 + Control 2.3 + Control 2.8 |

    See [`../../_shared/powershell-baseline.md#3-sovereign-cloud-endpoints-gcc-gcc-high-dod`](../../_shared/powershell-baseline.md#3-sovereign-cloud-endpoints-gcc-gcc-high-dod) for sovereign endpoint resolution if you ever need to script against the commercial-only surface from a sovereign management workstation.

!!! tip "Portal Navigation May Shift Post-GA"
    Microsoft is expected to refine Agent 365 navigation through 2026 Wave 1 and Wave 2 release cycles. If a blade name in this playbook does not match what you see, search the admin center for the underlying noun ("Agent 365", "Pending Requests", "Governance Templates", "Researcher") and consult [Microsoft Learn — Microsoft Agent 365](https://learn.microsoft.com/en-us/microsoft-agent-365/overview). Screenshot anchors in this playbook record the navigation that was verified at the **Last UI Verified** date in the [Control 2.25](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md) header (May 2026, post-GA prerequisite refresh).

---

## Document Map

| § | Section | Verification Criterion Evidenced |
|---|---|---|
| 0 | [Pre-flight Prerequisites and Triage](#0-pre-flight-prerequisites-and-triage) | All — gating checks |
| 1 | [Sovereign Cloud Variant and Compensating Controls](#1-sovereign-cloud-variant-and-compensating-controls) | All (substitute path) |
| 2 | [Initial Console Access and Role Validation](#2-initial-console-access-and-role-validation) | VC-1 |
| 3 | [Overview Dashboard Tour and Governance Card Rhythm](#3-overview-dashboard-tour-and-governance-card-rhythm) | VC-1, VC-2 |
| 4 | [Agent Registry — Filtering, Inspection, and Export](#4-agent-registry-filtering-inspection-and-export) | VC-3, VC-7 |
| 5 | [Publishing Approval Workflow](#5-publishing-approval-workflow) | VC-2, VC-4 |
| 6 | [Activation Approval Workflow](#6-activation-approval-workflow) | VC-2, VC-4 |
| 7 | [Lifecycle Actions — Deploy, Pin, Block, Remove, Delete](#7-lifecycle-actions-deploy-pin-block-remove-delete) | VC-5 |
| 8 | [Approve Updates — Version-Pinning Workflow](#8-approve-updates-version-pinning-workflow) | VC-5 |
| 9 | [Governance Templates — Default and Custom](#9-governance-templates-default-and-custom) | VC-4 |
| 10 | [Researcher with Computer Use Configuration](#10-researcher-with-computer-use-configuration) | VC-6 |
| 11 | [Agent Analytics Navigation](#11-agent-analytics-navigation) | VC-7 |
| 12 | [Inventory Export and Retention](#12-inventory-export-and-retention) | VC-7, VC-8 |
| 13 | [Examiner Evidence Collection Patterns](#13-examiner-evidence-collection-patterns) | VC-8 |
| 14 | [Closing Decision Matrix — Portal vs PowerShell vs Graph](#14-closing-decision-matrix-portal-vs-powershell-vs-graph) | Operational reference |

---

## 0. Pre-flight Prerequisites and Triage

Before you click anything in any portal, run through this gate. Skipping a gate produces silent failures later — for example, the **Agent 365** node will not appear in the M365 admin center if no user has a qualifying Agent 365 entitlement assigned, and the wrong role will let you read the registry but not approve a publishing request.

### 0.1 Confirm tenant cloud and tenant ID

1. Sign in to [`https://admin.microsoft.com`](https://admin.microsoft.com) as an account that holds at least **Entra Global Reader** (read-only) — escalate to **AI Administrator** or **Entra Global Admin** only when about to make a configuration change.
2. In the upper-right corner, click your profile photo → **Switch directory** if you are a multi-tenant operator. Confirm you are in the tenant you intend to govern.
3. Navigate to the M365 admin center home, then to **Settings → Org settings → Organization profile**. Capture the **Tenant ID** GUID and the **Primary domain** (for example, `contoso.onmicrosoft.com`). Record both in your runbook.
4. Confirm **Country or region** matches the regulated entity. For US broker-dealers and banks this is typically `United States`.

*Screenshot anchor: docs/images/2.25/EXPECTED.md#0-1-tenant-overview — M365 admin Organization profile blade showing Tenant ID, Primary domain, and Country.*

!!! warning "Tenant Cloud Detection"
    If the URL bar shows `admin.microsoft.us` (GCC High / DoD) or you authenticate against `login.microsoftonline.us`, **stop here and jump to [§1](#1-sovereign-cloud-variant-and-compensating-controls)**. Continuing this playbook in a sovereign tenant will fail at §2 because the Agent 365 admin center has no announced parity in `*.us` clouds as of GA (May 1, 2026).

### 0.2 Confirm role assignments

Use the canonical role names from [`docs/reference/role-catalog.md`](../../../reference/role-catalog.md). The Agent 365 admin surface honors a small set of roles at GA — Microsoft has stated that fine-grained or read-only Agent 365-specific roles are not planned for the GA wave. Plan governance workflows accordingly and apply Microsoft Entra Privileged Identity Management (PIM) to **Entra Global Admin**.

| Role | Required for | Where to assign |
|---|---|---|
| **Entra Global Admin** | Tenant enrollment, licensing, and emergency lifecycle actions; first-time governance template authoring. **Activate via PIM** for the duration of the change window only. | Entra → Roles & admins |
| **AI Administrator** | Day-to-day approval, registry, deployment, blocking, and template-application tasks. This is the daily operator role. | Entra → Roles & admins → search "AI Administrator" |
| **Entra Global Reader** | Evidence-only access for auditors, examiners, and the Compliance Officer collecting screenshots without change rights. | Entra → Roles & admins |
| **Purview Compliance Admin** | Cross-reference for retention labels and Purview Audit / AI Compliance Assessment policies surfaced inside Default and Custom Governance Templates. | Purview → Roles & scopes |
| **Power Platform Admin** | Cross-reference where a published agent originates from Copilot Studio and overlaps with environment-level governance (Pillar 2 controls 2.10–2.16). | Power Platform admin center → Settings |

1. In Entra, navigate to **Identity → Roles & admins → Roles**.
2. Search for each role above and click into it. Confirm at minimum **two named human accounts** (no service principals, no break-glass) hold each operating role per FINRA dual-control expectations.
3. If any role shows zero or one assignee, open a ticket with your Entra owner before proceeding — single-person admin coverage on identity governance roles is itself an audit finding under FINRA Rule 3110 supervisory review.

*Screenshot anchor: docs/images/2.25/EXPECTED.md#0-2-role-assignments — Roles & admins grid filtered to "AI Administrator" and "Global Administrator" (PIM-eligible).*

!!! example "Examiner Evidence Box — Role Coverage"
    | Element | Value |
    |---|---|
    | Artifact produced | CSV export of `directoryRole` membership for AI Administrator, Entra Global Admin (PIM-eligible), Entra Global Reader, Purview Compliance Admin, Power Platform Admin |
    | Retention duration | 6 years (SEC 17a-4 / FINRA 4511) |
    | Regulatory mapping | FINRA 3110 (supervision — dual control), SOX §404 (segregation of duties), NYDFS 23 NYCRR 500 (access governance) |

### 0.3 Confirm Agent 365 licensing

1. Open [`https://admin.microsoft.com`](https://admin.microsoft.com) → **Billing → Licenses**.
2. Confirm at least one named user who will sponsor or own agents is assigned one of the following qualifying entitlements:
   - **Microsoft 365 E7** ("Frontier Suite") — bundles E5 + Microsoft 365 Copilot + Microsoft Entra Suite + Agent 365.
   - **Microsoft Agent 365** standalone — per-user license layered on a Microsoft 365 Copilot prerequisite.
3. If the standalone Agent 365 SKU is used, confirm the count of **Microsoft 365 Copilot** licenses is greater than zero (required as the base prerequisite).
4. Click into **Licenses → Microsoft Agent 365** (or the E7 SKU) and confirm at least one active user assignment is present. Capture the assigned-vs-available counts and record both in your runbook.
5. Confirm OBO scope: agents acting **on behalf of** a licensed user are covered under that user's license. Autonomous agent identities with their own mailboxes and broad permissions remain in preview at GA and are out of scope for this control.

*Screenshot anchor: docs/images/2.25/EXPECTED.md#0-3-licenses — Billing → Licenses page showing Agent 365 / E7 SKU and Microsoft 365 Copilot SKU counts.*

!!! warning "Autonomous Agent Identities Are Preview at GA"
    Autonomous agent identities — agent service principals with their own mailboxes, broad delegated permissions, and no human "on behalf of" attribution — are **not in scope** for Agent 365 at GA. Do not attempt to govern those identities through the Agent 365 console; route them to [Control 2.26 — Entra Agent ID Identity Governance](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md) and apply the sponsor / access-package model. Mixing the two governance surfaces during the preview-to-GA window creates supervisory chain ambiguity that examiners will flag.

### 0.4 Confirm the Agent 365 navigation node is present

1. Return to [`https://admin.microsoft.com`](https://admin.microsoft.com).
2. In the left navigation, look for **Agent 365** (typically grouped under **Copilot** or as a top-level node depending on tenant rollout state). If it is not visible, click **Show all** at the bottom of the left navigation.
3. If **Agent 365** still does not appear after at least one qualifying user assignment, allow up to 24 hours for entitlement propagation, then re-verify. If still missing after 24 hours, open a ticket via the M365 admin center **Help & support** widget and reference Agent 365 GA (May 1, 2026).

*Screenshot anchor: docs/images/2.25/EXPECTED.md#0-4-agent365-node — Left navigation showing Agent 365 node expanded with Overview, Agents, Pending Requests, Governance, Analytics children.*

### 0.5 Pre-flight gate summary

Do not proceed past this section unless **all** of the following are true:

- [ ] You are signed in to the correct tenant and have captured the tenant ID.
- [ ] Tenant is in M365 Commercial cloud (or you have switched to §1 sovereign path).
- [ ] At least two named humans hold each governance role in §0.2.
- [ ] **Entra Global Admin** is assigned via PIM (eligible, not active by default).
- [ ] At least one named user who will sponsor or own agents has Microsoft 365 E7 or standalone Agent 365 assigned.
- [ ] Microsoft 365 Copilot licenses are assigned where standalone Agent 365 is used.
- [ ] The **Agent 365** node is visible in the left navigation of the M365 admin center.
- [ ] Your governance runbook records the firm's documented SLAs for Pending Requests review (illustrative defaults: weekly Zone 2, daily Zone 3 — examiners will hold the firm to its own documented SLA, not these defaults).

!!! tip "If a Gate Fails"
    Open [`./troubleshooting.md`](./troubleshooting.md) and search for the gate name (for example, "Agent 365 node missing" or "License propagation pending"). Do not attempt workarounds in production until the gate clears — most workarounds for missing licensing or roles create their own audit findings under FINRA 3110 and SOX 404.

---

## 1. Sovereign Cloud Variant and Compensating Controls

**Audience:** Operators in M365 GCC, GCC High, or DoD tenants. Skip this section if you are in M365 Commercial.

As of GA (May 1, 2026), **the Microsoft Agent 365 Admin Center is not announced for any US sovereign cloud**. Microsoft has not committed to a sovereign GA timeline. Until parity arrives, sovereign-cloud organizations cannot rely on the admin-gated publish/activate workflow, governance template engine, or Pending Requests / Ownerless Agents governance cards described in §3–§13. Examiners (FINRA 3110, OCC Heightened Standards, FFIEC IT Handbook, NYDFS 23 NYCRR 500) will still expect equivalent governance evidence. The substitute is a **manual quarterly attestation pattern** anchored on the agent registry from [Control 1.2](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md), enforced through the firm's change-management workflow ([Control 2.3](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md)) and segregation-of-duties controls ([Control 2.8](../../../controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md)).

If Agent 365 ships in your sovereign cloud after this playbook's verification date, **do not silently switch over**. Treat parity arrival as a controlled change: dual-run the §3–§13 portal procedure alongside the §1 manual procedure for at least one full quarter, reconcile the two sources, obtain compliance officer sign-off, and document the cutover per [Control 2.3](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md) before retiring the manual attestation.

### 1.1 Sovereign substitute — agent registry as the system of record

1. Confirm the firm maintains a Control 1.2 Agent Registry CSV (or equivalent SharePoint list) containing at minimum: `agent_id`, `agent_display_name`, `publisher`, `platform`, `zone`, `owner_upn`, `owner_manager_upn`, `governance_template_documented`, `last_attested_date`, `last_change_approval_id`. If any of those columns is missing, treat the registry as non-compliant and remediate before proceeding.
2. Apply a Microsoft Purview retention label of **6 years** with **WORM (records management) enforcement** to the registry storage location (SharePoint document library or Dataverse table). FINRA 4511 and SEC 17a-4 expect immutability for the retention horizon.
3. Designate a named human owner — typically the **AI Governance Lead** — accountable for the registry. Backup ownership goes to the **Information Security Officer**.

*Screenshot anchor: docs/images/2.25/EXPECTED.md#1-1-sovereign-registry — SharePoint list view of the Control 1.2 agent registry with the 6-year retention label applied and column set visible.*

### 1.2 Manual quarterly attestation

1. On the first business day of each calendar quarter, the **AI Governance Lead** exports the agent registry to CSV and distributes it via a Purview-labeled (Confidential / Internal) attestation workbook to each named **Agent Owner**.
2. Each Agent Owner confirms in writing (Microsoft Forms response, signed PDF, or Power Automate approval task) that:
   - They still own the agent and remain accountable for its operation.
   - The agent's listed permissions, data connections, and grounding sources remain necessary and proportionate.
   - The agent is operating within the documented zone (Zone 1 / 2 / 3) and no scope expansion has occurred without a Control 2.3 change approval.
   - No undisclosed third-party agents are operating under their sponsorship.
3. The **Compliance Officer** archives signed attestations to the Purview-immutable location alongside the registry snapshot. Use ISO 8601 file naming: `agent-registry-attestation-YYYY-QN.csv` and `agent-attestation-responses-YYYY-QN.zip`.
4. Any agent without a returned attestation within **14 calendar days** of the campaign deadline is treated as **orphaned** and routed through [Control 3.6 — Orphaned Agent Detection and Remediation](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) for disable-or-delete. Document the disable action in the change-management system.

*Screenshot anchor: docs/images/2.25/EXPECTED.md#1-2-attestation-workbook — sample Microsoft Forms attestation response page and the resulting Power Automate approval audit trail.*

!!! example "Examiner Evidence Box — Sovereign Manual Attestation"
    | Element | Value |
    |---|---|
    | Artifact produced | Quarterly attestation CSV, signed Agent Owner responses, non-response remediation log, change-management ticket IDs for any disable actions |
    | Retention duration | 6 years on Purview record label (WORM) |
    | Regulatory mapping | FINRA 3110 (supervision), FINRA 4511 (books and records), SEC 17a-3/17a-4 (recordkeeping), OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12) (technology risk), FFIEC IT Handbook (governance), NYDFS 23 NYCRR 500 (cybersecurity governance) |

### 1.3 Compensating control mapping

| Commercial-only Agent 365 surface | Sovereign substitute | Residual risk |
|---|---|---|
| Agent 365 admin-gated publish workflow | Control 2.3 change-management approval before manual deployment by **Power Platform Admin** or equivalent platform admin | Manual workflow drift; reviewer fatigue |
| Agent 365 admin-gated activation workflow | Control 2.8 segregation of duties — distinct **Change Management Lead** approval before the **Power Platform Admin** activates | Latency; possible weekend gaps in coverage |
| Default Governance Template auto-application | Documented zone-mapped policy bundle in the Agent Registry; manual application of equivalent Entra Identity Protection, SharePoint access, and Purview Audit / AI Compliance Assessment policies | Manual data drift between platform configuration and registry record |
| Pending Requests governance card | Weekly (Zone 2) / daily (Zone 3) review meeting — captured in a recurring Outlook calendar invite with the agenda and decisions logged in the change-management system | No native oldest-pending sort; manual queue management |
| Ownerless Agents governance card | Quarterly attestation non-response report (§1.2 step 4) | Detection latency up to 14 days |
| Inventory Export | Manual CSV export of the agent registry with ISO 8601 filename | Same retention obligations apply |
| Researcher with Computer Use admin scoping | If Computer Use is unavailable in your sovereign cloud, document the absence; if available, configure it via the M365 admin center → Integrated Apps surface and apply Zone 3 restrictions identically | Verify sovereign availability per Microsoft 365 Government roadmap |

### 1.4 Sovereign roadmap monitoring cadence

1. The **Technology Risk Manager** re-verifies the sovereign roadmap **quarterly** via:
   - [Microsoft 365 Government roadmap](https://aka.ms/m365gov-roadmap)
   - [Microsoft Agent 365 overview](https://learn.microsoft.com/en-us/microsoft-agent-365/overview)
   - The firm's Microsoft FastTrack contact (where applicable)
2. Status changes are reported to the AI Governance Council and recorded in the firm's AI risk register.
3. Disclose the absence of native technical enforcement in the firm's Written Supervisory Procedures so FINRA, OCC, or NYDFS examiners are not surprised by the substitute pattern.

**End of sovereign substitute path. Sections §2–§13 below assume an M365 Commercial tenant.**

---

## 2. Initial Console Access and Role Validation

**Verification Criterion evidenced:** VC-1 (Agent 365 admin center is accessible and the operating roles are correctly assigned and least-privileged).

### 2.1 Activate Entra Global Admin via PIM (only when needed)

The **Entra Global Admin** role is required for tenant enrollment, licensing changes, first-time governance template authoring, and emergency lifecycle actions (such as bulk Block or Delete during an incident). For routine governance work, you should be operating as **AI Administrator**.

1. Sign in to [`https://entra.microsoft.com`](https://entra.microsoft.com) as your daily-use account.
2. Navigate to **Identity governance → Privileged Identity Management → My roles**.
3. Locate **Global Administrator** in the **Eligible assignments** tab.
4. Click **Activate**, set the activation duration to the **shortest interval consistent with the change window** (typically 1–4 hours), and provide a business justification that names the change-management ticket ID per [Control 2.3](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md).
5. Complete any MFA challenge. PIM activation events are logged to the Entra audit log with the justification text and ticket ID — examiners may request these logs as evidence of just-in-time elevation.

*Screenshot anchor: docs/images/2.25/EXPECTED.md#2-1-pim-activation — PIM My roles blade showing Global Administrator eligible and the activation form with justification field populated.*

!!! warning "Do Not Operate Daily as Entra Global Admin"
    Daily operations as Entra Global Admin breaks the segregation-of-duties expectations of [Control 2.8](../../../controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md) and creates an audit finding under FINRA 3110 and SOX §404. Use **AI Administrator** for the §3–§13 procedures below; activate Entra Global Admin only for the discrete tasks that explicitly require it.

### 2.2 Sign in to the M365 admin center as AI Administrator

1. Sign in to [`https://admin.microsoft.com`](https://admin.microsoft.com) as your **AI Administrator** account.
2. Confirm the upper-right user chip shows the AI Administrator account, not your Entra Global Admin account.
3. In the left navigation, expand **Copilot** (or locate the top-level **Agent 365** node depending on tenant rollout) and click **Agent 365 → Overview**.
4. Capture the URL — typically `https://admin.microsoft.com/Adminportal/Home#/agent365/overview` or the GA equivalent — and record it in your runbook.

*Screenshot anchor: docs/images/2.25/EXPECTED.md#2-2-agent365-overview-landing — Agent 365 Overview landing page with the AI Administrator persona visible in the upper-right user chip.*

### 2.3 Validate read-only access for the Compliance Officer

1. Have the **Compliance Officer** sign in to the same URL using their **Entra Global Reader** account.
2. Confirm they see the Overview, Agents, Pending Requests, Governance, and Analytics blades **but cannot perform any approve/deploy/block/delete action** — write controls should be greyed out or absent.
3. Document the read-only verification in the role-coverage evidence pack (§0.2 examiner evidence box).

!!! example "Examiner Evidence Box — Console Access Validation"
    | Element | Value |
    |---|---|
    | Artifact produced | Screenshots of Agent 365 Overview as AI Administrator (write-capable) and as Entra Global Reader (read-only); PIM activation log entry for any Entra Global Admin activation in the prior 30 days |
    | Retention duration | 6 years (SEC 17a-4 / FINRA 4511) |
    | Regulatory mapping | FINRA 3110 (supervision), SOX §404 (segregation of duties), NYDFS 23 NYCRR 500 (access governance) |

---

## 3. Overview Dashboard Tour and Governance Card Rhythm

**Verification Criteria evidenced:** VC-1 (Agent 365 admin center is configured and accessible), VC-2 (governance cards are reviewed on a documented cadence with named owners).

The Agent 365 Overview dashboard is the daily entry point for governance staff. It surfaces five hero metrics, two persistent governance cards, and one trend chart. The Overview is read-only — it drives the AI Administrator's queue but the lifecycle actions themselves happen on the Agent Registry and Pending Requests blades.

### 3.1 Hero metrics panel

1. From **Agent 365 → Overview**, scroll to the top of the page. You should see five tiles in this order (subject to change in 2026 Wave 1):

   | Tile | Description | Governance signal |
   |---|---|---|
   | **Agent Registry count** | Total agents discovered in the tenant across all publishers and platforms | Sudden increase suggests bulk import or shadow-AI activity |
   | **Active Users (30d)** | Distinct users who interacted with at least one agent in the last 30 days | Adoption trend; capacity planning input |
   | **Total Sessions (30d)** | Sum of agent invocation sessions in the last 30 days | Volumetric trend; correlate with Exception Rate |
   | **Exception Rate (30d)** | Percentage of sessions that did **not** complete successfully | Configure manual or scripted threshold (illustrative default ≥5% triggers escalation; firms must set and document their own threshold) |
   | **Agent Runtime (30d)** | Aggregate compute/processing time across all agents | Cost-control and capacity input |

2. Capture a monthly screenshot of the hero metrics panel for the firm's AI risk register and the operational evidence pack.
3. Document the firm's Exception Rate threshold in the AI governance policy and the incident response runbook. Reference [Control 2.3](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md) for change-management notification when the threshold is breached.

*Screenshot anchor: docs/images/2.25/EXPECTED.md#3-1-hero-metrics — Agent 365 Overview top-of-page tile row with the five hero metrics labeled.*

### 3.2 Pending Requests governance card

1. Scroll to the **Pending Requests** card on the Overview page.
2. Confirm the card shows the count of pending publish and activate requests, sorted oldest-first, with a week-over-week delta badge (▲ / ▼).
3. The **AI Administrator** reviews this card on the firm's documented cadence:
   - **Zone 2 (illustrative default):** weekly governance session, 5-business-day SLA on individual requests.
   - **Zone 3 (illustrative default):** daily review, 2-business-day SLA on individual requests.
   - **Examiners will hold the firm to its own documented SLA, not these illustrative defaults.** Document the chosen cadence and SLA in the AI governance policy and the firm's Written Supervisory Procedures.
4. Click **View all** on the card to navigate to **Agent 365 → Pending Requests**, where the full list is filterable by zone, requester, agent platform, and submission date. The publishing approval workflow itself is detailed in §5; activation in §6.
5. Record the count, the oldest-pending age, and any SLA breaches in the weekly governance session minutes. SLA breaches should be escalated to the **AI Governance Lead** and recorded against [Control 2.3](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md).

*Screenshot anchor: docs/images/2.25/EXPECTED.md#3-2-pending-requests-card — Pending Requests governance card showing oldest-pending age and the week-over-week delta badge.*

!!! warning "Stale Pending Requests Are an Audit Finding"
    A pending request older than the firm's documented SLA is itself evidence that the supervisory chain required by FINRA Rule 3110 has degraded. Examiners reviewing the inventory export and the Pending Requests card history will compare oldest-pending dates against the WSP-documented SLA. Do not let the queue age past the documented threshold without an escalation note in the change-management system.

### 3.3 Ownerless Agents governance card

1. Scroll to the **Ownerless Agents** card on the Overview page.
2. Confirm the card shows the count of agents whose **Owner UPN** field is blank, points to a disabled Entra account, or points to a user whose `employeeLeaveDateTime` has passed.
3. Use the inline **Assign Owner** action to assign a named, accountable owner before the next governance cycle closes.
4. If a fully orphaned agent (no candidate owner identifiable) is detected, route it through [Control 3.6 — Orphaned Agent Detection and Remediation](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) for the disable-or-delete decision. Do not leave an ownerless agent active across a governance cycle.

*Screenshot anchor: docs/images/2.25/EXPECTED.md#3-3-ownerless-card — Ownerless Agents governance card with the inline Assign Owner action visible on a row.*

!!! example "Examiner Evidence Box — Governance Card Rhythm"
    | Element | Value |
    |---|---|
    | Artifact produced | Weekly (Zone 2) / daily (Zone 3) governance session minutes; Pending Requests aging report; Ownerless Agents remediation log |
    | Retention duration | 6 years (SEC 17a-4 / FINRA 4511) on Purview record label |
    | Regulatory mapping | FINRA 3110 (supervision), FINRA Regulatory Notice 25-07 (AI tools governance), SOX §404 (control operation) |

### 3.4 Agent Runtime trend chart

1. Below the governance cards, locate the **Agent Runtime trend** chart (typically a 90-day line chart of aggregate runtime).
2. Use this chart for capacity planning input, cost forecasting, and anomaly detection (sudden spikes may indicate runaway agents or test traffic in production).
3. Capture a quarterly screenshot for the AI risk register and the firm's capacity-planning workpaper.

*Screenshot anchor: docs/images/2.25/EXPECTED.md#3-4-runtime-trend — Agent Runtime trend chart showing a 90-day line series.*

For PowerShell automation of governance card data extraction (oldest-pending age, ownerless count) for off-portal dashboarding and SIEM forwarding, see [`./powershell-setup.md`](./powershell-setup.md). For test cases that validate governance card population and SLA reporting, see [`./verification-testing.md`](./verification-testing.md).

---

## 4. Agent Registry — Filtering, Inspection, and Export

**Verification Criteria evidenced:** VC-3 (Agent Registry maintained as the system of record), VC-7 (inventory export produced on a documented cadence and retained per SEC 17a-4 / FINRA 4511).

The Agent Registry is the authoritative inventory of all agents discoverable in the tenant — Microsoft-published (Researcher, Analyst, Sales, Service), org-published (Copilot Studio agents your firm built), and third-party agents registered through the Microsoft Agent Framework. The registry powers every other governance action in this control.

### 4.1 Open the Agent Registry

1. From **Agent 365 → Agents**, click **All Agents**. The grid loads with default columns: **Display name**, **Publisher**, **Platform**, **Owner**, **Status**, **Deployment scope**, **Last modified**.
2. Use the column chooser (gear icon, upper-right of the grid) to add: **Agent ID**, **Governance template applied**, **Last approval timestamp**, **Approver UPN**. These columns are required for the §12 inventory export.
3. Confirm the grid row count matches the **Agent Registry count** hero tile on the Overview (§3.1). A mismatch indicates a filter is applied or the page has not refreshed.

*Screenshot anchor: docs/images/2.25/EXPECTED.md#4-1-registry-grid — Agent Registry grid with the full column set visible and the row count matching the Overview hero tile.*

### 4.2 Filter the registry

1. Use the filter chips above the grid to narrow by:
   - **Publisher** — Microsoft / Organization / Partner (third-party).
   - **Platform** — Microsoft 365 Copilot / Copilot Studio / Azure AI Foundry / Microsoft Agent Framework / Partner.
   - **Status** — Active / Pending Publish / Pending Activation / Blocked / Removed / Pending Update Approval.
   - **Deployment scope** — All Users / Specific Groups / No Users / Pinned.
   - **Governance template applied** — Default / Custom (with template name) / None (a "None" result in Zone 2 or Zone 3 is itself an audit finding).
2. Save common filter combinations as views: **"Zone 2 Active without Governance Template"**, **"Zone 3 Pending Activation"**, **"Third-party publisher"**. Saved views drive the weekly governance session agenda.
3. The filter chips do not persist across user sessions; saved views do.

*Screenshot anchor: docs/images/2.25/EXPECTED.md#4-2-filters — Agent Registry with filter chips applied (Publisher = Organization, Status = Active, Governance template applied = None).*

### 4.3 Inspect a single agent

1. Click any agent row to open the agent detail flyout.
2. Confirm the flyout exposes:
   - **Agent metadata:** Agent ID (GUID), display name, publisher, platform, version, last modified.
   - **Owner:** named human owner with UPN and Entra object ID. Verify the owner's account is not disabled and `employeeLeaveDateTime` is null or in the future.
   - **Data connections:** SharePoint sites, Dataverse tables, Microsoft Graph endpoints, third-party connectors. Confirm each connection is documented in the Control 1.2 Agent Registry record and approved per [Control 2.3](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md).
   - **Tools:** functions, plugins, OpenAPI actions the agent can invoke. Each tool with write or external-network capability requires a documented business justification.
   - **Governance template applied:** Default or Custom (with template name).
   - **Approval history:** publish approval, activation approval, last update approval — each with timestamp and approver UPN.
3. Cross-reference the flyout content against the Control 1.2 Agent Registry record. Discrepancies (for example, a data connection visible in the flyout but absent from the registry) must be reconciled within the firm's documented reconciliation SLA.

*Screenshot anchor: docs/images/2.25/EXPECTED.md#4-3-agent-detail — Agent detail flyout showing metadata, owner, data connections, tools, governance template, and approval history sections.*

### 4.4 Export the registry

1. From **Agent 365 → Agents → All Agents**, click **Export** (top-right of the grid).
2. Choose the format the tenant offers — typically **CSV** or **Excel**. Microsoft has stated CSV/Excel are the supported export formats at GA; verify against the current Microsoft Learn documentation if a different format appears in your tenant.
3. Confirm the export contains, at minimum:
   - `agent_id`, `display_name`, `publisher`, `platform`, `owner_upn`, `status`, `deployment_scope`, `governance_template_applied`, `last_approval_timestamp`, `approver_upn`.
4. Where Microsoft's export omits any of those fields, supplement with the Microsoft Graph API export (see [`./powershell-setup.md`](./powershell-setup.md)) or with the [Control 1.2 Agent Registry](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md) record. Document the supplementation in the export manifest.
5. Save the export with an ISO 8601 filename: `agent365-registry-YYYY-MM-DD.csv`. Retention and WORM placement are detailed in §12.

*Screenshot anchor: docs/images/2.25/EXPECTED.md#4-4-export — Agent Registry export dialog with CSV format selected and the destination path visible.*

!!! example "Examiner Evidence Box — Agent Registry Snapshot"
    | Element | Value |
    |---|---|
    | Artifact produced | Monthly Agent Registry CSV/Excel export with ISO 8601 filename; supplementation manifest where any required column was filled from Graph or Control 1.2 |
    | Retention duration | 6 years on Purview WORM-locked records label per FINRA 4511 / SEC 17a-4 |
    | Regulatory mapping | FINRA 3110 (supervision artifact), FINRA 4511 (books and records), SEC 17a-3/17a-4 (recordkeeping), SOX §404 (control evidence), NYDFS 23 NYCRR 500 (asset inventory) |

For PowerShell automation of registry export, scheduled snapshots, and Microsoft Graph supplementation, see [`./powershell-setup.md`](./powershell-setup.md). For test cases validating column completeness and filename conventions, see [`./verification-testing.md`](./verification-testing.md).

---

## 5. Publishing Approval Workflow

**Verification Criteria evidenced:** VC-2 (admin-gated publication is enforced as the default for Zone 2 / Zone 3 agents), VC-4 (governance template is applied at publish time).

The publishing approval workflow is the primary supervisory checkpoint for agents entering org-wide visibility. Microsoft's design intent is that an agent moves from author-private to org-published only after an **AI Administrator** (or higher) has reviewed the agent's description, owner, data connections, tools, and intended audience, and has applied an appropriate governance template. **Do not bypass this workflow** by granting end users self-service publish rights in Zone 2 or Zone 3.

### 5.1 Open the Pending Requests blade

1. From **Agent 365 → Pending Requests**, select the **Publishing** tab.
2. The grid lists every agent awaiting publication approval, sorted oldest-first by submission timestamp.
3. Filter by **Zone** (where the requester has self-tagged the zone), **Platform**, and **Requester UPN** as needed for the day's queue.

*Screenshot anchor: docs/images/2.25/EXPECTED.md#5-1-publishing-queue — Pending Requests blade with the Publishing tab selected and the oldest-first sort visible.*

### 5.2 Review the agent under request

1. Click the agent row to open the Publishing review wizard.
2. **Step 1 — Agent Overview:** Confirm the **display name** is professional and unambiguous (no internal codenames in production); the **description** clearly states purpose, data scope, and intended user population; the **publisher** matches the firm or an approved partner.
3. **Step 2 — Owner & Sponsor:** Confirm the **named owner UPN** is a current employee with manager attribution. Cross-reference against [Control 2.26 — Entra Agent ID Identity Governance](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md) for autonomous-agent sponsor rules. Reject any submission with a generic mailbox or service account as owner.
4. **Step 3 — Data Connections:** Inspect every connection: SharePoint sites, Dataverse tables, Microsoft Graph endpoints, third-party connectors. For each, confirm:
   - The connection is documented in the Control 1.2 Agent Registry record.
   - The data scope aligns with the agent's stated purpose (no over-broad connections).
   - Sensitive sources (MNPI, PII, customer financial data, trading data) trigger Zone 3 requirements (§5.5).
5. **Step 4 — Tools:** Inspect every tool / plugin / OpenAPI action. Tools with **write** capability or **external-network** capability require an explicit business justification recorded in the change-management ticket.
6. **Step 5 — Audience Scoping:** The default scope is **No Users** (visible in the registry but not deployed). Confirm the requested audience (specific groups, all users) is appropriate for the zone.

*Screenshot anchor: docs/images/2.25/EXPECTED.md#5-2-publishing-review — Publishing review wizard Step 1 with display name, description, and publisher fields visible.*

### 5.3 Apply the governance template

1. **Step 6 — Apply Template:** This step is **mandatory** for Zone 2 and Zone 3 agents. Select from:
   - **Default Governance Template** — Microsoft documents the GA Default as bundling a baseline set of **Microsoft Entra Identity Protection**, **Lifecycle Management**, **SharePoint access**, and **Microsoft Purview Audit / AI Compliance Assessment** policies, plus auto-assignment of the Agent 365 license. **Verify the exact policy composition in your tenant after each Microsoft release wave before asserting any specific policy is enforced.**
   - **Custom Governance Template** — extends the Default with additional policies. For Zone 3 the Custom template **must** include an **Entra Access Package** for scoped, time-bound access authorization (see §9.3). Optional extensions include **Global Secure Access (GSA)** network visibility, **Purview Know Your Data** classification feedback, and **SharePoint Content Permissions Insights**.
2. Do not skip this step. A blank template selection on a Zone 2 or Zone 3 publish is itself an audit finding under FINRA 3110 (supervisory chain) and SOX §404 (control operation).
3. The template selection is recorded against the agent's approval history and surfaces in the inventory export `governance_template_applied` column (§4.4).

*Screenshot anchor: docs/images/2.25/EXPECTED.md#5-3-apply-template — Publishing wizard Step 6 with the Default Governance Template selected and the policy composition list expanded.*

### 5.4 Approve, request changes, or reject

1. **Step 7 — Decision:** Choose one of:
   - **Approve & Publish** — agent moves to **Active** status with the selected audience scope and template applied.
   - **Request Changes** — agent returns to the requester with a reviewer comment. The reviewer comment is mandatory and is logged in the approval history.
   - **Reject** — agent moves to **Rejected** status with a mandatory reason. Rejected agents remain in the registry for audit purposes and can be re-submitted by the requester after addressing the reason.
2. The **AI Administrator** records the change-management ticket ID in the decision comment field (where Microsoft's surface allows). This creates the cross-link between the Agent 365 approval history and the firm's change-management system per [Control 2.3](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md).
3. The decision timestamp and approver UPN are written to the approval history and to the inventory export `last_approval_timestamp` and `approver_upn` columns.

*Screenshot anchor: docs/images/2.25/EXPECTED.md#5-4-decision — Publishing wizard Step 7 with the Approve & Publish action selected and the change-management ticket ID in the comment field.*

### 5.5 Zone 3 additional requirements

For Zone 3 agents (typically those with access to MNPI, customer financial data, trading data, or other regulated content), the following additional steps are required before clicking **Approve & Publish**:

1. **Compliance Officer concurrence:** the Compliance Officer must record concurrence in the change-management ticket. Capture the ticket URL in the publishing decision comment.
2. **Information Security Officer review:** for any agent with external-network tool capability, the Information Security Officer must concur on the network egress posture. Capture the concurrence in the change-management ticket.
3. **Custom Governance Template with Entra Access Package:** the template selected at §5.3 must be a Custom template that includes a named Entra Access Package. Audience scoping at §5.2 Step 5 must default to **No Users** at publish time — actual user assignment happens through the Access Package after publication.
4. **Documented business justification in WSPs:** Zone 3 agents must be enumerated in the firm's Written Supervisory Procedures with named registered principal supervisory responsibility per FINRA Rule 3110.

!!! warning "Zone 3 Without Compliance Concurrence Is a Finding"
    Approving a Zone 3 publication without recorded Compliance Officer concurrence in the change-management system breaks the firm's documented supervisory chain. The Agent 365 approval history alone is not sufficient — the change-management ticket carrying the Compliance Officer signature is the artifact examiners will request. Do not approve until both records exist.

*Screenshot anchor: docs/images/2.25/EXPECTED.md#5-5-zone3-publish — Publishing wizard with a Zone 3 agent showing Custom Governance Template selected and the Compliance Officer ticket URL pasted in the decision comment.*

!!! example "Examiner Evidence Box — Publishing Approval Decision"
    | Element | Value |
    |---|---|
    | Artifact produced | Agent 365 approval history entry (timestamp, approver UPN, template applied, decision comment with ticket ID); change-management ticket with Compliance Officer / Information Security Officer concurrence for Zone 3 |
    | Retention duration | 6 years (SEC 17a-4 / FINRA 4511) |
    | Regulatory mapping | FINRA 3110 (supervision), FINRA 4511 (books and records), FINRA Regulatory Notice 25-07 (AI tools governance), SOX §302/§404 (internal controls), OCC Bulletin 2026-13 (formerly OCC 2011-12) (technology risk), NYDFS 23 NYCRR 500 |

For PowerShell automation of bulk publishing approvals (scripted reviews against a documented allowlist) and approval-history extraction, see [`./powershell-setup.md`](./powershell-setup.md). For end-to-end test cases including a deliberate misconfiguration to validate that the workflow rejects it, see [`./verification-testing.md`](./verification-testing.md). For common publishing wizard errors (missing template selection, owner UPN resolution failures, audience scope conflicts), see [`./troubleshooting.md`](./troubleshooting.md).

---

## 6. Activation Approval Workflow

**Verification Criteria evidenced:** VC-2 (admin-gated activation is enforced for agents requiring an instance to be created), VC-4 (governance template is reapplied or confirmed at activation time).

For agent platforms that distinguish **publication** (the agent is org-visible and assignable) from **activation** (an instance of the agent is created for a specific user, group, or environment), the activation step is reviewed separately. This separation enables phased rollouts — for example, publishing an agent broadly but activating it only in pilot environments first.

### 6.1 Open the Activation queue

1. From **Agent 365 → Pending Requests**, select the **Activation** tab.
2. The grid lists every activation request awaiting approval, sorted oldest-first.
3. Filter by **Zone**, **Requested by**, **Target environment** (for Copilot Studio / Power Platform agents), and **Submission date**.

*Screenshot anchor: docs/images/2.25/EXPECTED.md#6-1-activation-queue — Pending Requests blade with the Activation tab selected.*

### 6.2 Review the activation request

1. Click the activation request row to open the Activation review flyout.
2. Confirm:
   - The agent is already **Active** (publication-approved) per §5.
   - The **target audience or environment** for activation matches the firm's documented rollout plan.
   - The **governance template** previously applied at publish time is still appropriate for the activation scope. If the activation expands scope (for example, from a pilot group to a broader audience), the template may need to be upgraded to a Custom template with additional policies.
3. For Zone 3 activations, reconfirm Compliance Officer concurrence in the change-management ticket — concurrence at publish time does not automatically extend to subsequent activation expansions.

*Screenshot anchor: docs/images/2.25/EXPECTED.md#6-2-activation-review — Activation review flyout showing the agent's current status, target audience, and governance template.*

### 6.3 Approve, request changes, or reject

1. Choose **Approve & Activate**, **Request Changes**, or **Reject**. The decision is logged to the approval history with timestamp and approver UPN.
2. Capture the change-management ticket ID in the decision comment.
3. After approval, the activation propagates within minutes; verify by refreshing the **Agent Registry** and confirming the **Status** column changed from **Pending Activation** to **Active** with the new audience scope.

*Screenshot anchor: docs/images/2.25/EXPECTED.md#6-3-activation-decision — Activation review flyout with Approve & Activate selected and the change-management ticket ID in the comment field.*

!!! example "Examiner Evidence Box — Activation Approval Decision"
    | Element | Value |
    |---|---|
    | Artifact produced | Agent 365 approval history entry for activation (timestamp, approver UPN, target audience, decision comment with ticket ID); change-management ticket reflecting any scope expansion |
    | Retention duration | 6 years (SEC 17a-4 / FINRA 4511) |
    | Regulatory mapping | FINRA 3110 (supervision), SOX §404 (phased rollout control), NYDFS 23 NYCRR 500 |

For PowerShell automation of activation approvals and bulk activation against an allowlist, see [`./powershell-setup.md`](./powershell-setup.md). For activation-flow test cases, see [`./verification-testing.md`](./verification-testing.md).

---

## 7. Lifecycle Actions — Deploy, Pin, Block, Remove, Delete

**Verification Criterion evidenced:** VC-5 (lifecycle actions are exercised under documented authorization with attribution).

After publication and activation, the **AI Administrator** uses five lifecycle actions to manage how agents reach users and how they exit the environment. Each action writes to the agent's approval history with timestamp and approver UPN, and each should be cross-referenced to a change-management ticket.

| Action | Effect | Reversible | Typical authorization |
|---|---|---|---|
| **Deploy** | Pushes the agent to a defined audience automatically (the agent appears for the user without further action). | Yes — by re-scoping the deployment audience or removing. | Change-management ticket; **AI Administrator** with optional Compliance Officer concurrence for Zone 3. |
| **Pin** | Surfaces the agent prominently in the Microsoft 365 Copilot UI (pinned at the top of the agent picker for the targeted audience). | Yes — by un-pinning. | Change-management ticket; **AI Administrator**. |
| **Block** | Restricts access org-wide. The agent remains in the registry but is not invocable by any user until unblocked. | Yes — by unblocking. | Change-management ticket OR an active security incident; **AI Administrator** for routine, **Information Security Officer** + **AI Administrator** for incident-driven. |
| **Remove** | Removes the agent from active inventory. The agent record is retained for audit but no users see or invoke it. **Re-addable** by an admin. | Yes — by re-adding. | Change-management ticket; **AI Administrator**. |
| **Delete** | Permanently deletes the agent and its associated files (knowledge sources, conversation history per Microsoft's retention policy). **Not reversible.** | **No.** | Change-management ticket + Compliance Officer concurrence + (for Zone 3) Information Security Officer concurrence; deletion of any agent with regulated-content access requires WSP-aligned retention review before action. |

### 7.1 Open the lifecycle actions menu

1. From **Agent 365 → Agents → All Agents**, locate the target agent and click the row to open the agent detail flyout.
2. In the flyout header, click **Manage**. The lifecycle actions menu surfaces the five actions above (some actions may be greyed out if the agent's current status disallows the action — for example, **Activate** is unavailable for an already-active agent).

*Screenshot anchor: docs/images/2.25/EXPECTED.md#7-1-manage-menu — Agent detail flyout with the Manage menu expanded showing Deploy, Pin, Block, Remove, Delete options.*

### 7.2 Deploy

1. Click **Manage → Deploy**.
2. In the Deploy dialog, select the target audience: **All Users**, **Specific Groups** (Entra security groups or M365 groups), or **Specific Users** (UPN list).
3. For Zone 3 agents with regulated-content access, the audience must be the Entra Access Package assigned through the Custom Governance Template (see §9.3) — do not deploy to **All Users**.
4. Capture the change-management ticket ID in the deployment comment field.
5. Click **Deploy**. The audience receives the agent within minutes.

*Screenshot anchor: docs/images/2.25/EXPECTED.md#7-2-deploy-dialog — Deploy dialog showing audience selection and the change-management ticket ID in the comment field.*

### 7.3 Pin

1. Click **Manage → Pin**.
2. Select the audience for whom the agent should be pinned (typically a subset of the deployed audience — for example, pin only for the operations team within a broader deployment).
3. Capture the change-management ticket ID in the comment.
4. Click **Pin**.

*Screenshot anchor: docs/images/2.25/EXPECTED.md#7-3-pin-dialog — Pin dialog showing audience selection.*

### 7.4 Block

1. Click **Manage → Block**.
2. Select the block scope: **All Users** (full org-wide block) or **Specific Groups / Users** (selective block, for example to remove access from a departed team).
3. Provide a mandatory reason. For incident-driven blocks, reference the incident ticket ID; for routine policy blocks, reference the change-management ticket ID.
4. Click **Block**. The agent immediately becomes non-invocable for the target scope.

*Screenshot anchor: docs/images/2.25/EXPECTED.md#7-4-block-dialog — Block dialog with All Users selected and an incident ticket ID in the reason field.*

!!! warning "Block as Incident Containment"
    The Block action is the fastest tenant-level kill switch for an agent that is malfunctioning, leaking data, or behaving anomalously. Information Security Officers and AI Administrators should rehearse the Block action quarterly so the team is fluent under incident pressure. Document the rehearsal in the incident response runbook per [Control 2.3](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md).

### 7.5 Remove

1. Click **Manage → Remove**.
2. Confirm the agent removal. The agent record is retained but the agent disappears from end-user surfaces.
3. Capture the change-management ticket ID. Removed agents can be re-added by an admin via **Manage → Re-add**.

*Screenshot anchor: docs/images/2.25/EXPECTED.md#7-5-remove-dialog — Remove confirmation dialog.*

### 7.6 Delete

1. Click **Manage → Delete**.
2. Read the warning carefully — Delete is **permanent** and removes associated agent files (knowledge sources, conversation history per Microsoft's retention policy for the platform). For agents with regulated-content access, confirm that all retention obligations have been satisfied (records exported and archived to Purview WORM storage) **before** deleting.
3. The Delete dialog requires typing the agent display name to confirm — this is by design to prevent accidental deletion.
4. Capture the change-management ticket ID, the Compliance Officer concurrence reference, and (for Zone 3) the Information Security Officer concurrence reference in the deletion comment.
5. Click **Delete**.

*Screenshot anchor: docs/images/2.25/EXPECTED.md#7-6-delete-dialog — Delete confirmation dialog with the agent name typed in the confirmation field and the change-management / Compliance Officer references in the comment.*

!!! warning "Deletion Is Not a Substitute for Retention"
    Deleting an agent does not relieve the firm of SEC 17a-4 / FINRA 4511 retention obligations for records the agent generated. Retention applies to the **records produced by the agent's operation**, which must be archived to Purview WORM storage **before** the agent is deleted. Deleting an agent with unfulfilled retention obligations is itself an audit finding under FINRA 4511 and SOX §404.

!!! example "Examiner Evidence Box — Lifecycle Action Audit Trail"
    | Element | Value |
    |---|---|
    | Artifact produced | Approval history entries for every Deploy, Pin, Block, Remove, and Delete action with timestamp, approver UPN, action scope, and change-management ticket ID; rehearsal records for the quarterly Block drill |
    | Retention duration | 6 years (SEC 17a-4 / FINRA 4511) |
    | Regulatory mapping | FINRA 3110 (supervisory action attribution), FINRA 4511 (lifecycle records), SOX §404 (control operation), NYDFS 23 NYCRR 500 (incident response governance) |

For PowerShell automation of bulk lifecycle actions (for example, scripted Block during an incident or scheduled Remove for unused agents), see [`./powershell-setup.md`](./powershell-setup.md). For test cases including a Block-then-unblock incident drill and a Delete pre-condition retention check, see [`./verification-testing.md`](./verification-testing.md).

---

## 8. Approve Updates — Version-Pinning Workflow

**Verification Criterion evidenced:** VC-5 (agent updates are admin-reviewed before reaching users; the previous version remains active until approval).

When an agent author publishes a new version of an existing agent, the new version is held in **Pending Update Approval** state. The previous version remains active for end users until an **AI Administrator** reviews and approves the update. This version-pinning behavior is the primary control against unreviewed prompt-injection vectors, scope creep, and capability changes that bypass the original publication review.

### 8.1 Open the Updates queue

1. From **Agent 365 → Pending Requests**, select the **Updates** tab.
2. The grid lists every agent version awaiting approval, with columns: **Agent display name**, **Current active version**, **Pending version**, **Submitted by**, **Submitted at**, **Diff summary** (where the platform provides one).

*Screenshot anchor: docs/images/2.25/EXPECTED.md#8-1-updates-queue — Pending Requests blade with the Updates tab selected showing version diffs.*

### 8.2 Review the update diff

1. Click the row to open the Update review flyout.
2. The flyout surfaces a diff between the active version and the pending version, including:
   - **Description and instruction (system prompt) changes** — review for scope expansion, removal of safety language, or new instructions that conflict with firm policy.
   - **Data connection changes** — added or removed SharePoint sites, Dataverse tables, Microsoft Graph endpoints, third-party connectors. Each addition requires re-review against the original publication scope.
   - **Tool changes** — added or removed plugins, OpenAPI actions. New tools with write or external-network capability require explicit business justification.
   - **Audience scope changes** — any expansion to a broader audience requires re-review against the zone classification.
3. If the diff includes any change that materially expands the agent's capability, sensitivity, or audience beyond the original publication approval, the update must be treated as a **new publication** and routed through the §5 publishing workflow with full Compliance Officer / Information Security Officer concurrence (for Zone 3).

*Screenshot anchor: docs/images/2.25/EXPECTED.md#8-2-update-diff — Update review flyout showing the diff between active and pending versions across instruction, data connections, tools, and audience.*

### 8.3 Approve, request changes, or reject

1. Choose **Approve Update**, **Request Changes**, or **Reject**.
2. **Approve Update:** the pending version becomes active immediately; users transition to the new version on their next agent invocation. The previous version is retained in version history for audit reference.
3. **Request Changes:** returns the update to the author with reviewer comments. The active version remains in production unaffected.
4. **Reject:** discards the pending version. The active version remains in production unaffected.
5. Capture the change-management ticket ID in the decision comment.

*Screenshot anchor: docs/images/2.25/EXPECTED.md#8-3-update-decision — Update review flyout with Approve Update selected and the change-management ticket ID in the comment.*

!!! warning "Approve Updates Is Not Optional"
    Leaving updates in the queue indefinitely creates two risks: (1) the author may bypass the queue by editing other surfaces (Copilot Studio, Azure AI Foundry) and re-submitting, creating governance gaps; (2) examiners reviewing oldest-pending update age will compare it to the firm's documented SLA for [Control 2.3 change management](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md). Process the Updates queue on the same cadence as the Pending Requests queue (§3.2).

!!! example "Examiner Evidence Box — Update Approval Audit Trail"
    | Element | Value |
    |---|---|
    | Artifact produced | Update approval history entries with version diff snapshot, timestamp, approver UPN, change-management ticket ID; version history of the agent showing the pinned previous version |
    | Retention duration | 6 years (SEC 17a-4 / FINRA 4511) |
    | Regulatory mapping | FINRA 3110 (supervisory review of changes), FINRA 4511 (version records), SOX §404 (change control), NYDFS 23 NYCRR 500 (change management) |

For PowerShell automation of update queue extraction and bulk approval against an allowlist (for example, auto-approving description-only diffs), see [`./powershell-setup.md`](./powershell-setup.md). For test cases that submit a prompt-injection diff and validate that the workflow holds the change for review, see [`./verification-testing.md`](./verification-testing.md).

---

## 9. Governance Templates — Default and Custom

**Verification Criterion evidenced:** VC-4 (governance templates are configured per zone and applied at publish/activate time).

Governance templates are configurable policy bundles applied at publish or activate time. They are the primary mechanism by which the Agent 365 console wires an agent into the firm's broader Microsoft Entra, Microsoft Purview, and SharePoint policy estate.

### 9.1 Verify the Default Governance Template composition

1. From **Agent 365 → Governance → Templates**, select the **Default** template.
2. Review the policy composition. Microsoft documents the GA Default as bundling a baseline set of:
   - **Microsoft Entra Identity Protection** policies (sign-in risk, user risk).
   - **Microsoft Entra Lifecycle Management** policies (joiner / mover / leaver).
   - **SharePoint access** policies (sensitivity-aligned site access).
   - **Microsoft Purview Audit / AI Compliance Assessment** policies.
   - Auto-assignment of the Agent 365 license.
3. **Verify the exact policy composition in your tenant** — Microsoft's documented composition is a baseline that may evolve across release waves. Capture a screenshot of the Default template detail view at every quarterly verification cycle. The policy list visible in your tenant is the authoritative composition for that point in time.
4. Document the verified composition in the AI governance policy with the verification date.

*Screenshot anchor: docs/images/2.25/EXPECTED.md#9-1-default-template — Default Governance Template detail view showing the bundled policy list with each policy expandable.*

!!! warning "Do Not Assume the Default Template Composition"
    The framework documentation and Microsoft Learn both describe the Default template at a moment in time. Do not assert in a Written Supervisory Procedures document that "the Default template enforces X" without a screenshot from your tenant, dated to your verification cycle. Examiners will compare your WSP language against the live composition; mismatches are findings.

### 9.2 Create a Custom Governance Template

1. From **Agent 365 → Governance → Templates**, click **Create template**.
2. Provide a clear, zone-aligned name: for example, `Z3-trading-desk-template`, `Z3-research-mnpi-template`, `Z2-marketing-template`.
3. Start from the Default and **add** policies — do not subtract from the Default unless an explicit business justification is recorded in the change-management ticket.
4. Common Custom additions:
   - **Microsoft Entra Access Package** — required for Zone 3; provides scoped, time-bound, requestable access with attestation.
   - **Microsoft Entra Global Secure Access (GSA)** — adds network egress visibility for agents that invoke external endpoints.
   - **Microsoft Purview Know Your Data** — feeds classification signals back to the AI governance posture.
   - **SharePoint Content Permissions Insights** — surfaces over-permissioned data the agent might reach.
   - **Additional Microsoft Purview retention labels** — apply records-management labels to agent-generated content.
5. Save the template. New publications can now select this Custom template at §5.3 Step 6.

*Screenshot anchor: docs/images/2.25/EXPECTED.md#9-2-custom-template-create — Create Custom Governance Template wizard with the Default selected as base and the Entra Access Package + GSA + Know Your Data extensions added.*

### 9.3 Wire an Entra Access Package into a Zone 3 Custom Template

1. Before creating the Custom template, the **Entra Identity Governance Admin** creates the Access Package in **Entra → Identity Governance → Entitlement management → Access packages**. The Access Package defines:
   - Resources granted (the agent's required Entra security group, SharePoint site memberships, Dataverse roles).
   - Eligible requestor population (the team / role / business function approved to use the agent).
   - Approval workflow (typically the Agent Owner + Compliance Officer for Zone 3).
   - Lifecycle (recurring access reviews, expiration).
2. In the Custom Governance Template, add the Access Package as a referenced policy.
3. At publish time (§5), the Zone 3 audience scope defaults to **No Users** — actual user assignment happens through the Access Package request/approval workflow, not through Deploy.
4. Cross-reference: see [Control 2.26 — Entra Agent ID Identity Governance](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md) §4 for the Entitlement Management catalog and Access Package authoring procedure.

*Screenshot anchor: docs/images/2.25/EXPECTED.md#9-3-access-package — Custom Governance Template detail view showing the linked Entra Access Package with its resource list and approval workflow.*

### 9.4 Govern template change management

1. Any change to the Default or a Custom template is itself a control change. Route every template edit through [Control 2.3 — Change Management and Release Planning](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md).
2. Capture before/after screenshots of the template detail view in the change-management ticket.
3. Re-run the §9.1 verification of the Default template composition after every Microsoft release wave (typically Wave 1 in spring, Wave 2 in autumn).
4. The **Change Management Lead** is the named owner of the template change-management workflow; the **AI Governance Lead** is the named owner of the template content.

!!! example "Examiner Evidence Box — Governance Template Configuration"
    | Element | Value |
    |---|---|
    | Artifact produced | Default template composition screenshot (dated); Custom template definitions per zone with linked Entra Access Package references; change-management tickets for every template edit |
    | Retention duration | 6 years (SEC 17a-4 / FINRA 4511) |
    | Regulatory mapping | FINRA 3110 (supervisory framework), FINRA 4511 (configuration records), SOX §404 (control configuration), OCC Bulletin 2026-13 (formerly OCC 2011-12) (technology risk control), NYDFS 23 NYCRR 500 |

For PowerShell automation of template composition export, see [`./powershell-setup.md`](./powershell-setup.md). For test cases verifying that a Zone 3 publish without a Custom template is rejected by your firm's enforcement script, see [`./verification-testing.md`](./verification-testing.md).

---

## 10. Researcher with Computer Use Configuration

**Verification Criterion evidenced:** VC-6 (Researcher with Computer Use is configured with an affirmative, zone-appropriate access decision and a documented website allowlist where required).

Researcher with Computer Use is generally available since **October 2025** for tenants with Microsoft 365 Copilot licensing (no longer Frontier-gated). It allows the Researcher agent to operate a virtual browser to retrieve and synthesize information from web sources. It is **default-on** for tenants with Copilot licensing — FSI Zone 2 and Zone 3 organizations should make an **affirmative restrictive decision** rather than relying on default-on, because uncontrolled Computer Use creates regulatory and data-leakage risk that examiners will probe.

### 10.1 Open the Researcher Computer Use surface

1. Sign in to [`https://admin.microsoft.com`](https://admin.microsoft.com) as **AI Administrator**.
2. Navigate to **Integrated Apps** (under **Settings** in the left navigation, or via the admin center search bar).
3. In the Integrated Apps grid, filter or search for **Agents**, then locate **Researcher**.
4. Click **Researcher**, then click **Computer Use** in the configuration tab strip.

*Screenshot anchor: docs/images/2.25/EXPECTED.md#10-1-researcher-cu-landing — Integrated Apps → Agents → Researcher → Computer Use configuration page.*

!!! warning "Default-On Behavior — Make an Affirmative Decision"
    Computer Use is generally enabled for tenants with Copilot licensing unless explicitly disabled by an admin. **Do not leave the configuration in the default-on state without a recorded decision.** A recorded affirmative-restrictive decision is itself the evidence examiners will request — the absence of a recorded decision is a finding under FINRA Regulatory Notice 25-07 and OCC Bulletin 2026-13 (formerly OCC 2011-12) (third-party technology risk).

### 10.2 Configure Access scope

1. The **Access** setting controls which users may invoke Computer Use through the Researcher agent. Options:
   - **All Users** — every Copilot-licensed user can invoke Computer Use.
   - **Specific Groups** — only members of named Entra security groups can invoke Computer Use.
   - **No Users** — Computer Use is disabled for all users.
2. Apply the zone-appropriate setting:

   | Zone | Recommended Access scope | Rationale |
   |---|---|---|
   | Zone 1 (Personal) | **All Users** acceptable, with a documented user-awareness communication (training acknowledgment or banner) | Personal exposure; minimal regulatory surface |
   | Zone 2 (Team) | **Specific Groups** — limit to teams with a documented business need | Reduces over-broad exposure; aligns with least-privilege |
   | Zone 3 (Enterprise / Regulated) | **No Users** OR **Specific Groups** restricted to a small named population (for example, the research desk only) | Minimizes data egress and MNPI / regulated-content exposure; aligns with FINRA / SEC examination expectations |

3. Capture the change-management ticket ID in any decision record.

*Screenshot anchor: docs/images/2.25/EXPECTED.md#10-2-cu-access — Computer Use Access scope configured to Specific Groups with a named research-desk security group selected.*

### 10.3 Configure Work data access

1. The **Work data access** toggle controls whether Computer Use sessions can incorporate the user's Microsoft 365 work data (mail, calendar, files) as grounding context.
2. The toggle is **off by default**, but in many tenants is **user-enableable** unless an admin explicitly restricts it.
3. For Zone 2 and Zone 3, set the admin restriction so that **users cannot enable Work data access on their own**. Document the restriction in the AI governance policy.

*Screenshot anchor: docs/images/2.25/EXPECTED.md#10-3-cu-work-data — Computer Use Work data access toggle showing the admin-restricted (user-cannot-enable) state.*

### 10.4 Configure Website Access policy

1. The **Website Access** policy controls which web destinations Computer Use sessions may browse. Options:
   - **Allow All** — Computer Use can browse any reachable URL (the default behavior in many tenants).
   - **Specific URLs (Allowlist)** — Computer Use can only browse URLs matching the allowlist.
   - **Exclude Specific URLs (Denylist)** — Computer Use can browse any URL except those matching the denylist.
2. Apply the zone-appropriate policy:

   | Zone | Recommended Website Access policy | Rationale |
   |---|---|---|
   | Zone 1 | **Allow All** with documented user awareness | Personal use; minimal regulatory surface |
   | Zone 2 | **Exclude Specific URLs** at minimum (deny known-risky categories: file-sharing, generative AI sites, social media for client-facing teams) | Baseline egress hygiene |
   | Zone 3 | **Specific URLs (Allowlist)** restricted to the firm's approved research domain set (Bloomberg, Reuters, regulator sites, internal research portals); MNPI-relevant teams get a more restrictive allowlist | Minimizes uncontrolled data egress; aligns with FINRA / SEC examination expectations on AI-driven external data access |

3. Maintain the allowlist / denylist in the change-management system. Every addition or removal is itself a Control 2.3 change with the requesting team's business justification.

*Screenshot anchor: docs/images/2.25/EXPECTED.md#10-4-cu-website-access — Computer Use Website Access configured to Specific URLs with the firm's allowlist visible.*

### 10.5 Record the affirmative decision

1. Save the configuration. The Researcher Computer Use configuration page displays the current Access, Work data access, and Website Access settings.
2. Capture a screenshot of the saved configuration page and archive it to the firm's compliance evidence repository with the change-management ticket ID.
3. Record the decision (Access scope, Work data access state, Website Access policy, justification, change-management ticket ID, decision date, approver UPN) in the AI governance policy and in the firm's Written Supervisory Procedures.
4. Re-verify the configuration **quarterly** — Microsoft may change defaults across release waves.

!!! example "Examiner Evidence Box — Researcher Computer Use Decision"
    | Element | Value |
    |---|---|
    | Artifact produced | Saved configuration screenshot (dated); decision record in the AI governance policy with Access scope, Work data access state, Website Access policy, justification, change-management ticket ID, approver UPN; quarterly re-verification log |
    | Retention duration | 6 years (SEC 17a-4 / FINRA 4511) |
    | Regulatory mapping | FINRA Regulatory Notice 25-07 (AI tools governance), OCC Bulletin 2026-13 (formerly OCC 2011-12) (technology risk — third-party retrieval), NYDFS 23 NYCRR 500 (data egress controls), GLBA 501(b) (safeguards) |

For PowerShell automation of Researcher Computer Use configuration export and drift detection, see [`./powershell-setup.md`](./powershell-setup.md). For test cases that validate the allowlist enforcement against a deliberately blocked URL, see [`./verification-testing.md`](./verification-testing.md).

---

## 11. Agent Analytics Navigation

**Verification Criterion evidenced:** VC-7 (analytics signals are reviewed on a documented cadence and feed the firm's AI risk register).

Agent Analytics provides the trend signals governance staff use to detect anomalies, plan capacity, and respond to FINRA Regulatory Notice 25-07-style examination questions about adoption and exposure.

### 11.1 Open the Analytics blade

1. From **Agent 365 → Analytics**, the landing page surfaces three primary panels: **Agents by Publisher**, **Agents by Platform**, and **Active Users Over Time**.

*Screenshot anchor: docs/images/2.25/EXPECTED.md#11-1-analytics-landing — Agent 365 Analytics landing page with the three primary panels visible.*

### 11.2 Agents by Publisher panel

1. Review the breakdown across **Microsoft / Organization / Partner (third-party)** publishers.
2. A growing **Partner** count without commensurate growth in publishing approvals is a shadow-AI signal — investigate whether agents are being side-loaded.
3. Capture a quarterly screenshot for the AI risk register.

### 11.3 Agents by Platform panel

1. Review the breakdown across **Microsoft 365 Copilot / Copilot Studio / Azure AI Foundry / Microsoft Agent Framework / Partner**.
2. The platform mix informs which Pillar 2 controls (2.10–2.16 for Copilot Studio governance, 2.20+ for Azure AI Foundry) require deeper attention.

### 11.4 Active Users Over Time panel

1. Review the trend chart for the firm's chosen lookback window (default 30 days; many tenants offer 90-day and 12-month options).
2. Sudden spikes correlate with new deployments or pin actions — verify against the §7 lifecycle action history.
3. Sudden drops may indicate an outage, a Block action, or end-user dissatisfaction — investigate via incident response.

*Screenshot anchor: docs/images/2.25/EXPECTED.md#11-4-active-users-trend — Active Users Over Time chart with a 90-day window selected.*

!!! example "Examiner Evidence Box — Analytics Trend Review"
    | Element | Value |
    |---|---|
    | Artifact produced | Quarterly screenshots of all three Analytics panels; correlation notes against §7 lifecycle actions for any anomalous spike or drop |
    | Retention duration | 6 years (SEC 17a-4 / FINRA 4511) |
    | Regulatory mapping | FINRA Regulatory Notice 25-07 (AI adoption metrics), SOX §404 (control monitoring), NYDFS 23 NYCRR 500 (operational metrics) |

For PowerShell / Microsoft Graph extraction of analytics signals into the firm's SIEM or BI estate, see [`./powershell-setup.md`](./powershell-setup.md).

---

## 12. Inventory Export and Retention

**Verification Criteria evidenced:** VC-7 (inventory export produced on a documented cadence), VC-8 (retention placement satisfies SEC 17a-4 / FINRA 4511 obligations).

The inventory export is the primary artifact examiners request to validate the firm's claim that the agent registry is the system of record. The §4.4 procedure produced an export; this section governs the **retention** of those exports.

### 12.1 Schedule the export cadence

1. The **AI Administrator** (or a delegated PowerShell-automated job — see [`./powershell-setup.md`](./powershell-setup.md)) produces an inventory export on the firm's documented cadence:
   - **Zone 2 default:** monthly.
   - **Zone 3 default:** monthly with weekly delta exports during high-change periods.
2. Document the cadence in the firm's AI governance policy and in the records-management calendar.

### 12.2 Apply ISO 8601 file naming

1. Name every export `agent365-registry-YYYY-MM-DD.csv` (or `.xlsx` per the chosen export format).
2. Where supplementation is required (a column the Microsoft export omits, filled from Microsoft Graph or the Control 1.2 registry), produce a parallel manifest file `agent365-registry-YYYY-MM-DD-manifest.txt` documenting which columns were supplemented and from which source.
3. ISO 8601 naming makes chronological sorting unambiguous and survives copy-paste into examination response packages.

### 12.3 Place exports in WORM-protected retention

1. The retention destination is a Microsoft Purview records-management labeled location — typically a SharePoint document library or a Microsoft 365 Records Management retention label applied to a container.
2. Apply a label of **6 years** with **records management (WORM)** lock so that exports cannot be modified or deleted before the retention horizon expires.
3. Treat the entire signed evidence pack (export + manifest + governance session minutes) as 6-year retention; **3-year minimums apply only to non-supervisory artifacts where the firm has documented that classification** in the AI governance policy. Examiners will challenge any classification that shortens supervisory artifact retention.
4. The **Purview Compliance Admin** (or **Purview Records Manager**) is the named owner of the retention configuration. The **AI Administrator** is the named producer of the exports.

*Screenshot anchor: docs/images/2.25/EXPECTED.md#12-3-worm-label — SharePoint document library settings showing the 6-year records-management label applied to the Agent 365 export folder.*

### 12.4 Verify retention quarterly

1. Each quarter, the **Compliance Officer** (or **Purview Compliance Admin**) verifies:
   - Exports for every month in the prior quarter are present.
   - Filenames match the ISO 8601 convention.
   - Each export is locked under the records-management label (no edits or deletions possible).
   - The supplementation manifest exists for any month where supplementation occurred.
2. Capture the verification in a quarterly retention attestation entry in the AI governance policy log.

!!! warning "Retention Gaps Are Findings"
    A missing month in the export sequence is itself an audit finding under FINRA 4511 and SEC 17a-4. If the schedule is missed, the recovery procedure is to (1) produce the missing export from the current registry as a best-available snapshot, (2) annotate the manifest as a recovery snapshot with the original due date and the actual production date, (3) record the gap in the change-management system, and (4) document the corrective action that prevents recurrence.

!!! example "Examiner Evidence Box — Inventory Export Retention"
    | Element | Value |
    |---|---|
    | Artifact produced | Monthly inventory exports with ISO 8601 filenames; supplementation manifests; quarterly retention attestation log; SharePoint records-management label configuration screenshot |
    | Retention duration | 6 years on Purview WORM-locked records label |
    | Regulatory mapping | FINRA 4511 (books and records), SEC 17a-3/17a-4 (recordkeeping), SOX §404 (control evidence retention), NYDFS 23 NYCRR 500 |

For PowerShell automation of the scheduled export, manifest generation, and Purview label verification, see [`./powershell-setup.md`](./powershell-setup.md). For test cases including a deliberate gap-recovery drill, see [`./verification-testing.md`](./verification-testing.md).

---

## 13. Examiner Evidence Collection Patterns

**Verification Criterion evidenced:** VC-8 (the firm can produce a complete examiner evidence package on demand).

This section consolidates the evidence patterns referenced throughout §0–§12 into examiner-ready bundles. Each bundle maps to a specific regulator's typical examination question pattern. **None of these patterns substitutes for the firm's Written Supervisory Procedures or for assignment of an appropriately registered principal under FINRA Rule 3110**; they help the firm produce evidence that the supervisory and control framework is operating.

### 13.1 FINRA Rule 3110 (Supervision) — agent supervisory chain

Examiners will ask the firm to demonstrate the supervisory chain for any AI agent that interacts with customers, registered representatives, or registered-principal-supervised activities.

| Examiner question | Evidence to produce | Source section |
|---|---|---|
| "Show me the registered principal responsible for supervising AI agent use." | Firm's Written Supervisory Procedures naming the registered principal; the §0.2 role-coverage CSV demonstrating dual-control on the operating roles | §0.2, WSP (out-of-scope artifact) |
| "Show me the approval record for this agent." | Agent 365 approval history flyout (publish + activate + last update) with timestamp, approver UPN, governance template applied; cross-referenced change-management ticket | §5, §6, §8 |
| "Show me the queue review cadence." | Weekly (Zone 2) / daily (Zone 3) governance session minutes; Pending Requests aging report | §3.2 |
| "Show me what happens when an owner leaves." | Ownerless Agents card remediation log; Control 2.26 lifecycle workflow evidence; Control 3.6 orphaned agent remediation log | §3.3, [Control 2.26](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md), [Control 3.6](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) |

### 13.2 FINRA Rule 4511 / SEC Rules 17a-3 and 17a-4 (Books and Records)

| Examiner question | Evidence to produce | Source section |
|---|---|---|
| "Produce the inventory of all AI agents active in your firm during the examination period." | Monthly inventory exports (CSV / Excel) with ISO 8601 filenames; supplementation manifests | §4.4, §12 |
| "Demonstrate retention of these records for the required horizon." | SharePoint records-management label configuration showing 6-year WORM lock; quarterly retention attestation log | §12.3, §12.4 |
| "Produce the lifecycle history of this specific agent." | Agent detail flyout approval history; lifecycle action audit trail (Deploy / Pin / Block / Remove / Delete) | §4.3, §7 |

### 13.3 FINRA Regulatory Notice 25-07 (AI Tools)

| Examiner question | Evidence to produce | Source section |
|---|---|---|
| "What governance applies to your firm's AI tools?" | AI governance policy referencing this control framework; Default and Custom Governance Template definitions | §9 |
| "How do you control external data retrieval by AI tools?" | Researcher Computer Use configuration screenshot; Website Access allowlist / denylist; quarterly re-verification log | §10 |
| "How do you respond to an AI tool malfunction?" | Block action quarterly rehearsal record; incident response runbook | §7.4 |
| "Show your AI adoption metrics." | Quarterly Analytics screenshots; Active Users Over Time chart | §3.1, §11 |

### 13.4 SEC Sections 302 / 404 (SOX Internal Controls)

| Examiner question | Evidence to produce | Source section |
|---|---|---|
| "Demonstrate segregation of duties between agent authoring, approving, and operating roles." | Role-coverage CSV (§0.2); PIM activation log for any Entra Global Admin activations | §0.2, §2.1 |
| "Demonstrate that template changes follow change control." | Change-management tickets for every template edit with before/after screenshots | §9.4 |
| "Demonstrate that updates are reviewed before reaching users." | Approve Updates queue history; version diff snapshots; rejected-update records | §8 |

### 13.5 OCC Bulletin 2026-13 (Technology Risk Management)

| Examiner question | Evidence to produce | Source section |
|---|---|---|
| "Show your inventory of third-party AI agents in use." | Agents by Publisher analytics panel; Partner-publisher filtered registry view | §4.2, §11.2 |
| "Show your control framework for those third-party agents." | Custom Governance Template applied to third-party publications; Compliance Officer / Information Security Officer concurrence records | §5.5, §9.2 |
| "Show your monitoring of third-party agent operation." | Exception Rate hero metric; Agent Runtime trend; SIEM forwarding evidence | §3.1, §3.4 |

### 13.6 NYDFS 23 NYCRR 500 (Cybersecurity)

| Examiner question | Evidence to produce | Source section |
|---|---|---|
| "Show your asset inventory for AI agents." | Monthly inventory exports | §4.4, §12 |
| "Show your access governance for AI agents." | Custom Governance Template with Entra Access Package; access review evidence (cross-reference to [Control 2.26 §6](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md)) | §9.3 |
| "Show your incident response readiness for AI agents." | Block action rehearsal record; incident response runbook | §7.4 |

!!! example "Examiner Evidence Box — Examination-Ready Bundle Composition"
    | Element | Value |
    |---|---|
    | Artifact produced | A single zipped bundle containing: most recent inventory export + manifest; role-coverage CSV; PIM activation log (prior 90 days); Default + Custom template screenshots; Researcher Computer Use configuration screenshot; quarterly governance session minutes; Block rehearsal record; analytics quarterly screenshots; cross-references to Control 1.2, 2.3, 2.8, 2.26, 3.6 evidence packs |
    | Retention duration | 6 years on Purview WORM-locked records label |
    | Regulatory mapping | All of the above |

For PowerShell automation that assembles the examination-ready bundle into a single zip, see [`./powershell-setup.md`](./powershell-setup.md). For end-to-end verification of bundle composition before examination submission, see [`./verification-testing.md`](./verification-testing.md).

---

## 14. Closing Decision Matrix — Portal vs PowerShell vs Graph

Use this matrix to decide which surface to operate for each governance task. Portal is correct for ad-hoc, low-volume, evidence-rich work; PowerShell is correct for scheduled, repeatable, scripted work; Microsoft Graph is correct for integration with the firm's broader BI / SIEM / change-management estate.

| Task | Portal | PowerShell | Microsoft Graph | Recommended primary |
|---|---|---|---|---|
| First-time tenant access validation | ✅ Best | — | — | Portal — humans validating role coverage |
| Daily Pending Requests review | ✅ Best | — | — | Portal — visual queue triage |
| Weekly governance session evidence capture | ✅ Best | — | — | Portal — screenshots and minutes |
| Bulk publish approval against an allowlist | — | ✅ Best | ✅ | PowerShell — see [`./powershell-setup.md`](./powershell-setup.md) |
| Scheduled monthly inventory export | — | ✅ Best | ✅ | PowerShell — repeatable, auditable, ISO 8601 named |
| Inventory export supplementation (filling Microsoft-omitted columns) | — | ✅ | ✅ Best | Graph — programmatic completeness |
| Incident-driven Block of an agent | ✅ Best | ✅ | — | Portal first (speed under pressure); PowerShell as the rehearsed fallback |
| Quarterly Default Governance Template composition verification | ✅ Best | — | — | Portal — visual capture of the live composition |
| Custom Governance Template authoring | ✅ Best | — | — | Portal — wizard-driven |
| Researcher Computer Use configuration | ✅ Best | — | — | Portal — single configuration page |
| Researcher Computer Use drift detection (config changed without ticket) | — | ✅ Best | ✅ | PowerShell — scheduled config snapshot diff |
| SIEM forwarding of agent governance events | — | — | ✅ Best | Graph + Azure Monitor Diagnostic Settings |
| BI dashboard of governance KPIs (queue age, ownerless count, exception rate) | — | ✅ | ✅ Best | Graph — Power BI direct query |
| Examination evidence bundle assembly | ✅ | ✅ Best | ✅ | PowerShell — repeatable, hashable bundle |

### Final readiness checklist

Before declaring this control operational, confirm all of the following:

- [ ] §0 pre-flight gates passed (tenant ID captured, roles dual-covered, Agent 365 licensed and visible).
- [ ] §1 sovereign-cloud variant applied if applicable, with documented compensating controls and quarterly attestation cadence.
- [ ] §2 Entra Global Admin operates only via PIM with justification; AI Administrator is the daily operator.
- [ ] §3 governance card review cadence and SLAs documented in the firm's WSPs.
- [ ] §4 Agent Registry exports include all required columns; supplementation manifest in place where needed.
- [ ] §5 publishing approval workflow exercised end-to-end with a Zone 2 and a Zone 3 test agent.
- [ ] §6 activation approval workflow exercised end-to-end.
- [ ] §7 Deploy / Pin / Block / Remove / Delete actions rehearsed; quarterly Block drill scheduled.
- [ ] §8 Approve Updates queue is reviewed on the documented cadence; no stale pending updates.
- [ ] §9 Default Governance Template composition verified and screenshotted; Custom templates created for Zone 3 with linked Entra Access Packages.
- [ ] §10 Researcher Computer Use configured with affirmative restrictive decision per zone; allowlist (Zone 3) maintained under change control.
- [ ] §11 Analytics review captured in the AI risk register quarterly.
- [ ] §12 Inventory exports produced monthly with ISO 8601 names, placed under Purview 6-year WORM retention.
- [ ] §13 Examination-ready bundle assembled and verified.
- [ ] Cross-references to [Control 1.2](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md), [Control 2.3](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md), [Control 2.8](../../../controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md), [Control 2.26](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md), and [Control 3.6](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) are wired into the firm's evidence pack.
- [ ] Sibling playbooks reviewed: [`./powershell-setup.md`](./powershell-setup.md), [`./verification-testing.md`](./verification-testing.md), [`./troubleshooting.md`](./troubleshooting.md).

!!! tip "What This Control Does — and Does Not — Do"
    This control **supports compliance with** the supervisory, recordkeeping, and technology risk frameworks named throughout. It **does not** by itself satisfy any single regulatory obligation. It **does not** assign a registered principal under FINRA Rule 3110, **does not** classify records under FINRA 4511, **does not** attest to internal controls under SOX §302, and **does not** substitute for the firm's Written Supervisory Procedures. Treat the Agent 365 admin center as a **control surface** that produces evidence the firm's supervisory and compliance program then evaluates and acts upon.

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
