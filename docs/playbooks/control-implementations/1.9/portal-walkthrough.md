# Control 1.9 — Portal Walkthrough: Data Retention and Deletion Policies

**Control:** 1.9 — Data Retention and Deletion Policies
**Pillar:** Pillar 1 — Security
**Audience:** Purview Records Manager, Purview Compliance Admin, Purview eDiscovery Roles, Compliance Officer, Power Platform Admin, Exchange Online Admin, Legal / General Counsel
**Companion playbooks:** [PowerShell setup](./powershell-setup.md) · [Verification & testing](./verification-testing.md) · [Troubleshooting](./troubleshooting.md)

> This playbook walks through the **Microsoft Purview portal** (April 2026 UI) to configure retention labels, label policies, retention policies, AI-experience retention, Preservation Lock, eDiscovery holds, and disposition review for [Control 1.9](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md).
>
> **Hedging note.** Following this playbook helps meet, and is recommended to support compliance with, SEC 17 CFR 240.17a-4, FINRA 4511, SOX §404 / §802, GLBA 501(b), CFTC 1.31, and IRS recordkeeping rules. It does **not by itself** satisfy SEC 17a-4(f) — see "SEC 17a-4(f) caveat" in the parent control. Implementation requires legal review and verification against the firm's Written Supervisory Procedures (WSPs).

---

## Prerequisites

Before opening the portal:

1. **Retention schedule signed off by counsel.** Each record type → regulatory citation → retention period → action (delete / start disposition review). Without this, you will create labels you cannot defend in an examination.
2. **Licensing.** Microsoft 365 E5 (or E3 + Microsoft 365 E5 Compliance / Information Protection & Governance add-on) for retention labels, Records Management, Preservation Lock, and disposition review. Microsoft 365 Copilot license for the **Microsoft 365 Copilot and AI experiences** retention location. AI App PAYG meter enabled (see Control 1.7) for **Other AI Apps**.
3. **Roles assigned (canonical names from the role catalog):**
    - **Purview Records Manager** for label authoring and disposition setup
    - **Purview Compliance Admin** for retention policies and Preservation Lock
    - **Purview eDiscovery Roles** for legal hold work
    - **Power Platform Admin** for Dataverse long-term retention
4. **Change window approved by CAB.** Preservation Lock is irreversible. Treat lock application as a SEV-2 change and capture pre/post evidence in the change ticket.
5. **Test environment.** Apply every step in a non-production tenant first, especially Preservation Lock.
6. **Disposition reviewers identified.** Stage 1 (Records Management), Stage 2 (Compliance Officer), Stage 3 (Legal). Email-enabled security groups are recommended over individual mailboxes.

---

## Portal map (April 2026)

All steps below start from one of these entry points:

| Surface | URL | Used for |
|---|---|---|
| Microsoft Purview portal | `https://purview.microsoft.com` | Retention labels, label policies, retention policies, Records Management, Disposition, eDiscovery, Audit |
| Power Platform Admin Center | `https://admin.powerplatform.microsoft.com` | Dataverse long-term retention for Microsoft Copilot Studio environments |
| Exchange admin center (legacy holds) | `https://admin.exchange.microsoft.com` | In-Place Hold / Litigation Hold on individual mailboxes (use only when eDiscovery hold is impractical) |

---

## Step 1 — Create retention labels for agent data

**Path:** Microsoft Purview > **Solutions** > **Records management** > **File plan** > **+ Create a label**
*(For non-record labels, use Purview > **Solutions** > **Data lifecycle management** > **Labels** > **+ Create a label**.)*

### 1.1 Label: agent communications (3-year, communications classification)

1. Open the Purview portal and go to **Records management** > **File plan**.
2. Click **+ Create a label**.
3. **Label settings:**
    - Name: `FSI-Agent-Communications-3Year`
    - Description for users: "Agent transcript classified as a communication under SEC 17a-4(b)(4). 3-year retention; first 2 years readily accessible."
    - Description for admins: "Created for Control 1.9. Maps to 17 CFR 240.17a-4(b)(4)."
