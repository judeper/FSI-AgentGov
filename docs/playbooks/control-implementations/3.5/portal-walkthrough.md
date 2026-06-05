# Portal Walkthrough — Control 3.5: Cost Allocation and Budget Tracking

> **Operating manual** for [Control 3.5 — Cost Allocation and Budget Tracking](../../../controls/pillar-3-reporting/3.5-cost-allocation-and-budget-tracking.md).
>
> **Sister playbooks:** [PowerShell Setup](powershell-setup.md) · [Verification & Testing](verification-testing.md) · [Troubleshooting](troubleshooting.md)
>
> **Last UI Verified:** April 2026 against the Microsoft 365 admin center, Power Platform admin center (`admin.powerplatform.microsoft.com`), and Azure portal (`portal.azure.com`). Re-verify portal paths each cycle before relying on automated routes.

---

!!! warning "Non-Substitution — Tooling Supports, It Does Not Replace"
    The Microsoft 365 Copilot billing policies, Azure Cost Management budgets, Power Platform capacity views, Power BI dashboards, and Purview retention policies referenced in this walkthrough are **financial-evidence and notification surfaces**. They support compliance with — they do not replace:

    - The firm's **written cost-allocation methodology** approved by Finance / the Controller and reviewed by external auditors as part of SOX 404 ITGC walkthroughs.
    - **Books-and-records retention** under SEC Rule 17a-4(b)(4) and FINRA Rule 4511 — chargeback ledgers, rate cards, and variance memos must land in WORM-equivalent storage. Cost Management exports to a non-immutable storage account are **not** records.
    - **Registered-principal supervisory review** under FINRA Rule 3110 of changes to billing policies, rate cards, and variance thresholds.
    - **Board / Audit Committee reporting** of safeguards-program funding under the FTC Safeguards Rule (GLBA 501(b)).
    - **Hard cost caps.** Azure Cost Management budgets and M365 Copilot PAYG alerts are **notification-only** surfaces — they do not stop spend. Hard caps require process: deactivation of billing policies, removal from Entra ID security groups, agent suspension via Control 2.1 environment policies, or finance-led service de-provisioning.

    A clean run of this walkthrough produces an examiner-defensible **starting point** for IT cost governance of AI-agent workloads. It does not by itself satisfy any single regulation.

---

## Document Map

| § | Section | Surface |
|---|---------|---------|
| 0 | Pre-flight prerequisites and least-privilege role planning | All |
| 1 | Establish the cost-allocation taxonomy (BU, environment, tag) | Governance design |
| 2 | Power Platform admin center — Capacity & analytics | `admin.powerplatform.microsoft.com` |
| 3 | Microsoft 365 admin center — Copilot billing & usage policies | `admin.microsoft.com` |
| 4 | Azure portal — Tagging policy and tag inheritance | `portal.azure.com` |
| 5 | Azure Cost Management — Cost views and scheduled exports (WORM-bound) | `portal.azure.com` |
| 6 | Azure Cost Management — Budget alerts (notification-only) | `portal.azure.com` |
| 7 | Power BI — Cost dashboard from Cost Management connector | `app.powerbi.com` |
| 8 | Microsoft Purview — Retention policy for chargeback artifacts | `purview.microsoft.com` |
| 9 | Operating cadence — monthly close, quarterly evidence sample | Operating model |
| 10 | Decision matrix — Portal vs PowerShell vs Graph |  |

---

## §0 Pre-flight Prerequisites and Least-Privilege Role Planning

### 0.1 Operator role prerequisites (least-privilege)

Cost-allocation work touches four trust boundaries (M365 Copilot billing, Power Platform tenant, Azure subscriptions, Purview retention). Use Privileged Identity Management (PIM) to elevate **per task**; do not maintain standing membership in tenant-wide admin roles for routine cost work.

