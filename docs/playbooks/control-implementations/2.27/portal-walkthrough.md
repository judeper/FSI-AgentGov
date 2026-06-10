# Portal Walkthrough — Control 2.27: Consumption-Entitlement Governance

!!! info "Metered Copilot consumption billing — availability and licensing context"
    This playbook configures governance over **who may incur metered Copilot spend** (Copilot Credits and pay-as-you-go consumption). Microsoft's **Copilot Credits consumption-billing model** becomes the operative metering path for several agent surfaces from **June 16, 2026** 🔎, the same day the Work IQ API moves to Copilot-Credits consumption billing. Two policy objects back metered spend: a **PAYG billing policy** (Azure subscription, tenant ceiling **50** 🔎, **budget alerts only — not a hard-stop**, covers all metered surfaces including SharePoint grounding) and a **prepaid credit policy** (no Azure subscription, tenant ceiling **10** 🔎, standalone **hard-stop**; the standalone credit-policy hard-stop is **Chat-only today** — SharePoint grounding is funded via a paired PAYG policy). Pricing context is **$0.01 per credit** 🔎 and the prepaid pack is **25,000 credits per month, non-rolling** 🔎. The **June 2026 Microsoft Copilot Studio Licensing Guide (footnotes 6 & 7)** 🔎 resolves the base zero-rating question: Copilot Studio–built agents surfaced on **Teams, SharePoint, and Microsoft 365 Copilot**, invoked under the licensed user's own identity, are **included** in the Microsoft 365 Copilot User SL at no additional charge, subject to **fair-usage limits**. **Verify the current ceilings, per-feature credit rates, footnote numbering, and the June 16 2026 switch date against Microsoft licensing documentation before wiring enforcement** — Microsoft consumption-billing surfaces are changing rapidly during this window.