4. **File plan descriptors** (recommended for examiner-ready evidence): Citation `17 CFR 240.17a-4(b)(4)`, Authority `SEC`, Department `Compliance`.
5. **Label scope:** Items.
6. **Retention settings:**
    - Retain items for: **3 years**
    - Start retention based on: **When items were created**
    - At end of retention: **Start a disposition review**
7. **Disposition reviewers:** Stage 1 `records-mgmt-stage1@contoso.com`, Stage 2 `compliance-stage2@contoso.com`, Stage 3 `legal-stage3@contoso.com`.
8. **Mark items as a record:** **Yes** (locks retention so it can be extended but not reduced).
9. **Mark items as a regulatory record:** **No** for communications (regulatory-record flag is best reserved for content where you want absolute immutability — see 1.3).
10. **Review and create.**

### 1.2 Label: agent books-and-records (6-year)

Repeat 1.1 with these differences:

- Name: `FSI-Agent-BooksRecords-6Year`
- Description: "Agent transcript that evidences or generates an SEC 17a-3 record. 6-year retention; first 2 years readily accessible."
- File plan descriptors: Citation `17 CFR 240.17a-4(b)(2)-(3); FINRA 4511`, Authority `SEC / FINRA`.
- Retain items for: **6 years**.
- Mark items as a record: **Yes**.

### 1.3 Label: agent regulatory record (10-year, immutable)

For audit metadata and any content the firm classifies as a true regulatory record where deletion must be impossible without lock release:

- Name: `FSI-Agent-RegRecord-10Year`
- Description: "Agent audit metadata and regulated artifacts. 10-year retention; immutable."
- Retain items for: **10 years**, action: **Start a disposition review**.
- Mark items as a record: **Yes**.
- Mark items as a regulatory record: **Yes**.

!!! warning "Regulatory record is one-way"
    Marking as a regulatory record cannot be undone, the label cannot be removed from items it has been applied to, and retention can only be extended. Use only for content classes where the firm has accepted that constraint in writing.

### 1.4 Label: agent configuration (6-year)

For Copilot Studio agent definitions, version history, and topic exports stored in SharePoint:

- Name: `FSI-Agent-Configuration-6Year`
- Retain items for: **6 years**.
- At end of retention: **Delete items automatically** (no disposition review needed for engineering artifacts).
- Mark items as a record: **No** (allows engineering teams to manage versioning).

---

## Step 2 — Publish labels via a label policy

**Path:** Purview > **Solutions** > **Records management** > **Label policies** > **+ Publish labels**

1. Click **+ Publish labels**.
2. **Choose labels to publish:** select all four `FSI-Agent-*` labels created in Step 1.
3. **Choose admin units (optional):** scope to a Zone 3 administrative unit if used.
4. **Choose locations:** enable all of the following that the firm uses for agent-touching data:
    - Exchange email
    - SharePoint classic and communication sites
    - OneDrive accounts
    - Microsoft 365 Group mailboxes & sites
    - Teams chats and Copilot interactions
    - Teams channel messages (standard, private, shared)
    - Viva Engage user messages
    - Viva Engage community messages
5. **Policy settings:**
    - Name: `FSI-Agent-Labels-Publish-Zone3`
    - Description: "Publishes Control 1.9 retention labels to Zone 3 in-scope users and locations."
6. **Review and submit.** Distribution typically takes 24 hours (up to 7 days for fully populated mailboxes). Track in **Label policies** > policy detail > **Distribution status**.

---

## Step 3 — Create retention policies for AI interaction surfaces

**Path:** Purview > **Solutions** > **Data lifecycle management** > **Policies** > **+ New retention policy**

You will create three policies — one per AI-specific location. Container-level retention here complements the item-level labels published in Step 2.

