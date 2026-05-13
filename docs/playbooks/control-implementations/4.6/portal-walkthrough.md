# Control 4.6 — Portal Walkthrough: Grounding Scope Governance

**Control:** [4.6 Grounding Scope Governance](../../../controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md)
**Audience:** SharePoint Admin, Power Platform Admin, Purview Compliance Admin, Entra Global Admin
**Surfaces:** SharePoint Admin Center (SPAC) · Power Platform Admin Center (PPAC) · Copilot Studio (validation only)
**Estimated time:** 90–120 minutes for the full walkthrough across both portals (excluding tenant-wide rollouts)
**Last UI verified:** April 2026

!!! danger "Do not run this walkthrough directly in production without a change record"
    Restricted Content Discovery (RCD), Restricted SharePoint Search (RSS), and Power Platform DLP all alter what users and Copilot agents can see at runtime. A misconfigured RCD toggle can silently break in‑app Microsoft 365 Copilot answers for the affected site, and an over‑broad DLP policy can block every Copilot Studio agent from grounding on SharePoint or OneDrive. Stage every change in a non‑production environment, capture screenshots and Unified Audit Log (UAL) evidence, and obtain change approval before promoting to your Zone 2 / Zone 3 production tenant.

!!! warning "This control supports — it does not guarantee — compliance"
    The portal steps below help support FINRA Rule 4511, SEC Rule 17a‑4, SOX 302/404, GLBA Safeguards Rule, NY DFS 23 NYCRR 500, and FINRA Regulatory Notice 25‑07 record‑keeping and oversight obligations. They do not by themselves satisfy any single rule. Your firm's compliance, legal, and risk teams remain accountable for full obligation coverage.

---

## What this walkthrough covers

| Surface | What you will configure | Why it matters for Control 4.6 |
| --- | --- | --- |
| **SPAC → Reports → Data access governance (DAG)** | Generate and review Site permissions, Sharing links activity, and EEEU activity reports to nominate sites for RCD/RSS scoping. | Identifies the high‑risk sites that grounding scope governance must protect first. |
| **SPAC → Active sites → site → Settings → Restrict content from Microsoft 365 Copilot** | Apply per‑site Restricted Content Discovery (RCD) to remove the site from organization‑wide Copilot grounding while preserving direct user access. | Primary technical control for surgical scope reduction in Zone 2 / Zone 3. |
| **SPAC → Settings → Restricted SharePoint Search** | Enable tenant‑wide Restricted SharePoint Search (RSS) and curate the allowed‑list of up to 100 sites. | Short‑term remediation while RCD is rolled out at scale. Not a security boundary. |
| **PPAC → Policies → Data policies** | Create or update a Power Platform DLP policy that classifies the Copilot Studio SharePoint / OneDrive knowledge connectors and applies endpoint filtering. | Governs which SharePoint and OneDrive surfaces custom Copilot Studio agents may ground on. |
| **Copilot Studio (validation only)** | Re‑publish a test agent and verify the SharePoint knowledge picker reflects DLP and RCD scope. | Confirms end‑to‑end handshake from SPAC → PPAC → agent runtime. |

What this walkthrough does **not** cover (use the linked playbooks instead):

- Bulk PowerShell automation for RCD across thousands of sites → see [`powershell-setup.md`](powershell-setup.md).
- Repeatable verification queries (KQL / SPO / Graph) you run after each change → see [`verification-testing.md`](verification-testing.md).
- Common failure modes and recovery (e.g., rolling back an RCD toggle, restoring an RSS allowed‑list site) → see [`troubleshooting.md`](troubleshooting.md).

---

## §0 Coverage boundary, surface inventory, and portal vs PowerShell matrix

### 0.1 Coverage boundary (what is in scope for "grounding scope governance")

In scope for Control 4.6 — and for this walkthrough:

- **SharePoint sites and their associated Microsoft 365 Group / Teams content** that any Copilot surface (Microsoft 365 Copilot, Copilot Studio agents, Copilot in Teams, Copilot in Outlook) may ground on through the SharePoint search index.
- **OneDrive for Business document libraries** that are surfaced to Copilot Studio agents through the SharePoint / OneDrive knowledge connectors. (Note: OneDrive sites cannot have RCD applied; they are governed exclusively through DLP, sensitivity labels, and conditional access.)
- **Custom Copilot Studio agents** (formerly Power Virtual Agents / "copilots") that bind to SharePoint or OneDrive as a knowledge source.
- **Search‑driven grounding paths** that flow through Microsoft Graph / SharePoint Search APIs into any Copilot reasoning loop.

Out of scope for Control 4.6 (covered by sibling controls — see §9):

- Sensitivity label policy authoring → Control 1.5.
- DSPM for AI inventory and posture → Control 1.6.
- Comprehensive Unified Audit Logging baseline → Control 1.7.
- Insider risk signals from Copilot prompts → Control 1.12.
- Item‑level permission scanning for over‑shared documents inside an in‑scope site → Control 4.8.
- SharePoint Information Access Governance (IAG) restricted content discovery posture review → Control 4.1.

### 0.2 Surface inventory (where each setting actually lives in April 2026)

| # | Setting | Portal path (April 2026 UI) | Sovereign clouds where path applies |
| --- | --- | --- | --- |
| S1 | DAG reports — Site permissions | `SPAC → Reports → Data access governance → Site permissions` | Commercial, GCC, GCC High, DoD |
| S2 | DAG reports — Sharing links activity | `SPAC → Reports → Data access governance → Sharing links activity` | Commercial, GCC, GCC High, DoD |
| S3 | DAG reports — EEEU activity ("Everyone except external users") | `SPAC → Reports → Data access governance → EEEU activity` | Commercial, GCC, GCC High, DoD |
| S4 | Per‑site RCD | `SPAC → Sites → Active sites → [select site] → Settings tab → Restrict content from Microsoft 365 Copilot → On → Save` | Commercial, GCC, GCC High, DoD |
| S5 | RCD delegation flag | PowerShell only — `Set-SPOTenant -DelegateRestrictedContentDiscoverabilityManagement $true` | Commercial, GCC, GCC High, DoD |
| S6 | Restricted SharePoint Search (tenant toggle + allowed‑list) | `SPAC → Settings → Restricted SharePoint Search` (tenant toggle + allowed list management); PowerShell mirror `Set-SPOTenantRestrictedSearchMode -Mode Enabled` | Commercial, GCC, GCC High, DoD |
| S7 | Power Platform DLP for Copilot Studio knowledge connectors | `PPAC → Policies → Data policies → + New policy` (then classify the Copilot Studio knowledge connectors and apply endpoint filtering) | Commercial, GCC, GCC High, DoD |
| S8 | Copilot Studio knowledge picker validation | `Copilot Studio → [agent] → Knowledge → + Add knowledge → SharePoint / OneDrive` | Commercial, GCC, GCC High, DoD |

### 0.3 Portal vs PowerShell — when to use which

| Operation | Portal path (this walkthrough) | PowerShell mirror | Recommended primary surface |
| --- | --- | --- | --- |
| Apply RCD to one site | SPAC → Active sites → site → Settings | `Set-SPOSite -Identity <url> -RestrictContentOrgWideSearch $true` | Portal for first 25 sites and any change‑managed production change. |
| Apply RCD to many sites (≥25) | Not feasible from the portal at scale | `Get-SPOSite | Where-Object {…} | Set-SPOSite -RestrictContentOrgWideSearch $true` | PowerShell — see [`powershell-setup.md`](powershell-setup.md). |
| Read back RCD status | SPAC site Home tab shows "Restricted" marker | `Get-SPOSite -Identity <url> | Select-Object Url, RestrictContentOrgWideSearch` | PowerShell for evidence capture; portal for spot checks. |
| Delegate RCD management to non‑SharePoint Admins | Not available in portal | `Set-SPOTenant -DelegateRestrictedContentDiscoverabilityManagement $true` | PowerShell only — log written justification to UAL. |
| Enable RSS tenant‑wide | SPAC → Settings → Restricted SharePoint Search (toggle) | `Set-SPOTenantRestrictedSearchMode -Mode Enabled` | Portal for one‑time enable; PowerShell for documented scripted change. |
| Manage RSS allowed list (≤100 sites) | SPAC → Settings → Restricted SharePoint Search (allowed‑list pane) | `Add-SPOTenantRestrictedSearchAllowedListSites` (verify exact cmdlet against `Get-Command -Module Microsoft.Online.SharePoint.PowerShell -Name *RestrictedSearch*`) | Either — pick one and document it as the system of record. |
| Generate DAG report | SPAC → Reports → Data access governance | Not available via PowerShell | Portal only. |
| Create/edit Power Platform DLP policy | PPAC → Policies → Data policies | `New-DlpPolicy` / `Set-DlpPolicy` (Power Apps cmdlets) | Portal for first authoring; PowerShell for promotion across environments. |

