# Control 1.13 — Portal Walkthrough: Sensitive Information Types, EDM, Document Fingerprinting, Named Entities, and Trainable Classifiers

**Control:** [1.13 Sensitive Information Types (SITs) and Pattern Recognition](../../../controls/pillar-1-security/1.13-sensitive-information-types-sits-and-pattern-recognition.md)
**Audience:** M365 administrator (US financial services) configuring Microsoft Purview classification primitives in the unified Purview portal for the first time
**Last UI Verified:** May 2026 (Microsoft Purview portal IA: **Solutions → Information protection → Classifiers → Sensitive info types**)
**Last Verified:** 2026-10-16 — Microsoft Learn documentation review only; tenant UI not tested.
**Estimated time:** Firm planning estimate: 12–24 configuration hours, excluding host setup, classifier processing, and data-collection readiness. Do not interpret this estimate or a same-day prompt test as a Microsoft processing SLA; see Steps 5, 8, and 10.

> This playbook provides portal configuration guidance for [Control 1.13](../../../controls/pillar-1-security/1.13-sensitive-information-types-sits-and-pattern-recognition.md). It supports compliance with FINRA Rule 4511 (books and records), FINRA RN 24-09 / Rule 3110 (AI-tool governance), SEC Rules 17a-3 / 17a-4 (broker-dealer records), SEC Regulation S-P (2024 amendments — customer information safeguards and 30-day breach notification), GLBA 501(b) (safeguards rule), SOX 404 (internal controls), PCI-DSS (cardholder data), CFTC Rule 1.31 (swap-dealer recordkeeping), and OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12) / Federal Reserve SR 26-2 (formerly SR 11-7) (model-risk management — applicable when a Trainable Classifier is used as a primary detection control). SITs are a **detection primitive**, not an enforcement layer — by themselves they do not block, redact, retain, or supervise anything. Enforcement is implemented by DLP ([Control 1.5](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md)), DSPM for AI ([Control 1.6](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md)), Communication Compliance ([Control 1.10](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md)), retention ([Control 1.9](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md)), and eDiscovery ([Control 1.19](../../../controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md)).

---

!!! danger "READ FIRST — SITs do not protect Copilot directly; they feed the policies that do"
    A Sensitive Information Type, by itself, does **not** prevent Microsoft 365 Copilot from grounding on a sensitive document, does **not** redact a prompt, and does **not** create a supervision event. SITs are the **detection primitive** consumed by:

    1. **DLP for Microsoft 365 Copilot** — SIT conditions inspect typed prompts for prompt-processing restriction (preview, rollout dependent) or web-search restriction. Grounding-file/email exclusion uses a separate **Sensitivity labels** condition; SIT prompt conditions do not scan grounding files or uploaded-file contents.
    2. **DSPM for AI** — Surfaces "sensitive data shared with Copilot" telemetry using these SITs.
    3. **Auto-labeling** — SIT-driven labels can identify source items for a separate Copilot-location DLP exclusion rule. A label alone does not carry an "exclude from Copilot" property.
    4. **Communication Compliance** — Reviews messages containing matched SITs for MNPI / suitability / NPI conditions.

    **Before you start work in this playbook:**
    2. Confirm the downstream consumer (DLP-for-Copilot, DSPM for AI, sensitivity labels, retention, Communication Compliance) **exists and is licensed** before authoring SITs that have no consumer. Orphan SITs are an audit-finding pattern.
    3. every Microsoft Learn citation in this playbook at the time of deployment — Microsoft has been actively re-organizing Purview classification surfaces and the Copilot DLP location.

---

!!! warning "Read the boundary before you begin"
    SITs **detect patterns** in content. They do **not** retain, block, supervise, or label anything by themselves.

    | If you need to … | Use … |
    
    | **Block** an email / file / Teams message that contains a matched SIT | DLP — [Control 1.5](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) |
    | **Exclude** a sensitive document from Copilot grounding | DLP for Microsoft 365 Copilot (Step 9 below) **and/or** sensitivity-label-driven exclusion ([Control 1.5](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md)) |
    | **Surface** "sensitive data shared with Copilot" telemetry | DSPM for AI — [Control 1.6](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md) (Step 10 below) |
    | **Retain** records that contain matched SITs under WORM / SEC 17a-4(f) / FINRA 4511 | Retention & records management — [Control 1.9](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md) |
    | **Supervise** communications containing matched SITs for MNPI / suitability | Communication Compliance — [Control 1.10](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md) |
    | **Investigate / score** users whose activity correlates with sensitive-data movement | Insider Risk Management — [Control 1.12](../../../controls/pillar-1-security/1.12-insider-risk-detection-and-response.md) |
    | **Place a legal hold** on items containing matched SITs | eDiscovery (Premium) — [Control 1.19](../../../controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md) |
    | **Restrict the grounding scope** of a Copilot agent to specific SharePoint sites | Grounding scope governance — [Control 4.6](../../../controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md) |

    SIT definitions, EDM rule packages, Document Fingerprints, and Trainable Classifiers are **working classification artifacts**, not books-and-records under SEC 17a-4(f) / FINRA 4511. Promote any artifact that must be preserved (SIT XML exports, EDM schema XML, classifier seed-set manifests, Test-pane validation transcripts) into the Evidence Pack (Section 6) and onward to retention / records management ([Control 1.9](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md)).

---

## Section 0 — Coverage and surface inventory

This playbook covers **every** classification primitive Microsoft Purview exposes in the unified portal, because the control catalog entry treats them as **distinct detection paths** and an FSI deployment must reason about them separately.

| Primitive | Where in Purview portal (Apr 2026) | Portal-only? | Covered in step |

| **Built-in pattern SITs** (SSN, Credit Card, US Bank Account, ABA Routing, ITIN, EIN, CUSIP, etc.) | Solutions → Information protection → Classifiers → **Sensitive info types** | No (read-only — built-ins are Microsoft-published) | Steps 1–2 |
| **Custom pattern SITs** (regex + keyword + proximity + confidence) | Information Protection → Classifiers → Sensitive info types → **Create sensitive info type** | No (also XML rule-package cmdlets in Security & Compliance PowerShell) | Step 4 |
| **Keyword dictionaries** | In a custom SIT pattern, choose a primary/supporting **Keyword dictionary** element | No (also PowerShell) | Step 3 |
| **Exact Data Match (EDM)** rule package + schema + hash agent | Solutions → Information protection → Classifiers → **Exact data match** (sensitive info types and stores) | **Mixed** — schema and rule-package authoring portal-or-PowerShell; **EdmUploadAgent.exe** is a Windows agent run on a hash-agent host | Step 5 |
| **Document Fingerprinting** | Solutions → Information protection → Classifiers → Sensitive info types → **Create fingerprint based SIT** | No — both portal (`Create fingerprint based SIT`) and Security & Compliance PowerShell (`New-DlpSensitiveInformationType -FileData`) | Step 6 |
| **Named Entity Recognition (NER)** SITs (bundled — "All full names", "All physical addresses", country bundles) | Solutions → Information protection → Classifiers → Sensitive info types (filter: Microsoft-published, type **Named entity**) | Read-only discovery (consumed by DLP / labels / DSPM-for-AI) | Step 7 |
| **Trainable classifiers** — pre-trained and **custom** | Information Protection or Data Loss Prevention → Classifiers → **Trainable classifiers** (record actual breadcrumb) | Documented portal lifecycle; do not assume a classifier-status cmdlet | Step 8 |
| **DLP for Microsoft 365 Copilot** consumer policy | Solutions → **Data Loss Prevention** → Policies → Create policy → **Custom** template → Location: **Microsoft 365 Copilot and Copilot Chat** | No (also `New-DlpCompliancePolicy` via IPPS) | Step 9 |
| **DSPM for AI** consumer insight | Solutions → **DSPM for AI** (Microsoft is consolidating the classic AI Hub experience into the unified DSPM experience — verify the in-portal label at deployment) | Mostly portal; PowerShell support is narrow | Step 10 |

**Out of scope for this playbook (deferred to peers):**

- Authoring of non-Copilot DLP rules and sensitivity-label policies — see [Control 1.5](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md).
- DSPM-for-AI policy authoring beyond the SIT-consumption verification — see [Control 1.6](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md).
- Communication Compliance policy authoring that consumes these SITs — see [Control 1.10](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md).
- Retention label and records-management authoring — see [Control 1.9](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md).

For supported PowerShell parity see the sibling [`powershell-setup.md`](powershell-setup.md). Fingerprint creation supports `New-DlpSensitiveInformationType -FileData`; custom regex SITs use rule-package XML cmdlets. Classifier training/publishing follows the documented portal workflow.

---

## Section 2 — Prerequisites

### 2.1 License & entitlement matrix per primitive

| Primitive | Minimum tenant SKU | Per-user SKU required for the **author** | Per-user SKU required for **end-user enforcement** | Notes |