### 3.1 Policy: Microsoft 365 Copilot and AI experiences

1. Click **+ New retention policy**.
2. **Name:** `FSI-Copilot-AIExperiences-Retention`
3. **Description:** "Retains M365 Copilot and Copilot Studio interactions for FSI books-and-records compliance. Mapped to Control 1.9."
4. **Policy type:** **Adaptive** (recommended). Create or select an adaptive scope targeting users in scope (e.g., licensed M365 Copilot users in regulated business units).
5. **Choose locations:** select **Microsoft 365 Copilot and AI experiences**.
6. **Decide if you want to retain content, delete it, or both:**
    - **Retain items for a specific period:** **6 years**
    - **At end of retention period:** **Delete items automatically**
    - Start retention based on: **When items were created**
7. **Review and submit.**

### 3.2 Policy: Enterprise AI Apps

Repeat 3.1 with:

- Name: `FSI-EnterpriseAIApps-Retention`
- Locations: **Enterprise AI Apps**
- Retention: **6 years**, then delete.

### 3.3 Policy: Other AI Apps

Repeat 3.1 with:

- Name: `FSI-OtherAIApps-Retention`
- Locations: **Other AI Apps** (requires AI App PAYG meter enabled — see Control 1.7).
- Retention: **6 years**, then delete.

!!! note "Adaptive scopes recommended"
    Adaptive scopes update the in-scope user/site set automatically as Entra group membership or attributes change. Static scopes require manual edits and are a frequent source of "policy not applying" tickets.

---

## Step 4 — Configure Dataverse long-term retention for Copilot Studio