!!! note "Why both surfaces are required"
    The portal gives you change‑managed UI evidence (screenshots) that auditors expect for SOX 302/404 control walkthroughs. PowerShell gives you the deterministic, reproducible read‑backs that satisfy SEC 17a‑4 / FINRA 4511 evidence preservation and let you scale beyond what the SPAC UI can handle. Use both — never one alone.


---

## §1 Sovereign cloud applicability matrix

Use this matrix at the top of every change record so reviewers can see at a glance whether the steps in §4 apply to your tenant.

| Capability | Commercial | GCC | GCC High | DoD | Gallatin (China 21Vianet) |
| --- | --- | --- | --- | --- | --- |
| SPAC → Reports → Data access governance | ✅ Available | ✅ Available | ✅ Available | ✅ Available | ❌ Not available |
| Per‑site RCD (`RestrictContentOrgWideSearch`) | ✅ Available | ✅ Available | ✅ Available | ✅ Available | ❌ Not available |
| RCD delegation flag | ✅ Available | ✅ Available | ✅ Available | ✅ Available | ❌ Not available |
| Restricted SharePoint Search (RSS) | ✅ Available | ✅ Available | ✅ Available | ✅ Available | ❌ Not available |
| Power Platform DLP for Copilot Studio knowledge connectors | ✅ Available | ✅ Available (verify connector availability per environment) | ✅ Available (verify connector availability per environment) | ✅ Available (verify connector availability per environment) | ❌ Not available |
| Microsoft 365 Copilot grounding on SharePoint | ✅ Available | ✅ Available (license‑gated) | ✅ Available (license‑gated, region‑restricted) | ✅ Available (license‑gated, region‑restricted) | ❌ Not available |
| Copilot Studio agents grounding on SharePoint | ✅ Available | ✅ Available (validate connector parity) | ✅ Available (validate connector parity, **payload limit ≈ 450 KB vs 5 MB commercial**) | ✅ Available (validate connector parity, payload limit applies) | ❌ Not available |

### 1.1 Compensating controls when a capability is not available

If you operate in **Gallatin (China 21Vianet)** or any other tenant where the capabilities above are not available, do not skip Control 4.6 — apply the following compensating controls and record the deviation in your control register:

- **Compensate for missing RCD:** Use sensitivity labels (Control 1.5) with encryption + content marking on every container that must be hidden from broad search; combine with per‑site search visibility settings (`Set-SPOSite -NoCrawl $true` for canary sites only — never as a production strategy because it removes the site from the index entirely).
- **Compensate for missing RSS:** Reduce the surface area of `Everyone except external users` (EEEU) groups (Control 4.1), tighten default sharing settings, and apply per‑site sharing restrictions through SPAC.
- **Compensate for missing Copilot Studio DLP coverage:** Restrict the list of Copilot Studio environments where SharePoint / OneDrive connectors can be added (Power Platform environment strategy), and disable maker self‑service for the SharePoint connector entirely if the connector is unavailable.
- **Compensate for missing DAG reports:** Run scheduled Microsoft Graph queries against `/sites` and `/sites/{id}/permissions` and stage the output in a governed Microsoft Lists / Dataverse table that your SOC reviews on the same cadence DAG would have driven.

### 1.2 Per‑surface caveats you must record before acting

| Caveat | What it means in practice |
| --- | --- |
| **OneDrive sites cannot have RCD applied.** | Any "block this from Copilot grounding" requirement targeted at OneDrive must be implemented through DLP, sensitivity labels, or conditional access — never RCD. The portal will not surface the toggle for OneDrive sites; PowerShell will return an error. |
| **RSS is short‑term remediation only.** | RSS is not a security boundary. It limits which sites the org‑wide search index can return for grounding queries, but it does not change file‑level permissions, sharing links, or a determined user's ability to navigate directly. Use it to buy time while you roll out RCD per site. |
| **DAG reports lag.** | Reports refresh on a tenant‑managed cadence (typically every 24–72 hours). Do not assume a report run immediately after a permission change reflects the new state — capture both the pre‑change and post‑change report runs as evidence. |
| **DLP for Copilot Studio names connectors specifically.** | Verify the connector display names in your tenant before authoring DLP rules — Microsoft has renamed and split these connectors several times. As of April 2026 the canonical name set includes "Knowledge source with SharePoint and OneDrive in Copilot Studio" and sibling connectors for public websites and uploaded documents. |
| **GCC High / DoD payload limits.** | The Copilot Studio SharePoint / OneDrive knowledge connector enforces a smaller payload limit in GCC High (≈ 450 KB) than in commercial (≈ 5 MB). Test agents must use representative content sizes. |

---

## §2 Pre‑flight gates

Do not proceed past §2 until every gate below is signed off. Each gate maps to a concrete artifact you will produce; the artifact name appears in the Evidence Pack table in §6.

### 2.1 License and capability gate

| Gate | Required state | How to verify | Evidence artifact |
| --- | --- | --- | --- |
| Microsoft 365 Copilot or Standalone Agent Mode (SAM) license present | The tenant must have **either** at least one Microsoft 365 Copilot license assigned **or** at least one Standalone Agent Mode (SAM) license assigned. Tenants with neither cannot use Copilot Studio agents and Control 4.6 does not apply. | `Microsoft 365 admin center → Billing → Licenses` — confirm at least one assigned seat for either SKU. | E1 — License posture screenshot |
| SharePoint plan supports DAG and RCD | SharePoint Plan 1 or higher; Microsoft 365 E3/E5/G3/G5 family. | Same Licenses page; record SKU. | E1 (combined) |
| Power Platform environment exists for testing | At least one Power Platform environment that is **not** the default environment, designated as the canary environment. | `PPAC → Environments` — confirm a `cs-grounding-canary` (or equivalent) environment exists with an isolated Dataverse database. | E2 — Canary environment screenshot |

!!! warning "Common license misconception"
    SAM access is granted via **either** ≥ 1 Copilot license assigned in the tenant **or** a standalone SAM license. It is **not** "Copilot license only" and **not** "SAM license only" — either path qualifies. Document which path your tenant uses in the change record so license audits trace back to the correct SKU.

### 2.2 Role and role‑assignment gate

You will need the following Entra / workload roles assigned to the named operator(s) for the duration of this walkthrough. Use canonical names from the [Role Catalog](../../../reference/role-catalog.md).

| Role | Required for | Assigned to (named operator) | Time‑bound? |
| --- | --- | --- | --- |
| **SharePoint Admin** | Steps §4a, §4b, §4c | _name + UPN_ | Yes — PIM eligible, activate for the change window |
| **Power Platform Admin** | Step §4e (DLP) | _name + UPN_ | Yes — PIM eligible, activate for the change window |
| **Copilot Studio Admin** (or Power Platform Admin) | Step §4f (validation) | _name + UPN_ | Yes — PIM eligible |
| **Purview Compliance Admin** (read‑only audit search) | Evidence collection (§6) | _name + UPN_ | Standing read‑only |
| **Entra Global Admin** | Break‑glass only (do not use for routine steps) | _break‑glass account_ | Standing, monitored |

Record PIM activations in the change record and include the activation timestamps in evidence artifact E3.

### 2.3 Tenant readiness gate

