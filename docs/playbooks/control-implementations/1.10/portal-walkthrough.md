# Control 1.10 — Portal Walkthrough: Communication Compliance Monitoring

**Control:** [1.10 Communication Compliance Monitoring](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md)
**Audience:** M365 administrator (US financial services)
**Last UI Verified:** April 2026
**Cloud coverage:** Commercial · GCC · GCC High · DoD (see sovereign cloud table below)
**Estimated Time:** 4–8 hours (excludes Teams/Exchange processing windows and pilot validation)

> This playbook provides portal configuration guidance for [Control 1.10](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md). It is written to support compliance with FINRA Rule 3110 (supervision), FINRA Rule 4511 (books and records), SEC Rule 17a-4 (record retention), SEC Rule 17a-3 (record creation), and CFTC Rule 1.31. Communication Compliance is a **detection and review** control. By itself it does not satisfy any single regulatory obligation — records retention is implemented separately under [Control 1.9](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md), and incident handling is governed by your firm's supervisory procedures.

---

!!! warning "Read the boundary before you begin"
    Communication Compliance (CC) **scans message content** for policy-relevant patterns and routes matches to a supervisory review queue. It is **not** a records-retention vault, **not** a message-encryption product, and **not** a substitute for eDiscovery or Insider Risk Management.

    | If you need to … | Use … |
    |---|---|
    | Retain `SupervisionRuleMatch` / `SupervisoryReviewTag` history under WORM | Records retention — [Control 1.9](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md) |
    | Investigate a non-supervisory data exfiltration risk | Insider Risk Management — [Control 1.12](../../../controls/pillar-1-security/1.12-insider-risk-detection-and-response.md) |
    | Encrypt or rights-protect a message | Microsoft Purview Message Encryption / IRM (out of scope here) |
    | Search across mailboxes for legal hold / production | eDiscovery — [Control 1.19](../../../controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md) |
    | Block content from being sent or shared with AI | DLP — [Control 1.5](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) |

    Encrypted / rights-protected messages: Communication Compliance scans the **decrypted content** that the service can resolve through indexing. Messages whose content the service cannot resolve (third-party encryption, BYOK with restrictive policies) will not surface meaningful matches — route those to Microsoft Purview Message Encryption / IRM.

---

## Sovereign Cloud Availability

| Cloud | Portal URL | Communication Compliance | Copilot interactions template | Content safety classifiers (Hate / Violence / Sexual / Self-harm) | PAYG for non-M365 AI |
|---|---|---|---|---|---|
| Commercial | `https://purview.microsoft.com` | GA | GA | GA (Teams) | GA |
| GCC | `https://purview.microsoft.com` | GA | GA (verify per Microsoft 365 roadmap) | GA (Teams) | GA |
| GCC High | `https://purview.microsoft.us` | GA | Limited — verify against current Learn before relying on it | Limited; some classifiers preview-only or not at parity | Limited — verify Azure dependency availability for the tenant region |
| DoD | `https://purview.microsoft.us` (DoD instance) | GA | Limited — verify against current Learn before relying on it | Limited; some classifiers preview-only or not at parity | Limited — verify Azure dependency availability for the tenant region |

> Communication Compliance availability depends on **Azure service dependencies** in the tenant's geography. Before relying on a feature in GCC / GCC High / DoD, verify against [Azure dependency availability by country/region](https://learn.microsoft.com/en-us/troubleshoot/azure/general/dependency-availability-by-country) and the Microsoft 365 Roadmap. Record any cloud-specific gap in your Zone-3 exception register.

For PowerShell parity see `docs/playbooks/_shared/powershell-baseline.md`. **Note:** PowerShell is **not supported** for creating or managing Communication Compliance policies — all policy configuration is portal-only. PowerShell is used here only for prerequisites (audit log, distribution groups, compliance security filters) and validation (audit search).

---

## Prerequisites

Complete every item in this section **before** opening the policy wizard. A missed prerequisite is the most common cause of a CC policy that "looks created" in the portal but produces zero alerts.

### 1. License entitlement

Per current Microsoft Learn, Communication Compliance is included in:

- **Microsoft 365 E5** or **Office 365 E5**
- **Microsoft 365 E5 Compliance** add-on
- **Microsoft 365 E5 Insider Risk Management** add-on
- **Microsoft Purview Suite** per-user license
- Per-user standalone Communication Compliance licensing for users in the Government Community Cloud where applicable

