# Control 1.5 — Portal Walkthrough: Data Loss Prevention (DLP) and Sensitivity Labels

**Control:** [1.5 Data Loss Prevention and Sensitivity Labels](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md)
**Pillar:** 1 — Security & Identity
**Last UI Verified:** April 2026 (Microsoft Purview portal `purview.microsoft.com`, Power Platform Admin Center `admin.powerplatform.microsoft.com`, Microsoft 365 admin center)
**Audience:** M365 administrator at a US financial services firm (bank, broker-dealer, insurance carrier, investment adviser, credit union)
**Cloud coverage:** Commercial · GCC · GCC High · DoD (sovereign cloud parity table in §2)
**Estimated time:** 8–14 hours initial buildout (covers all 13 DLP surfaces); 2–3 hours per surface refresh thereafter; pilot validation windows excluded

> This playbook operationalizes [Control 1.5](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md). It is written to **support compliance with** FINRA 3110/4511, FINRA Notice 25-07 (RFC, contextual), SEC Reg S-P (17 CFR 248, 2024 amendments), SEC Rule 17a-4, GLBA 501(b), SOX 302/404, NYDFS 23 NYCRR 500.11/500.15/500.16, OCC Bulletin 2026-13 (formerly OCC 2011-12), FFIEC, PCI DSS 4.0 (where card data flows), and state breach-notification laws (NY GBL 899-aa, MA 201 CMR 17, CCPA/CPRA). It does **not**, by itself, satisfy any single regulatory obligation. Implementation requires sustained operator discipline; organizations should verify configuration against current regulatory expectations and their own legal counsel's interpretation.

---

!!! danger "READ FIRST — Scope and the central FSI failure mode"
    This walkthrough configures the **two distinct DLP control planes** referenced in the control doc — Microsoft Purview DLP (`purview.microsoft.com`) and Power Platform data policies (`admin.powerplatform.microsoft.com`) — across **all 13 DLP surfaces** an FSI tenant typically needs instrumented. The single most common FSI DLP failure pattern is **partial coverage**: SharePoint and OneDrive instrumented but Teams chat, Endpoint, the Copilot prompt/response surface, unmanaged AI traffic, Power BI / Fabric, or on-prem file shares left silent. Sensitive data exfiltrates through whichever surface is uninstrumented.

    **The 13 surfaces (every one is configured in this playbook):**

    | # | Surface | Where configured |
    |---|---|---|
    | 1 | SharePoint Online sites | Purview DLP location `SharePoint sites` (§5) |
    | 2 | OneDrive for Business | Purview DLP location `OneDrive accounts` (§5) |
    | 3 | Exchange Online (mail in transit) | Purview DLP location `Exchange email` (§5) |
    | 4 | Teams chat & channel messages (incl. private channels) | Purview DLP location `Teams chat and channel messages` — extend default policy beyond credit cards (§6) |
    | 5 | Endpoint DLP — Win 10/11, Win Server 2019/2022, last 3 macOS | Purview DLP location `Devices` (§7) |
    | 6 | Microsoft 365 Copilot & Copilot Chat — block by label (GA) | Purview DLP location `Microsoft 365 Copilot and Copilot Chat`, Custom template (§8) |
    | 7 | Microsoft 365 Copilot & Copilot Chat — block prompts by SIT (preview) | Same location, separate rule (§8) |
    | 8 | Power Platform connector classification (Microsoft Copilot Studio agents) | PPAC `Policies > Data policies` (§9) |
    | 9 | Power Platform HTTP endpoint filtering (preview) | PPAC connector configuration (§9) |
    | 10 | Edge for Business — unmanaged AI (preview) — ChatGPT, Gemini, DeepSeek, Copilot consumer | Purview Endpoint DLP browser/site restrictions + Edge configuration policy (§10) |
    | 11 | Network DLP for unmanaged AI (preview) | Purview Endpoint DLP **Network activity** rules (§10) |
    | 12 | Defender for Cloud Apps file policies (non-Microsoft SaaS) | Defender for Cloud Apps `Policies > File policies` (§11) |
    | 13a | Power BI / Fabric workspaces | Purview DLP location `Fabric and Power BI workspaces` (§12) |
    | 13b | On-premises file shares / on-prem SharePoint | Purview Information Protection scanner (§13) |

    If any row above is uninstrumented in **Zone 3**, treat that surface as the *most likely* exfiltration path during an incident and document the gap in your Written Supervisory Procedures.