| Gate | Required state | How to verify |
| --- | --- | --- |
| DAG reports enabled and at least one historical run exists | `SPAC → Reports → Data access governance` shows generated reports for at least the last 30 days. | Visual check; capture screenshot E4. |
| Unified Audit Log (UAL) ingestion confirmed | UAL has been on for ≥ 90 days (or since tenant creation if newer). | `Purview → Audit → Search` returns results for `RestrictContentDiscoverabilityEnabled` (or any common operation). |
| Sensitivity labels published | Required for OneDrive compensating control and for cross‑reference to Control 1.5. | `Purview → Information protection → Labels` shows ≥ 1 published label. |

### 2.4 Test fixtures gate (named identities, sites, agents)

Before any production change, the following test fixtures must exist in the canary environment. These names appear throughout §4 and §5.

**Test identities:**

| Identity | Purpose |
| --- | --- |
| `svc-grounding-rcd-pos@<tenant>` | "Positive" identity expected to retain access via direct permissions on a restricted site. |
| `svc-grounding-rcd-neg@<tenant>` | "Negative" identity expected to lose grounding visibility once RCD is enabled. |
| `svc-grounding-rss-allowed@<tenant>` | Identity used to validate RSS allowed‑list behavior. |
| `svc-grounding-rss-denied@<tenant>` | Identity used to validate RSS denied (default) behavior. |

**Test sites (canary tenant or canary site collection):**

| Site URL (suffix) | Purpose |
| --- | --- |
| `/sites/cs-rcd-positive` | Site that **will** have RCD enabled — direct‑access user keeps access; org‑wide search loses it. |
| `/sites/cs-rcd-negative` | Site that **stays** discoverable — control case for the RCD test. |
| `/sites/cs-rss-allowed` | Site listed on the RSS allowed‑list while RSS is on. |
| `/sites/cs-rss-denied` | Site **not** listed on the RSS allowed‑list while RSS is on. |
| `/sites/cs-recent-interaction` | Site used to validate the recent‑interaction carve‑out (see §5.2). |

**Test agents (Copilot Studio):**

| Agent | Bound knowledge source | Purpose |
| --- | --- | --- |
| `grounding-test-Z2-001` | `cs-rcd-positive`, `cs-rss-allowed` | Zone 2 representative agent — must reflect RCD/RSS scoping after each change. |
| `grounding-test-Z3-001` | `cs-rcd-positive`, `cs-rcd-negative`, `cs-rss-allowed`, `cs-rss-denied` | Zone 3 multi‑source representative agent. |
| `grounding-test-RCD-positive-001` | `cs-rcd-positive` only | Isolates RCD behavior. |
| `grounding-test-RCD-negative-001` | `cs-rcd-negative` only | Control for RCD test. |

### 2.5 Two‑portal precondition

Both SPAC and PPAC sessions must be open and authenticated **as the named operator role** (not as Global Admin) before you start §4. The SPAC change in §4b/§4c will create a precondition that the PPAC DLP change in §4e validates against. If you finish §4b/§4c and then discover your PPAC role is missing, you must roll back §4b/§4c before re‑attempting — do not leave the tenant in a half‑configured state.

### 2.6 Separation of duties

The operator who **applies** an RCD or RSS change must not be the same operator who **approves** the change record, and must not be the same operator who **collects** the post‑change evidence (§6). At minimum:

- Approver: Compliance officer or Risk lead (named in change record).
- Operator (applies change): Named SharePoint Admin / Power Platform Admin.
- Evidence collector: Purview Compliance Admin (read‑only).

Document the three named individuals and their email approvals in the change record before proceeding.

---

## §3 Roles per step matrix

This matrix tells the change reviewer exactly who must perform each step in §4. All role names are canonical names from the [Role Catalog](../../../reference/role-catalog.md). Do not substitute longer Entra display names (e.g., "Global Administrator" → use "Entra Global Admin").

| Step | Operator role | Reviewer role | Evidence collector | Approval required before action? |
| --- | --- | --- | --- | --- |
| §4a — Generate DAG reports | SharePoint Admin | n/a (read‑only) | SharePoint Admin | No |
| §4a — Nominate sites for RCD/RSS | SharePoint Admin + Compliance Officer | Risk lead | Purview Compliance Admin | Yes — written nomination list |
| §4b — Toggle per‑site RCD on canary site | SharePoint Admin | n/a (canary) | SharePoint Admin | No (canary) / Yes (production) |
| §4b — Toggle per‑site RCD on production site | SharePoint Admin | Compliance Officer | Purview Compliance Admin | **Yes — change record approved** |
| §4b — Set RCD delegation flag | SharePoint Admin | Compliance Officer + Risk lead | Purview Compliance Admin | **Yes — written justification logged to UAL** |
| §4c — Enable RSS tenant‑wide | SharePoint Admin | Compliance Officer | Purview Compliance Admin | **Yes** |
| §4c — Manage RSS allowed list | SharePoint Admin (delegate allowed for additions only) | Compliance Officer (sample audit) | Purview Compliance Admin | Yes for first 10 additions; sample audit thereafter |
| §4d — DAG report follow‑up | SharePoint Admin | n/a | SharePoint Admin | No |
| §4e — Create / edit Power Platform DLP for Copilot Studio | Power Platform Admin | Compliance Officer | Power Platform Admin | **Yes** |
| §4f — Validate in Copilot Studio | Copilot Studio Admin | n/a (validation) | Copilot Studio Admin | No |

!!! warning "Do not perform any §4 step as Entra Global Admin"
    Global Admin must remain a break‑glass role. Use SharePoint Admin and Power Platform Admin (PIM‑activated for the change window) as your primary operator roles. If you find yourself reaching for Global Admin to perform a routine step, that is a signal to add the operator‑specific role to the named operator instead.

---

## §4a — SPAC: Data access governance reports (the site nomination feeder)

**Purpose:** Identify the high‑risk sites that should be the first candidates for per‑site RCD or RSS allowed‑list inclusion. The DAG reports are how you make grounding scope decisions defensible — without them, every RCD toggle is an opinion, not a control.

**Operator:** SharePoint Admin
**Estimated time:** 20–30 minutes (excluding report generation lag)
**Outcome:** A signed nomination list of sites for RCD and RSS treatment.

### 4a.1 Generate the three DAG reports

1. Sign in to **SharePoint Admin Center** (`https://<tenant>-admin.sharepoint.com`) as the named SharePoint Admin (PIM‑activated).
2. In the left navigation, expand **Reports**.
3. Select **Data access governance**.
4. You will see three report categories. Generate each one in turn:
   - **Site permissions** — choose **Run report** for the report types you need (e.g., "Sites shared with Everyone except external users", "Sites shared externally", "Sites with sensitivity label X"). Repeat for each variant your nomination list requires.
   - **Sharing links activity** — generate the latest run.
   - **EEEU activity** — generate the latest run.
5. Wait for each report's status to move from **In progress** to **Completed**. Reports refresh on a tenant‑managed cadence — capture the timestamp shown for each report and record it in evidence artifact E4.

### 4a.2 Capture report screenshots (E4)

For each report:

1. Click into the report to open the detail pane.
2. Capture a full‑window screenshot showing: report title, date range, total site count, and the first page of results.
3. Export to CSV (where available) and store the CSV alongside the screenshot in the evidence pack.

### 4a.3 Nominate sites for RCD or RSS treatment

Build the nomination list by joining the three reports. A site qualifies for **immediate per‑site RCD** if it meets any of the following:

- Contains content tagged with a confidentiality sensitivity label (e.g., `Confidential`, `Highly Confidential`) **and** appears on the EEEU activity report.
- Is shared with `Everyone except external users` (EEEU) **and** has had ≥ 1 anonymous link or "anyone" link created in the last 90 days.
- Has been flagged by Insider Risk (Control 1.12) for unusual download or copy activity in the last 30 days.
- Hosts content covered by a regulated record class (e.g., FINRA 4511 books and records, SEC 17a‑4 retained communications).

A site qualifies for **RSS allowed‑list inclusion** (rather than RCD) when:

- The site **must remain** discoverable to Microsoft 365 Copilot grounding for an authorized population (e.g., a curated knowledge hub).
- The site does **not** carry confidential or regulated content beyond what the authorized population may already access.
- The total number of allowed‑list sites will remain ≤ 100 (the tenant cap).

