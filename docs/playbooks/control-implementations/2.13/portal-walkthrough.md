# Control 2.13 — Portal Walkthrough: Documentation and Record Keeping

**Control:** 2.13 — Documentation and Record Keeping
**Pillar:** Pillar 2 — Management
**Audience:** SharePoint Admin, Purview Records Manager, Purview Compliance Admin, Power Platform Admin, Compliance Officer, AI Governance Lead
**Companion playbooks:** [PowerShell Setup](./powershell-setup.md) · [Verification & Testing](./verification-testing.md) · [Troubleshooting](./troubleshooting.md)
**Estimated Time:** 4–6 hours (Zone 1), 6–8 hours (Zone 2), 8–12 hours (Zone 3)
**Last UI verified:** April 2026
**Last Verified:** 2026-11-09 (live Microsoft documentation; tenant UI and screenshots not re-tested)

---

## Regulatory hedging notice

This walkthrough is intended to help support FSI organizations in configuring documentation and record-keeping infrastructure for AI agents. It aids in meeting expectations from FINRA Rule 4511 (books and records), FINRA Rule 3110 (supervision documentation), FINRA Regulatory Notice 24-09 (Gen AI guidance for AI communications recordkeeping), SEC Rule 17a-3 (record creation), SEC Rule 17a-4 (record preservation, including the October 2022 amendments / May 2023 compliance date for the audit-trail alternative), SOX §§302/404 (internal controls documentation), GLBA 501(b) (safeguards documentation), OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12) / Federal Reserve SR 26-2 (formerly SR 11-7) (model risk management documentation), and CFTC Regulation 1.31 (5-year retention for FCMs, swap dealers, CPOs).

Completion of this walkthrough **does not guarantee legal or regulatory compliance**, does not by itself constitute a 17a-4(f) attestation, and does not replace the firm's written supervisory procedures or independent records-management assessment. Organizations should verify configuration meets their specific regulatory obligations.

---

## Prerequisites

Before starting, confirm the following:

