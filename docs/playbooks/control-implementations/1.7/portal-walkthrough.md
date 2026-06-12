# Control 1.7 — Portal Walkthrough: Comprehensive Audit Logging and Compliance

**Control ID:** 1.7 — Comprehensive Audit Logging and Compliance
**Pillar:** 1 — Security & Identity
**Last UI Verified:** May 2026
**Estimated Time:** 4–8 hours initial buildout (single tenant); 60–120 minutes per environment for Dataverse audit enablement; 30–45 minutes per quarterly evidence-pack refresh
**Audience:** Purview Audit Admin, Purview Compliance Admin, Exchange Online Organization Configuration role holder, SOC Analyst, Power Platform Admin, Entra Security Admin, Azure Storage Account Owner
**Prerequisites:** Microsoft 365 E5 (or Office 365 E5 / Microsoft Purview Suite / E5 eDiscovery & Audit add-on) per Copilot user; per-user **10-Year Audit Log Retention** add-on for any user placed on a documented 10-year capture-window policy; Exchange Online PowerShell module v3.0+; Azure subscription for immutable blob storage (if WORM export is in scope); change-management ticket open for any tenant-wide audit ingestion change.

---

!!! danger "READ FIRST — Scope and Sibling Routing"
    This walkthrough operationalizes the **capture plane** of Control 1.7: how Microsoft 365 Audit (Standard, Premium, and the 10-Year Audit Log Retention add-on), Dataverse environment audit, and Entra agent sign-in telemetry are enabled, scoped, retained, and exported as evidence for FINRA, SEC, OCC, NYDFS, CFTC, and Federal Reserve examinations.

    **This walkthrough IS:**

    - The portal-side procedure for verifying / enabling unified audit logging, validating per-user license entitlement, authoring Audit (Premium) custom retention policies that explicitly cover the Copilot record types, enabling pay-as-you-go (PAYG) collection for non-Microsoft AI app interactions, configuring Dataverse environment-level and Microsoft Copilot Studio per-table audit, capturing Entra agent sign-in telemetry, and exporting evidence to a Cohasset-attested 17a-4(f) preservation layer.
    - The point-in-time **capture-trail** runbook examiners walk during books-and-records examinations.

    **This walkthrough is NOT (route to the linked sibling):**

    | Topic | Where it lives |
    |-------|----------------|
    | Retrieving the **prompt and response body** for a `CopilotInteraction` audit record | [Control 1.6 — DSPM for AI](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md), [Control 1.19 — eDiscovery (Premium) for Agent Interactions](../../../controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md), [Control 1.10 — Communication Compliance Monitoring](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md) |
    | DLP policy authoring and sensitivity-label enforcement on Copilot data flows | [Control 1.5 — DLP and Sensitivity Labels](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) |
    | Communications supervisory review of AI-generated messages for FINRA Rule 3110 | [Control 2.12 — Supervision and Oversight](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) |
    | Records-management retention/disposition labels distinct from audit retention | [Control 2.6 — Model Risk Management (OCC Bulletin 2026-13 (formerly OCC 2011-12) / Fed SR 26-2 (formerly SR 11-7))](../../../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md) and the Records Management retention label set documented in your firm's records schedule |
    | Incident reporting and root-cause documentation when an audit gap is discovered | [Control 3.4 — Incident Reporting and Root-Cause Analysis](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) |
    | Sentinel ingestion rules, KQL detections, and SIEM-side correlation | [Control 3.9 — Microsoft Sentinel Integration](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md) |

    If your task maps to a row above, **stop and route to the linked playbook**. Continuing here will produce duplicate or conflicting evidence — and, worse, may give the false impression that the audit log alone preserves prompt and response content (it does not).