Document the nomination list (site URL, classification rationale, target action, target completion date) and obtain Compliance Officer + Risk lead approval before proceeding to §4b.

### 4a.4 Common pitfalls in §4a

- **Stale report data.** DAG reports lag actual permission state by 24–72 hours. Re‑run the report after any permission change and before any production RCD toggle.
- **Missing sensitivity context.** A DAG report alone does not tell you what content is on the site. Cross‑reference with sensitivity label coverage (Control 1.5) and DSPM for AI inventory (Control 1.6).
- **Not capturing the pre‑change baseline.** Always run and screenshot the DAG report **before** §4b and again **after** §4b. The two snapshots together are your evidence the control changed state.

---

## §4b — SPAC: Per‑site Restricted Content Discovery (RCD)

**Purpose:** Apply Restricted Content Discovery to a specific SharePoint site so that the site's content is removed from organization‑wide Microsoft 365 Copilot grounding while users with direct permissions retain in‑site access.

**Operator:** SharePoint Admin
**Estimated time:** 5 minutes per site (UI); plus DAG re‑run lag for verification.
**Outcome:** The target site shows the **Restricted** marker on its Home tab; `Get-SPOSite … | Select RestrictContentOrgWideSearch` returns `True`; UAL records `RestrictContentDiscoverabilityEnabled`.

### 4b.1 Apply RCD to the canary site (`/sites/cs-rcd-positive`)

1. In SPAC, navigate to **Sites → Active sites**.
2. In the search box, type `cs-rcd-positive` and press Enter.
3. Click the site row (do **not** click the URL — clicking the URL navigates away from SPAC).
4. The site detail panel opens on the right. Select the **Settings** tab.
5. Scroll to **Restrict content from Microsoft 365 Copilot**.
6. Toggle **On**.
7. Read the confirmation dialog carefully. The dialog explains that:
   - Users with direct site permissions will continue to see content in the site itself and in direct in‑app Copilot calls when they are actively in the site context.
   - Tenant‑wide Copilot grounding will no longer return content from this site.
   - Microsoft Search continues to honor user permissions for direct queries.
8. Click **Save**.
9. Capture the confirmation screenshot for evidence artifact E5.

### 4b.2 Verify the RCD marker

1. Open the site (`https://<tenant>.sharepoint.com/sites/cs-rcd-positive`) in a separate tab as the SharePoint Admin.
2. The site Home tab now displays a **Restricted** marker / banner. Capture this for evidence artifact E6.
3. Switch to PowerShell (signed in as SharePoint Admin) and run:

```powershell
Get-SPOSite -Identity "https://<tenant>.sharepoint.com/sites/cs-rcd-positive" |
    Select-Object Url, RestrictContentOrgWideSearch
```

4. The output must show `RestrictContentOrgWideSearch : True`. Capture the console output for evidence artifact E7.

### 4b.3 Confirm the Unified Audit Log entry

1. Sign in to **Purview** (`https://purview.microsoft.com`) as Purview Compliance Admin.
2. Navigate to **Audit → Search**.
3. Set the date range to cover the change window.
4. In **Activities — friendly names**, type and add: `RestrictContentDiscoverabilityEnabled` (you may also see `RestrictContentDiscoverabilityDisabled` and `RestrictContentDiscoverabilityUpdated`).
5. Set **Users** to the SharePoint Admin who performed §4b.1.
6. Run the search.
7. Confirm the audit row appears within 60 minutes (UAL ingestion is near real‑time but not synchronous). Capture the row detail JSON for evidence artifact E8.

### 4b.4 OneDrive caveat (must record in change record)

RCD **cannot** be applied to OneDrive sites. If the toggle is missing on a site you expected to restrict, verify the site is not a OneDrive site:

```powershell
Get-SPOSite -IncludePersonalSite $true -Identity "<url>" | Select-Object Url, Template
```

If `Template` returns `SPSPERS` (or a `RedirectSite#0` fronting a personal site), you cannot apply RCD. Use these compensating controls instead:

- Apply a sensitivity label with encryption to the documents (Control 1.5).
- Restrict OneDrive sharing tenant‑wide (`SPAC → Sharing`).
- Use Power Platform DLP (§4e) to block the OneDrive connector for Copilot Studio agents in the affected environments.
- Ensure DSPM for AI (Control 1.6) inventories OneDrive grounding usage.

### 4b.5 Delegating RCD management (optional, regulated by §3)

If your operating model requires non‑SharePoint Admins to toggle RCD on a delegated set of sites (e.g., a site owner of a Confidential site), enable the delegation flag:

```powershell
Set-SPOTenant -DelegateRestrictedContentDiscoverabilityManagement $true
```

Read‑back:

```powershell
Get-SPOTenant | Select-Object DelegateRestrictedContentDiscoverabilityManagement
```

Before running the delegation cmdlet:

1. Document the written justification (who is being delegated, which sites, why, for how long) in the change record.
2. Have the Compliance Officer + Risk lead sign the justification.
3. Capture the pre‑change `Get-SPOTenant` value for rollback.
4. Run the cmdlet.
5. Capture the post‑change `Get-SPOTenant` value for evidence artifact E9.
6. Search UAL for `SetSPOTenant` events scoped to the delegation property and capture the row.

### 4b.6 Rolling back an RCD toggle (in case of false‑fail)

A common false‑fail pattern: an end user reports "Copilot in the site stopped working" after RCD is enabled. Before rolling back, check:

- Is the user actually losing access to in‑app Copilot, or only to org‑wide Copilot answers? RCD is expected to remove the latter; the former is a different issue.
- Has the user lost direct site permission unrelated to RCD?
- Did the change window allow ≥ 60 minutes for indexing to settle?

If a true rollback is needed:

1. Repeat §4b.1 with the toggle set to **Off**.
2. Capture the off‑state screenshot for evidence (note "rollback").
3. Confirm `RestrictContentOrgWideSearch : False` via PowerShell.
4. Confirm UAL `RestrictContentDiscoverabilityDisabled` event.
5. Add a post‑mortem entry to the change record explaining the false‑fail.

---

## §4c — SPAC: Restricted SharePoint Search (RSS)

**Purpose:** Use Restricted SharePoint Search as a tenant‑wide short‑term remediation that limits org‑wide Copilot grounding to a curated allowed‑list of up to 100 sites, while RCD is being rolled out at scale per §4b. RSS is **not a security boundary** — it limits what the search index returns for grounding, not who can access the underlying content.

**Operator:** SharePoint Admin
**Estimated time:** 15–30 minutes for the initial enable + first 10 allowed‑list sites; ongoing curation as sites are nominated.
**Outcome:** RSS is enabled tenant‑wide; the allowed‑list contains only the curated Zone 2 / Zone 3 sites your nomination list approved; PowerShell read‑backs confirm the same state; UAL records the change.

### 4c.1 Decide RSS vs RCD vs both

| Situation | Recommended posture |
| --- | --- |
| You can scope per‑site RCD to all high‑risk sites within the change window | RCD only; do not enable RSS. |
| You have > 100 high‑risk sites and cannot complete RCD rollout in the change window | Enable RSS as a stop‑gap, then progressively apply RCD and remove sites from the RSS allowed list as they are restricted. |
| You operate a small set of curated knowledge hubs and want grounding to default to "deny" with explicit allow | RSS as the primary control; RCD only on the hubs that themselves contain confidential content. |

### 4c.2 Enable RSS tenant‑wide via the portal

1. In SPAC, go to **Settings**.
2. Locate **Restricted SharePoint Search** in the settings list. Click to open the page.
3. Read the on‑page guidance about the 100‑site cap, the carve‑outs (recently visited, directly shared, files the user owns, last 2,000 entities), and the ~ 1 hour propagation time.
4. Toggle **Enable Restricted SharePoint Search** to **On**.
5. Save the change.
6. Capture the screenshot for evidence artifact E10.

### 4c.3 Mirror via PowerShell (canonical surface for evidence)

The portal toggle and the PowerShell cmdlet write the same state. PowerShell is the canonical surface for evidence because the read‑back is deterministic.

