# Portal Walkthrough — Control 3.6: Orphaned Agent Detection and Remediation

!!! danger "READ FIRST — Scope and Sibling Routing"
    This walkthrough covers **portal-first detection and remediation of orphaned agents** across Microsoft 365 Copilot, Copilot Studio, Power Platform, SharePoint, and Entra. It is the primary operational procedure for Control 3.6.

    **In scope**

    | Topic | Where it lives |
    |-------|----------------|
    | Agent 365 admin center **Ownerless Agents** governance card | §2 |
    | Entra **Lifecycle Workflows** leaver signals that cascade to agents | §3 (cross-references Control 2.26) |
    | **Power Platform admin center (PPAC)** maker-departed and environment-owner-departed detection | §4, §5 |
    | **SharePoint** Copilot agent author-disabled audit | §6 |
    | **PPAC Recycle bin** and deleted-environment reconciliation | §7 |
    | **Microsoft Defender for Cloud Apps** shadow-agent discovery | §8 |
    | Remediation ordering (Agent 365 inline → 2.26 sponsor manager-transfer → PPAC/Copilot Studio reassignment → bulk Graph/PowerShell) | §9 |
    | Zone-specific cadence (Z3 daily / Z2 weekly / Z1 monthly) and examiner evidence | §10 |

    **Out of scope — routed to siblings**

    | Topic | Route to |
    |-------|----------|
    | Bulk Graph API and Microsoft Graph PowerShell scripting | [powershell-setup.md](./powershell-setup.md) |
    | Tenant-wide sweep and KPI verification queries | [verification-testing.md](./verification-testing.md) |
    | UI anomalies, throttling, stale cache, delta-badge mismatches | [troubleshooting.md](./troubleshooting.md) |
    | Authoritative HR leaver feed configuration | [Control 2.26 — Entra Agent ID Identity Governance](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md) |
    | Master agent registry definition | [Control 1.2 — Agent Registry and Integrated Apps Management](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md) |
    | Agent 365 admin center Overview / Usage / Capacity surfaces | [Control 2.25 — Agent 365 Admin Center Governance Console](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md) |
    | Agent 365 analytics and long-window retention | [Control 3.13 — Agent 365 Admin Center Analytics](../../../controls/pillar-3-reporting/3.13-agent-365-admin-center-analytics.md) |

    If the task at hand is **not** a portal-driven orphan detection or remediation action, stop and follow the routing above before continuing.

!!! warning "Hedged-Language Reminder"
    Detection signals **support** ownership-attestation and supervisory review obligations; they do **not replace** registered-principal review under FINRA Rule 3110, recordkeeping under SEC 17a-4(f), or independent risk-management oversight under OCC Bulletin 2011-12 / Fed SR 11-7. All evidence captured in this walkthrough is intended to **aid** examiners; final attestation rests with named human owners.

!!! info "License and Program Requirements"

    | Capability | License / SKU |
    |------------|---------------|
    | Agent 365 admin center governance cards (Ownerless Agents) | Microsoft 365 Copilot tenant license; Agent 365 program enrollment |
    | Entra Lifecycle Workflows | Microsoft Entra ID Governance (P1 + ID Governance add-on, or Suite) |
    | Power Platform admin center | Power Platform Admin role; Power Apps / Automate per-app or per-user plan inventory rights |
    | Microsoft Defender for Cloud Apps | Defender for Cloud Apps standalone or E5 / E5 Security |
    | Purview Audit (long retention) | Microsoft 365 E5 / E5 Compliance or Audit Premium add-on |

!!! warning "Sovereign Cloud Parity"

    | Cloud | Agent 365 Ownerless card | Lifecycle Workflows | PPAC maker/env signals | Defender for Cloud Apps shadow detection | Compensating control |
    |-------|--------------------------|---------------------|------------------------|------------------------------------------|----------------------|
    | Commercial | GA | GA | GA | GA | n/a |
    | GCC | GA (parity may lag commercial by 30–90 days) | GA | GA | GA | n/a |
    | GCC High | Limited / staged rollout | GA | GA | Limited | **Quarterly manual reconciliation worksheet** (see §1) |
    | DoD | Not available at time of writing | Limited | GA | Not available | **Quarterly manual reconciliation worksheet** (see §1) |

    Verify rollout status against the Microsoft 365 roadmap and the Agent 365 sovereign release notes before each control execution. Sovereign tenants must keep the §1 compensating-control worksheet on file as the primary evidence artifact until parity is confirmed.

!!! tip "Portal Navigation May Shift"
    Microsoft updates portal blade names and navigation regularly. Where this walkthrough cites a path such as **Microsoft 365 admin center → Agents → Overview**, treat the path as descriptive, not authoritative. If the blade has moved, anchor on the **page title** and any documented telemetry node IDs rather than the breadcrumb. Capture the new path in [troubleshooting.md](./troubleshooting.md) so it can be promoted into the next revision.

## Document Map

| § | Section | Primary surface | Verification criterion |
|---|---------|-----------------|------------------------|
| 0 | Pre-flight prerequisites and triage | All portals | VC-1 (roles, licenses, scope) |
| 1 | Sovereign-cloud variant and compensating controls | Manual worksheet | VC-2 |
| 2 | Signal #1 — Agent 365 Ownerless Agents card | Microsoft 365 admin center → Agents → Overview | VC-3 |
| 3 | Signal #2 — Entra Lifecycle Workflows leaver cascade | Entra admin center → Identity Governance → Lifecycle Workflows | VC-3, VC-4 |
| 4 | Signal #3 — PPAC maker-departed | Power Platform admin center → Resources → Power Apps | VC-3 |
| 5 | Signal #4 — PPAC environment-owner-departed | PPAC → Environments | VC-3 |
| 6 | Signal #5 — SharePoint Copilot agent author-disabled | SharePoint admin center → Content services → Copilot agents | VC-3 |
| 7 | Signal #6 — PPAC Recycle bin and deleted-environment audit | PPAC → Environments → Recycle bin | VC-5 |
| 8 | Signal #10 — Shadow-agent discovery via Defender for Cloud Apps | Defender XDR → Cloud Apps → Cloud App Catalog | VC-6 |
| 9 | Remediation walkthrough (4-step ordering) | Agent 365 → 2.26 → PPAC / Copilot Studio → bulk Graph | VC-7 |
| 10 | Evidence capture, zone cadence, and examiner packet | All portals + Purview | VC-8 |