**Path:** [Power Platform Admin Center](https://admin.powerplatform.microsoft.com) > **Environments** > select the Copilot Studio environment > **Settings** > **Audit and logs** / **Data management**

1. Select the Copilot Studio environment hosting agents in scope.
2. Open **Settings** > **Data management** > **Long-term retention**.
3. **Create a retention policy** for each in-scope table:
    - `botcomponent` — agent definition and configuration → **6 years** (FSI-Agent-Configuration-6Year alignment)
    - `conversationtranscript` — agent transcripts → **6 years** (default; **3 years** if classified as communications-only)
    - `botsession` / `botinteraction` — runtime sessions and interactions → **6 years**
4. **Archive trigger:** rows older than **2 years** archive to long-term storage; remain queryable via the Long-Term Retention panel.
5. Confirm creation; archive jobs run on Microsoft's schedule (review **Job history** weekly).

!!! warning "Dataverse retention is separate from Purview"
    Long-term retention here is the **Dataverse-native** archival tier; Purview retention policies for Copilot interactions cover the M365-side surfaces. Plan both, document in WSPs which surface authoritatively retains the regulatory copy, and reconcile retrieval procedures in the firm's records procedures.

---

## Step 5 — Apply Preservation Lock (Zone 3 — irreversible)

> **Read this entire step before clicking anything.** Preservation Lock cannot be undone. After locking, no one — including Global Admin or Microsoft Support — can disable, delete, or shorten the policy. Only adding locations or extending retention is permitted.

**Path:** Preservation Lock has **no portal toggle** as of April 2026. Apply it via Security & Compliance PowerShell — see [PowerShell Setup §6](./powershell-setup.md).

After locking via PowerShell, return to the Purview portal:

1. Open the locked policy in Purview > **Data lifecycle management** > **Policies**.
2. Confirm the policy detail panel shows **Preservation Lock: On**.
3. Confirm the **Edit** flow only offers **Add locations** and **Extend retention**.
4. Capture a screenshot of the locked policy panel for the change ticket. This screenshot is auditor evidence.

---

## Step 6 — Configure disposition review

**Path:** Purview > **Solutions** > **Records management** > **Disposition**

1. Open **Disposition** > **Reviewers**.
2. Confirm the email-enabled groups configured in Step 1 (Stage 1, 2, 3) appear with the correct stage assignments per label.
3. Open **Settings** > **Disposition review options** and verify:
    - **Items pending disposition:** retained until reviewer action
    - **Disposition decisions:** **Approve disposal**, **Extend retention**, **Relabel**, **Justify decision** (free text — required for examiner evidence)
    - **Notification cadence:** at least weekly to reviewers
4. (Optional, recommended for FSI) Enable **Disposition for items in SharePoint and OneDrive** so on-prem-style files in document libraries flow to the same disposition workflow.

---

## Step 7 — Stand up eDiscovery / Litigation hold

**Path:** Purview > **Solutions** > **eDiscovery** > **Cases** > **+ Create a case** (use **Premium** if licensed; **Standard** otherwise)

1. Create a case named for the matter, not the system (e.g., `Matter-2026-NYAG-001`, not `Test-Hold`).
2. **Add hold:** **Holds** > **+ Create hold**.
3. **Hold scope** — choose locations:
    - User mailboxes (named custodians)
    - SharePoint sites in scope
    - Teams chat / Copilot interaction locations (via mailbox attribution)
    - Microsoft 365 Group mailboxes & sites
4. **Hold query (optional):** narrow by keywords, date range, or sensitive information types (SITs). For agent transcripts, a typical query: `(Copilot OR "agent" OR "AI assistant") AND date>=YYYY-MM-DD`.
5. **Activate hold.** Status will progress through **On (Pending)** → **On**. Capture a screenshot of the activated hold for the legal file.

!!! warning "Hold beats retention"
    eDiscovery hold preserves content **regardless** of any retention or disposition policy. When the hold is released, normal retention resumes — including any disposition action that was pending. Document the hold release decision before clicking Release.

---

## Step 8 — Verify audit log captures retention and deletion events

**Path:** Purview > **Solutions** > **Audit** > **Search**

1. Confirm Audit is enabled (see Control 1.7).
2. Run a test search:
    - **Date range:** last 7 days
    - **Activities:** **Created retention compliance policy**, **Modified retention compliance policy**, **Deleted file**, **Hard deleted file**, **Applied retention label**, **Removed retention label**
3. Confirm results return for the policies and labels you just created.
4. (For Zone 3) Confirm an audit-log retention policy retains these event types for at least the longest record retention period in the firm's schedule (typically 10 years). See [Control 1.7 portal walkthrough](../1.7/portal-walkthrough.md) for setup.

---

## Step 9 — Document the configuration as evidence

For each examination-ready file:

| Artifact | Source | Where to store |
|---|---|---|
| Retention schedule (signed) | Counsel + Compliance | WSP repository |
| Label inventory CSV | PowerShell `Get-ComplianceTag` export (see PowerShell §7) | Compliance evidence vault |
| Policy inventory CSV | PowerShell `Get-RetentionCompliancePolicy` export | Compliance evidence vault |
| Preservation Lock proof | PowerShell `Get-RetentionCompliancePolicy | Where RetentionComplianceLockType -eq 'Lock'` export + portal screenshot | Compliance evidence vault, change ticket |
| Disposition reviewer roster | Group membership export | Records management binder |
| eDiscovery hold inventory | Purview > eDiscovery > Holds export | Legal hold register |
| Audit log retention proof | Purview > Audit > Audit retention policies | Audit evidence vault |

---

## Cross-references

- [Control 1.7 — Comprehensive Audit Logging and Compliance](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md): the audit trail that proves retention and disposition occurred.
- [Control 4.3 — Site and Document Retention Management](../../../controls/pillar-4-sharepoint/4.3-site-and-document-retention-management.md): SharePoint-specific guidance.
- [Control 1.5 — DLP and Sensitivity Labels](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md): sensitivity label interaction with retention.

---

[Back to Control 1.9](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md) · [PowerShell setup](./powershell-setup.md) · [Verification & testing](./verification-testing.md) · [Troubleshooting](./troubleshooting.md)

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