```powershell
# Enable RSS tenant‑wide
Set-SPOTenantRestrictedSearchMode -Mode Enabled

# Read back
Get-SPOTenantRestrictedSearchMode
```

Capture the read‑back output for evidence artifact E11.

To disable (rollback):

```powershell
Set-SPOTenantRestrictedSearchMode -Mode Disabled
```

!!! note "Verify the exact cmdlet name in your installed module"
    The Microsoft.Online.SharePoint.PowerShell module has shipped multiple cmdlet variants for RSS over its lifecycle (e.g., older `Set-SPOTenant -EnableRestrictedSearchAllList` style names that are now deprecated or renamed). Run the following to confirm the canonical cmdlet set in your installed version before scripting:

    ```powershell
    Get-Command -Module Microsoft.Online.SharePoint.PowerShell -Name *RestrictedSearch*
    ```

    Use the cmdlets returned by that query as the system of record for your runbooks.

### 4c.4 Manage the RSS allowed list

In the SPAC `Restricted SharePoint Search` page, the lower pane lists the allowed sites.

1. Click **+ Add sites**.
2. Search for the site by URL or name. Select it.
3. Repeat for each site approved on the §4a nomination list (up to 100).
4. Save.
5. Capture the populated allowed list for evidence artifact E12.

PowerShell mirror (verify the exact cmdlet name as above):

```powershell
# Add a site to the allowed list
Add-SPOTenantRestrictedSearchAllowedListSites -SitesList "https://<tenant>.sharepoint.com/sites/cs-rss-allowed"

# Read back
Get-SPOTenantRestrictedSearchAllowedListSites
```

!!! warning "100‑site cap and hub associations"
    The RSS allowed list is capped at 100 sites tenant‑wide. **Hub‑associated sites do not count individually** — adding the hub site brings its associated sites along for grounding purposes. Use this to your advantage when curating the list, but document the hub membership snapshot in the change record because it can drift over time.

### 4c.5 Verify RSS carve‑outs are intact

RSS preserves several carve‑outs that prevent it from breaking everyday Copilot interactions:

- **Recently visited sites** — sites a user has interacted with recently remain in their personal grounding set.
- **Directly shared content** — files explicitly shared with the user remain available.
- **Files the user owns** — owner content is always available.
- **Last 2,000 entities** — the user's most recent 2,000 SharePoint entities remain reachable.

Run the §5.2 recent‑interaction carve‑out test before claiming the rollout is successful.

### 4c.6 RSS effective time and audit

- RSS changes propagate in **approximately 1 hour**. Do not test sooner; record the wait period in the change log.
- UAL records `SPORestrictedSearchMode` (or equivalent — verify via Audit search) and allowed‑list mutation events. Capture for evidence artifact E13.

---

## §4d — DAG report follow‑up

After §4b and §4c, re‑run the DAG reports from §4a to capture the post‑change state.

1. Repeat §4a.1 to regenerate **Site permissions**, **Sharing links activity**, and **EEEU activity**.
2. Wait for the report status to move to **Completed**.
3. Capture screenshots and CSV exports as evidence artifact E14 (post‑change DAG snapshot).
4. Diff E4 (pre‑change) against E14 (post‑change) — every site that was nominated in §4a should now show:
   - Reduced grounding surface (visible in the report metadata or via a follow‑up `Get-SPOSite | Select RestrictContentOrgWideSearch` query).
   - No unexpected new exposures.
5. Record the diff summary in the change record.

If a nominated site does **not** show the expected change, do not promote to the next zone — return to §4b/§4c, identify the gap, and re‑run.

---

## §4e — PPAC: Power Platform DLP for Copilot Studio knowledge connectors

**Purpose:** Govern which SharePoint and OneDrive surfaces custom Copilot Studio agents are permitted to ground on, by classifying the Copilot Studio knowledge connectors in a Power Platform DLP policy and applying endpoint filtering.

**Operator:** Power Platform Admin
**Estimated time:** 30–45 minutes for the first policy; 10–15 minutes for subsequent edits.
**Outcome:** A DLP policy named (suggested) `dlp-copilot-studio-grounding-zone-2` (and a Zone 3 sibling) classifies the Copilot Studio SharePoint / OneDrive knowledge connectors and applies endpoint filtering to the approved site list.

### 4e.1 Open PPAC and create the policy

1. Sign in to **Power Platform Admin Center** (`https://admin.powerplatform.microsoft.com`) as the named Power Platform Admin (PIM‑activated).
2. In the left navigation, expand **Policies → Data policies**.
3. Click **+ New policy**.
4. **Name:** `dlp-copilot-studio-grounding-zone-2` (or your equivalent naming convention).
5. **Environment scope:** Select the environment(s) that host the Zone 2 Copilot Studio agents. **Do not** apply to the default environment unless you have ratified that as your Zone 2 host. Click **Next**.

### 4e.2 Classify the Copilot Studio knowledge connectors

The Copilot Studio knowledge connectors must be classified into the **Business** data group (or equivalent) so they can be governed independently from generic SharePoint usage in Power Apps / Power Automate.

1. In the connector list, set the search filter to `Copilot Studio`.
2. Locate the canonical connector names. As of April 2026 these include:
   - **Knowledge source with SharePoint and OneDrive in Copilot Studio** — the primary connector for SharePoint / OneDrive grounding.
   - **Knowledge source with public websites in Copilot Studio** — sibling connector for public web grounding.
   - **Knowledge source with documents in Copilot Studio** — sibling connector for uploaded documents.
3. For each connector, select the row and click **Move to Business** (the right‑hand action).
4. Capture the connector classification screenshot for evidence artifact E15.

!!! warning "Connector naming evolves"
    Microsoft has renamed and split the Copilot Studio knowledge connectors several times across H2 2025 and H1 2026 releases. Verify the connector display names in your tenant before authoring the policy. If you do not see the expected connector, search for `Copilot` and `SharePoint` separately, and document the actual name(s) in the change record alongside this playbook.

### 4e.3 Apply endpoint filtering to the SharePoint / OneDrive knowledge connector

Endpoint filtering lets you allow only a specific list of SharePoint sites (or OneDrive accounts) for Copilot Studio grounding.

1. Still on the connector configuration page, select the **Knowledge source with SharePoint and OneDrive in Copilot Studio** connector row.
2. Click **Configure connector → Connector endpoints** (the menu varies slightly by PPAC release; if you do not see "Connector endpoints", choose **Configure** then look for an "Endpoints" tab).
3. Set the default rule to **Deny** (block any endpoint not explicitly allowed).
4. Add an **Allow** rule for each approved SharePoint site URL (e.g., `https://<tenant>.sharepoint.com/sites/cs-rss-allowed`). Pattern syntax follows the Power Platform endpoint filtering rules — wildcards may be supported for site collections; verify behavior in your canary environment before relying on a wildcard.
5. Save the endpoint configuration.

### 4e.4 Finish the policy

1. Click **Next**.
2. Review the policy scope summary.
3. Click **Create policy**.
4. Capture the final policy summary screenshot for evidence artifact E16.

### 4e.5 Sibling Zone 3 policy

For Zone 3 (Enterprise Managed) agents, repeat §4e.1–§4e.4 with these differences:

- **Name:** `dlp-copilot-studio-grounding-zone-3`.
- **Environment scope:** Zone 3 environment(s) only; never apply Zone 2 and Zone 3 policies to the same environment.
- **Endpoint allow list:** Restrict to the curated Zone 3 grounding sites only. Zone 3 is typically the **smallest** allowed list, not the largest.

### 4e.6 GCC / GCC High / DoD payload caveat

In GCC High and DoD, the SharePoint / OneDrive knowledge connector enforces a smaller payload limit (≈ 450 KB vs. the ≈ 5 MB commercial limit). Test agents in §4f must use representative content sizes — large PDFs that ground successfully in commercial may silently truncate or fail in GCC High. Record the payload limit in the change record so future maker requests are routed correctly.

---

## §4f — Copilot Studio: validate the SPAC ↔ PPAC handshake

**Purpose:** Confirm that the SPAC RCD/RSS state and the PPAC DLP state combine to produce the expected runtime grounding scope on a real Copilot Studio agent. This is the **handshake validation** — without it you have configured two surfaces independently and only hope they agree.

