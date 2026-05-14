# Portal Walkthrough — Control 2.1: Managed Environments

!!! danger "READ FIRST — Scope, Non-Substitution, and Sibling Routing"
    **This playbook configures Power Platform Managed Environments** — the premium governance substrate that enables sharing limits, solution-checker enforcement, IP firewall, IP-based cookie binding, Customer Lockbox, Customer-Managed Keys, maker welcome content, the weekly usage-insights digest, and tenant isolation for an environment or a group of environments. It walks you through the **Power Platform Admin Center (PPAC)** at [`https://admin.powerplatform.microsoft.com`](https://admin.powerplatform.microsoft.com) and the complementary **Microsoft 365 admin center → Agent 365** governance surface for agents that originate in Copilot Studio and surface in Microsoft 365 Copilot.

    **Managed Environments are an enforcement substrate, not a governance program.** They do **NOT** replace:

    - **Model-risk governance** required by OCC Bulletin 2011-12 and Federal Reserve SR 11-7 — see [Control 2.6](../../../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md). A Managed Environment toggle is not an independent model validation.
    - **Supervisory review by an appropriately registered principal** required by FINRA Rule 3110 — see [Control 2.12](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md). Solution-checker "Block" is not a Series-24 sign-off.
    - **Books-and-records retention** required by FINRA Rule 4511 and SEC Rules 17a-3 / 17a-4 — see [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) and [Control 3.1](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md). The weekly digest is operational telemetry, not a regulated record.
    - **Written Supervisory Procedures (WSPs)** documenting who reviews what, when, and how. Examiners hold the firm to its own WSPs.

    Treat this playbook as the technical configuration record that makes the human-and-process controls above operable, evidenced, and auditable.

    **This walkthrough IS for:**

    | In Scope | Surface | Outcome |
    |---|---|---|
    | License-entitlement precheck before any toggle | PPAC → Resources → License consumption | Documented entitlement coverage for every active maker before enable |
    | Enabling Managed Environment on a single environment | PPAC → Environments → {env} → Settings → Enable Managed Environment | Per-environment governance substrate established |
    | Enabling Managed Environment on a group of environments (bulk) | PPAC → Environments → Edit Managed Environment status | Tier-aligned enable across an entire zone |
    | Configuring sharing limits for canvas apps, solution-aware cloud flows, agent flows, and Copilot Studio agents | PPAC → Environments → {env} → Settings → Sharing | Sprawl reduced; SoD pre-conditions enforced |
    | Solution checker enforcement (None / Warn / Block) with documented remediation workflow | PPAC → Environments → {env} → Settings → Solution checker | Critical-issue solutions blocked from import in Zone 3 |
    | Maker welcome content with WSP and training cross-references | PPAC → Environments → {env} → Settings → Maker welcome content | Documented policy acknowledgment surface |
    | Usage insights weekly digest with named recipients (commercial only) | PPAC → Environments → {env} → Settings → Usage insights | Weekly operational telemetry to governance and security distribution lists |
    | IP firewall in audit-only mode for 2–4 weeks before enforcement flip | PPAC → Environments → {env} → Settings → IP firewall | Verified allow-list with no false positives before enforcement |
    | IP-based cookie binding to bind sessions to source IP | PPAC → Environments → {env} → Settings → IP-based cookie binding | Token-replay risk reduced for Zone 3 |
    | Customer Lockbox approval workflow for Microsoft engineer access | PPAC → Environments → {env} → Settings → Customer Lockbox | Documented approval of every Microsoft access event |
    | Customer-Managed Keys via Power Platform Enterprise Policies + Azure Key Vault | PPAC → Policies → Enterprise policies → Encryption | Tenant-controlled encryption key with documented service-coverage exclusions |
    | Tenant Isolation for Entra-authenticated connectors | PPAC → Security → Identity and access → Tenant isolation | Cross-tenant connector flows controlled at the platform |
    | Environment routing for new makers (does NOT choose region) | PPAC → Settings → Environment routing | Makers steered into governed personal developer environments or environment groups |
    | Pipeline targets with Managed Environment status enabled | PPAC → Environments (filter: pipeline target) → Enable Managed Environment | No ungoverned promotion targets in the ALM topology |
    | Agent 365 governance integration for agents shared from Copilot Studio | M365 admin center → Agent 365 → Pending Requests / Governance | Tenant-level visibility, approval, and blocking for Copilot-surfaced agents |
    | Maker / approver / admin separation via security group assignment | Entra → Groups; PPAC → Environments → {env} → Settings → Users + permissions | SoD pre-conditions enforced for the environment |
    | Inactive resource view feeding orphan detection | PPAC → Environments → {env} → Analytics → Inactive resources | Orphan candidates routed to Control 3.6 |

    **This walkthrough is NOT for:**

    | Out of Scope | Use Instead |
    |---|---|
    | Tier classification of environments and environment-group membership | [Control 2.2 — Environment Groups and Tier Classification](../../../controls/pillar-2-management/2.2-environment-groups-and-tier-classification.md) |
    | DLP policy authoring and connector classification | [Control 1.5](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) and [Control 1.4](../../../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md) |
    | Agent registry of record across publishers and platforms | [Control 1.2](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md) |
    | Audit-log preservation under FINRA 4511 / SEC 17a-4 | [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) |
    | Orphan-agent detection and remediation workflow | [Control 3.6](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) |
    | Sentinel ingestion of Power Platform and Agent 365 audit data | [Control 3.9](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md) |
    | Agent 365 governance console end-to-end procedures | [Control 2.25](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md) |
    | PowerShell / Microsoft Graph automation for the same surfaces | [`./powershell-setup.md`](./powershell-setup.md) |
    | Test cases, sample queries, and evidence collection scripts | [`./verification-testing.md`](./verification-testing.md) |
    | Common errors, missing blades, console behavior anomalies | [`./troubleshooting.md`](./troubleshooting.md) |

!!! warning "Hedged-Language Reminder"
    This playbook helps your organization **support compliance with** FINRA Rule 4511 (Books and Records), FINRA Regulatory Notice 25-07 (AI Tools — RFC, contextual only), SEC Rules 17a-3 / 17a-4 (Recordkeeping), SOX Sections 302/404 (Internal Controls over Financial Reporting), GLBA 501(b) (Safeguards Rule), OCC Bulletin 2011-12 (Technology Risk Management), Federal Reserve SR 11-7 (Model Risk Management Guidance), CFTC oversight expectations for registered entities, NYDFS 23 NYCRR 500.06 (Audit Trail), and the FFIEC IT Examination Handbook. It does **not** by itself satisfy any of those obligations and **does not substitute for** the firm's documented Written Supervisory Procedures, model-risk governance committee, or registered-principal supervisory review. Implementation requires premium Power Platform entitlement coverage for every active maker, validated change-control procedures under [Control 2.3](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md), and independent testing by your compliance function. Organizations should verify all configurations against their own examination workpapers and consult legal counsel before treating these procedures as adequate evidence.

!!! warning "June 2026 Licensing-Enforcement Timeline"
    Microsoft is rolling out **end-user license-compliance notifications for Managed Environments starting in June 2026**. Users who interact with a Managed Environment without a qualifying premium entitlement (Power Apps Premium, Power Automate Premium, a Copilot Studio license that includes Power Platform Premium, Power Pages, or a qualifying Dynamics 365 license) will see **in-product banners**, and **tenant administrators will receive admin-center notifications**. **Pay-as-you-go (PAYG) billing alone is NOT sufficient** to entitle a user to a Managed Environment — PAYG meters runtime consumption but does not confer the per-user license that the Managed Environments licensing floor requires.

    Action: complete the §1 license-consumption precheck **before** enabling Managed Environment on any environment that hosts users not already covered by a qualifying entitlement. Document remediation (assign licenses, remove users, or reclassify the environment as Zone 1 personal-productivity with no premium-feature use) in your change-management ticket. Re-run the precheck **30 days before** the enforcement date and again **7 days before** to confirm coverage.

!!! warning "Sovereign Cloud Availability — GCC, GCC High, DoD, China"
    Managed Environments are available in sovereign clouds with **material feature gaps** that affect FSI evidence pipelines:

    | Feature | Commercial | GCC | GCC High | DoD | China (21Vianet) | Substitute approach |
    |---|---|---|---|---|---|---|
    | Managed Environment toggle | ✅ | ✅ | ✅ | ✅ | ✅ | — |
    | Sharing limits | ✅ | ✅ | ✅ | ✅ | ✅ | — |
    | Solution checker enforcement | ✅ | ✅ | ✅ | ✅ | ✅ | — |
    | IP firewall + IP cookie binding | ✅ | ✅ | ✅ | ✅ | ✅ | — |
    | Customer Lockbox | ✅ | ✅ | ✅ | ✅ | ❌ | Document exclusion in WSP |
    | Customer-Managed Keys | ✅ (broad coverage) | ⚠️ Partial | ⚠️ Partial (differs from commercial) | ⚠️ Partial | ⚠️ Verify | Verify per-service coverage in [Learn — Customer-managed key](https://learn.microsoft.com/en-us/power-platform/admin/customer-managed-key) before asserting CMK in your control narrative |
    | Usage insights / weekly digest | ✅ | ❌ | ❌ | ❌ | ❌ | Microsoft Graph activity exports + Purview audit ([Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) / [Control 3.1](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md)) + Sentinel ([Control 3.9](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md)) |
    | Tenant Isolation | ✅ | ✅ | ✅ | ✅ | ✅ | — |
    | Agent 365 governance console | ✅ (GA May 1, 2026) | ❌ Not announced | ❌ Not announced | ❌ Not announced | ❌ | Manual quarterly attestation per [Control 2.25](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md) §1 substitute path |

    Re-verify sovereign-cloud parity quarterly via the [Microsoft 365 Government roadmap](https://aka.ms/m365gov-roadmap) and the [Power Platform US Government documentation](https://learn.microsoft.com/en-us/power-platform/admin/powerapps-us-government). Where a feature is unavailable, disclose the absence in the firm's WSPs and document the substitute control. See §18 for the consolidated sovereign compensating-control table.

!!! info "Sovereign Cloud URLs"
    | Cloud | PPAC URL |
    |---|---|
    | Commercial | `https://admin.powerplatform.microsoft.com` |
    | GCC | `https://gcc.admin.powerplatform.microsoft.us` |
    | GCC High | `https://high.admin.powerplatform.microsoft.us` |
    | DoD | `https://admin.appsplatform.us` |
    | China (21Vianet) | `https://admin.powerplatform.partner.microsoftonline.cn` |

    Verify the current URL against [Microsoft Learn — Power Apps US Government](https://learn.microsoft.com/en-us/power-platform/admin/powerapps-us-government) before bookmarking.

---

## Document Map

| § | Section | Verification Criterion Evidenced |
|---|---|---|
| 0 | [Pre-flight Prerequisites and Triage](#0-pre-flight-prerequisites-and-triage) | All — gating checks |
| 1 | [PPAC Navigation and Licensing Precheck](#1-ppac-navigation-and-licensing-precheck) | VC-1 |
| 2 | [Enable Managed Environment on a Single Environment](#2-enable-managed-environment-on-a-single-environment) | VC-2 |
| 3 | [Enable Managed Environment on a Group of Environments](#3-enable-managed-environment-on-a-group-of-environments) | VC-2 |
| 4 | [Sharing Limits — Canvas Apps, Solution-Aware Flows, Agent Flows, Agents](#4-sharing-limits-canvas-apps-solution-aware-flows-agent-flows-agents) | VC-3 |
| 5 | [Solution Checker Enforcement](#5-solution-checker-enforcement) | VC-4 |
| 6 | [Maker Welcome Content](#6-maker-welcome-content) | VC-5 |
| 7 | [Usage Insights — Weekly Digest and Recipients](#7-usage-insights-weekly-digest-and-recipients) | VC-6 |
| 8 | [IP Firewall — Audit-Only Then Enforcement](#8-ip-firewall-audit-only-then-enforcement) | VC-7 |
| 9 | [IP-Based Cookie Binding](#9-ip-based-cookie-binding) | VC-7 |
| 10 | [Customer Lockbox](#10-customer-lockbox) | VC-8 |
| 11 | [Customer-Managed Keys (CMK)](#11-customer-managed-keys-cmk) | VC-8 |
| 12 | [Tenant Isolation](#12-tenant-isolation) | VC-9 |
| 13 | [Environment Routing](#13-environment-routing) | VC-10 |
| 14 | [Pipeline Targets — Managed Environment Status](#14-pipeline-targets-managed-environment-status) | VC-11 |
| 15 | [Microsoft Agent 365 / M365 Admin Center Governance Integration](#15-microsoft-agent-365-m365-admin-center-governance-integration) | VC-12 |
| 16 | [Maker / Approver / Admin Separation](#16-maker-approver-admin-separation) | VC-13 |
| 17 | [Inactive Resource View — Orphan Detection Feed](#17-inactive-resource-view-orphan-detection-feed) | VC-14 |
| 18 | [Sovereign Cloud Compensating Controls](#18-sovereign-cloud-compensating-controls) | All (substitute path) |
| 19 | [Closing Decision Matrix — Portal vs PowerShell vs Graph](#19-closing-decision-matrix-portal-vs-powershell-vs-graph) | Operational reference |

---
## 0. Pre-flight Prerequisites and Triage

Before clicking anything in any portal, run through this gate. Skipping a gate produces silent failures later — for example, the **Enable Managed Environments** wizard succeeds even when downstream users lack premium entitlement, only to surface the licensing gap as in-product banners and admin notifications after the June 2026 enforcement date.

### 0.1 Confirm tenant cloud and tenant ID

1. Sign in to [`https://admin.microsoft.com`](https://admin.microsoft.com) as an account that holds at least **Entra Global Reader** (read-only); escalate to **Power Platform Admin** or **Entra Global Admin** only when about to make a configuration change.
2. In the upper-right corner, click your profile chip → **Switch directory** if you are a multi-tenant operator. Confirm you are in the tenant you intend to govern.
3. Navigate to **Settings → Org settings → Organization profile**. Capture the **Tenant ID** GUID and **Primary domain** (for example, `contoso.onmicrosoft.com`). Record both in your runbook.
4. Confirm **Country or region** matches the regulated entity. For US broker-dealers and banks this is typically `United States`.

!!! warning "Tenant Cloud Detection"
    If the URL bar shows `admin.microsoft.us` (GCC High / DoD) or you authenticate against `login.microsoftonline.us`, the usage-insights digest (§7) and the Agent 365 governance integration (§15) are unavailable. Continue this playbook for the §2–§6, §8–§14, §16–§17 surfaces that **are** available, and substitute the §18 compensating controls for §7 and §15.

### 0.2 Confirm role assignments

Use the canonical role names from [`docs/reference/role-catalog.md`](../../../reference/role-catalog.md). Managed Environments configuration honors a small set of roles. Apply Microsoft Entra Privileged Identity Management (PIM) to **Entra Global Admin** and to **Power Platform Admin**.

| Role | Required for | Where to assign |
|---|---|---|
| **Power Platform Admin** | All Managed Environments toggles, sharing limits, solution checker, maker welcome content, IP firewall, IP cookie binding, Customer Lockbox enable, CMK assignment, tenant isolation, environment routing. **Activate via PIM** for change windows. | Entra → Roles & admins → search "Power Platform Administrator" |
| **Power Platform Service Admin** | Day-to-day environment operations, sharing-limit edits, weekly digest recipient changes, pipeline-target enables. | Entra → Roles & admins (Microsoft documents a single role; "Service Admin" denotes the day-to-day operator persona within the role catalog) |
| **Entra Global Admin** | Tenant-wide identity and Cross-Tenant Access settings; CMK Enterprise Policy creation that requires both Power Platform Admin and Entra Global Admin role activation; emergency lifecycle actions. **PIM-eligible only.** | Entra → Roles & admins |
| **M365 Admin** | Agent 365 governance integration (§15); license assignment; Customer Lockbox tenant-wide enable surface in M365 admin center. | Entra → Roles & admins |
| **AI Governance Lead** | Approver of zone classification, sharing-limit baselines, solution-checker enforcement level, and welcome-content text per the firm's AI governance policy. Documented in change ticket; not necessarily an Entra role. | Internal RACI |
| **Compliance Officer** | Read-only review of Managed Environments configuration and weekly digest distribution; signs off on books-and-records substitution path in sovereign clouds. | Entra → Roles & admins → **Entra Global Reader** |
| **CISO** | Final approver for IP firewall enforcement flip, CMK assignment, Tenant Isolation enforcement, and any deviation from the documented Zone 3 baseline. | Internal RACI |
| **Purview Compliance Admin** | Cross-reference for retention labels and Purview Audit policies aligned with the weekly digest and CMK exclusion list. | Purview → Roles & scopes |

1. In Entra, navigate to **Identity → Roles & admins → Roles**.
2. Search for **Power Platform Administrator** and **Global Administrator**. Confirm at minimum **two named human accounts** hold each operating role (no service principals, no break-glass-only accounts) per FINRA dual-control expectations.
3. If any role shows zero or one assignee, open a ticket with your Entra owner before proceeding — single-person admin coverage on Power Platform Admin is itself an audit finding under FINRA Rule 3110 supervisory review.

!!! example "Examiner Evidence Box — Role Coverage"
    | Element | Value |
    |---|---|
    | Artifact produced | CSV export of `directoryRole` membership for Power Platform Admin, Entra Global Admin (PIM-eligible), Entra Global Reader, M365 Admin, Purview Compliance Admin |
    | Retention duration | 6 years (SEC 17a-4 / FINRA 4511) on Purview WORM-locked records label |
    | Regulatory mapping | FINRA 3110 (supervision — dual control), SOX §404 (segregation of duties), NYDFS 23 NYCRR 500.06 (access governance audit trail) |

### 0.3 Confirm prerequisites for the target environment

For **each** environment you intend to enable Managed Environment on:

- [ ] Environment GUID captured (not just display name — display names can be edited and are not unique across operations).
- [ ] **Dataverse provisioned** in the environment — Managed Environments require a Dataverse-backed environment for solution checker, maker welcome content storage, and several telemetry surfaces. Personal developer environments and trial environments without Dataverse cannot be Managed Environments.
- [ ] Zone classification determined per [Control 2.2](../../../controls/pillar-2-management/2.2-environment-groups-and-tier-classification.md): Zone 1 (Personal), Zone 2 (Team), Zone 3 (Enterprise/Regulated).
- [ ] Region aligned with data-residency policy (region was selected at environment provisioning; environment routing in §13 does **not** change region of an existing environment).
- [ ] DLP policy assignment ready per [Control 1.5](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) and connector policy per [Control 1.4](../../../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md). Managed Environments are complementary to DLP — they are **not** a substitute. Standalone (non-solution-aware) cloud flows are not governed by Managed Environment sharing limits and rely on DLP for connector control.
- [ ] License-entitlement coverage verified per §1.2.
- [ ] Maker welcome content drafted (≤ 1500 characters) — see §6 for content rules and the CMK exclusion warning.
- [ ] Change-management ticket open per [Control 2.3](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md) referencing the target environment GUID.

### 0.4 Pre-flight gate summary

Do not proceed past this section unless **all** of the following are true:

- [ ] You are signed in to the correct tenant and have captured the tenant ID.
- [ ] Tenant cloud is identified and you have read the §0.1 sovereign-cloud warning.
- [ ] At least two named humans hold each governance role in §0.2.
- [ ] **Entra Global Admin** and **Power Platform Admin** are PIM-eligible (not active by default).
- [ ] Target environment GUID, region, Dataverse status, zone, DLP plan, and license-coverage status are recorded.
- [ ] Change-management ticket is open and references the environment GUID.
- [ ] Your governance runbook records the firm's documented SLAs for Managed Environments review (illustrative defaults: weekly digest review every Monday 09:00 ET; quarterly sovereign substitute attestation — examiners will hold the firm to its own documented SLA).

!!! tip "If a Gate Fails"
    Open [`./troubleshooting.md`](./troubleshooting.md) and search for the gate name. Do not attempt workarounds in production until the gate clears — most workarounds for missing licensing or roles create their own audit findings under FINRA 3110 and SOX §404.

---

## 1. PPAC Navigation and Licensing Precheck

### 1.1 Navigate to PPAC

1. From the Microsoft 365 admin center launcher, click **Show all → Power Platform**, or browse directly to the cloud-appropriate URL from the §0 table.
2. Verify the upper-right tenant indicator displays the tenant primary domain captured in §0.1. **If the wrong tenant is loaded, sign out — do not "switch directory" mid-session**, because cached blade state can cause configuration to apply to the wrong tenant. This has been observed in support cases and is the single most common Managed Environments mis-target incident.
3. Confirm the left-rail blade list contains: **Environments**, **Analytics**, **Resources**, **Help + support**, **Policies**, **Settings**.

### 1.2 License-consumption precheck

This precheck is **mandatory** before enabling Managed Environment on any environment that hosts users not already covered by a qualifying entitlement. It produces the evidence required to defend the §0 June 2026 enforcement banner against an examiner question of "how did the firm know it was license-compliant before enabling enforcement substrate?"

1. Navigate to **PPAC → Resources → License consumption**.
2. The **License consumption** blade lists active per-user license types (Power Apps Premium, Power Automate Premium, Copilot Studio licenses including Power Platform Premium, Power Pages, qualifying Dynamics 365 SKUs) and the count of users actively consuming features that require those entitlements.
3. Apply the **Environment** filter and select the GUID of the environment you intend to enable Managed Environment on.
4. Export the active-user roster to CSV. The CSV columns include **User principal name**, **License (qualifying)**, **License (PAYG-only flag)**, **Last activity**.
5. For each user in the CSV:
   - If the user holds a qualifying premium per-user license, mark **Coverage: Yes**.
   - If the user is consuming features under PAYG only (no qualifying per-user license), mark **Coverage: PAYG-only — INSUFFICIENT** and flag for remediation.
   - If the user is inactive (last activity > 90 days), mark **Coverage: Inactive — candidate for removal** and route to [Control 3.6](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) for orphan handling.
6. For users flagged **PAYG-only — INSUFFICIENT**, the documented remediation options are:
   - Assign a qualifying license via M365 admin center → Users → Licenses.
   - Remove the user from the environment via PPAC → Environments → {env} → Settings → Users + permissions → Remove.
   - Reclassify the environment as Zone 1 (personal productivity) with no premium-feature use and **do not enable Managed Environment** until coverage is achieved.
7. Attach the annotated CSV to the change-management ticket. Re-run this precheck **30 days before** and again **7 days before** the June 2026 enforcement date.

!!! warning "PAYG Is Not a Substitute for Per-User Licensing"
    PAYG (pay-as-you-go) billing meters runtime consumption (Dataverse capacity, premium connector calls, AI-builder credits) but **does not entitle a user to access a Managed Environment**. The Managed Environments licensing floor requires a per-user qualifying entitlement. Enabling Managed Environment on an environment where users rely on PAYG only will, after the June 2026 enforcement date, surface in-product banners and admin-center notifications — and produce a foreseeable audit finding under SOX §404 (operating effectiveness of license-controls).

!!! example "Examiner Evidence Box — License Coverage Precheck"
    | Element | Value |
    |---|---|
    | Artifact produced | Annotated `License-consumption-{env-guid}-{YYYY-MM-DD}.csv` with Coverage column; remediation outcome per flagged user |
    | Retention duration | 6 years on Purview WORM-locked records label |
    | Regulatory mapping | SOX §302/404 (entitlement controls), FINRA 4511 (books and records), GLBA §501(b) (administrative safeguards) |

---

## 2. Enable Managed Environment on a Single Environment

This procedure enables the Managed Environments substrate on **one** environment. Use §3 for bulk enablement on a group of environments.

### 2.1 Navigate to the environment

1. **PPAC → Environments**. The environment table displays Name, Type, State, Region, Dataverse, Managed.
2. Confirm the **Managed** column shows **No** for the target environment. If it already shows **Yes**, jump to §2.6 verification.
3. Click the environment **Display name** to open the environment overview blade.
4. Confirm the overview shows the expected Region, Type (Production / Sandbox / Developer / Trial), and Dataverse status.

### 2.2 Open the Enable Managed Environment wizard

1. From the environment overview blade, click the **Enable Managed Environments** button in the command bar (top of the blade), **or** click **Settings → Product → Managed Environment**.
2. The **Enable Managed Environments** wizard opens. The wizard surfaces five configurable groups:
   - **Limit sharing** (canvas-app sharing limit — see §4)
   - **Usage insights** (weekly digest enrollment — see §7; commercial only)
   - **Maker welcome content** (URL or text — see §6)
   - **Solution checker enforcement** (None / Warn / Block — see §5)
   - **IP firewall** (off by default — see §8 for guarded enable path)

3. **Recommended posture for first-enable**:
   - **Limit sharing**: configure per zone (see §4 baselines below). For Zone 3, set to **Limit total individuals who can share to** with a small named cap (illustrative default: 5) and **exclude security groups: Off** to force named-individual sharing only.
   - **Usage insights**: **On** in commercial; recipients = security distribution + governance distribution + AI Governance Lead. (Sovereign clouds: leave **On** if available; otherwise rely on §18 substitutes.)
   - **Maker welcome content**: paste the firm's policy text (≤ 1500 characters) or link to the WSP intranet location. See §6 CMK exclusion warning.
   - **Solution checker**: **Warn** in Zone 1/2; **Block** in Zone 3.
   - **IP firewall**: **Off** at the wizard step. Configure separately in §8 with the **audit-only first** workflow.

4. Click **Enable**. The wizard returns to the environment overview blade. The **Managed** column flips to **Yes**, typically within 30 seconds. Refresh the blade if the indicator does not update.

### 2.3 Confirm the per-environment Settings → Product layout

After enable, the environment **Settings** blade exposes a **Product** section with the following Managed-Environments-only configuration items, each addressed in a dedicated section below:

- **Managed Environment** (status, edit settings, disable)
- **Sharing** (sharing limits — §4)
- **Solution checker** (enforcement level — §5)
- **Maker welcome content** (§6)
- **Usage insights** (digest recipients — §7; commercial only)
- **IP firewall** (§8)
- **IP-based cookie binding** (§9)
- **Customer Lockbox** (§10)
- **Customer-managed key** (§11)

### 2.4 Apply the Zone 3 baseline (if Zone 3)

For Zone 3 enterprise/regulated environments, apply this baseline immediately after enable. Refer to the linked sections for portal step detail; the table is a checklist.

| Setting | Zone 3 baseline | Section |
|---|---|---|
| Sharing — canvas apps | Limit total individuals who can share **5**; exclude security groups **Off** | §4.2 |
| Sharing — solution-aware flows | Limit total individuals who can share **5** | §4.3 |
| Sharing — Copilot Studio agents | Limit total individuals who can share **3**; exclude security groups **Off** | §4.5 |
| Solution checker | **Block** | §5 |
| Maker welcome content | Firm WSP excerpt + AI Acceptable Use link | §6 |
| Usage insights | **On**; recipients = sec-dist + gov-dist + AI Governance Lead | §7 |
| IP firewall | **Audit-only** for ≥ 14 days, then **Enforce** | §8 |
| IP-based cookie binding | **On** | §9 |
| Customer Lockbox | **On** (if not already tenant-wide) | §10 |
| Customer-managed key | **On** with named Key Vault and rotation policy | §11 |
| Tenant Isolation | Allow-list of partner tenants; otherwise deny inbound | §12 |

### 2.5 Apply the Zone 2 baseline (if Zone 2)

| Setting | Zone 2 baseline | Section |
|---|---|---|
| Sharing — canvas apps | Limit total individuals who can share **20** | §4.2 |
| Sharing — solution-aware flows | Limit total individuals who can share **20** | §4.3 |
| Sharing — Copilot Studio agents | Limit total individuals who can share **10** | §4.5 |
| Solution checker | **Warn** | §5 |
| Maker welcome content | Firm WSP excerpt + AI Acceptable Use link | §6 |
| Usage insights | **On**; recipients = governance distribution | §7 |
| IP firewall | Off (rely on Conditional Access; document the rationale) | §8 |
| IP-based cookie binding | Off (rely on token-binding via Conditional Access) | §9 |
| Customer Lockbox | **On** (tenant-wide) | §10 |
| Customer-managed key | Optional — risk-tier dependent | §11 |
| Tenant Isolation | Tenant-wide allow-list | §12 |

### 2.6 Verification

- [ ] **PPAC → Environments → {env} → Settings → Product → Managed Environment** shows **Status: Enabled**.
- [ ] **PPAC → Environments** table shows **Managed: Yes** for the target environment.
- [ ] **Audit log entry** in Purview Audit (`SearchUnifiedAuditLog`) shows `EnableManagedEnvironment` event for the environment GUID with the operator UPN. Capture the event GUID for the change ticket.
- [ ] Zone-baseline settings (per §2.4 or §2.5) applied; partial-baseline state must not be left in production.

!!! example "Examiner Evidence Box — Managed Environment Enable"
    | Element | Value |
    |---|---|
    | Artifact produced | Screenshot of **Settings → Product → Managed Environment** showing Enabled status with timestamp; Purview Audit export of the `EnableManagedEnvironment` event including operator UPN |
    | Retention duration | 6 years (FINRA 4511 / SEC 17a-4) |
    | Regulatory mapping | FINRA 3110 (supervisory configuration baseline), SOX §404 (control change), NYDFS 23 NYCRR 500.06 (audit trail of configuration change) |

---

## 3. Enable Managed Environment on a Group of Environments

PPAC supports bulk enable from the environments table or via the **Edit Managed Environment status** action surface. Use this for a coordinated tier-aligned rollout (for example, all Zone 3 environments in a single change window).

### 3.1 Bulk enable via the environments table

1. **PPAC → Environments**. Use the column-filter chevrons to filter by:
   - **State = Ready**
   - **Type = Production** (or Sandbox for non-prod waves)
   - **Managed = No** (so you do not re-enable already-managed environments)
   - **Environment group = {your zone group}** (set per [Control 2.2](../../../controls/pillar-2-management/2.2-environment-groups-and-tier-classification.md))
2. Select the row checkboxes for each environment to enable.
3. From the command bar, click **Enable Managed Environments**.
4. The bulk wizard surfaces the same five configuration groups as §2.2 but applies them to **all** selected environments. **The settings are uniform across all selected environments** — the wizard does not allow per-environment overrides during bulk enable.
5. Pre-baseline the wizard with the Zone 3 (or Zone 2) values from §2.4 / §2.5.
6. Click **Enable**. A status drawer opens; each environment's enable progress is shown. Wait for **all** rows to reach **Enabled** before closing the drawer (typical: 30–90 seconds per environment).

### 3.2 Edit Managed Environment status

To **change** Managed Environment status (enable, disable, or copy settings) on environments that are already in scope:

1. **PPAC → Environments** → multi-select the environments.
2. **More actions → Edit Managed Environment status**.
3. Select **Enable**, **Disable**, or **Copy settings from existing environment**.
4. **Copy settings from existing environment** is the recommended idempotent pattern when standing up new Zone 3 environments — pick a known-good Zone 3 reference environment as the source. Copy includes: sharing limits, solution checker, maker welcome content, usage insights recipients, IP firewall **rules** (the firewall **enable state** is not copied — the new environment lands in **audit-only**), IP cookie binding, Customer Lockbox, and CMK assignment **only** when both source and target reference the **same** Enterprise Policy.

### 3.3 Bulk verification

- [ ] All selected environments show **Managed: Yes** in the environments table.
- [ ] Spot-check 3 environments: open Settings → Product → Managed Environment and verify the per-environment baseline matches the bulk-applied values.
- [ ] Purview Audit shows one `EnableManagedEnvironment` event per environment GUID, all attributed to the same operator UPN within the change window.

!!! warning "Disabling Is Not a Reversible Roll-Back"
    Disabling Managed Environments removes sharing limits, solution-checker enforcement, the IP firewall, IP cookie binding, and Customer-Managed-Key enforcement (the data remains encrypted under the previously assigned key, but new key-rotation will not propagate). Re-enabling restores the substrate but does **not** re-apply the previous configuration values; you must re-baseline. Examiners should see this asymmetry documented in the firm's WSPs as part of the change-management procedure under [Control 2.3](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md).

---
## 4. Sharing Limits — Canvas Apps, Solution-Aware Flows, Agent Flows, Agents

### 4.1 What sharing limits govern (and what they do not)

Sharing limits, per [Microsoft Learn — Limit sharing](https://learn.microsoft.com/en-us/power-platform/admin/managed-environment-sharing-limits), apply to:

- **Canvas apps** (Power Apps canvas designer)
- **Solution-aware cloud flows** (cloud flows authored inside a Dataverse solution)
- **Solution-aware agent flows** (agent-runtime flows packaged in a solution)
- **Copilot Studio agents** (agents authored in the Copilot Studio author canvas; sharing limit applies to the author-time share surface)

Sharing limits do **NOT** apply to:

- **Standalone (non-solution-aware) cloud flows** — these can be shared without bound by a maker who holds the necessary Dataverse / Power Automate role. **You must compensate with DLP** ([Control 1.5](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md)) and **Advanced Connector Policies** ([Control 1.4](../../../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md)). This is the single most common Managed Environments scope misunderstanding in FSI deployments and a frequent cause of Zone 3 examiner findings.
- **Model-driven apps** — sharing is governed by Dataverse security roles, not by Managed Environment sharing limits.
- **Power Pages sites** — sharing is governed by site authentication settings, not by sharing limits.
- **Copilot Studio agent runtime distribution** — once published to Microsoft 365 Copilot or Microsoft Teams, runtime distribution is governed by Agent 365 / Teams admin policies (see §15 and [Control 2.25](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md)).

### 4.2 Canvas-app sharing limits

1. **PPAC → Environments → {env} → Settings → Product → Sharing**.
2. The **Sharing** blade exposes three sections corresponding to the three sharing surfaces. The **Apps** section governs canvas apps.
3. Choose one of:
   - **Don't limit sharing** — no limit; not recommended in Zone 2 or Zone 3.
   - **Exclude sharing with security groups** — apps cannot be shared with security groups (only with named individuals). Forces per-individual share events to flow into Dataverse audit and Sentinel.
   - **Limit total individuals who can share** + numeric cap — enforces a maximum number of individual share assignments per app.
4. Recommended:
   - **Zone 1**: Don't limit sharing; document the exception in WSP (Zone 1 is personal-productivity).
   - **Zone 2**: Limit total individuals who can share **20**.
   - **Zone 3**: Limit total individuals who can share **5**, **and** exclude sharing with security groups.
5. Click **Save**. The blade displays the new limits and a banner confirming the change. The configuration is effective immediately for **new** share operations; existing shares are not retroactively trimmed.

### 4.3 Solution-aware cloud flow sharing limits

1. Same blade — scroll to the **Cloud flows** section.
2. The same three options (Don't limit / Exclude security groups / Limit total individuals) apply.
3. Recommended Zone 3: Limit total individuals who can share **5**.
4. Click **Save**.

### 4.4 Agent flows sharing limits

1. Same blade — scroll to the **Agent flows** section.
2. Apply the same Zone 3 limit (5) or Zone 2 limit (20).
3. Click **Save**.

### 4.5 Copilot Studio agent sharing limits

1. Same blade — scroll to the **Agents** section.
2. Recommended:
   - **Zone 3**: Limit total individuals who can share **3**, and exclude sharing with security groups.
   - **Zone 2**: Limit total individuals who can share **10**.
3. Click **Save**.

!!! warning "Sharing Limits Are Author-Time, Not Run-Time"
    Sharing limits constrain **who can be granted authoring or co-authoring access** to the resource. They do **not** constrain run-time consumption of a published agent or app. For run-time distribution control of agents that surface in Microsoft 365 Copilot or Teams, see §15 and [Control 2.25](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md).

### 4.6 Verification

- [ ] **PPAC → Environments → {env} → Settings → Sharing** shows the configured limits per surface.
- [ ] Test: as a maker, attempt to share a canvas app with a security group when the **Exclude security groups** setting is enabled. The share UI should display "Sharing with security groups is restricted by your administrator."
- [ ] Test: as a maker, attempt to share a canvas app with a 6th individual when the limit is set to 5. The share UI should display "You have reached the sharing limit set by your administrator."
- [ ] Purview Audit shows `UpdateManagedEnvironmentSettings` event with the share-limit configuration delta.

!!! example "Examiner Evidence Box — Sharing Limits"
    | Element | Value |
    |---|---|
    | Artifact produced | Screenshot of **Settings → Sharing** with limits visible per surface; screenshots of denied-share attempts; Purview Audit export of `UpdateManagedEnvironmentSettings` |
    | Retention duration | 6 years (FINRA 4511 / SEC 17a-4) |
    | Regulatory mapping | FINRA 3110 (supervisory limits on maker-controlled distribution), GLBA §501(b) (access controls), SOX §404 (operating effectiveness) |

---

## 5. Solution Checker Enforcement

### 5.1 What solution checker enforces

Per [Microsoft Learn — Power Platform Build Tools](https://learn.microsoft.com/en-us/power-platform/alm/devops-build-tools), Managed Environments run solution checker on **import** of any unmanaged or managed solution and on **publish** of components inside a solution. The enforcement levels:

- **None** — solution checker runs but does not block import/publish. Results are surfaced to the maker but unenforced.
- **Warn** — solutions with **critical** issues display a warning banner; the maker can override and proceed. Override events are written to Dataverse audit.
- **Block** — solutions with **critical** issues are **blocked** from import/publish. The maker must remediate critical issues before retrying. Block events are written to Dataverse audit.

Issue severity is set by the solution-checker rule catalog. Critical severity rules are documented in [Microsoft Learn — Power Apps Checker API](https://learn.microsoft.com/en-us/power-platform/alm/checker-api/overview). Examples of critical-severity rules include cleartext credential patterns, unsafe HTTP-action use, and patterns that bypass platform security boundaries.

### 5.2 Configure enforcement

1. **PPAC → Environments → {env} → Settings → Product → Solution checker**.
2. Choose **None**, **Warn**, or **Block**.
3. Recommended:
   - **Zone 1**: **None** (personal-productivity; document rationale).
   - **Zone 2**: **Warn**.
   - **Zone 3**: **Block**.
4. Click **Save**.

### 5.3 Documented remediation workflow (Zone 3 Block)

When a maker hits a Block in Zone 3:

1. The import/publish UI displays the failing solution-checker rule(s) with severity, rule ID, and affected component.
2. The maker opens a remediation ticket in the firm's ITSM tool referencing the solution name, the rule ID, and the affected component.
3. The maker remediates the issue locally, re-runs solution checker in the **maker** environment (Zone 1 personal developer environment) to confirm the fix, then re-attempts the import/publish in the Zone 3 target.
4. **Override is not available in Block mode.** A maker who insists the rule is a false positive must escalate to the AI Governance Lead, who can:
   - Open a Microsoft support case to dispute the rule classification, **or**
   - Document an accepted exception in the firm's risk register, temporarily change the enforcement to **Warn**, allow the import, and immediately revert to **Block**. The exception window must be ≤ 24 hours and recorded in change management with a Compliance Officer co-signature.

### 5.4 Verification

- [ ] **Settings → Product → Solution checker** shows the configured enforcement level.
- [ ] Test (Zone 3 Block): import a deliberately-broken solution into a non-prod Zone 3 sandbox; confirm the import is blocked with the expected critical-rule message.
- [ ] Purview Audit shows `UpdateManagedEnvironmentSettings` event with the enforcement-level delta.
- [ ] Dataverse audit shows `SolutionCheckerResult` events for each import attempt.

!!! example "Examiner Evidence Box — Solution Checker Block"
    | Element | Value |
    |---|---|
    | Artifact produced | Screenshot of Block setting; screenshot of denied-import dialog; Dataverse audit export of `SolutionCheckerResult` event for the test import |
    | Retention duration | 6 years (FINRA 4511 / SEC 17a-4) |
    | Regulatory mapping | FINRA 3110 (supervisory pre-deployment review), SOX §404 (change-control operating effectiveness), OCC 2011-12 (technology risk — pre-deployment validation) |

---

## 6. Maker Welcome Content

### 6.1 Purpose

Maker welcome content is rendered to a maker the first time they enter the environment and is reachable from the maker portal at any time afterwards. It is the firm's documented opportunity to put the **AI Acceptable Use Policy**, the **WSP excerpt covering AI tools** (FINRA Notice 25-07 contextual), and the **link to the model-risk register** in front of every maker.

### 6.2 Configure

1. **PPAC → Environments → {env} → Settings → Product → Maker welcome content**.
2. Two input modes:
   - **URL** — link to the firm's intranet landing page (e.g., SharePoint Online site). Recommended when the firm wants centrally-controlled content with version history.
   - **Markdown text** — paste up to 1500 characters of Markdown directly into the field.
3. Recommended (URL mode): paste the SharePoint Online URL of the **AI Tools — Maker Welcome** page, which embeds the WSP excerpt, AUP link, and incident-reporting link.
4. Click **Save**. The welcome surface appears for any maker entering the environment.

!!! note "Maker Welcome Content Is EXCLUDED from Customer-Managed Keys"
    Per [Microsoft Learn — Customer-managed key — Excluded data](https://learn.microsoft.com/en-us/power-platform/admin/customer-managed-key#excluded-data), maker welcome content is among the data categories **NOT encrypted by Customer-Managed Keys** even when CMK is enabled on the environment. Other excluded categories (non-exhaustive — verify against current Microsoft documentation):
    - Maker welcome content
    - Solution-checker results metadata
    - Power Apps display names and descriptions
    - Connection metadata
    - Copilot Studio data sent as part of Agent 365 security audit logging
    Do **not** place anything in maker welcome content that the firm classifies as Confidential or above. Use a URL link to a permission-scoped intranet page instead of pasting Confidential text.

### 6.3 Cross-references

- Cross-reference with [Control 2.14 — Maker Training and Enablement](../../../controls/pillar-2-management/2.14-training-and-awareness-program.md) to ensure the welcome page content aligns with the firm's documented maker-onboarding training curriculum.
- Cross-reference with [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) for the audit treatment of maker first-entry events.

### 6.4 Verification

- [ ] **Settings → Product → Maker welcome content** shows the configured URL or Markdown text.
- [ ] Test: with a maker test account, enter the environment for the first time. Confirm the welcome content renders.
- [ ] Confirm the linked SharePoint page is owned by the AI Governance Lead and has version history enabled.

---

## 7. Usage Insights — Weekly Digest and Recipients

!!! warning "Sovereign Cloud Unavailability"
    The usage insights / weekly digest feature is **unavailable in GCC, GCC High, DoD, and China (21Vianet)**. In sovereign clouds, substitute the §18.2 compensating-control pipeline (Microsoft Graph activity exports + Purview audit + Sentinel workbook). Do **not** assert "weekly governance review" in your control narrative for sovereign-cloud environments without naming the substitute pipeline and the named-recipient distribution list.

### 7.1 Configure recipients (commercial)

1. **PPAC → Environments → {env} → Settings → Product → Usage insights**.
2. Toggle **Weekly digest** to **On**.
3. In the **Recipients** field, add named recipients. **Recommended distribution lists** (use Entra mail-enabled security groups, not personal mailboxes):
   - `dl-aigovernance@{firm}.com` — AI Governance Lead and delegates
   - `dl-secops-power@{firm}.com` — Security Operations Power Platform monitoring
   - `dl-compliance-supervisory@{firm}.com` — Compliance officers responsible for FINRA 3110 supervisory review of the environment
4. Click **Save**.

### 7.2 What the digest contains

The digest summarizes the past 7 days of activity in the environment, including (non-exhaustive — verify against current Microsoft documentation):

- Active makers and active users
- Apps launched, app-launch counts
- Flows runs, flows failed
- Top apps by user count
- Top flows by run count
- Solution-checker results summary
- Sharing-limit enforcement events
- IP-firewall enforcement / audit events (when configured)

### 7.3 Operational SLA (firm-defined)

Document in the firm's WSP the SLA for digest review. Illustrative defaults (the firm's actual SLA is what examiners will hold the firm to):

- Recipient distribution-list owner reviews each weekly digest within **48 hours of receipt**.
- Anomalies (sharing-limit enforcement spike, solution-checker block spike, IP-firewall denied-traffic spike) are routed to the SecOps incident queue within **4 business hours of identification**.
- Quarterly: AI Governance Lead reviews the trailing 13 weeks of digests with the Compliance Officer; signed-off review minutes are retained in the governance evidence library for 6 years.

### 7.4 Verification

- [ ] **Settings → Product → Usage insights** shows **On** with the named recipients.
- [ ] Test: confirm the first weekly digest arrives in the named distribution lists at the expected cadence (Monday 09:00 UTC by default).
- [ ] Documented review SLA exists in the firm's WSP and the digest-review log shows compliance with the SLA.

!!! example "Examiner Evidence Box — Weekly Digest Operational Cadence"
    | Element | Value |
    |---|---|
    | Artifact produced | Screenshot of Usage insights configuration; trailing-13-weeks digest archive in the governance evidence library; digest-review log (signed-off entries) |
    | Retention duration | 6 years (FINRA 4511 / SEC 17a-4) on Purview WORM-locked records label |
    | Regulatory mapping | FINRA 3110 (supervisory cadence), SOX §404 (operating effectiveness), GLBA §501(b) (administrative safeguards), NYDFS 23 NYCRR 500.06 (audit trail review cadence) |

---
## 8. IP Firewall — Audit-Only Then Enforcement

### 8.1 What the IP firewall governs

The Power Platform IP firewall, when enabled on a Managed Environment, restricts **API calls to Dataverse and to selected Power Platform services from outside the configured allow-list of public IP CIDR ranges**. It is a perimeter control for Dataverse-bound traffic from maker portals, Power Apps native runners, and selected service-to-service traffic. It does **not** by itself govern Microsoft 365 Copilot agent invocations (those are governed by the M365 Copilot tenant network controls and Conditional Access).

The firewall has two operating modes:

- **Audit-only** (default first state) — denied-by-policy traffic is **not blocked**; events are logged so you can verify the allow-list before turning on enforcement.
- **Enforce** — denied-by-policy traffic is blocked; events are logged.

**Always enable in audit-only first.** Do not flip to enforce on day one. The recommended audit window is **2 to 4 weeks** for a Zone 3 production environment with diverse maker geography (offices, work-from-home, third-party-data-center egress, partner connectivity).

### 8.2 Build the allow-list

Before opening the blade, prepare the allow-list as a CSV with these columns: **CIDR**, **Description**, **Owner**, **Source-of-truth**.

Common CIDR sources to enumerate:

- Corporate office egress IPv4 ranges (from network engineering)
- VPN concentrator egress IPv4 ranges
- Cloud-hosted bastion / virtual-desktop egress IPv4 ranges
- ZTNA / SASE egress IPv4 ranges (from the SASE provider)
- Approved partner data-center egress (per partner BAA / DPA)
- Reverse-proxy / SSE platform egress (if a Forwarded-header reverse proxy fronts user traffic — see §8.5)

Have the network team co-sign the CSV. The CSV becomes the firm's source-of-truth audit artifact for the firewall configuration.

### 8.3 Configure in audit-only mode

1. **PPAC → Environments → {env} → Settings → Product → IP firewall**.
2. Toggle **IP firewall** to **On**.
3. Toggle **Audit-only mode** to **On**. This is the critical safety setting — it must be **On** for the initial enable.
4. In **Allowed IP ranges**, paste the CIDR list (one entry per line in `CIDR` notation, for example `203.0.113.0/24`).
5. Click **Save**. The blade displays the configured ranges and a banner confirming **Audit-only mode is enabled**.

### 8.4 Capture the would-be-blocked traffic for 2–4 weeks

During the audit window:

1. Stream Power Platform audit events to Microsoft Sentinel ([Control 3.9](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md)).
2. Each day, run a Sentinel query for the audit-only **would-be-blocked** events for the environment GUID.
3. For each unique source-IP that would have been blocked:
   - **If the IP is a known good source missing from the allow-list** — add it to the allow-list CSV, re-paste into the blade, save, and document in the change-management ticket.
   - **If the IP is unexpected** — investigate as a potential incident with SecOps.
4. **Do not flip to enforce until the audit log shows ≥ 7 consecutive days of zero would-be-blocked events** from known good sources.

### 8.5 Reverse-proxy IP addresses (Forwarded header)

If your firm fronts maker traffic with a reverse proxy or SSE / SASE platform that **rewrites the Layer-3 source IP**, the apparent client IP at the Power Platform edge is the proxy egress IP, not the maker's true client IP. To allow Power Platform to use the **true client IP** for firewall evaluation, configure the **Reverse proxy IP addresses** field on the IP firewall blade with the proxy egress CIDRs. Power Platform then trusts the standard `Forwarded` HTTP header (per [RFC 7239](https://datatracker.ietf.org/doc/html/rfc7239)) from those source IPs and applies the firewall against the original client IP carried in the header.

1. On the IP firewall blade, expand **Reverse proxy IP addresses**.
2. Paste the proxy egress CIDR(s).
3. Click **Save**.
4. Verify with SecOps that the proxy is configured to set the standard `Forwarded` header (not just `X-Forwarded-For`); Power Platform requires the standard `Forwarded` header for trusted-proxy IP attribution.

!!! warning "Trusted-Proxy Misconfiguration Is a Bypass"
    A misconfigured reverse-proxy entry can be exploited to **spoof the client IP via a forged `Forwarded` header** if the firm's egress allows untrusted senders to reach Power Platform with the proxy's source IP. Always pin reverse-proxy entries to the **smallest possible CIDR** that contains the legitimate proxy egress addresses, and validate with SecOps that the proxy strips inbound `Forwarded` headers before adding its own. Confirm against [Microsoft Learn — IP firewall](https://learn.microsoft.com/en-us/power-platform/admin/ip-firewall) for current trusted-proxy configuration guidance.

### 8.6 Flip to enforcement

After ≥ 7 consecutive days of clean audit-only logs, and with CISO sign-off recorded in the change ticket:

1. **PPAC → Environments → {env} → Settings → Product → IP firewall**.
2. Toggle **Audit-only mode** to **Off**.
3. Click **Save**. The blade banner now displays **Enforcement enabled**.
4. Monitor Sentinel for the first 24 hours; have a documented rollback path (toggle audit-only back **On**) if a false-positive deny pattern appears.

### 8.7 Verification

- [ ] Allow-list CSV is signed by Network Engineering and AI Governance Lead.
- [ ] **Settings → Product → IP firewall** shows enforcement enabled (or audit-only with a documented end-date for the audit window).
- [ ] Sentinel query for the trailing 7 days shows zero would-be-blocked events from known-good sources.
- [ ] Test (post-enforce): from a non-allow-listed test IP (lab egress), attempt a Dataverse API call. Confirm the call is denied with the expected firewall-deny error.
- [ ] Purview Audit shows `UpdateManagedEnvironmentSettings` events for both the enable and the audit-to-enforce flip.

!!! example "Examiner Evidence Box — IP Firewall Enforcement"
    | Element | Value |
    |---|---|
    | Artifact produced | Signed allow-list CSV; Sentinel report of audit-only window with zero would-be-blocked events for ≥ 7 consecutive days; CISO sign-off email in change ticket; screenshot of Enforcement enabled |
    | Retention duration | 6 years (FINRA 4511 / SEC 17a-4) |
    | Regulatory mapping | FINRA 3110 (supervisory perimeter control), GLBA §501(b) (administrative + technical safeguards), NYDFS 23 NYCRR 500.07 (access privileges), FFIEC IT Handbook (network controls) |

---

## 9. IP-Based Cookie Binding

### 9.1 What it does

IP-based cookie binding ties an authenticated session cookie to the **source IP** that obtained the cookie. If the cookie is replayed from a different source IP, Power Platform invalidates it and forces re-authentication. This reduces the impact of token-replay attacks (e.g., AiTM phishing kits that steal session cookies) by binding the session to the network location at issuance.

It is **complementary** to Conditional Access token-binding policies, not a replacement. Use both for Zone 3.

### 9.2 Configure

1. **PPAC → Environments → {env} → Settings → Product → IP-based cookie binding**.
2. Toggle to **On**.
3. Click **Save**.

!!! warning "User-Experience Impact for Mobile / Roaming Users"
    Users on mobile networks or who roam between Wi-Fi and cellular will see frequent re-authentication prompts. Document this in the firm's user-communications plan before enabling on a Zone 3 environment with a mobile maker population. Consider deploying with a phased pilot group first.

### 9.3 Verification

- [ ] **Settings → Product → IP-based cookie binding** shows **On**.
- [ ] Test: capture a session cookie in browser A on IP-1; replay the cookie in browser B from IP-2; confirm Power Platform invalidates the session and forces re-auth.
- [ ] Purview Audit shows `UpdateManagedEnvironmentSettings` event with the cookie-binding delta.

---

## 10. Customer Lockbox

### 10.1 What it does

Customer Lockbox requires **explicit customer approval** before a Microsoft engineer can access tenant data during a support escalation. Without Lockbox approval, Microsoft engineers cannot view, copy, or modify customer data, even when troubleshooting a support case. Approval requests appear in the M365 admin center and are time-bound.

### 10.2 Enable tenant-wide

Customer Lockbox is enabled at the **tenant** level in the M365 admin center; the per-environment Managed-Environments setting confirms the environment honors the tenant Lockbox policy.

1. **M365 admin center → Settings → Org settings → Security & privacy → Customer Lockbox**.
2. Toggle **Require approval for all data access requests** to **On**.
3. Configure the **Approver** group — typically the CISO + designated alternate. This must be a **named human approver group**, not a service principal.
4. Click **Save**.

### 10.3 Confirm at the per-environment Managed Environment surface

1. **PPAC → Environments → {env} → Settings → Product → Customer Lockbox**.
2. Confirm the blade shows **Customer Lockbox: Enabled** (inherited from the tenant policy).

### 10.4 Operational handling of a Lockbox request

When a Microsoft support engineer requests access via Lockbox:

1. The named Approver group receives an email and an admin-center notification.
2. The Approver opens **M365 admin center → Support → Customer Lockbox requests**, reviews the support case, the requested scope, and the time-bound access window.
3. The Approver **Approves** or **Denies** with a documented justification.
4. The decision and the support case ID are written to Purview Audit as a `CustomerLockbox*` event. The decision audit entry is preserved per [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md).

### 10.5 Verification

- [ ] **M365 admin center → Customer Lockbox** shows **On** with named approver group.
- [ ] Per-environment **Customer Lockbox** blade shows **Enabled**.
- [ ] Approver-group membership audit (last 90 days) confirms only authorized human accounts.
- [ ] Test (annual exercise): coordinate with Microsoft support to generate a synthetic Lockbox request; document the approve/deny path end-to-end.

---

## 11. Customer-Managed Keys (CMK)

### 11.1 What CMK does

Customer-Managed Keys (CMK) bring tenant control of the encryption key used to encrypt Dataverse data at rest, in conjunction with Azure Key Vault. The key is created and managed in the firm's Azure subscription; Microsoft uses the key to wrap the per-environment data-encryption keys; key revocation by the firm renders the environment data inaccessible. CMK is a regulatory expectation in many FSI scenarios (NYDFS 500, certain bank examiner positions on key-control).

### 11.2 Documented CMK exclusions

Per [Microsoft Learn — Customer-managed key — Excluded data](https://learn.microsoft.com/en-us/power-platform/admin/customer-managed-key#excluded-data), the following data categories are **NOT** encrypted by CMK even when CMK is enabled:

| Excluded category | Implication |
|---|---|
| Maker welcome content | See §6 — do not place Confidential text here |
| Solution-checker results metadata | Treat as Microsoft-managed metadata; do not place Confidential text in solution names that surface in checker output |
| Power Apps display names and descriptions | Treat as tenant metadata; classify accordingly |
| Connection metadata | Connection display names, accounts, target endpoints; do not embed credentials in display names |
| Copilot Studio data sent as part of Agent 365 security audit logging | Audit-trail content emitted to the Agent 365 / M365 governance pipeline; document in WSP that this telemetry is service-managed |

**Verify the current excluded-data list against Microsoft documentation each quarter** — Microsoft can add or remove categories as the platform evolves. Document any change in the firm's risk register.

### 11.3 Sovereign-cloud CMK coverage differs

The set of services covered by CMK in **GCC High** and **DoD** differs from the commercial coverage. Do not assert CMK coverage in your control narrative without validating the per-service support matrix in the cloud you operate in. Check [Microsoft Learn — Customer-managed key — US Government](https://learn.microsoft.com/en-us/power-platform/admin/customer-managed-key) and the Power Platform US Government documentation.

### 11.4 Prerequisites

- Azure subscription owned by the firm with **Key Vault** provisioned in the **same Azure region** as the Power Platform environment.
- Azure Key Vault configured with **purge protection enabled** and **soft-delete enabled** (Microsoft will not accept a key from a Key Vault without these).
- Two named Key Vault Administrators (PIM-eligible).
- Power Platform Enterprise Policy created — this is a separate Azure resource type that links Power Platform environments to the Key Vault key.
- Both **Power Platform Admin** and **Entra Global Admin** roles activated for the operator performing the Enterprise Policy assignment.

### 11.5 Create the Enterprise Policy and assign

1. In the Azure portal, create a Key Vault key (RSA-HSM 2048 or 3072) with rotation policy aligned to the firm's key-rotation standard (illustrative default: rotate every 365 days, retain 4 prior versions).
2. Grant the Power Platform service principal `Key Vault Crypto Service Encryption User` role on the key.
3. In **PPAC → Policies → Enterprise policies → Encryption**, click **+ New policy**.
4. Name the policy (e.g., `cmk-prod-zone3-eastus`), pick the Azure subscription, the Key Vault, and the key version. Click **Save**.
5. The Enterprise Policy is created and visible in the encryption policies list.
6. From the policy's command bar, click **Add environment**. Select the Managed Environments to bind to this CMK policy.
7. Click **Save**. The portal initiates a **lock-then-encrypt-then-unlock** sequence per environment. The environment becomes **read-only** during the encryption transition (typically tens of minutes for small environments; can extend to many hours for large Dataverse environments). Schedule this operation in a maintenance window with the business.

### 11.6 Verification

- [ ] Enterprise Policy lists the target environments under **Bound environments**.
- [ ] Per-environment **Settings → Product → Customer-managed key** shows **Status: Encrypted with customer-managed key** and the key URI.
- [ ] Azure Key Vault diagnostic logs show wrap/unwrap operations from the Power Platform service principal.
- [ ] Documented CMK rotation runbook exists (operator, cadence, evidence).
- [ ] Document in the firm's risk register the CMK exclusion categories from §11.2 and the firm's compensating controls for them.

!!! example "Examiner Evidence Box — CMK Assignment"
    | Element | Value |
    |---|---|
    | Artifact produced | Screenshot of Enterprise Policy with bound environments; per-environment screenshot of CMK status with key URI; Azure Key Vault diagnostic-log export showing first wrap operations; documented rotation runbook with named operator |
    | Retention duration | 6 years (FINRA 4511 / SEC 17a-4) |
    | Regulatory mapping | NYDFS 23 NYCRR 500.15 (encryption), GLBA §501(b) (technical safeguards), OCC 2011-12 (technology risk — cryptographic-key control), FFIEC IT Handbook |

---

## 12. Tenant Isolation

### 12.1 Scope

Tenant Isolation governs **inbound and outbound cross-tenant connector flows that authenticate via Microsoft Entra ID**. When enabled, the platform denies cross-tenant connector authentications except where the partner tenant ID is explicitly added to an inbound or outbound allow-list. It is the platform-layer counterpart to Entra Cross-Tenant Access Settings.

**Scope limit — Entra-authenticated connectors only.** Connectors that do not use Entra ID for authentication (custom connectors, on-premises connectors using gateway accounts, OAuth-via-third-party-IdP connectors) are **not** in scope of Tenant Isolation. Govern those with DLP and ACP ([Control 1.5](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md), [Control 1.4](../../../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md)).

### 12.2 Known issue — Azure DevOps connector exception

The Azure DevOps connector authenticates against the Azure DevOps tenant configured for the connection, which may be a tenant other than the host Power Platform tenant even within the same firm (legacy ADO acquisitions). Tenant Isolation can produce **false-positive denies** for Azure DevOps connector flows where the ADO tenant ≠ the Power Platform tenant. Microsoft has documented this as a known-issue exception. Mitigation: pin Azure DevOps to a designated DLP non-business or business group with explicit endpoint allow-list, and add the ADO tenant ID to the Tenant Isolation outbound allow-list. Re-test after any Microsoft platform update.

### 12.3 Configure

1. **PPAC → Security → Identity and access → Tenant isolation**.
2. Toggle **Tenant isolation** to **On**.
3. Choose default direction:
   - **Inbound from other tenants: Allow / Deny**
   - **Outbound to other tenants: Allow / Deny**
   - Recommended Zone 3: **Deny by default in both directions**, then add named partner tenant IDs to the allow-list.
4. Add allow-list entries: tenant ID GUID + direction (Inbound, Outbound, Both) + description (partner / counterparty name and BAA reference).
5. Click **Save**.

### 12.4 Verification

- [ ] **Tenant isolation** shows **On** with the configured default direction and allow-list.
- [ ] Test: a connector flow from a non-allow-listed tenant should fail with a tenant-isolation-denied error.
- [ ] Allow-list entries are documented in the firm's third-party register with associated BAA / DPA references.
- [ ] Quarterly review of allow-list with Vendor Risk Management.

---

## 13. Environment Routing

### 13.1 What it does (and what it does NOT do)

Environment routing automatically directs **new makers** (a user who creates their first Power App or cloud flow) into a designated **personal developer environment** or environment group, instead of the default tenant-wide environment. This supports the [Control 2.2](../../../controls/pillar-2-management/2.2-environment-groups-and-tier-classification.md) tier-classification model by ensuring new makers do not start in a Zone 3 environment by accident.

**Environment routing does NOT choose region or data residency.** Region is set at environment provisioning. Routing only decides **which existing environment** a new maker is dropped into; the region of that environment was already determined by whoever provisioned it. To control region for new makers, configure **environment provisioning policies** at the tenant level so that auto-provisioned personal developer environments land in the correct region (see [Control 2.15 — Region Selection and Data Residency](../../../controls/pillar-2-management/2.15-environment-routing.md)).

### 13.2 Configure

1. **PPAC → Settings → Environment routing**.
2. Toggle **Environment routing** to **On**.
3. Choose the routing target:
   - **New developer environment per maker** (the platform auto-provisions a personal developer environment in the configured region the first time the maker arrives)
   - **An existing environment group** (the maker is added to a designated environment group)
4. Configure the maker-experience text (welcome message, link to firm WSP).
5. Click **Save**.

### 13.3 Verification

- [ ] **Settings → Environment routing** shows **On** with the configured target.
- [ ] Test: with a maker test account that has never created a Power Platform resource, create a canvas app via [`https://make.powerapps.com`](https://make.powerapps.com). Confirm the maker lands in the routed environment, **not** in the default environment.
- [ ] Confirm the default environment is **not** itself a Zone 3 environment (the default environment must be Zone 1 — see [Control 2.2](../../../controls/pillar-2-management/2.2-environment-groups-and-tier-classification.md)).

---

## 14. Pipeline Targets — Managed Environment Status

### 14.1 Why pipeline targets must be Managed Environments

Power Platform Pipelines (the in-product ALM pipelines surface) deploys solutions from a development environment to test and production targets. **Every target of a pipeline must be a Managed Environment** so the destination enforces sharing limits, solution-checker, IP firewall, CMK, and audit baseline. A non-Managed pipeline target is an ungoverned promotion landing pad — solutions imported there bypass the entire Managed-Environments substrate.

### 14.2 Verify pipeline-target status

1. **PPAC → Environments**. Filter the table by **Type = Production** and **Type = Sandbox**.
2. Cross-reference the environments referenced by your firm's pipelines (in the **Pipelines** experience inside the Power Platform pipelines admin app).
3. For every environment that is a pipeline target, confirm **Managed: Yes**.
4. For any pipeline target showing **Managed: No**, enable Managed Environment per §2 immediately, with the appropriate zone baseline.

### 14.3 Pipeline Governance Cleanup solution

The companion `FSI-AgentGov-Solutions` repository (see [`docs/reference/solutions-index.md`](../../../reference/solutions-index.md)) ships a **Pipeline Governance Cleanup** solution that includes a scheduled cloud flow to detect non-Managed pipeline targets and notify the AI Governance Lead. Deploy it to a Zone 3 management environment and target the cloud flow at all environments to receive a weekly delta report.

### 14.4 Verification

- [ ] All pipeline targets in the firm's pipeline catalog show **Managed: Yes**.
- [ ] Pipeline Governance Cleanup solution is deployed and emitting weekly delta reports to the named distribution list.
- [ ] Quarterly attestation by the AI Governance Lead that no non-Managed pipeline targets exist.

---

## 15. Microsoft Agent 365 / M365 Admin Center Governance Integration

### 15.1 Scope and complementarity

Microsoft 365 admin center exposes the **Agent 365** governance console for agents authored in Copilot Studio that surface in Microsoft 365 Copilot or Microsoft Teams. This is **complementary** to the per-environment Managed-Environments substrate — Managed Environments govern the **author-time** environment in which the agent is built, while Agent 365 governs the **tenant-wide runtime** distribution and visibility of the published agent in M365 Copilot.

For full Agent 365 console coverage, see [Control 2.25 — Agent 365 Admin Center Governance Console](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md) and its [`portal-walkthrough.md`](../2.25/portal-walkthrough.md). This section documents only the **handoff points** between Managed Environments and Agent 365.

### 15.2 Handoff points

| Surface | Managed Environments role | Agent 365 role |
|---|---|---|
| Author-time sharing limit on a Copilot Studio agent | §4.5 sets the per-environment author-time share cap | Not applicable |
| Publish-time approval to M365 Copilot | Not applicable | Pending Requests queue with named approver |
| Runtime distribution to Teams or M365 Copilot users | Not applicable | Agent 365 governance policies (allow / block / scope by Entra group) |
| Audit trail of agent invocations | Dataverse + Purview Audit (per §6.2 CMK exclusion warning for Copilot Studio audit) | Agent 365 audit log + Purview Audit |
| Maker's first-entry policy acknowledgment | §6 maker welcome content | Not applicable |

### 15.3 Operational checklist

- [ ] AI Governance Lead is the named approver for Pending Requests in Agent 365 (configured per [Control 2.25](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md)).
- [ ] Every Copilot Studio agent published from a Managed Environment routes through the Agent 365 Pending Requests queue.
- [ ] Sentinel ingests Agent 365 audit events ([Control 3.9](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md)).
- [ ] Quarterly attestation: the firm's agent inventory ([Control 1.2](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md), [Control 3.1](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md)) reconciles to Agent 365's view of published agents in the tenant.

!!! warning "Agent 365 Sovereign-Cloud Status"
    Agent 365 reached commercial GA on May 1, 2026. **No GA date has been announced for GCC, GCC High, DoD, or China (21Vianet)** at the time of this playbook. In sovereign clouds, substitute the §18 manual quarterly attestation pipeline.

---

## 16. Maker / Approver / Admin Separation

### 16.1 Why segregation of duties matters here

Managed Environments enforce a number of controls that depend on segregation of duties for their operating effectiveness — for example, solution-checker Block (§5) is meaningful only if the maker who authored the solution is not the same person as the operator who can flip enforcement to **Warn**. Apply SoD to the three personas:

- **Maker** — authors apps, flows, agents in a development environment.
- **Approver** — approves promotions through pipelines (technical approver) and approves the WSP-required pre-deployment review (governance approver).
- **Admin** — operates the Managed Environments substrate (this playbook).

No human should hold more than one of these personas for the same environment in Zone 3. See [Control 2.8 — Segregation of Duties (SoD)](../../../controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md) for the full SoD matrix and Entra Identity Governance Access Reviews configuration.

### 16.2 Implement via Entra security groups

1. In Entra, create three security groups per Zone 3 environment:
   - `pp-{env-shortname}-makers`
   - `pp-{env-shortname}-approvers`
   - `pp-{env-shortname}-admins`
2. Configure Entra **Identity Governance → Access reviews** to review each group quarterly. Reviewer = AI Governance Lead.
3. **PPAC → Environments → {env} → Settings → Users + permissions → Users**: assign the `pp-{env-shortname}-makers` group with the **Environment Maker** Dataverse security role.
4. Assign the `pp-{env-shortname}-admins` group at the tenant level only via PIM activation of the Power Platform Admin role; do **not** add to per-environment Dataverse roles.
5. Approver group is assigned in the Pipelines configuration (separate surface; see [Control 2.3](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md)).

### 16.3 Verification

- [ ] Three security groups exist per Zone 3 environment with the documented naming convention.
- [ ] Quarterly Access Reviews are configured and the most recent review shows zero overlapping memberships across the three groups.
- [ ] Purview Audit `Add member to role` events for the Power Platform Admin role show only PIM activations (not standing assignments).

---

## 17. Inactive Resource View — Orphan Detection Feed

### 17.1 What the inactive resource view shows

The **Inactive resources** blade lists Power Platform resources (apps, flows, custom connectors, agents) that have not been used within a configurable inactivity window (default 90 days). It is the primary input feed for [Control 3.6 — Orphaned Agent Detection and Remediation](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md).

### 17.2 Configure

1. **PPAC → Environments → {env} → Analytics → Inactive resources**.
2. Set the **Inactivity window** to **90 days** (illustrative default — align to the firm's WSP).
3. Schedule the **Inactive resources** export to run weekly with output to a named SharePoint Online document library owned by the AI Governance Lead.

### 17.3 Routing to Control 3.6

The Pipeline Governance Cleanup solution (referenced in §14.3) and the orphan-detection workflow ([Control 3.6](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md)) consume the weekly inactive-resources export. Each candidate resource is enriched with: maker UPN (if still in the directory), last-modified timestamp, sharing scope, and connection inventory; routed to the maker for "use, transfer, or decommission" decision; and timed-out to decommission after the firm's documented response window.

### 17.4 Verification

- [ ] Inactive resources blade shows the configured window.
- [ ] Weekly export is landing in the named SharePoint library.
- [ ] Control 3.6 workflow consumes the export and produces decision-aged reporting for the AI Governance Lead.

---

## 18. Sovereign Cloud Compensating Controls

For **GCC, GCC High, DoD, and China (21Vianet)** environments where the §7 weekly digest and the §15 Agent 365 governance integration are unavailable (or where CMK service coverage differs per §11.3), apply this consolidated compensating-control matrix and document each named owner in the firm's WSP.

### 18.1 Compensating-control matrix

| Commercial feature unavailable | Sovereign-cloud substitute | Named owner | Cadence | Evidence |
|---|---|---|---|---|
| Weekly usage-insights digest (§7) | Microsoft Graph activity exports → Purview audit ingestion → Sentinel workbook with KQL queries equivalent to the digest contents | AI Governance Lead | Weekly review; quarterly attestation | Sentinel workbook export; signed-off review minutes; 6-year retention |
| Agent 365 governance console (§15) | Manual quarterly attestation: Power Apps admin app + Power Automate admin app + Copilot Studio admin app exports reconciled against Entra published-agent registrations and against [Control 1.2](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md) registry | AI Governance Lead | Quarterly | Reconciliation workbook + signed attestation; 6-year retention |
| CMK partial service coverage (§11.3) | Per-service inventory: list each Power Platform service used in the environment; mark CMK-covered vs Microsoft-managed-key for each; document residual risk in firm's risk register; offset with stricter [Control 1.5](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) DLP and tenant-level Customer Lockbox | CISO | Quarterly review | Per-service CMK coverage CSV; risk-register entry; 6-year retention |
| Customer Lockbox unavailable (China only) | Document Microsoft access exclusion in WSP; require contractual approval from Microsoft for any data-access escalation in China cloud | CISO + Legal | Per support case | Contract clause; per-incident approval evidence; 6-year retention |

### 18.2 Substitute Sentinel workbook outline (for §18.1 row 1)

The Sentinel substitute for the weekly digest aggregates over a rolling 7-day window, per environment GUID:

- Active maker count (distinct UPN with a `MakerSession` event)
- App launch count and top-N apps by launch count
- Cloud flow run count and failure count
- Solution-checker result counts by severity
- Sharing-limit enforcement event count (if logged in audit)
- IP firewall would-be-blocked / blocked event counts
- New users routed via Environment Routing (§13)

The workbook is deployed to the firm's Sentinel workspace and emails the §7.1 distribution lists every Monday 09:00 UTC via a Logic App.

### 18.3 Quarterly sovereign-substitute attestation

The AI Governance Lead signs a quarterly attestation that:

- The compensating controls in §18.1 are operating.
- No commercial-only feature has been claimed in a regulator-facing artifact for a sovereign-cloud environment.
- The firm's WSP language for sovereign clouds reflects the actual implemented substitute pipeline.

The signed attestation is preserved in the governance evidence library for 6 years.

---

## 19. Closing Decision Matrix — Portal vs PowerShell vs Graph

| Task | Portal (this playbook) | PowerShell ([`./powershell-setup.md`](./powershell-setup.md)) | Microsoft Graph / Power Platform API |
|---|---|---|---|
| First-time enable on a single environment with operator review of every wizard step | ✅ Best | OK for known-good baseline | Not recommended |
| Bulk enable across an environment group with uniform baseline | OK (UI bulk wizard) | ✅ Best (idempotent script with change log) | OK |
| Rotate sharing-limit values in response to incident | ✅ Best (visible audit of change) | OK | OK |
| Add CIDR to IP firewall allow-list | ✅ Best (immediate visual confirmation) | OK | OK |
| Flip IP firewall from audit-only to enforce | ✅ Best (CISO present at the keyboard) | Not recommended | Not recommended |
| Bind a new environment to an existing CMK Enterprise Policy | ✅ Best (Enterprise Policy + maintenance window coordination) | OK with strict change control | OK with strict change control |
| Daily "is every Zone 3 env still Managed?" check | OK (column filter) | ✅ Best (script + Sentinel alert) | ✅ Best |
| Tenant Isolation allow-list periodic review | ✅ Best (visual cross-reference with vendor register) | OK | OK |
| Disable Managed Environment (irreversible re-baseline path) | ✅ Best (CISO + AI Gov Lead both present) | Not recommended | Not recommended |
| Customer Lockbox approval handling | ✅ Best (M365 admin center) | Not applicable | Not applicable |
| Pipeline-target Managed-status sweep | OK (column filter) | ✅ Best (scheduled flow + Sentinel alert) | ✅ Best |

Use the portal for changes that benefit from operator-in-the-loop visual confirmation and from organic audit attribution to the operator's UPN. Use PowerShell or Graph for repeated, high-volume, or scheduled operations where the change log is the primary audit artifact.

---

## Cross-References

- [Control 2.1 — Managed Environments (control specification)](../../../controls/pillar-2-management/2.1-managed-environments.md)
- [Control 2.2 — Environment Groups and Tier Classification](../../../controls/pillar-2-management/2.2-environment-groups-and-tier-classification.md)
- [Control 2.3 — Change Management and Release Planning](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md)
- [Control 2.6 — Model Risk Management Alignment with OCC 2011-12 / SR 11-7](../../../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md)
- [Control 2.8 — Segregation of Duties (SoD)](../../../controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md)
- [Control 2.12 — Supervision and Oversight (FINRA Rule 3110)](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md)
- [Control 2.14 — Maker Training and Enablement](../../../controls/pillar-2-management/2.14-training-and-awareness-program.md)
- [Control 2.15 — Region Selection and Data Residency](../../../controls/pillar-2-management/2.15-environment-routing.md)
- [Control 2.25 — Agent 365 Admin Center Governance Console](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md)
- [Control 1.2 — Agent Registry and Integrated Apps Management](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md)
- [Control 1.4 — Advanced Connector Policies (ACP)](../../../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md)
- [Control 1.5 — Data Loss Prevention and Sensitivity Labels](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md)
- [Control 1.7 — Comprehensive Audit Logging and Compliance](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md)
- [Control 3.1 — Agent Inventory and Metadata Management](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md)
- [Control 3.6 — Orphaned Agent Detection and Remediation](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md)
- [Control 3.9 — Microsoft Sentinel Integration](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md)
- [Companion playbooks: PowerShell setup](./powershell-setup.md), [Verification testing](./verification-testing.md), [Troubleshooting](./troubleshooting.md)
- [Solutions catalog](../../../reference/solutions-index.md) — Pipeline Governance Cleanup, Sentinel governance workbook
- [Microsoft Learn — Managed Environments overview](https://learn.microsoft.com/en-us/power-platform/admin/managed-environment-overview)
- [Microsoft Learn — Customer-managed key](https://learn.microsoft.com/en-us/power-platform/admin/customer-managed-key)
- [Microsoft Learn — IP firewall](https://learn.microsoft.com/en-us/power-platform/admin/ip-firewall)
- [Microsoft Learn — Solution checker enforcement](https://learn.microsoft.com/en-us/power-platform/alm/devops-build-tools)

---

## Appendix A — Operating Cadence Summary (Illustrative SLAs)

The cadences below are illustrative defaults; the firm's documented WSP cadences are what examiners hold the firm to. Replace each row with the firm's actual SLA before treating this table as evidence.

| Activity | Cadence | Owner | Output artifact | Retention |
|---|---|---|---|---|
| License-consumption precheck before any new Managed Environment enable | Per change | Power Platform Admin | Annotated `License-consumption-{env}-{date}.csv` attached to change ticket | 6 years |
| License-consumption precheck before June 2026 enforcement | T-30 days; T-7 days | Power Platform Admin | Two annotated CSVs in change ticket; CISO notification on residual gap | 6 years |
| Weekly digest review (commercial) | Weekly (Monday 09:00 ET) | AI Governance Lead delegate | Signed-off review note in governance evidence library | 6 years |
| Sovereign substitute Sentinel review (sovereign) | Weekly (Monday 09:00 ET) | AI Governance Lead delegate | Signed-off Sentinel workbook screenshot + review note | 6 years |
| Quarterly sovereign substitute attestation | Quarterly | AI Governance Lead | Signed attestation cover letter | 6 years |
| Sharing-limit posture review | Quarterly | AI Governance Lead + Compliance Officer | Signed posture review minutes | 6 years |
| Solution-checker exception register review | Monthly | AI Governance Lead | Exception register snapshot with disposition column | 6 years |
| IP firewall allow-list review | Monthly | Network Engineering + AI Governance Lead | Signed CIDR list (current vs prior diff) | 6 years |
| CMK key rotation | Per firm key-rotation standard (illustrative: 365 days) | Key Vault Administrator + Power Platform Admin | Rotation ticket with old/new key versions, audit-log proof of wrap operations | 6 years |
| CMK exclusion-categories review (services + categories) | Quarterly | CISO | Updated CMK coverage CSV; risk-register entry on residual exposure | 6 years |
| Customer Lockbox approver-group membership review | Quarterly | CISO | Signed access-review export | 6 years |
| Tenant Isolation allow-list review | Quarterly | Vendor Risk Management + AI Governance Lead | Signed allow-list with BAA cross-reference | 6 years |
| Pipeline-target Managed-status sweep | Weekly (automated) + monthly (signed review) | AI Governance Lead | Pipeline Governance Cleanup weekly report; monthly attestation | 6 years |
| Inactive resources orphan review (handoff to Control 3.6) | Weekly (automated) + monthly (signed review) | AI Governance Lead | Weekly inactive-resource export; monthly orphan-disposition log | 6 years |
| Maker / Approver / Admin segregation Access Review | Quarterly | AI Governance Lead | Entra Access Review completion report | 6 years |
| Quarterly sovereign-cloud parity verification (Microsoft roadmaps) | Quarterly | AI Governance Lead | Roadmap-delta memo to CISO + Compliance | 6 years |

---

## Appendix B — Common Misconceptions and Corrections

| Misconception | Correction |
|---|---|
| "Managed Environments encrypts everything in Dataverse with our key when CMK is on." | CMK does not cover the §11.2 excluded categories. Document the exclusions and offset with adjacent controls. |
| "PAYG users can use a Managed Environment after we enable PAYG billing on the environment." | PAYG meters runtime consumption only; per-user qualifying entitlement is required for Managed Environments. |
| "Solution-checker Block protects against all unsafe authoring patterns." | Block enforces the rule catalog only. Solution checker is one input to a layered defense; it does not substitute for code review or supervisory review under FINRA 3110. |
| "Sharing limits prevent makers from giving an app to too many users." | Sharing limits constrain author-time co-author / co-owner share; they do not constrain run-time consumption of a published app. |
| "Tenant Isolation blocks all cross-tenant data movement." | Tenant Isolation governs Entra-authenticated connector flows only. Other connectors require DLP / ACP coverage. |
| "The weekly digest is a regulated record." | The digest is operational telemetry. Books-and-records retention is satisfied by Purview audit on the records label, per Control 1.7. |
| "Disable + re-enable Managed Environments rolls back to the prior configuration." | Re-enable lands in defaults — you must re-baseline. Treat disable as an irreversible operation in change management. |
| "Environment routing chooses the data residency for new makers." | Routing chooses the destination environment; the destination's region was set at provisioning. Combine with Control 2.15 to pin region. |
| "Customer Lockbox decisions are made by an automated workflow." | Lockbox approvals must be made by a named human approver group; document the decision and justification per Lockbox event. |

---

*Updated: April 2026 | Version: v1.6.2 | UI Verification Status: Current*