!!! warning "Two distinct DLP control planes — do not conflate them"
    Microsoft Purview DLP and Power Platform data policies are **different products** with different portals, cmdlets, and licensing.

    | Product | Governs | Portal (Commercial) | Cmdlet family |
    |---|---|---|---|
    | **Microsoft Purview DLP** | First-party Copilot prompts and labeled grounding files; SharePoint, OneDrive, Exchange, Teams, Devices, Fabric / Power BI | `purview.microsoft.com` | `Get-DlpCompliancePolicy`, `Get-DlpComplianceRule` |
    | **Power Platform data policies** | Copilot Studio agents, connector classification, channel publishing, HTTP endpoint filtering | `admin.powerplatform.microsoft.com` | `Get-DlpPolicy` (PowerApps cmdlets) |

    A change to one does **not** apply to the other. References: [DLP for Microsoft 365 Copilot location (Learn)](https://learn.microsoft.com/en-us/purview/dlp-microsoft365-copilot-location-learn-about) · [Power Platform DLP overview (Learn)](https://learn.microsoft.com/en-us/power-platform/admin/wp-data-loss-prevention).

!!! warning "Hedged-language reminder (mandatory)"
    Throughout this playbook — and in any derivative ticket template, attestation memo, or examiner-response narrative — these overclaim phrases **must not appear**:

    - "ensures compliance with…" → use **"supports compliance with…"**
    - "guarantees…" → use **"is designed to…"** or **"helps the organization…"**
    - "will prevent…" → use **"is intended to reduce the likelihood of…"**
    - "eliminates the risk of…" → use **"helps mitigate…"**

    DLP and labels reduce risk surface. They do **not** produce a legal compliance guarantee.

---

## §1 — Prerequisites

Confirm **every** item below before starting. A missed prerequisite causes a downstream surface to silently produce zero matches.

### 1.1 Licensing

| Capability | Required SKU(s) |
|---|---|
| Purview DLP for Exchange/SharePoint/OneDrive/Teams/Devices/Fabric | Microsoft 365 E5 / E5 Compliance / Microsoft Purview Suite per monitored user — verify against [Purview DLP licensing guidance](https://learn.microsoft.com/en-us/office365/servicedescriptions/microsoft-365-service-descriptions/microsoft-365-tenantlevel-services-licensing-guidance) |
| Endpoint DLP (Devices location) | E5 Compliance entitlement; device onboarding via Defender for Endpoint **or** Purview standalone onboarding |
| Microsoft 365 Copilot DLP location (block by label, GA; block by SIT, preview) | Microsoft 365 Copilot per-user license for users in scope |
| Sensitivity labels (file/email + container) | Included with E3+; encryption requires Azure Information Protection P1/P2 entitlement |
| Double Key Encryption (DKE) — NYDFS 500.15 / state regulator scenarios | DKE service deployed by the institution; cross-link [Control 1.15](../../../controls/pillar-1-security/1.15-encryption-data-in-transit-and-at-rest.md) |
| Adaptive Protection (DLP risk-tiered enforcement) | Insider Risk Management entitlement (E5 Compliance / Purview Suite) — **Commercial only**; see §14 |
| Power Platform data policies | Power Platform admin role (no extra SKU); Managed Environments add-on recommended for Zone 3 |
| Defender for Cloud Apps file policies | Microsoft Defender for Cloud Apps standalone or Microsoft 365 E5 Security |
| `AIAppInteraction` audit records (non-Microsoft AI app interactions) | **Purview Audit pay-as-you-go (PAYG)** Azure subscription bound to the tenant; cross-link [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) |

### 1.2 Data dependencies

- **SITs from [Control 1.13](../../../controls/pillar-1-security/1.13-sensitive-information-types-sits-and-pattern-recognition.md)** deployed and validated, with documented confidence threshold and proximity, including FSI-specific custom SITs (e.g., `U.S. Bank Account Number`, `ABA Routing Number`, `U.S. SSN`, custom MNPI patterns)
- **EDM (Exact Data Match) classifiers** authored per [Control 1.13](../../../controls/pillar-1-security/1.13-sensitive-information-types-sits-and-pattern-recognition.md) for FSI account numbers (when matching against an authoritative customer master), MNPI watch lists, and research-report inventories
- **Trainable classifiers** trained per [Control 1.13](../../../controls/pillar-1-security/1.13-sensitive-information-types-sits-and-pattern-recognition.md) for research reports, board materials, and other FSI document types where pattern matching is insufficient
- A defined **sensitivity label taxonomy** (Public / Internal / Confidential / Highly Confidential — adjust to your scheme) approved by Information Protection / Records governance
- **Agent inventory** ([Control 1.4](../../../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md) / [Control 2.16](../../../controls/pillar-2-management/2.16-rag-source-integrity-validation.md)) so you know which agents touch which data
- Onboarded devices for the Endpoint DLP location (§7)

### 1.3 Roles required

Use canonical short names from `docs/reference/role-catalog.md`. Avoid Entra Global Admin where a workload-specific role is sufficient.

| Workstream | Role |
|---|---|
| Purview DLP policies and rules | Purview Compliance Admin |
| Sensitivity labels and label policies | Purview Information Protection Admin |
| Power Platform data policies and connector classification | Power Platform Admin |
| Endpoint device onboarding and browser policy | Intune Admin (Endpoint admin) + Purview Compliance Admin |
| Adaptive Protection (Commercial only) | Insider Risk Management role group + Purview Compliance Admin |
| Defender for Cloud Apps file policies | Defender Admin (or Cloud App Security admin role) |
| AI prompt/response content review | Reviewer with **Purview Data Security AI Content Viewer** |
| Audit telemetry destination | Purview Audit Admin (see [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md)) |
| SIEM ingestion | Sentinel contributor (see [Control 3.9](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md)) |

> **Least privilege.** The Microsoft 365 Copilot and Copilot Chat DLP location does **not support administrative units** — a Restricted Administrative Unit-scoped admin cannot create or edit a policy that includes this location. Use a tenant-scoped role.

---

## §2 — Sovereign cloud portal endpoints and parity

| Cloud | Purview portal | Power Platform Admin Center | Defender for Cloud Apps | Notes |
|---|---|---|---|---|
| Commercial | `https://purview.microsoft.com` | `https://admin.powerplatform.microsoft.com` | `https://security.microsoft.com` | Reference cloud for this walkthrough |
| GCC | `https://compliance.microsoft.com` (transitioning to `purview.microsoft.com`) | `https://admin.powerplatform.microsoft.us` | `https://security.microsoft.com` (GCC tenant) | Verify rollout per workload |
| GCC High | `https://purview.microsoft.us` | `https://admin.powerplatform.microsoft.us` | `https://security.microsoft.us` | **IRM and Adaptive Protection NOT available** |
| DoD | `https://purview.microsoft.us` (DoD) | `https://admin.powerplatform.microsoft.us` | `https://security.apps.mil` | **IRM and Adaptive Protection NOT available** |

!!! danger "Sovereign cloud reality — IRM / Adaptive Protection in US Government clouds"
    Per Microsoft Learn, **Insider Risk Management — and therefore Adaptive Protection — is not available in any US Government cloud (GCC, GCC High, DoD)** as of April 2026. For Zone 3 deployments in GCC / GCC High / DoD:

    1. Use **static role-based DLP rules** keyed off Entra group membership (e.g., a `FSI-Privileged-Brokers` group) rather than IRM-derived risk tiers.
    2. Document the gap as a **compensating control** in your sovereign-cloud exception register.
    3. Strengthen supervisory review under [Control 2.12](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) to compensate for the absence of risk-adaptive enforcement.

    Reference: [Adaptive Protection in Microsoft Purview (Learn)](https://learn.microsoft.com/en-us/purview/insider-risk-management-adaptive-protection).

---

## §3 — Propagation banner (read once, applies to every step)

!!! danger "Plan validation windows around propagation"
    - **Purview DLP for the Microsoft 365 Copilot and Copilot Chat location:** changes can take **up to 4 hours** to take effect. Treat earlier "no match" results as inconclusive, not as failure.
    - **Purview DLP for SharePoint / OneDrive / Exchange / Teams / Devices:** typically minutes to ~1 hour for new policies; up to several hours for rule changes on large content stores.
    - **Power Platform data policies:** allow ~1–2 hours for connector-classification changes to propagate to runtime; HTTP endpoint filtering may take additional time.
    - **Sensitivity labels:** publishing a label policy can take **up to 24 hours** to surface in Office clients.
    - **Auto-labeling:** initial simulation can take hours to days depending on corpus size.
    - **Defender for Cloud Apps file policies:** initial scan can take hours to days depending on connected app inventory.

    Always start new policies in **Test with policy tips / Test with notifications** mode (the Purview UI uses both terms — they refer to the **same** pre-enforcement validation phase). Only move to **Turn it on right away** after the propagation window and a documented validation pass. **Zone 3 must complete a documented simulation pass before enforcement.**

---

## §4 — Sensitivity labels: create, publish, and understand the boundaries (do this first)

> Labels do not appear to users until a label policy is **published**. Create labels first because every downstream DLP rule that references a label depends on the label existing in the tenant.

### 4.1 Create labels (Purview portal)

1. Sign in to your tenant cloud's Purview portal (per §2).
2. Navigate **Solutions → Information Protection → Labels**.
3. Select **+ Create a label**.
4. Define the FSI taxonomy — illustrative only; substitute your scheme:

    | Label | Default posture | FSI use |
    |---|---|---|
    | **Public** | Allow; audit optional | Marketing collateral, SEC filings post-publication |
    | **Internal** | Allow; audit recommended | Routine internal correspondence |
    | **Confidential** | Warn or restrict; always log | Customer correspondence, draft research |
    | **Highly Confidential** | Block-by-label for Copilot processing; incident report | MNPI, customer PII, M&A working files, board materials |

5. Configure **encryption** for Confidential and Highly Confidential. Encryption is required for any label intended to enforce access on content that leaves SharePoint/OneDrive (e.g., emailed externally, downloaded to an unmanaged device).
6. For NYDFS 23 NYCRR 500.15 or state-regulator scenarios where the institution must hold a key, enable **Double Key Encryption (DKE)** instead of the default Microsoft-managed key path. DKE requires a customer-hosted key service. Cross-link [Control 1.15](../../../controls/pillar-1-security/1.15-encryption-data-in-transit-and-at-rest.md) for the DKE deployment runbook.
7. Configure **content marking** (header / footer / watermark) per zone.
8. Save each label.

### 4.2 Publish at least one label policy

1. **Information Protection → Label policies → + Publish labels**.
2. Select the labels created in 4.1.
3. Scope to the users and groups who create or handle content (and to agent owners and compliance reviewers).
4. Configure **default label**, **mandatory labeling** (Zone 3), and **require justification on label change to lower classification**.
5. Save and allow up to 24 hours for clients to refresh.

Reference: [Sensitivity labels overview (Learn)](https://learn.microsoft.com/en-us/purview/sensitivity-labels).

### 4.3 Container labels vs. file labels

Labels applied to Microsoft 365 Groups, Teams, and SharePoint sites govern **container-level settings** (privacy, external sharing, device access, default link types). Items inside the container do **not** inherit the container label. File-level labeling requires a published file/email label policy, an auto-labeling policy (§4.4), or manual application.

### 4.4 Auto-labeling — locations and limits

1. **Information Protection → Auto-labeling → + Create auto-labeling policy**.
2. The **only** auto-labeling locations supported by Purview are:
    - **SharePoint Online** sites
    - **OneDrive for Business** accounts
    - **Exchange Online** mailboxes
3. There is **no "AI interactions" auto-labeling location.** Auto-labeling does not label Copilot prompts or agent responses. Label-based DLP for Copilot relies on labels already present on the underlying SPO/OneDrive/Exchange items at the time of the prompt.
4. Use SITs, EDM, or trainable classifiers from [Control 1.13](../../../controls/pillar-1-security/1.13-sensitive-information-types-sits-and-pattern-recognition.md) as match conditions.
5. Run the policy in **Simulation** first; review matches; remediate false positives in the SIT/EDM/classifier; then **Turn it on**.

Reference: [Apply a sensitivity label automatically (Learn)](https://learn.microsoft.com/en-us/purview/apply-sensitivity-label-automatically).

### 4.5 Conditional Access session controls for label-restricted access

Entra Conditional Access can enforce label-restricted access — for example, **block download of Highly Confidential** from unmanaged devices, or require a compliant device to open a Confidential file. Configure these in the Entra portal under **Protection → Conditional Access**, scoped to the SharePoint cloud app with session controls enforcing app-enforced restrictions.

Cross-links: [Control 1.20 — Network isolation / private connectivity](../../../controls/pillar-1-security/1.20-network-isolation-private-connectivity.md) and [Control 1.21 — Adversarial input logging](../../../controls/pillar-1-security/1.21-adversarial-input-logging.md).

---

## §5 — Surfaces 1–3: SharePoint sites, OneDrive accounts, Exchange email

### 5.1 Create the baseline FSI Purview DLP policy

1. Purview portal → **Solutions → Data Loss Prevention → Policies**.
2. **+ Create policy**.
3. Choose category **Custom → Custom policy** (Standard templates do not surface every location you'll need later for the Copilot location). Click **Next**.
4. Name: `FSI-Baseline-DLP-SPO-OneDrive-Exchange`. Add a description that references this control and the change ticket.
5. Admin scope: tenant. Do **not** select a Restricted Administrative Unit.
6. **Locations** — enable:
    - **SharePoint sites** (Surface 1)
    - **OneDrive accounts** (Surface 2)
    - **Exchange email** (Surface 3)
   Configure include/exclude scoping per the agent inventory and zone matrix.
7. **Next** to the rule editor.

### 5.2 Author the rules

Create one rule per FSI risk category (named to make audit review easier). Each rule references SITs, EDM classifiers, or trainable classifiers from [Control 1.13](../../../controls/pillar-1-security/1.13-sensitive-information-types-sits-and-pattern-recognition.md):

| Rule | Condition (Content contains) | Action | Notes |
|---|---|---|---|
| `R1-Customer-PII-PCI` | SITs: U.S. SSN, U.S. Bank Account Number, ABA Routing Number, Credit Card Number | Block with override (Confidential+); incident report | Confidence per SIT calibration; record proximity |
| `R2-EDM-Customer-Account-Master` | EDM classifier: customer account master | Block; no override; incident report | Authoritative match — high confidence |
| `R3-MNPI-WatchList` | EDM classifier: MNPI ticker watch list **OR** Trainable classifier: research-report content | Block with justified override (broker-dealer research department only); incident report; high severity | Cross-link [Control 2.12](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) supervision queue |
| `R4-Sensitivity-Label` | Sensitivity labels: Confidential, Highly Confidential | Restrict access / Block external sharing | Acts on items already labeled per §4 |

For each rule:

- **User notifications:** enable **policy tips** with FSI-appropriate text referencing the internal data-handling standard.
- **User overrides:** enable override **only** with **required business justification**. Override telemetry routes to Purview Audit (see [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md)) and Sentinel (see [Control 3.9](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md)); supervisors review per [Control 2.12](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md).
- **Incident reports:** route to the DLP / SecOps shared mailbox; severity per zone.
- **Mode:** **Test with notifications** (also labeled **Test with policy tips** in some UI variants — same pre-enforcement state).

### 5.3 Move to enforcement after the simulation pass

Zone 3 requires a documented simulation pass: a recorded set of test prompts/uploads, the resulting alerts in **DLP Alerts** and **Activity Explorer**, and sign-off by the Information Protection lead. After sign-off, edit the policy → **Turn it on right away**.

---

## §6 — Surface 4: Teams chat & channel messages (extend default policy beyond credit cards)

The Microsoft-provided default Teams DLP policy targets credit-card numbers only. **An FSI tenant must extend coverage** to U.S. SSN, U.S. Bank Account Number, ABA Routing Number, MNPI watch lists, and Confidential / Highly Confidential labels.

1. Purview portal → **Solutions → Data Loss Prevention → Policies**.
2. **+ Create policy → Custom → Custom policy → Next**.
3. Name: `FSI-Teams-DLP-Extended`.
4. **Locations** → enable **Teams chat and channel messages** (this includes private channels). Scope to in-scope users / teams.
5. Create rules referencing the same SITs, EDM classifiers, trainable classifiers, and sensitivity labels as §5.2. The Teams location supports both message-content and shared-file matching.
6. **Actions:** for Confidential/Highly Confidential matches, **Block with override and require business justification**; for SIT matches in Zone 3 chats, **Block** with no override.
7. **Mode:** Test with notifications → simulation pass → enforce.

> Override telemetry from Teams DLP also flows through Purview Audit / Sentinel and is reviewed under [Control 2.12](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md).

---

## §7 — Surface 5: Endpoint DLP (Devices) — Win 10/11, Win Server 2019/2022, last 3 macOS versions

Endpoint DLP rules apply only to **onboarded devices**. If devices are not onboarded, your endpoint rules silently produce zero matches.

### 7.1 Onboard devices

1. Purview portal → **Settings → Device onboarding** (or use Defender for Endpoint if already deployed; managed devices auto-onboard once Defender is enabled with the shared signal).
2. Choose your onboarding method (Local script, Group Policy, Intune, Microsoft Configuration Manager, or VDI). Reference: [Onboarding tools and methods (Learn)](https://learn.microsoft.com/en-us/purview/device-onboarding-overview).
3. Push the onboarding package to a pilot ring first; expand once telemetry is healthy.
4. Confirm devices appear under **Device onboarding → Devices** with status **Active**.
5. Reconcile the device inventory to your monitored-user list; record any gap as a coverage exception.

### 7.2 Verify supported OS coverage

Endpoint DLP supports **Windows 10/11**, **Windows Server 2019/2022**, and the **last three macOS major versions** (per Microsoft Learn at the time of UI verification). Devices outside that matrix are not in scope; flag them in the exception register and route to alternative controls (network DLP §10, Defender for Cloud Apps §11).

### 7.3 Author endpoint rules

1. Create or edit a Purview DLP policy and enable the **Devices** location.
2. Add rules for:
    - SIT matches on **file activities** (copy to USB, copy to network share, print, copy to cloud sync, upload to unallowed app/site).
    - Sensitivity-label matches on the same activities.
3. Configure **Endpoint DLP settings** (tenant-wide) in **Settings → Endpoint DLP settings**:
    - **Unallowed apps / Restricted apps** — list consumer cloud-storage and file-sharing clients.
    - **Unallowed Bluetooth apps**, **Restricted services domains**, **Browser and domain restrictions**.
    - **Sensitive service domains** — list the FSI-approved cloud services.
4. **Mode:** Test with notifications → simulation pass → enforce.

---

## §8 — Surfaces 6 & 7: Microsoft 365 Copilot & Copilot Chat (block by label GA; block by SIT preview)

### 8.1 Why a separate policy

The Standard DLP templates (Financial, Privacy, etc.) **do not surface** the *Microsoft 365 Copilot and Copilot Chat* location. You must use **Custom → Custom policy** to expose it. Source: [Learn — DLP for Microsoft 365 Copilot location](https://learn.microsoft.com/en-us/purview/dlp-microsoft365-copilot-location-learn-about).

### 8.2 Create the Copilot DLP policy

1. Purview portal → **Solutions → Data Loss Prevention → Policies → + Create policy**.
2. **Custom → Custom policy → Next**.
3. Name: `FSI-Copilot-DLP-Baseline`. Description references this control + ticket.
4. Admin scope: **tenant**. Do **not** select a Restricted Administrative Unit (the Copilot location does not support AUs).
5. **Locations** → enable **Microsoft 365 Copilot and Copilot Chat**. Scope to the user/group population from your agent inventory.
6. **Next** to the rule editor.

### 8.3 Same-rule restriction — author **two separate rules** in the same policy

!!! danger "Same-rule restriction"
    For the Microsoft 365 Copilot and Copilot Chat location, you **cannot** combine *Content contains → Sensitive info types* and *Content contains → Sensitivity labels* in the **same rule**. The Purview UI rejects saving a single rule with both. You must create **two rules in the same policy**. Source: [Learn — DLP for Microsoft 365 Copilot location](https://learn.microsoft.com/en-us/purview/dlp-microsoft365-copilot-location-learn-about) (Important callout).

**Rule A — SIT condition (Surface 7, prompt-blocking, preview):**

1. **+ Create rule** → name `Rule-A-SITs-Copilot-Prompts`.
2. **Conditions → Content contains → Add → Sensitive info types** → select SITs and EDM classifiers from §1.2 (U.S. SSN, U.S. Bank Account Number, ABA Routing Number, custom MNPI EDM, etc.). Record confidence and proximity.
3. Leave the *Content contains → Sensitivity labels* row empty for this rule.
4. **Actions:** **Restrict Copilot from processing prompts containing this content** (preview).
5. Configure policy tips, override-with-justification, and incident report (§5.2 conventions).
6. Save the rule.

**Rule B — Sensitivity label condition (Surface 6, grounding-content blocking, GA):**

1. **+ Create rule** → name `Rule-B-Labels-Copilot-Grounding`.
2. **Conditions → Content contains → Add → Sensitivity labels** → select **Highly Confidential** (and **Confidential** if your zone matrix calls for it).
3. Leave the *Sensitive info types* row empty for this rule.
4. **Actions:** **Prevent Microsoft 365 Copilot and Copilot Chat from processing the content** (GA).
5. Save the rule.

> If the UI shows a validation banner referencing combined-condition restriction, you have placed both condition types in one rule — split them.

### 8.4 Block-by-label scope — communicate the boundaries

!!! warning "Block-by-label scope"
    The *Prevent Copilot from processing the content* action applies only to:

    - Files in **SharePoint Online** and **OneDrive for Business**
    - **Emails sent on or after January 1, 2025** (Exchange Online)
    - **Calendar invites are NOT supported**
    - Items still appear in **citations with a link** even when content is not summarized into the response
    - **Files uploaded directly into a Copilot prompt are NOT scanned by this DLP location**

    Communicate these boundaries to stakeholders so the control is not assumed to be broader than its documented scope.

### 8.5 Mode and propagation

- Save the policy in **Test with notifications** mode.
- Wait the **up to 4-hour** propagation window.
- Run the deterministic test in §15 before flipping to **Turn it on right away**.

---

## §9 — Surfaces 8 & 9: Power Platform data policies (Copilot Studio agents) and HTTP endpoint filtering (preview)

> This is a **separate product** from Purview DLP — configure it in PPAC.

### 9.1 Create or edit a data policy

1. Sign in to PPAC (`admin.powerplatform.microsoft.com` — sovereign URL per §2).
2. **Policies → Data policies**.
3. Select an existing policy or **+ New policy**.
4. Name and assign **environments** per zone (one policy per zone is the recommended pattern).

### 9.2 Surface 8 — Classify connectors (Business / Non-Business / Blocked)

In the **Connectors** tab, classify each connector. Connectors classified Business and Non-Business **cannot be combined in the same agent / app / flow**; Blocked connectors cannot be used at all.

| Connector (illustrative) | Zone 1 | Zone 2 | Zone 3 |
|---|---|---|---|
| AI Builder (GPT, Document Processing) | Business | Business | Business (with usage monitoring per [Control 3.1](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md)) |
| Copilot Studio (topics / skills / knowledge) | Business | Business | Business (require change-control approval) |
| HTTP with Microsoft Entra ID | Business or Non-Business | Business | Business **with endpoint filtering — see 9.3** |
| HTTP Webhook (unauthenticated) | Non-Business | Blocked | **Blocked** |
| Direct Line | Business | Business | Business |
| Microsoft Teams + M365 Channel | Business | Business | Business |
| SharePoint channel | Business | Non-Business | Non-Business or Blocked |
| Custom Website / Direct Line custom channel | Non-Business | Blocked | **Blocked** |
| Social-media channels (Facebook, WhatsApp) | Blocked | Blocked | **Blocked** |

> The connector catalog is maintained by Microsoft and grows over time. Refer to the **live PPAC list** for current inventory rather than relying on a static count. Save and allow ~1–2 hours for propagation.

### 9.3 Surface 9 — HTTP endpoint filtering (preview)

!!! info "Preview status"
    Connector endpoint filtering is in **preview** as of April 2026. Verify rollout in your tenant before relying on it as a sole Zone 3 control. Reference: [Connector endpoint filtering (Learn)](https://learn.microsoft.com/en-us/power-platform/admin/connector-endpoint-filtering).

1. In the data policy, locate **HTTP with Microsoft Entra ID** in the Business group.
2. Open the connector configuration → **Endpoint filtering** (or **Connector configurations** depending on UI revision).
3. Choose **Allow list** (Zone 3 default) or **Block list** (Zone 1–2).
4. Add URL patterns (substitute your own approved domains; the patterns below are illustrative):

    ```
    https://api.internal.example.com/*    # Internal corporate APIs
    https://api.sec.gov/*                  # SEC EDGAR
    https://api.finra.org/*                # FINRA regulatory data
    https://www.ffiec.gov/*                # FFIEC data repository
    https://data.treasury.gov/*            # U.S. Treasury data feeds
    https://www.federalreserve.gov/*       # Federal Reserve data
    https://*.marketdata.example.com/*     # Approved market-data vendors (with vendor data-license agreement)
    ```

    Block patterns (Zone 1/2):

    ```
    http://*                               # Any non-HTTPS
    https://*.social-network.example.com/* # Social media APIs
    https://*.file-sharing.example.com/*   # Consumer file sharing
    ```

5. Save and allow ~1–2 hours for propagation.
6. Document allowed endpoints in change control ([Control 2.3](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md)) and obtain dual approval (Power Platform Admin + AI Governance Lead) for Zone 3 per [Control 2.8](../../../controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md).

### 9.4 PAYG implications for non-Microsoft channels

When Copilot Studio agents publish to **non-Microsoft channels**, Microsoft's billing model can route consumption through **Purview pay-as-you-go (PAYG)** for some governance signals (DSPM for AI, content capture). Treat non-Microsoft channels as a higher-risk surface:

- Require named agent owner and dual approval before publishing.
- Verify the Azure subscription bound to PAYG billing is in scope of finance/cost-control.
- Cross-reference [Control 1.6 — DSPM for AI](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md) for PAYG-related visibility implications.

---

## §10 — Surfaces 10 & 11: Edge for Business unmanaged AI (preview) and Network DLP for unmanaged AI (preview)

These two surfaces address the FSI-critical exfiltration path of users pasting customer data into **consumer AI sites** (ChatGPT, Gemini, DeepSeek, Copilot consumer, Claude.ai, etc.).

### 10.1 Surface 10 — Edge for Business unmanaged-AI inline protection (preview)

1. Push the **Edge for Business configuration policy** via Intune (this is a configuration policy, not a browser extension). Document the Intune policy ID and assignment scope.
2. For Chrome / Firefox (Windows-only), push the **Microsoft Purview browser extension** via Intune to in-scope devices.
3. Purview portal → **Settings → Endpoint DLP settings → Browser and domain restrictions to sensitive data** → add consumer AI hostnames (`chat.openai.com`, `chatgpt.com`, `gemini.google.com`, `deepseek.com`, `copilot.microsoft.com` consumer surface, `claude.ai`, etc.) to **Sensitive service domains** or **Unallowed sites** depending on your zone posture.
4. In your Endpoint DLP rules (§7), add an action targeting **Browser activities → Upload to a restricted website** for matches on FSI SITs, EDM, or labels.
5. Configure policy tips with required justification on user override; route override telemetry to Purview Audit and Sentinel as in §5.2.

### 10.2 Surface 11 — Network DLP for unmanaged AI (preview)

1. Purview portal → **Data Loss Prevention → Policies → + Create policy → Custom → Custom policy**.
2. Name: `FSI-Network-DLP-UnmanagedAI`.
3. Enable the **Devices** location and, in the rule, add **Network activities** conditions targeting **Send to unallowed network destination** matched by hostname or IP for the consumer AI services in 10.1.
4. **Actions:** Block (Zone 3) or Audit + warn (Zone 1–2).
5. **Mode:** Test with notifications → simulation pass → enforce.

> **Audit destination:** Endpoint DLP and unmanaged-AI DLP records flow through Purview Audit (Standard). Note that some non-Microsoft AI app interactions captured under the audit operation `AIAppInteraction` are **PAYG-only** (Audit Premium PAYG) — see [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) for the audit-tier distinction.

---

## §11 — Surface 12: Defender for Cloud Apps file policies (non-Microsoft SaaS)

For sanctioned non-Microsoft SaaS (ServiceNow, Workday, Salesforce, Box, Dropbox Business, etc.), Purview DLP does not have native locations. Use **Defender for Cloud Apps file policies**:

1. Sign in to the Defender portal (`security.microsoft.com` Commercial; sovereign per §2).
2. **Cloud Apps → Policies → Policy management → + Create policy → File policy**.
3. Name: `FSI-DfCA-File-DLP-{AppName}`.
4. **Apps:** select the connected app (must be App-Connector-onboarded first).
5. **Filters:** match by file type, content inspection method (DLP using Microsoft Data Classification Service), and the same SITs / EDM / labels referenced in §5.2.
6. **Actions:** Quarantine, restrict access, remove external collaborators, notify owner — choose per zone.
7. **Mode:** start in **Audit only**; move to enforcement after simulation pass.

Reference connected-app coverage and supported governance actions in the Defender for Cloud Apps documentation linked in §17.

---

## §12 — Surface 13a: Power BI / Fabric workspaces

Sensitive data exfiltration via embedded reports, dataset exports, and semantic models is an FSI-relevant path that is invisible to SharePoint/OneDrive DLP.

1. Purview portal → **Data Loss Prevention → Policies → + Create policy → Custom → Custom policy**.
2. Name: `FSI-Fabric-PowerBI-DLP`.
3. **Locations → Fabric and Power BI workspaces** — scope to **Premium** capacities containing sensitive datasets (DLP for Fabric/Power BI typically requires a Premium-class capacity; verify entitlement against current Microsoft Learn).
4. Author rules referencing FSI SITs, EDM classifiers, and sensitivity labels (Confidential, Highly Confidential).
5. **Actions:** notify dataset owner; generate alert; route to incident report mailbox.
6. **Mode:** Test → simulation pass → enforce.

---

## §13 — Surface 13b: On-premises file shares / on-prem SharePoint (Purview Information Protection scanner)

For pre-existing on-prem repositories (file shares, on-prem SharePoint Server) where FSI long-tail records still live:

1. Purview portal → **Information Protection → Scanners** (or under **Settings**, depending on UI revision).
2. Provision an **AIP/Information Protection scanner** instance on a Windows Server with line-of-sight to the repository and an Azure-registered service principal.
3. Configure the scanner to use the **published label policies** from §4 and any **auto-labeling policies** from §4.4.
4. Run **Discovery mode** first to enumerate sensitive content; then **Enforce** to apply labels and (optionally) protection.
5. Reference: [Microsoft Purview Information Protection scanner](https://learn.microsoft.com/en-us/purview/deploy-scanner).

> Once on-prem content is labeled, downstream Purview DLP policies that match on sensitivity labels will apply when the labeled content is later moved into SharePoint Online / OneDrive / Exchange.

---

## §14 — Adaptive Protection (Commercial only — IRM-dependent)

Adaptive Protection lets DLP rule strength scale with a user's IRM-derived risk tier (low / moderate / elevated). It is the recommended pattern for risk-tiered enforcement on Zone 2 / Zone 3 populations **in Commercial**.

!!! warning "Sovereign caveat — repeat from §2"
    **Not available in GCC, GCC High, or DoD.** In those clouds, document the gap as a compensating-control note and rely on static role-based DLP rules keyed off Entra group membership. Source: [Adaptive Protection in Microsoft Purview (Learn)](https://learn.microsoft.com/en-us/purview/insider-risk-management-adaptive-protection).

### 14.1 Prerequisites

- Insider Risk Management onboarded with a completed baseline window before risk tiers populate (see [Control 1.12](../../../controls/pillar-1-security/1.12-insider-risk-detection-and-response.md)).
- The **Insider Risk Management** role group is assigned to the operator enabling Adaptive Protection.

### 14.2 Enable

1. Purview portal → **Solutions → Insider Risk Management → Adaptive Protection** (or **Settings → Adaptive Protection**).
2. Enable Adaptive Protection and review default risk-level definitions.
3. In your DLP rules from §5/§6/§8, add a condition referencing **User's risk level for adaptive protection** = Elevated / Moderate as appropriate.
4. Save and validate behavior in a non-production tenant first.

---

## §15 — Verification: deterministic test, DLP Alerts, Activity Explorer, Audit, Sentinel

A "policy created" screenshot is **not** evidence the rule fires. Generate a known event and assert the row exists.

### 15.1 Deterministic test

1. Wait the propagation window (**≥ 4 hours** for the Copilot location; minutes-to-hours for others).
2. Pick a named test user (M365 Copilot-licensed where Copilot rules are in scope; in policy scope).
3. At a recorded UTC timestamp, have them perform each of the following and capture the policy-tip text the user sees (or absence thereof):
    - Paste a **synthetic** SSN from a controlled test set into a Copilot prompt → expect Rule A match (§8).
    - Reference a SharePoint file labeled **Highly Confidential** in a Copilot prompt → expect Rule B match (§8).
    - Upload a synthetic-PII file to OneDrive → expect §5 match.
    - Send a Teams message containing a synthetic ABA routing number → expect §6 match.
    - Attempt to copy a labeled file to a USB drive on an onboarded Windows endpoint → expect §7 match.
    - Attempt to paste a synthetic SSN into `chat.openai.com` from an onboarded device → expect §10 match.
    - Upload a labeled file to a connected Box/Dropbox Business app → expect §11 match.

### 15.2 Confirm in DLP Alerts

1. Purview portal → **Solutions → Data Loss Prevention → Alerts**.
2. Filter by policy name and the test UTC window.
3. Confirm an alert appears with the expected severity, user, and matching rule.
4. Capture screenshot.

### 15.3 Confirm in Activity Explorer

1. Purview portal → **Solutions → Data Loss Prevention → Activity Explorer** (or **Solutions → Information Protection → Activity explorer** in some tenants).
2. Filter by **Activity** = `DLPRuleMatch` (and related), **User**, and the UTC window.
3. Assert event count ≥ 1 with matching policy / rule / user.
4. Export to CSV for evidence.

### 15.4 Confirm telemetry destination

- **Purview Audit** ingestion of the rule-match record per [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md). Note that records under operation `AIAppInteraction` are **Audit Premium PAYG**-only.
- **Sentinel** ingestion via the Microsoft 365 / Purview connector per [Control 3.9](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md). Validate that override-with-justification telemetry surfaces an analytics rule for supervisor review under [Control 2.12](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md).

### 15.5 Reg S-P 2024 incident-response readiness

Before turning the policy on for Zone 3, confirm that the alert routes feed your written incident-response program ([Control 3.4](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md)) and that responders understand the **dual notification clocks** introduced by the SEC Reg S-P 2024 amendments:

| Clock | Trigger | Audience | Maximum |
|---|---|---|---|
| **30-day customer notification** | Determination that unauthorized access/use is reasonably likely to result in substantial harm or inconvenience | Affected individuals | "As soon as practicable but not later than 30 days" |
| **72-hour service-provider notification** | Discovery by a covered service provider that customer information was or was reasonably likely accessed/used without authorization | The covered institution | Written notice within 72 hours |

DLP telemetry feeds the **determination** that starts both clocks; it does not, by itself, satisfy the written-program obligation.

---

## §16 — Zone-specific configuration summary

| Surface | **Zone 1 (Personal Productivity)** | **Zone 2 (Team Collaboration)** | **Zone 3 (Enterprise Managed)** |
|---|---|---|---|
| 1–3 SPO / OneDrive / Exchange | Test-with-notifications baseline; SIT rule on customer PII | Enforce after pilot; SIT + Confidential label rules | All rules enforced; EDM + trainable classifier rules; mandatory simulation pass |
| 4 Teams chat & channels | Audit-only beyond default credit-card rule | Block sensitive label matches with override | Block all FSI SITs + Highly Confidential label; no override on EDM matches |
| 5 Endpoint (Devices) | Pilot ring; audit USB / cloud-sync activities | Restrict USB and cloud-sync for Confidential+; require justification | Block USB / unmanaged cloud-sync; block print of Highly Confidential |
| 6 Copilot block-by-label (GA) | Test with notifications | Enforce on Highly Confidential | Enforce on Highly Confidential **and** Confidential |
| 7 Copilot block-by-SIT (preview) | Off or audit only | Test with notifications | Enforce after preview-status caveat documented |
| 8 PP connector classification | Block social channels | Block HTTP Webhook; classify SharePoint / Custom Website channels Non-Business | Allow-list only; block all unauthenticated connectors; dual approval per change |
| 9 PP HTTP endpoint filtering (preview) | Block-list mode | Allow-list or block-list per agent | **Allow-list only** |
| 10 Edge unmanaged AI (preview) | Audit + warn | Block uploads of FSI SIT matches | Block all consumer AI hostnames or block uploads of any labeled content |
| 11 Network DLP unmanaged AI (preview) | Audit | Block on Confidential+ | Block on any FSI SIT or label match |
| 12 Defender for Cloud Apps file policies | Audit on connected apps | Quarantine on label match | Quarantine + remove external collaborators; notify owner |
| 13a Fabric / Power BI | Optional | Notify dataset owner on SIT match | Block export; notify owner; alert |
| 13b On-prem scanner | Optional | Discovery mode | Discovery + enforce labels and protection |
| Adaptive Protection | n/a | Optional (Commercial) | **Required (Commercial)**; static role-based fallback (GCC/GCC High/DoD) |
| Sensitivity labels | Optional labeling; publish taxonomy | Recommended labeling on shared content; quarterly oversharing review | Mandatory labeling; auto-labeling on SPO/OneDrive/Exchange; monthly oversharing review; DKE for NYDFS 500.15 scenarios |

**Zone 3 must complete a documented simulation pass before "Turn it on right away" for every surface.**

---

## §17 — Evidence pack

Use a consistent file-naming convention:

```
Control-1.5_{TenantId}_{Cloud}_{Surface#}_{ArtifactType}_{YYYYMMDD-HHmm-UTC}.{ext}
Control-1.5_{TenantId}_{Cloud}_{Surface#}_{ArtifactType}_{YYYYMMDD-HHmm-UTC}.{ext}.sha256
```

| Artifact | Source | Format | Frequency |
|---|---|---|---|
| Custom-template selection (Copilot policy) | Purview → DLP → Create policy | PNG | On change |
| Two-rule policy export | `Get-DlpComplianceRule` (see PowerShell setup playbook for the same control) | JSON | On change |
| Test-with-notifications mode evidence per policy | Purview → Policy detail | PNG | On change |
| Deterministic test result per surface (user, prompt/action, UTC, alert ID) | Tester log + DLP Alerts + Activity Explorer | CSV + log | Weekly (Z3) / Monthly (Z2) |
| Sensitivity label list and published label policies | `Get-Label`, `Get-LabelPolicy` | JSON | On change |
| Auto-labeling policy locations | `Get-AutoSensitivityLabelPolicy` | JSON | On change |
| Power Platform data-policy export | `Get-DlpPolicy` (PowerApps PowerShell) | JSON | On change |
| Endpoint device onboarding inventory | Purview → Device onboarding | CSV | Weekly |
| Browser coverage report (Edge config + Purview extension) | Intune | CSV | Weekly |
| Defender for Cloud Apps file-policy export | DfCA portal | JSON | On change |
| Fabric / Power BI DLP policy export | Purview → DLP | JSON | On change |
| Information Protection scanner inventory | Scanner console / Purview | CSV | Monthly |
| Adaptive Protection threshold + policy snapshot (Commercial) | IRM | JSON | On change |
| Sovereign-cloud exception register (GCC/GCC High/DoD parity gaps; IRM/AP absence) | Internal tracker | JSON | Quarterly review |
| Override-with-justification telemetry sample | Purview Audit + Sentinel | CSV | Weekly |
| Reg S-P 2024 incident-response readiness attestation | Internal IR program | PDF | Quarterly |

Store in immutable storage (Purview retention label, SharePoint hold, or WORM blob) aligned to [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) retention.

---

## §18 — Validation checklist

Use this as the §15 sign-off checklist before any Zone 3 enforcement decision.

1. [ ] **Surfaces 1–3** (SPO/OneDrive/Exchange) — DLP policy created with rules referencing FSI SITs, EDM classifiers, and Confidential/Highly Confidential labels; in **Test with notifications**; deterministic test produced an alert.
2. [ ] **Surface 4** (Teams) — Default credit-card policy **extended** to U.S. SSN, U.S. Bank Account Number, ABA Routing, MNPI, and label matches; including private channels.
3. [ ] **Surface 5** (Devices/Endpoint DLP) — Devices onboarded (status **Active**) on Win 10/11, Win Server 2019/2022, last 3 macOS; coverage gaps recorded.
4. [ ] **Surface 6** (Copilot block-by-label, GA) — Rule B authored with Highly Confidential (and Confidential per zone matrix); block-by-label scope (no calendar; citations still appear; uploaded-to-prompt files not scanned) communicated to stakeholders.
5. [ ] **Surface 7** (Copilot block-by-SIT, preview) — Rule A authored separately from Rule B (same-rule restriction respected); preview status documented in Zone 3 caveat.
6. [ ] **Surface 8** (PP connector classification) — Live PPAC connector list reviewed; HTTP Webhook and Custom Website channels Blocked in Zone 3.
7. [ ] **Surface 9** (PP HTTP endpoint filtering, preview) — Allow-list mode for Zone 3 with documented endpoint inventory and dual approval; preview status recorded.
8. [ ] **Surface 10** (Edge unmanaged AI, preview) — Edge configuration policy and Purview browser extension deployed via Intune; consumer AI hostnames listed in Sensitive service domains.
9. [ ] **Surface 11** (Network DLP unmanaged AI, preview) — Network activities rule created and tested.
10. [ ] **Surface 12** (Defender for Cloud Apps) — File policies created on connected apps; in Audit only → enforcement after simulation.
11. [ ] **Surface 13a** (Fabric / Power BI) — DLP policy enabled on Premium capacities; rule-match alerts route to dataset owners.
12. [ ] **Surface 13b** (On-prem scanner) — Information Protection scanner deployed; Discovery completed; Enforce mode where in scope.
13. [ ] **Sensitivity labels** exist **and at least one label policy is published** (`Get-LabelPolicy` returns expected policy with `Mode = Enable`); DKE evaluated for NYDFS 500.15 scenarios.
14. [ ] **Auto-labeling**, where used, is scoped to SPO / OneDrive / Exchange only (no "AI interactions" location exists).
15. [ ] **Conditional Access** session controls evaluated for label-restricted access (e.g., block download of Highly Confidential from unmanaged devices).
16. [ ] **Policy tips** with required justification on user override are configured; override telemetry routes to Purview Audit and Sentinel; supervisors review per [Control 2.12](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md).
17. [ ] **Adaptive Protection** — In Commercial: IRM baseline complete; condition added to in-scope DLP rules. In GCC/GCC High/DoD: gap recorded as compensating-control note; static role-based rules in place.
18. [ ] **Audit tier** — Standard vs PAYG distinction documented for `AIAppInteraction` records ([Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md)); SIEM ingestion via [Control 3.9](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md) verified.
19. [ ] **Reg S-P 2024 dual clocks** — Incident-response runbook reflects the 30-day customer notification clock and the 72-hour service-provider notification clock; alert routing tested end-to-end.
20. [ ] **Simulation pass** documented for every Zone 3 surface before flipping to **Turn it on right away**.
21. [ ] Administrator who created the Copilot-location policy is **tenant-scoped**, not Restricted-AU-scoped.

---

## §19 — Common pitfalls

| Pitfall | Symptom | Fix |
|---|---|---|
| Used a Standard template for the Copilot policy | "Microsoft 365 Copilot and Copilot Chat" location not visible | Recreate from **Custom → Custom policy** |
| Combined SIT + label conditions in one Copilot rule | Purview UI rejects save | Split into two rules in the same policy (§8.3) |
| Restricted Administrative Unit-scoped admin | Cannot create/edit Copilot-location policy | Use a tenant-scoped Purview Compliance Admin |
| Verified within 1 hour of saving the Copilot policy | "No matches" — assumed failure | Wait the **full ≥ 4-hour** propagation window before drawing conclusions |
| Devices not onboarded | Endpoint DLP rules silently produce zero matches | Onboard devices via §7.1; confirm **Active** status |
| Default Teams policy left at credit-card-only | SSNs, ABA routing, MNPI in Teams chat not detected | Extend policy per §6 |
| Edge config policy missing for Chrome/Firefox users | §10 unmanaged-AI events missing for those users | Push Purview browser extension via Intune |
| Auto-labeling expected to label Copilot prompts | No labels appear on prompts | Confirm label-based DLP relies on labels **already present** on SPO/OneDrive/Exchange items at prompt time |
| Container label assumed to label files inside | Files inside the Group/Team/Site remain unlabeled | Apply file/email label policy or auto-labeling separately |
| Treating Adaptive Protection as available in GCC High/DoD | Adaptive Protection condition not effective | Use static role-based rules; document compensating-control note |
| Override telemetry not flowing to Sentinel | Supervisor review queue empty | Verify Purview Audit → Sentinel connector ([Control 3.9](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md)) |
| Non-Microsoft channel published without PAYG | DSPM for AI / content-capture telemetry missing | Bind PAYG Azure subscription before publishing channel |
| Blocked-by-label perceived as fully removing Copilot access | Citations still appear in Copilot responses | Communicate documented scope to stakeholders (§8.4) |
| Preview-status capability used as sole Zone 3 control | Examiner finding | Layer with a GA control or document acceptance with sign-off |

---

## §20 — Related playbooks

- **Same control:** `powershell-setup.md`, `verification-testing.md`, and [troubleshooting.md](./troubleshooting.md) under `docs/playbooks/control-implementations/1.5/`
- [Control 1.6 — DSPM for AI portal walkthrough](../1.6/portal-walkthrough.md) — aggregated AI data security view
- [Control 1.7 — Audit logging portal walkthrough](../1.7/portal-walkthrough.md) — durable evidence backbone, Audit Standard vs Premium PAYG
- Control 1.12 Insider Risk Detection portal walkthrough — IRM dependency for Adaptive Protection (path: `docs/playbooks/control-implementations/1.12/portal-walkthrough.md`)
- [Control 1.13 — Sensitive Information Types](../1.13/portal-walkthrough.md) — SIT / EDM / trainable classifier authoring
- [Control 1.15 — Encryption (incl. DKE)](../1.15/portal-walkthrough.md) — Double Key Encryption for NYDFS 500.15 scenarios
- [Control 1.20 — Network isolation](../1.20/portal-walkthrough.md) and [Control 1.21 — Adversarial input logging](../1.21/portal-walkthrough.md) — Conditional Access session controls for label-restricted access
- [Control 2.12 — Supervision (FINRA 3110)](../2.12/portal-walkthrough.md) — supervisor review of override telemetry
- [Control 3.4 — Incident Reporting & RCA](../3.4/portal-walkthrough.md) — Reg S-P 2024 dual-clock IR program
- [Control 3.9 — Sentinel integration](../3.9/portal-walkthrough.md) — SIEM ingestion of DLP and override telemetry

## §21 — Authoritative Microsoft Learn references

- [Learn about Microsoft Purview Data Loss Prevention](https://learn.microsoft.com/en-us/purview/dlp-learn-about-dlp)
- [DLP for Microsoft 365 Copilot location](https://learn.microsoft.com/en-us/purview/dlp-microsoft365-copilot-location-learn-about) — Custom-template requirement, same-rule restriction, block-by-label scope
- [Create and deploy data loss prevention policies](https://learn.microsoft.com/en-us/purview/dlp-create-deploy-policy)
- [Sensitivity labels overview](https://learn.microsoft.com/en-us/purview/sensitivity-labels)
- [Sensitivity labels for containers (Teams / Groups / Sites)](https://learn.microsoft.com/en-us/purview/sensitivity-labels-teams-groups-sites)
- [Apply a sensitivity label automatically](https://learn.microsoft.com/en-us/purview/apply-sensitivity-label-automatically)
- [Double Key Encryption (DKE) overview](https://learn.microsoft.com/en-us/purview/double-key-encryption)
- [Adaptive Protection in Microsoft Purview](https://learn.microsoft.com/en-us/purview/insider-risk-management-adaptive-protection) — sovereign-cloud non-availability
- [Endpoint DLP / device onboarding overview](https://learn.microsoft.com/en-us/purview/device-onboarding-overview)
- [Power Platform DLP overview](https://learn.microsoft.com/en-us/power-platform/admin/wp-data-loss-prevention)
- [Connector endpoint filtering (preview)](https://learn.microsoft.com/en-us/power-platform/admin/connector-endpoint-filtering)
- [Microsoft Purview Information Protection scanner](https://learn.microsoft.com/en-us/purview/deploy-scanner)
- [Defender for Cloud Apps file policies](https://learn.microsoft.com/en-us/defender-cloud-apps/data-protection-policies)
- [DLP for Power BI (Fabric)](https://learn.microsoft.com/en-us/fabric/governance/data-loss-prevention-overview)

---

[Back to Control 1.5](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) | [Troubleshooting](./troubleshooting.md)

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