**Operator:** Copilot Studio Admin (or Power Platform Admin)
**Estimated time:** 15–20 minutes per validation pass.
**Outcome:** Each test agent (`grounding-test-Z2-001`, `grounding-test-Z3-001`) shows the expected grounding behavior; deviations are logged and remediated before promotion.

### 4f.1 Open the test agent

1. Sign in to **Copilot Studio** (`https://copilotstudio.microsoft.com`) as Copilot Studio Admin.
2. Switch to the canary environment.
3. Open `grounding-test-Z2-001`.

### 4f.2 Check the Knowledge picker

1. Navigate to **Knowledge** in the agent's left navigation.
2. Click **+ Add knowledge → SharePoint / OneDrive**.
3. The picker should now reflect the DLP endpoint allow list:
   - Allowed sites (e.g., `cs-rss-allowed`) appear as selectable.
   - Sites not on the allow list are either filtered out, greyed out, or produce a "blocked by data policy" message when entered manually.
4. Capture screenshots of the picker behavior — both an allowed selection and a denied attempt — and add to evidence artifact E16.

### 4f.3 Republish the agent and run the test prompts

1. Re‑publish the agent.
2. Open the test pane.
3. Run the named test prompts from §5 (RCD positive, RCD negative, RSS allowed, RSS denied, recent‑interaction carve‑out, DLP block, DLP endpoint filter).
4. For each prompt, capture the agent response and confirm against the expected outcome in §5.

### 4f.4 Promotion gate

Do not promote any agent (or the underlying SPAC/PPAC change) to a higher zone until:

- All §5 test scenarios pass.
- All evidence artifacts E1–E16 are captured and named per the §6 manifest.
- The SHA‑256 manifest in §6 is generated and signed by the evidence collector.
- The Compliance Officer has counter‑signed the change record.

---

## §5 Deterministic test scenarios

Each scenario below is a named, reproducible test that validates one specific aspect of the SPAC ↔ PPAC ↔ Copilot Studio handshake. Run all of them before promoting from canary → Zone 2 and again before promoting from Zone 2 → Zone 3.

### 5.1 RCD positive (the core "removes from org‑wide grounding" test)

**Goal:** Confirm that a site with RCD enabled is no longer returned by org‑wide Microsoft 365 Copilot grounding queries while remaining visible to a user with direct site permission.

**Setup:**

- Site: `/sites/cs-rcd-positive` (RCD = On).
- Identity A: `svc-grounding-rcd-pos@<tenant>` — a member of the site, holding direct permissions.
- Identity B: `svc-grounding-rcd-neg@<tenant>` — **not** a member of the site, but a Microsoft 365 Copilot licensed user.
- Test agent: `grounding-test-RCD-positive-001` bound to `cs-rcd-positive`.
- Canary file in the site: `RCD-positive-canary.docx` containing the unique phrase `"FSIGOV-RCD-POS-CANARY-2026"`.

**Steps:**

