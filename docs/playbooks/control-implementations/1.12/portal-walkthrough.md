# Control 1.12 — Portal Walkthrough: Insider Risk Management

**Control:** [1.12 Insider Risk Detection and Response](../../../controls/pillar-1-security/1.12-insider-risk-detection-and-response.md)
**Audience:** M365 administrator (US financial services)
**Last UI Verified:** April 2026
**Cloud coverage:** Commercial · GCC · GCC High · DoD (see sovereign cloud table — **HARD GAPS exist for FSI Government-cloud tenants**)
**Estimated Time:** 8–16 hours (excludes analytics processing windows of up to 48 hours, HR connector first-ingest cycle, and pilot validation)

> This playbook provides portal configuration guidance for [Control 1.12](../../../controls/pillar-1-security/1.12-insider-risk-detection-and-response.md). It is written to support compliance with FINRA Rule 3110 (supervision), FINRA 25-07 (AI agent supervision), GLBA 501(b) (safeguards), SOX 404 (internal controls), SEC Rule 17a-4 (record retention — see boundary note), OCC Bulletin 2011-12, Federal Reserve SR 11-7, and NYDFS 23 NYCRR 500 §500.17(a). Insider Risk Management (IRM) is a **detect / investigate / act** surface. By itself it does not satisfy any single regulatory obligation — durable records retention is implemented separately under [Control 1.9](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md), and incident handling is governed by your firm's Written Supervisory Procedures (WSP) and the FSI Incident Handling section of the Control 1.12 troubleshooting playbook.

---

!!! danger "READ FIRST — Sovereign cloud HARD GAP for US Government clouds"
    Microsoft Purview Insider Risk Management — and in particular **Adaptive Protection**, **Forensic Evidence**, and several browser-derived templates (**Risky AI usage**, **Risky browser usage**) — has **limited or no availability** in **US Government cloud programs (GCC, GCC High, DoD)** per current Microsoft Learn (`insider-risk-management-adaptive-protection`, `insider-risk-management-forensic-evidence`, `insider-risk-management-browser-support`). This is a **HARD BLOCKER** for FSI tenants in those clouds.

    Before you start work in this playbook:

    1. Confirm your tenant's cloud against the **Sovereign Cloud Availability** table below
    2. For any capability marked **Limited / Not at parity / Not available**, **do not assume it will appear in the portal** even if you have the right license
    3. Document each gap as a control exception in your governance register and apply the **compensating controls** listed in the table
    4. Re-verify every cell against Microsoft Learn at the time of deployment — Government-cloud parity changes by service update

---

