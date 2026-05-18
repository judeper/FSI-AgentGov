# Control 2.13 — Portal Walkthrough: Documentation and Record Keeping

**Control:** 2.13 — Documentation and Record Keeping
**Pillar:** Pillar 2 — Management
**Audience:** SharePoint Admin, Purview Records Manager, Purview Compliance Admin, Power Platform Admin, Compliance Officer, AI Governance Lead
**Companion playbooks:** [PowerShell Setup](./powershell-setup.md) · [Verification & Testing](./verification-testing.md) · [Troubleshooting](./troubleshooting.md)
**Estimated Time:** 4–6 hours (Zone 1), 6–8 hours (Zone 2), 8–12 hours (Zone 3)
**Last UI verified:** April 2026

---

## Regulatory hedging notice

This walkthrough is intended to help support FSI organizations in configuring documentation and record-keeping infrastructure for AI agents. It aids in meeting expectations from FINRA Rule 4511 (books and records), FINRA Rule 3110 (supervision documentation), FINRA 25-07 (AI communications recordkeeping), SEC Rule 17a-3 (record creation), SEC Rule 17a-4 (record preservation, including the October 2022 amendments / May 2023 compliance date for the audit-trail alternative), SOX §§302/404 (internal controls documentation), GLBA 501(b) (safeguards documentation), OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12) / Federal Reserve SR 26-2 (formerly SR 11-7) (model risk management documentation), and CFTC Regulation 1.31 (5-year retention for FCMs, swap dealers, CPOs).

Completion of this walkthrough **does not guarantee legal or regulatory compliance**, does not by itself constitute a 17a-4(f) attestation, and does not replace the firm's written supervisory procedures or independent records-management assessment. Organizations should verify configuration meets their specific regulatory obligations.

---

## Prerequisites

Before starting, confirm the following:

| Prerequisite | Details |
|---|---|
| **SharePoint Admin** role | Required for site creation, library configuration, and content type management |
| **Purview Records Manager** role | Required for retention label creation and retention policy publishing |
| **Purview Compliance Admin** role | Required for auto-labeling policies and compliance configuration |
| **Power Platform Admin** role | Required for Microsoft Copilot Studio environment documentation (Zone 2+) |
| **Retention schedule approved** | Firm-specific retention schedule reviewed by Compliance Officer per FINRA 4511 / SEC 17a-4 record-type matrix |
| **Document taxonomy defined** | Record categories, metadata fields, and classification scheme approved |
| **License entitlements** | Microsoft 365 E5 or E5 Compliance add-on recommended for Purview Records Management, auto-labeling, and Audit Premium. E3 supports manual label application only. |
| **Zone classification determined** | Agent zone assignment per [Control 2.2 — Environment Groups and Tier Classification](../../../controls/pillar-2-management/2.2-environment-groups-and-tier-classification.md) |

---

## Zone 1 — Personal Productivity Agents

Zone 1 agents have low regulatory exposure. Basic documentation and standard retention apply.

### Step 1: Create the AI Governance SharePoint Site