1. As Identity A, open Microsoft 365 Copilot in the browser and prompt: `Find any document containing FSIGOV-RCD-POS-CANARY-2026`.
2. Expected: Identity A (direct permission) sees the canary document referenced.
3. As Identity B, open Microsoft 365 Copilot and submit the same prompt.
4. Expected: Identity B does **not** see the canary document — RCD has removed it from the org‑wide grounding index for users without direct permission.
5. Open `grounding-test-RCD-positive-001` test pane and run: `Summarize FSIGOV-RCD-POS-CANARY-2026`.
6. Expected: Agent returns the summary (because the agent is configured with the site as a knowledge source and runs in the agent's identity context).

**Pass criteria:** All three expected outcomes occur. Capture screenshots / response transcripts for evidence artifact E16 (test transcripts).

### 5.2 Recent‑interaction carve‑out (false‑fail prevention)

**Goal:** Confirm that the RSS / RCD recent‑interaction carve‑out behaves as documented — a user who has recently interacted with a site retains personal grounding access to it.

**Setup:**

- Site: `/sites/cs-recent-interaction` (RSS enabled tenant‑wide; site **not** on the RSS allowed list).
- Identity: `svc-grounding-rss-denied@<tenant>` (a member of the site).
- Canary file: `recent-interaction-canary.docx` with phrase `"FSIGOV-RECENT-2026"`.

**Steps:**

1. As the identity, **explicitly** open and edit `recent-interaction-canary.docx` in the SharePoint site (this records a recent interaction).
2. Wait 5 minutes for the interaction to register in the user's recent activity index.
3. In Microsoft 365 Copilot, prompt: `Find FSIGOV-RECENT-2026`.
4. Expected: Copilot returns the document — the recent‑interaction carve‑out preserves access despite the site not being on the RSS allowed list.

**Pass criteria:** The document is returned. If it is not returned, do **not** assume RSS is misconfigured — verify the recent interaction was recorded and that ≥ 5 minutes elapsed.

!!! note "Why this scenario matters"
    Without this test, the most common false‑fail report is: "RSS broke Copilot for our team — they can't find their own files." In nearly every case, the team can find their own recent files; the report stems from a single user querying for a site they have not visited recently. Run §5.2 in production after every RSS rollout to head off false escalations.

### 5.3 RSS allowed‑list grounding

**Goal:** Confirm that a site on the RSS allowed list remains discoverable to org‑wide grounding for permitted users.

**Setup:**

- Site: `/sites/cs-rss-allowed` (on the RSS allowed list; RCD = Off).
- Identity: `svc-grounding-rss-allowed@<tenant>` (member).
- Canary file: `rss-allowed-canary.docx` with phrase `"FSIGOV-RSS-ALLOW-2026"`.

**Steps:**

1. As the identity, prompt M365 Copilot: `Find FSIGOV-RSS-ALLOW-2026`.
2. Expected: Document is returned via org‑wide grounding.
3. As `svc-grounding-rss-denied@<tenant>` (not a member), repeat. Expected: Document is **not** returned (allowed‑list controls indexing visibility, not file ACLs).

**Pass criteria:** Both outcomes occur.

### 5.4 RSS denied default

**Goal:** Confirm that a site **not** on the allowed list is not returned by org‑wide grounding (subject to the carve‑outs in §5.2).

**Setup:**

- Site: `/sites/cs-rss-denied` (RSS enabled; site **not** on allowed list).
- Identity: `svc-grounding-rss-denied@<tenant>` who has **not** recently interacted with the site.
- Canary file: `rss-denied-canary.docx` with phrase `"FSIGOV-RSS-DENY-2026"`.

**Steps:**

1. As the identity, prompt M365 Copilot: `Find FSIGOV-RSS-DENY-2026`.
2. Expected: Document is **not** returned.

**Pass criteria:** The document is not returned. If it is returned, verify the recent‑interaction carve‑out is not in play (run §5.2 reasoning in reverse) and verify the RSS state via `Get-SPOTenantRestrictedSearchMode`.

### 5.5 DLP block (negative path) for Copilot Studio knowledge picker

**Goal:** Confirm that a Copilot Studio agent in an environment subject to the DLP policy from §4e cannot bind to a SharePoint site that is **not** on the endpoint allow list.

**Setup:**

- Environment: Zone 2 environment with `dlp-copilot-studio-grounding-zone-2` applied.
- Test agent: `grounding-test-Z2-001`.
- Target site: a site **not** on the endpoint allow list (e.g., `cs-rss-denied`).

**Steps:**

1. Open `grounding-test-Z2-001` in Copilot Studio.
2. Knowledge → + Add knowledge → SharePoint / OneDrive.
3. Attempt to add the URL of `cs-rss-denied`.
4. Expected: The picker either filters the site out, greys it out, or returns a "blocked by data policy" message. The agent **cannot** bind to it.

**Pass criteria:** The bind attempt fails with a clear DLP message. Capture the error.

### 5.6 DLP endpoint filter (positive path)

**Goal:** Confirm that an allowed site can be bound and grounding works end‑to‑end through the DLP allow list.

**Setup:**

- Same environment / agent as §5.5.
- Target site: `cs-rss-allowed` (on the endpoint allow list).

**Steps:**

1. Knowledge → + Add knowledge → SharePoint / OneDrive → enter `cs-rss-allowed`.
2. Expected: The site binds successfully.
3. Re‑publish the agent.
4. Run a test prompt: `Summarize FSIGOV-RSS-ALLOW-2026`.
5. Expected: The agent returns a grounded answer referencing the canary content.

**Pass criteria:** Bind succeeds and grounded answer is returned.

### 5.7 OneDrive cannot‑RCD compensating control test (Gallatin compatible)

**Goal:** Confirm that the compensating control for OneDrive (sensitivity label + DLP endpoint deny) prevents grounding on a OneDrive document that should not be reachable.

**Setup:**

- OneDrive document `od-canary.docx` owned by a test user, labeled `Confidential` with encryption.
- DLP endpoint filter denies the OneDrive endpoint for the Zone 2 environment.

**Steps:**

1. As another user (not the document owner), attempt to query M365 Copilot: `Find od-canary`.
2. Expected: Document is not returned (sensitivity label blocks access; DLP blocks Copilot Studio binding).
3. As the owner, repeat. Expected: Owner can find their own document (label honors owner permissions).

**Pass criteria:** Outsider cannot find the document; owner can.

---

## §6 Evidence pack (E1–E16) and SHA‑256 manifest

The evidence pack is the artifact you hand to internal audit, external regulators, and the change‑review board. It is the difference between "we configured Control 4.6" (assertion) and "we configured Control 4.6 and here is the deterministic proof" (defensible evidence).

### 6.1 Evidence artifact table

| ID | Artifact | Source | Format | Captured by | Promotion gate |
| --- | --- | --- | --- | --- | --- |
| E1 | License posture | M365 admin center → Billing → Licenses | PNG | Power Platform Admin or Compliance Admin | Pre‑flight |
| E2 | Canary environment | PPAC → Environments | PNG | Power Platform Admin | Pre‑flight |
| E3 | PIM activation log | Entra → PIM → Activation history | CSV / PNG | Compliance Admin | Pre‑flight |
| E4 | DAG report (pre‑change) | SPAC → Reports → DAG | PNG + CSV | SharePoint Admin | Before §4b |
| E5 | RCD toggle confirmation | SPAC → Sites → site → Settings | PNG | SharePoint Admin | Per site, after §4b |
| E6 | Site Home "Restricted" marker | Site Home tab | PNG | SharePoint Admin | After §4b |
| E7 | `Get-SPOSite` read‑back | PowerShell console | TXT | SharePoint Admin | After §4b |
| E8 | UAL `RestrictContentDiscoverabilityEnabled` row | Purview → Audit | JSON | Purview Compliance Admin | After §4b |
| E9 | RCD delegation flag read‑back | PowerShell `Get-SPOTenant` | TXT | SharePoint Admin | If §4b.5 performed |
| E10 | RSS portal toggle | SPAC → Settings → Restricted SharePoint Search | PNG | SharePoint Admin | After §4c |
| E11 | `Get-SPOTenantRestrictedSearchMode` read‑back | PowerShell | TXT | SharePoint Admin | After §4c |
| E12 | RSS allowed‑list contents | SPAC RSS page + PowerShell read‑back | PNG + TXT | SharePoint Admin | After §4c |
| E13 | UAL RSS / allowed‑list mutation events | Purview → Audit | JSON | Purview Compliance Admin | After §4c |
| E14 | DAG report (post‑change) | SPAC → Reports → DAG | PNG + CSV | SharePoint Admin | After §4d |
| E15 | DLP connector classification | PPAC → Policies → Data policies → policy detail | PNG | Power Platform Admin | After §4e |
| E16 | DLP policy summary + Copilot Studio handshake transcripts (§4f, §5) | PPAC + Copilot Studio + audit | PNG + TXT | Power Platform Admin + Copilot Studio Admin | Final promotion |

### 6.2 Evidence file naming convention

Use the following deterministic naming pattern for every artifact so the SHA‑256 manifest is reproducible:

```
4.6_E<NN>_<short-name>_<YYYYMMDD>_<HHMM>_<operator-upn-suffix>.<ext>
```

Examples:

```
4.6_E04_dag-pre_20260415_0930_jdoe.png
4.6_E04_dag-pre_20260415_0930_jdoe.csv
4.6_E07_get-spo-site-canary_20260415_0945_jdoe.txt
4.6_E11_get-rss-mode_20260415_1015_jdoe.txt
4.6_E16_handshake-z2-transcripts_20260415_1100_kpark.txt
```

### 6.3 SHA‑256 manifest

After all artifacts are captured for a given change run, generate a SHA‑256 manifest and store it alongside the artifacts:

```powershell
Get-ChildItem -Path .\evidence\4.6\<run-id>\ -File |
    Get-FileHash -Algorithm SHA256 |
    Select-Object Hash, Path |
    Export-Csv -Path .\evidence\4.6\<run-id>\manifest-sha256.csv -NoTypeInformation
```

The Compliance Officer must counter‑sign the manifest (PGP, S/MIME, or your firm's evidence signing process) before the change is considered closed.

### 6.4 Promotion table per zone

| From → To | Required evidence set | Approver |
| --- | --- | --- |
| Canary → Zone 2 | E1, E2, E3, E4, E5–E8 (all canary sites), E10–E13, E14, E15, E16 (all §5 tests pass) | Compliance Officer |
| Zone 2 → Zone 3 | All Zone 2 evidence + E5–E8 for each Zone 3 site, E16 for `grounding-test-Z3-001` | Compliance Officer + Risk lead |
| Steady state — quarterly review | Re‑run E4/E14 diff, refresh E11/E12, refresh E15, sample 10% of E5–E8 | Compliance Officer |

---

## §7 Anti‑patterns (do not do these)

The following anti‑patterns have caused real production incidents in FSI tenants. Treat each as a "do not do this" rule and a "if you see this, escalate" tripwire.

1. **Treating RSS as a security boundary.** RSS limits what the org‑wide search index returns for grounding queries. It does not change file ACLs, sharing links, or direct URL access. A user with the URL and permission can still open the file. Use RCD plus sensitivity labels for security; use RSS only for short‑term grounding scope reduction.

2. **Rolling back RCD because in‑app Copilot "stopped working".** RCD is **expected** to remove a site from org‑wide grounding. Users may report "Copilot doesn't see this site any more" and that is the control working as designed. Verify against §5.1 before rolling back.

3. **Applying RCD to OneDrive.** OneDrive sites cannot have RCD applied. Attempting to apply via PowerShell returns an error; the SPAC toggle is hidden. Use sensitivity labels + DLP + sharing restrictions instead. Do not invent a workaround that puts a OneDrive into a regular site collection.

4. **Enabling RSS without curating the allowed list first.** Enabling RSS with an empty (or default) allowed list breaks org‑wide grounding for almost every user simultaneously. Curate the allowed list (or pre‑plan a 60‑minute remediation window) before enabling.

5. **Adding > 100 sites to the RSS allowed list.** The allowed list is capped at 100 sites tenant‑wide. Adding the 101st site fails or silently drops a previous entry depending on your PowerShell module version. Use hub‑associated sites to fan out within the cap.

6. **Authoring DLP policies in the default Power Platform environment.** The default environment hosts ad‑hoc maker activity across the entire tenant. Restricting connectors there breaks unrelated apps and flows. Always scope DLP to a named, governed environment.

7. **Naming connectors by guesswork.** Microsoft has renamed Copilot Studio knowledge connectors multiple times. Verify the connector display name in your tenant before authoring DLP. Do not copy a name from a release blog and assume it matches.

8. **Performing operator steps as Entra Global Admin.** Global Admin must remain a break‑glass role. Use SharePoint Admin and Power Platform Admin (PIM‑activated) for every step in §4. Capture PIM activation in evidence artifact E3.

9. **Skipping the DAG re‑run after RCD/RSS changes.** Without a post‑change DAG snapshot you have no diff against the pre‑change baseline. Auditors expect both snapshots — do not promote without them.

10. **Treating the DAG report timestamp as "now".** DAG reports lag actual permission state by 24–72 hours. A report run immediately after a change does not reflect the post‑change state. Wait for the next refresh cycle, or use PowerShell read‑backs for immediate verification.

11. **Setting `DelegateRestrictedContentDiscoverabilityManagement = $true` without a written justification.** This flag widens RCD authority beyond SharePoint Admin and must be approved by Compliance + Risk. Always log the justification to the change record before flipping the flag.

12. **Forgetting the GCC High / DoD payload limit.** A test that succeeds in commercial with a 1 MB document will silently fail in GCC High where the payload limit is ≈ 450 KB. Test agents must use representative content sizes for the target sovereign cloud.

13. **Conflating "Copilot in the site" with "org‑wide Copilot grounding".** RCD removes the site from org‑wide grounding; it does **not** remove the user's ability to invoke Copilot when they are inside the site. Reports that conflate the two lead to incorrect rollbacks.

14. **Promoting a Zone 2 change to Zone 3 with the same allowed list.** Zone 3 is typically the smallest allowed list, not the largest. Re‑curate the list for Zone 3 — do not simply copy Zone 2.

---

## §8 FSI incident handling — when grounding scope is suspected of disclosing regulated content

If post‑change verification (or any subsequent monitoring) suggests that a Copilot grounding query returned content that should have been out of scope — particularly content covered by NPI, MNPI, books‑and‑records obligations, or sensitive customer information — treat this as a potential disclosure incident and escalate immediately.

### 8.1 Trigger conditions

Treat as an incident if any of the following is true:

- A user reports finding (via Copilot grounding) content from a site that was supposed to be RCD‑restricted or absent from the RSS allowed list.
- DSPM for AI (Control 1.6) flags a Copilot session that grounded on a site outside the approved scope for that user's role.
- A regulated record (FINRA 4511 books and records, SEC 17a‑4 retained communications, GLBA‑covered NPI) was returned in a Copilot answer to a user who should not have had access.
- Post‑change DAG reports show the site is **not** in the expected state and the discrepancy cannot be reconciled within 24 hours.

### 8.2 Immediate containment (within 1 hour)

1. **Re‑apply RCD and/or remove from RSS allowed list** for the affected site(s) using the steps in §4b/§4c. Capture before/after state.
2. **Disable the affected Copilot Studio agent** if a custom agent was the disclosure path: Copilot Studio → agent → Settings → Disable.
3. **Preserve evidence** — the UAL records, the agent transcript, the DAG reports — by exporting them now (UAL retention is finite; do not rely on "we can pull it later").
4. **Open an incident ticket** in your firm's incident management system; reference Control 4.6 and the named site(s) and agent(s).

### 8.3 Regulatory notification timelines (US financial services)

The following table summarizes the **outer bounds** of US regulatory notification timelines that may apply when grounding scope failures result in disclosure of regulated information. Your General Counsel and Compliance officers determine which apply to a given incident — do not interpret this table as legal advice.

| Regulator / Rule | Threshold for notification | Outer notification deadline |
| --- | --- | --- |
| **NY DFS — 23 NYCRR 500 §500.17(a)** | "Cybersecurity event" affecting a Covered Entity | **72 hours** to notify the NY DFS Superintendent |
| **SEC — Reg S‑P §248.30(a)(4)** (as amended) | Unauthorized access or use of "sensitive customer information" | **30 days** to notify affected customers; **federal regulator within 1 business day** of detection |
| **FINRA — Rule 4530** | Reportable event per Rule 4530 categories | **Quarterly** statistical reporting; specific events within prescribed periods (consult Rule text) |
| **FINRA — Reg Notice 25‑07** | AI‑related supervisory failure / oversight gap | Member firm responsibility to integrate into existing 4530 / supervisory reporting |
| **GLBA Safeguards Rule — 16 CFR §314.4(j)** | Unauthorized acquisition of unencrypted customer information affecting **≥ 500 consumers** | **30 days** to notify the Federal Trade Commission |
| **SEC — Rule 17a‑4 / SOX 302/404** | n/a — these are evidence preservation obligations, not notification rules | Preserve all relevant records for the prescribed retention period; do not delete agent transcripts, UAL exports, or DAG reports during incident response |

### 8.4 Escalation path

1. **Hour 0:** Operator (or monitoring system) detects symptom → opens incident ticket → engages Compliance Officer.
2. **Hour 0–1:** Containment per §8.2.
3. **Hour 1–4:** Compliance Officer + General Counsel determine which regulatory clocks have started (table §8.3) and notify Risk lead.
4. **Hour 4–24:** Forensic capture — full UAL export for the affected window, full agent transcript export, full DAG snapshot, full SPAC RCD/RSS state snapshot, full PPAC DLP policy snapshot.
5. **Hour 24–72:** Regulatory notifications (per §8.3) prepared and dispatched as determined by General Counsel.
6. **Day 7+:** Post‑incident review; update Control 4.6 runbooks; update §5 test scenarios with any new failure mode discovered; record in MILESTONES.md if a framework‑level change resulted.

### 8.5 Cross‑reference to AI incident response playbook

For the full incident response procedure (including communication templates, SOC engagement, and customer notification language), follow the [AI Incident Response Playbook](../../incident-and-risk/ai-incident-response-playbook.md). Control 4.6 incidents are a specific subtype of AI agent disclosure incident; the playbook governs the broader response and this section governs the Control 4.6‑specific containment.

---

## §9 Cross‑references

This walkthrough is one part of a larger framework. Use the cross‑references below to navigate related controls and companion playbooks.

### 9.1 Control 4.6 companion playbooks

- [`powershell-setup.md`](powershell-setup.md) — Bulk PowerShell automation for RCD across thousands of sites; canonical RSS cmdlet set; delegation flag automation.
- [`verification-testing.md`](verification-testing.md) — Repeatable verification queries (KQL / SPO / Graph) you run after each change.
- [`troubleshooting.md`](troubleshooting.md) — Common failure modes and recovery paths (rolling back RCD, restoring RSS allowed‑list sites, DLP precedence questions).

### 9.2 Related controls (read in this order)

| Control | Relationship to 4.6 |
| --- | --- |
| [4.1 — SharePoint Information Access Governance / Restricted Content Discovery posture](../../../controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md) | Provides the IAG posture review that feeds §4a nominations. |
| [4.8 — Item‑level permission scanning](../../../controls/pillar-4-sharepoint/4.8-item-level-permission-scanning-agent-knowledge-sources.md) | Once a site is in scope (or RCD‑restricted), 4.8 governs item‑level over‑sharing inside the site. |
| [1.5 — Data Loss Prevention and sensitivity labels](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) | Compensating control for OneDrive (where RCD is unavailable) and reinforcement for any RCD'd site. |
| [1.6 — Microsoft Purview DSPM for AI](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md) | Inventory and posture monitoring for Copilot grounding usage; flags scope drift that 4.6 must remediate. |
| [1.7 — Comprehensive audit logging and compliance](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) | UAL baseline that makes evidence artifacts E8 and E13 possible. |
| [1.8 — Runtime protection and external threat detection](../../../controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md) | Detection layer that may surface a Control 4.6 incident before users do. |
| [1.12 — Insider risk detection and response](../../../controls/pillar-1-security/1.12-insider-risk-detection-and-response.md) | Insider risk signals that should feed §4a nominations. |
| [1.14 — Data minimization and agent scope control](../../../controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md) | Companion control that governs Copilot Studio agent scope at the data‑minimization layer; works in tandem with 4.6's grounding scope. |
| [2.16 — RAG source integrity validation](../../../controls/pillar-2-management/2.16-rag-source-integrity-validation.md) | Once 4.6 has narrowed grounding scope, 2.16 validates the integrity of the remaining sources. |

### 9.3 Reference materials

- [Role Catalog](../../../reference/role-catalog.md) — canonical short names for every role referenced in this walkthrough.
- [Parent control: 4.6 Grounding Scope Governance](../../../controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md) — full control specification including regulatory mappings, zone‑specific requirements, and verification criteria.
- [AI Incident Response Playbook](../../incident-and-risk/ai-incident-response-playbook.md) — overall AI agent incident response procedure.

---

*Updated: April 2026 | Version: v1.6.2 | UI Verification Status: Current*