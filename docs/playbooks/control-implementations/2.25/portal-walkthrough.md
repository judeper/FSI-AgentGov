# Portal Walkthrough — Control 2.25: Microsoft Agent 365 Admin Center Governance Console

**Last Verified:** 2026-11-09 (Microsoft documentation only; tenant/UI execution pending). Sources and collection limits: [verification ledger](./verification-testing.md#microsoft-documentation-verification-ledger). Firm evidence requirements below are not promises of native export columns or shipped automation.

!!! danger "READ FIRST — Scope and Sibling Routing"
    **This playbook configures the Microsoft Agent 365 Admin Center governance console** — the unified control plane for agent lifecycle management, publication and activation approval workflows, governance template enforcement, ownerless-agent remediation, and operational monitoring. It walks you through the **Microsoft 365 admin center**, the **Agent 365** blades (Overview, Agent Registry, Pending Requests, Governance Templates, Analytics), and the **Agents > Researcher** surface required to satisfy Verification Criteria 1–8 of [Control 2.25](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md).

    **This walkthrough IS for:**

    | In Scope | Surface | Outcome |
    |---|---|---|
    | Validating Agent 365 licensing (Microsoft 365 E7 ("Frontier Suite") or standalone Agent 365) | M365 admin center → Billing → Licenses | Confirmed entitlement before any governance change |
    | Daily/weekly governance card rhythm (Pending Requests, Ownerless Agents) | M365 admin center → Agents > Overview | Documented review cadence and SLA adherence |
    | Filtering, inspecting, and exporting the Agent Registry | Agents > All agents > Registry | Audit-ready CSV/Excel inventory snapshots |
    | Admin-gated publishing approval workflow with template application | Agents > All agents > Requests (Pending review) | Zero unreviewed Zone 2 / Zone 3 publications |
    | Admin-gated activation approval workflow | Agents > All agents > Requests (Pending activate) | Phased rollout control evidence |
    | Lifecycle actions — Deploy, Pin, Block, Remove, Delete, Approve Updates | Agents > All agents > Registry → \[Agent\] → Manage | Documented lifecycle decisions with admin attribution |
    | Default and Custom Governance Template configuration | Agents > Settings > Security templates | Zone-appropriate policy bundles applied at publish/activate time |
    | Researcher with Computer Use access scoping | M365 admin center → Agents > Researcher → Computer Use | Affirmative restrictive decision per zone, recorded |
    | Agent Analytics navigation for capacity and risk planning | Agents > Overview (analytics) | Trend evidence for the firm's AI risk register |
    | Inventory Export for examiner submission and 6-year WORM retention | Agents > All agents > Registry → Export | ISO 8601-named monthly snapshots in compliance archive |

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
    This playbook helps your organization **support compliance with** FINRA Rule 3110 (Supervision), FINRA Rule 4511 (Books and Records), FINRA RN 24-09 / Rule 3110 (AI Tools), SEC Rules 17a-3 / 17a-4 (Recordkeeping), SOX Sections 302/404 (Internal Controls), GLBA 501(b) (Safeguards Rule), OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12) (Technology Risk Management), and NYDFS 23 NYCRR 500 (Cybersecurity). It does **not** by itself provide any regulatory outcome and **does not substitute for** the firm's obligation to assign an appropriately registered principal where Rule 3110 requires registered supervisory responsibility. Implementation requires Agent 365 licensing (Microsoft 365 E7 ("Frontier Suite") or standalone Agent 365 with an eligible Microsoft 365 subscription), validated change-control procedures, and independent testing by your compliance function. Organizations should verify all configurations against their own examination workpapers and legal counsel before treating these procedures as adequate evidence.