1. Navigate to **[SharePoint Admin Center](https://admin.microsoft.com/sharepoint)** > **Active sites** > **+ Create**
2. Select **Team site** (Microsoft 365 group-connected)
3. Configure:
   - **Site name:** `AI-Governance`
   - **Group email address:** `ai-governance`
   - **Site address:** `/sites/AI-Governance`
   - **Privacy:** Private
   - **Language:** English (United States)
4. Click **Next**, then add site owners (SharePoint Admin, AI Governance Lead)
5. Click **Create site**

!!! note "FSI Evidence Capture"
    Screenshot the site creation confirmation page showing site URL, group membership, and privacy setting. Save as `evidence-2.13-site-creation.png`.

### Step 2: Create Document Libraries

1. Navigate to the new AI Governance site
2. Click **+ New** > **Document library** for each of the following:

| Library Name | Purpose | Zone 1 Required |
|---|---|---|
| `AgentConfigurations` | Agent manifest exports, prompt versions, system instructions | ✓ |
| `InteractionLogs` | Conversation transcripts, session logs | ✓ |
| `GovernanceDecisions` | Policy decisions, risk acceptances, governance meeting minutes | ✓ |

3. For each library, navigate to **Settings** (⚙️) > **Library settings** > **Versioning settings**:
   - Set **Require content approval:** No
   - Set **Create a version each time you edit a file:** Yes — Major versions
   - Set **Keep drafts for the following number of major versions:** 500

### Step 3: Configure Basic Metadata Columns

1. Navigate to **Site settings** > **Site columns** > **Create**
2. Create the following site columns in a new group called **AI Governance**:

| Column Name | Internal Name | Type | Required |
|---|---|---|---|
| Agent ID | `AgentID` | Single line of text | Yes |
| Document Category | `DocCategory` | Choice: Configuration, Log, Decision | Yes |
| Classification Date | `ClassificationDate` | Date and Time | Yes |

3. Navigate to each library > **Settings** > **Add from existing site columns** > select the **AI Governance** group > **Add**
4. Apply columns to all three libraries

### Step 4: Establish Annual Review Schedule

1. In the `GovernanceDecisions` library, create a document: `Annual-Documentation-Review-Schedule.docx`
2. Define the review cadence: **Annual** for Zone 1
3. Assign the **AI Governance Lead** as the review owner

!!! note "FSI Evidence Capture"
    Export the site columns list and library settings as evidence. Navigate to **Site settings** > **Site columns** and screenshot the AI Governance column group.

---

## Zone 2 — Team Collaboration Agents

Zone 2 adds Purview retention labels, auto-labeling, documented approval chains, and Copilot Studio versioning documentation. Complete all Zone 1 steps first.

### Step 5: Create Additional Document Libraries

1. In the AI Governance site, add the following libraries:

| Library Name | Purpose | Zone 2 Required |
|---|---|---|
| `ApprovalRecords` | Deployment approvals, change requests, WSP addenda | ✓ |
| `IncidentReports` | Security incidents, compliance findings, remediation evidence | ✓ |
| `SupervisionRecords` | FINRA 3110 supervision logs, sampling evidence, review outcomes | ✓ |

2. Apply the same versioning settings and AI Governance site columns as Zone 1 libraries

### Step 6: Expand the Metadata Schema

1. Navigate to **Site settings** > **Site columns** > **Create**
2. Add additional columns to the **AI Governance** group:

| Column Name | Internal Name | Type | Choices / Format |
|---|---|---|---|
| Regulatory Reference | `RegReference` | Choice (allow multiple) | FINRA 4511, FINRA 3110, SEC 17a-3, SEC 17a-4, SOX 302, SOX 404, GLBA 501(b), OCC Bulletin 2026-13 (formerly OCC 2011-12), Fed SR 26-2 (formerly SR 11-7), CFTC 1.31 |
| Retention Period | `RetentionPeriod` | Choice | 3 years, 5 years, 6 years, 7 years, 10 years, Permanent |
| Record Owner | `RecordOwner` | Person or Group | N/A |
| Governance Zone | `GovZone` | Choice | Zone 1, Zone 2, Zone 3 |

3. Add these columns to all Zone 2 libraries

### Step 7: Create Purview Retention Labels

1. Open **[Microsoft Purview portal](https://purview.microsoft.com)** > **Data lifecycle management** > **Microsoft 365** > **Labels**
2. Click **+ Create a label** and create each of the following:

| Label Name | Retention Period | Retention Action | Record Type | Regulatory Basis |
|---|---|---|---|---|
| `FSI-Agent-Communications-3Year` | 3 years | Delete items automatically | Record | SEC 17a-4(b)(4) — communications |
| `FSI-Agent-BooksRecords-6Year` | 6 years | Delete items automatically | Record | SEC 17a-4(a) — financial records |
| `FSI-Agent-Governance-6Year` | 6 years | Delete items automatically | Item | FINRA 4511 — governance records |
| `FSI-Agent-Supervision-6Year` | 6 years | Delete items automatically | Record | FINRA 3110 — supervision records |

3. For each label:
   - Set **Retain items for:** the specified period
   - Set **Start the retention period based on:** When items were created
   - Select **Mark items as a record** where indicated above
   - Add a **File plan descriptor** with the regulatory reference
4. Click **Next** through remaining pages and **Create**

!!! warning "Record labels are permanent"
    Once an item is marked as a record, users cannot edit or delete it until the retention period expires. Plan label taxonomy carefully before publishing. Organizations should verify this behavior meets their operational requirements.

### Step 8: Publish Retention Labels

1. In Purview > **Data lifecycle management** > **Microsoft 365** > **Label policies** > **Publish labels**
2. Select all four FSI-Agent labels created in Step 7
3. On the **Choose locations** page:
   - Enable **SharePoint sites** > add the AI Governance site URL
   - Enable **OneDrive accounts** if agent documentation is stored in OneDrive
4. **Policy name:** `FSI-AI-Governance-Retention`
5. Click **Submit**

!!! note "Propagation delay"
    Published labels may take up to 7 days to appear in SharePoint libraries. For Zone 2 deployments, plan a 1-week buffer between label publishing and auto-labeling configuration.

### Step 9: Configure Auto-Labeling Policy

1. In Purview > **Data lifecycle management** > **Microsoft 365** > **Auto-apply a label**
2. Click **+ Auto-apply a label**
3. Configure:
   - **Label to auto-apply:** `FSI-Agent-Communications-3Year`
   - **Conditions:** Apply label to content that contains specific words or phrases
   - **Keywords/Phrases:** `Agent ID`, `Copilot interaction`, `agent session`
   - **Locations:** SharePoint sites > AI Governance site > `InteractionLogs` library
4. **Policy name:** `FSI-AutoLabel-InteractionLogs`
5. Enable the policy

!!! tip "Alternative: content type-based auto-labeling"
    For more precise targeting, create a SharePoint content type for interaction logs and use the content type as the auto-labeling condition instead of keyword matching.

### Step 10: Document Copilot Studio Agent Versioning

1. Open **[Power Platform Admin Center](https://admin.powerplatform.microsoft.com)** > **Environments** > select the environment containing the agent
2. Navigate to **Copilot Studio** > **Agents** > select the agent
3. Review the **Publish history** pane, which shows:
   - Each published version with timestamp
   - The user who published
   - Version number
4. Export the publish history:
   - Click the **⋮** (more options) > **Solution history** (if the agent is in a managed solution)
   - Screenshot the publish history for evidence

!!! note "SKU/License consideration"
    Copilot Studio publish history is available in all licensed tiers. However, solution layer history and detailed change tracking require the agent to be deployed within a Dataverse solution in a managed environment.

!!! note "FSI Evidence Capture"
    Export the Copilot Studio agent overview page showing version number, last published date, and environment. Save as `evidence-2.13-agent-version-[AgentName].png`.

---

## Zone 3 — Enterprise Managed Agents

Zone 3 requires SEC 17a-4 compliance, automated retention, examination-ready documentation, and monthly audits. Complete all Zone 1 and Zone 2 steps first.

### Step 11: Configure SEC 17a-4 Compliant Storage

Per the October 2022 SEC amendments (compliance date May 3, 2023), broker-dealers may choose either WORM storage or an audit-trail alternative. **Standard Microsoft 365 retention does not by itself constitute either path.** Organizations should consult legal counsel and verify their specific obligations.

#### Option A: WORM Storage (Azure Immutable Blob)

1. Open **[Azure Portal](https://portal.azure.com)** > **Storage accounts** > **+ Create**
2. Configure the storage account:
   - **Resource group:** `rg-fsi-governance`
   - **Storage account name:** `fsiaigov[tenantshort]`
   - **Region:** Select per your data residency requirements
   - **Performance:** Standard
   - **Redundancy:** GRS (Geo-redundant storage) recommended for regulated workloads
3. After creation, navigate to **Containers** > **+ Container**:
   - **Name:** `ai-governance-records`
   - **Access level:** Private
4. Navigate to the container > **Access policy** > **Immutable blob storage**:
   - Click **+ Add policy** > **Time-based retention**
   - Set **Retention period:** 2190 days (6 years) or 2555 days (7 years with buffer)
   - Click **Save**
5. **Lock the policy** (⚠️ IRREVERSIBLE):
   - Click the **Lock** icon on the time-based retention policy
   - Confirm the lock — once locked, the retention period cannot be shortened and the container cannot be deleted until all blobs expire

!!! danger "WORM lock is irreversible"
    Locking a time-based retention policy is a **one-way operation**. It cannot be reversed, shortened, or deleted. Test thoroughly in a non-production environment before locking in production. Organizations should verify this meets their operational requirements and consult with Compliance Officer before locking.

6. Configure an export pipeline (Power Automate or Azure Data Factory) to copy agent records from SharePoint / Purview to the immutable blob container on a scheduled basis

#### Option B: Audit-Trail Alternative

1. Verify the firm's electronic recordkeeping system maintains a complete time-stamped audit trail of all original records and any modifications
2. Confirm the system provides serialized indexing of all records
3. Verify the system includes verifying records that enable integrity confirmation
4. Confirm a **Designated Executive Officer (DEO) representation** or **Designated Third Party (DTP) undertaking** is on file per SEC 17a-4(f)(3)(vii)
5. Obtain or maintain a **Cohasset Associates** (or equivalent) attestation for the electronic recordkeeping system
6. Document the audit-trail alternative implementation in the firm's Written Supervisory Procedures (WSPs)

!!! warning "Legal review required"
    Both Option A and Option B require legal counsel review before implementation. The audit-trail alternative requires specific representations and undertakings that go beyond technical configuration. Organizations should verify requirements with their compliance and legal teams.

### Step 12: Create Regulatory Record Labels (Zone 3 Only)

1. In Purview > **Data lifecycle management** > **Microsoft 365** > **Labels** > **+ Create a label**
2. Create additional Zone 3 labels:

| Label Name | Retention | Action | Record Type | Regulatory Basis |
|---|---|---|---|---|
| `FSI-Agent-RegRecord-7Year` | 7 years | Delete items automatically | Regulatory record | SEC 17a-4 (6-year + buffer) |
| `FSI-Agent-CFTC-5Year` | 5 years | Delete items automatically | Regulatory record | CFTC 1.31 — derivatives records |
| `FSI-Agent-ModelRisk-6Year` | 6 years | Delete items automatically | Record | OCC Bulletin 2026-13 (formerly OCC 2011-12) / Fed SR 26-2 (formerly SR 11-7) — model documentation |
| `FSI-Agent-Permanent` | Indefinite | No action | Regulatory record | Board approvals, critical governance |

3. Mark as **Regulatory record** where indicated — this designation prevents label removal and deletion by any user, including administrators

!!! warning "Regulatory record labels cannot be removed"
    Items labeled as regulatory records cannot have the label removed, cannot be deleted, and the retention period cannot be shortened. This is more restrictive than a standard record label. Only use for content with clear regulatory retention requirements.

### Step 13: Configure Comprehensive Document Taxonomy

1. Navigate to **Site settings** > **Content types** > **Create**
2. Create the following content types in the **AI Governance** group:

| Content Type | Parent | Description | Libraries |
|---|---|---|---|
| `Agent Configuration Record` | Document | Agent manifest exports, system instructions, prompt versions | AgentConfigurations |
| `Agent Interaction Log` | Document | Conversation transcripts, session data | InteractionLogs |
| `Governance Approval Record` | Document | Deployment approvals, change authorizations | ApprovalRecords |
| `Incident Report` | Document | Security incidents, compliance findings | IncidentReports |
| `Supervision Evidence` | Document | FINRA 3110 review logs, sampling reports | SupervisionRecords |

3. Associate each content type with the appropriate AI Governance site columns
4. Apply each content type to its designated library
5. Set the **default content type** for each library to the matching type

### Step 14: Establish Examination Response Procedures

1. In the `GovernanceDecisions` library, create: `Examination-Response-Procedure.docx`
2. Document the following in the procedure:

| Section | Content |
|---|---|
| **Designated Custodians** | Primary custodian name and contact, backup custodian name and contact |
| **Response SLA** | 24 hours for initial acknowledgment, 48 hours for initial document production |
| **Search Procedures** | How to locate agent records using Purview Content Search, eDiscovery, and SharePoint search |
| **Export and Production** | Procedures for exporting records to examiner-ready format (PST, CSV, or native) |
| **Chain of Custody** | Documentation of record handling from retrieval through production |
| **Legal Hold Integration** | Process for placing agent records on legal hold per [Control 1.19 — eDiscovery](../../../controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md) |

3. Assign the label `FSI-Agent-Governance-6Year` to the procedure document
4. Have the Compliance Officer and designated custodians review and sign

!!! note "FSI Evidence Capture"
    Export the examination response procedure with signature block. This document is typically requested early in FINRA or SEC examinations.

### Step 15: Configure Quarterly Documentation Audit

1. In the `GovernanceDecisions` library, create: `Quarterly-Audit-Schedule.docx`
2. Define the audit scope:
   - Completeness: All required libraries populated
   - Labeling: Retention labels applied to all governed content
   - Metadata: All required metadata fields populated
   - Version history: Agent configuration version history maintained
   - Access controls: Library permissions limited to authorized roles
3. Assign quarterly audit owners and due dates
4. Create a recurring calendar entry for the AI Governance team

### Step 16: Power Platform Admin Center — Environment Documentation

1. Open **[Power Platform Admin Center](https://admin.powerplatform.microsoft.com)** > **Environments**
2. For each environment containing agents:
   - Navigate to **Settings** > **Audit and logs** > verify Dataverse auditing is enabled
   - Navigate to **Solutions** > review solution layers for each agent solution
   - Export the environment details (Name, Type, Region, Creator, Created Date) as evidence
3. In **Copilot Studio** for each Zone 3 agent:
   - Export the agent definition (Topics, Actions, Knowledge sources) via **Settings** > **Agent details**
   - Document the current publish version
   - Screenshot the analytics dashboard for usage metrics

!!! note "FSI Evidence Capture"
    For each Zone 3 agent, capture: (1) Copilot Studio agent details page, (2) publish history, (3) solution layer history, (4) analytics overview. Save to the `AgentConfigurations` library with appropriate metadata.

---

## Configuration Summary

| Setting | Zone 1 (Personal) | Zone 2 (Team) | Zone 3 (Enterprise) |
|---------|-------------------|---------------|---------------------|
| **SharePoint site** | Basic (3 libraries) | Comprehensive (6 libraries) | Full (6 libraries + hub) |
| **Metadata schema** | 3 core columns | 7 columns with multi-value | 7 columns + content types |
| **Retention labels** | Manual application | Published + auto-labeling | Regulatory record labels |
| **Auto-labeling** | Not required | Recommended | Required |
| **SEC 17a-4** | Not applicable | Not applicable | WORM or audit-trail alternative |
| **Copilot Studio versioning** | Informal | Documented per environment | Exported and preserved per agent |
| **Audit cadence** | Annual | Quarterly | Monthly |
| **Examination procedures** | Basic contact list | Documented procedure | Full procedure with legal hold integration |

---

## Post-Configuration Validation

After completing all steps for your zone, verify:

- [ ] SharePoint site created with all zone-required libraries
- [ ] Metadata columns added and applied to all libraries
- [ ] Versioning enabled on all libraries (500 major versions)
- [ ] Retention labels created with correct retention periods
- [ ] Label policies published and labels visible in libraries (allow up to 7 days)
- [ ] Auto-labeling policy configured and enabled (Zone 2+)
- [ ] SEC 17a-4 compliant storage configured with appropriate option (Zone 3)
- [ ] Examination response procedure documented and signed (Zone 3)
- [ ] Copilot Studio agent version history documented (Zone 2+)
- [ ] Audit cadence scheduled and owners assigned

---

[Back to Control 2.13](../../../controls/pillar-2-management/2.13-documentation-and-record-keeping.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
