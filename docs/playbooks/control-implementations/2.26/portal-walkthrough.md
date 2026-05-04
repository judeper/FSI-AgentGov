# Portal Walkthrough — Control 2.26: Entra Agent ID Identity Governance

!!! info "Post-GA Status — May 2026"
    **Microsoft Agent 365 reached general availability on May 1, 2026** and **Microsoft Entra Agent ID is generally available** as of May 2026. The pre-GA "Frontier program enrollment" gate has been replaced by **Microsoft Agent 365** (standalone per-user license) or **Microsoft 365 E7** ("Frontier Suite" — bundles E5 + Microsoft 365 Copilot + Entra Suite + Agent 365) license assignment. Where this playbook references "Frontier program" or "Frontier preview" as a gating mechanism, read it as **Microsoft Agent 365 / Microsoft 365 E7 license assignment**. Section names, anchor IDs, and PowerShell function/test names that include "Preview" or "Frontier" are retained for backward compatibility — the underlying probe logic (whether the calling principal can reach the agent identity surface) remains valid because the same observable is gated by licensing post-GA. A follow-up issue tracks the deeper structural rename.

!!! danger "READ FIRST — Scope and Sibling Routing"
    **This playbook configures identity governance for Microsoft Entra Agent IDs** — the directory objects that represent autonomous AI agents (Copilot Studio agents, Agent 365 agents, declarative agents with autonomous actions, and third-party agents registered through the Microsoft Agent Framework). It walks you through the **Microsoft Entra admin center**, **Microsoft Entra Identity Governance**, **Microsoft 365 admin center (Microsoft Agent 365 / E7 licensing)**, and **Microsoft Purview / Azure Monitor** surfaces required to satisfy Verification Criteria 1–8 of [Control 2.26](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md).

    **This walkthrough IS for:**

    | In Scope | Surface | Outcome |
    |---|---|---|
    | Enabling Entra Agent ID via Microsoft Agent 365 / M365 E7 license assignment | M365 admin center → Billing → Licenses | Agent identities blade appears in Entra |
    | Assigning sponsors (human owners of record) to every Zone 2 / Zone 3 agent | Entra → Agent identities → Properties | Zero null-sponsor agents |
    | Provisioning agent permissions through Entitlement Management access packages | Entra → Identity Governance → Entitlement management | Time-bound (≤365 day) entitlements with audit trail |
    | Configuring Lifecycle Workflows to handle sponsor departure | Entra → Identity Governance → Lifecycle workflows | Augment (not replace) Microsoft's default manager-transfer behavior |
    | Running access review campaigns scoped to agent assignments | Entra → Identity Governance → Access reviews | Quarterly attestation evidence for Z3 |
    | Forwarding agent identity events to SIEM with 6-year retention | Entra → Diagnostic settings + Azure Monitor | Examiner-ready evidence pipeline |

    **This walkthrough is NOT for:**

    | Out of Scope | Use Instead |
    |---|---|
    | Discovering and inventorying agents (the agent registry itself) | [Control 1.2 — Agent Registry and Integrated Apps Management](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md) |
    | Detecting and remediating orphaned agents whose sponsor has fully left | [Control 3.6 — Orphaned Agent Detection and Remediation](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) |
    | DLP / sensitivity-label enforcement on agent outputs | Pillar 2 data-protection controls (2.4–2.10) |
    | Conditional Access policy authoring for agent sign-ins | Control 2.1 — Conditional Access for Agents |
    | PowerShell / Microsoft Graph automation for the same surfaces | [`./powershell-setup.md`](./powershell-setup.md) |
    | Test cases, sample queries, and evidence collection scripts | [`./verification-testing.md`](./verification-testing.md) |
    | Common errors, missing blades, and remediation steps | [`./troubleshooting.md`](./troubleshooting.md) |

!!! warning "Hedged-Language Reminder"
    This playbook helps your organization **support compliance with** FINRA Rule 3110 (supervision), SEC Rule 17a-4 (records retention), SOX §404 (internal controls over financial reporting), GLBA Safeguards Rule (access controls), OCC Bulletin 2013-29 (third-party / model risk management), and Federal Reserve SR 11-7 (model risk management). It does **not** by itself guarantee any regulatory outcome. Implementation requires Microsoft Agent 365 or Microsoft 365 E7 licensing, validated change-control procedures, and independent testing by your compliance function. Organizations should verify all configurations against their own regulatory examination workpapers and legal counsel before treating these procedures as adequate evidence.

!!! info "License and Program Requirements"
    | Requirement | Why | Where to verify |
    |---|---|---|
    | Microsoft 365 Copilot license per agent sponsor | Required to author and own agents | M365 admin center → Billing → Licenses |
    | **Microsoft Agent 365 or Microsoft 365 E7 licensing** | Surfaces the **Agent identities** blade in Entra and unlocks the Agent 365 control plane (post-GA: May 1, 2026); replaces the pre-GA Frontier program enrollment | M365 admin center → Billing → Licenses |
    | Entra ID P2 (Identity Governance) | Required for Entitlement Management, Lifecycle Workflows, and Access Reviews — all three are mandatory for this control | Entra → Identity → Overview → License |
    | Microsoft Purview Audit (Standard or Premium) | Required to retain agent identity events for the 6-year SEC 17a-4 horizon | Purview → Audit → Audit retention policies |
    | Workday / SAP SuccessFactors / SAP HCM HR connector (or Azure AD Connect with HR attribute flow) | Populates `employeeLeaveDateTime` on sponsor user objects — the leaver-trigger signal source for Lifecycle Workflows | Entra → Identity → Inbound provisioning |