!!! danger "READ FIRST — Scope and Sibling Routing"
    **This playbook configures the consumption-entitlement decision** — which users are entitled to incur metered or premium consumption through an agent, under which billing or credit policy, on which surface. It walks you through the **Microsoft 365 admin center**, the **Power Platform admin center (PPAC)**, the **Microsoft Entra admin center**, and the **Power Apps / Dataverse** surfaces required to satisfy Verification Criteria 1–8 of [Control 2.27](../../../controls/pillar-2-management/2.27-consumption-entitlement-governance.md). The companion **[Copilot Billing Governance](https://judeper.github.io/FSI-AgentGov-Solutions/solutions/copilot-billing-governance/)** 🔎 solution implements the entitlement contract, per-agent caps, and coverage-gap analysis referenced throughout.

    **This walkthrough IS for:**

    | In Scope | Surface | Outcome |
    |---|---|---|
    | Confirming Copilot licensing and at least one consumption-billing policy | M365 admin center → Billing → Licenses | Operating admin holds AI Administrator; ≥1 policy exists |
    | Establishing the PAYG billing policy (two-step add → connect) | Power Platform admin center → Billing → Billing policies | PAYG policy bound to an Azure subscription, environments connected |
    | Establishing the prepaid credit policy and choosing a configuration | M365 admin center / PPAC → Copilot capacity 🔎 | credit-only / credit + PAYG / PAYG-only recorded |
    | Registering the admission-gated security-group registry | Entra → Groups + Power Apps `fsi_cbgapprovedgrouppolicy` | Every scope group `securityEnabled` and **not** `mailEnabled` |
    | Classifying each agent's consumption pathway | CBG `Invoke-EntitlementEvaluation.ps1` inputs | Every Zone 2/3 metered agent mapped to a pathway |
    | Applying the entitlement contract per pathway | CBG entitlement engine | Materialized `(agent, user)` decisions with `ZeroRatingResolved` posture |
    | Configuring per-agent metered spend caps (Zone 3) | Power Apps `fsi_cbgcoveragegap` / cap record | Enforcement mode (enforce vs **detect-and-alert**) recorded |
    | Running the monitor-only coverage-gap analysis + sign-off | CBG coverage-gap output | Would-be-blocked population reviewed before enforcement |
    | Retaining decisions and forwarding evidence to SIEM | Dataverse retention + SIEM connector | Six-year-aligned retention, examiner-ready pipeline |

    **This walkthrough is NOT for:**

    | Out of Scope | Use Instead |
    |---|---|
    | Governing the agent's **identity** lifecycle (sponsor, access packages, decommission) | [Control 2.26 — Entra Agent ID Identity Governance](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md) |
    | **Functional** authorization (who may author / publish / invoke an agent) | [Control 1.18 — Application-Level Authorization and RBAC](../../../controls/pillar-1-security/1.18-application-level-authorization-and-role-based-access-control-rbac.md) |
    | Cost **reporting**, chargeback, and budget alerting on the spend that results | [Control 3.5 — Cost Allocation and Budget Tracking](../../../controls/pillar-3-reporting/3.5-cost-allocation-and-budget-tracking.md) |
    | Vendor / third-party AI spend oversight framing | [Control 2.7 — Vendor and Third-Party Risk Management](../../../controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md) |
    | PowerShell / Microsoft Graph automation for the same surfaces | [`./powershell-setup.md`](./powershell-setup.md) |
    | Test cases, decision-outcome assertions, and evidence collection | [`./verification-testing.md`](./verification-testing.md) |
    | Common failure modes, missing blades, and remediation steps | [`./troubleshooting.md`](./troubleshooting.md) |

!!! warning "Hedged-Language Reminder"
    This playbook helps your organization **support compliance with** SOX §404 (IT general controls over spend authorization), GLBA 501(b) (Safeguards Rule), FINRA Rule 4511 (books and records), and SEC Rule 17a-4(b)(4) (records preservation), and **contributes to** third-party AI spend oversight informed by OCC Bulletin 2023-17. **This control governs the entitlement *decision* — who may incur metered spend, under which policy, on which surface. It does not, on its own, satisfy any regulation,** and it does not by itself constitute a hard-stop on spend. Implementation requires Microsoft 365 Copilot licensing, validated change-control, and independent testing by your compliance function. Organizations should verify all configurations against their own examination workpapers and legal counsel before treating these procedures as adequate evidence.

!!! note "Model-risk guidance is adjacent context, not the primary spend authority"
    **OCC Bulletin 2026-13 (formerly OCC 2011-12)** and **Federal Reserve SR 26-2 (formerly SR 11-7)** are **model-risk-management** guidance and, in their 2026 restatements, **expressly exclude generative and agentic AI from scope**. They are cited here only as **adjacent technology-risk context** for metered AI usage; they are **not** the primary regulatory authority for a consumption-entitlement / spend control. Do not represent Control 2.27 as satisfying SR 26-2 / OCC 2026-13 model-risk obligations.

!!! info "License and Billing Prerequisites"
    | Requirement | Why | Where to verify |
    |---|---|---|
    | Microsoft 365 Copilot license for in-scope users | The base entitlement signal for the `mcp-cs` and `mcp-agentbuilder` pathways | M365 admin center → Billing → Licenses |
    | At least one consumption-billing policy (PAYG and/or prepaid credit) | Backs metered spend; the entitlement engine reads policy state | PPAC → Billing → Billing policies; M365 admin center → Copilot capacity 🔎 |
    | **AI Administrator** directory role | Manages Copilot billing policies and Entra security-group scope; prefer over Entra Global Admin for least privilege | Entra → Roles & admins (use PIM for just-in-time elevation) |
    | Azure subscription (Owner/Contributor) for PAYG | Required for the two-step add → connect billing-policy flow | Azure portal → Subscriptions |
    | Power Platform Premium + Dataverse capacity | Hosts the CBG entitlement, cap, and coverage-gap tables and the evaluation flows | PPAC → Resources → Capacity |
    | Microsoft Graph `User.Read.All` / `Group.Read.All` | License read and security-group property checks (granted to a managed identity) | Entra → App registrations / managed identity |

!!! tip "Portal Navigation May Shift During the June 2026 Rollout"
    Microsoft consumption-billing surfaces (Copilot Studio capacity, Copilot Credits, pay-as-you-go) are changing during the June 2026 rollout. If a blade name in this playbook does not match what you see, search for the underlying noun ("billing policy", "Copilot capacity", "pay-as-you-go") and consult the canonical documentation roots: [Copilot Studio billing & licensing](https://learn.microsoft.com/en-us/microsoft-copilot-studio/billing-licensing) 🔎, [Copilot Studio capacity & messages](https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-messages-management) 🔎, and [Power Platform pay-as-you-go](https://learn.microsoft.com/en-us/power-platform/admin/pay-as-you-go-overview). Screenshot anchors record the navigation verified at the **Last UI Verified** date in the control header.

---

## Document Map

| § | Section | Key Config Point | Verification Criterion |
|---|---|---|---|
| 0 | [Pre-flight Prerequisites and Triage](#0-pre-flight-prerequisites-and-triage) | KCP-1 | Gating checks |
| 1 | [Confirm Licensing and Billing Prerequisites](#1-confirm-licensing-and-billing-prerequisites) | KCP-1 | VC-1 (input) |
| 2 | [Establish the Two Policy Objects and Choose a Configuration](#2-establish-the-two-policy-objects-and-choose-a-configuration) | KCP-2 | VC-1 |
| 3 | [Register the Admission-Gated Security-Group Registry](#3-register-the-admission-gated-security-group-registry) | KCP-3 | VC-2 |
| 4 | [Classify Each Agent's Consumption Pathway](#4-classify-each-agents-consumption-pathway) | KCP-4 | VC-3 |
| 5 | [Apply the Entitlement Contract per Pathway](#5-apply-the-entitlement-contract-per-pathway) | KCP-5 | VC-4 |
| 6 | [Configure Per-Agent Metered Spend Caps (Zone 3)](#6-configure-per-agent-metered-spend-caps-zone-3) | KCP-6 | VC-5 |
| 7 | [Run the Pre-Enforcement Coverage-Gap Analysis (Monitor-Only) and Sign-Off](#7-run-the-pre-enforcement-coverage-gap-analysis-monitor-only-and-sign-off) | KCP-7 | VC-6, VC-7 |
| 8 | [Retain Decisions and Forward Evidence](#8-retain-decisions-and-forward-evidence) | KCP-8 | VC-8 |
| ★ | [Closing Decision Matrix — Portal vs PowerShell vs Graph](#closing-decision-matrix-portal-vs-powershell-vs-graph) | — | Operational reference |

---

## 0. Pre-flight Prerequisites and Triage

Before you click anything in any portal, run through this gate. Skipping a gate produces silent failures later — for example, the entitlement engine resolves a licensed Copilot Studio user to **Fail-closed - Zero-rating Unresolved** if the surface zero-rating posture was never recorded, and a mail-enabled group is silently **rejected** by the admission-gated registry.

### 0.1 Confirm tenant cloud and tenant ID

1. Sign in to [`https://admin.microsoft.com`](https://admin.microsoft.com) as an account that holds at least the **AI Administrator** role.
2. Confirm you are in the tenant you intend to govern (upper-right profile → **Switch directory** if you operate multiple tenants).
3. Navigate to **Settings → Org settings → Organization profile** and capture the **Tenant ID** GUID and **Primary domain**. Record both in your runbook.
4. Confirm the tenant is in the **US commercial Microsoft 365 / Power Platform cloud** — the companion CBG solution targets this cloud.

*Screenshot anchor: `docs/images/2.27/EXPECTED.md#0-1-tenant-overview` — M365 admin Organization profile showing Tenant ID and Primary domain.*

### 0.2 Confirm role coverage

| Role | Required for | Where to assign |
|---|---|---|
| **AI Administrator** | Day-to-day management of PAYG + prepaid credit policies and Entra scope groups (§1–§3, §5); Copilot usage exports | Entra → Roles & admins (prefer over Global Admin; use PIM for JIT) |
| **Entra Global Admin** | One-time tenant-wide setup of Copilot billing policies where required (§2) | Entra → Roles & admins |
| **Power Platform Admin** | Dataverse schema (entitlement / cap / coverage-gap tables) and evaluation flows (§4–§8) | PPAC → Roles |
| **Entra User Admin** | Admission-gated security-group registry upkeep (§3) | Entra → Roles & admins |
| **Finance / Controller** | Approves cap thresholds and spend appetite; SOX 404 ITGC documentation (§6–§7) | Business approval (not a directory role) |
| **Compliance Officer** | Retention per FINRA 4511 / SEC 17a-4(b)(4); examination evidence (§8) | Business approval (not a directory role) |
| **Business Unit Owner** | Approves entitled cohorts for their unit's agents (§5, §7) | Business approval (not a directory role) |

1. In Entra, navigate to **Identity → Roles & admins → Roles** and confirm at minimum **two named human accounts** hold each directory role (no service principals, no break-glass) per the framework's separation-of-duties expectations (SOX 404 ITGC; FFIEC IT Handbook administrative safeguards).
2. If any role shows zero or one assignee, open a ticket with your Entra owner before proceeding.

*Screenshot anchor: `docs/images/2.27/EXPECTED.md#0-2-role-assignments` — Roles & admins grid showing AI Administrator and Power Platform Admin coverage.*

!!! example "Examiner Evidence Box — Role Coverage"
    | Element | Value |
    |---|---|
    | Artifact produced | CSV export of `directoryRole` membership for AI Administrator, Power Platform Admin, and Entra User Admin (PIM-aware if PIM is in use) |
    | Retention duration | 6 years (FINRA 4511 / SEC 17a-4(b)(4)) |
    | Regulatory mapping | SOX §404 (segregation of duties over spend authorization), GLBA 501(b) (administrative safeguard) |

### 0.3 Pre-flight gate summary

Do not proceed past this section unless **all** of the following are true:

- [ ] You are signed in to the correct tenant and have captured the tenant ID.
- [ ] Tenant is in the US commercial Microsoft 365 / Power Platform cloud.
- [ ] At least two named humans hold each directory role in §0.2.
- [ ] In-scope users hold a Microsoft 365 Copilot license (verified in §1).
- [ ] At least one consumption-billing policy (PAYG and/or prepaid credit) exists or is planned (created in §2).
- [ ] The CBG Dataverse schema is deployed (`fsi_cbgbillingpolicy`, `fsi_cbgcreditpolicy`, `fsi_cbgapprovedgrouppolicy`, `fsi_cbgentitlementmaterialized`, `fsi_cbgcoveragegap`).

!!! tip "If a Gate Fails"
    Open [`./troubleshooting.md`](./troubleshooting.md) and search for the symptom (e.g., "mail-enabled group rejected" or "licensed user fails closed"). Do not attempt workarounds in production until the gate clears — most workarounds for missing licensing or policy scope create their own audit findings.

---

## 1. Confirm Licensing and Billing Prerequisites

**Key Configuration Point:** KCP-1. **Verification Criterion supported:** VC-1 (input — establishes the licensing and policy preconditions).

The entitlement contract reads three preconditions: in-scope users hold **Microsoft 365 Copilot**, at least one Microsoft Copilot **consumption-billing policy** exists, and the operating admin holds the **AI Administrator** role.

### 1.1 Confirm Microsoft 365 Copilot license coverage

1. Open [`https://admin.microsoft.com`](https://admin.microsoft.com) → **Billing → Licenses**.
2. Confirm the count of **Microsoft 365 Copilot** licenses is greater than zero and that licenses are assigned to the in-scope user population (the cohorts who will invoke metered agents).
3. Export the assigned-license report as CSV. This is the license dimension the `mcp-cs` and `mcp-agentbuilder` pathways read.

**Verify:** the licensed-user count matches the intended in-scope population. Unlicensed users on a metered Copilot Studio pathway resolve to **Block – Missing license** by design.

*Screenshot anchor: `docs/images/2.27/EXPECTED.md#1-1-copilot-license-coverage` — M365 admin Licenses page showing Microsoft 365 Copilot assigned seat count.*

### 1.2 Confirm the AI Administrator role and prefer it over Global Admin

1. In Entra, navigate to **Identity → Roles & admins → Roles** and search for **AI Administrator**.
2. Confirm the operating principal holds **AI Administrator**. Prefer it over **Entra Global Admin** for day-to-day operation (least privilege).
3. Where a one-time Global Admin action is unavoidable (initial tenant-wide policy setup in §2), use **Entra Privileged Identity Management** for just-in-time elevation rather than standing Global Admin.

*Screenshot anchor: `docs/images/2.27/EXPECTED.md#1-2-ai-administrator-role` — Roles & admins showing AI Administrator membership with PIM eligibility.*

### 1.3 Confirm at least one consumption-billing policy exists

1. Open the **Power Platform admin center** ([`https://admin.powerplatform.microsoft.com`](https://admin.powerplatform.microsoft.com)) → **Billing → Billing policies** to check for an existing **PAYG** policy.
2. For prepaid **Copilot Credits / Copilot Studio capacity**, check **M365 admin center → Billing → Your products** (or the Copilot capacity blade — navigation is changing during the June 2026 rollout 🔎).
3. If no policy exists, proceed to [§2](#2-establish-the-two-policy-objects-and-choose-a-configuration) to create one.

!!! note "PPAC label caveat — same object, two names"
    PPAC currently surfaces the PAYG policy under **Licensing → Pay-as-you-go plans**; the billing API and the CBG schema call the same object a `billingPolicy`. The **Billing → Billing policies** path used here and the **Licensing → Pay-as-you-go plans** path in [`./powershell-setup.md`](./powershell-setup.md) reach the same object — follow whichever your tenant shows.

!!! example "Examiner Evidence Box — Licensing and Policy Preconditions"
    | Element | Value |
    |---|---|
    | Artifact produced | Microsoft 365 Copilot assigned-license CSV + AI Administrator role membership export + existing-policy inventory note |
    | Retention duration | 6 years (FINRA 4511 / SEC 17a-4(b)(4)) |
    | Regulatory mapping | SOX §404 (ITGC — access to spend authorization), GLBA 501(b) (administrative safeguard) |

!!! tip "Cross-Reference"
    The PowerShell equivalent — reading policy state programmatically with `Get-BillingPolicyInventory.ps1` — is documented at [`./powershell-setup.md`](./powershell-setup.md). For "AI Administrator role assigned but billing blade missing", see [`./troubleshooting.md`](./troubleshooting.md).

---

## 2. Establish the Two Policy Objects and Choose a Configuration

**Key Configuration Point:** KCP-2. **Verification Criterion evidenced:** VC-1 (both policy objects inventoried; configuration and ceilings documented).

Two policy objects back metered spend, and you select one of three configurations. Record both objects in the CBG tables `fsi_cbgbillingpolicy` (PAYG) and `fsi_cbgcreditpolicy` (prepaid credit).

!!! danger "PAYG Is Alert-Only — Not a Hard-Stop"
    The **PAYG billing policy** provides **budget alerts only**, not a programmatic hard-stop. A single broadly-shared metered agent can accumulate PAYG charges faster than budget alerting reacts.     Only the **prepaid credit policy** carries a standalone hard-stop, and as a standalone mechanism it is **Chat-only today** (SharePoint grounding requires a paired PAYG policy). Do not document PAYG as a spend ceiling that blocks consumption.

### 2.1 Create the PAYG billing policy (two-step add → connect)

The Power Platform pay-as-you-go flow is a **two-step add → connect**: you first *add* a billing policy bound to an Azure subscription, then *connect* environments to it.

1. Sign in to [`https://admin.powerplatform.microsoft.com`](https://admin.powerplatform.microsoft.com) as **AI Administrator** (or, for the one-time setup, an Azure subscription Owner under PIM).
2. Navigate to **Billing → Billing policies → New billing policy** (step 1 — *add*). *(PPAC may label this **Licensing → Pay-as-you-go plans → New billing plan**; it is the same `billingPolicy` object the billing API and the CBG schema use.)*
   - **Name:** `cbg-payg-metered-consumption`.
   - **Azure subscription / resource group / region:** select the subscription that will be metered. The operating identity needs Owner or Contributor on the subscription.
   - Click **Create**.
3. Open the new billing policy → **Environments → Add environments** (step 2 — *connect*). Add the environments whose metered agents should bill against this policy.
4. Record the **tenant ceiling of 50** 🔎 (verify the current value against Microsoft documentation) on the CBG `fsi_cbgbillingpolicy` row.

**Verify:** the billing policy shows **Connected environments > 0**. A billing policy with no connected environments meters nothing.

*Screenshot anchor: `docs/images/2.27/EXPECTED.md#2-1-payg-billing-policy-connected` — PPAC Billing policy detail with connected environments and Azure subscription binding.*

### 2.2 Establish the prepaid credit policy

1. Provision **Copilot Credits / Copilot Studio capacity** via **M365 admin center → Billing → Purchase services** (or the Copilot capacity blade — verify current navigation 🔎). The prepaid pack is **25,000 credits per month, non-rolling** 🔎 — unused credits do not carry over.
2. Record the **tenant ceiling of 10** 🔎 and the standalone **hard-stop** behavior on the CBG `fsi_cbgcreditpolicy` row.
3. Note the constraint: the standalone **credit-policy hard-stop is Chat-only today** — SharePoint-grounded consumption continues to bill against the PAYG policy from §2.1, and prepaid-pack credits reach SharePoint only via that paired PAYG configuration.

*Screenshot anchor: `docs/images/2.27/EXPECTED.md#2-2-credit-policy-capacity` — Copilot capacity / credits page showing prepaid pack and ceiling.*

### 2.3 Choose the configuration and document the spend scope

Select the configuration that matches the surfaces in use, and record it as a configuration note:

| Configuration | When to choose | Surface coverage |
|---|---|---|
| **credit-only** | Chat-surface agents only; no SharePoint grounding | Chat metered via credit hard-stop |
| **credit + PAYG** | Chat **and** SharePoint-grounded agents | Chat on credit; SharePoint on PAYG (alerts only) |
| **PAYG-only** | SharePoint grounding present; no prepaid credit pack | All metered surfaces on PAYG (alerts only) |

The CBG `fsi_spendscope` field carries the surface (Chat vs SharePoint) so the entitlement engine and coverage-gap analysis remain surface-aware.

**Verify:** run `Get-BillingPolicyInventory.ps1 -EnvironmentUrl <url> -PayAsYouGoCeiling 50 -CreditCeiling 10` (see [`./powershell-setup.md`](./powershell-setup.md)) and confirm both policy objects appear against their ceilings.

!!! example "Examiner Evidence Box — Policy Inventory and Configuration"
    | Element | Value |
    |---|---|
    | Artifact produced | Policy inventory export (PAYG + credit) + configuration note (credit-only / credit + PAYG / PAYG-only) + recorded ceilings (PAYG 50 / credit 10) and per-feature credit-rate basis |
    | Retention duration | 6 years (FINRA 4511 / SEC 17a-4(b)(4)) |
    | Regulatory mapping | SOX §404 (ITGC over spend configuration), GLBA 501(b) (oversight of service-consumption relationship) |

!!! tip "Cross-Reference"
    For "PAYG policy created but environments not metering", see [`./troubleshooting.md`](./troubleshooting.md). For the credit-rate constants used in the coverage-gap estimate, see [§7](#7-run-the-pre-enforcement-coverage-gap-analysis-monitor-only-and-sign-off).

---

## 3. Register the Admission-Gated Security-Group Registry

**Key Configuration Point:** KCP-3. **Verification Criterion evidenced:** VC-2 (registry populated; every group `securityEnabled` and **not** `mailEnabled`).

Entitlement scoping reads Entra **security groups** held in the admission-gated registry `fsi_cbgapprovedgrouppolicy` — credit-scope groups, API-audience cohorts, and billing-policy groups. **Admission gating rejects any group that is not `securityEnabled` or that is `mailEnabled`.**

!!! danger "Mail-Enabled Groups Are Rejected"
    A **mail-enabled** group (including Microsoft 365 Groups and mail-enabled security groups) is **rejected** by the registry. Scope groups must be **security-enabled and not mail-enabled**. This is the single most common registration failure — see [`./troubleshooting.md`](./troubleshooting.md) "mail-enabled group rejected by registry".

### 3.1 Create or identify the scope groups in Entra

1. Sign in to [`https://entra.microsoft.com`](https://entra.microsoft.com) as **Entra User Admin**.
2. Navigate to **Identity → Groups → All groups → + New group**.
3. For each scope group (credit-scope, API-audience, billing-policy):
   - **Group type:** **Security** (not Microsoft 365).
   - **Mail-enabled:** leave **off** — do not assign a mail address.
   - **Name:** e.g., `sg-cbg-credit-scope`, `sg-cbg-api-audience-<agent>`, `sg-cbg-billing-policy`.
4. Add the entitled members (or use dynamic membership rules where appropriate).

**Verify:** on each group's **Overview**, confirm **Membership type = Security** and **Email = (none)**.

*Screenshot anchor: `docs/images/2.27/EXPECTED.md#3-1-security-group-not-mail-enabled` — Entra group Overview showing Security type with no mail address.*

### 3.2 Confirm the security/mail properties via Microsoft Graph

Before registering, confirm the Graph-level properties — the admission gate checks `securityEnabled = true` and `mailEnabled = false`:

1. In **Graph Explorer** ([`https://aka.ms/ge`](https://developer.microsoft.com/graph/graph-explorer)) or via the PowerShell helper in [`./powershell-setup.md`](./powershell-setup.md), read each candidate group:
   - `GET /v1.0/groups/{id}?$select=id,displayName,securityEnabled,mailEnabled,groupTypes`
2. Confirm `securityEnabled = true` and `mailEnabled = false`. A group with `groupTypes` containing `Unified` is a Microsoft 365 Group and is **mail-enabled** — it will be rejected.

### 3.3 Register the groups in the admission-gated registry

1. Open **Power Apps** ([`https://make.powerapps.com`](https://make.powerapps.com)) in the environment that hosts the CBG schema → **Tables → CBG Approved Group Policy** (`fsi_cbgapprovedgrouppolicy`).
2. Add one row per scope group, recording the group object ID, the scope role (credit-scope / API-audience / billing-policy), and the owning agent or cohort.
3. The admission gate re-validates `securityEnabled`/`mailEnabled` at evaluation time; a row whose group later becomes mail-enabled is rejected on the next run.

**Verify:** a Graph group-property check across all registered groups returns **zero mail-enabled scope groups** (this is VC-2 evidence).

!!! example "Examiner Evidence Box — Scope-Group Registry"
    | Element | Value |
    |---|---|
    | Artifact produced | `fsi_cbgapprovedgrouppolicy` registry export + Microsoft Graph group-property check (`securityEnabled`/`mailEnabled`) showing zero mail-enabled scope groups |
    | Retention duration | 6 years (FINRA 4511 / SEC 17a-4(b)(4)) |
    | Regulatory mapping | SOX §404 (ITGC over entitlement scope), GLBA 501(b) (access scoping safeguard) |

!!! tip "Cross-Reference"
    The bulk Graph property check (`Get-MgGroup`) that enumerates every registered group and flags mail-enabled entries is the basis for manifest check `2.27.d` — see [`./verification-testing.md`](./verification-testing.md).

---

## 4. Classify Each Agent's Consumption Pathway

**Key Configuration Point:** KCP-4. **Verification Criterion evidenced:** VC-3 (every Zone 2/3 metered agent classified; `unmapped` count zero or recorded as anomaly with follow-up owner).

Pathway classification maps each in-scope agent to one of `none`, `mcp-cs`, `mcp-agentbuilder`, `api-direct`, `metered`, or `unmapped`. The Work IQ `configuredTier` signal is **authoritative and evaluated first**; the Azure Resource Graph `createdIn` signal is a **last-resort fallback**.

!!! warning "`unmapped` Is an Anomaly to Investigate — Not a Block"
    An agent that resolves to `unmapped` (missing or contradictory signals) **fails open with an anomaly** — a detection defect must not deny a user. Record each `unmapped` agent with a follow-up owner and triage it within the governance cadence; do **not** treat `unmapped` as a reason to block users.

### 4.1 Supply the classification inputs

1. Confirm the upstream signals are available:
   - **`configuredTier`** from the `work-iq-usage-detection` solution (values: `NotConfigured`, `NativeMcpCopilotStudio`, `NativeApiDirect`, `Adjacent`).
   - **`createdIn`** from the `copilot-agent-inventory` solution (Azure Resource Graph `PowerPlatformResources`).
2. Until both siblings are catalog-registered, supply a fixture file and run the engine with `Invoke-EntitlementEvaluation.ps1 -InputPath <fixture.json>` (see [`./powershell-setup.md`](./powershell-setup.md)).

### 4.2 Review the pathway mapping

The classifier applies the authoritative `configuredTier` mapping first:

| `configuredTier` (Work IQ — authoritative) | Pathway |
|---|---|
| `NativeMcpCopilotStudio` | `mcp-cs` |
| `NativeApiDirect` | `api-direct` |
| `NotConfigured`, `Adjacent` (and `none` / `classic` synonyms) | `none` (the agent majority) |
| `metered` / `generative` / `grounded` / `agent-action` / `premium` | `metered` |

The `createdIn` fallback (Copilot Studio → `mcp-cs`; Agent Builder → `mcp-agentbuilder`; API/declarative → `api-direct`; missing/contradictory → `unmapped`) applies **only** when `configuredTier` is empty or unrecognized.

**Verify:** for every Zone 2 and Zone 3 metered agent, a pathway is recorded. The `none` arm is expected to be the majority (non-metered agents).

*Screenshot anchor: `docs/images/2.27/EXPECTED.md#4-2-pathway-classification-report` — pathway classification report showing per-agent pathway and the `unmapped` follow-up column.*

### 4.3 Triage any `unmapped` agents

1. For each `unmapped` agent, open its configuration and determine why both signals were missing or contradictory (e.g., a newly imported agent with no Work IQ tier yet).
2. Assign a **follow-up owner** (typically the **Business Unit Owner** or **AI Administrator**) and a triage due date.
3. The objective for VC-3 is **`unmapped` count zero, or each `unmapped` recorded as an anomaly with a follow-up owner** — zero silent denials.

!!! example "Examiner Evidence Box — Pathway Classification"
    | Element | Value |
    |---|---|
    | Artifact produced | Pathway classification report (per-agent pathway) + `unmapped` anomaly log with follow-up owners |
    | Retention duration | 6 years (FINRA 4511 / SEC 17a-4(b)(4)) |
    | Regulatory mapping | SOX §404 (completeness of the spend-control population), FINRA 4511 (books and records — governed agent inventory) |

!!! tip "Cross-Reference"
    For "agent classified `unmapped` (fail-open anomaly)" triage steps, see [`./troubleshooting.md`](./troubleshooting.md). The pathway-classification assertions back manifest check `2.27.a`.

---

## 5. Apply the Entitlement Contract per Pathway

**Key Configuration Point:** KCP-5. **Verification Criterion evidenced:** VC-4 (entitlement contract evaluated across the in-scope `(agent, user)` population; decisions materialized; `ZeroRatingResolved` posture recorded per agent).

The engine **switches on the pathway**, then applies pathway-specific eligibility. Each `(agent, user)` evaluation resolves to exactly one auditable decision: **Allow**, **Block**, **Allow - Eligibility N/A**, **Fail-open - Anomaly**, or **Fail-closed - Zero-rating Unresolved**.

### 5.1 Review the per-pathway eligibility rules

| Pathway | Eligibility rule | Typical decision |
|---|---|---|
| `none` | Always allowed | **Allow - Eligibility N/A** (the majority) |
| `mcp-agentbuilder` | Requires a Copilot license | Allow, else **Block – Missing license** |
| `mcp-cs` | Requires a Copilot license **AND** (surface zero-rated **(when `ZeroRatingResolved = true`)** **OR** user in credit scope) | Allow, **Block – Missing license**, or **Fail-closed - Zero-rating Unresolved** |
| `api-direct` | Requires membership in the API-audience cohort | Allow, else **Block – No eligible cohort** |
| `metered` | Requires membership in the eligible cohort | Allow, else **Block – No eligible cohort** (the only bounded block) |
| `unmapped` | Fails open with an anomaly | **Fail-open - Anomaly** |

### 5.2 Set the `ZeroRatingResolved` posture per agent

The `mcp-cs` arm depends on the zero-rating posture, resolved per the **June 2026 Copilot Studio Licensing Guide (footnotes 6 & 7)** 🔎 (the zero-rating substance is confirmed on [Microsoft Learn — Copilot Studio billing and licensing](https://learn.microsoft.com/en-us/microsoft-copilot-studio/billing-licensing); the footnote numbering is unverified):

1. For agents surfaced on **Teams / SharePoint / Microsoft 365 Copilot** under the licensed user's own identity, leave `ZeroRatingResolved = true` (default). A Copilot-licensed user on a zero-rated Microsoft 365 surface is **Allowed** — the license is sufficient, no credit scope required.
2. To adopt the **conservative** posture for your tenant, run the engine with `-ZeroRatingResolved:$false`. Licensed `mcp-cs` users not in credit scope then resolve to **Fail-closed - Zero-rating Unresolved** rather than a silent allow.
3. Record the chosen posture per agent on the `fsi_cbgentitlement` row (`fsi_zeroratingresolved`). 🔎 Confirm the footnote numbering and fair-usage language against the current Licensing Guide PDF.

!!! note "Zero-Rating Refinement — Confirm per Tenant"
    Unlicensed users, **non-Microsoft-365 surfaces**, and the **generative-answer-with-tenant-grounding / beyond-fair-use** refinements remain **credit-metered**. These affect credit **cost**, not the base allow/deny for the footnote-7 case. Reconcile per tenant; do not over-claim that all Copilot Studio usage is zero-rated.

### 5.3 Evaluate and materialize decisions

1. Run `Invoke-EntitlementEvaluation.ps1 -InputPath <inputs.json> -OutputPath <decisions.json> -CacheTtlMinutes 1440` across the in-scope `(agent, user)` population (see [`./powershell-setup.md`](./powershell-setup.md)).
2. Decisions are **materialized** to `fsi_cbgentitlementmaterialized` with a time-to-live (`fsi_ttlexpiresat`) so a decision is auditable without replaying inputs. The cache stores the pathway, decision, block reason, spend scope, and source policy.

**Verify:** the materialized export shows, for each `(agent, user)`, the pathway, decision, block reason (where applicable), and the recorded `ZeroRatingResolved` posture. This is VC-4 evidence and backs manifest check `2.27.a`.

*Screenshot anchor: `docs/images/2.27/EXPECTED.md#5-3-materialized-decisions` — `fsi_cbgentitlementmaterialized` rows showing pathway, decision, and block reason.*

!!! example "Examiner Evidence Box — Entitlement Decisions"
    | Element | Value |
    |---|---|
    | Artifact produced | Materialized decision export (pathway, decision, block reason, spend scope, source policy) + per-agent `ZeroRatingResolved` posture record |
    | Retention duration | 6 years (FINRA 4511 / SEC 17a-4(b)(4)) |
    | Regulatory mapping | SOX §404 (authorization of metered spend), GLBA 501(b) (administrative safeguard over consumption), 1.18 (functional access is an input) |

!!! tip "Cross-Reference"
    For "licensed user fails-closed (zero-rating not resolved / not in credit scope)" remediation, see [`./troubleshooting.md`](./troubleshooting.md). The full decision tree and pseudocode live in the companion solution's [`docs/entitlement-contract.md`](https://judeper.github.io/FSI-AgentGov-Solutions/solutions/copilot-billing-governance/).

---

## 6. Configure Per-Agent Metered Spend Caps (Zone 3)

**Key Configuration Point:** KCP-6. **Verification Criterion evidenced:** VC-5 (per-agent caps configured for all Zone 3 metered agents; enforcement mode recorded; no Zone 3 agent documented as hard-stop where the write API is unproven).

For each Zone 3 metered agent, record a per-agent cap (monthly credit cap, enforcement mode, zone classification).

!!! danger "Detect-and-Alert Where No Write API Exists — Do Not Claim a Hard-Stop"
    A public **write API for credit-policy and per-agent cap enforcement may not yet exist** 🔎. Where a programmatic hard-stop cannot be applied, enforcement **degrades to detect-and-alert**: the cap is recorded and monitored, and breaches are surfaced — but consumption is **not** programmatically blocked. **Do not document a detect-and-alert cap as a hard-stop.** The only standalone hard-stop available today is the prepaid **credit policy** (Chat-only) from §2.2.

### 6.1 Record the per-agent cap

1. Open **Power Apps** → the CBG cap record (carried alongside `fsi_cbgcoveragegap` / the cap table for the agent).
2. For each Zone 3 metered agent, set:
   - **Monthly credit cap** — the agreed spend appetite for the agent.
   - **Enforcement mode** (`fsi_cbg_enforcementmode`) — **enforce** only where a verified hard-stop mechanism exists (e.g., the credit policy's standalone hard-stop), otherwise **detect-and-alert**.
   - **Zone** — `Z3-Enterprise` (caps are mandatory for Zone 3; recommended for Zone 2 shared metered agents).
3. Obtain **Finance / Controller** approval of the cap threshold and spend appetite, and document it for SOX 404 ITGC.

**Verify:** every Zone 3 metered agent has a cap record with the enforcement mode recorded. No Zone 3 agent shows enforcement mode `enforce` unless the underlying hard-stop is verified. This is VC-5 evidence and backs manifest check `2.27.b`.

*Screenshot anchor: `docs/images/2.27/EXPECTED.md#6-1-per-agent-cap-record` — cap record showing monthly cap, enforcement mode (detect-and-alert), and zone.*

!!! example "Examiner Evidence Box — Per-Agent Caps"
    | Element | Value |
    |---|---|
    | Artifact produced | Cap-record export (per Zone 3 metered agent: monthly cap, enforcement mode, zone) + Finance / Controller approval of cap thresholds |
    | Retention duration | 6 years (FINRA 4511 / SEC 17a-4(b)(4)) |
    | Regulatory mapping | SOX §404 (approval of spend thresholds — ITGC artifact), GLBA 501(b) (oversight of consumption) |

!!! tip "Cross-Reference"
    For "cap not enforcing (no write API → detect-and-alert)" expectations, see [`./troubleshooting.md`](./troubleshooting.md).

---

## 7. Run the Pre-Enforcement Coverage-Gap Analysis (Monitor-Only) and Sign-Off

**Key Configuration Point:** KCP-7. **Verification Criteria evidenced:** VC-6 (monitor-only coverage-gap run for all metered agents) and VC-7 (would-be-blocked population reviewed and signed off; spend estimate produced and reconciled).

The coverage-gap analysis is the load-bearing **"who would be blocked"** deliverable. It runs as a **per-agent aggregate in monitor-only mode** and **must be reviewed and signed off before any enforcement is activated**.

### 7.1 Run the per-agent coverage-gap aggregate in monitor-only mode

1. Run `Invoke-EntitlementEvaluation.ps1 -InputPath <inputs.json> -OutputPath <coverage-gap.json> -SampleCap 20 -GroupSizeThreshold 500 -RetentionDays 183` (see [`./powershell-setup.md`](./powershell-setup.md)).
2. The engine writes one `fsi_cbgcoveragegap` row **per agent** (not per agent × user — aggregating per agent keeps the output bounded). Each row records:

   | Field (logical name) | Meaning |
   |---|---|
   | `fsi_pathway` | Classified pathway |
   | `fsi_eligibleusers` | Count of users eligible under current policies |
   | `fsi_blockeduserscount` | Count of intended users who **would be blocked** |
   | `fsi_blockedsampleupns` | **Capped** sample of blocked UPNs (bounded to avoid row blow-up) |
   | `fsi_blockreasonsummary` | Dominant block reason across the cohort |
   | `fsi_spendscope` | Surface-aware scope (Chat vs SharePoint) |
   | `fsi_groupsizepartition` | Intended-audience size used to partition large groups above threshold T |
   | `fsi_monitoronly` | **`true`** first — gap rows take no enforcement action |
   | `fsi_analyzedat` | Timestamp when the coverage-gap analysis produced the row |
   | `fsi_retainuntil` | Retention horizon for the aggregate |

**Verify:** every coverage-gap row shows **`fsi_monitoronly = true`** prior to enforcement activation. This is VC-6 evidence and backs manifest check `2.27.c`.

*Screenshot anchor: `docs/images/2.27/EXPECTED.md#7-1-coverage-gap-monitor-only` — `fsi_cbgcoveragegap` rows with `monitorOnly = true`, eligible count, would-be-blocked count, and capped UPN sample.*

### 7.2 Produce the coverage-gap spend estimate

Estimate coverage-gap spend from the per-feature **Copilot credit rates** (reference constants — verify current values against Microsoft licensing documentation 🔎):

| Feature | Credits 🔎 |
|---|---|
| Classic answer | 1 |
| Generative answer | 2 |
| Agent action | 5 |
| Tenant-graph grounding | 10 |
| Agent flow | 13 per 100 flow actions |

Pricing context: **$0.01 per credit** 🔎; prepaid pack **25,000 credits per month, non-rolling** 🔎.

!!! warning "Estimate, Not an Invoice"
    These figures support cost **estimation**; they do **not** produce a billing-accurate invoice. Reconcile the estimate against the **Microsoft 365 admin center** and **Azure cost reporting**. State the estimate caveat in the sign-off record.

### 7.3 Review and obtain sign-off before enforcement

1. Convene the coverage-gap review (**AI Governance Lead** owns; **Business Unit Owner** confirms the entitled cohorts for their agents; **Finance / Controller** approves the spend appetite).
2. Review the **would-be-blocked count** per agent and the capped blocked-UPN sample. Resolve any unexpected blocks (e.g., a cohort that should be in credit scope but was omitted from the registry in §3).
3. Document the **sign-off** and the reconciliation note. **Enforcement is not activated until the would-be-blocked population is signed off** — this gate is VC-7.

!!! example "Examiner Evidence Box — Coverage-Gap and Sign-Off"
    | Element | Value |
    |---|---|
    | Artifact produced | Coverage-gap export (`monitorOnly = true` on all rows) + documented sign-off on the would-be-blocked population + spend estimate with reconciliation note (M365 admin center / Azure cost reporting) |
    | Retention duration | 6 years (FINRA 4511 / SEC 17a-4(b)(4)) |
    | Regulatory mapping | SOX §404 (review and approval before enforcement — ITGC), GLBA 501(b) (administrative safeguard), FINRA 4511 (coverage-gap evidence retention) |

!!! tip "Cross-Reference"
    For "coverage-gap counts look wrong" triage and "credit policy Chat-only surprise on SharePoint", see [`./troubleshooting.md`](./troubleshooting.md).

---

## 8. Retain Decisions and Forward Evidence

**Key Configuration Point:** KCP-8. **Verification Criterion evidenced:** VC-8 (decisions and coverage-gap evidence retained per FINRA 4511 / SEC 17a-4(b)(4) and forwarded to SIEM).

### 8.1 Apply the retention horizon

1. Confirm the materialized decisions (`fsi_cbgentitlementmaterialized`) and coverage-gap aggregates (`fsi_cbgcoveragegap`) carry a retention horizon aligned to **FINRA 4511 (six-year minimum)**.
2. For Zone 3, the audit-log retention minimum is **6 years**; Zone 2 is a minimum of **1 year** (see the [zone table](#zone-coverage-summary) below). Coordinate the Dataverse retention configuration with the **Compliance Officer**.

### 8.2 Forward decisions and coverage-gap evidence to SIEM

1. Configure the export/forwarding path (Dataverse → SIEM connector, or the nightly export flow described in the companion solution's flow configuration) so entitlement decisions and coverage-gap aggregates land in the organization's SIEM.
2. Confirm ingestion end-to-end: produce a known test decision and confirm it appears in the SIEM within the expected ingestion lag.

**Verify:** the retention policy configuration is documented and SIEM ingestion is confirmed. This is VC-8 evidence.

!!! example "Examiner Evidence Box — Retention and SIEM Forwarding"
    | Element | Value |
    |---|---|
    | Artifact produced | Retention policy configuration (six-year-aligned) + SIEM ingestion confirmation (sample query + recent results) |
    | Retention duration | 6 years (FINRA 4511); SEC 17a-4(b)(4) preservation of financial/operational-control records |
    | Regulatory mapping | FINRA 4511 (books and records), SEC 17a-4(b)(4) (records preservation), SOX §404 (audit-log integrity) |

!!! tip "Cross-Reference"
    The retention and SIEM-forwarding validation steps are in [`./verification-testing.md`](./verification-testing.md). For "decisions not landing in SIEM", see [`./troubleshooting.md`](./troubleshooting.md).

---

## Zone Coverage Summary

| Requirement | Zone 1 — Personal | Zone 2 — Team | Zone 3 — Enterprise |
|---|---|---|---|
| Entitlement evaluation | Not required | Evaluated for shared metered agents; pathway recorded | Mandatory for every metered `(agent, user)`; decisions materialized |
| Billing/credit policy scoping | Not required | Registry-scoped for shared agents | Mandatory registry scoping; all groups `securityEnabled`/not `mailEnabled`; configuration documented |
| Per-agent spend caps | Not required | Recommended for shared metered agents | Mandatory; enforcement mode (enforce vs detect-and-alert) recorded |
| Coverage-gap analysis | Not required | Monitor-only before any enforcement | Mandatory with documented sign-off before enforcement |
| Spend-appetite approval | Not required | Business Unit Owner approves cohorts | Finance / Controller approves caps + appetite (SOX 404 ITGC) |
| Audit log retention | Standard tenant retention | Minimum 1 year | Minimum 6 years (FINRA 4511); forwarded to SIEM |
| Anomaly handling | N/A | `unmapped` recorded + triaged | `unmapped` fail-open with anomaly, triaged; zero silent denials |

---

## Closing Decision Matrix — Portal vs PowerShell vs Graph

| Task | Portal | PowerShell / Graph | Recommended at scale |
|---|---|---|---|
| Confirm Copilot license coverage | M365 admin → Billing → Licenses | `Get-MgUserLicenseDetail` | Portal for spot-check; Graph for the full population |
| Create PAYG billing policy (add → connect) | PPAC → Billing → Billing policies | — (portal-first; verify current API 🔎) | Portal |
| Inventory both policy objects | PPAC + Copilot capacity | `Get-BillingPolicyInventory.ps1` | PowerShell |
| Register / validate scope groups | Entra → Groups + Power Apps | `Get-MgGroup` (`securityEnabled`/`mailEnabled`) | PowerShell for the property check |
| Classify pathways | — | `Invoke-EntitlementEvaluation.ps1` | PowerShell |
| Evaluate + materialize decisions | — | `Invoke-EntitlementEvaluation.ps1` | PowerShell |
| Configure per-agent caps | Power Apps cap record | — (detect-and-alert where no write API 🔎) | Portal |
| Run coverage-gap (monitor-only) | — | `Invoke-EntitlementEvaluation.ps1` | PowerShell |
| Retain + forward to SIEM | Dataverse retention + connector | export flow | Flow |

**Where the write API is unproven** 🔎, prefer the portal/record-and-monitor (detect-and-alert) path and do not represent it as a programmatic hard-stop.

---

## Related Documentation

- [Control 2.27 — Consumption-Entitlement Governance](../../../controls/pillar-2-management/2.27-consumption-entitlement-governance.md) — the control specification (source of truth)
- [`./powershell-setup.md`](./powershell-setup.md) — PowerShell and Microsoft Graph automation for these surfaces
- [`./verification-testing.md`](./verification-testing.md) — test procedures and the manifest-check cross-walk (`2.27.a`–`2.27.d`)
- [`./troubleshooting.md`](./troubleshooting.md) — common failure modes and resolutions
- [Copilot Billing Governance — companion solution](https://judeper.github.io/FSI-AgentGov-Solutions/solutions/copilot-billing-governance/) 🔎 — implements the entitlement contract, per-agent caps, and coverage-gap analysis
- [Microsoft Copilot Studio — billing and licensing](https://learn.microsoft.com/en-us/microsoft-copilot-studio/billing-licensing) 🔎
- [Microsoft Copilot Studio — capacity and messages](https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-messages-management) 🔎
- [Power Platform — pay-as-you-go overview](https://learn.microsoft.com/en-us/power-platform/admin/pay-as-you-go-overview)

*This walkthrough governs the consumption-entitlement decision; it does not, on its own, satisfy any regulation. Verify the 🔎-flagged figures (June 16 2026 switch date, Licensing Guide footnotes 6 & 7, per-feature credit rates, $0.01/credit, 25,000-credits-per-month, tenant ceilings 50/10, and cap write-API availability) against current Microsoft documentation before treating any procedure as examiner evidence.*