Per-user licensing is **required for every monitored user** (the user whose communications are scanned), not just for administrators or reviewers. Verify entitlement against the [current Microsoft 365 service description](https://learn.microsoft.com/en-us/office365/servicedescriptions/microsoft-365-service-descriptions/microsoft-365-tenantlevel-services-licensing-guidance) before each material change window — Microsoft licensing for compliance products has changed multiple times. Do not oversimplify in your evidence pack.

### 2. Enable the Unified Audit Log

Communication Compliance **requires** the Unified Audit Log (UAL) to display alerts and to log reviewer remediation actions (Resolve, Tag, Escalate, Notify, Remove). If UAL is off, policies appear to create successfully but produce no alerts and no reviewer actions are logged — a silent supervisory-system gap under FINRA 3110.

UAL has been on by default in all new Microsoft 365 tenants since 2023, but verify state explicitly. Detect first; only mutate if disabled.

**Detect from Exchange Online PowerShell:**

```powershell
# Run from Windows PowerShell 5.1 or PowerShell 7 with ExchangeOnlineManagement
# pinned per docs/playbooks/_shared/powershell-baseline.md §1
Connect-ExchangeOnline
(Get-AdminAuditLogConfig).UnifiedAuditLogIngestionEnabled
```

A return value of `True` is required. The same property surfaced through Security & Compliance PowerShell (IPPS) is unreliable — always read it from Exchange Online PowerShell.

**If `False`, enable from a holder of an Exchange role group** (Organization Management, Compliance Management, or Records Management):

```powershell
Set-AdminAuditLogConfig -UnifiedAuditLogIngestionEnabled $true
```

**Or from the portal:** Microsoft Defender portal → **Audit** → **Start recording user and admin activity**.

After enabling, allow up to several hours for ingestion to complete. Record the change in your CAB ticket and capture the `Get-AdminAuditLogConfig` JSON output as evidence.

### 3. Reviewer prerequisite — Exchange Online mailboxes

**Every reviewer assigned to a CC policy must have an Exchange Online mailbox.** Reviewers are individual users, not distribution groups. When you add a reviewer to a policy, the service automatically sends them a notification email — if they do not have an Exchange Online mailbox, policy creation fails or the reviewer never receives the queue assignment.

For reviewers with on-premises mailboxes (hybrid Exchange tenants), migrate the reviewer mailbox to Exchange Online before assignment. Document the mailbox state for each reviewer in your role-assignment evidence.

### 4. Pay-as-you-go (PAYG) billing — required for non-M365 AI scope

Any policy whose **Locations** include **Enterprise AI apps**, **Other AI apps**, or non-Microsoft 365 generative AI data (Copilot in Fabric, Microsoft Security Copilot, connected external AI applications, Copilot Studio non-M365 content) requires **Microsoft Purview pay-as-you-go (PAYG) billing** linked to an Azure subscription. The **Microsoft Copilot experiences** location (M365 Copilot and Copilot Chat) does **not** require PAYG.

PAYG is also required for **OCR processing** on policy attachments (see Step 5).

Configure PAYG per [Microsoft Purview billing models](https://learn.microsoft.com/en-us/purview/purview-billing-models). Track PAYG usage in the **Purview Usage center**. Without PAYG enabled, the non-M365 AI locations either do not appear in the wizard or silently produce zero matches — a classic "false-clean" trap on your evidence pack.

### 5. Role group assignment (Communication Compliance)

Decide between Option 1 (single catch-all `Communication Compliance` group) and Option 2 (segmented role groups for separation of duties) before the first policy is created. See **Step 2** for the detailed assignment procedure and the canonical role-group inventory.

### 6. Distribution groups for scoped users

Create **distribution groups** (not Microsoft 365 Groups, not dynamic distribution groups, not nested distribution groups, not mail-enabled security groups for scoped users) to represent each monitored population (e.g., `dg-cc-registered-reps`, `dg-cc-investment-advisers`, `dg-cc-copilot-pilot`). The behavior differs by group type:

| Group type | Behavior when used as a **scoped user** group |
|---|---|
| Distribution group | **Recommended.** Detects all emails and Teams chats from each user in the group |
| Microsoft 365 Group | Detects only messages **sent to** the group, not individual messages from members |
| Mail-enabled security group | Supported, but membership semantics vary — verify before relying on it |
| Dynamic distribution group | **Not supported** for scoped users |
| Nested distribution group | **Not supported** for scoped users |

For reviewer fields, individual users are required (no group types are supported for reviewers).

For tenants with on-premises Exchange or external mail providers, see the Microsoft Learn [Configure Communication Compliance](https://learn.microsoft.com/en-us/purview/communication-compliance-configure) guidance for the cloud-based-storage requirement to detect Teams chats for those users.

### 7. Custom SITs (if referenced in policy conditions)

If you intend to use custom Sensitive Information Types (e.g., MNPI Indicators, customer account number patterns, FINRA-specific patterns) inside any CC policy, **create them first under [Control 1.13](../../../controls/pillar-1-security/1.13-sensitive-information-types-sits-and-pattern-recognition.md)** with documented confidence threshold and proximity. Do **not** assume a SIT exists — referencing a non-existent SIT is a silent failure mode.

---

## Step 1 — Verify and document Pseudonymization (privacy default)

Communication Compliance is built **privacy-by-design**. Usernames are **pseudonymized by default** in alert and message review surfaces — reviewers see anonymized aliases instead of real user identities. This is a required default in many works-council and EU-data-residency contexts and is a defensible baseline for FSI under GLBA 501(b) and state privacy regimes.

**Investigators must be opted in by an admin** to view non-anonymized identities in the Conversation and Translation tabs and to take advanced remediation actions.

### Verify the default

1. Sign in to the [Microsoft Purview portal](https://purview.microsoft.com) (or the sovereign URL from the table above)
2. Open the **Communication Compliance** solution
3. Select **Settings** in the upper-right corner of the page
4. Select **Communication Compliance** → **Privacy** tab
5. Confirm the **Show anonymized versions of usernames** toggle is **On** (the default)
6. Capture a timestamped screenshot for evidence

### Opt out (only with documented justification)

If your firm's policy requires non-pseudonymized review (rare; typically only for named insider-risk investigations under HR/Legal direction):

1. On the **Privacy** tab, clear the **Show anonymized versions of usernames** checkbox
2. Save
3. **Required evidence to commit to the change ticket:**
   - Admin who made the change (Entra UPN)
   - Business justification (Compliance / HR / Legal sign-off)
   - Effective date and expected duration
   - Population of investigators who will see non-pseudonymized identities
   - Audit-log row for the configuration change (search the UAL for the `Set-` activity on the CC privacy setting)

Re-enable pseudonymization at the documented end date. The opt-out is **a privileged action and must be auditable**.

### Investigator opt-in

The **Communication Compliance Investigators** role group has the highest content-visibility surface (Conversation tab, Translation tab, message details report, message download). Investigator membership is **opt-in by an admin** — adding a user to this role group is a deliberate elevation, not an automatic consequence of being in another role group. Document each Investigator addition with: who added, who was added, business justification, and effective date.

---

## Step 2 — Configure role groups (correct Permissions navigation)

> **Portal navigation (verify before each session — it has changed):** Microsoft Purview portal → **Settings** (upper-right) → **Roles & scopes** → **Permissions** → **Microsoft Purview solutions** → **Communication compliance** → **Role groups**.
>
> The path is **Role groups**, not "Roles". A common cause of "I assigned the role but the user can't see CC" is assigning at the wrong level.

### Canonical role group inventory

There are **six** Communication Compliance role groups. Use the **plural** names exactly as they appear in the portal — synonyms ("CC Admins", "Comms Compliance Investigator") will not match audit-log queries.

| Role group (canonical name) | Configure policies & settings | Access & investigate alerts | Advanced remediation (escalate, remove Teams msg, download, run flows) | Access reports | View Conversation / Translation tabs |
|---|---|---|---|---|---|
| **Communication Compliance** (catch-all) | Yes | Yes | Yes | Yes | Yes |
| **Communication Compliance Admins** | Yes | No | No | No | No |
| **Communication Compliance Analysts** | No | Yes | No | No | No |
| **Communication Compliance Investigators** | No | Yes | Yes | No | Yes |
| **Communication Compliance Viewers** | No | No | No | Yes | No |

> The **Communication Compliance** role group is the catch-all (everything). Use it only for very small teams or pilot deployments. For FSI separation-of-duties, prefer Option 2 (segmented assignment).

### Option 1 — Single catch-all assignment (small teams / pilot)

1. Settings → **Roles and groups** → **Role groups**
2. Select the **Communication Compliance** role group → **Edit**
3. **Choose users** → select the users → **Select** → **Next**
4. **Save** → **Done**

### Option 2 — Segmented assignment (recommended for FSI)

Map your firm's compliance roles to the four specific role groups. A typical FSI mapping:

| Firm role | Assigned to (role group) | Rationale |
|---|---|---|
| Compliance team lead / WSP owner | Communication Compliance Admins | Policy & settings authority; no alert content visibility (separation of duties) |
| Frontline supervisory analyst | Communication Compliance Analysts | Triage and resolve alerts; cannot configure policy or download messages |
| Senior compliance investigator (FINRA-registered principal) | Communication Compliance Investigators | Advanced remediation, Conversation / Translation, message download |
| Internal Audit / SOX | Communication Compliance Viewers | Read-only reports for periodic audit reviews |

For each role group:

1. Settings → **Roles and groups** → **Role groups**
2. Select the role group → **Edit**
3. **Choose users** → add users → **Select** → **Next** → **Save**
4. Repeat for the next role group → **Close** when done

> **Always maintain at least one user** in either the **Communication Compliance** or **Communication Compliance Admins** role group to avoid a "zero administrator" lockout if a leaver removes the only configured admin.

### Propagation note

After assignment, **role propagation can take up to 30 minutes** to apply across the organization. If a newly assigned user reports they cannot see the CC menu, wait 30 minutes before troubleshooting.

### Avoid Global Admin

Holders of **Microsoft Entra Global Admin** or **Compliance Administrator** automatically inherit `Communication Compliance Admins` permissions. Do **not** rely on Global Admin for routine CC operations — minimize Global Admin holders per [Microsoft's least-privilege guidance](https://learn.microsoft.com/en-us/purview/purview-permissions). Assign workload-specific role groups instead.

---

## Step 3 — Plan and apply Administrative Units for reviewer scoping

For multi-region or multi-business-unit firms (a US broker-dealer with a German broker-dealer subsidiary; a parent bank with a separately-supervised RIA arm; an FCM with a swap-dealer affiliate), a single tenant-wide reviewer population is rarely defensible. Reviewers in one jurisdiction should not see content from users in another.

**Administrative Units (AUs) scope CC role-group members to specific user populations.**

### Plan first — what AUs scope and what they don't

| Scoped by AU | Not scoped by AU |
|---|---|
| Access and investigate alerts (for Communication Compliance, Analysts, Investigators role groups) | Access reports |
| Configure policies (for Communication Compliance, Admins role groups) | Configure settings (including notice templates) |
| | View and export audit logs |

Effects matrix per role group when AU scoping is enforced:

| Task | Scoped CC | Scoped CC Admins | Scoped CC Analysts | Scoped CC Investigators | Scoped CC Viewers |
|---|---|---|---|---|---|
| Access & investigate alerts | Scoped | No | Scoped | Scoped | No |
| Access reports | No | No | No | No | No |
| Configure policies | Scoped | Scoped | No | No | No |
| Configure settings | No | No | No | No | No |

> AUs and **adaptive scopes** **cannot be combined** in CC. Pick one. SharePoint sites and inactive mailboxes are out of scope for AU segmentation in CC.

### Apply

1. Create the AU per [Purview administrative units](https://learn.microsoft.com/en-us/purview/purview-admin-units) if it does not already exist (typically scoped to an Entra group representing the regulated population)
2. Assign the AU to the CC role group member(s) per the same Microsoft Learn procedure
3. The assigned member becomes a **restricted administrator** — they see only alerts/policies for users inside the AU
4. Members **without** an AU assignment remain **unrestricted administrators** with full-tenant visibility. Document this distinction for each role-group member in your evidence pack
5. When you create a CC policy under Step 4 below, scope the policy to the same AU on the **Admin units (preview)** page of the policy wizard

### FSI mapping example

| Firm scope | AU (Entra group source) | Role group member assigned to AU |
|---|---|---|
| US broker-dealer registered reps | `aug-bd-us-regreps` | US Compliance Investigators |
| EU MiFID II investment firm | `aug-mifid-eu` | EU Compliance Investigators |
| Swap dealer (CFTC) | `aug-cftc-swap-dealer` | CFTC Compliance Analysts |
| RIA affiliate (SEC IA) | `aug-ria-affiliate` | RIA Compliance Investigators |

---

## Step 4 — Create per-template policies

> **Templates are template-locked.** When you create a policy from a template, the **Locations**, **Direction**, and **Conditions** are pre-set and **cannot be changed** in the wizard. The template list is your menu — pick the right template for the supervisory scenario, or use **Custom policy** for free-form configuration. Do not assume "I can add Exchange to the Inappropriate content template" — you cannot.
>
> Per current Microsoft Learn, the seven templates are: **Conflict of interest**, **Copilot interactions** (`Detect Microsoft 365 Copilot and Microsoft 365 Copilot Chat interactions`), **Inappropriate content**, **Inappropriate images**, **Inappropriate text**, **Regulatory compliance** (`Detect financial regulatory compliance`), and **Sensitive information**. There is **no separate "Customer complaints" template** — Customer complaints is a **classifier** inside the Regulatory compliance template.

### Common policy creation entry path

For every template below:

1. Sign in to the Microsoft Purview portal (sovereign URL from the table above)
2. Open the **Communication Compliance** solution
3. Select **Policies** in the left navigation
4. Select **Create policy** → choose the template
5. In the right-side pane:
   - Set the **Policy name** (cannot be changed after creation — name carefully, e.g., `FSI-CC-RegComp-USBD-100pct-2026Q2`)
   - Set **Users or groups in scope** (use the distribution groups from Prerequisites #6)
   - Set **Reviewers** (individual users with Exchange Online mailboxes)
   - Optional: select **Customize policy** to expose OCR, review-percentage adjustments, and other tunable conditions
6. **Create policy**

### Policy A — Inappropriate text (FSI baseline supervisory)

| Property | Template-locked value |
|---|---|
| Locations | Exchange Online, Microsoft Teams, Viva Engage |
| Direction | Inbound, Outbound, Internal |
| Default review percentage | 100% |
| Conditions | Threat, Discrimination, Targeted harassment classifiers |

**Tunable in Customize policy:** Reviewer set, scoped users, OCR checkbox, review percentage (do **not** lower below the percentage demanded by your supervisory procedures).

**Recommended FSI configuration:**

- Scoped users: all employees in scope of FINRA 3110 supervision (a tenant-wide distribution group is acceptable; for an AU-scoped firm, use the AU)
- Reviewers: registered principals (Series 24 / 9-10 / 16) per your WSP
- Direction: keep all three (Inbound / Outbound / Internal)
- Review percentage: keep at **100%** for FSI

### Policy B — Regulatory compliance (the FSI workhorse — tune review percentage)

| Property | Template-locked value |
|---|---|
| Locations | Exchange Online, Microsoft Teams, Viva Engage |
| Direction | Inbound, Outbound |
| **Default review percentage** | **10%** |
| Conditions | Customer complaints, Gifts & entertainment, Money laundering, Regulatory collusion, Stock manipulation, Unauthorized disclosure classifiers |

**Critical FSI tuning — increase review percentage to 100% for supervised populations.** The 10% default is acceptable for general detection but **does not meet** FINRA 3110 supervisory expectations for registered representatives. For populations subject to written supervisory procedures (registered reps, investment advisers, swap dealers, FCM associated persons), tune to **100%**:

1. On the wizard, select **Customize policy**
2. On the **Choose conditions and review percentage** page, drag the **Review percentage** slider to **100**
3. Document the rationale in the change ticket (e.g., "FINRA 3110 supervised population; 100% review per WSP §X.Y")

> **Customer complaints is a classifier inside this template, not a standalone template.** If you need it as a separately tracked queue, create a second `Regulatory compliance` policy scoped to a specific population and reviewer set.

**Recommended FSI configuration:**

- Scoped users: distinct distribution groups per supervised population (registered reps, IA reps, swap-dealer APs)
- Reviewers: registered principals with the appropriate qualification per population
- Direction: Inbound + Outbound (template-locked)
- Review percentage: **100%** for supervised populations; document any population kept at 10% with risk-based justification
- Complaint workflow: apply a firm-defined AI-customer-complaint tag, record the message ID or Copilot conversation reference in the case note, and route tagged alerts to the Compliance Officer's FINRA Rule 4530(d) quarterly complaint register

### Policy C — Copilot interactions (the AI-monitoring template)

> **Use this template for AI prompt/response supervision.** Do not attempt to retrofit Inappropriate content or Inappropriate text to Copilot — those templates do not include the Copilot location and they do not auto-configure the AI-specific safety classifiers.

| Property | Template-locked value |
|---|---|
| Location | Microsoft 365 Copilot and Microsoft 365 Copilot Chat |
| Direction | Inbound, Outbound, Internal |
| Default review percentage | 100% |
| Conditions | **Prompt Shields** + **Protected material** classifiers (auto-configured) |

The full template name in the portal is **"Detect Microsoft 365 Copilot and Microsoft 365 Copilot Chat interactions"**.

**Tunable in Customize policy:** Reviewer set, scoped users, additional classifiers / SITs / keywords, review percentage.

**Recommended FSI configuration:**

- Scoped users: every user with a Microsoft 365 Copilot per-user license, plus any non-licensed user expected to use Copilot Chat (the broader entitlement). Reconcile against your Copilot per-user license inventory (Control 1.6 / Control 2.16 agent inventory)
- Reviewers: AI Governance Lead + Compliance Analyst rotation
- Review percentage: keep at **100%** (Copilot interactions are a new-and-evolving supervisory surface; sample only after a documented period of stable false-positive rates)
- Optional add-ons in Customize policy: custom SITs created under Control 1.13 (e.g., MNPI indicators), custom keyword dictionaries (e.g., "guaranteed return", "risk-free", "inside information"), and Microsoft trainable classifiers as needed

> For monitoring of **non-Microsoft AI applications** (Enterprise AI apps, Other AI apps, ChatGPT Enterprise via connectors, Copilot in Fabric, Microsoft Security Copilot), create a **Custom policy** (templates are locked to specific locations) and ensure **PAYG billing is enabled** (Prerequisites #4). Without PAYG, those locations either do not appear or produce zero matches.

### Policy D — Sensitive information

| Property | Template-locked value |
|---|---|
| Locations | Exchange Online, Microsoft Teams, Viva Engage |
| Direction | Inbound, Outbound, Internal |
| Default review percentage | 10% |
| Conditions | Sensitive information, OOB content patterns and types, custom dictionary option, attachments larger than 1 MB |

**Recommended FSI configuration:**

- Scoped users: full firm or population-specific, depending on customer-data exposure
- Reviewers: data-protection or privacy team
- Direction: Outbound is the priority (data-leak direction); keep Inbound and Internal unless tuned for a specific scenario
- Conditions: include the relevant out-of-the-box SITs (US Social Security Number, Credit Card Number, US Bank Account Number) **plus** the custom SITs you created under Control 1.13 (customer account number, MNPI indicators)
- Review percentage: tune up from 10% based on observed match volume; for a high-risk population, set to 100%

### Policy E — Inappropriate images

| Property | Template-locked value |
|---|---|
| Locations | Exchange Online, Microsoft Teams |
| Direction | Inbound, Outbound, Internal |
| Default review percentage | 100% |
| Conditions | Adult and Racy image classifiers |

**Recommended FSI configuration:**

- Scoped users: full firm
- Reviewers: HR + Compliance
- Note: To detect text printed or handwritten **inside** images attached to messages (e.g., a screenshot of a rate-sheet, a photo of a customer document), enable **OCR** in **Customize policy** on the Conditions page (Step 5 below). OCR is **not** automatic for this template.

### Policy F — Inappropriate content

| Property | Template-locked value |
|---|---|
| Locations | **Microsoft Teams, Viva Engage only** (does **not** include Exchange and does **not** include Copilot) |
| Direction | Inbound, Outbound, Internal |
| Default review percentage | 100% |
| Conditions | **Hate, Violence, Sexual, Self-harm** content-safety classifiers (Azure AI Content Safety, LLM-based) |

> **Common misconception:** "Inappropriate content" sounds like the all-purpose template. It is **not**. It is locked to Teams + Viva Engage and uses the LLM-based content-safety classifiers. For Exchange / harassment / discrimination, use **Inappropriate text**. For Copilot, use **Copilot interactions**.

**Recommended FSI configuration:**

- Scoped users: full firm
- Reviewers: HR + Compliance
- Direction: keep all three

### Policy G — Conflict of interest

| Property | Template-locked value |
|---|---|
| Locations | Exchange Online, Microsoft Teams, Viva Engage |
| Direction | **Internal only** |
| Default review percentage | 100% |
| Conditions | None (you must add conditions in Customize policy) |

**Recommended FSI configuration:**

- Scoped users: **two** distinct groups (the template detects communications **between** the two groups). Typical FSI pairings: research analysts ↔ investment-banking; trading desk ↔ research; M&A team ↔ rest-of-firm
- Reviewers: registered principals + Compliance + Legal
- Conditions: add custom keyword dictionaries (deal codes, codenames, "before announcement", "non-public"), custom SITs (deal codes from Control 1.13), and trainable classifiers as appropriate

### Custom policy (the only free-form path)

If your scenario does not fit any template (e.g., Copilot Studio agents on the Other AI apps location, custom SIT-only detection across non-template-supported location combinations), use **Custom policy**. The Custom policy wizard exposes every location, every direction, every condition, and the OCR checkbox without template constraints.

When using Custom policy, document the rationale in the policy description field — auditors should not have to reverse-engineer why a non-template path was chosen.

### Policy Match Preservation (PMP) — set per policy

> **Policy Match Preservation is NOT the records-retention mechanism for SEC 17a-4 / FINRA 4511.** PMP controls how long the **policy-match metadata** (the matched copy held inside the SupervisoryReview store) is preserved for the supervisory review workflow. For regulatory records retention of the **underlying communications** under SEC 17a-4(f) WORM, use Microsoft Purview retention policies — see [Control 1.9](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md).

PMP options (effective **2025-06-01** per current Microsoft Learn): **1 month**, **6 months**, **1 year (default)**, **7 years**.

For each policy:

1. Open **Customize policy** during creation, or **Edit policy** afterward
2. Set **Policy match preservation** based on supervisory needs. Recommended FSI default: **1 year** (the default), with explicit documentation that the 7-year SEC 17a-4 retention is implemented under Control 1.9 retention policies, **not** under PMP
3. Document the choice in the change ticket

### Per-policy alert volume / routing — what is configurable

CC does **not** expose a portal-level "High → email, Medium → Teams, Low → digest" routing matrix. Per-policy alert routing is implemented through the combination of:

- **Reviewer assignment per policy** (which queue an alert lands in)
- **Role group access** (who can see / act on a queue, scoped by AU if applicable)
- **Alert volume tuning** (review percentage, condition tightness, scoped user population)
- **Notification cadence** to reviewers (the standard Microsoft notification email; configurable digest is not a supported portal toggle)

If your firm's WSP requires a 24-hour analyst SLA and a 48-hour investigator SLA, those are **organizational** SLAs tracked outside CC (in your case-management or GRC tool). Do **not** document them as "settings in CC" — they are not.

---

## Step 5 — Configure OCR (on the conditions page; PAYG required)

> OCR is **a checkbox on the policy's Conditions page**, not a separate `Settings → OCR` panel. Older guidance referencing `Settings > OCR` is incorrect for the current portal.

### Enable OCR on a policy

1. Create a policy or edit an existing policy
2. Reach the **Choose conditions and review percentage** page (visible in template flows when you select **Customize policy**, and in the Custom policy wizard)
3. Configure at least one text-based condition (text, keywords, Microsoft trainable classifiers, or sensitive info types). The OCR checkbox is **disabled** until at least one such condition is configured — OCR exists to feed extracted text into those conditions
4. In the **Optical character recognition (OCR)** section, select **Use OCR to extract text from images** checkbox
5. Save the policy

### What OCR does and does not do

- OCR extracts printed and handwritten text from embedded or attached images (PNG, JPG, common image attachments) and feeds it through the **same conditions** configured on the policy
- OCR **requires PAYG billing** linked to an Azure subscription (per current Microsoft Learn)
- OCR processing typically takes approximately **1 hour** to take effect after enablement on a policy — early no-match results are inconclusive, not negative
- OCR does not translate; it does not classify image content (use Inappropriate images for image classification); it does not OCR text inside encrypted attachments the service cannot resolve

Document in your evidence pack: which policies have OCR enabled, the PAYG subscription ID, and the expected processing window.

---

## Step 6 — Validation: seed test message, wait the Learn processing window, verify Pending queue and audit rows

> Do **not** treat "policy created with no error" as PASS. Generate a known policy-relevant test message from a named test user, wait the documented Learn processing window, and assert both the **Pending** alert appears and the corresponding **audit-log rows** are written.

### Validation procedure (per policy)

1. **Identify a named test user** scoped to the policy. The user must be in the policy's scoped distribution group and (if AU-scoped) in the AU
2. **Identify a named test reviewer** assigned to the policy with an Exchange Online mailbox
3. **At a recorded UTC timestamp**, have the test user send a message that is **certain** to match the policy. Examples:
   - Inappropriate text: a test message containing a clear targeted-harassment classifier hit, sent from the test user's Exchange/Teams/Viva Engage to another internal user
   - Regulatory compliance: a test message containing a documented regulatory-collusion classifier phrase
   - Copilot interactions: a test prompt from M365 Copilot containing a Prompt Shields trigger
   - Sensitive information: a test message containing a clearly synthetic SSN that matches the policy's SIT
4. Record:
   - Sender UPN, recipient UPN
   - UTC send time (`Get-Date -Format 'yyyy-MM-ddTHH:mm:ssZ'`)
   - Channel (Exchange / Teams chat / Teams channel / Viva Engage / Copilot)
   - Expected matched condition
5. **Wait the documented Learn processing window:**
   - **Email (Exchange Online):** approximately **24 hours**
   - **Teams chats, Viva Engage, third-party platforms:** approximately **48 hours**
   - **Copilot interactions:** allow at least 24 hours; extend to 48 hours if no result by 24 hours
   - **OCR-driven matches:** add ~1 hour beyond the channel processing window
6. **Verify in the Pending queue:** open the policy → **Pending** tab → filter by user and the UTC window → confirm the alert appears with the matched condition
7. **Verify reviewer can take action:** as the test reviewer, open the alert and exercise **Resolve** and **Tag** (do not exercise **Remove** in production tests; use a non-production tenant for that). Record the reviewer UPN, action, and UTC timestamp
8. **Verify audit-log rows** in the Unified Audit Log (Microsoft Purview Audit search):

```text
Activities to filter for:
  - SupervisionRuleMatch     (the match was recorded)
  - SupervisoryReviewTag     (the reviewer tagged the alert)
Date range: UTC window covering send + processing window + reviewer action
Users: test user (for SupervisionRuleMatch) and test reviewer (for SupervisoryReviewTag)
```

Or via PowerShell:

```powershell
Connect-IPPSSession
Search-UnifiedAuditLog -StartDate (Get-Date).AddDays(-3) -EndDate (Get-Date) `
    -Operations 'SupervisionRuleMatch','SupervisoryReviewTag' `
    -ResultSize 5000 |
    Export-Csv -NoTypeInformation -Path ".\evidence\1.10-validation-$(Get-Date -Format 'yyyyMMddTHHmmssZ').csv"
```

Both rows must be present. If the **Pending** alert appears but `SupervisionRuleMatch` is missing from UAL, the audit log was not active at send time (regression — re-verify Prerequisites #2).

9. **Capture evidence:**
   - Screenshot of the alert in the Pending queue (with anonymized usernames if pseudonymization is on; capture both the anonymized and admin-resolved view if your firm requires it)
   - CSV export of the UAL search
   - SHA-256 sidecar per `docs/playbooks/_shared/powershell-baseline.md` §5

### Validation cadence

- **Per policy at creation:** required (one-time validation)
- **Per policy after any material change:** required (condition change, scope change, reviewer change, location change)
- **Quarterly:** sample-validate every Zone-3 policy (registered-rep populations, Copilot interactions)
- **Annually:** sample-validate every active policy

---

## Step 7 — Operationalization (cadence, escalation, integration with Insider Risk)

### Reviewer cadence (organizational, not portal)

Document in your firm's WSP — not in CC settings — the reviewer SLAs (e.g., "analyst triage within 24 hours, investigator escalation within 48 hours"). Track adherence in your case-management / GRC tool. The portal does not enforce SLAs; reviewer queue depth and per-alert age are the operational signals to monitor (visible on the Alerts dashboard).

### Escalation paths

| From CC | To | Trigger |
|---|---|---|
| CC Analyst | CC Investigator (escalate alert) | Alert confirmed as a violation |
| CC Investigator | HR | Personnel-conduct violation |
| CC Investigator | Legal | Regulatory violation; possible disclosure obligation |
| CC Investigator | Compliance Officer | Written customer complaint tied to an AI-assisted communication; determine FINRA Rule 4530(d) treatment and supervisory disposition |
| CC Investigator | eDiscovery ([Control 1.19](../../../controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md)) | Legal hold or production scope expansion needed |
| CC Investigator | Insider Risk Management ([Control 1.12](../../../controls/pillar-1-security/1.12-insider-risk-detection-and-response.md)) | Pattern of risky behavior across multiple alerts |
| CC Investigator | CISO + Legal | Cyber / data-loss event; trigger SEV-1/2 incident handling per [Control 1.10 troubleshooting §1](troubleshooting.md) |

### Customer complaint routing (FINRA Rule 4530(d))

1. When a reviewer confirms a written complaint about an AI-generated or AI-assisted communication, apply the firm's complaint tag and record the underlying message ID, prompt/response reference, or Copilot conversation ID in the case note.
2. Escalate the tagged item to the Compliance Officer or designated registered principal for reportability review, and notify the records team if additional preservation steps are required under Controls 1.7 and 1.9.
3. Export tagged complaint counts and dispositions into the firm's quarterly FINRA Rule 4530(d) complaint-statistics workflow. Verify the same complaint is not double-counted across manual and automated queues.

### Integration with Insider Risk Management (Control 1.12)

CC integrates with IRM in two directions:

1. **CC → IRM:** A CC `Detect inappropriate text` policy can act as a risk signal feeding IRM risky-user policies (created automatically from the IRM **Data leaks by risky users** template or generative-AI templates). This surfaces communication-based risk into IRM scoring without a separate manual workflow
2. **IRM → CC:** IRM alerts can be referenced during CC investigations to provide behavioral context (was this user on an IRM watchlist when the message was sent?)

Document any cross-product policies in both control evidence packs (Control 1.10 **and** Control 1.12) to avoid orphaned references during an audit.

### Compliance boundaries (eDiscovery interaction)

If your tenant uses **compliance boundaries** for eDiscovery (multi-segment tenant), CC reviewer access to mailboxes for full-conversation review can be blocked by the existing boundary. Update the boundary once to grant CC admins / reviewers access to the SupervisoryReview-prefixed mailboxes. The Microsoft Learn one-shot PowerShell:

```powershell
Import-Module ExchangeOnlineManagement
Connect-IPPSSession
New-ComplianceSecurityFilter `
    -FilterName 'CC_mailbox' `
    -Users '<comma-separated UPNs of CC admins and reviewers>' `
    -Filters "Mailbox_Name -like 'SupervisoryReview{*'" `
    -Action All
```

Run once. Re-run only when the reviewer population changes.

### Notice templates

For policies that require a **Notice** remediation action (a reminder email to the user), create a notice template per policy under **Settings → Communication Compliance → Notice templates**. Required fields: template name, send-from address, subject, body. Cc / Bcc are optional. Reviewers can edit notice content at send time.

---

## Anti-patterns

The following are common configuration mistakes that produce silent failures, false-clean evidence, or audit findings. Avoid all of them.

1. **Creating an Inappropriate content policy expecting it to cover Exchange or Copilot.** It does not. Use **Inappropriate text** for Exchange + harassment, and **Copilot interactions** for Copilot.
2. **Leaving Regulatory compliance at the 10% default for FINRA-supervised populations.** This produces only sampled review and is unlikely to satisfy 3110 supervisory expectations for registered reps.
3. **Treating "Customer complaints" as a separate template.** It is a classifier inside the Regulatory compliance template. Searching for a "Customer complaints" template wastes time and produces a wrong-named policy.
4. **Assigning reviewers without Exchange Online mailboxes.** Reviewer assignment fails or the reviewer never receives the queue assignment notification.
5. **Assigning roles at the wrong place.** The path is **Settings → Roles & scopes → Permissions → Microsoft Purview solutions → Communication compliance → Role groups**, not "Roles" under any other path.
6. **Using the wrong (singular / synonym) role-group names.** Audit-log queries match the canonical plural names (`Communication Compliance Investigators`, not `CC Investigator`). Wrong names produce empty queries and false-clean evidence.
7. **Using PowerShell to "create" CC policies.** PowerShell is not supported for CC policy management. Any script in this repo that purports to create CC policies via cmdlet is wrong.
8. **Disabling pseudonymization without an audit trail.** The opt-out is a privileged action and must be auditable. An undocumented opt-out is an SOX 404 / privacy finding.
9. **Adding users to Communication Compliance Investigators casually.** Investigators see non-pseudonymized identities and can download messages. Treat each addition as a privileged elevation with HR/Legal sign-off.
10. **Configuring AUs and adaptive scopes together on CC.** Not supported. Pick one scoping model.
11. **Treating Policy Match Preservation as records retention.** PMP retains the **policy-match metadata** in the supervisory store, not the underlying communications under SEC 17a-4(f) WORM. Records retention is implemented separately under [Control 1.9](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md).
12. **Assuming OCR is automatic.** OCR is a **checkbox on the policy Conditions page**, requires at least one text-type condition to enable, requires PAYG, and takes ~1 hour to take effect.
13. **Validating by "I created the policy and it didn't error."** Validation requires a **seeded test message** + the documented Learn processing window + verification of both the Pending queue entry and the `SupervisionRuleMatch` / `SupervisoryReviewTag` audit rows.
14. **Including non-M365 AI locations without PAYG.** Locations either do not appear in the wizard or silently produce zero matches.
15. **Documenting fabricated SLA toggles** ("24h analyst, 48h investigator") as portal settings. They are organizational SLAs, tracked outside CC.
16. **Routing CC alerts as a substitute for incident handling.** CC alerts feed supervisory review. A genuine cyber, NPI exposure, or insider-risk event must be escalated to incident handling per [troubleshooting.md §1](troubleshooting.md), not closed inside CC.
17. **Referencing custom SITs that have not been created in [Control 1.13](../../../controls/pillar-1-security/1.13-sensitive-information-types-sits-and-pattern-recognition.md).** The policy will save with a non-existent SIT name but will never produce matches against it.

---

## Evidence pack

Use a consistent file naming convention:

```
Control-1.10_{TenantId}_{Cloud}_{ArtifactType}_{YYYYMMDD-HHmm-UTC}.{ext}
Control-1.10_{TenantId}_{Cloud}_{ArtifactType}_{YYYYMMDD-HHmm-UTC}.{ext}.sha256
```

| Artifact | Source | Format | Frequency |
|---|---|---|---|
| Unified Audit Log status (`Get-AdminAuditLogConfig`) | Exchange Online PowerShell | JSON | Monthly + on change |
| License entitlement snapshot for monitored users | Graph `Get-MgUserLicenseDetail` | JSON | Quarterly |
| Role group membership (six CC role groups) | Purview portal export + Graph | CSV + JSON | Monthly + on change |
| Pseudonymization setting state and opt-out audit trail | Purview Privacy tab + UAL search | PNG + CSV | On change |
| Administrative Unit assignments per role-group member | Purview portal + Graph | JSON | On change |
| Policy inventory (name, template, locations, direction, conditions, review %, PMP, OCR, scope, reviewers, mode) | Purview Policies page export | JSON + CSV | Weekly |
| Per-policy validation result (sender, reviewer, UTC, condition, Pending entry, UAL rows) | Test log + UAL CSV | CSV + log | Per validation |
| Notice templates and notice-send history | Purview portal + UAL | CSV | Quarterly |
| Compliance boundary configuration (`Get-ComplianceSecurityFilter`) | IPPS PowerShell | JSON | On change |
| Tenant cloud + sovereign-cloud capability snapshot | Manual + Graph | JSON | On change |
| PAYG billing state (Purview Usage center export) | Purview portal | CSV | Monthly |

Store in immutable storage (Purview retention label, SharePoint hold, or WORM blob) aligned to [Control 1.9](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md) retention.

---

## Cross-references

- [Control 1.10 PowerShell Setup](powershell-setup.md)
- [Control 1.10 Troubleshooting (§1 — FSI Incident Handling — READ FIRST)](troubleshooting.md)
- [Control 1.5 DLP and Sensitivity Labels](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) — block layer that complements CC's review layer
- [Control 1.6 Microsoft Purview DSPM for AI](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md) — visibility for AI surfaces feeding the Copilot interactions template
- [Control 1.9 Data Retention and Deletion Policies](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md) — SEC 17a-4 / FINRA 4511 records retention (NOT Policy Match Preservation)
- [Control 1.12 Insider Risk Detection and Response](../../../controls/pillar-1-security/1.12-insider-risk-detection-and-response.md) — bidirectional integration with CC
- [Control 1.13 Sensitive Information Types](../../../controls/pillar-1-security/1.13-sensitive-information-types-sits-and-pattern-recognition.md) — create custom SITs **before** referencing them in CC policies
- [Control 1.19 eDiscovery for Agent Interactions](../../../controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md) — escalation path for production / legal hold
- [Microsoft Learn — Communication Compliance overview](https://learn.microsoft.com/en-us/purview/communication-compliance)
- [Microsoft Learn — Plan for Communication Compliance](https://learn.microsoft.com/en-us/purview/communication-compliance-plan)
- [Microsoft Learn — Configure Communication Compliance](https://learn.microsoft.com/en-us/purview/communication-compliance-configure)
- [Microsoft Learn — Communication Compliance policies](https://learn.microsoft.com/en-us/purview/communication-compliance-policies)
- [Microsoft Learn — Detect channel signals](https://learn.microsoft.com/en-us/purview/communication-compliance-channels)
- [Microsoft Learn — Communication Compliance permissions](https://learn.microsoft.com/en-us/purview/communication-compliance-permissions)
- [Microsoft Learn — Investigate and remediate alerts](https://learn.microsoft.com/en-us/purview/communication-compliance-investigate-remediate)
- [Microsoft Learn — Communication Compliance feature reference](https://learn.microsoft.com/en-us/purview/communication-compliance-policies)

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