| Built-in pattern SITs | Verify consuming feature entitlement | Verify task/role entitlement | License users benefiting from the consuming feature | Credential-scanning and advanced SITs have additional requirements |
| Custom pattern SITs | Verify consuming feature entitlement | Verify task/role entitlement | Consumer policy determines licensing | A visible catalog or tenant SKU alone does not prove entitlement |
| Keyword dictionaries | M365 E3 / E5 | None | None | Same posture as custom pattern SITs |
| **EDM** | Verify advanced classification/consuming-feature entitlement | Schema author permissions; upload user in tenant **EDM_DataUploaders security group** | Verify licenses for benefited users | Not a local group or a requirement to create it specifically as mail-enabled |
| Document Fingerprinting | E5 entitlement for new/modified fingerprints | Verify author entitlement | Verify consuming feature entitlement | E3 customers cannot create/modify fingerprints after April 2023 |
| Bundled Named Entity Recognition | Verify advanced-classification entitlement | Verify role | Verify licenses for benefited users | Missing licensing is not a documented guaranteed "silent no-op"; test actual supported workload behavior |
| Pre-trained Trainable Classifiers | M365 **E5** / E5 Compliance | None | E5 / E5 Compliance | Verify per-classifier availability — Microsoft has retired some pre-trained classifiers |
| Custom Trainable Classifiers | M365 **E5** / E5 Compliance | E5 / E5 Compliance on the admin authoring the classifier | E5 / E5 Compliance | English-only at the time of UI verification |
| **DLP for Microsoft 365 Copilot and Copilot Chat** | Verify the current Purview service-description row and experience | Verify author entitlement | Verify benefited-user licensing for the selected capability | Copilot Chat does not universally require a paid Microsoft 365 Copilot license; prompt restriction is preview/rollout dependent |
| **DSPM for AI** | M365 **E5** / E5 Compliance / E5 Information Protection & Governance | None | None additional | Insight surface — actual blocking still happens in DLP / labels |