| Prerequisite | Details |
|---|---|
| **SharePoint Admin** role | Required for admin-center site creation; grant the operator site-owner permissions for library, column, and content type configuration |
| **Purview Records Manager** role | Framework role; assign the **Records Management** role group in Purview for record labels and label policies, not an Entra directory role of this name |
| **Purview Compliance Admin** role | Required for auto-labeling policies and compliance configuration |
| **Power Platform Admin** role | Required for Microsoft Copilot Studio environment documentation (Zone 2+) |
| **Dataverse security roles** | Agent solution export requires at least **System Customizer**; auditing configuration requires System Administrator, System Customizer, or equivalent permissions in the environment |
| **Retention schedule approved** | Firm-specific retention schedule reviewed by Compliance Officer per FINRA 4511 / SEC 17a-4 record-type matrix |
| **Document taxonomy defined** | Record categories, metadata fields, and classification scheme approved |
| **License entitlements** | Microsoft 365 E3 supports basic retention labels and publishing. File plan, record/regulatory-record settings, disposition review, default library labels, and keyword-based auto-apply require feature-specific entitlements, such as Microsoft 365 E5 or Microsoft Purview Suite with an eligible base license. Audit Premium has separate entitlements. Verify the [current feature-level service description](https://learn.microsoft.com/en-us/office365/servicedescriptions/microsoft-365-service-descriptions/microsoft-365-tenantlevel-services-licensing-guidance/microsoft-purview-service-description) before Zone 2+ configuration. |
| **Zone classification determined** | Agent zone assignment per [Control 2.2 — Environment Groups and Tier Classification](../../../controls/pillar-2-management/2.2-environment-groups-and-tier-classification.md) |

---

## Zone 1 — Personal Productivity Agents

Zone 1 agents have low regulatory exposure. Basic documentation and standard retention apply.

### Step 1: Create the AI Governance SharePoint Site

1. Navigate to **[SharePoint Admin Center](https://admin.microsoft.com/sharepoint)** > **Active sites** > **+ Create**
2. Select **Team site** (Microsoft 365 group-connected), choose a template, and select **Use template**
3. Configure:
   - **Site name:** `AI-Governance`
   - **Group email address:** `ai-governance`
   - **Site address:** `/sites/AI-Governance`
   - **Privacy:** Private
   - **Language:** English (United States)
4. Follow the prompts to add site owners (SharePoint Admin, AI Governance Lead)
5. Click **Create site**

!!! note "FSI Evidence Capture"
    Screenshot the site creation confirmation page showing site URL, group membership, and privacy setting. Save as `evidence-2.13-site-creation.png`.

### Step 2: Create Document Libraries

1. Navigate to the new AI Governance site
2. Click **+ New** > **Document library**, start with a blank library, enter its name/description, and select **Create** for each of the following:

| Library Name | Purpose | Zone 1 Required |
|---|---|---|
| `AgentConfigurations` | Agent manifest exports, prompt versions, system instructions | ✓ |
| `InteractionLogs` | Conversation transcripts, session logs | ✓ |
| `GovernanceDecisions` | Policy decisions, risk acceptances, governance meeting minutes | ✓ |

3. For each library, navigate to **Settings** (⚙️) > **Library settings** > **More library settings** (if shown) > **Versioning settings**:
   - Set **Require content approval:** No
   - Under **Document Version History**, select **Create major versions**
   - Set the major-version count limit to **500** (not the draft/minor-version limit); review any version expiration setting separately

The 500-version count is this playbook's configuration baseline, not a retention guarantee. See [library version limits](https://learn.microsoft.com/en-us/sharepoint/library-version-limits).

### Step 3: Configure Basic Metadata Columns

1. Navigate to **Settings** > **Site information** > **View all site settings** > **Site columns** > **Create**
2. Create the following site columns in a new group called **AI Governance**:

| Column Name | Internal Name | Type | Required |
|---|---|---|---|
| Agent ID | `AgentID` | Single line of text | Yes |
| Document Category | `DocCategory` | Choice: Configuration, Log, Decision | Yes |
| Classification Date | `ClassificationDate` | Date and Time | Yes |

3. If matching the PowerShell schema, create columns using the internal-name values first, then rename their display names. Navigate to each library > **Settings** > **Library settings** > **Add from existing site columns** > select the **AI Governance** group > **Add**
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

1. Navigate to **Settings** > **Site information** > **View all site settings** > **Site columns** > **Create**
2. Add additional columns to the **AI Governance** group:

| Column Name | Internal Name | Type | Choices / Format |
|---|---|---|---|
| Regulatory Reference | `RegReference` | Choice (allow multiple) | FINRA 4511, FINRA 3110, SEC 17a-3, SEC 17a-4, SOX 302, SOX 404, GLBA 501(b), OCC Bulletin 2026-13 (formerly OCC 2011-12), Fed SR 26-2 (formerly SR 11-7), CFTC 1.31 |
| Retention Period | `RetentionPeriod` | Choice | 3 years, 5 years, 6 years, 7 years, 10 years, Permanent |
| Record Owner | `RecordOwner` | Person or Group | N/A |
| Governance Zone | `GovZone` | Choice | Zone 1, Zone 2, Zone 3 |

3. Add these columns to all Zone 2 libraries

### Step 7: Create Purview Retention Labels

1. Open **[Microsoft Purview portal](https://purview.microsoft.com)** > **Solutions** > **Records Management** > **File plan**
2. Select **+ Create a label** > **Retention label** and create each of the following:

| Label Name | Retention Period | Retention Action | Record Type | Regulatory Basis |
|---|---|---|---|---|
| `FSI-Agent-Communications-3Year` | 3 years | Delete items automatically | Record | SEC 17a-4(b)(4) — communications |
| `FSI-Agent-BooksRecords-6Year` | 6 years | Delete items automatically | Record | SEC 17a-4(a) — financial records |
| `FSI-Agent-Governance-6Year` | 6 years | Delete items automatically | Item | FINRA 4511 — governance records |
| `FSI-Agent-Supervision-6Year` | 6 years | Delete items automatically | Record | FINRA 3110 — supervision records |
| `FSI-Agent-Configuration-6Year` | 6 years | Delete items automatically | Item | Agent configuration documentation |

3. For each label:
   - Set **Retain items for:** the specified period
   - Choose to **retain** during that period, then delete at the end; deletion-only settings do not preserve content during the period
   - Set **Start the retention period based on:** When items were created
   - Select **Mark items as a record** where indicated above
   - Add a **File plan descriptor** with the regulatory reference
4. Review the settings, save the label, and repeat. If a label already exists (for example, from Control 1.9), compare its settings with the approved schedule before reusing it; do not overwrite an existing disposition-review workflow.

!!! warning "Records and regulatory records behave differently"
    A locked standard record blocks content edits and deletion, but authorized users can unlock it for record versioning; properties are editable by default, and a container administrator can remove a locked standard-record label. Regulatory records block editing and label removal, including by administrators. Deletion remains blocked during retention; disposition follows the label settings afterward. Verify the [action restrictions](https://learn.microsoft.com/en-us/purview/records-management#compare-restrictions-for-what-actions-are-allowed-or-blocked) before selecting either type.

### Step 8: Publish Retention Labels

1. In Purview > **Solutions** > **Records Management** > **Policies** > **Label policies** > **Publish labels**
2. Select the five FSI-Agent labels created in Step 7
3. Keep **Full directory** for admin units and choose a **Static** scope. On the **Choose locations** page:
   - For the group-connected team site created in Step 1, enable **Microsoft 365 Group mailboxes & sites** and select its group
   - Use **SharePoint classic and communication sites** only for sites that aren't group-connected; this static location does not include group-connected team sites
   - Enable **OneDrive accounts** if agent documentation is stored in OneDrive
4. **Policy name:** `FSI-AI-Governance-Retention-Zone2` (the PowerShell playbook creates a separate policy per label)
5. Click **Submit**

!!! note "Propagation delay"
    Published labels may take up to 7 days to appear in SharePoint libraries. For Zone 2 deployments, plan a 1-week buffer between label publishing and auto-labeling configuration.

### Step 9: Configure Auto-Labeling Policy

1. In Purview > **Solutions** > **Records Management** > **Policies** > **Label policies**
2. Select **Auto-apply a label**
3. Configure:
   - **Label to auto-apply:** `FSI-Agent-Communications-3Year`
   - **Conditions:** Apply label to content that contains specific words or phrases
   - **Query:** `ParentLink:"https://contoso.sharepoint.com/sites/AI-Governance/InteractionLogs" AND ("Agent ID" OR "Copilot interaction" OR "agent session")` — replace the library URL with its actual address
   - **Locations:** With a static scope, select the AI Governance group under **Microsoft 365 Group mailboxes & sites**. Library targeting is in the query, not a library picker
4. **Policy name:** `FSI-AutoLabel-InteractionLogs`
5. Run in **simulation mode**, review matching and nonmatching samples, then turn on the policy. Allow up to **7 days** for automatic application after deployment; publishing a label and auto-applying it are separate operations

!!! tip "Alternative: content type-based auto-labeling"
    For more precise targeting, create a SharePoint content type for interaction logs and query its indexed `ContentType` property. Test the query before deployment. Auto-apply policies do not replace an existing retention label and do not support regulatory-record labels. See [automatic retention labeling](https://learn.microsoft.com/en-us/purview/apply-retention-labels-automatically).

### Step 10: Document Copilot Studio Agent Versioning

1. Open **[Copilot Studio](https://copilotstudio.microsoft.com)**, select the correct environment, and open the agent
2. Open **Publish** and capture the displayed publication status. Preserve a release record with agent ID, environment ID, operator identity, timestamp, approval reference, and solution version
3. Open **Settings** > **Agent details** > **View solution**, or **…** > **Solutions** in the sidebar
4. In **[Power Apps](https://make.powerapps.com)**, select the same environment > **Solutions** > select the custom solution > **See history**. Capture operation, solution version, timestamps, and result. This is import/export/uninstall history, not an agent publication ledger; **Publisher** is the solution publisher, not proof of the human who published the agent
5. Preserve this evidence promptly: solution history older than **180 days** is automatically deleted

!!! note "Publication evidence and solution evidence are separate"
    The [publishing documentation](https://learn.microsoft.com/en-us/microsoft-copilot-studio/publication-fundamentals-publish-channels) documents the **Publish** page, not a universal version-numbered publish-history export. Use your release record for publisher identity and publication history. [Solution history](https://learn.microsoft.com/en-us/power-apps/maker/data-platform/solution-history) and [solution layers](https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-solutions-overview) are Dataverse solution capabilities; a Managed Environment is not a stated prerequisite for viewing them.

!!! note "FSI Evidence Capture"
    Capture the agent overview and Publish page with environment context, plus the release record and solution history. Record only fields actually displayed; do not invent a version number from the Publish page.

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
3. After creation, navigate to **Data storage** > **Containers** > **+ Container**:
   - **Name:** `ai-governance-records`
   - **Access level:** Private
4. On the container's **More** menu, select **Access policy** > **Immutable blob storage**:
   - Click **+ Add policy** > **Time-based retention**
   - Set **Retention period:** 2190 days (6 years) or 2555 days (7 years with buffer)
   - Leave **Enable version-level immutability** unchecked for this container-scoped procedure; blob versioning is not a prerequisite for container-scoped retention
   - Click **Save**
5. **Lock the policy** (⚠️ IRREVERSIBLE):
   - On the policy's **More** menu, select **Lock policy**
   - Confirm the lock — once locked, the retention period cannot be shortened; delete expired blobs before deleting the empty container

!!! danger "WORM lock is irreversible"
    Locking a time-based retention policy is a **one-way operation**. It cannot be reversed, shortened, or deleted. Test thoroughly in a non-production environment before locking in production. Organizations should verify this meets their operational requirements and consult with Compliance Officer before locking.

6. Configure an export pipeline (Power Automate or Azure Data Factory) to copy agent records from SharePoint / Purview to the immutable blob container on a scheduled basis

Use unique blob names for successive exports and verify successful copy, retention scope, and deletion/overwrite protection with disposable test data. Immutability policies can take up to 35 seconds to take effect. Pipeline design, source permissions, completeness checks, and error monitoring are separate implementation work, not provided by creating the container. See [container-scoped immutability configuration](https://learn.microsoft.com/en-us/azure/storage/blobs/immutable-policy-configure-container-scope).

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

1. Have an authorized Purview administrator enable the regulatory-record option using the documented `Set-RegulatoryComplianceUI -Enabled $true` command in Security & Compliance PowerShell. This only displays the option; it does not declare any records. See [Declare records](https://learn.microsoft.com/en-us/purview/declare-records). Then open **Solutions** > **Records Management** > **File plan** > **+ Create a label** > **Retention label**
2. Create additional Zone 3 labels:

| Label Name | Retention | Action | Record Type | Regulatory Basis |
|---|---|---|---|---|
| `FSI-Agent-RegRecord-7Year` | 7 years | Delete items automatically | Regulatory record | SEC 17a-4 (6-year + buffer) |
| `FSI-Agent-CFTC-5Year` | 5 years | Delete items automatically | Regulatory record | CFTC 1.31 — derivatives records |
| `FSI-Agent-ModelRisk-6Year` | 6 years | Delete items automatically | Record | OCC Bulletin 2026-13 (formerly OCC 2011-12) / Fed SR 26-2 (formerly SR 11-7) — model documentation |
| `FSI-Agent-Permanent` | Indefinite | No action | Regulatory record | Board approvals, critical governance |

3. Mark as **Regulatory record** where indicated — this blocks label removal and user deletion, including by administrators, during retention. Complete metadata before applying the label
4. Publish the additional labels through **Policies** > **Label policies** to the governance group/site using Step 8. Apply regulatory-record labels from the published policy, not an auto-apply policy. The optional `FSI-Agent-Permanent` label is created here in the portal, not by the PowerShell sample

!!! warning "Regulatory record labels cannot be removed"
    Nobody can remove a regulatory-record label from an item, and its retention period cannot be shortened after the label is saved. Content and properties cannot be edited. At the end of a finite retention period, the configured disposition action can delete the item; indefinite retention has no expiry. This is more restrictive than a standard record label. Only use for content with clear regulatory retention requirements.

### Step 13: Configure Comprehensive Document Taxonomy

1. Navigate to **Settings** > **Site information** > **View all site settings** > **Site content types** > **Create content type** (site-scoped gallery, not the tenant content type hub)
2. Create the following content types in the **AI Governance** group:

| Content Type | Parent | Description | Libraries |
|---|---|---|---|
| `Agent Configuration Record` | Document | Agent manifest exports, system instructions, prompt versions | AgentConfigurations |
| `Agent Interaction Log` | Document | Conversation transcripts, session data | InteractionLogs |
| `Governance Approval Record` | Document | Deployment approvals, change authorizations | ApprovalRecords |
| `Incident Report` | Document | Security incidents, compliance findings | IncidentReports |
| `Supervision Evidence` | Document | FINRA 3110 review logs, sampling reports | SupervisionRecords |

3. Associate each content type with the appropriate AI Governance site columns
4. In each designated library > **Library settings** > **Advanced settings**, enable **Allow management of content types**, then add the existing site content type
5. Set the **default content type** for each library to the matching type

### Step 14: Establish Examination Response Procedures

1. In the `GovernanceDecisions` library, create: `Examination-Response-Procedure.docx`
2. Document the following in the procedure:

| Section | Content |
|---|---|
| **Designated Custodians** | Primary custodian name and contact, backup custodian name and contact |
| **Response SLA** | 24 hours for initial acknowledgment, 48 hours for initial document production |
| **Search Procedures** | How to locate agent records using searches in Microsoft Purview eDiscovery and SharePoint search |
| **Export and Production** | Procedures for exporting records to examiner-ready format: mailbox items as PST or individual messages, SharePoint/OneDrive files in native format, and CSV export reports |
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

1. Open **[Power Platform Admin Center](https://admin.powerplatform.microsoft.com)** > **Manage** > **Environments**
2. For each environment containing agents:
   - Navigate to **Settings** > **Audit and logs** > **Audit settings** and verify **Start Auditing**; also verify auditing on the required tables and columns
   - In Copilot Studio's solution explorer, select the solution > **Agents** > agent > **Advanced** > **See solution layers**
   - Export the environment details (Name, Type, Region, Creator, Created Date) as evidence
3. In **Copilot Studio** for each Zone 3 agent:
   - Follow [export agents using solutions](https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-solutions-import-export): add the agent to a custom unmanaged solution, use **Add required objects**, then **Export solution**. Managed solutions cannot be exported from the target environment; preserve the deployment package from the source
   - Check dependency completeness and separately document excluded data (for example, topic comments, channel settings, and external knowledge content); a solution ZIP is not a full transcript/data backup
   - Document the solution version and publication release record from Step 10
   - Where supported for the agent, open **Monitor** and capture the displayed usage metrics. Record unavailable metrics rather than assuming every agent/harness exposes the same analytics

!!! note "FSI Evidence Capture"
    For each Zone 3 agent, capture: (1) agent details and Publish page with release record, (2) source solution ZIP and dependency inventory, (3) solution operation history and component layers, (4) analytics overview. Save to `AgentConfigurations` with appropriate metadata. [Dataverse auditing](https://learn.microsoft.com/en-us/power-platform/admin/manage-dataverse-auditing) requires environment, table, and column settings; an environment-level toggle alone is insufficient.

---

## Configuration Summary

| Setting | Zone 1 (Personal) | Zone 2 (Team) | Zone 3 (Enterprise) |
|---------|-------------------|---------------|---------------------|
| **SharePoint site** | Basic (3 libraries) | Comprehensive (6 libraries) | Full (6 libraries + content types) |
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
- [ ] Copilot Studio publication release record, solution version/history, and source solution export preserved (Zone 2+)
- [ ] Audit cadence scheduled and owners assigned

---

## Microsoft documentation reviewed

Live sources checked on **2026-11-09**. This verifies documented product behavior, not tenant configuration, screenshots, or regulatory suitability.

- [SharePoint site creation](https://learn.microsoft.com/en-us/sharepoint/create-site-collection) and [library version limits](https://learn.microsoft.com/en-us/sharepoint/library-version-limits)
- [Library creation](https://support.microsoft.com/en-us/sharepoint/documents-and-library/create-a-document-library-in-sharepoint), [site columns](https://support.microsoft.com/en-us/office/create-a-column-in-a-list-or-library-2b0361ae-1bd3-41a3-8329-269e5f81cfa2), [versioning settings](https://support.microsoft.com/en-us/office/enable-and-configure-versioning-for-a-list-or-library-1555d642-23ee-446a-990a-bcab618c7a37), [site content types](https://support.microsoft.com/en-us/office/introduction-to-content-types-and-content-type-publishing-e1277a2e-a1e8-4473-9126-91a0647766e5), and [library content types](https://support.microsoft.com/en-us/office/add-a-content-type-to-a-list-or-library-917366ae-f7a2-47ad-87a5-9689a1884e60)
- [Purview licensing by feature](https://learn.microsoft.com/en-us/office365/servicedescriptions/microsoft-365-service-descriptions/microsoft-365-tenantlevel-services-licensing-guidance/microsoft-purview-service-description) and [Records Management permissions](https://learn.microsoft.com/en-us/purview/get-started-with-records-management)
- [File plan and label creation](https://learn.microsoft.com/en-us/purview/file-plan-manager), [record restrictions](https://learn.microsoft.com/en-us/purview/records-management), and [regulatory-record enablement](https://learn.microsoft.com/en-us/purview/declare-records)
- [Publish retention labels](https://learn.microsoft.com/en-us/purview/create-apply-retention-labels), [policy locations](https://learn.microsoft.com/en-us/purview/retention-settings), and [auto-apply conditions and timing](https://learn.microsoft.com/en-us/purview/apply-retention-labels-automatically)
- [Copilot Studio publishing](https://learn.microsoft.com/en-us/microsoft-copilot-studio/publication-fundamentals-publish-channels), [solutions and layers](https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-solutions-overview), [agent export limitations](https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-solutions-import-export), and [solution history retention](https://learn.microsoft.com/en-us/power-apps/maker/data-platform/solution-history)
- [Dataverse auditing](https://learn.microsoft.com/en-us/power-platform/admin/manage-dataverse-auditing) and [container-scoped immutable storage](https://learn.microsoft.com/en-us/azure/storage/blobs/immutable-policy-configure-container-scope)
- [eDiscovery search exports](https://learn.microsoft.com/en-us/purview/edisc-search-export)
- [Copilot Studio Monitor and analytics scope](https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-overview)

[Back to Control 2.13](../../../controls/pillar-2-management/2.13-documentation-and-record-keeping.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: November 2026 | Version: v1.6.2 | UI Verification Status: Needs Review (documentation verified 2026-11-09; tenant UI last verified April 2026)*