| Task | Canonical Role (per [`role-catalog.md`](../../../reference/role-catalog.md)) | PIM-eligible? | Notes |
|------|-------------------------------------------------------------------------------|---------------|-------|
| Initial Copilot billing policy creation (one-time) | **Entra Global Admin** | Yes — short-lived elevation | After initial setup, hand off to AI Administrator. Document the elevation in the change ticket. |
| Day-to-day Copilot billing policy maintenance | **AI Administrator** | Yes | Sufficient for PAYG and Credit policy management. Do not use Global Admin. |
| Power Platform capacity reads + tag enforcement | **Power Platform Admin** | Yes | For environment-level cost analytics. |
| Azure budget creation, exports, tag policy | **Cost Management Contributor** + **Resource Policy Contributor** (Azure RBAC) | Yes | Scope to the relevant subscription / management group, not tenant-wide. |
| Cost Management read-only review (BU owners, Finance) | **Cost Management Reader** | Standing OK at narrow scope | BU owners read only their own scope. |
| Retention policy for chargeback evidence | **Purview Compliance Admin** or **Purview Records Manager** | Yes | Records Manager preferred for records-management surfaces. |
| Examiner walkthrough preparation | **Compliance Officer** + **Cost Management Reader** | Standing OK | Read-only across scope; sign-off via separate workflow. |

!!! danger "Do not attach Global Admin to a service principal for cost automation"
    Cost automation (exports, budget creation, billing-policy assignment via Graph) must use a **dedicated app registration** with the smallest scope that satisfies the operation. Global Admin on an unattended principal is an immediate FINRA Rule 3110 supervisory finding and an OCC Bulletin 2026-13 (formerly OCC 2011-12) third-party-risk concern.

### 0.2 Pre-work checklist

- [ ] Documented chart of accounts entries for each AI cost center (`CC-####`) confirmed with Controller.
- [ ] Approved rate card (CFO/Controller signature, version-numbered, dated).
- [ ] Entra ID security groups created per business unit, populated, owner attested.
- [ ] Azure subscription / management group strategy confirmed — typically one subscription per cost center, or one subscription with resource-group-per-BU and tag enforcement.
- [ ] Purview retention label `FSI-Records-FinancialBooks` exists and is scoped to the Storage account that will hold Cost Management exports (see §8).
- [ ] Change record opened for the initial setup (FINRA Rule 3110 supervisory artifact).

---

## §1 Establish the Cost-Allocation Taxonomy

The taxonomy is the most important step in this control. Every downstream surface (PPAC, Copilot billing policy, Azure tag, Power BI filter) reads from this taxonomy. Changes to the taxonomy after rollout are expensive and disrupt prior chargeback ledgers — design it once with Finance.

### 1.1 Environment naming convention

Recommended pattern: **`{BU}-{Zone}-{Lifecycle}-{Suffix}`**

| Token | Domain | Examples |
|-------|--------|----------|
| `BU` | 4–8 char business-unit code from the chart of accounts | `WEALTH`, `LENDING`, `TRADESURV`, `CORPCOMMS` |
| `Zone` | `Z1` / `Z2` / `Z3` per [zones-and-tiers.md](../../../framework/zones-and-tiers.md) | `Z3` |
| `Lifecycle` | `DEV`, `TEST`, `UAT`, `PROD` | `PROD` |
| `Suffix` | Optional: agent name, region, or instance | `ADVISOR-CHAT` |

**Example:** `WEALTH-Z3-PROD-ADVISOR-CHAT`

### 1.2 Mandatory Azure tag set