!!! info "Generally Available — May 1, 2026"
    Microsoft Agent 365 reached **general availability on May 1, 2026**. Licensing options:

    | Option | Composition | Notes |
    |---|---|---|
    | Microsoft 365 E7 ("Frontier Suite") | E5 + Microsoft 365 Copilot + Microsoft Entra Suite + Agent 365 | Bundled SKU; covers OBO agents under user license |
    | Standalone Microsoft Agent 365 | Per-user subscription for eligible Microsoft 365 subscriptions; Copilot is not a universal prerequisite | Verify the current entitlement for each agent type; AI teammates have separate documented identity and licensing behavior |

    Tenants that did not participate in the pre-GA Frontier feature program can adopt Agent 365 directly at GA without prior enrollment. Microsoft now documents a tenant-enablement prerequisite: at least one user must be assigned a qualifying Microsoft Agent 365 license before Agent 365 can be enabled. See [Agent 365 overview](https://learn.microsoft.com/en-us/microsoft-agent-365/overview) for current SKU and entitlement guidance. This review verified Microsoft documentation, not the historical March/April UI claims or a live tenant — re-verify portal navigation periodically as 2026 Wave 1 and Wave 2 release cycles are expected to evolve naming, entry points, and the Default Governance Template policy composition.


!!! tip "Portal Navigation May Shift Post-GA"
    Microsoft is expected to refine Agent 365 navigation through 2026 Wave 1 and Wave 2 release cycles. If a blade name in this playbook does not match what you see, search the admin center for the underlying noun ("Agent 365", "Pending Requests", "Governance Templates", "Researcher") and consult [Microsoft Learn — Microsoft Agent 365](https://learn.microsoft.com/en-us/microsoft-agent-365/overview). Screenshot descriptions below are capture requirements, not proof of completed UI verification. Store actual screenshots locally under `maintainers-local/tenant-evidence/`.

---

## Document Map

| § | Section | Verification Criterion Evidenced |
|---|---|---|
| 0 | [Pre-flight Prerequisites and Triage](#0-pre-flight-prerequisites-and-triage) | All — gating checks |
| 1 | [Initial Console Access and Role Validation](#1-initial-console-access-and-role-validation) | VC-1 |
| 2 | [Overview Dashboard Tour and Governance Card Rhythm](#2-overview-dashboard-tour-and-governance-card-rhythm) | VC-1, VC-2 |
| 3 | [Agent Registry — Filtering, Inspection, and Export](#3-agent-registry-filtering-inspection-and-export) | VC-3, VC-7 |
| 4 | [Publishing Approval Workflow](#4-publishing-approval-workflow) | VC-2, VC-4 |
| 5 | [Activation Approval Workflow](#5-activation-approval-workflow) | VC-2, VC-4 |
| 6 | [Lifecycle Actions — Deploy, Pin, Block, Remove, Delete](#6-lifecycle-actions-deploy-pin-block-remove-delete) | VC-5 |
| 7 | [Approve Updates — Version-Pinning Workflow](#7-approve-updates-version-pinning-workflow) | VC-5 |
| 8 | [Governance Templates — Default and Custom](#8-governance-templates-default-and-custom) | VC-4 |
| 9 | [Researcher with Computer Use Configuration](#9-researcher-with-computer-use-configuration) | VC-6 |
| 10 | [Agent Analytics Navigation](#10-agent-analytics-navigation) | VC-7 |
| 11 | [Inventory Export and Retention](#11-inventory-export-and-retention) | VC-7, VC-8 |
| 12 | [Examiner Evidence Collection Patterns](#12-examiner-evidence-collection-patterns) | VC-8 |
| 13 | [Closing Decision Matrix — Portal vs PowerShell vs Graph](#13-closing-decision-matrix-portal-vs-powershell-vs-graph) | Operational reference |

---

## 0. Pre-flight Prerequisites and Triage

Before you click anything in any portal, run through this gate. Skipping a gate produces silent failures later — for example, the **Agent 365** node will not appear in the M365 admin center if no user has a qualifying Agent 365 entitlement assigned, and the wrong role will let you read the registry but not approve a publishing request.

### 0.1 Confirm tenant cloud and tenant ID

1. Sign in to [`https://admin.microsoft.com`](https://admin.microsoft.com) as an account that holds at least **Entra Global Reader** (read-only) — escalate to **AI Administrator** or **Entra Global Admin** only when about to make a configuration change.
2. In the upper-right corner, click your profile photo → **Switch directory** if you are a multi-tenant operator. Confirm you are in the tenant you intend to govern.
3. Navigate to the M365 admin center home, then to **Settings → Org settings → Organization profile**. Capture the **Tenant ID** GUID and the **Primary domain** (for example, `contoso.onmicrosoft.com`). Record both in your runbook.
4. Confirm **Country or region** matches the regulated entity. For US broker-dealers and banks this is typically `United States`.

*Screenshot requirement: capture the actual supported surface and any separate firm evidence described above. See `docs/images/2.25/EXPECTED.md`; no screenshot or UI execution was verified in this documentation review.*


### 0.2 Confirm role assignments

Use the canonical role names from [`docs/reference/role-catalog.md`](../../../reference/role-catalog.md). Current documentation includes **AI Reader** and **Entra Global Reader** for read-only access and **AI Administrator** for management. AI Governance Lead is a firm responsibility, not an Entra built-in role. Plan governance workflows accordingly and apply Microsoft Entra Privileged Identity Management (PIM) to **Entra Global Admin**.

| Role | Required for | Where to assign |
|---|---|---|
| **Entra Global Admin** | Tenant enrollment, licensing, and emergency lifecycle actions; first-time governance template authoring. **Activate via PIM** for the duration of the change window only. | Entra → Roles & admins |
| **AI Administrator** | Day-to-day approval, registry, deployment, blocking, and template-application tasks. This is the daily operator role. | Entra → Roles & admins → search "AI Administrator" |
| **Entra Global Reader** | Evidence-only access for auditors, examiners, and the Compliance Officer collecting screenshots without change rights. | Entra → Roles & admins |
| **Purview Compliance Admin** | Cross-reference for retention labels and Purview Audit / AI Compliance Assessment policies surfaced inside Default and Custom Governance Templates. | Purview → Roles & scopes |
| **Power Platform Admin** | Cross-reference where a published agent originates from Microsoft Copilot Studio and overlaps with environment-level governance (Pillar 2 controls 2.10–2.16). | Power Platform admin center → Settings |

1. In Entra, navigate to **Identity → Roles & admins → Roles**.
2. Search for each role above and click into it. Confirm at minimum **two named human accounts** (no service principals, no break-glass) hold each operating role per FINRA dual-control expectations.
3. If any role shows zero or one assignee, open a ticket with your Entra owner before proceeding — single-person admin coverage on identity governance roles is itself an audit finding under FINRA Rule 3110 supervisory review.

*Screenshot requirement: capture the actual supported surface and any separate firm evidence described above. See `docs/images/2.25/EXPECTED.md`; no screenshot or UI execution was verified in this documentation review.*

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
   - **Microsoft Agent 365** standalone — per-user subscription for eligible Microsoft 365 subscriptions.
3. Verify the eligible base subscription and the entitlement for each feature. Basic inventory/governance and advanced Agent 365 capabilities have different license requirements.
4. Click into **Licenses → Microsoft Agent 365** (or the E7 SKU) and confirm at least one active user assignment is present. Capture the assigned-vs-available counts and record both in your runbook.
5. Confirm OBO scope: agents acting **on behalf of** a licensed user are covered under that user's license. AI teammates now have documented identity, licensing, and mailbox behavior; verify their current entitlement and route identity governance to Control 2.26.

*Screenshot requirement: capture the actual supported surface and any separate firm evidence described above. See `docs/images/2.25/EXPECTED.md`; no screenshot or UI execution was verified in this documentation review.*

!!! warning "Verify Agent-Type Coverage"
    Do not infer universal platform or identity coverage from registry visibility; route them to [Control 2.26 — Entra Agent ID Identity Governance](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md) and apply the sponsor / access-package model. Mixing the two governance surfaces during the preview-to-GA window creates supervisory chain ambiguity that examiners will flag.

### 0.4 Confirm the Agent 365 navigation node is present

1. Return to [`https://admin.microsoft.com`](https://admin.microsoft.com).
2. In the left navigation, look for **Agents**. If it is not visible, click **Show all** at the bottom of the left navigation.
3. If **Agents** or a licensed feature remains unavailable, verify the role and feature entitlement, record the error and correlation ID, then open a ticket via the M365 admin center **Help & support** widget and reference Agent 365 GA (May 1, 2026).

*Screenshot requirement: capture the actual supported surface and any separate firm evidence described above. See `docs/images/2.25/EXPECTED.md`; no screenshot or UI execution was verified in this documentation review.*

### 0.5 Pre-flight gate summary

Do not proceed past this section unless **all** of the following are true:

- [ ] You are signed in to the correct tenant and have captured the tenant ID.
- [ ] Tenant is in M365 Commercial cloud.
- [ ] At least two named humans hold each governance role in §0.2.
- [ ] **Entra Global Admin** is assigned via PIM (eligible, not active by default).
- [ ] At least one named user who will sponsor or own agents has Microsoft 365 E7 or standalone Agent 365 assigned.
- [ ] Feature-specific entitlement and an eligible Microsoft 365 base subscription are verified.
- [ ] The **Agents** node is visible in the left navigation of the M365 admin center.
- [ ] Your governance runbook records the firm's documented SLAs for Pending Requests review (illustrative defaults: weekly Zone 2, daily Zone 3 — examiners will hold the firm to its own documented SLA, not these defaults).

!!! tip "If a Gate Fails"
    Open [`./troubleshooting.md`](./troubleshooting.md) and search for the gate name (for example, "Agent 365 node missing" or "License propagation pending"). Do not attempt workarounds in production until the gate clears — most workarounds for missing licensing or roles create their own audit findings under FINRA 3110 and SOX 404.

---

## 1. Initial Console Access and Role Validation

**Verification Criterion evidenced:** VC-1 (Agent 365 admin center is accessible and the operating roles are correctly assigned and least-privileged).

### 1.1 Activate Entra Global Admin via PIM (only when needed)

The **Entra Global Admin** role is required for tenant enrollment, licensing changes, first-time governance template authoring, and emergency lifecycle actions (such as bulk Block or Delete during an incident). For routine governance work, you should be operating as **AI Administrator**.

1. Sign in to [`https://entra.microsoft.com`](https://entra.microsoft.com) as your daily-use account.
2. Navigate to **Identity governance → Privileged Identity Management → My roles**.
3. Locate **Global Administrator** in the **Eligible assignments** tab.
4. Click **Activate**, set the activation duration to the **shortest interval consistent with the change window** (typically 1–4 hours), and provide a business justification that names the change-management ticket ID per [Control 2.3](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md).
5. Complete any MFA challenge. PIM activation events are logged to the Entra audit log with the justification text and ticket ID — examiners may request these logs as evidence of JIT elevation.

*Screenshot requirement: capture the actual supported surface and any separate firm evidence described above. See `docs/images/2.25/EXPECTED.md`; no screenshot or UI execution was verified in this documentation review.*

!!! warning "Do Not Operate Daily as Entra Global Admin"
    Daily operations as Entra Global Admin breaks the segregation-of-duties expectations of [Control 2.8](../../../controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md) and creates an audit finding under FINRA 3110 and SOX §404. Use **AI Administrator** for the §2–§12 procedures below; activate Entra Global Admin only for the discrete tasks that explicitly require it.

### 1.2 Sign in to the M365 admin center as AI Administrator

1. Sign in to [`https://admin.microsoft.com`](https://admin.microsoft.com) as your **AI Administrator** account.
2. Confirm the upper-right user chip shows the AI Administrator account, not your Entra Global Admin account.
3. In the left navigation, select **Agents > Overview**.
4. Record the actual URL and capture time; do not rely on an undocumented hard-coded route.

*Screenshot requirement: capture the actual supported surface and any separate firm evidence described above. See `docs/images/2.25/EXPECTED.md`; no screenshot or UI execution was verified in this documentation review.*

### 1.3 Validate read-only access for the Compliance Officer

1. Have the **Compliance Officer** sign in to the same URL using their **Entra Global Reader** account.
2. Confirm they can view Overview and the registry **but cannot perform any approve/deploy/block/delete action** — write controls should be greyed out or absent.
3. Document the read-only verification in the role-coverage evidence pack (§0.2 examiner evidence box).

!!! example "Examiner Evidence Box — Console Access Validation"
    | Element | Value |
    |---|---|
    | Artifact produced | Screenshots of Agent 365 Overview as AI Administrator (write-capable) and as Entra Global Reader (read-only); PIM activation log entry for any Entra Global Admin activation in the prior 30 days |
    | Retention duration | 6 years (SEC 17a-4 / FINRA 4511) |
    | Regulatory mapping | FINRA 3110 (supervision), SOX §404 (segregation of duties), NYDFS 23 NYCRR 500 (access governance) |

---

## 2. Overview Dashboard Tour and Governance Card Rhythm

**Verification Criteria evidenced:** VC-1 (Agent 365 admin center is configured and accessible), VC-2 (governance cards are reviewed on a documented cadence with named owners).

The Agent 365 Overview dashboard is the daily entry point for governance staff. It surfaces four hero metrics, two persistent governance cards, and one trend chart. The Overview is read-only — it drives the AI Administrator's queue but the lifecycle actions themselves happen on the Agent Registry and Pending Requests blades.

### 2.1 Hero metrics panel

Open **Agents > Overview**. Record **Agent registry**, **Active users**, **Agent run-time**, and **Registry sync**. Runtime is hours over the last 30 days; third-party activity starts accumulating at license activation, so the first period may be shorter. Sessions and Exceptions belong to supported per-agent Activity views, not Overview hero cards.

For exception monitoring, capture **Agents with exceptions** and, where supported, derive `100 * error sessions / sessions` for the same agent/date range. Higher is worse. Missing telemetry or zero sessions means no rate, not zero or PASS. Preserve the firm's existing escalation threshold and review evidence.

### 2.2 Pending Requests governance card

1. Scroll to the **Pending Requests** card on the Overview page.
2. The card shows three pending requests, newest first. It is not a full aging report or a guaranteed delta-badge view.
3. The **AI Administrator** reviews this card on the firm's documented cadence:
   - **Zone 2 (illustrative default):** weekly governance session, 5-business-day SLA on individual requests.
   - **Zone 3 (illustrative default):** daily review, 2-business-day SLA on individual requests.
   - **Examiners will hold the firm to its own documented SLA, not these illustrative defaults.** Document the chosen cadence and SLA in the AI governance policy and the firm's Written Supervisory Procedures.
4. Click **Manage requests** to open **Agents > All agents > Requests**. Use documented state/channel filters; derive firm zone and SLA aging from retained request evidence, not assumed native zone filters. The publishing approval workflow itself is detailed in §4; activation in §5.
5. Record the count, the oldest-pending age, and any SLA breaches in the weekly governance session minutes. SLA breaches should be escalated to the **AI Governance Lead** and recorded against [Control 2.3](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md).

*Screenshot requirement: capture the actual supported surface and any separate firm evidence described above. See `docs/images/2.25/EXPECTED.md`; no screenshot or UI execution was verified in this documentation review.*

!!! warning "Stale Pending Requests Are an Audit Finding"
    A pending request older than the firm's documented SLA is itself evidence that the supervisory chain required by FINRA Rule 3110 has degraded. Examiners reviewing the inventory export and the Pending Requests card history will compare oldest-pending dates against the WSP-documented SLA. Do not let the queue age past the documented threshold without an escalation note in the change-management system.

### 2.3 Ownerless Agents governance card

1. Scroll to the **Ownerless Agents** card on the Overview page.
2. Use **Agents without owners** to open the filtered registry. Independently reconcile disabled, departed, or otherwise invalid owners with directory/source-platform records; the card does not prove all of those firm checks ran.
3. Open the agent detail view and assign an owner to assign a named, accountable owner before the next governance cycle closes.
4. If a fully orphaned agent (no candidate owner identifiable) is detected, route it through [Control 3.6 — Orphaned Agent Detection and Remediation](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) for the disable-or-delete decision. Do not leave an ownerless agent active across a governance cycle.

*Screenshot requirement: capture the actual supported surface and any separate firm evidence described above. See `docs/images/2.25/EXPECTED.md`; no screenshot or UI execution was verified in this documentation review.*

!!! example "Examiner Evidence Box — Governance Card Rhythm"
    | Element | Value |
    |---|---|
    | Artifact produced | Weekly (Zone 2) / daily (Zone 3) governance session minutes; Pending Requests aging report; Ownerless Agents remediation log |
    | Retention duration | 6 years (SEC 17a-4 / FINRA 4511) on Purview record label |
    | Regulatory mapping | FINRA 3110 (supervision), FINRA RN 24-09 / Rule 3110 (AI tools governance), SOX §404 (control operation) |

### 2.4 Agent Runtime trend chart

1. Review **Agent run-time** (hours over the last 30 days) and the documented Active users trend. Capture the actual date range; do not assume a separate 90-day runtime chart exists.
2. Use this chart for capacity planning input, cost forecasting, and anomaly detection (sudden spikes may indicate runaway agents or test traffic in production).
3. Capture a quarterly screenshot for the AI risk register and the firm's capacity-planning workpaper.

*Screenshot requirement: capture the actual supported surface and any separate firm evidence described above. See `docs/images/2.25/EXPECTED.md`; no screenshot or UI execution was verified in this documentation review.*

For PowerShell automation of governance card data extraction (oldest-pending age, ownerless count) for off-portal dashboarding and SIEM forwarding, see [`./powershell-setup.md`](./powershell-setup.md). For test cases that validate governance card population and SLA reporting, see [`./verification-testing.md`](./verification-testing.md).

---

## 3. Agent Registry — Filtering, Inspection, and Export

**Verification Criteria evidenced:** VC-3 (Agent Registry maintained as the system of record), VC-7 (inventory export produced on a documented cadence and retained per SEC 17a-4 / FINRA 4511).

The Agent Registry is the authoritative inventory of all agents discoverable in the tenant — Microsoft-published (Researcher, Analyst, Sales, Service), org-published (Copilot Studio agents your firm built), and third-party agents registered through the Microsoft Agent Framework. The registry powers every other governance action in this control.

### 3.1 Open the Agent Registry

1. From **Agents > All agents > Registry**, click **All Agents**. The grid loads with default columns: **Display name**, **Publisher**, **Platform**, **Owner**, **Status**, **Deployment scope**, **Last modified**.
2. Capture the columns actually offered. Agent ID, template assignment, approval time, and approver attribution are firm evidence requirements; supplement missing fields from approved records rather than assume they are native columns.
3. Confirm the grid row count matches the **Agent Registry count** hero tile on the Overview (§2.1). Compare the same scope and capture time. Total agents is unaffected by filters; inventory/analytics timing differences and source coverage must be reconciled.

*Screenshot requirement: capture the actual supported surface and any separate firm evidence described above. See `docs/images/2.25/EXPECTED.md`; no screenshot or UI execution was verified in this documentation review.*

### 3.2 Filter the registry

Use the filters actually offered, such as status, publisher type, channel, platform, and data source. Record scope and filters with the export. Firm zones and template/approval joins may require a separate inventory query; do not assume native zone, approval, or saved-view filters.

The Total agents count remains unchanged when filtering. Reconcile exported rows against the selected All agents / Filtered agents scope.

### 3.3 Inspect a single agent

1. Click any agent row to open the agent detail flyout.
2. Record available native fields and supplement missing firm-required evidence; the following is not a guaranteed flyout schema:
   - **Agent metadata:** Agent ID (GUID), display name, publisher, platform, version, last modified.
   - **Owner:** named human owner with UPN and Entra object ID. Verify the owner's account is not disabled and `employeeLeaveDateTime` is null or in the future.
   - **Data connections:** SharePoint sites, Dataverse tables, Microsoft Graph endpoints, third-party connectors. Confirm each connection is documented in the Control 1.2 Agent Registry record and approved per [Control 2.3](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md).
   - **Tools:** functions, plugins, OpenAPI actions the agent can invoke. Each tool with write or external-network capability requires a documented business justification.
   - **Governance template applied:** Default or Custom (with template name).
   - **Approval history:** publish approval, activation approval, last update approval — each with timestamp and approver UPN.
3. Cross-reference the flyout content against the Control 1.2 Agent Registry record. Discrepancies (for example, a data connection visible in the flyout but absent from the registry) must be reconciled within the firm's documented reconciliation SLA.

*Screenshot requirement: capture the actual supported surface and any separate firm evidence described above. See `docs/images/2.25/EXPECTED.md`; no screenshot or UI execution was verified in this documentation review.*

### 3.4 Export the registry

1. From **Agents > All agents > Registry**, click **Export** (top-right of the grid).
2. Choose the format the tenant offers — typically **CSV** or **Excel**. Learn describes CSV and Excel export experiences; record the actual format and All agents / Filtered agents scope.
3. Compare the actual export with the firm's minimum evidence schema (these are not guaranteed native headers):
   - `agent_id`, `display_name`, `publisher`, `platform`, `owner_upn`, `status`, `deployment_scope`, `governance_template_applied`, `last_approval_timestamp`, `approver_upn`.
4. Where Microsoft's export omits any of those fields, supplement with independently validated feature-specific evidence (the companion adapters are not implemented) or with the [Control 1.2 Agent Registry](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md) record. Document the supplementation in the export manifest.
5. Save the export with an ISO 8601 filename: `agent365-registry-YYYY-MM-DD.csv` or `.xlsx`, preserving the real format. Retention and WORM placement are detailed in §11.

*Screenshot requirement: capture the actual supported surface and any separate firm evidence described above. See `docs/images/2.25/EXPECTED.md`; no screenshot or UI execution was verified in this documentation review.*

!!! example "Examiner Evidence Box — Agent Registry Snapshot"
    | Element | Value |
    |---|---|
    | Artifact produced | Monthly Agent Registry CSV/Excel export with ISO 8601 filename; supplementation manifest where any required column was filled from Graph or Control 1.2 |
    | Retention duration | 6 years on Purview WORM-locked records label per FINRA 4511 / SEC 17a-4 |
    | Regulatory mapping | FINRA 3110 (supervision artifact), FINRA 4511 (books and records), SEC 17a-3/17a-4 (recordkeeping), SOX §404 (control evidence), NYDFS 23 NYCRR 500 (asset inventory) |

For PowerShell automation of registry export, scheduled snapshots, and Microsoft Graph supplementation, see [`./powershell-setup.md`](./powershell-setup.md). For test cases validating column completeness and filename conventions, see [`./verification-testing.md`](./verification-testing.md).

---

## 4. Publishing Approval Workflow

**Verification Criteria evidenced:** VC-2 (admin-gated publication is enforced as the default for Zone 2 / Zone 3 agents), VC-4 (governance template is applied at publish time).

The publishing approval workflow is the primary supervisory checkpoint for agents entering org-wide visibility. Microsoft's design intent is that an agent moves from author-private to org-published only after an **AI Administrator** (or higher) has reviewed the agent's description, owner, data connections, tools, and intended audience, and has applied an appropriate governance template. **Do not bypass this workflow** by granting end users self-service publish rights in Zone 2 or Zone 3.

### 4.1 Open the Pending Requests blade

Open **Agents > All agents > Requests** and filter **State = Pending review**. Review the full list; the Overview card only shows three newest requests. Use actual submission-date evidence and the firm's zone registry to calculate SLA age.

### 4.2 Review the agent under request

1. Click the agent row to open the Publishing review wizard.
2. **Firm review — Agent Overview (not a guaranteed wizard step):** Confirm the **display name** is professional and unambiguous (no internal codenames in production); the **description** clearly states purpose, data scope, and intended user population; the **publisher** matches the firm or an approved partner.
3. **Firm review — Owner & Sponsor:** Confirm the **named owner UPN** is a current employee with manager attribution. Cross-reference against [Control 2.26 — Entra Agent ID Identity Governance](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md) for autonomous-agent sponsor rules. Reject any submission with a generic mailbox or service account as owner.
4. **Firm review — Data Connections:** Inspect every connection: SharePoint sites, Dataverse tables, Microsoft Graph endpoints, third-party connectors. For each, confirm:
   - The connection is documented in the Control 1.2 Agent Registry record.
   - The data scope aligns with the agent's stated purpose (no over-broad connections).
   - Sensitive sources (MNPI, PII, customer financial data, trading data) trigger Zone 3 requirements (§4.5).
5. **Firm review — Tools:** Inspect every tool / plugin / OpenAPI action. Tools with **write** capability or **external-network** capability require an explicit business justification recorded in the change-management ticket.
6. **Firm review — Audience Scoping:** Record the offered scope; do not assume a No Users default. Confirm the requested audience (specific groups, all users) is appropriate for the zone.

*Screenshot requirement: capture the actual supported surface and any separate firm evidence described above. See `docs/images/2.25/EXPECTED.md`; no screenshot or UI execution was verified in this documentation review.*

### 4.3 Apply the governance template

1. **Policy selection — Apply Template (not a guaranteed step number):** This step is **mandatory** for Zone 2 and Zone 3 agents. Select from:
   - **Default Governance Template** — Microsoft documents the GA Default as bundling a baseline set of **Microsoft Entra Identity Protection**, **Lifecycle Management**, **SharePoint access**, and **Microsoft Purview Audit / AI Compliance Assessment** policies, with license assignment documented during activation. Current Default also includes Entra network visibility, Purview Know your data, SharePoint content permissions insights, and Defender policies. **Verify the exact policy composition in your tenant after each Microsoft release wave before asserting any specific policy is enforced.**
   - **Custom Governance Template** — extends the Default with additional policies. For Zone 3 the Custom template **must** include an **Entra Access Package** for scoped, time-bound access authorization (see §8.3). Network visibility, Know your data, and content permissions insights are also documented in the Default Template; verify actual composition.
2. Do not skip this step. A blank template selection on a Zone 2 or Zone 3 publish is itself an audit finding under FINRA 3110 (supervisory chain) and SOX §404 (control operation).
3. Retain the template selection and approval attribution in the firm's evidence pack. A native approval-history or export column is not guaranteed.

*Screenshot requirement: capture the actual supported surface and any separate firm evidence described above. See `docs/images/2.25/EXPECTED.md`; no screenshot or UI execution was verified in this documentation review.*

### 4.4 Approve, request changes, or reject

Use the documented **Publish to store** flow: select users and any preinstallation choice, select the policy template, review permissions, then **Publish**. **Reject submission** is also documented. Return corrections through the firm's ticket workflow; do not assume a native Request Changes button or decision-comment field.

Record decision time, operator, agent ID, template, audience, and change-management ticket in the firm's approval register. Native export columns alone are insufficient evidence.

### 4.5 Zone 3 additional requirements

For Zone 3 agents (typically those with access to MNPI, customer financial data, trading data, or other regulated content), the following additional steps are required before clicking **Approve & Publish**:

1. **Compliance Officer concurrence:** the Compliance Officer must record concurrence in the change-management ticket. Capture the ticket URL in the publishing decision comment.
2. **Information Security Officer review:** for any agent with external-network tool capability, the Information Security Officer must concur on the network egress posture. Capture the concurrence in the change-management ticket.
3. **Custom Governance Template with Entra Access Package:** the template selected at §4.3 must be a Custom template that includes a named Entra Access Package. Audience scoping at §4.2 Step 5 must default to **No Users** at publish time — actual user assignment happens through the Access Package after publication.
4. **Documented business justification in WSPs:** Zone 3 agents must be enumerated in the firm's Written Supervisory Procedures with named registered principal supervisory responsibility per FINRA Rule 3110.

!!! warning "Zone 3 Without Compliance Concurrence Is a Finding"
    Approving a Zone 3 publication without recorded Compliance Officer concurrence in the change-management system breaks the firm's documented supervisory chain. The Agent 365 approval history alone is not sufficient — the change-management ticket carrying the Compliance Officer signature is the artifact examiners will request. Do not approve until both records exist.

*Screenshot requirement: capture the actual supported surface and any separate firm evidence described above. See `docs/images/2.25/EXPECTED.md`; no screenshot or UI execution was verified in this documentation review.*

!!! example "Examiner Evidence Box — Publishing Approval Decision"
    | Element | Value |
    |---|---|
    | Artifact produced | Retained approval evidence (native records where available plus firm register) (timestamp, approver UPN, template applied, decision comment with ticket ID); change-management ticket with Compliance Officer / Information Security Officer concurrence for Zone 3 |
    | Retention duration | 6 years (SEC 17a-4 / FINRA 4511) |
    | Regulatory mapping | FINRA 3110 (supervision), FINRA 4511 (books and records), FINRA RN 24-09 / Rule 3110 (AI tools governance), SOX §302/§404 (internal controls), OCC Bulletin 2026-13 (formerly OCC 2011-12) (technology risk), NYDFS 23 NYCRR 500 |

For PowerShell automation of bulk publishing approvals (scripted reviews against a documented allowlist) and approval-history extraction, see [`./powershell-setup.md`](./powershell-setup.md). For end-to-end test cases including a deliberate misconfiguration to validate that the workflow rejects it, see [`./verification-testing.md`](./verification-testing.md). For common publishing wizard errors (missing template selection, owner UPN resolution failures, audience scope conflicts), see [`./troubleshooting.md`](./troubleshooting.md).

---

## 5. Activation Approval Workflow

**Verification Criteria evidenced:** VC-2 (admin-gated activation is enforced for agents requiring an instance to be created), VC-4 (governance template is reapplied or confirmed at activation time).

For agent platforms that distinguish **publication** (the agent is org-visible and assignable) from **activation** (an instance of the agent is created for a specific user, group, or environment), the activation step is reviewed separately. This separation enables phased rollouts — for example, publishing an agent broadly but activating it only in pilot environments first.

### 5.1 Open the Activation queue

Open **Agents > All agents > Requests** and filter **State = Pending activate**. Capture the full pending list and join firm zones/request dates from approved evidence; no separate native Activation tab or zone filter is assumed.

### 5.2 Review the activation request

1. Click the activation request row to open the Activation review flyout.
2. Confirm:
   - The agent is already **Active** (publication-approved) per §4.
   - The **target audience or environment** for activation matches the firm's documented rollout plan.
   - The **governance template** previously applied at publish time is still appropriate for the activation scope. If the activation expands scope (for example, from a pilot group to a broader audience), the template may need to be upgraded to a Custom template with additional policies.
3. For Zone 3 activations, reconfirm Compliance Officer concurrence in the change-management ticket — concurrence at publish time does not automatically extend to subsequent activation expansions.

*Screenshot requirement: capture the actual supported surface and any separate firm evidence described above. See `docs/images/2.25/EXPECTED.md`; no screenshot or UI execution was verified in this documentation review.*

### 5.3 Approve, request changes, or reject

1. Follow the documented activation flow from **Pending activate**, reviewing identity, policy, permissions, and any license assignment before activation.
2. Record the decision, operator, time, target scope, and change-management ticket in the firm's approval register. Do not assume a native Request Changes button or decision-comment field.
3. Refresh the registry and verify actual availability for the approved population. Record errors or pending provisioning; no fixed propagation time is established here.

*Screenshot requirement: capture the actual supported surface and any separate firm evidence described above. See `docs/images/2.25/EXPECTED.md`; no screenshot or UI execution was verified in this documentation review.*

!!! example "Examiner Evidence Box — Activation Approval Decision"
    | Element | Value |
    |---|---|
    | Artifact produced | Retained approval evidence (native records where available plus firm register) for activation (timestamp, approver UPN, target audience, decision comment with ticket ID); change-management ticket reflecting any scope expansion |
    | Retention duration | 6 years (SEC 17a-4 / FINRA 4511) |
    | Regulatory mapping | FINRA 3110 (supervision), SOX §404 (phased rollout control), NYDFS 23 NYCRR 500 |

For PowerShell automation of activation approvals and bulk activation against an allowlist, see [`./powershell-setup.md`](./powershell-setup.md). For activation-flow test cases, see [`./verification-testing.md`](./verification-testing.md).

---

## 6. Lifecycle Actions — Deploy, Pin, Block, Remove, Delete

**Verification Criterion evidenced:** VC-5 (lifecycle actions are exercised under documented authorization with attribution).

After publication and activation, use the supported lifecycle action for the agent's type and state. Preserve each action's operator, timestamp, scope, result, and change-management ticket in the firm's evidence register; a complete native approval-history view is not guaranteed.

| Action | Effect | Reversible | Typical authorization |
|---|---|---|---|
| **Deploy / Install** | Use the documented Install/preinstallation experience for the selected population; availability and installation are distinct. | Use the supported Uninstall action. | Change-management ticket; **AI Administrator** with optional Compliance Officer concurrence for Zone 3. |
| **Pin** | Surfaces the agent prominently in the Microsoft 365 Copilot UI (pinned at the top of the agent picker for the targeted audience). | Yes — by un-pinning. | Change-management ticket; **AI Administrator**. |
| **Block** | Blocks Agent Builder/Copilot Studio agents across hosts; for SharePoint/Foundry agents, blocks Copilot Chat availability, not all source-platform execution. | Yes — by unblocking. | Change-management ticket OR an active security incident; **AI Administrator** for routine, **Information Security Officer** + **AI Administrator** for incident-driven. |
| **Remove / Uninstall** | Uninstalls where supported; does not establish deletion of the agent or removal from every source platform. | Reinstall where supported. | Change-management ticket; **AI Administrator**. |
| **Delete** | Soft-deletes with a 30-day recovery window. Restore is available within that window; Permanently delete is a separate irreversible action. | Soft deletion: recoverable within 30 days. Permanent deletion: no. | Change-management ticket + Compliance Officer concurrence + (for Zone 3) Information Security Officer concurrence; deletion of any agent with regulated-content access requires WSP-aligned retention review before action. |

### 6.1 Open the lifecycle actions menu

1. From **Agents > All agents > Registry**, locate the target agent and click the row to open the agent detail flyout.
2. Inspect the actions actually offered for the agent type/state. Current documentation uses Install/Uninstall, Activate, Block/Unblock, Delete/Restore/Permanently delete; do not assume one universal five-action Manage menu.

*Screenshot requirement: capture the actual supported surface and any separate firm evidence described above. See `docs/images/2.25/EXPECTED.md`; no screenshot or UI execution was verified in this documentation review.*

### 6.2 Deploy

1. Use **Install** or the documented preinstallation choice during **Publish to store**, where supported.
2. Select the offered users/groups and capture the actual audience and install scope.
3. For Zone 3 agents with regulated-content access, the audience must be the Entra Access Package assigned through the Custom Governance Template (see §8.3) — do not deploy to **All Users**.
4. Capture the change-management ticket in the firm's evidence register; do not assume a native deployment-comment field.
5. Complete the offered action and verify the resulting installation/availability for the intended population.

*Screenshot requirement: capture the actual supported surface and any separate firm evidence described above. See `docs/images/2.25/EXPECTED.md`; no screenshot or UI execution was verified in this documentation review.*

### 6.3 Pin

1. Use the documented **Manage pinned agents** entry from the registry where available; do not assume a per-agent Manage > Pin menu.
2. Select the audience for whom the agent should be pinned (typically a subset of the deployed audience — for example, pin only for the operations team within a broader deployment).
3. Capture the change-management ticket ID in the comment.
4. Click **Pin**.

*Screenshot requirement: capture the actual supported surface and any separate firm evidence described above. See `docs/images/2.25/EXPECTED.md`; no screenshot or UI execution was verified in this documentation review.*

### 6.4 Block

1. Select the documented **Block** action for the agent.
2. Inspect the supported action and platform scope; do not assume a selective-block dialog or complete source-platform shutdown.
3. Record the reason and incident/change ticket in the firm's evidence register.
4. Complete Block, then verify availability in the affected hosts. Researcher and Analyst can be tenant-blocked; Edit users is disabled for these agents.

*Screenshot requirement: capture the actual supported surface and any separate firm evidence described above. See `docs/images/2.25/EXPECTED.md`; no screenshot or UI execution was verified in this documentation review.*

!!! warning "Block as Incident Containment"
    The Block action is the fastest tenant-level kill switch for an agent that is malfunctioning, leaking data, or behaving anomalously. Information Security Officers and AI Administrators should rehearse the Block action quarterly so the team is fluent under incident pressure. Document the rehearsal in the incident response runbook per [Control 2.3](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md).

### 6.5 Remove

1. Select the documented **Uninstall** action where offered.
2. Confirm the agent removal. The agent record is retained but the agent disappears from end-user surfaces.
3. Capture the change-management ticket ID. Installation and availability are separate states; use documented Install/Uninstall and Block/Unblock actions, not an assumed Re-add command.

*Screenshot requirement: capture the actual supported surface and any separate firm evidence described above. See `docs/images/2.25/EXPECTED.md`; no screenshot or UI execution was verified in this documentation review.*

### 6.6 Delete

1. Select **Delete** from the agent's documented lifecycle actions.
2. Read the warning carefully — Delete first soft-deletes the agent with a **30-day** recovery window. Restore and Permanently delete are separate actions; permanent deletion is irreversible. Do not infer source-platform file or conversation deletion behavior. For agents with regulated-content access, confirm that all retention obligations have been satisfied (records exported and archived to Purview WORM storage) **before** deleting.
3. Record the actual confirmation presented; a required typed-name field is not established by the current documentation.
4. Capture the change-management ticket ID, the Compliance Officer concurrence reference, and (for Zone 3) the Information Security Officer concurrence reference in the deletion comment.
5. Click **Delete**.

*Screenshot requirement: capture the actual supported surface and any separate firm evidence described above. See `docs/images/2.25/EXPECTED.md`; no screenshot or UI execution was verified in this documentation review.*

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

## 7. Approve Updates — Version-Pinning Workflow

**Verification Criterion evidenced:** VC-5 (agent updates are admin-reviewed before reaching users; the previous version remains active until approval).

When an agent author publishes a new version of an existing agent, the new version is held in **Pending Update Approval** state. The previous version remains active for end users until an **AI Administrator** reviews and approves the update. This version-pinning behavior is the primary control against unreviewed prompt-injection vectors, scope creep, and capability changes that bypass the original publication review.

### 7.1 Open the Updates queue

Open **Agents > All agents > Requests** and filter **State = Pending update**. Capture the agent, requester, and actual version/change evidence. The previous version stays available until the update is approved.

### 7.2 Review the update diff

Review the publisher's retained before/after description, instructions, connections, tools, and audience against the change ticket. The current Microsoft instructions do not promise a complete native system-prompt diff or version-history export; obtain missing evidence from the source platform.

Material scope, sensitivity, or audience expansion follows the firm's existing new-publication approval process, including Zone 3 concurrence. Missing change evidence blocks approval.

### 7.3 Approve, request changes, or reject

Use **Update in store** and review the offered update flow before approval. Until approval, the previous version remains available. Record the decision, version evidence, operator, timestamp, and change ticket in the firm register. Handle requested corrections through that ticket; do not assume a native Request Changes action or guaranteed retained version-history UI.

## 8. Governance Templates — Default and Custom

**Verification Criterion evidenced:** VC-4 (governance templates are configured per zone and applied at publish/activate time).

Governance templates are configurable policy bundles applied at publish or activate time. They are the primary mechanism by which the Agent 365 console wires an agent into the firm's broader Microsoft Entra, Microsoft Purview, and SharePoint policy estate.

### 8.1 Verify the Default Governance Template composition

1. From **Agents > Settings > Security templates**, select the **Default** template.
2. Review the policy composition. Microsoft documents the GA Default as bundling a baseline set of:
   - **Microsoft Entra Identity Protection** policies (sign-in risk, user risk).
   - **Microsoft Entra Lifecycle Management** policies (joiner / mover / leaver).
   - **SharePoint access** policies (sensitivity-aligned site access).
   - **Microsoft Purview Audit / AI Compliance Assessment** policies.
   - License assignment during activation; distinguish this step from the policy list.
3. **Verify the exact policy composition in your tenant** — Microsoft's documented composition is a baseline that may evolve across release waves. Capture a screenshot of the Default template detail view at every quarterly verification cycle. Capture actual selected policies and verify their downstream state; the template label alone is not proof of enforcement.
4. Document the verified composition in the AI governance policy with the verification date.

*Screenshot requirement: capture the actual supported surface and any separate firm evidence described above. See `docs/images/2.25/EXPECTED.md`; no screenshot or UI execution was verified in this documentation review.*

!!! warning "Do Not Assume the Default Template Composition"
    The framework documentation and Microsoft Learn both describe the Default template at a moment in time. Do not assert in a Written Supervisory Procedures document that "the Default template enforces X" without a screenshot from your tenant, dated to your verification cycle. Examiners will compare your WSP language against the live composition; mismatches are findings.

### 8.2 Create a Custom Governance Template

1. From **Agents > Settings > Security templates**, click **Create template**.
2. Provide a clear, zone-aligned name: for example, `Z3-trading-desk-template`, `Z3-research-mnpi-template`, `Z2-marketing-template`.
3. Start from the Default and **add** policies — do not subtract from the Default unless an explicit business justification is recorded in the change-management ticket.
4. Validate the selected policy combination; the following are not all exclusively Custom additions:
   - **Microsoft Entra Access Package** — required for Zone 3; provides scoped, time-bound, requestable access with attestation.
   - **Microsoft Entra network visibility** — also included in the documented Default Template; review visibility for agents that invoke external endpoints.
   - **Microsoft Purview Know Your Data** — also documented in Default; feeds classification signals back to the AI governance posture.
   - **SharePoint Content Permissions Insights** — also documented in Default; surfaces over-permissioned data the agent might reach.
   - **Additional Microsoft Purview retention labels** — apply records-management labels to agent-generated content.
5. Save the template. New publications can now select this Custom template at §4.3 policy-selection stage.

*Screenshot requirement: capture the actual supported surface and any separate firm evidence described above. See `docs/images/2.25/EXPECTED.md`; no screenshot or UI execution was verified in this documentation review.*

### 8.3 Wire an Entra Access Package into a Zone 3 Custom Template

1. Before creating the Custom template, the **Entra Identity Governance Admin** creates the Access Package in **Entra → Identity Governance → Entitlement management → Access packages**. The Access Package defines:
   - Resources granted (the agent's required Entra security group, SharePoint site memberships, Dataverse roles).
   - Eligible requestor population (the team / role / business function approved to use the agent).
   - Approval workflow (typically the Agent Owner + Compliance Officer for Zone 3).
   - Lifecycle (recurring access reviews, expiration).
2. Verify the firm's required access-package association and assignment policy using the supported template and Entra surfaces. AI Administrator alone cannot configure access-package or Conditional Access policies; retain the cross-system association evidence.
3. Under firm policy at publish time (§4), keep the Zone 3 audience unassigned where supported; this is not a guaranteed native No Users default — actual user assignment happens through the Access Package request/approval workflow, not through Deploy.
4. Cross-reference: see [Control 2.26 — Entra Agent ID Identity Governance](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md) §3 for the Entitlement Management catalog and Access Package authoring procedure.

*Screenshot requirement: capture the actual supported surface and any separate firm evidence described above. See `docs/images/2.25/EXPECTED.md`; no screenshot or UI execution was verified in this documentation review.*

### 8.4 Govern template change management

1. Any change to the Default or a Custom template is itself a control change. Route every template edit through [Control 2.3 — Change Management and Release Planning](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md).
2. Capture before/after screenshots of the template detail view in the change-management ticket.
3. Re-run the §8.1 verification of the Default template composition after every Microsoft release wave (typically Wave 1 in spring, Wave 2 in autumn).
4. The **Change Management Lead** is the named owner of the template change-management workflow; the **AI Governance Lead** is the named owner of the template content.

!!! example "Examiner Evidence Box — Governance Template Configuration"
    | Element | Value |
    |---|---|
    | Artifact produced | Default template composition screenshot (dated); Custom template definitions per zone with linked Entra Access Package references; change-management tickets for every template edit |
    | Retention duration | 6 years (SEC 17a-4 / FINRA 4511) |
    | Regulatory mapping | FINRA 3110 (supervisory framework), FINRA 4511 (configuration records), SOX §404 (control configuration), OCC Bulletin 2026-13 (formerly OCC 2011-12) (technology risk control), NYDFS 23 NYCRR 500 |

For PowerShell automation of template composition export, see [`./powershell-setup.md`](./powershell-setup.md). For test cases verifying that a Zone 3 publish without a Custom template is rejected by your firm's enforcement script, see [`./verification-testing.md`](./verification-testing.md).

---

## 9. Researcher with Computer Use Configuration

**Verification Criterion evidenced:** VC-6 (Researcher with Computer Use is configured with an affirmative, zone-appropriate access decision and a documented website allowlist where required).

Current Microsoft documentation describes Researcher Computer use configuration; this review does not substantiate the previous October 2025 GA or universal availability claims. It allows the Researcher agent to operate a virtual browser to retrieve and synthesize information from web sources. Do not assume it is default-on — FSI Zone 2 and Zone 3 organizations should make an **affirmative restrictive decision** rather than relying on an assumed default, because uncontrolled Computer Use creates regulatory and data-leakage risk that examiners will probe.

### 9.1 Open the Researcher Computer Use surface

1. Sign in to [`https://admin.microsoft.com`](https://admin.microsoft.com) as **AI Administrator**.
2. Open the admin **Agents** page (`https://admin.cloud.microsoft/?#/copilot/agents`).
3. Locate **Researcher** in the agent list.
4. Click **Researcher**, then click **Computer Use** in the configuration tab strip.

*Screenshot requirement: capture the actual supported surface and any separate firm evidence described above. See `docs/images/2.25/EXPECTED.md`; no screenshot or UI execution was verified in this documentation review.*

!!! warning "Default-On Behavior — Make an Affirmative Decision"
    Capture actual availability and configured access; current configuration documentation does not establish a universal default-on. **Do not rely on an assumed default without a recorded decision.** A recorded affirmative-restrictive decision is itself the evidence examiners will request — the absence of a recorded decision is a finding under FINRA RN 24-09 / Rule 3110 and OCC Bulletin 2026-13 (formerly OCC 2011-12) (third-party technology risk).

### 9.2 Configure Access scope

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

*Screenshot requirement: capture the actual supported surface and any separate firm evidence described above. See `docs/images/2.25/EXPECTED.md`; no screenshot or UI execution was verified in this documentation review.*

### 9.3 Configure Work data access

1. The **Work data access** toggle controls whether Computer Use sessions can incorporate the user's Microsoft 365 work data (mail, calendar, files) as grounding context.
2. If admin-enabled, users must still manually turn on **Work** in Sources. If admin-disabled, Work is unavailable. Record both administrative and user state.
3. For Zone 2 and Zone 3, set the admin restriction so that **users cannot enable Work data access on their own**. Document the restriction in the AI governance policy.

*Screenshot requirement: capture the actual supported surface and any separate firm evidence described above. See `docs/images/2.25/EXPECTED.md`; no screenshot or UI execution was verified in this documentation review.*

### 9.4 Configure Website Access policy

1. The **Website Access** policy controls which web destinations Computer Use sessions may browse. Options:
   - **Allow All** — Computer Use can browse any reachable URL (record the observed setting; do not assume a default).
   - **Specific URLs (Allowlist)** — Computer Use can only browse URLs matching the allowlist.
   - **Exclude Specific URLs (Denylist)** — Computer Use can browse any URL except those matching the denylist.
2. Apply the zone-appropriate policy:

   | Zone | Recommended Website Access policy | Rationale |
   |---|---|---|
   | Zone 1 | **Allow All** with documented user awareness | Personal use; minimal regulatory surface |
   | Zone 2 | **Exclude Specific URLs** at minimum (deny known-risky categories: file-sharing, generative AI sites, social media for client-facing teams) | Baseline egress hygiene |
   | Zone 3 | **Specific URLs (Allowlist)** restricted to the firm's approved research domain set (Bloomberg, Reuters, regulator sites; do not assume private intranet reachability from the isolated virtual computer); MNPI-relevant teams get a more restrictive allowlist | Minimizes uncontrolled data egress; aligns with FINRA / SEC examination expectations on AI-driven external data access |

3. Maintain the allowlist / denylist in the change-management system. Every addition or removal is itself a Control 2.3 change with the requesting team's business justification.

*Screenshot requirement: capture the actual supported surface and any separate firm evidence described above. See `docs/images/2.25/EXPECTED.md`; no screenshot or UI execution was verified in this documentation review.*

### 9.5 Record the affirmative decision

1. Save the configuration. The Researcher Computer Use configuration page displays the current Access, Work data access, and Website Access settings.
2. Capture a screenshot of the saved configuration page and archive it to the firm's compliance evidence repository with the change-management ticket ID.
3. Record the decision (Access scope, Work data access state, Website Access policy, justification, change-management ticket ID, decision date, approver UPN) in the AI governance policy and in the firm's Written Supervisory Procedures.
4. Re-verify the configuration **quarterly** — Microsoft may change defaults across release waves.

!!! example "Examiner Evidence Box — Researcher Computer Use Decision"
    | Element | Value |
    |---|---|
    | Artifact produced | Saved configuration screenshot (dated); decision record in the AI governance policy with Access scope, Work data access state, Website Access policy, justification, change-management ticket ID, approver UPN; quarterly re-verification log |
    | Retention duration | 6 years (SEC 17a-4 / FINRA 4511) |
    | Regulatory mapping | FINRA RN 24-09 / Rule 3110 (AI tools governance), OCC Bulletin 2026-13 (formerly OCC 2011-12) (technology risk — third-party retrieval), NYDFS 23 NYCRR 500 (data egress controls), GLBA 501(b) (safeguards) |

For PowerShell automation of Researcher Computer Use configuration export and drift detection, see [`./powershell-setup.md`](./powershell-setup.md). For test cases that validate the allowlist enforcement against a deliberately blocked URL, see [`./verification-testing.md`](./verification-testing.md).

---

## 10. Agent Analytics Navigation

**Verification Criterion evidenced:** VC-7 (analytics signals are reviewed on a documented cadence and feed the firm's AI risk register).

Agent Analytics provides the trend signals governance staff use to detect anomalies, plan capacity, and respond to FINRA RN 24-09 / Rule 3110-style examination questions about adoption and exposure.

### 10.1 Open the Analytics blade

1. From **Agents > Overview (analytics)**, the landing page surfaces three primary panels: **Agents by Publisher**, **Agents by Platform**, and **Active Users Over Time**.

*Screenshot requirement: capture the actual supported surface and any separate firm evidence described above. See `docs/images/2.25/EXPECTED.md`; no screenshot or UI execution was verified in this documentation review.*

### 10.2 Agents by Publisher panel

1. Review the breakdown across **Microsoft / Organization / Partner (third-party)** publishers.
2. A growing **Partner** count without commensurate growth in publishing approvals is a shadow-AI signal — investigate whether agents are being side-loaded.
3. Capture a quarterly screenshot for the AI risk register.

### 10.3 Agents by Platform panel

1. Review the breakdown across **Microsoft 365 Copilot / Copilot Studio / Azure AI Foundry / Microsoft Agent Framework / Partner**.
2. Use the platform mix to select applicable governance controls. [Control 2.20](../../../controls/pillar-2-management/2.20-adversarial-testing-and-red-team-framework.md) covers adversarial testing across Microsoft 365 Copilot, Copilot Studio and Foundry-backed agents; it is not the start of a Foundry-only control range.

### 10.4 Active Users Over Time panel

1. Review the trend chart for the firm's chosen lookback window (default 30 days; many tenants offer 90-day and 12-month options).
2. Sudden spikes correlate with new deployments or pin actions — verify against the §6 lifecycle action history.
3. Sudden drops may indicate an outage, a Block action, or end-user dissatisfaction — investigate via incident response.

*Screenshot requirement: capture the actual supported surface and any separate firm evidence described above. See `docs/images/2.25/EXPECTED.md`; no screenshot or UI execution was verified in this documentation review.*

!!! example "Examiner Evidence Box — Analytics Trend Review"
    | Element | Value |
    |---|---|
    | Artifact produced | Quarterly screenshots of all three Analytics panels; correlation notes against §6 lifecycle actions for any anomalous spike or drop |
    | Retention duration | 6 years (SEC 17a-4 / FINRA 4511) |
    | Regulatory mapping | FINRA RN 24-09 / Rule 3110 (AI adoption metrics), SOX §404 (control monitoring), NYDFS 23 NYCRR 500 (operational metrics) |

For PowerShell / Microsoft Graph extraction of analytics signals into the firm's SIEM or BI estate, see [`./powershell-setup.md`](./powershell-setup.md).

---

## 11. Inventory Export and Retention

**Verification Criteria evidenced:** VC-7 (inventory export produced on a documented cadence), VC-8 (retention placement satisfies SEC 17a-4 / FINRA 4511 obligations).

The inventory export is the primary artifact examiners request to validate the firm's claim that the agent registry is the system of record. The §3.4 procedure produced an export; this section governs the **retention** of those exports.

### 11.1 Schedule the export cadence

1. The **AI Administrator** (or a delegated PowerShell-automated job — see [`./powershell-setup.md`](./powershell-setup.md)) produces an inventory export on the firm's documented cadence:
   - **Zone 2 default:** monthly.
   - **Zone 3 default:** monthly with weekly delta exports during high-change periods.
2. Document the cadence in the firm's AI governance policy and in the records-management calendar.

### 11.2 Apply ISO 8601 file naming

1. Name every export `agent365-registry-YYYY-MM-DD.csv` or `.xlsx`, preserving the real format.
2. Where supplementation is required (a column the Microsoft export omits, filled from Microsoft Graph or the Control 1.2 registry), produce a parallel manifest file `agent365-registry-YYYY-MM-DD-manifest.txt` documenting which columns were supplemented and from which source.
3. ISO 8601 naming makes chronological sorting unambiguous and survives copy-paste into examination response packages.

### 11.3 Place exports in WORM-protected retention

1. The retention destination is a Microsoft Purview records-management labeled location — typically a SharePoint document library or a Microsoft 365 Records Management retention label applied to a container.
2. Apply a label of **6 years** with **records management (WORM)** lock so that exports cannot be modified or deleted before the retention horizon expires.
3. Treat the entire signed evidence pack (export + manifest + governance session minutes) as 6-year retention; **3-year minimums apply only to non-supervisory artifacts where the firm has documented that classification** in the AI governance policy. Examiners will challenge any classification that shortens supervisory artifact retention.
4. The **Purview Compliance Admin** (or **Purview Records Manager**) is the named owner of the retention configuration. The **AI Administrator** is the named producer of the exports.

*Screenshot requirement: capture the actual supported surface and any separate firm evidence described above. See `docs/images/2.25/EXPECTED.md`; no screenshot or UI execution was verified in this documentation review.*

### 11.4 Verify retention quarterly

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

## 12. Examiner Evidence Collection Patterns

**Verification Criterion evidenced:** VC-8 (the firm can produce a complete examiner evidence package on demand).

This section consolidates the evidence patterns referenced throughout §0–§11 into examiner-ready bundles. Each bundle maps to a specific regulator's typical examination question pattern. **None of these patterns substitutes for the firm's Written Supervisory Procedures or for assignment of an appropriately registered principal under FINRA Rule 3110**; they help the firm produce evidence that the supervisory and control framework is operating.

### 12.1 FINRA Rule 3110 (Supervision) — agent supervisory chain

Examiners will ask the firm to demonstrate the supervisory chain for any AI agent that interacts with customers, registered representatives, or registered-principal-supervised activities.

| Examiner question | Evidence to produce | Source section |
|---|---|---|
| "Show me the registered principal responsible for supervising AI agent use." | Firm's Written Supervisory Procedures naming the registered principal; the §0.2 role-coverage CSV demonstrating dual-control on the operating roles | §0.2, WSP (out-of-scope artifact) |
| "Show me the approval record for this agent." | Retained firm approval register plus native records available for publish, activate, and update with timestamp, approver UPN, governance template applied; cross-referenced change-management ticket | §4, §5, §7 |
| "Show me the queue review cadence." | Weekly (Zone 2) / daily (Zone 3) governance session minutes; Pending Requests aging report | §2.2 |
| "Show me what happens when an owner leaves." | Ownerless Agents card remediation log; Control 2.26 lifecycle workflow evidence; Control 3.6 orphaned agent remediation log | §2.3, [Control 2.26](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md), [Control 3.6](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) |

### 12.2 FINRA Rule 4511 / SEC Rules 17a-3 and 17a-4 (Books and Records)

| Examiner question | Evidence to produce | Source section |
|---|---|---|
| "Produce the inventory of all AI agents active in your firm during the examination period." | Monthly inventory exports (CSV / Excel) with ISO 8601 filenames; supplementation manifests | §3.4, §11 |
| "Demonstrate retention of these records for the required horizon." | SharePoint records-management label configuration showing 6-year WORM lock; quarterly retention attestation log | §11.3, §11.4 |
| "Produce the lifecycle history of this specific agent." | Validated source-platform audit and firm approval history; lifecycle action audit trail (Deploy / Pin / Block / Remove / Delete) | §3.3, §6 |

### 12.3 FINRA RN 24-09 / Rule 3110 (AI Tools)

| Examiner question | Evidence to produce | Source section |
|---|---|---|
| "What governance applies to your firm's AI tools?" | AI governance policy referencing this control framework; Default and Custom Governance Template definitions | §8 |
| "How do you control external data retrieval by AI tools?" | Researcher Computer Use configuration screenshot; Website Access allowlist / denylist; quarterly re-verification log | §9 |
| "How do you respond to an AI tool malfunction?" | Block action quarterly rehearsal record; incident response runbook | §6.4 |
| "Show your AI adoption metrics." | Quarterly Analytics screenshots; Active Users Over Time chart | §2.1, §10 |

### 12.4 SEC Sections 302 / 404 (SOX Internal Controls)

| Examiner question | Evidence to produce | Source section |
|---|---|---|
| "Demonstrate segregation of duties between agent authoring, approving, and operating roles." | Role-coverage CSV (§0.2); PIM activation log for any Entra Global Admin activations | §0.2, §1.1 |
| "Demonstrate that template changes follow change control." | Change-management tickets for every template edit with before/after screenshots | §8.4 |
| "Demonstrate that updates are reviewed before reaching users." | Approve Updates queue history; version diff snapshots; rejected-update records | §7 |

### 12.5 OCC Bulletin 2026-13 (Technology Risk Management)

| Examiner question | Evidence to produce | Source section |
|---|---|---|
| "Show your inventory of third-party AI agents in use." | Agents by Publisher analytics panel; Partner-publisher filtered registry view | §3.2, §10.2 |
| "Show your control framework for those third-party agents." | Custom Governance Template applied to third-party publications; Compliance Officer / Information Security Officer concurrence records | §4.5, §8.2 |
| "Show your monitoring of third-party agent operation." | Agents with exceptions view; supported Activity counts and firm-derived error-session rate; Agent run-time; validated SIEM forwarding evidence | §2.1, §2.4 |

### 12.6 NYDFS 23 NYCRR 500 (Cybersecurity)

| Examiner question | Evidence to produce | Source section |
|---|---|---|
| "Show your asset inventory for AI agents." | Monthly inventory exports | §3.4, §11 |
| "Show your access governance for AI agents." | Custom Governance Template with Entra Access Package; access review evidence (cross-reference to [Control 2.26 §5](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md)) | §8.3 |
| "Show your incident response readiness for AI agents." | Block action rehearsal record; incident response runbook | §6.4 |

!!! example "Examiner Evidence Box — Examination-Ready Bundle Composition"
    | Element | Value |
    |---|---|
    | Artifact produced | A single zipped bundle containing: most recent inventory export + manifest; role-coverage CSV; PIM activation log (prior 90 days); Default + Custom template screenshots; Researcher Computer Use configuration screenshot; quarterly governance session minutes; Block rehearsal record; analytics quarterly screenshots; cross-references to Control 1.2, 2.3, 2.8, 2.26, 3.6 evidence packs |
    | Retention duration | 6 years on Purview WORM-locked records label |
    | Regulatory mapping | All of the above |

For PowerShell automation that assembles the examination-ready bundle into a single zip, see [`./powershell-setup.md`](./powershell-setup.md). For end-to-end verification of bundle composition before examination submission, see [`./verification-testing.md`](./verification-testing.md).

---

## 13. Closing Decision Matrix — Portal vs PowerShell vs Graph

Use this matrix to decide which surface to operate for each governance task. Portal is correct for ad-hoc, low-volume, evidence-rich work; PowerShell is correct for scheduled, repeatable, scripted work; Microsoft Graph is correct for integration with the firm's broader BI / SIEM / change-management estate.

| Task | Portal | PowerShell | Microsoft Graph | Recommended primary |
|---|---|---|---|---|
| First-time tenant access validation | ✅ Best | — | — | Portal — humans validating role coverage |
| Daily Pending Requests review | ✅ Best | — | — | Portal — visual queue triage |
| Weekly governance session evidence capture | ✅ Best | — | — | Portal — screenshots and minutes |
| Bulk publish approval against an allowlist | Manual review | Not implemented | No validated mutation adapter here | Portal and firm's approval register; do not schedule the examples as delivered automation |
| Scheduled monthly inventory export | Manual export | Adapter required | Documented package API is not the complete firm inventory schema | Portal export plus coverage reconciliation |
| Inventory export supplementation (filling Microsoft-omitted columns) | Approved supplemental records | Adapter required | Feature-specific coverage must be validated | No universal Graph completeness fallback |
| Incident-driven Block of an agent | Primary | No validated fallback here | — | Portal action plus host-specific read-back |
| Quarterly Default Governance Template composition verification | ✅ Best | — | — | Portal — visual capture of the live composition |
| Custom Governance Template authoring | ✅ Best | — | — | Portal — wizard-driven |
| Researcher Computer Use configuration | ✅ Best | — | — | Portal — single configuration page |
| Researcher Computer Use drift detection (config changed without ticket) | Manual comparison | Not implemented | No validated policy endpoint here | Capture actual configuration and approved baseline |
| SIEM forwarding of agent governance events | Source audit evidence | Connector required | No unified governance-event contract here | Validate source-to-table mapping with a known event |
| BI dashboard of governance KPIs (queue age, ownerless count, exception rate) | Manual evidence | Collector required | No unified metrics contract here | Validate each metric's scope, denominator, and provenance |
| Examination evidence bundle assembly | Approved firm process | Firm implementation requires validation | Not a native Graph pack API | Retain source records, supplements, hashes, and sign-off |

### Final readiness checklist

Before declaring this control operational, confirm all of the following:

- [ ] §0 pre-flight gates passed (tenant ID captured, roles dual-covered, Agent 365 licensed and visible).
- [ ] §1 Entra Global Admin operates only via PIM with justification; AI Administrator is the daily operator.
- [ ] §2 governance card review cadence and SLAs documented in the firm's WSPs.
- [ ] §3 Agent Registry exports include all required columns; supplementation manifest in place where needed.
- [ ] §4 publishing approval workflow exercised end-to-end with a Zone 2 and a Zone 3 test agent.
- [ ] §5 activation approval workflow exercised end-to-end.
- [ ] §6 Deploy / Pin / Block / Remove / Delete actions rehearsed; quarterly Block drill scheduled.
- [ ] §7 Approve Updates queue is reviewed on the documented cadence; no stale pending updates.
- [ ] §8 Default Governance Template composition verified and screenshotted; Custom templates created for Zone 3 with linked Entra Access Packages.
- [ ] §9 Researcher Computer Use configured with affirmative restrictive decision per zone; allowlist (Zone 3) maintained under change control.
- [ ] §10 Analytics review captured in the AI risk register quarterly.
- [ ] §11 Inventory exports produced monthly with ISO 8601 names, placed under Purview 6-year WORM retention.
- [ ] §12 Examination-ready bundle assembled and verified.
- [ ] Cross-references to [Control 1.2](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md), [Control 2.3](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md), [Control 2.8](../../../controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md), [Control 2.26](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md), and [Control 3.6](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) are wired into the firm's evidence pack.
- [ ] Sibling playbooks reviewed: [`./powershell-setup.md`](./powershell-setup.md), [`./verification-testing.md`](./verification-testing.md), [`./troubleshooting.md`](./troubleshooting.md).

!!! tip "What This Control Does — and Does Not — Do"
    This control **supports compliance with** the supervisory, recordkeeping, and technology risk frameworks named throughout. It **does not** by itself satisfy any single regulatory obligation. It **does not** assign a registered principal under FINRA Rule 3110, **does not** classify records under FINRA 4511, **does not** attest to internal controls under SOX §302, and **does not** substitute for the firm's Written Supervisory Procedures. Treat the Agent 365 admin center as a **control surface** that produces evidence the firm's supervisory and compliance program then evaluates and acts upon.

---

*Updated: November 2026 | Version: v1.6.2 | UI Verification Status: Needs Review (documentation verified 2026-11-09; tenant execution pending)*

*Targeted correction, #911 (2026-11-06): 2.20 scope reference only. Not a whole-page re-verification; the UI verification status above is the prior record and is unchanged.*