!!! danger "Capture vs Preservation — the central non-substitution warning"
    Microsoft 365 Audit (Standard, Premium, and the 10-Year Audit Log Retention add-on) is **record-CAPTURE operational telemetry**. It is **not**, by itself, a SEC Rule 17a-4(f)–compliant electronic recordkeeping system for the books-and-records record set. Broker-dealers, FCMs, swap dealers, and CPOs subject to SEC 17a-4 / FINRA 4511 / CFTC 1.31 must satisfy **preservation** through one of:

    - **WORM-format storage** of the books-and-records record set — for example, **Azure immutable blob storage** with a time-based retention policy in a locked state. Cohasset Associates has issued an attestation that this configuration meets the non-rewriteable, non-erasable storage requirements of SEC 17a-4(f), CFTC 1.31, and FINRA 4511. See [Microsoft Learn: Immutable storage for Azure blob data](https://learn.microsoft.com/en-us/azure/storage/blobs/immutable-storage-overview).
    - The **audit-trail alternative** introduced by the SEC's October 2022 amendments to Rule 17a-4(f) (compliance date **3 May 2023**), which requires the system to preserve original records and a complete time-stamped audit trail of all modifications and deletions, **plus** a Designated Executive Officer (DEO) representation **or** a Designated Third Party (DTP) undertaking, **plus** an independent records-management assessment.

    A defensible 17a-4(f) program for AI agent communications typically combines **three** layers:

    1. **Microsoft 365 Audit** (this control) — for activity capture and the join key.
    2. **DSPM for AI / eDiscovery (Premium) / Communication Compliance** (Controls 1.6, 1.19, 1.10) — for content retrieval from the Microsoft 365 Substrate.
    3. A **17a-4(f)-attested archive** for preservation — either **Azure immutable blob storage** (Cohasset-attested) or a SEC 17a-4-attested third-party books-and-records vendor such as **Smarsh Enterprise Archive**, **Global Relay Archive**, **Proofpoint Enterprise Archive**, **Mimecast Cloud Archive**, **Bloomberg Vault**, or **Veritas Enterprise Vault.cloud**.

    **Do not rely on the 10-year audit retention add-on as your 17a-4(f) preservation layer.** The 10-year add-on extends the audit *capture* window; it does not transform Microsoft 365 Audit into a non-rewriteable, non-erasable record store with an attached DEO/DTP undertaking.

!!! warning "Hedged-Language Reminder (Mandatory)"
    Throughout this playbook — and in any derivative runbook, ticket template, attestation memo, or examiner-response narrative — the following overclaim phrases **must not appear**:

    - "ensures compliance with..." → use **"supports compliance with..."** or **"helps the organization meet..."**
    - "guarantees..." → use **"is designed to..."**
    - "will prevent..." → use **"is intended to reduce the likelihood of..."**
    - "eliminates the risk of..." → use **"helps mitigate..."**

    Microsoft 365 Audit, DSPM for AI, eDiscovery, and Communication Compliance reduce risk surface and produce evidence; they do not produce a legal compliance guarantee. Examiners and outside counsel read every audit narrative; an unhedged sentence in a 17a-4 attestation is the single fastest way to convert a routine inquiry into a finding. When in doubt, attach: "**Implementation requires sustained operator discipline; organizations should verify configuration against current regulatory expectations and their own legal counsel's interpretation.**"

!!! info "License Requirements"
    Audit retention beyond the 180-day Audit Standard default depends on **per-user licensing**. Verify entitlement before configuring retention policies — without the user-side license, retention silently caps at 180 days regardless of the policy you create.

    | Retention horizon | Required per-user license |
    |---|---|
    | 180 days (Audit Standard default) | Any commercial M365 enterprise SKU |
    | 1 year for `AzureActiveDirectory` / `Exchange` / `OneDrive` / `SharePoint` only (non-modifiable default policy) | Microsoft 365 E5, Office 365 E5, **Microsoft Purview Suite** (formerly M365 E5 Compliance), or M365 E5 eDiscovery and Audit add-on |
    | Custom audit retention policy covering any non-default workload (including all Copilot record types) | Same as above (Audit Premium entitlement) |
    | Up to 10 years | All of the above **plus** the per-user **10-Year Audit Log Retention** add-on |
    | `AIAppInteraction` (non-Microsoft AI apps captured via network/browser DLP under the `AIApp` workload) | **Audit pay-as-you-go (PAYG)**; explicit enablement; 180-day retention for PAYG records; consumption billed against an Azure subscription |
    | Microsoft-built Copilot / Copilot Studio agent `CopilotInteraction` and `ConnectedAIAppInteraction` events | Included in Audit (Standard) at no incremental cost (verify per-workload scope on Microsoft Learn before assuming) |

---

---

## §0 — Coverage Boundary, Capture vs Content, and Portal-vs-PowerShell Decision Matrix

### 0.1 What Control 1.7 Owns vs. What It Doesn't

Control 1.7 owns **operational telemetry capture** for Microsoft 365 Copilot and agent activity: who invoked which agent, when, against what resources, with what model provider, and whether jailbreak / cross-prompt-injection (XPIA) detection fired. It also owns the **retention** of that telemetry inside Microsoft Purview Audit and the **export / preservation** of that telemetry into a 17a-4(f)-attested archive.

| In scope for 1.7 | Out of scope for 1.7 (linked control) |
|------------------|---------------------------------------|
| Verifying / enabling unified audit logging tenant-wide | Capturing the human supervisory review of AI-generated communications ([2.12](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md)) |
| Authoring Audit (Premium) custom retention policies that explicitly include the Copilot record types | Authoring DLP policies that *block* sensitive data in Copilot prompts ([1.5](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md)) |
| Enabling PAYG collection for `AIAppInteraction` (non-Microsoft AI apps via network/browser DLP) | Reviewing the prompt and response **body text** of a captured `CopilotInteraction` ([1.6](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md), [1.19](../../../controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md), [1.10](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md)) |
| Enabling Dataverse environment-level audit and per-table audit on the six Copilot Studio entities | Authoring the Copilot Studio agent sponsorship and lifecycle workflow (Control 1.2) |
| Configuring Entra `agentSignIn` log forwarding to a Log Analytics workspace | Writing Sentinel KQL detection rules against the forwarded data ([3.9](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md)) |
| Configuring Azure immutable blob storage for WORM export of audit artifacts | Drafting the Designated Executive Officer (DEO) representation or Designated Third Party (DTP) undertaking required by the 17a-4(f) audit-trail alternative |
| Reporting an audit-pipeline gap as a finding | Running the root-cause analysis on that gap ([3.4](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md)) |

### 0.2 Audit Record vs Conversation Content — Where the Text Actually Lives

This is the most consequential design distinction in the entire control. Get it wrong and the firm will wrongly tell an examiner that "the audit log preserves the AI conversation."

| Layer | What it carries | Where it lives | Retrieval surface |
|---|---|---|---|
| **Audit record** (`CopilotInteraction`) | Timestamps, `UserId`, `AgentId`, `AgentName`, `AgentVersion`, `Messages[].ID`, `Messages[].IsPrompt`, `Messages[].JailbreakDetected`, `AccessedResources[].XPIADetected`, `ModelTransparencyDetails.ModelProviderName`. **Not** the prompt or response body text. | Microsoft Purview unified audit log (workload `Copilot`) | Purview Audit search; `Search-UnifiedAuditLog`; Audit Search Graph API; Office 365 Management Activity API |
| **Conversation content** | Full prompt text and full response text for Microsoft 365 Copilot interactions | Microsoft 365 Substrate — the per-user Copilot interaction history mailbox | **DSPM for AI** ([1.6](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md)) for compliance-manager transcript view; **eDiscovery (Premium)** ([1.19](../../../controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md)) for legal hold / collection / review; **Communication Compliance** ([1.10](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md)) for FINRA Rule 3110 supervisory review |

Compliance-design implication: the audit log is the **evidence trail and the join key**; the Substrate (via DSPM / eDiscovery / Comm Compliance) is the **content store**. A SEC 17a-4(b)(4) communications-retention program for Copilot must address **both**, and (for broker-dealers) export both into the firm's 17a-4(f)-attested preservation layer. §3 of this walkthrough shows how to navigate from a Purview Audit search hit to each of the three content-retrieval surfaces.

### 0.3 Portal-vs-PowerShell Decision Matrix

| Task | Portal | PowerShell | Notes |
|---|:---:|:---:|---|
| Verify `UnifiedAuditLogIngestionEnabled` | ⚠️ Not exposed | ✅ Required | Must run from **Exchange Online PowerShell** — Security & Compliance PowerShell always returns `False` |
| Enable unified audit logging | ✅ Audit solution banner | ✅ `Enable-OrganizationCustomization`-gated | Portal is the simpler change-managed path |
| Author custom audit retention policy | ✅ Audit > Policies | ✅ `New-UnifiedAuditLogRetentionPolicy` | Portal for first-time setup, PowerShell for bulk lifecycle |
| Enable PAYG for `AIAppInteraction` | ✅ Audit > Settings | ⚠️ Some toggles portal-only | PAYG enablement is portal-first |
| Search and export | ✅ Audit > New search | ✅ `Search-UnifiedAuditLog -SessionCommand ReturnLargeSet` | Portal capped at 180-day window and 50,000 records per session; PowerShell required for larger windows or paginated extraction |
| Dataverse environment-level audit | ✅ PPAC > Audit and logs | ✅ Power Platform CLI / Dataverse Web API | Portal is the documented path |
| Per-table audit on Copilot Studio entities | ✅ Maker portal > Tables | ✅ Dataverse Web API | Portal preferred for the six-entity scope |
| `agentSignIn` log forwarding | ✅ Entra > Diagnostic settings | ✅ `New-AzDiagnosticSetting` | Portal recommended for first-time enablement |
| Azure immutable blob policy | ✅ Storage container > Access policy | ✅ `Set-AzStorageContainerImmutabilityPolicy` | Portal for initial creation; PowerShell for the **lock** action (audit-trail-friendly) |

Where this walkthrough invokes PowerShell, it does so for verification or for tasks the portal does not expose. Operational extraction at scale belongs in [PowerShell Setup](powershell-setup.md).

---

## §1 — Pre-Flight Gates (Run Before Any Configuration Change)

### 1.1 Roles required for this walkthrough

Use the canonical short names from the role catalog. Verify role assignments in Entra ID > Roles & administrators **and** in the Exchange admin center role groups.

| Task | Required role | Notes |
|---|---|---|
| Verify audit ingestion status | Purview Compliance Admin (with `View-Only Audit Logs`) or Entra Global Reader | Run `Get-AdminAuditLogConfig` from Exchange Online PowerShell |
| Enable unified audit logging | Purview Audit Admin (Exchange `Audit Logs` role) | Tenant-wide — change-managed |
| Search audit logs | Purview Compliance Admin or holder of `Audit Logs` / `View-Only Audit Logs` | Purview Audit solution |
| Author / modify audit retention policies | Exchange **Organization Configuration** role | **Purview Compliance Admin alone is NOT sufficient** for retention policy create/modify (per Microsoft Learn) |
| Enable Dataverse environment audit | Power Platform Admin (or Dynamics 365 Admin) | Per environment |
| Configure `agentSignIn` diagnostic forwarding | Entra Security Admin | Tenant-wide diagnostic setting |
| Configure Azure immutable blob storage | Azure Storage Account Owner / Contributor | Subscription-level RBAC |
| Approve PAYG cost commitment | Purview Audit Admin **plus** Azure subscription Owner | PAYG bills against an Azure subscription |

### 1.2 License inventory snapshot (mandatory first step)

Audit retention policies that exceed the entitlement of the underlying user **silently fail open at 180 days**. This is the single most common audit finding in US FSI tenants. Before authoring any retention policy:

1. Open `https://admin.microsoft.com` > **Billing > Licenses**.
2. Capture the assigned counts for each of: `Microsoft 365 E5`, `Office 365 E5`, `Microsoft Purview Suite`, `E5 eDiscovery and Audit add-on`, `10-Year Audit Log Retention add-on`.
3. Cross-reference against the user list assigned a Microsoft 365 Copilot license (any user without one of the four Audit Premium SKUs above caps at 180 days; any user assigned to a documented 10-year capture-window policy without the 10-Year add-on caps at 1 year).
4. Export the user × SKU × add-on matrix to CSV; SHA-256 hash and add to the evidence pack as `Control-1.7_{Tenant}_LicenseMatrix_{YYYYMMDD-UTC}.csv` plus `.sha256` sidecar.

### 1.3 Change-management gate

For any change to tenant-wide audit ingestion (§2), retention policy (§5), PAYG enablement (§6), or `agentSignIn` diagnostic forwarding (§9), open a change ticket that records:

- The pre-change state (the PowerShell verification output captured in §2.1).
- The intended post-change state.
- The named approver (typically the FSI Compliance Officer or Records Officer).
- The rollback step.
- The post-change verification timestamp and result.

---

## §2 — Verify (or Enable) Unified Audit Logging

### 2.1 Verify status first (do not assume)

Audit-on-by-default has applied to Microsoft 365 enterprise tenants since **January 2019**. It is **not** on by default for Business Basic / Business Standard / Business Premium SKUs or for unmanaged trial tenants. Before enabling, verify status:

```powershell
# Run from Exchange Online PowerShell — NOT Security & Compliance PowerShell
Connect-ExchangeOnline -ShowBanner:$false
Get-AdminAuditLogConfig | Format-List UnifiedAuditLogIngestionEnabled
```

- Expected for enterprise tenants: `UnifiedAuditLogIngestionEnabled : True`.
- Capture this output as evidence even if no change is required: `Control-1.7_{Tenant}_AuditConfig_{YYYYMMDD-UTC}.json` plus SHA-256 sidecar.

!!! warning "The same cmdlet from Security & Compliance PowerShell always returns `False`"
    Per Microsoft Learn, `Get-AdminAuditLogConfig` exists in both Exchange Online PowerShell and Security & Compliance PowerShell, but `UnifiedAuditLogIngestionEnabled` is **always reported as `False` from S&C PowerShell** regardless of true tenant state. Always run this check from Exchange Online PowerShell, and verify your active connection URI before trusting the result:

    ```powershell
    (Get-ConnectionInformation | Where-Object State -eq 'Connected').ConnectionUri
    # Expected: outlook.office365.com  (Commercial)
    # Expected: outlook.office365.com (commercial)
    # If URI is ps.compliance.protection.outlook.com, you are in S&C PowerShell — reconnect via EXO.
    ```

### 2.2 Enable if status is `False`

In the Microsoft Purview portal:

1. Open `https://purview.microsoft.com`.
2. From the left navigation, open the **Audit** solution.
3. If the **"Start recording user and admin activity"** banner is shown, click it.
4. Confirm the change in the §1.3 change-management ticket.
5. Wait up to 60 minutes for configuration propagation; ingestion of *events* into the audit log can take longer (Microsoft does not commit to a specific time).
6. Re-run the §2.1 verification and capture the post-change output as evidence.

---

## §3 — Search the Audit Log and Navigate from Record to Content

### 3.1 Run a Copilot / agent audit search

In the Purview portal:

1. Open **Audit > New search**.
2. Set **Date and time range (UTC)** for the period of interest. The portal search window is capped at **180 days**; for longer windows use PowerShell `Search-UnifiedAuditLog -SessionCommand ReturnLargeSet` paginated to completion, or the [Audit Search Graph API](https://learn.microsoft.com/en-us/purview/audit-search) (supported on both Audit Standard and Audit Premium).
3. In **Record types**, select the Copilot / agent types in scope:
    - `CopilotInteraction` — Microsoft 365 Copilot interactions.
    - `ConnectedAIAppInteraction` — Connected AI app interactions (Microsoft-built Copilot Studio agents at no incremental cost; some non-Microsoft AI app scenarios under this RecordType are PAYG-billable — see §6).
    - `AIAppInteraction` — Non-Microsoft AI assistance events captured via network/browser DLP under the `AIApp` workload (PAYG-only — see §6; 180-day retention for PAYG records).
    - `PowerPlatformAdministratorActivity` — Copilot Studio admin / agent lifecycle activity.
    - Power Platform: `PowerPlatformAdministratorActivity`, `MicrosoftFlow`, `PowerAppsApp` (as applicable).
4. Optionally filter by **Users**, **File, folder, or site**, or **Admin Units**.
5. Enter a **Search name** (e.g., `Q3-2026-FraudTriageAgent-Reconstruction`).
6. Click **Search**. Searches run **asynchronously**, search jobs persist for **30 days**, and there is a per-admin cap of **10 concurrent jobs (1 unfiltered)**. Refresh the search list to monitor completion.
7. When complete, **Export** results to CSV and immediately:
    - Compute SHA-256 over the CSV; save the hash sidecar.
    - Copy the CSV plus sidecar into the §10 immutable blob container within the search-job 30-day retention window.

!!! danger "`PowerPlatformAdminActivity` is NOT a valid RecordType"
    Earlier drafts of FSI playbooks used `-RecordType PowerPlatformAdminActivity`. That name is **not** in the published `AuditLogRecordType` enumeration. Some Exchange Online module versions silently return zero rows for invalid RecordType values, producing **false-clean evidence**. Use the names listed above and verify them at runtime via `[Enum]::GetNames([Microsoft.Office.CompliancePolicy.PSCmdlets.AuditRecordType])` before authoring any production search.

!!! warning "Activity vs operation vs record type"
    The Purview Audit search UI separates **friendly activity names**, **operation names**, **record types**, **workloads**, and the **search name** field. These are different fields with different valid values. Earlier drafts of this playbook listed activity-style names like `AgentCreated`, `AgentModified`, `AgentInteraction` — **these are not in the published Microsoft Learn schema** and will return zero results. Use the record-type names in step 3 above. To discover specific operation names, run a small RecordType search and inspect the `Operation` field of returned records.

### 3.2 From a `CopilotInteraction` audit record to the conversation content

The audit record carries metadata only. To retrieve the prompt and response body text, navigate to the appropriate content surface:

| Navigation goal | Portal path | Sibling control |
|---|---|---|
| Compliance manager wants to view chat transcripts for `CopilotInteraction` events | `https://purview.microsoft.com` > **DSPM for AI** > **Activity explorer** — locate the matching event by user, agent, and timestamp; open the activity to view the linked transcript surface | [Control 1.6](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md) |
| Legal needs to place hold, collect, and review Copilot interactions across custodians | `https://purview.microsoft.com` > **eDiscovery** > **Premium** > create case > add custodians > create hold > collection query targeting the Copilot interactions location for those custodians | [Control 1.19](../../../controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md) |
| Designated supervisor needs FINRA Rule 3110 supervisory review of AI-generated communications | `https://purview.microsoft.com` > **Communication Compliance** > **Policies** — confirm a policy is scoped to Copilot interactions; review hits in the **Pending review** queue | [Control 1.10](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md) |

> The audit record's `Messages[].ID` value is the join key the eDiscovery / DSPM surfaces use internally. Capture the audit record CSV alongside any content extract so the join is reproducible.

---

## §4 — Audit Standard vs Audit Premium vs 10-Year Add-On vs PAYG

| Feature | Audit Standard | Audit Premium (E5 / Purview Suite / E5 eDiscovery & Audit add-on) | 10-Year Audit Log Retention add-on | Audit PAYG |
|---|---|---|---|---|
| Default retention | 180 days (changed from 90 days on **2023-10-17**; pre-October-2023 records still 90-day) | 1-year non-modifiable default policy for `AzureActiveDirectory` / `Exchange` / `OneDrive` / `SharePoint` per E5 user | 10 years for any record explicitly named in a custom retention policy, per-user-licensed | **180 days** for PAYG-captured records |
| Custom retention policies (other workloads, including all Copilot record types) | ⛔ Not supported | ✅ Supported (per-user license required) | ✅ Required to extend any custom policy past 1 year | ⛔ PAYG records use the 180-day fixed retention |
| Up to 10-year retention | ⛔ | ⛔ (capped at 1 year without add-on) | ✅ | ⛔ |
| Audit Search Graph API | ✅ | ✅ | ✅ | ✅ |
| Higher-bandwidth Office 365 Management Activity API | Standard limit | Higher bandwidth per Learn | Same as Premium | Same as Premium |
| Intelligent insights / High-value events (e.g., `MailItemsAccessed`, `Send`) | ⛔ | ✅ | ✅ | n/a |
| Microsoft-built Copilot / Copilot Studio interaction events (`CopilotInteraction`, in-scope `ConnectedAIAppInteraction`) | ✅ at no incremental cost (verify per-workload scope on Learn) | ✅ | ✅ | n/a |
| `AIAppInteraction` for non-Microsoft AI apps (network/browser DLP `AIApp` workload) | ⛔ | ⛔ unless PAYG enabled | ⛔ unless PAYG enabled | ✅ — explicit enablement; 180-day retention; consumption billed against an Azure subscription |
| Per-user license required at event ingestion time | n/a (universal) | ✅ Yes — without it, retention silently caps at 180 days | ✅ Yes — without the add-on, retention silently caps at 1 year | n/a (PAYG fixed retention) |

**There is no native 3-year, 5-year, 6-year, or 7-year Audit tier.** Use the record-class schedule as the governing rule — 3 years for communications, 6 years for financial/accounting or governance records, 5 years for CFTC records, and longer only where a specific rule or the firm's records schedule requires it. If the firm wants a capture window beyond 1 year in Microsoft 365 Audit, configure a **10-year** custom retention policy only as a documented capture-window extension / over-retention choice.

---

## §5 — Create a Custom Audit Retention Policy

!!! danger "Required role: Organization Configuration"
    Authoring or modifying audit retention policies requires the Exchange **Organization Configuration** role. The Purview Compliance Admin role alone returns access denied on policy creation. Confirm role assignment before starting this step.

!!! warning "The default Audit (Premium) retention policy covers only four workloads"
    The platform default Audit (Premium) retention policy covers **only** `AzureActiveDirectory`, `Exchange`, `OneDrive`, and `SharePoint`. Copilot record types (`CopilotInteraction`, `ConnectedAIAppInteraction`, `PowerPlatformAdministratorActivity`, `AIAppInteraction`) silently fall back to **180 days** unless a custom policy explicitly names them. This is a non-obvious default — verify against [Microsoft Learn: Audit log retention policies](https://learn.microsoft.com/en-us/purview/audit-log-retention-policies) before you assume otherwise.

1. In the Purview portal Audit solution, open **Policies > Create audit retention policy**.
2. Enter a descriptive **Policy name** that encodes the zone and intent (e.g., `FSI-Zone3-Copilot-10y`, `FSI-Zone2-Copilot-1y`).
3. Set **Duration** to one of the supported values: `Three Months`, `Six Months`, `Nine Months`, `Twelve Months` (Audit Premium), `Ten Years` (Audit Premium + per-user 10-Year add-on). Apply the firm's record-class schedule — 3 years for communications, 6 years for financial/accounting or governance records, 5 years for CFTC records, and longer only where a specific rule or the firm's records schedule requires it — and use `Ten Years` only when the firm intentionally extends the Audit capture window beyond 1 year because Microsoft 365 Audit has no native intermediate tier for those record classes.
4. Under **Record types**, explicitly add **every** Copilot record type in scope:
    - `CopilotInteraction`
    - `ConnectedAIAppInteraction`
    - `AIAppInteraction` (only if PAYG enabled — note PAYG records cap at 180 days regardless)
    - `PowerPlatformAdministratorActivity`
    - `PowerPlatformAdministratorActivity`, `MicrosoftFlow`, `PowerAppsApp` (as applicable)
5. Under **Users**, choose **All users** for tenant-wide coverage, or scope to a **license-derived security group** (recommended pattern: scope by license group, not by individual UPN, because license assignments change).
6. Set **Priority** explicitly (1 = highest); document the priority decision in the policy description so the audit binder can explain conflict resolution.
7. Click **Save**.
8. Per-organization limit: **50 audit retention policies**. Reserve at least 10 slots for incident-response policies that may be added under examination.

---

## §6 — Enable PAYG for `AIAppInteraction` (If Non-Microsoft AI Apps Are in Scope)

`AIAppInteraction` (and certain `ConnectedAIAppInteraction` scenarios involving non-Microsoft AI apps surfaced via Connected AI App) are billed under Audit (Premium) **pay-as-you-go** and require explicit enablement. Without enablement, audit search returns **zero rows** for these record types and the firm has no audit evidence for non-Microsoft AI usage — a material gap if employees use non-Microsoft AI assistance from managed endpoints.

1. In the Purview portal, navigate to **Audit > Settings** and locate the AI app interaction PAYG enablement toggle. Verify the current location against [Microsoft Learn: Audit pay-as-you-go billing models](https://learn.microsoft.com/en-us/purview/purview-billing-models) at the time of configuration — the surface has shifted across recent UI revisions.
2. Confirm the PAYG cost commitment with the Azure subscription Owner; PAYG bills against an Azure subscription, not a per-seat license.
3. Enable the AI app interaction PAYG charge.
4. Document the enablement decision in the §1.3 change ticket and capture the confirmation screenshot.
5. Validate after the next ingestion window:

    ```powershell
    Search-UnifiedAuditLog -RecordType AIAppInteraction `
        -StartDate (Get-Date).AddDays(-1) -EndDate (Get-Date) -ResultSize 1
    ```

6. Note that PAYG-captured records are subject to **180-day retention** regardless of any custom retention policy — for longer preservation, export to the §10 immutable blob layer on a recurring schedule.

> **Note:** `AIAppInteraction` PAYG availability may vary. Verify against Microsoft Learn before relying on this capability.

---

## §7 — Dataverse Environment-Level and Per-Table Audit (Power Platform / Copilot Studio)

Required for Copilot Studio agent admin / lifecycle events to surface in `ConnectedAIAppInteraction` and for Fed SR 26-2 (formerly SR 11-7) model-lifecycle reconstruction.

### 7.1 Enable environment-level auditing (per environment)

1. Sign in to the Power Platform Admin Center (`admin.powerplatform.microsoft.com`).
2. Navigate to **Environments** > select the target environment.
3. Open **Settings** > expand **Audit and logs** > select **Audit settings**.
4. Toggle **Start Auditing** to **ON**.
5. Set **Retain these logs for**:
    - Zone 1 environments: minimum **180 days**.
    - Zone 2 environments: minimum **365 days**.
    - Zone 3 environments: minimum **730 days** (or **Custom** / **Forever** for longer).
6. Click **Save**.
7. Capture screenshot for the evidence pack.
8. **Repeat for every environment in the tenant.** Use the [Audit Compliance Manager](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/audit-compliance-manager) for tenant-wide automation.

### 7.2 Enable tenant-level Dataverse auditing policy

1. In PPAC > **Security > Compliance > Auditing**, enable **Turn on Auditing**.
2. Additionally enable the **User Sign-In** and **Activity** checkboxes to capture sign-in events and entity-level activity across all Dataverse environments.

### 7.3 Enable per-table audit on the six Copilot Studio entities

Even with environment-level audit enabled, agent-specific changes only surface when per-table audit is enabled on the Copilot Studio entities. The canonical six-entity set is:

1. `bot`
2. `botcomponent`
3. `botcomponentcollection`
4. `botpublishstatus` (or equivalent publish-state entity — verify the live name in your environment)
5. `botcomponentassociation`
6. `botactivelearningdialog` (or the current set documented by the audit-compliance-manager solution — verify before relying on the list)

For each of the six entities:

1. From the Power Apps Maker portal (`https://make.powerapps.com`), select the target environment.
2. Open **Tables** and locate the entity.
3. Open **Properties** and enable **Audit changes to its data**.
4. At the column level, confirm which fields generate audit events; enable column audit for any field tracked under the firm's records schedule.
5. Save and capture screenshot.

!!! warning "Dataverse before/after field values change — May 2026"
    Starting May 2026, Dataverse will no longer include before-and-after field change values in audit events sent to Microsoft Purview. Organizations requiring detailed field-level change data for regulatory recordkeeping should retrieve this data directly from the Dataverse Web API (`auditdetails` endpoint) or via Synapse Link audit export. This change may affect SEC 17a-4 / FINRA 4511 programs that rely on Purview audit integration for Dataverse field-level change records. Plan the transition before May 2026 and document the alternate retrieval pipeline in the audit binder.

---

## §8 — Entra Sign-In Telemetry for Agent Identities (Preview Surfaces)

### 8.1 Verify the live filter affordance before adding to runbooks

!!! danger "Filter chip naming has shifted across recent UI revisions"
    Earlier framework drafts referenced an `Is Agent = Yes` filter chip on the Entra sign-in logs page. **Do not hardcode that label.** As of the April 2026 verification window, the published Entra sign-in logs UI exposes four sign-in **types**:

    - **Interactive user sign-ins**
    - **Non-interactive user sign-ins**
    - **Service principal sign-ins**
    - **Managed identity sign-ins**

    plus a separate **Agent activity** log entry on the **Monitoring & health** page. The path-of-record and the filter labels are still evolving. **Verify the actual filter affordance in your tenant** before documenting it in any tenant-specific runbook, and re-verify each quarter.

Portal path:

```text
Microsoft Entra admin center
  > Identity > Monitoring & health > Sign-in logs
    (toggle between the four sign-in types)
  > Identity > Monitoring & health > Agent activity   (separate entry — verify label in your tenant)
```

### 8.2 Enable `agentSignIn` diagnostic forwarding (Preview)

The `agentSignIn` resource type is the preview category dedicated to authentication events performed by AI agent identities. Forward to a Log Analytics workspace for SIEM correlation (handed off to [Control 3.9](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md) for KQL detection authoring):

```text
Microsoft Entra admin center
  > Monitoring & health
    > Diagnostic settings
      > Add diagnostic setting
        > Check: agentSignIn
        > Destination: Log Analytics workspace / Storage account / Event Hub
```

!!! info "Preview feature — verify availability"
    The `agentSignIn` resource type is currently in preview. Configuration and field names may change before general availability. Verify availability in your tenant's Entra admin center surface; verify any access-prerequisite claims against Microsoft Learn or in your tenant.

### 8.3 Enable `MicrosoftServicePrincipalSignInLogs` (Preview, opt-in, high-volume)

```text
Microsoft Entra admin center
  > Monitoring & health
    > Diagnostic settings
      > Add diagnostic setting
        > Check: MicrosoftServicePrincipalSignInLogs
        > Destination: Log Analytics workspace / Storage account / Event Hub
```

!!! warning "High-volume stream — assess cost before enabling"
    `MicrosoftServicePrincipalSignInLogs` captures first-party Microsoft service-to-service token requests (Teams requesting Word resources, Copilot requesting agent APIs, M365 service orchestration calls). Volume can be significantly higher than standard sign-in logs. Enable only after assessing ingestion-cost impact on the Log Analytics workspace and SIEM. Recommended for tenants with complex M365 service orchestration or regulated Zone 3 agent workloads.

### 8.4 Confirm agent-correlation fields in the SIEM ingestion schema

The following Entra sign-in fields support agent-specific audit correlation. **`AppOwnerTenantId`, `ResourceOwnerTenantId`, `SessionId`, and `ASN` are long-standing fields** present on every user, service principal, and managed identity sign-in for years — they are not agent-specific or new. Confirm with the SIEM team that they are already in the ingestion schema before adding new mappings; only `SourceAppClientID` is reliably newer in the agent on-behalf-of (OBO) context.

| Attribute | Status | FSI use case |
|---|---|---|
| `AppOwnerTenantId` | Long-standing | Cross-tenant agent attribution |
| `ResourceOwnerTenantId` | Long-standing | Data-residency verification |
| `SessionId` | Long-standing | Session-level audit reconstruction |
| `SourceAppClientID` | Newer in agent OBO context | Agent identity-chain mapping |
| `ASN` | Long-standing | Geolocation and routing audit review |

---

## §9 — SIEM Integration

| Method | Use case |
|---|---|
| Microsoft Sentinel — Office 365 connector | Native ingestion to Sentinel; recommended for Zone 2/3. Detection-rule authoring is owned by [Control 3.9](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md). |
| Office 365 Management Activity API | Programmatic export at higher bandwidth (Audit Premium); preferred for high-volume tenants and for non-Sentinel SIEMs |
| Audit Search Graph API | Modern programmatic search path; supported on both Audit Standard and Audit Premium |
| Manual export | Ad-hoc investigations; subject to 30-day search-job retention and 50,000-record session ceiling |

**End-to-end ingestion latency:** Microsoft does not publish a hard SLA for audit availability. Empirically, core services (Exchange / SharePoint / OneDrive) typically appear within 60–90 minutes; Power Platform / Copilot Studio / Dataverse can take longer. Sentinel ingestion adds connector-poll latency on top. Treat any 5-minute / 15-minute SLA claim as fabricated unless cited to a specific Microsoft commitment.

**Verification procedure:** generate a known event (e.g., a single `CopilotInteraction` from a test account), record the exact UTC timestamp, and query the SIEM with a tight time window pinned to that timestamp after the documented latency ceiling. Capture the round-trip time and add to the §11 evidence pack as the documented end-to-end latency.

---

## §10 — Preservation Layer: Azure Immutable Blob Storage (or 17a-4-Attested Vendor)

Per the SEC's October 2022 amendments to Rule 17a-4(f) (compliance date 3 May 2023), broker-dealers may use either WORM storage or the audit-trail alternative for required record preservation. Microsoft 365 Audit alone — even with the 10-year add-on — does not satisfy 17a-4(f); preservation must come from one of:

| Option | Description | FSI applicability |
|---|---|---|
| **Azure Immutable Blob Storage** (time-based or legal hold, locked) | Export audit records and content extracts to an immutable container with a locked time-based retention policy. Cohasset-attested for SEC 17a-4(f), CFTC 1.31, and FINRA 4511. | Direct WORM equivalent; combine with chain-of-custody manifest |
| **Third-party 17a-4-attested archive** | Vendor with WORM or audit-trail compliance attestation: **Smarsh Enterprise Archive**, **Global Relay Archive**, **Proofpoint Enterprise Archive**, **Mimecast Cloud Archive**, **Bloomberg Vault**, **Veritas Enterprise Vault.cloud** | Verify vendor's 17a-4(f) third-party access undertaking is current; capture the attestation letter for the audit binder |
| Microsoft 365 Audit (Premium) with 10-year add-on | Native retention up to 10 years | **Capture layer only**; not a substitute for a 17a-4(f)-attested archive. Evaluate audit-trail-alternative sufficiency with compliance and legal counsel before relying on it standalone. |

### 10.1 Configure Azure Immutable Blob Storage (Cohasset-attested path)

1. In the Azure portal, create or select a storage account in an appropriate US Azure region.
2. Create a blob container dedicated to audit preservation (one container per record-class per retention horizon is recommended).
3. On the container, open **Access policy > Add policy > Time-based retention** (or **Legal hold** for litigation-bound records).
4. Set the retention period to the regulatory floor:
    - **3 years** for SEC 17a-4(b)(4) communications records (first 2 years readily accessible).
    - **5 years** for CFTC 1.31 regulatory records.
    - **6 years** for SEC 17a-4(a) financial / accounting records.
    - **Longer periods** only where a specific rule or the firm's records schedule requires them (for example, an OCC-driven or firm-standard over-retention decision may be documented separately).
    - **NYDFS 23 NYCRR 500.06** records retention obligation: minimum 5 years for cybersecurity-event records (verify against your firm's NYDFS program).
5. **Lock** the policy after validation — once locked, retention can be extended but never shortened or removed. The lock action itself is auditable via Azure Activity Log.
6. Capture the policy state and add to the evidence pack:

    ```powershell
    Get-AzStorageContainerImmutabilityPolicy -ResourceGroupName <rg> `
        -StorageAccountName <sa> -ContainerName <container>
    ```

7. Configure a recurring export from Purview Audit (and from DSPM for AI / eDiscovery for the content tier) to this container with a per-batch SHA-256 manifest. The manifest is the chain-of-custody artifact a 17a-4(f) attestation requires.

### 10.2 17a-4(f) audit-trail alternative — additional documentation

If the firm relies on the **audit-trail alternative** (rather than WORM), the §10 export pipeline must be accompanied by:

- **DEO representation** signed by a Designated Executive Officer **OR** a **DTP undertaking** signed by a Designated Third Party.
- **Independent records-management assessment** (typically by Cohasset Associates or equivalent) covering the end-to-end pipeline (capture → retention → export → preservation → retrieval).

These documents live outside Microsoft 365 — capture pointers to them in the §11 evidence pack so the audit binder is self-describing.

---

## §11 — Evidence Pack for FSI Examiners

Capture for every audit-binder refresh (cadence per [Verification & Testing](verification-testing.md) — typically monthly for Zone 1, weekly for Zone 2, daily for Zone 3):

1. **Tenant audit configuration** — output of `Get-AdminAuditLogConfig | Format-List` from Exchange Online PowerShell. Naming: `Control-1.7_{Tenant}_AuditConfig_{YYYYMMDD-UTC}.json` plus `.sha256` sidecar.
2. **License entitlement matrix** (§1.2) — user × SKU × add-on CSV. Required to support every retention attestation.
3. **Custom retention policies** — JSON export from `Get-UnifiedAuditLogRetentionPolicy | ConvertTo-Json -Depth 10`. Note in the binder that this **does not include** the platform default policy.
4. **PAYG enablement state** (§6) — confirmation screenshot plus a positive test result for `AIAppInteraction`.
5. **Per-environment Dataverse audit settings** (§7.1) — screenshot or API export per environment.
6. **Per-table audit state on the six Copilot Studio entities** (§7.3) — screenshot per entity per environment.
7. **`agentSignIn` and `MicrosoftServicePrincipalSignInLogs` diagnostic settings** (§8) — Entra portal screenshot plus the Log Analytics destination resource ID.
8. **Sample reconstruction artifact** — for one randomly selected agent, run a reconstruction search ("all `CopilotInteraction` records for `AgentId` X over date range Y–Z"), navigate from the audit hit to the **DSPM for AI** transcript surface (per §3.2), capture both, and bundle with a chain-of-custody manifest.
9. **Worked examiner example** — the canonical FINRA / SEC examiner question is *"Show me the audit trail and the underlying communications for AI-generated communications to customer X between dates Y and Z."* Maintain a current worked-example file showing: (a) the Purview Audit search filter, (b) the audit CSV export with SHA-256, (c) the DSPM for AI / eDiscovery content extract, and (d) the chain-of-custody manifest tying audit IDs to content IDs.
10. **WORM / immutability evidence** (§10) — output of `Get-AzStorageContainerImmutabilityPolicy` (or vendor equivalent); locked-state confirmation; pointer to DEO/DTP and Cohasset-equivalent assessment if relying on the audit-trail alternative.
11. **SIEM ingestion proof** (§9) — Sentinel query result showing the same event the audit search returned, with documented end-to-end latency.

All artifacts: SHA-256 hashed at capture time; copied to the §10 immutable blob container; referenced in the attestation statement (template in [Verification & Testing](verification-testing.md)).

---

## §12 — Zone-Specific Portal Workflows

### Zone 1 — Personal productivity agents

| Configuration | Setting |
|---|---|
| Unified audit logging | Enabled (verify per §2) |
| Audit retention policy | `Twelve Months` policy named `FSI-Zone1-Copilot-1y` covering `CopilotInteraction`, `ConnectedAIAppInteraction`, `PowerPlatformAdministratorActivity` |
| 10-Year Audit Log Retention add-on | Not required |
| PAYG `AIAppInteraction` | Optional; enable only if non-Microsoft AI is permitted on managed endpoints |
| Dataverse environment audit | Enabled, 180-day retention |
| Per-table audit on Copilot Studio entities | Enabled in default environment only |
| `agentSignIn` diagnostic forwarding | Recommended; not required |
| Azure immutable blob preservation | Optional |
| Review cadence | Monthly |
| Evidence pack refresh | Monthly |

### Zone 2 — Team / departmental shared agents

| Configuration | Setting |
|---|---|
| Unified audit logging | Enabled |
| Audit retention policy | `Twelve Months` (minimum) policy named `FSI-Zone2-Copilot-1y`; consider `Ten Years` for departments touching books-and-records data |
| 10-Year Audit Log Retention add-on | Required for any user whose interactions feed a documented 10-year capture-window policy |
| PAYG `AIAppInteraction` | Required if non-Microsoft AI is in scope |
| Dataverse environment audit | Enabled, 365-day retention, **all** non-default environments |
| Per-table audit on Copilot Studio entities | Required across all environments hosting shared agents |
| `agentSignIn` diagnostic forwarding | Required, forwarded to Log Analytics |
| Azure immutable blob preservation | Recommended |
| SIEM integration | Required |
| Review cadence | Weekly |
| Evidence pack refresh | Weekly |

### Zone 3 — Enterprise / regulated agents (broker-dealer, FCM, swap dealer, CPO, NYDFS-regulated)

| Configuration | Setting |
|---|---|
| Unified audit logging | Enabled |
| Audit retention policy | Record-class-based: apply the preservation schedule from Control 1.7 (3 years for communications, 6 years for financial/accounting or governance records, 5 years for CFTC records, and longer only where a specific rule or the firm's records schedule requires it). Because Microsoft 365 Audit has no native 3-year/5-year/6-year tier, firms that need a capture window beyond 1 year typically use a documented `Ten Years` policy as a capture-window extension / over-retention choice. |
| 10-Year Audit Log Retention add-on | Required only for users included in that documented 10-year capture-window scope; reconcile against the §1.2 license matrix on every binder refresh |
| PAYG `AIAppInteraction` | Required (non-Microsoft AI assumed in scope unless explicitly blocked by [Control 1.5](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md)) |
| Dataverse environment audit | Enabled, 730-day minimum retention (or **Forever**), all environments |
| Per-table audit on the six Copilot Studio entities | Required across all environments |
| `agentSignIn` diagnostic forwarding | Required |
| `MicrosoftServicePrincipalSignInLogs` | Evaluated and documented; enabled where ingestion-cost analysis supports it |
| Azure immutable blob preservation **OR** 17a-4-attested vendor | **Required** for broker-dealer / FCM / swap dealer / CPO; preservation horizon per the §10 regulatory floor table |
| SIEM integration | Required, with documented end-to-end latency |
| DSPM for AI ([1.6](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md)) / eDiscovery (Premium) ([1.19](../../../controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md)) / Communication Compliance ([1.10](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md)) | Required for content retrieval — audit alone does not preserve prompt/response text |
| Review cadence | Daily |
| Evidence pack refresh | Daily for capture verification; weekly for full binder refresh |
| Quarterly attestation (control owner + records officer + compliance officer) | Required |

---

## §13 — Implementation Notes

Implementation notes for US financial-services commercial tenants:
- **Azure immutable blob storage**: the **Cohasset attestation** and SEC 17a-4(f) coverage statement should be re-verified at vendor cadence (annually) and stored alongside the §11 evidence pack.

---

## §14 — Downstream Control Linkage

| Downstream control | Linkage |
|---|---|
| [1.5 — DLP and Sensitivity Labels](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) | DLP policy hits surface in audit; deny events from DLP feed the [Deny Event Correlation Report](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/deny-event-correlation-report) solution |
| [1.6 — DSPM for AI](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md) | Primary content-retrieval surface for `CopilotInteraction` audit hits |
| [1.10 — Communication Compliance](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md) | FINRA Rule 3110 supervisory-review surface for AI-generated communications captured in audit |
| [1.19 — eDiscovery (Premium) for Agent Interactions](../../../controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md) | Legal hold / collection / review surface for Copilot interactions; the audit `Messages[].ID` is the join key |
| [2.6 — Model Risk Management (OCC Bulletin 2026-13 (formerly OCC 2011-12) / Fed SR 26-2 (formerly SR 11-7))](../../../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md) | Model-card store referenced by `ModelTransparencyDetails.ModelProviderName` in audit; supplements the audit log where `ModelName` / `ModelVersion` are not populated for M365 Copilot |
| [2.12 — Supervision and Oversight (FINRA Rule 3110)](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) | Supervisory-review program that consumes the Comm Compliance hits driven by audit |
| [3.4 — Incident Reporting and Root-Cause Analysis](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) | Destination for any audit-pipeline gap discovered during a binder refresh |
| [3.9 — Microsoft Sentinel Integration](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md) | KQL detection authoring against forwarded audit, `agentSignIn`, and `MicrosoftServicePrincipalSignInLogs` data |

---

## §15 — Regulatory Cross-Reference

This walkthrough is designed to support compliance with the following — it does not, by itself, satisfy any of them. Each citation should be verified against the firm's own legal counsel's current interpretation before being relied upon in an examiner narrative.

| Citation | Relevance to this walkthrough |
|---|---|
| **FINRA Rule 4511** | Books-and-records retention. §5 (custom retention) + §10 (preservation layer) + §11 (evidence pack). |
| **FINRA Rule 3110** | Supervision of communications. Audit capture in §3 + content-tier handoff to [Control 1.10](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md) and [Control 2.12](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md). |
| **FINRA RN 25-07 (Request for Comment, April 2025)** | RFC on workplace modernization including AI-generated communications recordkeeping. **Not final guidance**; this walkthrough anticipates the direction of the RFC by capturing AI origin (`ApplicationId`, `AgentId`) and metadata that supports human vs AI attribution. Monitor for final-rule publication. |
| **SEC Rule 17a-3** | Record creation. Audit captures the *creation* events for required books and records. |
| **SEC Rule 17a-4(a)** | Financial / accounting records — 6-year retention. §10 retention floor table. |
| **SEC Rule 17a-4(b)(4)** | Communications records — 3-year retention (first 2 years readily accessible). Agent conversation logs typically qualify as communications. |
| **SEC Rule 17a-4(f) (October 2022 amendments, compliance date 3 May 2023)** | Permits WORM storage **OR** the audit-trail alternative with DEO/DTP and independent records-management assessment. §10 implements both options. |
| **SOX 302/404** | Internal controls over AI system logging. §11 evidence pack supports management certification. |
| **GLBA 501(b) / Safeguards Rule** | Security safeguards including audit trails for non-public personal information access. §3 + §11. |
| **OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12) / Federal Reserve SR 26-2 (formerly SR 11-7)** | Model risk management — model identity, version, and use must be auditable. Audit captures `ModelProviderName`; full model identification supplemented by the Control 2.6 model-card store (audit log alone does **not** satisfy Fed SR 26-2 (formerly SR 11-7) model inventories for M365 Copilot). |
| **CFTC Rule 1.31** | 5-year retention of regulatory records (FCMs, swap dealers, CPOs) in tamper-evident format with complete metadata. §10 retention floor. |
| **NYDFS 23 NYCRR 500.06** | Records retention for cybersecurity events — 5 years. §10 retention floor. |
| **NYDFS 500.16** | Incident response plan — supported by the §11 evidence pack and the [3.4](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) handoff. |
| **NYDFS 500.17** | Notice of cybersecurity event to the Department within 72 hours — audit evidence supports the required reconstruction. |
| **FFIEC IT Examination Handbook** | Information security audit-trail expectations — §11 evidence pack designed to map. |
| **IRS Rev. Proc. 97-22 / 98-25** | Electronic record retention for tax purposes — §10 immutable blob layer supports the records-integrity requirements. |

---

## §16 — Anti-Pattern Catalog

| Anti-pattern | Why it fails | Correct approach |
|---|---|---|
| Treating Microsoft 365 Audit (Premium) + 10-year add-on as a 17a-4(f)-compliant preservation system | The 10-year add-on extends capture; it does not constitute non-rewriteable, non-erasable storage with a DEO/DTP undertaking | Pair audit with §10 preservation layer (Azure immutable blob or 17a-4-attested vendor) |
| Telling an examiner "the audit log preserves the AI conversation" | The audit record carries metadata only; prompt/response text lives in the Substrate | Always pair audit evidence with the matching content extract from DSPM for AI / eDiscovery / Comm Compliance |
| Authoring a 10-year custom retention policy without checking the per-user 10-Year add-on assignment | Records silently cap at 1 year for users without the add-on | §1.2 license matrix is mandatory before §5 |
| Running `Get-AdminAuditLogConfig` from Security & Compliance PowerShell | Always returns `False` regardless of true tenant state | Run from Exchange Online PowerShell only; verify the connection URI |
| Using `-RecordType PowerPlatformAdminActivity` | Not a valid `AuditLogRecordType`; some module versions silently return zero rows | Use the names in §3.1 and validate against `[Enum]::GetNames(...)` |
| Hardcoding `Is Agent = Yes` in an Entra sign-in runbook | The filter chip naming has shifted across recent UI revisions | §8.1 — verify the live filter affordance each quarter |
| Enabling `MicrosoftServicePrincipalSignInLogs` without a cost assessment | High volume can dwarf the rest of the Log Analytics workspace | §8.3 — assess ingestion cost first |
| Assuming default Audit (Premium) retention covers Copilot record types | Default policy covers only AzureActiveDirectory / Exchange / OneDrive / SharePoint | §5 — explicitly name every Copilot record type in a custom policy |
| Forgetting to enable per-table audit on the Copilot Studio entities after enabling environment-level audit | Agent admin events do not surface in `ConnectedAIAppInteraction` | §7.3 — six-entity per-table enablement |
| Relying on a single-shot `Search-UnifiedAuditLog -ResultSize` | Truncates silently past the session ceiling | Use `-SessionCommand ReturnLargeSet -SessionId <guid>` paginated to completion (per [PowerShell Setup](powershell-setup.md)) |
| Using "ensures compliance" / "guarantees" / "prevents" / "eliminates" in any control narrative | Overclaim — invites finding | Use the hedged-language alternatives in the Hedged-Language Reminder above |

---

## §17 — Verification Handoff

After completing this walkthrough, hand off to [Verification & Testing](verification-testing.md) to execute the full verification criteria from the control document, including:

1. Unified audit logging enabled (run `Get-AdminAuditLogConfig | Format-List UnifiedAuditLogIngestionEnabled` from Exchange Online PowerShell).
2. Audit (Premium) license entitlement verified per Copilot user.
3. Per-user 10-Year Audit Log Retention add-on assigned for every user included in a documented 10-year capture-window policy.
4. Copilot record types appear in audit search results.
5. Custom audit retention policies explicitly include the Copilot record types.
6. Retention policies configured per governance tier.
7. Export capability produces complete records using paginated `ReturnLargeSet`.
8. SIEM integration functional with documented end-to-end ingestion latency.
9. WORM storage **or** audit-trail alternative configured per SEC 17a-4(f).
10. Dataverse environment-level audit enabled across all environments.
11. Per-table Dataverse audit enabled on the six Copilot Studio entities.
12. Audit log retention set to a minimum of 180 days per environment.
13. `agentSignIn` logging enabled / validated for Zone 2 and Zone 3.
14. Agent-correlation sign-in fields confirmed present in the SIEM ingestion schema.
15. `MicrosoftServicePrincipalSignInLogs` evaluated and documented for Zone 3.
16. Evidence-pack capture procedure produces named, hashed, immutable artifacts.

---

## §18 — Troubleshooting Handoff

For common failure modes (audit-search-returns-zero, retention-silently-falls-back-to-180-days, PowerShell connection-URI mismatch, Dataverse per-table audit not surfacing, `agentSignIn` not appearing in Log Analytics, immutable-blob policy lock errors), see [Troubleshooting](troubleshooting.md).

---

[Back to Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) | [PowerShell Setup](powershell-setup.md) | [Verification & Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