Apply via Azure Policy; report violations weekly. (Tag enforcement is Control 3.1's primary metadata surface — this control consumes the tag values.)

| Tag | Required | Allowed values | Source of truth |
|-----|----------|----------------|-----------------|
| `CostCenter` | Yes | Chart-of-accounts code (`CC-####`) | Finance / Controller |
| `BusinessUnit` | Yes | Match `BU` token | Finance |
| `Zone` | Yes | `Zone1` / `Zone2` / `Zone3` | Governance |
| `Owner` | Yes | UPN of Agent Owner | Agent inventory (Control 3.1) |
| `Application` | Yes | Agent or workload short name | Agent inventory |
| `Environment` | Recommended | `Dev` / `Test` / `UAT` / `Prod` | DevOps |
| `DataClassification` | Recommended | `Public` / `Internal` / `Confidential` / `Restricted` | Information protection |

### 1.3 BU mapping table (illustrative — replace with the firm's chart of accounts)

| BU code | Cost Center | Business Unit | Zone(s) | Finance contact |
|---------|-------------|----------------|---------|-----------------|
| `WEALTH` | `CC-1001` | Wealth Management | Z2 / Z3 | wealth-finance@example.com |
| `LENDING` | `CC-1002` | Consumer Lending | Z2 / Z3 | lending-finance@example.com |
| `TRADESURV` | `CC-1003` | Trade Surveillance | Z3 | surv-finance@example.com |
| `OPS` | `CC-1004` | Operations | Z1 / Z2 | ops-finance@example.com |
| `SHARED` | `CC-1099` | Shared Services (un-allocable) | Z1 | it-finance@example.com |

Document this mapping in a Power BI dataset or Dataverse reference table; do not hard-code into individual scripts.

---

## §2 Power Platform Admin Center — Capacity and Analytics

**Portal:** [`https://admin.powerplatform.microsoft.com`](https://admin.powerplatform.microsoft.com)

### 2.1 Capacity overview

1. Sign in as **Power Platform Admin** (PIM-elevated).
2. Navigate to **Resources → Capacity**.
3. Review the four capacity buckets:

   | Capacity | Unit | Procurement model |
   |----------|------|-------------------|
   | Dataverse storage (database, file, log) | GB | Included with licenses + add-on capacity packs |
   | AI Builder credits | Credits | Included with Premium + add-on credit packs |
   | Microsoft Copilot Studio messages | Messages | Per-tenant pool, license- and add-on-driven |
   | Power Automate per-flow / per-user runs | Runs | License-driven |

4. Drill into **Per-environment** view to see consumption by environment.
5. Note the trend curve — sustained >80 % consumption against a capacity pool warrants a procurement decision; >95 % is an immediate operational risk (new agents may fail to deploy).

### 2.2 Analytics — Copilot Studio messages

1. From PPAC, navigate to **Analytics → Copilot Studio**.
2. Filter to the rolling 30-day window.
3. Export to CSV; the export drives the chargeback in §9.

### 2.3 Environment naming + ownership audit

1. Navigate to **Environments**.
2. Sort by **Display name** and confirm every environment matches the §1.1 naming convention.
3. Open each non-conforming environment and either rename (where supported) or open a remediation ticket.
4. Confirm each environment has an active **Environment Admin** (no orphaned environments — see Control 3.6).

---

## §3 Microsoft 365 Admin Center — Copilot Billing & Usage Policies

**Portal:** [`https://admin.microsoft.com`](https://admin.microsoft.com) → **Copilot** → **Billing & usage**

### 3.1 Decide the billing model

| Model | When to use | Constraints |
|-------|-------------|-------------|
| **Per-user M365 Copilot license** | Stable, all-day Copilot user populations | Standard EA/MCA seat licensing — consumption is bundled |
| **PAYG (pay-as-you-go) billing policy** | Variable / on-demand consumption (Copilot Chat for non-licensed users; agent message overage; declarative agents) | Up to 50 active billing policies per tenant; assignment scope is **immutable** after creation |
| **Copilot Credit policy** (GA April 2026) | Departments funded from a prepaid credit pool; PAYG not desired | Same 50-policy limit; pre-purchased credit packs |

### 3.2 Create a PAYG billing policy

1. Navigate to **Copilot → Billing & usage → Billing policies**.
2. Click **+ Add a billing policy**.
3. Provide:
   - **Policy name** — encode the BU and intended scope, e.g., `WEALTH-Z3-Copilot-PAYG-2026Q2`
   - **Azure subscription + resource group** — the Azure scope that will be invoiced
   - **Scope: Specific group(s)** — assign to the BU's Entra ID security group
   - **Services covered** — pick the services (Copilot Chat, agent messages, etc.)
4. Click **Create**.

!!! danger "Scope is immutable"
    Once created, the **assigned group cannot be changed**. To change scope, delete and recreate the policy. Document deletions and recreations in your supervisory change log (FINRA 3110).

### 3.3 Create a Copilot Credit policy (April 2026 GA)

1. Same path; choose **Credit policy** instead of **PAYG**.
2. Bind to a purchased Copilot Credit pack.
3. Assign scope group.

### 3.4 Verify high-usage users (March 2026 GA)

1. Navigate to **Copilot → Usage → High-usage users**.
2. Confirm the report refreshes daily.
3. Set up a saved view filtered to the relevant policy scope.
4. The high-usage report drives the variance investigation in §9 and is the primary input to license optimization.

### 3.5 Naming and audit conventions

- Encode the policy creation quarter in the name so retired policies are easy to identify.
- Keep a tenant-level register of active policies (`policy-name`, `scope group`, `created by`, `change ticket`); reconcile monthly against the admin-center list.

---

## §4 Azure Portal — Tagging Policy and Tag Inheritance

**Portal:** [`https://portal.azure.com`](https://portal.azure.com)

### 4.1 Assign the tag-enforcement policy

1. Navigate to **Policy → Definitions**.
2. Find the built-in policy **`Require a tag and its value on resources`** (or the modern `Require a tag on resources` for tag-key-only enforcement).
3. Assign once per required tag (`CostCenter`, `BusinessUnit`, `Zone`, `Owner`, `Application`).
4. Set effect to **`Deny`** at the management-group scope so non-compliant resources cannot be created.

!!! tip "Use `Audit` first, then `Deny`"
    For brownfield tenants with existing untagged resources, assign with effect **`Audit`** for two weekly reporting cycles, remediate the report, then switch to **`Deny`**. A `Deny` policy applied without remediation lead-time will block legitimate change tickets.

### 4.2 Configure tag inheritance from resource group → resource

1. Assign the built-in policy **`Inherit a tag from the resource group if missing`** for each cost-allocation tag.
2. Inheritance reduces tag-application errors at the resource level — essential for cost attribution where individual resources are created by Power Platform (where direct tag setting is not always available).

### 4.3 Confirm coverage

1. Navigate to **Policy → Compliance**.
2. Filter to the cost-tag policy assignments.
3. Confirm 100 % compliance after the second weekly cycle.
4. Any sustained non-compliance is an examiner-visible defect — track to closure in the operating cadence (§9).

---

## §5 Azure Cost Management — Cost Views and Scheduled Exports

**Portal:** Azure portal → **Cost Management + Billing** → **Cost Management**.

### 5.1 Build cost views

1. Open **Cost analysis**.
2. Set the scope to the management group (or subscription) that contains AI workloads.
3. Group by **Tag: `CostCenter`** — verify the chart shows your BU codes.
4. Save the view as **`AI-Agents-By-CostCenter`**.
5. Repeat with grouping by **`BusinessUnit`**, **`Service name`**, and **`Resource group`**; save each.

### 5.2 Configure scheduled exports (the WORM evidence path)

1. Open **Exports → + Add export**.
2. Configure:
   - **Export type:** `Daily export of month-to-date costs` (recommended) or `Custom date range`
   - **Dataset:** `Amortized cost` (preferred for chargeback because reservations are spread across the period)
   - **Storage account:** the firm's records-retention storage account (must have **immutability policy** enabled — see §8)
   - **Container/path:** `cost-mgmt-exports/{ManagementGroup}/{YYYY}/{MM}`
   - **File format:** Parquet (smaller, columnar — easier to query in Power BI)
   - **Schedule:** Daily
3. Click **Create**.
4. Validate within 24 hours that the first export landed in storage.

!!! danger "Storage must be immutable for the export to count as a record"
    A scheduled export to an unprotected blob is an operational dataset — not a SEC 17a-4(b)(4) record. Apply a time-based **immutability policy** (Azure Storage immutable blob storage) sized to the firm's records-retention period (commonly 6 years). Lock the policy after the soft-test period to prevent accidental shortening.

### 5.3 Validate exports against invoice

Once per month after the invoice cuts:

1. Sum the daily exports for the month for the management-group scope.
2. Compare to the Microsoft Customer Agreement / EA invoice for the same period.
3. Variance >5 % is an anomaly — open an investigation; document the variance memo (Verification §1).

---

## §6 Azure Cost Management — Budget Alerts (Notification-Only)

### 6.1 Create a budget per BU

1. Navigate to **Cost Management → Budgets → + Add**.
2. Configure:
   - **Scope:** the BU's resource group(s) or subscription
   - **Filter:** `Tag: CostCenter = CC-####` (preferred) or `Resource group ∈ ...`
   - **Period:** Monthly
   - **Amount:** the BU-approved monthly budget (from the §0 prerequisites)
   - **Expiration date:** the firm's fiscal year-end
3. **Alert thresholds** (cumulative actual cost):

   | Threshold | Recipients | Action |
   |-----------|------------|--------|
   | 50 % | BU owner | Informational |
   | 75 % | BU owner + Finance | Investigate trajectory |
   | 90 % | BU owner + Finance + AI Governance Lead | Variance memo opens |
   | 100 % | All above + Compliance Officer | Pre-defined enforcement action triggers (e.g., suspend non-essential agents, freeze new deployments) |

4. Click **Create**.

!!! warning "Alerts are notify-only"
    Crossing 100 % does not stop spend. The firm's enforcement mechanism — typically a Power Automate flow that disables non-essential billing policies, or an SOC playbook that suspends the lowest-priority agents — must be designed, tested, and exercised separately. Document the enforcement-mechanism owner in the budget's description field.

### 6.2 Forecast budgets

Set a second budget per BU with **`Forecast`** (instead of `Actual`) thresholds at 90 / 100 %. Forecast budgets fire earlier and give the BU owner room to react before the month closes.

---

## §7 Power BI — Cost Dashboard from the Cost Management Connector

**Portal:** [`https://app.powerbi.com`](https://app.powerbi.com)

1. Create a new workspace `FSI-AI-Cost-Governance`.
2. From Power BI Desktop, **Get Data → Azure → Azure Cost Management**.
3. Provide the billing account or management-group scope; authenticate.
4. Build pages:

   | Page | Visuals | Filters |
   |------|---------|---------|
   | **Executive** | YTD cost, MoM change, top-5 BUs, top-5 agents | None |
   | **Per-BU** | 13-month trend, budget vs actual, forecast | `BusinessUnit` |
   | **Per-agent** | Cost per agent (joined with Control 3.1 inventory), cost per interaction | `Application` |
   | **License utilization** | Assigned vs active Copilot seats, idle >30 days | `BusinessUnit` |
   | **Variance** | Variance by BU, threshold breaches, open variance memos | `Period` |

5. Configure row-level security so BU owners see only their BU; Finance and AI Governance Lead see all.
6. Schedule daily refresh.

---

## §8 Microsoft Purview — Retention Policy for Chargeback Artifacts

**Portal:** [`https://purview.microsoft.com`](https://purview.microsoft.com)

Chargeback ledgers, rate cards, variance memos, and the underlying Cost Management exports are **financial books and records** under SEC Rule 17a-4(b)(4) and FINRA Rule 4511.

1. Navigate to **Solutions → Data Lifecycle Management → Retention policies**.
2. Create or extend a retention policy `FSI-Records-FinancialBooks`:
   - **Retention period:** 6 years (verify against the firm's records-retention schedule; certain jurisdictions require longer)
   - **Action at end of period:** Retain and review (do not auto-delete financial records)
   - **Locations:** SharePoint sites where the chargeback workbooks are stored, plus OneDrive (rate cards, variance memos)
3. For Azure-side artifacts (Cost Management exports), configure **Storage account immutability policy** at the container level (see §5.2). Purview retention does not natively cover Azure Storage; this is a parallel control surface.
4. For SharePoint-stored chargeback artifacts, apply the retention label `FSI-Records-FinancialBooks` automatically by site or via auto-apply rules.
5. Document the retention-policy assignments in the records-management register.

---

## §9 Operating Cadence

### 9.1 Daily (automated)

- Cost Management exports run.
- Power BI refreshes.
- Tag-policy compliance summary checked (any new resource without required tags surfaces here).

### 9.2 Monthly close (humans + automation)

By the 5th business day after month-end:

1. Run [`Get-Fsi35MonthlyChargeback`](powershell-setup.md#4-monthly-close-helpers) (PowerShell setup §4).
2. Reconcile total against the EA / MCA invoice — variance memo for any >5 % delta.
3. Generate the BU-level chargeback ledger; route to Finance for sign-off.
4. Apply the retention label to the signed PDF; archive to the SharePoint records library.
5. Distribute the Power BI Executive page link to the AI Governance Committee.

### 9.3 Quarterly

- Pull a one-record evidence sample (one billing policy, one budget, one chargeback ledger, one variance memo). Walk through the SOX 404 ITGC test script. Sign and retain. (Verification §3.)
- Review Copilot license utilization; reclaim seats idle >30 days.
### 9.4 Annual

- Re-baseline the rate card with Finance.
- Re-attest BU-owner assignments against Entra ID security groups.
- Renew the records-retention policy review.

---

## §10 Decision Matrix — Portal vs PowerShell vs Graph

| Operation | Portal | PowerShell | Graph / REST |
|-----------|--------|------------|---------------|
| Create Copilot billing policy | ✓ (one-time setup) | Limited (no GA cmdlet for billing-policy CRUD as of April 2026) | ✓ via M365 admin Graph beta — verify per release |
| Read Copilot consumption | ✓ | ✓ via Microsoft Graph reports | ✓ |
| Create Azure budget | ✓ | ✓ `New-AzConsumptionBudget` (Az.Billing) | ✓ ARM REST |
| Schedule cost export | ✓ | ✓ `New-AzCostManagementExport` (Az.CostManagement) | ✓ |
| Query costs | ✓ | ✓ `Invoke-AzCostManagementQuery` (Az.CostManagement) | ✓ |
| Apply tag policy | ✓ | ✓ `New-AzPolicyAssignment` | ✓ |
| Apply Purview retention | ✓ | Limited via PnP.PowerShell for SharePoint label binding | ✓ Microsoft Graph compliance APIs |

For automation patterns, see [`powershell-setup.md`](powershell-setup.md).

---

## Final Readiness Checklist

- [ ] Cost-allocation taxonomy documented and signed by Finance
- [ ] Environment naming convention applied; non-conforming environments tracked
- [ ] Mandatory Azure tag set enforced via `Deny` policy with inheritance
- [ ] M365 Copilot billing policies created per BU with documented immutable scope
- [ ] Azure Cost Management views built and exports scheduled to immutable storage
- [ ] Budget alerts created for every BU at 50 / 75 / 90 / 100 %
- [ ] Power BI cost dashboard published with row-level security
- [ ] Purview retention policy `FSI-Records-FinancialBooks` covers chargeback artifacts
- [ ] Monthly close cadence documented and assigned to a named owner
- [ ] Quarterly SOX 404 evidence-sample procedure scheduled

---

[Back to Control 3.5](../../../controls/pillar-3-reporting/3.5-cost-allocation-and-budget-tracking.md) · [PowerShell Setup](powershell-setup.md) · [Verification & Testing](verification-testing.md) · [Troubleshooting](troubleshooting.md)

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
