# Control 3.7: PPAC Security Posture Assessment — Portal Walkthrough

> Step-by-step Power Platform Admin Center (PPAC) configuration for [Control 3.7](../../../controls/pillar-3-reporting/3.7-ppac-security-posture-assessment.md). Audience: M365 administrators in US financial services.

---

## Prerequisites

- [ ] **Power Platform Admin** role (canonical name; see [role-catalog.md](../../../reference/role-catalog.md)). Environment Admins can view their owned environments only.
- [ ] **Entra Security Admin** role for Defender XDR cross-reference (optional, used in Step 8)
- [ ] **Tenant-level analytics enabled** (mandatory prerequisite for the security score and most recommendations) — see [How do I turn on tenant-level analytics?](https://learn.microsoft.com/en-us/power-platform/admin/tenant-level-analytics)
- [ ] Up to **24 hours** elapsed since enabling analytics, otherwise the Security > Overview page displays "Calculating security score"
- [ ] Approved **change ticket** (CAB) if any inline remediation will be performed; capture before/after screenshots for SOX 404 evidence

!!! warning "Sovereign cloud reminder"
    If your tenant is in GCC, GCC High, or DoD, sign in to the sovereign-specific PPAC URL. Recommendations and score behaviour are equivalent, but feature rollout dates may lag commercial. Verify against [Power Platform US Government plans](https://learn.microsoft.com/en-us/power-platform/admin/microsoft-dynamics-365-government).

---

## Step 1 — Open the PPAC Security area

**Portal path:** `Power Platform Admin Center > Security`

1. Sign in to [admin.powerplatform.microsoft.com](https://admin.powerplatform.microsoft.com).
2. In the left navigation, select **Security**.
3. The Security node expands into four pages: **Overview**, **Data protection and privacy**, **Identity and access management**, and **Compliance**.

> **UI note (April 2026):** The current PPAC Security UI is organized as four navigation pages, not as tabs. Older internal documentation referring to "Overview / Health / Monitor / Controls" tabs is out of date — the equivalent capabilities are now spread across the Security pages plus the **Actions** page (formerly Power Platform Advisor).

---

## Step 2 — Review the Security Score on Overview

**Portal path:** `PPAC > Security > Overview`

1. Read the **Security score** card at the top. Confirm it shows a percentage and a qualitative label (Low / Medium / High).
2. If it shows "Calculating security score," verify tenant-level analytics is on and wait up to 24 hours.
3. Capture a screenshot for the monthly posture record. Note that the score is **Preview** functionality — Microsoft has stated they are not investing in further changes to the preview implementation. Treat the score as a **directional indicator only**; supervisory evidence should rest on the underlying recommendations and configuration.
4. Record the score, the date, and the **Total possible score** in your posture log. The denominator can change as Microsoft adds scored features, so a score change in isolation is not necessarily configuration drift.

| Score Range | Label | Suggested FSI Response |
|-------------|-------|------------------------|
| 0–50 | Low | Treat as elevated risk; remediate High-severity items immediately |
| 51–80 | Medium | Schedule remediation within zone-aligned SLA |
| 81–100 | High | Maintain; investigate any score regression |

---

## Step 3 — Review and triage recommendations on the Actions page

**Portal path:** `PPAC > Actions` (also surfaced contextually in `PPAC > Security > Overview`)

1. Select **Actions** in the left navigation.
2. Open the **Recommendations** tab. Review each item; note **Severity** (High / Medium / Low), **Refresh frequency**, and whether **Managed Environments only** applies.
3. For each recommendation expand the side panel to read **Why is this important**, **What can I do**, **Instructions**, and **Affected Resources**.
4. Decide an action per recommendation:
    - **Remediate** via inline action (Managed Environments only) or by following the linked Settings page.
    - **Snooze** — non-security recommendations only, up to two months. Document the business reason.
    - **Dismiss** — security recommendations only, when not applicable. Requires a documented justification under FINRA 3110 supervisory procedures and SOX 404 IT general controls; revisit during the next quarterly review.
5. Use the **Action history** tab to confirm completion and to produce evidence of remediation activity.

!!! warning "Inline actions require Managed Environments"
    Inline remediation is only available on Managed Environments. Non-Managed Environments display a summary banner with a lock icon — convert to Managed via PPAC, or apply the change manually through the environment Settings page. After conversion, allow up to **72 hours** for full affected-resource detail to appear on the Actions page.

---

## Step 4 — Review Data Protection and Privacy posture

**Portal path:** `PPAC > Security > Data protection and privacy`

Validate the following are configured per zone:

| Setting | Zone 1 | Zone 2 | Zone 3 |
|---------|--------|--------|--------|
| Tenant-level DLP policy | Recommended | Required | Required |
| IP firewall | Optional | Recommended | Required |
| Customer Lockbox | Optional | Recommended | Required (where supported) |
| Customer-managed key (CMK) | Optional | Optional | Recommended |
| Azure Virtual Network | Optional | Recommended | Required for sensitive data |

For each Zone 2/3 environment, capture a screenshot of the configured state and archive with the monthly evidence pack (see [PowerShell setup](powershell-setup.md) for SHA-256 emission).

---

## Step 5 — Review Identity and Access Management posture

**Portal path:** `PPAC > Security > Identity and access management`

1. Verify **Tenant isolation** is on at the tenant level.
2. For each environment confirm:
    - **Security group** assigned (required for Zone 2/3).
    - **Restricted guest access** turned on.
    - **Administrator privileges** — fewer than 10 admins where practical; document exceptions per FINRA Rule 3110 supervisory procedures.
    - **Client application access control** configured wherever auditing is on.
    - **IP address-based cookie binding** configured for Zone 3 environments holding non-public personal information (NPI) under GLBA 501(b).

---

## Step 6 — Review Compliance posture

**Portal path:** `PPAC > Security > Compliance`

1. Confirm **Dataverse auditing** is enabled per environment with retention aligned to [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) (≥ 180 days; SEC 17a-4(f) and FINRA 4511 retention obligations may extend this).
2. Confirm in-scope environments are converted to **Managed Environments** ([Control 2.1](../../../controls/pillar-2-management/2.1-managed-environments.md)).
3. Cross-reference the Actions page for any unresolved Compliance-category recommendations.

---

## Step 7 — Verify per-environment privacy and security settings

**Portal path:** `PPAC > Environments > [Environment] > Settings > Privacy + Security`

Some hardening settings are **not** surfaced as PPAC recommendations and must be reviewed manually per environment:

1. **Blocked attachments** — confirm the dangerous-extension list is populated. Minimum recommended: `ade;adp;app;asa;asp;bat;cdx;cmd;com;cpl;crt;csh;dll;exe;hta;inf;ins;jar;js;jse;lnk;mda;mdb;mde;msc;msi;msp;mst;pcd;pif;reg;scr;sct;shb;shs;tmp;url;vb;vbe;vbs;ws;wsc;wsf;wsh`.
2. **Blocked MIME types** — minimum: `application/javascript`, `application/x-javascript`, `text/javascript`, `application/hta`, `application/msaccess`, `text/scriplet`, `application/xml`, `application/prg`.
3. **Inactivity timeout** — enabled, ≤ 120 minutes (Zone 3: ≤ 60 minutes).
4. **Session expiration** — "Set custom session timeout" enabled, ≤ 1440 minutes (Zone 3: ≤ 720 minutes).
5. **Content security policy** — under **Model Driven**, "Enforce content security policy" enabled.

Repeat for every Zone 2 and Zone 3 environment. Capture screenshots and archive.

!!! note "These settings are per-environment"
    PPAC Security recommendations do not flag these items today. Drift here is invisible to the security score and must be detected through the Configuration Hardening Baseline review or the PowerShell collector ([powershell setup](powershell-setup.md)).

---

## Step 8 — Cross-reference Defender for Cloud Apps (optional, recommended for Zone 3)

!!! danger "License deadline: 2026-07-01 — Agent 365 required for AI Agent Inventory"
    Defender for Cloud Apps AI Agent Inventory access requires **Agent 365** after 2026-07-01. Until 2026-07-01, Defender for Cloud Apps license alone provides access (grace period). After 2026-07-01, organizations without Agent 365 **lose AI Agent Inventory visibility entirely**. Source: [AI agent inventory](https://learn.microsoft.com/en-us/defender-cloud-apps/ai-agent-inventory)

For Zone 3 / customer-facing agents, correlate PPAC posture with Microsoft Defender:

1. Open the **Microsoft Defender** portal as Entra Security Admin.
2. Navigate to **Cloud apps > AI agent inventory** (preview where available).
3. Confirm Power Platform connector is enabled and AI agents are enumerated.
4. Review **Attack path analysis** for any path involving an agent identity that intersects with NPI (GLBA 501(b)) or covered records (SEC 17a-4).
5. Document findings in the same posture report as the PPAC review.

See [Microsoft Learn: AI agent inventory (Defender for Cloud Apps)](https://learn.microsoft.com/en-us/defender-cloud-apps/ai-agent-inventory).

---

## Step 9 — Generate the periodic posture report

Produce a report containing:

| Section | Content |
|---------|---------|
| Executive summary | Score, label, delta vs prior period, attestation by Power Platform Admin |
| Recommendations summary | Counts by severity (High/Medium/Low) and status (open/snoozed/dismissed/completed) |
| Dismissed recommendations log | Item, business justification, approver, review-by date |
| Per-environment hardening (Step 7) | Pass/Fail per environment, Zone, evidence reference |
| Defender cross-reference (Step 8) | Findings summary, escalations |
| Action history | Items completed since last report, with timestamps |

Run the [PowerShell setup](powershell-setup.md) `New-Control37PostureReport` cmdlet to automate report assembly with SHA-256 evidence emission.

---

## Step 10 — Configuration hardening baseline review

For comprehensive cross-control drift detection (consolidating PPAC-detectable settings with manually-verified items across Controls 1.1, 1.7, 1.18, 1.27, 2.1, 2.22, and 3.7), see [Configuration Hardening Baseline](../../advanced-implementations/configuration-hardening-baseline/index.md).

Cadence:

| Zone | Hardening Baseline Cadence | Posture Report Cadence |
|------|---------------------------|------------------------|
| Zone 1 | Monthly | Quarterly |
| Zone 2 | Bi-weekly | Monthly |
| Zone 3 | Weekly | Monthly + ad-hoc on score regression |

---

## FSI-Specific Considerations

- **Score is not a control objective.** Auditors will ask for the underlying configuration evidence and the dismissed-recommendations log, not the headline percentage.
- **Document score-model changes.** If the **Total possible score** changes between reports, note the date and source (Microsoft release notes) so reviewers can distinguish a model change from configuration drift.
- **Snooze and dismiss are auditable events.** Treat each as a control exception requiring written justification and a review-by date.
- **Sovereign cloud lag.** Some recommendations roll out to GCC / GCC High / DoD on a delayed schedule. Confirm parity in your tenant before treating an absent recommendation as compliant.

---

## Related Playbooks

- [PowerShell Setup](powershell-setup.md) — collection, scoring, evidence emission
- [Verification & Testing](verification-testing.md) — test cases and audit evidence
- [Troubleshooting](troubleshooting.md) — common issues

[Back to Control 3.7](../../../controls/pillar-3-reporting/3.7-ppac-security-posture-assessment.md)

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