!!! warning "Sovereign Cloud Parity (Commercial Only)"
    As of **May 2026**, Microsoft Entra Agent ID is **generally available in the Microsoft 365 Commercial cloud only** (with Microsoft Agent 365 or Microsoft 365 E7 licensing). Agent 365 reached general availability on **May 1, 2026** in Commercial. **No GA timeline has been published for GCC, GCC High, or DoD.** If you operate in a sovereign cloud, this control's primary surface is **not available** and you must apply compensating controls. See [§1 — Sovereign Cloud Variant](#1-sovereign-cloud-variant-and-compensating-controls) below for the substitute procedure.

    | Cloud | Entra Agent ID blade | Microsoft Agent 365 / E7 licensing | Substitute approach |
    |---|---|---|---|
    | M365 Commercial | ✅ GA (May 2026) | ✅ Available | Follow this playbook end-to-end |
    | GCC | ❌ Not available | ❌ Not announced | §1 manual quarterly attestation + Control 1.2 agent registry |
    | GCC High | ❌ Not available | ❌ Not announced | §1 manual quarterly attestation + Control 1.2 agent registry |
    | DoD | ❌ Not available | ❌ Not announced | §1 manual quarterly attestation + Control 1.2 agent registry |

    See [`../../_shared/powershell-baseline.md#3-sovereign-cloud-endpoints-gcc-gcc-high-dod`](../../_shared/powershell-baseline.md#3-sovereign-cloud-endpoints-gcc-gcc-high-dod) for sovereign endpoint resolution if you ever need to script against the commercial-only surface from a sovereign management workstation.

!!! tip "Portal Navigation May Shift During Preview"
    Microsoft has restructured the Entra navigation twice in the last 12 months. If a blade name in this playbook does not match what you see, search the Entra admin center for the underlying noun ("Agent identities", "Access packages", "Lifecycle workflows") and consult the canonical documentation root at [`learn.microsoft.com/entra/agent-id/`](https://learn.microsoft.com/entra/agent-id/). Screenshot anchors in this playbook record the navigation that was verified at the **Last UI Verified** date in the control header.

---

## Document Map

| § | Section | Verification Criterion Evidenced |
|---|---|---|
| 0 | [Pre-flight Prerequisites and Triage](#0-pre-flight-prerequisites-and-triage) | All — gating checks |
| 1 | [Sovereign Cloud Variant and Compensating Controls](#1-sovereign-cloud-variant-and-compensating-controls) | All (substitute path) |
| 2 | [Frontier Program Enrollment](#2-frontier-program-enrollment) | VC-1 |
| 3 | [Sponsor Assignment in Entra Agent ID](#3-sponsor-assignment-in-entra-agent-id) | VC-2 |
| 4 | [Entitlement Management Catalog and Access Packages](#4-entitlement-management-catalog-and-access-packages) | VC-3, VC-4 |
| 5 | [Lifecycle Workflow for Sponsor Departure](#5-lifecycle-workflow-for-sponsor-departure) | VC-5 |
| 6 | [Access Review Campaigns for Agent Assignments](#6-access-review-campaigns-for-agent-assignments) | VC-6 |
| 7 | [Diagnostic Settings and SIEM Forwarding](#7-diagnostic-settings-and-siem-forwarding) | VC-7, VC-8 |
| 8 | [HR Connector Verification (`employeeLeaveDateTime`)](#8-hr-connector-verification-employeeleavedatetime) | VC-5 (signal source) |
| ★ | [Closing Decision Matrix — Portal vs PowerShell vs Graph](#closing-decision-matrix-portal-vs-powershell-vs-graph) | Operational reference |

---

## 0. Pre-flight Prerequisites and Triage

Before you click anything in any portal, run through this gate. Skipping a gate produces silent failures later — for example, the **Agent identities** blade simply will not appear if the tenant is not Frontier-enrolled, and the wrong role will let you read but not modify access packages.

### 0.1 Confirm tenant cloud and tenant ID

1. Sign in to [`https://entra.microsoft.com`](https://entra.microsoft.com) as an account that holds at least the **Entra Identity Governance Admin** role.
2. In the upper-right corner, click your profile photo → **Switch directory** if you are a multi-tenant operator. Confirm you are in the tenant you intend to govern.
3. Navigate to **Identity → Overview** and capture the **Tenant ID** GUID and the **Primary domain** (e.g., `contoso.onmicrosoft.com`). Record both in your runbook.
4. In the left blade, scroll to **Identity → Settings → Tenant properties** and confirm the **Country or region** matches the regulated entity. For US broker-dealers and banks, this is typically `United States`.

*Screenshot anchor: `docs/images/2.26/EXPECTED.md#0-1-tenant-overview` — Entra overview blade showing Tenant ID, Primary domain, and Country.*

!!! warning "Tenant Cloud Detection"
    If the URL bar shows `entra.microsoft.us` (GCC High / DoD) or you authenticate against `login.microsoftonline.us`, **stop here and jump to [§1](#1-sovereign-cloud-variant-and-compensating-controls)**. Continuing this playbook in a sovereign tenant will fail at §2 because the Frontier program is not offered in `*.us` clouds as of the verification date.

### 0.2 Confirm role assignments

| Role | Required for | Where to assign |
|---|---|---|
| **Entra Global Admin** (or **Entra Privileged Role Admin**) | One-time Frontier opt-in (§2) and initial Lifecycle Workflow template enablement (§5) | Entra → Roles & admins |
| **Entra Identity Governance Admin** | Entitlement Management catalogs, access packages, access reviews, lifecycle workflow authoring (§4–§6) | Entra → Roles & admins |
| **Entra Agent ID Admin** (preview role) | Read/write on agent identity properties including sponsor assignment (§3) | Entra → Roles & admins (filter to "Agent") |
| **AI Administrator** | Cross-surface read on Copilot agents in M365 admin center | M365 admin center → Roles |
| **Entra Security Admin** | Diagnostic settings authoring (§7) | Entra → Roles & admins |
| **Purview Compliance Admin** | Audit retention policy authoring (§7 long-term retention path) | Purview → Roles & scopes |

1. In Entra, navigate to **Identity → Roles & admins → Roles**.
2. Search for each role above and click into it. Confirm at minimum **two named human accounts** (no service principals, no break-glass) hold each role per FINRA dual-control expectations.
3. If any role shows zero or one assignee, open a ticket with your Entra owner before proceeding — single-person admin coverage on identity governance roles is itself an audit finding.

*Screenshot anchor: `docs/images/2.26/EXPECTED.md#0-2-role-assignments` — Roles & admins grid filtered to "Agent" and "Identity Governance".*

!!! example "Examiner Evidence Box — Role Coverage"
    | Element | Value |
    |---|---|
    | Artifact produced | CSV export of `directoryRole` membership for each governance role (PIM-aware if PIM is in use) |
    | Retention duration | 6 years (SEC 17a-4) |
    | Regulatory mapping | FINRA 3110 (supervision — dual control), SOX §404 (segregation of duties) |

### 0.3 Confirm licensing and Frontier enrollment status

1. Open [`https://admin.microsoft.com`](https://admin.microsoft.com) → **Billing → Licenses**.
2. Confirm the count of **Microsoft 365 Copilot** licenses is greater than zero and that licenses are assigned to the human accounts who will sponsor agents.
3. Navigate to **Setup → Microsoft 365 Frontier** (some tenants surface this as **"Get early access to Microsoft 365 features"** under **Setup → Organizational settings**).
4. Capture the current state:
   - **Not enrolled** → proceed to [§2](#2-frontier-program-enrollment) to enroll.
   - **Enrolled — pending propagation** → expect up to 24 hours before the Agent identities blade appears in Entra.
   - **Enrolled — active** → skip §2 and start at [§3](#3-sponsor-assignment-in-entra-agent-id).

*Screenshot anchor: `docs/images/2.26/EXPECTED.md#0-3-frontier-status` — M365 admin Setup page showing Frontier enrollment toggle state.*

### 0.4 Pre-flight gate summary

Do not proceed past this section unless **all** of the following are true:

- [ ] You are signed in to the correct tenant and have captured the tenant ID.
- [ ] Tenant is in M365 Commercial cloud (or you have switched to §1 sovereign path).
- [ ] At least two named humans hold each governance role in §0.2.
- [ ] Microsoft 365 Copilot licenses are assigned to intended sponsors.
- [ ] Frontier enrollment status is recorded.
- [ ] Entra ID P2 license is active on the tenant (Identity → Overview → License shows P2).
- [ ] An HR connector or HR-attribute provisioning path populates `employeeLeaveDateTime` on user objects (verify in [§8](#8-hr-connector-verification-employeeleavedatetime) before relying on Lifecycle Workflows).

!!! tip "If a Gate Fails"
    Open [`./troubleshooting.md`](./troubleshooting.md) and search for the gate name (e.g., "Frontier enrollment pending"). Do not attempt workarounds in production until the gate clears — most workarounds for missing licensing or roles create their own audit findings.

---

## 1. Sovereign Cloud Variant and Compensating Controls

**Audience:** Operators in M365 GCC, GCC High, or DoD tenants. Skip this section if you are in M365 Commercial.

As of the verification date, **Microsoft Entra Agent ID is not available in any US sovereign cloud**. Microsoft has not committed to a sovereign GA timeline. Until parity arrives, sovereign-cloud organizations cannot rely on the directory-resident agent identity, sponsor attribute, or access package surfaces described in §3–§7. Examiners (FFIEC IT Handbook, OCC Heightened Standards) will still expect equivalent governance evidence. The substitute is a **manual quarterly attestation pattern** anchored on the agent registry from Control 1.2.

### 1.1 Manual quarterly sponsor attestation

1. Pull the agent registry CSV produced by [Control 1.2 — Agent Registry](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md). The registry must include `agent_id`, `agent_display_name`, `zone`, `sponsor_upn`, `sponsor_manager_upn`, and `last_attested_date`.
2. Distribute the registry to each sponsor of record via a Purview-labeled (Confidential / Internal) attestation workbook. SharePoint list with retention label achieves the same outcome.
3. Sponsors confirm in writing (Forms response, signed PDF, or Power Automate approval task) that:
   - They still own the agent.
   - The agent's listed permissions remain necessary.
   - No undisclosed third-party agents are operating under their sponsorship.
4. Compliance archives signed attestations to a Purview-immutable location (records management label with retention `6 years` and locked policy).
5. Any agent without a returned attestation within 14 days of the campaign deadline is treated as **orphaned** and routed through [Control 3.6](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) for disable-or-delete.

*Screenshot anchor: `docs/images/2.26/EXPECTED.md#1-1-sovereign-attestation-workbook` — sample SharePoint attestation list with retention label applied.*

!!! example "Examiner Evidence Box — Sovereign Manual Attestation"
    | Element | Value |
    |---|---|
    | Artifact produced | Quarterly attestation CSV + signed sponsor responses + non-response remediation log |
    | Retention duration | 6 years (SEC 17a-4) on Purview record label |
    | Regulatory mapping | FINRA 3110, OCC Bulletin 2013-29 (third-party / model risk), FFIEC IT Handbook (governance) |

### 1.2 Compensating control mapping

| Commercial-only surface | Sovereign substitute | Residual risk |
|---|---|---|
| Entra Agent ID `sponsor` attribute | Agent registry `sponsor_upn` column attested quarterly | Manual data drift between attestations |
| Entitlement Management access packages for agents | Existing entitlement management for **human owner** + governed security group containing agent service principal | No native agent-identity time-bound assignment; rely on group expiration + scripted revocation |
| Lifecycle Workflows (sponsor leaver) | HR feed → Power Automate flow that emails compliance + disables agent's owning service principal | Detection latency (1–24 hours typical) |
| Access reviews scoped to agent assignments | Access reviews scoped to the governed security groups, with reviewer guidance to enumerate underlying agents | Reviewer cognitive load — risk of rubber-stamp approvals |
| Diagnostic categories surfacing `AgentIdentity*` events | `ApplicationManagement` + `UserManagement` Entra audit categories filtered downstream by service principal display-name pattern (e.g., `agent-*`) | Imperfect filter; requires display-name discipline |

### 1.3 When sovereign parity arrives

When Microsoft announces Agent ID GA for your sovereign cloud, do **not** silently switch over. Treat parity arrival as a controlled change: dual-run §3–§7 alongside the §1 manual procedure for at least one full quarter, reconcile the two sources, and obtain compliance sign-off before retiring the manual attestation. Document the cutover in your change-management system per Control 2.16.

---

<a id="2-frontier-program-enrollment"></a>

## 2. Microsoft Agent 365 / Microsoft 365 E7 License Assignment

**Verification Criterion evidenced:** VC-1 (Entra Agent ID enabled; **Agent identities** blade present in Entra).

Post-GA (May 2026), the Entra Agent ID surface is gated by **Microsoft Agent 365** (standalone per-user license) or **Microsoft 365 E7** ("Frontier Suite") licensing. Pre-GA this surface was gated by enrolment in the Microsoft Frontier early-access program; section numbering and anchor (`#2-microsoft-agent-365-microsoft-365-e7-license-assignment`) is preserved across the GA cutover. Verify the exact SKU part numbers available in your tenant via `Get-MgSubscribedSku` before assigning licenses at scale.

!!! danger "Tenant-Wide License Decisions"
    License assignment to Microsoft Agent 365 or Microsoft 365 E7 unlocks Agent ID and the broader Agent 365 surface for the assigned user. Coordinate with your finance, procurement, identity, and Copilot product owners before assignment at scale. Some Agent 365 surfaces still carry adjacent Public Preview labels — verify current GA / preview status against Microsoft Learn before relying on a specific surface in production. License changes should be approved through your standard change-control board.

### 2.1 Confirm tenant has Agent 365 or M365 E7 SKUs available

1. Sign in to [`https://admin.microsoft.com`](https://admin.microsoft.com) as **Entra Global Admin** or **Billing Administrator**.
2. In the left navigation, expand **Billing**, then click **Your products**.
3. Search for **Microsoft Agent 365** or **Microsoft 365 E7**. If neither is listed, work with your Microsoft account team to procure the appropriate SKU for your governance scenario (see Control 2.26 §1 license selection guidance).
4. Capture the resulting SKU list (SKU part number, total seats, assigned seats) — this is the baseline for license-coverage evidence in §9.

*Screenshot anchor: `docs/images/2.26/EXPECTED.md#2-1-license-skus-available` — M365 admin Billing → Your products page showing Microsoft Agent 365 or Microsoft 365 E7 SKU with available seats.*

### 2.2 Assign licenses to the Agent ID administrator(s)

1. From the M365 admin center, navigate to **Users → Active users**.
2. Select the user(s) who will administer Entra Agent ID (typically members of the **Entra Agent ID Admin** or **AI Administrator** role groups).
3. On the user's profile, click **Licenses and apps**.
4. Check the box for **Microsoft Agent 365** (or **Microsoft 365 E7** if the suite is being used). Optionally adjust per-app enablement under the SKU expansion.
5. Click **Save changes**.
6. Repeat for each Agent ID administrator. License-based access can also be group-based — see §2.3 for the recommended group-based pattern at scale.

*Screenshot anchor: `docs/images/2.26/EXPECTED.md#2-2-license-assigned` — M365 admin Licenses and apps page showing Microsoft Agent 365 or Microsoft 365 E7 enabled for an admin user.*

### 2.3 Verify the Agent identities blade is reachable

1. Wait at least 15 minutes after license assignment, then sign in to [`https://entra.microsoft.com`](https://entra.microsoft.com) as the licensed administrator.
2. In the left blade, navigate to **Identity → Applications**. Scroll the sub-blades — you should now see **Agent identities** as a sibling of **Enterprise applications** and **App registrations**. The blade may still carry an "(preview)" suffix on some assignment-policy toggles even though the core surface is GA — verify against Microsoft Learn for the exact label in current builds.
3. Click **Agent identities**. The blade should load without an "access denied" or "feature not available" banner. An empty list at this point is expected — agents will populate after sponsors begin authoring them.
4. If after 60 minutes the blade still does not render correctly:
   - Confirm the operator account holds Microsoft Agent 365 or Microsoft 365 E7 licensing **directly** (group-based works) — see Control 2.26 troubleshooting playbook §2.
   - Confirm the operator holds the **Entra Agent ID Admin** or **AI Administrator** directory role (RBAC gap is a common false-positive for "blade missing").
   - Confirm tenant region is one in which Agent ID GA has been announced (Commercial cloud at GA; verify sovereign availability against Microsoft Learn).
   - Open a Microsoft support case via M365 admin → **Support → New service request**, category **Microsoft Entra → Agent ID**.

*Screenshot anchor: `docs/images/2.26/EXPECTED.md#2-3-agent-identities-blade-empty` — Entra Agent identities blade with empty list, demonstrating successful access.*

### 2.4 Capture license assignment evidence

1. From the M365 admin **Billing → Licenses** page, capture a full-page screenshot showing the Microsoft Agent 365 / M365 E7 SKU, the assigned seat count, and the date range.
2. From the M365 audit log (Purview → Audit), search for the activity **"Add user license"** with workload **AzureActiveDirectory** in the 1-hour window around the assignment timestamp. Export the JSON record.
3. Store both artifacts in your control-evidence repository under the path convention `Control-2.26/VC-1/License-Assignment/<YYYY-MM-DD>/`.

!!! example "Examiner Evidence Box — License Assignment"
    | Element | Value |
    |---|---|
    | Artifact produced | Screenshot of Frontier toggle (On) + Purview audit JSON of "Updated organization settings" event |
    | Retention duration | 6 years (SEC 17a-4); audit JSON inherits Purview audit retention policy |
    | Regulatory mapping | FINRA 3110 (supervisory system change-control), SOX §404 (IT general controls — change management) |

!!! tip "Cross-Reference"
    The PowerShell equivalent of the verification step (querying for the existence of agent identity service principals via Microsoft Graph) is documented at [`./powershell-setup.md`](./powershell-setup.md). For symptoms like "blade visible but throws 403", see [`./troubleshooting.md`](./troubleshooting.md).

---

## 3. Sponsor Assignment in Entra Agent ID

**Verification Criterion evidenced:** VC-2 (every Zone 2 / Zone 3 agent has a non-null sponsor of record).

Every agent identity in your tenant must have a **named human sponsor** who is accountable for the agent's continued business justification, permission scope, and lifecycle decisions. Microsoft auto-populates the sponsor attribute with the **creating user** at agent provisioning time — so for newly-authored agents, the sponsor field is rarely null. The risk is **inherited or imported** agents (Copilot Studio agents migrated from Power Platform tenants, third-party agents registered via Microsoft Agent Framework, or agents whose original creator left before this control was implemented).

### 3.1 Inventory current sponsor coverage

1. Sign in to [`https://entra.microsoft.com`](https://entra.microsoft.com) as **Entra Agent ID Admin** or **Entra Identity Governance Admin**.
2. Navigate to **Identity → Applications → Agent identities (preview)**.
3. In the column chooser (gear icon, upper-right of the grid), enable the columns: **Display name**, **Application ID**, **Created date**, **Sponsor (UPN)**, **Sponsor manager (UPN)**, **Zone tag**, **Last sign-in**.
4. Sort by **Sponsor (UPN)** ascending. Empty cells will float to the top — these are your null-sponsor population.
5. Click **Download** (top of grid) → **CSV**. Save as `agent-sponsor-inventory-<YYYY-MM-DD>.csv`.

*Screenshot anchor: `docs/images/2.26/EXPECTED.md#3-1-agent-identities-grid-sorted` — Agent identities grid sorted by Sponsor with null entries visible.*

### 3.2 Resolve null sponsors

For each row with an empty Sponsor (UPN):

1. Click the agent's display name to open its properties blade.
2. Review **Created by** (often a service principal for migrated agents) and **Owners** (group or user). Use these signals to identify the human accountable today.
3. If a clear human owner exists:
   - Click **Properties → Edit**.
   - In the **Sponsor** field, type the UPN of the human owner. The picker validates against Entra users and rejects guests, service principals, and disabled accounts.
   - Click **Save**. The audit log records the change with `actor`, `before`, and `after` values.
4. If no clear human owner can be identified, follow the orphan-remediation procedure in [Control 3.6](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md). Do not assign a placeholder or shared mailbox as sponsor — examiners will treat that as a null sponsor.

*Screenshot anchor: `docs/images/2.26/EXPECTED.md#3-2-edit-sponsor-dialog` — Agent properties Edit pane with Sponsor picker validating a UPN.*

!!! warning "Manager-of-Record Verification"
    The Lifecycle Workflow in §5 fires when the **sponsor's manager** changes or the sponsor leaves. After assigning a sponsor, immediately verify that the sponsor user's `manager` attribute in Entra is populated and points to a current employee. A sponsor with no manager will not trigger leaver workflows correctly. Verify in **Identity → Users → [sponsor] → Edit properties → Job info → Manager**.

### 3.3 Apply zone tags

Zone tagging is the foundation for the Zone 2 / Zone 3 differentiated controls in §4–§6. The tag lives on the agent identity object as the `extensionAttribute_zone` custom property (or, where the preview surface exposes a first-class field, as **Zone**).

1. From the agent properties blade, click **Properties → Edit**.
2. Set **Zone** to one of `Z1-Personal`, `Z2-Team`, or `Z3-Enterprise` per the criteria in the [Framework — Agent Zones](../../../framework/zones-and-tiers.md) page.
3. Save. Repeat for every agent. The bulk-update PowerShell equivalent is documented at [`./powershell-setup.md`](./powershell-setup.md) — for tenants with more than ~50 agents, prefer the bulk path.

### 3.4 Verify zero null sponsors on Z2 / Z3

1. Re-export the CSV from §3.1.
2. Filter to rows where `Zone tag` is `Z2-Team` or `Z3-Enterprise`.
3. Confirm that every row in the filtered set has a populated `Sponsor (UPN)` value. The expected count of null sponsors in Z2/Z3 is **zero**.
4. If any null remains, return to §3.2.

!!! example "Examiner Evidence Box — Sponsor Coverage"
    | Element | Value |
    |---|---|
    | Artifact produced | Two CSVs: pre-remediation (showing nulls) and post-remediation (showing zero nulls in Z2/Z3) + Purview audit log of `Update agent identity` events |
    | Retention duration | 6 years (SEC 17a-4) |
    | Regulatory mapping | FINRA 3110 (named supervisor for each business activity), SR 11-7 (model owner identification), GLBA Safeguards (access accountability) |

!!! tip "Cross-Reference"
    The Graph API path for sponsor assignment is `PATCH /agentIdentities/{id}` with the `sponsor` and `manager` properties — see [`./powershell-setup.md`](./powershell-setup.md). For "sponsor field grayed out", see [`./troubleshooting.md`](./troubleshooting.md).

---

## 4. Entitlement Management Catalog and Access Packages

**Verification Criteria evidenced:** VC-3 (Z3 agents receive resources only via access packages) and VC-4 (time-bound assignments ≤365 days; no perpetual Z3 assignments).

This section is the operational heart of Control 2.26. You will:

1. Create a dedicated **Entitlement Management catalog** for agent-targeted access packages.
2. Add the resource types that access packages can grant to agents — **security groups, Microsoft Graph application permissions, and Entra directory roles**. (Access packages **cannot** assign SharePoint sites, Teams, or Power Platform environments **directly to agents** — for those resources, use a security group as the indirection layer.)
3. Author one access package per logical permission bundle, with a Z3-appropriate assignment policy: **time-bound (≤365 days), approval-required, scoped to "All agents (preview)"**.

!!! danger "What Access Packages Can and Cannot Assign to Agents"
    | Resource type | Direct assignment to agent? | Workaround if not |
    |---|---|---|
    | Security group (assignable / mail-disabled) | ✅ Yes | — |
    | Microsoft Graph application permission (e.g., `Sites.Selected`) | ✅ Yes | — |
    | Entra directory role (e.g., `Reports Reader`) | ✅ Yes | — |
    | SharePoint site | ❌ No | Grant via `Sites.Selected` Graph permission + site-scoped permission, or via SharePoint-permitted security group |
    | Teams team | ❌ No | Grant via security group that is a member of the Team |
    | Power Platform environment | ❌ No | Use environment security group + Power Platform Admin Center role |
    | Azure subscription role | ❌ No | Use Azure Privileged Identity Management separately |

### 4.1 Create the agent governance catalog

1. Sign in to [`https://entra.microsoft.com`](https://entra.microsoft.com) as **Entra Identity Governance Admin**.
2. Navigate to **Identity governance → Entitlement management → Catalogs**.
3. Click **+ New catalog**.
4. Set:
   - **Name:** `Agent Governance — Z2 Z3`
   - **Description:** `Catalog for access packages targeting Entra Agent ID identities. Owned by AI Governance Lead. Catalog scope: Z2 and Z3 agents per Control 2.26.`
   - **Enabled:** Yes
   - **Enabled for external users:** No (agents are tenant-internal)
5. Click **Create**.
6. Open the new catalog → **Roles and administrators** → **+ Add catalog owner**. Add at minimum:
   - The **AI Governance Lead** functional account (or the named individual currently in that role).
   - A backup catalog owner from your Identity Governance team.
7. Add a **Catalog reader** assignment for your **Compliance Officer** so they can pull evidence without write access.

*Screenshot anchor: `docs/images/2.26/EXPECTED.md#4-1-catalog-created` — Catalogs grid showing the Agent Governance catalog with two owners and one reader.*

### 4.2 Add resources to the catalog

For each resource you intend to grant to agents:

1. From the catalog, click **Resources → + Add resources**.
2. Choose the resource type (**Groups and Teams**, **Applications**, or **Roles**).
3. Search and select the specific resource. Examples:
   - Security group `sg-agent-sales-data-readers`
   - Application permission `Sites.Selected` on `Microsoft Graph`
   - Directory role `Reports Reader` (read-only)
4. Click **Add**.

Repeat until all resources required by your planned access packages are present in the catalog. Resources outside the catalog cannot be added to its access packages.

!!! warning "Least Privilege Discipline"
    Resist the temptation to add high-blast-radius resources (e.g., `Mail.ReadWrite.All`, `Files.ReadWrite.All`) to the agent governance catalog "just in case." Catalog membership itself is an inventory examiners will request. Resources should be added only when a specific access package needs them, and removed when no longer used.

### 4.3 Author an agent access package

The example below provisions a Z3-appropriate package granting an agent read-only access to a curated SharePoint document library via `Sites.Selected`.

1. From the catalog, click **Access packages → + New access package**.
2. **Basics** tab:
   - **Name:** `AP-Z3-Sales-Library-Reader`
   - **Description:** `Read-only access to the Sales Reference Library via Sites.Selected. Z3 agents only. Sponsor approval + AI Governance Lead approval required.`
   - **Catalog:** `Agent Governance — Z2 Z3` (pre-selected)
3. **Resource roles** tab:
   - Add the `Sites.Selected` application permission.
   - Add the `sg-sharepoint-sales-library-readers` security group (which itself has read on the SharePoint site — this provides the indirection layer).
4. **Requests** tab — this is where you scope the package to agents:
   - **Users who can request access:** Select **For users, service principals, and agent identities in your directory**.
   - In the picker, choose **All agents (preview)**. This special-purpose principal scopes the package to any agent identity in the tenant, not all users.
   - **Require approval:** Yes.
   - **Stages:** Stage 1 — **Sponsor of the requesting agent** (uses the sponsor attribute set in §3). Stage 2 — **AI Governance Lead** (group-based approver).
   - **Require requestor justification:** Yes.
   - **Decision must be made within:** 5 days.
5. **Requestor information** tab — add custom questions:
   - "Confirm the business case ID associated with this request."
   - "Confirm the data classification of records the agent will access."
6. **Lifecycle** tab — **this is the time-bound enforcement step**:
   - **Expiration:** **On date** or **Number of days** — set to a value ≤ **365 days**. For Z3, the recommended ceiling is **180 days** (semi-annual renewal); the absolute maximum permitted by Control 2.26 is **365 days**.
   - **Allow users to extend access:** Yes, but require approval for extensions. Extensions reset the clock to no more than 365 days from the extension date.
   - **Require access reviews:** Yes (this links to §6).
7. **Review + Create** → **Create**.

*Screenshot anchor: `docs/images/2.26/EXPECTED.md#4-3-access-package-lifecycle-tab` — Lifecycle tab showing 180-day expiration and access-review linkage.*

!!! danger "No Perpetual Z3 Assignments"
    The portal allows **No expiration** as an option on the Lifecycle tab. **Never select this for a Z3 access package.** Selection of "No expiration" on a Z3 package is a Control 2.26 violation that auditors will flag immediately. The PowerShell verification script at [`./verification-testing.md`](./verification-testing.md) enumerates all Z3-tagged packages and fails if any has `expirationType = noExpiration`.

### 4.4 Apply the assignment policy to in-flight agents

Newly-created access packages have no assignments. Sponsors must request them on behalf of their agents:

1. The sponsor signs in to [`https://myaccess.microsoft.com`](https://myaccess.microsoft.com).
2. Selects **Request on behalf of → Agent identity**, picks the agent, and requests the package.
3. The approval chain executes (sponsor → AI Governance Lead).
4. On approval, the agent receives the resource grant. The assignment carries an `expiredDateTime` derived from the lifecycle policy.

For agents that already had ad-hoc resource grants outside access packages, run the **migration to access packages** procedure in [`./powershell-setup.md`](./powershell-setup.md). Do not leave dual-path assignments in place — they confuse access reviews.

### 4.5 Verify VC-3 and VC-4

1. From the catalog → **Access packages**, confirm at least one access package exists per logical Z2/Z3 permission bundle.
2. Open each Z3 package → **Lifecycle** → confirm **Expiration** is set to a number of days ≤ 365 (preferably ≤ 180).
3. Open each Z3 package → **Assignments**, filter to **Active**, and confirm every active assignment shows a non-empty **Expiration date**.
4. From **Identity governance → Entitlement management → Reports → Access package assignments**, export the report scoped to your catalog. The exported CSV must show no row with empty `expiredDateTime` for Z3 assignments.

!!! example "Examiner Evidence Box — Access Packages"
    | Element | Value |
    |---|---|
    | Artifact produced | Catalog inventory CSV + access-package configuration export (one JSON per package) + assignment report CSV |
    | Retention duration | 6 years (SEC 17a-4) |
    | Regulatory mapping | FINRA 3110 (supervisory access controls), SOX §404 (logical access — IT general controls), GLBA Safeguards (access controls), OCC 2013-29 (third-party access governance) |

!!! tip "Cross-Reference"
    Bulk creation of access packages from a JSON manifest is documented at [`./powershell-setup.md`](./powershell-setup.md). For "All agents (preview) option not visible in requestor scope picker", see [`./troubleshooting.md`](./troubleshooting.md).

---

## 5. Lifecycle Workflow for Sponsor Departure

**Verification Criterion evidenced:** VC-5 (lifecycle workflow active for sponsor departure with execution evidence).

### 5.1 Understand Microsoft's default behavior first

Before authoring any custom lifecycle workflow, internalize this critical fact:

!!! danger "Microsoft Already Auto-Transfers Sponsorship by Default"
    When a user with `employeeLeaveDateTime` set in the past is processed by Entra, **Microsoft automatically transfers ownership of any agent identities they sponsor to that user's `manager`**. Your Lifecycle Workflow does **not** replace this behavior — it **augments** it with FSI-required notifications, attestations, and conditional disablement. **Do not author a workflow that disables agents on sponsor departure as the default action.** That breaks legitimate business continuity and is rarely the right outcome for Z2 agents.

The recommended pattern is:

| Sponsor event | Microsoft default | This control adds |
|---|---|---|
| Sponsor `employeeLeaveDateTime` reached | Transfer sponsorship to manager | Notify AI Governance Lead + sponsor's manager + compliance; create Power Automate task for manager to attest within 14 days; if no attestation within 14 days, disable agent |
| Sponsor's `manager` attribute is null at leave time | Transfer fails silently — agent becomes orphaned | Detect orphan; route to Control 3.6 |
| Sponsor goes on extended leave (>30 days; flagged via HR custom attribute) | No action | Notify AI Governance Lead + designate temporary sponsor via access package |

### 5.2 Enable the lifecycle workflow templates

1. Sign in to [`https://entra.microsoft.com`](https://entra.microsoft.com) as **Entra Identity Governance Admin**.
2. Navigate to **Identity governance → Lifecycle workflows → Workflows**.
3. Confirm the **Workflows** blade loads. (Lifecycle Workflows requires Entra ID Governance, included in P2 — verify via **Identity → Overview → License**.)
4. Click **+ Create a custom workflow** (or start from the **Pre-hire**, **Joiner**, **Mover**, **Leaver** templates and customize). For sponsor-departure governance, the **Leaver** workflow type is the correct base.

### 5.3 Author the "Agent Sponsor Leaver" workflow

1. **Basics** tab:
   - **Workflow display name:** `Agent Sponsor Leaver — Notify and Conditional Disable`
   - **Description:** `Augments Microsoft default sponsor-to-manager transfer with FSI notifications, manager attestation, and 14-day conditional disable. Implements Control 2.26 VC-5.`
   - **Workflow category:** Leaver
2. **Trigger details** tab:
   - **Trigger type:** Group membership change → choose a dynamic security group named `sg-agent-sponsors-active` whose membership rule is `(user.userType -eq "Member") and (user.extensionAttribute_isAgentSponsor -eq "true")`. The membership rule depends on the `extensionAttribute_isAgentSponsor` attribute being set to `true` whenever a user becomes a sponsor (you can populate this attribute via the Graph hook in [`./powershell-setup.md`](./powershell-setup.md)).
   - **Trigger evaluation:** When a user **leaves** the group (i.e., loses sponsor status because their `employeeLeaveDateTime` triggers Microsoft's default transfer-to-manager).
   - Alternative trigger: **`employeeLeaveDateTime` is in the past** with a scope filter to the dynamic group above. Either trigger pattern works; the group-leave pattern is easier to test.
3. **Configure scope** tab:
   - Set the scope to the same `sg-agent-sponsors-active` group. The workflow will only fire for users in scope at the moment of trigger evaluation.
4. **Review tasks** tab — add the following tasks in order:
   - **Task 1: Send email to manager.** Built-in task `Send email to user's manager before user's last day` — customize the template to reference the agents the user sponsors and the 14-day attestation deadline.
   - **Task 2: Send email to alternate contacts.** Built-in task `Send email to user's manager about user join` (re-purposed for leaver scenario by editing the template). Add the `AI Governance Lead` distribution list and the `Compliance Officer` mailbox as alternate recipients.
   - **Task 3: Run a custom task extension.** This is the conditional disable path:
     - Create a **Logic Apps custom task extension** (Entra → Lifecycle workflows → Custom task extensions → + New custom task extension).
     - Logic App: poll a SharePoint attestation list daily for 14 days; if no attestation row exists for `(sponsor_upn = leaver, agent_id = X)` after 14 days, call Graph `PATCH /servicePrincipals/{id}` with `{ "accountEnabled": false }`; emit an event to Log Analytics.
     - Wire the custom task extension into the workflow.
   - **Task 4: Generate TAP and send via email.** Skip this task — it is not relevant for sponsor leaver.
5. **Review + Create** → **Create**.
6. After creation, click **Enable** on the workflow. Workflows in `Disabled` state do not fire.

*Screenshot anchor: `docs/images/2.26/EXPECTED.md#5-3-leaver-workflow-tasks` — Lifecycle workflow tasks tab showing the four tasks in sequence.*

!!! warning "Test in a Lower Environment First"
    Lifecycle Workflows execute against production Entra. There is no "what-if" mode that simulates the conditional disable. Test the workflow against a non-production sponsor identity (or create a test user with `employeeLeaveDateTime` set to 1 day in the past) before relying on it. Document the test in your change record.

### 5.4 Verify execution evidence

1. After at least one trigger event has occurred (test or real), navigate to **Lifecycle workflows → [your workflow] → Workflow history**.
2. Each row represents a single user whose departure triggered the workflow. Click into a row to see per-task execution status (`Completed`, `Failed`, `In progress`).
3. Export the **Workflow history** as CSV (top of grid → **Download**).
4. Cross-reference the workflow execution rows against the agent identity audit log entries (Entra → Audit logs, filter to `category = AgentIdentity`) to confirm sponsorship was transferred (or the agent was disabled, in the no-attestation path).

!!! example "Examiner Evidence Box — Lifecycle Workflow Execution"
    | Element | Value |
    |---|---|
    | Artifact produced | Workflow configuration JSON export + Workflow history CSV + correlated audit log entries showing sponsorship transfer or disable action |
    | Retention duration | 6 years (SEC 17a-4); workflow run history retained 30 days in Entra by default — forward to SIEM per §7 for long-term retention |
    | Regulatory mapping | FINRA 3110 (supervisor change-of-control), SR 11-7 (model owner transitions), SOX §404 (segregation of duties — automated control) |

!!! tip "Cross-Reference"
    The Logic Apps template for the conditional-disable custom task extension is documented at [`./powershell-setup.md`](./powershell-setup.md). For "workflow shows Failed status with permission error", see [`./troubleshooting.md`](./troubleshooting.md).

---

## 6. Access Review Campaigns for Agent Assignments

**Verification Criterion evidenced:** VC-6 (quarterly access certification campaigns completed for Z3) and VC-7 (expired assignments renewed with justification or removed within 24 hours).

### 6.1 Scope reviews to assignments, not agent objects

A common authoring error is to scope an access review at the **agent identity object** ("review whether this agent should still exist"). That is the wrong question for this control — the existence question is owned by Control 1.2. The correct scope here is **the active assignment of an access package to an agent identity**: "Should this agent still hold this entitlement?"

### 6.2 Create the quarterly Z3 access review

1. Sign in to [`https://entra.microsoft.com`](https://entra.microsoft.com) as **Entra Identity Governance Admin**.
2. Navigate to **Identity governance → Entitlement management → Access packages**.
3. For each Z3 access package, open it and click **Access reviews → + New access review**.
4. **Settings** tab:
   - **Review name:** `AR-Q[N]-<YYYY>-<package-short-name>` (e.g., `AR-Q2-2026-Sales-Library-Reader`)
   - **Description:** `Quarterly Z3 access certification per Control 2.26 VC-6.`
   - **Start date:** First business day of the quarter.
   - **Frequency:** Quarterly.
   - **Duration (in days):** 14.
   - **End:** Never (recurring).
5. **Scope** tab:
   - **Review scope:** **Active assignments to the access package**. Do not select "All users" or "Guests only" — those scopes do not include agent identities.
6. **Reviewers** tab:
   - **Select reviewers:** **Sponsor** (resolves to the sponsor attribute on the agent identity — set in §3).
   - **Fallback reviewer:** **AI Governance Lead** group (covers cases where sponsor has left and not yet been transferred).
7. **Settings** tab (advanced):
   - **Auto-apply results to resource:** **Enabled**. This is critical — without it, decisions sit in a pending state and assignments do not get revoked even when reviewers vote Deny.
   - **If reviewers don't respond:** **Remove access**. Conservative posture for Z3.
   - **Action to apply on denied users:** **Remove access**.
   - **Justification required:** **Required** for both Approve and Deny decisions.
   - **Mail notifications:** **Enabled**.
   - **Reminders:** **Enabled** (sends at 7 days and 3 days before close).
   - **Additional content for reviewer email:** Include text such as: `Per Control 2.26, you must justify continued access. Approving without justification will be flagged in the next compliance review.`
8. **Review + Create** → **Create**.

*Screenshot anchor: `docs/images/2.26/EXPECTED.md#6-2-access-review-settings` — Access review Settings tab showing auto-apply enabled, remove-on-no-response, and justification required.*

### 6.3 Monitor the campaign

1. Navigate to **Identity governance → Access reviews → Reviews**.
2. Filter to your Z3 reviews. The grid shows status per review: `NotStarted`, `InProgress`, `Completed`, `Applied`.
3. Click into an in-progress review → **Results**. Each row shows the assignment, the agent, the reviewer, the decision, and the justification.
4. Mid-campaign, export the results as CSV. Compliance can use this snapshot to nudge non-responsive reviewers.

### 6.4 Handle expired assignments — VC-7

Per VC-7, when an assignment expires (either at lifecycle end-date from §4 or via access-review denial), one of two outcomes must occur **within 24 hours**:

- **Renewal with justification.** The sponsor requests an extension via [`https://myaccess.microsoft.com`](https://myaccess.microsoft.com); the approval chain runs; the assignment is reactivated with a new `expiredDateTime`.
- **Access removed.** The assignment moves to `Expired` state and the underlying resource grant is revoked.

To verify VC-7:

1. Navigate to **Identity governance → Entitlement management → Reports → Access package assignments**.
2. Filter the report to assignments whose `expiredDateTime` falls within the last 30 days.
3. Export to CSV. For each row:
   - If `assignmentState = Expired` and the resource grant is revoked → compliant outcome.
   - If `assignmentState = Delivered` (renewed) → confirm a corresponding renewal-request audit entry with justification text exists.
   - If `assignmentState = Expired` but the resource grant persists (rare — typically a permission-propagation lag) → escalate to [`./troubleshooting.md`](./troubleshooting.md).
4. Compute the time delta between `expiredDateTime` and the actual revocation event. The 95th-percentile delta should be < 24 hours. Investigate any outliers.

*Screenshot anchor: `docs/images/2.26/EXPECTED.md#6-4-assignment-report-expired-filter` — Access package assignment report filtered to Expired in last 30 days.*

### 6.5 Apply the campaign decisions

1. When the review duration ends, status moves to `Completed`. With **Auto-apply** enabled (§6.2), Entra applies decisions automatically within ~1 hour.
2. Navigate to the completed review → **Results** → confirm every row shows `Applied: Yes`.
3. Export the **Applied results** CSV.

!!! example "Examiner Evidence Box — Access Reviews"
    | Element | Value |
    |---|---|
    | Artifact produced | One CSV per quarterly campaign per Z3 access package: review settings + reviewer decisions + justifications + applied actions; plus the 30-day expired-assignment report from §6.4 |
    | Retention duration | 6 years (SEC 17a-4) |
    | Regulatory mapping | FINRA 3110 (periodic supervisory review), SOX §404 (recertification of logical access — IT general controls), GLBA Safeguards Rule (periodic access review), SR 11-7 (periodic model access certification) |

!!! tip "Cross-Reference"
    Bulk creation of quarterly reviews via Graph is at [`./powershell-setup.md`](./powershell-setup.md). For the "auto-apply did not run" symptom, see [`./troubleshooting.md`](./troubleshooting.md).

---

## 7. Diagnostic Settings and SIEM Forwarding

**Verification Criterion evidenced:** VC-8 (lifecycle event logs forwarded to SIEM with 6-year retention).

### 7.1 Understand the category-level export model

!!! danger "Category-Level Export Only — Filter Downstream"
    Entra Diagnostic Settings export logs at the **category** level (`AuditLogs`, `SignInLogs`, `ServicePrincipalSignInLogs`, `ProvisioningLogs`, etc.). There is **no native filter** that says "only events related to agent identities." You must export the broad categories that contain agent-related events (`AuditLogs` for `category = ApplicationManagement` / `UserManagement`, `ServicePrincipalSignInLogs`, `ProvisioningLogs`) and then **filter downstream in your SIEM** by correlating object IDs against the agent identity inventory from §3.

### 7.2 Choose the destination

You typically need both:

- **Log Analytics workspace** for short-term (90 day) hot queries via Kusto.
- **Azure Storage account (immutable / WORM blob)** or a SIEM-side cold store for the 6-year SEC 17a-4 retention horizon.

Some FSIs additionally stream to **Event Hub** for real-time SIEM ingestion (Splunk, Sentinel via direct connector, QRadar). Microsoft Sentinel customers can use the Entra connector which abstracts diagnostic settings.

### 7.3 Configure the diagnostic setting

1. Sign in to [`https://entra.microsoft.com`](https://entra.microsoft.com) as **Entra Security Admin**.
2. Navigate to **Identity → Monitoring & health → Diagnostic settings**.
3. Click **+ Add diagnostic setting**.
4. **Diagnostic setting name:** `ds-agent-id-governance-evidence`.
5. **Categories** — enable at minimum:
   - `AuditLogs` — captures sponsor changes, access package configuration changes, agent identity property changes, lifecycle workflow runs.
   - `SignInLogs` — captures human sign-ins (sponsor activity context).
   - `ServicePrincipalSignInLogs` — captures agent sign-ins.
   - `ManagedIdentitySignInLogs` — relevant if any agents use managed identity backing.
   - `ProvisioningLogs` — captures HR-driven attribute changes including `employeeLeaveDateTime`.
   - `ADFSSignInLogs` — only if applicable.
   - `RiskyUsers` and `UserRiskEvents` — for sponsor risk context.
6. **Destinations:**
   - **Send to Log Analytics workspace:** select your security workspace.
   - **Archive to a storage account:** select your immutable-blob-policy storage account. Set retention to **2190 days (6 years)** in the Storage account's lifecycle policy. Note: the per-category retention slider in the diagnostic-settings blade **only governs Log Analytics retention**; storage retention is separate.
   - **Stream to an event hub:** if applicable for real-time SIEM.
7. **Save**.

*Screenshot anchor: `docs/images/2.26/EXPECTED.md#7-3-diagnostic-setting-categories` — Diagnostic setting Add page with all required categories checked and three destinations configured.*

### 7.4 Configure 6-year immutable retention on storage

1. Sign in to the [Azure portal](https://portal.azure.com) as a contributor on the storage account.
2. Navigate to the storage account → **Data management → Lifecycle management → + Add a rule**.
3. Rule name: `agent-id-governance-6yr-retain`.
4. Rule scope: filter to blob path prefix `insights-logs-auditlogs/` and the other category prefixes from §7.3.
5. Action: **Delete blobs older than 2190 days**.
6. Configure **Immutable blob storage** policy (Containers → policies) with **time-based retention of 2190 days** and **Allow protected append writes** disabled. Lock the policy after a brief verification window. **Once locked, the policy cannot be shortened — coordinate with records management before locking.**

!!! warning "Immutable Lock Is Irreversible"
    Locking an immutable retention policy is **irreversible**. Test in a non-production storage account first. The policy can be **extended** after lock but never shortened or deleted. This is the property that satisfies SEC 17a-4(f) WORM requirements.

### 7.5 Build the agent-only SIEM filter

In your SIEM (the example below uses Microsoft Sentinel KQL — adapt for Splunk SPL or QRadar AQL), define a saved query / detection that scopes broad Entra logs to agent identity activity:

```kql
let agentIds = externaldata(servicePrincipalId: string)
    [@"https://<your-storage>.blob.core.windows.net/agent-inventory/current.csv"]
    with (format="csv", ignoreFirstRecord=true);
AuditLogs
| where Category in ("ApplicationManagement", "UserManagement")
| extend targetId = tostring(TargetResources[0].id)
| where targetId in (agentIds)
| project TimeGenerated, OperationName, InitiatedBy, targetId, Result, AdditionalDetails
```

The `agent-inventory/current.csv` blob is produced nightly by the Graph export script in [`./powershell-setup.md`](./powershell-setup.md). Refresh frequency determines detection latency.

Build dashboards / alerts for at minimum:

- Sponsor change events (sponsor attribute mutated).
- Access package assignment created / expired / revoked for an agent target.
- Lifecycle workflow execution outcomes for the `Agent Sponsor Leaver` workflow.
- Agent service principal `accountEnabled` toggled.
- Failed sign-ins by agent service principals exceeding baseline.

### 7.6 Verify forwarding end-to-end

1. From a non-production sponsor account, perform a known-test event — e.g., update the description of a test agent identity in §3.
2. Wait 5–10 minutes for the Entra → Log Analytics ingestion lag.
3. In Log Analytics, run:

   ```kql
   AuditLogs
   | where TimeGenerated > ago(15m)
   | where OperationName contains "agent"
   ```

4. Confirm the test event appears.
5. Wait an additional ~1 hour and confirm the same event has landed in the storage account blob path `insights-logs-auditlogs/resourceId=/.../y=YYYY/m=MM/d=DD/h=HH/...`.

!!! example "Examiner Evidence Box — SIEM Forwarding"
    | Element | Value |
    |---|---|
    | Artifact produced | Diagnostic setting JSON export + immutable retention policy configuration screenshot + monthly attestation that storage policy remains locked at 2190 days + sample SIEM query and recent results |
    | Retention duration | 6 years (SEC 17a-4); evidence of policy lock satisfies 17a-4(f) WORM requirement |
    | Regulatory mapping | SEC Rule 17a-4(f) (records preservation — non-rewriteable, non-erasable), FINRA 4511 (general books and records), SOX §404 (audit log integrity), GLBA Safeguards (security event logging) |

!!! tip "Cross-Reference"
    The PowerShell helper to validate that the storage policy is locked at 2190 days is at [`./verification-testing.md`](./verification-testing.md). For "logs not arriving in Log Analytics", see [`./troubleshooting.md`](./troubleshooting.md).

---

## 8. HR Connector Verification employeeLeaveDateTime

**Verification Criterion supported:** VC-5 (lifecycle workflow signal source).

The Lifecycle Workflow in §5 only fires correctly if the `employeeLeaveDateTime` attribute on sponsor user objects is **populated and accurate**. That attribute is sourced from your authoritative HR system via one of three paths:

| HR system | Connector | Where to verify in Entra |
|---|---|---|
| Workday | **Workday HR → Entra ID inbound provisioning** | Identity → Inbound provisioning → Workday connector |
| SAP SuccessFactors | **SAP SuccessFactors → Entra ID inbound provisioning** | Identity → Inbound provisioning → SuccessFactors connector |
| SAP HCM (on-prem) | **SAP HCM → Entra ID via Cloud Sync agent** | Identity → Cloud sync |
| Other HRIS | Custom Graph-based provisioning to set `employeeLeaveDateTime` | Identity → Audit logs filtered to `category = ProvisioningManagement` |
| No HR feed | Manual maintenance — **not recommended for FSI** | Manual data entry creates audit findings |

### 8.1 Confirm a connector exists and is healthy

1. Sign in to [`https://entra.microsoft.com`](https://entra.microsoft.com) as **Entra Identity Governance Admin**.
2. Navigate to **Identity → Inbound provisioning** (or **Identity → Provisioning** depending on tenant nav variant).
3. Locate the connector for your HR system. Confirm:
   - **Provisioning status:** **On** (not **Paused** or **Quarantined**).
   - **Last sync:** within the last 40 minutes (Entra default sync interval is 40 min).
   - **Sync errors:** zero. Investigate any quarantine state via **Audit logs → ProvisioningManagement**.
4. Click into the connector → **Provisioning** → **Mappings** → **Provision Microsoft Entra ID Users**.
5. Confirm the attribute mapping list includes a row for `employeeLeaveDateTime` mapping from the HR system's termination-date field. If the mapping is missing, add it:
   - Click **Add new mapping**.
   - **Mapping type:** Direct.
   - **Source attribute:** the HR system's termination-date field (e.g., Workday `Termination_Date`).
   - **Target attribute:** `employeeLeaveDateTime`.
   - **Match objects using this attribute:** No.
   - **Apply this mapping:** Always.
   - **Save**.

*Screenshot anchor: `docs/images/2.26/EXPECTED.md#8-1-connector-mapping` — Provisioning attribute mapping list with `employeeLeaveDateTime` row visible.*

### 8.2 Verify population on test sponsor

1. Identify a known-departed sponsor user (or, in a test tenant, set `employeeLeaveDateTime` manually via Graph PATCH for testing only).
2. In Entra, navigate to **Identity → Users → [test sponsor] → Edit properties → Job info**.
3. Confirm the **Employee leave date time** field shows the expected value.
4. Run the Lifecycle Workflow `On-demand run` against this user (Lifecycle workflows → [your workflow] → **Run on demand** → select the user). Confirm the workflow proceeds through all configured tasks.

### 8.3 Verify population coverage across the sponsor population

1. From an Entra Identity Governance Admin context, run the Graph query in [`./powershell-setup.md`](./powershell-setup.md) which enumerates the `sg-agent-sponsors-active` group and reports the percentage with `employeeLeaveDateTime` populated (for currently-active sponsors, the value will be null — that is expected; it should populate at the moment HR records the termination).
2. Spot-check three recently-departed sponsors (within the last 90 days) — confirm each shows a non-null `employeeLeaveDateTime` and that the Lifecycle Workflow fired for each.

!!! warning "Manual `employeeLeaveDateTime` Setting Is an Audit Finding"
    Some operators discover the missing-mapping problem and "fix" it by manually setting `employeeLeaveDateTime` via Graph PATCH for known leavers. This works mechanically but is not auditable as an ongoing control — the next examiner cycle will ask "what is the source of this attribute?" and "manual" is not an acceptable answer for an FSI population. Fix the upstream HR connector mapping; do not paper over it.

!!! example "Examiner Evidence Box — HR Connector"
    | Element | Value |
    |---|---|
    | Artifact produced | Connector configuration screenshot + attribute mapping export + sample provisioning log entries showing `employeeLeaveDateTime` set events + sponsor-coverage query output |
    | Retention duration | 6 years (SEC 17a-4) |
    | Regulatory mapping | FINRA 3110 (timely supervisor change reflection), SOX §404 (HR-IT integration controls), GLBA Safeguards (timely access removal on termination) |

!!! tip "Cross-Reference"
    HR connector setup detail (initial Workday / SuccessFactors integration) is out of scope for this playbook — see [Microsoft Learn: Plan inbound user provisioning](https://learn.microsoft.com/en-us/entra/identity/app-provisioning/plan-cloud-hr-provision). For "connector quarantined" symptoms, see [`./troubleshooting.md`](./troubleshooting.md).

---

## Closing Decision Matrix — Portal vs PowerShell vs Graph

This walkthrough used the portal end-to-end for clarity and screenshot evidence. In production, most operators mix surfaces. Use this matrix to choose the right surface for each task.

| Task | Portal | PowerShell (Microsoft.Graph) | Microsoft Graph REST | Recommended for FSI |
|---|---|---|---|---|
| Frontier enrollment | ✅ Only path (admin center toggle) | ❌ | ❌ | **Portal** — one-time, requires Global Admin, change-board approved |
| Tenant role assignment audit | ✅ Roles & admins grid | ✅ `Get-MgDirectoryRoleMember` | ✅ `GET /directoryRoles/{id}/members` | **PowerShell** for scheduled audit; portal for ad-hoc |
| Inventory agent identities | ✅ Agent identities grid + CSV export | ✅ `Get-MgServicePrincipal -Filter "tags/any(t:t eq 'AgentIdentity')"` | ✅ `GET /agentIdentities` (preview) | **PowerShell** for repeatability; portal for ad-hoc spot-check |
| Bulk sponsor assignment (>10 agents) | ❌ One-at-a-time | ✅ Loop `Update-MgServicePrincipal` | ✅ `PATCH /agentIdentities/{id}` | **PowerShell** — portal does not scale |
| Single sponsor change with audit trail visibility | ✅ | ✅ | ✅ | **Portal** — change visible in audit log identically; portal preferred for ceremonial single edits |
| Catalog creation | ✅ | ✅ `New-MgEntitlementManagementAccessPackageCatalog` | ✅ `POST /identityGovernance/entitlementManagement/catalogs` | **Portal** for the initial catalog; **PowerShell** for cross-tenant replication |
| Access package creation (one) | ✅ | ✅ | ✅ | **Portal** — author with the wizard, then export JSON for tenant promotion |
| Access package creation (many, IaC) | ❌ | ✅ Bulk script | ✅ | **PowerShell / Graph** with JSON manifests under source control |
| Lifecycle Workflow authoring | ✅ Wizard | ✅ `New-MgIdentityGovernanceLifecycleWorkflow` | ✅ `POST /identityGovernance/lifecycleWorkflows/workflows` | **Portal** for initial design; **PowerShell** for promotion across tenants |
| Lifecycle Workflow on-demand test run | ✅ | ✅ | ✅ | **Portal** — easier visibility into per-task status |
| Access review creation | ✅ | ✅ `New-MgIdentityGovernanceAccessReviewDefinition` | ✅ | **PowerShell** for the standing quarterly schedule across many packages; portal for one-off |
| Access review results extraction | ✅ CSV download | ✅ `Get-MgIdentityGovernanceAccessReviewDefinitionInstance` | ✅ | **PowerShell** for evidence pipeline; portal for human review |
| Diagnostic settings | ✅ | ✅ `New-AzDiagnosticSetting` (Az module) | ✅ Azure REST | **Portal** for initial; **PowerShell** for IaC parity |
| Storage immutable retention | ✅ | ✅ Az.Storage cmdlets | ✅ | **Portal** — locking is irreversible; ceremonial portal action with witness recommended |
| HR connector status check | ✅ | ✅ `Get-MgServicePrincipalSynchronizationJob` | ✅ | **Portal** — health UI is best-in-class |
| Daily evidence export to SIEM | ❌ | ✅ Scheduled Azure Automation runbook | ✅ | **PowerShell** in Azure Automation — see [`./powershell-setup.md`](./powershell-setup.md) |

### When to escalate to Microsoft support

Open a Microsoft service request (M365 admin → Support → New service request) for:

- **Frontier enrollment fails or remains in pending state >24 hours.** Category: Microsoft Entra → Preview features.
- **Agent identities blade returns 403 despite Frontier-enrolled, P2-licensed, and Identity Governance Admin role.** Category: Microsoft Entra → Identity Governance.
- **`employeeLeaveDateTime` does not surface even after HR connector mapping is added and a sync cycle completes.** Category: Microsoft Entra → Provisioning.
- **Lifecycle workflow custom task extension Logic App returns persistent permission errors against `/servicePrincipals/{id}` PATCH.** Category: Microsoft Graph → Permissions.
- **Diagnostic setting save returns "destination not found" despite valid Log Analytics workspace selection.** Category: Azure Monitor → Diagnostic settings.

### Final readiness checklist

Before declaring Control 2.26 implemented, confirm:

- [ ] §0 pre-flight gates all pass.
- [ ] §1 sovereign variant followed if applicable, OR §2–§8 fully completed for Commercial.
- [ ] §2 Frontier enrollment evidence captured (toggle screenshot + audit JSON).
- [ ] §3 zero null sponsors on Z2/Z3 agents (re-export CSV proves it).
- [ ] §4 every Z3 access package has expiration ≤ 365 days; no `noExpiration` policies; "All agents (preview)" used as requestor scope.
- [ ] §5 Lifecycle Workflow `Agent Sponsor Leaver` exists, is Enabled, and has at least one successful test run in workflow history.
- [ ] §6 quarterly access review configured per Z3 access package with auto-apply, justification-required, and remove-on-no-response.
- [ ] §7 diagnostic setting writes to Log Analytics + immutable storage with 2190-day locked retention; SIEM filter validated end-to-end.
- [ ] §8 HR connector populates `employeeLeaveDateTime`; spot-check passes for three recently-departed sponsors.
- [ ] All Examiner Evidence Box artifacts collected and stored under `Control-2.26/VC-N/` paths.
- [ ] Sibling playbooks reviewed: [`./powershell-setup.md`](./powershell-setup.md), [`./verification-testing.md`](./verification-testing.md), [`./troubleshooting.md`](./troubleshooting.md).

---

*Updated: April 2026 | Version: v1.0.0 | UI Verification Status: Verified against Entra admin center navigation as of April 2026 (Frontier preview). Portal navigation may shift during preview; consult `learn.microsoft.com/entra/agent-id/` if blade names diverge.*