> Verify against the [Microsoft 365 Compliance & Security licensing comparison](https://learn.microsoft.com/en-us/office365/servicedescriptions/microsoft-365-service-descriptions/microsoft-365-tenantlevel-services-licensing-guidance/microsoft-365-security-compliance-licensing-guidance) at the time of deployment. Microsoft adjusts SKU bundling on a service-update cadence.

### 2.2 Identity, role, and group prerequisites

In the unified Purview portal, role assignments are managed under **Settings → Roles & scopes → Role groups**. Use canonical short names from `docs/reference/role-catalog.md`:

| Task | Required Purview / M365 role group(s) | Eligible-not-permanent (PIM) recommended? |

| Browse the Sensitive info types catalog (read-only) | **Compliance Data Reader**, **Information Protection Reader**, or any role that contains the *View-Only Sensitive Information Type* RBAC permission | No |
| Create / edit / delete custom pattern SITs and keyword dictionaries | **Information Protection Admin** *or* **Compliance Administrator** | **Yes** — promote to PIM-eligible (activation required) for production tenants |
| Create / edit / delete EDM schemas and rule packages | **Information Protection Admin** *or* **Compliance Administrator** | **Yes** |
| Run **EdmUploadAgent.exe** on the hash-agent host | Authorized work/school user in the tenant's **EDM_DataUploaders security group**; follow documented user authorization | Not a local host group or an assumed certificate workload identity |
| Submit a Trainable Classifier seed set / publish a classifier | **Information Protection Admin** | **Yes** |
| Author a DLP-for-Copilot policy | **Compliance Administrator** *or* **DLP Compliance Management** role group | **Yes** |
| Validate signal in DSPM for AI | **DSPM for AI Administrator** *or* **Compliance Administrator** | No (read-mostly) |
| Pull Unified Audit Log evidence into the Evidence Pack | A non-admin **search-only** identity that holds **View-Only Audit Logs** (**not** the same identity that authored the SIT) | n/a |

**Separation of duties:** the identity that authors a SIT or EDM rule package **must not** be the identity that pulls audit-log evidence demonstrating it works. Maintain at minimum a 4-eyes split (author ↔ reviewer/evidence collector). This separation is what lets the Evidence Pack stand up under FINRA / SEC examination.

### 2.3 Tenant-level prerequisites (verify before Step 1)

- [ ] **Unified Audit Log enabled.** Verify via the Purview portal → **Audit** → search any 24-hour window and confirm rows return. If empty, complete [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) before continuing — without Unified Audit Log you cannot collect the evidence this control requires.
- [ ] **Sensitivity-label policy published** to at least the Zone-1 pilot user set ([Control 1.5](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md)) — required so that auto-labeling driven by these SITs has a label to apply.
- [ ] **DSPM for AI enabled** with at least one Copilot-interactions data source ([Control 1.6](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md)) — required so that Step 10 has a surface to validate against.
- [ ] **Tenant-level "Allow Microsoft to use my tenant's content for product improvement" telemetry setting reviewed** under Purview → Settings — many FSIs disable this. Document the chosen state.
- [ ] **PowerShell baseline installed** on the workstation that will run validation searches (`ExchangeOnlineManagement`, `Microsoft.Graph`, optionally `PnP.PowerShell` for SharePoint validation). See `docs/playbooks/_shared/powershell-baseline.md`.

### 2.4 EDM hash-agent host prerequisites (Step 5 only)

EDM is the only primitive that requires you to stand up infrastructure outside Microsoft 365. Do this work before you reach Step 5.

| Requirement | Specification |

| Operating system | Windows Server 2019 or later (verify supported versions per Microsoft Learn at deployment); domain-joined to the tenant's hybrid identity domain or Entra-joined |
| .NET runtime | .NET version required by the current EdmUploadAgent.exe build — verify per release |
| Compute / RAM | Sized to the **row count and width** of the sensitive table; rule of thumb: 8 vCPU / 32 GB RAM handles tables up to several million rows; tables in the tens of millions need additional capacity. against current Microsoft Learn guidance |
| Storage | The plain-text source CSV is held only transiently on the host **before** hashing; the **hashed** output is what is uploaded. Disk should be encrypted (BitLocker) and access-controlled to the EDM operator group only |
| Network | Outbound HTTPS to the EDM upload endpoint for the tenant's cloud — `https://*.protection.outlook.com` family (verify exact hostnames per Microsoft Learn) |
| Identity | Approved work/school account in the tenant's **EDM_DataUploaders security group**; separate schema-author permissions and feature licensing from upload authorization |
| Audit | Host event logging shipped to your SIEM ([Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md)). The plain-text CSV must never leave this host |
| Source data flow | A documented, repeatable extraction from the source-of-record (DBMS / data-warehouse) to the host. Document the **field-to-column mapping** and the change-data-capture cadence. Do not pull data into the host interactively from a production DBMS without a change-control ticket |

> The plaintext sensitive table never leaves your control. EdmUploadAgent.exe hashes (with the per-rule-package salt) on the host and uploads only the hashed payload. Microsoft never sees the plaintext.

### 2.5 Synthetic-data and naming-convention prerequisites

- **Test pane data must be synthetic.** Never use real customer identifiers. Prevalidate approved positives against the actual SIT: never-issued SSNs are not automatic positives, and the credit-card SIT excludes reserved payment test numbers, even if Luhn-valid. Keep separate positive, negative, and boundary samples with hashes.
- **Naming convention.** All artifacts authored under this control begin with **`FSI-`**. Use the form `FSI-{Pillar}-{Primitive}-{Subject}-{Version}` — for example `FSI-1-SIT-FINRA-CRD-v1`, `FSI-1-EDM-CustomerMaster-v3`, `FSI-1-TC-MNPI-Email-v1`, `FSI-1-DICT-MNPI-Lexicon-v1`, `FSI-1-DOCFP-DealMemoTemplate-v1`. This makes orphan / duplicate / drift detection trivial in a quarterly review.
- **Source control.** Export every custom SIT, EDM schema, EDM rule package, keyword dictionary, and trainable-classifier metadata file to XML / JSON and commit to a versioned repository (`config/purview/sit/`, `config/purview/edm/`, `config/purview/dictionaries/`, `config/purview/trainable-classifiers/`). The portal is the runtime state; the repo is the design-of-record.

---
## Step 1 — Discover and inventory the built-in SITs that matter to FSI

**Goal:** Produce an inventory of the Microsoft-published SITs that align to FSI regulatory obligations, and decide for each one (a) which **confidence level** you will consume, and (b) which **enforcement consumer** ([1.5](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md), [1.6](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md), [1.10](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md), label-driven Copilot exclusion) will use it.

**Roles:** Compliance Data Reader (read-only browse) — promote to Information Protection Admin only when you reach Step 2 (enable / tune / consume).

### 1.1 Open the Sensitive Info Types catalog

1. Sign in at `https://purview.microsoft.com`.
2. In the left navigation choose **Solutions → Information protection**.
3. Choose **Classifiers** in the secondary navigation, then the **Sensitive info types** tab. The list contains hundreds of Microsoft-published SITs plus any custom ones authored in this tenant.
4. Filter the **Type** column to **Microsoft-published** (built-in) for this discovery pass. Filter again to limit to country = **United States** for FSI scope.

!!! info "Portal IA changes"
    Microsoft has been re-organizing the Purview portal IA (the older Compliance portal exposed Sensitive info types under "Data classification"). At UI-verification (April 2026) the canonical path is **Solutions → Information protection → Classifiers → Sensitive info types**. If your tenant shows a different breadcrumb, capture a screenshot or breadcrumb text in your deployment record and against current Microsoft Learn (`sit-sensitive-information-type-learn-about`).

### 1.2 Map FSI obligations to built-in SITs

Build the inventory as a CSV in your Evidence Pack (`Control-1.13_{Tenant}_{Cloud}_BuiltInSITInventory_{date}.csv`). Suggested starter set:

| Built-in SIT | What it detects | Confidence levels offered | FSI obligation it supports | Recommended consumer |

| **U.S. Social Security Number (SSN)** | 9-digit SSN with delimiters or unformatted, with supporting evidence | Low / Medium / High | GLBA 501(b) safeguards; SEC Reg S-P NPI; state breach-notification laws | DLP-for-Copilot (Step 9), sensitivity-label auto-labeling, Communication Compliance |
| **Credit Card Number** | 14–19 digit supported-brand/Luhn-valid PAN; reserved test numbers excluded | Low / High | PCI-DSS; GLBA NPI | DLP outbound + supported typed-prompt restriction |
| **U.S. Bank Account Number** | 6–17 consecutive digits plus a bank-account keyword within 300 characters; no checksum or ABA requirement | Medium | GLBA NPI; FFIEC | Supported typed-prompt restriction, DSPM |
| **ABA Routing Number** | 9-digit routing with checksum + supporting evidence | Low / Medium / High | FFIEC; payment-rail safeguards | DLP outbound, DSPM for AI |
| **U.S. Individual Taxpayer Identification Number (ITIN)** | Nine digits beginning with 9; fourth/fifth digits 50–65, 70–88, 90–92, or 94–99; confidence depends on format/context | Low / Medium / High | GLBA NPI; IRS Pub 1075 (where in scope) | Auto-labeling + supported typed-prompt restriction |
| **EIN detector (verify inventory; custom if absent)** | Firm-validated identifier pattern/context; do not assume a built-in EIN SIT | Authored patterns only | KYC / customer files | DSPM for AI insight only |
| **CUSIP Number** | 9-character security identifier | Low / Medium | MNPI / restricted-list signal under FINRA 5280 (front-running), supervision under FINRA 3110 | Communication Compliance, **not** automatic block (false-positive risk on legitimate research) |

> CUSIP is a textbook example of why **detection ≠ enforcement**. A CUSIP appearing in a research analyst's email is normal business; a CUSIP appearing in a personal Outlook draft from a control-room employee is a supervision event. SITs flag the pattern; Communication Compliance ([Control 1.10](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md)) judges the **context**.

### 1.3 Decide confidence-level posture per SIT

The confidence level you consume is a **policy decision**, not a default. For each SIT in the inventory record:

- **Low confidence** — pattern matched, no supporting evidence required. Use only for low-cost telemetry (DSPM-for-AI insight, audit-only DLP). Never use as the trigger for a hard block.
- **Medium confidence** — pattern matched **plus** at least one supporting keyword/element within the proximity window. Default for FSI auto-labeling and Copilot exclusion.
- **High confidence** — pattern matched **plus** stronger / multiple supporting elements, or a checksum-validated identifier. Default for hard blocks (Exchange transport, endpoint DLP egress).

Record the decision and the justification in the inventory CSV. The justification column is what an examiner reads.

**Verification (Step 1 exit criteria):**

- [ ] Built-in SIT inventory CSV committed to the Evidence Pack with at minimum the seven rows above plus any others the obligation analysis identified.
- [ ] Each row shows the chosen confidence level and a written justification.
- [ ] Each row shows the named downstream consumer (DLP policy ID / label name / Communication Compliance policy / DSPM-for-AI insight) — `TBD` is acceptable here only if Step 9 / Step 10 is on this deployment's roadmap.

---

## Step 2 — Validate and tune built-in SITs in the Test pane

**Goal:** For each in-scope built-in SIT, run a synthetic-data Test-pane validation **before** you wire it to a production DLP / label / DSPM consumer. The Test pane is the only fast-feedback loop Microsoft Purview exposes for SIT precision/recall — do not skip it and do not substitute "wait for Content Explorer to populate".

**Roles:** Information Protection Admin.

### 2.1 Open the SIT and test it

1. Solutions → Information protection → Classifiers → Sensitive info types → click the SIT (e.g., **U.S. Social Security Number (SSN)**).
2. The detail blade opens. Scroll to **Test** (Microsoft has labelled this control variously as **Test**, **Test pattern**, or rendered an inline **"Test"** action in the SIT card — the function is the same: paste or upload a sample and inspect matches by confidence level).
3. Either paste plaintext (synthetic only) into the textbox **or** upload a `.txt` / `.docx` / `.pdf` containing the synthetic seed corpus.
4. Click **Test**. The pane returns matches grouped by confidence level (Low / Medium / High) with the matched substring and the supporting evidence that elevated the match.

### 2.2 Build the synthetic seed corpus

Commit a folder per SIT to the Evidence Pack:

```
config/purview/sit-test-corpus/
  ssn/
    must-match-high.txt        # well-formed SSN with strong supporting evidence ("SSN: 123-45-6789, DOB ...")
    must-match-medium.txt      # well-formed SSN with weaker supporting evidence
    must-match-low.txt         # bare 9-digit string with delimiters
    must-not-match.txt         # 9-digit strings that are NOT SSNs (phone+ext, invoice numbers, ABA routings)
  pan/
    must-match-luhn-valid.txt
    must-not-match-luhn-invalid.txt
  ...
```

**Synthetic-data rules:**

- Keep invalid/reserved SSN examples as negative or boundary cases unless the actual detector test establishes otherwise.
- Reserved payment test PANs are not reliable credit-card SIT positives; use approved synthetic samples prevalidated against the current definition, never a real card.
- Customer names: synthetic names from a published name-generator dataset; never a real customer name + real DOB combination.

### 2.3 Tune the consumer, not the SIT

You almost never edit a Microsoft-published SIT. Instead you tune the **consumer** policy:

- If a built-in SIT misses a real positive at the chosen confidence level, drop the consumer to a lower confidence level **and** add a custom pattern SIT (Step 4) that fills the precision gap.
- If a built-in SIT over-fires, raise the consumer to a higher confidence level and / or add **document-level exceptions** (sensitivity label, sender domain, SharePoint site exclusion) in the consumer policy.
- Capture every Test-pane run as a screenshot **plus** the input corpus and the output JSON (the Test pane exposes a copy-to-clipboard control). Store both in the Evidence Pack.

**Verification (Step 2 exit criteria):**

- [ ] Each in-scope built-in SIT has a Test-pane run captured for must-match-high, must-match-medium, must-match-low, and must-not-match corpora.
- [ ] The consumer policy (DLP / label / Communication Compliance) for each SIT references the **same confidence level** the Test pane validated.
- [ ] No real PII has been pasted into any portal Test pane (verify with a quick search of the Evidence Pack for the synthetic-data markers).

---

## Step 3 — Author keyword dictionaries

**Goal:** Stand up reusable keyword dictionaries (MNPI lexicon, restricted-list issuer names, complaint-detection lexicon) referenced by custom SITs and supported consuming policies. The documented creation workflow is inside a custom SIT's pattern editor, not a required peer **Keyword dictionaries** navigation node. Combined compressed dictionary size is limited to 1 MB per tenant.

**Roles:** Information Protection Admin.

### 3.1 Choose authoring mode

The portal supports two authoring modes:

- **Inline** — paste the keyword list directly into the wizard. Fastest for short lists (a few dozen terms).
- **Upload file** — follow the documented Unicode text-file workflow with one term per line. PowerShell examples read that file as bytes; dictionary cmdlet examples explicitly use UTF-16. Do not claim arbitrary encodings are supported.

> The [keyword-dictionary guide](https://learn.microsoft.com/en-us/purview/sit-create-a-keyword-dictionary) documents a combined post-compression tenant limit of **1 MB**. Splitting dictionaries does not avoid it.

### 3.2 Create the dictionary

1. **Information Protection → Classifiers → Sensitive info types → Create sensitive info type → Create pattern → Add a Primary element → Keyword dictionary**. Choose upload, existing dictionary, or manual entry. Dictionaries can also be supporting elements.
2. Name: follow the convention — `FSI-1-DICT-MNPI-Lexicon-v1`. Keep the version suffix; bump it on any term change (you will reference exact versions in the consumer SIT and the Evidence Pack).
3. Description: one sentence + the change-control ticket ID + the source-of-record (e.g., "Restricted list issuer names sourced from internal Compliance app `RestrictedList`, refreshed nightly via Logic App `RestrictedList-To-Purview-v2`, ticket `CHG-2026-04-118`").
4. Choose **Upload from file** and select the UTF-16 LE CSV (one term per line, no header), or paste terms in the inline editor.
5. Submit. The portal performs a basic format check; a bad encoding fails the upload silently or with a generic error — re-export and try again.

### 3.3 Operationalize the refresh

For lists that change (restricted lists, MNPI deal codenames, issuer ticker maps), the dictionary must refresh on a documented cadence:

- **Push pattern (recommended):** an Azure Logic App / Function pulls the latest list from the system-of-record, encodes UTF-16 LE, and calls `Set-DlpKeywordDictionary -Identity <name> -FileData (Get-Content -Encoding Byte ...)`. Schedule it nightly. Log every refresh to the Evidence Pack.
- **Pull pattern:** a human exports the list manually on a documented cadence and uploads via the portal. Acceptable for slow-changing dictionaries; not acceptable for restricted lists.

### 3.4 Reference from a custom SIT (preview)

Keyword dictionaries are **consumed**, not enforced. You will reference this dictionary from a custom pattern SIT in Step 4 (as a "supporting evidence" element). It can also be referenced directly from a Communication Compliance policy ([Control 1.10](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md)).

**Verification (Step 3 exit criteria):**

- [ ] At least one production keyword dictionary created with `FSI-` naming convention and version suffix.
- [ ] Dictionary source-of-record, refresh mechanism (push or pull), and refresh cadence documented in the Evidence Pack.
- [ ] First refresh executed and logged.
- [ ] Dictionary referenced from at least one consumer (custom SIT in Step 4 **or** Communication Compliance policy in [Control 1.10](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md)) — orphan dictionaries are an anti-pattern.

---
## Step 4 — Author a custom pattern SIT (worked example: FINRA CRD number)

**Goal:** Author a custom pattern SIT with a primary regex, supporting evidence elements, a tuned proximity window, and a defensible confidence-level posture. We use **FINRA CRD number** as the worked example because (a) it is genuinely FSI-specific, (b) **no checksum exists** so confidence cannot honestly exceed Medium, and (c) it exposes every authoring decision a reviewer cares about.

**Roles:** Information Protection Admin.

### 4.1 Define the pattern on paper before opening the wizard

| Element | FINRA CRD decision |

| Primary identifier | `\b\d{6,7}\b` — CRDs are 6 or 7 digits with no internal delimiters. **Anchor with `\b` on both sides** to avoid sub-string matches inside longer numerics. |
| Supporting evidence (any-of within proximity) | Keywords: `CRD`, `CRD #`, `CRD Number`, `Central Registration Depository`, `BrokerCheck`. **And/or**: an FSI-authored keyword dictionary `FSI-1-DICT-FINRA-Lexicon-v1` containing surrounding terms (`U4`, `U5`, `Form U4`, `Form BD`, `representative`). |
| Proximity window | 300 characters. Tighter than the Microsoft default of 300 increases precision but risks false-negatives across line breaks; looser increases false-positives. **Justify the chosen value in the description.** |
| Confidence — Low | Primary regex match, no supporting evidence. **Use only for DSPM-for-AI insight surface; never for a hard block.** |
| Confidence — Medium | Primary regex match + at least one supporting keyword OR one dictionary term within the proximity window. **This is the highest defensible confidence for CRD because no checksum is available.** |
| Confidence — High | **Do not author.** Without a checksum or a structurally distinguishing token there is no honest way to claim High. Document the decision. |

**Anti-pattern (do not author this):**

```
# BAD: confidence:High, regex unanchored, no supporting evidence required
Pattern: \d{6,7}
Confidence: High
Supporting evidence: (none)
Proximity: 300
```

This pattern matches **every** 6-7 digit substring in every document — invoice numbers, ZIP+4 with surrounding digits, order IDs, internal ticket IDs. At High confidence it triggers blocks. This is the textbook regex-only-High-confidence anti-pattern called out in [Control 1.13](../../../controls/pillar-1-security/1.13-sensitive-information-types-sits-and-pattern-recognition.md).

**Good pattern (author this):**

```
Name: FSI-1-SIT-FINRA-CRD-v1
Description: Detects FINRA CRD numbers (6-7 digit Central Registration Depository
identifiers). No checksum exists for CRD; maximum honest confidence is Medium.
Change ticket: CHG-2026-04-201. Owner: Compliance Engineering.
Primary pattern: \b\d{6,7}\b
Supporting evidence (any-of within 300 char proximity):
  Keywords: CRD, CRD #, CRD Number, Central Registration Depository, BrokerCheck
  Dictionary: FSI-1-DICT-FINRA-Lexicon-v1
Confidence Low:    primary match, no supporting evidence  -> consume in DSPM-for-AI only
Confidence Medium: primary match + >=1 supporting element -> consume in DLP-for-Copilot, auto-label
Confidence High:   not authored
```

### 4.2 Run the wizard

1. Solutions → Information protection → Classifiers → Sensitive info types → **Create sensitive info type**.
2. **Name** and **Description** per the convention; paste the description from Section 4.1 verbatim into the description field — examiners read this.
3. **Patterns** → **Create pattern**.
   - Confidence: start with **Medium**.
   - **Primary element** → **Regular expression** → paste `\b\d{6,7}\b`.
   - **Supporting elements** → **Add element** → **Keyword list** → paste the keyword list. **Add element** again → **Dictionary** → choose `FSI-1-DICT-FINRA-Lexicon-v1`.
   - **Character proximity** → 300 (or whatever you justified on paper).
   - Save the pattern.
4. **Add another pattern** → confidence **Low** → primary element only, no supporting evidence, same regex. Save.
5. **Recommended confidence level**: pick **Medium** (this is the value the consumer policy will reference by default; the consumer can still override).
6. **Review and save**.

### 4.3 Test the pattern in the Test pane

1. Open the saved SIT → **Test**.
2. Upload `config/purview/sit-test-corpus/finra-crd/must-match-medium.txt` (synthetic CRDs with surrounding "CRD #" and `Form U4` text). Confirm matches at **Medium**.
3. Upload `must-match-low.txt` (synthetic CRDs with no supporting evidence). Confirm matches at **Low only** — they must not bleed into Medium.
4. Upload `must-not-match.txt` (invoice/ticket numbers and phone extensions). Require no match at the consumer's Medium threshold; a regex-only Low pattern can legitimately match bare lookalike numbers. Reconcile each expected result with the authored patterns.
5. If any of (2)–(4) fails, return to Section 4.1 — do **not** push the SIT to a consumer policy.

### 4.4 Internal-account-number example (different pattern shape)

For an internal account number with a structurally distinguishing prefix and a check digit, you **can** honestly author High confidence. Example specification:

```
Name: FSI-1-SIT-InternalAccount-v2
Primary pattern: \b(ACT|CUS|RET)-\d{8}-[0-9]\b   # prefix + 8 digits + check digit
Supporting evidence: (none required for High because the primary pattern is itself distinguishing)
Validator: only a documented, supported validator; custom uploaded functions are unsupported
Confidence High: only if the authored pattern/evidence and measured results justify it
Confidence Medium: primary match, checksum not evaluated (legacy systems)
```

Do not represent a nine-digit regex as proof of checksum validity. If checksum validation is a business requirement, establish a supported implementation and test it; assigning confidence does not add checksum logic.

**Verification (Step 4 exit criteria):**

- [ ] Custom SIT authored with `FSI-` naming convention.
- [ ] Description field contains: purpose, change-ticket ID, owner, **and** the confidence-level justification (especially the "no High because no checksum" reasoning where applicable).
- [ ] Test-pane runs captured for must-match-Medium, must-match-Low, must-not-match corpora and committed to the Evidence Pack.
- [ ] Actual SIT definition XML exported from its rule package's `SerializedClassificationRuleCollection`; CLIXML is only an object snapshot, not importable definition XML.
- [ ] No SIT in the tenant carries Confidence = High **without** either a checksum or a structurally distinguishing primary token. (Run a quarterly review against this assertion.)

---

## Step 5 — Stand up Exact Data Match (EDM)

**Goal:** Detect the **exact** rows of a sensitive table (customer master, account master, employee master, restricted-list securities) inside Microsoft 365 content. EDM is the right primitive when "the SSN of an actual customer of ours" must be detected and "any-9-digit-with-supporting-evidence" is too noisy.

**Roles:** Information Protection Admin (schema and rule package); EDM_DataUploaders group member (hash agent run); platform / data engineering (host stand-up and source-data extraction).

EDM is a 9-substep workflow. Skipping a substep is the dominant EDM failure mode in audits.

### 5.1 Substep 1 — Define and version the schema

The schema identifies searchable primary fields and nonsearchable supporting fields; supporting fields are not cleartext return columns. The primary SIT must extract the value before EDM lookup, and the configured supporting values/proximity must also match.

```xml
<EdmSchema xmlns="http://schemas.microsoft.com/office/2018/edm">
  <DataStore name="FSI_CustomerMaster" description="FSI customer master EDM schema v3" version="3">
    <Field name="SSN"        searchable="true"  caseInsensitive="true"  ignoredDelimiters="-, "/>
    <Field name="AccountNum" searchable="true"  caseInsensitive="true"  ignoredDelimiters="- "/>
    <Field name="LastName"   searchable="false" caseInsensitive="true"/>
    <Field name="DOB"        searchable="false" caseInsensitive="true"/>
    <Field name="ZIP"        searchable="false" caseInsensitive="true"/>
  </DataStore>
</EdmSchema>
```

Constraints (verify per release against `sit-create-edm-sit-unified-ux`):

- The [schema guide](https://learn.microsoft.com/en-us/purview/sit-get-started-exact-data-match-create-schema) currently says up to **ten searchable fields** in the wizard, but still says **five** in its manual XML steps. Verify the selected workflow; do not use the previous 32-searchable-column claim.
- The EDM overview documents up to **100 million rows**; check actual schema/upload validation and current requirements.
- Validate the source file against the actual installed agent/schema; do not infer file-size limits from row limits.
- At least one column **must** be `searchable="true"`.
- Column names in the schema **must** match the CSV column headers exactly.

Commit the schema XML to `config/purview/edm/schemas/FSI_CustomerMaster.v3.xml`.

### 5.2 Substep 2 — Author the EDM rule package

The rule package is what binds the schema to the SIT detection logic — which searchable column triggers a match, what supporting evidence is required, and at what confidence level.

1. Solutions → Information protection → Classifiers → **Exact data match** → **EDM sensitive info types** → **Create EDM sensitive info type**.
2. Choose the schema (`FSI_CustomerMaster v3`) — if it is not present yet, complete substep 3 first to upload the schema.
3. Name the SIT: `FSI-1-EDM-CustomerMaster-SSN-v3`.
4. **Primary element** → `SSN` (the searchable column).
5. **Supporting elements** within proximity (recommended): `LastName` keyword list **and** `AccountNum` regex. Two supporting elements is a defensible minimum for High confidence on EDM.
6. Confidence and proximity: 300 chars; High requires primary + 2 supporting; Medium primary + 1; Low primary only (use Low only for telemetry).
7. Save. Export the rule package XML to `config/purview/edm/rule-packages/FSI-1-EDM-CustomerMaster-SSN-v3.xml`.

### 5.3 Substep 3 — Stand up the hash agent host

Per Section 2.4. Verify before continuing:

- Windows Server up, patched, BitLocker on.
- .NET runtime version per current EdmUploadAgent.exe build.
- Outbound HTTPS to the EDM upload endpoint family (`*.protection.outlook.com` family (verify exact hostnames per Microsoft Learn at deployment).
- Service identity is a member of `EDM_DataUploaders`.

### 5.4 Substep 4 — Install EdmUploadAgent.exe

Download EdmUploadAgent.exe from the Microsoft download surface (Microsoft has moved this binary between Download Center and Microsoft 365 Admin Center → Setup → Compliance — verify current location at deployment). Install to `C:\Program Files\Microsoft\EdmUploadAgent\` on the hash-agent host. Confirm the binary version matches the version Microsoft Learn documents for the current EDM service.

### 5.5 Substep 5 — Protect hashing outputs and salt

The [documented Upload Agent](https://learn.microsoft.com/en-us/purview/sit-get-started-exact-data-match-hash-upload) automatically adds salt by default. Optional `/Salt <saltvalue>` supplies a custom value; the guide warns that custom-salt users cannot return to the standard agent workflow for that use case. Do not invent a binary-salt parameter contract. Protect `.EdmHash`/`.EdmSalt` outputs and source data under the firm's approved custody controls.

**Salt lifecycle:** any firm-mandated rotation is an operational policy, not a Microsoft annual product requirement. Review the documented custom-salt restrictions and fully rehash/reupload/retest when changing it.

### 5.6 Substep 6 — Hash and upload

Extract the source data to the host as a UTF-8 CSV with column headers matching the schema. Then:

```powershell
# On the approved Windows host, signed in as the authorized EDM_DataUploaders user
Set-Location 'C:\Program Files\Microsoft\EdmUploadAgent'
.\EdmUploadAgent.exe /SaveSchema /DataStoreName FSI_CustomerMaster /OutputDir 'D:\edm-staging'
.\EdmUploadAgent.exe /ValidateData `
  /DataFile 'D:\edm-staging\customer-master-2026-04-15.csv' `
  /Schema 'D:\edm-staging\FSI_CustomerMaster.xml'
.\EdmUploadAgent.exe /CreateHash `
  /DataFile 'D:\edm-staging\customer-master-2026-04-15.csv' `
  /HashLocation 'D:\edm-staging\hashes' `
  /Schema 'D:\edm-staging\FSI_CustomerMaster.xml'

.\EdmUploadAgent.exe /Authorize
.\EdmUploadAgent.exe /UploadHash /DataStoreName FSI_CustomerMaster `
  /HashFile 'D:\edm-staging\hashes\customer-master-2026-04-15.EdmHash'
.\EdmUploadAgent.exe /GetDataStore
.\EdmUploadAgent.exe /GetSession /DataStoreName FSI_CustomerMaster
```

Use the exact saved schema and generated hash filename from the installed agent. `/Authorize` uses the documented work/school-user flow, not an assumed certificate workload identity. Plaintext is hashed locally; only hashed data is uploaded. Microsoft recommends same-version agents on separate offline hashing and online upload computers for isolation.

### 5.7 Substep 7 — Daily refresh

Schedule the extract → hash → upload pipeline daily via Windows Task Scheduler or an Azure Automation runbook that invokes the host. Record every run to the Evidence Pack (success / failure, row count, hash count, upload duration, any rows rejected for missing required columns).

### 5.8 Substep 8 — Verify with the Test pane

1. Open the EDM SIT → **Test**.
2. Upload a synthetic document containing **one row from the actual hashed dataset** (use a synthetic seed row that you injected into the source table for this purpose — never a real customer row outside a controlled audit).
3. After upload and indexing are confirmed, wait an hour before testing (also wait an hour after EDM SIT changes). Confirm the actual **EDM SIT**, not only its primary pattern SIT. Existing files may need separate reclassification.
4. Upload a document containing a **fabricated row** (same shape, never present in the dataset). Confirm zero matches — this is what proves EDM is doing exact-data-match and not pattern matching.

### 5.9 Substep 9 — Operational monitoring

Wire the following to your SIEM / observability stack:

- Daily EdmUploadAgent run success/failure (alert on consecutive failures).
- Row-count drift between consecutive runs > 5 % (alert; investigate source-system change).
- Hash-upload latency above an SLO (alert).
- Salt-rotation due-date approaching (ticket).
- A schema-drift signal: source-system column add / rename detected before the next hash run (block the run, raise a change-control ticket — uploading hashes against a drifted schema silently produces a broken SIT).

**Verification (Step 5 exit criteria):**

- [ ] Schema XML and rule package XML committed to source control.
- [ ] Salt stored in the secret store; salt-rotation procedure documented and a calendar item created.
- [ ] First successful hash + upload logged with row count, hash count, run identity, run timestamp.
- [ ] Test pane confirms a known-hashed synthetic row matches; a fabricated row does not.
- [ ] Daily refresh schedule active and the first three days of runs captured to the Evidence Pack.
- [ ] SIEM alerts wired for run failure, row-count drift, salt-rotation due, schema drift.

---

## Step 6 — Document Fingerprinting

**Goal:** Detect matching template **text**, not visual layout. [Document fingerprinting](https://learn.microsoft.com/en-us/purview/document-fingerprinting) supports configured partial or exact text matching; image-only/password-protected files and files larger than 4 MB are unsupported. Templates require 256–204,800 extracted characters; embedded-document text is not considered.

**Roles:** Information Protection Admin.

### 6.1 Choose the right template

The template you fingerprint **must be empty** (the blank form). If you fingerprint a pre-filled template you will inadvertently fingerprint the filled-in content, producing wide false positives across any document that re-uses the same boilerplate.

Good candidates for FSI:

- The blank deal-memo / pitch-book template used by the M&A team.
- The blank restricted-list addition request form used by control-room.
- The blank Form ADV / Form U4 / Form U5 templates (where used internally).

Bad candidates:

- A filled-in deal memo (anti-pattern — see Section 7).
- A template whose structure is dominated by company boilerplate that appears in **every** internal document (will FP on company letterhead).

### 6.2 Create the fingerprint-based SIT

1. Solutions → Information protection → Classifiers → Sensitive info types → **Create fingerprint based SIT**.
2. Name: `FSI-1-DOCFP-DealMemoTemplate-v1`.
3. Upload the **empty** template `.docx` / `.dotx` / `.pdf`.
4. The portal creates the fingerprint. PowerShell parity is documented with `New-DlpSensitiveInformationType -FileData <template-bytes> -ThresholdConfig ... -IsExact ...`; see the sibling example.
5. Set a default confidence level (Medium is a reasonable default; consumers can override).
6. Save.

### 6.3 Test and consume

1. Test pane → upload a copy of the template with synthetic content typed in. Confirm the fingerprint matches.
2. Test pane → upload an unrelated document. Confirm zero match.
3. Reference the fingerprint SIT from a DLP rule, sensitivity-label auto-labeling rule, or Communication Compliance policy as needed.

**Verification (Step 6 exit criteria):**

- [ ] At least one fingerprint SIT created from an **empty** template.
- [ ] Test pane confirms structural match against a filled-in copy and zero match against an unrelated document.
- [ ] Source template committed to source control as the design-of-record (with the change-ticket reference) — bumping the template version requires re-fingerprinting and a new SIT version.

---
## Step 7 — Discover and consume Named Entity Recognition (NER) SITs

**Goal:** Inventory supported named-entity SITs such as **All full names**, **All physical addresses**, and **All medical terms and conditions**. Credential scanning is a distinct SIT family, not a named-entity country bundle. Named-entity SITs cannot be edited or copied.

**Roles:** Information Protection Admin (consumption); Compliance Data Reader (discovery).

### 7.1 Inventory the available NER SITs

1. Solutions → Information protection → Classifiers → Sensitive info types.
2. Filter **Type** = **Named entity** (Microsoft-published).
3. Inventory each one to the Evidence Pack: name, what it detects, the supported language(s), and the **license requirement** (NER requires E5 / E5 Compliance on the user whose content is evaluated — Section 2.1).

Examples likely present at deployment (verify per release — Microsoft adds, removes, and renames bundles between updates):

- **All Full Names** — detects person names across many cultures.
- **All Physical Addresses** — detects postal addresses.
- **All Medical Terms And Conditions** — health information (HIPAA where in scope; FSI generally only when administering employee benefits).
- Region-specific physical-address SITs; verify each actual definition and language coverage.

### 7.2 Consume an NER SIT

NER SITs reference **into** DLP rules, sensitivity-label auto-labeling, and DSPM-for-AI insights exactly like pattern SITs:

1. From a DLP rule (or a custom SIT's "supporting evidence" element list): **Add condition → Content contains → Sensitive info types → search for the NER SIT name → Add**.
2. Pick a supported confidence level using the actual definition and measured results. Named-entity SITs use complex dictionary/pattern designs; neither their High nor pattern-SIT High universally means checksum validation. Do not translate NER High to pattern Medium as a product rule.

### 7.3 Document the residual risk

Named-entity detection can have false positives and negatives; validate rather than assuming trainable-model semantics. Capture in your Evidence Pack:

- The list of NER SITs you consume.
- The downstream consumer policy and the consumed confidence level.
- A statement that the residual FP/FN risk has been reviewed and accepted (with the accepting business owner named).
- The compensating control (typically: NER signals are **not** the sole evidence for any retention or supervision obligation; they are augmenting signals to pattern SITs and EDM).

**Verification (Step 7 exit criteria):**

- [ ] NER inventory captured to the Evidence Pack with license requirement noted.
- [ ] Each consumed NER SIT has a named consumer policy and a documented residual-risk acceptance.
- [ ] No retention obligation, supervision obligation, or hard-block decision rests on an NER signal alone.

---

## Step 8 — Trainable Classifiers (pre-trained and custom) — with the FSI Governance Gate

**Goal:** Use trainable classifiers for the cases pattern SITs cannot honestly express (MNPI-style language in email, complaint detection, "looks-like-a-resume", source code). Trainable classifiers are **statistical models**; before they are consumed in any control surface that supports a regulatory obligation, they must pass the FSI Governance Gate.

**Roles:** Information Protection Admin (authoring); Model Risk Management owner (Governance Gate sign-off — see [Control 1.13](../../../controls/pillar-1-security/1.13-sensitive-information-types-sits-and-pattern-recognition.md) §FSI Governance Gate); Compliance Officer (acceptance for production consumption).

### 8.1 The FSI Governance Gate (read this before authoring a classifier)

A trainable classifier consumed in a control surface that supports a recordkeeping or supervisory obligation is **a model under OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12) / Federal Reserve SR 26-2 (formerly SR 11-7)**. Before promoting a classifier to a production consumer:

| Gate item | Requirement |

| **MRM intake** | The classifier is registered in the firm's Model Risk Management inventory with an owner, intended use, and a tier rating |
| **Lifecycle clarity** | Document whether the classifier is **Preview** or **GA** at the time of consumption (Microsoft has Preview-only trainable classifiers — verify per release) |
| **Language scope** | Custom classifiers support English only; pretrained support is definition-specific. Record supported languages and unsupported content, without assuming a guaranteed silent no-op |
| **Out-of-sample validation** | A held-out validation set (not part of the seed corpus) achieves a documented precision and recall acceptable for the intended use; dataset and metrics archived in the Evidence Pack |
| **Periodic re-validation** | Calendar item to re-run validation at least annually and on every material change to the seed corpus |
| **Not-the-sole-evidence rule** | A trainable classifier signal is **not the sole evidence** for any SEC 17a-4 / FINRA 4511 retention decision or any FINRA 3110 supervisory determination. Pair with pattern SIT or EDM, or escalate to manual review under [Control 1.10](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md) |
| **Accept-in-writing** | The Compliance Officer signs an acceptance memo that names the classifier version, the consumer policy, the residual risk, and the compensating control. Memo lives in the Evidence Pack |

> Trainable classifiers are powerful and appropriate for many FSI use cases. The Gate is what makes them **defensible** to a regulator — it is not a recommendation against using them.

### 8.2 Inventory pre-trained classifiers

1. Solutions → Information protection → Classifiers → **Trainable classifiers**.
2. Inventory the pre-trained list to the Evidence Pack with status (Preview / GA), supported language, and Microsoft-published intended use. Microsoft has retired some pre-trained classifiers between releases — re-inventory at every quarterly review.
3. For each pre-trained classifier you intend to consume, walk it through the Governance Gate (Section 8.1).

### 8.3 Author a custom trainable classifier (worked example: MNPI in email)

1. **Trainable classifiers → Create trainable classifier**.
2. Name: `FSI-1-TC-MNPI-Email-v1`. Description: intended use, MRM tier, owner, ticket.
3. **Seed sets:** provide **50–500 positive** and **150–1,500 negative** text-based documents in separate, dedicated SharePoint folders accessible to the author (not OneDrive or Teams folders). Document provenance and use approved content-handling procedures. Image-only files are unsupported.
4. Submit and observe the actual portal status. The documented preview workflow describes seed processing within 24 hours or less; this is not a contractual SLA. Do not assume a `Get-Classifier` cmdlet exists.
5. When training completes, the portal opens a **publish-ready** review workflow. **Do not publish yet.**
6. **Test (the publish-ready workflow):** review the classifier's predictions against a separate set of documents (the held-out validation set per Governance Gate item 4). The portal records your accept/reject decisions and feeds them back to refine the model. Iterate until precision and recall are acceptable.
7. **Publish.** Verify support in each consuming workload. Communication Compliance supports Microsoft-provided classifiers only, not custom classifiers. Published custom classifiers cannot be retrained; replacement requires a new classifier and consumer-binding validation.

### 8.4 Consume the classifier

Reference exactly like a SIT from any consumer policy. Confidence levels are returned by the model — treat them with the not-the-sole-evidence rule (Section 8.1).

**Verification (Step 8 exit criteria):**

- [ ] Pre-trained classifier inventory captured (status, language, license).
- [ ] Every consumed classifier (pre-trained or custom) has a Governance Gate package in the Evidence Pack: MRM ticket, lifecycle status, validation dataset and metrics, acceptance memo, re-validation calendar item.
- [ ] No production policy uses a classifier as sole evidence for a SEC 17a-4 / FINRA 4511 retention decision or a FINRA 3110 supervisory determination.
- [ ] Custom classifier seed-set manifest committed to source control (extract methodology, document count, language, redaction posture, ticket reference).

---

## Step 9 — DLP for Microsoft 365 Copilot (consumer policy that uses the SITs)

**Goal:** Test two distinct controls: supported SITs in **typed prompt text**, and **sensitivity labels** on grounding files/emails. A source-file SIT match is not itself a Copilot grounding-exclusion condition. Follow the [current Copilot DLP documentation](https://learn.microsoft.com/en-us/purview/dlp-microsoft365-copilot-location-learn-about).

**Roles:** Compliance Administrator or DLP Compliance Management role group.

### 9.1 Confirm the Copilot location is enabled in your tenant

1. Solutions → **Data Loss Prevention** → **Policies**.
2. Verify the **Microsoft 365 Copilot** location is selectable in the Create-policy wizard. If it is not, confirm tenant licensing (Section 2.1) and against `dlp-microsoft365-copilot-location-learn-about` Microsoft Learn — Microsoft has staged availability per cloud and per service-update.

### 9.2 Author the policy

1. **Create policy → Custom → Custom policy**.
2. Name: `FSI-1-DLP-Copilot-SIT-Exclusion-v1`. Description: purpose, ticket, owner, and the **simulation→audit→enforce** rollout plan with dates.
3. **Locations:** turn on **Microsoft 365 Copilot and Copilot Chat**. Turn **off** every other location for this policy — keep this policy single-purpose. Cross-location DLP belongs in a separate policy authored under [Control 1.5](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md).
4. **Policy settings → Rules → Create rule**.
5. For prompt protection, choose **Content contains → Sensitive information types**, selecting documented built-in/custom SITs validated for typed text. Choose **Prevent Copilot from processing content → Processing prompts** (preview; verify tenant rollout), or the distinct **Performing Web Searches** action. Do not assume EDM, fingerprints, named entities, or trainable classifiers are supported by this condition.
6. For grounding exclusion, create a **separate rule** with **Content contains → Sensitivity labels** and **Prevent Copilot from processing content**. Apply labels through an independently tested labeling workflow; this rule does not auto-label files. SIT and label conditions cannot coexist in the same rule.
7. **User notifications and policy tips:** configure supported notifications. To customize the help destination, enable Policy Tips and **Provide a compliance URL for the end user to learn more about your organization's policies**, using a full accessible HTTPS URL. Only the **Learn about access restrictions** link destination changes, not the standard block-message/link text.
8. **Mode:** start in **Test with notifications** (simulation mode) for at least one full week. Review the simulation report daily. Promote to **Turn on** only after the false-positive rate is acceptable and the help-desk has been briefed.

### 9.3 Validate the policy

1. Record the initiating user's inclusion/exclusion, policy/rule IDs, mode, host, and rollout. User scope is valid; do not replace it with an agent GUID or SharePoint URL. Administrative units are unsupported.
2. Test a prevalidated synthetic SIT **typed directly into the prompt**, with a paired negative. Uploading a file does not test prompt SIT inspection; file contents aren't scanned by that condition.
3. Separately apply an excluded sensitivity label to a source file that the user otherwise can access, and ask Copilot to summarize it. On enforcement, content is excluded but a citation can remain. This is not universal response redaction.
4. Capture simulation and turned-on behavior separately. Allow up to four hours for policy updates. In Word/Excel/PowerPoint, reopen the file after mid-session labeling. Supported email exclusion applies to emails sent on/after January 1, 2025, not calendar invites.
5. If web-search restriction is selected, verify it independently: permitted internal-grounded answers can still occur. Preserve available telemetry without requiring an invented one-to-one UAL/DLP correlation. Copilot Studio connector coverage requires separate tests.

**Verification (Step 9 exit criteria):**

- [ ] DLP-for-Copilot policy authored with the in-scope SITs at validated confidence levels.
- [ ] Simulation-mode (Test with notifications) report captured for one full week with FP/FN summary.
- [ ] Production prompt-SIT and labeled-grounding tests captured separately, with supported positive/negative controls.
- [ ] Policy-tip text reviewed and approved by Communications / Legal.
- [ ] Sensitivity-label-driven exclusion path documented as the GA fallback if SIT-driven prompt restriction is Preview-only in your cloud.

---

## Step 10 — Validate the SITs in DSPM for AI

**Goal:** Confirm that custom SITs, EDM SITs, and trainable classifiers authored in Steps 4–8 surface in DSPM-for-AI insights so the firm has telemetry on "sensitive data shared with Copilot".

**Roles:** DSPM for AI Administrator (validation); Information Protection Admin (re-tune SIT if it does not surface).

### 10.1 Open DSPM for AI

1. Use **Solutions → DSPM** for the [current DSPM experience](https://learn.microsoft.com/en-us/purview/data-security-posture-management-learn-about), then **Discover → Activity explorer → AI activities**. The previous experience remains **DSPM for AI (classic)**. Record which experience is actually used; UI not tested in this review.
2. Confirm at least one Copilot-interactions data source is wired in ([Control 1.6](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md)). If not, complete Control 1.6 before continuing.

### 10.2 Seed and verify

1. As a pilot user, perform two synthetic-data prompts in Microsoft 365 Copilot Chat:
   - *"Pull the SSN for customer 12345 from the customer master."* (will / should match the EDM SIT and the SSN built-in SIT).
   - *"Look up CRD 1234567 in our records."* (will / should match the FINRA-CRD custom SIT at Medium confidence).
2. For classic DSPM new policies, allow at least 24 hours for data collection, not a maximum delivery SLA. For new DSPM initial setup, Microsoft says allow a day or so. Record actual readiness.
3. In DSPM for AI, open the **Sensitive data shared with Copilot** insight (the exact label may differ — verify per release). Confirm both interactions surface and that the matched SIT name shown is the `FSI-` artifact you authored, not just the bare built-in `U.S. Social Security Number`.
4. If the custom SIT does not surface but the built-in does: the custom SIT may not have been picked up by the DSPM for AI signal pipeline. Verify the SIT is **published** (not draft), the confidence level the signal pipeline consumes is at or below your tuning, and re-test after the propagation window. Open a Microsoft support ticket if the custom SIT remains invisible after 24 hours of repeated seeding.

### 10.3 Wire the policy templates

DSPM for AI ships policy templates ("Detect risky AI usage", "Detect sensitive info in AI prompts and responses", names verify per release) that consume these SITs. Enable the templates that match the firm's risk appetite, scope to the pilot population first, then expand to enterprise. Capture template state to the Evidence Pack.

**Verification (Step 10 exit criteria):**

- [ ] Both seeded prompts surface in DSPM-for-AI insights with the **custom** SIT names visible (not just built-ins).
- [ ] At least one DSPM-for-AI policy template is enabled and scoped at the chosen rollout stage.
- [ ] Propagation window for "sensitive data shared with Copilot" measured and documented (the actual time observed in your tenant — useful for incident-response runbooks).

---
## Section 6 — Evidence Pack

The Evidence Pack is the durable, examiner-facing artifact set that demonstrates Control 1.13 was implemented as designed. Promote it into retention / records management ([Control 1.9](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md)) on the same cadence the firm retains other compliance design records (typically 7 years for FSI; verify against firm policy).

### 6.1 Naming convention

Every Evidence Pack artifact name follows:

```
Control-1.13_{TenantId}_{Cloud}_{ArtifactType}_{YYYYMMDD-HHmm-UTC}.{ext}
```

- `TenantId` — the tenant GUID (do not use a friendly name; the GUID is unambiguous across cloud rebrands).
- `Cloud` — `Commercial`.
- `ArtifactType` — see the inventory table below.
- Timestamp in UTC to the minute, suffix `-UTC` to make the time zone explicit.

Example: `Control-1.13_5e3b...c2_Commercial_BuiltInSITInventory_20260415-1432-UTC.csv`.

### 6.2 Required artifact inventory

| ArtifactType token | What it contains | Source step |

| `BuiltInSITInventory` | CSV of in-scope built-in SITs, chosen confidence levels, justifications, named consumers | Step 1 |
| `SITTestRun` | Test-pane input corpus, output JSON, screenshot — one folder per SIT per run | Steps 2, 4, 5, 6 |
| `KeywordDictionary` | Source CSV (UTF-16 LE), refresh-mechanism description, refresh log | Step 3 |
| `CustomSITExport` | Definition XML from `Get-DlpSensitiveInformationTypeRulePackage`'s `SerializedClassificationRuleCollection`; CLIXML is an object snapshot, not authorable SIT XML | Step 4 |
| `EDMSchema` | Schema XML | Step 5.1 |
| `EDMRulePackage` | Rule-package XML | Step 5.2 |
| `EDMHashAgentRunLog` | Per-run record: identity, row count, hash count, upload duration, exit code | Step 5.6, 5.7 |
| `EDMSaltRotationRecord` | Salt-rotation event: previous salt fingerprint, new salt fingerprint, change ticket, operator | Step 5.5 |
| `DocFingerprintTemplate` | The empty source template that was fingerprinted | Step 6 |
| `NERInventory` | NER SIT inventory + residual-risk acceptance | Step 7 |
| `TrainableClassifierGate` | Governance-Gate package per classifier (MRM ticket, lifecycle status, validation dataset and metrics, acceptance memo, re-validation calendar item) | Step 8 |
| `TrainableClassifierSeedManifest` | Seed-set manifest: extract methodology, document count, language, redaction posture, ticket | Step 8.3 |
| `DLPCopilotPolicyExport` | DLP-for-Copilot policy export (`Get-DlpCompliancePolicy ... | Export-Clixml`) | Step 9 |
| `DLPCopilotSimulationReport` | One-week simulation-mode report with FP/FN summary | Step 9.2 |
| `DLPCopilotProductionValidation` | Before/after Copilot-grounding test transcripts | Step 9.3 |
| `DSPMforAIValidation` | Screenshot or export showing the seeded prompts surfacing in "sensitive data shared with Copilot" with custom SIT names visible | Step 10 |
| `RolesMatrix` | The per-step roles matrix (Section 8) snapshot at the deployment date | Section 8 |
| `SHA256Manifest` | A single `manifest.sha256` covering every other artifact in the pack | All |

### 6.3 SHA-256 manifest

Generate the manifest after the pack is otherwise complete:

```powershell
$pack = 'D:\evidence\Control-1.13\2026-04-15'
Get-ChildItem -Path $pack -Recurse -File | Where-Object Name -ne 'manifest.sha256' |
  ForEach-Object {
    "{0}  {1}" -f (Get-FileHash $_.FullName -Algorithm SHA256).Hash, $_.FullName.Substring($pack.Length + 1)
  } | Set-Content -Path (Join-Path $pack 'manifest.sha256') -Encoding ASCII
```

The manifest itself is **not** included in its own hash list (chicken-and-egg). Its integrity is established by the custody handoff in Section 6.4.

### 6.4 Custody handoff

The pack is generated by the implementation team and then transferred to the records-management custodian under the firm's documented evidence-handling procedure. The handoff record includes:

- Pack identifier (folder name).
- SHA-256 of the `manifest.sha256` file itself.
- Timestamp and named identities of the handing-off and receiving roles.
- Storage location in the records system.
- Retention class assigned (per [Control 1.9](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md)).

### 6.5 Refresh cadence

| Artifact type | Refresh cadence |

| `BuiltInSITInventory`, `NERInventory`, `RolesMatrix` | Quarterly + on every Microsoft service-update release note that touches classification |
| `SITTestRun` (regression set) | Quarterly + on every change to a custom SIT, EDM rule package, dictionary, or classifier |
| `EDMHashAgentRunLog` | Daily (the rolling 90-day log; archive to long-term storage monthly) |
| `EDMSaltRotationRecord` | On every salt rotation (annually minimum) |
| `TrainableClassifierGate` | On every classifier publish, on every re-validation, annually at minimum |
| `DLPCopilotSimulationReport`, `DLPCopilotProductionValidation`, `DSPMforAIValidation` | Quarterly + on every policy edit |

---

## Section 7 — Anti-patterns (do not do these)

These are the failure modes most often surfaced in audit findings against this control. Each one corresponds to a guardrail elsewhere in this playbook.

1. **Regex-only SIT at Confidence = High** — primary regex match with no supporting evidence and no checksum, scoped to a hard block. Produces wide false positives and policy-tip fatigue. Authored against the Step 4 anti-pattern call-out.
2. **Custom SIT without supporting evidence and without proximity tuning** — even at Medium, a bare regex over a 300-character window will FP on adjacent unrelated content. Always pair primary regex with a keyword list **or** dictionary within a justified proximity window.
3. **Unmanaged EDM salt lifecycle** — preserve approved custody and any firm-mandated rotation schedule. Do not call annual rotation a Microsoft requirement or replace the documented autogenerated/custom-salt workflow with an invented binary-salt procedure.
4. **EDM uploaded against a drifted source schema** — source-system column add/rename happens silently; the next hash run produces a broken SIT that returns zero matches and gives false comfort. Wire the Step 5.9 schema-drift signal.
5. **Trainable classifier promoted without out-of-sample validation** — relying on the portal's in-training acceptance loop as the sole quality signal. Hold out a separate validation set and archive metrics in the Governance Gate.
6. **Trainable classifier as sole evidence for a SEC 17a-4 / FINRA 4511 retention decision or a FINRA 3110 supervision determination** — statistical models are augmenting signals; the supporting record must rest on pattern SIT or EDM or human review.
7. **Document Fingerprint of a pre-filled template** — fingerprints the filled-in content and produces wide FPs. Always fingerprint the empty form.
8. **Custom SITs without the `FSI-` naming prefix** — defeats orphan-detection sweeps and makes the quarterly review impossible. All custom SITs, dictionaries, EDM rule packages, fingerprints, and trainable classifiers carry the `FSI-` prefix.
9. **Real PII pasted into the Test pane** — a Test-pane input is logged and persisted within the service. Synthetic data only; verify the synthetic-data markers are present in every Test-pane corpus committed to the Evidence Pack.
10. **Orphan SITs / dictionaries / classifiers** — artifacts authored with no consumer policy. Either there is a downstream consumer (DLP / label / Communication Compliance / DSPM-for-AI) named at authoring time or the artifact does not get authored. Quarterly orphan sweep using PowerShell — see sibling `verification-testing.md`.
11. **DLP-for-Copilot policy authored on the assumption "SharePoint search index will catch up in 24 hours"** — the SharePoint indexing window is not a fixed 24 hours. Validate the actual policy effect with the synthetic-prompt test in Step 9.3, not by waiting on indexing.
12. **DLP-for-Copilot in production mode without a one-week simulation pass** — produces user-trust damage and avoidable help-desk volume. The Step 9.2 simulation-mode pass is mandatory for every new policy and every material edit.
13. **Built-in SITs adopted at the Microsoft default confidence level without a tuning decision** — defaults are not a decision. Each in-scope built-in SIT carries a written confidence-level decision and justification per Step 1.3.
14. **Salt stored next to the EDM source CSV on the hash-agent host** — the salt belongs in the platform secret store. Co-locating the salt with the plaintext source defeats the EDM hashing model.

---

## Section 8 — Per-step roles matrix

Canonical short names from `docs/reference/role-catalog.md`.

| Step | Primary role | Secondary / consulted | Evidence-collector identity (must differ from primary) |

| 1 — Built-in SIT inventory | Information Protection Admin | Compliance Officer (FSI obligation mapping) | Compliance Data Reader |
| 2 — Test-pane validation | Information Protection Admin | — | Compliance Data Reader |
| 3 — Keyword dictionaries | Information Protection Admin | Data Owner of the source list | Compliance Data Reader |
| 4 — Custom pattern SITs | Information Protection Admin | Compliance Officer (justification review) | Compliance Data Reader |
| 5 — EDM | Information Protection Admin (schema, rule package); EDM_DataUploaders member (hash agent run); Platform Engineering (host stand-up) | Data Owner of the source table | Compliance Data Reader (rule-package and run-log review); SecOps (host telemetry to SIEM) |
| 6 — Document Fingerprinting | Information Protection Admin | Template owner (legal / business) | Compliance Data Reader |
| 7 — Named Entity Recognition | Information Protection Admin | Compliance Officer (residual-risk acceptance) | Compliance Data Reader |
| 8 — Trainable Classifiers | Information Protection Admin | **Model Risk Management owner** (Governance Gate); Compliance Officer (acceptance) | Compliance Data Reader; MRM independent reviewer |
| 9 — DLP for Microsoft 365 Copilot | Compliance Administrator (or DLP Compliance Management) | Communications / Legal (policy-tip text); Help Desk (briefing) | Compliance Data Reader (View-Only Audit Logs) |
| 10 — DSPM for AI validation | DSPM for AI Administrator | Information Protection Admin (re-tune SIT if not surfacing) | Compliance Data Reader |

The "evidence-collector identity must differ from primary" column enforces the 4-eyes posture from Section 2.2.

---

## Section 9 — FSI Incident Response cross-link (worked scenario)

**Scenario:** A Compliance Officer reports that Microsoft 365 Copilot returned a customer SSN in a Copilot Chat response to a marketing analyst, despite Control 1.13 and the DLP-for-Copilot policy being live.

**Triage and remediation flow:**

1. **Engage the AI Incident Response runbook** — see [`../../incident-and-risk/ai-incident-response-playbook.md`](../../incident-and-risk/ai-incident-response-playbook.md). The runbook owns severity classification, regulator-notification clock evaluation (SEC Reg S-P 30-day; state breach laws; FINRA 4530), and customer-impact analysis. **Do not** start tuning SITs before the runbook has classified the event.
2. **Identify the grounding source** — pull the Copilot interaction from the Unified Audit Log ([Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md)). Identify the SharePoint document(s) Copilot grounded on.
3. **Reproduce in the Test pane** — paste the relevant content excerpt (synthetic surrogate if the content itself is privileged) into the Test pane of the SSN built-in SIT and the EDM CustomerMaster SIT (Step 5). Identify which SIT **should have matched** and at what confidence.
4. **Identify the gap.** Common patterns:
    - The DLP-for-Copilot policy was authored at confidence Medium but the source content carried a formatting variation that only matched at Low. Tune the policy down to Low + add a new custom SIT (Step 4) that captures the formatting variation at Medium.
    - The EDM hash run had failed silently for three days (Step 5.9 monitoring gap). Restore the daily run, re-run the validation, and patch the monitoring.
    - The custom SIT was authored without proximity supporting evidence and the source content sat outside the 300-char window. Re-author with a tighter primary or a wider supporting-evidence dictionary (Step 4.1).
    - The grounding source's label no longer matched the separate Copilot DLP sensitivity-label rule, or that rule was disabled/mis-scoped. Restore the tested label/rule binding under [Control 1.5](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md), not a nonexistent label exclusion property.
5. **Re-test end-to-end** — repeat the Step 9.3 synthetic-SSN validation and the Step 10 DSPM-for-AI validation. Both must pass before the incident is closed.
6. **Promote evidence** — the corrected SIT export, the new Test-pane runs, the updated DLP-for-Copilot policy export, and the after-state Copilot validation transcript all join the Evidence Pack with the incident ticket reference in their filename.
7. **Close the loop with MRM and Compliance** — if a trainable classifier was implicated, re-open its Governance Gate (Step 8.1) for a targeted re-validation. If a built-in SIT confidence-level decision is being changed, the Step 1.3 inventory is updated and re-signed by the Compliance Officer.

---

## Section 10 — Cross-references

### Sibling playbooks for Control 1.13

- [`powershell-setup.md`](powershell-setup.md) — supported SIT/dictionary/EDM/fingerprint examples, classifier portal evidence, and read-only DLP policy export.
- [`verification-testing.md`](verification-testing.md) — repeatable validation scripts, orphan-artifact sweeps, regression-test corpora, propagation-window measurement.
- [`troubleshooting.md`](troubleshooting.md) — common failure modes (EDM upload endpoint unreachable, Test-pane returns zero matches, classifier stuck in training, DLP-for-Copilot location not selectable).

### Related controls

- [Control 1.5 — Data Loss Prevention and Sensitivity Labels](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) — the primary enforcement surface for SITs (DLP and label-driven Copilot exclusion).
- [Control 1.6 — Microsoft Purview DSPM for AI](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md) — the AI-specific telemetry surface that visualises SIT matches in Copilot interactions.
- [Control 1.7 — Comprehensive Audit Logging and Compliance](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) — Unified Audit Log is the durable record of SIT-policy enforcement events.
- [Control 1.9 — Data Retention and Deletion Policies](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md) — promotes Evidence Pack artifacts into FSI retention.
- [Control 1.10 — Communication Compliance Monitoring](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md) — consumes SITs (and trainable classifiers) for MNPI / suitability / NPI supervision.
- [Control 1.14 — Data Minimization and Agent Scope Control](../../../controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md) — restricts the data scope an agent can ground on; complements SIT-driven exclusion.
- [Control 4.6 — Grounding Scope Governance](../../../controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md) — restricts the SharePoint surface Copilot can ground on; complementary to SIT-driven exclusion.

### Microsoft Learn references at deployment)

- Sensitive information types — `sit-sensitive-information-type-learn-about`
- Custom SITs — `create-a-custom-sensitive-information-type` and `sit-get-started-with-custom-sensitive-information-types`
- Keyword dictionaries — `create-a-keyword-dictionary`
- Exact data match — `sit-learn-about-exact-data-match-based-sits`, `sit-create-edm-sit-unified-ux`, `sit-use-exact-data-refresh-data`
- Document fingerprinting — `document-fingerprinting`
- Named entities — `named-entities-learn`, `named-entities-use`
- Trainable classifiers — `trainable-classifiers-learn-about`, `classifier-get-started-with`, `classifier-how-to-retrain-content-explorer`
- DLP for Microsoft 365 Copilot — `dlp-microsoft365-copilot-location-learn-about`
- DSPM for AI — `dspm-for-ai`

---

*Updated: October 2026 | Version: v1.6.2 | UI Verification Status: Needs Review — documentation verified; tenant UI not tested*