The numbering of detection signals (#1, #2, #3, #4, #5, #6, #10) intentionally mirrors the **Detection Signal Sources** table in [Control 3.6](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md). Signals #7 (inactivity), #8 (license-expired), and #9 (broken connector) are covered in [verification-testing.md](./verification-testing.md) because they are query-driven rather than portal-driven.

## 0. Pre-flight Prerequisites and Triage

Before opening any portal blade, complete the pre-flight checks below. A failed pre-flight gate is itself an auditable finding and must be logged in the control session worksheet.

### 0.1 Role elevation via Entra PIM

Every role used in this walkthrough must be activated through **Microsoft Entra Privileged Identity Management (PIM)** with a justification reference and, where required, approver sign-off. Session maximums of 4–8 hours are recommended; do not leave roles permanently assigned.

| Canonical role | Surfaces required for | Elevation recommendation |
|----------------|----------------------|--------------------------|
| AI Administrator | Agent 365 admin center, Ownerless card, agent reassignment | 4 h session, ticket justification |
| AI Governance Lead | Control owner sign-off on reconciliation worksheet | 8 h session, dual-approver for Z3 findings |
| Power Platform Admin | PPAC maker, environment, recycle bin views | 4 h session, ticket justification |
| Entra Agent ID Admin | Agent service-principal / managed identity reassignment | 4 h session |
| Entra Identity Governance Admin | Lifecycle Workflows review and manager-transfer confirmation | 4 h session |
| Entra Global Reader | Read-only sweep of directory and sign-in logs | 8 h session |
| Purview Compliance Admin | Audit search, WORM evidence retention confirmation | 4 h session |

!!! example "Examiner Evidence Box — Role elevation"
    **Capture for every control execution:**

    1. PIM activation history export (CSV) filtered to the control-session window.
    2. Ticket ID from the change / access-management system (ServiceNow, Jira, Azure DevOps).
    3. Screenshot of the PIM "My roles" blade showing active assignments at session start.
    4. Expiration timestamp for each activation.

    Store in the Purview-backed evidence library tagged **Control=3.6, Session=<ISO-date>**.

### 0.2 License and feature verification

1. In the **Microsoft 365 admin center**, confirm the tenant has an active Copilot license and that **Agent 365 admin center** is enrolled (visible under **Settings → Org settings → Services**).
2. In **Microsoft Entra admin center**, confirm **ID Governance** SKU coverage at **Identity Governance → Overview**.
3. In **Power Platform admin center**, confirm **Admin analytics** is enabled at **Tenant → Analytics settings**.
4. In **Defender XDR**, confirm **Cloud Apps** is provisioned and the **Cloud App Catalog** loads with a non-zero discovered-app count.
5. Record the **tenant region** and **sovereign-cloud flag** on the session worksheet — this determines whether §1 compensating controls apply.

### 0.3 Authoritative-source readiness

Orphan detection is only as reliable as the upstream signals that drive it. Confirm the following **before** executing any detection sweep:

| Source | Owner | Check |
|--------|-------|-------|
| HR leaver feed | Entra Identity Governance Admin (via 2.26) | Last sync ≤ 24 h, row count within ±5% of expected baseline |
| Entra disabled-user set | Entra Global Reader | `accountEnabled eq false` count stable; no anomalous spike |
| Agent registry (Control 1.2) | AI Governance Lead | Last attestation ≤ 30 days; owner field populated for 100% of registered agents |
| Power Platform maker / environment export | Power Platform Admin | Last export ≤ 7 days |
| Purview audit ingestion | Purview Compliance Admin | No ingestion-lag banner on **Purview → Audit** landing page |

A failure in any row **blocks** the control session; open a ticket and re-schedule.

### 0.4 Pre-flight gate checklist

- [ ] All required roles activated via PIM and evidence captured (§0.1)
- [ ] Licensing and feature flags confirmed (§0.2)
- [ ] Authoritative-source freshness confirmed (§0.3)
- [ ] Sovereign-cloud flag recorded on session worksheet
- [ ] Zone scope (Z1 / Z2 / Z3) declared for this session
- [ ] Evidence library path and session tag prepared in Purview
- [ ] ITSM ticket opened and linked to the session worksheet

Only proceed to §1 or §2 after every box is ticked.

!!! tip "Cross-Reference"
    Pre-flight role and licensing checks overlap with [Control 2.25 §0 pre-flight](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md). Do not re-capture identical evidence; reference the most recent 2.25 session worksheet where possible.

## 1. Sovereign Cloud Variant and Compensating Controls

GCC High and DoD tenants (and occasionally GCC during staged rollouts) may not yet have full parity with the Agent 365 Ownerless Agents card and Defender for Cloud Apps shadow-agent discovery. Until parity is confirmed in the Microsoft roadmap, the **Quarterly Manual Reconciliation Worksheet** below becomes the **primary evidence artifact** for Control 3.6 in those tenants.

### 1.1 Worksheet inputs

Export the following four artifacts, each timestamped within the same 24-hour window:

| Input | Source | Export format |
|-------|--------|---------------|
| A — Agent registry | Control 1.2 registry system of record | CSV with columns: AgentId, DisplayName, Owner (UPN), Sponsor (UPN), Maker (UPN), Environment, LastAttested |
| B — HR leaver list | HR system of record (Workday, SAP SuccessFactors, etc.) | CSV with columns: EmployeeId, UPN, TerminationDate, Status |
| C — Entra disabled-user list | Entra admin center → Users → Filter `accountEnabled = false` | CSV |
| D — Power Platform maker / environment export | PPAC → Analytics → Export | CSV |

### 1.2 Reconciliation logic

For every row in **A**:

1. If `Owner`, `Sponsor`, or `Maker` UPN appears in **B** or **C**, flag as **candidate orphan**.
2. If the agent's `Environment` is absent from **D** (i.e., environment deleted or quarantined), flag as **candidate orphan**.
3. If `LastAttested` is older than 90 days, flag as **stale-attestation**.
4. Any row with no flags is considered **reconciled** for this quarter.

### 1.3 Worksheet output and signing

The completed worksheet must be:

1. Rendered to PDF with the reconciliation date, tenant ID, and sovereign-cloud flag in the header.
2. **Dual-signed** by the AI Governance Lead and one of (Entra Identity Governance Admin, Purview Compliance Admin). Digital signatures via a Purview-approved signing workflow are acceptable; wet signatures scanned to PDF are also acceptable.
3. Stored in the Purview evidence library with **retention label = 6 years WORM** to help meet SEC 17a-4(f) recordkeeping expectations.
4. Linked from the ITSM session ticket.

!!! example "Examiner Evidence Box — Sovereign reconciliation"
    **Capture each quarter:**

    1. The four input CSVs (A, B, C, D), hashed (SHA-256) and stored alongside the worksheet.
    2. The rendered PDF worksheet with dual signatures.
    3. The Purview evidence-library URL and retention-label confirmation screenshot.
    4. ITSM ticket ID and linked change record.

### 1.4 Commercial / GCC tenants

Commercial and GCC tenants with full Agent 365 Ownerless card parity **do not** execute §1.2 — proceed directly to §2. However, commercial tenants are **encouraged** to run the manual worksheet **annually** as a defense-in-depth compensating control; this aids supervisory review under FINRA Rule 3110 and supports the "independent review" expectation in OCC Bulletin 2011-12 / Fed SR 11-7.

!!! tip "Cross-Reference"
    The HR leaver feed and Entra disabled-user surfaces are configured in [Control 2.26](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md). If inputs B or C are stale or missing, remediate 2.26 **before** continuing here.

## 2. Signal #1 — Agent 365 Ownerless Agents Card

The **Ownerless Agents** governance card in the Agent 365 admin center is the **primary portal-driven detection surface** for orphaned agents in commercial and GCC tenants. It aggregates signals from Entra directory state, the Control 1.2 agent registry, Power Platform maker telemetry, and SharePoint author state.

### 2.1 Navigation

1. Sign in to the **Microsoft 365 admin center** at [https://admin.microsoft.com](https://admin.microsoft.com) with the **AI Administrator** role activated.
2. In the left nav, expand **Copilot** (or **Agents**, depending on tenant rollout) and select **Overview**.
3. Locate the governance strip near the top of the Overview page. The **Ownerless Agents** card is one of the governance cards alongside **Unattested Agents**, **High-Risk Agents**, and **Expired Credentials**.

[Screenshot anchor: `docs/images/3.6/EXPECTED.md#2-1-ownerless-card-overview`]

### 2.2 Reading the card

The card surfaces four elements:

| Element | Meaning | Action |
|---------|---------|--------|
| Headline count | Number of agents flagged ownerless at last refresh | Compare against last session's count |
| Week-over-week delta badge | `+N` or `-N` vs. the prior 7-day snapshot | Investigate any upward delta as a Z3 signal |
| Top-N table | Up to ten highest-priority ownerless agents (typically ranked by usage, sensitivity label, or Zone) | Drill in via **Review** |
| "Last refreshed" timestamp | Card data freshness | Expect ≤ 24 h for commercial / GCC |

!!! warning "Stale card data"
    If **Last refreshed** is more than 48 hours old, treat the card as untrusted and escalate to [troubleshooting.md](./troubleshooting.md). Do not capture evidence from a stale card.

### 2.3 Drill-in and inline Assign Owner

1. From the card, click **Review** (or **See all**) to open the full **Ownerless Agents** list blade.
2. Filter by **Zone** if only a subset is in scope for this session:
    - **Zone 3 (Enterprise)** — daily cadence
    - **Zone 2 (Team)** — weekly cadence
    - **Zone 1 (Personal)** — monthly cadence
3. For each row, click the **Assign Owner** action in the inline row menu (or the flyout pane on the right).
4. In the **Assign Owner** dialog:
    - Enter the replacement owner UPN. The picker resolves against Entra directory; only active (non-disabled) users may be selected.
    - Optionally enter a **secondary owner** (recommended for Zone 3 agents).
    - Enter a **justification** (required) that references the ITSM ticket ID.
    - Click **Assign**.
5. Confirm the row disappears from the ownerless list on the next refresh (may take up to 15 minutes) or that the delta badge decrements accordingly.

[Screenshot anchor: `docs/images/3.6/EXPECTED.md#2-3-inline-assign-owner`]

### 2.4 Zone cadence and SLA

| Zone | Detection cadence | Remediation SLA from detection to assigned owner |
|------|-------------------|--------------------------------------------------|
| Z3 (Enterprise) | Daily card review | 24 hours |
| Z2 (Team) | Weekly card review | 5 business days |
| Z1 (Personal) | Monthly card review | 20 business days |

SLAs help meet supervisory expectations under FINRA Rule 3110 for timely remediation of control findings. They do **not** guarantee examination outcomes; document any SLA breach with root-cause analysis in the session worksheet.

### 2.5 Bulk export for evidence

From the full Ownerless Agents blade:

1. Click **Export** (top-right) and choose **CSV**.
2. Rename the downloaded file to `ownerless-agents_<tenantId>_<ISO-date>.csv`.
3. Hash the file (SHA-256) and store both the CSV and the hash in the Purview evidence library.
4. Capture a full-page screenshot of the blade header (including refresh timestamp and total count).

!!! example "Examiner Evidence Box — Ownerless card session"
    **Capture for every session:**

    1. Overview page screenshot showing the **Ownerless Agents** card with headline count, delta badge, and refresh timestamp.
    2. Full-page screenshot of the drill-in blade with Zone filter applied.
    3. CSV export (hashed) of the filtered blade.
    4. One screenshot per **Assign Owner** action showing the dialog with justification text.
    5. Post-remediation screenshot of the card showing decremented count (may be a subsequent-day capture).
    6. ITSM ticket IDs referenced in justifications.

!!! tip "Cross-Reference"
    The Ownerless Agents card shares a governance strip with the cards described in [Control 2.25 §3](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md). If the card is missing entirely (not just empty), verify Agent 365 program enrollment before assuming a detection gap.

## 3. Signal #2 — Entra Lifecycle Workflows Leaver Cascade

When an agent's **sponsor** (the registered human accountable party from Control 1.2) leaves the organization, Entra **Lifecycle Workflows** is the authoritative detection channel. Control 2.26 defines the upstream configuration; this section covers the **portal review** that Control 3.6 owns.

### 3.1 Navigation

1. Sign in to the **Microsoft Entra admin center** at [https://entra.microsoft.com](https://entra.microsoft.com) with **Entra Identity Governance Admin** activated.
2. Navigate to **Identity Governance → Lifecycle Workflows**.
3. Select the **Workflows** tab and locate the leaver workflow configured under 2.26 (commonly named `Leaver - Agent Sponsor Cascade` or similar).

[Screenshot anchor: `docs/images/3.6/EXPECTED.md#3-1-lifecycle-workflows`]

### 3.2 Reviewing execution history

1. Click into the leaver workflow.
2. Select **Workflow history** (or **Runs**, depending on UI version).
3. Filter the run history by the session window (typically last 24 h for Z3, last 7 days for Z2, last 30 days for Z1).
4. Confirm each run's **status = Succeeded**. Any **Failed** or **Partially completed** rows are in-scope Control 3.6 findings even if no agent is yet visibly orphaned — the **cascade did not run**, which means the Ownerless card may underreport.
5. Drill into any failed run to capture the error reason, impacted user UPN, and downstream agents (listed under **Tasks**).

### 3.3 Manager-transfer confirmation

The 2.26 workflow default is to **transfer agent sponsorship to the departing user's manager** on termination. This is a default, not a guarantee; Control 3.6 confirms the transfer actually occurred for each leaver in the window.

For each successful leaver run:

1. Capture the **prior sponsor UPN** (the leaver) and the **new sponsor UPN** (expected to be the manager per Entra directory at `manager` attribute).
2. Cross-check against the agent registry (Control 1.2) — the registry's sponsor field should reflect the new UPN within the 2.26-defined SLA (typically 24 h).
3. If the registry is **not** updated, open a finding against 2.26 **and** override the sponsor manually via the registry workflow defined in Control 1.2.

### 3.4 Override scenarios

Manager-transfer is inappropriate in the following cases; override is required:

| Scenario | Override target |
|----------|----------------|
| Manager has also left or is disabled | AI Governance Lead routes to BU-designated backup sponsor |
| Agent is Zone 3 (Enterprise) and manager lacks required clearance | Route to named Zone 3 sponsor pool per 1.2 |
| Agent spans multiple BUs | Route per agent registry `sponsor-routing` field |

Overrides are executed via the Agent 365 Ownerless card (§2.3) — the agent will surface there until a valid sponsor is assigned.

!!! example "Examiner Evidence Box — Lifecycle Workflows cascade"
    **Capture each session:**

    1. Screenshot of **Workflow history** filtered to the session window showing run counts and status distribution.
    2. CSV export of the run history (via **Export** button where available, or Graph API per [powershell-setup.md](./powershell-setup.md)).
    3. For each **Failed** run: screenshot of the error detail and ITSM ticket linking the finding.
    4. For each override: justification document referencing the override scenario above.

!!! tip "Cross-Reference"
    The upstream workflow configuration, HR feed mapping, and manager-transfer defaults are owned by [Control 2.26](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md). Do not modify workflow definitions from this walkthrough — route configuration changes through 2.26.

## 4. Signal #3 — PPAC Maker-Departed

Power Platform **makers** are the low-code builders who authored Copilot Studio agents, Power Apps, and Power Automate flows. A maker becoming disabled in Entra does not automatically orphan the agent — PPAC retains the reference until administratively updated — so Control 3.6 sweeps PPAC to catch maker-departed orphans that the Ownerless card may miss during rollout lag.

### 4.1 Navigation

1. Sign in to the **Power Platform admin center** at [https://admin.powerplatform.microsoft.com](https://admin.powerplatform.microsoft.com) with **Power Platform Admin** activated.
2. In the left nav, select **Resources → Power Apps** (for canvas / model-driven / Copilot Studio agents surfaced as apps).
3. Alternatively select **Resources → Copilot agents** or **Resources → Chatbots** for the Copilot Studio–specific list (UI naming varies by rollout).

[Screenshot anchor: `docs/images/3.6/EXPECTED.md#4-1-ppac-resources-power-apps`]

### 4.2 Filtering by maker

1. In the top-right of the list blade, open the **Filters** pane.
2. Set **Owner** (or **Maker**) to **All users**.
3. Sort by **Modified** descending to prioritize recent activity.
4. Export the full list via **Export to Excel**; the export includes columns: `DisplayName`, `AppId` / `BotId`, `Owner`, `Environment`, `Modified`, `Created`.

### 4.3 Cross-referencing against Entra disabled users

1. Export the Entra disabled-user set (see §0.3, input C).
2. In a controlled worksheet (Excel with macros disabled, or a governance KQL workbook), join the two exports on UPN.
3. Every PPAC row whose owner UPN matches the disabled-user set is an **in-scope Control 3.6 finding**.
4. For each finding, note:
    - The **environment** the agent lives in (important for §5 and §7).
    - Whether the agent has a **co-owner** (if yes, co-owner auto-promotion may apply — verify in §9.3).
    - The agent's **Zone** per the 1.2 registry (drives cadence and SLA).

### 4.4 Remediation from this surface

!!! warning "PPAC reassignment is maker-scoped, not sponsor-scoped"
    Reassigning the **maker / owner** in PPAC transfers edit rights on the underlying Power Platform resource. It does **not** update the agent **sponsor** in the Control 1.2 registry. Both updates are required; see §9 for the ordering.

Inline reassignment steps:

1. Select the row and click **See details → Share** (for Power Apps) or **Settings → Administration** (for Copilot Studio agents).
2. Add the replacement owner (active Entra user).
3. For Power Apps, set the replacement as **Co-owner** first, then remove the disabled principal in a second step to avoid losing the resource reference.
4. For Copilot Studio agents, use the **Assign owner** action under the agent's admin blade.
5. Capture a screenshot of the post-change ownership state.

!!! example "Examiner Evidence Box — PPAC maker-departed"
    1. PPAC export CSV (hashed).
    2. Join-result CSV listing findings with matched UPN and agent IDs.
    3. Pre- and post-remediation screenshots of each remediated agent's ownership blade.
    4. Confirmation that the Control 1.2 registry sponsor field was updated via §9.

!!! tip "Cross-Reference"
    For bulk PPAC reassignment across thousands of rows, pivot to the Power Platform admin PowerShell module procedures in [powershell-setup.md](./powershell-setup.md#bulk-maker-reassignment).

## 5. Signal #4 — PPAC Environment-Owner-Departed

An environment-owner-departed event is structurally more severe than a maker-departed event because the **environment** is the security boundary for every agent within it. A disabled environment owner can leave dozens of agents in a fragile state even when each individual maker is still active.

### 5.1 Navigation

1. In **PPAC**, select **Environments** in the left nav.
2. The default view lists all environments with columns **Name**, **Type**, **Region**, **Created on**, **Created by**.
3. Add the **Security group** and **Owner** columns via the column chooser if not already visible.

[Screenshot anchor: `docs/images/3.6/EXPECTED.md#5-1-ppac-environments`]

### 5.2 Filtering and export

1. Export the full environment list via **Export to Excel**.
2. Cross-reference the **Created by** and any environment-admin role assignments against the Entra disabled-user set.
3. Any environment whose owner UPN matches the disabled-user set is in-scope for Control 3.6.

### 5.3 Reassignment

1. Click into the environment.
2. Select **Settings → Users + permissions → Users**.
3. Search for the disabled UPN, confirm the role assignment(s).
4. Add the replacement environment admin (active user, typically the BU Power Platform CoE lead or a named delegate).
5. Remove the disabled principal in a second action.
6. For **production** environments containing Zone 3 agents, require dual-approver sign-off before removal — capture the second approver in the ITSM ticket.

### 5.4 Special handling for Default and Developer environments

| Environment type | Special handling |
|------------------|------------------|
| Default | Cannot be deleted; reassign to tenant Power Platform Admin pool. |
| Developer (per-user) | If the developer is a leaver, schedule the environment for §7 recycle-bin review after grace window; do not auto-delete during this session. |
| Trial | Allow expiration; capture the expiration date in the worksheet. |
| Production / Sandbox | Reassign as above; never delete during a Control 3.6 session. |

!!! example "Examiner Evidence Box — Environment-owner-departed"
    1. Environment list export (hashed).
    2. Pre- and post-remediation screenshots of **Settings → Users + permissions** for each remediated environment.
    3. Dual-approver record for any Zone 3 production environment.
    4. List of Developer environments deferred to §7.

!!! tip "Cross-Reference"
    Environment lifecycle policy (creation gates, retention, deletion) lives in the Pillar 1 environment-strategy controls; this section addresses **only** the orphan-detection slice. Refer to those controls for any policy override.

## 6. Signal #5 — SharePoint Copilot Agent Author-Disabled

SharePoint-hosted Copilot agents (authored via **Copilot in SharePoint**) carry their own author attribution that is independent of the Agent 365 Ownerless card during rollout. Catching these agents requires a targeted SharePoint admin center sweep.

### 6.1 Navigation

1. Sign in to the **SharePoint admin center** at `https://<tenant>-admin.sharepoint.com`. The AI Administrator or a delegated SharePoint Admin role is required.
2. In the left nav, expand **Content services** and select **Copilot agents** (may appear as **Agents** or **Copilots** depending on rollout).
3. If the blade is not present, the feature may be disabled at the tenant level; confirm via **Settings → Copilot** before escalating as a finding.

[Screenshot anchor: `docs/images/3.6/EXPECTED.md#6-1-sharepoint-copilot-agents`]

### 6.2 Reviewing authorship

1. The blade lists Copilot agents with **Name**, **Site URL**, **Created by**, **Modified by**, **Last modified**.
2. Sort by **Last modified** descending.
3. Export via **Export** (CSV).
4. Cross-reference **Created by** and **Modified by** UPNs against the Entra disabled-user set (§0.3 input C).
5. Any match is an in-scope finding.

### 6.3 Remediation

SharePoint Copilot agents are tied to a **site**; reassignment is effectively a site-owner change:

1. From the agent row, click **Open site** to navigate to the parent site.
2. In the site's **Settings → Site permissions**, confirm the site owner is active; if not, add a new site owner via the standard SharePoint site-ownership process (typically owned by the site-provisioning control, not by 3.6).
3. Return to the Copilot agents blade and click **Edit** on the agent. If the editor prompts for a new primary author, select the replacement.
4. Where the agent was built against a SharePoint list or library that the departed author uniquely owned, confirm list-item permissions are not broken (check the site's **Shared with** pane).

!!! example "Examiner Evidence Box — SharePoint Copilot agents"
    1. Copilot agents blade export (CSV, hashed).
    2. List of matched author-disabled findings.
    3. Pre- and post-remediation site-permission screenshots.
    4. Any site-provisioning tickets opened for downstream site-owner changes.

!!! tip "Cross-Reference"
    The broader SharePoint site-ownership lifecycle is governed by Purview and SharePoint governance controls outside Control 3.6. This section narrows to the **Copilot agent author** attribute specifically.

## 7. Signal #6 — PPAC Recycle Bin and Deleted-Environment Audit

An orphaned agent may be inadvertently deleted along with its environment, either by a leaver prior to departure or by a downstream cleanup job. The PPAC **Recycle bin** provides a 7-to-30-day window (varies by environment type and tenant configuration) in which deleted environments can be recovered — Control 3.6 owns the audit of this window to ensure **no registered agent was silently deleted**.

### 7.1 Navigation

1. In **PPAC**, navigate to **Environments**.
2. Click **Recycle bin** (top-right action bar).
3. The recycle bin lists recently deleted environments with **Name**, **Deleted on**, **Deleted by**, **Type**, and a **Restore** action.

[Screenshot anchor: `docs/images/3.6/EXPECTED.md#7-1-recycle-bin`]

### 7.2 Audit procedure

1. Export the recycle bin (screenshot + copy the table into the session worksheet; a direct export may not be available in all rollouts).
2. For each deleted environment, check the Control 1.2 agent registry for any agent whose `Environment` field matches the deleted environment name or ID.
3. Any match within the recycle bin retention window is a **high-severity finding** — capture:
    - Environment name / ID
    - Deleted-on timestamp
    - Deleted-by UPN (whether active or disabled)
    - List of affected agents from the 1.2 registry
4. Engage the AI Governance Lead immediately to determine whether to **Restore** the environment or **retire** the affected agents from the registry.

### 7.3 Restore vs. retire decision

| Decision | When appropriate |
|----------|-----------------|
| Restore environment | Deletion was unintended, registered Zone 2 or Zone 3 agent(s) still in-scope, within retention window |
| Retire from registry | Deletion was intentional per a documented decommissioning ticket, and no registered agent is impacted |
| Escalate | Deleted-by UPN is disabled (possible insider risk indicator) — engage security incident response |

Restoration is performed by clicking **Restore** on the recycle bin row. Restoration may take several minutes; confirm the environment reappears in the **Environments** blade and that the agents report healthy via Copilot Studio before closing the finding.

!!! example "Examiner Evidence Box — Recycle bin audit"
    1. Recycle bin screenshot for the audit window.
    2. Cross-reference worksheet mapping deleted environments to registry agents.
    3. Restore-vs-retire decision record, including approver and ticket ID.
    4. Post-restoration health screenshot for any restored environments.

!!! warning "Retention window is not guaranteed"
    Recycle bin retention varies by environment type and tenant configuration; do not rely on the recycle bin as a primary recovery mechanism. The §1 reconciliation worksheet and the §10 evidence library provide the durable audit trail.

## 8. Signal #10 — Shadow-Agent Discovery via Defender for Cloud Apps

**Shadow agents** are AI agents operating in the tenant's data plane that are **not** present in the Control 1.2 registry. They may be legitimate experiments, vendor-delivered components, or unauthorized tools. Every shadow agent is implicitly ownerless until reconciled, so Control 3.6 sweeps Defender for Cloud Apps to surface them.

### 8.1 Navigation

1. Sign in to **Microsoft Defender XDR** at [https://security.microsoft.com](https://security.microsoft.com) with a role that includes Defender for Cloud Apps read access.
2. In the left nav, expand **Cloud apps** and select **Cloud app catalog**.
3. Apply the built-in filter **Category = Generative AI** (UI may label this **AI / Gen AI** depending on catalog version).

[Screenshot anchor: `docs/images/3.6/EXPECTED.md#8-1-cloud-app-catalog`]

### 8.2 Triage

1. Review the filtered list of discovered AI services and agent frameworks.
2. For each entry, note:
    - **Users** (count of users with activity in the discovery window)
    - **Traffic** (bytes / transactions)
    - **Last seen**
    - **Sanction status** (Sanctioned / Unsanctioned / Monitored / null)
3. Cross-reference each entry against the Control 1.2 registry:
    - **Registered** → no action, but confirm sanction status = Sanctioned.
    - **Not registered, legitimate** → open an onboarding ticket routed to the AI Governance Lead.
    - **Not registered, not legitimate** → mark **Unsanctioned** in Defender for Cloud Apps and open a finding.
4. Export the filtered catalog via **Export → CSV**.

### 8.3 Unsanctioning workflow

To mark an app **Unsanctioned**:

1. Click into the app row.
2. In the top-right, toggle **Tag as Unsanctioned** (enterprise policy may trigger automatic block via Defender for Endpoint / web content filtering).
3. Confirm the change propagates to the **Discovered apps** dashboard.
4. Record the justification and approver in the session worksheet.

!!! warning "Unsanctioning has real-world impact"
    Unsanctioning can block end-user traffic enterprise-wide. Coordinate with the security operations team and change-management board before unsanctioning any app with non-trivial user count. For low-confidence findings, use **Monitored** status first and pivot to **Unsanctioned** only after confirmation.

### 8.4 Shadow-agent reconciliation artifact

Produce a reconciliation artifact each session:

| Column | Source |
|--------|--------|
| App name | Defender cloud app catalog |
| Users | Defender |
| Last seen | Defender |
| Registry match | Control 1.2 registry lookup |
| Disposition | Onboard / Unsanction / Monitor |
| Approver | AI Governance Lead UPN |
| Ticket ID | ITSM |

!!! example "Examiner Evidence Box — Shadow-agent discovery"
    1. Filtered Cloud App Catalog CSV (hashed).
    2. Reconciliation artifact (CSV or PDF) with dispositions and approver.
    3. Screenshots of each **Tag as Unsanctioned** action with justification visible.
    4. Onboarding tickets for any legitimate-but-unregistered agents.

!!! tip "Cross-Reference"
    The authoritative agent inventory is maintained by [Control 1.2](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md). Shadow-agent findings that disposition to **Onboard** must be driven into 1.2 within the 1.2-defined SLA.

## 9. Remediation Walkthrough — Four-Step Ordering

Detection without remediation is not a control. Control 3.6 mandates the **four-step remediation ordering** below. Steps must be executed in order; skipping or re-sequencing breaks the audit trail and may produce inconsistent state across surfaces.

### 9.1 Step 1 — Agent 365 inline Assign Owner (preferred)

The Agent 365 Ownerless card's **inline Assign Owner** action (§2.3) is the **default** remediation surface because it:

- Updates the agent's surfaced ownership atomically.
- Decrements the Ownerless card delta in a verifiable way.
- Captures justification text directly into Agent 365 telemetry, which feeds Purview audit.

Use Step 1 for **every** agent that surfaces in the Ownerless card and has a known replacement owner. Only escalate to Steps 2–4 when Step 1 cannot complete (e.g., the agent does not appear in the card during sovereign rollout lag, or the replacement owner requires a sponsor / manager confirmation upstream).

### 9.2 Step 2 — Confirm or override 2.26 sponsor manager-transfer

If the orphan was triggered by a sponsor leaver, the 2.26 Lifecycle Workflow may have already transferred sponsorship to the leaver's manager. Confirm via §3.3 and:

- **Accept the transfer** if appropriate (capture confirmation in the session worksheet).
- **Override** via §3.4 if the manager is not a valid sponsor (e.g., manager also disabled, or Zone 3 clearance gap).

Step 2 is **always** executed when the trigger is a sponsor-leaver event, even if Step 1 also succeeded — the two steps update different fields (Agent 365 owner vs. registry sponsor) and both must be consistent.

### 9.3 Step 3 — PPAC / Copilot Studio maker reassignment

If the orphan involves a Power Platform maker or environment owner (§4 / §5), execute the PPAC reassignment per those sections. Specifically:

1. Add the replacement as **Co-owner** first.
2. Remove the disabled principal in a separate action.
3. For Copilot Studio agents, also open the agent in **Copilot Studio (make.powerautomate.com / copilotstudio.microsoft.com)** and confirm the **Authentication** and **Channels** configuration still references active credentials. A disabled maker may have authored the auth principal; if so, rotate per the Pillar 1 credential controls.

Step 3 is required whenever a PPAC sweep produced a finding **even if** Step 1 also succeeded for the same agent — Agent 365 owner is presentation-layer; PPAC owner is authorization-layer.

### 9.4 Step 4 — Bulk Graph / PowerShell

When the volume of findings exceeds a practical portal-driven session (typically > 25 agents in a single sweep), pivot to bulk remediation via:

- **Microsoft Graph PowerShell SDK** for Entra-side service-principal and managed-identity reassignment.
- **Power Platform admin PowerShell** (`Microsoft.PowerApps.Administration.PowerShell`) for bulk maker / environment reassignment.
- **CLI for Microsoft 365** for SharePoint Copilot agent author updates.

Bulk procedures are documented in [powershell-setup.md](./powershell-setup.md). Bulk runs **must** be:

1. Pre-approved by the AI Governance Lead.
2. Logged via PowerShell transcript (`Start-Transcript`).
3. Validated post-run by re-checking the Ownerless card in the next refresh cycle.

### 9.5 Remediation ordering decision tree

| Trigger | Step 1 | Step 2 | Step 3 | Step 4 |
|---------|--------|--------|--------|--------|
| Single agent in Ownerless card, owner-only change | ✅ | — | — | — |
| Sponsor leaver (one or few agents) | ✅ | ✅ | — | — |
| Maker leaver (one or few agents) | ✅ | — | ✅ | — |
| Environment-owner leaver | ✅ where surfaced | — | ✅ | If many envs |
| Bulk leaver event (e.g., RIF, divestiture) | — | ✅ at registry layer | — | ✅ |
| Shadow agent disposition = Onboard | Onboard via 1.2, then ✅ once registered | — | — | — |

!!! example "Examiner Evidence Box — Remediation"
    For each remediated agent:

    1. Pre-state screenshot (per signal section).
    2. Justification text (capture from the Assign Owner dialog or PowerShell transcript).
    3. Post-state screenshot showing new owner and absence from Ownerless card.
    4. ITSM ticket linkage and approver record.
    5. Time-to-remediation timestamp (for SLA tracking, see §10).

## 10. Evidence Capture, Zone Cadence, and Examiner Packet

A Control 3.6 session produces a standardized evidence packet regardless of which signal surfaced the orphan. This section defines the packet contents, retention, and cadence expectations.

### 10.1 Per-session evidence packet

| Artifact | Source | Format | Retention |
|----------|--------|--------|-----------|
| Session worksheet | AI Governance Lead | PDF (signed) | 6 years WORM (Purview) |
| Role-elevation record | Entra PIM | CSV | 6 years |
| Signal-blade screenshots | Each portal § | PNG | 6 years |
| CSV exports with SHA-256 hash | Each portal § | CSV + TXT | 6 years |
| Remediation pre / post screenshots | §9 | PNG | 6 years |
| Defender for Cloud Apps reconciliation artifact | §8 | CSV / PDF | 6 years |
| Sovereign reconciliation worksheet (if applicable) | §1 | PDF (dual-signed) | 6 years |
| ITSM ticket linkage | ServiceNow / Jira / ADO | Text | 6 years |

All artifacts are stored in the Purview-backed evidence library with the retention label **`FSI-AgentGov-6yr-WORM`** (or the tenant-specific equivalent) to help meet SEC 17a-4(f) recordkeeping expectations. The 6-year window also supports FINRA Rule 4511 and OCC / Fed book-and-records expectations.

### 10.2 Zone cadence summary

| Zone | Detection cadence | Remediation SLA | Evidence cadence |
|------|-------------------|-----------------|------------------|
| Zone 3 (Enterprise) | Daily | 24 hours | Daily packet, weekly roll-up |
| Zone 2 (Team) | Weekly | 5 business days | Weekly packet, monthly roll-up |
| Zone 1 (Personal) | Monthly | 20 business days | Monthly packet, quarterly roll-up |

Cadence drift (e.g., a missed daily Z3 sweep) is itself an auditable event. Record drift in the session worksheet with root-cause analysis; repeated drift must escalate to the AI Governance Lead for control-effectiveness review.

### 10.3 Monthly and quarterly roll-up

Beyond per-session packets, Control 3.6 requires:

1. **Monthly roll-up (all zones)** — aggregate orphan counts, remediation SLA compliance, repeat-offender users, and shadow-agent disposition stats. Signed by AI Governance Lead.
2. **Quarterly attestation** — formal attestation that all Zone 3 findings in the quarter were remediated within SLA, signed by the AI Governance Lead and a named business-line control owner. Supports supervisory review under FINRA Rule 3110.
3. **Annual control-effectiveness review** — aggregate trend analysis, coverage-gap assessment (especially sovereign parity), and control-design refresh recommendations. Supports independent review expectations under OCC Bulletin 2011-12 / Fed SR 11-7.

### 10.4 KPIs

The following KPIs are produced by [verification-testing.md](./verification-testing.md) and surfaced to governance dashboards:

- **Mean time to remediation (MTTR)** by zone
- **SLA compliance rate** by zone (target ≥ 95% for Z3, ≥ 90% for Z2, ≥ 85% for Z1)
- **Orphan count trend** (week-over-week, month-over-month)
- **Shadow-agent disposition distribution** (Onboard / Unsanction / Monitor)
- **Ownerless card delta reconciliation rate** (card decrement matches remediation count)

!!! example "Examiner Evidence Box — Quarterly packet"
    When an examiner requests evidence, provide the following bundle:

    1. Quarter's signed session worksheets (index with dates and session IDs).
    2. Monthly roll-ups (three per quarter).
    3. Quarterly attestation PDF with dual signatures.
    4. KPI dashboard export for the quarter.
    5. List of any SLA breaches with root-cause analysis and remediation.
    6. Sovereign reconciliation worksheets, if applicable.

!!! tip "Cross-Reference"
    KPIs and long-window analytics are also surfaced via [Control 3.13](../../../controls/pillar-3-reporting/3.13-agent-365-admin-center-analytics.md). Align the Control 3.6 KPI definitions with the 3.13 dashboard definitions to avoid evidence divergence.

## Closing Decision Matrix — Portal vs PowerShell vs Graph

Use the matrix to choose the right execution surface for a given Control 3.6 task.

| Task | Portal (this walkthrough) | PowerShell ([powershell-setup.md](./powershell-setup.md)) | Graph API ([powershell-setup.md](./powershell-setup.md)) |
|------|---------------------------|---------------------------|---------------------|
| Daily Z3 Ownerless card review | ✅ Preferred | — | — |
| Weekly Z2 Ownerless card review | ✅ Preferred | Optional for KPI export | — |
| Monthly Z1 sweep | ✅ for review; bulk export via PS | ✅ for export | — |
| Single-agent Assign Owner | ✅ Preferred | — | — |
| Bulk reassignment (> 25 agents) | — | ✅ Preferred | ✅ for tenant-wide directory updates |
| Lifecycle Workflow run history review | ✅ for visual triage | ✅ for export | ✅ via Graph runs endpoint |
| Sovereign quarterly reconciliation worksheet | Manual (per §1) | ✅ for input exports | ✅ for input exports |
| Shadow-agent catalog review | ✅ Preferred | — | ✅ for catalog export |
| Recycle bin audit | ✅ Required | — | — |
| KPI publication to governance dashboard | — | ✅ | ✅ |

### Final readiness checklist

Before declaring a Control 3.6 session complete, confirm **every** item:

- [ ] Pre-flight gates passed (§0.4)
- [ ] Sovereign worksheet executed if applicable (§1)
- [ ] Ownerless card reviewed for the in-scope zone(s) (§2)
- [ ] Lifecycle Workflow run history reviewed (§3)
- [ ] PPAC maker sweep executed (§4)
- [ ] PPAC environment-owner sweep executed (§5)
- [ ] SharePoint Copilot author sweep executed (§6)
- [ ] PPAC recycle bin audit executed (§7)
- [ ] Defender for Cloud Apps shadow-agent sweep executed (§8)
- [ ] Remediations executed in the four-step ordering (§9)
- [ ] Per-session evidence packet assembled and stored in Purview (§10.1)
- [ ] Cadence drift, if any, documented with root-cause analysis (§10.2)
- [ ] Session worksheet signed and ITSM ticket closed
- [ ] Findings beyond session scope routed to siblings ([powershell-setup.md](./powershell-setup.md), [verification-testing.md](./verification-testing.md), [troubleshooting.md](./troubleshooting.md)) or upstream controls ([1.2](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md), [2.25](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md), [2.26](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md), [3.13](../../../controls/pillar-3-reporting/3.13-agent-365-admin-center-analytics.md))

A session that fails to satisfy any checklist item is **incomplete**; do not file the evidence packet until every box is ticked or a documented exception is approved by the AI Governance Lead.

---

*Updated: April 2026 | Version: v1.4.0 | UI Verification Status: Current*