!!! warning "Read the boundary before you begin"
    Insider Risk Management **scores user activity** for risky patterns, opens **alerts** and **cases**, and (where in scope) drives **Adaptive Protection** to raise DLP / Data Lifecycle Management / Conditional Access posture. It is **not** a records-retention vault, **not** a communications supervision queue, and **not** a substitute for DLP enforcement.

    | If you need to … | Use … |
    |---|---|
    | Retain alert / case / Forensic Evidence artifacts under WORM beyond their working lifecycle | Records retention — [Control 1.9](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md). **Forensic Evidence clips auto-delete 120 days after capture unless exported.** |
    | Supervise emails, Teams chats, Viva Engage, Copilot interactions for content violations | Communication Compliance — [Control 1.10](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md) |
    | Block content from being sent or shared with AI | DLP — [Control 1.5](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) |
    | Place a legal hold over a user's mailbox / OneDrive / Teams | eDiscovery (Premium) — [Control 1.19](../../../controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md) |
    | See AI app inventory, sensitive prompts, and unprotected sources | DSPM for AI — [Control 1.6](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md) |

    IRM cases, alerts, and Forensic Evidence clips are **working investigative artifacts**, not books-and-records under SEC 17a-4(f) / FINRA 4511. Promote any artifact that must be retained beyond the IRM working lifecycle (and **before** Forensic Evidence's 120-day clip expiry) to retention policies / records management ([Control 1.9](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md)) or eDiscovery (Premium).

---

## Sovereign Cloud Availability

| Cloud | Portal URL | IRM core (policies, alerts, cases) | Risky AI usage | Risky Agents (default) | Risky browser usage (preview) | Forensic Evidence | Adaptive Protection | Triage Agent |
|---|---|---|---|---|---|---|---|---|
| Commercial | `https://purview.microsoft.com` | GA | GA (browser ext.) | Applied by default | Preview (verify lifecycle on Learn) | Opt-in (PAYG) | GA | Verify lifecycle on Learn |
| GCC | `https://purview.microsoft.com` | GA | Verify per Microsoft 365 roadmap | Verify on Learn at deployment | Verify per roadmap | Verify per roadmap | Verify per roadmap | Verify per roadmap |
| GCC High | `https://purview.microsoft.us` | Limited — verify on Learn at deployment | **Not at parity — verify on Learn** | Verify on Learn at deployment | **Likely unavailable — verify on Learn** | **Not at parity — verify on Learn** | **Not at parity — verify on Learn** | **Likely unavailable — verify on Learn** |
| DoD | `https://purview.microsoft.us` (DoD instance) | Limited — verify on Learn at deployment | **Not at parity — verify on Learn** | Verify on Learn at deployment | **Likely unavailable — verify on Learn** | **Not at parity — verify on Learn** | **Not at parity — verify on Learn** | **Likely unavailable — verify on Learn** |

> Verify every cell against Microsoft Learn (`insider-risk-management`, `insider-risk-management-adaptive-protection`, `insider-risk-management-forensic-evidence`, `insider-risk-management-browser-support`) at deployment time. Government-cloud parity is the most volatile dimension of this control.

### Compensating controls when an IRM capability is unavailable

| Unavailable capability | Compensating control(s) |
|---|---|
| IRM core (no IRM at all in this cloud) | Communication Compliance ([Control 1.10](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md)) for content-based supervision; DLP ([Control 1.5](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md)) for blocking; comprehensive Audit logging ([Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md)); Microsoft Defender for Cloud Apps anomaly detection; Microsoft Sentinel UEBA |
| Risky AI usage / Risky browser usage | DSPM for AI ([Control 1.6](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md)); DLP for AI prompts ([Control 1.5](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md)); Communication Compliance Copilot interactions template ([Control 1.10](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md)) |
| Risky Agents (default policy unavailable) | DSPM for AI ([Control 1.6](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md)); agent inventory and runtime audit ([Control 3.1](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md)); Audit ([Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md)) for Copilot Studio / Foundry agent operations |
| Forensic Evidence | Endpoint DLP audit trails ([Control 1.5](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md)); Defender for Endpoint timeline; Microsoft Sentinel; HR / Legal interview-driven evidence |
| Adaptive Protection | Static DLP, Conditional Access, and Data Lifecycle Management policies tuned to the highest-risk population (lose dynamism); manual case-driven elevation by IRM Investigators |
| Triage Agent | Manual triage by Insider Risk Management Analysts; severity-based queue filters in the standard alerts dashboard |

Document the gap, compensating control, and review cadence in your Zone-3 exception register.

---

For PowerShell parity see `docs/playbooks/_shared/powershell-baseline.md`. **Note:** PowerShell support for IRM is intentionally narrow — IRM **policies, role-group assignment, settings, priority user groups, and Forensic Evidence** are configured **portal-only**. PowerShell is used here only for prerequisites (audit log, license inventory, Defender for Endpoint state, HR connector orchestration) and validation (audit search, evidence collection).

---

## Prerequisites

Complete every item in this section **before** opening the IRM policy wizard. Most "I created the policy and nothing happens" problems trace back to a missed prerequisite.

### 1. License entitlement

Per current Microsoft Learn, IRM core capability requires one of:

- **Microsoft 365 E5** (or Office 365 E5 + Microsoft 365 E5 Compliance)
- **Microsoft 365 E5 Compliance** add-on
- **Microsoft 365 E5 Insider Risk Management** standalone add-on
- **Microsoft Purview Suite** per-user license

Per-user licensing is **required for every monitored user** (every user whose activity is scored), not just for administrators or investigators. Specific capabilities require additional billing:

| Capability | Additional billing requirement |
|---|---|
| Forensic Evidence | **Pay-as-you-go (PAYG)** linked to an Azure subscription (organizational storage trial available — verify current trial size on Microsoft Learn at deployment) |
| Selected detection indicators flagged "PAYG" in Settings → Policy indicators | **PAYG** linked to an Azure subscription |
| Triage Agent | Verify capacity / consumption prerequisites on Microsoft Learn at deployment (subject to change) |

Verify entitlement against the [current Microsoft 365 service description](https://learn.microsoft.com/en-us/office365/servicedescriptions/microsoft-365-service-descriptions/microsoft-365-tenantlevel-services-licensing-guidance) before each material change window — Microsoft licensing for compliance products has changed multiple times. Capture a license-inventory snapshot in your evidence pack.

### 2. Enable the Unified Audit Log

IRM policies and analytics scans **require** the Unified Audit Log (UAL). If UAL is off, policies appear to create successfully but produce no signal and no scoring — a silent supervisory-system gap and the **most common silent-failure mode** for this control.

UAL has been on by default in all new Microsoft 365 tenants since 2023, but verify state explicitly. Detect first; only mutate if disabled.

**Detect from Exchange Online PowerShell** (sovereign endpoints listed below):

```powershell
# Run from Windows PowerShell 5.1 or PowerShell 7 with ExchangeOnlineManagement
# pinned per docs/playbooks/_shared/powershell-baseline.md §1
Import-Module ExchangeOnlineManagement

# Commercial / GCC
Connect-ExchangeOnline

# GCC High
# Connect-ExchangeOnline -ExchangeEnvironmentName O365USGovGCCHigh

# DoD
# Connect-ExchangeOnline -ExchangeEnvironmentName O365USGovDoD

(Get-AdminAuditLogConfig).UnifiedAuditLogIngestionEnabled
```

A return value of `True` is required. The same property surfaced through Security & Compliance PowerShell (IPPS) is unreliable — always read it from Exchange Online PowerShell.

**If `False`, enable from a holder of an Exchange role group** (Organization Management, Compliance Management, or Records Management):

```powershell
Set-AdminAuditLogConfig -UnifiedAuditLogIngestionEnabled $true
```

**Or from the portal:** Microsoft Defender portal → **Audit** → **Start recording user and admin activity**.

> **Government-cloud reminder:** if your tenant is in a Government cloud where IRM is not at parity (see Sovereign Cloud Availability), enabling UAL alone will not unlock IRM — verify capability availability **before** enabling and configuring policies.

After enabling, allow up to several hours for ingestion to complete. Record the change in your CAB ticket and capture the `Get-AdminAuditLogConfig` JSON output as evidence.

### 3. Pseudonymization (privacy default — verify on)

Usernames are **pseudonymized by default** in the IRM Alerts, Cases, Activity Explorer, and Triage surfaces. This is a privacy-by-design baseline that supports GLBA 501(b) safeguards and aligns with state employee-monitoring expectations (CT, DE, NY) and EU works-council requirements where in scope.

- Preserve the default unless your privacy framework documents a justification for re-identification
- Re-identification is a **privileged action** that emits an audit-trail entry; the **Insider Risk Management Auditors** role group is responsible for periodic review of unmask events
- Verification step is in **Step 1** below

### 4. Microsoft 365 HR connector (required for departing-user scenarios)

The **Microsoft 365 HR connector** (CSV upload + scheduled ingestion) — **not** a generic Logic App / API — feeds termination, resignation, and performance-review signals into IRM. It is required for:

- *Data theft by departing users* (uses HR-supplied resignation/last-working-date to scope scoring)
- *Data leaks by risky users* (PIP / performance-improvement signals)
- *General security policy violations* — departing-users variant
- Any policy that uses the **Resignation date** or **Last working date** as the triggering event

**Required CSV fields (minimum, per Microsoft Learn `import-hr-data`):**

| Field | Purpose |
|---|---|
| `EmployeeID` | Source-of-truth employee identifier from HRIS |
| `UserPrincipalName` | Maps the HRIS employee to the Entra identity |
| `ResignationDate` | Triggers the departing-user scoring window |
| `LastWorkingDate` | Closes the scoring window |

Optional fields support performance reviews, role / job-level changes, and personal data (used by *Risky users* templates). Refer to [Import HR data](https://learn.microsoft.com/en-us/purview/import-hr-data) for the full schema.

Configure the connector under **Microsoft Purview portal → Settings (gear icon, upper-right) → Data connectors → HR data → Add connector**, then schedule the CSV ingest job (HRIS export → SFTP / blob → connector). The Microsoft 365 HR connector is a separate Microsoft Entra app registration; capture the application ID and the schedule cadence in evidence.

> **Silent-failure trap:** if the HR connector is configured but the CSV is empty or the date format is wrong (the connector expects ISO 8601 `YYYY-MM-DD`), the departing-user policy will **score nobody**. Validate with a known synthetic resignation row before relying on the connector.

### 5. Microsoft Defender for Endpoint integration (required for security-violation templates)

Per Microsoft Learn, the *General security policy violations* templates (and the priority-/departing-/risky-user variants) tie to **Microsoft Defender for Endpoint (MDE)** alerts — security control evasion, unwanted software installation, and MDE-detected suspicious behaviors. **Failed authentication attempts and risky sign-ins are Entra ID Protection signals, not MDE — do not assume IRM consumes them under this template.**

Prerequisites:

- Devices in scope are onboarded to MDE (or to standalone Microsoft Purview device onboarding where the indicator supports it)
- MDE → Microsoft Purview integration is enabled (Microsoft Defender XDR settings → **Endpoints** → **Advanced features** → enable Microsoft Purview integration where exposed)
- The MDE-derived indicators are enabled in **Settings → Policy indicators** (Step 3 below)

Without MDE, the *General security policy violations* template can be created but will produce no alerts.

### 6. Microsoft Defender for Cloud Apps connectors (required for departing-user cloud-app coverage)

The *Data theft by departing users* template is **a single template**. Cloud-app coverage (Box, Dropbox, Google Drive, Amazon S3, Azure) is supplied by **Microsoft Defender for Cloud Apps** app connectors — not by separate IRM templates.

For departing-user scoring against non-Microsoft 365 cloud storage:

1. Configure the corresponding **Defender for Cloud Apps** app connector (Box, Dropbox, Google Drive, Amazon S3, Azure)
2. Confirm activity flows into the Defender for Cloud Apps activity log
3. Enable the corresponding cloud-storage indicators in IRM **Settings → Policy indicators**

If your firm uses none of these cloud apps (a common posture for FSI under acceptable-use policy), document the exclusion explicitly — reviewers should not be left wondering why the cloud-app indicators are off.

### 7. Browser signal source (required for Risky AI usage / Risky browser usage / browser-derived indicators)

Per Microsoft Learn `insider-risk-management-browser-support`:

| Browser | Required extension |
|---|---|
| Microsoft Edge | **Microsoft Insider risk extension** (or the Microsoft Purview extension where indicated by Learn for the specific scenario) |
| Google Chrome | **Microsoft Purview extension** |
| Other browsers | **Not supported** |

Additional requirements:

- **Windows-only** (macOS / Linux / mobile not supported for IRM browser signals)
- Devices must be **onboarded to Microsoft Purview**
- Browsing indicators must be enabled in **Settings → Policy indicators → Browsing indicators** (Step 3 below)
- Push the extension via **Intune** (managed install) — do not rely on user-side installation in regulated populations

Without a configured browser extension on the user's device, *Risky AI usage* and *Risky browser usage* will produce no signal even when the policies are configured correctly.

### 8. DLP for Data leaks — High severity incident report requirement

When a Microsoft Purview DLP policy is the trigger source for the *Data leaks* (or *Data leaks by priority/risky users*) template, Microsoft Learn requires the upstream DLP policy to be configured for **High severity incident reports**. The IRM template consumes the High-severity DLP signal as a triggering event — Medium / Low severity DLP matches will not trigger scoring.

Validate this on your DLP policies before mapping them as IRM triggers. See [Control 1.5](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) for DLP configuration.

### 9. Forensic Evidence prerequisites (only if opting in)

Forensic Evidence is **off by default** and is **opt-in**. Skip this prerequisite if the firm's privacy / WSP posture excludes Forensic Evidence.

If opting in, all of the following must be in place:

- **Microsoft Purview Client** installed on the in-scope device
- **Windows 10 or Windows 11 Enterprise** (other editions / OS unsupported)
- Device is **onboarded to Microsoft Purview**
- **Pay-as-you-go (PAYG)** billing linked to an Azure subscription (organizational storage trial available — verify trial size on Learn)
- **Insider Risk Management Approvers** role group populated and **distinct** from Investigators (Step 2 below)
- **Privacy / Legal sign-off** on state-law notice posture (CT, DE, NY, and any other applicable jurisdictions; collective-bargaining notice if applicable)

> Captured Forensic Evidence clips are **automatically deleted 120 days after capture** unless exported to a long-term store. Forensic clips are **not records under SEC 17a-4(f) / FINRA 4511**. Promote any required retention to retention policies / records management ([Control 1.9](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md)) or eDiscovery (Premium) before the 120-day expiry.

### 10. Custom SITs, custom keyword dictionaries, sensitivity labels

If any IRM policy will reference custom Sensitive Information Types (SITs), custom keyword dictionaries, or sensitivity labels (in priority content), **create them first**:

- Custom SITs / dictionaries → [Control 1.13](../../../controls/pillar-1-security/1.13-sensitive-information-types-sits-and-pattern-recognition.md)
- Sensitivity labels → [Control 1.5](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md)

Referencing a non-existent SIT or label name is a silent-failure mode — the policy saves but never matches.

---

## Step 1 — Verify and document Pseudonymization (privacy default)

IRM is built **privacy-by-design**. Usernames are **pseudonymized by default** across the IRM workspace. This is a defensible baseline for FSI under GLBA 501(b) and several US state employee-monitoring laws.

> **Investigator unmasking is opt-in by an admin** and is auditable. Re-identification is a **privileged action**; the **Insider Risk Management Auditors** role group is responsible for periodic review of unmask events.

### Verify the default

1. Sign in to the [Microsoft Purview portal](https://purview.microsoft.com) (or the sovereign URL from the table above)
2. Open **Insider Risk Management**
3. Select the **Settings** gear (upper-right) → **Insider Risk Management** → **Privacy**
4. Confirm **Show anonymized versions of usernames** is **On** (the default)
5. Capture a timestamped screenshot for evidence

### Opt out (only with documented justification)

If your firm's policy requires non-pseudonymized review (rare; typically only for named investigations under HR/Legal direction):

1. On the **Privacy** page, clear the **Show anonymized versions of usernames** setting
2. Save
3. **Required evidence to commit to the change ticket:**
   - Admin who made the change (Entra UPN)
   - Business justification (Compliance / HR / Legal sign-off)
   - Effective date and expected duration
   - Population of users / investigators who will see non-pseudonymized identities
   - UAL row for the configuration change (search for the IRM settings update)
4. Re-enable pseudonymization at the documented end date

The opt-out is **a privileged action and must be auditable** — an undocumented opt-out is a privacy / SOX 404 finding. The Insider Risk Management Auditors role group should review unmask events on a documented cadence (monthly is a defensible baseline).

---

## Step 2 — Configure role groups (six canonical IRM role groups)

> **Portal navigation (verify before each session — it has changed):** Microsoft Purview portal → **Settings** (gear, upper-right) → **Roles & scopes** → **Permissions** → **Microsoft Purview solutions** → **Insider Risk Management** → **Role groups**.

### Canonical role group inventory

There are **six** Insider Risk Management role groups (per Microsoft Learn `insider-risk-management-permissions`). Use the canonical plural names exactly as they appear in the portal — synonyms ("IRM Admin", "IRM Investigator") will not match audit-log queries and will produce false-clean evidence.

| Role group (canonical name) | Configure policies, settings, role groups, priority groups, indicators | Triage and review alerts (no content view) | Investigate cases / view content (subject to pseudonymization) | Submit Forensic Evidence capture requests | **Approve** Forensic Evidence capture requests | View IRM audit logs (admin actions, settings changes, unmask events) |
|---|---|---|---|---|---|---|
| **Insider Risk Management** (catch-all) | Yes | Yes | Yes | Yes | No (Approver role group is required for approval) | Limited |
| **Insider Risk Management Admins** | Yes | No | No | No | No | No |
| **Insider Risk Management Analysts** | No | Yes | No | No | No | No |
| **Insider Risk Management Investigators** | No | Yes | Yes | Yes | No | No |
| **Insider Risk Management Auditors** | No | No | No | No | No | Yes |
| **Insider Risk Management Approvers** | No | No | No | No | **Yes (required for Forensic Evidence dual-auth)** | No |

> **Approvers must be distinct from Investigators.** Forensic Evidence uses a **dual-authorization** model: Investigator submits the capture request; Approver approves it. Assigning the same user to both role groups breaks dual-auth and is a control deficiency. Capture role-group membership monthly and on every change.

### Option 1 — Single catch-all assignment (small teams / pilot only)

1. Settings → **Roles & scopes** → **Permissions** → **Microsoft Purview solutions** → **Insider Risk Management** → **Role groups**
2. Select the **Insider Risk Management** role group → **Edit**
3. **Choose users** → select the users → **Select** → **Next**
4. **Save** → **Done**

Catch-all is acceptable only for very small teams or pilots. For Zone-3 (Enterprise) FSI deployments, **prefer Option 2**.

### Option 2 — Segmented assignment (recommended for FSI Zone 3)

Map your firm's compliance / Legal / Internal Audit roles to the six specific role groups. A typical FSI mapping:

| Firm role | Assigned to (role group) | Rationale |
|---|---|---|
| IRM Compliance Lead / WSP owner | Insider Risk Management Admins | Policy & settings authority; no alert content visibility (separation of duties) |
| Tier-1 supervisory analyst | Insider Risk Management Analysts | Triage and review alerts; no file/email content access |
| Senior Compliance investigator (FINRA-registered principal where applicable) | Insider Risk Management Investigators | Investigate cases, view content under pseudonymization, submit Forensic Evidence requests |
| Internal Audit / SOX assurance | Insider Risk Management Auditors | Independent review of admin actions, settings changes, and unmask events. **Must not** also be Admin or Investigator |
| Compliance / Privacy Approver (separate from Investigator team) | Insider Risk Management Approvers | Approve Forensic Evidence capture requests under dual-auth |

For each role group:

1. Settings → **Roles & scopes** → **Permissions** → **Microsoft Purview solutions** → **Insider Risk Management** → **Role groups**
2. Select the role group → **Edit**
3. **Choose users** → add users → **Select** → **Next** → **Save**
4. Repeat for the next role group → **Close** when done

> **Always maintain at least one user** in either the **Insider Risk Management** or **Insider Risk Management Admins** role group to avoid a "zero administrator" lockout if a leaver removes the only configured admin.

### Propagation note

After assignment, **role propagation can take up to 30 minutes** to apply across the organization. If a newly assigned user reports they cannot see the IRM menu, wait 30 minutes before troubleshooting.

### Avoid Global Admin

Holders of **Microsoft Entra Global Admin** or **Compliance Administrator** automatically inherit broad Purview permissions. Do **not** rely on Global Admin for routine IRM operations — minimize Global Admin holders per [Microsoft's least-privilege guidance](https://learn.microsoft.com/en-us/purview/purview-permissions). Assign workload-specific role groups instead.

### Administrative Units for IRM scoping (FSI subsidiary / LOB segregation)

For multi-LOB or multi-region firms (parent bank with broker-dealer, RIA, swap-dealer, and FCM affiliates; US broker-dealer with a German subsidiary; firms required to segregate Information Barriers populations from supervisory review), tenant-wide IRM administrator visibility is rarely defensible.

**Administrative Units (AUs)** scope IRM admin / analyst / investigator membership to specific user populations. Per Microsoft Learn, IRM supports AU scoping for the relevant role groups; verify the **exact** in-scope role groups and capabilities for AUs against Learn (`insider-risk-management-configure`) at the time of deployment as the matrix has been expanding.

Apply:

1. Create an Entra Administrative Unit per [Purview administrative units](https://learn.microsoft.com/en-us/purview/purview-admin-units) if it does not already exist (typically scoped to an Entra group representing the regulated population)
2. Assign the AU to the IRM role-group member(s) per the same Learn procedure
3. The assigned member becomes a **restricted administrator** — visibility is bounded to users inside the AU
4. Members **without** an AU assignment remain **unrestricted administrators** with full-tenant visibility. Document this distinction for each role-group member in your evidence pack

#### FSI mapping example

| Firm scope | AU (Entra group source) | Role-group member assigned to AU |
|---|---|---|
| US broker-dealer registered reps | `aug-bd-us-regreps` | US Compliance — Insider Risk Management Investigators |
| RIA affiliate (SEC IA) | `aug-ria-affiliate` | RIA Compliance — Insider Risk Management Investigators |
| Bank line-of-business | `aug-bank-lob` | Bank Compliance — Insider Risk Management Analysts |
| Swap dealer (CFTC) | `aug-cftc-swap-dealer` | CFTC Compliance — Insider Risk Management Analysts |
| EU subsidiary (works-council jurisdiction) | `aug-eu-subsidiary` | EU Compliance — Insider Risk Management Investigators (with stricter Forensic Evidence controls) |

---

## Step 3 — Configure IRM Settings (analytics, indicators, priority groups, intelligent detections)

> **Portal navigation:** Microsoft Purview portal → **Insider Risk Management** → **Settings** (gear, upper-right) → **Insider Risk Management**.
>
> Per Microsoft Learn `insider-risk-management-configure`, the IRM Settings surface includes (verify exact navigation labels at the time of deployment): **Privacy**, **Policy indicators**, **Policy timeframes**, **Intelligent detections**, **Export alerts**, **Priority user groups**, **Priority physical assets**, **Power Automate flows**, **Microsoft Teams**, **Analytics**, **Inline alert customization**, **Admin notifications**. **There is no "Investigation" settings page** — older guidance referencing such a page is incorrect for the current portal.

### 3.1 Analytics — enable the de-identified scan

Analytics provides a **de-identified, tenant-wide insider-risk scan** that surfaces potential risk patterns **before** any policy is created. It is the recommended starting point — use it to inform which policy templates the firm actually needs.

1. **Settings → Insider Risk Management → Analytics**
2. Toggle **Scan your tenant's user activity to identify potential insider risks** to **On**
3. Acknowledge the privacy notice (the scan is de-identified)
4. **Wait up to 48 hours** for the initial scan to complete (per Microsoft Learn — analytics scans may take up to 48 hours)
5. Return to the Analytics dashboard and capture screenshots of the scan results for evidence

> Analytics produces **insights**, not alerts. Use the insights to scope policy creation in Step 4.

### 3.2 Policy indicators — enable per-template signals

**Settings → Insider Risk Management → Policy indicators**

Policy indicators are the **per-signal toggles** consumed by the policy templates. A template lists the indicators it uses, but the **indicator must be enabled at the tenant level** before it produces signal. Common silent-failure mode: template created with indicators that are off at the tenant level.

Indicator categories (verify exact labels and PAYG markers on Learn at deployment):

| Category | Examples | Notes |
|---|---|---|
| **Office indicators** | SharePoint download, OneDrive download, Teams shared, email sent externally | Tenant-default; confirm enabled |
| **Device indicators** | USB copy, print, copy to network share, copy to clipboard for sensitive content | Requires device onboarding (Defender for Endpoint or standalone) |
| **Browsing indicators** | Risky browser usage, Risky AI prompts, downloads from risky sites | Requires the browser extension (Prerequisite #7); Windows-only |
| **Cloud-storage indicators** | Box / Dropbox / Google Drive / Amazon S3 / Azure file activity | Requires Defender for Cloud Apps app connectors (Prerequisite #6) |
| **Defender for Endpoint alerts** | Security control evasion, unwanted software install, MDE alert types | Requires MDE integration (Prerequisite #5) |
| **Healthcare / EHR indicators** | (HIPAA-specific) | Out of scope for FSI — leave off unless your firm has a healthcare line |
| **Risky AI usage indicators** | Risky prompts to Copilot / Copilot Chat / non-Microsoft AI | Requires browser extension (Edge / Chrome) and Windows |
| **Cumulative exfiltration detection** | Activity above an established baseline | Tunable thresholds |

For each category that maps to a template you intend to create:

1. Open the category
2. Enable the relevant indicators
3. Save
4. Capture a screenshot of the enabled-indicator state for evidence

> **Indicator variants flagged "PAYG":** require pay-as-you-go billing on a linked Azure subscription. Without PAYG, those indicators silently produce no signal.

### 3.3 Priority user groups — define and **scope visibility**

**Settings → Insider Risk Management → Priority user groups**

Priority user groups identify populations that warrant elevated scrutiny (trading desk, RIA staff, agent administrators, departing-user watchlists, executives with MNPI exposure). They are referenced by *Data leaks by priority users* and *General security policy violations — priority users* templates.

> **Critical Learn step (often missed):** when you create a priority user group, you must define **who can view** the group — either specific named users or specific IRM role groups. Without an explicit viewer assignment, the priority group exists but no IRM member can see its alerts. Define the viewer assignment at creation.

Procedure:

1. Settings → **Priority user groups** → **Create priority user group**
2. **Name** (use a stable, descriptive name; this name appears in templates): e.g.,
   - `pug-fsi-trading-desk`
   - `pug-fsi-ria-staff`
   - `pug-fsi-mna-team`
   - `pug-fsi-agent-admins`
   - `pug-fsi-departing-watchlist` (typically driven by HR connector resignation rows)
   - `pug-fsi-executives-mnpi`
3. **Choose users / groups** — populate from a distribution group, mail-enabled security group, or named users
4. **Choose users and roles who can view this priority user group's data** — assign the IRM role groups (typically Insider Risk Management Investigators and Analysts in the corresponding Compliance team) and any specific named users
5. Save

#### FSI priority-group examples

| Priority user group | Scope | Allowed viewers (IRM role groups / named users) | FSI rationale |
|---|---|---|---|
| `pug-fsi-trading-desk` | Trading desk staff | US Compliance Investigators / Analysts | MNPI / market manipulation exposure |
| `pug-fsi-ria-staff` | RIA registered reps | RIA Compliance Investigators | SEC IA fiduciary duty + Reg BI |
| `pug-fsi-mna-team` | M&A and research | Senior Compliance + Legal | Information Barrier / front-running risk |
| `pug-fsi-agent-admins` | Power Platform / Copilot Studio admins | AI Governance Lead + Compliance | Privileged access to agents and grounding sources |
| `pug-fsi-departing-watchlist` | Users with HR `ResignationDate` populated | US Compliance Investigators | Departing-user data theft |
| `pug-fsi-executives-mnpi` | Named C-suite + officers | Senior Compliance + Legal | Pre-announcement MNPI exposure |

### 3.4 Intelligent detections, alert thresholds, and policy timeframes

- **Intelligent detections** — tune the score thresholds for Minor / Moderate / Elevated risk levels and the alert-volume controls. Defaults are reasonable starting points; tune only after observing real signal in your tenant
- **Policy timeframes** — set the **activation window** (typically the trigger event start), the **past activity** lookback, and the **inactivity timeframes**. Document the values chosen in your evidence pack — auditors will ask
- **Inline alert customization** (where exposed) — controls how alerts are surfaced to investigators

### 3.5 Export alerts (SIEM / case-management integration)

If your firm forwards IRM alerts to Microsoft Sentinel, Splunk, or another SIEM / case-management system:

1. **Settings → Export alerts** → enable Office 365 Management Activity API export (current Learn-supported path; verify at deployment)
2. Capture the configuration (target subscription, retention, filters) for evidence

### 3.6 Microsoft Teams — investigator collaboration channel

If your investigators collaborate via Microsoft Teams, enable Teams integration to auto-create a per-case Team for evidence-collection and chat. Document the team-naming convention and retention posture (Teams chat retention is governed by [Control 1.9](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md)).

---

## Step 4 — Configure HR connector (Microsoft 365 HR connector)

If you completed Prerequisite #4 above, the connector exists. This step covers ongoing operational verification.

### 4.1 Confirm connector health

1. Microsoft Purview portal → **Settings** (gear) → **Data connectors** → **HR data**
2. Confirm the connector's **Last successful run** is within the documented schedule (typically nightly)
3. Confirm row count > 0 on the most recent run
4. If the row count is 0 (and your HRIS export is non-empty), the most likely causes are:
   - CSV header mismatch (`EmployeeID` vs `Employee_ID`)
   - Date format mismatch (must be ISO 8601 `YYYY-MM-DD`)
   - SFTP / blob credential expiry on the upstream HRIS export
   - File-size limit exceeded (chunk the export if needed)

### 4.2 Validate end-to-end with a synthetic resignation row

Validate the connector end-to-end by inserting a **synthetic resignation row** into the HRIS export pipeline:

1. Identify a named test user (a non-production identity) and assign a `ResignationDate` (today + 1 day) and a `LastWorkingDate` (today + 30 days)
2. Push the synthetic CSV row through the normal HRIS → connector pipeline
3. Wait for the connector's next scheduled run (or trigger manually)
4. Confirm the test user appears in the relevant IRM context (Activity Explorer, departing-user policy scope) within the documented window
5. Remove the synthetic row at the end of validation

### 4.3 Document data-handling posture

The HR connector ingests employee personal data (employment status, performance signals where opted in). Document:

- Retention of the HRIS source CSV (typically encrypted SFTP or blob with retention aligned to HR records policy)
- Access to the connector's Entra app registration (treat the secret / certificate as a privileged credential)
- Privacy / Legal sign-off on the optional fields (job-level changes, performance reviews) before opting in to *Data leaks by risky users*

---

## Step 5 — Create per-template policies

> **Templates use Learn-canonical names verbatim.** Do not invent template names. The template wizard exposes only the templates Microsoft has shipped at this Learn revision; verify the in-portal list against [Microsoft Learn — Insider Risk Management policy templates](https://learn.microsoft.com/en-us/purview/insider-risk-management-policy-templates) at the time of deployment.

### Templates considered for FSI

| Template | FSI use | Notes |
|---|---|---|
| **Data theft by departing users** | Yes | Single template; cloud-app coverage via Defender for Cloud Apps connectors (Box, Dropbox, Google Drive, Amazon S3, Azure) |
| **Data leaks** | Yes | General data-leak detection; tunable to DLP-triggered or activity-triggered modes |
| **Data leaks by priority users** | Yes (recommended) | Scoped to MNPI / trading / RIA / executive priority groups |
| **Data leaks by risky users** | Yes (where HR risk-user signals are in scope) | Requires HR connector with PIP / performance signals |
| **General security policy violations** | Yes | Requires Microsoft Defender for Endpoint integration |
| **General security policy violations (priority users)** | Yes | Requires MDE + priority user groups |
| **General security policy violations (departing users)** | Yes | Requires MDE + HR connector |
| **General security policy violations (risky users)** | Conditional | Requires MDE + HR risky-user signals |
| **Risky AI usage** | Yes | Requires browser extension (Edge / Chrome) on Windows; feeds Adaptive Protection where available |
| **Risky browser usage (preview)** | Conditional | Verify lifecycle (Preview vs GA) on Learn at deployment; requires browser extension |
| **Forensic evidence** | Conditional | Separate paired policy; opt-in; PAYG; dual-auth; 120-day clip lifecycle (Step 7 below) |
| **Patient data misuse (HIPAA)** | **Out of scope for FSI** | Document the explicit exclusion in your control evidence |

> **Risky Agents is applied by default for all organizations** when IRM is configured, per Microsoft Learn. Do **not** select it from the **Create policy** wizard — it is not surfaced there. Verify the default-apply behavior, the scope (Microsoft 365 Copilot agents, Copilot Studio agents, Microsoft Foundry agents), and the lifecycle (Preview vs GA) on Learn at deployment. Risky Agents flags signals such as: risky prompts sent to agents, agents emitting responses with sensitive content, agents accessing sensitive or priority SharePoint sites, agents sharing SharePoint files externally, and agent activity above an established baseline.

> **Quick policies vs templates.** The IRM home page surfaces "quick policy" launch tiles with friendly labels (e.g., "Data theft from Microsoft 365 apps by users leaving your organization"). These tiles are convenience launchers — the underlying template is the canonical Learn name (e.g., *Data theft by departing users*). When documenting policy inventory, **use the canonical template name**, not the tile label.

### Common policy creation entry path

For every template below:

1. Sign in to the Microsoft Purview portal (sovereign URL from the cloud table)
2. Open **Insider Risk Management**
3. Select **Policies** in the left navigation
4. Select **Create policy** → **Policy template**
5. Walk through the wizard: **Name & description → Users & groups → Priority content (where applicable) → Triggering event → Indicators → Decision (test / production)**
6. **Submit**

### Policy A — Data theft by departing users

| Property | Value |
|---|---|
| Triggering event | HR connector `ResignationDate` (or Microsoft Entra account deletion) |
| Users & groups | Recommended: `pug-fsi-departing-watchlist` priority user group, or a tenant-wide scope filtered by HR resignation |
| Priority content | Sensitivity labels (Confidential, MNPI), priority SharePoint sites (research, M&A, trading systems), client account number SITs |
| Indicators | Office downloads (SharePoint, OneDrive), email-with-attachment to external recipients, USB copy, print, network-share copy, cloud-storage upload (Box / Dropbox / Google Drive / S3 / Azure via Defender for Cloud Apps connectors) |

**Recommended FSI configuration:**

- Scope to the priority user group that mirrors HR-driven departing-user signals
- Enable cloud-storage indicators **only** for the cloud apps your firm permits under acceptable-use; explicitly exclude (with evidence) any cloud app the firm prohibits
- Set the activation window to the typical resignation-to-last-working-date span; tune the past-activity lookback to the audit-log retention horizon
- Assign reviewers (Investigators) per AU scope (US BD vs RIA vs bank LOB)

### Policy B — Data leaks (general)

| Property | Value |
|---|---|
| Triggering event | DLP policy match (High severity incident report — Prerequisite #8) **or** activity-based |
| Users & groups | Tenant-wide or scoped distribution group |
| Priority content | Sensitivity labels (Confidential, NPI, MNPI), client account number SITs |
| Indicators | Email to external recipients, file sharing externally, endpoint exfiltration, cumulative exfiltration |

**Recommended FSI configuration:**

- If using the DLP-trigger path, confirm the upstream DLP policy is configured for **High severity incident reports** ([Control 1.5](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md))
- Enable cumulative exfiltration detection for client-data SITs

### Policy C — Data leaks by priority users (FSI-critical)

| Property | Value |
|---|---|
| Triggering event | DLP policy match or activity-based |
| Users & groups | Priority user group (`pug-fsi-trading-desk`, `pug-fsi-ria-staff`, `pug-fsi-mna-team`, `pug-fsi-executives-mnpi`) |
| Priority content | Same as Policy B, plus deal-code / research SITs |
| Indicators | Same as Policy B |

**Recommended FSI configuration:**

- Create one Data leaks by priority users policy **per priority population** rather than collapsing them into a single policy — supervisory ownership and AU scoping work best when policies are per-population

### Policy D — Data leaks by risky users (HR-driven)

| Property | Value |
|---|---|
| Triggering event | HR-supplied risk signal (PIP / performance review) **or** Communication Compliance risky-user signal |
| Users & groups | All users — the template uses the HR / CC signal to dynamically scope risky users |
| Priority content | Same as Policy B / C |
| Indicators | Same as Policy B / C |

> The Communication Compliance integration ([Control 1.10](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md)) feeds into this template — a CC alert pattern can promote a user into the IRM "risky" cohort, which then activates this policy. Document the cross-product dependency in both control evidence packs.

### Policy E — General security policy violations (and variants)

| Property | Value |
|---|---|
| Triggering event | Microsoft Defender for Endpoint alert (security control evasion, unwanted software, MDE alert types) |
| Users & groups | Tenant-wide, or priority / departing / risky variants |
| Priority content | Not typically used for this template |
| Indicators | MDE-derived indicators (Prerequisite #5) |

**Recommended FSI configuration:**

- Create the **base** *General security policy violations* policy first
- Add the **priority-users** variant for `pug-fsi-agent-admins` (privileged access surface — agents and grounding sources)
- Add the **departing-users** variant where the firm's risk model treats departing-user MDE alerts as high-priority

### Policy F — Risky AI usage (Copilot and non-Microsoft AI)

| Property | Value |
|---|---|
| Triggering event | Risky prompt / response signal from Copilot / Copilot Chat / non-Microsoft AI (via the browser extension) |
| Users & groups | Recommended: every user with a Microsoft 365 Copilot per-user license, plus any non-licensed user expected to use Copilot Chat. Reconcile against your Copilot license inventory ([Control 1.6](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md) / [Control 3.1](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md)) |
| Priority content | Sensitivity labels relevant to AI exposure (MNPI, NPI, Confidential) |
| Indicators | Browsing indicators (risky AI prompts, risky AI responses); requires Edge / Chrome extension on Windows |

**Recommended FSI configuration:**

- Pre-deploy the browser extension via Intune to the in-scope Windows population **before** creating the policy (otherwise the policy produces no signal)
- Cross-reference DSPM for AI ([Control 1.6](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md)) for the corresponding visibility surface
- Where Adaptive Protection is available, enable the bound DLP / DLM / Conditional Access policies (Step 6)

### Policy G — Risky browser usage (preview)

> Verify the lifecycle (Preview vs GA) on Microsoft Learn at deployment — the template may have changed status.

| Property | Value |
|---|---|
| Triggering event | Browsing-indicator signal (downloads from risky sites, browsing to risky categories) |
| Users & groups | Tenant-wide or scoped |
| Indicators | Browsing indicators; requires Edge / Chrome extension on Windows |

### Policy H — Risky Agents (default; do not select from wizard)

Per Microsoft Learn, **Risky Agents is applied by default** when Insider Risk Management is configured. **Do not attempt to create it from the Create policy wizard.** Validate the default policy is producing signal in the IRM Alerts surface (Step 8 — Validation).

If the default policy is not visible in the Alerts dashboard within the analytics window after IRM is configured, verify:

- Tenant cloud supports Risky Agents (Sovereign Cloud Availability table)
- IRM is fully configured (Settings completed; UAL on; analytics scan complete)
- The expected agent surfaces (Microsoft 365 Copilot, Copilot Studio, Microsoft Foundry) are licensed and in use in the tenant

### Patient data misuse — explicit exclusion

For FSI tenants, **explicitly document** that the *Patient data misuse* (HIPAA) template is out of scope and not configured. Auditors should not have to reverse-engineer the absence of HIPAA templates in a financial-services control inventory.

### Test mode vs production mode

> **Critical silent-failure mode:** policies in **Test mode** **do not produce alerts**. Per Microsoft Learn, Test mode allows you to validate policy logic against historical activity without surfacing alerts to the Alerts dashboard. **Promote to production** at the end of the documented validation window, otherwise the policy "exists" but generates no supervisory signal.

For each policy in your inventory, capture the current mode (Test / Production), the date of the last mode change, the change ticket reference, and the rationale.

### Policy naming convention (use a strict convention)

Name policies with a strict prefix to make audit-log queries and evidence collection deterministic:

```
FSI-IRM-<TemplateShortName>-<Population>-<Mode>-<YYYYQN>
e.g., FSI-IRM-DataTheftDeparting-USBD-Prod-2026Q2
e.g., FSI-IRM-DataLeaksPriority-TradingDesk-Prod-2026Q2
e.g., FSI-IRM-RiskyAIUsage-CopilotLicensed-Test-2026Q2
e.g., FSI-IRM-SecPolViol-AgentAdmins-Prod-2026Q2
```

Policy names cannot be edited after creation in the same surface — name carefully.

---

## Step 6 — Adaptive Protection (where available)

> **Adaptive Protection has limited availability in US Government clouds.** Verify the Sovereign Cloud Availability table at the top of this playbook before relying on Adaptive Protection.

Adaptive Protection dynamically assigns DLP, Data Lifecycle Management (extended retention preservation for elevated-risk users), and Conditional Access controls based on the user's calculated insider-risk level (Minor / Moderate / Elevated). It consumes signals from configured IRM policies including *Risky AI usage* and the default *Risky Agents* policy.

### Configure Adaptive Protection

1. **Insider Risk Management → Adaptive Protection** (verify the navigation label on Learn `insider-risk-management-adaptive-protection` at deployment)
2. Configure the **risk levels** (Minor / Moderate / Elevated) and the IRM signals that promote a user into each level. Defaults are reasonable; tune only after observing signal in your tenant
3. Bind the corresponding **DLP policy** ([Control 1.5](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md)) to each risk level — typically a stricter DLP enforcement (Block, Block with override → Block) for Elevated users
4. Bind the corresponding **Data Lifecycle Management** preservation (typically 120-day retention preservation for Elevated users — preserves activity for investigation)
5. Bind the corresponding **Conditional Access** policy (typically a step-up MFA challenge or session control for Elevated users)
6. Save and capture configuration as evidence

### Validate Adaptive Protection (threshold-trigger test)

Validation is by **threshold-trigger test**: drive a synthetic test user's risk level into Elevated through a controlled IRM signal (a synthetic risky-AI prompt or a synthetic departing-user data download in a non-production tenant), then verify the bound DLP / DLM / CA controls activate within the documented window.

Capture: the synthetic signal, the user's IRM risk level transition, the DLP block event, the DLM preservation event, the CA policy match, all with UTC timestamps.

---

## Step 7 — Forensic Evidence (opt-in; dual-auth; PAYG; 120-day clip lifecycle)

> **Forensic Evidence is off by default.** Skip this step if your firm's privacy / WSP posture excludes Forensic Evidence. **State-law notice obligations (CT, DE, NY, and others) and any collective-bargaining-agreement notice posture must be cleared with Privacy / Legal before opting in.**
>
> **Forensic Evidence has limited availability in US Government clouds.** Verify the Sovereign Cloud Availability table.

### 7.1 Confirm prerequisites

All of the following must be true before opt-in:

- **Insider Risk Management Approvers** role group populated and **distinct** from Investigators (Step 2)
- **Microsoft Purview Client** installed on in-scope devices
- Devices on **Windows 10 / 11 Enterprise** and **onboarded to Microsoft Purview**
- **PAYG billing** linked to an Azure subscription (verify current organizational storage trial size on Microsoft Learn `insider-risk-management-forensic-evidence` at deployment)
- **Privacy / Legal sign-off on state-law notice posture** (CT, DE, NY, plus any other applicable jurisdictions; CBA notice if applicable). Capture the sign-off in the change ticket
- Employee-monitoring notice updated in employee handbook / acceptable-use policy where required

### 7.2 Opt in and create the Forensic Evidence policy

1. Microsoft Purview portal → **Insider Risk Management** → **Forensic Evidence settings** (verify exact navigation on Learn at deployment)
2. **Onboard devices** for Forensic Evidence (subset of Purview-onboarded devices)
3. Configure **capture options** — clip duration, capture frequency, sensitive-content masking
4. **Create a Forensic Evidence policy** that pairs to a primary detection policy (e.g., *Data theft by departing users* or *Risky AI usage* for the in-scope priority population)
5. Assign reviewers (Investigators) and approvers (Approvers — distinct from Investigators)
6. Save

### 7.3 Capture lifecycle (dual-auth)

For each capture event:

1. **Investigator submits** a capture request from an alert / case in the IRM workspace
2. **Approver approves** the request from the Approver queue (or it is rejected with documented rationale)
3. The capture executes on the in-scope device (visible to the user in the Microsoft Purview Client per the privacy notice)
4. The clip lands in the Forensic Evidence storage (PAYG-billed)
5. **Clip is automatically deleted 120 days after capture** unless exported. Document the export-or-discard decision in the case record before the 120-day expiry

### 7.4 Records retention boundary

Forensic Evidence clips are **working investigative artifacts**, not records under SEC 17a-4(f) / FINRA 4511. If a clip must be retained beyond 120 days for regulatory or litigation purposes:

- Export the clip and place it under a retention label / records management policy ([Control 1.9](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md))
- Or place the corresponding case under a legal hold via eDiscovery (Premium) ([Control 1.19](../../../controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md))

Do **not** rely on Forensic Evidence storage as a records system — the 120-day auto-delete is the documented Microsoft Learn behavior.

---

## Step 8 — Validation (deterministic seed-and-assert)

> Do **not** treat "policy created with no error" as PASS. Generate a known seed activity from a named test user, wait the documented Learn processing window, and assert both the **alert appears** in the IRM workspace and the corresponding **audit-log rows** are written.

### Validation procedure (per policy)

1. **Identify a named test user** scoped to the policy (in the priority user group / AU / HR-driven scope as applicable)
2. **At a recorded UTC timestamp**, have the test user perform an activity that is **certain** to match the policy's indicators. Examples:
   - *Data theft by departing users* — synthetic resignation row + bulk SharePoint download from a sensitivity-labeled site (non-production data)
   - *Data leaks* — DLP-trigger event (sending an email containing a synthetic SSN matching the SIT) — confirm the upstream DLP policy is configured for High severity incident reports
   - *Risky AI usage* — submit a synthetic risky prompt to Copilot from a Windows device with the Edge / Chrome extension installed (use a non-production / clearly-marked test prompt)
   - *General security policy violations* — controlled MDE-detected event in a non-production endpoint
   - *Risky Agents* (default) — exercise an in-scope agent with a synthetic risky prompt and observe the Risky Agents alert
3. Record:
   - Sender UPN
   - UTC activity time (`Get-Date -Format 'yyyy-MM-ddTHH:mm:ssZ'`)
   - Activity type and indicator(s) expected to match
   - Policy expected to score the activity
4. **Wait the documented Learn processing window:**
   - Analytics scans: **up to 48 hours** for initial completion (per Learn)
   - Policy alerts: **not immediate** — allow the documented Learn window for the indicator type; Microsoft does not publish a single SLA — allow up to 24 hours for most indicator types and up to 48 hours for low-frequency batched indicators
   - HR-driven scoring: starts after the next HR connector run + activation window
5. **Verify in the IRM workspace:**
   - Open **Insider Risk Management → Alerts**
   - Filter by user and the UTC window
   - Confirm the alert appears with the matched indicator(s)
   - If the firm uses the Triage Agent (where in scope and lifecycle permits — verify on Learn), confirm the alert is triaged into the expected priority bucket
6. **Verify investigator workflow:**
   - As an Insider Risk Management Investigator, open the alert
   - Create a case (record the case ID and UTC timestamp)
   - Exercise content preview where in scope (verify the capability lifecycle on Learn at deployment)
   - Where Forensic Evidence is opted-in: submit a capture request, have the Approver approve it, confirm the clip is captured (use a non-production endpoint for this test), and verify the 120-day auto-delete clock starts
7. **Verify audit-log rows** in the Unified Audit Log (Microsoft Purview Audit search):

```text
Activities to filter for (verify exact operation names against current Learn at the time of search):
  - Insider Risk Management policy operations (policy create / update / delete)
  - Insider Risk Management alert operations (alert triage state changes)
  - Insider Risk Management case operations (case create / update / close)
  - Insider Risk Management settings changes (privacy, indicators, priority groups)
  - Forensic Evidence capture-request submitted / approved / rejected (where opted-in)
  - Pseudonymization unmask events (where Auditor review is in scope)
Date range: UTC window covering activity + processing window + investigator action
Users: test user, test investigator, test approver (where in scope)
```

Or via PowerShell (read-only audit search):

```powershell
Connect-IPPSSession   # or the sovereign equivalent per powershell-baseline.md §3
Search-UnifiedAuditLog -StartDate (Get-Date).AddDays(-3) -EndDate (Get-Date) `
    -RecordType 'InsiderRiskManagement' `
    -ResultSize 5000 |
    Export-Csv -NoTypeInformation -Path ".\evidence\1.12-validation-$(Get-Date -Format 'yyyyMMddTHHmmssZ').csv"
```

> Verify the `RecordType` value against the current `Search-UnifiedAuditLog` documentation; Microsoft has occasionally introduced more specific RecordTypes for IRM sub-surfaces. If the broad RecordType returns no rows, fall back to `-Operations` filtering by the specific IRM operation names.

8. **Capture evidence** with SHA-256 sidecar per `docs/playbooks/_shared/powershell-baseline.md` §5:
   - Screenshot of the alert in the IRM workspace (with anonymized usernames if pseudonymization is on; capture both anonymized and admin-resolved view if your firm requires it)
   - Case record export
   - CSV export of the UAL search
   - Forensic Evidence capture-request audit row (where in scope)
   - SHA-256 sidecar for each artifact

### Validation cadence

- **Per policy at creation:** required (one-time deterministic validation)
- **Per policy after any material change:** required (template, scope, indicator, priority-group, mode change)
- **Quarterly:** sample-validate every Zone-3 policy (priority-user policies, departing-user policies, Risky AI usage)
- **Annually:** sample-validate every active policy
- **On demand:** when investigators or auditors flag suspected silent-failure (zero alerts during a period of expected activity)

---

## Step 9 — Operationalization (cadence, escalation, integration)

### Triage cadence (organizational, not portal)

Microsoft does not publish IRM alert / investigation SLAs. Document in your firm's **Written Supervisory Procedures (WSP)** — not in IRM settings — the triage and investigation cadence (e.g., "Tier-1 analyst triage within \<firm-defined window\>; investigator escalation within \<firm-defined window\>"). Track adherence in your case-management / GRC tool. The portal does not enforce SLAs; alert queue depth and per-alert age are the operational signals to monitor.

> Any cadence cited in this framework or in your firm's WSP is a **firm-defined supervisory commitment**, not a Microsoft-stated ceiling. Frame all cadence numbers as your firm's WSP.

### Escalation paths

| From IRM | To | Trigger |
|---|---|---|
| IRM Analyst | IRM Investigator | Alert confirmed as risk-bearing |
| IRM Investigator | HR | Personnel-conduct violation |
| IRM Investigator | Legal | Potential disclosure obligation; state-law notice question |
| IRM Investigator | eDiscovery (Premium) ([Control 1.19](../../../controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md)) | Legal hold needed; production scope expansion |
| IRM Investigator | Communication Compliance ([Control 1.10](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md)) | Communication-content evidence relevant to case |
| IRM Investigator | DSPM for AI ([Control 1.6](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md)) | AI prompt / response context relevant to Risky AI usage cases |
| IRM Investigator | CISO + Legal | Cyber / data-loss event; trigger SEV-1/2 incident handling per the FSI Incident Handling section of [troubleshooting.md §1](troubleshooting.md) |
| IRM Investigator | Records management ([Control 1.9](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md)) | Promote artifact for retention beyond IRM working lifecycle (especially **before** Forensic Evidence's 120-day clip expiry) |

### Integration with Communication Compliance (Control 1.10)

IRM integrates with Communication Compliance in two directions:

1. **CC → IRM:** A CC `Detect inappropriate text` or `Regulatory compliance` policy can act as a risk signal feeding IRM risky-user policies (the *Data leaks by risky users* template can consume CC-flagged-user signal). This surfaces communication-based risk into IRM scoring without a separate manual workflow
2. **IRM → CC:** IRM alerts and cases can be referenced during CC investigations to provide behavioral context (was this user on an IRM watchlist when the message was sent?)

Document any cross-product policies in both control evidence packs (Control 1.10 **and** Control 1.12) to avoid orphaned references during an audit.

### Integration with DSPM for AI (Control 1.6)

DSPM for AI provides the visibility plane for AI prompts, sensitive-prompt classifiers, and unprotected grounding sources. IRM provides the **scoring and case workflow** for risky AI usage. The two are designed to be used together for FSI Copilot supervision under FINRA 25-07. See [Control 1.6](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md).

### Records retention boundary (restated)

IRM is a **detect / investigate / act** surface. Durable, tamper-resistant retention is implemented separately under retention policies and records management ([Control 1.9](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md)).

- **IRM alerts and cases** are working artifacts retained per the IRM service lifecycle — promote any artifact required for SEC 17a-4(f) / FINRA 4511 purposes to retention policies / records management
- **Forensic Evidence clips auto-delete 120 days after capture** — promote required clips to retention before expiry

---

## Anti-patterns

The following are common configuration mistakes that produce silent failures, false-clean evidence, or audit findings. Avoid all of them.

1. **Assuming IRM is at parity in US Government clouds.** Adaptive Protection, Forensic Evidence, and several browser-derived templates have **limited or no availability** in GCC / GCC High / DoD. Verify the Sovereign Cloud Availability table before relying on this control in those clouds.
2. **Leaving policies in Test mode.** Test-mode policies **do not produce alerts**. Promote to Production at the end of the validation window and capture evidence of the mode change.
3. **Treating IRM as a records-retention vault.** IRM alerts, cases, and Forensic Evidence clips are working investigative artifacts — Forensic Evidence clips auto-delete after 120 days. Use [Control 1.9](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md) for SEC 17a-4(f) / FINRA 4511 retention.
4. **Configuring Forensic Evidence with the same user in Investigators and Approvers.** Breaks dual-authorization. **Approvers must be distinct from Investigators.**
5. **Using the wrong (singular / synonym) role-group names.** Audit-log queries match the canonical plural names (`Insider Risk Management Investigators`, not `IRM Investigator`). Wrong names produce empty queries and false-clean evidence.
6. **Selecting "Risky Agents" from the Create policy wizard.** Risky Agents is **applied by default**. The wizard does not surface it.
7. **Using fabricated template names** (e.g., "Data theft from Microsoft 365 apps by users leaving your organization" as if it were a separate template, or "Agent-Related Insider Risk" custom policy as a substitute). The canonical name is *Data theft by departing users* (single template, with cloud-app coverage via Defender for Cloud Apps connectors), and the agent surface is covered by *Risky Agents* (default) plus *Risky AI usage*.
8. **Assuming Security policy violations consumes failed-authentication signals.** It consumes **Microsoft Defender for Endpoint** alerts (security control evasion, unwanted software, MDE alert types). Failed authentication and risky sign-in are **Entra ID Protection** signals, handled separately.
9. **Treating the HR connector as a generic Logic App / API.** It is the **Microsoft 365 HR connector** (CSV upload + scheduled ingestion). Schema mismatch (header names, ISO 8601 dates) is a silent-failure mode — synthetic-row validation is required.
10. **Creating a *Data leaks* policy with DLP as the trigger but the upstream DLP policy not configured for High severity incident reports.** The IRM policy will not trigger.
11. **Creating a Risky AI usage policy without deploying the browser extension via Intune.** Produces no signal.
12. **Creating a priority user group without defining who can view it.** The group exists but no IRM member can see its alerts. Define the viewer assignment at creation.
13. **Disabling pseudonymization without an audit trail.** Privileged action; must be auditable. The Insider Risk Management Auditors role group reviews unmask events.
14. **Adding users to Insider Risk Management Investigators casually.** Investigators see content (subject to pseudonymization), can submit Forensic Evidence capture requests, and can drive case escalation. Treat each addition as a privileged elevation with HR / Legal sign-off.
15. **Combining Investigators and Auditors in the same person.** Auditors review investigator and admin actions — independence is required.
16. **Documenting fabricated SLA toggles** (e.g., "48-hour Low/Medium triage, 4-hour High/Critical triage") **as portal settings**. Microsoft does not publish IRM SLAs. Cadence is firm-defined and tracked in your WSP / case-management tool, not in IRM settings.
17. **Configuring Adaptive Protection bindings without validating the threshold-trigger end-to-end.** A bound DLP / DLM / CA policy that does not actually fire when a user crosses Elevated is a silent failure.
18. **Opting in to Forensic Evidence without state-law / CBA notice posture cleared.** Privacy and Legal sign-off is a prerequisite. CT, DE, NY, and several other US states have specific employee-monitoring notice requirements.
19. **Leaving Forensic Evidence clips to auto-delete at 120 days when the case requires longer retention.** Promote the clip to retention / eDiscovery (Premium) before the 120-day expiry.
20. **Treating Triage Agent and Content preview as GA without verifying lifecycle on Learn.** These capabilities have changed status; verify Preview vs GA at deployment and write defensively.
21. **Assuming PAYG-flagged indicators "just work" without PAYG enabled.** Without PAYG, the indicator is silently zero.
22. **Validating by "I created the policy and it didn't error."** Validation requires a **seeded test activity** + the documented Learn processing window + verification of both the alert in the IRM workspace and the IRM-related audit-log rows.

---

## Evidence pack

Use a consistent file naming convention:

```
Control-1.12_{TenantId}_{Cloud}_{ArtifactType}_{YYYYMMDD-HHmm-UTC}.{ext}
Control-1.12_{TenantId}_{Cloud}_{ArtifactType}_{YYYYMMDD-HHmm-UTC}.{ext}.sha256
```

| Artifact | Source | Format | Frequency |
|---|---|---|---|
| Sovereign cloud capability snapshot (which IRM capabilities are at parity in this tenant cloud) | Manual + Learn-cited table | JSON / Markdown | Quarterly + on Microsoft service update |
| License entitlement snapshot for monitored users (E5 / E5 Compliance / IRM standalone / Purview Suite) | Graph `Get-MgUserLicenseDetail` | JSON | Quarterly |
| PAYG billing state (subscription, usage, organizational storage trial state for Forensic Evidence) | Purview Usage center | CSV | Monthly |
| Unified Audit Log status (`Get-AdminAuditLogConfig`) | Exchange Online PowerShell (sovereign endpoint) | JSON | Monthly + on change |
| Role-group membership (six IRM role groups) | Purview portal export + Graph | CSV + JSON | Monthly + on change |
| Approvers ≠ Investigators set-difference report | Computed from role-group export | CSV | Monthly + on change |
| Pseudonymization setting state and opt-out audit trail | Purview Privacy page + UAL | PNG + CSV | On change |
| Unmask-event review log (Auditors role group cadence) | UAL search | CSV | Monthly |
| Administrative Unit assignments per IRM role-group member | Purview portal + Graph | JSON | On change |
| Settings → Policy indicators state per category | Purview Settings export + screenshot | JSON + PNG | Quarterly + on change |
| Priority user groups (name, members, viewer assignment) | Purview Settings export | JSON | Monthly |
| Microsoft 365 HR connector health (last successful run, row count, schema) | Connector status page + HRIS export sample | JSON + CSV (with synthetic-row validation log) | Weekly + per validation |
| Microsoft Defender for Endpoint integration state | Defender XDR Advanced features export | JSON | Monthly + on change |
| Microsoft Defender for Cloud Apps connector inventory (Box, Dropbox, Google Drive, Amazon S3, Azure) | Defender for Cloud Apps export | JSON | Monthly + on change |
| Browser extension deployment status (Intune assignment, in-scope Windows population coverage) | Intune export | CSV | Monthly + on change |
| Policy inventory (template, name, mode, scope, priority-content, indicators, triggering event, reviewer / Approver assignment, AU scope, last validation timestamp) | Purview Policies page export | JSON + CSV | Weekly |
| Test mode → Production mode change log | Change tickets + UAL | CSV | On change |
| Adaptive Protection configuration (risk-level thresholds, DLP / DLM / CA bindings) | Purview portal export | JSON | On change |
| Adaptive Protection threshold-trigger validation log | Test execution log | Log + CSV | Per validation |
| Forensic Evidence configuration (opt-in state, device onboarding, capture options, Approver list, state-law notice posture, Privacy/Legal sign-off) | Purview portal export + change ticket | JSON + PDF | On change |
| Forensic Evidence capture-request log (submit / approve / reject; clip retention or export decision before 120-day expiry) | Purview portal + UAL | CSV | Monthly |
| Per-policy validation result (test user, UTC, indicator, alert appearance, audit rows) | Test log + UAL CSV | CSV + log | Per validation |
| Risky Agents default-policy signal validation | Test log + alert export | CSV + screenshot | Quarterly |

Store in immutable storage (Purview retention label, SharePoint hold, or WORM blob) aligned to [Control 1.9](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md) retention.

---

## Cross-references

- [Control 1.12 PowerShell Setup](powershell-setup.md)
- [Control 1.12 Verification & Testing](verification-testing.md)
- [Control 1.12 Troubleshooting (FSI Incident Handling — READ FIRST)](troubleshooting.md)
- [Control 1.5 DLP and Sensitivity Labels](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) — block layer + Adaptive Protection bindings + DLP-trigger source for Data leaks
- [Control 1.6 Grounding Data Protection / DSPM for AI](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md) — visibility surface that complements IRM scoring for AI risk
- [Control 1.7 Comprehensive Audit Logging](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) — UAL prerequisite + audit-log evidence for IRM operations
- [Control 1.9 Records Retention and Immutability](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md) — durable retention plane (IRM is **not** the records store; Forensic Evidence clips auto-delete at 120 days)
- [Control 1.10 Communication Compliance Monitoring](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md) — bidirectional integration with IRM
- [Control 1.13 Sensitive Information Types](../../../controls/pillar-1-security/1.13-sensitive-information-types-sits-and-pattern-recognition.md) — create custom SITs **before** referencing them in IRM priority content
- [Control 1.19 eDiscovery for Agent Interactions](../../../controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md) — escalation path for legal hold / production
- [Control 2.6 Model Risk Management](../../../controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md) — ML risk scoring and Triage Agent require MRM governance under OCC 2011-12 / SR 11-7
- [Control 2.12 Supervision and Oversight (FINRA 3110)](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) — FINRA 3110 / 25-07 supervisory framing
- [Control 3.1 Agent Inventory and Metadata Management](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md) — agent inventory used to scope Risky AI usage
- [Microsoft Learn — Insider Risk Management overview](https://learn.microsoft.com/en-us/purview/insider-risk-management)
- [Microsoft Learn — Configure Insider Risk Management](https://learn.microsoft.com/en-us/purview/insider-risk-management-configure)
- [Microsoft Learn — Insider Risk Management permissions](https://learn.microsoft.com/en-us/purview/insider-risk-management-permissions)
- [Microsoft Learn — Insider Risk Management policies](https://learn.microsoft.com/en-us/purview/insider-risk-management-policies)
- [Microsoft Learn — Insider Risk Management policy templates](https://learn.microsoft.com/en-us/purview/insider-risk-management-policy-templates)
- [Microsoft Learn — Settings: Policy indicators](https://learn.microsoft.com/en-us/purview/insider-risk-management-settings-policy-indicators)
- [Microsoft Learn — Adaptive Protection](https://learn.microsoft.com/en-us/purview/insider-risk-management-adaptive-protection)
- [Microsoft Learn — Forensic Evidence](https://learn.microsoft.com/en-us/purview/insider-risk-management-forensic-evidence)
- [Microsoft Learn — Browser support for Insider Risk Management](https://learn.microsoft.com/en-us/purview/insider-risk-management-browser-support)
- [Microsoft Learn — Import HR data](https://learn.microsoft.com/en-us/purview/import-hr-data)
- [Microsoft Learn — Insider Risk Management cases](https://learn.microsoft.com/en-us/purview/insider-risk-management-cases)
- [Microsoft Learn — Insider Risk Management activities](https://learn.microsoft.com/en-us/purview/insider-risk-management-activities)

---

*Updated: April 2026 | Version: v1.4 | UI Verification Status: Current (commercial); GCC / GCC High / DoD verified per Sovereign Cloud Availability table — multiple HARD GAPs documented for Government clouds*
